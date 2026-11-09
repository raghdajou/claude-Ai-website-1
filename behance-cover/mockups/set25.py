# Two iPad mockups with the Employees page: "ipadclose" (212, front-on screen corner running off the
# frame, page from its top) and "ipadhand" (213, tilted iPad in one hand; screen edges line-fitted,
# fingers kept in front, workforce-cost section). Upwork 4:3 (1000, 2000 JPEG; 4000 PNG + JPEG) and
# Behance artboard 16:9 (1400, 2800).
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage
I = '/tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/images/'
page = Image.open(I + '209.jpg').convert('RGB')
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

import sys
PAGE, BOX, NAME = sys.argv[1], tuple(int(v) for v in sys.argv[2].split(',')), sys.argv[3]
page = Image.open(I + PAGE).convert('RGB')
# --- tilted iPad in a hand ---
base = Image.open(I + '213.png').convert('RGB'); a = np.asarray(base).astype(int); g = a.mean(-1)
Q = [(612.7, 144.9), (1240.6, 532.5), (950.2, 1003.0), (322.2, 615.4)]; R = 4 / 3
band = page.crop(BOX)   # a 4:3 window of the page
src = band.resize((3200, 2400), Image.LANCZOS)
sm = Image.new('L', src.size, 0); ImageDraw.Draw(sm).rounded_rectangle((0, 0, src.width - 1, src.height - 1), 70, fill=255)
quad = Image.new('L', base.size, 0); ImageDraw.Draw(quad).polygon(Q, fill=255); quad = np.asarray(quad) > 0
sat = a.max(-1) - a.min(-1)
skin = (sat > 25) & (a[..., 0] > a[..., 2] + 10) & (g < 200)          # warm skin tones = the fingers over the screen
skin[:780] = False                                                   # the hand is only at the bottom (the old photo is warm too)
lab, n = ndimage.label(skin); sz = ndimage.sum(skin, lab, range(1, n + 1))
hand = ndimage.binary_fill_holes(ndimage.binary_closing(np.isin(lab, np.nonzero(sz > 2000)[0] + 1), iterations=2))
hand = ndimage.binary_dilation(hand, iterations=1)
for F in (1, 2, 2.5):
    W, H = round(1600 * F), round(1200 * F); sc = base.resize((W, H), Image.LANCZOS); SS = 2
    qs = [(x * F * SS, y * F * SS) for x, y in Q]
    c = coeffs(qs, [(0, 0), (src.width, 0), (src.width, src.height), (0, src.height)])
    warped = src.transform((W * SS, H * SS), Image.PERSPECTIVE, tuple(c), Image.BICUBIC).resize((W, H), Image.LANCZOS)
    warped = tone(warped, 0.6 * F) if False else warped.filter(ImageFilter.UnsharpMask(radius=0.6 * F, percent=60, threshold=1))
    m = sm.transform((W * SS, H * SS), Image.PERSPECTIVE, tuple(c), Image.BICUBIC, fillcolor=0).resize((W, H), Image.LANCZOS)
    hm = Image.fromarray((hand * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.6 * F))
    m = Image.fromarray((np.asarray(m).astype(np.float32) * (1 - np.asarray(hm).astype(np.float32) / 255)).astype(np.uint8))
    save(Image.composite(warped, sc, m), NAME, F, 130)
print('done hand')
