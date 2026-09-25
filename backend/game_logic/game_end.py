"""GE-1 "The Verdict and the Fall" — how a campaign ENDS.

Spec: docs/GAME_END_SPEC.md §2 (R1–R9, the gate record) and
docs/ENDGAME_PLAN.md §3–§6 (RULED — the routing authority for row EP). The
user's September 25, 2026 additions ride here too: the Emperor's death as
the third arm of the Fall ("The Eagle Falls"), and the exile story on the
Fall, told from the campaign's own record.

One module, one seam per concern:

* **The flag (R7).** The rules arm only where a scenario AUTHORS them — a
  `campaign_end` block (`europe_1805.json`). A new derived flag,
  `endings_armed`, never `sandbox_mode` (read in nine modules to mean "this
  is the Europe world"; flipping it would re-arm the 75% conquest win and the
  60-turn defeat EC-6 removed). The tutorial and the bare flag world never
  arm, so the suite's `SOVEREIGN_SCENARIO=none` pin keeps every sandbox test
  as it is.
* **`record_ending(world, kind, cause)`** — the ONE entry point every ending
  passes through (R7), into ONE serialized list `world.endings`. A terminal
  ending (the Fall) sets `game_over`; a marked one (the Verdict, the Humbled
  Peace) never does. Each cause is stamped once.
* **`process_end_of_turn`** — the ONE per-turn caller: the fall clocks
  (`fall.tick_fall_clocks`) and the Verdict at the authored turn. Called
  from `TurnManager.end_turn` after `advance_turn`, never from the victory
  check (which runs twice a turn).
* **`campaign_totals`** — ONE display-only accumulator (R4), written at the
  moment each thing happens because nothing the engine keeps is durable
  (`event_log` rolls at 500, the war ledgers pop at peace). GR6: never read
  by a mechanic.
* **`province_title`** — the stabilization substrate GE-3's Congress counts
  (ENDGAME_PLAN §2.2): a conquest joins the order only when the loser signs
  for it or when Europe has stopped contesting it.
* **The Humbled Peace** — a marked, non-terminal defeat stamped at the ratify
  seams when France signs away Paris, half its homeland, or its crown.
* **The Verdict** — four tiers from the state of the realm at the authored
  turn; **the exile story** — a deterministic epilogue (GR6: never the LLM).

GR5: every predicate answers for any nation; only the player's endings end
anything.
"""

from __future__ import annotations

import copy
from typing import Any, Dict, Iterable, List, Optional

# ════════════════════════════════════════════════════════════════════════
# Levers (the file convention: False reproduces the pre-GE-1 game).
# ════════════════════════════════════════════════════════════════════════

# R7: the campaign can end where the scenario authors a `campaign_end`
# block. Down, `endings_armed` is False everywhere — no clock, no Verdict,
# no Humbled Peace, no death roll: the sandbox byte-for-byte.
THE_CAMPAIGN_CAN_END = True

# The user's Sept 25, 2026 ask ("or if Napoleon dies"): at the ONE removal
# seam, a sovereign whose corps is destroyed on the battlefield may DIE
# instead of being taken. Down, the NP-4 death guard converts every removal
# to capture, as before.
THE_EMPEROR_IS_MORTAL = True

# The chance, in percent, that a sovereign whose corps is annihilated in the
# fighting dies with it rather than being taken. Blessed default, in-band
# tunable. 15: a battlefield death stays the rare catastrophe (Lannes at
# Aspern, the Réunion cannonball at Bautzen) — most annihilated corps give
# up their commander alive — while never being a thing the player can rule
# out. Measured frequency in the landing record.
SOVEREIGN_DEATH_CHANCE_PCT = 15

# The causes that are a BATTLEFIELD: an army annihilated in the fighting.
# Never attrition (starving is capture by the nearest court), internment,
# dismissal or a nation's teardown — and never while captive (a prisoner is
# never destroyed at all). "bombardment" is the auto-bombardment kill: the
# preparatory barrage that destroys a corps before the assault — a
# cannonball is a battlefield death.
BATTLEFIELD_CAUSES = frozenset({"battle", "charge", "bombardment"})

# The Humbled Peace (ENDGAME_PLAN §3 / GAME_END_SPEC §7.6).
THE_HUMBLED_PEACE_IS_MARKED = True

# §2.2 reconciliation: a court that SIGNED a cession has that province's
# Revanche weight read 0 while the treaty holds. Read by agendas.py.
A_SIGNED_CESSION_IS_RECONCILED = True

# ── Defaults (the scenario's block overrides; `cfg`) ──────────────────────
TITLE_TURNS_DEFAULT = 12

# ════════════════════════════════════════════════════════════════════════
# The flag.
# ════════════════════════════════════════════════════════════════════════


def campaign_end_block(world) -> Dict[str, Any]:
    block = getattr(world, "campaign_end", None)
    return dict(block) if isinstance(block, dict) else {}


def endings_armed(world) -> bool:
    """True where the scenario authored the rules (R7). Europe worlds only;
    the tutorial and the bare flag world author no block."""
    if not THE_CAMPAIGN_CAN_END or world is None:
        return False
    if not getattr(world, "sandbox_mode", False):
        return False
    return bool(campaign_end_block(world))


def cfg(world, key: str, default: Any) -> Any:
    value = campaign_end_block(world).get(key, default)
    if isinstance(value, bool) or value is None:
        return default
    return value


def verdict_turn(world) -> Optional[int]:
    value = campaign_end_block(world).get("verdict_turn")
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return int(value)


# ════════════════════════════════════════════════════════════════════════
# The endings.
# ════════════════════════════════════════════════════════════════════════

CAUSE_SOIL = "soil_or_sword"
CAUSE_CHAINS = "chains"
CAUSE_EAGLE_FALLS = "eagle_falls"
CAUSE_HUMBLED = "humbled_peace"
CAUSE_VERDICT = "verdict"
# GE-3's victory (ENDGAME_PLAN §2.6, D7 mark-and-continue): the register and
# its title are declared HERE so the end screen (GE-2) takes the fourth
# register from the same table the other three ride, and GE-3's
# `record_ending(world, "victory", CAUSE_IMPERIAL_PEACE)` needs no client
# change. Nothing stamps it before GE-3 lands the Congress.
CAUSE_IMPERIAL_PEACE = "imperial_peace"

TERMINAL_CAUSES = frozenset({CAUSE_SOIL, CAUSE_CHAINS, CAUSE_EAGLE_FALLS})

REGISTERS = {
    CAUSE_SOIL: "fall",
    CAUSE_CHAINS: "fall",
    CAUSE_EAGLE_FALLS: "fall",
    CAUSE_HUMBLED: "humbled_peace",
    CAUSE_VERDICT: "verdict",
    CAUSE_IMPERIAL_PEACE: "imperial_peace",
}

REGISTER_TITLES = {
    "fall": "THE FALL OF THE EMPIRE",
    "humbled_peace": "THE HUMBLED PEACE",
    "verdict": "THE VERDICT OF HISTORY",
    "imperial_peace": "THE IMPERIAL PEACE",
}


def _cause_line(world, cause: str, detail: Dict[str, Any]) -> str:
    """The one sentence the end screen leads with (ENDGAME_PLAN §4)."""
    from backend.game_logic import fall
    if cause == CAUSE_SOIL:
        realm, sword = bool(detail.get("realm")), bool(detail.get("sword"))
        held = [str(r) for r in (detail.get("held") or []) if r]
        # Worded by the count (review round): the arm fires at ≤ 1 province,
        # so "no soil remains" was false while Paris itself was still French.
        if realm and not sword:
            if held:
                return (f"The Empire is reduced to {held[0]} alone — a province, "
                        f"not a realm.")
            return ("No soil remains to the Emperor — his armies fight on for "
                    "a realm that is gone.")
        if sword and not realm:
            return ("No sword remains to the Emperor — no corps stands, and "
                    "none can be raised.")
        if held:
            return (f"The Empire is reduced to {held[0]} alone, and no sword "
                    f"remains to hold it.")
        return "No soil and no sword remain to the Emperor."
    if cause == CAUSE_CHAINS:
        grace = int(cfg(world, "captivity_grace_turns", fall.CAPTIVITY_GRACE_TURNS))
        held_for = int(detail.get("held_turns") or 0)
        paused = int(detail.get("paused_turns") or 0)
        # The clock counts turns at WAR with the captor; a truce pauses it.
        # Say what is true when the two differ (review round) — and name the
        # turns at war only when the truces account for the rest
        # (verification round: a clock that merely STARTED late, on a
        # pre-GE-1 save loaded with the Emperor already a prisoner, never
        # paused, and "10 of them at war" was false of 19 turns of war).
        if held_for > grace and paused > 0 and held_for == grace + paused:
            return (f"The Emperor, a prisoner these {held_for} turns — "
                    f"{grace} of them at war with his captor — is deposed.")
        if held_for > grace:
            return f"The Emperor, a prisoner these {held_for} turns, is deposed."
        return (f"The Emperor, a prisoner these {grace} turns, is deposed.")
    if cause == CAUSE_EAGLE_FALLS:
        return "The Emperor is dead."
    if cause == CAUSE_HUMBLED:
        return "The Emperor has signed a peace that humbles the Empire."
    if cause == CAUSE_VERDICT:
        return "The reign, unfinished, is judged as it stands."
    if cause == CAUSE_IMPERIAL_PEACE:
        return "Europe accepts the order of the French Empire."
    return ""


def endings(world) -> List[Dict[str, Any]]:
    value = getattr(world, "endings", None)
    return value if isinstance(value, list) else []


def terminal_ending(world) -> Optional[Dict[str, Any]]:
    for record in endings(world):
        if record.get("terminal"):
            return record
    return None


