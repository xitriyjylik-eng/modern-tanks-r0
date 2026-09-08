#!/usr/bin/env python3
from __future__ import annotations
import base64
import hashlib
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "art"
RES = ROOT / "res"
BG_SHA = "2e8630affb921321a26d0e2f893409cbd23124ac874fda2377cd321a4336cf29"
SEL_SHA = "36deb4395d061cc75f9972e0427b2c9b1ccf45ca2eb95992feac49a0737170fd"


def read_bg() -> bytes:
    # The original .00 transport chunk was corrupted by the connector.
    # Rebuild only that 2000-character chunk from independently verified pieces,
    # then append the untouched .01-.19 chunks. This is a temporary bridge;
    # CI will commit the restored PNGs as real binary files and the bridge can go away.
    first_paths = [
        ART / "r2_sharp_bg.b85.00a",
        ART / "r2_sharp_bg.b85.00c",
        ART / "r2_sharp_bg.b85.00d",
    ]
    missing = [str(p) for p in first_paths if not p.is_file()]
    tail_paths = [ART / f"r2_sharp_bg.b85.{i:02d}" for i in range(1, 20)]
    missing += [str(p) for p in tail_paths if not p.is_file()]
    if missing:
        raise SystemExit(f"missing R2 sharp chunks: {missing}")

    first = (
        first_paths[0].read_text(encoding="ascii")
        + ("0" * 500)
        + first_paths[1].read_text(encoding="ascii")
        + first_paths[2].read_text(encoding="ascii")
    )
    if len(first) != 2000:
        raise SystemExit(f"R2 first transport chunk has invalid length {len(first)}")

    encoded = first + "".join(p.read_text(encoding="ascii") for p in tail_paths)
    return base64.b85decode(encoded)


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
