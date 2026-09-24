"""GE-1 "The Verdict and the Fall" — the two clocks of the Fall of the Empire.

Spec: docs/GAME_END_SPEC.md §2 R1 (the gate record) and docs/ENDGAME_PLAN.md
§3 (RULED). The third arm of the Fall — the Emperor's death — is not a clock:
it is immediate, and lives at the ONE removal seam (`WorldState.destroy_marshal`)
beside the rule it breaks, with its constants in `game_end`.

Two arms, each a warned clock:

* **"The Empire Without Soil or Sword"** (`soil_or_sword`) — the realm holds
  at most one province (the ONE collapse predicate, `collapse.get_collapse_state`,
  read and never forked — SYSTEMS_REFERENCE §41), OR no free corps stands and
  no marshal can be commissioned (`recruitment.first_affordable_commission`,
  the executor's own gate). Five consecutive turns and the Empire falls.
* **"The Eagle in Chains"** (`chains`) — the sovereign is a prisoner. Ten
  consecutive turns unfreed and the regency falls.

**The Fall is a death in war.** Both clocks run only while the war that
threatens them is being fought:

* the soil-or-sword clock ticks only while the realm is at WAR with at least
  one court, and resets the turn it is at war with nobody — a France that has
  made its peace, however humbled, is a rump state and not a fallen one (the
  Humbled Peace continues; ENDGAME_PLAN §3);
* the chains clock ADVANCES only on a turn the realm is at WAR with the court
  that holds him, and PAUSES — never resets — while a truce (or a vassal
  treaty) stands between them. It resets only on release. A truce always ends
  in war (the clock resumes) or in peace (which frees him —
  `set_diplomatic_state` releases mutual prisoners on WAR/ARMISTICE → PEACE),
  so a pause can never become a permanent hiding place.

**Exits, per disjunct (the §5 test 2 contradiction, resolved):** the realm
arm lifts when a second province is held again, or when peace is made; the
sword arm lifts when a corps stands free again — a marshal commissioned, a
prisoner released (a release returns him at the head of 5,000 men) — or when
peace is made; the chains arm lifts when he is freed — by the captor's terms
(any peace with his captor releases him; the captor OFFERS those terms, priced
to the purse — `ai_diplomacy`'s captor rung, the reachability proof R1
requires), or by storming the city that holds him.

**Paris alone never triggers either arm** (PL-31): the realm arm reads the
province COUNT, and a France that loses Paris and holds ten provinces is not
collapsed.

GR5: `get_fall_state(world, nation)` answers for ANY nation — the same two
predicates. Only the player's clocks are kept (ONE serialized `fall_clock`),
because only the player's Fall ends the game; AI courts keep losing the way
they always have, by elimination and by suing through the peace rungs (R5).

The ONE writer is `tick_fall_clocks`, called once per end turn from
`game_end.process_end_of_turn` AFTER `advance_turn` (never from the victory
check, which runs twice a turn, and never from the dispatch, which is rebuilt
in pins). Everything else here is a pure read.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

# ── The arms ────────────────────────────────────────────────────────────────
ARM_SOIL = "soil_or_sword"
ARM_CHAINS = "chains"
ARMS = (ARM_CHAINS, ARM_SOIL)   # the order a same-turn double fall is read in

# R1's blessed graces (in-band tunable; the scenario's `campaign_end` block
# may author its own — `game_end.cfg`).
FALL_GRACE_TURNS = 5
CAPTIVITY_GRACE_TURNS = 10

ARM_TITLES = {
    ARM_SOIL: "The Empire Without Soil or Sword",
    ARM_CHAINS: "The Eagle in Chains",
}

# Flip lever (the file convention): False keeps both clocks silent — no
# tick, no warning, no Fall — which is the pre-GE-1 sandbox byte-for-byte.
THE_EMPIRE_CAN_FALL = True


# ════════════════════════════════════════════════════════════════════════
# Predicates — pure reads (GR5: any nation).
# ════════════════════════════════════════════════════════════════════════

def free_corps(world, nation: str) -> List[Any]:
    """Every standing corps of `nation`: strength > 0 and not a prisoner.

    The same test as `collapse.get_collapse_state`'s `standing` and
    `recruitment._standing_count` (one rule, three readers). The roster, not
    the map (GR8)."""
    return [m for m in getattr(world, "marshals", {}).values()
            if m.nation == nation
            and int(getattr(m, "strength", 0) or 0) > 0
            and not getattr(m, "captured_by", "")]


def sovereign_of(world, nation: str):
    """The nation's LIVING sovereign marshal (free or captive), or None."""
    for m in getattr(world, "marshals", {}).values():
        if m.nation == nation and getattr(m, "is_sovereign", False):
            return m
    return None


