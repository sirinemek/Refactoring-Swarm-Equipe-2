"""
Prompt_Engineer.py
==================
Module central de gestion des prompts pour le système multi-agents

Responsable : [TON NOM]
Date : [DATE]

Ce module exporte toutes les fonctions de génération de prompts
pour les 3 agents du système de refactoring automatique.

Architecture :
    - Agent Auditeur : Analyse le code et génère un plan
    - Agent Correcteur : Applique les corrections
    - Agent Testeur : Valide les résultats
"""

from pathlib import Path
from typing import Dict, Any

# ============================================================
# IMPORTS DES PROMPTS DE CHAQUE AGENT
# ============================================================

# Import des fonctions du prompt Auditeur
from src.Prompts.auditor_prompts import (
    get_auditor_prompt,
    get_reaudit_prompt,
    AUDITOR_SYSTEM_PROMPT
)

# Import des fonctions du prompt Correcteur
from .fixer_prompts import (
    get_fixer_prompt,
    FIXER_SYSTEM_PROMPT
)

# Import des fonctions du prompt Testeur
from .judge_prompts import (
    get_judge_prompt,
    JUDGE_SYSTEM_PROMPT
)


# ============================================================
# MÉTADONNÉES DU MODULE
# ============================================================

__version__ = "1.0.0"
__author__ = "[TON NOM]"
__description__ = "Gestion centralisée des prompts pour le système multi-agents de refactoring"


# ============================================================
# FONCTION UTILITAIRE : Métadonnées
# ============================================================

def get_prompt_metadata() -> Dict[str, Any]:
    """
    Retourne les métadonnées du module de prompts.
    
    Utilisé pour le logging scientifique et la documentation.
    
    Returns:
        Dict contenant les informations sur le module
    """
    return {
        "module": "Prompt_Engineer",
        "version": __version__,
        "author": __author__,
        "description": __description__,
        
        "agents": {
            "auditor": {
                "name": "Agent Auditeur (The Auditor)",
                "role": "Analyse le code et génère un plan de refactoring",
                "functions": ["get_auditor_prompt", "get_reaudit_prompt"],
                "tools_used": ["list_python_files", "read_file", "run_pylint"]
            },
            "fixer": {
                "name": "Agent Correcteur (The Fixer)",
                "role": "Applique les corrections sur le code",
                "functions": ["get_fixer_prompt"],
                "tools_used": ["read_file", "write_file"]
            },
            "judge": {
                "name": "Agent Testeur (The Judge)",
                "role": "Valide les résultats et décide de la suite",
                "functions": ["get_judge_prompt"],
                "tools_used": ["run_pytest", "run_pylint"]
            }
        },
        
        "optimization_strategy": "context-aware, tool-focused",
        "token_saving_techniques": [
            "structured_output (JSON)",
            "clear_instructions",
            "examples_in_prompts",
            "no_markdown_in_responses"
        ],
        
        "quality_measures": [
            "Prompts testés avec Gemini API",
            "Format JSON validé",
            "Outils synchronisés avec l'Ingénieur Outils",
            "Exemples concrets dans chaque prompt"
        ]
    }


# ============================================================
# FONCTION UTILITAIRE : Validation
# ============================================================

def validate_prompt_response(response: str, expected_format: str = "json") -> bool:
    """
    Valide qu'une réponse de l'agent est dans le bon format.
    
    Args:
        response: La réponse reçue de Gemini
        expected_format: Format attendu ("json" ou "code")
        
    Returns:
        True si le format est valide, False sinon
    """
    import json
    
    if expected_format == "json":
        try:
            # Nettoie la réponse (enlève les markdown si présents)
            clean_response = response.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:]
            if clean_response.startswith("```"):
                clean_response = clean_response[3:]
            if clean_response.endswith("```"):
                clean_response = clean_response[:-3]
            
            # Tente de parser le JSON
            json.loads(clean_response.strip())
            return True
        except json.JSONDecodeError:
            return False
    
    elif expected_format == "code":
        # Vérifie que c'est du code (pas de markdown)
        if "```python" in response or "```" in response[:10]:
            return False
        return True
    
    return False


# ============================================================
# FONCTION UTILITAIRE : Statistiques
# ============================================================

