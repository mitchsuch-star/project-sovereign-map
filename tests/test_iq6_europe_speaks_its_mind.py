"""IQ-6 "Europe Speaks Its Mind" — the row's own test file (contract §2, T1–T7).

Build contract: the IQ-6 contract (§1 rulings N1–N4, V1–V5; §2 tests). The
row's claim — "`intent_hardens` / `intent_eases` fired 0 times in twelve
40-turn runs; `volte_face` likewise 0" — split in two under measurement:

* the NARRATION zero was an instrument defect: the playtest digest printed
  only HIGH/CRITICAL dispatch rows, and the Stage-F lines are MEDIUM/LOW.
  N1 makes the digest read the whole dispatch (`THE_DIGEST_READS_THE_WHOLE_
  DISPATCH`), N2 gives the engine a FLOOR beside its ceiling (in
  tests/test_ai_intent_assurance.py), N3 pins delivery end to end;
* the VOLTE-FACE zero was real: nobody courted, and a perfect courtship could
  not land inside the 15-turn window. V1 widens it to 20 (ceiling 25), V2 lets
  the courier skip the routine ask cooldown, V3 retires the exhaustion arm
  under GR9 (the defeat is the soil), V4 makes Talleyrand and the war room say
  the door is open.

Where this file stands beside `tests/test_iq6_volte_face.py` (Builder A's):
that file proves the volte-face half on the BILATERAL route with unit
staging (a separate peace through `_ratify_treaty`, the mission started by
the dialogue arm, the identity grid against a verbatim copy of the old
predicate). This one proves the contract's ORDINARY GEOMETRY on the real
1805 board, touching nothing by hand: the playtest driver itself, in
process, running the committed commanded script with `--diplomacy accept`
and the historical seed — Britain's coalition settlement ratified on the
REAL settlement path (R49 running), Austria's soil held by France's bloc
from the fighting, courting typed through `/command` every turn, the
courier, the conflict confirm and the ratify all answered by the driver's
own policy. The hooks below READ; T7 proves they do not steer (the hooked
in-process digest and the unhooked subprocess digest are the same game,
turn block for turn block).

Measured when landed (September 14, 2026; historical seed, identical across
PYTHONHASHSEED 1 / 5 / 777):
* the settlement ends France's boot war with Austria on world turn 4 (R49
  pops Austria's 71 war exhaustion inside the ratification);
* uncourted, the counsel names the open door every turn t4–t22 and the
  relation drifts -80 -> -62: never courted, never receptive;
* courted from loop 5, the relation first reads 43 at t20 — exactly the
  counsel's forecast from every courting turn — the courier proposes that
  same turn through a live routine ask cooldown (V2), and the alliance signs
  at t21, inside the last signing turn 23: one beat, one dispatch;
* with the window lever down the same courtship is never receptive, and
  Austria's own ladder alliance lands at t29 — 25 turns after the war, which
  is why the ceiling is 25.
"""

from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

from backend.game_logic import ai_diplomacy as AD
from backend.game_logic import diplomacy as D
from backend.game_logic import diplomatic_advisory as ADV
from backend.game_logic import emergent_designs as ED
from backend.game_logic.diplomatic_dialogue import (
    MISSION_EFFECTS,
    mission_effect_magnitude,
)
from backend.game_logic.dispatch import _DIPLOMATIC_EVENT_PRIORITY
from backend.game_logic.intent import INTENT_DISPATCH_CAP
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
DRIVER = REPO / "tools" / "playtest_driver.py"
SCRIPTS = REPO / "tools" / "playtest_scripts"
SCENARIO = str(REPO / "godot-client" / "project-sovereign" / "assets"
               / "maps" / "europe_1805.json")
PLAYER = "France"
COURT = "Austria"
FLOOR = ED.VOLTE_FACE_RELATION_FLOOR
COURTING_ORDER = "Talleyrand, improve relations with Austria"
INTENT_TYPES = ("intent_hardens", "intent_eases", "intent_movement_tail")


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


def _load_driver(name):
    spec = importlib.util.spec_from_file_location(name, str(DRIVER))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# The module other files already load under their own names; this one is
# ours, so a monkeypatched lever here never leaks into theirs.
pdriver = _load_driver("playtest_driver_iq6")


def _copy(world):
    with _quiet():
        return WorldState.from_dict(world.to_dict())


def _rel(world, a=PLAYER, b=COURT):
    return int(world.nation_relations.get(world._make_diplo_key(a, b), 0) or 0)


# ═══════════════════════════════════════════════════════════════════════════
# The instrument: the REAL driver, in process, with read-only hooks
# ═══════════════════════════════════════════════════════════════════════════

class Run:
    """Everything one driven campaign left behind."""

    def __init__(self):
        self.rows = []          # Austria, read at her diplomatic phase
        self.fires = []         # every maybe_fire_volte_face call
        self.cleanups = []      # every cleanup_war_end touching Austria
        self.ends = []          # every end-turn response's morning dispatch
        self.snap = {}          # world copies at the two moments that matter
        self.world = None
        self.md = ""
        self.records = []
        self.meta = {}

    # ── derived ──
    def peace_row(self):
        return next(r for r in self.rows if r["state"] != "WAR")

    def first_receptive(self):
        return next((r for r in self.rows if r["rec"]), None)

    def volte_rows(self):
        return [r for r in self.rows if r["reason"] == "volte_face"]

    def blocks(self):
        return _turn_blocks(self.md)


def _turn_blocks(md):
    """{turn: [lines]} for every `## Turn N` block of a digest."""
    out = {}
    for chunk in md.split("\n## Turn ")[1:]:
        head, _, body = chunk.partition("\n")
        out[int(head.split()[0])] = body.split("\n")
    return out


