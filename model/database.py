# model/database.py

import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from config import DATABASE_URL

# ----------------------------------------------------
# 1. SQL Queries for Physical Data Model (PostgreSQL)
# ----------------------------------------------------

CREATE_TABLES_SQL: str = """
CREATE TABLE IF NOT EXISTS CATEGORIE (
    id_categorie SERIAL PRIMARY KEY,
    nom_categorie TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS OBJET_CELESTE (
    id_objet SERIAL PRIMARY KEY,
    nom_fr TEXT NOT NULL UNIQUE,
    nom_scientifique TEXT, 
    description TEXT NOT NULL,
    distance_al REAL, 
    url_image TEXT, 
    date_publication DATE NOT NULL,
    fk_id_categorie INTEGER NOT NULL,
    CONSTRAINT fk_categorie
        FOREIGN KEY(fk_id_categorie) 
        REFERENCES CATEGORIE(id_categorie)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ADMINISTRATEUR (
    id_admin SERIAL PRIMARY KEY,
    pseudo TEXT NOT NULL UNIQUE,
    mot_de_passe_hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS SAISIR (
    fk_id_admin INTEGER NOT NULL,
    fk_id_objet INTEGER NOT NULL,
    date_saisie TIMESTAMP NOT NULL,
    PRIMARY KEY (fk_id_admin, fk_id_objet),
    FOREIGN KEY (fk_id_admin) REFERENCES ADMINISTRATEUR(id_admin),
    FOREIGN KEY (fk_id_objet) REFERENCES OBJET_CELESTE(id_objet)
);

CREATE TABLE IF NOT EXISTS AVIS_SONDAGE (
    id_avis SERIAL PRIMARY KEY,
    email TEXT NOT NULL,
    preference TEXT NOT NULL,
    date_sondage TIMESTAMP NOT NULL,
    fk_id_objet INTEGER,
    FOREIGN KEY (fk_id_objet) REFERENCES OBJET_CELESTE(id_objet)
);
"""

# ----------------------------------------------------
# 2. Connection and Security Functions
# ----------------------------------------------------

def get_db_connection():
    """Creates and returns a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"❌ Impossible de se connecter à PostgreSQL: {e}")
        return None

def create_tables() -> None:
    """Creates all tables defined in the PDM."""
    conn = get_db_connection()
    if not conn: return
    try:
        with conn.cursor() as cur:
            cur.execute(CREATE_TABLES_SQL)
        conn.commit()
        print("✅ Database tables created successfully.")
    except Exception as e:
        print(f"❌ Error during table creation: {e}")
        conn.rollback()
    finally:
        conn.close()

def hash_password(password: str) -> str:
    """Hashes a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def insert_initial_data() -> None:
    """Inserts default categories and the initial administrator."""
    conn = get_db_connection()
    if not conn: return
    try:
        categories = [
            ('Amas Globulaire',), ('Astéroïde',), ('Étoile',),
            ('Galaxie',), ('Lune',), ('Nébuleuse',),
            ('Planète',), ('Planète Externe',)
        ]
        with conn.cursor() as cur:
            cur.executemany("INSERT INTO CATEGORIE (nom_categorie) VALUES (%s) ON CONFLICT DO NOTHING", categories)
            
            hashed_pwd = hash_password("admin123")
            cur.execute(
                "INSERT INTO ADMINISTRATEUR (pseudo, mot_de_passe_hash) VALUES (%s, %s) ON CONFLICT DO NOTHING", 
                ('webmaster', hashed_pwd)
            )
        conn.commit()
        print("✅ Initial data inserted successfully.")
    except Exception as e:
        print(f"❌ Error inserting initial data: {e}")
        conn.rollback()
    finally:
        conn.close()

def initialize_database() -> None:
    """Initializes the PostgreSQL database."""
    print("🚀 Initializing PostgreSQL database...")
    create_tables()
    insert_initial_data()

# ----------------------------------------------------
# 3. Application CRUD Functions
# ----------------------------------------------------

def get_all_celestial_objects() -> List[Dict[str, Any]]:
    """Retrieves all celestial objects, ordered by publication date."""
    conn = get_db_connection()
    if not conn: return []
    query = """
    SELECT 
        o.id_objet, o.nom_fr, o.nom_scientifique, 
        LEFT(o.description, 150) AS extrait_description, 
        o.url_image, o.date_publication, c.nom_categorie
    FROM OBJET_CELESTE o
    JOIN CATEGORIE c ON o.fk_id_categorie = c.id_categorie
    ORDER BY o.date_publication DESC;
    """
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query)
            return cur.fetchall()
    except Exception as e:
        print(f"Error reading catalogue: {e}")
        return []
    finally:
        conn.close()

def get_object_by_id(object_id: int) -> Optional[Dict[str, Any]]:
    """Retrieves detailed information for a specific celestial object."""
    conn = get_db_connection()
    if not conn: return None
    query = """
    SELECT 
        o.id_objet, o.nom_fr, o.nom_scientifique, o.description, o.distance_al, 
        o.url_image, o.date_publication, c.nom_categorie
    FROM OBJET_CELESTE o
    JOIN CATEGORIE c ON o.fk_id_categorie = c.id_categorie
    WHERE o.id_objet = %s
    """
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (object_id,))
            return cur.fetchone()
    except Exception as e:
        print(f"Error reading object details: {e}")
        return None
    finally:
        conn.close()

