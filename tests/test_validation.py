# tests/test_validation.py
from model.database import get_utilisateur_by_identifiant


def test_utilisateur_inexistant_retourne_none():
    assert get_utilisateur_by_identifiant("utilisateur_inexistant_xyz") is None


if __name__ == "__main__":
    test_utilisateur_inexistant_retourne_none()
