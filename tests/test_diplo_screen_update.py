"""
Tests for Diplomatic Screen Update — diplomatic_ledger.py enrichments,
wizard endpoint enrichments, and relation_history serialization.
"""
import unittest
from backend.models.world_state import WorldState
from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger


def _make_world(**overrides) -> WorldState:
    """Create a test WorldState with sensible defaults."""
    world = WorldState(player_nation="France")
    for k, v in overrides.items():
        setattr(world, k, v)
    return world


class TestNationsTradeIncome(unittest.TestCase):
    """N5: trade_income field per diplomatic state."""

    def test_nations_trade_income_peace(self):
        world = _make_world()
        # France-Austria is PEACE
        ledger = build_diplomatic_ledger(world)
        austria = next(n for n in ledger["nations"] if n["name"] == "Austria")
        self.assertEqual(austria["trade_income"], 50)

    def test_nations_trade_income_war(self):
        world = _make_world()
        # France-Britain is WAR → trade 0
        ledger = build_diplomatic_ledger(world)
        britain = next(n for n in ledger["nations"] if n["name"] == "Britain")
        self.assertEqual(britain["trade_income"], 0)

    def test_nations_trade_income_alliance(self):
        world = _make_world()
        key = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[key] = "ALLIANCE"
        ledger = build_diplomatic_ledger(world)
        austria = next(n for n in ledger["nations"] if n["name"] == "Austria")
        self.assertEqual(austria["trade_income"], 200)


class TestNationsRelationDescriptor(unittest.TestCase):
    """N6: relation_descriptor matches get_relation_descriptor()."""

    def test_nations_relation_descriptor(self):
        world = _make_world()
        ledger = build_diplomatic_ledger(world)
        for n in ledger["nations"]:
            self.assertIn("relation_descriptor", n)
            self.assertIsInstance(n["relation_descriptor"], str)
            self.assertNotEqual(n["relation_descriptor"], "")


class TestNationsRelationTrend(unittest.TestCase):
    """N7: relation_trend detection."""

    def test_nations_relation_trend_rising(self):
        world = _make_world()
        key = world._make_diplo_key("France", "Austria")
        world.relation_history = {key: [-30, -25]}  # Two snapshots
        world.nation_relations[key] = -10  # Current: big jump up
        ledger = build_diplomatic_ledger(world)
        austria = next(n for n in ledger["nations"] if n["name"] == "Austria")
        self.assertEqual(austria["relation_trend"], "rising")

    def test_nations_relation_trend_falling(self):
        world = _make_world()
        key = world._make_diplo_key("France", "Austria")
        world.relation_history = {key: [10, 5]}
        world.nation_relations[key] = -10
        ledger = build_diplomatic_ledger(world)
        austria = next(n for n in ledger["nations"] if n["name"] == "Austria")
        self.assertEqual(austria["relation_trend"], "falling")

    def test_nations_relation_trend_stable(self):
        world = _make_world()
        key = world._make_diplo_key("France", "Austria")
        world.relation_history = {key: [-30, -30]}
        world.nation_relations[key] = -30
        ledger = build_diplomatic_ledger(world)
        austria = next(n for n in ledger["nations"] if n["name"] == "Austria")
        self.assertEqual(austria["relation_trend"], "stable")

    def test_nations_relation_trend_insufficient_history(self):
        world = _make_world()
        # No history — should be stable
        ledger = build_diplomatic_ledger(world)
        austria = next(n for n in ledger["nations"] if n["name"] == "Austria")
        self.assertEqual(austria["relation_trend"], "stable")


class TestTreatiesTurnSigned(unittest.TestCase):
    """T2: turn_signed field present."""

    def test_treaties_turn_signed(self):
        world = _make_world()
        key = world._make_diplo_key("France", "Austria")
        world.active_treaties[key] = {
            "type": "non_aggression",
            "nations": ["France", "Austria"],
            "clauses": [],
            "turn_signed": 5,
        }
        ledger = build_diplomatic_ledger(world)
        self.assertTrue(len(ledger["treaties"]) > 0)
        treaty = ledger["treaties"][0]
        self.assertEqual(treaty["turn_signed"], 5)


class TestTreatiesInvolvesPlayer(unittest.TestCase):
    """T3: involves_player distinction."""

    def test_treaties_involves_player(self):
        world = _make_world()
        key = world._make_diplo_key("France", "Austria")
        world.active_treaties[key] = {
            "type": "non_aggression",
            "nations": ["France", "Austria"],
            "clauses": [],
        }
        # AI-AI treaty
        ai_key = world._make_diplo_key("Austria", "Prussia")
        world.active_treaties[ai_key] = {
            "type": "defensive_alliance",
            "nations": ["Austria", "Prussia"],
            "clauses": [],
        }
        ledger = build_diplomatic_ledger(world)
        player_treaty = next(t for t in ledger["treaties"] if "France" in [t["nation_a"], t["nation_b"]])
        ai_treaty = next(t for t in ledger["treaties"] if "France" not in [t["nation_a"], t["nation_b"]])
        self.assertTrue(player_treaty["involves_player"])
        self.assertFalse(ai_treaty["involves_player"])


