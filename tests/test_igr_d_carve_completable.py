"""IGR-D — "the carve becomes completable".

`docs/INGAME_REVIEW_FIXES_SPEC.md` §2 IGR-D, gate record §5 Q2.

The July-25 in-game review reached every prerequisite for the NA-6c carve by
real play — at war with Prussia, Posen held and secured, the eligibility gate
green, the clause authored — and neither route completed. The JOINT settlement
needed all four courts at 50; the BILATERAL route the game itself offers
("Make peace with {target} only") dropped identity clauses by design. The
Proclamation card had never once been sighted in-client.

Gate Q2 answered it as a SPLIT:

  (a) `create_client` CARRIES into the pair-substitute bilateral peace. That
      is Tilsit — the Duchy of Warsaw was carved out of Prussia ALONE while
      the British war ran — so a separate peace is the canonical instance of
      the clause, not an edge case.
  (b) every OTHER identity clause (vassalage / liberation / forced_alliance)
      stays settlement-tier, and the bilateral peace is DISABLED with a
      stated reason rather than silently throwing the drafting away.

The G4F-15 ruling stands untouched: a truce never erects a client state.
"""

import os
import pathlib

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent

SCENARIO = "godot-client/project-sovereign/assets/maps/europe_1805.json"


def _europe_world():
    """The shipped 1805 campaign, with France at war with Prussia and Posen
    taken — the exact board the review reached by play."""
    os.environ.setdefault("LLM_MODE", "mock")
    from backend.game_logic.diplomacy import declare_war
    from backend.models.world_state import WorldState

    world = WorldState.from_scenario(SCENARIO)
    declare_war(world, "France", "Prussia")
    world.regions["Posen"].controller = "France"
    world.invalidate_active_nations_cache()
    return world


def _beaten_prussia():
    """A court that has actually been BEATEN — the DoD's precondition.

    Its field army is destroyed and its provinces are held. The army has to
    be GONE rather than merely weakened: a proposal spends a full turn in
    transit, and a Prussian corps still on the board retakes Posen during
    that tick, at which point the carve honestly refuses with
    `carve_provinces_not_held`. That refusal is correct behaviour and it is
    what a fixture with a merely-bruised Prussia was really testing."""
    from backend.game_logic.diplomacy import set_diplomatic_state

    world = _europe_world()
    for name in [m.name for m in world.marshals.values()
                 if m.nation == "Prussia"]:
        del world.marshals[name]
    # And the war is with Prussia ALONE — the Tilsit shape. Left at boot,
    # France is also at war with Russia, whose marshal walks into Posen
    # during the transit turn and takes the soil out from under the carve.
    for nation in list(world.get_active_nations()):
        if nation in ("France", "Prussia"):
            continue
        if world.get_diplomatic_state("France", nation) == "WAR":
            set_diplomatic_state(world, "France", nation, "PEACE", "fixture")
    for name in ("Posen", "Berlin", "Silesia"):
        if name in world.regions:
            world.regions[name].controller = "France"
    world.invalidate_active_nations_cache()
    world.war_scores[world._make_diplo_key("France", "Prussia")] = 100
    world.nation_gold["France"] = 20000
    return world


def _carve_demand(count=1):
    return {
        "type": "create_client",
        "value": count,
        "tag": "DuchyOfWarsaw",
        "provinces": ["Posen"],
        "client_display_name": "Duchy of Warsaw",
    }


def _proposal_dialogue(terms):
    """The shape `_enrich_proposal_summary` reads terms out of."""
    return {"prompt": "", "options": [
        {"action": "execute_proposal", "terms": terms}]}


def _carve_term(to_nation="France"):
    return {
        "type": "create_client",
        "from": "Prussia",
        "to": to_nation,
        "tag": "DuchyOfWarsaw",
        "provinces": ["Posen"],
        "client_display_name": "Duchy of Warsaw",
    }


# ══════════════════════════════════════════════════════════════════════
# ARM A.1 — the carry-over translator
# ══════════════════════════════════════════════════════════════════════

class TestTheCarveTravels:

    def test_create_client_is_seeded_as_a_demand(self):
        from backend.game_logic.settlement_actions import (
            _pair_substitute_seed_terms,
        )
        seed = _pair_substitute_seed_terms(
            [_carve_term()], target="Prussia", proposer_leader="France",
        )
        carves = [d for d in seed["demands"]
                  if d.get("type") == "create_client"]
        assert len(carves) == 1, seed
        assert carves[0]["tag"] == "DuchyOfWarsaw"
        assert carves[0]["provinces"] == ["Posen"]
        assert carves[0]["client_display_name"] == "Duchy of Warsaw"

    def test_it_rides_demands_not_sweeteners_or_clauses(self):
        """Load-bearing. `_ratify_treaty` builds its clause list from
        `sweeteners` + `demands` ONLY — `proposal["clauses"]` is read once,
        as a bare `"open_borders" in ...` string test. A carve seeded into
        `clauses` would price, annotate, warn about estates, ratify into the
        treaty record and then apply NOTHING, reproducing this slice's own
        defect one layer down. It is also what makes G4F-15 free."""
        from backend.game_logic.settlement_actions import (
            _pair_substitute_seed_terms,
        )
        seed = _pair_substitute_seed_terms(
            [_carve_term()], target="Prussia", proposer_leader="France",
        )
        assert any(d.get("type") == "create_client"
                   for d in seed["demands"]), (
            "the carve must be IN demands — the only list _ratify_treaty "
            "converts. Asserting only its absence elsewhere passes with the "
            "whole seed change reverted."
        )
        assert not any(s.get("type") == "create_client"
                       for s in seed["sweeteners"])
        assert "clauses" not in seed

    def test_the_province_count_rides_the_value(self):
        """The bilateral acceptance walk multiplies by `value`, so a
        two-province template must cost more than a one-province one."""
        from backend.game_logic.settlement_actions import (
            _pair_substitute_seed_terms,
        )
        term = dict(_carve_term(), provinces=["Posen", "Silesia"])
        seed = _pair_substitute_seed_terms(
            [term], target="Prussia", proposer_leader="France",
        )
        assert seed["demands"][0]["value"] == 2

    def test_an_ally_beneficiary_carve_does_not_travel(self):
        """`create_client` is carver-parameterised (GR5), so a joint draft
        may carry a carve an ALLY makes out of this same court. The demand
        builder derives direction from which list a term sat in, so carrying
        it would silently re-stamp FRANCE as the carver and erect someone
        else's client on France's authority."""
        from backend.game_logic.settlement_actions import (
            _pair_substitute_seed_terms,
        )
        seed = _pair_substitute_seed_terms(
            [_carve_term(to_nation="Austria")],
            target="Prussia", proposer_leader="France",
        )
        assert seed["demands"] == []

    def test_another_courts_carve_does_not_travel(self):
        from backend.game_logic.settlement_actions import (
            _pair_substitute_seed_terms,
        )
        term = dict(_carve_term(), **{"from": "Austria"})
        seed = _pair_substitute_seed_terms(
            [term], target="Prussia", proposer_leader="France",
        )
        assert seed["demands"] == []

    def test_the_carried_set_and_the_seed_agree(self):
        from backend.game_logic.settlement_staging import (
            PAIR_SUBSTITUTE_CARRIED_TYPES,
        )
        assert "create_client" in PAIR_SUBSTITUTE_CARRIED_TYPES

    def test_the_dropped_labels_no_longer_claim_the_carve(self):
        """`create_client` carries, so naming it as left behind would be a
        new lie. The other six rows stay live for arm (b)."""
        from backend.game_logic.settlement_staging import (
            _PAIR_SUBSTITUTE_DROPPED_LABELS,
        )
        assert "create_client" not in _PAIR_SUBSTITUTE_DROPPED_LABELS
        assert "vassalage" in _PAIR_SUBSTITUTE_DROPPED_LABELS


