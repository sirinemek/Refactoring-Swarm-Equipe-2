"""
Orchestrateur du Refactoring Swarm
Coordonne l'exécution des agents Auditor, Fixer et Judge
"""
import shutil
import json
from pathlib import Path
from typing import Dict, Any
from src.agents import AuditorAgent, FixerAgent, JudgeAgent
from src.utils import config, get_logger_stats


class RefactoringOrchestrator:
    """Orchestre le workflow de refactoring"""
    
    def __init__(self, target_dir: str):
        """
        Initialise l'orchestrateur
        
        Args:
            target_dir: Répertoire contenant le code à refactorer
        """
        self.target_dir = Path(target_dir)
        self.sandbox_dir = config.SANDBOX_DIR / self.target_dir.name
        
        # Initialiser les agents
        print("\n" + "="*60)
        print("🚀 INITIALISATION DU SYSTÈME REFACTORING SWARM")
        print("="*60)
        
        self.auditor = AuditorAgent()
        self.fixer = FixerAgent()
        self.judge = JudgeAgent()
        
        print("="*60)
        
        # Résultats
        self.analysis_results = {}
        self.fix_results = {}
        self.validation_results = {}
    
    def setup_sandbox(self) -> bool:
        """
        Copie le code cible dans le sandbox
        
        Returns:
            True si succès
        """
        try:
            # Créer le sandbox s'il n'existe pas
            if self.sandbox_dir.exists():
                shutil.rmtree(self.sandbox_dir)
            
            # Copier le code
            shutil.copytree(self.target_dir, self.sandbox_dir)
            
            print(f"📁 Code copié dans le sandbox: {self.sandbox_dir}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de la création du sandbox: {e}")
            return False
    
    def run(self) -> Dict[str, Any]:
        """
        Lance le workflow complet de refactoring
        
        Returns:
            Résumé final
        """
        print("\n" + "="*60)
        print("🎬 DÉMARRAGE DU WORKFLOW DE REFACTORING")
        print("="*60)
        
        # Étape 0: Préparer le sandbox
        if not self.setup_sandbox():
            return self._create_failure_summary("Échec de la préparation du sandbox")
        
        # Étape 1: AUDIT
        print("\n" + "🔍"*20)
        print("ÉTAPE 1: AUDIT DU CODE")
        print("🔍"*20)
        
        self.analysis_results = self.auditor.analyze_directory(self.sandbox_dir)
        
        if not self.analysis_results:
            return self._create_failure_summary("Aucun fichier analysé")
        
        # Étape 2: CORRECTION
        print("\n" + "🔧"*20)
        print("ÉTAPE 2: CORRECTION DU CODE")
        print("🔧"*20)
        
        self.fix_results = self.fixer.fix_all_files(self.analysis_results)
        
        if not self.fix_results:
            return self._create_failure_summary("Aucune correction effectuée")
        
        # Étape 3: VALIDATION + ITÉRATIONS
        print("\n" + "⚖️"*20)
        print("ÉTAPE 3: VALIDATION ET ITÉRATIONS")
        print("⚖️"*20)
        
        iteration = 1
        max_iterations = config.MAX_ITERATIONS
        
        while iteration <= max_iterations:
            print(f"\n{'='*60}")
            print(f"🔄 ITÉRATION {iteration}/{max_iterations}")
            print(f"{'='*60}")
            
            # Valider tous les fichiers
            self.validation_results = self.judge.validate_all_files(
                self.fix_results,
                self.analysis_results
            )
            
            # Vérifier si des corrections supplémentaires sont nécessaires
            needs_retry, feedback = self.judge.check_iteration_needed(
                self.validation_results,
                iteration,
                max_iterations
            )
            
            if not needs_retry:
                print("\n✅ Validation terminée avec succès!")
                break
            
            if iteration >= max_iterations:
                print(f"\n⚠️ Limite d'itérations atteinte ({max_iterations})")
                break
            
            # Appliquer les corrections itératives
            print(f"\n🔄 Application des corrections itératives...")
            
            for filepath, error_report in feedback.items():
                if error_report == "MAX_ITERATIONS_REACHED":
                    continue
                
                try:
                    file_path = Path(filepath)
                    
                    # Lire le code actuel
                    with open(file_path, 'r', encoding='utf-8') as f:
                        current_code = f.read()
                    
                    # Correction avec feedback
                    fix_result = self.fixer.fix_with_feedback(
                        file_path,
                        current_code,
                        error_report
                    )
                    
                    # Appliquer
                    fixed_code = fix_result.get("fixed_code", "")
                    if fixed_code:
                        self.fixer.apply_fix(file_path, fixed_code)
                        self.fix_results[filepath] = fix_result
                        self.fix_results[filepath]["applied"] = True
                    
                except Exception as e:
                    print(f"❌ Erreur itération {filepath}: {e}")
            
            iteration += 1
        
        # Générer le résumé final
        final_summary = self._create_final_summary()
        
        # Sauvegarder le résumé
        self._save_summary(final_summary)
        
        return final_summary
    
    def _create_final_summary(self) -> Dict[str, Any]:
        """Crée le résumé final du workflow"""
        
        # Statistiques de validation
        judge_summary = self.judge.get_final_summary(self.validation_results)
        
        # Statistiques de logging
        logger_stats = get_logger_stats()
        
        # Scores Pylint
        scores_before = [
            analysis.get("pylint_score_before", 0)
            for analysis in self.analysis_results.values()
            if "pylint_score_before" in analysis
        ]
        
        scores_after = [
            validation.get("score_after", 0)
            for validation in self.validation_results.values()
            if "score_after" in validation
        ]
        
        avg_before = sum(scores_before) / len(scores_before) if scores_before else 0
        avg_after = sum(scores_after) / len(scores_after) if scores_after else 0
        
        summary = {
            "workflow_status": "COMPLETED",
            "files_processed": len(self.analysis_results),
            "files_fixed": len(self.fix_results),
            "files_validated": len(self.validation_results),
            "success_rate": judge_summary.get("success_rate", 0),
            "quality_metrics": {
                "average_score_before": round(avg_before, 2),
                "average_score_after": round(avg_after, 2),
                "improvement": round(avg_after - avg_before, 2)
            },
            "validation_details": judge_summary,
            "logging_stats": logger_stats,
            "sandbox_directory": str(self.sandbox_dir)
        }
        
        return summary
    
    def _create_failure_summary(self, reason: str) -> Dict[str, Any]:
        """Crée un résumé d'échec"""
        return {
            "workflow_status": "FAILED",
            "reason": reason,
            "files_processed": len(self.analysis_results),
            "logging_stats": get_logger_stats()
        }
    
    def _save_summary(self, summary: Dict[str, Any]):
        """Sauvegarde le résumé dans un fichier JSON"""
        try:
            with open(config.SUMMARY_FILE, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Résumé sauvegardé dans: {config.SUMMARY_FILE}")
            
        except Exception as e:
            print(f"⚠️ Erreur sauvegarde résumé: {e}")
    
    def print_final_report(self, summary: Dict[str, Any]):
        """Affiche le rapport final"""
        print("\n" + "="*60)
        print("📊 RÉSUMÉ FINAL")
        print("="*60)
        
        print(f"\n📈 Statistiques:")
        print(f"   - Fichiers traités: {summary.get('files_processed', 0)}")
        print(f"   - Réussis: {summary.get('validation_details', {}).get('successful_files', 0)} ✅")
        print(f"   - Échoués: {summary.get('validation_details', {}).get('failed_files', 0)} ❌")
        print(f"   - Taux de succès: {summary.get('success_rate', 0):.1f}%")
        
        quality = summary.get("quality_metrics", {})
        print(f"\n📊 Qualité du code:")
        print(f"   - Score moyen avant: {quality.get('average_score_before', 0):.2f}/10.0")
        print(f"   - Score moyen après: {quality.get('average_score_after', 0):.2f}/10.0")
        print(f"   - Amélioration: {quality.get('improvement', 0):+.2f}")
        
        logger_stats = summary.get("logging_stats", {})
        print(f"\n📝 Données collectées:")
        print(f"   - Actions loggées: {logger_stats.get('total_actions', 0)}")
        print(f"   - Taux de succès: {logger_stats.get('success_rate', 0):.1f}%")
        
        print("\n" + "="*60)
        print("✨ WORKFLOW TERMINÉ")
        print("="*60)
        
        # Message de conclusion
        success_rate = summary.get('success_rate', 0)
        if success_rate >= 80:
            print("\n🎉 MISSION ACCOMPLIE avec succès!")
        elif success_rate >= 50:
            print("\n⚠️ MISSION PARTIELLEMENT ACCOMPLIE")
        else:
            print("\n❌ MISSION ÉCHOUÉE - Des améliorations sont nécessaires")
        
       
