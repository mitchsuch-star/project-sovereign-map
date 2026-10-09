"""UXR-1 "The theme floor" — the one-time sweep (October 9, 2026), kept as the
record of the rule it applied; `tests/test_uxr1_scale_fix.py` pins the result.

The rule: no raw font-size override under 14 logical px survives in the client.
    * a BODY surface (the command window's output and its command line, the
      ledgers' content areas, the dispatch and the Moniteur, the tutor card's
      body) DROPS its override and takes the theme's 16;
    * every other Label / Button / RichTextLabel under 14 takes the theme's
      Caption family (`theme_type_variation` Caption / CaptionButton /
      CaptionRich = 14) — badges, hints, tab buttons, counters, version lines.
    * EXEMPT, with a reason: the map's world-space furniture in
      `scenes/map_renderer_base.gd` (name stacks, garrison chips, sail counts —
      scaled by the camera, not the interface; UXR-X4 owns them) and the
      war-detail popup's two COMPUTED sizes (`max(7, font_size - 3)`, UXR-2's).
    * a site authored at EXACTLY 14 is caption-SIZED, and the first AFTER census
      read every body-class one RED at 1080p (14 < 16): each is decided by the
      table below — a dialog's ACTION button and a body description DROP the
      override (the theme's Button 16 / body 16), chrome (close ×, minimize,
      the command row, log headers) and sub-lines (an objection's trust /
      authority lines, a warning, a header in a small popup) take the Caption
      family so the census reads them as the captions they are.

Idempotent: a second run finds nothing to change.
"""
from __future__ import annotations

import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
PROJECT = REPO / "godot-client" / "project-sovereign"
FLOOR = 14

# (scene file, node name) pairs that are BODY text: the override goes, the theme's 16 stays.
BODY_NODES = {
    ("main.tscn", "OutputDisplay"), ("main.tscn", "CommandInput"),
    ("strategic_ledger.tscn", "ContentArea"), ("diplomatic_ledger.tscn", "ContentArea"),
    ("region_panel.tscn", "ContentArea"),
    ("dispatch_view.tscn", "ContentLabel"), ("gazette_view.tscn", "ContentLabel"),
    ("tutorial_overlay.tscn", "BodyText"),
}
VARIATION = {"Label": "Caption", "Button": "CaptionButton", "RichTextLabel": "CaptionRich",
             "LineEdit": None}
GD_EXEMPT = {"map_renderer_base.gd"}

# The sites authored at exactly 14 (scene, node) → "drop" (the theme's size) or
# "caption" (the Caption family). Every 14 in the client is listed; one that is
# not raises, so a new 14 is a decision, not a drift.
FOURTEEN_TSCN = {
    ("capture_choice_dialog.tscn", "DescriptionLabel"): "drop",
    ("commitment_paradox_popup.tscn", "HonorButton"): "drop",
    ("commitment_paradox_popup.tscn", "BreakButton"): "drop",
    ("diplomacy_wizard.tscn", "CloseButton"): "caption",
    ("glorious_charge_dialog.tscn", "WarningLabel"): "caption",
    ("glorious_charge_dialog.tscn", "ChargeButton"): "drop",
    ("glorious_charge_dialog.tscn", "RestrainButton"): "drop",
    ("incoming_proposal_popup.tscn", "AcceptButton"): "drop",
    ("incoming_proposal_popup.tscn", "CounterButton"): "drop",
    ("incoming_proposal_popup.tscn", "RejectButton"): "drop",
    ("incoming_proposal_popup.tscn", "DismissButton"): "drop",
    ("load_dialog.tscn", "CancelButton"): "drop",
    ("mailbox_panel.tscn", "CloseButton"): "caption",
    ("main.tscn", "Title"): "caption",
    ("main.tscn", "MinimizeButton"): "caption",
    ("main.tscn", "DiplomacyButton"): "caption",
    ("marshal_management.tscn", "ContentArea"): "drop",
    ("objection_dialog.tscn", "PersonalityLabel"): "caption",
    ("objection_dialog.tscn", "TrustLabel"): "caption",
    ("objection_dialog.tscn", "VindicationLabel"): "caption",
    ("objection_dialog.tscn", "AuthorityLabel"): "caption",
    ("objection_dialog.tscn", "TrustButton"): "drop",
    ("objection_dialog.tscn", "InsistButton"): "drop",
    ("objection_dialog.tscn", "CompromiseButton"): "drop",
    ("redemption_dialog.tscn", "TrustLabel"): "caption",
    ("reward_dialog.tscn", "CancelButton"): "drop",
    ("sabotage_discovery_popup.tscn", "ConfrontButton"): "drop",
    ("sabotage_discovery_popup.tscn", "OverlookButton"): "drop",
    ("talleyrand_objection_popup.tscn", "ProceedButton"): "drop",
    ("talleyrand_objection_popup.tscn", "ModifyButton"): "drop",
    ("talleyrand_objection_popup.tscn", "CancelButton"): "drop",
    ("vassal_rebellion_popup.tscn", "InvestButton"): "drop",
    ("vassal_rebellion_popup.tscn", "GarrisonButton"): "drop",
    ("vassal_rebellion_popup.tscn", "AcceptButton"): "drop",
    ("war_detail_popup.tscn", "HeaderLabel"): "caption",
    ("war_detail_popup.tscn", "CloseButton"): "caption",
}
# UXR-1b (the whole-client census): the six literal 15s — dialog titles, a
# message, the pause menu's two confirm buttons — were the last body-class
# rows RED at 1080p. All drop to the theme (16).
FIFTEEN_TSCN = {
    ("clarification_popup.tscn", "MessageLabel"): "drop",
    ("diplomacy_wizard.tscn", "TitleLabel"): "drop",
    ("interrupt_popup.tscn", "MessageLabel"): "drop",
    ("pause_menu.tscn", "ConfirmNewGameButton"): "drop",
    ("pause_menu.tscn", "CancelNewGameButton"): "drop",
    ("redemption_dialog.tscn", "MessageLabel"): "drop",
}
FOURTEEN_GD = {
    ("campaign_log.gd", "header_btn"): "caption",
    ("clarification_popup.gd", "btn"): "drop",
    ("interrupt_popup.gd", "btn"): "drop",
    ("load_dialog.gd", "btn"): "drop",
    ("main_menu.gd", "warn"): "caption",
    ("marshal_petition_dialog.gd", "btn"): "drop",
    ("proposal_confirm_popup.gd", "btn"): "drop",
    ("settings_panel.gd", "_scale_value"): "caption",
}


