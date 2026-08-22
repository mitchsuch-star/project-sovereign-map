"""HC-G "Le Moniteur" (gate §7a) — the deterministic Gazette.

The Dispatch is the STAFF BRIEFING (this turn, actionable). The Gazette
is the PERIODICAL: retrospective, published every ISSUE_INTERVAL turns
(plus forced special editions), the continent's story told as news, and
— the half the Dispatch structurally cannot do — a browsable BACK-ISSUE
ARCHIVE. Zero LLM (the monetization ruling's spine); an optional LLM
polish pass is a LATER slice behind BYOK, never required.

Eviction-proof by construction: issues are COMPOSED at generation time
and STORED in the serialized `world.gazette_issues` (cap MAX_ISSUES,
oldest evicted) — never recomposed from the 500-capped event log later
(the IGR-B trap, named at the gate). Fog-honest by construction: the
composition reads only `filter_campaign_log`'s output — the exact rows
the campaign-log screen shows the player.

GR6/GR5: display-only; no mechanic reads an issue; the press is
player-facing color. Dormancy: no calendar anchor (`world.start_date`
empty — the legacy fixture world) → no gazette, byte-identically.
"""

from typing import Dict, List, Optional

from backend.campaign_log import filter_campaign_log, format_event_oneliner

ISSUE_INTERVAL = 5      # blessed, in-band — an issue every 5 turns
MAX_ISSUES = 20         # blessed, in-band — the archive's depth

# Event types each section collects. The composition NEVER reads raw
# world state for its rows — only already-fog-filtered events — so a
# fog-hidden battle can never appear in print.
_WAR_TYPES = {
    "battle", "region_captured", "expedition_landed",
    "expedition_intercepted", "expedition_turned_back", "fleet_action",
    "trafalgar", "blockade_begins", "blockade_broken", "cs_tier_shift",
}
_COURT_TYPES = {
    "war_declaration", "diplomatic_war_declared", "peace_ratified",
    "third_party_peace", "diplomatic_treaty_signed", "nation_formed",
    "nation_eliminated", "incoming_ultimatum", "coalition_formed",
    "coalition_dissolved", "vassal_created", "vassal_rebellion",
}
_ARMY_TYPES = {
    "glory_crowned", "glory_crown_lost", "dotation_granted",
    "estate_confiscated", "marshal_captured", "last_stand",
    "marshal_destroyed",
    "marshal_petition",
}

_SECTION_CAP = 8  # rows per section — a paper, not a ledger dump


def _is_great_power(world, nation: str) -> bool:
    """The Gazette's own great-power predicate (gate §7a): the authored
    power tier where one exists, the canonical five as fallback."""
    if not nation:
        return False
    tier = ""
    get_tier = getattr(world, "get_power_tier", None)
    if callable(get_tier):
        try:
            tier = str(get_tier(nation) or "")
        except Exception:
            tier = ""
    if tier:
        return tier == "major"
    return nation in ("France", "Britain", "Russia", "Austria", "Prussia")


def _player_sovereign_taken(world, turn_events: List[Dict]) -> bool:
    """NP-4, asked of a whole turn: is the player's own sovereign among
    this turn's visible events?

    `_special_reason` returns on the first MATCHING EVENT, not in source
    order, so an arm's position in the file does not rank it — the log
    does. Measured: `_special_reason(w, [paris_falls, emperor_taken])`
    answered with the capital. The dispatch ranks these correctly by
    weight (`sovereign_captured` 101 > `capital_lost` 100); the Gazette
    needs this to agree with it.
    """
    player = getattr(world, "player_nation", "France")
    return any(
        str(e.get("type", "")) == "marshal_captured"
        and e.get("sovereign")
        and str(e.get("nation") or "") == player
        for e in turn_events
    )


