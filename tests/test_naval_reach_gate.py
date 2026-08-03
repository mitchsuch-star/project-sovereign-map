"""NV-9 — THE REACH GATE and the adversarial-review fixes (August 2, 2026).

A 6-lens find→refute review fleet over the day's naval work (commits
7b9cf91..89576c5) returned 16 findings. The refuters were cut short by a
credit exhaustion, so EVERY claim here was re-verified by hand before it
was fixed; the headline reproduced exactly as reported.

THE P1, measured on master at 89576c5:

    Murat (cavalry, movement_range 2) at Paris, Moore at London.
    `attack Moore` → success=True, and **Murat ended the turn standing in
    London** — having crossed water the Royal Navy commands at 1.9x.

Why: `crossing_check` gates the DIRECT pair, and `is_sea_link(Paris,
London)` is False, so it early-returned "open" and neither the ratio arm
nor the NV-4 host rule ever ran. The water was on the MIDDLE leg. The
2-tile MOVE seam had always checked both legs; the attack, the charge and
the post-victory advance had not.
"""
import os

import pytest

from backend.ai.enemy_ai import EnemyAI
from backend.commands.executor import CommandExecutor
from backend.game_logic import naval
from backend.models.world_state import WorldState

SCENARIO = os.path.join(
    "godot-client", "project-sovereign", "assets", "maps", "europe_1805.json")


@pytest.fixture(scope="module")
def _booted():
    return WorldState.from_scenario(SCENARIO)


@pytest.fixture()
def world(_booted):
    return WorldState.from_dict(_booted.to_dict())


@pytest.fixture()
def executor():
    return CommandExecutor()


def _cavalry_at(world, name, region, strength=30000):
    marshal = world.get_marshal(name)
    marshal.location = region
    marshal.strength = strength
    world._build_marshal_index()
    return marshal


class TestTheReachGate:
    def test_the_water_on_the_middle_leg_is_seen(self, world):
        """The predicate itself. Paris→London is distance 2 and its only
        route runs through the Normandy sea link, which is SHUT to France
        — the direct pair cannot see that, the reach form must."""
        assert world.get_distance("Paris", "London") == 2
        assert naval.crossing_allowed(world, "France", "Paris", "London") is True
        assert naval.crossing_allowed(world, "France", "Normandy", "London") is False
        reach = naval.crossing_check_reach(world, "France", "Paris", "London")
        assert reach["allowed"] is False
        assert reach["coverer"] == "Britain"

    def test_a_dry_route_still_passes(self, world):
        """The gate refuses the SEA, not the range. Two land steps inside
        France are untouched — otherwise every cavalry strike in Europe
        would be blocked by a rule about the Channel."""
        assert world.get_distance("Paris", "Burgundy") <= 2
        assert naval.crossing_check_reach(
            world, "France", "Paris", "Burgundy")["allowed"] is True

    def test_one_step_keeps_the_direct_verdict(self, world):
        """At range 1 the reach form IS the direct form — byte-identical,
        so nothing about the existing seams changed underneath them."""
        for origin, dest in (("Normandy", "London"), ("Paris", "Normandy"),
                             ("London", "Normandy")):
            direct = naval.crossing_check(world, "France", origin, dest)
            reach = naval.crossing_check_reach(world, "France", origin, dest)
            assert reach["allowed"] == direct["allowed"]
            assert reach["verdict"] == direct["verdict"]


class TestTheCavalryChannelHop:
    def test_the_attack_verb_refuses_the_hop(self, world, executor):
        """THE P1, pinned. Reproduces the exact measured shape."""
        murat = _cavalry_at(world, "Murat", "Paris")
        assert getattr(murat, "cavalry", False) is True
        assert murat.movement_range == 2
        moore = world.get_marshal("Moore")
        moore.location = "London"
        moore.strength = 8000
        world._build_marshal_index()
        world.actions_remaining = 9

        result = executor.execute(
            {"command": {"marshal": "Murat", "action": "attack",
                         "target": "Moore", "type": "specific"}},
            {"world": world})
        assert result["success"] is False
        assert result.get("blocked_naval") == "Britain"
        # The measured failure was the POSITION, so pin the position.
        assert murat.location == "Paris"
        assert world.regions["London"].controller == "Britain"

    def test_the_charge_verb_refuses_it_too(self, world, executor):
        """The Glorious Charge only gated its ADVANCE, so a reckless
        squadron could fight the full 2x-damage battle across the Channel
        for free and simply not move. The verb the attack arm refuses
        outright cannot be a bypass."""
        murat = _cavalry_at(world, "Murat", "Normandy")
        moore = world.get_marshal("Moore")
        moore.location = "London"
        moore.strength = 8000
        world._build_marshal_index()
        result = executor._combat._execute_glorious_charge(
            murat, "Moore", world, {"world": world})
        assert result["success"] is False
        assert result.get("blocked_naval") == "Britain"
        assert murat.location == "Normandy"

    def test_the_ai_never_scores_the_hop(self, world):
        """GR5: the council reads the same reach predicate, so it cannot
        order what the executor refuses."""
        murat = _cavalry_at(world, "Murat", "Paris")
        moore = world.get_marshal("Moore")
        moore.location = "London"
        moore.strength = 4000
        world._build_marshal_index()
        ai = EnemyAI(CommandExecutor())
        offered = ai._find_attack_opportunity(murat, "France", world)
        assert not (offered and offered.get("target") in ("Moore", "London"))

    def test_beating_the_fleet_opens_the_hop(self, world, executor):
        """Control arm — the refusal is the SEA, not the geometry. Sink
        the Royal Navy and the same charge lands in London."""
        naval.get_fleet(world, "Britain")["ships"] = 0
        naval.get_fleet(world, "Russia")["ships"] = 0
        murat = _cavalry_at(world, "Murat", "Paris")
        moore = world.get_marshal("Moore")
        moore.location = "London"
        moore.strength = 3000
        world._build_marshal_index()
        assert naval.crossing_check_reach(
            world, "France", "Paris", "London")["allowed"] is True


