"""
Test suite for Marshal Overview / Marshal Management UI (Phase 6.5)

~50 tests covering data completeness, int wrapping, relationships,
unit types, biographies, status flags, abilities, skills, trust,
serialization, and the API endpoint.
"""

import pytest

from backend.models.world_state import WorldState
from backend.models.marshal import Marshal, StrategicOrder, Stance
from backend.game_logic.marshal_overview import (
    build_marshal_overview,
    _WIRED_ABILITY_MARSHALS,
    _RELATIONSHIP_LABELS,
)


# ════════════════════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════════════════════

def _make_world():
    """Create a standard WorldState for testing."""
    return WorldState(player_nation="France")


def _get_overview(world=None):
    """Build overview from world, defaulting to fresh game."""
    if world is None:
        world = _make_world()
    return build_marshal_overview(world)


def _find_marshal(overview, name):
    """Find a specific marshal in the overview list."""
    for m in overview:
        if m["name"] == name:
            return m
    return None


def _assert_no_floats(obj, path="root"):
    """Recursively assert no float values exist in the data structure."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            _assert_no_floats(v, f"{path}.{k}")
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            _assert_no_floats(v, f"{path}[{i}]")
    elif isinstance(obj, float):
        pytest.fail(f"Float found at {path}: {obj}")
    elif isinstance(obj, bool):
        pass  # bools are fine


# ════════════════════════════════════════════════════════════════════════════════
# STRUCTURAL TESTS
# ════════════════════════════════════════════════════════════════════════════════

class TestStructure:
    """Tests for overall structure and completeness."""

    def test_returns_list(self):
        """Overview returns a list."""
        overview = _get_overview()
        assert isinstance(overview, list)

    def test_player_marshals_only(self):
        """Only player nation marshals are included."""
        overview = _get_overview()
        names = {m["name"] for m in overview}
        # French marshals only
        assert names == {"Ney", "Davout", "Grouchy", "Drouot"}
        # No enemies
        for m in overview:
            assert m["nation"] == "France"

    def test_enemy_marshals_excluded(self):
        """Enemy marshals are not in the overview."""
        overview = _get_overview()
        names = {m["name"] for m in overview}
        assert "Wellington" not in names
        assert "Blucher" not in names
        assert "Uxbridge" not in names
        assert "Gneisenau" not in names
        assert "ArchdukeCharles" not in names

    def test_all_required_keys_present(self):
        """Every marshal dict has all required keys."""
        required_keys = {
            # Identity
            "name", "nation", "personality", "personality_description",
            "unit_type", "unit_type_description", "movement_range", "biography",
            # Ability
            "ability_name", "ability_description", "ability_trigger",
            "ability_effect", "ability_active",
            # Combat stats
            "strength", "starting_strength", "morale", "skills", "tactical_skill",
            # Trust & standing
            "trust_value", "trust_label", "vindication_score",
            "has_pending_vindication", "orders_overridden",
            "battles_won", "battles_lost",
            # Current status
            "location", "stance", "strategic_order",
            "is_fortified", "defense_bonus", "is_drilling", "drilling_locked",
            "shock_bonus", "is_retreating", "retreat_recovery",
            "is_broken", "broken_recovery",
            "idle_turns", "is_autonomous", "autonomy_reason",
            # Unit specifics
            "cavalry", "counter_punch_available", "counter_punch_turns",
            "holding_position", "artillery", "bombardments_this_turn",
            "moved_this_turn",
            # Relationships
            "relationships",
        }
        overview = _get_overview()
        for m in overview:
            missing = required_keys - set(m.keys())
            assert not missing, f"{m['name']} missing keys: {missing}"

    def test_empty_overview_when_no_player_marshals(self):
        """If no player marshals exist, returns empty list."""
        world = _make_world()
        # Remove all French marshals
        to_remove = [n for n, m in world.marshals.items() if m.nation == "France"]
        for n in to_remove:
            del world.marshals[n]
        overview = build_marshal_overview(world)
        assert overview == []


# ════════════════════════════════════════════════════════════════════════════════
# NO-FLOAT ENFORCEMENT
# ════════════════════════════════════════════════════════════════════════════════

class TestNoFloats:
    """All numeric values must be int, not float (Godot crashes on floats)."""

    def test_no_floats_in_overview(self):
        """Scan entire overview structure for floats."""
        overview = _get_overview()
        _assert_no_floats(overview)

    def test_no_floats_after_state_changes(self):
        """No floats even after fortify/drill/combat changes."""
        world = _make_world()
        ney = world.marshals["Ney"]
        ney.fortified = True
        ney.defense_bonus = 0.16  # float internally
        ney.morale = 73
        ney.vindication_score = 3
        overview = build_marshal_overview(world)
        _assert_no_floats(overview)

    def test_defense_bonus_is_int_percentage(self):
        """Defense bonus is converted from float (0.16) to int percentage (16)."""
        world = _make_world()
        davout = world.marshals["Davout"]
        davout.fortified = True
        davout.defense_bonus = 0.12
        overview = build_marshal_overview(world)
        d = _find_marshal(overview, "Davout")
        assert d["defense_bonus"] == 12
        assert isinstance(d["defense_bonus"], int)


# ════════════════════════════════════════════════════════════════════════════════
# UNIT TYPE DETECTION
# ════════════════════════════════════════════════════════════════════════════════

class TestUnitType:
    """Unit type derived from cavalry/artillery flags."""

    def test_ney_is_cavalry(self):
        overview = _get_overview()
        ney = _find_marshal(overview, "Ney")
        assert ney["unit_type"] == "Cavalry"
        assert ney["cavalry"] is True
        assert ney["artillery"] is False

    def test_davout_is_infantry(self):
        overview = _get_overview()
        davout = _find_marshal(overview, "Davout")
        assert davout["unit_type"] == "Infantry"
        assert davout["cavalry"] is False
        assert davout["artillery"] is False

    def test_drouot_is_artillery(self):
        overview = _get_overview()
        drouot = _find_marshal(overview, "Drouot")
        assert drouot["unit_type"] == "Artillery"
        assert drouot["artillery"] is True
        assert drouot["cavalry"] is False

    def test_grouchy_is_infantry(self):
        overview = _get_overview()
        grouchy = _find_marshal(overview, "Grouchy")
        assert grouchy["unit_type"] == "Infantry"


# ════════════════════════════════════════════════════════════════════════════════
# BIOGRAPHY
# ════════════════════════════════════════════════════════════════════════════════

class TestBiography:
    """Biography blurbs exist and serialize correctly."""

    def test_all_player_marshals_have_biography(self):
        """Every player marshal has a non-empty biography."""
        overview = _get_overview()
        for m in overview:
            assert m["biography"] != "", f"{m['name']} has empty biography"
            assert len(m["biography"]) > 20, f"{m['name']} biography too short"

    def test_all_marshals_have_biography_in_world(self):
        """All 9 marshals (player + enemy) have biographies set."""
        world = _make_world()
        for name, marshal in world.marshals.items():
            assert marshal.biography != "", f"{name} has empty biography"

    def test_biography_under_200_chars(self):
        """All biographies are under 200 characters (card blurbs)."""
        world = _make_world()
        for name, marshal in world.marshals.items():
            assert len(marshal.biography) <= 200, (
                f"{name} biography too long: {len(marshal.biography)} chars"
            )

    def test_biography_serialization_roundtrip(self):
        """Biography survives to_dict/from_dict for all 9 marshals."""
        world = _make_world()
        for name, marshal in world.marshals.items():
            original_bio = marshal.biography
            data = marshal.to_dict()
            assert "biography" in data
            assert data["biography"] == original_bio
            restored = Marshal.from_dict(data)
            assert restored.biography == original_bio, (
                f"{name} biography lost in roundtrip"
            )


# ════════════════════════════════════════════════════════════════════════════════
# PERSONALITY DESCRIPTION
# ════════════════════════════════════════════════════════════════════════════════

class TestPersonalityDescription:
    """Personality type descriptions explain gameplay effects."""

    def test_all_marshals_have_personality_description(self):
        """Every player marshal has a non-empty personality description."""
        overview = _get_overview()
        for m in overview:
            assert m["personality_description"] != "", (
                f"{m['name']} has empty personality_description"
            )

    def test_aggressive_description_mentions_attack(self):
        """Aggressive personality description mentions attack bonus."""
        overview = _get_overview()
        ney = _find_marshal(overview, "Ney")
        assert "attack" in ney["personality_description"].lower()

    def test_cautious_description_mentions_defense(self):
        """Cautious personality description mentions defense bonus."""
        overview = _get_overview()
        davout = _find_marshal(overview, "Davout")
        assert "defense" in davout["personality_description"].lower()

    def test_literal_description_mentions_orders(self):
        """Literal personality description mentions order compliance."""
        overview = _get_overview()
        grouchy = _find_marshal(overview, "Grouchy")
        assert "order" in grouchy["personality_description"].lower()

    def test_three_personality_types_covered(self):
        """All three personality types have descriptions."""
        from backend.game_logic.marshal_overview import _PERSONALITY_DESCRIPTIONS
        assert "aggressive" in _PERSONALITY_DESCRIPTIONS
        assert "cautious" in _PERSONALITY_DESCRIPTIONS
        assert "literal" in _PERSONALITY_DESCRIPTIONS


# ════════════════════════════════════════════════════════════════════════════════
# UNIT TYPE DESCRIPTION
# ════════════════════════════════════════════════════════════════════════════════

class TestUnitTypeDescription:
    """Unit type descriptions explain gameplay effects."""

    def test_all_marshals_have_unit_type_description(self):
        """Every player marshal has a non-empty unit_type_description."""
        overview = _get_overview()
        for m in overview:
            assert m["unit_type_description"] != "", (
                f"{m['name']} has empty unit_type_description"
            )

    def test_cavalry_description_mentions_movement(self):
        """Cavalry description mentions movement range advantage."""
        overview = _get_overview()
        ney = _find_marshal(overview, "Ney")
        assert "movement" in ney["unit_type_description"].lower() or "range" in ney["unit_type_description"].lower()

    def test_artillery_description_mentions_bombard(self):
        """Artillery description mentions bombardment mechanic."""
        overview = _get_overview()
        drouot = _find_marshal(overview, "Drouot")
        assert "bombard" in drouot["unit_type_description"].lower()

    def test_artillery_description_mentions_cannot_attack_after_move(self):
        """Artillery description mentions movement restriction."""
        overview = _get_overview()
        drouot = _find_marshal(overview, "Drouot")
        desc = drouot["unit_type_description"].lower()
        assert "cannot attack after moving" in desc or "attack after moving" in desc

    def test_three_unit_types_covered(self):
        """All three unit types have descriptions."""
        from backend.game_logic.marshal_overview import _UNIT_TYPE_DESCRIPTIONS
        assert "Infantry" in _UNIT_TYPE_DESCRIPTIONS
        assert "Cavalry" in _UNIT_TYPE_DESCRIPTIONS
        assert "Artillery" in _UNIT_TYPE_DESCRIPTIONS


# ════════════════════════════════════════════════════════════════════════════════
# ABILITY DATA
# ════════════════════════════════════════════════════════════════════════════════

class TestAbility:
    """Ability fields present and ability_active correctly derived."""

    def test_ability_fields_present(self):
        """All 4 ability fields present per marshal."""
        overview = _get_overview()
        for m in overview:
            assert "ability_name" in m
            assert "ability_description" in m
            assert "ability_trigger" in m
            assert "ability_effect" in m
            assert "ability_active" in m

    def test_ney_ability_active(self):
        """Ney's Bravest of the Brave is wired (active)."""
        overview = _get_overview()
        ney = _find_marshal(overview, "Ney")
        assert ney["ability_active"] is True
        assert ney["ability_name"] == "Bravest of the Brave"

    def test_davout_ability_active(self):
        """Davout's Counter-Punch Mastery is wired (active)."""
        overview = _get_overview()
        davout = _find_marshal(overview, "Davout")
        assert davout["ability_active"] is True
        assert davout["ability_name"] == "Counter-Punch Mastery"
        assert "+20%" in davout["ability_effect"]

    def test_grouchy_ability_inactive(self):
        """Grouchy's Literal Obedience is deferred — ability fields empty."""
        overview = _get_overview()
        grouchy = _find_marshal(overview, "Grouchy")
        assert grouchy["ability_active"] is False
        assert grouchy["ability_name"] == ""

    def test_drouot_ability_active(self):
        """Drouot's Sage of the Grand Army is wired (active)."""
        overview = _get_overview()
        drouot = _find_marshal(overview, "Drouot")
        assert drouot["ability_active"] is True
        assert drouot["ability_name"] == "Sage of the Grand Army"

    def test_wired_ability_set_correct(self):
        """Verify the wired ability set matches current documentation."""
        assert _WIRED_ABILITY_MARSHALS == {"Ney", "Davout", "Drouot", "Wellington", "Blucher", "Uxbridge"}


