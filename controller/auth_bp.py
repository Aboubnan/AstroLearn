from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, session)
from model.database import (
    get_admin_by_pseudo, get_utilisateur_by_identifiant, check_password
)

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/connexion', methods=['GET', 'POST'])
def login():
    # Déjà connecté → rediriger vers le bon espace
    if session.get('is_admin'):
        return redirect(url_for('admin_bp.admin_dashboard'))
    if session.get('user_id'):
        return redirect(url_for('user_bp.dashboard'))

    if request.method == 'POST':
        identifiant = request.form.get('identifiant', '').strip()
        password    = request.form.get('password', '').strip()

        if not identifiant or not password:
            flash("Veuillez remplir tous les champs.", "error")
            return render_template('login.html')

        # 1. Cherche d'abord dans les administrateurs
        admin = get_admin_by_pseudo(identifiant)
        if admin and check_password(admin['mot_de_passe_hash'], password):
            session.permanent   = True
            session['is_admin'] = True
            session['admin_id'] = admin['id_admin']
            flash(f"Bienvenue, {admin.get('prenom') or admin['pseudo']} !", "success")
            return redirect(url_for('admin_bp.admin_dashboard'))

        # 2. Sinon cherche dans les utilisateurs
        user = get_utilisateur_by_identifiant(identifiant)
        if user:
            if not user['est_actif']:
                flash("Votre compte a été désactivé. Contactez l'administrateur.", "error")
                return render_template('login.html')

            if check_password(user['mot_de_passe_hash'], password):
                session.permanent      = True
                session['user_id']     = user['id_utilisateur']
                session['user_pseudo'] = user['pseudo']
                session['user_photo']  = user['photo_profil']
                flash(f"Bienvenue, {user['prenom']} !", "success")
                return redirect(url_for('user_bp.dashboard'))

        # Aucune correspondance
        flash("Identifiant ou mot de passe incorrect.", "error")

    return render_template('login.html')


@auth_bp.route('/deconnexion')
def logout():
    session.clear()
    flash("Vous avez été déconnecté.", "info")
    return redirect(url_for('main_bp.index'))