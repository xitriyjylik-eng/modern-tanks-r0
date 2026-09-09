#include <genesis.h>
#include "resources.h"
#include "battle_r3.h"

/*
 * Modern Tanks R3 — Battle Renderer / HUD foundation.
 *
 * The 320x224 display is only a viewport. The stress world is 8192x8192 px.
 * Plane B = lower world; Plane A = upper/decor world; Window = fixed L-shaped HUD.
 * A 64x32 hardware plane is used as a circular cache. World tiles are generated
 * on demand from deterministic coordinates, so world size is not tied to VRAM.
 */

#define R3_TILE_SIZE 8
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
#define R3_TREE_HOLD_TICKS 10
#define R3_WATER_HOLD_TICKS 8
#define R3_MINIMAP_HOLD_TICKS 12

#define WT_BLANK 0
#define WT_GRASS_BASE 1
#define WT_GRASS_COUNT 16
#define WT_ROAD_BASE 17
#define WT_ROAD_COUNT 12
#define WT_WATER_BASE 29
#define WT_WATER_COUNT 8
#define WT_SHORE_BASE 37
#define WT_SHORE_COUNT 8
#define WT_DECOR_BASE 45
#define WT_DECOR_COUNT 8
#define WT_BRIDGE_BASE 53
#define WT_BRIDGE_COUNT 8
#define WT_STRUCT_BASE 61
#define WT_STRUCT_COUNT 12
#define WT_TREE_BASE 73
#define WT_TREE_FRAMES 12
#define WT_TREE_QUADS 4
#define WT_EXTRA_BASE 121
#define WT_EXTRA_COUNT 7

#define HT_BG 0
#define HT_SOLID 1
#define HT_HLINE 2
#define HT_VLINE 3
#define HT_CORNER 4
#define HT_DIAG 5
#define HT_DOT 6
#define HT_GLYPH_BASE 8

static const char r3Charset[] = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ:-/ .";

static u16 worldTileBase = 0;
static u16 hudTileBase = 0;
static s32 cameraCenterX = R3_WORLD_WIDTH_PX / 2;
static s32 cameraCenterY = R3_WORLD_HEIGHT_PX / 2;
static s16 loadedOriginX = 0;
static s16 loadedOriginY = 0;
static s16 lastCameraTileX = -32768;
static s16 lastCameraTileY = -32768;
static u16 padHeld = 0;
static u16 treeFrame = 0;
static u16 waterFrame = 0;
static u16 treeTick = 0;
static u16 waterTick = 0;
static u16 minimapTick = 0;
static bool active = FALSE;

static u16 hash16(s16 x, s16 y)
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

static s16 riverCenterX(s16 worldY)
{
    /* Broad, gently meandering north/south river crossing the stress-map center. */
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

static bool isWater(s16 wx, s16 wy)
{
    s16 d = wx - riverCenterX(wy);
    if (d < 0) d = -d;
    return d <= 6;
}

static bool isShore(s16 wx, s16 wy)
{
    s16 d = wx - riverCenterX(wy);
    if (d < 0) d = -d;
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
    return isWater(wx, wy) && isRoad(wx, wy);
}

static bool forestField(s16 wx, s16 wy)
{
    u16 coarse;
    if (!worldInBounds(wx, wy) || isWater(wx, wy) || isShore(wx, wy) || isRoad(wx, wy)) return FALSE;
    coarse = hash16(wx >> 4, wy >> 4);
    /* Stress belt plus procedural patches. */
    if ((wx > 470) && (wx < 550) && (wy > 440) && (wy < 590)) return TRUE;
    return (coarse & 255) < 82;
}

static bool hasTreeAnchor(s16 ax, s16 ay)
{
    if ((ax & 1) || (ay & 1)) return FALSE;
    if (!forestField(ax, ay) || !forestField(ax + 1, ay + 1)) return FALSE;
    return (hash16(ax, ay) & 7) < 5;
}

static u16 baseTileAttr(s16 wx, s16 wy)
{
    u16 h = hash16(wx, wy);
    u16 id;
    u16 pal;

    if (!worldInBounds(wx, wy))
        return TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, worldTileBase + WT_STRUCT_BASE + 9);

    if (isBridge(wx, wy))
    {
        id = WT_BRIDGE_BASE + (h % WT_BRIDGE_COUNT);
        pal = PAL3;
    }
    else if (isWater(wx, wy))
    {
        id = WT_WATER_BASE + ((waterFrame + (h & 3)) % WT_WATER_COUNT);
        pal = PAL1;
    }
    else if (isShore(wx, wy))
    {
        id = WT_SHORE_BASE + (h % WT_SHORE_COUNT);
        pal = PAL3;
    }
    else if (isRoad(wx, wy))
    {
        id = WT_ROAD_BASE + (h % WT_ROAD_COUNT);
        pal = PAL3;
    }
    else
    {
        id = WT_GRASS_BASE + (h % WT_GRASS_COUNT);
        pal = PAL2;
    }

    return TILE_ATTR_FULL(pal, FALSE, FALSE, FALSE, worldTileBase + id);
}

