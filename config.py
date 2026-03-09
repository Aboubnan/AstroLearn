# config.py - AstroLearn Configuration

import os
from typing import List, Dict, Optional, Any

# ==================== DATABASE CONFIGURATION ====================
DATABASE_NAME: str = "astrolearn.db"
BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH: str = os.path.join(BASE_DIR, DATABASE_NAME)

# ==================== FLASK SERVER ====================
# Using environment variables for security in production
SECRET_KEY: str = os.environ.get('SECRET_KEY', 'dev_key_change_in_production')
HOST: str = '127.0.0.1'
PORT: int = 5000

# ==================== GEMINI AI API ====================
# Get API key from environment or fallback to the provided string
API_KEY: str = os.environ.get('GEMINI_API_KEY', "AIzaSyD0emeGIX-S9JkCYgQa3pOGbCSNF5NS5xQ")

# Gemini 2.5 Flash Endpoint (Latest stable model as of 2026)
GEMINI_API_URL: str = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
CHATBOT_MODEL: str = "gemini-2.5-flash"

# ==================== NASA API ====================
NASA_IMAGES_URL: str = "https://images-api.nasa.gov/search"

# ==================== USAGE NOTES ====================
# Gemini Free Tier Limits:
# - 60 requests per minute
# - 1500 requests per day
# - No credit card required for this tier