"""FA-26 / FA-N1 — "The Question Is Asked" (FA build slice 8, September 5, 2026).

The audit's highest-leverage row: the ES-7 erosion tick lowered a neglected
marshal's trust every turn and never consulted `check_redemption_threshold`,
so he bled 85 -> 0 over thirty turns with one terminal warning at <40 and no
question ever (measured before the fix on the 1805 boot: Lannes 23 -> 20 ->
17, `redemption_pending` False throughout, `world.pending_redemption` None).
FA-N1's census found three unchecked families in all — the tick, the attack's
failed-reinforcer -3, and jealousy's petition docks reached through
`/marshal_petition_response` — plus two small ones the per-turn net covers
(the confiscation -1, the diplomatic reactions clamped to +-5). The census's
fourth family, the strategic "proceed" -10, was a FALSE entry: that arm is
reachable only through `_handle_strategic_objection_from_endpoint`, which
zeroes the penalty it has already applied and runs its own final checker.

The fix: ONE helper, `disobedience.stage_redemption(world, marshal, result=,
events=)`, after every trust-LOWERING write, and ONE per-turn NET in
`_check_trust_warnings` that puts every player marshal at trust <= 20 to the
checker. Two flip levers (`REDEMPTION_AT_EVERY_TRUST_WRITE`,
`REDEMPTION_NET_ACTIVE`); zero new serialized fields — the latch, the
cooldown and `world.pending_redemption` already existed.

Every pin drives the real `/command` or `/marshal_petition_response` route on
the 1805 boot with a MOCK parser (the .env key would be billed per test) and
carries a lever-off arm that reproduces the pre-slice shape.
"""

import contextlib
import io
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.commands.disobedience as DO
import backend.game_logic.jealousy as J
import backend.main as M
from backend.commands.parser import CommandParser
from backend.game_logic import dotation as D
from backend.models.world_state import WorldState

ROOT = Path(__file__).resolve().parents[1]
SCENARIO = str(ROOT / "godot-client" / "project-sovereign" / "assets" / "maps"
               / "europe_1805.json")

LEVERS = [(DO, "REDEMPTION_AT_EVERY_TRUST_WRITE"), (DO, "REDEMPTION_NET_ACTIVE")]


@pytest.fixture(autouse=True)
def _levers_at_default():
    saved = [(mod, name, getattr(mod, name)) for mod, name in LEVERS]
    yield
    for mod, name, value in saved:
        setattr(mod, name, value)


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


@pytest.fixture
def board(monkeypatch):
    """The 1805 boot on the module-global seams the routes read, mock parser."""
    with _quiet():
        world = WorldState.from_scenario(SCENARIO)
    parser = CommandParser(use_real_llm=False)
    assert parser.llm.use_real_api is False
    monkeypatch.setattr(M, "world", world)
    monkeypatch.setattr(M, "parser", parser)
    monkeypatch.setitem(M.game_state, "world", world)
    return world


@pytest.fixture
def client():
    return TestClient(M.app)


def post(client, text):
    with _quiet():
        return client.post("/command", json={"command": text}).json()


def end_turn(client):
    return post(client, "end turn")


def levers(write, net):
    DO.REDEMPTION_AT_EVERY_TRUST_WRITE = write
    DO.REDEMPTION_NET_ACTIVE = net


def stage_erosion(world, name="Lannes", trust=23, wins=3):
    """FA-26's own reproduction geometry: expectation 120 (three victories),
    satisfaction 0 (no estate, no rente), grace elapsed. Boot turn 1 makes
    `turn - GRACE_TURNS` negative, which the tick reads as "no clock" and
    opens a fresh grace — so the board is advanced to turn 10 first."""
    m = world.marshals[name]
    m.battles_won = wins
    m.trust.set(trust)
    world.current_turn = 10
    m.expectation_grace_turn = int(world.current_turn) - D.GRACE_TURNS
    assert D.get_expectation(m) == 120
    assert D.get_satisfaction(m, world) == 0
    assert D.is_dotation_world(world)
    return m


