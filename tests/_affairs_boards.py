"""RE-6 "Affairs of State" — the Edicts' offers stood aside on a crafted board.

The three offers (E1 the Magazines, E2 the Remounts, E3 the Camps of
Instruction — `docs/RECURRING_EVENTS_SPEC.md` §6.2) premise on boards the
older pins crafted for one letter alone: E1 wherever a corps draws campaign
pay (the Host's boards quarter corps on Bavaria), E2 while the cavalry pool
sits under 60 % of its cap (the boot's 15,000 of 30,000 never regenerates
under `moments.tick`). A pin that reads the Host's, the Chancellor's,
Berthier's or the Marine's morning alone calls `rest_the_offers` first: one
`passed` row per offer on `turn`, so each sits on its eight-turn cooldown
(`affairs.on_cooldown`) — never an arrival, so the act's cap of six and the
Watch are untouched — with no change to the authored deck. A pin that runs
past `turn` + 8 passes a later `turn`.
"""
from __future__ import annotations

OFFERS = ("the_magazines", "the_remounts", "camps_of_instruction")
# AU-3b (AUTHORITY_CURRENCY_SPEC.md §6.6.6): the Proclamation, armed by the
# user's "Arm it" (November 5, 2026)
AU3B_LETTERS = ("the_proclamation",)


def rest_the_offers(world, turn: int = 1) -> None:
    """Each offer passed over on `turn` — on cooldown until `turn` + 8."""
    state = world.moments.setdefault("state", {})
    lord = str(getattr(world, "player_nation", "") or "")
    for template in OFFERS:
        mid = f"{template}#1"
        state[mid] = {"id": mid, "status": "passed", "turn": int(turn), "reason": "premise",
                      "lord": lord, "bind": {}, "tier": 1}
    world.__dict__.pop("_affairs_memo", None)


def without_the_proclamation(world) -> None:
    """AU-3b's Proclamation — ARMED by the user's "Arm it" (November 5, 2026)
    — out of a crafted board's deck. Its premise is the war itself and its
    latch an enemy army seen within a march of the Emperor: the 1805 boot's
    own (Mack in Swabia, a march from the Emperor at Lorraine). Its streak is
    the war's, so on a board crafted for one letter it out-stands that letter
    and takes the pulse and a Watch slot from it (AU-2c's isolation idiom,
    `_without_au2c_letters`; a rest would hold it only twelve mornings). Its
    own pins: `tests/test_standing_offices.py`; its measured interplay: the
    reach record (`tests/test_affairs_reach.py`)."""
    aff = world.moments["block"]["affairs"]
    aff["deck"] = [e for e in aff["deck"] if e.get("id") not in AU3B_LETTERS]
    world.__dict__.pop("_affairs_memo", None)
