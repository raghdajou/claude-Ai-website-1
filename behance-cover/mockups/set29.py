# Studio monitor ("allia", 228, 2000x1500) with the Leave Requests page from its title down.
# Screen corners from line-fitted edges. Upwork 4:3: 4000x3000 PNG (+2000, 1000); artboard 16:9.
import math, numpy as np
from PIL import Image, ImageDraw, ImageFilter
I = '/tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/images/'
Q = [(321.2, 158.2), (1701.4, 145.8), (1681.1, 1028.9), (299.3, 1005.8)]
def coeffs(dst, pts):
    A, B = [], []
    for (x, y), (u, v) in zip(dst, pts):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]; B += [u, v]
    return np.linalg.solve(np.array(A, float), np.array(B, float))
base = Image.open(I + '228.webp').convert('RGB')
sw = (math.dist(Q[0], Q[1]) + math.dist(Q[3], Q[2])) / 2; sh = (math.dist(Q[0], Q[3]) + math.dist(Q[1], Q[2])) / 2; r = sw / sh
page = Image.open(I + '229.jpg').convert('RGB')
# a little space above "Requests In Numbers", down to the end of the first charts' notes; the band is
# taller than the screen ratio, so it is centred on the page colour (no stretching)
TOP, BOT = 180, 655; PAD = 34
h = BOT - TOP + PAD; w = round(h * r); bg = page.getpixel((page.width // 2, page.height - 5))
band = Image.new('RGB', (w, h), bg); import numpy as np
pa = np.asarray(page); body = Image.fromarray(np.concatenate([np.repeat(pa[TOP:TOP + 1], PAD, 0), pa[TOP:BOT]], 0))
band.paste(body, ((w - page.width) // 2, 0))
src = band.resize((round(2600 * r), 2600), Image.LANCZOS)
src = src.point(lambda v: round(255 * (v / 255) ** 1.12)).filter(ImageFilter.UnsharpMask(radius=2.4, percent=90, threshold=2))
F = 2; W, H = 4000, 3000; SS = 2
sc = base.resize((W, H), Image.LANCZOS)
qs = [(x * F * SS, y * F * SS) for x, y in Q]
c = coeffs(qs, [(0, 0), (src.width, 0), (src.width, src.height), (0, src.height)])
warped = src.transform((W * SS, H * SS), Image.PERSPECTIVE, tuple(c), Image.BICUBIC).resize((W, H), Image.LANCZOS)
m = Image.new('L', (W * SS, H * SS), 0); ImageDraw.Draw(m).polygon(qs, fill=255); m = m.resize((W, H), Image.LANCZOS)
out = Image.composite(warped, sc, m)
out.save('uw-allia-leave-x4-4000.png', optimize=True)
out.resize((2000, 1500), Image.LANCZOS).save('uw-allia-leave-2000.png', optimize=True); out.resize((1000, 750), Image.LANCZOS).save('uw-allia-leave-1000.png', optimize=True)
out.crop((0, 200, 4000, 2450)).resize((2800, 1576), Image.LANCZOS).save('ab-allia-leave-2800.png')
print('ratio', round(r, 3), w, h)
