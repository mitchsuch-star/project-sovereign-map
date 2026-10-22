"""RR6-X3 — ONE SIGHTING RULE (Pre-Deploy S14b's head, October 21, 2026).

Measured on the slice tree's FLD arm, turn 7: the enemy-phase dialog showed
Archduke John take Provence (PT-E5), the desk answered "Ney stands at Munich,
beyond reach of Archduke John at Provence", and the very next line
`Ney, attack Archduke John` answered "No intelligence on Archduke John's
position" — the order read the intel store's snapshots alone, Provence's was
turn 6's own-soil read (empty), and no shown action wrote a sighting.

Ruled (BUG_FIXES §RR6, SYSTEMS_REFERENCE §142): `intel_surfaces.last_seen` is
the one answer — (1) a corps IN SIGHT (his own province reads PARTIAL or
better: the map's rule) is placed where he stands; (2) out of sight, his
newest sighting, each snapshot entry its own turn; (3) the store learns what
the dialog SHOWED (`record_shown_sightings`, at the end turn, before the
dispatch and the autosave). The order, its per-turn gate, the cautious
objection, the desk, the dispatch, the Ledger, the status report and the map
read it. Siblings RR6-X4 … X8 (the sweep) pinned beside it.
"""
import contextlib
import io

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.commands import disobedience as DS
from backend.commands.parser import CommandParser
from backend.game_logic import enemy_phase_fog as EPF
from backend.game_logic import intel_surfaces as IS
from backend.game_logic.turn_manager import TurnManager
from backend.models.intel import FULL, PARTIAL, SEEN_TURN_KEY, STALE, UNKNOWN


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture
def shipped(monkeypatch):
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    with _quiet():
        M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    return TestClient(M.app), M.world


def post(client, command):
    with _quiet():
        return client.post("/command", json={"command": command}).json()


def _conquest_phase():
    """The FLD arm's turn-6 action, as the AI's executor returns it."""
    return {
        "nations": {"Austria": {"actions": [{
            "ai_action": {"marshal": "ArchdukeJohn", "action": "attack",
                          "target": "Provence", "walk_in": True},
            "events": [{"type": "conquest", "marshal": "ArchdukeJohn",
                        "region": "Provence", "unopposed": True,
                        "captured_by": "Austria", "captured_from": "France",
                        "capture_choice": "secure"}],
        }], "action_count": 1}},
        "total_actions": 1,
        "summary": [],
    }


def _stage_the_capture(monkeypatch, world, record=True):
    """The enemy phase takes Provence for Archduke John (Provence's three
    neighbours hold no French corps, so nothing reads it after the capture),
    then stands still on every later turn."""
    state = {"done": False}

    def _phase(self, game_state):
        if state["done"]:
            return {"nations": {}, "total_actions": 0, "summary": []}
        state["done"] = True
        john = world.marshals["ArchdukeJohn"]
        john.location = "Provence"
        world.regions["Provence"].controller = "Austria"
        world._build_marshal_index()
        return _conquest_phase()

    monkeypatch.setattr(TurnManager, "_process_enemy_turns", _phase)
    if not record:
        monkeypatch.setattr(IS, "record_shown_sightings", lambda world, shown: 0)


# ═══════════════════════════════════════════════════════════════════════════
# The reproduction, through the real endpoint
# ═══════════════════════════════════════════════════════════════════════════

