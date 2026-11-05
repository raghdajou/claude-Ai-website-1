# A laptop drawn in true 3D perspective (simple pinhole camera looking down at the ground) and set
# into an overhead flower photo, its screen showing the Foxlytics dashboard. Behance cover 1616 x 1264.
import sys, math, numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage
HERE = '/tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/scratchpad/hires/'
DASH = Image.open('/tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/images/110.jpg').convert('RGB')
W, H, SS = 1616, 1264, 3
name, cx, cy, scale = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
YAW = math.radians(float(sys.argv[5]) if len(sys.argv) > 5 else -14)
ELEV = float(sys.argv[6]) if len(sys.argv) > 6 else 52      # camera angle above the ground
OCC = float(sys.argv[7]) if len(sys.argv) > 7 else 0        # share of the laptop's height that front flowers may cover

# background: cover crop of the photo
bg = Image.open(HERE + name + '.jpg').convert('RGB')
k = max(W / bg.width, H / bg.height); bg = bg.resize((round(bg.width * k), round(bg.height * k)), Image.LANCZOS)
bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))

# camera: above the ground, tilted 52 degrees down, laptop at the origin (units: cm; z up)
EL = math.radians(ELEV); DIST = 120; F = 2.0 * W * SS * scale
cam = np.array([0, -DIST * math.cos(EL), DIST * math.sin(EL)])
fwd = -cam / np.linalg.norm(cam); right = np.array([1.0, 0, 0]); up = np.cross(right, fwd)
def P(p):
    x, y, z = p; c, s = math.cos(YAW), math.sin(YAW)
    q = np.array([c * x - s * y, s * x + c * y, z]) - cam
    zc = q @ fwd; return (cx * SS + F * (q @ right) / zc, cy * SS - F * (q @ up) / zc)
def poly(pts): return [P(p) for p in pts]

BW, BD, BT = 31.0, 22.0, 1.5            # base width, depth, thickness
LA = math.radians(112)                   # lid opening angle
LD, LT = 21.0, 0.6                       # lid height, thickness
x0, x1, y0, y1 = -BW / 2, BW / 2, -BD / 2, BD / 2
def lid(u, v, off=0.0):                  # point on the lid: u across (0..1), v up the lid (0..1)
    d = v * LD
    return (x0 + u * BW, y1 + d * math.cos(math.pi - LA) + off * math.sin(math.pi - LA), BT + d * math.sin(math.pi - LA) - off * math.cos(math.pi - LA))

img = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
# shadow on the ground, drawn separately and blurred
sh = Image.new('L', (W * SS, H * SS), 0); ds = ImageDraw.Draw(sh)
ds.polygon(poly([(x0 - 1, y0 - 1, 0), (x1 + 1, y0 - 1, 0), (x1 + 3, y1 + 9, 0), (x0 + 3, y1 + 9, 0)]), fill=200)
sh = sh.filter(ImageFilter.GaussianBlur(14 * SS))
# a tight contact shadow right under the base, so it sits on the ground
cs = Image.new('L', (W * SS, H * SS), 0)
ImageDraw.Draw(cs).polygon(poly([(x0, y0, 0), (x1, y0, 0), (x1, y1, 0), (x0, y1, 0)]), fill=255)
cs = cs.filter(ImageFilter.GaussianBlur(3 * SS))

ALU, ALU_D, ALU_L = (196, 199, 204), (150, 153, 158), (222, 224, 228)
# base: front and right side, then top
d.polygon(poly([(x0, y0, 0), (x1, y0, 0), (x1, y0, BT), (x0, y0, BT)]), fill=ALU_D)
d.polygon(poly([(x1, y0, 0), (x1, y1, 0), (x1, y1, BT), (x1, y0, BT)]), fill=(170, 173, 178))
d.polygon(poly([(x0, y0, BT), (x1, y0, BT), (x1, y1, BT), (x0, y1, BT)]), fill=ALU)
d.line(poly([(x0, y0, BT), (x1, y0, BT)]), fill=ALU_L, width=2 * SS)
# keyboard well and keys
kx0, kx1, ky0, ky1 = x0 + 2.2, x1 - 2.2, y1 - 11.2, y1 - 1.4
d.polygon(poly([(kx0, ky0, BT), (kx1, ky0, BT), (kx1, ky1, BT), (kx0, ky1, BT)]), fill=(40, 41, 44))
rows, cols = 6, 14; gx = (kx1 - kx0) / cols; gy = (ky1 - ky0) / rows
for r in range(rows):
    for c in range(cols):
        a, b = kx0 + c * gx + 0.12, ky0 + r * gy + 0.12
        d.polygon(poly([(a, b, BT), (a + gx - 0.24, b, BT), (a + gx - 0.24, b + gy - 0.24, BT), (a, b + gy - 0.24, BT)]), fill=(22, 22, 24))
