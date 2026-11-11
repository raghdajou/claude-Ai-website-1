# Laptop on a rock (243): screen quad from fitted top/left edges and the visible right/bottom edge
# points; Employees page from "Workforce Cost Intelligence" (a little space above) down to the
# chart's bottom labels, fitted without stretching. Notch + round top corners drawn in screen space.
# Upwork 4:3: 4000x3000 PNG (+2000, 1000); Behance artboard 16:9.
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
I = '/tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/images/'
Q = [(832.2, 262.2), (1388.5, 525.4), (1303.5, 911.8), (755.7, 632.4)]; R = 1.55
def coeffs(dst, pts):
    A, B = [], []
    for (x, y), (u, v) in zip(dst, pts):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]; B += [u, v]
    return np.linalg.solve(np.array(A, float), np.array(B, float))
page = Image.open(I + '244.jpg').convert('RGB'); bgc = page.getpixel((730, 1900))
TOP, BOT = 440, 1445
h = BOT - TOP; w = round(h * R); band = Image.new('RGB', (w, h), bgc)
band.paste(page.crop((0, TOP, page.width, BOT)), ((w - page.width) // 2, 0))
src = band.resize((round(3000 * R), 3000), Image.LANCZOS)
src = src.point(lambda v: round(255 * (v / 255) ** 1.08)).filter(ImageFilter.UnsharpMask(radius=1.6, percent=70, threshold=2))
sm = Image.new('L', src.size, 0); d = ImageDraw.Draw(sm); s = src.height / 2400
d.rounded_rectangle((0, 0, src.width - 1, src.height - 1), 60 * s, fill=255); d.rectangle((0, src.height // 2, src.width, src.height), fill=255)
nw = 392 / 3713 * src.width; cx = src.width / 2; d.rounded_rectangle((cx - nw / 2, -60 * s, cx + nw / 2, 70 * s), 22 * s, fill=0)
base = Image.open(I + '243.webp').convert('RGB'); F = 2; W, H = 4000, 3000; SS = 2
sc = base.resize((W, H), Image.LANCZOS)
qs = [(x * F * SS, y * F * SS) for x, y in Q]
c = coeffs(qs, [(0, 0), (src.width, 0), (src.width, src.height), (0, src.height)])
warped = src.transform((W * SS, H * SS), Image.PERSPECTIVE, tuple(c), Image.BICUBIC).resize((W, H), Image.LANCZOS)
m = sm.transform((W * SS, H * SS), Image.PERSPECTIVE, tuple(c), Image.BICUBIC, fillcolor=0).resize((W, H), Image.LANCZOS)
out = Image.composite(warped, sc, m)
out.save('uw-rock-employees-x4-4000.png', optimize=True)
out.resize((2000, 1500), Image.LANCZOS).save('uw-rock-employees-2000.png', optimize=True); out.resize((1000, 750), Image.LANCZOS).save('uw-rock-employees-1000.png', optimize=True)
out.crop((0, 300, 4000, 2550)).resize((2800, 1576), Image.LANCZOS).save('ab-rock-employees-2800.png')
print('done')
