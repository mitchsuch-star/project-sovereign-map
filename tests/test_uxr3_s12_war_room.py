"""UXR-3 fixes — Pre-Deploy S12 part 2, parts 2 and 3: the R6 driven proofs
(October 14, 2026).

R6 counts a HANDOFF control (its only answer an API call or a signal outward)
and a NOT PRESSED control (save, load, new campaign, main menu, quit) only
where a live-backend driven record shows its road's visible answer. This is
that record: the action probe's WAR-ROOM mode (`tools/uxr3_action_probe.py
--war-room`) opens each hand-off surface INSIDE the real `main.tscn`, whose
real client talks to a sandboxed backend (an unused port from 8006, its own
save directory, the mock parser — never the player's 8005), presses the road's
control, and reads the war room's LIVE frame for 500 ms and 30 frames: a change
under a standing modal screen (the terminal's echo beneath the Generals) is no
answer. A quit is proven by the engine exiting cleanly after the press.

The run is a driven session like Mode C's, and like the action probe's record
it is committed (`docs/audits/uxr3_s12b/war_room.json`) and re-run by the
closing re-read on the tree it reads; it is not re-run in every hook (three
and a half minutes of engine time). These pins hold the citations to it: every
road answered on screen, the backend was never the player's, the save wrote a
file, the Main Menu stood, a quit closed the window, a chip under a screen
greyed to "Sent", and every citation in `live_citations.json` names its road's
record and matches the road's own control.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
TOOLS = REPO / "tools"
RECORDS = REPO / "docs" / "audits" / "uxr3_s12b"
sys.path.insert(0, str(TOOLS))

import uxr3_action_probe as PROBE  # noqa: E402

ROAD_IDS = [r[0] for r in PROBE.ROADS]
RECORD = "docs/audits/uxr3_s12b/war_room.json"


def _load(name: str) -> dict:
    path = RECORDS / name
    assert path.is_file(), f"the committed record is missing: {path}"
    return json.loads(path.read_text(encoding="utf-8"))


def _control(war: dict, road: str) -> dict:
    rec = war["roads"][road]
    assert rec.get("reached"), (road, rec.get("errors"))
    assert rec["controls"], (road, "no control matched the road", rec.get("errors"))
    return rec["controls"][0]


class TestEveryRoadAnswersInTheLiveFrame:
    def test_every_road_was_pressed_and_answered_on_screen(self):
        war = _load("war_room.json")
        assert set(war["roads"]) == set(ROAD_IDS), sorted(set(ROAD_IDS) ^ set(war["roads"]))
        for road in ROAD_IDS:
            c = _control(war, road)
            assert c["result"] == "VISIBLE", (road, c.get("result"), c.get("changes"), c.get("signals"))
            assert not c.get("script_errors"), (road, c["script_errors"])

    def test_the_backend_was_never_the_players(self):
        war = _load("war_room.json")
        assert war["tool"] == "tools/uxr3_action_probe.py --war-room"
        assert not re.search(r":8005\b", war["backend"]), war["backend"]
        for rec in war["roads"].values():
            assert not str(rec.get("backend", "")).endswith(":8005"), rec.get("backend")

    def test_save_went_through_the_real_save_road(self):
        war = _load("war_room.json")
        c = _control(war, "pause_save")
        assert any("Saving game" in ch or "saved successfully" in ch for ch in c["changes"]), c["changes"]
        assert "quicksave.json" in war.get("saves_written", []), war.get("saves_written")

    def test_load_opens_the_load_dialog(self):
        c = _control(_load("war_room.json"), "pause_load")
        assert any("shown" in ch for ch in c["changes"]), c["changes"]

    def test_the_main_menu_stands_after_the_change(self):
        war = _load("war_room.json")
        for road in ("pause_main_menu", "fall_main_menu"):
            c = _control(war, road)
            assert c["changes"][0] == "the scene -> main_menu.tscn", (road, c["changes"][:3])

    def test_a_quit_closes_the_window(self):
        war = _load("war_room.json")
        for road in ("pause_quit", "menu_quit"):
            c = _control(war, road)
            assert c.get("engine_exit") == 0, (road, c)
            assert "the window closed" in c["changes"][0], (road, c)

    def test_a_chip_under_a_screen_greys_to_sent(self):
        """The chips whose order's echo lies under their screen answer in
        place: the Generals' order, the vassal chip, the law and the
        Admiralty chips, the Orders tab's Cancel."""
        war = _load("war_room.json")
        for road in ("generals_order", "diplo_vassal", "ledger_law", "ledger_admiralty", "ledger_cancel"):
            c = _control(war, road)
            assert any("Sent: " in ch for ch in c["changes"]), (road, c["changes"])


class TestEveryRoadIsCited:
    def test_the_citations_name_every_roads_record(self):
        cits = _load("live_citations.json")["citations"]
        cited = {c["road"]: c for c in cits if c.get("road")}
        assert set(cited) == set(ROAD_IDS), sorted(set(ROAD_IDS) ^ set(cited))
        for road, c in cited.items():
            assert c["cite"] == f"{RECORD} roads.{road} (tools/uxr3_action_probe.py --war-room)", c
        # S11's citation is carried
        assert any(c.get("match", {}).get("text") == "Load a campaign" for c in cits)

    def test_each_citation_matches_its_roads_own_control(self):
        cits = {c["road"]: c for c in _load("live_citations.json")["citations"] if c.get("road")}
        for road, sid, match in PROBE.ROADS:
            assert cits[road]["match"] == match, (road, cits[road]["match"], match)

    def test_the_record_is_the_closing_rereads_tree(self):
        """The record and the closing re-read's probe read the same tree."""
        war = _load("war_room.json")
        probe = _load("probe.json")
        assert war["client_commit"] and war["client_commit"] == probe["client_commit"]


class TestTheProbeKeepsItsWarRoomRails:
    def test_the_war_room_refuses_8005_and_sandboxes_its_saves(self):
        gd = (TOOLS / "uxr3_action_probe.gd").read_text(encoding="utf-8")
        assert ('if _war_room and Utils.backend_url().ends_with(":8005"):' in gd)
        runner = (TOOLS / "uxr3_action_probe.py").read_text(encoding="utf-8")
        assert "while port == 8005 or not _free(port):" in runner
        assert '"INK_IRON_SAVE_DIR": str(saves)' in runner and '"LLM_MODE": "mock"' in runner
        assert 'assert env["SOVEREIGN_PORT"] != "8005"' in runner

    def test_a_war_room_answer_is_read_in_the_live_frame_only(self):
        gd = (TOOLS / "uxr3_action_probe.gd").read_text(encoding="utf-8")
        assert "changed = _live_only(changed, [before, a2, a3])" in gd
        live = re.search(r"(?ms)^func _live_only\(.*?(?=^func )", gd).group(0)
        assert "floor_now = mini(floor_now" in live
        assert "int(layers.get(key.substr(2), 0)) >= floor_now" in live
