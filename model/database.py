import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from config import DATABASE_URL

# ----------------------------------------------------
# 1. SQL — Modèle Physique de Données
# ----------------------------------------------------

CREATE_TABLES_SQL: str = """
CREATE TABLE IF NOT EXISTS CATEGORIE (
    id_categorie SERIAL PRIMARY KEY,
    nom_categorie TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS UTILISATEUR (
    id_utilisateur   SERIAL PRIMARY KEY,
    pseudo           TEXT NOT NULL UNIQUE,
    nom              TEXT NOT NULL,
    prenom           TEXT NOT NULL,
    email            TEXT NOT NULL UNIQUE,
    mot_de_passe_hash TEXT NOT NULL,
    genre            TEXT CHECK (genre IN ('homme', 'femme', 'autre', 'non_precise'))
                     DEFAULT 'non_precise',
    photo_profil     TEXT DEFAULT 'uploads/profils/default_avatar.png',
    date_inscription TIMESTAMP NOT NULL DEFAULT NOW(),
    est_actif        BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS OBJET_CELESTE (
    id_objet         SERIAL PRIMARY KEY,
    nom_fr           TEXT NOT NULL UNIQUE,
    nom_scientifique TEXT,
    description      TEXT NOT NULL,
    distance_al      REAL,
    url_image        TEXT,
    date_publication DATE NOT NULL,
    fk_id_categorie  INTEGER NOT NULL,
    fk_id_utilisateur INTEGER,
    CONSTRAINT fk_categorie
        FOREIGN KEY(fk_id_categorie)
        REFERENCES CATEGORIE(id_categorie) ON DELETE CASCADE,
    CONSTRAINT fk_auteur
        FOREIGN KEY(fk_id_utilisateur)
        REFERENCES UTILISATEUR(id_utilisateur) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS ADMINISTRATEUR (
    id_admin          SERIAL PRIMARY KEY,
    pseudo            TEXT NOT NULL UNIQUE,
    mot_de_passe_hash TEXT NOT NULL,
    nom               TEXT,
    prenom            TEXT,
    email             TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS PROPOSITION (
    id_proposition    SERIAL PRIMARY KEY,
    nom_fr            TEXT NOT NULL,
    nom_scientifique  TEXT,
    description       TEXT NOT NULL,
    url_image         TEXT,
    fk_id_categorie   INTEGER NOT NULL,
    fk_id_utilisateur INTEGER NOT NULL,
    statut            TEXT NOT NULL DEFAULT 'en_attente'
                      CHECK (statut IN ('en_attente', 'accepte', 'refuse', 'modifie')),
    commentaire_admin TEXT,
    date_proposition  TIMESTAMP NOT NULL DEFAULT NOW(),
    date_traitement   TIMESTAMP,
    notif_lue         BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (fk_id_categorie)   REFERENCES CATEGORIE(id_categorie),
    FOREIGN KEY (fk_id_utilisateur) REFERENCES UTILISATEUR(id_utilisateur) ON DELETE CASCADE
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
    id_avis      SERIAL PRIMARY KEY,
    email        TEXT NOT NULL,
    preference   TEXT NOT NULL,
    date_sondage TIMESTAMP NOT NULL,
    fk_id_objet  INTEGER,
    FOREIGN KEY (fk_id_objet) REFERENCES OBJET_CELESTE(id_objet)
);
"""

# Migration pour les BDD existantes
MIGRATE_SQL: str = """
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
        WHERE table_name='administrateur' AND column_name='nom') THEN
        ALTER TABLE ADMINISTRATEUR ADD COLUMN nom TEXT; END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
        WHERE table_name='administrateur' AND column_name='prenom') THEN
        ALTER TABLE ADMINISTRATEUR ADD COLUMN prenom TEXT; END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
        WHERE table_name='administrateur' AND column_name='email') THEN
        ALTER TABLE ADMINISTRATEUR ADD COLUMN email TEXT UNIQUE; END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
        WHERE table_name='objet_celeste' AND column_name='fk_id_utilisateur') THEN
        ALTER TABLE OBJET_CELESTE ADD COLUMN fk_id_utilisateur INTEGER
            REFERENCES UTILISATEUR(id_utilisateur) ON DELETE SET NULL; END IF;
END$$;
"""

# ----------------------------------------------------
# 2. Connexion & Sécurité
# ----------------------------------------------------

def get_db_connection():
    try:
        return psycopg2.connect(DATABASE_URL)
    except Exception as e:
        print(f"❌ Impossible de se connecter à PostgreSQL: {e}")
        return None

