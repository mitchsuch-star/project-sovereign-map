"""Phase 2A Batch 5 tests: Vassal Cleanup + Dialogue + Sweetener.

R50: Continental System membership cleared on vassal release
R48: Auto-armistice/peace after vassalization for conflicting states
R57: threat wired in diplomatic_dialogue context
R53: Sweetener value floor in _try_add_desired_clauses
"""
from backend.models.world_state import WorldState
from backend.game_logic.vassal import (
    create_vassal_treaty,
    create_vassal_conquest,
    release_vassal,
)


def make_world():
    return WorldState()


# ═══════════════════════════════════════════════════════
# R50: Continental System cleared on release
# ═══════════════════════════════════════════════════════

class TestContinentalSystemClearOnRelease:
    """R50: continental_system_members.discard on release_vassal."""

    def test_cs_cleared_on_release(self):
        world = make_world()
        # Set up Saxony as vassal + CS member
        key = world._make_diplo_key("France", "Saxony")
        world.diplomatic_states[key] = "OPEN_BORDERS"
        create_vassal_treaty(world, "France", "Saxony")
        world.continental_system_members = ["Saxony", "Prussia"]
        release_vassal(world, "Saxony")
        assert "Saxony" not in world.continental_system_members
        assert "Prussia" in world.continental_system_members

    def test_cs_unaffected_when_not_member(self):
        world = make_world()
        key = world._make_diplo_key("France", "Saxony")
        world.diplomatic_states[key] = "OPEN_BORDERS"
        create_vassal_treaty(world, "France", "Saxony")
        world.continental_system_members = ["Prussia"]
        release_vassal(world, "Saxony")
        assert world.continental_system_members == ["Prussia"]


# ═══════════════════════════════════════════════════════
# R48: Reconcile diplomatic conflicts after vassalization
# ═══════════════════════════════════════════════════════

class TestReconcileVassalDiplomacy:
    """R48: Vassal's conflicting alliances/wars resolved on vassalization."""

    def test_vassal_war_with_lord_ally_becomes_armistice(self):
        world = make_world()
        # France allied with Austria, Saxony at war with Austria
        fa_key = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[fa_key] = "ALLIANCE"
        sa_key = world._make_diplo_key("Saxony", "Austria")
        world.diplomatic_states[sa_key] = "WAR"
        # Vassalize Saxony
        fs_key = world._make_diplo_key("France", "Saxony")
        world.diplomatic_states[fs_key] = "OPEN_BORDERS"
        create_vassal_treaty(world, "France", "Saxony")
        # Saxony-Austria should now be ARMISTICE
        assert world.diplomatic_states[sa_key] == "ARMISTICE"

    def test_vassal_ally_of_lord_enemy_becomes_peace(self):
        world = make_world()
        # France at war with Prussia, Saxony allied with Prussia
        fp_key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[fp_key] = "WAR"
        sp_key = world._make_diplo_key("Prussia", "Saxony")
        world.diplomatic_states[sp_key] = "ALLIANCE"
        # Vassalize Saxony
        fs_key = world._make_diplo_key("France", "Saxony")
        world.diplomatic_states[fs_key] = "OPEN_BORDERS"
        create_vassal_treaty(world, "France", "Saxony")
        # Saxony-Prussia alliance should be broken to PEACE
        assert world.diplomatic_states[sp_key] == "PEACE"

    def test_conquest_also_reconciles(self):
        world = make_world()
        # France at war with Britain, Saxony allied with Britain
        fb_key = world._make_diplo_key("Britain", "France")
        world.diplomatic_states[fb_key] = "WAR"
        bs_key = world._make_diplo_key("Britain", "Saxony")
        world.diplomatic_states[bs_key] = "DEFENSIVE_ALLIANCE"
        create_vassal_conquest(world, "France", "Saxony")
        # Saxony-Britain should be broken to PEACE
        assert world.diplomatic_states[bs_key] == "PEACE"

    def test_unrelated_diplomacy_unchanged(self):
        world = make_world()
        # Austria-Prussia has their own state
        ap_key = world._make_diplo_key("Austria", "Prussia")
        original = world.diplomatic_states.get(ap_key, "PEACE")
        # Vassalize Saxony
        fs_key = world._make_diplo_key("France", "Saxony")
        world.diplomatic_states[fs_key] = "OPEN_BORDERS"
        create_vassal_treaty(world, "France", "Saxony")
        assert world.diplomatic_states.get(ap_key, "PEACE") == original


# ═══════════════════════════════════════════════════════
# R57: Threat wired in diplomatic dialogue
# ═══════════════════════════════════════════════════════

class TestThreatInDialogue:
    """R57: threat value in diplomatic_dialogue context uses world.threat_level."""

    def test_threat_reflects_world_state(self):
        from backend.game_logic.diplomatic_dialogue import generate_dialogue
        world = make_world()
        world.threat_level = 45
        key = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[key] = "PEACE"
        dialogue = generate_dialogue("propose", {"target_nation": "Austria", "proposal_type": "open_borders"}, world)
        assert dialogue["context"]["threat"] == 45

    def test_threat_zero_when_no_threat(self):
        from backend.game_logic.diplomatic_dialogue import generate_dialogue
        world = make_world()
        world.threat_level = 0
        key = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[key] = "PEACE"
        dialogue = generate_dialogue("propose", {"target_nation": "Austria", "proposal_type": "open_borders"}, world)
        assert dialogue["context"]["threat"] == 0


# ═══════════════════════════════════════════════════════
# R53: Sweetener value floor
# ═══════════════════════════════════════════════════════

class TestSweetenerFloor:
    """R53: Sweetener value floored at 5 in _try_add_desired_clauses."""

    def test_sweetener_minimum_value(self):
        """AI sweetener offers should have value >= 5."""
        from backend.game_logic.ai_diplomacy import _try_add_desired_clauses
        world = make_world()
        key = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[key] = "WAR"
        world.nation_relations[key] = 30  # Friendly enough for acceptance
        # Build terms that will use Austria's desires
        terms = {
            "type": "peace",
            "proposer_nation": "Austria",
            "target_nation": "France",
            "sweeteners": [],
            "demands": [],
            "clauses": [],
        }
        result = _try_add_desired_clauses(terms, "Austria", world)
        if result:
            for s in result.get("sweeteners", []):
                if s["type"] in ("gold_lump", "gold_per_turn", "territory"):
                    assert s["value"] >= 5, f"Sweetener {s['type']} has value {s['value']} < 5"
