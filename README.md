# AstroLearn

Application web éducative sur l'astronomie : catalogue d'objets célestes, système solaire 3D
interactif, assistant conversationnel AstroIA, comptes utilisateurs et espace d'administration.

Démo en ligne : https://astrolearn.nayaweb.fr

## Stack technique

- **Backend** : Python 3.12, Flask (organisé en blueprints), PostgreSQL (psycopg2)
- **NoSQL** : MongoDB (pymongo) pour les fils de commentaires imbriqués
- **Frontend** : Jinja2, Tailwind CSS, Three.js (système solaire 3D), JavaScript vanilla
- **Sécurité** : bcrypt (hachage des mots de passe), Flask-WTF (protection CSRF)
- **IA** : API Gemini 2.5 Flash (chatbot AstroIA)
- **Tests** : pytest
- **CI** : GitHub Actions (flake8, black, pytest)
- **Déploiement** : Gunicorn + nginx + systemd (VPS), ou Docker

## Architecture

```
controller/   Routes Flask, organisées en blueprints (main, auth, user, admin, chatbot, skymap, comment)
model/        Accès aux données (PostgreSQL + MongoDB) et services métier
              (ex: chatbot_service.py, comment_service.py)
templates/    Vues Jinja2
static/       CSS, JS, images, uploads utilisateurs
tests/        Tests pytest (unitaires et d'intégration)
```

## Installation locale (sans Docker)

Prérequis : Python 3.12+, PostgreSQL en local, MongoDB en local (pour les commentaires).

```bash
python -m venv venv
source venv/bin/activate  # venv\Scripts\activate sous Windows
pip install -r requirements.txt

cp .env.example .env
# éditer .env : DB_PASSWORD, SECRET_KEY, GEMINI_API_KEY au minimum

python app.py
```

L'application est alors disponible sur http://127.0.0.1:5000.

## Installation avec Docker

Prérequis : Docker et Docker Compose.

```bash
cp .env.example .env
# éditer .env : DB_PASSWORD, SECRET_KEY, GEMINI_API_KEY au minimum

docker compose up --build
```

Le service `web` (Flask + Gunicorn) démarre sur http://localhost:5000. Le service `db`
(PostgreSQL 16) est exposé sur le port hôte 5433, et le service `mongo` (MongoDB 7) sur le
port hôte 27018, pour éviter tout conflit avec des instances locales déjà installées. Le
schéma PostgreSQL est créé automatiquement au premier démarrage.

## Variables d'environnement

Voir `.env.example` pour la liste complète. Les indispensables :

| Variable | Description |
|---|---|
| `DB_PASSWORD` | Mot de passe PostgreSQL |
| `SECRET_KEY` | Clé de signature des sessions Flask (`python -c "import secrets; print(secrets.token_hex(32))"`) |
| `GEMINI_API_KEY` | Clé API Google Gemini, pour le chatbot AstroIA |

`MONGO_URI` est optionnelle (par défaut `mongodb://localhost:27017`, ou `mongodb://mongo:27017`
avec Docker via `docker-compose.yml`).

`ADMIN_PSEUDO` / `ADMIN_PASSWORD` / `ADMIN_EMAIL` sont optionnelles : si toutes les trois sont
renseignées, un compte administrateur est créé automatiquement au premier démarrage.

## Base de données

Le schéma (tables, contraintes, migrations) est créé et mis à jour automatiquement au
démarrage de l'application (`initialize_database()`).

### Jeu d'essai

Pour peupler une base de **test** avec un jeu de données représentatif (objets célestes,
utilisateurs, une proposition, des favoris) :

```bash
python seed_jeu_essai.py
```

À utiliser uniquement sur une base de test/dev, jamais sur la base de production.

### Sauvegarde et restauration

```bash
# Sauvegarde
pg_dump -U $DB_USER -h $DB_HOST -d $DB_NAME -F c -f astrolearn_backup.dump

# Restauration sur une base vide
pg_restore -U $DB_USER -h $DB_HOST -d $DB_NAME --clean --if-exists astrolearn_backup.dump
```

Avec Docker, la sauvegarde peut se faire directement depuis le conteneur `db` :

```bash
docker compose exec db pg_dump -U postgres -d astrolearn_db -F c -f /tmp/backup.dump
docker compose cp db:/tmp/backup.dump ./astrolearn_backup.dump
```

### Commentaires (NoSQL)

Les fils de commentaires (profondeur illimitée, réponses aux réponses) sont stockés dans
MongoDB plutôt qu'en relationnel : ce type de donnée arborescente de taille variable se prête
mal aux jointures SQL classiques. Un document par objet céleste, avec l'arbre complet des
commentaires imbriqué dedans :

```json
{
  "objet_id": 1,
  "commentaires": [
    {
      "commentaire_id": "uuid",
      "utilisateur_id": 12,
      "pseudo": "alice",
      "texte": "Superbe objet !",
      "date": "2026-07-29T10:10:25+00:00",
      "reponses": [
        { "commentaire_id": "uuid", "...": "...", "reponses": [] }
      ]
    }
  ]
}
```

La logique métier (validation, insertion récursive dans l'arbre) est encapsulée dans
`model/comment_service.py` (classe `CommentaireService`).

Un compte utilisateur ou un compte admin peuvent tous les deux commenter/répondre (deux
systèmes de session distincts, gérés par `controller/comment_routes.py`). Les commentaires
postés par un admin apparaissent sous l'identité générique « Administration AstroLearn ».
Le tableau de bord admin propose un onglet **Commentaires** : liste de tous les commentaires
tous objets confondus, badge du nombre de nouveaux commentaires, réponse et suppression
(avec ses éventuelles réponses imbriquées) directement depuis l'interface.

## Tests

```bash
pytest tests/
```

`test_db.py` et `test_db_connexion.py` nécessitent une base PostgreSQL accessible (fournie par un
conteneur de service dans la CI GitHub Actions) ; les autres sont des tests unitaires isolés
(mocks) qui tournent sans dépendance externe.

`test_astroia.py` appelle une vraie clé API Gemini payante : il est volontairement exclu de la
CI (`pytest tests/ --ignore=tests/test_astroia.py`) pour ne pas consommer de quota ni dépendre
d'un service externe à chaque push. À lancer manuellement en local si besoin :
`pytest tests/test_astroia.py -v`.

## Qualité de code

```bash
flake8 controller/ model/ --max-line-length=120
black controller/ model/ --check
```

## Éco-conception

Quelques choix appliqués pour limiter l'empreinte de l'application :

- **Chargement différé des images** (`loading="lazy"`) sur les grilles d'objets célestes, les
  listes de propositions et les tableaux d'administration, pour ne charger que les images
  réellement visibles à l'écran.
- **Pas d'images par défaut stockées inutilement** : un placeholder généré à la volée
  (`placehold.co`) est utilisé tant qu'aucune image n'a été uploadée pour un objet, plutôt que
  de stocker une image de remplacement pour chaque entrée.
- **Requêtes SQL ciblées** : les pages ne récupèrent que les colonnes nécessaires à l'affichage,
  pas de `SELECT *` systématique sur des tables larges.
- **Dépendances minimales** : pas de framework JS lourd, Three.js n'est chargé que sur la page
  qui en a besoin (système solaire).

Limite connue : Tailwind CSS est chargé via son CDN de développement (`cdn.tailwindcss.com`),
qui compile le CSS à la volée côté client. Une build de production avec le CLI Tailwind
(purge des classes inutilisées, fichier CSS statique et minifié) réduirait le poids transféré
à chaque page ; ce n'est pas encore en place.
