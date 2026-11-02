"""RE-3 — "Affairs of State": the reach, re-measured on the live tree (ERR-3;
`docs/RECURRING_EVENTS_SPEC.md` §16 "RE-3" done-when, §14 the brakes, §0b
P6 "stays an event"; the landing record §21), read off the committed record
`tools/_s14c_sweep_final.json` — composed by `tools/_affairs_measure.py
record` (`tools/_s14c_sweep_record.py`) from the nine commanded arms, the
three accept arms, the nine road arms and Road I answered, the 21 sweep
runs, the treaty road REACH-AAR and the six hand-played DD-B starts, every
run carrying the moments' trace; the road arms beside an UNARMED control
run on the same commit (`road_control`). Seeded paths, not laws: each
template's reach is reported per arm, and the record says why where it did
not arrive. A deck whose MECHANICS change reds the hash pin until the
measure is run again.

RE-H H0 (November 1, 2026; `RECURRING_EVENTS_SPEC.md` §22.1): the fourth
letter, the Haiti letter, joins the record — re-measured on the same 52 runs
with the control held unarmed through the driver's own seam; the standing
figures read for the first time (REH-1 — the record tool read the button's
word "standing" while the Decline's quote says "Authority").
"""
import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
RECORD = REPO / "tools" / "_s14c_sweep_final.json"
SCENARIO = REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
FAMILIES = ("sweep", "commanded", "accept", "road", "road_accept", "reach_aar", "saves", "haiti")
SCRIPTED = ("commanded", "accept", "road", "road_accept", "reach_aar")
# RE-H (§22.2, reading 7): the family that SAILS the squadron — a passive France
# at home under Britain's blockade with the accept dial, three seeds — and,
# since ERR-5 (the at-home clause dropped), the Rhine road's accept arm on
# `historical`; the other runs never sail one (the passive runs lapse every
# letter, the treaty road declines, the commanded driver makes peace with
# Britain before the pulse finds the letter a morning).
HAITI_ARMS = ("HAITI-historical", "HAITI-austerlitz", "HAITI-marengo")
TEMPLATES = ("chancellors_letters", "the_host", "berthiers_memorial", "santo_domingo")
H1 = "santo_domingo"
ACT = 20                      # §14: "an act" — twenty turns


@pytest.fixture(scope="module")
def record():
    return json.loads(RECORD.read_text(encoding="utf-8"))


def _rows(record, families=FAMILIES):
    for family in families:
        for name, row in (record.get(family) or {}).items():
            yield family, name, row


def _arrivals(reach):
    """The arrival turn of each occurrence line: "the_host#1 arrived T13, …"."""
    return [int(line.split(" arrived T", 1)[1].split(",", 1)[0]) for line in reach["occurrences"]]


class TestTheRecordMeasuredTheArmedDeck:
    def test_the_measured_deck_is_the_shipped_one(self, record):
        from tools._s14c_sweep_record import deck_sha
        block = json.loads(SCENARIO.read_text(encoding="utf-8"))["moments"]
        assert "affairs" in block, "the deck is not armed"
        assert record["deck_sha"] == deck_sha(block), "the deck changed: re-measure (tools/_affairs_measure.py)"
        assert record["affairs_deck"] == [e["id"] for e in block["affairs"]["deck"]] == list(TEMPLATES)

    def test_every_family_was_measured_with_the_trace(self, record):
        assert set(record["reach_aar"]) == {"REACH-AAR"}
        assert set(record["saves"]) == {f"DDB-{d}-{r}" for d in ("24", "25") for r in ("conquest", "diplomacy", "sea")}
        assert set(record["haiti"]) == set(HAITI_ARMS)
        for family, name, row in _rows(record):
            assert row["measured"] and row["mornings"] > 0 and row["errors"] == [], (family, name)
            assert list(row["affairs_reach"]) == list(TEMPLATES), (family, name)


