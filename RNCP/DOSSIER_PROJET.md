# AstroLearn : Dossier de Projet

**RNCP Concepteur Développeur d'Applications**

## Sommaire

1. Résumé du projet
2. Compétences du référentiel couvertes par le projet
3. Contexte, cahier des charges, utilisateurs et rôles
4. Analyse des besoins et maquettage
5. Architecture logicielle
6. Base de données relationnelle
7. Composants d'accès aux données SQL et NoSQL
8. Interfaces et composants métier
9. Sécurité
10. Gestion de projet
11. Plan de tests
12. Déploiement
13. Démarche DevOps
14. Veille technologique et sécurité
15. Bilan
16. Annexes

---

## 1. Résumé du projet

AstroLearn est une application web sur l'astronomie que j'ai développée dans le cadre de ma
certification. On y trouve un catalogue d'objets célestes (planètes, galaxies,
constellations) qu'on peut filtrer et parcourir, une carte 3D du système solaire, et un
chatbot (AstroIA) qui répond aux questions des visiteurs sur l'astronomie.

Les utilisateurs qui créent un compte peuvent aller plus loin : mettre des objets en
favoris, proposer eux-mêmes de nouveaux objets pour le catalogue (un admin valide ensuite),
et discuter sous les fiches d'objets grâce à un système de commentaires qui peut s'imbriquer
sur plusieurs niveaux. Côté admin, il y a un espace dédié pour gérer le catalogue, les
comptes et les propositions en attente, avec un suivi de qui a ajouté ou validé chaque objet.

Côté technique, j'ai construit l'application en Python avec Flask, sur une architecture MVC.
Les données sont réparties entre deux bases : PostgreSQL pour tout ce qui est relationnel
(catalogue, comptes, propositions) et MongoDB pour les commentaires imbriqués. Le site
tourne en production sur un VPS (Gunicorn, nginx, HTTPS), avec une intégration continue qui
lance les tests et vérifie la qualité du code à chaque modification.

### Abstract

AstroLearn is an educational web application about astronomy. It offers a browsable,
filterable catalog of celestial objects (planets, galaxies, constellations), an interactive 3D
visualization of the solar system, and a conversational assistant (AstroIA) that answers
visitors' astronomy questions.

Registered users can bookmark objects as favorites, submit new celestial objects for the
catalog (subject to administrator approval), and comment on object pages through a
nested discussion system. The administration area manages the full catalog, user
accounts, and pending submissions, with a traceability log of who added or validated
each entry.

The application follows an MVC architecture in Python/Flask, with hybrid persistence:
PostgreSQL for relational data (catalog, accounts, submissions) and MongoDB for nested
comments. It is deployed in production on a VPS server (Gunicorn, nginx, HTTPS), with
continuous integration automatically running tests and code quality checks on every
change.

---

## 2. Compétences du référentiel couvertes par le projet

| Bloc | CP | Compétence professionnelle | Section |
|---|---|---|---|
| 1 | CP1 | Installer et configurer son environnement de travail en fonction du projet | §12.2 |
| 1 | CP2 | Développer des interfaces utilisateur | §8.2 |
| 1 | CP3 | Développer des composants métier | §8.3 |
| 1 | CP4 | Contribuer à la gestion d'un projet informatique | §10 |
| 2 | CP5 | Analyser les besoins et maquetter une application | §4 |
| 2 | CP6 | Définir l'architecture logicielle d'une application | §5 |
| 2 | CP7 | Concevoir et mettre en place une base de données relationnelle | §6 |
| 2 | CP8 | Développer des composants d'accès aux données SQL et NoSQL | §7 |
| 3 | CP9 | Préparer et exécuter les plans de tests d'une application | §11 |
| 3 | CP10 | Préparer et documenter le déploiement d'une application | §12 |
| 3 | CP11 | Contribuer à la mise en production dans une démarche DevOps | §13 |

---

## 3. Contexte, cahier des charges, utilisateurs et rôles

### 3.1 Contexte

AstroLearn est un projet individuel que j'ai réalisé pour la certification RNCP Concepteur
Développeur d'Applications. Au départ, je voulais rester sur quelque chose de simple : un
catalogue, un chatbot, un formulaire de sondage, une authentification simulée. Au fil du
développement, le projet s'est beaucoup enrichi : j'ai ajouté de vrais comptes utilisateurs,
un système de favoris, un workflow de proposition d'objets validé par un administrateur,
des commentaires imbriqués, un espace d'administration complet, et pour finir une vraie
mise en production documentée.

### 3.2 Cahier des charges

**Objectif.** Développer une plateforme web dynamique, responsive et sécurisée autour de
l'astronomie, avec un catalogue d'objets célestes, une visualisation 3D du système solaire,
un assistant IA conversationnel, des comptes utilisateurs avec favoris et propositions
d'objets, et un espace d'administration.

**Exigences fonctionnelles**

| Module | Fonctionnalité | Rôle | CRUD |
|---|---|---|---|
| Catalogue | Afficher la liste des objets célestes | Visiteur | R |
| Détail | Afficher les informations d'un objet | Visiteur | R |
| Chatbot | Interroger l'IA sur l'astronomie | Visiteur | - |
| Formulaire | Soumettre un sondage/avis | Visiteur | C |
| Compte utilisateur | S'inscrire, se connecter, modifier son profil | Utilisateur | C, U |
| Favoris | Ajouter ou retirer un objet de ses favoris | Utilisateur | C, D |
| Proposition | Proposer un nouvel objet céleste | Utilisateur | C |
| Proposition | Valider, modifier ou refuser une proposition | Admin | U |
| Commentaires | Commenter un objet, répondre à un commentaire | Utilisateur, Admin | C, D |
| Administration | Gérer le catalogue (ajout, modification, suppression) | Admin | C, U, D |
| Administration | Gérer les comptes (utilisateurs et administrateurs) | Admin | C, R, U, D |
| Traçabilité | Savoir quel administrateur a saisi ou validé un objet | Admin | R |

**Exigences techniques**

| Catégorie | Exigence | Outils / Technologies |
|---|---|---|
| Architecture | Patron MVC, organisé en blueprints Flask | Python 3.12 / Flask |
| Base de données | Stockage relationnel et NoSQL | PostgreSQL (psycopg2), MongoDB (pymongo) |
| Front-End | Interface responsive | HTML5, Tailwind CSS, JavaScript, Three.js |
| Gestion de version | Git, historique lisible | Git / GitHub |
| Sécurité | Requêtes paramétrées, hashage, protection CSRF | psycopg2, bcrypt, Flask-WTF |
| Qualité | Tests automatisés à chaque push | Pytest, GitHub Actions |
| API | Connexion à une API LLM pour le chatbot | Gemini 2.5 Flash |
| Déploiement | Mise en production reproductible et documentée | VPS OVH, Gunicorn, nginx, systemd, Certbot |
| Déploiement | Environnement conteneurisé pour le développement | Docker, Docker Compose |

### 3.3 Utilisateurs et rôles

L'application distingue trois profils. Ça correspond à deux systèmes de comptes bien
distincts en base de données : les administrateurs et les utilisateurs ne partagent pas la
même table, un choix de séparation stricte des privilèges.

- **Visiteur** : non authentifié, accède au contenu public.
- **Utilisateur** : compte inscrit, accède aux fonctionnalités personnelles (favoris,
  propositions, commentaires, profil).
- **Administrateur** : compte distinct, gère le catalogue, les comptes et modère les
  contributions.

### 3.4 Matrice des droits par profil

| Action | Visiteur | Utilisateur | Admin |
|---|---|---|---|
| Consulter le catalogue et les fiches objets | ✓ | ✓ | ✓ |
| Utiliser l'assistant AstroIA | ✓ | ✓ | ✓ |
| Répondre au sondage (avis) | ✓ | ✓ | ✓ |
| Créer un compte / se connecter | ✓ | / | / |
| Se connecter (accès admin) | ✗ | ✗ | ✓ |
| Modifier son profil | ✗ | ✓ | ✓ |
| Ajouter / retirer un favori | ✗ | ✓ | ✗ |
| Proposer un objet céleste | ✗ | ✓ | ✗ |
| Consulter ses propositions | ✗ | ✓ | ✗ |
| Commenter un objet | ✗ | ✓ | ✓ |
| Répondre à un commentaire | ✗ | ✗ | ✓ |
| Supprimer un commentaire | ✗ | ✗ | ✓ |
| Valider / modifier / refuser une proposition | ✗ | ✗ | ✓ |
| Ajouter / modifier / supprimer un objet du catalogue | ✗ | ✗ | ✓ |
| Gérer les comptes utilisateurs | ✗ | ✗ | ✓ |
| Gérer les comptes administrateurs | ✗ | ✗ | ✓ |
| Consulter la traçabilité de saisie | ✗ | ✗ | ✓ |

