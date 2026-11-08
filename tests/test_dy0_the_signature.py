"""DY-0 — the Concert's instrument (`DYNAMISM_SPEC.md` §7; the Tier-2 gate
record `AI_INTENT_SPEC.md` §3.8.2; landed at Tier 2's head, November 8,
2026).

What this file pins:

  * THE COLUMNS — `derive_metrics` and `_variance_signature` carry the
    Concert's five (`questions_turned`, `awakening_events`,
    `rank_promotions`, `guarantees_given`, `formations`), derived from the
    run's own rows on the one clock. The three future-tier columns read
    EMPTY today (their event types — `question_turns`, `awakening_*`,
    `rank_promotion` — are the contract their owning tiers must emit), so
    each tier's landing is its own signature change and the assurance
    suite's controls (same seed EQUAL, variance-off EQUAL to historical)
    hold by construction.
  * THE STORY CLASS — the coarse, timing-blind projection (sets, never
    turns): two runs differing only in WHEN share a class; a run differing
    in WHO fought, fell, formed, guaranteed, turned, rose or awoke does
    not. `story_class_count` is the deploy gate's number.
  * THE BASELINE — `tools/_dy_signature_baseline.json`, written by
    `tools/_dy0_baseline.py` running ALONE over the ten ambient
    `SWEEP_SEEDS`: the record's shape, its internal consistency (the count
    equals the distinct classes it itself stores), the future-tier columns
    empty on every seed (nothing emits them yet), and the measured count —
    the pre-band floor the Concert must beat.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tools.ai_v_sweep import (  # noqa: E402
    SWEEP_SEEDS,
    _variance_signature,
    derive_metrics,
    story_class,
    story_class_count,
)

BASELINE = REPO / "tools" / "_dy_signature_baseline.json"

DY0_COLUMNS = ("questions_turned", "awakening_events", "rank_promotions",
               "guarantees_given", "formations")
FUTURE_COLUMNS = ("questions_turned", "awakening_events", "rank_promotions")


def _row(turn, events=(), intents=None, wars_opened=()):
    """A minimal per-turn row carrying every key `derive_metrics` reads."""
    return {
        "turn": int(turn),
        "threat": 0,
        "gold": {},
        "exhaustion": {},
        "mirror": ["", 0, ""],
        "intents": dict(intents or {}),
        "events": list(events),
        "dispatch_queue": [],
        "wars_opened": list(wars_opened),
        "wars_ended": [],
        "incoming_proposals": [],
        "moments_open": 0,
        "foreground_in_tenure": False,
    }


def _digest(rows, formations=None):
    return {
        "meta": {"player": "France", "france_needles": []},
        "turns": list(rows),
        "final": {"formations": dict(formations or {}),
                  "moments": {"state": {}}},
    }


def _derived(rows, formations=None):
    digest = _digest(rows, formations)
    digest["derived"] = derive_metrics(digest)
    return digest


# ═══════════════════════════════════════════════════════════════════════
# The columns
# ═══════════════════════════════════════════════════════════════════════
class TestTheColumns:
    def test_the_five_ride_derived_and_signature(self):
        digest = _derived([_row(1)])
        for column in DY0_COLUMNS:
            assert column in digest["derived"], column
            assert column in _variance_signature(digest), column

    def test_a_guarantee_pledged_is_a_row(self):
        digest = _derived([_row(3, events=[
            {"type": "guarantee_pledged", "guarantor": "France",
             "protected": "Hanover"}])])
        assert digest["derived"]["guarantees_given"] == [
            [3, "France", "Hanover"]]

    def test_the_future_tier_contract_types_derive(self):
        """The event types the owning tiers MUST emit (§3.8.2's contract):
        Tier 5 `question_turns`, Tier 4 `rank_promotion`, Tier 6
        `awakening_*` — each lands as its column's row the day it exists."""
        digest = _derived([_row(5, events=[
            {"type": "question_turns", "question": "the_german_question"},
            {"type": "rank_promotion", "nation": "Saxony"},
            {"type": "awakening_risen", "nation": "Spain"}])])
        derived = digest["derived"]
        assert derived["questions_turned"] == [[5, "the_german_question"]]
        assert derived["rank_promotions"] == [[5, "Saxony"]]
        assert derived["awakening_events"] == [[5, "Spain"]]

    def test_formations_promoted_from_the_final_block(self):
        digest = _derived([_row(1)], formations={"Germany": {"turn": 30}})
        assert digest["derived"]["formations"] == ["Germany"]
        assert _variance_signature(digest)["formations"] == ["Germany"]

    def test_empty_on_a_bare_board(self):
        derived = _derived([_row(1), _row(2)])["derived"]
        for column in DY0_COLUMNS:
            assert derived[column] == [], column


# ═══════════════════════════════════════════════════════════════════════
# The story class — coarse and timing-blind
# ═══════════════════════════════════════════════════════════════════════
class TestTheStoryClass:
    WAR = {"attackers": ["Prussia"], "defenders": ["Hanover"],
           "ai_initiated": True}

    def test_timing_blind(self):
        """Two runs in which the same war opens on DIFFERENT turns and the
        same court falls on different turns are the SAME story."""
        early = _derived([
            _row(2, wars_opened=[dict(self.WAR)]),
            _row(3, events=[{"type": "nation_eliminated",
                             "nation": "Hanover"}])])
        late = _derived([
            _row(9, wars_opened=[dict(self.WAR)]),
            _row(14, events=[{"type": "nation_eliminated",
                              "nation": "Hanover"}])])
        assert story_class(early) == story_class(late)
        assert _variance_signature(early) != _variance_signature(late)

    def test_a_different_fate_is_a_different_class(self):
        fell = _derived([
            _row(2, wars_opened=[dict(self.WAR)]),
            _row(3, events=[{"type": "nation_eliminated",
                             "nation": "Hanover"}])])
        survived = _derived([_row(2, wars_opened=[dict(self.WAR)])])
        assert story_class(fell) != story_class(survived)

    def test_the_fight_roster_is_in_the_class(self):
        quiet = _derived([_row(1, intents={
            "Austria": ["", "", 0, "press"]})])
        fighting = _derived([_row(1, intents={
            "Austria": ["", "", 0, "fight"]})])
        assert story_class(quiet) != story_class(fighting)

    def test_the_count_is_distinct_classes(self):
        a = story_class(_derived([_row(1)]))
        b = story_class(_derived([_row(2)]))        # timing only — same
        c = story_class(_derived([_row(1, wars_opened=[dict(self.WAR)])]))
        assert story_class_count([a, b, c]) == 2


# ═══════════════════════════════════════════════════════════════════════
# The baseline record
# ═══════════════════════════════════════════════════════════════════════
@pytest.fixture(scope="module")
def baseline():
    return json.loads(BASELINE.read_text(encoding="utf-8"))


class TestTheBaseline:
    def test_ten_seeds_every_one_measured(self, baseline):
        assert sorted(baseline["seeds"]) == sorted(SWEEP_SEEDS)
        for seed, row in baseline["seeds"].items():
            assert row["signature"], seed
            assert row["story_class"], seed

    def test_the_count_is_the_records_own_distinct_classes(self, baseline):
        classes = [json.dumps(baseline["seeds"][s]["story_class"],
                              sort_keys=True) for s in SWEEP_SEEDS]
        assert baseline["story_class_count"] == len(set(classes))

    def test_the_future_tier_columns_are_empty_on_every_seed(self, baseline):
        """Nothing emits `question_turns`, `rank_promotion` or
        `awakening_*` yet — a nonzero here before Tiers 4–6 land is a
        contract leak, not progress."""
        for seed, row in baseline["seeds"].items():
            for column in FUTURE_COLUMNS:
                assert row["signature"][column] == [], (seed, column)
            for key, values in row["story_class"]:
                if key in ("questions", "promotions", "awakened"):
                    assert values == [], (seed, key)

    def test_the_measured_floor(self, baseline):
        """The pre-band floor, byte-pinned — the Concert's tiers must move
        it, and the deploy gate re-measures (>= 4 of 10). Re-seat with the
        re-run baseline when a tier lands, cause quoted."""
        assert baseline["story_class_count"] == STORY_CLASS_COUNT_BASELINE

    def test_the_one_shared_class_is_eylau_and_rivoli(self, baseline):
        """The chain's own grouping (November 8, 2026): nine distinct
        stories on the ten pre-band seeds — eylau and rivoli alone share
        one. A coarser or finer read of the SAME record is a class-function
        change and re-seats here with its cause."""
        grouped = {}
        for seed in SWEEP_SEEDS:
            key = json.dumps(baseline["seeds"][seed]["story_class"],
                             sort_keys=True)
            grouped.setdefault(key, []).append(seed)
        shared = sorted(members for members in grouped.values()
                        if len(members) > 1)
        assert shared == [["eylau", "rivoli"]], shared


# The measured pre-band floor (the chain of November 8, 2026 — ten ambient
# seeds x 40 turns at K=10000): NINE distinct stories of ten. The deploy
# gate's bar is >= 4 of 10, measured at the gate on the full board.
STORY_CLASS_COUNT_BASELINE = 9
