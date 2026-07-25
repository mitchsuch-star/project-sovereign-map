"""AI-2b — the D5 counter-instruments (Stage C).

docs/AI_INTENT_SPEC.md §6 D5 / §3.3 / §12.3 / §5 pins 8 + 23:

- Compensation buys a design OFF — it suspends at the agenda chokepoint
  and mints a standing expectation; reneging is the strongest grievance
  and a weight surge in intent (Stage D adds the casus belli).
- Directed sponsorship is ONE record for the paid form, the licence
  (amount 0 — pin 23: a licence is a bond) and sell-neutrality
  (kind="neutrality", the opposite flow).
- A guarantee deters coveters (the intent weight the ledger shows) and
  its abandonment is the enforcement `protection_promised` never had.
- All records are serialized (§5 pin 8) and both directions of every
  bond bind identically (GR5).
"""

from pathlib import Path

import pytest

from backend.commands.executor import CommandExecutor
from backend.game_logic.agendas import get_active_agenda
from backend.game_logic.instruments import (
    BUYOFF_BASE_PRICE,
    BUYOFF_PRICE_PER_WEIGHT,
    GUARANTEE_GRACE_TURNS,
    GUARANTEE_WEIGHT_DETERRENT,
    WEIGHT_RENEGED_BARGAIN,
    compute_buyoff_price,
    create_compensation_bargain,
    design_suspended,
    grant_directed_sponsorship,
    has_renege_grievance,
    pledge_guarantee,
    process_instruments,
    standing_sponsorship_amount,
)
from backend.game_logic.intent import get_nation_intent
from backend.models.world_state import WorldState

SCENARIO_PATH = (Path(__file__).resolve().parents[1] / "godot-client"
                 / "project-sovereign" / "assets" / "maps"
                 / "europe_1805.json")


@pytest.fixture(scope="module")
def world1805():
    """Read-only module-scoped 1805 campaign — mutating tests copy it."""
    return WorldState.from_scenario(str(SCENARIO_PATH))


@pytest.fixture
def world(world1805):
    return WorldState.from_dict(world1805.to_dict())


def _executor(world):
    return CommandExecutor(), {"world": world, "debug_mode": True}


def _make_war(world, aggressor, defender, *, start_turn=None):
    """An ATTRIBUTED war: the first arg is the declarer. The renege
    arms read the war_instances attackers side (`_pair_aggressor`) —
    a bare diplomatic_states write has no declarer and lapses records
    instead of branding anyone."""
    from backend.game_logic.settlement_helpers import (
        ensure_war_instance_for_pair,
    )
    result = ensure_war_instance_for_pair(world, aggressor, defender,
                                 entry_path="stage_c_test")
    if not result.get("ok"):
        # Validation refused (e.g. a standing treaty) — hand-craft the
        # minimal attributed instance the renege arms read.
        wid = f"stage_c_test_{aggressor}_{defender}"
        world.war_instances[wid] = {
            "war_id": wid, "attackers": [aggressor],
            "defenders": [defender], "ended_turn": None,
            "active_participants": [aggressor, defender],
        }
        if hasattr(world, "invalidate_war_instance_indexes"):
            world.invalidate_war_instance_indexes()
    key = world._make_diplo_key(aggressor, defender)
    world.diplomatic_states[key] = "WAR"
    world.war_start_turns[key] = (int(start_turn)
                                  if start_turn is not None
                                  else int(world.current_turn))
    world.invalidate_bloc_members_cache()


# ═══════════════════════════════════════════════════════════════════════
# The player verbs
# ═══════════════════════════════════════════════════════════════════════


