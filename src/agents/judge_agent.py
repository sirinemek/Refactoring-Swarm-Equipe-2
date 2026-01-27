"""
Agent Testeur - Exécute les tests et évalue le code
"""
import json
import os
from typing import Dict, Any, List
from .base_agent import BaseAgent
from ..utils.tools import code_tools
from ..utils.logger import ActionType

class JudgeAgent(BaseAgent):
    """Agent chargé d'exécuter les tests et d'évaluer la qualité du code"""
    
    def __init__(self):
        """Initialise l'agent testeur"""
        super().__init__(name="Judge_Agent")
        
        # Définir le prompt système
        system_prompt = """Tu es un expert senior en assurance qualité Python spécialisé en tests et validation.

TON RÔLE:
1. Exécuter et analyser les tests unitaires
2. Évaluer la qualité globale du code
3. Décider si le code est prêt pour la production
4. Identifier les régressions

CRITÈRES D'ÉVALUATION:
1. Tests unitaires: Tous doivent passer
2. Couverture de code: Idéalement > 80%
3. Qualité statique: Score Pylint > 8.0/10
4. Documentation: Docstrings complètes
5. Gestion d'erreurs: Appropriée
6. Performance: Aucune régression

FORMAT DE SORTIE ATTENDU (JSON):
{
  "verdict": "PASS|FAIL|NEEDS_IMPROVEMENT",
  "test_results": {
    "total_tests": 10,
    "passed": 8,
    "failed": 2,
    "passed_ratio": 0.8,
    "failed_tests": [
      {
        "test_name": "test_example",
        "error": "AssertionError",
        "details": "Détails de l'erreur"
      }
    ]
  },
  "quality_metrics": {
    "pylint_score": 7.5,
    "docstring_coverage": 0.6,
    "complexity_score": "MEDIUM"
  },
  "recommendations": [
    "Corriger les tests échoués",
    "Améliorer la documentation"
  ],
  "next_action": "CONTINUE_REFACTORING|RETRY_FIX|COMPLETE"
}

IMPORTANT:
- Sois objectif et basé sur les données
- Fournis des preuves concrètes
- Priorise la stabilité sur les nouvelles fonctionnalités
- Recommande des actions claires et réalisables"""
        
        self.set_system_prompt(system_prompt)
    
    def run_tests(self, target_path: str) -> Dict[str, Any]:
        """
        Exécute les tests sur un fichier/répertoire
        
        Args:
            target_path: Chemin vers les tests
            
        Returns:
            Résultats des tests
        """
        try:
            # Vérifier si le chemin existe
            if not os.path.exists(target_path):
                # Chercher des tests dans le répertoire parent
                parent_dir = os.path.dirname(target_path)
                if os.path.isdir(parent_dir):
                    target_path = parent_dir
            
            # Exécuter pytest
            test_results = code_tools.run_pytest(target_path)
            
            if not test_results['success']:
                return {
                    'success': False,
                    'error': test_results.get('error', 'Erreur inconnue pendant les tests')
                }
            
            # Analyser les résultats avec le LLM
            analysis_prompt = f"""
RÉSULTATS DES TESTS:
{json.dumps(test_results, indent=2)}

CODE TESTÉ: {target_path}

INSTRUCTIONS:
1. Analyse ces résultats de tests
2. Donne un verdict (PASS/FAIL/NEEDS_IMPROVEMENT)
3. Évalue la qualité globale
4. Recommande des actions
5. Suis strictement le format JSON demandé

CONTEXTE: Ce code vient d'être refactoré. Il doit maintenir sa fonctionnalité originale.
"""
            
            # Appeler le LLM pour l'analyse
            response = self.call_llm(
                prompt=analysis_prompt,
                context={'target_path': target_path, 'test_results': test_results},
                action_type=ActionType.ANALYSIS
            )
            
            # Parser la réponse
            try:
                if '```json' in response:
                    json_str = response.split('```json')[1].split('```')[0].strip()
                elif '```' in response:
                    json_str = response.split('```')[1].strip()
                    if json_str.startswith('json'):
                        json_str = json_str[4:].strip()
                else:
                    json_str = response.strip()
                
                analysis = json.loads(json_str)
                
                # Ajouter les résultats bruts
                analysis['raw_test_results'] = test_results
                
                return {
                    'success': True,
                    'result': analysis
                }
                
            except json.JSONDecodeError as e:
                return {
                    'success': False,
                    'error': f"Erreur parsing JSON: {str(e)}",
                    'raw_response': response
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Erreur exécution tests: {str(e)}"
            }
    
    def evaluate_quality(self, filepath: str) -> Dict[str, Any]:
        """
        Évalue la qualité d'un fichier
        
        Args:
            filepath: Chemin vers le fichier
            
        Returns:
            Évaluation de qualité
        """
        try:
            # Analyser avec pylint
            pylint_result = code_tools.run_pylint(filepath)
            
            # Analyser la structure
            structure_result = code_tools.analyze_code_structure(filepath)
            
            # Lire le code
            code_content = code_tools.read_file(filepath)
            
            # Créer le prompt d'évaluation
            evaluation_prompt = f"""
ÉVALUATION DE QUALITÉ: {filepath}

CODE:

RÉSULTATS PYLINT:
{json.dumps(pylint_result, indent=2) if pylint_result.get('success') else f"Erreur: {pylint_result.get('error', 'Unknown')}"}

ANALYSE STRUCTURELLE:
{json.dumps(structure_result, indent=2) if structure_result.get('success') else f"Erreur: {structure_result.get('error', 'Unknown')}"}

INSTRUCTIONS:
1. Évalue la qualité globale de ce code
2. Donne un score sur 10
3. Identifie les points forts et faibles
4. Recommande des améliorations
5. Décide si c'est "production ready"
6. Suis strictement le format JSON demandé
"""
            
            # Appeler le LLM
            response = self.call_llm(
                prompt=evaluation_prompt,
                context={'filepath': filepath},
                action_type=ActionType.ANALYSIS
            )
            
            # Parser la réponse
            try:
                if '```json' in response:
                    json_str = response.split('```json')[1].split('```')[0].strip()
                elif '```' in response:
                    json_str = response.split('```')[1].strip()
                    if json_str.startswith('json'):
                        json_str = json_str[4:].strip()
                else:
                    json_str = response.strip()
                
                evaluation = json.loads(json_str)
                
                # Ajouter les métriques objectives
                evaluation['objective_metrics'] = {
                    'pylint_score': pylint_result.get('score', 0) if pylint_result.get('success') else 0,
                    'docstring_coverage': structure_result.get('docstring_coverage', 0) if structure_result.get('success') else 0,
                    'lines_of_code': structure_result.get('lines', 0) if structure_result.get('success') else 0
                }
                
                return {
                    'success': True,
                    'result': evaluation
                }
                
            except json.JSONDecodeError as e:
                return {
                    'success': False,
                    'error': f"Erreur parsing JSON: {str(e)}",
                    'raw_response': response
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Erreur évaluation qualité: {str(e)}"
            }
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Traite une requête d'évaluation
        
        Args:
            input_data: Doit contenir 'target' et 'evaluation_type'
            
        Returns:
            Résultats de l'évaluation
        """
        target = input_data.get('target')
        evaluation_type = input_data.get('evaluation_type', 'tests')
        
        if not os.path.exists(target):
            return {
                'success': False,
                'error': f"Cible non trouvée: {target}"
            }
        
        if evaluation_type == 'tests':
            return self.run_tests(target)
        elif evaluation_type == 'quality':
            return self.evaluate_quality(target)
        else:
            return {
                'success': False,
                'error': f"Type d'évaluation inconnu: {evaluation_type}"
            }