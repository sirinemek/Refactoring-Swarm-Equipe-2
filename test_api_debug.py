"""Debug complet de la configuration API"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

print("=" * 70)
print("🔍 DIAGNOSTIC COMPLET DE L'API GEMINI")
print("=" * 70)

# 1. Vérifier le fichier .env
print("\n[1/5] Vérification du fichier .env...")
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if api_key:
    print(f"✅ Clé API trouvée")
    print(f"   Longueur : {len(api_key)} caractères")
    print(f"   Début : {api_key[:10]}...")
    print(f"   Fin : ...{api_key[-10:]}")
else:
    print("❌ ERREUR : Clé API non trouvée dans .env")
    print("\n💡 SOLUTION :")
    print("   1. Vérifie que le fichier .env existe à la racine")
    print("   2. Vérifie qu'il contient : GOOGLE_API_KEY=ta_clé")
    print("   3. Pas d'espace, pas de guillemets")
    exit(1)

# 2. Vérifier le format de la clé
print("\n[2/5] Vérification du format de la clé...")
if api_key.startswith("AIza"):
    print("✅ Format correct (commence par 'AIza')")
else:
    print("⚠️  Format suspect (devrait commencer par 'AIza')")

# 3. Configurer l'API
print("\n[3/5] Configuration de l'API...")
try:
    genai.configure(api_key=api_key)
    print("✅ API configurée")
except Exception as e:
    print(f"❌ Erreur configuration : {e}")
    exit(1)

# 4. Lister les modèles
print("\n[4/5] Tentative de liste des modèles...")
try:
    models_list = list(genai.list_models())
    print(f"✅ Requête réussie")
    print(f"📊 Nombre de modèles : {len(models_list)}")
    
    if len(models_list) == 0:
        print("\n⚠️  LISTE VIDE - Problèmes possibles :")
        print("   1. La clé API n'a pas accès aux modèles Gemini")
        print("   2. La clé est invalide ou révoquée")
        print("   3. Le compte Google n'a pas activé l'API Gemini")
    else:
        print("\n📦 Modèles disponibles :")
        for model in models_list[:5]:
            print(f"   - {model.name}")
        if len(models_list) > 5:
            print(f"   ... et {len(models_list) - 5} autres")
    
except Exception as e:
    print(f"❌ Erreur lors de la requête : {e}")
    print(f"\n💡 Détails de l'erreur :")
    import traceback
    traceback.print_exc()

# 5. Test direct avec un modèle connu
print("\n[5/5] Test direct avec 'gemini-pro'...")
try:
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Réponds juste: OK")
    print(f"✅ Modèle 'gemini-pro' fonctionne !")
    print(f"   Réponse : {response.text}")
except Exception as e:
    error_str = str(e)
    print(f"❌ Erreur : {error_str[:200]}...")
    
    if "API key not valid" in error_str or "invalid" in error_str.lower():
        print("\n🔑 PROBLÈME DE CLÉ API DÉTECTÉ")
        print("   La clé est invalide, révoquée, ou n'a pas les permissions")
    elif "quota" in error_str.lower() or "429" in error_str:
        print("\n⏱️  PROBLÈME DE QUOTA")
        print("   Tu as dépassé les limites gratuites")
    elif "404" in error_str:
        print("\n📦 MODÈLE NON TROUVÉ")
        print("   Le modèle n'existe pas ou n'est pas accessible")

print("\n" + "=" * 70)
print("🏁 DIAGNOSTIC TERMINÉ")
print("=" * 70)