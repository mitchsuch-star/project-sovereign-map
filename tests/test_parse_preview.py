"""UI-6 "The readback" — `GET /parse_preview` (Session UI-6, November 13,
2026; the contract is `backend/commands/parse_preview.py`'s docstring and
`docs/SYSTEMS_REFERENCE.md` §217).

How a typed line WOULD be read, before Enter — and nothing else: it never
executes, never spends an action, never writes history, a popup or a trace,
never draws from `random`, never calls the model, and it keeps the game's fog
doctrine (`llm_client._askable_enemy_names`): a commander out of sight is read
by name and side exactly as `/command` reads him, and nothing of where he
stands or what he fields ever rides a reading. The heavier `/command` census
rides `tests/test_parse_preview_vs_command.py` (a separate module, so the
parallel lanes place the two apart) — fogged-name lines included.

Pins:
  (a) parity — the reading names the marshal and the action the live parse
      names, over the golden corpus (1805 + any), lines naming a man out of
      sight included, the deliberate voids (a standing question, the
      secretary) counted and capped;
  (b) zero side effects — the board byte for byte, the pools, the history,
      `random`, the trace, the provenance, the dialogue queue, every
      pending field; the model is never called, and a line the LIVE client
      would hand it reads "secretary";
  (c) the doctrine — a man out of sight is answered by name and court (the
      enemy-addressee refusal, "no intelligence on his position"), and no
      reading carries his province, his strength or any figure of his corps
      (13 templates × the fogged names), nor a roster key (R7);
  (d) Golden Rule 2 — no float anywhere;
  (e) the cost — the parse state built once per state epoch (Rule 8), the
      warm reading fast, the lock serialising readers, "busy" under a POST.

UI-6's first wave read a hidden name exactly as an invented one (A12's
strict gate); the lead's ruling of November 13, 2026 restored the doctrine,
and (c) was re-pointed from "a hidden name reads as a name on no roster" to
"his name and side are public, his place never is".
"""

import contextlib
import io
import json
import random
import re
import statistics
import threading
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.ai import parse_trace as _ptrace
from backend.commands import parse_preview as PP
from backend.commands.parser import CommandParser
from backend.display_names import humanize_entity_name
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
CORPUS = REPO / "tests" / "data" / "parser_golden_corpus.json"


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture(scope="module")
def board():
    """The shipped 1805 board behind the real app, a mock parser, and the
    board's own snapshot (each pin installs a fresh copy)."""
    mp = pytest.MonkeyPatch()
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        mp.delenv(key, raising=False)
    mp.setenv("LLM_MODE", "mock")
    prior = (M.world, M.game_state.get("world"), M.parser)
    with _quiet():
        M._reset_world_state()
        M.parser = CommandParser(use_real_llm=False)
    snap = json.dumps(M.world.to_dict(), default=str)
    PP.invalidate()
    try:
        # one portal for the module (a `with` block): a bare TestClient opens a fresh
        # event loop and socket pair per request, and the censuses post thousands
        # of lines (WinError 10055 under the hook's parallel load)
        with TestClient(M.app) as client:
            yield client, snap
    finally:
        M.world, M.parser = prior[0], prior[2]
        M.game_state["world"] = prior[1]
        PP.invalidate()
        mp.undo()


def _fresh(snap, without=None):
    """Install a fresh copy of the board (optionally with one marshal on no
    roster at all) and return it."""
    with _quiet():
        world = WorldState.from_dict(json.loads(snap))
        if without:
            world.marshals.pop(without, None)
            world._build_marshal_index()
            world.calculate_visibility()
        M._set_active_world(world)
        M.parser = CommandParser(use_real_llm=False)
    PP.invalidate()
    return world


def pv(client, line):
    with _quiet():
        return client.get("/parse_preview", params={"line": line}).json()


def _hidden_names(world, limit=4):
    from backend.game_logic.intel_surfaces import in_sight
    names = [m.name for m in world.marshals.values()
             if m.nation != world.player_nation and m.strength > 0
             and not in_sight(world, world.player_nation, m)]
    preferred = [n for n in ("Kutuzov", "ArchdukeCharles", "Moore", "Buxhowden", "Hohenlohe")
                 if n in names]
    return (preferred + [n for n in names if n not in preferred])[:limit]


