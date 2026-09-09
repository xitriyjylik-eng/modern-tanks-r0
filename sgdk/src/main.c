#include <genesis.h>
#include "resources.h"
#include "r3_stream_world.h"

/*
 * Modern Tanks R2 — refined ambient pass.
 * R1 state/bank/input core remains accepted and preserved.
 *
 * This pass changes only the agreed ambient details:
 * - river flow follows the local river course instead of a screen-axis scroll
 * - right flag uses the original cloth/emblem, smoothly warped on the existing flagpole
 * - upper and lower static flame-looking pixels are removed from the background
 * - both fires are independent, irregular transparent multi-tongue animations
 * - a small lower-right foliage group moves subtly in the same wind as the flag
 * - accepted menu, typography, composition and landscape palette remain authoritative
 */

typedef enum
{
    STATE_BOOT = 0,
    STATE_TITLE,
    STATE_MAIN_MENU,
    STATE_TEST_BATTLE,
    STATE_GARAGE,
    STATE_COUNT
} GameState;

typedef enum
{
    BANK_NONE = 0,
    BANK_CORE,
    BANK_MENU,
    BANK_BATTLE_SHELL,
    BANK_GARAGE_SHELL
} ResourceBank;

typedef struct
{
    u16 held;
    u16 pressed;
    u16 released;
} InputState;

#define R2_LOGIC_HZ 60
#define R2_BOOT_TICKS 60
#define R2_MENU_COUNT 4

#define R2_RIVER_FRAMES 12
#define R2_FLAG_FRAMES 12
#define R2_FIRE_FRAMES 8
#define R2_TREE_FRAMES 12

#define R2_RIVER_HOLD_TICKS 6
#define R2_FLAG_HOLD_TICKS 6
#define R2_FIRE_TOP_HOLD_TICKS 4
#define R2_FIRE_BOTTOM_HOLD_TICKS 5
#define R2_TREE_HOLD_TICKS 10

#define R2_SELECTOR_X 11
#define R2_SELECTOR_W 18
#define R2_SELECTOR_H 2
#define R2_SELECTOR_CRAM_INDEX 15

/* Tile-aligned positions in the accepted 320x224 composition. */
#define R2_RIVER_X 0
#define R2_RIVER_Y 0
#define R2_FLAG_RIGHT_X 36
#define R2_FLAG_RIGHT_Y 13
#define R2_FIRE_TOP_X 30
#define R2_FIRE_TOP_Y 5
#define R2_FIRE_BOTTOM_X 29
#define R2_FIRE_BOTTOM_Y 17
#define R2_TREES_X 34
#define R2_TREES_Y 22

static GameState currentState = STATE_BOOT;
static ResourceBank activeBank = BANK_NONE;
static InputState input;

static u16 previousPad = 0;
static u16 menuIndex = 0;
static u16 videoHz = 60;
static u16 logicAccumulator = 0;
static u16 stateTicks = 0;
static u16 transitionCount = 0;
static u16 bankGeneration = 0;
static u16 errorCount = 0;
static const char *lastError = "NONE";

static u16 patchTileBase = 0;
static u16 selectorTileBase = 0;
static u16 riverTileBase = 0;
static u16 flagRightTileBase = 0;
static u16 fireTopTileBase = 0;
static u16 fireBottomTileBase = 0;
static u16 treesTileBase = 0;

static u16 selectorPulse = 0;
static u16 riverAnimTick = 0;
static u16 flagAnimTick = 0;
static u16 fireTopAnimTick = 0;
static u16 fireBottomAnimTick = 0;
static u16 treesAnimTick = 0;

static u16 riverAnimFrame = 0;
static u16 flagAnimFrame = 0;
static u16 fireTopAnimFrame = 0;
static u16 fireBottomAnimFrame = 3;
static u16 treesAnimFrame = 2;
static bool menuArtLoaded = FALSE;

/* Native pixel Y rows 88/104/120/136 -> tile rows 11/13/15/17. */
static const u16 selectorY[R2_MENU_COUNT] = {11, 13, 15, 17};

