# Wedding-style scene (card on sky with white petals): the hero picture becomes a Foxlytics screen and
# the serif line under it is rewritten for Foxlytics; the four petals stay in front (GrabCut masks).
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
I = '/tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/images/'
FONT = '/tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/scratchpad/fonts/is.woff2'
SS = 3
scene = Image.open(I + '152.webp').convert('RGB'); W, H = scene.size
HERO = (290, 263, 1709.5, 1244.5); RAD = 10
pet = np.asarray(Image.open('petal_mask.png').convert('L').filter(ImageFilter.GaussianBlur(0.8))).astype(np.float32) / 255
hm = Image.new('L', (W * SS, H * SS), 0)
ImageDraw.Draw(hm).rounded_rectangle([v * SS for v in HERO[:2]] + [HERO[2] * SS, (HERO[3] + 40) * SS], RAD * SS, fill=255)
ImageDraw.Draw(hm).rectangle((0, round(HERO[3] * SS), W * SS, H * SS), fill=0)
hm = np.asarray(hm.resize((W, H), Image.LANCZOS)).astype(np.float32) / 255
hw, hh = HERO[2] - HERO[0], HERO[3] - HERO[1]; r = hw / hh
SCREENS = {'brand': ('141.jpg', None), 'payroll': ('130.jpg', 420), 'projects': ('131.jpg', 560)}
for scr, (df, top) in SCREENS.items():
    d = Image.open(I + df).convert('RGB')
    if top is None:
        cw = round(d.height * r); x0 = int(np.clip(900 - cw / 2, 0, d.width - cw)); box = (x0, 0, x0 + cw, d.height)
    else:
        bh = round(d.width / r); t = min(top, d.height - bh); box = (0, t, d.width, t + bh)
    big = d.crop(box).resize((round(hw * SS), round(hh * SS)), Image.LANCZOS)
    layer = Image.new('RGB', (W * SS, H * SS)); layer.paste(big, (round(HERO[0] * SS), round(HERO[1] * SS)))
    layer = np.asarray(layer.resize((W, H), Image.LANCZOS)).astype(np.float32)
    a = np.asarray(scene).astype(np.float32)
    m = (hm * (1 - pet))[..., None]
    out = Image.fromarray((a * (1 - m) + layer * m).clip(0, 255).astype(np.uint8))
    # the serif line under the hero: cream over the old words, then the Foxlytics line (cut by the frame edge like the original)
    dr = ImageDraw.Draw(out); dr.rectangle((292, 1352, 1707, H), fill=(254, 253, 245))
    f = ImageFont.truetype(FONT, 78)
    for i, line in enumerate(["Foxlytics turns your people data into", "calm, clear decisions for every team."]):
        w = dr.textlength(line, font=f); dr.text((1000 - w / 2, 1366 + i * 70), line, font=f, fill=(24, 24, 22))
    cw = round(H * 808 / 632); x0 = (W - cw) // 2
    o = out.crop((x0, 0, x0 + cw, H)).resize((1616, 1264), Image.LANCZOS)
    o.save(f'pt-{scr}.png'); o.resize((808, 632), Image.LANCZOS).save(f'pt-{scr}-808.png'); print('done', scr)
