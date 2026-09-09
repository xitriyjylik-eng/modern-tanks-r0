#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
C = ROOT / 'sgdk/src/battle/battle_r3.c'
H = ROOT / 'sgdk/inc/battle_r3.h'
GEN = ROOT / 'sgdk/tools/build_r3_assets.py'
TEST = ROOT / 'sgdk/tools/test_r3_world.py'


def sub1(text, pattern, repl, label):
    out, n = re.subn(pattern, repl, text, count=1, flags=re.S)
    if n != 1:
        raise SystemExit(f'{label}: expected 1 replacement, got {n}')
    return out

s = C.read_text(encoding='utf-8')

constants = r'''#define R3_TILE_SIZE 8
#define R3_WORLD_W_TILES (R3_WORLD_WIDTH_PX / R3_TILE_SIZE)
#define R3_WORLD_H_TILES (R3_WORLD_HEIGHT_PX / R3_TILE_SIZE)
#define R3_PLANE_W 64
#define R3_PLANE_H 32
#define R3_PREFETCH_LEFT 18
#define R3_PREFETCH_TOP 4
#define R3_VIEW_W_TILES 28
#define R3_VIEW_H_TILES 24
#define R3_MINIMAP_X 29
#define R3_MINIMAP_Y 8
#define R3_MINIMAP_W 10
#define R3_MINIMAP_H 8
#define R3_MINIMAP_SAMPLE_STEP 24
#define R3_TREE_HOLD_TICKS 10
#define R3_WATER_HOLD_TICKS 8
#define R3_MINIMAP_HOLD_TICKS 12
#define R3_CAMERA_FP_SHIFT 8
#define R3_CAMERA_RESPONSE_SHIFT 3
#define R3_CAMERA_MAX_STEP_Q8 (5L << R3_CAMERA_FP_SHIFT)

/* Exact atlas layout emitted by build_r3_assets.py. The previous renderer
 * treated coherent metatiles as unrelated 8x8 tiles, creating mosaic noise. */
#define WT_BLANK 0
#define WT_GRASS_BASE 1
#define WT_GRASS_META 12
#define WT_GRASS_W 4
#define WT_GRASS_H 4
#define WT_ROAD_BASE 193
#define WT_ROAD_META 8
#define WT_ROAD_W 4
#define WT_ROAD_H 4
#define WT_WATER_BASE 321
#define WT_WATER_VARIANTS 3
#define WT_WATER_FRAMES 8
#define WT_SHORE_BASE 417
#define WT_SHORE_VARIANTS_PER_SIDE 3
#define WT_BRIDGE_BASE 513
#define WT_BRIDGE_META 4
#define WT_DECOR_BASE 577
#define WT_DECOR_META 24
#define WT_STRUCT_BASE 673
#define WT_STRUCT_META 8
#define WT_TREE_BASE 769
#define WT_TREE_FRAMES 12
#define WT_TREE_W 4
#define WT_TREE_H 3
#define WT_TREE_FRAME_TILES 12

#define HT_BG 0
#define HT_SOLID 1
#define HT_HLINE 2
#define HT_VLINE 3
#define HT_CORNER 4
#define HT_DIAG 5
#define HT_DOT 6
#define HT_GLYPH_BASE 8

static const char r3Charset[]'''
s = sub1(s, r'#define R3_TILE_SIZE 8.*?static const char r3Charset\[\]', constants, 'constants')

s = s.replace(
    'static s32 cameraCenterX = R3_WORLD_WIDTH_PX / 2;\nstatic s32 cameraCenterY = R3_WORLD_HEIGHT_PX / 2;',
    'static s32 cameraCenterX = R3_WORLD_WIDTH_PX / 2;\nstatic s32 cameraCenterY = R3_WORLD_HEIGHT_PX / 2;\n'
    'static s32 cameraPosXQ8 = (R3_WORLD_WIDTH_PX / 2) << R3_CAMERA_FP_SHIFT;\n'
    'static s32 cameraPosYQ8 = (R3_WORLD_HEIGHT_PX / 2) << R3_CAMERA_FP_SHIFT;\n'
    'static s32 cameraTargetXQ8 = (R3_WORLD_WIDTH_PX / 2) << R3_CAMERA_FP_SHIFT;\n'
    'static s32 cameraTargetYQ8 = (R3_WORLD_HEIGHT_PX / 2) << R3_CAMERA_FP_SHIFT;',
    1)

