"""
CR-1 Parser Eval Harness (COMMAND_ROBUSTNESS_SPEC.md slice CR-1).

Golden-corpus regression gate for the command parse pipeline: a data file
of (utterance -> expected parse fields) pairs evaluated over BOTH scenario
worlds (the legacy 19-region fixture and the shipped 126-province 1805
campaign) through the production call shape
    parser.parse(utterance, llm_game_state, world=world).

The corpus lives at tests/data/parser_golden_corpus.json. Each entry:

    {
      "id": "unique-kebab-slug",
      "utterance": "Soult, attack Mack",
      "world": "1805",            // "legacy" | "1805" | "any" (= both)
      "expected": { ... },         // PARTIAL — only present keys assert
      "source": "file::test or CR-1 authored",
      "notes": "optional"
    }

Expected keys (all optional):
    success          bool  — result["success"]. IMPLICIT success=True when
                     absent: negative-only expectations (not_action,
                     marshal:null, strategic_type:null) must not pass
                     vacuously against a hard parse failure. Entries whose
                     contract is "this fails" say so explicitly.
    marshal          str|null — command.marshal
    action           str   — command.action
    not_action       str   — command.action must NOT equal this
    target           str|null — command.target
    type             str   — command.type (classifier vocabulary + "diplomatic")
    strategic_type   str|null — top-level strategic_type (null = NOT strategic)
    target_stance    str   — command.target_stance
    requested_type   str   — command.requested_type (recruit family)
    error_contains   str   — substring of result.error (failure entries)
    diplo            {action?, proposal_type?, target_nation?, mission_type?,
                      tone?} — asserted against command.diplomatic_data

Modes:
    Mock (CI, deterministic): the pytest harness
    tests/test_command_robustness_cr1_eval_harness.py runs every entry with
    use_real_llm=False.

    Live (on demand): run
        .venv\\Scripts\\python.exe -m backend.ai.parser_eval --live
    with LLM_MODE=anthropic + ANTHROPIC_API_KEY configured. This exercises
    the SAME pipeline with the live-provider fallback armed — note the fast
    parser still short-circuits at confidence >= 0.7, which is the shipped
    behavior under test, not a harness artifact.

Adding an action to the parser? Add at least one corpus entry — the
harness's coverage gate fails if a mock-reachable action id has no entry.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CORPUS_PATH = REPO_ROOT / "tests" / "data" / "parser_golden_corpus.json"
SCENARIO_1805_PATH = (
    REPO_ROOT / "godot-client" / "project-sovereign" / "assets" / "maps"
    / "europe_1805.json"
)

WORLD_KEYS = ("legacy", "1805")

# Keys an entry's `expected` block may carry (hygiene-checked by the harness)
ALLOWED_EXPECTED_KEYS = {
    "success", "marshal", "action", "not_action", "target", "type",
    "strategic_type", "target_stance", "requested_type", "error_contains",
    "diplo",
    # CR-7-2: the compound / conditional keys. Before this the harness had
    # no way to assert a dropped tail, a condition or an arrival — 24 rows
    # carried a marker and 0 asserted any of the three, and a row asserting
    # a deliberately wrong `dropped_sequel` reported PASS on the CLI.
    "dropped_sequel", "warning_contains", "strategic_condition",
    "attack_on_arrival",
}
ALLOWED_DIPLO_KEYS = {
    "action", "proposal_type", "target_nation", "mission_type", "tone",
}


def load_corpus(path: Optional[Path] = None) -> Dict:
    corpus_path = Path(path) if path else DEFAULT_CORPUS_PATH
    with open(corpus_path, encoding="utf-8") as f:
        return json.load(f)


def build_world(world_key: str):
    """Construct the named scenario world (fresh instance)."""
    from backend.models.world_state import WorldState
    if world_key == "legacy":
        return WorldState(player_nation="France")
    if world_key == "1805":
        return WorldState.from_scenario(str(SCENARIO_1805_PATH))
    raise ValueError(f"Unknown world key: {world_key}")


def build_llm_game_state(world) -> Dict:
    """Mirror of backend.main.get_llm_game_state() (main.py:148) for an
    arbitrary world — INCLUDING the R5/V2-5 fog filter on enemies, so the
    corpus runs against the production-shaped payload."""
    from backend.models.intel import FULL, PARTIAL, VISIBILITY_PRIORITY
    marshals = {
        m.name: {"location": m.location, "strength": int(m.strength),
                 "morale": int(m.morale)}
        for m in world.get_player_marshals() if m.strength > 0
    }
    enemies = {}
    for m in world.get_enemy_marshals():
        if m.strength > 0:
            vis = world.get_region_intel(m.location).visibility
            if VISIBILITY_PRIORITY.get(vis, 0) >= VISIBILITY_PRIORITY[PARTIAL]:
                enemies[m.name] = {
                    "location": m.location,
                    "strength": int(m.strength) if vis == FULL else "unknown",
                    "nation": m.nation,
                }
    map_data = {}
    for region_name, region in world.regions.items():
        marshals_here = world.get_marshals_in_region(region_name)
        region_vis = world.get_region_intel(region_name).visibility_at_least(PARTIAL)
        visible_marshals = [
            {"name": m.name, "personality": getattr(m, 'personality', 'unknown')}
            for m in marshals_here
            if m.strength > 0
            and (m.nation == world.player_nation or region_vis)
        ]
        map_data[region_name] = {
            "controller": region.controller or "Neutral",
            "marshals": visible_marshals,
        }
    return {"turn": int(world.current_turn), "gold": int(world.gold),
            "marshals": marshals, "enemies": enemies, "map_data": map_data,
            # Mirrors production: providers read game_state["world"] for
            # the command-history repetition guardrail
            "world": world}


def worlds_for_entry(entry: Dict) -> List[str]:
    world = entry.get("world", "any")
    if world == "any":
        return list(WORLD_KEYS)
    return [world]


def evaluate_entry(parser, entry: Dict, world_key: str, world,
                   game_state: Dict) -> List[str]:
    """Run one corpus entry on one world. Returns a list of mismatch
    strings — empty means the entry passed."""
    expected = entry.get("expected", {})
    result = parser.parse(entry["utterance"], game_state, world=world)
    mismatches: List[str] = []

    def check(label, actual, want):
        if actual != want:
            mismatches.append(f"{label}: expected {want!r}, got {actual!r}")

    # CR-7-2: an expected key the harness cannot evaluate is a FAILURE, not
    # a silent pass — `evaluate_entry` used to check only the keys it knew,
    # so a row asserting anything else was green whatever the parser did.
    # The pytest hygiene gate (`test_expected_keys_allowed`) still forbids
    # such rows from being committed; this makes the CLI say so too.
    unknown = sorted(set(expected) - ALLOWED_EXPECTED_KEYS)
    if unknown:
        mismatches.append(f"unknown expected key(s): {unknown}")
        return mismatches

    # Implicit success=True when unstated — negative-only expectations must
    # never pass vacuously against a hard parse failure (a regression that
    # makes 'attack wellington' error out would otherwise keep the gate
    # green because command={} satisfies every negative check).
    expected_success = expected.get("success", True)
    check("success", bool(result.get("success")), expected_success)
    if "error_contains" in expected:
        error_text = (result.get("error") or "") + " " + (result.get("suggestion") or "")
        if expected["error_contains"].lower() not in error_text.lower():
            mismatches.append(
                f"error_contains: {expected['error_contains']!r} not in {error_text!r}")
    if not expected_success:
        return mismatches

    command = result.get("command") or {}
    if "marshal" in expected:
        check("marshal", command.get("marshal"), expected["marshal"])
    if "action" in expected:
        check("action", command.get("action"), expected["action"])
    if "not_action" in expected and command.get("action") == expected["not_action"]:
        mismatches.append(
            f"not_action: action must not be {expected['not_action']!r}")
    if "target" in expected:
        check("target", command.get("target"), expected["target"])
    if "type" in expected:
        check("type", command.get("type"), expected["type"])
    if "strategic_type" in expected:
        actual = result.get("strategic_type") if result.get("is_strategic") else None
        check("strategic_type", actual, expected["strategic_type"])
    if "target_stance" in expected:
        check("target_stance", command.get("target_stance"), expected["target_stance"])
    if "requested_type" in expected:
        check("requested_type", command.get("requested_type"), expected["requested_type"])
    if "diplo" in expected:
        diplo = command.get("diplomatic_data") or {}
        for key, want in expected["diplo"].items():
            check(f"diplo.{key}", diplo.get(key), want)
    # CR-7-2: the compound / conditional keys. `dropped_sequel` and
    # `attack_on_arrival` compare the parse result's own top-level values
    # (None when absent — a row may assert `null` to pin "nothing dropped");
    # `strategic_condition` compares the StrategicCondition-shaped dict;
    # `warning_contains` is a substring of the parser's `warning`.
    if "dropped_sequel" in expected:
        check("dropped_sequel", result.get("dropped_sequel"), expected["dropped_sequel"])
    if "attack_on_arrival" in expected:
        actual = result.get("attack_on_arrival") if result.get("is_strategic") else None
        check("attack_on_arrival", bool(actual) if actual is not None else None,
              expected["attack_on_arrival"])
    if "strategic_condition" in expected:
        actual = result.get("strategic_condition") if result.get("is_strategic") else None
        check("strategic_condition", actual, expected["strategic_condition"])
    if "warning_contains" in expected:
        warning = result.get("warning") or ""
        if expected["warning_contains"].lower() not in warning.lower():
            mismatches.append(
                f"warning_contains: {expected['warning_contains']!r} not in {warning!r}")
    return mismatches


def run_corpus(corpus: Optional[Dict] = None, use_real_llm: bool = False,
               only_world: Optional[str] = None,
               only_ids: Optional[List[str]] = None,
               verbose: bool = False, parser=None) -> Dict:
    """Evaluate the whole corpus. Returns a summary dict with failures.

    ``parser`` (IQ-9, September 18, 2026): an already-armed CommandParser to
    evaluate WITH — the keyless replay CLI (`--replay`) and the cassette
    recorder pass one whose LLM client is bound to a replay/recording SDK
    client. ``None`` reproduces the pre-IQ-9 loop byte-for-byte
    (`CommandParser(use_real_llm=use_real_llm)`), and the "refusing to
    report a mock run as live" guard reads `parser.llm.provider_name` exactly
    as before.
    """
    from backend.commands.parser import CommandParser

    corpus = corpus or load_corpus()
    if parser is None:
        parser = CommandParser(use_real_llm=use_real_llm)
    if use_real_llm and parser.llm.provider_name == "mock":
        raise RuntimeError(
            "--live requested but the LLM provider resolved to MOCK "
            "(set LLM_MODE=anthropic + ANTHROPIC_API_KEY) — refusing to "
            "report a mock run as live.")

    contexts = {}
    for world_key in WORLD_KEYS:
        if only_world and world_key != only_world:
            continue
        world = build_world(world_key)
        contexts[world_key] = (world, build_llm_game_state(world))

    total = passed = skipped_live_only = skipped_mock_only = 0
    failures = []
    for entry in corpus["entries"]:
        if only_ids and entry["id"] not in only_ids:
            continue
        # live_only entries assert a LIVE-LLM behavior (e.g. the CR-5 delegation
        # personality bias — under mock a delegation verb degrades to ASK, so the
        # biased action is unobservable). Evaluate them ONLY with the live
        # provider armed; skip (counted, never silent) under mock.
        if entry.get("live_only") and not use_real_llm:
            skipped_live_only += 1
            continue
        # mock_only mirrors live_only: the entry pins a MOCK-parser behavior
        # (e.g. the V2-55 word-boundary "Unknown action" shape) that the live
        # LLM legitimately resolves differently (it may interpret the whole
        # utterance). Skip (counted, never silent) when the live provider runs.
        if entry.get("mock_only") and use_real_llm:
            skipped_mock_only += 1
            continue
        for world_key in worlds_for_entry(entry):
            if world_key not in contexts:
                continue
            world, game_state = contexts[world_key]
            total += 1
            mismatches = evaluate_entry(parser, entry, world_key, world, game_state)
            if mismatches:
                failures.append({
                    "id": entry["id"], "world": world_key,
                    "utterance": entry["utterance"], "mismatches": mismatches,
                })
                if verbose:
                    print(f"FAIL [{world_key}] {entry['id']}: {entry['utterance']!r}")
                    for m in mismatches:
                        print(f"     {m}")
            else:
                passed += 1
                if verbose:
                    print(f"ok   [{world_key}] {entry['id']}")
    return {"total": total, "passed": passed, "failed": len(failures),
            "skipped_live_only": skipped_live_only,
            "skipped_mock_only": skipped_mock_only, "failures": failures}


def _run_replay(corpus: Dict, only_world: Optional[str] = None,
                only_ids: Optional[List[str]] = None,
                verbose: bool = False) -> Dict:
    """IQ-9 `--replay`: the `live_only` rows through the SAME evaluate loop,
    on a parser whose Anthropic client is bound to the committed cassettes.

    Keyless and offline by construction: the replay client is the
    `tests/_parser_replay.py` ReplayClient (BYOK fake key, network guard
    up), and a cassette MISS raises a BaseException the loop does not
    catch — surfaced here as exit 2 rather than a green fallback.
    """
    try:
        from tests._parser_replay import (
            CassetteMiss, armed_parser, install_network_guard,
            load_all_cassettes, load_manifest)
    except ImportError as exc:  # pragma: no cover — run from the repo root
        raise RuntimeError(
            "--replay needs the repo's tests/ tree on sys.path (run from the "
            f"repository root): {exc}") from exc
    install_network_guard()
    cassettes = list(load_all_cassettes().values())
    manifest = load_manifest()
    live_only_ids = [e["id"] for e in corpus["entries"] if e.get("live_only")]
    ids = [i for i in live_only_ids if not only_ids or i in only_ids]
    if not ids:
        raise RuntimeError("--replay: no live_only corpus rows selected")
    # One armed parser per world (the replay client is keyed by world).
    total = passed = 0
    failures: List[Dict] = []
    calls = 0
    served = set()
    drifted: Dict = {}
    for world_key in WORLD_KEYS:
        if only_world and world_key != only_world:
            continue
        parser, replay = armed_parser(cassettes, world_key, manifest)
        world = build_world(world_key)
        game_state = build_llm_game_state(world)
        for entry in corpus["entries"]:
            if entry["id"] not in ids or world_key not in worlds_for_entry(entry):
                continue
            total += 1
            try:
                mismatches = evaluate_entry(parser, entry, world_key, world,
                                            game_state)
            except CassetteMiss as miss:
                raise RuntimeError(f"cassette miss on {entry['id']} "
                                   f"[{world_key}]: {miss}") from None
            if mismatches:
                failures.append({"id": entry["id"], "world": world_key,
                                 "utterance": entry["utterance"],
                                 "mismatches": mismatches})
                if verbose:
                    print(f"FAIL [{world_key}] {entry['id']}")
            else:
                passed += 1
                if verbose:
                    print(f"ok   [{world_key}] {entry['id']}")
        calls += len(replay.calls)
        served.update(replay.served)
        drifted.update(replay.drifted)
    return {"total": total, "passed": passed, "failed": len(failures),
            "skipped_live_only": 0, "skipped_mock_only": 0,
            "failures": failures, "replay_calls": calls,
            "replay_cassettes": len(served),
            "replay_drifted": sorted(drifted)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="CR-1 parser eval harness (golden corpus, both worlds)")
    ap.add_argument("--corpus", type=Path, default=None,
                    help="corpus JSON path (default: tests/data/parser_golden_corpus.json)")
    ap.add_argument("--live", action="store_true",
                    help="arm the live LLM provider fallback (needs LLM_MODE + key; "
                         "default is pure mock)")
    ap.add_argument("--replay", action="store_true",
                    help="IQ-9: run the live_only rows KEYLESSLY on the committed "
                         "cassettes (tests/data/parser_cassettes); exit 2 on a "
                         "cassette miss; no network")
    ap.add_argument("--world", choices=WORLD_KEYS, default=None,
                    help="restrict to one world")
    ap.add_argument("--id", action="append", dest="ids", default=None,
                    help="restrict to specific entry id(s)")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)

    corpus = load_corpus(args.corpus)
    if args.replay and args.live:
        print("ERROR: --replay and --live are exclusive (replay is keyless)")
        return 2
    try:
        if args.replay:
            summary = _run_replay(corpus, only_world=args.world,
                                  only_ids=args.ids, verbose=args.verbose)
        else:
            summary = run_corpus(corpus, use_real_llm=args.live,
                                 only_world=args.world, only_ids=args.ids,
                                 verbose=args.verbose)
    except RuntimeError as exc:
        print(f"ERROR: {exc}")
        return 2
    mode_label = "REPLAY" if args.replay else ("LIVE" if args.live else "mock")
    print(f"\nParser eval: {summary['passed']}/{summary['total']} passed "
          f"({mode_label} mode)")
    if args.replay:
        print(f"  (replayed {summary['replay_calls']} live call(s) from "
              f"{summary['replay_cassettes']} cassette(s); "
              f"drifted: {summary['replay_drifted'] or 'none'})")
    if summary.get("skipped_live_only"):
        print(f"  ({summary['skipped_live_only']} live_only entr"
              f"{'y' if summary['skipped_live_only'] == 1 else 'ies'} skipped -- "
              f"run with --live to evaluate)")
    if summary.get("skipped_mock_only"):
        print(f"  ({summary['skipped_mock_only']} mock_only entr"
              f"{'y' if summary['skipped_mock_only'] == 1 else 'ies'} skipped -- "
              f"they pin fast-parser behavior)")
    for failure in summary["failures"]:
        print(f"  FAIL [{failure['world']}] {failure['id']}: {failure['utterance']!r}")
        for m in failure["mismatches"]:
            print(f"       {m}")
    if summary["total"] == 0:
        print("ERROR: zero corpus entries evaluated -- check --id/--world filters")
        return 2
    return 1 if summary["failures"] else 0


if __name__ == "__main__":
    sys.exit(main())
