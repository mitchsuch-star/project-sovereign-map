"""S14k "The Courts Take the Field" — part 1: armies, benches and the ceiling;
part 2: the courts' goals and the Porte's New Order.

The user, October 28, 2026: "they should get armies or the ability to make
them, we want the game dynamic". Nine courts booted with no marshal and no
bench, so they could never raise an army whatever their gold; three more
(Denmark, Naples, the Ottomans) had one general and no bench; and the force
limit's one floor let a court of one province arm toward 94,000 men.
`SYSTEMS_REFERENCE.md` §160; the seams `tests/_oct27_seams.py::S14K_SEAMS_BY_ROW`.

K1 the 1805 field corps (Saxony's observation corps, Portugal's army);
K2 a bench for every court that fought in the period (+ the save backfill);
K3 a menaced court calls up its first general (armed neutrality);
K4 a satellite fights its lord's war by its contingent;
K5 the force limit reads the court's tier.

Part 2 (the user: "it should be possible for underdog stories, see EU4:
generally the same but some runs are surprising"; "what if ottomans
reformed"):
G1 the courts' goals — Saxony's Wettin Crown, Hesse's Westphalian Duchy, the
   neutral postures of Portugal, Hanover and Switzerland, Denmark's Scania and
   the Porte's Black Sea Shore behind their neutrality;
G2 Saxony's and Hesse's courts read sleepier than the ladder's default, so a
   moment wakes the design and the clock does not;
G3 the Porte's one-law deck, the New Order (a `force_limit` clause to a great
   power's floor; proclaimed by the AI only at war or called to arms).
"""
import copy
import json
from pathlib import Path

import pytest

from backend.game_logic import recruitment as R
from backend.game_logic import reforms as RF
from backend.game_logic import statecraft as SC
from backend.game_logic.diplomacy import set_diplomatic_state
from backend.game_logic.intent import IntentView, get_nation_intent, rung_index
from backend.game_logic.ledger import _build_economy
from backend.modding.validator import validate_scenario
from backend.models import world_state as WS
from backend.models.world_state import WorldState, severe_band_threshold
from tests._oct27_seams import S14K_SEAMS_BY_ROW, hold_down

SCENARIO = (Path(__file__).resolve().parents[1] / "godot-client" / "project-sovereign"
            / "assets" / "maps" / "europe_1805.json")

BENCHES = {
    "Portugal": ["Silveira"],
    "Saxony": ["LeCoq"],
    "Hesse": ["Emil"],
    "Hanover": ["Wallmoden", "Alten"],
    "Holland": ["Janssens"],
    "KingdomOfItaly": ["Fontanelli"],
    "Switzerland": ["Wattenwyl", "Bachmann"],
    "Denmark": ["ChristianAugust"],
    "Naples": ["Philippsthal"],
    "Ottoman": ["Alemdar", "YusufZiya"],
}


@pytest.fixture
def world():
    return WorldState.from_scenario(str(SCENARIO))


def _view(nation, against, price):
    return IntentView(nation=nation, want_id="test_design", want_title="Test",
                      want_type="acquire_regions", against=against, weight=75,
                      price=price)


class TestK1TheFieldCorps:
    def test_saxony_and_portugal_boot_armed(self, world):
        zez = world.marshals["Zezschwitz"]
        assert (zez.nation, zez.location, zez.strength, zez.personality) == \
            ("Saxony", "Dresden", 15000, "cautious")
        freire = world.marshals["BernardimFreire"]
        assert (freire.nation, freire.location, freire.strength, freire.personality) == \
            ("Portugal", "Lisbon", 12000, "cautious")

    def test_each_armed_court_boots_solvent(self, world):
        assert _build_economy(world, "Saxony")["net"] == 180
        assert _build_economy(world, "Portugal")["net"] == 654

    def test_the_corps_stand_down_with_the_seam(self, monkeypatch):
        hold_down(monkeypatch, S14K_SEAMS_BY_ROW["K1"])
        world = WorldState.from_scenario(str(SCENARIO))
        assert "Zezschwitz" not in world.marshals
        assert "BernardimFreire" not in world.marshals
        assert len(world.marshals) == 22


