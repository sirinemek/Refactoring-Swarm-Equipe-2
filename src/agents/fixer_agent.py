"""
Agent Correcteur - Modifie le code selon le plan de refactoring
"""
import json
import os
from typing import Dict, Any, List
from .base_agent import BaseAgent
from ..utils.tools import code_tools
from ..utils.logger import ActionType

class FixerAgent(BaseAgent):
    """Agent chargé de corriger le code selon le plan de refactoring"""
    
    def __init__(self):
        """Initialise l'agent correcteur"""
        super().__init__(name="Fixer_Agent")
        
        # Définir le prompt système
        system_prompt = """Tu es un expert senior en développement Python spécialisé en refactoring et correction de code.

TON RÔLE:
1. Implémenter les corrections spécifiées dans le plan de refactoring
2. Corriger les bugs identifiés
3. Améliorer la qualité du code sans changer sa fonctionnalité
4. Assurer que le code reste fonctionnel après modifications

RÈGLES STRICTES:
- NE CHANGE PAS la fonctionnalité du code (sauf pour corriger des bugs)
- RESPECTE les conventions PEP 8
- AJOUTE des docstrings si manquantes
- AMÉLIORE la lisibilité
- OPTIMISE les performances si possible
- GÈRE les erreurs proprement
- ÉCRIS des commentaires explicatifs pour les modifications complexes
- VALIDE la syntaxe Python après chaque modification

FORMAT DE SORTIE ATTENDU (JSON):
{
  "modified_file": "nom_du_fichier.py",
  "original_code": "code original",
  "modified_code": "code modifié",
  "changes_made": [
    {
      "line_start": 10,
      "line_end": 15,
      "change_type": "BUG_FIX|STYLE_IMPROVEMENT|OPTIMIZATION|DOCUMENTATION",
      "description": "Description de la modification",
      "reason": "Raison de la modification"
    }
  ],
  "validation_result": {
    "syntax_valid": true,
    "message": "Message de validation"
  }
}

IMPORTANT:
- Modifie UNIQUEMENT ce qui est nécessaire
- Garde les tests existants fonctionnels
- Documente tes changements
- Sois conservatif: mieux vaut peu de changements bien faits que beaucoup de changements risqués"""
        
        self.set_system_prompt(system_prompt)
    
    def apply_fix(self, filepath: str, issue: Dict[str, Any], original_code: str = None) -> Dict[str, Any]:
        """
        Applique une correction spécifique
        
        Args:
            filepath: Chemin vers le fichier
            issue: Description du problème à corriger
            original_code: Code original (optionnel)
            
        Returns:
            Résultat de la correction
        """
        try:
            # Lire le code original si non fourni
            if original_code is None:
                original_code = code_tools.read_file(filepath)
            
            # Créer le prompt de correction
            fix_prompt = f"""
FICHIER À CORRIGER: {filepath}

PROBLÈME À RÉSOUDRE:
{json.dumps(issue, indent=2)}

CODE ORIGINAL:

INSTRUCTIONS:
1. Corrige EXACTEMENT le problème spécifié
2. Modifie le MINIMUM de code nécessaire
3. Garde la même fonctionnalité (sauf pour corriger des bugs)
4. Améliore la qualité si pertinent
5. Fournis le code complet modifié
6. Liste les changements effectués
7. Valide la syntaxe Python

FORMAT DE RÉPONSE: JSON strict comme spécifié
"""
            
            # Appeler le LLM
            response = self.call_llm(
                prompt=fix_prompt,
                context={'filepath': filepath, 'issue': issue},
                action_type=ActionType.FIX
            )
            
            # Parser la réponse
            try:
                # Extraire le JSON
                if '```json' in response:
                    json_str = response.split('```json')[1].split('```')[0].strip()
                elif '```' in response:
                    json_str = response.split('```')[1].strip()
                    if json_str.startswith('json'):
                        json_str = json_str[4:].strip()
                else:
                    json_str = response.strip()
                
                fix_result = json.loads(json_str)
                
                # Valider la syntaxe du code modifié
                validation_result = code_tools.validate_python_syntax(
                    fix_result.get('modified_code', '')
                )
                
                fix_result['validation_result'] = {
                    'syntax_valid': validation_result[0],
                    'message': validation_result[1]
                }
                
                return {
                    'success': True,
                    'result': fix_result,
                    'filepath': filepath
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
                'error': f"Erreur application correctif: {str(e)}"
            }
    
    def apply_refactoring_plan(self, filepath: str, plan_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Applique un plan de refactoring complet sur un fichier
        
        Args:
            filepath: Chemin vers le fichier
            plan_items: Items du plan à appliquer
            
        Returns:
            Résultat du refactoring
        """
        try:
            original_code = code_tools.read_file(filepath)
            current_code = original_code
            all_changes = []
            
            print(f"  🔧 Application du plan sur {os.path.basename(filepath)}...")
            
            # Appliquer chaque item du plan
            for i, plan_item in enumerate(plan_items):
                print(f"    📝 Étape {i+1}/{len(plan_items)}: {plan_item.get('action')}")
                
                # Créer une "issue" artificielle à partir du plan
                issue = {
                    'description': plan_item.get('description', ''),
                    'issue_type': plan_item.get('action', 'IMPROVEMENT'),
                    'severity': 'MEDIUM',
                    'suggestion': plan_item.get('description', '')
                }
                
                # Appliquer la correction
                fix_result = self.apply_fix(filepath, issue, current_code)
                
                if fix_result['success']:
                    result = fix_result['result']
                    current_code = result.get('modified_code', current_code)
                    
                    # Collecter les changements
                    if 'changes_made' in result:
                        all_changes.extend(result['changes_made'])
            
            # Écrire le code final
            if current_code != original_code:
                code_tools.write_file(filepath, current_code)
                
                # Vérifier avec pylint
                pylint_result = code_tools.run_pylint(filepath)
                
                return {
                    'success': True,
                    'filepath': filepath,
                    'changes_applied': len(all_changes),
                    'pylint_score_improvement': pylint_result.get('score', 0),
                    'all_changes': all_changes,
                    'pylint_result': pylint_result
                }
            else:
                return {
                    'success': True,
                    'filepath': filepath,
                    'changes_applied': 0,
                    'message': 'Aucune modification nécessaire'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Erreur application plan: {str(e)}"
            }
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Traite une requête de correction
        
        Args:
            input_data: Doit contenir 'filepath' et 'plan' ou 'issue'
            
        Returns:
            Résultats de la correction
        """
        filepath = input_data.get('filepath')
        plan = input_data.get('plan')
        issue = input_data.get('issue')
        
        if not os.path.exists(filepath):
            return {
                'success': False,
                'error': f"Fichier non trouvé: {filepath}"
            }
        
        if plan:
            return self.apply_refactoring_plan(filepath, plan)
        elif issue:
            return self.apply_fix(filepath, issue)
        else:
            return {
                'success': False,
                'error': "Données insuffisantes: fournir 'plan' ou 'issue'"
            }