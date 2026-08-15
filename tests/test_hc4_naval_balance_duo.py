"""HC-4 "The Lifeline and the Bill" (gate §5) — the naval-balance duo.

(a) The Royal Navy's lifeline: ONE arm in `process_supply_attrition`
    reading the abstraction's own coverage (blockade posture projects;
    a side's pooled fleet convoys), granting or stripping the EXISTING
    1.5× home-turf multiplier. Zero new constants, zero new serialized
    fields; contested or empty water → today's numbers byte-identically;
    GR5 — the same loop serves both boards.
(b) The Admiralty's bill: the AI's naval_expedition / naval_diversion
    bill at the `world._action_costs` TABLE price (2 / 1) against its
    2-AP admin budget, and the expedition rung is affordability-gated.

Both halves carry a flip lever (`naval.SHORE_SUPPLY_ACTIVE`,
`enemy_ai.AI_NAVAL_AP_PARITY`) for the BASELINE_SERIES attribution
experiment — False reproduces the pre-slice behavior byte-identically.
"""

from pathlib import Path
from types import SimpleNamespace

import pytest

from backend.game_logic import naval
from backend.models.world_state import WorldState

from tests.conftest import MarshalFactory, WorldFactory

SCENARIO_PATH = (
    Path(__file__).resolve().parents[1]
    / "godot-client" / "project-sovereign" / "assets" / "maps"
    / "europe_1805.json"
)


@pytest.fixture
def europe():
    world = WorldState.from_scenario(str(SCENARIO_PATH))
    naval.derive_ai_postures(world)
    return world


class TestShoreVerdicts:
    """The tri-state on the 1805 boot — measured facts, pinned."""

    def test_boot_french_coast_is_contested_none(self, europe):
        # The Combined Fleet is outmatched but AFLOAT — the Royal
        # Navy's watch does not yet starve the French coast. Boot
        # supply numbers are byte-identical by construction.
        assert naval.shore_supply_state(europe, "France", "Brittany") is None

    def test_britain_ashore_reads_lifeline(self, europe):
        # The motivating case: an at-war British corps on a continental
        # shore eats like a home army under the Royal Navy's convoys.
        assert naval.shore_supply_state(
            europe, "Britain", "Lisbon") == "lifeline"

    def test_post_trafalgar_france_is_strangled(self, europe):
        for nation in ("France", "Spain", "Holland"):
            naval.get_fleets(europe)[nation]["ships"] = 0
        assert naval.shore_supply_state(
            europe, "France", "Brittany") == "strangled"

    def test_fleetless_world_reads_none(self):
        world = WorldFactory.with_war("France", "Britain")
        assert naval.shore_supply_state(world, "France", "Brittany") is None

    def test_flip_lever_restores_none(self, europe, monkeypatch):
        monkeypatch.setattr(naval, "SHORE_SUPPLY_ACTIVE", False)
        assert naval.shore_supply_state(
            europe, "Britain", "Lisbon") is None


