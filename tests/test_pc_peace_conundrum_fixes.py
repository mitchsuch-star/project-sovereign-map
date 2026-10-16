"""The Peace Conundrum's conservative fixes — PC-F1, PC-F3, PC-F5, PC-F6
(October 15, 2026; `docs/audits/PEACE_CONUNDRUM_2026_10_15.md` §4 A;
`docs/BUG_FIXES.md` §PC; `SYSTEMS_REFERENCE.md` §120).

  PC-F1  every refusal of a separate peace under the alliance paradox named
         the ally and both ways out; PC-R1 (S13e part 1) retired the stop —
         the pins now read the one verdict ("Bavaria's war with Austria
         ends in this instrument; she takes nothing by it") on the wizard
         rows, the draft's note, the chip, the counsel, the Congress lever.
  PC-F3  the War Status rows show what the peace math reads: the scorer's
         tier (the side pressure on the stored scores, not the live
         aggregate), each court's settlement total out of 50, and the note
         that this turn's victories count from next turn.
  PC-F5  the AI's diplomatic phase reads the war as it stands at the end of
         the turn, not as the last advance left it.
  PC-F6  a decisive exchange is credited only to the side that inflicted it
         and won the field: a pyrrhic victory and a bloody repulse book none;
         a garrison that holds still books a defender victory (the ruling);
         the war panel flags the very battle that was decisive.
"""
from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path

import pytest

from backend.game_logic import diplomacy as D
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCENARIO = REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
SCRIPTS = REPO / "godot-client" / "project-sovereign" / "scripts"

# PC-R1 (S13e part 1): the one verdict's note on the 1805 boot — the leader's
# peace carries Bavaria's pair (she is on France's side of war_1).
BAVARIA_NOTE = "Bavaria's war with Austria ends in this instrument; she takes nothing by it."


@pytest.fixture(scope="module")
def boot() -> WorldState:
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(str(SCENARIO))


@pytest.fixture
def w(boot) -> WorldState:
    return WorldState.from_dict(json.loads(json.dumps(boot.to_dict(), default=str)))


def _rows(world, nation):
    acts = D.get_available_diplomatic_actions(world, nation)
    return acts.get("actions") if isinstance(acts, dict) else acts


# ═══════════════════════════════════════════════════════════════════════════
# PC-F1 — the paradox names the ally and both ways out
# ═══════════════════════════════════════════════════════════════════════════