def sweep_tscn(path: pathlib.Path) -> int:
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    out, changed = [], 0
    node_type = node_name = None
    applied_for_node = False
    for line in lines:
        m = re.match(r'\[node name="([^"]+)"(?: type="([^"]+)")?', line)
        if m:
            node_name, node_type = m.group(1), m.group(2)
            applied_for_node = False
            out.append(line)
            continue
        m = re.match(r'theme_override_font_sizes/([a-z_]+) = (\d+)\s*$', line)
        if m and int(m.group(2)) < FLOOR:
            changed += 1
            if (path.name, node_name) in BODY_NODES:
                continue                      # drop: the theme's 16
            var = VARIATION.get(node_type or "")
            if var is None:
                continue                      # LineEdit: the theme's 16
            if not applied_for_node:
                out.append(f'theme_type_variation = &"{var}"\n')
                applied_for_node = True
            continue
        if m and int(m.group(2)) == FLOOR + 1:
            rule = FIFTEEN_TSCN.get((path.name, node_name))
            if rule is not None:
                changed += 1
                continue                      # "drop": the theme's size
        if m and int(m.group(2)) == FLOOR:
            rule = FOURTEEN_TSCN.get((path.name, node_name))
            if rule is None:
                raise SystemExit(f"{path.name}: {node_name} at 14 is not in FOURTEEN_TSCN — decide it")
            changed += 1
            if rule == "caption":
                var = VARIATION.get(node_type or "")
                if var is not None and not applied_for_node:
                    out.append(f'theme_type_variation = &"{var}"\n')
                    applied_for_node = True
            continue                          # "drop": the theme's size
        out.append(line)
    if changed:
        path.write_text("".join(out), encoding="utf-8")
    return changed


def _class_of(var: str, lines: list[str], at: int) -> str:
    for j in range(at, max(-1, at - 80), -1):
        mm = re.search(rf'\b{re.escape(var)}\b\s*(?::\s*(\w+))?\s*:?=\s*(\w+)\.new\(\)', lines[j])
        if mm:
            return mm.group(1) or mm.group(2)
        mm = re.search(rf'var {re.escape(var)}\s*:\s*(\w+)', lines[j])
        if mm:
            return mm.group(1)
    return "?"


def sweep_gd(path: pathlib.Path) -> int:
    if path.name in GD_EXEMPT:
        return 0
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    changed = 0
    seen_rich: set[tuple[str, int]] = set()
    for i, line in enumerate(lines):
        m = re.search(r'^(\s*)(\w+)\.add_theme_font_size_override\("([a-z_]+)", *(\d+)\)\s*$', line)
        if not m or int(m.group(4)) > FLOOR:
            continue
        if int(m.group(4)) == FLOOR:
            rule = FOURTEEN_GD.get((path.name, m.group(2)))
            if rule is None:
                raise SystemExit(f"{path.name}:{i + 1}: {m.group(2)} at 14 is not in FOURTEEN_GD — decide it")
            changed += 1
            if rule == "drop":
                lines[i] = ""
            else:
                cls14 = _class_of(m.group(2), lines, i)
                lines[i] = f'{m.group(1)}{m.group(2)}.theme_type_variation = &"{VARIATION[cls14]}"\n'
            continue
        indent, var, cls = m.group(1), m.group(2), _class_of(m.group(2), lines, i)
        variation = VARIATION.get(cls)
        if variation is None:
            raise SystemExit(f"{path.name}:{i + 1}: cannot type {var} ({cls})")
        changed += 1
        if cls == "RichTextLabel":
            # several size keys on one label → ONE variation line
            key = (var, i - (1 if (var, i - 1) in seen_rich else 0))
            if any(k[0] == var and abs(k[1] - i) <= 2 for k in seen_rich):
                lines[i] = ""
                continue
            seen_rich.add((var, i))
        lines[i] = f'{indent}{var}.theme_type_variation = &"{variation}"\n'
    if changed:
        path.write_text("".join(lines), encoding="utf-8")
    return changed


def main() -> int:
    total = 0
    for p in sorted((PROJECT / "scenes").glob("*.tscn")):
        n = sweep_tscn(p)
        if n:
            print(f"  {p.name}: {n} override(s)")
            total += n
    for p in sorted(list((PROJECT / "scripts").glob("*.gd")) + list((PROJECT / "scenes").glob("*.gd"))):
        n = sweep_gd(p)
        if n:
            print(f"  {p.name}: {n} override(s)")
            total += n
    print(f"swept {total} site(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
