"""
Script de vérification de l'environnement
Vérifie que tout est correctement installé avant de lancer le TP
"""
import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Vérifie la version de Python"""
    print("🐍 Vérification de Python...")
    version = sys.version_info
    
    if version.major == 3 and version.minor in [10, 11]:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor} - Requis: 3.10 ou 3.11")
        return False


def check_package(package_name, import_name=None):
    """Vérifie qu'un package est installé"""
    if import_name is None:
        import_name = package_name.replace("-", "_")
    
    try:
        __import__(import_name)
        print(f"   ✅ {package_name}")
        return True
    except ImportError:
        print(f"   ❌ {package_name} - Installez avec: pip install {package_name}")
        return False


def check_packages():
    """Vérifie tous les packages requis"""
    print("\n📦 Vérification des packages...")
    
    packages = [
        ("google-generativeai", "google.generativeai"),
        ("pylint", "pylint"),
        ("pytest", "pytest"),
        ("python-dotenv", "dotenv"),
        ("colorama", "colorama")
    ]
    
    all_ok = True
    for package, import_name in packages:
        if not check_package(package, import_name):
            all_ok = False
    
    return all_ok


def check_env_file():
    """Vérifie la présence du fichier .env"""
    print("\n🔐 Vérification du fichier .env...")
    
    env_file = Path(".env")
    
    if not env_file.exists():
        print("   ❌ Fichier .env non trouvé")
        print("\n   📝 Créez un fichier .env avec:")
        print("      GOOGLE_API_KEY=votre_clé_ici")
        print("\n   🔑 Obtenez une clé gratuite sur:")
        print("      https://aistudio.google.com/app/apikey")
        return False
    
    # Vérifier le contenu
    content = env_file.read_text()
    if "GOOGLE_API_KEY" not in content:
        print("   ⚠️ GOOGLE_API_KEY non trouvée dans .env")
        return False
    
    if "AIzaSy" in content or len(content.split("=")[1].strip()) > 20:
        print("   ✅ Fichier .env configuré")
        return True
    else:
        print("   ⚠️ La clé API semble invalide")
        return False


def check_directories():
    """Vérifie la structure des répertoires"""
    print("\n📁 Vérification de la structure...")
    
    required_dirs = [
        "src",
        "src/agents",
        "src/prompts",
        "src/utils",
        "logs",
        "sandbox"
    ]
    
    all_ok = True
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"   ✅ {dir_path}/")
        else:
            print(f"   ❌ {dir_path}/ - Créez ce répertoire")
            all_ok = False
    
    return all_ok


def check_key_files():
    """Vérifie la présence des fichiers clés"""
    print("\n📄 Vérification des fichiers clés...")
    
    required_files = [
        "main.py",
        "requirements.txt",
        "src/utils/config.py",
        "src/utils/logger.py",
        "src/utils/tools.py",
        "src/agents/base_agent.py",
        "src/agents/auditor_agent.py",
        "src/agents/fixer_agent.py",
        "src/agents/judge_agent.py",
        "src/prompts/auditor_prompts.py",
        "src/prompts/fixer_prompts.py",
        "src/prompts/tester_prompts.py"
    ]
    
    all_ok = True
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - Fichier manquant")
            all_ok = False
    
    return all_ok


def test_api_connection():
    """Test de connexion à l'API Gemini"""
    print("\n🔌 Test de connexion à l'API Gemini...")
    
    try:
        from dotenv import load_dotenv
        import os
        import google.generativeai as genai
        
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            print("   ❌ Clé API non trouvée")
            return False
        
        genai.configure(api_key=api_key)
        
        # Test simple
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content("Réponds juste 'OK'")
        
        if "OK" in response.text.upper():
            print(f"   ✅ Connexion réussie - Réponse: {response.text.strip()}")
            return True
        else:
            print(f"   ⚠️ Réponse inattendue: {response.text}")
            return True  # Connexion OK quand même
            
    except Exception as e:
        print(f"   ❌ Erreur: {str(e)[:100]}")
        return False


def main():
    """Fonction principale"""
    print("="*60)
    print("🔍 VÉRIFICATION DE L'ENVIRONNEMENT")
    print("="*60)
    
    checks = [
        ("Python", check_python_version()),
        ("Packages", check_packages()),
        ("Fichier .env", check_env_file()),
        ("Structure", check_directories()),
        ("Fichiers clés", check_key_files()),
        ("API Gemini", test_api_connection())
    ]
    
    print("\n" + "="*60)
    print("📊 RÉSUMÉ")
    print("="*60)
    
    all_passed = True
    for name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"{status} {name}")
        if not passed:
            all_passed = False
    
    print("="*60)
    
    if all_passed:
        print("\n🎉 TOUT EST OK! Vous pouvez lancer le système.")
        print("\n🚀 Prochaines étapes:")
        print("   1. Créez un répertoire de test avec du code Python")
        print("   2. Lancez: python main.py --target_dir ./test")
        return 0
    else:
        print("\n⚠️ Certaines vérifications ont échoué.")
        print("   Corrigez les problèmes ci-dessus avant de continuer.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