def create_tables() -> None:
    conn = get_db_connection()
    if not conn: return
    try:
        with conn.cursor() as cur:
            cur.execute(CREATE_TABLES_SQL)
            cur.execute(MIGRATE_SQL)
        conn.commit()
        print("✅ Tables créées avec succès.")
    except Exception as e:
        print(f"❌ Erreur création tables: {e}")
        conn.rollback()
    finally:
        conn.close()

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(hashed_password: str, user_password: str) -> bool:
    return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password.encode('utf-8'))

def insert_initial_data() -> None:
    conn = get_db_connection()
    if not conn: return
    try:
        categories = [
            ('Amas Globulaire',), ('Astéroïde',), ('Étoile',),
            ('Galaxie',), ('Lune',), ('Nébuleuse',),
            ('Planète',), ('Planète Externe',)
        ]
        with conn.cursor() as cur:
            cur.executemany(
                "INSERT INTO CATEGORIE (nom_categorie) VALUES (%s) ON CONFLICT DO NOTHING",
                categories
            )
            cur.execute(
                """INSERT INTO ADMINISTRATEUR (pseudo, mot_de_passe_hash, nom, prenom, email)
                   VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING""",
                ('webmaster', hash_password("admin123"), 'Admin', 'Super', 'admin@astrolearn.fr')
            )
        conn.commit()
        print("✅ Données initiales insérées.")
    except Exception as e:
        print(f"❌ Erreur insertion initiale: {e}")
        conn.rollback()
    finally:
        conn.close()

def initialize_database() -> None:
    print("🚀 Initialisation de la base de données...")
    create_tables()
    insert_initial_data()

# ----------------------------------------------------
# 3. CRUD Objets Célestes
# ----------------------------------------------------

def get_all_celestial_objects() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    if not conn: return []
    query = """
    SELECT o.id_objet, o.nom_fr, o.nom_scientifique,
           LEFT(o.description, 150) AS extrait_description,
           o.url_image, o.date_publication, c.nom_categorie,
           u.pseudo AS auteur_pseudo
    FROM OBJET_CELESTE o
    JOIN CATEGORIE c ON o.fk_id_categorie = c.id_categorie
    LEFT JOIN UTILISATEUR u ON o.fk_id_utilisateur = u.id_utilisateur
    ORDER BY o.date_publication DESC;
    """
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query)
            return cur.fetchall()
    except Exception as e:
        print(f"Erreur catalogue: {e}")
        return []
    finally:
        conn.close()

def get_object_by_id(object_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    if not conn: return None
    query = """
    SELECT o.id_objet, o.nom_fr, o.nom_scientifique, o.description, o.distance_al,
           o.url_image, o.date_publication, c.nom_categorie,
           u.pseudo AS auteur_pseudo, u.photo_profil AS auteur_photo
    FROM OBJET_CELESTE o
    JOIN CATEGORIE c ON o.fk_id_categorie = c.id_categorie
    LEFT JOIN UTILISATEUR u ON o.fk_id_utilisateur = u.id_utilisateur
    WHERE o.id_objet = %s
    """
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (object_id,))
            return cur.fetchone()
    except Exception as e:
        print(f"Erreur détails objet: {e}")
        return None
    finally:
        conn.close()

def search_celestial_objects(search_term: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    if not conn: return []
    p = f'%{search_term.lower()}%'
    query = """
    SELECT o.id_objet, o.nom_fr, o.nom_scientifique,
           LEFT(o.description, 150) AS extrait_description,
           o.url_image, o.date_publication, c.nom_categorie,
           u.pseudo AS auteur_pseudo
    FROM OBJET_CELESTE o
    JOIN CATEGORIE c ON o.fk_id_categorie = c.id_categorie
    LEFT JOIN UTILISATEUR u ON o.fk_id_utilisateur = u.id_utilisateur
    WHERE LOWER(o.nom_fr) LIKE %s OR LOWER(o.nom_scientifique) LIKE %s
       OR LOWER(o.description) LIKE %s
    ORDER BY o.date_publication DESC;
    """
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (p, p, p))
            return cur.fetchall()
    except Exception as e:
        print(f"Erreur recherche: {e}")
        return []
    finally:
        conn.close()

def get_all_categories() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    if not conn: return []
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id_categorie, nom_categorie FROM CATEGORIE ORDER BY nom_categorie")
            return cur.fetchall()
    except Exception as e:
        print(f"Erreur catégories: {e}")
        return []
    finally:
        conn.close()

