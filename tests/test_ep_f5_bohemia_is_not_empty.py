"""Row EP, slice F5 — "Bohemia is not empty" (`docs/ENDGAME_PLAN.md` §1 F5).

Two halves from the September 23, 2026 live review:

* **LV-D2 (FA-D13 re-opened)** — a minor's single corps took three
  great-power homeland provinces in one AI turn (Bavaria's Deroy: Bohemia
  and two more on turn 1 of the historical seed), promoting Austria's
  Revanche against Bavaria the same turn and drawing Charles into a
  three-turn punishment. P4.5's walk-in rung had no per-turn cap and no
  strength check for a "literal" marshal. Now: one walk-in per corps per
  turn (`movement_range` of them), and a literal corps runs the cautious
  counter-attack check before stepping beside a stronger enemy. Two levers
  (`enemy_ai.ONE_WALK_IN_PER_CORPS_PER_TURN`,
  `enemy_ai.THE_LITERAL_TAKES_THE_CAUTIOUS_STRENGTH_CHECK`); both down is
  the pre-F5 rung byte-for-byte. `BASELINE_SERIES` re-recorded ONCE with a
  four-arm attribution (`tools/_f5_series_arms.py`).
* **LV-14(a) / LV-D4** — the whole-war legitimacy blocker names the courts
  ("London and Vilna are unbeaten — a whole-war peace needs their consent
  (Austria 31/50, Britain 23/50, Russia 23/50). Press Austria alone: the
  separate peace.") and a covered court at or above the threshold gets a
  "Separate peace with <court>" chip on its row, routed to the existing
  pair-substitute tier with ITS court in the structured params. The
  predicate is unchanged.
"""

import contextlib
import io
import os
import random

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.ai import enemy_ai as EA
from backend.ai.enemy_ai import EnemyAI
from backend.commands.executor import CommandExecutor
from backend.commands.parser import CommandParser
from backend.game_logic import settlement_staging as SS
from backend.game_logic.diplomacy import get_war_score_for
from backend.game_logic.turn_manager import TurnManager
from backend.models.world_state import WorldState
from tests import _chip_census as C

REPO = C.REPO
SCENARIO = C.PROJECT / "assets" / "maps" / "europe_1805.json"
SEEDS = ("historical", "ulm", "austerlitz")


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


def _boot(seed="historical"):
    with _quiet():
        return WorldState.from_scenario(str(SCENARIO), seed=seed)


def _bavaria_holdings(world):
    return {r.name for r in world.regions.values() if r.controller == "Bavaria"}


def _bavarias_phase(world):
    """One AI phase for Bavaria alone, on the boot board, the M7 re-seed idiom."""
    executor = CommandExecutor()
    ai = EnemyAI(executor)
    before = _bavaria_holdings(world)
    random.seed(10_000)
    with _quiet():
        ai.process_nation_turn("Bavaria", world, {"world": world, "executor": executor})
    return sorted(_bavaria_holdings(world) - before)


def _check_passes_board():
    """The boot board with every Austrian corps sent far from Bavaria's
    frontier AND cut to a remnant, so the counter-attack check passes for
    any walk-in target and only the cap can stop a second one."""
    world = _boot()
    deroy = world.marshals["Deroy"]
    near = set(world.regions[deroy.location].adjacent_regions) | {deroy.location}
    far = [r.name for r in world.regions.values()
           if r.controller == "Austria" and r.name not in near
           and not (set(r.adjacent_regions) & near)]
    assert far, "no Austrian province far from Deroy"
    for m in world.marshals.values():
        if m.nation == "Austria":
            m.location = far[0]
            m.strategic_order = None
            m.strength = 1000
    return world


# ═══════════════════════════════════════════════════════════════════════════
# LV-D2 — the walk-in cap
# ═══════════════════════════════════════════════════════════════════════════