terrain = r'''static u16 hash16(s16 x, s16 y)
{
    u32 h = ((u32)(u16)x * 1103515245UL) ^ ((u32)(u16)y * 2654435761UL) ^ 0x9E3779B9UL;
    h ^= h >> 16;
    h *= 2246822519UL;
    h ^= h >> 13;
    return (u16)(h ^ (h >> 16));
}

static s16 triWave(s16 value, u16 period)
{
    u16 p = ((u16)value) % period;
    u16 half = period >> 1;
    if (p >= half) p = period - 1 - p;
    return (s16)p - (s16)(half >> 1);
}

static u16 valueNoise8(s16 wx, s16 wy, u16 shift, s16 seedX, s16 seedY)
{
    const u16 scale = (u16)(1U << shift);
    const u16 mask = scale - 1;
    s16 gx = wx >> shift;
    s16 gy = wy >> shift;
    u16 fx = ((u16)wx) & mask;
    u16 fy = ((u16)wy) & mask;
    u16 v00 = hash16(gx + seedX, gy + seedY) & 255;
    u16 v10 = hash16(gx + 1 + seedX, gy + seedY) & 255;
    u16 v01 = hash16(gx + seedX, gy + 1 + seedY) & 255;
    u16 v11 = hash16(gx + 1 + seedX, gy + 1 + seedY) & 255;
    u32 a = (u32)v00 * (scale - fx) + (u32)v10 * fx;
    u32 b = (u32)v01 * (scale - fx) + (u32)v11 * fx;
    return (u16)((a * (scale - fy) + b * fy) >> (shift * 2));
}

static s16 riverCenterX(s16 worldY)
{
    return 512 + (triWave(worldY >> 1, 192) >> 1) + (triWave(worldY >> 3, 64) >> 2);
}

static s16 roadCenterY(s16 worldX)
{
    return 512 + (triWave(worldX >> 1, 256) >> 2);
}

static bool worldInBounds(s16 wx, s16 wy)
{
    return (wx >= 0) && (wy >= 0) && (wx < R3_WORLD_W_TILES) && (wy < R3_WORLD_H_TILES);
}

static s16 riverDistance(s16 wx, s16 wy)
{
    s16 d = wx - riverCenterX(wy);
    return (d < 0) ? -d : d;
}

static bool isWater(s16 wx, s16 wy) { return riverDistance(wx, wy) <= 6; }
static bool isShore(s16 wx, s16 wy)
{
    s16 d = riverDistance(wx, wy);
    return (d >= 7) && (d <= 9);
}

static bool isRoad(s16 wx, s16 wy)
{
    s16 d = wy - roadCenterY(wx);
    if (d < 0) d = -d;
    return d <= 2;
}

static bool isBridge(s16 wx, s16 wy)
{
    return isRoad(wx, wy) && (riverDistance(wx, wy) <= 9);
}

static bool forestField(s16 wx, s16 wy)
{
    u16 large, medium, score;
    if (!worldInBounds(wx, wy) || isWater(wx, wy) || isShore(wx, wy) || isRoad(wx, wy)) return FALSE;
    if ((wx > 760) && (wx < 900) && (wy > 700) && (wy < 880)) return TRUE;
    large = valueNoise8(wx, wy, 6, 17, -29);
    medium = valueNoise8(wx, wy, 4, -53, 41);
    score = (u16)(((u32)large * 3 + medium) >> 2);
    return score < 92;
}

static bool hasTreeAnchor(s16 ax, s16 ay)
{
    if (!worldInBounds(ax, ay) || !worldInBounds(ax + 3, ay + 2)) return FALSE;
    if ((ax & 3) != 0 || (ay % 3) != 0) return FALSE;
    if (!forestField(ax + 1, ay + 1) || !forestField(ax + 2, ay + 1)) return FALSE;
    return (hash16(ax >> 2, ay / 3) & 7) < 5;
}

static u16 meta4x4(u16 base, u16 variant, s16 wx, s16 wy)
{
    return base + variant * 16 + ((((u16)wy) & 3) << 2) + (((u16)wx) & 3);
}

static u16 baseTileAttr(s16 wx, s16 wy)
{
    u16 variant, id, pal;
    if (!worldInBounds(wx, wy))
        return TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, worldTileBase + WT_BLANK);

    if (isBridge(wx, wy))
    {
        variant = hash16(wx >> 2, wy >> 2) % WT_BRIDGE_META;
        id = meta4x4(WT_BRIDGE_BASE, variant, wx, wy);
        pal = PAL3;
    }
    else if (isWater(wx, wy))
    {
        u16 local = ((((u16)wy) & 1) << 1) | (((u16)wx) & 1);
        variant = hash16(wx >> 1, wy >> 1) % WT_WATER_VARIANTS;
        id = WT_WATER_BASE + (variant * WT_WATER_FRAMES + waterFrame) * 4 + local;
        pal = PAL1;
    }
    else if (isShore(wx, wy))
    {
        s16 center = riverCenterX(wy);
        bool left = wx < center;
        s16 localX = left ? (wx - (center - 10)) : (wx - (center + 7));
        u16 lx = (u16)((localX < 0) ? 0 : (localX > 3 ? 3 : localX));
        u16 ly = ((u16)wy) & 3;
        variant = (left ? 0 : WT_SHORE_VARIANTS_PER_SIDE) +
                  (hash16(wy >> 2, left ? 7 : 19) % WT_SHORE_VARIANTS_PER_SIDE);
        id = WT_SHORE_BASE + variant * 16 + ly * 4 + lx;
        pal = PAL3;
    }
    else if (isRoad(wx, wy))
    {
        variant = hash16(wx >> 2, wy >> 2) % WT_ROAD_META;
        id = meta4x4(WT_ROAD_BASE, variant, wx, wy);
        pal = PAL3;
    }
    else
    {
        variant = hash16(wx >> 2, wy >> 2) % WT_GRASS_META;
        id = meta4x4(WT_GRASS_BASE, variant, wx, wy);
        pal = PAL2;
    }
    return TILE_ATTR_FULL(pal, FALSE, FALSE, FALSE, worldTileBase + id);
}

static u16 overlayTileAttr(s16 wx, s16 wy)
{
    s16 ax, ay;
    u16 h;
    if (!worldInBounds(wx, wy))
        return TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, worldTileBase + WT_BLANK);

    ax = wx - (wx & 3);
    ay = wy - (wy % 3);
    if (hasTreeAnchor(ax, ay))
    {
        u16 phase = (hash16(ax, ay) >> 4) % WT_TREE_FRAMES;
        u16 frame = (treeFrame + phase) % WT_TREE_FRAMES;
        u16 q = (u16)((wy - ay) * 4 + (wx - ax));
        return TILE_ATTR_FULL(PAL2, TRUE, FALSE, FALSE,
                              worldTileBase + WT_TREE_BASE + frame * WT_TREE_FRAME_TILES + q);
    }

    ax = wx - (wx & 3);
    ay = wy - (wy % 3);
    if (worldInBounds(ax + 3, ay + 2) && !forestField(ax + 1, ay + 1) &&
        !isRoad(ax + 1, ay + 1) && !isWater(ax + 1, ay + 1) && !isShore(ax + 1, ay + 1))
    {
        h = hash16(ax >> 2, ay / 3);
        if ((h & 1023) < 10)
        {
            u16 variant = (h >> 10) % WT_STRUCT_META;
            u16 q = (u16)((wy - ay) * 4 + (wx - ax));
            return TILE_ATTR_FULL(PAL3, TRUE, FALSE, FALSE,
                                  worldTileBase + WT_STRUCT_BASE + variant * 12 + q);
        }
    }

    ax = wx - (wx & 1);
    ay = wy - (wy & 1);
    if (!isWater(wx, wy) && !isShore(wx, wy) && !isRoad(wx, wy))
    {
        h = hash16(ax >> 1, ay >> 1);
        if ((h & 255) < 13)
        {
            u16 variant = (h >> 8) % WT_DECOR_META;
            u16 q = (u16)((wy - ay) * 2 + (wx - ax));
            return TILE_ATTR_FULL((variant < 12) ? PAL0 : PAL2, TRUE, FALSE, FALSE,
                                  worldTileBase + WT_DECOR_BASE + variant * 4 + q);
        }
    }
    return TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, worldTileBase + WT_BLANK);
}

static void setWorldCell'''
s = sub1(s, r'static u16 hash16.*?static void setWorldCell', terrain, 'terrain')

