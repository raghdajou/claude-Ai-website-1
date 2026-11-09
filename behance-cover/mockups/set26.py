# Two stacked web pages on black ("stack", 216): top page = Analytics from its Productive Heat Map,
# bottom page = Payroll from the top (runs off the bottom edge). Upwork 4:3 (1000, 2000 JPEG;
# 4000 PNG + JPEG) and Behance artboard 16:9 (1400, 2800).
from PIL import Image, ImageFilter
I = '/tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/images/'
base = Image.open(I + '216.webp').convert('RGB')
PAGES = [('218.jpg', 815, (248, 0, 1312, 626)), ('217.webp', 0, (248, 661, 1312, 1200))]
def tone(p, k): return p.point(lambda v: round(255 * (v / 255) ** 1.12)).filter(ImageFilter.UnsharpMask(radius=0.7 * k, percent=90, threshold=2))
for F in (1, 2, 2.5):
    W, H = round(1600 * F), round(1200 * F); out = base.resize((W, H), Image.LANCZOS)
    for f, top, (l, t, r, b) in PAGES:
        src = Image.open(I + f).convert('RGB'); w, h = round((r - l) * F), round((b - t) * F); k = w / src.width
        p = src.resize((w, round(src.height * k)), Image.LANCZOS); y = round(top * k)
        out.paste(tone(p.crop((0, y, w, y + h)), k), (round(l * F), round(t * F)))
    if F == 1:
        out.resize((1000, 750), Image.LANCZOS).save('uw-stack-1000.jpg', quality=97, subsampling=0)
        out.crop((0, 150, W, 1050)).resize((1400, 788), Image.LANCZOS).save('ab-stack-1400.png')
    elif F == 2:
        out.resize((2000, 1500), Image.LANCZOS).save('uw-stack-2000.jpg', quality=97, subsampling=0)
        out.crop((0, 300, W, 2100)).resize((2800, 1576), Image.LANCZOS).save('ab-stack-2800.png')
    else:
        out.save('uw-stack-x4-4000.png', optimize=True); out.save('uw-stack-x4-4000.jpg', quality=95, subsampling=0)
print('done')
