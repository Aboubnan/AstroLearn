// solar_system.js - VERSION AMÉLIORÉE
let scene, camera, renderer, controls;
let planets = [];
let sun;
let isPaused = false;
let animationSpeed = 1;

const planetData = {
    sun: { 
        name: "Soleil", 
        distance: 0, 
        diameter: 1.392e6, 
        color: 0xfdb813,
        emissive: 0xfdb813,
        info: "Étoile centrale du système solaire. Température : 5 778 K.",
        rotationSpeed: 0.002,
        orbitSpeed: 0
    },
    mercury: { 
        name: "Mercure", 
        distance: 15, 
        diameter: 4879, 
        color: 0x8c7853,
        info: "La plus petite planète et la plus proche du Soleil. Température extrême : -173°C à 427°C.",
        rotationSpeed: 0.01,
        orbitSpeed: 0.00048
    },
    venus: { 
        name: "Vénus", 
        distance: 22, 
        diameter: 12104, 
        color: 0xffc649,
        info: "Planète sœur de la Terre. Atmosphère toxique de CO₂. Température : 462°C.",
        rotationSpeed: 0.005,
        orbitSpeed: 0.00035
    },
    earth: { 
        name: "Terre", 
        distance: 30, 
        diameter: 12756, 
        color: 0x6b93d6,
        info: "Notre planète bleue. Seule planète connue abritant la vie. 71% d'eau.",
        rotationSpeed: 0.015,
        orbitSpeed: 0.0003
    },
    mars: { 
        name: "Mars", 
        distance: 38, 
        diameter: 6792, 
        color: 0xc1440e,
        info: "La planète rouge. Volcans géants et canyons profonds. Température : -125°C à 20°C.",
        rotationSpeed: 0.014,
        orbitSpeed: 0.00024
    },
    jupiter: { 
        name: "Jupiter", 
        distance: 55, 
        diameter: 142984, 
        color: 0xd8ca9d,
        info: "Géante gazeuse. Grande Tache Rouge : tempête de 350 ans. 79 lunes connues.",
        rotationSpeed: 0.025,
        orbitSpeed: 0.00013
    },
    saturn: { 
        name: "Saturne", 
        distance: 75, 
        diameter: 120536, 
        color: 0xfad5a5,
        info: "Célèbre pour ses anneaux spectaculaires. Densité < eau. 82 lunes.",
        rotationSpeed: 0.022,
        orbitSpeed: 0.0001,
        hasRings: true
    },
    uranus: { 
        name: "Uranus", 
        distance: 95, 
        diameter: 51118, 
        color: 0x4fd0e7,
        info: "Planète glacée inclinée à 98°. Méthane dans l'atmosphère. -224°C.",
        rotationSpeed: 0.018,
        orbitSpeed: 0.00007,
        tilt: Math.PI / 2
    },
    neptune: { 
        name: "Neptune", 
        distance: 115, 
        diameter: 49528, 
        color: 0x4b70dd,
        info: "Planète la plus éloignée. Vents les plus rapides du système solaire (2 000 km/h).",
        rotationSpeed: 0.017,
        orbitSpeed: 0.00005
    }
};

