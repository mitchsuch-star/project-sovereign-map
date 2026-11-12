"""Session G4 — the open readings, ruled and built (DYNAMISM_SPEC.md §7d;
November 11, 2026).

The user's word, at session G3's close: "evaluate options choose the best"
(Italy), then "and decide and do these" — a pact a court brings into a
vassalage, a client's non-aggression pacts, the rest of session G2's list.
Fourteen rulings, drafted in Plan Mode and approved; one class a ruling:

  1  FORM     a nation is proclaimed on what it HOLDS, at its authored bar
  2  WON      an ally's soil is not won
  3  LAPSE    a pact lapses at the vassalage
  4           a client's lesser pacts stay its own (nothing built — pinned)
  5  REAR     a backer is no menace
  6  KING     the people drive out a foreign king
  7           the push stays 10 for every backer (nothing built — pinned)
  8  CEILING  a commission reads the arming ceiling
  9  ALLY     the Emperor's ally takes no separate peace while it is winning
  10 GUNS     no guns from a sanctuary
  11 WAGON    a bandwagoner joins a neighbour's war
  12          the dispatch drops a capture the morning has overtaken
  13          the crown row leads the demands
  14          no "§" in the sponsor chip
  +  HOUSE    the treaty fuzzer's catch: a client joins no war against a
              client of a house it stands at peace with
  +           the counter's dry run on a draft with no clauses list
"""
from __future__ import annotations

import contextlib
import inspect
import io
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from backend.commands import combat_executor as CE  # noqa: E402
from backend.game_logic import agendas as AG  # noqa: E402
from backend.game_logic import crowns as CR  # noqa: E402
from backend.game_logic import diplomacy as DI  # noqa: E402
from backend.game_logic import dispatch as DP  # noqa: E402
from backend.game_logic import formations as FM  # noqa: E402
from backend.game_logic import intent as IT  # noqa: E402
from backend.game_logic import recruitment as RC  # noqa: E402
from backend.game_logic import settlement_third_party as TP  # noqa: E402
from backend.game_logic import vassal as V  # noqa: E402
from backend.game_logic import war_council as WC  # noqa: E402
from tests._t3_seams import T3_SEAMS_BY_ROW, hold_down  # noqa: E402
from tests.test_session_g2_the_played_campaign import (  # noqa: E402
    _austria_beaten, _hungary_term, _laurels, _separate_peace,
)

SCENARIO = (REPO / "godot-client" / "project-sovereign" / "assets"
            / "maps" / "europe_1805.json")
ROWS = ("G4-FORM", "G4-WON", "G4-LAPSE", "G4-REAR", "G4-CEILING", "G4-ALLY",
        "G4-GUNS", "G4-WAGON", "G4-KING", "G4-HOUSE")
SEAMS = {
    "G4-FORM": FM.a_nation_is_proclaimed_on_what_it_holds,
    "G4-WON": AG.an_allys_soil_is_not_won,
    "G4-LAPSE": V.a_pact_lapses_at_the_vassalage,
    "G4-REAR": WC.a_backer_is_no_menace,
    "G4-CEILING": RC.a_commission_reads_the_arming_ceiling,
    "G4-ALLY": TP.the_emperors_ally_takes_no_separate_peace,
    "G4-GUNS": CE.no_guns_from_a_sanctuary,
    "G4-WAGON": WC.a_bandwagoner_joins_a_neighbours_war,
    "G4-KING": CR.the_people_drive_out_a_foreign_king,
    "G4-HOUSE": DI.a_client_joins_no_war_against_a_house_at_peace,
}


def _world(seed: str = "historical"):
    from backend.models.world_state import WorldState
    return WorldState.from_scenario(str(SCENARIO), seed=seed)


@pytest.fixture()
def world():
    return _world("historical")


@pytest.fixture()
def jena():
    """The seed that casts Naples: `roman_expedition` at her deck's head."""
    return _world("jena")


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


def _state(world, a: str, b: str) -> str:
    return str(world.get_diplomatic_state(a, b))


def _set_state(world, a: str, b: str, state: str) -> None:
    world.diplomatic_states[world._make_diplo_key(a, b)] = state
    world.invalidate_bloc_members_cache()


def _flush(world) -> None:
    world.invalidate_active_nations_cache()
    world.invalidate_bloc_members_cache()


def _down(row: str):
    """A context holding ONE of the session's seams down."""
    patcher = pytest.MonkeyPatch.context()
    m = patcher.__enter__()
    hold_down(m, T3_SEAMS_BY_ROW[row])
    return patcher


# ═══════════════════════════════════════════════════════════════════════
# 1 — FORM: a nation is proclaimed on what it holds, at its bar
# ═══════════════════════════════════════════════════════════════════════

def _free_italy(world) -> dict:
    """The Kingdom of Italy out of its vassalage and at peace with Europe —
    the board on which its Risorgimento wakes."""
    del world.vassals["KingdomOfItaly"]
    for court in ("France", "Austria", "Britain", "Russia"):
        _set_state(world, court, "KingdomOfItaly", "PEACE")
    _flush(world)
    return world.agendas["KingdomOfItaly"][0]


