"""Tier 6 — session D (`DYNAMISM_SPEC.md` §5; the Tier-6 gate record §5a;
§2b session D; November 10, 2026). One file for the Awakening's second half:
DY-5, five rules behind their own seams (`tests/_t3_seams.py` rows T6-LEVEE,
T6-DIAL, T6-REVANCHE, T6-LIBERATORS, T6-ARMS).

THE LIBERATION LEVÉE (`awakening.levee_terms`, seam `the_levee_rises` —
1813): a court whose people stand at `stirring` or above, AT WAR, with home
soil contested (the last tick's derived count), regenerates infantry ×1.5
and prices the draft ×0.75 — read by `get_manpower_regen_rates` (after the
war exhaustion, before the laws) and by `_recruit_cost_terms` (after the
doctrine's term, before the laws; the AI's P1 rung reads the same pricer).
The National Guard — the third letter's Accept — doubles it for a term. The
levée is a beat (`levee`, the census 184 → 185): raised, stood down, the
Guard armed.

THE CLIENT DIAL — THE TIGER RIDDEN (`awakening.client_dial`, seam
`the_tiger_is_ridden`): an awakened client's loyalty −2 a turn at autonomy
≤ 1, +1 at autonomy ≥ 2 — ONE read for the tick, the forecast and the
debug breakdown; a rebellion of an awakened client names its cause.

THE INTERPLAYS: a people at `risen` promotes its grievance with any lost
homeland (`risen_grievance`, seam `a_risen_people_swears_revanche`); the
league frees an awakened people at half the friction
(`coalition_friction_step`, seam `liberators_hold_together`).

THE NATION IN ARMS (seam `the_nation_writes`, row DY-5 of
`affairs.SINCE_ROWS`): the third letter — the player's own people at `risen`
against an invader; Accept arms the National Guard (the `national_guard`
op, the thirteenth), Decline authority on the floor.
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

from backend import campaign_log as CL  # noqa: E402
from backend.commands import economy_executor as EE  # noqa: E402
from backend.game_logic import affairs as AF  # noqa: E402
from backend.game_logic import awakening as AW  # noqa: E402
from backend.game_logic import coalition as CO  # noqa: E402
from backend.game_logic import emergent_designs as EM  # noqa: E402
from backend.game_logic import game_end as GE  # noqa: E402
from backend.game_logic import gazette as GZ  # noqa: E402
from backend.game_logic import moments as MO  # noqa: E402
from backend.game_logic import vassal as VS  # noqa: E402
from backend.modding.validator import validate_scenario  # noqa: E402
from tests._t3_seams import T3_SEAMS_BY_ROW, hold_down  # noqa: E402

SCENARIO = (REPO / "godot-client" / "project-sovereign" / "assets"
            / "maps" / "europe_1805.json")
FIXTURE = REPO / "tests" / "fixtures" / "affairs_block.json"
LETTER = "the_nation_in_arms"
ROWS = ("T6-LEVEE", "T6-DIAL", "T6-REVANCHE", "T6-LIBERATORS", "T6-ARMS")
AUSTRIAN = ("Tyrol", "Carniola", "Moravia")            # three of Austria's seven, Vienna kept
FRENCH = ("Lorraine", "Champagne", "Burgundy", "Franche-Comte", "Ardennes", "Picardy")


@pytest.fixture()
def world():
    from backend.models.world_state import WorldState
    return WorldState.from_scenario(str(SCENARIO), seed="historical")


def _scenario() -> dict:
    return json.loads(SCENARIO.read_text(encoding="utf-8"))


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


def _events(world, etype: str):
    return [e for e in world.event_log if e.get("type") == etype]


def _takes(world, nation: str, *regions: str) -> None:
    with _quiet():
        for region_name in regions:
            world.capture_region(region_name, nation)


def _holds(world, holder: str, *regions: str) -> None:
    for region_name in regions:
        world.regions[region_name].controller = holder
    world.invalidate_active_nations_cache()


def _dispatch_lines(world, *etypes: str):
    from backend.game_logic.dispatch import _format_dispatch_event_text
    return [_format_dispatch_event_text(e["type"], e["template_vars"])
            for e in world.pending_dispatch_events if e["type"] in etypes]


def _set(world, court: str, value: int) -> None:
    AW.move(world, court, value - AW.level(world, court), "test")


def _tick(world):
    with _quiet():
        return AW.tick(world)


def _austria_contested(world, level: int = 45):
    """The 1813 board in miniature: France holds three Austrian provinces
    (Vienna kept — a court's LAST province walks T4-2's road), the tick
    writes the count, the people set at `level`."""
    _takes(world, "France", *AUSTRIAN)
    _tick(world)
    _set(world, "Austria", level - AW.band_raise(len(AUSTRIAN)))
    _tick(world)                       # the second tick writes the levée's bit at `level`


def _no_war(monkeypatch, world):
    monkeypatch.setattr(world, "get_nations_at_war_with", lambda nation: [])


# ═══════════════════════════════════════════════════════════════════════
# The liberation levée
# ═══════════════════════════════════════════════════════════════════════

class TestTheLevee:
    def test_quiet_at_the_boot(self, world):
        assert AW.levee_terms(world, "Austria") == (1.0, 1.0, "")
        assert AW.levee_terms(world, "France") == (1.0, 1.0, "")
        assert not AW.levee_holds(world, "Austria") and not _events(world, "levee")

    def test_the_levee_needs_all_three(self, world, monkeypatch):
        _austria_contested(world)
        assert AW.occupied(world, "Austria") == 3 and AW.level(world, "Austria") == 45
        assert AW.levee_terms(world, "Austria") == (1.5, 0.75, "the levée")
        _set(world, "Austria", 39)
        assert AW.levee_terms(world, "Austria") == (1.0, 1.0, ""), "a quiet people raises no levée"
        _set(world, "Austria", 45)
        with monkeypatch.context() as m:
            _no_war(m, world)
            assert AW.levee_terms(world, "Austria") == (1.0, 1.0, ""), "at peace there is no levée"
        _holds(world, "Austria", *AUSTRIAN)
        _tick(world)
        assert AW.occupied(world, "Austria") == 0
        assert AW.levee_terms(world, "Austria") == (1.0, 1.0, ""), "home soil free: no levée"

    def test_the_regen_rides_the_levee_after_exhaustion_and_before_the_laws(self, world, monkeypatch):
        _austria_contested(world)
        with monkeypatch.context() as m:
            hold_down(m, T3_SEAMS_BY_ROW["T6-LEVEE"])
            before = world.get_manpower_regen_rates("Austria")
        after = world.get_manpower_regen_rates("Austria")
        assert after["infantry"] == int(before["infantry"] * 1.5)
        assert (after["cavalry"], after["artillery"]) == (before["cavalry"], before["artillery"])
        src = inspect.getsource(type(world).get_manpower_regen_rates)
        assert src.index("we_penalty") < src.index("levee_terms") < src.index("apply_manpower_regen")

    def test_the_draft_is_priced_by_the_one_pricer(self, world, monkeypatch):
        _austria_contested(world)
        region = world.regions["Hungary"]
        pricer = EE._levy_pricer()
        with monkeypatch.context() as m:
            hold_down(m, T3_SEAMS_BY_ROW["T6-LEVEE"])
            quiet, quiet_terms = pricer._recruit_cost_terms(region, world, nation="Austria")
        price, terms = pricer._recruit_cost_terms(region, world, nation="Austria")
        assert "×0.75 the levée" in terms and "the levée" not in " ".join(quiet_terms)
        assert price == int(round(quiet * 0.75))
        # the substitute market never reads it (the draft alone)
        _sub, sub_terms = pricer._recruit_cost_terms(region, world, nation="Austria", draft=False)
        assert not any("levée" in t for t in sub_terms)
        src = inspect.getsource(EE.EconomyExecutor._recruit_cost_terms)
        assert (src.index("from backend.game_logic.doctrines import recruit_price_term")
                < src.index("levee_terms")
                < src.index("from backend.game_logic.reforms import recruit_price_terms"))
        # the AI's P1 rung reads this pricer and keeps no copy of the levée
        from backend.ai import enemy_ai
        ai_src = inspect.getsource(enemy_ai)
        assert "_calculate_recruit_cost(" in ai_src and "levee" not in ai_src

    def test_the_player_too(self, world):
        _takes(world, "Austria", *FRENCH[:3])
        _tick(world)
        _set(world, "France", 45)
        assert AW.levee_terms(world, "France") == (1.5, 0.75, "the levée")

    def test_the_beat_rises_and_stands_down(self, world, monkeypatch):
        _takes(world, "France", *AUSTRIAN)
        _tick(world)
        assert not _events(world, "levee"), "a quiet people raises no levée"
        _set(world, "Austria", 45)
        beats = _tick(world)
        rows = _events(world, "levee")
        assert [(r["nation"], r["direction"], r["occupied"]) for r in rows] == [("Austria", "raised", 3)]
        assert any(b["type"] == "levee" for b in beats)
        assert rows[0]["message"].startswith("THE NATION IN ARMS: the people of Austria")
        assert not any(ch.isdigit() for ch in rows[0]["message"].replace("3 home provinces", ""))
        [line] = _dispatch_lines(world, "levee")
        assert line == rows[0]["message"]
        assert _tick(world) == [] or not any(b["type"] == "levee" for b in _tick(world)), "no beat twice"
        with monkeypatch.context() as m:
            _no_war(m, world)
            _tick(world)
        assert [r["direction"] for r in _events(world, "levee")] == ["raised", "stood_down"]
        assert "stands down" in _events(world, "levee")[-1]["message"]

    def test_the_one_new_log_type_the_census_and_the_surfaces(self):
        assert "levee" in CL.CAMPAIGN_LOG_TYPES and len(CL.CAMPAIGN_LOG_TYPES) == 185
        assert "levee" in CL.LOG_TIER_LEAD and "levee" in GZ._COURT_TYPES
        from backend.game_logic.dispatch import (
            _DIPLOMATIC_EVENT_PRIORITY, _DIPLOMATIC_EVENT_TEMPLATES)
        assert _DIPLOMATIC_EVENT_TEMPLATES["levee"] == "{line}"
        assert _DIPLOMATIC_EVENT_PRIORITY["levee"] == "HIGH"
        up = CL.format_event_oneliner({"type": "levee", "nation": "Prussia", "direction": "raised"})
        down = CL.format_event_oneliner({"type": "levee", "nation": "Prussia", "direction": "stood_down"})
        guard = CL.format_event_oneliner({"type": "levee", "nation": "France", "direction": "guard"})
        assert up == "THE NATION IN ARMS — the people of Prussia fill the depots"
        assert down == "The levée of Prussia stands down"
        assert guard == "THE NATIONAL GUARD OF FRANCE UNDER ARMS — the levée doubled"

    def test_the_national_guard_doubles_for_a_term(self, world):
        _austria_contested(world)
        turn = world.current_turn
        beat = AW.arm_national_guard(world, "Austria", 6)
        assert beat["direction"] == "guard" and AW.guard_until(world, "Austria") == turn + 6
        assert AW.levee_terms(world, "Austria") == (2.0, 0.5, "the National Guard")
        assert AW.store(world)["courts"]["Austria"] == {"level": 45, "occupied": 3, "levee": 1, "guard": turn + 6}
        world.current_turn = turn + 6
        assert not AW.guard_stands(world, "Austria")
        assert AW.levee_terms(world, "Austria") == (1.5, 0.75, "the levée")
        _tick(world)
        assert "guard" not in AW.store(world)["courts"]["Austria"], "a lapsed term leaves the row"
        assert AW.arm_national_guard(world, "Austria", 99)["direction"] == "guard"
        assert AW.guard_until(world, "Austria") == world.current_turn + AW.GUARD_TURNS_BOUNDS[1], "clamped"

    def test_the_bits_survive_a_save(self, world):
        from backend.models.world_state import WorldState
        _austria_contested(world)
        AW.arm_national_guard(world, "Austria", 4)
        with _quiet():
            again = WorldState.from_dict(world.to_dict())
        assert AW.store(again)["courts"]["Austria"] == AW.store(world)["courts"]["Austria"]
        assert AW.levee_terms(again, "Austria") == (2.0, 0.5, "the National Guard")

    def test_the_seam_down_reads_one_and_beats_nothing(self, world, monkeypatch):
        hold_down(monkeypatch, T3_SEAMS_BY_ROW["T6-LEVEE"])
        _austria_contested(world)
        _tick(world)
        assert AW.levee_terms(world, "Austria") == (1.0, 1.0, "")
        assert not _events(world, "levee") and AW.arm_national_guard(world, "Austria", 6) is None
        assert "levee" not in AW.store(world)["courts"]["Austria"]


    def test_an_erased_court_raises_no_levee(self, world):
        """A people outlives its court (C3); a levée does not — the harness's
        Austria, every province taken by turn 11, stirs and rises under the
        march and never fills a depot."""
        _austria_contested(world)
        assert AW.levee_holds(world, "Austria")
        _takes(world, "France", "Vienna", "Bohemia", "Hungary", "Croatia")
        assert "Austria" not in world.get_active_nations()
        assert not AW.levee_holds(world, "Austria") and AW.levee_terms(world, "Austria") == (1.0, 1.0, "")

# ═══════════════════════════════════════════════════════════════════════
# The client dial — the tiger ridden
# ═══════════════════════════════════════════════════════════════════════

class TestTheClientDial:
    def test_a_quiet_people_reads_zero(self, world):
        assert AW.client_dial(world, "Holland", 0) == ("", 0)
        _set(world, "Holland", 39)
        assert AW.client_dial(world, "Holland", 1) == ("", 0)

    def test_the_tiger_ridden(self, world):
        _set(world, "Holland", 45)
        assert AW.client_dial(world, "Holland", 0) == ("the people's awakening", -2)
        assert AW.client_dial(world, "Holland", 1) == ("the people's awakening", -2)
        assert AW.client_dial(world, "Holland", 2) == ("the tiger ridden", 1)

    def test_the_tick_the_forecast_and_the_breakdown_share_the_read(self, world, monkeypatch):
        world.vassals["Holland"]["loyalty"] = 80
        _set(world, "Holland", 45)
        with monkeypatch.context() as m:
            hold_down(m, T3_SEAMS_BY_ROW["T6-DIAL"])
            quiet = dict(VS.forecast_vassal_loyalty(world, "France", "Holland"))
            assert (quiet["awakening_label"], quiet["awakening_drift"]) == ("", 0)
        hot = VS.forecast_vassal_loyalty(world, "France", "Holland")
        assert (hot["awakening_label"], hot["awakening_drift"]) == ("the people's awakening", -2)
        assert hot["forecast"] == quiet["forecast"] - 2
        world.vassals["Holland"]["autonomy"] = 2
        ridden = VS.forecast_vassal_loyalty(world, "France", "Holland")
        assert (ridden["awakening_label"], ridden["awakening_drift"]) == ("the tiger ridden", 1)
        world.vassals["Holland"]["autonomy"] = 1
        with _quiet():
            events = VS.process_vassal_loyalty(world)
        [row] = [e for e in events if e["vassal"] == "Holland"]
        assert "the people's awakening" in row["reason"]
        assert row["new_loyalty"] - row["old_loyalty"] == hot["forecast"] or row["delta"] <= hot["forecast"]
        import backend.main as M
        assert "client_dial" in inspect.getsource(M.debug_vassal_loyalty)

    def test_a_rebellion_names_the_cause(self, world):
        _set(world, "Holland", 45)
        world.vassals["Holland"]["loyalty"] = 0
        with _quiet():
            VS.check_vassal_rebellion(world)
        [row] = _events(world, "vassal_broke_free")
        assert row["vassal"] == "Holland" and row["cause"] == "awakening"
        lines = _dispatch_lines(world, "diplomatic_vassal_rebellion",
                                "diplomatic_vassal_broke_free_armistice",
                                "diplomatic_vassal_broke_free_peace")
        assert lines and lines[0].endswith(" Its people had risen against the yoke.")
        assert "Holland" in lines[0] and "{" not in lines[0]
        assert CL.format_event_oneliner(row).endswith(" Its people had risen.")

    def test_a_quiet_peoples_rebellion_names_nothing(self, world):
        world.vassals["Switzerland"]["loyalty"] = 0
        with _quiet():
            VS.check_vassal_rebellion(world)
        [row] = _events(world, "vassal_broke_free")
        assert "cause" not in row
        assert not CL.format_event_oneliner(row).endswith("Its people had risen.")

    def test_a_court_subjugated_later_feels_the_dial(self, world):
        """Spain under Joseph: a court vassalized LATER keeps its boot house
        (§5a C2), so its new lord's garrisons are foreign — the count rises,
        and the dial reads the same scalar (the player's most-played road)."""
        record = dict(world.vassals["Holland"])
        record["lord"] = "France"
        world.vassals["Spain"] = record
        world.invalidate_bloc_members_cache()
        world.invalidate_active_nations_cache()
        _holds(world, "France", "Madrid", "Leon", "Aragon")
        _tick(world)
        assert AW.occupied(world, "Spain") == 3
        _set(world, "Spain", 45)
        assert AW.client_dial(world, "Spain", 1) == ("the people's awakening", -2)
        # the boot-web boundary: a boot client's soil under its lord is home
        _holds(world, "France", "Amsterdam")
        _tick(world)
        assert AW.occupied(world, "Holland") == 0

    def test_the_seam_down(self, world, monkeypatch):
        hold_down(monkeypatch, T3_SEAMS_BY_ROW["T6-DIAL"])
        _set(world, "Holland", 60)
        assert AW.client_dial(world, "Holland", 0) == ("", 0)
        assert AW.rebellion_cause(world, "Holland") == ""


# ═══════════════════════════════════════════════════════════════════════
# The interplays
# ═══════════════════════════════════════════════════════════════════════

class TestTheInterplays:
    def test_a_risen_people_swears_revanche(self, world, monkeypatch):
        _holds(world, "France", "Posen")            # one province: under AI-5b's bar, no record
        with _quiet():
            assert EM.process_emergent_designs(world) == []
        _set(world, "Prussia", 70)
        with monkeypatch.context() as m:
            hold_down(m, T3_SEAMS_BY_ROW["T6-REVANCHE"])
            with _quiet():
                assert EM.process_emergent_designs(world) == [], "the seam down keeps the bar"
        with _quiet():
            [event] = EM.process_emergent_designs(world)
        assert event["type"] == "design_promoted" and event["nation"] == "Prussia"
        assert event["author"] == "France" and event["cause"] == "awakening"
        assert event["message"].endswith("The people have risen, and the court swears what they demand.")
        assert world.agendas["Prussia"][0]["id"] == "revanche_prussia"
        [line] = _dispatch_lines(world, "design_promoted")
        assert line.startswith("REVANCHE: Prussia") and "The people have risen" in line

    def test_a_partition_keeps_its_own_cause(self, world):
        _holds(world, "France", "Posen", "Pomerania")   # the bar met on its own
        _set(world, "Prussia", 70)
        with _quiet():
            [event] = EM.process_emergent_designs(world)
        assert "cause" not in event and "The people have risen" not in event["message"]

    def test_the_liberators_hold_together(self, world, monkeypatch):
        assert AW.coalition_friction_step(world, "France") == 2
        _austria_contested(world)
        assert AW.friction_eased(world, "France") and AW.coalition_friction_step(world, "France") == 1
        assert AW.coalition_friction_step(world, "Prussia") == 2, "a house holding no awakened soil"
        key = world._make_diplo_key("Austria", "Russia")
        world.nation_relations[key] = 80
        with monkeypatch.context() as m:
            hold_down(m, T3_SEAMS_BY_ROW["T6-LIBERATORS"])
            CO.apply_coalition_friction(world)
            assert world.nation_relations[key] == 78
        CO.apply_coalition_friction(world)
        assert world.nation_relations[key] == 77, "1 a turn, not 2, while the league frees a people"

    def test_the_eased_friction_reads_the_awakened_courts_alone(self, world):
        _takes(world, "France", *AUSTRIAN)
        _tick(world)
        assert not AW.friction_eased(world, "France"), "a quiet people under the garrisons eases nothing"
        _set(world, "Austria", 40)
        assert AW.friction_eased(world, "France")


# ═══════════════════════════════════════════════════════════════════════
# The Nation in Arms
# ═══════════════════════════════════════════════════════════════════════

class TestTheNationInArms:
    def test_the_three_letters_in_lockstep(self):
        scenario = _scenario()["moments"]["affairs"]
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))["affairs"]
        assert scenario == fixture
        ids = [e["id"] for e in fixture["deck"]]
        assert ids[-3:] == ["the_people_stir", "the_ulcer", LETTER] and len(ids) == 13
        e = fixture["deck"][-1]
        assert e["since"] == "DY-5" and e["shape"] == "bill" and e["scope"] == "owner"
        assert e["when"] == {"predicate": "nation_in_arms"}
        # an authority-alone Decline keeps the floor (the validator's own rule)
        assert e["bites"] == "floor"
        assert [op["op"] for op in e["accept"]["ops"]] == ["gold", "admin", "national_guard"]
        assert e["accept"]["ops"][2] == {"op": "national_guard", "turns": 6}
        assert [op["op"] for op in e["decline"]["ops"]] == ["authority"]
        assert e["voice"] == {"speaker": "named", "name": "Moncey, Major-General of the National Guard"}
        assert "may" in e["watch"] and "will" not in e["watch"]
        assert "{host}" in e["line"] and "{court}" in e["line"]

    def test_the_predicate_the_op_and_the_row_are_registered(self):
        assert AF.PREDICATES["nation_in_arms"] is AF._nation_in_arms and AF.PREDICATE_PARAMS["nation_in_arms"] == ()
        assert "DY-5" in AF.SINCE_ROWS and AF.row_armed("DY-5") is True
        assert "national_guard" in AF.AFFAIR_OPS and AF.AFFAIR_OP_BOUNDS["national_guard"] == (3, 12)
        assert "national_guard" in MO.DECLINE_FORBIDDEN_OPS and "national_guard" not in AF.DECLINE_ALLOWED_OPS
        assert "national_guard" not in MO.OP_BOUNDS and "national_guard" not in AF.BARRED_OPS
        assert len(MO.OPS) == 13

    def test_the_letter_sits_in_the_shipped_deck(self, world):
        assert [e["id"] for e in MO.affairs_deck(world)][-1] == LETTER

    def test_the_predicate_reads_the_lords_own_people(self, world, monkeypatch):
        no = {"holds": False, "bind": {}, "measure": None, "latch": False}
        assert AW.nation_in_arms(world, "France", {}) == no
        _takes(world, "Austria", *FRENCH[:3])
        _tick(world)
        _set(world, "France", 69)
        assert AW.nation_in_arms(world, "France", {}) == no, "below risen"
        _set(world, "France", 70)
        read = AW.nation_in_arms(world, "France", {})
        assert read == {"holds": True, "bind": {"host": "Austria"}, "measure": 3, "latch": False}
        with monkeypatch.context() as m:
            _no_war(m, world)
            assert AW.nation_in_arms(world, "France", {}) == no, "at peace"
        AW.arm_national_guard(world, "France", 6)
        assert AW.nation_in_arms(world, "France", {}) == no, "the Guard already stands"
        world.current_turn += 6
        assert AW.nation_in_arms(world, "France", {})["holds"]

    def test_the_invader_is_the_house_holding_the_most(self, world):
        _takes(world, "Austria", *FRENCH[:2])
        _takes(world, "Russia", *FRENCH[2:5])
        _tick(world)
        _set(world, "France", 75)
        assert AW.nation_in_arms(world, "France", {})["bind"] == {"host": "Russia"}

    def test_the_op_plans_and_applies(self, world):
        turn = world.current_turn
        plan = MO.OPS["national_guard"][0](world, "France", {"op": "national_guard", "turns": 6})
        assert not plan["refusal"] and plan["turns"] == 6 and plan["until"] == turn + 6
        assert plan["line"].startswith("the National Guard of France under arms until ") and "6 turns" in plan["line"]
        MO.OPS["national_guard"][1](world, "France", plan)
        assert AW.guard_until(world, "France") == turn + 6
        assert [r["direction"] for r in _events(world, "levee")] == ["guard"]
        again = MO.OPS["national_guard"][0](world, "France", {"op": "national_guard", "turns": 6})
        assert again["refusal"].startswith("The National Guard already stands under arms until ")

    def test_the_validator_refuses_a_decline_a_term_out_of_band_and_a_court(self):
        data = _scenario()
        deck = {e["id"]: e for e in data["moments"]["affairs"]["deck"]}
        deck[LETTER]["decline"]["ops"].append({"op": "national_guard", "turns": 6})
        deck[LETTER]["accept"]["ops"][2]["turns"] = 20
        deck["the_ulcer"]["accept"]["ops"].append({"op": "national_guard", "turns": 6, "court": "$host"})
        result = validate_scenario(data, check_adjacency=True)
        messages = " ".join(e.message for e in result.errors)
        assert "A Decline carries only" in messages
        assert any(e.path.endswith("ops[2].turns") for e in result.errors)
        assert any(e.path.endswith(".court") and "lord's own" in e.message for e in result.errors)

    def test_the_seam_holds_the_template_out(self, world, monkeypatch):
        hold_down(monkeypatch, T3_SEAMS_BY_ROW["T6-ARMS"])
        assert AF.row_armed("DY-5") is False
        assert LETTER not in {e["id"] for e in MO.affairs_deck(world)}
        _takes(world, "Austria", *FRENCH[:3])
        _tick(world)
        _set(world, "France", 80)
        assert not AW.nation_in_arms(world, "France", {})["holds"]
        # the two of DY-4 still stand
        assert [e["id"] for e in MO.affairs_deck(world)][-2:] == ["the_people_stir", "the_ulcer"]

    def test_the_bind_fills_the_slots(self, world):
        _takes(world, "Austria", *FRENCH[:3])
        _tick(world)
        _set(world, "France", 75)
        [entry] = [e for e in MO.affairs_deck(world) if e["id"] == LETTER]
        read = AW.nation_in_arms(world, "France", {})
        text = AF.fill_slots(world, entry["line"], {"bind": read["bind"], "lord": "France"}, entry,
                             n=read["measure"], m=1)
        assert "Austria" in text and "France" in text and "{" not in text

    def test_on_the_frozen_board_the_letter_arrives_and_arms_the_guard(self, world):
        """"Events appear": the frozen board — Austria holds six French
        provinces by treaty, the map held still, the mornings advanced by
        hand (the peoples' tick, then the moments' tick), the Emperor's
        grip at full (an authority-alone Decline keeps the floor) and the
        post read each morning. The French people stir at the 15th morning
        (+3 a turn), the levée rises with them, the rising comes at the
        25th and The Nation in Arms follows by its own conditions; the
        Accept arms the Guard and the levée doubles."""
        world.authority_tracker.authority = 100
        for r in FRENCH:
            _holds(world, "Austria", r)
            with _quiet():
                GE.record_province_title(world, r, GE.TITLE_TREATY, "France", "Austria")
        arrivals = {}
        letter_row = None
        for _ in range(32):
            world.current_turn += 1
            dm = world.dialogue_manager
            for letter in list(dm.iter_queue()) + ([dm.peek()] if dm.peek() else []):
                if MO.is_moment_letter(letter):
                    if MO.template_of(MO.moment_id_of(letter)) == LETTER:
                        letter_row = letter
                        continue
                    with _quiet():
                        MO.answer(world, letter, "decline")
            with _quiet():
                AW.tick(world)
                for mid in MO.tick(world):
                    arrivals.setdefault(MO.template_of(mid), world.current_turn)
            if LETTER in arrivals:
                break
        beats = [(e["turn"], e["phase"]) for e in _events(world, "awakening") if e["nation"] == "France"]
        assert beats == [(15, "stirring"), (25, "risen")]
        levee = [(e["turn"], e["direction"]) for e in _events(world, "levee") if e["nation"] == "France"]
        assert levee[:1] == [(15, "raised")]
        assert LETTER in arrivals and arrivals[LETTER] >= 27, arrivals
        rows = {k: v for k, v in MO._state(world).items() if k.startswith(LETTER + "#")}
        [(key, row)] = rows.items()
        assert row["bind"] == {"host": "Austria"} and row["status"] == "fired"
        # the Accept: the Guard armed, the levée doubled
        assert AW.levee_terms(world, "France") == (1.5, 0.75, "the levée")
        dm = world.dialogue_manager
        letter_row = next(d for d in list(dm.iter_queue()) + ([dm.peek()] if dm.peek() else [])
                          if MO.is_moment_letter(d) and MO.template_of(MO.moment_id_of(d)) == LETTER)
        with _quiet():
            result = MO.answer(world, letter_row, "accept")
        assert result.get("ok", True), result
        assert AW.guard_stands(world, "France") and AW.levee_terms(world, "France") == (2.0, 0.5, "the National Guard")
        assert [e["direction"] for e in _events(world, "levee") if e["nation"] == "France"][-1] == "guard"