function init() {
    scene = new THREE.Scene();
    scene.fog = new THREE.Fog(0x000000, 100, 500);
    
    // Fond avec dégradé (noir → bleu foncé)
    const bgCanvas = document.createElement('canvas');
    bgCanvas.width = 2;
    bgCanvas.height = 512;
    const context = bgCanvas.getContext('2d');
    const gradient = context.createLinearGradient(0, 0, 0, 512);
    gradient.addColorStop(0, '#000011');
    gradient.addColorStop(0.5, '#000033');
    gradient.addColorStop(1, '#000000');
    context.fillStyle = gradient;
    context.fillRect(0, 0, 2, 512);
    const texture = new THREE.CanvasTexture(bgCanvas);
    scene.background = texture;

    const container = document.getElementById('solar-system-container');

    // ─── Créer le panneau EN PREMIER pour connaître sa hauteur ───
    createControlPanel();

    const panelHeight = document.getElementById('control-panel').offsetHeight;
    const width  = container.clientWidth;
    const height = container.clientHeight - panelHeight;

    // Caméra
    camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 2000);
    camera.position.set(50, 60, 120);
    camera.lookAt(0, 0, 0);

    // Renderer
    renderer = new THREE.WebGLRenderer({ 
        antialias: true,
        alpha: true,
        powerPreference: "high-performance"
    });
    renderer.setSize(width, height);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;

    // ─── Positionner le canvas SOUS la barre ───
    renderer.domElement.style.position = 'absolute';
    renderer.domElement.style.top      = panelHeight + 'px';
    renderer.domElement.style.left     = '0';
    renderer.domElement.style.width    = '100%';
    container.appendChild(renderer.domElement);

    // Contrôles
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping    = true;
    controls.dampingFactor    = 0.08;
    controls.rotateSpeed      = 0.5;
    controls.zoomSpeed        = 0.8;
    controls.minDistance      = 20;
    controls.maxDistance      = 400;
    controls.maxPolarAngle    = Math.PI / 1.8;
    controls.autoRotate       = false;
    controls.autoRotateSpeed  = 0.3;

    // Lumières
    const ambientLight = new THREE.AmbientLight(0x222244, 0.3);
    scene.add(ambientLight);
    
    const sunLight = new THREE.PointLight(0xffffff, 2, 500);
    sunLight.position.set(0, 0, 0);
    sunLight.castShadow = true;
    sunLight.shadow.camera.near = 0.1;
    sunLight.shadow.camera.far  = 500;
    scene.add(sunLight);

    addEnhancedStars();
    addSun();
    addPlanets();
    addAsteroidBelt();
    setupInteractivity();

    window.addEventListener('resize', onWindowResize, false);
    animate();
    
    console.log('🌌 Système solaire initialisé avec succès !');
}

// ─────────────────────────────────────────────
//  PANNEAU DE CONTRÔLE  (barre horizontale fixe)
// ─────────────────────────────────────────────
function createControlPanel() {
    const container = document.getElementById('solar-system-container');

    const panel = document.createElement('div');
    panel.id = 'control-panel';
    panel.style.cssText = `
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        width: 100%;
        background: rgba(0, 0, 20, 0.92);
        padding: 8px 12px;
        border-bottom: 2px solid #ff8811;
        color: white;
        font-family: Arial, sans-serif;
        z-index: 20;
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 10px;
        box-sizing: border-box;
    `;

    panel.innerHTML = `
        <span style="color:#ff8811;font-weight:bold;font-size:13px;">⚙️ Contrôles</span>

        <button id="playPauseBtn" style="padding:5px 12px;background:#ff8811;border:none;border-radius:5px;color:white;cursor:pointer;font-weight:bold;font-size:13px;">
            ⏸️ Pause
        </button>

        <div style="display:flex;align-items:center;gap:6px;font-size:13px;">
            <label>Vitesse : <span id="speedValue">1x</span></label>
            <input type="range" id="speedSlider" min="0.1" max="5" step="0.1" value="1" style="width:80px;">
        </div>

        <button id="resetBtn" style="padding:5px 12px;background:#4b70dd;border:none;border-radius:5px;color:white;cursor:pointer;font-size:13px;">
            🔄 Réinitialiser
        </button>

        <label style="display:flex;align-items:center;gap:5px;font-size:13px;">
            <input type="checkbox" id="autoRotateCheck"> Rotation auto
        </label>

        <label style="display:flex;align-items:center;gap:5px;font-size:13px;">
            <input type="checkbox" id="labelsCheck"> Afficher noms
        </label>
    `;

    // ✅ Injecter AVANT d'attacher les listeners
    container.insertBefore(panel, container.firstChild);

    // ── Listeners ──────────────────────────────
    document.getElementById('playPauseBtn').addEventListener('click', () => {
        isPaused = !isPaused;
        document.getElementById('playPauseBtn').innerHTML = isPaused ? '▶️ Lecture' : '⏸️ Pause';
    });

    document.getElementById('speedSlider').addEventListener('input', (e) => {
        animationSpeed = parseFloat(e.target.value);
        document.getElementById('speedValue').textContent = animationSpeed.toFixed(1) + 'x';
    });

    document.getElementById('resetBtn').addEventListener('click', () => {
        camera.position.set(50, 60, 120);
        camera.lookAt(0, 0, 0);
        controls.reset();
        animationSpeed = 1;
        isPaused = false;
        document.getElementById('speedSlider').value = 1;
        document.getElementById('speedValue').textContent = '1x';
        document.getElementById('playPauseBtn').innerHTML = '⏸️ Pause';
    });

    document.getElementById('autoRotateCheck').addEventListener('change', (e) => {
        controls.autoRotate = e.target.checked;
    });

    document.getElementById('labelsCheck').addEventListener('change', (e) => {
        planets.forEach(planet => {
            if (planet.userData.label) {
                planet.userData.label.visible = e.target.checked;
            }
        });
    });
}

