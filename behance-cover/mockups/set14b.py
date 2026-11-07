# Two overlapping web pages on grey ("nuro"): the back page becomes Leave Requests, the front page
# Overview (welcome screen), each shown from the top of the page (intro first). The front page's soft shadow on the
# back page is measured from the original and laid back on. Behance artboard 1400x788 (+2x) and
# Upwork 4:3 1000x750 (+2x, JPEG).
import numpy as np
from PIL import Image, ImageFilter
I = '/tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/images/'
base = Image.open(I + '167.webp').convert('RGB'); W0, H0 = base.size
BACK, FRONT = (766, 135, 1864, H0), (135, 400, 1240, H0)
g = np.asarray(base.convert('L')).astype(np.float32)
prof = np.clip(np.median(g[450:1000, 1240:1300], 0) / 255, 0, 1)          # shadow strength by distance from the front page
def page(f, w, h):
    p = Image.open(I + f).convert('RGB'); k = w / p.width
    p = p.resize((w, round(p.height * k)), Image.LANCZOS).crop((0, 0, w, h))
    # the screenshots are small, so they are enlarged; a light unsharp mask brings back crisp text edges
    return p.filter(ImageFilter.UnsharpMask(radius=0.8 * k, percent=90, threshold=2))
for K in (1, 2):
    sc = base.resize((W0 * K, H0 * K), Image.LANCZOS); a = np.asarray(sc).astype(np.float32).copy()
    l, t, r, b = [v * K for v in BACK]
    a[t:b, l:r] = np.asarray(page('168.jpg', r - l, b - t)).astype(np.float32)
    sh = np.ones((H0 * K, W0 * K), np.float32); n = len(prof) * K
    sh[FRONT[1] * K + 12 * K:, FRONT[2] * K:FRONT[2] * K + n] = np.repeat(prof, K)[None, :]
    ramp = np.clip((np.arange(H0 * K) - (FRONT[1] + 2) * K) / (30 * K), 0, 1)[:, None]   # fade in at the top corner
    sh = 1 - (1 - sh) * ramp
    a[:, :, :] *= np.where(np.zeros_like(sh, bool), 1, sh)[..., None] if True else 1
    l, t, r, b = [v * K for v in FRONT]
    a[t:b, l:r] = np.asarray(page('170.jpg', r - l, b - t)).astype(np.float32)
    out = Image.fromarray(a.clip(0, 255).astype(np.uint8)); W, H = out.size
    cw = round(H * 4 / 3); x0 = (W - cw) // 2                                   # Upwork 4:3
    out.crop((x0, 0, x0 + cw, H)).resize((2000, 1500) if K == 2 else (1000, 750), Image.LANCZOS).save(
        f'uw-nuro2-{2000 if K == 2 else 1000}.jpg', quality=97, subsampling=0)
    ch = round(W * 9 / 16); y0 = 95 * K                                         # Behance 16:9, top of both pages kept
    out.crop((0, y0, W, y0 + ch)).resize((2800, 1576) if K == 2 else (1400, 788), Image.LANCZOS).save(
        f'ab-nuro2-{2800 if K == 2 else 1400}.png')
print('done')
