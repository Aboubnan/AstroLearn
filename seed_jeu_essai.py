# seed_jeu_essai.py - Jeu d'essai complet pour une base de données de test
#
# À exécuter uniquement sur une base de test/dev (jamais sur la production).
# Peuple les tables OBJET_CELESTE, UTILISATEUR, PROPOSITION et FAVORI avec
# des données représentatives, pour disposer d'un jeu d'essai exploitable
# lors des tests manuels ou de la restauration d'un environnement de test.

from model.database import (
    initialize_database,
    insert_solar_system_body,
    create_utilisateur,
    get_utilisateur_by_identifiant,
    create_proposition,
    toggle_favori,
    get_all_celestial_objects,
    get_all_categories,
)

OBJETS_CELESTES = [
    (
        "Mars",
        "Mars",
        "La planète rouge, quatrième planète du système solaire.",
        "Planet",
    ),
    (
        "Titan",
        "Titan",
        "La plus grande lune de Saturne, dotée d'une atmosphère dense.",
        "Moon",
    ),
    (
        "Proxima du Centaure",
        "Proxima Centauri",
        "L'étoile la plus proche du Soleil.",
        "Star",
    ),
    (
        "Andromède",
        "Andromeda Galaxy",
        "La galaxie spirale la plus proche de la Voie lactée.",
        "Galaxy",
    ),
    (
        "Nébuleuse d'Orion",
        "Orion Nebula",
        "Une vaste région de formation d'étoiles.",
        "Nebula",
    ),
    (
        "Cérès",
        "Ceres",
        "La plus grande planète naine de la ceinture d'astéroïdes.",
        "Asteroid",
    ),
]

UTILISATEURS_TEST = [
    {
        "pseudo": "jeu_essai_alice",
        "nom": "Dupont",
        "prenom": "Alice",
        "email": "alice.jeu-essai@example.com",
        "password": "JeuEssai123!",
        "genre": "femme",
        "photo_profil": "uploads/profils/default_avatar.png",
    },
    {
        "pseudo": "jeu_essai_bob",
        "nom": "Martin",
        "prenom": "Bob",
        "email": "bob.jeu-essai@example.com",
        "password": "JeuEssai123!",
        "genre": "homme",
        "photo_profil": "uploads/profils/default_avatar.png",
    },
    {
        "pseudo": "jeu_essai_chris",
        "nom": "Lefèvre",
        "prenom": "Chris",
        "email": "chris.jeu-essai@example.com",
        "password": "JeuEssai123!",
        "genre": "autre",
        "photo_profil": "uploads/profils/default_avatar.png",
    },
]


def seed() -> None:
    initialize_database()

    print("🪐 Insertion des objets célestes de test...")
    for name_fr, name_en, description, body_type in OBJETS_CELESTES:
        insert_solar_system_body(
            name_fr=name_fr,
            name_en=name_en,
            description=description,
            body_type=body_type,
        )

    print("👤 Création des utilisateurs de test...")
    for u in UTILISATEURS_TEST:
        if not get_utilisateur_by_identifiant(u["pseudo"]):
            create_utilisateur(**u)

    alice = get_utilisateur_by_identifiant("jeu_essai_alice")
    objets = get_all_celestial_objects()
    categories = get_all_categories()

    if alice and objets and categories:
        print("📝 Création d'une proposition de test...")
        create_proposition(
            nom_fr="Europe",
            nom_scientifique="Europa",
            description="Lune glacée de Jupiter, candidate à l'habitabilité.",
            url_image=None,
            id_categorie=categories[0]["id_categorie"],
            id_utilisateur=alice["id_utilisateur"],
        )

        print("⭐ Ajout de favoris de test...")
        for objet in objets[:2]:
            toggle_favori(alice["id_utilisateur"], objet["id_objet"])

    print("✅ Jeu d'essai inséré avec succès.")


if __name__ == "__main__":
    print("🔧 SEED JEU D'ESSAI — à utiliser sur une base de test uniquement")
    confirmation = input("Continuer ? (y/n) : ")
    if confirmation.lower() in ("y", "yes", "o", "oui"):
        seed()
    else:
        print("❌ Opération annulée.")
