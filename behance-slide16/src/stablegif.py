# Flicker-free GIF: one global palette; the still parts of the slide are dithered once and reused
# in every frame, and only pixels that actually change are re-dithered. ffmpeg then writes exact
# palette colours (no dither) with unchanged pixels transparent, so nothing static ever shimmers.
import numpy as np, subprocess, sys
from PIL import Image
src, W, Hh, fps, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
vf = f'scale={W}:{Hh}:flags=lanczos'
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', src, '-vf', vf + ',palettegen=max_colors=256:stats_mode=full', 'pal.png'], check=True)
pal = Image.open('pal.png').convert('RGB'); cols = np.asarray(pal).reshape(-1, 3)[:256]
pimg = Image.new('P', (1, 1)); pimg.putpalette(cols.flatten().tolist() + [0] * (768 - cols.size))
dec = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-i', src, '-vf', vf, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
enc = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{Hh}', '-r', str(fps), '-i', '-',
                        '-i', 'pal.png', '-lavfi', 'paletteuse=dither=none:diff_mode=rectangle', '-gifflags', '+transdiff', '-loop', '0', out], stdin=subprocess.PIPE)
n = W * Hh * 3; ref = None; Q0 = None
def q(a): return np.asarray(Image.fromarray(a).quantize(palette=pimg, dither=Image.Dither.FLOYDSTEINBERG))
frames = []
while True:
    b = dec.stdout.read(n)
    if len(b) < n: break
    frames.append(np.frombuffer(b, np.uint8).reshape(Hh, W, 3))
# the reference is the per-pixel most common value: what the slide looks like where nothing moves
stack_mode = np.median(np.stack(frames[::8]), axis=0).astype(np.uint8)
Q0 = q(stack_mode)
for f in frames:
    same = (f == stack_mode).all(-1)
    idx = np.where(same, Q0, q(f))
    enc.stdin.write(cols[idx].astype(np.uint8).tobytes())
enc.stdin.close(); enc.wait(); print(out, len(frames))
