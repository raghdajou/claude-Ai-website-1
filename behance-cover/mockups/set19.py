# Wide page card (NURO layout: page at x 136-1864 from y 135, running off the bottom) on the cleaned
# streaked-blue wallpaper of the "Masen James" desktop, with a soft drop shadow. Usage: page top name.
# Upwork 4:3 (1000x750, 2000x1500 JPEG). Behance artboard 16:9 (1400x788, 2800x1576): the wallpaper is
# mirrored outward at the sides first, then the same page is placed in the middle.
import sys, numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage
I = '/tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/images/'
SRC, TOP, NAME = sys.argv[1], int(sys.argv[2]), sys.argv[3]
wall = Image.open('wall193.png').convert('RGB'); W0, H0 = wall.size
def compose(bg, l, t, r, b, K):
    sc = np.asarray(bg).astype(np.float32).copy(); H, W = sc.shape[:2]
    sh = np.zeros((H, W), np.float32); sh[t + 18 * K:b, l:r] = 1
    sc *= (1 - ndimage.gaussian_filter(sh, 30 * K) * 0.55)[..., None]
    p = Image.open(I + SRC).convert('RGB'); k = (r - l) / p.width
    p = p.resize((r - l, round(p.height * k)), Image.LANCZOS); y = round(TOP * k); p = p.crop((0, y, r - l, y + b - t))
    p = p.point(lambda v: round(255 * (v / 255) ** 1.12)).filter(ImageFilter.UnsharpMask(radius=0.7 * k, percent=90, threshold=2))
    sc[t:b, l:r] = np.asarray(p).astype(np.float32)
    return Image.fromarray(sc.clip(0, 255).astype(np.uint8))
for K in (1, 2):
    w = wall.resize((W0 * K, H0 * K), Image.LANCZOS); W, H = w.size
    out = compose(w, 136 * K, 135 * K, 1864 * K, H, K)
    out.resize((2000, 1500) if K == 2 else (1000, 750), Image.LANCZOS).save(f'uw-desk-{NAME}-{2000 if K == 2 else 1000}.jpg', quality=97, subsampling=0)
    Ha = H - 100 * K; Wa = round(Ha * 16 / 9); padx = (Wa - W) // 2 + 1
    wa = Image.fromarray(np.pad(np.asarray(w), ((0, 0), (padx, padx), (0, 0)), mode='reflect')[:Ha])
    wa = wa.crop(((wa.width - Wa) // 2, 0, (wa.width - Wa) // 2 + Wa, Ha)); off = (Wa - W) // 2
    ab = compose(wa, (136 + 0) * K + off, 135 * K, 1864 * K + off, Ha, K)
    ab.resize((2800, 1576) if K == 2 else (1400, 788), Image.LANCZOS).save(f'ab-desk-{NAME}-{2800 if K == 2 else 1400}.png')
print('done', NAME)
