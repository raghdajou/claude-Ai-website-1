# Floating open laptop in a misty crystal landscape ("float"): only the screen changes. Edges were
# line-fitted (<1 px); the camera notch and rounded top corners are drawn in screen space and warped.
# Cover 1616x1264 (+808), Behance artboard 1400x788 (+2x), Upwork 4:3 1000x750 (+2x, JPEG).
import numpy as np
from PIL import Image, ImageDraw
I = '/tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/images/'
Q = [(621.9, 195.1), (976.6, 365.2), (880.4, 719.2), (514.4, 578.9)]
R = 1.547
SCREENS = {'analytics': ('173.jpg', 540)}
def coeffs(dst, pts):
    A, B = [], []
    for (x, y), (u, v) in zip(dst, pts):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]; B += [u, v]
    return np.linalg.solve(np.array(A, float), np.array(B, float))
base = Image.open(I + '172.webp').convert('RGB')
for scr, (df, top) in SCREENS.items():
    d = Image.open(I + df).convert('RGB'); bh = round(d.width / R)
    src = d.crop((0, top, d.width, top + bh)).resize((round(2400 * R), 2400), Image.LANCZOS)
    sm = Image.new('L', src.size, 0); dd = ImageDraw.Draw(sm)
    dd.rounded_rectangle((0, 0, src.width - 1, src.height - 1), 70, fill=255); dd.rectangle((0, src.height // 2, src.width, src.height), fill=255)
    nw = 392 / 3713 * src.width; cx = src.width / 2
    dd.rounded_rectangle((cx - nw / 2, -60, cx + nw / 2, 70), 22, fill=0)
    for K in (1, 2):
        SS = 3 if K == 1 else 2
        scene = base.resize((base.width * K, base.height * K), Image.LANCZOS) if K > 1 else base.copy(); W, H = scene.size
        qs = [(x * K * SS, y * K * SS) for x, y in Q]
        c = coeffs(qs, [(0, 0), (src.width, 0), (src.width, src.height), (0, src.height)])
        warped = src.transform((W * SS, H * SS), Image.PERSPECTIVE, tuple(c), Image.BICUBIC).resize((W, H), Image.LANCZOS)
        m = sm.transform((W * SS, H * SS), Image.PERSPECTIVE, tuple(c), Image.BICUBIC, fillcolor=0).resize((W, H), Image.LANCZOS)
        out = Image.composite(warped, scene, m)
        if K == 1:
            cw = round(H * 808 / 632); x0 = (W - cw) // 2
            o = out.crop((x0, 0, x0 + cw, H)).resize((1616, 1264), Image.LANCZOS)
            o.save(f's15-float-{scr}.png'); o.resize((808, 632), Image.LANCZOS).save(f's15-float-{scr}-808.png')
            out.resize((1000, 750), Image.LANCZOS).save(f'uw-float-{scr}-1000.jpg', quality=97, subsampling=0)
        else:
            out.resize((2000, 1500), Image.LANCZOS).save(f'uw-float-{scr}-2000.jpg', quality=97, subsampling=0)
        y0 = 160 * K   # 16:9 window (1600 x 900) around the laptop
        a = out.crop((0, y0, W, y0 + 900 * K))
        a.resize((2800, 1576) if K == 2 else (1400, 788), Image.LANCZOS).save(f'ab-float-{scr}-{2800 if K == 2 else 1400}.png')
    print('done', scr)
