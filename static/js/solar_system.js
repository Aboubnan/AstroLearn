// solar_system.js - VERSION FINALE NETTOYÉE, ENRICHIE ET MOBILE
let scene, camera, renderer, controls;
let planets = [];
let sun;
let isPaused = false;
let animationSpeed = 1;

const planetData = {
    sun: {
        name: "Soleil", distance: 0, diameter: 1.392e6, color: 0xfdb813,
        info: "Étoile centrale du système solaire (type G2V). Température de surface : 5 778 K. Il contient 99,86 % de la masse totale du système et sa gravité maintient toutes les planètes en orbite.",
        rotationSpeed: 0.005, orbitSpeed: 0
    },
    mercury: {
        name: "Mercure", distance: 25, diameter: 4879, color: 0x8c7853, rotationSpeed: 0.01, orbitSpeed: 0.04,
        info: "La plus petite planète et la plus proche du Soleil. Son année ne dure que 88 jours. Dépourvue d'atmosphère, ses températures varient de -173°C la nuit à 427°C le jour."
    },
    venus: {
        name: "Vénus", distance: 40, diameter: 12104, color: 0xffc649, rotationSpeed: 0.005, orbitSpeed: 0.015,
        info: "Souvent appelée 'étoile du Berger'. C'est la planète la plus chaude (462°C) à cause d'un effet de serre massif provoqué par son atmosphère dense en CO₂. Elle tourne dans le sens inverse des autres planètes."
    },
    earth: {
        name: "Terre", distance: 55, diameter: 12756, color: 0x6b93d6, rotationSpeed: 0.015, orbitSpeed: 0.01,
        info: "Notre maison. La seule planète connue abritant la vie. Sa surface est recouverte à 71% d'eau liquide. Elle possède un satellite naturel, la Lune."
    },
    mars: {
        name: "Mars", distance: 70, diameter: 6792, color: 0xc1440e, rotationSpeed: 0.014, orbitSpeed: 0.008,
        info: "La planète rouge. Elle possède le plus haut volcan du système solaire, l'Olympus Mons (21 km de haut), et d'immenses canyons. Des traces d'eau liquide ancienne y ont été découvertes."
    },
    jupiter: {
        name: "Jupiter", distance: 100, diameter: 142984, color: 0xd8ca9d, rotationSpeed: 0.025, orbitSpeed: 0.004,
        info: "La plus grande planète, une géante gazeuse. Sa Grande Tache Rouge est une tempête anticyclonique plus grande que la Terre, active depuis au moins 350 ans. Elle possède 79 lunes connues."
    },
    saturn: {
        name: "Saturne", distance: 130, diameter: 120536, color: 0xfad5a5, rotationSpeed: 0.022, orbitSpeed: 0.002, hasRings: true,
        info: "Célèbre pour ses anneaux spectaculaires composés de glace et de poussière. Moins dense que l'eau, elle flotterait si on la plongeait dans un océan géant. Elle possède 82 lunes."
    },
    uranus: {
        name: "Uranus", distance: 160, diameter: 51118, color: 0x4fd0e7, rotationSpeed: 0.018, orbitSpeed: 0.0011,
        info: "Une géante de glace de couleur cyan. Sa particularité est d'avoir son axe de rotation incliné à 98°, elle 'roule' donc sur son orbite. Elle possède 27 lunes."
    },
    neptune: {
        name: "Neptune", distance: 190, diameter: 49528, color: 0x4b70dd, rotationSpeed: 0.017, orbitSpeed: 0.0009,
        info: "La planète la plus éloignée du Soleil. Les vents y soufflent à plus de 2 000 km/h, les plus rapides du système solaire. C'est une géante glacée et venteuse possédant 14 lunes."
    }
};