def _drive(script, turns, name, levers=(), hooks=True):
    """Run `tools/playtest_driver.py`'s own `run()` in this process.

    ⚠ `main()` re-execs nothing, but a SUBPROCESS would discard a
    monkeypatched lever (the s16_d4 lesson) — hence in process. Everything
    the driver touches is restored: the env it sets (it POPS the conftest's
    `SOVEREIGN_SCENARIO=none` sentinel), `backend.main`'s world and parser
    (`/new_game` never rebuilds the parser, so it is set to a mock one here —
    otherwise a process that imported backend.main under the dev `.env`
    would parse through the live model), the hooks and the levers.

    The hooks only READ, with one discipline: every lever-down reading is a
    flip-and-restore of a pure predicate, and anything that might write
    (`_is_on_cooldown` reaches `_is_situation_urgent`) is read off a COPY
    later, never here."""
    run = Run()
    keys = ("LLM_MODE", "SOVEREIGN_SEED", "INK_IRON_SAVE_DIR", "DEBUG_MODE",
            "SOVEREIGN_SCENARIO", "SOVEREIGN_SMOKE_START", "SOVEREIGN_MAP")
    prior_env = {k: os.environ.get(k) for k in keys}
    os.environ["LLM_MODE"] = "mock"
    os.environ["SOVEREIGN_SEED"] = "historical"
    with _quiet():
        import backend.main as M
        from backend.commands.parser import CommandParser
    prior_main = (M.world, M.game_state.get("world"), M.parser)
    drv = _load_driver(f"playtest_driver_iq6_{name}")

    real_phase = AD.process_diplomatic_phase
    real_fire = ED.maybe_fire_volte_face
    real_cleanup = D.cleanup_war_end
    real_post = drv.Transport.post

    def _reading(world, module, attr, value):
        prev = getattr(module, attr)
        setattr(module, attr, value)
        try:
            return ED.volte_face_receptive(world, COURT, PLAYER)
        finally:
            setattr(module, attr, prev)

    def phase(nation, world):
        if nation != COURT:
            return real_phase(nation, world)
        row = {
            "turn": int(world.current_turn),
            "rel": _rel(world),
            "state": world.get_diplomatic_state(PLAYER, COURT),
            "clauses": ED.volte_face_failing_clauses(
                world, COURT, PLAYER, exhaustive=True),
            "rec": ED.volte_face_receptive(world, COURT, PLAYER),
            "rec_window_down": _reading(
                world, ED, "THE_WINDOW_FITS_THE_COURTSHIP", False),
            "rec_soil_down": _reading(world, ED, "THE_DEFEAT_IS_THE_SOIL", False),
            "view": ED.volte_face_courtship(world, COURT, PLAYER),
            "line": ED.volte_face_counsel_line(world, COURT, PLAYER),
            "road": D.forecast_relation_to(world, COURT, FLOOR),
            "we": (getattr(world, "war_exhaustion", {}) or {}).get(COURT),
            "soil": list(ED._lost_homeland(world, COURT)),
            "cooldowns": {k: v for k, v in
                          (getattr(world, "ai_proposal_cooldowns", {}) or {}).items()
                          if str(k).startswith(f"{COURT}|")},
            "mission": dict(world.active_diplomatic_mission or {}),
        }
        if row["state"] != "WAR" and "at_peace" not in run.snap:
            run.snap["at_peace"] = _copy(world)
        if row["rec"] and "at_courier" not in run.snap:
            run.snap["at_courier"] = _copy(world)
        proposal = real_phase(nation, world)
        row["reason"] = (proposal or {}).get("decision_reason")
        row["ptype"] = (proposal or {}).get("proposal_type")
        run.rows.append(row)
        return proposal

    def fire(world, nation_a, nation_b):
        ceiling = None
        if COURT in (nation_a, nation_b):
            ceiling = {
                "end": ED._latest_war_end_turn(world, COURT, PLAYER),
                "recent_at_ceiling": ED._war_with_ended_recently(
                    world, COURT, PLAYER, ED.VOLTE_FACE_WINDOW_CEILING),
                "recent_past_ceiling": ED._war_with_ended_recently(
                    world, COURT, PLAYER, ED.VOLTE_FACE_WINDOW_CEILING + 1),
            }
        out = real_fire(world, nation_a, nation_b)
        run.fires.append({"turn": int(world.current_turn), "a": nation_a,
                          "b": nation_b, "fired": bool(out), "ceiling": ceiling})
        return out

    def cleanup(world, diplo_key, *args, **kwargs):
        if COURT not in diplo_key.split("|"):
            return real_cleanup(world, diplo_key, *args, **kwargs)
        before = (getattr(world, "war_exhaustion", {}) or {}).get(COURT)
        out = real_cleanup(world, diplo_key, *args, **kwargs)
        run.cleanups.append({"turn": int(world.current_turn), "key": diplo_key,
                             "before": before,
                             "after": (getattr(world, "war_exhaustion", {}) or {})
                             .get(COURT)})
        return out

    def post(self, path, payload=None):
        out = real_post(self, path, payload)
        if path == "/command" and (payload or {}).get("command") == "end turn":
            morning = out.get("morning_dispatch")
            run.ends.append({
                "has_dispatch": isinstance(morning, dict),
                "rows": [{"type": e.get("type"), "priority": e.get("priority"),
                          "text": e.get("text")}
                         for e in ((morning or {}).get("diplomatic_events") or [])
                         if isinstance(e, dict)]})
        return out

    prior_levers = [(module, attr, getattr(module, attr))
                    for module, attr, _ in levers]
    tmp = tempfile.mkdtemp(prefix=f"iq6_{name}_")
    try:
        for module, attr, value in levers:
            setattr(module, attr, value)
        if hooks:
            AD.process_diplomatic_phase = phase
            ED.maybe_fire_volte_face = fire
            D.cleanup_war_end = cleanup
            drv.Transport.post = post
        os.environ["INK_IRON_SAVE_DIR"] = os.path.join(tmp, "saves")
        M.parser = CommandParser()      # LLM_MODE=mock is set above
        # FA-D24's Berthier rotation was a PROCESS-global counter
        # (`battle_report._OBSERVATION_COUNTS`) that nothing reset, so two
        # identical in-process drives printed different observation lines
        # (measured: turn 1, Charles vs Massena) and this helper cleared it
        # by hand — filed as IQ6-X1. IQ-8 item 8 (September 18, 2026) hung
        # the reset on the campaign's own creation (`WorldState.__init__`,
        # lever `battle_report.THE_ROTATION_BEGINS_WITH_THE_CAMPAIGN`), so
        # the `/new_game` every drive posts starts the count where a fresh
        # process does. The test-side clear is REMOVED, deliberately: T7's
        # hooked-vs-unhooked control now rides the production reset, and
        # would go red if that lever were ever flipped.
        ns = argparse.Namespace(
            name=name, turns=turns, seed="historical", llm="mock", scenario="",
            script=str(SCRIPTS / script), from_save="", http="",
            out=os.path.join(tmp, "out"), save_at="", objection="",
            diplomacy="accept", redemption="", petition="", declare_war="",
            paradox="", rebellion="", sabotage="", reward="", last_stand="",
            contact="", missions="", reload_every=0, cheats=False,
            strict=False, verbose=False, fresh=True, archive=False)
        with _quiet():
            rc = drv.run(ns)
        assert rc == 0, rc
        run.world = M.world
    finally:
        AD.process_diplomatic_phase = real_phase
        ED.maybe_fire_volte_face = real_fire
        D.cleanup_war_end = real_cleanup
        drv.Transport.post = real_post
        for module, attr, value in prior_levers:
            setattr(module, attr, value)
        M.world, M.parser = prior_main[0], prior_main[2]
        M.game_state["world"] = prior_main[1]
        for key, value in prior_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
    out_dir = Path(tmp) / "out" / name
    run.md = (out_dir / "digest.md").read_text(encoding="utf-8")
    run.records = [json.loads(line) for line in
                   (out_dir / "digest.jsonl").read_text(encoding="utf-8").splitlines()
                   if line.strip()]
    run.meta = json.loads((out_dir / "meta.json").read_text(encoding="utf-8"))
    return run


