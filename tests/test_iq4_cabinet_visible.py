"""IQ-4 "The Cabinet Is Visible" — the row's behaviour pins.

Build contract: `fleet_contract.md` §4, T1–T17, plus the R2 pin
`TestGratitudeReadsTheProposalCase` (§7). Two binding amendments from the
lead supersede the contract text:

* **(1)** COURT_NATION never completes at the ceiling: its work is the
  favour, which lasts only while he stays, so it HOLDS the court (paid, and
  said so) until recalled. T1(c) is re-stated accordingly. (The first cut
  completed once relation and favour were both full; measured, that threw
  the favour away on the tick it filled — 56 ACCEPT became 48.)
* **(2)** `recall_command` spells the court by its KEY — the wizard's own
  echo (`diplomacy_wizard.gd` `_build_command`, the `cancel_mission` arm;
  the contract calls that function `_action_to_command`, a name the file
  does not carry) — never the display name.

Every lever has a DOWN arm reproducing master `7bbf82b8` on its surface.
Every probe boots the shipped 1805 board explicitly (the suite pins
`SOVEREIGN_SCENARIO=none`). HTTP-shaped pins swap `backend.main.world`,
`game_state["world"]` and the MOCK parser together (the TestClient
world-swap rule). COURT's 20% blowback is switched OFF for every pin by an
autouse fixture; the pins that need it switch it back ON.

A pin that fails here is a production defect or a contract premise the
board does not support. It is kept, not xfailed, and reported.
"""

from __future__ import annotations

import contextlib
import io
import json
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

with contextlib.redirect_stdout(io.StringIO()):
    import backend.main as M
    from backend import campaign_log as CL
    from backend.commands import diplomatic_executor as DE
    from backend.commands import meta_executor as ME
    from backend.commands.executor import CommandExecutor
    from backend.commands.parser import CommandParser
    from backend.display_names import FEEDBACK_STRINGS
    from backend.game_logic import diplomacy as D
    from backend.game_logic import diplomatic_dialogue as DD
    from backend.game_logic import diplomatic_ledger as DL
    from backend.game_logic import dispatch as DI
    from backend.game_logic import ledger as L
    from backend.game_logic import settlement_reactions as SR
    from backend.models import world_state as WS
    from backend.models.world_state import WorldState
    from backend.notifications import DIPLOMATIC_MISSION, NotificationPriority

ROOT = Path(__file__).resolve().parents[1]
SCENARIO = str(ROOT / "godot-client" / "project-sovereign" / "assets" / "maps"
               / "europe_1805.json")
SCRIPTS = ROOT / "godot-client" / "project-sovereign" / "scripts"

_LEVERS = (
    (D, "MISSION_COMPLETES_AT_THE_CLAMP"),
    (D, "COURT_EXEMPTION_IS_THE_COURTED_PAIR"),
    (D, "COURT_FAVOUR_ACTIVE"),
    (D, "COURT_FAVOUR_PER_TURN"),
    (D, "COURT_FAVOUR_CAP"),
    (D, "COUNSEL_NAMES_THE_COURT"),
    (D, "REASSURE_ONLY_AT_ALLIANCE"),
    (D, "MISSION_AT_THE_CEILING_IS_FINISHED"),
    (DD, "MISSION_RAIL_NOTICE"),
    (DD, "MISSION_LOG_ENDS"),
    (L, "MISSION_LEDGER_BLOCK"),
    (DL, "TALLEYRAND_TAB_READS_THE_CABINET"),
    (DE, "MISSION_START_IS_NOT_A_REJECTION"),
    (DE, "MISSION_CANCEL_READS_THE_NAME"),
    (ME, "MISSION_HELP_BLOCK"),
    (CL, "THE_LOG_NAMES_THE_MISSION"),
    (SR, "GRATITUDE_HOOK_READS_THE_PROPOSAL_CASE"),
    # the review round's levers
    (WS, "COUNTER_OFFER_RETURN_RESTORES_HIM"),
    (D, "COURT_EXEMPTION_KEEPS_THE_THAW"),
    (D, "UNDERMINE_ENDS_ON_THE_BREAK"),
    (D, "MISSION_PROGRESS_READS_AFTER_DRIFT"),
    (DI, "IDLE_NUDGE_READS_THE_LIVE_MISSION"),
)

_MISSION_ROW = {
    "IMPROVE_RELATIONS": "mission_improve_relations",
    "COURT_NATION": "mission_court",
    "GATHER_INTEL": "mission_gather_intel",
    "UNDERMINE_ALLIANCE": "mission_undermine",
    "REASSURE_ALLY": "mission_reassure",
}


# ════════════════════════════════════════════════════════════════════
# fixtures + helpers
# ════════════════════════════════════════════════════════════════════

@pytest.fixture(autouse=True)
def _levers_restored():
    saved = [(mod, name, getattr(mod, name)) for mod, name in _LEVERS]
    yield
    for mod, name, value in saved:
        setattr(mod, name, value)


@pytest.fixture(autouse=True)
def _no_blowback(monkeypatch):
    """COURT's 20% blowback is a die roll; every pin runs it at 0 unless it
    sets it itself (monkeypatch restores the table either way)."""
    monkeypatch.setitem(DD.MISSION_EFFECTS["COURT_NATION"], "undermine_chance", 0.0)


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


with _quiet():
    _PARSER = CommandParser(use_real_llm=False)


def _europe():
    with _quiet():
        return WorldState.from_scenario(SCENARIO)


def _key(w, a, b):
    return w._make_diplo_key(a, b)


def _rel(w, a, b):
    return int(w.nation_relations.get(_key(w, a, b), 0) or 0)


def _set_rel(w, a, b, value):
    w.nation_relations[_key(w, a, b)] = int(value)


def _set_state(w, a, b, state):
    w.diplomatic_states[_key(w, a, b)] = state
    invalidate = getattr(w, "invalidate_bloc_members_cache", None)
    if callable(invalidate):
        invalidate()


def _stage(w, mission_type, target, **extra):
    """The mission dict the executor's `start_mission` arm writes."""
    mission = {
        "type": mission_type, "target": target, "turns_active": 0,
        "paused": False, "paused_turns": 0,
        "started_turn": int(w.current_turn),
        "initial_relation": _rel(w, w.player_nation, target),
    }
    mission.update(extra)
    w.active_diplomatic_mission = mission
    w.talleyrand_state = "ON_MISSION"
    return mission


def _tick(w, dp=10):
    """One quiet mission tick — steps 2, 3 and 4c of
    `process_diplomacy_turn`, in its order. Returns (DP charged, events)."""
    w.diplomatic_points = dp
    with _quiet():
        D._process_mission_dp(w)
        charged = dp - int(w.diplomatic_points)
        events = D._process_mission_effects(w)
        D._process_relation_decay(w)
    return charged, events


def _advance(w):
    with _quiet():
        w.advance_turn()


def _proposal(target="Prussia", ptype="alliance", proposer="France"):
    return {"type": ptype, "proposer_nation": proposer, "target_nation": target,
            "sweeteners": [], "demands": [], "clauses": []}


def _score(w, proposal):
    with _quiet():
        return D.calculate_acceptance(dict(proposal), w)


def _rows(w):
    return [n for n in w.notifications.get_pending()
            if n.get("type") == DIPLOMATIC_MISSION]


def _row(w):
    """The mission's rail row — at most ONE, never an `enabled` key."""
    rows = _rows(w)
    assert len(rows) <= 1, f"more than one mission row: {[r['title'] for r in rows]}"
    for r in rows:
        assert "enabled" not in (r.get("details") or {}), r
    return rows[0] if rows else None


def _proposal_results(w):
    return [n for n in w.notifications.get_pending()
            if n.get("type") == "diplomatic_proposal_result"]


def _start_exec(w, mission_type, target, ally=None):
    """Drive the REAL `start_mission` dialogue arm (not a hand-set dict)."""
    terms = {"mission_type": mission_type, "target_nation": target}
    if ally:
        terms["target_ally"] = ally
    w.dialogue_manager.replace({
        "type": "mission", "target_nation": target,
        "talleyrand_text": "Very well, Sire.",
        "options": [
            {"label": "Begin mission", "description": "Start.",
             "action": "start_mission", "terms": terms},
            {"label": "Dismiss", "description": "Cancel.", "action": "dismiss"},
        ],
        "context": {"dp_cost_per_turn": int(DD.MISSION_DP_COSTS[mission_type])},
        "turn_created": int(w.current_turn),
        "blocking": False,
    })
    w.diplomatic_points = max(int(w.diplomatic_points), 10)
    with _quiet():
        return CommandExecutor()._diplomatic.handle_diplomatic_dialogue_response(
            1, {"world": w})


@pytest.fixture
def http(monkeypatch):
    world = _europe()
    assert _PARSER.llm.use_real_api is False
    monkeypatch.setattr(M, "world", world)
    monkeypatch.setattr(M, "parser", _PARSER)
    monkeypatch.setitem(M.game_state, "world", world)
    world.diplomatic_points = 10
    world.talleyrand_defiance_cooldown = 99   # no sabotage die on a send
    return world, TestClient(M.app)


def _cmd(client, text):
    with _quiet():
        return client.post("/command", json={"command": text}).json()


def _respond(client, choice, dialogue_id=None):
    with _quiet():
        return client.post("/respond_to_diplomatic_dialogue",
                           json={"choice": choice, "dialogue_id": dialogue_id}).json()


def _start_http(client, text):
    """The player's road: the typed echo, then the confirm's Begin button."""
    r = _cmd(client, text)
    dlg = r.get("diplomatic_dialogue") or {}
    assert dlg.get("type") == "mission", r.get("message")
    actions = [o.get("action") for o in dlg.get("options", [])]
    assert "start_mission" in actions, actions
    return _respond(client, actions.index("start_mission") + 1, dlg.get("dialogue_id"))


def _send_http(client, text):
    """A proposal through the wizard's echo and the confirm's Send button."""
    r = _cmd(client, text)
    dlg = r.get("diplomatic_dialogue") or {}
    actions = [o.get("action") for o in dlg.get("options", [])]
    assert "execute_proposal" in actions, (r.get("message"), actions)
    return _respond(client, actions.index("execute_proposal") + 1, dlg.get("dialogue_id"))


def _walk_numbers(value, path="$"):
    """Every number in a payload, with its path (GR2: no floats to Godot)."""
    if isinstance(value, dict):
        for k, v in value.items():
            yield from _walk_numbers(v, f"{path}.{k}")
    elif isinstance(value, (list, tuple)):
        for i, v in enumerate(value):
            yield from _walk_numbers(v, f"{path}[{i}]")
    elif isinstance(value, (int, float)):
        yield path, value


def _gd_func(path, name):
    """A GDScript function body, scoped to that function."""
    src = path.read_text(encoding="utf-8")
    m = re.search(r"^func " + re.escape(name) + r"\(.*?(?=^func |\Z)", src, re.S | re.M)
    assert m, f"func {name} not found in {path.name}"
    return m.group(0)


def _gd_code(path, name):
    """A GDScript function body with its docstring and `#` comment lines
    stripped — so a pin reads CODE, never the comment that explains it (the
    review found three client pins satisfied by their own comments)."""
    body = re.sub(r'"""(.*?)"""', "", _gd_func(path, name), flags=re.S)
    return "\n".join(line for line in body.splitlines()
                     if not line.lstrip().startswith("#"))


# ════════════════════════════════════════════════════════════════════
# T1 — the mission ends at the ceiling (real decay)
# ════════════════════════════════════════════════════════════════════

class TestTheMissionEndsAtTheCeiling:
    """MS-9b: the effect wrote +100 and step 4c's decay took it to 99 in
    the same turn, so `_before == _after` never held and IMPROVE/REASSURE
    parked at 99 charging DP forever."""

    def test_improve_completes_on_the_tick_that_writes_the_clamp(self):
        w = _europe()
        _set_rel(w, "France", "Prussia", 95)
        _stage(w, "IMPROVE_RELATIONS", "Prussia")
        charged, events = _tick(w)
        assert charged == 1
        done = [e for e in events if e["type"] == "diplomatic_mission_completed"]
        assert done and done[0].get("reason") == "ceiling"
        assert w.active_diplomatic_mission["completed"] is True
        assert _rel(w, "France", "Prussia") == 99, "decay still runs after"
        for _ in range(4):
            assert _tick(w)[0] == 0, "no DP after the work is done"

    def test_reassure_completes_on_the_tick_that_writes_the_clamp(self):
        w = _europe()
        assert w.get_diplomatic_state("France", "Bavaria") == "ALLIANCE"
        _set_rel(w, "France", "Bavaria", 95)
        _stage(w, "REASSURE_ALLY", "Bavaria")
        charged, _ = _tick(w)          # 95 + 4 = 99, then decay 98
        assert charged == 1
        assert not w.active_diplomatic_mission.get("completed")
        charged, events = _tick(w)     # 98 + 4 = 102 -> clamp 100
        assert charged == 1
        assert w.active_diplomatic_mission["completed"] is True
        assert any(e.get("reason") == "ceiling" for e in events)
        for _ in range(3):
            assert _tick(w)[0] == 0

    def test_court_holds_the_court_and_keeps_its_favour(self):
        """Amendment (1), re-stated at integration: COURT never completes at
        the ceiling. The favour lasts only while he stays, so completing —
        even with the favour full — threw it away (Prussia's alliance read 56
        ACCEPT on the fourth funded tick and 48 on the fifth). He HOLDS, the
        hold is paid, and the Cabinet says so."""
        w = _europe()
        _set_rel(w, "France", "Prussia", 95)
        _stage(w, "COURT_NATION", "Prussia")
        seen = []
        for _ in range(8):
            charged, _ = _tick(w)
            m = w.active_diplomatic_mission
            seen.append((_rel(w, "France", "Prussia"), charged, bool(m.get("completed"))))
        assert all(s == (100, 2, False) for s in seen), seen
        assert D.court_favour_mod(w, _proposal()) == D.COURT_FAVOUR_CAP
        status = DD.mission_status(w)
        assert (status["remaining_kind"], status["remaining_turns"]) == ("holding", -1)
        assert status["remaining_note"] == (
            "the favour stands at +10 and holds while he stays — recall him once "
            "the treaty is signed")

    def test_court_without_the_favour_completes_at_the_clamp(self):
        """The favour gate on COURT's completion rides COURT_FAVOUR_ACTIVE."""
        D.COURT_FAVOUR_ACTIVE = False
        w = _europe()
        _set_rel(w, "France", "Prussia", 95)
        _stage(w, "COURT_NATION", "Prussia")
        charged, _ = _tick(w)
        assert charged == 2
        assert w.active_diplomatic_mission["completed"] is True
        assert _tick(w)[0] == 0

    def test_lever_down_parks_at_ninety_nine_and_taxes_forever(self):
        D.MISSION_COMPLETES_AT_THE_CLAMP = False
        w = _europe()
        _set_rel(w, "France", "Prussia", 95)
        _stage(w, "IMPROVE_RELATIONS", "Prussia")
        for _ in range(8):
            charged, _ = _tick(w)
            assert charged == 1
            assert _rel(w, "France", "Prussia") == 99
            assert not w.active_diplomatic_mission.get("completed")

    def test_the_ms9_pins_keep_their_meaning(self):
        """`TestTheMissionStopsWhenItsWorkIsDone` — its three cases."""
        def at(relation):
            w = _europe()
            _stage(w, "IMPROVE_RELATIONS", "Prussia", turns_active=9)
            _set_rel(w, "France", "Prussia", relation)
            return w
        w = at(100)
        with _quiet():
            D._process_mission_effects(w)
        assert w.active_diplomatic_mission["completed"]
        w = at(40)
        with _quiet():
            D._process_mission_effects(w)
        assert not w.active_diplomatic_mission.get("completed")
        D.MISSION_AT_THE_CEILING_IS_FINISHED = False
        w = at(100)
        with _quiet():
            D._process_mission_effects(w)
        assert not w.active_diplomatic_mission.get("completed")

    def test_the_real_turn_charges_nothing_after_the_ceiling(self):
        """The whole `process_diplomacy_turn`, DP regen and all."""
        w, ctrl = _europe(), _europe()
        _set_rel(w, "France", "Prussia", 95)
        _stage(w, "IMPROVE_RELATIONS", "Prussia")
        with _quiet():
            D.process_diplomacy_turn(w)
            D.process_diplomacy_turn(ctrl)
        assert w.active_diplomatic_mission["completed"] is True
        assert ctrl.diplomatic_points - w.diplomatic_points == 1
        with _quiet():
            D.process_diplomacy_turn(w)
            D.process_diplomacy_turn(ctrl)
        assert w.diplomatic_points == ctrl.diplomatic_points