def _at_war_with_anyone(world, nation: str) -> bool:
    try:
        return bool(world.get_nations_at_war_with(nation))
    except Exception:
        return False


def _grace(world, arm: str) -> int:
    from backend.game_logic import game_end
    if arm == ARM_CHAINS:
        return int(game_end.cfg(world, "captivity_grace_turns",
                                CAPTIVITY_GRACE_TURNS))
    return int(game_end.cfg(world, "fall_grace_turns", FALL_GRACE_TURNS))


def _soil_or_sword(world, nation: str) -> Optional[Dict[str, Any]]:
    """The realm-or-sword predicate, or None when the realm stands."""
    from backend.game_logic import collapse
    state = collapse.get_collapse_state(world, nation)
    corps = free_corps(world, nation)
    no_sword = False
    if not corps:
        try:
            from backend.game_logic.recruitment import first_affordable_commission
            no_sword = first_affordable_commission(world, nation) is None
        except Exception:
            no_sword = True
    if state is None and not no_sword:
        return None
    return {
        "realm": state is not None,        # ≤ 1 province (the collapse)
        "sword": bool(no_sword),           # no free corps, no commission
        "collapse": state,
    }


def _chains(world, nation: str) -> Optional[Dict[str, Any]]:
    """The captive-sovereign predicate, or None while he is free (or gone)."""
    sov = sovereign_of(world, nation)
    captor = (getattr(sov, "captured_by", "") or "") if sov is not None else ""
    if not captor:
        return None
    return {
        "sovereign": sov.name,
        "captor": captor,
        "captured_turn": int(getattr(sov, "captured_turn", -1) or -1),
        "at_war_with_captor": bool(world.is_at_war(nation, captor)),
    }


# ════════════════════════════════════════════════════════════════════════
# The state — what every surface reads.
# ════════════════════════════════════════════════════════════════════════

def _clock(world, nation: str, arm: str) -> Dict[str, Any]:
    if nation != getattr(world, "player_nation", None):
        return {}
    return dict((getattr(world, "fall_clock", {}) or {}).get(arm) or {})


def _exits(world, nation: str, arm: str, detail: Dict[str, Any]) -> List[str]:
    """The exits a player can walk, stated as roads — never the rule."""
    from backend.game_logic.formations import formed_display_name
    if arm == ARM_CHAINS:
        captor = formed_display_name(world, detail["captor"])
        return [f"accept {captor}'s terms — any peace with {captor} frees him",
                "storm the city that holds him"]
    exits: List[str] = []
    if detail.get("realm"):
        exits.append("retake a province")
    if detail.get("sword"):
        exits.append("commission a marshal or free a captive corps")
    exits.append("make peace")
    return exits


def _arm_view(world, nation: str, arm: str,
              detail: Dict[str, Any]) -> Dict[str, Any]:
    grace = _grace(world, arm)
    clock = _clock(world, nation, arm)
    turns = int(clock.get("turns", 0) or 0)
    if arm == ARM_CHAINS:
        ticking = bool(detail.get("at_war_with_captor"))
    else:
        ticking = _at_war_with_anyone(world, nation)
    turns_left = max(0, grace - turns)
    current = int(getattr(world, "current_turn", 0) or 0)
    return {
        "arm": arm,
        "title": ARM_TITLES[arm],
        "detail": detail,
        "turns": turns,
        "grace": grace,
        "turns_left": turns_left,
        "ticking": ticking,
        # The end of turn on which the arm fires if nothing changes: the
        # tick at the end of turn N moves the clock one step, and the arm
        # fires on the tick that reaches the grace.
        "falls_at_end_of_turn": int(current - 1 + turns_left) if turns else None,
        "exits": _exits(world, nation, arm, detail),
    }


