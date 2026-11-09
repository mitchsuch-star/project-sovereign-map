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
}
T3_SEAMS_DOWN = [spec for row in T3_SEAMS_BY_ROW
                 for spec in T3_SEAMS_BY_ROW[row]]
