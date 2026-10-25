# Slide 16:9 – 16 · bubble motion

Figma: HR – System Dashboard, frame "Slide 16:9 - 16" (node 629:8586). Only the three glass bubbles move;
every other pixel is the Figma export.

- `exports/grow-gently-bubbles-2800x1985.gif` – Behance width at 2x (Retina), 10 s seamless loop, 30 fps
- `exports/grow-gently-bubbles-1400x992.gif` – Behance width at 1x
- `exports/grow-gently-bubbles-2800x1986.mp4` – the same loop as H.264 (one row of page colour added for an even height)

How it was made (`src/`): the slide, its photo card, the GROW GENTLY text and the "Why Foxlytics" card were
exported from Figma at 2x/4x; `rebuild.py` reassembles the photo card without the bubbles, `layers.py` lifts
each bubble out exactly as Figma rendered it (glass, highlights, shadow) and keeps the headline in front of
the first bubble, `animate2.py` sends the two large bubbles out to the photo card's corners and edges (squashing on each
hit) and back home, re-rendering each as glass every frame (`glass.py`: the background through a soft lens
plus the bubble's own highlights, rim and shadow); the small card bubble keeps a gentle bob. (`animate.py`
is the earlier, gentler figure-eight version.)

## v3 — five bubbles, always moving

- `exports/grow-gently-5-bubbles-1400x992.gif` — 1400 px Behance width, 50 fps, seamless 16 s loop (25 MB)
- `exports/grow-gently-5-bubbles-2800x1986.mp4` — 2800 px master, 50 fps

All five glass bubbles (the three from Figma plus a new medium and a new small one) glide at constant
speed and bounce softly off the photo card's edges (`src/paths.py`), never stopping; every path makes a
whole number of round trips per loop, so frame 800 runs straight into frame 1. `src/animate3.py` renders
the frames; `src/stablegif.py` encodes the GIF with one palette and a fixed dither for everything that
does not move, so the static slide never shimmers.

The GIF is written by `src/gifenc/hqgif.py` (with the C helpers in `gq.c`, built with
`gcc -O3 -shared -fPIC gq.c -o libgq.so`): every frame has its own palette fitted only to the pixels
that change, the still slide is repainted once in 16 tiles with a palette each, and nothing that
does not move is ever re-dithered — so far more than 256 colours, no speckles and no shimmer.
Dithering is limited to the photo (`src/gifenc/dithermask.png`, passed as the encoder's 6th argument);
the headline, the cards, the chart and all text are quantized without dither, so they stay crisp.
