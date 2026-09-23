"""FA slice 17, part 0 — "The Remnant Holds No Ground" (FA-9 P1 + FA-63).

FA-9. Played exactly as Berthier's card counsels, the School of War lost
French homeland provinces to a 1,218-man RETREATING remnant. The chain,
reproduced at HEAD on the tutorial board: Kienmayer routs at Swabia; the W6-1
doctrine's tier-5 flight puts him on at-war French soil (the Bavarian wall
leaves him nothing else); the AI's P1 recovery rung then flees again, into
ungarrisoned Lorraine — and the PF-3 walk-in capture in
`movement_executor._execute_move` tested the PROVINCE (controller / war /
hidden defenders / fortification / garrison) and never the MOVER, so the
fleeing remnant annexed each province it fled through (seed `gamma`: Lorraine,
Rhineland, Orleanais, +2 in one phase; 28 -> 23). One rung earlier the AI's
P-1 capture-current was blind the same way: `_corps_is_limited` read
`retreated_this_turn`/`broken` and not the multi-turn `retreating` window.

⚠ What the row's own fix would have missed, and what this deliberately does
not touch: REPRO_L measured the WORSE case (seed `beta`, 28 -> 12) to be a
HEALTHY 7,655-man corps at morale 100 walking through 25 ungarrisoned
provinces. No predicate on the mover's state reaches it; it is the FA-D27
balance gate's question and is routed there, not forced into this row.

⚠ What REPRO_L's recommended fix would have broken: "extend `_corps_is_limited`
to the whole recovery window" also gates the LIMITER arm (stance/wait), which
runs BEFORE the P1 recovery flight — so every beaten AI corps would have stood
where its rout dropped it for three turns instead of walking to safety. ONE
predicate (`Marshal.in_retreat_recovery`) is read at the two CAPTURE seams;
the flight stays legal, and a pin below says so.

FA-63. The scenario's authored timing premise ("the split start delays the
combined-strength attack into the designed turn-8+ free-play window") is
FALSE and is pinned false: Charles attacks Senarmont at Munich in the turn-2
enemy phase through the real `/command` surface. Both filed mechanical remedies
were measured inert (a province east buys one turn; an authored `fortified`
is stripped by the AI inside turn 1), so the copy was corrected instead.

Series: `BASELINE_SERIES` and provinces byte-identical on all four flip arms
(0 / A / B / AB), with the reason MEASURED, not asserted — an instrumented
40-turn ambient run counted 33 recovering marshal-turns, 2 open walk-in
evaluations, 421 AI capture-rung evaluations and ZERO refusals at either seam:
on the open 1805 board a recovering corps flees to friendly soil; only the
School's Bavarian wall forces the tier-5 flight into France.
"""

import contextlib
import io
import json
import pathlib
import random
import re

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend import save_manager
from backend.ai import enemy_ai as EA
from backend.ai.enemy_ai import EnemyAI
from backend.commands import movement_executor as MV
from backend.commands.executor import CommandExecutor
from backend.commands.parser import CommandParser
from backend.models.marshal import Marshal, Stance
from backend.models.world_state import WorldState

REPO = pathlib.Path(__file__).resolve().parents[1]
MAPS = REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
TUTORIAL = str(MAPS / "tutorial_1805.json")
OVERLAY = REPO / "godot-client" / "project-sovereign" / "scripts" / "tutorial_overlay.gd"
SCRIPT_DOC = REPO / "docs" / "TUTORIAL_SCRIPT.md"


def _quiet(fn, *a, **k):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*a, **k)


def _tutorial():
    return _quiet(WorldState.from_scenario, TUTORIAL)


def _park(world, names, at="Vienna"):
    for m in world.marshals.values():
        if m.name in names:
            m.location = at


def _recovering(m: Marshal, strength=1218):
    m.strength = strength
    m.retreating = True
    m.retreat_recovery = 1
    m.broken = False
    m.retreated_this_turn = False
    m.stance = Stance.DEFENSIVE


def _refresh(world):
    world.invalidate_active_nations_cache()
    if hasattr(world, "_build_marshal_index"):
        world._build_marshal_index()
    _quiet(world.calculate_visibility)