class TestG4F15StandsUntouched:
    """"A truce that erects a client state is not a truce." The armistice
    arm empties `seed["demands"]` wholesale, so seeding the carve as a
    DEMAND satisfies the ruling by construction — this pins that it stays
    that way rather than being satisfied by accident."""

    def test_the_armistice_arm_drops_the_carve(self):
        """Executes the PRODUCTION guard. A hand-rolled `dict(seed,
        demands=[])` and then asserting nothing is in `[]` is a tautology
        that stays green with the real guard disabled."""
        import inspect

        from backend.game_logic import settlement_actions
        from backend.game_logic.settlement_actions import (
            _pair_substitute_seed_terms,
        )
        seed = _pair_substitute_seed_terms(
            [_carve_term()], target="Prussia", proposer_leader="France",
        )
        assert seed["demands"], "precondition: the peace arm carries it"
        # The guard lives inside `_execute_pair_substitute_handoff`; pin the
        # real source of it, and that it keys off the armistice arm.
        body = inspect.getsource(
            settlement_actions._execute_pair_substitute_handoff)
        guard = 'if proposal_type == "armistice" and seed["demands"]:'
        assert guard in body, (
            "the G4F-15 armistice guard was removed or reshaped: " + guard
        )
        assert 'seed = dict(seed, demands=[])' in body


# ══════════════════════════════════════════════════════════════════════
# ARM A.2 — the bilateral apply seam
# ══════════════════════════════════════════════════════════════════════

