# model/api_utils.py

import time
import functools
import requests
import json
from typing import Callable, Any, Optional, List, Dict, Union
from config import API_KEY, NASA_IMAGES_URL
from model.database import insert_solar_system_body

# Gemini Configuration - 2026 Stable Endpoint
GEMINI_API_URL: str = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

def retry_with_backoff(func: Callable) -> Callable:
    """Décorateur pour retenter l'appel API en cas d'échec (2 tentatives, délai 2s)."""
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        for attempt in range(2):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == 1:
                    raise e
                time.sleep(2)
        return None
    return wrapper

@retry_with_backoff
def call_gemini_api(user_input: str, system_instruction: Optional[str] = None, history: List[Dict[str, str]] = []) -> Optional[str]:
    """
    Appelle l'API Gemini 2.5 Flash avec support de l'historique et des instructions système.
    """
    if not API_KEY:
        return "❌ Erreur : Clé API manquante dans le fichier .env"

    # 1. Préparation de l'historique au format Gemini (user -> user, assistant -> model)
    contents = []
    for msg in history:
        role = "user" if msg['role'] == "user" else "model"
        contents.append({
            "role": role,
            "parts": [{"text": msg['content']}]
        })

    # Ajouter le message actuel de l'utilisateur
    contents.append({
        "role": "user",
        "parts": [{"text": user_input}]
    })

    # 2. Construction du Payload
    payload: Dict[str, Any] = {
        "contents": contents,
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 800,
        }
    }

    # Ajout des instructions système si présentes
    if system_instruction:
        payload["system_instruction"] = {
            "parts": [{"text": system_instruction}]
        }

    url: str = f"{GEMINI_API_URL}?key={API_KEY}"
    headers: Dict[str, str] = {"Content-Type": "application/json"}

    try:
        print(f"🚀 AstroIA : Envoi de la requête (Historique: {len(history)} messages)")
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 429:
            return "⚠️ Quota dépassé. Attends une minute."
        
        response.raise_for_status()
        result = response.json()

        # Extraction de la réponse
        if 'candidates' in result and result['candidates']:
            parts = result['candidates'][0].get('content', {}).get('parts', [])
            if parts:
                return parts[0].get('text', '').strip()

        return "❌ L'IA a renvoyé une réponse vide."

    except Exception as e:
        print(f"❌ Erreur Gemini API : {e}")
        return None

# --- NASA API FUNCTIONS ---
# (Gardées identiques car elles ne dépendent pas de la migration PostgreSQL)

@retry_with_backoff
def get_paged_nasa_search_data(search_term: str, page_number: int) -> Optional[List[Dict[str, Any]]]:
    """Récupère les métadonnées d'images depuis l'API NASA."""
    url: str = f"{NASA_IMAGES_URL}?q={search_term}&media_type=image&page={page_number}&page_size=100"
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        items = data.get('collection', {}).get('items', [])
        
        if items:
            results = []
            for item in items:
                metadata = item.get('data', [{}])[0]
                results.append({
                    "nasa_id": metadata.get('nasa_id', 'N/A'),
                    "title": metadata.get('title', 'Unknown Title'),
                    "description": metadata.get('description', 'No description available'),
                    "keywords": metadata.get('keywords', []),
                })
            return results
        return None
    except Exception as e:
        print(f"❌ NASA API Error: {e}")
        return None

def ingest_solar_system_data_paged(search_term: str, max_pages: int) -> int:
    """Orchestre l'ingestion de données NASA vers PostgreSQL avec détection de type."""
    total_success_count: int = 0
    
    for page in range(1, max_pages + 1):
        data = get_paged_nasa_search_data(search_term, page)
        if not data: break
            
        for item in data:
            try:
                nasa_id = item.get('nasa_id', '')
                title = item.get('title', 'Unknown')
                desc = item.get('description', '').lower()
                image_url = f"https://images-assets.nasa.gov/image/{nasa_id}/{nasa_id}~thumb.jpg"
                
                # --- LOGIQUE DE DÉTECTION DE TYPE ---
                # On analyse le titre et la description pour trouver la catégorie
                detected_type = 'Object' # Par défaut
                
                if any(word in desc or word in title.lower() for word in ['planet', 'planète']):
                    detected_type = 'Planet'
                elif any(word in desc or word in title.lower() for word in ['moon', 'lune', 'satellite']):
                    detected_type = 'Moon'
                elif any(word in desc or word in title.lower() for word in ['star', 'étoile', 'sun', 'soleil']):
                    detected_type = 'Star'
                elif any(word in desc or word in title.lower() for word in ['galaxy', 'galaxie']):
                    detected_type = 'Galaxie'
                elif any(word in desc or word in title.lower() for word in ['nebula', 'nébuleuse']):
                    detected_type = 'Nebula'
                elif any(word in desc or word in title.lower() for word in ['asteroid', 'astéroïde', 'comet', 'comète']):
                    detected_type = 'Asteroid'

                # Appel de la fonction insert avec le type détecté
                result = insert_solar_system_body(
                    name_fr=title, # On garde le titre original
                    name_en=title, 
                    description=item.get('description', ''),
                    body_type=detected_type, # <--- ICI on envoie le type détecté !
                    mass_value=None, 
                    density=None, 
                    image_url=image_url
                )
                
                if result: 
                    total_success_count += 1
            except Exception as e:
                print(f"❌ Erreur lors de l'ingestion de {title}: {e}")
                continue
                
    return total_success_count
    """Orchestre l'ingestion de données NASA vers PostgreSQL."""
    total_success_count: int = 0
    translation_map = {'Sun': 'Soleil', 'Earth': 'Terre', 'Moon': 'Lune'} # Simplifié pour l'exemple

    for page in range(1, max_pages + 1):
        data = get_paged_nasa_search_data(search_term, page)
        if not data: break
            
        for item in data:
            try:
                nasa_id = item.get('nasa_id', '')
                title = item.get('title', 'Unknown')
                image_url = f"https://images-assets.nasa.gov/image/{nasa_id}/{nasa_id}~thumb.jpg"
                
                # Note: insert_solar_system_body utilise maintenant PostgreSQL via ton model/database.py
                result = insert_solar_system_body(
                    name_fr=translation_map.get(title, title), 
                    name_en=title, 
                    description=item.get('description', ''),
                    body_type='Object', 
                    mass_value=None, density=None, image_url=image_url
                )
                if result: total_success_count += 1
            except Exception: continue
                
    return total_success_count