class TestANationIsProclaimedOnWhatItHolds:
    def test_the_marker_names_the_bar(self, world):
        watch = FM.get_formation_watch(world, "KingdomOfItaly")
        assert (watch["held"], watch["required"], watch["at"]) == (2, 5, 3)
        assert watch["progress"] == "2 of 5 provinces held — 3 proclaim it"
        dutch = FM.get_formation_watch(world, "Holland")
        assert (dutch["held"], dutch["required"], dutch["at"]) == (0, 1, 1)
        assert dutch["progress"] == "0 of 1 province held"      # no bar authored: as before

    def test_the_hollow_road_is_closed(self, world):
        """Session G2's tree: freed with two provinces, Rome, Naples and
        Savoy in its allies' blocs — and ITALY stood. The proclamation
        reads possession now."""
        entry = _free_italy(world)
        for ally in ("PapalStates", "Naples", "France"):
            _set_state(world, "KingdomOfItaly", ally, "DEFENSIVE_ALLIANCE")
        forms = FM.get_forms_block(entry)
        assert FM.held_provinces(world, "KingdomOfItaly", entry) == ["Milan", "Piedmont"]
        assert FM.proclamation_due(world, "KingdomOfItaly", entry, forms) is False
        with _quiet():
            assert FM.process_formations(world) == []
        # the two seams down: the old read, and Italy on two provinces
        with pytest.MonkeyPatch.context() as m:
            hold_down(m, T3_SEAMS_BY_ROW["G4-FORM"] + T3_SEAMS_BY_ROW["G4-WON"])
            assert FM.proclamation_due(world, "KingdomOfItaly", entry, forms) is True

    def test_rome_makes_italy_and_the_rest_stay_her_claims(self, world):
        _free_italy(world)
        world.regions["Rome"].controller = "KingdomOfItaly"
        _flush(world)
        with _quiet():
            out = FM.process_formations(world)
        assert [(p["nation"], p["display_name"]) for p in out] == [("KingdomOfItaly", "Italy")]
        assert out[0]["unredeemed"] == ["Savoy", "Naples"]
        card = FM.build_proclamation_card(world, out[0])
        assert "it still claims Savoy and Naples" in card["terms"]
        assert world.nation_formations["KingdomOfItaly"]["formed"] is True
        # the forming design stays her live want until the list is whole
        assert AG.get_active_agenda("KingdomOfItaly", world).id == "risorgimento"
        # ... and she reaches for the south before France's Savoy (`forms.first`)
        assert AG.get_agenda_covets("KingdomOfItaly", world) == ["Naples", "Savoy"]
        with _quiet():
            assert FM.process_formations(world) == []       # once only

    def test_a_client_holding_three_proclaims_nothing(self, world):
        world.regions["Rome"].controller = "KingdomOfItaly"
        _flush(world)
        with _quiet():
            assert FM.process_formations(world) == []
        assert FM.get_formation_watch(world, "KingdomOfItaly")["blocked_by_vassalage"] is True

    def test_the_seam_down_wants_the_whole_list(self, world, monkeypatch):
        hold_down(monkeypatch, T3_SEAMS_BY_ROW["G4-FORM"])
        entry = _free_italy(world)
        world.regions["Rome"].controller = "KingdomOfItaly"
        _flush(world)
        assert FM.proclamation_bar(entry) == 5
        watch = FM.get_formation_watch(world, "KingdomOfItaly")
        assert (watch["at"], watch["progress"]) == (5, "3 of 5 provinces held")
        with _quiet():
            assert FM.process_formations(world) == []

    def test_the_browser_states_the_bar(self, world):
        rows = FM.build_formables_payload(world)
        texts = [t["text"] for group in rows.values() if isinstance(group, list)
                 for row in group if isinstance(row, dict)
                 for t in (row.get("gate_terms") or [])]
        assert "forms when a free Kingdom of Italy holds 3 of its 5 claimed provinces" in texts
        assert "forms when a free Holland holds its claimed province" in texts

    def test_the_validator_reads_the_bar(self):
        from backend.modding.validator import ValidationResult, _validate_forms_bar
        entry = {"type": "acquire_regions", "regions": ["A", "B", "C"],
                 "forms": {"display_name": "X", "at": 2}}
        ok = ValidationResult()
        _validate_forms_bar(ok, "agendas.X[0]", entry)
        assert not ok.errors and not ok.warnings
        for bad in (0, -1, "2", True, 1.5):
            result = ValidationResult()
            _validate_forms_bar(result, "agendas.X[0]", dict(entry, forms={"display_name": "X", "at": bad}))
            assert result.errors, bad
        past = ValidationResult()
        _validate_forms_bar(past, "agendas.X[0]", dict(entry, forms={"display_name": "X", "at": 9}))
        assert not past.errors and past.warnings
        other = ValidationResult()
        _validate_forms_bar(other, "agendas.X[0]", dict(entry, type="deny_regions"))
        assert not other.errors and other.warnings
        assert FM.proclamation_bar(dict(entry, forms={"display_name": "X", "at": 9})) == 3

    def test_the_shipped_scenario_authors_italy_at_three(self):
        deck = json.loads(SCENARIO.read_text(encoding="utf-8"))["agendas"]
        assert deck["KingdomOfItaly"][0]["forms"]["at"] == 3
        assert deck["KingdomOfItaly"][0]["forms"]["first"] == ["Rome", "Naples"]
        assert deck["KingdomOfItaly"][0]["regions"] == ["Milan", "Piedmont", "Savoy", "Naples", "Rome"]
        assert "at" not in deck["Holland"][0]["forms"] and "first" not in deck["Holland"][0]["forms"]

    def test_a_save_made_before_the_bar_gains_it_at_load(self, world):
        """The deck rides the save: the turn-10 save of the played campaign
        showed "all 5 of its claimed provinces" in the client. The load
        backfills the authored keys onto the saved entry — and never over a
        value the save holds."""
        scenario = json.loads(SCENARIO.read_text(encoding="utf-8"))
        forms = world.agendas["KingdomOfItaly"][0]["forms"]
        del forms["at"], forms["first"]                    # the deck as an old save carries it
        world._agenda_cache = None
        assert FM.get_formation_watch(world, "KingdomOfItaly")["at"] == 5
        assert FM.backfill_forms(world, scenario) == 2
        assert (forms["at"], forms["first"]) == (3, ["Rome", "Naples"])
        assert FM.get_formation_watch(world, "KingdomOfItaly")["at"] == 3
        assert FM.backfill_forms(world, scenario) == 0     # idempotent
        forms["at"] = 4                                    # a value the save holds stands
        assert FM.backfill_forms(world, scenario) == 0 and forms["at"] == 4
        # Holland's block authors neither key: untouched
        assert "at" not in world.agendas["Holland"][0]["forms"]

    def test_the_load_road_calls_the_backfill(self):
        from backend import save_manager as SM
        source = inspect.getsource(SM)
        assert source.count("_backfill_forms(world)") == 1
        assert "backfill_forms(world, data)" in inspect.getsource(SM._backfill_forms)

    def test_she_reaches_for_rome_first(self, world):
        """Played out before the pursuit order, a freed Kingdom of Italy
        fixed on Savoy — third in her list, and France's — and never turned
        to Rome. `forms.first` leads the order every reader takes the first
        unmet target from."""
        entry = _free_italy(world)
        assert AG._entry_regions(world, "KingdomOfItaly", entry) == [
            "Rome", "Naples", "Milan", "Piedmont", "Savoy"]
        assert AG.get_agenda_covets("KingdomOfItaly", world) == ["Rome", "Naples", "Savoy"]
        world._intent_cache = None
        assert IT.get_nation_intent("KingdomOfItaly", world).against == "PapalStates"
        with pytest.MonkeyPatch.context() as m:
            hold_down(m, T3_SEAMS_BY_ROW["G4-FORM"])
            world._agenda_cache = None
            world._intent_cache = None
            assert AG._entry_regions(world, "KingdomOfItaly", entry) == entry["regions"]
            assert IT.get_nation_intent("KingdomOfItaly", world).against == "France"

    def test_the_pursuit_order_is_the_forming_designs_alone(self, world):
        hesse = world.agendas["Hesse"][0]
        assert AG._pursuit_order(hesse, list(hesse["regions"])) == hesse["regions"]
        entry = {"regions": ["A", "B", "C"], "forms": {"display_name": "X", "first": ["C", "Z"]}}
        assert AG._pursuit_order(entry, ["A", "B", "C"]) == ["C", "A", "B"]     # a stray name is ignored
        assert AG._pursuit_order(dict(entry, forms={"display_name": "X"}), ["A", "B"]) == ["A", "B"]

    def test_the_validator_reads_the_pursuit_order(self):
        from backend.modding.validator import ValidationResult, _validate_forms_bar
        entry = {"type": "acquire_regions", "regions": ["A", "B", "C"],
                 "forms": {"display_name": "X", "first": ["C"]}}
        ok = ValidationResult()
        _validate_forms_bar(ok, "agendas.X[0]", entry)
        assert not ok.errors and not ok.warnings
        for bad in ("C", [1], [""], {"C": 1}):
            result = ValidationResult()
            _validate_forms_bar(result, "agendas.X[0]", dict(entry, forms={"display_name": "X", "first": bad}))
            assert result.errors, bad
        stray = ValidationResult()
        _validate_forms_bar(stray, "agendas.X[0]", dict(entry, forms={"display_name": "X", "first": ["Z"]}))
        assert not stray.errors and stray.warnings


# ═══════════════════════════════════════════════════════════════════════
# 2 — WON: an ally's soil is not won
# ═══════════════════════════════════════════════════════════════════════

class TestAnAllysSoilIsNotWon:
    def _hesse_allied(self, world) -> dict:
        entry = world.agendas["Hesse"][0]
        assert (entry["id"], entry["regions"]) == ("the_westphalian_duchy", ["Westphalia"])
        _set_state(world, "Hesse", "Hanover", "DEFENSIVE_ALLIANCE")
        return entry

    def test_the_design_sleeps_and_is_not_satisfied(self, world):
        entry = self._hesse_allied(world)
        assert AG.get_agenda_covets("Hesse", world) == []        # it sleeps (SF-LB-1's law)
        assert AG.entry_satisfied(world, "Hesse", entry) is False

    def test_the_seam_down_reads_the_alliance_as_a_conquest(self, world, monkeypatch):
        entry = self._hesse_allied(world)
        hold_down(monkeypatch, T3_SEAMS_BY_ROW["G4-WON"])
        assert AG.entry_satisfied(world, "Hesse", entry) is True

    def test_held_is_won_either_way(self, world):
        entry = world.agendas["Hesse"][0]
        assert AG.entry_satisfied(world, "Hesse", entry) is False
        world.regions["Westphalia"].controller = "Hesse"
        _flush(world)
        assert AG.entry_satisfied(world, "Hesse", entry) is True
        with pytest.MonkeyPatch.context() as m:
            hold_down(m, T3_SEAMS_BY_ROW["G4-WON"])
            assert AG.entry_satisfied(world, "Hesse", entry) is True


# ═══════════════════════════════════════════════════════════════════════
# 3 — LAPSE: a pact lapses at the vassalage
# ═══════════════════════════════════════════════════════════════════════

