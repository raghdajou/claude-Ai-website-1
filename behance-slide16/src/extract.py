import numpy as np, json
from PIL import Image
from scipy import ndimage
S=np.asarray(Image.open('slide.png').convert('RGB')).astype(np.float32)
C=np.asarray(Image.open('clean_full.png').convert('RGB')).astype(np.float32)
d=np.load('diff.npy')
H,W=d.shape
regions={'b1':(2200,360,2700,960),'b2':(3080,1020,3530,1480),'b3':(2650,1740,2880,1960)}
out={}
for k,(x0,y0,x1,y1) in regions.items():
    sub=d[y0:y1,x0:x1]
    m=ndimage.binary_opening(sub>22,iterations=4)
    lab,n=ndimage.label(m); sizes=ndimage.sum(m,lab,range(1,n+1)); i=int(np.argmax(sizes))+1
    blob=lab==i
    ys,xs=np.nonzero(blob)
    # circle fit (least squares) to the blob's outline
    edge=blob ^ ndimage.binary_erosion(blob)
    ey,ex=np.nonzero(edge); A=np.c_[2*ex,2*ey,np.ones(len(ex))]; bb=ex**2+ey**2
    cx,cy,c=np.linalg.lstsq(A,bb,rcond=None)[0]; r=float(np.sqrt(c+cx**2+cy**2))
    cx+=x0; cy+=y0
    out[k]=dict(cx=float(cx),cy=float(cy),r=r,area=int(sizes[i-1]))
    print(k,out[k])
json.dump(out,open('bubbles.json','w'),indent=1)
