# Flat white web card on a grainy green-white gradient ("mia"): the card becomes a Foxlytics page.
# Cover (1616 x 1264, 808 x 632) and Behance artboard (1400 x 788, 2800 x 1576) versions.
import numpy as np
from PIL import Image
I = '/tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/images/'
CARD = (175, 163.5, 1425, 1036)          # measured white card edges
SCREENS = {'brand': ('141.jpg', None), 'payroll': ('130.jpg', 255), 'projects': ('131.jpg', 470)}   # bands chosen so the whole charts show
base = Image.open(I + '162.webp').convert('RGB')
for scr, (df, top) in SCREENS.items():
    d = Image.open(I + df).convert('RGB'); r = (CARD[2] - CARD[0]) / (CARD[3] - CARD[1])
    if top is None:
        cw = round(d.height * r); x0 = int(np.clip(900 - cw / 2, 0, d.width - cw)); box = (x0, 0, x0 + cw, d.height)
    else:
        bh = round(d.width / r); box = (0, top, d.width, top + bh)
    page = d.crop(box)
    for K in (1, 2):
        scene = base.resize((base.width * K, base.height * K), Image.LANCZOS) if K > 1 else base.copy()
        S = 4   # place at 4x and scale down so the fractional top edge is anti-aliased
        big = scene.resize((scene.width * S, scene.height * S), Image.NEAREST)
        l, t, rr, b = [round(v * K * S) for v in CARD]
        big.paste(page.resize((rr - l, b - t), Image.LANCZOS), (l, t))
        out = big.resize(scene.size, Image.LANCZOS)
        if K == 1:
            W, H = out.size; cw = round(H * 808 / 632); x0 = (W - cw) // 2
            o = out.crop((x0, 0, x0 + cw, H)).resize((1616, 1264), Image.LANCZOS)
            o.save(f's11-mia-{scr}.png'); o.resize((808, 632), Image.LANCZOS).save(f's11-mia-{scr}-808.png')
        y0 = 150 * K   # 16:9 window (1600 x 900) holding the whole card
        a = out.crop((0, y0, out.width, y0 + 900 * K))
        (a.resize((2800, 1576), Image.LANCZOS).save(f'ab-mia-{scr}-2800.png') if K == 2 else a.resize((1400, 788), Image.LANCZOS).save(f'ab-mia-{scr}-1400.png'))
    print('done', scr)
