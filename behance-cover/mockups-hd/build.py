# Five Behance covers from high-resolution blank-screen photos (Unsplash). Each screen is found from the
# photo's own pixels: its outline is the paste mask (so notches, rounded corners and anything in front,
# like the leaf, stay as photographed), and straight lines fitted to its edges give the exact corners
# for the perspective warp. Each cover shows a different part of the Foxlytics dashboard.
import sys, numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage
HERE = '/tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/scratchpad/hires/'
DASH = Image.open('/tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/images/110.jpg').convert('RGB')
OUT_W, OUT_H = 1616, 1264

def region(a, seed, thr, maxsat):
    lum = a.mean(-1); sat = a.max(-1) - a.min(-1)
    lab, _ = ndimage.label((lum > thr) & (sat < maxsat))
    return ndimage.binary_fill_holes(lab == lab[seed[1], seed[0]])

def fit_sides(reg, rng):
    """lines fitted to the region's four edges; rng gives, per side, the stretches of the edge to use"""
    ys, xs = np.nonzero(reg); x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    lines = {}
    for side in ('top', 'bottom', 'left', 'right'):
        pts = []
        for lo, hi in rng.get(side, [(0.15, 0.85)]):
            if side in ('top', 'bottom'):
                for x in range(int(x0 + lo * (x1 - x0)), int(x0 + hi * (x1 - x0))):
                    col = np.nonzero(reg[:, x])[0]
                    if len(col): pts.append((x, col.min() if side == 'top' else col.max() + 1))
            else:
                for y in range(int(y0 + lo * (y1 - y0)), int(y0 + hi * (y1 - y0))):
                    row = np.nonzero(reg[y])[0]
                    if len(row): pts.append((row.min() if side == 'left' else row.max() + 1, y))
        p = np.array(pts, float)
        lines[side] = np.polyfit(p[:, 0], p[:, 1], 1) if side in ('top', 'bottom') else np.polyfit(p[:, 1], p[:, 0], 1)
    return lines

def corner(h, v):   # h: y = a x + b ; v: x = c y + d
    a, b = h; c, d = v; y = (a * d + b) / (1 - a * c); return (c * y + d, y)

def quad_from(lines):
    return [corner(lines['top'], lines['left']), corner(lines['top'], lines['right']),
            corner(lines['bottom'], lines['right']), corner(lines['bottom'], lines['left'])]

def coeffs(dst, pts):
    A, B = [], []
    for (x, y), (u, v) in zip(dst, pts):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]; B += [u, v]
    return np.linalg.solve(np.array(A, float), np.array(B, float))

def view(quad, centre=None, width=None, top=None):
    """a crop of the dashboard in the screen's proportions: a band from `top`, or a close-up around `centre`"""
    tl, tr, br, bl = quad
    sw = (np.hypot(tr[0] - tl[0], tr[1] - tl[1]) + np.hypot(br[0] - bl[0], br[1] - bl[1])) / 2
    sh = (np.hypot(bl[0] - tl[0], bl[1] - tl[1]) + np.hypot(br[0] - tr[0], br[1] - tr[1])) / 2
    if centre is None:
        cw = DASH.width; ch = min(round(cw * sh / sw), DASH.height); t = min(top, DASH.height - ch)
        return DASH.crop((0, t, cw, t + ch))
    cw = width; ch = round(cw * sh / sw)
    x = int(np.clip(centre[0] - cw / 2, 0, DASH.width - cw)); y = int(np.clip(centre[1] - ch / 2, 0, DASH.height - ch))
    return DASH.crop((x, y, x + cw, y + ch))

def paste(img, reg, quad, src, SS=2):
    W, H = img.size
    big = src.resize((src.width * SS, src.height * SS), Image.LANCZOS) if src.width < 2400 else src
    c = coeffs(quad, [(0, 0), (big.width, 0), (big.width, big.height), (0, big.height)])
    warped = big.transform((W, H), Image.PERSPECTIVE, tuple(c), Image.BICUBIC)
    # never paint where the warp has no dashboard (just outside the fitted corners): keep the photo there
    inside = Image.new('L', (W, H), 0); from PIL import ImageDraw; ImageDraw.Draw(inside).polygon([tuple(p) for p in quad], fill=255)
    inside = ndimage.binary_erosion(np.asarray(inside) > 0, iterations=1)
    m = ndimage.gaussian_filter((reg & inside).astype(np.float32), 0.7)[..., None]
    a = np.asarray(img).astype(np.float32) * (1 - m) + np.asarray(warped).astype(np.float32) * m
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))

