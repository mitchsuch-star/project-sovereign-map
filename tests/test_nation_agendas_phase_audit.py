"""Phase-audit fixes for Nation Agendas NA-0..NA-6b (July 18, 2026).

Audit memo: docs/audits/NATION_AGENDAS_PHASE_AUDIT_2026_07_18.md.

Four findings, four fix families:

  P1  deny satisfaction was anchored on BLOC MEMBERSHIP, and a coalition
      formed in play is not a bloc — `coalition.form_coalition` writes no
      ALLIANCE rows at all. A denier left in a bloc of one read its design
      SATISFIED while the denied great power held every listed province.
  P2  yielding to an ultimatum after the pair fell to WAR still executed
      the whole concession and reported "The peace holds".
  P3  an armistice both WOKE a guard_neutrality design and STRIPPED the war
      exemption from the army standing on that soil because of that war.
  C   a court that had WON its design could not be priced at ENTRENCH,
      because both acceptance scorers gate on the ACTIVE view.

The inverted-geometry arms deliberately leave co-belligerents at PEACE
rather than hand-writing ALLIANCE rows — hand-writing them is precisely
what hid this geometry from three prior slice reviews.
"""

import os
from pathlib import Path

import pytest

from backend.models.world_state import WorldState
from backend.game_logic import agendas, coalition, diplomacy

SCENARIO_PATH = (
    Path(__file__).parent.parent
    / "godot-client/project-sovereign/assets/maps/europe_1805.json"
)

LOW_COUNTRIES = ["Flanders", "Brabant", "Amsterdam"]


@pytest.fixture(scope="module")
def world1805():
    os.environ.pop("SOVEREIGN_SCENARIO", None)
    return WorldState.from_scenario(str(SCENARIO_PATH))


@pytest.fixture
def world(world1805):
    import copy
    return copy.deepcopy(world1805)


def _refresh(world):
    world.invalidate_bloc_members_cache()
    world.invalidate_active_nations_cache()
    world._agenda_cache = None


def _unally(world, nation):
    """Strip a court's formal alliances — what a coalition formed IN PLAY
    actually leaves behind (see TestCoalitionIsNotABloc)."""
    for other in list(world.get_active_nations()):
        if other == nation:
            continue
        if world.get_diplomatic_state(nation, other) in (
                "ALLIANCE", "DEFENSIVE_ALLIANCE"):
            diplomacy.set_diplomatic_state(world, nation, other, "PEACE")
    _refresh(world)


def _grind_france_down(world, taker="Austria", count=45):
    """The war goes badly for France: `taker` overruns the French camp.
    Britain's own design targets are deliberately NEVER touched."""
    moved = 0
    for name, region in world.regions.items():
        if name in LOW_COUNTRIES:
            continue
        if moved >= count:
            break
        if region.controller in ("France", "Bavaria", "Wurttemberg",
                                 "Baden", "Switzerland"):
            region.controller = taker
            moved += 1
    _refresh(world)
    return moved


# ══════════════════ THE LOAD-BEARING FALSE PREMISE ════════════════════════

class TestCoalitionIsNotABloc:
    """Spec §18 justified scoping deny satisfaction to bloc membership with
    "Coalition formation produces real ALLIANCE states". It does not. The
    boot Third Coalition is allied only because europe_1805.json authors
    those rows."""

    def test_form_coalition_writes_no_alliance_rows(self, world):
        members = ["Austria", "Britain", "Prussia", "Russia"]
        for a in list(world.get_active_nations()):
            for b in list(world.get_active_nations()):
                if a < b and world.get_diplomatic_state(a, b) in (
                        "ALLIANCE", "DEFENSIVE_ALLIANCE"):
                    diplomacy.set_diplomatic_state(world, a, b, "PEACE")
        world.active_coalition = None
        _refresh(world)

        assert coalition.form_coalition(members, world)

        for a in members:
            for b in members:
                if a < b:
                    assert world.get_diplomatic_state(a, b) != "ALLIANCE", (
                        f"{a}-{b} — if this ever starts writing ALLIANCE, the "
                        f"deny predicate's premise changes"
                    )
        assert world.get_bloc_members("Britain") == ["Britain"]


