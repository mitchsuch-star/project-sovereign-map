"""GE-V "the played campaign" (ENDGAME_PLAN §6 + §2.8, September 25, 2026).

The played reach from the 1805 boot to the Congress was measured on the
committed driver (memo `docs/audits/GE_V_PLAYED_CAMPAIGN_2026_09_25.md`)
and what the play exposed is pinned here, beside the plan's own rule:

1. **A court is subjugated by fiat only once BEATEN.** The first probe typed
   `vassalize Austria` on turn 1, no battle fought, and a great power at war
   became a French puppet — three archdukes assimilated. The unilateral verb
   now needs the war to have decided it (`vassal.subjugation_refusal`); the
   peace table's signed clause arrives with `by_treaty=True`.
2. **hold_titled 50 → 45** — §2.8's rule ("if it cannot reach 50 by turn 40")
   fired: the reach measured 41 at best and 35 at turn 12 on both openings.
3. **GE-D2 "The Guard is Spent", RULED and built:** the toll respects
   `GUARD_SPENT_FLOOR` (1,000 men), so the Emperor is ASKED before the fatal
   battle instead of paid down to a remnant the next defeat annihilates.
4. **`invest in <eliminated court>`** is answered as a court that is gone,
   never as a marshal's name (measured: "which marshal should act? Try:
   'Ney, attack Bavaria'").
5. **The driver's `--settlement` and `--decline-from` dials** — the harness
   changes the measurement needed (an accepting arm that refuses the
   league's table and the armistice of the court it is conquering).

Every `/command` pin drives the real endpoint on the shipped 1805 board.
"""

import contextlib
import io
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.commands.parser import CommandParser
from backend.game_logic import congress, vassal as V
from tests._chip_census import board_env

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def board(monkeypatch):
    board_env(monkeypatch)
    yield TestClient(M.app)
    with contextlib.redirect_stdout(io.StringIO()):
        M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))


def _post(client, sentence):
    return client.post("/command", json={"command": sentence}).json()


def _eliminate(world, nation, to="Austria"):
    """Stage an elimination the way the board does it: every province lost
    (R81: 0 regions = eliminated), then the teardown."""
    for name in list(world.get_nation_regions(nation) or []):
        world.regions[name].controller = to
    world.invalidate_active_nations_cache()
    with contextlib.redirect_stdout(io.StringIO()):
        world._eliminate_nation(nation)
    world.invalidate_active_nations_cache()


