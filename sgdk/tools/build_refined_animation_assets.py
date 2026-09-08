from PIL import Image
import numpy as np
from scipy import ndimage as ndi
from pathlib import Path
import math, random, hashlib, json

ROOT=Path(__file__).resolve().parents[1]
RES=ROOT/'res'
BG_PATH=RES/'r2_menu_bg.png'
bg=Image.open(BG_PATH); bg.load()
assert bg.mode=='P' and bg.size==(320,224)
orig=np.array(bg,dtype=np.uint8)
arr=orig.copy()
pal=np.array(bg.getpalette(),dtype=np.uint8).reshape(-1,3)
PALETTE_FLAT=bg.getpalette()

# ---------------- helpers ----------------
def save_p(a,path,palette_flat):
    im=Image.fromarray(a.astype(np.uint8),mode='P')
    im.putpalette(list(map(int,palette_flat)))
    im.save(path,optimize=False)
    return im

def overlay_palette(bank):
    p=np.zeros((256,3),dtype=np.uint8)
    p[:16]=pal[bank*16:bank*16+16]
    return p.reshape(-1).tolist()

PAL0=overlay_palette(0)
PAL1=overlay_palette(1)
PAL2=overlay_palette(2)
PAL3=overlay_palette(3)

def local_fill_same_bank(a,mask,seed=1,prefer_dark=False):
    """Deterministic local inpainting preserving each 8x8 tile palette bank."""
    out=a.copy(); H,W=a.shape
    ys,xs=np.where(mask)
    tiles={}
    for y,x in zip(ys,xs): tiles.setdefault((y//8,x//8),[]).append((y,x))
    for (ty,tx),pts in tiles.items():
        y0,x0=ty*8,tx*8
        bank=int(a[y0,x0]>>4)
        cy0=max(0,y0-16); cy1=min(H,y0+24); cx0=max(0,x0-24); cx1=min(W,x0+24)
        cand=[]
        for yy in range(cy0,cy1):
            for xx in range(cx0,cx1):
                if mask[yy,xx]: continue
                v=int(a[yy,xx])
                if (v>>4)!=bank: continue
                rgb=pal[v]
                if int(rgb[0])>180 and int(rgb[1])>80 and int(rgb[2])<80: continue
                cand.append(v)
        if not cand:
            cand=[int(v) for v in a[y0:y0+8,x0:x0+8].ravel() if (int(v)>>4)==bank]
        if not cand: cand=[bank<<4]
        vals,counts=np.unique(cand,return_counts=True)
        weighted=[]
        order=np.argsort(vals & 15)
        for oi in order:
            v=int(vals[oi]); c=int(counts[oi])
            w=min(c,20)
            if prefer_dark: w += (v&15)//4
            weighted.extend([v]*max(1,w))
        for y,x in pts:
            out[y,x]=weighted[(x*17+y*31+seed*13)%len(weighted)]
    return out

# ---------------- river: true-water mask, flow follows the river tangent ----------------
old=[]
for i in range(4):
    p=RES/f'r2_river_{i}.png'; im=Image.open(p); im.load(); old.append(np.array(im,dtype=np.uint8))
seed=np.zeros((224,80),dtype=bool)
for r in old: seed |= ((r[:,:80]&15)!=0)
water_like=np.isin(orig[:,:80],np.array([4,5,6,7]+list(range(17,32)),dtype=np.uint8))
lab,n=ndi.label(water_like)
river_mask=np.zeros_like(water_like)
for label in range(1,n+1):
    comp=(lab==label)
    if int((comp&seed).sum())>=3 and int(comp.sum())>=20:
        river_mask |= comp
river_mask[63:109,49:80]=False
lab,n=ndi.label(river_mask)
for label in range(1,n+1):
    m=(lab==label)
    if int(m.sum())<20: river_mask[m]=False
river_interior=ndi.binary_erosion(river_mask,np.ones((3,3)),iterations=1,border_value=0)
neigh=ndi.convolve(river_mask.astype(np.uint8),np.ones((3,3),dtype=np.uint8),mode='constant')
river_interior |= river_mask & (neigh>=7)
river_interior[63:109,49:80]=False

for y in range(224):
    for x in range(80):
        if not river_interior[y,x]: continue
        v=int(arr[y,x]); bank=v>>4; lo=v&15
        if bank==1:
            remap={1:3,2:3,3:5,4:6,6:7}
            if lo in remap: arr[y,x]=(bank<<4)|remap[lo]
        elif bank==0:
            remap={4:5,5:6}
            if lo in remap: arr[y,x]=remap[lo]

comp_lab,comp_n=ndi.label(river_interior)
cx=np.full((224,),np.nan,dtype=float)
slope=np.zeros((224,),dtype=float)
for label in range(1,comp_n+1):
    m=(comp_lab==label)
    ys=np.where(m.any(axis=1))[0]
    if len(ys)<2: continue
    row_c=[]
    for y in ys:
        xs=np.where(m[y])[0]; row_c.append(float(xs.mean()))
    row_c=np.asarray(row_c)
    smooth=ndi.gaussian_filter1d(row_c,sigma=2.0,mode='nearest')
    grad=np.gradient(smooth)
    for y,c,g in zip(ys,smooth,grad):
        cx[y]=c; slope[y]=float(np.clip(g,-1.0,1.0))

RIVER_FRAMES=12
river_frames=[]
for phase in range(RIVER_FRAMES):
    out=np.zeros((224,112),dtype=np.uint8)
    for y in range(224):
        if np.isnan(cx[y]): continue
        for x in range(80):
            if not river_interior[y,x]: continue
            u=x-cx[y]
            s=float(y) + slope[y]*u
            q=(s-phase)%RIVER_FRAMES
            h=((x*37+y*19+int(abs(u)*11))%101)/100.0
            col=0
            if q<0.85:
                col=2 if h<0.78 else 3
            elif 0.85<=q<1.55 and h>0.35:
                col=3
            elif 5.4<q<6.0 and h>0.76:
                col=5
            elif 8.8<q<9.3 and h>0.90:
                col=6
            if col: out[y,x]=col
    out[63:109,49:80]=0
    river_frames.append(out)
    save_p(out,RES/f'r2_river_{phase}.png',PAL1)

# ---------------- static animated-object removal ----------------
rgb=np.array(bg.convert('RGB'),dtype=np.uint8)
flag_box=(296,108,320,144); x0,y0,x1,y1=flag_box
sub=rgb[y0:y1,x0:x1]
redish=(sub[:,:,0] > sub[:,:,1]*1.20) & (sub[:,:,0]>68) & (sub[:,:,2] < sub[:,:,1]*0.90)
gyy,gxx=np.indices(redish.shape)
redish &= ((gxx+x0)>=303) & ((gyy+y0)>=114) & ((gyy+y0)<=140)
flab,fn=ndi.label(redish)
flag_local=np.zeros_like(redish)
if fn:
    best=None; bestscore=-1
    for label in range(1,fn+1):
        m=(flab==label); yy,xx=np.where(m)
        if not len(xx): continue
        score=int(m.sum()) - int(abs((xx.mean()+x0)-311)*2 + abs((yy.mean()+y0)-126))
        if score>bestscore: bestscore=score; best=m
    flag_local=best
flag_static=np.zeros_like(arr,dtype=bool)
flag_static[y0:y1,x0:x1]=flag_local
assert int(flag_static.sum())>90, int(flag_static.sum())
arr=local_fill_same_bank(arr,flag_static,seed=41,prefer_dark=False)

def darken_wreck_core(a,box,cx0,cy0,rx,ry):
    x0,y0,x1,y1=box
    out=a.copy(); changed=np.zeros_like(a,dtype=bool)
    for y in range(y0,y1):
        for x in range(x0,x1):
            if ((x-cx0)/rx)**2+((y-cy0)/ry)**2>1.0: continue
            v=int(out[y,x]); bank=v>>4; lo=v&15; r,g,b=map(int,pal[v])
            if bank==3 and r>75 and r>g+15 and b<65 and lo<=8:
                newlo={1:9,2:9,3:10,4:10,5:9,6:10,7:11,8:11}.get(lo,lo)
                out[y,x]=(bank<<4)|newlo; changed[y,x]=True
            elif bank==0 and lo in (9,10,11,12,14,15):
                out[y,x]=8 if lo<12 else 9; changed[y,x]=True
    return out,changed

arr,upper_static=darken_wreck_core(arr,(238,52,282,91),260,73,20,17)
arr,lower_static=darken_wreck_core(arr,(230,135,274,177),250,155,19,15)
for mask,seedv in ((upper_static,101),(lower_static,103)):
    grown=ndi.binary_dilation(mask,np.ones((3,3)),iterations=1) & (~mask)
    warm=np.zeros_like(mask)
    ys,xs=np.where(grown)
    for y,x in zip(ys,xs):
        v=int(arr[y,x]); r,g,b=map(int,pal[v])
        if r>95 and r>g+20 and b<70: warm[y,x]=True
    arr=local_fill_same_bank(arr,warm,seed=seedv,prefer_dark=True)

# ---------------- flag: 12 smooth frames from the real original cloth ----------------
FLAG_FRAMES=12
fx0,fy0=(288,104)
cloth_points=[]
ys,xs=np.where(flag_static)
for gy,gx in zip(ys,xs):
    if fx0<=gx<fx0+32 and fy0<=gy<fy0+40:
        cloth_points.append((gx-fx0,gy-fy0,int(orig[gy,gx]&15)))
assert len(cloth_points)>90
anchor_x=min(x for x,y,v in cloth_points)
free_x=max(x for x,y,v in cloth_points)
flag_frames=[]
for phase in range(FLAG_FRAMES):
    a=np.zeros((40,32),dtype=np.uint8)
    theta=2*math.pi*phase/FLAG_FRAMES
    by_col={}
    for x,y,v in cloth_points: by_col.setdefault(x,[]).append((y,v))
    for x,pts in by_col.items():
        f=(x-anchor_x)/max(1,free_x-anchor_x)
        dy=int(round(math.sin(theta + (x-anchor_x)*0.42)*1.25*f))
        dx=int(round(math.sin(theta)*0.85*f))
        tx=x+dx
        for y,v in pts:
            ty=y+dy
            if 0<=tx<32 and 0<=ty<40:
                a[ty,tx]=v
                if f>0.55 and ty+1<40 and ((x+y+phase)&7)==0:
                    a[ty+1,tx]=v
    flag_frames.append(a)
    save_p(a,RES/f'r2_flag_right_{phase}.png',PAL3)

# ---------------- fires: irregular multi-tongue silhouettes ----------------
def make_fire_frames(size,center_x,base_y,prefix,seed,top=True):
    W,H=size; frames=[]
    tongues=[(-4,0.95,0.55,0.2),(2,1.00,0.62,1.7),(6,0.72,0.46,3.0)] if top else [(-3,0.82,0.48,0.5),(2,1.00,0.55,2.2),(5,0.62,0.40,3.4)]
    maxh=29 if top else 18
    for phase in range(8):
        a=np.zeros((H,W),dtype=np.uint8)
        t=2*math.pi*phase/8
        scores=np.full((H,W),99.0,dtype=float)
        levels=np.zeros((H,W),dtype=float)
        for off,hscale,wscale,ph in tongues:
            height=maxh*hscale*(0.94+0.07*math.sin(t+ph))
            for y in range(max(0,int(base_y-height)-2),min(H,base_y+1)):
                rel=(base_y-y)/max(1.0,height)
                if rel<0 or rel>1.08: continue
                sway=math.sin(t+ph+rel*3.7)*(1.4 if top else 1.0)
                c=center_x+off+sway
                half=max(0.8,(8.0 if top else 6.0)*wscale*max(0.0,1-rel)**0.62)
                for x in range(max(0,int(c-half-2)),min(W,int(c+half+3))):
                    nx=abs(x-c)/half
                    d=nx + rel*0.18
                    rag=(((x*11+y*7+phase*13+seed)%17)-8)/32.0
                    d += rag*(0.18+0.2*rel)
                    if d<scores[y,x]: scores[y,x]=d; levels[y,x]=rel
        for y in range(H):
            for x in range(W):
                d=scores[y,x]; rel=levels[y,x]
                if d>1.0: continue
                if d>0.78 or rel>0.82: col=8
                elif d>0.56 or rel>0.66: col=9
                elif d>0.34: col=10
                else: col=11 if rel>0.25 else 12
                if ((x*5+y*9+phase*7+seed)%29)==0 and d>0.42: continue
                a[y,x]=col
        for k in range(3 if top else 2):
            x=center_x + int(round(math.sin(t*1.2+k*1.8)*(5 if top else 3))) + (k-1)
            y=max(0,base_y-maxh+((phase*2+k*5)%7))
            if 0<=x<W and 0<=y<H: a[y,x]=9 if k else 10
        frames.append(a)
        save_p(a,RES/f'{prefix}_{phase}.png',PAL0)
    return frames

fire_top=make_fire_frames((40,48),20,39,'r2_fire_top',421,top=True)
fire_bottom=make_fire_frames((40,40),18,27,'r2_fire_bottom',733,top=False)

# ---------------- subtle tree movement: sparse peripheral leaves only ----------------
TREE_FRAMES=12
tx0,ty0=(272,176)
subidx=orig[ty0:ty0+48,tx0:tx0+48]
subrgb=pal[subidx]
green=((subidx>>4)==2) & (subrgb[:,:,1]>=subrgb[:,:,0]*0.90) & (subrgb[:,:,1]>subrgb[:,:,2]*1.05)
glab,gn=ndi.label(green)
large=np.zeros_like(green)
component_ids=np.zeros_like(subidx,dtype=np.int16)
newid=1
for label in range(1,gn+1):
    m=(glab==label)
    if int(m.sum())>=12:
        large|=m; component_ids[m]=newid; newid+=1
edge=large & ~ndi.binary_erosion(large,np.ones((3,3)),iterations=1,border_value=0)
yy,xx=np.indices(edge.shape)
selected=edge & (((xx*13+yy*7)%5)<=1)
selected &= (yy>=10)
selected &= ((subidx>>4)==2)
assert int(selected.sum())>=25, int(selected.sum())
tree_static=np.zeros_like(arr,dtype=bool)
tree_static[ty0:ty0+48,tx0:tx0+48]=selected
arr=local_fill_same_bank(arr,tree_static,seed=909,prefer_dark=False)

tree_points=[]
sy,sx=np.where(selected)
for y,x in zip(sy,sx): tree_points.append((x,y,int(subidx[y,x]&15),int(component_ids[y,x])))
tree_frames=[]
for phase in range(TREE_FRAMES):
    a=np.zeros((48,48),dtype=np.uint8)
    for x,y,v,cid in tree_points:
        th=2*math.pi*phase/TREE_FRAMES + cid*0.85
        dx=int(round(math.sin(th)*0.85))
        dy=int(round(math.sin(th+1.3)*0.45)) if ((x+y+cid)%7)==0 else 0
        nx=x+dx; ny=y+dy
        if 0<=nx<48 and 0<=ny<48: a[ny,nx]=v
    tree_frames.append(a)
    save_p(a,RES/f'r2_trees_{phase}.png',PAL2)

new_bg=save_p(arr,BG_PATH,PALETTE_FLAT)
assert new_bg.getpalette()==PALETTE_FLAT

# ---------------- diagnostics ----------------
def frame_diffs(frames):
    return [int((frames[i]!=frames[(i+1)%len(frames)]).sum()) for i in range(len(frames))]

def warm_pixels(a,box):
    x0,y0,x1,y1=box; sub=pal[a[y0:y1,x0:x1]]
    return int(((sub[:,:,0]>85)&(sub[:,:,0]>sub[:,:,1]+15)&(sub[:,:,2]<75)).sum())

changed=(arr!=orig)
allowed_change=np.zeros_like(changed)
allowed_change[:,:80]|=river_interior
allowed_change|=flag_static|upper_static|lower_static|tree_static
allowed_change[50:93,236:284]=True
allowed_change[133:179,228:276]=True
assert not np.any(changed & ~allowed_change), int((changed & ~allowed_change).sum())
for a in river_frames: assert not np.any(a[:,80:]) and not np.any(a[63:109,49:80])
for a in river_frames: assert not np.any((a[:,:80]!=0) & ~river_interior)
upper_before=warm_pixels(orig,(238,52,282,91)); upper_after=warm_pixels(arr,(238,52,282,91))
lower_before=warm_pixels(orig,(230,135,274,177)); lower_after=warm_pixels(arr,(230,135,274,177))
assert upper_after < upper_before*0.75,(upper_before,upper_after)
assert lower_after < lower_before*0.75,(lower_before,lower_after)
rd=frame_diffs(river_frames); fd=frame_diffs(flag_frames); td=frame_diffs(tree_frames)
assert min(rd)>35,rd
assert min(fd)>4,fd
assert len({a.tobytes() for a in tree_frames})>=6,td
assert max(td)>100,td
assert all(int(a.max())<=6 for a in river_frames)
assert all(int(a.max())<=15 for a in flag_frames)
assert all(int(a.max())<=12 for a in fire_top+fire_bottom)
assert all(int(a.max())<=15 for a in tree_frames)

report={
    'river_mask_pixels':int(river_interior.sum()),
    'river_frame_diffs':rd,
    'flag_static_removed_pixels':int(flag_static.sum()),
    'flag_frame_diffs':fd,
    'upper_warm_before':upper_before,'upper_warm_after':upper_after,
    'lower_warm_before':lower_before,'lower_warm_after':lower_after,
    'tree_static_removed_pixels':int(tree_static.sum()),
    'tree_frame_diffs':td,
    'background_changed_pixels':int(changed.sum()),
    'background_sha256':hashlib.sha256(BG_PATH.read_bytes()).hexdigest(),
}
(RES/'R2_REFINED_ANIM_REPORT.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
