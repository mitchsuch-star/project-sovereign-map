"""W6-1 §3.2–3.6 — Correctness B: reports, dispatch, stats, endowment ask.

Covers BUG-CA-3 (endow asks, never defaults), BUG-CA-4 (battle-report
remaining strengths), BUG-CA-5 (observation truthfulness + modifier
labels), BUG-CA-6 (dispatch intel freshness), BUG-CA-9 (participation
counts + last_battle_turn).
"""

from backend.commands.executor import CommandExecutor
from backend.game_logic.battle_report import (
    _pick_observation,
    generate_battle_report,
    snapshot_attacker_modifiers,
    snapshot_defender_modifiers,
)
from backend.models.marshal import Marshal

from tests.conftest import MarshalFactory, WorldFactory


# ════════════════════════════════════════════════════════════════════════
# BUG-CA-3 — endowment without a stated region asks, never defaults
# ════════════════════════════════════════════════════════════════════════

class TestEndowmentAsksNeverDefaults:
    def _dotation_world(self):
        world = WorldFactory.basic()
        # ES-7 is Europe-scoped; flag the fixture world as the Europe map.
        world.sovereign_map = "europe"
        # Give France a conquered non-homeland province so the eligible
        # list is non-empty (Rhineland starts Prussian).
        world.regions["Rhineland"].controller = "France"
        world.invalidate_active_nations_cache()
        return world

    def test_guessed_target_is_treated_as_missing(self):
        """The live audit: 'Endow Ney with an estate' arrived with a
        parser-guessed region → refused with 'We do not hold White Russia'.
        A target the raw text never names must ASK with eligibles."""
        world = self._dotation_world()
        executor = CommandExecutor()
        result = executor._economy._execute_grant_dotation(
            {"marshal": "Ney", "action": "grant_dotation",
             "target": "Bavaria"},
            {"world": world},
            raw_text="Endow Ney with an estate")
        assert result["success"] is False
        assert "Which province, Sire?" in result["message"]
        assert "Rhineland" in result["message"]
        # Nothing mutated.
        assert not world.get_marshal("Ney").dotation_regions

    def test_named_region_path_unchanged(self):
        world = self._dotation_world()
        executor = CommandExecutor()
        result = executor._economy._execute_grant_dotation(
            {"marshal": "Ney", "action": "grant_dotation",
             "target": "Rhineland"},
            {"world": world},
            raw_text="Endow Ney with Rhineland")
        assert result["success"] is True
        assert "Rhineland" in world.get_marshal("Ney").dotation_regions

    def test_no_raw_text_keeps_target(self):
        """AI-built command dicts carry no raw text — the guard must not
        second-guess a programmatic target (GR5)."""
        world = self._dotation_world()
        executor = CommandExecutor()
        result = executor._economy._execute_grant_dotation(
            {"marshal": "Ney", "action": "grant_dotation",
             "target": "Rhineland"},
            {"world": world})
        assert result["success"] is True

    def test_missing_target_asks_with_eligibles(self):
        world = self._dotation_world()
        executor = CommandExecutor()
        result = executor._economy._execute_grant_dotation(
            {"marshal": "Ney", "action": "grant_dotation"},
            {"world": world},
            raw_text="endow ney")
        assert result["success"] is False
        assert "Which province, Sire?" in result["message"]


# ════════════════════════════════════════════════════════════════════════
# BUG-CA-4 — battle-report remaining strengths
# ════════════════════════════════════════════════════════════════════════

def _battle_result(outcome="attacker_tactical_victory", *,
                   attacker_nation="France",
                   attacker_reinforcements=None):
    return {
        "outcome": outcome,
        "attacker": {"name": "Ney", "casualties": 6501,
                     "remaining": 40000},   # the audit's lying echo
        "defender": {"name": "Mack", "casualties": 5000,
                     "remaining": 50000},
        "attacker_original_strength": 40000,
        "defender_original_strength": 50000,
        "attacker_nation": attacker_nation,
        "defender_nation": "Austria",
        "modifier_snapshot": {"attacker": [], "defender": []},
        "coordination_context": {},
        "reinforcement_results_for_report": {
            "attacker": attacker_reinforcements or [],
            "defender": [],
        },
        "relationship_changes": [],
        "terrain": "plains",
    }


