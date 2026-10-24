# Builds: the clean plate (slide with the bubbles lifted out) and one RGBA layer per bubble,
# exactly as Figma rendered it (glass, highlights, soft shadow).
import numpy as np
from PIL import Image
from scipy import ndimage
S=np.asarray(Image.open('slide.png').convert('RGB')).astype(np.float32)
C=np.asarray(Image.open('clean_full.png').convert('RGB')).astype(np.float32)
d=np.load('diff.npy'); H,W=d.shape
a2=np.load('text_a2.npy'); tx,ty=[int(v) for v in np.load('text_pos.npy')]
TA=np.zeros((H,W),np.float32); TA[ty:ty+a2.shape[0],tx:tx+a2.shape[1]]=a2
B={'b1':(2415,702,150),'b2':(3300,1218,165),'b3':(2755,1848,66)}
yy,xx=np.mgrid[0:H,0:W]
foot=np.zeros((H,W),np.float32)
for k,(cx,cy,r) in B.items():
    R=r+70   # glass plus its soft shadow
    x0,y0,x1,y1=cx-R,cy-R,cx+R,cy+R+30
    sub=d[y0:y1,x0:x1]; dist=np.hypot(xx[y0:y1,x0:x1]-cx,yy[y0:y1,x0:x1]-cy)
    disc=np.clip((r+1.5-dist)/3,0,1)                       # the glass itself, anti-aliased edge
    # its soft shadow: only in a ring just outside the glass, and never where the headline's
    # letters are (their edges differ by a hair between the slide and the rebuild)
    near_text=ndimage.binary_dilation(TA[y0:y1,x0:x1]>0.01,iterations=5)
    ring=((dist>=r-1)&(dist<r+60)).astype(np.float32)*(~near_text)
    halo=np.clip((sub-4)/12,0,1)*ring
    if k=='b3':
        # on the card: the glass only, shaped by what Figma drew (it has a notch), no shadow ring
        a=disc*np.clip((ndimage.gaussian_filter(sub,1.5)-6)/10,0,1)
        a=np.maximum(a,disc*(ndimage.binary_closing(sub>14,iterations=3)).astype(np.float32))
    else:
        a=np.maximum(disc,halo)
    rgb=S[y0:y1,x0:x1].copy()
    if k=='b1':
        # the headline sits in front of this bubble: lift its letters out of the layer and fill
        # the glass underneath from the surrounding glass (it is soft, so this blends in)
        ta=TA[y0:y1,x0:x1]; known=(ta<0.02).astype(np.float32)
        fill=rgb*known[...,None]; wgt=known.copy()
        for s in (2,4,8,16):
            f=np.stack([ndimage.gaussian_filter(fill[...,c],s) for c in range(3)],-1); w=ndimage.gaussian_filter(wgt,s)
            est=f/np.maximum(w[...,None],1e-4)
            rgb=np.where(known[...,None]>0.5,rgb,np.where(w[...,None]>0.05,est,rgb))
            fill=rgb*1.0; wgt=np.maximum(wgt,(w>0.05).astype(np.float32))
        # recover the true colour where letters' edges were blended over the glass
    lay=np.dstack([rgb,a*255]).clip(0,255).astype(np.uint8)
    Image.fromarray(lay,'RGBA').save(f'layer_{k}.png')
    open(f'layer_{k}.txt','w').write(f'{x0} {y0} {cx} {cy}')
    f=np.zeros((H,W),np.float32); f[y0:y1,x0:x1]=a; foot=np.maximum(foot,f)
# clean plate: the rebuild only around the bubbles (dilated for the motion), the slide elsewhere
w=ndimage.binary_dilation(foot>0.02,iterations=40).astype(np.float32)
w=ndimage.gaussian_filter(w,10)
plate=S*(1-w[...,None])+C*w[...,None]
Image.fromarray(plate.clip(0,255).astype(np.uint8)).save('plate.png')
np.save('text_full_a.npy',TA)
print('ok')
