# Laptop face-on in front of a dark chesterfield: only the screen changes; the camera notch and the
# round top corners are drawn in screen space (same notch size as the other MacBook mockups).
import itertools, math, numpy as np
from PIL import Image, ImageDraw
I = '/tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/images/'
SS = 3
def meet(a, b):   # a: x = a0*y + a1, b: y = b0*x + b1
    y = (b[0] * a[1] + b[1]) / (1 - b[0] * a[0]); return (a[0] * y + a[1], y)
q = [(473.6, 363.2), (1125.6, 363.2), (1124.0, 782.2), (473.6, 782.2)]
SCREENS = {'brand': ('141.jpg', None), 'payroll': ('130.jpg', 390), 'projects': ('131.jpg', 560)}
def coeffs(dst, pts):
    A, Bv = [], []
    for (x, y), (u, v) in zip(dst, pts):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]; Bv += [u, v]
    return np.linalg.solve(np.array(A, float), np.array(Bv, float))
scene = Image.open(I + '161.webp').convert('RGB'); W, H = scene.size
r = (652 / 419)
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
    sm = Image.new('L', src.size, 0); dd = ImageDraw.Draw(sm)
    dd.rounded_rectangle((0, 0, src.width - 1, src.height - 1), 55, fill=255); dd.rectangle((0, src.height // 2, src.width, src.height), fill=255)
    nw = 392 / 3713 * src.width; cx = src.width / 2 - 1.5 / 652 * src.width
    dd.rounded_rectangle((cx - nw / 2, -60, cx + nw / 2, 66), 22, fill=0)
    m = sm.transform((W * SS, H * SS), Image.PERSPECTIVE, tuple(c), Image.BICUBIC, fillcolor=0).resize((W, H), Image.LANCZOS)
    m = (np.asarray(m).astype(np.float32) / 255)[..., None]
    out = np.asarray(scene).astype(np.float32) * (1 - m) + np.asarray(warped).astype(np.float32) * m
    o = Image.fromarray(out.clip(0, 255).astype(np.uint8))
    cw = round(H * 808 / 632); x0 = (W - cw) // 2
    o = o.crop((x0, 0, x0 + cw, H)).resize((1616, 1264), Image.LANCZOS)
    o.save(f's10-chester-{scr}.png'); o.resize((808, 632), Image.LANCZOS).save(f's10-chester-{scr}-808.png'); print('done', scr)
