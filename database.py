import sqlite3
import os
import bcrypt 
from config import DATABASE_PATH
from datetime import datetime

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
    description TEXT NOT NULL,
    distance_al REAL NOT NULL, -- REAL pour les nombres décimaux (Années-lumière)
    url_image TEXT NOT NULL, -- Chemin vers l'image
    date_publication TEXT NOT NULL, -- TEXT pour stocker la date au format ISO8601
    fk_id_categorie INTEGER NOT NULL,
    FOREIGN KEY (fk_id_categorie) REFERENCES CATEGORIE(id_categorie)
);

-- Table ADMINISTRATEUR
CREATE TABLE IF NOT EXISTS ADMINISTRATEUR (
    id_admin INTEGER PRIMARY KEY AUTOINCREMENT,
    pseudo TEXT NOT NULL UNIQUE,
    mot_de_passe_hash TEXT NOT NULL -- Stockage du mot de passe haché (Sécurité)
);

-- Table de jonction SAISIR (Relation N,N entre Admin et Objet Céleste)
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
# 2. Fonctions d'Initialisation
# ----------------------------------------------------

def get_db_connection():
    """Crée et retourne une connexion à la base de données."""
    conn = sqlite3.connect(DATABASE_PATH)
    # Permet d'accéder aux colonnes par nom (dictionnaire) au lieu d'index (tuple)
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
    # Le sel est généré automatiquement par gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def insert_initial_data():
    """Insère des données de test dans la base de données."""
    conn = get_db_connection()
    try:
        # --- 1. Insertion des Catégories ---
        categories = [
            ('Galaxie',),
            ('Nébuleuse',),
            ('Planète Externe',),
            ('Amas Globulaire',)
        ]
        conn.executemany("INSERT INTO CATEGORIE (nom_categorie) VALUES (?)", categories)
        
        # Récupération des IDs pour les FK
        cursor = conn.cursor()
        cursor.execute("SELECT id_categorie FROM CATEGORIE WHERE nom_categorie = 'Galaxie'")
        id_galaxie = cursor.fetchone()[0]
        cursor.execute("SELECT id_categorie FROM CATEGORIE WHERE nom_categorie = 'Nébuleuse'")
        id_nebuleuse = cursor.fetchone()[0]
        cursor.execute("SELECT id_categorie FROM CATEGORIE WHERE nom_categorie = 'Planète Externe'")
        id_planete = cursor.fetchone()[0]

        # --- 2. Insertion des Objets Célestes (READ F.01 & F.02) ---
        objets = [
            # Galaxie d'Andromède
            # Utilisation de guillemets doubles pour les descriptions contenant des apostrophes
            ('Galaxie d\'Andromède (M31)', "La galaxie la plus proche de la Voie Lactée, visible à l'œil nu dans de bonnes conditions. Elle est en approche et une collision est prévue dans des milliards d'années.", 2.537, 'img/andromede.jpg', datetime.now().strftime("%Y-%m-%d"), id_galaxie),
            # Nébuleuse d'Orion
            ('Nébuleuse d\'Orion (M42)', "Une pouponnière d'étoiles très célèbre et massive, située juste sous la ceinture d'Orion. Elle est essentielle pour l'étude de la formation stellaire.", 0.00134, 'img/orion.jpg', datetime.now().strftime("%Y-%m-%d"), id_nebuleuse),
            # Planète Externe Kepler-186f
            ('Kepler-186f', "La première planète de taille terrestre découverte orbitant dans la zone habitable d'une autre étoile. Elle est souvent citée comme une potentielle 'seconde Terre'.", 490.0, 'img/kepler186f.jpg', datetime.now().strftime("%Y-%m-%d"), id_planete),
        ]
        conn.executemany("""
            INSERT INTO OBJET_CELESTE (nom_fr, description, distance_al, url_image, date_publication, fk_id_categorie)
            VALUES (?, ?, ?, ?, ?, ?)
        """, objets)

        # --- 3. Insertion d'un Administrateur (F.05) ---
        hashed_pwd = hash_password("admin123")
        conn.execute("INSERT INTO ADMINISTRATEUR (pseudo, mot_de_passe_hash) VALUES (?, ?)", ('webmaster', hashed_pwd))

        # --- 4. Simulation de saisie (Table SAISIR) ---
        cursor.execute("SELECT id_admin FROM ADMINISTRATEUR WHERE pseudo = 'webmaster'")
        id_admin = cursor.fetchone()[0]
        
        # CORRECTION 3 : Utilisation d'une requête paramétrée pour la sélection de l'ID objet
        nom_objet_cherche = 'Galaxie d\'Andromède (M31)'
        cursor.execute("SELECT id_objet FROM OBJET_CELESTE WHERE nom_fr = ?", (nom_objet_cherche,))
        
        # Correction 3 : Suppression de la ligne en double (id_objet_andromede = cursor.fetchone()[0])
        id_objet_andromede = cursor.fetchone()[0]
        
        conn.execute("INSERT INTO SAISIR (fk_id_admin, fk_id_objet, date_saisie) VALUES (?, ?, ?)", 
                     (id_admin, id_objet_andromede, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        conn.commit()
        print("Données initiales insérées avec succès (Objets et Admin).")

    except sqlite3.IntegrityError as e:
        print(f"Les données existent déjà ou erreur d'intégrité : {e}. Saut de l'insertion des données.")
    except sqlite3.Error as e:
        print(f"Erreur lors de l'insertion des données: {e}")
        conn.rollback()
    finally:
        conn.close()

def initialize_database():
    """Initialise la base de données : crée les tables et insère les données."""
    if os.path.exists(DATABASE_PATH):
        print(f"Base de données '{DATABASE_PATH}' existe déjà. Skipping creation and data insertion.")
    else:
        print(f"Création de la base de données '{DATABASE_PATH}'...")
        create_tables()
        insert_initial_data()

# ----------------------------------------------------
# Fonctions de Modèle pour l'Application (MVC - Modèle)
# ----------------------------------------------------

def get_all_celestial_objects():
    """Récupère les 10 derniers objets célestes pour le catalogue (F.01)."""
    conn = get_db_connection()
    query = """
    SELECT 
        o.id_objet, o.nom_fr, SUBSTR(o.description, 1, 150) AS extrait_description, 
        o.url_image, o.date_publication, c.nom_categorie
    FROM OBJET_CELESTE o
    JOIN CATEGORIE c ON o.fk_id_categorie = c.id_categorie
    ORDER BY o.date_publication DESC  -- Tri par date de publication décroissante
    LIMIT 10;                         -- Limite le résultat aux 10 premiers (les plus récents)
    """
    try:
        objects = conn.execute(query).fetchall()
        return [dict(obj) for obj in objects]
    except sqlite3.Error as e:
        print(f"Erreur de lecture du catalogue: {e}")
        return []
    finally:
        conn.close()

def get_object_by_id(object_id):
    """Récupère les détails d'un objet céleste (F.02)."""
    conn = get_db_connection()
    query = """
    SELECT 
        o.id_objet, o.nom_fr, o.description, o.distance_al, 
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