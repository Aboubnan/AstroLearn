# controller/main_routes.py - VERSION MODIFIÉE

import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from model.database import (
    get_all_celestial_objects,
    get_object_by_id,
    get_all_categories,
    search_celestial_objects,
    filter_celestial_objects
)

main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/', methods=['GET'])
def index():
    """Page d'accueil avec Hero Section."""
    return render_template('home.html',
                           now=datetime.datetime.now(),
                           title="Accueil - AstroLearn")


@main_bp.route('/catalogue', methods=['GET'])
def catalogue():
    """Page catalogue avec recherche et filtres."""
    
    search_term = request.args.get('search_term', '').strip()
    category_id_str = request.args.get('category_id', '').strip()
    
    objects = []
    
    # CAS 1 : Recherche + Filtre catégorie
    if search_term and category_id_str and category_id_str.isdigit():
        category_id = int(category_id_str)
        objects = filter_celestial_objects(category_id)
        search_lower = search_term.lower()
        objects = [
            obj for obj in objects 
            if search_lower in obj['nom_fr'].lower() 
            or (obj['nom_scientifique'] and search_lower in obj['nom_scientifique'].lower())
            or search_lower in obj['extrait_description'].lower()
        ]
    
    # CAS 2 : Seulement recherche
    elif search_term:
        objects = search_celestial_objects(search_term)
    
    # CAS 3 : Seulement filtre catégorie
    elif category_id_str and category_id_str.isdigit():
        category_id = int(category_id_str)
        objects = filter_celestial_objects(category_id)
    
    # CAS 4 : Tout afficher
    else:
        objects = get_all_celestial_objects()
    
    categories = get_all_categories()
    
    if (search_term or category_id_str) and not objects:
        flash("Aucun objet céleste ne correspond à vos critères.", 'warning')
    
    return render_template('catalogue.html',
                           objects=objects,
                           categories=categories,
                           now=datetime.datetime.now(),
                           title="Catalogue - AstroLearn")


@main_bp.route('/object/<int:object_id>')
def object_detail(object_id):
    """Page de détail d'un objet céleste."""
    obj = get_object_by_id(object_id)
    
    if obj is None:
        flash("Objet céleste non trouvé.", 'error')
        return redirect(url_for('main_bp.catalogue'))
    
    return render_template('detail.html',
                           obj=obj,
                           now=datetime.datetime.now(),
                           title=f"Détail : {obj['nom_fr']}")


@main_bp.route('/formulaire')
def formulaire():
    """Page formulaire de sondage."""
    EXTERNAL_FORM_URL = "https://tally.so/r/jaZGVR"
    return render_template('formulaire.html',
                           external_url=EXTERNAL_FORM_URL,
                           now=datetime.datetime.now(),
                           title="Sondage AstroLearn")