# ══════════════════════ P1 — THE INVERTED GEOMETRY ════════════════════════

class TestDenySatisfactionIsAboutProvinces:

    def test_boot_is_unchanged(self, world):
        entry = world.agendas["Britain"][0]
        assert entry["id"] == "low_countries"
        assert not agendas.entry_satisfied(world, "Britain", entry)

    def test_unallied_denier_while_a_third_power_out_masses_the_target(self, world):
        """THE P1. Britain in a bloc of one; Austria's bloc out-masses France;
        France and Holland still hold all three targets."""
        entry = world.agendas["Britain"][0]
        _unally(world, "Britain")
        _grind_france_down(world)

        hegemon, share = agendas._hegemon(world, "Britain")
        assert hegemon == "Austria" and share > 0.33, (
            "geometry precondition: a co-belligerent now reads as the hegemon"
        )
        assert {world.regions[r].controller for r in LOW_COUNTRIES} == {
            "France", "Holland"}, "targets must remain in the French camp"

        assert not agendas.entry_satisfied(world, "Britain", entry)
        assert agendas.get_agenda_resolve_delta("Britain", "France", world) == 0
        assert not agendas.agenda_separate_peace_ready("Britain", world)

    def test_a_beaten_great_power_is_still_a_great_power(self, world):
        """Guard 2's ruling, preserved: the design is the Scheldt, not
        France's overall size."""
        entry = world.agendas["Britain"][0]
        _unally(world, "Britain")
        _grind_france_down(world, count=60)
        assert not agendas.entry_satisfied(world, "Britain", entry)

    def test_own_soil_satisfies_even_while_allied_to_the_hegemon(self, world):
        """D70, fixed. A court holding its own targets is satisfied whatever
        the bloc rankings say. The alliance is the WHOLE point — without it
        this passes against the pre-fix code too."""
        entry = world.agendas["Britain"][0]
        _unally(world, "Britain")
        diplomacy.set_diplomatic_state(world, "Britain", "France", "ALLIANCE")
        for r in LOW_COUNTRIES:
            world.regions[r].controller = "Britain"
        _refresh(world)

        raw_hegemon = agendas._hegemon(world)[0]
        assert raw_hegemon is not None
        assert "Britain" in set(world.get_bloc_members(raw_hegemon)), (
            "precondition: Britain must sit INSIDE the dominant bloc — that is "
            "the geometry the old guard turned into a false negative"
        )
        assert agendas.entry_satisfied(world, "Britain", entry)

    def test_a_french_satellite_is_not_a_buffer_state(self, world):
        """The regression the fix-review caught: Holland is a MINOR on paper,
        so reading the literal controller let Napoleon's client pass as a
        neutral buffer once a co-belligerent out-massed France."""
        entry = world.agendas["Britain"][0]
        world.regions["Flanders"].controller = "Britain"   # Britain takes one
        _unally(world, "Britain")
        _grind_france_down(world)

        assert world.vassals.get("Holland"), "precondition: still a French client"
        assert world.regions["Brabant"].controller == "Holland"
        assert agendas._hegemon(world)[0] == "Austria", (
            "precondition: the RAW hegemon is now a co-belligerent"
        )
        assert not agendas.entry_satisfied(world, "Britain", entry)
        assert agendas.get_agenda_resolve_delta("Britain", "France", world) == 0
        assert not agendas.agenda_separate_peace_ready("Britain", world)

    def test_a_minor_buffer_state_satisfies(self, world):
        """§11.2's authored mirror in predicate form — deny means "not
        theirs", never "mine"."""
        entry = world.agendas["Britain"][0]
        world.vassals.pop("Holland", None)
        for r in LOW_COUNTRIES:
            world.regions[r].controller = "Holland"
        _refresh(world)
        assert agendas.entry_satisfied(world, "Britain", entry)

    def test_a_satellite_of_the_hegemon_does_not(self, world):
        """The same minor, still inside the hegemon's bloc — "London will not
        rest while the bloc holds it"."""
        entry = world.agendas["Britain"][0]
        for r in LOW_COUNTRIES:
            world.regions[r].controller = "Holland"
        _refresh(world)
        assert world.vassals.get("Holland"), "precondition: still a French client"
        assert not agendas.entry_satisfied(world, "Britain", entry)

    def test_another_great_power_never_satisfies(self, world):
        """D68's rule generalized: no OTHER great power may hold them."""
        entry = world.agendas["Britain"][0]
        for r in LOW_COUNTRIES:
            world.regions[r].controller = "Prussia"
        _refresh(world)
        assert not agendas.entry_satisfied(world, "Britain", entry)

    def test_unknown_hands_never_claim_success(self, world):
        entry = world.agendas["Britain"][0]
        for r in LOW_COUNTRIES:
            world.regions[r].controller = None
        _refresh(world)
        assert not agendas.entry_satisfied(world, "Britain", entry)

    def test_a_design_with_no_provinces_never_lands(self, world):
        assert not agendas.entry_satisfied(
            world, "Britain", {"type": "deny_regions", "regions": []})