class TestTheWalkInCap:

    def test_the_uncapped_rung_hands_deroy_two_provinces_in_one_phase(self, monkeypatch):
        """The defect, reproduced on the historical seed's boot: with the cap
        down Bavaria's one corps takes Bohemia and then Carniola in ONE
        phase (the review's "Bohemia + 2" was the commanded board)."""
        monkeypatch.setattr(EA, "ONE_WALK_IN_PER_CORPS_PER_TURN", False)
        monkeypatch.setattr(EA, "THE_LITERAL_TAKES_THE_CAUTIOUS_STRENGTH_CHECK", False)
        taken = _bavarias_phase(_boot())
        assert len(taken) >= 2, taken

    def test_the_cap_hands_deroy_one(self, monkeypatch):
        monkeypatch.setattr(EA, "ONE_WALK_IN_PER_CORPS_PER_TURN", True)
        monkeypatch.setattr(EA, "THE_LITERAL_TAKES_THE_CAUTIOUS_STRENGTH_CHECK", False)
        taken = _bavarias_phase(_boot())
        assert len(taken) <= 1, taken

    def test_the_cap_is_the_corps_movement_range(self, monkeypatch):
        """A cavalry corps (range 2) may take two; the counter is per corps."""
        monkeypatch.setattr(EA, "ONE_WALK_IN_PER_CORPS_PER_TURN", True)
        monkeypatch.setattr(EA, "THE_LITERAL_TAKES_THE_CAUTIOUS_STRENGTH_CHECK", False)
        world = _boot()
        deroy = world.marshals["Deroy"]
        ai = EnemyAI(CommandExecutor())
        ai._walk_ins_this_turn = {"Deroy": 1}
        assert ai._find_undefended_capture(deroy, "Bavaria", world) is None
        deroy.movement_range = 2
        assert ai._find_undefended_capture(deroy, "Bavaria", world) is not None
        ai._walk_ins_this_turn = {"Deroy": 2}
        assert ai._find_undefended_capture(deroy, "Bavaria", world) is None

    def test_the_action_is_tagged_and_the_loop_counts_it(self, monkeypatch):
        """The rung's dict carries `walk_in` so the loop can count it (the
        literal check is DOWN here: at boot it refuses Deroy Bohemia,
        74,000 against 22,000 — the other half of the slice)."""
        monkeypatch.setattr(EA, "THE_LITERAL_TAKES_THE_CAUTIOUS_STRENGTH_CHECK", False)
        world = _boot()
        deroy = world.marshals["Deroy"]
        ai = EnemyAI(CommandExecutor())
        ai._walk_ins_this_turn = {}
        action = ai._find_undefended_capture(deroy, "Bavaria", world)
        assert action is not None and action.get("walk_in") is True, action
        assert action["action"] == "attack"

    def test_the_literal_check_refuses_deroy_bohemia_at_boot(self, monkeypatch):
        """With the check UP the same call refuses: Bohemia is one march from
        the Austrian mass and Deroy's 22,000 would stand beside it."""
        monkeypatch.setattr(EA, "THE_LITERAL_TAKES_THE_CAUTIOUS_STRENGTH_CHECK", True)
        world = _boot()
        deroy = world.marshals["Deroy"]
        ai = EnemyAI(CommandExecutor())
        ai._walk_ins_this_turn = {}
        assert ai._find_undefended_capture(deroy, "Bavaria", world) is None

    def test_the_cap_binds_where_the_check_passes(self):
        """The cap's own pin, no lever touched: on the boot board the
        literal check refuses Deroy (Charles is one march from Bohemia), so
        a board where the check PASSES is staged — every Austrian corps
        sent far from the frontier — and Deroy, who then takes two
        provinces uncapped, takes one."""
        world = _check_passes_board()
        taken = _bavarias_phase(world)
        assert len(taken) <= 1, taken

    def test_the_same_board_uncapped_hands_him_two(self, monkeypatch):
        """The staging above is sensitive: with the cap down he takes two."""
        monkeypatch.setattr(EA, "ONE_WALK_IN_PER_CORPS_PER_TURN", False)
        world = _check_passes_board()
        taken = _bavarias_phase(world)
        assert len(taken) >= 2, taken

    def test_the_counter_resets_with_the_phase(self):
        world = _boot()
        ai = EnemyAI(CommandExecutor())
        ai._walk_ins_this_turn = {"Deroy": 5}
        random.seed(10_000)
        with _quiet():
            ai.process_nation_turn("Bavaria", world, {"world": world, "executor": ai.executor})
        assert ai._walk_ins_this_turn.get("Deroy", 0) <= 1


