"""UXR-3 — the look-and-feel review's checklist is FROZEN (Pre-Deploy S11 Part 1,
October 13, 2026).

`docs/UX_CHECKLIST_V1.json` holds the eight binary items R1–R8 of
`docs/UX_UI_REVIEW_PLAN.md` §UXR-3, each with its judge and its exact pass
rule, and the surface list: the plan's ten groups in its review order, each
split into the concrete surfaces the IQ-10 manifest names (plus the three
popups the plan names that the manifest has never shot). It was written and
committed BEFORE the first reading, the Score Finish's §4 pattern, so no rule
can be tuned to the marks: S11 reads against it and S12 re-reads its flipped
items against it.

These pins hold the freeze: the eight ids, the review order, every named shot
still in the manifest, and a SHA of the file's canonical JSON. An edit after
the reading fails here. A changed checklist is a NEW file (`UX_CHECKLIST_V2`),
never an edit to this one.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
CHECKLIST = REPO / "docs" / "UX_CHECKLIST_V1.json"
PROJECT = REPO / "godot-client" / "project-sovereign"

# The SHA-256 of json.dumps(checklist, sort_keys=True, separators=(",", ":"),
# ensure_ascii=False), taken at the freeze. Line endings and indentation do
# not move it; any change to a rule, an id or the order does.
FROZEN_SHA = "64a53aeb32ebf9305aeed435e3942e16fb31aadee217ba0302a22670b9ec1c82"

ITEM_IDS = ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8"]
JUDGES = {
    "R1": "instrument", "R2": "reader", "R3": "instrument", "R4": "instrument + reader",
    "R5": "reader + driven", "R6": "driven", "R7": "instrument", "R8": "reader",
}
# The review order (§UXR-3 "Surfaces, by time on screen") and each group's size.
GROUP_ORDER = [
    ("war_room", 27), ("dispatch", 11), ("generals", 8), ("diplomacy", 37),
    ("strategic_ledger", 32), ("tutorial", 2), ("enemy_phase_and_diorama", 8),
    ("popups", 10), ("menu_and_settings", 3), ("campaign_end", 7),
]
FIRST_OF_EACH = {
    "war_room": "war_room_boot", "dispatch": "dispatch_boot_today", "generals": "generals_boot",
    "diplomacy": "wizard_step1", "strategic_ledger": "ledger_boot_forces",
    "tutorial": "war_room_tutorial", "enemy_phase_and_diorama": "enemy_phase_t20",
    "popups": "objection_dialog", "menu_and_settings": "main_menu",
    "campaign_end": "campaign_end_verdict",
}
# The surface order itself: the SHA-256 of the 145 ids joined by "\n" in order.
ORDER_SHA = "183f07d72ab231b4538b4c3a73924271e39e5064188de958b1a53c8298f448eb"
UNREACHABLE = {"objection_dialog", "talleyrand_objection", "capture_choice"}


@pytest.fixture(scope="module")
def checklist() -> dict:
    assert CHECKLIST.is_file(), "the frozen checklist is missing"
    return json.loads(CHECKLIST.read_text(encoding="utf-8"))


def _surfaces(checklist: dict) -> list[dict]:
    return [s for g in checklist["groups"] for s in g["surfaces"]]


def _canonical_sha(obj) -> str:
    text = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class TestTheFreeze:
    def test_the_canonical_json_is_the_frozen_one(self, checklist):
        assert _canonical_sha(checklist) == FROZEN_SHA, (
            "docs/UX_CHECKLIST_V1.json changed after the S11 reading. The checklist is "
            "frozen: a new rule is a new file (UX_CHECKLIST_V2), never an edit.")

    def test_the_eight_items_and_their_judges(self, checklist):
        assert [it["id"] for it in checklist["items"]] == ITEM_IDS
        for it in checklist["items"]:
            assert it["judge"] == JUDGES[it["id"]], it["id"]
            assert it["pass_rule"].strip(), it["id"]
            assert it["name"] and it["text"], it["id"]

    def test_the_ten_groups_in_the_review_order(self, checklist):
        got = [(g["key"], len(g["surfaces"])) for g in checklist["groups"]]
        assert got == GROUP_ORDER
        assert [g["order"] for g in checklist["groups"]] == list(range(1, 11))
        # 'the top five by time on screen' = the first five groups (decided)
        assert [g["key"] for g in checklist["groups"] if g["top_five"]] == [k for k, _ in GROUP_ORDER[:5]]
        for g in checklist["groups"]:
            assert g["surfaces"][0]["id"] == FIRST_OF_EACH[g["key"]], g["key"]

    def test_the_surface_order_is_frozen(self, checklist):
        ids = [s["id"] for s in _surfaces(checklist)]
        assert len(ids) == len(set(ids)) == 145
        assert hashlib.sha256("\n".join(ids).encode("utf-8")).hexdigest() == ORDER_SHA, (
            "the review order moved: S12 re-reads against this order")
        assert ids[:4] == ["war_room_boot", "top_bar_boot", "top_bar_admiralty", "top_bar_mission_court"]
        assert ids[-1] == "campaign_end_fall_abdication"


class TestTheSurfacesAreReal:
    def test_every_named_shot_is_in_the_manifest_with_its_scene(self, checklist):
        sys.path.insert(0, str(REPO / "tools"))
        import iq10_run_captures as R  # noqa: E402 — the manifest itself
        shots = {s["id"]: s for s in R.SHOTS}
        for s in _surfaces(checklist):
            if s["shot"] is None:
                continue
            assert s["shot"] in shots, f"{s['id']}: the manifest lost its shot"
            assert shots[s["shot"]]["scene"] == s["scene"], s["id"]

    def test_the_freeze_read_the_whole_manifest_of_its_day(self, checklist):
        named = [s for s in _surfaces(checklist) if s["shot"] is not None]
        assert len(named) == 142          # every IQ-10 shot at the freeze, once

    def test_the_unreachable_name_real_scenes_and_no_shot(self, checklist):
        unreachable = {s["id"]: s for s in _surfaces(checklist) if s["shot"] is None}
        assert set(unreachable) == UNREACHABLE
        for s in unreachable.values():
            path = PROJECT / s["scene"].replace("res://", "")
            assert path.is_file(), s["scene"]
            assert "no IQ-10 shot" in s["reach"]

    def test_the_scenes_outside_the_order_exist(self, checklist):
        for scene in checklist["outside_the_order"]["scenes"]:
            assert (PROJECT / scene.replace("res://", "")).is_file(), scene
