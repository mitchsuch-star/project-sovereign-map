"""Row IC, Session 4 — IC-13, EVERY MAN HIS OWN LINE (November 22, 2026).

The design is `docs/INDEPENDENT_COMMAND_SPEC.md` §11 (the voice); the guide
`docs/MARSHAL_VOICE_BIBLE.md`; the rules `docs/SYSTEMS_REFERENCE.md` §235; the
modules `backend/game_logic/own_voice.py` (the lines), `said_lately.py` (the
rule) and the older pickers swept under it (`marshal_voice.py`, `enemy_voice.py`,
`jealousy.petition_speaker_line`).

What is pinned here:

  * THE RULES OF A LINE — written by hand: every line of every set is plain and
    short (at most two sentences, no number, "Sire" the only period word), is
    HIS (no line stands in two men's sets), and breaks none of his "never says"
    words (`own_voice.NEVER_SAYS` — the guide's lists live in code);
  * THE SETS — a kind a man can say on nights running carries four lines or
    more; every bank of the older pickers carries four or more;
  * SAID LATELY — no line twice within a man's last three, read on a long walk
    of moments for every named man and every nature (a man with nothing new to
    say says NOTHING); the historical seed says the first line of each set
    first; the chooser is PURE and there is ONE writer; the save; the take-back;
  * WHERE A LINE IS SAID — the read-back shows the line the order then says; a
    task given, a man stood down, a hand order over his task, the junior sent
    past him, the task to prove himself, the letter-following man's own lines;
  * EACH MAN REMEMBERS ONE THING — kept only by the man who remembers it, said
    once;
  * THE LESSON — its two cards on setting a man on his own and asking him.
"""
from __future__ import annotations

import ast
import contextlib
import io
import json
import random
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.commands import parse_preview as PP
from backend.commands.parser import CommandParser
from backend.game_logic import enemy_voice as EV
from backend.game_logic import marshal_voice as MV
from backend.game_logic import own_order as O
from backend.game_logic import own_voice as V
from backend.game_logic import said_lately as SL
from backend.game_logic import trial as T
from backend.models.marshal import Marshal
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCENARIO = REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
NATURE_OF = {"Ney": "bold", "Lannes": "bold", "Murat": "bold", "Massena": "bold",
             "Davout": "careful", "Bernadotte": "careful", "Soult": "literal", "Grouchy": "literal"}
PERSONALITY = {"bold": "aggressive", "careful": "cautious", "literal": "literal"}


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


def _every_set():
    """(owner, kind, lines) for every authored set — the named men's and the
    natures'."""
    for name, kinds in V.LINES.items():
        for kind, lines in kinds.items():
            yield name, kind, tuple(lines)
    for nature, kinds in V.BY_NATURE.items():
        for kind, lines in kinds.items():
            yield f"nature:{nature}", kind, tuple(lines)


def _man(name: str, nature: str) -> Marshal:
    return Marshal(name=name, location="Paris", strength=20000,
                   personality=PERSONALITY[nature], nation="France")


def _sentences(line: str) -> int:
    return len([part for part in re.split(r"[.!?]+", line) if part.strip()])


@pytest.fixture(scope="module")
def _snapshot():
    with _quiet():
        return json.dumps(WorldState.from_scenario(str(SCENARIO)).to_dict(), default=str)


@pytest.fixture
def world(_snapshot):
    with _quiet():
        return WorldState.from_dict(json.loads(_snapshot))


@pytest.fixture(scope="module")
def road():
    mp = pytest.MonkeyPatch()
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        mp.delenv(key, raising=False)
    mp.setenv("LLM_MODE", "mock")
    prior = (M.world, M.game_state.get("world"), M.parser)
    with _quiet():
        M._reset_world_state()
    snap = json.dumps(M.world.to_dict(), default=str)
    try:
        with TestClient(M.app) as client:
            yield client, snap
    finally:
        M.world, M.parser = prior[0], prior[2]
        M.game_state["world"] = prior[1]
        PP.invalidate()
        mp.undo()


def _board(snap) -> WorldState:
    with _quiet():
        board = WorldState.from_dict(json.loads(snap))
        M._set_active_world(board)
        M.parser = CommandParser(use_real_llm=False)
    PP.invalidate()
    return board


def _post(client, line, **body):
    random.seed(1805)
    with _quiet():
        return client.post("/command", json={"command": line, "typed": True, **body}).json()


def _preview(client, line):
    PP.invalidate()
    with _quiet():
        return client.get("/parse_preview", params={"line": line}).json()


def _says(reading) -> list:
    return [str(p.get("text") or "") for p in (reading.get("parts") or [])
            if p.get("role") == "answer"]


