# tests/test_validation.py
from model.database import create_utilisateur, get_utilisateur_by_identifiant


def test_utilisateur_validation():
    print("🔍 Test de robustesse : Validation des données utilisateur...")

    # Test 1 : Données manquantes
    res1 = create_utilisateur("", "", "", "", "", "non_precise", "")
    if not res1:
        print("✅ Succès : Le système rejette les données vides.")

    # Test 2 : Récupération utilisateur inexistant
    res2 = get_utilisateur_by_identifiant("utilisateur_inexistant_xyz")
    if not res2:
        print("✅ Succès : Retourne None pour un utilisateur inexistant.")


if __name__ == "__main__":
    test_utilisateur_validation()
