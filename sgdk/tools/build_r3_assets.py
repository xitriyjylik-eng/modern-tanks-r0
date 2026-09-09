#!/usr/bin/env python3
from pathlib import Path
from PIL import Image, ImageDraw
import hashlib, json, math, random

ROOT=Path(__file__).resolve().parents[1]
RES=ROOT/'res'
SOURCE=Image.open(RES/'r2_menu_bg.png'); SOURCE.load(); SRC_PAL=SOURCE.getpalette()
T=8
WORLD_COLS=WORLD_ROWS=32; WORLD_COUNT=1024
HUD_COLS=16; HUD_ROWS=8; HUD_COUNT=128

BLANK=0
GRASS_BASE=1; GRASS_META=12; GRASS_COUNT=192
ROAD_BASE=193; ROAD_META=8; ROAD_COUNT=128
WATER_BASE=321; WATER_VARIANTS=3; WATER_FRAMES=8; WATER_COUNT=96
SHORE_BASE=417; SHORE_META=6; SHORE_COUNT=96
BRIDGE_BASE=513; BRIDGE_META=4; BRIDGE_COUNT=64
DECOR_BASE=577; DECOR_META=24; DECOR_COUNT=96
STRUCT_BASE=673; STRUCT_VARIANTS=8; STRUCT_COUNT=96
TREE_BASE=769; TREE_FRAMES=12; TREE_W=4; TREE_H=3; TREE_COUNT=144
EXTRA_BASE=913; EXTRA_COUNT=111
assert EXTRA_BASE+EXTRA_COUNT==WORLD_COUNT

CHARSET='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ:-/ .'
HT_BG=0; HT_SOLID=1; HT_HLINE=2; HT_VLINE=3; HT_CORNER=4; HT_DIAG=5; HT_DOT=6; HT_RIVET=7
HT_GLYPH_BASE=8
assert HT_GLYPH_BASE+len(CHARSET)<=HUD_COUNT

FONT={
'0':['01110','10001','10011','10101','11001','10001','01110'],'1':['00100','01100','00100','00100','00100','00100','01110'],
'2':['01110','10001','00001','00010','00100','01000','11111'],'3':['11110','00001','00001','01110','00001','00001','11110'],
'4':['00010','00110','01010','10010','11111','00010','00010'],'5':['11111','10000','10000','11110','00001','00001','11110'],
'6':['01110','10000','10000','11110','10001','10001','01110'],'7':['11111','00001','00010','00100','01000','01000','01000'],
'8':['01110','10001','10001','01110','10001','10001','01110'],'9':['01110','10001','10001','01111','00001','00001','01110'],
'A':['01110','10001','10001','11111','10001','10001','10001'],'B':['11110','10001','10001','11110','10001','10001','11110'],
'C':['01111','10000','10000','10000','10000','10000','01111'],'D':['11110','10001','10001','10001','10001','10001','11110'],
'E':['11111','10000','10000','11110','10000','10000','11111'],'F':['11111','10000','10000','11110','10000','10000','10000'],
'G':['01111','10000','10000','10111','10001','10001','01111'],'H':['10001','10001','10001','11111','10001','10001','10001'],
'I':['11111','00100','00100','00100','00100','00100','11111'],'J':['00111','00010','00010','00010','10010','10010','01100'],
'K':['10001','10010','10100','11000','10100','10010','10001'],'L':['10000','10000','10000','10000','10000','10000','11111'],
'M':['10001','11011','10101','10101','10001','10001','10001'],'N':['10001','11001','10101','10011','10001','10001','10001'],
'O':['01110','10001','10001','10001','10001','10001','01110'],'P':['11110','10001','10001','11110','10000','10000','10000'],
'Q':['01110','10001','10001','10001','10101','10010','01101'],'R':['11110','10001','10001','11110','10100','10010','10001'],
'S':['01111','10000','10000','01110','00001','00001','11110'],'T':['11111','00100','00100','00100','00100','00100','00100'],
'U':['10001','10001','10001','10001','10001','10001','01110'],'V':['10001','10001','10001','10001','10001','01010','00100'],
'W':['10001','10001','10001','10101','10101','10101','01010'],'X':['10001','10001','01010','00100','01010','10001','10001'],
'Y':['10001','10001','01010','00100','00100','00100','00100'],'Z':['11111','00001','00010','00100','01000','10000','11111'],
':':['00000','00100','00100','00000','00100','00100','00000'],'-':['00000','00000','00000','11111','00000','00000','00000'],
'/':['00001','00010','00010','00100','01000','01000','10000'],'.':['00000','00000','00000','00000','00000','00100','00100'],
' ':['00000']*7,
}

