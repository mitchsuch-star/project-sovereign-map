"""SR-7c "Dispersion" (Score Finish Step 3, October 2, 2026) — AAR-D4.

Two rules behind `WorldState.DISPERSION_IS_NOT_PUNISHED`:
  (1) the PRESS the crowding tax counts — a corps on a SUPPORT order whose
      lead stands in the same province is a muster, not a crowd, and a
      capital or major city feeds one more corps free (the threshold rises
      to four corps there, three elsewhere); the engine, the Strategic
      Ledger and the muster preview read ONE press;
  (2) the retreat scan's FRIENDLY set is the soil France may enter and be
      fed on (ALLY_SUPPLY_STATES): an ally's or a vassal's province ranks
      with our own, not below an empty province of ours.
False = the shipped press and scan, byte for byte.
"""
from __future__ import annotations

import contextlib
import io
from pathlib import Path

import pytest

from backend.models.marshal import StrategicOrder
from backend.models import world_state as WS
from backend.models.world_state import WorldState

SCENARIO = (Path(__file__).resolve().parents[1] / "godot-client" / "project-sovereign"
            / "assets" / "maps" / "europe_1805.json")


def _boot():
    return WorldState.from_scenario(str(SCENARIO))


def _stand(world, names, region):
    for n in names:
        world.marshals[n].location = region
        world.marshals[n].strength = 10000
    for m in world.marshals.values():
        if m.name not in names and m.location == region:
            m.location = "Brittany"
    return [world.marshals[n] for n in names]


def _support(marshal, lead_name, turn=1):
    marshal.strategic_order = StrategicOrder(
        command_type="SUPPORT", target=lead_name, target_type="marshal",
        started_turn=turn, original_command=f"{marshal.name}, support {lead_name}")


class TestThePress:
    def test_three_corps_on_a_town_pay_the_tax(self):
        world = _boot()
        region = world.get_region("Lyonnais")           # a town: two corps free
        assert region.region_type not in ("capital", "major_city")
        corps = _stand(world, ["Ney", "Davout", "Lannes"], "Lyonnais")
        press, free = world.crowding_press(region, corps)
        assert (press, free) == (3, 2)
        assert world.supply_attrition_rate(30000, 100000, press, free_corps=free) > 0.0

    def test_three_corps_on_a_capital_are_fed_free_and_four_pay(self):
        world = _boot()
        paris = world.get_region("Paris")
        assert paris.region_type == "capital"
        corps = _stand(world, ["Ney", "Davout", "Lannes"], "Paris")
        press, free = world.crowding_press(paris, corps)
        assert (press, free) == (3, 3)
        assert world.supply_attrition_rate(30000, 100000, press, free_corps=free) == 0.0
        corps = _stand(world, ["Ney", "Davout", "Lannes", "Soult"], "Paris")
        press, free = world.crowding_press(paris, corps)
        assert (press, free) == (4, 3)
        assert world.supply_attrition_rate(40000, 100000, press, free_corps=free) > 0.0

    def test_a_support_corps_beside_its_lead_is_a_muster_not_a_crowd(self):
        world = _boot()
        region = world.get_region("Lyonnais")
        corps = _stand(world, ["Ney", "Davout", "Lannes"], "Lyonnais")
        _support(world.marshals["Davout"], "Ney")
        press, free = world.crowding_press(region, corps)
        assert press == 2 and free == 2
        assert world.supply_attrition_rate(30000, 100000, press, free_corps=free) == 0.0

    def test_a_support_order_for_a_lead_elsewhere_still_counts(self):
        world = _boot()
        region = world.get_region("Lyonnais")
        corps = _stand(world, ["Ney", "Davout", "Lannes"], "Lyonnais")
        _support(world.marshals["Davout"], "Soult")         # Soult is not here
        assert world.crowding_press(region, corps)[0] == 3

    def test_the_engine_bills_the_press(self):
        world = _boot()
        corps = _stand(world, ["Ney", "Davout", "Lannes"], "Paris")
        before = [m.strength for m in corps]
        with contextlib.redirect_stdout(io.StringIO()):
            events = world.process_supply_attrition()
        assert not [e for e in events if e.get("region") == "Paris" and e.get("cause") == "concentration"]
        assert [m.strength for m in corps] == before

    def test_the_ledger_and_the_engine_read_one_press(self):
        """Drift pin: the Strategic Ledger's supply verdict prices the same
        press the engine bills — three corps on Paris read OK, three on a
        town read Crowded."""
        from backend.game_logic.ledger import build_strategic_ledger
        world = _boot()
        _stand(world, ["Ney", "Davout", "Lannes"], "Paris")
        with contextlib.redirect_stdout(io.StringIO()):
            ledger = build_strategic_ledger(world)
        row = next(r for r in ledger["territories"] if r["name"] == "Paris")
        assert row["supply_status"] == "OK", row
        world = _boot()
        _stand(world, ["Ney", "Davout", "Lannes"], "Lyonnais")
        with contextlib.redirect_stdout(io.StringIO()):
            ledger = build_strategic_ledger(world)
        row = next(r for r in ledger["territories"] if r["name"] == "Lyonnais")
        assert row["supply_status"] != "OK", row

    def test_lever_down_three_corps_on_a_capital_pay(self, monkeypatch):
        monkeypatch.setattr(WS, "DISPERSION_IS_NOT_PUNISHED", False)
        world = _boot()
        paris = world.get_region("Paris")
        corps = _stand(world, ["Ney", "Davout", "Lannes"], "Paris")
        _support(world.marshals["Davout"], "Ney")
        press, free = world.crowding_press(paris, corps)
        assert (press, free) == (3, 2)
        assert world.supply_attrition_rate(30000, 100000, press, free_corps=free) > 0.0