class TestTheAdvanceIsAMove:
    def test_a_victor_does_not_sail_home_on_his_victory(self, world):
        """The post-battle advance was a bare `move_to` with no naval
        check at all. One seam now answers for every post-combat move."""
        combat = CommandExecutor()._combat
        murat = _cavalry_at(world, "Murat", "Normandy")
        assert combat._naval_advance_allowed(murat, "London", world) is False
        # ...and a land advance is untouched.
        assert combat._naval_advance_allowed(murat, "Paris", world) is True
        # Standing still is always allowed (the no-op arm).
        assert combat._naval_advance_allowed(murat, "Normandy", world) is True


class TestGunsAcrossTheStraitAreRefusedBeforeTheWar:
    def test_no_war_is_bought_for_an_impossible_order(self, world, executor):
        """Ordering bug: the strait rule lived only at the bombardment
        seam, BELOW the auto-war-declaration. At peace nothing covers a
        strait, so the crossing gate passed, the war-purpose card staged,
        and the player bought a war — and only then heard that guns do not
        carry across water. The refusal is now above the declaration."""
        # Isolate the ORDERING claim: with no fleet covering the strait
        # the crossing gate passes (its own refusal would mask this one),
        # which is exactly the peacetime case the finding described.
        for nation in list(world.fleets):
            rec = world.fleets.get(nation)
            if isinstance(rec, dict) and nation != "France":
                rec["ships"] = 0
        battery = world.get_marshal("Ney")
        battery.artillery = True
        battery.location = "Normandy"
        battery.strength = 12000
        target = world.get_marshal("Moore")
        target.location = "London"
        target.strength = 6000
        world.diplomatic_states[
            world._make_diplo_key("France", "Britain")] = "PEACE"
        world.invalidate_active_nations_cache()
        world._build_marshal_index()
        assert not world.is_at_war("France", "Britain")
        assert naval.crossing_check_reach(
            world, "France", "Normandy", "London")["allowed"] is True

        result = executor._combat._execute_attack(
            battery, "Moore", world, {"world": world})
        assert result["success"] is False
        assert "open water" in result["message"]
        # THE POINT: no war was declared to learn that.
        assert not world.is_at_war("France", "Britain")


class TestTheMusterPreviewTellsTheTruth:
    def test_a_sea_barred_corps_is_not_promised(self, world):
        """Rule 2b withholds a reinforcing corps across a covered link,
        but the preview ladder had no naval arm — so it listed him as
        answering the guns and the committed figure lied. NV-5's own
        expedition made this common: a corps lands at Normandy and
        London's garrison is shown 'coming'."""
        combat = CommandExecutor()._combat
        # France fights at London (its own descent) with a corps still on
        # the Norman shore — the crossing between them is SHUT to France,
        # which is precisely Rule 2b's case.
        primary = world.get_marshal("Ney")
        primary.location = "London"
        primary.strength = 12000
        candidate = world.get_marshal("Davout")
        candidate.location = "Normandy"
        candidate.strength = 6000
        world._build_marshal_index()
        assert naval.crossing_allowed(
            world, "France", "Normandy", "London") is False

        eligible = combat._is_reinforcement_eligible(
            candidate, primary, "London", "France", world)
        will_join, reason = combat._muster_reason(
            candidate, primary, "London", "France", world)
        # The preview and the mechanic must agree — that is the contract.
        assert eligible is False
        assert will_join is False
        assert reason == "sea_barred"

    def test_the_reason_has_player_facing_copy(self):
        """A raw reason code must never reach the muster block."""
        from backend.display_names import MUSTER_REASON_DISPLAY
        assert "sea_barred" in MUSTER_REASON_DISPLAY
        assert "_" not in MUSTER_REASON_DISPLAY["sea_barred"]


