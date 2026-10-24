import numpy as np
from PIL import Image
from scipy import ndimage
S=np.asarray(Image.open('slide.png').convert('RGB')).astype(np.float32)
def over_rgb(base,rgb,a,x,y):
    h,w=a.shape; reg=base[y:y+h,x:x+w]; reg[:]=rgb*a[...,None]+reg*(1-a[...,None])
P=np.asarray(Image.open('photo.png').convert('RGBA')).astype(np.float32)
clean=S.copy(); over_rgb(clean,P[...,:3],P[...,3]/255,2155,89)
a2=np.load('text_a2.npy'); tx,ty=np.load('text_pos.npy')
over_rgb(clean,np.full(a2.shape+(3,),255,np.float32),a2,int(tx),int(ty))
c4=np.asarray(Image.open('card4.png').convert('RGB')).astype(np.float32)
h4,w4=c4.shape[:2]; r=120
a4=np.ones((h4,w4),np.float32)
for (ys,xs) in [(slice(0,r),slice(0,r)),(slice(0,r),slice(w4-r,w4)),(slice(h4-r,h4),slice(0,r)),(slice(h4-r,h4),slice(w4-r,w4))]:
    v=c4[ys,xs].min(axis=2); a4[ys,xs]=np.clip((v-250)/5,0,1)
ca2=np.asarray(Image.fromarray((a4*255).astype(np.uint8)).resize((w4//2,h4//2),Image.BOX)).astype(np.float32)/255
cc2=np.asarray(Image.fromarray(c4.astype(np.uint8)).resize((w4//2,h4//2),Image.BOX)).astype(np.float32)
cc2=np.where(ca2[...,None]>0.02,(cc2-(1-ca2[...,None])*250)/np.maximum(ca2[...,None],0.02),255).clip(0,255)
def sc(x,y,box=(2700,1600,3300,1850)):
    t=clean.copy(); over_rgb(t,cc2,ca2,x,y)
    return np.abs(t[box[1]:box[3],box[0]:box[2]]-S[box[1]:box[3],box[0]:box[2]]).mean()
b=min((sc(x,y),x,y) for x in range(2582,2594) for y in range(1554,1566)); print('card',b)
over_rgb(clean,cc2,ca2,b[1],b[2])
Image.fromarray(clean.clip(0,255).astype(np.uint8)).save('clean_full.png')
d=np.abs(S-clean).max(axis=2)
m=np.zeros_like(d,bool); m[89:89+2258,2155:2155+1611]=True
mask=(d>6)&m
lab,n=ndimage.label(ndimage.binary_closing(mask,iterations=6))
sizes=ndimage.sum(mask,lab,range(1,n+1))
objs=ndimage.find_objects(lab)
for i in np.argsort(-sizes)[:8]:
    sl=objs[i]; print('blob',int(sizes[i]),'x',sl[1].start,sl[1].stop,'y',sl[0].start,sl[0].stop)
np.save('diff.npy',d)
