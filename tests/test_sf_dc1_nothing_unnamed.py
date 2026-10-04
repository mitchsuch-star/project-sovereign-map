"""SF-DC-1 "Nothing unnamed" (Score Finish Step 7, October 4, 2026).

The doctrines' T9 drift pin and T10 unnamed-effect census as ONE instrument
(`tools/_doctrine_census.py`, `tools/playtest_driver.py --doctrine-census`),
and the four places its first run found a doctrine changing an outcome with
no line the player could read:

  1. the enemy-phase dialog's report whitelist drew neither `doctrine_lines`
     nor `morale_line` — a doctrine-decided arrival or rout on DEFENCE, where
     the player fights most of his battles, was carried and never shown;
  2. the dialog read an AI levy's `doctrine_note` off `ai_action`, the AI's
     decision dict, which never carries it (the executor's result does);
  3. a standing order's battle printed its outcome and dropped Berthier's
     report, the doctrine lines with it;
  4. a supply bite's own attrition line never named the clause that caused it.

Every pin stages the ordinary case on the real 1805 boot or reads the
client's real source; levers run up (the shipped tree) and down where the
pin is byte identity.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

from backend.game_logic import doctrines as DC
from backend.models import world_state as WS
from backend.models.world_state import WorldState
from tools import _doctrine_census as CEN

ROOT = Path(__file__).resolve().parents[1]
SCENARIO = ROOT / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
JENA = ROOT / "tools" / "playtest_scripts" / "dc_jena_road.json"


def _boot():
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(str(SCENARIO))


@pytest.fixture
def world():
    return _boot()


def _stage_posen(world, strength):
    """Ney alone at Posen, French-held: listed poor country outside the 1805
    homeland — the clause bites (×0.8 of the fed cap)."""
    posen = world.get_region("Posen")
    posen.controller = "France"
    world.invalidate_active_nations_cache()
    for m in world.marshals.values():
        if m.location == "Posen":
            m.location = "Berlin"
    ney = world.marshals["Ney"]
    ney.location = "Posen"
    ney.strength = int(strength)
    return posen, ney


def _attrition(world):
    with contextlib.redirect_stdout(io.StringIO()):
        return world.process_supply_attrition()


def _ney_event(events):
    rows = [e for e in events if e.get("type") == "supply_attrition" and e.get("marshal") == "Ney"]
    assert len(rows) == 1, events
    return rows[0]


# ═══════════════════════ 4. the supply bite is named ═══════════════════════

class TestTheSupplyBiteIsNamed:
    def test_a_bite_the_clause_alone_caused_says_all_of_them(self, world):
        """54,000 at Posen: under the fed cap (60,000) whole, over its 80%
        (48,000) — every man lost is the clause's."""
        _stage_posen(world, 54000)
        ev = _ney_event(_attrition(world))
        assert ev["losses"] > 0
        assert ev["message"] == (
            f"Supply shortage at Posen: Ney loses {ev['losses']:,} troops — all of "
            f"them to living off the land (this poor country feeds a French army 80%)")
        assert ev["doctrine"] == "Living off the land"
        assert ev["doctrine_losses"] == ev["losses"]

    def test_a_bite_the_clause_deepened_names_its_share(self, world):
        """96,000 at Posen: over both caps — the share is the engine's own
        arithmetic re-read with the clause off."""
        posen, ney = _stage_posen(world, 96000)
        cap_on = world.get_effective_supply_cap("France", posen, forecast=False)
        cap_off = world.get_effective_supply_cap("France", posen, forecast=False,
                                                 with_doctrine=False)
        assert cap_off > cap_on
        on = int(96000 * world.supply_attrition_rate(96000, cap_on, 1))
        off = int(96000 * world.supply_attrition_rate(96000, cap_off, 1))
        assert 0 < off < on
        ev = _ney_event(_attrition(world))
        assert ev["losses"] == on
        assert ev["doctrine_losses"] == on - off
        assert ev["message"].endswith(
            f" — {on - off:,} of them to living off the land "
            f"(this poor country feeds a French army 80%)")

    def test_the_counterfactual_is_exact(self, world):
        posen, _ = _stage_posen(world, 1)
        fed = int(posen.supply_capacity * world.HOME_SUPPLY_MULTIPLIER)
        assert world.get_effective_supply_cap("France", posen, forecast=False,
                                              with_doctrine=False) == fed
        assert world.get_effective_supply_cap("France", posen, forecast=False) == int(
            posen.supply_capacity * world.HOME_SUPPLY_MULTIPLIER * 0.8)

    def test_home_soil_carries_no_clause(self, world):
        paris = world.get_region("Paris")
        ney = world.marshals["Ney"]
        for m in world.marshals.values():
            if m.location == "Paris" and m is not ney:
                m.location = "Lorraine"
        ney.location = "Paris"
        ney.strength = int(paris.supply_capacity * world.HOME_SUPPLY_MULTIPLIER * 1.5)
        ev = _ney_event(_attrition(world))
        assert ev["message"] == f"Supply shortage at Paris: Ney loses {ev['losses']:,} troops"
        assert "doctrine" not in ev

    def test_the_lever_down_is_the_old_line(self, world, monkeypatch):
        monkeypatch.setattr(WS, "THE_SUPPLY_BITE_IS_NAMED", False)
        _stage_posen(world, 96000)
        ev = _ney_event(_attrition(world))
        assert ev["message"] == f"Supply shortage at Posen: Ney loses {ev['losses']:,} troops"
        assert "doctrine" not in ev and "doctrine_losses" not in ev

    def test_the_concentration_tax_is_never_the_clauses(self, world):
        """Three corps under even the clause's cap pay the press, not the
        clause — the line says so and carries no share."""
        posen, ney = _stage_posen(world, 9000)
        for name in ("Davout", "Lannes"):
            m = world.marshals[name]
            m.location, m.strength = "Posen", 9000
        events = _attrition(world)
        rows = [e for e in events if e.get("region") == "Posen"]
        assert rows and all(e["cause"] == "concentration" for e in rows)
        assert all("doctrine" not in e and "living off the land" not in e["message"]
                   for e in rows)

    def test_the_bill_is_unchanged(self, world, monkeypatch):
        """Display only: the loss with the lever up equals the loss with it down."""
        _stage_posen(world, 96000)
        up = _ney_event(_attrition(world))["losses"]
        w2 = _boot()
        monkeypatch.setattr(WS, "THE_SUPPLY_BITE_IS_NAMED", False)
        _stage_posen(w2, 96000)
        assert _ney_event(_attrition(w2))["losses"] == up