# ═══════════════════════════════════════════════════════════════════════
# The predicate is the marshal's own
# ═══════════════════════════════════════════════════════════════════════

class TestThePredicateIsTheMarshalsOwn:

    def test_levers_default_on(self):
        assert MV.RECOVERING_CORPS_TAKES_NO_GROUND is True
        assert EA.RECOVERING_AI_CORPS_TAKES_NO_GROUND is True

    def test_in_retreat_recovery_reads_the_whole_window(self):
        w = _tutorial()
        k = w.get_marshal("Kienmayer")
        k.retreating, k.retreat_recovery = False, 0
        assert k.in_retreat_recovery() is False
        k.retreating, k.retreat_recovery = True, 0
        assert k.in_retreat_recovery() is True, "the flag alone is the window"
        k.retreating, k.retreat_recovery = False, 2
        assert k.in_retreat_recovery() is True, "a running stage alone is the window"

    def test_the_limiter_itself_was_not_widened(self):
        """The recovery FLIGHT must stay legal: `_corps_is_limited` gates the
        stance/wait limiter arm that runs BEFORE the P1 recovery rung."""
        w = _tutorial()
        k = w.get_marshal("Kienmayer")
        _recovering(k)
        assert EnemyAI._corps_is_limited(k) is False
        assert EnemyAI._corps_takes_no_ground(k) is True


# ═══════════════════════════════════════════════════════════════════════
# The shared walk-in seam (GR5 — both sides through the one executor)
# ═══════════════════════════════════════════════════════════════════════

class TestTheRecoveringCorpsHoldsNoGround:

    def _player_geometry(self):
        """Ney (France) at allied Franconia, recovering; Tyrol an EMPTY,
        unfortified, ungarrisoned Austrian province one march away."""
        w = _tutorial()
        ney = w.get_marshal("Ney")
        ney.location = "Franconia"
        _recovering(ney, strength=9000)
        _park(w, {"Jellacic", "ArchdukeCharles", "Schwarzenberg"}, at="Vienna")
        _park(w, {"Kienmayer"}, at="Hungary")
        tyrol = w.regions["Tyrol"]
        assert tyrol.controller == "Austria" and tyrol.garrison_strength == 0
        assert not tyrol.has_building("fortification")
        assert "Tyrol" in w.regions["Franconia"].adjacent_regions
        _refresh(w)
        ex = CommandExecutor()
        return w, ney, ex, {"world": w, "executor": ex}

    def test_a_retreating_player_corps_walks_on_and_takes_nothing(self):
        w, ney, ex, gs = self._player_geometry()
        r = _quiet(ex._movement._execute_move, ney, "Tyrol", w, gs)
        assert r["success"] is True, r
        assert ney.location == "Tyrol", "the MARCH stays legal"
        assert w.regions["Tyrol"].controller == "Austria", "…but the province is not taken"
        assert r.get("capture_refused_recovering") is True
        assert "still rallying from the rout" in r["message"], r["message"]
        assert not r.get("pending_capture_choice")

    def test_the_same_corps_whole_takes_the_province(self):
        """FALSIFIABLE CONTROL: the predicate reads the mover, not the map."""
        w, ney, ex, gs = self._player_geometry()
        ney.retreating, ney.retreat_recovery = False, 0
        r = _quiet(ex._movement._execute_move, ney, "Tyrol", w, gs)
        assert r["success"] is True
        assert w.regions["Tyrol"].controller == "France", r["message"]
        assert not r.get("capture_refused_recovering")
        assert "still rallying" not in r["message"]

    def test_the_lever_down_reproduces_the_annexation(self, monkeypatch):
        monkeypatch.setattr(MV, "RECOVERING_CORPS_TAKES_NO_GROUND", False)
        w, ney, ex, gs = self._player_geometry()
        r = _quiet(ex._movement._execute_move, ney, "Tyrol", w, gs)
        assert w.regions["Tyrol"].controller == "France", (
            "the defect: a corps in recovery annexed the province it fled onto")
        assert not r.get("capture_refused_recovering")

    def _ai_geometry(self):
        """REPRO_L's own case: Kienmayer at Franche-Comte, 1,218 men, in the
        recovery window; Lorraine French, garrison 0, no fort, no marshal."""
        w = _tutorial()
        k = w.get_marshal("Kienmayer")
        k.location = "Franche-Comte"
        _recovering(k)
        for m in w.marshals.values():
            if m.name != "Kienmayer" and m.location in ("Franche-Comte", "Lorraine", "Rhineland"):
                m.location = "Paris"
        _refresh(w)
        ex = CommandExecutor()
        return w, k, ex, {"world": w, "executor": ex}

    def test_the_ai_side_reads_the_same_predicate(self):
        w, k, ex, gs = self._ai_geometry()
        r = _quiet(ex._movement._execute_move, k, "Lorraine", w, gs)
        assert r["success"] is True
        assert k.location == "Lorraine"
        assert w.regions["Lorraine"].controller == "France", r["message"]
        assert r.get("capture_refused_recovering") is True
        # The player's sentence is the player's; the AI march says nothing extra.
        assert "still rallying" not in r["message"]

    def test_the_ai_lever_down_reproduces_the_row_verbatim(self, monkeypatch):
        monkeypatch.setattr(MV, "RECOVERING_CORPS_TAKES_NO_GROUND", False)
        w, k, ex, gs = self._ai_geometry()
        r = _quiet(ex._movement._execute_move, k, "Lorraine", w, gs)
        assert w.regions["Lorraine"].controller == "Austria"
        assert "Lorraine falls to Austria" in r["message"]


