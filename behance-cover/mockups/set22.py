# Laptop on the purple chair (158) with the whole Employees Workforce Cost section (fitted, not stretched), rendered
# at 1x, 2x and 2.5x (4000 px) scene scale: cover 1616x1264 (+808), Upwork 4:3 (1000x750, 2000x1500
# JPEG, 4000x3000 PNG), Behance artboard 16:9 (1400x788, 2800x1576).
import math, numpy as np
from PIL import Image, ImageDraw, ImageFilter
exec(open('set8.py').read().split('for (name, (f, q, asp')[0])
f, q, asp, notch, _ = SCENES['chair']; DF, TOP = '209.jpg', 470
base = Image.open(I + f).convert('RGB'); dash = Image.open(I + DF).convert('RGB'); r = asp
# like the single-page reference: full width, starting just above 'Workforce Cost Intelligence', down to
# the bottom value labels of the chart (no stretching: a 1.547 band of the page)
bh = round(dash.width / r); pg = dash.crop((0, 482, dash.width, 482 + bh))
src = pg.resize((round(3600 * r), 3600), Image.LANCZOS)
sm = Image.new('L', src.size, 0); d = ImageDraw.Draw(sm); s = src.height / 2400
d.rounded_rectangle((0, 0, src.width - 1, src.height - 1), 55 * s, fill=255); d.rectangle((0, src.height // 2, src.width, src.height), fill=255)
nw = 392 / 3713 * src.width; cx = src.width / 2; d.rounded_rectangle((cx - nw / 2, -60 * s, cx + nw / 2, 66 * s), 22 * s, fill=0)
for F in (1, 2, 2.5):
    W, H = round(base.width * F), round(base.height * F); S = 2
    scene = base.resize((W, H), Image.LANCZOS)
    qs = [(x * F * S, y * F * S) for x, y in q]
    c = coeffs(qs, [(0, 0), (src.width, 0), (src.width, src.height), (0, src.height)])
    warped = src.transform((W * S, H * S), Image.PERSPECTIVE, tuple(c), Image.BICUBIC).resize((W, H), Image.LANCZOS)
    warped = warped.filter(ImageFilter.UnsharpMask(radius=0.6 * F, percent=60, threshold=1))
    m = sm.transform((W * S, H * S), Image.PERSPECTIVE, tuple(c), Image.BICUBIC, fillcolor=0).resize((W, H), Image.LANCZOS)
    out = Image.composite(warped, scene, m)
    if F == 1:
        cw = round(H * 808 / 632); x0 = (W - cw) // 2; o = out.crop((x0, 0, x0 + cw, H)).resize((1616, 1264), Image.LANCZOS)
        o.save('s22-chair-employees.png'); o.resize((808, 632), Image.LANCZOS).save('s22-chair-employees-808.png')
        out.resize((1000, 750), Image.LANCZOS).save('uw-chair-employees-1000.jpg', quality=97, subsampling=0)
        out.crop((0, 100, W, 1000)).resize((1400, 788), Image.LANCZOS).save('ab-chair-employees-1400.png')
    elif F == 2:
        out.resize((2000, 1500), Image.LANCZOS).save('uw-chair-employees-2000.jpg', quality=97, subsampling=0)
        out.crop((0, 200, W, 2000)).resize((2800, 1576), Image.LANCZOS).save('ab-chair-employees-2800.png')
    else:
        out.save('uw-chair-employees-x4-4000.png', optimize=True)
    print('done', F, out.size)
