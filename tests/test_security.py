# tests/test_security.py
from model.database import hash_password, check_password


def test_encryption():
    mdp_test = "Astro123!"

    hashed = hash_password(mdp_test)
    assert mdp_test not in hashed, "Le mot de passe apparaît en clair dans le hash !"

    assert check_password(hashed, mdp_test), "La vérification du hash a échoué."
    assert not check_password(hashed, "MauvaisMotDePasse")


if __name__ == "__main__":
    test_encryption()