# ═══════════════════════════════════════════════════════════════════════
# The AI's capture rungs read the window; its flight does not
# ═══════════════════════════════════════════════════════════════════════

class TestTheAiCaptureRungsReadTheWindow:

    def _on_open_lorraine(self):
        """Kienmayer recovering ON ungarrisoned French Lorraine — the P-1
        capture-current case one step before the walk-in."""
        w = _tutorial()
        k = w.get_marshal("Kienmayer")
        k.location = "Lorraine"
        _recovering(k)
        for m in w.marshals.values():
            if m.name != "Kienmayer" and m.location in ("Franche-Comte", "Lorraine", "Rhineland"):
                m.location = "Paris"
        _refresh(w)
        return w, k

    def test_p_minus_1_refuses_a_recovering_corps(self):
        w, k = self._on_open_lorraine()
        action, _prio = _quiet(EnemyAI(CommandExecutor())._evaluate_marshal, k, "Austria", w)
        assert action is not None
        assert not (action.get("action") == "attack" and action.get("target") == "Lorraine"), action

    def test_a_stored_capture_intent_is_not_executed_by_a_recovering_corps(self):
        w, k = self._on_open_lorraine()
        ai = EnemyAI(CommandExecutor())
        ai._pending_intents["Kienmayer"] = {"intent": "capture", "target": "Lorraine"}
        action, _prio = _quiet(ai._evaluate_marshal, k, "Austria", w)
        assert not (action and action.get("action") == "attack"), action

    def test_a_whole_corps_still_captures_current(self):
        """FALSIFIABLE CONTROL for the rung."""
        w, k = self._on_open_lorraine()
        k.retreating, k.retreat_recovery = False, 0
        k.strength = 8000
        action, _prio = _quiet(EnemyAI(CommandExecutor())._evaluate_marshal, k, "Austria", w)
        assert action == {"marshal": "Kienmayer", "action": "attack", "target": "Lorraine"}, action

    def test_the_lever_down_lets_the_remnant_annex(self, monkeypatch):
        monkeypatch.setattr(EA, "RECOVERING_AI_CORPS_TAKES_NO_GROUND", False)
        w, k = self._on_open_lorraine()
        action, _prio = _quiet(EnemyAI(CommandExecutor())._evaluate_marshal, k, "Austria", w)
        assert action == {"marshal": "Kienmayer", "action": "attack", "target": "Lorraine"}, (
            "the defect: a 1,218-man recovering remnant annexed the province under it")

    def test_the_recovery_flight_itself_stays_legal(self):
        """The P1 recovery rung must still be REACHED: a recovering corps on
        its own soil with an enemy adjacent walks to a safe province."""
        w = _tutorial()
        k = w.get_marshal("Kienmayer")
        k.location = "Bohemia"                # Austrian soil
        _recovering(k, strength=3000)
        davout = w.get_marshal("Davout")
        davout.location = "Franconia"        # allied Bavaria, adjacent to Bohemia — the threat
        _park(w, {"ArchdukeCharles", "Schwarzenberg", "Jellacic"}, at="Hungary")
        _refresh(w)
        action, prio = _quiet(EnemyAI(CommandExecutor())._evaluate_marshal, k, "Austria", w)
        assert action is not None and action.get("action") == "move", (
            action, "the limiter must not swallow the recovery flight")
        assert prio == 1, "the P1 recovery rung, not the limiter arm"
        assert w.regions[action["target"]].controller == "Austria"