# ═══════════════ C — A WON DESIGN STILL DEFENDS ITSELF ════════════════════

class TestSatisfiedCourtsStillEntrench:

    def _austria_holding_milan(self, world):
        entry = world.agendas["Austria"][0]
        assert entry["type"] == "acquire_regions"
        for r in entry["regions"]:
            world.regions[r].controller = "Austria"
        _refresh(world)
        return entry

    def test_the_won_design_has_no_active_view(self, world):
        entry = self._austria_holding_milan(world)
        assert agendas.entry_satisfied(world, "Austria", entry)
        view = agendas.get_active_agenda("Austria", world)
        assert view is None or view.id != entry["id"], (
            "activation is the complement of satisfaction for acquire"
        )

    def _demand(self, world, regions):
        """The term shape _proposal_territory_content actually reads, at PEACE
        so the unrelated formal-peace arm cannot supply the -8 for us."""
        diplomacy.set_diplomatic_state(world, "France", "Austria", "PEACE")
        _refresh(world)
        return agendas.agenda_acceptance_mod({
            "target_nation": "Austria",
            "proposer_nation": "France",
            "type": "ultimatum_demand",
            "demands": [{"type": "territory", "regions": list(regions)}],
        }, world)

    def test_a_demand_for_the_won_province_still_entrenches(self, world):
        entry = self._austria_holding_milan(world)
        region = entry["regions"][0]
        assert self._demand(world, [region]) == agendas.AGENDA_ACCEPT_ENTRENCH, (
            f"a demand for {region} must not be free just because Austria won it"
        )

    def test_a_demand_for_an_unrelated_province_is_still_free(self, world):
        """The discriminating negative — without it the assertion above would
        pass on any input."""
        self._austria_holding_milan(world)
        assert self._demand(world, ["Normandy"]) == 0

    def test_every_won_entry_defends_itself_not_just_the_first(self, world):
        """A court that wins its WHOLE deck: the later design's provinces must
        not fall out of the strip arm."""
        deck = world.agendas["Austria"]
        if len(deck) < 2:
            pytest.skip("needs a two-entry territorial deck")
        later = [e for e in deck[1:] if e.get("regions")]
        if not later:
            pytest.skip("no later territorial entry authored")
        for entry in deck:
            for r in entry.get("regions") or []:
                world.regions[r].controller = "Austria"
        _refresh(world)
        assert agendas.get_active_agenda("Austria", world) is None, (
            "precondition: the whole deck is won"
        )
        region = later[0]["regions"][0]
        assert self._demand(world, [region]) == agendas.AGENDA_ACCEPT_ENTRENCH, (
            f"{region} belongs to a won LATER entry and must still be defended"
        )

    def test_a_settlement_term_stripping_the_won_province_entrenches(self, world):
        entry = self._austria_holding_milan(world)
        region = entry["regions"][0]
        mod = agendas.agenda_settlement_mod("Austria", [{
            "type": "territory",
            "from_nation": "Austria",
            "to_nation": "France",
            "regions": [region],
        }], world)
        assert mod == agendas.AGENDA_ACCEPT_ENTRENCH

    def test_a_satisfied_design_is_never_ADVANCED(self, world):
        """No +12 for handing a court what it already holds."""
        entry = self._austria_holding_milan(world)
        region = entry["regions"][0]
        mod = agendas.agenda_settlement_mod("Austria", [{
            "type": "territory",
            "from_nation": "France",
            "to_nation": "Austria",
            "regions": [region],
        }], world)
        assert mod != agendas.AGENDA_ACCEPT_ADVANCE

    def test_a_deckless_court_is_untouched(self, world):
        assert agendas.agenda_acceptance_mod({
            "target_nation": "France",
            "proposer_nation": "Austria",
            "type": "peace",
            "terms": {"demand_regions": ["Milan"]},
        }, world) == 0


