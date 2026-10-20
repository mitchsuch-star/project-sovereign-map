"""Pre-Deploy S13b part 4, slice S13b-6 — the sea (October 19, 2026;
`docs/BUG_FIXES.md` §DD-B; rules `SYSTEMS_REFERENCE.md` §132).

  DDB-21   a corps on soil its court holds by TITLE is home: the peace that
           titled Munster to France strands nobody there — no road home
           through Britain, no warning, no internment; the corridor is
           judged after the signature's titles; and a corps on his own
           shore across the water may embark (the ONE embark rule,
           `naval.embark_position_ok`, read by the executor, the Admiralty,
           the panel's chips and their reasons).
  DDB-X26  (found by DDB-21) a corps on his own soil with no foreign power
           beside it is never warned of an internment nobody can carry out
           ("failed to quit  soil" — nobody's).
  DDB-X27  (found by DDB-21) the §4.3 beachhead return while the war runs:
           a captured Irish beach is our soil across the water, and the
           transports take the corps off it rather than sending him to a
           yard he cannot walk to.

Every board is the shipped 1805 campaign; the reproductions were measured
on it before the fix (Lannes on Munster: an eight-march road through
Britain, warned three times, interned on the fourth tick).
"""
from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path

import pytest

from backend.commands.executor import CommandExecutor
from backend.game_logic import diplomacy as D
from backend.game_logic import game_end as GE
from backend.game_logic import naval as NV
from backend.game_logic import withdrawal as WD
from backend.models.world_state import WorldState

SCENARIO = (Path(__file__).resolve().parents[1] / "godot-client" / "project-sovereign"
            / "assets" / "maps" / "europe_1805.json")


@pytest.fixture(scope="module")
def boot() -> WorldState:
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(str(SCENARIO))


@pytest.fixture
def w(boot) -> WorldState:
    return WorldState.from_dict(json.loads(json.dumps(boot.to_dict(), default=str)))


def _quiet(fn, *a, **k):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*a, **k)


def _lannes_in_ireland(w, strength: int = 12000):
    """France takes Munster and Ulster from Britain; Lannes stands on Munster
    (the sea #21 shape — Oudinot there, commissioned in that campaign)."""
    for prov in ("Munster", "Ulster"):
        _quiet(w.capture_region, prov, "France")
    lannes = w.marshals["Lannes"]
    lannes.location = "Munster"
    lannes.strength = strength
    lannes.strategic_order = None
    w._build_marshal_index()
    return lannes


def _embark(w, marshal_name: str, target: str) -> dict:
    executor = CommandExecutor()
    return _quiet(executor._naval._execute_naval_expedition,
                  {"marshal": marshal_name, "action": "naval_expedition",
                   "target": target,
                   "raw_command": f"land {marshal_name} in {target}"},
                  {"world": w})


def _ticks(w, n: int) -> list:
    out = []
    for _ in range(n):
        w.current_turn += 1
        out.extend(_quiet(WD.process_evacuation_grants, w) or [])
    return out


