# Bubbles travel the photo card: out to its corners and edges, squash on each hit, and come home.
# Each bubble is re-rendered as glass every frame (the background behind it through a soft lens,
# plus its own highlights, rim and shadow from the Figma render), so it looks right anywhere.
import numpy as np, sys, subprocess, math
from PIL import Image
from scipy import ndimage
from glass import lens_sample, fit
L, FPS, OUT_W, OUT_H = 10.0, 30, 2800, 1985
S = np.asarray(Image.open('slide.png').convert('RGB')).astype(np.float32)
C = np.asarray(Image.open('clean_full.png').convert('RGB')).astype(np.float32)
plate = np.asarray(Image.open('plate.png').convert('RGB')).astype(np.float32)
H, W = plate.shape[:2]
TA = np.load('text_full_a.npy')
P = np.asarray(Image.open('photo.png').convert('RGBA')).astype(np.float32)[..., 3] / 255
PM = np.zeros((H, W), np.float32); PM[89:89 + P.shape[0], 2155:2155 + P.shape[1]] = P   # photo card shape
# the "Why Foxlytics" card sits above the travelling bubbles
c4 = np.asarray(Image.open('card4.png').convert('RGB')).astype(np.float32); h4, w4 = c4.shape[:2]; rr = 120
a4 = np.ones((h4, w4), np.float32)
for ys, xs in [(slice(0, rr), slice(0, rr)), (slice(0, rr), slice(w4 - rr, w4)), (slice(h4 - rr, h4), slice(0, rr)), (slice(h4 - rr, h4), slice(w4 - rr, w4))]:
    a4[ys, xs] = np.clip((c4[ys, xs].min(axis=2) - 250) / 5, 0, 1)