@pytest.fixture(scope="module")
def courted():
    """The committed courting script, to just past the beat (the court
    signs at t21 on the landing measurement)."""
    return _drive("volte_court_austria.json", 23, "courted")


@pytest.fixture(scope="module")
def courted_unhooked():
    """The SAME script, the SAME process, no hooks at all — the control for
    the 'the hooks do not steer' pin (T7). Anything the process carries from
    earlier tests is carried by both arms alike, so the two digests must be
    identical line for line, not merely as multisets."""
    return _drive("volte_court_austria.json", 23, "courted_unhooked", hooks=False)


@pytest.fixture(scope="module")
def plain():
    """The same commanded arm with no courting — the uncourted negative,
    and N3's `commanded_full40 --diplomacy accept --seed historical`."""
    return _drive("commanded_full40.json", 23, "plain")


@pytest.fixture(scope="module")
def window_down():
    """The courting script with the window lever DOWN, long enough to see
    Austria's own ladder alliance land (t29 when landed)."""
    return _drive("volte_court_austria.json", 29, "window_down",
                  levers=((ED, "THE_WINDOW_FITS_THE_COURTSHIP", False),))


# ═══════════════════════════════════════════════════════════════════════════
# T1 — the window fits the courtship (arithmetic from production sources)
# ═══════════════════════════════════════════════════════════════════════════

class TestT1TheWindowFitsTheCourtship:
    def _step(self, world, relation, effect):
        relation = max(-D.RELATION_CLAMP, min(D.RELATION_CLAMP, relation + effect))
        return relation + D.relation_drift_step(world, PLAYER, COURT,
                                                relation=relation, _court=None)

    def test_the_arithmetic_lands_inside_twenty_and_not_fifteen(
            self, courted, monkeypatch):
        """The best lever's arithmetic, derived from the production tables
        (not from the forecast helper): the Improve Relations base times the
        acting diplomat's skill multiplier, the thaw, the courted floor, and
        the peace-turn offset — the peace turn itself passes on the thaw
        alone (the script courts from the turn after), the court's letter is
        written in the diplomatic phase that first reads the floor, and it
        is answered the next turn. The derivation must reproduce the REAL
        run turn for turn, and must land inside the window at 20 and outside
        it at 15."""
        world = courted.snap["at_peace"]
        base = int(MISSION_EFFECTS["IMPROVE_RELATIONS"]["relation_change"])
        effect = int(round(base * D.get_mission_skill_multiplier(world)))
        assert (base, effect) == (5, 8), "Talleyrand's skill 10: +5 pays +8"
        assert effect == mission_effect_magnitude(
            world, "IMPROVE_RELATIONS", "relation_change")

        peace = courted.peace_row()
        relation = peace["rel"]
        relation += D.relation_drift_step(world, PLAYER, COURT,
                                          relation=relation, _court=None)
        stepped = [relation]
        while stepped[-1] < FLOOR:
            stepped.append(self._step(world, stepped[-1], effect))
        arrival = peace["turn"] + len(stepped)
        signing = arrival + 1

        real = {r["turn"]: r["rel"] for r in courted.rows}
        assert [real[peace["turn"] + 1 + i] for i in range(len(stepped))] == stepped
        assert courted.first_receptive()["turn"] == arrival
        fired = [f for f in courted.fires if f["fired"]]
        assert [f["turn"] for f in fired] == [signing]

        assert ED.volte_face_window() == 20
        assert signing - peace["turn"] < ED.volte_face_window()
        monkeypatch.setattr(ED, "THE_WINDOW_FITS_THE_COURTSHIP", False)
        assert ED.volte_face_window() == 15
        assert signing - peace["turn"] >= ED.volte_face_window(), (
            "the pre-IQ-6 window shut the door on a PERFECT courtship")

    def test_the_ceiling_is_the_ladder_alliance_on_the_real_board(
            self, window_down):
        """With the window lever DOWN, Austria's ROUTINE ladder alliance
        (open borders -> non-aggression -> defensive alliance -> alliance,
        her own asks) lands and calls the ratify hook, which stays silent.
        It lands exactly CEILING turns after the war: at a window of 25 the
        war no longer reads as recent, at 26 it would — so a window of 26+
        would announce an ordinary alliance as a reversal."""
        calls = [f for f in window_down.fires if f["ceiling"] is not None]
        assert len(calls) == 1 and calls[0]["fired"] is False, calls
        call = calls[0]
        war_end = window_down.peace_row()["turn"]
        assert call["ceiling"]["end"] == war_end
        assert call["turn"] - war_end == ED.VOLTE_FACE_WINDOW_CEILING == 25
        assert call["ceiling"]["recent_at_ceiling"] is False
        assert call["ceiling"]["recent_past_ceiling"] is True
        assert (ED.VOLTE_FACE_WINDOW_BEFORE_IQ6 < ED.VOLTE_FACE_WINDOW
                <= ED.VOLTE_FACE_WINDOW_CEILING)


# ═══════════════════════════════════════════════════════════════════════════
# T2 — the ordinary geometry, on the real board, nothing hand-written
# ═══════════════════════════════════════════════════════════════════════════