class TestK2TheBenches:
    def test_every_court_that_fought_has_a_bench(self, world):
        for nation, names in BENCHES.items():
            assert [c["name"] for c in world.marshal_pool[nation]] == names, nation

    def test_sardinia_and_the_papal_states_keep_their_garrisons_only(self, world):
        """GR9, said plainly: neither court fielded an army in the period
        (about 4,000 island regulars; Rome taken without a fight in 1808)."""
        for nation in ("Sardinia", "PapalStates"):
            assert nation not in world.marshal_pool
            assert not [m for m in world.marshals.values() if m.nation == nation]
            capital = world.regions[world.get_nation_capital(nation)]
            assert capital.garrison_strength == 10000

    def test_no_bench_name_sits_a_contingent_list(self, world):
        benched = {c["name"] for rows in world.marshal_pool.values() for c in rows}
        contingents = {c["name"] for rows in world.contingent_commanders.values() for c in rows}
        assert not benched & contingents
        assert {"Thielmann", "Gomes Freire"} <= contingents  # Saxony's and Portugal's stay

    def test_the_benches_stand_down_with_the_seam(self, monkeypatch):
        hold_down(monkeypatch, S14K_SEAMS_BY_ROW["K2"])
        world = WorldState.from_scenario(str(SCENARIO))
        assert set(world.marshal_pool) == {"France", "Austria", "Russia", "Prussia",
                                           "Britain", "Spain", "Sweden", "Bavaria"}

    def test_a_save_from_before_gains_the_benches(self, world):
        from backend.save_manager import _backfill_court_benches
        for nation in BENCHES:
            world.marshal_pool.pop(nation, None)
        world.marshal_pool["Hanover"] = []   # a bench the save already emptied
        _backfill_court_benches(world)
        assert world.marshal_pool["Hanover"] == []
        assert [c["name"] for c in world.marshal_pool["Ottoman"]] == ["Alemdar", "YusufZiya"]
        assert [c["name"] for c in world.marshal_pool["Portugal"]] == ["Silveira"]


class TestK3TheCourtCalledToArms:
    def test_a_court_at_peace_with_no_design_on_it_is_not_called(self, world):
        assert R.court_called_to_arms(world, "Hanover") is False   # Prussia boots at bandwagon
        world.nation_gold["Hanover"] = 10000
        assert R.find_ai_commission(world, "Hanover", 10000) is None

    def test_a_design_at_coerce_calls_hanover_up(self, world, monkeypatch):
        import backend.game_logic.intent as I
        real = I.get_nation_intent
        monkeypatch.setattr(I, "get_nation_intent", lambda n, w: (
            _view(n, "Hanover", "coerce") if n == "Prussia" else real(n, w)))
        world.nation_gold["Hanover"] = 10000
        assert R.court_called_to_arms(world, "Hanover") is True
        action = R.find_ai_commission(world, "Hanover", 10000)
        assert action["target"] == "Wallmoden" and action["_acting_nation"] == "Hanover"

    def test_europe_reading_france_against_a_court_calls_it_up(self, world, monkeypatch):
        import backend.game_logic.intent as I
        monkeypatch.setattr(I, "get_france_perceived_intent",
                            lambda w: ("coerce", 70, "Hesse"))
        world.nation_gold["Hesse"] = 10000
        assert R.court_called_to_arms(world, "Hesse") is True
        assert R.find_ai_commission(world, "Hesse", 10000)["target"] == "Emil"

    def test_a_poor_court_called_up_still_pays(self, world, monkeypatch):
        import backend.game_logic.intent as I
        monkeypatch.setattr(I, "get_france_perceived_intent",
                            lambda w: ("coerce", 70, "Hesse"))
        assert R.find_ai_commission(world, "Hesse", 3000) is None   # 2,500 + the 1,000 reserve

    def test_a_court_already_in_the_field_keeps_its_war_or_design_gate(self, world, monkeypatch):
        """The call-up is a court's FIRST general: Portugal, with Bernardim
        Freire standing, raises a second only at war or for its own design."""
        import backend.game_logic.intent as I
        monkeypatch.setattr(I, "get_france_perceived_intent",
                            lambda w: ("coerce", 70, "Portugal"))
        world.nation_gold["Portugal"] = 10000
        assert R.court_called_to_arms(world, "Portugal") is True
        assert R.find_ai_commission(world, "Portugal", 10000) is None

    def test_held_down_only_war_or_its_own_design_calls(self, world, monkeypatch):
        import backend.game_logic.intent as I
        monkeypatch.setattr(I, "get_france_perceived_intent",
                            lambda w: ("coerce", 70, "Hesse"))
        hold_down(monkeypatch, S14K_SEAMS_BY_ROW["K3"])
        assert R.find_ai_commission(world, "Hesse", 10000) is None


