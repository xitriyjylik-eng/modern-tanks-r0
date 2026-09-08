#include <genesis.h>

/*
 * Modern Tanks R1 — Core / State Machine
 *
 * Clean SGDK rebuild line only. No DEV code, no Granada assets/code.
 * R1 is intentionally a diagnostic shell: R2 owns final menu visuals.
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

#define R1_LOGIC_HZ 60
#define R1_BOOT_TICKS 90
#define R1_SOAK_TRANSITIONS 100
#define R1_SOAK_STEP_TICKS 4

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
static u16 stateEnterCount[STATE_COUNT];
static u16 stateLeaveCount[STATE_COUNT];

static bool soakActive = FALSE;
static bool soakPassed = FALSE;
static u16 soakTransitions = 0;
static u16 soakStepTicks = 0;

static const char *lastError = "NONE";

static const char *state_name(GameState state)
{
    switch (state)
    {
        case STATE_BOOT: return "BOOT";
        case STATE_TITLE: return "TITLE";
        case STATE_MAIN_MENU: return "MAIN_MENU";
        case STATE_TEST_BATTLE: return "TEST_BATTLE";
        case STATE_GARAGE: return "GARAGE";
        default: return "INVALID";
    }
}

static const char *bank_name(ResourceBank bank)
{
    switch (bank)
    {
        case BANK_NONE: return "NONE";
        case BANK_CORE: return "CORE";
        case BANK_MENU: return "MENU";
        case BANK_BATTLE_SHELL: return "BATTLE";
        case BANK_GARAGE_SHELL: return "GARAGE";
        default: return "INVALID";
    }
}

static ResourceBank state_bank(GameState state)
{
    switch (state)
    {
        case STATE_BOOT:
        case STATE_TITLE:
            return BANK_CORE;
        case STATE_MAIN_MENU:
            return BANK_MENU;
        case STATE_TEST_BATTLE:
            return BANK_BATTLE_SHELL;
        case STATE_GARAGE:
            return BANK_GARAGE_SHELL;
        default:
            return BANK_NONE;
    }
}

static void set_error(const char *code)
{
    errorCount++;
    lastError = code;
}

static void clear_all_palettes(void)
{
    /*
     * palette_black is SGDK's 64-entry all-black CRAM source.
     * Use one contiguous CPU write, then explicitly drain the VDP FIFO before
     * any readback. Immediate CRAM readback after FIFO-backed writes can see
     * stale values on Mega Drive timing/emulator implementations.
     */
    PAL_setColors(0, palette_black, 64, CPU);
    VDP_waitFIFOEmpty();
}

static bool palettes_are_black(void)
{
    u16 colors[64];
    u16 i;

    /* Ensure every earlier CRAM write is committed before changing the VDP
     * command port to CRAM-read mode. */
    VDP_waitFIFOEmpty();
    PAL_getColors(0, colors, 64);

    for (i = 0; i < 64; i++)
    {
        if (colors[i] != 0) return FALSE;
    }
    return TRUE;
}

static void resource_bank_unload(void)
{
    /* R1 cleanup contract: no state-owned plane, palette or VDP sprite survives. */
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

    activeBank = BANK_NONE;
    bankGeneration++;
}

static void resource_bank_load(ResourceBank bank)
{
    u32 backdrop = 0x080808;

    if (activeBank != BANK_NONE)
    {
        set_error("BANK_LOAD_OVERLAP");
        resource_bank_unload();
    }

    /* Built-in SGDK font only in R1. Real art banks start at R2/R3. */
    PAL_setPalette(PAL0, palette_grey, CPU);

    switch (bank)
    {
        case BANK_CORE: backdrop = 0x081018; break;
        case BANK_MENU: backdrop = 0x081C10; break;
        case BANK_BATTLE_SHELL: backdrop = 0x241008; break;
        case BANK_GARAGE_SHELL: backdrop = 0x180C24; break;
        default: backdrop = 0x200000; break;
    }

    PAL_setColor(0, RGB24_TO_VDPCOLOR(backdrop));
    activeBank = bank;
    bankGeneration++;
}

static void draw_number_at(u16 value, u16 x, u16 y, u16 minDigits)
{
    char buffer[8];
    uintToStr(value, buffer, minDigits);
    VDP_drawText(buffer, x, y);
}