class TestSponsorVerb:
    def test_sponsor_success_creates_directed_record(self, world):
        executor, gs = _executor(world)
        world.diplomatic_points = 3
        world.nation_gold["France"] = 2000
        result = executor._diplomatic._execute_sponsor_design(
            {"action": "sponsor_design", "target": "Prussia",
             "raw_input": "sponsor prussia against hanover, 150 gold"}, gs)
        assert result["success"], result["message"]
        record = world.directed_sponsorships[0]
        assert record["payer"] == "France"
        assert record["recipient"] == "Prussia"
        assert record["aim"] == "Hanover"
        assert record["amount_per_turn"] == 150
        assert record["kind"] == "sponsorship"
        assert world.diplomatic_points == 2
        assert standing_sponsorship_amount(world, "France", "Prussia") == 150

    def test_licence_verb_defaults_amount_zero(self, world):
        executor, gs = _executor(world)
        world.diplomatic_points = 3
        result = executor._diplomatic._execute_sponsor_design(
            {"action": "sponsor_design", "target": "Prussia",
             "raw_input": "license prussia against hanover"}, gs)
        assert result["success"], result["message"]
        record = world.directed_sponsorships[0]
        assert record["amount_per_turn"] == 0
        assert "licence" in result["message"].lower()
        assert "reneging" in result["message"].lower()

    def test_aim_defaults_to_the_designs_own_against(self, world):
        executor, gs = _executor(world)
        world.diplomatic_points = 3
        result = executor._diplomatic._execute_sponsor_design(
            {"action": "sponsor_design", "target": "Prussia",
             "raw_input": "sponsor prussia, 100 gold"}, gs)
        assert result["success"], result["message"]
        assert world.directed_sponsorships[0]["aim"] == "Hanover"

    def test_aim_mismatch_refused_naming_the_real_design(self, world):
        executor, gs = _executor(world)
        world.diplomatic_points = 3
        result = executor._diplomatic._execute_sponsor_design(
            {"action": "sponsor_design", "target": "Prussia",
             "raw_input": "sponsor prussia against austria, 100 gold"}, gs)
        assert not result["success"]
        assert "Hanover" in result["message"]

    def test_designless_recipient_refused_honestly(self, world):
        executor, gs = _executor(world)
        world.diplomatic_points = 3
        # Bavaria is a vassal at 1805 — indifferent (pin 18).
        result = executor._diplomatic._execute_sponsor_design(
            {"action": "sponsor_design", "target": "Bavaria",
             "raw_input": "sponsor bavaria against austria"}, gs)
        assert not result["success"]
        assert "no design" in result["message"].lower()

    def test_sponsoring_a_design_against_france_refused(self, world):
        executor, gs = _executor(world)
        world.diplomatic_points = 3
        # Sweden's design stands against France.
        result = executor._diplomatic._execute_sponsor_design(
            {"action": "sponsor_design", "target": "Sweden",
             "raw_input": "sponsor sweden, 100 gold"}, gs)
        assert not result["success"]

    def test_insufficient_dp_refused(self, world):
        executor, gs = _executor(world)
        world.diplomatic_points = 0
        result = executor._diplomatic._execute_sponsor_design(
            {"action": "sponsor_design", "target": "Prussia",
             "raw_input": "sponsor prussia, 100 gold"}, gs)
        assert not result["success"]
        assert "Diplomatic Points" in result["message"]


class TestBuyOffVerb:
    def test_buy_off_suspends_the_design_and_pays(self, world):
        executor, gs = _executor(world)
        world.diplomatic_points = 3
        view = get_nation_intent("Prussia", world)
        price = compute_buyoff_price(world, "Prussia")
        assert price == BUYOFF_BASE_PRICE + BUYOFF_PRICE_PER_WEIGHT * view.weight
        world.nation_gold["France"] = price + 500
        prussia_gold = int(world.nation_gold.get("Prussia", 0))
        result = executor._diplomatic._execute_buy_off_design(
            {"action": "buy_off_design", "target": "Prussia",
             "raw_input": "buy off prussia"}, gs)
        assert result["success"], result["message"]
        assert world.nation_gold["France"] == 500
        assert world.nation_gold["Prussia"] == prussia_gold + price
        assert design_suspended(world, "Prussia", view.want_id)
        # The agenda chokepoint skips the bought-off design (§3.1a b) —
        # Prussia's deck holds only the one design, so the court reads
        # indifferent and its ladder rung drops for free.
        after = get_nation_intent("Prussia", world)
        assert after.want_id != view.want_id
        assert world.diplomatic_points == 2

    def test_lowball_offer_refused_naming_the_price(self, world):
        executor, gs = _executor(world)
        world.diplomatic_points = 3
        price = compute_buyoff_price(world, "Prussia")
        world.nation_gold["France"] = price + 500
        result = executor._diplomatic._execute_buy_off_design(
            {"action": "buy_off_design", "target": "Prussia",
             "raw_input": "buy off prussia for 50 gold"}, gs)
        assert not result["success"]
        assert str(price) in result["message"]
        assert not world.compensation_bargains

    def test_survival_court_has_no_price(self, world):
        executor, gs = _executor(world)
        world.diplomatic_points = 3
        capital = world.get_nation_capital("Sweden")
        world.regions[capital].controller = "Russia"
        world.invalidate_active_nations_cache()
        assert get_nation_intent("Sweden", world).survival
        result = executor._diplomatic._execute_buy_off_design(
            {"action": "buy_off_design", "target": "Sweden",
             "raw_input": "buy off sweden"}, gs)
        assert not result["success"]
        assert "existence" in result["message"]

    def test_insufficient_treasury_refused(self, world):
        executor, gs = _executor(world)
        world.diplomatic_points = 3
        world.nation_gold["France"] = 10
        result = executor._diplomatic._execute_buy_off_design(
            {"action": "buy_off_design", "target": "Prussia",
             "raw_input": "buy off prussia"}, gs)
        assert not result["success"]
        assert not world.compensation_bargains


