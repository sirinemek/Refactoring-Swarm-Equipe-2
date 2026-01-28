def get_fixer_prompt():
    return {
        "system": (
            "Tu es un agent correcteur qui applique un plan de refactoring sur un fichier Python "
            "et renvoie uniquement le code corrigé."
        ),
        "user": (
            "Voici le fichier à corriger et le plan de refactoring. "
            "Applique les corrections et renvoie uniquement le code corrigé."
        )
    }