minimap = r'''enum R3MiniClass { R3_MINI_GRASS=0, R3_MINI_FOREST, R3_MINI_ROAD, R3_MINI_WATER, R3_MINI_BRIDGE };

static u16 miniMapClassAt(s16 wx, s16 wy)
{
    if (!worldInBounds(wx, wy)) return R3_MINI_GRASS;
    if (isBridge(wx, wy)) return R3_MINI_BRIDGE;
    if (isWater(wx, wy)) return R3_MINI_WATER;
    if (isRoad(wx, wy) || isShore(wx, wy)) return R3_MINI_ROAD;
    if (forestField(wx, wy)) return R3_MINI_FOREST;
    return R3_MINI_GRASS;
}

static u16 miniMapAttrBlock(s16 centerX, s16 centerY)
{
    static const s16 sample[3] = {-8,0,8};
    u16 counts[5] = {0,0,0,0,0};
    u16 ix, iy, cls;
    for (iy=0; iy<3; iy++) for (ix=0; ix<3; ix++)
    {
        cls = miniMapClassAt(centerX + sample[ix], centerY + sample[iy]);
        counts[cls]++;
    }
    if (counts[R3_MINI_BRIDGE]) cls = R3_MINI_BRIDGE;
    else if (counts[R3_MINI_WATER] >= 2) cls = R3_MINI_WATER;
    else if (counts[R3_MINI_ROAD]) cls = R3_MINI_ROAD;
    else if (counts[R3_MINI_FOREST] >= 3) cls = R3_MINI_FOREST;
    else cls = R3_MINI_GRASS;

    if (cls == R3_MINI_WATER) return TILE_ATTR_FULL(PAL1, TRUE, FALSE, FALSE, hudTileBase + HT_SOLID);
    if (cls == R3_MINI_ROAD || cls == R3_MINI_BRIDGE) return TILE_ATTR_FULL(PAL3, TRUE, FALSE, FALSE, hudTileBase + HT_SOLID);
    if (cls == R3_MINI_FOREST) return TILE_ATTR_FULL(PAL2, TRUE, FALSE, FALSE, hudTileBase + HT_SOLID);
    return TILE_ATTR_FULL(PAL2, TRUE, FALSE, FALSE, hudTileBase + HT_BG);
}

static void drawMiniMap(void)
{
    s16 centerTileX = (s16)(cameraTargetXQ8 >> (R3_CAMERA_FP_SHIFT + 3));
    s16 centerTileY = (s16)(cameraTargetYQ8 >> (R3_CAMERA_FP_SHIFT + 3));
    u16 x, y;
    for (y=0; y<R3_MINIMAP_H; y++) for (x=0; x<R3_MINIMAP_W; x++)
    {
        s16 wx = centerTileX + ((s16)x - (R3_MINIMAP_W/2)) * R3_MINIMAP_SAMPLE_STEP;
        s16 wy = centerTileY + ((s16)y - (R3_MINIMAP_H/2)) * R3_MINIMAP_SAMPLE_STEP;
        VDP_setTileMapXY(WINDOW, miniMapAttrBlock(wx, wy), R3_MINIMAP_X+x, R3_MINIMAP_Y+y);
    }
    VDP_setTileMapXY(WINDOW, TILE_ATTR_FULL(PAL0, TRUE, FALSE, FALSE, hudTileBase + HT_DOT),
                     R3_MINIMAP_X + R3_MINIMAP_W/2, R3_MINIMAP_Y + R3_MINIMAP_H/2);
}

static void drawHudFrame'''
s = sub1(s, r'static u16 miniMapAttr.*?static void drawHudFrame', minimap, 'minimap')

