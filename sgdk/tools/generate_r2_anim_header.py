#!/usr/bin/env python3
from pathlib import Path
from PIL import Image
import numpy as np
from collections import Counter
import hashlib
import math

ROOT = Path(__file__).resolve().parents[1]
BG_PATH = ROOT / "res" / "r2_menu_bg.png"
OUT_PATH = ROOT / "src" / "r2_anim_assets.h"
EXPECTED_BG_SHA256 = "2e8630affb921321a26d0e2f893409cbd23124ac874fda2377cd321a4336cf29"

bg = Image.open(BG_PATH)
bg.load()
assert bg.mode == "P" and bg.size == (320, 224)
assert hashlib.sha256(BG_PATH.read_bytes()).hexdigest() == EXPECTED_BG_SHA256
pal = bg.getpalette()
base = np.array(bg, dtype=np.uint8)

def clone_flagless_patch(src):
    a = src.copy()
    mask = np.zeros_like(a, dtype=bool)
    for y in range(115, 134):
        if y < 128:
            xl, xr = 305, 319
        else:
            xl, xr = 305, max(311, 319 - (y - 127))
        mask[y, xl:xr + 1] = True
    mask[:, :305] = False
    orig = src.copy()
    h, w = a.shape
    for y, x in zip(*np.where(mask)):
        ty = (y // 8) * 8
        tx = (x // 8) * 8
        banks = (orig[ty:ty+8, tx:tx+8].flatten() >> 4).tolist()
        bank = Counter(banks).most_common(1)[0][0]
        chosen = None
        for r in range(1, 18):
            for dx, dy in [(-r,0),(-r,-1),(-r,1),(0,-r),(-r//2,-r),(r,0),(0,r)]:
                sx, sy = x + dx, y + dy
                if 0 <= sx < w and 0 <= sy < h and not mask[sy, sx] and (orig[sy, sx] >> 4) == bank:
                    chosen = int(orig[sy, sx])
                    if (chosen & 15) not in (0, 15):
                        break
            if chosen is not None and (chosen & 15) not in (0, 15):
                break
        if chosen is None:
            chosen = bank << 4
        a[y, x] = chosen
    return a[112:152, 288:320]

flag_patch = clone_flagless_patch(base)

water_indices = set(list(range(17, 28)) + [29])
candidate = np.isin(base[:, :112], list(water_indices))
seen = np.zeros_like(candidate, dtype=bool)
water_mask = np.zeros_like(candidate, dtype=bool)
for yy in range(224):
    for xx in range(112):
        if candidate[yy, xx] and not seen[yy, xx]:
            stack = [(xx, yy)]
            seen[yy, xx] = True
            pts = []
            while stack:
                x0, y0 = stack.pop()
                pts.append((x0, y0))
                for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
                    nx, ny = x0 + dx, y0 + dy
                    if 0 <= nx < 112 and 0 <= ny < 224 and candidate[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        stack.append((nx, ny))
            if len(pts) >= 100:
                for x0, y0 in pts:
                    water_mask[y0, x0] = True

def lum(idx):
    r, g, b = pal[idx*3:idx*3+3]
    return 0.2126*r + 0.7152*g + 0.0722*b

shade_order = sorted(water_indices, key=lum)
rank = {idx:i for i,idx in enumerate(shade_order)}
def nudge(idx, delta):
    r = rank[int(idx)]
    return shade_order[max(0, min(len(shade_order)-1, r + delta))]

river_frames = []
region = base[:, :112]
for phase in (0, 2, 4, 6):
    rr = np.full((224, 112), 16, dtype=np.uint8)
    ys, xs = np.where(water_mask)
    for y, x in zip(ys, xs):
        idx = int(region[y, x])
        p = (y - phase + ((x*3 + (x >> 2)) & 7)) & 7
        hsh = (x*17 + y*13 + (x*y) % 19) & 15
        delta = 0
        if p == 0 and hsh < 7:
            delta = 1
        elif p == 1 and hsh < 3:
            delta = 1
        elif p == 4 and hsh < 5:
            delta = -1
        rr[y, x] = nudge(idx, delta)
    river_frames.append(rr)

flag_frames = []
for phase in (0, 2, 4, 6):
    fa = np.zeros((40, 32), dtype=np.uint8)
    anchor_x, top, height = 16, 5, 16
    for ly in range(top, top + height):
        t = ly - top
        wave = int(round(1.4 * math.sin((t / 4.0) + (phase * math.pi / 4.0))))
        right = 30 + (1 if ((phase + t // 5) & 3) == 1 else 0)
        left = anchor_x + 1
        if t > 11:
            right -= (t - 11) // 2
        for lx in range(left, right + 1):
            edge = min(lx-left, right-lx, t, height-1-t)
            if edge <= 0:
                val = 59
            elif ((lx + ly + phase) & 5) == 0:
                val = 53
            elif lx - left < 4:
                val = 56
            else:
                val = 50 if ((lx + ly) & 3) else 49
            xx = lx + wave
            if 0 <= xx < 32:
                fa[ly, xx] = val
    for ty in range(0, 40, 8):
        for tx in range(0, 32, 8):
            tile = fa[ty:min(ty+8,40), tx:tx+8]
            if np.any(tile >= 48):
                tile[tile == 0] = 48
    flag_frames.append(fa)

def make_fire(frame, lower=False):
    a = np.zeros((40,32), dtype=np.uint8)
    cx = 16
    if lower:
        base_y, height, base_half = 27, 15, 4
        ph = (frame + 1) * math.pi / 2 + 1.1
    else:
        base_y, height, base_half = 34, 25, 7
        ph = frame * math.pi / 2 + 0.3
    for yy in range(height):
        y = base_y - yy
        frac = yy / max(1, height - 1)
        sway = 1.7 * math.sin(ph + yy * 0.42)
        half = max(1, int(base_half * (1 - frac * 0.76) + 0.8 * math.sin(yy * 0.6 + frame)))
        c = int(round(cx + sway * (0.25 + frac)))
        for x in range(c-half, c+half+1):
            if 0 <= x < 32:
                d = abs(x-c) / max(1, half)
                if frac < .22 and d < .35:
                    val = 12
                elif frac < .52 and d < .48:
                    val = 11
                elif d < .72:
                    val = 10
                else:
                    val = 9 if ((x+y+frame) & 1) else 8
                a[y, x] = val
    return a

fire_upper_frames = [make_fire(i, False) for i in range(4)]
fire_lower_frames = [make_fire(i, True) for i in range(4)]

def frame_union(frames):
    h, w = frames[0].shape
    coords = []
    for ty in range(0, h, 8):
        for tx in range(0, w, 8):
            if any(np.any((a[ty:ty+8,tx:tx+8] & 15) != 0) for a in frames):
                coords.append((tx//8, ty//8))
    return coords

def tile_words(a, tx, ty):
    tile = a[ty*8:ty*8+8, tx*8:tx*8+8] & 15
    words = []
    for row in tile:
        val = 0
        for p in row:
            val = (val << 4) | int(p)
        words.append(val)
    return words

groups = [
    ("RIVER", river_frames, 1),
    ("FLAG", flag_frames, 3),
    ("FIRE_UPPER", fire_upper_frames, 0),
    ("FIRE_LOWER", fire_lower_frames, 0),
]

lines = [
    "#ifndef R2_ANIM_ASSETS_H",
    "#define R2_ANIM_ASSETS_H",
    "",
    "#include <genesis.h>",
    "",
    "#define R2_ANIM_FRAMES 4",
    "",
]

patch_coords = [(tx,ty) for ty in range(5) for tx in range(4)]
patch_banks = []
for tx, ty in patch_coords:
    t = flag_patch[ty*8:ty*8+8, tx*8:tx*8+8]
    banks = set((t.flatten() >> 4).tolist())
    assert len(banks) == 1
    patch_banks.append(next(iter(banks)))

lines.append(f"#define R2_FLAG_PATCH_TILE_COUNT {len(patch_coords)}")
lines.append("static const u8 r2_flag_patch_pal[R2_FLAG_PATCH_TILE_COUNT] = {")
lines.append("    " + ", ".join(str(x) for x in patch_banks))
lines.append("};")
lines.append("static const u32 r2_flag_patch_tiles[R2_FLAG_PATCH_TILE_COUNT][8] = {")
for tx, ty in patch_coords:
    words = tile_words(flag_patch, tx, ty)
    lines.append("    {" + ", ".join(f"0x{w:08X}" for w in words) + "},")
lines.append("};")
lines.append("")

for name, frames, palbank in groups:
    coords = frame_union(frames)
    cname = name.lower()
    lines.append(f"#define R2_{name}_TILE_COUNT {len(coords)}")
    lines.append(f"#define R2_{name}_PAL {palbank}")
    lines.append(f"static const u8 r2_{cname}_tile_x[R2_{name}_TILE_COUNT] = {{")
    lines.append("    " + ", ".join(str(x) for x,y in coords))
    lines.append("};")
    lines.append(f"static const u8 r2_{cname}_tile_y[R2_{name}_TILE_COUNT] = {{")
    lines.append("    " + ", ".join(str(y) for x,y in coords))
    lines.append("};")
    lines.append(f"static const u32 r2_{cname}_frames[R2_ANIM_FRAMES][R2_{name}_TILE_COUNT][8] = {{")
    for frame in frames:
        lines.append("  {")
        for tx, ty in coords:
            words = tile_words(frame, tx, ty)
            lines.append("    {" + ", ".join(f"0x{w:08X}" for w in words) + "},")
        lines.append("  },")
    lines.append("};")
    lines.append("")

lines.append("#endif")
OUT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("generated", OUT_PATH, hashlib.sha256(OUT_PATH.read_bytes()).hexdigest())
