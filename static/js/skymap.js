/* JavaScript pour la Carte Stellaire - Version Tactile */

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
        type: "svg"
    };

    Celestial.display(config, function(error) {
        if (error) return;
        
        const svg = container.querySelector("svg");
        if (svg) {
            svg.style.cursor = "pointer";
            
            // On utilise une fonction nommée pour pouvoir gérer Click et Touch
            const handleAction = (e) => {
                // Empêche le zoom natif du navigateur sur le double tap
                if (e.type === 'touchstart') e.preventDefault();
                handleSvgClick(e, svg);
            };

            svg.addEventListener("click", handleAction);
            svg.addEventListener("touchstart", handleAction, {passive: false});
        }
    });
}

function handleSvgClick(event, svg) {
    const rect = svg.getBoundingClientRect();
    
    // Récupération des coordonnées (Souris ou Doigt)
    const clientX = event.touches ? event.touches[0].clientX : event.clientX;
    const clientY = event.touches ? event.touches[0].clientY : event.clientY;

    const x = clientX - rect.left;
    const y = clientY - rect.top;

    const eq = Celestial.mapProjection.invert([x, y]);

    if (!eq || isNaN(eq[0])) return;

    const ra = eq[0];
    const dec = eq[1];

    const clicked = findNearestCelestialObject(ra, dec);

    if (clicked) {
        const name = clicked.properties.name || clicked.id || "Objet inconnu";
        const type = clicked.type || "Inconnu";
        alert(`Objet : ${name}\nType : ${type}`);
    }
}

function findNearestCelestialObject(raClick, decClick) {
    let nearest = null;
    let minDist = Infinity;
    const sources = ["stars", "dsos", "planets"];

    // Tolérance : 2.0 sur mobile (largeur d'un doigt), 0.5 sur PC
    const tolerance = window.innerWidth < 768 ? 2.0 : 0.5;

    sources.forEach(type => {
        const list = Celestial.data[type];
        if (!list || !list.features) return;

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

    return minDist < tolerance ? nearest : null;
}

function angularDistance(ra1, dec1, ra2, dec2) {
    const rad = Math.PI / 180;
    ra1 *= rad; dec1 *= rad; ra2 *= rad; dec2 *= rad;
    return Math.acos(
        Math.sin(dec1) * Math.sin(dec2) +
        Math.cos(dec1) * Math.cos(dec2) * Math.cos(ra1 - ra2)
    ) / rad;
}