static const Image * const riverFrames[R2_RIVER_FRAMES] =
{
    &r2_river_0, &r2_river_1, &r2_river_2, &r2_river_3,
    &r2_river_4, &r2_river_5, &r2_river_6, &r2_river_7,
    &r2_river_8, &r2_river_9, &r2_river_10, &r2_river_11
};

static const Image * const flagRightFrames[R2_FLAG_FRAMES] =
{
    &r2_flag_right_0, &r2_flag_right_1, &r2_flag_right_2, &r2_flag_right_3,
    &r2_flag_right_4, &r2_flag_right_5, &r2_flag_right_6, &r2_flag_right_7,
    &r2_flag_right_8, &r2_flag_right_9, &r2_flag_right_10, &r2_flag_right_11
};

static const Image * const fireTopFrames[R2_FIRE_FRAMES] =
{
    &r2_fire_top_0, &r2_fire_top_1, &r2_fire_top_2, &r2_fire_top_3,
    &r2_fire_top_4, &r2_fire_top_5, &r2_fire_top_6, &r2_fire_top_7
};

static const Image * const fireBottomFrames[R2_FIRE_FRAMES] =
{
    &r2_fire_bottom_0, &r2_fire_bottom_1, &r2_fire_bottom_2, &r2_fire_bottom_3,
    &r2_fire_bottom_4, &r2_fire_bottom_5, &r2_fire_bottom_6, &r2_fire_bottom_7
};

static const Image * const treesFrames[R2_TREE_FRAMES] =
{
    &r2_trees_0, &r2_trees_1, &r2_trees_2, &r2_trees_3,
    &r2_trees_4, &r2_trees_5, &r2_trees_6, &r2_trees_7,
    &r2_trees_8, &r2_trees_9, &r2_trees_10, &r2_trees_11
};

static ResourceBank state_bank(GameState state)
{
    switch (state)
    {
        case STATE_BOOT:
        case STATE_TITLE: return BANK_CORE;
        case STATE_MAIN_MENU: return BANK_MENU;
        case STATE_TEST_BATTLE: return BANK_BATTLE_SHELL;
        case STATE_GARAGE: return BANK_GARAGE_SHELL;
        default: return BANK_NONE;
    }
}

static void set_error(const char *code)
{
    errorCount++;
    lastError = code;
}

static void clear_all_palettes(void)
{
    PAL_setColors(0, palette_black, 64, CPU);
    VDP_waitFIFOEmpty();
}

static bool palettes_are_black(void)
{
    u16 colors[64];
    u16 i;

    VDP_waitFIFOEmpty();
    SYS_disableInts();
    PAL_getColors(0, colors, 64);
    SYS_enableInts();

    for (i = 0; i < 64; i++)
        if (colors[i] != 0) return FALSE;

    return TRUE;
}

static u16 max8(u16 a, u16 b, u16 c, u16 d, u16 e, u16 f, u16 g, u16 h)
{
    u16 m = a;
    if (b > m) m = b; if (c > m) m = c; if (d > m) m = d;
    if (e > m) m = e; if (f > m) m = f; if (g > m) m = g; if (h > m) m = h;
    return m;
}

static u16 max12(u16 a, u16 b, u16 c, u16 d, u16 e, u16 f,
                 u16 g, u16 h, u16 i, u16 j, u16 k, u16 l)
{
    u16 m = a;
    if (b > m) m = b; if (c > m) m = c; if (d > m) m = d;
    if (e > m) m = e; if (f > m) m = f; if (g > m) m = g;
    if (h > m) m = h; if (i > m) m = i; if (j > m) m = j;
    if (k > m) m = k; if (l > m) m = l;
    return m;
}

static void resource_bank_unload(void)
{
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
    VDP_clearPlane(WINDOW, TRUE);
    VDP_setHorizontalScroll(BG_A, 0);
    VDP_setHorizontalScroll(BG_B, 0);
    VDP_setVerticalScroll(BG_A, 0);
    VDP_setVerticalScroll(BG_B, 0);

    VDP_resetSprites();
    VDP_updateSprites(0, CPU);
    clear_all_palettes();

    if (!palettes_are_black()) set_error("PALETTE_RESIDUE");
    if (VDP_refreshHighestAllocatedSpriteIndex() != -1) set_error("SPRITE_LEAK");

    menuArtLoaded = FALSE;
    activeBank = BANK_NONE;
    bankGeneration++;
}

