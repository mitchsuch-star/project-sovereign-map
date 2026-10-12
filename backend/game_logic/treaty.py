"""The treaty's ONE verdict — DD-1 "The Table and the Treaty", Step 2.

Pre-Deploy S7 (October 11, 2026; `docs/PRE_DEPLOY_PLAN.md` §3.1). The
quarter's diplomacy P1s all had one shape: the table said yes and the treaty
said no — "can this be signed?" was answered in six places and the ratifier
kept the only maintained copy. This module is where that answer lives.

Slice A (this file's first landing) carries the WORDS for a declaration the
war-instance model refuses (DD1-11): the engine's code
(`war_instance_side_conflict`) never reaches the player. Slice B adds
`can_sign(world, letter) -> Verdict`, the ratifier's guard sequence lifted
out and read by every surface AND the ratifier.
"""
from __future__ import annotations

from typing import Any, Dict, Optional


def _court(world, nation: str, *, capitalize: bool = False) -> str:
    """A court by its formed display name, with its article."""
    from backend.display_names import with_definite_article
    from backend.game_logic.formations import formed_display_name
    shown = formed_display_name(world, nation) if nation else "a foreign court"
    return with_definite_article(shown, capitalize=capitalize)


def _other_side_leader(world, war_id: Optional[str], *nations: str) -> str:
    """The leader of the side NONE of `nations` stand on in `war_id`, or ''."""
    instance = (getattr(world, "war_instances", {}) or {}).get(str(war_id or ""))
    if not isinstance(instance, dict):
        return ""
    sides = instance.get("side_by_nation") or {}
    on = {str(sides.get(n) or "") for n in nations if n}
    on.discard("")
    if len(on) != 1:
        return ""
    side = next(iter(on))
    other = "defender_leader" if side == "attackers" else "attacker_leader"
    return str(instance.get(other) or "")


def declaration_refusal_words(world, aggressor: str, target: str,
                              result: Dict[str, Any]) -> str:
    """DD1-11: the sentence a refused declaration shows the player — the
    clause in words, read off the instance that refused it. `result` is the
    dict `ensure_war_instance_for_pair` / `validate_war_declaration` returned
    (`error`, `details`); the code and its details still ride the executor's
    result for the log and the tests, never this sentence."""
    error = str((result or {}).get("error") or "")
    details = (result or {}).get("details") or {}
    player = getattr(world, "player_nation", "France")
    target_shown = _court(world, target, capitalize=True)
    aggressor_shown = _court(world, aggressor)
    if error == "war_instance_side_conflict":
        leader = _other_side_leader(world, details.get("war_id"), aggressor, target)
        if aggressor == player:
            beside = "beside us"
        else:
            beside = f"beside {aggressor_shown}"
        if leader and leader not in (aggressor, target):
            return (f"{target_shown} fights {beside} in the war with "
                    f"{_court(world, leader)} — end that war first.")
        return (f"{target_shown} fights {beside} already — a declaration would "
                f"set one side of a war against itself. End that war first.")
    if error == "war_instance_merge_required":
        return (f"{target_shown} and {aggressor_shown} already stand on one side "
                f"of a war — a declaration would set that side against itself.")
    return (f"The chancery finds no lawful ground for a war on {_court(world, target)} "
            f"today.")
