"""WB-A: War bargain data model, creation, validation, and acceptance formula."""

from backend.game_logic.diplomacy import (
    _get_live_bargains,
    create_war_bargain_commitment,
    get_bargain_opposition_pairs,
    set_diplomatic_state,
    validate_war_bargain,
    _classify_witness_scope,
    calculate_acceptance,
    WITNESS_SCOPE_REGION_OBSERVER,
)
from backend.models.world_state import WorldState


def _wb_world() -> WorldState:
    world = WorldState()
    world.enemy_nations = ["Austria", "Prussia", "Britain", "Russia", "Saxony"]
    world.diplomatic_states = {}
    world.active_treaties = {}
    world.vassals = {}
    world.pending_dispatch_events = []
    world.event_log = []
    world.diplomatic_commitments = {}
    world.next_commitment_id = 1
    return world


# ── Record shape (3 tests) ──

def test_factory_creates_valid_record():
    world = _wb_world()
    set_diplomatic_state(world, "France", "Prussia", "ALLIANCE", "setup")
    set_diplomatic_state(world, "France", "Britain", "WAR", "setup")
    rec = create_war_bargain_commitment(
        world, "France", "Prussia", "Britain", "Hanover",
        "treaty_clause", "France|Prussia",
    )
    assert rec["id"] == 1
    assert rec["type"] == "war_bargain"
    assert rec["promiser"] == "France"
    assert rec["beneficiary"] == "Prussia"
    assert rec["target_enemy"] == "Britain"
    assert rec["status"] == "active"
    assert rec["source_pair"] == "France|Prussia"
    assert rec["cooldown_key"] == "France|Prussia::Britain"
    assert rec["claim_term"]["claim_region"] == "Hanover"
    assert rec["claim_term"]["claimant"] == "France"
    assert rec["zombie_clock_turns_elapsed"] == 0
    assert rec["dormant_notice_fired"] is False
    assert "1" in world.diplomatic_commitments


def test_factory_auto_increments_id():
    world = _wb_world()
    set_diplomatic_state(world, "France", "Prussia", "ALLIANCE", "setup")
    set_diplomatic_state(world, "France", "Britain", "WAR", "setup")
    set_diplomatic_state(world, "France", "Austria", "WAR", "setup")
    r1 = create_war_bargain_commitment(
        world, "France", "Prussia", "Britain", "Hanover",
        "treaty_clause", "France|Prussia",
    )
    r2 = create_war_bargain_commitment(
        world, "France", "Prussia", "Austria", "Bohemia",
        "treaty_clause", "France|Prussia",
    )
    assert r1["id"] == 1
    assert r2["id"] == 2
    assert world.next_commitment_id == 3


def test_source_pair_is_promiser_first():
    world = _wb_world()
    set_diplomatic_state(world, "France", "Prussia", "ALLIANCE", "setup")
    set_diplomatic_state(world, "France", "Britain", "WAR", "setup")
    rec = create_war_bargain_commitment(
        world, "France", "Prussia", "Britain", "Hanover",
        "treaty_clause", "France|Prussia",
    )
    assert rec["source_pair"] == "France|Prussia"
    assert rec["source_pair"].split("|")[0] == "France"


# ── Opposition pairs (3 tests) ──

def test_opposition_includes_war_enemies():
    world = _wb_world()
    set_diplomatic_state(world, "France", "Britain", "WAR", "setup")
    set_diplomatic_state(world, "France", "Austria", "WAR", "setup")
    pairs = get_bargain_opposition_pairs(world, "France", "Prussia")
    assert "Britain" in pairs
    assert "Austria" in pairs
    assert "Prussia" not in pairs
    assert "France" not in pairs


def test_opposition_includes_coalition_members():
    world = _wb_world()
    world.active_coalition = {
        "target_nation": "France",
        "members": ["Austria", "Russia", "Britain"],
    }
    pairs = get_bargain_opposition_pairs(world, "France", "Prussia")
    assert "Austria" in pairs
    assert "Russia" in pairs


def test_opposition_includes_conflict_pairs():
    world = _wb_world()
    world.diplomatic_commitments = {
        "1": {
            "id": 1, "type": "war_bargain", "status": "active",
            "promiser": "France", "beneficiary": "Austria",
            "target_enemy": "Russia",
            "claim_term": {"claim_region": "Warsaw"},
        },
    }
    pairs = get_bargain_opposition_pairs(world, "France", "Prussia")
    assert "Russia" in pairs


# ── Validation ──