class TestTheBilateralRouteCarves:

    def _ratify(self, world, demands=None):
        return world._ratify_treaty({
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [],
            "demands": demands if demands is not None else [_carve_demand()],
        })

    def test_the_subject_survives_the_demand_to_clause_conversion(self):
        """The extras allowlist strips every key it does not name. Without
        `tag` the clause arrives with nothing to carve."""
        world = _europe_world()
        self._ratify(world)
        treaty = world.active_treaties[
            world._make_diplo_key("France", "Prussia")]
        carve = next(c for c in treaty["clauses"]
                     if c.get("type") == "create_client")
        assert carve["tag"] == "DuchyOfWarsaw"
        assert carve["provinces"] == ["Posen"]
        assert carve["client_display_name"] == "Duchy of Warsaw"
        # Direction: a DEMAND becomes from=target, to=proposer.
        assert carve["from"] == "Prussia"
        assert carve["to"] == "France"

    def test_the_nation_is_minted(self):
        world = _europe_world()
        self._ratify(world)
        assert "DuchyOfWarsaw" in world.get_active_nations()
        assert world.regions["Posen"].controller == "DuchyOfWarsaw"
        assert world.vassals["DuchyOfWarsaw"]["lord"] == "France"
        assert world.vassals["DuchyOfWarsaw"]["carved_from"] == "Prussia"

    def test_the_proclamation_fires(self):
        """`create_client_nation` announces inline — the poll skips vassals
        and a carved client is a vassal from birth, so a route that waited
        for `process_formations` would wait forever."""
        world = _europe_world()
        self._ratify(world)
        card = world.nation_proclamation_popup
        assert card is not None
        assert card["display_name"] == "Duchy of Warsaw"
        assert card["subtitle"] == "By your hand."
        # Nothing died to make this nation.
        assert card["old_display_name"] == ""

    def test_the_ratification_summary_names_the_client(self):
        """`terms_ratified` is annotated from the proposal, reconciled
        against `applied_treaty_clauses` — see the refused-carve test below,
        which is the half that can actually fail."""
        world = _europe_world()
        event = self._ratify(world)
        summary = event["peace_ratification_summary"]
        joined = " ".join(summary["terms_ratified"])
        assert "Duchy of Warsaw" in joined, summary["terms_ratified"]
        assert "DuchyOfWarsaw" not in joined, "raw template id leaked"

    def test_a_carve_only_peace_is_not_a_white_peace(self):
        """France dismembers Prussia into a client state; the campaign log
        recorded that nothing happened."""
        world = _europe_world()
        event = self._ratify(world)
        assert event["peace_ratification_summary"]["war_outcome"] != "white_peace"

    def test_the_carve_is_not_reported_as_territory_gained(self):
        """The soil goes to the NEW nation, not to France. The outcome must
        count it as material without inflating France's gains."""
        world = _europe_world()
        event = self._ratify(world)
        summary = event["peace_ratification_summary"]
        assert "Posen" not in summary["territory_gained"]

    def test_eligibility_is_enforced_on_the_new_route(self):
        """The settlement route validates at authoring AND on every restage;
        the bilateral route has neither, and a full turn passes in transit.
        Here the carver does not hold the soil."""
        world = _europe_world()
        world.regions["Posen"].controller = "Prussia"
        world.invalidate_active_nations_cache()
        self._ratify(world)
        assert "DuchyOfWarsaw" not in world.get_active_nations()
        assert world.regions["Posen"].controller == "Prussia"

    def test_the_predicate_refuses_what_the_live_re_read_would_allow(self):
        """Isolates the NEW eligibility call from the live control re-check
        that `apply_create_client_clause` already performed. France HOLDS
        Rome here, so `cc_held` passes and the shared helper would mint --
        but Rome's starting controller is the Papacy, not Prussia, so
        `carve_not_defeated_soil` must refuse. Without this, deleting the
        eligibility call from `_ratify_treaty` left the suite green while
        the bilateral route silently lost the defeated-soil rule and the
        total-annexation floor that the settlement route enforces."""
        world = _beaten_prussia()
        world.regions["Rome"].controller = "France"
        world.invalidate_active_nations_cache()
        # Precondition: the shared apply body alone WOULD mint it.
        from backend.game_logic.formations import apply_create_client_clause
        from backend.game_logic.settlement_validation import (
            evaluate_create_client_eligibility,
        )
        war = next(w for w in world.war_instances.values()
                   if w.get("ended_turn") is None)
        assert not evaluate_create_client_eligibility(
            world, war_instance=war, template_id="RomanRepublic",
            from_court="Prussia", carver="France",
        )["eligible"], "precondition: the predicate must refuse this"
        probe = world.__class__.from_scenario(SCENARIO)
        probe.regions["Rome"].controller = "France"
        probe.invalidate_active_nations_cache()
        assert apply_create_client_clause(probe, {
            "type": "create_client", "from": "Prussia", "to": "France",
            "tag": "RomanRepublic",
        }) is not None, (
            "precondition: the live re-read alone does NOT refuse this, so "
            "the eligibility call is the only thing that can"
        )
        # Now the real route must refuse it.
        world._ratify_treaty({
            "type": "peace", "proposer_nation": "France",
            "target_nation": "Prussia", "sweeteners": [],
            "demands": [{"type": "create_client", "value": 1,
                         "tag": "RomanRepublic", "provinces": ["Rome"],
                         "client_display_name": "Roman Republic"}],
        })
        assert "RomanRepublic" not in world.get_active_nations()

    def test_soil_that_was_never_the_courts_cannot_be_carved(self):
        """`carve_not_defeated_soil` — the predicate's own rule, reached
        through the bilateral route rather than re-implemented beside it."""
        world = _europe_world()
        event = world._ratify_treaty({
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [],
            # Rome is Papal soil; Prussia may not be made to yield it.
            "demands": [{"type": "create_client", "value": 1,
                         "tag": "RomanRepublic", "provinces": ["Rome"],
                         "client_display_name": "Roman Republic"}],
        })
        assert event is not None
        assert "RomanRepublic" not in world.get_active_nations()

    def test_both_routes_apply_through_one_body(self):
        """The elimination gate, the live re-read and the already-active-tag
        refusal are the whole NA-6c §20.1 review. A second hand-written arm
        on the bilateral route would have had to re-earn every one of them,
        so both routes call `formations.apply_create_client_clause`."""
        import inspect

        from backend.game_logic import formations, settlement_ratify
        from backend.models import world_state

        assert hasattr(formations, "apply_create_client_clause")
        assert "apply_create_client_clause" in inspect.getsource(
            settlement_ratify._apply_settlement_terms)
        assert "apply_create_client_clause" in inspect.getsource(
            world_state.WorldState._ratify_treaty)
        # And the guard that stops the duplicate elimination announcement
        # lives in the shared body, not in either caller.
        body = inspect.getsource(formations.apply_create_client_clause)
        assert "cc_prior_controllers" in body
        assert "_eliminate_nation" in body

    def test_an_already_landless_court_is_not_re_announced(self):
        """Eligibility requires the CARVER to hold every template province,
        so by the time a carve applies the court is usually already landless
        and `capture_region` has already eliminated it. An ungated re-check
        fired a second, duplicate announcement — the §20.1 defect, now
        inherited correctly by the bilateral route."""
        world = _europe_world()
        for name, region in world.regions.items():
            if region.controller == "Prussia":
                region.controller = "France"
        world.invalidate_active_nations_cache()
        # Without a decisive score the total-annexation gate refuses the
        # carve BEFORE the elimination guard is ever reached, so the event
        # count is trivially unchanged and the guard is unpinned.
        world.war_scores[world._make_diplo_key("France", "Prussia")] = 95
        before = [e for e in world.event_log
                  if e.get("type") == "nation_eliminated"]
        self._ratify(world)
        after = [e for e in world.event_log
                 if e.get("type") == "nation_eliminated"]
        assert "DuchyOfWarsaw" in world.get_active_nations(), (
            "precondition failed: the carve never applied, so the "
            "elimination guard was never reached"
        )
        assert len(after) == len(before), (
            "a court this clause never took soil from was announced again"
        )


class TestTheProclamationReachesTheClient:
    """The deliverable. The card is stashed on the world, not returned in
    the result dict, and the bilateral route resolves inside `advance_turn`
    — the response that also carries `enemy_phase`. Pinned against the REAL
    endpoint because §17.1 already recorded one P1 where a response rebuild
    discarded an already-popped popup, and the formation latch is permanent:
    a delivery bug is unrecoverable for that campaign."""

    def test_end_turn_response_carries_the_card(self):
        """Drives the REAL `POST /command` end-turn route. The acceptance
        seam is patched to ACCEPT — the documented idiom in this repo — so
        the subject is DELIVERY, not the formula (which
        `TestTheCarveIsPriced` owns). Without the patch the AI's verdict is
        recomputed at resolve time against a board a fixture cannot hold
        still: `recalculate_war_scores` re-derives every score from live
        battle records each tick, so a hand-set war score is gone by the
        time the proposal lands."""
        from unittest.mock import patch

        from fastapi.testclient import TestClient

        import backend.main as main_module
        from backend.main import app

        world = _beaten_prussia()
        world.proposal_in_transit = {
            "target": "Prussia",
            "turn_sent": world.current_turn - 1,
            "diplomatic_state_at_send": "WAR",
            "proposal": {
                "type": "peace",
                "proposer_nation": "France",
                "target_nation": "Prussia",
                "sweeteners": [{"type": "gold_lump", "value": 6000}],
                "demands": [_carve_demand()],
            },
        }
        # BOTH handles: `main.py` keeps a module-level `world` alongside
        # `game_state["world"]`, the executor reads the dict and the
        # RESPONSE layers read the global. Setting only the dict runs the
        # command on this world and then builds the response from another.
        original_world = main_module.world
        original_state = dict(main_module.game_state)
        main_module._set_active_world(world)
        try:
            with patch(
                "backend.game_logic.diplomacy.calculate_acceptance",
                return_value={"score": 95, "outcome": "ACCEPT",
                              "feedback": "", "components": {}},
            ), patch(
                # An independent veto with its own coverage: the coalition
                # will not leave French vassals standing while a liberation
                # objective is live. Not this test's subject.
                "backend.game_logic.ai_diplomacy."
                "ai_should_accept_liberation_peace",
                return_value=True,
            ):
                client = TestClient(app)
                response = client.post(
                    "/command", json={"command": "end turn"})
            assert response.status_code == 200
            body = response.json()
            assert "DuchyOfWarsaw" in world.get_active_nations(), (
                "the carve never applied on the end-turn route"
            )
            card = body.get("nation_proclamation")
            assert card is not None, (
                "the Proclamation never reached the client — must-see #4. "
                "The card is stashed on the world by `_announce`, so a "
                "response rebuild that drops it is silent and permanent."
            )
            assert card["display_name"] == "Duchy of Warsaw"
            assert card["subtitle"] == "By your hand."
        finally:
            # Restore UNCONDITIONALLY. Guarding on `is not None` left this
            # test's world installed globally whenever main.py had not yet
            # booted one, and a leaked world changes later tests in the
            # file -- measured: the counter-offer regression test stopped
            # catching its own mutation once this test had run.
            main_module.world = original_world
            main_module.game_state.clear()
            main_module.game_state.update(original_state)


