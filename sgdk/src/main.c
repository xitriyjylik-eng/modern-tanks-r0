#include <genesis.h>
#include "resources.h"
#include "map01_stream.h"

/*
 * Modern Tanks R3 / Map 01 runtime.
 *
 * The battle view now streams the approved 1536x1152 hand-authored Map 01
 * artwork. No procedural world generation is performed at runtime.
 */

typedef enum
{
    STATE_TITLE = 0,
    STATE_MAIN_MENU,
    STATE_MAP01,
    STATE_GARAGE
} GameState;

typedef struct
{
    u16 held;
    u16 pressed;
    u16 released;
} InputState;

#define MENU_COUNT 4u
#define SELECTOR_X 11u
#define SELECTOR_W 18u
#define SELECTOR_H 2u

#define MAP_VIEW_WIDTH_PX 224u
#define MAP_VIEW_HEIGHT_PX 192u
#define CAMERA_CENTER_X 112u
#define CAMERA_CENTER_Y 96u
#define CAMERA_FP_SHIFT 8
#define CAMERA_ACCEL_FP 24
#define CAMERA_FRICTION_FP 28
#define CAMERA_MAX_SPEED_FP 384

#define MAP_START_X 900u
#define MAP_START_Y 564u

static GameState currentState = STATE_TITLE;
static InputState input;
static u16 previousPad = 0;
static u16 menuIndex = 0;
static u16 videoHz = 60;

static u16 selectorTileBase = 0;
static u16 mapTileBase = 0;
static u16 hudFillTile = 0;
static bool mapStreamActive = FALSE;

static s32 cameraFocusXFP = 0;
static s32 cameraFocusYFP = 0;
static s32 cameraVelocityXFP = 0;
static s32 cameraVelocityYFP = 0;
static u16 mapScrollX = 0;
static u16 mapScrollY = 0;
static u16 hudLastX = 0xFFFFu;
static u16 hudLastY = 0xFFFFu;

static const u16 selectorY[MENU_COUNT] = {11, 13, 15, 17};
static const u32 hudFillPattern[8] =
{
    0x11111111, 0x11111111, 0x11111111, 0x11111111,
    0x11111111, 0x11111111, 0x11111111, 0x11111111
};

static void clear_palettes(void)
{
    PAL_setColors(0, palette_black, 64, CPU);
}

static void reset_planes(void)
{
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
    VDP_clearPlane(WINDOW, TRUE);
    VDP_setHorizontalScroll(BG_A, 0);
    VDP_setHorizontalScroll(BG_B, 0);
    VDP_setVerticalScroll(BG_A, 0);
    VDP_setVerticalScroll(BG_B, 0);
}

static void leave_state(void)
{
    if (mapStreamActive)
    {
        MAP01_streamRelease();
        mapStreamActive = FALSE;
    }

    reset_planes();
    VDP_resetSprites();
    VDP_updateSprites(0, CPU);
    clear_palettes();
}

static void draw_title(void)
{
    PAL_setPalette(PAL0, palette_grey, CPU);
    PAL_setColor(0, RGB24_TO_VDPCOLOR(0x081018));
    VDP_setTextPlane(BG_A);
    VDP_setTextPalette(PAL0);
    VDP_setTextPriority(TRUE);
    VDP_drawText("MODERN TANKS", 14, 7);
    VDP_drawText("R3 / MAP 01", 14, 11);
    VDP_drawText("PRESS START OR A", 11, 17);
}

static void draw_selector(u16 newIndex, u16 oldIndex, bool firstDraw)
{
    if (!firstDraw)
        VDP_clearTileMapRect(BG_A, SELECTOR_X, selectorY[oldIndex], SELECTOR_W, SELECTOR_H);

    VDP_drawImageEx(BG_A, &r2_selector,
                    TILE_ATTR_FULL(PAL0, TRUE, FALSE, FALSE, selectorTileBase),
                    SELECTOR_X, selectorY[newIndex], FALSE, TRUE);
}

static void draw_menu(void)
{
    u16 bgTiles;

    VDP_setTextPlane(BG_A);
    VDP_setTextPalette(PAL0);
    VDP_setTextPriority(TRUE);

    VDP_drawImageEx(BG_B, &r2_menu_bg,
                    TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, TILE_USER_INDEX),
                    0, 0, TRUE, TRUE);

    bgTiles = r2_menu_bg.tileset->numTile;
    selectorTileBase = (u16) (TILE_USER_INDEX + bgTiles);
    if ((selectorTileBase + r2_selector.tileset->numTile) > TILE_USER_MAX_INDEX)
    {
        VDP_drawText("MENU VRAM ERROR", 12, 24);
        return;
    }

    draw_selector(menuIndex, menuIndex, TRUE);
}

static s32 camera_scale_for_video(s32 valueAt60Hz)
{
    return (valueAt60Hz * 60 + (videoHz >> 1)) / videoHz;
}

