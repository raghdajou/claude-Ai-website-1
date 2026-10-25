# Five glass bubbles glide around the photo card without ever stopping: each runs a periodic
# billiard path (paths.py), squashes softly on every wall hit, and the 16 s loop closes exactly
# where it began. The three Figma bubbles start from their own positions; two new ones, a medium
# and a small, use the same glass. A bubble that passes in front of another sees it through its lens.
import numpy as np, sys, subprocess, math, json
from PIL import Image
from scipy import ndimage
from glass import lens_sample, fit
from paths import Path, L
FPS, OUT_W, OUT_H = 50, 2800, 1985
S = np.asarray(Image.open('slide.png').convert('RGB')).astype(np.float32)
C = np.asarray(Image.open('clean_full.png').convert('RGB')).astype(np.float32)
plate = np.asarray(Image.open('plate.png').convert('RGB')).astype(np.float32)
H, W = plate.shape[:2]
TA = np.load('text_full_a.npy')
P = np.asarray(Image.open('photo.png').convert('RGBA')).astype(np.float32)[..., 3] / 255
PM = np.zeros((H, W), np.float32); PM[89:89 + P.shape[0], 2155:2155 + P.shape[1]] = P   # photo card shape
# the "Why Foxlytics" card sits above the bubbles behind it
c4 = np.asarray(Image.open('card4.png').convert('RGB')).astype(np.float32); h4, w4 = c4.shape[:2]; rr = 120
a4 = np.ones((h4, w4), np.float32)
for ys, xs in [(slice(0, rr), slice(0, rr)), (slice(0, rr), slice(w4 - rr, w4)), (slice(h4 - rr, h4), slice(0, rr)), (slice(h4 - rr, h4), slice(w4 - rr, w4))]:
    a4[ys, xs] = np.clip((c4[ys, xs].min(axis=2) - 250) / 5, 0, 1)
