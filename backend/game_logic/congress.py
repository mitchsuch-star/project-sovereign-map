"""GE-3 "The Congress of Paris" — the victory arm (ENDGAME_PLAN §2, RULED).

Napoleon's problem was never conquest; it was that Europe would not
RECOGNIZE the conquest. The ending is that problem made playable:

1. **Title** (GE-1, `game_end.titled_provinces`): conquests count only when
   settled — homeland, ceded by a treaty the loser signed, held twelve quiet
   turns, or a client's soil.
2. **The summons** (`summon`): with `hold_titled` (45 — 50 until GE-V, see
   ENDGAME_PLAN 2.8) titled provinces the
   Emperor may summon the Congress — 2 diplomatic points and 1
   administrative action, and it cannot be undone.
3. **The table** (`answer`, `price`): every great power answers — RECOGNIZES
   / REFUSES / SUES / SHUT OUT / GONE — and keeps answering every turn, with
   its reason and its PRICE on a public table. The table is the live
   projection of the same function the tick applies, so what it shows is
   what the eighth turn will read (shown = applied).
4. **The sitting** (`process_end_of_turn`): eight turns. Refusal has teeth
   (the pressure readers below), recognition has a price, the marshals and
   the satellites present their bills, and the HOLD (`hold_conditions`) must
   stand at every end turn from the summons.
5. **The Imperial Peace**: on the eighth turn, hold intact, every great
   power recognizing, shut out or gone → `game_end.record_ending(world,
   "victory", CAUSE_IMPERIAL_PEACE)`. Otherwise the Congress dissolves —
   alarm, a cooldown, a grudge, the marshals' expectation — and can be
   summoned again. E1, the Universal Monarchy: with no great power left
   standing, the Imperial Peace needs no Congress.

ONE serialized field, `world.congress` (None until the first ratification
with a great power or the first summons). Every hook elsewhere is DORMANT
BY CONSTRUCTION when no Congress sits: the ambient board never reaches 50
titled provinces, never summons and never meets E1, so `BASELINE_SERIES`
and M1–M7 cannot move (the attribution is measured, not asserted —
`tools/_ge3_series_arms.py`).

GR5: the Congress is the player's verb (the `game_end` precedent) — the
answers, the hold and the ending are read for the player's bloc only. The
pressure it puts on AI courts rides the SHARED systems (intent, the
coalition, the treasury transfer) unchanged. STAYS PLAYER-ONLY, written:
the refusal term, the lowered gate, the London subsidy and the bills.
"""

from __future__ import annotations

import math
import re as _re
from typing import Any, Dict, Iterable, List, Optional

# ════════════════════════════════════════════════════════════════════════
# Levers — module-level booleans, read at CALL time (the series-arm idiom:
# `tools/_ge3_series_arms.py` flips them in a child process, never by
# editing source).
# ════════════════════════════════════════════════════════════════════════

THE_CONGRESS_SITS = True              # the whole mechanic (summons, tick, surfaces)
THE_CONGRESS_HARDENS_REFUSERS = True  # intent +15/turn of refusal, Revanche weight
THE_CONGRESS_LOWERS_THE_GATE = True   # coalition gate 60 → 40, the refuser arm, the join
LONDON_FUNDS_THE_REFUSERS = True      # the paymaster at the Congress
THE_BILLS_COME_DUE = True             # petitions at the summons, ×1.5 rentes, ×2 stakes
THE_UNIVERSAL_MONARCHY = True         # E1 — no great power left to answer

# ════════════════════════════════════════════════════════════════════════
# The numbers (ENDGAME_PLAN §2.7). Every one is read through
# `game_end.cfg(world, key, DEFAULT)` from the scenario's `campaign_end`
# block (a GE-1 save carries the old four-key block and falls back here).
# All in-band tunable; the SHAPE is the ruling.
# ════════════════════════════════════════════════════════════════════════

HOLD_TITLED = 45  # GE-V (Sept 25, 2026): 50 -> 45 by ENDGAME_PLAN 2.8's rule — the played reach measured 41 at best
CONGRESS_TURNS = 8
RECOGNITION_THRESHOLD = 50
REFUSER_WEIGHT_PER_TURN = 15
CONGRESS_ALARM_GATE = 40
HOLD_ALARM_CEILING = 80
# VP-R1 P2 (September 25, 2026, `docs/audits/VP_R1_PROBES_2026_09_25.md`):
# 60 was unreachable from play. The Continent has 26 authored ports and the
# Pressburg shape minus the fixture's gifts closes 11 (42%); every Congress
# signatory in the System would close 15 (58%), and 16 needs a war on the
# Pope or on Denmark. 50% = 13 is reachable from a beaten Austria's forced
# alliance plus one walk-in, or two signatories' ports. The scenario key
# `campaign_end.cs_shutout_pct` carries the same number (in-band tunable).
CS_SHUTOUT_PCT = 50
SUE_SCORE = -40
SWEETENER_PER_1000 = 10
SWEETENER_CAP = 20
DISSOLVE_ALARM = 15
CONGRESS_COOLDOWN = 10

# Constants the plan fixes in prose (not scenario keys).
SUMMON_DP_COST = 2
SWEETENER_DP_COST = 1                 # the instrument verbs' price (INSTRUMENT_DP_COST)
BEATEN_WINDOW = 15                    # "beaten by France within 15 turns"
WEARINESS_MARK = 60                   # "war weariness ≥ 60"
WEARINESS_BONUS = 10
BEATEN_BONUS = 10
DESIGN_TERM = 12                      # ±12 — the NA-2 AGENDA_ACCEPT_ADVANCE magnitude
RECOGNITION_JITTER = 3                # ±3 through the campaign-seed helpers
RECOGNITION_TREATY_BONUS = {
    "ALLIANCE": 20,
    "DEFENSIVE_ALLIANCE": 10,
    "NON_AGGRESSION": 5,
    "OPEN_BORDERS": 5,
}
# The hegemony-fear floor for a court whose active design is NOT a
# contain design (§2.4 "Russia's arbiter_of_europe bites here": the
# arbiter's authored floor, 0.33, bites early; every other court fears only
# a larger bloc). In-band tunable.
FEAR_FLOOR_DEFAULT = 0.45
# "a declaration follows within 3–4 turns unless it recognizes": a refuser
# at peace that has refused this many end turns while a coalition already
# stands against France JOINS it (the War of the Congress — the coalition
# route, §16.2: player-targeted designs fight through the coalition). With
# no coalition standing, the lowered gate brews one (BREWING_COUNTDOWN 3).
WAR_AFTER_REFUSALS = 3
REVANCHE_WEIGHT = 10                  # "Refusers' Revanche designs get +weight"
LONDON_SUBSIDY = 200                  # "+200g/turn" to every other refuser
PEACE_DIVIDEND = 1.5                  # the reward rail's rentes during the sitting
PETITION_STAKES = 2                   # a client petition's loyalty stakes
REBELLION_BRINK = 10                  # vassal.py's VASSAL_REBELLION_IMMINENT line
GRUDGE_TURNS = 10                     # a refuser's grudge after a dissolution
GRUDGE_PER_REFUSER = 1                # +1 threat a turn each, inside AGENDA_GRUDGE_CAP

# Stances.
RECOGNIZES = "RECOGNIZES"
REFUSES = "REFUSES"
SUES = "SUES"
SHUT_OUT = "SHUT OUT"
GONE = "GONE"
STANCES = (RECOGNIZES, REFUSES, SUES, SHUT_OUT, GONE)
SATISFIED = (RECOGNIZES, SHUT_OUT, GONE)
# The end screen's words for a court at the Imperial Peace (ENDGAME_PLAN §4).
END_SCREEN_STANCE = {RECOGNIZES: "SIGNED", SHUT_OUT: "SHUT OUT", GONE: "GONE"}

# Statuses of `world.congress["status"]`.
SITTING = "sitting"
DISSOLVED = "dissolved"
CONCLUDED = "concluded"
ENDED = "ended"          # a Fall ended the campaign while it sat (review #49)

# The courts' seats — the metonym the prose uses ("Vienna answers the
# Congress with cannon"). Display only; a court without one is named.
COURT_SEATS = {
    "Britain": "London",
    "Russia": "St Petersburg",
    "Austria": "Vienna",
    "Prussia": "Berlin",
}

CABINET_HINT = "summon from the Cabinet (F1)"
SUMMON_COMMAND = "summon the congress"


# ════════════════════════════════════════════════════════════════════════
# The record and the small reads.
# ════════════════════════════════════════════════════════════════════════

def _cfg(world, key: str, default):
    from backend.game_logic import game_end
    return game_end.cfg(world, key, default)


def _int(world, key: str, default: int) -> int:
    try:
        return int(_cfg(world, key, default))
    except (TypeError, ValueError):
        return int(default)


def hold_titled(world) -> int:
    return _int(world, "hold_titled", HOLD_TITLED)


def congress_turns(world) -> int:
    return max(1, _int(world, "congress_turns", CONGRESS_TURNS))


def recognition_threshold(world) -> int:
    return _int(world, "recognition_threshold", RECOGNITION_THRESHOLD)


def sue_score(world) -> int:
    return _int(world, "sue_score", SUE_SCORE)


def dissolve_alarm(world) -> int:
    return max(0, _int(world, "dissolve_alarm", DISSOLVE_ALARM))


def cooldown_turns(world) -> int:
    return max(0, _int(world, "congress_cooldown", CONGRESS_COOLDOWN))


def armed(world) -> bool:
    """The Congress exists only where the scenario armed the endings (R7):
    the tutorial and the bare flag world never see it."""
    if not THE_CONGRESS_SITS or world is None:
        return False
    from backend.game_logic import game_end
    return game_end.endings_armed(world)


def record(world) -> Optional[Dict[str, Any]]:
    value = getattr(world, "congress", None)
    return value if isinstance(value, dict) else None


def _store(world) -> Dict[str, Any]:
    value = record(world)
    if value is None:
        value = {}
        world.congress = value
    return value


def sitting(world) -> bool:
    """The one guard every hook passes through (cheap: an attribute read
    and a key compare before anything else)."""
    value = getattr(world, "congress", None)
    if not isinstance(value, dict) or value.get("status") != SITTING:
        return False
    return armed(world)


def _player(world) -> str:
    return str(getattr(world, "player_nation", "") or "")


def _turn(world) -> int:
    return int(getattr(world, "current_turn", 0) or 0)


def day_of_sitting(world) -> int:
    """0 on the summons turn (the powers gather), 1..N on the sitting's
    turns — the end of turn `summoned + N` is the eighth answer."""
    c = record(world) or {}
    return max(0, _turn(world) - int(c.get("summoned_turn", _turn(world))))


def great_powers(world) -> List[str]:
    from backend.game_logic import game_end
    return list(game_end.great_powers(world))


def _display(nation: str) -> str:
    from backend.display_names import display_nation
    return display_nation(nation)


def seat(world, nation: str) -> str:
    return COURT_SEATS.get(nation) or _display(nation)


def court_gone(world, court: str) -> str:
    """'eliminated' / 'vassal' (of the player's chain) / '' — a great power
    that is gone is counted as recognizing by construction (§2.3)."""
    try:
        if not world.get_nation_regions(court):
            return "eliminated"
    except Exception:
        return ""
    player = _player(world)
    if court != player and world._top_overlord(court) == player:
        return "vassal"
    return ""


def no_great_power_stands(world) -> bool:
    powers = great_powers(world)
    return bool(powers) and all(court_gone(world, p) for p in powers)


def titled(world) -> Dict[str, Any]:
    from backend.game_logic import game_end
    view = game_end.titled_provinces(world, _player(world))
    return {"titled": list(view.get("titled") or []),
            "held": list(view.get("held") or []),
            "count": len(view.get("titled") or []),
            "needed": hold_titled(world)}


def _capital_held(world) -> bool:
    player = _player(world)
    capital = world.get_nation_capital(player) or ""
    region = getattr(world, "regions", {}).get(capital) if capital else None
    return bool(region is not None and region.controller == player)


def _emperor_free(world) -> bool:
    from backend.game_logic import fall
    sov = fall.sovereign_of(world, _player(world))
    return sov is None or not getattr(sov, "captured_by", "")


def _satellites_on_the_brink(world) -> List[str]:
    player = _player(world)
    out = []
    for name, row in sorted((getattr(world, "vassals", {}) or {}).items()):
        if not isinstance(row, dict) or row.get("lord") != player:
            continue
        if int(row.get("loyalty", 0) or 0) <= REBELLION_BRINK:
            out.append(name)
    return out


def _alarm(world) -> int:
    from backend.game_logic.coalition import displayed_threat
    return int(displayed_threat(world))


def alarm_road(world) -> str:
    """SR-1c: what lowers Europe's alarm, and by how much — the decay the
    coalition tick applies (`_calculate_threat_decay`: one, plus one for
    each court at peace with us, at most three, plus one under the
    Continental System) and the league-spent rule (a treaty that dissolves
    a league halves it). Read off the same helpers the tick uses."""
    from backend.game_logic import coalition as _co
    decay = int(_co._calculate_threat_decay(world))
    cs = ""
    if len(getattr(world, "continental_system_members", []) or []) >= 2:
        cs = ", plus one for the Continental System"
    parts = [f"it falls {decay} a turn (one, plus one for each court at peace "
             f"with us, at most three{cs})"]
    if getattr(_co, "THE_LEAGUE_SPENDS_ITS_ALARM", False):
        parts.append("a treaty that dissolves a league halves it")
    return "; ".join(parts)


def cooldown_left(world) -> int:
    c = record(world) or {}
    if c.get("status") != DISSOLVED or c.get("dissolved_turn") is None:
        return 0
    return max(0, int(c["dissolved_turn"]) + cooldown_turns(world) - _turn(world))


def imperial_peace_signed(world) -> bool:
    from backend.game_logic import game_end
    return game_end.has_ending(world, game_end.CAUSE_IMPERIAL_PEACE)


def imperial_peace_route(world) -> str:
    """'congress' / 'universal_monarchy' — how the stamped Imperial Peace was
    won ('' before it). Review #46: every surface that says "Europe signed at
    Paris" branches on it."""
    from backend.game_logic import game_end
    for rec in game_end.endings(world):
        if rec.get("cause") == game_end.CAUSE_IMPERIAL_PEACE:
            return str((rec.get("detail") or {}).get("route") or "congress")
    return ""


# ════════════════════════════════════════════════════════════════════════
# The summons — the gate terms and the act (§2.3).
# ════════════════════════════════════════════════════════════════════════