class TestPCF1:
    """PC-F1 named the ally whose war stopped the separate peace, with both
    ways out. PC-R1 (S13e part 1, October 16, 2026; §46 B + C) retired the
    stop: the paradox is ONE verdict — a peace the leader signs CARRIES the
    ally's pair ("Bavaria's war with Austria ends in this instrument; she
    takes nothing by it"), a peace France does not lead leaves the ally
    fighting at a named price. These pins are re-seated to that wording;
    every surface reads `diplomacy.separate_peace_words`."""

    def test_the_war_page_row_is_open_and_carries_the_note(self, w):
        row = next(a for a in _rows(w, "Austria") if a["action"] == "propose_peace")
        assert row["available"] is True and "closed_clause" not in row
        assert row["separate_peace_display"] == BAVARIA_NOTE

    def test_the_armistice_page_row_is_open_too(self, w):
        with contextlib.redirect_stdout(io.StringIO()):
            D.set_diplomatic_state(w, "France", "Austria", "ARMISTICE", "test_fixture")
        row = next(a for a in _rows(w, "Austria") if a["action"] == "propose_peace")
        assert row["available"] is True
        assert row["separate_peace_display"] == BAVARIA_NOTE

    def test_the_send_roads_verdict_signs(self, w):
        from backend.game_logic.treaty import can_sign
        v = can_sign(w, {"type": "peace", "proposer_nation": "France",
                         "target_nation": "Austria", "sweeteners": [], "demands": [],
                         "clauses": []}, at_send=True)
        assert v.ok and v.clause == ""
        conflicts = D.get_peace_commitment_conflicts(w, "France", "Austria", [])
        carried = [c for c in conflicts if c["conflict_type"] == "carried_in"]
        assert [c["affected_entity"] for c in carried] == ["Bavaria"]
        assert carried[0]["severity"] == "INFO" and carried[0]["display"] == BAVARIA_NOTE
        assert not any(c["severity"] == "HARD_STOP" for c in conflicts)

    def test_the_one_wording_reads_the_carry_in(self, w):
        words = D.separate_peace_words(w, "France", "Austria")
        assert words["carried"] == ["Bavaria"] and words["left"] == []
        assert words["leader"] is True and words["war_id"] == "war_1"
        assert words["display"] == BAVARIA_NOTE == words["chip"]

    def test_two_allies_take_their_own_fates(self, w):
        """Spain at war with Austria OUTSIDE war_1 is left fighting at a price;
        attached to the instance France leads, she is carried in too."""
        from backend.game_logic.settlement_helpers import attach_pair_to_war_instance
        w.diplomatic_states[w._make_diplo_key("Spain", "Austria")] = "WAR"
        words = D.separate_peace_words(w, "France", "Austria")
        assert sorted(words["allies"]) == ["Bavaria", "Spain"]
        assert words["carried"] == ["Bavaria"] and words["left"] == ["Spain"]
        assert words["display"] == (
            f"{BAVARIA_NOTE} Spain stays at war with Austria after this separate peace — "
            f"she fights on alone; it costs {words['price']['Spain']} relation with her.")
        with contextlib.redirect_stdout(io.StringIO()):
            assert attach_pair_to_war_instance(w, "war_1", "Austria", "Spain",
                                               entry_path="test")["ok"]
        words = D.separate_peace_words(w, "France", "Austria")
        assert words["carried"] == ["Bavaria", "Spain"] and words["left"] == []
        assert words["display"] == ("The wars of Bavaria and Spain with Austria end in this "
                                    "instrument; they take nothing by it.")

    def test_a_downgrade_no_longer_decides_anything(self, w):
        """The old second way out: the row is open with or without it."""
        with contextlib.redirect_stdout(io.StringIO()):
            assert D.execute_downgrade(w, "France", "Bavaria")["success"]
            assert D.execute_downgrade(w, "France", "Bavaria")["success"]
        row = next(a for a in _rows(w, "Austria") if a["action"] == "propose_peace")
        assert row["available"] is True
        assert D.separate_peace_words(w, "France", "Austria") == {}   # no ally at war

    def test_the_armistice_signs_as_before(self, w):
        from backend.game_logic.treaty import can_sign
        v = can_sign(w, {"type": D.armistice_variant_for(w, "France", "Austria"),
                         "proposer_nation": "France", "target_nation": "Austria",
                         "sweeteners": [], "demands": [], "clauses": []}, at_send=True)
        assert v.ok

    def test_the_drafts_note_says_what_the_peace_does(self, w):
        from backend.game_logic.diplomatic_dialogue import separate_peace_note_text
        text = separate_peace_note_text(w, "France", "Austria")
        assert text == f"Mark one thing, Sire: {BAVARIA_NOTE}"
        assert "I cannot deliver this" not in text

    def test_the_per_court_chip_is_open_with_the_note(self, w):
        from backend.game_logic import settlement_staging as SS
        from backend.game_logic import settlement_validation as SV
        war_id = next(iter(w.get_war_instances_by_participant("Austria")))
        elig = SV.evaluate_pair_peace_substitute_eligibility(
            w, war_id=war_id, actor_nation="France", target_nation="Austria",
            action="seek_bilateral_peace")
        assert elig["eligible"] is True
        chip = SS.separate_peace_chip(w, "Austria", war_id=war_id, staged_terms=[], actor="France")
        assert chip.get("available", True) is not False
        assert chip["separate_peace_display"] == BAVARIA_NOTE
        assert chip["carried_in"] == ["Bavaria"] and BAVARIA_NOTE in chip["description"]

    def test_the_counsel_says_what_the_peace_does(self, w):
        from backend.game_logic.diplomatic_advisory import _recommend_action
        dlg = _recommend_action("Austria", w)
        assert f"Mark one thing, Sire: {BAVARIA_NOTE}" in dlg["talleyrand_text"]
        assert "would break her war" not in dlg["talleyrand_text"]

    def test_the_congress_peace_lever_reads_the_send_road(self, w):
        from backend.game_logic import congress
        v = congress._lever_verdict(w, "Austria", "PEACE")
        assert v.ok
        assert congress._lever_verdict(w, "Austria", "OPEN_BORDERS").clause != "paradox"

    def test_no_client_copy_hardcodes_the_refusal(self):
        for path in SCRIPTS.glob("*.gd"):
            src = path.read_text(encoding="utf-8")
            assert "an ally's war" not in src, path.name
            assert "diplomatic contradiction" not in src, path.name
            assert "would break her war" not in src, path.name


