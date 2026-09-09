#!/usr/bin/env python3
from pathlib import Path
from PIL import Image
import hashlib, json, random

ROOT=Path(__file__).resolve().parents[1]
RES=ROOT/'res'
SOURCE=Image.open(RES/'r2_menu_bg.png'); SOURCE.load()
SRC_PAL=SOURCE.getpalette()

T=8
WORLD_COLS=16
WORLD_ROWS=8
WORLD_COUNT=WORLD_COLS*WORLD_ROWS
HUD_COLS=8
HUD_ROWS=8
HUD_COUNT=HUD_COLS*HUD_ROWS

# R3 world tile IDs. Tile zero is intentionally transparent for Plane A.
BLANK=0
GRASS_BASE=1; GRASS_COUNT=16
ROAD_BASE=17; ROAD_COUNT=12
WATER_BASE=29; WATER_COUNT=8
SHORE_BASE=37; SHORE_COUNT=8
DECOR_BASE=45; DECOR_COUNT=8
BRIDGE_BASE=53; BRIDGE_COUNT=8
STRUCT_BASE=61; STRUCT_COUNT=12
TREE_BASE=73; TREE_FRAMES=12; TREE_QUADS=4   # 73..120
EXTRA_BASE=121; EXTRA_COUNT=7
assert EXTRA_BASE+EXTRA_COUNT == WORLD_COUNT

CHARSET='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ:-/ .'
HUD_BG=0
HUD_SOLID=1
HUD_HLINE=2
HUD_VLINE=3
HUD_CORNER=4
HUD_DIAG=5
HUD_DOT=6
HUD_GLYPH_BASE=8
assert HUD_GLYPH_BASE+len(CHARSET) <= HUD_COUNT

# 5x7 font, intentionally blocky/MD-like. Missing chars fall back to blank.
FONT={
'0':['01110','10001','10011','10101','11001','10001','01110'],
'1':['00100','01100','00100','00100','00100','00100','01110'],
'2':['01110','10001','00001','00010','00100','01000','11111'],
'3':['11110','00001','00001','01110','00001','00001','11110'],
'4':['00010','00110','01010','10010','11111','00010','00010'],
'5':['11111','10000','10000','11110','00001','00001','11110'],
'6':['01110','10000','10000','11110','10001','10001','01110'],
'7':['11111','00001','00010','00100','01000','01000','01000'],
'8':['01110','10001','10001','01110','10001','10001','01110'],
'9':['01110','10001','10001','01111','00001','00001','01110'],
'A':['01110','10001','10001','11111','10001','10001','10001'],
'B':['11110','10001','10001','11110','10001','10001','11110'],
'C':['01111','10000','10000','10000','10000','10000','01111'],
'D':['11110','10001','10001','10001','10001','10001','11110'],
'E':['11111','10000','10000','11110','10000','10000','11111'],
'F':['11111','10000','10000','11110','10000','10000','10000'],
'G':['01111','10000','10000','10111','10001','10001','01111'],
'H':['10001','10001','10001','11111','10001','10001','10001'],
'I':['11111','00100','00100','00100','00100','00100','11111'],
'J':['00111','00010','00010','00010','10010','10010','01100'],
'K':['10001','10010','10100','11000','10100','10010','10001'],
'L':['10000','10000','10000','10000','10000','10000','11111'],
'M':['10001','11011','10101','10101','10001','10001','10001'],
'N':['10001','11001','10101','10011','10001','10001','10001'],
'O':['01110','10001','10001','10001','10001','10001','01110'],
'P':['11110','10001','10001','11110','10000','10000','10000'],
'Q':['01110','10001','10001','10001','10101','10010','01101'],
'R':['11110','10001','10001','11110','10100','10010','10001'],
'S':['01111','10000','10000','01110','00001','00001','11110'],
'T':['11111','00100','00100','00100','00100','00100','00100'],
'U':['10001','10001','10001','10001','10001','10001','01110'],
'V':['10001','10001','10001','10001','10001','01010','00100'],
'W':['10001','10001','10001','10101','10101','10101','01010'],
'X':['10001','10001','01010','00100','01010','10001','10001'],
'Y':['10001','10001','01010','00100','00100','00100','00100'],
'Z':['11111','00001','00010','00100','01000','10000','11111'],
':':['00000','00100','00100','00000','00100','00100','00000'],
'-':['00000','00000','00000','11111','00000','00000','00000'],
'/':['00001','00010','00010','00100','01000','01000','10000'],
'.':['00000','00000','00000','00000','00000','00100','00100'],
' ':['00000']*7,
}


