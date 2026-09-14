"""IQ-2 "The Collapse Is Legible" — the integration seams (Sept 14, 2026).

The five builder files each pin their own surface family. This file pins the
seams BETWEEN them that the integration pass closed — the places where one
builder's new key had no reader, or a defect sat in a file no builder owned:

- the coalition-dissolved chronicle line reads the `courts_at_war` stamp
  coalition.py now writes (the league lapses on low threat and ends no war);
- the war room's context keeps `threat_level` an int when a design is in
  check (the designs loop re-bound the SAME name to a nation key — GR2);
- the prisoner status note names the captor's court, not its raw key (R7);
- a field-battle / charge conquest stamps `captured_from`, so the
  enemy-phase dialog can read a French province lost in battle as a loss;
- the client reads the ledger's closed-depot flag and the Balance tab's
  collapse keys (source census, scoped to code lines);
- an order addressed to the captured Emperor is refused BY NAME on the
  typed path (the census's "cannot reach Paris from Vienna" was measured
  by driving the executor directly, below the /command guard).
"""

import ast
import contextlib
import io
import random
from pathlib import Path

import pytest

from backend.campaign_log import format_event_oneliner
from backend.models.world_state import WorldState

ROOT = Path(__file__).resolve().parents[1]
SCENARIO = str(ROOT / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json")
SCRIPTS = ROOT / "godot-client" / "project-sovereign" / "scripts"


def _boot():
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(SCENARIO)


def _code_lines(path: Path) -> str:
    """The .gd source minus full-line comments (a '#' inside a string such
    as '[color=#' survives — lines are never split on '#')."""
    return "\n".join(line for line in path.read_text(encoding="utf-8").splitlines()
                     if not line.lstrip().startswith("#"))


# ─────────────────────────────────────────────────────────────────────────
# The coalition-dissolved chronicle line
# ─────────────────────────────────────────────────────────────────────────

class TestTheLapsedLeagueInTheChronicle:
    def test_the_courts_still_at_war_are_named(self):
        line = format_event_oneliner({
            "type": "coalition_dissolved", "target_nation": "France",
            "courts_at_war": ["Austria", "Britain", "Russia"],
        })
        assert line == ("Coalition against France has dissolved — Austria, "
                        "Britain and Russia remain at war with us.")

    def test_one_court_takes_the_singular(self):
        line = format_event_oneliner({
            "type": "coalition_dissolved", "target_nation": "France",
            "courts_at_war": ["KingdomOfItaly"],
        })
        assert line.endswith("Kingdom of Italy remains at war with us.")

    def test_an_entry_without_the_stamp_is_byte_identical(self):
        for extra in ({}, {"courts_at_war": []}):
            line = format_event_oneliner({
                "type": "coalition_dissolved", "target_nation": "France", **extra})
            assert line == "Coalition against France has dissolved."

    def test_another_target_is_untouched(self):
        line = format_event_oneliner({
            "type": "coalition_dissolved", "target_nation": "Austria",
            "courts_at_war": ["Russia"],
        })
        assert line == "Coalition against Austria has dissolved."


# ─────────────────────────────────────────────────────────────────────────
# GR2: the war room's alarm stays an int
# ─────────────────────────────────────────────────────────────────────────

class TestTheWarRoomAlarmStaysAnInt:
    def test_threat_is_bound_once_in_the_assessment(self):
        """The designs-in-check loop used to assign `threat` — the name of
        the int alarm read at the top of `_assess_situation` — so the
        context's `threat_level` left for Godot as a nation key whenever a
        design was in check. One binding, and it is the int."""
        import backend.game_logic.diplomatic_advisory as adv
        tree = ast.parse(Path(adv.__file__).read_text(encoding="utf-8"))
        fn = next(n for n in ast.walk(tree)
                  if isinstance(n, ast.FunctionDef) and n.name == "_assess_situation")
        bindings = [n for n in ast.walk(fn)
                    if isinstance(n, (ast.Assign, ast.AnnAssign, ast.AugAssign))
                    for t in (n.targets if isinstance(n, ast.Assign) else [n.target])
                    if isinstance(t, ast.Name) and t.id == "threat"]
        assert len(bindings) == 1
        assert "int(" in ast.unparse(bindings[0].value)


# ─────────────────────────────────────────────────────────────────────────
# R7: the prisoner note names the court
# ─────────────────────────────────────────────────────────────────────────

def _card(world, name):
    from backend.game_logic.marshal_overview import build_marshal_overview
    data = build_marshal_overview(world)
    cards = data if isinstance(data, list) else data.get("marshals", [])
    return next(c for c in cards if c.get("name") == name)


class TestThePrisonerNoteNamesTheCourt:
    def test_a_camel_case_captor_is_humanized(self):
        w = _boot()
        with contextlib.redirect_stdout(io.StringIO()):
            w.capture_marshal(w.marshals["Ney"], "KingdomOfItaly")
        note = _card(w, "Ney")["status_note"]
        assert "Kingdom of Italy" in note and "KingdomOfItaly" not in note

    def test_lever_down_restores_the_raw_key(self, monkeypatch):
        import backend.game_logic.marshal_overview as mo
        monkeypatch.setattr(mo, "THE_PRISONER_NOTE_NAMES_THE_COURT", False)
        w = _boot()
        with contextlib.redirect_stdout(io.StringIO()):
            w.capture_marshal(w.marshals["Ney"], "KingdomOfItaly")
        assert "KingdomOfItaly" in _card(w, "Ney")["status_note"]

    def test_a_plain_captor_keeps_the_w6_7_wording(self):
        w = _boot()
        with contextlib.redirect_stdout(io.StringIO()):
            w.capture_marshal(w.marshals["Ney"], "Austria")
        assert _card(w, "Ney")["status_note"].startswith("PRISONER of Austria since T")


# ─────────────────────────────────────────────────────────────────────────
# The field-battle conquest names whom it was taken from
# ─────────────────────────────────────────────────────────────────────────

def _battle_the_frontier():
    """Mack, massively reinforced, attacks a token French corps on an
    ungarrisoned French province next to Swabia. Returns (world, result)."""
    from backend.commands.executor import CommandExecutor
    w = _boot()
    mack = w.marshals["Mack"]
    frontier = next(
        r for r in (w.regions[mack.location].adjacent_regions or [])
        if w.regions[r].controller == "France" and not w.regions[r].is_capital)
    # Every other French corps goes to the farthest French province — at
    # boot the Emperor stands one march away at Lorraine and marches to the
    # guns, so the defenders would hold the field and nothing would transfer.
    far = max((n for n, r in w.regions.items() if r.controller == "France"),
              key=lambda n: (w.get_distance(frontier, n), n))
    for m in w.marshals.values():
        if m.nation == "France" and m.name != "Ney":
            m.location = far
    victim = w.marshals["Ney"]
    victim.location = frontier
    # Measured: casualties scale to the defender, so a 300-man corps loses
    # 141 and still stands (no transfer); at 60 or fewer he is destroyed and
    # the province changes hands on every seed probed.
    victim.strength = 40
    region = w.regions[frontier]
    for attr in ("garrison", "garrison_detachment", "garrison_strength"):
        if hasattr(region, attr):
            setattr(region, attr, 0)
    region.fortification = 0 if hasattr(region, "fortification") else None
    mack.strength = 150000
    w.invalidate_active_nations_cache()
    random.seed(7)
    with contextlib.redirect_stdout(io.StringIO()):
        result = CommandExecutor().execute(
            {"success": True, "command": {"marshal": "Mack", "action": "attack",
                                          "target": "Ney"}},
            {"world": w})
    return w, frontier, result


class TestTheConquestNamesWhomItWasTakenFrom:
    def test_the_battle_event_stamps_captured_from(self):
        w, frontier, result = _battle_the_frontier()
        battle = next((e for e in result.get("events") or []
                       if e.get("type") == "battle"), None)
        # A skip here would be an inert pin — the fixture is tuned to conquer.
        assert battle is not None and battle.get("region_conquered") is True
        assert w.regions[frontier].controller == "Austria"
        assert battle.get("captured_from") == "France"

    def test_both_conquest_producers_carry_the_stamp(self):
        """Structural half: the attack's battle event and the charge event
        both read the holder captured BEFORE `_attempt_region_capture`."""
        src = (ROOT / "backend" / "commands" / "combat_executor.py").read_text(encoding="utf-8")
        assert '"captured_from": conquest_from' in src
        assert 'charge_event["captured_from"] = charge_conquest_from' in src
        attack_set = src.index("conquest_from = target_region.controller")
        assert attack_set < src.index("marshal, target_location, world, game_state, had_garrison=True)",
                                      attack_set)
        charge_set = src.index("charge_conquest_from = target_region.controller")
        assert charge_set < src.index("marshal, charge_battle_region, world, game_state, had_garrison=True",
                                      charge_set)


# ─────────────────────────────────────────────────────────────────────────
# The client reads the keys the integration added
# ─────────────────────────────────────────────────────────────────────────

class TestTheClientReadsTheIntegrationKeys:
    def test_the_manpower_tab_quotes_no_price_at_a_closed_depot(self):
        code = _code_lines(SCRIPTS / "strategic_ledger.gd")
        assert 'pool.get("depot_closed", false)' in code
        # The old priced line survives as the fallback.
        assert '" troops for " + str(recruit_cost) + "g"' in code

    def test_the_balance_tab_reads_the_collapse_keys(self):
        code = _code_lines(SCRIPTS / "diplomatic_ledger.gd")
        assert 'projection.get("collapse_line", "")' in code
        assert 'boe.get("headline_note", "")' in code
        # The projection line survives as the elif arm.
        assert "Next war of conquest: " in code

    def test_the_backend_keys_the_client_reads_exist(self):
        """Producer→renderer join: the two Balance keys and the depot flag
        ride their payloads under the collapse (and only then)."""
        import backend.game_logic.diplomatic_ledger as dl
        import backend.game_logic.ledger as lg
        dl_src = Path(dl.__file__).read_text(encoding="utf-8")
        lg_src = Path(lg.__file__).read_text(encoding="utf-8")
        assert 'threat_projection["collapse_line"]' in dl_src
        assert 'result["headline_note"]' in dl_src
        assert '"depot_closed"' in lg_src


# ─────────────────────────────────────────────────────────────────────────
# The captured Emperor is refused by name on the typed path
# ─────────────────────────────────────────────────────────────────────────

class TestTheCaptiveEmperorIsRefusedByName:
    def test_an_order_to_the_captive_emperor_names_his_captor(self, monkeypatch):
        from fastapi.testclient import TestClient
        import backend.main as M
        from backend.commands.parser import CommandParser
        w = _boot()
        with contextlib.redirect_stdout(io.StringIO()):
            w.capture_marshal(w.marshals["Napoleon"], "Austria")
            parser = CommandParser(use_real_llm=False)
        monkeypatch.setattr(M, "parser", parser)
        monkeypatch.setattr(M, "world", w)
        monkeypatch.setattr(M, "game_state", {"world": w})
        with contextlib.redirect_stdout(io.StringIO()):
            d = TestClient(M.app).post(
                "/command", json={"command": "Napoleon, attack Mack"}).json()
        msg = str(d.get("message", ""))
        assert "prisoner" in msg.lower() and "Austria" in msg
        assert "cannot reach" not in msg
