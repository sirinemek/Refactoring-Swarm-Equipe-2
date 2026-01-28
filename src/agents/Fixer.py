from pathlib import Path
from typing import List, Dict
from src.Prompts.fixer_prompts import get_fixer_prompt
from src.utils.TheToolSmith import read_file, write_file, send_to_gemini

class Fixer:
    def __init__(self, base_dir: Path, api_key: str):
        self.base_dir = base_dir
        self.api_key = api_key

    def build_prompt(self, filename: str, code: str, refactoring_plan: List[str]) -> str:
        prompt_dict = get_fixer_prompt()
        return (
            prompt_dict["user"]
            + f"\n\nFichier : {filename}\n"
            + f"\nCode source :\n{code}\n"
            + f"\nPlan de refactoring proposé :\n" + "\n".join(f"- {step}" for step in refactoring_plan)
        )

    def fix_file(self, relative_path: str, refactoring_plan: List[str]) -> None:
        file_path = self.base_dir / relative_path
        code = read_file(self.base_dir, relative_path)
        prompt = self.build_prompt(relative_path, code, refactoring_plan)
        response = send_to_gemini(prompt, self.api_key, model_name="gemini-2.5-flash")

        fixed_code = response.get("fixed_code") or response.get("refactored_code") or ""

        if not fixed_code:
            print(f"⚠️ Aucune correction générée pour {relative_path}, on garde le code original.")
            fixed_code = code

        write_file(self.base_dir, relative_path, fixed_code)
        print(f"🔧 Correction du fichier {relative_path} terminée.")

    # --- L'ERREUR ÉTAIT ICI (Indentation corrigée ci-dessous) ---
    def fix_all(self, audit_results: List) -> None:
        for result in audit_results:
            if isinstance(result, str):
                filename = result
                refactoring_plan = []
            else:
                filename = result.get("file")
                gemini_data = result.get("gemini")
                if isinstance(gemini_data, dict):
                    refactoring_plan = gemini_data.get("refactoring_plan", [])
                else:
                    refactoring_plan = []

            if filename:
                if not refactoring_plan:
                    print(f"⚠️ Pas de plan de refactoring détaillé pour {filename}, envoi tel quel.")
                self.fix_file(filename, refactoring_plan)
            else:
                print(f"⚠️ Données d'audit invalides : {result}")