class TestDDB21:
    def test_the_peace_that_titled_his_province_strands_nobody(self, w):
        lannes = _lannes_in_ireland(w)
        _quiet(D.set_diplomatic_state, w, "France", "Britain", "PEACE",
               "common_peace_settlement")
        assert GE.province_title_kind(w, "Munster", "France") == "treaty"
        assert GE.holds_by_title(w, "Munster", "France")
        home = WD.get_home_zone(w, "France")
        assert "Munster" not in home, "Ireland is not on the body of the realm"
        assert not WD.is_stranded(w, lannes, home), "titled soil is home"
        assert lannes.strategic_order is None, "no road home through Britain"
        assert not (w.evacuation_grants or {}), "nobody needed a corridor"
        granted = [e for e in w.event_log if e.get("type") == "evacuation_granted"]
        assert not [e for e in granted if "Lannes" in str(e.get("message"))]
        events = _ticks(w, 6)
        assert not [e for e in events if e.get("marshal") == "Lannes"], \
            "no warning, no internment"
        assert w.marshals["Lannes"].strength == 12000

    def test_a_held_enclave_still_needs_the_road(self, w):
        """The measured WIN-D3 shape stands: soil captured and never signed
        for is no title — a truce strands the corps on it."""
        lannes = _lannes_in_ireland(w)
        _quiet(D.set_diplomatic_state, w, "France", "Britain", "ARMISTICE",
               "armistice_ratified")
        assert GE.province_title_kind(w, "Munster", "France") == "held"
        assert not GE.holds_by_title(w, "Munster", "France")
        assert WD.is_stranded(w, lannes, WD.get_home_zone(w, "France"))

    def test_a_road_handed_out_before_the_title_is_done_with(self, w):
        """A road given before the signature titled his province (a save
        written mid-flight, or a treaty ratifier's own order) is cleared at
        the tick, as an arrival is."""
        lannes = _lannes_in_ireland(w)
        _quiet(D.set_diplomatic_state, w, "France", "Britain", "PEACE",
               "common_peace_settlement")
        from backend.models.marshal import StrategicOrder
        lannes.strategic_order = StrategicOrder(
            command_type="MOVE_TO", target="Normandy", target_type="region",
            started_turn=int(w.current_turn),
            original_command=WD.ROAD_HOME_COMMAND, path=[])
        lannes.road_home_offered = True
        w.evacuation_grants = {w._make_diplo_key("France", "Britain"): w.current_turn + 9}
        _ticks(w, 1)
        assert lannes.strategic_order is None
        assert lannes.road_home_offered is False
        assert WD.next_step_home(w, lannes) is None, "the AI's rung reads the same home"

    def test_the_corridor_reads_the_signatures_titles(self, w):
        """The setter opens the corridor AFTER the status quo's titles: the
        order of the two writes is the fix (before it, the corridor judged
        the pre-signature map and the road went out first)."""
        import inspect
        src = inspect.getsource(D.set_diplomatic_state)
        assert src.index("title_status_quo_retentions(") < src.index(
            "open_evacuation_corridor(world, nation_a, nation_b)")

    def test_he_may_embark_from_his_own_shore_across_the_water(self, w):
        _lannes_in_ireland(w)
        _quiet(D.set_diplomatic_state, w, "France", "Britain", "PEACE",
               "common_peace_settlement")
        assert not NV.on_home_soil(w, "France", "Munster")
        assert NV.embark_position_ok(w, w.marshals["Lannes"])
        result = _embark(w, "Lannes", "Brittany")
        message = str(result.get("message") or "")
        assert "must stand at one of our yards" not in message
        assert result.get("awaiting_clarification") or result.get("success"), message

    def test_home_soil_still_assembles_at_a_yard(self, w):
        """Unchanged: on the body of the realm a corps marches to a yard."""
        soult = w.marshals["Soult"]
        soult.location = "Picardy" if "Picardy" in w.regions else "Lorraine"
        soult.strength = 12000
        w._build_marshal_index()
        assert NV.on_home_soil(w, "France", soult.location)
        result = _embark(w, "Soult", "Munster")
        assert "must stand at one of our yards" in str(result.get("message")), result

    def test_the_panel_and_the_admiralty_read_the_same_rule(self, w):
        _lannes_in_ireland(w)
        _quiet(D.set_diplomatic_state, w, "France", "Britain", "PEACE",
               "common_peace_settlement")
        options = NV.expedition_landing_options(w, "France")
        assert any(o.get("marshal") == "Lannes"
                   for rows in options.values() for o in rows), \
            "the landing chips offer Lannes from Munster"

    def test_every_court_alike(self, w):
        """GR5: the predicate is the court's own record — an AI court's corps
        on soil signed to it is home; on soil merely held, it is not."""
        w.regions["Ulster"].controller = "Russia"
        w.invalidate_active_nations_cache()
        GE.record_province_title(w, "Ulster", GE.TITLE_TREATY, "Britain", "Russia")
        assert WD.title_is_home(w, "Russia", "Ulster")
        GE.record_province_title(w, "Ulster", GE.TITLE_CONQUEST, "Britain", "Russia")
        assert not WD.title_is_home(w, "Russia", "Ulster")
        w.current_turn += int(GE.TITLE_TURNS_DEFAULT) + 1
        assert WD.title_is_home(w, "Russia", "Ulster"), "a quiet conquest is a title"