// ─────────────────────────────────────────────
//  ÉTOILES
// ─────────────────────────────────────────────
function addEnhancedStars() {
    const starGeometry = new THREE.BufferGeometry();
    const starMaterial = new THREE.PointsMaterial({ 
        color: 0xffffff, 
        size: 2,
        transparent: true,
        opacity: 0.8,
        sizeAttenuation: true
    });
    
    const starVertices = [];
    for (let i = 0; i < 5000; i++) {
        const radius = 800 + Math.random() * 500;
        const theta  = Math.random() * Math.PI * 2;
        const phi    = Math.random() * Math.PI;
        starVertices.push(
            radius * Math.sin(phi) * Math.cos(theta),
            radius * Math.sin(phi) * Math.sin(theta),
            radius * Math.cos(phi)
        );
    }
    starGeometry.setAttribute('position', new THREE.Float32BufferAttribute(starVertices, 3));
    scene.add(new THREE.Points(starGeometry, starMaterial));
    
    const nearStarGeometry = new THREE.BufferGeometry();
    const nearStarMaterial = new THREE.PointsMaterial({ 
        color: 0xaaccff, 
        size: 1.5,
        transparent: true,
        opacity: 0.6
    });
    const nearStarVertices = [];
    for (let i = 0; i < 2000; i++) {
        nearStarVertices.push(
            (Math.random() - 0.5) * 1000,
            (Math.random() - 0.5) * 1000,
            (Math.random() - 0.5) * 1000
        );
    }
    nearStarGeometry.setAttribute('position', new THREE.Float32BufferAttribute(nearStarVertices, 3));
    scene.add(new THREE.Points(nearStarGeometry, nearStarMaterial));
}

// ─────────────────────────────────────────────
//  SOLEIL
// ─────────────────────────────────────────────
function addSun() {
    const sunRadius = 8;
    const sunGeometry = new THREE.SphereGeometry(sunRadius, 64, 64);
    const sunMaterial = new THREE.MeshBasicMaterial({ color: 0xfdb813 });
    
    sun = new THREE.Mesh(sunGeometry, sunMaterial);
    sun.userData = planetData.sun;
    scene.add(sun);
    
    const glowGeometry = new THREE.SphereGeometry(sunRadius * 1.3, 32, 32);
    const glowMaterial = new THREE.MeshBasicMaterial({
        color: 0xffaa44,
        transparent: true,
        opacity: 0.3,
        side: THREE.BackSide
    });
    sun.add(new THREE.Mesh(glowGeometry, glowMaterial));
    
    const coronaGeometry = new THREE.SphereGeometry(sunRadius * 1.5, 32, 32);
    const coronaMaterial = new THREE.MeshBasicMaterial({
        color: 0xff6600,
        transparent: true,
        opacity: 0.15,
        side: THREE.BackSide
    });
    sun.add(new THREE.Mesh(coronaGeometry, coronaMaterial));
    
    planets.push(sun);
}

