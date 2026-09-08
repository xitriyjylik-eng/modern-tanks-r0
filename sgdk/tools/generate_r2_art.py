from PIL import Image, ImageDraw, ImageFont
import os, math
W,H=320,224
OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'res'))
os.makedirs(OUT, exist_ok=True)
# Palette 0: battlefield (16 colors)
p0=[
(0,0,0),(7,14,13),(12,45,25),(20,77,35),(42,119,45),(65,41,24),(104,61,32),(152,93,45),
(16,64,117),(18,111,174),(50,172,225),(71,78,82),(157,169,164),(171,51,30),(244,126,27),(248,232,135)]
# Palette 1: logo steel/orange
p1=[
(0,0,0),(4,10,17),(12,24,37),(27,45,61),(53,71,86),(89,105,116),(140,151,156),(205,211,209),
(86,42,18),(138,62,19),(195,81,18),(235,110,23),(255,149,28),(255,190,58),(97,103,106),(245,240,210)]
# Palette 2: menu panel / selector
p2=[
(0,0,0),(3,10,17),(8,23,34),(15,39,53),(30,62,76),(65,92,103),(135,154,159),(224,231,225),
(44,123,74),(55,196,102),(127,139,145),(203,211,208),(152,127,27),(240,217,54),(199,68,39),(255,246,176)]
# Palette 3: lower HUD
p3=[
(0,0,0),(4,11,18),(9,25,36),(16,42,55),(35,66,80),(83,105,113),(159,173,175),(229,235,226),
(44,122,72),(63,191,101),(72,103,136),(211,153,42),(184,49,38),(240,73,45),(45,143,192),(250,220,61)]
pals=[p0,p1,p2,p3]
palette=[]
for pal in pals:
    for c in pal: palette.extend(c)
palette += [0,0,0]*(256-64)
def idx(p,c): return p*16+c
img=Image.new('P',(W,H),idx(0,1)); img.putpalette(palette)
d=ImageDraw.Draw(img)
# fonts
font_bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
font_mono='/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'
logo_modern=ImageFont.truetype(font_bold,21)
logo_tanks=ImageFont.truetype(font_bold,31)
menu_font=ImageFont.truetype(font_mono,11)
small=ImageFont.truetype(font_mono,7)
small_b=ImageFont.truetype(font_mono,8)
mini=ImageFont.truetype(font_mono,6)

# ---- battlefield texture helpers, PAL0 only ----
def tile_fill(tx,ty,kind,v=0):
    x,y=tx*8,ty*8
    if kind=='grass':
        d.rectangle((x,y,x+7,y+7),fill=idx(0,2+(v&1)))
        pts=[(1,1),(4,1),(6,3),(2,5),(5,6)] if not (v&1) else [(2,1),(6,1),(1,3),(4,5),(7,6)]
        for px,py in pts: d.point((x+px,y+py),fill=idx(0,4))
        d.point((x+3,y+3),fill=idx(0,1))
    elif kind=='dirt':
        d.rectangle((x,y,x+7,y+7),fill=idx(0,5))
        for px,py in [(1,1),(5,2),(2,5),(6,6)]: d.point((x+px,y+py),fill=idx(0,7 if (v&1) else 6))
        d.point((x+4,y+6),fill=idx(0,1))
    elif kind=='water':
        d.rectangle((x,y,x+7,y+7),fill=idx(0,8))
        d.line((x+1,y+2,x+5,y+2),fill=idx(0,10 if v&1 else 9))
        d.line((x+3,y+6,x+7,y+6),fill=idx(0,10))
        if (tx+ty)%5==0: d.point((x+1,y+5),fill=idx(0,15))
    elif kind=='brick':
        d.rectangle((x,y,x+7,y+7),fill=idx(0,13))
        d.line((x,y+3,x+7,y+3),fill=idx(0,14))
        d.line((x+(3 if not v else 5),y,x+(3 if not v else 5),y+3),fill=idx(0,15))
        d.line((x+(6 if not v else 2),y+4,x+(6 if not v else 2),y+7),fill=idx(0,6))
    elif kind=='steel':
        d.rectangle((x,y,x+7,y+7),fill=idx(0,11))
        d.rectangle((x+1,y+1,x+6,y+6),fill=idx(0,12))
        d.line((x+1,y+6,x+6,y+6),fill=idx(0,1))
        d.point((x+2,y+2),fill=idx(0,15))
    elif kind=='shore':
        d.rectangle((x,y,x+7,y+7),fill=idx(0,6))
        d.line((x,y+1,x+7,y+1),fill=idx(0,7))
        d.line((x,y+2,x+7,y+2),fill=idx(0,5))