static void resource_bank_load(ResourceBank bank)
{
    if (activeBank != BANK_NONE)
    {
        set_error("BANK_LOAD_OVERLAP");
        resource_bank_unload();
    }

    activeBank = bank;
    bankGeneration++;

    if (bank != BANK_MENU)
    {
        PAL_setPalette(PAL0, palette_grey, CPU);
        if (bank == BANK_CORE) PAL_setColor(0, RGB24_TO_VDPCOLOR(0x081018));
        else if (bank == BANK_BATTLE_SHELL) PAL_setColor(0, RGB24_TO_VDPCOLOR(0x241008));
        else if (bank == BANK_GARAGE_SHELL) PAL_setColor(0, RGB24_TO_VDPCOLOR(0x180C24));
        else PAL_setColor(0, RGB24_TO_VDPCOLOR(0x100808));
        VDP_waitFIFOEmpty();
    }
}

static void draw_selector(u16 newIndex, u16 oldIndex, bool firstDraw)
{
    if (!firstDraw)
        VDP_clearTileMapRect(BG_A, R2_SELECTOR_X, selectorY[oldIndex], R2_SELECTOR_W, R2_SELECTOR_H);

    VDP_drawImageEx(BG_A, &r2_selector,
                    TILE_ATTR_FULL(PAL0, TRUE, FALSE, FALSE, selectorTileBase),
                    R2_SELECTOR_X, selectorY[newIndex], FALSE, TRUE);
}

static void draw_river_frame(u16 frame)
{
    VDP_drawImageEx(BG_A, riverFrames[frame],
                    TILE_ATTR_FULL(PAL1, TRUE, FALSE, FALSE, riverTileBase),
                    R2_RIVER_X, R2_RIVER_Y, FALSE, TRUE);
}

static void draw_flag_right_frame(u16 frame)
{
    VDP_drawImageEx(BG_A, flagRightFrames[frame],
                    TILE_ATTR_FULL(PAL3, TRUE, FALSE, FALSE, flagRightTileBase),
                    R2_FLAG_RIGHT_X, R2_FLAG_RIGHT_Y, FALSE, TRUE);
}

static void draw_fire_top_frame(u16 frame)
{
    VDP_drawImageEx(BG_A, fireTopFrames[frame],
                    TILE_ATTR_FULL(PAL0, TRUE, FALSE, FALSE, fireTopTileBase),
                    R2_FIRE_TOP_X, R2_FIRE_TOP_Y, FALSE, TRUE);
}

static void draw_fire_bottom_frame(u16 frame)
{
    VDP_drawImageEx(BG_A, fireBottomFrames[frame],
                    TILE_ATTR_FULL(PAL0, TRUE, FALSE, FALSE, fireBottomTileBase),
                    R2_FIRE_BOTTOM_X, R2_FIRE_BOTTOM_Y, FALSE, TRUE);
}

static void draw_trees_frame(u16 frame)
{
    VDP_drawImageEx(BG_A, treesFrames[frame],
                    TILE_ATTR_FULL(PAL2, TRUE, FALSE, FALSE, treesTileBase),
                    R2_TREES_X, R2_TREES_Y, FALSE, TRUE);
}

