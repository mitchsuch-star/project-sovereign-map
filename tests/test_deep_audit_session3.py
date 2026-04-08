"""
Tests for Deep Audit Session 3: Diplomatic State Machine & War Score Sign.

Covers 13 real fixes (4 false positives, 1 subsumed, 1 doc-only skipped):
- Fix 1: War score sign — get_war_score_for() replaces raw war_scores.get()
- Fix 2: Stale proposal auto-rejected when diplomatic state changed
- Fix 3: break_treaty from WAR/ARMISTICE calls cleanup_war_end
- Fix 4: Ultimatum acceptance calls cleanup_war_end
- Fix 5: Auto-downgrade clears active_treaties
- Fix 6: Armistice→WAR clears active_treaties
- Fix 7: Self-war returns failure
- Fix 9: AI break_treaty doesn't add coalition threat
- Fix 11: _ratify_treaty failure shows rejection, not acceptance
- Fix 12: break_treaty clears proposal_in_transit for broken pair
- Fix 14: validate_transition allows VASSAL→NON_AGGRESSION
- Fix 15: Vassal-third-party relation decay not skipped
- Fix 17: Casus belli halves coalition threat on war declaration
"""

from backend.models.marshal import Marshal
from backend.models.world_state import WorldState
from backend.game_logic.diplomacy import (  # noqa: F401
    declare_war, break_treaty, validate_transition, get_war_score_for,
    _process_armistice_expiration, _process_relation_decay, check_auto_downgrade,
)


# ════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════

def _make_marshal(name="TestInf", location="Paris", strength=30000,
                  personality="cautious", nation="France",
                  cavalry=False, artillery=False, **kw):
    return Marshal(
        name=name, location=location, strength=strength,
        personality=personality, nation=nation,
        movement_range=2 if cavalry else 1,
        tactical_skill=7,
        skills=kw.pop("skills", {
            "tactical": 7, "shock": 7, "defense": 7,
            "logistics": 7, "administration": 7, "command": 7,
        }),
        cavalry=cavalry, artillery=artillery,
        spawn_location=kw.pop("spawn_location", location),
        **kw,
    )


def _make_world(current_turn=5):
    """Basic WorldState with France as player."""
    world = WorldState()
    world.current_turn = current_turn
    world.marshals.clear()
    m = _make_marshal()
    world.marshals[m.name] = m
    return world


def _make_war_world(nation_a="France", nation_b="Austria", war_score=15):
    """World with two nations at war and a war score set."""
    world = _make_world()
    diplo_key = world._make_diplo_key(nation_a, nation_b)
    world.diplomatic_states[diplo_key] = "WAR"
    world.war_scores[diplo_key] = war_score
    world.war_start_turns = {diplo_key: 1}
    return world


# ════════════════════════════════════════════════════════════════
# FIX 1: WAR SCORE SIGN BUG
# ════════════════════════════════════════════════════════════════

class TestFix1WarScoreSign:
    """get_war_score_for returns correct sign regardless of alphabetical key order."""

    def test_france_before_target_alphabetically(self):
        """France|Prussia — France is first, raw score is France's perspective."""
        world = _make_war_world("France", "Prussia", war_score=20)
        # France is alphabetically before Prussia, so raw score is already France's
        assert get_war_score_for(world, "France", "Prussia") == 20
        assert get_war_score_for(world, "Prussia", "France") == -20

    def test_france_after_target_alphabetically(self):
        """Austria|France — France is second, raw score is Austria's perspective."""
        world = _make_war_world("Austria", "France", war_score=10)
        # Key is Austria|France, raw 10 = Austria winning
        # France should see -10
        assert get_war_score_for(world, "France", "Austria") == -10
        assert get_war_score_for(world, "Austria", "France") == 10

    def test_get_game_bucket_uses_correct_sign(self):
        """get_game_bucket returns correct war bucket when France is alphabetically second."""
        from backend.game_logic.diplomatic_dialogue import get_game_bucket
        # Austria|France key, raw score 25 = Austria winning
        world = _make_war_world("Austria", "France", war_score=25)
        # France is losing badly (score -25 from France's perspective)
        bucket = get_game_bucket("Austria", world)
        assert bucket == "losing_slightly"  # -25 > -30

    def test_context_snapshot_war_score_sign(self):
        """generate_dialogue context snapshot uses correct war score sign."""
        from backend.game_logic.diplomatic_dialogue import generate_dialogue
        world = _make_war_world("Austria", "France", war_score=30)
        # France sees -30
        parsed = {"action": "propose_peace", "target_nation": "Austria"}
        dialogue = generate_dialogue("greeting", parsed, world)
        assert dialogue["context"]["war_score"] == -30

    def test_template_slot_war_score_sign(self):
        """resolve_template_text uses get_war_score_for for {war_score} slot."""
        from backend.game_logic.diplomatic_templates import resolve_template_text
        world = _make_war_world("Austria", "France", war_score=15)
        result = resolve_template_text("Score: {war_score}", world, target_nation="Austria")
        # France perspective: Austria|France raw=15 (Austria winning), France sees -15
        assert result == "Score: -15"


