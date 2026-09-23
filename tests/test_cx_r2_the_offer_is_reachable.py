"""CX-R2 — "The offer is reachable" (the Command-Road Queue, slice 4).

Build contract: `docs/audits/PARSER_AUTOFILL_ASSURANCE_2026_09_20.md`, row
CX-R, remediation item 4 (landing record appended there); row CQ-5 in
`docs/BUG_FIXES.md` §Command-Road Queue; rules `SYSTEMS_REFERENCE.md` §53.

THE RULE, ONE LAYER DEEPER
==========================
CX-3 landed *the game must not offer a sentence it cannot read*, and pinned
it at the PARSER, where it holds: 280 of 280 completer lines parse. This row
draws it one layer deeper — **the game must not offer a sentence it will
refuse** — because at the EXECUTOR, on the 1805 boot, 169 of those 280 were
refused (60.4%; the memo measured 59.3% on HEAD `15c498cb`): every target
pool ended in `out.sort()`, so a marshal at Rhineland was offered Albania,
Alentejo, Algiers; `attack` offered France's Bavarian ally and neutral
Prussia; `garrison <R>` named a province the executor never reads; and
`unfortify` / `drill` went to corps with no works and an enemy one march off.

Each slot now draws from the executor's own answer, nearest first — enemies
from `at_war_with_player`, marches over `passable_nations` and the open sea
crossings, moves from the move executor's own probe (`move_open`), scouting
within `scout_range`, the garrison on his own ground behind
`garrison_refusal`, and each no-target verb behind its `<verb>_refusal`.

HOW IT IS PROVED
================
`tools/cx_r2_completer_harness.gd` boots the REAL `main.tscn` headless,
hands the REAL map node the real `/map_topology` and the completer a real
board, and records what `_build_completions` offers for every prefix a
player can type — every verb of every marshal, every target list, the
continuations. This file sends EVERY offered line to POST /command on a
fresh copy of its board and reads the verdict. The boards: the 1805 boot,
a staged board (a fortified corps, room under the garrison cap, no enemy
one march off), and the turn-10 and turn-20 playtest fixtures. Skips
without the engine; a skip is not a pass — which is why the engine-free
classes below pin every payload field against the executor directly.

WHAT IS NOT CLOSED HERE, BY DECISION
====================================
A marshal's STATE refuses whole families of orders at once — fortified
(no move, no attack), locked in drill, recovering from a retreat, broken, a
prisoner, zero action points. That is the chips' CQ-21 class; the
completer's side is filed as CQ-24 with its own done-when and owner, and the
fixture pins below exempt exactly those marshals, BY NAME OF THE STATE,
with a pin that the exemption covers them and nobody else.
"""

import contextlib
import io
import json
import re
import subprocess
from collections import deque

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.commands.parser import CommandParser
from backend.display_names import humanize_entity_name
from backend.models.marshal import Stance
from tests import _chip_census as C

REPO = C.REPO
PROJECT = C.PROJECT
HARNESS = REPO / "tools" / "cx_r2_completer_harness.gd"
MAIN_GD = C.SCRIPTS / "main.gd"
FIXTURES = REPO / "tests" / "fixtures" / "playtest_saves"
BOARDS = ("boot", "staged", "t10", "t20")


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


# ═══════════════════════════════════════════════════════════════════════════
# The boards
# ═══════════════════════════════════════════════════════════════════════════
def stage_works(world):
    """The states the boot never shows: Davout dug in (unfortify is his to
    give; defend, fortify and drill are not), room under the garrison cap
    (Flanders' detachment withdrawn — the boot keeps exactly three), and the
    Austrians drawn off to Vienna (no enemy one march away, so drill opens
    and retreat closes)."""
    davout = world.get_marshal("Davout")
    davout.fortified = True
    davout.stance = Stance.DEFENSIVE
    davout.defense_bonus = 0.10
    flanders = world.get_region("Flanders")
    flanders.garrison_strength = 0
    flanders.garrison_detachment = False
    for name in ("Mack", "ArchdukeJohn"):
        world.get_marshal(name).location = "Vienna"
    C.refresh_view(world)


def load_board(name):
    """A fresh copy of the named board as the active world; returns a client."""
    with _quiet():
        if name in ("t10", "t20"):
            from backend.save_manager import load_game
            loaded = load_game(FIXTURES / f"fixture_{name}_ambient.json")
            assert loaded["success"], loaded["message"]
            M._set_active_world(loaded["world"])
        else:
            M._reset_world_state()
            if name == "staged":
                stage_works(M.world)
    M.parser = CommandParser(use_real_llm=False)
    return TestClient(M.app)


def topology_now():
    with _quiet():
        return TestClient(M.app).get("/map_topology").json()


def classify(response):
    """refused / staged (the executor asked the player something — an
    objection, a muster, an interrupt: the order was TAKEN) / executed."""
    if not response.get("success"):
        return "refused"
    if (response.get("state") in M._QUESTION_STATES
            or any(response.get(key) for key in M._QUESTION_KEYS)):
        return "staged"
    return "executed"


# ═══════════════════════════════════════════════════════════════════════════
# The completer, driven
# ═══════════════════════════════════════════════════════════════════════════
def _gd_table(name):
    source = MAIN_GD.read_text(encoding="utf-8")
    start = source.index(f"const {name} := [")
    open_at = source.index("[", start)
    depth = 0
    end = None
    for i in range(open_at, len(source)):
        if source[i] == "[":
            depth += 1
        elif source[i] == "]":
            depth -= 1
            if depth == 0:
                end = i
                break
    rows = re.findall(r"\[([^\]]*)\]", source[open_at + 1:end])
    return [[part.strip().strip('"') for part in row.split(",")] for row in rows]


