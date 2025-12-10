# app.py - Point d'entrée de l'application (Maintenant le "Contrôleur d'application")

import os
from flask import Flask
from config import SECRET_KEY, HOST, PORT, DATABASE_PATH
from model.database import initialize_database # Import ajusté
from controller.main_routes import main_bp
from controller.admin_routes import admin_bp
from controller.chatbot_routes import chatbot_bp

# ----------------------------------------------------
# 1. INITIALISATION DE LA BASE DE DONNÉES
# ----------------------------------------------------

if not os.path.exists(DATABASE_PATH):
    print("Base de données non trouvée. Initialisation en cours.")
    initialize_database()
else:
    print("Base de données trouvée. Démarrage de l'application.")

# ----------------------------------------------------
# 2. INITIALISATION DE L'APPLICATION FLASK
# ----------------------------------------------------

app = Flask(__name__)
app.secret_key = SECRET_KEY

# ----------------------------------------------------
# 3. ENREGISTREMENT DES BLUEPRINTS (CONTROLLERS)
# ----------------------------------------------------

app.register_blueprint(main_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(chatbot_bp) # Enregistrement des routes API du chatbot

# ----------------------------------------------------
# 4. DÉMARRAGE DE L'APPLICATION
# ----------------------------------------------------

if __name__ == '__main__':
    # Le 'debug=True' est important pour le rechargement
    app.run(debug=True, host=HOST, port=PORT)