def get_objects_by_category(category_id: int) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    if not conn: return []
    query = """
    SELECT o.id_objet, o.nom_fr, o.nom_scientifique,
           LEFT(o.description, 150) AS extrait_description,
           o.url_image, o.date_publication, c.nom_categorie,
           o.fk_id_categorie as id_categorie, u.pseudo AS auteur_pseudo
    FROM OBJET_CELESTE o
    JOIN CATEGORIE c ON o.fk_id_categorie = c.id_categorie
    LEFT JOIN UTILISATEUR u ON o.fk_id_utilisateur = u.id_utilisateur
    WHERE o.fk_id_categorie = %s ORDER BY o.nom_fr ASC;
    """
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (category_id,))
            return cur.fetchall()
    except Exception as e:
        print(f"❌ Erreur catégorie : {e}")
        return []
    finally:
        conn.close()

def insert_solar_system_body(name_fr, name_en, description, body_type,
                              mass_value=None, density=None, image_url=None) -> bool:
    conn = get_db_connection()
    if not conn: return False
    mapping = {
        'Planet': 'Planète', 'Moon': 'Lune', 'Star': 'Étoile',
        'Asteroid': 'Astéroïde', 'Dwarf Planet': 'Planète Externe',
        'Comet': 'Astéroïde', 'Nebula': 'Nébuleuse'
    }
    translated_type = mapping.get(body_type, body_type)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id_categorie FROM CATEGORIE WHERE nom_categorie ILIKE %s LIMIT 1",
                        (f"%{translated_type}%",))
            row = cur.fetchone()
            category_id = row[0] if row else 1
            cur.execute("""
                INSERT INTO OBJET_CELESTE (nom_fr, nom_scientifique, description, url_image,
                    date_publication, fk_id_categorie)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (nom_fr) DO UPDATE SET
                    fk_id_categorie = EXCLUDED.fk_id_categorie,
                    description = EXCLUDED.description;
            """, (name_fr, name_en, description, image_url, date.today(), category_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Erreur insertion {name_fr} : {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

# ----------------------------------------------------
# 4. CRUD Administrateurs
# ----------------------------------------------------

def get_admin_by_pseudo(identifiant: str) -> Optional[Dict[str, Any]]:
    """Récupère un admin par pseudo OU email."""
    conn = get_db_connection()
    if not conn: return None
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """SELECT id_admin, pseudo, mot_de_passe_hash, nom, prenom, email
                   FROM ADMINISTRATEUR WHERE pseudo = %s OR email = %s""",
                (identifiant, identifiant)
            )
            return cur.fetchone()
    except Exception as e:
        print(f"Erreur admin: {e}")
        return None
    finally:
        conn.close()

# ----------------------------------------------------
# 5. CRUD Utilisateurs
# ----------------------------------------------------

def create_utilisateur(pseudo: str, nom: str, prenom: str, email: str,
                        password: str, genre: str, photo_profil: str) -> bool:
    conn = get_db_connection()
    if not conn: return False
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO UTILISATEUR (pseudo, nom, prenom, email, mot_de_passe_hash, genre, photo_profil)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (pseudo, nom, prenom, email, hash_password(password), genre, photo_profil)
            )
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Erreur création utilisateur : {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def get_utilisateur_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    if not conn: return None
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """SELECT id_utilisateur, pseudo, nom, prenom, email, genre,
                          photo_profil, date_inscription, est_actif
                   FROM UTILISATEUR WHERE id_utilisateur = %s""",
                (user_id,)
            )
            return cur.fetchone()
    except Exception as e:
        print(f"Erreur utilisateur: {e}")
        return None
    finally:
        conn.close()

def get_utilisateur_by_identifiant(identifiant: str) -> Optional[Dict[str, Any]]:
    """Récupère un utilisateur par pseudo OU email."""
    conn = get_db_connection()
    if not conn: return None
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """SELECT id_utilisateur, pseudo, nom, prenom, email,
                          mot_de_passe_hash, genre, photo_profil, est_actif
                   FROM UTILISATEUR WHERE pseudo = %s OR email = %s""",
                (identifiant, identifiant)
            )
            return cur.fetchone()
    except Exception as e:
        print(f"Erreur utilisateur: {e}")
        return None
    finally:
        conn.close()