static u16 overlayTileAttr(s16 wx, s16 wy)
{
    s16 ax = wx & (s16)~1;
    s16 ay = wy & (s16)~1;
    u16 h;

    if (!worldInBounds(wx, wy))
        return TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, worldTileBase + WT_BLANK);

    if (hasTreeAnchor(ax, ay))
    {
        u16 phase = (hash16(ax, ay) >> 4) % WT_TREE_FRAMES;
        u16 frame = (treeFrame + phase) % WT_TREE_FRAMES;
        u16 q = (u16)((wy - ay) * 2 + (wx - ax));
        return TILE_ATTR_FULL(PAL2, TRUE, FALSE, FALSE,
                              worldTileBase + WT_TREE_BASE + frame * WT_TREE_QUADS + q);
    }

    h = hash16(wx, wy);
    if (!isWater(wx, wy) && !isShore(wx, wy) && !isRoad(wx, wy))
    {
        if ((h & 255) < 9)
            return TILE_ATTR_FULL(PAL0, TRUE, FALSE, FALSE,
                                  worldTileBase + WT_DECOR_BASE + (h % WT_DECOR_COUNT));
        if ((h & 511) == 127)
            return TILE_ATTR_FULL(PAL3, TRUE, FALSE, FALSE,
                                  worldTileBase + WT_STRUCT_BASE + (h % WT_STRUCT_COUNT));
    }

    return TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, worldTileBase + WT_BLANK);
}

static void setWorldCell(s16 wx, s16 wy)
{
    u16 px = ((u16)wx) & (R3_PLANE_W - 1);
    u16 py = ((u16)wy) & (R3_PLANE_H - 1);
    VDP_setTileMapXY(BG_B, baseTileAttr(wx, wy), px, py);
    VDP_setTileMapXY(BG_A, overlayTileAttr(wx, wy), px, py);
}

static void streamColumn(s16 wx)
{
    s16 y;
    for (y = loadedOriginY; y < (loadedOriginY + R3_PLANE_H); y++) setWorldCell(wx, y);
}

static void streamRow(s16 wy)
{
    s16 x;
    for (x = loadedOriginX; x < (loadedOriginX + R3_PLANE_W); x++) setWorldCell(x, wy);
}

static void fillRing(void)
{
    s16 x, y;
    for (y = loadedOriginY; y < (loadedOriginY + R3_PLANE_H); y++)
        for (x = loadedOriginX; x < (loadedOriginX + R3_PLANE_W); x++)
            setWorldCell(x, y);
}

static s32 cameraLeft(void) { return cameraCenterX - (R3_BATTLEFIELD_WIDTH_PX / 2); }
static s32 cameraTop(void)  { return cameraCenterY - (R3_BATTLEFIELD_HEIGHT_PX / 2); }

