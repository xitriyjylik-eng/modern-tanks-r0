#include <genesis.h>
#include "resources.h"
#include "r2_anim_assets.h"

/*
 * Modern Tanks R2 — Final Main Menu Visual Target, animated pass.
 * Clean SGDK rebuild. R1 core remains accepted and preserved.
 *
 * Direct R2 requirements implemented here:
 * - native 320x224 presentation
 * - accepted Russian menu typography retained
 * - top-right minimap removed from the menu background
 * - detailed battlefield background with original accepted color balance
 * - left decorative flag removed; right flag is a dedicated wind animation
 * - river ambience updates only true-water tiles and is slowed for smoother flow
 * - two independent fire animations; only flame pixels animate
 * - no detached decorative tank and no lower stat/minimap strip
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
#define R2_ANIM_FRAMES 4
#define R2_RIVER_HOLD_TICKS 10
#define R2_FLAG_HOLD_TICKS 9
#define R2_FIRE_HOLD_TICKS 7
#define R2_FIRE_LOWER_HOLD_TICKS 9

#define R2_SELECTOR_X 11
#define R2_SELECTOR_W 18
#define R2_SELECTOR_H 2
#define R2_SELECTOR_CRAM_INDEX 15

/* Overlay positions are tile aligned to the native 320x224 composition. */
#define R2_RIVER_X 0
#define R2_RIVER_Y 0
#define R2_FLAG_RIGHT_X 36
#define R2_FLAG_RIGHT_Y 14
#define R2_FIRE_X 31
#define R2_FIRE_Y 6
#define R2_FIRE_LOWER_X 29
#define R2_FIRE_LOWER_Y 16

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
static u16 flagPatchTileBase = 0;
static u16 selectorTileBase = 0;
static u16 riverTileBase = 0;
static u16 flagRightTileBase = 0;
static u16 fireTileBase = 0;
static u16 fireLowerTileBase = 0;
static u16 selectorPulse = 0;
static u16 riverAnimTick = 0;
static u16 flagAnimTick = 0;
static u16 fireAnimTick = 0;
static u16 fireLowerAnimTick = 0;
static u16 riverAnimFrame = 0;
static u16 flagAnimFrame = 0;
static u16 fireAnimFrame = 0;
static u16 fireLowerAnimFrame = 0;
static bool menuArtLoaded = FALSE;

/* Native pixel Y rows 88/104/120/136 -> tile rows 11/13/15/17. */
static const u16 selectorY[R2_MENU_COUNT] = {11, 13, 15, 17};

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
        VDP_clearTileMapRect(BG_A,
                             R2_SELECTOR_X,
                             selectorY[oldIndex],
                             R2_SELECTOR_W,
                             R2_SELECTOR_H);

    VDP_drawImageEx(BG_A,
                    &r2_selector,
                    TILE_ATTR_FULL(PAL0, TRUE, FALSE, FALSE, selectorTileBase),
                    R2_SELECTOR_X,
                    selectorY[newIndex],
                    FALSE,
                    TRUE);
}

static void map_flag_patch(void)
{
    u16 i;

    VDP_loadTileData((const u32 *) r2_flag_patch_tiles,
                     flagPatchTileBase,
                     R2_FLAG_PATCH_TILE_COUNT,
                     DMA);

    for (i = 0; i < R2_FLAG_PATCH_TILE_COUNT; i++)
    {
        VDP_setTileMapXY(BG_B,
                         TILE_ATTR_FULL(r2_flag_patch_pal[i],
                                        FALSE,
                                        FALSE,
                                        FALSE,
                                        flagPatchTileBase + i),
                         R2_FLAG_RIGHT_X + (i & 3),
                         R2_FLAG_RIGHT_Y + (i >> 2));
    }
}

static void map_ambient_tiles(void)
{
    u16 i;

    for (i = 0; i < R2_RIVER_TILE_COUNT; i++)
        VDP_setTileMapXY(BG_A,
                         TILE_ATTR_FULL(PAL1, TRUE, FALSE, FALSE, riverTileBase + i),
                         R2_RIVER_X + r2_river_tile_x[i],
                         R2_RIVER_Y + r2_river_tile_y[i]);

    for (i = 0; i < R2_FLAG_TILE_COUNT; i++)
        VDP_setTileMapXY(BG_A,
                         TILE_ATTR_FULL(PAL3, TRUE, FALSE, FALSE, flagRightTileBase + i),
                         R2_FLAG_RIGHT_X + r2_flag_tile_x[i],
                         R2_FLAG_RIGHT_Y + r2_flag_tile_y[i]);

    for (i = 0; i < R2_FIRE_UPPER_TILE_COUNT; i++)
        VDP_setTileMapXY(BG_A,
                         TILE_ATTR_FULL(PAL0, TRUE, FALSE, FALSE, fireTileBase + i),
                         R2_FIRE_X + r2_fire_upper_tile_x[i],
                         R2_FIRE_Y + r2_fire_upper_tile_y[i]);

    for (i = 0; i < R2_FIRE_LOWER_TILE_COUNT; i++)
        VDP_setTileMapXY(BG_A,
                         TILE_ATTR_FULL(PAL0, TRUE, FALSE, FALSE, fireLowerTileBase + i),
                         R2_FIRE_LOWER_X + r2_fire_lower_tile_x[i],
                         R2_FIRE_LOWER_Y + r2_fire_lower_tile_y[i]);
}