// ─────────────────────────────────────────────
//  PLANÈTES
// ─────────────────────────────────────────────
function addPlanets() {
    Object.keys(planetData).forEach((key) => {
        if (key === 'sun') return;
        
        const data     = planetData[key];
        const radius   = Math.log(data.diameter) * 0.18;
        const geometry = new THREE.SphereGeometry(radius, 32, 32);
        const material = new THREE.MeshPhongMaterial({ 
            color: data.color,
            shininess: 10,
            specular: 0x222222
        });

        const planet = new THREE.Mesh(geometry, material);
        planet.position.x  = data.distance;
        planet.userData    = data;
        planet.castShadow  = true;
        planet.receiveShadow = true;
        
        if (data.tilt) planet.rotation.z = data.tilt;
        
        scene.add(planet);
        planets.push(planet);

        // Orbite
        const orbitCurve    = new THREE.EllipseCurve(0, 0, data.distance, data.distance, 0, 2 * Math.PI, false, 0);
        const orbitPoints   = orbitCurve.getPoints(128);
        const orbitGeometry = new THREE.BufferGeometry().setFromPoints(orbitPoints);
        const orbitMaterial = new THREE.LineBasicMaterial({ color: 0x444466, transparent: true, opacity: 0.4 });
        const orbit         = new THREE.Line(orbitGeometry, orbitMaterial);
        orbit.rotation.x    = Math.PI / 2;
        scene.add(orbit);

        // Anneaux de Saturne
        if (data.hasRings) {
            const ringGeometry = new THREE.RingGeometry(radius * 1.4, radius * 2.8, 64);
            const ringMaterial = new THREE.MeshBasicMaterial({ 
                color: 0xccaa88,
                side: THREE.DoubleSide,
                transparent: true,
                opacity: 0.7
            });
            const ringCanvas = document.createElement('canvas');
            ringCanvas.width  = 512;
            ringCanvas.height = 1;
            const ctx      = ringCanvas.getContext('2d');
            const ringGrad = ctx.createLinearGradient(0, 0, 512, 0);
            ringGrad.addColorStop(0,   'rgba(200,170,130,0)');
            ringGrad.addColorStop(0.2, 'rgba(200,170,130,0.8)');
            ringGrad.addColorStop(0.5, 'rgba(220,190,150,1)');
            ringGrad.addColorStop(0.8, 'rgba(200,170,130,0.8)');
            ringGrad.addColorStop(1,   'rgba(200,170,130,0)');
            ctx.fillStyle = ringGrad;
            ctx.fillRect(0, 0, 512, 1);
            ringMaterial.map = new THREE.CanvasTexture(ringCanvas);
            ringMaterial.needsUpdate = true;
            const ring = new THREE.Mesh(ringGeometry, ringMaterial);
            ring.rotation.x = Math.PI / 2;
            planet.add(ring);
        }
        
        addPlanetLabel(planet, data.name);
    });
}

function addPlanetLabel(planet, name) {
    const canvas  = document.createElement('canvas');
    const context = canvas.getContext('2d');
    canvas.width  = 256;
    canvas.height = 64;
    context.fillStyle = 'rgba(0,0,0,0.6)';
    context.fillRect(0, 0, 256, 64);
    context.font      = 'Bold 24px Arial';
    context.fillStyle = '#ffffff';
    context.textAlign = 'center';
    context.fillText(name, 128, 40);
    
    const spriteMaterial = new THREE.SpriteMaterial({ 
        map: new THREE.CanvasTexture(canvas),
        transparent: true,
        opacity: 0.8
    });
    const sprite = new THREE.Sprite(spriteMaterial);
    sprite.scale.set(8, 2, 1);
    sprite.position.y        = planet.geometry.parameters.radius * 2;
    sprite.visible           = false;
    planet.userData.label    = sprite;
    planet.add(sprite);
}

// ─────────────────────────────────────────────
//  CEINTURE D'ASTÉROÏDES
// ─────────────────────────────────────────────
function addAsteroidBelt() {
    const asteroidGeometry = new THREE.SphereGeometry(0.1, 6, 6);
    const asteroidMaterial = new THREE.MeshPhongMaterial({ color: 0x665544, shininess: 2 });
    
    for (let i = 0; i < 800; i++) {
        const asteroid = new THREE.Mesh(asteroidGeometry, asteroidMaterial);
        const distance = 45 + Math.random() * 5;
        const angle    = Math.random() * Math.PI * 2;
        asteroid.position.set(
            distance * Math.cos(angle),
            (Math.random() - 0.5) * 2,
            distance * Math.sin(angle)
        );
        asteroid.userData = { 
            orbitRadius: distance,
            orbitAngle:  angle,
            orbitSpeed:  0.0001 + Math.random() * 0.0001
        };
        scene.add(asteroid);
        planets.push(asteroid);
    }
}

