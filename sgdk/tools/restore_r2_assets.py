#!/usr/bin/env python3
"""Restore the exact approved R2 native indexed assets.

The binary PNGs are source-controlled as small lossless Base64 chunks because the
chat GitHub transport can truncate larger binary/text payloads. This script does
no image generation or transformation: it only concatenates and decodes the
already-approved, already-quantized bytes and verifies their SHA-256 hashes.
"""
from __future__ import annotations

import base64
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "art"
RES = ROOT / "res"

EXPECTED = {
    "r2_menu_bg.png": "acf9bcd28e0d9d30d7bb205404ad97a0252e15e76db8039a251ed73526eb2e61",
    "r2_selector.png": "9da097c4fe2af98452d3787f91fd879aab9b468d5daf56a90f1b2d2bc617663f",
}


def restore_bg() -> bytes:
    parts = sorted(ART.glob("r2_final_bg.b64.*"))
    if len(parts) != 14:
        raise SystemExit(f"expected 14 R2 background chunks, found {len(parts)}")
    encoded = "".join(p.read_text(encoding="ascii").strip() for p in parts)
    return base64.b64decode(encoded, validate=True)


def restore_selector() -> bytes:
    encoded = (ART / "r2_final_selector.b64").read_text(encoding="ascii").strip()
    return base64.b64decode(encoded, validate=True)


def write_checked(name: str, data: bytes) -> None:
    sha = hashlib.sha256(data).hexdigest()
    if sha != EXPECTED[name]:
        raise SystemExit(f"{name}: restored SHA mismatch {sha} != {EXPECTED[name]}")
    path = RES / name
    path.write_bytes(data)
    print(f"restored {path.relative_to(ROOT)} {len(data)} bytes sha256={sha}")


def main() -> None:
    RES.mkdir(parents=True, exist_ok=True)
    write_checked("r2_menu_bg.png", restore_bg())
    write_checked("r2_selector.png", restore_selector())


if __name__ == "__main__":
    main()
