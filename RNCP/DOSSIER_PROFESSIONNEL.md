# Dossier Professionnel — Exemples de pratique professionnelle

Projet support pour les 3 activités-types : **AstroLearn**.

---

## Activité-type 1 : Concevoir et développer une application sécurisée en couches (CCP2)

### Exemple n°1 ▸ Projet AstroLearn

#### 1. Décrivez les tâches ou opérations que vous avez effectuées, et dans quelles conditions

**Résumé**

Pour AstroLearn, j'ai mené seul toute la phase de conception : cadrage des besoins et
des rôles, maquettage de l'interface, choix de l'architecture logicielle, conception de
la base de données relationnelle, puis développement des composants qui accèdent aux
données (SQL et NoSQL). Le projet est parti d'un simple catalogue statique pour devenir
une application complète avec comptes utilisateurs, favoris, propositions modérées,
commentaires imbriqués et espace d'administration.

**I. Analyser les besoins et maquetter une application**

J'ai commencé par cadrer le besoin : une plateforme web autour de l'astronomie, avec un
catalogue d'objets célestes, une carte 3D du système solaire, un chatbot, et des comptes
utilisateurs avec favoris et propositions d'objets. J'ai identifié deux rôles côté
compte (Utilisateur, Administrateur), plus le Visiteur non connecté.

J'ai avancé sur l'interface en quatre étapes, en partant de l'organisation générale pour
aller vers le rendu final :
- **Sitemap** : j'ai listé tous les écrans de l'application et je les ai organisés par
  niveau d'accès (visiteur, utilisateur connecté, administrateur), pour voir
  l'enchaînement des parcours avant de rentrer dans le détail visuel.
- **Zoning** : répartition des grandes zones de la page catalogue (en-tête, filtres,
  contenu, pied de page).
- **Wireframe** : placement des éléments réels de la page d'accueil, sans couleurs ni
  typographie définitives.
- **Maquette** : rendu final sous Figma, thème sombre, avec la charte graphique
  (couleurs, typographie Inter).

📎 Insérer ici : sitemap, zoning, wireframe, maquette et charte graphique
(`RNCP/2. Conception-UX_UI/`)

**II. Définir l'architecture logicielle d'une application**

J'ai organisé AstroLearn selon le patron **MVC (Model-View-Controller)**, avec trois
dossiers distincts (`model/`, `templates/`, `controller/`), pour séparer les
responsabilités et limiter l'impact d'un changement : modifier l'apparence d'une page ne
touche que `templates/`, changer une table ne touche que `model/`.

Le Model s'appuie sur deux bases de données différentes selon le type de données à
stocker : PostgreSQL pour tout ce qui est relationnel (catalogue, comptes,
propositions), MongoDB pour les commentaires imbriqués, dont l'arborescence de
profondeur variable colle mieux à un stockage en document qu'à des jointures
récursives.

Le dossier `controller/` est divisé en sept blueprints Flask, chacun pour un domaine
fonctionnel (pages publiques, connexion, espace utilisateur, administration, chatbot,
commentaires, système solaire 3D).

📎 Insérer ici : schéma d'architecture MVC (`RNCP/3. Architecture de données/Architecture MVC.png`)

**III. Concevoir et mettre en place une base de données relationnelle**

Pour la conception des données, j'ai suivi la méthode **Merise** : un diagramme de cas
d'utilisation UML pour cadrer les interactions entre les deux acteurs du système
(Utilisateur et Administrateur), puis une modélisation en trois étapes (MCD → MLD →
MPD), réalisée avec drawSQL.

Le MCD identifie sept entités (`UTILISATEUR`, `ADMIN`, `OBJET_CELESTE`, `CATEGORIE`,
`PROPOSITION`, `FAVORI`, `SAISIR`). Deux associations sont plusieurs-à-plusieurs, avec
une cardinalité (0,N) des deux côtés : `SAISIR` (traçabilité de l'administrateur qui a
saisi ou validé un objet) et `AIMER` (favoris). Chaque association N,N devient une table
de jonction au niveau logique ; les relations 1,N deviennent des clés étrangères. Le MPD
correspond directement au script SQL de création des tables (`CREATE_TABLES_SQL` dans
`model/database.py`), avec les contraintes `NOT NULL`, `UNIQUE`, et les politiques de
suppression (`ON DELETE CASCADE` ou `ON DELETE SET NULL` selon le cas).

