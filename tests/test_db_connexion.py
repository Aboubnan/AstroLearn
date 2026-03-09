# tests/test_db_connexion.py
from model.database import get_db_connection, get_all_categories

def test_database():
    print("🔍 Test d'Intégration : Connexion PostgreSQL...")
    conn = get_db_connection()
    
    if conn:
        print("✅ Connexion établie avec succès.")
        categories = get_all_categories()
        if categories:
            print(f"✅ {len(categories)} catégories récupérées avec succès.")
        else:
            print("⚠️ Connexion OK mais table CATEGORIE vide.")
        conn.close()
    else:
        print("❌ ÉCHEC : Impossible de joindre la base de données.")

if __name__ == "__main__":
    test_database()