def asked(response):
    return response.get("state") == "awaiting_redemption_choice" and bool(
        response.get("redemption_event"))


def redemption_rows(response):
    return [te for te in (response.get("tactical_events") or [])
            if isinstance(te, dict) and te.get("redemption_event")]


# ═══════════════════════════════════════════════════════════════════════════
# FA-26 — the erosion tick asks
# ═══════════════════════════════════════════════════════════════════════════

class TestTheErosionTickAsks:

    def test_lannes_is_asked_the_turn_he_crosses(self, board, client):
        lannes = stage_erosion(board)
        r = end_turn(client)
        assert lannes.trust.value == 20            # 23 - min(3, ceil(120/50))
        assert asked(r), r.get("state")
        assert r["redemption_event"]["marshal"] == "Lannes"
        assert lannes.redemption_pending is True
        assert board.pending_redemption is r["redemption_event"] or (
            board.pending_redemption["marshal"] == "Lannes")
        # the row rides the tactical list the end-turn hoist reads
        assert [te["redemption_event"]["marshal"] for te in redemption_rows(r)] == ["Lannes"]

    def test_levers_off_reproduce_the_measured_bleed(self, board, client):
        """The row's shape: 23 -> 20 -> 17 with no question anywhere."""
        levers(False, False)
        lannes = stage_erosion(board)
        r1 = end_turn(client)
        r2 = end_turn(client)
        assert (lannes.trust.value, lannes.redemption_pending) == (17, False)
        assert not asked(r1) and not asked(r2)
        assert board.pending_redemption is None
        assert redemption_rows(r1) == [] and redemption_rows(r2) == []

    def test_the_tick_stages_at_its_own_write_with_the_net_off(self, board, client):
        """Isolates seam 1: the net dark, the tick alone asks."""
        levers(True, False)
        lannes = stage_erosion(board)
        r = end_turn(client)
        assert lannes.trust.value == 20
        assert asked(r) and r["redemption_event"]["marshal"] == "Lannes"

    def test_the_question_is_not_asked_twice_while_it_stands(self, board, client):
        lannes = stage_erosion(board)
        r1 = end_turn(client)
        assert asked(r1)
        r2 = end_turn(client)
        # erosion continues (the question is owed, not a pardon) …
        assert lannes.trust.value == 17
        # … but the standing question is not minted again
        assert redemption_rows(r2) == []
        assert not asked(r2)
        assert board.pending_redemption["marshal"] == "Lannes"

    def test_the_tick_returns_its_events_as_a_list(self, board):
        stage_erosion(board)
        board.current_turn += 1
        with _quiet():
            events = board._process_dotation_state()
        assert isinstance(events, list) and len(events) == 1
        assert events[0]["type"] == "redemption_event"
        assert events[0]["redemption_event"]["marshal"] == "Lannes"
        # the same-turn idempotency guard answers with an EMPTY list
        with _quiet():
            assert board._process_dotation_state() == []

    def test_a_non_dotation_world_returns_an_empty_list(self):
        with _quiet():
            legacy = WorldState()
        assert not D.is_dotation_world(legacy)
        assert legacy._process_dotation_state() == []

    def test_an_eroding_ai_marshal_is_never_asked(self, board, client):
        """GR5: the erosion is symmetric, the question is the player's."""
        # 21, not 23: Mack's satisfaction is not zero (an AI court's own
        # ledger), so his erosion is 2 points a turn where Lannes's is 3
        mack = stage_erosion(board, name="Mack", trust=21)
        r = end_turn(client)
        assert mack.trust.value <= 20
        assert mack.redemption_pending is False
        assert not asked(r)
        assert board.pending_redemption is None


# ═══════════════════════════════════════════════════════════════════════════
# FA-N1 — the net
# ═══════════════════════════════════════════════════════════════════════════