VERBS = _gd_table("_MARSHAL_VERBS")


def shown_marshals(game_state):
    return sorted(humanize_entity_name(k) for k in game_state["marshals"])


def first_pass_prefixes(game_state):
    """Every verb of every marshal (typed to one letter short, so the verb
    itself is the offer), every target list, and the continuations that need
    no head target."""
    out = []
    for m in shown_marshals(game_state):
        for verb, slot, _action in VERBS:
            out.append(f"{m}, {verb[:-1]}")
            if slot:
                out.append(f"{m}, {verb} ")
        out.append(f"{m}, hold until ")
        out.append(f"{m}, hold for ")
    return out


# Probes on the boot board the per-verb sweep does not type: a half-typed
# head, a head no lawful road reaches (Hesse is at peace), a hold on such
# ground, and two reachable heads whose follow-on attack must be drawn
# nearest the DESTINATION.
BOOT_PROBES = [
    "Ney, march to Swa",
    "Ney, march to Nassau then a",
    "Ney, hold Nassau until ",
    "Ney, march to Lorraine then a",
    "Ney, march to Swabia then a",
    # Where the order FLIPS between the two origins, so drawing from the
    # wrong one is visible: from Milan Archduke John is nearer, from Bern
    # Mack is; from Rhineland Davout is nearest, from Lorraine Napoleon and
    # Soult are.
    "Massena, march to Bern then a",
    "Ney, hold Lorraine until ",
]


def synthetic_boards(staged_state):
    """Payloads the real boards never show, derived from the staged board and
    read by the CLIENT only (they are never sent to the executor):

    * `prisoner` — Ney off the map: he stays in `marshals` (as a captured
      marshal does, and as one on administrative duty does — the payload
      still names where he is) but stands on no map square, so he takes no
      field order and can be neither supported nor awaited. He is placed at
      LORRAINE, where Soult stands: a captive sits at his captor's capital,
      far beyond the five-offer cap, and the first sweep proved a distant
      Ney left the pin INERT (the cap, not the rule, kept him out). A marshal
      on administrative duty can stand this close.
    * `stale` / `partial` — Mack sighted one march from Ney (Swabia), once as
      a STALE sighting (not a position — no retreat is offered) and once
      seen now (the control that makes the first non-vacuous).
    * `far` — Mack seen now, two marches off (Munich): no danger, no retreat.
    * `blind` — Ney's scouting reach at 0: no province is in reach, so no
      scout is offered (on the real boards the five nearest provinces are
      always within reach, so the range cap is otherwise never seen)."""
    import copy
    out = {}
    prisoner = copy.deepcopy(staged_state)
    prisoner["marshals"]["Ney"]["location"] = "Lorraine"
    for region in prisoner["map_data"].values():
        region["marshals"] = [m for m in region.get("marshals", [])
                              if m.get("name") != "Ney"]
    out["prisoner"] = (prisoner, ["Ney, a", "Ney, attack ", "Ney, hol",
                                  "Soult, support ", "Soult, hold until "])
    for fog in ("stale", "partial"):
        board = copy.deepcopy(staged_state)
        board["enemies"]["Mack"] = {
            "location": "Swabia", "nation": "Austria", "strength": 0,
            "strength_band": "large", "fog_level": fog,
            "at_war_with_player": True}
        out[fog] = (board, ["Ney, retrea"])
    far = copy.deepcopy(staged_state)
    far["enemies"]["Mack"] = {
        "location": "Munich", "nation": "Austria", "strength": 0,
        "strength_band": "large", "fog_level": "partial",
        "at_war_with_player": True}
    out["far"] = (far, ["Ney, retrea"])
    blind = copy.deepcopy(staged_state)
    for m in blind["map_data"]["Rhineland"]["marshals"]:
        if m.get("name") == "Ney":
            m["tactical_state"]["scout_range"] = 0
    out["blind"] = (blind, ["Ney, scou", "Ney, scout "])
    return out


def drive(boards, work):
    """Run the harness once over `boards` = {name: (game_state, prefixes)};
    returns ({name: {prefix: [offers]}}, SCRIPT ERROR count, topology size)."""
    exe = C.engine()
    if exe is None:
        pytest.skip("Godot engine not on this machine — the driven pins skip, "
                    "and a skip is not a pass")
    out = work / "offers.json"
    log = work / "godot.log"
    spec = work / "spec.json"
    spec.write_text(json.dumps({
        "topology": boards["__topology__"],
        "boards": {name: {"game_state": pair[0], "prefixes": pair[1]}
                   for name, pair in boards.items()
                   if name != "__topology__"},
        "out": str(out)}), encoding="utf-8")
    import os
    env = dict(os.environ, CXR2_SPEC=str(spec))
    proc = subprocess.run(
        [exe, "--headless", "--path", str(PROJECT), "--log-file", str(log),
         "--script", str(HARNESS)],
        capture_output=True, text=True, timeout=300, env=env, cwd=str(PROJECT))
    if not out.is_file():
        pytest.fail("the harness wrote no result\n"
                    f"exit={proc.returncode}\nstderr tail:\n{proc.stderr[-2000:]}")
    result = json.loads(out.read_text(encoding="utf-8"))
    assert "error" not in result, result.get("error")
    text = log.read_text(encoding="utf-8", errors="replace") if log.is_file() else ""
    return result["offers"], text.count("SCRIPT ERROR"), int(result["topology_regions"])


