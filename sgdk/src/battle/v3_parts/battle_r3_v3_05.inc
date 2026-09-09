    }
    waterTick++;
    if (waterTick >= R3_WATER_HOLD_TICKS)
    {
        waterTick = 0;
        waterFrame = (waterFrame + 1) % WT_WATER_FRAMES;
        waterChanged = TRUE;
    }

    if (cameraMoved)
    {
        s16 tx = (s16)(cameraLeft() >> 3);
        s16 ty = (s16)(cameraTop() >> 3);
        if ((tx != lastCameraTileX) || (ty != lastCameraTileY)) updateStreaming();
        applyScroll();
        updateHudNumbers();
    }

    if (waterChanged || treesChanged) refreshVisibleAnimatedCells(waterChanged, treesChanged);

    minimapTick++;
    if ((targetMoved || cameraMoved) && minimapTick >= R3_MINIMAP_HOLD_TICKS)
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
