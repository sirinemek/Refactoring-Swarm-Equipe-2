from pathlib import Path
from typing import Dict
from src.utils.TheToolSmith import read_file, run_pylint, send_to_gemini
from src.Prompts.auditor_prompts import get_auditor_prompt
import json

class Auditor:
    def __init__(self, base_dir: Path, api_key: str):
        self.base_dir = base_dir
        self.api_key = api_key

    def build_prompt(self, filename: str, code: str, pylint_errors: list) -> str:
        prompt_dict = get_auditor_prompt(self.base_dir)
        user_prompt = prompt_dict["user"]
        return (
            user_prompt
            + f"\n\nFichier : {filename}\n"
            + f"\nCode source :\n{code}\n"
            + f"\nErreurs Pylint :\n{json.dumps(pylint_errors, indent=2)}"
        )

    def analyze_file(self, relative_path: str) -> Dict:
        code = read_file(self.base_dir, relative_path)
        pylint_result = run_pylint(self.base_dir / relative_path)
        prompt = self.build_prompt(relative_path, code, pylint_result["errors"])
        gemini_result = send_to_gemini(prompt, self.api_key)
        return {"file": relative_path, "pylint": pylint_result, "gemini": gemini_result}

    def analyze_all(self) -> Dict:
        results = {}
        for py_file in self.base_dir.rglob("*.py"):
            relative_path = str(py_file.relative_to(self.base_dir))
            results[relative_path] = self.analyze_file(relative_path)
        return results