# ═════════════ P3 — AN ARMISTICE IS A PAUSE, NOT NEUTRALITY ═══════════════

class TestArmisticeIsBelligerency:

    def test_an_armistice_holder_is_not_a_neutral(self, world):
        assert agendas._guard_active(world, "Denmark"), "boot: Denmark is neutral"
        diplomacy.set_diplomatic_state(world, "Denmark", "Sweden", "ARMISTICE")
        _refresh(world)
        assert not agendas._guard_active(world, "Denmark"), (
            "a power that has PAUSED its war is not a neutral whose "
            "neutrality can be violated"
        )

    def test_the_war_exemption_survives_the_armistice(self, world):
        diplomacy.set_diplomatic_state(world, "Denmark", "Sweden", "ARMISTICE")
        assert agendas._belligerent(world, "Sweden", "Denmark")
        diplomacy.set_diplomatic_state(world, "Denmark", "Sweden", "WAR")
        assert agendas._belligerent(world, "Sweden", "Denmark")
        diplomacy.set_diplomatic_state(world, "Denmark", "Sweden", "PEACE")
        assert not agendas._belligerent(world, "Sweden", "Denmark")

    def test_a_true_neutral_still_guards(self, world):
        """The trap must keep its teeth — this is not a blanket disarm."""
        assert agendas._guard_active(world, "Denmark")
        assert not agendas._has_belligerency(world, "Denmark")


# ═══════════ P2 — A DEMAND OVERTAKEN BY WAR IS NOT A BARGAIN ══════════════

