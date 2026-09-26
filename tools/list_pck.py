"""List (or check) the files inside a Godot 4 `.pck` (the release build, Sept 25, 2026).

The build row's done-when says the Godot export must carry every JSON the
boot reads. Godot cannot list a pack from the command line, so this reads the
pack directory itself: the PCK format v2 that Godot 4.x writes (`GDPC` magic,
format version, engine version, flags, file base, sixteen reserved words,
then the file table).

    python tools/list_pck.py deploy/dist/ink_iron_server/InkAndIron.pck
    python tools/list_pck.py <pck> --require res://assets/maps/europe_1805.json ...

`--require` exits 1 when any named path is missing — build.bat's gate.
"""

from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

PCK_MAGIC = b"GDPC"
PACK_DIR_ENCRYPTED = 1 << 0
PACK_REL_FILEBASE = 1 << 1  # Godot 4.4: file_base is relative to the pack start


def list_pck(path: Path) -> list[tuple[str, int, int]]:
    """Every (path, offset, size) in the pack, in directory order."""
    with open(path, "rb") as fh:
        head = fh.read(4)
        if head != PCK_MAGIC:
            raise ValueError(f"{path} is not a Godot pack (magic {head!r})")
        fmt, major, minor, patch, flags = struct.unpack("<5I", fh.read(20))
        (file_base,) = struct.unpack("<Q", fh.read(8))
        fh.read(16 * 4)  # reserved
        if flags & PACK_DIR_ENCRYPTED:
            raise ValueError(f"{path}: the directory is encrypted; cannot list it")
        (count,) = struct.unpack("<I", fh.read(4))
        entries = []
        for _ in range(count):
            (string_len,) = struct.unpack("<I", fh.read(4))
            raw = fh.read(string_len)
            name = raw.rstrip(b"\x00").decode("utf-8", errors="replace")
            offset, size = struct.unpack("<QQ", fh.read(16))
            fh.read(16)  # md5
            if fmt >= 2:
                fh.read(4)  # per-file flags
            entries.append((name, offset, size))
    return entries


def _bare(path: str) -> str:
    """Godot 4.4 stores pack paths WITHOUT the `res://` prefix (measured on the
    release export); a required path may be written either way."""
    return path[len("res://"):] if path.startswith("res://") else path


def _carries(names: set[str], required: str) -> bool:
    """A resource is in the pack as itself, or in its exported form: a scene
    or script exported as binary leaves `<path>.remap` at its path (the
    payload lives under `.godot/exported/`), an imported asset leaves
    `<path>.import` (the payload under `.godot/imported/`)."""
    bare = _bare(required)
    return bare in names or f"{bare}.remap" in names or f"{bare}.import" in names


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("pck", type=Path)
    ap.add_argument("--require", nargs="*", default=[],
                    help="res:// paths that must be present (exit 1 otherwise)")
    ap.add_argument("--grep", default="",
                    help="only print entries containing this substring")
    ap.add_argument("--quiet", action="store_true", help="print nothing but the verdict")
    args = ap.parse_args(argv)

    entries = list_pck(args.pck)
    names = {_bare(name) for name, _, _ in entries}
    if not args.quiet:
        for name, _offset, size in entries:
            if args.grep and args.grep not in name:
                continue
            print(f"{size:>12,d}  {name}")
        print(f"-- {len(entries)} files, {sum(s for _, _, s in entries):,d} bytes of content")

    missing = [p for p in args.require if not _carries(names, p)]
    if missing:
        print(f"[ERROR] {args.pck} is missing {len(missing)} required file(s):")
        for p in missing:
            print(f"   {p}")
        return 1
    if args.require:
        print(f"[OK] {args.pck.name} carries all {len(args.require)} required file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
