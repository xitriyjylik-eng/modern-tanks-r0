#!/usr/bin/env python3
from __future__ import annotations
import base64
import hashlib
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "art"
RES = ROOT / "res"
BG_SHA = "5ec08a6cb60201367bc45becdf116f3efe71597762f5f25d7aa28b62ff6426ea"
SEL_SHA = "36deb4395d061cc75f9972e0427b2c9b1ccf45ca2eb95992feac49a0737170fd"


def read_bg() -> bytes:
    parts = [ART / f"r2_exact_bg.b64.{i:02d}" for i in range(20)]
    missing = [str(p) for p in parts if not p.is_file()]
    if missing:
        raise SystemExit(f"missing R2 exact chunks: {missing}")
    encoded = "".join(p.read_text(encoding="ascii") for p in parts)
    return base64.b64decode(encoded, validate=True)


def read_selector() -> bytes:
    encoded = (ART / "r2_exact_selector.z85").read_text(encoding="ascii")
    return zlib.decompress(base64.b85decode(encoded))


def checked_write(name: str, data: bytes, expected: str) -> None:
    actual = hashlib.sha256(data).hexdigest()
    if actual != expected:
        raise SystemExit(f"{name}: SHA mismatch {actual} != {expected}")
    RES.mkdir(parents=True, exist_ok=True)
    (RES / name).write_bytes(data)
    print(f"restored {name}: {len(data)} bytes sha256={actual}")


def main() -> None:
    checked_write("r2_menu_bg.png", read_bg(), BG_SHA)
    checked_write("r2_selector.png", read_selector(), SEL_SHA)


if __name__ == "__main__":
    main()
