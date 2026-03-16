# controller/admin_routes.py
import os
import datetime
import functools
from typing import Callable, Any, Union
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, Response
from model.database import get_admin_by_pseudo, check_password
from model.api_utils import ingest_solar_system_data_paged
from werkzeug.utils import secure_filename
from datetime import date
from model.database import get_db_connection

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

@admin_bp.route('/admin/add-object', methods=['GET', 'POST'])
@admin_required
def add_celestial_object():
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        # On récupère l'ID de la catégorie depuis le <select> du HTML
        id_cat = request.form.get('category_id')

        # --- Gestion de l'image ---
        file = request.files.get('image')
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            upload_path = os.path.join('static', 'uploads', 'objects')
            if not os.path.exists(upload_path):
                os.makedirs(upload_path)
            file.save(os.path.join(upload_path, filename))
            image_url = f"uploads/objects/{filename}"
        else:
            image_url = "images/default_astro.png"

        # --- Insertion SQL ---
        try:
            cur.execute("""
                INSERT INTO objet_celeste (
                    nom_fr, nom_scientifique, description, 
                    url_image, date_publication, fk_id_categorie
                )
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (name, name, description, image_url, date.today(), id_cat))
            
            conn.commit()
            flash(f"'{name}' a été ajouté au catalogue !", "success")
            return redirect(url_for('admin_bp.admin_dashboard'))
        except Exception as e:
            conn.rollback()
            flash(f"Erreur : {str(e)}", "error")

    # Pour l'affichage initial (GET), on récupère les catégories
    cur.execute("SELECT id_categorie, nom_categorie FROM categorie ORDER BY nom_categorie")
    categories = cur.fetchall()
    
    cur.close()
    conn.close()
    return render_template('add_object.html', categories=categories, title="Ajouter un objet")
    if request.method == 'POST':
        name = request.form.get('name')
        body_type = request.form.get('body_type')
        description = request.form.get('description')

        # --- Gestion de l'image (Ton code actuel est bon ici) ---
        file = request.files.get('image')
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            upload_path = os.path.join('static', 'uploads', 'objects')
            if not os.path.exists(upload_path):
                os.makedirs(upload_path)
            file.save(os.path.join(upload_path, filename))
            image_url = f"uploads/objects/{filename}"
        else:
            image_url = "images/default_astro.png"

        # --- INSERTION EN BASE DE DONNÉES ---
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            # On définit une catégorie par défaut (ex: 1 pour Planète) 
            # ou on récupère l'ID envoyé par le formulaire
            id_cat = request.form.get('category_id', 1) 
            
            cur.execute("""
                INSERT INTO objet_celeste (
                    nom_fr, 
                    nom_scientifique, 
                    description, 
                    url_image, 
                    date_publication, 
                    fk_id_categorie
                )
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                name,               # nom_fr
                name,               # nom_scientifique (on met le même par défaut)
                description,        # description
                image_url,          # url_image
                date.today(),       # date_publication (obligatoire !)
                id_cat              # fk_id_categorie (obligatoire !)
            ))
            
            conn.commit()
            flash(f"L'objet '{name}' a été ajouté avec succès !", "success")
        except Exception as e:
            conn.rollback()
            print(f"Erreur SQL détaillée : {e}") # Pour voir l'erreur dans ton terminal
            flash(f"Erreur lors de l'ajout : {str(e)}", "error")
        finally:
            cur.close()
            conn.close()

        return redirect(url_for('admin_bp.admin_dashboard'))

    return render_template('add_object.html', title="Ajouter un objet")
    if request.method == 'POST':
        name = request.form.get('name')
        # ... récupère tes autres champs ...

        # Gestion de l'image
        file = request.files.get('image')
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            # On définit le chemin où sauvegarder (ex: static/uploads/objects/)
            upload_path = os.path.join('static', 'uploads', 'objects')
            
            # Créer le dossier s'il n'existe pas
            if not os.path.exists(upload_path):
                os.makedirs(upload_path)
                
            file.save(os.path.join(upload_path, filename))
            image_url = f"uploads/objects/{filename}"
        else:
            image_url = "images/default_astro.png" # Une image par défaut

        # Ici, ajoute 'image_url' dans ta requête d'insertion SQL
        # db.execute("INSERT INTO celestial_objects ...", (name, ..., image_url))
        
        flash(f"L'objet '{name}' a été ajouté !", "success")
        return redirect(url_for('admin_bp.admin_dashboard'))

    return render_template('add_object.html', title="Ajouter un objet")