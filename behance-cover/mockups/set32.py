# iPad close-up corner (212) with the Projects page from its top.
# Two iPad mockups with the Employees page: "ipadclose" (212, front-on screen corner running off the
# frame, page from its top) and "ipadhand" (213, tilted iPad in one hand; screen edges line-fitted,
# fingers kept in front, workforce-cost section). Upwork 4:3 (1000, 2000 JPEG; 4000 PNG + JPEG) and
# Behance artboard 16:9 (1400, 2800).
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage
I = '/tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/images/'
page = Image.open(I + '240.jpg').convert('RGB')   # Projects page, from its top
def tone(p, k): return p.point(lambda v: round(255 * (v / 255) ** 1.12)).filter(ImageFilter.UnsharpMask(radius=0.7 * k, percent=90, threshold=2))
def coeffs(dst, pts):
    A, B = [], []
    for (x, y), (u, v) in zip(dst, pts):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]; B += [u, v]
    return np.linalg.solve(np.array(A, float), np.array(B, float))
def save(out, name, F, ab_top):
    W, H = out.size
    if F == 1:
        out.resize((1000, 750), Image.LANCZOS).save(f'uw-{name}-1000.jpg', quality=97, subsampling=0)
        out.crop((0, ab_top, W, ab_top + 900)).resize((1400, 788), Image.LANCZOS).save(f'ab-{name}-1400.png')
    elif F == 2:
        out.resize((2000, 1500), Image.LANCZOS).save(f'uw-{name}-2000.jpg', quality=97, subsampling=0)
        out.crop((0, ab_top * 2, W, ab_top * 2 + 1800)).resize((2800, 1576), Image.LANCZOS).save(f'ab-{name}-2800.png')
    else:
        out.save(f'uw-{name}-x4-4000.png', optimize=True); out.save(f'uw-{name}-x4-4000.jpg', quality=95, subsampling=0)

# --- close-up corner, front-on: page from its top at ~1:1 ---
base = Image.open(I + '212.png').convert('RGB'); g = np.asarray(base.convert('L')).astype(int)
lab, _ = ndimage.label(g > 200); scr = ndimage.binary_fill_holes(lab == lab[800, 900])
S0 = 1.03 * 1460 / 1384   # same on-screen text size as the Employees version
for F in (1, 2, 2.5):
    W, H = round(1600 * F), round(1200 * F); sc = base.resize((W, H), Image.LANCZOS)
    pw = round(page.width * S0 * F); p = page.resize((pw, round(page.height * S0 * F)), Image.LANCZOS)
    layer = Image.new('RGB', (W, H), (250, 250, 250)); layer.paste(tone(p, S0 * F), (round(300 * F), round(304 * F)))
    m = Image.fromarray((scr * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.5 * F))
    save(Image.composite(layer, sc, m), 'ipadclose-projects', F, 250)
print('done close')

