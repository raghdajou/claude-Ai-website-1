# Single wide web page on grey ("nuro single"): the page becomes the Foxlytics given Foxlytics screen from
# a chosen row (command line: page file, start row, name), enlarged with Lanczos and a light unsharp mask. Upwork 4:3 (1000x750, 2000x1500 JPEG) and
# Behance artboard (1400x788, 2800x1576).
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
I = '/tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/images/'
base = Image.open(I + '184.webp').convert('RGB'); W0, H0 = base.size
PAGE = (135.5, 134.5, 1864.5, H0)
import sys
SRC, TOP, NAME = sys.argv[1], int(sys.argv[2]), sys.argv[3]   # page file, source row to start at, output name
for K in (1, 2):
    sc = base.resize((W0 * K, H0 * K), Image.LANCZOS)
    l, t, r, b = [round(v * K) for v in PAGE]
    p = Image.open(I + SRC).convert('RGB'); k = (r - l) / p.width
    p = p.resize((r - l, round(p.height * k)), Image.LANCZOS); y = round(TOP * k); bg = p.getpixel((p.width // 2, p.height - 3))
    q = Image.new('RGB', (r - l, b - t), bg); q.paste(p.crop((0, y, r - l, min(p.height, y + b - t))), (0, 0)); p = q   # page colour below its end
    # high quality: Lanczos enlarge, slightly deeper text tones, one gentle unsharp mask (no halos)
    p = p.point(lambda v: round(255 * (v / 255) ** 1.12))
    p = p.filter(ImageFilter.UnsharpMask(radius=0.7 * k, percent=90, threshold=2))
    sc.paste(p, (l, t))
    W, H = sc.size; cw = round(H * 4 / 3); x0 = (W - cw) // 2
    sc.crop((x0, 0, x0 + cw, H)).resize((2000, 1500) if K == 2 else (1000, 750), Image.LANCZOS).save(
        f'uw-{NAME}-{2000 if K == 2 else 1000}.jpg', quality=97, subsampling=0)
    ch = round(W * 9 / 16); y0 = 95 * K
    sc.crop((0, y0, W, y0 + ch)).resize((2800, 1576) if K == 2 else (1400, 788), Image.LANCZOS).save(
        f'ab-{NAME}-{2800 if K == 2 else 1400}.png')
print('done')