# ══════════════════════════════════════════════════════════════════════
# ARM A.3 — the AI must be able to judge it, and must not quietly re-draft
# ══════════════════════════════════════════════════════════════════════

class TestTheCarveIsPriced:

    def _score(self, world, demands):
        from backend.game_logic.diplomacy import calculate_acceptance
        return calculate_acceptance({
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [],
            "demands": demands,
        }, world)["score"]

    def test_adding_a_carve_to_an_already_harsh_package_costs_something(self):
        """THE defect. A carve's whole cost used to come from
        `harshness_penalty`, which SATURATES (harshness clamps at 1.0, the
        penalty caps at -40) — so against any realistic Tilsit package
        (indemnity + a cession + the carve) the AI's yes/no was provably
        independent of whether it was being dismembered. Measured on master:
        adding one carve, or two, or three, moved the score by exactly 0."""
        world = _europe_world()
        harsh = [{"type": "gold_lump", "value": 3000},
                 {"type": "territory_cede", "value": 2,
                  "regions": ["Posen", "Silesia"]}]
        before = self._score(world, harsh)
        after = self._score(world, harsh + [_carve_demand()])
        # Measured on master: 0. The magnitude is deliberately modest —
        # `harshness_penalty` still owns the carve's real cost — but it must
        # never be nothing.
        assert after <= before - 5, (
            f"the carve is nearly free on a harsh package: "
            f"{before} -> {after}"
        )

    def test_the_carve_is_reachable_for_a_victor_and_not_for_a_marginal_win(self):
        """The falsifiable acceptance shape, so the blessed number can be
        judged rather than argued. MEASURED on the shipped 1805 board with
        Prussia's army broken and a 6,000g sweetener, against the bar of 50:
        a victor holding ALL of Prussia carves; one holding only Posen does
        not. If the first ever fails, the price is too high and the marquee
        clause is unreachable on the route this slice opened; if the second
        ever passes, a state can be dismembered on a skirmish."""
        world_all = _europe_world()
        world_one = _europe_world()
        from backend.game_logic.diplomacy import recalculate_war_scores
        for world, hold_all in ((world_all, True), (world_one, False)):
            for marshal in list(world.marshals.values()):
                if marshal.nation == "Prussia":
                    marshal.strength = 2000
                    marshal.morale = 20
            if hold_all:
                for region in world.regions.values():
                    if region.controller == "Prussia":
                        region.controller = "France"
            world.invalidate_active_nations_cache()
            recalculate_war_scores(world)

        def carve_score(world):
            from backend.game_logic.diplomacy import calculate_acceptance
            return calculate_acceptance({
                "type": "peace",
                "proposer_nation": "France",
                "target_nation": "Prussia",
                "sweeteners": [{"type": "gold_lump", "value": 6000}],
                "demands": [_carve_demand()],
            }, world)["score"]

        assert carve_score(world_all) >= 50, (
            "a victor who holds the whole kingdom cannot carve a client "
            "out of it — the clause is priced out of its own route"
        )
        assert carve_score(world_one) < 50, (
            "a single captured province is enough to dismember a state"
        )

    def test_a_bigger_carve_costs_strictly_more(self):
        world = _europe_world()
        one = self._score(world, [_carve_demand()])
        three = self._score(world, [{
            "type": "create_client", "value": 3, "tag": "DuchyOfWarsaw",
            "provinces": ["Posen", "Silesia", "EastPrussia"],
        }])
        assert three < one

    def test_the_walk_not_the_table_carries_the_value(self):
        """A bare `DEMAND_VALUES` row would be a NO-OP: the generic branches
        multiply by `value`, and the number is derived from the harshness
        dialect (x50 for identity clauses) rather than invented."""
        from backend.game_logic.diplomacy import (
            CREATE_CLIENT_DEMAND_ERECTION,
            CREATE_CLIENT_DEMAND_PER_PROVINCE,
            DEMAND_VALUES,
        )
        from backend.game_logic.diplomatic_templates import (
            _accumulate_raw_treaty_harshness,
        )
        assert "create_client" in DEMAND_VALUES
        # The erection premium is half a province, mirroring the ratio the
        # harshness dialect already uses for this clause (0.3n + 0.15).
        assert CREATE_CLIENT_DEMAND_ERECTION == pytest.approx(
            CREATE_CLIENT_DEMAND_PER_PROVINCE / 2)
        # And the per-province rate is the table's own territory rate.
        assert CREATE_CLIENT_DEMAND_PER_PROVINCE == float(
            DEMAND_VALUES["territory_cede"])
        assert _accumulate_raw_treaty_harshness(
            {"demands": [_carve_demand()]}) > 0
        # THE BINDING PART: the constants are only decoration unless the
        # WALK reads them. Measure the score with the charge zeroed — the
        # registry row alone is a no-op, because the generic branches
        # multiply by `value`, so nothing else would catch its deletion.
        import backend.game_logic.diplomacy as D
        world = _europe_world()
        proposal = {
            "type": "peace", "proposer_nation": "France",
            "target_nation": "Prussia", "sweeteners": [],
            "demands": [_carve_demand()],
        }
        charged = D.calculate_acceptance(
            proposal, world)["components"]["deal_balance"]
        saved = (D.CREATE_CLIENT_DEMAND_PER_PROVINCE,
                 D.CREATE_CLIENT_DEMAND_ERECTION)
        try:
            D.CREATE_CLIENT_DEMAND_PER_PROVINCE = 0.0
            D.CREATE_CLIENT_DEMAND_ERECTION = 0.0
            free = D.calculate_acceptance(
                proposal, world)["components"]["deal_balance"]
        finally:
            (D.CREATE_CLIENT_DEMAND_PER_PROVINCE,
             D.CREATE_CLIENT_DEMAND_ERECTION) = saved
        assert charged < free, (
            "the walk branch does not read the constants — the carve is "
            f"free on deal_balance ({charged} vs {free})"
        )
        assert charged == pytest.approx(
            free + CREATE_CLIENT_DEMAND_PER_PROVINCE
            + CREATE_CLIENT_DEMAND_ERECTION)

    def test_talleyrand_does_not_call_a_dismemberment_generous(self):
        """The THIRD harshness dialect. Unscored, a carve-only peace read
        0.0, fell into the "< 0.3 = too generous" arm, and on a defiance
        roll got a perpetual 50g/turn tribute bolted on that the player
        never authored — silently lowering the acceptance they were shown."""
        from backend.commands.diplomatic_defiance import (
            calculate_proposal_harshness,
        )
        harshness = calculate_proposal_harshness(
            {"type": "peace", "demands": [_carve_demand()], "sweeteners": []})
        assert harshness >= 0.3, harshness


