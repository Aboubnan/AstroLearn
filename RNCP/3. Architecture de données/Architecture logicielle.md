# Architecture logicielle — AstroLearn

## Choix du pattern MVC

AstroLearn est organisé selon le patron **MVC (Model-View-Controller)**, structuré en trois
dossiers distincts (`model/`, `templates/`, `controller/`). L'objectif est de séparer les
responsabilités pour que chaque couche ne dépende que de son rôle propre :

- **Model** (`model/`) : accès aux données, sans aucune connaissance de HTTP ni de HTML.
  Un seul point d'entrée pour lire ou écrire dans PostgreSQL (`database.py`) ou MongoDB
  (`mongo_utils.py`, `comment_service.py`).
- **View** (`templates/`) : les pages Jinja2 affichées à l'utilisateur. Aucune logique
  métier ici, uniquement de l'affichage.
- **Controller** (`controller/`) : reçoit les requêtes HTTP, appelle le Model pour obtenir
  ou modifier les données, sélectionne la View à retourner.

Cette séparation limite l'impact d'un changement : modifier l'apparence d'une page ne touche
que `templates/`, changer la structure d'une table ne touche que `model/`. C'est ce
découplage qui est recherché dans une architecture "en couches", plutôt qu'un empilement de
scripts qui mélangent requêtes SQL, logique métier et HTML dans le même fichier.

## Une persistance hybride : SQL et NoSQL

Le Model s'appuie sur deux bases de données distinctes, `astrolearn_db` (PostgreSQL) et
`astrolearn_nosql` (MongoDB), chacune choisie pour le type de données qu'elle héberge.

Le catalogue d'objets célestes, les comptes utilisateurs, les propositions et les favoris
sont des données **structurées et relationnelles** : un objet appartient à une catégorie,
un utilisateur possède des favoris, une proposition est rattachée à un auteur. Ces relations
sont fixes et bénéficient des contraintes d'intégrité d'un SGBD relationnel (clés étrangères,
`NOT NULL`, `UNIQUE`) — PostgreSQL est le choix naturel.

Les commentaires forment au contraire une arborescence de profondeur variable : un
commentaire peut recevoir des réponses, elles-mêmes commentables. Représenter cette structure
en SQL demanderait des jointures récursives et une gestion manuelle de la profondeur. Un
document MongoDB peut stocker un commentaire et ses réponses imbriquées tel quel, sans
jointure. MongoDB est donc réservé à ce seul usage, pas utilisé comme base généraliste.

## Découpage du Controller en blueprints

Le dossier `controller/` est divisé en sept fichiers, chacun correspondant à un domaine
fonctionnel : `main_routes.py` (pages publiques), `auth_bp.py` (connexion/inscription),
`user_bp.py` (espace utilisateur), `admin_routes.py` (administration), `chatbot_routes.py`
(assistant IA), `comment_routes.py` (commentaires), `skymap_routes.py` (système solaire 3D).

Ce découpage utilise le mécanisme des **Blueprints** de Flask : chaque fichier déclare ses
propres routes et est enregistré indépendamment dans `app.py`. Plutôt que d'avoir un seul
fichier de routes de plusieurs milliers de lignes, chaque domaine métier reste isolé,
lisible et modifiable sans risquer d'impacter les autres.

## Flux d'une requête

1. L'utilisateur envoie une requête HTTP (GET ou POST) au Controller.
2. Le Controller appelle les fonctions du Model concernées (lecture ou écriture en base).
3. Le Model exécute la requête SQL ou NoSQL et retourne le résultat.
4. Le Controller transmet les données à la View, qui génère le HTML final envoyé au
   navigateur.

Ce flux est illustré par le diagramme `Architecture MVC.png` de ce même dossier.
