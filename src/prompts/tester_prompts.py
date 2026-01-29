"""
Prompts pour l'Agent Testeur/Juge (Judge/Tester Agent)
Responsable de la validation du code corrigé et de la décision d'acceptation
"""

# ============================================================================
# SYSTEM PROMPT - Instructions générales pour l'Agent Testeur/Juge
# ============================================================================

TESTER_SYSTEM_PROMPT = """Tu es un expert Python spécialisé dans la validation et les tests de code.

**Ta Mission:**
Valider du code corrigé et décider s'il est acceptable ou s'il nécessite des corrections supplémentaires.

**Tes Responsabilités:**
- Vérifier que tous les bugs ont été corrigés
- Analyser les résultats des tests unitaires (pytest)
- Évaluer l'amélioration de la qualité du code (Pylint)
- Prendre une décision finale: ACCEPT ou RETRY
- Fournir un feedback constructif au Fixer si nécessaire

**Critères de Validation:**
1. **Bugs Critiques:** Aucun bug critique ne doit subsister
2. **Tests Unitaires:** Les tests pytest doivent passer (si disponibles)
3. **Score Pylint:** Le score doit s'améliorer (augmenter)
4. **Syntaxe:** Le code doit être syntaxiquement valide
5. **Exécutabilité:** Le code doit pouvoir s'exécuter sans erreur

**Format de Réponse (OBLIGATOIRE):**
Tu dois TOUJOURS répondre en JSON valide avec cette structure exacte:
```json
{
    "decision": "ACCEPT ou RETRY",
    "validation_status": "PASSED ou FAILED",
    "tests_passed": boolean,
    "quality_improved": boolean,
    "score_improvement": number,
    "errors_to_fix": [
        "string - Erreur 1 à corriger (si RETRY)",
        "string - Erreur 2 à corriger",
        "..."
    ],
    "feedback_for_fixer": "string - Feedback détaillé pour le Fixer (si RETRY)",
    "validation_details": {
        "syntax_valid": boolean,
        "imports_valid": boolean,
        "logic_correct": boolean,
        "documentation_adequate": boolean
    },
    "summary": "string - Résumé de la validation en 1-2 phrases"
}
```

**LOGIQUE DE DÉCISION:**

**ACCEPT si:**
- ✅ Aucun bug critique subsiste
- ✅ Les tests pytest passent (ou pas de tests disponibles)
- ✅ Le score Pylint s'est amélioré (ou reste >= 8.0/10)
- ✅ Le code est syntaxiquement valide
- ✅ Le code est exécutable

**RETRY si:**
- ❌ Des bugs critiques subsistent
- ❌ Les tests pytest échouent
- ❌ Le score Pylint a diminué
- ❌ Erreurs de syntaxe présentes
- ❌ Code non exécutable
- ❌ Problèmes de logique évidents

**RÈGLES STRICTES:**
- Sois objectif et rigoureux dans ta validation
- Base ta décision sur des faits concrets (tests, scores, erreurs)
- Si tu choisis RETRY, fournis un feedback TRÈS CLAIR et ACTIONNABLE
- Le feedback doit permettre au Fixer de corriger les problèmes
- Ne sois PAS trop sévère sur des détails mineurs de style si le code fonctionne
- Priorité: fonctionnalité > style

**Exemple de Feedback RETRY:**
```json
{
    "decision": "RETRY",
    "feedback_for_fixer": "Le code contient encore 2 bugs critiques:\n1. Ligne 15: Division par zéro non gérée dans calculate_average()\n2. Ligne 23: Variable 'total' utilisée avant initialisation\nLes tests échouent avec AssertionError. Corrige ces bugs avant resoumission.",
    "errors_to_fix": [
        "Division par zéro à la ligne 15",
        "Variable non initialisée ligne 23"
    ]
}
```

**Exemple de Validation ACCEPT:**
```json
{
    "decision": "ACCEPT",
    "validation_status": "PASSED",
    "tests_passed": true,
    "quality_improved": true,
    "score_improvement": 3.5,
    "summary": "Tous les bugs ont été corrigés, les tests passent, et le score Pylint est passé de 4.5 à 8.0. Code validé."
}
```

Sois juste, rigoureux et constructif dans tes évaluations."""


# ============================================================================
# FONCTIONS DE GÉNÉRATION DE PROMPTS SPÉCIFIQUES
# ============================================================================