# ═════════════════ 1–3. the client draws what the wire carries ═════════════════

def _body(file, func):
    return CEN.gd_body(file, func)


class TestTheClientDrawsTheDoctrineLines:
    def test_the_enemy_phase_whitelist_reads_the_doctrine_lines_and_the_morale_line(self):
        code = _body("enemy_phase_dialog.gd", "_format_berthier_report")
        assert 'var doctrine_lines = report.get("doctrine_lines", [])' in code
        assert 'var morale_line = report.get("morale_line", "")' in code
        assert "Utils.humanize_nation_keys_in_text(dl)" in code
        assert "Utils.humanize_nation_keys_in_text(morale_line)" in code
        # main.gd's order: after the trust note, before Berthier's observation
        assert (code.index('report.get("trust_note"') < code.index('report.get("doctrine_lines"')
                < code.index('report.get("morale_line"') < code.index('report.get("observation"'))

    def test_the_levys_note_is_read_off_the_action_entry(self):
        code = _body("enemy_phase_dialog.gd", "_format_action")
        assert re.search(r'(?<![\w.])action\.get\("doctrine_note"', code)
        assert 'ai_action.get("doctrine_note"' not in code

    def test_a_standing_orders_battle_draws_berthiers_report(self):
        code = _body("main.gd", "_show_strategic_reports")
        assert ('if report.get("battle_report") is Dictionary and not '
                'report.battle_report.is_empty():') in code
        assert "_display_berthier_report(report.battle_report)" in code
        assert code.index('report.get("battle_message"') < code.index("_display_berthier_report(")

    def test_the_backend_puts_the_note_where_the_dialog_reads_it(self):
        """The census's model of the client is only as good as the backend's
        shape: the enemy-phase action entry IS the executor's result, with the
        AI's decision under `ai_action` (enemy_ai.py sets result["ai_action"])."""
        src = (ROOT / "backend" / "ai" / "enemy_ai.py").read_text(encoding="utf-8")
        assert src.count('result["ai_action"] = action') >= 2
        ee = (ROOT / "backend" / "commands" / "economy_executor.py").read_text(encoding="utf-8")
        assert '"doctrine_note": f"{_dnote[0]}, ×{_dnote[1]:g}" if _dnote else ""' in ee

    def test_the_census_model_of_the_client_reads_every_route(self):
        model = CEN.client_model()
        for route, row in model["routes"].items():
            assert all(row["reads"].values()), (route, row)
        assert model["routes"]["strategic_report"]["formatters"] == ["_display_berthier_report"]
        assert model["routes"]["enemy_phase"]["formatters"] == ["_format_berthier_report"]
        assert model["recruit_note_on_the_action"] is True
        assert model["tactical_messages"] is True
        assert model["dispatch_headline"] is True


