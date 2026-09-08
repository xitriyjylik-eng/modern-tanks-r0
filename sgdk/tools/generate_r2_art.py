from pathlib import Path
import base64
import hashlib

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "art"
OUT = ROOT / "res"
OUT.mkdir(parents=True, exist_ok=True)

ASSETS = {
    "r2_menu_bg.png": "927534f927eaf17cd939a4977f20adbd8a705ca405f4c1a37511bd2a593376d0",
    "r2_sel_0.png": "aff874e5ed4bbb10891ca6de050b7732e803466e09da63e257bc75ef11df17ae",
    "r2_sel_1.png": "8a1a6d595f41a6c030cf504e3be94ee9672a51ed367e510bfb362a3997d78e75",
    "r2_sel_2.png": "9dfc4a52da30efe9982e6c6d9f07505895f90e6aa0875d16d73d01288ff23bdb",
    "r2_sel_3.png": "7e23c26e84400d28452f7c674ca226a023a3db02fc6448e3f6bac5e19d8f53f4",
    "r2_anim_tank.png": "8a2b0700f17a8e7e7c0fba441574da4f5f1a870edfad8afd24b1ec90ca38e055",
}

for name, expected in ASSETS.items():
    if name == "r2_menu_bg.png":
        encoded = "".join((SRC / f"{name}.b64.{i:02d}").read_text(encoding="ascii").strip() for i in range(4))
    else:
        encoded = (SRC / f"{name}.b64").read_text(encoding="ascii").strip()
    data = base64.b64decode(encoded, validate=True)
    actual = hashlib.sha256(data).hexdigest()
    if actual != expected:
        raise SystemExit(f"R2 asset hash mismatch: {name}: {actual} != {expected}")
    (OUT / name).write_bytes(data)
    print(f"R2 asset OK: {name} {actual}")
