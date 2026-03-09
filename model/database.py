# model/database.py

import sqlite3
import os
import bcrypt
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, date
from config import DATABASE_PATH

# ----------------------------------------------------
# 1. SQL Queries for Physical Data Model (PDM)
# ----------------------------------------------------

CREATE_TABLES_SQL: str = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS CATEGORIE (
    id_categorie INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_categorie TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS OBJET_CELESTE (
    id_objet INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_fr TEXT NOT NULL UNIQUE,
    nom_scientifique TEXT, 
    description TEXT NOT NULL,
    distance_al REAL, 
    url_image TEXT, 
    date_publication TEXT NOT NULL,
    fk_id_categorie INTEGER NOT NULL,
    FOREIGN KEY (fk_id_categorie) REFERENCES CATEGORIE(id_categorie)
);

CREATE TABLE IF NOT EXISTS ADMINISTRATEUR (
    id_admin INTEGER PRIMARY KEY AUTOINCREMENT,
    pseudo TEXT NOT NULL UNIQUE,
    mot_de_passe_hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS SAISIR (
    fk_id_admin INTEGER NOT NULL,
    fk_id_objet INTEGER NOT NULL,
    date_saisie TEXT NOT NULL,
    PRIMARY KEY (fk_id_admin, fk_id_objet),
    FOREIGN KEY (fk_id_admin) REFERENCES ADMINISTRATEUR(id_admin),
    FOREIGN KEY (fk_id_objet) REFERENCES OBJET_CELESTE(id_objet)
);

CREATE TABLE IF NOT EXISTS AVIS_SONDAGE (
    id_avis INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    preference TEXT NOT NULL,
    date_sondage TEXT NOT NULL,
    fk_id_objet INTEGER,
    FOREIGN KEY (fk_id_objet) REFERENCES OBJET_CELESTE(id_objet)
);
"""

# ----------------------------------------------------
# 2. Initialization and Security Functions
# ----------------------------------------------------

def get_db_connection() -> sqlite3.Connection:
    """Creates and returns a connection to the SQLite database."""
    conn: sqlite3.Connection = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables() -> None:
    """Creates all tables defined in the PDM."""
    conn: sqlite3.Connection = get_db_connection()
    try:
        conn.executescript(CREATE_TABLES_SQL)
        print("Database tables created successfully.")
    except sqlite3.Error as e:
        print(f"Error during table creation: {e}")
    finally:
        conn.close()


def hash_password(password: str) -> str:
    """Hashes a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def insert_initial_data() -> None:
    """Inserts default categories and the initial administrator."""
    conn: sqlite3.Connection = get_db_connection()
    try:
        categories: List[tuple] = [
            ('Amas Globulaire',), ('Astéroïde',), ('Étoile',),
            ('Galaxie',), ('Lune',), ('Nébuleuse',),
            ('Planète',), ('Planète Externe',)
        ]
        conn.executemany("INSERT OR IGNORE INTO CATEGORIE (nom_categorie) VALUES (?)", categories)
        
        hashed_pwd: str = hash_password("admin123")
        conn.execute(
            "INSERT OR IGNORE INTO ADMINISTRATEUR (pseudo, mot_de_passe_hash) VALUES (?, ?)", 
            ('webmaster', hashed_pwd)
        )

        conn.commit()
        print("Initial categories and Administrator inserted successfully.")
    except sqlite3.Error as e:
        print(f"Error inserting initial data: {e}")
        conn.rollback()
    finally:
        conn.close()


def initialize_database() -> None:
    """Initializes the database: creates tables and inserts default data."""
    if os.path.exists(DATABASE_PATH):
        print(f"Database '{DATABASE_PATH}' already exists.")
    else:
        print(f"Creating database '{DATABASE_PATH}'...")
        create_tables()
        insert_initial_data()

# ----------------------------------------------------
# 3. Application CRUD Functions
# ----------------------------------------------------

def get_all_celestial_objects() -> List[Dict[str, Any]]:
    """Retrieves all celestial objects, ordered by publication date."""
    conn: sqlite3.Connection = get_db_connection()
    query: str = """
    SELECT 
        o.id_objet, o.nom_fr, o.nom_scientifique, 
        SUBSTR(o.description, 1, 150) AS extrait_description, 
        o.url_image, o.date_publication, c.nom_categorie
    FROM OBJET_CELESTE o
    JOIN CATEGORIE c ON o.fk_id_categorie = c.id_categorie
    ORDER BY o.date_publication DESC;
    """
    try:
        objects: List[sqlite3.Row] = conn.execute(query).fetchall()
        return [dict(obj) for obj in objects]
    except sqlite3.Error as e:
        print(f"Error reading catalogue: {e}")
        return []
    finally:
        conn.close()


def filter_celestial_objects(category_id: int) -> List[Dict[str, Any]]:
    """Retrieves objects filtered by category ID."""
    conn: sqlite3.Connection = get_db_connection()
    try:
        query: str = """
        SELECT 
            o.id_objet, o.nom_fr, o.nom_scientifique, 
            SUBSTR(o.description, 1, 150) AS extrait_description, 
            o.url_image, o.date_publication, c.nom_categorie
        FROM OBJET_CELESTE o
        JOIN CATEGORIE c ON o.fk_id_categorie = c.id_categorie
        WHERE o.fk_id_categorie = ?
        ORDER BY o.date_publication DESC;
        """
        objects: List[sqlite3.Row] = conn.execute(query, (category_id,)).fetchall()
        return [dict(obj) for obj in objects]
    except sqlite3.Error as e:
        print(f"Error filtering objects: {e}")
        return []
    finally:
        conn.close()


def get_object_by_id(object_id: int) -> Optional[Dict[str, Any]]:
    """Retrieves detailed information for a specific celestial object."""
    conn: sqlite3.Connection = get_db_connection()
    query: str = """
    SELECT 
        o.id_objet, o.nom_fr, o.nom_scientifique, o.description, o.distance_al, 
        o.url_image, o.date_publication, c.nom_categorie
    FROM OBJET_CELESTE o
    JOIN CATEGORIE c ON o.fk_id_categorie = c.id_categorie
    WHERE o.id_objet = ?
    """
    try:
        obj: Optional[sqlite3.Row] = conn.execute(query, (object_id,)).fetchone()
        return dict(obj) if obj else None
    except sqlite3.Error as e:
        print(f"Error reading object details: {e}")
        return None
    finally:
        conn.close()


def search_celestial_objects(search_term: str) -> List[Dict[str, Any]]:
    """Performs a case-insensitive search across names and descriptions."""
    conn: sqlite3.Connection = get_db_connection()
    search_pattern: str = f'%{search_term.lower()}%'
    
    query: str = """
    SELECT 
        o.id_objet, o.nom_fr, o.nom_scientifique, 
        SUBSTR(o.description, 1, 150) AS extrait_description, 
        o.url_image, o.date_publication, c.nom_categorie
    FROM OBJET_CELESTE o
    JOIN CATEGORIE c ON o.fk_id_categorie = c.id_categorie
    WHERE 
        LOWER(o.nom_fr) LIKE ? OR 
        LOWER(o.nom_scientifique) LIKE ? OR 
        LOWER(o.description) LIKE ?
    ORDER BY o.date_publication DESC;
    """
    try:
        objects: List[sqlite3.Row] = conn.execute(
            query, (search_pattern, search_pattern, search_pattern)
        ).fetchall()
        return [dict(obj) for obj in objects]
    except sqlite3.Error as e:
        print(f"Error during search: {e}")
        return []
    finally:
        conn.close()


def insert_solar_system_body(
    name_fr: str, name_en: str, description: str, body_type: str, 
    mass_value: Optional[float], density: Optional[float], image_url: str
) -> bool:
    """Inserts a celestial body with smart automated categorization."""
    conn: sqlite3.Connection = get_db_connection()
    
    name_fr_l: str = name_fr.lower()
    name_en_l: str = (name_en or '').lower()
    type_l: str = body_type.lower()
    
    # Category determination logic
    if any(k in name_fr_l or k in type_l for k in ['asteroid', 'comet', 'astéroïde', 'comète']):
        cat_name = 'Astéroïde'
    elif any(k in name_fr_l or k in type_l for k in ['galaxy', 'galaxie']):
        cat_name = 'Galaxie'
    elif any(k in name_fr_l or k in type_l for k in ['nebula', 'nébuleuse']):
        cat_name = 'Nébuleuse'
    elif any(p in name_fr_l for p in ['mercure', 'vénus', 'terre', 'mars', 'jupiter', 'saturne', 'uranus', 'neptune', 'pluton']) \
         or any(p in name_en_l for p in ['mercury', 'venus', 'earth', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune', 'pluto']):
        cat_name = 'Planète'
    elif any(m in name_fr_l for m in ['lune', 'io', 'europe', 'ganymède', 'callisto', 'titan', 'encelade', 'triton']) \
         or 'moon' in type_l or 'satellite' in type_l:
        cat_name = 'Lune'
    elif name_fr == 'Soleil' or name_en == 'Sun' or 'star' in type_l:
        cat_name = 'Étoile'
    elif 'cluster' in type_l or 'amas' in name_fr_l:
        cat_name = 'Amas Globulaire'
    else:
        cat_name = 'Planète'

    cursor = conn.cursor()
    cursor.execute("SELECT id_categorie FROM CATEGORIE WHERE nom_categorie = ?", (cat_name,))
    cat_result = cursor.fetchone()
    fk_id_categorie: Optional[int] = cat_result[0] if cat_result else None
    
    if fk_id_categorie is None:
        conn.close()
        return False
        
    try:
        conn.execute(
            """
            INSERT OR REPLACE INTO OBJET_CELESTE 
            (fk_id_categorie, nom_fr, nom_scientifique, description, url_image, date_publication, distance_al) 
            VALUES (?, ?, ?, ?, ?, ?, ?);
            """,
            (fk_id_categorie, name_fr, name_en, description, image_url, 
             date.today().strftime("%Y-%m-%d"), None)
        )
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Database insertion error: {e}")
        return False
    finally:
        conn.close()

# ----------------------------------------------------
# 4. Feedback Functions (Survey)
# ----------------------------------------------------

def insert_survey_feedback(email: str, preference: str, object_id: Optional[int] = None) -> bool:
    """Inserts feedback from the user survey."""
    conn: sqlite3.Connection = get_db_connection()
    now: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        conn.execute(
            "INSERT INTO AVIS_SONDAGE (email, preference, date_sondage, fk_id_objet) VALUES (?, ?, ?, ?);",
            (email, preference, now, object_id)
        )
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error inserting survey feedback: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

# ----------------------------------------------------
# 5. Admin & Category Management
# ----------------------------------------------------

def get_all_categories() -> List[Dict[str, Any]]:
    """Retrieves all categories sorted alphabetically."""
    conn: sqlite3.Connection = get_db_connection()
    try:
        categories: List[sqlite3.Row] = conn.execute(
            "SELECT id_categorie, nom_categorie FROM CATEGORIE ORDER BY nom_categorie"
        ).fetchall()
        return [dict(cat) for cat in categories]
    except sqlite3.Error as e:
        print(f"Error reading categories: {e}")
        return []
    finally:
        conn.close()


def get_admin_by_pseudo(pseudo: str) -> Optional[Dict[str, Any]]:
    """Retrieves an admin record by their username."""
    conn: sqlite3.Connection = get_db_connection()
    query: str = "SELECT id_admin, pseudo, mot_de_passe_hash FROM ADMINISTRATEUR WHERE pseudo = ?"
    try:
        admin: Optional[sqlite3.Row] = conn.execute(query, (pseudo,)).fetchone()
        return dict(admin) if admin else None
    except sqlite3.Error as e:
        print(f"Error reading admin record: {e}")
        return None
    finally:
        conn.close()


def check_password(hashed_password: str, user_password: str) -> bool:
    """Verifies a plain-text password against a bcrypt hash."""
    return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password.encode('utf-8'))