# ════════════════════════════════════════════════════════════════════
# T2 — the court freezes only its own pair
# ════════════════════════════════════════════════════════════════════

class TestTheCourtFreezesOnlyItsOwnPair:

    def _court(self):
        w = _europe()
        assert _rel(w, "Prussia", "Russia") == 30, "the shipped board moved"
        _set_rel(w, "France", "Prussia", 60)
        _stage(w, "COURT_NATION", "Prussia")
        return w

    def test_the_courted_pair_holds_and_the_rest_of_europe_drifts(self):
        w = self._court()
        _tick(w)
        assert _rel(w, "France", "Prussia") == 68, "+8, no decay on the courted pair"
        assert _rel(w, "Prussia", "Russia") == 29, "an AI-vs-AI pair is not courted"

    def test_after_completion_nothing_is_frozen(self):
        """A courting mission ends by recall (it holds at the ceiling); with
        the favour lever down it completes at the clamp. Either way, once it
        is not live nothing is frozen."""
        D.COURT_FAVOUR_ACTIVE = False
        w = self._court()
        for _ in range(10):
            if w.active_diplomatic_mission.get("completed"):
                break
            _tick(w)
        assert w.active_diplomatic_mission.get("completed")
        fp, pr = _rel(w, "France", "Prussia"), _rel(w, "Prussia", "Russia")
        _tick(w)
        assert _rel(w, "France", "Prussia") == fp - 1
        assert _rel(w, "Prussia", "Russia") == pr - 1

    def test_after_a_recall_nothing_is_frozen(self):
        w = self._court()
        for _ in range(3):
            _tick(w)
        w.active_diplomatic_mission = None          # the recall's own write
        w.talleyrand_state = "IDLE"
        fp = _rel(w, "France", "Prussia")
        _tick(w)
        assert _rel(w, "France", "Prussia") == fp - 1

    def test_lever_down_freezes_every_pair_of_the_court_for_good(self):
        D.COURT_EXEMPTION_IS_THE_COURTED_PAIR = False
        D.COURT_FAVOUR_ACTIVE = False     # the pre-IQ-4 shape: COURT completes
        w = self._court()
        for _ in range(8):
            _tick(w)
            assert _rel(w, "Prussia", "Russia") == 30
        assert w.active_diplomatic_mission.get("completed")
        assert _rel(w, "France", "Prussia") == 100, "frozen after completion too"

    def test_the_legacy_pin_still_holds(self):
        """`test_phase3_balance::test_court_nation_pair_skipped`'s shape: a
        bare {type, target} dict (no `completed` key) is a live mission."""
        w = _europe()
        _set_state(w, "France", "Austria", "PEACE")
        _set_rel(w, "France", "Austria", 50)
        w.active_diplomatic_mission = {"type": "COURT_NATION", "target": "Austria"}
        with _quiet():
            D._process_relation_decay(w)
        assert _rel(w, "France", "Austria") == 50


# ════════════════════════════════════════════════════════════════════
# T3 — the drift step IS the decay (the pure refactor, no lever)
# ════════════════════════════════════════════════════════════════════

class TestTheDriftStepIsTheDecay:

    @pytest.mark.parametrize("court_lever", [True, False])
    def test_every_pair_on_the_board(self, court_lever):
        D.COURT_EXEMPTION_IS_THE_COURTED_PAIR = court_lever
        w = _europe()
        _set_state(w, "France", "Prussia", "ARMISTICE")
        _set_rel(w, "France", "Prussia", -50)
        _set_rel(w, "France", "Saxony", 50)
        _stage(w, "COURT_NATION", "Saxony")
        _set_rel(w, "France", "Holland", 60)          # vassal-lord, above the band
        assert w.vassals["Holland"]["lord"] == "France"
        nations = list(w.get_active_nations())
        expected = {}
        for i, a in enumerate(nations):
            for b in nations[i + 1:]:
                expected[frozenset((a, b))] = (a, b, D.relation_drift_step(w, a, b))
        before = {p: _rel(w, a, b) for p, (a, b, _s) in expected.items()}
        with _quiet():
            D._process_relation_decay(w)
        wrong = [(a, b, step, _rel(w, a, b) - before[p])
                 for p, (a, b, step) in expected.items()
                 if _rel(w, a, b) - before[p] != step]
        assert not wrong, wrong[:10]

        def step(a, b):
            return expected[frozenset((a, b))][2]
        assert step("France", "Prussia") == D.ARMISTICE_THAW_PER_TURN
        assert step("France", "Austria") == 0, "WAR freezes"
        assert step("France", "Holland") == 0, "vassal-lord pairs never drift"
        assert step("France", "Saxony") == 0, "the courted pair"
        assert sum(1 for (_a, _b, s) in expected.values() if s) > 10, "vacuous"


# (pair, state or None to keep the board's, relation, courted, step) — LITERAL
# steps, never computed with `relation_drift_step` (review P4 c: the table
# above is circular by construction, so a mis-transcribed step passed it).
_DRIFT_TABLE = [
    (("France", "Prussia"), "PEACE", 11, False, -1),
    (("France", "Prussia"), "PEACE", 10, False, 0),
    (("France", "Prussia"), "PEACE", -10, False, 0),
    (("France", "Prussia"), "PEACE", -11, False, 1),
    (("France", "Prussia"), "ARMISTICE", 50, False, -3),
    (("France", "Prussia"), "ARMISTICE", -50, False, 3),
    (("France", "Prussia"), "ARMISTICE", 10, False, 0),
    (("France", "Prussia"), "ARMISTICE", -11, False, 3),
    (("France", "Austria"), "WAR", 50, False, 0),
    (("France", "Austria"), "WAR", -50, False, 0),
    (("Prussia", "Russia"), "PEACE", 30, False, -1),
    (("Prussia", "Russia"), "PEACE", -30, False, 1),
    (("Prussia", "Russia"), "PEACE", 10, False, 0),
    (("France", "Holland"), None, 60, False, 0),
    (("France", "Holland"), None, -60, False, 0),
    (("France", "Saxony"), "PEACE", 50, True, 0),
    (("France", "Saxony"), "PEACE", -50, True, 1),
    (("France", "Saxony"), "ARMISTICE", 50, True, 0),
    (("France", "Saxony"), "ARMISTICE", -50, True, 3),
]


class TestTheDriftStepAgainstLiterals:

    @pytest.mark.parametrize("pair,state,relation,courted,step", _DRIFT_TABLE)
    def test_the_step_and_the_decay_are_the_literal(self, pair, state, relation, courted, step):
        w = _europe()
        a, b = pair
        if state is not None:
            _set_state(w, a, b, state)
        else:
            assert w.vassals[b]["lord"] == a, "the vassal-lord pair moved"
        _set_rel(w, a, b, relation)
        if courted:
            _stage(w, "COURT_NATION", b)
        assert D.relation_drift_step(w, a, b) == step
        with _quiet():
            D._process_relation_decay(w)
        assert _rel(w, a, b) - relation == step


# ════════════════════════════════════════════════════════════════════
# T4 — the Court's Favour (⚠ FOR USER CONFIRMATION)
# ════════════════════════════════════════════════════════════════════

class TestTheCourtsFavour:

    def _courting(self, target="Prussia", turns=3):
        w = _europe()
        _stage(w, "COURT_NATION", target, turns_active=turns)
        return w

    def test_the_formula_over_funded_ticks(self):
        w = _europe()
        _set_rel(w, "France", "Prussia", 0)
        _stage(w, "COURT_NATION", "Prussia")
        seen = []
        for _ in range(7):
            seen.append(D.court_favour_mod(w, _proposal()))
            _tick(w)
        assert seen == [0, 2, 4, 6, 8, 10, 10]

    def test_the_positive_control(self):
        assert D.court_favour_mod(self._courting(), _proposal()) == 6

    def test_the_gate_reads_either_case(self):
        assert D.court_favour_mod(self._courting(), _proposal(ptype="ALLIANCE")) == 6

    def test_a_different_court_gets_nothing(self):
        assert D.court_favour_mod(self._courting(), _proposal("Saxony")) == 0

    def test_no_mission_gets_nothing(self):
        assert D.court_favour_mod(_europe(), _proposal()) == 0

    def test_a_completed_mission_gets_nothing(self):
        w = self._courting()
        w.active_diplomatic_mission["completed"] = True
        assert D.court_favour_mod(w, _proposal()) == 0

    def test_another_mission_type_gets_nothing(self):
        w = _europe()
        _stage(w, "IMPROVE_RELATIONS", "Prussia", turns_active=3)
        assert D.court_favour_mod(w, _proposal()) == 0

    def test_an_ai_proposer_gets_nothing(self):
        assert D.court_favour_mod(self._courting(), _proposal(proposer="Austria")) == 0

    @pytest.mark.parametrize("ptype", ["peace", "vassalage"])
    def test_non_cooperative_types_get_nothing(self, ptype):
        assert D.court_favour_mod(self._courting(), _proposal(ptype=ptype)) == 0

    def test_a_pair_at_war_gets_nothing(self):
        w = self._courting("Austria")
        assert w.get_diplomatic_state("France", "Austria") == "WAR"
        assert D.court_favour_mod(w, _proposal("Austria")) == 0

    def test_prussias_alliance_is_bought_by_the_courting(self):
        """T4(c): 48 COUNTER_OFFER with no favour -> 58 ACCEPT after five
        funded ticks. (Amendment (1) completes COURT on that fifth tick, and
        the favour gate reads `mission_is_live`.)"""
        w = _europe()
        _set_rel(w, "France", "Prussia", 60)
        base = _score(w, _proposal())
        assert (base["score"], base["outcome"]) == (48, "COUNTER_OFFER")
        _stage(w, "COURT_NATION", "Prussia")
        for _ in range(4):
            _tick(w)
        four = _score(w, _proposal())
        assert four["components"]["court_favour_mod"] == 8
        assert (four["score"], four["outcome"]) == (56, "ACCEPT")
        _tick(w)       # the fifth funded tick
        five = _score(w, _proposal())
        assert five["components"]["court_favour_mod"] == D.COURT_FAVOUR_CAP, (
            f"after five funded ticks the favour reads "
            f"{five['components']['court_favour_mod']}: the mission "
            f"completed={w.active_diplomatic_mission.get('completed')} on the "
            f"tick its favour reached the cap, and the gate discards it")
        assert (five["score"], five["outcome"]) == (58, "ACCEPT")

    def _court_non_aggression(self, http):
        w, client = http
        _set_state(w, "France", "Prussia", "NON_AGGRESSION")
        _set_rel(w, "France", "Prussia", 30)
        r = _start_http(client, "court Prussia")
        assert r.get("success"), r.get("message")
        for _ in range(3):
            _tick(w)
        w.diplomatic_points = 10
        return w, client

    def test_a_wizard_shaped_proposal_scores_the_favour(self, http):
        w, client = self._court_non_aggression(http)
        rows = {a["action"]: a for a in D.get_available_diplomatic_actions(w, "Prussia")}
        assert rows["propose_defensive_alliance"]["available"]
        r = _send_http(client, "propose defensive alliance with Prussia")
        assert r.get("success"), r.get("message")
        proposal = w.proposal_in_transit["proposal"]
        assert proposal["type"] == "defensive_alliance"
        assert _score(w, proposal)["components"]["court_favour_mod"] == 6

    def _spy_arrival(self, monkeypatch):
        seen = []
        real = D.calculate_acceptance

        def spy(proposal, world):
            result = real(proposal, world)
            seen.append(result)
            return result
        monkeypatch.setattr(D, "calculate_acceptance", spy)
        return seen

    def test_the_arrival_is_scored_with_the_favour_it_was_sent_with(self, http, monkeypatch):
        w, client = self._court_non_aggression(http)
        assert _send_http(client, "propose defensive alliance with Prussia").get("success")
        pit = w.proposal_in_transit
        snapshot = int(pit["acceptance_snapshot"])
        w.diplomatic_points = 10
        with _quiet():
            D._process_mission_dp(w)        # the transit tick: he waits (MS-10b)
        assert w.diplomatic_points == 10
        assert w.active_diplomatic_mission["turns_active"] == 3
        seen = self._spy_arrival(monkeypatch)
        w.current_turn += 1
        with _quiet():
            w._process_proposal_in_transit()
        assert seen, "the arrival was never scored"
        assert seen[0]["components"]["court_favour_mod"] == 6
        assert int(seen[0]["score"]) == snapshot

    def test_a_typed_recall_in_transit_is_refused_and_the_send_keeps_its_favour(
            self, http, monkeypatch):
        """Review P4 (d): the rail and the Cabinet withhold Recall while he
        carries a proposal, and the EC-Q transit gate refuses every typed
        spelling of it — the old pin drove `_recall_mission` by hand, a state
        no player road reaches. The reachable contract: refused, the mission
        kept, and the arrival scored with the favour it was sent with."""
        w, client = self._court_non_aggression(http)
        assert _send_http(client, "propose defensive alliance with Prussia").get("success")
        snapshot = int(w.proposal_in_transit["acceptance_snapshot"])
        assert w.talleyrand_state == "IN_TRANSIT"
        for text in ("Talleyrand, cancel mission with Prussia", "Talleyrand, cancel mission",
                     "recall Talleyrand"):
            r = _cmd(client, text)
            assert r.get("success") is False, (text, r.get("message"))
            assert DD.mission_is_live(w), text
            assert w.active_diplomatic_mission["target"] == "Prussia"
            assert w.active_diplomatic_mission["turns_active"] == 3
            assert w.talleyrand_state == "IN_TRANSIT"
        seen = self._spy_arrival(monkeypatch)
        w.current_turn += 1
        with _quiet():
            w._process_proposal_in_transit()
        assert seen, "the arrival was never scored"
        assert seen[0]["components"]["court_favour_mod"] == 6
        assert int(seen[0]["score"]) == snapshot

    def test_the_wizard_row_rises_by_exactly_the_favour(self):
        w = _europe()
        _set_state(w, "France", "Prussia", "NON_AGGRESSION")
        _set_rel(w, "France", "Prussia", 30)
        w.diplomatic_points = 10

        def row():
            return {a["action"]: a for a in
                    D.get_available_diplomatic_actions(w, "Prussia")}["propose_defensive_alliance"]
        before = row()["likelihood_score"]
        _stage(w, "COURT_NATION", "Prussia", turns_active=3)
        favour = DD.mission_status(w)["favour_now"]
        assert favour == 6
        assert row()["likelihood_score"] == before + favour

    def test_the_favour_is_never_negative(self):
        for turns in range(0, 12):
            w = self._courting(turns=turns)
            _set_rel(w, "France", "Prussia", -100)
            favour = D.court_favour_mod(w, _proposal())
            assert 0 <= favour <= D.COURT_FAVOUR_CAP

    def test_no_payload_titles_the_raw_key(self, http):
        w, client = self._court_non_aggression(http)
        with _quiet():
            preview = D.get_diplomatic_preview(w, "Prussia")
        drafted = _cmd(client, "propose defensive alliance with Prussia")
        blob = json.dumps([preview, drafted], default=str)
        assert "Court Favour Mod" not in blob

    def test_the_labels_are_the_ruled_copy(self):
        assert FEEDBACK_STRINGS["court_favour_mod"] == {
            "positive": "the months Talleyrand has spent at their court",
            "negative": "no courtship at their court",
        }
        from backend.game_logic.diplomatic_templates import SPOKEN_BLOCKER_PHRASES
        assert "court_favour_mod" not in SPOKEN_BLOCKER_PHRASES

    def test_lever_down_the_components_are_todays(self):
        D.COURT_FAVOUR_ACTIVE = False
        w, ctrl = _europe(), _europe()
        for world in (w, ctrl):
            _set_rel(world, "France", "Prussia", 60)
        _stage(w, "COURT_NATION", "Prussia", turns_active=5)
        a, b = _score(w, _proposal()), _score(ctrl, _proposal())
        assert "court_favour_mod" not in a["components"]
        assert a["components"] == b["components"]
        assert a["score"] == b["score"] == 48


