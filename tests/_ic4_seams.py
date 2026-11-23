"""Row IC, Session 4 — "the voice, and the other side of the hill" (November 22,
2026): the session's seams, held DOWN.

`docs/INDEPENDENT_COMMAND_SPEC.md` §10 (the enemy), §13 (R-INERT, R-HILL,
R-HUNT). Every rule of the session that can move the board sits behind a named
zero-argument FUNCTION in the module it gates (`tools/playtest_driver.py --seam
MODULE:NAME=EXPR`; no levers). This list is the session OFF: with every row
down the game is the commit before (`b69d0a5e`), and a board recorded before the
session replays under the rules it was recorded under (`tests/_oct27_seams.py`
folds these rows in, as it folds row OC's). The rows stand in LADDER order — the
measure's arms bring them up one by one (`tools/_ic4_measure.py`).

    PLAN      IC-14 — `war_plans.the_courts_follow_a_plan`: each court at war
              WITH FRANCE (the coalition, when courts fight her together) draws
              a written war plan; its marshals who follow orders to the letter
              are moved by the plan's exact orders (`war_plans.the_pass`, before
              the enemy's phase) and by nothing else but survival, a battle they
              are in, the ground they stand on and the road home. Down: no pass,
              no plan order, no gate — the court's own logic moves every man, as
              before. Built in Session 4 and shipped down (R-HILL (4) missed);
              FIXED November 23, 2026 by the user's "fix warplans" (IC4-D1: a
              plan drawn only against France) and measured again — the thirty
              seeds still raise no minor with it up, 200 fresh seeds raise one
              as often up as down (SYSTEMS_REFERENCE §236.8) — and SHIPS UP by
              his word on those numbers, "Switch them on".

    FAVOUR    IC-14 — `war_plans.a_plan_names_a_favoured_province`: a plan's
              step names ONE province the court's other corps lean toward (the
              march's pull — `EnemyAI._agenda_covet_set` — never the permission
              `war_council.annexation_permitted`). Down: the pull is the court's
              aims alone, as before. Up as written, and INERT while PLAN is
              down (no plan is drawn, so no province is favoured).

    LEARNS    IC-15, the design's §10.3 — `war_plans.a_court_learns_a_routed_mans_task`:
              a French marshal ON HIS OWN who is routed gives his task away; if
              he was to take a place, the court's corps favour it for five
              turns. Down: nothing is learned. Up as written, and INERT while
              PLAN is down (a court with no plan has nowhere to keep it).

    MOOD      IC-14, §10.6 — `enemy_ai.each_man_has_his_own_mood`: an enemy
              marshal's mood is drawn from the campaign seed, the turn and HIS
              NAME, not from his nation's one stream in call order. SHIPS DOWN —
              an arm of the measure, adopted only with the user's word.

    HUNT      IC-15, §10.5 — `enemy_ai.the_enemy_hunts_a_lone_corps`: one term
              in the enemy's advance that draws it toward a French corps it can
              see with no friend within one march. SHIPS DOWN — an arm of the
              measure (R-HUNT), adopted only with the user's word.

    FIGHT     IC-14's arm for the user's decision —
              `war_plans.a_planned_man_still_strikes_at_good_odds`: a marshal
              under a plan keeps today's fighting sense (his court's attack
              rung, one thing a turn); his orders still decide where he stands
              and when he falls back. SHIPS DOWN; inert while PLAN is down.

`the_plan_forced` (`war_plans`) is NOT a row: it is the measure's own lever —
it names the plan every holder draws ("" as shipped: the seed draws).

The voice (IC-13) and what France learns of the plans (IC-15's store) carry no
seam by design: neither moves a corps nor a die — the lines are display, the
store is what was learned. Their proof is arm 0: both are in it, and arm 0 must
equal `b69d0a5e` on every surface.
"""
from __future__ import annotations

IC4_SEAMS_BY_ROW = {
    "PLAN": ["backend.game_logic.war_plans:the_courts_follow_a_plan=False"],
    "FAVOUR": ["backend.game_logic.war_plans:a_plan_names_a_favoured_province=False"],
    "LEARNS": ["backend.game_logic.war_plans:a_court_learns_a_routed_mans_task=False"],
    "MOOD": ["backend.ai.enemy_ai:each_man_has_his_own_mood=False"],
    "HUNT": ["backend.ai.enemy_ai:the_enemy_hunts_a_lone_corps=False"],
    "FIGHT": ["backend.game_logic.war_plans:a_planned_man_still_strikes_at_good_odds=False"],
}

# As shipped (November 23, 2026 — the user's "Switch them on"): the plans are
# UP, and with them the two rows that read a plan; the three arms are DOWN.
IC4_SHIPPED_UP = ("PLAN", "FAVOUR", "LEARNS")
IC4_SHIPPED_DOWN = ("MOOD", "HUNT", "FIGHT")

IC4_SEAMS_DOWN = [spec for row in IC4_SEAMS_BY_ROW for spec in IC4_SEAMS_BY_ROW[row]]
