"""
Agent Auditeur (Auditor Agent)
Responsable de l'analyse du code et de la production du plan de refactoring
"""
from pathlib import Path
from typing import Dict, Any
from src.agents.base_agent import BaseAgent
from src.prompts.auditor_prompts import AUDITOR_SYSTEM_PROMPT, get_auditor_analysis_prompt
from src.utils.logger import ActionType
from src.utils.tools import run_pylint, parse_pylint_output


class AuditorAgent(BaseAgent):
    """Agent responsable de l'audit du code"""
    
    def __init__(self):
        super().__init__(
            agent_name="Auditor_Agent",
            system_prompt=AUDITOR_SYSTEM_PROMPT
        )
    
    def analyze_file(self, file_path: Path, code_content: str) -> Dict[str, Any]:
        """
        Analyse un fichier Python et produit un plan de refactoring
        
        Args:
            file_path: Chemin du fichier à analyser
            code_content: Contenu du code source
            
        Returns:
            Dictionnaire contenant l'analyse et le plan de refactoring
        """
        print(f"\n🔍 [{self.agent_name}] Analyse de {file_path.name}...")
        
        # Étape 1: Exécuter Pylint
        pylint_output = run_pylint(str(file_path))
        pylint_score, pylint_report = parse_pylint_output(pylint_output)
        
        print(f"📊 Score Pylint actuel: {pylint_score}/10.0")
        
        # Étape 2: Construire le prompt d'analyse
        analysis_prompt = get_auditor_analysis_prompt(
            filename=file_path.name,
            filepath=str(file_path),
            pylint_score=pylint_score,
            pylint_report=pylint_report,
            code_content=code_content
        )
        
        # Étape 3: Appeler le LLM
        additional_details = {
            "file_analyzed": str(file_path),
            "pylint_score_before": pylint_score,
            "code_length": len(code_content.split("\n"))
        }
        
        analysis_result = self.safe_call_llm_json(
            user_prompt=analysis_prompt,
            action_type=ActionType.ANALYSIS,
            additional_details=additional_details
        )
        
        # Étape 4: Enrichir le résultat avec les données Pylint
        analysis_result["pylint_score_before"] = pylint_score
        analysis_result["pylint_report"] = pylint_report
        analysis_result["file_path"] = str(file_path)
        
        # Afficher un résumé
        total_issues = analysis_result.get("total_issues", 0)
        critical_count = len(analysis_result.get("critical_issues", []))
        quality_count = len(analysis_result.get("quality_issues", []))
        
        print(f"✅ Analyse terminée:")
        print(f"   - Problèmes totaux: {total_issues}")
        print(f"   - Critiques: {critical_count}")
        print(f"   - Qualité: {quality_count}")
        
        return analysis_result
    
    def analyze_directory(self, directory_path: Path) -> Dict[str, Dict[str, Any]]:
        """
        Analyse tous les fichiers Python d'un répertoire
        
        Args:
            directory_path: Chemin du répertoire
            
        Returns:
            Dictionnaire {filepath: analysis_result}
        """
        print(f"\n🔍 [{self.agent_name}] Analyse du répertoire {directory_path}...")
        
        results = {}
        
        # Trouver tous les fichiers Python
        python_files = list(directory_path.rglob("*.py"))
        
        # Filtrer les fichiers de test et __init__.py
        python_files = [
            f for f in python_files 
            if f.name != "__init__.py" and not f.name.startswith("test_")
        ]
        
        if not python_files:
            print("⚠️ Aucun fichier Python trouvé")
            return results
        
        print(f"📁 {len(python_files)} fichier(s) Python trouvé(s)")
        
        for file_path in python_files:
            try:
                # Lire le contenu
                with open(file_path, 'r', encoding='utf-8') as f:
                    code_content = f.read()
                
                # Analyser
                analysis = self.analyze_file(file_path, code_content)
                results[str(file_path)] = analysis
                
            except Exception as e:
                print(f"❌ Erreur lors de l'analyse de {file_path}: {e}")
                results[str(file_path)] = {
                    "error": str(e),
                    "status": "FAILED"
                }
        
        return results
    
    def get_refactoring_summary(self, analysis_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Génère un résumé global de tous les fichiers analysés
        
        Args:
            analysis_results: Résultats de l'analyse de tous les fichiers
            
        Returns:
            Résumé global
        """
        total_files = len(analysis_results)
        total_issues = sum(
            result.get("total_issues", 0) 
            for result in analysis_results.values()
        )
        
        avg_score = sum(
            result.get("pylint_score_before", 0) 
            for result in analysis_results.values()
        ) / max(total_files, 1)
        
        critical_files = [
            filepath 
            for filepath, result in analysis_results.items()
            if result.get("pylint_score_before", 10) < 5.0
        ]
        
        summary = {
            "total_files_analyzed": total_files,
            "total_issues_found": total_issues,
            "average_pylint_score": round(avg_score, 2),
            "critical_files": critical_files,
            "files_details": analysis_results
        }
        
        print(f"\n📊 Résumé global:")
        print(f"   - Fichiers analysés: {total_files}")
        print(f"   - Problèmes totaux: {total_issues}")
        print(f"   - Score moyen: {avg_score:.2f}/10.0")
        print(f"   - Fichiers critiques: {len(critical_files)}")
        
        return summary
