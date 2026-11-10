# Upwork Project Catalog slide in the "page grid" style (3x3 white page cards on cool grey, outer
# cards running off the frame). Each card is one snap of a Foxlytics page, cropped to start at a
# section title and to the exact aspect of the card's visible area, so nothing is stretched.
# Rendered at 2.5x the 1600x1200 layout = 4000x3000 PNG (+ 2000x1500 / 1000x750, artboard 16:9).
from PIL import Image, ImageFilter
I = '/tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/images/'
BG = (222, 226, 227)
COLS = {'L': (0, 352), 'C': (400, 1200), 'R': (1248, 1600)}
ROWS = {'T': (0, 326), 'M': (375, 825), 'B': (873, 1200)}
CARDS = {   # card: (source, crop x0, y0, width) -- height follows the card's aspect
    'LT': ('224.jpg', 440, 412, 360),    # Analytics: Turnover Rate
    'CT': ('220.jpg', 112, 618, 726),    # Payroll: employee salary table
    'RT': ('224.jpg', 95, 418, 345),     # Analytics: Headcount Trend & Forecast
    'LM': ('223.jpg', 545, 1325, 310),   # Overview: Leaves Requests
    'CM': ('224.jpg', -8, 826, 826),     # Analytics: Productive Heat Map (centre)
    'RM': ('223.jpg', 30, 1325, 400),    # Overview: Workload Distributions
    'LB': ('221.jpg', 195, 1350, 540),   # Payroll (bottom): Salary Distribution Analysis
    'CB': ('222.jpg', 170, 790, 1175),   # Projects: Projects Pipeline Flow
    'RB': ('223.jpg', 35, 290, 405),     # Overview: Foxlytics In Numbers (KPIs)
}
def snap(f, x0, y0, w, aspect):
    src = Image.open(I + f).convert('RGB'); h = round(w / aspect)
    page = src.getpixel((src.width // 2, src.height - 5))
    c = Image.new('RGB', (w, h), page); c.paste(src.crop((max(x0, 0), y0, min(x0 + w, src.width), min(y0 + h, src.height))), (max(-x0, 0), 0))
    return c
for F, tag in ((2.5, 'x4-4000'), (1.25, '2000'), (0.625, '1000')):
    W, H = round(1600 * F), round(1200 * F); out = Image.new('RGB', (W, H), BG)
    for key, (f, x0, y0, w) in CARDS.items():
        (l, r), (t, b) = COLS[key[0]], ROWS[key[1]]
        cw, ch = round((r - l) * F), round((b - t) * F)
        s = snap(f, x0, y0, w, (r - l) / (b - t)); k = cw / s.width
        s = s.resize((cw, ch), Image.LANCZOS)
        s = s.point(lambda v: round(255 * (v / 255) ** 1.1)).filter(ImageFilter.UnsharpMask(radius=0.6 * k, percent=80, threshold=2))
        out.paste(s, (round(l * F), round(t * F)))
    if tag == 'x4-4000':
        out.save('uw-grid-x4-4000.png', optimize=True)
        out.crop((0, 375, W, 375 + 2250)).resize((2800, 1576), Image.LANCZOS).save('ab-grid-2800.png')
    else:
        out.save(f'uw-grid-{tag}.png', optimize=True)
print('done')
