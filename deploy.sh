#!/usr/bin/env bash
# Script de déploiement AstroLearn sur le VPS de production.
# À lancer depuis le VPS : bash deploy.sh
set -euo pipefail

PROJECT_DIR="/var/www/AstroLearn_Project"
SERVICE_NAME="astrolearn.service"
HEALTH_URL="https://astrolearn.nayaweb.fr/"

cd "$PROJECT_DIR"

echo "==> Récupération du dernier code (git pull)"
git pull

echo "==> Installation des dépendances Python"
venv/bin/pip install -r requirements.txt

echo "==> Redémarrage du service $SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"

echo "==> Attente du démarrage des workers Gunicorn"
sleep 3
sudo systemctl status "$SERVICE_NAME" --no-pager -l | head -n 15

echo "==> Test de santé HTTP sur $HEALTH_URL"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$HEALTH_URL")
if [ "$HTTP_CODE" = "200" ]; then
    echo "OK : le site répond (HTTP $HTTP_CODE)"
else
    echo "ÉCHEC : le site répond avec le code HTTP $HTTP_CODE"
    echo "Vérifier les logs : sudo journalctl -u $SERVICE_NAME -n 50 --no-pager"
    exit 1
fi

echo "==> Déploiement terminé, dernier commit en ligne :"
git log -1 --format="%h %an %ad %s" --date=short