# ════════════════════════════════════════════════════════════════
# FIX 2: STALE PROPOSAL BYPASSES STATE CHANGES
# ════════════════════════════════════════════════════════════════

class TestFix2StaleProposal:
    """Proposals sent before state change are auto-rejected on delivery."""

    def test_proposal_rejected_when_state_changed(self):
        """Peace proposal sent during WAR, but alliance formed before delivery — now invalid."""
        world = _make_world(current_turn=5)
        diplo_key = world._make_diplo_key("France", "Austria")
        # Proposal was sent last turn for peace (requires WAR state)
        world.proposal_in_transit = {
            "turn_sent": 4,
            "target": "Austria",
            "proposal": {
                "type": "peace",
                "proposer_nation": "France",
                "target_nation": "Austria",
                "sweeteners": [],
                "demands": [],
                "clauses": [],
            },
        }
        # But state changed to ALLIANCE between send and delivery
        # WAR→PEACE is valid, ALLIANCE→PEACE is not (downgrade)
        world.diplomatic_states[diplo_key] = "ALLIANCE"
        world.nation_relations[diplo_key] = 80

        events = world._process_proposal_in_transit()
        assert len(events) >= 1
        assert events[0]["outcome"] == "REJECT"
        assert "diplomatic situation has changed" in events[0]["message"]
        assert world.proposal_in_transit is None

    def test_valid_proposal_still_processed(self):
        """Peace proposal during WAR is still valid and gets processed normally."""
        world = _make_world(current_turn=5)
        diplo_key = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[diplo_key] = "WAR"
        world.war_scores[diplo_key] = 0
        world.nation_relations[diplo_key] = 50

        world.proposal_in_transit = {
            "turn_sent": 4,
            "target": "Austria",
            "proposal": {
                "type": "peace",
                "proposer_nation": "France",
                "target_nation": "Austria",
                "sweeteners": [],
                "demands": [],
                "clauses": [],
            },
        }

        events = world._process_proposal_in_transit()
        # Should NOT be auto-rejected (WAR→PEACE is valid transition)
        assert len(events) >= 1
        # Outcome determined by acceptance formula, not stale-reject
        assert events[0]["outcome"] in ("ACCEPT", "REJECT", "COUNTER_OFFER")


# ════════════════════════════════════════════════════════════════
# FIX 3: BREAK_TREATY FROM WAR/ARMISTICE CALLS CLEANUP
# ════════════════════════════════════════════════════════════════

class TestFix3BreakTreatyWarCleanup:
    """break_treaty from WAR/ARMISTICE calls cleanup_war_end."""

    def test_break_from_war_clears_war_scores(self):
        """Breaking treaty during WAR should clear war scores."""
        world = _make_war_world("France", "Austria", war_score=20)
        diplo_key = world._make_diplo_key("France", "Austria")
        # Need an active treaty to break
        world.active_treaties = {
            diplo_key: {"type": "peace", "nations": ["France", "Austria"]},
        }
        result = break_treaty(diplo_key, "France", world)
        assert result["success"]
        # War scores should be cleaned up
        assert diplo_key not in world.war_scores

    def test_break_from_armistice_clears_data(self):
        """Breaking treaty during ARMISTICE should clear war data."""
        world = _make_world()
        diplo_key = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[diplo_key] = "ARMISTICE"
        world.war_scores[diplo_key] = 10
        world.active_treaties = {
            diplo_key: {"type": "armistice", "nations": ["France", "Austria"]},
        }
        result = break_treaty(diplo_key, "France", world)
        assert result["success"]
        assert diplo_key not in world.war_scores


