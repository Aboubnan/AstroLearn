# Veille technologique et sécurité — déploiement

Ce document trace la veille effectuée sur les évolutions technologiques et les
problématiques de sécurité liées au **déploiement** d'AstroLearn (infrastructure,
CI/CD, dépendances) — à distinguer de la veille sur les vulnérabilités applicatives
menée au niveau du code (voir les mentions de sécurité dans le
[README](./README.md)).

## Sources suivies

- **GitHub Dependabot** : alertes de sécurité et pull requests automatiques sur les
  dépendances Python du projet (activé sur le dépôt).
- **Notes de version / changelogs** des briques d'infrastructure utilisées :
  PostgreSQL, MongoDB, nginx, Gunicorn, Certbot/Let's Encrypt.
- **Ubuntu Security Notices (USN)** pour les mises à jour de sécurité du système du
  VPS (Ubuntu 22.04 LTS).
- **Documentation officielle GitHub Actions**, notamment sur la gestion des permissions
  et des scopes de token.

## Méthode

Les alertes Dependabot sont vérifiées à chaque notification ; une mise à jour est
appliquée après vérification qu'elle ne casse pas la suite de tests (`pytest`) et la
CI (flake8/black). Les correctifs de sécurité système (Ubuntu, PostgreSQL, MongoDB)
sont appliqués via les gestionnaires de paquets (`apt`) lors des fenêtres de
maintenance du VPS.

## Exemples concrets appliqués pendant le projet

**27/07/2026 — Mise à jour de dépendances signalées par Dependabot.**
Dependabot a signalé des versions obsolètes de Flask (3.1.2), idna (3.11),
python-dotenv (1.2.1), requests (2.32.5), urllib3 (2.5.0) et Werkzeug (3.1.4),
contenant des correctifs de sécurité mineurs. Mise à jour vers les versions
patchées (Flask 3.1.3, idna 3.15, python-dotenv 1.2.2, requests 2.33.0,
urllib3 2.7.0, Werkzeug 3.1.6), vérifiée par la suite de tests avant déploiement
(commit `ec1448e`).

**Installation de MongoDB sur le VPS — principe du moindre privilège.**
La documentation de sécurité MongoDB recommande l'authentification SCRAM-SHA-256 et
la création de comptes applicatifs dédiés plutôt qu'un compte administrateur
partagé. Appliqué lors de l'installation : un utilisateur `astrolearn_app` limité au
rôle `readWrite` sur la seule base `astrolearn_nosql`, distinct du compte `admin` du
serveur, avec `security.authorization: enabled` dans `/etc/mongod.conf` (vérifié par
un test de connexion sans authentification, rejeté comme attendu).

**Scope de token GitHub Actions.**
Lors d'une mise à jour du workflow CI (`.github/workflows/ci.yml`), un push a été
rejeté par GitHub : le token d'authentification utilisé ne disposait pas du scope
`workflow`, requis pour modifier des fichiers sous `.github/workflows/`. Ceci illustre
concrètement le principe de moindre privilège appliqué aux jetons CI/CD : un token
sans ce scope ne peut pas altérer le pipeline d'intégration continue, ce qui limite
l'impact d'une éventuelle fuite de token.

**Base de données de test éphémère plutôt qu'exposition de la production.**
Plutôt que d'exposer la base PostgreSQL de production à internet pour que les
runners GitHub Actions (hébergés dans le cloud) puissent l'atteindre, un conteneur
PostgreSQL jetable est démarré comme service dans le workflow CI lui-même
(`.github/workflows/ci.yml`), initialisé et détruit à chaque run. Réduit la surface
d'attaque sans sacrifier la couverture de test.

**Renouvellement automatique du certificat HTTPS.**
Le certificat TLS du domaine est géré par Certbot/Let's Encrypt avec renouvellement
automatique via son propre timer systemd, évitant une expiration manuelle du
certificat en production.