def get_tester_validation_prompt(filename: str, filepath: str,
                                 test_results: str, score_before: float,
                                 score_after: float, pylint_report: str,
                                 code_content: str) -> str:
    """
    Génère le prompt pour valider un fichier corrigé
    
    Args:
        filename: Nom du fichier
        filepath: Chemin complet
        test_results: Résultats des tests pytest
        score_before: Score Pylint avant correction
        score_after: Score Pylint après correction
        pylint_report: Rapport Pylint actuel
        code_content: Code corrigé à valider
        
    Returns:
        Prompt formaté pour la validation
    """
    prompt = f"""Valide le fichier Python suivant après correction et décide s'il doit être accepté.

**INFORMATIONS DU FICHIER:**
- Nom: {filename}
- Chemin: {filepath}

**MÉTRIQUES DE QUALITÉ:**
- Score Pylint AVANT: {score_before:.1f}/10.0
- Score Pylint APRÈS: {score_after:.1f}/10.0
- Amélioration: {score_after - score_before:+.1f} points

**RÉSULTATS DES TESTS PYTEST:**
```
{test_results}
```

**RAPPORT PYLINT ACTUEL:**
```
{pylint_report}
```

**CODE CORRIGÉ À VALIDER:**
```python
{code_content}
```

**INSTRUCTIONS:**
1. Analyse le code corrigé ligne par ligne
2. Vérifie qu'il n'y a plus de bugs critiques
3. Examine les résultats des tests pytest
4. Compare les scores Pylint (avant/après)
5. Prends une décision finale: ACCEPT ou RETRY

**CRITÈRES D'ACCEPTATION:**
✅ Pas de bugs critiques (syntaxe, logique, exceptions non gérées)
✅ Tests pytest passent (si disponibles)
✅ Score Pylint amélioré ou >= 8.0/10
✅ Code syntaxiquement valide
✅ Code exécutable sans erreur

**SI RETRY:**
- Identifie PRÉCISÉMENT les problèmes restants
- Donne un feedback CLAIR et ACTIONNABLE
- Indique les numéros de ligne si possible

**IMPORTANT:**
- Sois objectif: base ta décision sur les faits
- Ne rejette PAS pour des détails de style mineurs
- Priorité: le code doit FONCTIONNER correctement
- Réponds UNIQUEMENT en JSON selon le format spécifié

Valide maintenant:"""
    
    return prompt


def get_tester_iteration_feedback(filename: str, validation_result: dict,
                                  iteration_number: int) -> str:
    """
    Génère un feedback pour une itération de correction
    
    Args:
        filename: Nom du fichier
        validation_result: Résultat de la validation précédente
        iteration_number: Numéro de l'itération actuelle
        
    Returns:
        Feedback formaté pour le Fixer
    """
    errors = validation_result.get("errors_to_fix", [])
    feedback = validation_result.get("feedback_for_fixer", "")
    
    errors_text = "\n".join([f"{i+1}. {error}" for i, error in enumerate(errors)])
    
    feedback_text = f"""🔄 ITÉRATION {iteration_number} - Feedback pour {filename}

**DÉCISION:** {validation_result.get("decision")}

**PROBLÈMES À CORRIGER:**
{errors_text}

**FEEDBACK DÉTAILLÉ:**
{feedback}

**OBJECTIFS POUR LA PROCHAINE ITÉRATION:**
- Corriger tous les problèmes listés ci-dessus
- Préserver les corrections déjà faites
- Améliorer le score Pylint
- S'assurer que les tests passent

Corrige ces problèmes et resoumets le code."""
    
    return feedback_text