function init() {
    scene = new THREE.Scene();
    const container = document.getElementById('solar-system-container');

    createControlPanel();
    const pHeight = document.getElementById('control-panel').offsetHeight;

    camera = new THREE.PerspectiveCamera(60, container.clientWidth / (container.clientHeight - pHeight), 0.1, 2000);
    camera.position.set(150, 100, 250);

    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(container.clientWidth, container.clientHeight - pHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.domElement.style.position = 'absolute';
    renderer.domElement.style.top = pHeight + 'px';

    // CORRECTION MOBILE : désactive le comportement touch natif sur le canvas
    // pour que OrbitControls et nos listeners touchend soient prioritaires
    renderer.domElement.style.touchAction = 'none';

    container.appendChild(renderer.domElement);

    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.autoRotate = true;
    controls.autoRotateSpeed = 0.5;

    setupLights();
    addEnhancedStars();
    addSun();
    addPlanets();
    setupInteractivity();
    updateCelestialCounter();

    window.addEventListener('resize', onWindowResize);
    animate();
}

function createControlPanel() {
    const container = document.getElementById('solar-system-container');
    const panel = document.createElement('div');
    panel.id = 'control-panel';
    panel.style.cssText = `
        position: absolute; top: 0; left: 0; width: 100%; background: #0a0a1e;
        padding: 10px; border-bottom: 2px solid #FF8811; color: white;
        z-index: 100; display: flex; align-items: center; justify-content: center; gap: 20px; flex-wrap: wrap;
    `;

    panel.innerHTML = `
        <button id="playPauseBtn" style="background:#FF8811; border:none; color:white; padding:8px 15px; border-radius:5px; cursor:pointer; font-weight:bold;">⏸️ PAUSE TOTALE</button>
        <div style="display:flex; align-items:center; gap:10px;">
            <label>Vitesse</label>
            <input type="range" id="speedSlider" min="0" max="10" step="0.1" value="1">
            <span id="speedValue">1x</span>
        </div>
        <label><input type="checkbox" id="labelsCheck"> Afficher les noms</label>
    `;
    container.insertBefore(panel, container.firstChild);

    document.getElementById('playPauseBtn').onclick = function() {
        isPaused = !isPaused;
        controls.autoRotate = !isPaused;
        this.innerHTML = isPaused ? '▶️ REPRENDRE' : '⏸️ PAUSE TOTALE';
        this.style.background = isPaused ? '#4caf50' : '#FF8811';
    };

    document.getElementById('speedSlider').oninput = function() {
        animationSpeed = parseFloat(this.value);
        document.getElementById('speedValue').innerText = animationSpeed.toFixed(1) + 'x';
    };

    document.getElementById('labelsCheck').onchange = function() {
        planets.forEach(p => { if (p.userData.label) p.userData.label.visible = this.checked; });
    };
}

function addPlanets() {
    Object.keys(planetData).forEach((key) => {
        if (key === 'sun') return;
        const data = planetData[key];
        const radius = Math.log(data.diameter) * 0.25;

        const planet = new THREE.Mesh(
            new THREE.SphereGeometry(radius, 32, 32),
            new THREE.MeshPhongMaterial({ color: data.color, shininess: 20 })
        );
        planet.userData = data;
        planet.userData.currentAngle = Math.random() * Math.PI * 2;

        const label = createLabel(data.name, radius);
        planet.add(label);
        planet.userData.label = label;

        const orbitGeometry = new THREE.RingGeometry(data.distance - 0.2, data.distance + 0.2, 128);
        const orbitMaterial = new THREE.MeshBasicMaterial({ color: 0xffffff, side: THREE.DoubleSide, transparent: true, opacity: 0.15 });
        const orbit = new THREE.Mesh(orbitGeometry, orbitMaterial);
        orbit.rotation.x = Math.PI / 2;
        scene.add(orbit);

        scene.add(planet);
        planets.push(planet);

        if (data.hasRings) {
            const ring = new THREE.Mesh(
                new THREE.RingGeometry(radius * 1.5, radius * 2.8, 64),
                new THREE.MeshBasicMaterial({ color: 0xaaaaaa, side: THREE.DoubleSide, transparent: true, opacity: 0.4 })
            );
            ring.rotation.x = Math.PI / 2;
            planet.add(ring);
        }
    });
}

function createLabel(name, radius) {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = 320;
    canvas.height = 128;
    ctx.font = "Bold 64px Arial";
    ctx.fillStyle = "white";
    ctx.textAlign = "center";
    ctx.fillText(name, 160, 80);
    const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(canvas), transparent: true }));
    sprite.scale.set(20, 5, 1);
    sprite.position.y = radius + 6;
    sprite.visible = false;
    return sprite;
}

function animate() {
    requestAnimationFrame(animate);

    if (!isPaused) {
        planets.forEach((planet) => {
            if (planet.userData.rotationSpeed) planet.rotation.y += planet.userData.rotationSpeed * animationSpeed;
            if (planet.userData.orbitSpeed && planet.userData.distance) {
                planet.userData.currentAngle += (planet.userData.orbitSpeed * 0.1) * animationSpeed;
                planet.position.x = planet.userData.distance * Math.cos(planet.userData.currentAngle);
                planet.position.z = planet.userData.distance * Math.sin(planet.userData.currentAngle);
            }
        });
        if (sun) sun.rotation.y += 0.001 * animationSpeed;
        controls.update();
    }

    renderer.render(scene, camera);
}