# ═══════════════════════════════════════════════════════════════════════════
# PC-F6 — the decisive goes to the side that inflicted it
# ═══════════════════════════════════════════════════════════════════════════

def _record(world, *, winner, atk_cas, def_cas, location="Vienna",
            attacker="France", defender="Austria"):
    D.record_battle(world, attacker, defender, winner, atk_cas, def_cas, location)


class TestPCF6:
    def test_massenas_repulse_books_no_decisive(self, w):
        """The live case: the garrison held, Austria lost 8,485 to France's
        2,872 — a defender victory (the ruling), but no decisive for anyone."""
        key = w._make_diplo_key("France", "Austria")
        _record(w, winner="Austria", atk_cas=2872, def_cas=8485)
        rec = w.battle_records[key][-1]
        assert rec["winner"] == "Austria"           # the city stood
        assert not rec.get("decisive")
        assert w.decisive_battles[key] == []
        assert D.calculate_war_score("France", "Austria", w, return_components=True)["decisive"] == 0

    def test_a_winner_who_inflicted_it_books_the_decisive(self, w):
        key = w._make_diplo_key("France", "Austria")
        _record(w, winner="France", atk_cas=3000, def_cas=9000, location="Ulm")
        assert [d["winner"] for d in w.decisive_battles[key]] == ["France"]
        assert w.battle_records[key][-1]["decisive"] is True
        assert w.decisive_battles[key][0]["location"] == "Ulm"

    def test_a_pyrrhic_victory_books_none(self, w):
        key = w._make_diplo_key("France", "Austria")
        _record(w, winner="France", atk_cas=9000, def_cas=3000, location="Aspern")
        assert w.decisive_battles[key] == []

    def test_the_repulse_leaves_the_slot_for_austerlitz(self, w):
        key = w._make_diplo_key("France", "Austria")
        _record(w, winner="Austria", atk_cas=2872, def_cas=8485)
        _record(w, winner="France", atk_cas=3000, def_cas=9000, location="Swabia")
        _record(w, winner="France", atk_cas=4000, def_cas=12000, location="Moravia")
        assert [d["location"] for d in w.decisive_battles[key]] == ["Swabia", "Moravia"]

    def test_the_seam_is_one_predicate(self):
        from backend.game_logic import battle_scale as BS
        assert BS.decisive_credit("France", "Austria", "Austria", 2872, 8485) is None
        assert BS.decisive_credit("France", "Austria", "France", 3000, 9000) == "France"
        assert BS.decisive_credit("France", "Austria", "Austria", 9000, 3000) == "Austria"
        assert BS.decisive_credit("France", "Austria", "France", 9000, 3000) is None
        assert BS.decisive_credit("France", "Austria", "France", 3000, 5000) is None

    def test_the_contribution_reads_the_same_predicate(self, w):
        """The settlement contribution's +25 is the war score's own decisive:
        the repulse earns Austria none, the rout earns France it."""
        from backend.game_logic import war_contribution as WC
        repulse = WC.accrue_battle_contribution(
            w, attacker_nation="France", defender_nation="Austria",
            winner_nation="Austria", attacker_casualties=2872,
            defender_casualties=8485, location="Vienna")
        rout = WC.accrue_battle_contribution(
            w, attacker_nation="France", defender_nation="Austria",
            winner_nation="France", attacker_casualties=3000,
            defender_casualties=9000, location="Ulm")
        assert repulse is not None and repulse["decisive"] is False
        assert rout is not None and rout["decisive"] is True

    def test_the_reward_curve_reads_the_same_predicate(self):
        from backend.game_logic.dotation import is_decisive_victory
        assert is_decisive_victory("attacker_tactical_victory", 3000, 9000) is True
        assert is_decisive_victory("attacker_tactical_victory", 9000, 3000) is False

    def test_the_panel_flags_the_very_battle(self, w):
        """Two assaults the same turn, the same winner: only the decisive one
        wears the star (the panel matched on (turn, winner) and starred both)."""
        from backend.game_logic.war_status import build_active_wars
        _record(w, winner="France", atk_cas=4657, def_cas=8030, location="Vienna")   # 1.7:1
        _record(w, winner="France", atk_cas=2872, def_cas=8485, location="Vienna")   # 2.95:1
        rows = build_active_wars(w)["wars"]
        battles = [b for r in rows for b in (r.get("recent_battles") or [])
                   if b.get("location") == "Vienna"]
        assert len(battles) == 2
        assert sorted(bool(b["decisive"]) for b in battles) == [False, True]


