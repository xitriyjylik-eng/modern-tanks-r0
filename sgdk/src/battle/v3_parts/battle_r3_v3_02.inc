        u16 phase = (hash16(ax, ay) >> 4) % WT_TREE_FRAMES;
        u16 frame = (treeFrame + phase) % WT_TREE_FRAMES;
        u16 q = (u16)((wy - ay) * WT_TREE_W + (wx - ax));
        return TILE_ATTR_FULL(PAL2, TRUE, FALSE, FALSE,
                              worldTileBase + WT_TREE_BASE + frame * WT_TREE_FRAME_TILES + q);
    }

    /* Rare 32x24 structures are also emitted as coherent metatiles. */
    ax = wx - (wx & (WT_STRUCT_W - 1));
    ay = wy - (wy % WT_STRUCT_H);
    if (worldInBounds(ax + WT_STRUCT_W - 1, ay + WT_STRUCT_H - 1) &&
        !forestField(ax + 1, ay + 1) && !isRoad(ax + 1, ay + 1) &&
        !isWater(ax + 1, ay + 1) && !isShore(ax + 1, ay + 1))
    {
        h = hash16(ax >> 2, ay / WT_STRUCT_H);
        if ((h & 1023) < 10)
        {
            u16 variant = (h >> 10) % WT_STRUCT_META;
            u16 q = (u16)((wy - ay) * WT_STRUCT_W + (wx - ax));
            return TILE_ATTR_FULL(PAL3, TRUE, FALSE, FALSE,
                                  worldTileBase + WT_STRUCT_BASE + variant * 12 + q);
        }
    }

    /* Small rocks/bushes are 16x16 and stay internally coherent. */
    ax = wx - (wx & 1);
    ay = wy - (wy & 1);
    if (!isWater(wx, wy) && !isShore(wx, wy) && !isRoad(wx, wy))
    {
        h = hash16(ax >> 1, ay >> 1);
        if ((h & 255) < 13)
        {
            u16 variant = (h >> 8) % WT_DECOR_META;
            u16 q = (u16)((wy - ay) * WT_DECOR_W + (wx - ax));
            return TILE_ATTR_FULL((variant < 12) ? PAL0 : PAL2, TRUE, FALSE, FALSE,
                                  worldTileBase + WT_DECOR_BASE + variant * 4 + q);
        }
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

enum R3MiniClass
{
    R3_MINI_GRASS = 0,
    R3_MINI_FOREST,
    R3_MINI_ROAD,
    R3_MINI_WATER,
    R3_MINI_BRIDGE
};

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
    static const s16 sample[3] = {-8, 0, 8};
    u16 counts[5] = {0,0,0,0,0};