📎 Insérer ici : UML, MCD, MLD, MPD (`RNCP/3. Architecture de données/`)

**IV. Développer des composants d'accès aux données SQL et NoSQL**

Toute la logique d'accès aux données est isolée dans le dossier `model/`, aucune requête
SQL ou NoSQL n'apparaît dans le Controller. Je n'utilise aucun ORM : les requêtes SQL
sont écrites directement avec `psycopg2`, et les documents MongoDB sont manipulés
directement avec `pymongo`.

Chaque fonction qui modifie la base PostgreSQL utilise `try` / `commit`, `except` /
`rollback`, `finally` / `close`, pour ne jamais laisser la base dans un état à moitié
modifié en cas d'erreur (par exemple `traiter_proposition()`, qui met à jour la
proposition, crée l'objet et trace la saisie en une seule fois, tout ou rien).

Côté MongoDB, la collection `commentaires` stocke un document par objet céleste, avec
l'arbre complet des commentaires et de leurs réponses imbriquées. `CommentaireService`
récupère le document, modifie l'arbre directement en mémoire, puis réenregistre tout le
document avec `update_one(..., upsert=True)`.

J'applique plusieurs bonnes pratiques de sécurité sur l'accès aux données : requêtes
paramétrées (jamais de texte SQL construit à la main), mots de passe hashés avec
`bcrypt`, séparation stricte des tables `UTILISATEUR` et `ADMINISTRATEUR`, et gestion des
erreurs systématique (`try/except` autour de chaque fonction qui accède à la base).

📎 Insérer ici : extraits de code (`RNCP/Capture/carbon_get_object_by_id.png`,
`carbon_document_commentaires.png`, `carbon_securite_acces_donnees.png`)

#### 2. Précisez les moyens utilisés

- Ordinateur, connexion internet
- VS Code (éditeur de code)
- Figma (maquettage)
- drawSQL (modélisation MCD/MLD/MPD)
- Python 3.12, Flask, PostgreSQL (psycopg2), MongoDB (pymongo)
- Git / GitHub (versionnement)
- Notion / GitHub Projects (suivi de l'avancement)

#### 3. Avec qui avez-vous travaillé ?

J'ai travaillé seul, dans le cadre d'un projet individuel réalisé pendant ma formation.

#### 4. Contexte

| Champ | Valeur |
|---|---|
| Nom de l'entreprise, organisme ou association | Beauvoir |
| Chantier, atelier, service | Projet personnel / autoformation |
| Période d'exercice | Du 03/12/2025 au 30/07/2026 |

#### 5. Informations complémentaires (facultatif)

_(rien à ajouter)_

---

## Activité-type 2 : Développer une application sécurisée (CCP1)

### Exemple n°1 ▸ Projet AstroLearn

#### 1. Décrivez les tâches ou opérations que vous avez effectuées, et dans quelles conditions

**Résumé**

Après la phase de conception, j'ai développé AstroLearn de bout en bout : mise en place
de mon environnement de travail, interfaces utilisateur, composants métier côté serveur,
et sécurisation de l'ensemble. J'ai aussi géré ce projet individuel avec les outils
habituels du développement en équipe (dépôt Git, Kanban, intégration continue), adaptés
à un seul développeur.

**I. Installer et configurer son environnement de travail en fonction du projet**

J'ai mis en place un environnement Python 3.12 avec un environnement virtuel dédié
(`venv`), les dépendances gérées via `requirements.txt` et installées par `pip`. Le
dépôt est hébergé sur GitHub, avec un `.gitignore` qui exclut l'environnement virtuel,
les uploads utilisateurs et les fichiers sensibles.

J'ai aussi mis en place un `docker-compose.yml` qui définit trois services (base
PostgreSQL, base MongoDB, application Flask/Gunicorn) pour reproduire l'environnement de
production en local, sans rien installer sur ma machine. Le `README.md` documente les
deux parcours d'installation (avec ou sans Docker) et la liste des variables
d'environnement requises, pour qu'un environnement identique puisse être reconstitué à
partir du dépôt seul.

📎 Insérer ici : capture du `docker-compose.yml` ou du `README.md`

**II. Développer des interfaces utilisateur**

