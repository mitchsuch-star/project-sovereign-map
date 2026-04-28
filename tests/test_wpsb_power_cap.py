"""WPS-B: Vassalage Power Cap tests.

Spec: `docs/WAR_PURPOSE_SCORE_SEMANTICS_SPEC.md` §8.
Plan: `docs/PEACE_DEALS_UMBRELLA_SPEC.md` §5.

Covers (35 tests):
  1.  calculate_national_power — region income sum
  2.  calculate_national_power — vassal contribution (50%)
  3.  calculate_national_power — British naval income included
  4.  calculate_national_power — controller_override projection
  5.  Starting power values match spec §8.5
  6.  check_vassalage_power_cap — allowed (Saxony)
  7.  check_vassalage_power_cap — blocked (Austria)
  8.  check_vassalage_power_cap — pct / reason fields
  9.  project_power_after_terms — territory cession shifts power
  10. project_power_after_terms — invalid region skipped
  11. project_power_after_terms — from_nation mismatch skipped
  12. check_vassalage_power_cap with terms — post-cession allows
  13. Treaty vassalage gate — blocked by power cap
  14. Treaty vassalage gate — allowed for minor
  15. Conquest vassalage gate — blocked by power cap
  16. Conquest vassalage gate — allowed for minor
  17. Wizard propose_vassal — disabled when target too powerful
  18. Wizard propose_vassal — enabled for minor
  19. War Purpose popup — subjugation greyed out with power_pct
  20. AI vassalage pre-check note (deferred, no-op test)
"""
from __future__ import annotations

from backend.game_logic.diplomacy import (
    BRITISH_NAVAL_INCOME_POWER,
    calculate_national_power,
    project_power_after_terms,
    check_vassalage_power_cap,
    get_available_war_objectives,
    get_available_diplomatic_actions,
    set_diplomatic_state,
)
from backend.game_logic.vassal import (
    create_vassal_treaty,
    create_vassal_conquest,
)
from backend.commands.diplomatic_executor import DiplomaticExecutor
from backend.models.world_state import WorldState


# ════════════════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════════════════

def _fresh_world() -> WorldState:
    return WorldState(player_nation="France")


def _power(nation, world):
    return calculate_national_power(nation, world)


# ════════════════════════════════════════════════════════════════════════════
# 1-4. CALCULATE_NATIONAL_POWER
# ════════════════════════════════════════════════════════════════════════════

class TestCalculateNationalPower:

    def test_region_income_sum(self):
        world = _fresh_world()
        power = _power("France", world)
        expected = sum(
            r.income_value for r in world.regions.values()
            if r.controller == "France"
        )
        assert power == expected
        assert power > 0

    def test_vassal_contribution_half(self):
        world = _fresh_world()
        set_diplomatic_state(world, "France", "Saxony", "WAR", "test")
        base = _power("France", world)
        create_vassal_conquest(world, "France", "Saxony")
        with_vassal = _power("France", world)
        saxony_income = sum(
            r.income_value for r in world.regions.values()
            if r.controller == "Saxony"
        )
        assert with_vassal == base + saxony_income // 2

    def test_british_naval_income_included(self):
        world = _fresh_world()
        region_only = sum(
            r.income_value for r in world.regions.values()
            if r.controller == "Britain"
        )
        total = _power("Britain", world)
        assert total > region_only
        assert total == region_only + min(
            BRITISH_NAVAL_INCOME_POWER,
            150 + 50 * sum(
                1 for r in world.regions.values()
                if r.controller == "Britain" and r.is_coastal
            ),
        )

    def test_british_naval_power_reads_coastal_metadata(self):
        world = _fresh_world()
        base = _power("Britain", world)
        world.regions["Hanover"].is_coastal = True
        world.invalidate_active_nations_cache()
        assert _power("Britain", world) == base + 50

    def test_controller_override_projection(self):
        world = _fresh_world()
        base_france = _power("France", world)
        base_prussia = _power("Prussia", world)
        override = {"Berlin": "France"}
        france_proj = calculate_national_power("France", world,
                                               controller_override=override)
        prussia_proj = calculate_national_power("Prussia", world,
                                                controller_override=override)
        berlin_income = world.regions["Berlin"].income_value
        assert france_proj == base_france + berlin_income
        assert prussia_proj == base_prussia - berlin_income


# ════════════════════════════════════════════════════════════════════════════
# 5. STARTING POWER VALUES (§8.5)
# ════════════════════════════════════════════════════════════════════════════

