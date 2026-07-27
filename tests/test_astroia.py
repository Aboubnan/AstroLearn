# test_astroia.py
import os
from dotenv import load_dotenv
from model.api_utils import call_gemini_api

load_dotenv()


def test_connexion():
    api_key = os.getenv("GEMINI_API_KEY")
    assert api_key, "Clé API Gemini manquante dans le .env"

    prompt = "Peux-tu m'expliquer ce qu'est une naine blanche en une phrase ?"
    system_instr = "Tu es AstroIA, expert en astronomie. Réponds brièvement en français."

    reponse = call_gemini_api(user_input=prompt, system_instruction=system_instr)

    assert reponse, "Aucune réponse reçue de l'API Gemini."


if __name__ == "__main__":
    test_connexion()
