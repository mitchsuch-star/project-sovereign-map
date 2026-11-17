"""Row BA, session BA-4 — "the roads and the fog" (November 16, 2026): the
session's seams, held DOWN.

Every rule of the session that moves a world-line sits behind a named
zero-argument FUNCTION in the module it gates (`tools/playtest_driver.py
--seam MODULE:NAME=EXPR`, the S13b idiom; no levers — the code-health ratchet
stands at 231 of 231). This list is the session OFF: an attribution arm holds
a seam down and must reproduce the tree before it, and a recorded board — one
recorded before the session — replays under the rules it was recorded under
(`tests/_oct27_seams.py` folds these rows in, as it folds Tier 3's).

The measure's ladder (`tools/_ba4_measure.py`) brings them up one arm at a
time, in this order.

    BA2-X2    `enemy_ai.a_corps_raised_mid_phase_takes_its_turn` — the AI
              phase's fairness tally takes a corps that was not on its opening
              roster; down: the tally's `KeyError` loses the court's turn.

    BA2-X12   `combat_executor.a_battery_is_spared_its_own_shells` — a
              battery is left out of its own collateral roll; down: a battery
              standing in its target's province is rolled for like any corps
              there.

    BA2-X10   `strategic.a_road_round_keeps_to_open_frontiers` — a road
              plotted ROUND a corps keeps to provinces the corps may enter,
              for a court as for the player, and has no terrain-only rung
              behind it; down: the reroute ladder as it was (its last rung
              dropped the frontier law).

    APPROACH  `strategic.a_support_order_halts_before_the_friends_foe` — a
              SUPPORT order whose next step is barred by a corps the friend
              can strike halts at the approach and joins his next attack;
              down: DDB-20's arm alone (the foe on the friend's own province).

    BA2-X20   `intel_surfaces.a_battle_lights_its_field_only_for_those_who_fought`
              — a battle grants the player FULL sight of its province only
              when he is a party to it or it is fought on his own soil (and a
              great battle abroad, or an ally's in a shared war, is news);
              down: every battle lights its field for the player.

    PURSUIT   `combat_executor.a_pursuit_is_any_corps_that_fought` — §15.5.7:
              when the lead has no pursuit ability the best among the
              victor's corps that fought fires it; down: the lead's alone
              (MC-1's "he must lead the killing blow").

    QUARTERS  `combat_executor.the_last_hour_brings_three_quarters` — §15.5.7:
              an arrival won by 5 points or fewer brings three quarters of
              its weight, and the muster's forecast weighs that roll the same
              way; down: a corps that arrives brings all the weight it has.

    TELL      the rows that move no number, together — the arm that must read
              exactly as the arm before it:
              `combat_executor.the_muster_names_only_an_order_that_brings`
              (BA2-X7: the muster's lever sentence names an order only where
              sending it brings the corps),
              `battle_day.a_word_is_quoted_in_points` (BA3-X5: a quote says a
              word's price in the day's points), `battle_day.a_day_is_one_battle`
              (a day keeps one name; a later clash is "— the second clash") and
              `battle_day.a_days_close_is_told` (the close's one line, on the
              table, in the log and in the morning's turn events).

    BA4-X1    `battle_day.a_brought_up_corps_is_one_the_table_offers` — the
              day takes as "a corps is brought up" only the support order its
              table offers as a "Bring up" chip (the plan's own reading); any
              other support order for the lead is an ordinary order at an
              action; down: every support order for the lead is a word of the
              day (BA-3's taker — also for a corps five provinces off).

    BA3-X13   `battle_day.a_dead_day_bars_nothing` — night bars a pair only
              where the day was still a day when night began; down: every day
              open at nightfall bars its pair.

    BA3-X16   `campaign_variance.an_order_draws_its_own_temper` — the seeded
              temper's identity carries the order's own mark (its stance, its
              recruit type, its count); down: marshal, action and target.

    BA3-X15   `battle_day.a_lead_holds_one_day` — a second hanging great
              battle of a lead whose day is open opens none (the user's
              ruling at the plan gate); down: a day a hanging great battle.

    BA3-X14   `battle_day.his_word_is_scored_from_the_day` — his word's order
              is scored from a stream of the day's own; down: his court's
              stream of the phase.
"""
from __future__ import annotations

BA4_SEAMS_BY_ROW = {
    "BA2-X2": [
        "backend.ai.enemy_ai:a_corps_raised_mid_phase_takes_its_turn=False",
    ],
    "BA2-X12": [
        "backend.commands.combat_executor:a_battery_is_spared_its_own_shells=False",
    ],
    "BA2-X10": [
        "backend.commands.strategic:a_road_round_keeps_to_open_frontiers=False",
    ],
    "APPROACH": [
        "backend.commands.strategic:a_support_order_halts_before_the_friends_foe=False",
    ],
    "BA2-X20": [
        "backend.game_logic.intel_surfaces:a_battle_lights_its_field_only_for_those_who_fought=False",
    ],
    "PURSUIT": [
        "backend.commands.combat_executor:a_pursuit_is_any_corps_that_fought=False",
    ],
    "QUARTERS": [
        "backend.commands.combat_executor:the_last_hour_brings_three_quarters=False",
    ],
    "TELL": [
        "backend.commands.combat_executor:the_muster_names_only_an_order_that_brings=False",
        "backend.game_logic.battle_day:a_word_is_quoted_in_points=False",
        "backend.game_logic.battle_day:a_day_is_one_battle=False",
        "backend.game_logic.battle_day:a_days_close_is_told=False",
    ],
    "BA4-X1": [
        "backend.game_logic.battle_day:a_brought_up_corps_is_one_the_table_offers=False",
    ],
    "BA3-X13": [
        "backend.game_logic.battle_day:a_dead_day_bars_nothing=False",
    ],
    "BA3-X16": [
        "backend.game_logic.campaign_variance:an_order_draws_its_own_temper=False",
    ],
    "BA3-X15": [
        "backend.game_logic.battle_day:a_lead_holds_one_day=False",
    ],
    "BA3-X14": [
        "backend.game_logic.battle_day:his_word_is_scored_from_the_day=False",
    ],
}
BA4_SEAMS_DOWN = [spec for row in BA4_SEAMS_BY_ROW
                  for spec in BA4_SEAMS_BY_ROW[row]]

# The key bar — no switch but a number: the men a battle must engage, both
# sides together, to be fought on as a day when it hangs. The session's rule
# (M6, `BATTLE_DIORAMA_SPEC.md` §15.19) picked 50,000 where the game had the
# great battle's own 80,000 (`battle_day.key_bar`, one function). The session
# OFF holds it at 80,000: a board recorded before the session replays under
# the bar it was recorded under, and the measure's arm 0 is the commit before
# on a served campaign too. (Found by the full suite on the final tree: the
# scripted volte-face arm, RS-27, meets five days at 50,000 where it met
# three, and its beat returns with the bar held.)
BA4_THE_KEY_BAR = ["backend.game_logic.battle_day:key_bar=80000"]
BA4_SESSION_OFF = BA4_SEAMS_DOWN + BA4_THE_KEY_BAR