Un compte administrateur n'a pas accès aux actions "sociales" comme les favoris ou les
propositions. Ces fonctionnalités sont rattachées à la table `UTILISATEUR`, à laquelle un
compte `ADMINISTRATEUR` n'a tout simplement pas accès. C'est voulu : un admin n'a pas à se
comporter comme un utilisateur inscrit.

---

## 4. Analyse des besoins et maquettage

J'ai avancé sur l'interface en quatre étapes, en partant de l'organisation générale pour
aller vers le rendu final : zoning (répartition des zones fonctionnelles), wireframe
(placement des éléments réels sans design), maquette (rendu final avec la charte
graphique), puis développement.

### 4.1 Arborescence d'écrans (sitemap)

Avant de zoner ou de maquetter une page en particulier, j'ai listé tous les écrans de
l'application et je les ai organisés par niveau d'accès, histoire de voir l'enchaînement des
parcours avant de rentrer dans le détail visuel.

**Visiteur (non authentifié)**
- Accueil (`/`)
  - Encyclopédie / Catalogue (`/catalogue`) → Fiche d'un objet céleste (`/object/<id>`)
  - Carte du Système Solaire (`/sky-map`)
  - Sondage de satisfaction (`/formulaire`)
  - Mentions légales (`/legal`)
  - Connexion (`/connexion`) / Inscription (`/inscription`)
  - Assistant AstroIA (widget de chat, accessible depuis n'importe quelle page)

**Utilisateur connecté** (en plus des écrans visiteur)
- Mon espace (`/mon-espace`), organisé en deux onglets :
  - Mes propositions (statut : en attente / acceptée / refusée)
  - Mes favoris
- Mon profil (`/mon-profil`)
- Changer mon mot de passe (`/changer-mot-de-passe`)
- Proposer un objet céleste (`/proposer-objet`)
- Ajout/retrait d'un favori (action directe sur la fiche objet, sans changement de page)
- Commenter un objet ou répondre à un commentaire (sur la fiche objet)

**Administrateur** (espace de connexion séparé)
- Connexion admin (`/admin_login`)
- Tableau de bord admin (`/admin_dashboard`), organisé en onglets :
  - Gestion du catalogue (ajout, modification, suppression d'objets)
  - Gestion des comptes (utilisateurs et administrateurs)
  - Traitement des propositions en attente
  - Modération des commentaires
  - Ingestion du catalogue NASA

📎 Insérer ici : `RNCP/2. Conception-UX_UI/sitemap.png` (schéma visuel de
l'arborescence ci-dessus, à main levée ou via tldraw)

### 4.2 Zoning

Répartition des grandes zones de la page catalogue : en-tête (logo, liens de navigation,
bouton d'abonnement), zone de filtrage par catégorie, zone de contenu (cartes d'objets),
pied de page (liens légaux, réseaux sociaux).

📎 Insérer ici : `RNCP/2. Conception-UX_UI/zoning AstroLearn.png`

### 4.3 Wireframe

Mise en place des éléments réels de la page d'accueil (desktop) : logo, boutons de
navigation, bloc de texte principal, liste de filtres latérale, zone d'image, pied de page
structuré en colonnes, sans couleurs ni typographie définitives à ce stade.

📎 Insérer ici : `RNCP/2. Conception-UX_UI/wireframe.png`

### 4.4 Maquette

Rendu final réalisé sous Figma : thème sombre, barre de recherche, filtres par catégorie
(Planètes / Galaxies / Constellations), grille de cartes d'objets avec image, badge de
catégorie, description et bouton d'accès au détail.

📎 Insérer ici : `RNCP/2. Conception-UX_UI/maquette.png`

### 4.5 Charte graphique

| Usage | Couleur | HEX | RVB |
|---|---|---|---|
| Fond principal | Bleu nuit très sombre | #000525 | (0, 5, 36) |
| Fond secondaire | Bleu nuit | #1c2a5a | (28, 42, 90) |
| Texte clair | Lavande pâle | #e0e6f7 | (224, 230, 247) |
| Accentuation | Orange | #ff8811 | (255, 136, 17) |

Pour la typographie, j'ai choisi **Inter** : Bold pour les titres, Regular pour le texte
courant, appliquée partout sur le site sans exception.

📎 Insérer ici : `RNCP/2. Conception-UX_UI/Charte graphique/Charte graphique AstroLearn.png`

---

## 5. Architecture logicielle

### 5.1 Patron MVC

J'ai organisé AstroLearn selon le patron **MVC (Model-View-Controller)**, avec trois
dossiers distincts (`model/`, `templates/`, `controller/`). L'idée est de séparer les
responsabilités pour que chaque couche ne dépende que de son propre rôle :

- **Model** : accès aux données, sans aucune connaissance de HTTP ni de HTML. Un seul
  point d'entrée pour lire ou écrire dans PostgreSQL ou MongoDB.
- **View** : les pages Jinja2 affichées à l'utilisateur. Aucune logique métier ici,
  uniquement de l'affichage.
- **Controller** : reçoit les requêtes HTTP, appelle le Model pour obtenir ou modifier les
  données, sélectionne la View à retourner.

Cette séparation limite l'impact d'un changement. Modifier l'apparence d'une page ne touche
que `templates/`. Changer la structure d'une table ne touche que `model/`.

📎 Insérer ici : `RNCP/3. Architecture de données/Architecture MVC.png`

### 5.2 Deux bases de données : SQL et NoSQL

Le Model s'appuie sur deux bases de données différentes, choisies selon le type de données
à stocker :

| Base | Type de données | Justification |
|---|---|---|
| PostgreSQL | Catalogue, comptes, propositions, favoris | Données structurées et relationnelles, avec contraintes d'intégrité (clés étrangères, unicité) |
| MongoDB | Commentaires | Arborescence de profondeur variable (réponses imbriquées), plus naturelle à stocker en document qu'en jointures récursives |

### 5.3 Découpage du Controller en blueprints

Le dossier `controller/` est divisé en sept fichiers, chacun pour un domaine fonctionnel :
`main_routes.py` (pages publiques), `auth_bp.py` (connexion/inscription), `user_bp.py`
(espace utilisateur), `admin_routes.py` (administration), `chatbot_routes.py` (assistant
IA), `comment_routes.py` (commentaires) et `skymap_routes.py` (système solaire 3D). J'ai
utilisé le mécanisme des Blueprints de Flask pour ça : chaque fichier déclare ses propres
routes, qui sont ensuite enregistrées dans `app.py`.

### 5.4 Flux d'une requête

1. L'utilisateur envoie une requête HTTP au Controller.
2. Le Controller appelle les fonctions du Model concernées.
3. Le Model exécute la requête SQL ou NoSQL et retourne le résultat.
4. Le Controller transmet les données à la View, qui génère le HTML final.

### 5.5 Éco-conception

Quelques choix que j'ai retenus pour limiter l'empreinte de l'application :

- **Chargement différé des images** (`loading="lazy"`) sur les grilles d'objets
  célestes, les listes de propositions et les tableaux d'administration : seules les
  images réellement visibles à l'écran sont chargées.
- **Pas d'image de remplacement stockée** pour chaque objet sans photo. J'utilise un
  placeholder généré à la volée (service `placehold.co`) tant qu'aucune image n'a été
  téléversée, plutôt que de stocker un fichier de substitution pour chaque entrée.
- **Requêtes SQL ciblées** : les pages ne récupèrent que les colonnes nécessaires à
  l'affichage, pas de `SELECT *` systématique sur les tables volumineuses.
- **Dépendances client minimales** : pas de framework JavaScript lourd. La
  bibliothèque Three.js (rendu 3D) n'est chargée que sur la page qui en a besoin, le
  système solaire, pas sur l'ensemble du site.

---

## 6. Base de données relationnelle

Pour la conception des données, j'ai suivi la méthode **Merise** : d'abord un diagramme de
cas d'utilisation pour cadrer les interactions, puis une modélisation en trois étapes, en
allant du plus général au plus précis (MCD → MLD → MPD), réalisée avec drawSQL.

### 6.1 Diagramme de cas d'utilisation (UML)

Ce diagramme identifie les deux acteurs du système (Utilisateur et Administrateur) et
leurs interactions avec l'application : consulter le catalogue, interroger le chatbot,
s'inscrire, proposer un objet, commenter, ainsi que les actions d'administration (gérer le
catalogue, valider les propositions, gérer les comptes). Il m'a servi de support pour
cadrer les fonctionnalités avant de me lancer dans la conception de la base de données.

📎 Insérer ici : `RNCP/3. Architecture de données/UML.png`

### 6.2 Modèle Conceptuel de Données (MCD)

Le MCD identifie sept entités et leurs associations : `UTILISATEUR`, `ADMIN`,
`OBJET_CELESTE`, `CATEGORIE`, `PROPOSITION`, `FAVORI` et `SAISIR`. Deux associations
sont de type plusieurs-à-plusieurs, avec une cardinalité (0,N) des deux côtés, et
modélisées par une entité-association dédiée :

- `SAISIR`, entre `ADMIN` et `OBJET_CELESTE` : plusieurs administrateurs peuvent avoir
  saisi ou validé le même objet, et un administrateur peut avoir saisi plusieurs objets.
- `AIMER` (favoris), entre `UTILISATEUR` et `OBJET_CELESTE` : un utilisateur peut
  mettre plusieurs objets en favori, et un objet peut être mis en favori par plusieurs
  utilisateurs.

Les autres associations (`CLASSIFIER`, `CONCERNER`, `PROPOSER`, `AjOUTER`) sont des
relations 1,N classiques, reflétées par une clé étrangère au niveau logique.

📎 Insérer ici : `RNCP/3. Architecture de données/MCD.png`

### 6.3 Modèle Logique de Données (MLD)

Chaque association N,N du MCD devient une table de jonction au niveau logique ; les
relations 1,N deviennent des clés étrangères portées par l'entité du côté "N".

📎 Insérer ici : `RNCP/3. Architecture de données/MLD.webp`

Notation textuelle (clé primaire en tête, `#` pour les clés étrangères) :

```
CATEGORIE = (id_categorie, nom_categorie)

UTILISATEUR = (id_utilisateur, pseudo, nom, prenom, email, mot_de_passe_hash,
               genre, photo_profil, date_inscription, est_actif)

ADMINISTRATEUR = (id_admin, pseudo, mot_de_passe_hash, nom, prenom, email)

OBJET_CELESTE = (id_objet, nom_fr, nom_scientifique, description, distance_al,
                 url_image, date_publication, #fk_id_categorie, #fk_id_utilisateur)

PROPOSITION = (id_proposition, nom_fr, nom_scientifique, description, url_image,
               #fk_id_categorie, #fk_id_utilisateur, statut, commentaire_admin,
               date_proposition, date_traitement, notif_lue)

SAISIR = (#fk_id_admin, #fk_id_objet, date_saisie)
         clé primaire composite (fk_id_admin, fk_id_objet)

FAVORI = (id_favori, #fk_id_utilisateur, #fk_id_objet, date_ajout)
         contrainte d'unicité (fk_id_utilisateur, fk_id_objet)
```

### 6.4 Modèle Physique de Données (MPD)

Le MPD correspond directement au script SQL de création des tables (`CREATE_TABLES_SQL`
dans `model/database.py`), avec les types PostgreSQL, les contraintes `NOT NULL`,
`UNIQUE`, et les clés étrangères avec leur politique de suppression (`ON DELETE CASCADE`
ou `ON DELETE SET NULL` selon le cas).

📎 Insérer ici : `RNCP/3. Architecture de données/MPD.png`

### 6.5 Dictionnaire de données

**CATEGORIE**

| Champ | Type | Contrainte | Description |
|---|---|---|---|
| id_categorie | SERIAL | Clé primaire | Identifiant unique de la catégorie |
| nom_categorie | TEXT | NOT NULL, UNIQUE | Nom de la catégorie (Planète, Galaxie, Constellation...) |

**UTILISATEUR**

| Champ | Type | Contrainte | Description |
|---|---|---|---|
| id_utilisateur | SERIAL | Clé primaire | Identifiant unique |
| pseudo | TEXT | NOT NULL, UNIQUE | Pseudonyme affiché publiquement |
| nom | TEXT | NOT NULL | Nom de famille |
| prenom | TEXT | NOT NULL | Prénom |
| email | TEXT | NOT NULL, UNIQUE | Adresse email, identifiant de connexion |
| mot_de_passe_hash | TEXT | NOT NULL | Hash bcrypt du mot de passe (jamais le mot de passe en clair) |
| genre | TEXT | CHECK (homme/femme/autre/non_precise) | Genre déclaré, optionnel |
| photo_profil | TEXT | DEFAULT avatar générique | Chemin vers la photo de profil |
| date_inscription | TIMESTAMP | NOT NULL, DEFAULT NOW() | Date de création du compte |
| est_actif | BOOLEAN | DEFAULT TRUE | Compte actif ou désactivé par un administrateur |

**OBJET_CELESTE**

| Champ | Type | Contrainte | Description |
|---|---|---|---|
| id_objet | SERIAL | Clé primaire | Identifiant unique |
| nom_fr | TEXT | NOT NULL, UNIQUE | Nom en français |
| nom_scientifique | TEXT | / | Nom scientifique/latin, optionnel |
| description | TEXT | NOT NULL | Texte descriptif de l'objet |
| distance_al | REAL | / | Distance en années-lumière, optionnel |
| url_image | TEXT | / | Chemin ou URL de l'image |
| date_publication | DATE | NOT NULL | Date d'ajout au catalogue |
| fk_id_categorie | INTEGER | Clé étrangère → CATEGORIE, NOT NULL, ON DELETE CASCADE | Catégorie de l'objet |
| fk_id_utilisateur | INTEGER | Clé étrangère → UTILISATEUR, ON DELETE SET NULL | Utilisateur à l'origine de la proposition acceptée (traçabilité) |

**ADMINISTRATEUR**

| Champ | Type | Contrainte | Description |
|---|---|---|---|
| id_admin | SERIAL | Clé primaire | Identifiant unique |
| pseudo | TEXT | NOT NULL, UNIQUE | Identifiant de connexion admin |
| mot_de_passe_hash | TEXT | NOT NULL | Hash bcrypt du mot de passe |
| nom | TEXT | / | Nom de famille |
| prenom | TEXT | / | Prénom |
| email | TEXT | UNIQUE | Adresse email |

**PROPOSITION**

| Champ | Type | Contrainte | Description |
|---|---|---|---|
| id_proposition | SERIAL | Clé primaire | Identifiant unique |
| nom_fr | TEXT | NOT NULL | Nom en français proposé |
| nom_scientifique | TEXT | / | Nom scientifique proposé, optionnel |
| description | TEXT | NOT NULL | Texte descriptif proposé |
| url_image | TEXT | / | Image jointe à la proposition |
| fk_id_categorie | INTEGER | Clé étrangère → CATEGORIE, NOT NULL | Catégorie proposée |
| fk_id_utilisateur | INTEGER | Clé étrangère → UTILISATEUR, NOT NULL, ON DELETE CASCADE | Auteur de la proposition |
| statut | TEXT | CHECK (en_attente/accepte/refuse/modifie), DEFAULT en_attente | État de traitement |
| commentaire_admin | TEXT | / | Motif de refus ou de modification laissé par l'admin |
| date_proposition | TIMESTAMP | NOT NULL, DEFAULT NOW() | Date de soumission |
| date_traitement | TIMESTAMP | / | Date de validation ou de refus |
| notif_lue | BOOLEAN | DEFAULT FALSE | Notification vue par l'utilisateur proposant |

**SAISIR** (table de traçabilité, clé primaire composite)

| Champ | Type | Contrainte | Description |
|---|---|---|---|
| fk_id_admin | INTEGER | Clé primaire composite, clé étrangère → ADMINISTRATEUR | Administrateur ayant saisi ou validé l'objet |
| fk_id_objet | INTEGER | Clé primaire composite, clé étrangère → OBJET_CELESTE | Objet céleste concerné |
| date_saisie | TIMESTAMP | NOT NULL | Date de la saisie ou de la validation |

**FAVORI**

| Champ | Type | Contrainte | Description |
|---|---|---|---|
| id_favori | SERIAL | Clé primaire | Identifiant unique |
| fk_id_utilisateur | INTEGER | Clé étrangère → UTILISATEUR, ON DELETE CASCADE | Utilisateur ayant ajouté le favori |
| fk_id_objet | INTEGER | Clé étrangère → OBJET_CELESTE, ON DELETE CASCADE | Objet mis en favori |
| date_ajout | TIMESTAMP | NOT NULL, DEFAULT NOW() | Date d'ajout aux favoris |

La paire (`fk_id_utilisateur`, `fk_id_objet`) est contrainte `UNIQUE`, donc un même
utilisateur ne peut pas ajouter deux fois le même objet à ses favoris.

---

## 7. Composants d'accès aux données SQL et NoSQL

### 7.1 Vue d'ensemble

Toute la logique d'accès aux données est isolée dans le dossier `model/`. Aucune requête
SQL ou NoSQL n'apparaît dans les fichiers du Controller. Deux modules principaux :

| Fichier | Rôle |
|---|---|
| `model/database.py` | Connexion PostgreSQL (`psycopg2`) et toutes les fonctions CRUD relationnelles |
| `model/mongo_utils.py` + `comment_service.py` | Connexion MongoDB (`pymongo`) et logique des commentaires imbriqués |

Je n'utilise aucun ORM : les requêtes SQL sont écrites directement avec `psycopg2`, et les
documents MongoDB sont manipulés directement avec `pymongo`, pour rester au plus près du
langage propre à chaque base.

### 7.2 Accès aux données relationnelles (PostgreSQL / psycopg2)

Chaque fonction ouvre sa connexion, exécute sa requête via `RealDictCursor` (résultat sous
forme de dictionnaire, directement exploitable dans les templates), puis la referme dans
un bloc `finally`. Exemple sur la lecture d'un objet céleste avec ses jointures
(`get_object_by_id`, dans `model/database.py`) :

📎 Insérer ici : `RNCP/Capture/carbon_get_object_by_id.png`

Deux autres points à noter sur les fonctions d'accès :

- **Écriture sécurisée** : chaque fonction qui modifie la base utilise `try` / `commit`,
  `except` / `rollback`, `finally` / `close`, pour ne jamais laisser la base dans un état
  à moitié modifié en cas d'erreur (ex. `traiter_proposition()`, qui met à jour la
  proposition, crée l'objet et trace la saisie en une seule fois, tout ou rien).
- **Une seule requête pour plusieurs objets** : les compteurs de favoris du catalogue sont
  récupérés en une seule requête groupée (`get_favoris_counts()`) plutôt qu'une requête par
  objet, ce qui évite de multiplier les allers-retours vers la base.

### 7.3 Accès aux données NoSQL (MongoDB / pymongo)

La collection `commentaires` stocke un document par objet céleste, contenant l'arbre
complet des commentaires et de leurs réponses imbriquées :

📎 Insérer ici : `RNCP/Capture/carbon_document_commentaires.png`

Ce système convient bien à une discussion avec des réponses imbriquées, qui peuvent aller
plus ou moins profond. Avec une base relationnelle classique, il aurait fallu une table qui
se référence elle-même et des requêtes bien plus compliquées à écrire. Ici,
`CommentaireService` récupère le document, modifie l'arbre des commentaires directement en
mémoire (pour ajouter une réponse ou supprimer un commentaire, peu importe à quel niveau il
se trouve), puis réenregistre tout le document avec `update_one(..., upsert=True)`. Comme
les documents restent petits, cette solution reste simple et suffit largement pour ce
projet.

### 7.4 Sécurité des accès aux données

J'applique plusieurs bonnes pratiques de sécurité sur l'accès aux données, illustrées ici
par les fonctions de hashage et la récupération d'un administrateur (`model/database.py`) :

📎 Insérer ici : `RNCP/Capture/carbon_securite_acces_donnees.png`

- **Requêtes paramétrées** : toutes les requêtes SQL passent par des paramètres `%s`
  gérés par `psycopg2` (jamais de texte SQL construit à la main avec des f-strings ou des
  additions de chaînes), ce qui empêche les injections SQL.
- **Mots de passe hashés** : les mots de passe sont hashés avec `bcrypt` (fonctions
  `hash_password()` / `check_password()`), aussi bien pour les comptes utilisateurs que
  pour les comptes admin. Le mot de passe en clair n'est jamais stocké ni écrit dans les
  logs.
- **Séparation stricte des rôles** : `UTILISATEUR` et `ADMINISTRATEUR` sont deux tables
  complètement séparées. Un compte admin ne peut pas avoir de favoris ni de propositions,
  aucune fonction ne relie `ADMINISTRATEUR` à `FAVORI` ou `PROPOSITION`. Cette séparation
  est donc directement dans la base, pas juste vérifiée dans le code.
- **Gestion des erreurs** : chaque fonction qui accède à la base est entourée d'un
  `try/except`. En cas d'erreur, elle l'enregistre côté serveur et renvoie une valeur
  neutre (liste vide, `None`, `False`) plutôt que de laisser une erreur SQL brute
  remonter jusqu'à la page.

---

## 8. Interfaces et composants métier

### 8.1 Vue d'ensemble

Le Controller est organisé en sept blueprints Flask (`main_routes`, `auth_bp`, `user_bp`,
`admin_routes`, `chatbot_routes`, `comment_routes`, `skymap_routes`). Chacun reçoit la
requête HTTP, vérifie que l'utilisateur a le droit de faire l'action demandée, appelle le
Model pour aller chercher ou modifier les données, puis choisit quelle page renvoyer. Les
templates Jinja2, eux, ne font que de l'affichage : je n'y mets aucune logique, juste des
conditions simples pour montrer ou cacher un élément (par exemple le bouton "Modifier",
visible seulement si l'utilisateur est propriétaire de la ressource). Un exemple simple qui
résume ce fonctionnement (`toggle_favori_route`, dans `controller/user_bp.py`) :

📎 Insérer ici : `RNCP/Capture/carbon_toggle_favori_route.png`

### 8.2 Développement front-end (CP2)

Pour l'affichage, j'utilise des templates **Jinja2** (le rendu se fait côté serveur),
**Tailwind CSS** (des classes toutes prêtes, je n'écris presque pas de CSS moi-même), un
peu de **JavaScript** pur pour les quelques interactions qui n'ont pas besoin de recharger
la page (ajouter ou retirer un favori en AJAX, par exemple), et **Three.js** pour le rendu
3D du système solaire.

Les couleurs et la police sont les mêmes partout grâce aux couleurs Tailwind
personnalisées : fond bleu nuit très sombre (`#000525`), orange en couleur d'accent
(`#ff8811`), texte en lavande pâle (`#e0e6f7`), et la police **Inter** sur tout le site.

Pour que ça s'adapte bien à tous les écrans, j'ai d'abord pensé l'affichage pour mobile,
puis j'ai ajouté des règles pour les écrans plus larges avec les préfixes Tailwind (`md:`,
`lg:`, `xl:`) sur les pages les plus importantes. La grille du catalogue, par exemple,
passe d'une colonne sur mobile à quatre colonnes sur grand écran :

📎 Insérer ici : `RNCP/Capture/carbon_catalogue_responsive.png` (extrait de
`templates/catalogue.html`, lignes 60-84 : grille responsive, `loading="lazy"`,
attribut `alt`, image de repli)

📎 Insérer ici : `RNCP/Capture/responsive_desktop_mobile.png` (site en vrai, vue
bureau et vue mobile côte à côte)

**Accessibilité (RGAA).** J'ai fait passer un audit Lighthouse sur une fiche d'objet
céleste : score de **91/100**, 18 vérifications automatiques passées. Il reste deux points
à améliorer, que j'ai repérés mais pas encore corrigés : le contraste de certains éléments
secondaires, et des liens qui se distinguent du texte autour uniquement par leur couleur,
sans soulignement ni autre signe visuel.

📎 Insérer ici : `RNCP/Capture/lighthouse_accessibility.png`

### 8.3 Développement back-end / composants métier (CP3)

Plutôt que d'écrire toute la logique métier directement dans les routes du Controller, je
l'ai mise dans des classes à part, chacune dédiée à une tâche précise : `CommentaireService`
(qui lit et modifie l'arbre de commentaires MongoDB) et `AstroIAChatbot` (qui valide les
messages envoyés au chatbot, prépare le contexte envoyé à l'API Gemini, et nettoie la
réponse reçue). Cette deuxième classe vient d'ailleurs d'un refactor : au départ cette
logique était directement dans la route, et je l'ai sortie à part pour séparer ce qui
concerne le métier de ce qui concerne le HTTP.

📎 Insérer ici : `RNCP/Capture/carbon_astroia_chatbot.png` (`model/chatbot_service.py`,
méthode `ask()`, lignes 34-60 : validation des entrées, exceptions typées,
délégation à l'API, nettoyage de la sortie)

Chaque classe vérifie elle-même ce qu'elle reçoit et renvoie une erreur précise si besoin
(`ValueError` si le message est vide ou trop long, `RuntimeError` si l'IA ne renvoie rien
d'utilisable). Le Controller n'a plus qu'à transformer ça en réponse HTTP : la classe
métier, elle, ne connaît ni Flask ni le HTTP.

Le parcours de proposition d'objet illustre bien l'articulation Controller/Model :
un utilisateur propose un objet (`user_bp.proposer_objet`), qui reste en attente
jusqu'à ce qu'un administrateur le traite (`admin_bp.traiter_proposition_route`) :

📎 Insérer ici : `RNCP/Capture/carbon_traiter_proposition_route.png`

Le Controller se contente de lire le formulaire et de tout déléguer au Model, via la
fonction `traiter_proposition()` : mise à jour du statut de la proposition, création de
l'objet céleste si elle est acceptée, et enregistrement de l'administrateur qui a traité
la demande. Le droit de traiter une proposition, lui, est vérifié par le décorateur
`@admin_required`.

J'ai documenté chaque classe de service avec des docstrings qui expliquent ce qu'elle fait
et les exceptions qu'elle peut renvoyer. Je les ai aussi couvertes chacune par leur propre
suite de tests, sans dépendre de rien d'extérieur grâce à des mocks : 15 tests pour
`CommentaireService`, 6 pour `AstroIAChatbot`, tous passants.

Pour les règles de nommage, j'ai essayé de rester cohérent sur tout le projet : tables et
colonnes PostgreSQL en français, en MAJUSCULES pour les noms de table (`UTILISATEUR`,
`OBJET_CELESTE`) et en `snake_case` pour les colonnes, avec un préfixe `fk_` systématique
pour toute clé étrangère. Côté Python, `snake_case` pour les fonctions et variables,
`PascalCase` pour les classes (`CommentaireService`, `AstroIAChatbot`). Ces conventions
sont vérifiées automatiquement à chaque push par `flake8` (conformité PEP8), plutôt que de
compter juste sur moi pour les respecter.

### 8.4 Commentaires : un point d'entrée pour deux types de comptes

Les commentaires sont ouverts aux utilisateurs comme aux administrateurs, alors que ce
sont deux systèmes de connexion différents : un compte utilisateur identifié par
`user_id`, un compte administrateur identifié par `admin_id`, stockés dans deux tables
séparées de la base PostgreSQL. Plutôt que de dupliquer les routes, `comment_routes.py`
identifie l'auteur une seule fois, au même endroit :

📎 Insérer ici : `RNCP/Capture/carbon_identite_auteur.png`

Le reste de la route (`_ajouter`) n'a pas besoin de savoir qui écrit le commentaire : il
transmet simplement les informations récupérées (identifiant, pseudo, rôle) à
`CommentaireService.ajouter_commentaire()`.

### 8.5 Sécurité des interfaces

Deux exemples de décorateurs d'accès, utilisés sur toutes les routes qui en ont besoin
(`controller/user_bp.py` et `controller/admin_routes.py`) :

📎 Insérer ici : `RNCP/Capture/carbon_decorateurs_acces.png`

- **Décorateurs d'accès** : `login_required` (espace utilisateur) et `admin_required`
  (espace admin) vérifient si la session existe et redirigent vers la bonne page de
  connexion si ce n'est pas le cas, pour éviter de répéter ce contrôle dans chaque route.
- **Upload de fichiers encadré** : l'extension est vérifiée avec une liste d'extensions
  autorisées (`ALLOWED_EXTENSIONS`), et le nom du fichier est nettoyé par
  `secure_filename()` (Werkzeug) avant d'être écrit sur le serveur, aussi bien pour les
  photos de profil que pour les images de proposition.
- **Validation côté serveur** : chaque formulaire est revalidé côté Controller (champs
  obligatoires, longueur du mot de passe, correspondance de confirmation). La validation
  HTML côté client rend juste les choses plus agréables à utiliser, elle ne garantit rien
  en soi.

---

## 9. Sécurité

La sécurité n'est pas traitée dans un module à part chez AstroLearn, elle est présente au
fil des sections précédentes. Cette partie sert surtout de synthèse et couvre les points
qui n'ont pas encore été détaillés.

### 9.1 Récapitulatif des mesures déjà présentées

| Risque | Mesure |
|---|---|
| Injection SQL | Requêtes paramétrées (`%s` via `psycopg2`), jamais de concaténation de chaînes dans une requête |
| Mots de passe en clair | Hachage `bcrypt` (avec sel intégré) sur les deux tables de comptes, utilisateurs et administrateurs |
| Élévation de privilège | Tables `UTILISATEUR` et `ADMINISTRATEUR` séparées en base, sans passerelle au niveau du schéma |
| Upload malveillant | Extension de fichier vérifiée par liste blanche, nom de fichier nettoyé par `secure_filename()` (Werkzeug) |
| Accès non autorisé à une route | Décorateurs `login_required` (espace utilisateur) et `admin_required` (espace admin), qui vérifient la session avant d'exécuter la route |

### 9.2 Protection CSRF

Toutes les requêtes qui modifient une donnée (formulaires HTML et appels JSON en AJAX,
comme l'ajout ou le retrait d'un favori) sont protégées par `Flask-WTF` :

```python
csrf = CSRFProtect(app)
```

Cette protection est activée pour toute l'application dans `app.py`, et demande un jeton
valide sur chaque requête `POST`. Ce jeton est ajouté automatiquement dans les formulaires
Jinja2, et envoyé à la main dans l'en-tête `X-CSRFToken` pour les appels AJAX.

### 9.3 Cookies de session

Les cookies de session Flask sont configurés avec trois attributs de sécurité :

```python
SESSION_COOKIE_SAMESITE='Lax',
SESSION_COOKIE_SECURE=True,
SESSION_COOKIE_HTTPONLY=True
```

`HTTPONLY` empêche le cookie d'être lu par du JavaScript, ce qui protège contre le vol de
session si le site a une faille XSS. `SECURE` oblige à ce qu'il ne soit envoyé qu'en
HTTPS. Et `SAMESITE=Lax` limite son envoi quand la requête vient d'un autre site.

### 9.4 Gestion des secrets

Aucun secret, que ce soit un mot de passe base de données, une clé Flask ou une clé
d'API, n'est écrit en dur dans le code source. Tout est chargé depuis un fichier `.env`
(non versionné, listé dans `.gitignore`) via `python-dotenv`. La configuration refuse
même de démarrer sans `SECRET_KEY` définie, plutôt que d'utiliser une valeur par défaut
connue :

```python
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY manquante : définis-la dans le fichier .env. ...")
```

Même logique pour le compte administrateur initial : il n'est créé que si
`ADMIN_PSEUDO` et `ADMIN_PASSWORD` sont explicitement définis dans le `.env`. Sans ça,
aucun admin n'est créé automatiquement, pour éviter un couple identifiant/mot de passe
par défaut connu de tous.

### 9.5 HTTPS

Le trafic en production est chiffré de bout en bout : certificat TLS Let's Encrypt,
obtenu et renouvelé automatiquement par Certbot (timer systemd dédié), configuré sur
le reverse proxy nginx, qui gère le HTTPS avant de transmettre la requête à
l'application.

### 9.6 Référentiels suivis et RGPD

Je m'appuie sur des référentiels reconnus plutôt que d'improviser mes choix de
sécurité. Le Top 10 OWASP guide plusieurs décisions déjà présentées dans ce dossier :
requêtes paramétrées contre les injections SQL, hachage bcrypt contre les mots de
passe faibles ou mal protégés, et validation systématique des données côté serveur. Je
suis aussi les recommandations de l'ANSSI sur la robustesse des mots de passe et le
chiffrement des échanges en HTTPS.

Côté RGPD, je limite la collecte aux données nécessaires au fonctionnement du site :
pseudo, nom, prénom, email et mot de passe à l'inscription, une photo de profil
optionnelle. Un utilisateur peut modifier son profil ou demander la suppression de son
compte, et aucune donnée n'est revendue à des tiers. Une page de mentions légales
(`/legal`) est accessible depuis le pied de page du site.

---

## 10. Gestion de projet

### 10.1 Méthodologie

Comme AstroLearn est un projet individuel, une organisation Scrum complète (sprints
fixes, cérémonies, équipe) n'aurait pas eu beaucoup de sens. J'ai plutôt repris les
principes qui restent utiles à un seul développeur : une liste de fonctionnalités
priorisées, une livraison itérative par lot fonctionnel plutôt qu'un développement
monolithique, et un retour régulier au cahier des charges, qui a d'ailleurs évolué en
cours de route à mesure que le projet s'enrichissait.

### 10.2 Outillage de suivi

- **Dépôt Git** hébergé sur GitHub, historique complet et public, avec un `.gitignore`
  excluant l'environnement virtuel, les uploads utilisateurs et les fichiers sensibles.
- **Tableau Kanban** (GitHub Projects) pour suivre l'avancement des fonctionnalités
  (à faire / en cours / terminé) :

📎 Insérer ici : `RNCP/Capture/KanBan GitHub.png`

- **Intégration continue** (GitHub Actions) : à chaque push, un job automatique
  vérifie la qualité du code (`flake8`, `black`) et exécute la suite de tests
  (`pytest`) avant qu'un changement soit considéré comme validé.

### 10.3 Convention de commits et de branches

Mes commits suivent une convention proche de *Conventional Commits* (`feat:`, `fix:`,
`refactor:`, `chore:`, `docs:`), pour garder un historique lisible et pouvoir repérer
rapidement la nature d'un changement. La branche `main` reçoit aussi des pull requests
automatiques de **Dependabot**, qui signale et propose la mise à jour des dépendances
présentant une faille de sécurité connue.

📎 Insérer ici : `RNCP/Capture/github_commits.png`

### 10.4 Journal de bord

Jalons principaux du projet :

| Période | Étape |
|---|---|
| Déc. 2025 | Socle initial : maquette, chatbot connecté à l'API Gemini, carte 3D Three.js |
| Mars 2026 | Migration vers PostgreSQL, refonte en MVC typée, comptes utilisateurs, favoris, dashboard, espace admin |
| Avr. 2026 | Mise en conformité qualité (Flake8/Black), tests Pytest, mise en place de la CI/CD |
| Juil. 2026 | Revue de code, protection CSRF, accessibilité RGAA, conteneurisation Docker, commentaires imbriqués sur MongoDB |
| Fin juil. 2026 | Documentation (déploiement, veille, plan de tests) et mise en production sur le VPS |

---

## 11. Plan de tests

### 11.1 Stratégie de test

J'ai combiné quatre niveaux de test : des **tests unitaires** (`pytest`, avec mocks) sur
la logique métier, sans dépendre de rien d'extérieur, des **tests d'intégration**
(`app.test_client()`) sur le comportement HTTP réel, des **tests de sécurité** ciblés
(hachage bcrypt, rejet des requêtes sans jeton CSRF), et une **campagne fonctionnelle
manuelle** sur les parcours qui n'ont pas encore de test automatisé dédié. Les tests
automatisés tournent en intégration continue (GitHub Actions) à chaque push, dans le
même job qui vérifie aussi la qualité et le formatage du code (`flake8`, `black`).

📎 Insérer ici : `RNCP/Capture/github_actions_pytest.png` (fin du log `pytest`, résumé
`33 passed, 3 warnings in 2.15s`)

### 11.2 Couverture automatisée

| Domaine | Type | Fichier(s) | Résultat |
|---|---|---|---|
| Hachage des mots de passe, CSRF | Unitaire + intégration | `test_security.py`, `test_csrf.py` | ✅ 8/8 |
| Chatbot AstroIA | Unitaire (mocké) | `test_chatbot_service.py` | ✅ 6/6 |
| Commentaires imbriqués (NoSQL) | Unitaire (mocké) | `test_comment_service.py` | ✅ 15/15 |
| Connexion BDD / catégories | Intégration (PostgreSQL réel) | `test_db.py`, `test_db_connexion.py` | ✅ |
| Mapping catégories NASA, validations | Unitaire | `test_logic.py`, `test_validation.py` | ✅ |
| API Gemini réelle | Manuel, hors CI (quota payant) | `test_astroia.py` | ⚠️ manuel |

Certaines routes admin à faible fréquence d'usage (modification/suppression d'un
compte admin, traduction FR/EN, ingestion du catalogue NASA) n'ont pas encore de test
dédié. C'est un point identifié et priorisé selon le risque, sachant que ces routes
n'impactent pas les données d'un autre utilisateur qu'un administrateur.

### 11.3 Campagne fonctionnelle manuelle (30/07/2026)

Exécutée sur l'environnement Docker, base de données réinitialisée par
`seed_jeu_essai.py`. Elle couvre les parcours de bout en bout : inscription,
connexion (utilisateur et admin), favoris, proposition d'objet, traitement d'une
proposition, ajout d'objet et suppression d'un compte utilisateur.
**14/14 vérifications conformes**.

### 11.4 Jeu d'essai détaillé (commentaires imbriqués)

J'ai choisi ce test comme le plus représentatif, parce qu'il combine PostgreSQL
(identité utilisateur/admin), MongoDB (arbre de commentaires), la sécurité (CSRF, double
système de session) et la couche de service `CommentaireService`, qui centralise toute la
logique d'ajout, de réponse et de suppression dans l'arbre de commentaires, à n'importe
quel niveau.

| Scénario | Valeurs saisies | Résultat attendu |
|---|---|---|
| Commentaire racine par un utilisateur | Objet Mars (id 1), `jeu_essai_user`, « Superbe vue sur Mars... » | Nœud créé, `est_admin: false`, `utilisateur_id` renseigné |
| Réponse d'un administrateur (profondeur 1) | Réponse au commentaire ci-dessus | Nœud imbriqué dans `reponses[]`, `est_admin: true`, `utilisateur_id: null` |
| Réponse de l'utilisateur à l'admin (profondeur 2) | « Avec plaisir, hâte d'en savoir plus... » | Arbre à 3 nœuds, imbrication à 2 niveaux |
| Consultation du dashboard admin (1ère puis 2e visite) | / | Badge non-lus : 3 puis 0 |
| Suppression du commentaire racine par l'admin | / | Les 2 réponses disparaissent avec lui (cascade) |

**Résultat : 16/16 vérifications conformes** (exécution du 30/07/2026).

J'ai rencontré deux écarts en écrivant les vérifications, mais aucun n'était un vrai
bug de l'application. Le premier : l'apostrophe du texte de profondeur 2 apparaissait
échappée (`&#39;`) dans le HTML. En fait c'est le comportement anti-XSS normal de
Jinja2, donc j'ai simplement corrigé le test en conséquence. Le second : le badge
non-lus partageait ses classes CSS avec le badge « propositions en attente », ce qui
faisait remonter le mauvais badge lors de la vérification. Une vérification directe via
`count_non_lus()` en base a confirmé que ce n'était pas un bug, juste un test mal ciblé.
Je l'ai corrigé en ciblant précisément l'onglet Commentaires.

### 11.5 Sécurité des tests

- Aucun secret réel en CI : PostgreSQL et `SECRET_KEY` jetables, générés dans le
  workflow lui-même.
- Le test contre l'API Gemini réelle est exclu de la CI (clé et quota payant).
- Les identifiants admin utilisés pour la campagne manuelle sont des valeurs
  jetables, retirées du `.env` après la campagne.

---

## 12. Déploiement

### 12.1 Environnements

| Environnement | Usage | Base de données |
|---|---|---|
| Local (dev) | Développement quotidien | PostgreSQL + MongoDB locaux, ou via `docker compose` |
| CI (GitHub Actions) | Vérification à chaque push (vérification du code + tests automatisés) | PostgreSQL temporaire, supprimé à la fin de chaque exécution |
| Production (VPS OVH) | `https://astrolearn.nayaweb.fr` | PostgreSQL et MongoDB installés sur le serveur, avec authentification |

Docker n'est utilisé qu'en local et en CI, pas en production. Dans l'idéal, la meilleure
pratique serait d'utiliser le même Docker partout, du développement jusqu'à la
production, pour être sûr de tester la même chose que ce qui tourne en ligne. Je ne l'ai
pas fait : la production est installée directement sur le VPS, sans Docker, parce que
gérer un seul serveur à la main reste plus simple à mon échelle, un seul développeur et
un seul serveur, plutôt que d'ajouter Docker en plus. C'est un choix que j'assume, pas un
oubli : sur un projet plus gros, avec plusieurs serveurs, je ferais autrement.

### 12.2 Environnement de travail

**Outils de développement installés.** Python 3.12 avec un environnement virtuel dédié
(`venv`) pour isoler les dépendances du projet de celles du système, gérées via
`requirements.txt` et installées par `pip`. Git pour le suivi de version en local.

**Outils de gestion de version et de collaboration.** Le dépôt est hébergé sur
**GitHub**, avec un historique de commits public et un tableau Kanban (GitHub Projects)
pour suivre l'avancement des fonctionnalités. **Dependabot** est activé pour signaler
automatiquement les dépendances Python présentant une faille de sécurité connue.

**Conteneurs implémentant les services requis.** Un `docker-compose.yml` définit trois
services pour reproduire l'environnement de production en local, sans rien installer
sur la machine hôte :

| Service | Image | Port hôte | Rôle |
|---|---|---|---|
| `db` | `postgres:16` | 5433 | Base relationnelle (décalé de 5432 pour ne pas entrer en conflit avec un PostgreSQL local existant) |
| `mongo` | `mongo:7` | 27018 | Base NoSQL des commentaires (décalé de 27017 pour la même raison) |
| `web` | Build local (`Dockerfile`) | 5000 | Application Flask/Gunicorn, dépend de `db` et `mongo` (via `depends_on` + `healthcheck`) |

`docker compose up --build` construit et démarre les trois services. Le schéma
PostgreSQL est créé automatiquement au premier démarrage de l'application.

**Documentation technique comprise.** Le `README.md` du dépôt documente, en français,
les deux parcours d'installation (avec ou sans Docker), la liste des variables
d'environnement requises (`DB_PASSWORD`, `SECRET_KEY`, `GEMINI_API_KEY`) et la stack
technique complète. L'idée, c'est qu'un environnement de travail identique puisse être
reconstitué par n'importe qui à partir du dépôt seul.

### 12.3 Préparation du serveur et nom de domaine

Avant de pouvoir déployer quoi que ce soit, j'ai dû préparer le serveur et le nom de
domaine.

Le VPS tourne sous **Ubuntu 22.04 LTS**, avec Python 3.12 et un environnement virtuel
dédié, PostgreSQL et MongoDB installés directement dessus, nginx comme reverse proxy, et
systemd pour gérer le service de l'application.

Pour le nom de domaine, `astrolearn.nayaweb.fr` est un sous-domaine de `nayaweb.fr`, mon
domaine personnel. J'ai créé un enregistrement DNS de type **A**, avec pour nom
`astrolearn` et pour valeur l'adresse IP publique du VPS OVH, pour que ce sous-domaine
pointe directement vers le serveur.

### 12.4 Premier déploiement

Une fois le serveur prêt, l'installation initiale s'est faite en plusieurs étapes :
récupération du code et des dépendances Python, création de la base PostgreSQL et de
son utilisateur dédié, installation de MongoDB avec un utilisateur applicatif limité à
la base `astrolearn_nosql`, remplissage du fichier `.env` de production, déclaration du
service systemd qui lance l'application avec Gunicorn, puis configuration de nginx en
reverse proxy avec le certificat HTTPS.

Preuve que la base PostgreSQL et son utilisateur dédié existent bien sur le serveur :

📎 Insérer ici : capture terminal, résultat de `sudo -u postgres psql -c "\l"` et `\du`
sur le VPS

Côté MongoDB, l'authentification est active et l'utilisateur applicatif est limité à la
base `astrolearn_nosql` :

📎 Insérer ici : capture terminal, résultat de `cat /etc/mongod.conf` (section
`security`) et de la liste des utilisateurs Mongo

Le service systemd qui fait tourner l'application avec Gunicorn :

📎 Insérer ici : capture terminal, résultat de `cat /etc/systemd/system/astrolearn.service`

Et la configuration nginx qui expose l'application en HTTPS :

📎 Insérer ici : capture terminal, résultat de `cat /etc/nginx/sites-available/astrolearn`

Une fois ces étapes faites, l'application est en ligne, et le schéma PostgreSQL se crée
automatiquement au premier démarrage.

### 12.5 Architecture de production

L'application tourne derrière **Gunicorn** (3 workers), géré comme service **systemd**
avec redémarrage automatique en cas de plantage, lui-même exposé via un reverse proxy
**nginx** qui gère le HTTPS (certificat Let's Encrypt / Certbot, renouvelé
automatiquement). Les bases PostgreSQL et MongoDB sont installées directement sur le
serveur. MongoDB est en écoute uniquement locale, avec un utilisateur applicatif dédié
restreint en lecture/écriture à la seule base `astrolearn_nosql`, distinct du compte
administrateur du serveur MongoDB : c'est le principe du moindre privilège.

### 12.6 Mise à jour de l'application

Chaque mise à jour passe par [`deploy.sh`](../deploy.sh), qui automatise `git pull`,
l'installation des dépendances, le redémarrage du service et un test de santé HTTP
(`curl` sur la page d'accueil). Le script s'arrête au premier échec (`set -euo
pipefail`), pour ne jamais laisser la production dans un état intermédiaire silencieux.

### 12.7 Rollback

En cas de problème : retour à un commit stable (`git checkout <hash>`), réinstallation
des dépendances et redémarrage du service. Si une migration PostgreSQL est en cause,
restauration de la dernière sauvegarde (`pg_restore`).

### 12.8 Vérifications post-déploiement

```bash
sudo systemctl status astrolearn.service --no-pager
sudo journalctl -u astrolearn.service -n 50 --no-pager
curl -I https://astrolearn.nayaweb.fr/
```

📎 Insérer ici : `RNCP/Capture/curl_https.png` (sortie réelle de `curl -I
https://astrolearn.nayaweb.fr/`, code 200, en-têtes HTTPS)

---

## 13. Démarche DevOps

### 13.1 Pipeline d'intégration continue

Un unique job GitHub Actions (`.github/workflows/ci.yml`) se déclenche à chaque push,
sur toutes les branches, pas seulement `main`, pour détecter un problème avant qu'il
n'atteigne la branche principale. Il enchaîne la vérification du code (`flake8`), du
formatage (`black --check`), puis exécute la suite `pytest` (33 tests) contre un
PostgreSQL temporaire lancé pour l'occasion, supprimé à la fin de chaque exécution.

### 13.2 Gestion des dépendances

Le dépôt a l'alerte de sécurité **Dependabot** activée : chaque dépendance
présentant une faille connue génère une pull request automatique de mise à jour. Le
correctif est ensuite appliqué directement par fusion de la PR, ou par mise à jour
manuelle de `requirements.txt` suivie de la clôture de la PR devenue inutile. C'est
d'ailleurs ce qui m'est arrivé en préparant cette section : plusieurs alertes étaient
restées ouvertes alors que les versions corrigées étaient déjà en place sur `main`. Je
les ai nettoyées via `@dependabot rebase`, qui ferme automatiquement la PR quand il
constate que le correctif est déjà appliqué.

📎 Insérer ici : `RNCP/Capture/dependabot_pr_closed.png` (PR `urllib3` fermée par
Dependabot avec le message « Looks like urllib3 is up-to-date now... »)

### 13.3 De l'intégration à la livraison

La CI est entièrement automatisée. Le déploiement, lui, reste **déclenché
manuellement** via le script `deploy.sh` (qui automatise l'installation des dépendances,
le redémarrage du service et un test de santé HTTP) plutôt que branché directement sur
la CI. C'est un choix que j'assume pour un projet solo : je préfère éviter de donner à
GitHub Actions un accès SSH permanent au serveur de production, et garder une validation
humaine avant chaque mise en ligne, parce que je n'ai pas d'outils de supervision et de
rollback assez solides pour faire de la livraison continue sans surveillance humaine.

---

## 14. Veille technologique et sécurité

### 14.1 Sources et méthode

Cette veille porte sur l'infrastructure et les dépendances, à ne pas confondre avec la
veille applicative déjà présentée plus haut dans ce dossier. Je suis les alertes **GitHub
Dependabot**, les notes de version des outils utilisés (PostgreSQL, MongoDB, nginx,
Gunicorn, Certbot), les **alertes de sécurité Ubuntu** pour le système du VPS, et la
documentation officielle de GitHub Actions. Une mise à jour n'est appliquée qu'après avoir
vérifié qu'elle ne casse ni les tests automatisés ni la vérification du code. Les
correctifs du système, eux, sont appliqués avec `apt` lors des moments de maintenance
du VPS.

### 14.2 Mesures de sécurité issues de la veille

- **Dépendances Python obsolètes ou vulnérables** : détectées par les alertes
  Dependabot activées sur le dépôt, qui ouvrent une pull request automatique dès
  qu'une faille connue touche une dépendance ; le correctif n'est appliqué qu'après
  validation par la suite de tests et la vérification du code.
- **Moindre privilège sur MongoDB** : le compte que l'application utilise pour se
  connecter est limité au rôle `readWrite` sur la seule base `astrolearn_nosql`,
  différent du compte administrateur du serveur MongoDB, avec l'authentification
  SCRAM activée.
- **Isolation des tests d'intégration** : la suite de tests automatisés s'exécute
  contre un conteneur PostgreSQL temporaire, lancé uniquement pour l'exécution du job
  CI, jamais contre la base de production, pour ne pas exposer d'identifiants réels ni
  risquer d'altérer les données par accident.
- **Renouvellement automatique du certificat HTTPS** : le certificat TLS du domaine
  est géré par Certbot/Let's Encrypt, avec un renouvellement automatique programmé
  via un timer systemd dédié, pour ne pas dépendre d'un renouvellement manuel qui
  pourrait être oublié.

![Pull requests automatiques Dependabot](Capture/Capture%20d'écran%202026-08-17%20102429.png)

*Historique des pull requests automatiques ouvertes par Dependabot sur le dépôt
(idna, urllib3, python-dotenv, requests, werkzeug, flask).*

### 14.3 Scope de token GitHub Actions

En modifiant le pipeline CI, j'ai eu un push refusé par GitHub sur
`.github/workflows/ci.yml` : le token que j'utilisais n'avait pas le scope `workflow`,
obligatoire pour modifier des fichiers dans ce dossier. En cherchant dans la
documentation GitHub, j'ai compris que c'était une restriction voulue : un token sans
ce scope ne peut pas modifier le pipeline d'intégration continue, ce qui limite les
dégâts si jamais un token fuite un jour. J'ai ajouté ce scope une fois que j'ai compris
pourquoi il existait, plutôt que de chercher à le contourner.

### 14.4 Cookie `Secure` et client de test HTTP

En écrivant mes premiers tests d'intégration HTTP, j'ai rencontré une difficulté
récurrente : le paramètre `SESSION_COOKIE_SECURE=True`, qui empêche les cookies de
session Flask d'être envoyés en clair, fait que la bibliothèque `requests` **ignore
silencieusement** le cookie de session reçu quand le test tourne en simple HTTP, sans
certificat TLS. Son objet `Session` refuse tout simplement de garder un cookie marqué
`Secure` sur une connexion non chiffrée. Résultat, mes tests échouaient sans message
clair : redirection vers la page de connexion, comme si l'utilisateur n'avait jamais été
authentifié. En cherchant dans la documentation de `requests`, j'ai compris que c'était
un comportement normal de la bibliothèque, pas un défaut de mon application. La solution
que j'ai retenue : récupérer moi-même l'en-tête `Set-Cookie` de la réponse et le renvoyer
tel quel dans l'en-tête `Cookie` des requêtes suivantes, sans passer par la gestion
automatique des cookies du client de test.

---

## 15. Bilan

### 15.1 Bilan technique

Ce que j'ai livré va bien au-delà de ce que j'avais imaginé au départ. Du catalogue
statique prévu au début, le projet est devenu une application complète : comptes
utilisateurs réels, favoris, propositions modérées, commentaires imbriqués, espace
d'administration et mise en production documentée. L'architecture MVC, les deux bases
de données (SQL et NoSQL) et la CI ont bien tenu face à cette croissance, sans que j'aie
eu besoin de tout reconstruire.

### 15.2 Limites et pistes d'amélioration

- **Couverture de test incomplète** sur certaines routes admin à faible fréquence
  d'usage (modification/suppression d'un compte admin, traduction, ingestion NASA).
  C'est un point identifié lors de la rédaction du plan de tests, que je n'ai pas
  encore traité.
- **Déploiement manuel plutôt qu'automatisé** : un choix que j'assume pour un projet
  solo, mais une vraie livraison continue demanderait des outils de supervision et de
  rollback plus solides que ce que j'ai actuellement.
- **Suivi des dépendances relâché pendant plusieurs mois** : en préparant ce dossier,
  j'ai découvert plusieurs alertes Dependabot qui traînaient depuis longtemps et que
  j'ai corrigées, alors que j'aurais dû m'en occuper au fur et à mesure. J'en retiens
  une leçon sur la discipline de maintenance, pas seulement sur le développement de
  fonctionnalités.
- **Dette technique mineure identifiée mais non corrigée** : usage de
  `datetime.utcnow()` (déprécié), que j'ai repéré via un warning affiché par Pytest
  lors de l'exécution en CI.

### 15.3 Bilan personnel

Ce projet individuel m'a fait passer par l'intégralité d'un cycle de développement, de
l'analyse des besoins jusqu'à la mise en production. J'ai dû endosser tous les rôles
(conception, développement, tests, sécurité, déploiement) qui, dans une équipe, sont
habituellement répartis entre plusieurs personnes. Le développement s'est étalé sur
plusieurs mois, avec des périodes d'interruption entre décembre 2025 et juillet 2026,
ce qui m'a obligé à documenter mes choix au fur et à mesure plutôt que de compter sur ma
mémoire à court terme. Cette habitude m'a d'ailleurs directement servi pour rédiger ce
dossier.

---

## 16. Annexes

### 16.1 Liens

- Dépôt GitHub : `github.com/Aboubnan/AstroLearn`
- Application en production : `https://astrolearn.nayaweb.fr`
- Pipeline CI : `github.com/Aboubnan/AstroLearn/actions`

### 16.2 Glossaire

| Terme | Définition |
|---|---|
| MVC | Patron d'architecture séparant les données (Model), la présentation (View) et la logique de contrôle (Controller) |
| Blueprint (Flask) | Sous-module Flask regroupant un ensemble de routes liées (ex. `admin_bp`, `user_bp`) |
| ORM | Bibliothèque faisant correspondre des objets à des lignes de base de données (non utilisé ici, requêtes SQL directes via `psycopg2`) |
| CSRF | *Cross-Site Request Forgery*, falsification de requête contrée par un jeton unique par session |
| Bcrypt | Algorithme de hachage de mot de passe avec sel intégré, résistant aux attaques par force brute |
| CI/CD | Intégration continue / livraison continue : automatisation des vérifications (et, idéalement, du déploiement) à chaque changement de code |
| Document (MongoDB) | Unité de stockage NoSQL, équivalent d'une ligne SQL mais de structure arborescente et flexible |
| MCD / MLD | Modèle Conceptuel / Logique de Données, étapes de la méthode Merise pour concevoir une base relationnelle |
| WSGI | Interface standard entre un serveur web et une application Python (utilisée par Gunicorn pour faire tourner Flask) |
| Gunicorn | Serveur d'application WSGI qui exécute le code Flask en production |
| Reverse proxy (nginx) | Serveur qui reçoit les requêtes HTTPS en premier et les redirige vers l'application, sans exposer directement Gunicorn sur internet |
| systemd | Système de gestion des services sous Linux, utilisé pour démarrer et redémarrer l'application automatiquement |
| RGAA | Référentiel Général d'Amélioration de l'Accessibilité, les règles françaises d'accessibilité numérique |
| VPS | Serveur privé virtuel loué chez un hébergeur (ici OVH), sur lequel l'application est déployée |

### 16.3 Documentation technique complémentaire

Documents versionnés dans le dépôt, utilisés comme base de rédaction de ce dossier et
disponibles pour un niveau de détail supplémentaire : `README.md`, `DEPLOIEMENT.md`,
`PLAN_DE_TESTS.md`, `VEILLE_DEPLOIEMENT.md`.
