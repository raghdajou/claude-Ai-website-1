# Glass model for a bubble: what you see inside = the background behind it seen through a lens
# (magnified about the centre and softened) plus a per-pixel veil of light/dark taken from the
# Figma render, so highlights and rim stay exactly as designed while the view through it changes.
import numpy as np
from PIL import Image
from scipy import ndimage
def lens_sample(bg, cx, cy, r, k, sigma):
    H, W = bg.shape[:2]; R = int(r) + 2
    yy, xx = np.mgrid[-R:R + 1, -R:R + 1].astype(np.float32)
    sx = cx + xx * k; sy = cy + yy * k
    out = np.stack([ndimage.map_coordinates(bg[..., c], [sy, sx], order=1, mode='nearest') for c in range(3)], -1)
    if sigma > 0: out = np.stack([ndimage.gaussian_filter(out[..., c], sigma) for c in range(3)], -1)
    return out, xx, yy
def fit(O, G, disc):
    lighter = (O.mean(-1) >= G.mean(-1))
    Wc = np.where(lighter[..., None], 255.0, 0.0)
    num = ((O - G) * (Wc - G)).sum(-1); den = ((Wc - G) ** 2).sum(-1) + 1e-3
    a = np.clip(num / den, 0, 1) * disc
    return a, Wc
def render(G, a, Wc):
    return G * (1 - a[..., None]) + Wc * a[..., None]
