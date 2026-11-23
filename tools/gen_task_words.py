"""Generate the parser's and the client's lists from THE WORD TABLE.

Row IC, Session 2 (IC-8; `docs/INDEPENDENT_COMMAND_SPEC.md` §8.3). The one
hand-written table of what the typed line takes for a task is
`backend/ai/word_table.py`. This tool renders it into

    backend/ai/task_words.py                                  the parser's lists
    godot-client/project-sovereign/scripts/task_words.gd      the client's chips,
                                                              Tab words and Help

Every alternation `(a|b)` and option `[word]` of a table phrase is expanded
into flat phrases, lower-cased, de-duplicated and ordered longest first — the
order a matcher must try them in. A phrase that two parts both claim is an
error here, before anything is written.

Why GENERATED modules rather than a read at import: the client cannot import
Python at all, and the census (`tests/test_ic8_the_line.py`) wants plain data
it can compare byte for byte — the pattern of `tools/gen_routed_order_words`
(CX-R1). The census re-renders both files and fails when either has drifted.

Run:
    python -m tools.gen_task_words            # rewrite both files
    python -m tools.gen_task_words --check    # exit 1 when either is stale
"""
from __future__ import annotations

import itertools
import re
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
PY_TARGET = REPO / "backend" / "ai" / "task_words.py"
GD_TARGET = REPO / "godot-client" / "project-sovereign" / "scripts" / "task_words.gd"


# ── the phrase syntax ───────────────────────────────────────────────────────

def _split_top(text: str, sep: str = "|") -> List[str]:
    """Split on `sep` outside any bracket."""
    out, depth, start = [], 0, 0
    for i, ch in enumerate(text):
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth -= 1
        elif ch == sep and depth == 0:
            out.append(text[start:i])
            start = i + 1
    out.append(text[start:])
    return out


def _tokens(phrase: str) -> List[str]:
    """Top-level tokens of a phrase: words, `(a|b)` groups, `[opt]` groups."""
    out, depth, start = [], 0, 0
    for i, ch in enumerate(phrase):
        if ch in "([":
            if depth == 0 and i > start:
                out.append(phrase[start:i])
                start = i
            depth += 1
        elif ch in ")]":
            depth -= 1
            if depth == 0:
                out.append(phrase[start:i + 1])
                start = i + 1
    if start < len(phrase):
        out.append(phrase[start:])
    return [t for t in out if t != ""]


def expand(phrase: str) -> List[str]:
    """Every flat phrase a table phrase stands for.

    >>> expand("attack [(him|them)]")
    ['attack', 'attack him', 'attack them']
    """
    choices: List[List[str]] = []
    for token in _tokens(phrase):
        if token.startswith("(") and token.endswith(")"):
            alts: List[str] = []
            for alt in _split_top(token[1:-1]):
                alts.extend(expand(alt))
            choices.append(alts)
        elif token.startswith("[") and token.endswith("]"):
            choices.append([""] + expand(token[1:-1]))
        else:
            choices.append([token])
    flat = []
    for combo in itertools.product(*choices):
        text = re.sub(r"\s+", " ", "".join(combo)).strip()
        if text and text not in flat:
            flat.append(text)
    return flat


def _flat(phrases: Iterable[str]) -> List[str]:
    """Expanded, lower-cased (slots kept), de-duplicated, longest first."""
    seen: List[str] = []
    for phrase in phrases:
        for text in expand(phrase):
            low = re.sub(r"\{(\w+)\}", lambda m: "{" + m.group(1) + "}", text.lower())
            if low not in seen:
                seen.append(low)
    return sorted(seen, key=lambda t: (-len(t), t))


# ── the render ──────────────────────────────────────────────────────────────