# ════════════════════════════════════════════════════════════════════
# T5 — one source for the mission
# ════════════════════════════════════════════════════════════════════

# type -> (target, ally, France<->target relation, court whose wizard row
# carries the type)
# IMPROVE is staged INSIDE the ±10 calm band (review S2): +8 carries it to 14,
# where the same tick's decay takes 1 — net +7, not effect + today's drift.
_TYPED = {
    "IMPROVE_RELATIONS": ("Prussia", None, 6, "Prussia"),
    "COURT_NATION": ("Prussia", None, 30, "Prussia"),
    "REASSURE_ALLY": ("Bavaria", None, 60, "Bavaria"),
    "GATHER_INTEL": ("Prussia", None, -10, "Prussia"),
    "UNDERMINE_ALLIANCE": ("Austria", "Russia", None, "Prussia"),
}


def _typed_world(mission_type):
    target, ally, relation, _court = _TYPED[mission_type]
    w = _europe()
    if relation is not None:
        _set_rel(w, "France", target, relation)
    if ally:
        _set_state(w, target, ally, "ALLIANCE")
        _set_rel(w, target, ally, 60)
        _stage(w, mission_type, target, target_ally=ally, initial_pair_relation=60)
    else:
        _stage(w, mission_type, target)
    return w


def _moved_pair(mission_type):
    target, ally, _r, _c = _TYPED[mission_type]
    return (target, ally) if ally else ("France", target)


@pytest.mark.parametrize("mission_type", list(_TYPED))
class TestOneSourceForTheMission:

    def test_the_effect_is_the_ticks_own_write(self, mission_type):
        w = _typed_world(mission_type)
        status = DD.mission_status(w)
        pair = _moved_pair(mission_type)
        before = _rel(w, *pair)
        w.diplomatic_points = 10
        with _quiet():
            D._process_mission_dp(w)
            D._process_mission_effects(w)
        assert _rel(w, *pair) - before == status["effect_per_turn"]

    def test_the_net_is_the_quiet_worlds_delta(self, mission_type):
        w = _typed_world(mission_type)
        status = DD.mission_status(w)
        pair = _moved_pair(mission_type)
        before = _rel(w, *pair)
        _tick(w)
        assert _rel(w, *pair) - before == status["net_per_turn"]

    def test_every_number_is_an_int(self, mission_type):
        status = DD.mission_status(_typed_world(mission_type))
        floats = [(p, v) for p, v in _walk_numbers(status) if isinstance(v, float)]
        assert not floats, floats

    def test_every_surface_quotes_the_one_text(self, mission_type):
        w = _typed_world(mission_type)
        long_text = DD.mission_effect_text(w, mission_type)
        short_text = DD.mission_effect_text(w, mission_type, short=True)
        assert long_text and short_text
        tab = DL.build_diplomatic_ledger(w)["talleyrand"]["active_mission"]
        assert tab["effect_text"] == long_text
        court = _TYPED[mission_type][3]
        rows = {a["action"]: a for a in D.get_available_diplomatic_actions(w, court)}
        assert rows[_MISSION_ROW[mission_type]]["effect_text"] == short_text
        assert short_text in ME._missions_help_block(w)
        with _quiet():
            cabinet = L.build_strategic_ledger(w)["cabinet"]
        assert cabinet["effect_text"] == long_text
        DD.restate_mission_notice(w, beat="begun")
        message = _row(w)["message"]
        target_display = DD.mission_status(w)["target_display"]
        assert message.startswith(
            f"Talleyrand has gone to {target_display}. "
            f"{long_text[:1].upper()}{long_text[1:]}.")


def test_the_court_text_is_the_ruled_copy(monkeypatch):
    """§3.6 verbatim, at the shipped 20% blowback."""
    monkeypatch.setitem(DD.MISSION_EFFECTS["COURT_NATION"], "undermine_chance", 0.20)
    w = _europe()
    _stage(w, "COURT_NATION", "Prussia", turns_active=2)
    assert DD.mission_effect_text(w, "COURT_NATION") == (
        "+8 relation per turn; our proposals to them +2 per turn courted "
        "(max +10, now +4); 20% chance of -3")
    assert DD.mission_effect_text(w, "COURT_NATION", short=True) == (
        "+8 relation/turn, proposals +2/turn courted (max +10), 20% blowback")
    D.COURT_FAVOUR_ACTIVE = False
    assert DD.mission_effect_text(w, "COURT_NATION") == "+8 relation per turn, 20% blowback risk"
    assert DD.mission_effect_text(w, "COURT_NATION", short=True) == "+8 relation/turn, 20% blowback"


def test_the_recall_button_is_the_ruled_copy():
    assert DD.MISSION_RECALL_LABEL == "Recall Talleyrand"
    assert DD.MISSION_RECALL_DETAIL == (
        "Free — no DP, no action point. He comes home; relations keep what he has won.")


# ════════════════════════════════════════════════════════════════════
# T6 — the forecast is labelled, and exact in a quiet world
# ════════════════════════════════════════════════════════════════════

class TestTheForecastIsLabelledAndExactInAQuietWorld:

    def test_improve_from_minus_ten_lands_on_the_forecast(self):
        w = _europe()
        _set_rel(w, "France", "Prussia", -10)
        _stage(w, "IMPROVE_RELATIONS", "Prussia")
        forecast = DD.mission_status(w)["remaining_turns"]
        assert 0 < forecast <= 40
        ticks = 0
        while DD.mission_is_live(w) and ticks < 41:
            assert DD.mission_status(w)["remaining_turns"] == forecast - ticks
            _tick(w)
            ticks += 1
        assert w.active_diplomatic_mission.get("completed")
        assert ticks == forecast

    def test_gather_counts_down_three_two_one(self):
        w = _europe()
        _stage(w, "GATHER_INTEL", "Prussia")
        seen = []
        for _ in range(3):
            status = DD.mission_status(w)
            assert status["remaining_kind"] == "duration"
            seen.append(status["remaining_turns"])
            _tick(w)
        assert seen == [3, 2, 1]
        assert DD.mission_status(w) is None
        assert w.active_diplomatic_mission.get("completed")

    def test_undermine_states_terms_never_a_count(self):
        w = _typed_world("UNDERMINE_ALLIANCE")
        w.turns_below_threshold[_key(w, "Austria", "Russia")] = 2
        status = DD.mission_status(w)
        assert status["remaining_kind"] == "alliance"
        assert status["remaining_turns"] == -1
        floor = int(D.STATE_RELATION_THRESHOLDS["ALLIANCE"]) - 30
        assert f"at {floor} or below" in status["remaining_note"]
        assert "2 of 5 counted" in status["remaining_note"]

    def test_transit_is_a_note_not_a_count(self):
        w = _europe()
        _stage(w, "IMPROVE_RELATIONS", "Prussia", paused=True)
        w.talleyrand_state = "IN_TRANSIT"
        status = DD.mission_status(w)
        assert (status["remaining_kind"], status["remaining_turns"]) == ("transit", -1)
        assert status["remaining_note"] == (
            "paused: he is carrying your proposal — costs nothing, earns nothing "
            "until he returns")

    def test_a_starved_pause_counts_to_its_collapse(self):
        w = _europe()
        w.diplomats["France"].skill = 5        # C4: staged — France never starves
        _stage(w, "IMPROVE_RELATIONS", "Prussia", paused=True, paused_turns=1)
        status = DD.mission_status(w)
        assert (status["remaining_kind"], status["remaining_turns"]) == ("starved", 2)
        assert status["remaining_note"] == "paused: 1 DP needed — collapses in 2 turns without it"

    @pytest.mark.parametrize("mission_type", ["IMPROVE_RELATIONS", "REASSURE_ALLY"])
    def test_every_ceiling_note_is_labelled_a_forecast(self, mission_type):
        status = DD.mission_status(_typed_world(mission_type))
        assert status["remaining_kind"] == "ceiling"
        assert "≈" in status["remaining_note"]
        assert status["remaining_note"] == (
            f"≈{status['remaining_turns']} turns to +100 at the present rate")

    def test_court_counts_its_funded_turns_to_the_full_favour(self):
        """COURT has no ceiling end (it holds): its count is the funded
        turns to the full favour — exact, since `turns_active` moves only on
        a funded tick — and then it says the favour holds."""
        w = _europe()
        _set_rel(w, "France", "Prussia", 20)
        _stage(w, "COURT_NATION", "Prussia")
        seen = []
        for _ in range(6):
            status = DD.mission_status(w)
            seen.append((status["remaining_kind"], status["remaining_turns"]))
            _tick(w)
        assert seen == [("favour", 5), ("favour", 4), ("favour", 3), ("favour", 2),
                        ("favour", 1), ("holding", -1)]
        assert DD.mission_status(w)["remaining_kind"] == "holding"

    def test_court_without_the_favour_keeps_the_ceiling_forecast(self):
        D.COURT_FAVOUR_ACTIVE = False
        status = DD.mission_status(_typed_world("COURT_NATION"))
        assert status["remaining_kind"] == "ceiling"
        assert "≈" in status["remaining_note"] and "barring blowback" in status["remaining_note"]


# ════════════════════════════════════════════════════════════════════
# T7 — the rail has one row per mission
# ════════════════════════════════════════════════════════════════════

def _hesse_world(w, relation=40):
    _set_rel(w, "France", "Hesse", relation)
    return w


