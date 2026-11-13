# Front-on monitor over blurred flowers (251): the screen gets the Attendees page's first chart
# (Attendance Flow Analysis, a little space above its title, through its notes), fitted without
# stretching on the page colour. 4000x3000 PNG (+2000, 1000) and 16:9 artboard.
from PIL import Image, ImageFilter
I = '/tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/images/'
L, T, R, B = 100.5, 123.5, 1897.5, 1135.5; TOP, BOT = 340, 1112   # from just above Attendance Flow Analysis down to the chart's end
base = Image.open(I + '251.webp').convert('RGB'); page = Image.open(I + '252.jpg').convert('RGB')
bg = page.getpixel((page.width // 2, page.height - 5)); asp = (R - L) / (B - T)
# chart only (no section title or controls), filling the screen edge to edge at full content width
X0 = 112; w = page.width - X0; h = round(w / asp); y0 = 600 - (h - 512) // 2   # chart rows 600-1112, centred
band = page.crop((X0, y0, page.width, y0 + h))
from PIL import ImageDraw
ImageDraw.Draw(band).rectangle((0, 0, band.width, 598 - y0), fill=bg)   # hide the divider line above the chart
F = 2; W, H = 4000, 3000; out = base.resize((W, H), Image.LANCZOS)
cw, ch = round((R - L) * F), round((B - T) * F); k = cw / w
snap = band.resize((cw, ch), Image.LANCZOS).point(lambda v: round(255 * (v / 255) ** 1.08)).filter(ImageFilter.UnsharpMask(radius=0.7 * k, percent=70, threshold=2))
out.paste(snap, (round(L * F), round(T * F)))
out.save('uw-solva-attendees-x4-4000.png', optimize=True)
out.resize((2000, 1500), Image.LANCZOS).save('uw-solva-attendees-2000.png', optimize=True); out.resize((1000, 750), Image.LANCZOS).save('uw-solva-attendees-1000.png', optimize=True)
out.crop((0, 100, 4000, 2350)).resize((2800, 1576), Image.LANCZOS).save('ab-solva-attendees-2800.png')
print('done', round(k, 2))