static s32 camera_axis(s32 velocity, bool negativeHeld, bool positiveHeld)
{
    const s32 accel = camera_scale_for_video(CAMERA_ACCEL_FP);
    const s32 friction = camera_scale_for_video(CAMERA_FRICTION_FP);
    const s32 maxSpeed = camera_scale_for_video(CAMERA_MAX_SPEED_FP);

    if (negativeHeld && !positiveHeld) velocity -= accel;
    else if (positiveHeld && !negativeHeld) velocity += accel;
    else if (velocity > friction) velocity -= friction;
    else if (velocity < -friction) velocity += friction;
    else velocity = 0;

    if (velocity > maxSpeed) velocity = maxSpeed;
    if (velocity < -maxSpeed) velocity = -maxSpeed;
    return velocity;
}

static void update_camera(void)
{
    const s32 minX = ((s32) CAMERA_CENTER_X) << CAMERA_FP_SHIFT;
    const s32 minY = ((s32) CAMERA_CENTER_Y) << CAMERA_FP_SHIFT;
    const s32 maxX = ((s32) (MAP01_WORLD_WIDTH_PX - MAP_VIEW_WIDTH_PX + CAMERA_CENTER_X)) << CAMERA_FP_SHIFT;
    const s32 maxY = ((s32) (MAP01_WORLD_HEIGHT_PX - MAP_VIEW_HEIGHT_PX + CAMERA_CENTER_Y)) << CAMERA_FP_SHIFT;

    cameraVelocityXFP = camera_axis(cameraVelocityXFP,
                                    (input.held & BUTTON_LEFT) != 0,
                                    (input.held & BUTTON_RIGHT) != 0);
    cameraVelocityYFP = camera_axis(cameraVelocityYFP,
                                    (input.held & BUTTON_UP) != 0,
                                    (input.held & BUTTON_DOWN) != 0);

    cameraFocusXFP += cameraVelocityXFP;
    cameraFocusYFP += cameraVelocityYFP;

    if (cameraFocusXFP < minX) { cameraFocusXFP = minX; cameraVelocityXFP = 0; }
    if (cameraFocusXFP > maxX) { cameraFocusXFP = maxX; cameraVelocityXFP = 0; }
    if (cameraFocusYFP < minY) { cameraFocusYFP = minY; cameraVelocityYFP = 0; }
    if (cameraFocusYFP > maxY) { cameraFocusYFP = maxY; cameraVelocityYFP = 0; }
}

static void fill_hud_rect(u16 x, u16 y, u16 w, u16 h)
{
    const u16 attr = TILE_ATTR_FULL(PAL0, TRUE, FALSE, FALSE, hudFillTile);
    u16 yy;
    u16 xx;
    for (yy = y; yy < (u16) (y + h); yy++)
        for (xx = x; xx < (u16) (x + w); xx++)
            VDP_setTileMapXY(BG_A, attr, xx, yy);
}

static void update_hud_coordinates(u16 focusX, u16 focusY)
{
    char buffer[8];

    if (focusX != hudLastX)
    {
        hudLastX = focusX;
        uintToStr(focusX, buffer, 4);
        VDP_drawText(buffer, 32, 5);
    }
    if (focusY != hudLastY)
    {
        hudLastY = focusY;
        uintToStr(focusY, buffer, 4);
        VDP_drawText(buffer, 32, 7);
    }
}

static void draw_map_hud(void)
{
    /* 224x192 world viewport: 28x24 tiles. The rest of the 320x224 screen is
     * an opaque status frame on BG_A, so streamed BG_B data behind it is free. */
    VDP_loadTileData(hudFillPattern, hudFillTile, 1, DMA);
    fill_hud_rect(28, 0, 12, 28);
    fill_hud_rect(0, 24, 28, 4);

    VDP_setTextPlane(BG_A);
    VDP_setTextPalette(PAL0);
    VDP_setTextPriority(TRUE);
    VDP_drawText("MAP 01", 31, 2);
    VDP_drawText("X:", 29, 5);
    VDP_drawText("Y:", 29, 7);
    VDP_drawText("D-PAD", 31, 13);
    VDP_drawText("CAMERA", 30, 15);
    VDP_drawText("B: MENU", 30, 21);
    VDP_drawText("MAP 01 / APPROVED WORLD ART", 1, 25);
    VDP_drawText("1536x1152 / STREAMED", 1, 26);
}