def complete_lines(offers):
    """Every offered line that is a whole command (a verb completion ends in
    a space, waiting for its target)."""
    lines = []
    for got in offers.values():
        for line in got:
            if not str(line).endswith(" ") and line not in lines:
                lines.append(line)
    return lines


@pytest.fixture(scope="module")
def offered(tmp_path_factory):
    """The completer driven over the four boards and the synthetic payloads —
    what it OFFERS, nothing sent yet."""
    work = tmp_path_factory.mktemp("cxr2")
    with pytest.MonkeyPatch.context() as mp:
        C.board_env(mp)
        states, first = {}, {}
        for name in BOARDS:
            load_board(name)
            states[name] = C.game_state_now()
            first[name] = (states[name], first_pass_prefixes(states[name]))
        first["boot"][1].extend(BOOT_PROBES)
        first.update(synthetic_boards(states["staged"]))
        first["__topology__"] = topology_now()
        offers, errors, regions = drive(first, work)
        # The second pass: the two-step order, headed by the nearest march.
        second = {"__topology__": first["__topology__"]}
        for name in BOARDS:
            prefixes = []
            for m in shown_marshals(states[name]):
                marches = [line for line in offers[name].get(f"{m}, march to ", [])]
                if marches:
                    prefixes.append(marches[0] + " then attack ")
            second[name] = (states[name], prefixes)
        work2 = tmp_path_factory.mktemp("cxr2b")
        offers2, errors2, _ = drive(second, work2)
        for name in BOARDS:
            offers[name].update(offers2[name])
    return {"offers": offers, "states": states,
            "errors": errors + errors2, "regions": regions}


@pytest.fixture(scope="module")
def driven(offered):
    """Every line the completer offered on a real board, sent to POST
    /command on a fresh copy of that board. (The synthetic payloads are the
    client's alone — never scored.)"""
    verdicts = {}
    with pytest.MonkeyPatch.context() as mp:
        C.board_env(mp)
        for name in BOARDS:
            rows = []
            for line in complete_lines(offered["offers"][name]):
                client = load_board(name)
                response = C.post(client, {"command": line})
                rows.append({"line": line, "verdict": classify(response),
                             "message": (response.get("message") or "")[:200]})
            verdicts[name] = rows
    return dict(offered, verdicts=verdicts)


def _garrisons_offered(offered):
    """Every garrison line offered on the staged board — each names the
    province its marshal STANDS in."""
    staged = offered["offers"]["staged"]
    gs = offered["states"]["staged"]
    lines = []
    for m in shown_marshals(gs):
        got = staged[f"{m}, garrison "]
        if got:
            where = gs["marshals"][m]["location"]
            assert got == [f"{m}, garrison {where}"], (m, got)
            lines.append(got[0])
    return lines


def _refused(driven, board):
    return [(r["line"], r["message"][:90]) for r in driven["verdicts"][board]
            if r["verdict"] == "refused"]


def _who(line):
    return line.split(",", 1)[0]


# ═══════════════════════════════════════════════════════════════════════════
# 1. No offer is refused
# ═══════════════════════════════════════════════════════════════════════════
class TestNoOfferIsRefused:

    def test_the_boot_board_offers_nothing_the_executor_refuses(self, driven):
        """The memo's own board: 169 of 280 refused before. Now none — and
        the scored set is substantial, or the zero is vacuous."""
        rows = driven["verdicts"]["boot"]
        assert len(rows) >= 150, len(rows)
        assert _refused(driven, "boot") == []

    def test_most_boot_offers_execute_outright(self, driven):
        """The rest STAGE a question — an objection, a muster, an interrupt:
        the order was taken and the marshal answered in character (Ney does
        not like to dig in). The memo's executed share was 28.6%."""
        rows = driven["verdicts"]["boot"]
        executed = sum(1 for r in rows if r["verdict"] == "executed")
        assert executed / len(rows) >= 0.75, (executed, len(rows))

    @pytest.mark.parametrize("board", ["staged", "t10", "t20"])
    def test_a_board_refuses_only_a_marshal_whose_state_refuses_the_order(
            self, driven, board, env):
        """CQ-24's class — a marshal whose STATE refuses whole families of
        orders (fortified: no move; recovering from a retreat: no attack, no
        scout, no standing order) — exempted by the state, never by the
        line. Everything else offered on these boards is taken."""
        rows = driven["verdicts"][board]
        assert len(rows) >= 120, len(rows)
        blocked = self._state_gated(board)
        bad = [(line, msg) for line, msg in _refused(driven, board)
               if _who(line) not in blocked]
        assert bad == [], bad[:6]

    @pytest.mark.parametrize("board,who", [("staged", "Davout"), ("t20", "Bernadotte")])
    def test_the_state_exemption_is_earned_and_narrow(self, driven, env, board, who):
        """Each board where it applies carries exactly one state-gated corps —
        Davout dug in on the staged board, Bernadotte recovering from a
        retreat on t20 — whose offers ARE refused (the exemption is not
        vacuous), and it covers nobody else."""
        assert self._state_gated(board) == {who}
        assert any(_who(line) == who for line, _m in _refused(driven, board)), who

    def test_the_boot_and_t10_have_no_state_gated_corps(self, driven, env):
        """So their zero refusals are not an exemption at work."""
        assert self._state_gated("boot") == set()
        assert self._state_gated("t10") == set()
        assert _refused(driven, "t10") == []

    def test_every_continuation_offered_is_taken(self, driven):
        for board in ("boot", "staged"):
            rows = [r for r in driven["verdicts"][board]
                    if " then attack " in r["line"] or " until " in r["line"]
                    or " for 3 turns" in r["line"]]
            assert rows, board
            assert [r for r in rows if r["verdict"] == "refused"] == [], board

    def test_the_fortified_corps_takes_the_order_he_is_offered(self, driven):
        verdicts = {r["line"]: r["verdict"] for r in driven["verdicts"]["staged"]}
        assert verdicts["Davout, unfortify"] == "executed"

    def test_every_garrison_offered_is_left_where_he_stands(self, driven):
        lines = _garrisons_offered(driven)
        verdicts = {r["line"]: r["verdict"] for r in driven["verdicts"]["staged"]}
        assert lines and all(verdicts[line] == "executed" for line in lines), lines

    @staticmethod
    def _state_gated(board):
        load_board(board)
        world = M.world
        out = set()
        for m in world.marshals.values():
            if m.nation != world.player_nation:
                continue
            if (getattr(m, "retreating", False) or getattr(m, "broken", False)
                    or getattr(m, "fortified", False)
                    or getattr(m, "drilling_locked", False)
                    or m.strength <= 0):
                out.add(humanize_entity_name(m.name))
        return out


