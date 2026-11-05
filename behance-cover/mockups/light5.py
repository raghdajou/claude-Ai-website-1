# Four light mockup scenes (front monitor, angled monitor, front display, laptop on a rock) with the
# Payroll and Projects screens. Only the screen is replaced; the laptop's notch and the base in front
# of its lower screen are kept; cropped to the Behance cover shape (1616 x 1264).
import math, itertools, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
I = '/tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/images/'
SS = 3
SCENES = {   # file, screen quad TL TR BR BL (measured), corner radius
    'vance':  ('132.webp', [(116, 188), (1884, 188), (1884, 1186), (116, 1186)], 0),
    'barret': ('133c.png', [(288, 196), (1369.5, 207), (1369.5, 902), (289, 927)], 6),
    'luca':   ('134c.png', [(289, 197), (1311, 197), (1311, 774), (289, 774)], 0),
    'objects':('135c.png', [(711, 278), (1647, 211), (1637, 881), (693, 948)], 10),
}
SCREENS = {'brand': ('141.jpg', None)}   # the Foxlytics brand photo, cover-fitted around the wordmark and face
FOCUS = (900, 640)
def coeffs(dst, pts):
    A, B = [], []
    for (x, y), (u, v) in zip(dst, pts):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]; B += [u, v]
    return np.linalg.solve(np.array(A, float), np.array(B, float))
for (name, (f, q, rad)), (scr, (df, top)) in itertools.product(SCENES.items(), SCREENS.items()):
    scene = Image.open(I + f).convert('RGB'); W, H = scene.size; dash = Image.open(I + df).convert('RGB')
    tl, tr, br, bl = q
    sw = (math.dist(tl, tr) + math.dist(bl, br)) / 2; sh = (math.dist(tl, bl) + math.dist(tr, br)) / 2
    r = sw / sh
    if dash.width / dash.height > r:   # photo wider than the screen: trim the sides around the focus
        cw = round(dash.height * r); x0 = int(np.clip(FOCUS[0] - cw / 2, 0, dash.width - cw)); box = (x0, 0, x0 + cw, dash.height)
    else:
        ch = round(dash.width / r); y0 = int(np.clip(FOCUS[1] - ch / 2, 0, dash.height - ch)); box = (0, y0, dash.width, y0 + ch)
    src = dash.crop(box).resize((int(sw * SS), int(sh * SS)), Image.LANCZOS)
    qs = [(x * SS, y * SS) for x, y in q]
    c = coeffs(qs, [(0, 0), (src.width, 0), (src.width, src.height), (0, src.height)])
    warped = src.transform((W * SS, H * SS), Image.PERSPECTIVE, tuple(c), Image.BICUBIC).resize((W, H), Image.LANCZOS)
    m = Image.new('L', (W * SS, H * SS), 0); ImageDraw.Draw(m).polygon(qs, fill=255)
    m = np.asarray(m.resize((W, H), Image.LANCZOS)).astype(np.float32) / 255
    a = np.asarray(scene).astype(np.float32); g = a.mean(-1)
    if rad:   # rounded screen corners: keep the photo's own dark bezel just inside each corner
        for (cx, cy) in q:
            yy, xx = np.ogrid[:H, :W]; near = (np.abs(xx - cx) < rad * 1.6) & (np.abs(yy - cy) < rad * 1.6)
            m[near & (g < 90)] = 0
    if name == 'objects':
        notch = np.zeros((H, W), bool); notch[205:275, 1105:1240] = True
        m[notch & (g < 200)] = 0                                    # camera notch
        low = np.zeros((H, W), bool); low[812:, :] = True           # lower screen: only where the photo shows screen white
        # screen white below y 812 that is still joined to the screen above (the rock under the base is not)
        lab, _ = ndimage.label((g > 185) & (m > 0.5))
        ids = np.unique(lab[790:812][lab[790:812] > 0])
        keep = ndimage.binary_closing(np.isin(lab, ids), iterations=4)
        m[low & ~keep] = 0
    out = a * (1 - m[..., None]) + np.asarray(warped).astype(np.float32) * m[..., None]
    o = Image.fromarray(out.clip(0, 255).astype(np.uint8))
    cw = round(H * 808 / 632); x0 = (W - cw) // 2
    o = o.crop((x0, 0, x0 + cw, H)).resize((1616, 1264), Image.LANCZOS)
    o.save(f'lt-{name}-{scr}.png'); o.resize((808, 632), Image.LANCZOS).save(f'lt-{name}-{scr}-808.png'); print('done', name, scr)
