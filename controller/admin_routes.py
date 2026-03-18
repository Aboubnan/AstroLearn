import os
import datetime
import functools
import bcrypt as _bcrypt
from typing import Callable, Any, Union
from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, session, Response, jsonify)
from model.database import (
    get_admin_by_pseudo, check_password, get_db_connection,
    get_all_propositions, traiter_proposition, get_all_utilisateurs
)
from model.api_utils import ingest_solar_system_data_paged
from werkzeug.utils import secure_filename
from datetime import date
from deep_translator import GoogleTranslator

admin_bp = Blueprint('admin_bp', __name__)

def admin_required(view_func: Callable) -> Callable:
    @functools.wraps(view_func)
    def wrapper(*args: Any, **kwargs: Any) -> Union[Response, Any]:
        if not session.get('is_admin'):
            flash("Accès refusé. Veuillez vous connecter.", 'warning')
            return redirect(url_for('admin_bp.admin_login'))
        return view_func(*args, **kwargs)
    return wrapper

# --- AUTHENTICATION ---

@admin_bp.route('/admin_login', methods=['GET', 'POST'])
def admin_login() -> Union[str, Response]:
    if request.method == 'POST':
        pseudo   = request.form.get('pseudo', '')
        password = request.form.get('password', '')
        admin    = get_admin_by_pseudo(pseudo)

        if admin and check_password(admin['mot_de_passe_hash'], password):
            session.permanent    = True
            session['is_admin']  = True
            session['admin_id']  = admin['id_admin']
            flash("Connexion administrateur réussie.", 'success')
            return redirect(url_for('admin_bp.admin_dashboard'))

        flash("Pseudo ou mot de passe invalide.", 'error')

    return render_template('login.html', now=datetime.datetime.now(), title="Admin Login")

@admin_bp.route('/admin_logout')
def admin_logout() -> Response:
    session.clear()
    flash("Vous avez été déconnecté.", 'info')
    return redirect(url_for('main_bp.index'))

# --- DASHBOARD ---

@admin_bp.route('/admin_dashboard')
@admin_required
def admin_dashboard():
    conn = get_db_connection()
    cur  = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM objet_celeste")
    count_objects = cur.fetchone()[0]

    try:
        cur.execute("SELECT COUNT(*) FROM historique_ia")
        count_ia = cur.fetchone()[0]
    except:
        conn.rollback()
        count_ia = "0"

    cur.execute("""
        SELECT o.id_objet, o.nom_fr, o.date_publication, c.nom_categorie
        FROM objet_celeste o
        JOIN categorie c ON o.fk_id_categorie = c.id_categorie
        ORDER BY o.date_publication DESC
    """)
    rows = cur.fetchall()
    objects = [{'id_objet': r[0], 'nom_fr': r[1],
                'date_publication': r[2], 'nom_categorie': r[3]} for r in rows]

    cur.execute("SELECT id_admin, pseudo, nom, prenom, email FROM ADMINISTRATEUR ORDER BY id_admin ASC")
    admin_rows = cur.fetchall()
    admins = [{'id_admin': r[0], 'pseudo': r[1], 'nom': r[2] or '',
               'prenom': r[3] or '', 'email': r[4] or ''} for r in admin_rows]

    cur.close()
    conn.close()

    # Propositions en attente
    propositions = get_all_propositions()
    nb_en_attente = sum(1 for p in propositions if p['statut'] == 'en_attente')

    # Liste des utilisateurs
    utilisateurs = get_all_utilisateurs()

    return render_template('admin_dashboard.html',
                           objects=objects,
                           count_objects=count_objects,
                           count_ia=count_ia,
                           admins=admins,
                           propositions=propositions,
                           nb_en_attente=nb_en_attente,
                           utilisateurs=utilisateurs)

# --- CRUD OBJETS CÉLESTES ---