def _special_reason(world, turn_events: List[Dict]) -> Optional[str]:
    """A forced special edition's cause among THIS turn's visible
    events, or None. The detector runs per-turn at publish time — never
    a later scan over the evictable log (the IGR-B trap)."""
    player = getattr(world, "player_nation", "France")
    for event in turn_events:
        etype = str(event.get("type", ""))
        if etype == "nation_eliminated":
            return "a crown struck from the map"
        if etype == "nation_formed":
            return "a nation proclaimed"
        if etype in ("war_declaration", "diplomatic_war_declared"):
            aggressor = str(event.get("aggressor")
                            or event.get("nation") or "")
            target = str(event.get("target") or "")
            if _is_great_power(world, aggressor) \
                    and _is_great_power(world, target):
                return "war between the great powers"
        if etype in ("peace_ratified", "third_party_peace",
                     "diplomatic_treaty_signed"):
            parties = [str(event.get(k) or "") for k in
                       ("proposer", "target", "nation", "with")]
            if sum(1 for p in parties if _is_great_power(world, p)) >= 2:
                return "peace between the great powers"
        if etype == "region_captured":
            # Review round [17]: every production producer stamps
            # `captured_from` (capture_executor, movement_executor, the
            # AI capture arms) — the older keys stay as fallbacks only.
            prev = str(event.get("captured_from")
                       or event.get("previous_controller")
                       or event.get("old_controller") or "")
            region = str(event.get("region") or "")
            if prev and region \
                    and world.get_nation_capital(prev) == region:
                # WO-D6 (slice 4): Le Moniteur is OUR paper. When the
                # stormed capital is the player's own, the caption was
                # still the victor's phrasing - the player read the
                # fall of Paris as somebody else's good news. Caps
                # mirror the sovereign arm below: our own catastrophe
                # shouts, every other court's is a lowercase noun
                # phrase.
                if prev == player:
                    # ...but never above the Emperor himself. See
                    # `_player_sovereign_taken`: the arms are ranked by
                    # LOG ORDER, so without this the fall of Paris
                    # preempts "THE EMPEROR TAKEN" whenever it happens
                    # to be logged first, and the paper contradicts the
                    # dispatch that ranks the same two events 101 > 100.
                    if _player_sovereign_taken(world, turn_events):
                        # RETURN, never `continue`. The first cut deferred
                        # to "whatever matches next", and because the arms
                        # are ranked by log order that next match is often
                        # LOWER than both: measured, a turn carrying Paris
                        # + a marshal + the Emperor captioned itself "a
                        # marshal of France lost". `_player_sovereign_taken`
                        # has already proved the sovereign event is in this
                        # turn's visible set, so naming its caption here is
                        # both correct and order-independent.
                        return "THE EMPEROR TAKEN"
                    return "THE CAPITAL HAS FALLEN"
                return "a capital stormed"
        if etype == "marshal_captured" and event.get("sovereign"):
            # NP-4 (NAPOLEON_SPEC §9): the Eagle in Chains outranks every
            # other cause on this page — checked before the generic
            # marshal-lost arm so the sovereign's capture never prints as
            # one more marshal.
            if str(event.get("nation") or "") == player:
                return "THE EMPEROR TAKEN"
            if str(event.get("captor") or "") == player:
                return "a crowned head taken"
        if etype in ("marshal_captured", "last_stand", "marshal_destroyed"):
            if str(event.get("nation") or "") == player:
                return "a marshal of France lost"
    return None


def _press_lead(world, war_rows: List[Dict]) -> str:
    """The front-page line — the period press's register: triumphalist
    on French victories, delicate on French reverses, dry otherwise.
    Deterministic; composed from the section's own rows."""
    player = getattr(world, "player_nation", "France")
    triumph = None
    reverse = None
    for event in war_rows:
        if str(event.get("type", "")) != "battle":
            continue
        outcome = str(event.get("outcome", ""))
        attacker_nation = str(event.get("attacker_nation") or "")
        defender_nation = str(event.get("defender_nation") or "")
        # Review round [10/19]: the paper claims a triumph or a reverse
        # ONLY for a battle France actually fought — a fog-visible
        # third-party field is news for the sections, never the lead.
        if player not in (attacker_nation, defender_nation):
            continue
        won = ("victory" in outcome
               and ((attacker_nation == player
                     and "attacker" in outcome)
                    or (defender_nation == player
                        and "defender" in outcome)))
        lost = ("victory" in outcome and not won)
        if won and triumph is None:
            triumph = event
        elif lost and reverse is None:
            reverse = event
    if triumph is not None:
        location = str(triumph.get("location") or "the field")
        # NP-5 (NAPOLEON_SPEC §9): the standing lead credits "the
        # Emperor's genius" by convention — when the sovereign PERSONALLY
        # led the winning side, the paper says so as fact.
        _outcome = str(triumph.get("outcome", ""))
        _lead_name = str(triumph.get(
            "attacker" if "attacker" in _outcome else "defender") or "")
        _lead = getattr(world, "marshals", {}).get(_lead_name)
        if _lead is not None and getattr(_lead, "is_sovereign", False):
            return (f"VICTOIRE! The Emperor himself carries the day at "
                    f"{location} — France has seen his genius with her "
                    f"own eyes.")
        return (f"VICTOIRE! The eagles of France carry the day at "
                f"{location} — the Emperor's genius shines upon the army.")
    if reverse is not None:
        location = str(reverse.get("location") or "the frontier")
        return (f"From {location}, the army executes a manoeuvre of "
                f"the greatest delicacy; the situation develops.")
    if war_rows:
        return "The armies of Europe are in motion; the capital watches."
    return "The continent holds its breath; commerce and the salons go on."


def _bourse_line(world) -> str:
    """One line of treasury-and-trade chatter — ledger-derived facts in
    the press's voice, never a recomputed net (the CA9-N11 caveat:
    counts and standing facts only, no projection)."""
    player = getattr(world, "player_nation", "France")
    treasury = int(getattr(world, "nation_gold", {}).get(player, 0))
    blockaded = False
    try:
        from backend.game_logic.naval import is_blockaded
        blockaded = is_blockaded(world, player)
    except Exception:
        blockaded = False
    if blockaded:
        return (f"THE BOURSE — The English squadrons press our trade; "
                f"the Treasury stands at {treasury:,} francs and the "
                f"merchants grumble.")
    return (f"THE BOURSE — The Treasury stands at {treasury:,} francs; "
            f"the funds are steady.")


