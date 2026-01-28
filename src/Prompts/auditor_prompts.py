def get_auditor_prompt(base_dir):
    """
    Retourne les prompts pour l'agent Auditeur.
    Tu peux étendre ça avec des versions ou d'autres prompts.
    """
    return {
        "system": (
            "Tu es un agent auditeur qui analyse du code Python pour détecter bugs, "
            "mauvaises pratiques, et propose un plan de refactoring précis."
        ),
        "user": (
            "Analyse ce code, identifie les erreurs et problèmes, "
            "et propose un plan de refactoring détaillé fichier par fichier. "
            "Format attendu : JSON avec clés 'errors' (liste des erreurs détectées) "
            "et 'refactoring_plan' (liste des étapes à appliquer)."
        )
    }