# ════════════════════════════════════════════════════════════════════════════════
# SKILLS
# ════════════════════════════════════════════════════════════════════════════════

class TestSkills:
    """Skills range and completeness."""

    def test_all_six_skills_present(self):
        """All 6 skills present per marshal."""
        expected_skills = {"tactical", "shock", "defense", "logistics", "administration", "command"}
        overview = _get_overview()
        for m in overview:
            assert set(m["skills"].keys()) == expected_skills, (
                f"{m['name']} missing skills"
            )

    def test_skills_in_range(self):
        """All skills 1-10."""
        overview = _get_overview()
        for m in overview:
            for skill, val in m["skills"].items():
                assert 1 <= val <= 10, (
                    f"{m['name']} {skill}={val} out of range"
                )

    def test_tactical_skill_in_range(self):
        """Legacy tactical_skill 0-12."""
        overview = _get_overview()
        for m in overview:
            assert 0 <= m["tactical_skill"] <= 12, (
                f"{m['name']} tactical_skill={m['tactical_skill']} out of range"
            )


# ════════════════════════════════════════════════════════════════════════════════
# TRUST & STANDING
# ════════════════════════════════════════════════════════════════════════════════

class TestTrustStanding:
    """Trust values and labels match."""

    def test_trust_values_in_range(self):
        """Trust values 0-100."""
        overview = _get_overview()
        for m in overview:
            assert 0 <= m["trust_value"] <= 100, (
                f"{m['name']} trust={m['trust_value']} out of range"
            )

    def test_trust_label_non_empty(self):
        """Trust label is a non-empty string."""
        overview = _get_overview()
        for m in overview:
            assert isinstance(m["trust_label"], str)
            assert len(m["trust_label"]) > 0

    def test_vindication_in_range(self):
        """Vindication -5 to +5."""
        overview = _get_overview()
        for m in overview:
            assert -5 <= m["vindication_score"] <= 5