# ═══════════════════════════ the rules of a line ═════════════════════════════

class TestTheRulesOfALine:

    def test_there_are_lines_for_every_man_the_design_names(self):
        assert set(V.LINES) == {"Ney", "Davout", "Murat", "Lannes", "Massena", "Bernadotte",
                                "Soult", "Grouchy"}
        assert set(V.BY_NATURE) == {"bold", "careful", "literal"}
        assert sum(len(lines) for _o, _k, lines in _every_set()) >= 400

    def test_every_line_is_plain_and_short(self):
        for owner, kind, lines in _every_set():
            for line in lines:
                assert isinstance(line, str) and line.strip() == line and line, (owner, kind)
                assert _sentences(line) <= 2, (owner, kind, line)
                assert not re.search(r"\d", line), f"a line states no number: {owner} {kind}: {line}"
                assert len(line) <= 120, (owner, kind, line)
                assert set(re.findall(r"\{(\w+)\}", line)) <= {"orders"}, (owner, kind, line)

    def test_sire_is_the_only_period_word(self):
        for owner, kind, lines in _every_set():
            for line in lines:
                for word in V.PERIOD_WORDS:
                    assert not re.search(rf"\b{re.escape(word)}\b", line, re.I), (owner, kind, line)

    def test_no_line_stands_in_two_sets(self):
        seen = {}
        for owner, kind, lines in _every_set():
            assert len(set(lines)) == len(lines), (owner, kind)
            for line in lines:
                assert line not in seen or seen[line] == owner, \
                    f"{line!r} stands in {seen.get(line)}'s set and in {owner}'s"
                seen.setdefault(line, owner)

    def test_no_man_says_what_he_never_says(self):
        """Every line a man CAN say — his own set and the lines of his nature
        that fall through to him (`own_voice.pool`): Ney never says he fell
        back, Murat never says he dug."""
        assert set(V.NEVER_SAYS) == set(V.LINES)
        for name, words in V.NEVER_SAYS.items():
            assert words, name
            nature = NATURE_OF[name]
            for kind in sorted(set(V.LINES[name]) | set(V.BY_NATURE[nature])):
                for line in V.pool(name, nature, kind):
                    for word in words:
                        assert not re.search(rf"\b{re.escape(word)}", line, re.I), \
                            f"{name} never says {word!r}: {kind}: {line}"
        # ... and the filter really bites: the bold nature's own lines say both
        assert any("fell back" in line.lower() for line in V.BY_NATURE["bold"]["fell_back"])
        assert any("dug" in line.lower() for line in V.BY_NATURE["bold"]["dug_in"])
        assert len(V.pool("Murat", "bold", "dug_in")) >= 4

    def test_the_letter_following_mans_repeat_line_carries_his_orders(self):
        for owner in ("Soult", "Grouchy"):
            assert all("{orders}" in line for line in V.LINES[owner]["repeat"])
        assert all("{orders}" in line for line in V.BY_NATURE["literal"]["repeat"])
        soult = _man("Soult", "literal")
        said = V.voice(None, soult, "repeat", orders="Hold Lorraine.")
        assert "Hold Lorraine." in said and "{orders}" not in said


# ═══════════════════════════ the sets ════════════════════════════════════════

class TestTheSets:

    def test_a_kind_said_on_nights_running_carries_four_lines_a_man(self):
        for name, nature in NATURE_OF.items():
            for kind in V.RECURRING:
                held = V.pool(name, nature, kind)
                if nature == "literal" and not held:
                    continue        # a letter-following man is never on his own
                assert len(held) >= 4, (name, kind, len(held))
        for nature in ("bold", "careful"):
            for kind in V.RECURRING:
                assert len(V.BY_NATURE[nature].get(kind) or ()) >= 4, (nature, kind)

    def test_every_named_mans_set_of_every_kind_is_four_or_more(self):
        for name, nature in NATURE_OF.items():
            for kind in V.LINES[name]:
                assert len(V.pool(name, nature, kind)) >= 4, (name, kind)

    def test_his_own_lines_come_before_his_natures(self):
        held = V.pool("Ney", "bold", "idle")
        own = V.LINES["Ney"]["idle"]
        assert held[:len(own)] == tuple(own) and len(held) > len(own)
        assert V.pool("Suchet", "careful", "idle") == tuple(V.BY_NATURE["careful"]["idle"])
        assert V.pool("Napoleon", "", "idle") == ()

    def test_every_bank_of_the_older_pickers_is_four_or_more(self):
        for bank in (MV.LITERAL_ACK, MV.LITERAL_COMPLETE, MV.LITERAL_EXACT, MV._MUSTER_HALT_LINES):
            assert len(bank) >= 4
        for nature, kinds in MV._ACK_LINES.items():
            for kind, bank in kinds.items():
                assert len(bank) >= 4, (nature, kind)
        for nature, bank in MV._COMPLETION_LINES.items():
            assert len(bank) >= 4, nature
        for name, nature in NATURE_OF.items():
            for situation in MV.OWN_VOICE_SITUATIONS:
                assert len(MV.voice_bank(name, PERSONALITY[nature], situation)) >= 4
        for personality in ("aggressive", "cautious", "literal"):
            for situation in EV.VOICE_SITUATIONS:
                assert len(EV.voice_bank("Nobody", personality, situation)) >= 4
        from backend.game_logic import jealousy
        for personality, bank in jealousy._PETITION_VOICE.items():
            assert len(bank) >= 4, personality