# ═══════════════════════════════════════════════════════════════════════════
# 2. The offer is the NEAREST, and it is reachable
# ═══════════════════════════════════════════════════════════════════════════
def _bfs(world, origin, passable=None, closed=frozenset()):
    dist = {origin: 0}
    queue = deque([origin])
    while queue:
        here = queue.popleft()
        for nxt in world.regions[here].adjacent_regions:
            if nxt in dist or frozenset((here, nxt)) in closed:
                continue
            holder = world.regions[nxt].controller
            if passable is not None and holder and holder not in passable:
                continue
            dist[nxt] = dist[here] + 1
            queue.append(nxt)
    return dist


def _closed_links(game_state):
    overlay = game_state.get("naval_overlay") or {}
    return frozenset(
        frozenset((v["link_a"], v["link_b"]))
        for v in overlay.get("sea_link_verdicts", [])
        if v["verdict"] not in ("open", "open_ratio", "window"))


def _nearest(names_at, dist, n=5):
    ranked = sorted((dist[place], shown) for shown, place in names_at
                    if place in dist)
    return [shown for _d, shown in ranked][:n]


class TestTheOfferIsNearest:
    """An independent Python computation of every pool, against what the
    real completer offered — a drift pin between the two implementations."""

    def test_the_harness_ran_clean(self, offered):
        assert offered["errors"] == 0
        assert offered["regions"] == 126

    @pytest.mark.parametrize("board", BOARDS)
    def test_the_march_offers_are_the_nearest_lawful_provinces(self, offered, board, env):
        gs = offered["states"][board]
        load_board(board)
        world = M.world
        passable = set(gs["passable_nations"])
        closed = _closed_links(gs)
        checked = 0
        for key, row in gs["marshals"].items():
            shown = humanize_entity_name(key)
            got = offered["offers"][board].get(f"{shown}, march to ")
            if got is None or not self._on_map(gs, key):
                continue
            dist = _bfs(world, row["location"], passable, closed)
            dist.pop(row["location"], None)
            want = _nearest([(p, p) for p in dist], dist)
            assert got == [f"{shown}, march to {p}" for p in want], (board, shown)
            checked += 1
        assert checked >= 5

    @pytest.mark.parametrize("board", BOARDS)
    def test_the_move_offers_are_the_move_executors_own(self, offered, board, env):
        gs = offered["states"][board]
        load_board(board)
        world = M.world
        checked = 0
        for key, row in gs["marshals"].items():
            entry = self._on_map(gs, key)
            if not entry:
                continue
            shown = humanize_entity_name(key)
            dist = _bfs(world, row["location"])
            want = _nearest([(p, p) for p in entry["tactical_state"]["move_open"]], dist)
            got = offered["offers"][board].get(f"{shown}, move to ")
            assert got == [f"{shown}, move to {p}" for p in want], (board, shown)
            checked += 1
        assert checked >= 5

    @pytest.mark.parametrize("board", BOARDS)
    def test_the_scout_offers_are_within_his_range_nearest_first(self, offered, board, env):
        gs = offered["states"][board]
        load_board(board)
        world = M.world
        for key, row in gs["marshals"].items():
            entry = self._on_map(gs, key)
            if not entry:
                continue
            shown = humanize_entity_name(key)
            reach = entry["tactical_state"]["scout_range"]
            dist = _bfs(world, row["location"])
            dist.pop(row["location"], None)
            want = _nearest([(p, p) for p, d in dist.items() if d <= reach], dist)
            got = offered["offers"][board].get(f"{shown}, scout ")
            assert got == [f"{shown}, scout {p}" for p in want], (board, shown)

    @pytest.mark.parametrize("board", BOARDS)
    def test_the_attack_offers_are_enemies_at_war_nearest_first(self, offered, board, env):
        gs = offered["states"][board]
        load_board(board)
        world = M.world
        passable = set(gs["passable_nations"])
        closed = _closed_links(gs)
        for key, row in gs["marshals"].items():
            if not self._on_map(gs, key):
                continue
            shown = humanize_entity_name(key)
            dist = _bfs(world, row["location"], passable, closed)
            at_war = [(humanize_entity_name(k), e["location"])
                      for k, e in gs["enemies"].items() if e["at_war_with_player"]]
            want = _nearest(at_war, dist)
            got = offered["offers"][board].get(f"{shown}, attack ", [])
            assert got == [f"{shown}, attack {e}" for e in want], (board, shown)

    def test_the_boot_offers_no_court_at_peace_or_in_alliance(self, offered):
        """The memo's done-when, verbatim: `attack` offers no court at PEACE
        or ALLIANCE — Deroy (Bavaria, France's ally) and Brunswick (Prussia,
        at peace) are visible at the boot and are never offered."""
        lines = [line for got in offered["offers"]["boot"].values() for line in got]
        assert any(", attack Mack" in line for line in lines)
        for enemy in ("Deroy", "Brunswick"):
            assert not any(f"attack {enemy}" in line for line in lines), enemy

    def test_a_province_no_lawful_road_reaches_is_never_a_march(self, offered):
        """Hesse is at peace with France and stands beside the Rhine corps —
        the nearest provinces to Ney are Hesse's Nassau and Frankfurt."""
        got = offered["offers"]["boot"]["Ney, march to "]
        assert got[:3] == ["Ney, march to Brabant", "Ney, march to Gelderland",
                           "Ney, march to Lorraine"], got
        assert not any(p in line for line in got for p in ("Nassau", "Frankfurt"))

    @staticmethod
    def _on_map(gs, key):
        where = gs["marshals"][key]["location"]
        for m in gs["map_data"].get(where, {}).get("marshals", []):
            if m.get("name") == key:
                return m
        return None


