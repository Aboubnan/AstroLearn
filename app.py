# app.py - Application Entry Point

import os
from datetime import datetime, timedelta
from typing import Dict
from flask import Flask
from config import SECRET_KEY, HOST, PORT, DATABASE_URL
from model.database import initialize_database
from controller.main_routes import main_bp
from controller.admin_routes import admin_bp
from controller.chatbot_routes import chatbot_bp
from controller.skymap_routes import skymap_bp
from controller.user_bp import user_bp
from controller.auth_bp import auth_bp

# ----------------------------------------------------
# 1. DATABASE INITIALIZATION
# ----------------------------------------------------

initialize_database()

# ----------------------------------------------------
# 2. FLASK APPLICATION SETUP
# ----------------------------------------------------

app = Flask(__name__)
app.secret_key = SECRET_KEY

# CONFIGURATION DES SESSIONS (CRUCIAL POUR MOBILE)
app.config.update(
    SESSION_PERMANENT=True,
    PERMANENT_SESSION_LIFETIME=timedelta(days=7),
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True
)

@app.context_processor
def inject_current_year() -> Dict[str, int]:
    """Injecte l'année courante dans tous les templates."""
    return {'current_year': datetime.utcnow().year}

# ----------------------------------------------------
# 3. BLUEPRINT REGISTRATION (CONTROLLERS)
# ----------------------------------------------------

app.register_blueprint(main_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(chatbot_bp)
app.register_blueprint(skymap_bp)
app.register_blueprint(user_bp)
app.register_blueprint(auth_bp)

# ----------------------------------------------------
# 4. APPLICATION LAUNCH
# ----------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True, host=HOST, port=PORT)