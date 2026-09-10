#!/usr/bin/env python3
import csv
import json
import statistics
from pathlib import Path
from PIL import Image
import numpy as np

ROOT = Path('sgdk/out/camera_deep')
MAP_PATH = Path('sgdk/res/r3_region1_map.png')
PLAY_W, PLAY_H = 1024, 768
VIEW_W, VIEW_H = 224, 192
MAX_X, MAX_Y = PLAY_W - VIEW_W, PLAY_H - VIEW_H
LEVELS = np.array([0, 49, 87, 119, 146, 174, 206, 255], dtype=np.uint8)

src = np.array(Image.open(MAP_PATH).convert('RGB'), dtype=np.uint8)
map_rgb = LEVELS[src // 32]


def active_crop(menu):
    if menu.size == (320, 224):
        return (0, 0, 320, 224)
    a = np.array(menu.convert('RGB'))
    mask = np.any(a != 0, axis=2)
    ys, xs = np.where(mask)
    if not len(xs):
        raise ValueError('menu screenshot is black')
    box = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
    if (box[2]-box[0], box[3]-box[1]) != (320,224):
        raise ValueError(f'active frame is not 320x224: raw={menu.size}, bbox={box}')
    return box


def locate_field(field):
    probes = (96, 64, 128, 32, 160)
    for probe in probes:
        needle = field[probe].tobytes()
        for my in range(probe, min(PLAY_H, MAX_Y + probe + 1)):
            row = map_rgb[my].tobytes()
            pos = row.find(needle)
            while pos != -1:
                if pos % 3 == 0:
                    x = pos // 3
                    y = my - probe
                    if 0 <= x <= MAX_X and 0 <= y <= MAX_Y:
                        if np.array_equal(map_rgb[y:y+VIEW_H, x:x+VIEW_W], field):
                            return (x, y)
                pos = row.find(needle, pos + 1)
    return None


def load_trace(path):
    out = {}
    with path.open(newline='') as f:
        for row in csv.DictReader(f):
            out[row['label']] = int(row['epoch_ms'])
    return out


def analyze_region(name):
    d = ROOT / name
    raw = {p.stem: Image.open(p).convert('RGB') for p in d.glob('*.png') if not p.stem.endswith('_active')}
    if '00_menu' not in raw:
        raise ValueError(f'{name}: missing 00_menu')
    crop = active_crop(raw['00_menu'])
    trace = load_trace(d/'trace.csv')
    positions = {}
    unresolved = []
    for label, image in sorted(raw.items()):
        active = image.crop(crop)
        active.save(d/f'{label}_active.png')
        if label == '00_menu':
            continue
        field = np.array(active, dtype=np.uint8)[:VIEW_H,:VIEW_W]
        found = locate_field(field)
        if found is None:
            unresolved.append(label)
        else:
            positions[label] = list(found)

    failures = []
    warnings = []
    if unresolved:
        failures.append(f'unresolved exact map positions: {unresolved}')

    def pos(label):
        if label not in positions:
            raise KeyError(label)
        return positions[label]
    def same(a,b):
        return pos(a) == pos(b)
    def require(cond, text):
        if not cond:
            failures.append(text)

    if '01_start' in positions:
        require(pos('01_start') == [320,224], f"start scroll {pos('01_start')} != [320,224]")

    right_labels = [f'10_right_{i:02d}' for i in range(1,9)]
    if all(x in positions for x in right_labels) and '01_start' in positions:
        seq = [pos('01_start')] + [pos(x) for x in right_labels]
        require(all(seq[i+1][0] > seq[i][0] for i in range(len(seq)-1)), f'RIGHT samples not strictly increasing: {seq}')
        require(all(p[1] == 224 for p in seq), f'RIGHT changed Y: {seq}')
        speeds=[]
        for a,b in zip(right_labels[-4:-1], right_labels[-3:]):
            dt=(trace[b]-trace[a])/1000.0
            if dt>0:
                speeds.append((pos(b)[0]-pos(a)[0])/dt)
        steady_speed = statistics.median(speeds) if speeds else 0.0
        first_dt=(trace[right_labels[1]]-trace[right_labels[0]])/1000.0
        first_speed=(pos(right_labels[1])[0]-pos(right_labels[0])[0])/first_dt if first_dt>0 else 0.0
        require(65.0 <= steady_speed <= 115.0, f'steady RIGHT speed out of range: {steady_speed:.2f}px/s')
        require(first_speed < steady_speed, f'no visible acceleration: first={first_speed:.2f}, steady={steady_speed:.2f}')
    else:
        steady_speed=0.0
        first_speed=0.0

    rel = ['11_release_00','11_release_01','11_release_02','11_release_03','11_settle_a','11_settle_b']
    if all(x in positions for x in rel) and right_labels[-1] in positions:
        rseq=[pos(right_labels[-1])]+[pos(x) for x in rel]
        require(all(rseq[i+1][0] >= rseq[i][0] for i in range(len(rseq)-1)), f'RIGHT release reversed/stuck: {rseq}')
        require(all(p[1] == rseq[0][1] for p in rseq), f'RIGHT release changed Y: {rseq}')
        require(same('11_settle_a','11_settle_b'), f'camera did not settle after RIGHT release: {pos("11_settle_a")} vs {pos("11_settle_b")}')
        coast=pos('11_settle_a')[0]-pos(right_labels[-1])[0]
        require(0 <= coast <= 40, f'RIGHT coast distance suspicious: {coast}px')
    else:
        coast=None

    edge_checks = [
        ('21_right_edge_a','21_right_edge_b',0,MAX_X,'RIGHT'),
        ('31_left_edge_a','31_left_edge_b',0,0,'LEFT'),
        ('41_bottom_edge_a','41_bottom_edge_b',1,MAX_Y,'DOWN'),
        ('51_top_edge_a','51_top_edge_b',1,0,'UP'),
    ]
    for a,b,axis,want,direction in edge_checks:
        if a in positions and b in positions:
            require(pos(a)[axis] == want, f'{direction} edge {pos(a)} has axis={pos(a)[axis]}, expected {want}')
            require(same(a,b), f'{direction} wrapped/moved while held at edge: {pos(a)} -> {pos(b)}')

    if '21_right_edge_b' in positions and '30_left_mid' in positions:
        require(pos('30_left_mid')[0] < pos('21_right_edge_b')[0], 'LEFT did not reduce X')
    if '31_left_edge_b' in positions and '40_down_mid' in positions:
        require(pos('40_down_mid')[1] > pos('31_left_edge_b')[1], 'DOWN did not increase Y')
    if '41_bottom_edge_b' in positions and '50_up_mid' in positions:
        require(pos('50_up_mid')[1] < pos('41_bottom_edge_b')[1], 'UP did not reduce Y')

    diag = [f'60_diag_dr_{i:02d}' for i in range(1,6)]
    if all(x in positions for x in diag) and '51_top_edge_b' in positions:
        dseq=[pos('51_top_edge_b')]+[pos(x) for x in diag]
        require(all(dseq[i+1][0] > dseq[i][0] and dseq[i+1][1] > dseq[i][1] for i in range(len(dseq)-1)), f'DOWN+RIGHT diagonal is not monotonic: {dseq}')
        require(all(abs(p[0]-p[1]) <= 2 for p in dseq), f'diagonal axes diverge: {dseq}')

    drel=['61_diag_release_00','61_diag_release_01','61_diag_release_02','61_diag_settle_a','61_diag_settle_b']
    if all(x in positions for x in drel):
        require(same('61_diag_settle_a','61_diag_settle_b'), f'diagonal release did not settle: {pos("61_diag_settle_a")} vs {pos("61_diag_settle_b")}')
    if '70_diag_ul_edge_a' in positions and '70_diag_ul_edge_b' in positions:
        require(pos('70_diag_ul_edge_a') == [0,0], f'UP+LEFT did not reach top-left: {pos("70_diag_ul_edge_a")}')
        require(same('70_diag_ul_edge_a','70_diag_ul_edge_b'), 'UP+LEFT edge not stable')
    if '71_final_settle' in positions:
        require(pos('71_final_settle') == [0,0], f'final settle not at top-left: {pos("71_final_settle")}')

    report={
        'region':name,
        'raw_size':list(raw['00_menu'].size),
        'active_crop':list(crop),
        'positions':positions,
        'unresolved':unresolved,
        'steady_right_speed_px_s':steady_speed,
        'first_right_speed_px_s':first_speed,
        'right_coast_px':coast,
        'status':'PASS' if not failures else 'FAIL',
        'failures':failures,
        'warnings':warnings,
    }
    (d/'R3_CAMERA_DEEP_REPORT.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

reports={name:analyze_region(name) for name in ('ntsc','pal')}
failures=[]
for name,r in reports.items():
    failures.extend([f'{name}: {x}' for x in r['failures']])
ns=reports['ntsc']['steady_right_speed_px_s']
ps=reports['pal']['steady_right_speed_px_s']
if ns and ps:
    ratio=ps/ns
    if not 0.85 <= ratio <= 1.15:
        failures.append(f'PAL/NTSC steady speed ratio {ratio:.3f} outside 0.85..1.15')
else:
    ratio=None
combined={
    'status':'PASS' if not failures else 'FAIL',
    'regions':{k:{'status':v['status'],'steady_right_speed_px_s':v['steady_right_speed_px_s'],'right_coast_px':v['right_coast_px']} for k,v in reports.items()},
    'pal_to_ntsc_speed_ratio':ratio,
    'failures':failures,
}
(ROOT/'R3_CAMERA_DEEP_COMBINED_REPORT.json').write_text(json.dumps(combined,indent=2)+'\n')
print(json.dumps(combined,indent=2))
raise SystemExit(1 if failures else 0)
