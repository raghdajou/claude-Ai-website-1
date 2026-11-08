# 4x PNG of the "intelli" mockup (angled monitor, faded Foxlytics wordmark) with the Projects screen:
# the scene is enlarged to 4000 px wide, the screen is re-warped at that scale (sharp UI), and the
# wordmark backdrop (wm_layer from wordmark.py) is enlarged and laid back outside the monitor.
import math, numpy as np
from PIL import Image, ImageDraw, ImageFilter
exec(open('set7.py').read().split('for (name, (f, q, asp))')[0])
f, q, asp = SCENES['intelli']; df, top = SCREENS['projects']
base = Image.open(I + f).convert('RGB'); F = 4000 / base.width; W, H = 4000, round(base.height * F)
dash = Image.open(I + df).convert('RGB'); r = asp
bh = round(dash.width / r); t = min(top, dash.height - bh)
src = dash.crop((0, t, dash.width, t + bh)).resize((round(3600 * r), 3600), Image.LANCZOS)
SS2 = 2; qs = [(x * F * SS2, y * F * SS2) for x, y in q]
c = coeffs(qs, [(0, 0), (src.width, 0), (src.width, src.height), (0, src.height)])
warped = src.transform((W * SS2, H * SS2), Image.PERSPECTIVE, tuple(c), Image.BICUBIC).resize((W, H), Image.LANCZOS)
warped = warped.filter(ImageFilter.UnsharpMask(radius=1.2, percent=60, threshold=1))
m = Image.new('L', (W * SS2, H * SS2), 0); ImageDraw.Draw(m).polygon(qs, fill=255)
m = np.asarray(m.resize((W, H), Image.LANCZOS)).astype(np.float32)[..., None] / 255
sc = np.asarray(base.resize((W, H), Image.LANCZOS)).astype(np.float32)
raw = sc * (1 - m) + np.asarray(warped).astype(np.float32) * m
layer = np.asarray(Image.fromarray(np.load('wm_layer.npy').clip(0, 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)).astype(np.float32)
mon = np.asarray(Image.fromarray((np.load('wm_mon.npy') * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)).astype(np.float32)[..., None] / 255
out = Image.fromarray((raw * mon + layer * (1 - mon)).clip(0, 255).astype(np.uint8))
out.resize((4000, 3000), Image.LANCZOS).save('uw-intelli-projects-x4-4000.png', optimize=True); print(out.size)