class TestTheCounterOfferDoesNotAmputateTheCarve:
    """`generate_counter_offer` deep-copies the PLAYER's own proposal and
    deletes whichever single element raises acceptance most. A carve is by
    construction the most expensive line in any package, so it was struck
    every time — and the counter's summary never said so. The player would
    accept a peace they believed erected the Duchy of Warsaw and receive a
    gold treaty."""

    def test_a_counter_never_silently_drops_the_client_state(self):
        from backend.game_logic.ai_diplomacy import generate_counter_offer

        world = _beaten_prussia()
        # The AI must be able to AFFORD a counter, or `generate_counter_offer`
        # returns None before it reaches the strike loop and the test asserts
        # nothing at all — which is exactly what the first cut of this test
        # did, leaving the headline fix with zero coverage.
        world.nation_dp = {"Prussia": 5}
        proposal = {
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            # Tuned into the 30-49 counter band, so a counter is really built.
            "sweeteners": [{"type": "gold_lump", "value": 2000}],
            "demands": [_carve_demand(), {"type": "gold_lump", "value": 300}],
        }
        counter = generate_counter_offer(proposal, world)
        assert counter is not None, (
            "precondition failed: no counter was generated, so this test "
            "would assert nothing"
        )
        types = [d.get("type") for d in counter.get("demands", [])]
        assert "create_client" in types, (
            f"the counter kept the gold and deleted the nation: {types}"
        )

    def test_the_exemption_is_still_in_the_strike_loop(self):
        """A source pin beside the behavioural one. The live assertion above
        is order-sensitive -- measured: it catches the guard's deletion when
        run alone but not after the end-turn E2E test in this same file, so
        on its own it would let the fix be deleted silently in a full run.
        This pin cannot be fooled by ambient state."""
        import inspect

        from backend.game_logic import ai_diplomacy
        body = inspect.getsource(ai_diplomacy.generate_counter_offer)
        demand_loop = body[body.index("for i, d in enumerate("):]
        assert 'if d.get("type") == "create_client":' in demand_loop, (
            "the counter-offer strike loop no longer exempts the carve"
        )
        guard = demand_loop[demand_loop.index(
            'if d.get("type") == "create_client":'):]
        assert "continue" in guard.split("test_terms")[0], (
            "the exemption no longer skips the clause"
        )


# ══════════════════════════════════════════════════════════════════════
# ARM A.4 — ES-7: a new territory route is a new place to lose the warning
# ══════════════════════════════════════════════════════════════════════

class TestTheEstateWarningSurvivesTheNewRoute:

    def _endow(self, world):
        """Give Ney an estate on the province the carve will take."""
        marshal = world.get_marshal("Ney")
        marshal.dotation_regions = ["Posen"]
        return marshal

    def test_a_carve_warns_that_it_strips_the_estate(self):
        from backend.game_logic.diplomatic_dialogue import (
            _enrich_proposal_summary,
        )
        world = _europe_world()
        self._endow(world)
        dialogue = _enrich_proposal_summary(
            _proposal_dialogue({
                "type": "peace", "sweeteners": [], "clauses": [],
                "demands": [_carve_demand()]}),
            "Prussia", "peace", world,
        )
        text = " ".join(dialogue.get("proposal_terms_summary", []))
        assert "Posen" in text and "Ney" in text, text

    def test_a_territory_demand_does_not_warn(self):
        """Scope guard. A `territory_cede` DEMAND acquires land — warning on
        it would tell the player that TAKING a province strips his marshal's
        estate. The demands pass is deliberately create_client-only."""
        from backend.game_logic.diplomatic_dialogue import (
            _enrich_proposal_summary,
        )
        world = _europe_world()
        self._endow(world)
        dialogue = _enrich_proposal_summary(
            _proposal_dialogue({
                "type": "peace", "sweeteners": [], "clauses": [],
                "demands": [{"type": "territory_cede", "value": 1,
                             "regions": ["Posen"]}]}),
            "Prussia", "peace", world,
        )
        text = " ".join(dialogue.get("proposal_terms_summary", []))
        assert "strips his estate" not in text, text

    def test_an_ordinary_cession_still_warns(self):
        """The pre-existing behaviour the extractor swap must not lose."""
        from backend.game_logic.diplomatic_dialogue import (
            _enrich_proposal_summary,
        )
        world = _europe_world()
        self._endow(world)
        dialogue = _enrich_proposal_summary(
            _proposal_dialogue({
                "type": "peace", "clauses": [], "demands": [],
                "sweeteners": [{"type": "territory_cede", "value": 1,
                                "regions": ["Posen"]}]}),
            "Prussia", "peace", world,
        )
        text = " ".join(dialogue.get("proposal_terms_summary", []))
        assert "Ney" in text, text


class TestTheClientIsNamedNotTagged:

    def test_the_confirm_line_names_the_client_and_its_soil(self):
        from backend.display_names import format_terms_for_display
        lines = format_terms_for_display(
            {"type": "peace", "demands": [_carve_demand()], "sweeteners": []},
            "peace", "Prussia",
        )
        joined = " ".join(lines)
        assert "Duchy of Warsaw" in joined, lines
        assert "Posen" in joined, lines
        assert "DuchyOfWarsaw" not in joined, "raw template id leaked"


# ══════════════════════════════════════════════════════════════════════
# ARM B — the settlement-tier clauses disable the route with their reason
# ══════════════════════════════════════════════════════════════════════

