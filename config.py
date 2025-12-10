# Fichier de configuration pour centraliser les chemins et constantes
import os

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