class TestT2TheOrdinaryGeometry:
    def test_the_boot_war_ends_through_the_real_settlement_with_r49(self, courted):
        """France's boot war with Austria is ended by the coalition's own
        settlement offer, accepted by the driver's policy through the real
        settlement path. Austria's war exhaustion (above the old mark while
        she fought) is popped by R49 inside the ratification — that is the
        route the retired exhaustion arm could never survive."""
        peace = courted.peace_row()
        before = [r for r in courted.rows if r["turn"] < peace["turn"]]
        assert before and all(r["state"] == "WAR" for r in before)
        assert peace["state"] == "PEACE"
        assert int(before[-1]["we"] or 0) >= ED.VOLTE_FACE_WE_MARK
        popped = [c for c in courted.cleanups
                  if c["turn"] == peace["turn"]
                  and int(c["before"] or 0) >= ED.VOLTE_FACE_WE_MARK
                  and not c["after"]]
        assert popped, courted.cleanups
        assert not peace["we"]

    def test_the_soil_is_held_by_frances_bloc_and_only_courting_is_missing(
            self, courted):
        world = courted.snap["at_peace"]
        lost = ED._lost_homeland(world, COURT)
        assert lost, "Austria lost homeland provinces in the fighting"
        bloc = set(world.get_bloc_members(PLAYER))
        held = [r for r in lost
                if (world._top_overlord(world.regions[r].controller)
                    or world.regions[r].controller) in bloc]
        assert held, {r: world.regions[r].controller for r in lost}
        assert courted.peace_row()["clauses"] == [ED.VOLTE_CLAUSE_NOT_COURTED]

    def test_courted_through_the_executor_every_turn(self, courted):
        """The courting is typed at `/command` on every loop from 5 and
        answered by the real mission pipeline: the mission is live on every
        turn from the first order to the courier's turn."""
        orders = [r for r in courted.records
                  if r.get("kind") == "command" and r.get("text") == COURTING_ORDER]
        assert orders and all(o.get("success") is not False for o in orders), orders
        first = next(r for r in courted.rows if r["mission"])
        courier = courted.volte_rows()[0]
        for row in courted.rows:
            if first["turn"] <= row["turn"] <= courier["turn"]:
                assert row["mission"].get("type") == "IMPROVE_RELATIONS", row
                assert row["mission"].get("target") == COURT, row["mission"]
        assert "[anthropic" not in courted.md, "the run must parse in mock"

    def test_the_courier_proposes_inside_the_window(self, courted):
        receptive = courted.first_receptive()
        assert receptive is not None
        index = courted.rows.index(receptive)
        assert receptive["rel"] >= FLOOR > courted.rows[index - 1]["rel"]
        volte = courted.volte_rows()
        assert [r["turn"] for r in volte] == [receptive["turn"]]
        assert volte[0]["ptype"] == "alliance"
        last_signing = courted.rows[index - 1]["view"]["last_signing_turn"]
        assert receptive["turn"] + 1 <= last_signing
        assert receptive["turn"] + 1 - courted.peace_row()["turn"] < ED.volte_face_window()

    def test_the_alliance_ratifies_with_exactly_one_beat(self, courted):
        fired = [f for f in courted.fires if f["fired"]]
        assert len(fired) == 1 and {fired[0]["a"], fired[0]["b"]} == {COURT, PLAYER}
        assert fired[0]["turn"] == courted.volte_rows()[0]["turn"] + 1
        world = courted.world
        assert world.get_diplomatic_state(PLAYER, COURT) == "ALLIANCE"
        events = [e for e in world.event_log if e.get("type") == "volte_face"]
        assert len(events) == 1 and events[0]["nation"] == COURT
        assert events[0]["partner"] == PLAYER
        rows = [r for r in courted.records
                if r.get("kind") == "dispatch_row" and r.get("dtype") == "volte_face"]
        assert len(rows) == 1, rows
        assert courted.meta["dispatch_type_counts"]["volte_face"] == 1

    def test_the_measured_geometry(self, courted):
        """The landing measurement, pinned. A later slice that moves the
        board re-measures this consciously; the derived pins above stay."""
        assert courted.peace_row()["turn"] == 4
        assert courted.first_receptive()["turn"] == 20
        assert [f["turn"] for f in courted.fires if f["fired"]] == [21]


class TestT2Negatives:
    def test_uncourted_the_door_never_opens(self, plain):
        peace = plain.peace_row()
        rows = [r for r in plain.rows if r["turn"] >= peace["turn"]]
        assert rows[-1]["turn"] >= peace["turn"] + ED.volte_face_window() - 2, (
            "the run must cover the whole window")
        assert not any(r["rec"] for r in plain.rows)
        assert not plain.volte_rows()
        assert not any(f["fired"] for f in plain.fires)
        assert max(r["rel"] for r in rows) < FLOOR
        assert "volte_face" not in plain.meta["dispatch_type_counts"]

    def test_drift_alone_can_never_court(self, plain):
        """Why the uncourted arm is structural, not a seed accident: at
        peace the drift step never lifts a relation past +10, so a court
        below the courted floor stays below it unless somebody courts."""
        world = plain.snap["at_peace"]
        for relation in range(-100, 101):
            step = D.relation_drift_step(world, PLAYER, COURT, relation=relation)
            assert relation + step <= max(relation, 10), (relation, step)

    def test_lever_down_the_real_arm_never_reverses(self, window_down, courted):
        """The window lever DOWN, on the real board: the same courtship,
        the same game until the courier's turn (the lever changes only what
        the predicate reads), and never receptive — the ladder alliance it
        signs later is ordinary."""
        assert not any(r["rec"] for r in window_down.rows)
        assert not window_down.volte_rows()
        assert not any(f["fired"] for f in window_down.fires)
        assert "volte_face" not in window_down.meta["dispatch_type_counts"]
        assert not [e for e in window_down.world.event_log
                    if e.get("type") == "volte_face"]
        courier_turn = courted.first_receptive()["turn"]
        up = [(r["turn"], r["rel"]) for r in courted.rows if r["turn"] <= courier_turn]
        down = [(r["turn"], r["rel"]) for r in window_down.rows
                if r["turn"] <= courier_turn]
        assert up == down
        # The lever-down reading taken INSIDE the courted run agrees on every
        # turn of it: the old window never opens for this courtship.
        assert not any(r["rec_window_down"] for r in courted.rows)


# ═══════════════════════════════════════════════════════════════════════════
# T3 — V2, the courier skips the routine acceptance cooldown
# ═══════════════════════════════════════════════════════════════════════════

class TestT3TheCourierSkipsTheRoutineCooldown:
    def test_the_real_courier_turn_carried_a_routine_cooldown(self, courted):
        """Measured: France accepted Austria's own open-borders ask the turn
        before, so the NATION acceptance cooldown was live on the one turn
        the door opened — the courier proposed through it."""
        courier = courted.volte_rows()[0]
        assert courier is courted.first_receptive()
        assert int(courier["cooldowns"].get(f"{COURT}|nation") or 0) > 0
        assert not courier["cooldowns"].get(f"{COURT}|alliance")

    def test_lever_down_the_same_turn_is_held(self, courted, monkeypatch):
        snapshot = courted.snap["at_courier"]
        probe = _copy(snapshot)
        assert AD._is_on_cooldown(COURT, "alliance", probe) is True
        assert AD._is_on_cooldown(COURT, "alliance", probe,
                                  skip_nation_cooldown=True) is False
        with _quiet():
            up = AD.process_diplomatic_phase(COURT, _copy(snapshot))
        assert (up or {}).get("decision_reason") == "volte_face"
        monkeypatch.setattr(AD, "THE_VOLTE_COURIER_IGNORES_ROUTINE_COOLDOWN", False)
        with _quiet():
            down = AD.process_diplomatic_phase(COURT, _copy(snapshot))
        assert (down or {}).get("decision_reason") != "volte_face"

    def test_the_alliance_type_cooldown_still_holds_it(self, courted):
        world = _copy(courted.snap["at_courier"])
        world.ai_proposal_cooldowns[f"{COURT}|alliance"] = 3
        with _quiet():
            proposal = AD.process_diplomatic_phase(COURT, world)
        assert (proposal or {}).get("decision_reason") != "volte_face"


