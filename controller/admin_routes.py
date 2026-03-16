import os
import datetime
import functools
from typing import Callable, Any, Union
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, Response, jsonify
from model.database import get_admin_by_pseudo, check_password, get_db_connection
from model.api_utils import ingest_solar_system_data_paged
from werkzeug.utils import secure_filename
from datetime import date
from deep_translator import GoogleTranslator

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

# --- AUTHENTICATION ---

@admin_bp.route('/admin_login', methods=['GET', 'POST'])
def admin_login() -> Union[str, Response]:
    if request.method == 'POST':
        pseudo = request.form.get('pseudo', '')
        password = request.form.get('password', '')
        admin = get_admin_by_pseudo(pseudo)
        
        if admin and check_password(admin['mot_de_passe_hash'], password):
            session['is_admin'] = True
            session['admin_id'] = admin['id_admin']
            flash("Administrator connection successful.", 'success')
            return redirect(url_for('admin_bp.admin_dashboard'))
        flash("Invalid username or password.", 'error')
            
    return render_template('login.html', now=datetime.datetime.now(), title="Admin Login")

@admin_bp.route('/admin_logout')
def admin_logout() -> Response:
    session.pop('is_admin', None)
    session.pop('admin_id', None)
    flash("You have been logged out.", 'info')
    return redirect(url_for('main_bp.index'))

# --- DASHBOARD ---

@admin_bp.route('/admin_dashboard')
@admin_required
def admin_dashboard():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # 1. Compte des objets
    cur.execute("SELECT COUNT(*) FROM objet_celeste")
    count_objects = cur.fetchone()[0]

    # 2. Compte IA (Safe check)
    try:
        cur.execute("SELECT COUNT(*) FROM historique_ia")
        count_ia = cur.fetchone()[0]
    except:
        conn.rollback()
        count_ia = "0"

    # 3. Liste des objets
    cur.execute("""
        SELECT o.id_objet, o.nom_fr, o.date_publication, c.nom_categorie 
        FROM objet_celeste o
        JOIN categorie c ON o.fk_id_categorie = c.id_categorie
        ORDER BY o.date_publication DESC
    """)
    rows = cur.fetchall()
    objects = [{'id_objet': r[0], 'nom_fr': r[1], 'date_publication': r[2], 'nom_categorie': r[3]} for r in rows]

    cur.close()
    conn.close()
    
    return render_template('admin_dashboard.html', 
                           objects=objects, 
                           count_objects=count_objects, 
                           count_ia=count_ia)

# --- CRUD OPERATIONS ---

@admin_bp.route('/admin/add-object', methods=['GET', 'POST'])
@admin_required
def add_celestial_object():
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        id_cat = request.form.get('category_id')
        file = request.files.get('image')

        image_url = "images/default_astro.png"
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            upload_path = os.path.join('static', 'uploads', 'objects')
            if not os.path.exists(upload_path): os.makedirs(upload_path)
            file.save(os.path.join(upload_path, filename))
            image_url = f"uploads/objects/{filename}"

        try:
            cur.execute("""
                INSERT INTO objet_celeste (nom_fr, nom_scientifique, description, url_image, date_publication, fk_id_categorie)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (name, name, description, image_url, date.today(), id_cat))
            conn.commit()
            flash(f"'{name}' ajouté !", "success")
            return redirect(url_for('admin_bp.admin_dashboard'))
        except Exception as e:
            conn.rollback()
            flash(f"Erreur : {e}", "error")

    cur.execute("SELECT id_categorie, nom_categorie FROM categorie ORDER BY nom_categorie")
    categories = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('add_object.html', categories=categories)

@admin_bp.route('/admin/delete-object/<int:object_id>', methods=['POST'])
@admin_required
def delete_celestial_object(object_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM objet_celeste WHERE id_objet = %s", (object_id,))
        conn.commit()
        flash("Objet supprimé.", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Erreur : {e}", "error")
    finally:
        conn.close()
    return redirect(url_for('admin_bp.admin_dashboard'))

# --- API & TOOLS ---

@admin_bp.route('/admin/ingest_solar_system', methods=['POST'])
@admin_required
def ingest_data():
    count = ingest_solar_system_data_paged('solar system', 5)
    if count > 0:
        flash(f"{count} objets synchronisés !", 'success')
    else:
        flash("Échec de l'ingestion.", 'error')
    return redirect(url_for('admin_bp.admin_dashboard'))

@admin_bp.route('/api/translate', methods=['POST'])
def translate_text():
    """Route API de traduction accessible via JavaScript"""
    data = request.json
    text = data.get('text', '')
    target_lang = data.get('lang', 'fr')
    
    if not text or len(text) < 3:
        return jsonify({'translated_text': text})
        
    try:
        source_lang = 'en' if target_lang == 'fr' else 'fr'
        translated = GoogleTranslator(source=source_lang, target=target_lang).translate(text)
        return jsonify({'translated_text': translated})
    except Exception as e:
        return jsonify({'error': str(e)}), 500