// DNA Carousel: image cards arranged on two intertwined strands of a helix
// that spins continuously and can be dragged.

// Free images from Unsplash (https://unsplash.com/license); photographer in each comment.
const IMAGES = [
  { id: "1637929476734-bd7f5f78e40a", alt: "White and blue DNA double helix on a dark background" }, // Warren Umoh
  { id: "1643780668909-580822430155", alt: "Close-up of a blue and purple molecular structure" }, // Sangharsh Lohakare
  { id: "1631556097152-c39479bbff93", alt: "Fluorescent blue cells under a microscope" }, // National Cancer Institute
  { id: "1770320742520-99d616bba277", alt: "Glowing green test tube with bubbles" }, // Logan Voss
  { id: "1641903202531-bfa6bf0c6419", alt: "Glowing white DNA double helix" }, // Sangharsh Lohakare
  { id: "1594814532732-37c265b0dd3c", alt: "Bioluminescent blue waves on a rocky shore" }, // Trevor McKinnon
  { id: "1732046801426-f32529468176", alt: "DNA helix made of red and white particles" }, // MJH SHIKDER
  { id: "1576086476234-1103be98f096", alt: "Stress fibers and microtubules in cells" }, // National Cancer Institute
  { id: "1770320742705-a1aa0bd9364d", alt: "Glowing pink test tube with bubbles" }, // Logan Voss
  { id: "1628595351029-c2bf17511435", alt: "DNA double helix render on blue" }, // Braňo
  { id: "1562156194-215edc144205", alt: "Phytoplankton under a microscope" }, // NOAA
  { id: "1557264322-b44d383a2906", alt: "Green and pink abstract fluid art" }, // Pawel Czerwinski
  { id: "1770320742270-0cacc28b56b9", alt: "Glowing golden test tube with bubbles" }, // Logan Voss
  { id: "1681911046064-e663d5192921", alt: "Textured DNA strand on a soft blue background" }, // digitale.de
].map((img, i) => ({
  src: `images/dna-${i + 1}.jpg`, // saved from images.unsplash.com/photo-<id>
  alt: img.alt,
}));

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
    const { src, alt } = IMAGES[(i * 2 + strand) % IMAGES.length];
    img.src = src;
    img.alt = alt;
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
