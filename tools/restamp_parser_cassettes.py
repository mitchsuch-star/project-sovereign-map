"""Re-stamp the IQ-9 parser cassettes' prompt fingerprints, KEYLESSLY.

A parse prompt names every action the model may answer with (the list is
rendered from `validation.VALID_ACTIONS`) and carries the few-shot examples
(`prompt_builder.FEW_SHOT_TEMPLATES`). So adding an action or an example moves
every parse prompt — and with it the fingerprint each authored cassette
records, the record `tests/data/l1_prompt_restamp.json` and the manifest
`tests/data/parser_cassettes/MANIFEST.json` (pinned by
`tests/test_l1_the_prompt_turns_around.py::TestTheCassetteAttribution` and
`tests/test_iq9_keyless_parser_gate.py`).

The RESPONSES are authored and never change here: this tool asks the model
nothing. It replays each cassette's own utterance through the suite's replay
arm (`tests/_parser_replay.py` — the same road the pins walk), reads the
fingerprint of the request the parser would have sent TODAY, and writes that
fingerprint back. Row IC's directives (November 19, 2026) added the tool: five
slices before it re-stamped by hand ("keylessly, the same way").

    .venv/Scripts/python.exe tools/restamp_parser_cassettes.py            # rewrite
    .venv/Scripts/python.exe tools/restamp_parser_cassettes.py --check    # exit 1 if stale

It prints, per cassette, the prompt's length before and after — the figure
the pin's docstring records ("every parse prompt +N characters").
"""
from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RESTAMP_PATH = ROOT / "tests" / "data" / "l1_prompt_restamp.json"
NEWLINE = chr(10)


def _write_json(path: pathlib.Path, data) -> None:
    with open(path, "w", encoding="utf-8", newline=NEWLINE) as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write(NEWLINE)


def restamp(check: bool = False) -> int:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    import tests.test_iq9_keyless_parser_gate as IQ9
    from tests._parser_replay import (MANIFEST_PATH, body_kind, cassette_key, fingerprint,
                                      load_all_cassettes, load_manifest, utterance_of,
                                      write_cassette)
    cassettes = load_all_cassettes()
    manifest = load_manifest()
    record = json.loads(RESTAMP_PATH.read_text(encoding="utf-8"))
    stale = behind = 0
    skipped: list = []
    for cid in sorted(cassettes):
        entry = cassettes[cid]
        request = entry.get("request") or {}
        if not request.get("prompt_sha256"):
            continue
        world, state = IQ9.fresh_world(entry["world"])
        parser, replay = IQ9.arm(list(cassettes.values()), entry["world"], manifest)
        try:
            if entry.get("kind") == "parse":
                IQ9.parse(parser, entry["utterance"], state, world)
            else:
                # Berthier's recovery prompt names the typed orders too — the
                # road `TestCassetteHygiene` walks for it.
                with IQ9._quiet():
                    parser.llm.generate_berthier_recovery(entry["utterance"], state, {},
                                                          skip_llm=False)
        except Exception as exc:      # an authored error cassette raises by design
            if not replay.calls:
                print(f"!! {cid}: the replay raised before any request: {exc!r}")
                return 2
        key = cassette_key(entry)
        prints = [fingerprint(body) for body in replay.calls
                  if (body_kind(body), utterance_of(body), entry["world"]) == key]
        if not prints:
            # A cassette of another road (Berthier's recovery prompt is sent only
            # when the parse fails over to it): this tool walks the parse road
            # alone, and the pins say if that one moved.
            skipped.append(cid)
            continue
        live = prints[0]
        moved = {k: (request.get(k), v) for k, v in live.items() if request.get(k) != v}
        if moved:
            stale += 1
            was, now = int(request.get("prompt_chars", 0) or 0), int(live["prompt_chars"])
            print(f"  {cid}: prompt {was} -> {now} characters ({now - was:+d})"
                  + ("; the tool schema moved" if "tool_schema_sha256" in moved else "")
                  + ("; the system prompt moved" if "system_sha256" in moved else ""))
            if not check:
                entry["request"] = dict(request, **live)
                write_cassette(entry)
        # The record and the manifest follow the cassette, whether or not it was
        # written on THIS run: a run cut short leaves them behind, and this
        # brings them level.
        row = record.get(cid)
        if row is not None and (row.get("static_first_sha256") != live["prompt_sha256"]
                                or row.get("static_first_chars") != int(live["prompt_chars"])):
            behind += 1
            row["static_first_sha256"] = live["prompt_sha256"]
            row["static_first_chars"] = int(live["prompt_chars"])
        listed = (manifest.get("cassettes") or {}).get(cid)
        if listed is not None and listed.get("prompt_sha256") != live["prompt_sha256"]:
            behind += 1
            listed["prompt_sha256"] = live["prompt_sha256"]
    if skipped:
        print(f"  (not on the parse road, left as they are: {', '.join(skipped)})")
    if check:
        print("the cassettes are current" if not (stale or behind)
              else f"{stale} cassette(s) stale, {behind} record or manifest line(s) behind")
        return 1 if (stale or behind) else 0
    if stale or behind:
        _write_json(RESTAMP_PATH, record)
        _write_json(MANIFEST_PATH, manifest)
    print(f"re-stamped {stale} cassette(s), {behind} record or manifest line(s); "
          "the responses are untouched")
    return 0


if __name__ == "__main__":
    sys.exit(restamp(check="--check" in sys.argv[1:]))
