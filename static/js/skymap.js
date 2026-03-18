/* static/js/skymap.js - Version Tactile Optimisée */

document.addEventListener("DOMContentLoaded", () => {
    if (typeof Celestial === 'undefined') {
        console.error("Celestial n'est pas défini.");
        return;
    }
    initializeCelestialMap();
});

function initializeCelestialMap() {
    const container = document.getElementById("star-map-container");
    if (!container) return;

    container.innerHTML = "";

    const config = {
        container: "star-map-container",
        datapath: "https://cdn.jsdelivr.net/npm/d3-celestial/data/",
        interactive: true,
        planets: { show: true, names: true },
        stars: { show: true, limit: 6 },
        dsos: { show: true },
        form: false,
        type: "svg"
    };

    Celestial.display(config, function(error) {
        if (error) return;

        const svg = container.querySelector("svg");
        if (svg) {
            svg.style.cursor = "pointer";

            // Variables pour détecter le scroll vs tap
            let touchStartX = 0;
            let touchStartY = 0;

            // Gestion PC : clic classique
            svg.addEventListener("click", (e) => handleAction(e, svg));

            // Gestion mobile : on mémorise la position au début du touch
            svg.addEventListener("touchstart", (e) => {
                touchStartX = e.touches[0].clientX;
                touchStartY = e.touches[0].clientY;
            }, { passive: true });

            // On déclenche l'action seulement si le doigt n'a pas scrollé (< 10px)
            svg.addEventListener("touchend", (e) => {
                const dx = Math.abs(e.changedTouches[0].clientX - touchStartX);
                const dy = Math.abs(e.changedTouches[0].clientY - touchStartY);
                if (dx < 10 && dy < 10) {
                    e.preventDefault(); // Empêche le click synthétique 300ms après
                    handleAction(e, svg);
                }
            }, { passive: false });
        }
    });
}

function handleAction(event, svg) {
    // Empêche la propagation pour ne pas que le chatbot reçoive l'event
    event.stopPropagation();
    handleSvgClick(event, svg);
}

function handleSvgClick(event, svg) {
    const rect = svg.getBoundingClientRect();

    // Pour touchend, les coordonnées sont dans changedTouches
    let clientX, clientY;
    if (event.changedTouches && event.changedTouches.length > 0) {
        clientX = event.changedTouches[0].clientX;
        clientY = event.changedTouches[0].clientY;
    } else if (event.touches && event.touches.length > 0) {
        clientX = event.touches[0].clientX;
        clientY = event.touches[0].clientY;
    } else {
        clientX = event.clientX;
        clientY = event.clientY;
    }

    const x = clientX - rect.left;
    const y = clientY - rect.top;

    // Inversion de la projection pour obtenir RA/DEC
    try {
        const eq = Celestial.mapProjection.invert([x, y]);
        if (!eq || isNaN(eq[0])) return;

        const ra = eq[0];
        const dec = eq[1];

        const clicked = findNearestCelestialObject(ra, dec);

        if (clicked) {
            const name = clicked.properties.name || clicked.id || "Objet inconnu";
            const type = clicked.type || "Inconnu";
            console.log(`Objet détecté : ${name}`);
            alert(`Objet : ${name}\nType : ${type}`);
        }
    } catch (err) {
        console.error("Erreur de projection :", err);
    }
}

function findNearestCelestialObject(raClick, decClick) {
    let nearest = null;
    let minDist = Infinity;

    const sources = ["planets", "stars", "dsos"];

    // Tolérance accrue sur mobile : le doigt est moins précis qu'un curseur
    const isMobile = window.innerWidth < 768;
    const tolerance = isMobile ? 3.0 : 0.8;

    sources.forEach(type => {
        const list = Celestial.data ? Celestial.data[type] : null;
        if (!list || !list.features) return;

        list.features.forEach(obj => {
            let ra, dec;
            if (obj.properties && obj.properties.ra !== undefined) {
                ra = obj.properties.ra;
                dec = obj.properties.dec;
            } else if (obj.geometry && obj.geometry.coordinates) {
                ra = obj.geometry.coordinates[0];
                dec = obj.geometry.coordinates[1];
            }

            if (ra === undefined || dec === undefined) return;

            const dist = angularDistance(ra, dec, raClick, decClick);

            if (dist < minDist) {
                minDist = dist;
                nearest = obj;
            }
        });
    });

    return minDist < tolerance ? nearest : null;
}

function angularDistance(ra1, dec1, ra2, dec2) {
    const rad = Math.PI / 180;
    const phi1 = dec1 * rad;
    const phi2 = dec2 * rad;
    const deltaLambda = (ra1 - ra2) * rad;

    // Formule de la loi des cosinus pour la distance angulaire
    return Math.acos(
        Math.sin(phi1) * Math.sin(phi2) +
        Math.cos(phi1) * Math.cos(phi2) * Math.cos(deltaLambda)
    ) / rad;
}