def get_fall_state(world, nation: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Every fall arm that holds for `nation`, with its clock — or None.

    Armed worlds only (`game_end.endings_armed`): the bare flag world, the
    tutorial and the legacy map never answer (R7). GR5: the predicate is
    the same for any nation; the clock is kept for the player alone."""
    from backend.game_logic import game_end
    if not THE_EMPIRE_CAN_FALL or world is None:
        return None
    if not game_end.endings_armed(world):
        return None
    nation = nation or getattr(world, "player_nation", None)
    if not nation:
        return None
    arms: Dict[str, Dict[str, Any]] = {}
    chains = _chains(world, nation)
    if chains is not None:
        arms[ARM_CHAINS] = _arm_view(world, nation, ARM_CHAINS, chains)
    soil = _soil_or_sword(world, nation)
    if soil is not None:
        arms[ARM_SOIL] = _arm_view(world, nation, ARM_SOIL, soil)
    if not arms:
        return None
    running = [a for a in arms.values() if a["turns"] > 0]
    soonest = (min(running, key=lambda a: (a["turns_left"], ARMS.index(a["arm"])))
               if running else None)
    return {
        "nation": nation,
        "arms": arms,
        "soonest": soonest,
    }


# ════════════════════════════════════════════════════════════════════════
# The ONE writer.
# ════════════════════════════════════════════════════════════════════════

def tick_fall_clocks(world) -> Optional[str]:
    """Advance the player's clocks one turn. Returns the arm that FELL this
    tick (the caller records the ending), or None.

    Called once per end turn after `advance_turn`. An arm whose predicate
    no longer holds is dropped from `fall_clock` (its clock resets)."""
    from backend.game_logic import game_end
    if not THE_EMPIRE_CAN_FALL or not game_end.endings_armed(world):
        return None
    if game_end.terminal_ending(world) is not None:
        return None
    nation = getattr(world, "player_nation", None)
    if not nation:
        return None
    clock = getattr(world, "fall_clock", None)
    if not isinstance(clock, dict):
        clock = {}
        world.fall_clock = clock
    turn = int(getattr(world, "current_turn", 0) or 0)

    # The chains: advance while at war with the captor; pause in a truce;
    # reset (drop) on release or a change of captor.
    chains = _chains(world, nation)
    if chains is None:
        clock.pop(ARM_CHAINS, None)
    else:
        entry = clock.get(ARM_CHAINS)
        if not isinstance(entry, dict) or entry.get("captor") != chains["captor"]:
            entry = {"turns": 0, "since": turn, "captor": chains["captor"]}
        if chains["at_war_with_captor"]:
            entry["turns"] = int(entry.get("turns", 0)) + 1
            entry["paused"] = False
        else:
            entry["paused"] = True
        clock[ARM_CHAINS] = entry

    # The soil or the sword: tick while at war with anyone; reset at peace
    # or when both disjuncts lift.
    soil = _soil_or_sword(world, nation)
    if soil is None or not _at_war_with_anyone(world, nation):
        clock.pop(ARM_SOIL, None)
    else:
        entry = clock.get(ARM_SOIL)
        if not isinstance(entry, dict):
            entry = {"turns": 0, "since": turn}
        entry["turns"] = int(entry.get("turns", 0)) + 1
        entry["realm"] = bool(soil["realm"])
        entry["sword"] = bool(soil["sword"])
        clock[ARM_SOIL] = entry

    for arm in ARMS:
        entry = clock.get(arm)
        if isinstance(entry, dict) and int(entry.get("turns", 0)) >= _grace(world, arm):
            return arm
    return None


# ════════════════════════════════════════════════════════════════════════
# The words — every surface composes from these.
# ════════════════════════════════════════════════════════════════════════

def _join(items: List[str]) -> str:
    items = [i for i in items if i]
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} or {items[1]}"
    return ", ".join(items[:-1]) + f", or {items[-1]}"


def arm_condition_sentence(world, view: Dict[str, Any]) -> str:
    """What holds, in one sentence — never the rule's name."""
    from backend.game_logic import collapse
    from backend.game_logic.formations import formed_display_name
    detail = view["detail"]
    if view["arm"] == ARM_CHAINS:
        captor = formed_display_name(world, detail["captor"])
        return f"The Emperor is a prisoner of {captor}."
    parts: List[str] = []
    state = detail.get("collapse")
    if state is not None:
        parts.append(collapse.realm_sentence(world, state))
    if detail.get("sword"):
        parts.append("No corps of ours stands free, and no marshal can be "
                     "commissioned.")
    return " ".join(parts)


def arm_clock_sentence(world, view: Dict[str, Any]) -> str:
    """The clock and its exits, in one breath.

    "The Empire falls at the end of turn 17 — 2 turns remain — unless we
    retake a province or make peace." Honest when paused ("…the clock
    stands still while the truce holds.") and when not yet running."""
    from backend.display_names import plural
    title = view["title"].upper()
    exits = _join(view["exits"])
    turns, grace = view["turns"], view["grace"]
    if view["arm"] == ARM_CHAINS:
        if not view["ticking"]:
            return (f"{title}: {turns} of {grace} turns of captivity counted — "
                    f"the clock stands still while there is no war with his "
                    f"captor. To free him: {exits}.")
        if turns <= 0:
            return (f"{title}: the regency falls after {plural(grace, 'turn')} "
                    f"of captivity unless he is freed — {exits}.")
        return (f"{title}: {turns} of {grace} — the regency falls at the end "
                f"of turn {view['falls_at_end_of_turn']} "
                f"({_remain(view['turns_left'])}) unless he is "
                f"freed: {exits}.")
    if not view["ticking"]:
        return (f"{title}: at peace, no clock runs against the Empire — a new "
                f"war would start one ({plural(grace, 'turn')}).")
    if turns <= 0:
        return (f"{title}: the Empire falls after {plural(grace, 'turn')} of "
                f"this unless we {exits}.")
    return (f"{title}: {turns} of {grace} — the Empire falls at the end of "
            f"turn {view['falls_at_end_of_turn']} "
            f"({_remain(view['turns_left'])}) unless we {exits}.")


def _remain(n: int) -> str:
    """'1 turn remains' / '3 turns remain' — the verb agrees."""
    from backend.display_names import plural
    return f"{plural(n, 'turn')} {'remains' if int(n) == 1 else 'remain'}"


def scope_sentence(world, nation: Optional[str] = None) -> str:
    """The tail every collapse surface ends on (IQ-2's `CAMPAIGN_CONTINUES`,
    re-pointed by R9): the clock and its exits where the rules are authored,
    the old sentence where they are not (the bare flag world, the tutorial,
    the lever down) — so the unarmed surfaces are byte-identical."""
    from backend.game_logic import collapse
    state = get_fall_state(world, nation)
    if state is None:
        from backend.game_logic import game_end
        if game_end.endings_armed(world):
            from backend.display_names import plural
            return ("The Empire can still fall: a realm reduced to one province, "
                    "or left with no corps and no marshal to commission, falls "
                    f"after {plural(_grace(world, ARM_SOIL), 'turn')} of war.")
        return collapse.CAMPAIGN_CONTINUES
    view = state["soonest"] or state["arms"].get(ARM_CHAINS) or state["arms"].get(ARM_SOIL)
    return arm_clock_sentence(world, view)


def warning_state(world) -> Optional[Dict[str, Any]]:
    """The defeat-imminent warning on an ARMED world — the clock and the
    exits named (R1), for the player. None when no arm holds."""
    state = get_fall_state(world)
    if state is None:
        return None
    from backend.game_logic import collapse
    arms = [state["arms"][a] for a in ARMS if a in state["arms"]]
    collapse_state = None
    soil = state["arms"].get(ARM_SOIL)
    if soil is not None:
        collapse_state = soil["detail"].get("collapse")
    lead_parts: List[str] = []
    if collapse_state is not None:
        lead_parts.append(collapse.summary_line(world, collapse_state))
    else:
        for view in arms:
            lead_parts.append(arm_condition_sentence(world, view))
    clock_parts = [arm_clock_sentence(world, v) for v in arms]
    soonest = state["soonest"]
    critical = bool(soonest and soonest["ticking"]
                    and soonest["turns_left"] <= 2) or (
        collapse_state is not None
        and collapse_state["tier"] == collapse.TIER_FALLEN)
    title = (soonest or arms[0])["title"]
    return {
        "message": " ".join([p for p in lead_parts if p] + clock_parts),
        "severity": "critical" if critical else "warning",
        "notification_title": title,
        "heading": "THE FALL OF THE EMPIRE",
        "fall": {
            "arms": [
                {"arm": v["arm"], "title": v["title"], "turns": int(v["turns"]),
                 "grace": int(v["grace"]), "turns_left": int(v["turns_left"]),
                 "ticking": bool(v["ticking"]),
                 "falls_at_end_of_turn": (int(v["falls_at_end_of_turn"])
                                          if v["falls_at_end_of_turn"] is not None
                                          else None),
                 "exits": list(v["exits"])}
                for v in arms
            ],
        },
    }
