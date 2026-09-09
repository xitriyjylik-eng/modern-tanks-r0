#!/usr/bin/env python3
from pathlib import Path
import argparse
import base64
import gzip
import hashlib

ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'


def decode_gzip(s: str):
    padded = s + ('=' * (-len(s) % 4))
    try:
        raw = base64.b64decode(padded, validate=True)
        data = gzip.decompress(raw)
        return raw, data
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='/tmp/R3_IMPLEMENTATION.patch')
    args = ap.parse_args()

    parts = sorted(Path('r3').glob('R3_IMPLEMENTATION.patch.gz.b64.part[0-9][0-9]'))
    if len(parts) != 4:
        raise SystemExit(f'expected 4 transport parts, got: {[str(p) for p in parts]}')

    raw_parts = [p.read_text(encoding='ascii') for p in parts]
    clean_parts = [''.join(ch for ch in text if ch in ALPHABET + '=') for text in raw_parts]
    clean = ''.join(clean_parts).rstrip('=')

    print('parts:', [(p.name, len(c)) for p, c in zip(parts, clean_parts)])
    print('data chars:', len(clean), 'mod4=', len(clean) % 4)

    result = decode_gzip(clean)
    repair = 'none'

    # A mod-4 length of 1 most commonly means one extra base64 character.
    # Try deleting exactly one character. gzip.decompress validates the gzip
    # trailer/CRC, so a false repair is extraordinarily unlikely.
    if result is None:
        for i in range(len(clean)):
            candidate = clean[:i] + clean[i + 1:]
            result = decode_gzip(candidate)
            if result is not None:
                repair = f'delete index {i} char {clean[i]!r}'
                clean = candidate
                break

    # If the transport instead dropped one character, first try the four
    # chunk boundaries where manual splitting could have caused the loss.
    if result is None:
        boundaries = []
        pos = 0
        for chunk in clean_parts[:-1]:
            pos += len(chunk.rstrip('='))
            boundaries.append(pos)
        for pos in boundaries:
            for ch in ALPHABET:
                candidate = clean[:pos] + ch + clean[pos:]
                result = decode_gzip(candidate)
                if result is not None:
                    repair = f'insert {ch!r} at boundary {pos}'
                    clean = candidate
                    break
            if result is not None:
                break

    if result is None:
        raise SystemExit('unable to recover a CRC-valid gzip stream with one-character transport repair')

    compressed, patch = result
    out = Path(args.out)
    out.write_bytes(patch)
    Path('sgdk/out').mkdir(parents=True, exist_ok=True)
    report = Path('sgdk/out/R3_PATCH_RECOVERY.txt')
    report.write_text(
        '\n'.join([
            f'repair={repair}',
            f'base64_chars={len(clean)}',
            f'gzip_bytes={len(compressed)}',
            f'gzip_sha256={hashlib.sha256(compressed).hexdigest()}',
            f'patch_bytes={len(patch)}',
            f'patch_sha256={hashlib.sha256(patch).hexdigest()}',
            '',
        ]),
        encoding='utf-8',
    )
    print(report.read_text(encoding='utf-8'))


if __name__ == '__main__':
    main()
