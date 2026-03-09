# tests/test_db.py
from model.database import get_all_categories

def test_categories():
    print("🔍 Test de lecture des catégories PostgreSQL...")
    categories = get_all_categories()
    
    if categories and len(categories) > 0:
        print(f"✅ Succès : {len(categories)} catégories trouvées.")
        for cat in categories:
            print(f"   - {cat['nom_categorie']}")
    else:
        print("❌ Échec : Aucune catégorie trouvée ou erreur de connexion.")

if __name__ == "__main__":
    test_categories()