# ═══════════════════════════════════════════════════════════════════════════
# 3. The no-target verbs read their own gates
# ═══════════════════════════════════════════════════════════════════════════
class TestTheNoTargetVerbsReadTheirGates:

    def test_the_boot_offers_no_unfortify_no_drill_no_garrison(self, offered):
        """Nobody is dug in; every corps stands one march from Mack or John;
        France keeps its three garrisons — so none of the three is offered."""
        boot = offered["offers"]["boot"]
        for m in shown_marshals(offered["states"]["boot"]):
            assert boot[f"{m}, unfortif"] == []
            assert boot[f"{m}, dril"] == []
            assert boot[f"{m}, garriso"] == []

    def test_a_fortified_corps_is_offered_its_one_move(self, offered):
        staged = offered["offers"]["staged"]
        assert staged["Davout, unfortif"] == ["Davout, unfortify"]
        assert staged["Davout, fortif"] == []
        assert staged["Davout, defen"] == []
        assert staged["Davout, dril"] == []

    def test_with_room_under_the_cap_the_garrison_is_his_own_ground(self, offered):
        assert len(_garrisons_offered(offered)) >= 4

    def test_no_enemy_near_opens_the_drill_and_closes_the_retreat(self, offered):
        staged = offered["offers"]["staged"]
        assert staged["Ney, dril"] == ["Ney, drill"]
        assert staged["Ney, retrea"] == []
        boot = offered["offers"]["boot"]
        assert boot["Ney, retrea"] == ["Ney, retreat"]


# ═══════════════════════════════════════════════════════════════════════════
# 4. The continuations
# ═══════════════════════════════════════════════════════════════════════════
class TestTheContinuations:

    def test_typing_the_continuation_keeps_it_offered(self, offered):
        """The cut read `hold until ` as a province called "until" — every
        offer vanished at the word the continuation is built for."""
        boot = offered["offers"]["boot"]
        until = boot["Ney, hold until "]
        assert until and all(line.startswith("Ney, hold until ") and
                             line.endswith(" arrives") for line in until), until
        assert until[0] == "Ney, hold until Davout arrives"   # his own province
        assert boot["Ney, hold for "] == ["Ney, hold for 3 turns"]

    def test_the_attack_is_drawn_nearest_the_destination(self, offered):
        boot = offered["offers"]["boot"]
        heads = [p for p in boot if p.endswith(" then attack ")]
        assert heads, "no continuation was offered"
        for prefix in heads:
            got = boot[prefix]
            assert got and all(line.startswith(prefix) for line in got), prefix

    def test_a_half_typed_head_offers_no_continuation(self, offered):
        got = offered["offers"]["boot"]["Ney, march to Swa"]
        assert got == ["Ney, march to Swabia"], got

    def test_a_head_no_lawful_road_reaches_offers_nothing(self, offered):
        """Nassau is Hesse's, at peace: a march there is refused, so neither
        the two-step order nor a hold there is offered — while the same
        probe on French Lorraine is."""
        boot = offered["offers"]["boot"]
        assert boot["Ney, march to Nassau then a"] == []
        assert boot["Ney, hold Nassau until "] == []
        assert boot["Ney, march to Lorraine then a"], "the control offered nothing"

    def test_the_follow_on_attack_is_nearest_the_destination(self, offered, env):
        """Drawn over the lawful road from where the march ENDS, not from
        where he stands — Mack holds Swabia, so at Swabia he comes first."""
        boot = offered["offers"]["boot"]
        gs = offered["states"]["boot"]
        load_board("boot")
        closed = _closed_links(gs)
        passable = set(gs["passable_nations"])
        at_war = [(humanize_entity_name(k), e["location"])
                  for k, e in gs["enemies"].items() if e["at_war_with_player"]]
        for dest in ("Lorraine", "Swabia"):
            dist = _bfs(M.world, dest, passable, closed)
            want = [f"Ney, march to {dest} then attack {e}"
                    for e in _nearest(at_war, dist)]
            assert boot[f"Ney, march to {dest} then a"] == want, dest
        assert boot["Ney, march to Swabia then a"][0].endswith("then attack Mack")

    def test_the_attack_is_drawn_from_where_the_march_ends(self, offered):
        """From Milan, Archduke John is nearer; from Bern, Mack is — the
        order the two-step line offers is the destination's."""
        got = offered["offers"]["boot"]["Massena, march to Bern then a"]
        assert got == ["Massena, march to Bern then attack Mack",
                       "Massena, march to Bern then attack Archduke John"], got

    def test_the_awaited_marshal_is_drawn_from_the_ground_held(self, offered):
        """Holding Lorraine, Napoleon and Soult stand ON it; from Rhineland,
        where Ney stands, Davout would come first."""
        got = offered["offers"]["boot"]["Ney, hold Lorraine until "]
        assert got[:2] == ["Ney, hold Lorraine until Napoleon arrives",
                           "Ney, hold Lorraine until Soult arrives"], got



