#include "map01_stream.h"
#include "resources.h"

#define MAP01_TILE_BYTES 32u
#define MAP01_PREFETCH_TILES 2

static u16 streamTileBase = 0;
static s16 streamOriginX = -1;
static s16 streamOriginY = -1;
static bool streamActive = FALSE;

static s16 clamp_s16(s16 value, s16 low, s16 high)
{
    if (value < low) return low;
    if (value > high) return high;
    return value;
}

static u16 world_tile_index(u16 tx, u16 ty)
{
    return (u16) (ty * MAP01_WORLD_TILES_X + tx);
}

static u16 cache_pattern_index(u16 tx, u16 ty)
{
    return (u16) (streamTileBase + ((ty & 31u) * MAP01_STREAM_CACHE_W) + (tx & 31u));
}

static void map_tilemap_entry(u16 tx, u16 ty)
{
    const u16 worldIndex = world_tile_index(tx, ty);
    const u16 patternIndex = cache_pattern_index(tx, ty);
    const u16 palette = map01_world_tile_palettes[worldIndex] & 3u;

    VDP_setTileMapXY(BG_B,
                     TILE_ATTR_FULL(palette, FALSE, FALSE, FALSE, patternIndex),
                     tx & 63u, ty & 31u);
}

static void load_single_tile(u16 tx, u16 ty)
{
    const u16 worldIndex = world_tile_index(tx, ty);
    const u32 *src = (const u32 *) &map01_world_tiles[(u32) worldIndex * MAP01_TILE_BYTES];

    VDP_loadTileData(src, cache_pattern_index(tx, ty), 1, DMA);
    map_tilemap_entry(tx, ty);
}

/* A complete world row is contiguous in ROM. Split only where the 32-tile
 * VRAM ring wraps. This keeps initial loading to at most two DMAs per row. */
static void load_row(u16 worldY, u16 worldX0)
{
    const u16 slotX = worldX0 & 31u;
    const u16 firstCount = (u16) (MAP01_STREAM_CACHE_W - slotX);
    const u16 secondCount = (u16) (MAP01_STREAM_CACHE_W - firstCount);
    const u16 rowSlot = (worldY & 31u) * MAP01_STREAM_CACHE_W;
    const u16 worldIndex = world_tile_index(worldX0, worldY);
    const u32 *src = (const u32 *) &map01_world_tiles[(u32) worldIndex * MAP01_TILE_BYTES];
    u16 x;

    VDP_loadTileData(src, streamTileBase + rowSlot + slotX, firstCount, DMA);
    if (secondCount)
        VDP_loadTileData(src + ((u32) firstCount * 8u), streamTileBase + rowSlot, secondCount, DMA);

    for (x = 0; x < MAP01_STREAM_CACHE_W; x++)
        map_tilemap_entry((u16) (worldX0 + x), worldY);
}

static void load_column(u16 worldX, u16 worldY0)
{
    u16 y;
    for (y = 0; y < MAP01_STREAM_CACHE_H; y++)
        load_single_tile(worldX, (u16) (worldY0 + y));
}

static void load_full_window(u16 originX, u16 originY)
{
    u16 y;
    for (y = 0; y < MAP01_STREAM_CACHE_H; y++)
        load_row((u16) (originY + y), originX);

    streamOriginX = (s16) originX;
    streamOriginY = (s16) originY;
}

static void desired_origin(u16 scrollX, u16 scrollY, s16 *outX, s16 *outY)
{
    s16 x = (s16) (scrollX >> 3) - MAP01_PREFETCH_TILES;
    s16 y = (s16) (scrollY >> 3) - MAP01_PREFETCH_TILES;

    x = clamp_s16(x, 0, (s16) (MAP01_WORLD_TILES_X - MAP01_STREAM_CACHE_W));
    y = clamp_s16(y, 0, (s16) (MAP01_WORLD_TILES_Y - MAP01_STREAM_CACHE_H));
    *outX = x;
    *outY = y;
}

bool MAP01_streamInit(u16 tileBase, u16 scrollX, u16 scrollY)
{
    s16 originX;
    s16 originY;

    streamTileBase = tileBase;
    streamOriginX = -1;
    streamOriginY = -1;
    streamActive = TRUE;

    /* Palette words are stored big-endian in ROM and already quantized to
     * Mega Drive 3-bit RGB. All four hardware palettes are used by Map 01. */
    PAL_setColors(0, (const u16 *) map01_world_palette, 64, CPU);

    desired_origin(scrollX, scrollY, &originX, &originY);
    load_full_window((u16) originX, (u16) originY);
    MAP01_streamScrollTo(scrollX, scrollY);
    return TRUE;
}

void MAP01_streamScrollTo(u16 scrollX, u16 scrollY)
{
    s16 desiredX;
    s16 desiredY;

    if (!streamActive) return;

    desired_origin(scrollX, scrollY, &desiredX, &desiredY);

    /* Camera moves at <=1.5 px/frame, so normal operation changes by one
     * tile at a time. The loops also make large jumps safe. */
    while (streamOriginX < desiredX)
    {
        streamOriginX++;
        load_column((u16) (streamOriginX + MAP01_STREAM_CACHE_W - 1), (u16) streamOriginY);
    }
    while (streamOriginX > desiredX)
    {
        streamOriginX--;
        load_column((u16) streamOriginX, (u16) streamOriginY);
    }
    while (streamOriginY < desiredY)
    {
        streamOriginY++;
        load_row((u16) (streamOriginY + MAP01_STREAM_CACHE_H - 1), (u16) streamOriginX);
    }
    while (streamOriginY > desiredY)
    {
        streamOriginY--;
        load_row((u16) streamOriginY, (u16) streamOriginX);
    }

    VDP_setHorizontalScroll(BG_B, -(s16) scrollX);
    VDP_setVerticalScroll(BG_B, (s16) scrollY);
}

void MAP01_streamRelease(void)
{
    streamActive = FALSE;
    streamOriginX = -1;
    streamOriginY = -1;
    VDP_setHorizontalScroll(BG_B, 0);
    VDP_setVerticalScroll(BG_B, 0);
}
