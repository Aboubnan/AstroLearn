# tests/test_security.py
from model.database import hash_password, check_password


def test_encryption():
    mdp_test = "Astro123!"

    hashed = hash_password(mdp_test)
    assert mdp_test not in hashed, "Le mot de passe apparaît en clair dans le hash !"

    assert check_password(hashed, mdp_test), "La vérification du hash a échoué."
    assert not check_password(hashed, "MauvaisMotDePasse")


def test_hash_password_is_salted():
    """Deux hachages du même mot de passe doivent différer (sel bcrypt aléatoire)."""
    mdp_test = "Astro123!"

    assert hash_password(mdp_test) != hash_password(mdp_test)


def test_hash_password_uses_bcrypt_format():
    hashed = hash_password("Astro123!")

    assert hashed.startswith(
        ("$2a$", "$2b$", "$2y$")
    ), "Le hash ne suit pas le format bcrypt attendu."


if __name__ == "__main__":
    test_encryption()
    test_hash_password_is_salted()
    test_hash_password_uses_bcrypt_format()
