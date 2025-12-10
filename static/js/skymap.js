document.addEventListener("DOMContentLoaded", () => {
    initializeCelestialMap();
});

function initializeCelestialMap() {
    const container = document.getElementById("star-map-container");
    if (!container) {
        console.error("Conteneur #star-map-container non trouvé.");
        return;
    }

    container.innerHTML = "";  // Vide le conteneur

    const config = {
        container: "star-map-container",
        datapath: "https://cdn.jsdelivr.net/npm/d3-celestial/data/",
        interactive: true,
        planets: { show: true, names: true },
        stars: { show: true, limit: 6 },
        dsos: { show: true },
        type: "svg"
    };

    try {
        Celestial.display(config, function(error) {
            if (error) {
                console.error("Erreur lors de l'affichage de la carte céleste :", error);
                return;
            }
            console.log("Carte céleste chargée avec succès.");

            // Une fois affichée, récupère l'élément SVG
            const svg = container.querySelector("svg");
            if (svg) {
                svg.style.cursor = "pointer";
                svg.addEventListener("click", function (event) {
                    handleSvgClick(event, svg);
                });
            } else {
                console.error("SVG non trouvé dans le conteneur après affichage.");
            }
        });
    } catch (e) {
        console.error("Erreur lors de l'initialisation de Celestial :", e);
    }
}

// --------------------------- 
// GESTION DU CLIC SUR SVG
// ---------------------------

function handleSvgClick(event, svg) {
    const rect = svg.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    const eq = Celestial.mapProjection.invert([x, y]);

    if (!eq) {
        console.log("Clic hors de la projection.");
        return;
    }

    const ra = eq[0];
    const dec = eq[1];

    const clicked = findNearestCelestialObject(ra, dec);

    if (clicked) {
        const name = clicked.properties.name || clicked.id || "Objet inconnu";
        const mag = clicked.properties.mag || "N/A";
        const type = clicked.type || "Inconnu";

        alert(`
Objet cliqué :
Nom : ${name}
Type : ${type}
Magnitude : ${mag}
        `);
    } else {
        alert("Aucun objet trouvé près du clic.");
    }
}

// -----------------------------------------------------
// FONCTION : Trouve l'objet le plus proche dans les data
// -----------------------------------------------------

function findNearestCelestialObject(raClick, decClick) {
    let nearest = null;
    let minDist = Infinity;

    const sources = ["stars", "dsos", "planets"];

    sources.forEach(type => {
        const list = Celestial.data[type];
        if (!list || !list.features) {
            console.warn(`Données pour ${type} non disponibles.`);
            return;
        }

        list.features.forEach(obj => {
            const ra = obj.properties.ra;
            const dec = obj.properties.dec;
            if (ra === undefined || dec === undefined) return;

            const dist = angularDistance(ra, dec, raClick, decClick);

            if (dist < minDist) {
                minDist = dist;
                nearest = obj;
            }
        });
    });

    return minDist < 0.4 ? nearest : null;
}

// -----------------------------------------------------
// Calcule la distance angulaire entre deux points RA/DEC
// -----------------------------------------------------
function angularDistance(ra1, dec1, ra2, dec2) {
    const rad = Math.PI / 180;
    ra1 *= rad;
    dec1 *= rad;
    ra2 *= rad;
    dec2 *= rad;

    return Math.acos(
        Math.sin(dec1) * Math.sin(dec2) +
        Math.cos(dec1) * Math.cos(dec2) * Math.cos(ra1 - ra2)
    ) / rad;
}

document.addEventListener("DOMContentLoaded", () => {
    console.log("DOM chargé. Vérification de Celestial :", typeof Celestial);  // Ajoutez cette ligne
    if (typeof Celestial === 'undefined') {
        console.error("Celestial n'est pas défini. Vérifiez le chargement des scripts.");
        return;
    }
    initializeCelestialMap();
});