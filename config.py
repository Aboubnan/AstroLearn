# config.py - Configuration AstroLearn

import os

# ==================== BASE DE DONNÉES ====================
DATABASE_NAME = "astrolearn.db"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, DATABASE_NAME)

# ==================== FLASK ====================
SECRET_KEY = os.environ.get('SECRET_KEY', 'une_cle_secrete_tres_faible_pour_le_dev')
HOST = '127.0.0.1'
PORT = 5000

# ==================== API GEMINI ====================
# Clé API Gemini (configurée et prête à l'emploi)
API_KEY = "AIzaSyD0emeGIX-S9JkCYgQa3pOGbCSNF5NS5xQ"

# URL de l'API Gemini 2.5 Flash (le meilleur modèle disponible)
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

# Modèle utilisé (documentation)
CHATBOT_MODEL = "gemini-2.5-flash"

# ==================== API NASA ====================
NASA_IMAGES_URL = "https://images-api.nasa.gov/search"

# ==================== NOTES ====================
# Limites gratuites Gemini:
# - 60 requêtes par minute
# - 1500 requêtes par jour
# - Pas de carte bancaire requise