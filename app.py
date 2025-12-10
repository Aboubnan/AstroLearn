# app.py - Le Contrôleur (C de MVC)
import os
import json
import time
import functools
import datetime
import requests

# REMPLACEMENT DES IMPORTS OPENAI : On utilise seulement 'requests' pour l'API Hugging Face
# from openai import OpenAI
# from openai import APIError # Plus nécessaire

# AJOUT : URL pour l'API NASA Image and Video Library
NASA_IMAGES_URL = "https://images-api.nasa.gov/search"

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify # <-- jsonify est importé !


# Importation du Modèle et de la Configuration
from database import (
    initialize_database,
    get_all_celestial_objects,
    get_object_by_id,
    get_all_categories,
    get_admin_by_pseudo,
    check_password,
    search_celestial_objects,
    filter_celestial_objects,
    insert_solar_system_body
)
# Assurez-vous d'avoir corrigé CHATBOT_MODEL à "gemini-2.5-flash" dans config.py
from config import SECRET_KEY, CHATBOT_MODEL, HOST, PORT, DATABASE_PATH

# ----------------------------------------------------
# 1. INITIALISATION DE L'APPLICATION
# ----------------------------------------------------

# Initialisation de la base de données au démarrage (si elle n'existe pas)
if not os.path.exists(DATABASE_PATH):
    print("Base de données non trouvée. Initialisation en cours.")
    initialize_database()
else:
    print("Base de données trouvée. Démarrage de l'application.")

app = Flask(__name__)
app.secret_key = SECRET_KEY

# ----------------------------------------------------
# 1.5. DÉCORATEURS DE SÉCURITÉ
# ----------------------------------------------------

def admin_required(view_func):
    """Décorateur pour exiger que l'utilisateur soit administrateur."""
    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):
        if not session.get('is_admin'):
            flash("Accès refusé. Veuillez vous connecter.", 'warning')
            return redirect(url_for('admin_login'))
        return view_func(*args, **kwargs)
    return wrapper

# ----------------------------------------------------
# 2. FONCTIONS UTILITAIRES API (F.03 : Chatbot & API Externes)
# ----------------------------------------------------

# REMPLACEZ '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' PAR VOTRE VRAI TOKEN D'ACCÈS HUGGING FACE
API_KEY = "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" 

# NOUVELLE CONSTANTE : Point de terminaison du modèle (Mistral 7B Instruct v0.2)
HUGGING_FACE_API_URL = "https://router.huggingface.co/models/HuggingFaceTB/SmolLM3-3B"

def retry_with_backoff(func):
    """Décorateur pour implémenter l'Exponential Backoff pour les appels API."""
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