# ═══════════════════════════════════════════════════════════════════════════
# 1. A court is subjugated by fiat only once BEATEN
# ═══════════════════════════════════════════════════════════════════════════
class TestACourtIsSubjugatedOnlyWhenBeaten:
    def test_the_boot_refuses_to_subjugate_austria_with_a_word(self, board):
        world = M.world
        assert world.get_diplomatic_state("France", "Austria") == "WAR"
        response = _post(board, "vassalize Austria")
        assert response.get("success") is False
        assert "still stands" in response.get("message", "")
        assert "peace table" in response.get("message", "")
        assert "Austria" not in world.vassals
        assert world.get_diplomatic_state("France", "Austria") == "WAR"
        for name in ("Mack", "ArchdukeCharles", "ArchdukeJohn"):
            assert world.marshals[name].nation == "Austria", name

    def test_the_refusal_names_the_three_roads(self, board):
        message = _post(board, "subjugate Austria").get("message", "")
        assert "Vienna is its own" in message
        assert "corps are in the field" in message
        assert f"submits at {V.SUBJUGATION_WAR_SCORE:+d}" in message

    def test_the_capital_held_admits_it(self, board):
        world = M.world
        world.regions["Vienna"].controller = "France"
        world.invalidate_active_nations_cache()
        assert V.subjugation_refusal(world, "France", "Austria") == ""
        response = _post(board, "vassalize Austria")
        assert response.get("success") is True, response.get("message")
        assert world.vassals["Austria"]["path"] == "conquest"

    def test_the_capital_held_by_a_satellite_of_the_bloc_admits_it(self, board):
        world = M.world
        world.regions["Vienna"].controller = "KingdomOfItaly"
        world.invalidate_active_nations_cache()
        assert V.subjugation_refusal(world, "France", "Austria") == ""

    def test_the_war_score_admits_it(self, board):
        world = M.world
        # The stored score is the alphabetically-first court's view:
        # "Austria|France" at -40 = Austria beaten to the sue line.
        world.war_scores[world._make_diplo_key("France", "Austria")] = -40
        assert V.subjugation_refusal(world, "France", "Austria") == ""
        assert _post(board, "vassalize Austria").get("success") is True

    def test_a_war_score_short_of_the_line_does_not(self, board):
        world = M.world
        world.war_scores[world._make_diplo_key("France", "Austria")] = -39
        assert V.subjugation_refusal(world, "France", "Austria") != ""

    def test_no_standing_corps_admits_it(self, board):
        world = M.world
        for m in world.marshals.values():
            if m.nation == "Austria":
                m.strength = 0
        assert V.subjugation_refusal(world, "France", "Austria") == ""

    def test_a_captive_corps_does_not_count_as_standing(self, board):
        world = M.world
        for m in world.marshals.values():
            if m.nation == "Austria":
                m.captured_by = "France"
        assert V.subjugation_refusal(world, "France", "Austria") == ""

    def test_the_signed_clause_bypasses_the_gate(self, board):
        world = M.world
        with contextlib.redirect_stdout(io.StringIO()):
            result = V.create_vassal_conquest(world, "France", "Austria", by_treaty=True)
        assert result["success"] is True, result["message"]

    def test_the_ratify_seam_passes_by_treaty(self):
        src = (ROOT / "backend" / "game_logic" / "settlement_ratify.py").read_text(
            encoding="utf-8")
        i = src.index("vassal_result = create_vassal_conquest(")
        assert "by_treaty=True" in src[i:i + 300]

    def test_gr5_any_lord_meets_the_same_gate(self, board):
        world = M.world
        from backend.game_logic.diplomacy import set_diplomatic_state
        # Denmark fields a corps (Frederick) — Saxony fields none and would
        # be admitted at once by the no-standing-corps road.
        with contextlib.redirect_stdout(io.StringIO()):
            set_diplomatic_state(world, "Prussia", "Denmark", "WAR", "test")
        assert V.subjugation_refusal(world, "Prussia", "Denmark") != ""
        # "Denmark|Prussia": Denmark's own view at -40.
        world.war_scores[world._make_diplo_key("Prussia", "Denmark")] = -40
        assert V.subjugation_refusal(world, "Prussia", "Denmark") == ""

    def test_lever_down_restores_the_bare_war(self, board, monkeypatch):
        monkeypatch.setattr(V, "A_COURT_IS_SUBJUGATED_ONLY_WHEN_BEATEN", False)
        assert V.subjugation_refusal(M.world, "France", "Austria") == ""
        assert _post(board, "vassalize Austria").get("success") is True

    def test_the_gate_never_raises(self):
        assert V.subjugation_refusal(object(), "France", "Austria") == ""


# ═══════════════════════════════════════════════════════════════════════════
# 2. hold_titled 50 → 45 — §2.8's rule
# ═══════════════════════════════════════════════════════════════════════════
class TestHoldTitledIsFortyFive:
    def test_the_default_and_the_scenario_agree_on_45(self, board):
        assert congress.HOLD_TITLED == 45
        assert congress.hold_titled(M.world) == 45
        scenario = json.loads((ROOT / "godot-client" / "project-sovereign" / "assets"
                               / "maps" / "europe_1805.json").read_text(encoding="utf-8"))
        assert scenario["campaign_end"]["hold_titled"] == 45

    def test_the_boot_gate_reads_35_of_45(self, board):
        line = congress.state_line(M.world)
        assert line.startswith("THE CONGRESS OF PARIS — 35 of 45 titled")
        assert "45 are needed" in congress.summon_refusal(M.world)

    def test_the_staged_fixtures_stand_on_the_new_line(self):
        fixtures = ROOT / "tests" / "fixtures" / "playtest_saves"
        premature = json.loads((fixtures / "fixture_ge3_premature.json").read_text(encoding="utf-8"))
        pressburg = json.loads((fixtures / "fixture_ge3_pressburg.json").read_text(encoding="utf-8"))
        from backend.models.world_state import WorldState
        with contextlib.redirect_stdout(io.StringIO()):
            w_pre = WorldState.from_dict(premature["world_state"])
            w_press = WorldState.from_dict(pressburg["world_state"])
        assert congress.titled(w_pre)["count"] == 45, "the Premature arm summons on EXACTLY the line"
        assert congress.titled(w_press)["count"] >= 45


