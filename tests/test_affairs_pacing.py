"""RE-1 — the affairs' pacing, measured and pinned (`docs/RECURRING_EVENTS_SPEC.md`
§7, §0b P8, §17b "the first affair about T13 — UNVERIFIED until RE-1").

`tools/_affairs_first_arrival_probe.py` grafts the staged deck
(`tests/fixtures/affairs_block.json`) on the shipped boot and plays the passive
board (the series harness's own loop) to turn 20 on the ten `SWEEP_SEEDS`,
twice per seed — the CONTROL (unarmed, as shipped) and the ARMED arm — with the
moments' trace installed. The record `tools/_affairs_first_arrival.json` is
read here: the moments' arrival turns identical on both arms (§7: the moments
are blind to affairs); no ceiling or floor breach; the first affair per seed
reported, never a law. The look-ahead itself (P8) is pinned on a crafted
morning in `tests/test_affairs_engine.py`.
"""
import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
RECORD = REPO / "tools" / "_affairs_first_arrival.json"
FIXTURE = REPO / "tests" / "fixtures" / "affairs_block.json"
SWEEP_SEEDS = ["historical", "ulm", "austerlitz", "jena", "marengo",
               "eylau", "friedland", "wagram", "lodi", "rivoli"]


@pytest.fixture(scope="module")
def record():
    return json.loads(RECORD.read_text(encoding="utf-8"))


class TestTheRecordMeasuredTheStagedDeck:
    def test_the_record_carries_the_fixture_s_mechanical_identity(self, record):
        from tools._s14c_sweep_record import deck_sha
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        assert record["fixture_sha"] == deck_sha(fixture), (
            "the staged deck's mechanics changed since the probe ran — re-run "
            "tools/_affairs_first_arrival_probe.py")
        assert record["affairs"] == ["chancellors_letters", "the_host", "berthiers_memorial"]

    def test_every_seed_was_played_on_both_arms_to_turn_twenty(self, record):
        assert record["turns"] == 20
        assert sorted(record["seeds"]) == sorted(SWEEP_SEEDS)
        for seed, arms in record["seeds"].items():
            assert set(arms) == {"control", "armed"}, seed
            for arm in arms.values():
                assert arm["last_turn"] == 21 and arm["errors"] == [], (seed, arm["errors"])


class TestTheMomentsAreBlindOnEverySeed:
    @pytest.mark.parametrize("seed", SWEEP_SEEDS)
    def test_the_moments_arrival_turns_are_identical_armed_against_unarmed(self, record, seed):
        arms = record["seeds"][seed]
        assert arms["armed"]["moments"] == arms["control"]["moments"], seed
        assert arms["control"]["affairs"] == {}                     # unarmed: no occurrence row

    @pytest.mark.parametrize("seed", SWEEP_SEEDS)
    def test_the_ceilings_and_the_floors_hold_on_the_armed_arm(self, record, seed):
        judged = record["seeds"][seed]["armed"]["judged"]
        assert judged["ceiling_breaches"] == [] and judged["floor_breaches"] == [], seed
        assert judged["shown_equals_applied"] is True
        assert all(f["verdict"] in ("ok", "pending", "released") for f in judged["floors"].values())


class TestTheFirstArrivalIsReportedPerSeed:
    """Seeded paths, not laws (§10). The passive board keeps the Emperor at home
    and no second corps on an ally's soil, so T1 and T2 never premise there;
    the door opens where the hoard clears the Staff's bar."""

    def test_the_first_affair_per_seed(self, record):
        firsts = {seed: arms["armed"]["first_affair"] for seed, arms in record["seeds"].items()}
        reached = {seed: f for seed, f in firsts.items() if f}
        assert set(reached) == {"ulm", "austerlitz"}, reached
        assert all(f["id"] == "berthiers_memorial#1" and f["turn"] == 19 for f in reached.values())

    def test_every_occurrence_is_the_doors_and_lapsed_on_a_passive_france(self, record):
        for seed, arms in record["seeds"].items():
            for mid, row in arms["armed"]["affairs"].items():
                assert mid.startswith("berthiers_memorial#"), (seed, mid)
                assert row["status"] == "lapsed" and row["bind"] == {"law": "grand_quartier_general"}, (seed, row)
                assert row["tier"] == 1

    def test_the_streaks_build_where_the_premise_holds_and_nothing_is_due_at_the_end(self, record):
        for seed, arms in record["seeds"].items():
            armed = arms["armed"]
            assert armed["due"] == {}, seed
            assert all(isinstance(v, int) and v >= 1 for v in armed["streaks"].values()), seed
