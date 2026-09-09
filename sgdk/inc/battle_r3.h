#ifndef _BATTLE_R3_H_
#define _BATTLE_R3_H_

#include <genesis.h>

#define R3_WORLD_WIDTH_PX 8192
#define R3_WORLD_HEIGHT_PX 8192
#define R3_BATTLEFIELD_WIDTH_PX 224
#define R3_BATTLEFIELD_HEIGHT_PX 192
#define R3_HUD_WIDTH_PX 96
#define R3_LOG_HEIGHT_PX 32

void R3_battleEnter(void);
void R3_battleLeave(void);
void R3_battleSetInput(u16 held, u16 pressed);
void R3_battleUpdate(void);
void R3_battleSetCameraTarget(s32 worldX, s32 worldY);
bool R3_pointInsideBattlefield(s16 screenX, s16 screenY);

#endif
