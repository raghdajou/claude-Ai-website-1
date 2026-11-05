# Rovello-style cover for Foxlytics: the dashboard on a laptop in a dark studio, lit with the
# brand's lime and teal instead of Rovello's orange. 4:3 like the Framer gallery images.
# Laptop photo: ostudio on Unsplash (blank-screen mockup).
import sys, numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage
U = '/tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/scratchpad/unsplash-bg/'
I = '/tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/images/'
TOP = int(sys.argv[2]) if len(sys.argv) > 2 else 560          # where the dashboard crop starts
photo = Image.open(U + 'laptop.jpg').convert('RGB')             # 3000 x 2000
P = np.asarray(photo).astype(np.float32)
lum = P.mean(-1)

# the screen: the large bright area; its four corners from the extremes of x+y and x-y
scr = ndimage.binary_opening(lum > 170, iterations=3)
lab, n = ndimage.label(scr); scr = lab == (np.argmax(ndimage.sum(scr, lab, range(1, n + 1))) + 1)
ys, xs = np.nonzero(scr)
tl = (xs[np.argmin(xs + ys)], ys[np.argmin(xs + ys)]); br = (xs[np.argmax(xs + ys)], ys[np.argmax(xs + ys)])
tr = (xs[np.argmax(xs - ys)], ys[np.argmax(xs - ys)]); bl = (xs[np.argmin(xs - ys)], ys[np.argmin(xs - ys)])
print('screen corners', tl, tr, br, bl)

# dashboard, cropped to the screen's own proportions, warped into the quad
dash = Image.open(I + '110.jpg').convert('RGB')
sw = np.hypot(tr[0] - tl[0], tr[1] - tl[1]); sh = np.hypot(bl[0] - tl[0], bl[1] - tl[1])
cw = dash.width; ch = round(cw * sh / sw)
src = dash.crop((0, TOP, cw, TOP + ch))
def coeffs(dst, srcpts):
    A, B = [], []
    for (x, y), (u, v) in zip(dst, srcpts):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]; B += [u, v]
    return np.linalg.solve(np.array(A, float), np.array(B, float))
c = coeffs([tl, tr, br, bl], [(0, 0), (src.width, 0), (src.width, src.height), (0, src.height)])
warped = np.asarray(src.transform(photo.size, Image.PERSPECTIVE, tuple(c), Image.BICUBIC)).astype(np.float32)
# the screen mask keeps the camera notch and the bezel exactly as photographed; edges softened by a pixel
m = ndimage.gaussian_filter(ndimage.binary_dilation(scr, iterations=2).astype(np.float32), 0.8)[..., None]
m *= (lum[..., None] > 60)                                       # never paint over the dark notch
out = P * (1 - m) + warped * m

# brand light: a lime-to-teal glow behind and around the laptop, plus the screen's spill on the desk
H, W = lum.shape; yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
cx, cy = (tl[0] + br[0]) / 2, (tl[1] + br[1]) / 2
r = np.hypot((xx - cx) / (W * 0.55), (yy - cy) / (H * 0.62))
glow = np.exp(-r ** 2 * 2.2)[..., None]
mix = np.clip((xx - W * 0.2) / (W * 0.7), 0, 1)[..., None]
col = np.array([196, 226, 101]) * (1 - mix) + np.array([64, 186, 170]) * mix       # lime -> teal (the chart colours)
dark = (1 - np.clip((lum[..., None] - 40) / 120, 0, 1))                          # light the dark studio, not the screen
out = out + col * glow * dark * 0.42
spill = np.exp(-(((xx - cx) / (W * 0.30)) ** 2 + ((yy - (br[1] + 260)) / (H * 0.10)) ** 2))[..., None]
out = out + np.array([214, 236, 190]) * spill * dark * 0.22
img = Image.fromarray(out.clip(0, 255).astype(np.uint8))

# 4:3 framing around the laptop, at 2400 x 1800 (2x the Framer gallery's 1200 x 900)
fw = 2667; fx = int(np.clip(cx - fw / 2, 0, W - fw))
img = img.crop((fx, 0, fx + fw, 2000)).resize((2400, 1800), Image.LANCZOS)
img.save(sys.argv[1]); img.resize((1200, 900), Image.LANCZOS).save(sys.argv[1].replace('.png', '-1200.png'))
