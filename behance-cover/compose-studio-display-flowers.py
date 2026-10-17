# Cut the white Studio Display out of its wall with a hand-measured outline and set it on the flower photo.
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
src = Image.open('studio-display-white.png').convert('RGB')
k = src.width / 2000                         # outline measured on a 2000px-wide view
pts = [(400,198),(1620,191),(1618,996),(1208,994),(1204,1222),(1226,1230),(1222,1254),
       (802,1258),(798,1242),(914,1226),(898,996),(384,974)]
mask = Image.new('L', src.size, 0)
ImageDraw.Draw(mask).polygon([(x*k, y*k) for x, y in pts], fill=255)
mask = mask.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
box = mask.getbbox(); obj, mask = src.crop(box), mask.crop(box)

W, H = 3200, 2400
bg = Image.open('flowers.jpg').convert('RGB')
sc = max(W / bg.width, H / bg.height) * 1.02
bg = bg.resize((int(bg.width*sc), int(bg.height*sc)), Image.LANCZOS)
ox, oy = (bg.width-W)//2, (bg.height-H)//2
scene = bg.crop((ox, oy, ox+W, oy+H)).filter(ImageFilter.GaussianBlur(2))
vign = Image.radial_gradient('L').resize((W, H)).point(lambda v: int(v*0.30))
scene = Image.composite(Image.new('RGB', (W, H), (40, 52, 20)), scene, vign)

s = 2250 / obj.width
obj = obj.resize((int(obj.width*s), int(obj.height*s)), Image.LANCZOS)
mask = mask.resize(obj.size, Image.LANCZOS)
px, py = (W-obj.width)//2, (H - obj.height)//2 + 40
shadow = Image.new('L', (W, H), 0)
shadow.paste(mask.filter(ImageFilter.GaussianBlur(40)).point(lambda v: int(v*0.38)), (px+30, py+60))
ImageDraw.Draw(shadow).ellipse([W//2-520, py+obj.height-40, W//2+520, py+obj.height+50], fill=150)
shadow = shadow.filter(ImageFilter.GaussianBlur(30))
scene = Image.composite(Image.new('RGB', (W, H), (30, 36, 12)), scene, shadow)
scene.paste(obj, (px, py), mask)
scene.save('sd-flowers.png', optimize=True)
scene.resize((1200, 900), Image.LANCZOS).save('sd-flowers-preview.jpg', quality=90)