class TestTheRailHasOneRowPerMission:

    def test_quiet_turns_refresh_one_row_in_place(self):
        w = _hesse_world(_europe())
        assert _start_exec(w, "IMPROVE_RELATIONS", "Hesse")["success"]
        first = _row(w)
        assert first["details"]["beat"] == "begun"
        assert first["details"]["target_nation"] == "Hesse"
        assert first["title"] == "Talleyrand: Improving Relations - Hesse"
        for _ in range(5):
            _advance(w)
            row = _row(w)
            assert row["id"] == first["id"], "a standing turn never re-issues"
            assert row["details"]["beat"] == "running"
            assert row["details"]["action_command"] == "Talleyrand, cancel mission with Hesse"

    def test_a_send_and_its_return(self, http):
        w, client = http
        _hesse_world(w)
        assert _start_http(client, "improve relations with Hesse").get("success")
        begun = _row(w)["id"]
        r = _send_http(client, "propose open borders with Hesse")
        assert r.get("success"), r.get("message")
        paused = _row(w)
        assert paused["id"] != begun, "a change of state rings once"
        assert paused["details"]["beat"] == "paused_transit"
        _advance(w)
        assert w.proposal_in_transit is None
        assert w.talleyrand_state == "ON_MISSION"
        back = _row(w)
        assert back["id"] == paused["id"], "resume after transit is a refresh"
        assert back["details"]["beat"] == "running"

    def test_blowback_rings_a_new_high_row(self, monkeypatch):
        monkeypatch.setitem(DD.MISSION_EFFECTS["COURT_NATION"], "undermine_chance", 1.0)
        w = _europe()
        assert _start_exec(w, "COURT_NATION", "Prussia")["success"]
        first = _row(w)["id"]
        _advance(w)
        row = _row(w)
        assert row["id"] != first
        assert row["details"]["beat"] == "blowback"
        assert row["priority"] == int(NotificationPriority.HIGH)
        assert "caught Talleyrand at his courting" in row["message"]

    def test_a_proposal_voided_by_the_coalition_reads_running(self, http, monkeypatch):
        """The seam-order pin (contract A5): the restate sits AFTER
        `process_coalition_turn`, whose EC-2 branch resumes the mission."""
        w, client = http
        _hesse_world(w)
        assert _start_http(client, "improve relations with Hesse").get("success")
        assert _send_http(client, "propose open borders with Hesse").get("success")
        assert _row(w)["details"]["beat"] == "paused_transit"
        # still on the road when the coalition sits
        w.proposal_in_transit["turn_sent"] = int(w.current_turn) + 10
        from backend.game_logic import coalition as C
        real_coalition = C.process_coalition_turn
        real_restate = DD.restate_mission_notice
        order = []

        def coalition_voids(world):
            order.append("coalition")
            events = real_coalition(world)
            # The effect of the EC-2 void branch (`form_coalition`): the court
            # he travels to joined the league — the proposal is void, the
            # DP refunded, and he resumes his mission.
            world.proposal_in_transit = None
            world.talleyrand_state = "ON_MISSION"
            world.active_diplomatic_mission["paused"] = False
            return events

        def restate_spy(world, beat=None, **kw):
            if beat is None:
                order.append("restate")
            return real_restate(world, beat=beat, **kw)
        monkeypatch.setattr(C, "process_coalition_turn", coalition_voids)
        monkeypatch.setattr(DD, "restate_mission_notice", restate_spy)
        _advance(w)
        assert "coalition" in order and "restate" in order, order
        assert order.index("coalition") < order.index("restate"), order
        assert _row(w)["details"]["beat"] == "running"

    def test_completion_rings_once_and_offers_no_recall(self):
        w = _hesse_world(_europe(), 95)
        assert _start_exec(w, "IMPROVE_RELATIONS", "Hesse")["success"]
        begun = _row(w)["id"]
        _advance(w)
        row = _row(w)
        assert w.active_diplomatic_mission.get("completed")
        assert row["id"] != begun
        assert row["details"]["beat"] == "completed"
        assert "action_command" not in row["details"]
        assert row["priority"] == int(NotificationPriority.NORMAL)
        assert row["message"].startswith(
            "Relations with Hesse stand at +100. Talleyrand's mission is done and he is home")
        _advance(w)
        assert _row(w)["id"] == row["id"], "the ended row survives the next advance"

    def test_a_new_mission_elsewhere_replaces_the_row(self):
        w = _hesse_world(_europe())
        assert _start_exec(w, "IMPROVE_RELATIONS", "Hesse")["success"]
        assert _start_exec(w, "IMPROVE_RELATIONS", "Saxony")["success"]
        row = _row(w)
        assert row["details"]["target_nation"] == "Saxony"
        assert row["details"]["beat"] == "begun"

    def test_lever_down_rings_nothing(self, http):
        DD.MISSION_RAIL_NOTICE = False
        w, client = http
        _hesse_world(w)
        assert _start_http(client, "improve relations with Hesse").get("success")
        assert _send_http(client, "propose open borders with Hesse").get("success")
        _advance(w)
        assert _rows(w) == []

    def test_a_counter_offer_return_does_not_ring_a_false_starvation(self, http):
        """Probe-found: the COUNTER_OFFER branch of
        `_process_proposal_in_transit` sets Talleyrand IDLE and skips the
        restore, so the paused mission is read as STARVED (HIGH, "collapses
        in 3 turns") with the DP in hand."""
        w, client = http
        assert _start_http(client, "court Prussia").get("success")
        _advance(w)
        _advance(w)
        w.diplomatic_points = 10
        assert _send_http(client, "propose open borders with Prussia").get("success")
        _advance(w)
        assert w.proposal_in_transit is None
        dm = w.dialogue_manager
        dtypes = [d.get("type") for d in [dm.peek(), *dm.iter_queue()] if d]
        assert "counter_offer_response" in dtypes, (
            f"the proposal did not come back as a counter-offer: {dtypes}")
        assert w.talleyrand_state == "ON_MISSION"
        assert not w.active_diplomatic_mission.get("paused")
        row = _row(w)
        assert row["details"]["beat"] != "paused_starved", (
            f"talleyrand_state={w.talleyrand_state}, "
            f"mission paused={w.active_diplomatic_mission.get('paused')}, "
            f"DP={w.diplomatic_points}: {row['message']}")
        assert row["priority"] == int(NotificationPriority.NORMAL)

    def test_lever_down_a_counter_offer_return_reads_as_starved(self, http):
        """The DOWN arm (review P4 e): with the restore skipped for a
        counter-offer, he is left IDLE with the mission paused, and the rail
        reads the false starvation the fix removed."""
        WS.COUNTER_OFFER_RETURN_RESTORES_HIM = False
        w, client = http
        assert _start_http(client, "court Prussia").get("success")
        _advance(w)
        _advance(w)
        w.diplomatic_points = 10
        assert _send_http(client, "propose open borders with Prussia").get("success")
        _advance(w)
        assert w.proposal_in_transit is None
        dm = w.dialogue_manager
        dtypes = [d.get("type") for d in [dm.peek(), *dm.iter_queue()] if d]
        assert "counter_offer_response" in dtypes, dtypes
        assert w.talleyrand_state != "ON_MISSION"
        assert w.active_diplomatic_mission.get("paused")
        assert _row(w)["details"]["beat"] == "paused_starved"

    def test_a_failed_counter_offer_does_not_strand_him_in_transit(self, http, monkeypatch):
        """Probe-found (pre-existing, `world_state._process_proposal_in_transit`):
        a COUNTER_OFFER outcome with no viable counter terms clears the
        proposal but skips the Talleyrand restore — he stays IN_TRANSIT with
        nothing in transit, every diplomatic order is refused "en route", and
        the paused mission (and its rail row) can never resume or be recalled."""
        w, client = http
        assert _start_http(client, "court Prussia").get("success")
        _advance(w)
        _advance(w)
        w.diplomatic_points = 10
        from backend.game_logic import ai_diplomacy as AID
        monkeypatch.setattr(AID, "generate_counter_offer", lambda proposal, world: None)
        assert _send_http(client, "propose open borders with Prussia").get("success")
        _advance(w)
        assert w.proposal_in_transit is None
        assert w.talleyrand_state != "IN_TRANSIT", (
            "the proposal is resolved and nothing is in transit, but Talleyrand "
            "is still IN_TRANSIT")
        assert _row(w)["details"]["beat"] != "paused_transit"


# ════════════════════════════════════════════════════════════════════
# T8 — the launch is not a rejection
# ════════════════════════════════════════════════════════════════════

class TestTheLaunchIsNotARejection:

    def test_a_start_raises_no_rejection_row(self, http):
        w, client = http
        r = _start_http(client, "court Prussia")
        assert r.get("success")
        assert not r.get("proposal_result")
        assert _proposal_results(w) == []
        assert _row(w)["details"]["beat"] == "begun"

    def test_the_confirm_carries_its_cost(self, http):
        _w, client = http
        dlg = _cmd(client, "court Prussia").get("diplomatic_dialogue") or {}
        assert dlg.get("dp_cost") == 2

    def test_the_cancel_arm_raises_no_rejection_row(self, http):
        w, client = http
        assert _start_http(client, "court Prussia").get("success")
        w.dialogue_manager.replace(DD.generate_mission_dialogue(
            {"target_nation": "Prussia", "mission_type": "CANCEL"}, w))
        top = w.dialogue_manager.peek()
        r = _respond(client, 1, top.get("dialogue_id"))
        assert r.get("success"), r.get("message")
        assert w.active_diplomatic_mission is None
        assert _proposal_results(w) == []
        assert _row(w)["details"]["beat"] == "recalled"

    def test_lever_down_titles_the_launch_a_rejection(self, http):
        DE.MISSION_START_IS_NOT_A_REJECTION = False
        w, client = http
        assert _start_http(client, "court Prussia").get("success")
        rows = _proposal_results(w)
        assert [n["title"] for n in rows] == ["Diplomatic Action Rejected"]


# ════════════════════════════════════════════════════════════════════
# T9 — recall
# ════════════════════════════════════════════════════════════════════

class TestRecall:

    def test_the_ledgers_recall_ends_the_mission(self, http):
        w, client = http
        assert _start_http(client, "court Prussia").get("success")
        with _quiet():
            recall = L.build_strategic_ledger(w)["cabinet"]["recall_command"]
        r = _cmd(client, recall)
        assert r.get("success"), r.get("message")
        assert w.active_diplomatic_mission is None

    def test_the_rails_recall_ends_the_mission(self, http):
        w, client = http
        assert _start_http(client, "court Prussia").get("success")
        r = _cmd(client, _row(w)["details"]["action_command"])
        assert r.get("success"), r.get("message")
        assert w.active_diplomatic_mission is None
        assert _row(w)["details"]["beat"] == "recalled"

    def test_the_recall_is_free(self, http):
        w, client = http
        assert _start_http(client, "court Prussia").get("success")
        ap, dp = w.actions_remaining, w.diplomatic_points
        assert _cmd(client, "Talleyrand, cancel mission with Prussia").get("success")
        assert (w.actions_remaining, w.diplomatic_points) == (ap, dp)

    def test_a_mismatched_recall_is_refused_by_name(self, http):
        w, client = http
        assert _start_http(client, "court Prussia").get("success")
        r = _cmd(client, "Talleyrand, cancel mission with Austria")
        assert r.get("success") is False
        assert r.get("message") == (
            "Talleyrand is in Prussia, not Austria. Recall him from Prussia, or "
            "leave him to his work.")
        assert DD.mission_is_live(w)
        assert w.active_diplomatic_mission["target"] == "Prussia"

    def test_a_bare_recall_cancels(self, http):
        w, client = http
        assert _start_http(client, "court Prussia").get("success")
        r = _cmd(client, "Talleyrand, cancel mission")
        assert r.get("success"), r.get("message")
        assert w.active_diplomatic_mission is None

    @pytest.mark.parametrize("text", ["Talleyrand, cancel mission",
                                      "Talleyrand, cancel mission with Prussia"])
    def test_a_completed_record_is_not_recalled(self, http, text):
        w, client = http
        _stage(w, "GATHER_INTEL", "Prussia", turns_active=3, completed=True)
        r = _cmd(client, text)
        assert r.get("success") is False
        assert r.get("message") == (
            "Talleyrand has no mission running — his last, in Prussia, is already done.")
        assert w.active_diplomatic_mission["completed"] is True

    def test_the_recall_string_is_the_wizards(self):
        body = _gd_func(SCRIPTS / "diplomacy_wizard.gd", "_build_command")
        m = re.search(r'"cancel_mission":\s*\n\s*return "([^"]*)" \+ nation', body)
        assert m, "the wizard's cancel_mission echo moved"
        w = _europe()
        _stage(w, "IMPROVE_RELATIONS", "PapalStates")
        assert DD.mission_recall_command(w) == m.group(1) + "PapalStates"

    def test_papal_states_resolves(self, http):
        w, client = http
        assert _start_http(client, "improve relations with Papal States").get("success")
        assert w.active_diplomatic_mission["target"] == "PapalStates"
        with _quiet():
            cabinet = L.build_strategic_ledger(w)["cabinet"]
        assert cabinet["target_display"] == "Papal States"
        assert _row(w)["title"] == "Talleyrand: Improving Relations - Papal States"
        r = _cmd(client, "Talleyrand, cancel mission with Papal States")
        assert r.get("success"), r.get("message")
        assert "Papal States" in r["message"] and "PapalStates" not in r["message"]

    def test_the_confirm_names_the_court_not_the_tag(self, http):
        """R7: the mission confirm is the player's first sight of the mission."""
        _w, client = http
        dlg = _cmd(client, "improve relations with Papal States").get("diplomatic_dialogue") or {}
        text = dlg.get("talleyrand_text", "")
        assert "Papal States" in text and "PapalStates" not in text, text

    def test_the_transit_row_offers_no_button_the_executor_refuses(self, http):
        """The rail's `paused_transit` beat carries the Recall button, but the
        EC-Q transit gate refuses every `diplomatic_mission` while he is IN
        TRANSIT. A button on the rail must do what it says, or not be there."""
        w, client = http
        _hesse_world(w)
        assert _start_http(client, "improve relations with Hesse").get("success")
        assert _send_http(client, "propose open borders with Hesse").get("success")
        row = _row(w)
        assert row["details"]["beat"] == "paused_transit"
        button = row["details"].get("action_command")
        if button:
            r = _cmd(client, button)
            assert r.get("success"), f"the rail's Recall is refused: {r.get('message')}"

    def test_lever_down_a_mismatched_recall_clears_the_mission(self, http):
        DE.MISSION_CANCEL_READS_THE_NAME = False
        w, client = http
        assert _start_http(client, "court Prussia").get("success")
        r = _cmd(client, "Talleyrand, cancel mission with Austria")
        assert r.get("success")
        assert w.active_diplomatic_mission is None


# ════════════════════════════════════════════════════════════════════
# T10 — the ledger carries the Cabinet
# ════════════════════════════════════════════════════════════════════

class TestTheLedgerCarriesTheCabinet:

    def _ledger(self, w):
        with _quiet():
            return L.build_strategic_ledger(w)

    def test_live(self):
        w = _typed_world("IMPROVE_RELATIONS")
        cabinet = self._ledger(w)["cabinet"]
        assert cabinet["live"] is True
        assert cabinet["type_display"] == "Improving Relations"
        assert cabinet["target_display"] == "Prussia"
        assert cabinet["recall_command"] == "Talleyrand, cancel mission with Prussia"

    def test_idle(self):
        assert self._ledger(_europe())["cabinet"] == {"live": False}

    def test_idle_with_the_last_mission(self):
        w = _europe()
        provinces = sum(1 for r in w.regions.values() if r.controller == "Prussia")
        _stage(w, "GATHER_INTEL", "Prussia")
        for _ in range(3):
            _tick(w)
        assert w.active_diplomatic_mission.get("completed")
        expiry = int(w.current_turn) + 5
        assert self._ledger(w)["cabinet"] == {
            "live": False,
            "last": {
                "type_display": "Gathering Intel",
                "target_display": "Prussia",
                "reason": "duration",
                "regions": provinces,
                "expiry": expiry,
                "reason_phrase": (f"done — {provinces} province"
                                  f"{'' if provinces == 1 else 's'} open to us "
                                  f"until turn {expiry}"),
            },
        }

    def test_every_number_is_an_int(self):
        for mission_type in _TYPED:
            cabinet = self._ledger(_typed_world(mission_type))["cabinet"]
            floats = [(p, v) for p, v in _walk_numbers(cabinet) if isinstance(v, float)]
            assert not floats, (mission_type, floats)

    def test_the_orders_list_is_untouched_and_the_lever_drops_the_key(self):
        w = _typed_world("COURT_NATION")
        on = self._ledger(w)
        L.MISSION_LEDGER_BLOCK = False
        off = self._ledger(w)
        assert "cabinet" not in off
        assert on["orders"] == off["orders"]
        assert all("marshal" in o for o in on["orders"])


# ════════════════════════════════════════════════════════════════════
# T11 — the log records the end
# ════════════════════════════════════════════════════════════════════

def _ended(w):
    return [e for e in w.event_log if e.get("type") == "diplomatic_mission_ended"]


