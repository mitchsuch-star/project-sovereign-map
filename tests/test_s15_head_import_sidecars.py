"""S15's head — RE3-9 (November 6, 2026; the row `BUG_FIXES.md` §RE3, the rules
`SYSTEMS_REFERENCE.md` §177.1): every Godot import sidecar of a tracked asset
is tracked, and every tracked sidecar has its asset.

`assets/` is git-ignored (`.gitignore:40`) and `*.import` with it
(`project-sovereign/.gitignore:7`), so each asset AND its `.import` is
force-added by hand; RE3-3 found three sidecars missing (the dress), RE3-9's
sweep 188 more (the portraits, the icons, the fonts, the heraldry, the
ornaments) — a fresh clone re-imported them with Godot's defaults and fresh
uids. On-disk assertions cannot see this by construction (the NP-V lesson,
`tests/test_ui_visual_foundation.py`); this file asks git, once, for the whole
project. The user's word, November 6, 2026: "Force-add all 188".
"""
import re
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PROJECT = "godot-client/project-sovereign"
# The extensions Godot imports through a `.import` sidecar that the project
# ships (textures, fonts, audio); a scene, a resource and a script need none.
IMPORTED = {".png", ".jpg", ".jpeg", ".svg", ".webp", ".bmp", ".tga",
            ".ttf", ".otf", ".woff", ".woff2", ".mp3", ".ogg", ".wav"}
# a drive letter (not the `s:/` of `res://`), a user's folder, this checkout
MACHINE = re.compile(r"(?i)(?<![a-z])[a-z]:[\\/]|[\\/]users[\\/]|pycharmprojects")


def _tracked():
    out = subprocess.run(["git", "ls-files", "--", PROJECT], cwd=str(REPO),
                         capture_output=True, text=True, check=True).stdout
    return {line.strip() for line in out.splitlines() if line.strip()}


class TestEveryTrackedAssetShipsItsSidecar:
    def test_every_tracked_asset_has_a_tracked_import(self):
        tracked = _tracked()
        assets = sorted(p for p in tracked if Path(p).suffix.lower() in IMPORTED)
        assert len(assets) >= 360, len(assets)          # 360 at RE3-9; only ever more
        missing = [p for p in assets if f"{p}.import" not in tracked]
        assert not missing, (
            f"{len(missing)} tracked asset(s) ship without a tracked .import sidecar "
            f"(assets/ is git-ignored — `git add -f` the sidecar beside the asset): {missing[:20]}")

    def test_every_tracked_import_has_its_asset(self):
        tracked = _tracked()
        imports = sorted(p for p in tracked if p.endswith(".import"))
        assert len(imports) >= 360, len(imports)
        orphans = [p for p in imports if p[: -len(".import")] not in tracked]
        assert not orphans, orphans

    def test_no_tracked_import_carries_a_machine_path(self):
        """A sidecar's paths are `res://` — a drive letter or a user's folder in
        one would make a clone's import differ from this tree's."""
        for rel in sorted(p for p in _tracked() if p.endswith(".import")):
            text = (REPO / rel).read_text(encoding="utf-8", errors="replace")
            assert not MACHINE.search(text), rel