# ═══════════════════════════ said lately ═════════════════════════════════════

class TestSaidLately:

    def test_no_line_twice_within_his_last_three_on_a_long_walk(self):
        """Every named man and every nature, four thousand moments each, the
        kinds drawn at random (the same kind many times running among them):
        a line he says is never one of the three he said before it."""
        rng = random.Random(1805)
        men = [(name, nature) for name, nature in NATURE_OF.items()]
        men += [("Suchet", "careful"), ("Oudinot", "bold"), ("Dokhturov", "literal")]
        for name, nature in men:
            man = _man(name, nature)
            kinds = sorted(set(V.LINES.get(name, {})) | set(V.BY_NATURE[nature]))
            trail, silent = [], 0
            for _step in range(4000):
                kind = rng.choice(kinds)
                line = V.speak(None, man, kind)
                if not line:
                    silent += 1
                    continue
                key = SL.key_of(line)
                assert key not in trail[-3:], (name, kind, line)
                trail.append(key)
            assert len(man.said_lately) <= SL.KEPT
            assert silent < 4000 * 0.35, (name, silent)      # he mostly has something to say

    def test_on_nights_running_he_always_has_a_line(self):
        rng = random.Random(7)
        for name, nature in NATURE_OF.items():
            if nature == "literal":
                continue
            man = _man(name, nature)
            for _step in range(2000):
                assert V.speak(None, man, rng.choice(V.RECURRING)), name

    def test_a_man_with_nothing_new_to_say_says_nothing(self):
        man = _man("Suchet", "careful")
        small = ("one.", "two.", "three.")
        said = [SL.speak(man, small) for _ in range(3)]
        assert said == ["one.", "two.", "three."]
        assert SL.choose(man, small) == "" and SL.speak(man, small) == ""
        assert SL.speak(man, small + ("four.",)) == "four."

    def test_the_historical_seed_says_the_first_line_of_each_set_first(self, world):
        assert not world.campaign_seed or world.campaign_seed == "historical"
        for name, nature in NATURE_OF.items():
            for kind in V.LINES[name]:
                fresh = _man(name, nature)
                assert V.voice(world, fresh, kind, orders="x") == V.pool(name, nature, kind)[0].format(
                    orders="x"), (name, kind)

    def test_another_seed_starts_each_set_at_a_fixed_place(self, world):
        world.campaign_seed = "austerlitz"
        firsts = set()
        for name, nature in NATURE_OF.items():
            for kind in V.LINES[name]:
                held = V.pool(name, nature, kind)
                one = V.voice(world, _man(name, nature), kind, orders="x")
                assert one == V.voice(world, _man(name, nature), kind, orders="x")
                firsts.add(one == held[0].format(orders="x"))
        assert firsts == {True, False}, "a seeded campaign starts some sets elsewhere"

    def test_the_chooser_is_pure_and_there_is_one_writer(self):
        man = _man("Ney", "bold")
        for _ in range(5):
            assert V.voice(None, man, "idle") == V.LINES["Ney"]["idle"][0]
        assert not man.said_lately
        first = V.speak(None, man, "idle")
        assert man.said_lately == [SL.key_of(first)]
        assert V.voice(None, man, "idle") != first
        # a template's key is the template's: "the order was {order}" is one
        # line whatever the order
        assert SL.key_of("\"{order}.\" As written, Sire.") != SL.key_of("\"Hold.\" As written, Sire.")

    def test_only_the_voice_modules_write_what_he_said(self):
        """`said_lately.say` / `speak` are called from the voice's own modules
        and nowhere else; `Marshal.said_lately` is assigned in `said_lately`
        (and by the save's reader) only."""
        callers = set()
        for path in (REPO / "backend").rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            if "said_lately" not in text or path.name == "said_lately.py":
                continue
            tree = ast.parse(text)
            for node in ast.walk(tree):
                if isinstance(node, ast.Attribute) and node.attr in ("say", "speak") \
                        and isinstance(node.value, ast.Name) \
                        and node.value.id in ("_lately", "_said", "said_lately", "SL"):
                    callers.add(path.name)
                if isinstance(node, (ast.Assign, ast.AugAssign)):
                    targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                    for target in targets:
                        if isinstance(target, ast.Attribute) and target.attr == "said_lately":
                            assert path.name == "marshal.py", f"{path.name} writes said_lately"
        assert callers == {"own_voice.py", "marshal_voice.py", "enemy_voice.py"}, callers

    def test_what_he_said_is_saved_and_only_when_held(self):
        man = _man("Ney", "bold")
        assert "said_lately" not in man.to_dict()
        V.speak(None, man, "idle")
        V.speak(None, man, "struck")
        data = man.to_dict()
        assert data["said_lately"] == man.said_lately and len(data["said_lately"]) == 2
        back = Marshal.from_dict(json.loads(json.dumps(data)))
        assert back.said_lately == man.said_lately
        assert V.voice(None, back, "idle") == V.voice(None, man, "idle")
        old = dict(data)
        old.pop("said_lately")
        assert Marshal.from_dict(old).said_lately == []

    def test_an_order_taken_back_takes_its_line_back(self):
        from backend.commands import take_back
        assert "marshals" in take_back.ORDER_KEYS      # `said_lately` rides the marshal


