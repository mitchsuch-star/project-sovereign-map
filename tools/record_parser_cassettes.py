"""Record parser cassettes from the LIVE model — opt-in, never from the suite.

IQ-9 "The Keyless Parser Gate" (September 18, 2026). The test suite replays
`tests/data/parser_cassettes/*.json` through the provider's named seam
(`AnthropicProvider.bind_sdk_client`) and NEVER records: a cassette miss is a
`BaseException`. This tool is the only path that spends the key, and it
refuses to run unless BOTH of these hold:

    * ``--record`` is passed, and
    * ``ANTHROPIC_API_KEY`` is present after this tool's own ``load_dotenv()``
      (the only place in the gate that reads the repo ``.env``).

``--dry-run`` lists what would be recorded, keyless. Nothing here is
imported by ``tests/`` (an AST pin asserts it).

    .venv/Scripts/python.exe tools/record_parser_cassettes.py --dry-run
    .venv/Scripts/python.exe tools/record_parser_cassettes.py --record --ids cr5-deleg-aggressive-ney-resolves-live
    .venv/Scripts/python.exe tools/record_parser_cassettes.py --record --phrasings tests/data/parser_cassettes/phrasings.json
    .venv/Scripts/python.exe tools/record_parser_cassettes.py --record --refresh-drifted

What one recording does: builds the named world exactly as the corpus does
(`parser_eval.build_world` / `build_llm_game_state` — the production-mirrored
payload), arms `LLMClient(provider="anthropic")` (env key), wraps the REAL SDK
client in a Recorder through the same seam the replay uses, parses the
utterance through the real pipeline, and writes one cassette per request the
pipeline made (two when Berthier's text-mode recovery fires). Request
prompts are stored as hashes (~16.6 KB each otherwise); responses verbatim
(`message.to_dict()`), plus the request id and the SDK version.

Overwrite policy: an existing cassette is NOT overwritten unless
``--overwrite`` is passed or the id was selected by ``--refresh-drifted``. A
field diff (action / marshals / target / stop_reason) against the existing
cassette is printed either way.

Cost: ~$0.0065 per parse (CR-3 measured); the whole starting set is ~17
calls ≈ $0.11.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tests._parser_replay import (  # noqa: E402
    CASSETTE_DIR, CASSETTE_VERSION, MANIFEST_PATH, MODEL_PIN, PHRASINGS_PATH,
    body_kind, cassette_key, load_all_cassettes, load_manifest, load_phrasings,
    request_snapshot, utterance_of, write_cassette,
)

COST_PER_PARSE_USD = 0.0065


class Recorder:
    """Wraps the REAL SDK client: forwards messages.create, captures the body
    (hashes only) and the response, and hands both to the writer."""

    def __init__(self, real_client):
        self._real = real_client
        self.messages = _RecorderMessages(real_client.messages)

    @property
    def captured(self) -> List[Tuple[Dict, object]]:
        return self.messages.captured


class _RecorderMessages:
    def __init__(self, real_messages):
        self._real = real_messages
        self.captured: List[Tuple[Dict, object]] = []

    def create(self, **body):
        message = self._real.create(**body)
        self.captured.append((body, message))
        return message


def _corpus_live_only_rows() -> List[Dict]:
    from backend.ai.parser_eval import load_corpus
    return [e for e in load_corpus()["entries"] if e.get("live_only")]


def _plan(args) -> List[Dict]:
    """The (id, utterance, world, source) rows this run would record."""
    rows: List[Dict] = []
    existing = load_all_cassettes()
    manifest = load_manifest() if MANIFEST_PATH.exists() else {"cassettes": {}}

    def add(cassette_id: str, utterance: str, world: str, source: str):
        if args.world != "any" and world != args.world:
            return
        rows.append({"id": cassette_id, "utterance": utterance, "world": world,
                     "source": source,
                     "existing": existing.get(cassette_id, {}).get("provenance")})

    if args.ids:
        wanted = set(args.ids)
        for entry in _corpus_live_only_rows():
            if entry["id"] not in wanted:
                continue
            worlds = ["legacy", "1805"] if entry.get("world", "any") == "any" \
                else [entry["world"]]
            for world in worlds:
                cid = (entry["id"] if len(worlds) == 1
                       else f"{entry['id']}.{world}")
                add(cid, entry["utterance"], world, "corpus live_only")
        missing = wanted - {e["id"] for e in _corpus_live_only_rows()}
        if missing:
            print(f"WARNING: not live_only corpus ids (ignored): {sorted(missing)}")
    if args.phrasings:
        with open(args.phrasings, encoding="utf-8") as fh:
            phr = json.load(fh)
        for entry in phr["entries"]:
            add(entry.get("cassette") or entry["id"], entry["utterance"],
                entry["world"], f"phrasings {Path(args.phrasings).name}")
    if args.refresh_drifted:
        for cid, meta in manifest.get("cassettes", {}).items():
            entry = existing.get(cid)
            if not entry or entry.get("kind") != "parse":
                continue
            if _is_drifted(entry):
                add(cid, entry["utterance"], entry["world"],
                    "manifest drift refresh")
    # de-duplicate by (utterance, world) — one request records both kinds
    seen = set()
    plan = []
    for row in rows:
        k = (row["utterance"], row["world"])
        if k in seen:
            continue
        seen.add(k)
        plan.append(row)
    return plan


def _is_drifted(entry: Dict) -> bool:
    """Recompute the live prompt hash for a cassette's utterance/world and
    compare with the recorded one (keyless: prompt building needs no key)."""
    from backend.ai.parser_eval import build_world, build_llm_game_state
    from backend.ai.prompt_builder import build_parse_prompt
    from tests._parser_replay import fingerprint
    recorded = (entry.get("request") or {}).get("prompt_sha256")
    if not recorded:
        return False
    world = build_world(entry["world"])
    gs = build_llm_game_state(world)
    prompt = build_parse_prompt(raw_input=entry["utterance"], game_state=gs,
                                command_history=[])
    live = fingerprint({"messages": [{"role": "user", "content": prompt}],
                        "system": "", "tools": []})["prompt_sha256"]
    return live != recorded


def _field_diff(old: Optional[Dict], new: Dict) -> List[str]:
    """Human-readable diff of the parse fields that matter."""
    if not old:
        return ["(new cassette)"]

    def fields(entry):
        content = (entry.get("response") or {}).get("content") or []
        inp = {}
        for block in content:
            if block.get("type") == "tool_use":
                inp = block.get("input") or {}
                break
        return {"action": inp.get("action"), "marshals": inp.get("marshals"),
                "target": inp.get("target"),
                "stop_reason": (entry.get("response") or {}).get("stop_reason")}

    a, b = fields(old), fields(new)
    return [f"{k}: {a[k]!r} -> {b[k]!r}" for k in a if a[k] != b[k]] or ["(no field change)"]


def record(plan: List[Dict], args) -> int:
    import anthropic
    from backend.ai.llm_client import LLMClient
    from backend.ai.parser_eval import build_world, build_llm_game_state
    from backend.commands.parser import CommandParser

    existing = load_all_cassettes()
    manifest = load_manifest() if MANIFEST_PATH.exists() else {
        "corpus_version": CASSETTE_VERSION, "cassettes": {}}
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    worlds = {}
    written = 0
    for row in plan:
        wk = row["world"]
        if wk not in worlds:
            world = build_world(wk)
            worlds[wk] = (world, build_llm_game_state(world))
        world, gs = worlds[wk]
        parser = CommandParser(use_real_llm=False)
        parser.llm = LLMClient(provider="anthropic")
        if parser.llm.provider_name != "anthropic" or not parser.llm.api_key:
            print("ERROR: the anthropic provider did not arm (no key?)")
            return 2
        real = parser.llm.provider._client()
        recorder = Recorder(real)
        parser.llm.provider.bind_sdk_client(recorder)
        print(f"-> recording {row['id']!r} ({wk}): {row['utterance']!r}")
        parser.parse(row["utterance"], gs, world=world)
        # Berthier's live arm is main.py's (it fires on a parse failure); the
        # CLI records the parse request(s) the pipeline made. A recovery
        # cassette is recorded when the pipeline itself asked for one.
        if not recorder.captured:
            print("   (no live call was made — the fast parser was confident; "
                  "nothing to record)")
            continue
        for body, message in recorder.captured:
            kind = body_kind(body)
            cid = row["id"] if kind == "parse" else f"{row['id']}.recovery"
            entry = {
                "id": cid, "kind": kind,
                "utterance": utterance_of(body) or row["utterance"],
                "world": wk, "history": list(
                    world.get_command_history_for_prompt() or []),
                "provenance": "recorded",
                "request": request_snapshot(body),
                "response": message.to_dict(),
                "recorded": {"at": now, "sdk": anthropic.__version__,
                             "request_id": getattr(message, "_request_id", None),
                             "corpus_version": CASSETTE_VERSION},
                "notes": existing.get(cid, {}).get("notes", ""),
            }
            old = existing.get(cid)
            for line in _field_diff(old, entry):
                print(f"   diff {cid}: {line}")
            refresh = args.refresh_drifted and row["source"].startswith("manifest")
            if old and not (args.overwrite or refresh):
                print(f"   SKIP {cid}: exists (pass --overwrite to replace)")
                continue
            write_cassette(entry)
            manifest.setdefault("cassettes", {})[cid] = {
                "kind": kind, "utterance": entry["utterance"], "world": wk,
                "provenance": "recorded",
                "prompt_sha256": entry["request"]["prompt_sha256"],
                "drift": None,
            }
            written += 1
            print(f"   wrote {cid} (request_id={entry['recorded']['request_id']})")
    with open(MANIFEST_PATH, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"\nrecorded {written} cassette(s); manifest updated")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--record", action="store_true",
                    help="actually call the live model (needs ANTHROPIC_API_KEY)")
    ap.add_argument("--dry-run", action="store_true",
                    help="list what would be recorded; no key, no network")
    ap.add_argument("--ids", nargs="*", default=None,
                    help="corpus live_only ids to record")
    ap.add_argument("--phrasings", default=None,
                    help=f"a phrasings file (default set: {PHRASINGS_PATH})")
    ap.add_argument("--world", choices=("1805", "legacy", "any"), default="any")
    ap.add_argument("--refresh-drifted", action="store_true",
                    help="re-record only the cassettes whose prompt hash drifted")
    ap.add_argument("--overwrite", action="store_true",
                    help="replace an existing cassette (default: keep it)")
    args = ap.parse_args(argv)

    if not (args.record or args.dry_run):
        ap.error("pass --record (spends the key) or --dry-run (keyless)")
    if not (args.ids or args.phrasings or args.refresh_drifted):
        ap.error("select work: --ids ..., --phrasings FILE and/or --refresh-drifted")

    plan = _plan(args)
    if not plan:
        print("nothing to record")
        return 0

    import anthropic
    print(f"model pin: {MODEL_PIN} | sdk: anthropic {anthropic.__version__} | "
          f"cassette dir: {CASSETTE_DIR}")
    print(f"planned requests: {len(plan)} (~${len(plan) * COST_PER_PARSE_USD:.2f} "
          f"at ${COST_PER_PARSE_USD}/parse; Berthier recovery calls extra)")
    for row in plan:
        print(f"  - {row['id']} [{row['world']}] {row['utterance']!r} "
              f"({row['source']}; existing: {row['existing'] or 'none'})")
    if args.dry_run and not args.record:
        print("\n--dry-run: no key read, no call made")
        return 0

    # The ONLY place the gate reads .env, and only on --record.
    from dotenv import load_dotenv
    load_dotenv()
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: --record needs ANTHROPIC_API_KEY (set it or put it in .env)")
        return 2
    return record(plan, args)


if __name__ == "__main__":
    sys.exit(main())
