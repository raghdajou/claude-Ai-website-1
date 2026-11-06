# "intelli" scene: the faded "Intelli™" behind the monitor becomes "Foxlytics" with the same fade.
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage
SS = 3
def meet(a, b):
    y = (b[0] * a[1] + b[1]) / (1 - b[0] * a[0]); return (a[0] * y + a[1], y)
orig = np.asarray(Image.open('../../images/155.webp').convert('RGB')).astype(np.float32); H, W = orig.shape[:2]; g = orig.mean(-1)
# monitor silhouette: bezel outer edges (fitted) pushed out over the silver rim, top corners rounded
T, L, R = (0.08424, 174.301), (0.00093, 278.249), (0.06722, 1147.529)
tl = meet((L[0], L[1] - 11), (T[0], T[1] - 9)); tr = meet((R[0], R[1] + 4), (T[0], T[1] - 9))
mon = Image.new('L', (W * SS, H * SS), 0); d = ImageDraw.Draw(mon)
d.polygon([(x * SS, y * SS) for x, y in [tl, tr, (R[0] * H + R[1] + 4, H), (L[0] * H + L[1] - 11, H)]], fill=255)
mon = np.asarray(mon.resize((W, H), Image.LANCZOS)).astype(np.float32) / 255
band = np.zeros((H, W), bool); band[:470] = True
free = mon < 0.02
# backdrop without the word: estimate from pixels the word does not touch, iterated
bg = ndimage.gaussian_filter(orig, (80, 80, 0))
for it in range(4):
    text = band & free & (g > bg.mean(-1) + 4)
    text = ndimage.binary_dilation(text, iterations=6)
    w = (free & ~text).astype(np.float32)
    s = 30
    bg = ndimage.gaussian_filter(orig * w[..., None], (s, s, 0)) / np.maximum(ndimage.gaussian_filter(w, s), 1e-4)[..., None]
np.save('wm_bg.npy', bg); np.save('wm_text.npy', text); np.save('wm_mon.npy', mon)
vis = orig.copy(); vis[text] = vis[text] * 0.5 + np.array([255, 0, 0]) * 0.5
Image.fromarray(vis.astype(np.uint8)).save('wm_textmask.png')
clean = np.where(band[..., None], bg, orig)
Image.fromarray(clean.clip(0, 255).astype(np.uint8)).save('wm_clean.png')

# ---- new word ----
FONT = '/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf'
WORD, TRACK, TOP, CX, SPAN = 'Foxlytics', -0.03, 42, 724, 1300
probe = ImageFont.truetype(FONT, 400)
wid = sum(probe.getlength(ch) for ch in WORD) + TRACK * 400 * (len(WORD) - 1)
size = round(400 * SPAN / wid); font = ImageFont.truetype(FONT, size * SS)
cap_top = font.getbbox('F')[1]; cap_h = (font.getbbox('F')[3] - cap_top) / SS
canvas = Image.new('L', (W * SS, H * SS), 0); dr = ImageDraw.Draw(canvas)
x = (CX - SPAN / 2) * SS
for ch in WORD:
    dr.text((x, TOP * SS - cap_top), ch, font=font, fill=255); x += font.getlength(ch) + TRACK * size * SS
cov = np.asarray(canvas.resize((W, H), Image.LANCZOS)).astype(np.float32) / 255
# fade measured on the old word (cap top 42 → baseline ~390), stretched onto the new cap height
ys = np.array([42, 65, 90, 115, 140, 165, 190, 215, 240, 265, 290, 315, 340, 365, 390, 410], float)
al = np.array([.96, .94, .81, .67, .59, .50, .39, .30, .25, .22, .18, .13, .08, .05, .025, 0])
yy = np.arange(H, dtype=float); fade = np.interp(TOP + (yy - TOP) * (348 / cap_h), ys, al)
A = (cov * fade[:, None])[..., None]
new_bg = clean * (1 - A) + 255 * A
blend = np.clip((480 - yy) / 20, 0, 1)[:, None, None]          # band → untouched picture below y≈470
np.save('wm_layer.npy', new_bg * blend + orig * (1 - blend)); print('font size', size, 'cap', cap_h)
