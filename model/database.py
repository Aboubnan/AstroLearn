# model/database.py

import sqlite3
import os
import bcrypt 
from config import DATABASE_PATH
from datetime import datetime, date 

# ----------------------------------------------------
# 1. Requêtes SQL pour le Modèle Physique de Données (MPD)
# ----------------------------------------------------

CREATE_TABLES_SQL = """
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
# 2. Fonctions d'Initialisation et Sécurité
# ----------------------------------------------------

def get_db_connection():
    """Crée et retourne une connexion à la base de données."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    """Crée toutes les tables définies dans le MPD."""
    conn = get_db_connection()
    try:
        conn.executescript(CREATE_TABLES_SQL)
        print("Tables créées avec succès.")
    except sqlite3.Error as e:
        print(f"Erreur lors de la création des tables: {e}")
    finally:
        conn.close()


def hash_password(password):
    """Hache un mot de passe en utilisant bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def insert_initial_data():
    """Insère les catégories de base et l'administrateur initial."""
    conn = get_db_connection()
    try:
        categories = [
            ('Amas Globulaire',),
            ('Astéroïde',),
            ('Étoile',),
            ('Galaxie',),
            ('Lune',),
            ('Nébuleuse',),
            ('Planète',),
            ('Planète Externe',)
        ]
        conn.executemany("INSERT OR IGNORE INTO CATEGORIE (nom_categorie) VALUES (?)", categories)
        
        hashed_pwd = hash_password("admin123")
        conn.execute("INSERT OR IGNORE INTO ADMINISTRATEUR (pseudo, mot_de_passe_hash) VALUES (?, ?)", 
                    ('webmaster', hashed_pwd))

        conn.commit()
        print("Catégories et Administrateur initial insérés avec succès.")

    except sqlite3.IntegrityError as e:
        print(f"Les données existent déjà ou erreur d'intégrité : {e}.")
    except sqlite3.Error as e:
        print(f"Erreur lors de l'insertion des données initiales: {e}")
        conn.rollback()
    finally:
        conn.close()


def initialize_database():
    """Initialise la base de données : crée les tables et insère les données."""
    if os.path.exists(DATABASE_PATH):
        print(f"Base de données '{DATABASE_PATH}' existe déjà.")
        # Ajouter la catégorie Étoile si elle n'existe pas
        conn = get_db_connection()
        try:
            conn.execute("INSERT OR IGNORE INTO CATEGORIE (nom_categorie) VALUES (?)", ('Étoile',))
            conn.commit()
        except:
            pass
        finally:
            conn.close()
    else:
        print(f"Création de la base de données '{DATABASE_PATH}'...")
        create_tables()
        insert_initial_data()

# ----------------------------------------------------
# 3. Fonctions CRUD pour l'Application
# ----------------------------------------------------

def get_all_celestial_objects():
    """Récupère tous les objets célestes, ordonnés par date."""
    conn = get_db_connection()
    query = """
    SELECT 
        o.id_objet, o.nom_fr, o.nom_scientifique, 
        SUBSTR(o.description, 1, 150) AS extrait_description, 
        o.url_image, o.date_publication, c.nom_categorie
    FROM OBJET_CELESTE o
    JOIN CATEGORIE c ON o.fk_id_categorie = c.id_categorie
    ORDER BY o.date_publication DESC;
    """
    try:
        objects = conn.execute(query).fetchall()
        return [dict(obj) for obj in objects]
    except sqlite3.Error as e:
        print(f"Erreur de lecture du catalogue: {e}")
        return []
    finally:
        conn.close()


def filter_celestial_objects(category_id):
    """Récupère les objets filtrés par catégorie."""
    conn = get_db_connection()
    try:
        query = """
        SELECT 
            o.id_objet, o.nom_fr, o.nom_scientifique, 
            SUBSTR(o.description, 1, 150) AS extrait_description, 
            o.url_image, o.date_publication, c.nom_categorie
        FROM OBJET_CELESTE o
        JOIN CATEGORIE c ON o.fk_id_categorie = c.id_categorie
        WHERE o.fk_id_categorie = ?
        ORDER BY o.date_publication DESC;
        """
        objects = conn.execute(query, (category_id,)).fetchall()
        return [dict(obj) for obj in objects]
    except sqlite3.Error as e:
        print(f"Erreur de filtrage: {e}")
        return []
    finally:
        conn.close()


def get_object_by_id(object_id):
    """Récupère les détails d'un objet céleste."""
    conn = get_db_connection()
    query = """
    SELECT 
        o.id_objet, o.nom_fr, o.nom_scientifique, o.description, o.distance_al, 
        o.url_image, o.date_publication, c.nom_categorie
    FROM OBJET_CELESTE o
    JOIN CATEGORIE c ON o.fk_id_categorie = c.id_categorie
    WHERE o.id_objet = ?
    """
    try:
        obj = conn.execute(query, (object_id,)).fetchone()
        return dict(obj) if obj else None
    except sqlite3.Error as e:
        print(f"Erreur de lecture de l'objet: {e}")
        return None
    finally:
        conn.close()