class TestK4TheSatelliteServesByItsContingent:
    def test_hollands_war_beside_france_raises_no_corps_of_its_own(self, world):
        assert world.is_at_war("Holland", "Britain")       # France's war, at boot
        assert R.satellite_serves_by_contingent(world, "Holland") is True
        assert R.find_ai_commission(world, "Holland", 10000) is None

    def test_a_war_of_its_own_opens_its_bench(self, world):
        from backend.game_logic.diplomacy import set_diplomatic_state
        set_diplomatic_state(world, "Holland", "France", "WAR", "setup")
        world.nation_gold["Holland"] = 10000
        assert R.satellite_serves_by_contingent(world, "Holland") is False
        assert R.find_ai_commission(world, "Holland", 10000)["target"] == "Janssens"

    def test_held_down_a_satellite_commissions_in_its_lords_war(self, world, monkeypatch):
        hold_down(monkeypatch, S14K_SEAMS_BY_ROW["K4"])
        world.nation_gold["Holland"] = 10000
        assert R.find_ai_commission(world, "Holland", 10000)["target"] == "Janssens"


class TestK5TheForceLimitReadsTheTier:
    @pytest.mark.parametrize("nation,limit", [
        ("France", 130000),        # major: 60,000 + 28 provinces
        ("Austria", 77500),        # the binding boot constraint, unchanged
        ("Spain", 52500),          # secondary: 30,000 + 9
        ("Ottoman", 65000),        # secondary: 30,000 + 14
        ("Saxony", 17500),         # minor: 15,000 + 1
        ("Portugal", 25000),       # minor: 15,000 + 4
        ("Bavaria", 22500),        # minor: 15,000 + 3 — Deroy's 22,000 fits
    ])
    def test_the_floor_is_the_tiers(self, world, nation, limit):
        assert world.get_force_limit(nation) == limit

    def test_no_court_boots_over_its_limit(self, world):
        """At boot only the great powers that stood over their limit before
        pay a surcharge — every turn-1 bill is unchanged."""
        surcharged = {n for n in world.get_active_nations()
                      if world.calculate_turn_upkeep(n).get("surcharge", 0)}
        assert surcharged == {"France", "Austria", "Prussia"}

    def test_a_one_province_court_arms_no_further_than_its_severe_band(self, world):
        assert severe_band_threshold(world.get_force_limit("Switzerland")) == 26250

    def test_held_down_one_floor_for_every_court(self, monkeypatch):
        hold_down(monkeypatch, S14K_SEAMS_BY_ROW["K5"])
        world = WorldState.from_scenario(str(SCENARIO))
        assert world.get_force_limit("Saxony") == 62500
        assert world.get_force_limit("France") == 130000

    def test_the_counsel_names_the_courts_own_floor(self, world):
        from backend.ai.state_desk import _answer_force_limit
        assert "It grows with the Empire: 60,000 men" in _answer_force_limit(world)
        assert WS.force_limit_floor(world, "Saxony") == 15000