static void draw_menu_art(void)
{
    u16 bgTiles;
    u16 patchTiles;
    u16 selectorTiles;
    u16 riverTiles;
    u16 flagRightTiles;
    u16 fireTopTiles;
    u16 fireBottomTiles;
    u16 treesTiles;
    u16 nextTile;

    VDP_setTextPlane(BG_A);
    VDP_setTextPriority(TRUE);

    VDP_drawImageEx(BG_B, &r2_menu_bg,
                    TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, TILE_USER_INDEX),
                    0, 0, TRUE, TRUE);

    bgTiles = r2_menu_bg.tileset->numTile;
    patchTiles = r2_top_right_patch.tileset->numTile;
    patchTileBase = TILE_USER_INDEX + bgTiles;

    VDP_drawImageEx(BG_B, &r2_top_right_patch,
                    TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, patchTileBase),
                    29, 0, FALSE, TRUE);

    selectorTiles = r2_selector.tileset->numTile;
    riverTiles = max12(r2_river_0.tileset->numTile, r2_river_1.tileset->numTile,
                       r2_river_2.tileset->numTile, r2_river_3.tileset->numTile,
                       r2_river_4.tileset->numTile, r2_river_5.tileset->numTile,
                       r2_river_6.tileset->numTile, r2_river_7.tileset->numTile,
                       r2_river_8.tileset->numTile, r2_river_9.tileset->numTile,
                       r2_river_10.tileset->numTile, r2_river_11.tileset->numTile);
    flagRightTiles = max12(r2_flag_right_0.tileset->numTile, r2_flag_right_1.tileset->numTile,
                           r2_flag_right_2.tileset->numTile, r2_flag_right_3.tileset->numTile,
                           r2_flag_right_4.tileset->numTile, r2_flag_right_5.tileset->numTile,
                           r2_flag_right_6.tileset->numTile, r2_flag_right_7.tileset->numTile,
                           r2_flag_right_8.tileset->numTile, r2_flag_right_9.tileset->numTile,
                           r2_flag_right_10.tileset->numTile, r2_flag_right_11.tileset->numTile);
    fireTopTiles = max8(r2_fire_top_0.tileset->numTile, r2_fire_top_1.tileset->numTile,
                        r2_fire_top_2.tileset->numTile, r2_fire_top_3.tileset->numTile,
                        r2_fire_top_4.tileset->numTile, r2_fire_top_5.tileset->numTile,
                        r2_fire_top_6.tileset->numTile, r2_fire_top_7.tileset->numTile);
    fireBottomTiles = max8(r2_fire_bottom_0.tileset->numTile, r2_fire_bottom_1.tileset->numTile,
                           r2_fire_bottom_2.tileset->numTile, r2_fire_bottom_3.tileset->numTile,
                           r2_fire_bottom_4.tileset->numTile, r2_fire_bottom_5.tileset->numTile,
                           r2_fire_bottom_6.tileset->numTile, r2_fire_bottom_7.tileset->numTile);
    treesTiles = max12(r2_trees_0.tileset->numTile, r2_trees_1.tileset->numTile,
                       r2_trees_2.tileset->numTile, r2_trees_3.tileset->numTile,
                       r2_trees_4.tileset->numTile, r2_trees_5.tileset->numTile,
                       r2_trees_6.tileset->numTile, r2_trees_7.tileset->numTile,
                       r2_trees_8.tileset->numTile, r2_trees_9.tileset->numTile,
                       r2_trees_10.tileset->numTile, r2_trees_11.tileset->numTile);

    selectorTileBase = patchTileBase + patchTiles;
    nextTile = selectorTileBase + selectorTiles;
    riverTileBase = nextTile; nextTile += riverTiles;
    flagRightTileBase = nextTile; nextTile += flagRightTiles;
    fireTopTileBase = nextTile; nextTile += fireTopTiles;
    fireBottomTileBase = nextTile; nextTile += fireBottomTiles;
    treesTileBase = nextTile; nextTile += treesTiles;

    if ((nextTile - 1) > TILE_USER_MAX_INDEX)
    {
        set_error("R2_VRAM_TILES");
        menuArtLoaded = FALSE;
        return;
    }

    riverAnimTick = flagAnimTick = fireTopAnimTick = fireBottomAnimTick = treesAnimTick = 0;
    riverAnimFrame = 0;
    flagAnimFrame = 0;
    fireTopAnimFrame = 0;
    fireBottomAnimFrame = 3;
    treesAnimFrame = 2;

    draw_river_frame(riverAnimFrame);
    draw_flag_right_frame(flagAnimFrame);
    draw_fire_top_frame(fireTopAnimFrame);
    draw_fire_bottom_frame(fireBottomAnimFrame);
    draw_trees_frame(treesAnimFrame);

    draw_selector(menuIndex, menuIndex, TRUE);

    selectorPulse = 0;
    menuArtLoaded = TRUE;
}

