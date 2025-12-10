# app.py - Point d'entrée de l'application (Maintenant le "Contrôleur d'application")

import os
from flask import Flask, render_template, request, jsonify
from config import SECRET_KEY, HOST, PORT, DATABASE_PATH
from model.database import initialize_database # Import ajusté
from controller.main_routes import main_bp
from controller.admin_routes import admin_bp
from controller.chatbot_routes import chatbot_bp
from controller.skymap_routes import skymap_bp
from datetime import datetime # NOUVEL IMPORT

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

# ----------------------------------------
    # NOUVEAU : CONTEXTE TEMPLATE POUR L'ANNÉE ACTUELLE
# ----------------------------------------

@app.context_processor
def inject_current_year():
    # Cette fonction est appelée avant chaque rendu de template
    return {'current_year': datetime.utcnow().year} # Renvoie l'année UTC

# ----------------------------------------------------
# 3. ENREGISTREMENT DES BLUEPRINTS (CONTROLLERS)
# ----------------------------------------------------

app.register_blueprint(main_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(chatbot_bp) # Enregistrement des routes API du chatbot
app.register_blueprint(skymap_bp)


# ----------------------------------------------------
# 4. DÉMARRAGE DE L'APPLICATION
# ----------------------------------------------------

if __name__ == '__main__':
    # Le 'debug=True' est important pour le rechargement
    app.run(debug=True, host=HOST, port=PORT)