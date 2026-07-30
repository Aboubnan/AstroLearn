# Procédure de déploiement — AstroLearn

Ce document décrit les environnements de l'application, la procédure d'installation
initiale du serveur de production, et la procédure de mise à jour courante.

## Environnements

| Environnement | Usage | Base de données |
|---|---|---|
| Local (dev) | Développement quotidien | PostgreSQL + MongoDB locaux, ou via `docker compose` |
| CI (GitHub Actions) | Vérification automatique à chaque push (flake8, black, pytest) | Conteneur PostgreSQL 16 éphémère, jetable à chaque run |
| Production (VPS OVH) | Application en ligne, https://astrolearn.nayaweb.fr | PostgreSQL et MongoDB installés sur le VPS, avec authentification |

## Prérequis serveur de production

- Ubuntu 22.04 LTS ("jammy")
- Python 3.12+, `venv`
- PostgreSQL (serveur local)
- MongoDB Community Edition (serveur local, avec authentification activée)
- nginx (reverse proxy + certificats HTTPS via Certbot/Let's Encrypt)
- systemd (gestion du service Gunicorn)

## Premier déploiement (installation initiale)

### 1. Récupération du code

```bash
sudo mkdir -p /var/www/AstroLearn_Project
cd /var/www/AstroLearn_Project
git clone https://github.com/Aboubnan/AstroLearn.git .
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

### 2. Base de données PostgreSQL

```bash
sudo -u postgres psql
```
```sql
CREATE DATABASE astrolearn_db;
CREATE USER astrolearn_user WITH PASSWORD 'un-mot-de-passe-fort';
GRANT ALL PRIVILEGES ON DATABASE astrolearn_db TO astrolearn_user;
```

### 3. MongoDB (commentaires)

```bash
sudo apt install -y mongodb-org
sudo systemctl enable --now mongod
```

Créer un utilisateur applicatif dédié, en lecture/écriture uniquement sur la base
`astrolearn_nosql` (principe du moindre privilège — pas d'accès `admin`) :

```bash
mongosh --eval '
db = db.getSiblingDB("astrolearn_nosql");
db.createUser({
  user: "astrolearn_app",
  pwd: "un-mot-de-passe-fort",
  roles: [{ role: "readWrite", db: "astrolearn_nosql" }]
});
'
```

Puis activer l'authentification dans `/etc/mongod.conf` :

```yaml
security:
  authorization: enabled
```

```bash
sudo systemctl restart mongod
```

### 4. Variables d'environnement

```bash
cp .env.example .env
```
Éditer `.env` avec les vraies valeurs de production : `DB_PASSWORD`, `SECRET_KEY`
(générée via `python -c "import secrets; print(secrets.token_hex(32))"`),
`GEMINI_API_KEY`, `MONGO_URI` (`mongodb://astrolearn_app:MOT_DE_PASSE@localhost:27017/astrolearn_nosql`).

### 5. Service systemd

Fichier `/etc/systemd/system/astrolearn.service` :

```ini
[Unit]
Description=Gunicorn instance to serve AstroLearn
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/var/www/AstroLearn_Project
Environment="PATH=/var/www/AstroLearn_Project/venv/bin"
ExecStart=/var/www/AstroLearn_Project/venv/bin/gunicorn --workers 3 --bind unix:astrolearn.sock -m 007 app:app

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now astrolearn.service
```

### 6. nginx (reverse proxy + HTTPS)

Fichier `/etc/nginx/sites-available/astrolearn` (activé via un lien symbolique dans
`sites-enabled/`) :

```nginx
server {
    server_name astrolearn.nayaweb.fr;
    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/AstroLearn_Project/astrolearn.sock;
    }
    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/astrolearn.nayaweb.fr/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/astrolearn.nayaweb.fr/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
}

server {
    if ($host = astrolearn.nayaweb.fr) {
        return 301 https://$host$request_uri;
    }
    listen 80;
    server_name astrolearn.nayaweb.fr;
    return 404;
}
```

Le certificat HTTPS est géré par Certbot (renouvellement automatique via son propre
timer systemd, `certbot renew`).

```bash
sudo ln -s /etc/nginx/sites-available/astrolearn /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Déploiement courant (mise à jour de l'application)

Une fois l'installation initiale faite, chaque mise à jour se fait via le script
[`deploy.sh`](./deploy.sh), qui automatise : `git pull`, installation des dépendances,
redémarrage du service, vérification du statut et test de santé HTTP.

```bash
cd /var/www/AstroLearn_Project
bash deploy.sh
```

Le script s'arrête (`set -e`) au premier échec (conflit git, dépendance cassée,
service qui ne redémarre pas, ou site qui ne répond pas en HTTP 200), pour éviter de
laisser la production dans un état intermédiaire silencieux.

## Rollback en cas de problème

Revenir à un commit précédent qui fonctionnait, puis relancer le service :

```bash
cd /var/www/AstroLearn_Project
git log --oneline -5          # identifier le dernier commit stable
git checkout <hash-du-commit>
venv/bin/pip install -r requirements.txt
sudo systemctl restart astrolearn.service
```

Si le problème vient d'une migration de schéma PostgreSQL, restaurer la dernière
sauvegarde (voir la section « Sauvegarde et restauration » du [README](./README.md)) :

```bash
pg_restore -U $DB_USER -h $DB_HOST -d $DB_NAME --clean --if-exists astrolearn_backup.dump
```

Une fois le commit stable confirmé fonctionnel, revenir sur la branche principale :

```bash
git checkout main
git reset --hard <hash-du-commit>   # si le commit défectueux doit être écarté
```

## Vérifications post-déploiement

```bash
sudo systemctl status astrolearn.service --no-pager
sudo journalctl -u astrolearn.service -n 50 --no-pager
curl -I https://astrolearn.nayaweb.fr/
```
