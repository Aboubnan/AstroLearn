# AstroLearn — Fiche de révision pour l'oral

Basé sur `ASTROLEARN.pptx` (32 slides) et `DOSSIER_PROJET.md`. À relire avant la
soutenance, dans l'ordre de la présentation. Objectif : 35 min de présentation + 5 min
de démonstration live.

---

## 0. Les chiffres à connaître par cœur

| Chiffre | Ce qu'il représente |
|---|---|
| **11** | Compétences professionnelles (CP1 à CP11) couvertes, sur 3 blocs |
| **7** | Entités/tables en base : UTILISATEUR, ADMINISTRATEUR, OBJET_CELESTE, CATEGORIE, PROPOSITION, FAVORI, SAISIR |
| **7** | Blueprints Flask (main, auth, user, admin, chatbot, comment, skymap) |
| **3** | Profils utilisateurs : Visiteur, Utilisateur, Administrateur |
| **2** | Bases de données : PostgreSQL (relationnel) + MongoDB (commentaires) |
| **33** | Tests automatisés, exécutés à chaque push (`pytest`) |
| **16/16** | Vérifications conformes du jeu d'essai détaillé (commentaires imbriqués, 30/07/2026) |
| **14/14** | Vérifications conformes de la campagne fonctionnelle manuelle |
| **91/100** | Score Lighthouse accessibilité sur une fiche objet |
| **3** | Workers Gunicorn en production |
| **Déc. 2025 → juil. 2026** | Durée de développement du projet |

---

## 1. Slide titre (en anglais)

Présentation courte et simple : qui je suis, pourquoi j'ai créé AstroLearn (passion pour
l'astronomie), ce que c'est (site éducatif : catalogue, carte 3D, chatbot IA), que ce
n'est pas un projet scolaire figé mais un vrai site en ligne. Reste en anglais **seulement
sur cette slide**, le reste de l'oral est en français.

## 2. Sommaire

Plan en 11 points, dans l'ordre réel de la présentation :
Présentation → Conception & maquettage → Architecture & BDD → Développement & accès aux
données → Tests & jeu d'essai → Veille technologique → Sécurité & RGPD → Déploiement →
Gestion de projet → Bilan → Démonstration.

⚠️ **Point de vigilance** : le texte affiché sur la slide 2 liste un ordre légèrement
différent de l'ordre réel des slides (il place "Veille technologique" après "Gestion de
projet", alors qu'elle est en réalité juste après les tests, avant la sécurité). Ce n'est
pas grave à l'oral (personne ne compare slide par slide), mais si tu as le temps avant le
jury, harmonise le texte de cette slide avec l'ordre réel.

## 3. Contexte

- Projet **individuel**, certification RNCP CDA.
- Parti d'une version simple (catalogue + chatbot + sondage + auth basique), enrichi
  progressivement.
- Objectif : plateforme complète sur l'astronomie (catalogue, carte 3D, IA, comptes,
  favoris, propositions, espace admin).
- Résultat : deux bases de données, déployé en production sur un VPS que tu administres
  toi-même.

**Cahier des charges (dossier §3.2)** — si le jury demande des détails sur les besoins :
exigences fonctionnelles par rôle (tableau CRUD complet dans le dossier), exigences
techniques (MVC, PostgreSQL+MongoDB, sécurité, tests, déploiement documenté).

## 4. Stack technique

- **Back-end** : Python 3.12, Flask 3.1, MVC, PostgreSQL (psycopg2) + MongoDB (pymongo),
  bcrypt.
- **Front-end** : Jinja2 (rendu serveur), Tailwind CSS, Three.js (3D), JS vanilla.
- **APIs** : Google Gemini 2.5 Flash (chatbot), NASA Images API (catalogue), Tally
  (sondage).
- **DevOps** : VPS OVH Ubuntu 22.04, Gunicorn + nginx, HTTPS Let's Encrypt, Docker (dev/CI
  seulement, pas en prod — assume-le si on te demande pourquoi), GitHub Actions.