class TestLifelineArm:
    """The supply-attrition integration — the arm grants/strips the
    SAME 1.5× multiplier, and only where the verdict says so."""

    def _overstacked(self, europe, nation, region_name, strength=90000):
        """Park one over-capacity corps of `nation` on `region_name`."""
        m = MarshalFactory.infantry(
            name="HC4Test", location=region_name, strength=strength,
            nation=nation, personality="cautious")
        europe.marshals.clear()
        europe.marshals[m.name] = m
        return m

    def _attrition_losses(self, europe, marshal):
        before = marshal.strength
        europe.process_supply_attrition()
        return before - marshal.strength

    def test_lifeline_feeds_the_landed_army(self, europe, monkeypatch):
        # Britain over-stacked on FRENCH coastal soil (at war, hostile
        # shore): with the arm the RN lifeline applies the 1.5× cap the
        # army would only have at home — measured as LOWER attrition
        # than with the lever off.
        m = self._overstacked(europe, "Britain", "Brittany")
        region = europe.regions["Brittany"]
        assert region.is_coastal and region.controller == "France"
        with_arm = self._attrition_losses(europe, m)

        m.strength = 90000
        monkeypatch.setattr(naval, "SHORE_SUPPLY_ACTIVE", False)
        without_arm = self._attrition_losses(europe, m)
        assert with_arm < without_arm

    def test_strangled_shore_strips_the_home_bonus(self, europe,
                                                   monkeypatch):
        # Post-Trafalgar France over-stacked on its OWN coast: the
        # dominating hostile fleet strips the 1.5× home treatment —
        # measured as HIGHER attrition than with the lever off.
        for nation in ("France", "Spain", "Holland"):
            naval.get_fleets(europe)[nation]["ships"] = 0
        m = self._overstacked(europe, "France", "Brittany")
        with_arm = self._attrition_losses(europe, m)

        m.strength = 90000
        monkeypatch.setattr(naval, "SHORE_SUPPLY_ACTIVE", False)
        without_arm = self._attrition_losses(europe, m)
        assert with_arm > without_arm

    def test_inland_army_untouched(self, europe, monkeypatch):
        # The arm never reaches a non-coastal province — byte-identical
        # attrition with the lever on or off.
        m = self._overstacked(europe, "Britain", "Swabia")
        assert not europe.regions["Swabia"].is_coastal
        with_arm = self._attrition_losses(europe, m)
        m.strength = 90000
        monkeypatch.setattr(naval, "SHORE_SUPPLY_ACTIVE", False)
        without_arm = self._attrition_losses(europe, m)
        assert with_arm == without_arm

    def test_peacetime_army_untouched(self, europe, monkeypatch):
        # An army whose nation wages no war keeps today's numbers even
        # on a coastal province (the arm gates on AT WAR).
        for key in list(europe.diplomatic_states):
            if "Britain" in key.split("|"):
                europe.diplomatic_states[key] = "PEACE"
        m = self._overstacked(europe, "Britain", "Brittany")
        with_arm = self._attrition_losses(europe, m)
        m.strength = 90000
        monkeypatch.setattr(naval, "SHORE_SUPPLY_ACTIVE", False)
        without_arm = self._attrition_losses(europe, m)
        assert with_arm == without_arm


