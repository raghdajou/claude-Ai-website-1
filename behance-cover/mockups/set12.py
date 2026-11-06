# "Mascara" card on a grainy sky: the front photo of the stack becomes the Foxlytics Analytics screen
# (KPI cards + Performance Distribute chart); the stacked cards behind, the card and the sky stay.
# Cover 1616x1264, Behance artboard 1400x788 (+2x), Upwork 4:3 1000x750 (+2x, JPEG).
import numpy as np
from PIL import Image, ImageDraw
I = '/tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/images/'
PHOTO = (284.2, 438.0, 1314.0, 1084.2); RAD = 12          # measured front photo, rounded top corners
base = Image.open(I + '164.webp').convert('RGB')
SCREENS = {'analytics': ('165.jpg', 555)}                    # band: KPI cards and the whole bar chart
for scr, (df, top) in SCREENS.items():
    d = Image.open(I + df).convert('RGB'); r = (PHOTO[2] - PHOTO[0]) / (PHOTO[3] - PHOTO[1])
    bh = round(d.width / r); page = d.crop((0, top, d.width, top + bh))
    for K in (1, 2):
        scene = base.resize((base.width * K, base.height * K), Image.LANCZOS) if K > 1 else base.copy()
        S = 3; W, H = scene.size
        l, t, rr, b = [v * K * S for v in PHOTO]
        layer = Image.new('RGB', (W * S, H * S)); layer.paste(page.resize((round(rr - l), round(b - t)), Image.LANCZOS), (round(l), round(t)))
        m = Image.new('L', (W * S, H * S), 0); dm = ImageDraw.Draw(m)
        dm.rounded_rectangle((l, t, rr, b), RAD * K * S, fill=255); dm.rectangle((l, (t + b) / 2, rr, b), fill=255)
        layer = layer.resize((W, H), Image.LANCZOS); m = m.resize((W, H), Image.LANCZOS)
        out = Image.composite(layer, scene, m)
        if K == 1:
            cw = round(H * 808 / 632); x0 = (W - cw) // 2
            o = out.crop((x0, 0, x0 + cw, H)).resize((1616, 1264), Image.LANCZOS)
            o.save(f's12-mascara-{scr}.png'); o.resize((808, 632), Image.LANCZOS).save(f's12-mascara-{scr}-808.png')
        else:
            for w, h in ((2000, 1500), (1000, 750)): out.resize((w, h), Image.LANCZOS).save(f'uw-mascara-{scr}-{w}.jpg', quality=95, subsampling=0)
        y0 = 200 * K   # 16:9 window holding the whole card
        a = out.crop((0, y0, W, y0 + 900 * K))
        a.resize((2800, 1576) if K == 2 else (1400, 788), Image.LANCZOS).save(f'ab-mascara-{scr}-{2800 if K == 2 else 1400}.png')
    print('done', scr)
