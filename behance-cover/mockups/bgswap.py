# The "Luca" display (with the Foxlytics screen) lifted off its plain grey studio and set on new photo
# backgrounds. The device keeps its own pixels; its floor shadow is carried over as a darkening map.
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage
I = '/tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/images/'
BGS = {'blue': '136.jpg', 'white-flower': '137.jpg', 'anemone': '138.jpg', 'haze': '139.jpg', 'yellow': '140.jpg'}
W, H = 1616, 1264
for scr in ('payroll', 'projects'):
    src = Image.open(f'lt-luca-{scr}.png').convert('RGB'); a = np.asarray(src).astype(np.float32)
    g = a.mean(-1)
    # studio backdrop estimate: heavy blur of the image with the device removed
    rough = np.abs(g - np.median(g)) > 10
    base = a.copy(); base[rough] = np.median(a.reshape(-1, 3), 0)
    bgest = ndimage.gaussian_filter(base, (60, 60, 0))
    diff = np.abs(a - bgest).max(-1)
    dev = ndimage.binary_fill_holes(diff > 12)
    dev[1056:] = False
    # the stand foot, row by row: fill between the outermost stand pixels (x 660..960), so the soft
    # floor shadow beside the plate stays out; the last rows reuse row 1096's span (shadow under it)
    span = None
    for y in range(1056, 1104):
        if y <= 1096:
            xs_ = np.nonzero(np.abs(g[y, 660:960] - 232) > 8)[0]
            if len(xs_): span = (660 + xs_.min(), 660 + xs_.max())
        if span: dev[y, span[0]:span[1] + 1] = True
    lab, n = ndimage.label(dev); sizes = ndimage.sum(dev, lab, range(1, n + 1))
    dev = lab == (np.argmax(sizes) + 1)                       # the display + stand (drops the corner logo)
    dev = ndimage.binary_closing(dev, iterations=3)
    alpha = ndimage.gaussian_filter(dev.astype(np.float32), 0.7)[..., None]
    # floor shadow: the thin contact shadow under the plate, taken from the studio floor as a darkening map
    ratio = np.clip(g / 232.0, 0.35, 1.0)
    shadow = np.ones((H, W), np.float32)
    zone = np.zeros((H, W), bool); zone[1097:1118, 420:1200] = True
    shadow[zone & ~dev] = ratio[zone & ~dev]
    # fade the shadow out toward its ends so it reads as contact, not a stripe across the picture
    xx = np.arange(W); fall = np.clip(1 - (np.abs(xx - 808) - 150) / 170, 0, 1) ** 1.5
    shadow = 1 - (1 - shadow) * fall[None, :]
    shadow = ndimage.gaussian_filter(shadow, 1.5)[..., None]
    for name, f in BGS.items():
        bg = Image.open(I + f).convert('RGB')
        k = max(W / bg.width, H / bg.height); bg = bg.resize((round(bg.width * k), round(bg.height * k)), Image.LANCZOS)
        bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
        b = np.asarray(bg).astype(np.float32) * shadow
        out = b * (1 - alpha) + a * alpha
        o = Image.fromarray(out.clip(0, 255).astype(np.uint8))
        o.save(f'bgs-{name}-{scr}.png'); o.resize((808, 632), Image.LANCZOS).save(f'bgs-{name}-{scr}-808.png')
    print('done', scr)