class TestTheLogRecordsTheEnd:

    def test_ceiling(self):
        w = _europe()
        _set_rel(w, "France", "Prussia", 95)
        _stage(w, "IMPROVE_RELATIONS", "Prussia")
        _tick(w)
        (row,) = _ended(w)
        assert (row["reason"], row["mission_type"], row["target"]) == (
            "ceiling", "IMPROVE_RELATIONS", "Prussia")
        assert (row["turns_active"], row["dp_spent"]) == (1, 1)
        assert (row["relation_start"], row["relation_end"]) == (95, 100)

    def test_duration(self):
        w = _europe()
        provinces = sum(1 for r in w.regions.values() if r.controller == "Prussia")
        _stage(w, "GATHER_INTEL", "Prussia")
        for _ in range(3):
            _tick(w)
        (row,) = _ended(w)
        assert row["reason"] == "duration"
        assert (row["turns_active"], row["dp_spent"]) == (3, 3)
        assert row["regions_revealed"] == provinces > 0

    def test_alliance_broken(self):
        w = _typed_world("UNDERMINE_ALLIANCE")
        _tick(w)
        assert _ended(w) == []
        _set_state(w, "Austria", "Russia", "PEACE")     # the alliance breaks
        _tick(w)
        (row,) = _ended(w)
        assert row["reason"] == "alliance_broken"
        assert (row["turns_active"], row["dp_spent"]) == (2, 4)

    def test_recalled(self):
        w = _europe()
        _stage(w, "COURT_NATION", "Prussia", turns_active=2)
        with _quiet():
            assert CommandExecutor()._diplomatic._recall_mission(None, w)["success"]
        (row,) = _ended(w)
        assert (row["reason"], row["turns_active"], row["dp_spent"]) == ("recalled", 2, 4)

    def test_starved(self):
        w = _europe()
        _stage(w, "IMPROVE_RELATIONS", "Prussia", turns_active=4, paused=True, paused_turns=2)
        w.diplomatic_points = 0
        with _quiet():
            D._process_mission_dp(w)
        assert w.active_diplomatic_mission is None
        (row,) = _ended(w)
        assert row["reason"] == "starved"
        assert _row(w)["details"]["beat"] == "collapsed"
        assert _row(w)["priority"] == int(NotificationPriority.HIGH)

    def test_elimination_keeps_its_own_row(self):
        w = _europe()
        _stage(w, "IMPROVE_RELATIONS", "Hesse")
        for region in w.regions.values():
            if region.controller == "Hesse":
                region.controller = "France"
        for marshal in w.marshals.values():
            if marshal.nation == "Hesse":
                marshal.strength = 0
        with _quiet():
            D._check_mission_target_eliminated(w)
        assert w.active_diplomatic_mission is None
        assert _ended(w) == []
        assert [e for e in w.event_log
                if e.get("type") == "diplomatic_mission_cancelled_eliminated"]
        assert _row(w)["details"]["beat"] == "eliminated"
        assert _row(w)["message"] == (
            "Talleyrand's mission to Hesse has ended — Hesse no longer exists.")

    def test_the_one_liners_are_english(self):
        w = _europe()
        _stage(w, "COURT_NATION", "PapalStates", turns_active=2)
        w.log_event({"type": "diplomatic_mission_started",
                     "mission_type": "COURT_NATION", "target": "PapalStates"})
        with _quiet():
            CommandExecutor()._diplomatic._recall_mission(None, w)
        started = [e for e in w.event_log if e.get("type") == "diplomatic_mission_started"][-1]
        (ended,) = _ended(w)
        assert CL.format_event_oneliner(started) == "Talleyrand sent to Papal States: Courting."
        line = CL.format_event_oneliner(ended)
        assert line == "Talleyrand's mission to Papal States ended: recalled (2 turns, 4 DP)."
        for text in (CL.format_event_oneliner(started), line):
            assert "_" not in text and "PapalStates" not in text
            assert "COURT_NATION" not in text

    def test_every_reason_reads_without_a_key(self):
        rows = []
        w = _europe()
        _set_rel(w, "France", "Prussia", 95)
        _stage(w, "IMPROVE_RELATIONS", "Prussia")
        _tick(w)
        rows += _ended(w)
        w = _europe()
        _stage(w, "GATHER_INTEL", "Prussia")
        for _ in range(3):
            _tick(w)
        rows += _ended(w)
        w = _typed_world("UNDERMINE_ALLIANCE")
        _set_state(w, "Austria", "Russia", "PEACE")
        _tick(w)
        rows += _ended(w)
        w = _europe()
        _stage(w, "IMPROVE_RELATIONS", "Prussia", paused=True, paused_turns=2)
        w.diplomatic_points = 0
        with _quiet():
            D._process_mission_dp(w)
        rows += _ended(w)
        assert sorted(r["reason"] for r in rows) == [
            "alliance_broken", "ceiling", "duration", "starved"]
        for row in rows:
            line = CL.format_event_oneliner(row)
            assert "_" not in line, line
            assert not re.search(r"\b[A-Z]{3,}_[A-Z]", line), line
        kept = CL.filter_campaign_log(rows, _europe())
        assert len(kept) == len(rows), "the fog must pass the player's own mission"

    def test_the_type_is_registered(self):
        assert "diplomatic_mission_ended" in CL.CAMPAIGN_LOG_TYPES
        assert CL.CATEGORY_MAP["diplomatic_mission_ended"] == "diplomacy"
        assert len(CL.CAMPAIGN_LOG_TYPES) == 165  # 164->165 flipped consciously: IQ-7 (Sept 16, 2026) adds `client_petition_answered` — a loyal satellite's petition (THE PROVINCE / THE RELIEF) is the web's first non-rebellion decision, and its answer — granted, refused, or left to lapse — had no persistent surface (no inert diplomacy type was retired in exchange: the six producerless ones are the FA-R5 census's, not this slice's)

    def test_lever_down_logs_no_end(self):
        DD.MISSION_LOG_ENDS = False
        w = _europe()
        _stage(w, "COURT_NATION", "Prussia", turns_active=2)
        with _quiet():
            CommandExecutor()._diplomatic._recall_mission(None, w)
        assert _ended(w) == []
        assert _row(w)["details"]["beat"] == "recalled", "the rail still rings"

    def test_lever_down_the_started_line_is_todays(self):
        CL.THE_LOG_NAMES_THE_MISSION = False
        line = CL.format_event_oneliner({"type": "diplomatic_mission_started",
                                         "mission_type": "COURT_NATION",
                                         "target": "PapalStates"})
        assert line == "Talleyrand dispatched on COURT NATION to PapalStates"


# ════════════════════════════════════════════════════════════════════
# T12 — the help names the missions
# ════════════════════════════════════════════════════════════════════

_HELP_END = "recall him from either, free."


def _help_block(client):
    message = _cmd(client, "help").get("message") or ""
    assert "  missions   -" in message, "the missions entry is missing"
    start = message.index("  missions   -")
    return message[start:message.index(_HELP_END, start) + len(_HELP_END)]


def _family_keywords():
    gd = (SCRIPTS / "main.gd").read_text(encoding="utf-8")
    m = re.search(r"const\s+DIPLO_FAMILY_KEYWORDS\s*=\s*\[(.*?)\n\]", gd, re.S)
    assert m, "DIPLO_FAMILY_KEYWORDS not found in main.gd"
    words = re.findall(r'"([^"]*)"', m.group(1))
    assert words
    return words


class TestTheHelpNamesTheMissions:

    def test_talleyrand_at_ten(self, http):
        _w, client = http
        block = _help_block(client)
        for line in ("Improve Relations - 1 DP a turn", "Court - 2 DP a turn",
                     "Reassure Ally - 1 DP a turn", "Undermine Alliance - 2 DP a turn",
                     "Gather Intel - 1 DP a turn"):
            assert line in block, line
        assert block.count("+8 relation/turn") == 2, "Improve and Court"
        assert "+4 relation/turn" in block
        assert "-4 relation between targets/turn" in block
        assert "F1" in block

    def test_a_skill_five_diplomat_reads_his_own_figures(self, http):
        w, client = http
        w.diplomats["France"].skill = 5
        block = _help_block(client)
        assert block.count("+4 relation/turn") == 2
        assert "+2 relation/turn" in block
        assert "-2 relation between targets/turn" in block
        assert "+8 relation" not in block

    def test_no_quoted_typed_mission_verb(self, http):
        _w, client = http
        block = _help_block(client).lower()
        quoted = re.findall(r'"([^"]*)"', block)
        for keyword in _family_keywords():
            for q in quoted:
                assert keyword.lower() not in q, (keyword, q)

    def test_lever_down_drops_the_entry(self, http):
        ME.MISSION_HELP_BLOCK = False
        _w, client = http
        message = _cmd(client, "help").get("message") or ""
        assert "  missions   -" not in message
        assert "war terms" in message


# ════════════════════════════════════════════════════════════════════
# T13 — the School names the Cabinet
# ════════════════════════════════════════════════════════════════════

class TestTheSchoolNamesTheCabinet:

    def _entry(self):
        src = (SCRIPTS / "tutorial_overlay.gd").read_text(encoding="utf-8")
        m = re.search(r'"id":\s*"free_books".*?"advance"', src, re.S)
        assert m
        return m.group(0)

    def test_five_instruments_and_the_mission(self):
        entry = self._entry()
        assert "Five more instruments" in entry
        assert "Four more instruments" not in entry
        assert ("And from F1 you may send Talleyrand himself on a mission — to warm "
                "a court, reassure an ally, spy, or pry two allies apart; it costs "
                "diplomatic points every turn it runs, and stands in the ledger's "
                "Orders book and on the notice rail until it is done.") in entry

    def test_no_chip(self):
        assert re.search(r'"suggest":\s*""', self._entry())

    def test_the_script_names_the_row(self):
        assert "IQ-4" in (ROOT / "docs" / "TUTORIAL_SCRIPT.md").read_text(encoding="utf-8")


# ════════════════════════════════════════════════════════════════════
# T14 — the client reads it (source scrapes, scoped to function bodies)
# ════════════════════════════════════════════════════════════════════

class TestTheClientReadsIt:

    def test_the_orders_tab_renders_the_cabinet_first(self):
        """Code only (review P4 b): comments stripped, and the warning colour
        read inside the Cabinet block's `paused` branch — the FA-N36 idle
        line below it already used COLOR_WARNING."""
        body = _gd_code(SCRIPTS / "strategic_ledger.gd", "_render_orders")
        assert 'cached_data.get("cabinet")' in body
        assert "[url=do:" in body
        assert body.index('cached_data.get("cabinet")') < body.index("if orders.size() == 0")
        cabinet = body[body.index("var cabinet ="):body.index("if orders.size() == 0")]
        assert re.search(r'if paused:\s*\n\s*bbcode \+= "\[color=#" \+ Utils\.COLOR_WARNING'
                         r' \+ "\]" \+ head', cabinet), "the paused Cabinet is not a warning"
        assert "═══ THE CABINET ═══" in body
        assert ("Talleyrand is at the Cabinet. Press F1, choose a court, and send him "
                "on a mission.") in body

    @pytest.mark.parametrize("func,var", [("update_diplomatic_fields", "mission_summary"),
                                          ("_set_talleyrand_summary", "clean_summary")])
    def test_the_top_bar_reads_none_as_idle(self, func, var):
        code = _gd_code(SCRIPTS / "top_bar.gd", func)
        assert re.search(r"if [^\n]*\b" + var + r' == "None"', code), code

    def test_the_rail_maps_the_type(self):
        src = (SCRIPTS / "notification_bar.gd").read_text(encoding="utf-8")
        icons = re.search(r"const TYPE_ICONS = \{(.*?)\n\}", src, re.S).group(1)
        svgs = re.search(r"const TYPE_ICON_SVGS = \{(.*?)\n\}", src, re.S).group(1)
        assert '"diplomatic_mission": "MSN"' in icons
        assert '"diplomatic_mission": "book-open"' in svgs
        assert (ROOT / "godot-client" / "project-sovereign" / "assets" / "ui" / "icons"
                / "phosphor" / "book-open.svg").exists()

    def test_the_talleyrand_tab_renders_the_note(self):
        code = _gd_code(SCRIPTS / "diplomatic_ledger.gd", "_render_talleyrand")
        assert 'mission.get("remaining_note"' in code
        assert 't.get("last_mission")' in code
        assert 'last_mission.get("reason_phrase"' in code


# ════════════════════════════════════════════════════════════════════
# T15 — every mission has its cell (completion part (i))
# ════════════════════════════════════════════════════════════════════

def _hesse_like(court, relation):
    w = _europe()
    _set_rel(w, "France", court, relation)
    return w


def _dp_to_accept(w, mission_type, target, proposal_type, limit=40):
    """Fewest DP to a bare ACCEPT by real ticks; (dp, turns) or None."""
    _stage(w, mission_type, target)
    cost = int(DD.MISSION_DP_COSTS[mission_type])
    for n in range(limit + 1):
        if _score(w, _proposal(target, ptype=proposal_type))["score"] >= 50:
            return n * cost, n
        if not DD.mission_is_live(w):
            return None
        _tick(w)
    return None


class TestEveryMissionHasItsCell:

    def test_improve_is_uniquely_best_for_saxonys_alliance(self):
        improve = _dp_to_accept(_europe(), "IMPROVE_RELATIONS", "Saxony", "alliance")
        court = _dp_to_accept(_europe(), "COURT_NATION", "Saxony", "alliance")
        assert improve and court, (improve, court)
        assert improve[0] < court[0], (improve, court)

    def test_court_is_uniquely_best_for_prussias_bare_alliance(self):
        """Among missions, bare offer (contract B1): relation alone stops at 48."""
        def at_sixty():
            w = _europe()
            _set_rel(w, "France", "Prussia", 60)
            return w
        assert _dp_to_accept(at_sixty(), "IMPROVE_RELATIONS", "Prussia", "alliance") is None
        assert _dp_to_accept(at_sixty(), "COURT_NATION", "Prussia", "alliance") is not None

    @pytest.mark.parametrize("court,relation,court_road,improve_road", [
        ("Denmark", 10, (2, 1), (2, 2)),     # same DP, one turn sooner
        ("Prussia", 10, (4, 2), (4, 4)),     # same DP, two turns sooner
    ])
    def test_court_is_uniquely_best_on_a_rung_the_cabinet_offers(
            self, court, relation, court_road, improve_road):
        """T15's own definition, on rows the Cabinet OFFERS (integration
        finding): at PEACE the Cabinet offers the Court and Improve rows and
        the next rung, Open Borders, short of ACCEPT. By T15's rule — fewest
        DP, ties to fewer turns — courting is uniquely best."""
        w = _europe()
        w.diplomatic_points = 10
        _set_rel(w, "France", court, relation)
        assert w.get_diplomatic_state("France", court) == "PEACE"
        rows = {a["action"]: a for a in D.get_available_diplomatic_actions(w, court)}
        for row in ("mission_court", "mission_improve_relations", "propose_open_borders"):
            assert rows[row]["available"], (row, rows[row].get("disabled_reason"))
        assert rows["propose_open_borders"]["likelihood_score"] < D.ACCEPT_SCORE
        cr = _dp_to_accept(_hesse_like(court, relation), "COURT_NATION", court, "open_borders")
        ir = _dp_to_accept(_hesse_like(court, relation), "IMPROVE_RELATIONS", court,
                           "open_borders")
        assert (cr, ir) == (court_road, improve_road)
        assert cr < ir, "fewest DP, ties to fewer turns"

    def test_the_alliance_leap_is_unpayable_while_courting(self, http):
        """Why T15 reads the OFFERED rungs: the only cell past relation's cap
        (Prussia's alliance, 48 at relation 60+) is a leap up the ladder that
        costs 4-6 DP, and a courting France holds 3 (5 regen, 2 to the
        mission). Measured through the typed road."""
        w, client = http
        _set_state(w, "France", "Prussia", "NON_AGGRESSION")
        _set_rel(w, "France", "Prussia", 60)
        assert _start_http(client, "court Prussia").get("success")
        _advance(w)
        assert w.diplomatic_points == 3
        assert D.get_transition_dp_cost("NON_AGGRESSION", "ALLIANCE") == 4
        r = _cmd(client, "propose alliance with Prussia")
        assert r.get("success") is False
        assert "costs 4 DP, but we only have 3" in (r.get("message") or "")

    def test_reassure_is_the_only_relation_row_for_an_ally(self):
        w = _europe()
        w.diplomatic_points = 10
        assert w.get_diplomatic_state("France", "Bavaria") == "ALLIANCE"
        rows = {a["action"] for a in D.get_available_diplomatic_actions(w, "Bavaria")}
        relation_rows = rows & {"mission_improve_relations", "mission_court", "mission_reassure"}
        assert relation_rows == {"mission_reassure"}

    def test_gather_and_undermine_alone_do_their_work(self):
        effects = DD.MISSION_EFFECTS
        assert [t for t, e in effects.items() if e.get("duration")] == ["GATHER_INTEL"]
        assert [t for t, e in effects.items() if e.get("target_pair_relation_change")] == [
            "UNDERMINE_ALLIANCE"]
        w = _europe()
        _stage(w, "GATHER_INTEL", "Prussia")
        for _ in range(3):
            _tick(w)
        prussian = {r.name for r in w.regions.values() if r.controller == "Prussia"}
        assert prussian and prussian <= set(w.intel_grants)
        w = _typed_world("UNDERMINE_ALLIANCE")
        before = _rel(w, "Austria", "Russia")
        w.diplomatic_points = 10
        with _quiet():
            D._process_mission_dp(w)
            D._process_mission_effects(w)
        assert _rel(w, "Austria", "Russia") - before == -4

    def test_lever_down_the_court_has_no_cell(self):
        D.COURT_FAVOUR_ACTIVE = False
        w = _europe()
        _set_rel(w, "France", "Prussia", 60)
        assert _dp_to_accept(w, "COURT_NATION", "Prussia", "alliance") is None