# ════════════════════════════════════════════════════════════════════════════════
# STATUS FLAGS
# ════════════════════════════════════════════════════════════════════════════════

class TestStatusFlags:
    """Status flags reflect marshal state correctly."""

    def test_fortified_flag(self):
        """Fortified marshal shows correct flag."""
        world = _make_world()
        davout = world.marshals["Davout"]
        davout.fortified = True
        davout.defense_bonus = 0.10
        overview = build_marshal_overview(world)
        d = _find_marshal(overview, "Davout")
        assert d["is_fortified"] is True
        assert d["defense_bonus"] == 10

    def test_not_fortified_by_default(self):
        """Fresh marshal is not fortified."""
        overview = _get_overview()
        ney = _find_marshal(overview, "Ney")
        assert ney["is_fortified"] is False
        assert ney["defense_bonus"] == 0

    def test_drilling_flag(self):
        """Drilling marshal shows correct flag."""
        world = _make_world()
        grouchy = world.marshals["Grouchy"]
        grouchy.drilling = True
        overview = build_marshal_overview(world)
        g = _find_marshal(overview, "Grouchy")
        assert g["is_drilling"] is True

    def test_drilling_locked_flag(self):
        """Locked drill shows both flags."""
        world = _make_world()
        grouchy = world.marshals["Grouchy"]
        grouchy.drilling_locked = True
        grouchy.shock_bonus = 2
        overview = build_marshal_overview(world)
        g = _find_marshal(overview, "Grouchy")
        assert g["is_drilling"] is True
        assert g["drilling_locked"] is True
        assert g["shock_bonus"] == 2

    def test_retreating_flag(self):
        """Retreating marshal shows correct state."""
        world = _make_world()
        ney = world.marshals["Ney"]
        ney.retreating = True
        ney.retreat_recovery = 2
        overview = build_marshal_overview(world)
        n = _find_marshal(overview, "Ney")
        assert n["is_retreating"] is True
        assert n["retreat_recovery"] == 2

    def test_broken_flag(self):
        """Broken marshal shows correct state."""
        world = _make_world()
        grouchy = world.marshals["Grouchy"]
        grouchy.broken = True
        grouchy.broken_recovery = 3
        overview = build_marshal_overview(world)
        g = _find_marshal(overview, "Grouchy")
        assert g["is_broken"] is True
        assert g["broken_recovery"] == 3

    def test_autonomous_flag(self):
        """Autonomous marshal shows correct state."""
        world = _make_world()
        ney = world.marshals["Ney"]
        ney.autonomous = True
        ney.autonomy_reason = "redemption"
        overview = build_marshal_overview(world)
        n = _find_marshal(overview, "Ney")
        assert n["is_autonomous"] is True
        assert n["autonomy_reason"] == "redemption"

    def test_idle_turns(self):
        """Idle turns tracked."""
        world = _make_world()
        davout = world.marshals["Davout"]
        davout.idle_turns = 5
        overview = build_marshal_overview(world)
        d = _find_marshal(overview, "Davout")
        assert d["idle_turns"] == 5