class TestAPactLapsesAtTheVassalage:
    def test_the_decision(self, world):
        _set_state(world, "Saxony", "Sweden", "DEFENSIVE_ALLIANCE")
        assert V._vassalage_entry_decision(world, "France", "Saxony", "Sweden") == (
            "pact", "NON_AGGRESSION")
        _set_state(world, "Saxony", "Sweden", "ALLIANCE")
        assert V._vassalage_entry_decision(world, "France", "Saxony", "Sweden") == (
            "pact", "NON_AGGRESSION")
        # the lord's ENEMY: the older arm, said first
        _set_state(world, "Saxony", "Austria", "ALLIANCE")
        assert V._vassalage_entry_decision(world, "France", "Saxony", "Austria") == (
            "alliance", "PEACE")
        # inside the lord's house: the vassalage itself
        _set_state(world, "Saxony", "Holland", "DEFENSIVE_ALLIANCE")
        assert V._vassalage_entry_decision(world, "France", "Saxony", "Holland") is None
        # the rungs below a pact are no pact
        _set_state(world, "Saxony", "Denmark", "NON_AGGRESSION")
        assert V._vassalage_entry_decision(world, "France", "Saxony", "Denmark") is None

    def test_the_seam_down_leaves_it_standing(self, world, monkeypatch):
        hold_down(monkeypatch, T3_SEAMS_BY_ROW["G4-LAPSE"])
        _set_state(world, "Saxony", "Sweden", "DEFENSIVE_ALLIANCE")
        assert V._vassalage_entry_decision(world, "France", "Saxony", "Sweden") is None

    def test_the_entry_lapses_it_and_records_no_breach(self, world):
        _set_state(world, "Saxony", "Sweden", "DEFENSIVE_ALLIANCE")
        world.vassals["Saxony"] = dict(world.vassals["Holland"], lord="France")
        _flush(world)
        strikes = len(getattr(world, "betrayal_history", []) or [])
        before = len(world.event_log)
        with _quiet():
            V._reconcile_vassal_diplomacy(world, "France", "Saxony")
        assert _state(world, "Saxony", "Sweden") == "NON_AGGRESSION"
        assert len(getattr(world, "betrayal_history", []) or []) == strikes
        assert not [e for e in world.event_log[before:]
                    if "broken" in str(e.get("type")) or "breach" in str(e.get("type"))]

    def test_a_transfer_lapses_it_too(self, world):
        _set_state(world, "KingdomOfItaly", "Bavaria", "DEFENSIVE_ALLIANCE")
        with _quiet():
            result = V.transfer_vassal(world, "KingdomOfItaly", "Russia")
        assert result.get("success", True) is not False
        assert world.vassals["KingdomOfItaly"]["lord"] == "Russia"
        assert _state(world, "KingdomOfItaly", "Bavaria") == "NON_AGGRESSION"

    def test_the_conquests_quote_says_it(self, world):
        _set_state(world, "Saxony", "Sweden", "DEFENSIVE_ALLIANCE")
        plan = V.subjugation_plan(world, "France", "Saxony")
        assert {"court": "Sweden", "kind": "pact", "to": "NON_AGGRESSION"} in plan["entry"]
        assert {"pair": ["Saxony", "Sweden"], "from": "DEFENSIVE_ALLIANCE",
                "to": "NON_AGGRESSION"} in plan["closes"]
        assert ("Their alliance with Sweden lapses to a non-aggression pact — a client signs no "
                "alliance of its own.") in V.subjugation_quote(world, "France", "Saxony", plan)


# ═══════════════════════════════════════════════════════════════════════
# 4 — a client's lesser pacts stay its own (nothing built; pinned)
# ═══════════════════════════════════════════════════════════════════════

class TestAClientsLesserPactsStayItsOwn:
    def test_a_non_aggression_pact_does_not_hold_it_out_of_its_lords_war(self, world):
        """The reason nothing is built: the client follows its lord over its
        own non-aggression pact, and no broken word is recorded."""
        from backend.game_logic.diplomacy import declare_war
        _set_state(world, "KingdomOfItaly", "Prussia", "NON_AGGRESSION")
        assert _state(world, "France", "Prussia") != "WAR"
        strikes = len(getattr(world, "betrayal_history", []) or [])
        with _quiet():
            result = declare_war(world, "Prussia", "France")
        assert result["success"] is True
        assert _state(world, "KingdomOfItaly", "Prussia") == "WAR"
        joined = [e for e in world.event_log if e.get("type") == "vassal_auto_join_war"
                  and e.get("vassal") == "KingdomOfItaly"]
        assert joined and joined[-1]["against"] == "Prussia"
        assert not [h for h in (getattr(world, "betrayal_history", []) or [])[strikes:]
                    if "KingdomOfItaly" in json.dumps(h, default=str)]

    def test_the_vassalage_leaves_the_lesser_pacts_alone(self, world):
        for state in ("NON_AGGRESSION", "OPEN_BORDERS"):
            _set_state(world, "Saxony", "Denmark", state)
            assert V._vassalage_entry_decision(world, "France", "Saxony", "Denmark") is None


# ═══════════════════════════════════════════════════════════════════════
# 5 — REAR: a backer is no menace
# ═══════════════════════════════════════════════════════════════════════

def _back(world, payer: str, recipient: str, aim: str, amount: int = 0, turns: int = 10) -> None:
    world.directed_sponsorships.append({
        "kind": "sponsorship", "payer": payer, "recipient": recipient, "aim": aim,
        "amount_per_turn": int(amount), "turns_remaining": int(turns)})
    world.invalidate_bloc_members_cache()


class TestABackerIsNoMenace:
    def test_the_licensor_is_struck_from_the_rear(self, world):
        before = WC.get_exposure_view(world, "Prussia")
        assert before["worst_threat"] == "Russia"
        _back(world, "Russia", "Prussia", "Sweden")
        after = WC.get_exposure_view(world, "Prussia")
        assert "Russia" not in [t["nation"] for t in after["threats"]]
        assert after["worst_threat"] == "Bavaria"
        assert after["free"] > before["free"] and after["reserve"] < before["reserve"]
        assert WC.backers_of(world, "Prussia") == {"Russia"}

    def test_he_speaks_for_his_own_house_only(self, world):
        """The played board: France licenses Russia; Prussia on her flank
        holds her as before."""
        before = [t["nation"] for t in WC.get_exposure_view(world, "Russia")["threats"]]
        assert "Prussia" in before
        _set_state(world, "France", "Russia", "PEACE")
        _back(world, "France", "Russia", "Sweden")
        after = WC.get_exposure_view(world, "Russia")
        assert "Prussia" in [t["nation"] for t in after["threats"]]
        assert "France" not in [t["nation"] for t in after["threats"]]

    def test_the_compact_ended_he_menaces_again(self, world):
        _back(world, "Russia", "Prussia", "Sweden", turns=0)
        assert WC.backers_of(world, "Prussia") == set()
        assert WC.get_exposure_view(world, "Prussia")["worst_threat"] == "Russia"

    def test_a_backer_at_war_with_the_court_still_menaces(self, world):
        """No compact outlives a war between its two ends; the read does not
        lean on it."""
        _back(world, "Russia", "Prussia", "Sweden")
        _set_state(world, "Russia", "Prussia", "WAR")
        assert "Russia" in [t["nation"] for t in WC.get_exposure_view(world, "Prussia")["threats"]]

    def test_a_bought_neutrality_is_no_backing(self, world):
        world.directed_sponsorships.append({
            "kind": "neutrality", "payer": "Russia", "recipient": "Prussia", "aim": "Sweden",
            "amount_per_turn": 100, "turns_remaining": 10})
        world.invalidate_bloc_members_cache()
        assert WC.backers_of(world, "Prussia") == set()

    def test_the_seam_down_reads_no_backer(self, world, monkeypatch):
        hold_down(monkeypatch, T3_SEAMS_BY_ROW["G4-REAR"])
        _back(world, "Russia", "Prussia", "Sweden")
        assert WC.backers_of(world, "Prussia") == set()
        assert WC.get_exposure_view(world, "Prussia")["worst_threat"] == "Russia"


# ═══════════════════════════════════════════════════════════════════════
# 6 — KING: the people drive out a foreign king
# ═══════════════════════════════════════════════════════════════════════

def _soult_reigns(world) -> dict:
    for name in ("Soult", "Davout", "Massena"):
        _laurels(world, name)
    _austria_beaten(world, 45)
    _separate_peace(world, _hungary_term(world), gold=2800)
    assert world.marshals["Soult"].nation == "Hungary"
    return world.vassals["Hungary"]