# ════════════════════════════════════════════════════════════════
# FIX 4: ULTIMATUM ACCEPTANCE CALLS CLEANUP
# ════════════════════════════════════════════════════════════════

class TestFix4UltimatumCleanup:
    """PL-14: Ultimatum now pushes dialogue instead of immediate resolution."""

    def test_ultimatum_pushes_dialogue(self):
        """Ultimatum pushes ultimatum_confirm dialogue (PL-14 rework)."""
        from backend.commands.executor import CommandExecutor

        world = _make_world()
        diplo_key = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[diplo_key] = "PEACE"
        world.diplomatic_points = 5

        executor = CommandExecutor()
        result = executor._execute_diplomatic_ultimatum(
            {"target_nation": "Austria"}, world
        )
        assert result["success"]
        # Dialogue pushed, not immediate resolution
        assert result.get("awaiting_diplomatic_response") is True
        dialogue = world.pending_diplomatic_dialogue
        assert dialogue is not None
        assert dialogue["type"] == "ultimatum_confirm"
        assert dialogue["target_nation"] == "Austria"
        # DP not deducted yet (deducted on delivery)
        assert world.diplomatic_points == 5


# ════════════════════════════════════════════════════════════════
# FIX 5: AUTO-DOWNGRADE CLEARS ACTIVE_TREATIES
# ════════════════════════════════════════════════════════════════

class TestFix5AutoDowngradeTreaty:
    """Auto-downgrade from relation collapse clears active_treaties."""

    def test_auto_downgrade_removes_treaty(self):
        """When alliance auto-downgrades, the old treaty entry is removed."""
        world = _make_world(current_turn=10)
        diplo_key = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[diplo_key] = "ALLIANCE"
        world.active_treaties = {
            diplo_key: {"type": "alliance", "nations": ["France", "Austria"]},
        }
        # Set relation well below threshold, and turns_below_threshold to trigger
        world.nation_relations[diplo_key] = -80
        world.turns_below_threshold = {diplo_key: 5}

        events = check_auto_downgrade(world)

        # Should have downgraded
        found_downgrade = any(e.get("type") == "auto_downgrade" for e in events)
        assert found_downgrade
        # Treaty should be cleared
        assert diplo_key not in world.active_treaties


# ════════════════════════════════════════════════════════════════
# FIX 6: ARMISTICE→WAR CLEARS ACTIVE_TREATIES
# ════════════════════════════════════════════════════════════════

class TestFix6ArmisticeWarTreaty:
    """Armistice expiring to WAR clears active_treaties."""

    def test_armistice_to_war_clears_treaty(self):
        """When armistice expires with hostile relations, active treaty is cleared."""
        world = _make_world(current_turn=10)
        diplo_key = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[diplo_key] = "ARMISTICE"
        world.armistice_turns = {diplo_key: 4}  # Incremented to 5 → expires this turn
        world.nation_relations[diplo_key] = -80  # Hostile → reverts to WAR
        world.active_treaties = {
            diplo_key: {"type": "armistice", "nations": ["France", "Austria"]},
        }

        events = _process_armistice_expiration(world)

        assert world.diplomatic_states[diplo_key] == "WAR"
        assert diplo_key not in world.active_treaties


# ════════════════════════════════════════════════════════════════
# FIX 7: SELF-WAR PREVENTION
# ════════════════════════════════════════════════════════════════

class TestFix7SelfWar:
    """declare_war rejects self-war."""

    def test_self_war_returns_failure(self):
        world = _make_world()
        result = declare_war(world, "France", "France")
        assert not result["success"]
        assert "cannot declare war on itself" in result["message"].lower()


# ════════════════════════════════════════════════════════════════
# FIX 9: AI BREAK_TREATY THREAT
# ════════════════════════════════════════════════════════════════