# ════════════════════════════════════════════════════════════════════════════════
# STRATEGIC ORDERS
# ════════════════════════════════════════════════════════════════════════════════

class TestStrategicOrders:
    """Strategic order display."""

    def test_no_order_by_default(self):
        """Fresh marshal has no strategic order."""
        overview = _get_overview()
        ney = _find_marshal(overview, "Ney")
        assert ney["strategic_order"] is None

    def test_hold_order(self):
        """HOLD order shows correctly."""
        world = _make_world()
        davout = world.marshals["Davout"]
        davout.strategic_order = StrategicOrder(
            command_type="HOLD",
            target="Paris",
            target_type="region",
            started_turn=1,
            original_command="hold Paris"
        )
        overview = build_marshal_overview(world)
        d = _find_marshal(overview, "Davout")
        assert d["strategic_order"] is not None
        assert d["strategic_order"]["command_type"] == "HOLD"
        assert d["strategic_order"]["target"] == "Paris"

    def test_pursue_order(self):
        """PURSUE order shows target marshal."""
        world = _make_world()
        ney = world.marshals["Ney"]
        ney.strategic_order = StrategicOrder(
            command_type="PURSUE",
            target="Wellington",
            target_type="marshal",
            started_turn=1,
            original_command="pursue Wellington"
        )
        overview = build_marshal_overview(world)
        n = _find_marshal(overview, "Ney")
        assert n["strategic_order"]["command_type"] == "PURSUE"
        assert n["strategic_order"]["target"] == "Wellington"