class TestStartingPowerValues:

    def test_starting_powers(self):
        """Verify starting power values.

        Britain's naval income scales with coastal regions (min(300, 150+50*coastal)).
        With 1 coastal region (Netherlands), Britain gets 200 naval → 400 total.
        Spec §8.5 assumes full 300 naval; actual formula yields less at game start.
        """
        world = _fresh_world()
        france = _power("France", world)
        britain = _power("Britain", world)
        prussia = _power("Prussia", world)
        austria = _power("Austria", world)
        saxony = _power("Saxony", world)

        assert france == 1100, f"France power {france} != 1100"
        assert britain == 400, f"Britain power {britain} != 400"
        assert prussia == 400, f"Prussia power {prussia} != 400"
        assert austria == 650, f"Austria power {austria} != 650"
        assert saxony == 250, f"Saxony power {saxony} != 250"


# ════════════════════════════════════════════════════════════════════════════
# 6-8. CHECK_VASSALAGE_POWER_CAP
# ════════════════════════════════════════════════════════════════════════════

class TestPowerCapCheck:

    def test_allowed_for_saxony(self):
        world = _fresh_world()
        cap = check_vassalage_power_cap(world, "France", "Saxony")
        assert cap["allowed"] is True
        assert cap["reason"] == ""
        assert cap["pct"] < 50

    def test_blocked_for_austria(self):
        world = _fresh_world()
        cap = check_vassalage_power_cap(world, "France", "Austria")
        assert cap["allowed"] is False
        assert cap["pct"] > 50
        assert "too powerful" in cap["reason"]
        assert "Austria" in cap["reason"]

    def test_pct_and_reason_fields(self):
        world = _fresh_world()
        cap = check_vassalage_power_cap(world, "France", "Prussia")
        assert isinstance(cap["lord_power"], int)
        assert isinstance(cap["target_power"], int)
        assert isinstance(cap["pct"], int)
        assert cap["pct"] == int(cap["target_power"] * 100 // cap["lord_power"])

    def test_france_can_vassalize_prussia_britain_saxony_not_austria(self):
        world = _fresh_world()
        for nation in ("Saxony", "Prussia", "Britain"):
            cap = check_vassalage_power_cap(world, "France", nation)
            assert cap["allowed"] is True, f"France should be able to vassalize {nation}"
        cap = check_vassalage_power_cap(world, "France", "Austria")
        assert cap["allowed"] is False, "France should NOT be able to vassalize Austria"

    def test_zero_power_lord_cannot_vassalize(self):
        world = _fresh_world()
        for region in world.regions.values():
            if region.controller == "France":
                region.controller = "Britain"
        cap = check_vassalage_power_cap(world, "France", "Saxony")
        assert cap["allowed"] is False
        assert cap["lord_power"] == 0
        assert "lacks the national power" in cap["reason"]

    def test_eliminated_zero_power_target_cannot_be_vassalized(self):
        world = _fresh_world()
        for region in world.regions.values():
            if region.controller == "Saxony":
                region.controller = "France"
        cap = check_vassalage_power_cap(world, "France", "Saxony")
        assert cap["allowed"] is False
        assert cap["target_power"] == 0
        assert "no national power" in cap["reason"]

    def test_self_vassalage_blocked(self):
        world = _fresh_world()
        cap = check_vassalage_power_cap(world, "France", "France")
        assert cap["allowed"] is False
        assert "itself" in cap["reason"]


# ════════════════════════════════════════════════════════════════════════════
# 9-12. PROJECT_POWER_AFTER_TERMS
# ════════════════════════════════════════════════════════════════════════════

class TestProjectPowerAfterTerms:

    def test_territory_cession_shifts_power(self):
        world = _fresh_world()
        terms = [{"type": "territory_cession", "region": "Berlin",
                  "from": "Prussia", "to": "France"}]
        proj = project_power_after_terms(world, terms, "France", "Prussia")
        berlin_income = world.regions["Berlin"].income_value
        assert proj["France"] == _power("France", world) + berlin_income
        assert proj["Prussia"] == _power("Prussia", world) - berlin_income

    def test_real_territory_cede_regions_shape_shifts_power(self):
        world = _fresh_world()
        terms = [{"type": "territory_cede", "regions": ["Berlin"],
                  "from": "Prussia", "to": "France"}]
        proj = project_power_after_terms(world, terms, "France", "Prussia")
        berlin_income = world.regions["Berlin"].income_value
        assert proj["France"] == _power("France", world) + berlin_income
        assert proj["Prussia"] == _power("Prussia", world) - berlin_income

    def test_invalid_region_skipped(self):
        world = _fresh_world()
        terms = [{"type": "territory_cession", "region": "Atlantis",
                  "from": "Prussia", "to": "France"}]
        proj = project_power_after_terms(world, terms, "France", "Prussia")
        assert proj["France"] == _power("France", world)
        assert proj["Prussia"] == _power("Prussia", world)

    def test_from_nation_mismatch_skipped(self):
        world = _fresh_world()
        terms = [{"type": "territory_cession", "region": "Berlin",
                  "from": "Austria", "to": "France"}]
        proj = project_power_after_terms(world, terms, "France", "Prussia")
        assert proj["France"] == _power("France", world)
        assert proj["Prussia"] == _power("Prussia", world)

    def test_non_territory_terms_skipped(self):
        world = _fresh_world()
        terms = [{"type": "gold_lump", "value": 500,
                  "from": "Prussia", "to": "France"}]
        proj = project_power_after_terms(world, terms, "France", "Prussia")
        assert proj["France"] == _power("France", world)
        assert proj["Prussia"] == _power("Prussia", world)

    def test_duplicate_transfer_skipped(self):
        world = _fresh_world()
        terms = [
            {"type": "territory_cede", "regions": ["Berlin"],
             "from": "Prussia", "to": "France"},
            {"type": "territory_cede", "regions": ["Berlin"],
             "from": "Prussia", "to": "France"},
        ]
        proj = project_power_after_terms(world, terms, "France", "Prussia")
        berlin_income = world.regions["Berlin"].income_value
        assert proj["France"] == _power("France", world) + berlin_income
        assert proj["Prussia"] == _power("Prussia", world) - berlin_income

    def test_projection_does_not_mutate_world_state(self):
        world = _fresh_world()
        controllers_before = {
            rname: region.controller for rname, region in world.regions.items()
        }
        terms = [{"type": "territory_cede", "regions": ["Berlin"],
                  "from": "Prussia", "to": "France"}]
        project_power_after_terms(world, terms, "France", "Prussia")
        controllers_after = {
            rname: region.controller for rname, region in world.regions.items()
        }
        assert controllers_after == controllers_before

    def test_post_cession_allows_vassalage(self):
        """After taking enough Austrian territory, power cap clears."""
        world = _fresh_world()
        cap_before = check_vassalage_power_cap(world, "France", "Austria")
        assert cap_before["allowed"] is False

        terms = [{"type": "territory_cede", "regions": ["Vienna"],
                  "from": "Austria", "to": "France"}]
        cap_after = check_vassalage_power_cap(
            world, "France", "Austria", terms=terms,
        )
        assert cap_after["allowed"] is True
        assert cap_after["target_power"] == 350
        assert cap_after["lord_power"] == 1400


# ════════════════════════════════════════════════════════════════════════════
# 13-16. VASSAL CREATION GATES
# ════════════════════════════════════════════════════════════════════════════

class TestVassalCreationGates:

    def test_treaty_vassalage_blocked_by_power_cap(self):
        world = _fresh_world()
        set_diplomatic_state(world, "France", "Austria", "OPEN_BORDERS", "test")
        result = create_vassal_treaty(world, "France", "Austria")
        assert result["success"] is False
        assert "too powerful" in result["message"] or "cannot" in result["message"].lower()

    def test_treaty_vassalage_allowed_for_minor(self):
        world = _fresh_world()
        set_diplomatic_state(world, "France", "Saxony", "OPEN_BORDERS", "test")
        result = create_vassal_treaty(world, "France", "Saxony")
        assert result["success"] is True

    def test_conquest_vassalage_blocked_by_power_cap(self):
        world = _fresh_world()
        set_diplomatic_state(world, "France", "Austria", "WAR", "test")
        result = create_vassal_conquest(world, "France", "Austria")
        assert result["success"] is False
        assert "cannot impose vassalage" in result["message"].lower() or \
               "too powerful" in result["message"].lower()

    def test_conquest_vassalage_allowed_for_minor(self):
        world = _fresh_world()
        set_diplomatic_state(world, "France", "Saxony", "WAR", "test")
        result = create_vassal_conquest(world, "France", "Saxony")
        assert result["success"] is True


class TestTreatyRatificationPowerCap:

    def test_ratification_blocks_over_cap_vassalage_without_state_corruption(self):
        world = _fresh_world()
        set_diplomatic_state(world, "France", "Austria", "OPEN_BORDERS", "test")
        proposal = {
            "type": "vassalage",
            "proposer_nation": "France",
            "target_nation": "Austria",
            "sweeteners": [],
            "demands": [],
            "clauses": [],
        }

        result = world._ratify_treaty(proposal)

        assert result["type"] == "diplomatic_treaty_failed"
        assert "too powerful" in result["message"]
        assert world.get_diplomatic_state("France", "Austria") == "OPEN_BORDERS"
        assert "Austria" not in world.vassals

    def test_ratification_allows_post_cession_vassalage_package(self):
        world = _fresh_world()
        set_diplomatic_state(world, "France", "Austria", "WAR", "test")
        proposal = {
            "type": "vassalage",
            "proposer_nation": "France",
            "target_nation": "Austria",
            "sweeteners": [],
            "demands": [
                {"type": "territory_cede", "value": 1, "regions": ["Vienna"]},
            ],
            "clauses": [],
        }

        result = world._ratify_treaty(proposal)

        assert result["type"] == "diplomatic_treaty_signed"
        assert world.get_diplomatic_state("France", "Austria") == "VASSAL"
        assert world.vassals["Austria"]["lord"] == "France"
        assert world.regions["Vienna"].controller == "France"


# ════════════════════════════════════════════════════════════════════════════
# 17-18. WIZARD PROPOSE_VASSAL AVAILABILITY
# ════════════════════════════════════════════════════════════════════════════

class TestWizardVassalAvailability:

    def test_propose_vassal_disabled_when_too_powerful(self):
        world = _fresh_world()
        set_diplomatic_state(world, "France", "Austria", "OPEN_BORDERS", "test")
        actions = get_available_diplomatic_actions(world, "Austria")
        vassal_action = next(
            (a for a in actions if a["action"] == "propose_vassal"), None,
        )
        assert vassal_action is not None
        assert vassal_action["available"] is False
        assert "too powerful" in vassal_action["disabled_reason"]

    def test_propose_vassal_enabled_for_minor(self):
        world = _fresh_world()
        set_diplomatic_state(world, "France", "Saxony", "OPEN_BORDERS", "test")
        world.diplomatic_points = 5
        actions = get_available_diplomatic_actions(world, "Saxony")
        vassal_action = next(
            (a for a in actions if a["action"] == "propose_vassal"), None,
        )
        assert vassal_action is not None
        assert vassal_action["available"] is True

    def test_typed_vassalage_proposal_blocked_when_too_powerful(self):
        world = _fresh_world()
        world.diplomatic_points = 10
        set_diplomatic_state(world, "France", "Austria", "OPEN_BORDERS", "test")
        executor = DiplomaticExecutor(None)

        result = executor._execute_diplomatic_proposal(
            {"target_nation": "Austria", "proposal_type": "vassalage"},
            world,
        )

        assert result["success"] is False
        assert "too powerful" in result["message"]
        assert world.proposal_in_transit is None

    def test_send_vassalage_proposal_blocked_before_dp_loss(self):
        world = _fresh_world()
        world.diplomatic_points = 10
        set_diplomatic_state(world, "France", "Austria", "OPEN_BORDERS", "test")
        dialogue = {
            "target_nation": "Austria",
            "context": {"proposal_type": "vassalage"},
        }
        selected = {
            "terms": {
                "type": "vassalage",
                "proposal_type": "vassalage",
                "sweeteners": [],
                "demands": [],
                "clauses": [],
            },
        }

        result = DiplomaticExecutor(None)._process_dialogue_choice(
            "execute_proposal", selected, dialogue, world,
        )

        assert result["success"] is False
        assert "too powerful" in result["message"]
        assert world.diplomatic_points == 10
        assert world.proposal_in_transit is None


# ════════════════════════════════════════════════════════════════════════════
# 19. WAR PURPOSE POPUP — SUBJUGATION POWER CAP
# ════════════════════════════════════════════════════════════════════════════

class TestWarPurposeSubjugation:

    def test_subjugation_greyed_out_with_power_pct(self):
        world = _fresh_world()
        objectives = get_available_war_objectives(world, "France", "Austria")
        subj = next(o for o in objectives if o["type"] == "subjugation")
        assert subj["available"] is False
        assert subj["reason"] is not None
        assert "power_pct" in subj
        assert isinstance(subj["power_pct"], int)
        assert subj["power_pct"] > 50

    def test_subjugation_available_for_minor(self):
        world = _fresh_world()
        objectives = get_available_war_objectives(world, "France", "Saxony")
        subj = next(o for o in objectives if o["type"] == "subjugation")
        assert subj["available"] is True
        assert subj.get("reason") is None

    def test_conquest_always_available_regardless_of_power(self):
        world = _fresh_world()
        for target in ("Saxony", "Austria"):
            objectives = get_available_war_objectives(world, "France", target)
            conquest = next(o for o in objectives if o["type"] == "conquest")
            assert conquest["available"] is True

    def test_forced_alliance_always_available_regardless_of_power(self):
        world = _fresh_world()
        for target in ("Saxony", "Austria"):
            objectives = get_available_war_objectives(world, "France", target)
            fa = next(o for o in objectives if o["type"] == "forced_alliance")
            assert fa["available"] is True


# ════════════════════════════════════════════════════════════════════════════
# 20. SERIALIZATION — power cap helpers have no new state
# ════════════════════════════════════════════════════════════════════════════

class TestPowerCapNoNewState:
    """Power cap is a pure computation — no new WorldState fields to serialize."""

    def test_no_new_serialization_fields(self):
        world = _fresh_world()
        d = world.to_dict()
        world2 = WorldState.from_dict(d)
        assert _power("France", world2) == _power("France", world)
        assert _power("Austria", world2) == _power("Austria", world)