class TestWhatTheMapDoesNotShowIsNotOffered:
    """Client-only payloads (see `synthetic_boards`)."""

    def test_a_prisoner_takes_no_field_order(self, offered):
        board = offered["offers"]["prisoner"]
        assert board["Ney, a"] == [] and board["Ney, attack "] == []
        assert board["Ney, hol"] == []

    def test_a_prisoner_is_neither_supported_nor_awaited(self, offered):
        board = offered["offers"]["prisoner"]
        assert board["Soult, support "], "the control offered nothing"
        assert not any(line.endswith(" Ney") for line in board["Soult, support "])
        assert board["Soult, hold until "], "the control offered nothing"
        assert not any("until Ney arrives" in line
                       for line in board["Soult, hold until "])

    def test_an_enemy_two_marches_off_is_no_danger(self, offered):
        assert offered["offers"]["far"]["Ney, retrea"] == []

    def test_no_province_in_reach_offers_no_scout(self, offered):
        board = offered["offers"]["blind"]
        assert board["Ney, scou"] == [] and board["Ney, scout "] == []

    def test_a_stale_sighting_is_no_danger(self, offered):
        """A STALE sighting is where Mack WAS. The executor's danger test
        reads where he is; the completer may not guess, so it offers no
        retreat on it — and offers one on the same corps seen now."""
        assert offered["offers"]["stale"]["Ney, retrea"] == []
        assert offered["offers"]["partial"]["Ney, retrea"] == ["Ney, retreat"]


# ═══════════════════════════════════════════════════════════════════════════
# 5. The payload IS the executor (engine-free)
# ═══════════════════════════════════════════════════════════════════════════
@pytest.fixture
def env(monkeypatch):
    C.board_env(monkeypatch)
    return monkeypatch


def _player_entries(game_state):
    out = {}
    for where, region in game_state["map_data"].items():
        for m in region.get("marshals", []):
            if m.get("nation") == game_state["player_nation"]:
                out[m["name"]] = (where, m["tactical_state"])
    return out


