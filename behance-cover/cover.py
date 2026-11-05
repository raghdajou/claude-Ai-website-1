# Behance cover: a Studio-Display-style monitor (thick black bezel, aluminium stand, soft shadow,
# light floor fade, as in the reference) on the motion-blurred trees, its screen showing the
# Foxlytics Projects dashboard cropped so both charts fill it. Drawn at 4x and reduced for clean edges.
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFilter
I = '/tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/images/'
W, H = 1616, 1264; SS = 2                      # output size; supersampling for the shapes
w, h = W * SS, H * SS

# background: the trees, minus the screenshot's dark rounded border; the slider card in the middle is
# replaced by blurred surroundings (the monitor covers it, this only keeps its edges from showing)
bg = Image.open(I + '109.webp').convert('RGB').crop((9, 9, 1447, 793))
a = np.asarray(bg).astype(np.float32)
x0, y0, x1, y1 = 346, 238, 1088, 540                     # card, in the cropped image
fill = np.asarray(bg.filter(ImageFilter.GaussianBlur(60))).astype(np.float32)
for _ in range(3):                                       # pull the surroundings inwards
    a2 = a.copy(); a2[y0:y1, x0:x1] = fill[y0:y1, x0:x1]
    fill = np.asarray(Image.fromarray(a2.clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(40))).astype(np.float32)
a[y0:y1, x0:x1] = fill[y0:y1, x0:x1]
bg = Image.fromarray(a.clip(0, 255).astype(np.uint8))
k = max(w / bg.width, h / bg.height)
bg = bg.resize((round(bg.width * k), round(bg.height * k)), Image.LANCZOS)
bg = bg.crop(((bg.width - w) // 2, (bg.height - h) // 2, (bg.width - w) // 2 + w, (bg.height - h) // 2 + h))
canvas = bg.convert('RGBA')

# monitor geometry (outer bezel 1.74 : 1 like the reference)
MW = int(w * 0.86); MH = int(MW / 1.74); MX = (w - MW) // 2; MY = int(h * 0.12)
BZ = int(MW * 0.017); R = int(MW * 0.016)
NW = int(MW * 0.25); NX = (w - NW) // 2                   # stand column

def layer(): return Image.new('RGBA', (w, h), (0, 0, 0, 0))
# soft shadow behind the monitor and stand
sh = layer(); d = ImageDraw.Draw(sh)
d.rounded_rectangle((MX + 10 * SS, MY + 30 * SS, MX + MW - 10 * SS, MY + MH + 40 * SS), R, fill=(0, 0, 0, 120))
d.rectangle((NX + 6 * SS, MY + MH, NX + NW + 30 * SS, h), fill=(0, 0, 0, 70))
sh = sh.filter(ImageFilter.GaussianBlur(36 * SS)); canvas.alpha_composite(sh)

# light floor fade at the bottom, as in the reference
fade = np.zeros((h, w, 4), np.uint8); fade[..., :3] = (236, 238, 236)
yy = np.linspace(0, 1, h)[:, None]
fade[..., 3] = (np.clip((yy - 0.80) / 0.20, 0, 1) ** 1.6 * 200).astype(np.uint8)
canvas.alpha_composite(Image.fromarray(fade))

# stand column: brushed aluminium, darker just under the monitor, fading into the floor light
st = np.zeros((h - MY - MH, NW, 4), np.float32)
xs = np.linspace(0, 1, NW)[None, :]; ys = np.linspace(0, 1, h - MY - MH)[:, None]
tone = 206 + 22 * np.sin(np.pi * xs) - 34 * np.exp(-ys * 9) + 18 * ys
st[..., 0] = tone; st[..., 1] = tone + 1; st[..., 2] = tone + 3; st[..., 3] = 255
st[:, :2 * SS, :3] *= 0.86; st[:, -2 * SS:, :3] *= 0.86          # edges
canvas.alpha_composite(Image.fromarray(st.clip(0, 255).astype(np.uint8)), (NX, MY + MH))
canvas.alpha_composite(Image.fromarray(fade))                       # floor light over the stand foot

# bezel
bz = layer(); d = ImageDraw.Draw(bz)
d.rounded_rectangle((MX, MY, MX + MW, MY + MH), R, fill=(14, 14, 15, 255))
d.rounded_rectangle((MX + 2 * SS, MY + 2 * SS, MX + MW - 2 * SS, MY + MH - 2 * SS), R - 2 * SS, outline=(58, 58, 60, 255), width=SS)
canvas.alpha_composite(bz)

# screen: the dashboard from the section titles down through both charts and their legends
SX0, SY0, SX1, SY1 = MX + BZ, MY + BZ, MX + MW - BZ, MY + MH - BZ
sw, sh_ = SX1 - SX0, SY1 - SY0
dash = Image.open(I + '110.jpg').convert('RGB')
cw = dash.width; ch = round(cw * sh_ / sw)
top = 590                                                           # just above "Deadline Risk Readar"
scr = dash.crop((0, top, cw, top + ch)).resize((sw, sh_), Image.LANCZOS).convert('RGBA')
mask = Image.new('L', (sw, sh_), 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, sw - 1, sh_ - 1), 3 * SS, fill=255)
canvas.paste(scr, (SX0, SY0), mask)

# glass: a faint diagonal sheen across the upper left of the screen
g = np.zeros((sh_, sw, 4), np.float32); gx = np.linspace(0, 1, sw)[None, :]; gy = np.linspace(0, 1, sh_)[:, None]
g[..., :3] = 255; g[..., 3] = np.clip(1 - (gx * 0.9 + gy * 1.1) / 0.9, 0, 1) ** 2 * 26
canvas.alpha_composite(Image.fromarray(g.astype(np.uint8)), (SX0, SY0))

out = canvas.convert('RGB').resize((W, H), Image.LANCZOS)
out.save(sys.argv[1], quality=95) if sys.argv[1].endswith('.jpg') else out.save(sys.argv[1])
out.resize((808, 632), Image.LANCZOS).save(sys.argv[1].replace('.png', '-808.png'))
print('screen', sw // SS, 'x', sh_ // SS, 'dashboard crop', cw, 'x', ch, 'from y', top)