static void draw_river_frame(u16 frame)
{
    VDP_loadTileData((const u32 *) r2_river_frames[frame],
                     riverTileBase,
                     R2_RIVER_TILE_COUNT,
                     DMA);
}

static void draw_flag_frame(u16 frame)
{
    VDP_loadTileData((const u32 *) r2_flag_frames[frame],
                     flagRightTileBase,
                     R2_FLAG_TILE_COUNT,
                     DMA);
}

static void draw_fire_frame(u16 frame)
{
    VDP_loadTileData((const u32 *) r2_fire_upper_frames[frame],
                     fireTileBase,
                     R2_FIRE_UPPER_TILE_COUNT,
                     DMA);
}

static void draw_fire_lower_frame(u16 frame)
{
    VDP_loadTileData((const u32 *) r2_fire_lower_frames[frame],
                     fireLowerTileBase,
                     R2_FIRE_LOWER_TILE_COUNT,
                     DMA);
}

static void draw_menu_art(void)
{
    u16 bgTiles;
    u16 patchTiles;
    u16 selectorTiles;
    u16 nextTile;

    VDP_setTextPlane(BG_A);
    VDP_setTextPriority(TRUE);

    VDP_drawImageEx(BG_B,
                    &r2_menu_bg,
                    TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, TILE_USER_INDEX),
                    0,
                    0,
                    TRUE,
                    TRUE);

    bgTiles = r2_menu_bg.tileset->numTile;
    patchTiles = r2_top_right_patch.tileset->numTile;
    patchTileBase = TILE_USER_INDEX + bgTiles;

    VDP_drawImageEx(BG_B,
                    &r2_top_right_patch,
                    TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, patchTileBase),
                    29,
                    0,
                    FALSE,
                    TRUE);

    flagPatchTileBase = patchTileBase + patchTiles;
    map_flag_patch();

    selectorTiles = r2_selector.tileset->numTile;
    selectorTileBase = flagPatchTileBase + R2_FLAG_PATCH_TILE_COUNT;
    nextTile = selectorTileBase + selectorTiles;

    riverTileBase = nextTile;
    nextTile += R2_RIVER_TILE_COUNT;
    flagRightTileBase = nextTile;
    nextTile += R2_FLAG_TILE_COUNT;
    fireTileBase = nextTile;
    nextTile += R2_FIRE_UPPER_TILE_COUNT;
    fireLowerTileBase = nextTile;
    nextTile += R2_FIRE_LOWER_TILE_COUNT;

    if ((nextTile - 1) > TILE_USER_MAX_INDEX)
    {
        set_error("R2_VRAM_TILES");
        menuArtLoaded = FALSE;
        return;
    }

    riverAnimTick = 0;
    flagAnimTick = 0;
    fireAnimTick = 0;
    fireLowerAnimTick = 0;
    riverAnimFrame = 0;
    flagAnimFrame = 0;
    fireAnimFrame = 0;
    fireLowerAnimFrame = 0;

    map_ambient_tiles();
    draw_river_frame(riverAnimFrame);
    draw_flag_frame(flagAnimFrame);
    draw_fire_frame(fireAnimFrame);
    draw_fire_lower_frame(fireLowerAnimFrame);
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
        riverAnimFrame = (riverAnimFrame + 1) % R2_ANIM_FRAMES;
        draw_river_frame(riverAnimFrame);
    }

    flagAnimTick++;
    if (flagAnimTick >= R2_FLAG_HOLD_TICKS)
    {
        flagAnimTick = 0;
        flagAnimFrame = (flagAnimFrame + 1) % R2_ANIM_FRAMES;
        draw_flag_frame(flagAnimFrame);
    }

    fireAnimTick++;
    if (fireAnimTick >= R2_FIRE_HOLD_TICKS)
    {
        fireAnimTick = 0;
        fireAnimFrame = (fireAnimFrame + 1) % R2_ANIM_FRAMES;
        draw_fire_frame(fireAnimFrame);
    }

    fireLowerAnimTick++;
    if (fireLowerAnimTick >= R2_FIRE_LOWER_HOLD_TICKS)
    {
        fireLowerAnimTick = 0;
        fireLowerAnimFrame = (fireLowerAnimFrame + 1) % R2_ANIM_FRAMES;
        draw_fire_lower_frame(fireLowerAnimFrame);
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
    else if (state == STATE_TEST_BATTLE) draw_shell("TEST BATTLE SHELL", "BATTLE");
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
    (void) state;
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
            if (input.pressed & (BUTTON_START | BUTTON_A))
                change_state(STATE_MAIN_MENU);
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
            if (input.pressed & BUTTON_B)
                change_state(STATE_MAIN_MENU);
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
        if (stateTicks >= R2_BOOT_TICKS)
            change_state(STATE_TITLE);
        return;
    }

    if (currentState == STATE_MAIN_MENU)
        update_menu_visuals();
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