class TestFix9AIBreakThreat:
    """AI breaking treaty doesn't add to France's coalition threat."""

    def test_ai_break_no_threat(self):
        world = _make_world()
        diplo_key = world._make_diplo_key("Austria", "Prussia")
        world.diplomatic_states[diplo_key] = "ALLIANCE"
        world.active_treaties = {
            diplo_key: {"type": "alliance", "nations": ["Austria", "Prussia"]},
        }
        world.nation_relations[diplo_key] = 50
        # Austria needs DP to break treaty
        world.nation_dp = {"Austria": 5, "Prussia": 5}
        threat_before = getattr(world, 'threat_level', 0)

        result = break_treaty(diplo_key, "Austria", world)
        assert result["success"]

        threat_after = getattr(world, 'threat_level', 0)
        assert threat_after == threat_before  # No threat added

    def test_player_break_adds_threat(self):
        world = _make_world()
        diplo_key = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[diplo_key] = "ALLIANCE"
        world.active_treaties = {
            diplo_key: {"type": "alliance", "nations": ["France", "Austria"]},
        }
        world.nation_relations[diplo_key] = 50
        threat_before = getattr(world, 'threat_level', 0)

        result = break_treaty(diplo_key, "France", world)
        assert result["success"]

        threat_after = getattr(world, 'threat_level', 0)
        assert threat_after > threat_before  # Threat added for player


# ════════════════════════════════════════════════════════════════
# FIX 11: RATIFY FAILURE SHOWS REJECTION
# ════════════════════════════════════════════════════════════════

class TestFix11RatifyFailure:
    """_ratify_treaty failure yields REJECT outcome, not ACCEPT."""

    def test_ratify_failure_returns_reject(self):
        """If _ratify_treaty returns a failure event, proposal shows as rejected."""
        from unittest.mock import patch

        world = _make_world(current_turn=5)
        diplo_key = world._make_diplo_key("France", "Austria")
        # Set state to ALLIANCE — proposing alliance again would fail (downgrade guard)
        world.diplomatic_states[diplo_key] = "ALLIANCE"

        world.proposal_in_transit = {
            "turn_sent": 4,
            "target": "Austria",
            "proposal": {
                "type": "alliance",
                "proposer_nation": "France",
                "target_nation": "Austria",
                "sweeteners": [],
                "demands": [],
                "clauses": [],
            },
        }

        # Force acceptance from formula so we reach _ratify_treaty
        # But validate_transition ALLIANCE→ALLIANCE is False, so Fix 2 catches it first
        # Let's test differently: set to NON_AGGRESSION (valid transition for alliance)
        # but _ratify_treaty will fail because already at higher state
        # Actually, let's use a more realistic scenario: mock acceptance + have ratify fail
        world.diplomatic_states[diplo_key] = "NON_AGGRESSION"
        # Make nation_relations high enough for alliance
        world.nation_relations[diplo_key] = 80

        with patch("backend.game_logic.diplomacy.calculate_acceptance") as mock_calc:
            mock_calc.return_value = {
                "outcome": "ACCEPT",
                "score": 80,
                "feedback": "Excellent!",
                "components": {},
            }
            # Mock _ratify_treaty to return a failure
            with patch.object(world, "_ratify_treaty") as mock_ratify:
                mock_ratify.return_value = {
                    "type": "diplomatic_treaty_failed",
                    "target": "Austria",
                    "message": "Relations insufficient.",
                }
                events = world._process_proposal_in_transit()

        # Should show REJECT, not ACCEPT
        returned_events = [e for e in events if e.get("type") == "diplomatic_proposal_returned"]
        assert len(returned_events) >= 1
        assert returned_events[0]["outcome"] == "REJECT"
        assert "diplomatic situation has changed" in returned_events[0]["message"]


# ════════════════════════════════════════════════════════════════
# FIX 12: BREAK_TREATY CLEARS PROPOSAL_IN_TRANSIT
# ════════════════════════════════════════════════════════════════