def search_celestial_objects(search_term: str) -> List[Dict[str, Any]]:
    """Performs a case-insensitive search across names and descriptions."""
    conn = get_db_connection()
    if not conn: return []
    search_pattern = f'%{search_term.lower()}%'
    query = """
    SELECT 
        o.id_objet, o.nom_fr, o.nom_scientifique, 
        LEFT(o.description, 150) AS extrait_description, 
        o.url_image, o.date_publication, c.nom_categorie
    FROM OBJET_CELESTE o
    JOIN CATEGORIE c ON o.fk_id_categorie = c.id_categorie
    WHERE 
        LOWER(o.nom_fr) LIKE %s OR 
        LOWER(o.nom_scientifique) LIKE %s OR 
        LOWER(o.description) LIKE %s
    ORDER BY o.date_publication DESC;
    """
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (search_pattern, search_pattern, search_pattern))
            return cur.fetchall()
    except Exception as e:
        print(f"Error during search: {e}")
        return []
    finally:
        conn.close()

def insert_survey_feedback(email: str, preference: str, object_id: Optional[int] = None) -> bool:
    """Inserts feedback from the user survey."""
    conn = get_db_connection()
    if not conn: return False
    now = datetime.now()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO AVIS_SONDAGE (email, preference, date_sondage, fk_id_objet) VALUES (%s, %s, %s, %s);",
                (email, preference, now, object_id)
            )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error inserting survey feedback: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def get_all_categories() -> List[Dict[str, Any]]:
    """Retrieves all categories sorted alphabetically."""
    conn = get_db_connection()
    if not conn: return []
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id_categorie, nom_categorie FROM CATEGORIE ORDER BY nom_categorie")
            return cur.fetchall()
    except Exception as e:
        print(f"Error reading categories: {e}")
        return []
    finally:
        conn.close()

def get_admin_by_pseudo(pseudo: str) -> Optional[Dict[str, Any]]:
    """Retrieves an admin record by their username."""
    conn = get_db_connection()
    if not conn: return None
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id_admin, pseudo, mot_de_passe_hash FROM ADMINISTRATEUR WHERE pseudo = %s", (pseudo,))
            return cur.fetchone()
    except Exception as e:
        print(f"Error reading admin record: {e}")
        return None
    finally:
        conn.close()

def check_password(hashed_password: str, user_password: str) -> bool:
    """Verifies a plain-text password against a bcrypt hash."""
    return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_objects_by_category(category_id: int) -> List[Dict[str, Any]]:
    """Retrieves all celestial objects belonging to a specific category."""
    conn = get_db_connection()
    if not conn: return []
    
    query = """
    SELECT 
        o.id_objet, o.nom_fr, o.nom_scientifique, 
        LEFT(o.description, 150) AS extrait_description, 
        o.url_image, o.date_publication, c.nom_categorie,
        o.fk_id_categorie as id_categorie
    FROM OBJET_CELESTE o
    JOIN CATEGORIE c ON o.fk_id_categorie = c.id_categorie
    WHERE o.fk_id_categorie = %s
    ORDER BY o.nom_fr ASC;
    """
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (category_id,))
            return cur.fetchall()
    except Exception as e:
        print(f"❌ Erreur lors de la récupération par catégorie : {e}")
        return []
    finally:
        conn.close()

def insert_solar_system_body(name_fr: str, name_en: str, description: str, 
                             body_type: str, mass_value: Optional[float] = None, 
                             density: Optional[float] = None, image_url: Optional[str] = None) -> bool:
    """
    Inserts a new celestial object from the NASA API into PostgreSQL with translated categories.
    """
    conn = get_db_connection()
    if not conn: return False
    
    # Mapping des types NASA (Anglais) vers tes catégories (Français)
    mapping = {
        'Planet': 'Planète',
        'Moon': 'Lune',
        'Star': 'Étoile',
        'Asteroid': 'Astéroïde',
        'Dwarf Planet': 'Planète Externe',
        'Comet': 'Astéroïde', # On peut grouper ou créer une catégorie Comète
        'Nebula': 'Nébuleuse'
    }
    
    translated_type = mapping.get(body_type, body_type)
    
    query_cat = "SELECT id_categorie FROM CATEGORIE WHERE nom_categorie ILIKE %s LIMIT 1"
    
    query_insert = """
    INSERT INTO OBJET_CELESTE (nom_fr, nom_scientifique, description, url_image, date_publication, fk_id_categorie)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT (nom_fr) DO UPDATE SET 
        fk_id_categorie = EXCLUDED.fk_id_categorie,
        description = EXCLUDED.description;
    """
    
    try:
        with conn.cursor() as cur:
            # 1. Trouver l'ID de la catégorie correspondante
            cur.execute(query_cat, (f"%{translated_type}%",))
            row = cur.fetchone()
            category_id = row[0] if row else 1 # Défaut à 1 si non trouvé
            
            # 2. Insérer ou mettre à jour si le nom existe déjà (pour corriger les catégories)
            cur.execute(query_insert, (
                name_fr, name_en, description, image_url, date.today(), category_id
            ))
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'insertion de l'objet {name_fr} : {e}")
        conn.rollback()
        return False
    finally:
        conn.close()