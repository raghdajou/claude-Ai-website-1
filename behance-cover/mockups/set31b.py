# Page card seen from its bottom ("hartt end", 236): card x 300-1300, top runs off the frame, bottom
# edge at y 1098. The Projects page (237, 1998 px wide) fills it at its full width; the page is a bit
# shorter than the card, so the blank page colour continues above it. 4000x3000 PNG (+2000, 1000) and
# a 16:9 Behance artboard.
from PIL import Image, ImageFilter
I = '/tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/images/'
L, R, B = 300, 1300, 1098
base = Image.open(I + '236.webp').convert('RGB'); page = Image.open(I + '238.webp').convert('RGB')
F = 2.5; W, H = 4000, 3000; out = base.resize((W, H), Image.LANCZOS)
w, h = round((R - L) * F), round(B * F); k = w / page.width
p = page.resize((w, round(page.height * k)), Image.LANCZOS)
p = p.point(lambda v: round(255 * (v / 255) ** 1.08)).filter(ImageFilter.UnsharpMask(radius=0.8, percent=60, threshold=2))
card = Image.new('RGB', (w, h), (250, 250, 250)); card.paste(p.crop((0, p.height - h, w, p.height)) if p.height > h else p, (0, max(h - p.height, 0)))   # bottom of the page, top runs off the frame
out.paste(card, (round(L * F), 0))
out.save('uw-hartt-projects-bottom-x4-4000.png', optimize=True)
out.resize((2000, 1500), Image.LANCZOS).save('uw-hartt-projects-bottom-2000.png', optimize=True)
out.resize((1000, 750), Image.LANCZOS).save('uw-hartt-projects-bottom-1000.png', optimize=True)
ab = Image.new('RGB', (4000, 2250), base.getpixel((20, 1180))); ab.paste(out.crop((0, 750, 4000, 3000)), (0, 0))
ab.resize((2800, 1576), Image.LANCZOS).save('ab-hartt-projects-bottom-2800.png')
print(w, h, p.size)
