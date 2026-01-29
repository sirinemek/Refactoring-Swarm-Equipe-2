"""
Agent Testeur/Juge (Judge Agent)
Responsable de la validation du code corrigé
"""
from pathlib import Path
from typing import Dict, Any, Tuple
from src.agents.base_agent import BaseAgent
from src.prompts.tester_prompts import (
    TESTER_SYSTEM_PROMPT,
    get_tester_validation_prompt,
    get_tester_iteration_feedback
)
from src.utils.logger import ActionType
from src.utils.tools import run_pytest, run_pylint, parse_pylint_output


class JudgeAgent(BaseAgent):
    """Agent responsable de la validation et des tests"""
    
    def __init__(self):
        super().__init__(
            agent_name="Judge_Agent",
            system_prompt=TESTER_SYSTEM_PROMPT
        )
    
    def validate_file(self, file_path: Path, code_content: str,
                     score_before: float) -> Dict[str, Any]:
        """
        Valide un fichier corrigé
        
        Args:
            file_path: Chemin du fichier
            code_content: Code corrigé
            score_before: Score Pylint avant correction
            
        Returns:
            Résultat de la validation
        """
        print(f"\n⚖️ [{self.agent_name}] Validation de {file_path.name}...")
        
        # Étape 1: Exécuter les tests pytest
        test_results = self._run_tests(file_path)
        
        # Étape 2: Analyser avec Pylint
        pylint_output = run_pylint(str(file_path))
        score_after, pylint_report = parse_pylint_output(pylint_output)
        
        print(f"📊 Score Pylint: {score_before:.1f} → {score_after:.1f}")
        
        # Étape 3: Construire le prompt de validation
        validation_prompt = get_tester_validation_prompt(
            filename=file_path.name,
            filepath=str(file_path),
            test_results=test_results,
            score_before=score_before,
            score_after=score_after,
            pylint_report=pylint_report,
            code_content=code_content
        )
        
        # Étape 4: Appeler le LLM pour la décision
        additional_details = {
            "file_validated": str(file_path),
            "score_before": score_before,
            "score_after": score_after,
            "improvement": score_after - score_before
        }
        
        validation_result = self.safe_call_llm_json(
            user_prompt=validation_prompt,
            action_type=ActionType.DEBUG,
            additional_details=additional_details
        )
        
        # Enrichir le résultat
        validation_result["file_path"] = str(file_path)
        validation_result["score_before"] = score_before
        validation_result["score_after"] = score_after
        
        # Afficher la décision
        decision = validation_result.get("decision", "UNKNOWN")
        status = validation_result.get("validation_status", "UNKNOWN")
        
        if decision == "ACCEPT":
            print(f"✅ Validation réussie! Code accepté")
        elif decision == "RETRY":
            print(f"⚠️ Validation échouée - Besoin de corrections supplémentaires")
        else:
            print(f"❓ Décision: {decision}, Statut: {status}")
        
        return validation_result
    
    def _run_tests(self, file_path: Path) -> str:
        """
        Exécute les tests pytest sur un fichier
        
        Args:
            file_path: Chemin du fichier
            
        Returns:
            Résultats des tests
        """
        try:
            # Chercher les fichiers de test associés
            test_file = file_path.parent / f"test_{file_path.name}"
            
            if test_file.exists():
                print(f"🧪 Exécution des tests: {test_file.name}")
                test_output = run_pytest(str(test_file))
            else:
                # Pas de fichier de test trouvé
                print(f"⚠️ Aucun fichier de test trouvé pour {file_path.name}")
                test_output = "No test file found. Skipping pytest."
            
            return test_output
            
        except Exception as e:
            return f"Error running tests: {str(e)}"
    
    def validate_all_files(self, fix_results: Dict[str, Dict[str, Any]],
                          analysis_results: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Valide tous les fichiers corrigés
        
        Args:
            fix_results: Résultats de correction du Fixer
            analysis_results: Résultats d'analyse originaux (pour scores avant)
            
        Returns:
            Dictionnaire {filepath: validation_result}
        """
        print(f"\n⚖️ [{self.agent_name}] Validation de tous les fichiers...")
        
        validation_results = {}
        
        for filepath, fix_result in fix_results.items():
            # Ignorer les fichiers en erreur
            if not fix_result.get("applied", False):
                print(f"⚠️ Fichier ignoré (pas de correction appliquée): {filepath}")
                continue
            
            try:
                file_path = Path(filepath)
                
                # Récupérer le score avant
                score_before = analysis_results.get(filepath, {}).get("pylint_score_before", 0)
                
                # Lire le code corrigé
                with open(file_path, 'r', encoding='utf-8') as f:
                    code_content = f.read()
                
                # Valider
                validation = self.validate_file(file_path, code_content, score_before)
                validation_results[filepath] = validation
                
            except Exception as e:
                print(f"❌ Erreur lors de la validation de {filepath}: {e}")
                validation_results[filepath] = {
                    "error": str(e),
                    "status": "FAILED",
                    "decision": "ABORT"
                }
        
        # Calculer le résumé
        self._print_validation_summary(validation_results)
        
        return validation_results
    
    def check_iteration_needed(self, validation_results: Dict[str, Dict[str, Any]],
                               iteration_number: int, max_iterations: int = 10) -> Tuple[bool, Dict[str, str]]:
        """
        Vérifie si une itération supplémentaire est nécessaire
        
        Args:
            validation_results: Résultats de validation
            iteration_number: Numéro d'itération actuel
            max_iterations: Nombre max d'itérations
            
        Returns:
            (needs_retry, feedback_by_file)
        """
        needs_retry = False
        feedback_by_file = {}
        
        for filepath, result in validation_results.items():
            decision = result.get("decision", "UNKNOWN")
            
            if decision == "RETRY" and iteration_number < max_iterations:
                needs_retry = True
                feedback = result.get("feedback_for_fixer", "")
                errors = result.get("errors_to_fix", [])
                
                feedback_text = f"{feedback}\n\nErreurs:\n"
                for error in errors:
                    feedback_text += f"- {error}\n"
                
                feedback_by_file[filepath] = feedback_text
            
            elif decision == "RETRY" and iteration_number >= max_iterations:
                print(f"⚠️ Limite d'itérations atteinte pour {filepath}")
                feedback_by_file[filepath] = "MAX_ITERATIONS_REACHED"
        
        return needs_retry, feedback_by_file
    
    def _print_validation_summary(self, validation_results: Dict[str, Dict[str, Any]]):
        """Affiche un résumé des validations"""
        total = len(validation_results)
        accepted = sum(1 for r in validation_results.values() if r.get("decision") == "ACCEPT")
        retry = sum(1 for r in validation_results.values() if r.get("decision") == "RETRY")
        abort = sum(1 for r in validation_results.values() if r.get("decision") == "ABORT")
        
        print(f"\n📊 Résumé de la validation:")
        print(f"   - Total: {total}")
        print(f"   - Acceptés: {accepted} ✅")
        print(f"   - À refaire: {retry} ⚠️")
        print(f"   - Abandonnés: {abort} ❌")
    
    def get_final_summary(self, validation_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Génère un résumé final de toutes les validations
        
        Args:
            validation_results: Résultats de validation
            
        Returns:
            Résumé global
        """
        total_files = len(validation_results)
        successful = [
            filepath for filepath, result in validation_results.items()
            if result.get("decision") == "ACCEPT"
        ]
        
        failed = [
            filepath for filepath, result in validation_results.items()
            if result.get("decision") in ["RETRY", "ABORT"]
        ]
        
        avg_improvement = sum(
            result.get("score_after", 0) - result.get("score_before", 0)
            for result in validation_results.values()
        ) / max(total_files, 1)
        
        summary = {
            "total_files": total_files,
            "successful_files": len(successful),
            "failed_files": len(failed),
            "success_rate": (len(successful) / max(total_files, 1)) * 100,
            "average_improvement": round(avg_improvement, 2),
            "successful_list": successful,
            "failed_list": failed
        }
        
        return summary