class TestThePayloadIsTheExecutor:

    def test_at_war_with_player_is_is_at_war_on_every_enemy(self, env):
        load_board("boot")
        gs = C.game_state_now()
        world = M.world
        assert gs["enemies"], "no enemy visible — the pin is vacuous"
        for key, row in gs["enemies"].items():
            want = world.is_at_war(world.player_nation, row["nation"])
            assert row["at_war_with_player"] is want, key
        assert {k for k, r in gs["enemies"].items() if not r["at_war_with_player"]} \
            >= {"Deroy", "Brunswick"}

    def test_a_fogged_enemy_carries_the_flag_too(self, env):
        load_board("boot")
        gs = C.game_state_now()
        fogged = {k: r for k, r in gs["enemies"].items() if "fog_level" in r}
        assert fogged, "no PARTIAL enemy on the boot — the fog arm is untested"
        for key, row in fogged.items():
            assert "at_war_with_player" in row, key

    def test_passable_nations_is_can_enter_territory(self, env):
        from backend.game_logic.diplomacy import can_enter_territory
        load_board("boot")
        gs = C.game_state_now()
        world = M.world
        want = sorted(n for n in set(world.get_active_nations()) | {"France"}
                      if can_enter_territory(world, "France", n,
                                             ignore_evacuation=True))
        assert gs["passable_nations"] == want
        assert "Hesse" not in want and "Bavaria" in want

    def test_a_march_onto_soil_that_is_not_passable_is_refused(self, env):
        client = load_board("boot")
        response = C.post(client, {"command": "Ney, march to Nassau"})
        assert not response.get("success")
        assert "Cannot enter Nassau" in response["message"]

    @pytest.mark.parametrize("name", ["boot", "staged"])
    def test_move_open_is_what_the_move_executor_takes(self, env, name):
        """Every province within a marshal's reach, driven: `move to P` is
        refused exactly when P is not in `move_open`. A fortified corps is
        CQ-24's (his state refuses every move) and is left out, by name."""
        load_board(name)
        entries = _player_entries(C.game_state_now())
        checked = 0
        for key, (where, state) in entries.items():
            if key == "Davout" and name == "staged":
                continue
            client = load_board(name)
            marshal = M.world.get_marshal(key)
            reach = int(getattr(marshal, "movement_range", 1) or 1)
            dist = _bfs(M.world, where)
            for province, d in sorted(dist.items()):
                if d == 0 or d > reach:
                    continue
                client = load_board(name)
                response = C.post(client, {"command": f"{humanize_entity_name(key)}, move to {province}"})
                took = classify(response) != "refused"
                assert took == (province in state["move_open"]), (
                    name, key, province, response.get("message", "")[:100])
                checked += 1
        assert checked >= 20, checked

    @pytest.mark.parametrize("name", ["boot", "staged"])
    def test_the_verb_gates_are_what_the_executor_takes(self, env, name):
        load_board(name)
        entries = _player_entries(C.game_state_now())
        seen = {"garrison": set(), "unfortify": set(), "defend": set()}
        for key, (where, state) in entries.items():
            shown = humanize_entity_name(key)
            for verb, line in (("garrison", f"{shown}, garrison {where}"),
                               ("unfortify", f"{shown}, unfortify"),
                               ("defend", f"{shown}, defend")):
                client = load_board(name)
                response = C.post(client, {"command": line})
                took = classify(response) != "refused"
                assert took == (state[f"{verb}_refusal"] == ""), (
                    name, line, state[f"{verb}_refusal"], response.get("message", "")[:100])
                seen[verb].add(took)
        if name == "staged":
            assert seen["garrison"] == {True, False}
            assert seen["unfortify"] == {True, False}
            assert seen["defend"] == {True, False}

    def test_the_defend_refusal_comes_before_any_objection(self, env, monkeypatch):
        """The battery reads `defend_refusal` BEFORE the objection roll (the
        roll forced to STRONG, CN-4's pattern): a dug-in defensive Davout is
        refused in the executor's words and raises nothing; Ney, free to
        defend, draws the forced objection — the control that the patch is
        live."""
        import backend.commands.executor as X
        monkeypatch.setattr(X, "evaluate_situation",
                            lambda *a, **k: X.ConcernLevel.STRONG)
        monkeypatch.setattr(X, "apply_mood_variance", lambda concern: concern)
        client = load_board("staged")
        response = C.post(client, {"command": "Davout, defend"})
        assert not response.get("success"), response.get("message")
        assert "already defending and fortified" in response["message"]
        assert not M.world.pending_objection
        C.post(client, {"command": "Ney, defend"})
        assert (M.world.pending_objection or {}).get("marshal") == "Ney"

    def test_a_locked_drill_refuses_defend_on_both_roads(self, env, monkeypatch):
        """Turn two of a drill: only RETREAT is allowed. The player's road
        is refused before any objection (by the battery's broader
        locked-drill gate, which stands ahead of every order); the
        executor's own road — the AI's, which skips the battery — refuses
        through `defend_refusal`, and the drill is NOT cancelled on the way
        (the drill-cancel below the gate no longer asks about the lock)."""
        import backend.commands.executor as X
        from backend.commands.tactical_executor import TacticalExecutor
        monkeypatch.setattr(X, "evaluate_situation",
                            lambda *a, **k: X.ConcernLevel.STRONG)
        monkeypatch.setattr(X, "apply_mood_variance", lambda concern: concern)
        client = load_board("boot")
        turn = M.world.current_turn
        ney = M.world.get_marshal("Ney")
        ney.drilling, ney.drilling_locked = True, True
        ney.drill_complete_turn = turn + 1
        response = C.post(client, {"command": "Ney, defend"})
        assert not response.get("success")
        assert "locked in drill" in response["message"]
        assert not M.world.pending_objection
        mack = M.world.get_marshal("Mack")
        mack.drilling, mack.drilling_locked = True, True
        mack.drill_complete_turn = turn + 1
        result = TacticalExecutor(M.executor)._execute_defend(
            mack, M.world, {"world": M.world})
        assert result["success"] is False and result.get("drilling_locked") is True
        assert mack.drilling is True

    def test_scout_range_is_where_the_scout_stops(self, env):
        load_board("boot")
        entries = _player_entries(C.game_state_now())
        checked = 0
        for key, (where, state) in entries.items():
            reach = state["scout_range"]
            dist = _bfs(M.world, where)
            edge = sorted(p for p, d in dist.items() if d == reach)
            beyond = sorted(p for p, d in dist.items() if d == reach + 1)
            if not edge or not beyond:
                continue
            shown = humanize_entity_name(key)
            ok = C.post(load_board("boot"), {"command": f"{shown}, scout {edge[0]}"})
            no = C.post(load_board("boot"), {"command": f"{shown}, scout {beyond[0]}"})
            assert classify(ok) != "refused", (shown, edge[0], ok.get("message"))
            assert classify(no) == "refused" and "too far" in no["message"], (shown, beyond[0])
            checked += 1
        assert checked >= 5
        ranges = {state["scout_range"] for _w, state in entries.values()}
        assert ranges == {2, 3}, ranges   # the cautious kit's +1 is read

    def test_move_open_never_refuses_for_an_enemy_the_player_cannot_see(self, env):
        """The probe refuses only an enemy the player can SEE, so the payload
        says nothing the map does not. Murat (cavalry, reach 2): put an
        Austrian corps two marches off in a province France cannot see and
        it stays in his `move_open` — exactly as the move executor would
        walk him into it blind — while the same corps in a province France
        CAN see closes it. (At the boot all of his reach is in view, so the
        blind province is staged by fogging one.)"""
        from backend.models.world_state import _move_open_of
        load_board("boot")
        world = M.world
        murat = world.get_marshal("Murat")
        assert int(murat.movement_range) >= 2
        dist = _bfs(world, murat.location)
        open_before = sorted(_move_open_of(world, murat))
        two_off = [p for p in open_before if dist[p] == 2]
        assert len(two_off) >= 2, two_off
        blind, lit = two_off[0], two_off[1]
        world._intel_entry(blind).visibility = "unknown"
        assert world.get_region_intel(lit).visibility in ("full", "partial")
        mack = world.get_marshal("Mack")
        mack.location = blind
        assert blind in _move_open_of(world, murat), blind
        mack.location = lit
        assert lit not in _move_open_of(world, murat), lit


