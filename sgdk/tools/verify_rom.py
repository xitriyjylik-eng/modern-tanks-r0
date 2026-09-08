#!/usr/bin/env python3
import hashlib, json, struct, sys
from pathlib import Path

p = Path(sys.argv[1] if len(sys.argv) > 1 else "out/rom.bin")
data = p.read_bytes()

def be16(off): return struct.unpack_from(">H", data, off)[0]
def be32(off): return struct.unpack_from(">I", data, off)[0]

errors = []
if len(data) < 0x200:
    errors.append("ROM shorter than 0x200 bytes")

initial_sp = be32(0) if len(data) >= 8 else 0
reset_pc = be32(4) if len(data) >= 8 else 0
console = data[0x100:0x110].decode("ascii", errors="replace") if len(data) >= 0x110 else ""
header_checksum = be16(0x18E) if len(data) >= 0x190 else 0

checksum = 0
if len(data) >= 0x200:
    body = data[0x200:]
    if len(body) & 1:
        body += b"\0"
    checksum = sum(struct.unpack(">" + "H" * (len(body)//2), body)) & 0xFFFF

if not (0xFF0000 <= initial_sp <= 0xFFFFFF):
    errors.append(f"initial SP outside 68K RAM: 0x{initial_sp:08X}")
if not (0x000200 <= reset_pc < len(data)):
    errors.append(f"reset PC outside ROM payload: 0x{reset_pc:08X}")
if "SEGA" not in console:
    errors.append(f"SEGA signature missing at 0x100: {console!r}")
if header_checksum != checksum:
    errors.append(f"checksum mismatch header=0x{header_checksum:04X} calc=0x{checksum:04X}")

report = {
    "file": str(p),
    "size": len(data),
    "sha256": hashlib.sha256(data).hexdigest(),
    "initial_sp": f"0x{initial_sp:08X}",
    "reset_pc": f"0x{reset_pc:08X}",
    "console": console,
    "header_checksum": f"0x{header_checksum:04X}",
    "calculated_checksum": f"0x{checksum:04X}",
    "status": "PASS" if not errors else "FAIL",
    "errors": errors,
}
print(json.dumps(report, indent=2))
sys.exit(0 if not errors else 1)
