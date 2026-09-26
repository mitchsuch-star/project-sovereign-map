"""IQ-9 "The Keyless Parser Gate" — the live-LLM escalation path, pinned
deterministically, without a key and without a network (September 18, 2026).

Build contract: the IQ-9 recon §4–§6 as amended by the lead's addendum.
Support module: `tests/_parser_replay.py`. Cassettes:
`tests/data/parser_cassettes/` (all AUTHORED — the suite never records; the
user promotes them with `tools/record_parser_cassettes.py --record`).

What is pinned here, tier by tier:

  T0   the suite floor — LLM_MODE pinned mock (module-level for the
       import-time singleton in backend.main, per-test for hygiene) and the
       loopback-allowing network guard; the three env-derived tests recon §3
       named run mock under LLM_MODE=anthropic (a subprocess census).
  Seam `AnthropicProvider.bind_sdk_client` short-circuits the SDK build; a
       cassette miss is a BaseException (an Exception miss is swallowed into
       a green fallback — the sensitivity arm proves it).
  A    the four `live_only` corpus rows through `evaluate_entry` unchanged.
  B    the below-gate phrasing set (R7–R14): parse fields AND the executor
       dispatch decision through POST /command.
  CR-5 aggressive / cautious / literal arms + the CR-5b register gate.
  C    fifteen response shapes (S1–S16) — truncation, refusal, malformed
       input, hallucinations, generic/unknown targets, forbidden diplomatic
       fields, text fallback, empty content.
  D    the nine typed API errors — `llm_error`, and EXACTLY ONE live call per
       request (Berthier's live arm silenced by `skip_llm`).
  CR-2 the forced retry fires exactly once and cannot rescue the word-scan
       family today (IQ9-X1, pinned as CURRENT behaviour by name).
  E    the transport tier: a REAL SDK client over `httpx.MockTransport`, so
       the SDK's retry count and typed-error construction run for real.
  H    cassette hygiene: every live_only row has a cassette, the manifest is
       exact, drift is acknowledged or fails, no test imports the recorder,
       no test builds a bare SDK client.

Every pin that involves the model asserts the NUMBER of live calls. Three
measured deviations from the recon are recorded at the pins that carry them:
the guard surfaces through the SDK as `APIConnectionError` (cause chain);
"Zorglub, attack Mack" ends in the CR-2 `unknown_name` clarification (the
addressed-token guard outranks the model's empty marshal list); a failure
dict carries no `mode`, so `parse_mode` reads "mock" after a live-road
failure (pre-existing, filed, not fixed here).
"""

from __future__ import annotations

import ast
import asyncio
import contextlib
import io
import json
import os
import socket
import subprocess
import sys
import warnings
from pathlib import Path

import anthropic
import httpx
import pytest
from fastapi.testclient import TestClient