static void applyScroll(void)
{
    s16 sx = (s16)(cameraLeft() & 511);
    s16 sy = (s16)(cameraTop() & 255);
    VDP_setHorizontalScroll(BG_A, -sx);
    VDP_setHorizontalScroll(BG_B, -sx);
    /* SGDK positive vertical value moves the plane up, matching camera-down. */
    VDP_setVerticalScroll(BG_A, sy);
    VDP_setVerticalScroll(BG_B, sy);
}

static u16 glyphId(char c)
{
    u16 i = 0;
    while (r3Charset[i])
    {
        if (r3Charset[i] == c) return HT_GLYPH_BASE + i;
        i++;
    }
    return HT_GLYPH_BASE + 39; /* space */
}

static void hudText(u16 x, u16 y, const char *text)
{
    while (*text && x < 40)
    {
        VDP_setTileMapXY(WINDOW,
                         TILE_ATTR_FULL(PAL0, TRUE, FALSE, FALSE, hudTileBase + glyphId(*text)),
                         x++, y);
        text++;
    }
}

static void hudNumber4(u16 x, u16 y, u16 value)
{
    char s[5];
    s[4] = 0;
    s[3] = '0' + (value % 10); value /= 10;
    s[2] = '0' + (value % 10); value /= 10;
    s[1] = '0' + (value % 10); value /= 10;
    s[0] = '0' + (value % 10);
    hudText(x, y, s);
}

static u16 miniMapAttr(s16 wx, s16 wy)
{
    if (!worldInBounds(wx, wy)) return TILE_ATTR_FULL(PAL0, TRUE, FALSE, FALSE, hudTileBase + HT_BG);
    if (isBridge(wx, wy)) return TILE_ATTR_FULL(PAL3, TRUE, FALSE, FALSE, hudTileBase + HT_SOLID);
    if (isWater(wx, wy)) return TILE_ATTR_FULL(PAL1, TRUE, FALSE, FALSE, hudTileBase + HT_SOLID);
    if (isRoad(wx, wy) || isShore(wx, wy)) return TILE_ATTR_FULL(PAL3, TRUE, FALSE, FALSE, hudTileBase + HT_SOLID);
    if (forestField(wx, wy)) return TILE_ATTR_FULL(PAL2, TRUE, FALSE, FALSE, hudTileBase + HT_SOLID);
    return TILE_ATTR_FULL(PAL2, TRUE, FALSE, FALSE, hudTileBase + HT_BG);
}

static void drawMiniMap(void)
{
    s16 centerTileX = (s16)(cameraCenterX >> 3);
    s16 centerTileY = (s16)(cameraCenterY >> 3);
    u16 x, y;
    for (y = 0; y < R3_MINIMAP_H; y++)
    {
        for (x = 0; x < R3_MINIMAP_W; x++)
        {
            s16 wx = centerTileX + ((s16)x - (R3_MINIMAP_W / 2)) * 4;
            s16 wy = centerTileY + ((s16)y - (R3_MINIMAP_H / 2)) * 4;
            VDP_setTileMapXY(WINDOW, miniMapAttr(wx, wy), R3_MINIMAP_X + x, R3_MINIMAP_Y + y);
        }
    }
    VDP_setTileMapXY(WINDOW,
                     TILE_ATTR_FULL(PAL0, TRUE, FALSE, FALSE, hudTileBase + HT_DOT),
                     R3_MINIMAP_X + R3_MINIMAP_W / 2,
                     R3_MINIMAP_Y + R3_MINIMAP_H / 2);
}

