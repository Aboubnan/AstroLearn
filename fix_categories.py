# fix_categories.py - Script de correction des catégories basé sur les mots-clés

import sqlite3
from config import DATABASE_PATH

def fix_all_categories():
    """Recatégorise tous les objets basés sur les mots-clés dans leurs noms."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    
    # Récupérer les IDs des catégories
    categories = {}
    for cat in conn.execute("SELECT id_categorie, nom_categorie FROM CATEGORIE").fetchall():
        categories[cat['nom_categorie']] = cat['id_categorie']
    
    # Récupérer tous les objets
    objets = conn.execute("SELECT id_objet, nom_fr, nom_scientifique FROM OBJET_CELESTE").fetchall()
    
    corrections = {
        'Galaxie': 0,
        'Nébuleuse': 0,
        'Planète': 0,
        'Lune': 0,
        'Astéroïde': 0,
        'Amas Globulaire': 0,
        'Planète Externe': 0
    }
    
    for obj in objets:
        nom_complet = f"{obj['nom_fr']} {obj['nom_scientifique'] or ''}".lower()
        nouvelle_cat = None
        
        # ASTÉROÏDES & COMÈTES (très fréquent dans vos données)
        if any(word in nom_complet for word in ['asteroid', 'comet', 'astéroïde', 'comète', 'meteor']):
            nouvelle_cat = 'Astéroïde'
        
        # GALAXIES
        elif any(word in nom_complet for word in ['galaxy', 'galaxie', 'andromeda', 'milky way', 'voie lactée']):
            nouvelle_cat = 'Galaxie'
        
        # NÉBULEUSES
        elif any(word in nom_complet for word in ['nebula', 'nébuleuse', 'orion nebula', 'helix']):
            nouvelle_cat = 'Nébuleuse'
        
        # PLANÈTES (noms exacts)
        elif any(planet in nom_complet for planet in [
            'mercury', 'mercure', 'venus', 'vénus', 
            'earth', 'terre', 'mars', 
            'jupiter', 'saturn', 'saturne', 
            'uranus', 'neptune', 'pluto', 'pluton'
        ]):
            nouvelle_cat = 'Planète'
        
        # LUNES (noms exacts et mots-clés)
        elif any(moon in nom_complet for moon in [
            'moon', 'lune', 'io', 'europa', 'europe', 
            'ganymede', 'ganymède', 'callisto', 
            'titan', 'enceladus', 'encelade', 
            'triton', 'phobos', 'deimos'
        ]) or 'satellite' in nom_complet:
            nouvelle_cat = 'Lune'
        
        # AMAS GLOBULAIRES
        elif any(word in nom_complet for word in ['cluster', 'amas', 'globular']):
            nouvelle_cat = 'Amas Globulaire'
        
        # SYSTÈME SOLAIRE GÉNÉRAL (si "solar system" sans autre mot-clé)
        elif 'solar system' in nom_complet and nouvelle_cat is None:
            nouvelle_cat = 'Planète Externe'
        
        # PAR DÉFAUT (laisser en Planète)
        else:
            nouvelle_cat = 'Planète'
        
        # Mettre à jour la catégorie
        if nouvelle_cat and nouvelle_cat in categories:
            conn.execute(
                "UPDATE OBJET_CELESTE SET fk_id_categorie = ? WHERE id_objet = ?",
                (categories[nouvelle_cat], obj['id_objet'])
            )
            corrections[nouvelle_cat] += 1
    
    conn.commit()
    
    # Afficher le résultat
    print("\n" + "="*60)
    print("✅ RECATÉGORISATION TERMINÉE")
    print("="*60)
    for cat, count in corrections.items():
        print(f"  {cat:20} : {count:3} objets")
    print("="*60)
    
    # Afficher la nouvelle répartition
    print("\n📊 NOUVELLE RÉPARTITION")
    print("-"*60)
    repartition = conn.execute("""
        SELECT c.nom_categorie, COUNT(o.id_objet) as nb
        FROM CATEGORIE c
        LEFT JOIN OBJET_CELESTE o ON c.id_categorie = o.fk_id_categorie
        GROUP BY c.id_categorie
        ORDER BY nb DESC
    """).fetchall()
    
    for r in repartition:
        print(f"  {r['nom_categorie']:20} → {r['nb']} objets")
    
    conn.close()

if __name__ == '__main__':
    print("\n🔧 CORRECTION AUTOMATIQUE DES CATÉGORIES")
    print("="*60)
    print("Ce script va recatégoriser vos 420 objets basés sur")
    print("les mots-clés dans leurs noms (asteroid, galaxy, etc.)")
    print("="*60)
    
    response = input("\n➡️  Lancer la correction ? (oui/non) : ")
    
    if response.lower() in ['oui', 'o', 'yes', 'y']:
        print("\n🔄 Correction en cours...\n")
        fix_all_categories()
        print("\n✅ Terminé ! Relancez votre application Flask.")
        print("💡 Testez maintenant les filtres par catégorie.")
    else:
        print("\n❌ Annulé.")
    