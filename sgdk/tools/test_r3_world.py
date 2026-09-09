#!/usr/bin/env python3
"""Host-side R3 streaming model. 36,000 ticks = 10 min at 60 logic Hz."""
from pathlib import Path
import json, hashlib

WORLD_PX=8192; VIEW_W=224; VIEW_H=192; PLANE_W=64; PLANE_H=32; PREF_L=18; PREF_T=4
TICKS=36000

cx=cy=WORLD_PX//2
origin_x=((cx-VIEW_W//2)>>3)-PREF_L
origin_y=((cy-VIEW_H//2)>>3)-PREF_T
slots={}

def slot(wx,wy): return (wx&63,wy&31)
def load_cell(wx,wy): slots[slot(wx,wy)]=(wx,wy)
def fill():
    for y in range(origin_y,origin_y+PLANE_H):
        for x in range(origin_x,origin_x+PLANE_W): load_cell(x,y)
fill()

cross_x=cross_y=0
bounces=0
vx=4; vy=3
minx=VIEW_W//2; maxx=WORLD_PX-VIEW_W//2
miny=VIEW_H//2; maxy=WORLD_PX-VIEW_H//2
for tick in range(TICKS):
    cx += vx; cy += vy
    if cx<minx or cx>maxx:
        cx=max(minx,min(maxx,cx)); vx=-vx; bounces+=1
    if cy<miny or cy>maxy:
        cy=max(miny,min(maxy,cy)); vy=-vy; bounces+=1
    camx=(cx-VIEW_W//2)>>3; camy=(cy-VIEW_H//2)>>3
    target_x=camx-PREF_L; target_y=camy-PREF_T
    while origin_x<target_x:
        origin_x+=1; cross_x+=1
        wx=origin_x+PLANE_W-1
        for y in range(origin_y,origin_y+PLANE_H): load_cell(wx,y)
    while origin_x>target_x:
        origin_x-=1; cross_x+=1
        for y in range(origin_y,origin_y+PLANE_H): load_cell(origin_x,y)
    while origin_y<target_y:
        origin_y+=1; cross_y+=1
        wy=origin_y+PLANE_H-1
        for x in range(origin_x,origin_x+PLANE_W): load_cell(x,wy)
    while origin_y>target_y:
        origin_y-=1; cross_y+=1
        for x in range(origin_x,origin_x+PLANE_W): load_cell(x,origin_y)

    # Check every visible tile plus a 1-tile guard at representative intervals.
    if tick%47==0:
        for y in range(camy-1,camy+25):
            for x in range(camx-1,camx+29):
                assert slots[slot(x,y)]==(x,y),(tick,x,y,slots.get(slot(x,y)))
        assert minx<=cx<=maxx and miny<=cy<=maxy

report={'ticks':TICKS,'nominal_minutes':10,'ring':'64x32','world_px':'8192x8192','column_stream_events':cross_x,'row_stream_events':cross_y,'edge_bounces':bounces,'status':'PASS'}
out=Path(__file__).resolve().parents[1]/'out'
out.mkdir(exist_ok=True)
(out/'R3_STREAM_STRESS.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
