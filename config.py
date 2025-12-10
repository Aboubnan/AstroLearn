# Fichier de configuration pour centraliser les chemins et constantes
import os
import os # Gardez cet import si vous utilisez os.environ.get

# Nom du fichier de la base de données SQLite
DATABASE_NAME = "astrolearn.db"

# Chemin absolu du dossier du projet
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Chemin complet vers le fichier de la base de données
DATABASE_PATH = os.path.join(BASE_DIR, DATABASE_NAME)

# Clé secrète pour Flask (à changer en production !)
SECRET_KEY = os.environ.get('SECRET_KEY', 'une_cle_secrete_tres_faible_pour_le_dev')

# Modèle d'IA utilisé pour le chatbot (à des fins de documentation)
CHATBOT_MODEL = "gemini-2.5-flash"

# Définir le port et l'hôte
HOST = '127.0.0.1'
PORT = 5000

# ---------------------------------------------
# CONSTANTES API (AJOUTÉES POUR LE CHATBOT ET L'INGESTION)
# ---------------------------------------------

# TOKEN HUGGING FACE
# REMPLACEZ 'hf_votre_vrai_token_ici' par votre jeton d'accès réel (commence par hf_)
API_KEY = "AIzaSyCO3vs27jdpF7BDB0GZoFznwehzcUeHXoA" 

# NOUVELLE URL GEMINI API (point d'accès standard)
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

# URL pour l'API NASA Image and Video Library
NASA_IMAGES_URL = "https://images-api.nasa.gov/search"