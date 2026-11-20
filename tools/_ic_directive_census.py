"""Row IC, the directive — step 0: the census of every line to several corps.

Every command line in `tools/playtest_scripts/*.json` and every utterance of
the golden corpus (`tests/data/parser_golden_corpus.json`) that names the army
as a whole or two or more of France's marshals, with how the directive's
reader takes it on the shipped 1805 board (`backend/commands/directive.py`):

    kind    who the reader says the line is for — everyone / at / list / army —
            or null (an order to one man, or to nobody: "Lannes support Ney,
            Murat support Lannes" names two men and addresses one)
    takes   "fan_out" — the group road carries it to every man (the action and
            the standing-order type beside it); "one_order" — it stays one
            man's order (an attack is one battle: the first man leads and the
            muster calls the others); "answer" — a free answer stands in its
            place; "none" — the reader does not take the line

The census is the guard that a committed script or measure does not change
behaviour unnoticed: `tests/test_ic4_the_directive.py::TestTheCensus` rebuilds
it and compares. `commanded_full40.json` — the France band's script — has no
such line, and the byte-identity series sends no command at all.

    .venv/Scripts/python.exe tools/_ic_directive_census.py            # rewrite the record
    .venv/Scripts/python.exe tools/_ic_directive_census.py --check    # exit 1 if stale
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "tools" / "playtest_scripts"
CORPUS = ROOT / "tests" / "data" / "parser_golden_corpus.json"
RECORD = ROOT / "tests" / "data" / "directive_lines_census.json"
SCENARIO = ROOT / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"


def _lines_of(path: pathlib.Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    out = []
    turns = data.get("turns")
    if isinstance(turns, dict):
        for rows in turns.values():
            out.extend(str(r) for r in (rows or []) if isinstance(r, str))
    for key in ("orders", "questions"):
        for row in data.get(key) or []:
            if isinstance(row, dict) and isinstance(row.get("line"), str):
                out.append(row["line"])
    return out


def _board():
    os.environ.setdefault("LLM_MODE", "mock")
    os.environ.setdefault("SOVEREIGN_SCENARIO", "none")
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    with contextlib.redirect_stdout(io.StringIO()):
        import backend.main as main_module
        from backend.commands.parser import CommandParser
        from backend.models.world_state import WorldState
        world = WorldState.from_scenario(str(SCENARIO))
        main_module.world = world
        main_module.game_state = {"world": world}
        main_module.parser = CommandParser(use_real_llm=False)
    return main_module, world


def build(board=None) -> dict:
    """The census. `board` is ``(backend.main, world)`` when the caller has
    already seated a shipped 1805 board on the server module (the test's own
    fixture); else one is booted here."""
    main_module, world = board if board is not None else _board()
    from backend.commands import directive, group_orders, parse_preview
    names = sorted((m.name for m in world.get_player_marshals()), key=len, reverse=True)
    one = r"(?<![A-Za-z])(?:" + "|".join(re.escape(n) for n in names) + r")(?![A-Za-z])"
    collective = re.compile(r"(?<![A-Za-z])(?:" + group_orders._COLLECTIVE_WHO + r")(?![A-Za-z])",
                            re.IGNORECASE)

    def several(line: str) -> bool:
        return len({m.lower() for m in re.findall(one, line, re.IGNORECASE)}) >= 2 \
            or bool(collective.search(line))

    def reading(line: str) -> dict:
        found = directive.address(world, line)
        row = {"kind": None, "names": [], "rest": "", "takes": "none", "action": "", "strategic": ""}
        if found is None:
            return row
        row.update(kind=found["kind"], names=list(found.get("names") or []),
                   rest=str(found.get("rest") or ""))
        with contextlib.redirect_stdout(io.StringIO()), parse_preview.reading():
            parsed = parse_preview.mock_parse(world, line, main_module.get_llm_game_state, 0)
            built = group_orders.build(
                world, parse_preview._preview_parser(),
                parse_preview._llm_state(world, main_module.get_llm_game_state, 0),
                line, parsed, address=found)
        if built is None:
            row["takes"] = "one_order" if found["kind"] == "list" else "none"
        elif built[0] == "result":
            row["takes"] = "answer"
        else:
            row.update(takes="fan_out", action=str(built[1].get("action") or ""),
                       strategic=str(built[1].get("strategic_type") or ""))
        return row

    rows = []
    seen = set()
    sources = [(p.name, _lines_of(p)) for p in sorted(SCRIPTS.glob("*.json"))]
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))["entries"]
    sources.append(("parser_golden_corpus.json",
                    [str(e.get("utterance") or "") for e in corpus if e.get("world") in ("1805", "any")]))
    for source, lines in sources:
        for line in lines:
            if (source, line) in seen or not several(line):
                continue
            seen.add((source, line))
            rows.append(dict({"source": source, "line": line}, **reading(line)))
    rows.sort(key=lambda r: (r["source"], r["line"]))
    by_takes: dict = {}
    for r in rows:
        by_takes[r["takes"]] = by_takes.get(r["takes"], 0) + 1
    return {
        "_note": ("Row IC, the directive — step 0. Every line to several corps in the committed "
                  "playtest scripts and the golden corpus, with how backend/commands/directive.py "
                  "reads it on the shipped 1805 board. Written by tools/_ic_directive_census.py; "
                  "compared by tests/test_ic4_the_directive.py::TestTheCensus."),
        "counts": {"lines": len(rows), "by_takes": dict(sorted(by_takes.items()))},
        "band_script_lines": sum(1 for r in rows if r["source"] == "commanded_full40.json"),
        "rows": rows,
    }


def render(record: dict) -> str:
    return json.dumps(record, indent=1, ensure_ascii=False) + "\n"


def main(argv) -> int:
    record = build()
    text = render(record)
    if "--check" in argv:
        if not RECORD.exists() or RECORD.read_text(encoding="utf-8") != text:
            print("the directive census is stale: run tools/_ic_directive_census.py")
            return 1
        print(f"the directive census is current: {record['counts']}")
        return 0
    RECORD.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {RECORD.relative_to(ROOT)}: {record['counts']}; "
          f"lines in the band's script: {record['band_script_lines']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