def _without_epoch(reading):
    return {k: v for k, v in reading.items() if k != "epoch"}


# ═══════════════════════════════════════════════════════════════════════
# (a) parity with the live parse over the golden corpus
# ═══════════════════════════════════════════════════════════════════════

def _reference(world, text):
    """What `/command`'s own pure stages read for `text` (carryover, the
    lost-marshal guard, the premise, the parse) — "refused" or the parse."""
    from backend.ai.condition_grammar import premise_refusal, split_premise
    from backend.commands.context_carryover import resolve_context_references
    carry = resolve_context_references(text, world)
    if carry.get("kind") == "error":
        return "refused"
    reading = carry["command"] if carry.get("kind") == "rewrite" else text
    if M._addressed_lost_marshal_refusal(reading, world):
        return "refused"
    player = world.player_nation
    reading, premise = split_premise(
        reading, [m.name for m in world.marshals.values() if m.nation != player],
        list(world.regions.keys()),
        [m.name for m in world.marshals.values() if m.nation == player])
    if premise and premise_refusal(world, premise):
        return "refused"
    with _quiet():
        return M.parser.parse(reading, M.get_llm_game_state(), world=world)


class TestParity:

    def test_the_reading_names_what_the_live_parse_names(self, board):
        client, snap = board
        world = _fresh(snap)
        corpus = json.loads(CORPUS.read_text(encoding="utf-8"))["entries"]
        entries = sorted((e for e in corpus if e.get("world") in ("1805", "any")),
                         key=lambda e: e["id"])[::4]   # a fixed quarter: the budget (measured)
        compared = skipped = 0
        mismatches = []
        for entry in entries:
            line = entry["utterance"]
            pre = pv(client, line)
            # A line naming a man out of sight is read as /command reads it
            # (the doctrine) — compared like any other line, never skipped.
            if pre["kind"] in ("pending", "secretary", "busy"):
                skipped += 1
                continue
            ref = _reference(world, line)
            compared += 1
            if ref == "refused":
                if pre["kind"] != "refusal":
                    mismatches.append((line, "refused", pre["kind"]))
                continue
            cmd = ref.get("command") or {}
            own = cmd.get("marshal") in {m.name for m in world.get_player_marshals()}
            if ref.get("success") and own:
                if pre["kind"] not in ("order", "refusal", "unknown_name", "delegation"):
                    mismatches.append((line, "order", pre["kind"]))
                elif pre["kind"] == "order" and pre.get("directive"):
                    # Row IC: a line to several corps ("Ney and Davout fortify")
                    # reads as the list it will open — it names every man, so
                    # no ONE marshal is its reading; the order must still be
                    # the parse's own.
                    if pre["action"] != cmd.get("action"):
                        mismatches.append((line, cmd.get("action"), pre["action"]))
                elif pre["kind"] == "order" and isinstance(ref.get("own"), dict):
                    # Row IC, Session 3b: a TASK ON HIS OWN ("Ney, hold Rhineland
                    # carefully") reads as its man and the task's verb — its
                    # `action` is blank by design since Session 3 (the order is the
                    # task, not the plain hold the parse rides on). The sampled
                    # quarter never held such a line until this session's five
                    # golden rows moved it; the reading must still name the man
                    # and a verb.
                    if pre["marshal"] != humanize_entity_name(cmd["marshal"]) or not pre.get("verb"):
                        mismatches.append((line, cmd.get("marshal"), "a task on his own",
                                           pre["marshal"], pre.get("verb")))
                elif pre["kind"] == "order" and (
                        pre["marshal"] != humanize_entity_name(cmd["marshal"])
                        or pre["action"] != cmd.get("action")):
                    mismatches.append((line, cmd.get("marshal"), cmd.get("action"),
                                       pre["marshal"], pre["action"]))
            elif ref.get("success") and isinstance(cmd.get("question"), dict):
                if pre["kind"] not in ("question", "delegation"):
                    mismatches.append((line, "question", pre["kind"]))
            elif not ref.get("success") and ref.get("refusal"):
                if pre["kind"] not in ("refusal", "delegation"):
                    mismatches.append((line, "parse refusal", pre["kind"]))
            elif not ref.get("success") and ref.get("unknown_name") and \
                    ref.get("kind") in ("marshal_not_found", "marshal_suggest"):
                if pre["kind"] != "unknown_name":
                    mismatches.append((line, "unknown name", pre["kind"]))
        assert compared > 130, compared
        # The deliberate voids (a standing question, the secretary) stay few,
        # so the skip list can never hide drift.
        assert skipped <= 12, skipped
        assert mismatches == [], mismatches[:12]


