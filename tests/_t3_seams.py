"""Tier 3's content seams — each behavioural slice of the strategist
behind a named FUNCTION a series arm can replace
(`tools/playtest_driver.py --seam MODULE:NAME=EXPR`, the S13b idiom; no
levers — the code-health ratchet stands at 231 of 231). The list is the
slice OFF; an attribution arm holds a seam down and must reproduce the
prior tree's reading byte for byte.

    T3-3  `war_council.a_leash_pulls_the_march` — the leash: an at-war
          court's pick bias widens from its design's unmet targets to
          its WAR AIMS (the objective record's targets and the
          recapture of its own lost soil), the recall riding the aim
          itself; down: the design's targets alone — a court at war
          never credits its objective and never feels the pull home.

    T3-3  `war_council.annexation_follows_the_aim` — the conduct rule
          (the slice's second half, the user's "Extend with conduct
          rule"): an at-war court ANNEXES only its aim — P4.5's
          walk-ins and P4.25's storms skip off-pull soil; field
          battles stay lawful everywhere, their flips the residual;
          down: a court at war grabs whatever lies adjacent.

    T3-4  `settlement_third_party.a_held_aim_sues` — the terms, AI–AI: a
          court holding its war's aim against another AI court offers the
          aim's terms (its delivered provinces ceded by treaty) and the
          loser signs inside its band — an AI-only war ends whole on its
          leaders' aims, a pair inside France's war exits on its own;
          down: an AI war ends only when the loser breaks, both are spent,
          or a court falls.

    T3-4  `ai_diplomacy.a_held_aim_offers_terms` — the terms, AI–player:
          P8-Aim, the aim's letter to France at war score 25; down: only
          P8's dictated letter past 40.

    T3-5  `war_council.the_conduct_binds_every_runner` — the conduct rule
          binds an AI-run France (the harness) as every court; a marshal
          under the player's independent command stays exempt; down: the
          whole player nation exempt (T3-3's reading). (The terms'
          consistency fix of T3-5 rides T3-4's `a_held_aim_sues`.)

    T3-6  `game_end.a_peace_evacuates_what_it_does_not_cede` — occupation
          is not annexation: at a peace between AI courts the winner keeps
          what the treaty cedes and its authored aims and hands the rest of
          the loser's homeland back; down: SR-1a's retention of everything
          held (the player's peaces keep SR-1a either way).

    T4-1  `alarm.the_alarm_sounds` — the Alarm of Europe's write
          (DYNAMISM_SPEC.md §3, the Tier-4 gate §3c G1): an AI court's
          capture writes Europe's alarm against its house (6 / a capital
          12 / a third court's client 8, on top of the +2 every conqueror
          already paid); down: no `alarm:` write.

    T4-1  `alarm.an_alarmed_court_guarantees` — the guarantee rung (§3c
          G2): a court alarmed by a conqueror pledges the existing D5
          guarantee for the likely next victim; down: only the crisis
          producer ever pledges an AI guarantee.

    T4-1  `dispatch.a_lone_filler_yields_to_the_quiet_floor` — the page's
          sibling the Alarm's measure found: a board with ONE kind of capped
          front-page filler gets the quiet floor as its second kind (the
          rotation guard's own "alternates rather than repeats"); down: the
          lone filler leads a fifth time in ten.

    T4-2  `settlement_third_party.a_crown_falls_only_by_treaty` — sign at
          the last (§3c G5, row DY-1c): a court whose last province falls
          signs a pair peace with every AI court holding homeland it may not
          keep, gets that ground back and lives on; the reckless auto-charge
          asks the same question (the sibling sweep); down: the last
          province's capture erases the court, and the auto-charge asks
          nothing (the pre-T4-2 world).

    T4-2b `game_end.a_court_removes_its_seat` — the court removes (§3c
          "The seat", session A): a court whose seat a treaty of its own
          house titles to another holder moves it to the richest homeland
          province in its hands, and the seat returns with the authored
          capital; the moved seat rides `Region.is_capital` (no field);
          down: a court's seat is its authored capital for ever.

    T4-3  `reforms.a_minor_may_rise` — promotion (§3c G6, row DY-1b): a
          `rank` law — the 1806 crowns — may be enacted on its design's
          grounds and raises its court's DERIVED rank, and lapses when the
          grounds are lost; down: the promotion laws are struck at boot,
          a rank law enacts and raises nothing.

    T5-Q  `questions.the_questions_of_europe` — the Questions of Europe
          (DY-2, DYNAMISM_SPEC.md §4): the latch at the capture chokepoint,
          the envy term, the beat, the Balance tab's sentences, the
          guarantee rung's Question arm; down: no Question is read
          anywhere (the block still loads and saves).

    T5-C  `questions.the_congress_rules_a_question` — DY-3: a sitting
          Congress recognizes each open Question's present holder (the
          latch clears, the unseated claimants aggrieved); down: a
          sitting Congress rules nothing.

    T5-BERN `settlement_third_party.a_lord_signs_for_its_client` — DY-1e,
          the user's "Road home" for Bern: a client at its last province
          does not fall by the sword either — its lord signs for it;
          down: T4-2's client exemption (a client victim falls).

    T5-GIFT `settlement_third_party.a_leader_signs_for_its_allies` — DY-1f,
          the Emperor's gift (the AI's road): an aim peace carries each
          co-belligerent's delivered aim the side holds, ceded to that
          ally; down: the leaders' aims alone (T3-4).

    T5-SEAT `game_end.the_emperors_treaty_moves_a_seat` — DY-1g: a court
          whose capital the player's house takes by treaty removes its
          seat too, the Congress reading the historic capital; down:
          session A's boundary (2).

`hold_down(monkeypatch)` applies the list in-process
(`tests._standing_seams.hold_down` — one parser, one semantics).
"""
from __future__ import annotations

