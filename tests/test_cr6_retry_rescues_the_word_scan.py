"""IQ9-X1 + IQ9-X3 — the live road's two riders (Score Mandate Chunk 3, SR-3c,
September 26, 2026; homed to L-1 by the CR-6 triage, `COMMAND_ROBUSTNESS_SPEC.md`
§12; landing record §12.11). Every pin runs keyless on the IQ-9 replay.

IQ9-X1, reproduced before a line was written: `hunt down mack` — the fast
pass's marshal WORD SCAN read "down" as a typo of Davout; CR-2's one live
retry answered correctly (no marshal named, pursue Mack), and the retry's own
fuzzy pass re-ran the same word scan, so the live call was spent and
discarded and the player was asked "Did you mean Davout?". Lever
`parser.THE_RETRY_READS_THE_MARSHAL`.

IQ9-X3: a parser failure carried no `mode`, so a request that DID make a live
call was stamped `parse_mode: "mock"`. Lever `parser.A_FAILURE_NAMES_ITS_ROAD`
+ the transient `ParseResult.live_consulted` marker.
"""
import pytest

import backend.commands.parser as P
from backend.ai.schemas import ParseResult
from tests.test_iq9_keyless_parser_gate import (  # noqa: F401 — fixtures
    FILE_CASSETTES, MANIFEST, RETRY_UTT, arm, endpoint, fresh_world, parse,
    parse_worlds)


class TestTheRetryReadsTheMarshal:
    def test_the_retried_parse_is_adopted(self, parse_worlds):
        world, gs = parse_worlds["1805"]
        parser, replay = arm(list(FILE_CASSETTES.values()), "1805", MANIFEST)
        r = parse(parser, RETRY_UTT, gs, world)
        assert len(replay.calls) == 1
        assert r["success"] is True, r.get("error")
        command = r["command"]
        assert command.get("marshal") is None
        assert command.get("target") == "Mack"
        assert "down" not in str(r.get("error") or "")

    def test_at_the_wire_it_is_the_plain_pursue(self, endpoint):
        """The adopted reading gives the player what the fast road gives the
        unambiguous phrasing — `pursue mack` hands the pursuit to the same
        marshal — never a question about a name nobody typed."""
        endpoint(FILE_CASSETTES.values())
        hunted = endpoint.post(RETRY_UTT)
        endpoint(FILE_CASSETTES.values())
        plain = endpoint.post("pursue mack")
        for data in (hunted, plain):
            assert "pursues Mack" in str(data.get("message")), data.get("message")
        assert "Davout?" not in str(hunted.get("message"))
        pursuer = str(plain.get("message")).split(" pursues")[0]
        assert str(hunted.get("message")).startswith(pursuer)

    def test_a_named_marshal_is_still_validated(self, parse_worlds):
        world, gs = parse_worlds["1805"]
        parser, _ = arm(list(FILE_CASSETTES.values()), "1805", MANIFEST)
        _, error = parser._apply_fuzzy_matching(
            {"action": "attack", "marshal": "Zorglub", "target": "Mack",
             "mode": "anthropic"},
            RETRY_UTT, world=world, game_state=gs, trust_marshal_reading=True)
        assert error is not None and "Zorglub" in str(error.get("error")), error

    def test_the_primary_road_still_scans(self, parse_worlds):
        world, gs = parse_worlds["1805"]
        parser, _ = arm(list(FILE_CASSETTES.values()), "1805", MANIFEST)
        _, error = parser._apply_fuzzy_matching(
            {"action": "attack", "marshal": None, "target": "Mack", "mode": "mock"},
            RETRY_UTT, world=world, game_state=gs)
        assert error is not None and "'down' not found" in error["error"]

    def test_the_lever_down_discards_the_retry(self, parse_worlds, monkeypatch):
        monkeypatch.setattr(P, "THE_RETRY_READS_THE_MARSHAL", False)
        world, gs = parse_worlds["1805"]
        parser, replay = arm(list(FILE_CASSETTES.values()), "1805", MANIFEST)
        r = parse(parser, RETRY_UTT, gs, world)
        assert len(replay.calls) == 1
        assert r["success"] is False and "'down' not found" in r["error"]


