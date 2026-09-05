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
    # FA-25 (slice 11): `bombardment` was absent here, so a shelling that
    # took 28,800 men never reached Le Moniteur — while
    # `format_event_oneliner` had had a `bombardment` arm all along.
    "battle", "bombardment", "region_captured", "expedition_landed",
    "expedition_intercepted", "expedition_turned_back", "fleet_action",
    "trafalgar", "blockade_begins", "blockade_broken", "cs_tier_shift",
}
_COURT_TYPES = {
    "war_declaration", "diplomatic_war_declared", "peace_ratified",
    "third_party_peace", "diplomatic_treaty_signed", "nation_formed",
    "nation_eliminated", "incoming_ultimatum", "coalition_formed",
    # FA-N74 (slice 11): `vassal_rebellion` was whitelisted here and had no
    # producer either — the same inert shape as the campaign log's entry.
    # `vassal_broke_free` is the type that is now written, and
    # `format_event_oneliner` has an arm for it, so Le Moniteur prints a
    # sentence rather than the raw `Event: vassal_broke_free` fallback.
    # (`vassal_created` is ALSO producer-less; it is out of this slice's
    # scope and is left alone rather than quietly retired.)
    "coalition_dissolved", "vassal_created", "vassal_broke_free",
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


# WO-43 (WO slice 12): the special-edition captions RANKED BY GRAVITY.
# Every arm of `_special_reason` used to return on the first matching
# event inside `for event in turn_events`, so the masthead was decided by
# which catastrophe was appended to the log first — measured: an enemy
# capital stormed by France preempted THE EMPEROR TAKEN on a turn that
# carried both, while the dispatch ranks the same two events 101 > 100.
# The weights mirror the dispatch's own band order (sovereign > our
# capital > a crown struck > a nation proclaimed > a crowned head taken >
# the great powers at war / at peace > a capital stormed > a marshal
# lost). The slice-4 `_player_sovereign_taken` guard inside the capital
# arm is retired by construction — it existed only because the arms were
# ranked by log order.
_SPECIAL_WEIGHTS = {
    "THE EMPEROR TAKEN": 100,
    "THE CAPITAL HAS FALLEN": 95,
    "a crown struck from the map": 90,
    "a nation proclaimed": 85,
    "a crowned head taken": 80,
    "war between the great powers": 70,
    "peace between the great powers": 65,
    "a capital stormed": 60,
    "a marshal of France lost": 50,
}


def _special_reason(world, turn_events: List[Dict]) -> Optional[str]:
    """A forced special edition's cause among THIS turn's visible
    events, or None — the GRAVEST of them (WO-43), never merely the
    first logged. The detector runs per-turn at publish time — never a
    later scan over the evictable log (the IGR-B trap)."""
    candidates = _special_candidates(world, turn_events)
    if not candidates:
        return None
    return max(candidates, key=lambda c: c[0])[1]


def _special_candidates(world, turn_events: List[Dict]):
    """Every special-edition cause among `turn_events`, as
    `(weight, reason, key)` triples — `key` identifies the EVENT the
    caption is about (a region, a court pair, a marshal), so the
    publisher can tell "the same event again" from "another one".
    Pure; `_special_reason` reads the heaviest."""
    player = getattr(world, "player_nation", "France")
    found = []

    def _add(reason: str, key: str) -> None:
        found.append((_SPECIAL_WEIGHTS[reason], reason, f"{reason}|{key}"))

    for event in turn_events:
        etype = str(event.get("type", ""))
        if etype == "nation_eliminated":
            _add("a crown struck from the map",
                 str(event.get("nation") or event.get("eliminated") or ""))
        if etype == "nation_formed":
            _add("a nation proclaimed",
                 str(event.get("nation") or event.get("formed") or ""))
        if etype in ("war_declaration", "diplomatic_war_declared"):
            aggressor = str(event.get("aggressor")
                            or event.get("nation") or "")
            target = str(event.get("target") or "")
            if _is_great_power(world, aggressor) \
                    and _is_great_power(world, target):
                _add("war between the great powers",
                     "|".join(sorted((aggressor, target))))
        if etype in ("peace_ratified", "third_party_peace",
                     "diplomatic_treaty_signed"):
            parties = [str(event.get(k) or "") for k in
                       ("proposer", "target", "nation", "with")]
            if sum(1 for p in parties if _is_great_power(world, p)) >= 2:
                _add("peace between the great powers",
                     "|".join(sorted(p for p in parties if p)))
        if etype == "region_captured":
            # Review round [17]: every production producer stamps
            # `captured_from` (capture_executor, movement_executor, the
            # AI capture arms) — the older keys stay as fallbacks only.
            prev = str(event.get("captured_from")
                       or event.get("previous_controller")
                       or event.get("old_controller") or "")
            region = str(event.get("region") or "")
            # Aug 30, 2026 review: "the capital of whoever held it" misses the
            # case slice 4's own review widened the DISPATCH for — an ALLY
            # holding a liberated Paris loses it, so `prev` is Bavaria and
            # `get_nation_capital("Bavaria")` is Munich. The dispatch then runs
            # its highest ceremony ("PARIS HAS FALLEN", weight 100) while Le
            # Moniteur, the paper of record, printed nothing about it at all.
            # The player's own capital falling is a capital falling whoever was
            # standing in it — provided it fell to someone who is not us.
            _taker = str(event.get("captured_by") or event.get("captor") or "")
            _taker_is_ours = bool(_taker) and (
                _taker == player
                or (hasattr(world, "are_allies")
                    and world.are_allies(player, _taker))
                or _taker in (getattr(world, "vassals", {}) or {}))
            _player_capital = world.get_nation_capital(player)
            _is_our_capital_lost = bool(
                region and _player_capital and region == _player_capital
                and not _taker_is_ours)
            if region and (_is_our_capital_lost
                           or (prev
                               and world.get_nation_capital(prev) == region)):
                # WO-D6 (slice 4): Le Moniteur is OUR paper. When the
                # stormed capital is the player's own, the caption was
                # still the victor's phrasing - the player read the
                # fall of Paris as somebody else's good news. Caps
                # mirror the sovereign arm below: our own catastrophe
                # shouts, every other court's is a lowercase noun
                # phrase.
                if prev == player or _is_our_capital_lost:
                    # WO-43: no sovereign guard needed here any more —
                    # THE EMPEROR TAKEN outranks this caption by WEIGHT,
                    # whatever the log order (the slice-4 pins hold).
                    _add("THE CAPITAL HAS FALLEN", region)
                else:
                    _add("a capital stormed", region)
        if etype == "marshal_captured" and event.get("sovereign"):
            # NP-4 (NAPOLEON_SPEC §9): the Eagle in Chains outranks every
            # other cause on this page — by weight now, and the sovereign's
            # capture never also counts as "one more marshal" below.
            if str(event.get("nation") or "") == player:
                _add("THE EMPEROR TAKEN", str(event.get("marshal") or ""))
                continue
            if str(event.get("captor") or "") == player:
                _add("a crowned head taken", str(event.get("marshal") or ""))
                continue
        if etype in ("marshal_captured", "last_stand", "marshal_destroyed"):
            if str(event.get("nation") or "") == player:
                _add("a marshal of France lost",
                     str(event.get("marshal") or ""))
    return found


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
    # just-played turn.
    #
    # WO-44 (WO slice 12): the floor used to be clamped above the last
    # issue's turn — `max(last_turn + 1, turn - 1)` — so whenever ANY issue
    # had published on the immediately preceding tick, the just-played
    # turn's events were excluded entirely: measured, with the last issue
    # at turn 11 and Paris falling on turn 11, no paper at all. The clamp
    # existed so a TAIL-stamped special (a congress peace, a proclamation,
    # stamped with the post-increment turn) never forced two editions off
    # one event; that is now done by identity — the previous issue records
    # the KEY of the event its special was about, and the same key seen
    # again from the previous tick is not a second special.
    scan_floor = turn - 1
    turn_events = filter_campaign_log(
        world.get_events_since_turn(scan_floor), world)
    candidates = _special_candidates(world, turn_events)
    if issues and last_turn == turn - 1:
        _seen = str(issues[-1].get("special_key") or "")
        if _seen:
            candidates = [c for c in candidates if c[2] != _seen]
    special = max(candidates, key=lambda c: c[0])[1] if candidates else None
    special_key = (max(candidates, key=lambda c: c[0])[2]
                   if candidates else "")
    due = (turn - last_turn) >= ISSUE_INTERVAL if issues \
        else turn >= ISSUE_INTERVAL
    if not special and not due:
        return None

    issue = compose_issue(world, last_turn, special,
                          previous_issue=issues[-1] if issues else None)
    # WO-44: the event this special was about, so the next tick can tell
    # the same tail-stamped event from a new one (older issues lack the
    # key and are treated as "nothing to dedupe against").
    issue["special_key"] = special_key
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
