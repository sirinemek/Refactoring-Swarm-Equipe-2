#!/usr/bin/env python3
"""Test simple de l'API Gemini"""
import os
import sys
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ GOOGLE_API_KEY non configurée")
    sys.exit(1)

print("🔑 Clé API détectée")
print("🤖 Test de connexion à Gemini...")

try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=api_key,
        temperature=0.1,
        max_output_tokens=500,
        convert_system_message_to_human=True
    )
    
    response = llm.invoke("Bonjour! Réponds simplement 'OK' si tu fonctionnes.")
    print(f"✅ Réponse reçue: {response.content}")
    
except Exception as e:
    print(f"❌ Erreur: {str(e)}")
    import traceback
    traceback.print_exc()