static void update_menu_visuals(void)
{
    if (!menuArtLoaded) return;

    selectorPulse++;
    if ((selectorPulse & 15) == 0)
    {
        if (selectorPulse & 16)
            PAL_setColor(R2_SELECTOR_CRAM_INDEX, RGB24_TO_VDPCOLOR(0xFBE049));
        else
            PAL_setColor(R2_SELECTOR_CRAM_INDEX, RGB24_TO_VDPCOLOR(0xC9A72F));
    }

    riverAnimTick++;
    if (riverAnimTick >= R2_RIVER_HOLD_TICKS)
    {
        riverAnimTick = 0;
        riverAnimFrame = (riverAnimFrame + 1) % R2_RIVER_FRAMES;
        draw_river_frame(riverAnimFrame);
        draw_selector(menuIndex, menuIndex, TRUE);
    }

    flagAnimTick++;
    if (flagAnimTick >= R2_FLAG_HOLD_TICKS)
    {
        flagAnimTick = 0;
        flagAnimFrame = (flagAnimFrame + 1) % R2_FLAG_FRAMES;
        draw_flag_right_frame(flagAnimFrame);
    }

    fireTopAnimTick++;
    if (fireTopAnimTick >= R2_FIRE_TOP_HOLD_TICKS)
    {
        fireTopAnimTick = 0;
        fireTopAnimFrame = (fireTopAnimFrame + 1) % R2_FIRE_FRAMES;
        draw_fire_top_frame(fireTopAnimFrame);
    }

    fireBottomAnimTick++;
    if (fireBottomAnimTick >= R2_FIRE_BOTTOM_HOLD_TICKS)
    {
        fireBottomAnimTick = 0;
        fireBottomAnimFrame = (fireBottomAnimFrame + 1) % R2_FIRE_FRAMES;
        draw_fire_bottom_frame(fireBottomAnimFrame);
    }

    treesAnimTick++;
    if (treesAnimTick >= R2_TREE_HOLD_TICKS)
    {
        treesAnimTick = 0;
        treesAnimFrame = (treesAnimFrame + 1) % R2_TREE_FRAMES;
        draw_trees_frame(treesAnimFrame);
    }
}

static void draw_boot(void)
{
    VDP_setTextPalette(PAL0);
    VDP_drawText("MODERN TANKS", 14, 5);
    VDP_drawText("R2 ANIMATED MENU", 11, 9);
    VDP_drawText("R1 CORE ACCEPTED", 11, 13);
    VDP_drawText("LOADING MENU BANK...", 10, 17);
}

static void draw_title(void)
{
    VDP_setTextPalette(PAL0);
    VDP_drawText("MODERN TANKS", 14, 6);
    VDP_drawText("R2 ANIMATED MENU", 11, 10);
    VDP_drawText("PRESS START OR A", 11, 15);
}

static void draw_shell(const char *title, const char *bank)
{
    char buffer[8];

    VDP_setTextPalette(PAL0);
    VDP_drawText("MODERN TANKS / R2", 11, 2);
    VDP_drawText(title, 10, 8);
    VDP_drawText("NO GAMEPLAY IN R2", 11, 12);
    VDP_drawText("B: RETURN TO MENU", 11, 16);
    VDP_drawText("MENU BANK UNLOADED", 10, 19);
    VDP_drawText("BANK:", 4, 23);
    VDP_drawText(bank, 10, 23);
    VDP_drawText("ERR:", 22, 23);
    uintToStr(errorCount, buffer, 2);
    VDP_drawText(buffer, 27, 23);
}

static void draw_state(GameState state)
{
    if (state == STATE_BOOT) draw_boot();
    else if (state == STATE_TITLE) draw_title();
    else if (state == STATE_MAIN_MENU) draw_menu_art();
    else if (state == STATE_TEST_BATTLE) R3_worldEnter();
    else if (state == STATE_GARAGE) draw_shell("GARAGE SHELL", "GARAGE");
    else set_error("DRAW_INVALID_STATE");
}

static void state_enter(GameState state)
{
    ResourceBank expected = state_bank(state);
    stateTicks = 0;
    resource_bank_load(expected);
    if (activeBank != expected) set_error("BANK_STATE_MISMATCH");
    draw_state(state);
}

