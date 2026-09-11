#!/usr/bin/env python3
"""Convert approved Map 01 art into native Mega Drive streamed tiles.

This is a deterministic hardware conversion step only. It does not generate,
redesign or procedurally alter the map. Every 8x8 source tile is matched to the
best of four fixed 15-colour Mega Drive palettes and packed as 4bpp tile data.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

import numpy as np
from PIL import Image

PALETTES = np.array([
    [[0,0,0],[0,36,0],[36,36,0],[36,36,36],[73,36,36],[73,73,0],[73,73,36],[109,73,36],[109,109,36],[109,109,73],[146,109,36],[146,109,73],[146,146,73],[182,146,73],[182,146,109]],
    [[0,0,0],[0,36,0],[0,36,36],[36,36,0],[36,36,36],[36,73,0],[36,73,36],[73,73,0],[73,73,36],[73,109,0],[73,109,36],[109,109,36],[109,146,36],[109,146,73],[146,146,73]],
    [[0,0,0],[0,0,36],[0,36,0],[0,36,36],[36,36,0],[36,36,36],[36,36,73],[0,73,109],[36,73,36],[73,73,36],[73,73,109],[73,109,146],[109,109,73],[146,146,73],[109,146,182]],
    [[0,36,36],[0,36,73],[0,36,109],[0,73,109],[0,73,146],[36,73,73],[36,73,109],[36,73,146],[36,109,146],[36,109,182],[73,109,146],[109,109,73],[73,146,182],[109,146,182],[182,219,219]],
], dtype=np.uint8)

WORLD_W = 1536
WORLD_H = 1152
TILE = 8
WORLD_TILES_X = WORLD_W // TILE
WORLD_TILES_Y = WORLD_H // TILE


def vdp_word(rgb: np.ndarray) -> int:
    r, g, b = [int(x) for x in rgb]
    rr = round(r * 7 / 255) & 7
    gg = round(g * 7 / 255) & 7
    bb = round(b * 7 / 255) & 7
    return (bb << 9) | (gg << 5) | (rr << 1)


def quantize_tiles(tiles: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    n = len(tiles)
    assignment = np.empty(n, dtype=np.uint8)
    indices = np.empty((n, 64), dtype=np.uint8)

    for start in range(0, n, 512):
        block = tiles[start:start + 512].astype(np.int32)
        errors = np.empty((len(block), 4), dtype=np.int64)
        per_palette_indices = []
        for p in range(4):
            pal = PALETTES[p].astype(np.int32)
            dist = ((block[:, :, None, :] - pal[None, None, :, :]) ** 2).sum(axis=3)
            q = dist.argmin(axis=2)
            per_palette_indices.append(q)
            errors[:, p] = dist.min(axis=2).sum(axis=1)
        best = errors.argmin(axis=1)
        assignment[start:start + len(block)] = best.astype(np.uint8)
        for local in range(len(block)):
            indices[start + local] = per_palette_indices[int(best[local])][local].astype(np.uint8) + 1

    return assignment, indices


def pack_tiles(indices: np.ndarray) -> bytes:
    out = bytearray()
    for tile in indices:
        for y in range(8):
            row = tile[y * 8:(y + 1) * 8]
            for x in range(0, 8, 2):
                out.append((int(row[x]) << 4) | int(row[x + 1]))
    return bytes(out)


def build_preview(tiles: np.ndarray, assignment: np.ndarray, indices: np.ndarray) -> Image.Image:
    qtiles = np.empty_like(tiles)
    for p in range(4):
        ids = np.where(assignment == p)[0]
        qtiles[ids] = PALETTES[p][indices[ids] - 1]
    pixels = qtiles.reshape(WORLD_TILES_Y, WORLD_TILES_X, 8, 8, 3).transpose(0, 2, 1, 3, 4).reshape(WORLD_H, WORLD_W, 3)
    return Image.fromarray(pixels, mode="RGB")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("source", type=Path)
    ap.add_argument("output_dir", type=Path)
    ap.add_argument("--preview", action="store_true")
    args = ap.parse_args()

    image = Image.open(args.source).convert("RGB")
    if image.size != (WORLD_W, WORLD_H):
        raise SystemExit(f"Expected {WORLD_W}x{WORLD_H}, got {image.size[0]}x{image.size[1]}")

    pixels = np.asarray(image, dtype=np.uint8)
    tiles = pixels.reshape(WORLD_TILES_Y, 8, WORLD_TILES_X, 8, 3).transpose(0, 2, 1, 3, 4).reshape(-1, 64, 3)
    assignment, indices = quantize_tiles(tiles)

    tile_data = pack_tiles(indices)
    palette_selectors = assignment.tobytes()

    words = []
    for p in range(4):
        words.append(0)
        words.extend(vdp_word(c) for c in PALETTES[p])
    palette_data = b"".join(struct.pack(">H", w) for w in words)

    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    files = {
        "map01_world_tiles.bin": tile_data,
        "map01_world_tile_palettes.bin": palette_selectors,
        "map01_world_palette.bin": palette_data,
    }
    for name, data in files.items():
        (out / name).write_bytes(data)

    meta = {
        "source": str(args.source),
        "world_px": [WORLD_W, WORLD_H],
        "tile_px": 8,
        "world_tiles": [WORLD_TILES_X, WORLD_TILES_Y],
        "tile_count": WORLD_TILES_X * WORLD_TILES_Y,
        "palette_model": "4 fixed palettes x 15 opaque colours + transparent index 0",
        "sha256": {name: hashlib.sha256(data).hexdigest() for name, data in files.items()},
    }
    (out / "map01_world_stream_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    if args.preview:
        build_preview(tiles, assignment, indices).save(out / "map01_world_genesis_preview.png")

    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
