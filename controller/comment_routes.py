# controller/comment_routes.py

import functools
from typing import Any, Callable, Optional, Tuple
from flask import Blueprint, request, redirect, url_for, flash, session, Response

from model.comment_service import CommentaireService

comment_bp = Blueprint("comment_bp", __name__)

ADMIN_PSEUDO_AFFICHE = "Administration AstroLearn"


def _identite_auteur() -> Optional[Tuple[Optional[int], str, bool]]:
    """Identité (utilisateur_id, pseudo, est_admin) de l'auteur connecté.

    Renvoie None si ni un compte utilisateur ni un compte admin n'est
    connecté. Les comptes admin et utilisateur reposent sur deux systèmes
    de session distincts (admin_id vs user_id) : c'est pour ça qu'on ne
    peut pas se contenter d'un login_required générique ici.
    """
    if session.get("user_id"):
        return session["user_id"], session.get("user_pseudo", "Anonyme"), False
    if session.get("is_admin"):
        return None, ADMIN_PSEUDO_AFFICHE, True
    return None


def utilisateur_ou_admin_requis(view_func: Callable) -> Callable:
    @functools.wraps(view_func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if _identite_auteur() is None:
            flash("Connectez-vous pour commenter.", "warning")
            return redirect(url_for("auth_bp.login"))
        return view_func(*args, **kwargs)

    return wrapper


@comment_bp.route("/objet/<int:objet_id>/commentaire", methods=["POST"])
@utilisateur_ou_admin_requis
def ajouter_commentaire(objet_id: int) -> Response:
    """Ajoute un commentaire racine sur un objet céleste."""
    return _ajouter(objet_id, parent_id=None)


@comment_bp.route(
    "/objet/<int:objet_id>/commentaire/<commentaire_id>/reponse", methods=["POST"]
)
@utilisateur_ou_admin_requis
def repondre_commentaire(objet_id: int, commentaire_id: str) -> Response:
    """Ajoute une réponse imbriquée à un commentaire existant."""
    return _ajouter(objet_id, parent_id=commentaire_id)


def _ajouter(objet_id: int, parent_id: Optional[str]) -> Response:
    utilisateur_id, pseudo, est_admin = _identite_auteur()

    try:
        CommentaireService().ajouter_commentaire(
            objet_id=objet_id,
            utilisateur_id=utilisateur_id,
            pseudo=pseudo,
            texte=request.form.get("texte", ""),
            parent_id=parent_id,
            est_admin=est_admin,
        )
    except ValueError as e:
        flash(str(e), "error")
    else:
        flash("Commentaire publié.", "success")

    return redirect(
        url_for("main_bp.object_detail", object_id=objet_id) + "#commentaires"
    )
