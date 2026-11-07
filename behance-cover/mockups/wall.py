# Clean the streaked blue wallpaper of the "Masen James" desktop: icons, labels, top bar, window and
# dock are masked and each column is rebuilt by interpolating between unmasked rows (the streaks are
# vertical, so this keeps them), then a light vertical blur hides the seams.
import numpy as np
from PIL import Image
from scipy import ndimage
I = '/tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/images/'
a = np.asarray(Image.open(I + '193.webp').convert('RGB')).astype(np.float32); H, W = a.shape[:2]
m = np.zeros((H, W), bool); m[:70] = True
for l, t, r, b in [(60, 185, 230, 385), (455, 140, 620, 345), (1050, 145, 1215, 350), (1535, 110, 1705, 310),
                   (1815, 330, 1980, 530), (1535, 460, 1700, 665), (120, 760, 275, 965), (1725, 795, 1890, 1000),
                   (240, 405, 1490, 1170), (1200, 1130, 1355, 1250), (290, 1170, 455, 1375), (740, 1200, 1260, 1440),
                   (1735, 1160, 1900, 1360)]:
    m[t:b, l:r] = True
out = a.copy(); ys = np.arange(H)
for x in range(W):
    ok = ~m[:, x]
    for c in range(3): out[m[:, x], x, c] = np.interp(ys[m[:, x]], ys[ok], a[ok, x, c])
sm = ndimage.gaussian_filter(out, (25, 2, 0)); mm = ndimage.gaussian_filter(m.astype(np.float32), 6)[..., None]
out = out * (1 - mm) + sm * mm
Image.fromarray(out.clip(0, 255).astype(np.uint8)).save('wall193.png'); print('ok')