class TestGuaranteeVerb:
    def test_guarantee_success(self, world):
        executor, gs = _executor(world)
        world.diplomatic_points = 3
        result = executor._diplomatic._execute_guarantee_nation(
            {"action": "guarantee_nation", "target": "Denmark",
             "raw_input": "guarantee denmark"}, gs)
        assert result["success"], result["message"]
        assert world.diplomatic_guarantees[0]["guarantor"] == "France"
        assert world.diplomatic_guarantees[0]["protected"] == "Denmark"
        assert world.diplomatic_points == 2

    def test_duplicate_guarantee_refused(self, world):
        executor, gs = _executor(world)
        world.diplomatic_points = 3
        executor._diplomatic._execute_guarantee_nation(
            {"action": "guarantee_nation", "target": "Denmark",
             "raw_input": "guarantee denmark"}, gs)
        result = executor._diplomatic._execute_guarantee_nation(
            {"action": "guarantee_nation", "target": "Denmark",
             "raw_input": "guarantee denmark"}, gs)
        assert not result["success"]
        assert len(world.diplomatic_guarantees) == 1

    def test_guaranteeing_an_enemy_refused(self, world):
        executor, gs = _executor(world)
        world.diplomatic_points = 3
        result = executor._diplomatic._execute_guarantee_nation(
            {"action": "guarantee_nation", "target": "Austria",
             "raw_input": "guarantee austria"}, gs)
        assert not result["success"]

    def test_own_vassal_refused(self, world):
        executor, gs = _executor(world)
        world.diplomatic_points = 3
        vassal = next(
            (name for name, rec in world.vassals.items()
             if rec.get("lord") == "France"), None)
        assert vassal is not None
        result = executor._diplomatic._execute_guarantee_nation(
            {"action": "guarantee_nation", "target": vassal,
             "raw_input": f"guarantee {vassal.lower()}"}, gs)
        assert not result["success"]


# ═══════════════════════════════════════════════════════════════════════
# Intent coupling — the numbers the ledger shows
# ═══════════════════════════════════════════════════════════════════════


class TestIntentCoupling:
    def test_guarantee_deters_the_coveter(self, world):
        """Prussia (weight 59, align) drops below the align floor when a
        third party guarantees Hanover — D5-3's raised bar, shown."""
        before = get_nation_intent("Prussia", world)
        assert before.price == "align" and before.weight == 59
        pledge_guarantee(world, guarantor="Russia", protected="Hanover")
        after = get_nation_intent("Prussia", world)
        assert after.weight == before.weight - GUARANTEE_WEIGHT_DETERRENT
        assert after.price == "buy"

    def test_coveters_own_guarantee_does_not_deter_itself(self, world):
        """Prussia guaranteeing Hanover itself deters nothing — but the
        pledge's +5 relation bonus lifts Prussia|Hanover from the boot 0
        into the warm band, dropping the CHILLY +4 term: 59 → 55. The
        −8 deterrent (which would read 47) must NOT apply."""
        pledge_guarantee(world, guarantor="Prussia", protected="Hanover")
        assert get_nation_intent("Prussia", world).weight == 55

    def test_renege_surge_against_the_breaker(self, world):
        """France buys off Sweden's anti-France design then attacks
        Sweden: the design returns carrying the §3.3 surge."""
        view = get_nation_intent("Sweden", world)
        assert view.against == "France"
        create_compensation_bargain(
            world, payer="France", recipient="Sweden",
            design_id=view.want_id, granted={"gold": 500})
        assert get_nation_intent("Sweden", world).want_id != view.want_id
        _make_war(world, "France", "Sweden")
        events = process_instruments(world)
        assert any(e["type"] == "bargain_reneged" for e in events)
        assert not world.compensation_bargains
        assert has_renege_grievance(world, "Sweden", "France")
        after = get_nation_intent("Sweden", world)
        assert after.want_id == view.want_id  # the design is back
        assert after.price == "fight"         # at war with the breaker
        # The surge is visible in the weight (clamped at 100).
        assert after.weight == min(
            100, view.weight + 10 + WEIGHT_RENEGED_BARGAIN)


# ═══════════════════════════════════════════════════════════════════════
# The per-turn pass
# ═══════════════════════════════════════════════════════════════════════


