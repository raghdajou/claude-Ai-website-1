# Tablet held in two hands ("tablet"): the screen (x 348-1252, y 316-908, front-on) gets a Foxlytics page;
# the thumbs and hands that cover the screen edges stay in front. Hand edge per row is measured from the
# original (first white / coloured pixel inward from the screen edge), smoothed, and interpolated across
# the dark rows of the old site (black bar, dark photos). Upwork 4:3 (1000, 2000 JPEG, 4000 PNG) and
# Behance artboard 16:9 (1400, 2800).
import sys, numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage
I = '/tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/images/'
SRC, TOP, NAME = sys.argv[1], int(sys.argv[2]), sys.argv[3]
base = Image.open(I + '211.png').convert('RGB'); a0 = np.asarray(base).astype(int); g = a0.mean(-1); sat = a0.max(-1) - a0.min(-1)
L, T, R, B = 348, 316, 1252, 908
ys = np.arange(H0 := base.height)
left = np.full(H0, float(L)); right = np.full(H0, float(R))
rows = list(range(566, 736))
lv = [next((x for x in range(L, 520) if g[y, x] > 200), L) for y in rows]
rv = [next((x for x in range(R + 5, 1100, -1) if g[y, x] > 200 or sat[y, x] > 40), R) for y in rows + list(range(736, B + 1))]
left[566:736] = lv; left[736:785] = np.linspace(lv[-1], 402, 49); left[785:] = 402
right[566:B + 1] = rv
left = ndimage.uniform_filter1d(left, 7); right = ndimage.median_filter(right, 5); right[B - 4:B + 1] = right[B - 5]; left[B - 4:B + 1] = left[B - 5]; right[736:B + 1] += 2   # cover the old photo's last pixels at the hand edge
left[:566] = L; right[:566] = R
src = Image.open(I + SRC).convert('RGB')
for F in (1, 2, 2.5):
    W, H = round(base.width * F), round(base.height * F); sc = base.resize((W, H), Image.LANCZOS)
    w, h = round((R - L) * F), round((B - T) * F); k = w / src.width
    p = src.crop((0, TOP, src.width, TOP + round(h / k))).resize((w, h), Image.LANCZOS)
    p = p.point(lambda v: round(255 * (v / 255) ** 1.12)).filter(ImageFilter.UnsharpMask(radius=0.7 * k, percent=90, threshold=2))
    layer = Image.new('RGB', (W, H)); layer.paste(p, (round(L * F), round(T * F)))
    xx = np.arange(W)[None, :] / F; yy = np.arange(H)[:, None] / F; yi = np.clip(yy.astype(int), 0, H0 - 1)
    m = (xx >= left[yi] + 0.5) & (xx <= right[yi] - 0.5) & (yy >= T) & (yy <= B)
    m = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6 * F))
    out = Image.composite(layer, sc, m)
    if F == 1:
        out.resize((1000, 750), Image.LANCZOS).save(f'uw-{NAME}-1000.jpg', quality=97, subsampling=0)
        out.crop((0, 150, W, 1050)).resize((1400, 788), Image.LANCZOS).save(f'ab-{NAME}-1400.png')
    elif F == 2:
        out.resize((2000, 1500), Image.LANCZOS).save(f'uw-{NAME}-2000.jpg', quality=97, subsampling=0)
        out.crop((0, 300, W, 2100)).resize((2800, 1576), Image.LANCZOS).save(f'ab-{NAME}-2800.png')
    else:
        out.save(f'uw-{NAME}-x4-4000.png', optimize=True); out.save(f'uw-{NAME}-x4-4000.jpg', quality=95, subsampling=0)
print('done', NAME)