class TestTheLiteralTakesTheStrengthCheck:

    def _stage(self):
        """Deroy (literal, 22,000) at Franconia beside an empty Austrian
        Bohemia, with Charles's 54,000 standing on Bohemia's other side."""
        world = _boot()
        deroy = world.marshals["Deroy"]
        charles = world.marshals["ArchdukeCharles"]
        bohemia = world.regions["Bohemia"]
        neighbours = [n for n in bohemia.adjacent_regions
                      if n != deroy.location and world.regions[n].controller == "Austria"]
        assert neighbours, bohemia.adjacent_regions
        charles.location = neighbours[0]
        charles.strategic_order = None
        assert charles.strength > deroy.strength * 1.5
        return world, deroy

    def test_a_literal_corps_refuses_the_walk_in_beside_a_stronger_enemy(self, monkeypatch):
        monkeypatch.setattr(EA, "THE_LITERAL_TAKES_THE_CAUTIOUS_STRENGTH_CHECK", True)
        world, deroy = self._stage()
        ai = EnemyAI(CommandExecutor())
        safe, reason = ai._evaluate_capture_safety(deroy, "Bohemia", "Bavaria", world)
        assert safe is False and reason.startswith("Literal:"), (safe, reason)

    def test_with_the_lever_down_he_walks_in(self, monkeypatch):
        monkeypatch.setattr(EA, "THE_LITERAL_TAKES_THE_CAUTIOUS_STRENGTH_CHECK", False)
        world, deroy = self._stage()
        ai = EnemyAI(CommandExecutor())
        safe, _reason = ai._evaluate_capture_safety(deroy, "Bohemia", "Bavaria", world)
        assert safe is True

    def test_the_cautious_check_is_untouched(self, monkeypatch):
        monkeypatch.setattr(EA, "THE_LITERAL_TAKES_THE_CAUTIOUS_STRENGTH_CHECK", False)
        world, deroy = self._stage()
        deroy.personality = "cautious"
        ai = EnemyAI(CommandExecutor())
        safe, reason = ai._evaluate_capture_safety(deroy, "Bohemia", "Bavaria", world)
        assert safe is False and reason.startswith("Cautious:"), (safe, reason)


class TestThreeSeeds:
    """The plan's own measurement: Bavaria takes at most ONE Austrian province
    on turn 1, on each of three seeds, and Austria's Revanche against Bavaria
    does not promote on turn 1 on any of them."""

    @pytest.mark.parametrize("seed", SEEDS)
    def test_at_most_one_province_on_turn_one(self, seed):
        world = _boot(seed)
        executor = CommandExecutor()
        tm = TurnManager(world, executor=executor)
        before = {r.name: r.controller for r in world.regions.values()}
        random.seed(10_000)
        with _quiet():
            tm.end_turn({"world": world, "executor": executor})
        taken = [n for n, r in world.regions.items()
                 if r.controller == "Bavaria" and before[n] == "Austria"]
        assert len(taken) <= 1, (seed, taken)
        revanche = [e for e in world.event_log
                    if e.get("type") == "design_promoted" and e.get("nation") == "Austria"
                    and "Bavaria" in str(e)]
        assert revanche == [], (seed, revanche)


class TestTheSeriesAttribution:

    def test_the_arms_tool_exists_and_names_both_levers(self):
        src = (REPO / "tools" / "_f5_series_arms.py").read_text(encoding="utf-8")
        assert "ONE_WALK_IN_PER_CORPS_PER_TURN" in src
        assert "THE_LITERAL_TAKES_THE_CAUTIOUS_STRENGTH_CHECK" in src

    def test_the_recorded_series_is_the_shipped_tree(self):
        from tests.test_ai_intent_threat_migration import BASELINE_SERIES
        assert BASELINE_SERIES[:8] == [70, 68, 66, 64, 62, 60, 58, 46]


# ═══════════════════════════════════════════════════════════════════════════
# LV-14(a) / LV-D4 — the legitimacy sentence and the separate-peace chip
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture(autouse=True)
def _restore_active_world():
    prior = (M.world, M.game_state.get("world"), M.parser)
    yield
    M.world = prior[0]
    M.game_state["world"] = prior[1]
    M.parser = prior[2]


def _set_france_score(world, court, score):
    """Write the pair war score so that France reads +score
    (`get_war_score_for` flips for the alphabetically-second nation)."""
    key = world._make_diplo_key("France", court)
    world.war_scores[key] = int(score) if key.split("|")[0] == "France" else -int(score)
    assert get_war_score_for(world, "France", court) == score


