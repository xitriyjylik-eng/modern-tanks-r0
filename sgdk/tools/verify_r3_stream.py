from pathlib import Path
import hashlib

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "res"
SRC = ROOT / "src"

WORLD_W = 960
WORLD_H = 960
WORLD_TILES = (WORLD_W // 8) * (WORLD_H // 8)
CHUNK_BYTES = 480 * 32

# Runtime uses the raw uncompressed ROM data directly.
# The authored source PNG is intentionally not required for CI/build.
for i in range(30):
    p = RES / f"r3_target_world_tiles_{i:02d}.bin"
    assert p.stat().st_size == CHUNK_BYTES, (p, p.stat().st_size)

banks = RES / "r3_target_world_banks.bin"
assert banks.stat().st_size == WORLD_TILES, banks.stat().st_size

res = (RES / "resources.res").read_text(encoding="utf-8")
for i in range(30):
    token = f'BIN r3_target_world_tiles_{i:02d} "r3_target_world_tiles_{i:02d}.bin" 4 4 0 NONE FALSE'
    assert token in res, token
assert 'BIN r3_target_world_banks "r3_target_world_banks.bin" 2 2 0 NONE FALSE' in res

main = (SRC / "main.c").read_text(encoding="utf-8")
stream = (SRC / "r3_stream_world.c").read_text(encoding="utf-8")

for token in (
    '#include "r3_stream_world.h"',
    'R3_worldEnter();',
    'R3_worldLeave();',
    'R3_worldUpdate(input.held);',
):
    assert token in main, token

for token in (
    "R3_VIEW_W_PX 224",
    "R3_VIEW_H_PX 192",
    "R3_CAM_RESPONSE_SHIFT 2",
    "R3_CAM_MAX_STEP_Q8",
    "R3_RING_W 32",
    "R3_RING_H 32",
    "VDP_loadTileData",
    "VDP_setTileMapXY",
):
    assert token in stream, token

menu = RES / "r2_menu_bg.png"
assert menu.exists()
print("r2_menu_bg_sha256", hashlib.sha256(menu.read_bytes()).hexdigest())

print("R3 STREAM VERIFY PASS")
print("world_tiles", WORLD_TILES)
print("raw_pattern_bytes", WORLD_TILES * 32)
print("palette_bank_bytes", WORLD_TILES)
print("compression", "NONE")
