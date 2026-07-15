"""
Playtest fixes — 2026-07-14 (vassal improvements + recent slices).

Covers the fixes routed from a live europe_1805 playtest + a 14-agent
adversarial verification (memo: docs/audits/VASSAL_PLAYTEST_2026_07_14.md):

  F1/F1c/C1  recovery hint names only WORKING levers, grip-aware, single source
             (dropped the blunted "grant autonomy", the nonexistent "subsidy",
             and the DEAD "garrison their capital" lever)
  C2         autonomy-up blunt is explained in the spiral band, like invest
  F6         typed autonomy commands parse (executor reads raw_command; mock breadth)
  F3         danger/threat readings exclude allied/neutral co-located forces
  F8b        a blocked vassal rebellion becomes independent, never a stale-VASSAL orphan
  F5         the Berthier recovery prompt feeds human-readable verbs, not raw ids
  F4         a messy MOVE destination resolves to a region / clean-fails (no raw leak)
"""

import pytest

from backend.models.world_state import WorldState
from backend.models.authority import AUTHORITY_ACCELERATE_BELOW
from backend.game_logic.vassal import (
    recovery_hint_for_grip,
    process_vassal_loyalty,
    change_vassal_autonomy,
    check_vassal_rebellion,
    AUTONOMY_SATELLITE,
    AUTONOMY_AUTONOMOUS,
)


def _make_world(authority=100):
    world = WorldState()
    world.current_turn = 5
    world.player_nation = "France"
    world.authority_tracker.authority = authority
    return world


def _add_vassal(world, name="Saxony", loyalty=80, autonomy=AUTONOMY_SATELLITE,
                lord="France"):
    world.vassals[name] = {"lord": lord, "loyalty": loyalty, "autonomy": autonomy}
    world.nation_relations[world._make_diplo_key(name, lord)] = 0
    return world.vassals[name]


# ═══════════════════════════════════════════════════════════════════════════
# F1 / F1c / C1 — recovery-hint copy names only WORKING levers
# ═══════════════════════════════════════════════════════════════════════════

class TestRecoveryHintCopy:
    def test_healthy_names_working_levers_only(self):
        hint = recovery_hint_for_grip(80).lower()
        assert "invest" in hint
        assert "autonomy" in hint
        # F1c: the dead "garrison their capital" lever is gone
        assert "garrison" not in hint
        # F1: no nonexistent "subsidy" action
        assert "subsid" not in hint

    def test_spiral_names_only_unblunted_arrests(self):
        hint = recovery_hint_for_grip(20).lower()
        # working spiral arrests: win a decisive battle, or release
        assert "battle" in hint
        assert "release" in hint
        # F1: NOT the blunted "grant autonomy" lever, NOT a "subsidy", NOT garrison
        assert "grant autonomy" not in hint
        assert "subsid" not in hint
        assert "garrison" not in hint

    def test_healthy_and_spiral_copy_differ(self):
        assert recovery_hint_for_grip(80) != recovery_hint_for_grip(20)

    def test_event_surfaces_the_grip_aware_hint(self):
        w = _make_world(authority=100)  # grip 100 → healthy variant
        _add_vassal(w, "Saxony", loyalty=80, autonomy=AUTONOMY_SATELLITE)
        events = process_vassal_loyalty(w)
        ev = next((e for e in events if e.get("vassal") == "Saxony"), None)
        assert ev is not None
        assert ev["recovery_hint"] == recovery_hint_for_grip(100)
        assert "garrison" not in ev["recovery_hint"].lower()

    def test_garrison_not_advertised_and_does_not_fire(self):
        """F1c: garrison-loyalty is unwired in production (reads a field
        nothing assigns), so it must never surface as a contributor in a
        normal satellite's recovery event, and the hint must not name it."""
        w = _make_world(authority=100)
        _add_vassal(w, "Saxony", loyalty=80)
        events = process_vassal_loyalty(w)
        for ev in events:
            assert "garrison" not in (ev.get("reason") or "").lower()
            assert "garrison" not in (ev.get("recovery_hint") or "").lower()