# ═══════════════════════════════════════════════════════════════════════
# (b) zero side effects; the model is never called
# ═══════════════════════════════════════════════════════════════════════

SIDE_EFFECT_LINES = [
    "Ney, attack Mack", "Davout, fortify", "Ney, march to Vienna", "Soult, deal with Mack",
    "where is Mack", "what if Ney attacks Mack", "what can I do", "status", "help",
    "end turn", "everyone fortify", "all marshals march to Swabia",
    "Ney, march to Swabia then attack Mack", "Ney, follow Davout", "Ney, hold",
    "Ney, atack Mack", "Nye, attack Mack", "Kutuzov, attack Mack", "Zorglub, attack Mack",
    "Ney, attack Kutuzov", "if Mack is still in Swabia, attack him",
    "if Kutuzov is still in Swabia, attack him", "improve relations with Prussia",
    "recruit infantry in Paris", "why", "again", "Ney, attack him",
    "Ney, attack Mack and then fortify", "Ney, retreat", "Ney, never attack Mack",
    "Lannes, scout Swabia", "Murat, attack Mack", "Ney, pursue Mack",
    "Davout, hold Lorraine until Kutuzov arrives", "Ney, garrison",
    "Davout, drill", "Ney, defend", "Soult, support Davout", "everyone stop",
    "Ney, go and sort out that mess",
]


def _board_fingerprint(world):
    dm = world.dialogue_manager
    return {
        "board": json.dumps(world.to_dict(), sort_keys=True, default=str),
        "military": int(world.actions_remaining),
        "admin": int(world.admin_actions_remaining),
        "history": len(world.command_history),
        "trace": json.dumps(getattr(world, "_last_parse_trace", None), sort_keys=True, default=str),
        "dialogue": (json.dumps(dm.peek(), sort_keys=True, default=str), len(dm.iter_queue())),
        "pending": {k: json.dumps(getattr(world, k, None), sort_keys=True, default=str)
                    for k in ("pending_objection", "pending_strategic_objection",
                              "pending_capture_choice", "pending_diplomatic_dialogue")},
        "interrupts": [json.dumps(getattr(m, "pending_interrupt", None), default=str)
                       for m in world.get_player_marshals()],
    }