class TestAFailureNamesItsRoad:
    def test_a_live_failure_names_the_live_road(self, endpoint):
        world, replay = endpoint(FILE_CASSETTES.values())
        data = endpoint.post("flurble the wibble")
        assert replay.call_kinds()[:1] == ["parse"]
        assert data["parse_mode"] == "anthropic"

    def test_a_discarded_retry_names_the_live_road(self, parse_worlds, monkeypatch):
        monkeypatch.setattr(P, "THE_RETRY_READS_THE_MARSHAL", False)
        world, gs = parse_worlds["1805"]
        parser, replay = arm(list(FILE_CASSETTES.values()), "1805", MANIFEST)
        r = parse(parser, RETRY_UTT, gs, world)
        assert len(replay.calls) == 1 and r["success"] is False
        assert r["mode"] == "anthropic"

    def test_an_offline_failure_stays_mock(self, parse_worlds):
        """A condition the engine refuses (CR-7-4) is read by the fast parser
        alone — no live call, so the road is the offline one."""
        world, gs = parse_worlds["1805"]
        parser, replay = arm(list(FILE_CASSETTES.values()), "1805", MANIFEST)
        r = parse(parser, "Ney, hold Rhineland until Godot arrives", gs, world)
        assert replay.calls == []
        assert r["success"] is False and r.get("refusal") == "condition", r
        assert r["mode"] == "mock"

    def test_the_marker_rides_the_dict_only_when_set(self):
        assert "live_consulted" not in ParseResult().to_dict()
        marked = ParseResult(live_consulted=True).to_dict()
        assert marked["live_consulted"] is True
        assert ParseResult.from_dict(marked).live_consulted is True

    def test_the_lever_down_leaves_the_failure_bare(self, endpoint, monkeypatch):
        monkeypatch.setattr(P, "A_FAILURE_NAMES_ITS_ROAD", False)
        endpoint(FILE_CASSETTES.values())
        data = endpoint.post("flurble the wibble")
        assert data["parse_mode"] == "mock"


@pytest.mark.parametrize("lever", [True, False])
def test_the_success_road_is_unchanged(parse_worlds, lever, monkeypatch):
    """A successful fast parse still names whose reading it acts on."""
    monkeypatch.setattr(P, "A_FAILURE_NAMES_ITS_ROAD", lever)
    world, gs = parse_worlds["1805"]
    parser, replay = arm(list(FILE_CASSETTES.values()), "1805", MANIFEST)
    r = parse(parser, "Ney, attack Mack", gs, world)
    assert replay.calls == [] and r["success"] is True
    assert r.get("mode", "mock") == "mock"


class TestTheFallbackIsMarked:
    """Both of the client's fallbacks after a live answer mark the offline
    reading as live-consulted, and keep its mode "mock" (whose reading it
    is — CR-5's guardrail (e) reads the mode)."""

    @staticmethod
    def _client(answer):
        from backend.ai.llm_client import LLMClient

        class Stub:
            def parse(self, text, game_state):
                return answer

        client = LLMClient()
        client.provider = Stub()
        return client

    def test_an_unmatched_live_answer(self):
        _, gs = fresh_world("1805")
        fast = ParseResult(action="attack", target="Mack", mode="mock")
        client = self._client(ParseResult(matched=False, mode="anthropic"))
        out = client._parse_with_live_provider("flurble the wibble", gs, fast)
        assert out is fast and out.live_consulted is True and out.mode == "mock"

    def test_a_live_answer_that_fails_validation(self):
        _, gs = fresh_world("1805")
        fast = ParseResult(action="attack", target="Mack", mode="mock")
        client = self._client(ParseResult(matched=True, action="attack",
                                          marshals=["Zorglub"], target="Mack",
                                          mode="anthropic"))
        out = client._parse_with_live_provider("Zorglub, attack Mack", gs, fast)
        assert out is fast and out.live_consulted is True and out.mode == "mock"