class TestSettlementTierClauseDisablesTheBilateralRoute:

    def test_vassalage_blocks_with_a_reason(self):
        from backend.game_logic.settlement_staging import (
            pair_substitute_settlement_tier_block,
        )
        reason = pair_substitute_settlement_tier_block(
            [{"type": "vassalage", "from": "Prussia", "to": "France"}],
            target="Prussia",
        )
        assert reason
        assert "vassalage" in reason
        assert "joint settlement" in reason

    def test_liberation_and_forced_alliance_block_too(self):
        from backend.game_logic.settlement_staging import (
            pair_substitute_settlement_tier_block,
        )
        for term in (
            {"type": "liberation", "from": "Prussia", "to": "France"},
            {"type": "forced_alliance", "from": "Prussia", "to": "France"},
            {"type": "vassal_transfer", "from": "Prussia", "to": "France"},
        ):
            assert pair_substitute_settlement_tier_block(
                [term], target="Prussia"), term

    def test_the_carve_does_not_block(self):
        """The split. Q2(a) and Q2(b) read the SAME carried-types set, so
        the two halves can never drift into blocking what now travels."""
        from backend.game_logic.settlement_staging import (
            pair_substitute_settlement_tier_block,
        )
        assert pair_substitute_settlement_tier_block(
            [_carve_term()], target="Prussia") == ""

    def test_money_and_territory_do_not_block(self):
        from backend.game_logic.settlement_staging import (
            pair_substitute_settlement_tier_block,
        )
        assert pair_substitute_settlement_tier_block(
            [{"type": "gold_indemnity", "from": "Prussia", "to": "France",
              "amount": 300},
             {"type": "territory_cede", "from": "Prussia", "to": "France",
              "region": "Posen"}],
            target="Prussia") == ""

    def test_another_courts_clause_does_not_block_this_pair(self):
        from backend.game_logic.settlement_staging import (
            pair_substitute_settlement_tier_block,
        )
        assert pair_substitute_settlement_tier_block(
            [{"type": "vassalage", "from": "Austria", "to": "France"}],
            target="Prussia") == ""

    def test_no_identity_clause_is_ever_dropped_silently(self):
        """The gate's own words. Every settlement-tier identity clause must
        either travel or produce a stated reason — never vanish."""
        from backend.game_logic.settlement_actions import (
            _pair_substitute_seed_terms,
        )
        from backend.game_logic.settlement_staging import (
            _PAIR_SUBSTITUTE_DROPPED_LABELS,
            pair_substitute_settlement_tier_block,
        )
        for ttype in _PAIR_SUBSTITUTE_DROPPED_LABELS:
            term = {"type": ttype, "from": "Prussia", "to": "France"}
            seed = _pair_substitute_seed_terms(
                [term], target="Prussia", proposer_leader="France")
            travelled = any(d.get("type") == ttype for d in seed["demands"])
            blocked = bool(pair_substitute_settlement_tier_block(
                [term], target="Prussia"))
            assert travelled or blocked, (
                f"{ttype} neither travels nor states a reason — it is "
                f"silently dropped, which is the whole defect"
            )


class TestTheDisabledOptionKeepsItsShape:
    """Behavioural, not a source scrape. The earlier version of this class
    only ran `inspect.getsource(...)` substring checks, which stay green if
    the block is moved behind a condition that never fires — or if the
    option is HIDDEN instead of disabled, the exact SC-29 policy violation
    the class is named for."""

    def _blocked_dialogue(self, terms):
        """A genuinely blocked REVIEW, staged through the production entry
        point with the draft in place — `build_settlement_confirm_dialogue`
        reads its terms from the PREVIEW it is handed, so injecting them
        into a dialogue afterwards never reaches the gate at all."""
        from backend.game_logic.settlement_staging import (
            stage_settlement_confirm,
        )
        from backend.models.world_state import WorldState
        from tests.helpers.full_europe_settlement_fixtures import (
            make_synthetic_war_instance,
        )

        world = WorldState()
        war = make_synthetic_war_instance(
            "war_1", attackers=["France"], defenders=["Austria", "Prussia"],
            attacker_leader="France", defender_leader="Austria",
            created_turn=1, created_sequence=1,
        )
        world.war_instances["war_1"] = war
        for pair in war["active_diplo_keys"]:
            a, _ = pair.split("|")
            world.diplomatic_states[pair] = "WAR"
            world.war_scores[pair] = 80 if a != "France" else -80
        world.invalidate_war_instance_indexes()
        staged = stage_settlement_confirm(
            world, war_id="war_1",
            covered_enemy_participants=["Austria", "Prussia"],
            selected_target_nation="Austria",
            settlement_terms=terms,
        )
        return staged["diplomatic_dialogue"]

    def _by_action(self, dialogue):
        return {o.get("action"): o for o in dialogue.get("options", [])}

    def test_a_clean_draft_leaves_the_peace_substitute_available(self):
        """The control. Without it, a test that only checks the disabled
        case passes on a build where the option never appears at all."""
        options = self._by_action(self._blocked_dialogue(None))
        assert "seek_bilateral_peace" in options
        assert options["seek_bilateral_peace"].get("available") is not False

    def test_vassalage_disables_the_peace_substitute_with_its_reason(self):
        options = self._by_action(self._blocked_dialogue(
            [{"type": "vassalage", "from": "Austria", "to": "France"}]))
        # DISABLED, never hidden — fixtures elsewhere index options[] by
        # action and would raise rather than fail.
        assert "seek_bilateral_peace" in options, "the row was HIDDEN"
        row = options["seek_bilateral_peace"]
        assert row.get("available") is False
        reason = str(row.get("disabled_reason_display") or "")
        assert "vassalage" in reason, reason
        assert "joint settlement" in reason, reason

    def test_the_armistice_substitute_stays_available(self):
        """G4F-15 already governs the truce, and disabling it too would
        leave a blocked player no exit at all."""
        options = self._by_action(self._blocked_dialogue(
            [{"type": "vassalage", "from": "Austria", "to": "France"}]))
        assert options.get("seek_armistice_instead", {}).get(
            "available") is not False

    def test_a_carve_does_not_disable_it(self):
        options = self._by_action(self._blocked_dialogue([{
            "type": "create_client", "from": "Austria", "to": "France",
            "tag": "RomanRepublic", "provinces": ["Rome"],
        }]))
        assert options["seek_bilateral_peace"].get("available") is not False


