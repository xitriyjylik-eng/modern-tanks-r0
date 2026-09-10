#!/usr/bin/env python3
import json
from pathlib import Path
from PIL import Image

root = Path('sgdk/out/runtime_smoke')
names = ['01_title','02_menu','03_battle_start','04_battle_right','05_battle_down','06_menu_return']
raw = {n: Image.open(root / f'{n}.png').convert('RGB') for n in names}
raw_sizes = {n: list(v.size) for n, v in raw.items()}

# BlastEm 0.6.3.4 on Ubuntu may save overscan/border around the native H40 frame.
# Derive the 320x224 active frame from the menu shot instead of assuming raw PNG size.
menu = raw['02_menu']
if menu.size == (320, 224):
    crop = (0, 0, 320, 224)
else:
    pix = menu.load()
    xs = []
    ys = []
    for y in range(menu.height):
        for x in range(menu.width):
            if pix[x, y] != (0, 0, 0):
                xs.append(x)
                ys.append(y)
    if not xs:
        raise SystemExit('menu screenshot is completely black')
    crop = (min(xs), min(ys), max(xs) + 1, max(ys) + 1)
    if (crop[2] - crop[0], crop[3] - crop[1]) != (320, 224):
        raise SystemExit(f'cannot identify 320x224 active frame, raw={menu.size}, bbox={crop}')

im = {n: v.crop(crop) for n, v in raw.items()}
for n, v in im.items():
    if v.size != (320, 224):
        raise SystemExit(f'normalized screenshot {n} is {v.size}, expected 320x224')
    v.save(root / f'{n}_active.png')


def diff_ratio(a, b, box=None):
    if box:
        a = a.crop(box)
        b = b.crop(box)
    pa = list(a.getdata())
    pb = list(b.getdata())
    return sum(x != y for x, y in zip(pa, pb)) / len(pa)


def yellow_mask_diff(a, b, box):
    a = a.crop(box)
    b = b.crop(box)
    pa = list(a.getdata())
    pb = list(b.getdata())
    def yellow(p):
        r, g, bl = p
        return r > 180 and g > 130 and bl < 100
    return sum(yellow(x) != yellow(y) for x, y in zip(pa, pb)) / len(pa)

field = (0, 0, 224, 192)
right_hud = (224, 0, 320, 192)
bottom = (0, 192, 320, 224)
full = (0, 0, 320, 224)

metrics = {
    'title_to_menu_full': diff_ratio(im['01_title'], im['02_menu'], full),
    'menu_to_battle_full': diff_ratio(im['02_menu'], im['03_battle_start'], full),
    'camera_right_field': diff_ratio(im['03_battle_start'], im['04_battle_right'], field),
    'camera_right_hud_raw': diff_ratio(im['03_battle_start'], im['04_battle_right'], right_hud),
    'camera_right_bottom_raw': diff_ratio(im['03_battle_start'], im['04_battle_right'], bottom),
    'camera_down_field': diff_ratio(im['04_battle_right'], im['05_battle_down'], field),
    'camera_down_hud_raw': diff_ratio(im['04_battle_right'], im['05_battle_down'], right_hud),
    'camera_down_bottom_raw': diff_ratio(im['04_battle_right'], im['05_battle_down'], bottom),
    'camera_right_bottom_text_mask': yellow_mask_diff(im['03_battle_start'], im['04_battle_right'], bottom),
    'camera_down_bottom_text_mask': yellow_mask_diff(im['04_battle_right'], im['05_battle_down'], bottom),
    'return_vs_menu_full': diff_ratio(im['06_menu_return'], im['02_menu'], full),
    'return_vs_battle_full': diff_ratio(im['06_menu_return'], im['05_battle_down'], full),
}

failures = []
warnings = []
if metrics['title_to_menu_full'] < 0.08:
    failures.append('TITLE->MENU did not visibly transition')
if metrics['menu_to_battle_full'] < 0.15:
    failures.append('MENU->BATTLE did not visibly transition')
if metrics['camera_right_field'] < 0.08:
    failures.append('RIGHT hold did not visibly move battlefield')
if metrics['camera_down_field'] < 0.08:
    failures.append('DOWN hold did not visibly move battlefield')
if metrics['camera_right_hud_raw'] > 0.20:
    failures.append('right HUD changed too much during RIGHT camera move')
if metrics['camera_down_hud_raw'] > 0.20:
    failures.append('right HUD changed too much during DOWN camera move')
if metrics['camera_right_bottom_text_mask'] > 0.001:
    failures.append('bottom fixed UI text moved during RIGHT camera move')
if metrics['camera_down_bottom_text_mask'] > 0.001:
    failures.append('bottom fixed UI text moved during DOWN camera move')
if metrics['return_vs_menu_full'] != 0.0:
    failures.append('BATTLE->MENU did not return pixel-identically to captured menu')
if metrics['return_vs_menu_full'] >= metrics['return_vs_battle_full']:
    failures.append('B button did not return screen closer to menu than battle')

# The SGDK system font uses transparent color 0. Because battle text is on BG_A,
# the scrolling BG_B can be visible through transparent glyph/background pixels.
# This does not move the UI itself, but is a visual-layering issue for Stage 8.
if metrics['camera_right_bottom_raw'] > 0.05 or metrics['camera_down_bottom_raw'] > 0.05:
    warnings.append('BG_B is visible through transparent battle text cells; UI text mask itself is fixed. Review visual layering in Stage 8.')

report = {
    'emulator': 'BlastEm 0.6.3.4 Ubuntu package',
    'region': 'U/NTSC',
    'raw_screenshot_sizes': raw_sizes,
    'active_frame_crop': list(crop),
    'active_frame_size': [320, 224],
    'metrics': metrics,
    'status': 'FAIL' if failures else ('PASS_WITH_WARNINGS' if warnings else 'PASS'),
    'failures': failures,
    'warnings': warnings,
}
(root / 'R3_RUNTIME_SMOKE_REPORT.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
raise SystemExit(1 if failures else 0)
