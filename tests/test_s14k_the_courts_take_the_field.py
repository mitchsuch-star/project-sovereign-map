"""S14k "The Courts Take the Field" — part 1: armies, benches and the ceiling.

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
"""
from pathlib import Path

import pytest

from backend.game_logic import recruitment as R
from backend.game_logic.intent import IntentView
from backend.game_logic.ledger import _build_economy
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


class TestTheRowsHeldDownAreTheOldBoot:
    def test_every_s14k_row_down_boots_the_world_before_it(self, monkeypatch):
        hold_down(monkeypatch, [s for row in S14K_SEAMS_BY_ROW for s in S14K_SEAMS_BY_ROW[row]])
        world = WorldState.from_scenario(str(SCENARIO))
        assert len(world.marshals) == 22
        assert world.eliminated_nations_notified == {
            "Portugal", "Saxony", "Hanover", "Hesse", "PapalStates", "Sardinia",
            "Holland", "KingdomOfItaly", "Switzerland"}
        assert world.get_force_limit("Switzerland") == 62500
