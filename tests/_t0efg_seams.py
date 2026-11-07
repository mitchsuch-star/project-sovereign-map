"""T0-E / T0-F / T0-G — the November 6, 2026 review's series-moving fixes,
each behind a named FUNCTION a series arm can replace
(`tools/playtest_driver.py --seam MODULE:NAME=EXPR`, the S13b idiom; no
levers — the code-health ratchet is at 231 of 231). The list is the fix
OFF; `tools/_t0efg_series_arms.py` holds each seam down with its reach
counted in the child, and arm 0 (every seam down) reproduces the tree
before the three slices.

    T0E-P39  `enemy_ai.p39_reads_the_brakes`        — GR-35: the jealousy
             glory hunt routed through `_engageable_enemies`; down: the
             hunt reads only the crossing and the odds
    T0E-STM  `enemy_ai.storms_read_the_pair`        — GR-36: P4.25 reads
             the pair stamp for its garrison target; down: the same
             garrison stormed 2-3 times a phase
    T0E-DSP  `enemy_ai.desperation_reads_the_brakes` — GR-1 (+ the in-arm
             sibling): the stagnation breaker's two attack arms routed
             through `_engageable_enemies`; down: Deroy's third assault
    T0F-BRW  `coalition.brew_follows_formation`     — GR-4/GR-39: the brew
             reads the formation's member rule at both brew sites, and a
             failed expiry rests the chanceries; down: the 3-turn loop
    T0F-ASK  `ai_diplomacy.a_refused_ask_rests`     — GR-41: a refused
             design ask stamps and reads the ordered-pair cooldown
             (6/12/18); down: the fixed 6-turn cadence
    T0G-RCH  `reforms.the_staff_must_be_reachable`  — GR-47: the rung (and
             the counsel's hint) saves only for a Staff whose ceiling
             stands at the bar; down: the unconditional save, the band
    T0G-EDS  `affairs.edicts_respect_the_save`      — GR-15: a saving
             court's gold decrees held, the authority Decree open; down:
             the rung spends the chest the Staff needs

`hold_down(monkeypatch)` applies the same list in-process
(`tests._standing_seams.hold_down` — one parser, one semantics).
"""
from __future__ import annotations

from tests._standing_seams import hold_down, parse  # noqa: F401

T0EFG_SEAMS_BY_ROW = {
    "T0E-P39": ["backend.ai.enemy_ai:p39_reads_the_brakes=False"],
    "T0E-STM": ["backend.ai.enemy_ai:storms_read_the_pair=False"],
    "T0E-DSP": ["backend.ai.enemy_ai:desperation_reads_the_brakes=False"],
    "T0F-BRW": ["backend.game_logic.coalition:brew_follows_formation=False"],
    "T0F-ASK": ["backend.game_logic.ai_diplomacy:a_refused_ask_rests=False"],
    "T0G-RCH": ["backend.game_logic.reforms:the_staff_must_be_reachable=False"],
    "T0G-EDS": ["backend.game_logic.affairs:edicts_respect_the_save=False"],
}
T0EFG_SEAMS_DOWN = [spec for row in T0EFG_SEAMS_BY_ROW
                    for spec in T0EFG_SEAMS_BY_ROW[row]]
