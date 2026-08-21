# Cahier des Charges - Projet AstroLearn

**Thème :** Blog Interactif sur l'Exploration Spatiale et les Constellations.
**Architecture :** MVC (Model-View-Controller).
**Durée estimée :** 5 jours (pour une seule personne).

## 1. Objectifs du Projet

L'objectif principal est de développer une plateforme web dynamique, responsive et sécurisée
qui utilise des données stockées (corps célestes) et intègre des outils modernes (API
conversationnelle et formulaire externe). Ce projet sert de preuve de compétence pour la
maîtrise de l'architecture MVC et des bonnes pratiques de développement web.

## 2. Exigences Fonctionnelles (QUOI ?)

| ID | Module | Fonctionnalité | Rôle | CRUD | Description Détaillée |
|---|---|---|---|---|---|
| F.01 | Catalogue | Afficher la liste des objets célestes | Visiteur | R (Read) | La page d'accueil affiche les objets stockés dans la base de données. |
| F.02 | Détail | Afficher les informations d'un objet | Visiteur | R (Read) | Accès à une page dédiée affichant le nom, la description, l'image et les données techniques. |
| F.03 | Chatbot | Interroger l'IA sur l'astronomie | Visiteur | - | Intégration d'un chatbot (API Gemini/Hugging Face) pour répondre aux questions. |
| F.04 | Formulaire | Soumettre un sondage/avis | Visiteur | C (Create) | Intégration d'un formulaire externe (Tally ou équivalent) pour collecter un avis sur l'objet préféré. |
| F.05 | Administration | S'authentifier (Simulé) | Admin | - | Route réservée simulant la vérification de l'accès administrateur. |

## 3. Exigences Techniques (COMMENT ?)

| ID | Catégorie | Exigence | Outils / Technologies |
|---|---|---|---|
| T.01 | Architecture | Utilisation stricte du patron MVC. | Python / Flask |
| T.02 | Base de Données | Stockage local des données (objets célestes, administrateurs). | SQLite |
| T.03 | Front-End | Interface entièrement responsive (Desktop, Mobile). | HTML5, CSS (Tailwind CSS), JavaScript |
| T.04 | Gestion de Version | Utilisation de Git (commits clairs, branches pour les fonctionnalités). | Git / GitHub |
| T.05 | Sécurité | Prévention des Injections SQL via requêtes paramétrées. | sqlite3 et le Contrôleur |
| T.06 | Qualité | Mise en place de tests unitaires et fonctionnels. | Pytest |
| T.07 | API | Connexion et gestion des requêtes vers une API LLM pour le Chatbot. | fetch() API / Gemini 2.5 Flash |

## 4. Conception Graphique

**Charte Graphique :** Thème sombre (noir/bleu nuit) pour évoquer l'espace. Couleurs
d'accentuation vives (orange/jaune) pour les éléments interactifs.

**Maquettage :** Création des Mockups (Desktop et Mobile) via Figma.

**Pages à maquetter :** Page d'accueil (Catalogue), Page Détail (Objet Céleste), Page Chatbot.
