# "Cascade" style (pages tilted ~27 degrees, stacked down a diagonal) on the frosted backdrops of the
# two display mockups (197 dark, 196 light). The display is removed from each backdrop first: its
# columns are rebuilt by interpolating the unmasked rows, which keeps the vertical frosted streaks.
# Pages: Overview (top), Analytics (middle), Projects (bottom). Upwork 4:3 and Behance artboard 16:9.
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
from scipy import ndimage
I = '/tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/images/'
def clean(f):
    a = np.asarray(Image.open(I + f).convert('RGB')).astype(np.float32); H, W = a.shape[:2]
    m = np.zeros((H, W), bool); m[288:1005, 180:1420] = True; m[995:, 640:960] = True
    out = a.copy(); ys = np.arange(H)
    for x in range(W):
        if m[:, x].any():
            ok = ~m[:, x]
            for c in range(3): out[m[:, x], x, c] = np.interp(ys[m[:, x]], ys[ok], a[ok, x, c])
    sm = ndimage.gaussian_filter(out, (20, 3, 0)); mm = ndimage.gaussian_filter(m.astype(np.float32), 8)[..., None]
    return Image.fromarray((out * (1 - mm) + sm * mm).clip(0, 255).astype(np.uint8))
PAGES = [('170.jpg', 0, (446, -95)), ('186.webp', 240, (800, 600)), ('189.webp', 560, (1154, 1295))]   # one page apart along the tilted strip, with gaps
ANGLE, PW, R = 27, 1150, 1.78
for name, bgf in (('cascade-dark', '197.webp'), ('cascade-light', '196.webp')):
    bg0 = clean(bgf)
    for K in (1, 2):
        bg = bg0.resize((1600 * K, 1200 * K), Image.LANCZOS).convert('RGBA')
        for f, top, (cx, cy) in PAGES:
            src = Image.open(I + f).convert('RGB'); w, h = PW * K, round(PW * K / R); k = w / src.width
            p = src.crop((0, top, src.width, top + round(h / k))).resize((w, h), Image.LANCZOS)
            p = p.point(lambda v: round(255 * (v / 255) ** 1.12)).filter(ImageFilter.UnsharpMask(radius=0.7 * k, percent=90, threshold=2))
            S = 2   # rotate at 2x then downscale for clean edges
            pr = p.resize((w * S, h * S), Image.LANCZOS).convert('RGBA').rotate(ANGLE, resample=Image.BICUBIC, expand=True)
            pr = pr.resize((pr.width // S, pr.height // S), Image.LANCZOS)
            sh = Image.new('RGBA', pr.size, (0, 0, 0, 0)); a = np.asarray(pr)[..., 3].astype(np.float32)
            sha = ndimage.gaussian_filter(a, 22 * K) * 0.45
            sh = Image.fromarray(np.dstack([np.zeros_like(a)] * 3 + [sha]).astype(np.uint8), 'RGBA')
            x0, y0 = cx * K - pr.width // 2, cy * K - pr.height // 2
            bg.alpha_composite(sh, (x0 + 10 * K, y0 + 22 * K)); bg.alpha_composite(pr, (x0, y0))
        out = bg.convert('RGB')
        out.resize((2000, 1500) if K == 2 else (1000, 750), Image.LANCZOS).save(f'uw-{name}-{2000 if K == 2 else 1000}.jpg', quality=97, subsampling=0)
        out.crop((0, 150 * K, 1600 * K, 1050 * K)).resize((2800, 1576) if K == 2 else (1400, 788), Image.LANCZOS).save(f'ab-{name}-{2800 if K == 2 else 1400}.png')
    print('done', name)