# ═══════════════════════════════════════════════════════════════════════════
# T4 — V3, the defeat is the soil
# ═══════════════════════════════════════════════════════════════════════════

class TestT4TheDefeatIsTheSoil:
    def test_the_ordinary_door_opens_on_soil_alone(self, courted):
        """After the real settlement the exhaustion is gone every turn the
        door stands, so the retired arm never showed this defeat — and the
        lever makes no difference on the ordinary route."""
        peace = courted.peace_row()
        after = [r for r in courted.rows if r["turn"] >= peace["turn"]]
        assert all(not r["we"] for r in after), [(r["turn"], r["we"]) for r in after]
        assert all(r["soil"] for r in after)
        assert all(r["rec_soil_down"] == r["rec"] for r in courted.rows)

    def test_exhaustion_without_soil_is_no_longer_a_defeat(self, courted, monkeypatch):
        """Russia after the same settlement: at peace, no province lost, her
        exhaustion popped by R49. Given an exhaustion far past the old mark
        and relations at the courted floor (staged — T4 only), she is NOT
        receptive with the lever up and IS with it down."""
        world = _copy(courted.snap["at_peace"])
        assert world.get_diplomatic_state(PLAYER, "Russia") == "PEACE"
        assert not ED._lost_homeland(world, "Russia")
        assert not (world.war_exhaustion or {}).get("Russia")
        assert ED.volte_face_failing_clauses(world, "Russia", PLAYER, exhaustive=True) == [
            ED.VOLTE_CLAUSE_NO_MARK, ED.VOLTE_CLAUSE_NOT_COURTED]
        world.war_exhaustion["Russia"] = 80
        world.nation_relations[world._make_diplo_key(PLAYER, "Russia")] = FLOOR
        assert ED.volte_face_receptive(world, "Russia", PLAYER) is False
        assert ED.volte_face_failing_clauses(world, "Russia", PLAYER) == [
            ED.VOLTE_CLAUSE_NO_MARK]
        assert ED.volte_face_counsel_line(world, "Russia", PLAYER) == ""
        monkeypatch.setattr(ED, "THE_DEFEAT_IS_THE_SOIL", False)
        assert ED.volte_face_receptive(world, "Russia", PLAYER) is True


# ═══════════════════════════════════════════════════════════════════════════
# V1b (Builder A's addition) — its lever, on both routes
# ═══════════════════════════════════════════════════════════════════════════

class TestV1bTheSeparatePeace:
    def test_the_common_route_never_needed_it(self, courted, monkeypatch):
        """A common settlement stamps the participant's exit, so the lever
        changes nothing on the ordinary geometry."""
        world = courted.snap["at_peace"]
        monkeypatch.setattr(ED, "THE_SEPARATE_PEACE_ENDS_THE_WAR", False)
        assert ED.volte_face_failing_clauses(world, COURT, PLAYER, exhaustive=True) == [
            ED.VOLTE_CLAUSE_NOT_COURTED]

    def test_a_bilateral_peace_needs_it(self, monkeypatch):
        """France's separate peace with Austria through the real bilateral
        ratify, Tyrol ceded by the treaty: Austria still fights France's
        allies, so only the pair's resolution says the war with France is
        over."""
        with _quiet():
            world = WorldState.from_scenario(SCENARIO)
            world._ratify_treaty({
                "type": "peace", "proposer_nation": PLAYER, "target_nation": COURT,
                "sweeteners": [],
                "demands": [{"type": "territory_cede", "regions": ["Tyrol"]}]})
        assert world.get_diplomatic_state(PLAYER, COURT) == "PEACE"
        assert ED.volte_face_failing_clauses(world, COURT, PLAYER, exhaustive=True) == [
            ED.VOLTE_CLAUSE_NOT_COURTED]
        assert ED._latest_war_end_turn(world, COURT, PLAYER) == int(world.current_turn)
        monkeypatch.setattr(ED, "THE_SEPARATE_PEACE_ENDS_THE_WAR", False)
        assert ED.volte_face_failing_clauses(world, COURT, PLAYER)[0] == (
            ED.VOLTE_CLAUSE_NOT_BEATEN)


# ═══════════════════════════════════════════════════════════════════════════
# T5 — V4, it speaks its mind
# ═══════════════════════════════════════════════════════════════════════════

def _ints(value):
    if isinstance(value, dict):
        for item in value.values():
            yield from _ints(item)
    elif isinstance(value, list):
        for item in value:
            yield from _ints(item)
    elif isinstance(value, (int, float)) and not isinstance(value, bool):
        yield value


