# fix_categories.py - Category Correction Script based on Keywords

import sqlite3
from typing import Dict, List, Optional, Any
from config import DATABASE_PATH

def get_category_mapping(name: str) -> str:
    """
    Business logic to determine the correct category based on name keywords.
    Returns the category name as a string.
    """
    n: str = name.lower()
    
    # ASTEROIDS & COMETS
    if any(w in n for w in ['asteroid', 'comet', 'astéroïde', 'comète', 'meteor']):
        return 'Astéroïde'
    
    # GALAXIES
    if any(w in n for w in ['galaxy', 'galaxie', 'andromeda', 'milky way', 'voie lactée']):
        return 'Galaxie'
    
    # NEBULAE
    if any(w in n for w in ['nebula', 'nébuleuse', 'orion nebula', 'helix']):
        return 'Nébuleuse'
    
    # PLANETS
    planets: List[str] = [
        'mercury', 'mercure', 'venus', 'vénus', 'earth', 'terre', 'mars', 
        'jupiter', 'saturn', 'saturne', 'uranus', 'neptune', 'pluto', 'pluton'
    ]
    if any(p in n for p in planets):
        return 'Planète'
    
    # MOONS
    moons: List[str] = [
        'moon', 'lune', 'io', 'europa', 'europe', 'ganymede', 'ganymède', 
        'callisto', 'titan', 'enceladus', 'encelade', 'triton', 'phobos', 'deimos'
    ]
    if any(m in n for m in moons) or 'satellite' in n:
        return 'Lune'
    
    # CLUSTERS
    if any(w in n for w in ['cluster', 'amas', 'globular']):
        return 'Amas Globulaire'
    
    # GENERAL SOLAR SYSTEM
    if 'solar system' in n:
        return 'Planète Externe'
    
    # DEFAULT FALLBACK
    return 'Planète'

def fix_all_categories() -> None:
    """Recategorizes all objects based on keywords in their names."""
    conn: sqlite3.Connection = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    
    try:
        # 1. Fetch category IDs into a dictionary {Name: ID}
        categories: Dict[str, int] = {}
        for cat in conn.execute("SELECT id_categorie, nom_categorie FROM CATEGORIE").fetchall():
            categories[cat['nom_categorie']] = cat['id_categorie']
        
        # 2. Fetch all objects
        objects: List[sqlite3.Row] = conn.execute(
            "SELECT id_objet, nom_fr, nom_scientifique FROM OBJET_CELESTE"
        ).fetchall()
        
        corrections_stats: Dict[str, int] = {k: 0 for k in categories.keys()}
        
        # 3. Process each object
        print("🔄 Processing objects...")
        for obj in objects:
            full_name: str = f"{obj['nom_fr']} {obj['nom_scientifique'] or ''}"
            target_cat_name: str = get_category_mapping(full_name)
            
            if target_cat_name in categories:
                conn.execute(
                    "UPDATE OBJET_CELESTE SET fk_id_categorie = ? WHERE id_objet = ?",
                    (categories[target_cat_name], obj['id_objet'])
                )
                corrections_stats[target_cat_name] += 1
        
        conn.commit()
        
        # 4. Display Results
        print("\n" + "="*40)
        print("✅ RECATEGORIZATION COMPLETE")
        print("="*40)
        for cat, count in corrections_stats.items():
            print(f" {cat:20} : {count:3} objects updated")
        
        # 5. New Distribution Stats
        print("\n📊 NEW DISTRIBUTION")
        print("-" * 40)
        distribution = conn.execute("""
            SELECT c.nom_categorie, COUNT(o.id_objet) as nb
            FROM CATEGORIE c
            LEFT JOIN OBJET_CELESTE o ON c.id_categorie = o.fk_id_categorie
            GROUP BY c.id_categorie
            ORDER BY nb DESC
        """).fetchall()
        
        for row in distribution:
            print(f" {row['nom_categorie']:20} → {row['nb']} objects")

    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    print("\n🔧 CATEGORY REPAIR UTILITY")
    print("="*40)
    print("This script will re-classify all objects based on internal keywords.")
    
    user_input: str = input("\n➡️ Start correction? (y/n): ")
    
    if user_input.lower() in ['y', 'yes', 'o', 'oui']:
        fix_all_categories()
        print("\n✨ Done! You can now restart Flask and test your filters.")
    else:
        print("\n❌ Operation cancelled.")