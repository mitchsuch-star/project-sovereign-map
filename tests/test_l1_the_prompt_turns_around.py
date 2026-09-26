"""L-1 — "The prompt turns around" (Score Mandate Chunk 3, SR-3c, September 26,
2026; contract = `docs/audits/LOCAL_PARSER_FEASIBILITY_2026_09_20.md` §4 L-1;
landing record = `docs/COMMAND_ROBUSTNESS_SPEC.md` §12.11).

Measured on the shipped 1805 boot before a line was written: two parse
prompts for the SAME order on boards one battle apart shared 84 characters —
the board (our marshals, the enemy, the per-marshal compass lines) sat at the
top, so nothing above the command could be reused. Up: rules, the output
contract and the board-independent examples FIRST, then the board, then the
order. Lever `prompt_builder.THE_PROMPT_IS_STATIC_FIRST`; down is the
pre-slice prompt byte for byte, which is how every IQ-9 parse cassette's
re-stamp is attributed (`tests/data/l1_prompt_restamp.json`).
"""
import contextlib
import io
import json
import random
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.ai.prompt_builder as PB
import backend.main as M
from backend.ai.parser_eval import build_llm_game_state
from backend.commands.executor import CommandExecutor
from backend.commands.parser import CommandParser
from tests._parser_replay import body_kind, cassette_key, fingerprint, utterance_of
import tests.test_iq9_keyless_parser_gate as IQ9

RESTAMP = json.loads((Path(__file__).parent / "data" / "l1_prompt_restamp.json")
                     .read_text(encoding="utf-8"))
SHARED_PREFIX_FLOOR = 14_000  # the contract's number, in characters


@pytest.fixture
def shipped(monkeypatch):
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    with contextlib.redirect_stdout(io.StringIO()):
        M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    return TestClient(M.app), M.world


def _prompt(world, utterance="Ney, attack Mack"):
    gs = build_llm_game_state(world)
    name, pers = PB.addressed_marshal(utterance, gs)
    return PB.build_parse_prompt(utterance, gs, marshal_name=name,
                                 personality=pers,
                                 command_history=world.get_command_history_for_prompt())


def _shared(a, b):
    n = 0
    for x, y in zip(a, b):
        if x != y:
            break
        n += 1
    return n


def _one_battle(world):
    random.seed(1805)
    with contextlib.redirect_stdout(io.StringIO()):
        CommandExecutor().execute(
            {"command": {"marshal": "Ney", "action": "attack", "target": "Mack",
                         "type": "specific", "_muster_confirmed": True}},
            {"world": world})


