#!/usr/bin/env python3
import json
from pathlib import Path
from PIL import Image
import numpy as np

ROOT = Path('sgdk/out/camera_deep')
HUD_PATH = Path('sgdk/res/r3_battle_hud.png')
W, H = 320, 224
FIELD_W, FIELD_H = 224, 192
RIGHT_X = 224
BOTTOM_Y = 192

# BlastEm output for accepted PAL0 index 7 and index 15.
HUD_BG = np.array([0, 0, 0], dtype=np.uint8)
HUD_YELLOW = np.array([255, 206, 49], dtype=np.uint8)

STATIC_TEXT = (
    ("REGION 1", 30, 2),
    ("X:", 29, 4),
    ("Y:", 29, 6),
    ("MAP", 31, 10),
    ("SCROLL", 30, 18),
    ("D-PAD", 30, 20),
    ("B: MENU", 29, 22),
    ("R3 WORLD STREAM / CAMERA", 1, 25),
    ("STATIC AUTHORED MAP", 1, 26),
)

def load_rgb(path):
    im = Image.open(path).convert('RGB')
    if im.size != (W, H):
        raise ValueError(f'{path}: expected {(W,H)}, got {im.size}')
    return np.array(im, dtype=np.uint8)

def cell_rect(tx, ty, length=1):
    return (tx * 8, ty * 8, (tx + length) * 8, (ty + 1) * 8)

def only_bg_or_yellow(region):
    bg = np.all(region == HUD_BG, axis=2)
    fg = np.all(region == HUD_YELLOW, axis=2)
    return bool(np.all(bg | fg)), int(np.size(bg) - np.count_nonzero(bg | fg))

def analyze_region(name):
    d = ROOT / name
    paths = sorted(p for p in d.glob('*_active.png') if p.stem not in ('00_boot_active',))
    if not paths:
        raise ValueError(f'{name}: no active battle screenshots')
    ref_path = d / '01_start_active.png'
    if not ref_path.exists():
        raise ValueError(f'{name}: missing 01_start_active.png')

    ref = load_rgb(ref_path)
    failures = []
    max_bottom_diff = 0
    max_right_static_diff = 0
    coord_foreign_pixels = 0
    static_text_foreign_pixels = 0

    # Mask for right panel pixels that are legitimately dynamic: four X digits and four Y digits.
    right_static_mask = np.ones((FIELD_H, W - RIGHT_X), dtype=bool)
    for ty in (4, 6):
        x0, y0, x1, y1 = cell_rect(31, ty, 4)
        right_static_mask[y0:y1, x0-RIGHT_X:x1-RIGHT_X] = False

    for path in paths:
        cur = load_rgb(path)

        # Bottom log is fully fixed and must be pixel-identical at every camera position.
        bottom_diff = np.any(cur[BOTTOM_Y:H, :] != ref[BOTTOM_Y:H, :], axis=2)
        bottom_count = int(np.count_nonzero(bottom_diff))
        max_bottom_diff = max(max_bottom_diff, bottom_count)
        if bottom_count:
            failures.append(f'{name}:{path.name}: bottom HUD changed in {bottom_count} pixels')

        # Right HUD may change only inside X/Y numeric digit cells.
        rd = np.any(cur[:FIELD_H, RIGHT_X:W] != ref[:FIELD_H, RIGHT_X:W], axis=2)
        static_count = int(np.count_nonzero(rd & right_static_mask))
        max_right_static_diff = max(max_right_static_diff, static_count)
        if static_count:
            failures.append(f'{name}:{path.name}: right static HUD changed in {static_count} pixels')

        # Dynamic coordinate cells must contain only opaque HUD black or yellow glyph pixels.
        for ty in (4, 6):
            x0, y0, x1, y1 = cell_rect(31, ty, 4)
            ok, foreign = only_bg_or_yellow(cur[y0:y1, x0:x1])
            coord_foreign_pixels += foreign
            if not ok:
                failures.append(f'{name}:{path.name}: coordinate cells contain {foreign} world/foreign pixels')

        # All static HUD text cells must likewise be opaque: no world pixels may leak through glyph background.
        for text, tx, ty in STATIC_TEXT:
            x0, y0, x1, y1 = cell_rect(tx, ty, len(text))
            ok, foreign = only_bg_or_yellow(cur[y0:y1, x0:x1])
            static_text_foreign_pixels += foreign
            if not ok:
                failures.append(f'{name}:{path.name}:{text}: static text cells contain {foreign} world/foreign pixels')

    # Source HUD contract: battlefield is transparent, fixed right/bottom areas are fully opaque.
    hud = np.array(Image.open(HUD_PATH), dtype=np.uint8)
    if hud.shape != (H, W):
        failures.append(f'{name}: source HUD shape {hud.shape} != {(H,W)}')
    else:
        field_nonzero = int(np.count_nonzero(hud[:FIELD_H, :FIELD_W]))
        right_zero = int(np.count_nonzero(hud[:FIELD_H, RIGHT_X:] == 0))
        bottom_zero = int(np.count_nonzero(hud[BOTTOM_Y:, :] == 0))
        if field_nonzero:
            failures.append(f'{name}: source HUD covers battlefield with {field_nonzero} nonzero pixels')
        if right_zero:
            failures.append(f'{name}: source right HUD has {right_zero} transparent pixels')
        if bottom_zero:
            failures.append(f'{name}: source bottom HUD has {bottom_zero} transparent pixels')
    report = {
        'region': name,
        'frames_checked': len(paths),
        'max_bottom_changed_pixels': max_bottom_diff,
        'max_right_static_changed_pixels': max_right_static_diff,
        'coordinate_foreign_pixels_total': coord_foreign_pixels,
        'static_text_foreign_pixels_total': static_text_foreign_pixels,
        'status': 'PASS' if not failures else 'FAIL',
        'failures': failures,
    }
    (d / 'R3_HUD_VISUAL_REPORT.json').write_text(json.dumps(report, indent=2) + '\n')
    return report

reports = {name: analyze_region(name) for name in ('ntsc', 'pal')}
failures = [f for r in reports.values() for f in r['failures']]
combined = {
    'status': 'PASS' if not failures else 'FAIL',
    'geometry': {
        'battlefield': [0, 0, 224, 192],
        'right_hud': [224, 0, 320, 192],
        'bottom_log': [0, 192, 320, 224],
    },
    'regions': reports,
    'failures': failures,
}
(ROOT / 'R3_HUD_VISUAL_COMBINED_REPORT.json').write_text(json.dumps(combined, indent=2) + '\n')
print(json.dumps({
    'status': combined['status'],
    'regions': {
        k: {
            'frames_checked': v['frames_checked'],
            'max_bottom_changed_pixels': v['max_bottom_changed_pixels'],
            'max_right_static_changed_pixels': v['max_right_static_changed_pixels'],
            'coordinate_foreign_pixels_total': v['coordinate_foreign_pixels_total'],
            'static_text_foreign_pixels_total': v['static_text_foreign_pixels_total'],
        } for k, v in reports.items()
    },
    'failure_count': len(failures),
}, indent=2))
raise SystemExit(1 if failures else 0)
