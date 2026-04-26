"""WPS-C: Forced alliance + liberation tests.

Covers:
- Forced alliance clause in acceptance formula (base override -15, demand -20)
- Forced alliance ratification (ALLIANCE state, relation reset, Continental System, origin tag, threat)
- Forced alliance relation drift (-10/turn, lifecycle cleanup)
- Liberation clause ratification (release_vassal, DEFENSIVE_ALLIANCE, relation adjustments, threat reduction)
- Serialization round-trip for alliance_origins
- Campaign log event types and oneliners
- Harshness calculation for new clause types
"""
import pytest
from backend.models.world_state import WorldState


def _make_world():
    """Create a minimal WorldState for WPS-C tests."""
    world = WorldState()
    world.player_nation = "France"
    world.enemy_nations = ["Prussia", "Austria", "Britain", "Saxony"]
    world.current_turn = 10
    return world


def _put_at_war(world, a, b, war_score=0):
    from backend.game_logic.diplomacy import set_diplomatic_state
    set_diplomatic_state(world, a, b, "WAR", "test")
    diplo_key = world._make_diplo_key(a, b)
    world.war_start_turns[diplo_key] = 1
    world.war_scores[diplo_key] = war_score


def _make_peace_proposal_with_forced_alliance(proposer, target, war_score_mod=0):
    return {
        "type": "peace",
        "proposer_nation": proposer,
        "target_nation": target,
        "sweeteners": [],
        "demands": [
            {"type": "forced_alliance", "value": 1},
        ],
        "clauses": [],
    }


def _make_liberation_proposal():
    return {
        "type": "peace",
        "proposer_nation": "Austria",
        "target_nation": "France",
        "sweeteners": [],
        "demands": [
            {"type": "liberation", "value": 1,
             "vassal_nation": "Saxony", "lord_nation": "France",
             "liberator": "Austria"},
        ],
        "clauses": [],
    }


def _make_liberation_world():
    world = _make_world()
    from backend.game_logic.diplomacy import set_diplomatic_state
    set_diplomatic_state(world, "France", "Saxony", "WAR", "test")
    world.war_start_turns[world._make_diplo_key("France", "Saxony")] = 1
    world.vassals["Saxony"] = {
        "lord": "France",
        "loyalty": 60,
        "autonomy": "satellite",
        "path": "treaty",
        "created_turn": 1,
        "tribute_rate": 0.3,
        "carved_from": None,
        "regions": None,
    }
    set_diplomatic_state(world, "France", "Saxony", "VASSAL", "test")
    _put_at_war(world, "France", "Austria", war_score=-40)
    return world


# ═══════════════════════════════════════════════════════
# ACCEPTANCE FORMULA
# ═══════════════════════════════════════════════════════

class TestForcedAllianceAcceptance:
    def test_base_disposition_override(self):
        """Forced alliance clause overrides base from 30 to -15."""
        from backend.game_logic.diplomacy import calculate_acceptance
        world = _make_world()
        _put_at_war(world, "France", "Prussia", war_score=80)

        # Normal peace proposal
        normal = calculate_acceptance({
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [],
            "demands": [],
            "clauses": [],
        }, world)

        # Forced alliance proposal
        fa = calculate_acceptance(
            _make_peace_proposal_with_forced_alliance("France", "Prussia"),
            world,
        )

        assert normal["components"]["base_disposition"] == 30
        assert fa["components"]["base_disposition"] == -15

    def test_demand_penalty_applied(self):
        """Forced alliance demand contributes -20 to deal balance."""
        from backend.game_logic.diplomacy import calculate_acceptance
        world = _make_world()
        _put_at_war(world, "France", "Prussia", war_score=80)

        no_demands = calculate_acceptance({
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [],
            "demands": [],
            "clauses": [],
        }, world)

        with_fa = calculate_acceptance(
            _make_peace_proposal_with_forced_alliance("France", "Prussia"),
            world,
        )

        # Deal balance should be worse by -20 (forced_alliance demand)
        no_demand_balance = no_demands["components"]["deal_balance"]
        fa_balance = with_fa["components"]["deal_balance"]
        assert fa_balance < no_demand_balance
        assert abs(fa_balance - no_demand_balance - (-20)) < 0.1

    def test_high_war_score_makes_fa_achievable(self):
        """With war_score=80 and capital held, forced alliance can be accepted."""
        from backend.game_logic.diplomacy import calculate_acceptance
        from backend.models.region import NATION_CAPITALS
        world = _make_world()
        _put_at_war(world, "France", "Prussia", war_score=80)
        # France holds Berlin
        cap = NATION_CAPITALS.get("Prussia")
        if cap and cap in world.regions:
            world.regions[cap].controller = "France"
        # Improve relations to make it borderline
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.nation_relations[diplo_key] = 30

        result = calculate_acceptance(
            _make_peace_proposal_with_forced_alliance("France", "Prussia"),
            world,
        )
        # Military supremacy (+25) should help
        assert result["components"]["military_supremacy"] == 25

    def test_low_war_score_rejects_fa(self):
        """Low war score makes forced alliance near-impossible."""
        from backend.game_logic.diplomacy import calculate_acceptance
        world = _make_world()
        _put_at_war(world, "France", "Prussia", war_score=20)

        result = calculate_acceptance(
            _make_peace_proposal_with_forced_alliance("France", "Prussia"),
            world,
        )
        assert result["outcome"] == "REJECT"