## 5. Utilisateurs et rôles

Trois profils, séparation stricte en base (deux tables distinctes `UTILISATEUR` et
`ADMINISTRATEUR`, aucune passerelle au niveau du schéma) :
- **Visiteur** : catalogue, chatbot, sondage.
- **Utilisateur** : + profil, favoris, propositions, commentaires.
- **Administrateur** : gère catalogue/comptes/propositions/modération, PAS d'accès aux
  favoris ni aux propositions (fonctionnalités "sociales" réservées aux utilisateurs).

Retenir la phrase clé : *"un admin n'a pas à se comporter comme un utilisateur inscrit"*.

## 6. Arborescence d'écrans (sitemap)

Vert = visiteur, bleu = utilisateur connecté, rouge = admin. Sert de base avant le zoning
et le wireframe. Connaître les URLs principales si le jury demande du concret :
`/catalogue`, `/object/<id>`, `/sky-map`, `/mon-espace`, `/admin_dashboard`.

## 7-10. Conception (Zoning, Wireframe, Charte graphique, Maquette)

Ordre de conception réel : sitemap → zoning (grandes zones sans détail) → wireframe
(éléments réels, sans couleur) → maquette (rendu final Figma).

**Charte graphique — à connaître précisément :**

| Usage | Couleur | HEX |
|---|---|---|
| Fond principal | Bleu nuit très sombre | `#000525` |
| Fond secondaire | Bleu nuit | `#1c2a5a` |
| Texte clair | Lavande pâle | `#e0e6f7` |
| Accentuation | Orange | `#ff8811` |

Police unique : **Inter** (Bold titres, Regular texte courant).

## 11. Diagramme UML (cas d'utilisation)

2 acteurs : Utilisateur (catalogue, chatbot, inscription, proposition, favoris,
commentaires) et Administrateur (gestion catalogue/propositions/comptes, modération).
Toute action sensible nécessite une authentification.

## 12. Architecture MVC

- **Model** : accès aux données, aucune connaissance de HTTP/HTML.
- **View** : templates Jinja2, aucune logique métier.
- **Controller** : 7 blueprints Flask, reçoit la requête, appelle le Model, choisit la
  View.
- Bénéfice : modifier l'apparence ne touche que `templates/`, changer une table ne touche
  que `model/`.

## 13-15. MCD / MLD / MPD (méthode Merise)

- **MCD** : 7 entités. Deux associations N,N avec cardinalité (0,N)-(0,N) : `SAISIR`
  (ADMIN↔OBJET_CELESTE, traçabilité) et `AIMER` (UTILISATEUR↔OBJET_CELESTE, favoris).
- **MLD** : les associations N,N deviennent des tables de jonction (`SAISIR`, `FAVORI`),
  les relations 1,N deviennent des clés étrangères (`fk_id_categorie`,
  `fk_id_utilisateur`...).
- **MPD** : script SQL réel (`CREATE_TABLES_SQL` dans `model/database.py`), avec `ON
  DELETE CASCADE` / `ON DELETE SET NULL` selon le cas, contraintes `UNIQUE` (pseudo,
  email), valeurs par défaut (`statut = 'en_attente'`).

**Si le jury demande le détail d'une table**, la plus susceptible d'être creusée est
`SAISIR` : clé primaire **composite** (`fk_id_admin`, `fk_id_objet`), sert à savoir quel
admin a saisi ou validé quel objet — implémentée réellement (pas juste documentée).

## 16. Accès aux données SQL et NoSQL

- **PostgreSQL** (`model/database.py`) : `psycopg2`, `RealDictCursor`, requêtes
  paramétrées (`%s`), bloc `try/commit/except/rollback/finally` sur toute écriture.