def test_validation_happy_path():
    world = _wb_world()
    set_diplomatic_state(world, "France", "Prussia", "ALLIANCE", "setup")
    set_diplomatic_state(world, "France", "Britain", "WAR", "setup")
    ok, reason = validate_war_bargain(world, "France", "Prussia", "Britain", "Hanover")
    assert ok is True
    assert reason == ""


def test_validation_rejects_no_treaty():
    world = _wb_world()
    set_diplomatic_state(world, "France", "Prussia", "PEACE", "setup")
    ok, reason = validate_war_bargain(world, "France", "Prussia", "Britain", "Hanover")
    assert ok is False
    assert "DEFENSIVE_ALLIANCE or ALLIANCE" in reason


def test_validation_rejects_invalid_opposition():
    world = _wb_world()
    set_diplomatic_state(world, "France", "Prussia", "ALLIANCE", "setup")
    ok, reason = validate_war_bargain(world, "France", "Prussia", "Russia", "Moscow")
    assert ok is False
    assert "not a valid opposition" in reason


def test_validation_rejects_wrong_holder():
    world = _wb_world()
    set_diplomatic_state(world, "France", "Prussia", "ALLIANCE", "setup")
    set_diplomatic_state(world, "France", "Britain", "WAR", "setup")
    ok, reason = validate_war_bargain(world, "France", "Prussia", "Britain", "Paris")
    assert ok is False
    assert "not held by Britain" in reason


def test_validation_accepts_subject_held_region():
    world = _wb_world()
    set_diplomatic_state(world, "France", "Prussia", "ALLIANCE", "setup")
    set_diplomatic_state(world, "France", "Austria", "WAR", "setup")
    world.vassals = {"Saxony": {"vassal_nation": "Saxony", "lord_nation": "Austria"}}
    ok, reason = validate_war_bargain(world, "France", "Prussia", "Austria", "Saxony")
    assert ok is True


def test_validation_rejects_duplicate_beneficiary_enemy():
    world = _wb_world()
    set_diplomatic_state(world, "France", "Prussia", "ALLIANCE", "setup")
    set_diplomatic_state(world, "France", "Britain", "WAR", "setup")
    create_war_bargain_commitment(
        world, "France", "Prussia", "Britain", "Hanover",
        "treaty_clause", "France|Prussia",
    )
    ok, reason = validate_war_bargain(world, "France", "Prussia", "Britain", "Netherlands")
    assert ok is False
    assert "Already have a live bargain with Prussia against Britain" in reason


def test_validation_rejects_duplicate_claim_region():
    world = _wb_world()
    set_diplomatic_state(world, "France", "Prussia", "ALLIANCE", "setup")
    set_diplomatic_state(world, "France", "Austria", "ALLIANCE", "setup")
    set_diplomatic_state(world, "Austria", "Saxony", "ALLIANCE", "setup")
    set_diplomatic_state(world, "France", "Britain", "WAR", "setup")
    create_war_bargain_commitment(
        world, "France", "Prussia", "Britain", "Hanover",
        "treaty_clause", "France|Prussia",
    )
    ok, reason = validate_war_bargain(world, "France", "Austria", "Britain", "Hanover")
    assert ok is False
    assert "Already have a live bargain claiming Hanover" in reason


def test_validation_rejects_contradictory():
    world = _wb_world()
    set_diplomatic_state(world, "France", "Prussia", "ALLIANCE", "setup")
    set_diplomatic_state(world, "France", "Austria", "ALLIANCE", "setup")
    set_diplomatic_state(world, "France", "Britain", "WAR", "setup")
    # Make Prussia a valid opposition target via WAR
    set_diplomatic_state(world, "France", "Prussia", "WAR", "setup")
    create_war_bargain_commitment(
        world, "France", "Austria", "Prussia", "Rhineland",
        "treaty_clause", "France|Austria",
    )
    # Restore alliance for the second bargain attempt
    set_diplomatic_state(world, "France", "Prussia", "ALLIANCE", "setup")
    # Now try bargain with Prussia against Austria — contradictory
    # (Austria is opposition via the existing bargain's target_enemy being Austria for another beneficiary)
    set_diplomatic_state(world, "France", "Austria", "WAR", "setup")
    ok, reason = validate_war_bargain(world, "France", "Prussia", "Austria", "Bohemia")
    assert ok is False
    assert "Contradictory" in reason


