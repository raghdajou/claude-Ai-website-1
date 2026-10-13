// DNA Carousel: image cards arranged on two intertwined strands of a helix
// that spins continuously and can be dragged.

// Generated in Higgsfield (Nano Banana). Cards cycle through this list.
const IMAGES = [
  "https://d8j0ntlcm91z4.cloudfront.net/user_3Kdq4ccmeO9l2lYL3HY1EWht7Bo/hf_20261013_170938_62a2cf62-2004-4ae4-b03a-7802bc5eab77.png",
  "https://d8j0ntlcm91z4.cloudfront.net/user_3Kdq4ccmeO9l2lYL3HY1EWht7Bo/hf_20261013_170123_38f4d25c-77b1-410a-b56b-804ee65f9c7a.png",
];

const CONFIG = {
  pairs: 14,          // rungs on the helix (each rung = 2 cards)
  radius: 200,        // helix radius in px
  spacing: 70,        // vertical distance between rungs in px
  twist: 0.45,        // radians of twist per rung
  speed: 0.25,        // auto-rotation in radians per second
  tilt: -18,          // whole-helix tilt in degrees
  dragFactor: 0.006,  // radians per dragged px
};

const root = document.getElementById("dna");
const stage = root.parentElement;
const cards = [];

for (let i = 0; i < CONFIG.pairs; i++) {
  for (let strand = 0; strand < 2; strand++) {
    const el = document.createElement("div");
    el.className = "dna-card";
    const img = document.createElement("img");
    img.src = IMAGES[(i * 2 + strand) % IMAGES.length];
    img.alt = "";
    img.draggable = false;
    el.appendChild(img);
    root.appendChild(el);
    cards.push({ el, rung: i, phase: strand * Math.PI });
  }
}

let rotation = 0;
let velocity = CONFIG.speed;
let dragging = false;
let lastX = 0;
let last = performance.now();

function radius() {
  return Math.min(CONFIG.radius, window.innerWidth * 0.32);
}

function render(now) {
  const dt = Math.min((now - last) / 1000, 0.05);
  last = now;

  if (!dragging) {
    // Ease back toward the resting auto-rotation speed after a fling.
    velocity += (CONFIG.speed - velocity) * Math.min(dt * 2, 1);
    rotation += velocity * dt;
  }

  const r = radius();
  const mid = (CONFIG.pairs - 1) / 2;

  for (const c of cards) {
    const angle = c.rung * CONFIG.twist + c.phase + rotation;
    const x = Math.sin(angle) * r;
    const z = Math.cos(angle) * r;
    const y = (c.rung - mid) * CONFIG.spacing;
    const depth = (z + r) / (2 * r); // 0 = back, 1 = front
    const facing = (angle * 180) / Math.PI;

    c.el.style.transform =
      `rotateZ(${CONFIG.tilt}deg) translate3d(${x}px, ${y}px, ${z}px) rotateY(${facing}deg)`;
    c.el.style.opacity = (0.35 + depth * 0.65).toFixed(3);
    c.el.style.filter = `blur(${((1 - depth) * 2).toFixed(2)}px) brightness(${(0.55 + depth * 0.45).toFixed(3)})`;
    c.el.style.zIndex = Math.round(depth * 1000);
  }

  requestAnimationFrame(render);
}

stage.addEventListener("pointerdown", (e) => {
  dragging = true;
  lastX = e.clientX;
  velocity = 0;
  stage.setPointerCapture(e.pointerId);
});

stage.addEventListener("pointermove", (e) => {
  if (!dragging) return;
  const dx = e.clientX - lastX;
  lastX = e.clientX;
  rotation += dx * CONFIG.dragFactor;
  velocity = dx * CONFIG.dragFactor * 60;
});

const endDrag = () => { dragging = false; };
stage.addEventListener("pointerup", endDrag);
stage.addEventListener("pointercancel", endDrag);

if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
  CONFIG.speed = 0;
  velocity = 0;
}

requestAnimationFrame(render);
