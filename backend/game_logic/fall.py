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
  one court, PAUSES (never resets) while its only quarrels stand in a truce,
  and resets the turn it is at war and in truce with nobody — a France that
  has made its peace, however humbled, is a rump state and not a fallen one
  (the Humbled Peace continues; ENDGAME_PLAN §3). A truce is not a peace
  (review round, Sept 25): signing one at 4 of 5 bought a whole new clock;
* the chains clock ADVANCES only on a turn the realm is at WAR with the court
  that holds him, and PAUSES — never resets — while a truce stands between
  them. It resets only on release, or on a fresh capture (the entry is keyed
  on the captivity itself — captor AND the turn he was taken — so freed and
  re-taken is a new clock). A truce always ends in war (the clock resumes)
  or in peace (which frees him), so a pause can never become a permanent
  hiding place. **No court out of war with his realm holds him**
  (verification round, Sept 25): every transition that leaves the war —
  peace, a vassal treaty, a forced alliance, a vassal's release — frees
  him at the ONE setter (`free_captive_sovereigns`, called from
  `diplomacy.set_diplomatic_state`); a lapsed safe passage escorts him home
  (`withdrawal._intern`); and a corps emptied with no court at war to take
  him is set down at home rather than handed to a court at peace
  (`WorldState.destroy_marshal`). On the turn a truce runs out, the pause
  reads the truce's own end (`diplomacy.armistice_resolves_this_turn`): a
  truce that collapses into war at this advance is a clock that TICKS this
  turn, dated and at its true severity.

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


def _in_truce_with_anyone(world, nation: str) -> bool:
    """A standing ARMISTICE with any court — the pause, not the peace. One
    pass over the pair dict (never the regions — GR8)."""
    for key, state in (getattr(world, "diplomatic_states", {}) or {}).items():
        if state != "ARMISTICE":
            continue
        if nation in str(key).split("|"):
            return True
    return False


def _truce_ends_in(world, nation: str, only: str = "") -> str:
    """How the realm's truces end at THIS end turn's advance: 'war' when any
    of them collapses back into war, 'peace' when every one that ends ends in
    peace, '' when none ends this turn. `only` narrows to the truce with one
    court (the captor). One pass over the pair dict (GR8)."""
    from backend.game_logic.diplomacy import armistice_resolves_this_turn
    outcomes = []
    for key, state in (getattr(world, "diplomatic_states", {}) or {}).items():
        if state != "ARMISTICE":
            continue
        parts = str(key).split("|")
        if len(parts) != 2 or nation not in parts:
            continue
        other = parts[0] if parts[1] == nation else parts[1]
        if only and other != only:
            continue
        outcome = armistice_resolves_this_turn(world, nation, other)
        if outcome:
            outcomes.append(outcome)
    if "war" in outcomes:
        return "war"
    return "peace" if outcomes else ""


