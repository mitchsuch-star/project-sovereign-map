"""
CR-1 Parser Eval Harness — the Command Robustness phase's regression gate
(COMMAND_ROBUSTNESS_SPEC.md slice CR-1).

Runs the golden parse corpus (tests/data/parser_golden_corpus.json) through
the production call shape parser.parse(utterance, llm_game_state, world=world)
in MOCK mode over both scenario worlds. Engine: backend/ai/parser_eval.py
(the same engine the on-demand live-provider CLI uses:
`python -m backend.ai.parser_eval --live`).

Gates enforced here beyond the per-entry expectations:
  - corpus hygiene (unique ids, known world tags, allowed expectation keys)
  - action coverage: every MOCK-reachable action id has >= 1 corpus entry —
    adding a new action to the parser without corpus coverage fails CI
    (extends the "Adding a new action" checklist in CLAUDE.md).

Land behavior changes AFTER this suite is green against them: expectation
churn here is the review artifact CR-2..CR-5 are measured by.
"""

import pytest

from backend.ai.parser_eval import (
    ALLOWED_DIPLO_KEYS,
    ALLOWED_EXPECTED_KEYS,
    WORLD_KEYS,
    build_llm_game_state,
    build_world,
    evaluate_entry,
    load_corpus,
    worlds_for_entry,
)
from backend.commands.parser import CommandParser

CORPUS = load_corpus()

# Every action id the MOCK keyword chain can produce (from the CR-1 audit of
# llm_client._parse_with_mock; diplomatic ids surface via diplomatic_data).
# If you add an action the mock can parse, add a corpus entry for it.
MOCK_REACHABLE_ACTIONS = [
    "attack", "defend", "retreat", "move", "scout", "recruit", "help",
    "end_turn", "status", "wait", "hold", "cancel", "charge", "restrain",
    "drill", "fortify", "unfortify", "stance_change", "build", "repair",
    "economy", "garrison", "form_square", "break_square",
    "invest_vassal", "change_autonomy", "make_vassal", "release_vassal",
    "cheat", "debug", "meta_command",
    "diplomatic_proposal", "diplomatic_mission", "diplomatic_declare_war",
    "diplomatic_ultimatum", "diplomatic_break", "diplomatic_error",
    # Review-round additions — these route through the diplomatic keyword
    # families and ARE mock-reachable (the first hand-built list missed them)
    "make_amends", "request_terms", "set_war_purpose", "repudiate_bargain",
    # ES-7 Estate Endowment (Economy Revisit S7)
    "grant_dotation",
    # W6-9 (EXP-D1): the strategic assessment verb — mock-reachable via the
    # assess/situation keyword branch AND the question path.
    "diplomatic_advisory",
]


@pytest.fixture(scope="module")
def parser():
    return CommandParser(use_real_llm=False)


@pytest.fixture(scope="module")
def contexts():
    """(world, llm_game_state) per world key — built once."""
    return {
        world_key: ((world := build_world(world_key)),
                    build_llm_game_state(world))
        for world_key in WORLD_KEYS
    }


def _corpus_params():
    params = []
    for entry in CORPUS["entries"]:
        # live_only entries assert a LIVE-LLM behavior (CR-5 delegation bias) —
        # under mock they degrade to ASK, so they are unobservable here. They are
        # exercised on demand via `python -m backend.ai.parser_eval --live`.
        if entry.get("live_only"):
            continue
        for world_key in worlds_for_entry(entry):
            params.append(pytest.param(entry, world_key,
                                       id=f"{entry['id']}[{world_key}]"))
    return params


@pytest.mark.parametrize("entry,world_key", _corpus_params())
def test_corpus_entry(parser, contexts, entry, world_key):
    world, game_state = contexts[world_key]
    mismatches = evaluate_entry(parser, entry, world_key, world, game_state)
    assert not mismatches, (
        f"{entry['id']} on {world_key}: {entry['utterance']!r}\n  "
        + "\n  ".join(mismatches)
        + f"\n  (source: {entry.get('source', '?')})"
    )


# ═══════════════════════════════════════════════════════════════════
# Corpus hygiene
# ═══════════════════════════════════════════════════════════════════