class TestTheCarryPromiseIsHonestOnEveryArm:
    """Three producers said "your drafted terms carry": the backend
    description (fixed July 25), the chooser's `.gd` BODY, and Talleyrand's
    voice line. Only the first was honest, so the promise the review caught
    was still being made in body text."""

    def test_the_dialogue_ships_the_honest_line_for_the_client_to_render(self):
        from backend.game_logic.settlement_staging import (
            _build_pair_substitute_confirm_dialogue,
        )
        dialogue = _build_pair_substitute_confirm_dialogue(
            {"settlement_terms": [
                {"type": "vassalage", "from": "Prussia", "to": "France"}],
             "war_id": "w1", "war_label": "the war"},
            action="seek_bilateral_peace",
            proposal_type="peace",
            selected_target="Prussia",
            eligibility={"eligible": True},
        )
        assert "vassalage" in dialogue["carry_line"]

    def test_the_armistice_arm_stops_promising_a_carry(self):
        from backend.game_logic.settlement_staging import (
            _build_pair_substitute_confirm_dialogue,
        )
        dialogue = _build_pair_substitute_confirm_dialogue(
            {"settlement_terms": [
                {"type": "gold_indemnity", "from": "Prussia",
                 "to": "France", "amount": 300}],
             "war_id": "w1", "war_label": "the war"},
            action="seek_armistice_instead",
            proposal_type="armistice",
            selected_target="Prussia",
            eligibility={"eligible": True},
        )
        line = dialogue["carry_line"]
        assert "carry into the talks." not in line, line
        assert "demand" in line.lower(), line

    def test_the_client_renders_the_backend_line(self):
        path = (REPO_ROOT / "godot-client" / "project-sovereign"
                / "scripts" / "proposal_confirm_popup.gd")
        with open(path, encoding="utf-8") as handle:
            source = handle.read()
        body = source[source.index("_build_pair_substitute_confirm_content"):]
        body = body[:body.index("func _build_settlement_scope_replace_content")]
        assert 'data.get("carry_line"' in body
        assert 'Your drafted terms for %s carry into the talks.[/color]' \
            not in body, "the unconditional promise is still hardcoded"

    def test_talleyrand_no_longer_guarantees_the_carry(self):
        from backend.game_logic.diplomatic_templates import (
            SETTLEMENT_VOICE_TEMPLATES,
        )
        line = SETTLEMENT_VOICE_TEMPLATES[
            "settlement_pair_substitute_confirm_talleyrand"]
        assert "travel with me" not in line


# ══════════════════════════════════════════════════════════════════════
# THE PAYOFF — a carve must be worth making
# ══════════════════════════════════════════════════════════════════════

class TestThePostLandingReviewFixes:
    """The find->refute review of `32ff834`. Every one of these was
    reproduced by hand before the fix was written."""

    def test_a_refused_carve_is_not_reported_as_ratified(self):
        """THE headline. `terms_ratified` was annotated from the SUBMITTED
        proposal, so a carve the eligibility gate correctly refused at
        ratification -- the ordinary case, since a full turn passes in
        transit and an enemy corps can retake the soil -- still told the
        player "France erects Duchy of Warsaw (Posen) out of Prussia" over a
        treaty that erected nothing. The exact silent lie this slice exists
        to kill, one surface downstream of the one it fixed."""
        world = _beaten_prussia()
        world.regions["Posen"].controller = "Prussia"   # lost in transit
        world.invalidate_active_nations_cache()
        event = world._ratify_treaty({
            "type": "peace", "proposer_nation": "France",
            "target_nation": "Prussia", "sweeteners": [],
            "demands": [_carve_demand()],
        })
        assert "DuchyOfWarsaw" not in world.get_active_nations()
        summary = event["peace_ratification_summary"]
        joined = " ".join(summary["terms_ratified"])
        assert "Warsaw" not in joined, (
            "reported as ratified when nothing was erected: " + joined
        )
        # And it is NAMED, not merely omitted -- the player must be able to
        # understand why the nation they drafted is not on the map.
        aftermath = " ".join(summary["political_aftermath"])
        assert "Duchy of Warsaw" in aftermath, aftermath
        assert "could not be erected" in aftermath, aftermath

    def test_a_successful_carve_is_still_reported(self):
        """The control: the reconciliation must not silence the happy
        path."""
        world = _beaten_prussia()
        event = world._ratify_treaty({
            "type": "peace", "proposer_nation": "France",
            "target_nation": "Prussia", "sweeteners": [],
            "demands": [_carve_demand()],
        })
        assert "DuchyOfWarsaw" in world.get_active_nations()
        joined = " ".join(
            event["peace_ratification_summary"]["terms_ratified"])
        assert "Duchy of Warsaw" in joined

    def test_subjugation_no_longer_vanishes_in_silence(self):
        """`subjugation` was in NEITHER the carried set nor the dropped
        labels, so the bilateral route threw it away without a word -- and
        the guard test could not see it, because it iterated the very dict
        the type was missing from."""
        from backend.game_logic.settlement_actions import (
            _pair_substitute_seed_terms,
        )
        from backend.game_logic.settlement_staging import (
            pair_substitute_settlement_tier_block,
        )
        term = {"type": "subjugation", "from": "Prussia", "to": "France"}
        assert not _pair_substitute_seed_terms(
            [term], target="Prussia", proposer_leader="France")["demands"]
        reason = pair_substitute_settlement_tier_block(
            [term], target="Prussia")
        assert "subjugation" in reason, reason

    def test_no_authorable_identity_clause_vanishes_in_silence(self):
        """The non-circular version of the guard. It walks the clause types
        the SETTLEMENT AUTHORING surface can actually put on a court --
        `settlement_actions._DEMAND_ADDABLE_CLAUSE_TYPES` -- instead of the
        label dict, which cannot report a type it is missing."""
        from backend.game_logic.settlement_actions import (
            _DEMAND_ADDABLE_CLAUSE_TYPES,
            _pair_substitute_seed_terms,
        )
        from backend.game_logic.settlement_staging import (
            pair_substitute_settlement_tier_block,
        )
        for ttype in _DEMAND_ADDABLE_CLAUSE_TYPES:
            term = {"type": ttype, "from": "Prussia", "to": "France",
                    "tag": "DuchyOfWarsaw", "provinces": ["Posen"],
                    "vassal_nation": "Saxony", "lord_nation": "Prussia",
                    "amount": 100, "turns": 3, "region": "Posen",
                    "vassal": "Saxony"}
            travels = bool(_pair_substitute_seed_terms(
                [term], target="Prussia",
                proposer_leader="France")["demands"])
            blocked = bool(pair_substitute_settlement_tier_block(
                [term], target="Prussia", proposer_leader="France"))
            assert travels or blocked, (
                repr(ttype) + " neither travels nor states a reason -- it is "
                "silently dropped, which is the whole defect"
            )

    def test_an_ally_beneficiary_carve_is_named_not_silently_dropped(self):
        """IGR-D moved `create_client` into the carried set and deleted its
        dropped-label row -- but the seed only carries a carve whose CARVER
        is the proposer, so an ally-beneficiary carve became the one clause
        dropped in total silence while the chooser promised a clean carry."""
        from backend.game_logic.settlement_staging import (
            _pair_substitute_carry_description,
            pair_substitute_settlement_tier_block,
        )
        ally = [{"type": "create_client", "from": "Prussia", "to": "Austria",
                 "tag": "DuchyOfWarsaw", "provinces": ["Posen"]}]
        assert pair_substitute_settlement_tier_block(
            ally, target="Prussia", proposer_leader="France")
        text = _pair_substitute_carry_description(
            {"settlement_terms": ally,
             "staged_leaders": {"attackers": "France"},
             "proposer_side": "attackers"}, "Prussia", "peace")
        assert "another power" in text, text

    def test_the_armistice_arm_names_what_it_abandons(self):
        """The early return skipped the `dropped` computation, so a truce
        named nothing it was giving up -- and arm B funnels a blocked player
        onto exactly that arm."""
        from backend.game_logic.settlement_staging import (
            _pair_substitute_carry_description,
        )
        text = _pair_substitute_carry_description(
            {"settlement_terms": [
                {"type": "vassalage", "from": "Prussia", "to": "France"}]},
            "Prussia", "armistice")
        assert "assalage" in text, text
        assert "joint settlement" in text, text

    def test_talleyrand_cannot_call_a_dismemberment_generous(self):
        """The carve's own 0.35 was dragged back under the 0.3 bar by the
        unconditional -0.1 per sweetener -- on the slice's OWN blessed
        reachability package (carve + the 6,000g the price requires), which
        then got an unauthored 50g/turn tribute bolted onto it."""
        from backend.commands.diplomatic_defiance import (
            TOO_GENEROUS_HARSHNESS,
            calculate_proposal_harshness,
        )
        blessed = {"type": "peace", "demands": [_carve_demand()],
                   "sweeteners": [{"type": "gold_lump", "value": 6000}]}
        assert calculate_proposal_harshness(
            blessed) >= TOO_GENEROUS_HARSHNESS
        # ...without making every generous peace look harsh.
        plain = {"type": "peace", "demands": [],
                 "sweeteners": [{"type": "gold_lump", "value": 6000}]}
        assert calculate_proposal_harshness(plain) < TOO_GENEROUS_HARSHNESS


