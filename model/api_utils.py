# model/api_utils.py

import time
import functools
import requests
import json
from typing import Callable, Any, Optional, List, Dict, Union
from config import API_KEY, NASA_IMAGES_URL
from model.database import insert_solar_system_body

# Gemini Configuration - Correct URL for 2026
GEMINI_API_URL: str = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

def retry_with_backoff(func: Callable) -> Callable:
    """Decorator to retry a function call twice with a 2-second delay on failure."""
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
def call_hf_api(prompt: str, system_prompt: Optional[str] = None) -> str:
    """
    Calls the Google Gemini API to generate content.
    Returns a string containing the AI response or an error message.
    """
    
    # API Key validation
    if not API_KEY or API_KEY.startswith('your_') or len(API_KEY) < 30:
        return (
            "❌ Gemini API Key missing or invalid.\n\n"
            "To use the chatbot:\n"
            "1. Visit https://aistudio.google.com/app/apikey\n"
            "2. Create an API key (free, 2 clicks)\n"
            "3. Copy it into config.py (API_KEY line)\n"
            "4. Restart Flask"
        )
    
    print("🚀 Calling Gemini Pro API...")
    
    try:
        # Build the full prompt including instructions
        full_prompt: str = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        
        # Gemini API Payload
        payload: Dict[str, Any] = {
            "contents": [{
                "parts": [{"text": full_prompt}]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 1024,
            }
        }
        
        url: str = f"{GEMINI_API_URL}?key={API_KEY}"
        headers: Dict[str, str] = {"Content-Type": "application/json"}
        
        print("📤 Sending request...")
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        status: int = response.status_code
        
        print(f"📥 Response Status: {status}")
        
        # Error handling based on HTTP status codes
        if status == 429:
            return "⚠️ Quota temporarily exceeded. Please wait 1 minute."
        if status == 401:
            return "❌ Invalid API Key. Please check config.py."
        if status == 400:
            try:
                error_msg: str = response.json().get('error', {}).get('message', '')
                return f"❌ Request Error: {error_msg}"
            except Exception:
                return "❌ Request error. Please rephrase your question."
        
        if status != 200:
            return f"❌ API Error ({status}). Please try again."
        
        # Parse JSON response
        result: Dict[str, Any] = response.json()
        
        if 'candidates' in result and len(result['candidates']) > 0:
            candidate: Dict[str, Any] = result['candidates'][0]
            if 'content' in candidate:
                parts: List[Dict[str, str]] = candidate['content'].get('parts', [])
                if parts:
                    text: str = parts[0].get('text', '').strip()
                    if text:
                        print(f"✅ Response received ({len(text)} chars)")
                        return text
        
        return "❌ Empty response. Please rephrase your question."
        
    except requests.exceptions.Timeout:
        return "⏱️ Request timeout. Please try again."
    except Exception as e:
        print(f"❌ Error in call_hf_api: {e}")
        return f"❌ Error: {str(e)}"


@retry_with_backoff
def get_paged_nasa_search_data(search_term: str, page_number: int) -> Optional[List[Dict[str, Any]]]:
    """
    Fetches image metadata from the NASA Images API for a specific page.
    """
    url: str = f"{NASA_IMAGES_URL}?q={search_term}&media_type=image&page={page_number}&page_size=100"
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data: Dict[str, Any] = response.json()
        items: List[Dict[str, Any]] = data.get('collection', {}).get('items', [])
        
        if items:
            results: List[Dict[str, Any]] = []
            for item in items:
                metadata: Dict[str, Any] = item.get('data', [{}])[0]
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
    """
    Orchestrates data ingestion from NASA and insertion into the local database.
    Translates major celestial body names and handles duplicates.
    """
    total_success_count: int = 0
    translation_map: Dict[str, str] = {
        'Sun': 'Soleil', 'Mercury': 'Mercure', 'Venus': 'Vénus', 'Earth': 'Terre', 
        'Mars': 'Mars', 'Jupiter': 'Jupiter', 'Saturn': 'Saturne', 'Uranus': 'Uranus', 
        'Neptune': 'Neptune', 'Pluto': 'Pluton', 'Moon': 'Lune', 'Ceres': 'Cérès'
    }

    for page in range(1, max_pages + 1):
        data: Optional[List[Dict[str, Any]]] = get_paged_nasa_search_data(search_term, page)
        if not data:
            break
            
        for item in data:
            try:
                nasa_id: str = item.get('nasa_id', '')
                title: str = item.get('title', 'Unknown Object')
                description_text: str = item.get('description', "No description available.")
                keywords: List[str] = item.get('keywords', ['Celestial Object'])
                
                name_en: str = title
                name_fr: str = translation_map.get(title, title)
                body_type: str = keywords[0].capitalize() if keywords else 'Celestial Object'
                image_url: str = f"https://images-assets.nasa.gov/image/{nasa_id}/{nasa_id}~thumb.jpg"
                
                # Database insertion call
                result: bool = insert_solar_system_body(
                    name_fr=name_fr, 
                    name_en=name_en, 
                    description=description_text,
                    body_type=body_type, 
                    mass_value=None, 
                    density=None, 
                    image_url=image_url
                )
                
                if result:
                    total_success_count += 1
            except Exception as e:
                print(f"❌ Error ingesting item {item.get('nasa_id')}: {e}")
                continue
                
    return total_success_count