class TestZeroSideEffects:

    def test_the_preview_parser_is_mock_only_and_its_own(self, board):
        parser = PP._preview_parser()
        assert parser.llm.provider_name == "mock"
        assert isinstance(parser.llm, PP._PreviewLLM)
        assert parser is not M.parser

    def test_forty_readings_change_nothing(self, board, monkeypatch):
        from backend.ai.llm_client import LLMClient
        client, snap = board
        world = _fresh(snap)
        with _quiet():   # one order on the record, so "again" has something to read
            client.post("/command", json={"command": "Davout, fortify"})
        # The LIVE client looks live; any call into a provider is a failure.
        M.parser.llm.provider_name = "anthropic"
        M.parser.llm.api_key = "sk-test"

        def _never(*_a, **_k):
            raise AssertionError("the readback called the model")
        monkeypatch.setattr(LLMClient, "_parse_with_live_provider", _never)
        before = _board_fingerprint(world)
        rng = random.getstate()
        readings = [pv(client, line) for line in SIDE_EFFECT_LINES]
        assert random.getstate() == rng, "the readback drew from random"
        assert _board_fingerprint(world) == before
        assert _ptrace.current() is None and _ptrace.rows() == []
        assert M._PARSE_PROVENANCE.get(None) is None
        assert all(r["success"] is True for r in readings)
        kinds = {r["line"]: r["kind"] for r in readings}
        # the low-confidence line is the LIVE model's — the readback says so
        # and quotes nothing; a confident one is read as usual
        vague = "Ney, go and sort out that mess"
        assert kinds[vague] == "secretary", kinds[vague]
        secretary = next(r for r in readings if r["line"] == vague)
        assert secretary["would_consult_llm"] is True
        assert secretary["marshal"] == "" and secretary["ap"] == 0
        assert kinds["Davout, fortify"] in ("order", "refusal")

    def test_a_mock_game_never_reads_secretary(self, board):
        client, snap = board
        _fresh(snap)
        for line in SIDE_EFFECT_LINES:
            assert pv(client, line)["kind"] != "secretary", line

    def test_a_standing_question_is_detected_never_answered(self, board):
        client, snap = board
        world = _fresh(snap)
        with _quiet():
            asked = client.post("/command", json={"command": "Zorglub, attack Mack"}).json()
        assert asked.get("state") == "awaiting_clarification", asked.get("message")
        top = json.dumps(world.dialogue_manager.peek(), sort_keys=True, default=str)
        reading = pv(client, "1")
        assert reading["kind"] == "pending", reading
        assert json.dumps(world.dialogue_manager.peek(), sort_keys=True, default=str) == top


# ═══════════════════════════════════════════════════════════════════════
# (c) the doctrine: his name and side are public, his place never is
# ═══════════════════════════════════════════════════════════════════════

FOG_TEMPLATES = [
    "Ney, attack {X}", "Ney, pursue {X}", "Ney, march to Vienna then attack {X}",
    "{X}, attack Mack", "{X} retreat", "Ney, attack {T}", "what if Ney attacks {X}",
    "where is {X}", "if {X} is still in Swabia, attack him", "Ney, deal with {X}",
    "Ney, support {X}", "Attack Marshal {X}", "Davout, hold Lorraine until {X} arrives",
    # A15 (UI6-X14 … X20): the delegation's other arms, the marshal-less
    # attack and scout, the hold, the follow and the charge
    "Bernadotte, deal with {X}", "Soult, deal with {X}", "everyone attack {X}",
    "Davout, hold {X}", "Ney, follow {X}", "scout {X}", "Murat, charge {X}",
]


def _typo(word):
    """One letter changed at the end — a near miss of the same shape."""
    return word[:-1] + ("q" if word[-1].lower() != "q" else "z")


def _figures(man):
    """Every way a reading could print where he stands or what he fields."""
    strength = int(man.strength)
    return {man.location, humanize_entity_name(man.location), str(strength),
            f"{strength:,}", f"{strength // 1000}k", f"{strength // 1000},000"}