class TestTheSavedAdjacencyIsReconciled:
    def test_a_pre_nv8c_save_loses_the_dead_edge(self, world):
        """`adjacent_regions` is serialized, but the registry is the
        single source for adjacency AND sea_links. A save taken before
        NV-8c reloaded with London-Flanders still WALKABLE while
        `is_sea_link` (live registry) answered False — so the crossing
        gate early-returned 'open' and that one edge became a free,
        ungated Channel march with neither the A5 headline nor the host
        rule on it."""
        stale = world.to_dict()
        stale["regions"]["London"]["adjacent_regions"] = sorted(
            set(stale["regions"]["London"]["adjacent_regions"]) | {"Flanders"})
        stale["regions"]["Flanders"]["adjacent_regions"] = sorted(
            set(stale["regions"]["Flanders"]["adjacent_regions"]) | {"London"})

        loaded = WorldState.from_dict(stale)
        assert "Flanders" not in loaded.regions["London"].adjacent_regions
        assert "London" not in loaded.regions["Flanders"].adjacent_regions
        # ...and the live crossing is untouched.
        assert "Normandy" in loaded.regions["London"].adjacent_regions

    def test_a_live_edge_is_never_pruned(self, world):
        """Negative control: an ordinary round-trip loses nothing."""
        loaded = WorldState.from_dict(world.to_dict())
        for name, region in world.regions.items():
            assert sorted(loaded.regions[name].adjacent_regions) == \
                sorted(region.adjacent_regions), name

    def test_an_unknown_province_set_is_left_alone(self):
        """Scoped tight: where the registry does not know the provinces
        (the legacy fixture, a mod), the SAVE is the source."""
        from backend.models.world_state import _reconcile_saved_adjacency
        from backend.models.region import create_regions, create_europe_regions
        legacy = create_regions()
        # ELEVEN legacy names also exist on the Europe map with entirely
        # different neighbours — the first cut reconciled per-province and
        # pruned ten legacy edges. Name overlap is not identity.
        overlap = set(legacy) & set(create_europe_regions())
        assert len(overlap) >= 10, "the trap this scope guards must be live"
        before = {n: list(r.adjacent_regions) for n, r in legacy.items()}
        assert _reconcile_saved_adjacency(legacy) == 0
        for name, adj in before.items():
            assert legacy[name].adjacent_regions == adj


class TestTheDioramaTellsOneStory:
    def test_an_annihilated_squadron_stays_in_the_line(self, world):
        """`iter_fleets` yields only ships > 0, so a squadron ANNIHILATED
        in the action vanished from the tableau — its dead uncounted, the
        odometer under the Admiralty's own figure on the same screen. The
        losses dict IS §4.4's record of who bled."""
        naval.get_fleet(world, "Holland")["ships"] = 1
        naval.get_fleet(world, "Holland")["readiness"] = 40
        result = naval.resolve_fleet_action(world, "France", "Britain")
        payload = result["naval_diorama"]
        losses = result["losses"]["France"]
        if losses.get("Holland", 0) < 1:
            pytest.skip("Holland survived this roll — no annihilation to pin")
        assert naval.get_fleet(world, "Holland")["ships"] == 0
        names = {c["nation"] for c in payload["attacker"]["contingents"]}
        assert "Holland" in names
        # The odometer must equal the verdict's own arithmetic.
        assert payload["attacker"]["casualties_total"] == sum(losses.values())

    def test_the_odometer_always_equals_the_verdict(self, world):
        """The general form of the same contract, both sides."""
        result = naval.resolve_fleet_action(world, "France", "Britain")
        payload = result["naval_diorama"]
        for side, nation in (("attacker", "France"), ("defender", "Britain")):
            assert payload[side]["casualties_total"] == sum(
                result["losses"].get(nation, {}).values())

    def test_an_indecisive_action_is_not_reported_as_a_triumph(self, world):
        """`_decisive()` read the LAND grammar (outcome == a victory), and
        a fleet action always carries a victor — so every sea action was
        'decisive', the indecisive banner was dead code, and a squadron
        that merely had the better of it read THE SEA IS OURS while the
        Admiralty said the enemy drew off in order. The payload carries
        §4.4's real answer; the client now reads it."""
        naval.get_fleet(world, "France")["ships"] = 95
        naval.get_fleet(world, "France")["readiness"] = 100
        result = naval.resolve_fleet_action(world, "France", "Britain")
        payload = result["naval_diorama"]
        assert payload["decisive"] == result["decisive"]
        assert payload["outcome"] in ("attacker_victory", "defender_victory")
        # The land grammar would have called this decisive whatever it was.
        if not result["decisive"]:
            assert payload["decisive"] is False

    def test_the_client_reads_the_naval_flag(self):
        """Static pin (the U5 idiom): _decisive() must branch on _is_naval."""
        gd = os.path.join("godot-client", "project-sovereign", "scripts",
                          "battle_diorama.gd")
        with open(gd, encoding="utf-8") as handle:
            source = handle.read()
        body = source.split("func _decisive()")[1].split("func ")[0]
        assert "_is_naval()" in body
        assert '_data.get("decisive"' in body

    def test_the_blockade_chip_never_leaks_a_raw_tag(self, world):
        """R7 at the chip: 'closes KingdomOfItaly' was reachable the
        moment Italy entered the war."""
        from backend.display_names import NATION_DISPLAY
        world.player_nation = "Britain"
        world.diplomatic_states[
            world._make_diplo_key("Britain", "KingdomOfItaly")] = "WAR"
        naval.get_fleet(world, "Britain")["posture"] = "guard"
        chips = {c["command"]: c
                 for c in naval.build_admiralty_report(world)["chips"]}
        note = chips["blockade the enemy"]["note"]
        for tag, display in NATION_DISPLAY.items():
            assert tag not in note or display in note

    def test_the_sea_overflow_is_squadrons(self):
        """'corps in reserve' is a land word — the NV-8b sweep missed it."""
        gd = os.path.join("godot-client", "project-sovereign", "scripts",
                          "battle_diorama.gd")
        with open(gd, encoding="utf-8") as handle:
            source = handle.read()
        assert "squadrons astern" in source