class TestInstrumentPass:
    def test_sponsorship_pays_per_turn(self, world):
        grant_directed_sponsorship(
            world, payer="France", recipient="Prussia", aim="Hanover",
            amount_per_turn=200)
        world.nation_gold["France"] = 1000
        prussia = int(world.nation_gold.get("Prussia", 0))
        process_instruments(world)
        assert world.nation_gold["France"] == 800
        assert world.nation_gold["Prussia"] == prussia + 200

    def test_licence_pays_nothing_but_persists(self, world):
        grant_directed_sponsorship(
            world, payer="France", recipient="Prussia", aim="Hanover",
            amount_per_turn=0)
        world.nation_gold["France"] = 1000
        process_instruments(world)
        assert world.nation_gold["France"] == 1000
        assert len(world.directed_sponsorships) == 1

    def test_sponsorship_expires_after_exactly_its_term(self, world):
        """The term COUNTER (review fix): a 2-turn promise pays exactly
        twice — player and AI mints alike — then lapses, logged."""
        grant_directed_sponsorship(
            world, payer="France", recipient="Prussia", aim="Hanover",
            amount_per_turn=100, turns=2)
        world.nation_gold["France"] = 1000
        prussia = int(world.nation_gold.get("Prussia", 0))
        for _ in range(2):
            world.current_turn += 1
            assert not [e for e in process_instruments(world)
                        if e["type"] == "sponsorship_expired"]
        assert world.nation_gold["Prussia"] == prussia + 200  # 2 payments
        world.current_turn += 1
        events = process_instruments(world)
        assert any(e["type"] == "sponsorship_expired" for e in events)
        assert not world.directed_sponsorships
        assert world.nation_gold["Prussia"] == prussia + 200  # no 3rd
        # The lapse reaches the record (review fix: expiry was dead code
        # on every surface).
        assert any(e.get("type") == "sponsorship_expired"
                   for e in world.event_log)

    def test_pin23_licensor_entering_licensed_war_is_reneging(self, world):
        """Pin 23: amount 0 creates the same bond as a paid sponsorship —
        the payer warring its recipient is the breaker."""
        grant_directed_sponsorship(
            world, payer="France", recipient="Prussia", aim="Hanover",
            amount_per_turn=0)
        _make_war(world, "France", "Prussia")
        events = process_instruments(world)
        renege = [e for e in events if e["type"] == "sponsorship_reneged"]
        assert renege and renege[0]["breaker"] == "France"
        assert renege[0]["licence"] is True
        assert has_renege_grievance(world, "Prussia", "France")
        assert not world.directed_sponsorships

    def test_pin23_guaranteeing_the_aim_is_reneging(self, world):
        grant_directed_sponsorship(
            world, payer="France", recipient="Prussia", aim="Hanover",
            amount_per_turn=100)
        pledge_guarantee(world, guarantor="France", protected="Hanover")
        events = process_instruments(world)
        renege = [e for e in events if e["type"] == "sponsorship_reneged"]
        assert renege and renege[0]["breaker"] == "France"

    def test_pin23_both_directions_ai_payer_binds_too(self, world):
        """GR5: an AI payer holds the same bond — Prussia licensing
        France's design then warring France is Prussia reneging."""
        grant_directed_sponsorship(
            world, payer="Prussia", recipient="France", aim="Hanover",
            amount_per_turn=0)
        _make_war(world, "Prussia", "France")
        events = process_instruments(world)
        renege = [e for e in events if e["type"] == "sponsorship_reneged"]
        assert renege and renege[0]["breaker"] == "Prussia"
        assert has_renege_grievance(world, "France", "Prussia")

    def test_neutrality_binds_the_recipient(self, world):
        """Sell-neutrality: the paid party entering the war against the
        payer is the breaker — the exact inverse flow (§12.3)."""
        grant_directed_sponsorship(
            world, payer="Prussia", recipient="France", aim="Russia",
            amount_per_turn=150, kind="neutrality")
        _make_war(world, "France", "Prussia")
        events = process_instruments(world)
        renege = [e for e in events if e["type"] == "sponsorship_reneged"]
        assert renege and renege[0]["breaker"] == "France"
        assert renege[0]["kind"] == "neutrality"
        assert has_renege_grievance(world, "Prussia", "France")

    def test_bargain_renege_on_retaken_grant(self, world):
        """§3.3: the granted province is a hostage — the payer's side
        retaking it tears up the bargain."""
        region = next(iter(world.get_nation_regions("Prussia")))
        view = get_nation_intent("Prussia", world)
        create_compensation_bargain(
            world, payer="France", recipient="Prussia",
            design_id=view.want_id, granted={"region": region})
        world.regions[region].controller = "France"
        world.invalidate_active_nations_cache()
        events = process_instruments(world)
        assert any(e["type"] == "bargain_reneged" for e in events)
        assert not world.compensation_bargains

    def test_guarantee_abandoned_after_grace(self, world):
        """Attacker must be a nation France is NOT already at war with
        (France fights Russia at boot, which would read as honouring) —
        Prussia is at peace with France in 1805. Grace runs from the
        LATER of war start and the pledge (review fix), so the pledge
        must be old enough to have owed a march."""
        pledge_guarantee(world, guarantor="France", protected="Denmark")
        _make_war(world, "Prussia", "Denmark",
                  start_turn=world.current_turn)
        world.current_turn += GUARANTEE_GRACE_TURNS
        events = process_instruments(world)
        abandoned = [e for e in events
                     if e["type"] == "guarantee_abandoned"]
        assert abandoned and abandoned[0]["breaker"] == "France"
        assert not world.diplomatic_guarantees
        assert has_renege_grievance(world, "Denmark", "France")

    def test_guarantee_honored_when_guarantor_fights(self, world):
        pledge_guarantee(world, guarantor="France", protected="Denmark")
        _make_war(world, "Prussia", "Denmark",
                  start_turn=world.current_turn)
        _make_war(world, "France", "Prussia")
        world.current_turn += GUARANTEE_GRACE_TURNS
        events = process_instruments(world)
        assert not any(e["type"] == "guarantee_abandoned" for e in events)
        assert len(world.diplomatic_guarantees) == 1

    def test_guarantee_holds_inside_grace_window(self, world):
        pledge_guarantee(world, guarantor="France", protected="Denmark")
        _make_war(world, "Prussia", "Denmark",
                  start_turn=world.current_turn)
        events = process_instruments(world)
        assert not any(e["type"] == "guarantee_abandoned" for e in events)
        assert len(world.diplomatic_guarantees) == 1

    def test_mid_war_pledge_still_gets_its_grace(self, world):
        """Review fix: a guarantee pledged into an ALREADY-old war used
        to brand the guarantor one turn later — before it could ever
        march. Grace now runs from the pledge."""
        _make_war(world, "Prussia", "Denmark",
                  start_turn=world.current_turn - 5)
        pledge_guarantee(world, guarantor="France", protected="Denmark")
        events = process_instruments(world)
        assert not any(e["type"] == "guarantee_abandoned" for e in events)
        assert len(world.diplomatic_guarantees) == 1

    def test_ward_aggression_voids_without_branding(self, world):
        """Review fix: the ward declaring on its own guarantor forfeits
        the protection — the guarantee VOIDS, nobody is branded."""
        pledge_guarantee(world, guarantor="France", protected="Denmark")
        _make_war(world, "Denmark", "France")
        events = process_instruments(world)
        assert not any(e["type"] == "guarantee_abandoned" for e in events)
        lapsed = [e for e in events if e["type"] == "instrument_lapsed"]
        assert lapsed and lapsed[0]["reason"] == "ward_aggression"
        assert not world.diplomatic_guarantees
        assert not has_renege_grievance(world, "Denmark", "France")