class TestTheCeilingsAndTheFloorsHoldArmed:
    def test_no_ceiling_breach_on_any_arm(self, record):
        for family, name, row in _rows(record):
            assert row["ceiling_breaches"] == [], (family, name, row["ceiling_breaches"])
        for name, row in record["sweep"].items():
            metrics = row["metrics"]
            assert metrics["max_per_turn"] <= 1 and metrics["open_max"] <= int(record["pacing"]["max_open"]), name
            assert metrics["during_foreground"] == 0, name

    def test_no_letter_fires_with_its_premise_false_and_none_passes_in_silence(self, record):
        """Done-when: none fires with its premise false — the trace's `premise`
        ceiling (a delivery on a morning the premise read false) is a breach,
        and every occurrence row stands (no `silent` floor)."""
        for family, name, row in _rows(record):
            assert row["floor_breaches"] == [], (family, name)
            assert not [b for b in row["ceiling_breaches"] if b.get("rule") == "premise"], (family, name)
            for template, reach in row["affairs_reach"].items():
                if reach["occurrences"]:
                    assert reach["premise_mornings"] >= 1, (family, name, template)

    def test_every_delivered_figure_equals_its_quote(self, record):
        """Shown = applied on every run; a purse named in passing that moved
        under the letter is context drift, recorded apart (the judge's rule)."""
        for family, name, row in _rows(record):
            assert row["shown_equals_applied"] and row["mismatches"] == [], (family, name, row["mismatches"])
            for drift in row.get("context_drift") or []:
                assert drift["figure"] == "quote", (family, name, drift)