class TestTheOrderPlacesHimWhereTheDeskDoes:

    def test_the_dialog_shows_the_capture_and_the_store_learns_it(self, shipped, monkeypatch):
        client, world = shipped
        _stage_the_capture(monkeypatch, world)
        r = post(client, "end turn")
        shown = (r.get("enemy_phase") or {}).get("nations", {}).get("Austria", {}).get("actions", [])
        assert [a["ai_action"]["marshal"] for a in shown] == ["ArchdukeJohn"]
        entry = next(km for km in world.intel["Provence"].known_marshals
                     if km["name"] == "ArchdukeJohn")
        assert entry[SEEN_TURN_KEY] == world.current_turn
        # the province's own read and label untouched — decay ages it as before
        assert world.intel["Provence"].last_updated_turn == world.current_turn - 1
        assert world.intel["Provence"].visibility == PARTIAL

    def test_the_morning_after_the_desk_and_the_order_agree(self, shipped, monkeypatch):
        client, world = shipped
        _stage_the_capture(monkeypatch, world)
        post(client, "end turn")
        seen = IS.last_seen(world, "France", "ArchdukeJohn")
        assert (seen["location"], seen["source"]) == ("Provence", "live")
        where = post(client, "where is Archduke John")["message"]
        assert "Provence" in where
        order = post(client, "Ney, attack Archduke John")
        assert order.get("clarification_kind") == "pursuit_ask", order.get("message")
        assert order["message"].startswith("Archduke John stands at Provence"), order["message"]
        rows = [x for x in world.last_morning_dispatch.get("intelligence", [])
                if x.get("roster_name") == "ArchdukeJohn"]
        assert [(x["location"], x["source"]) for x in rows] == [("Provence", "live")]

    def test_once_the_label_decays_he_is_last_seen_at_provence(self, shipped, monkeypatch):
        client, world = shipped
        _stage_the_capture(monkeypatch, world)
        for _ in range(3):
            post(client, "end turn")
        assert world.intel["Provence"].visibility == STALE
        seen = IS.last_seen(world, "France", "ArchdukeJohn")
        assert (seen["location"], seen["source"], seen["visibility"]) == ("Provence", "snapshot", STALE)
        order = post(client, "Ney, attack Archduke John")
        assert order.get("clarification_kind") == "pursuit_ask", order.get("message")
        # RR6-X5: out of sight, the ask says where he was LAST SEEN
        assert order["message"].startswith("Archduke John was last seen at Provence 2 turns ago"), order["message"]
        where = post(client, "where is Archduke John")["message"]
        assert "last reported at Provence, 2 turns ago" in where, where
        # RR6-X6: the what-if names the same sighting, never "no word"
        what_if = post(client, "what are Ney's odds against Archduke John")["message"]
        assert "last reported at Provence, 2 turns ago" in what_if, what_if
        assert "no word" not in what_if.lower()

    def test_the_morning_names_who_took_provence(self, shipped, monkeypatch):
        """Rule 3's visible half: the home-captured line reads the province's
        snapshot for who stands there — with the dialog's sighting written,
        "Archduke John's corps of ~10,000 stands there"; without, nobody."""
        from backend.game_logic import dispatch as D
        client, world = shipped
        _stage_the_capture(monkeypatch, world)
        post(client, "end turn")
        assert "Archduke John's corps" in D._home_captured_lever(world, "Provence", "France", None)

    def test_seam_down_the_morning_named_nobody(self, shipped, monkeypatch):
        from backend.game_logic import dispatch as D
        client, world = shipped
        _stage_the_capture(monkeypatch, world, record=False)
        post(client, "end turn")
        assert "Archduke John" not in D._home_captured_lever(world, "Provence", "France", None)

    def test_seam_down_the_order_had_no_intelligence(self, shipped, monkeypatch):
        """Rule 3's seam: with the dialog's sightings unwritten, the decayed
        label leaves the order nothing — the FLD arm's answer, reproduced."""
        client, world = shipped
        _stage_the_capture(monkeypatch, world, record=False)
        for _ in range(3):
            post(client, "end turn")
        assert IS.last_seen(world, "France", "ArchdukeJohn") is None
        order = post(client, "Ney, attack Archduke John")
        assert "No intelligence on Archduke John's position" in order["message"], order["message"]


# ═══════════════════════════════════════════════════════════════════════════
# Rule 1 — in sight is the map's rule, for every reader
# ═══════════════════════════════════════════════════════════════════════════

