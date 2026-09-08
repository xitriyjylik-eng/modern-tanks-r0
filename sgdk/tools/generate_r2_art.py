from pathlib import Path
import base64

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "art"
RES = ROOT / "res"
RES.mkdir(parents=True, exist_ok=True)

# The locked project reference PNGs are never modified by the build. The
# approved Mega Drive adaptation is stored as deterministic text-safe payloads.
def decode_text_payload(parts, out_name):
    payload = "".join((ART / name).read_text(encoding="ascii") for name in parts)
    payload = "".join(payload.split())
    print("decode", out_name, "chars", len(payload), "parts", len(parts))
    data = base64.b64decode(payload, validate=True)
    (RES / out_name).write_bytes(data)

# Background is split only to keep GitHub connector text writes lossless.
decode_text_payload([
    "r2_menu_bg.png.b64.00",
    "r2_menu_bg.png.b64.01",
    "r2_menu_bg.png.b64.02",
    "r2_menu_bg.png.b64.03",
], "r2_menu_bg.png")

for i in range(4):
    decode_text_payload([f"r2_sel_{i}.png.b64"], f"r2_sel_{i}.png")

print("decoded reference-faithful R2 assets", RES)