def gate_terms(world) -> List[Dict[str, Any]]:
    """The summons' honest-availability terms, in the order the executor
    refuses them (the administrative action first — `executor.py`'s
    generic pre-check runs before the sub-executor — the diplomatic points
    last). Conditional terms (a Congress already sitting, the Imperial
    Peace already signed, no great power left) appear only when they bite.
    `summon_refusal` reads the SAME list (drift-pinned)."""
    if not armed(world):
        return []
    from backend.display_names import plural
    terms: List[Dict[str, Any]] = []
    from backend.game_logic import game_end as _ge
    if _ge.terminal_ending(world) is not None:
        terms.append({"key": "fallen", "met": False,
                      "text": "the campaign has ended",
                      "breach": "the campaign has ended",
                      "refusal": "The campaign has ended — no Congress will sit."})
    admin = int(getattr(world, "admin_actions_remaining", 0) or 0)
    terms.append({"key": "admin", "met": admin >= 1,
                  "text": f"1 administrative action (you have {admin})",
                  "refusal": "No administrative action remains this turn — "
                             "the summons is an act of state."})
    if imperial_peace_signed(world):
        terms.append({"key": "signed", "met": False,
                      "text": "the Imperial Peace is already signed",
                      "refusal": "The Imperial Peace is signed — there is "
                                 "no Congress left to summon."})
    c = record(world) or {}
    if c.get("status") == SITTING:
        day = day_of_sitting(world)
        terms.append({"key": "sitting", "met": False,
                      "text": "the Congress already sits",
                      "refusal": ("The Congress already sits — "
                                  + (f"turn {day} of {congress_turns(world)}."
                                     if day >= 1 else
                                     "the powers are gathering at Paris."))})
    if no_great_power_stands(world):
        terms.append({"key": "monarchy", "met": False,
                      "text": "no great power remains to answer",
                      "breach": ("no great power remains — the Universal "
                                 "Monarchy needs no Congress"),
                      "refusal": "No great power remains to answer — the "
                                 "Universal Monarchy needs no Congress; it is "
                                 "proclaimed at this end turn."})
    view = titled(world)
    need, have = view["needed"], view["count"]
    terms.append({"key": "titled", "met": have >= need,
                  "text": f"{need} titled provinces ({have} of {need})",
                  "refusal": (f"The Congress cannot be summoned on {have} "
                              f"titled provinces — {need} are needed "
                              f"({need - have} more to win and settle).")})
    player = _player(world)
    capital = world.get_nation_capital(player) or "the capital"
    terms.append({"key": "capital", "met": _capital_held(world),
                  "text": f"{capital} held",
                  "breach": f"{capital} is not ours",
                  "refusal": f"{capital} is not ours — no Congress sits in "
                             f"an occupied capital."})
    terms.append({"key": "emperor", "met": _emperor_free(world),
                  "text": "the Emperor free",
                  "breach": "the Emperor is a prisoner",
                  "refusal": "The Emperor is a prisoner — a captive cannot "
                             "summon Europe."})
    brink = _satellites_on_the_brink(world)
    terms.append({"key": "satellites", "met": not brink,
                  "text": "no satellite on the brink of rebellion",
                  "breach": ("a satellite on the brink of rebellion ("
                             + ", ".join(_display(v) for v in brink) + ")"),
                  "refusal": ("A satellite stands on the brink of rebellion ("
                              + ", ".join(_display(v) for v in brink)
                              + ") — settle it first.") if brink else ""})
    alarm = _alarm(world)
    ceiling = _int(world, "hold_alarm_ceiling", HOLD_ALARM_CEILING)
    # SR-1c: the term names what lowers the alarm and by how much.
    _road = alarm_road(world)
    terms.append({"key": "alarm", "met": alarm < ceiling,
                  "text": f"Europe's alarm below {ceiling} (now {alarm} — {_road})",
                  "road": _road,
                  "breach": (f"Europe's alarm too high ({alarm} — the Congress "
                             f"needs it below {ceiling})"),
                  "refusal": (f"Europe's alarm stands at {alarm} — the Congress "
                              f"would dissolve at its first end turn (the hold "
                              f"needs it below {ceiling}).")})
    left = cooldown_left(world)
    terms.append({"key": "cooldown", "met": left <= 0,
                  "text": (f"no Congress dissolved within "
                           f"{cooldown_turns(world)} turns"
                           + (f" ({plural(left, 'turn')} to wait)" if left > 0 else "")),
                  "refusal": (f"The last Congress dissolved on turn "
                              f"{c.get('dissolved_turn')} — the powers will not "
                              f"answer another summons for "
                              f"{plural(left, 'turn')}.") if left > 0 else ""})
    dp = int(getattr(world, "diplomatic_points", 0) or 0)
    terms.append({"key": "dp", "met": dp >= SUMMON_DP_COST,
                  "text": f"{SUMMON_DP_COST} diplomatic points (you have {dp})",
                  "refusal": (f"The summons costs {SUMMON_DP_COST} diplomatic "
                              f"points; {dp} remain.")})
    return terms


def summon_refusal(world, *, skip_admin: bool = True) -> Optional[str]:
    """The first unmet gate term's refusal, or None. `skip_admin`: the
    sub-executor is reached only after `executor.py` has already charged
    the administrative pre-check, so it does not ask again."""
    if not armed(world):
        return ("There is no Congress of Paris in this campaign — its rules "
                "are not authored here.")
    for term in gate_terms(world):
        if skip_admin and term["key"] == "admin":
            continue
        if not term["met"]:
            return term.get("refusal") or f"The summons needs {term['text']}."
    return None


def summon(world) -> Dict[str, Any]:
    """The act (the executor charges the DP and the administrative action
    after this returns success). Opens the sitting, takes the first
    answers, presents the bills, and logs beat 1."""
    refusal = summon_refusal(world)
    if refusal:
        return {"success": False, "message": refusal}
    c = _store(world)
    number = int(c.get("number", 0) or 0) + 1
    turn = _turn(world)
    c.update({
        "number": number,
        "status": SITTING,
        "summoned_turn": turn,
        "ends_turn": turn + congress_turns(world),
        "answers": {},
        "strip": [],
        "withdrawn": {},
        "sweeteners": {},
        "declared": [],
        "lost": [],
        "rebellions": [],
        "shut_out_broken": False,
        "subsidized": [],
        "warned": [],
        "warned_turn": {},
        "joined": {},
        "defections": {},
        "petition_owed": False,
        "sued": {},
        "signed_at_table": {},
        "dissolved_turn": None,
        "dissolve_reason": "",
        "refusers": [],
    })
    table = _take_answers(world, first=True)
    _invalidate_intent(world)
    world.log_event({
        "type": "congress",
        "phase": "summoned",
        "nation": _player(world),
        "number": number,
        "ends_turn": int(c["ends_turn"]),
        "stances": {k: v["stance"] for k, v in table.items()},
        "message": "The Emperor summons the powers to Paris.",
    })
    bills = present_the_bills(world)
    lines = []
    for court in great_powers(world):
        row = table.get(court) or {}
        stance = row.get("stance", "")
        reason = row.get("reason", "")
        lines.append(f"{_display(court)} {stance}" + (f" — {reason}" if reason
                                                      and stance in (REFUSES, SUES)
                                                      else ""))
    message = (
        f"The Emperor summons the powers of Europe to Paris. The Congress "
        f"sits for {congress_turns(world)} turns, to the end of turn "
        f"{c['ends_turn']}. " + "; ".join(lines) + ". "
        f"Hold {hold_titled(world)} titled provinces, "
        f"{world.get_nation_capital(_player(world)) or 'the capital'} and the "
        f"Emperor's freedom — and declare no war.")
    if bills:
        message += " " + " ".join(bills)
    return {"success": True, "message": message, "congress": number,
            "stances": {k: v["stance"] for k, v in table.items()}}


def present_the_bills(world) -> List[str]:
    """§2.3/§2.5 — the marshals and the satellites present their bills at
    the summons. Returns the sentences for the summons' own report."""
    if not THE_BILLS_COME_DUE:
        return []
    out: List[str] = []
    said = _collective_petition(world)
    if said:
        out.append(said)
    from backend.game_logic import vassal as _vassal
    presented = _vassal.present_pending_asks(world, _player(world))
    if presented:
        from backend.display_names import plural
        out.append(f"{plural(len(presented), 'satellite')} "
                   f"present{'s' if len(presented) == 1 else ''} "
                   f"{'its' if len(presented) == 1 else 'their'} asks: "
                   + ", ".join(_display(v) for v in presented) + ".")
    _restate_the_bills(world)
    return out


def _restate_the_bills(world) -> None:
    """Every standing quote the Congress re-prices — the summons (×1.5 rentes,
    ×2 stakes) and its end, a dissolution or the Imperial Peace (review
    #20/#35/#37/#62: the end turn that dissolved it had left the rail quoting
    ×1.5 for a Congress that no longer sat). The reward rail's rows and the
    satellites' desk petitions are re-stated in place (UX23-A's restate
    idiom, never opened); the collective petition and the redemption
    audience are priced at DELIVERY (`jealousy.refresh_petition_affordability`,
    `disobedience.standing_redemption`)."""
    player = _player(world)
    try:
        from backend.game_logic import dotation
        for marshal in (getattr(world, "marshals", {}) or {}).values():
            if getattr(marshal, "nation", None) == player:
                dotation.restate_reward_notice(world, marshal)
    except Exception:
        pass
    try:
        from backend.game_logic import vassal as _vassal
        _vassal.restate_petition_notices(world, player)
    except Exception:
        pass


def _eroding_marshals(world) -> List[Any]:
    from backend.game_logic import dotation
    if not dotation.is_dotation_world(world):
        return []
    return [m for m in (getattr(world, "marshals", {}) or {}).values()
            if m.nation == _player(world) and m.strength > 0
            and not getattr(m, "captured_by", "")
            and dotation.is_eroding(m, world)]


def _collective_petition(world) -> str:
    """The peace dividend: estates before the peace. The collective
    petition fires AT the summons if any marshal is eroding — bypassing the
    F4 fuse and the Fontainebleau count, never the one petition slot (a
    blocked slot owes the bill to the next end turn)."""
    eroding = _eroding_marshals(world)
    c = _store(world)
    if not eroding:
        c["petition_owed"] = False
        return ""
    from backend.game_logic import jealousy
    status = jealousy.queue_fontainebleau_petition(world, eroding,
                                                   reason="congress")
    if status == jealousy.PETITION_QUEUED:
        world.fontainebleau_last_turn = _turn(world)
        world.fontainebleau_armed = False
        c["petition_owed"] = False
        from backend.display_names import plural
        verb = "asks" if len(eroding) == 1 else "ask"
        return (f"The marshals present their bill: "
                f"{plural(len(eroding), 'unrewarded marshal')} {verb} for "
                f"estates before the peace.")
    c["petition_owed"] = True
    return ""


# ════════════════════════════════════════════════════════════════════════
# The table — how a court answers (§2.4).
# ════════════════════════════════════════════════════════════════════════

def _war_score(world, court: str, overrides: Optional[Dict] = None) -> int:
    if overrides and "war_score" in overrides:
        return int(overrides["war_score"])
    from backend.game_logic.diplomacy import get_war_score_for
    try:
        return int(get_war_score_for(world, court, _player(world)))
    except Exception:
        return 0


def _signed(value: int) -> str:
    return f"+{int(value)}" if int(value) > 0 else str(int(value))


def _our_score_text(world, court: str, court_score: int,
                    overrides: Optional[Dict] = None) -> str:
    """The war score as every other war surface prints it — FROM THE
    EMPEROR'S SIDE (review #8/#48/#51: the table printed the court's own
    reckoning, −30, beside the war banner's +30 for the same war). The
    predicate reads the score reckoned at the last end turn; when today's
    field already reads otherwise (a capture mid-turn), the clause says both,
    so the line never lies about which number decides."""
    ours = -int(court_score)
    text = f"our war score {_signed(ours)}"
    if overrides and "war_score" in overrides:
        return text
    try:
        from backend.game_logic.diplomacy import calculate_war_score
        live = int(calculate_war_score(_player(world), court, world))
    except Exception:
        return text
    if live != ours:
        text += f"; {_signed(live)} by today's field, counted at the end turn"
    return text


def _capital_taken(world, court: str, overrides: Optional[Dict] = None) -> bool:
    if overrides and "capital_taken" in overrides:
        return bool(overrides["capital_taken"])
    capital = world.get_nation_capital(court) or ""
    region = getattr(world, "regions", {}).get(capital) if capital else None
    holder = getattr(region, "controller", None) if region is not None else None
    return bool(holder) and world._top_overlord(holder) == _player(world)


def _state(world, court: str, overrides: Optional[Dict] = None) -> str:
    if overrides and overrides.get("state"):
        return str(overrides["state"])
    return str(world.get_diplomatic_state(court, _player(world)) or "PEACE")


def court_must_sue(world, court: str, overrides: Optional[Dict] = None) -> bool:
    """A great power at WAR with France sues once its war score reaches
    `sue_score` (−40) or France holds its capital (§2.4) — the ONE
    predicate the P1 Congress rung and the SUES stance both read. The pair
    score it tests is the one the table prints (shown = applied)."""
    if not sitting(world) or court not in great_powers(world):
        return False
    if court_gone(world, court):
        return False
    if _state(world, court, overrides) != "WAR":
        return False
    return (_war_score(world, court, overrides) <= sue_score(world)
            or _capital_taken(world, court, overrides))


SUE_CADENCE = 3                       # a suing court sends its envoy every 3 turns


def sue_due(world, court: str) -> bool:
    c = record(world) or {}
    last = (c.get("sued") or {}).get(court)
    return last is None or _turn(world) - int(last) >= SUE_CADENCE


def note_sued(world, court: str) -> None:
    _store(world).setdefault("sued", {})[court] = _turn(world)


def _signed_record(world, court: str) -> Optional[Dict[str, Any]]:
    """The treaty latch (§2.4 "ratifying it flips the court to
    recognizes"): a court that signed a war-ending treaty with the Emperor
    has recognized the order it signed, until that is broken — a new war
    between them, or a French capture from its bloc or of its covets."""
    c = record(world) or {}
    rec = (c.get("signed") or {}).get(court)
    if not isinstance(rec, dict) or rec.get("broken"):
        return None
    return rec