ca2 = np.asarray(Image.fromarray((a4 * 255).astype(np.uint8)).resize((w4 // 2, h4 // 2), Image.BOX)).astype(np.float32) / 255
CM = np.zeros((H, W), np.float32); CM[1560:1560 + ca2.shape[0], 2587:2587 + ca2.shape[1]] = ca2
K, SIG = 0.9, 5

class Glass:
    """highlights, rim and shadow of one Figma bubble, fitted against the clean background"""
    def __init__(s, cx, cy, r, layer=None):
        s.r = r; R = s.R = int(r) + 64
        O = S[cy - R:cy + R + 1, cx - R:cx + R + 1].copy(); Cb = C[cy - R:cy + R + 1, cx - R:cx + R + 1]
        if layer:   # the bubble with the headline's letters lifted out, so they are not taken for its highlights
            img = np.asarray(Image.open(f'layer_{layer}.png').convert('RGB')).astype(np.float32)
            x0, y0 = [int(v) for v in open(f'layer_{layer}.txt').read().split()[:2]]
            ox, oy = (cx - R) - x0, (cy - R) - y0
            sub = img[max(oy, 0):oy + 2 * R + 1, max(ox, 0):ox + 2 * R + 1]
            O[max(-oy, 0):max(-oy, 0) + sub.shape[0], max(-ox, 0):max(-ox, 0) + sub.shape[1]] = sub
        G, xx, yy = lens_sample(C, cx, cy, R - 2, K, SIG); dist = np.hypot(xx, yy)
        disc = np.clip((r + 1.5 - dist) / 3, 0, 1)
        a, Wc = fit(O, G, disc)
        s.v = ndimage.gaussian_filter(a * np.where(Wc[..., 0] > 0, 1, -1), 2.0)   # signed veil: + light, - dark
        F = np.clip(O.mean(-1) / np.maximum(Cb.mean(-1), 1), 0.4, 1.0)
        ring = ((dist > r + 1) & (dist < r + 60)).astype(np.float32)
        s.F = 1 - ndimage.gaussian_filter((1 - F) * ring, 3)                       # soft shadow just outside
        s.disc = disc

class Bubble:
    def __init__(s, glass, path, r):
        s.g, s.p, s.r = glass, path, r; s.k = r / glass.r                          # scale of the glass model
        s.hits = path.hits()
    def state(s, t):
        x, y = s.p.pos(t % L)
        # squash after each wall hit: a quick, springy flattening against the wall's normal
        q, ang = 0.0, 0.0
        for (tk, n) in s.hits:
            dt = (t - tk) % L
            if dt < 0.9: q += 0.11 * math.exp(-dt * 6) * math.cos(dt * 18); ang = n
        return x, y, q, ang
    def draw(s, frame, t):
        x, y, q, ang = s.state(t); g = s.g
        R = int(s.r) + 64; X0, Y0 = max(int(x) - R - 8, 0), max(int(y) - R - 8, 0); X1, Y1 = int(x) + R + 9, int(y) + R + 9
        yy, xx = np.mgrid[Y0:Y1, X0:X1].astype(np.float32); dx, dy = xx - x, yy - y
        ca, sa = math.cos(ang), math.sin(ang)
        u = dx * ca + dy * sa; w = -dx * sa + dy * ca                 # along / across the wall normal
        u /= (1 - q); w /= (1 + 0.5 * q)
        lx = u * ca - w * sa; ly = u * sa + w * ca                   # back to the bubble's own frame
        mx, my = lx / s.k + g.R, ly / s.k + g.R
        samp = lambda A, cv: ndimage.map_coordinates(A, [my, mx], order=1, mode='constant', cval=cv)
        disc, v, F = samp(g.disc, 0), samp(g.v, 0), samp(g.F, 1)
        src = frame.copy() if s.see_others else plate                 # what lies behind it right now
        G = np.stack([ndimage.map_coordinates(src[..., c], [y + ly * K, x + lx * K], order=1, mode='nearest') for c in range(3)], -1)
        G = np.stack([ndimage.gaussian_filter(G[..., c], SIG * s.k ** 0.5) for c in range(3)], -1)
        a = np.abs(v); Wc = np.where(v > 0, 255.0, 0.0)
        glass = G * (1 - a[..., None]) + Wc[..., None] * a[..., None]
        base = frame[Y0:Y1, X0:X1]
        res = base * F[..., None]
        res = res * (1 - disc[..., None]) + glass * disc[..., None]
        pm = PM[Y0:Y1, X0:X1][..., None]
        frame[Y0:Y1, X0:X1] = res * pm + base * (1 - pm)
        return (X0, Y0, X1, Y1)

g1 = Glass(2415, 702, 150, layer='b1'); g2 = Glass(3300, 1218, 165)
cfg = {row[0]: row for row in json.load(open('paths.json'))}
def mk(name, glass):
    _, x, y, r, nx, ny, dx, dy = cfg[name]
    b = Bubble(glass, Path(x, y, r, nx, ny, dx, dy), r); b.see_others = True; return b
# back to front; the small Figma bubble (b3) rides above the card, like in the design
behind = [mk('s', g1), mk('m', g2), mk('b1', g1), mk('b2', g2)]
front = mk('b3', g1)

if __name__ == '__main__':
    out, i0, i1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    ff = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{OUT_W}x{OUT_H}',
                           '-r', str(FPS), '-i', '-', '-c:v', 'ffv1', out], stdin=subprocess.PIPE)
    for i in range(i0, i1):
        t = i / FPS
        fr = plate.copy()
        boxes = [b.draw(fr, t) for b in behind]
        for (bx0, by0, bx1, by1) in boxes:                            # the card stays in front of them
            sl = (slice(by0, by1), slice(bx0, bx1)); cm = CM[sl][..., None]; fr[sl] = plate[sl] * cm + fr[sl] * (1 - cm)
        boxes.append(front.draw(fr, t))
        for (bx0, by0, bx1, by1) in boxes:                            # and the headline above everything
            sl = (slice(by0, by1), slice(bx0, bx1)); ta = TA[sl][..., None]; fr[sl] = 255 * ta + fr[sl] * (1 - ta)
        img = Image.fromarray(fr.clip(0, 255).round().astype(np.uint8)).resize((OUT_W, OUT_H), Image.LANCZOS)
        ff.stdin.write(img.tobytes())
        if i % 50 == 0: print('frame', i, flush=True)
    ff.stdin.close(); ff.wait()