class TestThePeopleDriveOutAForeignKing:
    def test_his_people_rise_and_he_comes_home(self, world):
        _soult_reigns(world)
        soult = world.marshals["Soult"]
        corps = int(soult.strength)
        pool = int((world.manpower_pools.get("Hungary") or {}).get("infantry", 0))
        fate = CR.king_at_the_rebellion(world, "Hungary", "France", "awakening")
        home = world.get_nation_capital("France")
        assert fate == {"king_state": "driven_out", "returned_turn": int(world.current_turn),
                        "returned_with": corps // 2, "returned_to": home}
        assert (soult.nation, soult.location, int(soult.strength)) == ("France", home, corps // 2)
        assert int(world.manpower_pools["Hungary"]["infantry"]) == pool + (corps - corps // 2)
        assert world.nation_formations["Hungary"]["king_state"] == "driven_out"
        # he is on the Emperor's roster again
        from backend.game_logic.marshal_overview import build_marshal_overview
        assert "Soult" in [c["name"] for c in build_marshal_overview(world)]
        # a second call moves nothing
        assert CR.king_at_the_rebellion(world, "Hungary", "France", "awakening") == {}

    def test_his_court_turns_and_he_keeps_the_crown(self, world):
        _soult_reigns(world)
        assert CR.king_at_the_rebellion(world, "Hungary", "France", "") == {}
        assert world.marshals["Soult"].nation == "Hungary"
        assert CR.rebel_king_words(world, "Hungary") == (
            " Soult, whom you crowned as King of Hungary, keeps his throne and turns his "
            "corps against you.")

    def test_the_words_follow_the_road_he_took(self, world):
        _soult_reigns(world)
        corps = int(world.marshals["Soult"].strength)
        CR.king_at_the_rebellion(world, "Hungary", "France", "awakening")
        home = world.get_nation_capital("France")
        assert CR.rebel_king_words(world, "Hungary") == (
            f" Soult, whom you crowned as King of Hungary, is driven out by his people and comes "
            f"home to {home} with {corps // 2:,} men.")
        del world.vassals["Hungary"]
        _flush(world)
        row = CR.reigning_rows(world, "France")[0]
        assert row["state"] == "driven_out"
        assert row["line"] == (f"Soult — King of Hungary · driven out by his people; he came home to "
                               f"{home} with {corps // 2:,} men and serves you again")

    def test_the_rebellion_itself_calls_it_on_every_exit(self, world, monkeypatch):
        """The whole road: the kingdom's loyalty gone, the people risen —
        `check_vassal_rebellion` reads the cause and the king comes home."""
        from backend.game_logic import awakening as AW
        _soult_reigns(world)
        monkeypatch.setattr(AW, "rebellion_cause", lambda w, client: "awakening")
        world.vassals["Hungary"]["loyalty"] = 0
        with _quiet():
            V.check_vassal_rebellion(world)
        assert "Hungary" not in world.vassals
        assert world.marshals["Soult"].nation == "France"
        assert world.nation_formations["Hungary"]["king_state"] == "driven_out"

    def test_the_seam_down_he_always_keeps_it(self, world, monkeypatch):
        hold_down(monkeypatch, T3_SEAMS_BY_ROW["G4-KING"])
        _soult_reigns(world)
        assert CR.king_at_the_rebellion(world, "Hungary", "France", "awakening") == {}
        assert world.marshals["Soult"].nation == "Hungary"

    def test_a_king_named_in_the_treaty_is_seated_though_his_laurels_fade(self, world):
        """The replayed campaign: Soult, demanded as King of Hungary with
        glory 3, stood at 2 when the treaty was ratified two turns on — and
        the kingdom erected "under Soult" was a regency. The laurels are the
        pick's test; the treaty seats the king it names."""
        from backend.game_logic import jealousy as JZ
        for name in ("Soult", "Davout", "Massena"):
            _laurels(world, name)
        _austria_beaten(world, 45)
        term = _hungary_term(world)                      # named while he has the laurels
        assert term["king"] == "Soult"
        world.current_turn = int(world.current_turn) + JZ.GLORY_WINDOW + 1
        assert CR.marshal_has_laurels(world, world.marshals["Soult"]) is False
        assert CR.marshal_may_be_crowned(world, world.marshals["Soult"], "France") is False
        assert CR.marshal_free_to_reign(world, world.marshals["Soult"], "France") is True
        _separate_peace(world, term, gold=2800)
        assert world.vassals["Hungary"]["king"] == "Soult"
        assert world.marshals["Soult"].nation == "Hungary"

    def test_a_king_no_longer_the_emperors_to_seat_is_a_regency(self, world):
        for name in ("Soult", "Davout", "Massena"):
            _laurels(world, name)
        _austria_beaten(world, 45)
        term = _hungary_term(world)
        # a prisoner of a THIRD court (the ceding court's own prisoners come
        # home by the very peace, before the crown is erected)
        world.marshals["Soult"].captured_by = "Russia"
        assert CR.marshal_free_to_reign(world, world.marshals["Soult"], "France") is False
        _separate_peace(world, term, gold=2800)
        assert not world.vassals["Hungary"].get("king")
        assert world.marshals["Soult"].nation == "France"
        assert not world.nation_formations["Hungary"].get("king")

    def test_a_prince_and_a_regency_have_no_fate_here(self, world):
        assert CR.king_at_the_rebellion(world, "Holland", "France", "awakening") == {}
        assert CR.king_at_the_rebellion(world, "Nowhere", "France", "awakening") == {}

    def test_the_pick_says_both_roads(self, world):
        foot = CR.laurels_footnote(world, "France")
        assert foot.startswith(
            "A marshal king is beyond recall. If his court ever turns on you he keeps his crown "
            "and fights for it; if his people rise and drive him out, he comes home with half "
            "his corps.")
        with pytest.MonkeyPatch.context() as m:
            hold_down(m, T3_SEAMS_BY_ROW["G4-KING"])
            assert CR.laurels_footnote(world, "France").startswith(
                "A marshal king is beyond recall; should his kingdom ever rise against you, "
                "he keeps his crown and fights for it.")


# ═══════════════════════════════════════════════════════════════════════
# 7 — the push stays 10 for every backer (nothing built; pinned)
# ═══════════════════════════════════════════════════════════════════════

class TestThePushStays:
    def test_one_number_for_the_emperor_and_the_courts(self, world):
        assert IT.WEIGHT_BACKED_DESIGN == 10
        source = inspect.getsource(IT._derive_weight)
        assert source.count("WEIGHT_BACKED_DESIGN") == 1       # one term, no payer in it


# ═══════════════════════════════════════════════════════════════════════
# 8 — CEILING: a commission reads the arming ceiling
# ═══════════════════════════════════════════════════════════════════════

def _naples_can_commission(jena, standing: int) -> None:
    jena.marshals["Damas"].strength = int(standing)
    jena.nation_gold["Naples"] = 60_000
    pools = jena.manpower_pools.setdefault("Naples", {})
    pools["infantry"] = max(int(pools.get("infantry", 0) or 0), 20_000)
    jena._intent_cache = None


class TestACommissionReadsTheArmingCeiling:
    def test_the_played_boards_leak(self, jena):
        """Naples, limit 32,500, armed to her designed 48,000 — and then a
        general's 5,000 past the band of 48,750."""
        from backend.models.world_state import severe_band_threshold
        assert jena.get_force_limit("Naples") == 32_500
        assert severe_band_threshold(32_500) == 48_750
        assert RC._preparing_for_design(jena, "Naples") is True
        candidate = RC.get_marshal_pool(jena, "Naples")[0]
        assert (candidate["name"], RC.corps_requirement(candidate)) == ("Philippsthal", ("infantry", 5000))
        _naples_can_commission(jena, 48_000)
        assert RC.commission_over_the_ceiling(jena, "Naples", candidate) is True
        with _quiet():
            assert RC.find_ai_commission(jena, "Naples", 60_000) is None
        with pytest.MonkeyPatch.context() as m:
            hold_down(m, T3_SEAMS_BY_ROW["G4-CEILING"])
            with _quiet():
                action = RC.find_ai_commission(jena, "Naples", 60_000)
        assert action and (action["action"], action["target"]) == ("recruit_marshal", "Philippsthal")

    def test_under_the_band_she_still_commissions(self, jena):
        _naples_can_commission(jena, 40_000)
        with _quiet():
            action = RC.find_ai_commission(jena, "Naples", 60_000)
        assert action and action["target"] == "Philippsthal"

    def test_the_players_own_commission_is_not_gated(self):
        """The decision layer only (GR5's shared executor is untouched): the
        read sits in the AI's rung and nowhere else."""
        callers = sorted(
            p.relative_to(REPO).as_posix() for p in (REPO / "backend").rglob("*.py")
            if "commission_over_the_ceiling(" in p.read_text(encoding="utf-8"))
        assert callers == ["backend/game_logic/recruitment.py"]
        assert "commission_over_the_ceiling" not in inspect.getsource(RC.check_commission)


# ═══════════════════════════════════════════════════════════════════════
# 9 — ALLY: the Emperor's ally takes no separate peace while it is winning
# ═══════════════════════════════════════════════════════════════════════

def _pair_score(world, loser: str, winner: str, score: int) -> None:
    pair = world._make_diplo_key(loser, winner)
    world.war_scores[pair] = score if pair.split("|")[0] == loser else -score


class TestTheEmperorsAllyTakesNoSeparatePeace:
    def test_vienna_sues_munich_and_munich_refers_her_to_the_emperor(self, world):
        world.current_turn = 12
        _pair_score(world, "Austria", "Bavaria", -60)
        assert TP.ally_stands_by_the_emperor(world, "Bavaria", "Austria") is True
        assert TP.sub_pair_loser_sues(world, "Austria", "Bavaria", 1) is None
        with pytest.MonkeyPatch.context() as m:
            hold_down(m, T3_SEAMS_BY_ROW["G4-ALLY"])
            assert TP.sub_pair_loser_sues(world, "Austria", "Bavaria", 1) == ("Austria", "Bavaria", -60)

    def test_a_beaten_ally_may_still_be_knocked_out(self, world):
        world.current_turn = 12
        _pair_score(world, "Bavaria", "Austria", -60)
        assert TP.ally_stands_by_the_emperor(world, "Austria", "Bavaria") is False
        assert TP.sub_pair_loser_sues(world, "Austria", "Bavaria", 1) == ("Bavaria", "Austria", -60)

    def test_the_emperors_own_peace_frees_the_pair(self, world):
        world.current_turn = 12
        _pair_score(world, "Austria", "Bavaria", -60)
        _set_state(world, "France", "Austria", "PEACE")
        assert TP.ally_stands_by_the_emperor(world, "Bavaria", "Austria") is False
        assert TP.sub_pair_loser_sues(world, "Austria", "Bavaria", 1) == ("Austria", "Bavaria", -60)

    def test_the_read_is_the_allys_alone(self, world):
        # two courts that are not the Emperor's allies
        assert TP.ally_stands_by_the_emperor(world, "Austria", "Russia") is False
        # his client's road is its own rule (`client_pair_is_the_lords_war`)
        assert TP.ally_stands_by_the_emperor(world, "Holland", "Austria") is False
        # never the Emperor's own pair
        assert TP.ally_stands_by_the_emperor(world, "France", "Austria") is False
        assert TP.ally_stands_by_the_emperor(world, "Bavaria", "France") is False

    def test_her_held_aim_waits_for_his_treaty_too(self):
        source = inspect.getsource(TP.held_aim_suit)
        assert "ally_stands_by_the_emperor(world, winner, loser)" in source
        assert "ally_stands_by_the_emperor(world, winner, loser)" in inspect.getsource(TP.sub_pair_loser_sues)


# ═══════════════════════════════════════════════════════════════════════
# 10 — GUNS: no guns from a sanctuary
# ═══════════════════════════════════════════════════════════════════════

def _gun_park(world, owner_state: str = "PEACE"):
    """The played board's turn 20: a British battery on Austrian Carniola,
    France at peace with Austria, a French corps in Bohemia next door."""
    from backend.models.marshal import Marshal
    guns = Marshal(name="Shrapnel", strength=2000, location="Carniola", nation="Britain",
                   personality="cautious")
    guns.artillery = True
    world.marshals["Shrapnel"] = guns
    world.regions["Bohemia"].controller = "France"
    lannes = world.marshals["Lannes"]
    lannes.location = "Bohemia"
    _set_state(world, "France", "Austria", owner_state)
    _flush(world)
    assert world.regions["Carniola"].controller == "Austria"
    assert "Bohemia" in world.regions["Carniola"].adjacent_regions
    return guns, lannes


class TestNoGunsFromASanctuary:
    def test_the_read(self, world):
        guns, lannes = _gun_park(world)
        assert CE.fires_from_a_sanctuary(world, guns, "France") == "Austria"
        # the owner at war with the target: co-belligerent ground, no sanctuary
        _set_state(world, "France", "Austria", "WAR")
        assert CE.fires_from_a_sanctuary(world, guns, "France") == ""
        _set_state(world, "France", "Austria", "PEACE")
        # the firer's own soil, and the target's own
        world.regions["Carniola"].controller = "Britain"
        assert CE.fires_from_a_sanctuary(world, guns, "France") == ""
        world.regions["Carniola"].controller = "France"
        assert CE.fires_from_a_sanctuary(world, guns, "France") == ""
        # the target's client's soil is the target's house
        world.regions["Carniola"].controller = "KingdomOfItaly"
        assert CE.fires_from_a_sanctuary(world, guns, "France") == ""

    def test_the_battery_is_refused_with_words(self, world):
        from backend.commands.executor import CommandExecutor
        guns, lannes = _gun_park(world)
        before = int(lannes.strength)
        with _quiet():
            result = CommandExecutor()._execute_bombardment(guns, lannes, world, {"world": world})
        assert result["success"] is False
        assert result["message"] == (
            "Shrapnel's guns stand on the soil of Austria, which is at peace with France — no "
            "battery opens fire from neutral ground.")
        assert int(lannes.strength) == before

    def test_the_seam_down_he_shells_from_neutral_ground(self, world, monkeypatch):
        from backend.commands.executor import CommandExecutor
        hold_down(monkeypatch, T3_SEAMS_BY_ROW["G4-GUNS"])
        guns, lannes = _gun_park(world)
        with _quiet():
            result = CommandExecutor()._execute_bombardment(guns, lannes, world, {"world": world})
        assert result["success"] is True

    def test_the_emperors_guns_are_bound_alike(self, world):
        """GR5: a French battery on a neutral's soil is refused the same."""
        from backend.commands.executor import CommandExecutor
        from backend.models.marshal import Marshal
        battery = Marshal(name="Senarmont", strength=3000, location="Dresden", nation="France",
                          personality="aggressive")
        battery.artillery = True
        world.marshals["Senarmont"] = battery
        target = next(m for m in world.marshals.values() if m.nation == "Austria" and m.strength > 0)
        target.location = "Bohemia"
        _flush(world)
        assert world.regions["Dresden"].controller == "Saxony"
        assert "Bohemia" in world.regions["Dresden"].adjacent_regions
        assert CE.fires_from_a_sanctuary(world, battery, "Austria") == "Saxony"
        with _quiet():
            result = CommandExecutor()._execute_bombardment(battery, target, world, {"world": world})
        assert result["success"] is False and "neutral ground" in result["message"]

    def test_the_ai_scores_no_order_it_cannot_give(self):
        from backend.ai import enemy_ai
        source = Path(enemy_ai.__file__).read_text(encoding="utf-8")
        assert source.count("_fires_from_a_sanctuary(world, marshal, e") == 2      # P4's skip, P7's stay
        assert "fires_from_a_sanctuary(world, marshal, getattr(defender" in inspect.getsource(
            CE.CombatExecutor._execute_bombardment)


# ═══════════════════════════════════════════════════════════════════════
# 11 — WAGON: a bandwagoner joins a neighbour's war
# ═══════════════════════════════════════════════════════════════════════

class TestABandwagonerJoinsANeighboursWar:
    def test_reach_is_the_houses_frontier(self, world):
        assert WC.bandwagon_in_reach(world, "Prussia", "PapalStates") is False
        assert WC.bandwagon_in_reach(world, "Prussia", "Naples") is False
        assert WC.bandwagon_in_reach(world, "Prussia", "Hanover") is True
        assert WC.bandwagon_in_reach(world, "Prussia", "Sweden") is True
        # a client's frontier is its lord's house's: Milan borders Austria
        assert WC.bandwagon_in_reach(world, "France", "Austria") is True

    def test_the_seam_down_reaches_anywhere(self, world, monkeypatch):
        hold_down(monkeypatch, T3_SEAMS_BY_ROW["G4-WAGON"])
        assert WC.bandwagon_in_reach(world, "Prussia", "PapalStates") is True

    def test_the_join_itself(self, world, monkeypatch):
        """T2-3's own staging: Sweden against Denmark. Prussia has no
        frontier with Denmark and stays out; when Sweden is the weaker side
        the enemy is at her door and she joins."""
        from tests.test_t2_3_prussias_hook import STRENGTHS, _set_relation, _stage_war
        monkeypatch.setattr(WC, "_standing_strength", lambda w, n: int(STRENGTHS.get(n, 10000)))
        STRENGTHS.clear()
        STRENGTHS.update({"Sweden": 100000, "Denmark": 20000, "Prussia": 60000})
        _stage_war(world, "Sweden", "Denmark")
        _set_relation(world, "Prussia", "Denmark", -30)
        with _quiet():
            assert WC.process_bandwagon(world) == []
        STRENGTHS.update({"Sweden": 20000, "Denmark": 100000})
        _set_relation(world, "Prussia", "Sweden", -30)
        with _quiet():
            events = WC.process_bandwagon(world)
        assert [(e["type"], e["against"], e["beside"]) for e in events] == [
            ("ai_bandwagon_joined", "Sweden", "Denmark")]
        STRENGTHS.clear()

    def test_the_join_asks_it_before_the_declaration(self):
        source = inspect.getsource(WC._bandwagon_join)
        reach = source.index("bandwagon_in_reach(world, nation, enemy)")
        assert reach < source.index("can_declare_war(world, nation, enemy)")


# ═══════════════════════════════════════════════════════════════════════
# 12 — the dispatch drops a capture the morning has overtaken
# ═══════════════════════════════════════════════════════════════════════

def _capture(world, region: str, by: str, frm: str) -> None:
    world.event_log.append({"type": "region_captured", "region": region, "captured_by": by,
                            "captured_from": frm, "turn": int(world.current_turn)})


def _candidates(*pairs):
    return [{"class": cls, "identity": f"{cls}:{region}", "text": cls} for cls, region in pairs]


class TestTheDispatchDropsWhatTheMorningOvertook:
    def test_vienna_taken_and_lost_again_is_no_tricolor(self, world):
        world.current_turn = 12
        _capture(world, "Vienna", "France", "Austria")
        _capture(world, "Vienna", "Austria", "France")
        rows = _candidates(("capital_stormed", "Vienna"), ("region_lost", "Vienna"),
                           ("region_taken", "Moravia"))
        DP._drop_overtaken_captures(world, "France", rows)
        assert [c["class"] for c in rows] == ["region_lost", "region_taken"]

    def test_lost_and_retaken_is_no_wound(self, world):
        world.current_turn = 12
        _capture(world, "Bohemia", "Austria", "France")
        _capture(world, "Bohemia", "France", "Austria")
        rows = _candidates(("region_lost", "Bohemia"), ("region_taken", "Bohemia"))
        DP._drop_overtaken_captures(world, "France", rows)
        assert [c["class"] for c in rows] == ["region_taken"]

    def test_an_allys_hand_is_our_side(self, world):
        world.current_turn = 12
        _capture(world, "Munich", "Austria", "Bavaria")
        _capture(world, "Munich", "Bavaria", "Austria")
        rows = _candidates(("home_captured", "Munich"))
        DP._drop_overtaken_captures(world, "France", rows)
        assert rows == []

    def test_a_single_capture_stands_and_old_ones_do_not_vote(self, world):
        world.current_turn = 12
        world.event_log.append({"type": "region_captured", "region": "Vienna", "captured_by": "Austria",
                                "captured_from": "France", "turn": 5})       # outside the window
        _capture(world, "Vienna", "France", "Austria")
        rows = _candidates(("capital_stormed", "Vienna"))
        DP._drop_overtaken_captures(world, "France", rows)
        assert [c["class"] for c in rows] == ["capital_stormed"]

    def test_the_morning_itself(self, world):
        """Through the headline builder: the played campaign's turn 12."""
        world.current_turn = 12
        _capture(world, "Vienna", "France", "Austria")
        with _quiet():
            taken = DP._build_headline(world, "France", record=False)
        assert "tricolor flies over it" in json.dumps(taken, default=str)
        _capture(world, "Vienna", "Austria", "France")
        with _quiet():
            lost = DP._build_headline(world, "France", record=False)
        assert "tricolor flies over it" not in json.dumps(lost, default=str)


# ═══════════════════════════════════════════════════════════════════════
# 13 — the crown row leads the demands
# ═══════════════════════════════════════════════════════════════════════

def _row(label: str, group: str = "demand", **extra):
    return dict({"label": label, "group": group}, **extra)


class TestTheCrownLeadsTheDemands:
    def test_the_order(self):
        from backend.game_logic.settlement_staging import _crowns_first
        rows = [_row("Declared at the war: Tyrol", declared=True), _row("Cede Bohemia"),
                _row("Indemnity"), _row("An offer", "offer"),
                _row("Erect Hungary", crown="King of Hungary", available=True),
                _row("Erect Illyria", crown="Illyrian Provinces", available=False)]
        out = _crowns_first(rows)
        assert [r["label"] for r in out] == [
            "Declared at the war: Tyrol", "Erect Hungary", "Cede Bohemia", "An offer",
            "Indemnity", "Erect Illyria"]
        assert sorted(map(id, out)) == sorted(map(id, rows))       # the same rows, reordered

    def test_a_conceding_courts_offers_keep_the_head(self):
        from backend.game_logic.settlement_staging import _crowns_first
        rows = [_row("An offer", "offer"), _row("Cede Bohemia"),
                _row("Erect Hungary", crown="King of Hungary", available=True)]
        assert [r["label"] for r in _crowns_first(rows)] == ["An offer", "Erect Hungary", "Cede Bohemia"]

    def test_no_crown_no_change(self):
        from backend.game_logic.settlement_staging import _crowns_first
        rows = [_row("Cede Bohemia"), _row("An offer", "offer"), _row("A plain carve", available=True)]
        assert _crowns_first(rows) is rows

    def test_the_table_is_served_through_it(self):
        from backend.game_logic import settlement_staging as SS
        source = Path(SS.__file__).read_text(encoding="utf-8")
        assert source.count("_crowns_first(_court_demand_suggestions(") == 1
        # the builder itself sits at the 500-line ratchet: the reorder is a wrapper
        assert "_crowns_first" not in inspect.getsource(SS._court_demand_suggestions)


# ═══════════════════════════════════════════════════════════════════════
# 14 — no "§" in the sponsor chip
# ═══════════════════════════════════════════════════════════════════════

class TestTheChipNamesNoSection:
    def test_the_cabinets_chips_carry_no_section_sign(self, world):
        from backend.game_logic.diplomacy import get_available_diplomatic_actions
        for court in ("Prussia", "Russia", "Austria", "Hanover"):
            with _quiet():
                chips = get_available_diplomatic_actions(world, court)
            assert not [c for c in chips if "§" in json.dumps(c, ensure_ascii=False, default=str)], court
        with _quiet():
            sponsor = [c for c in get_available_diplomatic_actions(world, "Prussia")
                       if c.get("action") == "sponsor_design"][0]
        assert sponsor["effect_text"].startswith(
            "Aim their court at Hanover — gold flows, the compact binds both ends. ")


# ═══════════════════════════════════════════════════════════════════════
# HOUSE — the DD-1 treaty fuzzer's catch: Swiss neutrality and a defector
# ═══════════════════════════════════════════════════════════════════════

def _saxony_under_britain(world) -> None:
    """The fuzzed board's shape, crafted clean: a court that answers to
    Britain and stands outside the Emperor's war, a turn before it strikes."""
    world.vassals["Saxony"] = dict(world.vassals["Holland"], lord="Britain")
    _set_state(world, "Britain", "Saxony", "VASSAL")
    _flush(world)


class TestAClientKeepsItsPeaceWithAHouse:
    def test_the_boot_fact_the_rule_stands_on(self, world):
        """Switzerland is the Emperor's client and no party to his war with
        Britain (the Act of Mediation's neutrality); Holland is."""
        assert world.vassals["Switzerland"]["lord"] == "France"
        assert _state(world, "France", "Britain") == "WAR"
        assert _state(world, "Switzerland", "Britain") == "PEACE"
        assert _state(world, "Holland", "Britain") == "WAR"

    def test_the_read(self, world):
        _saxony_under_britain(world)
        assert DI.client_keeps_its_peace_with_the_house(world, "Switzerland", "Saxony") is True
        assert DI.client_keeps_its_peace_with_the_house(world, "Holland", "Saxony") is False
        # a free aggressor has no house but its own
        assert DI.client_keeps_its_peace_with_the_house(world, "Switzerland", "Austria") is False
        # a REBEL of the joiner's own house (his row stands while the cascade
        # runs) is no foreign lord's client: the loyal clients march on him
        assert DI.client_keeps_its_peace_with_the_house(world, "KingdomOfItaly", "Switzerland") is False
        assert DI.client_keeps_its_peace_with_the_house(world, "Holland", "Switzerland") is False

    def test_the_neutral_client_stays_out_and_the_belligerent_one_marches(self, world, monkeypatch):
        # Session G5 re-cut this rule (a client now takes up her lord's war
        # with the house and rallies — `tests/test_session_g5_a_client_rallies.py`);
        # this pin reads session G4's own tree, the later seam held down.
        hold_down(monkeypatch, T3_SEAMS_BY_ROW["G5-RALLY"])
        _saxony_under_britain(world)
        with _quiet():
            result = DI.declare_war(world, "Saxony", "France")
        assert result["success"] is True
        assert _state(world, "Saxony", "France") == "WAR"
        assert _state(world, "Holland", "Saxony") == "WAR"
        assert _state(world, "Switzerland", "Saxony") == "PEACE"
        # the fuzzer's own invariant: Britain's client fights no court Britain is at peace with
        for court in ("Holland", "KingdomOfItaly", "Switzerland"):
            if _state(world, "Saxony", court) == "WAR":
                assert _state(world, "Britain", court) == "WAR", court

    def test_the_seam_down_she_is_dragged_in(self, world, monkeypatch):
        hold_down(monkeypatch, T3_SEAMS_BY_ROW["G4-HOUSE"])
        _saxony_under_britain(world)
        with _quiet():
            DI.declare_war(world, "Saxony", "France")
        assert _state(world, "Switzerland", "Saxony") == "WAR"
        assert _state(world, "Britain", "Switzerland") == "PEACE"       # the fuzzer's I2

    def test_the_fuzzers_ledger_is_still_empty(self):
        """The class this closes: the DD-1 treaty fuzzer's I2, held at zero
        since S7 (`tests/test_dd1_treaty_fuzzer.py` runs the two seeds)."""
        ledger = json.loads((REPO / "tests" / "data" / "treaty_fuzzer_known_violations.json")
                            .read_text(encoding="utf-8"))
        assert ledger == {}


# ═══════════════════════════════════════════════════════════════════════
# Found in passing — the counter's dry run on a draft with no clauses list
# ═══════════════════════════════════════════════════════════════════════

class TestTheCounterDraftWithoutClauses:
    """The unattended board reported "treaty.counter_verdict: the dry run --
    KeyError: 'clauses'" (session G3's tree too): a court whose desire table
    reaches a protection or open-borders clause appended to a list the
    draft did not carry, and the Counter button's verdict was lost to it."""

    def test_the_desire_is_added_to_a_draft_that_had_no_list(self, world):
        from backend.game_logic import ai_diplomacy as AD
        assert ("protection", "protection_promised") in [
            (d.get("type"), d.get("clause")) for d in AD.NATION_DESIRES["Saxony"]]
        terms = {"type": "peace", "proposer_nation": "France", "target_nation": "Saxony",
                 "demands": [], "sweeteners": []}
        with _quiet():
            out = AD._try_add_desired_clauses(terms, "Saxony", world, accept_threshold=-1000)
        assert out is not None and out["clauses"] == ["protection_promised"]
        assert "clauses" not in terms                   # the caller's draft is a copy's source

    def test_a_draft_that_has_the_clause_is_left_alone(self, world):
        from backend.game_logic import ai_diplomacy as AD
        terms = {"type": "peace", "proposer_nation": "France", "target_nation": "Saxony",
                 "demands": [], "sweeteners": [], "clauses": ["protection_promised"]}
        with _quiet():
            out = AD._try_add_desired_clauses(terms, "Saxony", world, accept_threshold=-1000)
        assert out is None or out["clauses"].count("protection_promised") == 1


# ═══════════════════════════════════════════════════════════════════════
# The seams
# ═══════════════════════════════════════════════════════════════════════

class TestTheSeams:
    def test_every_rule_has_its_row_and_ships_up(self):
        assert tuple(SEAMS) == ROWS
        for row, seam in SEAMS.items():
            assert seam() is True, row
            assert inspect.signature(seam).parameters == {}, row
            spec = T3_SEAMS_BY_ROW[row]
            assert len(spec) == 1 and spec[0] == f"{seam.__module__}:{seam.__name__}=False", row

    def test_the_rows_join_the_recorded_boards_hold_list(self):
        from tests._oct27_seams import OCT27_SEAMS_DOWN
        for row in ROWS:
            assert T3_SEAMS_BY_ROW[row][0] in OCT27_SEAMS_DOWN

    def test_each_row_holds_its_own_seam_down(self):
        for row, seam in SEAMS.items():
            with pytest.MonkeyPatch.context() as m:
                hold_down(m, T3_SEAMS_BY_ROW[row])
                module = sys.modules[seam.__module__]
                assert getattr(module, seam.__name__)() is False, row


def _record(name: str) -> dict:
    return json.loads((REPO / "tools" / name).read_text(encoding="utf-8"))


def _dump(row) -> str:
    return json.dumps(row, sort_keys=True)


# ═══════════════════════════════════════════════════════════════════════
# The session's measure — ONE sweep, eleven arms, three surfaces, the series
# (`tools/_g4_measure.py`, `tools/_g4_series_arms.py`). Seeded paths, not
# laws (DYNAMISM_SPEC.md §7d; SYSTEMS_REFERENCE.md §210).
# ═══════════════════════════════════════════════════════════════════════

SEEDS = ("austerlitz", "eylau", "friedland", "historical", "jena", "lodi",
         "marengo", "rivoli", "ulm", "wagram")
STAMP = "2026_11_11"
ARM_NAMES = ("0", "FORM", "WON", "LAPSE", "REAR", "CEILING", "ALLY", "GUNS", "WAGON", "HOUSE", "ALL")
LABELS = dict({"0": "g4_control", "ALL": "g4"},
              **{name: f"g4_{name.lower()}" for name in ARM_NAMES[1:-1]})


class TestTheSessionG4Measure:
    """Written from the records after the sweep ran ALONE. Arm 0 reproduces
    session G3; each further arm raises one rule; ALL is the shipped tree."""

    def _sig(self, label: str) -> dict:
        return _record(f"_dy_signature_{label}_{STAMP}.json")

    def _census(self, label: str) -> dict:
        return _record(f"_{label}_census_{STAMP}.json")

    def _harness(self) -> dict:
        return _record(f"_g4_chain_d_{STAMP}.json")

    def _ambient_movers(self):
        prev, out = self._sig("g3"), {}
        for arm in ARM_NAMES:
            cur = self._sig(LABELS[arm])
            out[arm] = [s for s in SEEDS if _dump(cur["seeds"][s]["signature"])
                        != _dump(prev["seeds"][s]["signature"])]
            prev = cur
        return out

    def test_arm_0_reproduces_session_g3_on_both_surfaces(self):
        g3, ctl = self._sig("g3"), self._sig("g4_control")
        for seed in SEEDS:
            assert _dump(ctl["seeds"][seed]) == _dump(g3["seeds"][seed]), seed
        assert _dump(self._census("g4_control")["seeds"]) == _dump(self._census("g3")["seeds"])
        prior = _record(f"_g3_chain_d_{STAMP}.json")["arms"]["CLIENT"]
        assert _dump(self._harness()["arms"]["0"]) == _dump(prior)

    def test_the_unattended_board_arm_by_arm(self):
        """Six rules move no unattended seed; four do, each named."""
        assert self._ambient_movers() == {
            "0": [], "FORM": [], "WON": [], "LAPSE": [], "REAR": [],
            "CEILING": ["friedland", "lodi", "marengo", "rivoli", "ulm"],
            "ALLY": [], "GUNS": ["rivoli"], "WAGON": ["jena"],
            "HOUSE": ["friedland", "historical"], "ALL": []}
        assert all(self._sig(LABELS[arm])["story_class_count"] == 10 for arm in ARM_NAMES)

    def test_the_gate_reads_met_on_the_shipped_arm(self):
        shipped, census = self._sig("g4"), self._census("g4")
        assert shipped["story_class_count"] == 10
        promoted = {s: shipped["seeds"][s]["signature"]["rank_promotions"] for s in SEEDS
                    if shipped["seeds"][s]["signature"]["rank_promotions"]}
        assert promoted == {"lodi": [[33, "Hesse"]]}
        rosters = {s: tuple(n for _, n in shipped["seeds"][s]["signature"]["eliminations"]) for s in SEEDS}
        assert rosters["friedland"] == ()
        assert sorted(s for s, r in rosters.items() if r == ("KingdomOfItaly", "PapalStates")) == ["jena", "wagram"]
        assert len(set(rosters.values())) == 3
        assert census["totals"]["annexations_outside_aim"] == 0
        assert (census["totals"]["captures_outside_aim"], census["totals"]["rank_promotions"],
                census["totals"]["crowns_erected"]) == (266, 1, 0)
        assert all(shipped["seeds"][s]["signature"]["formations"] == [] for s in SEEDS)

    def test_the_ceiling_costs_marengos_crown(self):
        """REPORTED. Until the ceiling's arm both of session G's promotions
        stand; with it Hesse's Grand Ducal Title on marengo — enacted at
        turn 40, the window's last — no longer falls inside the forty turns
        (the cast Saxony, at her band, commissions no second general and the
        seed's wars re-time). The promotion clause rests on lodi alone."""
        before, after = self._sig("g4_rear"), self._sig("g4_ceiling")
        assert before["seeds"]["marengo"]["signature"]["rank_promotions"] == [[40, "Hesse"]]
        assert after["seeds"]["marengo"]["signature"]["rank_promotions"] == []
        for label in ("g4_rear", "g4_ceiling", "g4"):
            assert self._sig(label)["seeds"]["lodi"]["signature"]["rank_promotions"] == [[33, "Hesse"]]
        assert [self._census(LABELS[a])["totals"]["rank_promotions"] for a in ARM_NAMES] == [
            2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1]

    def test_the_neutral_client_saves_friedlands_kingdom(self):
        """HOUSE on friedland: Britain buys Switzerland at 9 and she marches
        on France; the Kingdom of Italy, at peace with Britain, no longer
        joins that war — and is not erased at 23."""
        before, after = self._sig("g4_wagon"), self._sig("g4_house")
        assert before["seeds"]["friedland"]["signature"]["eliminations"] == [[23, "KingdomOfItaly"]]
        assert after["seeds"]["friedland"]["signature"]["eliminations"] == []

    def test_the_bandwagoner_leaves_rome_alone_on_jena(self):
        before, after = self._sig("g4_guns"), self._sig("g4_wagon")
        assert before["seeds"]["jena"]["signature"]["eliminations"] == [[7, "KingdomOfItaly"], [26, "PapalStates"]]
        assert after["seeds"]["jena"]["signature"]["eliminations"] == [[7, "KingdomOfItaly"], [19, "PapalStates"]]
        assert len(after["seeds"]["jena"]["signature"]["war_turns"]) > len(
            before["seeds"]["jena"]["signature"]["war_turns"])

    def test_the_harness_arm_by_arm(self):
        mine = self._harness()
        prev, moved = "0", {}
        for arm in ARM_NAMES:
            moved[arm] = [s for s in SEEDS if _dump(mine["arms"][arm][s]) != _dump(mine["arms"][prev][s])]
            prev = arm
        assert moved == {
            "0": [], "FORM": ["austerlitz", "friedland", "historical", "marengo", "ulm"],
            "WON": [], "LAPSE": [], "REAR": [], "CEILING": ["austerlitz", "lodi"],
            "ALLY": ["eylau", "historical", "lodi", "wagram"], "GUNS": [],
            "WAGON": ["jena", "wagram"], "HOUSE": ["lodi"], "ALL": []}
        for arm in ARM_NAMES:
            totals = mine["totals"][arm]
            assert (totals["annexations_outside_aim"], totals["rank_promotions"],
                    totals["crowns_erected"]) == (0, 0, 0), arm
        assert [mine["totals"][a]["captures_outside_aim"] for a in ARM_NAMES] == [
            135, 138, 138, 138, 138, 138, 139, 139, 134, 140, 140]

    def test_the_harness_frances_provinces(self):
        mine = self._harness()
        final = {a: {s: mine["arms"][a][s]["france_provinces_final"] for s in SEEDS} for a in ("0", "ALL")}
        assert {s: (final["0"][s], final["ALL"][s]) for s in SEEDS if final["0"][s] != final["ALL"][s]} == {
            "eylau": (36, 38), "historical": (43, 44), "lodi": (46, 38), "marengo": (46, 45),
            "wagram": (44, 43)}
        # lodi is HOUSE's: Holland, no longer called against Britain's bought
        # Swiss, drifts from the harness's France and rises at 32
        assert mine["arms"]["WAGON"]["lodi"]["france_provinces_final"] == 46
        assert mine["arms"]["HOUSE"]["lodi"]["france_provinces_final"] == 38
        assert mine["arms"]["WAGON"]["lodi"]["formations"] == []
        assert mine["arms"]["HOUSE"]["lodi"]["formations"] == ["Holland"]

    def test_a_freed_kingdom_turns_on_rome_and_no_measured_arm_proclaims_italy(self):
        """FORM on the harness: the kingdom goes free of the harness's France
        at turn 22-28, asks Rome, and Naples answers for the Pope; on ulm she
        is beaten to her last province and signs at 40. Forty turns are too
        few from there — Italy is proclaimed on no measured arm (freed at the
        boot, she proclaims on three of five played seeds: §7d)."""
        mine = self._harness()
        assert [(a, s) for a in ARM_NAMES for s in SEEDS
                if "KingdomOfItaly" in mine["arms"][a][s]["formations"]] == []
        refuge = mine["arms"]["FORM"]["ulm"]["last_refuges"]
        assert [(r[0], r[1], r[2]) for r in refuge] == [(40, "KingdomOfItaly", "Naples")]
        assert mine["arms"]["0"]["ulm"]["last_refuges"] == []
        assert sorted(s for s in SEEDS if "Holland" in mine["arms"]["ALL"][s]["formations"]) == [
            "austerlitz", "eylau", "friedland", "lodi", "marengo", "wagram"]

    def test_the_band_stays_inside_its_guard(self):
        band = _record(f"_g4_band_{STAMP}.json")
        rows = {arm: [band["arms"][arm][n]["provinces"] for n in ("CMD-H", "CMD-A", "CMD-M")]
                for arm in ARM_NAMES}
        for arm in ("0", "FORM", "WON", "LAPSE", "REAR", "CEILING"):
            assert rows[arm] == [28, 27, 25], arm
        assert rows["ALLY"] == [26, 27, 25]             # the ally stands: the commanded H arm two down
        for arm in ("GUNS", "WAGON", "HOUSE", "ALL"):
            assert rows[arm] == [26, 26, 25], arm        # the guns: the A arm one down
        assert all(23 <= p <= 28 for row in rows.values() for p in row)

    def test_the_series_does_not_move_and_two_rules_bite_on_the_rig(self):
        series = _record("_g4_series_arms_final.json")
        for arm in ARM_NAMES:
            row = series["arms"][arm]
            assert row["first_divergence_vs_prior"] is None, arm
            assert row["series"] == series["prior"], arm
        reach = {arm: series["arms"][arm]["reach"]["counts"] for arm in ARM_NAMES}
        assert [reach[a]["rear_bites"] for a in ARM_NAMES] == [0, 0, 0, 0, 76, 76, 76, 76, 76, 76, 76]
        assert [reach[a]["house_bites"] for a in ARM_NAMES] == [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1]
        for key in ("ally_bites", "guns_bites", "wagon_bites", "ceiling_bites", "lapse_bites",
                    "king_bites", "form_proclaims"):
            assert {reach[a][key] for a in ARM_NAMES} == {0}, key
        assert reach["ALL"]["won_seam_reads"] > 3000 and reach["ALL"]["rear_seam_reads"] > 500
