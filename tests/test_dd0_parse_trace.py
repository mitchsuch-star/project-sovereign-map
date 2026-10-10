"""DD-0 S3 "The Command Road" — instrument 1, THE PARSE TRACE (October 10,
2026; PRE_DEPLOY_PLAN.md §3.0; rules SYSTEMS_REFERENCE.md §100).

Every stage that reads or rewrites a typed line appends a row to a trace
opened at `POST /command`'s door and closed by `build_base_response` on
whatever reply goes out. The rows ride the response under `parse_trace`
when the request asks (`trace: true`) or the environment does
(SOVEREIGN_PARSE_TRACE); the typed `why` prints the LAST line's trace,
free, without the flag.

Pinned here:
  - the trace costs nothing outside a request (a direct `parser.parse`
    records no row and raises nothing);
  - a set of lines spanning every stage family, driven through the real
    `POST /command`, each carry a trace whose FIRST row is the typed line
    and whose LAST row is the ONE terminal `reply` row (done / refused /
    asked) — "the trace on every response";
  - the stage each family must show (a typo repair, a split, a carryover,
    a premise, a guard refusal, a strategic order and the SFR-D11 relative
    place, a question, an auto-assigned scout, the recruit arm's
    substitution — SFR-D41's class, now DISCLOSED on the trace);
  - `why` prints the previous line's trace and costs nothing; `why` twice
    prints the same order; `why` with a subject is the state desk's;
  - the key is absent without the flag; the env flag puts it on.
"""
from __future__ import annotations

import contextlib
import io
import os
import tempfile

import pytest

from backend.ai import parse_trace


# ── the module alone ─────────────────────────────────────────────────────

class TestTheModule:
    def test_no_trace_open_is_a_no_op(self):
        assert parse_trace.current() is None
        parse_trace.note("x", "y", "a", "b")
        parse_trace.decide("x", "y", "z")
        assert parse_trace.rows() == []
        assert parse_trace.close_trace() is None

    def test_note_records_only_a_change_and_derives_the_span(self):
        parse_trace.open_trace("the line")
        try:
            parse_trace.note("parser", "inert", "same", "same")
            parse_trace.note("parser", "changed", "Ney, hodl Lorraine", "Ney, hold Lorraine")
            rows = parse_trace.rows()
            assert [r["rule"] for r in rows] == ["line", "changed"]
            assert rows[1]["span"] == [7, 9]
            assert rows[1]["before"] == "Ney, hodl Lorraine"
        finally:
            parse_trace.close_trace()
        assert parse_trace.current() is None

    def test_values_are_clipped_on_the_wire(self):
        parse_trace.open_trace()
        try:
            parse_trace.decide("s", "r", "x" * 1000)
            assert len(parse_trace.rows()[0]["detail"]) == parse_trace.MAX_VALUE_CHARS
        finally:
            parse_trace.close_trace()

    def test_fmt_is_one_line_per_row(self):
        text = parse_trace.fmt([
            {"stage": "typed", "rule": "line", "detail": "hold"},
            {"stage": "parser", "rule": "split", "before": "a, then b", "after": "a"},
        ], line="hold")
        lines = text.splitlines()
        assert lines[0] == "You typed: 'hold'"
        assert lines[1] == "typed · line · 'hold'"
        assert lines[2] == "parser · split · 'a, then b' → 'a'"

    def test_wanted_reads_the_request_flag_or_the_env(self, monkeypatch):
        monkeypatch.delenv(parse_trace.ENV_FLAG, raising=False)
        assert parse_trace.wanted(False) is False
        assert parse_trace.wanted(True) is True
        monkeypatch.setenv(parse_trace.ENV_FLAG, "1")
        assert parse_trace.wanted(False) is True

    def test_a_direct_parse_records_nothing(self):
        """The driver and every direct-parse test pay one None check per
        stage and get no row."""
        from backend.ai import parser_eval as pe
        from backend.commands.parser import CommandParser
        with contextlib.redirect_stdout(io.StringIO()):
            world = pe.build_world("legacy")
            gs = pe.build_llm_game_state(world)
            parser = CommandParser(use_real_llm=False)
            parser.parse("Ney, hodl Lorraine", gs, world=world)
        assert parse_trace.current() is None
        assert parse_trace.rows() == []

    def test_last_parse_trace_is_a_transient_private_field(self):
        """Never serialized: the serialization gate's R1 exempts a private
        name automatically, and `_last_parse_trace` is one."""
        from backend.models.world_state import WorldState
        world = WorldState(player_nation="France")
        world._last_parse_trace = {"line": "x", "rows": []}
        assert "_last_parse_trace" not in world.to_dict()
        assert "last_parse_trace" not in world.to_dict()