class TestT5ItSpeaksItsMind:
    def test_the_uncourted_door_is_named_every_turn_with_its_turns_left(self, plain):
        """Every turn of the uncourted peace the counsel names the open door:
        the turns left are the window's arithmetic, the forecast is the
        mission counsel's own, and the copy is honest about which it is — a
        road that still lands, one that no longer does, or a door closing."""
        peace = plain.peace_row()
        window = ED.volte_face_window()
        rows = [r for r in plain.rows if r["turn"] >= peace["turn"]]
        branches = set()
        for row in rows:
            view = row["view"]
            assert view is not None and row["clauses"] == [ED.VOLTE_CLAUSE_NOT_COURTED]
            left = max(0, peace["turn"] + window - 2 - row["turn"])
            assert view["turns_left"] == left, row
            assert view["last_signing_turn"] == peace["turn"] + window - 1
            assert view["relation"] == row["rel"] and view["floor"] == FLOOR
            assert all(isinstance(n, int) for n in _ints(view))
            line = row["line"]
            assert line.startswith(f"{COURT} was beaten, not broken — "), line
            ticks = row["road"][0]
            if left <= 0:
                branches.add("closed")
                assert "door closes before" in line and f"{row['rel']:+d}" in line
            elif ticks <= left:
                branches.add("reachable")
                assert (f"court her to {FLOOR} within {left} turn" in line
                        and f"≈{ticks} turn" in line
                        and f"stand at {row['rel']:+d}" in line), line
            else:
                branches.add("too_long")
                assert (f"would not carry them to {FLOOR} in the {left} turn"
                        in line), line
        assert branches == {"reachable", "too_long", "closed"}

    def test_the_forecast_is_what_the_courtship_does(self, courted):
        """While courting, the counsel's "≈N turns" is exactly the number of
        turns the real courtship then took to open the door — shown is
        applied, from every courting turn (the drift step included: from
        -8 it is 7 ticks with the drift and would be 6 without)."""
        arrival = courted.first_receptive()["turn"]
        courting = [r for r in courted.rows
                    if r["mission"] and r["turn"] < arrival]
        assert len(courting) >= 10
        for row in courting:
            assert row["road"][0] == arrival - row["turn"], row
            assert f"≈{arrival - row['turn']} turn" in row["line"], row["line"]

    def test_silent_once_courted_and_once_signed(self, courted):
        arrival = courted.first_receptive()["turn"]
        for row in courted.rows:
            if row["turn"] >= arrival:
                assert row["line"] == "" and row["view"] is None, row
            elif row["state"] == "WAR":
                assert row["line"] == "", row

    def test_the_preview_counsel_says_it(self, plain, monkeypatch):
        """Through the real endpoint the wizard reads (`GET
        /diplomatic_preview?nation=Austria`): the recommendation carries the
        line after its own counsel; lever down, it is the pre-IQ-6 text."""
        from fastapi.testclient import TestClient

        import backend.main as M
        from backend.commands.parser import CommandParser
        world = _copy(plain.snap["at_peace"])
        monkeypatch.setattr(M, "world", world)
        monkeypatch.setitem(M.game_state, "world", world)
        monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
        client = TestClient(M.app)
        line = ED.volte_face_counsel_line(world, COURT, PLAYER)
        assert line
        with _quiet():
            up = client.get("/diplomatic_preview", params={"nation": COURT}).json()
        assert up["success"], up
        assert up["recommendation"].endswith(f" {line}"), up["recommendation"]
        monkeypatch.setattr(ED, "VOLTE_FACE_SPEAKS_ITS_MIND", False)
        with _quiet():
            down = client.get("/diplomatic_preview", params={"nation": COURT}).json()
        assert down["recommendation"] == up["recommendation"][:-len(line) - 1]
        assert "beaten, not broken" not in down["recommendation"]
        assert down.get("recommended_mission") == up.get("recommended_mission")

    def test_the_war_room_says_it(self, plain, monkeypatch):
        world = _copy(plain.snap["at_peace"])
        line = ED.volte_face_counsel_line(world, COURT, PLAYER)
        with _quiet():
            room = ADV._assess_situation(world)
        assert f"  {line}" in room["talleyrand_text"].split("\n")
        openings = room["context"]["volte_openings"]
        assert [o["nation"] for o in openings] == [COURT]
        assert openings[0]["text"] == line
        assert openings[0]["turns_left"] == plain.peace_row()["view"]["turns_left"]
        assert all(isinstance(n, int) for n in _ints(openings))
        monkeypatch.setattr(ED, "VOLTE_FACE_SPEAKS_ITS_MIND", False)
        with _quiet():
            down = ADV._assess_situation(_copy(plain.snap["at_peace"]))
        assert "volte_openings" not in down["context"]
        assert "beaten, not broken" not in down["talleyrand_text"]
        assert ED.volte_face_counsel_line(world, COURT, PLAYER) == ""
        assert ED.volte_face_courtship(world, COURT, PLAYER) is None

    def test_the_war_room_is_silent_when_the_door_has_opened(self, courted):
        with _quiet():
            room = ADV._assess_situation(_copy(courted.snap["at_courier"]))
        assert "volte_openings" not in room["context"]
        assert "beaten, not broken" not in room["talleyrand_text"]


# ═══════════════════════════════════════════════════════════════════════════
# T6 — N1: the digest reads the whole dispatch (the recorder idiom)
# ═══════════════════════════════════════════════════════════════════════════

class _Recorder:
    """A stand-in that BORROWS the real Digest's `dispatch` — the stub
    shape five test files use, and the shape that breaks the moment the
    method reaches for eagerly-created private state."""

    def __init__(self):
        self.lines = []
        self.records = []

    def _md(self, line):
        self.lines.append(line)

    def record(self, kind, **fields):
        self.records.append({"kind": kind} | fields)

    dispatch = pdriver.Digest.dispatch


def _row(dtype, priority, text=None):
    return {"type": dtype, "priority": priority, "text": text or f"{dtype} text"}


MIXED = [
    _row("call_to_arms_refused_defensive", "CRITICAL"),
    *[_row("diplomatic_ai_proposal", "HIGH", f"envoy {i}")
      for i in range(pdriver.MAX_RAIL_ROWS + 1)],
    _row("agenda_shift", "MEDIUM"),
    _row("intent_hardens", "MEDIUM", "The court of Austria hardens."),
    _row("diplomatic_dp_regen", "LOW"),
    _row("diplomatic_dp_regen", "LOW"),
    _row("intent_eases", "LOW", "The court of Russia eases."),
    _row("intent_movement_tail", "LOW", "And 3 other courts stir."),
    _row("volte_face", "HIGH", "THE VOLTE-FACE"),
]


