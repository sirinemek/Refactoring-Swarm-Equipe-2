"""Test rapide de la clé API Gemini"""

import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

print("🧪 Test des modèles Gemini disponibles...")
print("=" * 60)

# ✅ NOMS CORRECTS DES MODÈLES (mis à jour)
modeles = [
    "gemini-1.5-flash",           # Sans "-latest"
    "gemini-1.5-pro",             # Sans "-latest"
    "gemini-pro",                 # Ancien nom stable
    "gemini-1.0-pro",             # Version 1.0
]

for modele_name in modeles:
    try:
        print(f"\n🔍 Test : {modele_name}")
        model = genai.GenerativeModel(modele_name)
        response = model.generate_content("Dis juste: OK")
        print(f"✅ {modele_name} : FONCTIONNE !")
        print(f"   Réponse : {response.text}")
        print(f"\n💡 UTILISE CE MODÈLE : {modele_name}")
        break
    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg:
            print(f"❌ {modele_name} : Modèle non trouvé (404)")
        else:
            print(f"❌ {modele_name} : {error_msg[:80]}...")

print("\n" + "=" * 60)