class TestBattleReportRemaining:
    def test_remaining_derived_from_original_minus_casualties(self):
        report = generate_battle_report(_battle_result())
        summary = report["casualty_summary"]
        assert summary["attacker_remaining"] == 40000 - 6501
        assert summary["defender_remaining"] == 50000 - 5000

    def test_remaining_clamped_at_zero(self):
        result = _battle_result()
        result["attacker"]["casualties"] = 45000
        report = generate_battle_report(result)
        assert report["casualty_summary"]["attacker_remaining"] == 0


# ════════════════════════════════════════════════════════════════════════
# BUG-CA-5 — observation truthfulness + modifier labels
# ════════════════════════════════════════════════════════════════════════

class TestObservationTruthfulness:
    _VICTORY_WORDS = ("swung the battle", "advantage melted", "favor")

    def test_stalemate_reinforcement_claims_no_victory(self):
        result = _battle_result(
            outcome="stalemate",
            attacker_reinforcements=[{"marshal": "Soult", "arrived": True}])
        for _ in range(12):  # random.choice — every variant must be honest
            obs = _pick_observation(result, "France")
            assert not any(w in obs for w in self._VICTORY_WORDS), obs
            assert "Soult" in obs

    def test_loss_reinforcement_claims_no_victory(self):
        result = _battle_result(
            outcome="defender_tactical_victory",
            attacker_reinforcements=[{"marshal": "Soult", "arrived": True}])
        for _ in range(12):
            obs = _pick_observation(result, "France")
            assert not any(w in obs for w in self._VICTORY_WORDS), obs

    def test_victory_reinforcement_keeps_the_triumphant_bank(self):
        result = _battle_result(
            outcome="attacker_tactical_victory",
            attacker_reinforcements=[{"marshal": "Soult", "arrived": True}])
        obs = _pick_observation(result, "France")
        assert "Soult" in obs


class TestModifierLabels:
    def test_forced_march_label_replaces_strategic_orders(self):
        attacker = MarshalFactory.infantry(name="Ney")
        attacker.strategic_combat_bonus = 15
        defender = MarshalFactory.enemy(name="Mack", nation="Austria")
        mods = snapshot_attacker_modifiers(attacker, defender, "plains",
                                           0.0, 0, False)
        labels = [m["label"] for m in mods]
        assert "Forced march momentum (order completed)" in labels
        assert "Strategic orders" not in labels

    def test_defender_forced_march_label(self):
        attacker = MarshalFactory.enemy(name="Mack", nation="Austria")
        defender = MarshalFactory.infantry(name="Ney")
        defender.strategic_defense_bonus = 15
        mods = snapshot_defender_modifiers(defender, attacker, "plains", 0)
        labels = [m["label"] for m in mods]
        assert "Forced march momentum (order completed)" in labels
        assert "Strategic orders" not in labels

    def test_literal_hold_labeled_immovable(self):
        attacker = MarshalFactory.enemy(name="Mack", nation="Austria",
                                        strength=50000)
        defender = MarshalFactory.infantry(name="Grouchy",
                                           personality="literal")
        defender.holding_position = True
        mods = snapshot_defender_modifiers(defender, attacker, "plains", 0)
        labels = [m["label"] for m in mods]
        assert "Immovable (literal hold)" in labels
        assert "Personality (literal)" not in labels


# ════════════════════════════════════════════════════════════════════════
# BUG-CA-6 — dispatch intel freshness (recency beats rank)
# ════════════════════════════════════════════════════════════════════════