class TestRenegeAttribution:
    """The review's headline P1: renege is an ACT ('entering the war
    later'), never a state. The AGGRESSOR of a post-mint war is the
    breaker, whoever holds which end; an unattributable or pre-existing
    war LAPSES the record and brands nobody."""

    def test_attacked_payer_is_not_the_breaker(self, world):
        """France licences Prussia; PRUSSIA then declares on France —
        Prussia (the aggressor) is the breaker, never the bound payer."""
        grant_directed_sponsorship(
            world, payer="France", recipient="Prussia", aim="Hanover",
            amount_per_turn=0)
        _make_war(world, "Prussia", "France")
        events = process_instruments(world)
        renege = [e for e in events if e["type"] == "sponsorship_reneged"]
        assert renege and renege[0]["breaker"] == "Prussia"
        assert has_renege_grievance(world, "France", "Prussia")
        assert not has_renege_grievance(world, "Prussia", "France")
        # No false player-blame popup for a war France did not start.
        assert world.proposal_result_popup is None

    def test_attacked_neutrality_recipient_is_not_the_breaker(self, world):
        """Prussia buys France's neutrality; PRUSSIA then declares on
        France — the payer-aggressor is the breaker, and the bound
        recipient (France) keeps its honour."""
        grant_directed_sponsorship(
            world, payer="Prussia", recipient="France", aim="Austria",
            amount_per_turn=150, kind="neutrality")
        _make_war(world, "Prussia", "France")
        events = process_instruments(world)
        renege = [e for e in events if e["type"] == "sponsorship_reneged"]
        assert renege and renege[0]["breaker"] == "Prussia"
        assert has_renege_grievance(world, "France", "Prussia")

    def test_bought_off_court_marching_anyway_is_the_breaker(self, world):
        """France buys off Prussia's design; PRUSSIA takes the gold and
        declares anyway — Prussia broke the bargain, not France."""
        view = get_nation_intent("Prussia", world)
        create_compensation_bargain(
            world, payer="France", recipient="Prussia",
            design_id=view.want_id, granted={"gold": 500})
        _make_war(world, "Prussia", "France")
        events = process_instruments(world)
        renege = [e for e in events if e["type"] == "bargain_reneged"]
        assert renege and renege[0]["breaker"] == "Prussia"
        assert has_renege_grievance(world, "France", "Prussia")

    def test_unattributed_war_lapses_without_a_breaker(self, world):
        """A bare state-write war (no instance, no declarer) can brand
        nobody — the record lapses on the log instead."""
        grant_directed_sponsorship(
            world, payer="France", recipient="Prussia", aim="Hanover",
            amount_per_turn=100)
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "WAR"
        world.war_start_turns[key] = int(world.current_turn)
        world.invalidate_bloc_members_cache()
        events = process_instruments(world)
        assert not any(e["type"] == "sponsorship_reneged" for e in events)
        lapsed = [e for e in events if e["type"] == "instrument_lapsed"]
        assert lapsed and lapsed[0]["reason"] == "war_unattributed"
        assert not world.directed_sponsorships
        assert not has_renege_grievance(world, "Prussia", "France")
        assert not has_renege_grievance(world, "France", "Prussia")

    def test_bargain_term_serves_and_the_design_wakes(self, world):
        """§3.3's asymmetry made finite (review balance fix): the bought
        design SLEEPS for the term, then wakes quietly."""
        from backend.game_logic.instruments import COMPENSATION_TERM_TURNS
        view = get_nation_intent("Prussia", world)
        create_compensation_bargain(
            world, payer="France", recipient="Prussia",
            design_id=view.want_id, granted={"gold": 500})
        assert get_nation_intent("Prussia", world).want_id != view.want_id
        world.current_turn += COMPENSATION_TERM_TURNS
        events = process_instruments(world)
        lapsed = [e for e in events if e["type"] == "instrument_lapsed"]
        assert lapsed and lapsed[0]["reason"] == "term_served"
        assert not world.compensation_bargains
        assert get_nation_intent("Prussia", world).want_id == view.want_id


