# Cuts the card images for each dashboard and version of the gallery slide.
#   split: the chosen region of the dashboard cut into three vertical strips (left / middle / right)
#   focus: the whole dashboard in the centre card, two zoomed sections on the side cards
import sys
from PIL import Image, ImageFilter
src_dir, out = sys.argv[1], sys.argv[2]
CENTER, SIDE = 415 / 500, 308 / 341          # card aspect ratios (w / h) from the Framer component
OUT_W = 960                                    # card image width in px (covers a 2x export)
BG = (249, 249, 249)                           # the dashboards' page colour, used for padding

def crop(im, cx, cy, w, aspect):
    h = w / aspect
    box = (int(cx - w / 2), int(cy - h / 2), int(cx + w / 2), int(cy + h / 2))
    canvas = Image.new('RGB', (box[2] - box[0], box[3] - box[1]), BG)
    canvas.paste(im.crop((max(0, box[0]), max(0, box[1]), min(im.width, box[2]), min(im.height, box[3]))),
                 (max(0, -box[0]), max(0, -box[1])))
    return canvas

def contain(im, aspect, pad=0.06):
    w = int(im.width * (1 + pad)); h = int(w / aspect)
    if h < im.height * (1 + pad): h = int(im.height * (1 + pad)); w = int(h * aspect)
    c = Image.new('RGB', (w, h), BG); c.paste(im, ((w - im.width) // 2, (h - im.height) // 2)); return c

def save(im, name, aspect):
    im = im.resize((OUT_W, int(OUT_W / aspect)), Image.LANCZOS).filter(ImageFilter.UnsharpMask(0.8, 40, 2))
    im.save(f'{out}/{name}.jpg', quality=93)

DASH = {
    # region for "split" (x0, y0, x1) + focus crops (cx, cy, width) for the side cards
    'payroll':   {'file': '65.jpg', 'split': (240, 300, 1890), 'left': (600, 1390, 700), 'right': (1480, 1420, 800)},
    'analytics': {'file': '66.jpg', 'split': (210, 540, 1720), 'left': (430, 660, 480), 'right': (1350, 1380, 700)},
    'overview':  {'file': '67.jpg', 'split': (20, 270, 850), 'left': (280, 1560, 500), 'right': (700, 1560, 300), 'center_top': True},
}
for name, d in DASH.items():
    im = Image.open(f"{src_dir}/{d['file']}").convert('RGB')
    x0, y0, x1 = d['split']; sw = (x1 - x0) / 3
    for i, part in enumerate(['left', 'center', 'right']):
        cx = x0 + sw * (i + 0.5)
        save(crop(im, cx, y0 + sw / CENTER / 2, sw, CENTER), f'{name}-split-{part}', CENTER)
    if d.get('center_top'):
        save(crop(im, im.width / 2, im.width / CENTER / 2, im.width, CENTER), f'{name}-focus-center', CENTER)
    else:
        save(contain(im, CENTER), f'{name}-focus-center', CENTER)
    for part in ['left', 'right']:
        cx, cy, w = d[part]; save(crop(im, cx, cy, w, SIDE), f'{name}-focus-{part}', SIDE)
print('done')