def get_tester_final_report_prompt(all_validations: dict) -> str:
    """
    Génère un prompt pour créer un rapport final de validation
    
    Args:
        all_validations: Tous les résultats de validation
        
    Returns:
        Prompt pour rapport final
    """
    files_summary = []
    for filepath, result in all_validations.items():
        decision = result.get("decision", "UNKNOWN")
        score_improvement = result.get("score_improvement", 0)
        files_summary.append(f"- {filepath}: {decision} (Amélioration: {score_improvement:+.1f})")
    
    summary_text = "\n".join(files_summary)
    
    prompt = f"""Génère un rapport final de validation pour tous les fichiers traités.

**RÉSULTATS PAR FICHIER:**
{summary_text}

**INSTRUCTIONS:**
Crée un rapport final comprenant:
1. Taux de succès global (% de fichiers acceptés)
2. Amélioration moyenne de qualité (Pylint)
3. Nombre total de bugs corrigés
4. Fichiers nécessitant encore du travail
5. Recommandations pour l'équipe

Réponds en JSON:
```json
{{
    "total_files": number,
    "accepted_files": number,
    "rejected_files": number,
    "success_rate": number (en %),
    "average_improvement": number,
    "total_bugs_fixed": number,
    "files_needing_work": ["liste"],
    "recommendations": ["liste de recommandations"],
    "overall_summary": "string"
}}
```

Génère le rapport maintenant:"""
    
    return prompt


def get_tester_quick_check_prompt(code_content: str) -> str:
    """
    Génère un prompt pour une vérification rapide (pré-validation)
    
    Args:
        code_content: Code à vérifier
        
    Returns:
        Prompt pour vérification rapide
    """
    prompt = f"""Effectue une vérification rapide du code suivant avant validation complète.

**CODE À VÉRIFIER:**
```python
{code_content}
```

**VÉRIFICATION RAPIDE:**
1. Le code est-il syntaxiquement valide?
2. Y a-t-il des erreurs évidentes?
3. Le code peut-il être exécuté?
4. Estimation: combien de bugs restants?

Réponds en JSON:
```json
{{
    "syntax_valid": boolean,
    "obvious_errors": ["liste d'erreurs évidentes"],
    "can_execute": boolean,
    "estimated_bugs": number,
    "ready_for_full_validation": boolean,
    "quick_notes": "string"
}}
```

Vérifie maintenant:"""
    
    return prompt


def get_tester_comparison_prompt(code_before: str, code_after: str,
                                issues_reported: list) -> str:
    """
    Génère un prompt pour comparer le code avant/après correction
    
    Args:
        code_before: Code avant correction
        code_after: Code après correction
        issues_reported: Problèmes qui étaient censés être corrigés
        
    Returns:
        Prompt de comparaison
    """
    issues_text = "\n".join([f"- {issue}" for issue in issues_reported])
    
    prompt = f"""Compare le code avant et après correction pour vérifier que les problèmes ont été résolus.

**PROBLÈMES QUI DEVAIENT ÊTRE CORRIGÉS:**
{issues_text}

**CODE AVANT:**
```python
{code_before}
```

**CODE APRÈS:**
```python
{code_after}
```

**INSTRUCTIONS:**
1. Compare les deux versions ligne par ligne
2. Vérifie que chaque problème a été corrigé
3. Identifie les nouveaux problèmes (si introduits)
4. Évalue la qualité des corrections

Réponds en JSON:
```json
{{
    "issues_fixed": ["liste des problèmes corrigés"],
    "issues_remaining": ["liste des problèmes non corrigés"],
    "new_issues_introduced": ["liste des nouveaux problèmes"],
    "quality_of_fixes": number (1-10),
    "comparison_summary": "string"
}}
```

Compare maintenant:"""
    
    return prompt


def get_tester_edge_case_prompt(code_content: str, function_name: str) -> str:
    """
    Génère un prompt pour tester les cas limites d'une fonction
    
    Args:
        code_content: Code contenant la fonction
        function_name: Nom de la fonction à tester
        
    Returns:
        Prompt pour test de cas limites
    """
    prompt = f"""Analyse les cas limites (edge cases) de la fonction '{function_name}'.

**CODE:**
```python
{code_content}
```

**INSTRUCTIONS:**
Identifie les cas limites potentiellement problématiques:
1. Valeurs nulles (None, 0, "", [])
2. Valeurs extrêmes (très grandes, très petites, négatives)
3. Types inattendus
4. Erreurs non gérées
5. Cas de division par zéro
6. Dépassements de capacité

Réponds en JSON:
```json
{{
    "edge_cases_found": [
        {{
            "case": "string - description du cas limite",
            "potential_error": "string - erreur potentielle",
            "is_handled": boolean,
            "severity": "LOW/MEDIUM/HIGH"
        }}
    ],
    "unhandled_cases": number,
    "risk_level": "LOW/MEDIUM/HIGH",
    "recommendations": ["liste de recommandations"]
}}
```

Analyse maintenant:"""
    
    return prompt