class TestTheCensusReadsTheClientNotItsComments:
    def test_a_key_named_only_in_a_comment_is_not_read(self, monkeypatch):
        src = ("func _format_action(action: Dictionary) -> String:\n"
               "\t# action.get(\"doctrine_note\", \"\") is read here, says the comment\n"
               "\tvar dnote = ai_action.get(\"doctrine_note\", \"\")\n"
               "\tresult += _format_berthier_report(action.battle_report)\n"
               "func _format_berthier_report(report: Dictionary) -> String:\n"
               "\t# report.get(\"doctrine_lines\")\n"
               "\tvar x = report.get(\"trust_note\", \"\")\n")
        monkeypatch.setitem(CEN._SRC_CACHE, "enemy_phase_dialog.gd", src)
        assert CEN.recruit_note_rendered() is False
        assert CEN.route_reads("enemy_phase", "doctrine_lines") is False
        assert CEN.route_reads("enemy_phase", "trust_note") is True

    def test_a_route_with_no_formatter_reads_nothing(self, monkeypatch):
        src = ("func _show_strategic_reports(response):\n"
               "\tvar battle_msg = report.get(\"battle_message\", \"\")\n")
        monkeypatch.setitem(CEN._SRC_CACHE, "main.gd", src)
        assert CEN.report_formatters("strategic_report") == []
        assert CEN.route_reads("strategic_report", "doctrine_lines") is False


# ═══════════════════════════ the census itself ═══════════════════════════════

class _Stub:
    """A digest's `record` and the backend module's `world`."""
    def __init__(self, world=None):
        self.world = world
        self.rows = []

    def record(self, kind, **fields):
        self.rows.append({"kind": kind} | fields)


def _report(attacker, defender, **keys):
    return {"casualty_summary": {"attacker_name": attacker, "defender_name": defender}, **keys}


class TestTheDriftPin:
    def test_a_stored_term_that_disagrees_with_a_fresh_derivation_is_drift(self, world):
        stub = _Stub(world)
        census = CEN.DoctrineCensus(stub, stub)
        census.observe("/command", {}, {})
        assert census.drift == [] and census.marshal_checks == len(world.marshals)
        world.marshals["Davout"]._doctrine_terms = dict(DC.terms_of(world.marshals["Davout"]),
                                                        attack=1.5)
        census.observe("/command", {}, {})
        assert [d["marshal"] for d in census.drift] == ["Davout"]
        assert any(r["kind"] == "doctrine_drift" for r in stub.rows)
        DC.refresh_doctrine_terms(world)
        census.drift.clear()
        census.observe("/command", {}, {})
        assert census.drift == []
        assert census.summary()["t9"]["pass"] is True


