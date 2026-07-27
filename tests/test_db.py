# tests/test_db.py
from model.database import get_all_categories


def test_categories():
    categories = get_all_categories()
    assert categories, "Aucune catégorie trouvée ou erreur de connexion."
    assert all("nom_categorie" in cat for cat in categories)


if __name__ == "__main__":
    test_categories()