// ─────────────────────────────────────────────
//  INTERACTIVITÉ (hover + clic)
// ─────────────────────────────────────────────
function setupInteractivity() {
    const raycaster = new THREE.Raycaster();
    const mouse     = new THREE.Vector2();
    let hoveredPlanet = null;

    renderer.domElement.addEventListener('mousemove', (event) => {
        const rect = renderer.domElement.getBoundingClientRect();
        mouse.x =  ((event.clientX - rect.left)  / rect.width)  * 2 - 1;
        mouse.y = -((event.clientY - rect.top)    / rect.height) * 2 + 1;

        raycaster.setFromCamera(mouse, camera);
        const intersects = raycaster.intersectObjects(planets.filter(p => p.userData.name));

        if (intersects.length > 0) {
            const planet = intersects[0].object;
            if (hoveredPlanet !== planet) {
                if (hoveredPlanet?.userData.label) hoveredPlanet.userData.label.visible = false;
                hoveredPlanet = planet;
                if (planet.userData.label) planet.userData.label.visible = true;
                renderer.domElement.style.cursor = 'pointer';
            }
        } else {
            if (hoveredPlanet?.userData.label) {
                if (!document.getElementById('labelsCheck').checked) {
                    hoveredPlanet.userData.label.visible = false;
                }
            }
            hoveredPlanet = null;
            renderer.domElement.style.cursor = 'default';
        }
    });

    renderer.domElement.addEventListener('click', (event) => {
        const rect = renderer.domElement.getBoundingClientRect();
        mouse.x =  ((event.clientX - rect.left)  / rect.width)  * 2 - 1;
        mouse.y = -((event.clientY - rect.top)    / rect.height) * 2 + 1;

        raycaster.setFromCamera(mouse, camera);
        const intersects = raycaster.intersectObjects(planets.filter(p => p.userData.name));
        if (intersects.length > 0) showModal(intersects[0].object.userData);
    });
}

// ─────────────────────────────────────────────
//  ANIMATION
// ─────────────────────────────────────────────
function animate() {
    requestAnimationFrame(animate);

    if (!isPaused) {
        const time = Date.now() * 0.001 * animationSpeed;
        
        planets.forEach((planet) => {
            if (planet.userData.rotationSpeed) {
                planet.rotation.y += planet.userData.rotationSpeed * animationSpeed;
            }
            if (planet.userData.orbitSpeed && planet.userData.distance) {
                const angle = time * planet.userData.orbitSpeed;
                planet.position.x = planet.userData.distance * Math.cos(angle);
                planet.position.z = planet.userData.distance * Math.sin(angle);
            }
            if (planet.userData.orbitRadius) {
                planet.userData.orbitAngle += planet.userData.orbitSpeed * animationSpeed;
                planet.position.x = planet.userData.orbitRadius * Math.cos(planet.userData.orbitAngle);
                planet.position.z = planet.userData.orbitRadius * Math.sin(planet.userData.orbitAngle);
            }
        });
        
        if (sun) {
            const pulse = 1 + Math.sin(Date.now() * 0.002) * 0.02;
            sun.scale.set(pulse, pulse, pulse);
        }
    }

    controls.update();
    renderer.render(scene, camera);
}

// ─────────────────────────────────────────────
//  MODAL INFO PLANÈTE
// ─────────────────────────────────────────────
function showModal(data) {
    const modal = document.getElementById('planet-modal');
    document.getElementById('modal-title').textContent = data.name;
    document.getElementById('modal-info').textContent  = data.info;
    modal.style.display       = 'block';
    modal.style.backdropFilter = 'blur(10px)';
}

function closeModal() {
    document.getElementById('planet-modal').style.display = 'none';
}

// ─────────────────────────────────────────────
//  RESPONSIVE
// ─────────────────────────────────────────────
function onWindowResize() {
    const container   = document.getElementById('solar-system-container');
    const panel       = document.getElementById('control-panel');
    const panelHeight = panel ? panel.offsetHeight : 0;
    const width       = container.clientWidth;
    const height      = container.clientHeight - panelHeight;

    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    renderer.setSize(width, height);
    renderer.domElement.style.top = panelHeight + 'px';
}

// ─────────────────────────────────────────────
//  INIT
// ─────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", init);