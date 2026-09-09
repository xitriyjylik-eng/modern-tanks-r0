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
    /* Extend the bridge across the banks too, instead of stopping at water. */
    return isRoad(wx, wy) && (riverDistance(wx, wy) <= 9);
}

static bool forestField(s16 wx, s16 wy)
{
    u16 large, medium, score;
    if (!worldInBounds(wx, wy) || isWater(wx, wy) || isShore(wx, wy) || isRoad(wx, wy)) return FALSE;

    /* The heavy stress forest is deliberately away from the initial camera so
     * the first impression is representative, while long-run stress still exists. */
    if ((wx > 760) && (wx < 900) && (wy > 700) && (wy < 880)) return TRUE;

    /* Bilinearly interpolated low-frequency fields avoid square 128px forest cells. */
    large = valueNoise8(wx, wy, 6, 17, -29);
    medium = valueNoise8(wx, wy, 4, -53, 41);
    score = (u16)(((u32)large * 3 + medium) >> 2);
    return score < 92;
}

static bool hasTreeAnchor(s16 ax, s16 ay)
{
    if (!worldInBounds(ax, ay) || !worldInBounds(ax + WT_TREE_W - 1, ay + WT_TREE_H - 1)) return FALSE;
    if ((ax & (WT_TREE_W - 1)) != 0 || (ay % WT_TREE_H) != 0) return FALSE;
    if (!forestField(ax + 1, ay + 1) || !forestField(ax + 2, ay + 1)) return FALSE;
    return (hash16(ax >> 2, ay / WT_TREE_H) & 7) < 5;
}

static u16 metaTileId(u16 base, u16 variant, u16 metaW, u16 metaH, s16 wx, s16 wy)
{
    u16 lx = ((u16)wx) % metaW;
    u16 ly = ((u16)wy) % metaH;
    return base + variant * metaW * metaH + ly * metaW + lx;
}

static u16 baseTileAttr(s16 wx, s16 wy)
{
    u16 variant, id, pal;

    if (!worldInBounds(wx, wy))
        return TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, worldTileBase + WT_BLANK);

    if (isBridge(wx, wy))
    {
        variant = hash16(wx >> 2, wy >> 2) % WT_BRIDGE_META;
        id = metaTileId(WT_BRIDGE_BASE, variant, WT_BRIDGE_W, WT_BRIDGE_H, wx, wy);
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
        variant = (left ? 0 : WT_SHORE_VARIANTS_PER_SIDE) + (hash16(wy >> 2, left ? 7 : 19) % WT_SHORE_VARIANTS_PER_SIDE);
        id = WT_SHORE_BASE + variant * 16 + ly * 4 + lx;
        pal = PAL3;
    }
    else if (isRoad(wx, wy))
    {
        variant = hash16(wx >> 2, wy >> 2) % WT_ROAD_META;
        id = metaTileId(WT_ROAD_BASE, variant, WT_ROAD_W, WT_ROAD_H, wx, wy);
        pal = PAL3;
    }
    else
    {
        variant = hash16(wx >> 2, wy >> 2) % WT_GRASS_META;
        id = metaTileId(WT_GRASS_BASE, variant, WT_GRASS_W, WT_GRASS_H, wx, wy);
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

    /* 32x24 tree frames: preserve the full 4x3 tile footprint. */
    ax = wx - (wx & (WT_TREE_W - 1));
    ay = wy - (wy % WT_TREE_H);
    if (hasTreeAnchor(ax, ay))
    {
