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

    T8-CROWN `crowns.a_crown_is_erected` — DY-6 (DYNAMISM_SPEC.md §6): the
          crown block's teeth — the crown templates in the catalogue, the
          title and the recognition field on the client's row, the Alarm
          (a capital's 12 on the carver's house), the beat's crown; down:
          the crown templates are struck from the catalogue at load and
          the `crowns` block is not installed (NA-6c's four plain carves).

    T8-KING `crowns.a_marshal_may_reign` — DY-6: the marshal king and the
          prince (the picker at the table, the king on the clause, the
          marshal re-homed with his corps, the loyalty seed from his
          trust, the passed-over marshals' grievance); down: no king is
          offered and a `king` on a clause is ignored — a regency.

    T8-AI `settlement_third_party.a_victor_erects_a_crown` — DY-6: the
          victor's AI erects an authored crown out of the soil its aim
          peace cedes (one `create_client` clause in place of those
          cessions, a regency, the Alarm); down: the cessions as T3-4 wrote
          them.

    T8-RECOG `crowns.the_legitimists_withhold` — DY-7 (DYNAMISM_SPEC.md §6,
          session F): the condition's read — a legitimist that signs a
          peace as the LOSER with the house of a crown's lord recognizes
          it (`recognized_by` written at the peace chokepoints), the
          Congress's grant and refusal, the `recognition` beat; down:
          `recognized_by` is never written — the legitimists withhold for
          ever and nothing is said of it (session E's words stand).

    T8-PRICE `crowns.an_unrecognized_crown_pays` — DY-7: the three prices
          of a crown unrecognized — the table's malus (−5 a crown, capped
          −15, on the settlement scorer and the bilateral formula), the
          lord's trade with a withholding court halved, the client dial −3
          on awakened soil; down: a withheld crown costs nothing.

    G-PACT `ai_diplomacy.no_pact_with_the_coveted` — session G, the gate
          earned (DYNAMISM_SPEC.md §7a, November 11, 2026): no defensive
          alliance or alliance between a coveter and the coveted — a court
          whose live acquire design covets a province of the other's house
          (the poll's gate and the recipient-addressed road's guard); down:
          the pact signs and the ally clause reads the ambition as won.

    G-CHEST `reforms.a_crown_is_bought_with_the_whole_chest` — session G:
          the AI's purse bar for a promotion law is the price and arrears
          alone (no reserve, no five turns' upkeep); down: 4,500 for a
          3,000 crown.

    G2-RECOG `crowns.the_war_names_the_beaten` — session G2, the played
          campaign (DYNAMISM_SPEC.md §7b, November 11, 2026): the court a
          peace beats is the court the WAR went against (the pair's score
          past the ratification record's own bar), the clause burden only
          for a drawn war; and the court out of whose lands a crown is
          carved recognizes it by the treaty that erects it; down: the
          loser by burden alone — an indemnity the victor pays for a carve
          names the victor beaten (session F).

    G2-ASK `ai_diplomacy.a_court_at_fight_still_asks` — a court at `fight`
          with its ladder unclimbed still sends the design ask; down: the
          ask at the asking rungs and at `coerce` only, so a court that
          reaches `fight` first never asks and never opens its crisis.

    G2-LADDER `ai_diplomacy.the_ladder_outlasts_the_rest` — the war
          council's ladder gate counts the refusals of the last 24 turns
          (the longest rest and one dedupe window) and the write keeps them
          that long; down: the 12-turn memory — climbed six turns in
          eighteen once T0-F's escalating rest spaces the asks.

    G2-BACKED `intent.a_backed_design_dares` — a live sponsorship or
          licence aimed at the holder of a court's acquire design adds
          `WEIGHT_BACKED_DESIGN` to its weight for the compact's term
          (never an aim in the player's house); down: a compact moves gold
          and binds its payer and nothing else.

    G3-CLIENT `ai_diplomacy.a_client_swears_no_pact_of_its_own` — session
          G3 (DYNAMISM_SPEC.md §7c, November 11, 2026 — the user's "make
          best cal for game"): a client's foreign policy is its lord's — no
          defensive alliance or alliance is proposed to or from a court
          that answers to a lord (the poll's gate, the recipient-addressed
          road's guard, `reason: client`); a NAP and open borders untouched;
          down: a client signs what it likes — the Kingdom of Italy's pact
          with Rome pulled it into Naples' war and it was erased.

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
    # Tier 6 (session C, November 10, 2026) rides the same registry.
    "T6-STIR": [
        "backend.game_logic.awakening:the_people_stir=False",
    ],
    "T6-ULCER": [
        "backend.game_logic.awakening:the_ulcer_bleeds=False",
    ],
    "T6-LETTERS": [
        "backend.game_logic.awakening:the_people_write=False",
    ],
    # Tier 6, session D (DY-5, November 10, 2026): the Awakening's second half.
    "T6-LEVEE": [
        "backend.game_logic.awakening:the_levee_rises=False",
    ],
    "T6-DIAL": [
        "backend.game_logic.awakening:the_tiger_is_ridden=False",
    ],
    "T6-REVANCHE": [
        "backend.game_logic.awakening:a_risen_people_swears_revanche=False",
    ],
    "T6-LIBERATORS": [
        "backend.game_logic.awakening:liberators_hold_together=False",
    ],
    "T6-ARMS": [
        "backend.game_logic.awakening:the_nation_writes=False",
    ],
    # Tier 8, session E (DY-6, November 10, 2026): Crowns & Recognition's
    # first half — the crown erected, the marshal king, the AI's road.
    "T8-CROWN": [
        "backend.game_logic.crowns:a_crown_is_erected=False",
    ],
    "T8-KING": [
        "backend.game_logic.crowns:a_marshal_may_reign=False",
    ],
    "T8-AI": [
        "backend.game_logic.settlement_third_party:a_victor_erects_a_crown=False",
    ],
    # Tier 8, session F (DY-7, November 10, 2026): Recognition — the
    # legitimists' condition and the Congress's grant, the three prices.
    "T8-RECOG": [
        "backend.game_logic.crowns:the_legitimists_withhold=False",
    ],
    "T8-PRICE": [
        "backend.game_logic.crowns:an_unrecognized_crown_pays=False",
    ],
    # Session G (the gate earned, November 11, 2026): the pact with the
    # coveted and the crown bought with the whole chest.
    "G-PACT": [
        "backend.game_logic.ai_diplomacy:no_pact_with_the_coveted=False",
    ],
    "G-CHEST": [
        "backend.game_logic.reforms:a_crown_is_bought_with_the_whole_chest=False",
    ],
    # Session G2 (the played campaign, November 11, 2026 — DYNAMISM_SPEC.md
    # §7b): the four rules a hand-played France found missing.
    "G2-RECOG": [
        "backend.game_logic.crowns:the_war_names_the_beaten=False",
    ],
    "G2-ASK": [
        "backend.game_logic.ai_diplomacy:a_court_at_fight_still_asks=False",
    ],
    "G2-LADDER": [
        "backend.game_logic.ai_diplomacy:the_ladder_outlasts_the_rest=False",
    ],
    "G2-BACKED": [
        "backend.game_logic.intent:a_backed_design_dares=False",
    ],
    # Session G3 (a client swears no pact of its own, November 11, 2026 —
    # DYNAMISM_SPEC.md §7c): the user's delegated ruling on his clients.
    "G3-CLIENT": [
        "backend.game_logic.ai_diplomacy:a_client_swears_no_pact_of_its_own=False",
    ],
}
T3_SEAMS_DOWN = [spec for row in T3_SEAMS_BY_ROW
                 for spec in T3_SEAMS_BY_ROW[row]]
