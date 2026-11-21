"""Row PW "Plain Words" (November 18, 2026 — the first playtest): WHILE YOU WAITED.

The player, of thirteen turns: "it seemd liek things randfomly flipped back to
enemy control. what happens on eenmy turns is opaque and ocnfusing." His own
record shows what happened — Carniola taken on turn 3, walked back into by
Austria on turn 5 because nothing stood there, taken again on turn 9, lost on
turn 12 when Buxhowden beat Ney on it — and the report of each of those turns
was a list of every court's every move in the order it was made, a province
changing hands one line among forty. Nothing said FIRST what changed for him.

This module is that first word. `snapshot(world)` is read when End Turn is
pressed; `digest(...)` when the turn has turned, from the difference:

* `lost` / `gained` — provinces that were his and are not, or are his and
  were not, each with its CAUSE in plain words ("Archduke Charles marched in;
  nobody was holding it", "Buxhowden beat Ney there", "the garrison was
  stormed", "the siege ended");
* `friends_lost` / `friends_gained` — the same for a court allied to him;
* `battles` — the fights his own corps were in, who won, the losses;
* `beside` — enemy corps we can see that moved and now stand on or beside
  his ground or his corps.

PURE: it reads the world and writes nothing. FOG (R5): a province's holder is
public (the map draws it); a battle his own corps fought is his to know; an
enemy marshal is NAMED only where the player sees him now
(`get_visible_enemies_in_region`) — otherwise it is "an Austrian army". ints
only (Golden Rule 2). One region scan when End Turn is pressed and one when
the turn has turned — never per response (Golden Rule 8).
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from backend.display_names import humanize_entity_name, nation_adjective
from backend.errors import report

# How many rows of a kind the digest carries (the rest are counted, not listed).
MAX_ROWS = 6


def the_turn_is_summed_up() -> bool:
    """Row PW seam (one line to reverse). Down (False): no digest is built and
    the enemy-phase report opens on its list of courts, as before."""
    return True


def a_loss_says_if_it_was_foreseen() -> bool:
    """Row IC seam (one line to reverse): the snapshot keeps the provinces in
    danger and the enemies in sight as End Turn is pressed, and each province
    lost by arms says "You were warned before the turn ended." or "The enemy
    who took it was out of your sight." Down (False): no `danger` / `seen` in
    the snapshot, no `foreseen` on a row, the lines as row PW wrote them."""
    return True


# What a lost province's row says of the warning, by its `foreseen` key.
FORESEEN_WORDS = {
    "warned": "You were warned before the turn ended.",
    "unseen": "The enemy who took it was out of your sight.",
}
# The causes that are a loss BY ARMS (a treaty's hand-over is foreseen by its
# signer, and a change with no cause read is tagged with nothing).
_BY_ARMS = frozenset({"battle", "stormed", "siege", "walked_in", "empty"})


def _court(world, nation: str) -> str:
    try:
        from backend.game_logic.formations import formed_display_name
        return formed_display_name(world, nation)
    except Exception as exc:
        report(exc, "while_you_waited._court: formed_display_name")
        return str(nation)


def _standing(world, nation: str) -> str:
    """'player' / 'friend' / 'foe' / 'neutral' — `main.battle_standing`'s rule
    (diplomacy has no fog)."""
    nation = str(nation or "")
    player = str(getattr(world, "player_nation", "") or "")
    if not nation:
        return ""
    if nation == player:
        return "player"
    try:
        state = world.get_diplomatic_state(player, nation)
    except Exception as exc:
        report(exc, "while_you_waited._standing: get_diplomatic_state")
        return "neutral"
    if state == "WAR":
        return "foe"
    if state in ("ALLIANCE", "DEFENSIVE_ALLIANCE", "VASSAL"):
        return "friend"
    return "neutral"


def before(world, resuming: bool = False) -> Dict[str, Any]:
    """The digest's "before", read as End Turn is pressed (`turn_manager.
    end_turn`'s first step). {} for a RESUMED close — a turn whose advance
    failed and is being finished has no honest "before" to compare with."""
    return {} if resuming else snapshot(world)


def attach(result: Dict[str, Any], world, before_the_turn: Dict[str, Any],
           enemy_phase=None, tactical_events=None) -> None:
    """`end_turn`'s last step: what changed for the PLAYER while the turn
    turned — the provinces lost and won with their causes, his own battles,
    the enemies now beside him — on the result as `while_you_waited`. A
    reading; nothing is written to the world."""
    if not before_the_turn:
        return
    told = digest(world, before_the_turn, enemy_phase, tactical_events)
    if told:
        result["while_you_waited"] = told


def snapshot(world) -> Dict[str, Any]:
    """The board as End Turn is pressed: who holds each province, which corps
    stand where, the garrisons on the player's own ground. {} with the seam
    down."""
    if not the_turn_is_summed_up():
        return {}
    try:
        player = world.player_nation
        regions: Dict[str, str] = {}
        garrisons: Dict[str, int] = {}
        for name, region in world.regions.items():
            holder = str(getattr(region, "controller", "") or "")
            regions[name] = holder
            if holder == player:
                garrisons[name] = int(getattr(region, "garrison_strength", 0) or 0)
        corps: Dict[str, List[List[str]]] = {}
        places: Dict[str, str] = {}
        for m in world.marshals.values():
            if int(getattr(m, "strength", 0) or 0) <= 0 or getattr(m, "captured_by", ""):
                continue
            corps.setdefault(str(m.location), []).append([m.name, str(m.nation)])
            places[m.name] = str(m.location)
        # The pairs at war or in a truce as End Turn is pressed (the review,
        # PW-R6): a province that changes hands between two courts that WERE
        # at war and no longer are was moved by their peace.
        wars = sorted(str(key) for key, state in (getattr(world, "diplomatic_states", {}) or {}).items()
                      if state in ("WAR", "ARMISTICE"))
        out = {"turn": int(world.current_turn), "regions": regions, "garrisons": garrisons,
               "corps": corps, "places": places, "wars": wars}
        out.update(_what_was_foreseen(world))
        return out
    except Exception as exc:
        report(exc, "while_you_waited.snapshot")
        return {}


def _what_was_foreseen(world) -> Dict[str, Any]:
    """Row IC: what the player had been TOLD as End Turn was pressed — the
    provinces the desk listed as in danger (`threats.in_danger`: an enemy in
    sight one march from a province nothing held), and every FOREIGN corps in
    sight at all — at war with us or not (the review, IC-R2: a court at peace
    that stood in plain sight, declared war in the night and walked in was
    said to have been "out of your sight"). {} with the seam down."""
    if not a_loss_says_if_it_was_foreseen():
        return {}
    try:
        from backend.game_logic import intel_surfaces, threats
        player = world.player_nation
        return {"danger": sorted(str(row["region"]) for row in threats.in_danger(world, player)),
                "seen": sorted(str(m.name) for m in world.marshals.values()
                               if intel_surfaces.in_sight(world, player, m))}
    except Exception as exc:
        report(exc, "while_you_waited._what_was_foreseen")
        return {}


def _events(enemy_phase, tactical_events) -> List[Dict[str, Any]]:
    """Every event of the turn, flat: the enemy phase's (each stamped with the
    court that acted) and the turn's own (`get_last_tactical_events`)."""
    out: List[Dict[str, Any]] = []
    for nation, data in ((enemy_phase or {}).get("nations") or {}).items():
        for action in (data or {}).get("actions") or []:
            if not isinstance(action, dict):
                continue
            for event in action.get("events") or []:
                if isinstance(event, dict):
                    row = dict(event)
                    row.setdefault("_court", nation)
                    out.append(row)
    for event in tactical_events or []:
        if isinstance(event, dict):
            out.append(dict(event))
    return out


def _seen_here(world, region_name: str) -> set:
    """The enemy marshals the PLAYER sees in a province right now (names)."""
    try:
        rows = world.get_visible_enemies_in_region(region_name, world.player_nation)
    except Exception as exc:
        report(exc, "while_you_waited._seen_here: get_visible_enemies_in_region")
        return set()
    return {str(r.get("name") if isinstance(r, dict) else getattr(r, "name", "")) for r in rows}


def _named(world, marshal_key: str, nation: str, region_name: str, *, ours: bool) -> str:
    """A marshal's name where the player may know it (his own or a friend's
    corps, or an enemy he sees there now) — else the court's army, said as a
    person would say it: "a British army", "an Austrian army" (the one table
    of adjectives, `display_names.nation_adjective`)."""
    key = str(marshal_key or "")
    if key and (ours or key in _seen_here(world, region_name)):
        return humanize_entity_name(key)
    if nation:
        whose = nation_adjective(nation) or _court(world, nation)
        article = "an" if whose[:1].lower() in "aeiou" else "a"
        return f"{article} {whose} army"
    return "an army"


def _cause(world, before: Dict[str, Any], region: str, old: str, new: str,
           events: Iterable[Dict[str, Any]]) -> Dict[str, str]:
    """Why `region` changed hands: {'how', 'by', 'words'} — read off the
    turn's own events, in the order of what settles most: a battle fought for
    it, a garrison stormed, a siege ended, a march into it."""
    battle = stormed = siege = walked = None
    for event in events:
        kind = str(event.get("type") or "")
        if kind == "battle" and (str(event.get("region_name") or "") == region
                                 or str(event.get("location") or "") == region
                                 or str(event.get("advanced_to") or "") == region):
            battle = event
        elif kind in ("garrison_destroyed", "garrison_assault") and str(event.get("region") or "") == region:
            stormed = event
        elif kind == "occupation_complete" and str(event.get("region") or "") == region:
            siege = event
        elif kind == "conquest" and str(event.get("region") or "") == region:
            walked = event
        elif kind == "move" and str(event.get("to") or "") == region and event.get("captured_from"):
            walked = event
    taker_ours = _standing(world, new) in ("player", "friend")
    if battle is not None:
        attacker = battle.get("attacker") if isinstance(battle.get("attacker"), dict) else {}
        defender = battle.get("defender") if isinstance(battle.get("defender"), dict) else {}
        winner_key = str(battle.get("victor") or attacker.get("name") or "")
        loser_key = str(defender.get("name") if winner_key == str(attacker.get("name") or "")
                        else attacker.get("name") or "")
        winner_nation = str(battle.get("attacker_nation") if winner_key == str(attacker.get("name") or "")
                            else battle.get("defender_nation") or "")
        loser_nation = str(battle.get("defender_nation") if winner_key == str(attacker.get("name") or "")
                           else battle.get("attacker_nation") or "")
        winner = _named(world, winner_key, winner_nation, region, ours=taker_ours)
        loser = _named(world, loser_key, loser_nation, region,
                       ours=_standing(world, loser_nation) in ("player", "friend"))
        return {"how": "battle", "by": winner, "words": f"{winner} beat {loser} there",
                "taker": winner_key}
    if stormed is not None:
        taker = str(stormed.get("marshal") or stormed.get("attacker") or "")
        by = _named(world, taker, new, region, ours=taker_ours)
        return {"how": "stormed", "by": by, "words": f"{by} stormed the garrison", "taker": taker}
    if siege is not None:
        taker = str(siege.get("marshal") or "")
        by = _named(world, taker, new, region, ours=taker_ours)
        return {"how": "siege", "by": by, "words": f"{by}'s siege ended", "taker": taker}
    # The review (PW-R5): WHO HELD IT is said only of the player's OWN
    # province — his garrison (the snapshot keeps no other court's) and his own
    # side's corps there are his to know. Of an ally's or an enemy's province
    # the digest says who marched in and stops: "nobody was holding it" there
    # was a guess (an ally's detachment read as none), and it turned on corps
    # the player could not see.
    known = old == world.player_nation
    held_by = [name for name, nation in (before.get("corps") or {}).get(region, [])
               if nation == old or _standing(world, nation) in ("player", "friend")] if known else []
    garrison = int((before.get("garrisons") or {}).get(region, 0) or 0) if known else 0
    if walked is not None:
        taker = str(walked.get("marshal") or "")
        by = _named(world, taker, new, region, ours=taker_ours)
        if not known:
            return {"how": "walked_in", "by": by, "words": f"{by} marched in", "taker": taker}
        if not held_by and garrison <= 0:
            return {"how": "walked_in", "by": by, "words": f"{by} marched in; nobody was holding it",
                    "taker": taker}
        if not held_by:
            return {"how": "walked_in", "by": by, "taker": taker,
                    "words": f"{by} marched in; the garrison of {garrison:,} was too small to hold it"}
        return {"how": "walked_in", "by": by, "words": f"{by} marched in", "taker": taker}
    # No fight and no march this turn. The review (PW-R6): "under a treaty" is
    # said only where the two courts WERE at war (or in a truce) as the turn
    # ended and are not now — their peace moved it. Any other change of hands
    # with no event of its own (a revolt, a release, a road this digest does
    # not read) names no cause: a wrong one is worse than none.
    try:
        at_war = bool(old and new and world.is_at_war(old, new))
        was_at_war = bool(old and new and world._make_diplo_key(old, new) in set(before.get("wars") or []))
        in_truce = bool(old and new and world.get_diplomatic_state(old, new) == "ARMISTICE")
    except Exception as exc:
        report(exc, "while_you_waited._cause: the pair's state")
        at_war, was_at_war, in_truce = False, False, False
    if was_at_war and not at_war and not in_truce:
        return {"how": "treaty", "by": "", "words": "handed over under their peace treaty"}
    if at_war and known and not held_by and garrison <= 0:
        return {"how": "empty", "by": "", "words": "nobody was holding it"}
    return {"how": "", "by": "", "words": ""}


def _change_row(world, before, region: str, old: str, new: str, events) -> Dict[str, Any]:
    cause = _cause(world, before, region, old, new, events)
    row = {"region": region, "from": old, "from_shown": _court(world, old) if old else "",
           "to": new, "to_shown": _court(world, new) if new else "",
           "how": cause["how"], "by": cause["by"], "why": cause["words"]}
    if old == world.player_nation:
        row["foreseen"] = _foreseen(before, region, cause)
    return row


def _foreseen(before: Dict[str, Any], region: str, cause: Dict[str, str]) -> str:
    """Row IC: of a province of OURS lost by arms — "warned" (the desk listed
    it as in danger when End Turn was pressed), "unseen" (the corps that took
    it stood in no province we could see), or "" (it was held and threatened
    in plain sight, the taker is not known, the cause was no feat of arms, or
    the snapshot is an older one that kept neither list). The taker's roster
    key never leaves this function: the row's own `by` is already what the
    player may read (`_named`)."""
    if "danger" not in before or cause.get("how") not in _BY_ARMS:
        return ""
    if region in set(before.get("danger") or []):
        return "warned"
    taker = str(cause.get("taker") or "")
    if taker and taker not in set(before.get("seen") or []):
        return "unseen"
    return ""


def _lost_line(row: Dict[str, Any]) -> str:
    line = f"{row['region']} — lost to {row['to_shown'] or 'no one'}."
    if row.get("why"):
        why = str(row["why"])
        line += " " + why[:1].upper() + why[1:] + "."
    said = FORESEEN_WORDS.get(str(row.get("foreseen") or ""))
    if said:
        line += " " + said
    return line


def _gained_line(row: Dict[str, Any], *, ours: bool = True) -> str:
    head = (f"{row['region']} — now yours" if ours
            else f"{row['region']} — now {row['to_shown']}'s")
    if row.get("from_shown"):
        head += f" (was {row['from_shown']}'s)"
    line = head + "."
    if row.get("why"):
        why = str(row["why"])
        line += " " + why[:1].upper() + why[1:] + "."
    return line


def _our_battles(world, events) -> List[Dict[str, Any]]:
    """The fights the player's OWN corps were in this turn."""
    player = world.player_nation
    rows: List[Dict[str, Any]] = []
    for event in events:
        if str(event.get("type") or "") != "battle":
            continue
        a_nation = str(event.get("attacker_nation") or "")
        d_nation = str(event.get("defender_nation") or "")
        if player not in (a_nation, d_nation):
            continue
        attacker = event.get("attacker") if isinstance(event.get("attacker"), dict) else {}
        defender = event.get("defender") if isinstance(event.get("defender"), dict) else {}
        we_attacked = a_nation == player
        ours = attacker if we_attacked else defender
        theirs = defender if we_attacked else attacker
        our_name = humanize_entity_name(str(ours.get("name") or ""))
        his_name = humanize_entity_name(str(theirs.get("name") or ""))
        victor = str(event.get("victor") or "")
        outcome = str(event.get("outcome") or "")
        if outcome == "stalemate" or not victor:
            result = "none"
            said = (f"{our_name} attacked {his_name} — no winner" if we_attacked
                    else f"{his_name} attacked {our_name} — no winner")
        elif victor == str(ours.get("name") or ""):
            result = "won"
            said = (f"{our_name} attacked {his_name} and won" if we_attacked
                    else f"{his_name} attacked {our_name} and was beaten off")
        else:
            result = "lost"
            said = (f"{our_name} attacked {his_name} and was beaten" if we_attacked
                    else f"{his_name} attacked {our_name} and won")
        # A great battle that did not decide the day is not won or lost yet:
        # the day stands open (the tableau's `day`), whatever the clash read.
        tableau = event.get("diorama") if isinstance(event.get("diorama"), dict) else {}
        day = tableau.get("day") if isinstance(tableau.get("day"), dict) else None
        if day is not None and day.get("open"):
            result = "open"
            who = (f"{our_name} attacked {his_name}" if we_attacked
                   else f"{his_name} attacked {our_name}")
            if str(day.get("awaits") or "") != "ours":
                said = f"{who} — no winner yet: the battle goes on"
            elif _lead_takes_no_orders(world, str(day.get("lead") or ours.get("name") or "")):
                # Row IC, Session 2b (IC2B-X17, the desk row's sibling): a
                # lead on his task to prove himself waits for no order — what
                # is still the Emperor's is to send him help.
                said = (f"{who} — no winner yet: {our_name} takes no orders; "
                        f"you can send him help this turn")
            else:
                said = f"{who} — no winner yet: the battle waits for your orders this turn"
        place = str(event.get("location") or event.get("region_name") or "")
        our_loss = int(ours.get("casualties", 0) or 0)
        his_loss = int(theirs.get("casualties", 0) or 0)
        tail = ""
        if result == "open":
            pass
        elif ours.get("forced_retreat"):
            tail = f" {our_name} was driven off."
        elif theirs.get("forced_retreat"):
            tail = f" {his_name} was driven off."
        rows.append({
            "place": place, "ours": our_name, "theirs": his_name, "result": result,
            "our_loss": our_loss, "their_loss": his_loss,
            "line": (f"{place}: {said}. Losses: you {our_loss:,}, him {his_loss:,}." + tail),
        })
    return rows


def _lead_takes_no_orders(world, name: str) -> bool:
    """Row IC, Session 2b: our lead in this battle is on his task to prove
    himself (`trial.on_trial`, the one reader) — he can be given no word of
    the day."""
    try:
        from backend.game_logic import trial as _trial
        getter = getattr(world, "get_marshal", None)
        marshal = getter(name) if callable(getter) and name else None
        return marshal is not None and _trial.on_trial(marshal)
    except Exception as exc:
        report(exc, "while_you_waited._lead_takes_no_orders: trial.on_trial")
        return False


def _now_beside(world, before) -> List[Dict[str, Any]]:
    """Enemy corps the player SEES that moved this turn and now stand on his
    ground, or beside a province or a corps of his."""
    player = world.player_nation
    rows: List[Dict[str, Any]] = []
    try:
        seen = world.get_visible_enemies(player)
    except Exception as exc:
        report(exc, "while_you_waited._now_beside: get_visible_enemies")
        return rows
    our_places = {str(m.location) for m in world.get_player_marshals()
                  if int(getattr(m, "strength", 0) or 0) > 0}
    was = before.get("places") or {}
    for foe in seen:
        here = str(getattr(foe, "location", "") or "")
        if not here or was.get(foe.name) == here or int(getattr(foe, "strength", 0) or 0) <= 0:
            continue
        region = world.get_region(here)
        if region is None:
            continue
        shown = humanize_entity_name(foe.name)
        on_ours = str(getattr(region, "controller", "") or "") == player
        beside = ""
        with_ours = here in our_places
        if not on_ours and not with_ours:
            for name in getattr(region, "adjacent_regions", []) or []:
                neighbour = world.get_region(name)
                if neighbour is not None and str(getattr(neighbour, "controller", "") or "") == player:
                    beside = name
                    break
            if not beside:
                beside = next((name for name in (getattr(region, "adjacent_regions", []) or [])
                               if name in our_places), "")
                if beside:
                    beside = "your corps at " + beside
        if not on_ours and not beside and not with_ours:
            continue
        # (said as where he IS: in a province of ours; in the same province as
        # a corps of ours — "next to your corps there" read oddly for a man
        # standing on the same ground; else beside a province or a corps)
        if with_ours:
            where = f"{shown} is in {here}, where your corps stands"
        elif on_ours:
            where = f"{shown} now stands in {here} — your province"
        else:
            where = f"{shown} moved to {here}, next to {beside}"
        rows.append({"marshal": foe.name, "shown": shown, "at": here, "on_ours": bool(on_ours),
                     "line": where + "."})
    rows.sort(key=lambda r: (0 if r["on_ours"] else 1, r["shown"]))
    return rows


MAX_PLAQUES = 6

_BATTLE_PLAQUE = {"won": "battle won", "lost": "battle lost", "none": "battle — no winner",
                  "open": "battle — no winner yet"}


def _plaques(lost, friends_lost, battles, gained, friends_gained) -> List[Dict[str, str]]:
    """The words the map wears at a province while the enemy's moves are
    played on it (`main.gd::_pw_play_then_report`): rows of {region, text,
    tone} — `tone` "bad" (a province lost), "good" (one gained) or "battle".
    The player's own losses lead; at most MAX_PLAQUES. Built from the
    digest's own rows: it says nothing the report does not."""
    rows: List[Dict[str, str]] = []
    for row in lost:
        rows.append({"region": str(row["region"]), "tone": "bad",
                     "text": f"{row['region']} — lost to {row.get('to_shown') or 'no one'}"})
    for row in friends_lost:
        rows.append({"region": str(row["region"]), "tone": "bad",
                     "text": (f"{row['region']} — {row.get('from_shown') or 'an ally'} lost it to "
                              f"{row.get('to_shown') or 'no one'}")})
    for row in battles:
        place = str(row.get("place") or "")
        if place:
            result = str(row.get("result") or "")
            words = _BATTLE_PLAQUE.get(result, "battle")
            rows.append({"region": place, "tone": {"won": "good", "lost": "bad"}.get(result, "battle"),
                         "text": f"{place} — {words}"})
    for row in gained:
        rows.append({"region": str(row["region"]), "tone": "good", "text": f"{row['region']} — now yours"})
    for row in friends_gained:
        rows.append({"region": str(row["region"]), "tone": "good",
                     "text": f"{row['region']} — now {row.get('to_shown') or 'an ally'}'s"})
    return rows[:MAX_PLAQUES]


def digest(world, before: Optional[Dict[str, Any]], enemy_phase=None,
           tactical_events=None) -> Dict[str, Any]:
    """What changed for the player between `before` (End Turn pressed) and
    now. {} when there is no snapshot or the seam is down; `quiet: True` when
    nothing of his changed (the report then says so in one line). (Row IC,
    Session 2b: the `own_way` rows — a French marshal moved by the enemy's
    decision logic — went with that engine; a man on his task to prove
    himself reports in the strategic rows.)"""
    if not before or not the_turn_is_summed_up():
        return {}
    try:
        player = world.player_nation
        events = _events(enemy_phase, tactical_events)
        lost: List[Dict[str, Any]] = []
        gained: List[Dict[str, Any]] = []
        friends_lost: List[Dict[str, Any]] = []
        friends_gained: List[Dict[str, Any]] = []
        was = before.get("regions") or {}
        for name, region in world.regions.items():
            old = str(was.get(name, "") or "")
            new = str(getattr(region, "controller", "") or "")
            if old == new:
                continue
            row = _change_row(world, before, name, old, new, events)
            if old == player:
                row["line"] = _lost_line(row)
                lost.append(row)
            elif new == player:
                row["line"] = _gained_line(row)
                gained.append(row)
            elif _standing(world, old) == "friend" and _standing(world, new) != "friend":
                row["line"] = (f"{name} ({row['from_shown']}'s) — lost to {row['to_shown']}."
                               + ((" " + row["why"][:1].upper() + row["why"][1:] + ".") if row["why"] else ""))
                friends_lost.append(row)
            elif _standing(world, new) == "friend" and _standing(world, old) != "friend":
                row["line"] = _gained_line(row, ours=False)
                friends_gained.append(row)
        battles = _our_battles(world, events)
        beside = _now_beside(world, before)
        out = {
            "turn": int(before.get("turn", 0) or 0),
            "lost": lost[:MAX_ROWS], "lost_more": max(0, len(lost) - MAX_ROWS),
            "gained": gained[:MAX_ROWS], "gained_more": max(0, len(gained) - MAX_ROWS),
            "friends_lost": friends_lost[:MAX_ROWS],
            "friends_lost_more": max(0, len(friends_lost) - MAX_ROWS),
            "friends_gained": friends_gained[:MAX_ROWS],
            "friends_gained_more": max(0, len(friends_gained) - MAX_ROWS),
            "battles": battles[:MAX_ROWS], "battles_more": max(0, len(battles) - MAX_ROWS),
            "beside": beside[:MAX_ROWS], "beside_more": max(0, len(beside) - MAX_ROWS),
            # every province that changed hands on or beside his side: the map flashes them
            "flash": [r["region"] for r in (lost + gained + friends_lost + friends_gained)][:24],
        }
        out["quiet"] = not (lost or gained or friends_lost or friends_gained or battles or beside)
        # Row PW part 2 (the user, of the report: "can we show the pieces moving
        # or something better?"): the few words the MAP wears at a province
        # while the turn is played on it — the report's own facts, no new one.
        out["plaques"] = _plaques(lost, friends_lost, battles, gained, friends_gained)
        # How to keep what is taken: said with the first province lost to a
        # march onto empty ground (the Carniola of the first playtest).
        out["keep_it"] = ""
        if any(r.get("how") in ("walked_in", "empty") for r in lost):
            out["keep_it"] = ("An empty province can be walked back into. Leave a corps in it, "
                              "or post a garrison there, to hold it.")
        return out
    except Exception as exc:
        report(exc, "while_you_waited.digest")
        return {}