from backend.ai.llm_client import LLMClient, LLM_FALLBACK_CONFIDENCE_THRESHOLD
from backend.ai.parser_eval import (
    _run_replay, build_llm_game_state, build_world, evaluate_entry, load_corpus,
    run_corpus, worlds_for_entry,
)
from backend.ai.providers import (
    MAX_RETRIES, PARSE_TOOL, PARSE_TOOL_NAME, REQUEST_TIMEOUT_SECONDS,
    AnthropicProvider,
)
from backend.commands.delegation import (
    _AGGRESSIVE_FLOORS, describe_cautious_delegation, detect_delegation,
    parse_resolved_to_action,
)
from backend.commands.parser import CommandParser
from tests._parser_replay import (
    API_ERROR_KINDS, CASSETTE_DIR, CassetteMiss, MANIFEST_PATH, MODEL_PIN,
    PROVENANCE_VALUES, KINDS, ReplayFault, RequestInvariantViolation,
    REPLAY_API_KEY, armed_parser, authored_cassette, body_kind,
    cassette_files, cassette_key, check_request_invariants, fingerprint,
    is_loopback_host, load_all_cassettes, load_manifest, load_phrasings,
    make_api_error, message_from_wire, network_guard_installed, text_message,
    tool_message, utterance_of, wire_message,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
TESTS_DIR = REPO_ROOT / "tests"
PY = sys.executable

CORPUS = load_corpus()
FILE_CASSETTES = load_all_cassettes()
MANIFEST = load_manifest()
PHRASINGS = load_phrasings()
LIVE_ONLY_ROWS = [e for e in CORPUS["entries"] if e.get("live_only")]

# The S/E-tier phrase: a plain below-gate order (fast 0.5) that is NOT a
# delegation, so the CR-5 ASK arm never consumes it and main.py's Berthier
# recovery IS reached on a failure.
UTT = "Ney, get after Mack"
A_INPUT = {
    "matched": True, "command_type": "tactical", "marshals": ["Ney"],
    "action": "attack", "target": "Mack", "target_stance": None,
    "is_strategic": False, "strategic_type": None, "strategic_condition": None,
    "ambiguity": 20, "strategic_score": 15, "interpretation": "Ney attacks Mack",
    "flavor": None, "suggestion": None, "diplomatic_data": None,
}
DELEG = "Ney, deal with Mack"
DELEG_INPUT = FILE_CASSETTES["cr5-deleg-aggressive-ney-resolves-live"][
    "response"]["content"][0]["input"]
SENTINEL = "UNEXPECTED BERTHIER LIVE CALL"

_QUIET = io.StringIO()


def _quiet():
    return contextlib.redirect_stdout(_QUIET)


def fresh_world(world_key="1805"):
    with _quiet():
        world = build_world(world_key)
        return world, build_llm_game_state(world)


def arm(cassettes, world_key="1805", manifest=None):
    with _quiet():
        return armed_parser(cassettes, world_key, manifest)


def berthier_sentinel(utterance, world_key="1805"):
    """A recovery cassette whose text names itself, so an UNEXPECTED Berthier
    live call is visible in the response and not only in the call count."""
    return authored_cassette(f"sentinel:{utterance}", utterance, world_key,
                             kind="berthier", response=text_message(SENTINEL))


def parse(parser, text, gs, world):
    with _quiet():
        return parser.parse(text, gs, world=world)


@pytest.fixture(scope="module")
def parse_worlds():
    """Parse-level tests share worlds: `parser.parse` does not mutate them."""
    return {wk: fresh_world(wk) for wk in ("1805", "legacy")}


@pytest.fixture
def endpoint():
    """The CR-5 `endpoint1805` idiom: swap main_module's parser/world/state for
    an armed parser on a FRESH 1805 world; yields a driver."""
    import backend.main as main_module

    orig = (main_module.parser, main_module.world, main_module.game_state)
    state = {}

    def install(cassettes, extra_berthier_sentinel_for=None):
        world, gs = fresh_world("1805")
        pool = list(cassettes)
        if extra_berthier_sentinel_for:
            pool.append(berthier_sentinel(extra_berthier_sentinel_for))
        parser, replay = arm(pool, "1805", MANIFEST)
        main_module.parser = parser
        main_module.world = world
        main_module.game_state = {"world": world}
        state.update(world=world, gs=gs, parser=parser, replay=replay)
        install.gs = gs
        install.parser = parser
        return world, replay

    def post(text):
        with _quiet():
            return TestClient(main_module.app).post(
                "/command", json={"command": text}).json()

    install.post = post
    install.module = main_module
    try:
        yield install
    finally:
        (main_module.parser, main_module.world,
         main_module.game_state) = orig


# ═══════════════════════════════════════════════════════════════════════════
# T0 — the suite floor
# ═══════════════════════════════════════════════════════════════════════════

class TestT0SuiteFloor:

    def test_llm_mode_is_pinned_mock_for_the_suite(self):
        assert os.environ.get("LLM_MODE") == "mock"
        with _quiet():
            assert LLMClient().provider_name == "mock"       # env-derived
            assert CommandParser().llm.provider_name == "mock"

    def test_the_import_time_parser_singleton_is_mock(self):
        """backend.main builds `parser = CommandParser()` at IMPORT, during
        collection, before any fixture runs — which is why the pin is ALSO a
        module-level assignment in conftest and not only an autouse fixture.
        The ca9 negation test drives this very object."""
        import backend.main as main_module
        assert main_module.parser.llm.provider_name == "mock"

    def test_network_guard_is_installed(self):
        assert network_guard_installed()
        assert is_loopback_host("127.0.0.1") and is_loopback_host("::1")
        assert is_loopback_host("localhost") and is_loopback_host("127.5.5.5")
        assert not is_loopback_host("api.anthropic.com")
        assert not is_loopback_host("1.1.1.1")

    def test_network_guard_refuses_api_anthropic_com_through_the_sdk(self):
        """MEASURED DEVIATION from recon §4.5: the SDK wraps the transport's
        RuntimeError into APIConnectionError (after its retries), keeping the
        original as __cause__ — so the pin is the cause chain, not the type.
        `http_client=` is passed only to satisfy the no-bare-client census
        (it is a plain httpx.Client, whose transport the guard patches)."""
        client = anthropic.Anthropic(api_key="sk-guard-probe", max_retries=0,
                                     http_client=httpx.Client())
        with pytest.raises(anthropic.APIConnectionError) as info:
            client.messages.create(
                model=MODEL_PIN, max_tokens=5,
                messages=[{"role": "user", "content": "hi"}])
        cause = info.value.__cause__
        assert isinstance(cause, RuntimeError)
        assert "IQ-9 network guard" in str(cause)
        assert "api.anthropic.com" in str(cause)

    def test_network_guard_refuses_a_raw_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            with pytest.raises(RuntimeError, match="IQ-9 network guard"):
                sock.connect(("1.1.1.1", 443))
        finally:
            sock.close()

    def test_network_guard_allows_loopback(self):
        """asyncio's Windows self-pipe is a loopback socketpair that CONNECTS
        to 127.0.0.1; TestClient needs an event loop; the IQ-8 driver pins
        bind a real server on loopback. All three must keep working."""
        loop = asyncio.new_event_loop()
        try:
            assert loop.run_until_complete(asyncio.sleep(0, result=7)) == 7
        finally:
            loop.close()
        a, b = socket.socketpair()
        try:
            a.sendall(b"ping")
            assert b.recv(4) == b"ping"
        finally:
            a.close()
            b.close()
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.bind(("127.0.0.1", 0))
        srv.listen(1)
        try:
            cli = socket.create_connection(srv.getsockname(), timeout=2)
            cli.close()
        finally:
            srv.close()
        import backend.main as main_module
        with _quiet():
            assert TestClient(main_module.app).get("/test").status_code == 200

    def test_the_three_env_derived_tests_now_run_mock(self, tmp_path):
        """The recon §3 census: three test ids in two files built ENV-DERIVED
        clients and would have escalated to the live API on an anthropic
        .env. Re-run them under LLM_MODE=anthropic + a fake key with the
        census plugin (`tests/_escalation_census.py`, which also raises the
        guard) and assert ZERO env-derived escalation opportunities — the
        conftest pin makes an env-derived client mock by construction.

        The two `TestT0FixtureRestoresADirtyEnv` ids ride along IN ORDER so
        the per-test fixture is exercised in a controlled sequence."""
        out = tmp_path / "census.jsonl"
        ids = [
            "tests/test_creative_audit_ca9_2026_08_08.py::"
            "TestReviewObjectionAnswersAreNegationSafe::"
            "test_a_negated_answer_executes_nothing[no compromise]",
            "tests/test_review_2026_08_30.py::TestAQuestionIsNotAnOrder::"
            "test_the_imperative_still_issues_and_still_costs"
            "[Lannes, march to Paris-Lannes-MOVE_TO]",
            "tests/test_review_2026_08_30.py::TestAProperNameDoesNotTakeAnArticle::"
            "test_an_articled_noun_never_binds_a_commander[Ney, advance over the moor]",
            "tests/test_iq9_keyless_parser_gate.py::TestT0FixtureRestoresADirtyEnv::"
            "test_a_dirty_direct_write",
            "tests/test_iq9_keyless_parser_gate.py::TestT0FixtureRestoresADirtyEnv::"
            "test_b_sees_mock_again",
        ]
        env = dict(os.environ)
        env.pop("PYTHONIOENCODING", None)
        env.update({"LLM_MODE": "anthropic",
                    "ANTHROPIC_API_KEY": "sk-census-fake-never-sent",
                    "ESCALATION_CENSUS_OUT": str(out)})
        proc = subprocess.run(
            [PY, "-m", "pytest", *ids, "-q", "-p", "no:randomly",
             "-p", "tests._escalation_census", "--tb=short"],
            cwd=str(REPO_ROOT), env=env, capture_output=True, text=True,
            timeout=900)
        assert proc.returncode == 0, proc.stdout[-3000:] + proc.stderr[-1500:]
        rows = []
        if out.exists():
            rows = [json.loads(line) for line in
                    out.read_text(encoding="utf-8").splitlines() if line.strip()]
        # The instrument ran: the three ids DO reach the gate (that is the
        # recon's own reading — 4 opportunities: 3 parse escalations + the
        # ca9 Berthier arm). `env_derived` says how a client was BUILT; the
        # harm is an env-derived client that resolved LIVE. Measured before
        # the pin under LLM_MODE=anthropic: provider_name "anthropic" on all
        # three; after: "mock" on all four rows.
        env_derived = [r for r in rows if r["env_derived"]]
        assert len(env_derived) >= 3, rows
        assert {r["test"].split("::")[0] for r in env_derived} == {
            "tests/test_creative_audit_ca9_2026_08_08.py",
            "tests/test_review_2026_08_30.py"}
        live = [r for r in env_derived if r["provider_name"] != "mock"]
        assert live == [], live


class TestT0FixtureRestoresADirtyEnv:
    """The per-test half of T0. `test_a` dirties the environment with a plain
    assignment (no monkeypatch — the shape a careless test would use);
    pytest's monkeypatch undo in the autouse fixture's teardown restores the
    value it saw at setenv time ("mock"), so `test_b` — run after it in the
    census subprocess and in file order — sees mock. Under the module-level
    pin alone `test_a`'s write would leak into `test_b`."""

    def test_a_dirty_direct_write(self):
        os.environ["LLM_MODE"] = "anthropic"
        assert os.environ["LLM_MODE"] == "anthropic"

    def test_b_sees_mock_again(self):
        assert os.environ.get("LLM_MODE") == "mock"
        with _quiet():
            assert LLMClient().provider_name == "mock"


# ═══════════════════════════════════════════════════════════════════════════
# The seam
# ═══════════════════════════════════════════════════════════════════════════

class TestSeam:

    def test_pre_set_sdk_client_short_circuits_client_build(self):
        provider = AnthropicProvider()
        provider._api_key = "sk-seam-probe"
        fake = object()
        provider.bind_sdk_client(fake)
        assert provider._client() is fake
        # ...and a provider nobody bound builds the SDK client (offline: no
        # call is made by construction).
        plain = AnthropicProvider()
        plain._api_key = "sk-seam-probe"
        assert isinstance(plain._client(), anthropic.Anthropic)

    def test_binding_is_per_instance_and_default_is_untouched(self):
        a, b = AnthropicProvider(), AnthropicProvider()
        a._api_key = b._api_key = "sk-seam-probe"
        a.bind_sdk_client("A")
        assert a._client() == "A"
        assert b._sdk_client is None

    def test_a_cassette_miss_is_a_base_exception_and_propagates(self, parse_worlds):
        assert issubclass(CassetteMiss, BaseException)
        assert not issubclass(CassetteMiss, Exception)
        assert issubclass(RequestInvariantViolation, ReplayFault)
        assert not issubclass(ReplayFault, Exception)
        world, gs = parse_worlds["1805"]
        parser, replay = arm([])
        with pytest.raises(CassetteMiss):
            parse(parser, UTT, gs, world)
        assert replay.misses == [("parse", UTT, "1805")]
        assert len(replay.calls) == 1

    def test_an_exception_miss_would_have_been_swallowed(self, parse_worlds):
        """SENSITIVITY: the same miss raised as an Exception subclass is eaten
        by `_post_messages`'s catch-all and comes back as a green fast-parser
        fallback with llm_error=True — the vacuous pass the BaseException rule
        exists to forbid."""
        world, gs = parse_worlds["1805"]
        parser, replay = arm([])

        def exception_miss(**body):
            raise AssertionError("plain-Exception miss")
        replay.messages.create = exception_miss
        result = parse(parser, UTT, gs, world)
        assert result["success"] is False
        assert result.get("llm_error") is True

    def test_armed_parser_is_the_byok_shape(self, parse_worlds):
        parser, replay = arm([])
        assert parser.llm.provider_name == "anthropic"
        assert parser.llm.key_source == "byok"
        assert parser.llm.api_key == REPLAY_API_KEY
        assert parser.llm.provider._client() is replay


# ═══════════════════════════════════════════════════════════════════════════
# Request invariants
# ═══════════════════════════════════════════════════════════════════════════

class TestRequestInvariants:

    def test_parse_body_is_forced_tool_temperature_zero_model_pin_max_tokens(
            self, parse_worlds):
        world, gs = parse_worlds["1805"]
        parser, replay = arm([authored_cassette("a", UTT, "1805",
                                                response=tool_message(A_INPUT))])
        parse(parser, UTT, gs, world)
        assert len(replay.calls) == 1
        body = replay.calls[0]
        assert body["tools"] == [PARSE_TOOL]
        assert body["tool_choice"] == {"type": "tool", "name": PARSE_TOOL_NAME}
        assert body["temperature"] == 0
        assert body["model"] == MODEL_PIN
        assert body["max_tokens"] == 1000
        assert utterance_of(body) == UTT
        assert body_kind(body) == "parse"

    def test_berthier_body_has_no_tools_and_no_temperature(self, parse_worlds):
        world, gs = parse_worlds["1805"]
        parser, replay = arm([berthier_sentinel(UTT)])
        with _quiet():
            text = parser.llm.generate_berthier_recovery(
                UTT, gs, {"recognized_marshal": "Ney", "recognized_target": None,
                          "raw_input": UTT}, skip_llm=False)
        assert text == SENTINEL
        body = replay.calls[0]
        assert body_kind(body) == "berthier"
        assert "tools" not in body and "tool_choice" not in body
        assert "temperature" not in body
        assert body["model"] == MODEL_PIN and body["max_tokens"] == 1000
        assert utterance_of(body) == UTT

    def test_the_invariant_checker_fires_on_a_drifted_body(self, parse_worlds):
        """SENSITIVITY for the checker every replay runs through."""
        world, gs = parse_worlds["1805"]
        parser, replay = arm([authored_cassette("a", UTT, "1805",
                                                response=tool_message(A_INPUT))])
        parse(parser, UTT, gs, world)
        body = replay.calls[0]
        check_request_invariants(body)                       # the real body passes
        for broken in (dict(body, temperature=0.3), dict(body, model="claude-3-haiku"),
                       dict(body, max_tokens=500),
                       {k: v for k, v in body.items() if k != "tool_choice"},
                       dict(body, tools=[])):
            with pytest.raises(RequestInvariantViolation):
                check_request_invariants(broken)


# ═══════════════════════════════════════════════════════════════════════════
# The gate itself — what NEVER reaches the model
# ═══════════════════════════════════════════════════════════════════════════

class TestGateNeverReachesTheModel:

    def test_a_confident_fast_parse_never_reaches_the_model(self, parse_worlds):
        world, gs = parse_worlds["1805"]
        parser, replay = arm([])                               # any call = miss
        result = parse(parser, "Ney, attack Mack", gs, world)
        assert result["success"] and result["command"]["action"] == "attack"
        assert result["command"]["mode"] == "mock"
        assert replay.calls == []
        assert LLM_FALLBACK_CONFIDENCE_THRESHOLD == 0.7

    def test_a_parse_neg_refusal_never_reaches_the_model(self, parse_worlds):
        world, gs = parse_worlds["1805"]
        parser, replay = arm([])
        result = parse(parser, "Ney, never attack Mack", gs, world)
        assert result["success"] is False
        assert result.get("refusal")
        assert replay.calls == []


# ═══════════════════════════════════════════════════════════════════════════
# Tier A — the live_only corpus rows through the CR-1 evaluator unchanged
# ═══════════════════════════════════════════════════════════════════════════

def _live_only_params():
    params = []
    for entry in LIVE_ONLY_ROWS:
        for wk in worlds_for_entry(entry):
            params.append(pytest.param(entry, wk, id=f"{entry['id']}[{wk}]"))
    return params


class TestLiveOnlyCorpusRows:

    @pytest.mark.parametrize("entry,world_key", _live_only_params())
    def test_live_only_row_replays_through_evaluate_entry(
            self, parse_worlds, entry, world_key):
        world, gs = parse_worlds[world_key]
        parser, replay = arm(list(FILE_CASSETTES.values()), world_key, MANIFEST)
        with _quiet():
            mismatches = evaluate_entry(parser, entry, world_key, world, gs)
        assert not mismatches, mismatches
        assert len(replay.calls) == 1, "exactly one live call per row"
        assert replay.misses == []
        served = replay.served[0]
        assert FILE_CASSETTES[served]["utterance"] == entry["utterance"]
        assert FILE_CASSETTES[served]["world"] == world_key

    def test_parser_eval_replay_mode_runs_every_live_only_row(self):
        with _quiet():
            summary = _run_replay(CORPUS)
        assert summary["failed"] == 0
        assert summary["total"] == summary["passed"] == len(_live_only_params())
        assert summary["replay_calls"] == summary["total"]
        assert summary["replay_drifted"] == []

    def test_run_corpus_default_loop_is_unchanged(self):
        """The `parser=None` default reproduces the pre-IQ-9 loop; an explicit
        mock parser gives the same answer."""
        with _quiet():
            default = run_corpus(CORPUS, only_ids=["ultimatum-to-britain"])
            explicit = run_corpus(CORPUS, only_ids=["ultimatum-to-britain"],
                                  parser=CommandParser(use_real_llm=False))
        assert default["passed"] == default["total"] == 2
        assert explicit["passed"] == explicit["total"] == 2
        # `only_ids` filters BEFORE the live_only skip is counted (unchanged).
        assert default["skipped_live_only"] == 0


# ═══════════════════════════════════════════════════════════════════════════
# Tier B — the below-gate phrasing set (R7–R14)
# ═══════════════════════════════════════════════════════════════════════════

def _phrasing_params():
    return [pytest.param(e, id=e["id"]) for e in PHRASINGS["entries"]]


class TestBelowGatePhrasings:

    @pytest.mark.parametrize("entry", _phrasing_params())
    def test_parse_fields(self, parse_worlds, entry):
        world, gs = parse_worlds[entry["world"]]
        parser, replay = arm(list(FILE_CASSETTES.values()), entry["world"], MANIFEST)
        with _quiet():
            mismatches = evaluate_entry(parser, entry, entry["world"], world, gs)
        assert not mismatches, mismatches
        assert len(replay.calls) == 1 and replay.served == [entry["cassette"]]

    def test_live_results_carry_live_provenance(self, parse_worlds):
        world, gs = parse_worlds["1805"]
        parser, replay = arm(list(FILE_CASSETTES.values()), "1805", MANIFEST)
        cmd = parse(parser, UTT, gs, world)["command"]
        assert cmd["mode"] == "anthropic"
        assert cmd["key_source"] == "byok"
        assert cmd["confidence"] == 0.85           # telemetry only

    def test_demonym_targets_are_cleared_and_hinted(self, parse_worlds):
        world, gs = parse_worlds["1805"]
        parser, replay = arm(list(FILE_CASSETTES.values()), "1805", MANIFEST)
        r = parse(parser, "Murat, harass the Austrians", gs, world)
        assert r["command"]["target"] is None
        assert r["command"]["target_nation_hint"] == "Austria"
        r = parse(parser, "Ney, hit the Prussians hard", gs, world)
        assert r["command"]["target"] is None
        assert r["command"]["target_nation_hint"] == "Prussia"
        assert len(replay.calls) == 2

    def test_make_your_way_upgrades_to_move_to_deterministically(self, parse_worlds):
        world, gs = parse_worlds["1805"]
        parser, replay = arm(list(FILE_CASSETTES.values()), "1805", MANIFEST)
        r = parse(parser, "Lannes, make your way to Swabia", gs, world)
        assert r["command"]["action"] == "move"          # `march` remapped
        assert r["is_strategic"] and r["strategic_type"] == "MOVE_TO"
        assert r["command"]["target"] == "Swabia"

    # ── the executor dispatch decision, through POST /command ──────────────

    def test_get_after_attacks_and_charges_ap(self, endpoint):
        world, replay = endpoint(FILE_CASSETTES.values(), UTT)
        data = endpoint.post(UTT)
        assert data["success"] is True
        assert "MUSTER" in data["message"] and "Mack" in data["message"]
        assert int(world.actions_remaining) == 3
        assert replay.call_kinds() == ["parse"]
        assert data["parse_mode"] == "anthropic"

    def test_keep_an_eye_scouts_without_the_cautious_clamp_note(self, endpoint):
        utt = "Davout, keep an eye on Mack"
        world, replay = endpoint(FILE_CASSETTES.values(), utt)
        data = endpoint.post(utt)
        assert data["success"] is True
        assert data["message"].startswith("Davout scouts Swabia")
        assert "press the assault" not in data["message"]   # no delegation note
        assert int(world.actions_remaining) == 3
        assert replay.call_kinds() == ["parse"]

    def test_make_your_way_issues_a_move_to_order(self, endpoint):
        utt = "Lannes, make your way to Swabia"
        world, replay = endpoint(FILE_CASSETTES.values(), utt)
        data = endpoint.post(utt)
        assert data["success"] is True
        order = world.get_marshal("Lannes").strategic_order
        assert order is not None and order.target == "Swabia"
        assert "MOVE_TO" in str(getattr(order, "order_type", order))
        assert int(world.actions_remaining) == 3
        assert replay.call_kinds() == ["parse"]

    def test_ask_austria_stages_the_diplomatic_desk(self, endpoint):
        utt = "ask Austria what they want"
        world, replay = endpoint(FILE_CASSETTES.values(), utt)
        data = endpoint.post(utt)
        assert data["success"] is True
        assert "Austria" in data["message"]
        assert world.pending_diplomatic_dialogue is not None
        assert int(world.actions_remaining) == 4
        assert replay.call_kinds() == ["parse"]

    def test_unknown_addressee_reaches_the_unknown_name_clarification(self, endpoint):
        """MEASURED DEVIATION from recon R11 ("Which marshal?"): the model's
        `marshals: []` is outranked by the deterministic addressed-token
        guard, so the live road ends in the CR-2 `unknown_name` question —
        the same question the mock road asks. One live call, no AP."""
        utt = "Zorglub, attack Mack"
        world, replay = endpoint(FILE_CASSETTES.values(), utt)
        data = endpoint.post(utt)
        assert data.get("clarification_kind") == "unknown_name"
        assert "Zorglub" in data["message"]
        assert int(world.actions_remaining) == 4
        assert replay.call_kinds() == ["parse"]

    def test_harass_the_austrians_resolves_the_hint_to_mack(self, endpoint):
        utt = "Murat, harass the Austrians"
        world, replay = endpoint(FILE_CASSETTES.values(), utt)
        data = endpoint.post(utt)
        assert data["success"] is True
        assert "Murat" in data["message"] and "Mack" in data["message"]
        assert int(world.actions_remaining) == 3
        assert replay.call_kinds() == ["parse"]

    def test_gibberish_is_followed_by_berthiers_own_live_call(self, endpoint):
        """R13: the model says matched:false → the fast result stands →
        main.py's Berthier recovery makes its OWN text-mode call, served by
        the SECOND cassette one request consumes."""
        utt = "flurble the wibble"
        world, replay = endpoint(FILE_CASSETTES.values())   # no sentinel: the
        data = endpoint.post(utt)                            # real recovery cassette
        assert data["success"] is False
        assert data["message"].startswith("Berthier blinks at the dispatch")
        assert replay.call_kinds() == ["parse", "berthier"]
        assert replay.served == ["gibberish-berthier", "gibberish-berthier.recovery"]
        assert int(world.actions_remaining) == 4

    def test_hit_the_prussians_is_refused_honestly_out_of_reach(self, endpoint):
        utt = "Ney, hit the Prussians hard"
        world, replay = endpoint(FILE_CASSETTES.values(), utt)
        data = endpoint.post(utt)
        assert data["success"] is False
        assert "No Prussia force is within Ney's reach" in data["message"]
        assert int(world.actions_remaining) == 4
        assert replay.call_kinds() == ["parse"]

    def test_a_live_road_failure_names_the_live_road(self, endpoint):
        """IQ9-X3 — FLIPPED CONSCIOUSLY by SR-3c (September 26, 2026,
        `COMMAND_ROBUSTNESS_SPEC.md` §12.11). This pin used to record the
        defect as current behaviour: the parser's failure dicts carried no
        `mode`, so `_PARSE_PROVENANCE` read "mock" on a request that DID make
        a live call. A failure now names the road it came down
        (`parser.A_FAILURE_NAMES_ITS_ROAD`); the full rule is pinned in
        `tests/test_cr6_retry_rescues_the_word_scan.py`."""
        utt = "flurble the wibble"
        world, replay = endpoint(FILE_CASSETTES.values())
        data = endpoint.post(utt)
        assert replay.call_kinds() == ["parse", "berthier"]
        assert data["parse_mode"] == "anthropic"


# ═══════════════════════════════════════════════════════════════════════════
# CR-5 arms + CR-5b register gate
# ═══════════════════════════════════════════════════════════════════════════

def _co_locate_weak_mack(world):
    """The non-modal success path for the aggressive PURSUE: a weak Mack
    beside Ney, at war, scouted (the CR-5 hint test's own setup)."""
    ney, mack = world.get_marshal("Ney"), world.get_marshal("Mack")
    mack.location = ney.location
    mack.strength = 2000
    ney.strength = 60000
    world.diplomatic_states[world._make_diplo_key(ney.nation, mack.nation)] = "WAR"
    world.update_intel_from_scout(ney.location, world.current_turn)
    world.delegation_hint_shown = True          # keep the hint out of the message


class TestCR5Arms:

    def test_the_live_delegation_parse_resolves(self, parse_worlds):
        world, gs = parse_worlds["1805"]
        parser, replay = arm(list(FILE_CASSETTES.values()), "1805", MANIFEST)
        r = parse(parser, DELEG, gs, world)
        cmd = r["command"]
        assert cmd["action"] == "attack"           # `pursue` remapped (CR-3)
        assert cmd["marshal"] == "Ney" and cmd["target"] == "Mack"
        assert cmd["mode"] == "anthropic"
        assert cmd["flavor"] == DELEG_INPUT["flavor"]   # the CR-5b lift
        assert parse_resolved_to_action(r) is True
        assert len(replay.calls) == 1

    def test_aggressive_arm_creates_delegation_inferred_pursue_and_withholds_flavor_on_the_modal(
            self, endpoint):
        world, replay = endpoint(FILE_CASSETTES.values(), DELEG)
        data = endpoint.post(DELEG)
        assert data.get("clarification_kind") != "delegation", "degraded to ASK"
        assert data.get("pending_interrupt"), "the bad-odds modal did not mount"
        order = world.get_marshal("Ney").strategic_order
        assert order is not None and order.delegation_inferred is True
        assert order.target == "Mack"
        assert int(world.actions_remaining) == 3
        assert "Mack will learn" not in data["message"]      # withheld on the modal
        assert replay.call_kinds() == ["parse"]

    def test_aggressive_flavor_attaches_on_the_non_modal_success_path(self, endpoint):
        world, replay = endpoint(FILE_CASSETTES.values(), DELEG)
        _co_locate_weak_mack(world)
        data = endpoint.post(DELEG)
        assert data["success"] is True
        assert not data.get("pending_interrupt")
        assert DELEG_INPUT["flavor"] in data["message"]
        assert replay.call_kinds() == ["parse"]

    def test_flavor_register_gate_drops_a_parroting_line_to_the_floor(self, endpoint):
        parrot = "Ney will deal with Mack, Sire."
        cassette = authored_cassette(
            "parrot", DELEG, "1805",
            response=tool_message(dict(DELEG_INPUT, flavor=parrot)))
        world, replay = endpoint([cassette], DELEG)
        _co_locate_weak_mack(world)
        data = endpoint.post(DELEG)
        assert data["success"] is True
        assert parrot not in data["message"]
        floors = {f.format(marshal="Ney", target="Mack") for f in _AGGRESSIVE_FLOORS}
        assert any(f in data["message"] for f in floors), data["message"]
        assert replay.call_kinds() == ["parse"]

    def test_cautious_arm_clamps_to_scout_with_register_gated_prefix(self, endpoint):
        utt = "Davout, deal with Mack"
        world, replay = endpoint(FILE_CASSETTES.values(), utt)
        with _quiet():
            match = detect_delegation(world, utt, None)
        note = describe_cautious_delegation(match, "scout")
        prefix = FILE_CASSETTES["cr5-deleg-cautious-davout-resolves-live"][
            "response"]["content"][0]["input"]["flavor"]
        data = endpoint.post(utt)
        assert data["success"] is True
        assert data["message"].startswith("Davout scouts Swabia")
        assert prefix in data["message"]
        assert note in data["message"]
        assert data["message"].index(prefix) < data["message"].index(note)
        assert int(world.actions_remaining) == 3
        assert replay.call_kinds() == ["parse"]

    def test_cautious_prefix_is_dropped_when_the_live_line_is_exclamatory(self, endpoint):
        utt = "Davout, deal with Mack"
        base = FILE_CASSETTES["cr5-deleg-cautious-davout-resolves-live"][
            "response"]["content"][0]["input"]
        loud = "Davout weighs the ground first, Sire! Mack will keep."
        world, replay = endpoint([authored_cassette(
            "loud", utt, "1805", response=tool_message(dict(base, flavor=loud)))], utt)
        with _quiet():
            match = detect_delegation(world, utt, None)
        data = endpoint.post(utt)
        assert data["success"] is True
        assert loud not in data["message"]
        assert describe_cautious_delegation(match, "scout") in data["message"]
        assert replay.call_kinds() == ["parse"]

    def test_literal_arm_asks_even_when_the_model_resolved(self, endpoint, parse_worlds):
        utt = "Soult, deal with Mack"
        world_p, gs = parse_worlds["1805"]
        parser, _ = arm(list(FILE_CASSETTES.values()), "1805", MANIFEST)
        assert parse_resolved_to_action(parse(parser, utt, gs, world_p)) is True
        world, replay = endpoint(FILE_CASSETTES.values(), utt)
        data = endpoint.post(utt)
        assert data.get("clarification_kind") == "delegation"
        assert "Soult will not presume your meaning" in data["message"]
        assert int(world.actions_remaining) == 4
        assert world.get_marshal("Soult").strategic_order is None
        assert replay.call_kinds() == ["parse"]

    def test_mock_mode_delegation_still_degrades_to_ask(self, endpoint):
        """Guardrail (e), the other direction of the R1 pin: the fast parser
        resolves a keyword-bearing delegation at 0.95 (mode mock) and the
        aggressive arm must NOT fire on it — no live call was made."""
        utt = "Ney, deal with the attack on Mack"
        world, replay = endpoint([], utt)             # a call would be a miss
        data = endpoint.post(utt)
        assert data.get("clarification_kind") == "delegation"
        assert replay.calls == []
        assert parse_resolved_to_action(
            {"success": True, "mode": "mock", "command": {"action": "attack"}}) is False


# ═══════════════════════════════════════════════════════════════════════════
# Tier C — response shapes
# ═══════════════════════════════════════════════════════════════════════════

def _shape(response, label="shape"):
    return authored_cassette(label, UTT, "1805", response=response)


def _parse_shape(parse_worlds, response):
    world, gs = parse_worlds["1805"]
    with warnings.catch_warnings():
        # S3's leniently-constructed Message serialises with pydantic
        # warnings (the string input is exactly the shape being tested).
        warnings.simplefilter("ignore")
        parser, replay = arm([_shape(response)])
        r = parse(parser, UTT, gs, world)
    assert len(replay.calls) == 1
    return r


def _assert_fast_fallback_no_error(r):
    """The fast result stands — NOT an API error."""
    assert r["success"] is False
    assert r["error"] == "Unknown action: unknown"
    assert not r.get("llm_error")


def _assert_attack_mack(r, target="Mack"):
    assert r["success"] is True
    assert r["command"]["action"] == "attack"
    assert r["command"]["marshal"] == "Ney"
    assert r["command"]["target"] == target
    assert r["command"]["mode"] == "anthropic"


class TestResponseShapes:

    def test_s1_truncation_at_max_tokens_discards_the_partial_tool_call(self, parse_worlds):
        _assert_fast_fallback_no_error(
            _parse_shape(parse_worlds, tool_message(A_INPUT, stop_reason="max_tokens")))

    def test_s2_refusal_is_a_no_parse(self, parse_worlds):
        _assert_fast_fallback_no_error(
            _parse_shape(parse_worlds, tool_message(A_INPUT, stop_reason="refusal")))

    def test_s3_a_string_tool_input_falls_to_the_text_fallback_and_no_parse(
            self, parse_worlds):
        """The SDK's lenient response construction (Message.construct) is what
        a real wire with a non-dict input would yield; the provider's
        isinstance guard skips it and the text fallback finds nothing."""
        _assert_fast_fallback_no_error(
            _parse_shape(parse_worlds, tool_message("not a dict")))

    def test_s4_action_null_fails_validation(self, parse_worlds):
        _assert_fast_fallback_no_error(
            _parse_shape(parse_worlds, tool_message(dict(A_INPUT, action=None))))

    def test_s5_unknown_verb_fails_validation(self, parse_worlds):
        _assert_fast_fallback_no_error(_parse_shape(
            parse_worlds, tool_message(dict(A_INPUT, action="bombard_everything"))))

    def test_s6_hallucinated_marshal_fails_validation(self, parse_worlds):
        # Grouchy is in the 1805 marshal POOL, not on the roster.
        _assert_fast_fallback_no_error(
            _parse_shape(parse_worlds, tool_message(dict(A_INPUT, marshals=["Grouchy"]))))

    def test_s7_invented_marshal_is_cleared_and_the_text_rebinds_ney(self, parse_worlds):
        r = _parse_shape(parse_worlds, tool_message(dict(A_INPUT, marshals=["Davout"])))
        _assert_attack_mack(r)

    def test_s8_marshals_as_a_string_is_normalised(self, parse_worlds):
        _assert_attack_mack(
            _parse_shape(parse_worlds, tool_message(dict(A_INPUT, marshals="Ney"))))

    def test_s9_generic_target_collapses_to_none(self, parse_worlds):
        _assert_attack_mack(
            _parse_shape(parse_worlds, tool_message(dict(A_INPUT, target="generic"))),
            target=None)

    def test_s10_unknown_region_passes_through_for_the_executor_to_name(
            self, parse_worlds):
        r = _parse_shape(parse_worlds,
                         tool_message(dict(A_INPUT, action="move", target="Venetia")))
        assert r["success"] and r["command"]["action"] == "move"
        assert r["command"]["target"] == "Venetia"

    def test_s11_forbidden_diplomatic_fields_are_stripped(self, parse_worlds):
        utt = "ask Austria what they want"
        world, gs = parse_worlds["1805"]
        base = FILE_CASSETTES["diplomatic-ask-austria"]["response"]["content"][0]["input"]
        smuggled = dict(base, diplomatic_data=dict(
            base["diplomatic_data"], confirmed_objection=True,
            _treaty_warning_resolved=True, ally_entry_decisions={"x": 1}))
        parser, replay = arm([authored_cassette("s11", utt, "1805",
                                                response=tool_message(smuggled))])
        r = parse(parser, utt, gs, world)
        assert r["success"] and r["command"]["action"] == "diplomatic_proposal"
        assert sorted(r["command"]["diplomatic_data"]) == [
            "action", "is_question", "proposal_type", "target_nation", "tone"]
        assert len(replay.calls) == 1

    def test_s12_diplomatic_action_outside_the_allowlist_fails_validation(
            self, parse_worlds):
        utt = "ask Austria what they want"
        world, gs = parse_worlds["1805"]
        base = FILE_CASSETTES["diplomatic-ask-austria"]["response"]["content"][0]["input"]
        bad = dict(base, diplomatic_data=dict(base["diplomatic_data"],
                                              action="declare_everything"))
        parser, replay = arm([authored_cassette("s12", utt, "1805",
                                                response=tool_message(bad))])
        r = parse(parser, utt, gs, world)
        _assert_fast_fallback_no_error(r)
        assert len(replay.calls) == 1

    def test_s13_invalid_strategic_type_falls_back_to_tactical(self, parse_worlds):
        r = _parse_shape(parse_worlds, tool_message(
            dict(A_INPUT, is_strategic=True, strategic_type="FLANK")))
        _assert_attack_mack(r)
        assert not r.get("is_strategic")

    def test_s14_text_block_json_fallback_still_parses(self, parse_worlds):
        _assert_attack_mack(_parse_shape(parse_worlds, text_message(json.dumps(A_INPUT))))

    def test_s15_empty_content_is_a_no_parse(self, parse_worlds):
        _assert_fast_fallback_no_error(
            _parse_shape(parse_worlds, message_from_wire(wire_message([], "end_turn"))))

    def test_s16_a_tool_use_block_for_another_tool_is_a_no_parse(self, parse_worlds):
        _assert_fast_fallback_no_error(
            _parse_shape(parse_worlds, tool_message(A_INPUT, tool_name="some_other_tool")))


# ═══════════════════════════════════════════════════════════════════════════
# Tier D — typed API errors: llm_error, and exactly one live call
# ═══════════════════════════════════════════════════════════════════════════

EXPECTED_ERROR_MESSAGE = {
    "rate_limit": "Rate limited - too many requests",
    "auth": "Invalid API key",
    "permission": "API key lacks permission for this model",
    "not_found": f"Unknown model '{MODEL_PIN}'",
    "bad_request": "Invalid request (see server log)",
    "timeout": f"Request timed out after {REQUEST_TIMEOUT_SECONDS}s",
    "connection": "Connection failed - check internet",
    "overloaded": "Server error (529)",
    "generic": "Unexpected error: ValueError",
}


class _Raiser:
    """A bound SDK client whose one call raises the given error."""

    def __init__(self, exc):
        self.messages = self
        self._exc = exc

    def create(self, **body):
        raise self._exc


class TestTypedErrors:

    @pytest.mark.parametrize("kind", API_ERROR_KINDS)
    def test_error_sets_llm_error_and_the_request_makes_exactly_one_live_call(
            self, endpoint, kind):
        world, replay = endpoint(
            [authored_cassette(kind, UTT, "1805", error=kind)], UTT)
        r = parse(endpoint.parser, UTT, endpoint.gs, world)
        assert r["success"] is False
        assert r.get("llm_error") is True
        n_parse = len(replay.calls)
        assert n_parse == 1
        data = endpoint.post(UTT)
        assert replay.call_kinds()[n_parse:] == ["parse"], (
            "a failed parse call must NOT be followed by a Berthier live call")
        assert data["success"] is False
        assert SENTINEL not in data["message"]
        assert "Sire" in data["message"]               # the mock template

    @pytest.mark.parametrize("kind", API_ERROR_KINDS)
    def test_the_ladder_names_which_failure(self, kind):
        """Each typed exception has its own arm and its own message (the
        whole point of the typed ladder — a deleted arm falls through to a
        neighbour and the message changes)."""
        provider = AnthropicProvider()
        provider._api_key = REPLAY_API_KEY
        provider.bind_sdk_client(_Raiser(make_api_error(kind)))
        with _quiet():
            response, error = provider._post_messages(
                {"model": MODEL_PIN, "max_tokens": 1000, "system": "s",
                 "messages": [{"role": "user", "content": "u"}]})
        assert response is None
        assert error == EXPECTED_ERROR_MESSAGE[kind]

    def test_make_api_error_builds_the_sdks_own_types(self):
        assert isinstance(make_api_error("rate_limit"), anthropic.RateLimitError)
        assert isinstance(make_api_error("auth"), anthropic.AuthenticationError)
        assert isinstance(make_api_error("timeout"), anthropic.APITimeoutError)
        assert isinstance(make_api_error("overloaded"), anthropic.APIStatusError)
        assert make_api_error("overloaded").status_code == 529
        assert not isinstance(make_api_error("generic"), anthropic.APIError)


# ═══════════════════════════════════════════════════════════════════════════
# CR-2 — the forced retry
# ═══════════════════════════════════════════════════════════════════════════

RETRY_UTT = "hunt down mack"


class TestCR2Retry:

    def test_retry_fires_exactly_once_on_a_confident_fuzzy_error(self, parse_worlds):
        world, gs = parse_worlds["1805"]
        with _quiet():
            fast = CommandParser(use_real_llm=False).llm.fast_parse(RETRY_UTT, gs)
        assert fast.confidence >= LLM_FALLBACK_CONFIDENCE_THRESHOLD   # never the gate
        parser, replay = arm(list(FILE_CASSETTES.values()), "1805", MANIFEST)
        parse(parser, RETRY_UTT, gs, world)
        assert len(replay.calls) == 1
        assert body_kind(replay.calls[0]) == "parse"
        assert utterance_of(replay.calls[0]) == RETRY_UTT
        assert replay.served == ["cr2-retry-hunt-down-mack"]

    def test_the_retry_rescues_the_word_scan_family(self, parse_worlds):
        """IQ9-X1 — FLIPPED CONSCIOUSLY by SR-3c (September 26, 2026,
        `COMMAND_ROBUSTNESS_SPEC.md` §12.11). This pin used to record the
        defect as current behaviour: the retried live parse (marshal-less
        `pursue Mack`) was re-run through the fuzzy pass, whose marshal WORD
        SCAN re-read 'down' → Davout, so the one live call was discarded and
        the original error stood. The retry's marshal reading now stands
        (`parser.THE_RETRY_READS_THE_MARSHAL`); the full rule is pinned in
        `tests/test_cr6_retry_rescues_the_word_scan.py`."""
        world, gs = parse_worlds["1805"]
        parser, replay = arm(list(FILE_CASSETTES.values()), "1805", MANIFEST)
        r = parse(parser, RETRY_UTT, gs, world)
        assert len(replay.calls) == 1
        assert r["success"] is True
        assert r["command"].get("marshal") is None
        assert r["command"].get("target") == "Mack"
        assert not r.get("llm_error")

    def test_retry_api_failure_reaches_the_failure_dict_and_silences_berthier(
            self, endpoint):
        world, replay = endpoint(
            [authored_cassette("rr", RETRY_UTT, "1805", error="timeout")], RETRY_UTT)
        r = parse(endpoint.parser, RETRY_UTT, endpoint.gs, world)
        assert r["success"] is False and r.get("llm_error") is True
        n = len(replay.calls)
        assert n == 1
        data = endpoint.post(RETRY_UTT)
        assert replay.call_kinds()[n:] == ["parse"]
        assert data.get("clarification_kind") == "unknown_name"
        assert SENTINEL not in data["message"]

    def test_retry_is_skipped_when_the_parse_call_already_errored(self, parse_worlds):
        world, gs = parse_worlds["1805"]
        parser, replay = arm(list(FILE_CASSETTES.values()), "1805", MANIFEST)
        with _quiet():
            retried, retry_llm_error = parser.llm.reparse_with_llm(
                RETRY_UTT, gs, {"action": "attack", "mode": "mock", "llm_error": True})
        assert (retried, retry_llm_error) == (None, False)
        assert replay.calls == []


# ═══════════════════════════════════════════════════════════════════════════
# Berthier's second call
# ═══════════════════════════════════════════════════════════════════════════

class TestBerthierSecondCall:

    def test_a_no_parse_is_followed_by_one_text_mode_call(self, endpoint):
        world, replay = endpoint(
            [_shape(tool_message(A_INPUT, stop_reason="max_tokens"), "s1")], UTT)
        data = endpoint.post(UTT)
        assert replay.call_kinds() == ["parse", "berthier"]
        assert data["success"] is False
        assert data["message"] == SENTINEL
        berthier_body = replay.calls[1]
        assert "tools" not in berthier_body and "temperature" not in berthier_body

    def test_an_api_error_is_not(self, endpoint):
        world, replay = endpoint(
            [authored_cassette("e", UTT, "1805", error="timeout")], UTT)
        data = endpoint.post(UTT)
        assert replay.call_kinds() == ["parse"]
        assert data["success"] is False
        assert SENTINEL not in data["message"]


# ═══════════════════════════════════════════════════════════════════════════
# Tier E — transport: the REAL SDK over httpx.MockTransport
# ═══════════════════════════════════════════════════════════════════════════

def _sdk_over_transport(status, body_json, hits):
    def handler(request):
        hits.append(request)
        return httpx.Response(status, json=body_json,
                              headers={"request-id": "req_replay_1"})
    return anthropic.Anthropic(
        api_key=REPLAY_API_KEY,
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
        timeout=anthropic.Timeout(REQUEST_TIMEOUT_SECONDS, connect=2.0, pool=1.0),
        max_retries=MAX_RETRIES)


def _transport_parser(status, body_json, hits):
    with _quiet():
        parser = CommandParser(use_real_llm=False)
        parser.llm = LLMClient(provider="anthropic", api_key=REPLAY_API_KEY)
    parser.llm.provider.bind_sdk_client(_sdk_over_transport(status, body_json, hits))
    return parser


class TestTransport:

    def test_200_tool_use_parses_in_one_hit(self, parse_worlds):
        world, gs = parse_worlds["1805"]
        hits = []
        parser = _transport_parser(200, tool_message(A_INPUT).to_dict(), hits)
        r = parse(parser, UTT, gs, world)
        _assert_attack_mack(r)
        assert len(hits) == 1
        assert hits[0].url.host == "api.anthropic.com"

    def test_200_max_tokens_is_a_no_parse_in_one_hit(self, parse_worlds):
        world, gs = parse_worlds["1805"]
        hits = []
        parser = _transport_parser(
            200, tool_message(A_INPUT, stop_reason="max_tokens").to_dict(), hits)
        _assert_fast_fallback_no_error(parse(parser, UTT, gs, world))
        assert len(hits) == 1

    def test_429_is_retried_once_then_typed(self, parse_worlds):
        world, gs = parse_worlds["1805"]
        hits = []
        parser = _transport_parser(
            429, {"type": "error", "error": {"type": "rate_limit_error",
                                             "message": "slow down"}}, hits)
        r = parse(parser, UTT, gs, world)
        assert r["success"] is False and r.get("llm_error") is True
        assert len(hits) == 1 + MAX_RETRIES
        assert MAX_RETRIES == 1


# ═══════════════════════════════════════════════════════════════════════════
# Cassette hygiene
# ═══════════════════════════════════════════════════════════════════════════

def _unacknowledged_drift(drifted, cassettes, manifest):
    """Recorded cassettes whose prompt drifted and whose manifest `drift`
    field is still null. Authored cassettes are exempt by policy."""
    out = []
    for cid, (recorded, live) in drifted.items():
        if cassettes[cid].get("provenance") != "recorded":
            continue
        ack = manifest["cassettes"].get(cid, {}).get("drift")
        if not ack:
            out.append(cid)
    return sorted(out)


def _test_sources():
    """Every Python module under tests/ — RECURSIVE, because `tests/helpers/`
    holds importable modules too and a census scoped to the top level would
    count the directory, not the thing (measured: two nested modules)."""
    files = [p for p in TESTS_DIR.rglob("*.py")
             if "__pycache__" not in p.parts and p.name != "conftest.py"]
    return sorted(files) + [TESTS_DIR / "conftest.py"]


def _imports_recorder(source: str) -> bool:
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any("record_parser_cassettes" in a.name for a in node.names):
                return True
        elif isinstance(node, ast.ImportFrom):
            if node.module and "record_parser_cassettes" in node.module:
                return True
            if node.module == "tools" and any(
                    a.name == "record_parser_cassettes" for a in node.names):
                return True
        elif isinstance(node, ast.Call):
            # importlib.import_module("tools.record_parser_cassettes") /
            # spec_from_file_location(..., ".../record_parser_cassettes.py")
            f = node.func
            name = (f.attr if isinstance(f, ast.Attribute) else
                    f.id if isinstance(f, ast.Name) else "")
            if name in ("import_module", "spec_from_file_location",
                        "__import__", "run_path"):
                for arg in node.args:
                    if (isinstance(arg, ast.Constant) and isinstance(arg.value, str)
                            and "record_parser_cassettes" in arg.value):
                        return True
    return False


def _bare_sdk_clients(source: str):
    """Every `anthropic.Anthropic(...)` / `Anthropic(...)` call that passes no
    `http_client=` — a client whose transport is the real network."""
    tree = ast.parse(source)
    offenders = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        f = node.func
        name = (f.attr if isinstance(f, ast.Attribute) else
                f.id if isinstance(f, ast.Name) else None)
        if name not in ("Anthropic", "AsyncAnthropic"):
            continue
        if not any(k.arg == "http_client" for k in node.keywords):
            offenders.append(node.lineno)
    return offenders


class TestCassetteHygiene:

    def test_every_live_only_row_has_a_cassette_per_world(self):
        keys = {cassette_key(c) for c in FILE_CASSETTES.values()}
        for entry in LIVE_ONLY_ROWS:
            for wk in worlds_for_entry(entry):
                assert ("parse", entry["utterance"], wk) in keys, (
                    f"{entry['id']} has no cassette for {wk}")

    def test_every_phrasing_names_a_committed_cassette(self):
        for entry in PHRASINGS["entries"]:
            c = FILE_CASSETTES[entry["cassette"]]
            assert (c["utterance"], c["world"]) == (entry["utterance"], entry["world"])

    def test_manifest_lists_every_cassette_and_nothing_else(self):
        ids_on_disk = {p.stem for p in cassette_files()}
        assert set(MANIFEST["cassettes"]) == ids_on_disk
        assert MANIFEST["corpus_version"] == 1
        for cid, meta in MANIFEST["cassettes"].items():
            entry = FILE_CASSETTES[cid]
            assert entry["id"] == cid
            assert meta["prompt_sha256"] == entry["request"]["prompt_sha256"]
            assert meta["provenance"] == entry["provenance"] in PROVENANCE_VALUES
            assert meta["kind"] == entry["kind"] in KINDS
            assert (meta["utterance"], meta["world"]) == (entry["utterance"], entry["world"])
            assert "drift" in meta

    def test_cassette_keys_are_unique(self):
        keys = [cassette_key(c) for c in FILE_CASSETTES.values()]
        assert len(keys) == len(set(keys))

    def test_every_cassette_serves_a_real_message(self):
        for cid, entry in FILE_CASSETTES.items():
            msg = message_from_wire(entry["response"])
            assert isinstance(msg, anthropic.types.Message), cid
            assert msg.to_dict()["stop_reason"] == entry["response"]["stop_reason"]

    def test_every_file_cassette_is_currently_authored(self):
        """The suite ships AUTHORED shapes (the lead never spends the user's
        key). This pin is DESCRIPTIVE: when the user records, flip it to the
        recorded count and the drift policy takes over."""
        assert {c["provenance"] for c in FILE_CASSETTES.values()} == {"authored"}

    def test_drift_is_acknowledged_or_fails(self, parse_worlds):
        drifted = {}
        for wk in ("1805", "legacy"):
            world, gs = parse_worlds[wk]
            parser, replay = arm(list(FILE_CASSETTES.values()), wk, MANIFEST)
            for entry in FILE_CASSETTES.values():
                if entry["world"] != wk:
                    continue
                with _quiet():
                    if entry["kind"] == "parse":
                        parser.parse(entry["utterance"], gs, world=world)
                    else:
                        parser.llm.generate_berthier_recovery(
                            entry["utterance"], gs, {}, skip_llm=False)
            drifted.update(replay.drifted)
        assert _unacknowledged_drift(drifted, FILE_CASSETTES, MANIFEST) == []
        # Today's authored set matches today's prompt exactly (informational).
        assert drifted == {}

    def test_drift_checker_sensitivity(self):
        cassettes = {"r": {"provenance": "recorded"}, "a": {"provenance": "authored"}}
        drifted = {"r": ("old", "new"), "a": ("old", "new")}
        assert _unacknowledged_drift(drifted, cassettes,
                                     {"cassettes": {"r": {"drift": None}}}) == ["r"]
        assert _unacknowledged_drift(
            drifted, cassettes,
            {"cassettes": {"r": {"drift": {"acknowledged": "2026-09-18"}}}}) == []

    def test_the_census_walks_nested_test_modules(self):
        """SENSITIVITY for the walk itself: the census must see modules below
        the top level (tests/helpers/ exists today) and this very file."""
        names = {p.relative_to(TESTS_DIR).as_posix() for p in _test_sources()}
        assert "test_iq9_keyless_parser_gate.py" in names
        assert "conftest.py" in names
        assert "_parser_replay.py" in names
        assert any(n.startswith("helpers/") and n.endswith(".py") for n in names), names
        assert not any("__pycache__" in n for n in names)

    def test_no_test_imports_the_recorder(self):
        offenders = [p.name for p in _test_sources()
                     if _imports_recorder(p.read_text(encoding="utf-8-sig"))]
        assert offenders == []
        # sensitivity
        assert _imports_recorder("from tools.record_parser_cassettes import main\n")
        assert _imports_recorder("import tools.record_parser_cassettes as r\n")
        assert _imports_recorder("from tools import record_parser_cassettes\n")
        assert _imports_recorder(
            'importlib.import_module("tools.record_parser_cassettes")\n')
        assert not _imports_recorder("from tests._parser_replay import armed_parser\n")
        assert not _imports_recorder('doc = "see tools/record_parser_cassettes.py"\n')

    def test_no_test_builds_a_real_sdk_client_without_injection(self):
        offenders = {p.name: _bare_sdk_clients(p.read_text(encoding="utf-8-sig"))
                     for p in _test_sources()}
        offenders = {k: v for k, v in offenders.items() if v}
        assert offenders == {}
        # sensitivity
        assert _bare_sdk_clients('c = anthropic.Anthropic(api_key="k")\n') == [1]
        assert _bare_sdk_clients('c = Anthropic(api_key="k", max_retries=0)\n') == [1]
        assert _bare_sdk_clients(
            'c = anthropic.Anthropic(api_key="k", http_client=httpx.Client())\n') == []

    def test_replay_create_has_exactly_two_outcomes(self):
        with pytest.raises(ValueError):
            authored_cassette("x", UTT, "1805")                        # neither
        with pytest.raises(ValueError):
            authored_cassette("x", UTT, "1805", response=text_message("t"),
                              error="timeout")                         # both

    def test_the_fingerprint_is_provenance_not_a_key(self, parse_worlds):
        """Same utterance, two boots → identical prompt hash; one order in
        history → a different hash — so a hash could never key a cassette
        inside a campaign (recon §1.7, measured +355 chars)."""
        world_a, gs_a = fresh_world()
        world_b, gs_b = fresh_world()
        fps = []
        for world, gs in ((world_a, gs_a), (world_b, gs_b)):
            parser, replay = arm([_shape(tool_message(A_INPUT))])
            parse(parser, UTT, gs, world)
            fps.append(fingerprint(replay.calls[0])["prompt_sha256"])
        assert fps[0] == fps[1]
        world_b.add_to_command_history({"raw_input": "Ney, attack Mack",
                                        "marshal": "Ney", "action": "attack",
                                        "target": "Mack", "turn": 1})
        gs_b = build_llm_game_state(world_b)
        parser, replay = arm([_shape(tool_message(A_INPUT))])
        parse(parser, UTT, gs_b, world_b)
        assert fingerprint(replay.calls[0])["prompt_sha256"] != fps[0]
        assert utterance_of(replay.calls[0]) == UTT        # the key still resolves
