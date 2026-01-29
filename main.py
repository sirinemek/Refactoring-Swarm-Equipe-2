"""
Point d'entrée principal du Refactoring Swarm
École Nationale Supérieure d'Informatique - 2025-2026
Enseignant: BATATA Sofiane
"""
import argparse
import sys
from pathlib import Path
from src.utils import config
from src.orchestrator import RefactoringOrchestrator


def print_banner():
    """Affiche la bannière du système"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║           🐝 THE REFACTORING SWARM 🐝                    ║
    ║                                                           ║
    ║     Système Multi-Agents de Refactoring Automatique      ║
    ║                                                           ║
    ║  École Nationale Supérieure d'Informatique               ║
    ║  Année Universitaire 2025-2026 - Niveau 1CS              ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def parse_arguments():
    """Parse les arguments de ligne de commande"""
    parser = argparse.ArgumentParser(
        description="The Refactoring Swarm - Système de refactoring automatique",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python main.py --target_dir ./test
  python main.py --target_dir ./sandbox/messy_code

Le système va:
  1. Analyser le code avec l'Agent Auditeur
  2. Corriger les bugs avec l'Agent Correcteur
  3. Valider avec l'Agent Testeur/Juge
  4. Itérer jusqu'à validation ou limite atteinte
        """
    )
    
    parser.add_argument(
        '--target_dir',
        type=str,
        required=True,
        help='Répertoire contenant le code à refactorer'
    )
    
    parser.add_argument(
        '--max_iterations',
        type=int,
        default=config.MAX_ITERATIONS,
        help=f'Nombre maximum d\'itérations (défaut: {config.MAX_ITERATIONS})'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Activer les logs détaillés'
    )
    
    return parser.parse_args()


def validate_target_dir(target_dir: str) -> bool:
    """
    Valide que le répertoire cible existe et contient des fichiers Python
    
    Args:
        target_dir: Chemin du répertoire cible
        
    Returns:
        True si valide
    """
    target_path = Path(target_dir)
    
    if not target_path.exists():
        print(f"❌ Erreur: Le répertoire '{target_dir}' n'existe pas")
        return False
    
    if not target_path.is_dir():
        print(f"❌ Erreur: '{target_dir}' n'est pas un répertoire")
        return False
    
    # Vérifier qu'il y a au moins un fichier Python
    python_files = list(target_path.rglob("*.py"))
    if not python_files:
        print(f"⚠️ Attention: Aucun fichier Python trouvé dans '{target_dir}'")
        return False
    
    return True


def main():
    """Fonction principale"""
    try:
        # Afficher la bannière
        print_banner()
        
        # Parser les arguments
        args = parse_arguments()
        
        # Mettre à jour la config si nécessaire
        if args.max_iterations != config.MAX_ITERATIONS:
            config.MAX_ITERATIONS = args.max_iterations
        
        if args.verbose:
            config.VERBOSE = True
        
        # Afficher la configuration
        print("\n📋 CONFIGURATION:")
        print(f"   - Répertoire cible: {args.target_dir}")
        print(f"   - Max itérations: {config.MAX_ITERATIONS}")
        print(f"   - Modèle LLM: {config.MODEL_NAME}")
        print(f"   - Sandbox: {config.SANDBOX_DIR}")
        print(f"   - Logs: {config.EXPERIMENT_LOG_FILE}")
        
        # Vérifier la configuration
        print("\n🔧 Vérification de la configuration...")
        if not config.validate_config():
            print("❌ Configuration invalide")
            return 1
        print("✅ Configuration valide")
        
        # Valider le répertoire cible
        if not validate_target_dir(args.target_dir):
            print("\n💡 Assurez-vous que:")
            print("   1. Le répertoire existe")
            print("   2. Il contient au moins un fichier .py")
            return 1
        
        # Créer et lancer l'orchestrateur
        print("\n🚀 Lancement du système...")
        
        orchestrator = RefactoringOrchestrator(args.target_dir)
        summary = orchestrator.run()
        
        # Afficher le rapport final
        orchestrator.print_final_report(summary)
        
        # Retourner 0 si succès, 1 sinon
        if summary.get("workflow_status") == "COMPLETED":
            success_rate = summary.get("success_rate", 0)
            return 0 if success_rate >= 50 else 1
        else:
            return 1
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Interruption par l'utilisateur")
        return 130
    
    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