- **MongoDB** (`comment_service.py`) : un document par objet céleste, arbre de
  commentaires modifié en mémoire puis réenregistré en un `update_one(upsert=True)`.
- **Pas d'ORM** : choix assumé, pour rester au plus près du langage propre à chaque base.
- Optimisation à citer : `get_favoris_counts()` récupère tous les compteurs en une seule
  requête groupée plutôt qu'une requête par objet.

## 17. Front-end (exemple : toggle favori)

`toggle_favori_route` (`user_bp.py`) : clic sur le cœur → requête AJAX POST → route
protégée par `login_required` → le Model ajoute/retire le favori et renvoie le nouvel
état → le Controller renvoie du JSON → JavaScript met à jour l'icône et le compteur sans
recharger la page. Bon exemple pour illustrer la séparation MVC en pratique.

## 18. Back-end (exemple : chatbot)

Route reçoit le JSON, vérifie sa validité, délègue à `AstroIAChatbot.ask()` (dans le
Model) qui valide le message (vide/trop long → `ValueError`), appelle Gemini, gère les
erreurs (`RuntimeError` si réponse inexploitable). Le Controller traduit juste le
résultat en code HTTP (200/400/500). **Point d'honnêteté à mentionner si utile** : cette
classe est née d'un refactor, la logique était au départ directement dans la route.

## 19. Éco-conception

- Chargement différé des images (`loading="lazy"`).
- Pas d'image de remplacement stockée : placeholder généré à la volée
  (`placehold.co`).
- Requêtes SQL ciblées, pas de `SELECT *` systématique.
- Pas de framework JS lourd ; Three.js chargé seulement sur la page carte 3D.

## 20. APIs REST

Trois APIs : `/api/chatbot` (Gemini), `/favori/toggle` (AJAX favoris), `/api/translate`
(traduction FR→EN à la demande, avec cache client). Toutes en JSON, bons codes HTTP.

## 21. Tests