static void draw_common_header(void)
{
    VDP_drawText("MODERN TANKS", 14, 1);
    VDP_drawText("R1 CORE / STATE MACHINE", 8, 3);
}

static void draw_debug_layer(void)
{
    VDP_drawText("STATE:                 ", 1, 22);
    VDP_drawText(state_name(currentState), 8, 22);

    VDP_drawText("BANK:            GEN:     ", 1, 23);
    VDP_drawText(bank_name(activeBank), 7, 23);
    draw_number_at(bankGeneration, 24, 23, 3);

    VDP_drawText("VIDEO:      HZ LOGIC:60", 1, 24);
    draw_number_at(videoHz, 8, 24, 2);

    VDP_drawText("TRANS:     ERR:     ", 1, 25);
    draw_number_at(transitionCount, 7, 25, 3);
    draw_number_at(errorCount, 16, 25, 2);

    VDP_drawText("LAST ERROR:                   ", 1, 26);
    VDP_drawText(lastError, 13, 26);

    if (soakActive)
    {
        VDP_drawText("SOAK:     /100 RUNNING", 1, 27);
        draw_number_at(soakTransitions, 7, 27, 3);
    }
    else if (soakPassed)
    {
        VDP_drawText("SOAK: PASS 100/100     ", 1, 27);
    }
    else
    {
        VDP_drawText("SOAK: READY - C IN MENU", 1, 27);
    }
}

static void draw_boot(void)
{
    draw_common_header();
    VDP_drawText("BOOT", 18, 7);
    VDP_drawText("STANDARD SGDK STARTUP", 9, 10);
    VDP_drawText("3-BUTTON INPUT PATH", 10, 12);
    VDP_drawText("RESOURCE BANK API READY", 8, 14);
    VDP_drawText("AUTO -> TITLE", 13, 18);
}

static void draw_title(void)
{
    draw_common_header();
    VDP_drawText("TITLE SHELL", 14, 8);
    VDP_drawText("PRESS START OR A", 11, 13);
    VDP_drawText("R1 FUNCTIONAL SHELL ONLY", 7, 17);
    VDP_drawText("FINAL MENU ART BEGINS AT R2", 6, 19);
}

static void draw_menu(void)
{
    static const char *items[4] =
    {
        "PLAY [TEST BATTLE]",
        "GARAGE",
        "STATISTICS [R1 LOCKED]",
        "OPTIONS [R1 LOCKED]"
    };
    u16 i;

    draw_common_header();
    VDP_drawText("MAIN MENU SHELL", 12, 6);

    for (i = 0; i < 4; i++)
    {
        VDP_drawText((i == menuIndex) ? ">" : " ", 6, 9 + (i * 2));
        VDP_drawText(items[i], 8, 9 + (i * 2));
    }

    VDP_drawText("A/START: ENTER  C: 100-TRANS SOAK", 2, 19);
}

static void draw_test_battle(void)
{
    draw_common_header();
    VDP_drawText("TEST BATTLE SHELL", 11, 8);
    VDP_drawText("NO GAMEPLAY IN R1", 11, 11);
    VDP_drawText("B: RETURN TO MENU", 11, 15);
    VDP_drawText("BATTLE BANK IS ISOLATED", 8, 18);
}

static void draw_garage(void)
{
    draw_common_header();
    VDP_drawText("GARAGE SHELL", 14, 8);
    VDP_drawText("NO GARAGE ART IN R1", 10, 11);
    VDP_drawText("B: RETURN TO MENU", 11, 15);
    VDP_drawText("GARAGE BANK IS ISOLATED", 8, 18);
}

static void state_draw(GameState state)
{
    switch (state)
    {
        case STATE_BOOT: draw_boot(); break;
        case STATE_TITLE: draw_title(); break;
        case STATE_MAIN_MENU: draw_menu(); break;
        case STATE_TEST_BATTLE: draw_test_battle(); break;
        case STATE_GARAGE: draw_garage(); break;
        default: set_error("DRAW_INVALID_STATE"); break;
    }
    draw_debug_layer();
}