s = s.replace('hudText(30, 17, "MAP 8K");', 'hudText(30, 17, "MAP X24");')
s = s.replace('hudText(1, 25, "STREAMED WORLD / PLANE A+B / R3");', 'hudText(1, 25, "STREAMED WORLD / SMOOTH FOLLOW / R3");')
s = s.replace('hudText(1, 27, "8192X8192  TREES+WATER  HUD FIXED");', 'hudText(1, 27, "8192X8192  METATILES  HUD FIXED");')

enter_old = 'cameraCenterX = R3_WORLD_WIDTH_PX / 2;\n    cameraCenterY = R3_WORLD_HEIGHT_PX / 2;\n    loadedOriginX'
enter_new = ('cameraCenterX = R3_WORLD_WIDTH_PX / 2;\n    cameraCenterY = R3_WORLD_HEIGHT_PX / 2;\n'
             '    cameraPosXQ8 = cameraCenterX << R3_CAMERA_FP_SHIFT;\n'
             '    cameraPosYQ8 = cameraCenterY << R3_CAMERA_FP_SHIFT;\n'
             '    cameraTargetXQ8 = cameraPosXQ8;\n'
             '    cameraTargetYQ8 = cameraPosYQ8;\n'
             '    loadedOriginX')
if enter_old not in s:
    raise SystemExit('enter init anchor missing')