class TestTheNet:

    def test_a_direct_write_is_asked_at_the_turn_boundary(self, board, client):
        murat = board.marshals["Murat"]
        murat.trust.modify(-90)          # bypasses every seam
        r = end_turn(client)
        assert asked(r) and r["redemption_event"]["marshal"] == "Murat"
        assert murat.redemption_pending is True
        assert [te["redemption_event"]["marshal"] for te in redemption_rows(r)] == ["Murat"]

    def test_net_off_leaves_a_direct_write_unasked(self, board, client):
        """Isolates the net's lever: the seams stay live, the census is dark."""
        levers(True, False)
        murat = board.marshals["Murat"]
        murat.trust.modify(-90)
        r = end_turn(client)
        assert murat.trust.value == 0 and murat.redemption_pending is False
        assert not asked(r) and board.pending_redemption is None

    def test_two_men_cross_in_one_tick_exactly_one_question(self, board, client):
        board.marshals["Murat"].trust.set(15)
        board.marshals["Soult"].trust.set(12)
        r = end_turn(client)
        rows = redemption_rows(r)
        assert len(rows) == 1
        first = rows[0]["redemption_event"]["marshal"]
        assert first in ("Murat", "Soult")
        assert asked(r) and r["redemption_event"]["marshal"] == first
        latched = [n for n in ("Murat", "Soult")
                   if board.marshals[n].redemption_pending]
        assert latched == [first]

    def test_the_second_man_asks_once_the_first_is_answered(self, board, client):
        board.marshals["Murat"].trust.set(15)
        board.marshals["Soult"].trust.set(12)
        r1 = end_turn(client)
        first = r1["redemption_event"]["marshal"]
        second = "Soult" if first == "Murat" else "Murat"
        with _quiet():
            answer = client.post("/respond_to_redemption",
                                 json={"choice": "grant_autonomy"}).json()
        assert answer.get("success", True)
        assert board.pending_redemption is None
        # The granted man now acts on his own at end turn — the AI's choice,
        # with battle randomness that can put a CAPTURE question on the same
        # response (a legitimate two-question turn, slice 6's business, not
        # this pin's). Stand him down; his cooldown is what the pin needs.
        board.marshals[first].autonomous = False
        r2 = end_turn(client)
        assert asked(r2) and r2["redemption_event"]["marshal"] == second
        assert board.marshals[second].redemption_pending is True

    def test_an_ai_marshal_at_ten_is_never_asked(self, board, client):
        mack = board.marshals["Mack"]
        mack.trust.set(10)
        r = end_turn(client)
        assert mack.redemption_pending is False
        assert not asked(r) and board.pending_redemption is None

    def test_the_net_honours_the_cooldown_after_an_answer(self, board, client):
        murat = board.marshals["Murat"]
        murat.trust.set(15)
        end_turn(client)
        with _quiet():
            client.post("/respond_to_redemption", json={"choice": "grant_autonomy"})
        assert board.pending_redemption is None
        murat.autonomous = False         # stand him down (see the pin above);
        murat.trust.set(10)              # still at the threshold, still ours
        assert board.current_turn < murat.redemption_cooldown_until
        r = end_turn(client)
        # the checker's own cooldown refuses a second question for the same man
        assert not asked(r)
        assert redemption_rows(r) == []


# ═══════════════════════════════════════════════════════════════════════════
# FA-N1 — jealousy's docks, at the petition endpoint
# ═══════════════════════════════════════════════════════════════════════════

def _stub_petition(delta, name="Ney"):
    def _stub(world, choice, executor=None, game_state=None):
        world.marshals[name].modify_trust(delta)
        world.pending_marshal_petition = None
        return {"success": True, "message": f"{name} answers the petition."}
    return _stub