static void drawHudFrame(void)
{
    u16 x, y;
    u16 bg = TILE_ATTR_FULL(PAL0, TRUE, FALSE, FALSE, hudTileBase + HT_BG);
    u16 line = TILE_ATTR_FULL(PAL0, TRUE, FALSE, FALSE, hudTileBase + HT_HLINE);

    /* Window is an L shape because Genesis combines H/V window conditions with OR. */
    VDP_setWindowHPos(TRUE, 14); /* 14 * 16 = 224px -> right 96px */
    VDP_setWindowVPos(TRUE, 24); /* 24 * 8 = 192px -> bottom 32px */

    for (y = 0; y < 28; y++)
        for (x = 0; x < 40; x++)
            VDP_setTileMapXY(WINDOW, bg, x, y);

    for (y = 0; y < 24; y++) VDP_setTileMapXY(WINDOW,
        TILE_ATTR_FULL(PAL0, TRUE, FALSE, FALSE, hudTileBase + HT_VLINE), 28, y);
    for (x = 0; x < 40; x++) VDP_setTileMapXY(WINDOW, line, x, 24);

    hudText(30, 1, "R3 WORLD");
    hudText(29, 3, "X:");
    hudText(29, 5, "Y:");
    hudText(30, 17, "MAP 8K");
    hudText(29, 20, "C FAST");
    hudText(29, 22, "B MENU");
    hudText(1, 25, "STREAMED WORLD / PLANE A+B / R3");
    hudText(1, 27, "8192X8192  TREES+WATER  HUD FIXED");
    drawMiniMap();
}

static void updateHudNumbers(void)
{
    hudNumber4(31, 3, (u16)(cameraCenterX >> 3));
    hudNumber4(31, 5, (u16)(cameraCenterY >> 3));
}

static void refreshVisibleAnimatedCells(bool waterChanged, bool treesChanged)
{
    s16 left = (s16)(cameraLeft() >> 3) - 1;
    s16 top = (s16)(cameraTop() >> 3) - 1;
    s16 x, y;
    for (y = top; y < top + R3_VIEW_H_TILES + 2; y++)
    {
        for (x = left; x < left + R3_VIEW_W_TILES + 2; x++)
        {
            if (waterChanged && isWater(x, y))
                VDP_setTileMapXY(BG_B, baseTileAttr(x, y), ((u16)x)&63, ((u16)y)&31);
            if (treesChanged)
                VDP_setTileMapXY(BG_A, overlayTileAttr(x, y), ((u16)x)&63, ((u16)y)&31);
        }
    }
}

static void updateStreaming(void)
{
    s16 camTileX = (s16)(cameraLeft() >> 3);
    s16 camTileY = (s16)(cameraTop() >> 3);
    s16 targetOriginX = camTileX - R3_PREFETCH_LEFT;
    s16 targetOriginY = camTileY - R3_PREFETCH_TOP;

    while (loadedOriginX < targetOriginX)
    {
        loadedOriginX++;
        streamColumn(loadedOriginX + R3_PLANE_W - 1);
    }
    while (loadedOriginX > targetOriginX)
    {
        loadedOriginX--;
        streamColumn(loadedOriginX);
    }
    while (loadedOriginY < targetOriginY)
    {
        loadedOriginY++;
        streamRow(loadedOriginY + R3_PLANE_H - 1);
    }
    while (loadedOriginY > targetOriginY)
    {
        loadedOriginY--;
        streamRow(loadedOriginY);
    }

    lastCameraTileX = camTileX;
    lastCameraTileY = camTileY;
}

void R3_battleEnter(void)
{
    u16 next;
    if (active) return;

    VDP_setTextPlane(BG_A);
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
    VDP_clearPlane(WINDOW, TRUE);

    /* Keep exactly the accepted R2 64-color visual language in CRAM. */
    PAL_setColors(0, r2_menu_bg.palette->data, r2_menu_bg.palette->length, CPU);

    worldTileBase = TILE_USER_INDEX;
    next = worldTileBase + r3_world_tiles.numTile;
    hudTileBase = next;
    next += r3_hud_tiles.numTile;
    if ((next - 1) > TILE_USER_MAX_INDEX)
    {
        /* Fail visibly but safely; current R3 assets are far below this limit. */
        PAL_setColor(0, RGB24_TO_VDPCOLOR(0x400000));
        return;
    }

    VDP_loadTileSet(&r3_world_tiles, worldTileBase, CPU);
    VDP_loadTileSet(&r3_hud_tiles, hudTileBase, CPU);

    cameraCenterX = R3_WORLD_WIDTH_PX / 2;
    cameraCenterY = R3_WORLD_HEIGHT_PX / 2;
    loadedOriginX = (s16)(cameraLeft() >> 3) - R3_PREFETCH_LEFT;
    loadedOriginY = (s16)(cameraTop() >> 3) - R3_PREFETCH_TOP;
    treeFrame = waterFrame = treeTick = waterTick = minimapTick = 0;
    padHeld = 0;
    fillRing();
    applyScroll();
    drawHudFrame();
    updateHudNumbers();
    lastCameraTileX = (s16)(cameraLeft() >> 3);
    lastCameraTileY = (s16)(cameraTop() >> 3);
    active = TRUE;
}

