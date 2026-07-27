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
SECRET_KEY: Optional[str] = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY manquante : définis-la dans le fichier .env. "
        "Aucune valeur de secours n'est utilisée pour éviter de signer "
        "les sessions avec une clé publique connue."
    )

HOST: str = '127.0.0.1'
PORT: int = 5000

# ==================== BOOTSTRAP ADMIN (optionnel) ====================
# Compte admin créé au premier démarrage si ces variables sont définies
# dans le .env. Si elles sont absentes, aucun admin n'est créé
# automatiquement (évite un couple identifiant/mot de passe connu dans
# le code source).
ADMIN_PSEUDO: Optional[str] = os.environ.get('ADMIN_PSEUDO')
ADMIN_PASSWORD: Optional[str] = os.environ.get('ADMIN_PASSWORD')
ADMIN_EMAIL: Optional[str] = os.environ.get('ADMIN_EMAIL')
ADMIN_NOM: str = os.environ.get('ADMIN_NOM', 'Admin')
ADMIN_PRENOM: str = os.environ.get('ADMIN_PRENOM', 'Super')

# ==================== API CONFIGURATION ====================
# Ici, on ne met PLUS JAMAIS la clé en texte brut. 
# Si os.environ.get ne trouve rien, l'app ne pourra pas appeler l'API, ce qui est normal.
API_KEY: Optional[str] = os.environ.get('GEMINI_API_KEY')

GEMINI_API_URL: str = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
NASA_IMAGES_URL: str = "https://images-api.nasa.gov/search"