class TestT6TheDigestReadsTheWholeDispatch:
    def test_a_low_intent_row_prints_on_courts_and_is_recorded(self):
        d = _Recorder()
        d.dispatch("head", events=[_row("intent_eases", "LOW",
                                        "The court of Russia eases over X.")])
        assert "- COURTS: The court of Russia eases over X." in d.lines
        assert not any("RAIL" in line for line in d.lines)
        assert {"kind": "dispatch_row", "dtype": "intent_eases",
                "priority": "LOW", "text": "The court of Russia eases over X."} in d.records

    def test_the_three_stage_f_types_print_in_order_and_nothing_else_is_tallied(self):
        d = _Recorder()
        d.dispatch("head", events=[
            _row("intent_hardens", "MEDIUM", "The court of Austria hardens."),
            _row("intent_eases", "LOW", "The court of Russia eases."),
            _row("intent_movement_tail", "LOW", "And 3 other courts stir.")])
        courts = [line for line in d.lines if line.startswith("- COURTS: ")]
        assert courts == ["- COURTS: The court of Austria hardens.",
                          "- COURTS: The court of Russia eases.",
                          "- COURTS: And 3 other courts stir."]
        assert not any(line.startswith("- DIPLO") for line in d.lines)
        assert not any("RAIL" in line for line in d.lines)

    def test_a_high_row_is_the_rails_alone_but_still_recorded(self):
        """No row prints twice: a HIGH row keeps its RAIL line and is neither
        a COURTS line nor counted in the tally — even a HIGH intent type."""
        d = _Recorder()
        d.dispatch("head", events=[_row("volte_face", "HIGH", "THE VOLTE-FACE"),
                                   _row("intent_hardens", "HIGH", "grave")])
        assert [line for line in d.lines if "RAIL" in line] == [
            "  - RAIL volte_face: THE VOLTE-FACE", "  - RAIL intent_hardens: grave"]
        assert not any(line.startswith(("- COURTS", "- DIPLO")) for line in d.lines)
        assert [r["dtype"] for r in d.records if r["kind"] == "dispatch_row"] == [
            "volte_face", "intent_hardens"]

    def test_the_tally_line_counts_what_was_not_printed(self):
        d = _Recorder()
        d.dispatch("head", events=MIXED)
        diplo = [line for line in d.lines if line.startswith("- DIPLO")]
        assert diplo == ["- DIPLO +3 medium/low (agenda_shift, diplomatic_dp_regen ×2)"]

    def test_no_tally_line_when_everything_was_printed(self):
        d = _Recorder()
        d.dispatch("head", events=[_row("volte_face", "HIGH"),
                                   _row("intent_eases", "LOW")])
        assert not any(line.startswith("- DIPLO") for line in d.lines)

    def test_every_row_is_recorded_outside_the_rail_cap(self):
        d = _Recorder()
        d.dispatch("head", events=MIXED)
        rows = [r for r in d.records if r["kind"] == "dispatch_row"]
        assert [(r["dtype"], r["priority"], r["text"]) for r in rows] == [
            (e["type"], e["priority"], e["text"]) for e in MIXED]
        assert any(line.startswith("  - RAIL +") for line in d.lines), (
            "the fixture overflows the rail cap")

    def test_lever_down_is_the_pre_iq6_digest_and_the_new_lines_only_follow(
            self, monkeypatch):
        """Lever up minus the new lines IS lever down, and every new line and
        record comes after the last old one."""
        up = _Recorder()
        up.dispatch("head", events=MIXED, turn_events=[{"t": 1}])
        monkeypatch.setattr(pdriver, "THE_DIGEST_READS_THE_WHOLE_DISPATCH", False)
        down = _Recorder()
        down.dispatch("head", events=MIXED, turn_events=[{"t": 1}])
        assert up.lines[:len(down.lines)] == down.lines
        assert up.records[:len(down.records)] == down.records
        new_lines = up.lines[len(down.lines):]
        assert new_lines and all(line.startswith(("- COURTS: ", "- DIPLO +"))
                                 for line in new_lines)
        new_records = up.records[len(down.records):]
        assert new_records and all(r["kind"] == "dispatch_row" for r in new_records)
        assert not any(line.startswith(("- COURTS", "- DIPLO")) for line in down.lines)
        assert not any(r["kind"] == "dispatch_row" for r in down.records)

    def _digest(self, tmp_path):
        return pdriver.Digest(tmp_path, {
            "name": "iq6", "seed": "historical", "llm": "mock",
            "transport": "stub", "policy": {}})

    def test_the_type_counts_accumulate_into_meta(self, tmp_path):
        digest = self._digest(tmp_path)
        meta = json.loads((tmp_path / "meta.json").read_text(encoding="utf-8"))
        assert meta["dispatch_type_counts"] == {}, "measured zero, not absent"
        digest.dispatch("a", events=MIXED)
        digest.dispatch("b", events=[_row("intent_eases", "LOW"),
                                     _row("volte_face", "HIGH")])
        digest._write_meta()
        meta = json.loads((tmp_path / "meta.json").read_text(encoding="utf-8"))
        counts = meta["dispatch_type_counts"]
        assert counts == {
            "agenda_shift": 1, "call_to_arms_refused_defensive": 1,
            "diplomatic_ai_proposal": pdriver.MAX_RAIL_ROWS + 1,
            "diplomatic_dp_regen": 2, "intent_eases": 2, "intent_hardens": 1,
            "intent_movement_tail": 1, "volte_face": 2}
        assert list(counts) == sorted(counts)

    def test_lever_down_meta_has_no_key(self, tmp_path, monkeypatch):
        monkeypatch.setattr(pdriver, "THE_DIGEST_READS_THE_WHOLE_DISPATCH", False)
        digest = self._digest(tmp_path)
        digest.dispatch("a", events=MIXED)
        digest._write_meta()
        meta = json.loads((tmp_path / "meta.json").read_text(encoding="utf-8"))
        assert "dispatch_type_counts" not in meta

    def test_every_priority_the_engine_grades_reaches_the_digest(self):
        """Census over the engine's own priority table: every type lands on
        the rail, on COURTS, or in the tally — and always in the jsonl."""
        assert len(_DIPLOMATIC_EVENT_PRIORITY) > 50
        for dtype, priority in _DIPLOMATIC_EVENT_PRIORITY.items():
            d = _Recorder()
            d.dispatch("head", events=[_row(dtype, priority)])
            if priority in pdriver.RAIL_PRIORITIES:
                assert any(line.startswith(f"  - RAIL {dtype}:") for line in d.lines)
            elif dtype in INTENT_TYPES:
                assert d.lines[-1] == f"- COURTS: {dtype} text"
            else:
                assert d.lines[-1] == f"- DIPLO +1 medium/low ({dtype})", (dtype, d.lines)
            assert [r["dtype"] for r in d.records if r["kind"] == "dispatch_row"] == [dtype]
        assert set(INTENT_TYPES) == set(pdriver.COURTS_DISPATCH_TYPES)
        for dtype in INTENT_TYPES:
            assert _DIPLOMATIC_EVENT_PRIORITY[dtype] not in pdriver.RAIL_PRIORITIES


# ═══════════════════════════════════════════════════════════════════════════
# T6 — N3: delivery end to end (the real run)
# ═══════════════════════════════════════════════════════════════════════════

