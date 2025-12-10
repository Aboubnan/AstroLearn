import sqlite3
import os
import bcrypt 
from config import DATABASE_PATH
from datetime import datetime, date 

# ----------------------------------------------------
# 1. Requêtes SQL pour le Modèle Physique de Données (MPD)
# ----------------------------------------------------

# MPD - Création des tables
CREATE_TABLES_SQL = """
-- Activation des Clés Étrangères (Obligatoire pour SQLite)
PRAGMA foreign_keys = ON;

-- Table CATEGORIE
CREATE TABLE IF NOT EXISTS CATEGORIE (
    id_categorie INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_categorie TEXT NOT NULL UNIQUE
);

-- Table OBJET_CELESTE
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

-- Table ADMINISTRATEUR
CREATE TABLE IF NOT EXISTS ADMINISTRATEUR (
    id_admin INTEGER PRIMARY KEY AUTOINCREMENT,
    pseudo TEXT NOT NULL UNIQUE,
    mot_de_passe_hash TEXT NOT NULL
);

-- Table de jonction SAISIR
CREATE TABLE IF NOT EXISTS SAISIR (
    fk_id_admin INTEGER NOT NULL,
    fk_id_objet INTEGER NOT NULL,
    date_saisie TEXT NOT NULL,
    PRIMARY KEY (fk_id_admin, fk_id_objet),
    FOREIGN KEY (fk_id_admin) REFERENCES ADMINISTRATEUR(id_admin),
    FOREIGN KEY (fk_id_objet) REFERENCES OBJET_CELESTE(id_objet)
);

-- Table AVIS_SONDAGE
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

# --- CONSERVATION DE LA LOGIQUE D'INSERTION DES CATÉGORIES ET DE L'ADMIN ---
def insert_initial_data():
    """Insère les catégories de base et l'administrateur initial."""
    conn = get_db_connection()
    try:
        # --- 1. Insertion des Catégories (Nécessaire pour l'ingestion API) ---
        categories = [
            ('Galaxie',),
            ('Nébuleuse',),
            ('Planète Externe',),
            ('Planète',),     
            ('Lune',),         
            ('Astéroïde',), 
            ('Amas Globulaire',)
        ]
        # Utilisation d'INSERT OR IGNORE pour éviter les erreurs si les catégories existent déjà
        conn.executemany("INSERT OR IGNORE INTO CATEGORIE (nom_categorie) VALUES (?)", categories)
        
        # --- 2. Insertion d'un Administrateur (Nécessaire pour l'accès Admin) ---
        hashed_pwd = hash_password("admin123")
        # Utilisation d'INSERT OR IGNORE pour éviter les doublons
        conn.execute("INSERT OR IGNORE INTO ADMINISTRATEUR (pseudo, mot_de_passe_hash) VALUES (?, ?)", ('webmaster', hashed_pwd))

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
    # Si la DB existe, on ne la réinitialise pas pour conserver les données API
    if os.path.exists(DATABASE_PATH):
        print(f"Base de données '{DATABASE_PATH}' existe déjà. Skipping creation and data insertion.")
    else:
        print(f"Création de la base de données '{DATABASE_PATH}'...")
        create_tables()
        # Appel de la fonction mise à jour qui n'insère QUE les catégories et l'admin
        insert_initial_data() 

# ----------------------------------------------------
# Fonctions de Modèle pour l'Application (CRUD & Recherche)
# ----------------------------------------------------

def get_all_celestial_objects():
    """Récupère TOUS les objets célestes pour le catalogue (F.01), ordonnés par date."""
    conn = get_db_connection()
    query = """
    SELECT 
        o.id_objet, o.nom_fr, o.nom_scientifique, SUBSTR(o.description, 1, 150) AS extrait_description, 
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
    """Récupère les objets célestes filtrés par l'ID de catégorie."""
    conn = get_db_connection()
    try:
        query = """
        SELECT 
            o.id_objet, o.nom_fr, o.nom_scientifique, SUBSTR(o.description, 1, 150) AS extrait_description, 
            o.url_image, o.date_publication, c.nom_categorie
        FROM OBJET_CELESTE o
        JOIN CATEGORIE c ON o.fk_id_categorie = c.id_categorie
        WHERE o.fk_id_categorie = ?
        ORDER BY o.date_publication DESC;
        """
        objects = conn.execute(query, (category_id,)).fetchall()
        return [dict(obj) for obj in objects]
    except sqlite3.Error as e:
        print(f"Erreur de filtrage du catalogue: {e}")
        return []
    finally:
        conn.close()


def get_object_by_id(object_id):
    """Récupère les détails d'un objet céleste (F.02)."""
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
    """Recherche des objets célestes par nom français, nom scientifique ou description."""
    conn = get_db_connection()
    search_pattern = f'%{search_term}%'
    
    query = """
    SELECT 
        o.id_objet, o.nom_fr, o.nom_scientifique, SUBSTR(o.description, 1, 150) AS extrait_description, 
        o.url_image, o.date_publication, c.nom_categorie
    FROM OBJET_CELESTE o
    JOIN CATEGORIE c ON o.fk_id_categorie = c.id_categorie
    WHERE 
        o.nom_fr LIKE ? OR 
        o.nom_scientifique LIKE ? OR 
        o.description LIKE ?
    ORDER BY o.date_publication DESC;
    """
    try:
        objects = conn.execute(query, (search_pattern, search_pattern, search_pattern)).fetchall()
        return [dict(obj) for obj in objects]
    except sqlite3.Error as e:
        print(f"Erreur de recherche du catalogue: {e}")
        return []
    finally:
        conn.close()