class TestTheConqueredCoast:
    """NV-10 — found by DRIVING the A2 strangulation arc, not by reading.

    The scripted drive marched Soult and Lannes on Portugal (Junot, 1807 —
    the Continental System's own central act, undertaken precisely to shut
    Lisbon to British trade). France took all four Portuguese provinces by
    turn 12 and the closure went DOWN, 38.5% → 23.1%. Conquering a coast
    has to CLOSE it.

    Cause: `closure_against` read only who a court was AT WAR with, and
    ports are authored per NATION (§3.2 deliberately keeps the denominator
    authored). A neutral whose coastline had been overrun still counted as
    open. A court whose CAPITAL is held by a power at war with the target
    now counts as closed — the conqueror keeps the harbour, and the
    conqueror is at war.

    Measured after: taking Lisbon flips 38.5% → 42.3% and fires the
    `cs_tier_shift` to tier 1 on turn 9 of the same drive.
    """

    def test_the_boot_fact_is_untouched(self, world):
        """§5.1's pinned boot arithmetic — nobody is conquered at boot, so
        the new arm must contribute exactly nothing."""
        assert naval.closure_against(world, "Britain") == pytest.approx(
            10 / 26, abs=0.001)
        assert naval.cs_closure_tier(
            naval.closure_against(world, "Britain")) == 0

    def test_taking_the_capital_closes_the_coast(self, world):
        """The historical act, as a unit: Lisbon falls, Portugal's two
        ports join the closure, and the System crosses its first notch."""
        before = naval.closure_against(world, "Britain")
        capital = world.get_nation_capital("Portugal")
        assert capital, "Portugal must have an authored capital"
        world.regions[capital].controller = "France"
        world.invalidate_active_nations_cache()
        after = naval.closure_against(world, "Britain")
        assert after > before
        portuguese_ports = int(world.fleets["Portugal"].get("ports", 0))
        total = naval.continental_ports_total(world)
        assert after == pytest.approx(before + portuguese_ports / total,
                                      abs=0.001)
        assert naval.cs_closure_tier(after) == 1

    def test_a_neutral_conqueror_closes_nothing(self, world):
        """Scoped: the harbour shuts to the TARGET only when its new owner
        is at war with the target. A conquest by a court at peace with
        Britain leaves Britain's trade alone."""
        before = naval.closure_against(world, "Britain")
        capital = world.get_nation_capital("Portugal")
        world.regions[capital].controller = "Austria"   # Britain's ally
        world.invalidate_active_nations_cache()
        assert not world.is_at_war("Austria", "Britain")
        assert naval.closure_against(world, "Britain") == pytest.approx(
            before, abs=0.001)

    def test_a_court_still_holding_its_capital_is_untouched(self, world):
        """Losing a province is not losing the war — only the capital
        flips the reading, which is the same threshold the rest of the
        game uses for a court being overrun."""
        before = naval.closure_against(world, "Britain")
        world.regions["Porto"].controller = "France"    # not the capital
        world.invalidate_active_nations_cache()
        assert naval.closure_against(world, "Britain") == pytest.approx(
            before, abs=0.001)
