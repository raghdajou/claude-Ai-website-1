# High-quality GIF encoder. Frame 1 is the whole slide, dithered once with a palette fitted to it.
# After that each frame carries only the pixels whose source colour changed, with its own palette
# fitted to just those pixels (the bubbles), so the moving glass gets a full 255 colours and the
# still slide is never re-dithered: no shimmer, no stray dots. Whenever part of the picture comes
# to rest, quiet frames repaint it one tile at a time (a 4 x 4 grid by default, GIF_TILES to change) with a palette of its own,
# so everything that holds still ends up with far more than 256 colours.
import numpy as np, subprocess, sys, ctypes, struct, os
from PIL import Image
from scipy.cluster.vq import kmeans2, vq
lib = ctypes.CDLL(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'libgq.so'))
P = np.ctypeslib.ndpointer
lib.fs_dither.argtypes = [P(np.float32), P(np.uint8), P(np.uint8), ctypes.c_int, ctypes.c_int, P(np.float32), ctypes.c_int, ctypes.c_float, P(np.uint8)]
lib.lzw.argtypes = [P(np.uint8), ctypes.c_int, ctypes.c_int, P(np.uint8)]; lib.lzw.restype = ctypes.c_int
STRENGTH = 0.85   # a touch under full error diffusion: smooth gradients, no salt-and-pepper grain

