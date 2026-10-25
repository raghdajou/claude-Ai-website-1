# Periodic "billiard" paths: each bubble glides at constant speed and bounces off the photo card's
# edges; x and y each make a whole number of round trips per loop, so the loop is seamless and no
# bubble ever stops. Card (2x px): x 2155..3766, y 89..2347.
import math
L = 16.0
X0, X1, Y0, Y1 = 2155, 3766, 89, 2347
PAD = 18
def tri(s):                       # 0..1..0 over one period
    s %= 1.0; return 1 - abs(2 * s - 1)
def phase_for(v, lo, hi, going_up):
    f = (v - lo) / (hi - lo); f = min(max(f, 0), 1)
    return f / 2 if going_up else 1 - f / 2
class Path:
    def __init__(s, x, y, r, nx, ny, dx, dy):
        s.r = r; s.nx, s.ny = nx, ny
        s.xlo, s.xhi = X0 + r + PAD, X1 - r - PAD; s.ylo, s.yhi = Y0 + r + PAD, Y1 - r - PAD
        s.px = phase_for(x, s.xlo, s.xhi, dx > 0); s.py = phase_for(y, s.ylo, s.yhi, dy > 0)
    def pos(s, t):
        return (s.xlo + (s.xhi - s.xlo) * tri(s.px + s.nx * t / L), s.ylo + (s.yhi - s.ylo) * tri(s.py + s.ny * t / L))
    def hits(s):
        """times of wall contacts with the wall's outward normal angle"""
        out = []
        T = L / s.nx
        for ph, ang in ((0.5, 0.0), (1.0, math.pi)):
            t0 = ((ph - s.px) % 1) * T
            out += [((t0 + i * T) % L, ang) for i in range(s.nx)]
        T = L / s.ny
        for ph, ang in ((0.5, math.pi / 2), (1.0, -math.pi / 2)):
            t0 = ((ph - s.py) % 1) * T
            out += [((t0 + i * T) % L, ang) for i in range(s.ny)]
        return sorted(out)