def build() -> Dict[str, object]:
    """The table, expanded — the plain data both files are rendered from."""
    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))
    from backend.ai import word_table as T

    tasks, rewrites, verbs = {}, [], []
    for row in T.TASKS:
        tasks[row["order"]] = {"task": row["task"], "object": row["object"],
                               "words": list(row["words"]), "bare": list(row["bare"]),
                               "new": sorted(row["new"])}
        for word, means in sorted(row["new"].items()):
            rewrites.append((word, means, row["object"]))
            verbs.append(word.split()[0])
    how_long = [(row["key"], row["say"]) for row in T.HOW_LONG]

    ifs: List[Tuple[str, str, str]] = []
    should: List[Tuple[str, str, str]] = []
    for row in T.IFS:
        for text in _flat(row["say"]):
            ifs.append((row["if"], row["slot"] or "", text))
        for text in _flat(row["should"]):
            should.append((row["if"], row["slot"] or "", text))
    thens: List[Tuple[str, bool, str]] = []
    for row in T.THENS:
        for text in _flat(row["say"]):
            thens.append((row["then"], bool(row["any_odds"]), text))
    for name, rows in (("IF", ifs), ("SHOULD", should)):
        texts = [r[2] for r in rows]
        dupes = sorted({t for t in texts if texts.count(t) > 1})
        if dupes:
            raise ValueError(f"word table: {name} phrase claimed twice: {dupes}")
    then_texts = [r[2] for r in thens]
    dupes = sorted({t for t in then_texts if then_texts.count(t) > 1})
    if dupes:
        raise ValueError(f"word table: THEN phrase claimed twice: {dupes}")
    key = lambda r: (-len(r[2]), r[2])   # noqa: E731 — longest first, then by text
    arrival = {}
    for row in T.ARRIVAL_THENS:
        for text in _flat(row["say"]):
            arrival[text] = row["verb"]
    bold = {"bolder": [], "careful": []}
    for row in T.HOW_BOLD:
        for text in _flat(row["say"]):
            if text not in bold[row["step"]]:
                bold[row["step"]].append(text)
    for step in bold:
        bold[step] = sorted(bold[step], key=lambda t: (-len(t), t))
    return {
        "tasks": tasks, "rewrites": rewrites, "verbs": sorted(set(verbs)),
        "how_long": how_long, "markers": list(T.IF_MARKERS),
        "ifs": sorted(ifs, key=key), "should": sorted(should, key=key),
        "thens": sorted(thens, key=key),
        "thens_for": {k: list(v) for k, v in sorted(T.THENS_FOR.items())},
        "arrival": dict(sorted(arrival.items())), "bold": bold,
        "filler": sorted({re.sub(r"\s+", " ", f.lower().strip()) for f in T.FILLER},
                         key=lambda t: (-len(t), t)),
        "held_back": sorted({re.sub(r"\s+", " ", f.lower().strip()) for f in T.HELD_BACK},
                            key=lambda t: (-len(t), t)),
        "open_ended": _flat(T.OPEN_ENDED),
        "examples": list(T.EXAMPLES),
        # Row IC, Session 3b: an army's task and the war goal's.
        "army_task": {kind: sorted({w.lower() for w in words}, key=lambda t: (-len(t), t))
                      for kind, words in T.ARMY_TASK.items()},
        "army_marks": [(said, means) for pattern, means in T.ARMY_MARKS for said in _flat([pattern])],
        "army_exact": _flat(T.ARMY_EXACT),
        "goal_verbs": _flat(T.GOAL_VERBS),
        "goal_objects": _flat([T.GOAL_OBJECT]),
        # Row IC, Session 4b: on his own with no task
        "free_task": sorted({re.sub(r"\s+", " ", f.lower().strip()) for f in T.FREE_TASK},
                            key=lambda t: (-len(t), t)),
    }


_PY_HEADER = '''"""GENERATED by `python -m tools.gen_task_words` — do not edit.

The parser's lists for a typed TASK, rendered from THE WORD TABLE
(`backend/ai/word_table.py`; row IC, Session 2 — IC-8,
`docs/INDEPENDENT_COMMAND_SPEC.md` §8.3). Every phrase is flat (alternations
expanded), lower-case, and ordered longest first within its list. The census in
`tests/test_ic8_the_line.py` re-renders this file from the table and fails when
it has drifted: after changing the table, regenerate it.
"""

'''


def _py_list(name: str, rows: Sequence, comment: str = "") -> str:
    out = (f"# {comment}\n" if comment else "") + f"{name} = (\n"
    for row in rows:
        out += f"    {row!r},\n"
    return out + ")\n\n"


def render_py(data: Dict[str, object]) -> str:
    out = _PY_HEADER
    out += "# order type -> the task's name, the kind of object it takes, its words\n"
    out += "TASKS = {\n"
    for order, row in data["tasks"].items():
        out += f"    {order!r}: {row!r},\n"
    out += "}\n\n"
    out += _py_list("TASK_REWRITES", data["rewrites"],
                    "(new word, the table word it means, the object it must stand before)")
    out += _py_list("TASK_VERBS", data["verbs"],
                    "the verb-position words of the NEW task words (the addressee rule's)")
    out += _py_list("HOW_LONG", data["how_long"], "(condition key, how it is said)")
    out += _py_list("IF_MARKERS", data["markers"])
    out += _py_list("IF_PHRASES", data["ifs"], "(the if, the slot it binds, the phrase)")
    out += _py_list("IF_SHOULD_PHRASES", data["should"],
                    "the inverted forms behind \"should\"")
    out += _py_list("THEN_PHRASES", data["thens"], "(the then, whatever the odds, the phrase)")
    out += "THENS_FOR = {\n"
    for key, value in data["thens_for"].items():
        out += f"    {key!r}: {tuple(value)!r},\n"
    out += "}\n\n"
    out += "# what a march does THEN: the phrase -> the arrival verb it means\n"
    out += "ARRIVAL_THENS = {\n"
    for phrase, verb in data["arrival"].items():
        out += f"    {phrase!r}: {verb!r},\n"
    out += "}\n\n"
    out += _py_list("BOLDER_WORDS", data["bold"]["bolder"])
    out += _py_list("CAREFUL_WORDS", data["bold"]["careful"])
    out += _py_list("FILLER", data["filler"],
                    "clauses that state no condition: a quiet note, blocking nothing")
    out += _py_list("HELD_BACK", data["held_back"],
                    "behind an attack on a named enemy: no glorious charge")
    out += _py_list("OPEN_ENDED", data["open_ended"],
                    "an 'until' that asks for no limit: filler, blocking nothing")
    out += _py_list("EXAMPLES", data["examples"])
    out += "# Row IC, Session 3b — a task for an ARMY: the verbs that make its line a task\n"
    out += "# (a take, a chase, a hold with a place named; `marked`: only with a mark)\n"
    out += "ARMY_TASK = {\n"
    for kind, words in data["army_task"].items():
        out += f"    {kind!r}: {tuple(words)!r},\n"
    out += "}\n\n"
    out += _py_list("ARMY_MARKS", data["army_marks"],
                    "(what an army is told of itself, how its commander hears it)")
    out += _py_list("ARMY_EXACT", data["army_exact"],
                    "the same words as a plain order to each corps")
    out += _py_list("GOAL_VERBS", data["goal_verbs"],
                    "\"Ney, take the war goal\": the verbs that take the goal as their object")
    out += _py_list("GOAL_OBJECTS", data["goal_objects"])
    out += _py_list("FREE_TASK", data["free_task"],
                    "Row IC, Session 4b — beside a mark of judgement, the words that still say \"no task\"")
    return out.rstrip("\n") + "\n"