class TestMintGates:
    """Review fix: the mint refuses honestly what the pass would brand —
    the guarantee verb's own idiom, applied to its siblings."""

    def test_buy_off_refused_at_war(self, world):
        executor, gs = _executor(world)
        world.diplomatic_points = 3
        world.nation_gold["France"] = 99999
        result = executor._diplomatic._execute_buy_off_design(
            {"action": "buy_off_design", "target": "Austria",
             "raw_input": "buy off austria"}, gs)
        assert not result["success"]
        assert "WAR" in result["message"]
        assert not world.compensation_bargains
        assert world.diplomatic_points == 3  # nothing charged

    def test_sponsor_refused_at_war_with_recipient(self, world):
        executor, gs = _executor(world)
        world.diplomatic_points = 3
        result = executor._diplomatic._execute_sponsor_design(
            {"action": "sponsor_design", "target": "Austria",
             "raw_input": "sponsor austria against prussia"}, gs)
        assert not result["success"]
        assert "WAR" in result["message"]

    def test_sponsor_refused_against_a_guaranteed_ward(self, world):
        executor, gs = _executor(world)
        world.diplomatic_points = 3
        pledge_guarantee(world, guarantor="France", protected="Hanover")
        result = executor._diplomatic._execute_sponsor_design(
            {"action": "sponsor_design", "target": "Prussia",
             "raw_input": "sponsor prussia against hanover, 100 gold"}, gs)
        assert not result["success"]
        assert "GUARANTEES" in result["message"]

    def test_duplicate_licence_is_not_a_relation_pump(self, world):
        """Review fix: one live record per (kind, payer, recipient,
        aim) — the second identical cast refuses, charges nothing,
        moves no relation."""
        executor, gs = _executor(world)
        world.diplomatic_points = 5
        first = executor._diplomatic._execute_sponsor_design(
            {"action": "sponsor_design", "target": "Prussia",
             "raw_input": "license prussia against hanover"}, gs)
        assert first["success"]
        relation_after_first = world.nation_relations.get(
            world._make_diplo_key("France", "Prussia"), 0)
        second = executor._diplomatic._execute_sponsor_design(
            {"action": "sponsor_design", "target": "Prussia",
             "raw_input": "license prussia against hanover"}, gs)
        assert not second["success"]
        assert len(world.directed_sponsorships) == 1
        assert world.diplomatic_points == 4  # only the first cast paid
        assert world.nation_relations.get(
            world._make_diplo_key("France", "Prussia"), 0) == (
            relation_after_first)

    def test_unsustainable_promise_refused(self, world):
        """Review fix (the paper bid): the player's standing promise is
        held to the AI's own sustain bar (four turns' cover)."""
        executor, gs = _executor(world)
        world.diplomatic_points = 3
        world.nation_gold["France"] = 500
        result = executor._diplomatic._execute_sponsor_design(
            {"action": "sponsor_design", "target": "Prussia",
             "raw_input": "sponsor prussia against hanover, 400 gold"}, gs)
        assert not result["success"]
        assert "SUSTAIN" in result["message"]


