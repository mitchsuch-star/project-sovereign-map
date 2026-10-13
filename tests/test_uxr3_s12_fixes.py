"""UXR-3 fixes — Pre-Deploy S12 part 1 (October 13, 2026).

The S11 review (`docs/audits/UXR3_REVIEW_2026_10_13.md`) filed 84 rows against
the frozen `docs/UX_CHECKLIST_V1.json`. S12 part 1 fixes them by class:

  Part 1  the harness's gaps — the three popups the checklist names and the
          IQ-10 manifest had never shot (UXR3-56 … 58), shot under the
          checklist's own ids; and two defects found shooting them (UXR3-X1,
          UXR3-X2).

The re-read of every flipped item is `docs/audits/UXR3_REREAD_2026_10_13.md`;
its records are `docs/audits/uxr3_s12/`. Rules `SYSTEMS_REFERENCE.md` §113.6.

The pins are engine-free where the source is the subject, and DRIVEN (the real
Godot binary, headless) where behaviour is. A driven pin skips without the
engine, and a skip is not a pass.
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import subprocess
import sys

import pytest

from tests import _chip_census as C

REPO = pathlib.Path(__file__).resolve().parents[1]
PROJECT = REPO / "godot-client" / "project-sovereign"
SCRIPTS = PROJECT / "scripts"
SCENES = PROJECT / "scenes"
TOOLS = REPO / "tools"
CHECKLIST = REPO / "docs" / "UX_CHECKLIST_V1.json"
sys.path.insert(0, str(TOOLS))

import iq10_capture_payloads as P  # noqa: E402
import iq10_run_captures as R  # noqa: E402
import uxr3_consistency_census as CEN  # noqa: E402
import uxr3_review as RV  # noqa: E402

NEVER_SHOT = ("objection_dialog", "capture_choice", "talleyrand_objection")


def _src(rel: str) -> str:
    return (PROJECT / rel).read_text(encoding="utf-8")


def _func(src: str, name: str) -> str:
    """The body of one GDScript func (to the next top-level func)."""
    m = re.search(rf"(?ms)^(?:static )?func {re.escape(name)}\(.*?(?=^(?:static )?func |\Z)", src)
    assert m, name
    return m.group(0)


# ═══ Part 1 — the harness's gaps (UXR3-56 … 58) ═══════════════════════════════

class TestTheThreePopupsAreShotUnderTheChecklistsIds:
    @pytest.fixture(scope="class")
    def checklist(self) -> dict:
        return json.loads(CHECKLIST.read_text(encoding="utf-8"))

    def test_each_has_a_shot_row_named_by_the_checklist(self, checklist):
        rows = {s["id"]: s for s in R.SHOTS}
        named = {s["id"]: s for g in checklist["groups"] for s in g["surfaces"]}
        for sid in NEVER_SHOT:
            assert named[sid]["shot"] is None            # the frozen checklist, untouched
            row = rows[sid]
            assert row["scene"] == named[sid]["scene"], sid
            assert row["payload"] == sid and row["mode"] == "call", sid
            assert row["must_show"], sid

    def test_each_is_opened_the_way_main_gd_opens_it(self):
        rows = {s["id"]: s for s in R.SHOTS}
        main = _src("scripts/main.gd")
        assert rows["objection_dialog"]["method"] == "show_from_response"
        assert rows["capture_choice"]["method"] == "show_capture_choice"
        assert rows["capture_choice"]["args"] == ["$payload.capture_data"]
        assert "capture_choice_dialog.show_capture_choice(capture_data)" in main
        assert rows["talleyrand_objection"]["method"] == "show_objection"
        assert rows["talleyrand_objection"]["args"] == ["$payload.diplomatic_objection"]
        assert "talleyrand_objection_popup.show_objection(response.diplomatic_objection)" in main

    def test_the_payloads_come_from_the_rows_own_boards(self):
        assert P.CAPTURES["popups_s12"] is P.cap_popups_s12
        src = pathlib.Path(P.__file__).read_text(encoding="utf-8")
        body = src[src.index("def cap_popups_s12"):src.index("CAPTURES = {")]
        # B4b's staged board, imported — never re-typed
        assert 'test_module("test_b4b_the_one_tail")' in body and "T._payloads(mp)" in body
        # the deep-audit declaration road, on the unstaged boot
        assert 'cmd(c, "declare war on Prussia")' in body and 'cmd(c, "1")' in body

    def test_the_review_reads_them_under_their_own_ids(self):
        for sid in NEVER_SHOT:
            assert RV.shot_of({"id": sid, "shot": None}) == sid
        assert RV.shot_of({"id": "never_in_the_manifest", "shot": None}) is None
        assert RV.shot_of({"id": "x", "shot": "ledger_boot_forces"}) == "ledger_boot_forces"

    def test_their_own_files_carry_no_one_off_grey_or_size(self):
        cache: dict = {}
        for f in ("res://scenes/objection_dialog.tscn", "res://scripts/objection_dialog.gd",
                  "res://scenes/capture_choice_dialog.tscn", "res://scripts/capture_choice_dialog.gd",
                  "res://scenes/talleyrand_objection_popup.tscn",
                  "res://scripts/talleyrand_objection_popup.gd"):
            assert CEN.census_file(f, cache) == [], f


# ═══ UXR3-X1 — the objection dialog's mapping, one home ══════════════════════

class TestTheObjectionMappingLivesInTheDialog:
    def test_main_gd_opens_the_dialog_through_the_dialogs_own_mapping(self):
        main = _src("scripts/main.gd")
        body = _func(main, "_show_objection_dialog")
        assert "ObjectionDialogScript.data_from_response(response)" in body
        assert '"insist_penalty": objection.get(' not in main      # the hand-built copy is gone
        assert 'const ObjectionDialogScript := preload("res://scripts/objection_dialog.gd")' in main

    def test_the_mapping_carries_every_key_the_dialog_reads(self):
        dlg = _src("scripts/objection_dialog.gd")
        mapping = _func(dlg, "data_from_response")
        shown = _func(dlg, "show_objection")
        read = set(re.findall(r'objection_data\.get\("(\w+)"', shown)) | \
            set(re.findall(r'objection_data\.has\("(\w+)"\)', shown))
        built = set(re.findall(r'^\t\t"(\w+)":', mapping, re.M))
        assert read, "the dialog reads no keys?"
        assert read <= built, sorted(read - built)
        assert {"insist_ap_cost", "insist_note", "trust_gain_modifier"} <= built


@pytest.fixture(scope="module")
def driven_mapping(tmp_path_factory):
    exe = C.engine()
    if exe is None:
        pytest.skip("Godot engine not on this machine — the driven pins skip, "
                    "and a skip is not a pass")
    work = tmp_path_factory.mktemp("uxr3_s12_map")
    out = work / "out.json"
    script = work / "objection_map_check.gd"
    script.write_text(
        "extends SceneTree\n"
        "func _init():\n"
        "\tvar S = load(\"res://scripts/objection_dialog.gd\")\n"
        "\tvar strategic = S.data_from_response({\"pending_objection\": true, \"marshal\": \"Ney\",\n"
        "\t\t\"trust\": 55, \"objection\": {\"marshal\": \"Ney\", \"tone\": \"firm\", \"message\": \"m\",\n"
        "\t\t\"trust_gain_modifier\": 0.5, \"insist_ap_cost\": 2,\n"
        "\t\t\"insist_note\": \"he must first go defensive\"}})\n"
        "\tvar tactical = S.data_from_response({\"marshal\": \"Lannes\", \"message\": \"t\",\n"
        "\t\t\"insist_note\": \"x\", \"insist_ap_cost\": 3, \"trust_gain_modifier\": 0.75})\n"
        "\tvar f = FileAccess.open(OS.get_environment(\"UXR3_OUT\"), FileAccess.WRITE)\n"
        "\tf.store_string(JSON.stringify({\"strategic\": strategic, \"tactical\": tactical}))\n"
        "\tf.close()\n"
        "\tquit(0)\n", encoding="utf-8")
    env = dict(os.environ, UXR3_OUT=str(out))
    proc = subprocess.run([exe, "--headless", "--path", str(PROJECT), "--script", str(script)],
                          capture_output=True, text=True, encoding="utf-8", errors="replace",
                          timeout=180, env=env, cwd=str(PROJECT), stdin=subprocess.DEVNULL)
    if not out.is_file():
        pytest.fail(f"the check wrote nothing\nexit={proc.returncode}\n{proc.stderr[-1500:]}")
    return json.loads(out.read_text(encoding="utf-8"))


class TestTheMappingDriven:
    def test_a_strategic_objection_carries_its_price_and_the_damper(self, driven_mapping):
        d = driven_mapping["strategic"]
        assert d["is_strategic"] is True and d["marshal"] == "Ney"
        assert d["insist_note"] == "he must first go defensive" and int(d["insist_ap_cost"]) == 2
        assert float(d["trust_gain_modifier"]) == 0.5
        assert int(d["trust"]) == 55                        # the response's own trust

    def test_a_tactical_objection_reads_the_top_level(self, driven_mapping):
        d = driven_mapping["tactical"]
        assert d["is_strategic"] is False and d["marshal"] == "Lannes"
        assert d["insist_note"] == "x" and int(d["insist_ap_cost"]) == 3
        assert float(d["trust_gain_modifier"]) == 0.75


# ═══ UXR3-X2 — the two popups fit their content ══════════════════════════════

class TestThePopupsFitTheirContent:
    @pytest.mark.parametrize("script, opener", [("objection_dialog.gd", "show_objection"),
                                                ("capture_choice_dialog.gd", "show_capture_choice")])
    def test_open_and_refit_shrink_after_the_clamp(self, script, opener):
        src = _src(f"scripts/{script}")
        for name in (opener, "refit"):
            body = _func(src, name)
            clamp = body.index("Utils.clamp_centered_panel($PanelContainer)")
            shrink = body.index("Utils.shrink_centered_panel_to_content($PanelContainer)")
            assert clamp < shrink, (script, name)

    def test_the_helper_only_ever_shrinks(self):
        body = _func(_src("scripts/utils.gd"), "shrink_centered_panel_to_content")
        assert "if need > 0.0 and need < have:" in body
        assert body.count("await panel.get_tree().process_frame") == 2
