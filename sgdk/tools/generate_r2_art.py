from PIL import Image, ImageDraw, ImageFont
import os

W, H = 320, 224
OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'res'))
os.makedirs(OUT, exist_ok=True)

# Four 16-color Mega Drive-oriented palettes. Pixels 0..63 encode PAL0..PAL3
# in their upper nibble for SGDK ResComp tile palette selection.
pals = [
    [(0,0,0),(7,18,20),(13,45,28),(21,77,35),(34,112,43),(79,141,52),(94,63,31),(126,82,38),(39,96,142),(44,140,196),(73,180,232),(126,199,241),(147,51,32),(210,76,34),(233,170,49),(235,236,210)],
    [(0,0,0),(7,12,18),(16,27,39),(28,44,59),(50,67,82),(82,98,113),(119,132,143),(161,170,177),(198,205,209),(235,238,239),(109,50,20),(173,78,25),(224,112,29),(247,157,37),(255,196,61),(255,235,170)],
    [(0,0,0),(5,13,20),(8,27,39),(13,42,57),(26,60,75),(52,82,96),(79,102,114),(121,138,146),(178,190,195),(235,241,239),(62,124,73),(80,189,98),(186,161,49),(251,224,73),(195,65,50),(244,120,65)],
    [(0,0,0),(4,12,18),(9,24,32),(18,42,53),(40,68,80),(67,96,106),(105,131,138),(161,178,180),(219,226,223),(242,244,229),(51,128,76),(65,196,105),(48,115,179),(73,177,224),(222,73,54),(247,206,67)]
]
palette = []
for pal in pals:
    for c in pal:
        palette.extend(c)
palette += [0, 0, 0] * (256 - 64)

def idx(p, c):
    return p * 16 + c

img = Image.new('P', (W, H), idx(0, 1))
img.putpalette(palette)
d = ImageDraw.Draw(img)

font_bold = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
font_mono = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'
logo1 = ImageFont.truetype(font_bold, 25)
logo2 = ImageFont.truetype(font_bold, 36)
small = ImageFont.truetype(font_mono, 9)
menu_font = ImageFont.truetype(font_mono, 12)
mini = ImageFont.truetype(font_mono, 8)

def grass_tile(x, y, v=0):
    base = idx(0, 2 + v % 2)
    hi = idx(0, 3 + v % 2)
    dark = idx(0, 1)
    d.rectangle([x, y, x+7, y+7], fill=base)
    pts = [(1,1),(5,2),(2,5),(6,6)] if v % 2 == 0 else [(2,1),(6,3),(1,6),(5,5)]
    for px, py in pts:
        d.point((x+px, y+py), fill=hi)
    d.point((x+3, y+3), fill=dark)

def dirt_tile(x, y, v=0):
    d.rectangle([x, y, x+7, y+7], fill=idx(0, 6))
    pts = [(1,2),(4,1),(6,5),(2,6)] if v % 2 == 0 else [(2,1),(5,3),(1,5),(6,6)]
    for px, py in pts:
        d.point((x+px, y+py), fill=idx(0, 7))

def water_tile(x, y, v=0):
    d.rectangle([x, y, x+7, y+7], fill=idx(0, 8))
    c = idx(0, 9 + (v % 2))
    d.line([x+1, y+2, x+5, y+2], fill=c)
    d.line([x+3, y+6, x+7, y+6], fill=c)

def brick_tile(x, y, v=0):
    d.rectangle([x, y, x+7, y+7], fill=idx(0, 12))
    d.line([x, y+3, x+7, y+3], fill=idx(0, 13))
    if v % 2 == 0:
        d.line([x+3, y, x+3, y+3], fill=idx(0, 15))
    else:
        d.line([x+5, y+3, x+5, y+7], fill=idx(0, 15))

def steel_tile(x, y, v=0):
    d.rectangle([x, y, x+7, y+7], fill=idx(0, 15))
    d.rectangle([x+1, y+1, x+6, y+6], fill=idx(0, 6))
    d.line([x+1, y+1, x+6, y+1], fill=idx(0, 15))