# ═══════════════════════════════════════════════════════════════════════════
# C2 — the autonomy-up blunt is EXPLAINED in the spiral band
# ═══════════════════════════════════════════════════════════════════════════

class TestAutonomyBluntExplained:
    def test_spiral_autonomy_up_names_the_blunt(self):
        w = _make_world(authority=20)  # grip 20 → spiral band
        assert w.authority_tracker.authority < AUTHORITY_ACCELERATE_BELOW
        _add_vassal(w, "Saxony", loyalty=50, autonomy=AUTONOMY_SATELLITE)
        w.diplomatic_points = 5
        res = change_vassal_autonomy(w, "Saxony", AUTONOMY_AUTONOMOUS)
        assert res["success"], res
        assert "blunts the gesture" in res["message"]
        assert "+4 loyalty" in res["message"]  # 10 × 0.40

    def test_healthy_autonomy_up_pays_full_no_blunt(self):
        w = _make_world(authority=100)  # grip 100 → healthy
        _add_vassal(w, "Saxony", loyalty=50, autonomy=AUTONOMY_SATELLITE)
        w.diplomatic_points = 5
        res = change_vassal_autonomy(w, "Saxony", AUTONOMY_AUTONOMOUS)
        assert res["success"], res
        assert "blunts the gesture" not in res["message"]
        assert "+10 loyalty" in res["message"]


# ═══════════════════════════════════════════════════════════════════════════
# F6 — typed autonomy commands actually parse + change the level
# ═══════════════════════════════════════════════════════════════════════════

class TestTypedAutonomyParse:
    def _executor(self):
        from backend.commands.vassal_executor import VassalExecutor
        return VassalExecutor(None)

    def test_executor_reads_raw_command_for_level(self):
        """The parser populates `raw_command`; the executor must read it (the
        old chain read only raw_input/original_command and dead-ended)."""
        w = _make_world()
        _add_vassal(w, "Saxony", loyalty=50, autonomy=AUTONOMY_SATELLITE)
        w.diplomatic_points = 5
        cmd = {"target": "Saxony", "raw_command": "change Saxony autonomy to autonomous"}
        res = self._executor()._execute_change_autonomy(cmd, {"world": w})
        assert res["success"], res
        assert w.vassals["Saxony"]["autonomy"] == AUTONOMY_AUTONOMOUS

    def test_executor_grant_more_autonomy_direction(self):
        w = _make_world()
        _add_vassal(w, "Saxony", loyalty=50, autonomy=AUTONOMY_SATELLITE)
        w.diplomatic_points = 5
        cmd = {"target": "Saxony", "raw_command": "grant Saxony more autonomy"}
        res = self._executor()._execute_change_autonomy(cmd, {"world": w})
        assert res["success"], res
        assert w.vassals["Saxony"]["autonomy"] == AUTONOMY_AUTONOMOUS

    @pytest.mark.parametrize("text", [
        "grant Saxony autonomy",
        "change Saxony autonomy to puppet",
        "make Saxony autonomous",
        "set Saxony puppet",
    ])
    def test_mock_parser_routes_to_change_autonomy(self, text):
        from backend.ai.llm_client import LLMClient
        client = LLMClient(use_real_api=False)
        result = client.parse_command(text)
        assert result.get("action") == "change_autonomy", (text, result.get("action"))


# ═══════════════════════════════════════════════════════════════════════════
# Sweep 4 (2026-07-15) — the FULL parse pipeline must not fuzzy-match a
# direction word ("more"/"less") to a marshal and FAIL a vassal command.
#   Root cause: change_autonomy targets a NATION (executor resolves it from
#   raw_command), but _apply_fuzzy_matching still hunted for a marshal in the
#   leftover words — "grant Holland MORE autonomy" matched "more" -> "Murat"
#   and returned a marshal_suggest error, so the command shrugged. "grant
#   Holland autonomy" (no direction word) parsed. The F6 tests above covered
#   the mock parser + executor but NOT CommandParser.parse, which is why the
#   gap slipped through — these pin the full pipeline.
# ═══════════════════════════════════════════════════════════════════════════