s = s.replace(enter_old, enter_new, 1)

update = r'''static s32 smoothCameraAxis(s32 posQ8, s32 targetQ8)
{
    s32 delta = targetQ8 - posQ8;
    s32 step;
    if (delta > -8 && delta < 8) return targetQ8;
    step = delta >> R3_CAMERA_RESPONSE_SHIFT;
    if (step > R3_CAMERA_MAX_STEP_Q8) step = R3_CAMERA_MAX_STEP_Q8;
    if (step < -R3_CAMERA_MAX_STEP_Q8) step = -R3_CAMERA_MAX_STEP_Q8;
    if (step == 0) step = (delta > 0) ? 1 : -1;
    return posQ8 + step;
}

void R3_battleSetCameraTarget(s32 worldX, s32 worldY)
{
    s32 minX = R3_BATTLEFIELD_WIDTH_PX / 2;
    s32 maxX = R3_WORLD_WIDTH_PX - R3_BATTLEFIELD_WIDTH_PX / 2;
    s32 minY = R3_BATTLEFIELD_HEIGHT_PX / 2;
    s32 maxY = R3_WORLD_HEIGHT_PX - R3_BATTLEFIELD_HEIGHT_PX / 2;
    if (worldX < minX) worldX = minX; if (worldX > maxX) worldX = maxX;
    if (worldY < minY) worldY = minY; if (worldY > maxY) worldY = maxY;
    cameraTargetXQ8 = worldX << R3_CAMERA_FP_SHIFT;
    cameraTargetYQ8 = worldY << R3_CAMERA_FP_SHIFT;
}

void R3_battleUpdate(void)
{
    s16 speed;
    bool targetMoved = FALSE, cameraMoved = FALSE;
    bool waterChanged = FALSE, treesChanged = FALSE;
    s32 oldCameraX, oldCameraY, targetX, targetY;
    if (!active) return;

    /* R3 input moves a synthetic future-tank target. R4 can feed real tank coordinates. */
    speed = (padHeld & BUTTON_C) ? 4 : 2;
    targetX = cameraTargetXQ8 >> R3_CAMERA_FP_SHIFT;
    targetY = cameraTargetYQ8 >> R3_CAMERA_FP_SHIFT;
    if (padHeld & BUTTON_LEFT)  { targetX -= speed; targetMoved = TRUE; }
    if (padHeld & BUTTON_RIGHT) { targetX += speed; targetMoved = TRUE; }
    if (padHeld & BUTTON_UP)    { targetY -= speed; targetMoved = TRUE; }
    if (padHeld & BUTTON_DOWN)  { targetY += speed; targetMoved = TRUE; }
    if (targetMoved) R3_battleSetCameraTarget(targetX, targetY);

    oldCameraX = cameraCenterX; oldCameraY = cameraCenterY;
    cameraPosXQ8 = smoothCameraAxis(cameraPosXQ8, cameraTargetXQ8);
    cameraPosYQ8 = smoothCameraAxis(cameraPosYQ8, cameraTargetYQ8);
    cameraCenterX = cameraPosXQ8 >> R3_CAMERA_FP_SHIFT;
    cameraCenterY = cameraPosYQ8 >> R3_CAMERA_FP_SHIFT;
    cameraMoved = (cameraCenterX != oldCameraX) || (cameraCenterY != oldCameraY);

    treeTick++;
    if (treeTick >= R3_TREE_HOLD_TICKS) { treeTick=0; treeFrame=(treeFrame+1)%WT_TREE_FRAMES; treesChanged=TRUE; }
    waterTick++;
    if (waterTick >= R3_WATER_HOLD_TICKS) { waterTick=0; waterFrame=(waterFrame+1)%WT_WATER_FRAMES; waterChanged=TRUE; }

    if (cameraMoved)
    {
        s16 tx = (s16)(cameraLeft() >> 3), ty = (s16)(cameraTop() >> 3);
        if ((tx != lastCameraTileX) || (ty != lastCameraTileY)) updateStreaming();
        applyScroll(); updateHudNumbers();
    }
    if (waterChanged || treesChanged) refreshVisibleAnimatedCells(waterChanged, treesChanged);

    minimapTick++;
    if ((targetMoved || cameraMoved) && minimapTick >= R3_MINIMAP_HOLD_TICKS)
    {
        minimapTick=0; drawMiniMap();
    }
}

bool R3_pointInsideBattlefield'''
s = sub1(s, r'void R3_battleUpdate\(void\).*?bool R3_pointInsideBattlefield', update, 'camera update')
C.write_text(s, encoding='utf-8')