# Battlefield backdrop, built at native 320x224 — never by shrinking the locked PNG.
for ty in range(21):
    for tx in range(40):
        x, y = tx * 8, ty * 8
        r = (tx * 7 + ty * 11) % 17
        if 13 <= tx <= 17 and ty < 20:
            water_tile(x, y, (tx + ty) & 1)
        elif 28 <= tx <= 31 and 1 <= ty <= 17:
            water_tile(x, y, (tx + ty) & 1)
        elif (tx in (6,7,32,33) and 2 <= ty <= 17) or (ty in (5,16) and tx in range(2,9)):
            brick_tile(x, y, (tx + ty) & 1)
        elif r < 3:
            dirt_tile(x, y, (tx + ty) & 1)
        else:
            grass_tile(x, y, (tx + ty) & 1)

for tx in range(0, 12):
    dirt_tile(tx * 8, 80, tx & 1)
for tx in range(25, 40):
    dirt_tile(tx * 8, 120, tx & 1)
for tx in range(27, 33):
    steel_tile(tx * 8, 72, tx & 1)

for cx, cy in [(38,43),(71,126),(250,42),(284,143)]:
    d.ellipse([cx-6, cy-4, cx+6, cy+4], fill=idx(0,1))
    d.point((cx,cy), fill=idx(0,7))

def tank(x, y, color, light, flip=False):
    d.rectangle([x+2, y+4, x+13, y+11], fill=color)
    d.rectangle([x+5, y+1, x+10, y+7], fill=light)
    if not flip:
        d.rectangle([x+10, y+3, x+15, y+4], fill=light)
    else:
        d.rectangle([x, y+3, x+5, y+4], fill=light)
    d.line([x+2, y+12, x+13, y+12], fill=idx(0,1))

tank(18,28,idx(0,3),idx(0,5))
tank(284,26,idx(0,12),idx(0,14),True)
tank(24,135,idx(0,6),idx(0,15))
tank(275,135,idx(0,12),idx(0,15),True)
for r, c in [(9,idx(0,13)),(6,idx(0,14)),(3,idx(0,15))]:
    d.rectangle([254-r,52-r,254+r,52+r], fill=c)

# Metallic title block, palette 1.
x0, y0, x1, y1 = 64, 8, 255, 63
d.rectangle([x0,y0,x1,y1], fill=idx(1,1))
for off, col in [(0,idx(1,3)),(2,idx(1,6)),(4,idx(1,2))]:
    d.rectangle([x0+off,y0+off,x1-off,y1-off], outline=col)

def centered_text(text, font, y, fill, shadow):
    bb = d.textbbox((0,0), text, font=font)
    x = (W - (bb[2]-bb[0])) // 2
    d.text((x+2,y+2), text, font=font, fill=shadow)
    d.text((x,y), text, font=font, fill=fill)

centered_text('MODERN', logo1, 9, idx(1,8), idx(1,2))
centered_text('TANKS', logo2, 27, idx(1,13), idx(1,10))
for rx, ry in [(68,12),(248,12),(68,56),(248,56)]:
    d.rectangle([rx,ry,rx+2,ry+2], fill=idx(1,8))

