# Remove the "ena" watermark from three mockup scenes: the box around it is refilled from the plain
# backdrop on all four sides (bilinear Coons patch), which suits these smooth studio gradients.
import numpy as np
from PIL import Image
I = '/tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/images/'
BOX = {'133.png': (30, 25, 180, 110), '134.png': (30, 25, 180, 110), '135.webp': (45, 40, 205, 128)}
for f, (l, t, r, b) in BOX.items():
    a = np.asarray(Image.open(I + f).convert('RGB')).astype(np.float32)
    L, R = a[t:b, l - 1], a[t:b, r]            # columns just outside, rows just outside
    T, B = a[t - 1, l:r], a[b, l:r]
    h, w = b - t, r - l
    u = (np.arange(w) + 1) / (w + 1); v = (np.arange(h) + 1) / (h + 1)
    U, V = u[None, :, None], v[:, None, None]
    lr = L[:, None] * (1 - U) + R[:, None] * U
    tb = T[None] * (1 - V) + B[None] * V
    c00, c10, c01, c11 = a[t - 1, l - 1], a[t - 1, r], a[b, l - 1], a[b, r]
    corner = c00 * (1 - U) * (1 - V) + c10 * U * (1 - V) + c01 * (1 - U) * V + c11 * U * V
    a[t:b, l:r] = lr + tb - corner
    Image.fromarray(a.clip(0, 255).round().astype(np.uint8)).save(I + f.split('.')[0] + 'c.png')
    print('clean', f)
