# Contexte du projet AstroLearn / RNCP — brief pour une nouvelle session Claude

Ce fichier existe parce qu'une longue session Claude Code (menée depuis WSL) a construit
tout le dossier de certification RNCP. En passant à une session 100% Git Bash (sans WSL),
l'historique brut de cette conversation ne suit pas. Ce document résume ce qu'il faut
savoir pour repartir sans perdre de contexte. Lis-le en entier avant d'agir sur ce dépôt.

## Qui est l'utilisateur

Aboubnan (a.boubnan@outlook.com), déjà développeur (pas en formation initiale au sens
"futur métier" — c'est une certification RNCP en cours d'obtention, pas une reconversion).
Propriétaire du projet AstroLearn et de nayaweb-v2 (autre dépôt, non lié à celui-ci).

## Le projet

**AstroLearn** : application web Flask/PostgreSQL/MongoDB sur l'astronomie (catalogue
d'objets célestes, carte 3D du système solaire, chatbot IA Gemini, comptes utilisateurs
avec favoris/propositions/commentaires imbriqués, espace admin). Déployée en production
sur `https://astrolearn.nayaweb.fr` (VPS OVH). Dépôt : `github.com/Aboubnan/AstroLearn`,
branche `master` (le clone local a une branche `main` qui push vers `origin/master`, ne
pas s'en étonner).

C'est aussi le **projet support de sa certification RNCP "Concepteur Développeur
d'Applications"**, formation Beauvoir. Tout le travail de certification vit dans le
dossier `RNCP/` à la racine du dépôt.

## État du dossier RNCP au moment de la bascule

Tout est commité et poussé sur GitHub (commit `d365fe7`, `docs(rncp): ajoute tous les
livrables de certification RNCP`). Rien ne devrait être perdu en cas de suppression de la
session Windows d'origine.

Fichiers clés dans `RNCP/` :

- **`DOSSIER_PROJET.md` / `DOSSIER_PROJET.docx`** — le dossier de projet officiel (16
  sections, ~56 pages en docx, sous le plafond de 60 pages du jury). Contenu vérifié
  factuellement contre le code réel à plusieurs reprises. Section §9.6 couvre
  explicitement OWASP/ANSSI/RGPD (mention obligatoire pour le jury, sinon éliminatoire).
- **`ASTROLEARN.pptx`** — le support de présentation orale, **32 slides**, revu slide par
  slide contre le code réel et les vraies captures d'écran. Timing calculé pour tenir en
  35 min max (~3000 mots de notes ≈ 25-27 min de lecture), + 5 min réservées à une
  démonstration vidéo silencieuse (slide 31, "Démonstration en direct", entre le Bilan et
  la Conclusion). Notes réécrites en langage simple, phrases fluides, première personne.
- **`REVISION_ORAL.md`** (nouveau) — fiche de révision pour l'oral, slide par slide, avec
  chiffres clés et questions probables du jury. À lire par l'utilisateur, pas par Claude.
- **`dossier professionnel.docx`** — le template officiel Ministère du Travail, rempli
  avec les 3 activités-types (via manipulation des content controls / SDT Word).
- **`Capture/`** — toutes les captures d'écran utilisées dans le dossier et le pptx.
- **`2. Conception-UX_UI/`, `3. Architecture de données/`** — schémas (zoning, wireframe,
  maquette, MCD/MLD/MPD, UML), certains régénérés récemment pour refléter l'état réel du
  site (le zoning/wireframe d'origine étaient obsolètes, refaits via cairosvg).
- **`REFERENTIEL CDA.pdf`, `passage jury.webp`** — documents de référence officiels du
  jury RNCP, utilisés pour vérifier que la présentation et le dossier cochent bien toutes
  les cases attendues (grille d'évaluation : la présentation de 40 min évalue précisément
  8 compétences — CP2 à CP9 — c'est vérifié, tout est couvert).

## Faits techniques à ne pas re-découvrir

- Domaine réel : `astrolearn.nayaweb.fr` (PAS `astrolearn.ddns.net`, qui apparaît dans
  d'anciennes captures obsolètes — à corriger si tu en croises une).
- Suppression de compte utilisateur = **admin-only** (`/admin/delete-user/<id>`), pas de
  self-service. Ne jamais présenter ça comme du libre-service.
- Le PPTX utilise deux polices mélangées : **Inter** sur la majorité du deck, mais
  **Poppins** sur les slides ajoutées le plus récemment (Utilisateurs & rôles, Sitemap,
  Démonstration) car clonées depuis une slide plus ancienne. Pas encore harmonisé —
  à vérifier visuellement si l'utilisateur le signale.
- La clé SSH `~/.ssh/id_ed25519` (empreinte `SHA256:NIgnFytJs9toi5mzJBWBjWmmaznKbW/G12ioBtW1OWY`)
  est celle du VPS de production (`nayaweb_vps@37.59.98.118`, host `vps-fb2a0617`),
  configurée via `~/.ssh/config` (alias `nayaweb_vps`). Critique pour tout déploiement.
- Le fichier `.gitignore` a été complété avec `~$*` pour ignorer les fichiers de
  verrouillage Word.

## Ce qui reste potentiellement à faire (non confirmé comme demandé, à vérifier avec l'utilisateur)

- Corriger le léger désordre dans le texte visible de la slide 2 (Sommaire) : elle liste
  "Veille technologique" en position 9, après "Gestion de projet", alors que dans l'ordre
  réel des slides elle vient juste après les tests (slide 24), avant la sécurité. Détail
  mineur, signalé dans `REVISION_ORAL.md`, pas corrigé automatiquement.
- Harmoniser la police Poppins/Inter sur les 3 slides récentes (voir plus haut).
- L'utilisateur prévoit d'enregistrer une vidéo de démonstration silencieuse (OBS Studio
  recommandé) et de l'insérer dans la slide 31 — pas encore fait au moment de la bascule.
- Trois fichiers dans `Téléchargements` Windows (`RÉPUBLIQUE FRANÇAISE.pdf`, `Adresse
  .pdf`, `eml.eml`) ont été signalés comme potentiellement importants mais leur contenu
  n'a pas été vérifié — sans lien avec AstroLearn a priori, mentionné ici juste pour
  mémoire de la conversation de migration.

## Comment travailler avec cet utilisateur (retours donnés pendant la session)

- Rigueur factuelle exigée : toujours vérifier une affirmation contre le code réel ou le
  dossier avant de l'écrire dans une slide/le dossier, ne rien laisser au doute.
- Préfère un rythme "on reprend slide par slide" / "on valide un point à la fois" plutôt
  que de gros changements d'un coup non validés.
- Notes de présentation : langage simple, phrases fluides à lire à voix haute, première
  personne, jamais de liste à puces dans le texte des notes elles-mêmes.
- Confirme avant toute action Git qui pousse sur le remote (mais commit local + push sur
  demande explicite est acceptable).

---

*Généré à la fin de la session WSL du 21/08/2026, avant bascule vers une session Git Bash
uniquement. Pour l'historique complet de la conversation qui a produit tout ce travail,
voir (si encore accessible) `~/.claude/projects/-mnt-c-Users-aboub-qo1p0sa-Desktop-Dev-Beauvoir-AstroLearn-AstroLearn-Project/*.jsonl`
côté WSL — 113 Mo, non portable vers Git Bash sans réinstaller WSL.*
