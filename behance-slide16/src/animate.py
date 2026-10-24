# Renders the bubbles' motion over the clean plate: each bubble drifts on its own slow figure-eight,
# breathes a little, and its glass wobbles slightly as it moves. Seamless 8 s loop at 30 fps.
import numpy as np, sys, subprocess, math
from PIL import Image
L, FPS = 8.0, 30
OUT_W, OUT_H = 2800, 1985
plate = Image.open('plate.png').convert('RGBA')
TA = np.load('text_full_a.npy')
text = np.dstack([np.full(TA.shape + (3,), 255, np.uint8), (TA * 255).astype(np.uint8)])
text_img = Image.fromarray(text, 'RGBA')
# (amplitude x, amplitude y, phase, breathing, wobble degrees)
MOTION = {
  'b1': dict(ax=10, ay=16, ph=0.0, s=0.025, rot=3.0),
  'b2': dict(ax=12, ay=20, ph=2.1, s=0.03, rot=-3.5),
  'b3': dict(ax=2.5, ay=4, ph=4.2, s=0.015, rot=1.0),   # small and on the card's edge: a gentle bob
}
layers = {}
for k in MOTION:
    x0, y0, cx, cy = [int(v) for v in open(f'layer_{k}.txt').read().split()]
    layers[k] = (Image.open(f'layer_{k}.png'), x0, y0, cx, cy)
ff = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{OUT_W}x{OUT_H}',
                       '-r', str(FPS), '-i', '-', '-c:v', 'ffv1', sys.argv[1]], stdin=subprocess.PIPE)
N = int(L * FPS)
for i in range(N):
    t = i / FPS; w = 2 * math.pi * t / L
    fr = plate.copy()
    for k, m in MOTION.items():
        img, x0, y0, cx, cy = layers[k]
        # figure-eight: once across, twice up and down per loop
        dx = m['ax'] * math.sin(w + m['ph']); dy = m['ay'] * math.sin(2 * w + m['ph'])
        sc = 1 + m['s'] * math.sin(2 * w + m['ph'] + math.pi / 2)
        ang = m['rot'] * math.sin(w + m['ph'] + 0.6)
        ox, oy = cx - x0, cy - y0
        big = img.resize((round(img.width * sc), round(img.height * sc)), Image.BICUBIC).rotate(ang, Image.BICUBIC, center=(ox * sc, oy * sc))
        px = round(cx + dx - ox * sc); py = round(cy + dy - oy * sc)
        fr.alpha_composite(big, (px, py))
        if k == 'b1':   # the headline stays in front of this bubble, as in the design
            box = (px - 20, py - 20, px + big.width + 20, py + big.height + 20)
            fr.alpha_composite(text_img.crop(box), (box[0], box[1]))
    out = fr.convert('RGB').resize((OUT_W, OUT_H), Image.LANCZOS)
    ff.stdin.write(out.tobytes())
ff.stdin.close(); ff.wait(); print('frames', N)
