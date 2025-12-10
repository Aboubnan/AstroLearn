// solar_system.js
let scene, camera, renderer, controls;
let planets = [];
let planetData = {
    sun: { name: "Soleil", distance: 0, diameter: 1.392e6, color: 0xffff00, texture: "https://i.imgur.com/2j8Q8wJ.jpg", info: "Étoile centrale du système solaire." },
    mercury: { name: "Mercure", distance: 8, diameter: 4879, color: 0x8c7853, texture: "https://i.imgur.com/4Q8Q8wJ.jpg", info: "La planète la plus proche du Soleil." },
    venus: { name: "Vénus", distance: 12, diameter: 12104, color: 0xffc649, texture: "https://i.imgur.com/6Q8Q8wJ.jpg", info: "Planète tellurique avec une atmosphère dense." },
    earth: { name: "Terre", distance: 16, diameter: 12756, color: 0x6b93d6, texture: "https://i.imgur.com/8Q8Q8wJ.jpg", info: "Notre planète, avec de l'eau et de la vie." },
    mars: { name: "Mars", distance: 20, diameter: 6792, color: 0xc1440e, texture: "https://i.imgur.com/aQ8Q8wJ.jpg", info: "La planète rouge, avec des calottes polaires." },
    jupiter: { name: "Jupiter", distance: 30, diameter: 142984, color: 0xd8ca9d, texture: "https://i.imgur.com/cQ8Q8wJ.jpg", info: "La plus grande planète, gazeuse." },
    saturn: { name: "Saturne", distance: 45, diameter: 120536, color: 0xfad5a5, texture: "https://i.imgur.com/eQ8Q8wJ.jpg", info: "Connue pour ses anneaux." },
    uranus: { name: "Uranus", distance: 60, diameter: 51118, color: 0x4fd0e7, texture: "https://i.imgur.com/gQ8Q8wJ.jpg", info: "Planète glacée, inclinée sur le côté." },
    neptune: { name: "Neptune", distance: 75, diameter: 49528, color: 0x4b70dd, texture: "https://i.imgur.com/iQ8Q8wJ.jpg", info: "La planète la plus éloignée." }
};

function init() {
    // Scène
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x000011);  // Fond bleu nuit

    // Caméra
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.set(0, 30, 80);  // Position plus éloignée pour voir tout

    // Rendu (responsive)
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth * 0.9, 600);  // Prend 90% de la largeur de la fenêtre, hauteur fixe
    document.getElementById('solar-system-container').appendChild(renderer.domElement);

    // Contrôles
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.minDistance = 20;
    controls.maxDistance = 300;

    // Lumière (plus intense pour mieux voir)
    const ambientLight = new THREE.AmbientLight(0x404040, 0.4);  // Plus lumineux
    scene.add(ambientLight);
    const directionalLight = new THREE.DirectionalLight(0xffffff, 1.5);  // Plus intense
    directionalLight.position.set(0, 0, 0).normalize();
    scene.add(directionalLight);

    // Ajouter des étoiles
    addStars();

    // Ajouter planètes
    addPlanets();

    // Gestion des clics
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

    window.addEventListener('click', function(event) {
        const rect = renderer.domElement.getBoundingClientRect();
        mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

        raycaster.setFromCamera(mouse, camera);
        const intersects = raycaster.intersectObjects(planets);

        if (intersects.length > 0) {
            const planet = intersects[0].object;
            showModal(planet.userData);
        }
    });

    // Redimensionnement responsive
    window.addEventListener('resize', onWindowResize, false);

    // Animation
    animate();
}

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth * 0.9, 600);
}

function addStars() {
    const starGeometry = new THREE.BufferGeometry();
    const starMaterial = new THREE.PointsMaterial({ color: 0xffffff, size: 1 });  // Étoiles plus grosses
    const starVertices = [];
    for (let i = 0; i < 1500; i++) {  // Plus d'étoiles
        starVertices.push((Math.random() - 0.5) * 2000);
        starVertices.push((Math.random() - 0.5) * 2000);
        starVertices.push((Math.random() - 0.5) * 2000);
    }
    starGeometry.setAttribute('position', new THREE.Float32BufferAttribute(starVertices, 3));
    const stars = new THREE.Points(starGeometry, starMaterial);
    scene.add(stars);
}

function addPlanets() {
    const textureLoader = new THREE.TextureLoader();

    Object.keys(planetData).forEach((key, index) => {
        const data = planetData[key];
        const radius = Math.log(data.diameter) * 0.15;  // Tailles augmentées pour mieux voir
        const geometry = new THREE.SphereGeometry(radius, 32, 32);
        const material = new THREE.MeshPhongMaterial({ color: data.color, shininess: 30 });  // Plus brillant

        if (data.texture) {
            textureLoader.load(data.texture, function(texture) {
                material.map = texture;
                material.needsUpdate = true;
            });
        }

        const planet = new THREE.Mesh(geometry, material);
        planet.position.x = data.distance;
        planet.userData = data;
        scene.add(planet);
        planets.push(planet);

        // Orbites plus visibles
        if (index > 0) {
            const orbitGeometry = new THREE.RingGeometry(data.distance - 0.2, data.distance + 0.2, 64);
            const orbitMaterial = new THREE.MeshBasicMaterial({ color: 0x666666, side: THREE.DoubleSide, transparent: true, opacity: 0.6 });  // Plus visible
            const orbit = new THREE.Mesh(orbitGeometry, orbitMaterial);
            orbit.rotation.x = Math.PI / 2;
            scene.add(orbit);
        }

        // Anneaux pour Saturne (plus visibles)
        if (key === 'saturn') {
            const ringGeometry = new THREE.RingGeometry(radius * 1.3, radius * 2.5, 32);
            const ringMaterial = new THREE.MeshBasicMaterial({ color: 0xaaaaaa, side: THREE.DoubleSide, transparent: true, opacity: 0.8 });
            const ring = new THREE.Mesh(ringGeometry, ringMaterial);
            ring.rotation.x = Math.PI / 2;
            planet.add(ring);
        }
    });
}

function animate() {
    requestAnimationFrame(animate);

    planets.forEach((planet, index) => {
        if (index > 0) {
            planet.position.x = planetData[Object.keys(planetData)[index]].distance * Math.cos(Date.now() * 0.0005 / (index + 1));
            planet.position.z = planetData[Object.keys(planetData)[index]].distance * Math.sin(Date.now() * 0.0005 / (index + 1));
            planet.rotation.y += 0.01;
        } else {
            planet.rotation.y += 0.005;
        }
    });

    controls.update();
    renderer.render(scene, camera);
}

function showModal(data) {
    document.getElementById('modal-title').textContent = data.name;
    document.getElementById('modal-info').textContent = `Distance au Soleil : ${data.distance} UA\nDiamètre : ${data.diameter} km\n${data.info}`;
    document.getElementById('planet-modal').style.display = 'block';
}

function closeModal() {
    document.getElementById('planet-modal').style.display = 'none';
}

document.addEventListener("DOMContentLoaded", init);
