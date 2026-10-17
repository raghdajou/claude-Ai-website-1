import sys, numpy as np
from PIL import Image, ImageDraw, ImageFilter
src, out, quad = sys.argv[1], sys.argv[2], np.array(eval(sys.argv[3]), float)
top = int(sys.argv[4]) if len(sys.argv) > 4 else 18
S = 4
im = Image.open(src).convert('RGB'); im = im.resize((im.width * S, im.height * S), Image.LANCZOS)
q = quad * S
# Screen aspect from the quad's average edge lengths; crop the dashboard top to match.
w = (np.linalg.norm(q[1] - q[0]) + np.linalg.norm(q[2] - q[3])) / 2
h = (np.linalg.norm(q[3] - q[0]) + np.linalg.norm(q[2] - q[1])) / 2
dash = Image.open('../cover/dashboard.jpg').convert('RGB')
ch = min(int(871 * h / w), 2000)
dash = dash.crop((0, top, 871, top + ch))
dash = dash.resize((871 * 3, ch * 3), Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=2, percent=70, threshold=2))
dw, dh = dash.size
A, b = [], []
for (x, y), (u, v) in zip(q, [(0, 0), (dw, 0), (dw, dh), (0, dh)]):
    A += [[x, y, 1, 0, 0, 0, -u*x, -u*y], [0, 0, 0, x, y, 1, -v*x, -v*y]]; b += [u, v]
c = np.linalg.solve(np.array(A, float), np.array(b, float))
screen = dash.transform(im.size, Image.PERSPECTIVE, c, Image.BICUBIC)
m = Image.new('L', im.size, 0); ImageDraw.Draw(m).polygon([tuple(p) for p in q], fill=255)
m = m.filter(ImageFilter.GaussianBlur(1))
im.paste(screen, (0, 0), m)
# faint top-left glass sheen
arr = np.asarray(im).astype(float); mm = np.asarray(m).astype(float)[..., None] / 255
yy, xx = np.mgrid[0:im.height, 0:im.width]
sheen = np.clip(0.06 - ((xx + yy) / (im.width + im.height)) * 0.1, 0, 0.06)[..., None]
arr = arr * (1 - sheen * mm) + 255 * sheen * mm
Image.fromarray(arr.clip(0, 255).astype(np.uint8)).save(out, optimize=True)
print(out, im.size)
