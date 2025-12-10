# model/api_utils.py

import time
import functools
import requests
import json
# Importez maintenant la variable GEMINI_API_URL (si vous l'avez ajoutée)
from config import API_KEY, GEMINI_API_URL, NASA_IMAGES_URL 
from model.database import insert_solar_system_body # Pour l'ingestion

# --- Décorateur (laissez-le, il est utile) ---
def retry_with_backoff(func):
    # ... (le code du décorateur reste inchangé) ...
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        MAX_RETRIES = 5
        DELAY = 1
        for attempt in range(MAX_RETRIES):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == MAX_RETRIES - 1:
                    raise e
                print(f"Erreur API ({e}). Nouvelle tentative dans {DELAY}s...")
                time.sleep(DELAY)
                DELAY *= 2
        return None
    return wrapper

# --- Chatbot API (MIGRATION VERS GEMINI) ---
@retry_with_backoff
def call_hf_api(prompt, system_prompt=None):
    """Appelle l'API Gemini pour générer une réponse."""
    
    if not API_KEY or API_KEY.startswith('hf_'):
        print("Erreur: Token Gemini manquant ou invalide.")
        return "Erreur: Le Token Gemini est manquant ou invalide. Veuillez le configurer."
    
    # Structure du corps de la requête GEMINI
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.5,
            "maxOutputTokens": 2048,
        }
    }
    
    # Ajouter systemInstruction seulement si fourni
    if system_prompt:
        payload["systemInstruction"] = {
            "parts": [
                {"text": system_prompt}
            ]
        }
    
    # URL et Headers pour GEMINI
    url = f"{GEMINI_API_URL}?key={API_KEY}"
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print(f"--- Tentative d'appel à l'API GEMINI ---")
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        response.raise_for_status()

        api_result = response.json()
        
        # Extraction de la réponse GEMINI
        candidate = api_result.get('candidates', [{}])[0]
        ai_response_text = candidate.get('content', {}).get('parts', [{}])[0].get('text', 'Erreur de réponse Gemini.')
        
        # Vérification des filtres de sécurité
        if ai_response_text == 'Erreur de réponse Gemini.' or 'blocked' in ai_response_text.lower():
            return "Erreur: La réponse a été bloquée par le filtre de sécurité de l'IA."
        
        # Renvoyer le texte de la réponse
        return ai_response_text 

    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response is not None else 'N/A'
        error_text = f"Erreur de connexion (HTTP {status_code}). Veuillez vérifier votre clé Gemini et les limites d'utilisation."
    except Exception as e:
        error_text = f"Erreur inattendue : {e}"
        
    return error_text

# --- NASA API et Ingestion ---
@retry_with_backoff
def get_paged_nasa_search_data(search_term, page_number):
    """Appelle l'API NASA Image and Video Library pour obtenir les données d'une page de résultats."""
    # ... (Le reste du code NASA/Ingestion reste inchangé) ...
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
    except requests.exceptions.HTTPError as e:
        print(f"Erreur HTTP API NASA Images ({e.response.status_code if e.response is not None else 'N/A'}) pour la page {page_number}: {e}")
        return None
    except Exception as e:
        print(f"Erreur inattendue lors de l'appel API NASA Images: {e}")
        return None

def ingest_solar_system_data_paged(search_term, max_pages):
    """
    Récupère les données de la NASA via pagination et les insère dans la BDD.
    """
    total_success_count = 0
    
    translation_map = {
        'Sun': 'Soleil', 'Mercury': 'Mercure', 'Venus': 'Vénus', 'Earth': 'Terre', 
        'Mars': 'Mars', 'Jupiter': 'Jupiter', 'Saturn': 'Saturne', 'Uranus': 'Uranus', 
        'Neptune': 'Neptune', 'Pluto': 'Pluton', 'Moon': 'Lune', 'Ceres': 'Cérès', 
        'Eris': 'Éris', 'Titan': 'Titan', 'Io': 'Io', 'Europa': 'Europe', 
        'Ganymede': 'Ganymède', 'Callisto': 'Callisto', 'Enceladus': 'Encelade', 
        'Triton': 'Triton', 'Phobos': 'Phobos', 'Deimos': 'Deimos', 'Vesta': 'Vesta'
    }
    
    for page in range(1, max_pages + 1):
        data = get_paged_nasa_search_data(search_term, page)
        
        if not data:
            break
        
        success_count = 0
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
                    success_count += 1
            except Exception as e:
                print(f"Erreur lors du traitement de l'objet {title} (ID: {nasa_id}): {e}")
                
        total_success_count += success_count
        
    return total_success_count