class TestShownEqualsAppliedCap:
    """Review round [13]: the dispatch's supply_strain headline and the
    attrition pass read ONE effective-cap source."""

    def test_effective_cap_is_shore_aware(self, europe):
        region = europe.regions["Brittany"]
        base = int(region.supply_capacity)
        # Contested boot water: home turf keeps its 1.5x.
        assert europe.get_effective_supply_cap("France", region) == \
            int(base * 1.5)
        # Post-Trafalgar: the strangled home coast loses it.
        for nation in ("France", "Spain", "Holland"):
            naval.get_fleets(europe)[nation]["ships"] = 0
        assert europe.get_effective_supply_cap("France", region) == base
        # The convoyed landing eats like a home army.
        assert europe.get_effective_supply_cap("Britain", region) == \
            int(base * 1.5)

    def test_dispatch_strain_reads_the_strangled_cap(self, europe):
        """A stack legal under the OLD inline 1.5x formula but over the
        strangled cap must HEADLINE — the old dispatch read 'no strain'
        while the attrition pass was killing men."""
        from backend.game_logic.dispatch import _supply_strain_candidate
        for nation in ("France", "Spain", "Holland"):
            naval.get_fleets(europe)[nation]["ships"] = 0
        region = europe.regions["Brittany"]
        base = int(region.supply_capacity)
        strength = int(base * 1.2)  # between base and 1.5x base
        m = MarshalFactory.infantry(
            name="HC4Strain", location="Brittany", strength=strength,
            nation="France", personality="cautious")
        europe.marshals.clear()
        europe.marshals[m.name] = m
        turn = int(europe.current_turn)
        for stamp in (turn - 1, turn):
            europe.event_log.append({
                "type": "supply_attrition", "turn": stamp,
                "marshal": m.name, "nation": "France",
                "region": "Brittany", "losses": 500,
                "message": "Supply shortage at Brittany",
            })
        candidate = _supply_strain_candidate(europe, "France")
        assert candidate is not None, (
            "the strangled strain never headlined — the dispatch is "
            "still reading the pre-HC-4a inline cap")
        assert candidate["region"] == "Brittany"
    """(b) — the billing seam and the affordability gate."""

    def _ai_with_stub_executor(self):
        from backend.ai.enemy_ai import EnemyAI
        ai = EnemyAI(SimpleNamespace(
            execute=lambda cmd, gs: {"success": True}))
        return ai

    def _run_phase(self, ai, picks):
        """Drive execute_admin_phase with a scripted pick sequence;
        returns the unused-AP gold bonus paid to the nation."""
        world = WorldFactory.with_war("Britain", "France",
                                      player_nation="France")
        world.fleets = {"Britain": {"ships": 10, "readiness": 100,
                                    "posture": "guard", "ports": 5,
                                    "dockyards": [], "island": True}}
        world.nation_gold["Britain"] = 0
        queue = list(picks)
        ai._pick_admin_action = (
            lambda nation, w, ap, skips: queue.pop(0) if queue else None)
        ai.execute_admin_phase("Britain", world, {"world": world})
        return world.nation_gold.get("Britain", 0)

    def test_expedition_bills_the_whole_admin_phase(self):
        ai = self._ai_with_stub_executor()
        bonus = self._run_phase(ai, [
            {"action": "naval_expedition", "marshal": "Moore",
             "target": "Lisbon", "confirmed": True},
        ])
        # 2 AP billed of 2 — nothing left to convert to gold.
        assert bonus == 0

    def test_diversion_bills_one(self):
        ai = self._ai_with_stub_executor()
        bonus = self._run_phase(ai, [
            {"action": "naval_diversion", "marshal": None, "target": None},
        ])
        assert bonus == 25  # 1 of 2 AP left -> the 25g conversion

    def test_land_actions_keep_the_flat_price(self):
        ai = self._ai_with_stub_executor()
        bonus = self._run_phase(ai, [
            {"action": "recruit", "marshal": "X", "target": None},
        ])
        assert bonus == 25

    def test_flip_lever_restores_flat_billing(self, monkeypatch):
        import backend.ai.enemy_ai as enemy_ai_module
        monkeypatch.setattr(enemy_ai_module, "AI_NAVAL_AP_PARITY", False)
        ai = self._ai_with_stub_executor()
        bonus = self._run_phase(ai, [
            {"action": "naval_expedition", "marshal": "Moore",
             "target": "Lisbon", "confirmed": True},
        ])
        assert bonus == 25  # pre-slice: the descent cost 1 of 2

    def test_rung_is_affordability_gated(self, europe, monkeypatch):
        """With 1 AP left the 2-AP expedition is never PICKED — the
        bill must be payable, not overdrawn into a hidden discount."""
        from backend.ai.enemy_ai import EnemyAI
        sentinel = {"action": "naval_expedition", "marshal": "Moore",
                    "target": "Lisbon", "confirmed": True}
        calls = []

        def fake_find(world, nation):
            calls.append(nation)
            return dict(sentinel)

        monkeypatch.setattr(naval, "find_ai_expedition", fake_find)
        ai = EnemyAI(SimpleNamespace(execute=lambda c, g: {"success": True}))
        # Skip every rung above the expedition so the pick reaches it.
        skips = {"recruit", "grant_dotation", "recruit_marshal",
                 "build_fleet", "invest_in_vassal",
                 "grant_region_to_vassal", "change_vassal_autonomy",
                 "grant_pension"}
        europe.nation_gold["Britain"] = 0
        picked_at_2 = ai._pick_admin_action("Britain", europe, 2,
                                            set(skips))
        picked_at_1 = ai._pick_admin_action("Britain", europe, 1,
                                            set(skips))
        assert picked_at_2 is not None \
            and picked_at_2.get("action") == "naval_expedition"
        assert (picked_at_1 is None
                or picked_at_1.get("action") != "naval_expedition")

    def test_table_price_is_the_single_source(self):
        # The parity bills at the TABLE, not a copied literal.
        world = WorldFactory.basic()
        assert world._action_costs["naval_expedition"] == 2
        assert world._action_costs["naval_diversion"] == 1