GOALS = {
    "Saxony": ["the_wettin_crown"],
    "Hesse": ["the_westphalian_duchy"],
    "Portugal": ["the_old_alliance"],
    "Hanover": ["the_electorate"],
    "Switzerland": ["the_confederation"],
    "Denmark": ["neutrality_of_the_north", "scania"],
    "Ottoman": ["guard_the_straits", "the_black_sea_shore"],
}


def _ids(world, nation):
    return [entry.get("id") for entry in world.agendas.get(nation, [])]


class TestG1TheCourtsGoals:
    def test_every_court_that_fought_has_a_goal(self, world):
        for nation, ids in GOALS.items():
            assert _ids(world, nation) == ids, nation

    def test_the_ambitions_sleep_at_boot(self, world):
        """The moment wakes them, not the clock: each design is aimed at
        its holder and priced below `coerce` on turn 1."""
        for nation, holder in (("Saxony", "Prussia"), ("Hesse", "Hanover")):
            view = get_nation_intent(nation, world)
            assert view.against == holder, nation
            assert rung_index(view.price) < rung_index("coerce"), (nation, view.price)

    def test_the_neutral_courts_guard_their_own_soil(self, world):
        for nation, want in (("Portugal", "the_old_alliance"),
                             ("Hanover", "the_electorate"),
                             ("Denmark", "neutrality_of_the_north"),
                             ("Ottoman", "guard_the_straits")):
            view = get_nation_intent(nation, world)
            assert (view.want_id, view.against) == (want, None), nation

    def test_switzerland_sleeps_while_frances_satellite(self, world):
        assert get_nation_intent("Switzerland", world).want_id is None

    def test_a_neutral_posture_yields_to_a_war(self, world):
        set_diplomatic_state(world, "Portugal", "Spain", "WAR", "test")
        assert get_nation_intent("Portugal", world).want_id is None

    def test_denmarks_scania_wakes_only_in_a_war(self, world):
        set_diplomatic_state(world, "Denmark", "Sweden", "WAR", "test")
        view = get_nation_intent("Denmark", world)
        assert (view.want_id, view.against) == ("scania", "Sweden")

    def test_the_portes_black_sea_shore_wakes_only_in_a_war(self, world):
        set_diplomatic_state(world, "Ottoman", "Russia", "WAR", "test")
        view = get_nation_intent("Ottoman", world)
        assert (view.want_id, view.against) == ("the_black_sea_shore", "Russia")

    def test_held_down_the_decks_are_as_before(self, monkeypatch):
        hold_down(monkeypatch, S14K_SEAMS_BY_ROW["G1"])
        world = WorldState.from_scenario(str(SCENARIO))
        for nation in ("Saxony", "Hesse", "Portugal", "Hanover", "Switzerland"):
            assert nation not in world.agendas, nation
        assert _ids(world, "Denmark") == ["neutrality_of_the_north"]
        assert _ids(world, "Ottoman") == ["guard_the_straits"]


class TestG2TheSleepierCourts:
    def test_saxony_and_hesse_read_sleepier_than_the_default(self, world):
        assert SC.statecraft_weight_mod(world, "Saxony") == -8
        assert SC.statecraft_weight_mod(world, "Hesse") == -12
        others = [n for n in world.get_active_nations() if n not in ("Saxony", "Hesse")]
        assert all(SC.statecraft_weight_mod(world, n) == 0 for n in others)

    def test_held_down_the_ladder_reads_the_default(self, monkeypatch):
        shipped = WorldState.from_scenario(str(SCENARIO))
        before = {n: get_nation_intent(n, shipped).weight for n in ("Saxony", "Hesse")}
        hold_down(monkeypatch, S14K_SEAMS_BY_ROW["G2"])
        down = WorldState.from_scenario(str(SCENARIO))
        assert get_nation_intent("Saxony", down).weight == before["Saxony"] + 8
        assert get_nation_intent("Hesse", down).weight == before["Hesse"] + 12


