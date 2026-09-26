"""Score Mandate Chunk 2 — the quick-win reserve (`docs/SCORE_MANDATE_PLAN.md`
§3; September 26, 2026): AAR-22, AAR-16, AAR-30, AAR-18, AAR-14, AAR-13.

Every pin binds to the production line it names (`tools/_sweep_sr2_reserve.json`);
each rule with a lever has its lever-down pin, so the old behaviour is
reproduced, not remembered.
"""
import contextlib
import io
from pathlib import Path

import pytest

import backend.ai.question_desk as QD
import backend.commands.economy_executor as EC
import backend.game_logic.dispatch as D
import backend.models.world_state as WS
from backend.campaign_log import format_event_oneliner
from backend.commands.executor import CommandExecutor
from backend.commands.naval_executor import intercepted_at_sea_line
from backend.models.intel import FULL
from backend.models.world_state import WorldState
from tests.conftest import MarshalFactory, WorldFactory

SCENARIO_PATH = (Path(__file__).resolve().parents[1] / "godot-client"
                 / "project-sovereign" / "assets" / "maps" / "europe_1805.json")


@pytest.fixture
def europe():
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(str(SCENARIO_PATH))


def _execute(world, command, original):
    parsed = {"command": command, "original_command": original}
    with contextlib.redirect_stdout(io.StringIO()):
        return CommandExecutor().execute(parsed, {"world": world})


def _war(world, a, b):
    key = world._make_diplo_key(a, b)
    world.diplomatic_states[key] = "WAR"
    world.war_start_turns[key] = world.current_turn


# ═══════════════════════════════════════════════════════════════════════
# AAR-22 — raw tags and in-place walk-ins in copy
# ═══════════════════════════════════════════════════════════════════════

class TestAAR22TheCopy:

    def test_the_guarantee_refusal_prints_the_court(self, europe):
        """"KingdomOfItaly is already under French protection" — the raw
        scenario tag reached the terminal on the guarantee refusal."""
        assert europe.vassals["KingdomOfItaly"]["lord"] == "France"
        result = _execute(europe, {"action": "guarantee_nation",
                                   "target": "KingdomOfItaly"},
                          "guarantee Kingdom of Italy")
        assert result["success"] is False
        message = result["message"]
        assert message.startswith(
            "Kingdom of Italy is already under French protection as a vassal.")
        assert "KingdomOfItaly" not in message

    def test_the_covering_court_is_an_adjective(self):
        """"the Britain squadrons" → "the British squadrons"."""
        line = intercepted_at_sea_line(
            {"coverer": "Britain", "troops_lost": 1200, "odds": 40},
            "Ney", "Munster")
        assert "the British squadrons catch the transports off Munster" in line
        assert "Britain squadrons" not in line
        assert "Ney loses 1,200 men" in line

    def test_the_covering_court_falls_back_to_the_enemy(self):
        assert "the enemy squadrons" in intercepted_at_sea_line(
            {"coverer": "", "troops_lost": 0}, "Ney", "Munster")

    def test_a_corps_takes_the_province_where_it_stands(self, europe):
        """"Kutuzov marches from Bohemia into Bohemia unopposed!" — a corps
        already standing on an undefended enemy province does not march."""
        bohemia = europe.get_region("Bohemia")
        assert bohemia.controller == "Austria"
        assert bohemia.garrison_strength == 0
        assert europe.is_at_war("France", "Austria")
        assert not [m for m in europe.marshals.values()
                    if m.location == "Bohemia"]
        ney = europe.get_marshal("Ney")
        ney.location = "Bohemia"
        result = _execute(europe, {"action": "attack", "marshal": "Ney",
                                   "target": "Bohemia"}, "Ney, attack Bohemia")
        message = result.get("message") or ""
        assert result.get("success") is True, message
        assert "Ney takes Bohemia where he stands!" in message
        assert "from Bohemia into Bohemia" not in message

    def test_an_ordinary_walk_in_still_marches(self, europe):
        hungary = europe.get_region("Hungary")
        assert hungary.controller == "Austria" and hungary.garrison_strength == 0
        assert not [m for m in europe.marshals.values()
                    if m.location == "Hungary"]
        ney = europe.get_marshal("Ney")
        ney.location = "Bohemia"
        result = _execute(europe, {"action": "attack", "marshal": "Ney",
                                   "target": "Hungary"}, "Ney, attack Hungary")
        message = result.get("message") or ""
        assert result.get("success") is True, message
        assert "Ney marches from Bohemia into Hungary unopposed!" in message