def compose_issue(world, since_turn: int,
                  special_reason: Optional[str] = None,
                  previous_issue: Optional[Dict] = None) -> Dict:
    """Compose one issue from the fog-filtered events stamped
    `since_turn` ONWARD (inclusive). Pure read — the caller stores it.

    Review round [18]: events are stamped with the PRE-increment turn,
    so the campaign turn played AFTER the last publication carries the
    SAME stamp as that issue's advance-tail rows. The window therefore
    re-opens AT the last issue's turn (inclusive) and rows already
    printed in `previous_issue` are dropped textually — no fifth turn
    of the campaign is ever lost, and no tail row prints twice.
    """
    events = filter_campaign_log(
        world.get_events_since_turn(max(1, int(since_turn))), world)
    war_rows = [e for e in events if str(e.get("type", "")) in _WAR_TYPES]
    court_rows = [e for e in events
                  if str(e.get("type", "")) in _COURT_TYPES]
    army_rows = [e for e in events if str(e.get("type", "")) in _ARMY_TYPES]

    # Review round [1/4]: the number continues from the last ISSUE, not
    # from the eviction-capped archive length — № 21 is followed by
    # № 22, not by № 21 forever.
    if previous_issue:
        number = int(previous_issue.get("number", 0)) + 1
    else:
        number = len(getattr(world, "gazette_issues", []) or []) + 1
    label = ""
    get_label = getattr(world, "get_calendar_label", None)
    if callable(get_label):
        label = str(get_label() or "")
    dateline = label or f"Turn {int(world.current_turn)}"

    def _section(rows: List[Dict], key: str) -> List[str]:
        lines = [format_event_oneliner(e) for e in rows]
        if previous_issue:
            already = set(previous_issue.get(key) or [])
            lines = [ln for ln in lines if ln not in already]
        return lines[-_SECTION_CAP:]

    issue = {
        "number": int(number),
        "turn": int(world.current_turn),
        "dateline": dateline,
        "masthead": f"LE MONITEUR — Paris, {dateline}",
        "special": bool(special_reason),
        "special_reason": str(special_reason or ""),
        "lead": _press_lead(world, war_rows),
        # The section rows ARE the campaign log's own lines (fog-honest,
        # R7-humanized by the shared formatter) — the paper never claims
        # a battle the log cannot show.
        "war": _section(war_rows, "war"),
        "courts": _section(court_rows, "courts"),
        "army": _section(army_rows, "army"),
        "bourse": _bourse_line(world),
    }
    return issue


def process_gazette(world) -> Optional[Dict]:
    """The once-per-turn publication check. Sited in the advance-turn
    tail AFTER the fog recompute (the filter must read the NEW turn's
    visibility). Returns the published issue or None.

    Cadence: a forced special on the gate's named moments, else an
    issue every ISSUE_INTERVAL turns since the last. One issue max per
    turn (a special resets the clock by BEING the last issue). Dormant
    without a calendar anchor — the legacy world never prints."""
    if not str(getattr(world, "start_date", "") or ""):
        return None
    issues = getattr(world, "gazette_issues", None)
    if issues is None:
        return None
    turn = int(world.current_turn)
    last_turn = int(issues[-1]["turn"]) if issues else 0
    if last_turn >= turn:
        return None  # one issue max per turn

    # Review round [6/11/16/22]: the campaign's own events (player phase
    # + enemy phase) are stamped with the PRE-increment turn, and this
    # check runs post-increment — a detector scanning only the NEW stamp
    # would never see a stormed capital. The scan floor is therefore the
    # just-played turn, clamped above the last issue's turn so a
    # tail-stamped special (a congress peace, a proclamation) never
    # forces two editions off one event.
    scan_floor = max(last_turn + 1, turn - 1)
    turn_events = filter_campaign_log(
        world.get_events_since_turn(scan_floor), world)
    special = _special_reason(world, turn_events)
    due = (turn - last_turn) >= ISSUE_INTERVAL if issues \
        else turn >= ISSUE_INTERVAL
    if not special and not due:
        return None

    issue = compose_issue(world, last_turn, special,
                          previous_issue=issues[-1] if issues else None)
    issues.append(issue)
    del issues[:-MAX_ISSUES]

    # The one-line notice on the existing rail — no popup class, no
    # queue slot, never a modal, never blocks the turn.
    try:
        from backend.notifications import (
            GAZETTE_PUBLISHED, NotificationPriority, create_notification,
        )
        world.notifications.add(create_notification(
            notification_type=GAZETTE_PUBLISHED,
            priority=NotificationPriority.NORMAL,
            title="The Moniteur is out",
            message=(f"№ {issue['number']} — {issue['dateline']}."
                     + (f" Special edition: {issue['special_reason']}."
                        if issue["special"] else "")),
            turn_created=turn,
        ))
    except Exception:
        pass  # the paper still publishes if the rail is absent (tests)
    return issue
