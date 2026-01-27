"""
Orchestrateur principal - Coordonne les agents
"""
import os
import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

from .agents.auditor_agent import AuditorAgent
from .agents.fixer_agent import FixerAgent
from .agents.judge_agent import JudgeAgent
from .utils.tools import code_tools
from .utils.logger import logger, log_experiment, ActionType

class RefactoringOrchestrator:
    """Orchestrateur du système de refactoring"""
    
    def __init__(self, max_iterations: int = 10):
        """
        Initialise l'orchestrateur
        
        Args:
            max_iterations: Nombre maximum d'itérations
        """
        self.max_iterations = max_iterations
        
        # Initialiser les agents
        self.auditor = AuditorAgent()
        self.fixer = FixerAgent()
        self.judge = JudgeAgent()
        
        # État du système
        self.current_iteration = 0
        self.execution_id = logger.get_execution_id()
        self.results = {
            'execution_id': self.execution_id,
            'start_time': datetime.now().isoformat(),
            'iterations': [],
            'final_status': 'IN_PROGRESS'
        }
    
    def log_orchestration(self, action: str, details: Dict[str, Any], status: str = "SUCCESS"):
        """Log une action d'orchestration"""
        log_experiment(
            agent_name="Orchestrator",
            model_used="SYSTEM",
            action=ActionType.ANALYSIS,
            details={
                'action': action,
                'iteration': self.current_iteration,
                'details': details,
                'input_prompt': f"Orchestration step: {action}",
                'output_response': f"Status: {status}"
            },
            status=status
        )
    
    def prepare_workspace(self, target_dir: str, sandbox_dir: str = "sandbox") -> str:
        """
        Prépare l'espace de travail en copiant le code cible
        
        Args:
            target_dir: Répertoire cible
            sandbox_dir: Répertoire sandbox
            
        Returns:
            Chemin du sandbox préparé
        """
        try:
            # Créer un sandbox unique pour cette exécution
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            execution_sandbox = os.path.join(sandbox_dir, f"execution_{timestamp}")
            
            # Copier récursivement le contenu
            import shutil
            
            if os.path.exists(target_dir):
                # Créer le répertoire sandbox
                os.makedirs(execution_sandbox, exist_ok=True)
                
                # Copier le contenu
                for item in os.listdir(target_dir):
                    source = os.path.join(target_dir, item)
                    destination = os.path.join(execution_sandbox, item)
                    
                    if os.path.isdir(source):
                        shutil.copytree(source, destination, dirs_exist_ok=True)
                    else:
                        shutil.copy2(source, destination)
                
                print(f"✅ Workspace préparé: {execution_sandbox}")
                self.log_orchestration(
                    action="prepare_workspace",
                    details={'target_dir': target_dir, 'sandbox_dir': execution_sandbox}
                )
                
                return execution_sandbox
            else:
                raise Exception(f"Répertoire cible non trouvé: {target_dir}")
                
        except Exception as e:
            self.log_orchestration(
                action="prepare_workspace",
                details={'error': str(e)},
                status="ERROR"
            )
            raise
    
    def audit_phase(self, target_dir: str) -> Dict[str, Any]:
        """
        Phase d'audit: analyse le code
        
        Args:
            target_dir: Répertoire à analyser
            
        Returns:
            Résultats de l'audit
        """
        print(f"\n{'='*60}")
        print("PHASE 1: AUDIT")
        print(f"{'='*60}")
        
        self.log_orchestration(
            action="start_audit_phase",
            details={'target_dir': target_dir, 'iteration': self.current_iteration}
        )
        
        # Exécuter l'audit
        audit_result = self.auditor.process({'target': target_dir})
        
        if audit_result['success']:
            result = audit_result['result']
            
            print(f"📊 Analyse terminée:")
            print(f"  • Fichiers analysés: {result.get('files_analyzed', 0)}/{result.get('total_files', 0)}")
            print(f"  • Score qualité: {result.get('global_quality_score', 0):.2f}/10")
            print(f"  • Problèmes trouvés: {result.get('total_issues_found', 0)}")
            print(f"  • HIGH priority: {result.get('issues_by_severity', {}).get('HIGH', 0)}")
            
            self.log_orchestration(
                action="complete_audit_phase",
                details={
                    'summary': {
                        'files_analyzed': result.get('files_analyzed'),
                        'quality_score': result.get('global_quality_score'),
                        'issues_found': result.get('total_issues_found')
                    }
                }
            )
            
            return result
        else:
            print(f"❌ Échec audit: {audit_result.get('error')}")
            self.log_orchestration(
                action="audit_phase_failed",
                details={'error': audit_result.get('error')},
                status="ERROR"
            )
            raise Exception(f"Audit failed: {audit_result.get('error')}")
    
    def fix_phase(self, target_dir: str, refactoring_plan: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Phase de correction: applique le refactoring
        
        Args:
            target_dir: Répertoire à corriger
            refactoring_plan: Plan de refactoring
            
        Returns:
            Résultats des corrections
        """
        print(f"\n{'='*60}")
        print("PHASE 2: CORRECTION")
        print(f"{'='*60}")
        
        self.log_orchestration(
            action="start_fix_phase",
            details={'target_dir': target_dir, 'plan_items': len(refactoring_plan)}
        )
        
        # Organiser le plan par fichier
        plan_by_file = {}
        for item in refactoring_plan:
            files = item.get('files', [])
            for file in files:
                if file not in plan_by_file:
                    plan_by_file[file] = []
                plan_by_file[file].append(item)
        
        # Appliquer le plan fichier par fichier
        results = []
        files_processed = 0
        
        for filename, file_plan in plan_by_file.items():
            filepath = os.path.join(target_dir, filename)
            
            if os.path.exists(filepath):
                print(f"🔧 Traitement de {filename}...")
                
                fix_result = self.fixer.process({
                    'filepath': filepath,
                    'plan': file_plan
                })
                
                if fix_result['success']:
                    results.append(fix_result)
                    files_processed += 1
                    print(f"  ✅ {fix_result.get('changes_applied', 0)} changements appliqués")
                else:
                    print(f"  ❌ Erreur: {fix_result.get('error')}")
            else:
                print(f"  ⚠ Fichier non trouvé: {filename}")
        
        summary = {
            'files_processed': files_processed,
            'total_changes': sum(r.get('changes_applied', 0) for r in results),
            'results': results
        }
        
        print(f"\n📋 Résumé correction:")
        print(f"  • Fichiers traités: {summary['files_processed']}")
        print(f"  • Changements totaux: {summary['total_changes']}")
        
        self.log_orchestration(
            action="complete_fix_phase",
            details=summary
        )
        
        return summary
    
    def judge_phase(self, target_dir: str) -> Dict[str, Any]:
        """
        Phase de jugement: exécute les tests et évalue
        
        Args:
            target_dir: Répertoire à évaluer
            
        Returns:
            Résultats des tests
        """
        print(f"\n{'='*60}")
        print("PHASE 3: JUGEMENT")
        print(f"{'='*60}")
        
        self.log_orchestration(
            action="start_judge_phase",
            details={'target_dir': target_dir}
        )
        
        # Exécuter les tests
        test_result = self.judge.process({
            'target': target_dir,
            'evaluation_type': 'tests'
        })
        
        if test_result['success']:
            result = test_result['result']
            verdict = result.get('verdict', 'UNKNOWN')
            
            print(f"⚖️ Verdict: {verdict}")
            
            if 'test_results' in result:
                tests = result['test_results']
                print(f"🧪 Tests:")
                print(f"  • Total: {tests.get('total_tests', 0)}")
                print(f"  • Réussis: {tests.get('passed', 0)}")
                print(f"  • Échoués: {tests.get('failed', 0)}")
                print(f"  • Taux de réussite: {tests.get('passed_ratio', 0)*100:.1f}%")
            
            # Évaluer la qualité
            quality_result = self.judge.process({
                'target': target_dir,
                'evaluation_type': 'quality'
            })
            
            if quality_result['success']:
                quality = quality_result['result']
                print(f"📈 Qualité: {quality.get('verdict', 'UNKNOWN')}")
            
            self.log_orchestration(
                action="complete_judge_phase",
                details={
                    'verdict': verdict,
                    'test_results': result.get('test_results'),
                    'quality_metrics': quality.get('quality_metrics') if quality_result.get('success') else None
                }
            )
            
            return {
                'test_result': result,
                'quality_result': quality_result.get('result') if quality_result.get('success') else None,
                'verdict': verdict
            }
        else:
            print(f"❌ Échec tests: {test_result.get('error')}")
            self.log_orchestration(
                action="judge_phase_failed",
                details={'error': test_result.get('error')},
                status="ERROR"
            )
            
            return {
                'verdict': 'FAIL',
                'error': test_result.get('error')
            }
    
    def should_continue(self, judge_result: Dict[str, Any], iteration: int) -> bool:
        """
        Détermine si le processus doit continuer
        
        Args:
            judge_result: Résultats du jugement
            iteration: Itération actuelle
            
        Returns:
            True si on doit continuer
        """
        if iteration >= self.max_iterations:
            print("⏹ Limite d'itérations atteinte")
            return False
        
        verdict = judge_result.get('verdict', 'FAIL')
        
        if verdict == 'PASS':
            print("✅ Objectif atteint: tous les tests passent")
            return False
        elif verdict == 'NEEDS_IMPROVEMENT' and iteration < 3:
            # Donner quelques chances pour les améliorations
            return True
        elif verdict == 'FAIL':
            # Toujours réessayer en cas d'échec (dans la limite)
            return True
        else:
            return False
    
    def run(self, target_dir: str) -> Dict[str, Any]:
        """
        Exécute le processus complet de refactoring
        
        Args:
            target_dir: Répertoire cible
            
        Returns:
            Résultats finaux
        """
        print(f"\n{'='*60}")
        print("🚀 DÉMARRAGE DU REFACTORING SWARM")
        print(f"📁 Cible: {target_dir}")
        print(f"🆔 Execution ID: {self.execution_id}")
        print(f"{'='*60}")
        
        try:
            # Préparer le workspace
            workspace = self.prepare_workspace(target_dir)
            
            # Boucle principale
            while self.current_iteration < self.max_iterations:
                self.current_iteration += 1
                logger.increment_iteration()
                
                print(f"\n{'='*60}")
                print(f"🔄 ITÉRATION {self.current_iteration}/{self.max_iterations}")
                print(f"{'='*60}")
                
                iteration_result = {
                    'iteration': self.current_iteration,
                    'start_time': datetime.now().isoformat()
                }
                
                # Phase 1: Audit
                audit_result = self.audit_phase(workspace)
                iteration_result['audit'] = audit_result
                
                # Phase 2: Correction
                refactoring_plan = audit_result.get('refactoring_plan', [])
                if refactoring_plan:
                    fix_result = self.fix_phase(workspace, refactoring_plan)
                    iteration_result['fix'] = fix_result
                else:
                    print("ℹ️ Aucun plan de refactoring, passage au jugement")
                
                # Phase 3: Jugement
                judge_result = self.judge_phase(workspace)
                iteration_result['judge'] = judge_result
                
                iteration_result['end_time'] = datetime.now().isoformat()
                self.results['iterations'].append(iteration_result)
                
                # Déterminer si on continue
                if not self.should_continue(judge_result, self.current_iteration):
                    break
            
            # Résultats finaux
            self.results['end_time'] = datetime.now().isoformat()
            self.results['workspace'] = workspace
            self.results['total_iterations'] = self.current_iteration
            
            # Déterminer le statut final
            last_judge = self.results['iterations'][-1]['judge'] if self.results['iterations'] else {}
            if last_judge.get('verdict') == 'PASS':
                self.results['final_status'] = 'SUCCESS'
                print(f"\n🎉 RÉFACTORING RÉUSSI en {self.current_iteration} itération(s)")
            else:
                self.results['final_status'] = 'PARTIAL_SUCCESS' if self.current_iteration < self.max_iterations else 'MAX_ITERATIONS_REACHED'
                print(f"\n⚠️ RÉFACTORING TERMINÉ avec statut: {self.results['final_status']}")
            
            # Sauvegarder les résultats
            results_file = os.path.join('logs', f'execution_{self.execution_id}.json')
            with open(results_file, 'w') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            
            print(f"\n📊 RÉSULTATS DÉTAILLÉS:")
            print(f"  • Statut: {self.results['final_status']}")
            print(f"  • Itérations: {self.current_iteration}")
            print(f"  • Workspace: {workspace}")
            print(f"  • Logs: logs/experiment_data.json")
            print(f"  • Résultats: {results_file}")
            
            return self.results
            
        except Exception as e:
            self.results['end_time'] = datetime.now().isoformat()
            self.results['final_status'] = 'ERROR'
            self.results['error'] = str(e)
            
            print(f"\n❌ ERREUR CRITIQUE: {str(e)}")
            
            # Sauvegarder malgré l'erreur
            results_file = os.path.join('logs', f'execution_{self.execution_id}_error.json')
            with open(results_file, 'w') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            
            raise