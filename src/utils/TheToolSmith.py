from pathlib import Path
from typing import List
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import subprocess
import json
import re
# ============================================================
#  Sécurité : vérification sandbox
# ============================================================

def _ensure_in_sandbox(base_dir: Path, target_path: Path) -> Path:
    """
    Vérifie que target_path est bien à l'intérieur de base_dir.
    Empêche les attaques de type ../ ou chemins absolus.
    """
    base_dir = base_dir.resolve()
    target_path = target_path.resolve()

    if not str(target_path).startswith(str(base_dir)):
        raise PermissionError(
            f"Accès interdit hors sandbox : {target_path}"
        )

    return target_path


# ============================================================
#  Lecture de fichier texte
# ============================================================

def read_file(base_dir: Path, relative_path: str) -> str:
    """
    Lit le contenu d'un fichier texte situé dans le dossier sandbox.

    Args:
        base_dir (Path): Dossier racine sandbox (--target_dir)
        relative_path (str): Chemin relatif du fichier

    Returns:
        str: Contenu du fichier
    """
    file_path = _ensure_in_sandbox(
        base_dir,
        base_dir / relative_path
    )

    if not file_path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {relative_path}")

    if not file_path.is_file():
        raise IsADirectoryError(f"Ce n'est pas un fichier : {relative_path}")

    return file_path.read_text(encoding="utf-8")


# ============================================================
#  Écriture de fichier texte
# ============================================================

def write_file(base_dir: Path, relative_path: str, content: str) -> None:
    """
    Écrit (ou écrase) un fichier texte dans le dossier sandbox.

    Args:
        base_dir (Path): Dossier racine sandbox
        relative_path (str): Chemin relatif du fichier
        content (str): Contenu à écrire
    """
    file_path = _ensure_in_sandbox(
        base_dir,
        base_dir / relative_path
    )

    # Créer les dossiers parents si nécessaire
    file_path.parent.mkdir(parents=True, exist_ok=True)

    file_path.write_text(content, encoding="utf-8")


# ============================================================
#  Liste des fichiers Python
# ============================================================

def list_python_files(base_dir: Path) -> List[str]:
    """
    Retourne la liste de tous les fichiers .py dans le sandbox
    (chemins relatifs).

    Args:
        base_dir (Path): Dossier racine sandbox

    Returns:
        List[str]: Liste des fichiers Python
    """
    base_dir = base_dir.resolve()
    python_files = []

    for path in base_dir.rglob("*.py"):
        _ensure_in_sandbox(base_dir, path)
        python_files.append(str(path.relative_to(base_dir)))

    return python_files


# ============================================================
# 🔹 Exécution sécurisée d'une commande shell
# ============================================================
def run_command(cmd: list, cwd: Path = None) -> Tuple[int, Optional[str], Optional[str]]:
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)


# ============================================================
# 🔹 Lancer Pylint et récupérer toutes les erreurs
# ============================================================
def run_pylint(base_dir: Path) -> Dict:
    if not isinstance(base_dir, Path):
        base_dir = Path(base_dir)

    cmd = [
        "pylint",
        str(base_dir),
        "--output-format=json",
        "--score=y"
    ]

    return_code, stdout, stderr = run_command(
        cmd,
        cwd=base_dir.parent if base_dir.is_file() else base_dir
    )

    raw_output = stdout + "\n" + stderr

    # Extraction du score global
    score = _extract_pylint_score(raw_output)

    # Extraction des erreurs JSON
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
    except json.JSONDecodeError:
        pass

    # 🔹 Extraction des erreurs depuis la sortie texte brute (pour E0001 et autres)
    text_pattern = re.compile(r"^(.*\.py):(\d+):(\d+): (\w+): (.*) \((.*)\)$")
    for line in raw_output.splitlines():
        match = text_pattern.match(line.strip())
        if match:
            file, lineno, col, code, message, symbol = match.groups()
            # Éviter les doublons
            if not any(err['line']==int(lineno) and err['code']==code for err in errors):
                errors.append({
                    "file": file,
                    "line": int(lineno),
                    "column": int(col),
                    "code": code,
                    "message": message,
                    "symbol": symbol
                })

    return {
        "score": score,
        "raw_output": raw_output,
        "errors": errors
    }


# ============================================================
# 🔹 Extraction du score global depuis la sortie texte
# ============================================================
def _extract_pylint_score(output: str) -> float:
    match = re.search(r"rated at\s+([-+]?\d*\.\d+|\d+)/10", output)
    if match:
        return float(match.group(1))
    return 0.0


# ============================================================
# 🔹 Exemple d'utilisation améliorée : capture toutes les erreurs
# ============================================================
if __name__ == "__main__":
    base_path = Path("sandbox/test.py")  # ou dossier complet
    result = run_pylint(base_path)

    print(f"Score global : {result['score']}/10\n")
    print("Erreurs détectées :")

    # 1️⃣ Afficher les erreurs JSON formatées
    for e in result["errors"]:
        print(f"{e['file']}:{e['line']}:{e['column']} [{e['code']}] {e['message']} ({e['symbol']})")

    # 2️⃣ Chercher les erreurs de parsing dans la sortie brute
    parsing_errors = re.findall(
        r"(.*\.py):(\d+):(\d+): (E\d+): (Parsing failed: .*) \((.*)\)",
        result["raw_output"]
    )

    for file, line, col, code, message, symbol in parsing_errors:
        print(f"{file}:{line}:{col} [{code}] {message} ({symbol})")

