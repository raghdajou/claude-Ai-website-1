# Three more mockups (floating panel over flowers, close-up angled monitor, monitor seen from below):
# only the screen is replaced. Screen edges were line-fitted (<1 px); corners outside the frame are
# where those lines meet. The two angled monitors are shown in perspective, so their screen is taken
# as 16:9 rather than measured from the picture.
import itertools, math, numpy as np
from PIL import Image, ImageDraw
I = '/tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/images/'
SS = 3
def meet(a, b):   # a: x = a0*y + a1 (near-vertical), b: y = b0*x + b1
    y = (b[0] * a[1] + b[1]) / (1 - b[0] * a[0]); return (a[0] * y + a[1], y)
l150, t150, r150, b150 = (-0.181417, 283.457), (1.071199, -877.458), (0.109240, 1259.763), (0.560775, 519.545)
l151, r151 = (-0.186207, 139.897), (0.186207, 1458.276)
SCENES = {
    'mxm':   ('149.webp', [(80, 145), (1518.5, 145), (1518.5, 1054.5), (80, 1054.5)], None),
    'tilt':  ('150.webp', [meet(l150, t150), meet(r150, t150), meet(r150, b150), meet(l150, b150)], 16 / 9),
    'below': ('151.webp', [meet(l151, (0, 188)), meet(r151, (0, 188)), meet(r151, (0, 868)), meet(l151, (0, 868))], 16 / 9),
}
SCREENS = {'brand': ('141.jpg', None), 'payroll': ('130.jpg', 420), 'projects': ('131.jpg', 560)}
FOCUS = (900, 640)
def coeffs(dst, pts):
    A, B = [], []
    for (x, y), (u, v) in zip(dst, pts):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]; B += [u, v]
    return np.linalg.solve(np.array(A, float), np.array(B, float))
for (name, (f, q, asp)), (scr, (df, top)) in itertools.product(SCENES.items(), SCREENS.items()):
    scene = Image.open(I + f).convert('RGB'); W, H = scene.size; dash = Image.open(I + df).convert('RGB')
    tl, tr, br, bl = q
    sw = (math.dist(tl, tr) + math.dist(bl, br)) / 2; sh = (math.dist(tl, bl) + math.dist(tr, br)) / 2
    r = asp or sw / sh
    if top is None:   # brand photo: cover-fit around the wordmark and face
        if dash.width / dash.height > r:
            cw = round(dash.height * r); x0 = int(np.clip(FOCUS[0] - cw / 2, 0, dash.width - cw)); box = (x0, 0, x0 + cw, dash.height)
        else:
            ch = round(dash.width / r); y0 = int(np.clip(FOCUS[1] - ch / 2, 0, dash.height - ch)); box = (0, y0, dash.width, y0 + ch)
    else:             # dashboard: full width, a band starting at `top`
        if name == 'mxm' and scr == 'payroll': top = 405   # taller band here: stop above the next section's heading
        bh = round(dash.width / r); t = min(top, dash.height - bh); box = (0, t, dash.width, t + bh)
    sh_px = 2400; src = dash.crop(box).resize((round(sh_px * r), sh_px), Image.LANCZOS)
    qs = [(x * SS, y * SS) for x, y in q]
    c = coeffs(qs, [(0, 0), (src.width, 0), (src.width, src.height), (0, src.height)])
    warped = src.transform((W * SS, H * SS), Image.PERSPECTIVE, tuple(c), Image.BICUBIC).resize((W, H), Image.LANCZOS)
    m = Image.new('L', (W * SS, H * SS), 0); ImageDraw.Draw(m).polygon(qs, fill=255)
    m = np.asarray(m.resize((W, H), Image.LANCZOS)).astype(np.float32)[..., None] / 255
    out = np.asarray(scene).astype(np.float32) * (1 - m) + np.asarray(warped).astype(np.float32) * m
    o = Image.fromarray(out.clip(0, 255).astype(np.uint8))
    cw = round(H * 808 / 632); x0 = (W - cw) // 2
    o = o.crop((x0, 0, x0 + cw, H)).resize((1616, 1264), Image.LANCZOS)
    o.save(f'n6-{name}-{scr}.png'); o.resize((808, 632), Image.LANCZOS).save(f'n6-{name}-{scr}-808.png'); print('done', name, scr, [tuple(round(v, 1) for v in p) for p in q] if scr == 'brand' else '')
