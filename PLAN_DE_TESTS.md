# Plan de tests — AstroLearn

## 1. Objectif et périmètre

Ce document couvre l'ensemble des fonctionnalités retenues de l'application :
authentification (utilisateur et administrateur), catalogue et fiches d'objets
célestes, favoris, propositions d'objets, tableau de bord admin (CRUD objets,
administrateurs, utilisateurs, propositions), commentaires imbriqués (NoSQL) et
modération, chatbot AstroIA, sécurité transverse (CSRF, hachage des mots de passe).

## 2. Environnements de test

| Environnement | Usage |
|---|---|
| Local (venv) | Tests unitaires isolés (mocks), lint |
| CI (GitHub Actions) | `flake8`, `black`, `pytest` à chaque push, PostgreSQL éphémère de service |
| Docker (`docker compose up`) | Campagne de tests fonctionnels/manuels bout-en-bout (PostgreSQL + MongoDB réels, jetables) |

Voir [`DEPLOIEMENT.md`](./DEPLOIEMENT.md) pour le détail de ces environnements.

## 3. Stratégie de test

- **Tests unitaires** (`pytest`, mocks) : logique métier isolée de toute
  dépendance externe — `CommentaireService`, `AstroIAChatbot`, hachage bcrypt,
  mapping de catégories NASA.
- **Tests d'intégration** (`pytest` + `app.test_client()`) : comportement HTTP
  réel de l'application — application et rejet du token CSRF sur les
  formulaires et l'API.
- **Tests de sécurité** : salage/format bcrypt des mots de passe, rejet des
  requêtes sans jeton CSRF (formulaires classiques et appels AJAX).
- **Tests fonctionnels manuels** (campagne du 30/07/2026, décrite en section 4
  et 5) : parcours bout-en-bout exécutés via HTTP réel contre l'environnement
  Docker, pour les fonctionnalités qui n'ont pas (encore) de test automatisé
  dédié — inscription, connexion, favoris, propositions, CRUD admin,
  commentaires imbriqués et modération.

## 4. Couverture fonctionnelle

