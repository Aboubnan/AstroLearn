# tests/test_comment_service.py
from unittest.mock import MagicMock, patch
import pytest

from model.comment_service import CommentaireService, MAX_COMMENT_LENGTH


class _FakeCollection:
    """Simule les opérations pymongo utilisées par CommentaireService,
    sur un ensemble de documents {objet_id: {...}} tenus en mémoire.
    """

    def __init__(self, docs=None):
        self._docs = {d["objet_id"]: dict(d) for d in (docs or [])}
        for i, d in enumerate(self._docs.values()):
            d.setdefault("_id", i)

    def find_one(self, query):
        return self._docs.get(query.get("objet_id"))

    def find(self):
        return list(self._docs.values())

    def update_one(self, filt, update, upsert=False):
        commentaires = update["$set"]["commentaires"]
        if "objet_id" in filt:
            objet_id = filt["objet_id"]
            if objet_id in self._docs:
                self._docs[objet_id]["commentaires"] = commentaires
            elif upsert:
                self._docs[objet_id] = {
                    "objet_id": objet_id,
                    "commentaires": commentaires,
                    "_id": len(self._docs),
                }
        elif "_id" in filt:
            for d in self._docs.values():
                if d["_id"] == filt["_id"]:
                    d["commentaires"] = commentaires


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


def _service_with_fake_collection(docs=None):
    collection = _FakeCollection(docs)
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


def test_commentaire_admin_a_utilisateur_id_none_et_est_admin_vrai():
    service, collection = _service_with_mock_collection()

    service.ajouter_commentaire(
        1,
        utilisateur_id=None,
        pseudo="Administration AstroLearn",
        texte="Réponse officielle",
        est_admin=True,
    )

    args, _ = collection.update_one.call_args
    commentaire = args[1]["$set"]["commentaires"][0]
    assert commentaire["utilisateur_id"] is None
    assert commentaire["est_admin"] is True
    assert commentaire["pseudo"] == "Administration AstroLearn"


def _commentaire(commentaire_id, texte, vu=False, reponses=None):
    return {
        "commentaire_id": commentaire_id,
        "utilisateur_id": 1,
        "pseudo": "alice",
        "texte": texte,
        "date": "2026-01-01T00:00:00",
        "vu": vu,
        "reponses": reponses or [],
    }


def test_get_tous_commentaires_aplatit_plusieurs_objets_et_tri_par_date():
    docs = [
        {
            "objet_id": 1,
            "commentaires": [
                {**_commentaire("a", "Premier"), "date": "2026-01-01T00:00:00"}
            ],
        },
        {
            "objet_id": 2,
            "commentaires": [
                {**_commentaire("b", "Second"), "date": "2026-02-01T00:00:00"}
            ],
        },
    ]
    service, _ = _service_with_fake_collection(docs)

    resultats = service.get_tous_commentaires()

    assert len(resultats) == 2
    assert resultats[0]["texte"] == "Second"  # plus récent en premier
    assert "reponses" not in resultats[0]
    assert {r["objet_id"] for r in resultats} == {1, 2}


def test_get_tous_commentaires_aplatit_les_reponses_imbriquees():
    docs = [
        {
            "objet_id": 1,
            "commentaires": [
                _commentaire(
                    "a", "Racine", reponses=[_commentaire("b", "Réponse imbriquée")]
                )
            ],
        }
    ]
    service, _ = _service_with_fake_collection(docs)

    resultats = service.get_tous_commentaires()

    textes = {r["texte"] for r in resultats}
    assert textes == {"Racine", "Réponse imbriquée"}


def test_count_non_lus():
    docs = [
        {
            "objet_id": 1,
            "commentaires": [
                _commentaire("a", "Lu", vu=True),
                _commentaire("b", "Pas lu", vu=False),
            ],
        }
    ]
    service, _ = _service_with_fake_collection(docs)

    assert service.count_non_lus() == 1


def test_marquer_tous_lus():
    docs = [
        {
            "objet_id": 1,
            "commentaires": [
                _commentaire(
                    "a", "Racine", vu=False, reponses=[_commentaire("b", "Réponse")]
                )
            ],
        }
    ]
    service, _ = _service_with_fake_collection(docs)

    service.marquer_tous_lus()

    assert service.count_non_lus() == 0


def test_supprimer_commentaire_racine():
    docs = [{"objet_id": 1, "commentaires": [_commentaire("a", "À supprimer")]}]
    service, _ = _service_with_fake_collection(docs)

    assert service.supprimer_commentaire(1, "a") is True
    assert service.get_commentaires(1) == []


def test_supprimer_commentaire_supprime_le_sous_arbre():
    docs = [
        {
            "objet_id": 1,
            "commentaires": [
                _commentaire(
                    "a", "Racine", reponses=[_commentaire("b", "Sera supprimée")]
                )
            ],
        }
    ]
    service, _ = _service_with_fake_collection(docs)

    assert service.supprimer_commentaire(1, "a") is True
    assert service.get_commentaires(1) == []


def test_supprimer_commentaire_introuvable_renvoie_false():
    docs = [{"objet_id": 1, "commentaires": [_commentaire("a", "Existe")]}]
    service, _ = _service_with_fake_collection(docs)

    assert service.supprimer_commentaire(1, "id-inexistant") is False
    assert len(service.get_commentaires(1)) == 1