def palette_flat():
    p=SRC_PAL[:192]
    return p+[0]*(768-len(p))
def pimg(w,h,fill=0):
    im=Image.new('P',(w,h),fill); im.putpalette(palette_flat()); return im
def put_tile(atlas,tid,pix,cols):
    x=(tid%cols)*8; y=(tid//cols)*8
    for yy in range(8):
        for xx in range(8): atlas.putpixel((x+xx,y+yy),int(pix[yy][xx] if isinstance(pix[0],list) else pix[yy*8+xx])&15)
def split_put(atlas,base,im,cols,rows,atlas_cols):
    p=im.load()
    for ty in range(rows):
        for tx in range(cols):
            tile=[[p[tx*8+x,ty*8+y] for x in range(8)] for y in range(8)]
            put_tile(atlas,base+ty*cols+tx,tile,atlas_cols)
def unique_tiles(im):
    return len({bytes(im.crop((x,y,x+8,y+8)).getdata()) for y in range(0,im.height,8) for x in range(0,im.width,8)})

world=pimg(WORLD_COLS*8,WORLD_ROWS*8,0); put_tile(world,BLANK,[[0]*8 for _ in range(8)],WORLD_COLS)

for v in range(GRASS_META):
    r=random.Random(1000+v); im=pimg(32,32,4+(v%3)); d=ImageDraw.Draw(im)
    for _ in range(18):
        x=r.randrange(-4,32); y=r.randrange(-4,32); rr=r.choice([1,2,3,4,5]); c=r.choice([1,2,3,5,6,7,8,9,10,11,12]); d.ellipse((x-rr,y-rr,x+rr,y+rr),fill=c)
    for _ in range(44):
        x=r.randrange(1,31); y=r.randrange(1,31); c=r.choice([1,2,7,8,10,11]); d.point((x,y),fill=c)
        if r.random()<.45:d.point((x,y-1),fill=c)
        if r.random()<.18:d.point((x+1,y),fill=c)
    for _ in range(10):
        x=r.randrange(2,30); y=r.randrange(2,30); c=r.choice([9,10,12,13]); d.rectangle((x,y,x+r.randrange(1,3),y+r.randrange(0,2)),fill=c)
    split_put(world,GRASS_BASE+v*16,im,4,4,WORLD_COLS)

for v in range(ROAD_META):
    r=random.Random(2000+v); im=pimg(32,32,r.choice([2,3,4,5])); d=ImageDraw.Draw(im)
    for _ in range(26):
        x=r.randrange(-3,32); y=r.randrange(-3,32); w=r.randrange(1,6); h=r.randrange(1,4); c=r.choice([1,2,3,4,5,6,7,8,9,10,11,12]); d.ellipse((x,y,x+w,y+h),fill=c)
    for yy in (8+(v%3),23-((v+1)%3)):
        for x in range(32):
            if (x+r.randrange(3))%4:d.point((x,yy),fill=r.choice([8,9,10,11]))
            if r.random()<.25 and yy+1<32:d.point((x,yy+1),fill=6)
    for _ in range(9):
        x=r.randrange(1,30); y=r.randrange(1,30); c=r.choice([1,6,9,12]); d.rectangle((x,y,x+1,y+1),fill=c)
    split_put(world,ROAD_BASE+v*16,im,4,4,WORLD_COLS)

for var in range(WATER_VARIANTS):
    for frame in range(WATER_FRAMES):
        im=pimg(16,16,5); d=ImageDraw.Draw(im); r=random.Random(3000+var*100+frame)
        for _ in range(14): d.point((r.randrange(16),r.randrange(16)),fill=r.choice([3,4,6,7,9,10,13]))
        for band in range(4):
            y=(2+band*4+(var&1))%16; start=(frame*2+band*5+var*3)%16; length=3+((band+var)%3)
            for t in range(length):
                x=(start+t)%16; d.point((x,y),fill=1 if t in (1,2) else 2)
                if t==1 and (band+frame)%2==0 and y+1<16:d.point((x,y+1),fill=4)
        split_put(world,WATER_BASE+(var*WATER_FRAMES+frame)*4,im,2,2,WORLD_COLS)

for m in range(SHORE_META):
    side=0 if m<3 else 1; var=m%3; r=random.Random(4000+m); im=pimg(32,32,4); d=ImageDraw.Draw(im)
    for _ in range(35):
        x=r.randrange(32); y=r.randrange(32); c=r.choice([1,2,3,5,6,7,8,9,10,11,12,13]); rr=r.choice([0,0,1,2]); d.ellipse((x-rr,y-rr,x+rr,y+rr),fill=c)
    xbase=28 if side==0 else 3
    for y in range(32):
        x=xbase+int(2*math.sin((y+var*5)/5))
        for dx in (-1,0,1):
            xx=x+dx
            if 0<=xx<32:d.point((xx,y),fill=9 if dx else 12)
    split_put(world,SHORE_BASE+m*16,im,4,4,WORLD_COLS)

for m in range(BRIDGE_META):
    im=pimg(32,32,3); d=ImageDraw.Draw(im)
    for y in range(32): d.line((0,y,31,y),fill=2 if ((y//4+m)&1)==0 else 5)
    for y in range(3,32,5): d.line((0,y,31,y),fill=9)
    for x in range(2+m%2,32,6):
        d.line((x,0,x,31),fill=6)
        for y in (3,27):d.rectangle((x,y,x+1,y+1),fill=1)
    d.line((0,2,31,2),fill=12); d.line((0,29,31,29),fill=12)
    split_put(world,BRIDGE_BASE+m*16,im,4,4,WORLD_COLS)

for m in range(DECOR_META):
    im=pimg(16,16,0); d=ImageDraw.Draw(im); r=random.Random(6000+m)
    if m<12:
        cx=7+r.randrange(-2,3); cy=9+r.randrange(-1,2); rx=r.randrange(3,6); ry=r.randrange(2,5); d.ellipse((cx-rx,cy-ry,cx+rx,cy+ry),fill=3); d.polygon([(cx-rx+1,cy),(cx-1,cy-ry),(cx+rx-1,cy-1),(cx+1,cy+ry)],fill=13); d.line((cx-rx+2,cy-1,cx,cy-ry+1),fill=2)
        if m%3==0:d.point((cx+2,cy-2),fill=1)
    else:
        for _ in range(5):
            cx=r.randrange(3,13); cy=r.randrange(4,12); rr=r.randrange(2,5); d.ellipse((cx-rr,cy-rr,cx+rr,cy+rr),fill=r.choice([3,4,7,8,10,11]))
        for _ in range(12):d.point((r.randrange(2,14),r.randrange(2,14)),fill=r.choice([1,2,6,12]))
    split_put(world,DECOR_BASE+m*4,im,2,2,WORLD_COLS)

for m in range(STRUCT_VARIANTS):
    im=pimg(32,24,0); d=ImageDraw.Draw(im); r=random.Random(7000+m); d.ellipse((3,17,29,23),fill=13); roof=r.choice([8,9,11,12,13]); d.polygon([(2,9),(9,2),(23,2),(30,9)],fill=roof); d.line((2,9,30,9),fill=15); wall=r.choice([1,2,3,5,6]); d.rectangle((5,9,27,21),fill=wall)
    for y in range(11,21,4):d.line((6,y,26,y),fill=r.choice([6,9,10,11]))
    dx=7+(m%3)*6; d.rectangle((dx,14,dx+5,21),fill=11); wx=20 if dx<15 else 8; d.rectangle((wx,12,wx+5,16),fill=1); d.rectangle((wx+1,13,wx+4,15),fill=14 if m%2==0 else 3)
    for _ in range(14):d.point((r.randrange(5,28),r.randrange(3,9)),fill=r.choice([8,9,10,11,12,13,15]))
    split_put(world,STRUCT_BASE+m*12,im,4,3,WORLD_COLS)

def tree_frame(frame):
    im=pimg(32,24,0); d=ImageDraw.Draw(im); d.rectangle((14,13,17,23),fill=11); d.rectangle((15,14,16,23),fill=9); centers=[(9,10,7),(15,7,8),(22,10,7),(14,13,8),(20,14,6),(7,14,5)]; sway=1 if frame in (2,3,4) else -1 if frame in (8,9,10) else 0; r=random.Random(8000+frame)
    for idx,(cx,cy,rr) in enumerate(centers):
        sx=sway if idx in (0,2,5) else 0; c=[4,5,7,8,10,11][idx]; d.ellipse((cx-rr+sx,cy-rr,cx+rr+sx,cy+rr),fill=c); d.ellipse((cx-rr//2+sx,cy-rr//2,cx+rr//2+sx,cy+rr//2),fill=max(1,c-3))
    for k in range(30):
        ang=(k*37+frame*5)%360; rr=9+(k%4); x=16+int(math.cos(math.radians(ang))*rr); y=11+int(math.sin(math.radians(ang))*rr*.7)
        if 0<=x<32 and 0<=y<22:
            if ((k+frame)%7)==0:d.point((x,y),fill=0)
            elif ((k*3+frame)%5)==0:d.point((x,y),fill=1)
    for _ in range(24):
        x=r.randrange(5,27); y=r.randrange(2,18)
        if im.getpixel((x,y))!=0:d.point((x,y),fill=r.choice([1,2,3,6,12]))
    return im
for f in range(TREE_FRAMES):split_put(world,TREE_BASE+f*12,tree_frame(f),4,3,WORLD_COLS)

for i in range(EXTRA_COUNT):
    r=random.Random(9000+i); a=[[0]*8 for _ in range(8)]; typ=i%3
    if typ==0:
        for y in range(8):
            for x in range(8):a[y][x]=4 if ((x+y+i)&3) else 7
        for x in range(i%4,8,4):
            for y in range(8):a[y][x]=10
    elif typ==1:
        for y in (2,5):
            for x in range(8):a[y][x]=6 if x%2 else 1
        for x in (1,6):
            for y in range(8):a[y][x]=9
    else:
        for y in range(8):
            for x in range(8):a[y][x]=r.choice([4,4,5,6,7,8])
        for _ in range(7):a[r.randrange(8)][r.randrange(8)]=r.choice([1,2,10,11])
    put_tile(world,EXTRA_BASE+i,a,WORLD_COLS)

hud=pimg(HUD_COLS*8,HUD_ROWS*8,0)
def hudtile(tid,a):put_tile(hud,tid,a,HUD_COLS)
a=[[7]*8 for _ in range(8)]
for y in range(8):
    for x in range(8):
        if ((x*3+y*5)&15)==0:a[y][x]=6
hudtile(HT_BG,a)
a=[[5 if 1<=x<=6 and 1<=y<=6 else 6 for x in range(8)] for y in range(8)];hudtile(HT_SOLID,a)
a=[[7]*8 for _ in range(8)]
for x in range(8):a[2][x]=3;a[3][x]=2;a[4][x]=6;a[5][x]=5
hudtile(HT_HLINE,a)
a=[[7]*8 for _ in range(8)]
for y in range(8):a[y][2]=3;a[y][3]=2;a[y][4]=6;a[y][5]=5
hudtile(HT_VLINE,a)
a=[[7]*8 for _ in range(8)]
for x in range(8):a[1][x]=3;a[2][x]=2
for y in range(8):a[y][1]=3;a[y][2]=2
hudtile(HT_CORNER,a)
a=[[7]*8 for _ in range(8)]
for i in range(8):a[i][i]=3;a[i][7-i]=5
hudtile(HT_DIAG,a)
a=[[7]*8 for _ in range(8)]
for y in (3,4):
    for x in (3,4):a[y][x]=15
hudtile(HT_DOT,a)
a=[[7]*8 for _ in range(8)];a[2][2]=3;a[2][5]=3;a[5][2]=3;a[5][5]=3;hudtile(HT_RIVET,a)
for ci,ch in enumerate(CHARSET):
    a=[[7]*8 for _ in range(8)]
    for y,row in enumerate(FONT.get(ch,FONT[' '])):
        for x,v in enumerate(row):
            if v=='1':a[y][x+1]=15
    hudtile(HT_GLYPH_BASE+ci,a)
for tid in range(HT_GLYPH_BASE+len(CHARSET),HUD_COUNT):
    r=random.Random(10000+tid); a=[[7]*8 for _ in range(8)]
    for _ in range(7):a[r.randrange(8)][r.randrange(8)]=r.choice([3,4,5,6,13,15])
    hudtile(tid,a)

world_path=RES/'r3_world_tiles.png'; hud_path=RES/'r3_hud_tiles.png'; world.save(world_path,optimize=False); hud.save(hud_path,optimize=False)
report={'world_tiles':WORLD_COUNT,'hud_tiles':HUD_COUNT,'world_unique_tiles':unique_tiles(world),'hud_unique_tiles':unique_tiles(hud),'world_pattern_bytes':WORLD_COUNT*32,'hud_pattern_bytes':HUD_COUNT*32,'total_r3_pattern_bytes':(WORLD_COUNT+HUD_COUNT)*32,'world_sha256':hashlib.sha256(world_path.read_bytes()).hexdigest(),'hud_sha256':hashlib.sha256(hud_path.read_bytes()).hexdigest(),'source_r2_palette_sha256':hashlib.sha256(bytes(SRC_PAL)).hexdigest(),'tree_frames':TREE_FRAMES,'water_frames':WATER_FRAMES,'tree_footprint':'32x24','ground_metatile':'32x32','palette_policy':'Exact accepted R2 palette; PAL0 steel/stone, PAL1 water, PAL2 foliage, PAL3 earth/wood.'}
(RES/'R3_ASSET_REPORT.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))