class TestThePetitionEndpointAsks:

    def _petition(self, board):
        board.pending_marshal_petition = {
            "kind": "jealousy_confrontation",
            "options": [{"id": "rebuke"}],
            "context": {"marshal": "Ney"},
        }

    def test_a_rebuke_that_crosses_twenty_asks(self, board, client, monkeypatch):
        ney = board.marshals["Ney"]
        ney.trust.set(24)
        self._petition(board)
        monkeypatch.setattr(J, "handle_petition_response", _stub_petition(-5))
        with _quiet():
            r = client.post("/marshal_petition_response",
                            json={"choice": "rebuke"}).json()
        assert ney.trust.value == 19
        assert asked(r) and r["redemption_event"]["marshal"] == "Ney"
        assert ney.redemption_pending is True
        assert board.pending_redemption["marshal"] == "Ney"

    def test_lever_off_the_rebuke_is_silent(self, board, client, monkeypatch):
        levers(False, False)
        ney = board.marshals["Ney"]
        ney.trust.set(24)
        self._petition(board)
        monkeypatch.setattr(J, "handle_petition_response", _stub_petition(-5))
        with _quiet():
            r = client.post("/marshal_petition_response",
                            json={"choice": "rebuke"}).json()
        assert ney.trust.value == 19
        assert not asked(r) and ney.redemption_pending is False
        assert board.pending_redemption is None

    def test_a_petition_that_lowers_no_one_asks_nothing(self, board, client, monkeypatch):
        self._petition(board)
        monkeypatch.setattr(J, "handle_petition_response", _stub_petition(+3))
        with _quiet():
            r = client.post("/marshal_petition_response",
                            json={"choice": "rebuke"}).json()
        assert not asked(r)
        assert not any(m.redemption_pending for m in board.marshals.values())

    def test_the_bystander_the_dock_touched_is_asked_too(self, board, client, monkeypatch):
        """The docks lower trust on men BESIDE the petitioner (rivalry, the
        Fontainebleau refusal); the endpoint puts every player marshal to the
        checker, not only the one the context names."""
        davout = board.marshals["Davout"]
        davout.trust.set(21)
        self._petition(board)
        monkeypatch.setattr(J, "handle_petition_response", _stub_petition(-2, name="Davout"))
        with _quiet():
            r = client.post("/marshal_petition_response",
                            json={"choice": "rebuke"}).json()
        assert davout.trust.value == 19
        assert asked(r) and r["redemption_event"]["marshal"] == "Davout"

    def test_the_petition_result_still_reaches_the_client(self, board, client, monkeypatch):
        """The staging must not eat the petition's own message."""
        ney = board.marshals["Ney"]
        ney.trust.set(24)
        self._petition(board)
        monkeypatch.setattr(J, "handle_petition_response", _stub_petition(-5))
        with _quiet():
            r = client.post("/marshal_petition_response",
                            json={"choice": "rebuke"}).json()
        assert "answers the petition" in (r.get("message") or "")
        assert r.get("success") is True


# ═══════════════════════════════════════════════════════════════════════════
# FA-N1 — the attack's failed reinforcer
# ═══════════════════════════════════════════════════════════════════════════

def _no_show(name):
    return [{"marshal": name, "arrived": False, "reason": "low_score",
             "score": 0, "threshold": 50, "strength": 0,
             "message": f"{name} does not march."}]


class TestTheFailedReinforcerAsks:

    def _battle(self, board, client, monkeypatch, reinforcer="Lannes"):
        combat = M.executor._combat
        monkeypatch.setattr(combat, "_calculate_reinforcements",
                            lambda primary, defender, region, nation, world: (
                                _no_show(reinforcer) if nation == board.player_nation else []))
        return post(client, "Ney, attack Mack")

    def test_a_no_show_that_crosses_twenty_is_asked_on_the_battle(self, board, client, monkeypatch):
        lannes = board.marshals["Lannes"]
        lannes.trust.set(22)
        r = self._battle(board, client, monkeypatch)
        assert r.get("battle_report") or "attack" in (r.get("message") or "").lower()
        assert lannes.trust.value == 19, r.get("message")
        assert asked(r) and r["redemption_event"]["marshal"] == "Lannes"
        assert lannes.redemption_pending is True

    def test_lever_off_the_no_show_is_docked_in_silence(self, board, client, monkeypatch):
        levers(False, False)
        lannes = board.marshals["Lannes"]
        lannes.trust.set(22)
        r = self._battle(board, client, monkeypatch)
        assert lannes.trust.value == 19
        assert not asked(r) and lannes.redemption_pending is False

    def test_a_no_show_above_the_threshold_asks_nothing(self, board, client, monkeypatch):
        lannes = board.marshals["Lannes"]
        lannes.trust.set(60)
        r = self._battle(board, client, monkeypatch)
        assert lannes.trust.value == 57
        assert not asked(r)


