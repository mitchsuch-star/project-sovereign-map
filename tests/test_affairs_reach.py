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
# RE-6 (November 2, 2026): the three offers — the Edicts (§6.2 E1–E3) — join
# the measured deck; the record is re-measured on the shipped default — the
# courts' rung ARMED by the user's word, "Flip it on" (§25.3, §25.6): the five
# courts with a laws deck decree the Edicts at the player's prices on every
# measured arm, and the roads' moves are attributed to them apart from the
# letters (`road_control` the shipped default, `road_letters` the letters alone).
TEMPLATES = ("chancellors_letters", "the_host", "berthiers_memorial", "santo_domingo",
             "the_magazines", "the_remounts", "camps_of_instruction")
# AU-2c (November 4, 2026; AUTHORITY_CURRENCY_SPEC.md §6.4): the Bank's Panic and
# the Pope's Refusal, authored in the deck and held out until the user's word —
# ARMED November 5, 2026 by the user's "Arm both" (§6.4.6): the shipped record
# measures them on every run, and reproduces the review record's armed reach
# (`tools/_affairs_au2c_letters.json`) on every run and template
LETTERS = ("the_bank", "the_popes_ports")
# DY-4 (November 10, 2026; DYNAMISM_SPEC.md §5, session C): the Awakening's two
# letters — The People Stir and The Ulcer — armed through
# `awakening.the_people_write` (row DY-4 of `affairs.SINCE_ROWS`); the record
# measures them on every run (their premise is a people at the threshold under
# the Emperor's garrisons, so most arms read "premise never held")
AWAKENING = ("the_people_stir", "the_ulcer")
# AU-3b (November 5, 2026; AUTHORITY_CURRENCY_SPEC.md §6.6): the Proclamation,
# authored after the offers and held out until the user's word — re-premised on
# the eve of battle by "Re-premise it first" and ARMED by the user's "Arm it" the
# same evening (§6.6.5, §6.6.6): the shipped record measures it on every run and
# reproduces the review record's armed reach (`tools/_affairs_au3b_proclamation.json`)
# on every run and template
P2 = "the_proclamation"
HELD = ()                     # a letter held out until the user's word — none today
DECK = TEMPLATES + (P2,) + LETTERS + AWAKENING
E1, E2, E3 = "the_magazines", "the_remounts", "camps_of_instruction"
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
        assert record["affairs_deck"] == [e["id"] for e in block["affairs"]["deck"]] == list(DECK)

    def test_every_family_was_measured_with_the_trace(self, record):
        assert set(record["reach_aar"]) == {"REACH-AAR"}
        assert set(record["saves"]) == {f"DDB-{d}-{r}" for d in ("24", "25") for r in ("conquest", "diplomacy", "sea")}
        assert set(record["haiti"]) == set(HAITI_ARMS)
        for family, name, row in _rows(record):
            assert row["measured"] and row["mornings"] > 0 and row["errors"] == [], (family, name)
            assert list(row["affairs_reach"]) == list(DECK), (family, name)
            for template in LETTERS + (P2,) + AWAKENING:   # armed: read on every morning, never held out
                assert not row["affairs_reach"][template]["verdict"].startswith("not in the deck"), (family, name)
            for template in HELD:                  # held out until the user's word (none today)
                reach = row["affairs_reach"][template]
                assert reach["verdict"] == "not in the deck (held out)" and not reach["occurrences"], (family, name)


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
    @pytest.mark.parametrize("template", TEMPLATES + (P2,) + LETTERS)
    def test_the_template_arrives_somewhere_and_the_record_says_why_elsewhere(self, record, template):
        verdicts = {f"{family}/{name}": row["affairs_reach"][template]["verdict"]
                    for family, name, row in _rows(record)}
        for arm, verdict in verdicts.items():
            assert verdict, (template, arm)
            assert verdict == "arrived" or verdict.startswith(("never due", "due,", "premise never held", "crowded")), (template, arm, verdict)
        arrived = [arm for arm, v in verdicts.items() if v == "arrived"]
        assert arrived, (template, verdicts)

    @pytest.mark.parametrize("template", AWAKENING)
    def test_the_awakenings_letters_are_read_on_every_arm_and_the_record_says_why(self, record, template):
        """DY-4 (session C): the Awakening's letters' premise is a people at
        the threshold under the Emperor's garrisons — the thresholds are the
        gate's (40 / 70, `DYNAMISM_SPEC.md` §5a) and a forty-turn arm may never
        reach them; the record says why on every arm, and where it arrived is
        REPORTED (seeded paths, not laws — no arrival floor is pinned here;
        `tests/test_dy4_the_awakening.py` carries the session's own reading)."""
        verdicts = {f"{family}/{name}": row["affairs_reach"][template]["verdict"]
                    for family, name, row in _rows(record)}
        for arm, verdict in verdicts.items():
            assert verdict, (template, arm)
            assert verdict == "arrived" or verdict.startswith(("never due", "due,", "premise never held", "crowded")), (template, arm, verdict)
            assert not verdict.startswith("not in the deck"), (template, arm, verdict)

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
        # RE-6 (November 2, 2026, re-measured on the shipped default with the
        # courts' Edicts ARMED by the user's word — §25.2, §25.6): the courts'
        # decrees re-roll every measured board (an admin action taken at rung
        # 1.79, the draws after it), so the older letters' counts moved both
        # ways — the Arch-Chancellor 9 scripted (8 with the rung parked), the
        # Host 16 (17), the Memorial 3 (0) with the door due and released on
        # thirteen scripted arms (nine): its scripted mornings go to the
        # offers — the Remounts (a bar of 2,500 against the Staff's 11,500,
        # so its premise stands longer and `affairs.pick` takes it) and the
        # Magazines. The reach review (RE-5) weighs the lever (`below_pct`, a
        # corps threshold of its own).
        # AU-2a (November 3, 2026; AUTHORITY_CURRENCY_SPEC.md §5.4, the record
        # §6.2): the hits, re-measured. The Arch-Chancellor writes at ANY
        # standing (`bites: "floor"`) — the hoarder CMD-A and CMD-M and their
        # accept arms now meet him at full standing: 9 → 15 scripted. The
        # Host's Complaint prices the Host's Decline −2 / −3 / −4 at the floor,
        # so on a board under 73 on the grip the letter no longer comes — the
        # bled war roads (CMD-H, CMD-M, VOLTE, CMD-M-ACCEPT, the Confederation
        # road on historical, the Rhine road on marengo and its accept arm, the
        # Throne road on historical): 16 → 8 scripted, the ruling's cost (§4.1
        # reading 13, §6.2.3). The Memorial's sweep mornings 8 → 7 (the
        # Chancellor takes one), the Remounts 31 → 30 and the Camps 7 → 6 (the
        # pulse's picks re-rolled where a hit landed first).
        # AU-2a's clamp (November 4, 2026 — the user's "Clamp it first", §6.2.5):
        # the Host's Claims arrive at any standing again (`bites: "clamp"`), so
        # the bled roads meet the letter as before AU-2a — 8 → 16 scripted (CMD-H,
        # CMD-M, VOLTE, CMD-M-ACCEPT, the Confederation road and the Throne road
        # on historical, the Rhine road on marengo and its accept arm), the
        # sweep 0 → 2. Its mornings come from the pulse's other picks: the
        # Memorial's two on the Rhine road at marengo (3 → 1 scripted; due and
        # released there), the Magazines' on HAITI-marengo and the Confederation
        # road on historical (17 → 15), the Remounts' on VOLTE (30 → 29).
        # AU-2b the lumps (November 4, 2026, §6.3): the Bulletins raise the bled
        # roads' standing over the letters' floor, so the Marine's letter takes
        # the Host's morning on the Confederation road at historical (16 → 15;
        # due and released there) and the Chancellor gains the Rhine road at
        # austerlitz (21 → 22 of the 58)
        # Session C (November 10, 2026 — the first re-record since T0-H, after
        # Tiers 1–5 of the Concert; SYSTEMS_REFERENCE.md §203): the deck gained
        # the Awakening's two letters and the record re-ran on four tiers of
        # world-lines (the seed, the Questions' envy, the Alarm, the seat, the
        # terms). The Awakening itself moved no row — with its scalar and ulcer
        # held down the record reproduces row for row (the attribution arms,
        # `tools/playtest_runs/t6_pacing_2026_11_10/attrib_*`); what moved is
        # the tiers' drift, read here for the first time: the Chancellor 18 → 17
        # scripted, the Host 16 → 12 (the courts' later wars put fewer of the
        # Emperor's corps on an ally's soil), the Memorial 3 → 4; its door due on
        # 10 scripted arms, pending (not arrived) on the Rhine road's accept arm
        # at austerlitz; its sweep mornings 6 → 4
        assert count("chancellors_letters", SCRIPTED) >= 15
        assert count("the_host", SCRIPTED) >= 12
        assert count("berthiers_memorial", SCRIPTED) >= 1
        # AU-4 the courts' flip (November 6, 2026 — the user's "Flip, flat grip"; §6.8): the courts take the
        # player's rules and decree in authority where their gold refuses — the five
        # courts with a laws deck decree the Remounts at turn 1 — so every measured
        # board re-rolls from its first morning and the letters move both ways: the
        # Chancellor 15 → 18 scripted, the Host 15 → 16, the Memorial 1 → 2 (its door
        # due on 15 → 11 scripted arms — CMD-H and its accept arm and the Confederation
        # road at austerlitz no longer meet its premise; its sweep runs 7 → 6). With
        # the courts held down (arm AUC) the parked record's counts return
        # RE3-6 (S15's head, November 6, 2026 — the user's "Ask him; loyalty
        # pays"): the Crown of the Reich, accepted at T15 on Road I answered at
        # austerlitz, re-times that board so the Memorial ARRIVES there where it
        # had been due and released (11 → 10 doors due, the Memorial 2 → 3
        # scripted); the old flags beside it (S15H-1 — the dated letters
        # declined) leave the door as the flip measured it
        assert sum(1 for _f, _n, row in _rows(record, SCRIPTED)
                   if row["affairs_reach"]["berthiers_memorial"]["verdict"].startswith("due")) >= 10
        assert record["road_accept"]["VP1-RH-austerlitz"]["affairs_reach"]["berthiers_memorial"]["verdict"].startswith("due")
        assert count("berthiers_memorial", ("saves",)) >= 2
        assert count("the_host", ("saves",)) >= 1 and count("chancellors_letters", ("saves",)) >= 1
        assert count("berthiers_memorial", ("sweep",)) >= 4
        # the offers' floors (§25.6): the Magazines on the war's roads — more of
        # them with the courts in arms (15 of 55; 8 with the rung parked) — and
        # three of the six hand-played starts; the Remounts wherever the horse
        # bleeds (31; the corps clause — none on the hand-played starts, whose
        # squadrons stand whole); the Camps at the golden peace of the
        # commanded arms and three hand-played starts (7), never on the sweep
        # at war with Britain
        # AU-2c armed (November 5, 2026, §6.4.6): the Pope's letter takes a
        # morning from each — the Magazines' T21 on HAITI-austerlitz (the Pope
        # arrives there at T21 and the accept dial answers it), 15 → 14; the
        # Remounts' on the scripted austerlitz board with soil (the Pope at
        # T16, the Bank at T20 and T40: the Remounts due, pending at the last
        # morning), 29 → 28
        # AU-3b armed (November 5, 2026, §6.6.6): the Proclamation takes two of
        # the Magazines' mornings — the passive friedland board's T6 (the
        # campaign's first affair) and the lodi board's T20 — 14 → 12; and the
        # Chancellor's T14 on the Throne road at austerlitz (scripted 16 → 15)
        # AU-19 at AU-4's head (November 5, 2026, §6.7): a capital is lost only by
        # its defender, when it falls — the standing no longer bled by "capital
        # lost" for the satellites' battles, the letters that bite above the floor
        # come back to the late mornings and the Magazines lose three runs —
        # armC_04_marengo (T32 and T40: the Pope arrives at T32), the Rhine road at
        # historical (T40: the Marine's letter at T38) and its accept arm (the
        # premise never holds there now) — 12 → 9; on CMD-H the
        # Chancellor's second letter (−8) finds room above the floor at T28 (eight
        # "capital lost" gone) and takes the Camps' morning — 6 → 5
        # AU-4 the courts' flip (November 6, 2026 — the user's "Flip, flat grip"; §6.8): the re-rolled boards
        # bleed the Emperor's horse on fewer runs and draw his corps onto campaign pay
        # on fewer mornings — the Remounts 28 → 19 runs, the Magazines 9 → 5; the Camps
        # 5 → 6 (the hand-played starts unmoved: they boot at turn 21)
        # T0-H (November 7, 2026 — the re-record on the final tree, §183): the
        # Remounts 19 → 17 — the T0-E/F/G battles repeat no braked pair, the
        # horse bleeds on two fewer boards; the Magazines 5 → 7 and the Camps
        # 6 → 5 under the same re-roll
        # Session C (November 10, 2026 — the re-record after Tiers 1–5, §203):
        # the Remounts reach 11 of the 55 (the horse bleeds less under the
        # tiers' quieter wars — the Alarm's guarantees and the seat hold the
        # coalition's march), the Camps the three hand-played starts alone
        # (the commanded arms' golden peace never comes on the tiers' boards);
        # the Magazines 8, three of them the hand-played starts
        assert count(E1, FAMILIES) >= 5 and count(E1, ("saves",)) >= 3
        assert count(E2, FAMILIES) >= 11 and count(E2, ("saves",)) <= 1      # the October 25 diplomacy start's horse bleeds now
        assert count(E3, FAMILIES) >= 3 and count(E3, ("saves",)) >= 3 and count(E3, ("sweep",)) == 0

    def test_the_haiti_letter_appears_at_war_with_britain_wherever_the_emperor_stands(self, record):
        """RE-H (the user's word of November 1, 2026 — "conditions that make
        them appear"; then, the same evening, "let Decrès write to
        headquarters" — ERR-5, §22.4): with `bites` on the floor half and the
        at-home clause dropped, the Haiti letter reaches the passive board (17
        of the 21 sweep runs — the campaign's first affair at T6–T9 on
        fifteen) and the roads whose marching Emperor keeps the war with
        Britain. RE-6 (November 2, 2026, the courts' Edicts armed — §25.6):
        the courts' decrees re-roll every board, and the offers' premises
        stand longer than the Marine's on the war's roads — the treaty road
        REACH-AAR, which met the letter twice with the rung parked (T23 and
        T38), now meets the Magazines, the Remounts and the Camps and the
        Marine's letter is due and released; the Rhine road on `historical`
        (and its accept arm) the same; the Throne road on `historical` (T13)
        and the Confederation road on `austerlitz` keep it. It never reaches
        the six hand-played turn-21 starts (peace with Britain by turn 19, the
        latch empty) nor the commanded arms — due there at T6–T9, but the
        driver's `diplomacy: accept` makes peace with Britain by T10–T19, the
        latch empties within twelve mornings, and the one free morning went
        to the Host's Claims, whose premise had stood longer (`affairs.pick`)
        — and the record says which clause held it back on each. Floors, not
        laws — the counts may only RISE without a re-measure; the reach
        review (RE-5) weighs the roads' loss with RE3-6 / RE3-7."""
        def verdict(family, name):
            return record[family][name]["affairs_reach"][H1]["verdict"]
        sweep = [n for n in record["sweep"] if verdict("sweep", n) == "arrived"]
        # AU-2c armed (November 5, 2026, §6.4.6): the Pope's T16 arrival takes the
        # Marine's morning on the scripted austerlitz board (due, released there), 17 → 16
        # AU-3b armed (November 5, 2026, §6.6.6 — the user's "Arm it", the cost
        # named before the word): the Proclamation's streak is the war's, so on the
        # eve of battle it takes the pulse's first morning where the Marine's
        # letter came first (T6–T9, and T14 on armC_02) and the Marine's never
        # comes after on eight sweep runs — the two historical runs, armC_00,
        # armC_02, armC_03, armC_05, and the scripted ulm board with and without
        # soil (there the Bank, put off its T9, takes the Marine's T19) — 16 → 8
        assert len(sweep) >= 8, sweep
        aar = record["reach_aar"]["REACH-AAR"]["affairs_reach"]
        # T0-H (November 7, 2026 — the re-record on the final tree, §183): the
        # treaty road MEETS the Marine's letter again (it had been due and
        # released since RE-6 took its mornings for the offers) and the Camps
        # with it; the Magazines stay due and released there
        assert aar[H1]["verdict"] == "arrived", aar[H1]["verdict"]
        # AU-4 the courts' flip (November 6, 2026 — the user's "Flip, flat grip"; §6.8): on the re-rolled
        # treaty road the Remounts keep their morning; the Magazines' (T24) and the
        # Camps' (T39) go to the board's other matters — due and released, due and pending
        # Session C (November 10, 2026 — the re-record after Tiers 1–5, §203): on
        # the treaty road the Remounts and the Magazines are CROWDED out (the
        # desk busier on the tiers' board) and the Camps' golden peace never
        # comes; the Marine's letter still arrives there. The Awakening moved
        # none of these (the attribution arms).
        assert aar[E2]["verdict"] == "crowded", aar[E2]["verdict"]
        assert aar[E1]["verdict"] == "crowded", aar[E1]["verdict"]
        assert aar[E3]["verdict"] == "premise never held", aar[E3]["verdict"]
        # the marching Emperor, the war with Britain kept: the roads that keep the letter
        kept = {f"{family}/{name}" for family in ("road", "road_accept") for name in record[family]
                if verdict(family, name) == "arrived"}
        # AU-2a (§6.2): the Rhine road on austerlitz kept it too — the Host's
        # Complaint (−2 at T15) left the Chancellor's tier-two −8 no room above
        # the floor at T26, and the Marine's −3 took the morning.
        # AU-2b the lumps (November 4, 2026, §6.3): a Te Deum and a Bulletin give
        # that board back its room, the Chancellor takes the morning and the
        # Marine's letter is due and released there; the Bulletins lift the
        # Confederation road on historical and the Rhine road's accept arm on
        # historical over the floor, and the letter arrives on both
        # AU-3b armed (November 5, 2026, §6.6.6): the Proclamation takes the
        # Marine's morning on the Throne road at historical (T18) and on the Rhine
        # road's accept arm (T28, accepted there) — the two Confederation roads keep it
        # AU-19 (November 5, 2026, §6.7): the Rhine road at historical no longer
        # bleeds six "capital lost" (its end 34 → 44), and the Marine's Decline (−3)
        # lands above the floor at T38 on the road and its accept arm
        # AU-4 the courts' flip (November 6, 2026 — the user's "Flip, flat grip"; §6.8): the Confederation
        # road at austerlitz loses the letter (its T14 the parked tree's — the premise
        # stands, the letter due and released), the Throne road at historical gains it (T28)
        # T0-H (November 7, 2026 — the re-record on the final tree, §183): the
        # System road at MARENGO gains the letter (it runs the full forty now,
        # the war with Britain kept to the end) and the Throne road at
        # historical loses it (its Fall at 35 comes first)
        assert kept == {"road/VP1-CS-historical", "road/VP1-CS-marengo",
                        "road/VP1-RH-historical", "road_accept/VP1-RH-historical"}, kept
        # … and so does the October 25 diplomacy start (DDB-25-diplomacy, T39): the
        # Host's two −2s (T24, T34) leave the Chancellor's second letter (−8) no
        # room above the floor, and the Marine's −3 takes the morning.
        # AU-4 the courts' flip (November 6, 2026 — the user's "Flip, flat grip"; §6.8): the commanded hoarder
        # CMD-A and its accept arm meet the letter at T37 — the Host's second letter,
        # which took that morning on the parked tree, no longer comes there
        # T0-H (November 7, 2026 — the re-record on the final tree, §183): the
        # commanded hoarder and its accept arm lose the letter's T37 morning
        # on the re-rolled boards (due, released on both); CMD-H's accept
        # arm — the bled war road — GAINS it, its longer war with Britain
        # keeping the latch; the October 25 diplomacy start keeps it
        # Session C (November 10, 2026 — the re-record after Tiers 1–5, §203): on
        # the tiers' boards the Marine's letter reaches the commanded hoarder's
        # board (CMD-H) and its accept arm and the VOLTE arm — their war with
        # Britain outlasts the opening now — and the October 25 diplomacy start
        # meets it due and released (its premise stands, the desk busy)
        reached_start = {"commanded/CMD-H", "commanded/VOLTE", "accept/CMD-H-ACCEPT"}
        for family in ("commanded", "accept", "saves"):
            for name in record[family]:
                v = verdict(family, name)
                if f"{family}/{name}" in reached_start:
                    assert v == "arrived", (family, name, v)
                    continue
                assert v.startswith(("premise never held", "never due", "due,")), (family, name, v)
        for family in ("road", "road_accept"):
            for name in record[family]:
                v = verdict(family, name)
                assert v == "arrived" or v.startswith(("never due", "due,")), (family, name, v)
        # the passive France's first affair is the Marine's letter, on the pulse's first morning
        # — read over every letter of the deck. AU-2c armed (November 5, 2026, §6.4.6):
        # on the scripted ulm board, with and without soil, the war outruns the chest
        # from the opening and the Bank's letter takes the pulse's first morning (T9)
        # from the Marine's — 15 → 13
        # AU-3b armed (November 5, 2026, §6.6.6): the passive France's first affair
        # is the Proclamation on fourteen of the 21 (T6–T9, T14 on armC_02; on the
        # scripted ulm board it takes the Bank's T9, the Bank comes at T19); the
        # Marine's letter keeps the
        # first morning on armB_austerlitz (T9) and armC_04_marengo (T14) — 13 → 2
        firsts = {}
        for name, row in record["sweep"].items():
            for template in TEMPLATES + (P2,) + LETTERS:
                for turn in _arrivals(row["affairs_reach"][template]):
                    if turn < firsts.get(name, (99, ""))[0]:
                        firsts[name] = (turn, template)
        first_is_haiti = [n for n, (t, template) in firsts.items() if template == H1]
        assert len(first_is_haiti) >= 2, firsts
        # T0-H (November 7, 2026 — the re-record on the final tree, §183):
        # the Proclamation opens twelve of the 21 sweep runs (was fourteen);
        # the Memorial opens four — the scripted ulm pair among them (T14,
        # where the Proclamation's eve never comes) — the Marine's letter
        # three and the Bank two
        # Session C (November 10, 2026 — the re-record after Tiers 1–5, §203): the
        # Proclamation opens nine of the 21, the Marine's letter six (austerlitz,
        # ulm, marengo and wagram — the Proclamation's eve opens later there),
        # the Memorial the four scripted boards; the Awakening moved none
        assert len([n for n, (t, template) in firsts.items() if template == P2]) >= 9, firsts
        assert firsts["armb_scripted_ulm"] == firsts["armb_scripted_ulm_soil"] == (14, "berthiers_memorial"), firsts
        # at most two an act, twelve apart, on every run
        for family, name, row in _rows(record):
            turns = _arrivals(row["affairs_reach"][H1])
            assert all(b - a >= 12 for a, b in zip(turns, turns[1:])), (family, name, turns)
            assert len([t for t in turns if t <= ACT]) <= 2, (family, name, turns)

    def test_the_squadron_sails_and_settles_where_the_letter_is_accepted_under_the_blockade(self, record):
        """RE-H's second landing, re-measured after ERR-5 and again at RE-6
        (the courts' Edicts armed): on the `haiti` family the Marine's letter
        arrives in its squadron form under Britain's blockade and the accept
        dial sends five of the line on all three seeds (home on `historical`
        at T11; caught on `austerlitz` at T18 and `marengo` at T20); the trace
        records the fate four turns on (the frozen odds, the draw, home or
        caught). The Rhine road's accept arm, which sailed one with the rung
        parked (accepted T23, caught T27), no longer meets the letter — its
        mornings go to the offers (§25.6). On every other arm no squadron
        sails — the fate is the one seeded roll per sailing, reported per
        seed, never a law."""
        sailed = {}
        for name in HAITI_ARMS:
            reach = record["haiti"][name]["affairs_reach"][H1]
            fates = [line for line in reach["occurrences"] if "; the squadron " in line]
            sailed[name] = fates
            for a in reach["answers"]:
                if a["answer"] == "accept":
                    assert a["gold"] == 500, (name, a)           # the squadron form's price
        assert all(sailed.values()), sailed
        for line in [f for fates in sailed.values() for f in fates]:
            assert " home T" in line or " caught T" in line, line
            assert "in 100, drew " in line, line
        assert any(" home T" in f for f in sailed["HAITI-historical"]), sailed
        # AU-2b the lumps (November 4, 2026, §6.3): the Bulletins lift the Rhine
        # road's accept arm on historical over the floor; the Marine's letter
        # arrived at T28, the arm accepted and five of the line sailed — home at T32.
        # AU-3b armed (November 5, 2026, §6.6.6): the Proclamation takes that T28
        # morning and the accept dial issues it (4 authority) — no squadron sails
        # outside the `haiti` family now
        # AU-19 (November 5, 2026, §6.7): the road's standing kept, the Proclamation
        # is issued at T33 and the Marine's letter returns at T38, accepted — its
        # squadron sails past the run's last morning, so no fate is read there
        # AU-4 the courts' flip (November 6, 2026 — the user's "Flip, flat grip"; §6.8): outside the `haiti`
        # family the squadron sails on two accept arms now — the Rhine road's at
        # historical (the Proclamation issued at T18; the Marine's letter at T25,
        # accepted, home at T29; its second at T40, past the run's last fate) and
        # the commanded hoarder's (CMD-A-ACCEPT: accepted at T37, caught at T41)
        # T0-H (November 7, 2026 — the re-record on the final tree, §183): the
        # Rhine road's accept arm alone sails outside `haiti` now — CMD-A-ACCEPT's
        # re-rolled board no longer meets the letter, and the Rhine arm's second
        # letter never comes (one sailing, home T29; the Proclamation's T18
        # acceptance stands)
        sailing = {}
        for family, name, row in _rows(record, [f for f in FAMILIES if f != "haiti"]):
            for line in row["affairs_reach"][H1]["occurrences"]:
                if "; the squadron " in line:
                    sailing[f"{family}/{name}"] = line
                    assert (" home T" in line or " caught T" in line) and "in 100, drew " in line, line
        assert set(sailing) == {"road_accept/VP1-RH-historical"}, sailing
        # Session C (November 10, 2026 — the re-record after Tiers 1–5, §203): the
        # Rhine road's accept arm meets the Marine's letter at T29 now (T25 before)
        # and the squadron is CAUGHT at T33 (36 in 100, drew 61) — the same odds,
        # a later draw; one sailing outside `haiti` still
        assert record["road_accept"]["VP1-RH-historical"]["affairs_reach"][H1]["occurrences"] == [
            "santo_domingo#1 arrived T29, answered accept T29; the squadron caught T33 (36 in 100, drew 61)"]
        assert any(" arrived T18, answered accept T18" in line for line in
                   record["road_accept"]["VP1-RH-historical"]["affairs_reach"][P2]["occurrences"])

    def test_the_bank_and_the_pope_reach_the_boards_their_premises_name(self, record):
        """AU-2c armed (November 5, 2026; AUTHORITY_CURRENCY_SPEC.md §6.4.3,
        §6.4.6): the Bank arrives only where the war outruns the chest — the
        sweep's scripted austerlitz and ulm boards, with and without the soil
        arm (5 arrivals on 4 runs, each lapsed to its Decline); the Pope from
        T14 on twelve sweep runs at war with Britain and on HAITI-austerlitz
        (accepted there at T21, 800 gold), never on the commanded, accept or
        road arms nor the hand-played starts — their peace with Britain comes
        first. Both answers priced as authored; at most two an act, spaced by
        the cooldown. Floors, not laws — the counts may only RISE without a
        re-measure."""
        def arrived(template, families=FAMILIES):
            return {f"{family}/{name}" for family, name, row in _rows(record, families)
                    if row["affairs_reach"][template]["verdict"] == "arrived"}
        bank = arrived("the_bank")
        # T0-H (November 7, 2026 — the re-record on the final tree, §183): the
        # Bank keeps the scripted austerlitz boards alone — on the ulm pair the
        # war no longer outruns the chest (GR-47 frees the courts to buy what
        # they can afford, and the kept gold holds the premise shut)
        # Session C (November 10, 2026 — the re-record after Tiers 1–5, §203): the
        # Bank keeps the scripted ULM boards now (with and without the soil arm)
        # and leaves the austerlitz pair — on the tiers' boards the war outruns
        # the chest at ulm and not at austerlitz; the Awakening moved neither
        assert {"sweep/armb_scripted_ulm",
                "sweep/armb_scripted_ulm_soil"} <= bank, bank
        assert all(arm.startswith("sweep/armb_scripted_") for arm in bank), bank
        pope = arrived("the_popes_ports")
        # AU-3b armed (November 5, 2026, §6.6.6): the Proclamation takes the Pope's
        # T21 on armC_04_marengo; on armB_jena and armC_08_lodi the Marine's letter,
        # put off its T6 by the Proclamation, comes at T13 and T14, the Pope's T14
        # finds no morning and the Pope never comes after — 13 → 10; four come
        # later (armB_austerlitz 16 → 20, armB_ulm and armC_01_ulm 15 → 19,
        # armC_09_rivoli 15 → 22)
        # AU-19 (November 5, 2026, §6.7): the Rhine road at marengo keeps its
        # standing (its end 68 → 83), the war with Britain outlasts the opening and
        # the Pope's Decline (−5) lands above the floor — T41 on the road and its
        # accept arm; never on the commanded or accept arms nor the hand-played starts.
        # AU-4 the courts' flip (November 6, 2026 — the user's "Flip, flat grip"; §6.8): the re-rolled boards
        # move the Pope's letter both ways — on eight sweep runs (12 → 8: it leaves
        # HAITI-austerlitz, the Rhine road at marengo and its accept arm, armC_04_marengo
        # and the scripted ulm boards; it comes to armC_02_austerlitz and armC_08_lodi)
        # T0-H (November 7, 2026 — the re-record on the final tree, §183): the
        # Pope reaches four sweep runs and HAITI-historical — where the accept
        # dial ANSWERS him (arrived T17, accepted, 800 gold, the quote
        # delivered figure for figure); the re-rolled boards close with
        # Britain sooner elsewhere and the premise lapses; on no scripted arm
        # nor hand-played start
        assert len(pope) >= 5, pope
        # Session C (November 10, 2026 — the re-record after Tiers 1–5, §203): the
        # Pope reaches twelve sweep runs, all three haiti arms, the treaty road
        # (T35, declined) and the Rhine road's accept arm at historical (T34,
        # accepted — 800 gold) — the war with Britain kept longer on the tiers'
        # boards; never the commanded or accept arms nor the hand-played starts
        assert all(arm.startswith(("sweep/", "haiti/", "reach_aar/", "road_accept/")) for arm in pope), pope
        assert arrived("the_popes_ports", SCRIPTED + ("saves",)) == {
            "reach_aar/REACH-AAR", "road_accept/VP1-RH-historical"}, pope
        cooldown = {"the_bank": 12, "the_popes_ports": 30}
        for family, name, row in _rows(record):
            for template in LETTERS:
                reach = row["affairs_reach"][template]
                turns = _arrivals(reach)
                assert all(b - a >= cooldown[template] for a, b in zip(turns, turns[1:])), (family, name, turns)
                assert len([t for t in turns if t <= ACT]) <= 2, (family, name, turns)
                if template == "the_popes_ports":
                    assert all(t >= 13 for t in turns), (family, name, turns)        # twelve mornings first
                for a in reach["answers"]:
                    if a["answer"] == "accept":
                        assert a["gold"] == (1000 if template == "the_bank" else 800), (family, name, a)
                    else:
                        assert a["gold"] == 0, (family, name, a)                     # the Decline: authority alone

    def test_the_proclamation_reaches_the_eve_of_battle_and_never_the_commanded_boards(self, record):
        """AU-3b armed (November 5, 2026 — the user's "Arm it" after "Re-premise
        it first"; AUTHORITY_CURRENCY_SPEC.md §6.6.5, §6.6.6): the Proclamation
        on the eve of battle — at war, an enemy army seen within a march of the
        Emperor on one of the last four mornings — arrives on 21 of the 55
        runs: sixteen of the 21 sweep runs (the campaign's first affair on
        fourteen), the Rhine road and the Throne road on historical, the Throne
        road on austerlitz, the Rhine road's accept arm (T28, issued: 4
        authority) and HAITI-historical (T12, issued); never on the commanded,
        accept or hand-played boards nor REACH-AAR — its due mornings there
        fall in the opening's silent weeks (the look-ahead before the Bavarian
        Match, the gap after an arrival). Priced in authority alone: an issue
        costs 4 (the recency rise unbought), a lapse nothing; at most two an
        act, spaced by its cooldown (12). Floors, not laws — the counts may
        only RISE without a re-measure."""
        arrived = {f"{family}/{name}" for family, name, row in _rows(record)
                   if row["affairs_reach"][P2]["verdict"] == "arrived"}
        # T0-H (November 7, 2026 — the re-record on the final tree, §183): 24
        # arrivals now — the sweep's 15 (one fewer: a re-rolled board's eve
        # falls in a silent week) plus ALL THREE haiti arms, the System road
        # at historical, the Rhine road at marengo AND its accept arm (the
        # road that stamps Pressburg there now fights its eve first); the
        # Throne road keeps historical and loses austerlitz (the Fall at 31
        # comes before its eve)
        # Session C (November 10, 2026 — the re-record after Tiers 1–5, §203): 27
        # arrivals — the sweep's 18, two haiti arms (HAITI-marengo loses its eve),
        # the Rhine road at historical and marengo with both accept arms and
        # austerlitz's accept arm, the Throne road at historical AND austerlitz
        # (the Fall there comes later now); the System road at historical loses
        # it. The Awakening moved none of these (the attribution arms).
        assert len(arrived) >= 21, sorted(arrived)
        assert len([a for a in arrived if a.startswith("sweep/")]) >= 15, sorted(arrived)
        assert {"road/VP1-RH-historical", "road/VP1-RH-marengo", "road/VP1-TH-historical",
                "road/VP1-TH-austerlitz", "road_accept/VP1-RH-historical",
                "road_accept/VP1-RH-marengo", "road_accept/VP1-RH-austerlitz",
                "haiti/HAITI-historical", "haiti/HAITI-austerlitz"} <= arrived, sorted(arrived)
        assert not [a for a in arrived if a.split("/", 1)[0] in ("commanded", "accept", "saves", "reach_aar")], arrived
        issued = 0
        for family, name, row in _rows(record):
            reach = row["affairs_reach"][P2]
            turns = _arrivals(reach)
            assert all(b - a >= 12 for a, b in zip(turns, turns[1:])), (family, name, turns)
            assert len([t for t in turns if t <= ACT]) <= 2, (family, name, turns)
            for a in reach["answers"]:
                assert a["gold"] == 0, (family, name, a)                      # never the chest
                if a["answer"] == "accept":
                    issued += 1
                    assert a["standing"] == 4, (family, name, a)              # 4 authority, the rise unbought
                else:
                    assert a["standing"] == 0, (family, name, a)              # the lapse: no change
        assert issued >= 2

    def test_the_host_s_claims_stay_an_event(self, record):
        """P6 (§0b): at two corps the Host's Claims reaches more boards (17 of
        the 25 scripted arms, beside the gate's 9 of 12 at three), and stays
        an event — never on every scripted board, never on a passive France
        whose corps are home."""
        scripted = {f"{family}/{name}": row["affairs_reach"]["the_host"]["verdict"]
                    for family, name, row in _rows(record, SCRIPTED)}
        arrived = sum(1 for v in scripted.values() if v == "arrived")
        assert 0 < arrived < len(scripted), scripted
        # T0-H (November 7, 2026 — the re-record on the final tree, §183): the
        # passive run's premise FLICKERS one morning now (two corps afield on
        # one T0-E/F/G world-line morning) and the letter still never comes —
        # an event, never a fixture, the pin's whole subject.
        assert record["sweep"]["armA_historical_run1"]["affairs_reach"]["the_host"]["verdict"].startswith(
            ("premise never held", "never due")), record["sweep"]["armA_historical_run1"]["affairs_reach"]["the_host"]["verdict"]

    def test_the_tiers_price_the_host_s_letter(self, record):
        """§5: 300 × tier — 600 at two corps on the host's soil, 900 at three
        or more; read off the accepted letters (the accept arms, Road I)."""
        lumps = {a["gold"] for _f, _n, row in _rows(record, ("accept", "road_accept"))
                 for a in row["affairs_reach"]["the_host"]["answers"] if a["answer"] == "accept"}
        assert lumps and lumps <= {300, 600, 900}, lumps
        # AU-4 the courts' flip (November 6, 2026 — the user's "Flip, flat grip"; §6.8): no accept arm takes
        # the third tier now — CMD-H-ACCEPT's letters of T23 and T33 find four or five
        # corps on the host's soil (600 each) where the parked tree found six (900);
        # the tier's price is pinned by `tests/test_affairs_engine.py`
        # (`test_tiers_from_the_two_scale_shapes`, `test_scaled_op_multiplies_the_listed_amounts_unless_a_tier_is_authored`)
        assert {300, 600} <= lumps