# ═══════════════════════════════════════════════════════════════════════
# Beat 4 — The Broken Bargain
# ═══════════════════════════════════════════════════════════════════════


class TestBeat4:
    def test_player_breaker_gets_the_cold_envoy_popup(self, world):
        view = get_nation_intent("Prussia", world)
        create_compensation_bargain(
            world, payer="France", recipient="Prussia",
            design_id=view.want_id, granted={"gold": 500})
        _make_war(world, "France", "Prussia")
        process_instruments(world)
        popup = world.proposal_result_popup
        assert popup is not None
        assert popup["proposal_type"] == "The Broken Bargain"
        assert popup["target_nation"] == "Prussia"
        # The Voice Bible register: a NAMED envoy speaks the reproach.
        assert "Hardenberg" in popup["message"]

    def test_ai_breaker_no_popup_but_the_mark_stands(self, world):
        grant_directed_sponsorship(
            world, payer="Prussia", recipient="France", aim="Hanover",
            amount_per_turn=0)
        _make_war(world, "Prussia", "France")
        process_instruments(world)
        assert world.proposal_result_popup is None
        assert has_renege_grievance(world, "France", "Prussia")

    def test_renege_event_reaches_the_campaign_log(self, world):
        from backend.campaign_log import filter_campaign_log
        view = get_nation_intent("Prussia", world)
        create_compensation_bargain(
            world, payer="France", recipient="Prussia",
            design_id=view.want_id, granted={"gold": 500})
        _make_war(world, "France", "Prussia")
        process_instruments(world)
        visible = filter_campaign_log(world.event_log, world)
        assert any(e.get("type") == "bargain_reneged" for e in visible)


# ═══════════════════════════════════════════════════════════════════════
# Serialization (§5 pin 8)
# ═══════════════════════════════════════════════════════════════════════


class TestSerialization:
    def test_all_three_stores_round_trip(self, world):
        grant_directed_sponsorship(
            world, payer="France", recipient="Prussia", aim="Hanover",
            amount_per_turn=100)
        view = get_nation_intent("Sweden", world)
        create_compensation_bargain(
            world, payer="France", recipient="Sweden",
            design_id=view.want_id, granted={"gold": 400})
        pledge_guarantee(world, guarantor="France", protected="Denmark")
        restored = WorldState.from_dict(world.to_dict())
        assert restored.directed_sponsorships == world.directed_sponsorships
        assert restored.compensation_bargains == world.compensation_bargains
        assert restored.diplomatic_guarantees == world.diplomatic_guarantees
        # The suspension survives the load — pin 8's point.
        assert design_suspended(restored, "Sweden", view.want_id)

    def test_pre_stage_c_save_reads_empty(self, world):
        data = world.to_dict()
        data.pop("directed_sponsorships")
        data.pop("compensation_bargains")
        data.pop("diplomatic_guarantees")
        restored = WorldState.from_dict(data)
        assert restored.directed_sponsorships == []
        assert restored.compensation_bargains == []
        assert restored.diplomatic_guarantees == []


