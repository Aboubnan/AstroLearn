# controller/admin_routes.py

import datetime
import functools
from typing import Callable, Any, Union
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, Response
from model.database import get_admin_by_pseudo, check_password
from model.api_utils import ingest_solar_system_data_paged

# Blueprint creation
admin_bp = Blueprint('admin_bp', __name__)

def admin_required(view_func: Callable) -> Callable:
    """Decorator to ensure the user is an administrator."""
    @functools.wraps(view_func)
    def wrapper(*args: Any, **kwargs: Any) -> Union[Response, Any]:
        if not session.get('is_admin'):
            flash("Access denied. Please log in.", 'warning')
            return redirect(url_for('admin_bp.admin_login'))
        return view_func(*args, **kwargs)
    return wrapper


@admin_bp.route('/admin_login', methods=['GET', 'POST'])
def admin_login() -> Union[str, Response]:
    """Admin Login route (Requirement F.05)."""
    
    if request.method == 'POST':
        pseudo: str = request.form.get('pseudo', '')
        password: str = request.form.get('password', '')
        
        admin: dict = get_admin_by_pseudo(pseudo)
        
        if admin:
            # Check password using the hash stored in the database
            if check_password(admin['mot_de_passe_hash'], password):
                session['is_admin'] = True
                session['admin_id'] = admin['id_admin']
                flash("Administrator connection successful.", 'success')
                return redirect(url_for('admin_bp.admin_dashboard'))
            else:
                flash("Invalid username or password.", 'error')
        else:
            flash("Invalid username or password.", 'error')
            
    return render_template(
        'login.html',
        now=datetime.datetime.now(),
        title="Admin Login"
    )

@admin_bp.route('/admin_dashboard')
@admin_required
def admin_dashboard() -> str:
    """Admin Dashboard (Protected route)."""
    return render_template(
        'admin_dashboard.html',
        now=datetime.datetime.now(),
        title="Admin Dashboard"
    )

@admin_bp.route('/admin/ingest_solar_system', methods=['POST'])
@admin_required
def ingest_data() -> Response:
    """Admin route to trigger paged Solar System data ingestion."""

    search_term: str = 'solar system'
    max_pages: int = 5

    # Run the ingestion script from api_utils
    count: int = ingest_solar_system_data_paged(search_term, max_pages)

    if count > 0:
        flash(
            f"{count} objects found via '{search_term}' (up to {max_pages} pages) "
            "have been inserted/updated.", 
            'success'
        )
    else:
        flash("Solar System data ingestion failed (check logs and API).", 'error')

    return redirect(url_for('admin_bp.admin_dashboard'))

@admin_bp.route('/admin_logout')
def admin_logout() -> Response:
    """Admin Logout route."""
    session.pop('is_admin', None)
    session.pop('admin_id', None)
    flash("You have been logged out.", 'info')
    # Redirect to the main index (from 'main_bp')
    return redirect(url_for('main_bp.index'))