class TestG3TheNewOrder:
    def test_the_porte_boots_with_the_new_order_not_in_force(self, world):
        assert [row["id"] for row in RF.deck(world, "Ottoman")] == ["nizam_i_cedid"]
        assert not RF.laws_in_force(world, "Ottoman")
        assert world.get_force_limit("Ottoman") == 65000   # secondary 30,000 + 14 provinces

    def test_proclaimed_the_porte_fields_an_army_as_a_great_power_does(self, world):
        world.nation_gold["Ottoman"] = 20000
        RF.enact_law(world, "Ottoman", RF.find_law(world, "Ottoman", "nizam_i_cedid"))
        assert WS.force_limit_floor(world, "Ottoman") == 60000
        assert world.get_force_limit("Ottoman") == 95000
        assert severe_band_threshold(world.get_force_limit("Ottoman")) == 142500
        assert RF.effect_clauses(world, "Ottoman", "recruit_morale") == [
            {"type": "recruit_morale", "arm": "infantry", "value": 5}]
        assert RF.law_upkeep_bill(world, "Ottoman") == 200

    def test_an_empty_chest_lapses_it_like_any_law(self, world):
        """The Janissaries' revolt of 1807, by machinery: the New Order
        lapses when the treasury cannot pay its wages, and the floor falls
        back to the Porte's own tier."""
        world.nation_gold["Ottoman"] = 20000
        RF.enact_law(world, "Ottoman", RF.find_law(world, "Ottoman", "nizam_i_cedid"))
        world.nation_gold["Ottoman"] = -50
        RF.process_law_lapses(world)
        assert not RF.laws_in_force(world, "Ottoman")
        assert world.get_force_limit("Ottoman") == 65000

    def test_a_quiet_porte_does_not_proclaim_it(self, world):
        world.nation_gold["Ottoman"] = 50000
        assert RF.threat_moves_the_court(world, "Ottoman") is False
        assert RF.find_ai_enactment(world, "Ottoman", 50000, 2) is None

    def test_a_porte_at_war_proclaims_it(self, world):
        world.nation_gold["Ottoman"] = 50000
        set_diplomatic_state(world, "Ottoman", "Russia", "WAR", "test")
        assert RF.find_ai_enactment(world, "Ottoman", 50000, 2) == {
            "action": "enact_law", "target": "nizam_i_cedid"}

    def test_a_design_priced_against_the_porte_proclaims_it(self, world, monkeypatch):
        import backend.game_logic.intent as I
        real = I.get_nation_intent
        monkeypatch.setattr(I, "get_nation_intent", lambda n, w: (
            _view(n, "Ottoman", "coerce") if n == "Russia" else real(n, w)))
        world.nation_gold["Ottoman"] = 50000
        assert RF.find_ai_enactment(world, "Ottoman", 50000, 2) == {
            "action": "enact_law", "target": "nizam_i_cedid"}

    def test_held_down_the_porte_has_no_deck(self, monkeypatch):
        hold_down(monkeypatch, S14K_SEAMS_BY_ROW["G3"])
        world = WorldState.from_scenario(str(SCENARIO))
        assert RF.deck(world, "Ottoman") == []
        assert world.get_force_limit("Ottoman") == 65000


@pytest.fixture(scope="module")
def scenario():
    with open(SCENARIO, encoding="utf-8") as fh:
        return json.load(fh)


def _reform_findings(scenario, mutate):
    data = copy.deepcopy(scenario)
    mutate(data["reforms"])
    result = validate_scenario(data)
    return ([str(e) for e in result.errors if "reforms" in str(e)],
            [str(w) for w in result.warnings if "reforms" in str(w)])