# ════════════════════════════════════════════════════════════════════════════════
# RELATIONSHIPS
# ════════════════════════════════════════════════════════════════════════════════

class TestRelationships:
    """Relationship data and filtering."""

    def test_relationships_present(self):
        """Each marshal has a relationships list."""
        overview = _get_overview()
        for m in overview:
            assert isinstance(m["relationships"], list)

    def test_relationship_has_required_fields(self):
        """Each relationship entry has name, value, label."""
        overview = _get_overview()
        for m in overview:
            for r in m["relationships"]:
                assert "name" in r
                assert "value" in r
                assert "label" in r

    def test_ney_davout_hostile(self):
        """Ney's relationship with Davout is Hostile (-2)."""
        overview = _get_overview()
        ney = _find_marshal(overview, "Ney")
        davout_rel = None
        for r in ney["relationships"]:
            if r["name"] == "Davout":
                davout_rel = r
                break
        assert davout_rel is not None
        assert davout_rel["value"] == -2
        assert davout_rel["label"] == "Hostile"

    def test_relationship_labels_correct(self):
        """All relationship values map to correct labels."""
        for val, label in _RELATIONSHIP_LABELS.items():
            assert label in {"Hostile", "Rival", "Professional", "Friendly", "Devoted"}

    def test_dead_marshal_excluded_from_relationships(self):
        """Relationships exclude dead marshals (strength=0)."""
        world = _make_world()
        # Kill Davout
        world.marshals["Davout"].strength = 0
        overview = build_marshal_overview(world)
        ney = _find_marshal(overview, "Ney")
        rel_names = {r["name"] for r in ney["relationships"]}
        assert "Davout" not in rel_names

    def test_relationships_only_include_existing_marshals(self):
        """Relationships only reference marshals that exist in world.marshals."""
        world = _make_world()
        # Add a relationship to a nonexistent marshal
        world.marshals["Ney"].relationships["Napoleon"] = 2
        overview = build_marshal_overview(world)
        ney = _find_marshal(overview, "Ney")
        rel_names = {r["name"] for r in ney["relationships"]}
        assert "Napoleon" not in rel_names


# ════════════════════════════════════════════════════════════════════════════════
# STANCE
# ════════════════════════════════════════════════════════════════════════════════

