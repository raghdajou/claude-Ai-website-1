# The flower-meadow laptop from the larger Behance capture: flowers recoloured, the laptop screen
# replaced by the Foxlytics dashboard, everything else as photographed. Behance cover 1616 x 1264.
import sys, colorsys, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
I = '/tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/images/'
# new hue (degrees) for each family of petal colour: (orange/peach, pink/magenta, purple, blue)
PALETTES = {
    'brand':  (72, 165, 182, 200),     # lime, teal, deep teal, sky: the dashboard's chart colours
    'white':  None,                    # white / cream petals
    'sunset': (38, 8, 350, 20),        # golden, red, rose, coral
}
img = Image.open(I + '118.webp').convert('RGB').crop((202, 214, 1800, 1203))
a = np.asarray(img).astype(np.float32) / 255
hsv = np.asarray(img.convert('HSV')).astype(np.float32)
H = hsv[..., 0] * 360 / 255; S = hsv[..., 1] / 255; V = hsv[..., 2] / 255
# petals: saturated, and not grass / stem green-yellow (hue 45..160)
petal = (S > 0.18) & (V > 0.25) & ~((H > 45) & (H < 160))
petal = ndimage.binary_opening(petal, iterations=1)
soft = ndimage.gaussian_filter(petal.astype(np.float32), 0.8)

# the screen: bright, low-saturation region (its outline is the paste mask, so the flower in front of
# the lower right stays in front); corners measured on the capture
lum = a.mean(-1) * 255; sat = (a.max(-1) - a.min(-1)) * 255
lab, _ = ndimage.label((lum > 150) & (sat < 40))
scr = ndimage.binary_fill_holes(lab == lab[650 - 214, 1000 - 202])
scr = ndimage.binary_dilation(scr, iterations=1)
Q = [(647, 327), (995, 376), (979, 564), (636.5, 535.5)]          # TL TR BR BL in the cropped capture
dash = Image.open(I + '110.jpg').convert('RGB')
def coeffs(dst, pts):
    A, B = [], []
    for (x, y), (u, v) in zip(dst, pts):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]; B += [u, v]
    return np.linalg.solve(np.array(A, float), np.array(B, float))
def recolour(name):
    pal = PALETTES[name]; out = a.copy()
    ys, xs = np.nonzero(soft > 0.01); h = H[ys, xs]; s = S[ys, xs]; v = V[ys, xs]
    if pal is None:     # white: drop saturation, lift value a little, keep a hint of warmth
        rgb = np.stack([v * 0.97 + 0.03, v * 0.96 + 0.03, v * 0.92 + 0.02], -1)
        mix = 0.65
    else:
        fam = np.select([(h < 45) | (h >= 345), (h >= 300), (h >= 255)], [0, 1, 2], 3)
        nh = np.array(pal, float)[fam] / 360
        rgb = np.array([colorsys.hsv_to_rgb(hh, min(ss * 1.05, 1), vv) for hh, ss, vv in zip(nh, s, v)])
        mix = 1.0
    w = soft[ys, xs][:, None] * mix
    out[ys, xs] = out[ys, xs] * (1 - w) + rgb * w
    o = Image.fromarray((out.clip(0, 1) * 255).astype(np.uint8))
    # Behance cover shape (808:632), full height, centred on the laptop; composite the screen at that size
    w = round(o.height * 808 / 632); x0 = int(np.clip(1010 - 202 - w / 2, 0, o.width - w))
    k = 1264 / o.height; SS = 3
    o = o.crop((x0, 0, x0 + w, o.height)).resize((1616, 1264), Image.LANCZOS)
    q = [((x - x0) * k, y * k) for x, y in Q]
    tl, tr, br, bl = q
    sw = (np.hypot(tr[0] - tl[0], tr[1] - tl[1]) + np.hypot(br[0] - bl[0], br[1] - bl[1])) / 2
    sh = (np.hypot(bl[0] - tl[0], bl[1] - tl[1]) + np.hypot(br[0] - tr[0], br[1] - tr[1])) / 2
    src = dash.crop((0, 560, dash.width, 560 + round(dash.width * sh / sw)))
    src = src.resize((int(sw * SS), int(sh * SS)), Image.LANCZOS)          # pre-shrink: no aliasing in the warp
    qs = [(x * SS, y * SS) for x, y in q]; outer = qs
    # extend the quad a hair outward so the mask's edge pixels are covered too
    cx, cy = np.mean([p[0] for p in qs]), np.mean([p[1] for p in qs]); ext = [(cx + (x - cx) * 1.012, cy + (y - cy) * 1.012) for x, y in qs]
    c = coeffs(ext, [(0, 0), (src.width, 0), (src.width, src.height), (0, src.height)])
    warped = src.transform((1616 * SS, 1264 * SS), Image.PERSPECTIVE, tuple(c), Image.BICUBIC).resize((1616, 1264), Image.LANCZOS)
    m = Image.fromarray((scr[:, x0:x0 + w] * 255).astype(np.uint8)).resize((1616, 1264), Image.LANCZOS)
    m = np.asarray(m).astype(np.float32)[..., None] / 255
    res = np.asarray(o).astype(np.float32) * (1 - m) + np.asarray(warped).astype(np.float32) * m
    return Image.fromarray(res.clip(0, 255).astype(np.uint8))

for n in (sys.argv[1:] or PALETTES):
    r = recolour(n); r.save(f'meadow-{n}.png'); r.resize((808, 632), Image.LANCZOS).save(f'meadow-{n}-808.png'); print('done', n)