class TestTreatiesArmisticeRemaining(unittest.TestCase):
    """T4: armistice countdown."""

    def test_treaties_armistice_remaining(self):
        world = _make_world()
        key = world._make_diplo_key("France", "Austria")
        world.active_treaties[key] = {
            "type": "armistice",
            "nations": ["France", "Austria"],
            "clauses": [],
        }
        world.armistice_turns = {key: 2}
        ledger = build_diplomatic_ledger(world)
        treaty = next(t for t in ledger["treaties"] if t["treaty_type"] == "armistice")
        self.assertEqual(treaty["armistice_remaining"], 3)  # 5 - 2


class TestThreatCoalitionCooldown(unittest.TestCase):
    """TH2: coalition cooldown value passed through."""

    def test_threat_coalition_cooldown(self):
        world = _make_world()
        world.coalition_cooldown = 4
        ledger = build_diplomatic_ledger(world)
        self.assertEqual(ledger["threat_coalition"]["coalition_cooldown"], 4)


class TestThreatSourceLabels(unittest.TestCase):
    """TH3: threat source keys mapped to labels."""

    def test_threat_source_labels(self):
        world = _make_world()
        world.threat_sources_this_turn = [
            {"source": "battle_win", "amount": 5},
            {"source": "capital_capture", "amount": 10},
        ]
        ledger = build_diplomatic_ledger(world)
        sources = ledger["threat_coalition"]["threat_sources_this_turn"]
        self.assertEqual(len(sources), 2)
        self.assertEqual(sources[0]["label"], "Won a battle")
        self.assertEqual(sources[1]["label"], "Captured an enemy capital")
        self.assertIn("display", sources[0])


class TestTalleyrandDPBreakdown(unittest.TestCase):
    """TA3: dp_breakdown components."""

    def test_talleyrand_dp_breakdown_components(self):
        world = _make_world()
        ledger = build_diplomatic_ledger(world)
        breakdown = ledger["talleyrand"]["dp_breakdown"]
        self.assertIn("base", breakdown)
        self.assertIn("skill_bonus", breakdown)
        self.assertIn("authority_bonus", breakdown)
        self.assertIn("capital_penalty", breakdown)
        self.assertEqual(breakdown["base"], 3)

    def test_talleyrand_dp_breakdown_capital_penalty(self):
        world = _make_world()
        # Lose Paris
        paris = world.regions.get("Paris")
        if paris:
            paris.controller = "Prussia"
        ledger = build_diplomatic_ledger(world)
        breakdown = ledger["talleyrand"]["dp_breakdown"]
        self.assertEqual(breakdown["capital_penalty"], -1)

    def test_talleyrand_dp_breakdown_skill_bonus(self):
        world = _make_world()
        # Talleyrand default skill is 10 >= 8
        ledger = build_diplomatic_ledger(world)
        breakdown = ledger["talleyrand"]["dp_breakdown"]
        self.assertEqual(breakdown["skill_bonus"], 1)


class TestTalleyrandMissionEffect(unittest.TestCase):
    """TA4: mission effect_text per mission type."""

    def test_talleyrand_mission_effect_text(self):
        world = _make_world()
        world.active_diplomatic_mission = {
            "type": "IMPROVE_RELATIONS",
            "target": "Austria",
            "turns_active": 2,
            "completed": False,
            "paused": False,
        }
        ledger = build_diplomatic_ledger(world)
        mission = ledger["talleyrand"]["active_mission"]
        self.assertIsNotNone(mission)
        self.assertEqual(mission["effect_text"], "+5 relation per turn")
        self.assertEqual(mission["dp_cost_per_turn"], 1)

    def test_talleyrand_mission_remaining_turns(self):
        world = _make_world()
        world.active_diplomatic_mission = {
            "type": "GATHER_INTEL",
            "target": "Austria",
            "turns_active": 1,
            "completed": False,
            "paused": False,
        }
        ledger = build_diplomatic_ledger(world)
        mission = ledger["talleyrand"]["active_mission"]
        self.assertIsNotNone(mission)
        # GATHER_INTEL duration=3, turns_active=1, remaining=2
        self.assertEqual(mission["remaining_turns"], 2)