def palette(px, k):
    """k colours for these pixels: median cut as the start, then k-means to settle them"""
    px = px.reshape(-1, 3)
    if len(px) > 200000: px = px[np.random.default_rng(0).choice(len(px), 200000, replace=False)]
    u = np.unique(px, axis=0)
    if len(u) <= k: return u.astype(np.float32)
    side = int(np.ceil(np.sqrt(len(px))))
    tile = np.zeros((side * side, 3), np.uint8); tile[:len(px)] = px; tile[len(px):] = px[0]
    q = Image.fromarray(tile.reshape(side, side, 3)).quantize(k, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    init = np.asarray(q.getpalette()[:3 * k], np.float32).reshape(-1, 3)
    w = np.array([2, 4, 3], np.float32) ** 0.5                      # same weighting as the dither's distance
    c, _ = kmeans2(px.astype(np.float32) * w, init * w, iter=6, minit='matrix', missing='warn')
    return np.clip(c / w, 0, 255).astype(np.float32)

def dither(img, mask, pal, dm):
    out = np.zeros(mask.shape, np.uint8)
    lib.fs_dither(np.ascontiguousarray(img, np.float32), np.ascontiguousarray(mask, np.uint8), np.ascontiguousarray(dm, np.uint8), mask.shape[0], mask.shape[1],
                  np.ascontiguousarray(pal, np.float32), len(pal), STRENGTH, out)
    return out

def block(idx, x, y, pal, trans, delay):
    k = 256; ct = np.zeros((k, 3), np.uint8); ct[:len(pal)] = np.round(pal)
    gce = b'\x21\xf9\x04' + bytes([(1 << 2) | (1 if trans is not None else 0)]) + struct.pack('<H', delay) + bytes([trans or 0]) + b'\x00'
    h, w = idx.shape
    desc = b'\x2c' + struct.pack('<HHHH', x, y, w, h) + bytes([0x80 | 7])   # local colour table, 256 entries
    buf = np.zeros(idx.size * 2 + 4096, np.uint8)
    n = lib.lzw(np.ascontiguousarray(idx.ravel()), idx.size, 8, buf)
    return gce + desc + ct.tobytes() + b'\x08' + buf[:n].tobytes()

src, Wd, Hd, fps, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
# optional: a greyscale image giving how much each pixel is dithered (white: fully, black: not at all, crisp)
DM = np.asarray(Image.open(sys.argv[6]).convert('L').resize((Wd, Hd), Image.NEAREST)).astype(np.uint8) if len(sys.argv) > 6 else np.full((Hd, Wd), 255, np.uint8)
dec = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-i', src, '-vf', f'scale={Wd}:{Hd}:flags=lanczos', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                       stdout=subprocess.PIPE)
n = Wd * Hd * 3; delay = round(100 / fps)
f = open(out, 'wb')
f.write(b'GIF89a' + struct.pack('<HH', Wd, Hd) + bytes([0x70, 0, 0]))        # no global table: every frame brings its own
f.write(b'\x21\xff\x0bNETSCAPE2.0\x03\x01\x00\x00\x00')                    # loop forever
TY = TX = int(os.environ.get("GIF_TILES", 4)); tiles = [(ty * Hd // TY, (ty + 1) * Hd // TY, tx * Wd // TX, (tx + 1) * Wd // TX) for ty in range(TY) for tx in range(TX)]
QUIET = 0.03                  # a frame may refine a tile when under 3% of its pixels are moving
# dither share in busy frames (GIF_MOTION_DITHER, default 1): lower it to make the GIF smaller, since
# the motion hides banding and the refinement repaints everything with full dither once it settles
MOTION = float(os.environ.get('GIF_MOTION_DITHER', 1))
MOTION_COLORS = int(os.environ.get('GIF_MOTION_COLORS', 255))   # palette size for busy frames (fewer: smaller)
# GIF_MOTION_BAYER: if set, busy frames use an ordered 8 x 8 dither of this spread (in levels) instead
# of error diffusion: the pattern is fixed to the canvas, so it hides banding yet compresses well
BAYER = float(os.environ.get('GIF_MOTION_BAYER', 0))
B8 = np.array([[0, 32, 8, 40, 2, 34, 10, 42], [48, 16, 56, 24, 50, 18, 58, 26], [12, 44, 4, 36, 14, 46, 6, 38],
               [60, 28, 52, 20, 62, 30, 54, 22], [3, 35, 11, 43, 1, 33, 9, 41], [51, 19, 59, 27, 49, 17, 57, 25],
               [15, 47, 7, 39, 13, 45, 5, 37], [63, 31, 55, 23, 61, 29, 53, 21]], np.float32) / 64 - 0.5 + 1 / 128
WQ = np.array([2, 4, 3], np.float32) ** 0.5
def ordered(reg, m, pal, x0, y0):
    h, w = m.shape
    th = np.tile(B8, (h // 8 + 2, w // 8 + 2))[y0 % 8:y0 % 8 + h, x0 % 8:x0 % 8 + w]
    px = np.clip(reg.astype(np.float32) + th[..., None] * BAYER, 0, 255)[m]
    idx = np.full(m.shape, 255, np.uint8); idx[m] = vq(px * WQ, pal * WQ)[0]
    return idx
pending = np.ones((Hd, Wd), bool); still = np.zeros((Hd, Wd), np.int32)   # painted but not yet refined; frames unchanged
last = None; i = 0
while True:
    b = dec.stdout.read(n)
    if len(b) < n: break
    fr = np.frombuffer(b, np.uint8).reshape(Hd, Wd, 3)
    if last is None:
        pal = palette(fr, 256); idx = dither(fr.astype(np.float32), np.ones((Hd, Wd), np.uint8), pal, DM)
        f.write(block(idx, 0, 0, pal, None, delay))
    else:
        ch = (np.abs(fr.astype(np.int16) - last).max(-1) > 0)
        pending |= ch; still = np.where(ch, 0, still + 1)
        busy = ch.mean() >= QUIET
        if not busy:
            ready = pending & (still >= 2)                      # settled for two frames
            counts = [ready[a:b, c:d].sum() for (a, b, c, d) in tiles]
            k = int(np.argmax(counts))
            if counts[k] > 0:
                ty0, ty1, tx0, tx1 = tiles[k]
                sub = np.zeros_like(ch); sub[ty0:ty1, tx0:tx1] = ready[ty0:ty1, tx0:tx1]
                ch |= sub; pending &= ~sub
        if not ch.any():
            f.write(block(np.zeros((1, 1), np.uint8), 0, 0, np.zeros((1, 3), np.float32), 0, delay))
        else:
            ys, xs = np.nonzero(ch); y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
            m = ch[y0:y1, x0:x1]; reg = fr[y0:y1, x0:x1]
            pal = palette(reg[m], MOTION_COLORS if busy else 255)           # index 255 is kept for "unchanged"
            dm = DM[y0:y1, x0:x1] if not busy else np.round(DM[y0:y1, x0:x1] * MOTION).astype(np.uint8)
            if busy and BAYER > 0: idx = ordered(reg, m, pal, x0, y0)
            else: idx = dither(reg.astype(np.float32), m.astype(np.uint8), pal, dm); idx[~m] = 255
            f.write(block(idx, x0, y0, pal, 255, delay))
    last = fr.astype(np.int16); i += 1
    if i % 100 == 0: print('frame', i, flush=True)
f.write(b'\x3b'); f.close(); print(out, i, 'frames', os.path.getsize(out) // 1024, 'KB')
