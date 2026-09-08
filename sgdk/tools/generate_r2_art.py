from pathlib import Path
import base64
import hashlib
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "art"
RES = ROOT / "res"
RES.mkdir(parents=True, exist_ok=True)

EXPECTED_BG_SHA256 = "3228dc767cfb2790fa5f60753f17ae5fa826a0eed41719340d4a93a1fffebae6"


def decode_text_payload(parts, out_name):
    payload = "".join((ART / name).read_text(encoding="ascii") for name in parts)
    payload = "".join(payload.split())
    print("decode", out_name, "chars", len(payload), "parts", len(parts))
    data = base64.b64decode(payload, validate=True)
    out = RES / out_name
    out.write_bytes(data)
    return out


bg_path = decode_text_payload([
    "r2_menu_bg.png.b64.000p0",
    "r2_menu_bg.png.b64.000p1",
    "r2_menu_bg.png.b64.000p2",
    "r2_menu_bg.png.b64.000p3",
    "r2_menu_bg.png.b64.000b2",
    "r2_menu_bg.png.b64.000c",
    "r2_menu_bg.png.b64.001",
    "r2_menu_bg.png.b64.01",
    "r2_menu_bg.png.b64.02",
    "r2_menu_bg.png.b64.03",
], "r2_menu_bg.png")

actual = hashlib.sha256(bg_path.read_bytes()).hexdigest()
if actual != EXPECTED_BG_SHA256:
    raise SystemExit(f"R2 background SHA mismatch: {actual}")

bg = Image.open(bg_path)
bg.load()
if bg.mode != "P" or bg.size != (320, 224):
    raise SystemExit(f"R2 background format mismatch: {bg.mode} {bg.size}")

palette = bg.getpalette()
target = (251, 224, 73)
yellow = min(
    range(256),
    key=lambda i: sum((palette[i * 3 + c] - target[c]) ** 2 for c in range(3)),
)
for i, y in enumerate((80, 96, 112, 128)):
    sel = bg.crop((112, y, 216, y + 16))
    sel.putpalette(palette)
    d = ImageDraw.Draw(sel)
    d.rectangle((0, 0, 103, 15), outline=yellow, width=1)
    d.polygon([(1, 7), (5, 3), (5, 11)], fill=yellow)
    d.polygon([(102, 7), (98, 3), (98, 11)], fill=yellow)
    sel.save(RES / f"r2_sel_{i}.png", optimize=False)

print("reference-faithful R2 assets ready", RES)
