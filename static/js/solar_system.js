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
    // Scène avec fond spatial dégradé
    scene = new THREE.Scene();
    scene.fog = new THREE.Fog(0x000000, 100, 500);
    
    // Fond avec dégradé (noir → bleu foncé)
    const canvas = document.createElement('canvas');
    canvas.width = 2;
    canvas.height = 512;
    const context = canvas.getContext('2d');
    const gradient = context.createLinearGradient(0, 0, 0, 512);
    gradient.addColorStop(0, '#000011');
    gradient.addColorStop(0.5, '#000033');
    gradient.addColorStop(1, '#000000');
    context.fillStyle = gradient;
    context.fillRect(0, 0, 2, 512);
    
    const texture = new THREE.CanvasTexture(canvas);
    scene.background = texture;

    // Caméra
    const container = document.getElementById('solar-system-container');
    const width = container.clientWidth;
    const height = container.clientHeight || 700;
    
    camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 2000);
    camera.position.set(50, 60, 120);
    camera.lookAt(0, 0, 0);

    // Renderer avec antialiasing
    renderer = new THREE.WebGLRenderer({ 
        antialias: true,
        alpha: true,
        powerPreference: "high-performance"
    });
    renderer.setSize(width, height);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    container.appendChild(renderer.domElement);

    // Contrôles améliorés
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.rotateSpeed = 0.5;
    controls.zoomSpeed = 0.8;
    controls.minDistance = 20;
    controls.maxDistance = 400;
    controls.maxPolarAngle = Math.PI / 1.8;
    controls.autoRotate = false;
    controls.autoRotateSpeed = 0.3;

    // Lumières améliorées
    const ambientLight = new THREE.AmbientLight(0x222244, 0.3);
    scene.add(ambientLight);
    
    // Lumière principale du Soleil
    const sunLight = new THREE.PointLight(0xffffff, 2, 500);
    sunLight.position.set(0, 0, 0);
    sunLight.castShadow = true;
    sunLight.shadow.camera.near = 0.1;
    sunLight.shadow.camera.far = 500;
    scene.add(sunLight);

    // Champ d'étoiles dense et animé
    addEnhancedStars();
    
    // Ajouter le Soleil
    addSun();
    
    // Ajouter les planètes
    addPlanets();
    
    // Ajouter la ceinture d'astéroïdes
    addAsteroidBelt();

    // Panneau de contrôle
    createControlPanel();

    // Gestion des clics (info-bulles)
    setupInteractivity();

    // Responsive
    window.addEventListener('resize', onWindowResize, false);

    // Animation
    animate();
    
    console.log('🌌 Système solaire initialisé avec succès !');
}

function addEnhancedStars() {
    // Étoiles lointaines (fond)
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
        const theta = Math.random() * Math.PI * 2;
        const phi = Math.random() * Math.PI;
        
        starVertices.push(
            radius * Math.sin(phi) * Math.cos(theta),
            radius * Math.sin(phi) * Math.sin(theta),
            radius * Math.cos(phi)
        );
    }
    
    starGeometry.setAttribute('position', new THREE.Float32BufferAttribute(starVertices, 3));
    const stars = new THREE.Points(starGeometry, starMaterial);
    scene.add(stars);
    
    // Étoiles proches (scintillantes)
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
    const nearStars = new THREE.Points(nearStarGeometry, nearStarMaterial);
    scene.add(nearStars);
}

function addSun() {
    const sunRadius = 8;
    const sunGeometry = new THREE.SphereGeometry(sunRadius, 64, 64);
    
    // Matériau du Soleil avec émission de lumière
    const sunMaterial = new THREE.MeshBasicMaterial({ 
        color: 0xfdb813,
        emissive: 0xff8800,
        emissiveIntensity: 1
    });
    
    sun = new THREE.Mesh(sunGeometry, sunMaterial);
    sun.userData = planetData.sun;
    scene.add(sun);
    
    // Ajouter une lueur autour du Soleil
    const glowGeometry = new THREE.SphereGeometry(sunRadius * 1.3, 32, 32);
    const glowMaterial = new THREE.MeshBasicMaterial({
        color: 0xffaa44,
        transparent: true,
        opacity: 0.3,
        side: THREE.BackSide
    });
    const glow = new THREE.Mesh(glowGeometry, glowMaterial);
    sun.add(glow);
    
    // Couronne solaire
    const coronaGeometry = new THREE.SphereGeometry(sunRadius * 1.5, 32, 32);
    const coronaMaterial = new THREE.MeshBasicMaterial({
        color: 0xff6600,
        transparent: true,
        opacity: 0.15,
        side: THREE.BackSide
    });
    const corona = new THREE.Mesh(coronaGeometry, coronaMaterial);
    sun.add(corona);
    
    planets.push(sun);
}

