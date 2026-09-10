#!/usr/bin/env python3
import csv, json
from pathlib import Path
from PIL import Image

ROOT = Path('sgdk/out/stage10_soak')
CASES = {
    'ntsc': {'min_seconds': 630, 'min_cycles': 40},
    'pal': {'min_seconds': 120, 'min_cycles': 8},
}


def active_crop(img):
    if img.size == (320, 224):
        return (0, 0, 320, 224)
    pix = img.load()
    xs, ys = [], []
    for y in range(img.height):
        for x in range(img.width):
            if pix[x, y] != (0, 0, 0):
                xs.append(x); ys.append(y)
    if not xs:
        raise ValueError('completely black screenshot')
    box = (min(xs), min(ys), max(xs)+1, max(ys)+1)
    if (box[2]-box[0], box[3]-box[1]) != (320, 224):
        raise ValueError(f'active frame is not 320x224: raw={img.size} bbox={box}')
    return box


def ratio(a, b, box=None):
    if box:
        a = a.crop(box); b = b.crop(box)
    pa = list(a.getdata()); pb = list(b.getdata())
    return sum(x != y for x, y in zip(pa, pb)) / len(pa)


def load_active(path, crop):
    return Image.open(path).convert('RGB').crop(crop)

reports = {}
all_failures = []
for case, req in CASES.items():
    d = ROOT / case
    failures = []
    summary = {}
    for line in (d / 'summary.txt').read_text().splitlines():
        if '=' in line:
            k, v = line.split('=', 1); summary[k] = v
    elapsed = int(summary.get('elapsed_seconds', 0))
    cycles = int(summary.get('cycles', 0))
    if elapsed < req['min_seconds']:
        failures.append(f'elapsed {elapsed}s < required {req["min_seconds"]}s')
    if cycles < req['min_cycles']:
        failures.append(f'cycles {cycles} < required {req["min_cycles"]}')

    base_menu_raw = Image.open(d / '002_initial_menu.png').convert('RGB')
    crop = active_crop(base_menu_raw)
    base_menu = base_menu_raw.crop(crop)
    base_battle = load_active(d / '001_initial_battle.png', crop)

    menu_diffs = []
    battle_diffs = []
    moved_diffs = []
    black_frames = 0
    field = (0, 0, 224, 192)

    for i in range(1, cycles + 1):
        tag = f'{i:03d}'
        bp = d / f'{tag}_battle.png'
        mp = d / f'{tag}_moved.png'
        up = d / f'{tag}_menu.png'
        for p in (bp, mp, up):
            if not p.exists(): failures.append(f'missing screenshot {p.name}')
        if not (bp.exists() and mp.exists() and up.exists()):
            continue
        b = load_active(bp, crop)
        m = load_active(mp, crop)
        u = load_active(up, crop)
        if max(sum(px) for px in b.getdata()) == 0 or max(sum(px) for px in m.getdata()) == 0 or max(sum(px) for px in u.getdata()) == 0:
            black_frames += 1
        bd = ratio(b, base_battle)
        md = ratio(m, b, field)
        ud = ratio(u, base_menu)
        battle_diffs.append(bd); moved_diffs.append(md); menu_diffs.append(ud)
        # Battle entry should reset to the same static camera/HUD state.
        if bd > 0.01:
            failures.append(f'cycle {i}: battle reset differs too much ({bd:.4f})')
        # Nine seconds of held movement from the fixed start must visibly move the battlefield.
        if md < 0.10:
            failures.append(f'cycle {i}: camera movement not visible ({md:.4f})')
        # Menu has accepted R2 ambient animation, so allow a small full-frame delta.
        if ud > 0.08:
            failures.append(f'cycle {i}: return screen not consistent with menu ({ud:.4f})')

    if black_frames:
        failures.append(f'{black_frames} black/corrupt active frames')

    rss = []
    with (d / 'cycles.csv').open(newline='') as f:
        for row in csv.DictReader(f):
            try: rss.append(int(row['rss_kb']))
            except Exception: pass
    rss_stats = {
        'first_kb': rss[0] if rss else None,
        'last_kb': rss[-1] if rss else None,
        'min_kb': min(rss) if rss else None,
        'max_kb': max(rss) if rss else None,
        'growth_kb': (rss[-1] - rss[0]) if len(rss) >= 2 else None,
    }

    report = {
        'region': summary.get('region'),
        'elapsed_seconds': elapsed,
        'cycles': cycles,
        'active_crop': list(crop),
        'screenshots_expected': 3 * cycles + 3,
        'menu_return_diff_max': max(menu_diffs) if menu_diffs else None,
        'battle_reset_diff_max': max(battle_diffs) if battle_diffs else None,
        'moved_field_diff_min': min(moved_diffs) if moved_diffs else None,
        'rss_diagnostic': rss_stats,
        'failures': failures,
        'status': 'PASS' if not failures else 'FAIL',
    }
    reports[case] = report
    all_failures.extend(f'{case}: {x}' for x in failures)

combined = {
    'test': 'R3 Stage 10 long real-emulator soak',
    'emulator': 'BlastEm 0.6.3.4 Ubuntu package',
    'rom_sha256_required': '94285501cd6cb72e909c31676a52c14da01f8e72b960e34636689768e13ed293',
    'cases': reports,
    'failures': all_failures,
    'status': 'PASS' if not all_failures else 'FAIL',
    'notes': [
        'Repeated MENU->BATTLE->MENU cycles repeatedly allocate/release the SGDK MAP and reload battle resources.',
        'BlastEm host RSS is diagnostic only; it is not treated as a direct measurement of Mega Drive game heap usage.',
        'Menu screenshot comparison allows accepted R2 ambient animation differences.'
    ]
}
(ROOT / 'R3_STAGE10_SOAK_REPORT.json').write_text(json.dumps(combined, indent=2) + '\n')
print(json.dumps(combined, indent=2))
raise SystemExit(1 if all_failures else 0)