# ════════════════════════════════════════════════════════════════════
# T16 — counsel names the court
# ════════════════════════════════════════════════════════════════════

_COURT_COUNSEL = ("Relations with Prussia can do no more for this treaty. "
                  "Talleyrand recommends: Court Prussia — every turn at their court "
                  "adds 2 to our proposals, up to 10.")
_IMPROVE_COUNSEL = ("No proposal would find purchase now. Talleyrand recommends: "
                    "Improve Relations mission to warm the diplomatic climate.")


def _staged_actions(score):
    return [
        {"action": "propose_alliance", "display_name": "Propose Alliance",
         "available": True, "likelihood_score": score},
        {"action": "mission_improve_relations", "available": True},
        {"action": "mission_court", "available": True},
    ]


class TestCounselNamesTheCourt:

    def _world(self, relation):
        w = _europe()
        _set_rel(w, "France", "Prussia", relation)
        return w

    def test_relation_sixty_and_forty_eight_names_the_court(self):
        out = D._recommendation_and_mission(
            self._world(60), "Prussia", _staged_actions(48), 10, False, {})
        assert out == (_COURT_COUNSEL, "COURT_NATION")

    def test_the_cheaper_road_is_counselled_and_the_quicker_one_named(self):
        """Review repair: the forecast now reads the formula's own
        relation-free sum, so a staged `likelihood_score` no longer drives it
        — the pin reads a REAL row. Prussia at PEACE, relation -15 (odd): Open
        Borders short of ACCEPT; improving is cheaper, courting quicker, and
        the quoted figures are the real ticks'."""
        w = self._world(-15)
        w.diplomatic_points = 10
        assert w.get_diplomatic_state("France", "Prussia") == "PEACE"
        actions = D.get_available_diplomatic_actions(w, "Prussia")
        rows = {a["action"]: a for a in actions}
        assert rows["propose_open_borders"]["available"]
        assert rows["propose_open_borders"]["likelihood_score"] < D.ACCEPT_SCORE
        c_dp, c_turns = _dp_to_accept(_hesse_like("Prussia", -15), "COURT_NATION",
                                      "Prussia", "open_borders")
        i_dp, i_turns = _dp_to_accept(_hesse_like("Prussia", -15), "IMPROVE_RELATIONS",
                                      "Prussia", "open_borders")
        assert i_dp < c_dp and c_turns < i_turns, ((c_dp, c_turns), (i_dp, i_turns))
        text, mission = D._recommendation_and_mission(w, "Prussia", actions, 10, False, {})
        assert mission == "IMPROVE_RELATIONS"
        assert text.startswith(_IMPROVE_COUNSEL)
        assert "Courting Prussia would be quicker" in text
        assert text == (_IMPROVE_COUNSEL + f" Courting Prussia would be quicker — "
                        f"≈{D._turns_phrase(c_turns)} against ≈{D._turns_phrase(i_turns)}, "
                        f"but {c_dp} DP to {i_dp}.")

    def test_court_is_counselled_where_it_is_no_dearer(self):
        """Denmark at PEACE, relation 10: Open Borders at 45. Courting 1 turn
        for 2 DP; improving 2 turns for 2 DP."""
        w = _europe()
        w.diplomatic_points = 10
        _set_rel(w, "France", "Denmark", 10)
        with _quiet():
            preview = D.get_diplomatic_preview(w, "Denmark")
        assert preview["recommendation"] == (
            "Talleyrand recommends: Court Denmark — ≈1 turn and 2 DP to carry Open "
            "Borders Agreement; improving relations would take ≈2 turns and 2 DP.")
        assert preview["recommended_mission"] == "COURT_NATION"

    def test_the_real_preview_carries_the_machine_key(self):
        w = _europe()
        w.diplomatic_points = 10
        with _quiet():
            preview = D.get_diplomatic_preview(w, "Prussia")
        assert preview["recommendation"] == (
            _IMPROVE_COUNSEL + " Courting Prussia would be quicker — ≈4 turns "
            "against ≈6 turns, but 8 DP to 6.")
        assert preview["recommended_mission"] == "IMPROVE_RELATIONS"

    @pytest.mark.parametrize("court,relation", [("Prussia", -10), ("Denmark", 10),
                                                ("Ottoman", -10),
                                                # odd relations (review S1): the
                                                # double rounding lived here
                                                ("Prussia", 25), ("Prussia", -5),
                                                ("Prussia", 11), ("Denmark", 11)])
    def test_the_forecast_is_the_tick(self, court, relation):
        """The counsel's figures are the real ticks' (quiet world), on both
        parities — every even cell matched before the review, and every odd
        cell was a turn out."""
        w = _europe()
        w.diplomatic_points = 10
        _set_rel(w, "France", court, relation)
        score = {a["action"]: a for a in D.get_available_diplomatic_actions(w, court)}[
            "propose_open_borders"]["likelihood_score"]
        for mission in ("COURT_NATION", "IMPROVE_RELATIONS"):
            forecast = D.forecast_mission_to_accept(w, court, "open_borders", score, mission)
            assert forecast == _dp_to_accept(_hesse_like(court, relation), mission, court,
                                             "open_borders")[::-1]

    def test_lever_down_the_string_is_todays(self):
        D.COUNSEL_NAMES_THE_COURT = False
        w = self._world(60)
        assert D._build_recommendation(w, "Prussia", _staged_actions(48), 10, False, {}) \
            == "Talleyrand recommends: Propose Alliance"
        w = _europe()
        w.diplomatic_points = 10
        with _quiet():
            preview = D.get_diplomatic_preview(w, "Prussia")
        assert "recommended_mission" not in preview
        assert preview["recommendation"] == _IMPROVE_COUNSEL

    def test_the_counsel_can_fire_on_the_shipped_board(self):
        """S3i exists so a player can DISCOVER the Court's Favour. The
        original cell (relation 60+) never fired — every offered row carries
        there — so the counsel is re-grounded on the rungs below it."""
        base = _europe()
        courts = [n for n in base.get_active_nations()
                  if n != base.player_nation and n not in base.vassals]
        fired = []
        for court in courts:
            for state in ("PEACE", "OPEN_BORDERS", "NON_AGGRESSION"):
                for relation in (-10, 0, 10, 20):
                    w = _europe()
                    w.diplomatic_points = 10
                    _set_state(w, "France", court, state)
                    _set_rel(w, "France", court, relation)
                    with _quiet():
                        actions = D.get_available_diplomatic_actions(w, court)
                        _text, mission = D._recommendation_and_mission(
                            w, court, actions, 10, False, w.vassals)
                    if mission == "COURT_NATION":
                        fired.append((court, state, relation))
        assert {("Denmark", "PEACE", 10), ("Prussia", "PEACE", 10),
                ("Spain", "PEACE", 0)} <= set(fired), fired


# ════════════════════════════════════════════════════════════════════
# T17 — REASSURE only at ALLIANCE
# ════════════════════════════════════════════════════════════════════

class TestReassureOnlyAtAlliance:

    def _rows(self, state):
        w = _europe()
        w.diplomatic_points = 10
        _set_state(w, "France", "Bavaria", state)
        return {a["action"] for a in D.get_available_diplomatic_actions(w, "Bavaria")}

    def test_the_defensive_alliance_rows(self):
        rows = self._rows("DEFENSIVE_ALLIANCE")
        assert "mission_reassure" not in rows
        assert "mission_improve_relations" in rows

    def test_the_alliance_rows_keep_it(self):
        assert "mission_reassure" in self._rows("ALLIANCE")

    def test_lever_down_restores_the_row(self):
        D.REASSURE_ONLY_AT_ALLIANCE = False
        assert "mission_reassure" in self._rows("DEFENSIVE_ALLIANCE")


# ════════════════════════════════════════════════════════════════════
# §7 R2 — settlement gratitude reads the proposal's own spelling
# ════════════════════════════════════════════════════════════════════

class TestGratitudeReadsTheProposalCase:

    def _grateful(self):
        w = _europe()
        _set_rel(w, "France", "Prussia", 60)
        SR._add_settlement_memory(
            w, actor="France", subject="Prussia", memory_type="settlement_gratitude",
            episode_id="iq4-r2", payload={}, expires_in=10)
        return w

    @pytest.mark.parametrize("ptype", ["alliance", "defensive_alliance"])
    def test_a_real_alliance_offer_carries_it(self, ptype):
        w = self._grateful()
        comps = _score(w, _proposal(ptype=ptype))["components"]
        assert comps["settlement_gratitude_mod"] == SR.SETTLEMENT_GRATITUDE_MOD

    def test_the_typed_alliance_offer_carries_it(self, http):
        w, client = http
        _set_state(w, "France", "Prussia", "DEFENSIVE_ALLIANCE")
        _set_rel(w, "France", "Prussia", 60)
        SR._add_settlement_memory(
            w, actor="France", subject="Prussia", memory_type="settlement_gratitude",
            episode_id="iq4-r2", payload={}, expires_in=10)
        assert _send_http(client, "propose alliance with Prussia").get("success")
        proposal = w.proposal_in_transit["proposal"]
        assert proposal["type"] == "alliance"
        assert _score(w, proposal)["components"]["settlement_gratitude_mod"] == 5

    def test_other_types_are_untouched(self):
        w = self._grateful()
        assert _score(w, _proposal(ptype="open_borders"))["components"][
            "settlement_gratitude_mod"] == 0

    def test_lever_down_reproduces_the_lost_term(self):
        SR.GRATITUDE_HOOK_READS_THE_PROPOSAL_CASE = False
        w = self._grateful()
        assert _score(w, _proposal())["components"]["settlement_gratitude_mod"] == 0
        assert SR.settlement_gratitude_mod(w, "France", "Prussia", "ALLIANCE") == 5


# ════════════════════════════════════════════════════════════════════
# Integration pins — the lead's fixes on the fleet's report
# ════════════════════════════════════════════════════════════════════

class TestIntegrationPins:

    def test_no_recall_is_offered_while_he_carries_a_proposal(self):
        """The EC-Q transit gate refuses a mission order in transit, so the
        Cabinet's [Recall] (hidden on "") and the rail's button stay away."""
        w = _europe()
        _stage(w, "IMPROVE_RELATIONS", "Prussia", paused=True)
        w.talleyrand_state = "IN_TRANSIT"
        assert DD.mission_status(w)["recall_command"] == ""
        with _quiet():
            assert L.build_cabinet(w)["recall_command"] == ""
        w.talleyrand_state = "ON_MISSION"
        w.active_diplomatic_mission["paused"] = False
        assert DD.mission_status(w)["recall_command"] == (
            "Talleyrand, cancel mission with Prussia")

    def test_the_intelligence_end_row_carries_its_expiry(self):
        w = _europe()
        _stage(w, "GATHER_INTEL", "Prussia")
        for _ in range(3):
            _tick(w)
        rows = [e for e in w.event_log if e.get("type") == "diplomatic_mission_ended"]
        assert rows and rows[-1]["reason"] == "duration"
        assert rows[-1]["expiry"] == int(w.current_turn) + 5

    def test_a_replaced_mission_is_logged_as_ended(self):
        w = _hesse_world(_europe())
        assert _start_exec(w, "IMPROVE_RELATIONS", "Hesse")["success"]
        assert _start_exec(w, "IMPROVE_RELATIONS", "Saxony")["success"]
        ended = [e for e in w.event_log if e.get("type") == "diplomatic_mission_ended"]
        assert [(e["target"], e["reason"]) for e in ended] == [("Hesse", "replaced")]
        order = [e.get("type") for e in w.event_log
                 if str(e.get("type", "")).startswith("diplomatic_mission_")]
        assert order[-2:] == ["diplomatic_mission_ended", "diplomatic_mission_started"]
        assert "replaced by a new mission" in CL.format_event_oneliner(ended[-1])
        assert _row(w)["details"]["beat"] == "begun"

    def test_a_drifting_rung_is_forecast_by_the_tick(self):
        """A cell where the courted pair's drift exemption changes the road:
        Prussia at NON_AGGRESSION, relation 30, the defensive alliance."""
        w = _europe()
        w.diplomatic_points = 10
        _set_state(w, "France", "Prussia", "NON_AGGRESSION")
        _set_rel(w, "France", "Prussia", 30)
        score = {a["action"]: a for a in D.get_available_diplomatic_actions(w, "Prussia")}[
            "propose_defensive_alliance"]["likelihood_score"]
        for mission in ("COURT_NATION", "IMPROVE_RELATIONS"):
            real = _hesse_like("Prussia", 30)
            _set_state(real, "France", "Prussia", "NON_AGGRESSION")
            forecast = D.forecast_mission_to_accept(
                w, "Prussia", "defensive_alliance", score, mission)
            assert forecast == _dp_to_accept(real, mission, "Prussia",
                                             "defensive_alliance")[::-1]


# ════════════════════════════════════════════════════════════════════
# The IQ-4 review round — each fix pinned, with its lever's DOWN arm
# ════════════════════════════════════════════════════════════════════

_WAR_NOTE = ("no favour while we are at war — his courting still warms relations, "
             "and the favour returns at the peace")
_HOLD_NOTE = ("the favour stands at +10 and holds while he stays — recall him once "
              "the treaty is signed")
_BLOWBACK = " Courting risks blowback — a 20% chance a turn of -3."
_NO_MORE_BRITAIN = ("Relations with Britain can do no more for this treaty. "
                    "Talleyrand recommends: Court Britain — every turn at their court "
                    "adds 2 to our proposals, up to 10.")


def _fund_advance(w, n=1):
    for _ in range(n):
        w.diplomatic_points = max(int(w.diplomatic_points), 10)
        _advance(w)


def _floor(state):
    return int(D.STATE_RELATION_THRESHOLDS[state]) - 30