# ═══════════════════════════════════════════════════════════════════════════
# the rider — the turn after a grant of autonomy serializes
# ═══════════════════════════════════════════════════════════════════════════

class TestTheTurnAfterAutonomySerializes:
    """Found by this slice's own pins: answering the question with
    `grant_autonomy` and ending the next turn returned HTTP 500 — the
    independent-command report embedded the autonomous man's whole executor
    result, `new_state` (the live WorldState) included, and the JSON encoder
    died on a tuple-keyed map inside it, the world already advanced.
    Reproduced on the committed pre-slice tree (2c451162) with the question
    staged by hand: grant_autonomy 200, next `end turn` 500. Pre-existing;
    FA-26's question made it reachable in ordinary play. No lever — a
    serialization repair, not a behaviour change."""

    def test_the_next_end_turn_answers_200_while_the_man_acts(self, board, client):
        soult = board.marshals["Soult"]
        soult.trust.set(12)
        end_turn(client)
        assert board.pending_redemption["marshal"] == "Soult"
        with _quiet():
            ans = client.post("/respond_to_redemption", json={"choice": "grant_autonomy"})
        assert ans.status_code == 200 and soult.autonomous is True
        with _quiet():
            resp = client.post("/command", json={"command": "end turn"})
        assert resp.status_code == 200          # raise_server_exceptions is on: a 500 raises
        body = resp.json()
        report = body.get("independent_command_report") or []
        assert report and report[0]["marshal"] == "Soult"
        assert all("new_state" not in (entry.get("result") or {}) for entry in report)

    def test_the_report_builder_strips_the_world(self, board):
        from backend.game_logic.turn_manager import TurnManager
        soult = board.marshals["Soult"]
        soult.autonomous = True
        soult.autonomy_turns = 3
        tm = TurnManager(board)
        with _quiet():
            out = tm._process_autonomous_marshals({"world": board})
        entries = [e for e in out["independent_command_report"] if e["marshal"] == "Soult"]
        assert entries
        assert "new_state" not in entries[0]["result"]
        # and the original executor result is untouched — the copy, not the source, was stripped
        import json
        json.dumps(entries[0]["result"], default=str)


# ═══════════════════════════════════════════════════════════════════════════
# the helper itself
# ═══════════════════════════════════════════════════════════════════════════

