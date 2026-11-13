# Front-on monitor over blurred flowers (251): the screen gets the Attendees page's first chart
# (Attendance Flow Analysis, a little space above its title, through its notes), fitted without
# stretching on the page colour. 4000x3000 PNG (+2000, 1000) and 16:9 artboard.
from PIL import Image, ImageFilter
I = '/tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/images/'
L, T, R, B = 100.5, 123.5, 1897.5, 1135.5; _OLD = 340, 1112   # from just above Attendance Flow Analysis down to the chart's end
base = Image.open(I + '251.webp').convert('RGB'); page = Image.open(I + '253.png').convert('RGB')
bg = page.getpixel((page.width // 2, page.height - 5)); asp = (R - L) / (B - T)
# Employees: from a little above "Workforce Cost Intelligence" down to the chart's bottom labels, sidebar left out;
# the section is taller than the screen's shape, so it is centred on the page colour (no stretching)
X0, TOP, BOT = 152, 540, 1442   # title left out: starts just above the three cards
sec = page.crop((X0, TOP, page.width, BOT)); h = sec.height; w = round(h * asp)
band = Image.new('RGB', (w, h), bg); band.paste(sec, ((w - sec.width) // 2, 0))
F = 2; W, H = 4000, 3000; out = base.resize((W, H), Image.LANCZOS)
cw, ch = round((R - L) * F), round((B - T) * F); k = cw / w
snap = band.resize((cw, ch), Image.LANCZOS).point(lambda v: round(255 * (v / 255) ** 1.08)).filter(ImageFilter.UnsharpMask(radius=0.7 * k, percent=70, threshold=2))
out.paste(snap, (round(L * F), round(T * F)))
out.save('uw-solva-employees-x4-4000.png', optimize=True)
out.resize((2000, 1500), Image.LANCZOS).save('uw-solva-employees-2000.png', optimize=True); out.resize((1000, 750), Image.LANCZOS).save('uw-solva-employees-1000.png', optimize=True)
out.crop((0, 100, 4000, 2350)).resize((2800, 1576), Image.LANCZOS).save('ab-solva-employees-2800.png')
print('done', round(k, 2))