# ═══════════════════════════════════════════════════════════════════════════
# PC-F3 — the war row shows what the peace math reads
# ═══════════════════════════════════════════════════════════════════════════

def _war_row(world):
    from backend.game_logic.war_status import build_active_wars
    with contextlib.redirect_stdout(io.StringIO()):
        rows = build_active_wars(world)["wars"]
    return next(r for r in rows if r.get("status") == "war" and "Austria" in (
        r.get("opponents") or [r.get("opponent")]))


def _stored_pressure(world, opponents):
    from backend.game_logic import settlement_scoring as SC
    war_id = next(iter(world.get_war_instances_by_participant("Austria")))
    instance = world.war_instances[war_id]
    side = instance["side_by_nation"]["France"]
    return SC.compute_side_pressure_score(
        world, instance, proposer_side=side,
        covered_enemy_participants=opponents)["score"]


class TestPCF3:
    def test_the_row_carries_the_tables_reading_and_every_court(self, w):
        row = _war_row(w)
        table = row["peace_table"]
        opponents = row.get("opponents") or [row["opponent"]]
        assert sorted(opponents) == ["Austria", "Britain", "Russia"]
        assert table["pressure"] == _stored_pressure(w, opponents)
        assert row["settlement_tier"] == table["tier"] == D.get_settlement_tier(table["pressure"])
        assert row["settlement_tier_display"] == table["tier_display"]
        assert sorted(c["nation"] for c in table["courts"]) == ["Austria", "Britain", "Russia"]
        assert all(c["threshold"] == 50 for c in table["courts"])
        assert table["lines"][0].startswith(
            f"The peace table reads the war at {table['pressure']} — {table['tier_display']}.")
        assert "A settlement carries only when every court reaches 50 — with no terms:" in (
            table["lines"][0])
        # PC-F37 / PC-F88 (S13e part 1): the averaging and each beaten
        # court's own readiness ride as further lines; no lag note at boot.
        assert table["lag_note"] == "" and len(table["lines"]) >= 1
        assert any(ln.startswith("Court by court: ") and "the table reads their mean" in ln
                   for ln in table["lines"])

    def test_the_court_totals_are_the_settlement_previews_own(self, w):
        from backend.game_logic.settlement_staging import build_settlement_preview
        row = _war_row(w)
        with contextlib.redirect_stdout(io.StringIO()):
            preview = build_settlement_preview(
                w, war_id=row["war_instance_id"], settlement_terms=[],
                actor_nation="France", ignore_active_dialogue=True)
        want = {c["nation"]: c["total"]
                for c in preview["settlement_preview"]["per_court_acceptance"]}
        assert {c["nation"]: c["total"] for c in row["peace_table"]["courts"]} == want

    def test_a_victory_this_turn_moves_the_field_not_the_table(self, w):
        """The live case's shape: the war score climbs on this turn's
        victories while the table — and the tier the row names — wait for
        the advance; the row says so."""
        before = _war_row(w)
        for loc in ("Ulm", "Swabia", "Moravia"):
            D.record_battle(w, "France", "Austria", "France", 3000, 12000, loc)
        mid = _war_row(w)
        table = mid["peace_table"]
        assert mid["war_score"] > before["war_score"]                 # the field moved
        assert table["pressure"] == before["peace_table"]["pressure"]   # the table did not
        assert table["pressure_live"] > table["pressure"]
        assert mid["settlement_tier"] == D.get_settlement_tier(table["pressure"])
        assert table["lag_note"] == (
            f"This turn's battles and captures count from next turn: the table "
            f"reads {table['pressure']} until the turn ends; the field stands at "
            f"{table['pressure_live']}.")
        assert table["lines"][-1] == table["lag_note"]
        # the advance's recalculation catches the table up, and the note goes
        D.recalculate_war_scores(w)
        after = _war_row(w)["peace_table"]
        assert after["pressure"] == after["pressure_live"] == table["pressure_live"]
        assert after["lag_note"] == ""

    def test_the_side_follows_the_tables_number(self, w):
        from backend.game_logic.war_status import _tier_side
        row = _war_row(w)
        assert row["settlement_tier_side"] == _tier_side(row["peace_table"]["pressure"])

    def test_the_hud_tooltip_and_the_popup_print_the_tables_lines(self):
        panel = (SCRIPTS / "war_status_panel.gd").read_text(encoding="utf-8")
        body = panel[panel.index("func _build_war_tooltip"):]
        assert 'war_data.get("peace_table", null)' in body
        assert 'peace_table.get("lines", [])' in body
        popup = (SCRIPTS / "war_detail_popup.gd").read_text(encoding="utf-8")
        body = popup[popup.index("func _render_war_detail"):]
        body = body[:body.index("\nfunc ")]
        assert 'w.get("peace_table", null)' in body
        assert 'peace_table.get("lines", [])' in body