class TestVoidUltimatum:
    """The ultimatum dialogue is non-blocking and lapses only at the START of
    the next end_turn, so it survives arbitrary state change across the whole
    of the player's turn. Reachable with zero player action: the issuer is
    dragged into an existing war by a third party's alliance cascade."""

    ISSUER = "Prussia"

    def _deliver(self, world):
        from backend.game_logic.ai_diplomacy import (
            deliver_ai_proposal, process_diplomatic_phase,
        )
        for other in list(world.get_active_nations()):
            if other == world.player_nation:
                continue
            key = world._make_diplo_key(world.player_nation, other)
            if world.diplomatic_states.get(key) == "WAR":
                world.diplomatic_states[key] = "PEACE"
        world.invalidate_bloc_members_cache()
        world.threat_level = 0
        world.regions["Hanover"].controller = world.player_nation
        world.invalidate_active_nations_cache()
        world.nation_relations[
            world._make_diplo_key(world.player_nation, self.ISSUER)] = -20
        for m in world.marshals.values():
            if m.nation == world.player_nation:
                m.strength = 2000
            elif m.nation == self.ISSUER:
                m.strength = 40000
        proposal = process_diplomatic_phase(self.ISSUER, world)
        assert proposal, "precondition: the §8 gates must hold"
        return deliver_ai_proposal(proposal, world)

    def _executor(self):
        from backend.commands.diplomatic_executor import DiplomaticExecutor
        return DiplomaticExecutor(None)

    def test_yield_after_the_pair_falls_to_war_transfers_nothing(self, world):
        dialogue = self._deliver(world)
        region = "Hanover"
        before = world.regions[region].controller
        treaties_before = len(getattr(world, "active_treaties", []) or [])

        diplomacy.set_diplomatic_state(
            world, world.player_nation, self.ISSUER, "WAR")

        result = self._executor()._handle_accept_ai_ultimatum(dialogue, world)

        assert result["success"]
        assert "void" in result["message"].lower()
        assert "peace holds" not in result["message"].lower(), (
            "the game must never report the peace holding while at WAR"
        )
        assert world.regions[region].controller == before, "no cession"
        assert len(getattr(world, "active_treaties", []) or []) == treaties_before, (
            "no perpetual tribute treaty written for a void demand"
        )

    def test_yield_to_an_eliminated_issuer_does_not_resurrect_it(self, world):
        dialogue = self._deliver(world)
        for name, region in world.regions.items():
            if region.controller == self.ISSUER:
                region.controller = "France"
        world.invalidate_active_nations_cache()
        world.invalidate_bloc_members_cache()
        assert self.ISSUER not in world.get_active_nations()

        self._executor()._handle_accept_ai_ultimatum(dialogue, world)
        assert self.ISSUER not in world.get_active_nations(), (
            "yielding must not raise a court from the dead"
        )

    def _last_event(self, world, *types):
        for event in reversed(getattr(world, "event_log", []) or []):
            if event.get("type") in types:
                return event
        return None

    def test_defying_a_void_demand_plants_no_pressure(self, world):
        dialogue = self._deliver(world)
        before = int(getattr(world, "ultimatum_rejection_pressure", {}).get(
            self.ISSUER, 0) or 0)
        diplomacy.set_diplomatic_state(
            world, world.player_nation, self.ISSUER, "WAR")

        self._executor()._handle_reject_ai_ultimatum(dialogue, world)

        after = int(getattr(world, "ultimatum_rejection_pressure", {}).get(
            self.ISSUER, 0) or 0)
        assert after == before, (
            "a court cannot bank a grievance for a refusal that cost nothing"
        )
        # The DURABLE record must agree with the popup — the campaign log
        # must not assert the grievance the code just refused to bank.
        event = self._last_event(
            world, "ai_ultimatum_void", "ai_ultimatum_rejected")
        assert event and event["type"] == "ai_ultimatum_void", (
            f"logged {event and event['type']} — the log would read 'we defied "
            f"them, their court will not forget' for a demand that lapsed"
        )
        assert event["reason"] == "war"

    def test_the_void_yield_logs_the_lapse(self, world):
        dialogue = self._deliver(world)
        diplomacy.set_diplomatic_state(
            world, world.player_nation, self.ISSUER, "WAR")
        self._executor()._handle_accept_ai_ultimatum(dialogue, world)
        event = self._last_event(
            world, "ai_ultimatum_void", "ai_ultimatum_accepted")
        assert event and event["type"] == "ai_ultimatum_void"

    def test_the_live_arms_still_log_their_own_types(self, world):
        dialogue = self._deliver(world)
        self._executor()._handle_accept_ai_ultimatum(dialogue, world)
        event = self._last_event(
            world, "ai_ultimatum_void", "ai_ultimatum_accepted")
        assert event and event["type"] == "ai_ultimatum_accepted"

    def test_a_live_demand_is_still_honoured_normally(self, world):
        """The guard must not blunt the ordinary path."""
        dialogue = self._deliver(world)
        result = self._executor()._handle_accept_ai_ultimatum(dialogue, world)
        assert result["success"]
        assert "peace holds" in result["message"].lower()