h = H.read_text(encoding='utf-8')
if 'R3_battleSetCameraTarget' not in h:
    h = h.replace('void R3_battleUpdate(void);', 'void R3_battleUpdate(void);\nvoid R3_battleSetCameraTarget(s32 worldX, s32 worldY);')
H.write_text(h, encoding='utf-8')

g = GEN.read_text(encoding='utf-8')
grass = '''for v in range(GRASS_META):
    r=random.Random(1000+v); im=pimg(32,32,4); d=ImageDraw.Draw(im)
    for _ in range(7):
        x=r.randrange(-8,32); y=r.randrange(-8,32); rx=r.randrange(5,13); ry=r.randrange(3,9)
        c=r.choice([3,5,6,7,8]); d.ellipse((x-rx,y-ry,x+rx,y+ry),fill=c)
    for _ in range(22):
        x=r.randrange(1,31); y=r.randrange(2,31); c=r.choice([1,2,7,8,10]); d.point((x,y),fill=c)
        if r.random()<.55:d.point((x,y-1),fill=c)
        if r.random()<.20 and x+1<32:d.point((x+1,y),fill=c)
    for _ in range(5):
        x=r.randrange(3,29); y=r.randrange(3,29); c=r.choice([9,10,12]); d.rectangle((x,y,x+r.randrange(1,3),y+r.randrange(0,2)),fill=c)
    split_put(world,GRASS_BASE+v*16,im,4,4,WORLD_COLS)

'''
g = sub1(g, r'for v in range\(GRASS_META\):.*?(?=for v in range\(ROAD_META\):)', grass, 'grass assets')
road = '''for v in range(ROAD_META):
    r=random.Random(2000+v); im=pimg(32,32,4); d=ImageDraw.Draw(im)
    for _ in range(10):
        x=r.randrange(-4,32); y=r.randrange(-4,32); w=r.randrange(3,11); h=r.randrange(2,6)
        c=r.choice([2,3,5,6,8]); d.ellipse((x,y,x+w,y+h),fill=c)
    for yy in (8+(v%2),23-((v+1)%2)):
        for x in range(32):
            if ((x+v)&3)!=0:d.point((x,yy),fill=r.choice([8,9,10]))
            if (x+v)%7==0 and yy+1<32:d.point((x,yy+1),fill=6)
    for _ in range(6):
        x=r.randrange(2,30); y=r.randrange(2,30); c=r.choice([1,6,9,12]); d.rectangle((x,y,x+1,y+1),fill=c)
    split_put(world,ROAD_BASE+v*16,im,4,4,WORLD_COLS)

'''
g = sub1(g, r'for v in range\(ROAD_META\):.*?(?=for var in range\(WATER_VARIANTS\):)', road, 'road assets')
water = '''for var in range(WATER_VARIANTS):
    for frame in range(WATER_FRAMES):
        im=pimg(16,16,5); d=ImageDraw.Draw(im); r=random.Random(3000+var*100+frame)
        for band in range(4):
            y=(2+band*4+(var&1))%16; start=(frame*2+band*5+var*3)%16; length=4+((band+var)%4)
            for t in range(length):
                x=(start+t)%16; d.point((x,y),fill=1 if 1<=t<=length-2 else 2)
                if t==2 and (band+frame)%2==0 and y+1<16:d.point((x,y+1),fill=4)
        for _ in range(5): d.point((r.randrange(16),r.randrange(16)),fill=r.choice([3,4,6,7]))
        split_put(world,WATER_BASE+(var*WATER_FRAMES+frame)*4,im,2,2,WORLD_COLS)

'''
g = sub1(g, r'for var in range\(WATER_VARIANTS\):.*?(?=for m in range\(SHORE_META\):)', water, 'water assets')
GEN.write_text(g, encoding='utf-8')

