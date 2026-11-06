# Three more monitors: front monitor on grey ("augment"), front monitor on a soft yellow-white blur
# ("vsl"), angled monitor over a hedge ("intelli"). Only the screen changes; in "intelli" the big faded
# "Intelli™" word behind the monitor is rewritten as "Foxlytics" in the same fade.
import itertools, math, numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage
I = '/tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/images/'
SS = 3
def meet(a, b):   # a: x = a0*y + a1, b: y = b0*x + b1
    y = (b[0] * a[1] + b[1]) / (1 - b[0] * a[0]); return (a[0] * y + a[1], y)
aL, aR = (-0.00711, 126.149), (0.00713, 1473.301)
iL, iR, iT, iB = (0.00731, 294.954), (0.06653, 1130.374), (0.08533, 189.256), (0.04375, 750.25)
SCENES = {
    'augment': ('153.webp', [meet(aL, (0, 124.2)), meet(aR, (0, 124.2)), meet(aR, (0, 884.68)), meet(aL, (0, 884.68))], None),
    'vsl':     ('154.webp', [(176.41, 141.32), (1822.6, 141.32), (1822.6, 1157.55), (176.41, 1157.55)], None),
    'intelli': ('155.webp', [meet(iL, iT), meet(iR, iT), meet(iR, iB), meet(iL, iB)], 16 / 9),
}
SCREENS = {'brand': ('141.jpg', None), 'payroll': ('130.jpg', 420), 'projects': ('131.jpg', 560)}
def coeffs(dst, pts):
    A, B = [], []
    for (x, y), (u, v) in zip(dst, pts):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]; B += [u, v]
    return np.linalg.solve(np.array(A, float), np.array(B, float))

def rewordmark(img):
    """Replace the faded 'Intelli™' behind the angled monitor with 'Foxlytics' in the same white fade."""
    a = np.asarray(img).astype(np.float32); H, W = a.shape[:2]; g = a.mean(-1)
    # monitor silhouette (outer frame) = bezel outer edges pushed out by the silver rim
    mon = Image.new('L', (W * SS, H * SS), 0)
    T, L, R = (0.08424, 174.301), (0.00093, 278.249), (0.06722, 1147.529)
    tl = meet((L[0], L[1] - 11), (T[0], T[1] - 9)); tr = meet((R[0], R[1] + 4), (T[0], T[1] - 9))
    poly = [tl, tr, (R[0] * H + R[1] + 4, H), (L[0] * H + L[1] - 11, H)]
    ImageDraw.Draw(mon).polygon([(x * SS, y * SS) for x, y in poly], fill=255)
    # round the two top corners of the frame
    cm = Image.new('L', mon.size, 0); d = ImageDraw.Draw(cm); rr = 14 * SS
    for (cx, cy), sx in ((tl, 1), (tr, -1)):
        d.rectangle((cx * SS - (rr if sx < 0 else 0), cy * SS, cx * SS + (rr if sx > 0 else 0), cy * SS + rr), fill=255)
        d.ellipse((cx * SS + (0 if sx > 0 else -2 * rr), cy * SS, cx * SS + (2 * rr if sx > 0 else 0), cy * SS + 2 * rr), fill=0)
    mon = np.maximum(np.asarray(mon).astype(np.float32) - np.asarray(cm).astype(np.float32), 0)
    mon = Image.fromarray(mon.astype(np.uint8)).resize((W, H), Image.LANCZOS)
    mon = np.asarray(mon).astype(np.float32) / 255
    band = np.zeros((H, W), bool); band[:460] = True
    # backdrop without the old word: smooth fill from the pixels the word does not touch
    bg = ndimage.gaussian_filter(a, (90, 90, 0)); text = np.zeros((H, W), bool)
    for _ in range(3):
        text = band & (mon < 0.5) & (g > bg.mean(-1) + 5)
        text = ndimage.binary_dilation(text, iterations=8)
        w = ((~text) & (mon < 0.5)).astype(np.float32)
        bg = ndimage.gaussian_filter(a * w[..., None], (45, 45, 0)) / np.maximum(ndimage.gaussian_filter(w, 45), 1e-3)[..., None]
    clean = np.where(band[..., None], bg, a)
    # new word, same fade: opaque-ish white at the top, gone by y≈420 (measured on the old 'I')
    font = ImageFont.truetype('/usr/share/fonts/truetype/inter/Inter-Bold.ttf' if False else 'Inter-Bold', 10)
    return clean, mon, band, text

for (name, (f, q, asp)), (scr, (df, top)) in itertools.product(SCENES.items(), SCREENS.items()):
    scene = Image.open(I + f).convert('RGB'); W, H = scene.size; dash = Image.open(I + df).convert('RGB')
    tl, tr, br, bl = q
    sw = (math.dist(tl, tr) + math.dist(bl, br)) / 2; sh = (math.dist(tl, bl) + math.dist(tr, br)) / 2
    r = asp or sw / sh
    if top is None:
        if dash.width / dash.height > r:
            cw = round(dash.height * r); x0 = int(np.clip(900 - cw / 2, 0, dash.width - cw)); box = (x0, 0, x0 + cw, dash.height)
        else:
            ch = round(dash.width / r); y0 = int(np.clip(640 - ch / 2, 0, dash.height - ch)); box = (0, y0, dash.width, y0 + ch)
    else:
        bh = round(dash.width / r); t = min(top, dash.height - bh); box = (0, t, dash.width, t + bh)
    src = dash.crop(box).resize((round(2400 * r), 2400), Image.LANCZOS)
    qs = [(x * SS, y * SS) for x, y in q]
    c = coeffs(qs, [(0, 0), (src.width, 0), (src.width, src.height), (0, src.height)])
    warped = src.transform((W * SS, H * SS), Image.PERSPECTIVE, tuple(c), Image.BICUBIC).resize((W, H), Image.LANCZOS)
    m = Image.new('L', (W * SS, H * SS), 0); ImageDraw.Draw(m).polygon(qs, fill=255)
    m = np.asarray(m.resize((W, H), Image.LANCZOS)).astype(np.float32)[..., None] / 255
    out = np.asarray(scene).astype(np.float32) * (1 - m) + np.asarray(warped).astype(np.float32) * m
    o = Image.fromarray(out.clip(0, 255).astype(np.uint8))
    o.save(f's7raw-{name}-{scr}.png')
    print('done', name, scr, [tuple(round(v, 1) for v in p) for p in q] if scr == 'brand' else '')
