# Three dark mockup scenes: only the screen is replaced (measured corners; the camera notch and the
# laptop base in front are kept), then cropped to the Behance cover shape (1616 x 1264).
import math, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
I = '/tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/images/'
SS = 3
SCENES = {   # file, quad TL TR BR BR BL, dashboard file, band top, cut below y, radius
    'walker': ('127.png', [(376.2, 332.3), (1327.6, 109.2), (1225.3, 774.5), (239.1, 919.2)], '126.jpg', 150, None, 0),
    'hayes':  ('128.png', [(224, 214), (1374, 214), (1403, 854), (181, 854)], '124.jpg', 420, None, 0),
    'oskar':  ('129.webp', [(258, 270), (1328, 270), (1352, 887), (242, 887)], '125.jpg', 470, 887, 14),
}
def coeffs(dst, pts):
    A, B = [], []
    for (x, y), (u, v) in zip(dst, pts):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]; B += [u, v]
    return np.linalg.solve(np.array(A, float), np.array(B, float))
for name, (f, q, df, top, cut, rad) in SCENES.items():
    scene = Image.open(I + f).convert('RGB'); W, H = scene.size; dash = Image.open(I + df).convert('RGB')
    tl, tr, br, bl = q
    sw = (math.dist(tl, tr) + math.dist(bl, br)) / 2; sh = (math.dist(tl, bl) + math.dist(tr, br)) / 2
    bh = round(dash.width * sh / sw); top = min(top, dash.height - bh)
    src = dash.crop((0, top, dash.width, top + bh)).resize((int(sw * SS), int(sh * SS)), Image.LANCZOS)
    qs = [(x * SS, y * SS) for x, y in q]
    c = coeffs(qs, [(0, 0), (src.width, 0), (src.width, src.height), (0, src.height)])
    warped = src.transform((W * SS, H * SS), Image.PERSPECTIVE, tuple(c), Image.BICUBIC).resize((W, H), Image.LANCZOS)
    m = Image.new('L', (W * SS, H * SS), 0); ImageDraw.Draw(m).polygon(qs, fill=255)
    if rad:   # rounded top corners of the laptop screen
        cm = Image.new('L', m.size, 0); x0, y0 = min(p[0] for p in qs), min(p[1] for p in qs)
        ImageDraw.Draw(cm).rounded_rectangle((x0, y0, max(p[0] for p in qs), max(p[1] for p in qs) + 200 * SS), rad * SS, fill=255)
        m = Image.fromarray(np.minimum(np.asarray(m), np.asarray(cm)))
    m = np.asarray(m.resize((W, H), Image.LANCZOS)).astype(np.float32) / 255
    a = np.asarray(scene).astype(np.float32)
    if cut: m[int(cut):] = 0
    if name == 'oskar':   # keep the camera notch: the near-black housing at the top centre
        nm = Image.new('L', (W * SS, H * SS), 0)
        ImageDraw.Draw(nm).rounded_rectangle((743 * SS, 250 * SS, 848 * SS, 287 * SS), 6 * SS, fill=255)
        m = m * (1 - np.asarray(nm.resize((W, H), Image.LANCZOS)).astype(np.float32) / 255)
    out = a * (1 - m[..., None]) + np.asarray(warped).astype(np.float32) * m[..., None]
    o = Image.fromarray(out.clip(0, 255).astype(np.uint8))
    cw = round(H * 808 / 632); x0 = (W - cw) // 2
    o = o.crop((x0, 0, x0 + cw, H)).resize((1616, 1264), Image.LANCZOS)
    o.save(f'fx-{name}.png'); o.resize((808, 632), Image.LANCZOS).save(f'fx-{name}-808.png'); print('done', name)
