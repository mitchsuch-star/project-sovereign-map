"""CR-7-2 — "The harness can see it" (the Command-Road Queue, CR-7 slice 2).

Build contract: `docs/audits/COMPOUND_CONDITIONAL_COMMANDS_2026_09_20.md`
§CR-7-2. Measured on this HEAD before a line was written (September 22,
2026): `ALLOWED_EXPECTED_KEYS` was 11 keys; of 449 corpus rows, 24 carried
a compound/conditional marker and 0 asserted `strategic_condition`,
`dropped_sequel` or `attack_on_arrival`; and `evaluate_entry` had no
unknown-key arm, so a row asserting `dropped_sequel` with a deliberately
WRONG value reported PASS on the CLI (the hygiene gate lives in pytest,
not in the CLI — a CLI-green run was not evidence).

Now the four keys are evaluated, the CLI REFUSES an unknown key, the marker
rows carry the value they actually produce, and the CR-7 rows the harness
could never express are in the corpus.

THE ONE THING IT STILL CANNOT DO (recorded, per the contract): the entry
schema has no key for a PRIOR command, so CR-4 context carryover ("again",
"same target", "him") is structurally uncoverable by corpus and its pins
live in pytest (`test_command_robustness_cr4_context_carryover.py`).
"""

import contextlib
import io

import pytest

from backend.ai.parser_eval import (
    ALLOWED_EXPECTED_KEYS,
    build_llm_game_state,
    build_world,
    evaluate_entry,
    load_corpus,
)
from backend.commands.parser import CommandParser

NEW_KEYS = {"dropped_sequel", "warning_contains", "strategic_condition",
            "attack_on_arrival"}


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


@pytest.fixture(scope="module")
def ctx():
    with _quiet():
        world = build_world("1805")
        state = build_llm_game_state(world)
        parser = CommandParser(use_real_llm=False)
    return parser, world, state


def _eval(ctx, utterance, expected):
    parser, world, state = ctx
    entry = {"id": "probe", "utterance": utterance, "world": "1805",
             "expected": expected}
    with _quiet():
        return evaluate_entry(parser, entry, "1805", world, state)


class TestTheKeysExist:

    def test_the_four_keys_are_allowed(self):
        assert NEW_KEYS <= ALLOWED_EXPECTED_KEYS

    def test_the_eleven_old_keys_are_untouched(self):
        old = {"success", "marshal", "action", "not_action", "target", "type",
               "strategic_type", "target_stance", "requested_type",
               "error_contains", "diplo"}
        assert old <= ALLOWED_EXPECTED_KEYS
        assert len(ALLOWED_EXPECTED_KEYS) == 15


class TestTheDoneWhen:
    """A row asserting `dropped_sequel: "attack Mack"` against a sentence
    that drops something ELSE must FAIL — today it passed."""

    def test_a_wrong_dropped_sequel_fails(self, ctx):
        mismatches = _eval(ctx, "Ney, fortify then hold Lorraine",
                           {"action": "fortify", "dropped_sequel": "attack Mack"})
        assert any(m.startswith("dropped_sequel") for m in mismatches), mismatches

    def test_the_right_dropped_sequel_passes(self, ctx):
        assert _eval(ctx, "Ney, fortify then attack Mack",
                     {"action": "fortify", "dropped_sequel": "attack Mack"}) == []

    def test_null_pins_nothing_dropped(self, ctx):
        assert _eval(ctx, "Ney, march to Swabia then attack Mack",
                     {"strategic_type": "MOVE_TO", "dropped_sequel": None}) == []
        mismatches = _eval(ctx, "Ney, fortify then attack Mack",
                           {"action": "fortify", "dropped_sequel": None})
        assert any(m.startswith("dropped_sequel") for m in mismatches), mismatches

    def test_attack_on_arrival_arm(self, ctx):
        assert _eval(ctx, "Ney, march to Swabia then attack Mack",
                     {"strategic_type": "MOVE_TO", "attack_on_arrival": True}) == []
        mismatches = _eval(ctx, "Ney, march to Swabia",
                           {"strategic_type": "MOVE_TO", "attack_on_arrival": True})
        assert any(m.startswith("attack_on_arrival") for m in mismatches), mismatches

    def test_strategic_condition_arm(self, ctx):
        assert _eval(ctx, "Davout, hold Lorraine until Ney arrives",
                     {"strategic_type": "HOLD",
                      "strategic_condition": {"until_marshal_arrives": "Ney"}}) == []
        mismatches = _eval(ctx, "Davout, hold Lorraine until Ney arrives",
                           {"strategic_type": "HOLD",
                            "strategic_condition": {"until_relieved": True}})
        assert any(m.startswith("strategic_condition") for m in mismatches), mismatches

    def test_warning_contains_arm(self, ctx):
        assert _eval(ctx, "Ney, fortify then attack Mack",
                     {"action": "fortify", "warning_contains": "One order at a time"}) == []
        mismatches = _eval(ctx, "Ney, fortify then attack Mack",
                           {"action": "fortify", "warning_contains": "must follow as its own"})
        assert any(m.startswith("warning_contains") for m in mismatches), mismatches

    def test_the_cli_refuses_an_unknown_key(self, ctx):
        """The hygiene gate forbids committing such a row; this makes the
        CLI say so instead of silently passing it."""
        mismatches = _eval(ctx, "Ney, attack Mack",
                           {"action": "attack", "dropped_seqel": "typo"})
        assert mismatches and "unknown expected key" in mismatches[0], mismatches


class TestTheCorpusCarriesTheValues:

    def test_the_marker_rows_now_assert_a_compound_key(self):
        corpus = load_corpus()
        by_id = {e["id"]: e for e in corpus["entries"]}
        amended = [
            "grouchy-hold-belgium-until-ney-arrives",
            "cr2-attack-bern-then-hold-sequential",
            "cr2-march-to-vienna-then-attack-not-split",
            "parseneg-until-then-attack-holds",
            "fa7-wait-for-then-attack-does-not-fight",
            "fa50-semicolon-splits-and-warns",
        ]
        for rid in amended:
            assert set(by_id[rid]["expected"]) & NEW_KEYS, rid
        carrying = [e for e in corpus["entries"] if set(e["expected"]) & NEW_KEYS]
        assert len(carrying) >= 25, len(carrying)   # 15 amended + the cr7-* rows

    def test_the_cr7_rows_are_green_on_the_1805_board(self, ctx):
        parser, world, state = ctx
        corpus = load_corpus()
        rows = [e for e in corpus["entries"] if e["id"].startswith("cr7-")]
        assert len(rows) >= 18, len(rows)
        failures = {}
        for entry in rows:
            with _quiet():
                mismatches = evaluate_entry(parser, entry, "1805", world, state)
            if mismatches:
                failures[entry["id"]] = mismatches
        assert not failures, failures

    def test_the_unmodified_rows_still_pass_the_hygiene_shape(self):
        corpus = load_corpus()
        for entry in corpus["entries"]:
            unknown = set(entry["expected"]) - ALLOWED_EXPECTED_KEYS
            assert not unknown, (entry["id"], unknown)