def cover(img, cx, cy, scale=1.0):
    """Behance cover crop (808:632) around (cx, cy); `scale` < 1 zooms in"""
    W, H = img.size; h = min(H, W * 632 / 808) * scale; w = h * 808 / 632
    x = np.clip(cx - w / 2, 0, W - w); y = np.clip(cy - h / 2, 0, H - h)
    return img.crop((int(x), int(y), int(x + w), int(y + h))).resize((OUT_W, OUT_H), Image.LANCZOS)

def build(name):
    img = Image.open(HERE + name + '.jpg').convert('RGB'); a = np.asarray(img).astype(np.int16)
    if name == 'hedge':          # laptop against greenery: the top of the dashboard (navigation, title, charts)
        reg = region(a, (1800, 900), 150, 40); q = quad_from(fit_sides(reg, {}))
        img = paste(img, reg, q, view(q, top=0)); return cover(img, 1800, 960)
    if name == 'angled':         # angled display on beige: both charts
        reg = region(a, (1762, 750), 238, 8); q = quad_from(fit_sides(reg, {}))
        img = paste(img, reg, q, view(q, top=560)); return cover(img, 1780, 1010)
    if name == 'dark':           # laptop and phone on a dark table: radar chart close-up; phone: bubble chart
        reg = region(a, (825, 1125), 150, 40)
        L = fit_sides(reg, {'top': [(0.55, 0.85)], 'right': [(0.15, 0.85)], 'bottom': [(0.3, 0.85)], 'left': [(0.2, 0.8)]})
        tr, br = corner(L['top'], L['right']), corner(L['bottom'], L['right'])
        # the screen runs off the photo on the left: its camera notch marks the middle of the top edge
        top_edge = np.array([np.nonzero(reg[:, x])[0].min() if reg[:, x].any() else 0 for x in range(0, 1660)])
        dip = np.nonzero(top_edge[300:1650] > np.polyval(L['top'], np.arange(300, 1650)) + 25)[0] + 300
        m = (dip.min() + dip.max()) / 2
        # top and bottom edges meet at the vanishing point v; the notch m is the screen's true middle, so the
        # hidden left end of the top edge is the harmonic conjugate:  (a-m)/(b-m) = -(a-v)/(b-v)
        v = (L['bottom'][1] - L['top'][1]) / (L['top'][0] - L['bottom'][0]); b = tr[0]
        tl_x = (v * (b - m) + m * (b - v)) / (2 * b - m - v)
        tl = (tl_x, np.polyval(L['top'], tl_x)); bl = (tl_x, np.polyval(L['bottom'], tl_x))   # left edge upright, like the right
        print('dark screen: notch', m, 'vanishing x', round(v), 'hidden left edge x', round(tl_x))
        q = [tl, tr, br, bl]
        img = paste(img, reg, q, view(q, centre=(675, 1290), width=900))
        preg = region(np.asarray(img).astype(np.int16), (2962, 1500), 150, 40)
        pq = quad_from(fit_sides(preg, {s: [(0.25, 0.75)] for s in ('top', 'bottom', 'left', 'right')}))
        img = paste(img, preg, pq, view(pq, centre=(1500, 1240), width=430)); return cover(img, 1650, 1350)
    if name == 'ipad':           # iPad with a trailing plant: bubble chart close-up (the leaf stays in front)
        reg = region(a, (1687, 1200), 170, 40)
        q = quad_from(fit_sides(reg, {'top': [(0.1, 0.6)], 'right': [(0.45, 0.85)], 'bottom': [(0.15, 0.8)], 'left': [(0.15, 0.85)]}))
        img = paste(img, reg, q, view(q, centre=(1500, 1335), width=860)); return cover(img, 1800, 1200)
    if name == 'studio':         # laptop glowing in a dark studio: the title and both chart headers
        reg = region(a, (1800, 1087), 170, 40)
        q = quad_from(fit_sides(reg, {'top': [(0.1, 0.35), (0.65, 0.9)]}))
        img = paste(img, reg, q, view(q, top=300)); return cover(img, 1800, 1150, 0.92)

for n in (sys.argv[1:] or ['hedge', 'angled', 'dark', 'ipad', 'studio']):
    o = build(n); o.save(HERE + f'foxlytics-{n}.png'); o.resize((808, 632), Image.LANCZOS).save(HERE + f'foxlytics-{n}-808.png'); print('done', n)