def test_validation_rejects_ally_held_region():
    world = _wb_world()
    set_diplomatic_state(world, "France", "Prussia", "ALLIANCE", "setup")
    set_diplomatic_state(world, "France", "Austria", "WAR", "setup")
    # Dresden is controlled by Saxony; make Saxony an ally of France
    set_diplomatic_state(world, "France", "Saxony", "ALLIANCE", "setup")
    # Try bargaining over Dresden (controlled by Saxony, ally — not Austria)
    ok, reason = validate_war_bargain(world, "France", "Prussia", "Austria", "Dresden")
    assert ok is False
    assert "ally-held" in reason


def test_validation_rejects_cooldown():
    world = _wb_world()
    set_diplomatic_state(world, "France", "Prussia", "ALLIANCE", "setup")
    set_diplomatic_state(world, "France", "Britain", "WAR", "setup")
    world.diplomatic_commitments["99"] = {
        "id": 99, "type": "war_bargain", "status": "breached",
        "promiser": "France", "beneficiary": "Prussia",
        "target_enemy": "Britain",
        "cooldown_key": "France|Prussia::Britain",
        "cooldown_until_turn": 20,
        "claim_term": {"claim_region": "Waterloo"},
    }
    world.current_turn = 15
    ok, reason = validate_war_bargain(world, "France", "Prussia", "Britain", "Netherlands")
    assert ok is False
    assert "Cooldown" in reason


def test_validation_accepts_beneficiary_war_enemy():
    world = _wb_world()
    set_diplomatic_state(world, "France", "Austria", "ALLIANCE", "setup")
    set_diplomatic_state(world, "Austria", "Britain", "WAR", "setup")
    set_diplomatic_state(world, "Austria", "Saxony", "ALLIANCE", "setup")

    ok, reason = validate_war_bargain(world, "France", "Austria", "Britain", "Hanover")

    assert ok is True
    assert reason == ""


def test_validation_rejects_no_strategic_interest():
    world = _wb_world()
    set_diplomatic_state(world, "France", "Austria", "ALLIANCE", "setup")
    set_diplomatic_state(world, "France", "Prussia", "WAR", "setup")

    ok, reason = validate_war_bargain(world, "France", "Austria", "Prussia", "Berlin")

    assert ok is False
    assert "strategic interest" in reason


def test_validation_rejects_no_participation_access():
    world = _wb_world()
    set_diplomatic_state(world, "France", "Prussia", "ALLIANCE", "setup")
    set_diplomatic_state(world, "France", "Britain", "WAR", "setup")
    for region in world.regions.values():
        if region.controller == "Prussia":
            region.controller = "Saxony"
    world.invalidate_active_nations_cache()

    ok, reason = validate_war_bargain(world, "France", "Prussia", "Britain", "Hanover")

    assert ok is False
    assert "participation access" in reason


# ── Acceptance formula ──

def test_bargain_value_mod_defensive_alliance():
    world = _wb_world()
    set_diplomatic_state(world, "France", "Prussia", "DEFENSIVE_ALLIANCE", "setup")
    world.nation_relations[world._make_diplo_key("France", "Prussia")] = 50
    proposal = {
        "type": "defensive_alliance",
        "proposer_nation": "France",
        "target_nation": "Prussia",
        "sweeteners": [{"type": "war_bargain", "named_enemy": "Britain", "claim_region": "Hanover"}],
        "demands": [],
    }
    result = calculate_acceptance(proposal, world)
    assert result["components"]["bargain_value_mod"] == 10


def test_bargain_value_mod_alliance():
    world = _wb_world()
    set_diplomatic_state(world, "France", "Prussia", "ALLIANCE", "setup")
    world.nation_relations[world._make_diplo_key("France", "Prussia")] = 60
    proposal = {
        "type": "alliance",
        "proposer_nation": "France",
        "target_nation": "Prussia",
        "sweeteners": [{"type": "war_bargain", "named_enemy": "Britain", "claim_region": "Hanover"}],
        "demands": [],
    }
    result = calculate_acceptance(proposal, world)
    assert result["components"]["bargain_value_mod"] == 15


def test_bargain_conflict_penalty():
    world = _wb_world()
    set_diplomatic_state(world, "France", "Austria", "ALLIANCE", "setup")
    set_diplomatic_state(world, "France", "Prussia", "WAR", "setup")
    create_war_bargain_commitment(
        world, "France", "Austria", "Prussia", "Rhineland",
        "treaty_clause", "France|Austria",
    )
    set_diplomatic_state(world, "France", "Prussia", "PEACE", "setup")
    world.nation_relations[world._make_diplo_key("France", "Prussia")] = 30
    proposal = {
        "type": "peace",
        "proposer_nation": "France",
        "target_nation": "Prussia",
        "sweeteners": [],
        "demands": [],
    }
    result = calculate_acceptance(proposal, world)
    assert result["components"]["bargain_conflict_penalty"] == -8