ca2 = np.asarray(Image.fromarray((a4 * 255).astype(np.uint8)).resize((w4 // 2, h4 // 2), Image.BOX)).astype(np.float32) / 255
CM = np.zeros((H, W), np.float32); CM[1560:1560 + ca2.shape[0], 2587:2587 + ca2.shape[1]] = ca2
K, SIG = 0.9, 5

class Bubble:
    def __init__(s, cx, cy, r, keys, layer=None):
        s.cx, s.cy, s.r, s.keys = cx, cy, r, keys
        R = s.R = int(r) + 64
        O = S[cy - R:cy + R + 1, cx - R:cx + R + 1].copy(); Cb = C[cy - R:cy + R + 1, cx - R:cx + R + 1]
        if layer:   # use the bubble with the headline's letters lifted out, so they are not taken for its highlights
            img = np.asarray(Image.open(f'layer_{layer}.png').convert('RGB')).astype(np.float32)
            x0, y0 = [int(v) for v in open(f'layer_{layer}.txt').read().split()[:2]]
            ox, oy = (cx - R) - x0, (cy - R) - y0
            sub = img[max(oy, 0):oy + 2 * R + 1, max(ox, 0):ox + 2 * R + 1]
            O[max(-oy, 0):max(-oy, 0) + sub.shape[0], max(-ox, 0):max(-ox, 0) + sub.shape[1]] = sub
        G, xx, yy = lens_sample(C, cx, cy, R - 2, K, SIG); dist = np.hypot(xx, yy)   # (the helper pads the radius by 2)
        disc = np.clip((r + 1.5 - dist) / 3, 0, 1)
        a, Wc = fit(O, G, disc)
        v = a * np.where(Wc[..., 0] > 0, 1, -1)                 # signed veil: + light, - dark
        s.v = ndimage.gaussian_filter(v, 2.0)                     # smoothed so it carries no background detail
        F = np.clip(O.mean(-1) / np.maximum(Cb.mean(-1), 1), 0.4, 1.0)
        ring = ((dist > r + 1) & (dist < r + 60)).astype(np.float32)
        s.F = 1 - ndimage.gaussian_filter((1 - F) * ring, 3)       # soft shadow just outside the glass
        s.disc = disc
    def state(s, t):
        ks = s.keys; t = t % L
        for i in range(len(ks) - 1):
            (t0, x0, y0, n0), (t1, x1, y1, n1) = ks[i], ks[i + 1]
            if t0 <= t <= t1:
                f = (t - t0) / (t1 - t0)
                # leave home and arrive home softly; between walls, glide and decelerate into each hit
                e = 0.5 - 0.5 * math.cos(math.pi * f) if (i == 0 or i == len(ks) - 2) else 1 - (1 - f) ** 1.6
                x, y = x0 + (x1 - x0) * e, y0 + (y1 - y0) * e
                break
        # squash after each wall hit: a quick, springy flattening against the wall's normal
        q, ang = 0.0, 0.0
        for (tk, _, _, n) in ks:
            if n is None: continue
            dt = (t - tk) % L
            if dt < 0.9: q += 0.13 * math.exp(-dt * 6) * math.cos(dt * 18); ang = n
        return x, y, q, ang
    def draw(s, frame, t):
        x, y, q, ang = s.state(t)
        R = s.R; X0, Y0 = int(x) - R - 8, int(y) - R - 8; X1, Y1 = int(x) + R + 9, int(y) + R + 9
        yy, xx = np.mgrid[Y0:Y1, X0:X1].astype(np.float32); dx, dy = xx - x, yy - y
        ca, sa = math.cos(ang), math.sin(ang)
        u = dx * ca + dy * sa; w = -dx * sa + dy * ca               # along / across the wall normal
        u /= (1 - q); w /= (1 + 0.5 * q)
        lx = u * ca - w * sa; ly = u * sa + w * ca                 # back to the bubble's own frame
        samp = lambda A: ndimage.map_coordinates(A, [ly + R, lx + R], order=1, mode='constant', cval=0 if A is not s.F else 1)
        disc, v, F = samp(s.disc), samp(s.v), samp(s.F)
        G = np.stack([ndimage.map_coordinates(plate[..., c], [y + ly * K, x + lx * K], order=1, mode='nearest') for c in range(3)], -1)
        G = np.stack([ndimage.gaussian_filter(G[..., c], SIG) for c in range(3)], -1)
        a = np.abs(v); Wc = np.where(v > 0, 255.0, 0.0)
        glass = G * (1 - a[..., None]) + Wc[..., None] * a[..., None]
        base = frame[Y0:Y1, X0:X1]
        res = base * F[..., None]
        res = res * (1 - disc[..., None]) + glass * disc[..., None]
        pm = PM[Y0:Y1, X0:X1][..., None]
        frame[Y0:Y1, X0:X1] = res * pm + base * (1 - pm)
        return (X0, Y0, X1, Y1)

# keyframes: (time s, x, y, wall-normal angle of the hit at that key, or None)
X0c, X1c, Y0c, Y1c = 2155, 3766, 89, 2347
b1 = Bubble(2415, 702, 150, [
    (0.0, 2415, 702, None),
    (1.8, X0c + 200, Y0c + 200, math.atan2(-1, -1)),      # top-left corner
    (3.6, X0c + 200, Y1c - 200, math.atan2(1, -1)),       # bottom-left corner
    (6.0, X1c - 175, 1450, 0.0),                          # right edge
    (8.4, 2415, 702, None), (10.0, 2415, 702, None)], layer='b1')
b2 = Bubble(3300, 1218, 165, [
    (0.0, 3300, 1218, None),
    (2.2, X1c - 210, Y1c - 210, math.atan2(1, 1)),        # bottom-right corner
    (4.6, X0c + 190, 1350, math.pi),                      # left edge
    (6.8, X1c - 190, 760, 0.0),                           # right edge, upper
    (8.8, 3300, 1218, None), (10.0, 3300, 1218, None)])
# the small bubble on the card keeps its gentle bob (its earlier layer)
lay3 = Image.open('layer_b3.png'); x03, y03, cx3, cy3 = [int(v) for v in open('layer_b3.txt').read().split()]
orig = {k: (Image.open(f'layer_{k}.png'), [int(v) for v in open(f'layer_{k}.txt').read().split()]) for k in ('b1', 'b2')}

ff = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{OUT_W}x{OUT_H}',
                       '-r', str(FPS), '-i', '-', '-c:v', 'ffv1', sys.argv[1]], stdin=subprocess.PIPE)
N = int(L * FPS)
import os
PICK=[int(v) for v in os.environ.get("PICK","").split(",") if v]
for i in (PICK or range(N)):
    t = i / FPS
    fr = plate.copy(); boxes = []
    for k, b in (('b1', b1), ('b2', b2)):
        x, y, q, _ = b.state(t)
        away = math.hypot(x - b.cx, y - b.cy)
        if away < 0.5 and abs(q) < 1e-3:
            img, (x0, y0, cx, cy) = orig[k]                         # at home: exactly the Figma render
            pim = Image.fromarray(fr.clip(0, 255).astype(np.uint8)).convert('RGBA'); pim.alpha_composite(img, (x0, y0))
            fr = np.asarray(pim.convert('RGB')).astype(np.float32); boxes.append((x0, y0, x0 + img.width, y0 + img.height))
        else:
            boxes.append(b.draw(fr, t))
    # the card and the headline stay in front
    for (bx0, by0, bx1, by1) in boxes:
        sl = (slice(max(by0, 0), by1), slice(max(bx0, 0), bx1))
        cm = CM[sl][..., None]; fr[sl] = plate[sl] * cm + fr[sl] * (1 - cm)
        ta = TA[sl][..., None]; fr[sl] = 255 * ta + fr[sl] * (1 - ta)
    w = 2 * math.pi * t / L
    pim = Image.fromarray(fr.clip(0, 255).astype(np.uint8)).convert('RGBA')
    sc = 1 + 0.015 * math.sin(2 * w + 4.2 + math.pi / 2); dx = 2.5 * math.sin(w + 4.2); dy = 4 * math.sin(2 * w + 4.2)
    big = lay3.resize((round(lay3.width * sc), round(lay3.height * sc)), Image.BICUBIC)
    pim.alpha_composite(big, (round(cx3 + dx - (cx3 - x03) * sc), round(cy3 + dy - (cy3 - y03) * sc)))
    ff.stdin.write(pim.convert('RGB').resize((OUT_W, OUT_H), Image.LANCZOS).tobytes())
    if i % 50 == 0: print('frame', i, flush=True)
ff.stdin.close(); ff.wait(); print('frames', N)