class TestCorpusHygiene:

    def test_ids_unique(self):
        ids = [e["id"] for e in CORPUS["entries"]]
        assert len(ids) == len(set(ids))

    def test_world_tags_valid(self):
        for entry in CORPUS["entries"]:
            assert entry.get("world") in ("legacy", "1805", "any"), entry["id"]

    def test_expected_keys_allowed(self):
        for entry in CORPUS["entries"]:
            assert entry.get("expected"), f"{entry['id']}: empty expected block"
            unknown = set(entry["expected"]) - ALLOWED_EXPECTED_KEYS
            assert not unknown, f"{entry['id']}: unknown expected keys {unknown}"
            diplo = entry["expected"].get("diplo")
            if diplo:
                unknown = set(diplo) - ALLOWED_DIPLO_KEYS
                assert not unknown, f"{entry['id']}: unknown diplo keys {unknown}"

    def test_failure_entries_carry_no_dead_command_expectations(self):
        """A success:false entry early-returns before command-field checks —
        command keys on such entries are dead weight that reads as
        assertions (review finding: ney-xyzzy carried a marshal key that
        was never evaluated and would have failed)."""
        allowed_on_failure = {"success", "error_contains", "not_action"}
        for entry in CORPUS["entries"]:
            if entry["expected"].get("success") is False:
                dead = set(entry["expected"]) - allowed_on_failure
                assert not dead, (
                    f"{entry['id']}: success:false entry carries never-"
                    f"evaluated keys {dead}")

    def test_error_contains_only_on_failure_entries(self):
        """error_contains asserts the FAILURE message — on a success entry
        it silently never fires."""
        for entry in CORPUS["entries"]:
            if "error_contains" in entry["expected"]:
                assert entry["expected"].get("success") is False, (
                    f"{entry['id']}: error_contains requires success:false")

    def test_expected_actions_are_known_ids(self, parser):
        """Positive action expectations must be real action ids (parser
        valid_actions, the mock's meta ids, or 'unknown')."""
        known = set(parser.valid_actions) | {
            "meta_command", "cheat", "unknown",
            "diplomatic_proposal", "diplomatic_mission",
            "diplomatic_feasibility", "diplomatic_advisory",
            "diplomatic_error", "diplomatic_break", "diplomatic_downgrade",
            "diplomatic_declare_war", "diplomatic_ultimatum",
        }
        for entry in CORPUS["entries"]:
            action = entry["expected"].get("action")
            if action is not None:
                assert action in known, f"{entry['id']}: unknown action {action!r}"


# ═══════════════════════════════════════════════════════════════════
# Action coverage gate
# ═══════════════════════════════════════════════════════════════════

class TestActionCoverage:

    def test_every_mock_reachable_action_has_a_corpus_entry(self):
        covered = set()
        for entry in CORPUS["entries"]:
            action = entry["expected"].get("action")
            if action:
                covered.add(action)
            diplo = entry["expected"].get("diplo") or {}
            if diplo.get("action"):
                covered.add(diplo["action"])
        missing = [a for a in MOCK_REACHABLE_ACTIONS if a not in covered]
        assert not missing, (
            f"Mock-reachable actions with NO corpus coverage: {missing} — "
            "add a golden-corpus entry per action (tests/data/"
            "parser_golden_corpus.json); this gate extends the new-action "
            "checklist."
        )

    def test_live_phrasing_backlog_present(self):
        """The CR-3 verb-coverage backlog rides the corpus file — keep the
        section (Golden Rule 9: it is the owner record for those
        phrasings)."""
        backlog = CORPUS.get("live_phrasing_backlog", {})
        assert backlog.get("utterances"), "live_phrasing_backlog missing/empty"
        assert "CR-3" in backlog.get("description", "")


# ═══════════════════════════════════════════════════════════════════
# Production-payload sync pin
# ═══════════════════════════════════════════════════════════════════

class TestGameStateMirrorSync:

    @pytest.mark.parametrize("world_key", WORLD_KEYS)
    def test_build_llm_game_state_matches_production(self, contexts, world_key,
                                                     monkeypatch):
        """The harness mirror must produce BYTE-IDENTICAL payloads to
        backend.main.get_llm_game_state() — the corpus (and the --live
        prompts built from map_data) are only meaningful against the
        production shape (review finding: the first mirror hardcoded
        map_data marshals=[] and every marshal-occupied region diverged)."""
        import backend.main as main_module
        world, harness_gs = contexts[world_key]
        monkeypatch.setattr(main_module, "world", world)
        production_gs = main_module.get_llm_game_state()
        assert harness_gs == production_gs, (
            f"build_llm_game_state diverges from backend.main."
            f"get_llm_game_state on the {world_key} world — update "
            f"backend/ai/parser_eval.py to match production")


# ═══════════════════════════════════════════════════════════════════
# The status wire (CR-1 fix landed with this slice)
# ═══════════════════════════════════════════════════════════════════

class TestStatusWire:

    def test_typed_status_parses(self, parser, contexts):
        """'status' was in VALID_ACTIONS, the mock, and the executor's
        free_actions — but missing from parser.valid_actions, so the typed
        form died at validation and fell to Berthier recovery."""
        for world_key in WORLD_KEYS:
            world, game_state = contexts[world_key]
            result = parser.parse("status", game_state, world=world)
            assert result["success"], result.get("error")
            assert result["command"]["action"] == "status"
