#!/usr/bin/env python3
from pathlib import Path
from PIL import Image
import hashlib,json
root=Path(__file__).resolve().parents[1]
res=root/'res'
for name,size,count in [('r3_world_tiles.png',(128,64),128),('r3_hud_tiles.png',(64,64),64)]:
    im=Image.open(res/name); im.load()
    assert im.mode=='P' and im.size==size,(name,im.mode,im.size)
    assert max(im.getdata())<=15,(name,max(im.getdata()))
    assert (im.width//8)*(im.height//8)==count
r2=Image.open(res/'r2_menu_bg.png'); r2.load()
w=Image.open(res/'r3_world_tiles.png'); w.load()
h=Image.open(res/'r3_hud_tiles.png'); h.load()
assert w.getpalette()==r2.getpalette(), 'R3 world palette metadata must exactly match accepted R2 palette'
assert h.getpalette()==r2.getpalette(), 'R3 HUD palette metadata must exactly match accepted R2 palette'
report=json.loads((res/'R3_ASSET_REPORT.json').read_text())
assert report['tree_frames']==12 and report['water_frames']==8
print('R3 asset verification PASS')
print(json.dumps(report,indent=2))
