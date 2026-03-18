import os
import functools
from typing import Callable, Any, Union
from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, session, Response)
from model.database import (
    get_utilisateur_by_identifiant, get_utilisateur_by_id, check_password,
    create_utilisateur, update_utilisateur_profil, update_utilisateur_password,
    get_all_categories, create_proposition, get_propositions_by_user,
    count_notifs_non_lues, marquer_notifs_lues
)
from werkzeug.utils import secure_filename

user_bp = Blueprint('user_bp', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
UPLOAD_FOLDER_PROFILS = os.path.join('static', 'uploads', 'profils')
UPLOAD_FOLDER_PROPOSITIONS = os.path.join('static', 'uploads', 'propositions')

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(view_func: Callable) -> Callable:
    """Décorateur : redirige vers login si non connecté."""
    @functools.wraps(view_func)
    def wrapper(*args: Any, **kwargs: Any) -> Union[Response, Any]:
        if not session.get('user_id'):
            flash("Connectez-vous pour accéder à cette page.", 'warning')
            return redirect(url_for('auth_bp.login'))  # ← auth_bp, pas user_bp
        return view_func(*args, **kwargs)
    return wrapper

# ----------------------------------------------------
# INSCRIPTION
# ----------------------------------------------------

@user_bp.route('/inscription', methods=['GET', 'POST'])
def inscription():
    if session.get('user_id'):
        return redirect(url_for('user_bp.dashboard'))

    if request.method == 'POST':
        pseudo   = request.form.get('pseudo', '').strip()
        nom      = request.form.get('nom', '').strip()
        prenom   = request.form.get('prenom', '').strip()
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        password_confirm = request.form.get('password_confirm', '').strip()
        genre    = request.form.get('genre', 'non_precise')
        file     = request.files.get('photo_profil')

        if not all([pseudo, nom, prenom, email, password]):
            flash("Tous les champs obligatoires doivent être remplis.", "error")
            return render_template('inscription.html')

        if len(password) < 6:
            flash("Le mot de passe doit contenir au moins 6 caractères.", "error")
            return render_template('inscription.html')

        if password != password_confirm:
            flash("Les mots de passe ne correspondent pas.", "error")
            return render_template('inscription.html')

        if get_utilisateur_by_identifiant(pseudo):
            flash(f"Le pseudo '{pseudo}' est déjà utilisé.", "error")
            return render_template('inscription.html')

        if get_utilisateur_by_identifiant(email):
            flash(f"L'email '{email}' est déjà associé à un compte.", "error")
            return render_template('inscription.html')

        photo_path = 'uploads/profils/default_avatar.png'
        if file and file.filename != '' and allowed_file(file.filename):
            os.makedirs(UPLOAD_FOLDER_PROFILS, exist_ok=True)
            filename = secure_filename(f"{pseudo}_{file.filename}")
            file.save(os.path.join(UPLOAD_FOLDER_PROFILS, filename))
            photo_path = f'uploads/profils/{filename}'

        if create_utilisateur(pseudo, nom, prenom, email, password, genre, photo_path):
            flash("Compte créé avec succès ! Connectez-vous.", "success")
            return redirect(url_for('auth_bp.login'))  # ← auth_bp
        else:
            flash("Erreur lors de la création du compte.", "error")

    return render_template('inscription.html')

# ----------------------------------------------------
# DASHBOARD UTILISATEUR
# ----------------------------------------------------

@user_bp.route('/mon-espace')
@login_required
def dashboard():
    user = get_utilisateur_by_id(session['user_id'])
    propositions = get_propositions_by_user(session['user_id'])
    marquer_notifs_lues(session['user_id'])

    stats = {
        'total':      len(propositions),
        'en_attente': sum(1 for p in propositions if p['statut'] == 'en_attente'),
        'acceptes':   sum(1 for p in propositions if p['statut'] in ('accepte', 'modifie')),
        'refuses':    sum(1 for p in propositions if p['statut'] == 'refuse'),
    }

    return render_template('user_dashboard.html', user=user,
                           propositions=propositions, stats=stats)

# ----------------------------------------------------
# PROPOSER UN OBJET
# ----------------------------------------------------

@user_bp.route('/proposer-objet', methods=['GET', 'POST'])
@login_required
def proposer_objet():
    categories = get_all_categories()

    if request.method == 'POST':
        nom_fr           = request.form.get('nom_fr', '').strip()
        nom_scientifique = request.form.get('nom_scientifique', '').strip()
        description      = request.form.get('description', '').strip()
        id_categorie     = request.form.get('category_id')
        file             = request.files.get('image')

        if not nom_fr or not description or not id_categorie:
            flash("Le nom, la description et la catégorie sont obligatoires.", "error")
            return render_template('proposer_objet.html', categories=categories)

        url_image = None
        if file and file.filename != '' and allowed_file(file.filename):
            os.makedirs(UPLOAD_FOLDER_PROPOSITIONS, exist_ok=True)
            filename = secure_filename(f"prop_{session['user_id']}_{file.filename}")
            file.save(os.path.join(UPLOAD_FOLDER_PROPOSITIONS, filename))
            url_image = f'uploads/propositions/{filename}'

        if create_proposition(nom_fr, nom_scientifique, description,
                               url_image, int(id_categorie), session['user_id']):
            flash("Votre proposition a été envoyée ! L'admin la traitera sous peu.", "success")
            return redirect(url_for('user_bp.dashboard'))
        else:
            flash("Erreur lors de l'envoi de la proposition.", "error")

    return render_template('proposer_objet.html', categories=categories)

# ----------------------------------------------------
# MODIFIER LE PROFIL
# ----------------------------------------------------

@user_bp.route('/mon-profil', methods=['GET', 'POST'])
@login_required
def edit_profil():
    user = get_utilisateur_by_id(session['user_id'])

    if request.method == 'POST':
        nom    = request.form.get('nom', '').strip()
        prenom = request.form.get('prenom', '').strip()
        email  = request.form.get('email', '').strip()
        genre  = request.form.get('genre', 'non_precise')
        file   = request.files.get('photo_profil')

        if not nom or not prenom or not email:
            flash("Nom, prénom et email sont obligatoires.", "error")
            return render_template('edit_profil.html', user=user)

        photo_path = None
        if file and file.filename != '' and allowed_file(file.filename):
            os.makedirs(UPLOAD_FOLDER_PROFILS, exist_ok=True)
            filename = secure_filename(f"{session['user_pseudo']}_{file.filename}")
            file.save(os.path.join(UPLOAD_FOLDER_PROFILS, filename))
            photo_path = f'uploads/profils/{filename}'
            session['user_photo'] = photo_path

        if update_utilisateur_profil(session['user_id'], nom, prenom, email, genre, photo_path):
            flash("Profil mis à jour avec succès !", "success")
            return redirect(url_for('user_bp.dashboard'))
        else:
            flash("Erreur lors de la mise à jour.", "error")

    return render_template('edit_profil.html', user=user)

# ----------------------------------------------------
# CHANGER LE MOT DE PASSE
# ----------------------------------------------------

@user_bp.route('/changer-mot-de-passe', methods=['POST'])
@login_required
def change_password():
    current_password = request.form.get('current_password', '').strip()
    new_password     = request.form.get('new_password', '').strip()
    confirm_password = request.form.get('confirm_password', '').strip()

    full_user = get_utilisateur_by_identifiant(
        get_utilisateur_by_id(session['user_id'])['pseudo']
    )

    if not check_password(full_user['mot_de_passe_hash'], current_password):
        flash("Mot de passe actuel incorrect.", "error")
        return redirect(url_for('user_bp.edit_profil'))

    if len(new_password) < 6:
        flash("Le nouveau mot de passe doit contenir au moins 6 caractères.", "error")
        return redirect(url_for('user_bp.edit_profil'))

    if new_password != confirm_password:
        flash("Les nouveaux mots de passe ne correspondent pas.", "error")
        return redirect(url_for('user_bp.edit_profil'))

    if update_utilisateur_password(session['user_id'], new_password):
        flash("Mot de passe changé avec succès !", "success")
    else:
        flash("Erreur lors du changement de mot de passe.", "error")

    return redirect(url_for('user_bp.edit_profil'))