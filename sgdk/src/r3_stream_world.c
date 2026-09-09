#include <genesis.h>
#include "resources.h"
#include "r3_stream_world.h"

#define R3_WORLD_W_PX 960
#define R3_WORLD_H_PX 960
#define R3_WORLD_W_TILES 120
#define R3_WORLD_H_TILES 120

#define R3_VIEW_W_PX 224
#define R3_VIEW_H_PX 192

#define R3_RING_W 32
#define R3_RING_H 32
#define R3_PLANE_W 64
#define R3_PLANE_H 32

#define R3_PATTERN_BASE TILE_USER_INDEX
#define R3_RING_PATTERN_COUNT (R3_RING_W * R3_RING_H)
#define R3_HUD_BG_TILE (R3_PATTERN_BASE + R3_RING_PATTERN_COUNT)
#define R3_HUD_SOLID_TILE (R3_HUD_BG_TILE + 1)

#define R3_CAM_FP_SHIFT 8
#define R3_CAM_RESPONSE_SHIFT 2
#define R3_CAM_MAX_STEP_Q8 (5L << R3_CAM_FP_SHIFT)
#define R3_CAM_SNAP_Q8 24

static s32 cameraPosXQ8 = 88L << R3_CAM_FP_SHIFT;
static s32 cameraPosYQ8 = 320L << R3_CAM_FP_SHIFT;
static s32 cameraTargetXQ8 = 88L << R3_CAM_FP_SHIFT;
static s32 cameraTargetYQ8 = 320L << R3_CAM_FP_SHIFT;

static s16 loadedBaseTileX = 0;
static s16 loadedBaseTileY = 0;

static const u8 * const r3TileChunks[8] =
{
    r3_target_world_tiles_0,
    r3_target_world_tiles_1,
    r3_target_world_tiles_2,
    r3_target_world_tiles_3,
    r3_target_world_tiles_4,
    r3_target_world_tiles_5,
    r3_target_world_tiles_6,
    r3_target_world_tiles_7
};

static s32 clampQ8(s32 value, s32 loPx, s32 hiPx)
{
    const s32 lo = loPx << R3_CAM_FP_SHIFT;
    const s32 hi = hiPx << R3_CAM_FP_SHIFT;
    if (value < lo) return lo;
    if (value > hi) return hi;
    return value;
}

static s32 smoothCameraAxis(s32 current, s32 target)
{
    s32 delta = target - current;
    s32 step;

    if ((delta > -R3_CAM_SNAP_Q8) && (delta < R3_CAM_SNAP_Q8))
        return target;

    step = delta >> R3_CAM_RESPONSE_SHIFT;
    if (step == 0) step = (delta > 0) ? 1 : -1;
    if (step > R3_CAM_MAX_STEP_Q8) step = R3_CAM_MAX_STEP_Q8;
    if (step < -R3_CAM_MAX_STEP_Q8) step = -R3_CAM_MAX_STEP_Q8;
    return current + step;
}

static u16 clampWorldTileX(s16 wx)
{
    if (wx < 0) return 0;
    if (wx >= R3_WORLD_W_TILES) return R3_WORLD_W_TILES - 1;
    return (u16) wx;
}

static u16 clampWorldTileY(s16 wy)
{
    if (wy < 0) return 0;
    if (wy >= R3_WORLD_H_TILES) return R3_WORLD_H_TILES - 1;
    return (u16) wy;
}

static void loadWorldTile(s16 worldX, s16 worldY, TransferMethod tm)
{
    const u16 wx = clampWorldTileX(worldX);
    const u16 wy = clampWorldTileY(worldY);
    const u32 worldIndex = ((u32) wy * R3_WORLD_W_TILES) + wx;
    const u16 chunk = wy / 15;
    const u16 localRow = wy % 15;
    const u32 localIndex = ((u32) localRow * R3_WORLD_W_TILES) + wx;

    const u16 slotX = ((u16) worldX) & (R3_RING_W - 1);
    const u16 slotY = ((u16) worldY) & (R3_RING_H - 1);
    const u16 planeX = ((u16) worldX) & (R3_PLANE_W - 1);
    const u16 planeY = ((u16) worldY) & (R3_PLANE_H - 1);

    const u16 patternIndex = R3_PATTERN_BASE + (slotY * R3_RING_W) + slotX;
    const u8 palette = r3_target_world_banks[worldIndex] & 3;
    const u8 *pattern = r3TileChunks[chunk] + (localIndex * 32UL);

    VDP_loadTileData((const u32 *) pattern, patternIndex, 1, tm);
    VDP_setTileMapXY(BG_B,
                     TILE_ATTR_FULL(palette, FALSE, FALSE, FALSE, patternIndex),
                     planeX, planeY);
}

static void loadColumn(s16 worldX, s16 baseY, TransferMethod tm)
{
    s16 y;
    for (y = 0; y < R3_RING_H; y++)
        loadWorldTile(worldX, baseY + y, tm);
}

static void loadRow(s16 baseX, s16 worldY, TransferMethod tm)
{
    s16 x;
    for (x = 0; x < R3_RING_W; x++)
        loadWorldTile(baseX + x, worldY, tm);
}

static void loadInitialRing(s16 baseX, s16 baseY)
{
    s16 y;
    s16 x;

    for (y = 0; y < R3_RING_H; y++)
        for (x = 0; x < R3_RING_W; x++)
            loadWorldTile(baseX + x, baseY + y, CPU);

    loadedBaseTileX = baseX;
    loadedBaseTileY = baseY;
}

