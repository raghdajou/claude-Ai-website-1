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
