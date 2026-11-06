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

AU3A_BUYS = ("edict_decreed", "word_given", "honoured", "by_decree")    # §5.3, AU-3a's four
# AU-3b: the crowns and offices — Endow them, the Titles (the Proclamation books `edict_decreed`)
PURCHASES = AU3A_BUYS + ("endowed", "titles_granted")
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
    baseline the reach and the series pins read; the buys live in the spender arm.

    AU-3b armed (the user's "Arm it", November 5, 2026; AUTHORITY_CURRENCY_SPEC.md
    §6.6.6) — one exception, named: the Proclamation's Accept is priced in
    authority ALONE, so where the accept dial issues it the letter's own answer
    books `edict_decreed` — HAITI-historical (T12) and the Rhine road's accept
    arm on historical (T28), 4 authority each, above the purchases' floor (81
    and 82 after). No other purchase on any shipped row."""

    PROCLAIMED = {("haiti", "HAITI-historical"), ("road_accept", "VP1-RH-historical")}

    @pytest.mark.parametrize("row", ROWS, ids=lambda r: f"{r['family']}/{r['arm']}")
    def test_no_purchase_on_a_shipped_row(self, row):
        bought = set(PURCHASES) & set(row.get("by_cause") or {})
        if (row["family"], row["arm"]) in self.PROCLAIMED:
            assert bought == {"edict_decreed"}, row["by_cause"]
            assert row["by_cause"]["edict_decreed"]["n"] == 1 and row["by_cause"]["edict_decreed"]["sum"] == -4
            assert row["lowest_after"]["edict_decreed"] >= standing.PURCHASE_FLOOR
        else:
            assert not bought, row["by_cause"]

    def test_the_proclaimed_rows_are_the_accept_dials(self):
        proclaimed = {(r["family"], r["arm"]) for r in ROWS if "edict_decreed" in (r.get("by_cause") or {})}
        assert proclaimed == self.PROCLAIMED, proclaimed


class TestTheSpenderArm:
    def test_the_nine_commanded_scripts(self):
        commanded = {r["arm"] for r in ROWS if r["family"] == "commanded"}
        assert set(BUYS["runs"]) == commanded and len(commanded) == 9, sorted(BUYS["runs"])

    def test_a_push_in_every_campaign(self):
        assert BUYS["runs_with_a_push"] == sorted(BUYS["runs"]), BUYS["runs_with_a_push"]
        assert all(run["pushes"] > 0 for run in BUYS["runs"].values())

    def test_each_of_the_four_buys_is_taken_or_offered_in_play(self):
        """AU-3b's two are reached by no measured spender run (the Fontainebleau
        card never comes to the nine scripts; no script decrees the Dotations) —
        pinned by `tests/test_standing_offices.py`, reported in §6.6.

        The courts' flip (November 6, 2026, the spender arm re-run on the final
        tree; AUTHORITY_CURRENCY_SPEC.md §6.8) — re-pinned consciously from
        `test_each_of_the_four_buys_is_taken_in_play`: three of AU-3a's four are
        TAKEN (Honour him, By my word, By Decree) and the fourth is OFFERED — the
        Remounts reach four of the nine scripts, eight letters, and their Decree
        stands closed each time at the purchases' floor, the spender's own
        Honours having spent the grip to 61–62 (18 on CMD-M) first; the driver
        never presses a closed answer, so the letter lapses. AU-3a's record took
        it once (CMD-A, turn 38). Seeded paths, not laws: the floor holds."""
        taken = {c for c, n in BUYS["totals"].items() if n > 0}
        assert set(AU3A_BUYS) - {"edict_decreed"} <= taken, BUYS["totals"]
        offered = [o for run in BUYS["runs"].values() for o in run.get("edicts_offered") or []]
        assert offered, "no Edict letter reached the spender"
        price = {"the_magazines": 5, "the_remounts": 3, "camps_of_instruction": 4}   # the deck's `authority`
        for o in offered:                     # a Decree untaken was closed at the floor that morning
            if o["answer"] != "decree":
                cost = price[o["letter"].split("#")[0]]
                assert o["kind"] == "lapse", o                  # the driver never presses a closed answer
                assert o["grip"] is not None and o["grip"] - cost < standing.PURCHASE_FLOOR, o

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
