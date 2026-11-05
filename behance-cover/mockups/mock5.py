# Five separate Behance-cover mockups, each made from one reference scene with only its screen swapped
# for the Foxlytics dashboard (plus, where needed, the scene's own branding/overlay cleaned up).
# Every scene card is enlarged to 1616 x 1264 first, so the dashboard is drawn sharp at the final size.
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage
I = '/tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/images/'
W, H, SS = 1616, 1264, 2
DASH = Image.open(I + '110.jpg').convert('RGB')

def fill(a, mask, sigmas=(24, 12, 6, 3), unknown=None):
    """replace masked pixels with a smooth fill from their unmasked surroundings (never from `unknown`)"""
    known = (~mask if unknown is None else ~(mask | unknown)).astype(np.float32); out = a.copy(); f = None
    for s in sigmas:
        num = ndimage.gaussian_filter(a * known[..., None], (s, s, 0)); den = ndimage.gaussian_filter(known, s)[..., None]
        g = num / np.maximum(den, 1e-6); f = g if f is None else np.where(den > 0.3, g, f)
    return np.where(mask[..., None], f, out)

def coeffs(dst, pts):
    A, B = [], []
    for (x, y), (u, v) in zip(dst, pts):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]; B += [u, v]
    return np.linalg.solve(np.array(A, float), np.array(B, float))

def build(cfg, out):
    img = Image.open(I + cfg['src']).convert('RGB')
    a = np.asarray(img).astype(np.float32)
    if 'clean' in cfg: a = cfg['clean'](a)
    x0, y0, x1, y1 = cfg['card']
    card = Image.fromarray(a.clip(0, 255).astype(np.uint8)).crop(cfg['card'])
    k = W / card.width
    scene = card.resize((W, H), Image.LANCZOS)
    P = lambda pts: [((x - x0) * k * SS, (y - y0) * k * SS) for x, y in pts]
    quad = cfg['quad']
    if 'text' in cfg: scene = cfg['text'](scene, k, x0, y0)
    # dashboard crop in the screen's own proportions (average of opposite sides)
    tl, tr, br, bl = quad
    sw = (np.hypot(tr[0] - tl[0], tr[1] - tl[1]) + np.hypot(br[0] - bl[0], br[1] - bl[1])) / 2
    sh = (np.hypot(bl[0] - tl[0], bl[1] - tl[1]) + np.hypot(br[0] - tr[0], br[1] - tr[1])) / 2
    cw = DASH.width; ch = min(round(cw * sh / sw), DASH.height)
    top = min(cfg.get('top', 560), DASH.height - ch)
    src = DASH.crop((0, top, cw, top + ch))
    big = (W * SS, H * SS)
    c = coeffs(P(quad), [(0, 0), (src.width, 0), (src.width, src.height), (0, src.height)])
    warped = src.transform(big, Image.PERSPECTIVE, tuple(c), Image.BICUBIC)
    m = Image.new('L', big, 0); d = ImageDraw.Draw(m); d.polygon(P(quad), fill=255)
    r = cfg.get('radius', 0) * k * SS
    if r:   # round the screen's corners: clip each corner with a circle tangent to both edges (approximate)
        cm = Image.new('L', big, 0); ImageDraw.Draw(cm).polygon(P(quad), fill=255)
        cm = cm.filter(__import__('PIL.ImageFilter', fromlist=['x']).MinFilter(int(r) * 2 + 1)).filter(__import__('PIL.ImageFilter', fromlist=['x']).MaxFilter(int(r) * 2 + 1))
        m = Image.fromarray(np.minimum(np.asarray(m), np.asarray(cm)))
    d = ImageDraw.Draw(m)
    for poly in cfg.get('keep_polys', []): d.polygon(P(poly), fill=0)
    m = np.asarray(m.resize((W, H), Image.LANCZOS)).astype(np.float32) / 255
    if 'keep_color' in cfg:                                    # objects in front of the screen (flowers)
        keep = cfg['keep_color'](np.asarray(scene).astype(np.float32), k, x0, y0)
        m = m * (1 - keep)
    out_img = np.asarray(scene).astype(np.float32) * (1 - m[..., None]) + np.asarray(warped.resize((W, H), Image.LANCZOS)).astype(np.float32) * m[..., None]
    o = Image.fromarray(out_img.clip(0, 255).astype(np.uint8))
    o.save(out); o.resize((808, 632), Image.LANCZOS).save(out.replace('.png', '-808.png'))

# --- per-scene settings (all coordinates in the original screenshot's pixels) ---
def flowers_114(s, k, x0, y0):
    hsv = np.asarray(Image.fromarray(s.astype(np.uint8)).convert('HSV')).astype(np.float32)
    keep = (hsv[..., 1] > 50) & (hsv[..., 2] > 40)            # coloured petals / green stems, not the white page
    box = np.zeros(keep.shape, bool)
    bx = lambda v, o: int((v - o) * k)
    box[bx(250, y0):bx(292, y0), bx(398, x0):bx(450, x0)] = True     # the flower over the screen's lower right
    keep = ndimage.binary_dilation(keep & box, iterations=1)
    return ndimage.gaussian_filter(keep.astype(np.float32), 0.8)