# ═══════════════════════════════════════════════════════════════════════
# AAR-16 — foreign constructions name their owner
# ═══════════════════════════════════════════════════════════════════════

def _completed(world, region_name, building="market"):
    region = world.get_region(region_name)
    region.building_under_construction = {"type": building, "turns_remaining": 1}
    events = world.process_construction_timers()
    return [e for e in events if e.get("region") == region_name][0]


class TestAAR16ForeignWorksNameTheirOwner:

    def test_a_foreign_construction_names_its_owner(self, europe):
        """"[tactical] Construction complete: Market in Vienna!" — Austria's
        market, printed in the player's terminal as if ours."""
        event = _completed(europe, "Vienna")
        assert event["nation"] == "Austria"
        assert event["message"] == "Austria completes a market at Vienna."

    def test_our_own_keeps_its_receipt(self, europe):
        event = _completed(europe, "Paris")
        assert event["nation"] == "France"
        assert event["message"] == "Construction complete: Market in Paris!"

    def test_a_multi_word_building_and_a_plural_one(self, europe):
        assert (_completed(europe, "Vienna", "supply_depot")["message"]
                == "Austria completes a supply depot at Vienna.")
        assert (_completed(europe, "Tyrol", "stables")["message"]
                == "Austria completes stables at Tyrol.")

    def test_the_watchtower_arm_reads_the_same_builder(self, europe):
        vienna = europe.get_region("Vienna")
        vienna.watchtower = "under_construction"
        vienna.watchtower_turns_remaining = 1
        events = [e for e in europe.process_construction_timers()
                  if e.get("region") == "Vienna"]
        assert events and events[0]["building"] == "watchtower"
        assert events[0]["message"] == "Austria completes a watchtower at Vienna."

    def test_the_lever_down_restores_the_ownerless_line(self, europe, monkeypatch):
        monkeypatch.setattr(WS, "FOREIGN_WORKS_NAME_THEIR_OWNER", False)
        assert (_completed(europe, "Vienna")["message"]
                == "Construction complete: Market in Vienna!")

    def test_the_campaign_log_names_the_owner_too(self):
        event = {"type": "building_completed", "building": "market",
                 "region": "Vienna", "nation": "Austria"}
        assert (format_event_oneliner(event, player_nation="France")
                == "Austria completes a market in Vienna")
        # our own row, and a reader that names no player, are byte-identical
        assert format_event_oneliner(event) == "Construction complete: Market in Vienna"
        own = dict(event, nation="France", region="Paris")
        assert (format_event_oneliner(own, player_nation="France")
                == "Construction complete: Market in Paris")

    def test_the_log_route_passes_the_player(self, europe):
        """`GET /campaign_log` renders a visible foreign construction with
        its owner — the route is the one reader that knows the player."""
        from fastapi.testclient import TestClient
        from backend.commands.parser import CommandParser
        import backend.main as M

        saved = (M.world, M.game_state, M.parser)
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                M.world = europe
                M.game_state = {"world": europe}
                M.parser = CommandParser(use_real_llm=False)
                europe.get_region_intel("Vienna").visibility = FULL
                europe.log_event({"type": "building_completed", "region": "Vienna",
                                  "building": "market", "nation": "Austria"})
                body = TestClient(M.app).get("/campaign_log").json()
        finally:
            M.world, M.game_state, M.parser = saved
        displays = [e.get("display", "") for t in body.get("turns", [])
                    for e in t.get("events", [])]
        assert "Austria completes a market in Vienna" in displays, displays[:8]


