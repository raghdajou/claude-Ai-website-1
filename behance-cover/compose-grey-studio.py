# Put a page or photo on the screen of the grey studio Studio Display shot (wall + black table).
# Args: image, region "x0,y0,x1,y1" (cropped to fill the screen), output name.
import sys
from PIL import Image, ImageFilter
src = Image.open('studio-display-grey.png').convert('RGB')
img = Image.open(sys.argv[1]).convert('RGB')
box = [int(v) for v in sys.argv[2].split(',')]
sx0, sy0, sx1, sy1 = 541, 441, 2288, 1436              # screen area inside the bezel
crop = img.crop(box).resize((sx1 - sx0, sy1 - sy0), Image.LANCZOS)
src.paste(crop.filter(ImageFilter.UnsharpMask(1.0, 50, 2)), (sx0, sy0))
src = src.resize((3200, 2400), Image.LANCZOS)
src.save(sys.argv[3] + '.png', optimize=True)
src.resize((1200, 900), Image.LANCZOS).save(sys.argv[3] + '-preview.jpg', quality=90)