def insert_solar_system_body(name_fr, name_en, description, body_type, mass_value, density, image_url):
    """
    Insère un corps céleste du Système Solaire dans la table OBJET_CELESTE, 
    incluant l'URL de l'image externe et une classification de catégorie basée sur le body_type.
    """
    conn = get_db_connection()
    
    # Détermination de la catégorie basée sur le type de corps (mapping simple)
    body_type_lower = body_type.lower()
    
    if 'planet' in body_type_lower or name_fr in ['Soleil', 'Mercure', 'Vénus', 'Terre', 'Mars', 'Jupiter', 'Saturne', 'Uranus', 'Neptune', 'Pluton']:
        cat_name = 'Planète'
    elif 'moon' in body_type_lower or 'satellite' in body_type_lower or name_fr in ['Lune', 'Io', 'Europe', 'Ganymède', 'Callisto', 'Titan', 'Encelade', 'Triton', 'Phobos', 'Deimos']:
        cat_name = 'Lune'
    elif 'star' in body_type_lower or name_fr == 'Soleil':
        # Le Soleil sera mis dans Planète (système solaire) pour simplifier le catalogue
        cat_name = 'Planète' 
    elif 'asteroid' in body_type_lower or 'comet' in body_type_lower or name_fr in ['Vesta', 'Cérès']:
        cat_name = 'Astéroïde'
    else:
        cat_name = 'Planète' 

    # Récupération de l'ID de catégorie
    cursor = conn.cursor()
    cursor.execute("SELECT id_categorie FROM CATEGORIE WHERE nom_categorie = ?", (cat_name,))
    cat_result = cursor.fetchone()
    fk_id_categorie = cat_result[0] if cat_result else None
    
    if fk_id_categorie is None:
        print(f"Alerte: Catégorie '{cat_name}' non trouvée. Insertion annulée.")
        return False
        
    # Tente d'insérer l'objet
    try:
        # INSERT OR REPLACE permet de mettre à jour si l'objet existe déjà (basé sur la clé nom_fr)
        conn.execute(
            """
            INSERT OR REPLACE INTO OBJET_CELESTE 
            (fk_id_categorie, nom_fr, nom_scientifique, description, url_image, date_publication, distance_al) 
            VALUES (?, ?, ?, ?, ?, ?, ?);
            """,
            (fk_id_categorie, name_fr, name_en, description, image_url, date.today().strftime("%Y-%m-%d"), None)
        )
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erreur d'insertion/remplacement du corps céleste {name_fr}: {e}")
        return False
    finally:
        conn.close()


# ----------------------------------------------------
# Fonctions de Modèle pour AVIS_SONDAGE (F.03)
# ----------------------------------------------------

def insert_survey_feedback(email, preference, objet_id=None):
    """
    Insère un avis (sondage) dans la table AVIS_SONDAGE.
    :param email: L'adresse email de l'utilisateur.
    :param preference: La préférence sélectionnée par l'utilisateur.
    :param objet_id: L'ID de l'objet céleste lié à l'avis (peut être None).
    :return: True si l'insertion réussit, False sinon.
    """
    conn = get_db_connection()
    date_sondage = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        conn.execute(
            """
            INSERT INTO AVIS_SONDAGE (email, preference, date_sondage, fk_id_objet) 
            VALUES (?, ?, ?, ?);
            """,
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
    """Récupère tous les avis de sondage liés à un objet céleste spécifique."""
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
# Fonctions Admin & Catégories
# ----------------------------------------------------

def get_all_categories():
    """Récupère toutes les catégories."""
    conn = get_db_connection()
    try:
        categories = conn.execute("SELECT id_categorie, nom_categorie FROM CATEGORIE").fetchall()
        return [dict(cat) for cat in categories]
    except sqlite3.Error as e:
        print(f"Erreur de lecture des catégories: {e}")
        return []
    finally:
        conn.close()

def get_admin_by_pseudo(pseudo):
    """Récupère l'administrateur par pseudo et mot de passe hashé."""
    conn = get_db_connection()
    query = "SELECT id_admin, pseudo, mot_de_passe_hash FROM ADMINISTRATEUR WHERE pseudo = ?"
    try:
        admin = conn.execute(query, (pseudo,)).fetchone()
        return dict(admin) if admin else None
    except sqlite3.Error as e:
        print(f"Erreur de lecture de l'administrateur: {e}")
        return None
    finally:
        conn.close()
        

def check_password(hashed_password, user_password):
    """Vérifie le mot de passe utilisateur avec le hash stocké."""
    return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password.encode('utf-8'))