def _walk_in_unread(world):
    """Archduke John stands at Provence under a PARTIAL label whose snapshot
    is empty (the province's read predates him) — the FLD turn-7 shape."""
    world.marshals["ArchdukeJohn"].location = "Provence"
    world._build_marshal_index()
    intel = world.intel["Provence"]
    intel.visibility, intel.known_marshals = PARTIAL, []
    for other in world.intel.values():
        other.known_marshals = [km for km in other.known_marshals
                                if km.get("name") != "ArchdukeJohn"]
    return world.marshals["ArchdukeJohn"]


class TestRuleOneInSight:

    def test_every_reader_places_him_at_provence(self, shipped):
        _client, world = shipped
        john = _walk_in_unread(world)
        assert world.get_last_known_location("ArchdukeJohn") is None   # the store alone
        from backend.commands.strategic import pursue_known_location
        assert pursue_known_location(world, world.marshals["Ney"], john) == "Provence"
        row = next(s for s in IS.enemy_sightings(world, "France") if s["roster_name"] == "ArchdukeJohn")
        assert (row["location"], row["source"], row["visibility"]) == ("Provence", "live", PARTIAL)
        from backend.intel_report import generate_intel_report
        with _quiet():
            report = generate_intel_report(world)
        listed = [r["region"] for r in report["recent_reports"]
                  if any(k.get("name") == "ArchdukeJohn" for k in r.get("known_marshals") or [])]
        assert listed == ["Provence"]

    def test_seam_down_the_order_reads_the_store_alone(self, shipped, monkeypatch):
        _client, world = shipped
        john = _walk_in_unread(world)
        monkeypatch.setattr(IS, "in_sight", lambda world, viewer, man: False)
        from backend.commands.strategic import pursue_known_location
        assert pursue_known_location(world, world.marshals["Ney"], john) is None

    def test_the_status_report_lists_a_man_once(self, shipped):
        """A man in sight at one PARTIAL province was also listed at the
        province his older snapshot named."""
        _client, world = shipped
        john = world.marshals["ArchdukeJohn"]
        old = world.intel["Tyrol"]
        assert any(k.get("name") == "ArchdukeJohn" for k in old.known_marshals)
        _walk_in_unread(world)
        old.known_marshals = [{"name": "ArchdukeJohn", "nation": "Austria", "band": "substantial force"}]
        from backend.intel_report import generate_intel_report
        with _quiet():
            report = generate_intel_report(world)
        listed = [r["region"] for r in report["recent_reports"] + report["last_known"]
                  if any(k.get("name") == john.name for k in r.get("known_marshals") or [])]
        assert listed == ["Provence"], listed

    def test_a_snapshot_of_a_man_who_left_a_province_in_sight_keeps_its_word(self, shipped):
        _client, world = shipped
        john = world.marshals["ArchdukeJohn"]
        unseen = next(r for r, i in sorted(world.intel.items()) if i.visibility == UNKNOWN)
        john.location = unseen
        world._build_marshal_index()
        tyrol = world.intel["Tyrol"]
        assert tyrol.visibility == PARTIAL
        tyrol.known_marshals = [{"name": "ArchdukeJohn", "nation": "Austria", "band": "substantial force"}]
        seen = IS.last_seen(world, "France", "ArchdukeJohn")
        assert (seen["location"], seen["source"]) == ("Tyrol", "snapshot")
        # the place moves to the rule; a PARTIAL report keeps its tier
        assert seen["visibility"] == PARTIAL


# ═══════════════════════════════════════════════════════════════════════════
# Rule 3 — what the dialog shows, and only that
# ═══════════════════════════════════════════════════════════════════════════

