#include <genesis.h>

#define R0_MIN_X 2
#define R0_MAX_X 37
#define R0_MIN_Y 17
#define R0_MAX_Y 22
#define R0A_FRAMES 120
#define R0B_FRAMES 120

static const char *button_name(u16 pressed)
{
    if (pressed & BUTTON_A) return "A";
    if (pressed & BUTTON_B) return "B";
    if (pressed & BUTTON_C) return "C";
    if (pressed & BUTTON_START) return "START";
    if (pressed & BUTTON_UP) return "UP";
    if (pressed & BUTTON_DOWN) return "DOWN";
    if (pressed & BUTTON_LEFT) return "LEFT";
    if (pressed & BUTTON_RIGHT) return "RIGHT";
    return "NONE";
}

static void draw_header(void)
{
    VDP_drawText("MODERN TANKS", 14, 3);
    VDP_drawText("R0 HARDWARE PROBE", 11, 5);
    VDP_drawText("SGDK 2.11 / H40 320x224 / 64x32", 3, 7);
}

static void clear_and_header(u32 backdrop)
{
    PAL_setColor(0, RGB24_TO_VDPCOLOR(backdrop));
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
    draw_header();
}

static void set_probe_backdrop(u16 pressed)
{
    /* Visible input confirmation independent of text rendering. */
    if (pressed & BUTTON_A)
        PAL_setColor(0, RGB24_TO_VDPCOLOR(0x082818));
    else if (pressed & BUTTON_B)
        PAL_setColor(0, RGB24_TO_VDPCOLOR(0x08182C));
    else if (pressed & BUTTON_C)
        PAL_setColor(0, RGB24_TO_VDPCOLOR(0x300C0C));
    else if (pressed & BUTTON_START)
        PAL_setColor(0, RGB24_TO_VDPCOLOR(0x201C08));
}

int main(bool hardReset)
{
    u16 markerX = 20;
    u16 markerY = 19;
    u16 previous;
    u16 i;

    (void) hardReset;

    /*
     * R0 uses only public SGDK 2.11 APIs after SGDK's own startup.
     * No custom bootstrap, no custom vectors, no resources, no SRAM,
     * no audio, no sprites, no maps and no gameplay code.
     */
    VDP_setScreenWidth320();
    VDP_setScreenHeight224();
    VDP_setPlaneSize(64, 32, TRUE);
    VDP_setTextPlane(BG_A);
    VDP_setTextPalette(PAL0);
    VDP_setTextPriority(TRUE);

    /*
     * R0A isolates SGDK startup + VDP + raw VSync waiting.
     * It deliberately DOES NOT call SYS_doVBlankProcess(), because that
     * routine also runs the integrated SGDK VBlank subsystems including
     * joypad polling.
     */
    clear_and_header(0x081018);
    VDP_drawText("R0A: BOOT + VDP + RAW VSYNC", 5, 11);
    VDP_drawText("WAITING 120 VSYNC PERIODS...", 5, 13);

    for (i = 0; i < R0A_FRAMES; i++)
        VDP_waitVSync();

    /*
     * R0B adds SGDK's complete per-frame VBlank processing but still does
     * not read controller state from user code. If R0A passes and R0B does
     * not, the fault is above raw VDP/VSync and inside the system pipeline.
     */
    clear_and_header(0x081820);
    VDP_drawText("R0A PASS: RAW VSYNC", 9, 10);
    VDP_drawText("R0B: SGDK VBLANK PIPELINE", 6, 12);
    VDP_drawText("WAITING 120 SYSTEM FRAMES...", 5, 14);

    for (i = 0; i < R0B_FRAMES; i++)
        SYS_doVBlankProcess();

    /*
     * R0C is the first phase that explicitly configures and reads port 1.
     * Use the simplest native Mega Drive controller protocol on purpose.
     */
    JOY_setSupport(PORT_1, JOY_SUPPORT_3BTN);

    clear_and_header(0x101808);
    VDP_drawText("R0A PASS: RAW VSYNC", 9, 9);
    VDP_drawText("R0B PASS: SYSTEM VBLANK", 7, 11);
    VDP_drawText("R0C: 3-BUTTON INPUT ACTIVE", 6, 13);
    VDP_drawText("LAST INPUT: NONE", 2, 15);
    VDP_drawText("D-PAD MOVES >", 2, 24);
    VDP_drawText("A/B/C/START CHANGE BACKDROP", 2, 25);
    VDP_drawText(">", markerX, markerY);

    previous = JOY_readJoypad(JOY_1);

    while (TRUE)
    {
        u16 current;
        u16 pressed;

        /* SGDK performs its normal system update once per frame. */
        SYS_doVBlankProcess();

        current = JOY_readJoypad(JOY_1);
        pressed = current & (u16) ~previous;

        if (pressed)
        {
            const u16 oldX = markerX;
            const u16 oldY = markerY;

            if ((pressed & BUTTON_LEFT) && (markerX > R0_MIN_X)) markerX--;
            if ((pressed & BUTTON_RIGHT) && (markerX < R0_MAX_X)) markerX++;
            if ((pressed & BUTTON_UP) && (markerY > R0_MIN_Y)) markerY--;
            if ((pressed & BUTTON_DOWN) && (markerY < R0_MAX_Y)) markerY++;

            if ((oldX != markerX) || (oldY != markerY))
            {
                VDP_drawText(" ", oldX, oldY);
                VDP_drawText(">", markerX, markerY);
            }

            VDP_drawText("LAST INPUT:            ", 2, 15);
            VDP_drawText(button_name(pressed), 14, 15);
            set_probe_backdrop(pressed);
        }

        previous = current;
    }

    return 0;
}
