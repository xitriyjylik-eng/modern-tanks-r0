from pathlib import Path

parts_dir = Path(__file__).resolve().parent / "r2_art_parts"
order = [
    "part00.pyfrag", "part01.pyfrag", "part02.pyfrag", "part03.pyfrag", "part04.pyfrag",
    "part05a.pyfrag", "part05b.pyfrag", "part05c.pyfrag", "part05d.pyfrag", "part06.pyfrag",
]
source = "".join((parts_dir / name).read_text(encoding="utf-8") for name in order)
exec(compile(source, "<r2-max-detail-art>", "exec"))