# ── the real road ────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def client():
    """The real road on the 1805 boot board. The suite pins
    `SOVEREIGN_SCENARIO=none` (the bare world), so the board is swapped in
    by hand — all three handles together (`main.world`,
    `main.game_state["world"]`, `main.parser`), the project's idiom — and
    restored at the module's end."""
    os.environ["LLM_MODE"] = "mock"
    os.environ.setdefault("INK_IRON_SAVE_DIR", tempfile.mkdtemp(prefix="dd0_trace_"))
    from fastapi.testclient import TestClient
    with contextlib.redirect_stdout(io.StringIO()):
        import backend.main as M
        c = TestClient(M.app)
    originals = (M.game_state["world"], M.world, M.parser)
    try:
        yield c, M
    finally:
        M.game_state["world"], M.world, M.parser = originals


def _fresh(M):
    from backend.ai import parser_eval as pe
    from backend.commands.parser import CommandParser
    with contextlib.redirect_stdout(io.StringIO()):
        world = pe.build_world("1805")
        M.game_state["world"] = world
        M.world = world
        M.parser = CommandParser(use_real_llm=False)


def _post(client, line, **extra):
    c, _ = client
    with contextlib.redirect_stdout(io.StringIO()):
        r = c.post("/command", json={"command": line, **extra})
    return r.json()


def _rules(trace, stage):
    return [r["rule"] for r in trace if r["stage"] == stage]


# Each line names the stage · rule the trace MUST show for it.
THE_FAMILIES = [
    ("Ney, attack Mack", ("dispatch", "attack")),
    ("Ney, hodl Lorraine", ("parser", "repair_leading_verb_typo")),
    ("Davout, march to Swabia, then hold", ("parser", "split")),
    ("Ney, do not attack Mack", ("guards", "refusal")),
    ("Davout, march to Swabia", ("strategic", "detected")),
    ("Soult, march home to Franche-Comte", ("strategic", "province_named_after_relative")),
    ("where is Mack?", ("parser", "is_question")),
    ("scout Swabia", ("executor", "auto_assign_scout")),
    ("Murat, recruit infantry", ("executor", "recruit_arm_substituted")),
    ("Lannes, if Mack is still in Swabia, attack him", ("premise", "split_premise")),
]


