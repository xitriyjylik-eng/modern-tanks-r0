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
#define R3_MINIMAP_SAMPLE_STEP 24 /* 24 world tiles = 192 px per minimap cell */
#define R3_TREE_HOLD_TICKS 10
#define R3_WATER_HOLD_TICKS 8
#define R3_MINIMAP_HOLD_TICKS 12
#define R3_CAMERA_FP_SHIFT 8
#define R3_CAMERA_RESPONSE_SHIFT 3
#define R3_CAMERA_MAX_STEP_Q8 (5L << R3_CAMERA_FP_SHIFT)

/* Exact layout emitted by build_r3_assets.py. Large assets are metatiles,
 * not bags of unrelated 8x8 tiles. Keeping their local coordinates intact is
 * essential for the R2-quality visual language. */
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
#define WT_WATER_W 2
#define WT_WATER_H 2
#define WT_SHORE_BASE 417
#define WT_SHORE_VARIANTS_PER_SIDE 3
#define WT_SHORE_W 4
#define WT_SHORE_H 4
#define WT_BRIDGE_BASE 513
#define WT_BRIDGE_META 4
#define WT_BRIDGE_W 4
#define WT_BRIDGE_H 4
#define WT_DECOR_BASE 577
#define WT_DECOR_META 24
#define WT_DECOR_W 2
#define WT_DECOR_H 2
#define WT_STRUCT_BASE 673
#define WT_STRUCT_META 8
#define WT_STRUCT_W 4
#define WT_STRUCT_H 3
#define WT_TREE_BASE 769
#define WT_TREE_FRAMES 12
#define WT_TREE_W 4
#define WT_TREE_H 3
#define WT_TREE_FRAME_TILES (WT_TREE_W * WT_TREE_H)

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
static s32 cameraPosXQ8 = (R3_WORLD_WIDTH_PX / 2) << R3_CAMERA_FP_SHIFT;
static s32 cameraPosYQ8 = (R3_WORLD_HEIGHT_PX / 2) << R3_CAMERA_FP_SHIFT;
static s32 cameraTargetXQ8 = (R3_WORLD_WIDTH_PX / 2) << R3_CAMERA_FP_SHIFT;
static s32 cameraTargetYQ8 = (R3_WORLD_HEIGHT_PX / 2) << R3_CAMERA_FP_SHIFT;
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

