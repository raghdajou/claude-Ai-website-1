# Four more: monitor with a big name (jackson), laptop on a green sofa (sofa), laptop on a purple
# chair (chair), flat browser card (redcow). Only the screen changes; laptop notches and the black
# rounded screen corners are kept from the photo.
import itertools, math, numpy as np
from PIL import Image, ImageDraw
I = '/tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/images/'
SS = 3
SCENES = {   # file, quad TL TR BR BL (edge-fitted), aspect (None = from quad), notch window, dashboard band top override
    'jackson': ('156.webp', [(420.67, 257.7), (1598.6, 246.5), (1580.93, 1000.08), (401.92, 981.02)], 16 / 9, None, None),
    'sofa':    ('157.webp', [(418.85, 307.08), (1082.24, 234.68), (1134.43, 679.55), (473.33, 765.27)], 1.547, (700, 240, 815, 300), None),
    'chair':   ('158.webp', [(578.37, 241.03), (1242.39, 297.14), (1242.51, 854.07), (578.63, 748.75)], 1.547, (845, 250, 945, 300), None),
    'redcow':  ('159.webp', [(200, 300), (1400, 300), (1400, 1200), (200, 1200)], None, None, 0),
}
SCREENS = {'brand': ('141.jpg', None), 'payroll': ('130.jpg', 420), 'projects': ('131.jpg', 560)}
def coeffs(dst, pts):
    A, B = [], []
    for (x, y), (u, v) in zip(dst, pts):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]; B += [u, v]
    return np.linalg.solve(np.array(A, float), np.array(B, float))
for (name, (f, q, asp, notch, top_o)), (scr, (df, top)) in itertools.product(SCENES.items(), SCREENS.items()):
    scene = Image.open(I + f).convert('RGB'); W, H = scene.size; dash = Image.open(I + df).convert('RGB')
    tl, tr, br, bl = q
    sw = (math.dist(tl, tr) + math.dist(bl, br)) / 2; sh = (math.dist(tl, bl) + math.dist(tr, br)) / 2
    r = asp or sw / sh
    if top is None:
        if dash.width / dash.height > r:
            cw = round(dash.height * r); x0 = int(np.clip(900 - cw / 2, 0, dash.width - cw)); box = (x0, 0, x0 + cw, dash.height)
        else:
            ch = round(dash.width / r); y0 = int(np.clip(640 - ch / 2, 0, dash.height - ch)); box = (0, y0, dash.width, y0 + ch)
    else:
        t0 = top if top_o is None else top_o
        if scr == 'payroll' and asp == 1.547: t0 = 395   # taller laptop band: stop above the next section's heading
        bh = round(dash.width / r); t = min(t0, dash.height - bh); box = (0, t, dash.width, t + bh)
    src = dash.crop(box).resize((round(2400 * r), 2400), Image.LANCZOS)
    qs = [(x * SS, y * SS) for x, y in q]
    c = coeffs(qs, [(0, 0), (src.width, 0), (src.width, src.height), (0, src.height)])
    warped = src.transform((W * SS, H * SS), Image.PERSPECTIVE, tuple(c), Image.BICUBIC).resize((W, H), Image.LANCZOS)
    m = Image.new('L', (W * SS, H * SS), 0)
    if name == 'redcow':
        ImageDraw.Draw(m).rounded_rectangle((200 * SS, 300 * SS, 1400 * SS, 1260 * SS), 4 * SS, fill=255)
    else:
        ImageDraw.Draw(m).polygon(qs, fill=255)
    m = np.asarray(m.resize((W, H), Image.LANCZOS)).astype(np.float32) / 255
    g = np.asarray(scene.convert('L')).astype(np.float32)
    if notch:   # laptop: rounded screen corners and the camera notch, drawn in screen space and warped
        sm = Image.new('L', src.size, 0); d = ImageDraw.Draw(sm)
        d.rounded_rectangle((0, 0, src.width - 1, src.height - 1), 55, fill=255)
        d.rectangle((0, src.height // 2, src.width, src.height), fill=255)   # MacBook screens: only the top corners are round
        nw = 392 / 3713 * src.width; cx = src.width / 2
        d.rounded_rectangle((cx - nw / 2, -60, cx + nw / 2, 66), 22, fill=0)
        sm = sm.transform((W * SS, H * SS), Image.PERSPECTIVE, tuple(c), Image.BICUBIC, fillcolor=0)
        m = m * np.asarray(sm.resize((W, H), Image.LANCZOS)).astype(np.float32) / 255
    m = m[..., None]
    out = np.asarray(scene).astype(np.float32) * (1 - m) + np.asarray(warped).astype(np.float32) * m
    o = Image.fromarray(out.clip(0, 255).astype(np.uint8))
    cw = round(H * 808 / 632); x0 = (W - cw) // 2
    o = o.crop((x0, 0, x0 + cw, H)).resize((1616, 1264), Image.LANCZOS)
    o.save(f's8-{name}-{scr}.png'); o.resize((808, 632), Image.LANCZOS).save(f's8-{name}-{scr}-808.png'); print('done', name, scr)