# ═══════════════════════════════════════════════════════
# RATIFICATION
# ═══════════════════════════════════════════════════════

class TestForcedAllianceRatification:
    def test_state_jumps_to_alliance(self):
        """Forced alliance ratification sets state to ALLIANCE."""
        world = _make_world()
        _put_at_war(world, "France", "Prussia", war_score=80)

        result = world._ratify_treaty({
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [],
            "demands": [{"type": "forced_alliance", "value": 1}],
            "clauses": [],
        })

        assert result is not None
        assert world.get_diplomatic_state("France", "Prussia") == "ALLIANCE"

    def test_relation_reset_to_zero(self):
        """Forced alliance resets relation to 0."""
        world = _make_world()
        _put_at_war(world, "France", "Prussia", war_score=80)
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.nation_relations[diplo_key] = -50

        world._ratify_treaty({
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [],
            "demands": [{"type": "forced_alliance", "value": 1}],
            "clauses": [],
        })

        assert world.nation_relations[diplo_key] == 0

    def test_continental_system_membership(self):
        """Forced alliance adds target to Continental System."""
        world = _make_world()
        _put_at_war(world, "France", "Prussia", war_score=80)
        assert "Prussia" not in world.continental_system_members

        world._ratify_treaty({
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [],
            "demands": [{"type": "forced_alliance", "value": 1}],
            "clauses": [],
        })

        assert "Prussia" in world.continental_system_members

    def test_origin_tag_set(self):
        """Forced alliance sets alliance_origins to 'forced'."""
        world = _make_world()
        _put_at_war(world, "France", "Prussia", war_score=80)

        world._ratify_treaty({
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [],
            "demands": [{"type": "forced_alliance", "value": 1}],
            "clauses": [],
        })

        diplo_key = world._make_diplo_key("France", "Prussia")
        assert world.alliance_origins.get(diplo_key) == "forced"

    def test_threat_generated(self):
        """Forced alliance generates +15 coalition threat."""
        world = _make_world()
        _put_at_war(world, "France", "Prussia", war_score=80)
        before = int(world.threat_level)

        world._ratify_treaty({
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [],
            "demands": [{"type": "forced_alliance", "value": 1}],
            "clauses": [],
        })

        assert world.threat_level >= before + 15

    def test_campaign_log_event(self):
        """Forced alliance emits a forced_alliance_imposed event."""
        world = _make_world()
        _put_at_war(world, "France", "Prussia", war_score=80)

        world._ratify_treaty({
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [],
            "demands": [{"type": "forced_alliance", "value": 1}],
            "clauses": [],
        })

        fa_events = [e for e in world.event_log if e.get("type") == "forced_alliance_imposed"]
        assert len(fa_events) >= 1
        assert fa_events[0]["imposer"] == "France"
        assert fa_events[0]["target"] == "Prussia"

    def test_existing_continental_system_membership_not_duplicated(self):
        """Forced alliance does not duplicate an existing Continental System member."""
        world = _make_world()
        _put_at_war(world, "France", "Prussia", war_score=80)
        world.continental_system_members = ["Prussia"]

        world._ratify_treaty({
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [],
            "demands": [{"type": "forced_alliance", "value": 1}],
            "clauses": [],
        })

        assert world.continental_system_members.count("Prussia") == 1

    def test_multiple_forced_alliance_clauses_process_independently(self):
        """Multiple forced-alliance clauses in one treaty each apply to their own pair."""
        world = _make_world()
        _put_at_war(world, "France", "Prussia", war_score=80)
        _put_at_war(world, "France", "Austria", war_score=80)
        austria_key = world._make_diplo_key("France", "Austria")
        before_threat = int(world.threat_level)

        world._ratify_treaty({
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [],
            "demands": [
                {"type": "forced_alliance", "value": 1},
                {"type": "forced_alliance", "value": 1,
                 "from_nation": "Austria", "to_nation": "France"},
            ],
            "clauses": [],
        })

        assert world.get_diplomatic_state("France", "Prussia") == "ALLIANCE"
        assert world.get_diplomatic_state("France", "Austria") == "ALLIANCE"
        assert world.alliance_origins[world._make_diplo_key("France", "Prussia")] == "forced"
        assert world.alliance_origins[austria_key] == "forced"
        assert "Prussia" in world.continental_system_members
        assert "Austria" in world.continental_system_members
        assert austria_key not in world.war_scores
        assert world.threat_level == before_threat + 30
        fa_events = [e for e in world.event_log if e.get("type") == "forced_alliance_imposed"]
        assert len(fa_events) == 2