// --- Fonctions utilitaires ---
function setupLights() {
    scene.add(new THREE.AmbientLight(0x444444));
    const light = new THREE.PointLight(0xffffff, 2, 1000);
    scene.add(light);
}

function addSun() {
    sun = new THREE.Mesh(new THREE.SphereGeometry(15, 64, 64), new THREE.MeshBasicMaterial({ color: 0xfdb813 }));
    sun.userData = planetData.sun;
    const label = createLabel("Soleil", 15);
    sun.add(label);
    sun.userData.label = label;
    scene.add(sun);
    planets.push(sun);
}

function addEnhancedStars() {
    const geo = new THREE.BufferGeometry();
    const pos = [];
    for (let i = 0; i < 8000; i++) {
        pos.push((Math.random() - 0.5) * 2000, (Math.random() - 0.5) * 2000, (Math.random() - 0.5) * 2000);
    }
    geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
    scene.add(new THREE.Points(geo, new THREE.PointsMaterial({ color: 0xffffff, size: 0.6 })));
}

function setupInteractivity() {
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

    // Fonction partagée pour extraire les coordonnées (click souris ou touch)
    function getEventCoords(e) {
        if (e.changedTouches && e.changedTouches.length > 0) {
            return { x: e.changedTouches[0].clientX, y: e.changedTouches[0].clientY };
        }
        return { x: e.clientX, y: e.clientY };
    }

    // Fonction partagée de raycasting
    function handleCanvasInteraction(e) {
        const rect = renderer.domElement.getBoundingClientRect();
        const { x: clientX, y: clientY } = getEventCoords(e);

        mouse.x = ((clientX - rect.left) / rect.width) * 2 - 1;
        mouse.y = -((clientY - rect.top) / rect.height) * 2 + 1;

        raycaster.setFromCamera(mouse, camera);
        const intersects = raycaster.intersectObjects(planets.filter(p => p.userData.name));
        if (intersects.length > 0) {
            showModal(intersects[0].object.userData);
        }
    }

    // CORRECTION MOBILE : variables pour détecter scroll vs tap
    let touchStartX = 0;
    let touchStartY = 0;

    renderer.domElement.addEventListener('touchstart', (e) => {
        touchStartX = e.touches[0].clientX;
        touchStartY = e.touches[0].clientY;
    }, { passive: true });

    // Click PC classique
    renderer.domElement.addEventListener('click', handleCanvasInteraction);

    // Touch mobile : on déclenche seulement si c'est un tap (pas un drag/zoom)
    renderer.domElement.addEventListener('touchend', (e) => {
        const dx = Math.abs(e.changedTouches[0].clientX - touchStartX);
        const dy = Math.abs(e.changedTouches[0].clientY - touchStartY);

        // Si le doigt n'a pas bougé de plus de 10px = c'est un tap, pas un scroll
        if (dx < 10 && dy < 10) {
            e.preventDefault(); // Empêche le click synthétique 300ms après
            handleCanvasInteraction(e);
        }
    }, { passive: false });
}

function onWindowResize() {
    const container = document.getElementById('solar-system-container');
    const pHeight = document.getElementById('control-panel').offsetHeight;
    camera.aspect = container.clientWidth / (container.clientHeight - pHeight);
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight - pHeight);
}

function showModal(data) {
    document.getElementById('modal-title').innerText = data.name;
    document.getElementById('modal-info').innerText = data.info;
    document.getElementById('planet-modal').style.display = 'block';
}

function closeModal() {
    document.getElementById('planet-modal').style.display = 'none';
}

function updateCelestialCounter() {
    const counterElement = document.getElementById('celestial-counter');
    if (!counterElement) return;

    const target = planets.length; // Récupère le nombre réel (ex: 809)
    const duration = 2000; // Animation de 2 secondes
    const start = 0;
    const startTime = performance.now();

    function animateCounter(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Calcul du nombre actuel avec un effet d'accélération/décélération
        const currentCount = Math.floor(progress * target);
        counterElement.innerText = currentCount;

        if (progress < 1) {
            requestAnimationFrame(animateCounter);
        } else {
            counterElement.innerText = target;
        }
    }

    requestAnimationFrame(animateCounter);
}

document.addEventListener("DOMContentLoaded", init);