_GD_HEADER = '''# GENERATED by `python -m tools.gen_task_words` — do not edit.
#
# The client's words for a typed TASK, rendered from THE WORD TABLE
# (`backend/ai/word_table.py`; row IC, Session 2 — IC-8). The chips under the
# command line, the Tab words and the Help page read these, so nothing the
# client offers is a word the parser does not read. Loaded by path (no
# class_name: a new one needs the engine's class cache).
extends RefCounted

'''


def _gd_str(text: str) -> str:
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _gd_array(name: str, rows: Sequence[str]) -> str:
    out = f"const {name} := [\n"
    for row in rows:
        out += f"\t{_gd_str(row)},\n"
    return out + "]\n\n"


def render_gd(data: Dict[str, object]) -> str:
    out = _GD_HEADER
    out += "# how long: what the \"until…\" and \"for N turns\" chips write\n"
    out += _gd_array("HOW_LONG", [say for _key, say in data["how_long"]])
    out += "# the words that open an if-then\n"
    out += _gd_array("IF_MARKERS", data["markers"])
    # One plain phrase an IF (the shortest said form) for the "if…" chips.
    shortest: Dict[Tuple[str, str], str] = {}
    for name, slot, text in data["ifs"]:
        key = (name, slot)
        if key not in shortest or len(text) < len(shortest[key]):
            shortest[key] = text
    out += "# the if-then chips: [the if, the slot it binds, what the chip writes]\n"
    out += "const IFS := [\n"
    for (name, slot), text in sorted(shortest.items()):
        out += f"\t[{_gd_str(name)}, {_gd_str(slot)}, {_gd_str(text)}],\n"
    out += "]\n\n"
    then_short: Dict[Tuple[str, bool], str] = {}
    for name, any_odds, text in data["thens"]:
        key = (name, any_odds)
        if key not in then_short or len(text) < len(then_short[key]):
            then_short[key] = text
    out += "# the answers: [the then, whatever the odds, what the chip writes]\n"
    out += "const THENS := [\n"
    for (name, any_odds), text in sorted(then_short.items()):
        out += f"\t[{_gd_str(name)}, {'true' if any_odds else 'false'}, {_gd_str(text)}],\n"
    out += "]\n\n"
    out += "# which answers an if may carry\n"
    out += "const THENS_FOR := {\n"
    for key, value in data["thens_for"].items():
        out += f"\t{_gd_str(key)}: [{', '.join(_gd_str(v) for v in value)}],\n"
    out += "}\n\n"
    out += "# what a march does then: the pick on the march card\n"
    out += "const ARRIVAL_THENS := {\n"
    for phrase, verb in data["arrival"].items():
        out += f"\t{_gd_str(phrase)}: {_gd_str(verb)},\n"
    out += "}\n\n"
    out += "# the sentences the Help page teaches (each is read back by the census)\n"
    out += _gd_array("EXAMPLES", data["examples"])
    return out.rstrip("\n") + "\n"


def main(argv: List[str]) -> int:
    data = build()
    rendered = {PY_TARGET: render_py(data), GD_TARGET: render_gd(data)}
    if "--check" in argv:
        stale = [p for p, text in rendered.items()
                 if not p.exists() or p.read_text(encoding="utf-8") != text]
        for path in stale:
            print(f"{path.relative_to(REPO)} is STALE — run `python -m tools.gen_task_words`.")
        if not stale:
            print("task_words.py and task_words.gd are current.")
        return 1 if stale else 0
    for path, text in rendered.items():
        path.write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote {path.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