def clean_115(a):
    # lift the large "MeetSync" wordmark (and its soft shadow) off the light card: the card there is a
    # gentle gradient, so rebuild the band above and beside the monitor from the clean rows above the letters
    ref = ndimage.gaussian_filter1d(a[42:50, :, :].mean(0), 6, axis=0)          # per-column card colour, just above the letters
    mon = Image.new('L', (a.shape[1], a.shape[0]), 0)
    ImageDraw.Draw(mon).polygon([(50, 123), (599, 127), (716, 425), (50, 425)], fill=255)
    mon = np.asarray(mon).astype(bool)
    out = a.copy()
    for y in range(36, 175):
        row = ~mon[y]; row[:56] = False
        t = np.clip((y - 160) / 15, 0, 1) + np.clip((42 - y) / 6, 0, 1)          # blend into the photo above y 42 and below y 160
        out[y, row] = ref[row] * (1 - t) + a[y, row] * t
    return out

def text_115(scene, k, x0, y0):
    # "Foxlytics" in the same place, size and faint white, behind the monitor
    font = ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-Bold.otf', int(112 * k))
    lay = Image.new('RGBA', scene.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.text(((90 - x0) * k, (136 - y0) * k), 'Foxlytics', font=font, fill=(251, 252, 253, 255), anchor='ls')
    mon = Image.new('L', scene.size, 255)
    ImageDraw.Draw(mon).polygon([((x - x0) * k, (y - y0) * k) for x, y in [(40, 124), (598, 127.5), (712, 418), (40, 420)]], fill=0)
    lay.putalpha(Image.fromarray(np.minimum(np.asarray(lay.getchannel('A')), np.asarray(mon))))
    s = scene.convert('RGBA'); s.alpha_composite(lay); return s.convert('RGB')

def clean_116a(a):
    # the grey Behance hover label across the monitor: fill it from the dark scene around it
    mask = np.zeros(a.shape[:2], bool); mask[383:425, 22:505] = True
    # outside the screen (left of x 104) the label sits on the ribbed stand: patch it with ribbed stand
    # from below, at the offset where the ribs line up best with the rows just above the label
    y0, y1, x0, x1 = 383, 425, 22, 104
    best = None
    for dy in range(42, 90):
        for dx in range(-40, 41):
            if x0 + dx < 22: continue
            e = np.abs(a[372:383, x0:x1] - a[372 + dy:383 + dy, x0 + dx:x1 + dx]).mean()
            if best is None or e < best[0]: best = (e, dx, dy)
    _, dx, dy = best
    out = a.copy(); out[y0:y1, x0:x1] = a[y0 + dy:y1 + dy, x0 + dx:x1 + dx]
    # the monitor's black frame edge runs nearly straight down here: continue it from the row above the label
    fx0 = 88                                                          # the black frame, x 88..97
    for yy in range(y0, y1):
        t = (yy - y0) / (y1 - y0)
        out[yy, fx0:x1] = a[y0 - 1, fx0:x1] * (1 - t) + a[y1, fx0:x1] * t
    rest = np.zeros(a.shape[:2], bool); rest[y0:y1, x1:505] = True     # the rest lies on the screen, which is replaced
    return fill(out, rest, (10, 5, 3))

SCENES = {
    'flowers':  dict(src='114.webp', card=(12, 0, 672, 516), quad=[(270, 155.5), (433.5, 177.5), (427, 278), (264, 254)],
                     radius=2, keep_color=flowers_114),
    'meetsync': dict(src='115.png', card=(56, 27, 716, 543), quad=[(56, 125.5), (596, 129.5), (707.5, 416), (56, 417)],
                     top=960),
    'dark-stand': dict(src='116.webp', card=(22, 49, 682, 565), quad=[(94, 138), (593, 210), (589, 533), (102, 433)],
                     clean=clean_116a),
    'tablet':   dict(src='116.webp', card=(730, 49, 1390, 565), quad=[(822, 179), (1298, 177), (1323, 441), (797, 441)], radius=9),
    'concrete': dict(src='117.png', card=(18, 13, 678, 529), quad=[(84.5, 97), (516, 150), (584, 421), (140, 426)], radius=5,
                     keep_polys=[[(284, 115), (338, 122), (334, 136.5), (288.5, 131.5)],
                                 [(110, 433), (210, 427.5), (295, 417.5), (370, 405), (440, 407.5), (580, 421), (700, 438), (700, 545), (110, 545)]]),
}
for name in (sys.argv[1:] or SCENES):
    build(SCENES[name], f'foxlytics-{name}.png'); print('done', name)