# ═══════════════════════════════════════════════════════════════════════
# The scale contract, the seams, the numbers
# ═══════════════════════════════════════════════════════════════════════

class TestTheScaleContract:
    def test_the_module_never_walks_the_map(self):
        src = inspect.getsource(AW)
        assert "regions.values()" not in src and "regions.items()" not in src

    def test_every_seam_is_registered_and_zero_arg(self):
        import importlib
        for row in ROWS:
            [spec] = T3_SEAMS_BY_ROW[row]
            module_path, rest = spec.split(":")
            name = rest.split("=")[0]
            seam = getattr(importlib.import_module(module_path), name)
            assert seam() is True and inspect.signature(seam).parameters == {}

    def test_the_numbers_are_the_gates(self):
        assert (AW.LEVEE_REGEN_FACTOR, AW.LEVEE_PRICE_FACTOR) == (1.5, 0.75)
        assert (AW.GUARD_REGEN_FACTOR, AW.GUARD_PRICE_FACTOR, AW.GUARD_TURNS_BOUNDS) == (2.0, 0.5, (3, 12))
        assert (AW.DIAL_PUPPET_DRIFT, AW.DIAL_AUTONOMOUS_DRIFT, AW.DIAL_AUTONOMY_SPLIT) == (-2, 1, 2)
        assert (AW.FRICTION_STEP, AW.FRICTION_STEP_EASED) == (2, 1)

    def test_the_tick_settles_the_levee_after_the_scalar(self):
        src = inspect.getsource(AW.tick)
        assert src.index("move(world, court, delta") < src.index("_settle_levee(world, court)")
        from backend.models.world_state import WorldState
        src = inspect.getsource(WorldState._advance_turn_internal)
        assert src.index("_awakening.tick(self)") < src.index("_moments.tick(self)")

    def test_the_levee_reads_the_stores_count_never_a_scan(self):
        src = inspect.getsource(AW.levee_holds)
        assert "occupied(world, court)" in src and "occupied_count" not in src


