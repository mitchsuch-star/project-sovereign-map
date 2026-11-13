"""Session UI-5 (November 12, 2026) — the sound census: no surface is silent.

The August wiring left six surfaces opening in silence (the survey's list:
the treaty confirm, the strategic report, Talleyrand's objection, the
sabotage discovery, the redemption, the load dialog) and every decision on a
letter sharing one cue. This census walks every player-facing surface script
— each popup, dialog, view, book, panel and menu in the client — and lists the
cues it plays (`AudioManager.play("…")`, `start_loop`, `play_anthem`,
`play_music_once`, `play_result`, `request_scene_music` …). A surface with no
sound of its own fails, unless it is named in SOUNDED_ELSEWHERE with the
reason its sound comes from another script.

    .venv/Scripts/python.exe tools/ui5_sound_census.py          # the table
    .venv/Scripts/python.exe tools/ui5_sound_census.py --check  # exit 1 on a silent surface

Pinned by tests/test_ui5_full_measure.py.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "godot-client" / "project-sovereign" / "scripts"
SCENES = REPO / "godot-client" / "project-sovereign" / "scenes"

# The surfaces that are not caught by the name patterns below.
NAMED_SURFACES = [
    "diplomacy_wizard.gd", "diplomatic_ledger.gd", "strategic_ledger.gd",
    "marshal_management.gd", "mailbox_panel.gd", "campaign_log.gd", "campaign_end.gd",
    "pause_menu.gd", "main_menu.gd", "settings_panel.gd", "scale_card.gd",
    "region_panel.gd", "war_status_panel.gd", "notification_bar.gd", "top_bar.gd",
    "tutorial_overlay.gd", "battle_diorama.gd", "order_confirm_card.gd",
    "codex_view.gd",
]
PATTERNS = ["*_popup.gd", "*_dialog.gd", "*_view.gd"]

# A surface whose sound is played by the script that opens it — named with the
# reason, so a silent surface is a decision on the record, never an accident.
SOUNDED_ELSEWHERE = {
    "popup_base.gd": "the base class: it plays `back` on close for every PopupBase surface",
}

CUE_RX = re.compile(
    r"AudioManager\.(play|start_loop|stop_loop|play_anthem|play_music_once|play_result|"
    r"request_scene_music|release_scene_music|start_scribble|preview_bus|keystroke|"
    r"hint_notification_priority|duck_music|set_bus_volume|announce_war|skip_track|"
    r"play_track)\(\s*(\"[^\"]*\")?")


def surfaces() -> list[pathlib.Path]:
    found: dict[str, pathlib.Path] = {}
    for pattern in PATTERNS:
        for path in SCRIPTS.glob(pattern):
            found[path.name] = path
    for name in NAMED_SURFACES:
        path = SCRIPTS / name
        if path.exists():
            found[name] = path
    return [found[k] for k in sorted(found)]


def cues_of(path: pathlib.Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    out = []
    for m in CUE_RX.finditer(text):
        call, arg = m.group(1), (m.group(2) or "").strip('"')
        out.append(f"{call}({arg})" if arg else call)
    return sorted(set(out))


def run(check: bool) -> int:
    silent = []
    rows = []
    for path in surfaces():
        cues = cues_of(path)
        reason = SOUNDED_ELSEWHERE.get(path.name, "")
        rows.append((path.name, cues, reason))
        if not cues and not reason:
            silent.append(path.name)
    width = max(len(r[0]) for r in rows)
    for name, cues, reason in rows:
        shown = ", ".join(cues) if cues else ("— " + reason if reason else "SILENT")
        print(f"{name:{width}s}  {shown}")
    print(f"\n{len(rows)} surfaces; silent: {len(silent)}")
    if silent:
        print("silent:", ", ".join(silent))
    return 1 if (check and silent) else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    return run(ap.parse_args().check)


if __name__ == "__main__":
    sys.exit(main())