class TestTheJudgement:
    def _arrival(self, *, line_on, route="command", seen=True):
        row = {"marshal": "ArchdukeJohn", "arrived": False, "reason": "doctrine_delayed",
               "doctrine": "The Hofkriegsrat"}
        eff = {"kind": "arrival", "row": row, "court": "Austria", "doctrine": "The Hofkriegsrat",
               "marshal": "ArchdukeJohn", "a": "ArchdukeCharles", "b": "Massena",
               "region": "Milan", "party": True, "reinforcer_is_player": False}
        census = CEN.DoctrineCensus()
        census.report_fog[id(row)] = seen
        line = "The Hofkriegsrat's orders reached Archduke John too late."
        rep = _report("Archduke Charles", "Massena",
                      doctrine_lines=[line] if line_on else [])
        return census, census._judge_battle(eff, [(route, rep)])

    def test_a_line_on_a_drawn_route_is_named(self):
        _c, v = self._arrival(line_on=True)
        assert v["verdict"] == "named" and v["named_on"] == ["command"]

    def test_a_line_the_report_lacks_is_unnamed(self):
        _c, v = self._arrival(line_on=False)
        assert v["verdict"] == "unnamed" and "absent" in v["reason"]

    def test_a_line_the_client_does_not_draw_is_unnamed(self, monkeypatch):
        monkeypatch.setattr(CEN, "route_reads", lambda route, key: False)
        _c, v = self._arrival(line_on=True, route="enemy_phase")
        assert v["verdict"] == "unnamed" and "does not read doctrine_lines" in v["reason"]

    def test_an_arrival_the_reports_fog_withheld_is_fogged(self):
        _c, v = self._arrival(line_on=False, seen=False)
        assert v["verdict"] == "fogged"

    def test_a_roll_the_bar_shifted_but_did_not_decide_is_no_effect(self):
        census = CEN.DoctrineCensus()
        row = {"marshal": "Ney", "arrived": True, "doctrine_arrived": False,
               "doctrine": "The corps system", "reason": "arrived"}
        eff = {"kind": "arrival", "row": row, "court": "France", "doctrine": "The corps system",
               "marshal": "Ney", "a": "Lannes", "b": "Mack", "party": True,
               "reinforcer_is_player": True}
        assert census._judge_battle(eff, [])["verdict"] == "no_effect"

    def test_a_players_battle_that_reached_no_route_is_unnamed(self):
        census = CEN.DoctrineCensus()
        eff = {"kind": "morale", "court": "Prussia", "doctrine": "Brittle", "marshal": "Brunswick",
               "a": "Ney", "b": "Brunswick", "party": True,
               "line": "the Prussian line broke: Brittle deepened the rout (−63 morale, not −42)"}
        v = census._judge_battle(eff, [])
        assert v["verdict"] == "unnamed" and "no client route" in v["reason"]

    def test_the_levy_is_named_off_the_action_entry(self):
        census = CEN.DoctrineCensus()
        eff = {"kind": "recruit", "court": "Austria", "doctrine": "The Hereditary Lands",
               "mult": 0.85, "marshal": "Mack", "party": False,
               "note": "The Hereditary Lands, ×0.85", "term": "×0.85 The Hereditary Lands"}
        action = {"ai_action": {"action": "recruit", "marshal": "Mack"},
                  "events": [{"type": "recruit", "marshal": "Mack"}],
                  "doctrine_note": "The Hereditary Lands, ×0.85"}
        resp = {"enemy_phase": {"nations": {"Austria": {"actions": [action]}}}}
        assert census._judge_recruit(eff, resp)["verdict"] == "named"
        action.pop("doctrine_note")
        assert census._judge_recruit(eff, resp)["verdict"] == "unnamed"
        assert census._judge_recruit(eff, {})["verdict"] == "fogged"

    def test_a_bite_is_named_by_its_attrition_line(self):
        census = CEN.DoctrineCensus()
        eff = {"kind": "supply", "court": "France", "doctrine": "Living off the land",
               "marshal": "Ney", "region": "Posen", "party": True, "losses": 101, "extra": 101}
        named = {"tactical_events": [{"type": "supply_attrition", "marshal": "Ney",
                                      "message": "Supply shortage at Posen: Ney loses 101 troops "
                                                 "— all of them to living off the land (...)"}]}
        bare = {"tactical_events": [{"type": "supply_attrition", "marshal": "Ney",
                                     "message": "Supply shortage at Posen: Ney loses 101 troops"}]}
        assert census._judge_supply(eff, named)["verdict"] == "named"
        assert census._judge_supply(eff, bare)["verdict"] == "unnamed"
        assert census._judge_supply(eff, {})["reason"] == "no attrition line reached the response"

    def test_a_drawn_line_with_no_effect_behind_it_is_a_phantom(self):
        census = CEN.DoctrineCensus()
        rep = _report("Ney", "Mack", doctrine_lines=["The corps system brought Murat in.",
                                                     "Berthier: the corps marched apart and arrived together."])
        census._phantoms([("command", rep)], [], 3, "/command")
        assert [p["line"] for p in census.phantoms] == ["The corps system brought Murat in."]
        census2 = CEN.DoctrineCensus()
        census2._phantoms([("command", rep)], [{"kind": "arrival",
                                                 "line": "The corps system brought Murat in."}],
                          3, "/command")
        assert census2.phantoms == []

    def test_a_failure_inside_the_census_is_recorded_not_swallowed(self, world):
        stub = _Stub(world)
        census = CEN.DoctrineCensus(stub, stub)
        census.pending.append({"kind": "nonsense"})        # _judge_recruit will KeyError
        census.observe("/command", {}, {})
        assert census.instrument_drift and "observe /command" in census.instrument_drift[0]["where"]

    def test_a_judged_row_reaches_the_jsonl_with_its_class_as_effect(self, world):
        stub = _Stub(world)
        census = CEN.DoctrineCensus(stub, stub)
        census.pending.append({"kind": "supply", "court": "France", "doctrine": "Living off the land",
                               "marshal": "Ney", "region": "Posen", "party": True,
                               "losses": 5, "extra": 5})
        census.observe("/command", {}, {})
        rows = [r for r in stub.rows if r["kind"] == "doctrine_effect"]
        assert rows and rows[0]["effect"] == "supply"