def free_captive_sovereigns(world, nation_a: str, nation_b: str) -> List[str]:
    """No court out of war with a sovereign's realm holds him (verification
    round). Called from the ONE diplomatic-state setter after every change
    that leaves the pair outside WAR and ARMISTICE: a sovereign of either
    side held by the other goes home through the release seam. Returns the
    names freed. GR5 by construction — any nation's sovereign; the 1805
    board authors one, and the ambient AI-vs-AI board holds none captive."""
    freed: List[str] = []
    for nation, captor in ((nation_a, nation_b), (nation_b, nation_a)):
        sov = sovereign_of(world, nation)
        if sov is None or (getattr(sov, "captured_by", "") or "") != captor:
            continue
        try:
            if world.release_captured_marshal(sov.name, reason="peace_treaty"):
                freed.append(sov.name)
        except Exception:
            continue
    return freed


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
    try:
        state = str(world.get_diplomatic_state(nation, captor) or "")
    except Exception:
        state = ""
    return {
        "sovereign": sov.name,
        "captor": captor,
        "captured_turn": int(getattr(sov, "captured_turn", -1) or -1),
        "at_war_with_captor": bool(world.is_at_war(nation, captor)),
        # The live relation to the captor, so the exits say only what can be
        # done from where we stand (review round: "any peace with Prussia
        # frees him" was shown to a France already at peace with Prussia).
        "captor_state": state,
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
        state = str(detail.get("captor_state") or "")
        if state == "WAR" or (not state and detail.get("at_war_with_captor")):
            return [f"accept {captor}'s terms — any peace with {captor} frees him",
                    "storm the city that holds him"]
        if state == "ARMISTICE":
            return [f"turn the truce with {captor} into a peace — the peace "
                    f"frees him",
                    "storm the city that holds him once the truce is over"]
        # At peace, or bound by treaty: no peace remains to be signed, so
        # none is offered as the road (the review's copy defect).
        return [f"make war on {captor} and storm the city that holds him"]
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
        paused_by = "captor" if not ticking else ""
        truce_ends = (_truce_ends_in(world, nation, only=str(detail.get("captor") or ""))
                      if not ticking and detail.get("captor_state") == "ARMISTICE"
                      else "")
    else:
        ticking = _at_war_with_anyone(world, nation)
        paused_by = ("truce" if not ticking and _in_truce_with_anyone(world, nation)
                     else "")
        truce_ends = _truce_ends_in(world, nation) if paused_by == "truce" else ""
    # A truce that collapses back into war at THIS end turn's advance is a
    # clock that ticks this turn (verification round): the war resumes inside
    # the advance and the tick counts it, so the pause is over before the
    # player can act on "the clock stands still".
    resuming = bool(not ticking and truce_ends == "war")
    counting = bool(ticking or resuming)
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
        "paused_by": paused_by,
        # 'war' / 'peace' when the pausing truce ends this turn, else ''.
        "truce_ends": truce_ends,
        "resuming": resuming,
        # The end of turn on which the arm fires if nothing changes: the
        # tick at the end of turn N moves the clock one step, and the arm
        # fires on the tick that reaches the grace. None while the clock
        # stands still — a paused arm has no date (the review round: it
        # reported a fall turn that slid forward every turn and never came)
        # — unless its truce ends in war this very turn.
        "falls_at_end_of_turn": (int(current - 1 + turns_left)
                                 if turns and counting else None),
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
    # A TICKING arm outranks a paused one whatever its count: the one clock
    # that will actually end the game is the one every surface must name
    # (review round: a paused 8-of-10 chains arm hid a ticking 3-of-5 soil
    # arm from the ledger, the status and the war room).
    # (A truce that ends in war this turn counts as ticking — verification
    # round.)
    soonest = (min(running, key=lambda a: (not (a["ticking"] or a["resuming"]),
                                           a["turns_left"],
                                           ARMS.index(a["arm"])))
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
    # reset (drop) on release or a fresh capture. The entry is keyed on the
    # CAPTIVITY — the captor and the turn he was taken — so a man freed and
    # re-taken between two ticks starts a new clock (review round: keyed on
    # the captor alone, a re-capture by the same court inherited the old
    # count and deposed him two turns after the new capture, and the
    # captor's offer cadence — turns 1, 4, 7 — was skipped entirely).
    chains = _chains(world, nation)
    if chains is None:
        clock.pop(ARM_CHAINS, None)
    else:
        entry = clock.get(ARM_CHAINS)
        if (not isinstance(entry, dict)
                or entry.get("captor") != chains["captor"]
                or int(entry.get("captured_turn", chains["captured_turn"]))
                != chains["captured_turn"]):
            entry = {"turns": 0, "since": turn, "captor": chains["captor"],
                     "captured_turn": chains["captured_turn"]}
        entry.setdefault("captured_turn", chains["captured_turn"])
        if chains["at_war_with_captor"]:
            entry["turns"] = int(entry.get("turns", 0)) + 1
            entry["paused"] = False
        else:
            entry["paused"] = True
            # The turns a truce held the clock (verification round): the
            # cause line's "N of them at war with his captor" is true only
            # when the pauses account for the rest of his captivity — a
            # clock that merely STARTED late (a pre-GE-1 save loaded with the
            # Emperor already a prisoner) never paused.
            entry["paused_turns"] = int(entry.get("paused_turns", 0) or 0) + 1
        clock[ARM_CHAINS] = entry

    # The soil or the sword: tick while at war with anyone; PAUSE while the
    # only quarrels stand in a truce; reset at a peace with everyone or when
    # both disjuncts lift.
    soil = _soil_or_sword(world, nation)
    at_war = _at_war_with_anyone(world, nation)
    if soil is None or (not at_war and not _in_truce_with_anyone(world, nation)):
        clock.pop(ARM_SOIL, None)
    else:
        entry = clock.get(ARM_SOIL)
        if not isinstance(entry, dict):
            entry = {"turns": 0, "since": turn}
        if at_war:
            entry["turns"] = int(entry.get("turns", 0)) + 1
            entry["paused"] = False
        else:
            entry["paused"] = True
        entry["realm"] = bool(soil["realm"])
        entry["sword"] = bool(soil["sword"])
        if entry.get("turns", 0) <= 0 and not at_war:
            # A truce that began before the clock ever ticked keeps no
            # entry: nothing is counted, nothing to pause.
            clock.pop(ARM_SOIL, None)
        else:
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
    truce_ends = str(view.get("truce_ends") or "")
    if view["arm"] == ARM_CHAINS:
        if not view["ticking"]:
            from backend.game_logic.formations import formed_display_name
            captor = formed_display_name(world, str(view["detail"].get("captor") or ""))
            # The truce with his captor runs out THIS turn (verification
            # round): into war — the clock counts this turn — or into peace,
            # which frees him.
            if view.get("resuming"):
                if turns <= 0:
                    return (f"{title}: the truce with {captor} ends this turn "
                            f"and the war resumes — the regency falls after "
                            f"{plural(grace, 'turn')} of captivity at war "
                            f"unless he is freed: {exits}.")
                return (f"{title}: {turns} of {grace} — the truce with {captor} "
                        f"ends this turn and the war resumes; the regency "
                        f"falls at the end of turn "
                        f"{view['falls_at_end_of_turn']} "
                        f"({_remain(view['turns_left'])}) unless he is "
                        f"freed: {exits}.")
            if truce_ends == "peace":
                return (f"{title}: {turns} of {grace} — the truce with {captor} "
                        f"ends in peace this turn, and the peace frees him.")
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
        if view.get("paused_by") == "truce":
            # A truce is not a peace (the round's own rule) — never "at
            # peace" while one stands, whatever the count (verification
            # round). And the count is stated in turns OF WAR still to come,
            # the unit the ticking sentence uses ("2 turns remain").
            if view.get("resuming"):
                if turns <= 0:
                    return (f"{title}: the truce ends this turn and the war "
                            f"resumes — the Empire falls after "
                            f"{plural(grace, 'turn')} of war unless we "
                            f"{exits}.")
                return (f"{title}: {turns} of {grace} — the truce ends this "
                        f"turn and the war resumes; the Empire falls at the "
                        f"end of turn {view['falls_at_end_of_turn']} "
                        f"({_remain(view['turns_left'])}) unless we {exits}.")
            if turns > 0:
                return (f"{title}: {turns} of {grace} — the clock stands still "
                        f"while the truce holds; if the war resumes, the "
                        f"Empire falls after "
                        f"{plural(view['turns_left'], 'more turn')} of war "
                        f"unless we {exits}.")
            return (f"{title}: no clock runs while the truce holds — if the "
                    f"war resumes, one starts: the Empire falls after "
                    f"{plural(grace, 'turn')} of war unless we {exits}.")
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
    view = state["soonest"]
    if view is None:
        # No clock has counted yet: name a TICKING arm first (the one about
        # to start), then any.
        held = [state["arms"][a] for a in ARMS if a in state["arms"]]
        view = next((v for v in held if v["ticking"] or v.get("resuming")),
                    held[0])
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
    # (A truce that ends in war this turn is a ticking clock — verification
    # round: the pause read "warning" with no date on the very turn the
    # truce collapsed and the Empire fell.)
    critical = bool(soonest and (soonest["ticking"] or soonest.get("resuming"))
                    and soonest["turns_left"] <= 2) or (
        collapse_state is not None
        and collapse_state["tier"] == collapse.TIER_FALLEN)
    title = (soonest or next((v for v in arms
                              if v["ticking"] or v.get("resuming")),
                             arms[0]))["title"]
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
                 "paused_by": str(v.get("paused_by") or ""),
                 "truce_ends": str(v.get("truce_ends") or ""),
                 "resuming": bool(v.get("resuming")),
                 "falls_at_end_of_turn": (int(v["falls_at_end_of_turn"])
                                          if v["falls_at_end_of_turn"] is not None
                                          else None),
                 "exits": list(v["exits"])}
                for v in arms
            ],
        },
    }