# ═══════════════════════════════════════════════════════════════════════════
# 3. GE-D2 "The Guard is Spent" — the floor the toll respects
# ═══════════════════════════════════════════════════════════════════════════
class TestTheGuardIsSpent:
    @staticmethod
    def _cornered_sovereign(strength):
        from backend.commands.executor import CommandExecutor
        from tests.conftest import MarshalFactory, WorldFactory
        nap = MarshalFactory.infantry(name="Napoleon", location="Belgium",
                                      strength=strength, personality="sovereign")
        assert nap.is_sovereign
        mack = MarshalFactory.enemy(name="Mack", location="Belgium", nation="Austria",
                                    strength=40000)
        world = WorldFactory.with_marshals([nap, mack])
        key = "|".join(sorted(["France", "Austria"]))
        world.diplomatic_states[key] = "WAR"
        world.war_start_turns[key] = world.current_turn
        ex = CommandExecutor()
        with contextlib.redirect_stdout(io.StringIO()):
            msg = ex._combat._check_marshal_fate(nap, mack, world)
        return nap, msg, world

    def test_the_floor_is_a_corps_that_can_still_fight(self):
        from backend.commands.combat_executor import CombatExecutor
        assert CombatExecutor.GUARD_SPENT_FLOOR == 1000
        assert CombatExecutor.GUARD_SPENT_FLOOR > CombatExecutor.GUARD_RUBBLE_FLOOR

    def test_the_guard_asks_before_the_last_battle(self):
        """The row's own named pin (DESIGN_REFINEMENT GE-D2): a Guard the
        toll would leave under the floor is ASKED — no toll is taken, the
        interrupt stands, and the corps is still a corps (1,200 men, not
        the 55-man remnant the old floor paid it down to)."""
        nap, msg, world = self._cornered_sovereign(1200)
        ask = nap.pending_interrupt
        assert ask and ask["interrupt_type"] == "last_stand" and ask.get("sovereign") is True
        assert "SPENT" in ask["message"] and "cannot buy another road" in ask["message"]
        assert nap.strength == 1200
        assert msg and "Guard is SPENT" in msg and "ENCIRCLED" not in msg

    def test_the_rail_row_names_the_question(self):
        nap, msg, world = self._cornered_sovereign(1200)
        pending = list(getattr(world.notifications, "_pending", []) or [])
        rows = [n for n in pending
                if "Guard is spent" in str((n or {}).get("title", "") if isinstance(n, dict)
                                           else getattr(n, "title", ""))]
        assert rows, [(n.get("title") if isinstance(n, dict) else getattr(n, "title", ""))
                      for n in pending]

    def test_a_guard_above_the_floor_still_buys_the_road(self):
        nap, msg, world = self._cornered_sovereign(3000)
        assert msg is None
        assert nap.strength == 2100
        assert nap.pending_interrupt is None
        assert "bought the road" in getattr(nap, "_sovereign_toll_note", "")

    def test_the_last_affordable_road_is_named(self):
        nap, msg, world = self._cornered_sovereign(1500)
        assert msg is None and nap.strength == 1050
        assert "cannot buy another road" in getattr(nap, "_sovereign_toll_note", "")

    def test_a_true_encirclement_still_reads_encircled(self):
        from backend.commands.executor import CommandExecutor
        from tests.conftest import MarshalFactory, WorldFactory
        nap = MarshalFactory.infantry(name="Napoleon", location="Belgium",
                                      strength=5000, personality="sovereign")
        mack = MarshalFactory.enemy(name="Mack", location="Belgium", nation="Austria",
                                    strength=40000)
        world = WorldFactory.with_marshals([nap, mack])
        key = "|".join(sorted(["France", "Austria"]))
        world.diplomatic_states[key] = "WAR"
        world.war_start_turns[key] = world.current_turn
        world.get_safe_retreat_destination = lambda *a, **k: None
        ex = CommandExecutor()
        with contextlib.redirect_stdout(io.StringIO()):
            msg = ex._combat._check_marshal_fate(nap, mack, world)
        assert msg and "ENCIRCLED" in msg
        assert "ENCIRCLED" in nap.pending_interrupt["message"]

    def test_the_breakout_copy_reads_the_same_floor(self):
        src = (ROOT / "backend" / "commands" / "strategic.py").read_text(encoding="utf-8")
        assert 'getattr(combat, "GUARD_SPENT_FLOOR"' in src


