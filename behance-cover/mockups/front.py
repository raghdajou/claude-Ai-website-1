# Front-facing monitor mockups: only the screen rectangle is replaced by the Foxlytics dashboard
# (measured edges, pixel-exact), then the scene is cropped to the Behance cover shape.
import sys
from PIL import Image
I = '/tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/images/'
DASH = Image.open(I + '110.jpg').convert('RGB')
SCENES = {   # file, screen box (left, top, right, bottom) in the photo, dashboard crop top
    'vela':   ('122.webp', (214, 221, 1722, 1069), 560),
    'kultur': ('123.png', (334, 213, 1286, 751), 560),
}
for name in (sys.argv[1:] or SCENES):
    f, (l, t, r, b), top = SCENES[name]
    scene = Image.open(I + f).convert('RGB')
    w, h = r - l, b - t
    src = DASH.crop((0, top, DASH.width, top + round(DASH.width * h / w))).resize((w, h), Image.LANCZOS)
    scene.paste(src, (l, t))
    cw = round(scene.height * 808 / 632); x0 = (scene.width - cw) // 2
    out = scene.crop((x0, 0, x0 + cw, scene.height)).resize((1616, 1264), Image.LANCZOS)
    out.save(f'foxlytics-{name}.png'); out.resize((808, 632), Image.LANCZOS).save(f'foxlytics-{name}-808.png'); print('done', name)