# trackpad
tw = 13.0; d.polygon(poly([(-tw / 2, y0 + 1.4, BT), (tw / 2, y0 + 1.4, BT), (tw / 2, ky0 - 1.0, BT), (-tw / 2, ky0 - 1.0, BT)]), fill=(186, 189, 194))
# lid: back edge thickness, aluminium frame, black bezel, screen
d.polygon(poly([lid(0, 0, -LT), lid(1, 0, -LT), lid(1, 1, -LT), lid(0, 1, -LT)]), fill=(120, 123, 128))
d.polygon(poly([lid(0, 0), lid(1, 0), lid(1, 1), lid(0, 1)]), fill=(150, 153, 158))
m = 0.012; d.polygon(poly([lid(m, 0.03), lid(1 - m, 0.03), lid(1 - m, 1 - m * 1.4), lid(m, 1 - m * 1.4)]), fill=(10, 10, 12))
sq = [lid(0.035, 0.07), lid(0.965, 0.07), lid(0.965, 0.955), lid(0.035, 0.955)]   # screen: TL..? (v=1 is top)
tl, tr, br, bl = P(sq[3]), P(sq[2]), P(sq[1]), P(sq[0])
sw = (math.dist(tl, tr) + math.dist(bl, br)) / 2; shh = (math.dist(tl, bl) + math.dist(tr, br)) / 2
src = DASH.crop((0, 560, DASH.width, 560 + round(DASH.width * shh / sw))).resize((int(sw), int(shh)), Image.LANCZOS)
A, B = [], []
for (x, y), (u, v) in zip([tl, tr, br, bl], [(0, 0), (src.width, 0), (src.width, src.height), (0, src.height)]):
    A += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]; B += [u, v]
c = np.linalg.solve(np.array(A, float), np.array(B, float))
scr = src.transform(img.size, Image.PERSPECTIVE, tuple(c), Image.BICUBIC).convert('RGBA')
sm = Image.new('L', img.size, 0); ImageDraw.Draw(sm).polygon([tl, tr, br, bl], fill=255)
img.paste(scr, (0, 0), sm)
# notch, and a faint glass sheen
nw = 0.06; d.polygon(poly([lid(0.5 - nw, 0.955), lid(0.5 + nw, 0.955), lid(0.5 + nw, 0.935), lid(0.5 - nw, 0.935)]), fill=(10, 10, 12))

# lighting: soft light from the upper left over the whole laptop, plus a tint of the scene's colour
L = np.asarray(img).astype(np.float32)
yy, xx = np.mgrid[0:L.shape[0], 0:L.shape[1]].astype(np.float32)
ys, xs = np.nonzero(L[..., 3] > 0); ny = (yy - ys.min()) / (ys.max() - ys.min() + 1); nx = (xx - xs.min()) / (xs.max() - xs.min() + 1)
light = 1.06 - 0.16 * (0.6 * ny + 0.4 * nx)
tint = np.asarray(bg).reshape(-1, 3).mean(0) / 255
L[..., :3] = np.clip(L[..., :3] * light[..., None] * (0.9 + 0.1 * tint * 2), 0, 255)
img = Image.fromarray(L.astype(np.uint8))
out = bg.convert('RGBA')
shade = Image.new('RGBA', (W, H), (8, 14, 6, 0)); shade.putalpha(sh.resize((W, H), Image.LANCZOS).point(lambda v: int(v * 0.85)))
out.alpha_composite(shade)
cshade = Image.new('RGBA', (W, H), (4, 6, 3, 0)); cshade.putalpha(cs.resize((W, H), Image.LANCZOS).point(lambda v: int(v * 0.75)))
out.alpha_composite(cshade)
out.alpha_composite(img.resize((W, H), Image.LANCZOS))
if OCC > 0:   # flowers in front: restore coloured (non-green) flower pixels over the lower part of the laptop
    la = np.asarray(img.resize((W, H), Image.LANCZOS))[..., 3] > 8
    ys, xs = np.nonzero(la); bot = ys.max(); band = np.zeros((H, W), bool)
    band[int(bot - OCC * (bot - ys.min())):, :] = True
    hsv = np.asarray(bg.convert('HSV')).astype(np.float32); hh = hsv[..., 0] * 360 / 255
    flower = (hsv[..., 1] > 60) & ~((hh > 50) & (hh < 150)) & (hsv[..., 2] > 70)
    flower = ndimage.binary_opening(flower, iterations=1)
    flower = ndimage.binary_fill_holes(ndimage.binary_closing(flower, iterations=5))   # whole clumps, not speckles
    lab, n = ndimage.label(flower); sizes = ndimage.sum(flower, lab, range(1, n + 1))
    flower = np.isin(lab, np.nonzero(sizes > 400)[0] + 1) & band
    fm = ndimage.gaussian_filter(flower.astype(np.float32), 0.8)[..., None]
    o2 = np.asarray(out.convert('RGB')).astype(np.float32) * (1 - fm) + np.asarray(bg).astype(np.float32) * fm
    out = Image.fromarray(o2.astype(np.uint8)).convert('RGBA')
o = out.convert('RGB'); o.save(HERE + f'meadow3d-{name}.png'); o.resize((808, 632), Image.LANCZOS).save(HERE + f'meadow3d-{name}-808.png')
print('ok', name)
