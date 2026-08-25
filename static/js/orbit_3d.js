/**
 * COSMOS 3D Keplerian Orbit Visualizer (Three.js)
 */

function init3DOrbitViewer(containerId, semiMajorAxis = 1.0, eccentricity = 0.05, inclination = 89.5) {
    const container = document.getElementById(containerId);
    if (!container || typeof THREE === 'undefined') return;

    container.innerHTML = '';

    const width = container.clientWidth || 600;
    const height = container.clientHeight || 400;

    // Scene, Camera, Renderer
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });

    renderer.setSize(width, height);
    renderer.setPixelRatio(window.devicePixelRatio);
    container.appendChild(renderer.domElement);

    // Host Star (Yellow Sphere + PointLight)
    const starGeo = new THREE.SphereGeometry(1.2, 32, 32);
    const starMat = new THREE.MeshBasicMaterial({ color: 0xffcc00 });
    const starMesh = new THREE.Mesh(starGeo, starMat);
    scene.add(starMesh);

    const light = new THREE.PointLight(0xffffff, 2, 100);
    scene.add(light);

    // Star Glow Ambient
    const ambLight = new THREE.AmbientLight(0x404040);
    scene.add(ambLight);

    // Orbit Curve Geometry
    const points = [];
    const segments = 128;
    const b = semiMajorAxis * Math.sqrt(1 - eccentricity * eccentricity);
    const c = semiMajorAxis * eccentricity; // Focal distance offset

    for (let i = 0; i <= segments; i++) {
        const theta = (i / segments) * Math.PI * 2;
        const x = semiMajorAxis * Math.cos(theta) - c;
        const z = b * Math.sin(theta);
        points.push(new THREE.Vector3(x * 5, 0, z * 5));
    }

    const orbitGeo = new THREE.BufferGeometry().setFromPoints(points);
    const orbitMat = new THREE.LineBasicMaterial({ color: 0x00ffb3, opacity: 0.7, transparent: true });
    const orbitLine = new THREE.Line(orbitGeo, orbitMat);

    // Apply Inclination tilt
    orbitLine.rotation.x = (inclination - 90) * (Math.PI / 180);
    scene.add(orbitLine);

    // Planet Sphere
    const planetGeo = new THREE.SphereGeometry(0.5, 24, 24);
    const planetMat = new THREE.MeshStandardMaterial({ color: 0x00bfe7, roughness: 0.4 });
    const planetMesh = new THREE.Mesh(planetGeo, planetMat);
    scene.add(planetMesh);

    // Camera Position
    camera.position.set(0, 12, 22);
    camera.lookAt(0, 0, 0);

    let angle = 0;
    function animate() {
        requestAnimationFrame(animate);
        angle += 0.015;

        const x = (semiMajorAxis * Math.cos(angle) - c) * 5;
        const z = (b * Math.sin(angle)) * 5;

        // Rotate planet along inclined orbit plane
        const vec = new THREE.Vector3(x, 0, z);
        vec.applyAxisAngle(new THREE.Vector3(1, 0, 0), (inclination - 90) * (Math.PI / 180));

        planetMesh.position.copy(vec);
        starMesh.rotation.y += 0.005;

        renderer.render(scene, camera);
    }

    animate();
}