class TestEachTemplatesReach:
    @pytest.mark.parametrize("template", TEMPLATES)
    def test_the_template_arrives_somewhere_and_the_record_says_why_elsewhere(self, record, template):
        verdicts = {f"{family}/{name}": row["affairs_reach"][template]["verdict"]
                    for family, name, row in _rows(record)}
        for arm, verdict in verdicts.items():
            assert verdict, (template, arm)
            assert verdict == "arrived" or verdict.startswith(("never due", "due,", "premise never held", "crowded")), (template, arm, verdict)
        arrived = [arm for arm, v in verdicts.items() if v == "arrived"]
        assert arrived, (template, verdicts)

    def test_the_three_reach_the_scripted_boards_and_the_hand_played_starts(self, record):
        """ERR-3 re-measured (November 1, 2026), then ERR-5's re-measure the
        same evening (the Marine's letter reaching the field — §22.4): on the
        25 scripted arms the Arch-Chancellor arrives on 8, the Host's Claims
        on 17, the Memorial on 8; on the six hand-played starts the
        Memorial on 2, the Chancellor on 1 and the Host on 1; on the
        21 passive sweep runs the Memorial on 9, the Chancellor on 3, the
        Host on 3 — 12, 22 and 19 of the 55 runs (before ERR-5:
        16, 21 and 21 — the fourth letter took mornings from the first and the
        third; the total per campaign barely moved). Floors, not laws — the
        counts may only RISE without a re-measure."""
        def count(template, families):
            return sum(1 for _f, _n, row in _rows(record, families)
                       if row["affairs_reach"][template]["verdict"] == "arrived")
        assert count("chancellors_letters", SCRIPTED) >= 8
        assert count("the_host", SCRIPTED) >= 17
        assert count("berthiers_memorial", SCRIPTED) >= 8
        assert count("berthiers_memorial", ("saves",)) >= 2
        assert count("the_host", ("saves",)) >= 1 and count("chancellors_letters", ("saves",)) >= 1
        assert count("berthiers_memorial", ("sweep",)) >= 9

    def test_the_haiti_letter_appears_at_war_with_britain_wherever_the_emperor_stands(self, record):
        """RE-H (the user's word of November 1, 2026 — "conditions that make
        them appear"; then, the same evening, "let Decrès write to
        headquarters" — ERR-5, §22.4): with `bites` on the floor half and the
        at-home clause dropped, the Haiti letter reaches the passive board (17
        of the 21 sweep runs — the campaign's first affair at T6–T9 on most),
        the treaty road REACH-AAR twice (T23 and T38, the cooldown of twelve
        between), and the roads whose marching Emperor keeps the war with
        Britain (VP1-TH-historical at T13 and T28, VP1-RH-historical at T23).
        It never reaches the six hand-played turn-21 starts (peace with Britain
        by turn 19, the latch empty) nor the commanded arms — due there at
        T6–T9, but the driver's `diplomacy: accept` makes peace with Britain by
        T10–T19, the latch empties within twelve mornings, and the one free
        morning went to the Host's Claims, whose premise had stood longer
        (`affairs.pick`) — and the record says which clause held it back on
        each. Floors, not laws — the counts may only RISE without a re-measure."""
        def verdict(family, name):
            return record[family][name]["affairs_reach"][H1]["verdict"]
        sweep = [n for n in record["sweep"] if verdict("sweep", n) == "arrived"]
        assert len(sweep) >= 17, sweep
        aar = record["reach_aar"]["REACH-AAR"]["affairs_reach"][H1]
        assert aar["verdict"] == "arrived" and len(aar["occurrences"]) == 2
        turns = _arrivals(aar)
        assert turns[1] - turns[0] >= 12, turns                      # the cooldown
        # the marching Emperor, the war with Britain kept: the roads
        assert verdict("road", "VP1-TH-historical") == "arrived"
        assert verdict("road", "VP1-RH-historical") == "arrived"
        assert verdict("road_accept", "VP1-RH-historical") == "arrived"
        for family in ("commanded", "accept", "saves"):
            for name in record[family]:
                v = verdict(family, name)
                assert v.startswith(("premise never held", "never due", "due,")), (family, name, v)
        for family in ("road", "road_accept"):
            for name in record[family]:
                v = verdict(family, name)
                assert v == "arrived" or v.startswith(("never due", "due,")), (family, name, v)
        # the passive France's first affair is the Marine's letter, on the pulse's first morning
        firsts = {}
        for name, row in record["sweep"].items():
            for template in TEMPLATES:
                for turn in _arrivals(row["affairs_reach"][template]):
                    if turn < firsts.get(name, (99, ""))[0]:
                        firsts[name] = (turn, template)
        first_is_haiti = [n for n, (t, template) in firsts.items() if template == H1]
        assert len(first_is_haiti) >= 13, firsts
        # at most two an act, twelve apart, on every run
        for family, name, row in _rows(record):
            turns = _arrivals(row["affairs_reach"][H1])
            assert all(b - a >= 12 for a, b in zip(turns, turns[1:])), (family, name, turns)
            assert len([t for t in turns if t <= ACT]) <= 2, (family, name, turns)

    def test_the_squadron_sails_and_settles_where_the_letter_is_accepted_under_the_blockade(self, record):
        """RE-H's second landing, re-measured after ERR-5: on the `haiti`
        family the Marine's letter arrives in its squadron form under
        Britain's blockade and the accept dial sends five of the line on all
        three seeds; on the Rhine road's accept arm (`VP1-RH-historical`) the
        marching Emperor accepts it at T23 and the squadron is caught at T27;
        the trace records the fate four turns on (the frozen odds, the draw,
        home or caught). On every other arm no squadron sails — the fate is
        the one seeded roll per sailing, reported per seed, never a law."""
        sailed = {}
        for name in HAITI_ARMS:
            reach = record["haiti"][name]["affairs_reach"][H1]
            fates = [line for line in reach["occurrences"] if "; the squadron " in line]
            sailed[name] = fates
            for a in reach["answers"]:
                if a["answer"] == "accept":
                    assert a["gold"] == 500, (name, a)           # the squadron form's price
        assert all(sailed.values()), sailed
        road = record["road_accept"]["VP1-RH-historical"]["affairs_reach"][H1]
        road_fates = [line for line in road["occurrences"] if "; the squadron " in line]
        assert road_fates, road
        for line in [f for fates in sailed.values() for f in fates] + road_fates:
            assert " home T" in line or " caught T" in line, line
            assert "in 100, drew " in line, line
        for family, name, row in _rows(record, [f for f in FAMILIES if f != "haiti"]):
            for line in row["affairs_reach"][H1]["occurrences"]:
                if (family, name) == ("road_accept", "VP1-RH-historical"):
                    continue
                assert "; the squadron " not in line, (family, name, line)

    def test_the_host_s_claims_stay_an_event(self, record):
        """P6 (§0b): at two corps the Host's Claims reaches more boards (17 of
        the 25 scripted arms, beside the gate's 9 of 12 at three), and stays
        an event — never on every scripted board, never on a passive France
        whose corps are home."""
        scripted = {f"{family}/{name}": row["affairs_reach"]["the_host"]["verdict"]
                    for family, name, row in _rows(record, SCRIPTED)}
        arrived = sum(1 for v in scripted.values() if v == "arrived")
        assert 0 < arrived < len(scripted), scripted
        assert record["sweep"]["armA_historical_run1"]["affairs_reach"]["the_host"]["verdict"] == "premise never held"

    def test_the_tiers_price_the_host_s_letter(self, record):
        """§5: 300 × tier — 600 at two corps on the host's soil, 900 at three
        or more; read off the accepted letters (the accept arms, Road I)."""
        lumps = {a["gold"] for _f, _n, row in _rows(record, ("accept", "road_accept"))
                 for a in row["affairs_reach"]["the_host"]["answers"] if a["answer"] == "accept"}
        assert lumps and lumps <= {300, 600, 900}, lumps
        assert 900 in lumps