static void state_leave(GameState state)
{
    if (state == STATE_TEST_BATTLE) R3_worldLeave();
    resource_bank_unload();
}

static bool transition_is_valid(GameState from, GameState to)
{
    if ((from == STATE_BOOT) && (to == STATE_TITLE)) return TRUE;
    if ((from == STATE_TITLE) && (to == STATE_MAIN_MENU)) return TRUE;
    if ((from == STATE_MAIN_MENU) && ((to == STATE_TEST_BATTLE) || (to == STATE_GARAGE))) return TRUE;
    if ((from == STATE_TEST_BATTLE) && (to == STATE_MAIN_MENU)) return TRUE;
    if ((from == STATE_GARAGE) && (to == STATE_MAIN_MENU)) return TRUE;
    return FALSE;
}

static void change_state(GameState next)
{
    if (!transition_is_valid(currentState, next))
    {
        set_error("INVALID_TRANSITION");
        return;
    }

    VDP_setEnable(FALSE);
    VDP_waitFIFOEmpty();
    state_leave(currentState);
    currentState = next;
    transitionCount++;
    state_enter(currentState);
    VDP_waitFIFOEmpty();
    VDP_setEnable(TRUE);
}

static void input_poll(void)
{
    u16 current = JOY_readJoypad(JOY_1);
    input.held = current;
    input.pressed = current & (u16) ~previousPad;
    input.released = previousPad & (u16) ~current;
    previousPad = current;
}

static void handle_input_frame(void)
{
    switch (currentState)
    {
        case STATE_TITLE:
            if (input.pressed & (BUTTON_START | BUTTON_A)) change_state(STATE_MAIN_MENU);
            break;

        case STATE_MAIN_MENU:
            if (input.pressed & BUTTON_UP)
            {
                u16 old = menuIndex;
                menuIndex = (menuIndex == 0) ? (R2_MENU_COUNT - 1) : (menuIndex - 1);
                draw_selector(menuIndex, old, FALSE);
            }
            if (input.pressed & BUTTON_DOWN)
            {
                u16 old = menuIndex;
                menuIndex = (menuIndex + 1) % R2_MENU_COUNT;
                draw_selector(menuIndex, old, FALSE);
            }
            if (input.pressed & (BUTTON_A | BUTTON_START))
            {
                if (menuIndex == 0) change_state(STATE_TEST_BATTLE);
                else if (menuIndex == 1) change_state(STATE_GARAGE);
            }
            break;

        case STATE_TEST_BATTLE:
        case STATE_GARAGE:
            if (input.pressed & BUTTON_B) change_state(STATE_MAIN_MENU);
            break;

        default:
            break;
    }
}

static void update_logic_tick(void)
{
    stateTicks++;
    if (currentState == STATE_BOOT)
    {
        if (stateTicks >= R2_BOOT_TICKS) change_state(STATE_TITLE);
        return;
    }
    if (currentState == STATE_MAIN_MENU) update_menu_visuals();
    else if (currentState == STATE_TEST_BATTLE) R3_worldUpdate(input.held);
}

int main(bool hardReset)
{
    (void) hardReset;

    VDP_setScreenWidth320();
    VDP_setScreenHeight224();
    VDP_setPlaneSize(64, 32, TRUE);
    VDP_setTextPlane(BG_A);
    VDP_setTextPalette(PAL0);
    VDP_setTextPriority(TRUE);

    JOY_setSupport(PORT_1, JOY_SUPPORT_3BTN);

    videoHz = SYS_isPAL() ? 50 : 60;
    clear_all_palettes();
    VDP_resetSprites();
    VDP_updateSprites(0, CPU);

    previousPad = JOY_readJoypad(JOY_1);
    state_enter(STATE_BOOT);

    while (TRUE)
    {
        SYS_doVBlankProcess();
        input_poll();
        handle_input_frame();

        logicAccumulator += R2_LOGIC_HZ;
        while (logicAccumulator >= videoHz)
        {
            logicAccumulator -= videoHz;
            update_logic_tick();
        }
    }

    return 0;
}