def _staged_table(war_score=58):
    """The review's board: Vienna held, Austria beaten in the field (the
    war score), the whole-war white peace drafted against the coalition."""
    with _quiet():
        M._reset_world_state()
    M.parser = CommandParser(use_real_llm=False)
    world = M.world
    client = TestClient(M.app)
    world.regions["Vienna"].controller = "France"
    world.invalidate_active_nations_cache()
    world.diplomatic_points = max(int(world.diplomatic_points), 5)
    _set_france_score(world, "Austria", war_score)
    with _quiet():
        r = client.post("/command", json={"command": "propose common peace with Austria"}).json()
    dialogue = r.get("diplomatic_dialogue") or {}
    assert dialogue.get("type") == "settlement_confirm", r.get("message")
    return world, client, dialogue


@pytest.fixture()
def table(monkeypatch):
    """One staged table per test, on the 1805 board, the active world kept
    live for the request the test then sends (the autouse fixture restores
    the prior world after)."""
    C.board_env(monkeypatch)
    return _staged_table()


class TestTheLegitimacySentence:

    def test_the_blocker_names_the_unbeaten_courts_and_the_one_to_press(self, table):
        _world, _client, dialogue = table
        text = str(dialogue.get("talleyrand_text", ""))
        rows = {r["nation"]: r for r in dialogue["per_court_acceptance"]}
        assert "the terms claim a victory the field has not delivered" in text, text
        assert "London and Vilna are unbeaten — a whole-war peace needs their consent (" in text, text
        for court in ("Austria", "Britain", "Russia"):
            assert f"{court} {rows[court]['total']}/{rows[court]['threshold']}" in text, text
        assert "Press Austria alone: the separate peace." in text, text
        assert "Vienna" not in text.split("unbeaten")[0].split("shifts.")[-1], text

    def test_the_predicate_is_unchanged(self, table):
        _world, _client, dialogue = table
        assert dialogue["overall_acceptance"]["carries"] is False
        assert "confirm_settlement" not in [o.get("action") for o in dialogue.get("options") or []]

    def test_an_unbeaten_court_is_the_wars_word(self, table):
        world, _client, dialogue = table
        rows = dialogue["per_court_acceptance"]
        holdouts = dialogue["overall_acceptance"]["holdout_courts"]
        sentence = SS.legitimacy_sentence(world, rows, holdouts, 50)
        assert sentence.startswith("London and Vilna are unbeaten")
        _set_france_score(world, "Britain", 30)
        sentence = SS.legitimacy_sentence(world, rows, holdouts, 50)
        assert sentence.startswith("Vilna is unbeaten — a whole-war peace needs its consent")
        assert "Press Austria and Britain alone" in sentence
        _set_france_score(world, "Britain", 0)

    def test_no_holdouts_no_sentence(self, table):
        world, _client, dialogue = table
        assert SS.legitimacy_sentence(world, dialogue["per_court_acceptance"], [], 50) == ""

    def test_the_lever_down_is_the_old_heading(self, table, monkeypatch):
        world, _client, dialogue = table
        monkeypatch.setattr(SS, "THE_BLOCKER_NAMES_THE_COURTS", False)
        rows = dialogue["per_court_acceptance"]
        holdouts = dialogue["overall_acceptance"]["holdout_courts"]
        assert SS.legitimacy_sentence(world, rows, holdouts, 50) == ""