class TestTheDoctrine:

    @pytest.fixture(scope="class")
    def hidden(self, board):
        _client, snap = board
        world = _fresh(snap)
        names = _hidden_names(world)
        assert len(names) >= 3, names
        return names

    def test_no_place_strength_or_figure_of_a_man_out_of_sight_rides_a_reading(self, board, hidden):
        """(a) Twenty shapes of line × the fogged commanders: no reading
        carries his province, his strength or a figure of his corps — nor
        his roster key (R7) — and no candidate the reading offers is a man
        the player cannot see. His name and his court may ride (the
        doctrine); `target_place` is set only for a man in sight."""
        client, snap = board
        for name in hidden:
            world = _fresh(snap)
            man = world.marshals[name]
            shown = humanize_entity_name(name)
            leaks = set(_figures(man))
            if shown != name:
                leaks.add(name)          # the roster key, never the player's word
            pool = ({humanize_entity_name(m.name) for m in world.get_player_marshals()}
                    | {humanize_entity_name(m.name) for m in world.get_visible_enemies(world.player_nation)}
                    | {humanize_entity_name(m.name) for m in world.get_enemy_marshals()
                       if m.name not in hidden}
                    | set(world.regions))
            for template in FOG_TEMPLATES:
                line = template.format(X=shown, T=_typo(shown))
                reading = pv(client, line)
                body = json.dumps({k: v for k, v in reading.items() if k != "line"})
                for leak in leaks:
                    assert leak not in body, (line, leak, reading)
                assert reading["target_place"] == "", (line, reading)
                for cand in reading["candidates"]:
                    assert cand["label"] in pool, (line, cand)

    def test_the_reading_names_him_as_command_does(self, board, hidden):
        """The doctrine's own answers, in the readback's short words: the
        enemy addressee is refused by name and court; an attack, a pursuit
        or a delegation on him finds no intelligence on his position; a
        support is told whose man he is. Every one free."""
        client, snap = board
        world = _fresh(snap)
        from backend.game_logic.formations import formed_display_name
        for name in hidden:
            shown = humanize_entity_name(name)
            court = formed_display_name(world, world.marshals[name].nation)
            expect = {
                f"{shown}, attack Mack": f"{shown} serves {court} — he does not answer to us",
                f"{shown} retreat": f"{shown} serves {court} — he does not answer to us",
                f"Ney, attack {shown}": f"No intelligence on {shown}’s position",
                f"Ney, pursue {shown}": f"No intelligence on {shown}’s position",
                f"Ney, deal with {shown}": f"No intelligence on {shown}’s position",
                # UI6-X14 (A15): the cautious and the literal arms too
                f"Bernadotte, deal with {shown}": f"No intelligence on {shown}’s position",
                f"Soult, deal with {shown}": f"No intelligence on {shown}’s position",
                # UI6-X15 (A15): the marshal-less attack
                f"everyone attack {shown}": f"No intelligence on {shown}’s position",
                f"Ney, support {shown}": f"{shown} serves {court} — pursue him, not support",
            }
            for line, words in expect.items():
                reading = pv(client, line)
                assert reading["kind"] == "refusal", (line, reading)
                assert words in reading["refusal"], (line, reading["refusal"])
                assert reading["ap"] == 0 and reading["parts"][-1]["text"] == "free refusal", reading
            # a slip of his name asks in the player's own word (CRT-2's seam)
            reading = pv(client, f"Ney, attack {_typo(shown)}")
            assert reading["kind"] == "unknown_name", reading
            assert reading["unknown"] == _typo(shown), reading
            assert shown not in json.dumps(reading), reading

    def test_a_visible_foe_shows_his_place_and_a_fogged_one_does_not(self, board):
        client, snap = board
        world = _fresh(snap)
        reading = pv(client, "Ney, attack Mack")
        assert reading["kind"] == "order" and reading["target_place"] == "Swabia", reading
        # Stage Mack out of sight: he is still named — no place, no price.
        mack = world.marshals["Mack"]
        from backend.models.intel import PARTIAL
        unseen = next(r for r in world.regions
                      if not world.get_region_intel(r).visibility_at_least(PARTIAL))
        mack.location = unseen
        with _quiet():
            world._build_marshal_index()
            world.calculate_visibility()
        PP.invalidate()
        reading = pv(client, "Ney, attack Mack")
        assert reading["kind"] == "refusal", reading
        assert "No intelligence on Mack’s position" in reading["refusal"], reading
        assert reading["target"] == "Mack" and reading["target_place"] == "", reading
        assert unseen not in json.dumps(reading)

    def test_a_sighting_on_the_record_is_priced_never_placed(self, board):
        """Out of sight now, seen before: the chase follows his last sighting
        (`strategic.pursue_known_location`, the executors' one rule) — the
        reading prices it and never says where."""
        client, snap = board
        world = _fresh(snap)
        mack = world.marshals["Mack"]
        from backend.models.intel import PARTIAL
        unseen = next(r for r in world.regions
                      if not world.get_region_intel(r).visibility_at_least(PARTIAL)
                      and r != mack.location)
        mack.location = unseen
        with _quiet():
            world._build_marshal_index()
            world.calculate_visibility()
        PP.invalidate()
        from backend.commands import strategic
        from unittest import mock
        with mock.patch.object(strategic, "pursue_known_location", return_value="Swabia"):
            reading = pv(client, "Ney, pursue Mack")
            ask = pv(client, "Ney, attack Mack")
        assert reading["kind"] == "order" and reading["ap"] >= 1, reading
        assert ask["kind"] == "order" and ask["asks_first"] is True, ask
        for r in (reading, ask):
            body = json.dumps(r)
            assert unseen not in body and "Swabia" not in body, r
            assert r["target_place"] == "" and r["turns"] == 0, r

    def test_the_premise_is_refused_without_his_place(self, board, hidden):
        client, snap = board
        for name in hidden:
            world = _fresh(snap)
            shown = humanize_entity_name(name)
            reading = pv(client, f"if {shown} is still in Swabia, attack him")
            assert reading["kind"] == "refusal", reading
            assert world.marshals[name].location not in json.dumps(reading), reading

    def test_the_readings_the_census_found_drifting(self, board):
        """The doctrine pass's own census finds (A14, November 13, 2026): each
        line below read as a priced ORDER while `/command` refused it free —
        a commander is no province ("Mack is a commander, Sire, not a
        province", "Region 'Davout' not found"), a delegation is no war
        ("We are not at war with Prussia"), and a slip of a fogged name is
        asked in the player's own word, never spelled out."""
        client, snap = board
        _fresh(snap)
        for line, words in (
                ("Ney, move to Mack", "Mack is a commander — name a province"),
                ("Ney, scout Mack", "Mack is a commander — name a province"),
                ("Ney, move to Davout", "Davout is a commander — name a province"),
                ("Ney, scout Kutuzov", "Kutuzov is a commander — name a province"),
                ("Ney, deal with Brunswick", "We are not at war with Prussia")):
            reading = pv(client, line)
            assert reading["kind"] == "refusal" and words in reading["refusal"], (line, reading)
            assert reading["ap"] == 0, (line, reading)
        reading = pv(client, "Ney, attack Kutuzoq")
        assert reading["kind"] == "unknown_name" and reading["unknown"] == "Kutuzoq", reading
        assert "Kutuzov" not in json.dumps(reading), reading

    def test_mentions_hidden_name_is_the_fog_oracle(self, board, hidden):
        """The history filter's oracle (UI6-X1): a line naming a man out of
        sight is never offered back from history."""
        _client, snap = board
        world = _fresh(snap)
        for name in hidden:
            assert PP.mentions_hidden_name(world, f"Ney, attack {humanize_entity_name(name)}")
            assert PP.mentions_hidden_name(world, f"ney, attack {name.lower()}")
        assert not PP.mentions_hidden_name(world, "Ney, attack Mack")
        assert not PP.mentions_hidden_name(world, "Zorglub, attack Mack")


