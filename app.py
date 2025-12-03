# app.py - Le Contrôleur (C de MVC)
import os
import json 
import time 
import functools 
import datetime 
import requests 

# AJOUT : URL pour l'API du Système Solaire
SOLAR_SYSTEM_URL = "https://api.le-systeme-solaire.net/rest/bodies/" 

from flask import Flask, render_template, request, redirect, url_for, flash, session

# Importation du Modèle et de la Configuration
from database import (
    initialize_database, 
    get_all_celestial_objects, 
    get_object_by_id, 
    get_all_categories, 
    get_admin_by_pseudo, 
    check_password 
)
from config import SECRET_KEY, CHATBOT_MODEL, HOST, PORT, DATABASE_PATH

# ----------------------------------------------------
# 1. INITIALISATION DE L'APPLICATION
# ----------------------------------------------------

# Initialisation de la base de données au démarrage (si elle n'existe pas)
if not os.path.exists(DATABASE_PATH):
    print("Base de données non trouvée. Initialisation en cours...")
    initialize_database()
else:
    print("Base de données trouvée. Démarrage de l'application.")

app = Flask(__name__)
# Utilisation de la clé secrète importée depuis config.py pour les sessions/messages flash
app.secret_key = SECRET_KEY

# ----------------------------------------------------
# 2. FONCTIONS UTILITAIRES API (F.03 : Chatbot & API Externes)
# ----------------------------------------------------

API_KEY = "" # Clé pour Gemini (si utilisée)

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
def call_gemini_api(prompt, system_prompt=None): 
    """Appelle l'API Gemini pour générer une réponse (simulée ici)."""
    
    print(f"DEBUG: Appel API simulé pour le prompt: {prompt}")
    
    # Simuler une réponse standard
    simulated_response = {
        "candidates": [{
            "content": {"parts": [{"text": "Je suis AstroIA, votre guide expert en astrophysique. Je peux répondre à vos questions sur les galaxies, les nébuleuses, et l'exploration spatiale. (Ceci est une réponse simulée en mode développement)."}]},
            "groundingMetadata": {"groundingAttributions": []}
        }]
    }
    
    return simulated_response

@retry_with_backoff 
def get_solar_system_body(body_id): 
    """Appelle l'API du Système Solaire pour un corps spécifique (ex: 'mars')."""
    
    url = SOLAR_SYSTEM_URL + body_id.lower()
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status() 
        
        return response.json()
        
    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            print(f"Corps céleste {body_id} non trouvé dans l'API du Système Solaire (404).")
            return None
        raise e 
    except Exception as e:
        print(f"Erreur inattendue lors de l'appel Solar System API: {e}")
        return None

# ----------------------------------------------------
# 3. ROUTES DU CONTRÔLEUR (F.01, F.02, F.03, F.04, F.05 et Nouvelles Routes)
# ----------------------------------------------------

@app.route('/', methods=['GET', 'POST']) 
def index(): 
    """Route de la page d'accueil, affichant le catalogue local par défaut."""
    
    # L'affichage par défaut revient à charger le catalogue local (les 10 derniers)
    objects = get_all_celestial_objects()
    categories = get_all_categories()
    
    # On vide les variables de l'ancienne API
    apod_list = []
    current_filter_date = ''
    
    # Rendu du template
    return render_template('index.html', 
                           apod_list=apod_list, # Sera toujours vide
                           objects=objects,     # Catalogue local
                           categories=categories, # Catégories
                           current_filter_date=current_filter_date,
                           now=datetime.datetime.now(), 
                           title="Accueil - AstroLearn")


@app.route('/systeme_solaire/<string:body_name>')
def solar_system_detail(body_name):
    """Affiche les détails d'un corps céleste du Système Solaire (API Externe)."""
    
    data = get_solar_system_body(body_name)
    
    if data:
        # Tente de capitaliser le nom en anglais, sinon utilise le nom français
        body_title = data.get('englishName', data.get('name', body_name)).capitalize()
        
        return render_template('solar_detail.html', 
                               body=data,
                               now=datetime.datetime.now(), 
                               title=f"Détail : {body_title}")
    else:
        flash(f"Corps céleste '{body_name}' non trouvé dans l'API du Système Solaire.", 'error')
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

@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot(): 
    """Route de la page Chatbot (F.03)."""
    user_message = ""
    ai_response_text = ""
    sources = []
    
    if request.method == 'POST':
        user_message = request.form.get('message', '')
        if user_message:
            system_prompt = "Act as an expert astrophysicist and provide a concise, factual answer about astronomy. Respond in French."
            
            api_result = call_gemini_api(user_message, system_prompt) 
            
            # Extraction des données
            try:
                candidate = api_result.get('candidates', [{}])[0]
                ai_response_text = candidate.get('content', {}).get('parts', [{}])[0].get('text', 'Erreur lors de la génération de la réponse.')
                
                # Extraction des sources (Grounding)
                grounding_metadata = candidate.get('groundingMetadata', {})
                if grounding_metadata and grounding_metadata.get('groundingAttributions'):
                    sources = [
                        {
                            'uri': attr.get('web', {}).get('uri'),
                            'title': attr.get('web', {}).get('title'),
                        }
                        for attr in grounding_metadata['groundingAttributions']
                        if attr.get('web', {}).get('uri') and attr.get('web', {}).get('title')
                    ]

            except Exception as e:
                ai_response_text = f"Une erreur s'est produite lors du traitement de l'API. ({e})"
                print(f"Erreur d'extraction de réponse API: {e}")

    # Appel à la Vue
    return render_template('chatbot.html', 
                           user_message=user_message, 
                           ai_response_text=ai_response_text, 
                           sources=sources,
                           now=datetime.datetime.now(), 
                           title="Chatbot AstroIA")

@app.route('/formulaire')
def formulaire():
    """Route pour le formulaire (F.04)."""
    EXTERNAL_FORM_URL = "https://tally.so/r/EXEMPLE-DE-FORMULAIRE-AVIS"
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
def admin_dashboard():
    """Tableau de bord Admin (Route protégée)."""
    if not session.get('is_admin'):
        flash("Accès refusé. Veuillez vous connecter.", 'warning')
        return redirect(url_for('admin_login'))

    return render_template('admin_dashboard.html', 
                           now=datetime.datetime.now(), 
                           title="Tableau de Bord Admin")

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