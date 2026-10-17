import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 3200, 2400
imac = Image.open('imac.png').convert('RGB')
a = np.asarray(imac).astype(int)

# 1. Cut out the iMac: flood-fill the white backdrop from the image border.
lum, sat = a.mean(2), a.max(2) - a.min(2)
bg = (lum > 238) & (sat < 14)
mask = Image.fromarray(np.where(bg, 255, 0).astype(np.uint8))
seed_img = Image.new('L', mask.size, 0)
probe = mask.copy()
for sx, sy in [(0, 0), (1249, 0), (0, 1249), (1249, 1249), (625, 0), (0, 625), (1249, 625), (625, 1249)]:
    if probe.getpixel((sx, sy)) == 255: ImageDraw.floodfill(probe, (sx, sy), 128)
outside = (np.asarray(probe) == 128)
alpha = Image.fromarray(np.where(outside, 0, 255).astype(np.uint8)).filter(ImageFilter.MinFilter(5)).filter(ImageFilter.GaussianBlur(1.1))

# 2. Put the dashboard on the screen with a perspective warp (in the photo's own coordinates, supersampled).
S = 1.95                                   # photo -> output scale
inner = np.array([(121, 249), (1034, 248), (1112, 771), (191, 853)], float) * S
dash = Image.open('../cover/dashboard.jpg').convert('RGB')
dash = dash.crop((0, 22, 871, 512))         # top of the dashboard at 16:9, like the iMac screen
dash = dash.resize((871 * 3, 490 * 3), Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=2, percent=70, threshold=2))
dw, dh = dash.size
def coeffs(dst, src):                      # PIL wants output->input mapping
    A, b = [], []
    for (x, y), (u, v) in zip(dst, src):
        A += [[x, y, 1, 0, 0, 0, -u*x, -u*y], [0, 0, 0, x, y, 1, -v*x, -v*y]]; b += [u, v]
    return np.linalg.solve(np.array(A, float), np.array(b, float))
iw, ih = int(1250 * S), int(1250 * S)
screen = dash.transform((iw, ih), Image.PERSPECTIVE, coeffs(inner, [(0, 0), (dw, 0), (dw, dh), (0, dh)]), Image.BICUBIC)
smask = Image.new('L', (iw, ih), 0); ImageDraw.Draw(smask).polygon([tuple(p) for p in inner], fill=255)
smask = smask.filter(ImageFilter.GaussianBlur(0.6))

# Gentle glass reflection, a diagonal sheen like the original photo's lighting.
yy, xx = np.mgrid[0:ih, 0:iw]
sheen = np.clip(0.10 - ((xx * 0.55 + yy) / (iw + ih)) * 0.16, 0, 0.10)
big = imac.resize((iw, ih), Image.LANCZOS)
big.paste(screen, (0, 0), smask)
arr = np.asarray(big).astype(float)
m = np.asarray(smask).astype(float)[..., None] / 255
arr = arr * (1 - sheen[..., None] * m) + 255 * sheen[..., None] * m
big = Image.fromarray(arr.clip(0, 255).astype(np.uint8))
big_alpha = alpha.resize((iw, ih), Image.LANCZOS)

# 3. Scene: meadow background, slight blur for depth, iMac centred with soft shadows.
meadow = Image.open('../cover/meadow.jpg').convert('RGB')
mw, mh = meadow.size; sc = max(W / mw, H / mh) * 1.02
meadow = meadow.resize((int(mw * sc), int(mh * sc)), Image.LANCZOS)
ox, oy = (meadow.width - W) // 2, int((meadow.height - H) * 0.45)
scene = meadow.crop((ox, oy, ox + W, oy + H)).filter(ImageFilter.GaussianBlur(3))
vign = Image.radial_gradient('L').resize((W, H)).point(lambda v: int(v * 0.55))
scene = Image.composite(Image.new('RGB', (W, H), (12, 26, 8)), scene, vign)

px, py = (W - iw) // 2 + 40, int(H - 1120 * S) - int(205 * S) + 250
shadow = Image.new('L', (W, H), 0)
sd = ImageDraw.Draw(shadow)
sh = big_alpha.filter(ImageFilter.GaussianBlur(40)).point(lambda v: int(v * 0.45))
shadow.paste(sh, (px + 30, py + 60))
foot_y = py + int(1185 * S)               # contact shadow under the stand's foot
sd.ellipse([px + int(420 * S), foot_y - 30, px + int(880 * S), foot_y + 60], fill=150)
shadow = shadow.filter(ImageFilter.GaussianBlur(28))
scene = Image.composite(Image.new('RGB', (W, H), (5, 12, 4)), scene, shadow)
scene.paste(big, (px, py), big_alpha)
scene.save('imac-cover.png', optimize=True)
scene.resize((1200, 900), Image.LANCZOS).save('imac-preview.jpg', quality=90)
print('saved', scene.size, 'imac box', px, py, iw, ih)