# ═══════════════════════════════════════════════════════════════════════
# AAR-30 — the capital discount is ours only
# ═══════════════════════════════════════════════════════════════════════

class TestAAR30TheCapitalDiscountIsOursOnly:

    @pytest.fixture
    def ec(self):
        return CommandExecutor()._economy

    def test_an_occupied_enemy_capital_pays_the_ordinary_price(self, europe, ec):
        """"Lannes recruits 10,000 infantry for Vienna — 450 gold (capital
        discount)": Vienna is Austria's seat, not ours, whoever holds it."""
        vienna = europe.get_region("Vienna")
        vienna.controller = "France"
        cost, terms = ec._recruit_cost_terms(vienna, europe, base_cost=200,
                                             nation="France")
        assert "capital discount" not in terms
        paris_cost, paris_terms = ec._recruit_cost_terms(
            europe.get_region("Paris"), europe, base_cost=200, nation="France")
        assert "capital discount" in paris_terms
        assert cost > paris_cost

    def test_the_owner_keeps_its_own_seat_and_so_does_the_ai(self, europe, ec):
        """GR5: the AI prices through the same helper — Austria at Vienna is
        discounted, Austria at a captured Munich is not."""
        vienna = europe.get_region("Vienna")
        _, terms = ec._recruit_cost_terms(vienna, europe, base_cost=200,
                                          nation="Austria")
        assert "capital discount" in terms
        munich = europe.get_region("Munich")
        munich.controller = "Austria"
        _, terms = ec._recruit_cost_terms(munich, europe, base_cost=200,
                                          nation="Austria")
        assert "capital discount" not in terms

    def test_the_lever_down_restores_the_region_type_rule(self, europe, ec, monkeypatch):
        monkeypatch.setattr(EC, "THE_CAPITAL_DISCOUNT_IS_OURS_ONLY", False)
        vienna = europe.get_region("Vienna")
        vienna.controller = "France"
        _, terms = ec._recruit_cost_terms(vienna, europe, base_cost=200,
                                          nation="France")
        assert "capital discount" in terms

    def test_a_nation_less_call_keeps_the_region_type_rule(self, europe, ec):
        """The legacy direct-call sites pass no nation and are byte-identical."""
        _, terms = ec._recruit_cost_terms(europe.get_region("Vienna"), europe,
                                          base_cost=200)
        assert "capital discount" in terms

    def test_the_receipt_and_the_event_agree(self, europe):
        """Shown = applied: the recruit result's note and its event flag read
        the terms the pricer applied."""
        vienna = europe.get_region("Vienna")
        vienna.controller = "France"
        vienna.garrison_strength = 0
        lannes = europe.get_marshal("Lannes")
        lannes.location = "Vienna"
        europe.nation_gold["France"] = 100_000
        result = _execute(europe, {"action": "recruit", "marshal": "Lannes",
                                   "target": "Vienna", "recruit_type": "infantry"},
                          "Lannes, recruit infantry in Vienna")
        assert result.get("success") is True, result.get("message")
        assert "(capital discount)" not in result["message"]
        event = [e for e in result["events"] if e.get("type") == "recruit"][0]
        assert event["capital_discount"] is False
        assert event["stability_premium"] is False


# ═══════════════════════════════════════════════════════════════════════
# AAR-18 — "what can I build" uses the executor's own gate
# ═══════════════════════════════════════════════════════════════════════

_HERE = {"kind": "can_build", "subject": "", "subject_type": "here"}


def _send_the_army_abroad(world):
    for marshal in world.get_player_marshals():
        marshal.location = "Swabia"          # Bavarian soil, not ours