def search_celestial_objects(search_term):
    """Recherche des objets (insensible à la casse)."""
    conn = get_db_connection()
    search_pattern = f'%{search_term.lower()}%'
    
    query = """
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
        objects = conn.execute(query, (search_pattern, search_pattern, search_pattern)).fetchall()
        return [dict(obj) for obj in objects]
    except sqlite3.Error as e:
        print(f"Erreur de recherche: {e}")
        return []
    finally:
        conn.close()


def insert_solar_system_body(name_fr, name_en, description, body_type, mass_value, density, image_url):
    """Insère un corps céleste avec catégorisation intelligente."""
    conn = get_db_connection()
    
    name_fr_lower = name_fr.lower()
    name_en_lower = (name_en or '').lower()
    body_type_lower = body_type.lower()
    
    # Détermination de la catégorie
    if 'asteroid' in name_fr_lower or 'comet' in name_fr_lower or 'asteroid' in body_type_lower or 'comet' in body_type_lower:
        cat_name = 'Astéroïde'
    elif 'galaxy' in name_fr_lower or 'galaxy' in body_type_lower or 'galaxie' in name_fr_lower:
        cat_name = 'Galaxie'
    elif 'nebula' in name_fr_lower or 'nebula' in body_type_lower or 'nébuleuse' in name_fr_lower:
        cat_name = 'Nébuleuse'
    elif any(planet in name_fr_lower for planet in ['mercure', 'vénus', 'terre', 'mars', 'jupiter', 'saturne', 'uranus', 'neptune', 'pluton']) \
         or any(planet in name_en_lower for planet in ['mercury', 'venus', 'earth', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune', 'pluto']):
        cat_name = 'Planète'
    elif any(moon in name_fr_lower for moon in ['lune', 'io', 'europe', 'ganymède', 'callisto', 'titan', 'encelade', 'triton', 'phobos', 'deimos']) \
         or 'moon' in body_type_lower or 'satellite' in body_type_lower:
        cat_name = 'Lune'
    elif name_fr == 'Soleil' or name_en == 'Sun' or 'star' in body_type_lower:
        cat_name = 'Étoile'
    elif 'cluster' in body_type_lower or 'amas' in name_fr_lower:
        cat_name = 'Amas Globulaire'
    elif 'solar system' in name_fr_lower:
        cat_name = 'Planète Externe'
    else:
        cat_name = 'Planète'

    cursor = conn.cursor()
    cursor.execute("SELECT id_categorie FROM CATEGORIE WHERE nom_categorie = ?", (cat_name,))
    cat_result = cursor.fetchone()
    fk_id_categorie = cat_result[0] if cat_result else None
    
    if fk_id_categorie is None:
        print(f"⚠️ Catégorie '{cat_name}' non trouvée pour {name_fr}")
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
        print(f"❌ Erreur d'insertion de {name_fr}: {e}")
        return False
    finally:
        conn.close()


# ----------------------------------------------------
# 4. Fonctions Sondage
# ----------------------------------------------------

def insert_survey_feedback(email, preference, objet_id=None):
    """Insère un avis de sondage."""
    conn = get_db_connection()
    date_sondage = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        conn.execute(
            "INSERT INTO AVIS_SONDAGE (email, preference, date_sondage, fk_id_objet) VALUES (?, ?, ?, ?);",
            (email, preference, date_sondage, objet_id)
        )
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erreur lors de l'insertion de l'avis: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def get_feedback_by_object(object_id):
    """Récupère les avis liés à un objet."""
    conn = get_db_connection()
    query = """
    SELECT email, preference, date_sondage 
    FROM AVIS_SONDAGE 
    WHERE fk_id_objet = ?
    ORDER BY date_sondage DESC;
    """
    try:
        feedback = conn.execute(query, (object_id,)).fetchall()
        return [dict(f) for f in feedback]
    except sqlite3.Error as e:
        print(f"Erreur de lecture des avis: {e}")
        return []
    finally:
        conn.close()


# ----------------------------------------------------
# 5. Fonctions Admin & Catégories
# ----------------------------------------------------

def get_all_categories():
    """Récupère toutes les catégories triées."""
    conn = get_db_connection()
    try:
        categories = conn.execute(
            "SELECT id_categorie, nom_categorie FROM CATEGORIE ORDER BY nom_categorie"
        ).fetchall()
        return [dict(cat) for cat in categories]
    except sqlite3.Error as e:
        print(f"Erreur de lecture des catégories: {e}")
        return []
    finally:
        conn.close()


def get_admin_by_pseudo(pseudo):
    """Récupère un admin par pseudo."""
    conn = get_db_connection()
    query = "SELECT id_admin, pseudo, mot_de_passe_hash FROM ADMINISTRATEUR WHERE pseudo = ?"
    try:
        admin = conn.execute(query, (pseudo,)).fetchone()
        return dict(admin) if admin else None
    except sqlite3.Error as e:
        print(f"Erreur de lecture admin: {e}")
        return None
    finally:
        conn.close()


def check_password(hashed_password, user_password):
    """Vérifie le mot de passe avec bcrypt."""
    return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password.encode('utf-8'))