class TestReviewTheForecastRoundsOnce:
    """S1: the forecast rebuilt its constant terms from the ROUNDED score and
    rounded again, so every odd relation (relation/2 is x.5 under
    round-half-even) put it a turn out — 75 cells at skill 10, and 39 counsel
    picks flipped. It now adds back the formula's own relation-free sum."""

    @pytest.mark.parametrize("skill", [10, 5])
    @pytest.mark.parametrize("court,state,relation,ptype", [
        ("Prussia", "PEACE", 25, "open_borders"),
        ("Prussia", "PEACE", 24, "open_borders"),
        ("Prussia", "PEACE", -5, "open_borders"),
        ("Russia", "PEACE", -5, "open_borders"),
        ("Russia", "PEACE", -4, "open_borders"),
        ("Britain", "OPEN_BORDERS", 11, "non_aggression"),
        ("Britain", "OPEN_BORDERS", 10, "non_aggression"),
    ])
    def test_the_forecast_is_the_tick_on_both_parities(self, court, state, relation,
                                                        ptype, skill):
        def world():
            w = _europe()
            w.diplomatic_points = 10
            w.diplomats["France"].skill = skill       # 5: staged, an authored skill
            if w.get_diplomatic_state("France", court) != state:
                _set_state(w, "France", court, state)
            _set_rel(w, "France", court, relation)
            return w
        w = world()
        row = {a["action"]: a for a in D.get_available_diplomatic_actions(w, court)}[
            f"propose_{ptype}"]
        assert row["available"] and 0 < row["likelihood_score"] < D.ACCEPT_SCORE
        for mission in ("COURT_NATION", "IMPROVE_RELATIONS"):
            forecast = D.forecast_mission_to_accept(w, court, ptype, row["likelihood_score"],
                                                    mission)
            real = _dp_to_accept(world(), mission, court, ptype)
            assert forecast == (real[::-1] if real else None), (mission, forecast, real)

    def test_the_reviews_headline_cells(self):
        """Russia at -5: improving takes 3 turns / 3 DP (the forecast said 4 / 4
        and counselled the dearer road). Britain at OPEN_BORDERS, 11: 6 / 6
        (it said 5 / 5 and told the player improving saved a DP)."""
        w = _europe()
        w.diplomatic_points = 10
        _set_state(w, "France", "Russia", "PEACE")      # Russia boots at war with France
        _set_rel(w, "France", "Russia", -5)
        with _quiet():
            preview = D.get_diplomatic_preview(w, "Russia")
        assert preview["recommended_mission"] == "IMPROVE_RELATIONS"
        assert "would be quicker — ≈2 turns against ≈3 turns, but 4 DP to 3." in \
            preview["recommendation"]
        w = _europe()
        w.diplomatic_points = 10
        _set_state(w, "France", "Britain", "OPEN_BORDERS")
        _set_rel(w, "France", "Britain", 11)
        with _quiet():
            preview = D.get_diplomatic_preview(w, "Britain")
        assert preview["recommended_mission"] == "COURT_NATION"
        assert preview["recommendation"] == (
            "Talleyrand recommends: Court Britain — ≈3 turns and 6 DP to carry "
            "Non-Aggression Pact; improving relations would take ≈6 turns and 6 DP.")

    def test_a_census_of_both_parities(self):
        checked = 0
        for court in ("Prussia", "Russia", "Britain"):
            for relation in range(-25, 36, 3):
                def world():
                    w = _europe()
                    w.diplomatic_points = 10
                    _set_rel(w, "France", court, relation)
                    return w
                w = world()
                if w.get_diplomatic_state("France", court) != "PEACE":
                    _set_state(w, "France", court, "PEACE")
                row = {a["action"]: a for a in D.get_available_diplomatic_actions(w, court)}.get(
                    "propose_open_borders")
                if not row or not row["available"] or \
                        not 0 < row["likelihood_score"] < D.ACCEPT_SCORE:
                    continue
                for mission in ("COURT_NATION", "IMPROVE_RELATIONS"):
                    real_world = world()
                    if real_world.get_diplomatic_state("France", court) != "PEACE":
                        _set_state(real_world, "France", court, "PEACE")
                    forecast = D.forecast_mission_to_accept(
                        w, court, "open_borders", row["likelihood_score"], mission)
                    real = _dp_to_accept(real_world, mission, court, "open_borders")
                    assert forecast == (real[::-1] if real else None), (
                        court, relation, mission, forecast, real)
                    checked += 1
        assert checked >= 60, checked

    def test_the_relation_free_sum_is_exact_and_lever_gated(self):
        for relation in (-7, 0, 13, 25, 40):
            w = _europe()
            _set_rel(w, "France", "Prussia", relation)
            result = _score(w, _proposal(ptype="open_borders"))
            free = result["relation_free_score"]
            assert isinstance(free, int)
            assert result["score"] == int(round(free + D.acceptance_relation_term(relation,
                                                                                  False)))
            assert D.acceptance_relation_free_score(w, "Prussia", "open_borders") == free
        D.COUNSEL_NAMES_THE_COURT = False
        w = _europe()
        assert "relation_free_score" not in _score(w, _proposal(ptype="open_borders"))
        assert D.acceptance_relation_free_score(w, "Prussia", "open_borders") is None


class TestReviewTheCourtAtWar:
    """S0/S11: at war the favour is suspended (0), not lost — and the note
    said "stands at +10 and holds" beside "(now +0)"."""

    def _courted(self):
        w = _europe()
        assert _start_exec(w, "COURT_NATION", "Prussia")["success"]
        _fund_advance(w, 6)
        status = DD.mission_status(w)
        assert (status["remaining_kind"], status["favour_now"]) == ("holding", 10)
        assert status["remaining_note"] == _HOLD_NOTE
        return w

    @pytest.mark.parametrize("aggressor,victim", [("France", "Prussia"), ("Prussia", "France")])
    def test_at_war_every_surface_says_suspended(self, aggressor, victim):
        w = self._courted()
        with _quiet():
            result = D.declare_war(w, aggressor, victim)
        assert result.get("success"), result
        assert w.get_diplomatic_state("France", "Prussia") == "WAR"
        status = DD.mission_status(w)
        assert (status["remaining_kind"], status["remaining_turns"]) == ("suspended", -1)
        assert status["remaining_note"] == _WAR_NOTE
        assert status["favour_now"] == 0
        _fund_advance(w)
        assert DD.mission_is_live(w), "the war does not end his courting"
        status = DD.mission_status(w)
        assert status["remaining_note"] == _WAR_NOTE
        row = _row(w)
        assert row["details"]["beat"] == "running"
        assert row["message"] == (
            f"Relations with Prussia {status['current_relation']}, net "
            f"{status['net_per_turn']:+d} a turn. {_WAR_NOTE[:1].upper()}{_WAR_NOTE[1:]}. "
            "2 DP a turn.")
        assert "stands at +10" not in row["message"]
        with _quiet():
            assert L.build_cabinet(w)["remaining_note"] == _WAR_NOTE
        assert DL.build_diplomatic_ledger(w)["talleyrand"]["active_mission"][
            "remaining_note"] == _WAR_NOTE

    def test_the_favour_returns_at_the_peace(self):
        w = self._courted()
        with _quiet():
            assert D.declare_war(w, "France", "Prussia").get("success")
        _fund_advance(w)
        assert D.court_favour_mod(w, _proposal()) == 0
        _set_state(w, "France", "Prussia", "PEACE")
        assert D.court_favour_mod(w, _proposal()) == D.COURT_FAVOUR_CAP
        assert D.court_favour_mod(w, _proposal(ptype="non_aggression")) == D.COURT_FAVOUR_CAP
        status = DD.mission_status(w)
        assert (status["remaining_kind"], status["favour_now"]) == ("holding", 10)
        assert status["remaining_note"] == _HOLD_NOTE

    def test_at_the_alliance_the_note_says_recall(self):
        w = self._courted()
        _set_state(w, "France", "Prussia", "ALLIANCE")
        status = DD.mission_status(w)
        assert status["remaining_kind"] == "holding"
        assert status["remaining_note"] == (
            "the alliance is signed — his +10 has no treaty left to carry; recall him")


class TestReviewTheNetIsTheTick:
    """S2: the net read today's drift BEFORE the effect landed and ignored the
    clamp — "+8" inside the calm band where the tick leaves +7, and "+8" for a
    court holding at +100 where it leaves 0."""

    @pytest.mark.parametrize("mission_type,court,relation,turns,net", [
        ("IMPROVE_RELATIONS", "Prussia", 6, 0, 7),
        ("IMPROVE_RELATIONS", "Portugal", 6, 0, 7),
        ("IMPROVE_RELATIONS", "Ottoman", -11, 0, 8),
        ("IMPROVE_RELATIONS", "Prussia", 94, 0, 5),
        ("COURT_NATION", "Denmark", 100, 6, 0),
    ])
    def test_the_net_is_what_the_tick_leaves(self, mission_type, court, relation, turns, net):
        w = _europe()
        _set_rel(w, "France", court, relation)
        _stage(w, mission_type, court, turns_active=turns)
        status = DD.mission_status(w)
        assert status["effect_per_turn"] == 8, "the effect stays the tick's raw write"
        DD.restate_mission_notice(w)
        assert _row(w)["message"].startswith(
            f"Relations with {DD.mission_status(w)['target_display']} {relation}, "
            f"net {net:+d} a turn.")
        before = _rel(w, "France", court)
        _tick(w)
        assert _rel(w, "France", court) - before == status["net_per_turn"] == net

    @pytest.mark.parametrize("lever", [True, False])
    def test_the_morning_progress_reads_after_the_decay(self, lever):
        D.MISSION_PROGRESS_READS_AFTER_DRIFT = lever
        w = _europe()
        _set_rel(w, "France", "Prussia", 6)
        _stage(w, "IMPROVE_RELATIONS", "Prussia")
        w.pending_dispatch_events = []
        _tick(w)
        (event,) = [e for e in w.pending_dispatch_events
                    if e.get("type") == "diplomatic_mission_progress"]
        after = _rel(w, "France", "Prussia")
        assert after == 13
        assert event["template_vars"]["value"] == (after if lever else after + 1)


class TestReviewTheUndermineRoad:
    """S3/S4: the auto-downgrade steps ONE rung, so an ALLIANCE falls to a
    defensive alliance (still allied) and the count restarts — and the mission
    billed a turn after the break."""

    def test_the_note_states_the_ladder(self):
        w = _typed_world("UNDERMINE_ALLIANCE")
        w.turns_below_threshold[_key(w, "Austria", "Russia")] = 2
        first, second = _floor("ALLIANCE"), _floor("DEFENSIVE_ALLIANCE")
        assert DD.mission_status(w)["remaining_note"] == (
            f"their alliance falls to a defensive alliance after 5 turns at {first} or "
            f"below — now 60, 2 of 5 counted; breaking it needs a further 5 turns at "
            f"{second} or below")
        _set_state(w, "Austria", "Russia", "DEFENSIVE_ALLIANCE")
        assert DD.mission_status(w)["remaining_note"] == (
            f"their alliance breaks after 5 turns at {second} or below — now 60, "
            "2 of 5 counted")
        _set_state(w, "Austria", "Russia", "NON_AGGRESSION")
        status = DD.mission_status(w)
        assert (status["remaining_kind"], status["remaining_turns"]) == ("alliance", -1)
        assert status["remaining_note"] == "their alliance is broken — he reports home"

    def _drive(self):
        w = _europe()
        assert w.get_diplomatic_state("Austria", "Russia") == "ALLIANCE"
        _set_rel(w, "Austria", "Russia", 8)       # shortens the road; the ladder is the same
        assert _start_exec(w, "UNDERMINE_ALLIANCE", "Austria", "Russia")["success"]
        turns = []
        for _ in range(20):
            if not DD.mission_is_live(w):
                break
            state = w.diplomatic_states.get(_key(w, "Austria", "Russia"))
            note = DD.mission_status(w)["remaining_note"]
            _fund_advance(w)
            turns.append({"state": state, "note": note,
                          "allied": w.are_allies("Austria", "Russia"),
                          "live": DD.mission_is_live(w)})
        return w, turns

    @pytest.mark.parametrize("lever", [True, False])
    def test_the_real_road_ends_on_the_turn_of_the_break(self, lever):
        D.UNDERMINE_ENDS_ON_THE_BREAK = lever
        w, turns = self._drive()
        downs = [(e["from_state"], e["to_state"]) for e in w.event_log
                 if e.get("type") == "auto_downgrade"
                 and {e.get("nation_a"), e.get("nation_b")} == {"Austria", "Russia"}]
        assert downs == [("ALLIANCE", "DEFENSIVE_ALLIANCE"),
                         ("DEFENSIVE_ALLIANCE", "NON_AGGRESSION")]
        first, second = _floor("ALLIANCE"), _floor("DEFENSIVE_ALLIANCE")
        by_state = {t["state"] for t in turns}
        assert {"ALLIANCE", "DEFENSIVE_ALLIANCE"} <= by_state, turns
        for t in turns:
            if t["state"] == "ALLIANCE":
                assert t["note"].startswith(
                    f"their alliance falls to a defensive alliance after 5 turns at {first} "
                    "or below")
                assert t["note"].endswith(f"breaking it needs a further 5 turns at {second} "
                                          "or below")
            elif t["state"] == "DEFENSIVE_ALLIANCE":
                assert t["note"].startswith(f"their alliance breaks after 5 turns at {second} "
                                            "or below")
        tails = [t for t in turns if not t["allied"] and t["live"]]
        (ended,) = _ended(w)
        assert ended["reason"] == "alliance_broken"
        assert ended["relation_start"] == 8, "the pair's own baseline"
        if lever:
            assert tails == [], "he stayed a turn after the alliance broke"
            assert (ended["turns_active"], ended["dp_spent"]) == (10, 20)
        else:
            assert len(tails) == 1, turns
            assert (ended["turns_active"], ended["dp_spent"]) == (11, 22)
            assert turns[-1]["note"] == "their alliance is broken — he reports home"
        ta = w.active_diplomatic_mission["turns_active"]
        _fund_advance(w)
        assert w.active_diplomatic_mission["turns_active"] == ta, "billed after the end"
        assert len(_ended(w)) == 1
        before = _rel(w, "Austria", "Russia")
        assert before < -10
        charged, _ = _tick(w)
        assert charged == 0
        assert _rel(w, "Austria", "Russia") - before == 1, "drift alone — no -4"


def _decline_incoming(w):
    """An unanswered incoming proposal suppresses Talleyrand's whole report."""
    for _ in range(6):
        top = w.pending_diplomatic_dialogue
        if not top or top.get("type") != "incoming_proposal":
            return
        actions = [o.get("action") for o in top.get("options", [])]
        assert "reject_ai_proposal" in actions, actions
        with _quiet():
            CommandExecutor()._diplomatic.handle_diplomatic_dialogue_response(
                actions.index("reject_ai_proposal") + 1, {"world": w})


def _nudges(w, turns=8):
    fired = []
    for _ in range(turns):
        _advance(w)
        _decline_incoming(w)
        observations = DI._build_talleyrand_report(w, w.player_nation)
        if "idle_nudge" in [o.get("trigger_type") for o in observations]:
            fired.append(int(w.current_turn))
    return fired


class TestReviewTheIdleNudgeReadsTheLiveMission:
    """S5: a COMPLETED mission is kept as a record (MS-1), and the raw dict
    silenced the idle nudge for the rest of the campaign."""

    def _gathered(self):
        w = _europe()
        assert _start_exec(w, "GATHER_INTEL", "Denmark")["success"]
        _fund_advance(w, 3)
        assert w.active_diplomatic_mission.get("completed") is True
        assert not DD.mission_is_live(w) and w.talleyrand_state == "IDLE"
        return w

    def test_a_completed_record_does_not_silence_him(self):
        assert _nudges(_europe()), "vacuous: the nudge never fires on the shipped board"
        fired = _nudges(self._gathered())
        assert fired, "a completed record silenced the idle nudge"

    def test_lever_down_the_record_silences_him(self):
        DI.IDLE_NUDGE_READS_THE_LIVE_MISSION = False
        assert _nudges(self._gathered()) == []