class TestTheBrakesAndTheRoad:
    def test_the_rhine_road_s_end_turns_and_stamp_are_the_control_s(self, record):
        """§14: the Rhine road's end turns stand unmoved with the lapse default
        — the armed road arms against the UNARMED control measured on the
        same commit (a scratch clone without the scenario's `affairs` key),
        per seed; the Confederation and the Throne roads alike."""
        control = record["road_control"]["arms"]
        assert {n.rsplit("-", 1)[0] for n in control} == {"VP1-RH", "VP1-CS", "VP1-TH"}
        for name, row in control.items():
            assert "control" in row, name
            assert row["unmoved"], (name, row["armed"], row["control"])
        rhine = {n: row for n, row in control.items() if n.startswith("VP1-RH")}
        assert {(row["armed"]["end_turns"], row["armed"]["stamped_turn"]) for row in rhine.values()} == {(34, 12), (40, 13), (28, -1)}

    def test_the_e1_band_is_untouched(self, record):
        """§14: the Edicts' E1 band (T1–T5) stays empty — no affair before the
        pulse's first morning (`first` ≥ 6) on any arm; the earliest arrival
        on the live tree is the Haiti letter at T6 (the band's low, drawn on
        jena and lodi; RE-3's earliest was the Memorial at T7, the authored
        value on `historical`)."""
        earliest = min(t for _f, _n, row in _rows(record) for reach in row["affairs_reach"].values()
                       for t in _arrivals(reach))
        assert earliest >= 6
        assert earliest == 6
        historical = min(t for template in TEMPLATES
                         for t in _arrivals(record["sweep"]["armA_historical_run1"]["affairs_reach"][template]))
        assert historical == 7                                     # the authored `first`

    def test_the_gold_and_the_standing_sit_inside_the_band(self, record):
        """§14: the Host's Claims at most 900 a letter and 1,800 a host an act
        (two letters); the Arch-Chancellor's two letters an act take at most
        16 points of standing (8 each, the grip floor beneath) — read off the
        answered figures of every arm."""
        for family, name, row in _rows(record):
            by_act = {}
            for a in row["affairs_reach"]["the_host"]["answers"]:
                assert a["gold"] <= 900, (family, name, a)
                by_act[(a["turn"] - 1) // ACT] = by_act.get((a["turn"] - 1) // ACT, 0) + a["gold"]
            assert all(total <= 1800 for total in by_act.values()), (family, name, by_act)
            standing = {}
            for a in row["affairs_reach"]["chancellors_letters"]["answers"]:
                assert 0 <= a["standing"] <= 8, (family, name, a)
                standing[(a["turn"] - 1) // ACT] = standing.get((a["turn"] - 1) // ACT, 0) + a["standing"]
            assert all(total <= 16 for total in standing.values()), (family, name, standing)
            # RE-H: the Haiti letter's Decline is −3, grip-floored — at most 6 an act
            haiti = {}
            for a in row["affairs_reach"][H1]["answers"]:
                assert 0 <= a["standing"] <= 3, (family, name, a)
                haiti[(a["turn"] - 1) // ACT] = haiti.get((a["turn"] - 1) // ACT, 0) + a["standing"]
            assert all(total <= 6 for total in haiti.values()), (family, name, haiti)
        # REH-1: the figures are READ (the record tool once saw 0 everywhere)
        costs = [a["standing"] for _f, _n, row in _rows(record)
                 for template in ("chancellors_letters", H1) for a in row["affairs_reach"][template]["answers"]]
        assert costs and max(costs) > 0, costs

    def test_the_decline_and_the_lapse_touch_no_purse(self, record):
        """The Decline is free of every purse (§5; `test_affairs_nondominance`):
        a lapsed or declined Host's letter takes no gold; a lapsed or declined
        Chancellor's letter costs standing only where the price bites."""
        for family, name, row in _rows(record):
            for a in row["affairs_reach"]["the_host"]["answers"]:
                if a["answer"] == "decline":
                    assert a["gold"] == 0, (family, name, a)
            for a in row["affairs_reach"]["berthiers_memorial"]["answers"]:
                assert a["gold"] == 0 and a["standing"] == 0, (family, name, a)
            for a in row["affairs_reach"][H1]["answers"]:
                if a["answer"] == "decline":
                    assert a["gold"] == 0, (family, name, a)          # the Decline is standing alone


class TestTheRecordToolReadsTheTrace:
    """`tools/_s14c_sweep_record.py`: each template's fate and each answer's
    figures composed from the trace alone, on a synthetic trace."""

    def _trace(self):
        return {
            "measured": True,
            "judged": {"mornings": 20,
                       "arrived": {"the_host#1": 13, "the_host#2": 18, "chancellors_letters#1": 15},
                       "passed": {"berthiers_memorial#1": "crowded"},
                       "floors": {"the_host#1": {"first_due": 13, "status": "answered", "verdict": "ok"},
                                  "berthiers_memorial#1": {"first_due": 16, "status": "passed", "verdict": "released"}}},
            "mornings": [{"turn": t, "delivered": [], "passed": {},
                          "affairs": {"true": ["the_host"] + (["chancellors_letters"] if t >= 15 else []),
                                      "false": [], "delivered": [], "withdrawn": ["the_host#2"] if t == 19 else [],
                                      "passed": {}, "due": []}} for t in range(1, 21)],
            "applications": [
                {"turn": 13, "moment": "the_host#1", "kind": "answer", "answer": "accept",
                 "shown": "Pay the host's claims: 900 gold (the treasury holds 11,649).",
                 "rows": [{"op": "gold", "figure": "treasury", "quoted": 10749, "delivered": 10749}]},
                {"turn": 16, "moment": "chancellors_letters#1", "kind": "lapse", "answer": "decline",
                 "shown": "", "applied": "Keep the pen: standing 92 → 84.", "rows": []},
            ],
        }

    def test_each_template_s_verdict_and_occurrence_lines(self):
        from tools._s14c_sweep_record import affairs_reach
        out = affairs_reach(self._trace(), ["chancellors_letters", "the_host", "berthiers_memorial", "haiti"])
        assert out["the_host"]["verdict"] == "arrived"
        assert out["the_host"]["occurrences"] == ["the_host#1 arrived T13, answered accept T13",
                                                  "the_host#2 arrived T18, withdrawn T19 (free)"]
        assert out["chancellors_letters"]["occurrences"] == ["chancellors_letters#1 arrived T15, lapsed T16 (its decline)"]
        assert out["berthiers_memorial"]["verdict"] == "crowded"
        assert out["berthiers_memorial"]["crowded"] == ["berthiers_memorial#1 crowded out (crowded)"]
        assert out["haiti"]["verdict"] == "premise never held" and out["haiti"]["occurrences"] == []
        assert out["the_host"]["premise_mornings"] == 20 and out["chancellors_letters"]["premise_mornings"] == 6
        assert out["the_host"]["first_due"] == 13 and out["berthiers_memorial"]["first_due"] == 16

    def test_each_answer_s_figures_are_the_deck_s_own(self):
        from tools._s14c_sweep_record import affairs_reach, answered_figures
        out = affairs_reach(self._trace(), ["chancellors_letters", "the_host"])
        host, = out["the_host"]["answers"]
        assert (host["occ"], host["turn"], host["kind"], host["answer"], host["gold"], host["standing"]) == \
            ("the_host#1", 13, "answer", "accept", 900, 0)
        assert host["figures"] == [{"op": "gold", "figure": "treasury", "quoted": 10749, "delivered": 10749}]
        pen, = out["chancellors_letters"]["answers"]
        assert (pen["kind"], pen["answer"], pen["gold"], pen["standing"]) == ("lapse", "decline", 0, 8)
        # a law's price in a quote is the law's, never a deck op's lump
        staff = answered_figures({"moment": "berthiers_memorial#1", "turn": 23, "kind": "answer", "answer": "accept",
                                  "shown": "Found the headquarters: 9,000 gold now, then 300 gold a turn.", "rows": []})
        assert staff["gold"] == 0 and staff["standing"] == 0