class TestAAR18TheDeskBreaksGround:

    def test_no_corps_on_our_soil_still_answers_from_the_gate(self, europe):
        """"what can I build" said nowhere while `build market at Paris`
        succeeded — the executor's build gate needs no corps."""
        _send_the_army_abroad(europe)
        answer = QD.answer_board_question(europe, _HERE) or ""
        assert "ground is broken without one" in answer
        assert "At Paris we may build:" in answer
        assert "g)" in answer
        assert "nowhere to break ground" not in answer

    def test_the_capital_leads_and_it_is_the_gate_s_own_answer(self, europe):
        """The capital leads even when a richer province of ours exists —
        Paris is also the richest French province at boot, so the pin
        stages a richer one to prove the ORDER, not the income."""
        from backend.models.region import BUILDING_TYPES, can_build
        _send_the_army_abroad(europe)
        # the richer province must itself be BUILDABLE, or the walk skips it
        richer_name = next(
            name for name in europe.get_nation_regions("France")
            if name != "Paris" and any(
                can_build(europe, europe.get_region(name), key, "France")[0]
                for key in BUILDING_TYPES))
        richer = europe.get_region(richer_name)
        richer.income_value = int(europe.get_region("Paris").income_value) * 50
        answer = QD.answer_board_question(europe, _HERE) or ""
        assert f"At {richer_name} we may build" not in answer
        paris = europe.get_region("Paris")
        for key, spec in BUILDING_TYPES.items():
            ok = can_build(europe, paris, key, "France")[0]
            if ok:
                assert key.replace("_", " ") in answer
                assert f"{int(spec['gold_cost']):,}g" in answer

    def test_a_corps_on_our_soil_is_still_preferred(self, europe):
        answer = QD.answer_board_question(europe, _HERE) or ""
        assert "ground is broken without one" not in answer
        assert "we may build:" in answer

    def test_the_lever_down_restores_the_shrug(self, europe, monkeypatch):
        monkeypatch.setattr(QD, "THE_DESK_BREAKS_GROUND_WITHOUT_A_CORPS", False)
        _send_the_army_abroad(europe)
        answer = QD.answer_board_question(europe, _HERE) or ""
        assert "nowhere to break ground" in answer

    def test_no_province_at_all_keeps_the_old_line(self, europe):
        _send_the_army_abroad(europe)
        for name in europe.get_nation_regions("France"):
            europe.get_region(name).controller = "Austria"
        europe.invalidate_active_nations_cache()
        answer = QD.answer_board_question(europe, _HERE) or ""
        assert "nowhere to break ground" in answer

    def test_the_capital_is_not_our_first_choice_when_it_is_lost(self, europe):
        _send_the_army_abroad(europe)
        europe.get_region("Paris").controller = "Austria"
        europe.invalidate_active_nations_cache()
        answer = QD.answer_board_question(europe, _HERE) or ""
        assert "ground is broken without one" in answer
        assert "At Paris" not in answer


# ═══════════════════════════════════════════════════════════════════════
# AAR-14 — the supply remedy names only ground a corps can march into
# ═══════════════════════════════════════════════════════════════════════

def _famine(extra_marshals=()):
    ney = MarshalFactory.infantry(name="Ney", location="Belgium", strength=90000)
    world = WorldFactory.with_marshals([ney, *extra_marshals], current_turn=6)
    for turn in (5, 6):
        world.event_log.append({"type": "supply_attrition", "nation": "France",
                                "region": "Belgium", "marshal": "Ney",
                                "losses": 2000, "turn": turn})
    return world


def _remedy(world):
    candidate = D._supply_strain_candidate(world, "France")
    assert candidate is not None
    return candidate["fields"]["remedy"]


def _feed(world, monkeypatch, *names):
    """Stage headroom: the named provinces feed half a million men. The cap
    is a derived property; the scan reads it through the SAME
    `get_effective_supply_cap` the attrition pass applies."""
    orig = world.get_effective_supply_cap
    monkeypatch.setattr(
        world, "get_effective_supply_cap",
        lambda nation, region: (500_000 if getattr(region, "name", "") in names
                                else orig(nation, region)))