class TestRuleThreeTheDialogsSightings:

    def test_the_end_turn_reads_the_dialogs_own_predicate(self):
        assert M._filter_enemy_phase_by_visibility is EPF.filter_enemy_phase_by_visibility
        assert M._own_soil_event_types is EPF.own_soil_event_types

    def test_a_hidden_action_writes_nothing(self, shipped):
        _client, world = shipped
        john = world.marshals["ArchdukeJohn"]
        unseen = next(r for r, i in sorted(world.intel.items()) if i.visibility == UNKNOWN)
        john.location = unseen
        world._build_marshal_index()
        phase = {"nations": {"Austria": {"actions": [{
            "ai_action": {"marshal": "ArchdukeJohn", "action": "move", "target": unseen},
            "events": [{"type": "move", "marshal": "ArchdukeJohn", "from": "Tyrol", "to": unseen}],
        }]}}}
        shown = EPF.shown_enemy_phase(phase, world)
        assert not shown["nations"]
        assert IS.record_shown_sightings(world, shown) == 0

    def test_a_battles_retreat_places_nobody(self, shipped):
        """The dialog never prints a battle's retreat road — so the store
        does not learn it."""
        _client, world = shipped
        action = {"ai_action": {"marshal": "ArchdukeJohn", "action": "attack", "target": "Ney"},
                  "events": [{"type": "retreat", "marshal": "ArchdukeJohn", "to": "Carniola"}]}
        assert IS._shown_place(world, action, "ArchdukeJohn") is None or \
            world.intel[world.marshals["ArchdukeJohn"].location].visibility == FULL

    def test_a_read_of_this_turn_outranks_the_dialog(self, shipped):
        _client, world = shipped
        world.marshals["ArchdukeJohn"].location = "Provence"
        world._build_marshal_index()
        world.intel["Provence"].known_marshals = []
        turn = int(world.current_turn)
        world.intel["Lyonnais"].last_updated_turn = turn
        world.intel["Lyonnais"].known_marshals = [{"name": "ArchdukeJohn", "nation": "Austria", "band": "small force"}]
        assert IS.record_shown_sightings(world, _conquest_phase()) == 0


# ═══════════════════════════════════════════════════════════════════════════
# The siblings (RR6-X4 … X8)
# ═══════════════════════════════════════════════════════════════════════════

