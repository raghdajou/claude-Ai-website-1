# Five flat "page card" styles (245-249), each holding a different Foxlytics page snap. The snap is
# a full-width band of the page at the card's aspect (no stretch), taken from a chosen row; corners
# follow each card's radius. Outputs per mockup: 4000x3000 PNG (+2000, 1000) and a 16:9 artboard.
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
I = '/tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/images/'
SETS = {   # name: scene, card (l, t, r, b), radius, round bottom?, page, start row
    'nirvaan-projects':    ('245.png',  (86.5, 70, 1514, 1200), 20, False, '238.webp', 0),
    'serife-payroll':      ('246.webp', (140.5, 167.5, 1460, 1034), 24, True, '221.jpg', 416),
    'evident-projects':    ('247.webp', (125, 192, 1474.5, 1008), 14, True, '240.jpg', 400),
    'travertine-projects': ('248.webp', (136.5, 137.5, 1850.5, 1500), 8, False, '237.webp', 0),
    'leon-employees':      ('249.webp', (256.5, 104.5, 1717, 1395.5), 40, True, '190.jpg', 180),
}
for name, (sf, (l, t, r, b), rad, rb, pf, top) in SETS.items():
    base = Image.open(I + sf).convert('RGB'); F = 4000 / base.width; W, H = 4000, round(base.height * F)
    sc = base.resize((W, H), Image.LANCZOS)
    page = Image.open(I + pf).convert('RGB'); bg = page.getpixel((page.width // 2, page.height - 5))
    cw, ch = round((r - l) * F), round((b - t) * F); k = cw / page.width
    bh = round((b - t) / (r - l) * page.width)
    band = Image.new('RGB', (page.width, bh), bg); end = 1325 if name == 'serife-payroll' else page.height   # stop before the next section's titles
    band.paste(page.crop((0, top, page.width, min(top + bh, end))), (0, 0))
    snap = band.resize((cw, ch), Image.LANCZOS)
    snap = snap.point(lambda v: round(255 * (v / 255) ** 1.08)).filter(ImageFilter.UnsharpMask(radius=0.7 * k, percent=70, threshold=2))
    S = 2; m = Image.new('L', (cw * S, ch * S), 0); d = ImageDraw.Draw(m)
    d.rounded_rectangle((0, 0, cw * S - 1, ch * S - 1), round(rad * F * S), fill=255)
    if not rb: d.rectangle((0, ch * S // 2, cw * S, ch * S), fill=255)
    m = m.resize((cw, ch), Image.LANCZOS)
    sc.paste(snap, (round(l * F), round(t * F)), m)
    out = sc if H == 3000 else sc.resize((4000, 3000), Image.LANCZOS)
    out.save(f'uw-{name}-x4-4000.png', optimize=True)
    out.resize((2000, 1500), Image.LANCZOS).save(f'uw-{name}-2000.png', optimize=True); out.resize((1000, 750), Image.LANCZOS).save(f'uw-{name}-1000.png', optimize=True)
    out.crop((0, 375, 4000, 2625)).resize((2800, 1576), Image.LANCZOS).save(f'ab-{name}-2800.png')
    print('done', name, round(k, 2))
