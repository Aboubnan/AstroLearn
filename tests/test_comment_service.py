# tests/test_comment_service.py
from unittest.mock import MagicMock, patch
import pytest

from model.comment_service import CommentaireService, MAX_COMMENT_LENGTH


def _service_with_mock_collection(existing_commentaires=None):
    collection = MagicMock()
    collection.find_one.return_value = (
        {"objet_id": 1, "commentaires": existing_commentaires}
        if existing_commentaires is not None
        else None
    )
    with patch(
        "model.comment_service.get_commentaires_collection", return_value=collection
    ):
        service = CommentaireService()
    return service, collection


def test_get_commentaires_renvoie_liste_vide_si_aucun_document():
    service, _ = _service_with_mock_collection()
    assert service.get_commentaires(1) == []


def test_ajouter_commentaire_rejette_texte_vide():
    service, _ = _service_with_mock_collection()
    with pytest.raises(ValueError):
        service.ajouter_commentaire(1, utilisateur_id=1, pseudo="alice", texte="   ")


def test_ajouter_commentaire_rejette_texte_trop_long():
    service, _ = _service_with_mock_collection()
    with pytest.raises(ValueError):
        service.ajouter_commentaire(
            1, utilisateur_id=1, pseudo="alice", texte="a" * (MAX_COMMENT_LENGTH + 1)
        )


def test_ajouter_commentaire_racine_est_persiste():
    service, collection = _service_with_mock_collection()

    service.ajouter_commentaire(1, utilisateur_id=1, pseudo="alice", texte="Salut !")

    args, kwargs = collection.update_one.call_args
    commentaires = args[1]["$set"]["commentaires"]
    assert len(commentaires) == 1
    assert commentaires[0]["texte"] == "Salut !"
    assert commentaires[0]["pseudo"] == "alice"
    assert commentaires[0]["reponses"] == []
    assert kwargs["upsert"] is True


def test_ajouter_reponse_est_imbriquee_sous_le_parent():
    parent_id = "abc-123"
    existing = [
        {
            "commentaire_id": parent_id,
            "utilisateur_id": 1,
            "pseudo": "alice",
            "texte": "Commentaire racine",
            "date": "2026-01-01T00:00:00",
            "reponses": [],
        }
    ]
    service, collection = _service_with_mock_collection(existing)

    service.ajouter_commentaire(
        1, utilisateur_id=2, pseudo="bob", texte="Réponse", parent_id=parent_id
    )

    args, _ = collection.update_one.call_args
    commentaires = args[1]["$set"]["commentaires"]
    assert commentaires[0]["reponses"][0]["texte"] == "Réponse"
    assert commentaires[0]["reponses"][0]["pseudo"] == "bob"


def test_reponse_a_une_reponse_est_imbriquee_en_profondeur():
    niveau_1_id = "niveau-1"
    niveau_2_id = "niveau-2"
    existing = [
        {
            "commentaire_id": niveau_1_id,
            "utilisateur_id": 1,
            "pseudo": "alice",
            "texte": "Niveau 1",
            "date": "2026-01-01T00:00:00",
            "reponses": [
                {
                    "commentaire_id": niveau_2_id,
                    "utilisateur_id": 2,
                    "pseudo": "bob",
                    "texte": "Niveau 2",
                    "date": "2026-01-01T00:00:00",
                    "reponses": [],
                }
            ],
        }
    ]
    service, collection = _service_with_mock_collection(existing)

    service.ajouter_commentaire(
        1, utilisateur_id=3, pseudo="chris", texte="Niveau 3", parent_id=niveau_2_id
    )

    args, _ = collection.update_one.call_args
    commentaires = args[1]["$set"]["commentaires"]
    niveau_3 = commentaires[0]["reponses"][0]["reponses"][0]
    assert niveau_3["texte"] == "Niveau 3"
    assert niveau_3["pseudo"] == "chris"


def test_ajouter_reponse_parent_introuvable_leve_erreur():
    service, _ = _service_with_mock_collection(existing_commentaires=[])
    with pytest.raises(ValueError):
        service.ajouter_commentaire(
            1,
            utilisateur_id=1,
            pseudo="alice",
            texte="Réponse orpheline",
            parent_id="id-inexistant",
        )
