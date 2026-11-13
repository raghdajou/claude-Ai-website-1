# Two flat page-card artboards (254 Serin, 255 Rei Mori), each with the Employees workforce-cost
# section and the Attendees flow chart. Each snap keeps its proportions and is centred on the page
# colour. 4000x3000 PNG (+2000, 1000) and a 16:9 artboard.
from PIL import Image, ImageFilter
I = '/tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/images/'
CARDS = {'serin': ('254.webp', (200, 100, 1400, 1099.5)), 'reimori': ('255.webp', (77, 150, 1522.5, 1049.5))}
def pieces(name, kind):
    """list of (file, box) stacked vertically, chosen so the snap suits the card's shape"""
    if kind == 'employees':
        return [('253.png', (152, 455, 1460, 1545))] if name == 'serin' else [('253.png', (152, 540, 1460, 1442))]
    return [('252.jpg', (112, 340, 1077, 1205))] if name == 'serin' else [('252.jpg', (112, 345, 1077, 418)), ('252.jpg', (112, 600, 1077, 1112))]
for name, (sf, (l, t, r, b)) in CARDS.items():
    base = Image.open(I + sf).convert('RGB'); asp = (r - l) / (b - t)
    for kind in ('employees', 'attendees'):
        parts = [Image.open(I + f).convert('RGB').crop(bx) for f, bx in pieces(name, kind)]
        bg = Image.open(I + pieces(name, kind)[0][0]).convert('RGB').getpixel((700, 1990))
        h = sum(p.height for p in parts); w = max(p.width for p in parts)
        if w / h < asp: W0, H0 = round(h * asp), h
        else: W0, H0 = w, round(w / asp)
        band = Image.new('RGB', (W0, H0), bg); y = (H0 - h) // 2
        for p in parts: band.paste(p, ((W0 - p.width) // 2, y)); y += p.height
        F = 2.5; out = base.resize((4000, 3000), Image.LANCZOS)
        cw, ch = round((r - l) * F), round((b - t) * F); k = cw / W0
        snap = band.resize((cw, ch), Image.LANCZOS).point(lambda v: round(255 * (v / 255) ** 1.08)).filter(ImageFilter.UnsharpMask(radius=0.7 * k, percent=70, threshold=2))
        out.paste(snap, (round(l * F), round(t * F)))
        n = f'{name}-{kind}'
        out.save(f'uw-{n}-x4-4000.png', optimize=True); out.resize((2000, 1500), Image.LANCZOS).save(f'uw-{n}-2000.png', optimize=True)
        out.resize((1000, 750), Image.LANCZOS).save(f'uw-{n}-1000.png', optimize=True)
        out.crop((0, 375, 4000, 2625)).resize((2800, 1576), Image.LANCZOS).save(f'ab-{n}-2800.png'); print('done', n, round(k, 2))