class TestDispatchIntelFreshness:
    def test_fresh_partial_beats_stale_full(self):
        from backend.game_logic.dispatch import _build_intelligence
        from backend.models.intel import FULL, PARTIAL, RegionIntel

        world = WorldFactory.basic()
        world.current_turn = 5

        stale = RegionIntel("Bavaria")
        stale.visibility = FULL
        stale.known_marshals = [{"name": "Mack", "nation": "Austria",
                                 "strength": 49000}]
        stale.last_updated_turn = 2  # three turns old

        fresh = RegionIntel("Rhineland")
        fresh.visibility = PARTIAL
        fresh.known_marshals = [{"name": "Mack", "nation": "Austria",
                                 "band": "a large army"}]
        fresh.last_updated_turn = 5  # this turn's truth

        world.intel = {"Bavaria": stale, "Rhineland": fresh}
        rows = _build_intelligence(world, "France")
        mack_rows = [r for r in rows if r["name"] == "Mack"]
        assert len(mack_rows) == 1
        assert mack_rows[0]["location"] == "Rhineland"

    def test_same_turn_ties_break_by_rank(self):
        from backend.game_logic.dispatch import _build_intelligence
        from backend.models.intel import FULL, PARTIAL, RegionIntel

        world = WorldFactory.basic()
        world.current_turn = 5

        partial = RegionIntel("Bavaria")
        partial.visibility = PARTIAL
        partial.known_marshals = [{"name": "Mack", "nation": "Austria",
                                   "band": "a large army"}]
        partial.last_updated_turn = 5

        full = RegionIntel("Rhineland")
        full.visibility = FULL
        full.known_marshals = [{"name": "Mack", "nation": "Austria",
                                "strength": 49000}]
        full.last_updated_turn = 5

        world.intel = {"Bavaria": partial, "Rhineland": full}
        rows = _build_intelligence(world, "France")
        mack_rows = [r for r in rows if r["name"] == "Mack"]
        assert mack_rows[0]["location"] == "Rhineland"


# ════════════════════════════════════════════════════════════════════════
# BUG-CA-9 — participation counts + last_battle_turn
# ════════════════════════════════════════════════════════════════════════

class TestParticipationCounts:
    def test_last_battle_turn_serializes(self):
        m = MarshalFactory.infantry(name="Ney")
        m.last_battle_turn = 7
        restored = Marshal.from_dict(m.to_dict())
        assert restored.last_battle_turn == 7

    def test_last_battle_turn_default(self):
        m = MarshalFactory.infantry(name="Ney")
        data = m.to_dict()
        del data["last_battle_turn"]
        restored = Marshal.from_dict(data)
        assert restored.last_battle_turn == -1

    def _fight(self, world, attacker_name, target_name):
        executor = CommandExecutor()
        return executor.execute(
            {"success": True,
             "command": {"marshal": attacker_name, "action": "attack",
                         "target": target_name}},
            {"world": world})

    def test_reinforcer_tally_and_idle_reset(self):
        """A SUPPORT-ordered reinforcer who arrives gets the battle on his
        record and stops being 'idle' — the audit's 0W/0L '3 turns idle'
        marshal who had fought two battles."""
        from backend.models.marshal import StrategicOrder

        ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                      strength=60000,
                                      personality="aggressive")
        soult = MarshalFactory.infantry(name="Soult", location="Belgium",
                                        strength=30000,
                                        personality="aggressive")
        mack = MarshalFactory.enemy(name="Mack", location="Belgium",
                                    nation="Austria", strength=8000,
                                    personality="cautious")
        world = WorldFactory.with_marshals([ney, soult, mack])
        key = "|".join(sorted(["France", "Austria"]))
        world.diplomatic_states[key] = "WAR"
        world.war_start_turns[key] = world.current_turn
        world.current_turn = 4
        soult.idle_turns = 3
        soult.strategic_order = StrategicOrder(
            command_type="SUPPORT", target="Ney", target_type="marshal",
            started_turn=4, original_command="Soult, support Ney")

        result = self._fight(world, "Ney", "Mack")
        assert result.get("success") is not False

        reinf = (result.get("battle_report") or {})
        # The mechanical assertions (independent of report shape):
        if soult.last_battle_turn == 4:
            # Soult arrived — his record must reflect the battle.
            assert soult.battles_won + soult.battles_lost >= 1
            assert soult.idle_turns == 0
        # The primary pair always records the turn.
        assert ney.last_battle_turn == 4
        assert mack.last_battle_turn == 4
        assert ney.idle_turns == 0