# ═══════════════════════════════════════════════════════════════════════════
# 6. A garrison is left where the corps stands
# ═══════════════════════════════════════════════════════════════════════════
class TestTheGarrisonIsLeftWhereTheCorpsStands:

    @staticmethod
    def _room():
        client = load_board("boot")
        flanders = M.world.get_region("Flanders")
        flanders.garrison_strength = 0
        flanders.garrison_detachment = False
        return client

    def test_a_province_he_does_not_stand_in_is_refused_with_the_road(self, env):
        client = self._room()
        ney = M.world.get_marshal("Ney")
        before = (ney.strength, M.world.get_region("Rhineland").garrison_strength)
        response = C.post(client, {"command": "Ney, garrison Bohemia"})
        assert not response.get("success")
        assert "stands at Rhineland" in response["message"]
        assert "March him to Bohemia first" in response["message"]
        assert (ney.strength, M.world.get_region("Rhineland").garrison_strength) == before

    @pytest.mark.parametrize("line", ["Ney, garrison Rhineland", "Ney, garrison",
                                      "Ney, garrison this province"])
    def test_his_own_ground_is_garrisoned(self, env, line):
        client = self._room()
        response = C.post(client, {"command": line})
        assert response.get("success"), response.get("message")
        assert M.world.get_region("Rhineland").garrison_strength > 0

    def test_a_nation_named_gets_the_region_matchers_answer(self, env):
        client = self._room()
        ney = M.world.get_marshal("Ney")
        before = ney.strength
        response = C.post(client, {"command": "Ney, garrison Austria"})
        assert not response.get("success")
        assert ney.strength == before
        assert M.world.get_region("Rhineland").garrison_strength == 0

    def test_the_ai_road_names_no_province_and_is_unchanged(self, env):
        """P6.75 sends `{marshal, action: garrison}` and nothing else, so the
        new refusal cannot fire for it (GR5 unchanged, and the series with
        it)."""
        from backend.ai import enemy_ai
        import inspect
        src = inspect.getsource(enemy_ai)
        emitted = re.findall(r'"action": "garrison"[^}]*}', src)
        assert emitted, "the AI's garrison order was not found"
        assert all('"target"' not in chunk and '"region"' not in chunk
                   for chunk in emitted), emitted


# ═══════════════════════════════════════════════════════════════════════════
# 7. "This province" is not Provence
# ═══════════════════════════════════════════════════════════════════════════
class TestThisProvinceIsNotProvence:

    def test_the_scout_no_longer_names_provence(self, env):
        client = load_board("boot")
        response = C.post(client, {"command": "Ney, scout this province"})
        assert "Provence" not in (response.get("message") or "")

    @pytest.mark.parametrize("word", ["province", "provinces", "region",
                                      "regions", "territory", "territories"])
    def test_the_common_nouns_for_a_place_are_not_targets(self, word):
        from backend.commands.parser import _NON_TARGET_WORDS
        assert word in _NON_TARGET_WORDS

    def test_provence_by_name_still_resolves(self, env):
        client = load_board("boot")
        response = C.post(client, {"command": "Ney, scout Provence"})
        assert "Provence" in (response.get("message") or "")


# ═══════════════════════════════════════════════════════════════════════════
# 8. The table, the gates and the verdicts agree (source)
# ═══════════════════════════════════════════════════════════════════════════
class TestTheTableAndTheGatesAgree:

    def test_every_slot_letter_is_known(self):
        assert {slot for _v, slot, _a in VERBS} <= {"", "E", "R", "A", "S", "H", "M"}
        slots = {verb: slot for verb, slot, _a in VERBS}
        assert slots["move to"] == "A" and slots["scout"] == "S"
        assert slots["garrison"] == "H" and slots["march to"] == "R"

    def test_every_gated_verb_reads_a_field_the_payload_ships(self, env):
        source = MAIN_GD.read_text(encoding="utf-8")
        block = source[source.index("const _VERB_GATE_FIELD := {"):]
        block = block[:block.index("}")]
        pairs = dict(re.findall(r'"(\w+)": "(\w+)"', block))
        no_target = {verb for verb, slot, _a in VERBS if slot == ""} | {"garrison"}
        assert set(pairs) == no_target - {"hold", "retreat"}, pairs
        load_board("staged")
        entries = _player_entries(C.game_state_now())
        for _key, (_where, state) in entries.items():
            for field in pairs.values():
                assert field in state, field

    def test_the_open_crossings_are_the_navys_own(self):
        from backend.game_logic.naval import _OPEN_VERDICTS
        source = MAIN_GD.read_text(encoding="utf-8")
        line = next(l for l in source.splitlines()
                    if l.startswith("const _OPEN_CROSSINGS"))
        assert set(re.findall(r'"(\w+)"', line)) == set(_OPEN_VERDICTS)
