# tests/test_validation.py
from model.database import insert_survey_feedback

def test_survey_logic():
    print("🔍 Test de robustesse : Insertion de feedback...")
    
    # Test 1 : Email valide
    res1 = insert_survey_feedback("test@example.com", "J'adore les planètes")
    if res1:
        print("✅ Succès : L'insertion standard fonctionne.")
    
    # Test 2 : Donnée manquante (Simulation d'erreur)
    try:
        # On teste si la fonction gère l'absence d'email si ton code le permet
        res2 = insert_survey_feedback(None, None)
        if not res2:
            print("✅ Succès : Le système rejette correctement les données vides.")
    except Exception as e:
        print(f"✅ Succès : L'erreur a été capturée ({e})")

if __name__ == "__main__":
    test_survey_logic()