class TestT6DeliveryEndToEnd:
    def test_the_end_turn_response_carries_intent_rows_within_five_loops(self, plain):
        """`commanded_full40 --diplomacy accept --seed historical`, five
        loops: the end-turn response's `morning_dispatch.diplomatic_events`
        carries the Stage-F lines at MEDIUM/LOW — the engine was never
        silent."""
        first_five = plain.ends[:5]
        assert len(first_five) == 5 and all(e["has_dispatch"] for e in first_five)
        rows = [r for e in first_five for r in e["rows"] if r["type"] in INTENT_TYPES]
        assert rows, first_five
        assert all(r["priority"] in ("MEDIUM", "LOW") for r in rows)

    def test_the_digest_prints_them_within_five_turns(self, plain):
        blocks = plain.blocks()
        courts = [line for turn in range(1, 6)
                  for line in blocks.get(turn, []) if line.startswith("- COURTS: ")]
        assert courts, "no COURTS line in the first five turns"
        assert not any("RAIL" in line for line in courts)

    @pytest.mark.parametrize("arm", ["plain", "courted"])
    def test_every_delivered_row_reaches_the_digest(self, arm, request):
        """What the end-turn responses carried is what the digest recorded,
        row for row: every row a `dispatch_row`, every Stage-F row a COURTS
        line, the per-type counts in meta."""
        run = request.getfixturevalue(arm)
        delivered = [r for e in run.ends for r in e["rows"]]
        recorded = [r for r in run.records if r.get("kind") == "dispatch_row"]
        assert [(r["type"], r["priority"]) for r in delivered] == [
            (r["dtype"], r["priority"]) for r in recorded]
        courts = [line for line in run.md.split("\n") if line.startswith("- COURTS: ")]
        intent = [r for r in delivered if r["type"] in INTENT_TYPES
                  and r["priority"] not in pdriver.RAIL_PRIORITIES]
        assert len(courts) == len(intent) >= 1
        counts = {}
        for r in delivered:
            counts[r["type"]] = counts.get(r["type"], 0) + 1
        assert run.meta["dispatch_type_counts"] == dict(sorted(counts.items()))

    @pytest.mark.parametrize("arm", ["plain", "courted", "window_down"])
    def test_the_engine_cap_bounds_the_courts_lines(self, arm, request):
        run = request.getfixturevalue(arm)
        for turn, lines in run.blocks().items():
            courts = [line for line in lines if line.startswith("- COURTS: ")]
            assert len(courts) <= INTENT_DISPATCH_CAP + 1, (turn, courts)


# ═══════════════════════════════════════════════════════════════════════════
# T7 — the committed courting script, end to end, as a subprocess (slow)
# ═══════════════════════════════════════════════════════════════════════════
# The assurance idiom: the real driver as its own process on the committed
# tree — no hook, no monkeypatch, PYTHONHASHSEED pinned. ~40 s.

@pytest.fixture(scope="module")
def t7_court(tmp_path_factory):
    root = tmp_path_factory.mktemp("iq6_t7_court")
    env = dict(os.environ)
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START",
                "PYTHONIOENCODING"):     # conftest's sentinel; the cp1252 trap
        env.pop(key, None)
    env.update({"LLM_MODE": "mock", "SOVEREIGN_SEED": "historical",
                "DEBUG_MODE": "false", "PYTHONHASHSEED": "0",
                "INK_IRON_SAVE_DIR": str(root / "saves"),
                "PYTHONPATH": str(REPO)})
    proc = subprocess.run(
        [sys.executable, str(DRIVER), "--name", "court", "--out", str(root),
         "--fresh", "--script", str(SCRIPTS / "volte_court_austria.json"),
         "--turns", "40", "--seed", "historical", "--diplomacy", "accept"],
        env=env, cwd=str(REPO), capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=900)
    assert proc.returncode == 0, (proc.stdout[-2000:], proc.stderr[-2000:])
    run = root / "court"
    return {
        "md": (run / "digest.md").read_text(encoding="utf-8"),
        "records": [json.loads(line) for line in
                    (run / "digest.jsonl").read_text(encoding="utf-8").splitlines()
                    if line.strip()],
        "meta": json.loads((run / "meta.json").read_text(encoding="utf-8")),
    }


class TestT7TheCommittedScript:
    def test_the_script_is_the_commanded_arm_plus_courting(self):
        court = json.loads((SCRIPTS / "volte_court_austria.json").read_text(encoding="utf-8"))
        base = json.loads((SCRIPTS / "commanded_full40.json").read_text(encoding="utf-8"))
        assert court["policy"] == base["policy"] and court["seed"] == base["seed"]
        assert set(court["turns"]) == set(base["turns"])
        for loop, orders in base["turns"].items():
            extra = [COURTING_ORDER] if int(loop) >= 5 else []
            assert court["turns"][loop] == extra + orders, loop

    def test_the_digest_carries_the_beat_exactly_once(self, t7_court):
        counts = t7_court["meta"]["dispatch_type_counts"]
        assert counts["volte_face"] == 1, counts
        logged = [r for r in t7_court["records"]
                  if r.get("kind") == "campaign_log" and r.get("dtype") == "volte_face"]
        assert len(logged) == 1 and COURT in logged[0]["text"], logged
        rail = [r for r in t7_court["records"]
                if r.get("kind") == "rail" and r.get("dtype") == "volte_face"]
        assert len(rail) == 1
        assert t7_court["md"].count("  - RAIL volte_face: ") == 1
        assert any(line.startswith("- COURTS: ") for line in t7_court["md"].split("\n"))

    def test_the_hooked_run_is_the_same_game(self, courted, courted_unhooked):
        """The in-process arms above READ through hooks; this proves they do
        not steer. The SAME script driven twice in the SAME process — once
        with every hook installed, once with none — writes the same digest,
        line for line, over every turn both played in full, the beat
        included.

        Why the control is in-process and not the subprocess (the pin's
        first form, September 14): a cross-process comparison carried two
        things this pin is not about — set-iteration order under a different
        PYTHONHASHSEED (the `strait_open` rows), and whatever process state
        thousands of earlier suite tests leave behind. It passed under hash
        seeds 1, 2, 3 and 7 in isolation and failed once inside the full
        pre-commit run. Both arms here share the process, so an exact
        comparison is the honest one; the cross-process claim lives in
        `test_the_subprocess_and_the_in_process_run_fire_the_same_beat`."""
        hooked = courted.blocks()
        control = courted_unhooked.blocks()
        shared = sorted(t for t in hooked if t in control)[:-1]    # last may carry the finish
        assert len(shared) >= 21
        for turn in shared:
            assert hooked[turn] == control[turn], turn
        assert any(line.startswith("  - RAIL volte_face: ")
                   for turn in shared for line in hooked[turn]), (
            "the compared span must include the beat")

    def test_the_subprocess_and_the_in_process_run_fire_the_same_beat(
            self, t7_court, courted):
        """Across processes (PYTHONHASHSEED=0 in the child, whatever this
        process has): the same script fires `volte_face` exactly once, on the
        same turn, and its meta tally agrees — order-independent facts about
        the GAME, not about display order."""
        assert t7_court["meta"]["dispatch_type_counts"]["volte_face"] == 1
        assert courted.meta["dispatch_type_counts"]["volte_face"] == 1

        def beat_turn(records):
            return [r.get("turn") for r in records
                    if r.get("kind") == "campaign_log" and r.get("dtype") == "volte_face"]

        assert beat_turn(t7_court["records"]) == beat_turn(courted.records)
        assert len(beat_turn(courted.records)) == 1
