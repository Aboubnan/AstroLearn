# controller/main_routes.py

import datetime
from typing import List, Dict, Any, Optional, Union
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response

from model.database import (
    get_all_celestial_objects,
    get_object_by_id,
    get_all_categories,
    search_celestial_objects,
    filter_celestial_objects
)

# Blueprint creation
main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/', methods=['GET'])
def index() -> str:
    """Home page with Hero Section."""
    return render_template(
        'home.html',
        now=datetime.datetime.now(),
        title="Home - AstroLearn"
    )


@main_bp.route('/catalogue', methods=['GET'])
def catalogue() -> str:
    """Catalogue page with search and filtering logic."""
    
    search_term: str = request.args.get('search_term', '').strip()
    category_id_str: str = request.args.get('category_id', '').strip()
    
    objects: List[Dict[str, Any]] = []
    
    # CASE 1: Search term + Category filter
    if search_term and category_id_str and category_id_str.isdigit():
        category_id: int = int(category_id_str)
        # We fetch by category first, then filter by search term in Python
        objects = filter_celestial_objects(category_id)
        search_lower: str = search_term.lower()
        objects = [
            obj for obj in objects 
            if search_lower in obj['nom_fr'].lower() 
            or (obj['nom_scientifique'] and search_lower in obj['nom_scientifique'].lower())
            or search_lower in obj.get('extrait_description', '').lower()
        ]
    
    # CASE 2: Search term only
    elif search_term:
        objects = search_celestial_objects(search_term)
    
    # CASE 3: Category filter only
    elif category_id_str and category_id_str.isdigit():
        category_id = int(category_id_str)
        objects = filter_celestial_objects(category_id)
    
    # CASE 4: Display all objects
    else:
        objects = get_all_celestial_objects()
    
    categories: List[Dict[str, Any]] = get_all_categories()
    
    # Feedback if no results found
    if (search_term or category_id_str) and not objects:
        flash("No celestial objects match your criteria.", 'warning')
    
    return render_template(
        'catalogue.html',
        objects=objects,
        categories=categories,
        now=datetime.datetime.now(),
        title="Catalogue - AstroLearn"
    )


@main_bp.route('/object/<int:object_id>')
def object_detail(object_id: int) -> Union[str, Response]:
    """Celestial object detail page."""
    obj: Optional[Dict[str, Any]] = get_object_by_id(object_id)
    
    if obj is None:
        flash("Celestial object not found.", 'error')
        return redirect(url_for('main_bp.catalogue'))
    
    return render_template(
        'detail.html',
        obj=obj,
        now=datetime.datetime.now(),
        title=f"Detail: {obj['nom_fr']}"
    )


@main_bp.route('/formulaire')
def formulaire() -> str:
    """Survey form page (Tally integration)."""
    external_form_url: str = "https://tally.so/r/jaZGVR"
    return render_template(
        'formulaire.html',
        external_url=external_form_url,
        now=datetime.datetime.now(),
        title="AstroLearn Survey"
    )