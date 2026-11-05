# The Rovello laptop scene with only the screen replaced by the Foxlytics dashboard, cropped to the
# Behance cover shape (808 x 632, made at 2x). Bezel, notch, keys and the orange set stay untouched.
import sys, numpy as np
from PIL import Image, ImageDraw
I = '/tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/images/'
TOP = int(sys.argv[2]) if len(sys.argv) > 2 else 560                 # dashboard crop start (the charts)
scene = Image.open(I + '113.webp').convert('RGB')                     # 1930 x 1438
TL, TR, BR, BL = (448, 163), (1526, 163), (1538.2, 853.6), (435.8, 853.6)   # screen corners, measured (+1 px over the old edge)
NOTCH = (931, 150, 1043.5, 182.5)                                       # camera notch, measured

dash = Image.open(I + '110.jpg').convert('RGB')
sw, sh = TR[0] - TL[0], BL[1] - TL[1]
cw = dash.width; ch = round(cw * sh / sw)
src = dash.crop((0, TOP, cw, TOP + ch))
def coeffs(dst, pts):
    A, B = [], []
    for (x, y), (u, v) in zip(dst, pts):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]; B += [u, v]
    return np.linalg.solve(np.array(A, float), np.array(B, float))
SS = 3   # warp at 3x and reduce, so the small dashboard text stays crisp
big = (scene.width * SS, scene.height * SS)
c = coeffs([(x * SS, y * SS) for x, y in (TL, TR, BR, BL)], [(0, 0), (src.width, 0), (src.width, src.height), (0, src.height)])
warped = src.transform(big, Image.PERSPECTIVE, tuple(c), Image.BICUBIC)
m = Image.new('L', big, 0); d = ImageDraw.Draw(m)
d.polygon([(x * SS, y * SS) for x, y in (TL, TR, BR, BL)], fill=255)
corner = Image.new('L', big, 0)                                        # the screen's rounded top corners
ImageDraw.Draw(corner).rounded_rectangle((BL[0] * SS, TL[1] * SS, BR[0] * SS, BR[1] * SS + 40 * SS), 10 * SS, fill=255)
m = Image.fromarray(np.minimum(np.asarray(m), np.asarray(corner)))
ImageDraw.Draw(m).rounded_rectangle([v * SS for v in NOTCH], 6 * SS, fill=0)   # notch stays as photographed
warped = warped.resize(scene.size, Image.LANCZOS); m = m.resize(scene.size, Image.LANCZOS)
out = Image.composite(warped, scene, m)

# Behance cover shape: full height, trimmed evenly at the sides (also drops the rounded card edge)
w = round(scene.height * 808 / 632); x0 = (scene.width - w) // 2
out = out.crop((x0, 0, x0 + w, scene.height))
out.resize((1616, 1264), Image.LANCZOS).save(sys.argv[1])
out.resize((808, 632), Image.LANCZOS).save(sys.argv[1].replace('.png', '-808.png'))
