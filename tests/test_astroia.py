# test_astroia.py
from model.api_utils import call_gemini_api
from dotenv import load_dotenv
import os

# 1. Charger les variables d'environnement
load_dotenv()

def test_connexion():
    print("🔍 Vérification de la configuration...")
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ ERREUR : Clé API non trouvée dans le .env")
        return

    print(f"✅ Clé API détectée (commence par : {api_key[:5]}...)")
    
    # 2. Test d'appel à l'IA
    prompt = "Peux-tu m'expliquer ce qu'est une naine blanche en une phrase ?"
    system_instr = "Tu es AstroIA, expert en astronomie. Réponds brièvement en français."
    
    print(f"\n📡 Envoi du message à Gemini : '{prompt}'")
    
    reponse = call_gemini_api(user_input=prompt, system_instruction=system_instr)
    
    if reponse:
        print(f"\n✨ Réponse d'AstroIA :\n{reponse}")
        print("\n✅ TEST RÉUSSI : La connexion entre Python, le .env et Gemini est opérationnelle.")
    else:
        print("\n❌ TEST ÉCHOUÉ : Aucune réponse reçue de l'API.")

if __name__ == "__main__":
    test_connexion()