class TestSubsidyContest:
    """AI-2e (§3.7): Britain is an auction, not a wall — the subsidy is
    visible, contestable (the outbid rides AI-2b's directed record),
    and its client can be bought away."""

    def _coalition(self, world):
        world.active_coalition = {
            "name": "The Third Coalition",
            "leader": "Austria",
            "members": ["Britain", "Austria", "Russia"],
            "target_nation": "France",
            "posture": "defensive",
            "formed_turn": 1,
        }
        world.nation_gold["Britain"] = 5000
        world.invalidate_bloc_members_cache()
        from backend.game_logic.agendas import get_paymaster_nation
        assert get_paymaster_nation(world) == "Britain"

    def test_boot_recipient_without_records(self, world):
        from backend.game_logic.coalition import (
            get_british_subsidy_recipient,
        )
        self._coalition(world)
        recipient = get_british_subsidy_recipient(world)
        assert recipient in ("Austria", "Russia")

    def test_french_sponsorship_outbids_the_subsidy(self, world):
        from backend.game_logic.agendas import get_paymaster_subsidy_amount
        from backend.game_logic.coalition import (
            get_british_subsidy_recipient,
        )
        self._coalition(world)
        first = get_british_subsidy_recipient(world)
        subsidy = get_paymaster_subsidy_amount(world, "Britain")
        grant_directed_sponsorship(
            world, payer="France", recipient=first, aim="Britain",
            amount_per_turn=subsidy)
        second = get_british_subsidy_recipient(world)
        assert second != first  # the client is outbid — next in line

    def test_underbid_does_not_move_the_client(self, world):
        from backend.game_logic.agendas import get_paymaster_subsidy_amount
        from backend.game_logic.coalition import (
            get_british_subsidy_recipient,
        )
        self._coalition(world)
        first = get_british_subsidy_recipient(world)
        subsidy = get_paymaster_subsidy_amount(world, "Britain")
        grant_directed_sponsorship(
            world, payer="France", recipient=first, aim="Britain",
            amount_per_turn=max(0, subsidy - 50))
        assert get_british_subsidy_recipient(world) == first

    def test_bought_off_client_is_not_worth_funding(self, world):
        from backend.game_logic.coalition import (
            get_british_subsidy_recipient,
        )
        self._coalition(world)
        first = get_british_subsidy_recipient(world)
        create_compensation_bargain(
            world, payer="France", recipient=first,
            design_id="any_design", granted={"gold": 500})
        assert get_british_subsidy_recipient(world) != first

    def test_subsidy_payment_reaches_the_campaign_log(self, world):
        from backend.game_logic.coalition import _process_british_subsidy
        self._coalition(world)
        events = _process_british_subsidy(world)
        assert events and events[0]["type"] == "british_subsidy"
        logged = [e for e in world.event_log
                  if e.get("type") == "british_subsidy"]
        assert logged and logged[0]["payer"] == "Britain"

    def test_subsidy_payload_names_payer_client_and_counterplay(
            self, world):
        from backend.game_logic.instruments import build_subsidy_payload
        assert build_subsidy_payload(world) is None  # no coalition
        self._coalition(world)
        payload = build_subsidy_payload(world)
        assert payload is not None
        assert payload["payer"] == "Britain"
        assert payload["amount"] > 0
        assert "outbids" in payload["counterplay"]

    def test_ledger_carries_both_surfaces(self, world):
        from backend.game_logic.diplomatic_ledger import (
            build_diplomatic_ledger,
        )
        self._coalition(world)
        grant_directed_sponsorship(
            world, payer="France", recipient="Prussia", aim="Hanover",
            amount_per_turn=100)
        ledger = build_diplomatic_ledger(world)
        assert ledger["balance_of_europe"]["paymaster_subsidy"] is not None
        prussia_row = next(n for n in ledger["nations"]
                           if n["name"] == "Prussia")
        assert prussia_row["compacts"] is not None
        assert "sponsors" in prussia_row["compacts"]
        # A court party to nothing omits the row (renderers skip null).
        quiet_row = next(n for n in ledger["nations"]
                         if n["name"] == "Denmark")
        assert quiet_row["compacts"] is None


class TestInstrumentsLine:
    def test_composes_every_family(self, world):
        from backend.game_logic.instruments import build_instruments_line
        grant_directed_sponsorship(
            world, payer="France", recipient="Prussia", aim="Hanover",
            amount_per_turn=0)
        pledge_guarantee(world, guarantor="France", protected="Prussia")
        line = build_instruments_line(world, "Prussia")
        assert "licences" in line
        assert "guarantees" in line

    def test_none_for_uninvolved_court(self, world):
        from backend.game_logic.instruments import build_instruments_line
        assert build_instruments_line(world, "Denmark") is None


class TestDecklessNeutral:
    def test_bare_world_verbs_refuse_gracefully(self):
        world = WorldState(player_nation="France")
        world.diplomatic_points = 3
        executor, gs = _executor(world)
        result = executor._diplomatic._execute_buy_off_design(
            {"action": "buy_off_design", "target": "Austria",
             "raw_input": "buy off austria"}, gs)
        assert not result["success"]
        result = executor._diplomatic._execute_sponsor_design(
            {"action": "sponsor_design", "target": "Austria",
             "raw_input": "sponsor austria against prussia"}, gs)
        assert not result["success"]

    def test_empty_stores_are_a_noop_pass(self):
        world = WorldState(player_nation="France")
        assert process_instruments(world) == []
