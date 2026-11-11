# Five flat "page card" styles (245-249), each holding a different Foxlytics page snap. The snap is
# a full-width band of the page at the card's aspect (no stretch), taken from a chosen row; corners
# follow each card's radius. Outputs per mockup: 4000x3000 PNG (+2000, 1000) and a 16:9 artboard.
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
I = '/tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/images/'
SETS = {   # this Employees page in all five cards, from "Workforce Cost Intelligence" with a little space above
    'nirvaan-employees':    ('245.png',  (86.5, 70, 1514, 1200), 20, False),
    'serife-employees':     ('246.webp', (140.5, 167.5, 1460, 1034), 24, True),
    'evident-employees':    ('247.webp', (125, 192, 1474.5, 1008), 14, True),
    'travertine-employees': ('248.webp', (136.5, 137.5, 1850.5, 1500), 8, False),
    'leon-employees':       ('249.webp', (256.5, 104.5, 1717, 1395.5), 40, True),
}
PF, TOP, BOT = '250.jpg', 440, 1445   # must show: title (505) down to the chart's bottom labels (~1430)
for name, (sf, (l, t, r, b), rad, rb) in SETS.items():
    pf, top = PF, TOP
    base = Image.open(I + sf).convert('RGB'); F = 4000 / base.width; W, H = 4000, round(base.height * F)
    sc = base.resize((W, H), Image.LANCZOS)
    page = Image.open(I + pf).convert('RGB'); bg = page.getpixel((page.width // 2, page.height - 5))
    cw, ch = round((r - l) * F), round((b - t) * F)
    asp = (r - l) / (b - t); need = BOT - TOP
    if page.width / asp >= need:   # tall card: full width, page continues below the section
        bw, bh = page.width, round(page.width / asp)
    else:                          # wide card: fit the section's height, page colour at the sides
        bw, bh = round(need * asp), need
    band = Image.new('RGB', (bw, bh), bg)
    band.paste(page.crop((0, top, page.width, min(top + bh, page.height))), ((bw - page.width) // 2, 0)); k = cw / bw
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
