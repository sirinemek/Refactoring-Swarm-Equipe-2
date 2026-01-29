"""
Configuration du système Refactoring Swarm
École Nationale Supérieure d'Informatique - 2025-2026
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# ============================================================================
# CONFIGURATION LLM
# ============================================================================

# Modèle Gemini à utiliser (TESTÉ ET FONCTIONNEL)
MODEL_NAME = "gemini-2.5-flash"  # OU "gemini-2.0-flash-exp" OU "gemini-1.5-flash"

# Clé API Google
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError(
        "❌ GOOGLE_API_KEY non trouvée!\n"
        "   1. Créez un fichier .env à la racine du projet\n"
        "   2. Ajoutez: GOOGLE_API_KEY=votre_clé_ici\n"
        "   3. Obtenez une clé gratuite: https://aistudio.google.com/app/apikey"
    )

# ============================================================================
# CONFIGURATION DU SYSTÈME
# ============================================================================

# Nombre maximum d'itérations de correction
MAX_ITERATIONS = 10

# Nombre de tentatives pour les appels LLM
MAX_RETRIES = 3

# Timeout pour les appels LLM (secondes)
LLM_TIMEOUT = 60

# ============================================================================
# CHEMINS
# ============================================================================

# Répertoire racine du projet
ROOT_DIR = Path(__file__).parent

# Répertoire sandbox (où le code est copié et modifié)
SANDBOX_DIR = ROOT_DIR / "sandbox"

# Répertoire des logs
LOGS_DIR = ROOT_DIR / "logs"

# Fichier de logs JSON
EXPERIMENT_LOG_FILE = LOGS_DIR / "experiment_data.json"

# Fichier de résumé final
SUMMARY_FILE = LOGS_DIR / "refactoring_summary.json"

# ============================================================================
# PARAMÈTRES PYLINT
# ============================================================================

# Score Pylint minimum acceptable
MIN_PYLINT_SCORE = 5.0

# Score Pylint cible
TARGET_PYLINT_SCORE = 8.0

# ============================================================================
# PARAMÈTRES DE LOGGING
# ============================================================================

# Activer les logs détaillés
VERBOSE = True

# Activer les couleurs dans le terminal
COLORFUL_OUTPUT = True

# ============================================================================
# VALIDATION
# ============================================================================

def validate_config():
    """Valide la configuration"""
    errors = []
    
    if not GOOGLE_API_KEY or len(GOOGLE_API_KEY) < 20:
        errors.append("❌ GOOGLE_API_KEY invalide ou manquante")
    
    if MAX_ITERATIONS < 1 or MAX_ITERATIONS > 20:
        errors.append(f"❌ MAX_ITERATIONS doit être entre 1 et 20 (actuel: {MAX_ITERATIONS})")
    
    if errors:
        print("\n".join(errors))
        return False
    
    return True


def ensure_directories():
    """Crée les répertoires nécessaires s'ils n'existent pas"""
    SANDBOX_DIR.mkdir(exist_ok=True)
    LOGS_DIR.mkdir(exist_ok=True)


# ============================================================================
# INITIALISATION
# ============================================================================

# Créer les répertoires au chargement du module
ensure_directories()

# Afficher la configuration si verbose
if VERBOSE and __name__ != "__main__":
    print("✅ Configuration chargée avec succès")
