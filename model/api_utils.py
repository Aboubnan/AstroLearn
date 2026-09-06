# model/api_utils.py

import time
import functools
import requests
from typing import Callable, Any, Optional, List, Dict
from config import API_KEY, MISTRAL_API_URL, MISTRAL_MODEL, NASA_IMAGES_URL
from model.database import insert_solar_system_body


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
def call_mistral_api(
    user_input: str,
    system_instruction: Optional[str] = None,
    history: Optional[List[Dict[str, str]]] = None,
) -> Optional[str]:
    """
    Appelle l'API Mistral (ministral-8b-2512) avec support de l'historique et des
    instructions système.

    Remplace Gemini le 31/08/2026 : la clé Gemini fonctionne très bien depuis un poste
    résidentiel mais échoue systématiquement depuis ce VPS OVH ("User location is not
    supported for the API use") — confirmé au niveau de l'IP du serveur (même clé, même
    modèle, testé en direct), pas de la clé ni du modèle. Mistral n'a pas cette
    restriction, testé et fonctionnel depuis ce même serveur.

    Modèle changé le 06/09/2026 : `mistral-small-latest` (et sa version datée
    `mistral-small-2603`) a un quota de requêtes à 0/minute sur le niveau gratuit tant
    que le Pay-As-You-Go n'est pas activé (carte bancaire requise). La famille
    `ministral` (modèles plus légers, open-weight) est en revanche incluse gratuitement
    sans activation : `ministral-8b-2512` offre un vrai quota (188 req/min mesuré) sans
    carte bancaire, largement suffisant pour ce chatbot.
    """
    if not API_KEY:
        return "❌ Erreur : Clé API manquante dans le fichier .env"

    history = history or []

    # Format Mistral : liste de messages {role, content} façon OpenAI. Le rôle
    # "assistant" est déjà celui utilisé côté historique (pas de renommage "model"
    # comme il fallait le faire avec Gemini).
    messages: List[Dict[str, str]] = []
    if system_instruction:
        messages.append({"role": "system", "content": system_instruction})
    for msg in history:
        role = "user" if msg["role"] == "user" else "assistant"
        messages.append({"role": role, "content": msg["content"]})
    messages.append({"role": "user", "content": user_input})

    payload: Dict[str, Any] = {
        "model": MISTRAL_MODEL,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 800,
    }

    headers: Dict[str, str] = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }

    try:
        print(f"🚀 AstroIA : Envoi de la requête (Historique: {len(history)} messages)")
        response = requests.post(MISTRAL_API_URL, headers=headers, json=payload, timeout=30)

        if response.status_code == 429:
            return "⚠️ Quota dépassé. Attends une minute."

        response.raise_for_status()
        result = response.json()

        choices = result.get("choices", [])
        if choices:
            content_text = choices[0].get("message", {}).get("content", "")
            if content_text:
                return content_text.strip()

        return "❌ L'IA a renvoyé une réponse vide."

    except Exception as e:
        print(f"❌ Erreur Mistral API : {e}")
        return None


# --- NASA API FUNCTIONS ---
# (Gardées identiques car elles ne dépendent pas de la migration PostgreSQL)


@retry_with_backoff
def get_paged_nasa_search_data(
    search_term: str, page_number: int
) -> Optional[List[Dict[str, Any]]]:
    """Récupère les métadonnées d'images depuis l'API NASA."""
    url: str = (
        f"{NASA_IMAGES_URL}?q={search_term}&media_type=image&page={page_number}&page_size=100"
    )
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        items = data.get("collection", {}).get("items", [])

        if items:
            results = []
            for item in items:
                metadata = item.get("data", [{}])[0]
                results.append(
                    {
                        "nasa_id": metadata.get("nasa_id", "N/A"),
                        "title": metadata.get("title", "Unknown Title"),
                        "description": metadata.get(
                            "description", "No description available"
                        ),
                        "keywords": metadata.get("keywords", []),
                    }
                )
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
        if not data:
            break

        for item in data:
            try:
                nasa_id = item.get("nasa_id", "")
                title = item.get("title", "Unknown")
                desc = item.get("description", "").lower()
                image_url = f"https://images-assets.nasa.gov/image/{nasa_id}/{nasa_id}~thumb.jpg"

                # --- LOGIQUE DE DÉTECTION DE TYPE ---
                # On analyse le titre et la description pour trouver la catégorie
                detected_type = "Object"  # Par défaut

                if any(
                    word in desc or word in title.lower()
                    for word in ["planet", "planète"]
                ):
                    detected_type = "Planet"
                elif any(
                    word in desc or word in title.lower()
                    for word in ["moon", "lune", "satellite"]
                ):
                    detected_type = "Moon"
                elif any(
                    word in desc or word in title.lower()
                    for word in ["star", "étoile", "sun", "soleil"]
                ):
                    detected_type = "Star"
                elif any(
                    word in desc or word in title.lower()
                    for word in ["galaxy", "galaxie"]
                ):
                    detected_type = "Galaxie"
                elif any(
                    word in desc or word in title.lower()
                    for word in ["nebula", "nébuleuse"]
                ):
                    detected_type = "Nebula"
                elif any(
                    word in desc or word in title.lower()
                    for word in ["asteroid", "astéroïde", "comet", "comète"]
                ):
                    detected_type = "Asteroid"

                # Appel de la fonction insert avec le type détecté
                result = insert_solar_system_body(
                    name_fr=title,  # On garde le titre original
                    name_en=title,
                    description=item.get("description", ""),
                    body_type=detected_type,  # <--- ICI on envoie le type détecté !
                    mass_value=None,
                    density=None,
                    image_url=image_url,
                )

                if result:
                    total_success_count += 1
            except Exception as e:
                print(f"❌ Erreur lors de l'ingestion de {title}: {e}")
                continue

    return total_success_count