class TestAAR14TheRemedyNamesOnlyOpenGround:

    def test_enemy_soil_is_never_the_remedy(self, monkeypatch):
        """"Vienna can feed 50,000 more — a corps marched there ends it":
        Vienna was Austria's, with 16,967 in the garrison."""
        world = _famine()
        rhineland = world.get_region("Rhineland")
        rhineland.controller = "Austria"
        rhineland.garrison_strength = 15000
        _feed(world, monkeypatch, "Rhineland")
        _war(world, "France", "Austria")
        assert "Rhineland" not in _remedy(world)
        # the pin binds: with the lever down the headroom scan names it
        monkeypatch.setattr(D, "THE_REMEDY_NAMES_ONLY_OPEN_GROUND", False)
        assert "Rhineland can feed" in _remedy(world)

    def test_an_enemy_corps_on_the_ground_is_the_probe_s_refusal(self, monkeypatch):
        """No second rule: a province with an enemy corps standing on it is
        refused by the executor's own move probe, lever up or down."""
        mack = MarshalFactory.enemy(name="Mack", location="Paris",
                                    nation="Austria", strength=20000)
        world = _famine([mack])
        _war(world, "France", "Austria")
        world.get_region_intel("Paris").visibility = FULL
        _feed(world, monkeypatch, "Paris")
        assert "Paris" not in _remedy(world)
        monkeypatch.setattr(D, "THE_REMEDY_NAMES_ONLY_OPEN_GROUND", False)
        assert "Paris" not in _remedy(world)

    def test_open_ground_is_still_named(self, monkeypatch):
        world = _famine()
        _feed(world, monkeypatch, "Paris")
        assert "Paris can feed" in _remedy(world)


# ═══════════════════════════════════════════════════════════════════════
# AAR-13 — the danger flag follows the province, not the marshal
# ═══════════════════════════════════════════════════════════════════════

def _starved_at_belgium(cause="shortage"):
    ney = MarshalFactory.infantry(name="Ney", location="Belgium")
    world = WorldFactory.with_marshals([ney], current_turn=7)
    for turn in (5, 6):
        world.event_log.append({"type": "supply_attrition", "turn": turn,
                                "marshal": "Ney", "nation": "France",
                                "region": "Belgium", "losses": 100,
                                "cause": cause})
    return world, ney


def _danger(world, ney):
    return D._derive_danger(ney, world, "France",
                            D._collect_supply_attrition_turns(world))


class TestAAR13TheDangerFlagFollowsTheProvince:

    def test_the_run_is_counted_where_he_stands(self):
        world, ney = _starved_at_belgium()
        assert _danger(world, ney).startswith(
            "Starving — supply has failed at Belgium two turns running")

    def test_a_fed_province_carries_no_flag(self):
        """"Lannes — Munich — Starving — supply has failed at Munich two
        turns running", the morning after he left starving Swabia."""
        world, ney = _starved_at_belgium()
        ney.location = "Paris"
        assert _danger(world, ney) == ""

    def test_the_collector_keys_the_province(self):
        world, _ = _starved_at_belgium()
        assert D._collect_supply_attrition_turns(world) == {"Ney": {"Belgium": [5, 6]}}

    def test_the_cause_is_read_at_the_province(self):
        world, ney = _starved_at_belgium("concentration")
        # a later, single shortage elsewhere must not re-label Belgium's run
        world.event_log.append({"type": "supply_attrition", "turn": 6,
                                "marshal": "Ney", "nation": "France",
                                "region": "Paris", "losses": 50,
                                "cause": "shortage"})
        assert _danger(world, ney).startswith("Crowded — Belgium carries more corps")

    def test_the_lever_down_restores_the_per_marshal_run(self, monkeypatch):
        monkeypatch.setattr(D, "THE_DANGER_FLAG_FOLLOWS_THE_PROVINCE", False)
        world, ney = _starved_at_belgium()
        ney.location = "Paris"
        assert D._collect_supply_attrition_turns(world) == {"Ney": [5, 6]}
        assert _danger(world, ney).startswith(
            "Starving — supply has failed at Paris two turns running")

    def test_a_legacy_per_marshal_list_still_reads(self):
        """The fixtures' shape: a bare list is "wherever he was"."""
        world, ney = _starved_at_belgium()
        ney.location = "Paris"
        out = D._derive_danger(ney, world, "France", {"Ney": [5, 6]})
        assert out.startswith("Starving — supply has failed at Paris")
