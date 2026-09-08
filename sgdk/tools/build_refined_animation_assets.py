from PIL import Image
import numpy as np
from scipy import ndimage as ndi
from pathlib import Path
import math, random, hashlib, json

ROOT=Path(__file__).resolve().parents[1]
RES=ROOT/'res'
BG_PATH=RES/'r2_menu_bg.png'
bg=Image.open(BG_PATH)
bg.load()
assert bg.mode=='P' and bg.size==(320,224)
orig=np.array(bg, dtype=np.uint8)
arr=orig.copy()
pal=np.array(bg.getpalette(), dtype=np.uint8).reshape(-1,3)

# ---------- helpers ----------
def save_p(arr2, path, palette_flat):
    im=Image.fromarray(arr2.astype(np.uint8), mode='P')
    im.putpalette(list(map(int,palette_flat)))
    im.save(path, optimize=False)
    return im

def local_fill_same_bank(a, mask, seed=1):
    """Replace masked pixels with deterministic texture sampled nearby while preserving tile palette bank."""
    rng=random.Random(seed)
    H,W=a.shape
    out=a.copy()
    ys,xs=np.where(mask)
    # process per tile so every replacement remains in tile's palette bank
    tiles={}
    for y,x in zip(ys,xs): tiles.setdefault((y//8,x//8),[]).append((y,x))
    for (ty,tx), pts in tiles.items():
        y0,x0=ty*8,tx*8
        tile=a[y0:y0+8,x0:x0+8]
        bank=int(tile[0,0]>>4)
        # candidates from a 24px ring, same bank, not masked, avoiding bright orange/flag-like warm pixels
        cy0=max(0,y0-16); cy1=min(H,y0+24); cx0=max(0,x0-24); cx1=min(W,x0+24)
        cand=[]
        for yy in range(cy0,cy1):
            for xx in range(cx0,cx1):
                if mask[yy,xx]: continue
                v=int(a[yy,xx])
                if (v>>4)!=bank: continue
                rgb=pal[v]
                # avoid obvious bright warm/fire pixels as fill sources
                if int(rgb[0])>145 and int(rgb[1])>55 and int(rgb[2])<65: continue
                cand.append(v)
        if not cand:
            cand=[int(v) for v in tile.ravel() if (int(v)>>4)==bank]
        if not cand:
            cand=[bank<<4]
        # Prefer common tones but preserve texture variation.
        vals,counts=np.unique(cand,return_counts=True)
        weighted=[]
        for v,c in zip(vals,counts): weighted.extend([int(v)]*min(int(c),20))
        for y,x in pts:
            # spatially deterministic choose based on coords
            idx=(x*17+y*31+seed*13) % len(weighted)
            out[y,x]=weighted[idx]
    return out

# ---------- river geometry and static base ----------
# Current working river frames; current r2_river_2 on main equals frame 0.
river_paths=[RES/f'r2_river_{i}.png' for i in range(4)]
river_imgs=[]
for i,p in enumerate(river_paths):
    im=Image.open(p); im.load(); river_imgs.append(np.array(im,dtype=np.uint8))
river_imgs[2]=river_imgs[0].copy()
union=np.zeros((224,112),bool)
for r in river_imgs:
    union |= ((r & 15)!=0)

# Water-like pixels in accepted background. These are the actual blue banks/tones used by the scene.
base112=orig[:,:112]
water_like=np.isin(base112, np.array([4,5,6,7]+list(range(17,32)),dtype=np.uint8))
strict=union & water_like
# Never animate the wooden bridge. Preserve a margin to stop blue fringe touching its edges.
strict[66:106,54:82]=False
# Do not animate isolated single pixels / false positives on buildings or terrain.
lab,n=ndi.label(strict)
for label in range(1,n+1):
    m=(lab==label)
    if m.sum()<10: strict[m]=False
# Erode only one pixel so the shoreline itself stays completely static.
interior=ndi.binary_erosion(strict, structure=np.ones((3,3)), iterations=1, border_value=0)
# Keep narrow river channels by retaining pixels with at least 5 water neighbours.
neigh=ndi.convolve(strict.astype(np.uint8), np.ones((3,3),dtype=np.uint8), mode='constant')
interior |= strict & (neigh>=7)
# Final explicit exclusions around upper-left structures and menu/bridge contacts.
interior[66:106,54:82]=False

# Neutralize only the moving highlights in static water, leaving shoreline and dark depth intact.
for y in range(224):
    for x in range(112):
        if not interior[y,x]: continue
        v=int(arr[y,x]); b=v>>4; lo=v&15
        if b==1:
            # bright blues -> mid/deep blues in same PAL1
            remap={1:5,2:3,3:5,4:6,6:7}
            if lo in remap: arr[y,x]=(b<<4)|remap[lo]
        elif b==0:
            remap={4:5,5:6}
            if lo in remap: arr[y,x]=remap[lo]

# ---------- remove static right flag cloth ----------
flag_static_mask=np.zeros_like(arr,dtype=bool)
# Cloth only; keep pole at x~300-302 untouched.
flag_static_mask[115:140,303:320]=True
# Narrow the top/bottom edges to the cloth silhouette and avoid unnecessary terrain replacement.
# Any very green PAL2 pixels in the rectangle are terrain, not cloth: keep them.
flag_static_mask &= ((orig>>4)==3)
arr=local_fill_same_bank(arr, flag_static_mask, seed=41)

# ---------- remove static lower fire/glow ----------
lower_box=(236,139,272,164)
lx0,ly0,lx1,ly1=lower_box
sub_rgb=pal[orig[ly0:ly1,lx0:lx1]]
# Warm/glowing pixels around the lower wreck; dark chassis remains static.
warm=(sub_rgb[:,:,0] > 120) & (sub_rgb[:,:,1] > 55) & (sub_rgb[:,:,1] < 145) & (sub_rgb[:,:,2] < 70)
# Also remove the brightest tan/orange cluster only near the centre, not road/ground outside wreck.
yy,xx=np.indices(warm.shape)
center=((xx-16)/18)**2+((yy-12)/11)**2 <= 1.0
warm &= center
lower_static_mask=np.zeros_like(arr,dtype=bool)
lower_static_mask[ly0:ly1,lx0:lx1]=warm
arr=local_fill_same_bank(arr, lower_static_mask, seed=77)

# Save refined static background using exactly the accepted palette.
new_bg=save_p(arr, BG_PATH, bg.getpalette())
assert new_bg.getpalette()==bg.getpalette()

# ---------- palette constructors for dedicated overlays ----------
def overlay_palette_from_bank(bank):
    p=np.zeros((256,3),dtype=np.uint8)
    p[:16]=pal[bank*16:bank*16+16]
    # fill remainder with zeros; only low nibble used in these resources
    return p.reshape(-1).tolist()

pal0=overlay_palette_from_bank(0)
pal1=overlay_palette_from_bank(1)
pal3=overlay_palette_from_bank(3)

# ---------- 8-frame refined river ----------
# Texture is generated from local scene detail, but constrained by the fixed interior mask.
# Lower-nibble palette 1..15 maps to existing PAL1 in runtime.
H,W=224,112
# local deterministic hash field; repeated vertically every 8 px for a seamless 8-frame downward cycle.
def hash01(x,y):
    z=(x*1103515245 + y*12345 + (x*y+97)*2654435761) & 0xffffffff
    z ^= z>>16; z=(z*2246822519)&0xffffffff; z ^= z>>13
    return (z & 0xffff)/65535.0

river_frames=[]
for phase in range(8):
    out=np.zeros((H,W),dtype=np.uint8)
    for y in range(H):
        for x in range(W):
            if not interior[y,x]: continue
            # Strict downward phase: pattern coordinate moves from y-phase.
            py=(y-phase) & 7
            h=hash01(x, (y-phase)//8)
            # Fine horizontal ripple lines with sparse brighter crests.
            wave=(py + (x//5) + (1 if h>0.72 else 0)) & 7
            if wave==0:
                col=2 if h<0.78 else 1   # light/mid blue, sparse bright crest
            elif wave in (1,7) and h>0.36:
                col=3 if h<0.82 else 2
            elif wave==4 and h>0.68:
                col=5
            elif h>0.93:
                col=6
            else:
                continue
            out[y,x]=col
    # No animation on bridge, regardless of any prior mask calculation.
    out[66:106,54:82]=0
    river_frames.append(out)
    save_p(out, RES/f'r2_river_{phase}.png', pal1)

# ---------- fire generator ----------
def make_fire_frames(size, center_x, base_y, height, width, prefix, palette_flat, seed, smoke=True):
    W,H=size
    frames=[]
    for phase in range(8):
        a=np.zeros((H,W),dtype=np.uint8)
        rng=random.Random(seed+phase*101)
        # Core flame: narrower toward the top; phase shifts asymmetrically by 1px.
        for y in range(base_y-height, base_y+1):
            rel=(base_y-y)/max(1,height)
            half=max(1, int((width/2)*(1-rel*0.72)))
            sway=int(round(math.sin(phase*math.pi/4 + rel*4.2)*1.4))
            cx=center_x+sway
            for x in range(max(0,cx-half), min(W,cx+half+1)):
                dx=abs(x-cx)/max(1,half)
                edge=dx + rel*0.20
                # ragged pixel-art edge, deterministic by phase/position
                if edge>0.92 and ((x*7+y*11+phase*5+seed)&3)!=0: continue
                # muted warm tones: avoid over-bright animation.
                if rel<0.30 and dx<0.35:
                    col=12 if ((x+y+phase)&3) else 14
                elif rel<0.58 and dx<0.55:
                    col=11
                elif rel<0.78:
                    col=10
                else:
                    col=9 if dx<0.75 else 8
                a[y,x]=col
        # Split/tongue pixels near top for natural flicker.
        tipy=max(1,base_y-height)
        for k in range(3):
            tx=center_x + int(round(math.sin((phase+k)*0.9)*3)) + (k-1)*2
            ty=tipy + ((phase*2+k*3) % 7)
            if 0<=tx<W and 0<=ty<H: a[ty,tx]=10 if k else 11
        if smoke:
            # Very sparse muted smoke/ember pixels; no white/yellow halo.
            for k in range(4):
                sx=center_x + int(round(math.sin(phase*0.7+k)*5))
                sy=max(0,tipy-4-k*3 + ((phase+k)&1))
                if 0<=sx<W and 0<=sy<H: a[sy,sx]=13  # muted grey-brown in PAL0
        frames.append(a)
        save_p(a, RES/f'{prefix}_{phase}.png', palette_flat)
    return frames

# Upper fire: substantially larger than previous 32x40 flame, but anchored to the existing wreck.
upper_fire=make_fire_frames((40,48), 20, 39, 28, 18, 'r2_fire_top', pal0, 121, smoke=True)
# Lower fire: separate phase/source, smaller and lower intensity.
lower_fire=make_fire_frames((40,40), 18, 25, 16, 14, 'r2_fire_bottom', pal0, 311, smoke=False)

# ---------- 8-frame right flag ----------
def make_flag_frames():
    W,H=32,40
    frames=[]
    for phase in range(8):
        a=np.zeros((H,W),dtype=np.uint8)
        # flag attaches at x=15, y=11..31; pole itself stays on static BG.
        top=11; fh=21; left_anchor=15
        for ry in range(fh):
            y=top+ry
            # wave grows toward free edge but anchor remains fixed
            row_sway=int(round(math.sin(phase*math.pi/4 + ry*0.42)*1.0))
            base_right=30 - (1 if ry>17 else 0)
            for x in range(left_anchor, base_right+1):
                # keep first 2 columns anchored; free edge waves by shifting texture and silhouette
                local=x-left_anchor
                free_factor=local/max(1,base_right-left_anchor)
                shift=int(round(row_sway*free_factor*1.8))
                xx=x+shift
                if xx<left_anchor or xx>=W: continue
                # wavy free edge
                if local>12 and ((ry+phase)&3)==0 and xx>=base_right-1: continue
                # PAL3 lower-nibble tones: dark red-brown body with muted beige emblem
                col=8  # global PAL3 index 56: brown-red
                # vertical shading/folds
                if ((local + phase) % 7)==0: col=9
                if ry in (0,fh-1) or local==0 or xx>=base_right-1: col=11
                # subtle lit fold
                if 4<=local<=7 and ((ry+phase)//4)%2==0: col=6
                # simple muted emblem, centered and deformed with cloth
                erx=local-8; ery=ry-10
                if (erx*erx + (ery*ery)//2) <= 12 and 5<=ry<=16:
                    col=1 if ((erx+ery+phase)&2) else 2
                a[y,xx]=col
        frames.append(a)
        save_p(a, RES/f'r2_flag_right_{phase}.png', pal3)
    return frames
flag_frames=make_flag_frames()

# ---------- diagnostics / invariants ----------
# No river overlay pixel may exist over bridge.
for i,a in enumerate(river_frames):
    assert not np.any(a[66:106,54:82]), i
# River is confined to strict water geometry.
for i,a in enumerate(river_frames):
    assert not np.any((a!=0) & ~interior), i
# Right flag cloth removed from static background: warm PAL3 cloth count should collapse strongly.
flag_orig=orig[115:140,303:320]
flag_new=arr[115:140,303:320]
# lower fire warm count reduced
orig_rgb=pal[orig[ly0:ly1,lx0:lx1]]; new_rgb=pal[arr[ly0:ly1,lx0:lx1]]
def warm_count(r): return int(((r[:,:,0]>120)&(r[:,:,1]>55)&(r[:,:,1]<145)&(r[:,:,2]<70)).sum())
report={
    'river_mask_pixels':int(interior.sum()),
    'river_frame_visible':[int((a!=0).sum()) for a in river_frames],
    'flag_static_changed':int((flag_orig!=flag_new).sum()),
    'lower_fire_warm_before':warm_count(orig_rgb),
    'lower_fire_warm_after':warm_count(new_rgb),
    'bg_sha256':hashlib.sha256(BG_PATH.read_bytes()).hexdigest(),
}
(RES/'R2_REFINED_ANIM_REPORT.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
