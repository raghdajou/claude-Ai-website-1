# Single page card on soft grey ("hartt", 230): the card (x 300-1300, y 100 to the bottom) becomes
# the Employees page, starting a little above the KPI cards. Upwork 4:3: 4000x3000 PNG (+2000, 1000);
# Behance artboard 16:9 (2800x1576).
from PIL import Image, ImageFilter
I = '/tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/images/'
L, T, R = 300, 100, 1300; TOP = 168
base = Image.open(I + '230.webp').convert('RGB'); page = Image.open(I + '231.webp').convert('RGB')
from PIL import ImageDraw
ImageDraw.Draw(page).rectangle((16, TOP - 6, 64, 187), fill=(241, 241, 241))   # clear the half-cut active icon above the KPIs
F = 2.5; W, H = 4000, 3000
out = base.resize((W, H), Image.LANCZOS)
w, h = round((R - L) * F), round((1200 - T) * F); k = w / page.width
PAD = 34   # extra space above the KPIs (source px): the clean row at TOP repeated
import numpy as np
pa = np.asarray(page); page = Image.fromarray(np.concatenate([np.repeat(pa[TOP:TOP + 1], PAD, 0), pa[TOP:]], 0)); TOP2 = 0
p = page.resize((w, round(page.height * k)), Image.LANCZOS); p = p.crop((0, 0, w, h))
p = p.point(lambda v: round(255 * (v / 255) ** 1.12)).filter(ImageFilter.UnsharpMask(radius=0.7 * k, percent=90, threshold=2))
out.paste(p, (round(L * F), round(T * F)))
out.save('uw-hartt-employees-x4-4000.png', optimize=True)
out.resize((2000, 1500), Image.LANCZOS).save('uw-hartt-employees-2000.png', optimize=True)
out.resize((1000, 750), Image.LANCZOS).save('uw-hartt-employees-1000.png', optimize=True)
# artboard: widen the plain grey at the sides, keep the card's top
import numpy as np
a = np.asarray(out); Ha = 2250; Wa = 4000
ab = Image.new('RGB', (round(Ha * 16 / 9), Ha), base.getpixel((20, 20))); ab.paste(out.crop((0, 0, W, Ha)), ((ab.width - W) // 2, 0))
ab.resize((2800, 1576), Image.LANCZOS).save('ab-hartt-employees-2800.png')
print('done')