class TestSweep4AutonomyDirectionParse:
    def _parser(self):
        from backend.commands.parser import CommandParser
        return CommandParser(use_real_llm=False)

    @pytest.mark.parametrize("text", [
        "grant Holland more autonomy",
        "give Holland more autonomy",
        "grant Holland less autonomy",
        "reduce Switzerland autonomy",
        "grant Holland autonomy",          # the no-direction control (always worked)
        "make Holland autonomous",
    ])
    def test_full_parse_pipeline_does_not_shrug_on_direction_word(self, text):
        w = _make_world()
        _add_vassal(w, "Holland", loyalty=90, autonomy=AUTONOMY_SATELLITE)
        _add_vassal(w, "Switzerland", loyalty=90, autonomy=AUTONOMY_SATELLITE)
        parser = self._parser()
        result = parser.parse(text, game_state={"world": w}, world=w)
        # Pre-fix: "more"/"less" -> success=False with a Murat marshal_suggest error.
        assert result.get("success") is True, (text, result.get("error"))
        cmd = result.get("command") or {}
        assert cmd.get("action") == "change_autonomy", (text, cmd.get("action"))
        # And the direction word must NOT have been absorbed as a marshal.
        assert cmd.get("marshal") is None, (text, cmd.get("marshal"))

    def test_more_autonomy_no_longer_suggests_a_marshal(self):
        """The exact Sweep-4 symptom: 'more' fuzzy-matched to a marshal."""
        w = _make_world()
        _add_vassal(w, "Holland", loyalty=90, autonomy=AUTONOMY_SATELLITE)
        result = self._parser().parse(
            "grant Holland more autonomy", game_state={"world": w}, world=w)
        assert result.get("success") is True
        # falsifiable: the pre-fix failure carried these keys
        assert result.get("kind") != "marshal_suggest"
        assert "Murat" not in (result.get("suggestion") or "")


# ═══════════════════════════════════════════════════════════════════════════
# VP-D5 (Sweep 4) — granting autonomy surfaces its PERMANENT tribute cut
# ═══════════════════════════════════════════════════════════════════════════

class TestAutonomyTributeLegibility:
    def test_autonomy_up_names_the_permanent_income_cut(self):
        w = _make_world(authority=100)
        _add_vassal(w, "Saxony", loyalty=50, autonomy=AUTONOMY_SATELLITE)
        w.diplomatic_points = 5
        res = change_vassal_autonomy(w, "Saxony", AUTONOMY_AUTONOMOUS)
        assert res["success"], res
        # shows the tribute DELTA (75% -> 50%) and flags it as a permanent cut
        assert "75% → 50%" in res["message"], res["message"]
        assert "permanent income cut" in res["message"], res["message"]

    def test_autonomy_down_names_the_income_gain(self):
        w = _make_world(authority=100)
        _add_vassal(w, "Saxony", loyalty=80, autonomy=AUTONOMY_AUTONOMOUS)
        w.diplomatic_points = 5
        res = change_vassal_autonomy(w, "Saxony", AUTONOMY_SATELLITE)
        assert res["success"], res
        assert "50% → 75%" in res["message"], res["message"]
        assert "collect more of their income" in res["message"], res["message"]


# ═══════════════════════════════════════════════════════════════════════════
# F3 — danger/threat readings exclude allies, vassals, and neutrals
# ═══════════════════════════════════════════════════════════════════════════