4 niveaux : unitaires (mocks), intégration (`app.test_client()` + PostgreSQL réel),
sécurité ciblée (bcrypt, CSRF), campagne manuelle (parcours non couverts par l'auto).
Répartition à connaître : `test_security.py`/`test_csrf.py` (8/8), `test_chatbot_service`
(6/6), `test_comment_service` (15/15). **Seul test hors CI** : celui qui appelle
vraiment l'API Gemini (quota payant).

## 22. Jeu d'essai (commentaires imbriqués)

Scénario réel : commentaire racine par un utilisateur sur Mars (id 1) → réponse admin
(profondeur 1) → réponse de l'utilisateur (profondeur 2) → vérification badge non-lus
(3→0 après consultation admin) → suppression du commentaire racine → les 2 réponses
disparaissent en cascade. **16/16 conformes**, exécuté le 30/07/2026.

**Anecdote utile si le jury demande "as-tu eu des surprises en testant"** : 2 écarts
rencontrés en écrivant les vérifications, aucun n'était un vrai bug — l'apostrophe
échappée (`&#39;`) est le comportement anti-XSS normal de Jinja2 ; le badge non-lus
partageait ses classes CSS avec un autre badge, corrigé en ciblant précisément l'onglet.

## 23. CI/CD

Flake8 (PEP8) → Black (formatage auto) → Pytest (33 tests, PostgreSQL temporaire) → tout
dans un seul job GitHub Actions, déclenché sur **toutes les branches**, pas seulement
`main`. Dependabot ouvre des PR automatiques sur faille connue.

## 24. Veille technologique

Sources : alertes Dependabot, notes de version (PostgreSQL/MongoDB/nginx/Gunicorn/Certbot),
alertes sécurité Ubuntu. Exemple concret à citer : plusieurs dépendances vulnérables
mises à jour après vérification par la suite de tests. Exemple MongoDB : compte
applicatif limité en lecture/écriture, jamais admin (moindre privilège).

**Anecdotes de veille utiles si creusé (dossier §14.3/14.4)** :
- Scope de token GitHub `workflow` manquant → push refusé sur `ci.yml` → compris que
  c'était une restriction volontaire de sécurité, pas un bug.
- `SESSION_COOKIE_SECURE=True` fait que la librairie `requests` ignore silencieusement le
  cookie en HTTP simple dans les tests → comportement normal de `requests`, pas un défaut
  de l'appli → solution : récupération manuelle de l'en-tête `Set-Cookie`.

## 25. Sécurité

- Bcrypt (sel automatique), jamais de mot de passe en clair.
- Sessions Flask : `HttpOnly` (anti-XSS), `Secure` (HTTPS obligatoire), `SameSite=Lax`
  (anti-CSRF) — **vérifiable en direct** via `curl -I https://astrolearn.nayaweb.fr/`.
- Clés API dans `.env`, jamais commit. `SECRET_KEY` obligatoire, l'appli refuse de
  démarrer sans elle.
- `@login_required` / `@admin_required` sur les routes sensibles.
- Protection CSRF (`Flask-WTF`) sur tous les POST, y compris AJAX (en-tête
  `X-CSRFToken`).
- **Conforme OWASP Top 10 et ANSSI** — à dire explicitement à voix haute, c'est un point
  attendu par le jury.

## 26. RGPD

Minimisation des données (pseudo, nom, prénom, email, mot de passe ; photo optionnelle).
Droit d'accès et de modification en libre-service. **Suppression du compte sur demande,
traitée par un administrateur** (pas encore de self-service — assume-le si demandé).
Aucune revente de données. Page `/legal` (mentions légales + politique de
confidentialité) accessible en pied de page partout.

## 27. Déploiement

VPS OVH Ubuntu 22.04, sous-domaine `astrolearn.nayaweb.fr` (enregistrement DNS de type A).
Étapes : préparation serveur → code + dépendances → PostgreSQL/MongoDB avec utilisateurs
dédiés → service systemd (Gunicorn, 3 workers, redémarrage auto) → nginx reverse proxy +
HTTPS (Certbot, renouvellement auto). Mise à jour via `deploy.sh` (`git pull` +
dépendances + redémarrage + test de santé HTTP, `set -euo pipefail`). Rollback : retour à
un commit stable + `pg_restore` si besoin. **Déploiement volontairement manuel**, pas
branché sur la CI (pas de SSH permanent donné à GitHub Actions, pas d'outils de
supervision/rollback assez solides pour du continu sans surveillance).

## 28-29. Gestion de projet (Kanban, Git)

Kanban GitHub Projects (à faire / en cours / terminé). Pas de Scrum complet — pas de sens
pour un solo — mais principes gardés : liste priorisée, livraison itérative, retour
régulier au cahier des charges. Commits type Conventional Commits (`feat:`, `fix:`,
`refactor:`, `chore:`, `docs:`). Dependabot ouvre des PR sur `main`.

**Jalons à connaître (dossier §10.4)** :
- Déc. 2025 : socle initial (maquette, chatbot Gemini, carte 3D).
- Mars 2026 : migration PostgreSQL, MVC typé, comptes, favoris, dashboard, admin.
- Avr. 2026 : qualité (Flake8/Black), tests Pytest, CI/CD.
- Juil. 2026 : revue de code, CSRF, RGAA, Docker, commentaires MongoDB.
- Fin juil. 2026 : documentation + mise en production.

## 30. Bilan

Technique : très au-delà de l'ambition de départ, l'architecture a tenu la croissance.
Personnel : cycle complet de développement, tous les rôles endossés seul — présente-le
comme un renforcement de tes compétences de développeur, **pas comme une préparation à un
futur métier** (tu es déjà développeur).

**Limites assumées à connaître si le jury demande "qu'est-ce qui ne va pas" (dossier
§15.2)** — ne pas cacher, mais formuler comme des choix conscients, pas des oublis :
- Couverture de test incomplète sur des routes admin peu utilisées (modif/suppression
  compte admin, traduction, ingestion NASA).
- Déploiement manuel plutôt qu'automatisé.
- Suivi des dépendances relâché plusieurs mois, corrigé en préparant ce dossier — leçon
  retenue sur la discipline de maintenance.
- `datetime.utcnow()` déprécié, repéré via un warning Pytest, non corrigé.

## 31. Démonstration (5 min)

Vidéo silencieuse, tu commentes en direct. Ordre prévu : catalogue → fiche objet → carte
3D → chatbot → toggle favori → proposition (utilisateur) puis validation (admin) →
commentaire imbriqué 3 niveaux avec badge admin.

## 32. Conclusion

AstroLearn = projet complet de A à Z, couvre les 11 CP, réellement en ligne et
fonctionnel (pas une maquette), vraies données NASA, vraie IA. Termine par un
remerciement et l'ouverture aux questions.

---

## Questions probables du jury (et éléments de réponse)

**"Pourquoi pas d'ORM ?"**
Choix assumé : rester au plus près du langage SQL/NoSQL propre à chaque base, comprendre
exactement ce qui s'exécute plutôt que de dépendre d'une couche d'abstraction.

**"Pourquoi Docker en dev/CI mais pas en prod ?"**
Choix pragmatique pour un seul développeur / un seul serveur. Idéalement, la même image
partout serait plus rigoureuse, mais ajouter Docker en prod n'apportait pas assez de
valeur à cette échelle. Sur un projet plus gros avec plusieurs serveurs, tu ferais
autrement.

**"Pourquoi le déploiement n'est pas automatisé (pas de CD) ?"**
Pas de SSH permanent donné à GitHub Actions, pas d'outils de supervision/rollback assez
solides pour de la livraison continue sans surveillance humaine. Contrôle humain gardé
volontairement avant chaque mise en ligne.

**"Comment gères-tu la différence entre un utilisateur et un admin qui commentent ?"**
`comment_routes.py` identifie l'auteur une seule fois (au même endroit), transmet
identifiant/pseudo/rôle à `CommentaireService`, qui n'a pas besoin de savoir qui écrit.

**"Qu'est-ce qui n'est pas testé ?"**
Routes admin peu fréquentes (modif/suppression compte admin, traduction FR/EN, ingestion
NASA) — identifié et priorisé par risque, ces routes n'affectent pas les données d'un
autre utilisateur.

**"Différence entre MCD, MLD et MPD ?"**
MCD = conceptuel, abstrait, entités et associations sans souci d'implémentation. MLD =
logique, associations N,N deviennent des tables de jonction, 1,N deviennent des clés
étrangères. MPD = physique, script SQL réel avec types PostgreSQL et contraintes.

**"Pourquoi MongoDB pour les commentaires et pas une table récursive en SQL ?"**
Un arbre de profondeur variable est naturel en document (tout l'arbre dans un seul objet)
alors qu'en SQL il aurait fallu une table auto-référencée avec des requêtes récursives
bien plus complexes.

**"Comment sais-tu que c'est sécurisé, pas juste écrit dans le code ?"**
Vérifiable en direct : `curl -I https://astrolearn.nayaweb.fr/` montre le cookie de
session avec `Secure; HttpOnly; SameSite=Lax` sur le vrai site en production, pas
seulement une intention dans le code.

**"Que ferais-tu différemment si c'était à refaire ?"**
Suivre les alertes Dependabot au fur et à mesure plutôt que de les laisser s'accumuler ;
mettre en place des tests dédiés sur les routes admin peu fréquentes dès leur écriture.

---

*Document généré à partir de `ASTROLEARN.pptx` (32 slides, contenu vérifié slide par
slide contre le code réel) et `DOSSIER_PROJET.md` (16 sections). Pour tout doute sur un
détail technique, le code source fait foi.*