def test_bargain_conflict_penalty_from_claim_region_holder():
    world = _wb_world()
    set_diplomatic_state(world, "France", "Austria", "ALLIANCE", "setup")
    set_diplomatic_state(world, "France", "Britain", "WAR", "setup")
    set_diplomatic_state(world, "Austria", "Saxony", "ALLIANCE", "setup")
    create_war_bargain_commitment(
        world, "France", "Austria", "Britain", "Hanover",
        "treaty_clause", "France|Austria",
    )
    world.regions["Hanover"].controller = "Prussia"
    proposal = {
        "type": "peace",
        "proposer_nation": "France",
        "target_nation": "Prussia",
        "sweeteners": [],
        "demands": [],
    }

    result = calculate_acceptance(proposal, world)

    assert result["components"]["bargain_conflict_penalty"] == -8


# ── Treaty ratification wiring ──

def test_ratify_treaty_creates_valid_war_bargain():
    world = _wb_world()
    set_diplomatic_state(world, "France", "Prussia", "PEACE", "setup")
    set_diplomatic_state(world, "France", "Britain", "WAR", "setup")
    world.nation_relations[world._make_diplo_key("France", "Prussia")] = 100
    proposal = {
        "type": "alliance",
        "proposer_nation": "France",
        "target_nation": "Prussia",
        "sweeteners": [{
            "type": "war_bargain",
            "named_enemy": "Britain",
            "claim_region": "Hanover",
        }],
        "demands": [],
        "clauses": [],
    }

    event = world._ratify_treaty(proposal)

    assert event["type"] == "diplomatic_treaty_signed"
    assert world.get_diplomatic_state("France", "Prussia") == "ALLIANCE"
    assert len(world.diplomatic_commitments) == 1
    rec = world.diplomatic_commitments["1"]
    assert rec["target_enemy"] == "Britain"
    assert rec["claim_term"]["claim_region"] == "Hanover"
    assert world.active_treaties[world._make_diplo_key("France", "Prussia")]["clauses"][0]["named_enemy"] == "Britain"


def test_ratify_treaty_rejects_invalid_war_bargain_without_state_change():
    world = _wb_world()
    set_diplomatic_state(world, "France", "Prussia", "PEACE", "setup")
    set_diplomatic_state(world, "France", "Britain", "WAR", "setup")
    world.nation_relations[world._make_diplo_key("France", "Prussia")] = 100
    proposal = {
        "type": "non_aggression",
        "proposer_nation": "France",
        "target_nation": "Prussia",
        "sweeteners": [{
            "type": "war_bargain",
            "named_enemy": "Britain",
            "claim_region": "Hanover",
        }],
        "demands": [],
        "clauses": [],
    }

    event = world._ratify_treaty(proposal)

    assert event["type"] == "diplomatic_treaty_failed"
    assert "Invalid war bargain" in event["message"]
    assert world.get_diplomatic_state("France", "Prussia") == "PEACE"
    assert world.diplomatic_commitments == {}


def test_ratify_treaty_rejects_multiple_war_bargains():
    world = _wb_world()
    set_diplomatic_state(world, "France", "Prussia", "PEACE", "setup")
    set_diplomatic_state(world, "France", "Britain", "WAR", "setup")
    set_diplomatic_state(world, "France", "Austria", "WAR", "setup")
    world.nation_relations[world._make_diplo_key("France", "Prussia")] = 100
    proposal = {
        "type": "alliance",
        "proposer_nation": "France",
        "target_nation": "Prussia",
        "sweeteners": [
            {"type": "war_bargain", "named_enemy": "Britain", "claim_region": "Hanover"},
            {"type": "war_bargain", "named_enemy": "Austria", "claim_region": "Bohemia"},
        ],
        "demands": [],
        "clauses": [],
    }

    event = world._ratify_treaty(proposal)

    assert event["type"] == "diplomatic_treaty_failed"
    assert "only one war bargain" in event["message"]
    assert world.diplomatic_commitments == {}


def test_ratify_treaty_rejects_claim_region_ceded_in_same_treaty():
    world = _wb_world()
    set_diplomatic_state(world, "France", "Prussia", "PEACE", "setup")
    set_diplomatic_state(world, "France", "Britain", "WAR", "setup")
    world.nation_relations[world._make_diplo_key("France", "Prussia")] = 100
    proposal = {
        "type": "alliance",
        "proposer_nation": "France",
        "target_nation": "Prussia",
        "sweeteners": [{
            "type": "war_bargain",
            "named_enemy": "Britain",
            "claim_region": "Hanover",
        }],
        "demands": [{"type": "territory_cede", "value": 1, "regions": ["Hanover"]}],
        "clauses": [],
    }

    event = world._ratify_treaty(proposal)

    assert event["type"] == "diplomatic_treaty_failed"
    assert "same treaty cedes it" in event["message"]
    assert world.diplomatic_commitments == {}