class TestDDBX26:
    def test_nobody_interns_a_corps_with_no_foreign_power_beside_him(self, w):
        """Munster's only neighbour is Ulster, ours: a truce strands Lannes
        there (held, not titled), and the judge neither warns him of an
        internment nor carries one out — before the fix he was interned on
        the fourth tick 'failed to quit  soil'."""
        lannes = _lannes_in_ireland(w)
        _quiet(D.set_diplomatic_state, w, "France", "Britain", "ARMISTICE",
               "armistice_ratified")
        assert WD.is_stranded(w, lannes, WD.get_home_zone(w, "France"))
        assert WD._nobody_to_intern_him(w, lannes)
        events = _ticks(w, 8)
        mine = [e for e in events if e.get("marshal") == "Lannes"]
        assert not [e for e in mine if e.get("type") in (
            "evacuation_lapsing", "marshal_interned")], mine
        assert "Lannes" in w.marshals and w.marshals["Lannes"].strength == 12000

    def test_a_corps_with_the_enemy_at_his_edge_is_still_judged(self, w):
        """Ulster borders the Highlands, Britain's: the ladder stands there."""
        lannes = _lannes_in_ireland(w)
        lannes.location = "Ulster"
        assert not WD._nobody_to_intern_him(w, lannes)


class TestDDBX27:
    def test_the_beachhead_return_while_the_war_runs(self, w):
        """At war, a captured Irish beach is our soil across the water: the
        transports take the corps off it (§4.3 "the same verb from the
        beachhead"); before, the yard rule sent him to Brittany."""
        assert w.get_diplomatic_state("France", "Britain") == "WAR"
        _lannes_in_ireland(w)
        assert not NV.on_home_soil(w, "France", "Munster")
        result = _embark(w, "Lannes", "Brittany")
        message = str(result.get("message") or "")
        assert "must stand at one of our yards" not in message
        assert result.get("awaiting_clarification") or result.get("success"), message


# ═══════════════════════════════════════════════════════════════════════════
# DDB-58 … 62 and X32 — the Admiralty speaks plainly
# ═══════════════════════════════════════════════════════════════════════════

def _report(w):
    return _quiet(NV.build_admiralty_report, w)


class TestDDB58:
    def test_the_rule_in_one_sentence(self, w):
        cs = _report(w)["continental_system"]
        assert cs["rule_line"] == NV.PORT_CLOSURE_RULE.format(target="Britain")

    def test_the_open_courts_with_their_ports(self, w):
        cs = _report(w)["continental_system"]
        rows = NV.ports_by_court_against(w, "Britain")
        open_rows = [(n, p) for n, p, closed in rows if not closed]
        assert open_rows, "the boot leaves courts open to Britain"
        assert cs["open_line"].startswith("Open to Britain: ")
        for nation, ports in open_rows:
            from backend.display_names import display_nation
            assert f"{display_nation(nation)} ({ports} port" in cs["open_line"]
        closed = sum(p for _n, p, c in rows if c)
        assert closed == NV.closed_ports_against(w, "Britain") == cs["ports_closed"]


