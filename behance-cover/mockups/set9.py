# Laptop on a tan leather sofa: the website's two rounded cards (cream panel + photo) fill almost the
# whole display on a black page; the Foxlytics screen replaces them as one rounded card on the same
# edges (fitted lines), keeping the black margin around it.
import itertools, math, numpy as np
from PIL import Image, ImageDraw
I = '/tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/images/'
SS = 3
def meet(a, b):   # a: x = a0*y + a1, b: y = b0*x + b1
    y = (b[0] * a[1] + b[1]) / (1 - b[0] * a[0]); return (a[0] * y + a[1], y)
L, R, T, B = (-0.04682, 419.229), (-0.0465, 1408.1), (0.04572, 86.05), (0.07683, 694.44)
q = [meet(L, T), meet(R, T), meet(R, B), meet(L, B)]; print([tuple(round(v, 1) for v in p) for p in q])
SCREENS = {'brand': ('141.jpg', None), 'payroll': ('130.jpg', 405), 'projects': ('131.jpg', 560)}
def coeffs(dst, pts):
    A, Bv = [], []
    for (x, y), (u, v) in zip(dst, pts):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]; Bv += [u, v]
    return np.linalg.solve(np.array(A, float), np.array(Bv, float))
scene = Image.open(I + '160.webp').convert('RGB'); W, H = scene.size
r = 1.58
for scr, (df, top) in SCREENS.items():
    d = Image.open(I + df).convert('RGB')
    if top is None:
        cw = round(d.height * r); x0 = int(np.clip(900 - cw / 2, 0, d.width - cw)); box = (x0, 0, x0 + cw, d.height)
    else:
        bh = round(d.width / r); t = min(top, d.height - bh); box = (0, t, d.width, t + bh)
    src = d.crop(box).resize((round(2400 * r), 2400), Image.LANCZOS)
    qs = [(x * SS, y * SS) for x, y in q]
    c = coeffs(qs, [(0, 0), (src.width, 0), (src.width, src.height), (0, src.height)])
    warped = src.transform((W * SS, H * SS), Image.PERSPECTIVE, tuple(c), Image.BICUBIC).resize((W, H), Image.LANCZOS)
    sm = Image.new('L', src.size, 0); ImageDraw.Draw(sm).rounded_rectangle((0, 0, src.width - 1, src.height - 1), 45, fill=255)
    m = sm.transform((W * SS, H * SS), Image.PERSPECTIVE, tuple(c), Image.BICUBIC, fillcolor=0).resize((W, H), Image.LANCZOS)
    m = (np.asarray(m).astype(np.float32) / 255)[..., None]
    out = np.asarray(scene).astype(np.float32) * (1 - m) + np.asarray(warped).astype(np.float32) * m
    o = Image.fromarray(out.clip(0, 255).astype(np.uint8))
    cw = round(H * 808 / 632); x0 = (W - cw) // 2
    o = o.crop((x0, 0, x0 + cw, H)).resize((1616, 1264), Image.LANCZOS)
    o.save(f's9-leather-{scr}.png'); o.resize((808, 632), Image.LANCZOS).save(f's9-leather-{scr}-808.png'); print('done', scr)
