# controller/admin_routes.py

import datetime
import functools
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from model.database import get_admin_by_pseudo, check_password
from model.api_utils import ingest_solar_system_data_paged # Import de la fonction d'ingestion

# Création du Blueprint
admin_bp = Blueprint('admin_bp', __name__)

# Décorateur de Sécurité (le décorateur lui-même doit être défini ici ou dans un fichier utilitaire)
def admin_required(view_func):
    """Décorateur pour exiger que l'utilisateur soit administrateur."""
    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):
        if not session.get('is_admin'):
            flash("Accès refusé. Veuillez vous connecter.", 'warning')
            # Utilisez le nom de fonction du Blueprint: 'admin_bp.admin_login'
            return redirect(url_for('admin_bp.admin_login'))
        return view_func(*args, **kwargs)
    return wrapper


@admin_bp.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    """Route de connexion Admin (F.05)."""
    
    if request.method == 'POST':
        pseudo = request.form.get('pseudo')
        password = request.form.get('password')
        
        admin = get_admin_by_pseudo(pseudo)
        
        if admin:
            if check_password(admin['mot_de_passe_hash'], password):
                session['is_admin'] = True
                session['admin_id'] = admin['id_admin']
                flash("Connexion Administrateur réussie.", 'success')
                return redirect(url_for('admin_bp.admin_dashboard'))
            else:
                flash("Identifiant ou mot de passe incorrect.", 'error')
        else:
            flash("Identifiant ou mot de passe incorrect.", 'error')
            
    return render_template('login.html',
                           now=datetime.datetime.now(),
                           title="Connexion Administrateur")

@admin_bp.route('/admin_dashboard')
@admin_required
def admin_dashboard():
    """Tableau de bord Admin (Route protégée)."""
    return render_template('admin_dashboard.html',
                           now=datetime.datetime.now(),
                           title="Tableau de Bord Admin")

@admin_bp.route('/admin/ingest_solar_system', methods=['POST'])
@admin_required
def ingest_data():
    """Route Admin pour déclencher l'ingestion des données paginées du Système Solaire."""

    search_term = 'solar system'
    max_pages = 5

    count = ingest_solar_system_data_paged(search_term, max_pages)

    if count > 0:
        flash(f"{count} objets trouvés via la recherche '{search_term}' (jusqu'à {max_pages} pages) ont été insérés/mis à jour.", 'success')
    else:
        flash("Échec de l'ingestion des données du Système Solaire (vérifiez les logs et l'API).", 'error')

    return redirect(url_for('admin_bp.admin_dashboard'))

@admin_bp.route('/admin_logout')
def admin_logout():
    """Déconnexion Admin."""
    session.pop('is_admin', None)
    session.pop('admin_id', None)
    flash("Vous êtes déconnecté.", 'info')
    # Redirection vers l'index qui est dans un autre Blueprint ('main_bp.index')
    return redirect(url_for('main_bp.index'))