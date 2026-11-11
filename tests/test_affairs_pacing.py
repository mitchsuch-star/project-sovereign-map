"""RE-1 — the affairs' pacing, measured and pinned (`docs/RECURRING_EVENTS_SPEC.md`
§7, §0b P8, §17b "the first affair about T13 — UNVERIFIED until RE-1").

`tools/_affairs_first_arrival_probe.py` plays the passive board (the series
harness's own loop) to turn 20 on the ten `SWEEP_SEEDS`, three times per seed
— the CONTROL (unarmed), the LETTERS arm (the deck armed, the courts' Edicts
rung held down — RE-6) and the ARMED arm (the shipped default) — with the
moments' trace installed. The record `tools/_affairs_first_arrival.json` is
read here: the moments' arrival turns identical on the control and the letters
arms (§7: the moments are blind to affairs — the letters move no dated
moment; the courts' decrees re-roll a board where they do, and the record
names the seeds); no ceiling or floor breach; the first affair per seed
reported on the shipped default, never a law. The look-ahead itself (P8) is
pinned on a crafted morning in `tests/test_affairs_engine.py`.
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
        # RE-H (November 1, 2026): the fourth letter, the Haiti letter;
        # RE-6 (November 2, 2026): the three offers, the Edicts;
        # AU-2c (November 4, 2026): the Bank's and the Pope's letters, authored,
        # ARMED November 5 by the user's word (the probe's arms read with them);
        # AU-3b (November 5, 2026): the Proclamation authored after the offers,
        # ARMED by the user's "Arm it" the same evening (the probe's arms read it);
        # DY-4 (November 10, 2026): The People Stir and The Ulcer — the Awakening's
        # letters (DYNAMISM_SPEC.md §5), armed through `awakening.the_people_write`
        assert record["affairs"] == ["chancellors_letters", "the_host", "berthiers_memorial", "santo_domingo",
                                     "the_magazines", "the_remounts", "camps_of_instruction",
                                     "the_proclamation", "the_bank", "the_popes_ports",
                                     "the_people_stir", "the_ulcer", "the_nation_in_arms"]

    def test_every_seed_was_played_on_the_three_arms_to_turn_twenty(self, record):
        assert record["turns"] == 20
        assert sorted(record["seeds"]) == sorted(SWEEP_SEEDS)
        for seed, arms in record["seeds"].items():
            # RE-6: the letters arm — the deck armed, the courts' rung held down
            assert set(arms) == {"control", "letters", "armed"}, seed
            for arm in arms.values():
                assert arm["last_turn"] == 21 and arm["errors"] == [], (seed, arm["errors"])


class TestTheMomentsAreBlindOnEverySeed:
    @pytest.mark.parametrize("seed", SWEEP_SEEDS)
    def test_the_moments_arrival_turns_are_identical_with_the_letters_against_unarmed(self, record, seed):
        """§7: the moments are blind to affairs — read against the LETTERS arm
        (RE-6, November 2, 2026): the courts' decrees on the shipped default
        re-roll a board (an admin action taken, the draws after it), which is
        the courts' doing and not the letters' (the pin below names where)."""
        arms = record["seeds"][seed]
        assert arms["letters"]["moments"] == arms["control"]["moments"], seed
        assert arms["control"]["affairs"] == {}                     # unarmed: no occurrence row

    def test_the_courts_decrees_re_roll_the_dated_moments_where_the_record_says(self, record):
        """Seeded paths, not laws: on the shipped default the courts decree
        from turn 2 on the passive board, and the dated moments move on four
        of the ten seeds against the letters arm — the courts' own move,
        attributed apart from the letters (whose arm is byte-identical to the
        control on every seed). What moves is the Throne of Holland: with no
        satellite rebelling in France's web Holland's loyalty holds, so the
        letter does not fall due within the probe's twenty turns on
        historical, wagram and rivoli, and comes a morning earlier on
        friedland (T17 against T18)."""
        moved = {seed for seed, arms in record["seeds"].items()
                 if arms["armed"]["moments"] != arms["letters"]["moments"]}
        # AU-19 at AU-4's head (November 5, 2026, §6.7): France keeps its standing
        # through the opening (no "capital lost" for its satellites' battles), its
        # grip on the web steadies, and Holland's letter moves with it — on wagram
        # it falls due at T18 on both arms, on rivoli on neither within the twenty
        # turns; historical and friedland as before
        # AU-4 the courts' flip (November 6, 2026 — the user's "Flip, flat grip"; §6.8): the courts' Decree
        # paid in authority where their gold refuses (AU-20 fixed) and their fields'
        # writes take the courts' move off historical — Holland's letter falls due at
        # T18 on both arms there, as on wagram; friedland as before
        # T0-H (November 7, 2026 — the re-record on the final tree, §183): the
        # courts' move widens to FIVE seeds, every one the Throne of Holland's
        # timing — due on the armed arm and not the letters' (austerlitz T19),
        # or the letters' and not the armed (historical and wagram T18, lodi
        # T18, ulm T19): the courts' decrees and fields hold or bleed
        # Holland's loyalty past the window per seed; friedland's T17/T18
        # morning-early move is subsumed in the wider set (its two arms agree
        # within the window now)
        # Session C (November 10, 2026 — the first re-record since T0-H, after
        # Tiers 1–5 of the Concert; SYSTEMS_REFERENCE.md §203): the deck gained
        # the Awakening's two letters and the probe re-ran on four tiers of
        # world-lines (the seed, the Questions' envy, the Alarm, the seat, the
        # terms). The Awakening itself moved no pacing row — its scalar and
        # ulcer held down reproduce the shipped record row for row (the
        # attribution arms `tools/playtest_runs/t6_pacing_2026_11_10/attrib_*`);
        # what moved is the tiers' drift, read here for the first time. The
        # courts' move is THREE seeds now, every one Holland's letter due on the
        # letters arm and not the armed (austerlitz T19, lodi T18, wagram T18);
        # the Match arrives on every seed on both arms (T8–T11), and historical,
        # ulm, rivoli and friedland agree within the window.
        assert moved == {"austerlitz", "lodi", "wagram"}, moved
        for seed, turn in (("austerlitz", 19), ("lodi", 18), ("wagram", 18)):
            assert record["seeds"][seed]["letters"]["moments"]["throne_of_holland"] == turn, seed
            assert "throne_of_holland" not in record["seeds"][seed]["armed"]["moments"], seed
        for seed in ("historical", "rivoli", "ulm", "friedland"):
            assert record["seeds"][seed]["letters"]["moments"] == record["seeds"][seed]["armed"]["moments"], seed
            assert set(record["seeds"][seed]["armed"]["moments"]) == {"bavarian_match"}, seed
        friedland = record["seeds"]["friedland"]
        assert friedland["armed"]["moments"]["bavarian_match"] == friedland["letters"]["moments"]["bavarian_match"] == 9

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
    the premise fell before the pulse opened (the Emperor driven from home).
    AU-3b armed (November 5, 2026 — the user's "Arm it" after "Re-premise it
    first", AUTHORITY_CURRENCY_SPEC.md §6.6.6): the Proclamation's premise is
    the war itself, so on the eve of battle it has stood longest on the
    pulse's first morning and takes the first affair on nine of the ten seeds
    — the Marine's letter keeps austerlitz."""

    def test_the_first_affair_per_seed(self, record):
        firsts = {seed: arms["armed"]["first_affair"] for seed, arms in record["seeds"].items()}
        reached = {seed: f for seed, f in firsts.items() if f}
        # RE-6 (November 2, 2026, §25.2): wagram — where the Haiti letter's
        # premise fell before the pulse opened — now meets the Remounts at
        # T13, the horse bled under the courts' attacks (the corps clause);
        # every other seed's first affair is still the Marine's letter on the
        # pulse's first morning
        # AU-3b armed (November 5, 2026, §6.6.6): the Proclamation on the pulse's
        # first morning on nine seeds (T6–T9 — on wagram at T9, before the
        # Remounts' T13); austerlitz keeps the Marine's letter at T9, and there
        # the Proclamation comes at T16
        # T0-H (November 7, 2026 — the re-record on the final tree, §183):
        # ULM joins austerlitz in meeting the Marine's letter first — the
        # T0-E/F/G world-lines put no enemy within a march of the Emperor
        # early there, so the Proclamation's eve never opens the pulse
        # (santo_domingo at T14 on austerlitz, T15 on ulm); the other eight
        # seeds keep the Proclamation at T6–T9, historical its authored T7
        # Session C (November 10, 2026 — the first re-record since T0-H, after
        # Tiers 1–5; §203): the tiers' world-lines re-time the first morning on
        # six seeds — the Marine's letter first on ulm (T14), austerlitz (T18)
        # and marengo (T16); the Proclamation first elsewhere, on the pulse's
        # first morning on jena, friedland, lodi and rivoli (T6–T7) and later on
        # historical (T13), eylau (T16) and wagram (T20), where no enemy stands
        # within a march of the Emperor until then. The Awakening moved none
        # of these (the attribution arms).
        assert set(reached) == set(SWEEP_SEEDS), reached
        assert {seed: f["id"] for seed, f in reached.items()} == {
            "historical": "the_proclamation#1", "ulm": "santo_domingo#1", "austerlitz": "santo_domingo#1",
            "jena": "the_proclamation#1", "marengo": "santo_domingo#1", "eylau": "the_proclamation#1",
            "friedland": "the_proclamation#1", "wagram": "the_proclamation#1", "lodi": "the_proclamation#1",
            "rivoli": "the_proclamation#1"}, reached
        assert {seed: f["turn"] for seed, f in reached.items()} == {
            "historical": 13, "ulm": 14, "austerlitz": 18, "jena": 6, "marengo": 16, "eylau": 16,
            "friedland": 6, "wagram": 20, "lodi": 6, "rivoli": 7}, reached

    def test_every_occurrence_is_lapsed_on_a_passive_france(self, record):
        """The unattended France answers nothing: every letter lapses to its
        Decline — the Haiti letter's rows bind where the letter found the
        Emperor (his seat, or his headquarters since ERR-5: marengo's second
        reaches him at Bohemia at T20 and still stands within its grace on the
        probe's last morning), the door's bind the Staff; both at tier 1."""
        # RE-6 (November 2, 2026): the Remounts reach the passive board too —
        # the horse bleeds under the courts' attacks (the corps clause, §25.2)
        for seed, arms in record["seeds"].items():
            rows = arms["armed"]["affairs"]
            # AU-2a (AUTHORITY_CURRENCY_SPEC.md §5.4): the Chancellor writes at any
            # standing — on ulm and austerlitz his letter takes the pulse's T21
            # morning (the Emperor afield since the opening), binding where it
            # finds him, as the Marine's does
            # AU-2c armed (November 5, 2026, §6.4.6): the Pope's letter at T14–T16 on
            # seven of the ten seeds, lapsed to its Decline like every other
            # AU-3b armed (November 5, 2026, §6.6.6): the Proclamation on all ten
            # (its second at T18–T19 on jena, marengo and eylau), lapsed to its
            # Decline — the army marches in silence; it binds nothing
            assert all(mid.startswith(("santo_domingo#", "berthiers_memorial#", "the_remounts#",
                                       "chancellors_letters#", "the_popes_ports#", "the_proclamation#"))
                       for mid in rows), (seed, list(rows))
            for mid, row in rows.items():
                standing = row["status"] == "fired" and int(row["turn"]) > int(record["turns"]) - 4
                # Session C (November 10, 2026 — the re-record after Tiers 1–5,
                # §203): on wagram and lodi the Marine's letter and the Pope's
                # are CROWDED OUT (passed, never fired — the desk busy past
                # their grace), the engine's own §7 rule on the tiers' boards
                crowded = row["status"] == "passed" and row.get("reason") == "crowded"
                assert (row["status"] == "lapsed" or standing or crowded) and row["tier"] == 1, (seed, row)
                if crowded:
                    assert seed in ("wagram", "lodi") and mid.startswith(("santo_domingo#", "the_popes_ports#")), (seed, mid)
                    continue
                if mid.startswith("berthiers_memorial#"):
                    assert row["bind"] == {"law": "grand_quartier_general"}, (seed, row)
                elif mid.startswith(("the_remounts#", "the_popes_ports#", "the_proclamation#")):
                    assert row["bind"] == {}, (seed, row)                   # an offer, the Pope: nothing bound
                else:
                    assert set(row["bind"]) == {"region", "sovereign"} and row["bind"]["sovereign"] == "Napoleon", (seed, row)
        with_door = {seed for seed, arms in record["seeds"].items()
                     if any(m.startswith("berthiers_memorial#") for m in arms["armed"]["affairs"])}
        # RE-6 (the courts' Edicts armed, November 2, 2026): the door's seeds
        # were ulm and austerlitz from RE-1; on the shipped default ulm's
        # board is re-rolled by the courts' decrees and its second letter is
        # the Marine's again — the door opens on austerlitz alone.
        # AU-2a (§5.4): the Chancellor at any standing takes austerlitz's T21
        # morning too; the door stands due past the probe's last morning
        assert with_door == set(), with_door

    def test_the_streaks_build_where_the_premise_holds_and_nothing_is_due_at_the_end(self, record):
        # RE-6: on austerlitz the Haiti letter's second is due on the probe's
        # last morning (its first lapsed at T11, the cooldown of twelve run)
        # AU-2a: the Chancellor's T21 letter on ulm and austerlitz leaves the
        # Marine's second (and, on austerlitz, the door) due on the last morning
        # AU-2c armed (November 5, 2026, §6.4.6): the Pope's T15–T16 morning moves
        # the Marine's second letter to T21 on ulm and austerlitz, so the
        # Chancellor's letter is the one due on the last morning; on eylau the
        # Pope at T15 and the Marine's second at T19 leave the Remounts due
        # AU-3b armed (November 5, 2026, §6.6.6): the Proclamation's mornings
        # re-time the pulse — on ulm (T9; the Marine's letter T15, the Pope's
        # T19) and austerlitz (T16; the Pope's T20) nothing stands due on the
        # last morning; on marengo the Marine's letter, put off its T6, takes
        # T13 and the Proclamation's second T18, and the Pope is due; on eylau
        # the Proclamation's second takes the Marine's T19, and the Marine's is due
        # AU-4 the courts' flip (November 6, 2026 — the user's "Flip, flat grip"; §6.8): the courts' decrees in
        # authority and their fields re-time the passive boards — on ulm and
        # austerlitz the Chancellor's letter and the Remounts stand due on the last
        # morning, on marengo the Chancellor's, the Remounts and the Pope's, on lodi
        # the Chancellor's and the Memorial; nothing on eylau
        # T0-H (November 7, 2026 — the re-record on the final tree, §183): the
        # T0-E/F/G world-lines clear the last morning on every seed but
        # marengo, where the Chancellor's letter, the Remounts and the Pope's
        # stand due (each once — the pulse re-timed under the courts' kept
        # chests and the later Proclamations)
        # Session C (November 10, 2026 — the first re-record since T0-H, after
        # Tiers 1–5; §203): the Pope's letter stands due on the last morning on
        # seven seeds (the war with Britain kept longer on the tiers' boards),
        # the Marine's on eylau and rivoli, the Remounts and the Proclamation
        # beside them on austerlitz (four busy mornings) and rivoli; wagram and
        # lodi clear (their due matters crowded out). The Awakening moved none.
        due_at_the_end = {"historical": {"the_popes_ports|": 1}, "ulm": {"the_popes_ports|": 2},
                          "austerlitz": {"the_remounts|": 4, "the_proclamation|": 4, "the_popes_ports|": 4},
                          "jena": {"the_popes_ports|": 1}, "marengo": {"the_popes_ports|": 3},
                          "eylau": {"santo_domingo|": 1, "the_popes_ports|": 1},
                          "friedland": {"the_popes_ports|": 2},
                          "rivoli": {"santo_domingo|": 2, "the_remounts|": 1}}
        for seed, arms in record["seeds"].items():
            armed = arms["armed"]
            assert armed["due"] == due_at_the_end.get(seed, {}), (seed, armed["due"])
            assert all(isinstance(v, int) and v >= 1 for v in armed["streaks"].values()), seed
