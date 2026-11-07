# "Felix" style: white rounded card on a blurred photo; the card becomes a Foxlytics page (one per
# screen, each from a chosen row). Upwork 4:3 (1000x750, 2000x1500 JPEG) and Behance artboard 16:9
# (1400x788, 2800x1576; the blurred backdrop is mirrored outward at the sides to widen the frame).
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
I = '/tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/images/'
CARD, RAD = (106.5, 149.0, 1492.5, 1050.0), 12
PAGES = {'overview': ('170.jpg', 0), 'analytics': ('186.webp', 0), 'attendees': ('187.webp', 228),
         'payroll': ('188.webp', 1055), 'projects': ('189.webp', 560), 'employees': ('190.jpg', 470)}
base = Image.open(I + '192.png').convert('RGB')
for name, (f, top) in PAGES.items():
    src = Image.open(I + f).convert('RGB')
    for K in (1, 2):
        S = 2; sc = base.resize((base.width * K, base.height * K), Image.LANCZOS); W, H = sc.size
        l, t, r, b = [v * K for v in CARD]; cw, ch = round(r - l), round(b - t)
        k = cw / src.width; p = src.resize((cw, round(src.height * k)), Image.LANCZOS)
        y = round(top * k); q = Image.new('RGB', (cw, ch), p.getpixel((cw // 2, p.height - 3)))
        q.paste(p.crop((0, y, cw, min(p.height, y + ch))), (0, 0))
        q = q.point(lambda v: round(255 * (v / 255) ** 1.12)).filter(ImageFilter.UnsharpMask(radius=0.7 * k, percent=90, threshold=2))
        m = Image.new('L', (W * S, H * S), 0); ImageDraw.Draw(m).rounded_rectangle((l * S, t * S, r * S, b * S), RAD * K * S, fill=255)
        m = m.resize((W, H), Image.LANCZOS); layer = Image.new('RGB', (W, H)); layer.paste(q, (round(l), round(t)))
        out = Image.composite(layer, sc, m)
        out.resize((2000, 1500) if K == 2 else (1000, 750), Image.LANCZOS).save(f'uw-felix-{name}-{2000 if K == 2 else 1000}.jpg', quality=97, subsampling=0)
        a = np.asarray(out); padx = round((H - 100 * K * 2) * 16 / 9 - W) // 2 + 1
        a = np.pad(a, ((0, 0), (padx, padx), (0, 0)), mode='reflect')[100 * K:H - 100 * K]
        ab = Image.fromarray(a); ab = ab.crop(((ab.width - round(ab.height * 16 / 9)) // 2, 0, (ab.width + round(ab.height * 16 / 9)) // 2, ab.height))
        ab.resize((2800, 1576) if K == 2 else (1400, 788), Image.LANCZOS).save(f'ab-felix-{name}-{2800 if K == 2 else 1400}.png')
    print('done', name)