# ═══════════════════════════ where a line is said ════════════════════════════

class TestWhereALineIsSaid:

    def test_the_read_back_shows_the_line_the_order_then_says(self, road):
        client, snap = road
        board = _board(snap)
        shown = _says(_preview(client, "Ney, take Swabia on your own"))
        assert len(shown) == 1 and shown[0].strip("“”") in V.pool("Ney", "bold", "ack")
        assert not board.marshals["Ney"].said_lately, "a reading records nothing"
        out = _post(client, "Ney, take Swabia on your own")
        assert out["success"]
        voices = out.get("voices") or []
        assert voices and voices[0]["speaker"] == "Ney"
        assert voices[0]["says"] == shown[0].strip("“”")
        ney = M.world.marshals["Ney"]
        assert ney.said_lately == [SL.key_of(voices[0]["says"])]

    def test_asking_him_changes_nothing(self, road):
        client, snap = road
        _board(snap)
        assert _post(client, "Davout, hold Rhineland on your own")["success"]
        before = json.dumps(M.world.to_dict(), default=str, sort_keys=True)
        davout = M.world.marshals["Davout"]
        for kind in ("night", "sight"):
            O.answer(M.world, davout, kind)
        O.proposal(M.world, M.world.marshals["Lannes"])
        T.proposal(M.world, M.world.marshals["Lannes"])
        V.voice(M.world, davout, "waited")
        MV.literal_exact_ack("Soult", 1, marshal=M.world.marshals["Soult"])
        _preview(client, "Lannes, take Swabia on your own")
        assert json.dumps(M.world.to_dict(), default=str, sort_keys=True) == before

    def test_a_man_stood_down_says_so(self, road):
        client, snap = road
        board = _board(snap)
        assert _post(client, "Murat, hold Franche-Comte on your own")["success"]
        board = M.world
        board.marshals["Murat"].strategic_order.own["given"] = int(board.current_turn) - 1
        board.marshals["Murat"].strategic_order.issued_turn = int(board.current_turn) - 1
        out = _post(client, "Murat, stand down")
        assert out["success"], out.get("message")
        voices = [v for v in out.get("voices") or [] if v["speaker"] == "Murat"]
        assert voices and voices[0]["says"] in V.pool("Murat", "bold", "recalled")
        # Murat REMEMBERS being recalled: it is on his mind, and said once
        murat = M.world.marshals["Murat"]
        assert V.has_memory(murat)
        again = V.recall_memory(M.world, murat, said=True)
        assert again in V.pool("Murat", "bold", "remembers") and not V.has_memory(murat)
        assert V.recall_memory(M.world, murat, said=True) == ""

    def test_a_hand_order_over_his_own_task_is_answered(self, road):
        client, snap = road
        _board(snap)
        assert _post(client, "Ney, hold Rhineland on your own")["success"]
        board = M.world
        ney = board.marshals["Ney"]
        # a man GIVEN his task today is not overruled by it
        quiet = {}
        from backend.commands import if_thens
        if_thens._overruled(board, ney, quiet)
        assert not quiet and not V.has_memory(ney)
        ney.said_lately = []
        ney.strategic_order.issued_turn = int(board.current_turn) - 1
        ney.strategic_order.started_turn = int(board.current_turn) - 1
        ney.last_ordered_turn = int(board.current_turn) - 1
        result = {}
        if_thens._overruled(board, ney, result)
        assert result["voices"][0]["speaker"] == "Ney"
        assert result["voices"][0]["says"] in V.pool("Ney", "bold", "overruled")
        assert V.has_memory(ney), "Ney remembers an order that overruled him"

    def test_the_memory_is_kept_only_by_the_man_who_remembers_that_thing(self, world):
        ney, davout, soult = (world.marshals[n] for n in ("Ney", "Davout", "Soult"))
        assert V.remembers_what(ney) == "overruled" and V.remembers_what(davout) == "passed_over"
        assert V.remembers_what(soult) == ""          # he holds his lines, not a grudge
        assert not V.note_memory(world, ney, "passed_over") and not V.has_memory(ney)
        assert V.note_memory(world, davout, "passed_over", "Ney") and V.has_memory(davout)
        assert not V.note_memory(world, soult, "overruled")
        assert V.recall_memory(world, davout, said=False) in V.pool("Davout", "careful", "remembers")
        assert V.has_memory(davout), "a preview does not put it away"

    def test_the_task_to_prove_himself_is_asked_and_ended_in_his_words(self, world):
        lannes = world.marshals["Lannes"]
        read = T.proposal(world, lannes)
        assert read["speaker"] == "Lannes" and read["says"] in V.pool("Lannes", "bold", "trial_ask")
        assert not lannes.said_lately
        given = T.give(world, lannes)
        assert given["given"] and "says" not in given       # one channel: `voices`
        assert given["voices"] == [{"says": read["says"], "speaker": "Lannes"}]
        assert lannes.said_lately == [SL.key_of(read["says"])]
        row = T.settle(world, lannes)
        assert row["speaker"] == "Lannes"
        assert row["says"] in (V.pool("Lannes", "bold", "trial_won") + V.pool("Lannes", "bold", "trial_lost"))
        told = [e for e in T.morning_events(world) if e.get("phase") == "ended"]
        assert told and told[0]["says"] == row["says"] and told[0]["speaker"] == "Lannes"

    def test_the_letter_following_man_speaks_his_own_lines(self, road):
        client, snap = road
        board = _board(snap)
        soult = board.marshals["Soult"]
        # exact orders, on the read-back: from HIS set, and nothing recorded
        shown = _says(_preview(client, "Soult, hold Lorraine. If attacked, dig in."))
        assert shown and shown[0].strip("“”") in V.LINES["Soult"]["exact"]
        # asked to go on his own: the refusal, and his own line beside it
        out = _post(client, "Soult, hold Lorraine on your own")
        assert not out["success"]
        voices = out.get("voices") or []
        assert voices and voices[0]["speaker"] == "Soult"
        assert voices[0]["says"] in V.pool("Soult", "literal", "refusal")
        # asked what he will do, with no order: he asks for his orders
        assert O.answer(M.world, M.world.marshals["Soult"], "night")["says"] in V.pool(
            "Soult", "literal", "refusal")
        assert not M.world.marshals["Soult"].said_lately and soult is not None

    def test_a_broken_line_and_used_lines_carry_his_line_on_the_desk(self, world):
        from backend.game_logic import today
        from backend.models.marshal import StrategicOrder
        soult = world.marshals["Soult"]
        turn = int(world.current_turn)
        soult.strategic_order = StrategicOrder(
            command_type="HOLD", target=soult.location, target_type="region",
            started_turn=turn - 2, issued_turn=turn - 2, original_command="Soult, hold Lorraine",
            if_thens=[{"if": "attacked", "then": "dig_in", "used": True, "written": turn - 2}])
        rows = [r for r in today.decide(world) if str(r.get("id", "")).startswith("orders_used:Soult")]
        assert rows and rows[0]["speaker"] == "Soult"
        assert rows[0]["says"] in V.pool("Soult", "literal", "not_covered")
        soult.strategic_order.if_thens[0]["struck"] = "Ney is gone"
        rows = [r for r in today.decide(world) if str(r.get("id", "")).startswith("orders_broken:Soult")]
        assert rows and rows[0]["says"] in V.pool("Soult", "literal", "broken")
        assert not soult.said_lately, "the desk is a reading"

    def test_the_older_pickers_obey_the_rule_when_given_the_man(self):
        ney = _man("Ney", "bold")
        said = [MV.personality_ack("aggressive", "MOVE_TO", 3, 5, marshal_name="Ney", marshal=ney)
                for _ in range(12)]
        assert all(said)
        for at, line in enumerate(said):
            assert line not in said[max(0, at - 3):at]
        soult = _man("Soult", "literal")
        acks = [MV.literal_ack("hold Lorraine", 4, marshal=soult) for _ in range(8)]
        for at, line in enumerate(acks):
            assert line and line not in acks[max(0, at - 3):at]
        # with no man they are the bare rotation, as before the session
        assert MV.personality_ack("aggressive", "MOVE_TO", 3, 5, marshal_name="Ney") == \
            MV.personality_ack("aggressive", "MOVE_TO", 3, 5, marshal_name="Ney")
        mack = Marshal(name="Mack", location="Swabia", strength=50000, personality="literal",
                       nation="Austria")
        lines = [EV.pick_enemy_voice("Mack", "literal", "repelled_you", 2, marshal=mack)
                 for _ in range(8)]
        for at, line in enumerate(lines):
            assert line and line not in lines[max(0, at - 3):at]

    def test_the_reply_carries_the_voices_key(self):
        assert "voices" in M._COMMAND_RESULT_SIMPLE_FIELDS

    def test_captured_orders_are_headed_in_the_courts_own_words(self, world):
        head = V.court_head(world, "Austria", "Mack")
        assert head == V.COURTS["Austria"][0].format(name="Mack")
        assert V.court_head(world, "Naples", "Damas") == V.COURTS[""][0].format(name="Damas")
        from backend.game_logic import learned
        told = learned.taken_words(world, {"court": "Austria", "marshal": "Mack",
                                           "orders": ["Mack holds Swabia."]})
        assert head in told and "Mack holds Swabia." in told


