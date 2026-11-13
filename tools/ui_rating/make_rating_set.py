"""Copy the fixed blind-rating frame set under neutral names.

usage: python make_rating_set.py <scaled_frames_dir> <physical_frames_dir> <tag> <out_dir> [--old-stagings]
The mapping (neutral name -> shot) is written to <out_dir>/../<tag>_mapping.json,
OUTSIDE the folder the readers are shown.

Session UI-4 (November 12, 2026): three frames are shot as the game shows them
(STAGED_UI4) — the province panel and the war detail over the live war room, the
menu with the war office answering — a declared measure correction; their marks are
reported apart from the 27 frames whose staging never moved. `--old-stagings` maps
them to the alone shots (UI-2's and UI-3's protocol).
"""
import json
import shutil
import sys
from pathlib import Path

# (neutral id, source kind, frame stem without the date tag)
SET = [
    ("F01", "scaled", "IQ10_WAR_ROOM_BOOT"),
    ("F02", "physical", "IQ10_WAR_ROOM_BOOT@5120x1440"),
    ("F03", "scaled", "IQ10_WAR_ROOM_BOOT_X2"),
    ("F04", "scaled", "IQ10_WAR_ROOM_TUTORIAL"),
    ("F05", "scaled", "IQ10_LEDGER_BOOT_FORCES"),
    ("F06", "scaled", "IQ10_LEDGER_BOOT_ECONOMY"),
    ("F07", "scaled", "IQ10_LEDGER_BOOT_TERRITORIES"),
    ("F08", "scaled", "IQ10_LEDGER_BOOT_MANPOWER"),
    ("F09", "scaled", "IQ10_GENERALS_BOOT"),
    ("F10", "scaled", "IQ10_GENERALS_T20"),
    ("F11", "scaled", "IQ10_DIPLO_BOOT_NATIONS"),
    ("F12", "scaled", "IQ10_DIPLO_BOOT_VASSALS"),
    ("F13", "scaled", "IQ10_DIPLO_T20_BALANCE"),
    ("F14", "scaled", "IQ10_WIZARD_STEP1"),
    ("F15", "scaled", "IQ10_WIZARD_STEP2_AUSTRIA"),
    ("F16", "scaled", "IQ10_SETTLEMENT_THREE_COURTS"),
    ("F17", "scaled", "IQ10_DISPATCH_T20"),
    ("F18", "scaled", "IQ10_GAZETTE_T20"),
    ("F19", "scaled", "IQ10_ENEMY_PHASE_T20"),
    ("F20", "scaled", "IQ10_DIORAMA_DADJ"),
    ("F21", "scaled", "IQ10_PETITION_POPUP"),
    ("F22", "scaled", "IQ10_AFFAIR_LETTER_BERTHIERS_MEMORIAL"),
    ("F23", "scaled", "IQ10_OBJECTION_DIALOG"),
    ("F24", "scaled", "IQ10_REGION_PARIS"),
    ("F25", "scaled", "IQ10_WAR_DETAIL_T20"),
    ("F26", "scaled", "IQ10_CAMPAIGN_END_IMPERIAL"),
    ("F27", "scaled", "IQ10_MAIN_MENU"),
    ("F28", "scaled", "IQ10_WAR_ROOM_PAUSE_SETTINGS"),
    ("F29", "scaled", "IQ10_MAILBOX_BOOT"),
    ("F30", "scaled", "IQ10_CORRESPONDENCE_DESK"),
]


# Session UI-4: the three re-staged frames (neutral id -> the in-context shot's stem).
STAGED_UI4 = {
    "F24": "IQ10_REGION_PARIS_WAR_ROOM",
    "F25": "IQ10_WAR_DETAIL_T20_WAR_ROOM",
    "F27": "IQ10_MAIN_MENU_ANSWERING",
}


def find(frames: Path, stem: str, tag: str) -> Path | None:
    if "@" in stem:
        base, res = stem.split("@")
        base = base.replace("IQ10_", "UXR0_"); cands = sorted(frames.glob(f"{base}_{res}_*{tag}.png"))
        return cands[0] if cands else None
    p = frames / f"{stem}_{tag}.png"
    return p if p.exists() else None


def main() -> int:
    scaled, physical, tag, out = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], Path(sys.argv[4])
    old_stagings = "--old-stagings" in sys.argv[5:]
    out.mkdir(parents=True, exist_ok=True)
    mapping, missing = {}, []
    for fid, kind, stem in SET:
        if not old_stagings and fid in STAGED_UI4:
            stem = STAGED_UI4[fid]
        src = find(scaled if kind == "scaled" else physical, stem, tag)
        if src is None:
            missing.append(stem)
            continue
        dst = out / f"{fid}.png"
        shutil.copyfile(src, dst)
        mapping[fid] = {"stem": stem, "src": str(src)}
    (out.parent / f"{tag}_mapping.json").write_text(json.dumps(mapping, indent=1), encoding="utf-8")
    print(f"copied {len(mapping)}; missing {missing}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