class TestDDB59:
    def test_the_legend_says_whose_sail_already_counts(self, w):
        legend = _report(w)["crossings_legend"]
        assert "pooling a fleet" not in legend
        assert "Spain's 30 sail" in legend and "already count" in legend

    def test_the_camp_line_says_why_none_is_staged(self, w):
        line = _report(w)["own_fleet"]["camp_line"]
        assert line.startswith("No army is staged: 0 of the 40,000 men")
        assert "no order needed" in line

    def test_the_count_toward_staging(self, w):
        rec = NV.get_fleet(w, "France")
        camp = list(rec["camp_provinces"])
        for name in ("Soult", "Ney"):
            w.marshals[name].location = camp[0]
        w._build_marshal_index()
        rec["camp_turns"] = 1
        line = _report(w)["own_fleet"]["camp_line"]
        assert line == "Staged after 2 turns standing at war with Britain (1 of 2) — no order needed."

    def test_at_peace_with_the_island_the_camp_says_so(self, w):
        _quiet(D.set_diplomatic_state, w, "France", "Britain", "PEACE", "peace_ratified")
        line = _report(w)["own_fleet"]["camp_line"]
        assert "stages only while we stand at war with an island power" in line


class TestDDB60:
    def test_the_fleet_answer_names_both_postures(self, w):
        from backend.ai.state_desk import _answer_fleet
        answer = _answer_fleet(w)
        # PC-X51 (S14 part 2): the postures by their Admiralty buttons
        assert "Recall to home waters covers every crossing" in answer
        assert "Blockade the enemy closes an at-war court's ports" in answer
        assert "1.25 to 1" in answer


class TestDDB61:
    def test_the_rot_carries_its_remedy(self, w):
        assert NV.is_blockaded(w, "France"), "the boot: Britain pins France"
        from backend.commands.naval_executor import _blockade_rot_clause
        clause = _blockade_rot_clause(w, "France")
        assert "that is the number to fix" not in clause
        assert NV.window_remedy(w, "France") in clause
        assert NV.window_remedy(w, "France") in _report(w)["own_fleet"]["rot_line"]

    def test_the_chip_states_the_price_before_the_order(self, w):
        chip = [c for c in _report(w)["chips"] if c["command"] == "blockade the enemy"][0]
        assert "our own coasts go unguarded" in chip["note"]
        assert "Britain still pins her" in chip["note"]

    def test_a_pinned_fleets_order_does_not_stand_out_to_sea(self, w):
        executor = CommandExecutor()
        result = _quiet(executor._naval._execute_set_fleet_posture,
                        {"action": "set_fleet_posture", "raw_command": "blockade the enemy"},
                        {"world": w})
        assert result["message"].startswith(
            "The fleet is ordered to blockade stations — Britain still pins her in port."), result["message"]
        assert "stands out to sea" not in result["message"]

    def test_the_war_banner_says_one_station(self, w):
        from backend.game_logic.war_status import _naval_line
        line = _naval_line(w, "France")
        assert "UNDER BLOCKADE" not in line
        assert line.endswith("guarding home waters — pinned in port by Britain")


class TestDDB62:
    def _lay(self, w, raw: str, target=None) -> str:
        executor = CommandExecutor()
        cmd = {"action": "build_fleet", "raw_command": raw}
        if target:
            cmd["target"] = target
        return _quiet(executor._naval._execute_build_fleet, cmd, {"world": w})["message"]

    def test_the_named_yard_is_echoed(self, w):
        message = self._lay(w, "lay down a ship at Normandy", "Normandy")
        assert message.startswith("A keel is laid at Normandy — one fleet, whichever yard lays her keel")

    def test_a_province_that_is_no_yard_is_said_so(self, w):
        message = self._lay(w, "lay down a ship at Lorraine", "Lorraine")
        assert "Lorraine is no yard of ours" in message

    def test_no_yard_named_keeps_the_first(self, w):
        assert self._lay(w, "build ships").startswith("A keel is laid at Bordelais (")


class TestDDBX32:
    def test_the_fleet_answer_names_its_yards_not_its_ports(self, w):
        from backend.ai.state_desk import _answer_fleet
        answer = _answer_fleet(w)
        assert "dockyards" not in answer
        assert "Her yards: Bordelais, Brittany, Normandy, Provence." in answer