class TestStance:
    """Stance display."""

    def test_default_stance_neutral(self):
        """Default stance is neutral — display name capitalized."""
        overview = _get_overview()
        for m in overview:
            assert m["stance"] == "Neutral"

    def test_aggressive_stance(self):
        """Aggressive stance reflected — display name capitalized."""
        world = _make_world()
        world.marshals["Ney"].stance = Stance.AGGRESSIVE
        overview = build_marshal_overview(world)
        ney = _find_marshal(overview, "Ney")
        assert ney["stance"] == "Aggressive"

    def test_defensive_stance(self):
        """Defensive stance reflected — display name capitalized."""
        world = _make_world()
        world.marshals["Davout"].stance = Stance.DEFENSIVE
        overview = build_marshal_overview(world)
        d = _find_marshal(overview, "Davout")
        assert d["stance"] == "Defensive"


# ════════════════════════════════════════════════════════════════════════════════
# CAVALRY / ARTILLERY SPECIFICS
# ════════════════════════════════════════════════════════════════════════════════

class TestUnitSpecifics:
    """Cavalry and artillery specific fields."""

    def test_counter_punch_available(self):
        """Davout counter-punch state shows correctly."""
        world = _make_world()
        world.marshals["Davout"].counter_punch_available = True
        world.marshals["Davout"].counter_punch_turns = 2
        overview = build_marshal_overview(world)
        d = _find_marshal(overview, "Davout")
        assert d["counter_punch_available"] is True
        assert d["counter_punch_turns"] == 2

    def test_artillery_bombardment_tracking(self):
        """Artillery bombardment count tracked."""
        world = _make_world()
        world.marshals["Drouot"].bombardments_this_turn = 1
        overview = build_marshal_overview(world)
        d = _find_marshal(overview, "Drouot")
        assert d["bombardments_this_turn"] == 1

    def test_artillery_moved_this_turn(self):
        """Artillery moved_this_turn flag tracked."""
        world = _make_world()
        world.marshals["Drouot"].moved_this_turn = True
        overview = build_marshal_overview(world)
        d = _find_marshal(overview, "Drouot")
        assert d["moved_this_turn"] is True

    def test_holding_position(self):
        """Grouchy holding position state."""
        world = _make_world()
        world.marshals["Grouchy"].holding_position = True
        overview = build_marshal_overview(world)
        g = _find_marshal(overview, "Grouchy")
        assert g["holding_position"] is True


# ════════════════════════════════════════════════════════════════════════════════
# API ENDPOINT
# ════════════════════════════════════════════════════════════════════════════════

class TestEndpoint:
    """Test the /marshal_overview endpoint via TestClient."""

    @pytest.fixture
    def client(self):
        """Create a test client with an active game."""
        from backend.main import app, game_state
        from fastapi.testclient import TestClient

        # Initialize game state
        world = WorldState(player_nation="France")
        game_state["world"] = world

        # Patch module-level 'world' reference
        import backend.main as main_module
        main_module.world = world

        return TestClient(app)

    def test_endpoint_returns_200(self, client):
        """GET /marshal_overview returns 200."""
        response = client.get("/marshal_overview")
        assert response.status_code == 200

    def test_endpoint_success_true(self, client):
        """Response has success=True."""
        response = client.get("/marshal_overview")
        data = response.json()
        assert data["success"] is True

    def test_endpoint_has_marshals_key(self, client):
        """Response has 'marshals' key with list."""
        response = client.get("/marshal_overview")
        data = response.json()
        assert "marshals" in data
        assert isinstance(data["marshals"], list)

    def test_endpoint_only_player_marshals(self, client):
        """Endpoint returns only player nation marshals."""
        response = client.get("/marshal_overview")
        data = response.json()
        names = {m["name"] for m in data["marshals"]}
        assert names == {"Ney", "Davout", "Grouchy", "Drouot"}

    def test_endpoint_no_floats(self, client):
        """No floats in API response."""
        response = client.get("/marshal_overview")
        data = response.json()
        _assert_no_floats(data["marshals"])

    def test_endpoint_no_game_returns_error(self):
        """Endpoint with no active game returns error."""
        from backend.main import app, game_state
        from fastapi.testclient import TestClient

        saved_world = game_state.get("world")
        game_state["world"] = None
        try:
            client = TestClient(app)
            response = client.get("/marshal_overview")
            data = response.json()
            assert data["success"] is False
        finally:
            game_state["world"] = saved_world
