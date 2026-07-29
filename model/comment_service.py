# model/comment_service.py

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from model.mongo_utils import get_commentaires_collection

MAX_COMMENT_LENGTH = 1000


class CommentaireService:
    """Gère les fils de commentaires imbriqués (profondeur illimitée) d'un objet céleste.

    Un document MongoDB par objet céleste, contenant l'arbre complet des
    commentaires et de leurs réponses. Ce document est de taille modeste
    (commentaires pédagogiques courts), donc la stratégie "lire l'arbre,
    le modifier en mémoire, le réécrire" reste simple et sûre.
    """

    def __init__(self) -> None:
        self._collection = get_commentaires_collection()

    def get_commentaires(self, objet_id: int) -> List[Dict[str, Any]]:
        doc = self._collection.find_one({"objet_id": objet_id})
        return doc["commentaires"] if doc else []

    def ajouter_commentaire(
        self,
        objet_id: int,
        utilisateur_id: int,
        pseudo: str,
        texte: str,
        parent_id: Optional[str] = None,
    ) -> str:
        """Ajoute un commentaire racine, ou une réponse si `parent_id` est fourni.

        Lève ValueError si le texte est vide, trop long, ou si `parent_id`
        ne correspond à aucun commentaire existant.
        """
        texte = (texte or "").strip()
        if not texte:
            raise ValueError("Commentaire vide")
        if len(texte) > MAX_COMMENT_LENGTH:
            raise ValueError(
                f"Commentaire trop long (max {MAX_COMMENT_LENGTH} caractères)"
            )

        nouveau_commentaire = {
            "commentaire_id": str(uuid.uuid4()),
            "utilisateur_id": utilisateur_id,
            "pseudo": pseudo,
            "texte": texte,
            "date": datetime.now(timezone.utc).isoformat(),
            "reponses": [],
        }

        commentaires = self.get_commentaires(objet_id)

        if parent_id is None:
            commentaires.append(nouveau_commentaire)
        else:
            if not self._inserer_reponse(commentaires, parent_id, nouveau_commentaire):
                raise ValueError("Commentaire parent introuvable")

        self._collection.update_one(
            {"objet_id": objet_id},
            {"$set": {"commentaires": commentaires}},
            upsert=True,
        )

        return nouveau_commentaire["commentaire_id"]

    def _inserer_reponse(
        self,
        noeuds: List[Dict[str, Any]],
        parent_id: str,
        nouveau_commentaire: Dict[str, Any],
    ) -> bool:
        """Parcourt récursivement l'arbre pour insérer une réponse sous `parent_id`."""
        for noeud in noeuds:
            if noeud["commentaire_id"] == parent_id:
                noeud["reponses"].append(nouveau_commentaire)
                return True
            if self._inserer_reponse(noeud["reponses"], parent_id, nouveau_commentaire):
                return True
        return False