# ── Serialization ──

def test_roundtrip_with_commitments():
    world = _wb_world()
    set_diplomatic_state(world, "France", "Prussia", "ALLIANCE", "setup")
    set_diplomatic_state(world, "France", "Britain", "WAR", "setup")
    create_war_bargain_commitment(
        world, "France", "Prussia", "Britain", "Hanover",
        "treaty_clause", "France|Prussia",
    )
    data = world.to_dict()
    assert "diplomatic_commitments" in data
    assert "next_commitment_id" in data
    assert data["next_commitment_id"] == 2

    world2 = WorldState.from_dict(data)
    assert len(world2.diplomatic_commitments) == 1
    assert world2.next_commitment_id == 2
    rec = world2.diplomatic_commitments["1"]
    assert rec["promiser"] == "France"
    assert rec["claim_term"]["claim_region"] == "Hanover"


def test_roundtrip_with_archived_commitments():
    world = _wb_world()
    world.archived_diplomatic_commitments = [{
        "id": 1,
        "type": "war_bargain",
        "status": "fulfilled",
        "promiser": "France",
        "beneficiary": "Prussia",
        "target_enemy": "Britain",
        "archived_turn": 20,
    }]

    world2 = WorldState.from_dict(world.to_dict())

    assert world2.archived_diplomatic_commitments == world.archived_diplomatic_commitments
    assert world2.diplomatic_commitments == {}


def test_commitment_roundtrip_does_not_share_nested_dicts():
    world = _wb_world()
    set_diplomatic_state(world, "France", "Prussia", "ALLIANCE", "setup")
    set_diplomatic_state(world, "France", "Britain", "WAR", "setup")
    create_war_bargain_commitment(
        world, "France", "Prussia", "Britain", "Hanover",
        "treaty_clause", "France|Prussia",
    )

    data = world.to_dict()
    data["diplomatic_commitments"]["1"]["claim_term"]["claim_region"] = "Waterloo"
    assert world.diplomatic_commitments["1"]["claim_term"]["claim_region"] == "Hanover"

    world2 = WorldState.from_dict(data)
    data["diplomatic_commitments"]["1"]["claim_term"]["claim_region"] = "Netherlands"
    assert world2.diplomatic_commitments["1"]["claim_term"]["claim_region"] == "Waterloo"


def test_roundtrip_empty_defaults():
    world = WorldState()
    data = world.to_dict()
    world2 = WorldState.from_dict(data)
    assert world2.diplomatic_commitments == {}
    assert world2.next_commitment_id == 1


# ── Region observer (1 test) ──

def test_region_observer_witness_scope():
    world = _wb_world()
    set_diplomatic_state(world, "France", "Prussia", "ALLIANCE", "setup")
    set_diplomatic_state(world, "France", "Britain", "WAR", "setup")
    # Prussia has alliance with Britain (injured party) → ally scope takes precedence
    set_diplomatic_state(world, "Prussia", "Britain", "ALLIANCE", "setup")
    create_war_bargain_commitment(
        world, "France", "Prussia", "Britain", "Hanover",
        "treaty_clause", "France|Prussia",
    )
    scope = _classify_witness_scope(world, "Prussia", "France", "Britain")
    assert scope == "ally"

    # Russia has no alliance with Britain, no war with France, no shared enemy
    # but also no bargain → should get ""
    scope_no_bargain = _classify_witness_scope(world, "Russia", "France", "Britain")
    assert scope_no_bargain == ""


def test_region_observer_fires_when_bargain_matches():
    world = _wb_world()
    set_diplomatic_state(world, "France", "Austria", "ALLIANCE", "setup")
    set_diplomatic_state(world, "France", "Britain", "WAR", "setup")
    set_diplomatic_state(world, "Austria", "Saxony", "ALLIANCE", "setup")
    create_war_bargain_commitment(
        world, "France", "Austria", "Britain", "Hanover",
        "treaty_clause", "France|Austria",
    )
    set_diplomatic_state(world, "Austria", "Britain", "PEACE", "setup")
    scope = _classify_witness_scope(world, "Austria", "France", "Britain")
    assert scope == WITNESS_SCOPE_REGION_OBSERVER or scope == "ally"
