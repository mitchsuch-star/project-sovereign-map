"""Tier 2's content seams — each behavioural slice of the Concert's Tier 2
behind a named FUNCTION a series arm can replace
(`tools/playtest_driver.py --seam MODULE:NAME=EXPR`, the S13b idiom; no
levers — the code-health ratchet stands at 231 of 231). The list is the
slice OFF; an attribution arm holds a seam down and must reproduce the
prior tree's reading byte for byte.

    T2-2  `agendas.a_fresh_peace_quiets_the_design` — peace closes the
          theatre: a region whose holder has just signed with the coveter
          is not coveted while the fresh-peace floor runs (the game's ONE
          fresh-peace rule, `coalition.fresh_peace_turns_left`, 5 turns);
          down: ink on the treaty changes nothing the morning after.

    T2-3  `war_council.a_bandwagoner_joins_the_stronger_side` — Prussia's
          hook: a court whose statecraft prefers the bandwagon rung joins
          a live AI-vs-AI war on the stronger side (relation with the
          weaker side's leader < 0), and reneges at most once a campaign
          when the scales turn; down: no court attaches itself to a war
          it was not called to.

    T2-4  `agendas.a_quiet_window_sleeps_the_arbiter` — Russia's two
          shores: a contain design sleeps once the court's own war with
          its hegemon has been over for the quiet window (8 turns, the
          ended-war witness required; WAR or ARMISTICE wakes it at
          once), so the deck advances — the arbiter stands down and
          `gulf_and_straits` wakes; down: the arbiter watches forever,
          the second shore never wakes by peace alone.

`hold_down(monkeypatch)` applies the list in-process
(`tests._standing_seams.hold_down` — one parser, one semantics).
"""
from __future__ import annotations

from tests._standing_seams import hold_down, parse  # noqa: F401

T2_SEAMS_BY_ROW = {
    "T2-2": ["backend.game_logic.agendas:a_fresh_peace_quiets_the_design=False"],
    "T2-3": ["backend.game_logic.war_council:a_bandwagoner_joins_the_stronger_side=False"],
    "T2-4": ["backend.game_logic.agendas:a_quiet_window_sleeps_the_arbiter=False"],
}
T2_SEAMS_DOWN = [spec for row in T2_SEAMS_BY_ROW
                 for spec in T2_SEAMS_BY_ROW[row]]