static void updateStreaming(s16 tileX, s16 tileY)
{
    while (tileX > loadedBaseTileX)
    {
        loadColumn(loadedBaseTileX + R3_RING_W, loadedBaseTileY, CPU);
        loadedBaseTileX++;
    }

    while (tileX < loadedBaseTileX)
    {
        loadedBaseTileX--;
        loadColumn(loadedBaseTileX, loadedBaseTileY, CPU);
    }

    while (tileY > loadedBaseTileY)
    {
        loadRow(loadedBaseTileX, loadedBaseTileY + R3_RING_H, CPU);
        loadedBaseTileY++;
    }

    while (tileY < loadedBaseTileY)
    {
        loadedBaseTileY--;
        loadRow(loadedBaseTileX, loadedBaseTileY, CPU);
    }
}

static void drawHud(void)
{
    /* Opaque dark panel tile and a generic solid tile for bars. */
    VDP_fillTileData(0x77, R3_HUD_BG_TILE, 1, TRUE);
    VDP_fillTileData(0x11, R3_HUD_SOLID_TILE, 1, TRUE);

    VDP_clearPlane(BG_A, TRUE);

    VDP_fillTileMapRect(BG_A,
        TILE_ATTR_FULL(PAL0, TRUE, FALSE, FALSE, R3_HUD_BG_TILE),
        28, 0, 12, 24);

    VDP_fillTileMapRect(BG_A,
        TILE_ATTR_FULL(PAL0, TRUE, FALSE, FALSE, R3_HUD_BG_TILE),
        0, 24, 40, 4);

    VDP_setTextPlane(BG_A);
    VDP_setTextPalette(PAL0);
    VDP_setTextPriority(TRUE);

    VDP_drawText("T-1", 30, 1);
    VDP_drawText("HP", 29, 4);
    VDP_drawText("ARMOR", 29, 7);
    VDP_drawText("AMMO", 29, 10);
    VDP_drawText("SCORE", 29, 14);
    VDP_drawText("002480", 29, 16);

    /* Simple segmented bars; final HUD art will replace these text-era blocks. */
    VDP_fillTileMapRect(BG_A,
        TILE_ATTR_FULL(PAL2, TRUE, FALSE, FALSE, R3_HUD_SOLID_TILE),
        32, 4, 6, 1);

    VDP_fillTileMapRect(BG_A,
        TILE_ATTR_FULL(PAL1, TRUE, FALSE, FALSE, R3_HUD_SOLID_TILE),
        32, 7, 5, 1);

    VDP_drawText("B: MENU", 1, 25);
    VDP_drawText("A/C: FAST", 15, 25);
}

void R3_worldEnter(void)
{
    const s16 cameraX = (s16)(cameraPosXQ8 >> R3_CAM_FP_SHIFT);
    const s16 cameraY = (s16)(cameraPosYQ8 >> R3_CAM_FP_SHIFT);
    const s16 tileX = cameraX >> 3;
    const s16 tileY = cameraY >> 3;

    VDP_setPlaneSize(R3_PLANE_W, R3_PLANE_H, TRUE);
    VDP_setScrollingMode(HSCROLL_PLANE, VSCROLL_PLANE);

    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);

    /* Exact four palette banks from the accepted R2 artwork. */
    PAL_setColors(0, r2_menu_bg.palette->data, 64, CPU);

    loadInitialRing(tileX, tileY);
    drawHud();

    VDP_setHorizontalScroll(BG_A, 0);
    VDP_setVerticalScroll(BG_A, 0);
    VDP_setHorizontalScroll(BG_B, -cameraX);
    VDP_setVerticalScroll(BG_B, cameraY);
}

void R3_worldLeave(void)
{
    VDP_setHorizontalScroll(BG_A, 0);
    VDP_setVerticalScroll(BG_A, 0);
    VDP_setHorizontalScroll(BG_B, 0);
    VDP_setVerticalScroll(BG_B, 0);

    /* R2 menu needs 40 visible tile columns. */
    VDP_setPlaneSize(64, 32, TRUE);
}

void R3_worldUpdate(u16 held)
{
    const s32 inputStepQ8 = ((held & BUTTON_C) ? 3L : 2L) << R3_CAM_FP_SHIFT;
    s16 cameraX;
    s16 cameraY;
    s16 tileX;
    s16 tileY;

    if ((held & BUTTON_LEFT) && !(held & BUTTON_RIGHT)) cameraTargetXQ8 -= inputStepQ8;
    if ((held & BUTTON_RIGHT) && !(held & BUTTON_LEFT)) cameraTargetXQ8 += inputStepQ8;
    if ((held & BUTTON_UP) && !(held & BUTTON_DOWN)) cameraTargetYQ8 -= inputStepQ8;
    if ((held & BUTTON_DOWN) && !(held & BUTTON_UP)) cameraTargetYQ8 += inputStepQ8;

    cameraTargetXQ8 = clampQ8(cameraTargetXQ8, 0, R3_WORLD_W_PX - R3_VIEW_W_PX);
    cameraTargetYQ8 = clampQ8(cameraTargetYQ8, 0, R3_WORLD_H_PX - R3_VIEW_H_PX);

    cameraPosXQ8 = smoothCameraAxis(cameraPosXQ8, cameraTargetXQ8);
    cameraPosYQ8 = smoothCameraAxis(cameraPosYQ8, cameraTargetYQ8);

    cameraX = (s16)(cameraPosXQ8 >> R3_CAM_FP_SHIFT);
    cameraY = (s16)(cameraPosYQ8 >> R3_CAM_FP_SHIFT);
    tileX = cameraX >> 3;
    tileY = cameraY >> 3;

    updateStreaming(tileX, tileY);

    VDP_setHorizontalScroll(BG_B, -cameraX);
    VDP_setVerticalScroll(BG_B, cameraY);
}
