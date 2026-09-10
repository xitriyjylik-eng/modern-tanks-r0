#!/usr/bin/env python3
"""Restore and verify the static, manually-authored R3 candidate in GitHub CI.
The payload files under sgdk/r3ci are lossless transport only; no random/procedural
terrain placement occurs here.
"""
from pathlib import Path
from PIL import Image
import base64, zlib, lzma, struct, hashlib, json, sys

ROOT = Path(__file__).resolve().parents[1]
RES, SRC, DATA, OUT = ROOT/'res', ROOT/'src', ROOT/'r3ci', ROOT/'out'
MAIN_SHA='0eb6593357d6b42c002ad9d0c457a156b3b5908048db118b1c227543fb641bcc'
RES_SHA='362551a132bc578a5732630a94bd17c8a72db47cf03790c2f574151eaa496b50'
WORLD_PIXEL_SHA='ca6722ef521a62af8936829308018698453ea6df7a5517c9b301cdc0dc141f00'
MAP_PIXEL_SHA='5536cb5234020e698a54d77823912673ae5d53ec52fcf80174044e5c84fe8d3f'
HUD_PIXEL_SHA='4a516cbc407142f95a064fcd2c3aa4e5eedf04cbbc2b7606cdbd34f52b8f59be'
PAL_SHA='b21fe2dc53ee77cefd085d08f3251cb64627a41f688602daf394f1915ddffc37'

def joined(prefix):
    return ''.join(p.read_text(encoding='ascii').strip() for p in sorted(DATA.glob(prefix+'.*.b64')))