def _shut_out_reading(world, court: str, overrides: Optional[Dict] = None) -> Dict[str, Any]:
    """Britain answers like the others and ADDITIONALLY reads SHUT OUT —
    not blocking — when the Continental System closes ≥ cs_shutout_pct of
    the Continent's ports and no corps of hers stands off her own soil, for
    every end turn of the sitting (§2.4, D5). GR5: the court is the
    authored trade-dominance holder, never the literal."""
    from backend.game_logic import naval
    out = {"applies": False, "holds": False, "closed": 0, "total": 0,
           "needed": 0, "corps_abroad": [], "broken": False}
    if naval.trade_dominance_nation(world) != court:
        return out
    out["applies"] = True
    total = int(naval.continental_ports_total(world))
    closure = (float(overrides["closure"]) if overrides and "closure" in overrides
               else float(naval.closure_against(world, court)))
    pct = _int(world, "cs_shutout_pct", CS_SHUTOUT_PCT) / 100.0
    out["total"] = total
    out["closed"] = int(round(closure * total))
    out["needed"] = int(math.ceil(pct * total - 1e-9))
    abroad = ([] if overrides and overrides.get("no_corps_abroad")
              else corps_on_the_continent(world, court))
    out["corps_abroad"] = abroad
    c = record(world) or {}
    out["broken"] = bool(sitting(world) and c.get("shut_out_broken"))
    out["holds"] = (total > 0 and closure + 1e-9 >= pct and not abroad
                    and not out["broken"])
    return out


def mainland(world) -> frozenset:
    """"The Continent" (§2.4, D5): every province the summoner's capital
    reaches by LAND — the walkable adjacency with the drawn sea links
    removed (`naval.is_sea_link`). On the 1805 map: 92 of 126 provinces;
    off it, the British Isles, Scandinavia (after DEF-14's renames
    "Schleswig"/"Jutland" are Norway, "Stralsund" and "Scania" Sweden),
    Zealand (Copenhagen), the islands and Asia Minor.

    Why not "off her own homeland" (the first cut): London broke the
    shut-out on every staged seed by putting 5,000 men ashore at Copenhagen
    on the sitting's last turn — an island France cannot reach while the
    Royal Navy holds the Sound (measured: "The crossing from Holstein to
    Copenhagen is barred"), so the table's own price, "drive her corps from
    the Continent", named a lever that did not exist. A corps France can
    march to is on the Continent; one across the water is not — as
    historically Britain held Sicily and fought beside Sweden throughout the
    Continental System. The adjacency is static, so the component is cached
    on the world per capital (GR8: one walk of 126 provinces, ever)."""
    capital = world.get_nation_capital(_player(world)) or "Paris"
    cache = getattr(world, "_congress_mainland_cache", None)
    if isinstance(cache, tuple) and cache and cache[0] == capital:
        return cache[1]
    from backend.game_logic import naval
    regions = getattr(world, "regions", {}) or {}
    seen = {capital} if capital in regions else set()
    stack = list(seen)
    while stack:
        here = stack.pop()
        for adj in getattr(regions.get(here), "adjacent_regions", []) or []:
            if adj in seen or adj not in regions:
                continue
            if naval.is_sea_link(world, here, adj):
                continue
            seen.add(adj)
            stack.append(adj)
    result = frozenset(seen)
    try:
        world._congress_mainland_cache = (capital, result)
    except Exception:
        pass
    return result


def corps_on_the_continent(world, court: str) -> List[str]:
    """The court's standing corps on the Continent — the summoner's
    mainland (`mainland`), a corps France can march to and drive off."""
    land = mainland(world)
    out = []
    for m in (getattr(world, "marshals", {}) or {}).values():
        if m.nation != court or int(getattr(m, "strength", 0) or 0) <= 0:
            continue
        if getattr(m, "captured_by", "") or getattr(m, "administrative", False):
            continue
        if m.location and m.location in land:
            out.append(m.name)
    return sorted(out)


def _bloc(world) -> set:
    return set(world.get_bloc_members(_player(world)))


def _design_reading(world, court: str, skip=()) -> Dict[str, Any]:
    from backend.game_logic.agendas import recognition_design_reading
    return recognition_design_reading(world, court, _player(world),
                                      skip_design_ids=tuple(skip or ()))


def _bloc_share(world) -> float:
    from backend.game_logic.coalition import bloc_power, power_score
    active = list(world.get_active_nations())
    europe = sum(power_score(n, world) for n in active)
    if europe <= 0:
        return 0.0
    return bloc_power(_player(world), world) / float(europe)