# ═══════════════════════════════════════════════════════════════════════
# The session's one measure — six arms on three surfaces, each ALONE
# (`tools/_t6b_measure.py`; `tools/_t6b_series_arms.py`; the pacing chain
# `tools/playtest_runs/t6b_pacing_2026_11_10/`). Seeded paths, not laws
# (DYNAMISM_SPEC.md §5b; SYSTEMS_REFERENCE.md §204).
# ═══════════════════════════════════════════════════════════════════════

def _record(name: str) -> dict:
    return json.loads((REPO / "tools" / name).read_text(encoding="utf-8"))


def _dump(row) -> str:
    return json.dumps(row, sort_keys=True)


SEEDS = ("austerlitz", "eylau", "friedland", "historical", "jena", "lodi",
         "marengo", "rivoli", "ulm", "wagram")
STAMP = "2026_11_10"
AMBIENT_ARMS = (("0", "t6b_control"), ("LEVEE", "t6b_levee"), ("DIAL", "t6b_dial"),
                ("REVANCHE", "t6b_revanche"), ("LIBERATORS", "t6b_liberators"), ("ALL", "t6b"))
ARM_NAMES = tuple(a for a, _ in AMBIENT_ARMS)


class TestTheSessionDMeasure:
    """The records of the shipped tree (one run; arm 0 reproduces session C
    on every surface). Read honestly: every DY-5 seam bites where its
    condition holds and NOT ONE measured world-line moves in forty turns."""

    def _sig(self, label: str) -> dict:
        return _record(f"_dy_signature_{label}_{STAMP}.json")

    def _census(self, label: str) -> dict:
        return _record(f"_{label}_census_{STAMP}.json")

    def test_arm_0_reproduces_session_cs_records_on_both_surfaces(self):
        c = _record("_dy_signature_t6_2026_11_10.json")
        ctl = self._sig("t6b_control")
        for seed in SEEDS:
            assert _dump(ctl["seeds"][seed]) == _dump(c["seeds"][seed]), seed
        c_census, ctl_census = _record("_t6_census_2026_11_10.json"), self._census("t6b_control")
        assert all(ctl_census["totals"][k] == v for k, v in c_census["totals"].items())
        assert (ctl_census["totals"]["levees_raised"], ctl_census["totals"]["guards_armed"],
                ctl_census["totals"]["awakened_rebellions"], ctl_census["totals"]["risen_revanche"]) == (0, 0, 0, 0)
        harness = _record(f"_t6b_chain_d_{STAMP}.json")
        prior = _record("_t6_chain_d_2026_11_10.json")["arms"]["ALL"]
        for seed in SEEDS:
            mine = harness["arms"]["0"][seed]
            assert _dump({k: mine.get(k) for k in prior[seed]}) == _dump(prior[seed]), seed

    def test_no_seam_moves_an_ambient_world_line_and_the_classes_hold(self):
        """Honest: the ambient signature is byte-identical on every arm — the
        idle France recruits nothing under its levée, Bavaria's comes at
        36–41, no client is awakened (a boot client's soil is home), no AI
        court reaches `risen` (the revanche's trigger), the idle France
        holds no awakened soil (the liberators' cause); the bill is unmoved."""
        ctl = self._sig("t6b_control")
        for arm, label in AMBIENT_ARMS:
            sig = self._sig(label)
            assert sig["story_class_count"] == 10, arm
            for seed in SEEDS:
                assert _dump(sig["seeds"][seed]) == _dump(ctl["seeds"][seed]), (arm, seed)
            census = self._census(label)
            assert census["totals"]["supply_losses"] == 1196439 and census["totals"]["captures_outside_aim"] == 251, arm
            assert census["totals"]["annexations_outside_aim"] == 0 and census["totals"]["awakening_beats"] == 25, arm
            assert (census["totals"]["awakened_rebellions"], census["totals"]["risen_revanche"],
                    census["totals"]["guards_armed"]) == (0, 0, 0), arm

    def test_the_levee_rises_on_every_ambient_seed(self):
        """The French people stir on every seed (the idle France invaded, at
        war) and the levée rises with them (25–33); Bavaria's on five seeds
        (36–41 — Munich and Swabia under Austria, at war) and stands down on
        marengo at 41 (Austria's peace hands the soil back); fifteen in all,
        the same on every arm from LEVEE on; none on arm 0."""
        for arm, label in AMBIENT_ARMS[1:]:
            census = self._census(label)
            beats = {s: [(b["turn"], b["court"], b["direction"]) for b in census["seeds"][s]["levee_beats"]]
                     for s in SEEDS}
            france = {s: next(t for t, c, d in beats[s] if c == "France" and d == "raised") for s in SEEDS}
            assert france == {"austerlitz": 31, "eylau": 30, "friedland": 30, "historical": 25, "jena": 33,
                              "lodi": 25, "marengo": 32, "rivoli": 30, "ulm": 26, "wagram": 25}, arm
            bavaria = {s: [t for t, c, d in beats[s] if c == "Bavaria" and d == "raised"] for s in SEEDS}
            assert {s: t for s, t in bavaria.items() if t} == {"friedland": [39], "jena": [39], "marengo": [36],
                                                               "rivoli": [36], "ulm": [41]}, arm
            assert beats["marengo"][-1] == (41, "Bavaria", "stood_down")
            assert census["totals"]["levees_raised"] == 15, arm
            assert {c for s in SEEDS for _, c, _ in beats[s]} == {"France", "Bavaria"}
        assert all(not self._census("t6b_control")["seeds"][s]["levee_beats"] for s in SEEDS)

    def test_the_raised_gates_clauses_read_against_the_record(self):
        sig = self._sig("t6b")
        assert all(sig["seeds"][s]["signature"]["eliminations"] == [[t, "KingdomOfItaly"]]
                   for s, t in zip(SEEDS, (10, 7, 23, 9, 7, 10, 21, 7, 10, 9))), "clause 3: unmet"
        assert all(sig["seeds"][s]["signature"]["formations"] == [] for s in SEEDS)
        assert all(sig["seeds"][s]["signature"]["rank_promotions"] == [] for s in SEEDS), "clause 2: unmet"
        assert sig["story_class_count"] == 10, "clause 1: met"

    def test_the_harness_the_levee_rises_on_eight_seeds_and_moves_nothing(self):
        """Chain D: Russia's levée rises on eight seeds (26–39 — Estonia held,
        Russia at war, its people at `stirring`) and never on eylau or
        friedland (the march never reaches Estonia); Austria's never — the
        march takes every Austrian province by turn 11 and a people outlives
        its court where a levée does not; and NOT ONE world-line moves:
        Russia's last recruit falls at 9–17 on every seed, before its levée.
        Reported, never gated."""
        harness = _record(f"_t6b_chain_d_{STAMP}.json")
        arms = harness["arms"]

        def world_line(row):
            return _dump({k: v for k, v in row.items() if k not in (
                "awakening_events", "supply_losses", "levee_events", "awakened_rebellions", "risen_revanche")})

        for a, b in zip(ARM_NAMES, ARM_NAMES[1:]):
            assert all(world_line(arms[b][s]) == world_line(arms[a][s]) for s in SEEDS), (a, b)
        russia = {s: [t for t, c, d in arms["ALL"][s]["levee_events"] if c == "Russia" and d == "raised"]
                  for s in SEEDS}
        assert russia == {"austerlitz": [29], "eylau": [], "friedland": [], "historical": [26], "jena": [28],
                          "lodi": [39], "marengo": [38], "rivoli": [27], "ulm": [30], "wagram": [26]}
        assert all({c for _, c, _ in arms["ALL"][s]["levee_events"]} <= {"Russia"} for s in SEEDS)
        assert all(arms["ALL"][s]["awakened_rebellions"] == [] and arms["ALL"][s]["risen_revanche"] == []
                   for s in SEEDS)
        bill = {arm: sum(arms[arm][s]["supply_losses"].get("France", 0) for s in SEEDS) for arm in ARM_NAMES}
        assert set(bill.values()) == {488612}
        assert all(harness["totals"][arm] == harness["totals"]["0"] for arm in ARM_NAMES)
        assert (harness["totals"]["ALL"]["captures_outside_aim"], harness["totals"]["ALL"]["annexations_outside_aim"],
                harness["totals"]["ALL"]["rank_promotions"]) == (117, 0, 0)

    def test_the_france_band_holds_on_every_arm(self):
        band = _record(f"_t6b_band_{STAMP}.json")
        lo, hi = band["band"]
        assert set(band["arms"]) == set(ARM_NAMES)
        for arm, rows in band["arms"].items():
            figures = {name: rows[name]["provinces"] for name in ("CMD-H", "CMD-A", "CMD-M")}
            assert figures == {"CMD-H": 28, "CMD-A": 27, "CMD-M": 26}, arm
            assert all(lo <= v <= hi for v in figures.values()), arm

    def test_the_standing_series_does_not_move(self):
        from tests.test_ai_intent_threat_migration import BASELINE_SERIES
        rec = _record("_t6b_series_arms_final.json")
        assert rec["prior"] == BASELINE_SERIES
        assert list(rec["arms"]) == list(ARM_NAMES)
        for arm, row in rec["arms"].items():
            assert row["first_divergence_vs_prior"] is None and row["series"] == BASELINE_SERIES, arm
        reach = {arm: rec["arms"][arm]["reach"]["counts"] for arm in rec["arms"]}
        assert (reach["0"]["levee_bites"], reach["LEVEE"]["levee_bites"], reach["LEVEE"]["levee_beats"]) == (0, 15, 1)
        assert reach["ALL"]["dial_bites"] == 0 and reach["ALL"]["revanche_bites"] == 0
        assert reach["ALL"]["friction_eased"] == 0 and reach["ALL"]["letters_nation_in_arms"] == 9
        assert reach["LIBERATORS"]["letters_nation_in_arms"] == 0

    def test_the_letter_arrives_where_the_grip_can_pay_it(self):
        """The pacing chain re-recorded (the deck changed; no arm's letter
        timings moved — the world-lines did not): on the 53 measured arms The
        Nation in Arms' premise never held on 32, held one to ten mornings
        on 17 and was NEVER due (the floor — the idle France's grip falls
        95 → 67 → 22 across turns 25–32 as the coalition takes its home
        provinces), was due on three (pending on two, released on one) and
        ARRIVED on the scripted France alone (`armb_scripted_historical`,
        T38, grip 100: "The line will hold: Authority 100 → 97", lapsed on
        its decline). The frozen-board pin above is the Accept's proof; the
        floor is the lever named in the record."""
        rec = _record("_s14c_sweep_final.json")
        verdicts = {}
        for family in ("sweep", "commanded", "accept", "road", "road_accept", "reach_aar", "saves", "haiti"):
            for name, row in (rec.get(family) or {}).items():
                verdicts[f"{family}/{name}"] = row["affairs_reach"][LETTER]["verdict"]
        assert len(verdicts) == 53
        never = [k for k, v in verdicts.items() if v == "premise never held"]
        held = [k for k, v in verdicts.items() if v.startswith("never due (premise held")]
        due = [k for k, v in verdicts.items() if v.startswith("due,")]
        arrived = [k for k, v in verdicts.items() if v == "arrived"]
        assert (len(never), len(held), len(due), arrived) == (32, 17, 3, ["sweep/armb_scripted_historical"])
        row = rec["sweep"]["armb_scripted_historical"]["affairs_reach"][LETTER]
        assert row["first_due"] == 36 and row["occurrences"] == ["the_nation_in_arms#1 arrived T38, lapsed T39 (its decline)"]
        assert row["answers"][0]["quote"].startswith("The line will hold: Authority 100 → 97")
        # the other letters' timings did not move: the record's deck is the new deck
        assert _record("_affairs_first_arrival.json")["affairs"][-1] == LETTER
        road = _record("_vp1_road_arms_final.json")
        assert "Session C" in road["note"], "the roads did not move — session C's record stands"