# ═══════════════════════════════════════════════════════
# FORCED ALLIANCE DRIFT
# ═══════════════════════════════════════════════════════

class TestForcedAllianceDrift:
    def test_drift_applies_minus_10(self):
        """Forced alliance applies -10/turn relation drift."""
        from backend.game_logic.diplomacy import _process_forced_alliance_drift
        world = _make_world()
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[diplo_key] = "ALLIANCE"
        world.alliance_origins[diplo_key] = "forced"
        world.nation_relations[diplo_key] = 0

        _process_forced_alliance_drift(world)

        assert world.nation_relations[diplo_key] == -10

    def test_no_drift_for_voluntary(self):
        """Voluntary alliances do not get forced-alliance drift."""
        from backend.game_logic.diplomacy import _process_forced_alliance_drift
        world = _make_world()
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[diplo_key] = "ALLIANCE"
        world.alliance_origins[diplo_key] = "voluntary"
        world.nation_relations[diplo_key] = 0

        _process_forced_alliance_drift(world)

        assert world.nation_relations[diplo_key] == 0

    def test_drift_clears_origin_on_state_drop(self):
        """If state is no longer ALLIANCE, origin is cleared during drift pass."""
        from backend.game_logic.diplomacy import _process_forced_alliance_drift
        world = _make_world()
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[diplo_key] = "DEFENSIVE_ALLIANCE"
        world.alliance_origins[diplo_key] = "forced"

        _process_forced_alliance_drift(world)

        assert diplo_key not in world.alliance_origins

    def test_origin_cleared_on_war_entry(self):
        """set_diplomatic_state clears origin when leaving ALLIANCE for WAR."""
        from backend.game_logic.diplomacy import set_diplomatic_state
        world = _make_world()
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[diplo_key] = "ALLIANCE"
        world.alliance_origins[diplo_key] = "forced"

        set_diplomatic_state(world, "France", "Prussia", "WAR", "test")

        assert diplo_key not in world.alliance_origins

    def test_multiple_forced_alliances_drift_simultaneously(self):
        """Drift processes each forced alliance origin independently."""
        from backend.game_logic.diplomacy import _process_forced_alliance_drift
        world = _make_world()
        prussia_key = world._make_diplo_key("France", "Prussia")
        austria_key = world._make_diplo_key("France", "Austria")
        for diplo_key in (prussia_key, austria_key):
            world.diplomatic_states[diplo_key] = "ALLIANCE"
            world.alliance_origins[diplo_key] = "forced"
            world.nation_relations[diplo_key] = 0

        _process_forced_alliance_drift(world)

        assert world.nation_relations[prussia_key] == -10
        assert world.nation_relations[austria_key] == -10