TEST.write_text('''#!/usr/bin/env python3
from pathlib import Path
import json
WORLD_PX=8192; VIEW_W=224; VIEW_H=192; PLANE_W=64; PLANE_H=32; PREF_L=18; PREF_T=4
TICKS=36000; FP=8; RESPONSE=3; MAX_STEP=5<<FP; MINIMAP_STEP_TILES=24

def smooth(pos,target):
    d=target-pos
    if -8<d<8:return target
    st=d>>RESPONSE; st=max(-MAX_STEP,min(MAX_STEP,st))
    if st==0:st=1 if d>0 else -1
    return pos+st
minx=VIEW_W//2; maxx=WORLD_PX-VIEW_W//2; miny=VIEW_H//2; maxy=WORLD_PX-VIEW_H//2
tx=ty=WORLD_PX//2; cxq=tx<<FP; cyq=ty<<FP
origin_x=((tx-VIEW_W//2)>>3)-PREF_L; origin_y=((ty-VIEW_H//2)>>3)-PREF_T; slots={}
def slot(x,y):return(x&63,y&31)
def load(x,y):slots[slot(x,y)]=(x,y)
for y in range(origin_y,origin_y+PLANE_H):
    for x in range(origin_x,origin_x+PLANE_W):load(x,y)
cross_x=cross_y=bounces=0; vx=4; vy=3; max_lag=0
for tick in range(TICKS):
    tx+=vx;ty+=vy
    if tx<minx or tx>maxx:tx=max(minx,min(maxx,tx));vx=-vx;bounces+=1
    if ty<miny or ty>maxy:ty=max(miny,min(maxy,ty));vy=-vy;bounces+=1
    cxq=smooth(cxq,tx<<FP);cyq=smooth(cyq,ty<<FP);cx=cxq>>FP;cy=cyq>>FP
    max_lag=max(max_lag,abs(tx-cx),abs(ty-cy));camx=(cx-VIEW_W//2)>>3;camy=(cy-VIEW_H//2)>>3
    target_x=camx-PREF_L;target_y=camy-PREF_T
    while origin_x<target_x:
        origin_x+=1;cross_x+=1;wx=origin_x+PLANE_W-1
        for y in range(origin_y,origin_y+PLANE_H):load(wx,y)
    while origin_x>target_x:
        origin_x-=1;cross_x+=1
        for y in range(origin_y,origin_y+PLANE_H):load(origin_x,y)
    while origin_y<target_y:
        origin_y+=1;cross_y+=1;wy=origin_y+PLANE_H-1
        for x in range(origin_x,origin_x+PLANE_W):load(x,wy)
    while origin_y>target_y:
        origin_y-=1;cross_y+=1
        for x in range(origin_x,origin_x+PLANE_W):load(x,origin_y)
    if tick%47==0:
        for y in range(camy-1,camy+25):
            for x in range(camx-1,camx+29):assert slots[slot(x,y)]==(x,y)
for _ in range(240):cxq=smooth(cxq,tx<<FP);cyq=smooth(cyq,ty<<FP)
assert cxq==(tx<<FP) and cyq==(ty<<FP)
report={'ticks':TICKS,'nominal_minutes':10,'ring':'64x32','world_px':'8192x8192','column_stream_events':cross_x,'row_stream_events':cross_y,'edge_bounces':bounces,'camera_model':'Q8 target follow','max_follow_lag_px':max_lag,'settles_exactly_on_target':True,'minimap_sample_step_tiles':24,'minimap_visible_world_px':'1920x1536','status':'PASS'}
out=Path(__file__).resolve().parents[1]/'out';out.mkdir(exist_ok=True);(out/'R3_STREAM_STRESS.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))
''', encoding='utf-8')

# Source contract: fail before SGDK if the visual addressing regresses.
final = C.read_text(encoding='utf-8')
for token in ('WT_GRASS_BASE 1','WT_ROAD_BASE 193','WT_WATER_BASE 321','WT_TREE_BASE 769','WT_TREE_FRAME_TILES 12','R3_MINIMAP_SAMPLE_STEP 24','smoothCameraAxis','R3_battleSetCameraTarget'):
    if token not in final: raise SystemExit('missing source contract: '+token)
print('R3 visual/camera v3 transform PASS')