def recognition_score(world, court: str,
                      overrides: Optional[Dict] = None) -> Dict[str, Any]:
    """The at-peace formula (§2.4), pure. `overrides` asks the counterfactual
    the price finder needs — never mutates the world:
      relation (delta), extra_gold, state, skip_designs, bought (bool —
      treat every design walked past as bought by France)."""
    ov = dict(overrides or {})
    player = _player(world)
    comps: List[Dict[str, Any]] = []

    def _add(key: str, label: str, value: int) -> None:
        comps.append({"key": key, "label": label, "value": int(value)})

    rel = int(world.nation_relations.get(world._make_diplo_key(court, player), 0) or 0)
    rel = max(-100, min(100, rel + int(ov.get("relation", 0) or 0)))
    _add("relation", "relations", rel)

    reading = _design_reading(world, court, ov.get("skip_designs") or ())
    bought_by_us = [d for d, payer in reading.get("bought", [])
                    if payer == player or d in (ov.get("skip_designs") or ())]
    if reading.get("survival"):
        design, dlabel = 0, "fights for its survival"
    elif reading.get("concerns"):
        design = -DESIGN_TERM
        dlabel = (f"its design {reading.get('active_title') or 'stands'} "
                  f"({', '.join(reading['concerns'][:3])})")
    elif bought_by_us:
        design, dlabel = DESIGN_TERM, "its design bought off"
    elif reading.get("satisfied_first"):
        design, dlabel = DESIGN_TERM, "its design satisfied"
    else:
        design, dlabel = 0, "its design"
    _add("design", dlabel, design)

    fear = 0
    # A court allied to us sits inside our bloc and does not fear it — the
    # alliance lever's counterfactual included (shown = applied).
    allied = str(ov.get("state") or "") in ("ALLIANCE", "DEFENSIVE_ALLIANCE")
    if court not in _bloc(world) and not allied:
        floor = (float(reading["contain_floor"])
                 if reading.get("contain_floor") is not None else FEAR_FLOOR_DEFAULT)
        excess = _bloc_share(world) - floor
        if excess > 0:
            fear = -int(excess * 100 + 1e-9)
    _add("fear", "fear of our bloc", fear)

    weary = int((getattr(world, "war_exhaustion", {}) or {}).get(court, 0) or 0)
    _add("weariness", "war weariness",
         WEARINESS_BONUS if weary >= WEARINESS_MARK else 0)

    _add("beaten", "beaten by us", BEATEN_BONUS if _beaten_recently(world, court) else 0)

    state = _state(world, court, ov)
    _add("treaty", "our treaty", RECOGNITION_TREATY_BONUS.get(state, 0))

    c = record(world) or {}
    paid = int((c.get("sweeteners") or {}).get(court, 0) or 0) if sitting(world) else 0
    paid += int(ov.get("extra_gold", 0) or 0)
    cap = _int(world, "sweetener_cap", SWEETENER_CAP)
    per = _int(world, "sweetener_per_1000", SWEETENER_PER_1000)
    _add("sweetener", "the sweetener", min(cap, paid * per // 1000))

    from backend.game_logic.campaign_variance import seeded_jitter
    number = int(c.get("number", 0) or 0)
    if c.get("status") != SITTING:
        # Before a summons the table projects the NEXT Congress (review #5:
        # the summons increments the number before its first answers, so the
        # projection read a Congress that never sits and re-rolled at once).
        number += 1
    jitter = seeded_jitter(str(getattr(world, "campaign_seed", "historical")),
                           f"congress::{number}::{court}", RECOGNITION_JITTER,
                           _turn(world))
    _add("jitter", "the mood of the court", jitter)

    score = sum(x["value"] for x in comps)
    return {"score": int(score), "threshold": recognition_threshold(world),
            "components": comps, "design": reading}


def _beaten_recently(world, court: str) -> bool:
    """"Beaten by France within 15 turns": a war with France ended inside the
    window AND some of the court's homeland stands in France's bloc (the
    volte-face V3 mark — no war instance records a winner)."""
    try:
        from backend.game_logic.emergent_designs import (
            _lost_homeland,
            _war_with_ended_recently,
        )
    except ImportError:
        return False
    player = _player(world)
    if not _war_with_ended_recently(world, court, player, BEATEN_WINDOW):
        return False
    bloc = _bloc(world)
    for region_name in _lost_homeland(world, court):
        region = getattr(world, "regions", {}).get(region_name)
        holder = getattr(region, "controller", None) if region else None
        if holder and (world._top_overlord(holder) or holder) in bloc:
            return True
    return False


def answer(world, court: str, overrides: Optional[Dict] = None) -> Dict[str, Any]:
    """How `court` answers the Congress NOW — the one derivation the table,
    the tick, the surfaces and the price finder all read."""
    ov = dict(overrides or {})
    row: Dict[str, Any] = {"court": court, "display": _display(court),
                           "seat": seat(world, court), "stance": REFUSES,
                           "by": "", "reason": "", "score": None,
                           "threshold": recognition_threshold(world)}
    gone = court_gone(world, court)
    if gone:
        row.update(stance=GONE, by=gone,
                   reason=("its crown is struck from the map" if gone == "eliminated"
                           else "it is our satellite"))
        return row
    signed = None if ov.get("ignore_treaty") else _signed_record(world, court)
    if signed is not None:
        row.update(stance=RECOGNIZES, by="treaty",
                   reason=f"it signed our peace on turn {int(signed.get('turn', 0))}")
        return row
    shut = _shut_out_reading(world, court, ov)
    if shut["holds"]:
        row.update(stance=SHUT_OUT, by="ports",
                   reason=(f"{shut['closed']} of {shut['total']} ports shut against "
                           f"her, no corps of hers on the Continent"))
        row["shut_out"] = shut
        return row
    if shut["applies"]:
        row["shut_out"] = shut
    state = _state(world, court, ov)
    if state == "WAR":
        score = _war_score(world, court, ov)
        row["war_score"] = int(score)
        ours = _our_score_text(world, court, score, ov)
        row["our_war_score"] = -int(score)
        projected = not sitting(world) and (
            score <= sue_score(world) or _capital_taken(world, court, ov))
        if court_must_sue(world, court, ov) or projected:
            taken = _capital_taken(world, court, ov)
            reason = (f"we hold {world.get_nation_capital(court)}" if taken
                      else f"beaten in the field ({ours})")
            if projected:
                # Before a summons no envoy comes (the sue rung is the
                # Congress's; the coalition's loyalty holds a member to −50):
                # the table says what the summons WOULD read (review #9/#25).
                reason += " — it would sue once the Congress sits"
            row.update(stance=SUES, by="war", reason=reason, projected=bool(projected))
        else:
            row.update(stance=REFUSES, by="war",
                       reason=f"at war with us ({ours} — it sues at "
                              f"+{-sue_score(world)})")
        return row
    c = record(world) or {}
    withdrawn = (c.get("withdrawn") or {}).get(court) if sitting(world) else None
    scored = recognition_score(world, court, ov)
    row["score"] = scored["score"]
    row["components"] = scored["components"]
    if withdrawn:
        row.update(stance=REFUSES, by="withdrawn", reason=str(withdrawn))
        return row
    at_table = ((c.get("signed_at_table") or {}).get(court)
                if sitting(world) and not ov.get("ignore_table") else None)
    if at_table is not None:
        # A signature given at the table HOLDS for the sitting (§2.4: the
        # flip-back triggers — a French declaration, a capture by force from
        # its bloc, annexing what it covets — are the only way back; the
        # capture seam writes `withdrawn` above). Without the latch an exact
        # price paid at 50 fell to 49 by the advance's ordinary relation
        # drift and the Congress dissolved "Berlin had not signed".
        row.update(stance=RECOGNIZES, by="table",
                   reason=f"it signed at the table on turn {int(at_table)}")
        return row
    if scored["score"] >= scored["threshold"]:
        row.update(stance=RECOGNIZES, by="formula",
                   reason=_top_term(scored["components"], positive=True))
        return row
    row.update(stance=REFUSES, by="formula",
               reason=_top_term(scored["components"], positive=False))
    if state == "ARMISTICE":
        row["reason"] = "a truce is not a peace — " + row["reason"]
    return row


def _top_term(components: List[Dict[str, Any]], positive: bool) -> str:
    pool = [c for c in components if c["key"] != "jitter"
            and ((c["value"] > 0) if positive else (c["value"] < 0))]
    if not pool:
        return "" if positive else "it will not sign"
    pick = (max(pool, key=lambda c: c["value"]) if positive
            else min(pool, key=lambda c: c["value"]))
    value = pick["value"]
    sign = "+" if value > 0 else ""
    return f"{pick['label']} {sign}{value}"


# ════════════════════════════════════════════════════════════════════════
# The price — the cheapest levers that would flip a court (§2.4). Display
# only (the price is counsel, never a bargain the court is bound to), but
# TRUE: every lever's value is the score the formula moves by when it is
# applied, and the bundle, applied, flips the court (driven pins).
# ════════════════════════════════════════════════════════════════════════

def _buy_off_chain(world, court: str) -> List[Dict[str, Any]]:
    """The designs that must be bought off, in order, before the court's
    design term stops reading against us (buying one wakes the next — the
    Austria Italy→Germany chain). Empty when no chain turns the term."""
    chain: List[Dict[str, Any]] = []
    skip: List[str] = []
    for _ in range(6):
        reading = _design_reading(world, court, skip)
        if reading.get("survival") or not reading.get("active_id"):
            break
        # A design reads against the order when it wants what our bloc holds
        # OR when it is a contain design — the arbiter's authored floor
        # (0.33) makes the court fear a bloc the default floor (0.45) would
        # not. Review #6: walking concerns alone never priced Russia's
        # arbiter, whose purchase is worth +29 through the real verb.
        if not (reading.get("concerns")
                or reading.get("active_type") == "contain_hegemon"):
            break
        chain.append({"id": reading.get("active_id"),
                      "title": reading.get("active_title") or "its design"})
        skip.append(str(reading.get("active_id")))
    return chain if chain else []


# The treaty lever: the best treaty the court's CURRENT relation permits
# (`STATE_RELATION_REQUIREMENTS` — `_ratify_treaty` refuses the rest; review
# #1: the first cut always priced an alliance, which a court at relation 30
# can never ratify). Best first.
_TREATY_LEVERS = (
    ("ALLIANCE", "an alliance"),
    ("DEFENSIVE_ALLIANCE", "a defensive alliance"),
    ("NON_AGGRESSION", "a non-aggression pact"),
    ("OPEN_BORDERS", "open borders"),
)


def _treaty_lever(world, court: str, base: int) -> Optional[Dict[str, Any]]:
    from backend.game_logic.diplomacy import (
        STATE_RELATION_REQUIREMENTS,
        check_relation_requirement,
        validate_transition,
    )
    state = _state(world, court)
    current = RECOGNITION_TREATY_BONUS.get(state, 0)
    rel = int(world.nation_relations.get(
        world._make_diplo_key(court, _player(world)), 0) or 0)
    for target, label in _TREATY_LEVERS:
        if RECOGNITION_TREATY_BONUS.get(target, 0) <= current:
            continue
        if not validate_transition(state, target):
            continue
        if not check_relation_requirement(state, target, rel):
            continue
        value = recognition_score(world, court, {"state": target})["score"] - base
        if value > 0:
            return {"key": "treaty", "value": value, "state": target,
                    "text": f"{label} with {_display(court)} (+{value})"}
    # None ratifiable today: name the alliance and the courtship it needs,
    # as one lever (its value counts the relations it takes).
    need = STATE_RELATION_REQUIREMENTS.get("ALLIANCE")
    if (need is not None and rel < int(need) and current < RECOGNITION_TREATY_BONUS["ALLIANCE"]
            and validate_transition(state, "ALLIANCE")):
        courted = int(need) - rel
        value = recognition_score(world, court, {"state": "ALLIANCE",
                                                  "relation": courted})["score"] - base
        if value > 0:
            return {"key": "treaty", "value": value, "state": "ALLIANCE",
                    "relation": courted,
                    "text": (f"court them to {int(need)} ({_signed(courted)} relations), "
                             f"then an alliance with {_display(court)} (+{value})")}
    return None


def _sweetener_gold(paid: int, per: int, points: int) -> int:
    """The smallest gold that buys `points` MORE at the table given what is
    already laid down (review #7: the quote ignored the part-paid remainder
    while the charge clipped to it, so quote, charge and receipt disagreed)."""
    have = paid * per // 1000
    return max(0, int(math.ceil((have + points) * 1000 / per)) - paid)


def _sweetener_points(paid: int, charge: int, per: int, cap: int) -> int:
    """What `charge` more gold moves the score by — the applied increment."""
    return min(cap, (paid + charge) * per // 1000) - min(cap, paid * per // 1000)


def price(world, court: str, row: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    row = row if row is not None else answer(world, court)
    stance = row.get("stance")
    out: Dict[str, Any] = {"text": "", "levers": [], "gap": 0}
    if stance in SATISFIED:
        return out
    if stance == SUES:
        if row.get("projected"):
            # Review #9/#25: before a summons no envoy comes.
            out["text"] = ("summon the Congress — beaten as it is, it sues once "
                           "the Congress sits, and the peace it signs then "
                           "recognizes the order")
            out["levers"] = [{"key": "summon", "value": None,
                              "text": "summon the Congress", "command": SUMMON_COMMAND}]
        else:
            out["text"] = ("sign the peace it sues for — its envoy brings the terms "
                           "(a peace signed while the Congress sits recognizes the order)")
            out["levers"] = [{"key": "peace", "text": "sign its peace", "value": None}]
        return out
    state = _state(world, court)
    truce_peace = None
    if state == "ARMISTICE" and sitting(world):
        # Review #2/#14: in a truce the one lever the latch honours — a peace
        # signed at the table's own time — leads the price.
        truce_peace = {"key": "peace", "value": None,
                       "text": (f"sign a peace with {_display(court)} — a peace "
                                f"signed while the Congress sits recognizes the order")}
    if row.get("by") == "withdrawn":
        if truce_peace is not None:
            out["levers"] = [truce_peace]
            out["text"] = truce_peace["text"]
            return out
        out["text"] = "none at this sitting — it withdrew; summon again after a dissolution"
        return out
    levers: List[Dict[str, Any]] = []
    if row.get("by") == "war":
        score = int(row.get("war_score", 0) or 0)
        capital = world.get_nation_capital(court) or ""
        levers.append({"key": "war", "value": None,
                       "text": (f"win the war to {_signed(-sue_score(world))} "
                                f"(now {_signed(-score)})")})
        # GE-V §4 nits (SR quick win, September 26, 2026): the seat is
        # display and the capital is the map's, so the lever names it as
        # the capital ("its capital, Vilna" under a "(St Petersburg)" seat);
        # and for an island court the ports lever comes BEFORE the capital
        # — a Descent most campaigns cannot mount should not lead the line.
        capital_lever = {"key": "capital", "value": None,
                         "text": (f"take its capital, {capital}" if capital
                                  else "take its capital")}
        ports = _ports_lever(row)
        island = bool(capital) and capital not in mainland(world)
        if island and ports is not None:
            levers.append(ports)
        levers.append(capital_lever)
        levers.append({"key": "peace", "value": None,
                       "text": f"sign a peace with {_display(court)}"})
        if ports is not None and not island:
            levers.append(ports)
        out["levers"] = levers
        out["text"] = " · or ".join(lv["text"] for lv in levers)
        return out
    # The at-peace formula — each lever priced by the formula itself.
    base = int(row.get("score") or 0)
    threshold = int(row.get("threshold") or recognition_threshold(world))
    gap = max(0, threshold - base)
    out["gap"] = gap
    comps = {c["key"]: c["value"] for c in (row.get("components") or [])}
    player = _player(world)
    at_war = world.is_at_war(court, player)

    if truce_peace is not None:
        levers.append(truce_peace)
    # 1. The sweetener — gold at the table, capped (only while it sits).
    cap = _int(world, "sweetener_cap", SWEETENER_CAP)
    per = _int(world, "sweetener_per_1000", SWEETENER_PER_1000)
    room = max(0, cap - int(comps.get("sweetener", 0)))
    if room > 0 and per > 0:
        points = min(room, gap) if gap > 0 else room
        c = record(world) or {}
        paid = (int((c.get("sweeteners") or {}).get(court, 0) or 0)
                if sitting(world) else 0)
        gold = _sweetener_gold(paid, per, points)
        levers.append({"key": "sweetener", "value": points, "gold": gold,
                       "text": f"a {gold:,}g sweetener at the table (+{points})",
                       "command": f"offer {court} {gold} gold for recognition"})
    # 2. The design — buy it off (the chain), where buying can turn it.
    if comps.get("design", 0) < DESIGN_TERM and not at_war:
        chain = _buy_off_chain(world, court)
        if chain:
            from backend.game_logic.instruments import (
                BUYOFF_RELATION_BONUS,
                compute_buyoff_price,
            )
            skip = [d["id"] for d in chain]
            # Shown = applied: a struck bargain ALSO warms the court toward
            # its payer (`create_compensation_bargain`, +BUYOFF_RELATION_BONUS
            # per design) — the lever's value is the whole of what buying moves.
            warmth = BUYOFF_RELATION_BONUS * len(chain)
            after = recognition_score(world, court, {"skip_designs": skip,
                                                     "relation": warmth})["score"]
            value = after - base
            if value > 0:
                first = compute_buyoff_price(world, court)
                names = " then ".join(d["title"] for d in chain)
                if len(chain) > 1:
                    # Review #57: one order buys ONE design; the next is
                    # priced when it wakes. The lever says so.
                    cost = (f" — one order each, {first:,}g the first"
                            if first else " — one order each")
                else:
                    cost = f" ({first:,}g)" if first else ""
                text = f"buy off {names}{cost} (+{value})"
                levers.append({"key": "design", "value": value, "gold": first or 0,
                               "chain": [d["id"] for d in chain], "warmth": warmth,
                               "orders": len(chain),
                               "text": text, "command": f"buy off {court}'s design"})
    # 3. A treaty — the best one the court's relation lets it ratify.
    if not at_war:
        treaty = _treaty_lever(world, court, base)
        if treaty is not None:
            levers.append(treaty)
    # 4. Relations — the universal lever, and the slowest.
    rel = int(comps.get("relation", 0))
    if rel < 100:
        levers.append({"key": "relation", "value": 100 - rel,
                       "text": "better relations (court them)"})
    # 5. The ports (the trade-dominance court): SHUT OUT satisfies the table
    # without the formula (review #6 — the at-peace arm never offered it).
    ports = _ports_lever(row)
    if ports is not None:
        levers.append(ports)
    out["levers"] = levers
    if gap <= 0:
        return out
    alternatives = [lv["text"] for lv in (truce_peace, ports) if lv is not None]
    # The bundle: gold first (immediate), then the treaty, then relations —
    # verified against the formula with every chosen lever applied at once.
    chosen: List[Dict[str, Any]] = []
    ov: Dict[str, Any] = {}
    for key in ("sweetener", "design", "treaty"):
        lever = next((lv for lv in levers if lv["key"] == key), None)
        if lever is None:
            continue
        chosen.append(lever)
        _apply_lever_override(ov, lever)
        if recognition_score(world, court, ov)["score"] >= threshold:
            break
    now = recognition_score(world, court, ov)["score"]
    if now < threshold:
        need = threshold - now
        courted = int(ov.get("relation", 0))
        if rel + courted + need <= 100:
            rel_lever = {"key": "relation", "value": need,
                         "text": f"{need} more relations (court them)"}
            chosen.append(rel_lever)
            _apply_lever_override(ov, rel_lever)
            now = recognition_score(world, court, ov)["score"]
    if now < threshold:
        base_text = f"needs +{gap} — more than this table can buy"
        out["text"] = " · or ".join(alternatives + [base_text])
        out["bundle"] = []
        return out
    # Drop any chosen lever the bundle does not need (smallest first) — the
    # cheapest bundle that still flips it.
    for lever in sorted(list(chosen), key=lambda lv: lv.get("value") or 0):
        trial = [lv for lv in chosen if lv is not lever]
        trial_ov: Dict[str, Any] = {}
        for lv in trial:
            _apply_lever_override(trial_ov, lv)
        if trial and recognition_score(world, court, trial_ov)["score"] >= threshold:
            chosen = trial
    out["bundle"] = [dict(lv) for lv in chosen]
    bundle = f"needs +{gap}: " + " + ".join(_bundle_text(lv) for lv in chosen)
    out["text"] = " · or ".join(alternatives + [bundle])
    return out


def _ports_lever(row: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Shut the ports (SHUT OUT). A shut-out spent this sitting is no lever
    (the ports must hold at EVERY end turn of it)."""
    shut = row.get("shut_out") or {}
    if not shut.get("applies") or shut.get("broken"):
        return None
    need = int(shut.get("needed", 0))
    text = f"shut {need} of {shut.get('total', 0)} ports (now {shut.get('closed', 0)})"
    if shut.get("corps_abroad"):
        text += " and drive her corps from the Continent"
    return {"key": "ports", "value": None, "text": text}


def _apply_lever_override(ov: Dict[str, Any], lever: Dict[str, Any]) -> None:
    key = lever.get("key")
    if key == "sweetener":
        ov["extra_gold"] = int(ov.get("extra_gold", 0)) + int(lever.get("gold", 0))
    elif key == "design":
        ov["skip_designs"] = list(ov.get("skip_designs") or []) + list(lever.get("chain") or [])
        ov["relation"] = int(ov.get("relation", 0)) + int(lever.get("warmth", 0) or 0)
    elif key == "treaty":
        ov["state"] = lever.get("state") or "ALLIANCE"
        ov["relation"] = int(ov.get("relation", 0)) + int(lever.get("relation", 0) or 0)
    elif key == "relation":
        ov["relation"] = int(ov.get("relation", 0)) + int(lever.get("value") or 0)


def _bundle_text(lever: Dict[str, Any]) -> str:
    if lever.get("key") == "relation":
        return f"{int(lever.get('value') or 0)} more relations (court them)"
    return str(lever.get("text") or "")


# ════════════════════════════════════════════════════════════════════════
# The hold (§2.5).
# ════════════════════════════════════════════════════════════════════════

def hold_conditions(world) -> List[Dict[str, Any]]:
    """The seven conditions, every end turn of the sitting. A failed one
    dissolves the Congress that turn."""
    c = record(world) or {}
    view = titled(world)
    player = _player(world)
    capital = world.get_nation_capital(player) or "the capital"
    lost = list(c.get("lost") or [])
    declared = list(c.get("declared") or [])
    joined = dict(c.get("joined") or {})
    rebels = list(c.get("rebellions") or [])
    alarm = _alarm(world)
    ceiling = _int(world, "hold_alarm_ceiling", HOLD_ALARM_CEILING)
    swords = [f"we declared on {', '.join(_display(d) for d in declared)}"] if declared else []
    swords += [f"we joined {_display(ally)}'s war on {_display(t)}"
               for t, ally in sorted(joined.items())]
    reopened = _reopened_by_war(world, view)
    titled_text = f"{view['needed']} titled provinces ({view['count']} of {view['needed']})"
    if reopened and view["count"] < view["needed"]:
        titled_text += f" — {reopened}"
    return [
        {"key": "titled", "met": view["count"] >= view["needed"],
         "text": titled_text},
        {"key": "capital", "met": _capital_held(world), "text": f"{capital} held"},
        {"key": "emperor", "met": _emperor_free(world), "text": "the Emperor free"},
        {"key": "satellites", "met": not rebels,
         "text": ("no satellite lost to rebellion or defection"
                  + (f" ({_lost_satellites_phrase(c, rebels)})" if rebels else ""))},
        {"key": "lost", "met": not lost,
         "text": ("no titled province lost"
                  + (f" ({', '.join(lost[:3])} taken)" if lost else ""))},
        {"key": "declared", "met": not swords,
         "text": ("no war declared or joined since the summons"
                  + (f" ({'; '.join(swords)})" if swords else ""))},
        {"key": "alarm", "met": alarm < ceiling,
         "text": f"Europe's alarm below {ceiling} (now {alarm})"},
    ]


def _reopened_by_war(world, view: Dict[str, Any]) -> str:
    """Review #12: a court that CEDED provinces by treaty and then goes to
    war with the Emperor — whoever declared — reopens its cessions (GE-1's
    renewed-war rule, `game_end.break_signed_titles`). The titled count then
    falls with no French act, so the hold names the war that did it
    ("Hanover's war reopened what it ceded (Kalenberg, Luneburg)")."""
    c = record(world) or {}
    since = int(c.get("summoned_turn", _turn(world)) or 0)
    store = getattr(world, "province_title", None)
    if not isinstance(store, dict):
        return ""
    held = set(view.get("held") or [])
    by: Dict[str, List[str]] = {}
    for region_name, rec in store.items():
        if not isinstance(rec, dict) or not rec.get("reopened_by"):
            continue
        if int(rec.get("reopened_turn", -1)) < since or region_name not in held:
            continue
        by.setdefault(str(rec["reopened_by"]), []).append(region_name)
    if not by:
        return ""
    parts = [f"{_display(court)}'s war reopened what it ceded "
             f"({', '.join(sorted(names)[:3])}{' …' if len(names) > 3 else ''})"
             for court, names in sorted(by.items())]
    return "; ".join(parts)


def _lost_satellites_phrase(c: Dict[str, Any], rebels: List[str]) -> str:
    """"Saxony rose in rebellion" / "Saxony defected to Britain" — joined."""
    defections = c.get("defections") or {}
    parts = []
    for name in rebels:
        to = defections.get(name)
        parts.append(f"{_display(name)} defected to {_display(to)}" if to
                     else f"{_display(name)} rose in rebellion")
    if len(parts) <= 1:
        return "".join(parts)
    return ", ".join(parts[:-1]) + " and " + parts[-1]


# ════════════════════════════════════════════════════════════════════════
# The per-turn tick (called from `game_end.process_end_of_turn`, after the
# fall clocks and before the Verdict).
# ════════════════════════════════════════════════════════════════════════

def _take_answers(world, first: bool = False) -> Dict[str, Dict[str, Any]]:
    """Re-derive every court's answer and write the record the pressure
    readers use (`refusing_since` — the refusal count is a per-turn
    reading that resets the turn a court stops refusing). Logs beat 3 (a
    recognition won) and beat 2's fore-warning and war."""
    c = _store(world)
    prior = dict(c.get("answers") or {})
    table: Dict[str, Dict[str, Any]] = {}
    turn = _turn(world)
    # The courts standing with the peace, updated in logging order so each
    # signature's beat counts only the signatures before it (review #50b).
    standing = {court: (prior.get(court) or {}).get("stance") in SATISFIED
                for court in great_powers(world)}
    for court in great_powers(world):
        row = answer(world, court)
        prev = prior.get(court) or {}
        stored = {"stance": row["stance"], "by": row.get("by", ""),
                  "reason": row.get("reason", ""), "score": row.get("score")}
        if row["stance"] == REFUSES:
            stored["refusing_since"] = (int(prev["refusing_since"])
                                        if prev.get("stance") == REFUSES
                                        and prev.get("refusing_since") is not None
                                        else turn)
        else:
            stored["refusing_since"] = None
        standing[court] = row["stance"] in SATISFIED
        if not first and prev:
            was, now = prev.get("stance"), row["stance"]
            if now in (RECOGNIZES, SHUT_OUT) and was not in (RECOGNIZES, SHUT_OUT, GONE):
                world.log_event({"type": "congress", "phase": "recognized",
                                 "nation": _player(world), "court": court,
                                 "by": row.get("by", ""), "stance": now,
                                 "standing": sum(1 for v in standing.values() if v),
                                 "message": f"{seat(world, court)} signs."})
            elif was == SHUT_OUT and now not in SATISFIED:
                # A court that was SHUT OUT never signed — it is no longer shut
                # out (a landing on the Continent, or the ports reopened), and
                # the line says which (measured: "London withdraws its
                # signature" after Paget landed at Lisbon).
                why = _shut_out_lapse_reason(world, court)
                world.log_event({"type": "congress", "phase": "withdrew",
                                 "was": SHUT_OUT,
                                 "nation": _player(world), "court": court,
                                 "reason": why,
                                 "message": (f"{seat(world, court)} is no longer "
                                             f"shut out — {why}.")})
            elif was == RECOGNIZES and now == REFUSES:
                world.log_event({"type": "congress", "phase": "withdrew",
                                 "was": RECOGNIZES,
                                 "nation": _player(world), "court": court,
                                 "reason": row.get("reason", ""),
                                 "message": f"{seat(world, court)} withdraws its signature."})
            if (was == REFUSES and prev.get("by") in ("formula", "withdrawn")
                    and row.get("by") == "war"
                    and court not in _france_drew_the_sword(c)):
                # Review #15/#44: a war the Emperor declared (or joined at an
                # ally's side) is his sword, not the court's cannon — the hold
                # says so ("we declared on Prussia"); the beat would blame Berlin.
                world.log_event({"type": "congress", "phase": "war",
                                 "nation": _player(world), "court": court,
                                 "message": f"{seat(world, court)} answers the "
                                            f"Congress with cannon."})
        c.setdefault("answers", {})[court] = stored
        table[court] = row
    return table


def _france_drew_the_sword(c: Dict[str, Any]) -> set:
    """The courts the Emperor went to war with during this sitting — the
    ones he declared on, and the ones he joined an ally's war against."""
    return set(c.get("declared") or []) | set((c.get("joined") or {}).keys())


def take_the_signatures(world) -> List[str]:
    """Latch every court whose live answer is a recognition AT THE TABLE
    (the formula) — called at the START of every end turn (TurnManager) and
    at the tick, so whatever the player won during the turn is signed before
    the advance moves relations. Deterministic: never on a read. Returns the
    courts newly latched."""
    if not sitting(world):
        return []
    c = _store(world)
    latched = c.setdefault("signed_at_table", {})
    new = []
    for court in great_powers(world):
        if court in latched:
            continue
        row = answer(world, court)
        if row["stance"] == RECOGNIZES and row.get("by") == "formula":
            latched[court] = _turn(world)
            new.append(court)
    return new


def _shut_out_lapse_reason(world, court: str) -> str:
    """Why the trade-dominance court is no longer shut out, in one clause."""
    reading = _shut_out_reading(world, court)
    abroad = list(reading.get("corps_abroad") or [])
    if abroad:
        from backend.display_names import humanize_entity_name
        names = [humanize_entity_name(n) for n in abroad[:2]]
        where = []
        for name in abroad[:2]:
            m = (getattr(world, "marshals", {}) or {}).get(name)
            if m is not None and getattr(m, "location", ""):
                where.append(str(m.location))
        tail = f" at {', '.join(sorted(set(where)))}" if where else ""
        return (f"{' and '.join(names)} stand{'s' if len(names) == 1 else ''} "
                f"on the Continent{tail}")
    return (f"only {reading.get('closed', 0)} of {reading.get('total', 0)} ports "
            f"are shut against her ({reading.get('needed', 0)} needed)")


def refusal_turns(world, court: str) -> int:
    """How many end turns `court` has refused — the per-turn reading the
    intent term multiplies (§2.5 "+15 a turn")."""
    if not sitting(world):
        return 0
    row = ((record(world) or {}).get("answers") or {}).get(court) or {}
    if row.get("stance") != REFUSES or row.get("refusing_since") is None:
        return 0
    return max(0, _turn(world) - int(row["refusing_since"]))


def stored_refusers(world) -> List[str]:
    if not sitting(world):
        return []
    return sorted(court for court, row in
                  ((record(world) or {}).get("answers") or {}).items()
                  if (row or {}).get("stance") == REFUSES)


def process_end_of_turn(world, turn_ended: int) -> List[Dict[str, Any]]:
    """E1, then the sitting's tick: the answers, the London purse, the War
    of the Congress, the hold, and on the last turn the resolution. Returns
    the endings stamped (the Imperial Peace), for `_attach_endings`."""
    if not armed(world):
        return []
    stamped: List[Dict[str, Any]] = []
    if (THE_UNIVERSAL_MONARCHY and not imperial_peace_signed(world)
            and no_great_power_stands(world)
            # Review #17: E1 waits while another court holds the capital or
            # the Emperor — the order is not "uncontested" from a cell.
            and _capital_held(world) and _emperor_free(world)):
        rec = _proclaim(world, turn_ended, route="universal_monarchy")
        if rec is not None:
            stamped.append(rec)
        return stamped
    c = record(world)
    if c is None or c.get("status") != SITTING:
        _lapse_grudges(world)
        return stamped
    take_the_signatures(world)
    table = _take_answers(world)
    if LONDON_FUNDS_THE_REFUSERS:
        _london_pays(world, table)
    if THE_CONGRESS_LOWERS_THE_GATE:
        _the_war_of_the_congress(world, table)
        table = {court: answer(world, court) for court in great_powers(world)}
    _latch_shut_out(world, table)
    day = int(turn_ended) - int(c.get("summoned_turn", turn_ended))
    conditions = hold_conditions(world)
    failed = [x for x in conditions if not x["met"]]
    view = titled(world)
    c.setdefault("strip", []).append({
        "turn": int(turn_ended), "day": int(day), "held": not failed,
        "titled": int(view["count"]),
        "stances": {k: v["stance"] for k, v in table.items()},
    })
    _invalidate_intent(world)
    if failed:
        _dissolve(world, turn_ended, table, reason=failed[0])
        return stamped
    if int(turn_ended) >= int(c.get("ends_turn", turn_ended + 1)):
        if all(row["stance"] in SATISFIED for row in table.values()):
            rec = _proclaim(world, turn_ended, route="congress", table=table)
            if rec is not None:
                stamped.append(rec)
        else:
            _dissolve(world, turn_ended, table, reason={
                "key": "unsigned", "met": False,
                "text": _unsigned_reason(table)})
        return stamped
    # Review #36: an owed bill is presented only to a Congress still sitting
    # after this tick's resolution — never on the tick that ends it.
    if (c.get("petition_owed") and THE_BILLS_COME_DUE
            and c.get("status") == SITTING):
        _collective_petition(world)
    # The stakes double from the sitting's first day (`petition_stakes`),
    # which begins at THIS tick — every standing quote is re-stated to it.
    if c.get("status") == SITTING and THE_BILLS_COME_DUE:
        _restate_the_bills(world)
    return stamped


def _unsigned_reason(table: Dict[str, Dict[str, Any]]) -> str:
    """Review #9: a court still SUING at the eighth turn is not a court that
    "would not sign" — it asked for a peace the Emperor did not sign."""
    refusing = [k for k, v in table.items() if v["stance"] == REFUSES]
    suing = [k for k, v in table.items() if v["stance"] == SUES]
    parts = []
    if refusing:
        parts.append("the courts would not sign: "
                     + ", ".join(_display(k) for k in refusing))
    if suing:
        names = ", ".join(_display(k) for k in suing)
        parts.append(f"{names} sued, and the Emperor did not sign "
                     f"{'its' if len(suing) == 1 else 'their'} peace")
    return "; ".join(parts) or "the courts would not sign"


def _latch_shut_out(world, table: Dict[str, Dict[str, Any]]) -> None:
    """"The Continental System closure is ≥ cs_shutout_pct (50% since VP-R1
    P2, September 25, 2026 — 60% was unreachable from play) for EVERY turn
    of the sitting" (§2.4): the first end turn the PORTS fall short, SHUT OUT is
    spent for this Congress. The other half — "no British corps stands on
    the Continent" — is a LIVE reading, never latched: a landing is answered
    by driving it into the sea before the eighth turn (the price says so).
    Latching it too made a single enemy-phase landing permanent with no
    counterplay (measured: Paget ashore at Copenhagen on the sixth day ended
    the Pressburg arm's Congress though the ports never fell short)."""
    c = _store(world)
    if c.get("shut_out_broken"):
        return
    from backend.game_logic import naval
    court = naval.trade_dominance_nation(world)
    if not court or court_gone(world, court) or _signed_record(world, court):
        return
    reading = _shut_out_reading(world, court)
    if reading["applies"] and int(reading["closed"]) < int(reading["needed"]):
        c["shut_out_broken"] = True


def _london_pays(world, table: Dict[str, Dict[str, Any]]) -> None:
    """A refusing paymaster funds every other refuser (§2.5) — the AI-2e
    outbid honoured (France's own standing sponsorship of the court at ≥ the
    subsidy outbids London), the war subsidy's recipient not paid twice."""
    from backend.game_logic import naval
    payer = naval.trade_dominance_nation(world)
    if not payer or (table.get(payer) or {}).get("stance") != REFUSES:
        return
    try:
        from backend.game_logic.coalition import get_british_subsidy_recipient
        war_recipient = get_british_subsidy_recipient(world)
    except Exception:
        war_recipient = None
    from backend.game_logic.instruments import standing_sponsorship_amount
    from backend.game_logic.agendas import survival_override_active
    if survival_override_active(world, payer):
        return
    # Review #24: the paymaster's own rules, generalized — its authored
    # treasury floor (the paymaster deck entry's), no gold to a court it is
    # at war with, and none to a court France has bought off (AI-2e's second
    # arm: a live compensation bargain from the summoner).
    floor = _paymaster_floor(world, payer)
    player = _player(world)
    bought = {r.get("recipient") for r in getattr(world, "compensation_bargains", []) or []
              if r.get("payer") == player}
    c = _store(world)
    paid_to = []
    for court, row in sorted(table.items()):
        if court == payer or row.get("stance") != REFUSES or court == war_recipient:
            continue
        if world.is_at_war(payer, court) or court in bought:
            continue
        if standing_sponsorship_amount(world, player, court) >= LONDON_SUBSIDY:
            continue
        gold = world.nation_gold
        if int(gold.get(payer, 0) or 0) - LONDON_SUBSIDY < floor:
            break
        gold[payer] = int(gold.get(payer, 0)) - LONDON_SUBSIDY
        gold[court] = int(gold.get(court, 0) or 0) + LONDON_SUBSIDY
        paid_to.append(court)
        if court not in (c.get("subsidized") or []):
            c.setdefault("subsidized", []).append(court)
            world.log_event({"type": "congress", "phase": "subsidy",
                             "nation": _player(world), "court": court,
                             "payer": payer, "amount": LONDON_SUBSIDY,
                             "message": (f"{seat(world, payer)} pays "
                                         f"{seat(world, court)} {LONDON_SUBSIDY}g a "
                                         f"turn to refuse the Congress.")})
    c["paid_this_turn"] = paid_to


def march_blocker(world, court: str) -> str:
    """What stands between a refuser's patience and war — '' when the War of
    the Congress WOULD take it once its refusals come due. The ONE predicate
    the join, the fore-warning, the table's countdown and the ledger read
    (review #4/#23/#43/#54: the countdown and the beat-2 warning had been
    derived from the refusal count alone, so a court in a truce, one we are
    allied to, or one with no coalition to join was told it would march at
    this end turn, and never did)."""
    from backend.game_logic.coalition import peace_with_target_is_fresh
    player = _player(world)
    state = str(world.get_diplomatic_state(court, player) or "PEACE")
    if state == "ARMISTICE":
        return "a truce holds it"
    if state in ("ALLIANCE", "DEFENSIVE_ALLIANCE"):
        return "our alliance holds it"
    if court in (getattr(world, "vassals", {}) or {}):
        return "it is a vassal"
    coalition = getattr(world, "active_coalition", None) or {}
    if coalition.get("target_nation") != player:
        from backend.game_logic.coalition import brewing_gate
        return (f"no coalition stands against us to join — a league gathers "
                f"only at alarm {brewing_gate(world)} (now {_alarm(world)})")
    if court in (coalition.get("members") or []):
        return "it is already in the coalition"
    if peace_with_target_is_fresh(court, world, player):
        return "its peace with us is too fresh to break"
    cooldown = int((getattr(world, "armistice_cooldowns", {}) or {}).get(
        world._make_diplo_key(court, player), 0) or 0)
    if cooldown > 0:
        return f"a truce's cooldown binds it ({cooldown} more turns)"
    if not refuser_qualifies(world, court, player):
        return "it does not refuse at peace"
    return ""


def _paymaster_floor(world, payer: str) -> int:
    """The payer's authored treasury floor (its `paymaster` deck entry) —
    0 when it has none (a deckless world keeps the bare solvency check)."""
    for entry in (getattr(world, "agendas", {}) or {}).get(payer) or []:
        if entry.get("type") == "paymaster":
            return int(entry.get("treasury_floor") or 0)
    return 0


def _the_war_of_the_congress(world, table: Dict[str, Dict[str, Any]]) -> None:
    """Refusal has teeth: a court refusing at peace for WAR_AFTER_REFUSALS
    end turns, while a coalition already stands against France, joins it
    (§16.2 — player-targeted war is the coalition's). One turn earlier the
    table and the dispatch fore-warn (beat 2). With no coalition standing
    the lowered gate brews one (`coalition_gate`)."""
    c = _store(world)
    coalition = getattr(world, "active_coalition", None) or {}
    player = _player(world)
    for court, row in sorted(table.items()):
        if row.get("stance") != REFUSES or row.get("by") not in ("formula", "withdrawn"):
            continue
        turns = refusal_turns(world, court)
        if march_blocker(world, court):
            continue
        if turns >= WAR_AFTER_REFUSALS - 1 and court not in (c.get("warned") or []):
            # The fore-warning ALWAYS precedes the war by one end turn: if
            # the blocker lifts late, the warning comes then, and the war the
            # turn after — never the two on one tick.
            c.setdefault("warned", []).append(court)
            c.setdefault("warned_turn", {})[court] = _turn(world)
            world.log_event({"type": "congress", "phase": "warning",
                             "nation": player, "court": court,
                             "message": (f"{seat(world, court)} warns: one more "
                                         f"turn of refusal, and it answers the "
                                         f"Congress with cannon.")})
            continue
        if turns < WAR_AFTER_REFUSALS:
            continue
        if int((c.get("warned_turn") or {}).get(court, -1)) >= _turn(world):
            continue
        from backend.game_logic.coalition import join_coalition
        result = join_coalition(world, court)
        if result.get("success"):
            world.log_event({"type": "congress", "phase": "war",
                             "nation": player, "court": court,
                             "coalition": str(coalition.get("name") or ""),
                             "message": (f"{seat(world, court)} answers the "
                                         f"Congress with cannon.")})
            # The stored answer moves with the court, so the next tick's
            # `_take_answers` does not log the same war a second time.
            c.setdefault("answers", {}).setdefault(court, {})["by"] = "war"


def _proclaim(world, turn_ended: int, *, route: str,
              table: Optional[Dict[str, Dict[str, Any]]] = None) -> Optional[Dict[str, Any]]:
    """THE IMPERIAL PEACE — stamped once (record_ending refuses a second),
    marked, never terminal (D7): Continue the reign / Retire."""
    from backend.game_logic import game_end
    from backend.game_logic.calendar import calendar_label
    c = _store(world)
    table = table if table is not None else {court: answer(world, court)
                                             for court in great_powers(world)}
    view = titled(world)
    courts = [{"nation": court, "display": _display(court),
               "stance": END_SCREEN_STANCE.get(row["stance"], row["stance"]),
               "by": row.get("by", "")}
              for court, row in table.items()]
    date = calendar_label(getattr(world, "start_date", ""), int(turn_ended))
    if route == "universal_monarchy":
        moniteur = (f"LE MONITEUR — Paris, {date}: No crown in Europe stands "
                    f"against the Emperor. The Universal Monarchy is proclaimed.")
    else:
        moniteur = (f"LE MONITEUR — Paris, {date}: The powers of Europe have "
                    f"signed at Paris. The Imperial Peace is proclaimed.")
    # Review #56: E1 fires without a Congress — only a SITTING Congress's
    # strip rides the card (never a dissolved one's, ending in ✗).
    strip = ([dict(s) for s in (c.get("strip") or []) if int(s.get("day", 0)) >= 1]
             if (route == "congress" or c.get("status") == SITTING) else [])
    detail = {
        "route": route,
        "number": int(c.get("number", 0) or 0),
        "summoned_turn": c.get("summoned_turn"),
        "courts": courts,
        "titled": int(view["count"]),
        "hold_titled": int(view["needed"]),
        "sitting": strip,
        "moniteur_line": moniteur,
    }
    rec = game_end.record_ending(world, "victory", game_end.CAUSE_IMPERIAL_PEACE,
                                 detail=detail, turn=int(turn_ended))
    if rec is None:
        return None
    if c.get("status") == SITTING:
        c["status"] = CONCLUDED
    c["concluded_turn"] = int(turn_ended)
    c["route"] = route
    c["petition_owed"] = False
    _restate_the_bills(world)
    return rec


def _dissolve(world, turn_ended: int, table: Dict[str, Dict[str, Any]],
              reason: Dict[str, Any]) -> None:
    """§2.6: alarm +15, a 10-turn cooldown, each refuser's 10-turn grudge,
    the marshals' expectation one rung up (they were promised the peace),
    and a beat naming the courts that would not sign. Not a defeat (D8)."""
    c = _store(world)
    # Review #9: the grudge is the REFUSERS' — a court still suing asked for
    # the peace, and is named apart.
    refusers = sorted(k for k, v in table.items() if v["stance"] == REFUSES)
    sued = sorted(k for k, v in table.items() if v["stance"] == SUES)
    c.update({"status": DISSOLVED, "dissolved_turn": int(turn_ended),
              "dissolve_reason": str(reason.get("text") or ""),
              "dissolve_key": str(reason.get("key") or ""),
              "refusers": refusers, "sued_at_the_end": sued,
              "petition_owed": False})
    from backend.game_logic.coalition import add_threat
    add_threat(world, dissolve_alarm(world), "congress_dissolved")
    raised = []
    from backend.game_logic import dotation
    for marshal in sorted((getattr(world, "marshals", {}) or {}).values(),
                          key=lambda m: m.name):
        if (marshal.nation != _player(world) or marshal.strength <= 0
                or getattr(marshal, "captured_by", "")
                or getattr(marshal, "is_sovereign", False)):
            continue
        if dotation.raise_expectation(marshal, world, "congress",
                                      ignore_cooldown=True):
            raised.append(marshal.name)
    c["expectation_raised"] = raised
    _restate_the_bills(world)
    world.log_event({"type": "congress", "phase": "dissolved",
                     "nation": _player(world), "refusers": refusers,
                     "sued": sued,
                     "reason": str(reason.get("text") or ""),
                     "key": str(reason.get("key") or ""),
                     "message": ("The Congress of Paris dissolves — "
                                 + str(reason.get("text") or "the hold broke") + ".")})


# ════════════════════════════════════════════════════════════════════════
# The latches — written by the seams elsewhere, read by the tick. Each
# returns at once when no Congress sits and no treaty latch exists.
# ════════════════════════════════════════════════════════════════════════

def note_ratification(world, parties: Iterable[str], war_ending: bool,
                      beaten: Iterable[str] = ()) -> None:
    """A war-ending treaty the player ratified with a great power latches
    its recognition (§2.4 — "the beaten court SUES; ratifying it flips the
    court to recognizes"). Called from `game_end.note_ratification` (both
    top-level ratifiers).

    Only a SIGNED peace latches, and only one of two kinds (review round,
    finding #0 — the first cut latched every war-ending peace at any time,
    so the commanded arm's turn-4 peace, or a peace in which France GAVE UP
    a province, settled three of the four answers years before the summons):

    * a peace ratified WHILE the Congress sits (the sue rung's peace, or any
      peace the Emperor signs at the table's own time), or
    * the peace of a BEATEN court — one that ceded provinces to the
      Emperor's bloc in this treaty (`beaten`, computed by the caller from
      the applied cessions: Pressburg, Tilsit).

    Any other peace feeds the at-peace formula like every court's. A truce
    that RUNS OUT into peace is not a signature and never latches (the ARMISTICE
    arm's price names the signed peace, the one road that does)."""
    if not war_ending or not armed(world):
        return
    powers = set(great_powers(world))
    beaten_set = set(beaten or ())
    now_sitting = sitting(world)
    signers = [p for p in (parties or []) if p in powers
               and (now_sitting or p in beaten_set)]
    if not signers:
        return
    c = _store(world)
    for court in signers:
        c.setdefault("signed", {})[court] = {
            "turn": _turn(world), "broken": None,
            "kind": "table" if now_sitting else "beaten"}
        if now_sitting:
            (c.get("withdrawn") or {}).pop(court, None)


def note_war_entry(world, nation_a: str, nation_b: str) -> None:
    """Every entry into WAR (the ONE diplomatic-state setter): a new war
    between France and a court breaks the court's treaty latch."""
    c = getattr(world, "congress", None)
    if not isinstance(c, dict) or not c.get("signed"):
        return
    player = _player(world)
    if player not in (nation_a, nation_b):
        return
    court = nation_b if nation_a == player else nation_a
    rec = (c.get("signed") or {}).get(court)
    if isinstance(rec, dict) and not rec.get("broken"):
        rec["broken"] = {"turn": _turn(world), "reason": "a new war"}


def note_declaration(world, aggressor: str, target: str) -> None:
    """France declares war during the sitting: "the Emperor who summons the
    Congress and then draws the sword has answered for Europe" (§2.5)."""
    if aggressor != _player(world) or not sitting(world):
        return
    c = _store(world)
    if target not in c.setdefault("declared", []):
        c["declared"].append(target)


def note_joined(world, joiner: str, target: str, ally: str) -> None:
    """The Emperor enters an ally's OFFENSIVE war during the sitting (the
    alliance cascade) — the hold reads it as drawing the sword (review #15:
    it had counted only his own declarations, so joining Spain's war on
    Prussia broke nothing and the chronicle blamed Berlin's cannon)."""
    if joiner != _player(world) or not sitting(world):
        return
    c = _store(world)
    c.setdefault("joined", {}).setdefault(target, ally)


def was_titled(world, region_name: str) -> bool:
    """Read BEFORE a capture changes the controller (the kind is written
    over by the capture itself)."""
    if not sitting(world):
        return False
    from backend.game_logic import game_end
    return game_end.province_title_kind(world, region_name, _player(world)) in (
        "homeland", "treaty", "conquest")


def note_capture(world, region_name: str, old_controller: str,
                 capturing_nation: str, was_titled: bool = False) -> None:
    """A capture by force (the two capture seams — `capture_region` and the
    auto-charge bypass). Non-force transfers (a treaty cession, a VS-3
    grant, a carve, an ultimatum yield) never come here.

    * A titled province of the player's bloc taken by anyone outside it
      breaks the hold (latched — "taken and retaken the same turn still
      breaks it").
    * France taking a province from a court's bloc or of its covets flips
      that court: a treaty latch is broken; a sitting recognizer withdraws.
    """
    c = getattr(world, "congress", None)
    if not isinstance(c, dict):
        return
    player = _player(world)
    capturer_top = world._top_overlord(capturing_nation) if capturing_nation else ""
    if sitting(world) and was_titled and capturer_top != player:
        if region_name not in c.setdefault("lost", []):
            c["lost"].append(region_name)
        # Review #63: a great power that seizes a titled province of our
        # bloc — at war with a satellite while at peace with us — does not
        # go on reading "it signed our peace". It withdraws, and the
        # dissolution counts it among the courts that would not sign.
        taker = capturer_top or capturing_nation
        if taker in great_powers(world) and not court_gone(world, taker):
            why = f"it took {region_name} from our bloc by force"
            rec = (c.get("signed") or {}).get(taker)
            if isinstance(rec, dict) and not rec.get("broken"):
                rec["broken"] = {"turn": _turn(world), "reason": why}
            c.setdefault("withdrawn", {})[taker] = f"it withdrew: {why}"
            (c.get("signed_at_table") or {}).pop(taker, None)
        return
    # Review #13: only the EMPEROR's own capture breaks a court's signature
    # or withdraws it — never a satellite's autonomous war (GE-1's ruling:
    # a satellite's own war does not unsign France's treaty).
    if capturing_nation != player:
        return
    if not (c.get("signed") or sitting(world)):
        return
    from backend.game_logic.agendas import get_agenda_covets
    for court in great_powers(world):
        if court_gone(world, court):
            continue
        from_bloc = bool(old_controller) and (
            old_controller == court
            or world._top_overlord(old_controller) == court
            or old_controller in set(world.get_bloc_members(court)))
        covets = region_name in set(get_agenda_covets(court, world) or [])
        if not (from_bloc or covets):
            continue
        why = (f"we took {region_name} from its bloc by force" if from_bloc
               else f"we took {region_name}, which it covets")
        rec = (c.get("signed") or {}).get(court)
        if isinstance(rec, dict) and not rec.get("broken"):
            rec["broken"] = {"turn": _turn(world), "reason": why}
        if sitting(world) and _was_signing(world, c, court):
            c.setdefault("withdrawn", {})[court] = f"it withdrew: {why}"
            (c.get("signed_at_table") or {}).pop(court, None)


def _was_signing(world, c: Dict[str, Any], court: str) -> bool:
    """Review #14: only a court that was RECOGNIZING (or shut out) withdraws
    — never one at war or in a truce with the Emperor (winning that war is
    the design's own counterplay), and never one that had not signed ("it
    withdraws its signature" of a court that never gave one)."""
    state = str(world.get_diplomatic_state(court, _player(world)) or "PEACE")
    if state in ("WAR", "ARMISTICE"):
        return False
    stored = ((c.get("answers") or {}).get(court) or {}).get("stance")
    if stored in (RECOGNIZES, SHUT_OUT) or court in (c.get("signed_at_table") or {}):
        return True
    # A recognition won mid-turn (bought at the table) is not yet stored.
    return answer(world, court, {"ignore_treaty": True}).get("stance") == RECOGNIZES


def note_rebellion(world, vassal_name: str, lord: str,
                   defected_to: str = "") -> None:
    """A satellite lost during the sitting breaks the hold — every rebellion
    exit (`vassal.record_vassal_break`) and a DEFECTION (VS-6: bought away by
    an enemy court, through `transfer_vassal` or into hostile independence —
    measured: Britain's gold took Saxony on the sitting's sixth day and the
    hold never heard of it)."""
    if lord != _player(world) or not sitting(world):
        return
    c = _store(world)
    if vassal_name not in c.setdefault("rebellions", []):
        c["rebellions"].append(vassal_name)
    if defected_to:
        c.setdefault("defections", {})[vassal_name] = defected_to


# ════════════════════════════════════════════════════════════════════════
# The pressure readers — read by the shared systems, 0/default when no
# Congress sits.
# ════════════════════════════════════════════════════════════════════════

def refusal_weight(world, nation: str, against: Optional[str]) -> int:
    """intent._derive_weight: a refuser's want against France rises
    `refuser_weight_per_turn` for every end turn it has refused."""
    if not THE_CONGRESS_HARDENS_REFUSERS or not against:
        return 0
    if against != _player(world) or not sitting(world):
        return 0
    return _int(world, "refuser_weight_per_turn", REFUSER_WEIGHT_PER_TURN) * refusal_turns(world, nation)


def revanche_weight(world, nation: str, agenda, against: Optional[str]) -> int:
    """A refuser's Revanche (an EMERGENT design) against France hardens."""
    if not THE_CONGRESS_HARDENS_REFUSERS or not against:
        return 0
    if against != _player(world) or not sitting(world):
        return 0
    params = getattr(agenda, "params", {}) or {}
    if not params.get("emergent"):
        return 0
    return REVANCHE_WEIGHT if nation in live_refusers(world) else 0


def live_refusers(world) -> List[str]:
    """The great powers REFUSING the Congress now — the LIVE answer (review
    #18: the pressure readers had read the answers stored at the last tick,
    so a court the player turned mid-turn — the receipt said "Prussia now
    RECOGNIZES the order" — was still enrolled by the coalition turn that
    runs inside the advance, BEFORE the tick). Empty when no Congress sits."""
    if not sitting(world):
        return []
    return sorted(court for court in great_powers(world)
                  if answer(world, court)["stance"] == REFUSES)


def spared_from_coalition(world, nation: str, target: Optional[str]) -> str:
    """While the Congress sits, the pressure it puts on Europe never marches
    a great power that ANSWERS it — recognizing or shut out — or one in a
    truce with the Emperor into a new coalition (review #10/#19/#41: the
    lowered gate, and even the stock gate at the eighth turn, enrolled
    Austria while it recognized by the peace it had signed; its war broke
    the latch, un-titled its cessions and dissolved the Congress with no
    French act). Returns the reason, or '' (dormant when no Congress sits)."""
    tgt = target or _player(world)
    if tgt != _player(world) or not sitting(world):
        return ""
    if nation not in great_powers(world) or court_gone(world, nation):
        return ""
    if str(world.get_diplomatic_state(nation, tgt) or "") == "ARMISTICE":
        return "in a truce with us"
    stance = answer(world, nation)["stance"]
    if stance == RECOGNIZES:
        return "it recognizes the Congress"
    if stance == SHUT_OUT:
        return "it is shut out of the Congress"
    return ""


def coalition_gate(world, target: Optional[str] = None) -> Optional[int]:
    """The coalition's brewing gate against `target` while the Congress sits
    and two great powers refuse — None when the stock gate stands."""
    if not THE_CONGRESS_LOWERS_THE_GATE:
        return None
    tgt = target or _player(world)
    if tgt != _player(world) or not sitting(world):
        return None
    if len(live_refusers(world)) < 2:
        return None
    return _int(world, "congress_alarm_gate", CONGRESS_ALARM_GATE)


def refuser_qualifies(world, nation: str, target: Optional[str]) -> bool:
    """The coalition's Congress arm: a great power REFUSING the Congress at
    peace with France qualifies whatever its relation (a court refusing
    out of fear alone would otherwise never march). Treaty partners above
    a pact are not marched out of their alliance."""
    if not THE_CONGRESS_LOWERS_THE_GATE:
        return False
    c = getattr(world, "congress", None)
    if not isinstance(c, dict) or c.get("status") != SITTING:
        return False
    tgt = target or _player(world)
    if tgt != _player(world) or not sitting(world):
        return False
    if nation not in great_powers(world):
        return False
    if nation in (getattr(world, "vassals", {}) or {}):
        return False
    if world.get_diplomatic_state(nation, tgt) not in (
            "PEACE", "NON_AGGRESSION", "OPEN_BORDERS"):
        return False
    return answer(world, nation)["stance"] == REFUSES


def grudge_contributions(world, budget: int) -> List[Dict[str, Any]]:
    """§2.6: each court that would not sign keeps a 10-turn grudge — +1
    threat a turn each, inside the shared AGENDA_GRUDGE_CAP (the NA-6d
    budget split: this family takes what the others leave)."""
    c = getattr(world, "congress", None)
    if not isinstance(c, dict) or c.get("status") != DISSOLVED:
        return []
    if c.get("dissolved_turn") is None or budget <= 0:
        return []
    if _turn(world) - int(c["dissolved_turn"]) >= GRUDGE_TURNS:
        return []
    alive = [r for r in (c.get("refusers") or []) if not court_gone(world, r)]
    amount = min(int(budget), GRUDGE_PER_REFUSER * len(alive))
    if amount <= 0:
        return []
    return [{"amount": amount, "source": "congress_grudge", "courts": alive}]


def close_on_fall(world, turn: int) -> None:
    """A terminal ending closes a sitting Congress — no alarm, cooldown or
    grudge (the Fall is the whole of the consequence), and no surface left
    reading "turn 9 of 8" or promising the Imperial Peace to a fallen
    Emperor (review #49). Called from `game_end.record_ending`."""
    c = record(world)
    if not isinstance(c, dict) or c.get("status") != SITTING:
        return
    c["status"] = ENDED
    c["ended_turn"] = int(turn)
    c["petition_owed"] = False


def _lapse_grudges(world) -> None:
    """Nothing to write — the grudge is a derived window (kept as the
    tick's no-Congress branch so the order of the reads is stated)."""
    return None


def peace_dividend(world, nation: Optional[str]) -> float:
    """×1.5 on the reward rail's rentes while the Congress sits — the
    summoner's own bill (GR5: 1.0 for every other court)."""
    if not THE_BILLS_COME_DUE or nation != _player(world) or not sitting(world):
        return 1.0
    return PEACE_DIVIDEND


def petition_stakes(world, lord: Optional[str]) -> int:
    """×2 on a client petition's loyalty stakes DURING the sitting — from its
    first day (turn summoned+1), as §2.5 rules. The bills presented AT the
    summons carry ordinary stakes: measured on the staged Pressburg board,
    five satellite asks arriving at once at ×2 (with the DP to grant only one
    of them after the summons' own 2) lapsed a fresh satellite below loyalty
    40, un-titled its homeland and broke the hold before the sitting began —
    a summons that dissolved itself. Quote == applied either way: a summons-
    turn petition is quoted and lapses on day 0."""
    if not THE_BILLS_COME_DUE or lord != _player(world) or not sitting(world):
        return 1
    if day_of_sitting(world) < 1:
        return 1
    return PETITION_STAKES


def _invalidate_intent(world) -> None:
    """The intent cache is per-turn; a summons or a tick changes a court's
    refusal count inside the turn (the formations `_agenda_cache` idiom)."""
    try:
        world._intent_cache = None
    except Exception:
        pass


# ════════════════════════════════════════════════════════════════════════
# The sweetener (§2.4 — "a sweetener the player attaches").
# ════════════════════════════════════════════════════════════════════════

def sweetener_refusal(world, court: str, amount: int) -> Optional[str]:
    if not armed(world):
        return "There is no Congress of Paris in this campaign."
    if not sitting(world):
        return ("A sweetener is paid at the table — summon the Congress first "
                f"({CABINET_HINT}).")
    if court not in great_powers(world):
        return f"{_display(court)} is not a great power — it has no seat at the Congress."
    if court_gone(world, court):
        return f"{_display(court)} is gone — it answers by construction."
    if world.is_at_war(court, _player(world)):
        return (f"We are at war with {_display(court)} — gold does not buy a "
                f"recognition in the middle of a war; beat it until it sues, or "
                f"make peace.")
    if int(amount) <= 0:
        return "Name the gold: offer a court 1000 gold for recognition."
    # Review #3/#30: gold moves only a court the FORMULA answers for. A court
    # that withdrew, that signed (by treaty or at the table), or that is shut
    # out cannot be moved — the verb refuses free, as the table says.
    row = answer(world, court)
    by = row.get("by")
    if by == "withdrawn":
        return (f"{_display(court)} withdrew from this sitting ({row.get('reason')}) "
                f"— no sweetener moves it; summon again after a dissolution.")
    if by in ("treaty", "table"):
        return f"{_display(court)} has signed — it already recognizes the order."
    if row["stance"] == SHUT_OUT:
        return (f"{_display(court)} is shut out of the Congress — the table does "
                f"not need her signature while the ports stay closed.")
    if row["stance"] == RECOGNIZES:
        return (f"{_display(court)} already recognizes the order "
                f"({row.get('score')} of {row.get('threshold')}) — its signature "
                f"is taken at this end turn; no gold is needed.")
    c = record(world) or {}
    paid = int((c.get("sweeteners") or {}).get(court, 0) or 0)
    cap = _int(world, "sweetener_cap", SWEETENER_CAP)
    per = _int(world, "sweetener_per_1000", SWEETENER_PER_1000)
    if per <= 0 or paid * per // 1000 >= cap:
        return (f"{_display(court)} already carries the most gold can buy at "
                f"this table (+{cap}).")
    if _sweetener_points(paid, sweetener_charge(world, court, amount), per, cap) <= 0:
        need = _sweetener_gold(paid, per, 1)
        return (f"{int(amount):,}g buys nothing at this table — every "
                f"{int(math.ceil(1000 / per)):,}g is one point (the next point "
                f"costs {need:,}g).")
    dp = int(getattr(world, "diplomatic_points", 0) or 0)
    if dp < SWEETENER_DP_COST:
        return (f"The sweetener is carried by an envoy — "
                f"{SWEETENER_DP_COST} diplomatic point, and {dp} remain.")
    gold = int((getattr(world, "nation_gold", {}) or {}).get(_player(world), 0) or 0)
    charge = sweetener_charge(world, court, amount)
    if gold < charge:
        return f"The treasury holds {gold:,}g — the sweetener asks {charge:,}g."
    return None


# A figure the player attached to money: "1000 gold", "1,500 gold", "800g",
# "1 000 gold", "2,000 ducats". Review #29: the executor had charged the
# FIRST number in the raw line, so a negated figure, a turn count or a year
# ("the treaty of 1805") was paid as gold.
_GOLD_FIGURE_RE = _re.compile(
    r"(?<![\w.])(\d{1,3}(?:[, ]\d{3})+|\d+)\s*(?:gold\b|g\b|ducats?\b|francs?\b)")
_BARE_FIGURE_RE = _re.compile(r"(?<![\w.])(\d{1,3}(?:,\d{3})+|\d+)(?![\w.])")
_NOT_GOLD_BEFORE_RE = _re.compile(r"(?:\bturns?|\bturn|\bin|\bof|\bon|\byear|\bday|\bdays)\s*$")


def sweetener_amount(text: str) -> tuple:
    """(amount, refusal) read off the GUARDED line — a negated clause and a
    deferred one are blanked first (`clause_guards`, PARSE-NEG's own
    guards), then the figure attached to gold is read. A bare figure counts
    only when it is the line's one number and is neither a year (1700–1899)
    nor a count of turns ("in 2 turns"). Two different gold figures refuse,
    naming both — the table never guesses which one the Emperor meant."""
    from backend.ai.clause_guards import strip_deferred_clauses, strip_negated_clauses
    guarded, _ = strip_negated_clauses(str(text or ""))
    guarded, _ = strip_deferred_clauses(guarded)
    lowered = guarded.lower()
    figures = [int(_re.sub(r"[, ]", "", m.group(1)))
               for m in _GOLD_FIGURE_RE.finditer(lowered)]
    distinct = sorted(set(figures))
    if len(distinct) > 1:
        shown = " and ".join(f"{g:,}g" for g in distinct[:2])
        return None, (f"The line names two sums ({shown}) — name one, Sire: "
                      f"'offer Prussia 1000 gold for recognition'.")
    if distinct:
        return distinct[0], None
    bare = []
    for m in _BARE_FIGURE_RE.finditer(lowered):
        value = int(m.group(1).replace(",", ""))
        before = lowered[:m.start()]
        if _NOT_GOLD_BEFORE_RE.search(before) or 1700 <= value <= 1899:
            continue
        bare.append(value)
    if len(set(bare)) == 1:
        return bare[0], None
    return None, None


def sweetener_charge(world, court: str, amount: int) -> int:
    """What the treasury actually pays: the offer, clipped to what the table
    still counts (gold past the cap buys nothing, and is not taken)."""
    c = record(world) or {}
    paid = int((c.get("sweeteners") or {}).get(court, 0) or 0)
    cap = _int(world, "sweetener_cap", SWEETENER_CAP)
    per = max(1, _int(world, "sweetener_per_1000", SWEETENER_PER_1000))
    room_gold = max(0, int(math.ceil(cap * 1000 / per)) - paid)
    return max(0, min(int(amount), room_gold))


def pay_sweetener(world, court: str, amount: int) -> Dict[str, Any]:
    refusal = sweetener_refusal(world, court, amount)
    if refusal:
        return {"success": False, "message": refusal}
    charge = sweetener_charge(world, court, amount)
    player = _player(world)
    before = answer(world, court)
    c0 = record(world) or {}
    paid_before = int((c0.get("sweeteners") or {}).get(court, 0) or 0)
    world.nation_gold[player] = int(world.nation_gold.get(player, 0)) - charge
    world.nation_gold[court] = int(world.nation_gold.get(court, 0) or 0) + charge
    try:
        world.record_gold_spent(player, charge)
    except Exception:
        pass
    c = _store(world)
    c.setdefault("sweeteners", {})[court] = int(
        (c.get("sweeteners") or {}).get(court, 0) or 0) + charge
    after = answer(world, court)
    per = _int(world, "sweetener_per_1000", SWEETENER_PER_1000)
    cap = _int(world, "sweetener_cap", SWEETENER_CAP)
    moved = _sweetener_points(paid_before, charge, per, cap)
    world.log_event({"type": "congress", "phase": "sweetener",
                     "nation": player, "court": court, "amount": int(charge),
                     "stance": after["stance"],
                     "message": (f"{charge:,}g laid before "
                                 f"{seat(world, court)} at the Congress.")})
    turned = before["stance"] != RECOGNIZES and after["stance"] == RECOGNIZES
    if turned:
        tail = f" {_display(court)} now RECOGNIZES the order."
    elif after.get("score") is not None and after.get("by") == "formula":
        tail = (f" {_display(court)} still {after['stance']} ({after.get('score')} of "
                f"{after.get('threshold')}).")
    else:
        tail = f" {_display(court)} still {after['stance']}."
    clipped = (f" (Only {charge:,}g of the {int(amount):,}g offered counts at "
               f"this table.)" if charge < int(amount) else "")
    return {"success": True, "charge": charge, "points": int(moved),
            "message": (f"{charge:,}g is laid before {seat(world, court)} "
                        f"(+{moved}).{clipped}{tail}"),
            "stance": after["stance"]}


# ════════════════════════════════════════════════════════════════════════
# The surfaces — ONE payload, ONE line.
# ════════════════════════════════════════════════════════════════════════

def phase(world) -> str:
    """'sitting' / 'cooldown' / 'concluded' / 'ended' / 'gate' ('' when
    unarmed). 'ended': a Fall closed the campaign — no surface says a
    Congress sits or may be summoned (review #49)."""
    if not armed(world):
        return ""
    if imperial_peace_signed(world):
        return "concluded"
    from backend.game_logic import game_end
    if game_end.terminal_ending(world) is not None:
        return "ended"
    c = record(world) or {}
    if c.get("status") == SITTING:
        return "sitting"
    if cooldown_left(world) > 0:
        return "cooldown"
    return "gate"


def _grouped_stances(world, table: Dict[str, Dict[str, Any]]) -> str:
    """"Austria REFUSES (Savoy) · Britain SHUT OUT · Prussia, Russia
    RECOGNIZE" — one group per stance, REFUSES/SUES named with their cause."""
    parts: List[str] = []
    order = [REFUSES, SUES, SHUT_OUT, RECOGNIZES, GONE]
    for stance in order:
        courts = [c for c in great_powers(world) if (table.get(c) or {}).get("stance") == stance]
        if not courts:
            continue
        if stance in (REFUSES, SUES):
            for court in courts:
                row = table[court]
                cause = _short_cause(row)
                parts.append(f"{_display(court)} {stance}" + (f" ({cause})" if cause else ""))
            continue
        names = ", ".join(_display(c) for c in courts)
        verb = stance
        if stance == RECOGNIZES and len(courts) > 1:
            verb = "RECOGNIZE"
        parts.append(f"{names} {verb}")
    return " · ".join(parts)


def _short_cause(row: Dict[str, Any]) -> str:
    if row.get("by") == "war":
        return "at war" if row.get("stance") == REFUSES else "beaten"
    if row.get("by") == "withdrawn":
        # Review #47: never a formula term for a court no lever can turn.
        m = _re.search(r"took (.+?)(?: from | which|,|$)", str(row.get("reason") or ""))
        return f"withdrew: {m.group(1)}" if m else "withdrew"
    for comp in sorted(row.get("components") or [], key=lambda c: c["value"]):
        if comp["key"] == "design" and comp["value"] < 0:
            design = (row.get("components") and comp.get("label")) or ""
            inside = design[design.find("(") + 1:design.rfind(")")] if "(" in design else ""
            return inside or "its design"
        if comp["value"] < 0 and comp["key"] != "jitter":
            return comp["label"]
    return ""


def state_line(world) -> Optional[str]:
    """The clock in ONE line — the war room, the Territories tab, the
    end-turn banner and the R screen read it (ENDGAME_PLAN §2.5/§4)."""
    ph = phase(world)
    if ph in ("", "concluded", "ended"):
        return None
    view = titled(world)
    have, need = view["count"], view["needed"]
    c = record(world) or {}
    if ph == "sitting":
        total = congress_turns(world)
        day = day_of_sitting(world)
        table = {court: answer(world, court) for court in great_powers(world)}
        head = (f"THE CONGRESS SITS — turn {day} of {total}" if day >= 1 else
                f"THE CONGRESS SITS — the powers gather; the sitting opens at "
                f"this end turn ({total} turns)")
        return f"{head} · {have} of {need} titled · {_grouped_stances(world, table)}"
    if ph == "cooldown":
        from backend.display_names import plural
        left = cooldown_left(world)
        again = int(c.get("dissolved_turn", 0)) + cooldown_turns(world)
        return (f"THE CONGRESS OF PARIS — dissolved on turn {c.get('dissolved_turn')}; "
                f"it may be summoned again on turn {again} ({plural(left, 'turn')} "
                f"{'remains' if left == 1 else 'remain'}) · {have} of {need} titled")
    held = view["held"]
    if have < need:
        tail = ""
        if held:
            shown = ", ".join(held[:3]) + (" …" if len(held) > 3 else "")
            tail = f" ({len(held)} held, unsettled: {shown})"
        return f"THE CONGRESS OF PARIS — {have} of {need} titled{tail} · {CABINET_HINT}"
    blocker = next((t for t in gate_terms(world)
                    if not t["met"] and t["key"] not in ("admin", "dp")), None)
    if blocker is not None:
        # Review #52: the BREACH, never the condition ("· the Emperor free"
        # had read as true while he sat in a cell).
        return (f"THE CONGRESS OF PARIS — {have} of {need} titled · "
                f"{blocker.get('breach') or blocker['text']}")
    return (f"THE CONGRESS OF PARIS — {have} of {need} titled · the powers may be "
            f"summoned — {CABINET_HINT}")


def clock_severity(world) -> str:
    ph = phase(world)
    if ph == "sitting":
        total = congress_turns(world)
        left = total - day_of_sitting(world)
        table = {court: answer(world, court) for court in great_powers(world)}
        unsigned = any(row["stance"] not in SATISFIED for row in table.values())
        return "critical" if (unsigned and left <= 2) else "warning"
    if ph == "cooldown":
        return "paused"
    return "gate"


def clock_payload(world) -> Optional[Dict[str, Any]]:
    """{line, severity, phase} — the sibling of `fall.clock_lines` every
    clock surface reads. None where the rules are not armed or after the
    Imperial Peace."""
    line = state_line(world)
    if not line:
        return None
    payload = {"line": line, "severity": clock_severity(world), "phase": phase(world)}
    if payload["phase"] == "gate":
        # SR-1c: each held province's road to title, for the Territories tab.
        from backend.game_logic import game_end as _ge
        payload["held_roads"] = _ge.title_roads(world, _player(world))
    return payload


def build_congress_payload(world) -> Optional[Dict[str, Any]]:
    """The table — the CONGRESS ledger tab, `GET /congress`, the wizard row,
    the war room and the Moniteur column all read THIS (ints only, GR2)."""
    if not armed(world):
        return None
    ph = phase(world)
    view = titled(world)
    c = record(world) or {}
    courts = []
    concluded = _concluded_courts(world) if ph == "concluded" else None
    for court in great_powers(world):
        if concluded is not None:
            # Review #55: after the Imperial Peace the table is the ENDING's
            # own — SIGNED / SHUT OUT / GONE as stamped — never a live
            # re-read (the sweetener counts only while it sits, so a court
            # that signed with gold read REFUSES again the moment it was
            # stamped, with a price no Congress can ever take).
            courts.append(concluded.get(court) or {
                "nation": court, "display": _display(court),
                "seat": seat(world, court), "stance": GONE, "by": "",
                "reason": "", "price": "", "levers": [], "score": None,
                "threshold": int(recognition_threshold(world))})
            continue
        row = answer(world, court)
        pr = price(world, court, row)
        entry = {
            "nation": court,
            "display": _display(court),
            "seat": seat(world, court),
            "stance": row["stance"],
            "by": row.get("by", ""),
            "reason": row.get("reason", ""),
            "price": pr.get("text", ""),
            "levers": [{k: (int(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v)
                        for k, v in lv.items() if k in ("key", "text", "value", "gold", "command")}
                       for lv in pr.get("levers") or []],
            # A withdrawn court's reckoning is no road back (review #30) —
            # only the formula's score is shown.
            "score": (int(row["score"]) if row.get("score") is not None
                      and row.get("by") == "formula" else None),
            "threshold": int(row.get("threshold") or recognition_threshold(world)),
        }
        if ph == "sitting" and row["stance"] == REFUSES and row.get("by") in ("formula", "withdrawn"):
            entry["refusing_turns"] = int(refusal_turns(world, court))
            blocker = march_blocker(world, court)
            if blocker:
                entry["march_blocker"] = blocker
            else:
                entry["war_in"] = int(war_in(world, court))
        courts.append(entry)
    terms = gate_terms(world)
    payload: Dict[str, Any] = {
        "armed": True,
        "phase": ph,
        "sitting": ph == "sitting",
        "number": int(c.get("number", 0) or 0),
        "titled": int(view["count"]),
        "titled_needed": int(view["needed"]),
        "held_unsettled": list(view["held"]),
        # SR-1c: the road each held province has to title, and the alarm's.
        "held_roads": [dict(r) for r in _title_roads(world)],
        "alarm_road": alarm_road(world),
        "state_line": state_line(world) or "",
        "severity": clock_severity(world),
        "courts": courts,
        "gate_terms": [{"text": t["text"], "met": bool(t["met"])} for t in terms],
        "available": all(t["met"] for t in terms),
        "unavailable_reason": _unavailable_reason(terms),
        "cost_text": summons_cost_text(world),
        "command": SUMMON_COMMAND,
        "cooldown_left": int(cooldown_left(world)),
        "turns": int(congress_turns(world)),
    }
    if ph == "sitting":
        payload.update({
            "summoned_turn": int(c.get("summoned_turn", 0)),
            "ends_turn": int(c.get("ends_turn", 0)),
            "day": int(day_of_sitting(world)),
            "turns_left": int(max(0, congress_turns(world) - day_of_sitting(world))),
            "hold": [{"text": h["text"], "met": bool(h["met"])} for h in hold_conditions(world)],
            "strip": [dict(s) for s in (c.get("strip") or [])],
        })
    if ph == "cooldown":
        # Review #53: the tab says what BROKE (the chronicle's one sentence),
        # never the hold condition's own words ("Paris held").
        from backend.campaign_log import congress_dissolve_reason
        payload["dissolve_reason"] = congress_dissolve_reason(
            c.get("dissolve_key"), c.get("dissolve_reason"))
        payload["refusers"] = list(c.get("refusers") or [])
    return payload


def _title_roads(world) -> List[Dict[str, Any]]:
    from backend.game_logic import game_end as _ge
    return _ge.title_roads(world, _player(world))


def _concluded_courts(world) -> Dict[str, Dict[str, Any]]:
    from backend.game_logic import game_end
    rec = next((e for e in game_end.endings(world)
                if e.get("cause") == game_end.CAUSE_IMPERIAL_PEACE), None)
    detail = (rec or {}).get("detail") or {}
    stance_of = {v: k for k, v in END_SCREEN_STANCE.items()}
    out: Dict[str, Dict[str, Any]] = {}
    for x in detail.get("courts") or []:
        court = str(x.get("nation") or "")
        if not court:
            continue
        shown = str(x.get("stance") or "")
        out[court] = {"nation": court, "display": _display(court),
                      "seat": seat(world, court),
                      "stance": stance_of.get(shown, shown), "signed": shown,
                      "by": str(x.get("by") or ""),
                      "reason": ("it signed the Imperial Peace" if shown == "SIGNED"
                                 else "shut out of the Continent" if shown == "SHUT OUT"
                                 else "gone"),
                      "price": "", "levers": [], "score": None,
                      "threshold": int(recognition_threshold(world))}
    return out


def _unavailable_reason(terms: List[Dict[str, Any]]) -> str:
    """Review #60: a TERMINAL term (the Imperial Peace signed, a Congress
    already sitting, no great power left) outranks a missing administrative
    action — "no action remains this turn" implied a summons next turn that
    could never come."""
    for key in ("fallen", "signed", "sitting", "monarchy"):
        term = next((t for t in terms if t["key"] == key and not t["met"]), None)
        if term is not None:
            return str(term.get("refusal") or "")
    return next((str(t.get("refusal", "")) for t in terms if not t["met"]), "")


def war_in(world, court: str) -> int:
    """End turns until the War of the Congress takes `court` at the earliest
    (the warning always comes one end turn before the war). Read only when
    `march_blocker` is empty."""
    turns = refusal_turns(world, court)
    c = record(world) or {}
    if court in (c.get("warned") or []):
        return max(1, WAR_AFTER_REFUSALS - turns)
    return max(1, WAR_AFTER_REFUSALS - 1 - turns) + 1


def rente_surcharge(world) -> int:
    """What the peace dividend adds to the summoner's standing rente bill a
    turn (review #38: the summons was priced at 2 DP + 1 action while it also
    raised every rente on the books by half, from its own end turn)."""
    if not THE_BILLS_COME_DUE:
        return 0
    from backend.game_logic import dotation
    if not dotation.is_dotation_world(world):
        return 0
    player = _player(world)
    extra = 0
    for m in (getattr(world, "marshals", {}) or {}).values():
        if m.nation != player or getattr(m, "captured_by", ""):
            continue
        face = int(getattr(m, "pension", 0) or 0)
        if face <= 0:
            continue
        extra += (int(math.ceil(dotation.RENTE_PREMIUM * PEACE_DIVIDEND * face))
                  - int(math.ceil(dotation.RENTE_PREMIUM * face)))
    return int(extra)


def summons_cost_text(world) -> str:
    text = f"{SUMMON_DP_COST} diplomatic points + 1 administrative action"
    extra = rente_surcharge(world)
    if extra > 0:
        text += (f"; and while it sits, from this end turn, your rentes cost "
                 f"×{PEACE_DIVIDEND:g} (+{extra:,}g a turn)")
    return text


def gazette_rows(world) -> List[str]:
    """The Congress column's table: one line per court in the paper's voice."""
    if not sitting(world):
        return []
    lines: List[str] = []
    for court in great_powers(world):
        row = answer(world, court)
        s = row["stance"]
        where = seat(world, court)
        if s == RECOGNIZES:
            lines.append(f"{where} has signed.")
        elif s == SHUT_OUT:
            lines.append(f"{where} is shut out — the ports of the Continent are closed to her.")
        elif s == GONE:
            continue
        elif s == SUES:
            lines.append(f"{where} sues for peace.")
        else:
            lines.append(f"{where} refuses — {row.get('reason') or 'it will not sign'}.")
    return lines


def summary_block(detail: Dict[str, Any]) -> Dict[str, Any]:
    """The end screen's Congress block, built from the ending's own detail —
    never from live state (the summary is persisted at the stamp)."""
    detail = detail or {}
    return {
        "route": str(detail.get("route") or "congress"),
        "number": int(detail.get("number") or 0),
        "courts": [dict(x) for x in (detail.get("courts") or [])],
        "titled": int(detail.get("titled") or 0),
        "hold_titled": int(detail.get("hold_titled") or 0),
        "sitting": [dict(x) for x in (detail.get("sitting") or [])],
        "moniteur_line": str(detail.get("moniteur_line") or ""),
    }


def counsel(world) -> Optional[Dict[str, Any]]:
    """Talleyrand's rung while the Congress sits: the biggest blocker and
    its price (the refuser with the largest gap; a war refuser outranks)."""
    if not sitting(world):
        return None
    worst = None
    for court in great_powers(world):
        row = answer(world, court)
        if row["stance"] in SATISFIED:
            continue
        pr = price(world, court, row)
        weight = (1000 if row.get("by") == "war" else 0) + int(pr.get("gap", 0) or 0)
        if worst is None or weight > worst[0]:
            worst = (weight, court, row, pr)
    if worst is None:
        return None
    _, court, row, pr = worst
    return {"court": court, "stance": row["stance"], "reason": row.get("reason", ""),
            "price": pr.get("text", "")}
