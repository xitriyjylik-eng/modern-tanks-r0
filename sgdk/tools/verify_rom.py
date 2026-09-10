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
    """Reproduce SGDK 2.11 SYS_computeChecksum()/sizebnd checksum semantics."""
    if len(buf) & 3:
        buf += b"\0" * ((4 - (len(buf) & 3)) & 3)
    chk = 0
    for (word,) in struct.iter_unpack(">I", buf):
        chk ^= word
    return (chk ^ (chk >> 16)) & 0xFFFF


def md_classic_checksum(buf):
    """Classic Mega Drive checksum: 16-bit sum from 0x200 to physical ROM EOF."""
    payload = buf[0x200:]
    if len(payload) & 1:
        payload += b"\0"
    total = 0
    for (word,) in struct.iter_unpack(">H", payload):
        total = (total + word) & 0xFFFF
    return total


errors = []
warnings = []
if len(data) < 0x200:
    errors.append("ROM shorter than 0x200 bytes")

initial_sp = be32(0) if len(data) >= 8 else 0
reset_pc = be32(4) if len(data) >= 8 else 0
console = data[0x100:0x110].decode("ascii", errors="replace") if len(data) >= 0x110 else ""
header_checksum = be16(0x18E) if len(data) >= 0x190 else 0
rom_start = be32(0x1A0) if len(data) >= 0x1A8 else 0
rom_end = be32(0x1A4) if len(data) >= 0x1A8 else 0
ram_start = be32(0x1A8) if len(data) >= 0x1B0 else 0
ram_end = be32(0x1AC) if len(data) >= 0x1B0 else 0
region = data[0x1F0:0x200].decode("ascii", errors="replace") if len(data) >= 0x200 else ""
actual_rom_end = len(data) - 1 if data else 0

# SGDK 2.11 maps RAM at 0xE0FF0000..0xE0FFFFFF in linker space and places
# __stack one byte past that range at 0xE1000000. sega.s subtracts the system
# stack reservation before the first stack push, so this is intentional SGDK ABI.
valid_sgdk_stack = (0xE0FF0000 < initial_sp <= 0xE1000000)

# SGDK sizebnd -checksum deliberately uses its own fast XOR-fold format.
sgdk_full_fold = sgdk_xor_fold(data) if data else 0
checksum_source = bytearray(data)
if len(checksum_source) >= 0x190:
    checksum_source[0x18E:0x190] = b"\0\0"
sgdk_required_checksum = sgdk_xor_fold(bytes(checksum_source)) if checksum_source else 0
classic_checksum = md_classic_checksum(data) if len(data) >= 0x200 else 0

if not valid_sgdk_stack:
    errors.append(f"initial SP is not valid for SGDK RAM/stack top: 0x{initial_sp:08X}")
if not (0x000200 <= reset_pc < len(data)):
    errors.append(f"reset PC outside ROM payload: 0x{reset_pc:08X}")
if "SEGA" not in console:
    errors.append(f"SEGA signature missing at 0x100: {console!r}")
if header_checksum != sgdk_required_checksum:
    errors.append(
        f"SGDK checksum field mismatch header=0x{header_checksum:04X} "
        f"required=0x{sgdk_required_checksum:04X}"
    )
if sgdk_full_fold != 0:
    errors.append(f"SGDK full-ROM XOR-fold is not zero: 0x{sgdk_full_fold:04X}")

if header_checksum != classic_checksum:
    warnings.append(
        f"classic Mega Drive additive checksum differs from SGDK checksum: "
        f"header=0x{header_checksum:04X}, classic=0x{classic_checksum:04X}"
    )
if rom_start != 0:
    warnings.append(f"ROM start field is non-zero: 0x{rom_start:08X}")
if rom_end != actual_rom_end:
    warnings.append(
        f"header ROM end 0x{rom_end:08X} differs from physical file end 0x{actual_rom_end:08X}; "
        "SGDK 2.11 default header declares 1 MiB"
    )

report = {
    "file": str(p),
    "size": len(data),
    "sha256": hashlib.sha256(data).hexdigest(),
    "initial_sp": f"0x{initial_sp:08X}",
    "reset_pc": f"0x{reset_pc:08X}",
    "console": console,
    "region": region,
    "header_checksum": f"0x{header_checksum:04X}",
    "sgdk_required_header_checksum": f"0x{sgdk_required_checksum:04X}",
    "sgdk_full_rom_xor_fold": f"0x{sgdk_full_fold:04X}",
    "classic_md_additive_checksum": f"0x{classic_checksum:04X}",
    "classic_md_checksum_matches_header": header_checksum == classic_checksum,
    "header_rom_start": f"0x{rom_start:08X}",
    "header_rom_end": f"0x{rom_end:08X}",
    "physical_rom_end": f"0x{actual_rom_end:08X}",
    "header_ram_start": f"0x{ram_start:08X}",
    "header_ram_end": f"0x{ram_end:08X}",
    "status": "FAIL" if errors else ("PASS_WITH_WARNINGS" if warnings else "PASS"),
    "errors": errors,
    "warnings": warnings,
}
print(json.dumps(report, indent=2))
sys.exit(0 if not errors else 1)
