# Cahier des Charges - Projet AstroLearn (V2)

**Thème :** Plateforme éducative sur l'astronomie (catalogue d'objets célestes, système
solaire 3D interactif, assistant conversationnel).
**Architecture :** MVC (Model-View-Controller), avec persistance relationnelle (PostgreSQL)
et NoSQL (MongoDB).
**Durée :** projet mené sur plusieurs semaines, en développement itératif. Le périmètre a
significativement augmenté par rapport à l'estimation initiale de 5 jours du CDC v1.

## 1. Objectifs du Projet

L'objectif est de livrer une plateforme web dynamique, responsive et sécurisée autour de
l'astronomie : catalogue d'objets célestes, visualisation 3D du système solaire, assistant
IA conversationnel, comptes utilisateurs avec système de favoris et de propositions
d'objets, et un espace d'administration complet. Le projet sert de preuve de compétence
pour la maîtrise d'une architecture en couches (MVC), la gestion de données relationnelles
et NoSQL, la sécurisation d'une application web, et la mise en production.

## 2. Exigences Fonctionnelles (QUOI ?)

| ID | Module | Fonctionnalité | Rôle | CRUD | Description Détaillée |
|---|---|---|---|---|---|
| F.01 | Catalogue | Afficher la liste des objets célestes | Visiteur | R | La page d'accueil affiche les objets stockés en base, filtrables par catégorie. |
| F.02 | Détail | Afficher les informations d'un objet | Visiteur | R | Page dédiée : nom, description, image, données techniques (distance, etc.). |
| F.03 | Chatbot | Interroger l'IA sur l'astronomie | Visiteur | - | Chatbot AstroIA (API Gemini 2.5 Flash) pour répondre aux questions. |
| F.04 | Formulaire | Soumettre un sondage/avis | Visiteur | C | Formulaire externe (Tally) pour recueillir l'avis sur l'objet préféré. Inchangé depuis la V1. |
| F.05 | Compte utilisateur | S'inscrire, se connecter, modifier son profil | Utilisateur | C, U | Authentification réelle (mot de passe hashé, session sécurisée). |
| F.06 | Favoris | Ajouter ou retirer un objet de ses favoris | Utilisateur | C, D | Liste de favoris consultable depuis le profil. Fonctionnalité ajoutée en plus de F.04, pas un remplacement. |
| F.07 | Proposition | Proposer un nouvel objet céleste | Utilisateur | C | Soumission mise en attente de validation par un administrateur. |
| F.08 | Proposition | Valider, modifier ou refuser une proposition | Admin | U | Traitement avec commentaire admin, l'objet est publié une fois accepté. |
| F.09 | Commentaires | Commenter un objet, répondre à un commentaire | Utilisateur, Admin | C, D | Fils de discussion imbriqués, réponses de l'admin possibles. |
| F.10 | Administration | Gérer le catalogue (ajout, modification, suppression d'objets) | Admin | C, U, D | Espace d'administration dédié. |
| F.11 | Administration | Gérer les comptes (utilisateurs et administrateurs) | Admin | C, R, U, D | CRUD complet, distinct de la simple authentification. |
| F.12 | Traçabilité | Savoir quel administrateur a saisi ou validé un objet | Admin | R | Historique de saisie par objet. |

## 3. Exigences Techniques (COMMENT ?)

| ID | Catégorie | Exigence | Outils / Technologies |
|---|---|---|---|
| T.01 | Architecture | Utilisation stricte du patron MVC, organisée en blueprints Flask. | Python 3.12 / Flask |
| T.02 | Base de Données | Stockage relationnel (catalogue, comptes, propositions) et NoSQL (commentaires imbriqués). | PostgreSQL (psycopg2), MongoDB (pymongo) |
| T.03 | Front-End | Interface entièrement responsive (Desktop, Mobile). | HTML5, Tailwind CSS, JavaScript, Three.js (système solaire 3D) |
| T.04 | Gestion de Version | Utilisation de Git (commits clairs, historique lisible). | Git / GitHub |
| T.05 | Sécurité | Requêtes paramétrées (anti-injection SQL), hashage des mots de passe, protection CSRF. | psycopg2, bcrypt, Flask-WTF |
| T.06 | Qualité | Tests unitaires et fonctionnels, exécutés automatiquement à chaque push. | Pytest, GitHub Actions (CI) |
| T.07 | API | Connexion et gestion des requêtes vers une API LLM pour le Chatbot. | Gemini 2.5 Flash |
| T.08 | Déploiement | Mise en production reproductible et documentée. | VPS OVH, Gunicorn, nginx, systemd, Certbot (HTTPS) |
| T.09 | Déploiement | Environnement conteneurisé pour le développement et les tests. | Docker, Docker Compose |

## 4. Conception Graphique

**Charte Graphique :** Thème sombre (noir/bleu nuit) pour évoquer l'espace. Couleurs
d'accentuation vives (orange/jaune) pour les éléments interactifs. Inchangée depuis la V1.

**Maquettage :** Mockups (Desktop et Mobile) réalisés via Figma en amont du développement.

**Pages maquettées :** Page d'accueil (Catalogue), Page Détail (Objet Céleste), Page
Chatbot, complétées en cours de projet par les pages Profil, Favoris, Propositions et
Espace d'administration au fur et à mesure de l'ajout de ces fonctionnalités.