class TestTheLessonsTwoCards:
    """The School of War teaches setting a man on his own, and asking him."""

    @staticmethod
    def _client_cards():
        src = (REPO / "godot-client" / "project-sovereign" / "scripts"
               / "tutorial_overlay.gd").read_text(encoding="utf-8")
        steps = src.split("const STEPS", 1)[1].split("\n]\n", 1)[0]
        heads = list(re.finditer(r'"id": "(\w+)",\s*(?:#[^\n]*\n\s*)*"turn_gate"', steps))
        ends = [h.start() for h in heads[1:]] + [len(steps)]
        return [dict(id=h.group(1), block=steps[h.start():e])
                for h, e in zip(heads, ends)]

    def test_the_two_cards_stand_before_the_instruments_in_both_places(self):
        """After "The Laws of State", before "The Instruments" — at gate 12, so
        the lesson's own catch-up walks them and the last two cards keep their
        gates (placed after "The Instruments" they held an idle player off the
        last card: the lesson's engine test and the review)."""
        from backend.game_logic.tutorial_state import STEPS
        ids = [c["id"] for c in self._client_cards()]
        assert ids[ids.index("laws"):ids.index("laws") + 5] == [
            "laws", "on_his_own", "ask_him", "free_books", "handoff"]
        mirror = [s[0] for s in STEPS]
        assert mirror == ids
        titles = {s[0]: s[2] for s in STEPS}
        gates = {s[0]: s[1] for s in STEPS}
        assert titles["on_his_own"] == "XIX. On His Own"
        assert titles["ask_him"] == "XX. Ask Him"
        assert titles["free_books"] == "XXI. The Instruments"
        assert (gates["on_his_own"], gates["ask_him"], gates["free_books"]) == (12, 12, 13)

    def test_they_carry_no_gate(self):
        cards = {c["id"]: c["block"] for c in self._client_cards()}
        for cid in ("on_his_own", "ask_him"):
            assert '"suggest": ""' in cards[cid] and '"suggest_action": ""' in cards[cid]
            assert '"open"' not in cards[cid]
            assert '"turn_gate": 12,' in cards[cid]
            # read, then passed by the next thing the player does
            assert '"advance": "_pred_any_success"' in cards[cid]

    def test_they_teach_the_task_and_the_question(self):
        cards = {c["id"]: c["block"] for c in self._client_cards()}
        assert "on your own" in cards["on_his_own"]
        assert "what will you do" in cards["ask_him"]

    def test_the_last_card_is_still_the_lesson_end(self):
        from backend.game_logic.tutorial_state import STEPS
        assert self._client_cards()[-1]["id"] == "handoff"
        assert STEPS[-1] == ("handoff", 14, "XXII. The Lesson Ends")