Pour l'affichage, j'utilise des templates **Jinja2** (rendu côté serveur), **Tailwind
CSS**, un peu de JavaScript pur pour les interactions qui n'ont pas besoin de recharger
la page (ajouter ou retirer un favori en AJAX, par exemple), et **Three.js** pour le
rendu 3D du système solaire. Les couleurs et la police sont les mêmes partout grâce aux
couleurs Tailwind personnalisées et à la police Inter.

J'ai pensé l'affichage pour mobile en premier, puis j'ai ajouté des règles pour les
écrans plus larges. J'ai aussi fait passer un audit Lighthouse sur une fiche d'objet
céleste (score de 91/100) pour vérifier l'accessibilité.

📎 Insérer ici : capture responsive (`RNCP/Capture/carbon_catalogue_responsive.png`,
`responsive_desktop_mobile.png`)

**III. Développer des composants métier**

Plutôt que d'écrire toute la logique métier directement dans les routes du Controller,
je l'ai mise dans des classes à part, chacune dédiée à une tâche précise :
`CommentaireService` (qui lit et modifie l'arbre de commentaires MongoDB) et
`AstroIAChatbot` (qui valide les messages envoyés au chatbot et prépare le contexte
envoyé à l'API Gemini). Chaque classe vérifie elle-même ce qu'elle reçoit et renvoie une
erreur précise si besoin, et je les ai couvertes chacune par leur propre suite de tests
(15 tests pour `CommentaireService`, 6 pour `AstroIAChatbot`).

Les commentaires sont un bon exemple de composant métier partagé : ils sont ouverts aux
utilisateurs comme aux administrateurs, alors que ce sont deux systèmes de connexion
différents. Plutôt que de dupliquer les routes, `comment_routes.py` identifie l'auteur
une seule fois, au même endroit.

📎 Insérer ici : capture (`RNCP/Capture/carbon_astroia_chatbot.png`,
`carbon_identite_auteur.png`)

**IV. Développer une application sécurisée**

La sécurité n'est pas traitée dans un module à part chez AstroLearn, elle est présente
au fil du développement : requêtes paramétrées contre les injections SQL, mots de passe
hashés avec `bcrypt`, protection CSRF sur toutes les requêtes qui modifient une donnée
(`Flask-WTF`), cookies de session avec les attributs `HttpOnly`, `Secure` et
`SameSite=Lax`, et aucun secret écrit en dur dans le code (tout est chargé depuis un
fichier `.env` non versionné). Les décorateurs `login_required` et `admin_required`
vérifient la session avant d'exécuter une route, et chaque formulaire est revalidé côté
serveur (la validation HTML côté client ne garantit rien en soi).

📎 Insérer ici : capture (`RNCP/Capture/carbon_decorateurs_acces.png`,
`carbon_securite_acces_donnees.png`)

**V. Contribuer à la gestion d'un projet informatique**

Comme AstroLearn est un projet individuel, j'ai repris les principes qui restent utiles
à un seul développeur plutôt qu'une organisation Scrum complète : une liste de
fonctionnalités priorisées, une livraison itérative par lot fonctionnel, et un retour
régulier au cahier des charges. J'ai utilisé un dépôt Git avec un historique de commits
public, un tableau Kanban (GitHub Projects) pour suivre l'avancement, et une intégration
continue (GitHub Actions) qui vérifie la qualité du code et exécute les tests à chaque
push. Mes commits suivent une convention proche de *Conventional Commits* (`feat:`,
`fix:`, `refactor:`, `chore:`, `docs:`).

📎 Insérer ici : capture (`RNCP/Capture/KanBan.png`, `github_commits.png`)

#### 2. Précisez les moyens utilisés

- Ordinateur, connexion internet
- VS Code (éditeur de code)
- Python 3.12, Flask, Jinja2, Tailwind CSS, JavaScript, Three.js
- Docker / Docker Compose
- Git / GitHub, GitHub Actions, GitHub Projects (Kanban)
- Lighthouse (audit d'accessibilité)

#### 3. Avec qui avez-vous travaillé ?

J'ai travaillé seul, dans le cadre d'un projet individuel réalisé pendant ma formation.

#### 4. Contexte

| Champ | Valeur |
|---|---|
| Nom de l'entreprise, organisme ou association | Beauvoir |
| Chantier, atelier, service | Projet personnel / autoformation |
| Période d'exercice | Du 03/12/2025 au 30/07/2026 |

#### 5. Informations complémentaires (facultatif)

_(rien à ajouter)_

---

## Activité-type 3 : Préparer le déploiement d'une application sécurisée (CCP3)

### Exemple n°1 ▸ Projet AstroLearn

#### 1. Décrivez les tâches ou opérations que vous avez effectuées, et dans quelles conditions

**Résumé**

Pour finir, j'ai préparé et exécuté le plan de tests d'AstroLearn, documenté son
déploiement, puis mis l'application en ligne sur un VPS avec une démarche DevOps :
intégration continue automatisée, déploiement manuel maîtrisé, et veille technologique
et sécurité continue.

**I. Préparer et exécuter les plans de tests**

J'ai combiné quatre niveaux de test : des tests unitaires (`pytest`, avec mocks) sur la
logique métier, des tests d'intégration (`app.test_client()`) sur le comportement HTTP
réel, des tests de sécurité ciblés (hachage bcrypt, rejet des requêtes sans jeton CSRF),
et une campagne fonctionnelle manuelle sur les parcours qui n'ont pas encore de test
automatisé dédié. Les tests automatisés tournent en intégration continue à chaque push,
dans le même job qui vérifie aussi la qualité du code.

J'ai aussi mené un jeu d'essai détaillé sur les commentaires imbriqués, la fonctionnalité
la plus représentative du projet car elle combine PostgreSQL, MongoDB, la sécurité et la
couche de service `CommentaireService`. Résultat : 16/16 vérifications conformes.

📎 Insérer ici : capture (`RNCP/Capture/github_actions_pytest.png`)

**II. Préparer et documenter le déploiement**

J'ai documenté toute la procédure de déploiement (`DEPLOIEMENT.md`) : préparation du
serveur (Ubuntu 22.04 LTS), nom de domaine, installation de PostgreSQL et MongoDB avec
authentification, service systemd pour Gunicorn, configuration nginx en reverse proxy
avec certificat HTTPS (Certbot/Let's Encrypt). Docker n'est utilisé qu'en local et en CI,
pas en production : c'est un choix que j'assume pour un seul développeur et un seul
serveur, plutôt qu'un oubli.

📎 Insérer ici : captures terminal (`RNCP/Capture/PostgreSQL.png`, `MongoDB —
configuration.png`, `Service systemd (Gunicorn).png`, `Configuration nginx.png`)

**III. Contribuer à la mise en production (DevOps)**

Un job GitHub Actions se déclenche à chaque push, sur toutes les branches : vérification
du code (`flake8`), formatage (`black --check`), puis suite `pytest` contre un
PostgreSQL temporaire. Le dépôt a l'alerte de sécurité Dependabot activée, qui ouvre une
pull request automatique dès qu'une faille connue touche une dépendance. Le déploiement,
lui, reste déclenché manuellement via un script (`deploy.sh`) plutôt que branché
directement sur la CI : je préfère garder une validation humaine avant chaque mise en
ligne, parce que je n'ai pas d'outils de supervision et de rollback assez solides pour
faire de la livraison continue sans surveillance humaine.

Je fais aussi une veille technologique et sécurité continue sur l'infrastructure : alertes
Dependabot, notes de version des briques utilisées, alertes de sécurité Ubuntu, et
documentation officielle GitHub Actions.

📎 Insérer ici : capture (`RNCP/Capture/dependabot.png`)

#### 2. Précisez les moyens utilisés

- Ordinateur, connexion internet
- pytest, GitHub Actions, flake8, black
- VPS OVH (Ubuntu 22.04 LTS), PostgreSQL, MongoDB
- nginx, Gunicorn, systemd, Certbot/Let's Encrypt
- Dependabot

#### 3. Avec qui avez-vous travaillé ?

J'ai travaillé seul, dans le cadre d'un projet individuel réalisé pendant ma formation.

#### 4. Contexte

| Champ | Valeur |
|---|---|
| Nom de l'entreprise, organisme ou association | Beauvoir |
| Chantier, atelier, service | Projet personnel / autoformation |
| Période d'exercice | Du 03/12/2025 au 30/07/2026 |

#### 5. Informations complémentaires (facultatif)

_(rien à ajouter)_

---
