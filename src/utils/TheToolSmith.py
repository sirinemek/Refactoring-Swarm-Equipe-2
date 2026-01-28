from pathlib import Path
from typing import List, Dict, Tuple, Optional
import subprocess
import json
import re
import requests

def read_file(base_dir: Path, relative_path: str) -> str:
    file_path = (base_dir / relative_path).resolve()
    if not file_path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {relative_path}")
    if not file_path.is_file():
        raise IsADirectoryError(f"Ce n'est pas un fichier : {relative_path}")
    if base_dir not in file_path.parents and base_dir != file_path:
        raise PermissionError("Accès interdit hors sandbox")
    return file_path.read_text(encoding="utf-8")

def write_file(base_dir: Path, relative_path: str, content: str) -> None:
    file_path = (base_dir / relative_path).resolve()
    if base_dir not in file_path.parents and base_dir != file_path:
        raise PermissionError("Accès interdit hors sandbox")
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")

def run_command(cmd: List[str], cwd: Optional[Path] = None) -> Tuple[int, str, str]:
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)

def _extract_pylint_score(output: str) -> float:
    match = re.search(r"rated at\s+([-+]?\d*\.?\d+)/10", output)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return 0.0
    return 0.0

def run_pylint(target: Path) -> Dict:
    cmd = ["pylint", str(target), "--output-format=json", "--score=y"]
    return_code, stdout, stderr = run_command(cmd, cwd=target.parent if target.is_file() else target)
    raw_output = stdout + "\n" + stderr

    score = _extract_pylint_score(raw_output)

    errors = []
    try:
        errors_json = json.loads(stdout) if stdout.strip() else []
        for e in errors_json:
            errors.append({
                "file": e.get("path"),
                "line": e.get("line"),
                "column": e.get("column"),
                "code": e.get("message-id"),
                "message": e.get("message"),
                "symbol": e.get("symbol")
            })
    except Exception:
        pass

    return {"score": score, "raw_output": raw_output, "errors": errors}

def parse_gemini_response(text: str) -> Dict:
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception as e:
        return {
            "errors": [],
            "refactoring_plan": [],
            "raw": text,
            "error": str(e)
        }
    return {
        "errors": [],
        "refactoring_plan": [],
        "raw": text,
        "error": "JSON non détecté"
    }

def send_to_gemini(prompt: str, api_key: str, model_name: str = "gemini-2.5-flash") -> Dict:
    endpoint = "generateContent"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:{endpoint}"
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "candidateCount": 1
        }
    }
    try:
        response = requests.post(
            f"{url}?key={api_key}",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        data = response.json()
        if "candidates" in data and len(data["candidates"]) > 0:
            candidate = data["candidates"][0]
            text_output = ""
            if "content" in candidate and "parts" in candidate["content"]:
                parts = candidate["content"]["parts"]
                for part in parts:
                    if "text" in part:
                        text_output += part["text"]
            elif "output" in candidate:
                text_output = candidate.get("output")
            if text_output:
                return parse_gemini_response(text_output)
            else:
                return {"errors": [], "refactoring_plan": [], "raw": data, "error": "Contenu vide dans la réponse"}
        else:
            return {"errors": [], "refactoring_plan": [], "raw": data, "error": "Pas de réponse candidates"}
    except requests.exceptions.HTTPError as http_err:
        return {"errors": [], "refactoring_plan": [], "raw": str(http_err), "error": f"HTTPError {http_err}"}
    except Exception as e:
        return {"errors": [], "refactoring_plan": [], "raw": "", "error": str(e)}