class TestTalleyrandHistoryAndReliability(unittest.TestCase):
    """TA1, TA2: diplomatic history and reliability rendered."""

    def test_talleyrand_history_rendered(self):
        world = _make_world()
        world.diplomatic_history = [
            {"turn": 3, "type": "proposal_accepted", "target": "Austria", "nation": "France", "proposal_type": "peace"},
        ]
        ledger = build_diplomatic_ledger(world)
        history = ledger["talleyrand"]["diplomatic_history"]
        self.assertTrue(len(history) > 0)
        self.assertEqual(history[0]["turn"], 3)

    def test_talleyrand_reliability_rendered(self):
        world = _make_world()
        world.diplomatic_reliability = {"France": 15}
        ledger = build_diplomatic_ledger(world)
        self.assertEqual(ledger["talleyrand"]["diplomatic_reliability"], 15)


class TestThreatSourceLabelFallback(unittest.TestCase):
    """TH3: Unknown source keys get title-cased fallback."""

    def test_unknown_source_key_fallback(self):
        world = _make_world()
        world.threat_sources_this_turn = [
            {"source": "broke_non_aggression", "amount": 8},
        ]
        ledger = build_diplomatic_ledger(world)
        sources = ledger["threat_coalition"]["threat_sources_this_turn"]
        self.assertEqual(len(sources), 1)
        # Fallback: "broke_non_aggression" → "Broke Non Aggression"
        self.assertEqual(sources[0]["label"], "Broke Non Aggression")
        self.assertIn("+8", sources[0]["display"])


class TestDPBreakdownAuthority(unittest.TestCase):
    """TA3: DP breakdown uses authority_tracker for player, not nation_authority."""

    def test_dp_breakdown_low_authority(self):
        world = _make_world()
        # Set player authority below 30 → should give -1 authority_bonus
        world.authority_tracker.authority = 20
        ledger = build_diplomatic_ledger(world)
        breakdown = ledger["talleyrand"]["dp_breakdown"]
        self.assertEqual(breakdown["authority_bonus"], -1)

    def test_dp_breakdown_high_authority(self):
        world = _make_world()
        world.authority_tracker.authority = 70
        ledger = build_diplomatic_ledger(world)
        breakdown = ledger["talleyrand"]["dp_breakdown"]
        self.assertEqual(breakdown["authority_bonus"], 1)

    def test_dp_breakdown_mid_authority(self):
        world = _make_world()
        world.authority_tracker.authority = 45  # 30-59 range → 0
        ledger = build_diplomatic_ledger(world)
        breakdown = ledger["talleyrand"]["dp_breakdown"]
        self.assertEqual(breakdown["authority_bonus"], 0)


class TestLedgerCurrentTurn(unittest.TestCase):
    """Top-level current_turn field."""

    def test_ledger_current_turn(self):
        world = _make_world()
        world.current_turn = 7
        ledger = build_diplomatic_ledger(world)
        self.assertEqual(ledger["current_turn"], 7)


# ═══════════════════════════════════════════════════════
# WIZARD ENDPOINT TESTS
# ═══════════════════════════════════════════════════════

class TestWizardStep1(unittest.TestCase):
    """W1, W2: Wizard Step 1 enrichment."""

    def _get_step1_response(self, world):
        """Simulate the Step 1 endpoint logic from main.py."""
        from backend.game_logic.diplomacy import _STATE_DISPLAY_NAMES, get_relation_descriptor
        player = world.player_nation
        enemy_nations = list(getattr(world, 'enemy_nations', []))
        vassals = getattr(world, 'vassals', {})
        active_mission = getattr(world, 'active_diplomatic_mission', None)
        mission_target = None
        if active_mission and not active_mission.get("completed"):
            mission_target = active_mission.get("target")

        categories = {"at_war": [], "treaties": [], "vassals": [], "neutral": []}
        treaty_states = {"ARMISTICE", "OPEN_BORDERS", "NON_AGGRESSION",
                         "DEFENSIVE_ALLIANCE", "ALLIANCE"}
        for n in enemy_nations:
            diplo_key = world._make_diplo_key(player, n)
            state = world.diplomatic_states.get(diplo_key, "PEACE")
            is_vassal = n in vassals
            relation = int(world.nation_relations.get(diplo_key, 0) or 0)
            entry = {
                "name": n,
                "state": state,
                "state_display": _STATE_DISPLAY_NAMES.get(state, state),
                "is_vassal": is_vassal,
                "relation": relation,
                "relation_descriptor": get_relation_descriptor(relation),
                "has_active_mission": (mission_target == n),
            }
            if is_vassal:
                categories["vassals"].append(entry)
            elif state == "WAR":
                categories["at_war"].append(entry)
            elif state in treaty_states:
                categories["treaties"].append(entry)
            else:
                categories["neutral"].append(entry)
        return categories

    def test_wizard_step1_includes_relation(self):
        world = _make_world()
        cats = self._get_step1_response(world)
        # Britain at war with France
        britain = cats["at_war"][0] if cats["at_war"] else None
        self.assertIsNotNone(britain)
        self.assertIn("relation", britain)
        self.assertIsInstance(britain["relation"], int)

    def test_wizard_step1_relation_descriptor(self):
        world = _make_world()
        cats = self._get_step1_response(world)
        for cat_list in cats.values():
            for entry in cat_list:
                self.assertIn("relation_descriptor", entry)
                self.assertIsInstance(entry["relation_descriptor"], str)

    def test_wizard_step1_mission_indicator(self):
        world = _make_world()
        world.active_diplomatic_mission = {
            "type": "IMPROVE_RELATIONS",
            "target": "Austria",
            "turns_active": 1,
            "completed": False,
        }
        cats = self._get_step1_response(world)
        austria = None
        for cat_list in cats.values():
            for entry in cat_list:
                if entry["name"] == "Austria":
                    austria = entry
                    break
        self.assertIsNotNone(austria)
        self.assertTrue(austria["has_active_mission"])
        # Others should be False
        for cat_list in cats.values():
            for entry in cat_list:
                if entry["name"] != "Austria":
                    self.assertFalse(entry["has_active_mission"])


