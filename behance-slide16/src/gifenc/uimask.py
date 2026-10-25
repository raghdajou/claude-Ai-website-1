# Dither mask from frames of the UI drawn alone on flat grey (?uimask): text and icon pixels are
# kept crisp (no dither), the glass box and tags get a light dither, the photo full dither.
import sys, numpy as np
from PIL import Image
from scipy import ndimage
out, W, H, glass = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4])
edge = np.zeros((H, W), np.float32); ui = np.zeros((H, W), bool)
for f in sys.argv[5:]:
    g = np.asarray(Image.open(f).convert('RGB').resize((W, H), Image.LANCZOS)).astype(np.float32)
    edge = np.maximum(edge, np.abs(g - ndimage.gaussian_filter(g, (1.2, 1.2, 0))).max(-1))
    ui |= np.abs(g - 128).max(-1) > 6                       # anything that is not the flat grey: box, tags, text
crisp = ndimage.binary_dilation(edge > 5, iterations=1)
ui = ndimage.binary_dilation(ui, iterations=4)
dm = np.where(ui, glass, 1.0); dm[crisp] = 0
Image.fromarray(np.round(dm * 255).astype(np.uint8)).save(out)
print(out, 'crisp %.2f%%  glass %.1f%%' % (100 * crisp.mean(), 100 * ui.mean()))
