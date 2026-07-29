# controller/comment_routes.py

from typing import Optional
from flask import Blueprint, request, redirect, url_for, flash, session, Response

from controller.user_bp import login_required
from model.comment_service import CommentaireService

comment_bp = Blueprint("comment_bp", __name__)


@comment_bp.route("/objet/<int:objet_id>/commentaire", methods=["POST"])
@login_required
def ajouter_commentaire(objet_id: int) -> Response:
    """Ajoute un commentaire racine sur un objet céleste."""
    return _ajouter(objet_id, parent_id=None)


@comment_bp.route(
    "/objet/<int:objet_id>/commentaire/<commentaire_id>/reponse", methods=["POST"]
)
@login_required
def repondre_commentaire(objet_id: int, commentaire_id: str) -> Response:
    """Ajoute une réponse imbriquée à un commentaire existant."""
    return _ajouter(objet_id, parent_id=commentaire_id)


def _ajouter(objet_id: int, parent_id: Optional[str]) -> Response:
    try:
        CommentaireService().ajouter_commentaire(
            objet_id=objet_id,
            utilisateur_id=session["user_id"],
            pseudo=session.get("user_pseudo", "Anonyme"),
            texte=request.form.get("texte", ""),
            parent_id=parent_id,
        )
    except ValueError as e:
        flash(str(e), "error")
    else:
        flash("Commentaire publié.", "success")

    return redirect(
        url_for("main_bp.object_detail", object_id=objet_id) + "#commentaires"
    )