class TestWizardStep2(unittest.TestCase):
    """W3, W5: Wizard Step 2 enrichment."""

    def test_wizard_step2_acceptance_preview(self):
        from backend.game_logic.diplomacy import get_diplomatic_preview
        world = _make_world()
        # Britain at WAR → has proposals → should have preview
        preview = get_diplomatic_preview(world, "Britain")
        # acceptance_preview may be None if no proposal available, or dict
        self.assertIn("acceptance_preview", preview)

    def test_wizard_step2_preview_top3(self):
        from backend.game_logic.diplomacy import get_diplomatic_preview
        world = _make_world()
        preview = get_diplomatic_preview(world, "Britain")
        ap = preview.get("acceptance_preview")
        if ap is not None:
            self.assertLessEqual(len(ap.get("positive", [])), 3)
            self.assertLessEqual(len(ap.get("negative", [])), 3)

    def test_wizard_step2_preview_labels(self):
        from backend.game_logic.diplomacy import get_diplomatic_preview
        world = _make_world()
        preview = get_diplomatic_preview(world, "Britain")
        ap = preview.get("acceptance_preview")
        if ap is not None:
            for entry in ap.get("positive", []) + ap.get("negative", []):
                self.assertIn("label", entry)
                self.assertIn("value", entry)
                self.assertIsInstance(entry["label"], str)

    def test_wizard_step2_mission_effect_text(self):
        from backend.game_logic.diplomacy import get_diplomatic_preview
        world = _make_world()
        # Austria at PEACE → has mission actions
        preview = get_diplomatic_preview(world, "Austria")
        actions = preview.get("actions", [])
        mission_actions = [a for a in actions if a["action"].startswith("mission_")]
        self.assertTrue(len(mission_actions) > 0)
        for ma in mission_actions:
            self.assertIn("effect_text", ma)
            if ma["action"] == "mission_improve_relations":
                self.assertEqual(ma["effect_text"], "+5 relation/turn")

    def test_wizard_step2_no_preview_no_proposals(self):
        from backend.game_logic.diplomacy import get_diplomatic_preview
        world = _make_world()
        # Set up alliance state so no upward proposals available
        key = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[key] = "ALLIANCE"
        world.nation_relations[key] = 60
        preview = get_diplomatic_preview(world, "Austria")
        # In ALLIANCE there are no propose_ actions → no acceptance_preview
        ap = preview.get("acceptance_preview")
        self.assertIsNone(ap)


# ═══════════════════════════════════════════════════════
# SERIALIZATION TESTS
# ═══════════════════════════════════════════════════════

class TestRelationHistorySerialization(unittest.TestCase):
    """N7: relation_history roundtrip."""

    def test_relation_history_serialization(self):
        world = _make_world()
        world.relation_history = {
            "Austria|France": [-30, -25, -20],
            "Britain|France": [-80, -75],
        }
        data = world.to_dict()
        restored = WorldState.from_dict(data)
        self.assertEqual(restored.relation_history["Austria|France"], [-30, -25, -20])
        self.assertEqual(restored.relation_history["Britain|France"], [-80, -75])

    def test_relation_history_snapshot(self):
        """advance_turn records current relations into history."""
        world = _make_world()
        self.assertEqual(world.relation_history, {})
        # Run advance_turn
        world.advance_turn()
        # Should now have snapshots for all relation keys
        for key in world.nation_relations:
            self.assertIn(key, world.relation_history)
            self.assertEqual(len(world.relation_history[key]), 1)


if __name__ == "__main__":
    unittest.main()