class TestTheNewOrderValidates:
    def test_the_portes_deck_carries_no_staff_and_validates(self, scenario):
        # RE-SEATED by T4-3 (session A, November 10, 2026): the crowns of 1806 are
        # promotion decks beside the R6 decks, and draw no warning either.
        assert {c for c, rows in scenario["reforms"].items()
                if not all(RF.is_promotion(r) for r in rows)} == set(RF.REFORM_DECKS)
        assert _reform_findings(scenario, lambda b: None) == ([], [])

    def test_a_great_power_still_carries_its_one_staff(self, scenario):
        errors, _ = _reform_findings(scenario, lambda b: b["France"].pop(0))
        assert errors

    def test_a_second_staff_on_the_porte_is_refused(self, scenario):
        def two(b):
            for law_id in ("a", "b"):
                staff = copy.deepcopy(b["France"][0])
                staff["id"] = law_id
                b["Ottoman"].append(staff)
        errors, _ = _reform_findings(scenario, two)
        assert errors

    def test_under_threat_is_a_boolean(self, scenario):
        errors, _ = _reform_findings(
            scenario, lambda b: b["Ottoman"][0].__setitem__("under_threat", "yes"))
        assert errors

    @pytest.mark.parametrize("tier", ["minor", "emperor"])
    def test_a_force_limit_clause_names_a_higher_tier(self, scenario, tier):
        errors, _ = _reform_findings(
            scenario, lambda b: b["Ottoman"][0]["effects"][0].__setitem__("tier", tier))
        assert errors

    def test_a_deck_beyond_r6_is_still_a_warning(self, scenario):
        errors, warnings = _reform_findings(
            scenario, lambda b: b.__setitem__("Saxony", copy.deepcopy(b["Ottoman"])))
        assert not errors and warnings


class TestTheRowsHeldDownAreTheOldBoot:
    def test_every_s14k_row_down_boots_the_world_before_it(self, monkeypatch):
        hold_down(monkeypatch, [s for row in S14K_SEAMS_BY_ROW for s in S14K_SEAMS_BY_ROW[row]])
        world = WorldState.from_scenario(str(SCENARIO))
        assert len(world.marshals) == 22
        assert world.eliminated_nations_notified == {
            "Portugal", "Saxony", "Hanover", "Hesse", "PapalStates", "Sardinia",
            "Holland", "KingdomOfItaly", "Switzerland"}
        assert world.get_force_limit("Switzerland") == 62500
        assert not any(nation in world.agendas for nation in
                       ("Saxony", "Hesse", "Portugal", "Hanover", "Switzerland"))
        assert _ids(world, "Ottoman") == ["guard_the_straits"]
        # RE-SEATED by T4-3 (session A, November 10, 2026): a later tier's content
        # under its own seam — the crowns stand (three of them on designs G1's
        # seam struck here: they boot with a warning and wait unenactable).
        assert {c for c, rows in world.reforms.items()
                if not all(RF.is_promotion(r) for r in rows)} == set(RF.GREAT_POWERS)
        assert RF.promotion_grounds(world, "Saxony", RF.deck(world, "Saxony")[0]) is None
        assert SC.statecraft_weight_mod(world, "Hesse") == 0


@pytest.mark.xfail(
    strict=True,
    reason="S14k part 3 (after S15 — the user's ruling, October 28, 2026: "
           "'After S15'; PRE_DEPLOY_PLAN.md §2 row S14k-3): GR10's sibling of "
           "G1. T2-6 (November 8, 2026) authored Bavaria's and Naples' decks "
           "(the Tyrol; the September Treaty + the Roman Expedition), so "
           "SPAIN alone still fields armies with no goal of its own — the "
           "S14k-3 residue. This turns RED the day Spain carries an authored "
           "deck — then retire the xfail.")
def test_every_armed_court_carries_a_goal(world):
    """Every court that fields an army at boot or can raise one (a bench)
    carries a deck of its own — the player's France aside (the Victory Pass
    owns its goals)."""
    armed = ({m.nation for m in world.marshals.values()}
             | {n for n, rows in (world.marshal_pool or {}).items() if rows})
    deckless = sorted(n for n in armed - {world.player_nation} if not world.agendas.get(n))
    assert deckless == [], deckless