function addPlanets() {
    Object.keys(planetData).forEach((key, index) => {
        if (key === 'sun') return; // Déjà ajouté
        
        const data = planetData[key];
        const radius = Math.log(data.diameter) * 0.18;
        const geometry = new THREE.SphereGeometry(radius, 32, 32);
        
        // Matériau avec meilleur rendu
        const material = new THREE.MeshPhongMaterial({ 
            color: data.color,
            shininess: 10,
            specular: 0x222222
        });

        const planet = new THREE.Mesh(geometry, material);
        planet.position.x = data.distance;
        planet.userData = data;
        planet.castShadow = true;
        planet.receiveShadow = true;
        
        // Inclinaison pour Uranus
        if (data.tilt) {
            planet.rotation.z = data.tilt;
        }
        
        scene.add(planet);
        planets.push(planet);

        // Orbites élégantes
        const orbitCurve = new THREE.EllipseCurve(
            0, 0,
            data.distance, data.distance,
            0, 2 * Math.PI,
            false,
            0
        );
        
        const orbitPoints = orbitCurve.getPoints(128);
        const orbitGeometry = new THREE.BufferGeometry().setFromPoints(orbitPoints);
        const orbitMaterial = new THREE.LineBasicMaterial({ 
            color: 0x444466,
            transparent: true,
            opacity: 0.4
        });
        
        const orbit = new THREE.Line(orbitGeometry, orbitMaterial);
        orbit.rotation.x = Math.PI / 2;
        scene.add(orbit);

        // Anneaux de Saturne détaillés
        if (data.hasRings) {
            const ringGeometry = new THREE.RingGeometry(radius * 1.4, radius * 2.8, 64);
            const ringMaterial = new THREE.MeshBasicMaterial({ 
                color: 0xccaa88,
                side: THREE.DoubleSide,
                transparent: true,
                opacity: 0.7
            });
            
            // Texture procédurale pour les anneaux
            const canvas = document.createElement('canvas');
            canvas.width = 512;
            canvas.height = 1;
            const ctx = canvas.getContext('2d');
            const gradient = ctx.createLinearGradient(0, 0, 512, 0);
            gradient.addColorStop(0, 'rgba(200, 170, 130, 0)');
            gradient.addColorStop(0.2, 'rgba(200, 170, 130, 0.8)');
            gradient.addColorStop(0.5, 'rgba(220, 190, 150, 1)');
            gradient.addColorStop(0.8, 'rgba(200, 170, 130, 0.8)');
            gradient.addColorStop(1, 'rgba(200, 170, 130, 0)');
            ctx.fillStyle = gradient;
            ctx.fillRect(0, 0, 512, 1);
            
            const ringTexture = new THREE.CanvasTexture(canvas);
            ringMaterial.map = ringTexture;
            ringMaterial.needsUpdate = true;
            
            const ring = new THREE.Mesh(ringGeometry, ringMaterial);
            ring.rotation.x = Math.PI / 2;
            planet.add(ring);
        }
        
        // Label flottant
        addPlanetLabel(planet, data.name);
    });
}

function addPlanetLabel(planet, name) {
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    canvas.width = 256;
    canvas.height = 64;
    
    context.fillStyle = 'rgba(0, 0, 0, 0.6)';
    context.fillRect(0, 0, 256, 64);
    
    context.font = 'Bold 24px Arial';
    context.fillStyle = '#ffffff';
    context.textAlign = 'center';
    context.fillText(name, 128, 40);
    
    const texture = new THREE.CanvasTexture(canvas);
    const spriteMaterial = new THREE.SpriteMaterial({ 
        map: texture,
        transparent: true,
        opacity: 0.8
    });
    
    const sprite = new THREE.Sprite(spriteMaterial);
    sprite.scale.set(8, 2, 1);
    sprite.position.y = planet.geometry.parameters.radius * 2;
    planet.add(sprite);
    sprite.visible = false; // Masqué par défaut
    planet.userData.label = sprite;
}

function addAsteroidBelt() {
    const asteroidCount = 800;
    const asteroidGeometry = new THREE.SphereGeometry(0.1, 6, 6);
    const asteroidMaterial = new THREE.MeshPhongMaterial({ 
        color: 0x665544,
        shininess: 2
    });
    
    for (let i = 0; i < asteroidCount; i++) {
        const asteroid = new THREE.Mesh(asteroidGeometry, asteroidMaterial);
        
        const distance = 45 + Math.random() * 5;
        const angle = Math.random() * Math.PI * 2;
        const height = (Math.random() - 0.5) * 2;
        
        asteroid.position.x = distance * Math.cos(angle);
        asteroid.position.z = distance * Math.sin(angle);
        asteroid.position.y = height;
        
        asteroid.userData = { 
            orbitRadius: distance,
            orbitAngle: angle,
            orbitSpeed: 0.0001 + Math.random() * 0.0001
        };
        
        scene.add(asteroid);
        planets.push(asteroid);
    }
}