void R3_battleLeave(void)
{
    if (!active) return;
    VDP_setWindowOff();
    VDP_setHorizontalScroll(BG_A, 0);
    VDP_setHorizontalScroll(BG_B, 0);
    VDP_setVerticalScroll(BG_A, 0);
    VDP_setVerticalScroll(BG_B, 0);
    padHeld = 0;
    active = FALSE;
}

void R3_battleSetInput(u16 held, u16 pressed)
{
    (void)pressed;
    padHeld = held;
}

void R3_battleUpdate(void)
{
    s16 speed;
    bool moved = FALSE;
    bool waterChanged = FALSE;
    bool treesChanged = FALSE;
    s32 minX = R3_BATTLEFIELD_WIDTH_PX / 2;
    s32 maxX = R3_WORLD_WIDTH_PX - (R3_BATTLEFIELD_WIDTH_PX / 2);
    s32 minY = R3_BATTLEFIELD_HEIGHT_PX / 2;
    s32 maxY = R3_WORLD_HEIGHT_PX - (R3_BATTLEFIELD_HEIGHT_PX / 2);

    if (!active) return;
    speed = (padHeld & BUTTON_C) ? 4 : 2;
    if (padHeld & BUTTON_LEFT)  { cameraCenterX -= speed; moved = TRUE; }
    if (padHeld & BUTTON_RIGHT) { cameraCenterX += speed; moved = TRUE; }
    if (padHeld & BUTTON_UP)    { cameraCenterY -= speed; moved = TRUE; }
    if (padHeld & BUTTON_DOWN)  { cameraCenterY += speed; moved = TRUE; }
    if (cameraCenterX < minX) cameraCenterX = minX;
    if (cameraCenterX > maxX) cameraCenterX = maxX;
    if (cameraCenterY < minY) cameraCenterY = minY;
    if (cameraCenterY > maxY) cameraCenterY = maxY;

    treeTick++;
    if (treeTick >= R3_TREE_HOLD_TICKS)
    {
        treeTick = 0;
        treeFrame = (treeFrame + 1) % WT_TREE_FRAMES;
        treesChanged = TRUE;
    }
    waterTick++;
    if (waterTick >= R3_WATER_HOLD_TICKS)
    {
        waterTick = 0;
        waterFrame = (waterFrame + 1) % WT_WATER_COUNT;
        waterChanged = TRUE;
    }

    if (moved)
    {
        s16 tx = (s16)(cameraLeft() >> 3);
        s16 ty = (s16)(cameraTop() >> 3);
        if ((tx != lastCameraTileX) || (ty != lastCameraTileY)) updateStreaming();
        applyScroll();
        updateHudNumbers();
    }

    if (waterChanged || treesChanged) refreshVisibleAnimatedCells(waterChanged, treesChanged);

    minimapTick++;
    if (moved && minimapTick >= R3_MINIMAP_HOLD_TICKS)
    {
        minimapTick = 0;
        drawMiniMap();
    }
}

bool R3_pointInsideBattlefield(s16 screenX, s16 screenY)
{
    /* Future R4/R6 sprites must pass this culling gate before VDP submission. */
    return (screenX >= 0) && (screenY >= 0) &&
           (screenX < R3_BATTLEFIELD_WIDTH_PX) && (screenY < R3_BATTLEFIELD_HEIGHT_PX);
}