# ═══════════════════════════════════════════════════════════════════════════
# 4. `invest in <eliminated court>` is answered as a court that is gone
# ═══════════════════════════════════════════════════════════════════════════
class TestInvestInAnEliminatedCourt:
    def test_the_court_is_named_as_gone_not_as_a_marshal(self, board):
        world = M.world
        _eliminate(world, "Bavaria")
        assert "Bavaria" not in world.get_active_nations()
        response = _post(board, "invest in Bavaria")
        assert response.get("success") is False
        message = response.get("message", "")
        assert "no longer exists" in message and "eliminated" in message
        assert "which marshal" not in message.lower()

    def test_a_living_non_vassal_keeps_its_own_refusal(self, board):
        message = _post(board, "invest in Saxony").get("message", "")
        assert "not a vassal" in message

    def test_the_authored_courts_stay_known_to_the_parser(self, board):
        from backend.ai.llm_client import _extract_known_nations
        world = M.world
        _eliminate(world, "Bavaria")
        state = M.get_llm_game_state()
        known = _extract_known_nations(state)
        assert known.get("bavaria") == "Bavaria"
        assert "Bavaria" not in {i.get("controller") for i in state["map_data"].values()}


# ═══════════════════════════════════════════════════════════════════════════
# 5. The driver's --settlement and --decline-from dials
# ═══════════════════════════════════════════════════════════════════════════
class TestTheDriverDials:
    @pytest.fixture(scope="class")
    def D(self):
        import importlib
        return importlib.import_module("tools.playtest_driver")

    def _answerer(self, D, **policy):
        return D.Answerer(None, None, dict(D.POLICY_DEFAULTS) | policy, False)

    def test_settlement_mirrors_diplomacy_when_absent(self, D):
        assert D.settlement_mode({"diplomacy": "accept"}) == "accept"
        assert D.settlement_mode({"diplomacy": "decline"}) == "decline"
        assert D.settlement_mode({"diplomacy": "accept", "settlement": "decline"}) == "decline"

    def test_decline_from_parses_a_comma_list(self, D):
        assert D.declined_courts({"decline_from": "Hanover, Naples"}) == frozenset({"Hanover", "Naples"})
        assert D.declined_courts({}) == frozenset()
        assert D._court_of({"from_nation": "Hanover"}) == "Hanover"
        assert D._court_of({"type": "proposal_confirm"}) == ""
        assert "settlement" in D.POLICY_FLAG_KEYS and "decline_from" in D.POLICY_FLAG_KEYS

    def test_the_league_table_is_refused_while_the_arm_accepts(self, D):
        offer = {"type": "incoming_settlement_offer",
                 "options": [{"id": "accept_settlement_offer"},
                             {"id": "reject_settlement_offer"}]}
        assert self._answerer(D, diplomacy="accept")._pick_dialogue_choice(
            dict(offer)) == "accept_settlement_offer"
        assert self._answerer(D, diplomacy="accept", settlement="decline")._pick_dialogue_choice(
            dict(offer)) == "reject_settlement_offer"

    def test_the_named_court_is_refused_on_both_shapes(self, D):
        a = self._answerer(D, diplomacy="accept", decline_from="Hanover")
        typed = {"type": "incoming_proposal", "from_nation": "Hanover",
                 "options": [{"id": "accept_ai_proposal"}, {"id": "reject_ai_proposal"}]}
        assert a._pick_dialogue_choice(dict(typed)) == "reject_ai_proposal"
        bare = {"from_nation": "Hanover", "proposal_type": "armistice_losing"}
        assert a._pick_dialogue_choice(dict(bare)) == "reject"
        other = {"type": "incoming_proposal", "from_nation": "Austria",
                 "options": [{"id": "accept_ai_proposal"}, {"id": "reject_ai_proposal"}]}
        assert a._pick_dialogue_choice(dict(other)) == "accept_ai_proposal"

    def test_absent_dials_leave_every_prior_arm_byte_identical(self, D):
        a = self._answerer(D, diplomacy="accept")
        typed = {"type": "incoming_proposal", "from_nation": "Hanover",
                 "options": [{"id": "accept_ai_proposal"}, {"id": "reject_ai_proposal"}]}
        assert a._pick_dialogue_choice(dict(typed)) == "accept_ai_proposal"