static void state_enter(GameState state)
{
    ResourceBank expected = state_bank(state);

    stateEnterCount[state]++;
    stateTicks = 0;
    resource_bank_load(expected);

    if (activeBank != expected) set_error("BANK_STATE_MISMATCH");
    state_draw(state);
}

static void state_leave(GameState state)
{
    stateLeaveCount[state]++;
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

    state_leave(currentState);
    currentState = next;
    transitionCount++;
    state_enter(currentState);
}

static void input_poll(void)
{
    u16 current = JOY_readJoypad(JOY_1);
    input.held = current;
    input.pressed = current & (u16) ~previousPad;
    input.released = previousPad & (u16) ~current;
    previousPad = current;
}

static void start_soak(void)
{
    if (currentState != STATE_MAIN_MENU) return;

    soakActive = TRUE;
    soakPassed = FALSE;
    soakTransitions = 0;
    soakStepTicks = 0;
}

static void update_soak_tick(void)
{
    GameState next;
    u16 phase;

    if (!soakActive) return;

    soakStepTicks++;
    if (soakStepTicks < R1_SOAK_STEP_TICKS) return;
    soakStepTicks = 0;

    phase = soakTransitions & 3;
    if (phase == 0) next = STATE_TEST_BATTLE;
    else if (phase == 1) next = STATE_MAIN_MENU;
    else if (phase == 2) next = STATE_GARAGE;
    else next = STATE_MAIN_MENU;

    change_state(next);
    soakTransitions++;

    if (soakTransitions >= R1_SOAK_TRANSITIONS)
    {
        soakActive = FALSE;
        soakPassed = (errorCount == 0) && (currentState == STATE_MAIN_MENU);
        if (!soakPassed) set_error("SOAK_FAILED");
        state_draw(currentState);
    }
}

static void handle_input_frame(void)
{
    if (soakActive) return;

    switch (currentState)
    {
        case STATE_TITLE:
            if (input.pressed & (BUTTON_START | BUTTON_A)) change_state(STATE_MAIN_MENU);
            break;

        case STATE_MAIN_MENU:
            if (input.pressed & BUTTON_UP)
            {
                menuIndex = (menuIndex == 0) ? 3 : (menuIndex - 1);
                state_draw(currentState);
            }
            if (input.pressed & BUTTON_DOWN)
            {
                menuIndex = (menuIndex + 1) & 3;
                state_draw(currentState);
            }
            if (input.pressed & BUTTON_C)
            {
                start_soak();
                state_draw(currentState);
            }
            if (input.pressed & (BUTTON_A | BUTTON_START))
            {
                if (menuIndex == 0) change_state(STATE_TEST_BATTLE);
                else if (menuIndex == 1) change_state(STATE_GARAGE);
                else
                {
                    lastError = "R1_ITEM_NOT_IMPLEMENTED";
                    state_draw(currentState);
                }
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
        if (stateTicks >= R1_BOOT_TICKS) change_state(STATE_TITLE);
        return;
    }

    update_soak_tick();
}

int main(bool hardReset)
{
    u16 i;

    (void) hardReset;

    VDP_setScreenWidth320();
    VDP_setScreenHeight224();
    VDP_setPlaneSize(64, 32, TRUE);
    VDP_setTextPlane(BG_A);
    VDP_setTextPalette(PAL0);
    VDP_setTextPriority(TRUE);

    JOY_setSupport(PORT_1, JOY_SUPPORT_3BTN);

    videoHz = SYS_isPAL() ? 50 : 60;
    for (i = 0; i < STATE_COUNT; i++)
    {
        stateEnterCount[i] = 0;
        stateLeaveCount[i] = 0;
    }

    clear_all_palettes();
    VDP_resetSprites();
    VDP_updateSprites(0, CPU);

    previousPad = JOY_readJoypad(JOY_1);
    state_enter(STATE_BOOT);

    while (TRUE)
    {
        /* SGDK owns VBlank and controller polling. */
        SYS_doVBlankProcess();
        input_poll();
        handle_input_frame();

        /* Fixed 60 Hz logic clock: PAL executes 6 logic ticks per 5 video frames. */
        logicAccumulator += R1_LOGIC_HZ;
        while (logicAccumulator >= videoHz)
        {
            logicAccumulator -= videoHz;
            update_logic_tick();
        }

        draw_debug_layer();
    }

    return 0;
}
