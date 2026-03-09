# app.py - Application Entry Point

import os
from datetime import datetime
from typing import Dict
from flask import Flask
from config import SECRET_KEY, HOST, PORT, DATABASE_URL
from model.database import initialize_database
from controller.main_routes import main_bp
from controller.admin_routes import admin_bp
from controller.chatbot_routes import chatbot_bp
from controller.skymap_routes import skymap_bp

# ----------------------------------------------------
# 1. DATABASE INITIALIZATION
# ----------------------------------------------------

initialize_database()

# ----------------------------------------------------
# 2. FLASK APPLICATION SETUP
# ----------------------------------------------------

app = Flask(__name__)
app.secret_key = SECRET_KEY

@app.context_processor
def inject_current_year() -> Dict[str, int]:
    """
    Injects the current year into all templates globally.
    Allows using {{ current_year }} in any HTML file.
    """
    return {'current_year': datetime.utcnow().year}

# ----------------------------------------------------
# 3. BLUEPRINT REGISTRATION (CONTROLLERS)
# ----------------------------------------------------

# Modular routing for better maintainability
app.register_blueprint(main_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(chatbot_bp)
app.register_blueprint(skymap_bp)

# ----------------------------------------------------
# 4. APPLICATION LAUNCH
# ----------------------------------------------------

if __name__ == '__main__':
    # Debug mode is enabled for development (hot-reloading)
    app.run(debug=True, host=HOST, port=PORT)