def get_prompt_statistics() -> Dict[str, Any]:
    """
    Retourne des statistiques sur les prompts.
    
    Utile pour l'analyse et l'optimisation.
    
    Returns:
        Dict avec les statistiques
    """
    return {
        "auditor_prompt_length": len(AUDITOR_SYSTEM_PROMPT),
        "fixer_prompt_length": len(FIXER_SYSTEM_PROMPT),
        "judge_prompt_length": len(JUDGE_SYSTEM_PROMPT),
        
        "total_prompt_length": (
            len(AUDITOR_SYSTEM_PROMPT) + 
            len(FIXER_SYSTEM_PROMPT) + 
            len(JUDGE_SYSTEM_PROMPT)
        ),
        
        "estimated_tokens": {
            "auditor": len(AUDITOR_SYSTEM_PROMPT) // 4,  # Approximation : 1 token ≈ 4 chars
            "fixer": len(FIXER_SYSTEM_PROMPT) // 4,
            "judge": len(JUDGE_SYSTEM_PROMPT) // 4
        }
    }


# ============================================================
# EXPORTS PUBLICS
# ============================================================

__all__ = [
    # Fonctions principales
    "get_auditor_prompt",
    "get_reaudit_prompt",
    "get_fixer_prompt",
    "get_judge_prompt",
    
    # Fonctions utilitaires
    "get_prompt_metadata",
    "validate_prompt_response",
    "get_prompt_statistics",
    
    # Constantes (si le Lead Dev en a besoin)
    "AUDITOR_SYSTEM_PROMPT",
    "FIXER_SYSTEM_PROMPT",
    "JUDGE_SYSTEM_PROMPT"
]


# ============================================================
# EXEMPLE D'UTILISATION (pour documentation)
# ============================================================

if __name__ == "__main__":
    """
    Exemple d'utilisation du module Prompt_Engineer.
    
    Ce code n'est exécuté que si on lance directement ce fichier.
    Il sert de documentation pour le Lead Dev.
    """
    
    print("=" * 60)
    print("MODULE PROMPT_ENGINEER - DÉMONSTRATION")
    print("=" * 60)
    
    # Afficher les métadonnées
    print("\n📊 MÉTADONNÉES :")
    metadata = get_prompt_metadata()
    print(f"  Version : {metadata['version']}")
    print(f"  Auteur : {metadata['author']}")
    print(f"  Agents disponibles : {len(metadata['agents'])}")
    
    # Afficher les statistiques
    print("\n📈 STATISTIQUES :")
    stats = get_prompt_statistics()
    print(f"  Longueur totale des prompts : {stats['total_prompt_length']} caractères")
    print(f"  Tokens estimés (Auditeur) : ~{stats['estimated_tokens']['auditor']}")
    print(f"  Tokens estimés (Correcteur) : ~{stats['estimated_tokens']['fixer']}")
    print(f"  Tokens estimés (Testeur) : ~{stats['estimated_tokens']['judge']}")
    
    # Exemple d'utilisation des fonctions
    print("\n💡 EXEMPLE D'UTILISATION :")
    print("\nPour le Lead Dev, voici comment utiliser les prompts :\n")
    
    print("# 1. Obtenir le prompt de l'Auditeur")
    print("from src.prompts.Prompt_Engineer import get_auditor_prompt")
    print("prompt = get_auditor_prompt(Path('./sandbox/code'))")
    print("# → Retourne {'system': '...', 'user': '...'}\n")
    
    print("# 2. Obtenir le prompt du Correcteur")
    print("from src.prompts.Prompt_Engineer import get_fixer_prompt")
    print("prompt = get_fixer_prompt(")
    print("    file_path='calculator.py',")
    print("    current_code=code,")
    print("    refactoring_plan=plan")
    print(")\n")
    
    print("# 3. Obtenir le prompt du Testeur")
    print("from src.prompts.Prompt_Engineer import get_judge_prompt")
    print("prompt = get_judge_prompt(")
    print("    pylint_result=pylint_data,")
    print("    pytest_result=test_data,")
    print("    initial_score=4.5,")
    print("    iteration=1")
    print(")")
    
    print("\n" + "=" * 60)
    print("✅ Module Prompt_Engineer prêt à être utilisé !")
    print("=" * 60)