class TestTheCarveIsWorthMaking:
    """Measured on master before IGR-D: the client was born at loyalty 30,
    five points BELOW the disaffected line, so it refused every call to arms
    from its first turn, was immediately bribe-eligible, and — with nothing
    offsetting the -2 satellite drift and no France<->client relation seeded
    at all — fell to open rebellion against its own creator in fifteen
    turns. Talleyrand's pitch for the clause promises "a friend that costs
    us nothing to garrison."
    """

    def _carve(self):
        from backend.game_logic.formations import create_client_nation
        world = _europe_world()
        create_client_nation(
            world, "DuchyOfWarsaw", "France", ceded_from="Prussia")
        return world

    def test_the_client_is_born_loyal_enough_to_fight(self):
        from backend.game_logic.vassal import (
            CONTRIBUTION_LOYAL_MIN,
            vassal_military_contribution,
        )
        world = self._carve()
        assert world.vassals["DuchyOfWarsaw"]["loyalty"] >= CONTRIBUTION_LOYAL_MIN
        assert vassal_military_contribution(world, "DuchyOfWarsaw") == "loyal"

    def test_the_client_is_not_bribable_on_the_day_it_is_born(self):
        from backend.game_logic.vassal import BRIBE_ELIGIBLE_LOYALTY
        world = self._carve()
        assert world.vassals["DuchyOfWarsaw"]["loyalty"] > BRIBE_ELIGIBLE_LOYALTY

    def test_the_patron_bond_is_seeded(self):
        from backend.game_logic.formations import CARVE_PATRON_RELATION
        world = self._carve()
        key = world._make_diplo_key("DuchyOfWarsaw", "France")
        assert world.nation_relations.get(key) == CARVE_PATRON_RELATION

    def test_it_does_not_drain_to_rebellion(self):
        """The bond offsets the satellite drift exactly, so a well-treated
        client is STABLE rather than a countdown — and still slides the
        moment relations sour."""
        from backend.game_logic.vassal import (
            forecast_vassal_loyalty,
            process_vassal_loyalty,
        )
        world = self._carve()
        assert forecast_vassal_loyalty(
            world, "France", "DuchyOfWarsaw")["forecast"] >= 0
        start = world.vassals["DuchyOfWarsaw"]["loyalty"]
        for _ in range(12):
            world.current_turn += 1
            process_vassal_loyalty(world)
        assert "DuchyOfWarsaw" in world.vassals, "the client rebelled"
        assert world.vassals["DuchyOfWarsaw"]["loyalty"] >= start

    def test_a_soured_patron_still_loses_the_client(self):
        """Stable, not free. The payoff uses the drift system's own lever
        rather than exempting the carve from it."""
        from backend.game_logic.vassal import forecast_vassal_loyalty
        world = self._carve()
        world.nation_relations[
            world._make_diplo_key("DuchyOfWarsaw", "France")] = -40
        assert forecast_vassal_loyalty(
            world, "France", "DuchyOfWarsaw")["forecast"] < 0

    def test_a_recarve_cannot_launder_spent_relations(self):
        from backend.game_logic.formations import create_client_nation
        world = self._carve()
        key = world._make_diplo_key("DuchyOfWarsaw", "France")
        world.nation_relations[key] = -50
        del world.vassals["DuchyOfWarsaw"]
        world.regions["Posen"].controller = "France"
        if "DuchyOfWarsaw" in world.enemy_nations:
            world.enemy_nations.remove("DuchyOfWarsaw")
        world.invalidate_active_nations_cache()
        create_client_nation(
            world, "DuchyOfWarsaw", "France", ceded_from="Prussia")
        assert world.nation_relations[key] == -50

    def test_the_proclamation_states_the_bargain(self):
        world = self._carve()
        terms = " ".join(world.nation_proclamation_popup["terms"])
        assert "tribute" in terms
        assert "marches" in terms

    def test_the_poland_chain_is_still_visible_and_still_honest(self):
        """The user's "it can eventually become Poland" — the watcher must
        show the dream AND state that vassalage blocks it, so the payoff is
        legible without becoming a promise the poll cannot keep."""
        from backend.game_logic.formations import get_formation_watch
        world = self._carve()
        watch = get_formation_watch(world, "DuchyOfWarsaw")
        assert watch is not None
        assert watch["forms"] == "Poland"
        assert watch["blocked_by_vassalage"] is True