# ═══════════════════════════ every line said is shown ════════════════════════
# The four readers' census (November 22, 2026): lines recorded as SAID and then
# dropped before the screen — the audience's, every one on the order-list road,
# the answer after an objection, the completion on arrival — and a line drawn
# twice. Each road below now carries what was said, once.

@pytest.fixture
def board_client(world, monkeypatch):
    from backend.commands import take_back as TB
    monkeypatch.setattr(M, "world", world)
    monkeypatch.setattr(M, "game_state", {"world": world, "executor": M.executor})
    with _quiet():
        monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    TB.new_board()
    PP.invalidate()
    yield TestClient(M.app)
    TB.new_board()
    PP.invalidate()


def _send(client, text, **extra):
    random.seed(1805)
    with _quiet():
        return client.post("/command", json=dict({"command": text}, **extra)).json()


class TestEveryLineSaidIsShown:

    def test_the_audience_shows_his_line_and_the_give_says_it(self, world, board_client):
        ney = world.marshals["Ney"]
        with _quiet():
            ney.trust.set(15)
            event = world.disobedience_system.check_redemption_threshold(ney, world)
        arm = next(o for o in event["options"] if o["id"] == "trial")
        assert arm["speaker"] == "Ney" and arm["says"] == T.proposal(world, ney)["says"]
        assert arm["says"] in V.pool("Ney", "bold", "trial_ask")
        with _quiet():
            reply = board_client.post("/respond_to_redemption", json={"choice": "trial"}).json()
        assert reply["success"] is True
        assert reply["voices"] == [{"says": arm["says"], "speaker": "Ney"}]

    def test_an_armys_task_reply_carries_the_commanders_line(self, world, board_client):
        assert _send(board_client, "form the Army of the Rhine with Ney, Davout and Soult")["success"]
        listing = _send(board_client, "Army of the Rhine, take Swabia", list_first=True)["directive"]
        lead = next(r for r in listing["rows"] if r.get("lead"))
        # (the army's LIST leaves his answer off — pressed in Session 3b, it
        # pushed the followers below the screen's foot; it stands under the
        # command line as you type, from the row's `voice`)
        shown = str(lead.get("voice") or "")
        assert shown.startswith("“"), lead
        members = [r["marshal"] for r in listing["rows"] if r["ticked"]]
        total = sum(int(r["ap"]) for r in listing["rows"] if r["marshal"] in members)
        reply = _send(board_client, listing["line"], list_first=True, members=members, expect_ap=total)
        assert reply["success"], reply.get("message")
        heard = {v["speaker"]: v["says"] for v in reply.get("voices") or []}
        assert heard.get(lead["marshal"]) == shown.strip("“”"), (heard, shown)

    def test_a_list_of_plain_orders_carries_each_mans_answer_once(self, world, board_client):
        listing = _send(board_client, "Ney and Davout, hold Rhineland for 3 turns",
                        list_first=True).get("directive") or {}
        assert listing.get("rows"), "the line opens a list"
        members = [r["marshal"] for r in listing["rows"] if r["ticked"]]
        total = sum(int(r["ap"]) for r in listing["rows"] if r["marshal"] in members)
        reply = _send(board_client, listing["line"], list_first=True, members=members, expect_ap=total)
        assert reply["success"], reply.get("message")
        heard = {v["speaker"]: v["says"] for v in reply.get("voices") or []}
        assert set(heard) == {"Ney", "Davout"}, reply.get("voices")
        for name, line in heard.items():
            assert line not in reply["message"], "said once — beside his portrait, not in the staff's text"
            # (the acknowledgement banks keep their quote marks in the record)
            assert {SL.key_of(line), SL.key_of(f'"{line}"')} & set(world.marshals[name].said_lately)

    def test_exact_orders_say_the_line_the_read_back_showed_every_time(self, world, board_client):
        world.actions_remaining = 12
        # (a NEW order each round: the read-back refuses a renewed hold of the
        # ground he holds — "already holding here" — while Enter gives it; that
        # older mismatch is filed, `BUG_FIXES.md` IC4-N1)
        orders = ("Soult, hold Lorraine. If attacked, dig in.",
                  "Soult, march to Champagne. If attacked, dig in.",
                  "Soult, march to Rhineland. If outnumbered, fall back on Lorraine.")
        for line in orders:
            PP.invalidate()
            with _quiet():
                reading = board_client.get("/parse_preview", params={"line": line}).json()
            shown = _says(reading)
            assert shown, reading
            reply = _send(board_client, line)
            assert reply["success"], reply.get("message")
            assert reply["voices"] == [{"speaker": "Soult", "says": shown[0].strip("“”")}]
            for older in MV.LITERAL_ACK:          # the verbatim quote is not said as well
                assert older.rsplit(".", 1)[0].split(". ")[-1].strip('" ') not in reply["message"] \
                    or "{order}" in older.rsplit(".", 1)[0].split(". ")[-1]

    def test_the_battle_lines_carry_their_speaker(self):
        import tests.test_marshal_voice_tier1 as tier1
        world, result = tier1.TestBattleReportCarriesOwnVoice()._fight()
        report = result.get("battle_report") or {}
        by = report.get("marshal_voice_by")
        assert by and by["speaker"] == "Ney"
        assert report["marshal_voice"] == f'Ney: "{by["says"]}"'
        if report.get("enemy_voice"):
            assert report["enemy_voice_by"]["speaker"] == "Mack"
            assert report["enemy_voice"] == f'Mack: "{report["enemy_voice_by"]["says"]}"'
        mack = world.get_marshal("Mack")
        if report.get("enemy_voice") and mack is not None:
            assert SL.key_of(report["enemy_voice_by"]["says"]) in mack.said_lately

    def test_a_night_with_no_fight_says_no_struck_line(self):
        moved = [{"success": True}]
        assert O._voice_act("take", {}, moved, [{"action": "move", "target": "Swabia"}]) == "march"
        assert O._voice_act("take", {}, [], []) == "claim"
        assert "claim" not in V.KIND_OF_ACT, "a claim of the ground he stands on has no line of his"
        fought = {"battle_result": {}}
        assert O._voice_act("take", fought, moved, [{"action": "attack"}]) == "take"
        assert O._voice_act("attack", fought, [], []) == "attack"
        # the verification (three skeptics of three): a siege kept up, or an
        # attack that ran no battle, claims no fight; a join says he marched
        assert O._voice_act("besiege", {}, [], []) == "claim"
        assert O._voice_act("storm", {}, [], []) == "claim"
        assert V.KIND_OF_ACT["join"] == "marched"

    def test_a_stay_says_the_line_that_fits_why_he_stayed(self):
        """A man who did your order today, did his night's work, was drawn into
        a friend's battle or has no corps says no line of the night; a quiet
        front is a waiting night; only a stay because the board changed says
        his "stayed" line (which claims that it changed)."""
        for why in ("your order today", "his night is done", "drawn in today", "no corps"):
            assert O._voice_act("stay", {}, [], [], why) == "claim", why
        assert V.KIND_OF_ACT[O._voice_act("stay", {}, [], [], "nothing to do")] == "waited"
        assert O._voice_act("stay", {}, [], [], "Mack's fight changed things") == "stay"
        assert V.KIND_OF_ACT["stay"] == "stayed"

    def test_his_proposal_line_follows_the_task_proposed(self, world):
        """A hold is never pitched as a chase: "proposal" for take, chase and
        support, "proposal_hold" for hold (the verification, three of three)."""
        seen = set()
        for name, nature in (("Ney", "bold"), ("Murat", "bold"), ("Lannes", "bold"),
                             ("Massena", "bold"), ("Davout", "careful"), ("Bernadotte", "careful")):
            man = world.marshals[name]
            for place in (str(man.location), "Brittany"):
                man.location = place
                world.refresh_marshal_indexes()
                prop = O.proposal(world, man)
                kind = "proposal_hold" if prop["task"] == "hold" else "proposal"
                seen.add(kind)
                if prop["says"]:
                    assert prop["says"] in V.pool(name, nature, kind), (name, prop["task"], prop["says"])
        assert seen == {"proposal", "proposal_hold"}, "both kinds were read"
        for name in ("Ney", "Murat", "Lannes"):
            assert len(V.pool(name, "bold", "proposal_hold")) >= 4

    def test_the_hand_built_replies_carry_voices(self):
        """The two replies built key by key (`/respond_to_redemption`,
        `/objection_response`) copy `voices`; the completion on arrival shows
        the line `_complete_order` said; a task done is said on its report row
        and not again on the morning's event."""
        main = (REPO / "backend" / "main.py").read_text(encoding="utf-8")
        assert main.count('_copy_truthy_result_fields(response, result, ("voices",))') >= 2
        strategic = (REPO / "backend" / "commands" / "strategic.py").read_text(encoding="utf-8")
        assert "done = self._complete_order(marshal, world, msg)" in strategic
        own = (REPO / "backend" / "game_logic" / "own_order.py").read_text(encoding="utf-8")
        assert ('world.log_event({"type": EVENT, "phase": "done", "marshal": man.name,\n'
                '                             "nation": man.nation, "message": message})') in own.replace("\r\n", "\n")
