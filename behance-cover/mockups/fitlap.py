import numpy as np, sys
from PIL import Image
def edge_after_dark(seq, thr_dark=5, thr=7):
    """seq runs from outside toward the screen; return the subpixel index where the content starts after
    the longest dark (bezel) run."""
    d = seq < thr_dark; best = (0, -1, -1); i = 0
    while i < len(seq):
        if d[i]:
            j = i
            while j < len(seq) and d[j]: j += 1
            if j - i > best[0]: best = (j - i, i, j)
            i = j
        else: i += 1
    if best[0] < 2: return None
    j = best[2]
    if j >= len(seq): return None
    k = j
    while k < len(seq) and seq[k] < thr: k += 1
    if k >= len(seq) or k - j > 4: return None
    return k - 1 + (thr - seq[k - 1]) / max(seq[k] - seq[k - 1], 1e-3)
def fit(name, pts):
    p = np.array([q for q in pts if q[1] is not None], float)
    c = np.polyfit(p[:, 0], p[:, 1], 1); res = np.abs(np.polyval(c, p[:, 0]) - p[:, 1])
    keep = res < max(1.0, np.median(res) * 3)
    c = np.polyfit(p[keep, 0], p[keep, 1], 1); res = np.abs(np.polyval(c, p[keep, 0]) - p[keep, 1])
    print(name, c.round(5), 'n', keep.sum(), '/', len(p), 'maxres', res.max().round(2)); return c
def run(f, L, R, T, B):
    g = np.asarray(Image.open(f).convert('L')).astype(float)
    # each spec: (scan values range, line approx a,b with other = a*s+b, half window)
    out = {}
    (ys, a, b, w) = L; out['L'] = fit('L', [(y, (lambda e, x0: None if e is None else x0 + e)(edge_after_dark(g[y, int(a*y+b-w):int(a*y+b+w)]), int(a*y+b-w))) for y in ys])
    (ys, a, b, w) = R; out['R'] = fit('R', [(y, (lambda e, x0: None if e is None else x0 - e)(edge_after_dark(g[y, int(a*y+b+w):int(a*y+b-w):-1]), int(a*y+b+w))) for y in ys])
    (xs, a, b, w) = T; out['T'] = fit('T', [(x, (lambda e, y0: None if e is None else y0 + e)(edge_after_dark(g[int(a*x+b-w):int(a*x+b+w), x]), int(a*x+b-w))) for x in xs])
    (xs, a, b, w) = B; out['B'] = fit('B', [(x, (lambda e, y0: None if e is None else y0 - e)(edge_after_dark(g[int(a*x+b+w):int(a*x+b-w):-1, x]), int(a*x+b+w))) for x in xs])
    def meet(Lc, Tc):
        y = (Tc[0] * Lc[1] + Tc[1]) / (1 - Tc[0] * Lc[0]); return (round(Lc[0] * y + Lc[1], 2), round(y, 2))
    print('quad', [meet(out['L'], out['T']), meet(out['R'], out['T']), meet(out['R'], out['B']), meet(out['L'], out['B'])])