class TestTheSiblings:

    def test_rr6_x4_the_cautious_scout_names_the_last_seen_province(self, shipped, monkeypatch):
        _client, world = shipped
        john = world.marshals["ArchdukeJohn"]
        unseen = next(r for r, i in sorted(world.intel.items()) if i.visibility == UNKNOWN)
        john.location = unseen
        world._build_marshal_index()
        tyrol = world.intel["Tyrol"]
        tyrol.visibility, tyrol.last_updated_turn = STALE, int(world.current_turn) - 4
        tyrol.known_marshals = [{"name": "ArchdukeJohn", "nation": "Austria", "band": "substantial force"}]
        from backend.commands import severity as SEV
        monkeypatch.setattr(SEV, "calculate_strategic_severity", lambda *a, **k: 0.9)
        davout = world.marshals["Davout"]
        objection = DS.check_strategic_objection(
            davout, "PURSUE", "ArchdukeJohn", [], world, {"world": world}, include_variance=False)
        assert objection and objection["reason"] == "davout_pursue_stale_intel", objection
        scout = next(o for o in objection["options"] if o.get("type") == "preferred")
        assert (scout["action"], scout["target"]) == ("scout", "Tyrol"), scout
        assert scout["text"] == "Trust: Davout scouts Tyrol", scout["text"]
        assert unseen not in str(objection)

    def test_rr6_x10_the_muster_bands_a_man_in_sight(self, shipped, monkeypatch):
        """The muster's fog band read the province's snapshot, which predates
        a man who walked in: "strength unknown" over a corps the map draws
        and the desk bands "small force"."""
        from backend.commands.combat_executor import CombatExecutor
        _client, world = shipped
        john = _walk_in_unread(world)
        world.intel["Provence"].strength_band = "no forces"
        shown = CombatExecutor._fog_banded_strength(john, world)
        assert shown == "substantial force", shown
        from backend.ai import question_desk as Q
        assert shown in Q._answer_enemy(world, "where", "ArchdukeJohn")
        monkeypatch.setattr(IS, "in_sight", lambda world, viewer, man: False)
        assert CombatExecutor._fog_banded_strength(john, world) == "strength unknown"

    def test_rr6_x11_who_is_at_provence_names_him(self, shipped):
        _client, world = shipped
        _walk_in_unread(world)
        from backend.ai import question_desk as Q
        answer = Q._answer_region(world, "who_at", "Provence")
        assert "Reported: Archduke John — substantial force, this turn." in answer, answer
        assert "No army stands" not in answer

    def test_rr6_x7_the_map_draws_no_man_who_walked_into_a_stale_province(self, shipped):
        _client, world = shipped
        john = world.marshals["ArchdukeJohn"]
        tyrol = world.intel["Tyrol"]
        # he walked into Provence unseen; Provence's label is stale and empty
        john.location = "Provence"
        world._build_marshal_index()
        prov = world.intel["Provence"]
        prov.visibility, prov.known_marshals = STALE, []
        tyrol.known_marshals = []
        summary = world.get_filtered_game_state_summary()
        assert not summary["map_data"]["Provence"]["fogged_forces"]
        assert "ArchdukeJohn" not in summary["enemies"]
        # the man last SEEN there is drawn, at the band he was seen at
        prov.known_marshals = [{"name": "ArchdukeJohn", "nation": "Austria", "band": "large force"}]
        summary = world.get_filtered_game_state_summary()
        ghosts = summary["map_data"]["Provence"]["fogged_forces"]
        assert [(g["name"], g["strength_band"], g["fog_level"]) for g in ghosts] == \
            [("ArchdukeJohn", "large force", STALE)]
        assert summary["enemies"]["ArchdukeJohn"]["location"] == "Provence"
        assert summary["enemies"]["ArchdukeJohn"]["fog_level"] == STALE

    def test_rr6_x8_a_stale_province_is_out_of_sight(self, shipped):
        client, world = shipped
        john = world.marshals["ArchdukeJohn"]
        john.location = "Provence"
        world._build_marshal_index()
        world.intel["Provence"].visibility = STALE
        assert world.get_visible_enemies_in_region("Provence", "France") == []
        with _quiet():
            r = client.get("/march_quotes", params={"marshal": "Massena", "enemy": "ArchdukeJohn"}).json()
        assert r.get("success") is False and "in sight" in str(r.get("message")), r
        world.intel["Provence"].visibility = PARTIAL
        assert [x["name"] for x in world.get_visible_enemies_in_region("Provence", "France")] == ["ArchdukeJohn"]


class TestRR6X9TheQuoteCannotKnowTheEnemysMarch:
    """Economy C3's verdict (the instrument): a turn whose enemy phase took
    French provinces is explained as a battle is — measured on the moved CMD-H
    arm's turn 30, two walk-ins (no battle, no materiel) drop the Emperor's
    grip under 70 and the "grip falters" term's +50 rate points bill 375
    against a 331 quote."""

    def _verdict(self, rows):
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from tools import _score_probes as P
        return P.economy_c3_verdict(rows)

    def test_a_turn_that_lost_provinces_is_explained(self):
        v = self._verdict([(10, 325, 325, 0, 0, 0, 0), (30, 331, 375, 0, 0, 0, 2)])
        assert v["measured"] and v["pass"], v
        assert "explained by the end turn's own battles or captures" in v["evidence"]

    def test_a_six_column_row_reads_as_before(self):
        v = self._verdict([(10, 325, 325, 0, 0, 0), (30, 331, 375, 0, 0, 0)])
        assert v["pass"] is False and "mismatches on battle-free turns" in v["evidence"]

