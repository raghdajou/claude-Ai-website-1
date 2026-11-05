# Foxlytics take on the "Always Rising." visual: the fisheye grass-and-sky photo with its slogan and
# logo lifted out of the sky, then a two-word Foxlytics line on one level and the Foxlytics fox logo
# (taken from the dashboard, turned white) beneath it. Behance cover size, 1616 x 1264.
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy import ndimage
HERE = '/tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/scratchpad/cover/'
I = '/tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/images/'
LINE = sys.argv[2] if len(sys.argv) > 2 else 'Grow Gently.'
W, H = 1616, 1264

src = np.asarray(Image.open(I + '112.webp').convert('RGB')).astype(np.float32)[0:512, 15:672]   # the card, no white margin
# fill: the old slogan and logo (bright marks on the sky) and the card's white bottom corners
mask = np.zeros(src.shape[:2], bool)
mask[160:224, 188:472] = True                                  # the old slogan, whole
mask[226:280, 262:390] = True                                  # the old logo, whole
mask |= src.min(-1) > 238                                      # white corners
mask = ndimage.binary_dilation(mask, iterations=3)
known = (~mask).astype(np.float32); img = src.copy()
# fill from the surrounding sky only (normalised blur), wide first, then finer where it is well covered
fill = None
for s_ in (60, 30, 15):
    num = ndimage.gaussian_filter(src * known[..., None], (s_, s_, 0)); den = ndimage.gaussian_filter(known, s_)[..., None]
    f = num / np.maximum(den, 1e-6)
    fill = f if fill is None else np.where(den > 0.25, f, fill)
img = np.where(mask[..., None], fill, src)
img = np.where(mask[..., None], ndimage.gaussian_filter(img, (3, 3, 0)), img)
# keep the sky's fine grain in the filled patch, so it is not flatter than the rest
grain = np.random.default_rng(3).normal(0, 1.4, src.shape[:2])[..., None]
img = np.where(mask[..., None], img + grain, img)
bg = Image.fromarray(img.clip(0, 255).astype(np.uint8))
k = max(W / bg.width, H / bg.height)
bg = bg.resize((round(bg.width * k), round(bg.height * k)), Image.LANCZOS)
bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
bg = bg.filter(ImageFilter.UnsharpMask(radius=2.2, percent=55, threshold=2)).convert('RGBA')

# the line, on one level, where the old one sat (centre 50.7% across, 36% down)
font = ImageFont.truetype(HERE + 'fonts/Poppins-Regular.ttf', 118)
txt = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(txt)
l, t, r, b = d.textbbox((0, 0), LINE, font=font, anchor='ls')
cx, base = W * 0.507, H * 0.36 + (b - t) / 2 - b
d.text((cx - (r - l) / 2 - l, base), LINE, font=font, fill=(255, 255, 255, 255), anchor='ls')
bg.alpha_composite(txt)

# the Foxlytics logo from the dashboard header, made white
dash = np.asarray(Image.open(I + '110.jpg').convert('L')).astype(np.float32)[90:165, 45:300]
a = np.clip((246 - dash) / 230, 0, 1)
ys, xs = np.nonzero(a > 0.05); a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
logo = np.zeros(a.shape + (4,), np.uint8); logo[..., :3] = 255; logo[..., 3] = (a * 255).astype(np.uint8)
logo = Image.fromarray(logo); lw = int(W * 0.17); lh = round(logo.height * lw / logo.width)
logo = logo.resize((lw, lh), Image.LANCZOS)
bg.alpha_composite(logo, (int(cx - lw / 2), int(H * 0.476 - lh / 2)))
bg.convert('RGB').save(sys.argv[1])
bg.convert('RGB').resize((808, 632), Image.LANCZOS).save(sys.argv[1].replace('.png', '-808.png'))
