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
        utilisateur_id: Optional[int],
        pseudo: str,
        texte: str,
        parent_id: Optional[str] = None,
        est_admin: bool = False,
    ) -> str:
        """Ajoute un commentaire racine, ou une réponse si `parent_id` est fourni.

        `utilisateur_id` est `None` pour un commentaire posté par un
        administrateur (identifié uniquement par `pseudo` et `est_admin`).

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
            "vu": False,
            "est_admin": est_admin,
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

    def get_tous_commentaires(self) -> List[Dict[str, Any]]:
        """Aplatit l'arbre de commentaires de tous les objets, pour la modération admin.

        Chaque entrée conserve `objet_id` mais pas `reponses` (vue à plat),
        triée du plus récent au plus ancien.
        """
        resultats: List[Dict[str, Any]] = []
        for doc in self._collection.find():
            self._aplatir(doc.get("commentaires", []), doc["objet_id"], resultats)
        resultats.sort(key=lambda c: c["date"], reverse=True)
        return resultats

    def _aplatir(
        self,
        noeuds: List[Dict[str, Any]],
        objet_id: int,
        resultats: List[Dict[str, Any]],
    ) -> None:
        for noeud in noeuds:
            entree = {k: v for k, v in noeud.items() if k != "reponses"}
            entree["objet_id"] = objet_id
            resultats.append(entree)
            self._aplatir(noeud.get("reponses", []), objet_id, resultats)

    def count_non_lus(self) -> int:
        return sum(1 for c in self.get_tous_commentaires() if not c.get("vu", False))

    def marquer_tous_lus(self) -> None:
        for doc in self._collection.find():
            commentaires = doc.get("commentaires", [])
            self._marquer_lu(commentaires)
            self._collection.update_one(
                {"_id": doc["_id"]}, {"$set": {"commentaires": commentaires}}
            )

    def _marquer_lu(self, noeuds: List[Dict[str, Any]]) -> None:
        for noeud in noeuds:
            noeud["vu"] = True
            self._marquer_lu(noeud["reponses"])

    def supprimer_commentaire(self, objet_id: int, commentaire_id: str) -> bool:
        """Supprime un commentaire et l'intégralité de ses réponses imbriquées."""
        commentaires = self.get_commentaires(objet_id)
        if not self._supprimer_noeud(commentaires, commentaire_id):
            return False

        self._collection.update_one(
            {"objet_id": objet_id}, {"$set": {"commentaires": commentaires}}
        )
        return True

    def _supprimer_noeud(
        self, noeuds: List[Dict[str, Any]], commentaire_id: str
    ) -> bool:
        for i, noeud in enumerate(noeuds):
            if noeud["commentaire_id"] == commentaire_id:
                del noeuds[i]
                return True
            if self._supprimer_noeud(noeud["reponses"], commentaire_id):
                return True
        return False