@admin_bp.route('/admin/add-object', methods=['GET', 'POST'])
@admin_required
def add_celestial_object():
    conn = get_db_connection()
    cur  = conn.cursor()

    if request.method == 'POST':
        name        = request.form.get('name')
        description = request.form.get('description')
        id_cat      = request.form.get('category_id')
        file        = request.files.get('image')

        image_url = "images/default_astro.png"
        if file and file.filename != '':
            filename    = secure_filename(file.filename)
            upload_path = os.path.join('static', 'uploads', 'objects')
            os.makedirs(upload_path, exist_ok=True)
            file.save(os.path.join(upload_path, filename))
            image_url = f"uploads/objects/{filename}"

        try:
            cur.execute("""
                INSERT INTO objet_celeste
                (nom_fr, nom_scientifique, description, url_image, date_publication, fk_id_categorie)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (name, name, description, image_url, date.today(), id_cat))
            conn.commit()
            flash(f"'{name}' ajouté avec succès !", "success")
            return redirect(url_for('admin_bp.admin_dashboard'))
        except Exception as e:
            conn.rollback()
            flash(f"Erreur : {e}", "error")

    cur.execute("SELECT id_categorie, nom_categorie FROM categorie ORDER BY nom_categorie")
    categories = cur.fetchall()
    cur.close(); conn.close()
    return render_template('add_object.html', categories=categories)

@admin_bp.route('/admin/edit-object/<int:object_id>', methods=['GET', 'POST'])
@admin_required
def edit_celestial_object(object_id):
    conn = get_db_connection()
    cur  = conn.cursor()

    if request.method == 'POST':
        nom_fr      = request.form.get('nom_fr')
        description = request.form.get('description')
        id_cat      = request.form.get('category_id')
        try:
            cur.execute("""
                UPDATE objet_celeste
                SET nom_fr=%s, description=%s, fk_id_categorie=%s
                WHERE id_objet=%s
            """, (nom_fr, description, id_cat, object_id))
            conn.commit()
            flash("Objet mis à jour !", "success")
            return redirect(url_for('admin_bp.admin_dashboard'))
        except Exception as e:
            conn.rollback()
            flash(f"Erreur : {e}", "error")

    cur.execute("SELECT * FROM objet_celeste WHERE id_objet = %s", (object_id,))
    obj = cur.fetchone()
    cur.execute("SELECT id_categorie, nom_categorie FROM categorie ORDER BY nom_categorie")
    categories = cur.fetchall()
    cur.close(); conn.close()
    return render_template('edit_object.html', obj=obj, categories=categories)

@admin_bp.route('/admin/delete-object/<int:object_id>', methods=['POST'])
@admin_required
def delete_celestial_object(object_id):
    conn = get_db_connection()
    cur  = conn.cursor()
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

# --- CRUD ADMINISTRATEURS ---

@admin_bp.route('/admin/add-admin', methods=['POST'])
@admin_required
def add_admin():
    pseudo   = request.form.get('pseudo',   '').strip()
    password = request.form.get('password', '').strip()
    password_confirm = request.form.get('password_confirm', '').strip()
    nom      = request.form.get('nom',      '').strip()
    prenom   = request.form.get('prenom',   '').strip()
    email    = request.form.get('email',    '').strip()

    if not pseudo or not password or not nom or not prenom or not email:
        flash("Tous les champs sont obligatoires.", "error")
        return redirect(url_for('admin_bp.admin_dashboard') + '#section-admins')
    if len(password) < 6:
        flash("Le mot de passe doit contenir au moins 6 caractères.", "error")
        return redirect(url_for('admin_bp.admin_dashboard') + '#section-admins')
    if password != password_confirm:
        flash("Les mots de passe ne correspondent pas.", "error")
        return redirect(url_for('admin_bp.admin_dashboard') + '#section-admins')

    conn = get_db_connection()
    cur  = conn.cursor()

    cur.execute("SELECT id_admin FROM ADMINISTRATEUR WHERE pseudo = %s", (pseudo,))
    if cur.fetchone():
        flash(f"Le pseudo '{pseudo}' est déjà utilisé.", "error")
        cur.close(); conn.close()
        return redirect(url_for('admin_bp.admin_dashboard') + '#section-admins')

    cur.execute("SELECT id_admin FROM ADMINISTRATEUR WHERE email = %s", (email,))
    if cur.fetchone():
        flash(f"L'email '{email}' est déjà utilisé.", "error")
        cur.close(); conn.close()
        return redirect(url_for('admin_bp.admin_dashboard') + '#section-admins')

    try:
        password_hash = _bcrypt.hashpw(password.encode('utf-8'), _bcrypt.gensalt()).decode('utf-8')
        cur.execute(
            "INSERT INTO ADMINISTRATEUR (pseudo, mot_de_passe_hash, nom, prenom, email) VALUES (%s,%s,%s,%s,%s)",
            (pseudo, password_hash, nom, prenom, email)
        )
        conn.commit()
        flash(f"Administrateur '{prenom} {nom}' créé !", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Erreur : {e}", "error")
    finally:
        cur.close(); conn.close()

    return redirect(url_for('admin_bp.admin_dashboard') + '#section-admins')

@admin_bp.route('/admin/edit-admin/<int:admin_id>', methods=['POST'])
@admin_required
def edit_admin(admin_id):
    if admin_id == session.get('admin_id'):
        flash("Vous ne pouvez pas modifier votre propre compte depuis ici.", "warning")
        return redirect(url_for('admin_bp.admin_dashboard') + '#section-admins')

    pseudo       = request.form.get('pseudo',       '').strip()
    nom          = request.form.get('nom',          '').strip()
    prenom       = request.form.get('prenom',       '').strip()
    email        = request.form.get('email',        '').strip()
    new_password = request.form.get('new_password', '').strip()

    if not pseudo or not nom or not prenom or not email:
        flash("Tous les champs sont obligatoires.", "error")
        return redirect(url_for('admin_bp.admin_dashboard') + '#section-admins')

    conn = get_db_connection()
    cur  = conn.cursor()
    try:
        if new_password:
            if len(new_password) < 6:
                flash("Mot de passe trop court (min. 6 caractères).", "error")
                return redirect(url_for('admin_bp.admin_dashboard') + '#section-admins')
            pwd_hash = _bcrypt.hashpw(new_password.encode('utf-8'), _bcrypt.gensalt()).decode('utf-8')
            cur.execute(
                "UPDATE ADMINISTRATEUR SET pseudo=%s, mot_de_passe_hash=%s, nom=%s, prenom=%s, email=%s WHERE id_admin=%s",
                (pseudo, pwd_hash, nom, prenom, email, admin_id)
            )
        else:
            cur.execute(
                "UPDATE ADMINISTRATEUR SET pseudo=%s, nom=%s, prenom=%s, email=%s WHERE id_admin=%s",
                (pseudo, nom, prenom, email, admin_id)
            )
        conn.commit()
        flash(f"Administrateur '{prenom} {nom}' mis à jour.", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Erreur : {e}", "error")
    finally:
        cur.close(); conn.close()

    return redirect(url_for('admin_bp.admin_dashboard') + '#section-admins')

@admin_bp.route('/admin/delete-admin/<int:admin_id>', methods=['POST'])
@admin_required
def delete_admin(admin_id):
    if admin_id == session.get('admin_id'):
        flash("Vous ne pouvez pas supprimer votre propre compte.", "error")
        return redirect(url_for('admin_bp.admin_dashboard') + '#section-admins')

    conn = get_db_connection()
    cur  = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM ADMINISTRATEUR")
    if cur.fetchone()[0] <= 1:
        flash("Impossible de supprimer le dernier administrateur.", "error")
        cur.close(); conn.close()
        return redirect(url_for('admin_bp.admin_dashboard') + '#section-admins')

    try:
        cur.execute("DELETE FROM ADMINISTRATEUR WHERE id_admin = %s", (admin_id,))
        conn.commit()
        flash("Administrateur supprimé.", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Erreur : {e}", "error")
    finally:
        cur.close(); conn.close()

    return redirect(url_for('admin_bp.admin_dashboard') + '#section-admins')

# --- GESTION DES PROPOSITIONS ---

@admin_bp.route('/admin/proposition/<int:prop_id>/traiter', methods=['POST'])
@admin_required
def traiter_proposition_route(prop_id):
    statut           = request.form.get('statut')
    commentaire      = request.form.get('commentaire', '').strip()
    nom_fr           = request.form.get('nom_fr', '').strip() or None
    nom_scientifique = request.form.get('nom_scientifique', '').strip() or None
    description      = request.form.get('description', '').strip() or None
    id_categorie     = request.form.get('category_id')
    id_categorie     = int(id_categorie) if id_categorie else None

    if statut not in ('accepte', 'refuse', 'modifie'):
        flash("Statut invalide.", "error")
        return redirect(url_for('admin_bp.admin_dashboard') + '#section-propositions')

    if traiter_proposition(prop_id, statut, commentaire, nom_fr,
                            nom_scientifique, description, id_categorie):
        labels = {'accepte': 'acceptée ✅', 'refuse': 'refusée ❌', 'modifie': 'modifiée et publiée ✏️'}
        flash(f"Proposition {labels.get(statut, statut)}.", "success")
    else:
        flash("Erreur lors du traitement.", "error")

    return redirect(url_for('admin_bp.admin_dashboard') + '#section-propositions')

# --- GESTION DES UTILISATEURS ---

@admin_bp.route('/admin/toggle-user/<int:user_id>', methods=['POST'])
@admin_required
def toggle_user(user_id):
    conn = get_db_connection()
    cur  = conn.cursor()
    try:
        cur.execute(
            "UPDATE UTILISATEUR SET est_actif = NOT est_actif WHERE id_utilisateur = %s RETURNING est_actif, pseudo",
            (user_id,)
        )
        row = cur.fetchone()
        conn.commit()
        etat = "activé" if row[0] else "désactivé"
        flash(f"Compte '{row[1]}' {etat}.", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Erreur : {e}", "error")
    finally:
        cur.close(); conn.close()
    return redirect(url_for('admin_bp.admin_dashboard') + '#section-utilisateurs')

# --- API & TOOLS ---

@admin_bp.route('/admin/ingest_solar_system', methods=['POST'])
@admin_required
def ingest_data():
    count = ingest_solar_system_data_paged('solar system', 5)
    flash(f"{count} objets synchronisés !" if count > 0 else "Échec de l'ingestion.",
          'success' if count > 0 else 'error')
    return redirect(url_for('admin_bp.admin_dashboard'))

@admin_bp.route('/api/translate', methods=['POST'])
def translate_text():
    data        = request.json
    text        = data.get('text', '')
    target_lang = data.get('lang', 'fr')
    if not text or len(text) < 3:
        return jsonify({'translated_text': text})
    try:
        source_lang = 'en' if target_lang == 'fr' else 'fr'
        translated  = GoogleTranslator(source=source_lang, target=target_lang).translate(text)
        return jsonify({'translated_text': translated})
    except Exception as e:
        return jsonify({'error': str(e)}), 500