class TestTheHelper:

    def test_result_and_events_both_carry_the_question(self, board):
        murat = board.marshals["Murat"]
        murat.trust.set(10)
        result, events = {}, []
        ev = DO.stage_redemption(board, murat, result=result, events=events)
        assert ev and ev["marshal"] == "Murat"
        assert result["redemption_event"] is ev
        assert result["state"] == "awaiting_redemption_choice"
        assert events == [{"type": "redemption_event", "redemption_event": ev}]
        assert board.pending_redemption is ev

    def test_a_question_already_riding_the_result_is_kept(self, board):
        murat, soult = board.marshals["Murat"], board.marshals["Soult"]
        murat.trust.set(10)
        soult.trust.set(10)
        result = {}
        first = DO.stage_redemption(board, murat, result=result)
        assert first["marshal"] == "Murat"
        # a second man while the first stands: the checker refuses him …
        assert DO.stage_redemption(board, soult, result=result) is None
        assert result["redemption_event"] is first
        assert soult.redemption_pending is False

    def test_a_foreign_question_on_the_result_is_kept(self, board):
        """Isolation pin: in production the checker's one-live-question rule
        means a dict already carrying a question is never handed a second
        event (the mutation sweep found the guard unreachable through the
        routes). The guard is kept as defence in depth for a producer that
        carries an event without latching, and pinned here by construction."""
        murat = board.marshals["Murat"]
        murat.trust.set(10)
        foreign = {"marshal": "Ghost", "type": "redemption"}
        result = {"redemption_event": foreign, "state": "awaiting_redemption_choice"}
        assert board.pending_redemption is None       # no standing question
        ev = DO.stage_redemption(board, murat, result=result)
        assert ev and ev["marshal"] == "Murat"        # Murat IS asked (latched, world field)
        assert result["redemption_event"] is foreign  # … but the dict keeps what it carried
        assert board.pending_redemption is ev

    def test_above_the_threshold_nothing_is_staged(self, board):
        ney = board.marshals["Ney"]
        ney.trust.set(21)
        result, events = {}, []
        assert DO.stage_redemption(board, ney, result=result, events=events) is None
        assert result == {} and events == []

    def test_lever_off_the_helper_is_inert(self, board):
        levers(False, True)
        murat = board.marshals["Murat"]
        murat.trust.set(10)
        result = {}
        assert DO.stage_redemption(board, murat, result=result) is None
        assert result == {} and murat.redemption_pending is False

    def test_no_world_no_marshal_no_system(self, board):
        murat = board.marshals["Murat"]
        murat.trust.set(10)
        assert DO.stage_redemption(None, murat) is None
        assert DO.stage_redemption(board, None) is None

        class Bare:
            pass
        assert DO.stage_redemption(Bare(), murat) is None


# ═══════════════════════════════════════════════════════════════════════════
# the census — the seams are where the record says they are
# ═══════════════════════════════════════════════════════════════════════════

def _src(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


class TestTheCensus:

    def test_the_tick_stages_beside_its_write(self):
        src = _src("backend/models/world_state.py")
        i = src.index("marshal.modify_trust(-points)")
        window = src[i:i + 500]
        assert "stage_redemption(self, marshal, events=events)" in window

    def test_the_failed_reinforcer_stages_beside_its_write(self):
        src = _src("backend/commands/combat_executor.py")
        i = src.index("failing.trust.modify(-3)")
        window = src[i:i + 500]
        assert "stage_redemption(world, failing, result=result)" in window

    def test_the_petition_endpoint_stages_and_surfaces(self):
        src = _src("backend/main.py")
        i = src.index("result = handle_petition_response(")
        window = src[i:i + 1600]
        assert "for _petitioned in world.get_player_marshals():" in window
        assert "stage_redemption(world, _petitioned, result=result)" in window

    def test_the_net_is_in_the_per_turn_sweep(self):
        src = _src("backend/models/world_state.py")
        i = src.index("def _check_trust_warnings")
        j = src.index("def _check_cavalry_limits", i)
        body = src[i:j]
        assert "REDEMPTION_NET_ACTIVE" in body
        assert "stage_redemption(self, marshal, events=warnings)" in body

    def test_the_strategic_proceed_arm_is_covered_one_frame_up(self):
        """The FA-N1 census listed the strategic 'proceed' -10 as unchecked.
        It is not: the arm is reached only through the endpoint handler,
        which zeroes the penalty it applied for every MODERATE+ objection
        and runs the checker at its own return. Pinned so the record's
        correction stays true."""
        src = _src("backend/commands/strategic_executor.py")
        i = src.index("def _handle_strategic_objection_from_endpoint")
        j = src.find("\n    def ", i + 1)
        end = j if j > 0 else len(src)      # the handler is the class's last method
        body = src[i:end]
        assert 'original_command["v2_insist_penalty"] = 0' in body
        assert re.search(r"check_redemption_threshold\(marshal, world\)", body)
        # and nothing outside that handler enters the post-objection branch
        # (the L2 "preferred" re-dispatch at the handler's sibling is a dict
        # literal, not an assignment, and never carries "proceed")
        sites = [m.start() for m in re.finditer(r'\["objection_response"\] = ', src)]
        assert len(sites) == 2 and all(i <= s < end for s in sites), sites
