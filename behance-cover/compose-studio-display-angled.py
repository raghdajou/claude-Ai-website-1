# Grey Studio Display on the meadow, warped to the angle and framing of the reference (images/52.png).
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
W, H = 3200, 2400
src = Image.open('studio-display-grey.png').convert('RGB')
k = src.width / 1400                      # source parts measured on a 1400px-wide view
f = W / 1536                              # target corners measured on a 1536px-wide view of the reference

def coeffs(dst, srcq):
    # Perspective coefficients mapping output (dst) points back to input (srcq) points.
    A, b = [], []
    for (x, y), (u, v) in zip(dst, srcq):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]
        b += [u, v]
    return np.linalg.solve(np.array(A, float), np.array(b, float))

def warp(box, dst, radius=0):
    x0, y0, x1, y1 = [c * k for c in box]
    srcq = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    dst = [(x * f, y * f) for x, y in dst]
    c = coeffs(dst, srcq)
    m = Image.new('L', src.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=255)
    img = src.transform((W, H), Image.PERSPECTIVE, c, Image.BICUBIC)
    msk = m.transform((W, H), Image.PERSPECTIVE, c, Image.BICUBIC)
    return img, msk.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.2))

head, hmask = warp((257, 208, 1156, 728), [(92, 150), (1452, 172), (1442, 995), (90, 948)], radius=int(6 * k))
stand, smask = warp((598, 728, 815, 894), [(645, 960), (960, 962), (978, 1215), (656, 1215)])

bg = Image.open('../cover/meadow.jpg').convert('RGB')
sc = max(W / bg.width, H / bg.height) * 1.02
bg = bg.resize((int(bg.width * sc), int(bg.height * sc)), Image.LANCZOS)
ox, oy = (bg.width - W) // 2, int((bg.height - H) * 0.45)
scene = bg.crop((ox, oy, ox + W, oy + H)).filter(ImageFilter.GaussianBlur(2))
vign = Image.radial_gradient('L').resize((W, H)).point(lambda v: int(v * 0.45))
scene = Image.composite(Image.new('RGB', (W, H), (12, 26, 8)), scene, vign)

both = Image.fromarray(np.maximum(np.asarray(hmask), np.asarray(smask)))
shadow = Image.new('L', (W, H), 0)
shadow.paste(both.filter(ImageFilter.GaussianBlur(45)).point(lambda v: int(v * 0.5)), (35, 55))
scene = Image.composite(Image.new('RGB', (W, H), (5, 12, 4)), scene, shadow.filter(ImageFilter.GaussianBlur(10)))
scene.paste(stand, (0, 0), smask)
scene.paste(head, (0, 0), hmask)
# Thin aluminium side edge on the near (right) side, as in the reference.
edge = Image.new('L', (W, H), 0)
ImageDraw.Draw(edge).polygon([(x * f, y * f) for x, y in [(1450, 172), (1458, 180), (1449, 990), (1441, 995)]], fill=255)
edge = edge.filter(ImageFilter.GaussianBlur(1.5))
grad = Image.linear_gradient('L').resize((W, H)).point(lambda v: 150 + v // 3)
scene = Image.composite(Image.merge('RGB', [grad] * 3), scene, edge)
scene.save('grey-meadow-angle.png', optimize=True)
scene.resize((1200, 900), Image.LANCZOS).save('grey-meadow-angle-preview.jpg', quality=90)
