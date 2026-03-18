# config.py - AstroLearn Configuration (Secured)

import os
from dotenv import load_dotenv
from typing import Optional

# Charge les variables du fichier .env
load_dotenv()

# ==================== POSTGRESQL CONFIGURATION ====================
DB_USER: str = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD: str = os.environ.get('DB_PASSWORD', '') # Lu depuis le .env
DB_HOST: str = os.environ.get('DB_HOST', 'localhost')
DB_PORT: str = os.environ.get('DB_PORT', '5432')
DB_NAME: str = os.environ.get('DB_NAME', 'astrolearn_db')

DATABASE_URL: str = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# ==================== FLASK SERVER ====================
SECRET_KEY: str = os.environ.get('SECRET_KEY', 'default_fallback_key')
HOST: str = '127.0.0.1'
PORT: int = 5000

# ==================== API CONFIGURATION ====================
# Ici, on ne met PLUS JAMAIS la clé en texte brut. 
# Si os.environ.get ne trouve rien, l'app ne pourra pas appeler l'API, ce qui est normal.
API_KEY: Optional[str] = os.environ.get('GEMINI_API_KEY')

GEMINI_API_URL: str = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
NASA_IMAGES_URL: str = "https://images-api.nasa.gov/search"