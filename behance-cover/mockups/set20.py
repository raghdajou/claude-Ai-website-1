# Front-facing display on a frosted backdrop, light (196) and dark (197): only the screen changes, one
# image per Foxlytics page (a 16:9 band from a chosen row). Upwork 4:3 = the whole scene (1000x750,
# 2000x1500 JPEG); Behance artboard 16:9 = rows 200-1100 (1400x788, 2800x1576).
from PIL import Image, ImageFilter
I = '/tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/images/'
SCENES = {'frost': ('196.webp', (200.5, 309.5, 1398.5, 983.5)), 'frostdark': ('197.webp', (196, 306, 1404, 991.5))}
PAGES = {'overview': ('170.jpg', 0), 'analytics': ('186.webp', 240), 'attendees': ('187.webp', 246),
         'payroll': ('188.webp', 1055), 'projects': ('189.webp', 560), 'employees': ('190.jpg', 560)}
for sn, (sf, (l0, t0, r0, b0)) in SCENES.items():
    base = Image.open(I + sf).convert('RGB')
    for pn, (pf, top) in PAGES.items():
        src = Image.open(I + pf).convert('RGB')
        for K in (1, 2):
            S = 4; sc = base.resize((base.width * K * S, base.height * K * S), Image.NEAREST) if False else None
            scene = base.resize((base.width * K, base.height * K), Image.LANCZOS)
            l, t, r, b = [round(v * K) for v in (l0, t0, r0, b0)]; w, h = r - l, b - t
            k = w / src.width; band = round(h / k)
            p = src.crop((0, top, src.width, top + band)).resize((w, h), Image.LANCZOS)
            p = p.point(lambda v: round(255 * (v / 255) ** 1.12)).filter(ImageFilter.UnsharpMask(radius=0.7 * k, percent=90, threshold=2))
            scene.paste(p, (l, t))
            scene.resize((2000, 1500) if K == 2 else (1000, 750), Image.LANCZOS).save(f'uw-{sn}-{pn}-{2000 if K == 2 else 1000}.jpg', quality=97, subsampling=0)
            scene.crop((0, 200 * K, scene.width, 1100 * K)).resize((2800, 1576) if K == 2 else (1400, 788), Image.LANCZOS).save(f'ab-{sn}-{pn}-{2800 if K == 2 else 1400}.png')
        print('done', sn, pn)
