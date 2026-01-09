"""Liste tous les modèles Gemini disponibles avec ta clé API"""

import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

print("🔍 LISTE DES MODÈLES GEMINI DISPONIBLES")
print("=" * 70)

try:
    models = genai.list_models()
    
    print(f"\n✅ Nombre de modèles disponibles : {len(list(models))}\n")
    
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"📦 {model.name}")
            print(f"   Description : {model.description[:80]}...")
            print(f"   Methods : {model.supported_generation_methods}")
            print()
    
except Exception as e:
    print(f"❌ Erreur : {e}")

print("=" * 70)
print("\n💡 Copie un nom de modèle (ex: models/gemini-1.5-flash)")
print("   et utilise-le dans main.py")