class TestReviewTheUndermineRecord:
    """S6: the end record and the recall beat read France↔target — a relation
    an undermining never touches — instead of the pair he moved."""

    def test_a_typed_recall_logs_and_rings_the_pair(self, http):
        w, client = http
        france_britain = _rel(w, "France", "Britain")
        assert _start_exec(w, "UNDERMINE_ALLIANCE", "Britain", "Russia")["success"]
        start = int(w.active_diplomatic_mission["initial_pair_relation"])
        _fund_advance(w, 3)
        pair = _rel(w, "Britain", "Russia")
        assert pair < start, "vacuous: the pair never moved"
        assert _rel(w, "France", "Britain") == france_britain
        r = _cmd(client, "Talleyrand, cancel mission with Britain")
        assert r.get("success"), r.get("message")
        (row,) = _ended(w)
        assert (row["reason"], row["relation_start"], row["relation_end"]) == (
            "recalled", start, pair)
        assert _row(w)["message"] == (
            f"Talleyrand is recalled from Britain. Britain and Russia stand at {pair:+d} "
            f"(from {start:+d}).")

    def test_an_old_save_without_the_baseline_reads_todays_pair(self):
        w = _europe()
        _stage(w, "UNDERMINE_ALLIANCE", "Britain", target_ally="Russia")
        france_britain = w.active_diplomatic_mission["initial_relation"]
        assert "initial_pair_relation" not in w.active_diplomatic_mission
        _tick(w)
        _tick(w)
        pair = _rel(w, "Britain", "Russia")
        assert pair != france_britain
        with _quiet():
            assert CommandExecutor()._diplomatic._recall_mission(None, w)["success"]
        (row,) = _ended(w)
        assert (row["relation_start"], row["relation_end"]) == (pair, pair)


class TestReviewTheCourtedPairKeepsItsThaw:
    """S7: the exemption protects his gains from DECAY; it froze the thaw a
    hostile court would have had as well."""

    @pytest.mark.parametrize("lever", [True, False])
    @pytest.mark.parametrize("state,relation,thaw", [
        ("PEACE", -50, 1), ("ARMISTICE", -50, 3), ("PEACE", 60, 0), ("ARMISTICE", 60, 0),
    ])
    def test_the_courted_pair(self, lever, state, relation, thaw):
        D.COURT_EXEMPTION_KEEPS_THE_THAW = lever
        w = _europe()
        _set_state(w, "France", "Prussia", state)
        _set_rel(w, "France", "Prussia", relation)
        _stage(w, "COURT_NATION", "Prussia")
        step = thaw if lever else 0
        assert D.relation_drift_step(w, "France", "Prussia") == step
        with _quiet():
            D._process_relation_decay(w)
        assert _rel(w, "France", "Prussia") - relation == step

    @pytest.mark.parametrize("lever,net,end", [(True, 9, -23), (False, 8, -26)])
    def test_a_hostile_court_over_three_ticks(self, lever, net, end):
        D.COURT_EXEMPTION_KEEPS_THE_THAW = lever
        w = _europe()
        _set_rel(w, "France", "Prussia", -50)
        _stage(w, "COURT_NATION", "Prussia")
        assert DD.mission_status(w)["net_per_turn"] == net
        for _ in range(3):
            _tick(w)
        assert _rel(w, "France", "Prussia") == end


class TestReviewTheCounselStatesTheBlowback:
    """S8: the counsel's DP figures are the quiet-world forecast; COURT's
    blowback is not in them, so it is stated beside them."""

    def _previews(self):
        w = _europe()
        w.diplomatic_points = 10
        _set_rel(w, "France", "Denmark", 10)
        with _quiet():
            denmark = D.get_diplomatic_preview(w, "Denmark")
        w = _europe()
        w.diplomatic_points = 10
        with _quiet():
            prussia = D.get_diplomatic_preview(w, "Prussia")
        return denmark, prussia

    def test_at_the_shipped_chance_both_arms_say_it(self, monkeypatch):
        monkeypatch.setitem(DD.MISSION_EFFECTS["COURT_NATION"], "undermine_chance", 0.20)
        denmark, prussia = self._previews()
        assert denmark["recommended_mission"] == "COURT_NATION"
        assert denmark["recommendation"].endswith(
            "improving relations would take ≈2 turns and 2 DP." + _BLOWBACK)
        assert prussia["recommended_mission"] == "IMPROVE_RELATIONS"
        assert prussia["recommendation"].endswith("but 8 DP to 6." + _BLOWBACK)

    def test_with_no_blowback_it_is_absent(self):
        for preview in self._previews():
            assert "blowback" not in preview["recommendation"]
        assert D._court_blowback_sentence() == ""


def _betrayed(court, state, relation, severity):
    """Three live betrayal strikes France→court, no shared enemy: the
    hard-reject posture clamps every deep treaty to 0."""
    w = _europe()
    _set_state(w, "France", court, state)
    w.diplomatic_points = 10
    key = D._betrayal_key("France", court)
    w.betrayal_history = dict(getattr(w, "betrayal_history", {}) or {})
    record = dict(w.betrayal_history.get(key, {}) or {})
    record["strikes"] = [{"severity": severity, "turn": 1, "episode_id": f"iq4-review-{i}",
                          "decays_on_turn": int(w.current_turn) + 6 + i} for i in range(3)]
    w.betrayal_history[key] = record
    _set_rel(w, "France", court, relation)
    assert D.has_hard_reject_posture(w, "France", court)
    assert not D._shared_enemy_exists(w, "France", court)
    return w


class TestReviewTheCounselNamesThePosture:
    """S9: on a posture-clamped treaty the counsel said "Improve Relations"
    even at +100, where the mission completes on its first tick."""

    _HEAD = ("{name} will not bind itself to us after repeated betrayals — the "
             "grievance fades in 6 turns.")

    def _preview(self, w, court):
        with _quiet():
            return D.get_diplomatic_preview(w, court)

    def test_at_one_hundred_no_mission_is_prescribed(self):
        w = _betrayed("Prussia", "NON_AGGRESSION", 100, "major")
        row = {a["action"]: a for a in D.get_available_diplomatic_actions(w, "Prussia")}[
            "propose_defensive_alliance"]
        assert (row["available"], row["likelihood_score"]) == (True, 0), "the clamp"
        preview = self._preview(w, "Prussia")
        assert preview["recommendation"].startswith(self._HEAD.format(name="Prussia"))
        assert "Improve Relations" not in preview["recommendation"]
        assert not preview.get("recommended_mission")

    @pytest.mark.parametrize("relation,mission,tail", [
        (30, "IMPROVE_RELATIONS", " Talleyrand recommends: Improve Relations meanwhile, "
                                  "so the treaty carries when it does."),
        (100, "", " Relations already carry the treaty once it does — wait it out."),
    ])
    def test_improve_only_while_relations_would_still_fall_short(self, relation, mission,
                                                                  tail):
        w = _betrayed("Saxony", "NON_AGGRESSION", relation, "moderate")
        preview = self._preview(w, "Saxony")
        assert preview["recommendation"] == self._HEAD.format(name="Saxony") + tail
        assert (preview.get("recommended_mission") or "") == mission

    def test_lever_down_the_counsel_is_todays(self):
        D.COUNSEL_NAMES_THE_COURT = False
        preview = self._preview(_betrayed("Saxony", "NON_AGGRESSION", 100, "moderate"),
                                "Saxony")
        assert preview["recommendation"] == _IMPROVE_COUNSEL
        assert "recommended_mission" not in preview


class TestReviewTheCancelRowReadsTheCabinet:
    """S10: the wizard's Cancel row computed its own progress, and for an
    undermining read France's frozen standing with the target."""

    def _cancel(self, w, court):
        return {a["action"]: a for a in D.get_available_diplomatic_actions(w, court)}[
            "cancel_mission"]

    def _delta(self, text):
        m = re.search(r"\(([+-]?\d+)(?:,| over) (\d+) turns\)", text)
        assert m, text
        return int(m.group(1)), int(m.group(2))

    def test_undermine_reads_the_pair(self):
        w = _europe()
        france_britain = _rel(w, "France", "Britain")
        assert _start_exec(w, "UNDERMINE_ALLIANCE", "Britain", "Russia")["success"]
        _fund_advance(w, 3)
        status = DD.mission_status(w)
        assert status["relation_delta"] < 0, "vacuous: the pair never moved"
        row = self._cancel(w, "Britain")
        assert row["effect_text"].startswith("Britain–Russia: ")
        assert self._delta(row["effect_text"]) == (status["relation_delta"],
                                                   status["turns_active"])
        assert _rel(w, "France", "Britain") == france_britain

    def test_improve_is_unchanged(self):
        w = _europe()
        _set_rel(w, "France", "Prussia", 0)
        assert _start_exec(w, "IMPROVE_RELATIONS", "Prussia")["success"]
        _fund_advance(w, 3)
        status = DD.mission_status(w)
        row = self._cancel(w, "Prussia")
        assert row["display_name"] == "Cancel: Improve Relations"
        assert "–" not in row["effect_text"]
        assert re.fullmatch(r"\w+( → \w+)? \(\+\d+(,| over) \d+ turns\)", row["effect_text"]), \
            row["effect_text"]
        assert self._delta(row["effect_text"]) == (status["relation_delta"],
                                                   status["turns_active"])


class TestReviewABlowbackRowFalls:
    """L1: `refresh` keeps the max priority, so after one blowback a routine
    running row stayed HIGH for the rest of the mission."""

    def test_the_next_standing_turn_reissues_at_normal(self, monkeypatch):
        monkeypatch.setitem(DD.MISSION_EFFECTS["COURT_NATION"], "undermine_chance", 1.0)
        w = _europe()
        assert _start_exec(w, "COURT_NATION", "Prussia")["success"]
        _advance(w)
        hot = _row(w)
        assert hot["details"]["beat"] == "blowback"
        assert hot["priority"] == int(NotificationPriority.HIGH)
        monkeypatch.setitem(DD.MISSION_EFFECTS["COURT_NATION"], "undermine_chance", 0.0)
        _advance(w)
        cool = _row(w)
        assert cool["details"]["beat"] == "running"
        assert cool["priority"] == int(NotificationPriority.NORMAL)
        assert cool["id"] != hot["id"]
        _advance(w)
        assert _row(w)["id"] == cool["id"], "then it refreshes in place again"


class TestReviewTheChipEchoIsHumanised:
    """L2 (R7): the Recall buttons spell the court by its KEY (amendment 2),
    and the chip/rail echo printed it raw — "cancel mission with PapalStates"."""

    @pytest.mark.parametrize("func", ["_on_reward_command", "_on_naval_command"])
    def test_the_echo_line_humanises_the_command(self, func):
        code = _gd_code(SCRIPTS / "main.gd", func)
        echoes = [line for line in code.splitlines() if "add_output(" in line and "►" in line]
        assert echoes, "vacuous: the echo line moved"
        for line in echoes:
            assert "Utils.humanize_nation_keys_in_text(command)" in line, line
        assert not re.search(r'"\]► " \+ command\b', code)


class TestReviewTheHelpStatesTheRules:
    """L3: "(allies only)" — a defensive ally is not offered Reassure; and the
    drift sentence named neither the truce thaw nor the courted court."""

    def _block(self):
        return " ".join(ME._missions_help_block(_europe()).split())

    def test_reassure_is_a_full_alliance_only(self):
        block = self._block()
        assert "Reassure Ally - 1 DP a turn (a full alliance only)" in block
        assert "(allies only)" not in block

    def test_lever_down_reassure_is_allies_only(self):
        D.REASSURE_ONLY_AT_ALLIANCE = False
        assert "Reassure Ally - 1 DP a turn (allies only)" in self._block()

    def test_the_drift_sentence_names_the_truce_and_the_court(self):
        block = self._block()
        assert ("Relations drift 1 a turn toward the calm band (a truce thaws faster); "
                "the court he courts does not cool while he is there.") in block
        assert "beside any mission" not in block


class TestReviewTheTalleyrandTabReadsTheCabinet:
    """P4 (a): TALLEYRAND_TAB_READS_THE_CABINET had no pin at all — flipping it
    turned nothing red."""

    @pytest.mark.parametrize("mission_type", list(_TYPED))
    def test_up_the_tab_is_the_cabinet(self, mission_type):
        w = _typed_world(mission_type)
        status = DD.mission_status(w)
        tab = DL.build_diplomatic_ledger(w)["talleyrand"]
        for k in ("type_display", "net_per_turn", "remaining_note", "remaining_kind"):
            assert tab["active_mission"][k] == status[k], k
        assert "last_mission" not in tab

    def _gathered(self):
        w = _europe()
        _stage(w, "GATHER_INTEL", "Prussia")
        for _ in range(3):
            _tick(w)
        assert w.active_diplomatic_mission.get("completed")
        return w

    def test_up_an_idle_desk_names_the_last_mission(self):
        w = self._gathered()
        tab = DL.build_diplomatic_ledger(w)["talleyrand"]
        assert tab["active_mission"] is None
        record = L.last_mission_record(w)
        assert record["reason_phrase"].startswith("done — ")
        assert tab["last_mission"] == {"type_display": "Gathering Intel",
                                       "target_display": "Prussia",
                                       "reason_phrase": record["reason_phrase"]}

    def test_lever_down_the_keys_are_absent(self):
        DL.TALLEYRAND_TAB_READS_THE_CABINET = False
        active = DL.build_diplomatic_ledger(_typed_world("COURT_NATION"))["talleyrand"][
            "active_mission"]
        for k in ("type_display", "net_per_turn", "remaining_note", "remaining_kind"):
            assert k not in active, k
        assert "last_mission" not in DL.build_diplomatic_ledger(self._gathered())["talleyrand"]


class TestReviewCanDoNoMoreOnARealBoard:
    """P4 (f): the "relations can do no more" branch never fires at skill 10;
    its old pin fed a list the Cabinet never offers. At an authored skill of 5
    it fires on real rows: Britain at OPEN_BORDERS, relation 10, the pact."""

    def _world(self):
        w = _europe()
        w.diplomatic_points = 10
        w.diplomats["France"].skill = 5        # staged: an authored diplomat skill
        _set_state(w, "France", "Britain", "OPEN_BORDERS")
        _set_rel(w, "France", "Britain", 10)
        return w

    def test_the_branch_fires_on_real_rows(self):
        w = self._world()
        actions = D.get_available_diplomatic_actions(w, "Britain")
        rows = {a["action"]: a for a in actions}
        for action in ("mission_court", "mission_improve_relations", "propose_non_aggression"):
            assert rows[action]["available"], (action, rows[action].get("disabled_reason"))
        assert rows["propose_non_aggression"]["likelihood_score"] < D.ACCEPT_SCORE
        assert _dp_to_accept(self._world(), "IMPROVE_RELATIONS", "Britain",
                             "non_aggression") is None
        assert _dp_to_accept(self._world(), "COURT_NATION", "Britain",
                             "non_aggression") == (20, 10)
        out = D._recommendation_and_mission(w, "Britain", actions, 10, False, w.vassals)
        assert out == (_NO_MORE_BRITAIN, "COURT_NATION")

    def test_with_the_shipped_blowback_it_says_so(self, monkeypatch):
        monkeypatch.setitem(DD.MISSION_EFFECTS["COURT_NATION"], "undermine_chance", 0.20)
        w = self._world()
        actions = D.get_available_diplomatic_actions(w, "Britain")
        assert D._recommendation_and_mission(w, "Britain", actions, 10, False, w.vassals) == (
            _NO_MORE_BRITAIN + _BLOWBACK, "COURT_NATION")