from tests._standing_seams import hold_down, parse  # noqa: F401

T3_SEAMS_BY_ROW = {
    "T3-3": [
        "backend.game_logic.war_council:a_leash_pulls_the_march=False",
        "backend.game_logic.war_council:annexation_follows_the_aim=False",
    ],
    "T3-4": [
        "backend.game_logic.settlement_third_party:a_held_aim_sues=False",
        "backend.game_logic.ai_diplomacy:a_held_aim_offers_terms=False",
    ],
    "T3-5": [
        "backend.game_logic.war_council:the_conduct_binds_every_runner=False",
    ],
    "T3-6": [
        "backend.game_logic.game_end:a_peace_evacuates_what_it_does_not_cede=False",
    ],
    # Tier 4 rides the same registry (the recorded boards' hold-list folds
    # every row — `tests/_oct27_seams.py`).
    "T4-1": [
        "backend.game_logic.alarm:the_alarm_sounds=False",
        "backend.game_logic.alarm:an_alarmed_court_guarantees=False",
        "backend.game_logic.dispatch:a_lone_filler_yields_to_the_quiet_floor=False",
    ],
    "T4-2": [
        "backend.game_logic.settlement_third_party:a_crown_falls_only_by_treaty=False",
    ],
    "T4-2b": [
        "backend.game_logic.game_end:a_court_removes_its_seat=False",
    ],
    "T4-3": [
        "backend.game_logic.reforms:a_minor_may_rise=False",
    ],
    # Tier 5 (session B, November 10, 2026) rides the same registry.
    "T5-Q": [
        "backend.game_logic.questions:the_questions_of_europe=False",
    ],
    "T5-C": [
        "backend.game_logic.questions:the_congress_rules_a_question=False",
    ],
    "T5-BERN": [
        "backend.game_logic.settlement_third_party:a_lord_signs_for_its_client=False",
    ],
    "T5-GIFT": [
        "backend.game_logic.settlement_third_party:a_leader_signs_for_its_allies=False",
    ],
    "T5-SEAT": [
        "backend.game_logic.game_end:the_emperors_treaty_moves_a_seat=False",
    ],
}
T3_SEAMS_DOWN = [spec for row in T3_SEAMS_BY_ROW
                 for spec in T3_SEAMS_BY_ROW[row]]
