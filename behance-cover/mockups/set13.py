# Angled monitor over a dark ribbed form ("lio"): only the screen changes (edges line-fitted, <0.2 px).
# Cover 1616x1264, Behance artboard 1400x788 (+2x), Upwork 4:3 1000x750 (+2x, JPEG).
import math, numpy as np
from PIL import Image, ImageDraw
I = '/tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/images/'
Q = [(309.89, 405.59), (1688.48, 209.37), (1684.99, 986.53), (256.28, 1150.69)]
SCREENS = {'analytics': ('165.jpg', 870), 'projects': ('131.jpg', 620), 'payroll': ('130.jpg', 420), 'brand': ('141.jpg', None)}   # 16:9 bands that hold whole charts
R = 16 / 9
def coeffs(dst, pts):
    A, B = [], []
    for (x, y), (u, v) in zip(dst, pts):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]; B += [u, v]
    return np.linalg.solve(np.array(A, float), np.array(B, float))
base = Image.open(I + '166.webp').convert('RGB')
for scr, (df, top) in SCREENS.items():
    d = Image.open(I + df).convert('RGB')
    if top is None and d.width / d.height > R:
        cw = round(d.height * R); x0 = int(np.clip(900 - cw / 2, 0, d.width - cw)); box = (x0, 0, x0 + cw, d.height)
    elif top is None:
        ch = round(d.width / R); y0 = int(np.clip(640 - ch / 2, 0, d.height - ch)); box = (0, y0, d.width, y0 + ch)
    else:
        bh = round(d.width / R); t = min(top, d.height - bh); box = (0, t, d.width, t + bh)
    src = d.crop(box).resize((round(2400 * R), 2400), Image.LANCZOS)
    for K in (1, 2):
        SS = 3 if K == 1 else 2
        scene = base.resize((base.width * K, base.height * K), Image.LANCZOS) if K > 1 else base.copy(); W, H = scene.size
        qs = [(x * K * SS, y * K * SS) for x, y in Q]
        c = coeffs(qs, [(0, 0), (src.width, 0), (src.width, src.height), (0, src.height)])
        warped = src.transform((W * SS, H * SS), Image.PERSPECTIVE, tuple(c), Image.BICUBIC).resize((W, H), Image.LANCZOS)
        m = Image.new('L', (W * SS, H * SS), 0); ImageDraw.Draw(m).polygon(qs, fill=255); m = m.resize((W, H), Image.LANCZOS)
        out = Image.composite(warped, scene, m)
        if K == 1:
            cw = round(H * 808 / 632); x0 = (W - cw) // 2
            o = out.crop((x0, 0, x0 + cw, H)).resize((1616, 1264), Image.LANCZOS)
            o.save(f's13-lio-{scr}.png'); o.resize((808, 632), Image.LANCZOS).save(f's13-lio-{scr}-808.png')
            out.resize((1000, 750), Image.LANCZOS).save(f'uw-lio-{scr}-1000.jpg', quality=95, subsampling=0)
        else:
            out.resize((2000, 1500), Image.LANCZOS).save(f'uw-lio-{scr}-2000.jpg', quality=95, subsampling=0)
        y0 = 150 * K   # 16:9 window (2000 x 1125) around the monitor
        a = out.crop((0, y0, W, y0 + 1125 * K))
        a.resize((2800, 1576) if K == 2 else (1400, 788), Image.LANCZOS).save(f'ab-lio-{scr}-{2800 if K == 2 else 1400}.png')
    print('done', scr)