class TestFix12BreakClearsProposal:
    """break_treaty voids proposal_in_transit for the broken pair."""

    def test_break_clears_matching_proposal(self):
        world = _make_world()
        diplo_key = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[diplo_key] = "ALLIANCE"
        world.active_treaties = {
            diplo_key: {"type": "alliance", "nations": ["France", "Austria"]},
        }
        world.proposal_in_transit = {
            "turn_sent": 4,
            "target": "Austria",
            "proposal": {
                "type": "defensive_alliance",
                "proposer_nation": "France",
                "target_nation": "Austria",
            },
        }

        result = break_treaty(diplo_key, "France", world)
        assert result["success"]
        assert world.proposal_in_transit is None

    def test_break_preserves_unrelated_proposal(self):
        world = _make_world()
        diplo_key = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[diplo_key] = "ALLIANCE"
        world.active_treaties = {
            diplo_key: {"type": "alliance", "nations": ["France", "Austria"]},
        }
        # Proposal is for a DIFFERENT nation pair
        world.proposal_in_transit = {
            "turn_sent": 4,
            "target": "Prussia",
            "proposal": {
                "type": "peace",
                "proposer_nation": "France",
                "target_nation": "Prussia",
            },
        }

        result = break_treaty(diplo_key, "France", world)
        assert result["success"]
        assert world.proposal_in_transit is not None  # Preserved


# ════════════════════════════════════════════════════════════════
# FIX 14: VASSAL→NON_AGGRESSION VALID TRANSITION
# ════════════════════════════════════════════════════════════════

class TestFix14VassalTransition:
    """validate_transition allows VASSAL→NON_AGGRESSION."""

    def test_vassal_to_non_aggression_valid(self):
        assert validate_transition("VASSAL", "NON_AGGRESSION") is True

    def test_vassal_to_war_still_valid(self):
        assert validate_transition("VASSAL", "WAR") is True

    def test_vassal_to_peace_still_valid(self):
        assert validate_transition("VASSAL", "PEACE") is True


# ════════════════════════════════════════════════════════════════
# FIX 15: VASSAL-THIRD-PARTY RELATION DECAY
# ════════════════════════════════════════════════════════════════

class TestFix15VassalRelationDecay:
    """Vassal-third-party relation decay is NOT skipped."""

    def test_vassal_lord_pair_skipped(self):
        """Relation decay skips Saxony-France (vassal-lord pair)."""
        world = _make_world(current_turn=10)
        world.enemy_nations = ["Austria", "Prussia", "Saxony"]
        world.vassals = {"Saxony": {"lord": "France", "loyalty": 50}}

        dk = world._make_diplo_key("France", "Saxony")
        world.diplomatic_states[dk] = "VASSAL"
        world.nation_relations[dk] = 30  # Above 10 → should decay

        _process_relation_decay(world)

        # Lord-vassal pair should be unaffected (skipped)
        assert world.nation_relations[dk] == 30

    def test_vassal_third_party_not_skipped(self):
        """Relation decay runs for Saxony-Austria (vassal-third-party pair)."""
        world = _make_world(current_turn=10)
        world.enemy_nations = ["Austria", "Prussia", "Saxony"]
        world.vassals = {"Saxony": {"lord": "France", "loyalty": 50}}

        dk_vassal_third = world._make_diplo_key("Austria", "Saxony")
        world.diplomatic_states[dk_vassal_third] = "PEACE"
        world.nation_relations[dk_vassal_third] = 30  # Above 10 → should decay

        _process_relation_decay(world)

        # Third-party pair should have decayed (not skipped)
        assert world.nation_relations[dk_vassal_third] < 30


# ════════════════════════════════════════════════════════════════
# FIX 17: CASUS BELLI HALVES COALITION THREAT
# ════════════════════════════════════════════════════════════════

class TestFix17CasusBelliThreat:
    """Casus belli halves coalition threat on war declaration."""

    def test_war_declaration_normal_threat(self):
        """Without casus belli, war declaration adds 20 threat."""
        world = _make_world()
        world.threat_level = 0
        result = declare_war(world, "France", "Austria", casus_belli=False)
        assert result["success"]
        assert world.threat_level == 20

    def test_war_declaration_casus_belli_half_threat(self):
        """With casus belli, war declaration adds only 10 threat."""
        world = _make_world()
        world.threat_level = 0
        result = declare_war(world, "France", "Austria", casus_belli=True)
        assert result["success"]
        assert world.threat_level == 10
