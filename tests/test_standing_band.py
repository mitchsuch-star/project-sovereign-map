"""AU-3a — the band pin (AUTHORITY_CURRENCY_SPEC.md §5.8, the landing record
§6.5): the standing's two committed records read per arm class.

- every row: `residual` 0 (the books explain every morning's change), and no
  dent ends under its floor — the purchases 60 (`standing.PURCHASE_FLOOR`), the
  letters' Declines 71 (`moments.AUTHORITY_GRIP_FLOOR`), the Claims 80
  (`standing.CLAIMS_FLOOR`); the laws keep their ruled quote and no floor
  (§4.1 reading 1). The record holds the standing after each dent and the
  floors are kept on the grip, which never stands above the player's standing
  (`authority.get_imperial_grip` only subtracts), so the standing's figure is
  the weaker reading of the same rule;
- the spender arm (`tools/_standing_buys.json`, the nine commanded scripts
  answered by a spender) and the war arms (the played and swept campaigns of
  `tools/_standing_final.json`) show, ON THE CLASS, a choice crossing under 85
  and a regrowth applied by play; the spender pushes in every campaign (§10);
- the ruin arms (the unattended France of the VP-1 roads), the saves and the
  probe: the first two only.

Min / max / end are reported per seed in the records and asserted nowhere
(seeded paths, not laws).
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from backend.game_logic import moments, standing

REPO = Path(__file__).resolve().parents[1]
SHIPPED = json.loads((REPO / "tools" / "_standing_final.json").read_text(encoding="utf-8"))
BUYS = json.loads((REPO / "tools" / "_standing_buys.json").read_text(encoding="utf-8"))

PURCHASES = ("edict_decreed", "word_given", "honoured", "by_decree")    # §5.3, AU-3a's four
# a price the Emperor chose to pay: the purchases and the priced answers
CHOICES = PURCHASES + ("letter_declined", "law", "act", "breach", "talleyrand_overruled",
                       "sabotage_confronted", "sabotage_overlooked", "fontainebleau_promise",
                       "redemption_dismissal")
FLOORS = dict({c: standing.PURCHASE_FLOOR for c in PURCHASES},
              letter_declined=moments.AUTHORITY_GRIP_FLOOR, claims=standing.CLAIMS_FLOOR)
# standing coming back by play (§5.5 and the field's own)
REGROWTH = ("field_won", "capital_taken", "own_hand_won", "bulletin", "bulletin_repaid", "te_deum",
            "return", "honour_repaid", "ceremony", "design_reward", "amends", "balanced_hand",
            "insisted_won", "compromise_won")
WAR = ("commanded", "accept", "haiti", "reach_aar", "enacts", "sweep")
FIRST_TWO_ONLY = ("road", "road_accept", "saves", "probe")

ROWS = [r for r in SHIPPED["rows"] if r.get("measured")]


def _regrown(row) -> int:
    return sum(int(v.get("sum", 0) or 0) for c, v in (row.get("by_cause") or {}).items()
               if c in REGROWTH and int(v.get("sum", 0) or 0) > 0)


class TestTheFloorsTable:
    def test_the_floors_are_the_codes(self):
        assert standing.PURCHASE_FLOOR == 60
        assert moments.AUTHORITY_GRIP_FLOOR == 71
        assert standing.CLAIMS_FLOOR == 80

    def test_every_measured_row_is_classed(self):
        families = {r["family"] for r in ROWS}
        assert families <= set(WAR) | set(FIRST_TWO_ONLY), families - set(WAR) - set(FIRST_TWO_ONLY)
        assert SHIPPED["measured"] == SHIPPED["arms"] >= 55 and SHIPPED["unmeasured"] == []


class TestTheFirstTwoOnEveryRow:
    @pytest.mark.parametrize("row", ROWS, ids=lambda r: f"{r['family']}/{r['arm']}")
    def test_the_shipped_row_explains_its_mornings_and_keeps_the_floors(self, row):
        assert row["residual_total"] == 0 and row["residual_unexplained"] == 0, row["residual_sites"]
        assert "lowest_after" in row, "the record predates the band's fields: re-compose it"
        for cause, floor in FLOORS.items():
            low = row["lowest_after"].get(cause)
            assert low is None or low >= floor, (cause, low, floor)

    @pytest.mark.parametrize("name", sorted(BUYS["runs"]))
    def test_the_spender_run_explains_its_mornings_and_keeps_the_floors(self, name):
        run = BUYS["runs"][name]
        assert run["status"] == "completed", run["status"]
        assert run["residual"]["total"] == 0 and run["residual"]["unexplained"] == 0, run["residual"]
        assert run["lowest_after_a_buy"] is None or run["lowest_after_a_buy"] >= standing.PURCHASE_FLOOR, run


class TestTheShippedMeasureBuysNothing:
    """The default dials answer no buy, so the shipped records are the unbought
    baseline the reach and the series pins read; the buys live in the spender arm."""

    @pytest.mark.parametrize("row", ROWS, ids=lambda r: f"{r['family']}/{r['arm']}")
    def test_no_purchase_on_a_shipped_row(self, row):
        assert not set(PURCHASES) & set(row.get("by_cause") or {}), row["by_cause"]


class TestTheSpenderArm:
    def test_the_nine_commanded_scripts(self):
        commanded = {r["arm"] for r in ROWS if r["family"] == "commanded"}
        assert set(BUYS["runs"]) == commanded and len(commanded) == 9, sorted(BUYS["runs"])

    def test_a_push_in_every_campaign(self):
        assert BUYS["runs_with_a_push"] == sorted(BUYS["runs"]), BUYS["runs_with_a_push"]
        assert all(run["pushes"] > 0 for run in BUYS["runs"].values())

    def test_each_of_the_four_buys_is_taken_in_play(self):
        assert {c for c, n in BUYS["totals"].items() if n > 0} == set(PURCHASES), BUYS["totals"]

    def test_the_class_crosses_85_by_a_buy_and_regrows_by_play(self):
        assert any(run["a_buy_crossed_85"] for run in BUYS["runs"].values())
        assert any(run["regrowth"] > 0 for run in BUYS["runs"].values())


class TestTheWarArms:
    def test_the_class_crosses_85_by_a_choice_and_regrows_by_play(self):
        war = [r for r in ROWS if r["family"] in WAR]
        assert war
        assert any(set(CHOICES) & set(r.get("crossed_85_by") or {}) for r in war), \
            [r["crossed_85_by"] for r in war]
        assert any(_regrown(r) > 0 for r in war)