# ═══════════════════════════════════════════════════════
# LIBERATION
# ═══════════════════════════════════════════════════════

class TestLiberationRatification:
    def _make_vassal_world(self):
        return _make_liberation_world()

    def test_liberation_releases_vassal(self):
        """Liberation clause releases the vassal."""
        world = self._make_vassal_world()
        assert "Saxony" in world.vassals

        world._ratify_treaty({
            "type": "peace",
            "proposer_nation": "Austria",
            "target_nation": "France",
            "sweeteners": [],
            "demands": [
                {"type": "liberation", "value": 1,
                 "vassal_nation": "Saxony", "lord_nation": "France",
                 "liberator": "Austria"},
            ],
            "clauses": [],
        })

        assert "Saxony" not in world.vassals

    def test_liberation_creates_defensive_alliance(self):
        """Liberated nation enters DEFENSIVE_ALLIANCE with liberator."""
        world = self._make_vassal_world()

        world._ratify_treaty({
            "type": "peace",
            "proposer_nation": "Austria",
            "target_nation": "France",
            "sweeteners": [],
            "demands": [
                {"type": "liberation", "value": 1,
                 "vassal_nation": "Saxony", "lord_nation": "France",
                 "liberator": "Austria"},
            ],
            "clauses": [],
        })

        assert world.get_diplomatic_state("Austria", "Saxony") == "DEFENSIVE_ALLIANCE"

    def test_liberation_relation_adjustments(self):
        """Liberation applies -20 to lord, +30 to liberator."""
        world = self._make_vassal_world()
        # Set baselines
        france_saxony_key = world._make_diplo_key("France", "Saxony")
        austria_saxony_key = world._make_diplo_key("Austria", "Saxony")
        world.nation_relations[france_saxony_key] = 0
        world.nation_relations[austria_saxony_key] = 0

        world._ratify_treaty({
            "type": "peace",
            "proposer_nation": "Austria",
            "target_nation": "France",
            "sweeteners": [],
            "demands": [
                {"type": "liberation", "value": 1,
                 "vassal_nation": "Saxony", "lord_nation": "France",
                 "liberator": "Austria"},
            ],
            "clauses": [],
        })

        assert world.nation_relations[france_saxony_key] == -20
        assert world.nation_relations[austria_saxony_key] == 30

    def test_liberation_reduces_threat(self):
        """Liberation reduces threat by 8."""
        world = self._make_vassal_world()
        world.threat_level = 50
        before = world.threat_level

        world._ratify_treaty({
            "type": "peace",
            "proposer_nation": "Austria",
            "target_nation": "France",
            "sweeteners": [],
            "demands": [
                {"type": "liberation", "value": 1,
                 "vassal_nation": "Saxony", "lord_nation": "France",
                 "liberator": "Austria"},
            ],
            "clauses": [],
        })

        assert world.threat_level == before - 8

    def test_liberation_emits_campaign_log_event(self):
        """Liberation ratification emits a vassal_liberated event."""
        world = self._make_vassal_world()

        world._ratify_treaty(_make_liberation_proposal())

        events = [e for e in world.event_log if e.get("type") == "vassal_liberated"]
        assert len(events) == 1
        assert events[0]["vassal_nation"] == "Saxony"
        assert events[0]["former_lord"] == "France"
        assert events[0]["liberator_nation"] == "Austria"


# ═══════════════════════════════════════════════════════
# SERIALIZATION
# ═══════════════════════════════════════════════════════

class TestSerialization:
    def test_alliance_origins_round_trip(self):
        """alliance_origins survives to_dict/from_dict."""
        world = _make_world()
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.alliance_origins[diplo_key] = "forced"

        data = world.to_dict()
        assert "alliance_origins" in data
        assert data["alliance_origins"][diplo_key] == "forced"

        world2 = WorldState.from_dict(data)
        assert world2.alliance_origins[diplo_key] == "forced"

    def test_empty_alliance_origins_default(self):
        """Pre-WPS-C saves load with {} default."""
        world = _make_world()
        data = world.to_dict()
        del data["alliance_origins"]

        world2 = WorldState.from_dict(data)
        assert world2.alliance_origins == {}