# Base varied grass/dirt upper 168px
for ty in range(21):
    for tx in range(40):
        r=(tx*17+ty*13+tx*ty)%29
        tile_fill(tx,ty,'dirt' if r<7 else 'grass',(tx+ty)&1)

# Winding river and right branch, matching the reference composition at native resolution.
river={
0:(9,14),1:(9,14),2:(8,13),3:(8,13),4:(8,14),5:(9,15),6:(9,15),7:(10,16),8:(10,16),9:(9,15),
10:(9,14),11:(9,14),12:(10,15),13:(10,15),14:(9,14),15:(9,14),16:(10,15),17:(10,15),18:(11,16),19:(11,16),20:(10,15)}
for ty,(a,b) in river.items():
    for tx in range(a,b+1): tile_fill(tx,ty,'water',(tx+ty)&1)
for ty in range(0,17):
    a=27+(ty//6)%2; b=30+(1 if ty in (3,4,5,10,11,12) else 0)
    for tx in range(a,b+1): tile_fill(tx,ty,'water',(tx+ty)&1)
for ty,(a,b) in river.items():
    if a-1>=0: tile_fill(a-1,ty,'shore',ty&1)
    if b+1<40: tile_fill(b+1,ty,'shore',(ty+1)&1)
for tx in range(8,16): tile_fill(tx,8,'steel',tx&1)
for tx in range(26,32): tile_fill(tx,6,'steel',tx&1)
for tx,ty in [(0,5),(1,5),(2,5),(3,5),(4,5),(34,3),(35,3),(36,3),(36,4),(36,5),(32,13),(33,13),(34,13),(34,14),(34,15),(4,15),(5,15),(5,16)]:
    tile_fill(tx,ty,'brick',(tx+ty)&1)
for tx,ty in [(0,11),(1,11),(2,11),(3,11),(24,16),(25,16),(26,16),(35,10),(36,10),(37,10)]:
    tile_fill(tx,ty,'steel',(tx+ty)&1)
for tx in range(0,9): tile_fill(tx,13,'dirt',tx&1)
for tx in range(31,40): tile_fill(tx,9,'dirt',tx&1)

# Trees, craters and debris.
def tree(cx,cy):
    d.rectangle((cx-1,cy+2,cx+1,cy+5),fill=idx(0,6))
    d.rectangle((cx-4,cy-4,cx+4,cy+2),fill=idx(0,2))
    d.rectangle((cx-3,cy-5,cx+2,cy+3),fill=idx(0,3))
    for px,py in [(-2,-3),(1,-4),(3,-1),(-3,0),(0,1)]: d.point((cx+px,cy+py),fill=idx(0,4))
    d.point((cx-1,cy-4),fill=idx(0,15))
for cx,cy in [(11,11),(27,14),(42,8),(60,25),(18,72),(42,67),(62,145),(75,155),(241,14),(260,25),(290,8),(305,31),(245,117),(270,145),(304,118),(21,150),(293,72),(233,145)]: tree(cx,cy)

def crater(cx,cy):
    d.ellipse((cx-6,cy-5,cx+6,cy+5),fill=idx(0,1))
    d.ellipse((cx-3,cy-2,cx+3,cy+2),outline=idx(0,6))
    d.point((cx-5,cy-4),fill=idx(0,7)); d.point((cx+5,cy+4),fill=idx(0,7))
for c in [(31,38),(58,120),(248,32),(285,125),(23,89),(300,57),(77,30)]: crater(*c)

# Distinct top-down tanks and scripted battlefield effects.
def battle_tank(x,y,body,hi,dir='r'):
    d.rectangle((x+2,y+4,x+14,y+13),fill=idx(0,1))
    d.rectangle((x+3,y+3,x+13,y+12),fill=body)
    d.line((x+3,y+4,x+13,y+4),fill=hi)
    d.rectangle((x+6,y+5,x+11,y+10),fill=hi)
    d.rectangle((x+7,y+4,x+10,y+11),fill=body)
    if dir=='r': d.rectangle((x+10,y+6,x+18,y+7),fill=hi)
    elif dir=='l': d.rectangle((x-3,y+6,x+7,y+7),fill=hi)
    elif dir=='d': d.rectangle((x+8,y+9,x+9,y+17),fill=hi)
    else: d.rectangle((x+8,y-4,x+9,y+6),fill=hi)
    for py in (5,9):
        d.point((x+2,y+py),fill=idx(0,12)); d.point((x+14,y+py),fill=idx(0,12))

def muzzle(x,y,dir='r'):
    if dir=='r': pts=[(x,y),(x+3,y-2),(x+6,y),(x+3,y+2)]
    elif dir=='l': pts=[(x,y),(x-3,y-2),(x-6,y),(x-3,y+2)]
    elif dir=='d': pts=[(x,y),(x-2,y+3),(x,y+6),(x+2,y+3)]
    else: pts=[(x,y),(x-2,y-3),(x,y-6),(x+2,y-3)]
    d.polygon(pts,fill=idx(0,14)); d.point((x,y),fill=idx(0,15))

def shell_trace(x0,y0,x1,y1):
    steps=6
    for i in range(steps):
        t=i/(steps-1); x=int(x0+(x1-x0)*t); y=int(y0+(y1-y0)*t)
        d.point((x,y),fill=idx(0,15 if i%2==0 else 14))

def explosion(cx,cy):
    d.rectangle((cx-6,cy-3,cx+6,cy+3),fill=idx(0,13))
    d.rectangle((cx-3,cy-6,cx+3,cy+6),fill=idx(0,13))
    d.rectangle((cx-4,cy-4,cx+4,cy+4),fill=idx(0,14))
    d.rectangle((cx-2,cy-2,cx+2,cy+2),fill=idx(0,15))
    for px,py in [(-8,-5),(8,-4),(-7,6),(9,5),(0,-9)]: d.point((cx+px,cy+py),fill=idx(0,14))

battle_tank(14,22,idx(0,3),idx(0,4),'r'); muzzle(31,29,'r'); shell_trace(34,29,49,31)
battle_tank(276,18,idx(0,6),idx(0,15),'l'); muzzle(272,25,'l'); shell_trace(266,25,255,29)
battle_tank(21,119,idx(0,11),idx(0,12),'r'); muzzle(39,126,'r')
battle_tank(278,120,idx(0,13),idx(0,15),'l'); muzzle(274,127,'l')
explosion(300,83); explosion(47,32)
for cx,cy,r in [(301,96,5),(294,102,4),(307,103,3)]: d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=idx(0,11))