# ═══════════════════════════════════════════════════════════════════════
# FA-63 — the reserve is already on you
# ═══════════════════════════════════════════════════════════════════════

@pytest.fixture
def lesson_client(monkeypatch, tmp_path):
    monkeypatch.setenv("INK_IRON_SAVE_DIR", str(tmp_path / "saves"))
    monkeypatch.setattr(save_manager, "SAVE_DIR", tmp_path / "saves")
    world = _tutorial()
    monkeypatch.setattr(M, "world", world)
    monkeypatch.setattr(M, "game_state", {"world": world})
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    return TestClient(M.app), world


def _post(client, text):
    with contextlib.redirect_stdout(io.StringIO()):
        return client.post("/command", json={"command": text}).json()


class TestFa63TheReserveIsAlreadyOnYou:

    def test_charles_strikes_munich_in_the_turn_two_phase(self, lesson_client):
        """The lesson's own two opening turns, through the real surface."""
        client, w = lesson_client
        assert w.get_marshal("ArchdukeCharles").location == "Hungary"
        _post(client, "economy")
        r = _post(client, "Senarmont, move to Munich")
        assert r.get("success"), r.get("message")
        random.seed(10_001)
        _post(client, "end turn")
        r = _post(client, "Ney, defend")
        if r.get("objection") or r.get("pending_objection"):
            _post(client, "insist")
        random.seed(10_002)
        _post(client, "end turn")
        assert w.current_turn == 3
        battles = [(e.get("turn"),
                    (e.get("attacker") or {}).get("name") if isinstance(e.get("attacker"), dict) else e.get("attacker"),
                    (e.get("defender") or {}).get("name") if isinstance(e.get("defender"), dict) else e.get("defender"))
                   for e in list(w.event_log) if e.get("type") == "battle"]
        assert (2, "ArchdukeCharles", "Senarmont") in battles, (
            "the counter-blow the cards placed at turn 8+ lands in the turn-2 phase", battles)

    def test_the_scenario_comment_no_longer_claims_turn_eight(self):
        """⚠ The corrected comment QUOTES the false claim in order to retract
        it, so a bare "claim absent" pin reds on its own correction (this
        test's first cut did). The pin is about ASSERTION: the claim may
        appear once, and only under the retraction."""
        data = json.loads(pathlib.Path(TUTORIAL).read_text(encoding="utf-8"))
        comment = data["_comment"]
        assert "MEASURED FALSE" in comment
        assert comment.count("turn-8+") == 1, "the claim survives only as the quoted retraction"
        assert comment.index("turn-8+") < comment.index("MEASURED FALSE")
        assert "turn-2" in comment and "turn 3" in comment

    def test_the_script_table_says_the_reserve_is_on_you(self):
        doc = SCRIPT_DOC.read_text(encoding="utf-8")
        row_xii = [ln for ln in doc.splitlines() if ln.startswith("| 8+ |")]
        assert row_xii, "the beat table lost its row XII"
        assert "~T8-10" not in row_xii[0]
        assert "ALREADY on you" in row_xii[0]
        assert "FA-63" in doc

    def test_card_xiii_no_longer_promises_a_future_blow(self):
        src = OVERLAY.read_text(encoding="utf-8")
        # Sept 23, 2026: the School gained three cards and the numerals
        # moved (XIII → XV); the pin follows the TITLE, not the numeral.
        card = src[src.index('The Counter-Blow"'):]
        body = re.search(r'"body": "(.*?)",\n', card, re.S).group(1)
        assert "will come west" not in body
        assert "have been on you since the second morning" in body