# Main menu, palette 2. Semantics remain frozen-design truth.
mx0, my0, mx1, my1 = 88, 64, 231, 167
d.rectangle([mx0,my0,mx1,my1], fill=idx(2,1))
d.rectangle([mx0,my0,mx1,my1], outline=idx(2,7), width=2)
d.rectangle([mx0+4,my0+4,mx1-4,my1-4], outline=idx(2,4))
text = 'ГЛАВНОЕ МЕНЮ'
bb = d.textbbox((0,0), text, font=small)
d.text(((W-(bb[2]-bb[0]))//2,69), text, font=small, fill=idx(2,8))
labels = ['ИГРАТЬ','ГАРАЖ','СТАТИСТИКА','НАСТРОЙКИ']
rowys = [80,96,112,128]
for i, (lab,y) in enumerate(zip(labels,rowys)):
    d.rectangle([96,y,223,y+15], fill=idx(2,2), outline=idx(2,5))
    d.rectangle([101,y+4,108,y+11], fill=idx(2,10 if i == 0 else 8))
    if i == 0:
        d.rectangle([104,y+1,106,y+4], fill=idx(2,11))
    d.text((116,y+1), lab, font=menu_font, fill=idx(2,9))
footer = 'БРОНЯ  •  ТАКТИКА  •  ПОБЕДА'
bb = d.textbbox((0,0), footer, font=mini)
d.text(((W-(bb[2]-bb[0]))//2,148), footer, font=mini, fill=idx(2,7))

# Lower information strip, palette 3.
d.rectangle([0,168,319,223], fill=idx(3,1))
d.rectangle([4,171,315,218], outline=idx(3,6), width=2)
for x in [8,48,88,128]:
    d.rectangle([x,180,x+31,207], fill=idx(3,2), outline=idx(3,5))

def mini_tank(x,y,c):
    d.rectangle([x+7,y+8,x+23,y+18], fill=c)
    d.rectangle([x+11,y+4,x+19,y+11], fill=idx(3,8))
    d.rectangle([x+19,y+7,x+27,y+8], fill=idx(3,8))

for i,c in enumerate([idx(3,10),idx(3,6),idx(3,15),idx(3,14)]):
    mini_tank(8+i*40,181,c)
for i,s in enumerate(['T-1','T-2','T-3','T-4']):
    d.text((14+i*40,207), s, font=mini, fill=idx(3,9 if i else 15))
d.text((8,171), 'КЛАССЫ ТАНКОВ', font=mini, fill=idx(3,8))
d.text((174,174), 'ПАРАМЕТРЫ', font=mini, fill=idx(3,8))
for j,name in enumerate(['ОГН','БРН','СКР','ДАЛ']):
    y = 184 + j*8
    d.text((174,y), name, font=mini, fill=idx(3,7))
    d.rectangle([198,y+1,236,y+5], outline=idx(3,5))
    d.rectangle([199,y+2,199+8+j*5,y+4], fill=idx(3,11))

d.rectangle([244,174,314,214], fill=idx(3,2), outline=idx(3,7))
for yy in range(178,212,8):
    for xx in range(248,312,8):
        val = (xx//8 + yy//8) % 5
        c = [idx(3,10),idx(3,12),idx(3,13),idx(3,4),idx(3,14)][val]
        d.rectangle([xx,yy,xx+6,yy+6], fill=c)
d.rectangle([274,190,288,202], outline=idx(3,9))
d.text((248,215), 'КАРТА', font=mini, fill=idx(3,8))
d.text((6,218), '1994 MODERN TANKS', font=mini, fill=idx(3,6))
d.text((122,216), 'START / A', font=mini, fill=idx(3,15))

# Enforce one Mega Drive palette per 8x8 tile.
def intended_pal(tx,ty):
    x, y = tx*8, ty*8
    if y >= 168: return 3
    if 64 <= x <= 231 and 64 <= y <= 167: return 2
    if 64 <= x <= 255 and 8 <= y <= 63: return 1
    return 0

allrgb = [c for p in pals for c in p]
pix = img.load()
for ty in range(28):
    for tx in range(40):
        p = intended_pal(tx,ty)
        allowed = pals[p]
        for yy in range(ty*8, min(ty*8+8,H)):
            for xx in range(tx*8, min(tx*8+8,W)):
                old = pix[xx,yy]
                oldrgb = allrgb[old] if old < 64 else (0,0,0)
                if old // 16 != p:
                    best = min(range(16), key=lambda i: sum((allowed[i][k]-oldrgb[k])**2 for k in range(3)))
                    pix[xx,yy] = idx(p,best)

img.save(os.path.join(OUT, 'r2_menu_bg.png'), optimize=False)

# Selected rows — only one is resident at a time.
for n, lab in enumerate(labels):
    ov = Image.new('P', (136,16), idx(2,0))
    ov.putpalette(palette)
    od = ImageDraw.Draw(ov)
    od.rectangle([0,0,135,15], fill=idx(2,2), outline=idx(2,13))
    od.rectangle([2,2,133,13], outline=idx(2,12))
    od.polygon([(3,8),(8,3),(8,13)], fill=idx(2,13))
    od.polygon([(132,8),(127,3),(127,13)], fill=idx(2,13))
    od.rectangle([12,4,19,11], fill=idx(2,11 if n == 0 else 8))
    od.text((28,1), lab, font=menu_font, fill=idx(2,13))
    ov.save(os.path.join(OUT, f'r2_sel_{n}.png'), optimize=False)

# Small scripted battlefield unit on Plane A.
anim = Image.new('P', (16,16), idx(0,0))
anim.putpalette(palette)
ad = ImageDraw.Draw(anim)
ad.rectangle([1,5,13,12], fill=idx(0,3))
ad.rectangle([4,2,10,8], fill=idx(0,5))
ad.rectangle([9,4,15,5], fill=idx(0,15))
ad.rectangle([0,13,14,14], fill=idx(0,1))
ad.point((4,3), fill=idx(0,15))
anim.save(os.path.join(OUT, 'r2_anim_tank.png'), optimize=False)

print('R2 art generated at native Mega Drive resolution:', OUT)