# Small edge signs echo the locked composition without embedding it.
def sign_panel(x,y,w,h,lines,accent=False):
    d.rectangle((x,y,x+w-1,y+h-1),fill=idx(0,1),outline=idx(0,12))
    d.rectangle((x+2,y+2,x+w-3,y+h-3),outline=idx(0,11))
    for i,s in enumerate(lines):
        d.text((x+5,y+3+i*7),s,font=mini,fill=idx(0,15 if not accent or i<len(lines)-1 else 14))
sign_panel(263,3,55,29,['НОВЫЕ КАРТЫ','НОВЫЕ ТАНКИ','ПОБЕЖДАЙ!'],True)
sign_panel(2,139,45,22,['ЗАЩИТИ','БАЗУ >'])
sign_panel(271,139,47,22,['ВРАГИ','ЖДУТ >'])

# ---- metallic logo block PAL1, tile aligned x72..247 y8..63 ----
lx0,ly0,lx1,ly1=72,8,247,63
d.rectangle((lx0,ly0,lx1,ly1),fill=idx(1,1))
for xoff in (0,3):
    col=idx(1,4+xoff//3)
    d.rectangle((lx0+xoff,ly0+xoff,lx1-xoff,ly1-xoff),outline=col)
for side in (-1,1):
    if side<0:
        d.polygon([(72,24),(63,27),(57,33),(63,39),(72,42)],fill=idx(1,3))
        d.line([(58,33),(70,33)],fill=idx(1,6),width=2)
    else:
        d.polygon([(247,24),(256,27),(262,33),(256,39),(247,42)],fill=idx(1,3))
        d.line([(249,33),(261,33)],fill=idx(1,6),width=2)
for rx,ry in [(76,12),(242,12),(76,58),(242,58),(84,20),(234,20)]:
    d.rectangle((rx,ry,rx+1,ry+1),fill=idx(1,7))
def draw_centered(text,font,y,main,shadow,highlight=None):
    bb=d.textbbox((0,0),text,font=font); tw=bb[2]-bb[0]; x=(W-tw)//2
    d.text((x+2,y+2),text,font=font,fill=shadow)
    d.text((x,y),text,font=font,fill=main)
    if highlight:
        d.text((x,y-1),text,font=font,fill=highlight)
        d.text((x,y),text,font=font,fill=main)
    return x,tw
draw_centered('MODERN',logo_modern,9,idx(1,7),idx(1,2),idx(1,15))
draw_centered('TANKS',logo_tanks,26,idx(1,11),idx(1,8),idx(1,13))
for sx,sy in [(123,42),(146,49),(177,38),(198,51)]: d.line((sx,sy,sx+3,sy-1),fill=idx(1,9))
d.rectangle((96,56,223,63),fill=idx(1,2),outline=idx(1,5))
tag='БРОНЯ • ТАКТИКА • ПОБЕДА'
bb=d.textbbox((0,0),tag,font=mini); d.text(((W-(bb[2]-bb[0]))//2,57),tag,font=mini,fill=idx(1,7))

# ---- central menu PAL2, narrower like the reference ----
mx0,my0,mx1,my1=104,64,215,159
d.rectangle((mx0,my0,mx1,my1),fill=idx(2,1))
for off,col in [(0,idx(2,6)),(2,idx(2,4)),(4,idx(2,2))]: d.rectangle((mx0+off,my0+off,mx1-off,my1-off),outline=col)
for rx,ry in [(107,67),(211,67),(107,155),(211,155)]: d.rectangle((rx,ry,rx+1,ry+1),fill=idx(2,7))
txt='ГЛАВНОЕ МЕНЮ'; bb=d.textbbox((0,0),txt,font=small_b); d.text(((W-(bb[2]-bb[0]))//2,68),txt,font=small_b,fill=idx(2,11))
labels=['ИГРАТЬ','ГАРАЖ','СТАТИСТИКА','НАСТРОЙКИ']
rowys=[80,96,112,128]
def row_icon(i,x,y):
    c=idx(2,10)
    if i==0:
        d.rectangle((x+1,y+4,x+10,y+10),fill=c); d.rectangle((x+4,y+1,x+7,y+7),fill=idx(2,9)); d.rectangle((x+7,y+4,x+13,y+5),fill=idx(2,9))
    elif i==1:
        d.line((x+2,y+10,x+10,y+2),fill=idx(2,11),width=2); d.rectangle((x+9,y+1,x+12,y+4),outline=idx(2,11))
    elif i==2:
        d.rectangle((x+2,y+7,x+4,y+11),fill=idx(2,8)); d.rectangle((x+6,y+4,x+8,y+11),fill=idx(2,9)); d.rectangle((x+10,y+1,x+12,y+11),fill=idx(2,11))
    else:
        d.ellipse((x+3,y+3,x+11,y+11),outline=idx(2,11)); d.rectangle((x+6,y+6,x+8,y+8),fill=idx(2,11))
for i,(lab,y) in enumerate(zip(labels,rowys)):
    d.rectangle((112,y,207,y+14),fill=idx(2,2),outline=idx(2,5))
    d.line((114,y+13,205,y+13),fill=idx(2,3))
    row_icon(i,115,y+1)
    d.text((132,y+1),lab,font=menu_font,fill=idx(2,11))
motto='МАЛЕНЬКИЕ ТАНКИ — БОЛЬШИЕ БИТВЫ'; bb=d.textbbox((0,0),motto,font=mini); d.text(((W-(bb[2]-bb[0]))//2,148),motto,font=mini,fill=idx(2,10))

# ---- lower HUD PAL3, y168..223 ----
d.rectangle((0,168,319,223),fill=idx(3,1))
for off,col in [(0,idx(3,6)),(2,idx(3,4)),(4,idx(3,2))]:
    d.rectangle((4+off,170+off,239-off,214-off),outline=col)
    d.rectangle((242+off,170+off,315-off,214-off),outline=col)
d.text((8,171),'КЛАССЫ ТАНКОВ',font=small,fill=idx(3,7))
d.text((246,171),'КАРТА: РЕЧНОЙ ФРОНТ',font=mini,fill=idx(3,7))
for i in range(4):
    x=8+i*35
    d.rectangle((x,180,x+32,207),fill=idx(3,2),outline=idx(3,4))
for off in range(2): d.rectangle((9+off,181+off,39-off,206-off),outline=idx(3,15))
def class_tank(cx,cy,body,light,variant):
    d.rectangle((cx-9,cy-6,cx-7,cy+7),fill=idx(3,1)); d.rectangle((cx+7,cy-6,cx+9,cy+7),fill=idx(3,1))
    d.rectangle((cx-7,cy-5,cx+7,cy+6),fill=body)
    if variant==0:
        d.rectangle((cx-5,cy-7,cx+4,cy+4),fill=light); d.rectangle((cx+1,cy-8,cx+2,cy+6),fill=body); d.rectangle((cx+2,cy-4,cx+11,cy-3),fill=light)
    elif variant==1:
        d.rectangle((cx-4,cy-6,cx+4,cy+3),fill=light); d.rectangle((cx+1,cy-3,cx+10,cy-2),fill=idx(3,7)); d.rectangle((cx-6,cy+3,cx+6,cy+6),fill=body)
    elif variant==2:
        d.rectangle((cx-6,cy-6,cx+6,cy+4),fill=light); d.rectangle((cx+2,cy-4,cx+12,cy-3),fill=idx(3,11)); d.rectangle((cx-4,cy-8,cx+3,cy-6),fill=body)
    else:
        d.rectangle((cx-5,cy-7,cx+5,cy+5),fill=light); d.rectangle((cx+2,cy-5,cx+12,cy-4),fill=idx(3,13)); d.rectangle((cx-7,cy+4,cx+7,cy+6),fill=body)
    d.point((cx-4,cy-4),fill=idx(3,7)); d.point((cx+4,cy+4),fill=idx(3,1))
class_tank(24,193,idx(3,8),idx(3,9),0)
class_tank(59,193,idx(3,10),idx(3,6),1)
class_tank(94,193,idx(3,11),idx(3,15),2)
class_tank(129,193,idx(3,12),idx(3,13),3)
for i,ss in enumerate(['ЛЁГК T-1','СРЕД T-2','ТЯЖ T-3','ШТУРМ T-4']): d.text((9+i*35,207),ss,font=mini,fill=idx(3,15 if i==0 else 7))
stats_x=151
d.text((stats_x,180),'ПАРАМЕТРЫ',font=mini,fill=idx(3,7))
for j,(name,val) in enumerate([('ОГН',4),('БРН',3),('СКР',4),('ДАЛ',3)]):
    y=188+j*6
    d.text((stats_x,y),name,font=mini,fill=idx(3,7))
    d.rectangle((172,y+1,232,y+4),outline=idx(3,5))
    for k in range(6):
        if k<val: d.rectangle((174+k*9,y+2,180+k*9,y+3),fill=idx(3,9))
x0,y0,x1,y1=246,180,311,210
d.rectangle((x0,y0,x1,y1),fill=idx(3,2))
for gy in range(4):
    for gx in range(8):
        xx=x0+2+gx*8; yy=y0+2+gy*7
        if gx in (3,4) or (gx==5 and gy in (1,2)): c=idx(3,14)
        elif (gx+gy)%4==0: c=idx(3,12)
        else: c=idx(3,8)
        d.rectangle((xx,yy,xx+6,yy+5),fill=c)
d.rectangle((272,187,285,199),outline=idx(3,7))
d.point((250,205),fill=idx(3,15)); d.point((306,184),fill=idx(3,15))
d.line((4,216,315,216),fill=idx(3,4))
d.text((8,218),'© 1994 MODERN TANKS',font=mini,fill=idx(3,6))
start='НАЖМИ START'; bb=d.textbbox((0,0),start,font=small_b); d.text(((W-(bb[2]-bb[0]))//2,216),start,font=small_b,fill=idx(3,15))
d.text((276,218),'— 16-BIT —',font=mini,fill=idx(3,6))

# Enforce one Mega Drive palette per 8x8 tile.
def intended_pal(tx,ty):
    x,y=tx*8,ty*8
    if y>=168: return 3
    if 104<=x<=215 and 64<=y<=159: return 2
    if 72<=x<=247 and 8<=y<=63: return 1
    if 56<=x<=263 and 24<=y<=47: return 1
    return 0
allrgb=[c for p in pals for c in p]
pix=img.load()
for ty in range(28):
    for tx in range(40):
        p=intended_pal(tx,ty); allowed=pals[p]
        for yy in range(ty*8,min(ty*8+8,H)):
            for xx in range(tx*8,min(tx*8+8,W)):
                old=pix[xx,yy]
                oldrgb=allrgb[old] if old<64 else (0,0,0)
                if old//16!=p:
                    best=min(range(16),key=lambda i:sum((allowed[i][k]-oldrgb[k])**2 for k in range(3)))
                    pix[xx,yy]=idx(p,best)
img.save(os.path.join(OUT,'r2_menu_bg.png'),optimize=False)

# Selector overlays 104x16, PAL2.
for n,lab in enumerate(labels):
    ov=Image.new('P',(104,16),idx(2,0)); ov.putpalette(palette); od=ImageDraw.Draw(ov)
    od.rectangle((0,0,103,15),fill=idx(2,2),outline=idx(2,13))
    od.rectangle((2,2,101,13),outline=idx(2,12))
    od.polygon([(2,8),(7,3),(7,13)],fill=idx(2,13)); od.polygon([(101,8),(96,3),(96,13)],fill=idx(2,13))
    if n==0:
        od.rectangle((11,5,20,11),fill=idx(2,9)); od.rectangle((14,2,17,8),fill=idx(2,10)); od.rectangle((17,5,24,6),fill=idx(2,10))
    elif n==1:
        od.line((12,11,20,3),fill=idx(2,15),width=2)
    elif n==2:
        for k,h in enumerate([4,7,10]): od.rectangle((12+k*4,12-h,14+k*4,12),fill=idx(2,13))
    else:
        od.ellipse((13,4,21,12),outline=idx(2,15)); od.rectangle((16,7,18,9),fill=idx(2,15))
    od.text((28,1),lab,font=menu_font,fill=idx(2,13))
    ov.save(os.path.join(OUT,f'r2_sel_{n}.png'),optimize=False)

# Animated background tank 16x16, PAL0.
anim=Image.new('P',(16,16),idx(0,0)); anim.putpalette(palette); ad=ImageDraw.Draw(anim)
ad.rectangle((1,5,13,13),fill=idx(0,1)); ad.rectangle((3,4,12,11),fill=idx(0,3)); ad.rectangle((5,2,10,8),fill=idx(0,4)); ad.rectangle((9,5,15,6),fill=idx(0,15)); ad.point((4,5),fill=idx(0,15)); ad.line((3,12,12,12),fill=idx(0,12))
anim.save(os.path.join(OUT,'r2_anim_tank.png'),optimize=False)
print('generated', OUT)
