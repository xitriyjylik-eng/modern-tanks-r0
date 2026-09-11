#ifndef MAP01_STREAM_H
#define MAP01_STREAM_H

#include <genesis.h>

#define MAP01_WORLD_WIDTH_PX      1536u
#define MAP01_WORLD_HEIGHT_PX     1152u
#define MAP01_WORLD_TILES_X       192u
#define MAP01_WORLD_TILES_Y       144u

#define MAP01_STREAM_CACHE_W      32u
#define MAP01_STREAM_CACHE_H      32u
#define MAP01_STREAM_CACHE_TILES  (MAP01_STREAM_CACHE_W * MAP01_STREAM_CACHE_H)

/*
 * Streams the approved 1536x1152 Map 01 artwork into a 32x32 tile-pattern
 * ring cache. The visual source is converted offline only; runtime does not
 * generate or reinterpret the world.
 */
bool MAP01_streamInit(u16 tileBase, u16 scrollX, u16 scrollY);
void MAP01_streamScrollTo(u16 scrollX, u16 scrollY);
void MAP01_streamRelease(void);

#endif
