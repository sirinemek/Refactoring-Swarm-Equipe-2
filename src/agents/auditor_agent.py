"""
Agent Auditeur - Analyse le code et produit un plan de refactoring
"""
import json
import os
import traceback
from typing import Dict, Any, List
from .base_agent import BaseAgent
from ..utils.tools import code_tools
from ..utils.logger import ActionType

class AuditorAgent(BaseAgent):
    """Agent chargé d'analyser le code et de produire un plan de refactoring"""
    
    def __init__(self):
        """Initialise l'agent auditeur"""
        super().__init__(name="Auditor_Agent")
        
        # Définir le prompt système SIMPLIFIÉ pour Gemini
        system_prompt = """Tu es un expert senior en génie logiciel Python spécialisé en analyse de code et refactoring.

TON RÔLE:
1. Analyser le code Python pour identifier les problèmes
2. Produire un plan de refactoring détaillé et priorisé
3. Proposer des améliorations de qualité

PROBLÈMES À DÉTECTER:
- Erreurs de syntaxe
- Bugs potentiels
- Violations des conventions PEP 8
- Code dupliqué
- Complexité cyclomatique excessive
- Absence de docstrings
- Mauvaises pratiques d'import
- Gestion d'erreurs insuffisante
- Optimisations possibles

FORMAT DE SORTIE ATTENDU (JSON):
{
  "analysis_summary": "Résumé de l'analyse",
  "quality_score": 7.5,
  "issues_found": [
    {
      "file": "nom_du_fichier.py",
      "line": 42,
      "issue_type": "BUG|STYLE|QUALITY|SECURITY|PERFORMANCE",
      "description": "Description détaillée du problème",
      "severity": "HIGH|MEDIUM|LOW",
      "suggestion": "Correction suggérée"
    }
  ],
  "refactoring_plan": [
    {
      "priority": 1,
      "action": "FIX_BUG|IMPROVE_STYLE|ADD_TESTS|OPTIMIZE|DOCUMENT",
      "file": "nom_du_fichier.py",
      "description": "Description de l'action",
      "estimated_effort": "SMALL|MEDIUM|LARGE"
    }
  ],
  "recommendations": [
    "Recommandation 1",
    "Recommandation 2"
  ]
}

IMPORTANT:
- Sois précis et factuel
- Donne des exemples de code corrigé quand c'est pertinent
- Priorise les bugs sur les améliorations de style
- Considère la maintenabilité à long terme
- Utilise UNIQUEMENT le format JSON ci-dessus
- Ne mets pas de texte avant ou après le JSON"""
        
        self.set_system_prompt(system_prompt)
    
    def analyze_file(self, filepath: str) -> Dict[str, Any]:
        """
        Analyse un fichier Python
        
        Args:
            filepath: Chemin vers le fichier
            
        Returns:
            Résultats de l'analyse
        """
        try:
            print(f"    📖 Lecture du fichier: {os.path.basename(filepath)}")
            
            # Lire le fichier
            code_content = code_tools.read_file(filepath)
            
            if not code_content or len(code_content.strip()) == 0:
                print(f"    ⚠️ Fichier vide ou presque vide")
                return {
                    'success': True,
                    'result': {
                        'file': filepath,
                        'analysis_summary': 'Fichier vide ou presque vide',
                        'quality_score': 10.0,
                        'issues_found': [],
                        'refactoring_plan': [],
                        'recommendations': ['Fichier vide, aucun refactoring nécessaire']
                    }
                }
            
            print(f"    📏 Taille: {len(code_content)} caractères, {len(code_content.splitlines())} lignes")
            
            # Analyser avec pylint
            print(f"    🔍 Exécution de pylint...")
            pylint_result = code_tools.run_pylint(filepath)
            
            if not pylint_result.get('success'):
                print(f"    ⚠️ Pylint échoué: {pylint_result.get('error', 'Erreur inconnue')}")
            
            # Analyser la structure
            print(f"    📊 Analyse structurelle...")
            structure_result = code_tools.analyze_code_structure(filepath)
            
            if not structure_result.get('success'):
                print(f"    ⚠️ Analyse structurelle échouée: {structure_result.get('error', 'Erreur inconnue')}")
            
            # Préparer le code pour l'analyse (prendre un échantillon raisonnable)
            code_sample = code_content
            if len(code_content) > 4000:
                code_sample = code_content[:2000] + "\n... [CODE TRONQUÉ POUR RAISON DE LONGUEUR] ...\n" + code_content[-2000:]
            
            # Créer le prompt d'analyse SIMPLIFIÉ
            analysis_prompt = f"""
ANALYSE DU FICHIER: {os.path.basename(filepath)}

CONTENU DU CODE:

INFORMATIONS TECHNIQUES:
- Score Pylint: {pylint_result.get('score', 'N/A') if pylint_result.get('success') else 'ERREUR'}
- Lignes de code: {structure_result.get('lines', 'N/A') if structure_result.get('success') else 'ERREUR'}
- Fonctions: {structure_result.get('functions', 'N/A') if structure_result.get('success') else 'ERREUR'}
- Classes: {structure_result.get('classes', 'N/A') if structure_result.get('success') else 'ERREUR'}
- Couverture docstrings: {structure_result.get('docstring_coverage', 'N/A') if structure_result.get('success') else 'ERREUR'}

INSTRUCTIONS DÉTAILLÉES:
1. Analyse ce code Python en détail
2. Identifie TOUS les problèmes (bugs, style, qualité, sécurité, performance)
3. Produis un plan de refactoring priorisé (du plus critique au moins critique)
4. Donne un score de qualité sur 10 (1=très mauvais, 10=excellent)
5. Fournis des recommandations concrètes pour l'amélioration
6. UTILISE UNIQUEMENT LE FORMAT JSON CI-DESSOUS, SANS AUCUN TEXTE AVANT OU APRÈS

FORMAT JSON REQUIS (doit être exactement ça):
{{
  "analysis_summary": "Résumé en 1-2 phrases",
  "quality_score": 7.5,
  "issues_found": [
    {{
      "file": "{os.path.basename(filepath)}",
      "line": 42,
      "issue_type": "BUG",
      "description": "Description claire du problème",
      "severity": "HIGH",
      "suggestion": "Solution suggérée"
    }}
  ],
  "refactoring_plan": [
    {{
      "priority": 1,
      "action": "FIX_BUG",
      "file": "{os.path.basename(filepath)}",
      "description": "Description de l'action à faire",
      "estimated_effort": "SMALL"
    }}
  ],
  "recommendations": [
    "Recommandation 1",
    "Recommandation 2"
  ]
}}

REMARQUE IMPORTANTE: 
- Sois factuel et précis
- Ne sors pas du format JSON
- Priorise les bugs et problèmes critiques
- Sois constructif dans les suggestions
"""
            
            print(f"    🤖 Appel du LLM pour analyse...")
            
            # Appeler le LLM
            response = self.call_llm(
                prompt=analysis_prompt,
                context={'filepath': filepath},
                action_type=ActionType.ANALYSIS
            )
            
            print(f"    📄 Réponse reçue ({len(response)} caractères)")
            
            if not response or len(response.strip()) == 0:
                print(f"    ❌ Réponse vide du LLM")
                return {
                    'success': False,
                    'error': "Réponse vide du LLM"
                }
            
            # Parser la réponse
            try:
                # Nettoyer la réponse - chercher le JSON
                response_clean = response.strip()
                
                # Essayer d'extraire le JSON si entouré de backticks
                if '```json' in response_clean:
                    json_str = response_clean.split('```json')[1].split('```')[0].strip()
                elif '```' in response_clean:
                    # Chercher n'importe quel bloc de code
                    parts = response_clean.split('```')
                    if len(parts) >= 2:
                        json_str = parts[1].strip()
                        if json_str.startswith('json'):
                            json_str = json_str[4:].strip()
                    else:
                        json_str = response_clean
                else:
                    json_str = response_clean
                
                # Nettoyer davantage si nécessaire
                json_str = json_str.strip()
                
                # S'assurer que c'est du JSON valide
                if not (json_str.startswith('{') and json_str.endswith('}')):
                    # Essayer de trouver le JSON dans la réponse
                    start_idx = json_str.find('{')
                    end_idx = json_str.rfind('}')
                    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                        json_str = json_str[start_idx:end_idx+1]
                
                print(f"    🔧 Tentative de parsing JSON ({len(json_str)} caractères)...")
                print(f"    🔍 Début du JSON: {json_str[:100]}...")
                
                analysis_result = json.loads(json_str)
                
                # Validation des champs requis
                required_fields = ['analysis_summary', 'quality_score', 'issues_found', 'refactoring_plan', 'recommendations']
                for field in required_fields:
                    if field not in analysis_result:
                        print(f"    ⚠️ Champ manquant: {field}")
                        analysis_result[field] = [] if field.endswith('s') else ""
                
                # Ajouter les métadonnées
                analysis_result['file'] = filepath
                analysis_result['pylint_results'] = pylint_result
                analysis_result['structure_analysis'] = structure_result
                
                # Valider le score de qualité
                try:
                    quality_score = float(analysis_result.get('quality_score', 5.0))
                    if quality_score < 0 or quality_score > 10:
                        analysis_result['quality_score'] = 5.0
                except (ValueError, TypeError):
                    analysis_result['quality_score'] = 5.0
                
                print(f"    ✅ Analyse réussie pour {os.path.basename(filepath)}")
                print(f"    📊 Score qualité: {analysis_result.get('quality_score', 'N/A')}")
                print(f"    🐛 Problèmes trouvés: {len(analysis_result.get('issues_found', []))}")
                print(f"    📋 Plan d'actions: {len(analysis_result.get('refactoring_plan', []))}")
                
                return {
                    'success': True,
                    'result': analysis_result
                }
                
            except json.JSONDecodeError as e:
                print(f"    ❌ Erreur parsing JSON: {str(e)}")
                print(f"    📋 Réponse brute (500 premiers caractères): {response[:500]}")
                
                # Créer un résultat par défaut en cas d'échec
                default_result = {
                    'file': filepath,
                    'analysis_summary': f'Analyse automatique - erreur de parsing JSON: {str(e)[:100]}',
                    'quality_score': 5.0,
                    'issues_found': [
                        {
                            'file': os.path.basename(filepath),
                            'line': 1,
                            'issue_type': 'QUALITY',
                            'description': f'Erreur lors de l\'analyse: {str(e)[:100]}',
                            'severity': 'MEDIUM',
                            'suggestion': 'Vérifier la syntaxe du code'
                        }
                    ],
                    'refactoring_plan': [
                        {
                            'priority': 1,
                            'action': 'DEBUG',
                            'file': os.path.basename(filepath),
                            'description': 'Diagnostiquer les problèmes d\'analyse',
                            'estimated_effort': 'SMALL'
                        }
                    ],
                    'recommendations': [
                        'Vérifier que le code est syntaxiquement valide',
                        'Simplifier le code pour faciliter l\'analyse'
                    ],
                    'pylint_results': pylint_result,
                    'structure_analysis': structure_result,
                    'parsing_error': True
                }
                
                return {
                    'success': True,
                    'result': default_result,
                    'warning': f"JSON parsing error, using default analysis: {str(e)}"
                }
                
        except Exception as e:
            print(f"    ❌ Exception dans analyze_file: {str(e)}")
            traceback.print_exc()
            
            return {
                'success': False,
                'error': f"Erreur analyse fichier: {str(e)}"
            }
    
    def analyze_directory(self, directory: str) -> Dict[str, Any]:
        """
        Analyse tous les fichiers Python d'un répertoire
        
        Args:
            directory: Répertoire à analyser
            
        Returns:
            Analyse globale
        """
        try:
            print(f"📁 Analyse du répertoire: {directory}")
            
            # Lister les fichiers Python
            python_files = code_tools.list_files(directory, ['.py'])
            
            if not python_files:
                print(f"❌ Aucun fichier Python trouvé dans {directory}")
                return {
                    'success': False,
                    'error': f"Aucun fichier Python trouvé dans {directory}"
                }
            
            print(f"📁 {len(python_files)} fichiers Python trouvés")
            
            # Analyser chaque fichier
            all_issues = []
            all_plans = []
            total_score = 0
            files_analyzed = 0
            successful_analyses = []
            failed_analyses = []
            
            for filepath in python_files:
                print(f"\n  🔍 Analyse de {os.path.basename(filepath)}...")
                
                file_analysis = self.analyze_file(filepath)
                
                if file_analysis['success']:
                    result = file_analysis['result']
                    successful_analyses.append(result)
                    
                    # Collecter les issues
                    if 'issues_found' in result:
                        for issue in result['issues_found']:
                            # S'assurer que chaque issue a un fichier
                            if 'file' not in issue or not issue['file']:
                                issue['file'] = os.path.basename(filepath)
                            all_issues.append(issue)
                    
                    # Collecter les plans
                    if 'refactoring_plan' in result:
                        for plan_item in result['refactoring_plan']:
                            # S'assurer que chaque plan a un fichier
                            if 'file' not in plan_item or not plan_item['file']:
                                plan_item['file'] = os.path.basename(filepath)
                            all_plans.append(plan_item)
                    
                    # Calculer le score moyen
                    if 'quality_score' in result:
                        try:
                            score = float(result['quality_score'])
                            total_score += score
                            files_analyzed += 1
                        except (ValueError, TypeError):
                            print(f"    ⚠️ Score de qualité invalide: {result.get('quality_score')}")
                else:
                    print(f"    ❌ Échec de l'analyse: {file_analysis.get('error')}")
                    failed_analyses.append({
                        'file': filepath,
                        'error': file_analysis.get('error', 'Erreur inconnue')
                    })
            
            print(f"\n📊 Résumé de l'analyse du répertoire:")
            print(f"  • Fichiers analysés avec succès: {len(successful_analyses)}/{len(python_files)}")
            print(f"  • Fichiers en échec: {len(failed_analyses)}")
            
            if files_analyzed == 0:
                print(f"⚠️ Aucun fichier n'a pu être analysé correctement")
                return {
                    'success': False,
                    'error': "Aucun fichier n'a pu être analysé correctement",
                    'failed_analyses': failed_analyses
                }
            
            # Créer le rapport global
            global_analysis = {
                'directory': directory,
                'total_files': len(python_files),
                'files_analyzed': files_analyzed,
                'files_failed': len(failed_analyses),
                'global_quality_score': total_score / files_analyzed if files_analyzed > 0 else 0,
                'total_issues_found': len(all_issues),
                'issues_by_severity': {
                    'HIGH': sum(1 for i in all_issues if i.get('severity', '').upper() == 'HIGH'),
                    'MEDIUM': sum(1 for i in all_issues if i.get('severity', '').upper() == 'MEDIUM'),
                    'LOW': sum(1 for i in all_issues if i.get('severity', '').upper() == 'LOW')
                },
                'issues_by_type': {
                    'BUG': sum(1 for i in all_issues if i.get('issue_type', '').upper() == 'BUG'),
                    'STYLE': sum(1 for i in all_issues if i.get('issue_type', '').upper() == 'STYLE'),
                    'QUALITY': sum(1 for i in all_issues if i.get('issue_type', '').upper() == 'QUALITY'),
                    'SECURITY': sum(1 for i in all_issues if i.get('issue_type', '').upper() == 'SECURITY'),
                    'PERFORMANCE': sum(1 for i in all_issues if i.get('issue_type', '').upper() == 'PERFORMANCE')
                },
                'all_issues': all_issues,
                'refactoring_plan': self._consolidate_plan(all_plans),
                'recommendations': self._generate_global_recommendations(all_issues),
                'successful_analyses': successful_analyses,
                'failed_analyses': failed_analyses
            }
            
            # Afficher un résumé détaillé
            print(f"📈 Score qualité global: {global_analysis['global_quality_score']:.2f}/10")
            print(f"🐛 Total des problèmes: {global_analysis['total_issues_found']}")
            print(f"   • HIGH: {global_analysis['issues_by_severity']['HIGH']}")
            print(f"   • MEDIUM: {global_analysis['issues_by_severity']['MEDIUM']}")
            print(f"   • LOW: {global_analysis['issues_by_severity']['LOW']}")
            print(f"📋 Plan consolidé: {len(global_analysis['refactoring_plan'])} actions")
            
            return {
                'success': True,
                'result': global_analysis
            }
            
        except Exception as e:
            print(f"❌ Erreur analyse répertoire: {str(e)}")
            traceback.print_exc()
            
            return {
                'success': False,
                'error': f"Erreur analyse répertoire: {str(e)}"
            }
    
    def _consolidate_plan(self, plans: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Consolide les plans de refactoring"""
        if not plans:
            return []
        
        # Grouper par priorité et type d'action
        consolidated = {}
        
        for item in plans:
            # Normaliser les clés
            priority = item.get('priority', 999)
            action = item.get('action', 'UNKNOWN').upper()
            file = item.get('file', 'unknown.py')
            
            key = f"{priority}_{action}"
            
            if key not in consolidated:
                consolidated[key] = {
                    'priority': priority,
                    'action': action,
                    'files': [],
                    'description': item.get('description', f'{action} action'),
                    'estimated_effort': item.get('estimated_effort', 'MEDIUM')
                }
            
            if file not in consolidated[key]['files']:
                consolidated[key]['files'].append(file)
        
        # Trier par priorité
        sorted_items = sorted(consolidated.values(), key=lambda x: x['priority'])
        
        # Limiter à 10 actions principales
        return sorted_items[:10]
    
    def _generate_global_recommendations(self, issues: List[Dict[str, Any]]) -> List[str]:
        """Génère des recommandations globales basées sur les issues"""
        recommendations = []
        
        if not issues:
            recommendations.append("✅ Code propre, aucune action urgente nécessaire")
            recommendations.append("✅ Considérer des améliorations incrémentales de style")
            return recommendations
        
        # Analyser les patterns
        high_priority_issues = [i for i in issues if i.get('severity', '').upper() == 'HIGH']
        style_issues = [i for i in issues if i.get('issue_type', '').upper() == 'STYLE']
        doc_issues = [i for i in issues if 'docstring' in str(i.get('description', '')).lower()]
        bug_issues = [i for i in issues if i.get('issue_type', '').upper() == 'BUG']
        
        if high_priority_issues:
            recommendations.append(f"🚨 PRIORITÉ ABSOLUE: Corriger les {len(high_priority_issues)} problèmes HIGH priority")
        
        if bug_issues:
            recommendations.append(f"🐛 Corriger les {len(bug_issues)} bugs identifiés")
        
        if style_issues and len(style_issues) > 5:
            recommendations.append(f"🎨 Appliquer un formateur automatique (black, autopep8) pour {len(style_issues)} violations de style")
        
        if doc_issues:
            recommendations.append(f"📝 Ajouter des docstrings: {len(doc_issues)} fonctions/classes en manquent")
        
        # Recommandations basées sur le volume
        if len(issues) > 50:
            recommendations.append("🔄 Refactoring majeur recommandé: le code a de nombreux problèmes")
        elif len(issues) > 20:
            recommendations.append("⚡ Refactoring modéré recommandé: plusieurs améliorations possibles")
        elif len(issues) > 5:
            recommendations.append("🔧 Refactoring léger recommandé: quelques améliorations identifiées")
        else:
            recommendations.append("✅ Code relativement propre, améliorations incrémentales suffisantes")
        
        # Recommandation technique
        recommendations.append("🧪 S'assurer que tous les tests passent avant le déploiement")
        
        return recommendations[:5]  # Limiter à 5 recommandations
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Traite une requête d'analyse
        
        Args:
            input_data: Doit contenir 'target' (chemin fichier ou répertoire)
            
        Returns:
            Résultats de l'analyse
        """
        target = input_data.get('target')
        
        if not target:
            return {
                'success': False,
                'error': "Paramètre 'target' manquant dans input_data"
            }
        
        print(f"🎯 Début de l'analyse de: {target}")
        
        if os.path.isdir(target):
            return self.analyze_directory(target)
        elif os.path.isfile(target):
            result = self.analyze_file(target)
            # Pour un seul fichier, formater comme une analyse de répertoire
            if result['success']:
                analysis = result['result']
                return {
                    'success': True,
                    'result': {
                        'directory': os.path.dirname(target),
                        'total_files': 1,
                        'files_analyzed': 1,
                        'files_failed': 0,
                        'global_quality_score': float(analysis.get('quality_score', 5.0)),
                        'total_issues_found': len(analysis.get('issues_found', [])),
                        'issues_by_severity': {
                            'HIGH': sum(1 for i in analysis.get('issues_found', []) if i.get('severity', '').upper() == 'HIGH'),
                            'MEDIUM': sum(1 for i in analysis.get('issues_found', []) if i.get('severity', '').upper() == 'MEDIUM'),
                            'LOW': sum(1 for i in analysis.get('issues_found', []) if i.get('severity', '').upper() == 'LOW')
                        },
                        'all_issues': analysis.get('issues_found', []),
                        'refactoring_plan': self._consolidate_plan(analysis.get('refactoring_plan', [])),
                        'recommendations': analysis.get('recommendations', ['Analyse complétée']),
                        'successful_analyses': [analysis],
                        'failed_analyses': []
                    }
                }
            else:
                return result
        else:
            return {
                'success': False,
                'error': f"Cible non trouvée: {target}"
            }