# Grey Studio Display (cut from its studio shot by a measured outline) on the purple-flower meadow.
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
src = Image.open('studio-display-grey.png').convert('RGB')
k = src.width / 1400                          # outline measured on a 1400px-wide view
pts = [(257,208),(1156,208),(1156,728),(815,728),(815,894),(598,894),(598,728),(257,728)]
mask = Image.new('L', src.size, 0)
d = ImageDraw.Draw(mask)
d.rounded_rectangle([257*k, 208*k, 1156*k, 728*k], radius=int(6*k), fill=255)
d.polygon([(x*k, y*k) for x, y in pts[3:]], fill=255)
mask = mask.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
box = mask.getbbox(); obj, mask = src.crop(box), mask.crop(box)

W, H = 3200, 2400
bg = Image.open('../cover/meadow.jpg').convert('RGB')
sc = max(W / bg.width, H / bg.height) * 1.02
bg = bg.resize((int(bg.width*sc), int(bg.height*sc)), Image.LANCZOS)
ox, oy = (bg.width-W)//2, int((bg.height-H)*0.45)
scene = bg.crop((ox, oy, ox+W, oy+H)).filter(ImageFilter.GaussianBlur(3))
vign = Image.radial_gradient('L').resize((W, H)).point(lambda v: int(v*0.55))
scene = Image.composite(Image.new('RGB', (W, H), (12, 26, 8)), scene, vign)

s = 2200 / obj.width
obj = obj.resize((int(obj.width*s), int(obj.height*s)), Image.LANCZOS)
mask = mask.resize(obj.size, Image.LANCZOS)
px, py = (W-obj.width)//2, H - obj.height - 300
shadow = Image.new('L', (W, H), 0)
shadow.paste(mask.filter(ImageFilter.GaussianBlur(40)).point(lambda v: int(v*0.45)), (px+30, py+60))
fy = py + obj.height
ImageDraw.Draw(shadow).ellipse([W//2-420, fy-30, W//2+420, fy+60], fill=170)
shadow = shadow.filter(ImageFilter.GaussianBlur(28))
scene = Image.composite(Image.new('RGB', (W, H), (5, 12, 4)), scene, shadow)
scene.paste(obj, (px, py), mask)
scene.save('grey-meadow.png', optimize=True)
scene.resize((1200, 900), Image.LANCZOS).save('grey-meadow-preview.jpg', quality=90)