class TestTheStaticPrefixIsShared:
    def test_one_battle_apart(self, shipped):
        client, world = shipped
        before = _prompt(world)
        _one_battle(world)
        with contextlib.redirect_stdout(io.StringIO()):
            client.post("/command", json={"command": "end turn"})
        after = _prompt(world)
        assert _shared(before, after) >= SHARED_PREFIX_FLOOR, _shared(before, after)

    def test_over_eight_turns_of_play(self, shipped):
        """The examples once named the first VISIBLE enemy and his CURRENT
        province, so the prefix fell to 13,280 on turn 3 and 12,199 on turn
        8 of the ambient board; the static examples are board-independent."""
        client, world = shipped
        base = _prompt(world)
        for _ in range(8):
            with contextlib.redirect_stdout(io.StringIO()):
                client.post("/command", json={"command": "end turn"})
            shared = _shared(base, _prompt(world))
            assert shared >= SHARED_PREFIX_FLOOR, (int(world.current_turn), shared)

    def test_different_orders_share_it_too(self, shipped):
        _, world = shipped
        a = _prompt(world, "Ney, attack Mack")
        b = _prompt(world, "march north")
        assert _shared(a, b) >= SHARED_PREFIX_FLOOR

    def test_the_lever_down_shares_almost_nothing(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(PB, "THE_PROMPT_IS_STATIC_FIRST", False)
        before = _prompt(world)
        _one_battle(world)
        assert _shared(before, _prompt(world)) < 1_000


class TestTheOrderOfTheSections:
    def test_rules_then_examples_then_board_then_order(self, shipped):
        _, world = shipped
        p = _prompt(world)
        order = ["## Valid Actions", "## Output", "## Examples\n",
                 "## Your Marshals", "## Enemy Forces", "## Map Orientation",
                 "## Command to Parse"]
        at = [p.find(h) for h in order]
        assert all(i >= 0 for i in at), dict(zip(order, at))
        assert at == sorted(at), dict(zip(order, at))
        assert p.rstrip().endswith("Respond only with the tool call — no prose.")

    def test_the_personality_rule_points_below(self, shipped):
        _, world = shipped
        p = _prompt(world)
        assert 'under "Your Marshals"\nbelow)' in p
        assert 'under "Your Marshals"\nabove)' not in p

    def test_the_geography_rides_the_board(self, shipped):
        _, world = shipped
        p = _prompt(world)
        rules = p[:p.find("## Your Marshals")]
        assert "Map orientation: each marshal's adjacent regions" in rules
        board = p[p.find("## Map Orientation"):p.find("## Command to Parse")]
        assert "Ney" in board


class TestTheAddressee:
    def test_an_addressed_order_names_its_marshal(self, shipped):
        _, world = shipped
        p = _prompt(world, "Ney, deal with Mack")
        assert "## The Order Is Addressed To\nNey (aggressive)" in p
        assert p.find("## Your Marshals") < p.find("## The Order Is Addressed To")

    def test_an_unaddressed_order_names_nobody(self, shipped):
        _, world = shipped
        assert "## The Order Is Addressed To" not in _prompt(world, "march north")

    def test_the_request_carries_it(self):
        """The providers pass the addressee — read off the request body the
        replay actually received, not off the builder."""
        world, gs = IQ9.fresh_world("1805")
        parser, replay = IQ9.arm(list(IQ9.FILE_CASSETTES.values()), "1805",
                                 IQ9.MANIFEST)
        IQ9.parse(parser, "Ney, deal with Mack", gs, world)
        bodies = [b for b in replay.calls if body_kind(b) == "parse"]
        assert bodies
        assert "## The Order Is Addressed To\nNey (" in bodies[0]["messages"][0]["content"]


class TestTheExamplesAreHonest:
    def test_the_static_examples_name_no_enemy_commander(self, shipped):
        _, world = shipped
        p = _prompt(world)
        static = p[p.find("## Examples\n"):p.find("## Your Marshals")]
        foes = [m.name for m in world.marshals.values()
                if m.nation != world.player_nation]
        for foe in foes:
            assert f'"{foe}"' not in static and f" {foe}\"" not in static, foe

    def test_the_board_examples_name_only_a_foe_in_view(self, shipped):
        _, world = shipped
        gs = build_llm_game_state(world)
        p = _prompt(world)
        board = p[p.find("## Examples on This Board"):p.find("## Command to Parse")]
        assert board.startswith("## Examples on This Board")
        in_view = set(gs["enemies"])
        named = {m.name for m in world.marshals.values()
                 if m.nation != world.player_nation and m.name in board}
        assert named and named <= in_view, (named, in_view)

    def test_each_template_is_taught_once(self, shipped):
        """The split never teaches a template twice — "attack the enemy" ->
        generic in the rules AND "attack Deroy" -> Deroy on the board would be
        two contradictory lessons from one template."""
        _, world = shipped
        p = _prompt(world)
        static = p[p.find("## Examples\n"):p.find("## Your Marshals")]
        board = p[p.find("## Examples on This Board"):p.find("## Command to Parse")]

        def lines(block):
            return sum(1 for line in block.splitlines()
                       if line[:1].isdigit() and '. "' in line)
        assert lines(static) + lines(board) == len(PB.FEW_SHOT_TEMPLATES)
        assert lines(board) == sum(1 for t in PB.FEW_SHOT_TEMPLATES
                                   if PB._names_an_enemy(t))


class TestTheCassetteAttribution:
    """Every re-stamped parse cassette: the lever DOWN reproduces the
    fingerprint the cassette carried before the slice, the lever UP the one it
    carries now — so the re-stamp is this reorder and nothing else."""

    @pytest.mark.parametrize("cid", sorted(RESTAMP))
    def test_both_arms(self, cid, monkeypatch):
        entry = IQ9.FILE_CASSETTES[cid]
        rec = RESTAMP[cid]
        assert entry["request"]["prompt_sha256"] == rec["static_first_sha256"]
        for lever, want_sha, want_chars in (
                (False, rec["recorded_sha256"], rec["recorded_chars"]),
                (True, rec["static_first_sha256"], rec["static_first_chars"])):
            monkeypatch.setattr(PB, "THE_PROMPT_IS_STATIC_FIRST", lever)
            world, gs = IQ9.fresh_world(entry["world"])
            parser, replay = IQ9.arm(list(IQ9.FILE_CASSETTES.values()),
                                     entry["world"], IQ9.MANIFEST)
            IQ9.parse(parser, entry["utterance"], gs, world)
            key = cassette_key(entry)
            fps = [fingerprint(b) for b in replay.calls
                   if (body_kind(b), utterance_of(b), entry["world"]) == key]
            assert fps, cid
            assert fps[0]["prompt_sha256"] == want_sha, (cid, lever)
            assert fps[0]["prompt_chars"] == want_chars, (cid, lever)
