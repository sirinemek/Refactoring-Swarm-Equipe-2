#!/usr/bin/env python3
"""
Point d'entrée principal du Refactoring Swarm
"""
import os
import sys
import argparse
from datetime import datetime

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.orchestrator import RefactoringOrchestrator
from src.utils.logger import logger

def parse_arguments():
    """Parse les arguments de ligne de commande"""
    parser = argparse.ArgumentParser(
        description='The Refactoring Swarm - Système multi-agents de refactoring automatique',
        epilog='Exemple: python main.py --target_dir "./sandbox/dataset"'
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
        default=10,
        help='Nombre maximum d\'itérations (défaut: 10)'
    )
    
    parser.add_argument(
        '--sandbox_dir',
        type=str,
        default='sandbox',
        help='Répertoire sandbox pour les modifications (défaut: sandbox)'
    )
    
    return parser.parse_args()

def validate_environment():
    """Valide l'environnement d'exécution"""
    # Vérifier la clé API
    if not os.getenv('GOOGLE_API_KEY'):
        print("❌ ERREUR: GOOGLE_API_KEY non configurée")
        print("  1. Créez un fichier .env à partir de .env.example")
        print("  2. Ajoutez votre clé Google Gemini")
        print("  3. Ne committez JAMAIS le fichier .env")
        return False
    
    # Vérifier les dossiers requis
    required_dirs = ['src', 'logs', 'sandbox']
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            print(f"❌ ERREUR: Dossier '{dir_name}' manquant")
            return False
    
    return True

def print_banner():
    """Affiche la bannière du système"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                THE REFACTORING SWARM                         ║
║         Système Multi-Agents de Refactoring Automatique      ║
║                    TP IGL 2025-2026                          ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def main():
    """Fonction principale"""
    # Afficher la bannière
    print_banner()
    
    # Parser les arguments
    args = parse_arguments()
    
    # Valider l'environnement
    if not validate_environment():
        sys.exit(1)
    
    # Vérifier que le répertoire cible existe
    if not os.path.exists(args.target_dir):
        print(f"❌ ERREUR: Le répertoire cible n'existe pas: {args.target_dir}")
        sys.exit(1)
    
    print(f"📁 Répertoire cible: {args.target_dir}")
    print(f"🔄 Itérations max: {args.max_iterations}")
    print(f"🆔 Execution ID: {logger.get_execution_id()}")
    print(f"⏰ Début: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Créer et exécuter l'orchestrateur
        orchestrator = RefactoringOrchestrator(max_iterations=args.max_iterations)
        results = orchestrator.run(args.target_dir)
        
        # Afficher le résumé
        print("\n" + "="*60)
        print("📋 RÉSUMÉ DE L'EXÉCUTION")
        print("="*60)
        
        if results['final_status'] == 'SUCCESS':
            print("✅ SUCCÈS: Tous les tests passent")
        elif results['final_status'] == 'PARTIAL_SUCCESS':
            print("⚠️ SUCCÈS PARTIEL: Améliorations faites mais tests non passants")
        elif results['final_status'] == 'MAX_ITERATIONS_REACHED':
            print("⏹ LIMITE D'ITÉRATIONS ATTEINTE")
        else:
            print("❌ ÉCHEC: Une erreur est survenue")
        
        print(f"📊 Itérations effectuées: {results['total_iterations']}")
        print(f"📁 Workspace final: {results.get('workspace', 'N/A')}")
        print(f"📄 Logs: logs/experiment_data.json")
        
        # Vérifier la qualité des logs
        log_summary = logger.get_log_summary()
        if not isinstance(log_summary, dict) or 'error' in log_summary:
            print("⚠️ ATTENTION: Problème avec les logs")
        else:
            print(f"📝 Entrées de log: {log_summary.get('total_entries', 0)}")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⏹ Interruption par l'utilisateur")
        return 130
    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())