class TestTheCensusOnTheEngine:
    def test_the_supply_reading_matches_the_engine_to_the_man(self, world):
        stub = _Stub(world)
        census = CEN.DoctrineCensus(stub, stub).install()
        try:
            _stage_posen(world, 96000)
            ev = _ney_event(_attrition(world))
        finally:
            census.uninstall()
        assert census.instrument_drift == []
        (eff,) = [e for e in census.pending if e["kind"] == "supply"]
        assert eff["extra"] == ev["doctrine_losses"]
        assert eff["losses"] == ev["losses"]

    def test_install_and_uninstall_restore_the_engine(self):
        from backend.commands import combat_executor as ce
        from backend.commands import economy_executor as ee
        from backend.game_logic import combat as cb
        before = (ce.CombatExecutor._calculate_reinforcements, ce.CombatExecutor._doctrine_lines,
                  cb.CombatResolver.resolve_battle, WS.WorldState.process_supply_attrition,
                  ee.EconomyExecutor._execute_recruit)
        census = CEN.DoctrineCensus().install()
        assert ce.CombatExecutor._calculate_reinforcements is not before[0]
        census.uninstall()
        after = (ce.CombatExecutor._calculate_reinforcements, ce.CombatExecutor._doctrine_lines,
                 cb.CombatResolver.resolve_battle, WS.WorldState.process_supply_attrition,
                 ee.EconomyExecutor._execute_recruit)
        assert after == before


# ═══════════════════════════ the driven census ═══════════════════════════════

class TestTheDrivenCensus:
    def test_the_jena_roads_opening_names_every_doctrine_effect(self, tmp_path):
        """Four loops of the T3 arm, in-process with the census on: no drift,
        nothing unnamed, no phantom — and the turn-3 Hofkriegsrat no-show in
        the enemy phase, which the client used to drop, is named there."""
        env = dict(os.environ, PYTHONHASHSEED="0", LLM_MODE="mock", SOVEREIGN_SEED="historical")
        env.pop("PYTHONIOENCODING", None)
        for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
            env.pop(key, None)
        env["INK_IRON_SAVE_DIR"] = str(tmp_path / "saves")
        proc = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "playtest_driver.py"), "--script", str(JENA),
             "--turns", "4", "--seed", "historical", "--out", str(tmp_path), "--name", "dc1",
             "--doctrine-census"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=900, env=env, cwd=str(ROOT))
        meta_path = tmp_path / "dc1" / "meta.json"
        assert meta_path.is_file(), proc.stderr[-2000:]
        census = json.loads(meta_path.read_text(encoding="utf-8"))["doctrine_census"]
        assert census["measured"] is True
        assert census["t9"]["pass"] is True and census["t9"]["posts"] > 0
        assert census["t10"]["unnamed_count"] == 0, census["t10"]["unnamed"]
        assert census["t10"]["phantom_count"] == 0
        assert census["instrument_drift"] == []
        rows = [json.loads(ln) for ln in
                (tmp_path / "dc1" / "digest.jsonl").read_text(encoding="utf-8").splitlines()
                if '"doctrine_effect"' in ln]
        hof = [r for r in rows if r.get("doctrine") == "The Hofkriegsrat"
               and r.get("verdict") == "named"]
        assert hof and "enemy_phase" in hof[0]["named_on"], rows
        md = (tmp_path / "dc1" / "digest.md").read_text(encoding="utf-8")
        assert "## Doctrine census (SF-DC-1)" in md and "T9 drift: 0 of" in md

    def test_the_census_is_off_by_default(self):
        src = (ROOT / "tools" / "playtest_driver.py").read_text(encoding="utf-8")
        assert 'ap.add_argument("--doctrine-census", action="store_true",' in src
        assert 'if getattr(args, "doctrine_census", False):' in src
        assert 'unmeasured(\n                "--http: the census reads the in-process world")' in src