def palette64(im):
    pal=im.getpalette()[:192]
    return pal + [0]*(768-len(pal))


def make_indexed(w,h):
    im=Image.new('P',(w,h),0)
    im.putpalette(palette64(SOURCE))
    return im


def put_tile(im, tid, pix, cols):
    x=(tid%cols)*T; y=(tid//cols)*T
    assert len(pix)==64
    for yy in range(8):
        for xx in range(8):
            im.putpixel((x+xx,y+yy), int(pix[yy*8+xx]) & 15)


def noise_tile(base, lights, shadows, seed, density=15):
    r=random.Random(seed)
    p=[base]*64
    for _ in range(density):
        i=r.randrange(64)
        p[i]=r.choice(lights+shadows)
    # a few paired pixels make the terrain read as authored rather than static noise
    for _ in range(3):
        x=r.randrange(7); y=r.randrange(8); c=r.choice(lights+shadows)
        p[y*8+x]=c; p[y*8+x+1]=c
    return p


def water_tile(frame):
    p=[5]*64   # PAL1 local 5 = dark steel-blue
    # horizontal glints drift slowly; phase variation is deterministic
    for y in (1,4,6):
        start=(frame*2 + y*3) & 7
        for k in range(3):
            x=(start+k) & 7
            p[y*8+x]=1 if k==1 else 4
    for x in range(8):
        if ((x+frame)&7)==0: p[3*8+x]=8
    return p


def shore_tile(seed):
    r=random.Random(seed)
    p=[4]*64 # PAL3 local 4 earth/olive
    for y in range(8):
        edge=2 + ((y+seed)&1)
        for x in range(edge): p[y*8+x]=6 if (x+y)&1 else 9
        if edge<8: p[y*8+edge]=1
    for _ in range(8): p[r.randrange(64)]=r.choice([2,5,7,10])
    return p


def bridge_tile(seed):
    p=[6]*64
    # wooden planks + dark joins
    for y in range(8):
        for x in range(8):
            p[y*8+x]=4 if ((x+seed)//2)&1 else 1
    for x in range(8):
        p[1*8+x]=9; p[6*8+x]=9
    for y in range(8):
        if (y+seed)%3==0:
            p[y*8+3]=12; p[y*8+4]=12
    return p


def structure_tile(seed):
    r=random.Random(seed)
    p=[7]*64
    for y in range(1,7):
        for x in range(1,7): p[y*8+x]=3 if (x+y+seed)&1 else 2
    for x in range(8): p[x]=6; p[7*8+x]=6
    for y in range(8): p[y*8]=6; p[y*8+7]=6
    for _ in range(5): p[r.randrange(64)]=4
    return p


def tree_frame(frame):
    # 16x16 foliage. The trunk is intentionally subtle; the accepted menu is foliage-heavy.
    g=[[0]*16 for _ in range(16)]
    cx=7 + (1 if frame in (3,4) else -1 if frame in (9,10) else 0)
    cy=7
    for y in range(16):
        for x in range(16):
            dx=x-cx; dy=y-cy
            if (dx*dx*3 + dy*dy*2) <= 105:
                v=4
                if ((x*7+y*5+frame)%11)==0: v=1
                elif ((x*3+y*7+frame)%9)==0: v=8
                elif y>9: v=10
                g[y][x]=v
    # carve irregular silhouette and make only a handful of edge pixels move
    for x,y in [(2,4),(13,5),(1,8),(14,9),(4,1),(11,2),(3,13),(12,12)]:
        phase=(x*3+y+frame)%12
        if phase in (0,1,2): g[y][x]=0
        elif phase in (6,7): g[y][x]=1
    # tiny dark trunk lower middle using dark PAL2 colors
    for y in range(11,16):
        for x in (7,8):
            if g[y][x]: g[y][x]=11
    return g


world=make_indexed(WORLD_COLS*T,WORLD_ROWS*T)
put_tile(world, BLANK, [0]*64, WORLD_COLS)
for i in range(GRASS_COUNT):
    put_tile(world, GRASS_BASE+i, noise_tile(4,[1,2,5],[8,10,11,12],100+i,18+i%5), WORLD_COLS)
for i in range(ROAD_COUNT):
    p=noise_tile(4,[1,2,5],[6,9,10,11],200+i,20)
    # wheel ruts in some variants
    if i%3==0:
        for y in range(8): p[y*8+1]=9; p[y*8+6]=9
    put_tile(world, ROAD_BASE+i,p,WORLD_COLS)
for i in range(WATER_COUNT): put_tile(world,WATER_BASE+i,water_tile(i),WORLD_COLS)
for i in range(SHORE_COUNT): put_tile(world,SHORE_BASE+i,shore_tile(300+i),WORLD_COLS)
for i in range(DECOR_COUNT):
    # rock / scrub detail, palette selected by C provider
    p=[0]*64; r=random.Random(400+i)
    cx=3+r.randrange(2); cy=4
    for y in range(8):
        for x in range(8):
            d=abs(x-cx)+abs(y-cy)
            if d<4: p[y*8+x]=3 if d<2 else (4 if (x+y+i)&1 else 2)
    put_tile(world,DECOR_BASE+i,p,WORLD_COLS)
for i in range(BRIDGE_COUNT): put_tile(world,BRIDGE_BASE+i,bridge_tile(i),WORLD_COLS)
for i in range(STRUCT_COUNT): put_tile(world,STRUCT_BASE+i,structure_tile(i),WORLD_COLS)
for frame in range(TREE_FRAMES):
    g=tree_frame(frame)
    for q in range(4):
        ox=(q&1)*8; oy=(q>>1)*8
        pix=[g[oy+y][ox+x] for y in range(8) for x in range(8)]
        put_tile(world,TREE_BASE+frame*4+q,pix,WORLD_COLS)
for i in range(EXTRA_COUNT):
    put_tile(world,EXTRA_BASE+i,noise_tile(6,[1,4],[9,10,12],500+i,25),WORLD_COLS)

world_path=RES/'r3_world_tiles.png'
world.save(world_path,optimize=False)

hud=make_indexed(HUD_COLS*T,HUD_ROWS*T)
put_tile(hud,HUD_BG,[7]*64,HUD_COLS)
put_tile(hud,HUD_SOLID,[4]*64,HUD_COLS)
p=[7]*64
for x in range(8): p[3*8+x]=4; p[4*8+x]=4
put_tile(hud,HUD_HLINE,p,HUD_COLS)
p=[7]*64
for y in range(8): p[y*8+3]=4; p[y*8+4]=4
put_tile(hud,HUD_VLINE,p,HUD_COLS)
p=[7]*64
for x in range(8): p[0*8+x]=4
for y in range(8): p[y*8+0]=4
put_tile(hud,HUD_CORNER,p,HUD_COLS)
p=[7]*64
for i in range(8): p[i*8+i]=4; p[i*8+(7-i)]=4
put_tile(hud,HUD_DIAG,p,HUD_COLS)
p=[7]*64; p[3*8+3]=15; p[3*8+4]=15; p[4*8+3]=15; p[4*8+4]=15
put_tile(hud,HUD_DOT,p,HUD_COLS)
# tile 7 reserved as another navy texture
put_tile(hud,7,noise_tile(7,[5],[6],777,5),HUD_COLS)
for ci,ch in enumerate(CHARSET):
    p=[7]*64
    glyph=FONT.get(ch,FONT[' '])
    for y,row in enumerate(glyph):
        for x,v in enumerate(row):
            if v=='1': p[(y)*8+(x+1)]=15
    put_tile(hud,HUD_GLYPH_BASE+ci,p,HUD_COLS)

hud_path=RES/'r3_hud_tiles.png'
hud.save(hud_path,optimize=False)

report={
 'world_tiles':WORLD_COUNT,'hud_tiles':HUD_COUNT,
 'world_sha256':hashlib.sha256(world_path.read_bytes()).hexdigest(),
 'hud_sha256':hashlib.sha256(hud_path.read_bytes()).hexdigest(),
 'source_r2_palette_sha256':hashlib.sha256(bytes(SRC_PAL)).hexdigest(),
 'tree_frames':TREE_FRAMES,'water_frames':WATER_COUNT,
 'charset':CHARSET,
 'palette_policy':'R3 tiles use local 0..15 indexes and select accepted R2 PAL0/PAL1/PAL2/PAL3 via tile attributes',
}
(RES/'R3_ASSET_REPORT.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