def decode_tile_payload(raw):
    assert raw[:4] == b'R3T1'
    w,h,n,iw = struct.unpack('<HHHB', raw[4:11]); p=11
    tiles=[raw[p+i*64:p+(i+1)*64] for i in range(n)]; p += n*64
    count=(w//8)*(h//8)
    if iw == 1: ids=list(raw[p:p+count])
    else: ids=[struct.unpack_from('<H',raw,p+i*2)[0] for i in range(count)]
    pixels=bytearray(w*h); k=0
    for ty in range(0,h,8):
        for tx in range(0,w,8):
            tile=tiles[ids[k]]; k+=1
            for y in range(8): pixels[(ty+y)*w+tx:(ty+y)*w+tx+8]=tile[y*8:y*8+8]
    return w,h,bytes(pixels)

def psha(im): return hashlib.sha256(im.tobytes()).hexdigest()
def image_p(size,pixels,palette):
    im=Image.frombytes('P',size,pixels); im.putpalette(palette); return im

def restore():
    main=zlib.decompress(base64.b64decode(joined('main')))
    rr=zlib.decompress(base64.b64decode((DATA/'resources.b64').read_text().strip()))
    assert hashlib.sha256(main).hexdigest()==MAIN_SHA
    assert hashlib.sha256(rr).hexdigest()==RES_SHA
    (SRC/'main.c').write_bytes(main); (RES/'resources.res').write_bytes(rr)

    menu=Image.open(RES/'r2_menu_bg.png'); menu.load(); pal=menu.getpalette()
    assert hashlib.sha256(bytes(pal)).hexdigest()==PAL_SHA
    world_raw=lzma.decompress(base64.b64decode(joined('world')))
    w,h,pix=decode_tile_payload(world_raw); assert (w,h)==(1024,768)
    playable=image_p((w,h),pix,pal); assert psha(playable)==WORLD_PIXEL_SHA
    playable.save(RES/'r3_region1_playable.png')

    runtime=Image.new('P',(1024,1024)); runtime.putpalette(pal)
    runtime.paste(playable,(0,0)); runtime.paste(playable.crop((0,512,1024,768)),(0,768))
    assert psha(runtime)==MAP_PIXEL_SHA; runtime.save(RES/'r3_region1_map.png')

    hud_raw=zlib.decompress(base64.b64decode((DATA/'hud.b64').read_text().strip()))
    hw,hh,hpix=decode_tile_payload(hud_raw); assert (hw,hh)==(320,224)
    hud=image_p((hw,hh),hpix,pal); assert psha(hud)==HUD_PIXEL_SHA
    hud.save(RES/'r3_battle_hud.png')
    print('R3 CI overlay restored from static authored payload')

def unique_tiles(im):
    return {im.crop((x,y,x+8,y+8)).tobytes() for y in range(0,im.height,8) for x in range(0,im.width,8)}

def verify():
    menu=Image.open(RES/'r2_menu_bg.png'); menu.load()
    play=Image.open(RES/'r3_region1_playable.png'); play.load()
    world=Image.open(RES/'r3_region1_map.png'); world.load()
    hud=Image.open(RES/'r3_battle_hud.png'); hud.load()
    assert play.size==(1024,768) and world.size==(1024,1024) and hud.size==(320,224)
    assert psha(play)==WORLD_PIXEL_SHA and psha(world)==MAP_PIXEL_SHA and psha(hud)==HUD_PIXEL_SHA
    assert world.crop((0,0,1024,768)).tobytes()==play.tobytes()
    assert world.getpalette()==play.getpalette()==hud.getpalette()==menu.getpalette()

    for im,name in ((world,'world'),(hud,'hud')):
        for ty in range(0,im.height,8):
            for tx in range(0,im.width,8):
                nibbles={im.getpixel((tx+x,ty+y))>>4 for y in range(8) for x in range(8)}
                assert len(nibbles)==1,(name,tx//8,ty//8)

    menu_tiles=set()
    for y in range(0,menu.height,8):
        for x in range(0,menu.width,8):
            if not (72<=x<240 and y<168): menu_tiles.add(menu.crop((x,y,x+8,y+8)).tobytes())
    total=shared=0
    for y in range(0,768,8):
        for x in range(0,1024,8):
            total += 1; shared += play.crop((x,y,x+8,y+8)).tobytes() in menu_tiles
    share=shared/total
    assert share>=0.95 and abs(share-0.982585)<0.000001

    src=(SRC/'main.c').read_text(encoding='utf-8'); rr=(RES/'resources.res').read_text(encoding='utf-8')
    for t in ('MAP_create(&r3_region1_map','MAP_scrollTo(battleMap','MAP_release(battleMap)',
              'R3_CAMERA_ACCEL_FP','R3_CAMERA_FRICTION_FP','R3_CAMERA_MAX_SPEED_FP',
              'camera_scale_for_video','update_battle_camera_frame','R3_VIEW_WIDTH_PX 224',
              'R3_VIEW_HEIGHT_PX 192','PAL_setPaletteColors(0, r2_menu_bg.palette, CPU)',
              'R3_HUD_FONT_COUNT 96','r3HudOpaqueFont','VDP_loadTileData(r3HudOpaqueFont',
              'r3_draw_hud_text("REGION 1"','r3_draw_hud_text(buffer, 31, 4)'):
        assert t in src,t
    assert 'VDP_drawText("REGION 1"' not in src
    assert 'VDP_drawText("R3 WORLD STREAM / CAMERA"' not in src
    for t in ('TILESET r3_region1_tileset "r3_region1_map.png" NONE ALL',
              'MAP r3_region1_map "r3_region1_map.png" r3_region1_tileset NONE',
              'IMAGE r3_battle_hud "r3_battle_hud.png" NONE ALL'):
        assert t in rr,t

    OUT.mkdir(exist_ok=True)
    report={'source_main_sha256':MAIN_SHA,'source_resources_sha256':RES_SHA,
            'resource_size':[1024,1024],'playable_size':[1024,768],'hud_size':[320,224],
            'map_unique_8x8_raw_playable':len(unique_tiles(play)),'hud_unique_8x8_raw':len(unique_tiles(hud)),
            'exact_accepted_landscape_tile_occurrences':shared,'playable_tile_occurrences':total,
            'exact_accepted_landscape_tile_occurrence_share':share,'playable_pixel_sha256':psha(play),
            'map_pixel_sha256':psha(world),'hud_pixel_sha256':psha(hud),
            'layout':'static manually authored Region 1','runtime_procedural_generation':False,
            'serialization':'lossless static CI transport only','battle_hud_text':'opaque SGDK 2.11 glyph mask on PAL0 index 7 background'}
    (OUT/'R3_STATIC_MAP_REPORT.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('R3 verification PASS'); print(f'R2 landscape tile share={share:.3%}')

def main():
    if len(sys.argv)!=2 or sys.argv[1] not in ('restore','verify'):
        raise SystemExit('usage: r3_ci_overlay_small.py restore|verify')
    restore() if sys.argv[1]=='restore' else verify()
if __name__=='__main__': main()
