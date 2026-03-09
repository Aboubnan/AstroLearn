# tests/test_security.py
from model.database import hash_password, check_password

def test_encryption():
    print("🔍 Test de Sécurité : Chiffrement Bcrypt...")
    mdp_test = "Astro123!"
    
    # 1. Hachage
    hashed = hash_password(mdp_test)
    print(f"✅ Mot de passe haché : {hashed}")
    
    if mdp_test in hashed:
        print("❌ ÉCHEC : Le mot de passe apparaît en clair dans le hash !")
        return

    # 2. Vérification
    if check_password(hashed, mdp_test):
        print("✅ Vérification réussie : Le hash correspond au mot de passe.")
    else:
        print("❌ ÉCHEC : La vérification du hash a échoué.")

if __name__ == "__main__":
    test_encryption()