class TestBelligerenceFilter:
    def _world_with_relations(self):
        w = _make_world()
        from backend.game_logic.diplomacy import set_diplomatic_state
        set_diplomatic_state(w, "France", "Austria", "WAR", "test")
        set_diplomatic_state(w, "France", "Bavaria", "ALLIANCE", "test")
        set_diplomatic_state(w, "France", "Prussia", "PEACE", "test")
        return w

    def test_only_belligerents_count_as_enemy(self):
        from backend.game_logic.dispatch import _intel_marshal_is_enemy
        w = self._world_with_relations()
        assert _intel_marshal_is_enemy(w, "France", {"nation": "Austria"}) is True
        # ally, neutral, own, and unknown are NOT enemies
        assert _intel_marshal_is_enemy(w, "France", {"nation": "Bavaria"}) is False
        assert _intel_marshal_is_enemy(w, "France", {"nation": "Prussia"}) is False
        assert _intel_marshal_is_enemy(w, "France", {"nation": "France"}) is False
        assert _intel_marshal_is_enemy(w, "France", {"nation": None}) is False
        assert _intel_marshal_is_enemy(w, "France", {}) is False


# ═══════════════════════════════════════════════════════════════════════════
# F8b — a blocked rebellion becomes independent, never a stale-VASSAL orphan
# ═══════════════════════════════════════════════════════════════════════════

class TestRebellionNoOrphan:
    def test_blocked_war_allocation_becomes_independent(self, monkeypatch):
        import backend.game_logic.settlement_helpers as sh
        monkeypatch.setattr(
            sh, "ensure_war_instance_for_pair",
            lambda *a, **k: {"ok": False, "error": "test_side_conflict", "details": {}},
        )
        w = _make_world()
        key = w._make_diplo_key("France", "KingdomOfItaly")
        w.diplomatic_states[key] = "VASSAL"
        w.vassals["KingdomOfItaly"] = {
            "lord": "France", "loyalty": 0, "autonomy": AUTONOMY_SATELLITE,
        }
        events = check_vassal_rebellion(w)
        # removed from the vassals dict AND no longer a phantom VASSAL relation
        assert "KingdomOfItaly" not in w.vassals
        assert w.diplomatic_states.get(key) != "VASSAL"
        assert w.diplomatic_states.get(key) == "PEACE"
        assert any(e.get("type") == "vassal_rebellion_independent" for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# F5 — the Berthier recovery prompt never feeds raw internal action ids
# ═══════════════════════════════════════════════════════════════════════════

class TestBerthierPromptNoRawIds:
    def test_prompt_has_no_underscored_action_ids(self):
        from backend.ai.prompt_builder import build_berthier_recovery_prompt
        game_state = {"marshals": {}, "map_data": {}, "enemies": {}}
        _system, user = build_berthier_recovery_prompt("blah blah nonsense", game_state)
        # the raw ids that leaked live must not appear verbatim
        for raw_id in ("invest_vassal", "change_autonomy", "make_vassal",
                       "release_vassal", "diplomatic_proposal"):
            assert raw_id not in user, raw_id
        # meta/debug verbs are dropped from the suggestion list
        assert "cheat" not in user.lower().split("valid actions")[-1]


# ═══════════════════════════════════════════════════════════════════════════
# F4 — a messy MOVE destination resolves to a region (no raw-string leak)
# ═══════════════════════════════════════════════════════════════════════════

class TestDestinationResolution:
    def test_region_in_messy_phrase_resolves(self):
        from backend.commands.strategic_executor import _resolve_region_from_phrase
        w = _make_world()
        region = max(w.regions, key=len)  # a distinctive, len>=4 region name
        phrase = f"On Some Enemy At {region}"
        assert _resolve_region_from_phrase(w, phrase) == region

    def test_gibberish_resolves_to_none(self):
        from backend.commands.strategic_executor import _resolve_region_from_phrase
        w = _make_world()
        assert _resolve_region_from_phrase(w, "xyzzy plugh quux") is None

    def test_empty_phrase_is_none(self):
        from backend.commands.strategic_executor import _resolve_region_from_phrase
        w = _make_world()
        assert _resolve_region_from_phrase(w, "") is None
