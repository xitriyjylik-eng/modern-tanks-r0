from pathlib import Path
import base64

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "art"
RES = ROOT / "res"
RES.mkdir(parents=True, exist_ok=True)

# R2 reference-faithful assets are prepared once from the project's locked
# MAIN_MENU_REFERENCE.png and TANKS_DETAILED_REFERENCE.png, then stored here
# as deterministic text-safe payloads for GitHub/CI. The locked references
# themselves are never modified by the build.
assets = {
    "r2_menu_bg.png": "r2_menu_bg.png.b64",
    "r2_sel_0.png": "r2_sel_0.png.b64",
    "r2_sel_1.png": "r2_sel_1.png.b64",
    "r2_sel_2.png": "r2_sel_2.png.b64",
    "r2_sel_3.png": "r2_sel_3.png.b64",
}

for out_name, src_name in assets.items():
    payload = (ART / src_name).read_text(encoding="ascii").strip()
    data = base64.b64decode(payload, validate=True)
    (RES / out_name).write_bytes(data)

print("decoded reference-faithful R2 assets", RES)