@retry_with_backoff
def call_hf_api(prompt, system_prompt=None): # NOUVELLE FONCTION pour Hugging Face
    """Appelle l'API d'Inférence Hugging Face pour générer une réponse."""

    # Note : Le service gratuit de Hugging Face peut être lent ou avoir des limites de débit.
    
    # Validation basique du token
    if not API_KEY or not API_KEY.startswith('hf_'):
        print("Erreur: Token Hugging Face manquant ou invalide.")
        return {
            "candidates": [{
                "content": {"parts": [{"text": "Erreur: Le Token Hugging Face est manquant ou invalide. Veuillez le configurer dans app.py."}]},
                "groundingMetadata": {"groundingAttributions": []}
            }]
        }
    
    # 1. Construction du Prompt pour le modèle Instruct (Mistral)
    # On intègre le system_prompt dans le corps de l'instruction
    full_prompt = f"### System Instruction:\n{system_prompt}\n\n### User Question:\n{prompt}"
    
    payload = {
        "inputs": full_prompt,
        "parameters": {
            "max_new_tokens": 512,
            "temperature": 0.5,
            "do_sample": True
        }
    }
    
    # 2. Construction des Headers (authentification)
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        # 3. Appel de l'API via requêtes HTTP
        response = requests.post(HUGGING_FACE_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status() # Lève une exception pour les codes d'erreur HTTP (4xx ou 5xx)

        # 4. Extraction du texte
        api_result_list = response.json()
        
        if not api_result_list or 'generated_text' not in api_result_list[0]:
            # Vérifie également si le modèle est en cours de chargement (typique du service gratuit)
            if response.status_code == 503 and 'estimated_time' in api_result_list:
                 raise ValueError(f"Modèle en cours de chargement sur Hugging Face. Temps estimé: {api_result_list.get('estimated_time', 60)}s. Veuillez réessayer.")
            
            raise ValueError("Réponse de l'API Hugging Face inattendue ou vide.")
            
        generated_text_full = api_result_list[0]['generated_text']
        
        # Nettoyage : retirer l'instruction/prompt que nous avons envoyé au modèle.
        # Le modèle a tendance à répéter l'entrée avant de donner sa réponse.
        ai_response_text = generated_text_full.replace(full_prompt, "", 1).strip()
        
        # 5. Reformatage de la réponse pour correspondre à la structure de la route /chatbot
        formatted_response = {
            "candidates": [{
                "content": {"parts": [{"text": ai_response_text}]},
                # Les sources sont toujours vides avec cette implémentation gratuite.
                "groundingMetadata": {"groundingAttributions": []} 
            }]
        }
        
        return formatted_response

    except requests.exceptions.HTTPError as e:
        print(f"Erreur HTTP API Hugging Face: {e}")
        # Message d'erreur personnalisé en cas de problème de quota/débit sur HF
        error_text = f"Erreur de connexion (HTTP): {e.response.status_code}. Le service gratuit de Hugging Face peut être surchargé ou le Token incorrect."
        
    except ValueError as e:
        print(f"Erreur de réponse API Hugging Face: {e}")
        error_text = f"Erreur de réponse: {e}"
        
    except Exception as e:
        print(f"Erreur inattendue lors de l'appel à l'API Hugging Face: {e}")
        error_text = f"Erreur inattendue : {e}"
        
    # Retourne un objet de réponse d'erreur formaté
    return {
        "candidates": [{
            "content": {"parts": [{"text": error_text}]},
            "groundingMetadata": {"groundingAttributions": []}
        }]
    }

# --- FONCTION API PAGINÉE ---
@retry_with_backoff
def get_paged_nasa_search_data(search_term, page_number):
    """
    Appelle l'API NASA Image and Video Library pour obtenir les données d'une page de résultats.
    """
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
                
                # Collecte des métadonnées essentielles pour l'ingestion
                results.append({
                    "nasa_id": metadata.get('nasa_id', 'N/A'),
                    "title": metadata.get('title', 'Titre Inconnu'),
                    "description": metadata.get('description', 'Description non disponible'),
                    "keywords": metadata.get('keywords', []),
                })
            return results
        
        return None # Retourne None si la page est vide

    except requests.exceptions.HTTPError as e:
        print(f"Erreur HTTP API NASA Images ({response.status_code}) pour la page {page_number}: {e}")
        return None
    except Exception as e:
        print(f"Erreur inattendue lors de l'appel API NASA Images: {e}")
        return None

# --- FONCTION : Ingestion Paginée ---
def ingest_solar_system_data_paged(search_term, max_pages):
    """
    Récupère les données de la NASA via pagination pour un terme de recherche et les insère dans la BDD.
    """
    total_success_count = 0
    
    # Dictionnaire de traduction (Anglais -> Français) pour les noms les plus courants
    translation_map = {
        'Sun': 'Soleil', 'Mercury': 'Mercure', 'Venus': 'Vénus', 'Earth': 'Terre', 
        'Mars': 'Mars', 'Jupiter': 'Jupiter', 'Saturn': 'Saturne', 'Uranus': 'Uranus', 
        'Neptune': 'Neptune', 'Pluto': 'Pluton', 'Moon': 'Lune', 'Ceres': 'Cérès', 
        'Eris': 'Éris', 'Titan': 'Titan', 'Io': 'Io', 'Europa': 'Europe', 
        'Ganymede': 'Ganymède', 'Callisto': 'Callisto', 'Enceladus': 'Encelade', 
        'Triton': 'Triton', 'Phobos': 'Phobos', 'Deimos': 'Deimos', 'Vesta': 'Vesta'
    }
    
    for page in range(1, max_pages + 1):
        print(f"Tentative d'ingestion pour la recherche '{search_term}' - Page {page}...")
        
        # 1. Appel de l'API paginée
        data = get_paged_nasa_search_data(search_term, page)
        
        if not data:
            print(f"Aucun résultat trouvé pour la page {page} ou fin des résultats.")
            break # Arrête la boucle si l'API ne renvoie plus de données
        
        # 2. Traitement des résultats de la page
        success_count = 0
        
        for item in data:
            try:
                # Extraction & Transformation
                nasa_id = item.get('nasa_id')
                title = item.get('title', 'Objet Inconnu')
                description_text = item.get('description', "Description non disponible.")
                keywords = item.get('keywords', ['Objet Céleste'])
                
                # Deviner le nom FR et EN (on utilise le titre pour l'anglais)
                name_en = title
                name_fr = translation_map.get(title, title) # Traduit si connu, sinon garde le titre
                
                # Deviner le type à partir du premier mot-clé (méthode simple)
                body_type = keywords[0].capitalize() if keywords else 'Objet Céleste'
                
                # URL de l'image construite à partir de l'ID (méthode rapide)
                image_url = f"https://images-assets.nasa.gov/image/{nasa_id}/{nasa_id}~thumb.jpg"
                
                # 3. Insertion dans la BDD
                result = insert_solar_system_body(
                    name_fr=name_fr,
                    name_en=name_en,
                    description=description_text,
                    body_type=body_type,
                    mass_value=None,
                    density=None,
                    image_url=image_url
                )

                if result:
                    success_count += 1
                    print(f"   -> {name_fr} ({body_type}) inséré/mis à jour avec succès. ID: {nasa_id}")
                    
            except Exception as e:
                # Souvent des erreurs si l'item n'a pas un format attendu
                print(f"Erreur lors du traitement de l'objet {title} (ID: {nasa_id}): {e}")
                
        total_success_count += success_count
        print(f"   -> {success_count} objets insérés/mis à jour sur la page {page}.")
        
    return total_success_count


# ----------------------------------------------------
# 3. ROUTES DU CONTRÔLEUR
# ----------------------------------------------------

@app.route('/', methods=['GET']) # CHANGEMENT: Utiliser la méthode GET pour les filtres d'URL
def index():
    """Route de la page d'accueil, gérant l'affichage par défaut, la recherche ou le filtrage."""
    
    # 1. Récupération des paramètres de l'URL (méthode GET)
    search_term = request.args.get('search_term', '').strip()
    category_id_str = request.args.get('category_id', '').strip()
    
    objects = []
    
    # 2. Logique de Filtrage/Recherche
    
    # A. Recherche par mot-clé (prioritaire)
    if search_term:
        objects = search_celestial_objects(search_term)
        
    # B. Filtre par catégorie
    elif category_id_str and category_id_str.isdigit():
        category_id = int(category_id_str) # Conversion en entier
        objects = filter_celestial_objects(category_id)
        
    # C. Affichage par défaut (si aucun filtre/recherche n'est actif)
    else:
        objects = get_all_celestial_objects()
        
    # 3. Récupération des catégories (pour le sélecteur du template)
    categories = get_all_categories()
    
    # 4. Message si aucun résultat n'est trouvé après le filtrage
    if (search_term or category_id_str) and not objects:
        flash("Aucun objet céleste ne correspond à vos critères de recherche/filtre.", 'warning')

    
    return render_template('index.html',
                           objects=objects,
                           categories=categories,
                           # Note: L'index.html utilise directement request.args.get() pour conserver les valeurs des champs
                           now=datetime.datetime.now(),
                           title="Accueil - AstroLearn")


@app.route('/systeme_solaire/<string:body_name>')
def solar_system_detail(body_name):
    """Affiche les détails d'un corps céleste du Système Solaire (API Externe)."""

    flash(f"La fonction de détail en temps réel via API est désactivée. Veuillez utiliser la page de détail du catalogue.", 'info')
    return redirect(url_for('index'))


@app.route('/object/<int:object_id>')
def object_detail(object_id):
    """Route de la page de détail d'un objet céleste (F.02)."""
    obj = get_object_by_id(object_id)
    
    if obj is None:
        flash("Objet céleste non trouvé.", 'error')
        return redirect(url_for('index'))
    
    return render_template('detail.html',
                           obj=obj,
                           now=datetime.datetime.now(),
                           title=f"Détail : {obj['nom_fr']}")

# NOUVELLE ROUTE API POUR LE CHATBOT FLOTTANT (REMPLACE L'ANCIENNE ROUTE /chatbot)
@app.route('/api/chatbot', methods=['POST'])
def api_chatbot():
    """Point de terminaison API pour le chatbot (appelé par AJAX)."""
    
    # Assure que la requête contient des données JSON
    if not request.is_json:
        return jsonify({"error": "Missing JSON in request"}), 400

    data = request.get_json()
    user_message = data.get('message', '').strip()

    if not user_message:
        return jsonify({"error": "Message utilisateur manquant"}), 400
    
    # Le system_prompt est défini ici pour l'appel à l'IA
    system_prompt = "Act as an expert astrophysicist and provide a concise, factual answer about astronomy. Respond in French. Do not mention that you are an AI, a model or a bot."
    
    # Appel à la fonction Hugging Face
    api_result = call_hf_api(user_message, system_prompt)
    
    # Extraction des données
    try:
        candidate = api_result.get('candidates', [{}])[0]
        ai_response_text = candidate.get('content', {}).get('parts', [{}])[0].get('text', 'Erreur lors de la génération de la réponse par l\'IA.')
        
        # Retourne la réponse en JSON pour le JavaScript
        return jsonify({
            "response": ai_response_text
        })
        
    except Exception as e:
        print(f"Erreur d'extraction de réponse API: {e}")
        # Retourne une erreur formatée pour le front-end
        return jsonify({"error": "Une erreur inattendue s'est produite lors du traitement de l'IA."}), 500


@app.route('/formulaire')
def formulaire():
    """Route pour le formulaire (F.04)."""
    EXTERNAL_FORM_URL = "https://tally.so/r/jaZGVR"
    return render_template('formulaire.html',
                           external_url=EXTERNAL_FORM_URL,
                           now=datetime.datetime.now(),
                           title="Sondage AstroLearn")

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    """Route de connexion Admin (F.05)."""
    
    if request.method == 'POST':
        pseudo = request.form.get('pseudo')
        password = request.form.get('password')
        
        admin = get_admin_by_pseudo(pseudo)
        
        if admin:
            # Vérification du mot de passe haché
            if check_password(admin['mot_de_passe_hash'], password):
                session['is_admin'] = True
                session['admin_id'] = admin['id_admin']
                flash("Connexion Administrateur réussie.", 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash("Identifiant ou mot de passe incorrect.", 'error')
        else:
            flash("Identifiant ou mot de passe incorrect.", 'error')
            
    return render_template('login.html',
                           now=datetime.datetime.now(),
                           title="Connexion Administrateur")

@app.route('/admin_dashboard')
@admin_required # Protection de la route
def admin_dashboard():
    """Tableau de bord Admin (Route protégée)."""
    return render_template('admin_dashboard.html',
                           now=datetime.datetime.now(),
                           title="Tableau de Bord Admin")

# --- Route d'ingestion utilisant la pagination ---
@app.route('/admin/ingest_solar_system', methods=['POST'])
@admin_required # Protection de la route
def ingest_data():
    """Route Admin pour déclencher l'ingestion des données paginées du Système Solaire."""

    # Paramètres pour la recherche large et la pagination
    search_term = 'solar system' # Recherche générique pour obtenir plus de résultats
    max_pages = 5 # Limite à 5 pages (5 x 100 objets = 500 objets max)

    count = ingest_solar_system_data_paged(search_term, max_pages)

    if count > 0:
        flash(f"{count} objets trouvés via la recherche '{search_term}' (jusqu'à {max_pages} pages) ont été insérés/mis à jour.", 'success')
    else:
        flash("Échec de l'ingestion des données du Système Solaire (vérifiez les logs et l'API).", 'error')

    return redirect(url_for('admin_dashboard'))

@app.route('/admin_logout')
def admin_logout():
    """Déconnexion Admin."""
    session.pop('is_admin', None)
    session.pop('admin_id', None)
    flash("Vous êtes déconnecté.", 'info')
    return redirect(url_for('index'))

# ----------------------------------------------------
# 4. DÉMARRAGE DE L'APPLICATION
# ----------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True, host=HOST, port=PORT)