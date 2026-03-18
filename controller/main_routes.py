# controller/main_routes.py

import datetime
from typing import List, Dict, Any, Optional, Union
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response, session

from model.database import (
    get_all_celestial_objects,
    get_object_by_id,
    get_all_categories,
    search_celestial_objects,
    get_objects_by_category,
    get_favoris_ids_utilisateur,
    count_favoris_objet,
    get_favoris_counts,
    est_favori
)

# Blueprint creation
main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/', methods=['GET'])
def index() -> str:
    """Home page with Hero Section."""
    all_objects    = get_all_celestial_objects()
    all_categories = get_all_categories()

    return render_template(
        'home.html',
        total_objects=len(all_objects) if all_objects else 0,
        total_categories=len(all_categories) if all_categories else 0,
        now=datetime.datetime.now(),
        title="Home - AstroLearn"
    )


@main_bp.route('/catalogue', methods=['GET'])
def catalogue() -> str:
    """Catalogue page with search and filtering logic."""

    search_term      = request.args.get('search_term', '').strip()
    category_id_str  = request.args.get('category_id', '').strip()

    objects: List[Dict[str, Any]] = []

    if search_term:
        objects = search_celestial_objects(search_term)
        if category_id_str and category_id_str.isdigit():
            cat_id  = int(category_id_str)
            objects = [obj for obj in objects if obj.get('id_categorie') == cat_id]

    elif category_id_str and category_id_str.isdigit():
        objects = get_objects_by_category(int(category_id_str))

    else:
        objects = get_all_celestial_objects()

    categories = get_all_categories()

    if (search_term or category_id_str) and not objects:
        flash("Aucun objet ne correspond à vos critères.", 'warning')

    # Favoris : 2 requêtes max au lieu de N+1
    favoris_ids    = get_favoris_ids_utilisateur(session['user_id']) if session.get('user_id') else []
    favoris_counts = get_favoris_counts()  # 1 seule requête pour tous les compteurs
    for obj in objects:
        obj['nb_favoris'] = favoris_counts.get(obj['id_objet'], 0)

    return render_template(
        'catalogue.html',
        objects=objects,
        categories=categories,
        favoris_ids=favoris_ids,
        now=datetime.datetime.now(),
        title="Catalogue - AstroLearn"
    )


@main_bp.route('/object/<int:object_id>')
def object_detail(object_id: int) -> Union[str, Response]:
    """Celestial object detail page."""
    obj: Optional[Dict[str, Any]] = get_object_by_id(object_id)

    if obj is None:
        flash("Objet céleste introuvable.", 'error')
        return redirect(url_for('main_bp.catalogue'))

    # Favoris pour la page détail
    user_id    = session.get('user_id')
    est_fav    = est_favori(user_id, object_id) if user_id else False
    nb_favoris = count_favoris_objet(object_id)

    return render_template(
        'detail.html',
        obj=obj,
        est_favori=est_fav,
        nb_favoris=nb_favoris,
        now=datetime.datetime.now(),
        title=f"Détail : {obj['nom_fr']}"
    )


@main_bp.route('/formulaire')
def formulaire() -> str:
    """Survey form page (Tally integration)."""
    return render_template(
        'formulaire.html',
        external_url="https://tally.so/r/jaZGVR",
        now=datetime.datetime.now(),
        title="AstroLearn Survey"
    )

@main_bp.route('/legal')
def legal():
    return render_template('legal.html', title="Mentions Légales")