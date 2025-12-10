# controllers/skymap_routes.py

from flask import Blueprint, render_template

# Définition du Blueprint
# Le premier argument 'skymap' est le nom du Blueprint
skymap_bp = Blueprint('skymap', __name__, template_folder='../templates')

@skymap_bp.route('/sky-map')
def sky_map():
    """Affiche la page de la carte interactive du ciel."""
    # Le template_folder est configuré pour trouver sky_map.html dans le dossier templates/
    return render_template('sky_map.html', title='Carte du Ciel Interactif')

# Note : Il n'y a pas d'appel au Modèle ici, car la logique principale est Front-End (JavaScript)