class TestTheTraceOnEveryResponse:
    @pytest.mark.parametrize("line,must", THE_FAMILIES, ids=[f[0] for f in THE_FAMILIES])
    def test_the_line_carries_its_stage_and_ends_on_the_reply(self, client, line, must):
        _, M = client
        _fresh(M)
        reply = _post(client, line, trace=True)
        trace = reply.get("parse_trace")
        assert trace, f"no trace on {line!r}"
        assert trace[0] == {"stage": "typed", "rule": "line", "detail": line}
        assert trace[-1]["stage"] == parse_trace.TERMINAL_STAGE
        assert trace[-1]["rule"] in ("done", "refused", "asked")
        stage, rule = must
        assert rule in _rules(trace, stage), (
            f"{line!r}: expected {stage}·{rule} in " + ", ".join(
                f"{r['stage']}·{r['rule']}" for r in trace))
        # the parse row is on every parsed line
        assert "result" in _rules(trace, "parse") or "refused" in _rules(trace, "premise")

    def test_the_premise_row_follows_the_carryover_rewrite(self, client):
        """The road's ORDER is on the trace: carryover (`him` → Mack) runs
        before the premise split, which runs before the parse."""
        _, M = client
        _fresh(M)
        _post(client, "Ney, attack Mack")  # the history CR-4's `him` resolves against
        trace = _post(client, "Lannes, if Mack is still in Swabia, attack him",
                      trace=True)["parse_trace"]
        stages = [r["stage"] for r in trace]
        assert "carryover" in stages, stages
        assert stages.index("carryover") < stages.index("premise")

    def test_the_recruit_arm_substitution_is_disclosed(self, client):
        """SFR-D41's class: cavalry asked and infantry paid (or the reverse)
        is now a row the player can ask for."""
        _, M = client
        _fresh(M)
        trace = _post(client, "Murat, recruit infantry", trace=True)["parse_trace"]
        row = next(r for r in trace if r["rule"] == "recruit_arm_substituted")
        assert row["before"] == "infantry" and row["after"] == "cavalry"
        assert row["marshal"] == "Murat"

    def test_the_relative_place_row_names_sfr_d11s_seam(self, client):
        _, M = client
        _fresh(M)
        trace = _post(client, "Soult, march home to Franche-Comte", trace=True)["parse_trace"]
        row = next(r for r in trace if r["rule"] == "province_named_after_relative")
        assert row["before"] == "home" and row["after"] == "Franche-Comte"

    def test_the_key_is_absent_without_the_flag(self, client, monkeypatch):
        _, M = client
        monkeypatch.delenv(parse_trace.ENV_FLAG, raising=False)
        _fresh(M)
        reply = _post(client, "Ney, attack Mack")
        assert "parse_trace" not in reply
        assert reply.get("success") is True

    def test_the_env_flag_puts_it_on(self, client, monkeypatch):
        _, M = client
        monkeypatch.setenv(parse_trace.ENV_FLAG, "1")
        _fresh(M)
        reply = _post(client, "Ney, attack Mack")
        assert reply["parse_trace"][-1]["stage"] == "reply"

    def test_a_refusal_road_ends_on_a_refused_reply(self, client):
        _, M = client
        _fresh(M)
        trace = _post(client, "Ney, do not attack Mack", trace=True)["parse_trace"]
        assert trace[-1]["rule"] == "refused"
        assert trace[-1]["detail"].get("refusal") == "negation" or any(
            r["rule"] == "refusal" and r["detail"].get("kind") == "negation" for r in trace)


class TestTheTypedWhy:
    def test_why_prints_the_last_lines_trace_and_costs_nothing(self, client):
        _, M = client
        _fresh(M)
        _post(client, "Ney, attack Mack")
        before = int(M.world.actions_remaining)
        reply = _post(client, "why")
        assert reply["success"] is True
        assert reply.get("parse_trace_explained") is True
        msg = reply["message"]
        assert msg.startswith("How the last line was read:")
        assert "You typed: 'Ney, attack Mack'" in msg
        assert "dispatch · attack" in msg
        assert int(M.world.actions_remaining) == before
        assert reply["action_info"]["cost"] == 0

    def test_why_twice_prints_the_same_order(self, client):
        _, M = client
        _fresh(M)
        _post(client, "scout Swabia")
        first = _post(client, "why?")["message"]
        second = _post(client, "explain")["message"]
        assert first == second
        assert "You typed: 'scout Swabia'" in second

    def test_why_before_any_order_says_so(self, client):
        _, M = client
        _fresh(M)
        reply = _post(client, "why")
        assert reply["success"] is True
        assert "give an order first" in reply["message"]

    def test_why_is_not_in_the_history(self, client):
        _, M = client
        _fresh(M)
        _post(client, "Ney, attack Mack")
        n = len(M.world.command_history)
        _post(client, "why")
        assert len(M.world.command_history) == n

    def test_why_with_a_subject_is_the_desks(self, client):
        """`why is Prussia at war` carries a subject: never this road."""
        _, M = client
        _fresh(M)
        _post(client, "Ney, attack Mack")
        reply = _post(client, "why is Prussia at war with us?")
        assert reply.get("parse_trace_explained") is None
        assert not str(reply["message"]).startswith("How the last line was read:")

    def test_the_why_forms(self):
        from backend.main import _WHY_RX
        for line in ("why", "why?", "Why?", "explain", "explain that", "what did you read",
                     "how did you read that", "why not"):
            assert _WHY_RX.match(line), line
        for line in ("why is Prussia at war", "why did the bills move", "explain the treaty",
                     "what did you read in the gazette"):
            assert not _WHY_RX.match(line), line