| Fonctionnalité | Type de test | Référence | Résultat |
|---|---|---|---|
| Hachage / vérification des mots de passe (bcrypt, sel aléatoire) | Automatisé (unitaire) | `tests/test_security.py` (3 tests) | ✅ PASS |
| Protection CSRF (formulaires + API AJAX) | Automatisé (intégration) | `tests/test_csrf.py` (5 tests) | ✅ PASS |
| Chatbot AstroIA (validation, troncature, historique) | Automatisé (unitaire, mocké) | `tests/test_chatbot_service.py` (6 tests) | ✅ PASS |
| Commentaires imbriqués (ajout, réponse, suppression en cascade, non-lus) | Automatisé (unitaire, mocké) | `tests/test_comment_service.py` (15 tests) | ✅ PASS |
| Connexion BDD / catégories | Automatisé (intégration, PostgreSQL réel) | `tests/test_db.py`, `tests/test_db_connexion.py` | ✅ PASS |
| Mapping catégories NASA FR/EN | Automatisé (unitaire) | `tests/test_logic.py` | ✅ PASS |
| Recherche utilisateur inexistant | Automatisé (unitaire) | `tests/test_validation.py` | ✅ PASS |
| Intégration API Gemini réelle | Automatisé, exclu de la CI (quota payant) | `tests/test_astroia.py` (manuel) | ⚠️ à exécuter manuellement, hors CI |
| Inscription utilisateur | Manuel (campagne 30/07/2026) | Section 4bis, étape 1 | ✅ PASS |
| Connexion utilisateur et admin | Manuel (campagne 30/07/2026) | Section 4bis, étapes 2 et 5 | ✅ PASS |
| Ajout/retrait de favori (AJAX) | Manuel (campagne 30/07/2026) | Section 4bis, étape 3 | ✅ PASS |
| Proposition d'un objet céleste | Manuel (campagne 30/07/2026) | Section 4bis, étape 4 | ✅ PASS |
| Traitement admin d'une proposition | Manuel (campagne 30/07/2026) | Section 4bis, étape 7 | ✅ PASS |
| Ajout d'un objet céleste (admin) | Manuel (campagne 30/07/2026) | Section 4bis, étape 6 | ✅ PASS |
| Suppression d'un utilisateur (admin) | Manuel (campagne 30/07/2026) | Section 4bis, étape 8 | ✅ PASS |
| Commentaires imbriqués bout-en-bout (profondeur 2, badge non-lus, suppression en cascade) | Manuel (jeu d'essai détaillé, section 5) | Section 5 | ✅ PASS |
| Modification d'un objet céleste (admin) | Non testé formellement | — | ⚠️ à couvrir |
| Modification/suppression d'un compte admin | Non testé formellement | — | ⚠️ à couvrir |
| Traduction FR/EN (`/api/translate`) | Non testé formellement | — | ⚠️ à couvrir |
| Ingestion catalogue NASA (`/admin/ingest_solar_system`) | Non testé formellement | — | ⚠️ à couvrir |

Les fonctionnalités marquées « à couvrir » sont un backlog de tests identifié
lors de la rédaction de ce plan, priorisé selon le risque (routes admin à
faible fréquence d'utilisation, sans impact sur les données d'un autre
utilisateur qu'un administrateur).

## 4bis. Campagne de tests fonctionnels manuels (30/07/2026)

Exécutée contre l'environnement Docker (`docker compose up`), base de données
réinitialisée et peuplée par `seed_jeu_essai.py` avant la campagne.

| # | Étape | Résultat attendu | Résultat obtenu |
|---|---|---|---|
| 1 | `POST /inscription` (nouveau compte) | Redirection 302 vers `/connexion` | 302 vers `/connexion` ✅ |
| 2 | `POST /connexion` (utilisateur) | Redirection 302 vers `/mon-espace` | 302 vers `/mon-espace` ✅ |
| 3 | `GET /mon-espace` | 200, tableau de bord affiché | 200 ✅ |
| 4 | `POST /favori/toggle/1` (AJAX, en-tête `X-CSRFToken`) | JSON `{"success": true, ...}` | `{"count":2,"est_favori":true,"success":true}` ✅ |
| 5 | `POST /proposer-objet` | Redirection 302 vers `/mon-espace` | 302 ✅ |
| 6 | `POST /connexion` (admin) | Redirection 302 vers `/admin_dashboard` | 302 ✅ |
| 7 | `GET /admin_dashboard` (admin) | 200 | 200 ✅ |
| 8 | `POST /admin/add-object` | Redirection 302, objet visible au catalogue | 302, présent dans `/catalogue` ✅ |
| 9 | `POST /admin/proposition/<id>/traiter` (statut=`accepte`) | Redirection 302, statut mis à jour en base | 302, `statut='accepte'` vérifié en base ✅ |
| 10 | `POST /admin/delete-user/<id>` | Redirection 302, compte supprimé | 302 ; tentative de connexion post-suppression → « Identifiant ou mot de passe incorrect » ✅ |

**Résultat : 14/14 vérifications conformes.**

## 5. Jeu d'essai détaillé — commentaires imbriqués (fonctionnalité la plus représentative)

Choisie comme fonctionnalité représentative car elle combine PostgreSQL (objet
céleste, identité utilisateur/admin), MongoDB (arbre de commentaires,
profondeur illimitée), sécurité (CSRF, double système de session
utilisateur/admin) et une couche de service dédiée (`CommentaireService`).

### Données en entrée

1. Un utilisateur (`jeu_essai_user`) poste un commentaire racine sur l'objet
   céleste n°1 (Mars) : `"Superbe vue sur Mars, merci pour la fiche !"`
2. Un administrateur répond à ce commentaire (profondeur 1) :
   `"Merci pour votre retour, ravi que la fiche vous plaise !"`
3. L'utilisateur répond à la réponse de l'administrateur (profondeur 2) :
   `"Avec plaisir, hâte d'en savoir plus sur les prochaines missions !"`

### Données attendues

- Un document MongoDB `{objet_id: 1, commentaires: [...]}` avec un arbre de
  3 nœuds correctement imbriqués (racine → réponse admin → réponse à la
  réponse), chacun avec `commentaire_id` (UUID), `date`, `vu: false`.
- Le commentaire de l'utilisateur a `utilisateur_id` renseigné et
  `est_admin: false` ; celui de l'administrateur a `utilisateur_id: null`,
  `est_admin: true` et `pseudo: "Administration AstroLearn"`.
- Les 3 messages affichés sur la page de l'objet, avec un badge « bouclier »
  pour le message admin.
- Le tableau de bord admin affiche un badge de 3 commentaires non lus à la
  première visite, puis 0 à la visite suivante (marqués lus automatiquement).
- La suppression du commentaire racine par l'admin supprime tout le
  sous-arbre (les 2 réponses disparaissent avec lui).

### Données obtenues (extrait réel, exécution du 30/07/2026)

```json
{
  "commentaire_id": "d0c016b5-2c30-4227-83b1-ec48593a54aa",
  "utilisateur_id": 5,
  "pseudo": "jeu_essai_user",
  "texte": "Superbe vue sur Mars, merci pour la fiche !",
  "date": "2026-07-30T08:26:00.392929+00:00",
  "vu": false,
  "est_admin": false,
  "reponses": [
    {
      "commentaire_id": "32dbb7de-f197-4136-9647-9ce2c6849a08",
      "utilisateur_id": null,
      "pseudo": "Administration AstroLearn",
      "texte": "Merci pour votre retour, ravi que la fiche vous plaise !",
      "date": "2026-07-30T08:26:00.750355+00:00",
      "vu": false,
      "est_admin": true,
      "reponses": [
        {
          "commentaire_id": "a0229217-9ce5-4e5b-a03e-e5f4880ab9a1",
          "utilisateur_id": 5,
          "pseudo": "jeu_essai_user",
          "texte": "Avec plaisir, hâte d'en savoir plus sur les prochaines missions !",
          "date": "2026-07-30T08:26:00.795576+00:00",
          "vu": false,
          "est_admin": false,
          "reponses": []
        }
      ]
    }
  ]
}
```

Badge non-lus : **3** à la première visite du tableau de bord admin, **0** à
la seconde (vérifié aussi directement en base : `count_non_lus()` passe de 3
à 0 entre les deux visites). Suppression du commentaire racine : le nœud et
ses 2 réponses ont bien disparu du document MongoDB.

**Résultat : conforme aux données attendues, 16/16 vérifications passées.**

### Analyse des écarts

Un écart est apparu lors du premier passage : le texte de la réponse de
profondeur 2 contient une apostrophe (« hâte **d'**en savoir »), et le texte
brut n'apparaissait pas tel quel dans le HTML obtenu. **Ce n'est pas un
défaut de l'application** : Jinja2 échappe automatiquement les caractères
spéciaux dans les templates (`'` devient `&#39;`), ce qui est le comportement
de sécurité attendu contre les injections XSS. Une fois le test corrigé pour
comparer avec le texte échappé, la vérification est passée. Ce point avait
déjà été identifié comme non-bug lors du développement de la fonctionnalité.

Un second écart est apparu sur la vérification du badge non-lus : la
première mesure retournait systématiquement 1 quel que soit l'état réel des
commentaires. Investigation : le badge des commentaires non lus et le badge
« propositions en attente » du tableau de bord partagent exactement les
mêmes classes CSS Tailwind (`bg-yellow-500 text-black text-xs px-1.5 py-0.5
rounded-full font-bold`), et un test qui cherche cette classe sans plus de
contexte capture le premier badge rencontré dans la page — pas forcément le
bon. Une vérification directe en base (via `count_non_lus()`) a confirmé que
la logique applicative était correcte (3 puis 0) ; le test a été corrigé en
ancrant la recherche sur `id="tab-commentaires"`, propre à l'onglet
Commentaires. Après correction, le résultat obtenu correspond exactement au
résultat attendu.

## 6. Sécurité des tests

- Les tests exécutés en CI ne s'appuient sur **aucun secret réel** :
  PostgreSQL éphémère avec des identifiants jetables (`postgres`/`postgres`),
  `SECRET_KEY` de test non sensible, générés dans le workflow lui-même (voir
  [`VEILLE_DEPLOIEMENT.md`](./VEILLE_DEPLOIEMENT.md)).
- Le test qui appelle une vraie API externe payante (Gemini) est exclu de la
  CI pour ne pas exposer de clé API réelle dans un environnement partagé ni
  consommer de quota à chaque push.
- Les identifiants administrateur utilisés pour la campagne de tests manuels
  (`.env` local, section `ADMIN_PSEUDO`/`ADMIN_PASSWORD`/`ADMIN_EMAIL`) sont
  des valeurs jetables, propres à l'environnement Docker de test, retirées du
  fichier `.env` après la campagne.
- Les tests de sécurité applicative (CSRF, hachage bcrypt) sont maintenus à
  jour au fil des évolutions technologiques : voir la veille dédiée dans
  [`VEILLE_DEPLOIEMENT.md`](./VEILLE_DEPLOIEMENT.md) (ex. mise à jour Flask/
  Werkzeug via Dependabot, vérifiée par la suite de tests avant déploiement).

## 7. Recherche menée durant la préparation des tests

Lors de l'écriture des tout premiers tests d'intégration HTTP (protection
CSRF, puis les campagnes manuelles de ce document), une difficulté récurrente
est apparue : le flag `SESSION_COOKIE_SECURE=True` (bonne pratique de
sécurité, empêche l'envoi du cookie de session en clair) fait que la
bibliothèque Python `requests` **ignore silencieusement** le cookie de
session reçu lorsque le test tourne en HTTP simple (comme c'est le cas en
local/CI, sans certificat TLS) — le `requests.Session` refuse de stocker un
cookie marqué `Secure` sur une connexion non chiffrée. Sans investigation,
les tests échouaient de façon peu explicite (redirections vers la page de
connexion comme si l'utilisateur n'était jamais authentifié).

Recherche effectuée : lecture de la documentation de `requests`/`http.cookiejar`
sur la gestion des cookies `Secure`, confirmant que ce n'est pas un bug de
l'application mais un comportement standard des clients HTTP. Solution
retenue et appliquée dans tous les scripts de test de ce projet : extraire
manuellement l'en-tête `Set-Cookie` de la réponse et le renvoyer tel quel
dans l'en-tête `Cookie` des requêtes suivantes, en contournant le cookiejar
automatique (voir la classe `Client` réutilisée dans les campagnes de tests
manuels de ce document).