static void draw_map01(void)
{
    const u16 nextTile = (u16) (TILE_USER_INDEX + MAP01_STREAM_CACHE_TILES + 1u);

    mapTileBase = TILE_USER_INDEX;
    hudFillTile = (u16) (mapTileBase + MAP01_STREAM_CACHE_TILES);

    if ((nextTile - 1u) > TILE_USER_MAX_INDEX)
    {
        PAL_setPalette(PAL0, palette_grey, CPU);
        VDP_drawText("MAP01 VRAM ERROR", 11, 12);
        return;
    }

    cameraFocusXFP = ((s32) MAP_START_X) << CAMERA_FP_SHIFT;
    cameraFocusYFP = ((s32) MAP_START_Y) << CAMERA_FP_SHIFT;
    cameraVelocityXFP = 0;
    cameraVelocityYFP = 0;
    mapScrollX = (u16) (MAP_START_X - CAMERA_CENTER_X);
    mapScrollY = (u16) (MAP_START_Y - CAMERA_CENTER_Y);
    hudLastX = 0xFFFFu;
    hudLastY = 0xFFFFu;

    if (!MAP01_streamInit(mapTileBase, mapScrollX, mapScrollY))
        return;

    mapStreamActive = TRUE;
    draw_map_hud();
    update_hud_coordinates(MAP_START_X, MAP_START_Y);
}

static void draw_garage(void)
{
    PAL_setPalette(PAL0, palette_grey, CPU);
    VDP_setTextPlane(BG_A);
    VDP_setTextPalette(PAL0);
    VDP_setTextPriority(TRUE);
    VDP_drawText("GARAGE", 17, 9);
    VDP_drawText("NOT CONNECTED YET", 11, 13);
    VDP_drawText("B: MENU", 16, 18);
}

static void enter_state(GameState state)
{
    VDP_setEnable(FALSE);
    leave_state();
    currentState = state;

    if (state == STATE_TITLE) draw_title();
    else if (state == STATE_MAIN_MENU) draw_menu();
    else if (state == STATE_MAP01) draw_map01();
    else draw_garage();

    VDP_waitFIFOEmpty();
    VDP_setEnable(TRUE);
}

static void input_poll(void)
{
    const u16 current = JOY_readJoypad(JOY_1);
    input.held = current;
    input.pressed = current & (u16) ~previousPad;
    input.released = previousPad & (u16) ~current;
    previousPad = current;
}

static void handle_input(void)
{
    if (currentState == STATE_TITLE)
    {
        if (input.pressed & (BUTTON_START | BUTTON_A)) enter_state(STATE_MAIN_MENU);
        return;
    }

    if (currentState == STATE_MAIN_MENU)
    {
        if (input.pressed & BUTTON_UP)
        {
            const u16 old = menuIndex;
            menuIndex = (menuIndex == 0u) ? (MENU_COUNT - 1u) : (u16) (menuIndex - 1u);
            draw_selector(menuIndex, old, FALSE);
        }
        if (input.pressed & BUTTON_DOWN)
        {
            const u16 old = menuIndex;
            menuIndex = (u16) ((menuIndex + 1u) % MENU_COUNT);
            draw_selector(menuIndex, old, FALSE);
        }
        if (input.pressed & (BUTTON_A | BUTTON_START))
        {
            if (menuIndex == 0u) enter_state(STATE_MAP01);
            else if (menuIndex == 1u) enter_state(STATE_GARAGE);
        }
        return;
    }

    if ((currentState == STATE_MAP01) || (currentState == STATE_GARAGE))
    {
        if (input.pressed & BUTTON_B) enter_state(STATE_MAIN_MENU);
    }
}

static void update_map_frame(void)
{
    u16 focusX;
    u16 focusY;
    u16 scrollX;
    u16 scrollY;

    if ((currentState != STATE_MAP01) || !mapStreamActive) return;

    update_camera();
    focusX = (u16) (cameraFocusXFP >> CAMERA_FP_SHIFT);
    focusY = (u16) (cameraFocusYFP >> CAMERA_FP_SHIFT);
    scrollX = (u16) (focusX - CAMERA_CENTER_X);
    scrollY = (u16) (focusY - CAMERA_CENTER_Y);

    if ((scrollX != mapScrollX) || (scrollY != mapScrollY))
    {
        mapScrollX = scrollX;
        mapScrollY = scrollY;
        MAP01_streamScrollTo(scrollX, scrollY);
    }

    update_hud_coordinates(focusX, focusY);
}

int main(bool hardReset)
{
    (void) hardReset;

    VDP_setScreenWidth320();
    VDP_setScreenHeight224();
    VDP_setPlaneSize(64, 32, TRUE);
    VDP_setScrollingMode(HSCROLL_PLANE, VSCROLL_PLANE);
    VDP_setBackgroundColor(0);

    JOY_setSupport(PORT_1, JOY_SUPPORT_3BTN);
    videoHz = SYS_isPAL() ? 50 : 60;

    reset_planes();
    clear_palettes();
    VDP_resetSprites();
    VDP_updateSprites(0, CPU);

    previousPad = JOY_readJoypad(JOY_1);
    draw_title();

    while (TRUE)
    {
        SYS_doVBlankProcess();
        input_poll();
        handle_input();
        update_map_frame();
    }

    return 0;
}