class TestTheSeparatePeaceChip:

    def test_a_row_at_the_threshold_carries_the_chip_and_only_then(self, table):
        _world, _client, dialogue = table
        for row in dialogue["per_court_acceptance"]:
            chips = [a for a in row.get("dial_actions") or [] if a.get("action") == "seek_bilateral_peace"]
            ready = (row.get("total") is not None and not row.get("hard_stops")
                     and int(row["total"]) >= int(row["threshold"]))
            assert bool(chips) == ready, (row["nation"], row.get("total"), chips)
            for chip in chips:
                assert chip["selected_target_nation"] == row["nation"]

    def test_the_chip_names_its_court_and_states_its_availability(self, table):
        world, _client, dialogue = table
        chip = SS.separate_peace_chip(world, "Britain", war_id=dialogue["war_id"],
                                      staged_terms=dialogue.get("settlement_terms") or [],
                                      actor="France")
        assert chip["label"] == "Separate peace with Britain"
        assert chip["action"] == "seek_bilateral_peace"
        assert chip["nation"] == chip["selected_target_nation"] == "Britain"
        assert chip["scope"] == "selected_pair" and chip["war_id"] == dialogue["war_id"]
        if chip.get("available") is False:
            assert chip["disabled_reason_display"]

    def test_the_chip_reaches_the_pair_tier_naming_its_own_court(self, table):
        """The structured-params road: the chip for Britain, sent from a
        table whose selected target is Austria, is judged for BRITAIN."""
        world, client, dialogue = table
        assert dialogue.get("selected_target_nation") == "Austria", dialogue.get("selected_target_nation")
        params = {"action": "seek_bilateral_peace", "scope": "selected_pair",
                  "nation": "Britain", "selected_target_nation": "Britain",
                  "war_id": dialogue["war_id"]}
        with _quiet():
            r = client.post("/respond_to_diplomatic_dialogue",
                            json={"choice": "seek_bilateral_peace", "action_params": params,
                                  "dialogue_id": dialogue.get("dialogue_id")}).json()
        assert r.get("success") is True, r.get("message")
        staged = r.get("diplomatic_dialogue") or {}
        assert staged.get("type") == "settlement_pair_substitute_confirm", staged.get("type")
        assert staged.get("selected_target_nation") == "Britain", staged
        assert "to treat with Britain alone" in str(r.get("message")), r.get("message")

    def test_a_foreign_name_in_the_params_falls_back_to_the_table(self, table):
        """A stale or foreign court in the params never re-aims the tier."""
        world, client, dialogue = table
        params = {"action": "seek_bilateral_peace", "scope": "selected_pair",
                  "nation": "Prussia", "selected_target_nation": "Prussia",
                  "war_id": dialogue["war_id"]}
        with _quiet():
            r = client.post("/respond_to_diplomatic_dialogue",
                            json={"choice": "seek_bilateral_peace", "action_params": params,
                                  "dialogue_id": dialogue.get("dialogue_id")}).json()
        staged = r.get("diplomatic_dialogue") or {}
        assert staged.get("selected_target_nation") == "Austria", (r.get("message"), staged)
        assert "to treat with Austria alone" in str(r.get("message")), r.get("message")

    def test_a_court_at_the_threshold_carries_the_chip(self, monkeypatch):
        """No shipped board puts a covered court at 50 on this staging
        (Austria reads 31 with Vienna held and Mack captive), so the gate
        is staged through the scorer's stable seam: Austria scored 70, its
        row carries the chip — and ONLY its row — and the sentence names
        it as the court to press alone."""
        from backend.game_logic import settlement_scoring as SC
        real = SC.calculate_common_peace_acceptance

        def _lift(world, **kw):
            out = real(world, **kw)
            if kw.get("accepting_leader") == "Austria" and out.get("score") is not None:
                out["score"] = max(int(out["score"]), 70)
            return out

        monkeypatch.setattr(SC, "calculate_common_peace_acceptance", _lift)
        C.board_env(monkeypatch)
        _world, _client, dialogue = _staged_table()
        rows = {r["nation"]: r for r in dialogue["per_court_acceptance"]}
        assert int(rows["Austria"]["total"]) >= int(rows["Austria"]["threshold"]), rows["Austria"]
        chips = [a for a in rows["Austria"]["dial_actions"] if a.get("action") == "seek_bilateral_peace"]
        assert len(chips) == 1, rows["Austria"]["dial_actions"]
        assert chips[0]["label"] == "Separate peace with Austria"
        assert chips[0]["selected_target_nation"] == "Austria"
        for court in ("Britain", "Russia"):
            assert not [a for a in rows[court]["dial_actions"] if a.get("action") == "seek_bilateral_peace"], court
        assert "Press Austria alone: the separate peace." in str(dialogue.get("talleyrand_text", ""))

    def test_the_tier2_renderer_honours_availability(self):
        src = (C.SCRIPTS / "proposal_confirm_popup.gd").read_text(encoding="utf-8")
        i = src.index("func _on_settlement_tier2_affordance") if "func _on_settlement_tier2_affordance" in src else 0
        assert 'if not bool(aff.get("available", true)):' in src
        assert 'btn.tooltip_text = aff_reason' in src

    def test_the_structured_path_knows_the_pair_verbs(self):
        from backend.commands import diplomatic_executor as DE
        assert {"seek_bilateral_peace", "seek_armistice_instead"} <= set(DE._SETTLEMENT_TIER2_ACTION_IDS)
