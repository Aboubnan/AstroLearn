# AstroLearn

Application web éducative sur l'astronomie : catalogue d'objets célestes, système solaire 3D
interactif, assistant conversationnel AstroIA, comptes utilisateurs et espace d'administration.

Démo en ligne : https://astrolearn.nayaweb.fr

## Stack technique

- **Backend** : Python 3.12, Flask (organisé en blueprints), PostgreSQL (psycopg2)
- **Frontend** : Jinja2, Tailwind CSS, Three.js (système solaire 3D), JavaScript vanilla
- **Sécurité** : bcrypt (hachage des mots de passe), Flask-WTF (protection CSRF)
- **IA** : API Gemini 2.5 Flash (chatbot AstroIA)
- **Tests** : pytest
- **CI** : GitHub Actions (flake8, black, pytest)
- **Déploiement** : Gunicorn + nginx + systemd (VPS), ou Docker

## Architecture

```
controller/   Routes Flask, organisées en blueprints (main, auth, user, admin, chatbot, skymap)
model/        Accès aux données (PostgreSQL) et services métier (ex: chatbot_service.py)
templates/    Vues Jinja2
static/       CSS, JS, images, uploads utilisateurs
tests/        Tests pytest (unitaires et d'intégration)
```

## Installation locale (sans Docker)

Prérequis : Python 3.12+, PostgreSQL en local.

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

Le service `web` (Flask + Gunicorn) démarre sur http://localhost:5000, le service `db`
(PostgreSQL 16) est exposé sur le port hôte 5433 pour éviter tout conflit avec un PostgreSQL
local existant. Le schéma de base de données est créé automatiquement au premier démarrage.

## Variables d'environnement

Voir `.env.example` pour la liste complète. Les indispensables :

| Variable | Description |
|---|---|
| `DB_PASSWORD` | Mot de passe PostgreSQL |
| `SECRET_KEY` | Clé de signature des sessions Flask (`python -c "import secrets; print(secrets.token_hex(32))"`) |
| `GEMINI_API_KEY` | Clé API Google Gemini, pour le chatbot AstroIA |

`ADMIN_PSEUDO` / `ADMIN_PASSWORD` / `ADMIN_EMAIL` sont optionnelles : si toutes les trois sont
renseignées, un compte administrateur est créé automatiquement au premier démarrage.

## Tests

```bash
pytest tests/
```

Certains tests (`test_db.py`, `test_db_connexion.py`, `test_astroia.py`) nécessitent une base
PostgreSQL accessible et une clé Gemini valide ; les autres sont des tests unitaires isolés
(mocks) qui tournent sans dépendance externe.

## Qualité de code

```bash
flake8 controller/ model/ --max-line-length=120
black controller/ model/ --check
```