# ═══════════════════════════════════════════════════════
# CAMPAIGN LOG + HARSHNESS
# ═══════════════════════════════════════════════════════

class TestCampaignLogAndHarshness:
    def test_event_types_in_whitelist(self):
        """WPS-C event types are in CAMPAIGN_LOG_TYPES."""
        from backend.campaign_log import CAMPAIGN_LOG_TYPES, CATEGORY_MAP
        assert "forced_alliance_imposed" in CAMPAIGN_LOG_TYPES
        assert "vassal_liberated" in CAMPAIGN_LOG_TYPES
        assert CATEGORY_MAP["forced_alliance_imposed"] == "diplomacy"
        assert CATEGORY_MAP["vassal_liberated"] == "diplomacy"

    def test_forced_alliance_oneliner(self):
        from backend.campaign_log import format_event_oneliner
        event = {"type": "forced_alliance_imposed", "imposer": "France", "target": "Prussia"}
        line = format_event_oneliner(event)
        assert "Prussia" in line
        assert "France" in line
        assert "alliance" in line.lower()

    def test_forced_alliance_oneliner_accepts_spec_fields(self):
        from backend.campaign_log import format_event_oneliner
        event = {
            "type": "forced_alliance_imposed",
            "imposing_nation": "France",
            "forced_nation": "Prussia",
        }
        line = format_event_oneliner(event)
        assert "Prussia" in line
        assert "France" in line

    def test_liberation_oneliner(self):
        from backend.campaign_log import format_event_oneliner
        event = {"type": "vassal_liberated", "vassal_nation": "Saxony", "liberator": "Austria"}
        line = format_event_oneliner(event)
        assert "Saxony" in line
        assert "Austria" in line

    def test_liberation_oneliner_accepts_spec_fields(self):
        from backend.campaign_log import format_event_oneliner
        event = {
            "type": "vassal_liberated",
            "vassal_nation": "Saxony",
            "former_lord": "France",
            "liberator_nation": "Austria",
        }
        line = format_event_oneliner(event)
        assert "Saxony" in line
        assert "France" in line
        assert "Austria" in line

    def test_harshness_forced_alliance(self):
        from backend.game_logic.diplomatic_templates import calculate_treaty_harshness
        h = calculate_treaty_harshness({"demands": [{"type": "forced_alliance", "value": 1}]})
        assert h >= 0.4

    def test_harshness_forced_alliance_clause(self):
        from backend.game_logic.diplomatic_templates import calculate_treaty_harshness
        h = calculate_treaty_harshness({"clauses": [{"type": "forced_alliance", "amount": 1}]})
        assert h >= 0.4

    def test_harshness_liberation(self):
        from backend.game_logic.diplomatic_templates import calculate_treaty_harshness
        h = calculate_treaty_harshness({"demands": [{"type": "liberation", "value": 1}]})
        assert h >= 0.3

    def test_harshness_liberation_clause(self):
        from backend.game_logic.diplomatic_templates import calculate_treaty_harshness
        h = calculate_treaty_harshness({"clauses": [{"type": "liberation", "amount": 1}]})
        assert h >= 0.3

    def test_ratified_forced_alliance_stores_harshness(self):
        world = _make_world()
        _put_at_war(world, "France", "Prussia", war_score=80)
        world._ratify_treaty({
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [],
            "demands": [{"type": "forced_alliance", "value": 1}],
            "clauses": [],
        })
        diplo_key = world._make_diplo_key("France", "Prussia")
        assert world.active_treaties[diplo_key]["harshness"] >= 0.4

    def test_ratified_liberation_stores_harshness(self):
        world = _make_liberation_world()
        world._ratify_treaty(_make_liberation_proposal())
        diplo_key = world._make_diplo_key("Austria", "France")
        assert world.active_treaties[diplo_key]["harshness"] >= 0.3

    def test_demand_values_registered(self):
        """forced_alliance and liberation are in DEMAND_VALUES."""
        from backend.game_logic.diplomacy import DEMAND_VALUES
        assert "forced_alliance" in DEMAND_VALUES
        assert "liberation" in DEMAND_VALUES
        assert DEMAND_VALUES["forced_alliance"] == -20
        assert DEMAND_VALUES["liberation"] == -15