function createControlPanel() {
    const panel = document.createElement('div');
    panel.id = 'control-panel';
    panel.style.cssText = `
        position: absolute;
        top: 20px;
        right: 20px;
        background: rgba(0, 0, 20, 0.8);
        padding: 15px;
        border-radius: 10px;
        border: 2px solid #ff8811;
        color: white;
        font-family: Arial, sans-serif;
        z-index: 100;
        min-width: 200px;
    `;
    
    panel.innerHTML = `
        <h3 style="margin: 0 0 10px 0; color: #ff8811;">⚙️ Contrôles</h3>
        
        <button id="playPauseBtn" style="width: 100%; padding: 8px; margin-bottom: 10px; background: #ff8811; border: none; border-radius: 5px; color: white; cursor: pointer; font-weight: bold;">
            ⏸️ Pause
        </button>
        
        <label style="display: block; margin-bottom: 5px;">Vitesse: <span id="speedValue">1x</span></label>
        <input type="range" id="speedSlider" min="0.1" max="5" step="0.1" value="1" style="width: 100%; margin-bottom: 10px;">
        
        <button id="resetBtn" style="width: 100%; padding: 8px; margin-bottom: 10px; background: #4b70dd; border: none; border-radius: 5px; color: white; cursor: pointer;">
            🔄 Réinitialiser
        </button>
        
        <label style="display: flex; align-items: center; margin-bottom: 5px;">
            <input type="checkbox" id="autoRotateCheck" style="margin-right: 8px;">
            Rotation auto
        </label>
        
        <label style="display: flex; align-items: center;">
            <input type="checkbox" id="labelsCheck" style="margin-right: 8px;">
            Afficher noms
        </label>
    `;
    
    document.getElementById('solar-system-container').appendChild(panel);
    
    // Event listeners
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
        document.getElementById('speedSlider').value = 1;
        document.getElementById('speedValue').textContent = '1x';
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

function setupInteractivity() {
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();
    let hoveredPlanet = null;

    renderer.domElement.addEventListener('mousemove', (event) => {
        const rect = renderer.domElement.getBoundingClientRect();
        mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

        raycaster.setFromCamera(mouse, camera);
        const intersects = raycaster.intersectObjects(planets.filter(p => p.userData.name));

        if (intersects.length > 0) {
            const planet = intersects[0].object;
            if (hoveredPlanet !== planet) {
                if (hoveredPlanet && hoveredPlanet.userData.label) {
                    hoveredPlanet.userData.label.visible = false;
                }
                hoveredPlanet = planet;
                if (planet.userData.label) {
                    planet.userData.label.visible = true;
                }
                renderer.domElement.style.cursor = 'pointer';
            }
        } else {
            if (hoveredPlanet && hoveredPlanet.userData.label) {
                const labelsVisible = document.getElementById('labelsCheck').checked;
                if (!labelsVisible) {
                    hoveredPlanet.userData.label.visible = false;
                }
            }
            hoveredPlanet = null;
            renderer.domElement.style.cursor = 'default';
        }
    });

    renderer.domElement.addEventListener('click', (event) => {
        const rect = renderer.domElement.getBoundingClientRect();
        mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

        raycaster.setFromCamera(mouse, camera);
        const intersects = raycaster.intersectObjects(planets.filter(p => p.userData.name));

        if (intersects.length > 0) {
            const planet = intersects[0].object;
            showModal(planet.userData);
        }
    });
}

function animate() {
    requestAnimationFrame(animate);

    if (!isPaused) {
        const time = Date.now() * 0.001 * animationSpeed;
        
        planets.forEach((planet) => {
            // Rotation sur elle-même
            if (planet.userData.rotationSpeed) {
                planet.rotation.y += planet.userData.rotationSpeed * animationSpeed;
            }
            
            // Orbite autour du Soleil
            if (planet.userData.orbitSpeed) {
                const angle = time * planet.userData.orbitSpeed;
                planet.position.x = planet.userData.distance * Math.cos(angle);
                planet.position.z = planet.userData.distance * Math.sin(angle);
            }
            
            // Ceinture d'astéroïdes
            if (planet.userData.orbitRadius) {
                planet.userData.orbitAngle += planet.userData.orbitSpeed * animationSpeed;
                planet.position.x = planet.userData.orbitRadius * Math.cos(planet.userData.orbitAngle);
                planet.position.z = planet.userData.orbitRadius * Math.sin(planet.userData.orbitAngle);
            }
        });
        
        // Animation du Soleil (pulsation légère)
        if (sun) {
            const pulse = 1 + Math.sin(time * 2) * 0.02;
            sun.scale.set(pulse, pulse, pulse);
        }
    }

    controls.update();
    renderer.render(scene, camera);
}

function showModal(data) {
    const modal = document.getElementById('planet-modal');
    document.getElementById('modal-title').textContent = data.name;
    document.getElementById('modal-info').textContent = data.info;
    modal.style.display = 'block';
    modal.style.background = 'rgba(13, 17, 23, 0.95)';
    modal.style.backdropFilter = 'blur(10px)';
}

function closeModal() {
    document.getElementById('planet-modal').style.display = 'none';
}

function onWindowResize() {
    const container = document.getElementById('solar-system-container');
    const width = container.clientWidth;
    const height = container.clientHeight || 700;
    
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    renderer.setSize(width, height);
}

// Initialisation au chargement
document.addEventListener("DOMContentLoaded", init);