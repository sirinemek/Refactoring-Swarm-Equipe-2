import argparse
from pathlib import Path
from dotenv import load_dotenv
import os

from src.Agents.Auditeur import Auditor
from src.Agents.Fixer import Fixer
from src.Agents.judge import Judge

def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="The Refactoring Swarm")
    parser.add_argument(
        "--target_dir",
        type=str,
        required=True,
        help="Chemin vers le dossier contenant le code Python à analyser"
    )
    args = parser.parse_args()

    base_dir = Path(args.target_dir).resolve()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Erreur : La clé GEMINI_API_KEY n'est pas définie dans le fichier .env")
        return

    print(f"🔎 Démarrage de l'Auditeur sur {base_dir}")
    auditor = Auditor(base_dir, api_key)
    audit_results = auditor.analyze_all()

    print("\n🛠️ Démarrage du Correcteur")
    fixer = Fixer(base_dir, api_key)
    fixer.fix_all(audit_results)

    print("\n✅ Lancement des tests unitaires par le Testeur")
    judge = Judge(base_dir)
    success, logs = judge.test()

    if success:
        print("🎉 Tous les tests sont passés avec succès !")
    else:
        print("❌ Échec des tests unitaires :")
        print(logs)

if __name__ == "__main__":
    main()