class TestTheRetreatsFriendlySet:
    def test_an_allys_capital_with_a_friendly_corps_outranks_our_empty_province(self):
        world = _boot()
        tyrol = world.get_region("Tyrol")
        adj = list(tyrol.adjacent_regions)
        # stage: one adjacent French-held empty province, one ally-held with a French corps
        own_empty, ally_held = "Bohemia", "Munich"
        world.get_region(own_empty).controller = "France"
        host = world.get_region(ally_held)
        host.controller = "Bavaria"
        world.diplomatic_states[world._make_diplo_key("France", "Bavaria")] = "ALLIANCE"
        world.invalidate_active_nations_cache()
        for m in world.marshals.values():
            if m.location in (own_empty, ally_held, "Tyrol"):
                m.location = "Brittany"
        world.marshals["Massena"].location = "Tyrol"
        world.marshals["Davout"].location = ally_held
        world.marshals["Davout"].strength = 20000
        for a in world.get_region("Tyrol").adjacent_regions:      # the other exits: at-war soil
            if a not in (own_empty, ally_held):
                world.get_region(a).controller = "Austria"
        world.invalidate_active_nations_cache()
        with contextlib.redirect_stdout(io.StringIO()):
            dest = world.get_safe_retreat_destination("Massena", attacker_location=None)
        assert dest == ally_held, (dest, own_empty, ally_held)

    def test_non_aggression_soil_stays_foreign(self):
        world = _boot()
        own_empty, guest = "Bohemia", "Munich"
        world.get_region(own_empty).controller = "France"
        world.get_region(guest).controller = "Bavaria"
        world.diplomatic_states[world._make_diplo_key("France", "Bavaria")] = "NON_AGGRESSION"
        world.invalidate_active_nations_cache()
        for m in world.marshals.values():
            if m.location in (own_empty, guest, "Tyrol"):
                m.location = "Brittany"
        world.marshals["Massena"].location = "Tyrol"
        world.marshals["Davout"].location = guest
        for a in world.get_region("Tyrol").adjacent_regions:
            if a not in (own_empty, guest):
                world.get_region(a).controller = "Austria"
        world.invalidate_active_nations_cache()
        with contextlib.redirect_stdout(io.StringIO()):
            dest = world.get_safe_retreat_destination("Massena", attacker_location=None)
        assert dest == own_empty

    def test_lever_down_the_allys_capital_ranks_below_our_empty_soil(self, monkeypatch):
        monkeypatch.setattr(WS, "DISPERSION_IS_NOT_PUNISHED", False)
        world = _boot()
        own_empty, ally_held = "Bohemia", "Munich"
        world.get_region(own_empty).controller = "France"
        world.get_region(ally_held).controller = "Bavaria"
        world.diplomatic_states[world._make_diplo_key("France", "Bavaria")] = "ALLIANCE"
        world.invalidate_active_nations_cache()
        for m in world.marshals.values():
            if m.location in (own_empty, ally_held, "Tyrol"):
                m.location = "Brittany"
        world.marshals["Massena"].location = "Tyrol"
        world.marshals["Davout"].location = ally_held
        for a in world.get_region("Tyrol").adjacent_regions:
            if a not in (own_empty, ally_held):
                world.get_region(a).controller = "Austria"
        world.invalidate_active_nations_cache()
        with contextlib.redirect_stdout(io.StringIO()):
            dest = world.get_safe_retreat_destination("Massena", attacker_location=None)
        assert dest == own_empty

    def test_the_predicate(self):
        world = _boot()
        assert world.retreat_soil_is_friendly("France", "France")
        assert world.retreat_soil_is_friendly("France", "KingdomOfItaly")      # a vassal
        assert not world.retreat_soil_is_friendly("France", "Prussia")         # at peace, no table
        assert not world.retreat_soil_is_friendly("France", None)
