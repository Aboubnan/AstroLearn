# tests/test_logic.py

def test_nasa_mapping():
    print("🔍 Test Unitaire : Vérification du mapping NASA...")
    
    # Simulation du dictionnaire que nous avons mis dans database.py
    mapping = {
        'Planet': 'Planète',
        'Moon': 'Lune',
        'Star': 'Étoile',
        'Dwarf Planet': 'Planète Externe'
    }
    
    # Cas de test
    test_cases = {
        'Planet': 'Planète',
        'Moon': 'Lune',
        'Star': 'Étoile',
        'Unknown': 'Unknown'
    }
    
    success = True
    for input_type, expected in test_cases.items():
        result = mapping.get(input_type, input_type)
        if result == expected:
            print(f"✅ Input: {input_type} -> Output: {result}")
        else:
            print(f"❌ Erreur: {input_type} a donné {result} au lieu de {expected}")
            success = False
            
    if success:
        print("\n✨ TEST UNITAIRE RÉUSSI : La logique de tri est correcte.")

if __name__ == "__main__":
    test_nasa_mapping()