# ═══════════════ SR-7d-X1 — the volte door and an ally's own war ═══════════════

class TestAnAllysWarIsItsOwn:
    """§6 row 20 (RULED under the delegation, FOR USER CONFIRMATION): the
    NOT-HUMILIATED clause's TREATY arm keeps IQ6-D2's whole bloc; its
    BATTLEFIELD arm (an emergent revanche) reads the hegemon's vassal chain."""

    @staticmethod
    def _austria_beaten_and_courted(world):
        from tests.test_ai_intent_emergent_designs import _beat_and_court
        _beat_and_court(world, power="Austria")

    @staticmethod
    def _revanche(world, author, regions=("Tyrol", "Croatia")):
        world.agendas.setdefault("Austria", []).insert(0, {
            "id": "revanche_austria", "type": "acquire_regions", "title": "Revanche",
            "regions": list(regions), "emergent": True, "author": author})

    def test_bavaria_is_an_ally_not_a_vassal(self, world):
        assert "Bavaria" in world.get_bloc_members("France")
        assert world._top_overlord("Bavaria") == "Bavaria"
        assert world._top_overlord("KingdomOfItaly") == "France"

    def test_a_revanche_charged_to_a_sovereign_ally_leaves_the_door_open(self, world):
        from backend.game_logic import emergent_designs as ED
        self._austria_beaten_and_courted(world)
        self._revanche(world, "Bavaria")
        assert ED.volte_face_failing_clauses(world, "Austria", "France") == []
        assert ED.volte_face_receptive(world, "Austria", "France") is True

    def test_lever_down_is_iq6_d2_as_built(self, world, monkeypatch):
        from backend.game_logic import emergent_designs as ED
        monkeypatch.setattr(ED, "AN_ALLYS_WAR_IS_ITS_OWN", False)
        self._austria_beaten_and_courted(world)
        self._revanche(world, "Bavaria")
        assert ED.volte_face_failing_clauses(world, "Austria", "France") == [
            ED.VOLTE_CLAUSE_REVANCHE]

    @pytest.mark.parametrize("author", ["France", "KingdomOfItaly"])
    def test_the_hegemons_own_chain_still_forecloses(self, world, author):
        from backend.game_logic import emergent_designs as ED
        self._austria_beaten_and_courted(world)
        self._revanche(world, author)
        assert ED.volte_face_failing_clauses(world, "Austria", "France") == [
            ED.VOLTE_CLAUSE_REVANCHE]

    def test_a_partition_signed_for_an_ally_still_forecloses(self, world):
        """The treaty arm keeps the bloc: a peace that CEDES Austrian homeland
        to Bavaria is a partition at the table (Tilsit's own reading)."""
        from backend.game_logic import emergent_designs as ED
        self._austria_beaten_and_courted(world)
        ED.record_punitive_cessions(world, {"Austria": [("Tyrol", "Bavaria"),
                                                        ("Croatia", "Bavaria")]})
        assert ED.volte_face_failing_clauses(world, "Austria", "France") == [
            ED.VOLTE_CLAUSE_PUNITIVE]

    def test_the_pressburg_board_promoted_by_the_engine_is_receptive(self, world):
        """The played shape, built by the engine's own poll: Bavaria holds two
        Austrian provinces (a partition), the revanche is charged to Bavaria,
        and the door stays open — the defeat shows on Bavaria's soil, in
        France's bloc."""
        from backend.game_logic import emergent_designs as ED
        self._austria_beaten_and_courted(world)
        world.regions["Bohemia"].controller = "Austria"       # France holds none
        for name in ("Tyrol", "Croatia"):
            world.regions[name].controller = "Bavaria"
        world.invalidate_active_nations_cache()
        with contextlib.redirect_stdout(io.StringIO()):
            events = ED.process_emergent_designs(world)
        assert [e["author"] for e in events if e["nation"] == "Austria"] == ["Bavaria"]
        assert ED.volte_face_failing_clauses(world, "Austria", "France") == []
