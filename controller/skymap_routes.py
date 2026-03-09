# controllers/skymap_routes.py

from flask import Blueprint, render_template

# Blueprint definition
# The template_folder is set to look for sky_map.html in the templates/ directory
skymap_bp = Blueprint('skymap', __name__, template_folder='../templates')

@skymap_bp.route('/sky-map')
def sky_map() -> str:
    """
    Renders the interactive sky map page.
    
    Note: The core logic of this feature is handled on the Front-End 
    using JavaScript (Virtual Sky / Stellarium-style libraries).
    """
    return render_template(
        'sky_map.html', 
        title='Interactive Sky Map'
    )