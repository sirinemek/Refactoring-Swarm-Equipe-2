from pathlib import Path
from typing import Dict, List

from utils.The_Toolsmith import (
    list_python_files,
    read_file,
    run_pylint
)


class AuditorAgent:
    """
    Agent Auditeur :
    - Analyse statique du code
    - Détecte les problèmes
    - Produit un plan de refactoring
    """

    def __init__(self, sandbox_dir: Path):
        self.sandbox_dir = sandbox_dir

    # ============================================================
    #  Analyse globale
    # ============================================================
    def analyze(self) -> Dict:
        """
        Lance l'analyse complète du projet Python.

        Returns:
            dict: Rapport d'audit structuré
        """

        python_files = list_python_files(self.sandbox_dir)

        pylint_result = run_pylint(self.sandbox_dir)

        refactoring_plan = self._build_refactoring_plan(
            pylint_result["errors"]
        )

        return {
            "summary": {
                "files_analyzed": len(python_files),
                "pylint_score": pylint_result["score"],
                "issues_found": len(pylint_result["errors"])
            },
            "files": python_files,
            "pylint": pylint_result,
            "refactoring_plan": refactoring_plan
        }

    # ============================================================
    #  Construction du plan de refactoring
    # ============================================================
    def _build_refactoring_plan(self, errors: List[Dict]) -> List[Dict]:
        """
        Transforme les erreurs pylint en tâches de refactoring.
        """

        plan = []

        for err in errors:
            task = {
                "file": err["file"],
                "line": err["line"],
                "type": self._classify_issue(err["code"]),
                "description": err["message"],
                "rule": err["symbol"],
                "suggested_action": self._suggest_fix(err)
            }
            plan.append(task)

        return plan

    # ============================================================
    #  Classification des problèmes
    # ============================================================
    def _classify_issue(self, code: str) -> str:
        if code.startswith("C"):
            return "STYLE"
        if code.startswith("W"):
            return "WARNING"
        if code.startswith("E"):
            return "ERROR"
        if code.startswith("R"):
            return "REFACTOR"
        return "UNKNOWN"

    # ============================================================
    #  Suggestion de correction
    # ============================================================
    def _suggest_fix(self, err: Dict) -> str:
        symbol = err.get("symbol", "")

        suggestions = {
            "missing-module-docstring": "Ajouter une docstring en début de fichier",
            "missing-function-docstring": "Ajouter une docstring à la fonction",
            "invalid-name": "Renommer la variable selon PEP8",
            "bad-indentation": "Corriger l'indentation (4 espaces)",
            "line-too-long": "Découper la ligne en plusieurs lignes",
            "disallowed-name": "Renommer la fonction ou variable"
        }

        return suggestions.get(
            symbol,
            "Analyser et corriger selon les bonnes pratiques Python"
        )


# ============================================================
# ▶ Test manuel rapide
# ============================================================
if __name__ == "__main__":
    auditor = AuditorAgent(Path("sandbox"))
    report = auditor.analyze()

    print("\n RÉSUMÉ")
    print(report["summary"])

    print("\n PLAN DE REFACTORING")
    for task in report["refactoring_plan"]:
        print(
            f"- {task['file']}:{task['line']} "
            f"[{task['type']}] {task['description']} → {task['suggested_action']}"
        )