def update_utilisateur_profil(user_id: int, nom: str, prenom: str, email: str,
                               genre: str, photo_profil: Optional[str] = None) -> bool:
    conn = get_db_connection()
    if not conn: return False
    try:
        with conn.cursor() as cur:
            if photo_profil:
                cur.execute(
                    """UPDATE UTILISATEUR SET nom=%s, prenom=%s, email=%s, genre=%s, photo_profil=%s
                       WHERE id_utilisateur=%s""",
                    (nom, prenom, email, genre, photo_profil, user_id)
                )
            else:
                cur.execute(
                    "UPDATE UTILISATEUR SET nom=%s, prenom=%s, email=%s, genre=%s WHERE id_utilisateur=%s",
                    (nom, prenom, email, genre, user_id)
                )
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Erreur update profil : {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def update_utilisateur_password(user_id: int, new_password: str) -> bool:
    conn = get_db_connection()
    if not conn: return False
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE UTILISATEUR SET mot_de_passe_hash=%s WHERE id_utilisateur=%s",
                (hash_password(new_password), user_id)
            )
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Erreur update password : {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def get_all_utilisateurs() -> List[Dict[str, Any]]:
    """Pour le dashboard admin."""
    conn = get_db_connection()
    if not conn: return []
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT u.id_utilisateur, u.pseudo, u.nom, u.prenom, u.email,
                       u.genre, u.photo_profil, u.date_inscription, u.est_actif,
                       COUNT(p.id_proposition) AS nb_propositions
                FROM UTILISATEUR u
                LEFT JOIN PROPOSITION p ON p.fk_id_utilisateur = u.id_utilisateur
                GROUP BY u.id_utilisateur
                ORDER BY u.date_inscription DESC
            """)
            return cur.fetchall()
    except Exception as e:
        print(f"Erreur liste utilisateurs: {e}")
        return []
    finally:
        conn.close()

# ----------------------------------------------------
# 6. CRUD Propositions
# ----------------------------------------------------

def create_proposition(nom_fr: str, nom_scientifique: str, description: str,
                        url_image: Optional[str], id_categorie: int,
                        id_utilisateur: int) -> bool:
    conn = get_db_connection()
    if not conn: return False
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO PROPOSITION
                   (nom_fr, nom_scientifique, description, url_image, fk_id_categorie, fk_id_utilisateur)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (nom_fr, nom_scientifique, description, url_image, id_categorie, id_utilisateur)
            )
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Erreur création proposition : {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def get_all_propositions() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    if not conn: return []
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT p.*, c.nom_categorie,
                       u.pseudo, u.prenom, u.nom AS nom_user, u.photo_profil
                FROM PROPOSITION p
                JOIN CATEGORIE c ON p.fk_id_categorie = c.id_categorie
                JOIN UTILISATEUR u ON p.fk_id_utilisateur = u.id_utilisateur
                ORDER BY
                    CASE p.statut WHEN 'en_attente' THEN 0 ELSE 1 END,
                    p.date_proposition DESC
            """)
            return cur.fetchall()
    except Exception as e:
        print(f"Erreur propositions: {e}")
        return []
    finally:
        conn.close()

def get_propositions_by_user(user_id: int) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    if not conn: return []
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT p.*, c.nom_categorie
                FROM PROPOSITION p
                JOIN CATEGORIE c ON p.fk_id_categorie = c.id_categorie
                WHERE p.fk_id_utilisateur = %s
                ORDER BY p.date_proposition DESC
            """, (user_id,))
            return cur.fetchall()
    except Exception as e:
        print(f"Erreur propositions user: {e}")
        return []
    finally:
        conn.close()

def traiter_proposition(id_proposition: int, statut: str, commentaire: str,
                         nom_fr: str = None, nom_scientifique: str = None,
                         description: str = None, id_categorie: int = None) -> bool:
    conn = get_db_connection()
    if not conn: return False
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                UPDATE PROPOSITION SET statut=%s, commentaire_admin=%s,
                date_traitement=NOW(), notif_lue=FALSE
                WHERE id_proposition=%s
                RETURNING *
            """, (statut, commentaire, id_proposition))
            prop = cur.fetchone()

            if statut in ('accepte', 'modifie'):
                cur.execute("""
                    INSERT INTO OBJET_CELESTE
                    (nom_fr, nom_scientifique, description, url_image,
                     date_publication, fk_id_categorie, fk_id_utilisateur)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (nom_fr) DO NOTHING
                """, (
                    nom_fr or prop['nom_fr'],
                    nom_scientifique or prop['nom_scientifique'],
                    description or prop['description'],
                    prop['url_image'],
                    date.today(),
                    id_categorie or prop['fk_id_categorie'],
                    prop['fk_id_utilisateur']
                ))
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Erreur traitement proposition : {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def count_notifs_non_lues(user_id: int) -> int:
    conn = get_db_connection()
    if not conn: return 0
    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT COUNT(*) FROM PROPOSITION
                   WHERE fk_id_utilisateur=%s AND notif_lue=FALSE AND statut != 'en_attente'""",
                (user_id,)
            )
            return cur.fetchone()[0]
    except:
        return 0
    finally:
        conn.close()

def marquer_notifs_lues(user_id: int) -> None:
    conn = get_db_connection()
    if not conn: return
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE PROPOSITION SET notif_lue=TRUE WHERE fk_id_utilisateur=%s AND notif_lue=FALSE",
                (user_id,)
            )
        conn.commit()
    except Exception as e:
        print(f"Erreur notifs: {e}")
    finally:
        conn.close()