# ═══════════════════════════════════════════════════════════════════════
# (d) Golden Rule 2 — no float reaches the client
# ═══════════════════════════════════════════════════════════════════════

def _floats(value, path="$"):
    if isinstance(value, bool):
        return []
    if isinstance(value, float):
        return [path]
    if isinstance(value, dict):
        return [p for k, v in value.items() for p in _floats(v, f"{path}.{k}")]
    if isinstance(value, list):
        return [p for i, v in enumerate(value) for p in _floats(v, f"{path}[{i}]")]
    assert isinstance(value, (int, str)) or value is None, (path, type(value))
    return []


class TestRuleTwo:

    def test_no_float_anywhere(self, board):
        client, snap = board
        _fresh(snap)
        for line in SIDE_EFFECT_LINES[:30]:
            reading = pv(client, line)
            assert _floats(reading) == [], (line, _floats(reading))
            for key in ("ap", "ap_left", "turns", "epoch"):
                assert type(reading[key]) is int, (line, key)


# ═══════════════════════════════════════════════════════════════════════
# (e) the cost: one state build per epoch, fast warm reads, the lock
# ═══════════════════════════════════════════════════════════════════════

WARM_LINES = ["Ney, attack Mack", "Davout, fortify", "Ney, march to Vienna", "where is Mack",
              "Soult, support Davout", "Lannes, scout Swabia", "everyone fortify",
              "Zorglub, attack Mack", "Ney, hold", "Murat, attack Mack"] * 2


