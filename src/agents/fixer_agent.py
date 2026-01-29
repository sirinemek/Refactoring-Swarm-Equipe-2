"""
Agent Correcteur (Fixer Agent)
Responsable de la correction du code selon le plan de refactoring
"""
from pathlib import Path
from typing import Dict, Any
from src.agents.base_agent import BaseAgent
from src.prompts.fixer_prompts import (
    FIXER_SYSTEM_PROMPT, 
    get_fixer_correction_prompt,
    get_fixer_iteration_prompt
)
from src.utils.logger import ActionType


class FixerAgent(BaseAgent):
    """Agent responsable de la correction du code"""
    
    def __init__(self):
        super().__init__(
            agent_name="Fixer_Agent",
            system_prompt=FIXER_SYSTEM_PROMPT
        )
    
    def fix_code(self, file_path: Path, code_content: str, 
                 analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Corrige le code selon l'analyse fournie
        
        Args:
            file_path: Chemin du fichier à corriger
            code_content: Contenu actuel du code
            analysis_result: Résultat de l'analyse de l'Auditeur
            
        Returns:
            Dictionnaire contenant le code corrigé et les modifications
        """
        print(f"\n🔧 [{self.agent_name}] Correction de {file_path.name}...")
        
        # Extraire les informations de l'analyse
        refactoring_plan = "\n".join(analysis_result.get("refactoring_plan", []))
        
        # Construire le résumé des problèmes
        critical_issues = analysis_result.get("critical_issues", [])
        quality_issues = analysis_result.get("quality_issues", [])
        
        issues_summary = "**Problèmes Critiques:**\n"
        for issue in critical_issues:
            issues_summary += f"- [{issue.get('type')}] Ligne {issue.get('line')}: {issue.get('description')}\n"
        
        issues_summary += "\n**Problèmes de Qualité:**\n"
        for issue in quality_issues:
            issues_summary += f"- [{issue.get('type')}] Ligne {issue.get('line')}: {issue.get('description')}\n"
        
        # Construire le prompt de correction
        correction_prompt = get_fixer_correction_prompt(
            filename=file_path.name,
            filepath=str(file_path),
            refactoring_plan=refactoring_plan,
            issues_summary=issues_summary,
            code_content=code_content
        )
        
        # Appeler le LLM
        additional_details = {
            "file_corrected": str(file_path),
            "issues_to_fix": len(critical_issues) + len(quality_issues),
            "original_code_length": len(code_content.split("\n"))
        }
        
        fix_result = self.safe_call_llm_json(
            user_prompt=correction_prompt,
            action_type=ActionType.FIX,
            additional_details=additional_details
        )
        
        # Enrichir le résultat
        fix_result["file_path"] = str(file_path)
        fix_result["original_code"] = code_content
        
        # Afficher un résumé
        changes_count = len(fix_result.get("changes_made", []))
        fixed_count = len(fix_result.get("issues_fixed", []))
        
        print(f"✅ Correction terminée:")
        print(f"   - Modifications: {changes_count}")
        print(f"   - Problèmes corrigés: {fixed_count}")
        
        return fix_result
    
    def fix_with_feedback(self, file_path: Path, code_content: str,
                          error_report: str) -> Dict[str, Any]:
        """
        Corrige le code suite à un feedback du Judge (itération)
        
        Args:
            file_path: Chemin du fichier
            code_content: Code actuel avec erreurs
            error_report: Rapport d'erreurs du Judge
            
        Returns:
            Dictionnaire contenant le code corrigé
        """
        print(f"\n🔄 [{self.agent_name}] Correction itérative de {file_path.name}...")
        
        # Construire le prompt d'itération
        iteration_prompt = get_fixer_iteration_prompt(
            filename=file_path.name,
            error_report=error_report,
            code_content=code_content
        )
        
        # Appeler le LLM
        additional_details = {
            "file_corrected": str(file_path),
            "iteration_type": "feedback_correction",
            "error_report_length": len(error_report)
        }
        
        fix_result = self.safe_call_llm_json(
            user_prompt=iteration_prompt,
            action_type=ActionType.FIX,
            additional_details=additional_details
        )
        
        # Enrichir le résultat
        fix_result["file_path"] = str(file_path)
        fix_result["original_code"] = code_content
        
        print(f"✅ Correction itérative terminée")
        
        return fix_result
    
    def apply_fix(self, file_path: Path, fixed_code: str) -> bool:
        """
        Applique la correction en écrivant le code corrigé dans le fichier
        
        Args:
            file_path: Chemin du fichier
            fixed_code: Code corrigé à écrire
            
        Returns:
            True si succès
        """
        try:
            # Écrire le code corrigé
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_code)
            
            print(f"💾 Code corrigé écrit dans {file_path.name}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de l'écriture de {file_path}: {e}")
            return False
    
    def fix_all_files(self, analysis_results: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Corrige tous les fichiers analysés
        
        Args:
            analysis_results: Résultats d'analyse de l'Auditeur
            
        Returns:
            Dictionnaire {filepath: fix_result}
        """
        print(f"\n🔧 [{self.agent_name}] Correction de tous les fichiers...")
        
        fix_results = {}
        
        for filepath, analysis in analysis_results.items():
            # Ignorer les fichiers en erreur
            if "error" in analysis:
                print(f"⚠️ Fichier ignoré (erreur d'analyse): {filepath}")
                continue
            
            try:
                file_path = Path(filepath)
                
                # Lire le code actuel
                with open(file_path, 'r', encoding='utf-8') as f:
                    code_content = f.read()
                
                # Corriger
                fix_result = self.fix_code(file_path, code_content, analysis)
                
                # Appliquer la correction
                fixed_code = fix_result.get("fixed_code", "")
                if fixed_code:
                    self.apply_fix(file_path, fixed_code)
                    fix_result["applied"] = True
                else:
                    print(f"⚠️ Aucun code corrigé reçu pour {filepath}")
                    fix_result["applied"] = False
                
                fix_results[filepath] = fix_result
                
            except Exception as e:
                print(f"❌ Erreur lors de la correction de {filepath}: {e}")
                fix_results[filepath] = {
                    "error": str(e),
                    "status": "FAILED",
                    "applied": False
                }
        
        print(f"\n✅ Correction terminée pour {len(fix_results)} fichier(s)")
        
        return fix_results
