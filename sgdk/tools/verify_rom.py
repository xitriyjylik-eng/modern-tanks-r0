#!/usr/bin/env python3
import hashlib, json, struct, sys
from pathlib import Path

p = Path(sys.argv[1] if len(sys.argv) > 1 else "out/rom.bin")
data = p.read_bytes()


def be16(off):
    return struct.unpack_from(">H", data, off)[0]


def be32(off):
    return struct.unpack_from(">I", data, off)[0]


def sgdk_xor_fold(buf):
    """Reproduce SGDK 2.11 SYS_computeChecksum() semantics."""
    if len(buf) & 3:
        buf += b"\0" * ((4 - (len(buf) & 3)) & 3)
    chk = 0
    for (word,) in struct.iter_unpack(">I", buf):
        chk ^= word
    return (chk ^ (chk >> 16)) & 0xFFFF


errors = []
if len(data) < 0x200:
    errors.append("ROM shorter than 0x200 bytes")

initial_sp = be32(0) if len(data) >= 8 else 0
reset_pc = be32(4) if len(data) >= 8 else 0
console = data[0x100:0x110].decode("ascii", errors="replace") if len(data) >= 0x110 else ""
header_checksum = be16(0x18E) if len(data) >= 0x190 else 0

# SGDK's linker uses RAM 0xE0FF0000..0xE0FFFFFF and deliberately places
# __stack one byte past that range at 0xE1000000; the first push enters RAM.
valid_sgdk_stack = (0xE0FF0000 < initial_sp <= 0xE1000000)

# sizebnd/SYS checksum is an XOR of 32-bit words folded to 16 bits.  A ROM
# with the embedded checksum included must fold to zero.  Zeroing the header
# checksum field yields the exact value that should be stored in the header.
sgdk_full_fold = sgdk_xor_fold(data) if data else 0
checksum_source = bytearray(data)
if len(checksum_source) >= 0x190:
    checksum_source[0x18E:0x190] = b"\0\0"
required_header_checksum = sgdk_xor_fold(bytes(checksum_source)) if checksum_source else 0

if not valid_sgdk_stack:
    errors.append(f"initial SP is not valid for SGDK RAM/stack top: 0x{initial_sp:08X}")
if not (0x000200 <= reset_pc < len(data)):
    errors.append(f"reset PC outside ROM payload: 0x{reset_pc:08X}")
if "SEGA" not in console:
    errors.append(f"SEGA signature missing at 0x100: {console!r}")
if header_checksum != required_header_checksum:
    errors.append(
        f"SGDK checksum field mismatch header=0x{header_checksum:04X} "
        f"required=0x{required_header_checksum:04X}"
    )
if sgdk_full_fold != 0:
    errors.append(f"SGDK full-ROM XOR-fold is not zero: 0x{sgdk_full_fold:04X}")

report = {
    "file": str(p),
    "size": len(data),
    "sha256": hashlib.sha256(data).hexdigest(),
    "initial_sp": f"0x{initial_sp:08X}",
    "reset_pc": f"0x{reset_pc:08X}",
    "console": console,
    "header_checksum": f"0x{header_checksum:04X}",
    "required_header_checksum": f"0x{required_header_checksum:04X}",
    "sgdk_full_rom_xor_fold": f"0x{sgdk_full_fold:04X}",
    "status": "PASS" if not errors else "FAIL",
    "errors": errors,
}
print(json.dumps(report, indent=2))
sys.exit(0 if not errors else 1)