class TestTheCost:

    def test_the_parse_state_is_built_once_per_epoch(self, board, monkeypatch):
        client, snap = board
        _fresh(snap)
        real = M.get_llm_game_state
        calls = []

        def counting():
            calls.append(1)
            return real()
        monkeypatch.setattr(M, "get_llm_game_state", counting)
        for line in WARM_LINES:
            pv(client, line)
        assert len(calls) == 1, len(calls)
        with _quiet():
            client.post("/command", json={"command": "status"})
        before = len(calls)
        pv(client, "Ney, attack Mack")
        assert len(calls) == before + 1, (before, len(calls))

    def test_a_warm_reading_is_fast(self, board):
        client, snap = board
        _fresh(snap)
        start = time.perf_counter()
        pv(client, "Ney, attack Mack")
        cold = time.perf_counter() - start
        times = []
        for line in WARM_LINES:
            start = time.perf_counter()
            pv(client, line)
            times.append(time.perf_counter() - start)
        # Measured on the shipped boot (Session UI-6): cold ~0.2 s, warm
        # median ~0.015 s, max ~0.05 s, single process. Generous for the
        # parallel lanes; tighten only on a measured baseline.
        assert cold < 0.8, cold
        assert statistics.median(times) < 0.15, times
        assert max(times) < 0.5, times

    def test_two_readers_never_cross(self, board):
        _client, snap = board
        world = _fresh(snap)
        kwargs = dict(llm_state=M.get_llm_game_state, epoch=M._STATE_EPOCH,
                      lost_marshal_refusal=M._addressed_lost_marshal_refusal,
                      why_rx=M._WHY_RX, live_llm=M.parser.llm,
                      unbound_addressee=M.executor._unbound_addressee,
                      premise_reader=M._premise_reading)
        lines = ("Ney, attack Mack", "Davout, fortify")
        alone = {line: PP.preview(world, line, **kwargs) for line in lines}
        seen = {line: [] for line in lines}

        def reader(line):
            for _ in range(40):
                seen[line].append(PP.preview(world, line, **kwargs))
        threads = [threading.Thread(target=reader, args=(line,)) for line in lines]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        for line in lines:
            busy = [r for r in seen[line] if r["kind"] == "busy"]
            assert len(busy) <= 4, len(busy)
            for reading in seen[line]:
                if reading["kind"] != "busy":
                    assert reading == alone[line], (line, reading, alone[line])

    def test_a_held_lock_reads_busy(self, board):
        _client, snap = board
        world = _fresh(snap)
        assert PP._LOCK.acquire(timeout=2)
        try:
            start = time.perf_counter()
            reading = PP.preview(world, "Ney, attack Mack", llm_state=M.get_llm_game_state)
            assert reading["kind"] == "busy"
            assert time.perf_counter() - start < 1.0
        finally:
            PP._LOCK.release()

    def test_a_post_in_flight_reads_busy(self, board):
        _client, snap = board
        world = _fresh(snap)
        reading = PP.preview(world, "Ney, attack Mack", llm_state=M.get_llm_game_state,
                             posts_in_flight=lambda: True)
        assert reading["kind"] == "busy"


# ═══════════════════════════════════════════════════════════════════════
# the price's free verbs stay the executor's
# ═══════════════════════════════════════════════════════════════════════

def test_the_free_order_verbs_are_the_executors():
    """`_FREE_ORDER_ACTIONS` copies the ORDER verbs of `executor.py`'s local
    `free_actions` list (the reports, the Cabinet's verbs and the debug words
    are read as other kinds); a verb added there must be added here."""
    from backend.ai.validation import CABINET_ACTIONS, META_ACTIONS, NON_ORDER_ACTIONS
    src = (REPO / "backend" / "commands" / "executor.py").read_text(encoding="utf-8")
    listed = re.search(r"free_actions = \[([^\]]*)\]", src)
    assert listed, "executor.py's free_actions list moved"
    free = set(re.findall(r'"([a-z_]+)"', listed.group(1)))
    orders = {a for a in free
              if a not in META_ACTIONS and a not in NON_ORDER_ACTIONS
              and a not in CABINET_ACTIONS and not a.startswith("diplomatic")
              and a not in ("unknown", "make_amends", "recognition_sweetener")}
    assert orders == set(PP._FREE_ORDER_ACTIONS), orders