# ═══════════════════════════════════════════════════════════════════════════
# PC-F5 — the AI's diplomatic phase reads the war as the turn ends
# ═══════════════════════════════════════════════════════════════════════════

class TestPCF5:
    def test_the_seam_brings_the_stored_score_to_the_field(self, w):
        from backend.game_logic import turn_manager as TM
        D.record_battle(w, "France", "Austria", "France", 3000, 12000, "Ulm")
        live = D.calculate_war_score("France", "Austria", w)
        assert D.get_war_score_for(w, "France", "Austria") != live
        TM.ai_phase_reads_the_field(w)
        assert D.get_war_score_for(w, "France", "Austria") == live

    def test_end_turn_runs_it_before_the_ai_phase(self, w, monkeypatch):
        """The phase itself, inside a real end turn, reads the score the
        field shows — not the one the last advance stored."""
        from backend.game_logic import turn_manager as TM
        for loc in ("Ulm", "Swabia"):
            D.record_battle(w, "France", "Austria", "France", 3000, 12000, loc)
        seen = {}

        def _phase(self):
            seen["stored"] = D.get_war_score_for(self.world, "Austria", "France")
            seen["live"] = D.calculate_war_score("Austria", "France", self.world)
            return None

        monkeypatch.setattr(TM.TurnManager, "_process_ai_diplomatic_phase", _phase)
        with contextlib.redirect_stdout(io.StringIO()):
            TM.TurnManager(w).end_turn({"world": w})
        assert seen, "the AI diplomatic phase never ran"
        assert seen["stored"] == seen["live"] < 0

    def test_the_seam_sits_before_the_phase_in_the_source(self):
        import inspect
        from backend.game_logic import turn_manager as TM
        src = inspect.getsource(TM.TurnManager.end_turn)
        assert src.index("ai_phase_reads_the_field(self.world)") < src.index(
            "self._process_ai_diplomatic_phase()")