class TestTheBrakesAndTheRoad:
    def test_the_rhine_road_s_end_turns_and_stamp_are_the_control_s_with_the_letters_alone(self, record):
        """§14: the Rhine road's end turns stand unmoved with the lapse default
        — the road arms with the LETTERS armed and the courts' rung held down
        (`road_letters`, RE-6) against the UNARMED control measured on the
        same commit (the driver's own seam without the scenario's `affairs`
        key), per seed; the Confederation and the Throne roads alike. The
        letters move no road."""
        letters = record["road_letters"]["arms"]
        assert {n.rsplit("-", 1)[0] for n in letters} == {"VP1-RH", "VP1-CS", "VP1-TH"}
        # Session C (November 10, 2026 — the first re-record since T0-H, after
        # Tiers 1–5; §203): on the tiers' tree the letters alone move ONE road
        # arm — the Throne road at austerlitz ends at 36 against its control's
        # 40 — where §14 read none on November 7. Attributed, not assumed: with
        # every Awakening seam held down that arm ends at 36 too
        # (`tools/playtest_runs/t6_pacing_2026_11_10/attrib_th0.json`), so the
        # mover is the tiers' world-lines under the letters' own lapse default;
        # the eight other roads stand unmoved with the letters alone.
        for name, row in letters.items():
            assert "control" in row, name
            if name == "VP1-TH-austerlitz":
                assert not row["unmoved"] and (row["armed"]["end_turns"], row["control"]["end_turns"]) == (36, 40), row
                continue
            assert row["unmoved"], (name, row["armed"], row["control"])
        rhine = {n: row for n, row in letters.items() if n.startswith("VP1-RH")}
        # AU-4 the courts' flip (November 6, 2026 — the user's "Flip, flat grip"; §6.8): the courts' battle
        # writes ride the letters arm and its control alike — on historical France
        # holds the Rhine road to the last turn (34 → 40, stamped at 12 on both)
        # T0-H (November 7, 2026 — the re-record on the final tree, §183): at
        # marengo the road stamps Pressburg at 13 on the letters arm AND its
        # control alike (30, 13) — the T0-E/F/G battles carry Austria to terms
        # there with or without the letters; the letters still move no road
        # Session C (§203): at marengo the letters arm ends at 28, stamped at 13
        # — the Fall comes sooner on the tiers' tree (30 → 28), the stamp stands
        assert {(row["armed"]["end_turns"], row["armed"]["stamped_turn"]) for row in rhine.values()} == {(40, 12), (40, 13), (28, 13)}
        assert "ai_decrees=False" in record["road_letters"]["_note"]

    def test_the_courts_decrees_move_every_road_and_the_record_attributes_them(self, record):
        """RE-6 (November 2, 2026; the courts' Edicts ARMED by the user's word
        — §25.3, §25.6): on the shipped default (`road_control`) every road
        arm's end turn moves against the unarmed control — the courts' decrees
        alone, since the letters alone move none (the pin above). Measured per
        seed, never a law: the Confederation road austerlitz 24 → 38,
        historical 30 → 35, marengo 27 → 24; the Rhine road austerlitz
        40 → 36, historical 34 → 40, marengo 28 unstamped → 40 sealed on turn
        13; the Throne road austerlitz 40 → 28, historical 40 → 33, marengo
        40 → 21 — France falls earlier on all three Throne-road arms: ×1.25
        supply for the corps that march on France, cheaper horse, +5 morale
        on every drill. The brake on France Q5 foresaw, taken by the user's
        word ("Flip it on")."""
        control = record["road_control"]["arms"]
        assert {n.rsplit("-", 1)[0] for n in control} == {"VP1-RH", "VP1-CS", "VP1-TH"}
        # AU-4 the courts' flip (November 6, 2026 — the user's "Flip, flat grip"; §6.8): the courts' battle
        # writes ride every arm — the control's seam holds the affairs alone — so the
        # controls re-time too (the Rhine road at historical 34 → 40); the courts'
        # decrees, paid in authority where their gold refuses, move six of the nine
        # roads against them, and three end with their control: the Confederation road
        # at historical (32), the Throne road at austerlitz and at historical (40)
        # T0-H (November 7, 2026 — the re-record on the final tree, §183): the
        # T0-E/F/G lines re-time controls and armed arms alike, and the courts'
        # decrees now move EIGHT of the nine roads against their controls — the
        # System road at marengo alone ends with its control (40); the Rhine
        # road at marengo stamps Pressburg at 13 on BOTH arms (the control
        # Falls at 30, the armed runs to 33), and the Throne road's Falls come
        # earlier on every seed (40 → 31/35/25 armed)
        assert all("control" in row for row in control.values())
        # Session C (November 10, 2026 — the first re-record since T0-H, after
        # Tiers 1–5; §203): on the tiers' tree the courts' decrees move FOUR of
        # the nine roads against their controls — the System road at historical
        # (40 → 28) and marengo (37 → 25), the Rhine road at marengo (28 → 34,
        # stamped at 13 on both arms) and the Rhine road at historical's stamp
        # alone unmoved at 40 — and five end with their control: the System road
        # at austerlitz (21), the Rhine road at austerlitz (40, stamped 13 on
        # both) and all three Throne roads (40 — France no longer Falls on them;
        # the Alarm's guarantees and the seat hold the coalition's march). The
        # Awakening moved none of these (the attribution arms).
        assert {n for n, row in control.items() if row["unmoved"]} == {
            "VP1-CS-austerlitz", "VP1-RH-austerlitz", "VP1-TH-austerlitz", "VP1-TH-historical",
            "VP1-TH-marengo"}, {n: row["unmoved"] for n, row in control.items()}
        ends = {n: (row["control"]["end_turns"], row["armed"]["end_turns"], row["armed"]["stamped_turn"])
                for n, row in control.items()}
        # AU-2b the lumps (November 4, 2026, §6.3): the Bulletins re-time the
        # Confederation road on historical on both arms (the control 30 → 32,
        # the armed 35 → 36); the eight other roads' ends unmoved
        # AU-19 (November 5, 2026, §6.7): the player's standing no longer bled by
        # "capital lost" re-times the Confederation road's armed arms — historical
        # 36 → 35, marengo 24 → 25; the controls and the seven other roads unmoved
        assert ends == {
            "VP1-CS-austerlitz": (21, 21, -1), "VP1-CS-historical": (40, 28, -1), "VP1-CS-marengo": (37, 25, -1),
            "VP1-RH-austerlitz": (40, 40, 13), "VP1-RH-historical": (40, 40, -1), "VP1-RH-marengo": (28, 34, 13),
            "VP1-TH-austerlitz": (40, 40, -1), "VP1-TH-historical": (40, 40, -1), "VP1-TH-marengo": (40, 40, -1),
        }, ends
        # the control of each road arm is the letters arm's control: one unarmed run per seed
        letters = record["road_letters"]["arms"]
        assert {n: row["control"] for n, row in control.items()} == {n: row["control"] for n, row in letters.items()}

    def test_the_e1_band_is_untouched(self, record):
        """§14: the Edicts' E1 band (T1–T5) stays empty — no affair before the
        pulse's first morning (`first` ≥ 6) on any arm; the earliest arrival
        on the live tree is T6 (the band's low, drawn on jena, friedland and
        lodi — the Haiti letter's until AU-3b's Proclamation was armed, the
        Proclamation's since, §6.6.6; RE-3's earliest was the Memorial at T7,
        the authored value on `historical`)."""
        earliest = min(t for _f, _n, row in _rows(record) for reach in row["affairs_reach"].values()
                       for t in _arrivals(reach))
        assert earliest >= 6
        assert earliest == 6
        # AU-3b armed: on `historical` the authored first morning (T7) is the
        # Proclamation's where it was the Marine's — read over the whole deck
        historical = min(t for template in DECK
                         for t in _arrivals(record["sweep"]["armA_historical_run1"]["affairs_reach"][template]))
        # Session C (November 10, 2026 — the re-record after Tiers 1–5, §203): on
        # the tiers' historical board no enemy stands within a march of the
        # Emperor until T13, so the Proclamation's eve — the first affair there
        # — opens the pulse at T13 (the authored `first`, 7, is the pulse's
        # floor, not its morning); the band's low (6) stands on jena, friedland
        # and lodi. The Awakening moved none of these (the attribution arms).
        assert historical == 13

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
        # AU-2c (November 4, 2026): a template no morning READ (neither `true` nor
        # `false`) was not in the deck — the synthetic trace reads "haiti" nowhere;
        # read false every morning, it is the premise that never held
        assert out["haiti"]["verdict"] == "not in the deck (held out)" and out["haiti"]["occurrences"] == []
        trace = self._trace()
        for m in trace["mornings"]:
            m["affairs"]["false"] = ["haiti"]
        assert affairs_reach(trace, ["haiti"])["haiti"]["verdict"] == "premise never held"
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
