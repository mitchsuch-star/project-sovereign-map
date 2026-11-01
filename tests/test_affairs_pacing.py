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
        # RE-H (November 1, 2026): the fourth letter, the Haiti letter
        assert record["affairs"] == ["chancellors_letters", "the_host", "berthiers_memorial", "santo_domingo"]

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
    the door opens where the hoard clears the Staff's bar. RE-H (November 1,
    2026 — the user's word, "conditions that make them appear"): the Haiti
    letter premises on that board — the Emperor at home, Britain's blockade
    from the opening, 45 sail, the chest past the Marine's bar by turn 5 —
    and with `bites: "floor"` it is the campaign's FIRST affair on nine of
    the ten seeds, on the pulse's first morning (T6–T9, the band); on wagram
    the premise fell before the pulse opened (the Emperor driven from home)."""

    def test_the_first_affair_per_seed(self, record):
        firsts = {seed: arms["armed"]["first_affair"] for seed, arms in record["seeds"].items()}
        reached = {seed: f for seed, f in firsts.items() if f}
        assert set(reached) == set(SWEEP_SEEDS) - {"wagram"}, reached
        assert all(f["id"] == "santo_domingo#1" and 6 <= f["turn"] <= 9 for f in reached.values()), reached
        assert reached["historical"]["turn"] == 7                  # the authored `first`

    def test_every_occurrence_is_lapsed_on_a_passive_france(self, record):
        """The unattended France answers nothing: every letter lapses to its
        Decline — the Haiti letter's rows bind the Emperor's seat, the door's
        bind the Staff; both at tier 1."""
        for seed, arms in record["seeds"].items():
            rows = arms["armed"]["affairs"]
            assert all(mid.startswith(("santo_domingo#", "berthiers_memorial#")) for mid in rows), (seed, list(rows))
            for mid, row in rows.items():
                assert row["status"] == "lapsed" and row["tier"] == 1, (seed, row)
                if mid.startswith("berthiers_memorial#"):
                    assert row["bind"] == {"law": "grand_quartier_general"}, (seed, row)
                else:
                    assert set(row["bind"]) == {"region", "sovereign"} and row["bind"]["sovereign"] == "Napoleon", (seed, row)
        with_door = {seed for seed, arms in record["seeds"].items()
                     if any(m.startswith("berthiers_memorial#") for m in arms["armed"]["affairs"])}
        assert with_door == {"ulm", "austerlitz"}, with_door             # as at RE-1, the door's seeds

    def test_the_streaks_build_where_the_premise_holds_and_nothing_is_due_at_the_end(self, record):
        for seed, arms in record["seeds"].items():
            armed = arms["armed"]
            assert armed["due"] == {}, seed
            assert all(isinstance(v, int) and v >= 1 for v in armed["streaks"].values()), seed
