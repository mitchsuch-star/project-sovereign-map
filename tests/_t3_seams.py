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
}
T3_SEAMS_DOWN = [spec for row in T3_SEAMS_BY_ROW
                 for spec in T3_SEAMS_BY_ROW[row]]
