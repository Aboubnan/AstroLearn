# model/api_utils.py - VERSION GEMINI TESTÉE ET FONCTIONNELLE

import time
import functools
import requests
import json
from config import API_KEY, NASA_IMAGES_URL
from model.database import insert_solar_system_body

# Configuration Gemini - URL CORRECTE (testée janvier 2026)
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

# --- Décorateur retry ---
def retry_with_backoff(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        for attempt in range(2):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == 1:
                    raise e
                time.sleep(2)
        return None
    return wrapper

# --- Chatbot API ---
@retry_with_backoff
def call_hf_api(prompt, system_prompt=None):
    """
    Appelle Google Gemini API (gratuit avec clé).
    """
    
    # Vérifier la clé
    if not API_KEY or API_KEY.startswith('votre_') or len(API_KEY) < 30:
        return """❌ Clé API Gemini manquante ou invalide.

Pour utiliser le chatbot:
1. Allez sur https://aistudio.google.com/app/apikey
2. Créez une clé API (gratuit, 2 clics)
3. Copiez-la dans config.py (ligne API_KEY)
4. Relancez Flask

En attendant, explorez le catalogue et la carte 3D ! 🌟"""
    
    print(f"🚀 Appel Gemini Pro...")
    
    try:
        # Construire le prompt complet
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        else:
            full_prompt = prompt
        
        # Payload Gemini
        payload = {
            "contents": [{
                "parts": [{"text": full_prompt}]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 1024,
            }
        }
        
        # URL avec clé
        url = f"{GEMINI_API_URL}?key={API_KEY}"
        headers = {"Content-Type": "application/json"}
        
        print(f"📤 Envoi...")
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        status = response.status_code
        
        print(f"📥 Status: {status}")
        
        # Gestion des erreurs
        if status == 429:
            return "⚠️ Quota temporairement dépassé. Attendez 1 minute et réessayez."
        if status == 401:
            return "❌ Clé API invalide. Vérifiez votre clé dans config.py"
        if status == 400:
            try:
                err = response.json().get('error', {}).get('message', '')
                return f"❌ Erreur: {err}"
            except:
                return "❌ Erreur de requête. Reformulez votre question."
        
        if status != 200:
            return f"❌ Erreur API ({status}). Réessayez."
        
        # Parser réponse
        result = response.json()
        
        if 'candidates' in result and len(result['candidates']) > 0:
            candidate = result['candidates'][0]
            
            if 'content' in candidate:
                parts = candidate['content'].get('parts', [])
                if parts:
                    text = parts[0].get('text', '').strip()
                    if text:
                        print(f"✅ Réponse ({len(text)} car.)")
                        return text
        
        return "❌ Réponse vide. Reformulez votre question."
        
    except requests.exceptions.Timeout:
        return "⏱️ Timeout. Réessayez."
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return f"❌ Erreur: {str(e)}"

# --- NASA API (INCHANGÉ) ---
@retry_with_backoff
def get_paged_nasa_search_data(search_term, page_number):
    url = f"{NASA_IMAGES_URL}?q={search_term}&media_type=image&page={page_number}&page_size=100"
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        items = data.get('collection', {}).get('items')
        if items:
            results = []
            for item in items:
                metadata = item.get('data', [{}])[0]
                results.append({
                    "nasa_id": metadata.get('nasa_id', 'N/A'),
                    "title": metadata.get('title', 'Titre Inconnu'),
                    "description": metadata.get('description', 'Description non disponible'),
                    "keywords": metadata.get('keywords', []),
                })
            return results
        return None
    except:
        return None

def ingest_solar_system_data_paged(search_term, max_pages):
    total_success_count = 0
    translation_map = {
        'Sun': 'Soleil', 'Mercury': 'Mercure', 'Venus': 'Vénus', 'Earth': 'Terre', 
        'Mars': 'Mars', 'Jupiter': 'Jupiter', 'Saturn': 'Saturne', 'Uranus': 'Uranus', 
        'Neptune': 'Neptune', 'Pluto': 'Pluton', 'Moon': 'Lune', 'Ceres': 'Cérès'
    }
    for page in range(1, max_pages + 1):
        data = get_paged_nasa_search_data(search_term, page)
        if not data:
            break
        for item in data:
            try:
                nasa_id = item.get('nasa_id')
                title = item.get('title', 'Objet Inconnu')
                description_text = item.get('description', "Description non disponible.")
                keywords = item.get('keywords', ['Objet Céleste'])
                name_en = title
                name_fr = translation_map.get(title, title)
                body_type = keywords[0].capitalize() if keywords else 'Objet Céleste'
                image_url = f"https://images-assets.nasa.gov/image/{nasa_id}/{nasa_id}~thumb.jpg"
                result = insert_solar_system_body(
                    name_fr=name_fr, name_en=name_en, description=description_text,
                    body_type=body_type, mass_value=None, density=None, image_url=image_url
                )
                if result:
                    total_success_count += 1
            except:
                pass
    return total_success_count