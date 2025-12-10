# controller/main_routes.py

import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from model.database import (
    get_all_celestial_objects,
    get_object_by_id,
    get_all_categories,
    search_celestial_objects,
    filter_celestial_objects
)

# Création du Blueprint
main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/', methods=['GET'])
def index():
    """Route de la page d'accueil, gérant l'affichage par défaut, la recherche ou le filtrage."""
    
    search_term = request.args.get('search_term', '').strip()
    category_id_str = request.args.get('category_id', '').strip()
    
    objects = []
    
    if search_term:
        objects = search_celestial_objects(search_term)
    elif category_id_str and category_id_str.isdigit():
        category_id = int(category_id_str)
        objects = filter_celestial_objects(category_id)
    else:
        objects = get_all_celestial_objects()
        
    categories = get_all_categories()
    
    if (search_term or category_id_str) and not objects:
        flash("Aucun objet céleste ne correspond à vos critères de recherche/filtre.", 'warning')

    
    return render_template('index.html',
                           objects=objects,
                           categories=categories,
                           now=datetime.datetime.now(),
                           title="Accueil - AstroLearn")


@main_bp.route('/systeme_solaire/<string:body_name>')
def solar_system_detail(body_name):
    """Affiche les détails d'un corps céleste du Système Solaire (API Externe)."""
    flash(f"La fonction de détail en temps réel via API est désactivée. Veuillez utiliser la page de détail du catalogue.", 'info')
    return redirect(url_for('main_bp.index'))


@main_bp.route('/object/<int:object_id>')
def object_detail(object_id):
    """Route de la page de détail d'un objet céleste (F.02)."""
    obj = get_object_by_id(object_id)
    
    if obj is None:
        flash("Objet céleste non trouvé.", 'error')
        return redirect(url_for('main_bp.index'))
    
    return render_template('detail.html',
                           obj=obj,
                           now=datetime.datetime.now(),
                           title=f"Détail : {obj['nom_fr']}")

@main_bp.route('/formulaire')
def formulaire():
    """Route pour le formulaire (F.04)."""
    EXTERNAL_FORM_URL = "https://tally.so/r/jaZGVR"
    return render_template('formulaire.html',
                           external_url=EXTERNAL_FORM_URL,
                           now=datetime.datetime.now(),
                           title="Sondage AstroLearn")