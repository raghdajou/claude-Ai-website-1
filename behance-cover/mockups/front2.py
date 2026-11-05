# Front-facing monitor mockups with three more Foxlytics screens (Payroll, Employees, Overview):
# only the measured screen rectangle changes; scene cropped to the Behance cover shape.
from PIL import Image
I = '/tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/images/'
SCENES = {'vela': ('122.webp', (214, 221, 1722, 1069)), 'kultur': ('123.png', (334, 213, 1286, 751))}
SCREENS = {'payroll': ('124.jpg', 420), 'employees': ('125.jpg', 470), 'overview': ('126.jpg', 150)}   # file, band top
for sn, (sf, (l, t, r, b)) in SCENES.items():
    for dn, (df, top) in SCREENS.items():
        scene = Image.open(I + sf).convert('RGB'); dash = Image.open(I + df).convert('RGB')
        w, h = r - l, b - t; bh = round(dash.width * h / w); top = min(top, dash.height - bh)
        scene.paste(dash.crop((0, top, dash.width, top + bh)).resize((w, h), Image.LANCZOS), (l, t))
        cw = round(scene.height * 808 / 632); x0 = (scene.width - cw) // 2
        out = scene.crop((x0, 0, x0 + cw, scene.height)).resize((1616, 1264), Image.LANCZOS)
        out.save(f'fx-{sn}-{dn}.png'); out.resize((808, 632), Image.LANCZOS).save(f'fx-{sn}-{dn}-808.png')
