# "Tilted wall" catalog slide (style 225): Foxlytics page snaps as white cards in staggered rows on
# near-black, the whole wall rotated ~16 degrees. The Productive Heat Map sits dead centre in the
# tallest row, flanked by the two colourful charts (payroll bubbles, performance bars); calmer
# tables/KPIs fill the outer rows. Snaps start at section titles and keep their aspect (no stretch).
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
I = '/tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/images/'
BG = (24, 24, 24)
C_IN, C_OUT = (232, 232, 232), (232, 232, 232)   # flat soft neutral grey, as the Integration reference
SN = {   # source, x0, y0, crop width, aspect
    'heat':   ('224.jpg', -47, 820, 904, 1.78),     # Analytics: Productive Heat Map
    'bubble': ('221.jpg', 180, 470, 1300, 1.67),   # Payroll: Efficiency Analysis bubbles
    'perf':   ('224.jpg', 100, 1420, 700, 1.67),    # Analytics: Performance Distribute
    'pipe':   ('222.jpg', 170, 790, 1175, 1.6),    # Projects: Pipeline Flow
    'table':  ('220.jpg', 112, 490, 726, 1.5),     # Payroll: salary table
    'trend':  ('224.jpg', 95, 410, 705, 1.9),      # Analytics: Headcount Trend + Turnover
    'pkpi':   ('222.jpg', 190, 420, 1160, 3.0),    # Projects In Numbers
    'hero':   ('223.jpg', 20, 150, 840, 1.6),      # Overview: welcome + KPIs
    'bars':   ('221.jpg', 200, 1355, 1290, 2.4),   # Payroll: salary distribution + over cost
    'donut':  ('223.jpg', 30, 580, 820, 2.2),      # Overview: workforce status + meetings
    'hiring': ('223.jpg', 30, 1010, 830, 3.2),     # Overview: hiring / interviews / alerts
    'work':   ('223.jpg', 30, 1325, 495, 1.0),     # Overview: workload distributions
    'leave':  ('223.jpg', 545, 1325, 310, 0.78),   # Overview: leaves requests
    'paytop': ('221.jpg', 0, 0, 1508, 2.4),        # Payroll: page top
}
ROWS = [  # (row height, x offset of the row's centre, cards left->right)
    (380, -150, ['donut', 'hiring', 'leave']),
    (400, 260, ['table', 'trend', 'pkpi']),
    (470, 0, ['perf', 'heat', 'bubble']),
    (400, -240, ['work', 'hero', 'pipe', 'bars']),
    (380, 180, ['paytop', 'table2', 'leave2']),
]
SN['table2'] = SN['bars']; SN['leave2'] = SN['work']
GAP = 60
def snap(key, w, h):
    f, x0, y0, cw, a = SN[key]; src = Image.open(I + f).convert('RGB'); ch = round(cw / a)
    page = src.getpixel((src.width // 2, src.height - 5))
    pad = round(cw * 0.05)   # breathing room above each card's title: the crop's top row repeated
    c = Image.new('RGB', (cw, ch), page); c.paste(src.crop((max(x0, 0), y0, min(x0 + cw, src.width), min(y0 + ch - pad, src.height))), (max(-x0, 0), pad))
    row = c.crop((0, pad, cw, pad + 1)).resize((cw, pad)); c.paste(row, (0, 0))
    k = w / cw; c = c.resize((w, h), Image.LANCZOS)
    return c.point(lambda v: round(255 * (v / 255) ** 1.1)).filter(ImageFilter.UnsharpMask(radius=0.6 * k, percent=80, threshold=2))
def render(F):
    PW, PH = round(3400 * F), round(2900 * F); plane = Image.new('RGB', (PW, PH), BG); pm = Image.new('L', (PW, PH), 0); cx, cy = PW / 2, PH / 2
    tot = sum(r[0] for r in ROWS) + GAP * (len(ROWS) - 1); y = cy - tot * F / 2
    for i, (rh, off, keys) in enumerate(ROWS):
        ws = [round(rh * SN[k][4] * F) for k in keys]; h = round(rh * F); g = round(GAP * F)
        if i == 2:   # centre the heat map exactly
            x = cx - ws[1] / 2 - g - ws[0]
        else:
            x = cx + off * F - (sum(ws) + g * (len(ws) - 1)) / 2
        for k, w in zip(keys, ws):
            card = snap(k, w, h); m = Image.new('L', (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), round(6 * F), fill=255)
            plane.paste(card, (round(x), round(y)), m); pm.paste(m, (round(x), round(y)), m); x += w + g
        if i == 2: hy = y + h / 2
        y += h + round(GAP * F)
    plane = plane.rotate(16, resample=Image.BICUBIC, center=(cx, hy), fillcolor=BG)
    pm = pm.rotate(16, resample=Image.BICUBIC, center=(cx, hy), fillcolor=0)
    W, H = round(1600 * F), round(1200 * F); box = (round(cx - W / 2), round(hy - H / 2), round(cx - W / 2) + W, round(hy - H / 2) + H)
    cards, m = np.asarray(plane.crop(box)).astype(np.float32), np.asarray(pm.crop(box)).astype(np.float32) / 255
    # studio backdrop: cool neutral grey, lighter behind the centre, gently darker to the corners
    yy, xx = np.mgrid[:H, :W]; r = np.hypot((xx - W / 2) / (W / 2), (yy - H * 0.47) / (H / 2))
    t = np.clip(r / 1.35, 0, 1) ** 1.6
    bg = np.array(C_IN)[None, None] * (1 - t[..., None]) + np.array(C_OUT)[None, None] * t[..., None]
    pass   # no grain: keeps the PNG under 5 MB; the gradient is smooth enough at 8 bits
    # soft, wide contact shadows under the cards (offset down, as if lit from above)
    from scipy import ndimage
    sh = ndimage.shift(m, (18 * F, 6 * F), order=1); sh = ndimage.gaussian_filter(sh, 26 * F) * 0.14 + ndimage.gaussian_filter(m, 5 * F) * 0.05
    bg = bg * (1 - np.clip(sh, 0, 0.45))[..., None]
    out = bg * (1 - m[..., None]) + cards * m[..., None]
    return Image.fromarray(out.clip(0, 255).astype(np.uint8))
out = render(2.5); out.save('uw-tiltsoft-x4-4000.png', optimize=True)
out.resize((2000, 1500), Image.LANCZOS).save('uw-tiltsoft-2000.png', optimize=True); out.resize((1000, 750), Image.LANCZOS).save('uw-tiltsoft-1000.png', optimize=True)
out.crop((0, 375, 4000, 2625)).resize((2800, 1576), Image.LANCZOS).save('ab-tiltsoft-2800.png')
print('done')