def latest_ending(world) -> Optional[Dict[str, Any]]:
    records = endings(world)
    return records[-1] if records else None


def has_ending(world, cause: str) -> bool:
    return any(r.get("cause") == cause for r in endings(world))


def record_ending(world, kind: str, cause: str,
                  detail: Optional[Dict[str, Any]] = None,
                  turn: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """The ONE seam every ending passes through (R7).

    Stamps the ending once per cause into `world.endings`, builds its
    campaign summary AT THE MOMENT (the Verdict's inputs are "derived at the
    moment and never stored beyond the stamped result" — R2), and — for a
    terminal cause — ends the war (`game_over`, `victory = "defeat"`).
    Returns the record, or None when the rules are not armed, the cause was
    already stamped, or a terminal ending already closed the campaign."""
    if not endings_armed(world):
        return None
    if has_ending(world, cause):
        return None
    if terminal_ending(world) is not None:
        return None
    if not isinstance(getattr(world, "endings", None), list):
        world.endings = []
    stamp_turn = int(turn if turn is not None
                     else getattr(world, "current_turn", 0) or 0)
    from backend.game_logic.calendar import calendar_label
    record: Dict[str, Any] = {
        "kind": str(kind),
        "cause": str(cause),
        "register": REGISTERS.get(cause, "verdict"),
        "title": REGISTER_TITLES.get(REGISTERS.get(cause, "verdict"), ""),
        "cause_line": _cause_line(world, cause, detail or {}),
        "turn": stamp_turn,
        "calendar_label": calendar_label(getattr(world, "start_date", ""),
                                         stamp_turn),
        "terminal": cause in TERMINAL_CAUSES,
        "nation": str(getattr(world, "player_nation", "") or ""),
        "detail": copy.deepcopy(detail or {}),
    }
    # Appended BEFORE its summary is built, so the summary grades the world
    # WITH this ending in it (review round: a Humbled Peace's own stamped
    # Verdict read "ascendant", because `verdict_inputs` could not yet see
    # the Humbled Peace that forces the eclipse).
    world.endings.append(record)
    record["summary"] = build_campaign_summary(world, record)
    if record["terminal"]:
        world.game_over = True
        world.victory = "defeat"
    try:
        verdict = (record.get("summary") or {}).get("verdict") or {}
        world.log_event({
            "type": "campaign_ending",
            "nation": record["nation"],
            "cause": record["cause"],
            "register": record["register"],
            "terminal": bool(record["terminal"]),
            "title": record["title"],
            "cause_line": record["cause_line"],
            "tier_title": str(verdict.get("title") or ""),
            "message": f"{record['title']}: {record['cause_line']}",
        })
    except Exception:
        pass
    return record


def compact(record: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """The ending as a save slot and a game-state summary carry it — the
    screen payload without the heavy epilogue facts."""
    if not isinstance(record, dict):
        return None
    summary = record.get("summary") or {}
    verdict = summary.get("verdict") or {}
    return {
        "kind": record.get("kind"),
        "cause": record.get("cause"),
        "register": record.get("register"),
        "title": record.get("title"),
        "cause_line": record.get("cause_line"),
        "turn": int(record.get("turn", 0) or 0),
        "calendar_label": record.get("calendar_label", ""),
        "terminal": bool(record.get("terminal")),
        "tier": verdict.get("tier", ""),
        "tier_title": verdict.get("title", ""),
    }


def screen_payload(record: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """The ending as the END SCREEN needs it (GE-2): the compact view plus
    the summary taken at the moment — totals, the Verdict's tier and lines,
    and the epilogue for a Fall or a Humbled Peace. Rides the end-turn road,
    `/load` and a `/command` that ended the war; `GET /campaign_end` returns
    every one. The client never recomputes any of it."""
    view = compact(record)
    if view is None:
        return None
    view["summary"] = copy.deepcopy(record.get("summary") or {})
    return view


# Flip lever (review round, Sept 25): False skips the CLOSE — the terminal
# summary stays as it was built at the stamp, and the unanswerable questions
# are left standing. It does NOT restore the pre-review /command-only attach
# (verification round): that attach was deleted, not kept behind this switch,
# so every response of a fallen campaign carries `game_over`/`ending` and
# the Final save either way.
THE_WAR_IS_CLOSED_AT_ONE_SEAM = True


def close_campaign(world) -> Optional[Dict[str, Any]]:
    """The war is over: finalize the TERMINAL record once, after whatever
    road stamped it has finished resolving, and clear every question nobody
    can answer.

    Called by every response (`main.build_base_response`), by the end-turn
    exits, by the Final save and by `/load` — idempotent (`closed`). The
    Emperor's death is stamped INSIDE the battle that kills him, before the
    battle is counted, before the province it takes changes hands; a summary
    built at the stamp said "0 battles" and laid him in state in a Paris
    that fell in the same fight. Rebuilt here, it reads the finished field.
    Returns the terminal record, or None.

    The summary is rebuilt ONCE; the clearing runs on EVERY call
    (verification round): a pause save taken after the Fall, or a question
    re-seeded by a road that runs after the response seam, would otherwise
    raise a card nobody can answer on every later response and load."""
    record = terminal_ending(world)
    if record is None or not THE_WAR_IS_CLOSED_AT_ONE_SEAM:
        return record
    if not record.get("closed"):
        record["closed"] = True
        try:
            record["summary"] = build_campaign_summary(world, record)
        except Exception:
            pass
    clear_unanswerable(world)
    return record


def clear_unanswerable(world) -> None:
    """Every choice a fallen campaign can no longer act on — the ONE list
    (run once, by `close_campaign`; the end-turn exits and every response
    close the campaign). A superset of the legacy
    `TurnManager._clear_game_over_modal_state`, which the unarmed game-over
    paths keep. Every command endpoint refuses once the war is over, so a question left
    standing is a card nobody can answer: in the response that ended the
    war, in the Final save, and in the load that opens it."""
    dm = getattr(world, "dialogue_manager", None)
    if dm is not None:
        try:
            while dm.peek():
                dm.pop()
        except Exception:
            pass
    queue = getattr(world, "_popup_queue", None)
    if queue is not None:
        try:
            from backend.models.cooldown_manager import PopupQueue
            for popup_type in PopupQueue.PRIORITY_ORDER:
                queue.clear_type(popup_type)
        except Exception:
            pass
    for attr, empty in (("vassal_rebellion_imminent_popups", []),
                        ("nation_proclamation_popups", []),
                        ("pending_capture_choice", None),
                        ("pending_objection", None),
                        ("pending_strategic_objection", None),
                        ("pending_redemption", None),
                        ("pending_marshal_petition", None)):
        if hasattr(world, attr):
            try:
                setattr(world, attr, copy.copy(empty))
            except Exception:
                pass
    player = _player(world)
    for marshal in (getattr(world, "marshals", {}) or {}).values():
        if getattr(marshal, "nation", None) != player:
            continue
        if getattr(marshal, "pending_interrupt", None):
            marshal.pending_interrupt = None
        if getattr(marshal, "pending_glorious_charge", False):
            try:
                marshal.reset_recklessness()
            except Exception:
                marshal.pending_glorious_charge = False


def victory_check(world) -> Dict[str, Any]:
    """`_check_victory_conditions`' sandbox arm: game over only when a
    TERMINAL ending has been recorded. A pure read — the clocks tick in
    `process_end_of_turn`, never here (the check runs twice a turn)."""
    record = terminal_ending(world) if endings_armed(world) else None
    if record is None:
        return {"game_over": False, "result": None, "reason": None}
    return {"game_over": True, "result": "defeat",
            "reason": record.get("cause_line") or record.get("title") or ""}


def process_end_of_turn(world, turn_ended: int) -> List[Dict[str, Any]]:
    """The ONE per-turn caller (after `advance_turn`): tick the fall clocks,
    then — at the authored turn, if the campaign still stands — render the
    Verdict. Returns the endings stamped this tick."""
    if not endings_armed(world):
        return []
    from backend.game_logic import fall
    stamped: List[Dict[str, Any]] = []
    fell = fall.tick_fall_clocks(world)
    if fell is not None:
        view = (fall.get_fall_state(world) or {}).get("arms", {}).get(fell) or {}
        detail = {"arm": fell}
        if view:
            d = view.get("detail") or {}
            if fell == fall.ARM_CHAINS:
                detail["captor"] = d.get("captor", "")
                taken = int(d.get("captured_turn", -1))
                if taken >= 0:
                    # How long he was HELD (the clock counts only turns at
                    # war with the captor — a truce pauses it).
                    detail["captured_turn"] = taken
                    detail["held_turns"] = max(0, int(turn_ended) - taken + 1)
                    entry = (getattr(world, "fall_clock", {}) or {}).get(fall.ARM_CHAINS) or {}
                    detail["paused_turns"] = int(entry.get("paused_turns", 0) or 0)
            else:
                detail["realm"] = bool(d.get("realm"))
                detail["sword"] = bool(d.get("sword"))
                detail["held"] = sorted(
                    world.get_nation_regions(_player(world)) or [])
        rec = record_ending(world, "defeat", fell, detail=detail,
                            turn=int(turn_ended))
        if rec is not None:
            stamped.append(rec)
    vt = verdict_turn(world)
    if (vt is not None and int(turn_ended) >= vt
            and terminal_ending(world) is None
            and not has_ending(world, CAUSE_VERDICT)):
        rec = record_ending(world, "verdict", CAUSE_VERDICT,
                            turn=int(turn_ended))
        if rec is not None:
            stamped.append(rec)
    return stamped


# ════════════════════════════════════════════════════════════════════════
# "The Eagle Falls" — the Emperor's death (Sept 25, 2026).
# ════════════════════════════════════════════════════════════════════════

def sovereign_death_roll(world, marshal, cause: str) -> bool:
    """Does the sovereign whose corps was just annihilated DIE?

    Called from `WorldState.destroy_marshal`'s sovereign arm — the ONE
    removal seam — and nowhere else. Armed worlds only; battlefield causes
    only; a deterministic draw on the campaign seed (`seeded_int`, the
    `naval._pct_roll` idiom: the historical seed still ROLLS — the
    historical-neutral arms of `seeded_jitter`/`seeded_tiebreak` would make
    him immortal on the suite's own seed). No module RNG is consumed (M1–M7
    and 21 test files depend on its draw order). The namespace carries the
    turn, the man and the cause, so two annihilations are two rolls."""
    if not THE_EMPEROR_IS_MORTAL or not endings_armed(world):
        return False
    if str(cause) not in BATTLEFIELD_CAUSES:
        return False
    if getattr(marshal, "captured_by", ""):
        return False
    from backend.game_logic.campaign_variance import seeded_int
    seed = str(getattr(world, "campaign_seed", "historical") or "historical")
    namespace = (f"sovereign::death::{int(getattr(world, 'current_turn', 0) or 0)}"
                 f"::{marshal.name}::{cause}")
    return seeded_int(seed, namespace, 0, 99) < int(SOVEREIGN_DEATH_CHANCE_PCT)


def record_sovereign_death(world, marshal, cause: str, victor: str = "",
                           location: str = "") -> None:
    """After the sovereign's removal: the ending (player) or nothing more
    (a foreign sovereign — GR5 by construction; none is authored in 1805).
    `location` is the FIELD he fell on (an attacker is destroyed before he
    advances, so his own `location` is still the province he marched from)."""
    if marshal.nation != getattr(world, "player_nation", None):
        return
    record_ending(world, "defeat", CAUSE_EAGLE_FALLS, detail={
        "location": str(location or getattr(marshal, "location", "") or ""),
        "cause": str(cause),
        "victor": str(victor or ""),
        "sovereign": marshal.name,
    })


# ════════════════════════════════════════════════════════════════════════
# campaign_totals — the display-only accumulator (R4, GR6).
# ════════════════════════════════════════════════════════════════════════

_COUNTERS = (
    "battles_fought", "battles_won", "battles_lost", "battles_drawn",
    "men_lost", "men_inflicted", "battles_in_person",
    "provinces_taken", "provinces_lost",
    "provinces_ceded", "provinces_gained_by_treaty",
    "enemy_marshals_taken", "own_marshals_taken",
    "marshals_fallen", "enemy_corps_destroyed",
    "coalitions_faced", "peaces_signed",
)
TREATY_MEMORY = 12
COALITION_MEMORY = 12


def totals(world) -> Dict[str, Any]:
    """The accumulator, with every key present (lazily completed)."""
    data = getattr(world, "campaign_totals", None)
    if not isinstance(data, dict):
        data = {}
        world.campaign_totals = data
    for key in _COUNTERS:
        data.setdefault(key, 0)
    # A record kept before the distinct list existed (a 975f1f13 save that
    # had already lost provinces): the distinct count and its courts cannot
    # be recovered, so the epilogue counts the LOSSES instead — the unit the
    # old record kept (verification round: "One province was lost, to
    # Austria." after six were lost, the one listed to Britain).
    if ("lost_regions" not in data
            and int(data.get("provinces_lost", 0) or 0) > 0):
        data["lost_regions_partial"] = True
    data.setdefault("lost_to", {})
    data.setdefault("taken_from", {})
    data.setdefault("lost_regions", [])
    data.setdefault("lost_region_to", {})
    data.setdefault("coalition_names", [])
    data.setdefault("treaties", [])
    data.setdefault("greatest_victory", None)
    data.setdefault("worst_defeat", None)
    data.setdefault("opening", {})
    return data


def _player(world) -> str:
    return str(getattr(world, "player_nation", "") or "")


def count_battle(world, *, player_side: str, won: bool, lost: bool,
                 inflicted: int, suffered: int, name: str, region: str,
                 enemy: str, in_person: bool = False) -> None:
    """One battle the player's army fought (every combat path's pipeline,
    plus the auto-charge's mirrored arm)."""
    data = totals(world)
    data["battles_fought"] += 1
    if won:
        data["battles_won"] += 1
    elif lost:
        data["battles_lost"] += 1
    else:
        data["battles_drawn"] += 1
    data["men_lost"] += max(0, int(suffered or 0))
    data["men_inflicted"] += max(0, int(inflicted or 0))
    if in_person:
        data["battles_in_person"] += 1
    row = {
        "name": str(name or f"the fighting at {region}"),
        "turn": int(getattr(world, "current_turn", 0) or 0),
        "region": str(region or ""),
        "enemy": str(enemy or ""),
        "inflicted": max(0, int(inflicted or 0)),
        "suffered": max(0, int(suffered or 0)),
        "side": str(player_side),
    }
    best = data.get("greatest_victory")
    if won and (not isinstance(best, dict)
                or row["inflicted"] > int(best.get("inflicted", 0))):
        data["greatest_victory"] = row
    worst = data.get("worst_defeat")
    if lost and (not isinstance(worst, dict)
                 or row["suffered"] > int(worst.get("suffered", 0))):
        data["worst_defeat"] = row


def count_capture(world, old_controller: str, capturing_nation: str,
                  region: str = "") -> None:
    """A province changing hands by force with the player on one side.
    `lost_regions` keeps the DISTINCT provinces lost (a province lost twice
    is one province — the epilogue says so), bounded by the map, and
    `lost_region_to` the court that took each LAST (verification round: the
    courts were ranked by capture events against a distinct count, so a
    province lost three times to Austria outweighed two lost to Britain)."""
    player = _player(world)
    if not player or old_controller == capturing_nation:
        return
    if capturing_nation == player and old_controller:
        data = totals(world)
        data["provinces_taken"] += 1
        data["taken_from"][old_controller] = int(
            data["taken_from"].get(old_controller, 0)) + 1
    elif old_controller == player and capturing_nation:
        data = totals(world)
        data["provinces_lost"] += 1
        data["lost_to"][capturing_nation] = int(
            data["lost_to"].get(capturing_nation, 0)) + 1
        if region:
            lost_regions = data.setdefault("lost_regions", [])
            if region not in lost_regions:
                lost_regions.append(str(region))
            data.setdefault("lost_region_to", {})[str(region)] = str(capturing_nation)


def count_marshal_captured(world, marshal_nation: str, captor: str) -> None:
    player = _player(world)
    if captor == player:
        totals(world)["enemy_marshals_taken"] += 1
    elif marshal_nation == player:
        totals(world)["own_marshals_taken"] += 1


def count_marshal_destroyed(world, marshal_nation: str, cause: str,
                            victor: str) -> None:
    player = _player(world)
    if marshal_nation == player and cause not in ("dismissed", "nation_eliminated"):
        totals(world)["marshals_fallen"] += 1
    elif victor and victor == player and marshal_nation != player:
        totals(world)["enemy_corps_destroyed"] += 1


def count_coalition(world, name: str) -> None:
    data = totals(world)
    data["coalitions_faced"] += 1
    names = data["coalition_names"]
    if name:
        names.append(str(name))
        del names[:-COALITION_MEMORY]


def seed_opening(world) -> None:
    """At boot (from_scenario only — never at load): what the reign began
    with, for the Verdict and the epilogue."""
    player = _player(world)
    if not player:
        return
    data = totals(world)
    data["opening"] = {
        "turn": int(getattr(world, "current_turn", 1) or 1),
        "provinces": int(len(getattr(world, "nation_starting_regions", {})
                             .get(player, []) or [])),
        "satellites": sorted(v for v, row in (getattr(world, "vassals", {}) or {}).items()
                             if isinstance(row, dict) and row.get("lord") == player),
    }
    coalition = getattr(world, "active_coalition", None) or {}
    if isinstance(coalition, dict) and coalition.get("target_nation") == player:
        count_coalition(world, str(coalition.get("name") or ""))


def backfill_record(world) -> None:
    """A save from before GE-1, armed at load (`save_manager`'s backfill):
    the opening seeded as boot would have (the homeland from the scenario's
    own starting regions), `record_since_turn` stamped so the summary says
    where the record begins, and a CONQUEST title record — quiet clock
    starting now — for every province held off its holder's homeland, so a
    conquest made before the upgrade can still earn title (review round:
    "held" forever, invisible to GE-3's count). One scan, at load only."""
    data = totals(world)
    if not data.get("opening"):
        seed_opening(world)
    data["record_since_turn"] = int(getattr(world, "current_turn", 0) or 0)
    store = _title_store(world)
    if store:
        return
    owners: Dict[str, str] = {}
    for nation, names in (getattr(world, "nation_starting_regions", {}) or {}).items():
        for name in names or []:
            owners.setdefault(name, nation)
    turn = int(getattr(world, "current_turn", 0) or 0)
    for name, region in (getattr(world, "regions", {}) or {}).items():
        holder = getattr(region, "controller", "") or ""
        if not holder or _is_homeland(world, name, holder):
            continue
        store[name] = {"kind": TITLE_CONQUEST, "since": turn,
                       "from": owners.get(name, ""), "holder": holder,
                       "house": str(world._top_overlord(holder) or holder)}
    # A carve made before the upgrade is a cession like one made after it
    # (verification round): its provinces the client still holds take the
    # carve's treaty record.
    for tag, row in (getattr(world, "vassals", {}) or {}).items():
        if not isinstance(row, dict) or not row.get("carved_from"):
            continue
        carved = [p for p in (row.get("regions") or [])
                  if getattr((getattr(world, "regions", {}) or {}).get(p),
                             "controller", "") == tag]
        record_carve_titles(world, carved, str(row.get("carved_from")), tag,
                            str(row.get("lord") or ""))


# ════════════════════════════════════════════════════════════════════════
# province_title — the stabilization substrate (ENDGAME_PLAN §2.2).
# ════════════════════════════════════════════════════════════════════════

TITLE_CONQUEST = "conquest"
TITLE_TREATY = "treaty"


def _title_store(world) -> Dict[str, Dict[str, Any]]:
    store = getattr(world, "province_title", None)
    if not isinstance(store, dict):
        store = {}
        world.province_title = store
    return store


def _is_homeland(world, region: str, nation: str) -> bool:
    return region in (getattr(world, "nation_starting_regions", {}) or {}).get(nation, [])


def record_province_title(world, region: str, kind: str, from_nation: str,
                          receiver: str, house: str = "") -> None:
    """Write (or clear) the title record when `region` changes hands.

    `house` (verification round) is the court the title belongs to — the
    SIGNATORY of a treaty, the conquering bloc's leader for a conquest
    (default: the receiver's top overlord). It is what survives a hand-off:
    the record follows the province to any holder of the same house (a
    satellite given it, the lord reclaiming it), and a signature is broken
    only by the two courts that signed it. GR5: written for every nation. A
    province returning to its own homeland court needs no record (homeland
    is title by construction) — the record is popped. Never raises (a title
    is display substrate, never a reason to fail a capture)."""
    if not region or not receiver:
        return
    try:
        store = _title_store(world)
        if _is_homeland(world, region, receiver):
            store.pop(region, None)
            return
        store[region] = {
            "kind": str(kind),
            "since": int(getattr(world, "current_turn", 0) or 0),
            "from": str(from_nation or ""),
            "holder": str(receiver),
            "house": str(house or world._top_overlord(receiver) or receiver),
        }
    except Exception:
        return


def record_carve_titles(world, provinces: Iterable[str], ceder: str,
                        client: str, carver: str) -> None:
    """A Tilsit carve is a cession (verification round): each carved province
    gets a TREATY record — from the ceder, held by the client, signed by the
    carver — so it reconciles, re-homes and breaks exactly like a province
    signed away by treaty, and outlives the client's release. Written
    directly: the client's homeland IS the carve (`create_client_nation`
    seeds its starting regions), so `record_province_title`'s homeland pop
    would erase the very record. Only the provinces carved — never whatever
    else the client later holds."""
    if not ceder or not client:
        return
    try:
        store = _title_store(world)
        turn = int(getattr(world, "current_turn", 0) or 0)
        for name in provinces or []:
            if not name:
                continue
            store[str(name)] = {
                "kind": TITLE_TREATY,
                "since": turn,
                "from": str(ceder),
                "holder": str(client),
                "house": str(carver or world._top_overlord(client) or client),
                "carve": True,
            }
    except Exception:
        return


def _house(world, rec: Dict[str, Any]) -> str:
    """The court a record's title belongs to (a record written before the
    key existed reads its holder's lord)."""
    house = str(rec.get("house") or "")
    if house:
        return house
    holder = str(rec.get("holder") or "")
    return str(world._top_overlord(holder) or holder) if holder else ""


def title_signed_cessions(world, terms: Iterable[Dict[str, Any]]) -> None:
    """A cession SIGNED for a province the receiver already occupies: the
    clause itself is skipped by the ratifiers (the ceder no longer holds it),
    but the loser has signed — title is immediate (§2.2 "ceded by treaty")."""
    try:
        from backend.game_logic.settlement_validation import _territory_term_regions
    except Exception:
        return
    for term in terms or []:
        if not isinstance(term, dict):
            continue
        if term.get("type") not in ("territory_cede", "territory"):
            continue
        receiver = str(term.get("to") or "")
        ceder = str(term.get("from") or "")
        if not receiver or not ceder:
            continue
        for region_name in _territory_term_regions(term):
            region = getattr(world, "regions", {}).get(region_name)
            if region is None or not region.controller:
                continue
            # The receiver's own satellite occupying the signed province is
            # the receiver's bloc holding it (review round): titled, with
            # the record's holder the court that actually holds it.
            if (region.controller == receiver
                    or world._top_overlord(region.controller)
                    == world._top_overlord(receiver)):
                record_province_title(world, region_name, TITLE_TREATY,
                                      ceder, region.controller,
                                      house=world._top_overlord(receiver))


def break_signed_titles(world, nation_a: str, nation_b: str) -> None:
    """A renewed WAR between the two courts that SIGNED a cession breaks the
    signature (§2.2's renewed-war restart): the treaty record becomes a
    conquest record whose quiet clock starts now. A later treaty that
    re-signs the province re-titles it (`title_signed_cessions`); a truce or
    a white peace that does not, no longer reconciles it (review round: an
    armistice inside the very war that broke the cession had read as "the
    treaty stands" and silenced the Revanche again). A carve is a treaty
    record like any other (`record_carve_titles`), broken the same way.

    The signatories are the ceder (`from`) and the record's `house` —
    never the two courts' BLOCS (verification round: a French satellite's
    own war with Austria, France and Austria still allied, unsigned
    France's Tyrol; a satellite's war pauses the reconciliation through
    `reconciled_regions`' at-war read instead). Called from the ONE
    diplomatic-state setter on every entry into WAR (the settlement's
    vassalage bookkeeping hop excepted), and from the two roads that
    repudiate a treaty without war (`diplomacy.break_treaty`, the paradox
    choice)."""
    store = getattr(world, "province_title", None)
    if not isinstance(store, dict):
        return
    turn = int(getattr(world, "current_turn", 0) or 0)
    pair = {str(nation_a or ""), str(nation_b or "")}
    for rec in store.values():
        if not isinstance(rec, dict) or rec.get("kind") != TITLE_TREATY:
            continue
        if {str(rec.get("from") or ""), _house(world, rec)} == pair:
            rec["kind"] = TITLE_CONQUEST
            rec["since"] = turn


def reconcile_province_titles(world) -> None:
    """The per-turn pass (advance_turn's NA block): a conquest's quiet
    clock restarts when a hostile army stands on it or its former owner is
    at war with its holder. A record whose holder no longer holds the
    province is dropped (it changed hands by a road that writes no title).
    ONE marshal pass (`get_disrupted_regions`) + the records (GR8)."""
    store = getattr(world, "province_title", None)
    if not isinstance(store, dict) or not store:
        return
    turn = int(getattr(world, "current_turn", 0) or 0)
    disrupted = None
    for region_name in list(store.keys()):
        rec = store.get(region_name)
        region = getattr(world, "regions", {}).get(region_name)
        if not isinstance(rec, dict) or region is None:
            store.pop(region_name, None)
            continue
        # The house is stamped while the holder's allegiance is still the
        # one that titled it (a record written before the key existed).
        if not rec.get("house"):
            rec["house"] = _house(world, rec)
        if region.controller != rec.get("holder"):
            # A hand-off to another holder of the same HOUSE — a VS-3 grant
            # to a satellite, the IQ-7 petition's province, and the lord's
            # reclaim of a grant from a rebel — carries the record (kind,
            # clock and ceder) to the new holder (review round: the grant
            # made a treaty province permanently "held"; verification round:
            # the reclaim ran after the rebel had left the bloc, so a bloc
            # test popped the record and the ceder's Revanche woke while the
            # treaty stood). A province returned to its new holder's own
            # homeland needs no record.
            new_holder = str(region.controller or "")
            new_top = world._top_overlord(new_holder) if new_holder else ""
            if (new_holder
                    and (new_top == rec.get("house")
                         or new_top == world._top_overlord(
                             str(rec.get("holder") or "")))
                    and not _is_homeland(world, region_name, new_holder)):
                rec["holder"] = new_holder
            else:
                store.pop(region_name, None)
                continue
        if rec.get("kind") == TITLE_TREATY:
            # The backup to the setter's `break_signed_titles`: the two
            # courts that signed (or their lords) at war breaks the
            # signature too. Never a satellite's own leftover sub-war, older
            # than the cession — that pauses the reconciliation
            # (`reconciled_regions` reads it) without unsigning the treaty.
            former = str(rec.get("from") or "")
            if former and world.is_at_war(world._top_overlord(former),
                                          world._top_overlord(rec["house"])):
                rec["kind"] = TITLE_CONQUEST
                rec["since"] = turn
            continue
        if rec.get("kind") != TITLE_CONQUEST:
            continue
        if disrupted is None:
            disrupted = world.get_disrupted_regions()
        former = str(rec.get("from") or "")
        contested = region_name in disrupted
        if not contested and former:
            holder_top = world._top_overlord(region.controller)
            former_top = world._top_overlord(former)
            contested = (world.is_at_war(former, region.controller)
                         or world.is_at_war(former_top, holder_top))
        if contested:
            rec["since"] = turn


def province_title_kind(world, region_name: str, leader: str) -> str:
    """`homeland` / `treaty` / `conquest` (quiet ≥ title_turns) / `held`
    (in the bloc, unsettled) / `` (not the bloc's).

    The bloc is the leader plus its vassal chain — never its allies
    (`get_bloc_members` includes ALLIANCE partners; the title rule is France
    plus her satellites)."""
    region = getattr(world, "regions", {}).get(region_name)
    if region is None or not region.controller:
        return ""
    holder = region.controller
    if world._top_overlord(holder) != leader:
        return ""
    if _is_homeland(world, region_name, holder):
        if holder == leader:
            return "homeland"
        row = (getattr(world, "vassals", {}) or {}).get(holder) or {}
        return "homeland" if int(row.get("loyalty", 0) or 0) >= 40 else "held"
    rec = (getattr(world, "province_title", {}) or {}).get(region_name) or {}
    if not rec or (world._top_overlord(str(rec.get("holder") or "")) != leader
                   and _house(world, rec) != leader):
        # (A hand-off inside the bloc — or back to the house that titled it,
        # a reclaim — keeps its record even before the per-turn pass
        # re-homes it.)
        return "held"
    if rec.get("kind") == TITLE_TREATY:
        return "treaty"
    title_turns = int(cfg(world, "title_turns", TITLE_TURNS_DEFAULT))
    if int(getattr(world, "current_turn", 0) or 0) - int(rec.get("since", 0)) >= title_turns:
        return "conquest"
    return "held"


def titled_provinces(world, leader: str) -> Dict[str, List[str]]:
    """The bloc's provinces split titled / held-unsettled — the count GE-3's
    Congress summons on. Reads the per-turn cached region index per bloc
    member (GR8)."""
    members = [leader] + sorted(v for v in (getattr(world, "vassals", {}) or {})
                                if world._top_overlord(v) == leader and v != leader)
    titled: List[str] = []
    held: List[str] = []
    for member in members:
        for region_name in world.get_nation_regions(member) or []:
            kind = province_title_kind(world, region_name, leader)
            if kind in ("homeland", "treaty", "conquest"):
                titled.append(region_name)
            elif kind == "held":
                held.append(region_name)
    return {"titled": sorted(titled), "held": sorted(held)}


def reconciled_regions(world, nation: str) -> set:
    """§2.2 rider: the provinces `nation` has SIGNED away while the treaty
    still holds — its Revanche reads them 0. Zero new world fields: the
    TREATY title record names the ceder, and "the treaty stands" is the
    record staying `treaty` — broken into a conquest by a renewed war
    between the signatories, or by a treaty repudiated without war
    (`break_signed_titles`); the `active_treaties` row is NOT read (review
    round: the armistice's own row had counted as "the treaty stands"). A
    Tilsit carve is a treaty record too (`record_carve_titles` —
    verification round: read off the client's vassal row, it reconciled the
    client's whole live territory, and lapsed when the client was released
    in peace). A war between the ceder and the province's holder, or the
    holder's lord, or the house that signed, PAUSES the reconciliation."""
    if not A_SIGNED_CESSION_IS_RECONCILED:
        return set()
    out = set()
    store = getattr(world, "province_title", None)
    if isinstance(store, dict):
        for region_name, rec in store.items():
            if not isinstance(rec, dict) or rec.get("kind") != TITLE_TREATY:
                continue
            if rec.get("from") != nation:
                continue
            holder = str(rec.get("holder") or "")
            if not holder:
                continue
            holder_top = world._top_overlord(holder)
            house = _house(world, rec)
            if (world.is_at_war(nation, holder)
                    or world.is_at_war(nation, holder_top)
                    or (house and world.is_at_war(nation, house))):
                continue
            out.add(region_name)
    return out


# ════════════════════════════════════════════════════════════════════════
# The ratification seams — title, totals, and the Humbled Peace.
# ════════════════════════════════════════════════════════════════════════

def count_peace(world, nation_a: str, nation_b: str) -> None:
    """A peace that no ratifier signs — an armistice that runs out into
    PEACE (`diplomacy._process_armistice_expiration`). The truce itself was
    never counted (a truce is not a peace), so the war it ends is counted
    here, once."""
    player = _player(world)
    if player and player in (nation_a, nation_b):
        totals(world)["peaces_signed"] += 1


def note_ratification(world, *, signed_terms: Iterable[Dict[str, Any]],
                      applied_clauses: Iterable[Dict[str, Any]],
                      was_vassal: bool, counterparts: Iterable[str],
                      war_ending: bool, source: str) -> Optional[Dict[str, Any]]:
    """Called once per ratification by the two top-level ratifiers
    (`WorldState._ratify_treaty` and `settlement_ratify.ratify_settlement_confirm`)
    — never inside `_apply_settlement_terms` or `apply_create_client_clause`,
    which run on headless paths and would stamp twice (the carve's applied
    clause is in both callers' lists, so the plan's third seam is covered).

    Titles every SIGNED cession (occupied provinces included), counts the
    player's peaces and cessions, and stamps the Humbled Peace when France
    signed away Paris, at least half its homeland, or its crown. Returns the
    Humbled-Peace record when one was stamped."""
    signed = [dict(t) for t in (signed_terms or []) if isinstance(t, dict)]
    applied = [dict(c) for c in (applied_clauses or []) if isinstance(c, dict)]
    title_signed_cessions(world, signed)
    player = _player(world)
    parties = [str(c) for c in (counterparts or []) if c]
    if not player or not parties:
        return None
    try:
        from backend.game_logic.settlement_validation import _territory_term_regions
    except Exception:
        return None
    ceded = set()
    gained = set()
    regions = getattr(world, "regions", {}) or {}

    def _ours(region_name: str) -> bool:
        # France or a satellite of France — never France's new LORD's bloc
        # (a treaty that makes France a vassal must not read every province
        # it ceded to that lord as still "ours").
        region = regions.get(region_name)
        if region is None or not region.controller:
            return False
        return (region.controller == player
                or world._top_overlord(region.controller) == player)

    # What actually changed hands (review round): a clause the ratifier
    # SKIPPED (PL-20's elimination guard, a carve that failed its
    # re-verification) left the province French, and was counted — "gave
    # away Paris itself" stamped while France still held Paris. A signed
    # territory term counts when the province is no longer ours (occupied
    # provinces signed away included — that is the point of the signature);
    # a carve counts only from the APPLIED list.
    for term in signed + applied:
        ttype = term.get("type")
        if ttype in ("territory_cede", "territory"):
            names = _territory_term_regions(term)
            if term.get("from") == player:
                ceded.update(r for r in names if not _ours(r))
            elif term.get("to") == player:
                gained.update(r for r in names if _ours(r))
    for term in applied:
        if term.get("type") == "create_client" and term.get("from") == player:
            ceded.update(str(p) for p in (term.get("provinces") or [])
                         if p and not _ours(str(p)))
    data = totals(world)
    if war_ending:
        data["peaces_signed"] += 1
    data["provinces_ceded"] += len(ceded)
    data["provinces_gained_by_treaty"] += len(gained)
    lord = str(((getattr(world, "vassals", {}) or {}).get(player) or {}).get("lord") or "")
    made_vassal = bool(lord) and not was_vassal
    row = {
        "turn": int(getattr(world, "current_turn", 0) or 0),
        "with": sorted(set(parties)),
        "source": str(source),
        "war_ending": bool(war_ending),
        "ceded": sorted(ceded),
        "gained": sorted(gained),
        "vassal_of": lord if made_vassal else "",
    }
    data["treaties"].append(row)
    del data["treaties"][:-TREATY_MEMORY]
    if not THE_HUMBLED_PEACE_IS_MARKED:
        return None
    homeland = list((getattr(world, "nation_starting_regions", {}) or {}).get(player, []) or [])
    capital = world.get_nation_capital(player) or ""
    ceded_home = ceded & set(homeland)
    capital_ceded = bool(capital) and capital in ceded
    half = bool(homeland) and len(ceded_home) * 2 >= len(homeland)
    if not (made_vassal or capital_ceded or half):
        return None
    return record_ending(world, "defeat", CAUSE_HUMBLED, detail={
        "with": row["with"],
        "ceded": sorted(ceded),
        "homeland_ceded": sorted(ceded_home),
        "homeland_total": len(homeland),
        "capital": capital,
        "capital_ceded": capital_ceded,
        "vassal_of": lord if made_vassal else "",
        "source": str(source),
    })


# ════════════════════════════════════════════════════════════════════════
# The Verdict of History (R2).
# ════════════════════════════════════════════════════════════════════════

# The tiers, best first: (id, minimum score, title, its three lines). The
# thresholds are in-band tunable; the SHAPE — four tiers, a status-quo reign
# reading "contested", a Humbled Peace forcing the eclipse — is the ruling.
VERDICT_TIERS = (
    ("triumph", 5, "A REIGN OF TRIUMPH", (
        "Europe has been remade, and it knows it.",
        "The great powers that stood against him in 1805 no longer stand as they did.",
        "History will call it the zenith — and ask only how long it could last.",
    )),
    ("ascendant", 2, "THE ASCENDANT EMPIRE", (
        "The Empire stands larger and surer than it began.",
        "Its enemies are fewer, or poorer, or both.",
        "History will call it a rising star — not yet fixed in the heavens.",
    )),
    ("contested", -1, "AN EMPIRE CONTESTED", (
        "The Empire holds what it held, and Europe has not accepted it.",
        "The coalition is beaten in the field and unbeaten at the table.",
        "History will call it unfinished — the question of 1805, still open.",
    )),
    ("eclipse", None, "THE ECLIPSE", (
        "The Empire is smaller, poorer and more alone than it began.",
        "Its enemies have learned that it can be beaten.",
        "History will call it the beginning of the end.",
    )),
)
TIER_LINE_CLOSINGS = {
    "triumph": "The Verdict of History: a reign of triumph.",
    "ascendant": "The Verdict of History: an empire ascendant.",
    "contested": "The Verdict of History: an empire contested, the question of 1805 still open.",
    "eclipse": "The Verdict of History: the eclipse.",
}


def great_powers(world) -> List[str]:
    """The other majors on the ROSTER (never `get_active_nations()`, which
    drops the dead): authored tier "major", else the canonical five."""
    player = _player(world)
    roster = [player] + list(getattr(world, "enemy_nations", []) or [])
    majors = []
    for nation in roster:
        if nation == player or nation in majors:
            continue
        try:
            tier = world.get_power_tier(nation)
        except Exception:
            tier = None
        if tier == "major":
            majors.append(nation)
    if not majors:
        from backend.game_logic.coalition import _CANONICAL_MAJORS
        majors = [n for n in _CANONICAL_MAJORS if n != player]
    return majors


def _eliminated(world, nation: str) -> bool:
    try:
        return not world.get_nation_regions(nation)
    except Exception:
        return False


def verdict_inputs(world) -> Dict[str, Any]:
    """Derived at the moment (R2) — never stored beyond the stamped result."""
    from backend.game_logic import fall
    from backend.game_logic.diplomacy import get_war_score_for
    player = _player(world)
    data = totals(world)
    opening = data.get("opening") or {}
    opening_provinces = int(opening.get("provinces") or len(
        (getattr(world, "nation_starting_regions", {}) or {}).get(player, []) or []))
    held = len(world.get_nation_regions(player) or [])
    capital = world.get_nation_capital(player) or ""
    capital_region = getattr(world, "regions", {}).get(capital) if capital else None
    capital_held = bool(capital_region is not None and capital_region.controller == player)
    sov = fall.sovereign_of(world, player)
    fallen_sov = any(isinstance(t, dict) and t.get("sovereign") and t.get("nation") == player
                     for t in (getattr(world, "fallen_marshals", {}) or {}).values())
    at_war = set(world.get_nations_at_war_with(player) or [])
    majors = great_powers(world)
    knocked_out = []
    at_war_rows = []
    vassals = getattr(world, "vassals", {}) or {}
    for nation in majors:
        row = vassals.get(nation) or {}
        if row.get("lord") == player or (_eliminated(world, nation) and nation not in vassals):
            knocked_out.append(nation)
            continue
        if nation in at_war:
            at_war_rows.append({"nation": nation,
                                "war_score": int(get_war_score_for(world, player, nation))})
    opening_sats = list(opening.get("satellites") or [])
    kept = [s for s in opening_sats if (vassals.get(s) or {}).get("lord") == player]
    return {
        "opening_provinces": opening_provinces,
        "provinces_held": int(held),
        "capital": capital,
        "capital_held": capital_held,
        "emperor": ("dead" if fallen_sov else
                    ("captive" if sov is not None and getattr(sov, "captured_by", "")
                     else ("free" if sov is not None else "absent"))),
        "great_powers": majors,
        "great_powers_knocked_out": knocked_out,
        "great_powers_at_war": at_war_rows,
        "satellites_opening": opening_sats,
        "satellites_kept": kept,
        "treasury": int(getattr(world, "gold", 0) or 0),
        "humbled": has_ending(world, CAUSE_HUMBLED),
        # A Fall forces the eclipse, as a Humbled Peace does (verification
        # round: a reign that had doubled its provinces and knocked out two
        # great powers closed the Emperor's funeral with "an empire
        # ascendant … a rising star", a paragraph after the Senate declared
        # the Empire at an end).
        "fallen": terminal_ending(world) is not None,
    }


def verdict_tier(world, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """The Verdict — a score over the inputs, read as one of four tiers."""
    inputs = inputs or verdict_inputs(world)
    score = 0
    opening = max(1, int(inputs["opening_provinces"]))
    ratio = inputs["provinces_held"] / float(opening)
    if ratio >= 1.75:
        score += 3
    elif ratio >= 1.4:
        score += 2
    elif ratio >= 1.15:
        score += 1
    elif ratio >= 0.9:
        score += 0
    elif ratio >= 0.6:
        score -= 1
    elif ratio >= 0.3:
        score -= 2
    else:
        score -= 3
    if not inputs["capital_held"]:
        score -= 2
    if inputs["emperor"] == "captive":
        score -= 3
    elif inputs["emperor"] == "dead":
        score -= 5
    score += min(4, 2 * len(inputs["great_powers_knocked_out"]))
    for row in inputs["great_powers_at_war"]:
        if row["war_score"] >= 25:
            score += 1
        elif row["war_score"] <= -25:
            score -= 1
    opening_sats = inputs["satellites_opening"]
    if opening_sats and len(inputs["satellites_kept"]) * 2 < len(opening_sats):
        score -= 1
    if inputs["treasury"] < 0:
        score -= 1
    tier_id, title, lines = VERDICT_TIERS[-1][0], VERDICT_TIERS[-1][2], VERDICT_TIERS[-1][3]
    if not inputs["humbled"] and not inputs.get("fallen"):
        for tid, floor, ttitle, tlines in VERDICT_TIERS:
            if floor is None or score >= floor:
                tier_id, title, lines = tid, ttitle, tlines
                break
    return {"tier": tier_id, "title": title,
            "lines": _tier_lines(world, tier_id, lines, inputs),
            "closing": TIER_LINE_CLOSINGS[tier_id],
            "score": int(score), "inputs": inputs}


def _tier_lines(world, tier_id: str, lines, inputs: Dict[str, Any]) -> List[str]:
    """The tier's three lines, each chosen from what is TRUE (review round:
    the fixed lines told a France that lost every battle "the coalition is
    beaten in the field", and one that had ceded eleven provinces "the
    Empire holds what it held"). The first line reads the provinces — and
    the capital and the Emperor, the losses the count cannot see
    (verification round) — the second the field; the third is History's
    judgement and always stands. A Fall, like a Humbled Peace, is always
    the eclipse (`verdict_tier`).
    `VERDICT_TIERS` keeps the canonical lines — the ones a reign that fits
    its tier exactly reads."""
    out = list(lines)
    data = totals(world)
    won = int(data.get("battles_won", 0) or 0)
    lost = int(data.get("battles_lost", 0) or 0)
    held = int(inputs.get("provinces_held", 0) or 0)
    opening = int(inputs.get("opening_provinces", 0) or 0)
    knocked = list(inputs.get("great_powers_knocked_out") or [])
    emperor = str(inputs.get("emperor") or "")
    capital = str(inputs.get("capital") or "")
    capital_lost = bool(capital) and not inputs.get("capital_held", True)
    beaten_somewhere = bool(lost) or capital_lost or emperor in ("captive", "dead")
    # The loss the province count cannot see (verification round: a
    # contested reign "holds what it held" with Paris in Austrian hands; an
    # ascendant one "stands surer" with its Emperor in chains).
    qualifier = ("its Emperor is a prisoner" if emperor == "captive" else
                 f"{capital} is in enemy hands" if capital_lost else "")
    if tier_id == "triumph":
        if not knocked:
            out[1] = "The great powers still stand, but none of them as tall as in 1805."
        if qualifier:
            out[0] = f"Europe has been remade, and it knows it — though {qualifier}."
    elif tier_id == "ascendant":
        if qualifier:
            out[0] = (f"The Empire stands larger than it began, though {qualifier}."
                      if held > opening else
                      f"The Empire stands where it began, though {qualifier}."
                      if held == opening else
                      f"The Empire stands, though {qualifier}.")
        elif held < opening:
            out[0] = "The Empire stands surer than it began, if not larger."
        elif held == opening:
            out[0] = "The Empire stands where it began, and surer of itself."
    elif tier_id == "contested":
        if held < opening:
            out[0] = ("The Empire has given ground it held in 1805, and Europe "
                      "has not accepted the rest.")
        elif qualifier:
            out[0] = (f"The Empire holds {'more than' if held > opening else 'as much as'} "
                      f"it held, though {qualifier}, and Europe has not accepted it.")
        elif held > opening:
            out[0] = "The Empire holds more than it held, and Europe has not accepted it."
        if lost > won:
            out[1] = ("The field has gone against it more often than not, and "
                      "the table is no kinder.")
        elif won == lost:
            out[1] = "Neither the field nor the table has settled anything."
    elif tier_id == "eclipse":
        worse = []
        if held < opening:
            worse.append("smaller")
        if int(inputs.get("treasury", 0) or 0) < 0:
            worse.append("poorer")
        opening_sats = list(inputs.get("satellites_opening") or [])
        if opening_sats and len(inputs.get("satellites_kept") or []) < len(opening_sats):
            worse.append("more alone")
        if worse:
            adj = (worse[0] if len(worse) == 1 else
                   ", ".join(worse[:-1]) + f" and {worse[-1]}")
            out[0] = f"The Empire is {adj} than it began."
        elif inputs.get("humbled"):
            out[0] = "The Empire signed away what its armies had not lost."
        # Name the loss that DROVE the eclipse when the provinces cannot
        # (verification round: "no greater than it began" of an Empire
        # holding 34 provinces of its 28, its Emperor dead or in chains).
        elif emperor == "dead":
            out[0] = "The Empire has lost its Emperor, whatever ground it holds."
        elif emperor == "captive":
            out[0] = ("The Empire has lost its Emperor to his captors, whatever "
                      "ground it holds.")
        elif capital_lost:
            out[0] = f"The Empire has lost {capital}, whatever ground it holds."
        elif held > opening:
            out[0] = "The Empire holds more than it began, and is losing its wars."
        else:
            out[0] = "The Empire is no greater than it began, and no longer feared."
        if not beaten_somewhere:
            out[1] = "Its enemies have learned that it can be made to yield."
    return out


# ════════════════════════════════════════════════════════════════════════
# The campaign summary (R4) and the exile story (Sept 25, 2026).
# ════════════════════════════════════════════════════════════════════════

def build_campaign_summary(world, ending: Dict[str, Any]) -> Dict[str, Any]:
    """The ONE payload GE-2's end screen renders, for every register."""
    data = copy.deepcopy(totals(world))
    verdict = verdict_tier(world)
    summary: Dict[str, Any] = {
        "register": ending.get("register"),
        "title": ending.get("title"),
        "cause_line": ending.get("cause_line"),
        "turn": int(ending.get("turn", 0) or 0),
        "calendar_label": ending.get("calendar_label", ""),
        "nation": _player(world),
        "provinces_held": int(len(world.get_nation_regions(_player(world)) or [])),
        "total_regions": int(len(getattr(world, "regions", {}) or {})),
        "totals": {k: data.get(k) for k in _COUNTERS},
        "greatest_victory": data.get("greatest_victory"),
        "worst_defeat": data.get("worst_defeat"),
        "coalition_names": list(data.get("coalition_names") or []),
        "verdict": {k: verdict[k] for k in ("tier", "title", "lines", "closing", "score")},
        # A save from before GE-1 kept no record until it was loaded: the
        # totals begin on that turn, and the end screen must say so rather
        # than print twenty turns of war as zeros (review round). None for a
        # campaign recorded from its first turn.
        "record_since_turn": data.get("record_since_turn"),
    }
    if ending.get("register") in ("fall", "humbled_peace"):
        summary["epilogue"] = build_exile_story(world, ending, verdict=verdict)
    return summary


# The places a captor sends a deposed Emperor. Britain's is history (the
# Bellerophon, St Helena); the continental courts' are their own state
# prisons, each with an echo the court would enjoy: Austria held Lafayette at
# Olmütz (1794–97); Prussia's Frederick was held at Küstrin by his father;
# Russia kept its state prisoners in Schlüsselburg on the Neva.
_CAPTIVITY = {
    "Britain": ("aboard the Bellerophon, and then to St Helena",
                "a rock in the South Atlantic from which no army marches"),
    "Austria": ("to the fortress of Olmütz",
                "where Austria once kept Lafayette, and knew how to keep a man"),
    "Prussia": ("to the citadel of Küstrin",
                "where Prussia once kept its own crown prince"),
    "Russia": ("to Schlüsselburg on the Neva",
               "where the Tsars keep the prisoners they do not name"),
}

# One line each, in the court's own voice (docs/DIPLOMAT_VOICE_BIBLE.md).
_CAPTOR_VOICE = {
    "Britain": ("Castlereagh writes, without warmth: \"His Majesty's "
                "Government observes that the island is sufficiently remote.\""),
    "Austria": ("Metternich, with perfect politeness: \"A small inconvenience "
                "of residence. The air at Olmütz is said to be bracing.\""),
    "Prussia": ("Hardenberg, stiffly: \"Prussia remembers Jena. Küstrin will "
                "serve.\""),
    "Russia": ("Czartoryski, with sweeping calm: \"History has appointed "
               "Russia the keeper of Europe's peace — and of its prisoners.\""),
}


def _court(world, nation: str) -> str:
    from backend.display_names import with_definite_article
    from backend.game_logic.formations import formed_display_name
    return with_definite_article(formed_display_name(world, nation))


def _Court(world, nation: str) -> str:
    text = _court(world, nation)
    return text[:1].upper() + text[1:]


def _man(name: str) -> str:
    from backend.display_names import humanize_entity_name
    return humanize_entity_name(name)


def _join_names(names: List[str]) -> str:
    names = [n for n in names if n]
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + f" and {names[-1]}"


def _date_of(world, turn: int) -> str:
    """'early July 1807' (the HC-0 label, lower-cased for prose), or
    'turn 44' without an anchor."""
    from backend.game_logic.calendar import calendar_label
    label = calendar_label(getattr(world, "start_date", ""), int(turn))
    if not label:
        return f"turn {int(turn)}"
    return label[:1].lower() + label[1:]


def _on(date: str) -> str:
    """'In early July 1807' / 'On turn 44'."""
    return f"On {date}" if date.startswith("turn ") else f"In {date}"


def build_exile_story(world, ending: Dict[str, Any],
                      verdict: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """The epilogue of a Fall (or a Humbled Peace) — three to six paragraphs,
    every clause derived from a fact on the record, with its source named in
    `facts`. Deterministic (GR6)."""
    from backend.game_logic import fall
    player = _player(world)
    verdict = verdict or verdict_tier(world)
    cause = ending.get("cause")
    detail = ending.get("detail") or {}
    data = totals(world)
    date = _date_of(world, ending.get("turn", 0))
    when = _on(date)
    facts: Dict[str, Any] = {"marshals": [], "courts": [], "battles": [],
                             "sources": {}}
    paragraphs: List[str] = []
    sov = fall.sovereign_of(world, player)
    sov_name = (sov.name if sov is not None else str(detail.get("sovereign") or ""))
    captor = str(getattr(sov, "captured_by", "") or "") if sov is not None else ""

    # ── 1. the fall, and the place ────────────────────────────────────
    if cause == CAUSE_EAGLE_FALLS:
        variant = "funeral"
        where = str(detail.get("location") or "")
        victor = str(detail.get("victor") or "")
        how = {"charge": "cut down in a charge",
               "bombardment": "struck by a cannonball in the barrage",
               }.get(str(detail.get("cause") or ""), "killed in the fighting")
        lead = (f"{when}, at {where}, the Emperor was {how}"
                + (f", his corps annihilated by {_court(world, victor)}" if victor else "")
                + ". France has no heir; within the week the Senate declared "
                  "the Empire at an end.")
        if victor:
            facts["courts"].append(victor)
        facts["sources"]["death"] = "fallen_marshals tombstone + the eagle_falls ending detail"
        capital = world.get_nation_capital(player) or ""
        cap_region = getattr(world, "regions", {}).get(capital) if capital else None
        if cap_region is not None and cap_region.controller == player:
            lead += (f" He lay in state in {capital}, and the city that had cheered "
                     f"his coronation walked past the bier in silence.")
        elif cap_region is not None and cap_region.controller:
            holder = cap_region.controller
            facts["courts"].append(holder)
            lead += (f" There was no state funeral: {capital} was in "
                     f"{_court(world, holder)}'s hands, and he was buried where "
                     f"he fell.")
        paragraphs.append(lead)
    elif cause == CAUSE_HUMBLED:
        variant = "humbled"
        parties = [p for p in (detail.get("with") or []) if p]
        facts["courts"].extend(parties)
        clauses = []
        if detail.get("capital_ceded"):
            clauses.append(f"{detail.get('capital')} itself")
        home = detail.get("homeland_ceded") or []
        if home and not detail.get("capital_ceded"):
            clauses.append(f"{len(home)} of the {int(detail.get('homeland_total') or 0)} "
                           f"provinces of the homeland")
        if detail.get("vassal_of"):
            facts["courts"].append(detail["vassal_of"])
            clauses.append(f"the crown's own sovereignty, to "
                           f"{_court(world, detail['vassal_of'])}")
        signed_away = _join_names(clauses) or "what the war had not already taken"
        paragraphs.append(
            f"{when}, the Emperor signed. The peace with "
            f"{_join_names([_court(world, p) for p in parties])} gave away "
            f"{signed_away}. He kept his throne; the reign goes on, humbled, "
            f"under terms every court in Europe has read.")
        facts["sources"]["treaty"] = "the humbled_peace ending detail (the signed terms)"
    elif captor:
        variant = "captivity"
        facts["courts"].append(captor)
        place, gloss = _CAPTIVITY.get(captor, (
            f"to a fortress of {_court(world, captor)}", "and the doors were locked"))
        grace = int(cfg(world, "captivity_grace_turns", fall.CAPTIVITY_GRACE_TURNS))
        taken = int(getattr(sov, "captured_turn", -1) or -1) if sov is not None else -1
        _taken_date = _date_of(world, taken) if taken >= 0 else ""
        taken_clause = ((f", taken {'on' if _taken_date.startswith('turn ') else 'in'} "
                         f"{_taken_date},") if _taken_date else "")
        # How long he was HELD, not the clock's count — a truce pauses the
        # clock, and the sentence names both dates (review round: "taken in
        # late September 1805 … for 10 turns" when he was held 17).
        held_for = int(detail.get("held_turns") or 0) or grace
        from backend.display_names import plural as _plural
        opening = (f"{when}, the Empire fell. The Emperor{taken_clause} had been "
                   f"a prisoner of {_court(world, captor)} for "
                   f"{_plural(held_for, 'turn')}, and "
                   if cause == CAUSE_CHAINS else
                   f"{when}, the Empire fell. The Emperor was a prisoner of "
                   f"{_court(world, captor)}, and ")
        paragraphs.append(
            opening + "Paris stopped waiting. "
            + f"{_Court(world, captor)} sent him {place} — {gloss}.")
        facts["sources"]["captivity"] = "the sovereign's captured_by / captured_turn"
    else:
        variant = "abdication"
        capital = world.get_nation_capital(player) or ""
        cap_region = getattr(world, "regions", {}).get(capital) if capital else None
        holder = (cap_region.controller if cap_region is not None
                  and cap_region.controller and cap_region.controller != player else "")
        lost_to = data.get("lost_to") or {}
        victor = holder or (max(sorted(lost_to), key=lambda n: lost_to[n])
                            if lost_to else "")
        if victor:
            facts["courts"].append(victor)
        realm, sword = bool(detail.get("realm")), bool(detail.get("sword"))
        # Worded by the count, as the cause line is (verification round:
        # "with no soil left to govern" beside "reduced to Paris alone").
        held = [str(r) for r in (detail.get("held") or []) if r]
        soil = (f"with only {held[0]} left to govern" if held
                else "with no soil left to govern")
        why = (f"{soil} and no sword left to hold it"
               if (realm and sword) else
               soil if realm else
               "with no army left to hold the realm" if sword else
               "with the war lost")
        paragraphs.append(
            f"{when}, {why}, the Emperor signed his abdication at "
            f"Fontainebleau. "
            + (f"{_Court(world, victor)} and its allies sent him to Elba — "
               if victor else "The Allies sent him to Elba — ")
            + "a small island, a small court, and a sovereign who had once "
              "governed a continent.")
        facts["sources"]["abdication"] = ("the capital's controller / "
                                          "campaign_totals.lost_to")

    # ── 2. the men ────────────────────────────────────────────────────
    marshals = getattr(world, "marshals", {}) or {}
    ours = [m for m in marshals.values()
            if m.nation == player and not getattr(m, "is_sovereign", False)]

    def _bond(m) -> int:
        try:
            return int(m.get_relationship(sov_name)) if sov_name else 0
        except Exception:
            return 0

    def _trust(m) -> int:
        try:
            return int(m.trust.value)
        except Exception:
            return 50

    free_men = [m for m in ours if not getattr(m, "captured_by", "")]
    loyal = sorted([m for m in free_men if _bond(m) >= 1 or _trust(m) >= 70],
                   key=lambda m: (-_bond(m), -_trust(m), m.name))[:2]
    broke = sorted([m for m in free_men if m not in loyal
                    and (_bond(m) <= -2 or _trust(m) <= 30)],
                   key=lambda m: (_bond(m), _trust(m), m.name))[:1]
    tombs = getattr(world, "fallen_marshals", {}) or {}
    # Only a battlefield death is "fallen" (the generals' death-odds memo,
    # §5(c)(i)): a starved-out, interned or dismissed corps is not a man
    # killed in the field, and the epilogue must never say it is.
    fallen = sorted(
        [(name, t) for name, t in tombs.items()
         if isinstance(t, dict) and t.get("nation") == player
         and not t.get("sovereign")
         and t.get("cause") in BATTLEFIELD_CAUSES],
        key=lambda nt: (int(nt[1].get("turn", 0)), nt[0]))[:3]
    captives = sorted(m.name for m in ours if getattr(m, "captured_by", ""))[:2]
    men: List[str] = []
    if loyal:
        names = _join_names([_man(m.name) for m in loyal])
        facts["marshals"].extend(m.name for m in loyal)
        if variant == "funeral":
            men.append(f"{names} stood at the bier.")
        elif variant == "humbled":
            men.append(f"{names} stayed at his side through the signing.")
        elif variant == "captivity":
            men.append(f"{names} asked to share his captivity, and "
                       f"{'was' if len(loyal) == 1 else 'were'} refused.")
        else:
            men.append(f"{names} followed him to the boat.")
    if fallen:
        parts = []
        for name, t in fallen:
            facts["marshals"].append(name)
            where = str(t.get("location") or "")
            parts.append(f"{_man(name)} at {where}" if where else _man(name))
        men.append(f"Some had not lived to see it: {_join_names(parts)} had "
                   f"fallen before him.")
    if captives:
        facts["marshals"].extend(captives)
        men.append(f"{_join_names([_man(n) for n in captives])} "
                   f"{'was' if len(captives) == 1 else 'were'} still "
                   f"{'a prisoner' if len(captives) == 1 else 'prisoners'} "
                   f"of the enemy.")
    if broke:
        m = broke[0]
        facts["marshals"].append(m.name)
        men.append(f"{_man(m.name)} had long since stopped answering his letters.")
    if men:
        paragraphs.append(" ".join(men))
        facts["sources"]["men"] = ("marshals' relationships to the sovereign and "
                                   "trust; fallen_marshals tombstones; captured_by")

    # ── 3. the record ─────────────────────────────────────────────────
    record: List[str] = []
    fought = int(data.get("battles_fought", 0))
    if fought:
        record.append(
            f"In {fought} {'battle' if fought == 1 else 'battles'} the Empire "
            f"won {int(data.get('battles_won', 0))} and lost "
            f"{int(data.get('battles_lost', 0))}; "
            f"{int(data.get('men_inflicted', 0)):,} of the enemy fell against "
            f"{int(data.get('men_lost', 0)):,} of our own.")
    best = data.get("greatest_victory")
    if isinstance(best, dict) and best.get("name"):
        facts["battles"].append(best["name"])
        record.append(f"{_battle_subject(best['name'])} "
                      f"({_date_of(world, best.get('turn', 0))}) "
                      f"was the high-water mark.")
    worst = data.get("worst_defeat")
    if isinstance(worst, dict) and worst.get("name"):
        facts["battles"].append(worst["name"])
        record.append(f"{_battle_subject(worst['name'])} was the worst day.")
    lost_regions = list(data.get("lost_regions") or [])
    region_to = {str(r): str(c) for r, c in
                 (data.get("lost_region_to") or {}).items() if c}
    # The courts are ranked in the SAME unit as the count (verification
    # round): distinct provinces, each credited to the court that took it
    # last. A record that cannot say that — kept before the distinct list or
    # its attribution existed — counts the losses instead, the unit it kept.
    partial = bool(data.get("lost_regions_partial")) or any(
        r not in region_to for r in lost_regions)
    if partial:
        losses = int(data.get("provinces_lost", 0) or 0)
        counts = {n: int(c) for n, c in (data.get("lost_to") or {}).items()
                  if int(c) > 0}
    else:
        losses = len(lost_regions)
        counts = {}
        for region_name in lost_regions:
            court = region_to[region_name]
            counts[court] = counts.get(court, 0) + 1
    if losses and counts:
        # "most of them" only when one court truly took most (review round:
        # "1 province … most of them", and a 2–2 tie named one court).
        ranked = sorted(counts, key=lambda n: (-counts[n], n))
        best_count = counts[ranked[0]]
        leaders = [n for n in ranked if counts[n] == best_count]
        facts["courts"].extend(leaders)
        if losses == 1:
            record.append(f"One province was lost, to {_court(world, ranked[0])}.")
        elif partial:
            head = f"Provinces were lost to the enemy {losses} times"
            if len(counts) == 1:
                record.append(f"{head}, every time to {_court(world, ranked[0])}.")
            elif len(leaders) == 1:
                record.append(f"{head}, most often to {_court(world, ranked[0])}.")
            elif len(leaders) == 2:
                record.append(f"{head}, as often to {_court(world, leaders[0])} "
                              f"as to {_court(world, leaders[1])}.")
            else:
                record.append(f"{head}, to "
                              f"{_join_names([_court(world, n) for n in leaders])} "
                              f"alike.")
        elif len(counts) == 1:
            record.append(f"{losses} provinces were lost to the enemy, all of them "
                          f"to {_court(world, ranked[0])}.")
        elif len(leaders) == 1:
            record.append(f"{losses} provinces were lost to the enemy; "
                          f"{_court(world, ranked[0])} took the most.")
        elif len(leaders) == 2:
            record.append(f"{losses} provinces were lost to the enemy, as many to "
                          f"{_court(world, leaders[0])} as to "
                          f"{_court(world, leaders[1])}.")
        else:
            record.append(f"{losses} provinces were lost to the enemy, shared among "
                          f"{_join_names([_court(world, n) for n in leaders])}.")
    names = list(data.get("coalition_names") or [])
    faced = int(data.get("coalitions_faced", 0))
    if faced:
        last = names[-1] if names else ""
        if faced == 1:
            record.append("One coalition stood against him"
                          + (f" — {_coalition_name(last)}." if last else "."))
        else:
            record.append(f"{faced} coalitions stood against him"
                          + (f" — the last, {_coalition_name(last)}." if last else "."))
    peaces = int(data.get("peaces_signed", 0))
    if peaces:
        humbled = has_ending(world, CAUSE_HUMBLED) and variant != "humbled"
        record.append(f"He signed {peaces} {'peace' if peaces == 1 else 'peaces'}"
                      + (", and one of them humbled him." if humbled else "."))
    since = data.get("record_since_turn")
    if record and since is not None:
        record.insert(0, f"(The record was kept from {_date_of(world, int(since))} "
                         f"only.)")
    if record:
        paragraphs.append(" ".join(record))
        facts["sources"]["record"] = "campaign_totals (written at the moment of each event)"

    # ── 4. the verdict, and one voice ─────────────────────────────────
    closing = verdict.get("closing") or ""
    voice = ""
    if variant == "captivity" and captor in _CAPTOR_VOICE:
        voice = _CAPTOR_VOICE[captor]
    elif variant == "funeral":
        voice = "Berthier closed the last order book and did not open another."
    elif variant == "humbled":
        voice = ("Talleyrand, leaving the signing: \"It is not a peace, Sire. "
                 "It is a truce with better handwriting.\"")
    else:
        voice = ("Talleyrand, who had served every government France had ever "
                 "had, served the next one too.")
    paragraphs.append(" ".join(p for p in (closing, voice) if p))
    facts["sources"]["verdict"] = "verdict_tier at the moment of the ending"
    facts["courts"] = sorted(set(facts["courts"]))
    facts["marshals"] = sorted(set(facts["marshals"]))
    return {"variant": variant, "paragraphs": paragraphs, "facts": facts}


def _coalition_name(name: str) -> str:
    """Mid-sentence form: "the Third Coalition", and a name authored with
    its own article is lower-cased ("the Fourth Austrian Coalition", never
    "— the last, The Fourth…")."""
    name = str(name or "").strip()
    if not name:
        return ""
    if name.lower().startswith("the "):
        return "the " + name[4:]
    return f"the {name}"


def _cap(text: str) -> str:
    """A sentence begins with a capital ("The assault on Vienna", not "the
    assault on Vienna" — the pipeline's fallback battle names are
    mid-sentence phrases)."""
    text = str(text or "")
    return text[:1].upper() + text[1:]


def _battle_subject(name: str) -> str:
    """A battle's name as the subject of a sentence: capitalised, and with
    its article (verification round: `compose_battle_name` gives "Battle of
    Swabia" / "Second Battle of X" bare, so "Battle of Munich was the worst
    day." sat beside "The Great Battle of Swabia … was the high-water
    mark.")."""
    text = _cap(name)
    low = text.lower()
    if not low.startswith("the ") and "battle of " in low:
        return "The " + text
    return text
