
# ============================================================================
# SYSTEM PROMPT - Instructions générales pour l'Agent Auditeur
# ============================================================================

AUDITOR_SYSTEM_PROMPT = """Tu es un expert Python spécialisé dans l'analyse et le refactoring.

**Ta Mission:**
Analyser du code Python de mauvaise qualité et produire un plan de refactoring détaillé et structuré.

**Tes Compétences:**
- Détection de bugs (erreurs de syntaxe, logique, exceptions non gérées)
- Analyse de la qualité du code (PEP 8, conventions de nommage, complexité)
- Identification des problèmes de maintenabilité (code dupliqué, fonctions trop longues)


**Principes à Respecter:**
1. **Précision:** Indique toujours le numéro de ligne exact pour chaque problème
2. **Priorisation:** Distingue les problèmes CRITIQUES (bugs) des problèmes de QUALITÉ
3. **Clarté:** Explique pourquoi chaque problème est problématique
4. **Pragmatisme:** Propose des solutions concrètes et applicables

**Format de Réponse (OBLIGATOIRE):**
Tu dois TOUJOURS répondre en JSON valide avec cette structure exacte:
```json
{
    "critical_issues": [
        {
            "type": "string (ex: 'SyntaxError', 'UnboundVariable', 'DivisionByZero')",
            "line": number,
            "description": "string - Description claire du problème",
            "severity": "CRITICAL",
            "suggested_fix": "string - Comment corriger ce problème"
        }
    ],
    "quality_issues": [
        {
            "type": "string (ex: 'MissingDocstring', 'PEP8Violation', 'ComplexFunction')",
            "line": number,
            "description": "string - Description du problème de qualité",
            "severity": "QUALITY",
            "suggested_fix": "string - Comment améliorer"
        }
    ],
    "refactoring_plan": [
        "string - Étape 1 du plan de refactoring",
        "string - Étape 2 du plan de refactoring",
        "..."
    ],
    "total_issues": number,
    "summary": "string - Résumé en 1-2 phrases de l'état du code"
}
```

**RÈGLES STRICTES:**
- Ne génère JAMAIS de code dans tes réponses, seulement des analyses et plans
- Utilise TOUJOURS le format JSON ci-dessus
- Ne réponds JAMAIS en texte libre, uniquement en JSON
- Assure-toi que le JSON est valide (guillemets, virgules, etc.)
- Si le code est parfait, renvoie des listes vides [] mais respecte la structure


Sois rigoureux, méthodique et ne te limite pas aux problèmes évidents. Cherche aussi les bugs subtils."""


# ============================================================================
# FONCTIONS DE GÉNÉRATION DE PROMPTS SPÉCIFIQUES
# ============================================================================

def get_auditor_analysis_prompt(filename: str, filepath: str, 
                                pylint_score: float, pylint_report: str,
                                code_content: str) -> str:
    """
    Génère le prompt pour analyser un fichier Python
    
    Args:
        filename: Nom du fichier
        filepath: Chemin complet du fichier
        pylint_score: Score Pylint actuel
        pylint_report: Rapport Pylint complet
        code_content: Contenu du code source
        
    Returns:
        Prompt formaté pour l'analyse
    """
    prompt = f"""Analyse le fichier Python suivant et produis un plan de refactoring détaillé.

**INFORMATIONS DU FICHIER:**
- Nom: {filename}
- Chemin: {filepath}
- Score Pylint actuel: {pylint_score}/10.0

**RAPPORT PYLINT:**
```
{pylint_report}
```

**CODE SOURCE:**
```python
{code_content}
```

**INSTRUCTIONS:**
1. Identifie TOUS les problèmes critiques (bugs, erreurs de syntaxe, variables non définies, etc.)
2. Identifie TOUS les problèmes de qualité (PEP 8, docstrings manquantes, complexité excessive, etc.)
3. Pour chaque problème, indique:
   - Le type exact du problème
   - Le numéro de ligne précis
   - Une description claire
   - Une suggestion de correction
4. Priorise les problèmes (critiques avant qualité)
5. Génère un plan de refactoring étape par étape

**IMPORTANT:**
- Sois exhaustif: ne manque aucun problème
- Sois précis: donne les numéros de ligne exacts
- Sois pragmatique: propose des solutions concrètes
- Réponds UNIQUEMENT en JSON valide selon le format spécifié dans ton système

Analyse maintenant:"""
    
    return prompt


def get_auditor_reanalysis_prompt(filename: str, code_content: str,
                                  previous_issues: list) -> str:
    """
    Génère le prompt pour ré-analyser un fichier après correction
    
    Args:
        filename: Nom du fichier
        code_content: Code corrigé
        previous_issues: Liste des problèmes précédents
        
    Returns:
        Prompt pour la ré-analyse
    """
    issues_text = "\n".join([
        f"- [{issue.get('type')}] Ligne {issue.get('line')}: {issue.get('description')}"
        for issue in previous_issues
    ])
    
    prompt = f"""Ré-analyse le fichier Python suivant après correction.

**FICHIER:** {filename}

**PROBLÈMES PRÉCÉDEMMENT IDENTIFIÉS:**
{issues_text}

**CODE CORRIGÉ:**
```python
{code_content}
```

**INSTRUCTIONS:**
1. Vérifie si les problèmes précédents ont été corrigés
2. Identifie tout nouveau problème introduit par les corrections
3. Identifie tout problème qui persiste
4. Génère un rapport d'analyse mis à jour

**IMPORTANT:**
- Compare avec la liste des problèmes précédents
- Signale les problèmes résolus, persistants et nouveaux
- Réponds en JSON selon le format habituel

Analyse maintenant:"""
    
    return prompt


def get_auditor_quick_check_prompt(filename: str, code_content: str) -> str:
    """
    Génère un prompt pour une vérification rapide (pas d'analyse détaillée)
    
    Args:
        filename: Nom du fichier
        code_content: Contenu du code
        
    Returns:
        Prompt pour vérification rapide
    """
    prompt = f"""Effectue une vérification rapide du fichier Python suivant.

**FICHIER:** {filename}

**CODE:**
```python
{code_content}
```

**INSTRUCTIONS:**
Vérifie rapidement:
1. Y a-t-il des erreurs de syntaxe évidentes?
2. Y a-t-il des variables non définies?
3. Le code peut-il être exécuté sans erreur?
4. Estimation rapide: combien de problèmes critiques et de qualité?

Réponds en JSON avec:
```json
{{
    "can_execute": boolean,
    "estimated_critical_issues": number,
    "estimated_quality_issues": number,
    "quick_summary": "string - évaluation rapide"
}}
```

Vérifie maintenant:"""
    
    return prompt