# ═══════════════════════════════════════════════════════════════════════════
# PC-F6 — a pre-fix save's misbooked decisive is dropped on load
# ═══════════════════════════════════════════════════════════════════════════

class TestPCF6TheSaveRepair:
    def _legacy(self, w, *, winner, atk_cas, def_cas, location):
        key = w._make_diplo_key("France", "Austria")
        w.battle_records.setdefault(key, []).append({
            "turn": int(w.current_turn), "winner": winner, "attacker": "France",
            "defender": "Austria", "attacker_casualties": atk_cas,
            "defender_casualties": def_cas, "location": location, "battle_name": ""})
        ratio = max(atk_cas, def_cas) / min(atk_cas, def_cas)
        w.decisive_battles.setdefault(key, []).append({
            "turn": int(w.current_turn), "winner": winner,
            "total_casualties": atk_cas + def_cas, "ratio": round(ratio, 1)})
        return key

    def test_the_vienna_repulse_is_dropped_and_a_true_decisive_kept(self, w):
        key = self._legacy(w, winner="France", atk_cas=3000, def_cas=9000, location="Ulm")
        self._legacy(w, winner="Austria", atk_cas=2872, def_cas=8485, location="Vienna")
        assert len(w.decisive_battles[key]) == 2
        with contextlib.redirect_stdout(io.StringIO()):
            loaded = WorldState.from_dict(json.loads(json.dumps(w.to_dict(), default=str)))
        assert [d["winner"] for d in loaded.decisive_battles[key]] == ["France"]

    def test_a_decisive_whose_battle_was_pruned_is_kept(self, w):
        key = w._make_diplo_key("France", "Austria")
        w.decisive_battles.setdefault(key, []).append(
            {"turn": 1, "winner": "Austria", "total_casualties": 11357, "ratio": 3.0})
        with contextlib.redirect_stdout(io.StringIO()):
            loaded = WorldState.from_dict(json.loads(json.dumps(w.to_dict(), default=str)))
        assert loaded.decisive_battles[key] == w.decisive_battles[key]



# ═══════════════════════════════════════════════════════════════════════════
# The series — PC-F5 and PC-F6 attributed against BASELINE_SERIES
# ═══════════════════════════════════════════════════════════════════════════

class TestTheSeries:
    """`tools/_pc_series_arms.py` (record `tools/_pc_series_arms_final.json`):
    arm 0 (both seams down) reproduces DD-B's shipped series byte for byte,
    and so does every other arm — BASELINE_SERIES does not move. The reach
    says both seams were met: the AI phase read a moved score on 29 of 35
    phases (68 pair scores), and two decisive exchanges won by the side that
    bled were no longer credited."""

    def _records(self):
        tools = REPO / "tools"
        pc = json.loads((tools / "_pc_series_arms_final.json").read_text(encoding="utf-8"))
        ddb = json.loads((tools / "_ddb_s13b_series_arms_final.json").read_text(encoding="utf-8"))
        return pc, ddb

    def test_the_record_links_to_the_last_one_and_the_baseline(self):
        import sys as _sys
        _sys.path.insert(0, str(REPO / "tests"))
        from test_ai_intent_threat_migration import BASELINE_SERIES
        pc, ddb = self._records()
        assert pc["prior"] == ddb["arms"]["ALL"]["series"]
        assert pc["arms"]["0"]["series"] == pc["prior"]
        assert BASELINE_SERIES == pc["arms"]["ALL"]["series"]
        for arm, rec in pc["arms"].items():
            assert rec["first_divergence_vs_prior"] is None, arm

    def test_both_seams_were_reached(self):
        pc, _ddb = self._records()
        reach = {arm: rec["reach"] for arm, rec in pc["arms"].items()}
        assert reach["L"]["ai_phase_pairs_moved"] > 0
        assert reach["0"]["ai_phase_pairs_moved"] == 0
        assert reach["E"].get("decisive_exchange|winner_bled|False", 0) > 0
        assert reach["0"].get("decisive_exchange|winner_bled|True", 0) > 0
