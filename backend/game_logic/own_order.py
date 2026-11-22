"""Row IC, Session 3 (IC-10 / IC-11) — A MARSHAL ON HIS OWN.

`docs/INDEPENDENT_COMMAND_SPEC.md` §6 (the rules), §8.6 (talking to him), §12
(the edge cases), §13 (R-ACTS, R-TOGETHER, R-FRIENDS, R-TRUE, R-VARIETY). The
user's direction for this session, verbatim: "make sure when you give genmrals
autonomy they really do stuff and iunteract withe achother and even help their
friends your strategoic suggestions are just guidance for ai".

WHAT IT IS. A standing order — take a place, pursue a named enemy army, hold one
or two provinces, support a friend — that a BOLD or CAREFUL marshal carries out
by his own judgement. Your task names the aim and the area; each night's act is
HIS choice inside it, by his nature, his odds, his record and the men beside
him — and it is shown under "Tonight" before you end the turn (D8: what the
screen said, or he stays put).

THE ORDER. `StrategicOrder.own` (a dict; the order keeps its standing type, so
every reader that asks "has he an order?" still says yes). The strategic pass
SKIPS an own order (`strategic.process_strategic_orders`): the cannon-fire
redirect, the stalemate questions, the careful man's dig-in and the bold man's
sally never touch him. His if-thens (two at most) are still read by the
if-then sub-pass — only on a night he waited (`acted_tonight`).

THE ONE READING. `read` / `tonight` are PURE — no write, no die, France's own
sight — and serve "Tonight" (the desk, the card, the End Turn list), the
read-back's "Tomorrow night", every question you ask him, and THE PASS that
carries the act out. So what you read is what he does.

THE PASS (`the_pass`) runs FIRST of all when you end the turn — before the
Congress signs, before the offers lapse, before the jealous strikes, before the
enemy moves (D6) — highest rank first (`precedence.order_of_precedence`), one
thing a turn (D7). Each man's act is re-read on the board the higher men left:
if it is what "Tonight" said, it is carried out through the executor (free —
`_strategic_execution`); otherwise he stays put and says why (D8).

HIS FRIENDS (R-FRIENDS). Every man on his own may answer the battle of any of
our corps attacked next to him — dug in or on his hold's post — by the game's
own arrival roll ("may"), never a man he hates (`answers_the_guns`, read by
`combat_executor._is_reinforcement_eligible` and `_muster_reason`). It is the one
exception to "one thing a turn".

TOGETHER (R-TOGETHER). Never two attacks on one enemy: a lower man whose target
a higher man has taken stands beside the lead (the arrival roll may bring him
into that ONE battle — the lead's forecast already counts him) or moves up
beside him, or takes his next target / his way of waiting; a man the lead's
forecast counts on is read as joining him.

THE COUNT. "On their own: n of N" — N = 1, +1 with the Staff, +1 with the
Emperor's Aides-de-Camp (the law effect `on_their_own`). Authority never moves
N (D31).
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from backend.display_names import humanize_entity_name
from backend.errors import report

# ═══════════════════════════ numbers (§13) ═══════════════════════════════════
COUNT_AT_START = 1
LAW_EFFECT = "on_their_own"
TRUST_NEEDED = 30            # the game's own line between Wary and Hostile
DEFAULT_ODDS = {"aggressive": 7, "cautious": 11}
ODDS_FLOOR, ODDS_CEILING = 3, 20     # the validator's clamp on an authored figure
MOST_STEPS = 2               # one from you + one from him
IMPATIENT_AFTER = 3          # a bold man's quiet nights before he grows impatient
ASK_LAPSE = 3                # an unanswered ask ends the order after three turns
BARRED_ASKS_AFTER = 2        # a road barred two turns: he asks
WAITS_ASKS_AFTER = 3         # his target in reach but beyond his odds three nights: he asks
UNSEEN_ASKS_AFTER = 3        # a pursued army unseen three turns: he asks
PURSUE_RING = 3              # marches from where the pursuit began
STAND_DOWN_TRUST = 3         # recalled mid-task by your choice
PRICE = {"take": 2, "pursue": 2, "hold": 2, "support": 1}
CHANGE_PRICE = 1
EVENT = "own_night"          # the campaign log's and the dispatch's event type

TASKS = ("take", "pursue", "hold", "support")
ORDER_TYPE = {"take": "MOVE_TO", "pursue": "PURSUE", "hold": "HOLD", "support": "SUPPORT"}
TASK_OF_ORDER = {v: k for k, v in ORDER_TYPE.items()}

# The acts of a night. WAITING acts leave his if-thens live (§2, §6.7.3).
WAITING_ACTS = frozenset({"look", "dig_in", "stay", "start", "asks", "recover"})
VISIBLE_ACTS = frozenset({"attack", "storm", "besiege", "take", "march", "move_up", "join",
                          "look", "probe", "dig_in", "fall_back", "strike"})


# ═══════════════════════════ the state ══════════════════════════════════════

def _int(spec: Optional[Dict[str, Any]], key: str, default: int = -1) -> int:
    """A turn number off the task (never through `or`: turn 0 is a turn)."""
    value = (spec or {}).get(key)
    try:
        return int(value) if value is not None else int(default)
    except (TypeError, ValueError):
        return int(default)


def own(marshal) -> Optional[Dict[str, Any]]:
    """His task on his own, or None."""
    order = getattr(marshal, "strategic_order", None)
    state = getattr(order, "own", None) if order is not None else None
    return state if isinstance(state, dict) else None


def on_his_own(marshal) -> bool:
    """THE one reader of the state — the exemptions, the count, every surface."""
    return own(marshal) is not None


def _nature(marshal) -> str:
    return {"aggressive": "bold", "cautious": "careful", "literal": "literal",
            "sovereign": "sovereign"}.get(str(getattr(marshal, "personality", "") or ""), "")


def _shown(name: str) -> str:
    return humanize_entity_name(str(name or ""))


def _turn(world) -> int:
    return int(getattr(world, "current_turn", 0) or 0)


def _player(world) -> str:
    return str(getattr(world, "player_nation", "") or "")


def _seats(world) -> Dict[str, int]:
    try:
        from backend.game_logic import precedence as _court
        return {m.name: n for n, m in enumerate(_court.order_of_precedence(world, _player(world)))}
    except Exception as exc:
        report(exc, "own_order._seats: order_of_precedence")
        return {}


def men(world) -> List[Any]:
    """Every man of ours on his own, highest rank first (then by name)."""
    nation = _player(world)
    found = [m for m in (getattr(world, "marshals", None) or {}).values()
             if m.nation == nation and on_his_own(m)]
    if not found:
        return []
    seats = _seats(world)
    return sorted(found, key=lambda m: (seats.get(m.name, len(seats)), m.name))


def record(marshal) -> Dict[str, Any]:
    """His saved nights (kept across orders): the last three acts, his quiet
    nights, his last battle's result."""
    rec = getattr(marshal, "own_record", None)
    if not isinstance(rec, dict):
        rec = {}
    rec.setdefault("acts", [])
    rec.setdefault("quiet", 0)
    rec.setdefault("last", "")
    return rec


def _record_view(marshal) -> Dict[str, Any]:
    """The same, read without writing (the reading is PURE)."""
    rec = getattr(marshal, "own_record", None)
    rec = rec if isinstance(rec, dict) else {}
    return {"acts": list(rec.get("acts") or []), "quiet": int(rec.get("quiet", 0) or 0),
            "last": str(rec.get("last") or ""), "said": str(rec.get("said") or ""),
            "held": bool(rec.get("held")), "idle_run": int(rec.get("idle_run", 0) or 0)}


# ═══════════════════════════ the count (§6.4) ═══════════════════════════════

def allowed(world, nation: Optional[str] = None) -> int:
    """N: one at the start; one more for each law in force with the effect
    `on_their_own` (the Staff, the Emperor's Aides-de-Camp)."""
    nation = nation or _player(world)
    total = COUNT_AT_START
    try:
        from backend.game_logic import reforms as _reforms
        for row, clause in _reforms.effect_terms(world, nation, LAW_EFFECT):
            # a law that needs another in force (the Aides need the Staff)
            # counts only while that one stands
            if _reforms.requires_law_refusal(world, nation, row):
                continue
            total += int(clause.get("value", 0) or 0)
    except Exception as exc:
        report(exc, "own_order.allowed: effect_terms")
    return max(COUNT_AT_START, int(total))


def count(world) -> int:
    return len(men(world))


def count_words(world) -> str:
    """"On their own: 1 of the 2 you may have" — the desk's line (the blind
    reading: "1 of 1" read as a count or a cap, nobody could tell)."""
    return f"On their own: {count(world)} of the {allowed(world)} you may have"


def why_not(world, marshal, task: str = "", *, replacing: bool = False) -> str:
    """Why he cannot be set on his own (for `task`), in plain words — "" when
    he can (§6.2). `replacing`: he is on his own already (a change)."""
    if marshal is None:
        return "there is no such marshal"
    shown = _shown(marshal.name)
    if marshal.nation != _player(world):
        return f"{shown} is not one of your marshals"
    nature = _nature(marshal)
    if nature == "sovereign":
        return "the Emperor commands himself"
    if nature == "literal":
        return f"{shown} follows orders to the letter — he takes exact orders, never a task on his own"
    if nature not in ("bold", "careful"):
        return f"only a bold or a careful marshal can be set on his own"
    if int(getattr(marshal, "strength", 0) or 0) <= 0 or getattr(marshal, "captured_by", ""):
        return f"{shown} has no corps to command"
    try:
        from backend.game_logic import trial as _trial
        if _trial.on_trial(marshal):
            return f"{shown} is on his task to prove himself"
    except Exception as exc:
        report(exc, "own_order.why_not: trial")
    trust = int(getattr(getattr(marshal, "trust", None), "value", 0) or 0)
    if trust < TRUST_NEEDED:
        return f"{shown}'s trust in you is {trust} — he needs {TRUST_NEEDED} to be trusted on his own"
    if getattr(marshal, "artillery", False) and task in ("take", "pursue"):
        return f"{shown}'s guns can only hold or support on their own"
    if task in ("take", "pursue") and not _at_war(world):
        return "at peace only a hold or a support can be given — a take or a pursuit needs a war"
    if not replacing and count(world) >= allowed(world):
        return (f"the count is full — {count_words(world).lower()}. Stand someone down first, "
                f"or give it as an exact order")
    return ""


def _at_war(world) -> bool:
    try:
        nation = _player(world)
        return bool(world.get_enemies_of_nation(nation)) or any(
            world.is_at_war(nation, other) for other in (world.get_active_nations() or [])
            if other != nation)
    except Exception as exc:
        report(exc, "own_order._at_war")
        return True


# ═══════════════════════════ his odds (§6.1, §6.7.6) ════════════════════════

def his_odds(marshal) -> int:
    """His own figure — "our N to their 10" — authored in the scenario file
    (`own_odds`), else by nature (bold 7, careful 11)."""
    authored = int(getattr(marshal, "own_odds", 0) or 0)
    if authored:
        return max(ODDS_FLOOR, min(ODDS_CEILING, authored))
    return DEFAULT_ODDS.get(str(getattr(marshal, "personality", "") or ""), 10)


def _his_step(marshal, rec: Dict[str, Any], reaching: bool = False) -> Tuple[int, str]:
    """`(steps bolder, why)` from him — ONE step at most, however many apply
    (§6.1): impatience, his last win, Ney reaching an enemy (bolder); his last
    defeat (more careful). Read from nights already past: a question cannot
    move it."""
    nature = _nature(marshal)
    key = str(getattr(marshal, "name", "") or "")
    if nature == "bold" and int(rec.get("quiet", 0) or 0) >= IMPATIENT_AFTER:
        return 1, f"after {int(rec.get('quiet', 0))} quiet nights — he is impatient"
    if rec.get("last") == "won":
        return 1, "since his last win"
    if rec.get("last") == "lost":
        return -1, "since his last defeat"
    if key == "Ney" and reaching:
        return 1, "as is his way with an enemy in reach"
    return 0, ""


def needed(marshal, risk: int = 0, rec: Optional[Dict[str, Any]] = None,
           reaching: bool = False) -> Dict[str, Any]:
    """The figure he attacks at tonight: his own, a step from you (`risk`: +1
    more risk, −1 less), a step from him — two at most in all."""
    rec = rec if rec is not None else _record_view(marshal)
    base = his_odds(marshal)
    you = max(-1, min(1, int(risk or 0)))
    him, why = _his_step(marshal, rec, reaching)
    figure = base - you - him
    figure = max(base - MOST_STEPS, min(base + MOST_STEPS, figure))
    return {"own": base, "you": you, "him": him, "him_why": why, "needed": max(1, figure)}


def needed_words(n: Dict[str, Any]) -> str:
    """"our 5 to their 10 (his own 6, one step bolder from you)"."""
    parts = []
    if n.get("you"):
        parts.append("one step bolder from you" if n["you"] > 0 else "one step more careful from you")
    if n.get("him"):
        word = "bolder" if n["him"] > 0 else "more careful"
        parts.append(f"one step {word} {n.get('him_why') or ''}".strip())
    tail = f" (his own {n['own']}, " + ", ".join(parts) + ")" if parts else ""
    return f"our {n['needed']} to their 10 or better{tail}"


def _tenths(ratio: float) -> str:
    value = round(float(ratio) * 10.0, 1)
    return f"{value:.0f}" if abs(value - round(value)) < 0.05 or value >= 20 else f"{value:.1f}"


def odds_against(world, marshal, enemy) -> Optional[Dict[str, Any]]:
    """The game's own battle forecast for HIS attack on `enemy`, as France knows
    it (§6.1): an exact sighting reads the muster's own ratio (ground, walls and
    the corps that would join him count); a partial one reads his force (with
    the corps that would join) against the middle of the enemy's band; no
    reading → None (he never attacks what France cannot see). PURE."""
    try:
        from backend.commands import order_quotes as _q
        force = _q._force_block(world, marshal, enemy)
        if not force:
            return None
        low, high = int(force.get("theirs_low", 0) or 0), int(force.get("theirs_high", 0) or 0)
        if low <= 0 and high <= 0:
            return None
        joining = [str(n) for n in (force.get("joining") or [])]
        exact = low == high
        if exact:
            reader = _q._MUSTER_READER.get("combat")
            muster = reader.muster_odds(marshal, enemy, world) if reader is not None else {}
            ratio = float(muster.get("ratio", 0.0) or 0.0)
            if ratio <= 0.0:
                ratio = float(force.get("ours_weight", 0) or 0) / float(max(1, low))
        else:
            mid = (low + high) / 2.0 if high else float(low)
            ratio = float(force.get("ours_weight", 0) or 0) / float(max(1.0, mid))
        return {"ratio": ratio, "tenths": _tenths(ratio), "exact": exact, "joining": joining,
                "theirs": str(force.get("theirs_label") or ""),
                "weight": int(force.get("ours_weight", 0) or 0), "theirs_low": low,
                "theirs_high": high}
    except Exception as exc:
        report(exc, "own_order.odds_against")
        return None


# ═══════════════════════════ what France sees (PURE) ════════════════════════

def _visible(world, place: str) -> bool:
    try:
        from backend.models.intel import FULL, PARTIAL
        return world.get_region_intel(place).visibility in (FULL, PARTIAL)
    except Exception as exc:
        report(exc, "own_order._visible")
        return False


def _full(world, place: str) -> bool:
    try:
        from backend.models.intel import FULL
        return world.get_region_intel(place).visibility == FULL
    except Exception as exc:
        report(exc, "own_order._full")
        return False


def _foes_at(world, marshal, place: str) -> List[Any]:
    """The enemy corps France SEES at `place`, strongest first."""
    if not place or not _visible(world, place):
        return []
    out = []
    try:
        from backend.commands.ground import _visible_foes
        for enemy in _visible_foes(world, place, marshal.nation):
            if getattr(enemy, "captured_by", ""):
                continue
            out.append(enemy)
    except Exception as exc:
        report(exc, "own_order._foes_at")
    out.sort(key=lambda e: (-_known(world, e), e.name))
    return out


def _known(world, enemy) -> int:
    from backend.commands import if_thens as _it
    return int(_it.known_strength(world, enemy))


def _near(world, place: str) -> List[str]:
    region = world.get_region(place) if place else None
    return [n for n in (getattr(region, "adjacent_regions", None) or []) if n != place]


def _distance(world, a: str, b: str) -> Optional[int]:
    if not a or not b:
        return None
    if a == b:
        return 0
    try:
        d = world.get_distance(a, b)
    except Exception as exc:
        report(exc, "own_order._distance")
        return None
    return int(d) if d is not None and int(d) >= 0 else None


def _in_strike_reach(world, marshal, place: str) -> bool:
    """The attack's own range rule (distance against `movement_range`) and no
    crossing the enemy's fleet shuts."""
    here = str(marshal.location or "")
    d = _distance(world, here, place)
    if d is None or d > max(1, int(getattr(marshal, "movement_range", 1) or 1)):
        return False
    if place == here:
        return True
    try:
        from backend.commands.strategic import strike_crossing_verdict
        if strike_crossing_verdict(world, marshal, place) is not None:
            return False
    except Exception as exc:
        report(exc, "own_order._in_strike_reach")
        return False
    if d >= 2:
        # the charge's own rule: a corps in the province between bars it
        # ("Cannot charge through X — Y blocks the path")
        between = [p for p in _near(world, here) if place in _near(world, p)]
        # (France's sight only: a corps France cannot see may still bar it —
        # the night then says so, the fog's honest surprise)
        if not any(not _foes_at(world, marshal, p) for p in between):
            return False
    return True


def _sheltered(world, marshal, enemy) -> bool:
    try:
        from backend.commands.order_quotes import _peace_soil_refusal_line
        return bool(_peace_soil_refusal_line(world, marshal, enemy))
    except Exception as exc:
        report(exc, "own_order._sheltered")
        return False


def _road(world, marshal, destination: str, avoid_foes: bool = False) -> List[str]:
    """His road to `destination` (without where he stands) — the game's one
    road-plotter; a careful man goes round the enemy France sees, and so does
    any man marching to a friend or back to his ground (`avoid_foes`)."""
    if not destination or destination == marshal.location:
        return []
    try:
        from backend.commands.strategic import enemy_occupied_regions, plot_route
        avoid = None
        if _nature(marshal) == "careful" or avoid_foes:
            avoid = [r for r in enemy_occupied_regions(world, marshal.nation, marshal=marshal,
                                                       fog_aware=True) if r != destination]
        road, _verdict = plot_route(world, marshal, destination, use_weighted=True,
                                    avoid_regions=avoid)
        return list(road or [])
    except Exception as exc:
        report(exc, "own_order._road")
        return []


def _first_leg(world, marshal, road: List[str]) -> List[str]:
    """The provinces tonight's march walks (the quote's own first-march rule:
    as far as he ranges, short of a corps we see, short of a frontier he may not
    cross)."""
    if not road:
        return []
    try:
        from backend.commands.order_quotes import _first_march
        return list(_first_march(world, marshal, {"road": list(road)}))
    except Exception as exc:
        report(exc, "own_order._first_leg")
        return []


def _garrison_known(world, place: str) -> Tuple[str, int]:
    try:
        from backend.game_logic.garrison_report import garrison_view
        form, value = garrison_view(world, place, _player(world))
        return str(form or ""), int(value) if form == "exact" else 0
    except Exception as exc:
        report(exc, "own_order._garrison_known")
        return "", 0


def _ground(world, marshal, place: str) -> Dict[str, Any]:
    from backend.commands import ground
    try:
        if place == marshal.location:
            return ground.standing(world, marshal)
        return ground.entering(world, marshal, place)
    except Exception as exc:
        report(exc, "own_order._ground")
        return {"code": ""}


def _day_may(world, marshal, enemy, odds: Optional[Dict[str, Any]]) -> bool:
    """"May become a great battle" — the attack card's own forecast."""
    try:
        from backend.game_logic import battle_day as _day
        if odds is None or _day.day_against(world, enemy.name) is not None:
            return False
        total = int(odds.get("weight", 0) or 0) + int(odds.get("theirs_low", 0) or 0)
        return _day.forecast(world, marshal, total, foe=enemy) is not None
    except Exception as exc:
        report(exc, "own_order._day_may")
        return False


def _unfit(world, marshal) -> str:
    try:
        from backend.game_logic import trial as _trial
        return _trial._unfit(world, marshal)
    except Exception as exc:
        report(exc, "own_order._unfit")
        return ""


def _court_name(nation: str) -> str:
    try:
        from backend.display_names import display_nation
        return str(display_nation(nation))
    except Exception as exc:
        report(exc, "own_order._court_name")
        return str(nation)


def _hates(marshal, other_name: str) -> bool:
    try:
        return int(marshal.get_relationship(other_name)) <= -2
    except Exception as exc:
        report(exc, "own_order._hates")
        return False


# ═══════════════════════════ the reading (PURE) ═════════════════════════════

def _reading(marshal, act: str, line: str, *, place: str = "", target: str = "",
             with_: str = "", why: str = "", do: Optional[List[Dict[str, Any]]] = None,
             odds: Optional[Dict[str, Any]] = None, need: Optional[Dict[str, Any]] = None,
             may_day: bool = False, step_out: bool = False, again: bool = False,
             counted: Optional[List[str]] = None) -> Dict[str, Any]:
    return {
        "marshal": marshal.name, "shown": _shown(marshal.name), "act": act,
        "place": place, "target": target, "with": with_, "why": why,
        "waiting": act in WAITING_ACTS, "visible": act in VISIBLE_ACTS and not again,
        "line": line, "do": list(do or []),
        "odds": (odds or {}).get("tenths", "") if odds else "",
        "needed": int((need or {}).get("needed", 0) or 0),
        "needed_words": needed_words(need) if need else "",
        "may_day": bool(may_day), "step_out": bool(step_out), "again": bool(again),
        "counts_on": list(counted or []),
    }


def key_of(reading: Optional[Dict[str, Any]]) -> Tuple[str, str, str]:
    """What makes two readings the same act (R-TRUE)."""
    if not reading:
        return ("", "", "")
    return (str(reading.get("act") or ""), str(reading.get("place") or ""),
            str(reading.get("target") or ""))


def _attack_choice(world, marshal, place: str, need: Dict[str, Any], taken: Dict[str, str],
                   *, verb: str = "attacks") -> Tuple[Optional[Dict[str, Any]], str]:
    """His attack on the enemy France sees at `place`, if his odds are met —
    `(reading, "")`; else `(None, why)`. A target a higher man has taken is
    left to him (`taken`)."""
    foes = _foes_at(world, marshal, place)
    if not foes:
        return None, ""
    foe = foes[0]
    if not _in_strike_reach(world, marshal, place):
        return None, f"{_shown(foe.name)} at {_shown(place)} is out of his reach"
    if _sheltered(world, marshal, foe):
        return None, f"{_shown(foe.name)} shelters on neutral ground"
    if foe.name in taken:
        return None, f"taken:{taken[foe.name]}"
    odds = odds_against(world, marshal, foe)
    if odds is None:
        return None, f"France cannot see how strong {_shown(foe.name)} is"
    met = float(odds["ratio"]) * 10.0 + 1e-9 >= float(need["needed"])
    if not met:
        return None, (f"{_shown(foe.name)} at {_shown(place)} is too strong for him: our "
                      f"{odds['tenths']} to their 10, and he goes in at {need['needed']}")
    others = [n for n in odds.get("joining") or [] if n != marshal.name]
    with_ = _names(others)
    day = _day_may(world, marshal, foe, odds)
    line = attack_line(marshal, verb, foe, place, odds, need, with_, day)
    do = []
    if getattr(marshal, "fortified", False):
        do.append({"action": "unfortify"})
    do.append({"action": "attack", "target": foe.name})
    return _reading(marshal, "attack", line, place=place, target=foe.name, with_=with_,
                    do=do, odds=odds, need=need, may_day=day, counted=others), ""


def _names(names: List[str]) -> str:
    shown = [_shown(n) for n in names[:3]]
    if not shown:
        return ""
    return shown[0] if len(shown) == 1 else ", ".join(shown[:-1]) + " and " + shown[-1]


def attack_line(marshal, verb: str, foe, place: str, odds: Dict[str, Any], need: Dict[str, Any],
                with_: str, day: bool, tail: str = "") -> str:
    """"Ney attacks Mack at Swabia, with Davout beside him (he may join) — the
    odds are our 12 to their 10, and he goes in when they are our 5 to their 10
    or better. May become a great battle." Both figures are said the same way
    round (row IC, Session 3b — read blind twice: "5 to 10 or better" was taken
    for the ENEMY at half his strength; `needed_words` already said "our 5 to
    their 10")."""
    head = f"{_shown(marshal.name)} {verb} {_shown(foe.name)} at {_shown(place)}"
    if with_:
        may = "they may join" if " and " in with_ else "he may join"
        head += f", with {with_} beside him ({may})"
    line = (f"{head} — the odds are our {odds['tenths']} to their 10, and he goes in when they are "
            f"our {need['needed']} to their 10 or better{tail}")
    if day:
        line += ". May become a great battle"
    return line


def _take_place(world, marshal, place: str, need: Dict[str, Any], taken: Dict[str, str],
                act_verb: str = "take") -> Tuple[Optional[Dict[str, Any]], str]:
    """What he does about an enemy-held `place` within his strike reach: attack
    the corps on it, storm its garrison (a bold man, at his odds), lay siege to
    its walls, or march in and take it. `(reading, "")` or `(None, why)`."""
    shown = _shown(marshal.name)
    if place in taken:
        return None, f"taken:{taken[place]}"
    if ("~" + place) in taken:
        return None, f"{_shown(taken['~' + place])} marches into {_shown(place)} tonight"
    reading, why = _attack_choice(world, marshal, place, need, taken)
    if reading is not None or why:
        return reading, why
    seen = _ground(world, marshal, place)
    code = str(seen.get("code") or "")
    here = place == marshal.location
    do_prefix = [{"action": "unfortify"}] if getattr(marshal, "fortified", False) else []
    if code == "garrison":
        if _nature(marshal) != "bold":
            return None, f"a garrison holds {_shown(place)} — a careful man will not storm it"
        _form, garrison = _garrison_known(world, place)
        if garrison <= 0:
            return None, f"France cannot see how strong the garrison of {_shown(place)} is"
        ratio = float(getattr(marshal, "strength", 0) or 0) / float(garrison)
        if ratio * 10.0 + 1e-9 < float(need["needed"]):
            return None, (f"the garrison of {_shown(place)} ({garrison:,}) is too strong: our "
                          f"{_tenths(ratio)} to their 10, and he goes in at {need['needed']}")
        if getattr(marshal, "name", "") == "Murat":
            return None, "Murat never storms walls"
        return _reading(marshal, "storm",
                        f"{shown} storms {_shown(place)} — a garrison of {garrison:,}, our "
                        f"{_tenths(ratio)} to their 10",
                        place=place, target=place, do=do_prefix + [{"action": "attack", "target": place}],
                        need=need), ""
    if code == "garrison_unsure":
        return None, f"a garrison stands in {_shown(place)} and France cannot see how strong"
    if code == "fort":
        if getattr(marshal, "name", "") == "Murat":
            return None, "Murat never storms walls"
        return _reading(marshal, "besiege", f"{shown} lays siege to {_shown(place)}",
                        place=place, target=place, do=do_prefix + [{"action": "attack", "target": place}],
                        need=need), ""
    if code == "besieging":
        return _reading(marshal, "besiege", f"{shown} keeps up the siege of {_shown(place)}",
                        place=place, target=place, do=[], need=need), ""
    if here and code == "open":
        return _reading(marshal, "take", f"{shown} takes {_shown(place)}, where he stands",
                        place=place, target=place, do=[{"action": "attack", "target": place}],
                        need=need), ""
    if not here and code in ("takes", "takes_if_open", "liberates"):
        frees = str(seen.get("line") or "")
        word = "frees" if code == "liberates" else "marches into"
        tail = f" — {frees}" if code == "liberates" and frees else (
            " and takes it" if code == "takes" else " to take it if nothing unseen holds it")
        return _reading(marshal, "take", f"{shown} {word} {_shown(place)}{tail}",
                        place=place, target=place, do=do_prefix + [{"action": "move", "target": place}],
                        need=need), ""
    if code in ("ours", "nobody", "not_at_war", "peace_passage"):
        return None, "ours"
    return None, str(seen.get("line") or "it cannot be taken")


def _march_toward(world, marshal, destination: str, need: Dict[str, Any], taken: Dict[str, str],
                  *, purpose: str, stop_short: int = 0,
                  avoid_foes: bool = False) -> Tuple[Optional[Dict[str, Any]], str]:
    """Tonight's march toward `destination` (up to his range, short of a corps
    France sees, short of a frontier he may not cross). `stop_short`: stop this
    many provinces before it (a support stays one march off)."""
    road = _road(world, marshal, destination, avoid_foes=avoid_foes)
    if stop_short:
        road = road[:max(0, len(road) - stop_short)]
    if not road:
        return None, f"there is no road to {_shown(destination)} he may take"
    leg = _first_leg(world, marshal, road)
    if not leg:
        blocker = _foes_at(world, marshal, road[0])
        if blocker:
            return None, f"barred:{blocker[0].name}:{road[0]}"
        return None, f"barred::{road[0]}"
    end = leg[-1]
    left = max(0, len(road) - len(leg))
    nights = "" if left == 0 else f" — {left} more march{'es' if left != 1 else ''} after tonight"
    shown = _shown(marshal.name)
    line = f"{shown} marches from {_shown(marshal.location)} to {_shown(end)}, {purpose}{nights}"
    do = [{"action": "unfortify"}] if getattr(marshal, "fortified", False) else []
    do += [{"action": "move", "target": step} for step in leg]
    return _reading(marshal, "march", line, place=end, target=destination, do=do, need=need), ""


def _looks(world, marshal, rec: Dict[str, Any],
           taken: Optional[Dict[str, str]] = None) -> List[Tuple[str, Dict[str, Any]]]:
    """The provinces next to him that France does not see whole — the ones
    nearer a seen enemy first — each a 'look' (the scout order). Not one a
    higher man walks or looks into tonight."""
    here = str(marshal.location or "")
    taken = taken or {}
    out = []
    for place in _near(world, here):
        if _full(world, place) or ("@" + place) in taken:
            continue
        if _foes_at(world, marshal, place) and _visible(world, place):
            rank = 0          # a corps seen only in part: look to learn his strength
        else:
            rank = 1
        out.append((rank, place))
    out.sort()
    shown = _shown(marshal.name)
    rows = []
    for _rank, place in out:
        rows.append((place, _reading(marshal, "look", f"{shown} sends his scouts into {_shown(place)}",
                                     place=place, target=place,
                                     do=[{"action": "scout", "target": place}])))
    return rows


def _nearest_foe(world, marshal) -> Tuple[Optional[Any], str]:
    from backend.commands import if_thens as _it
    best = None
    for enemy, where in _it.seen_enemies(world, marshal):
        d = _distance(world, marshal.location, where) or 0
        row = (d, -_known(world, enemy), enemy.name, enemy, where)
        if best is None or row[:3] < best[:3]:
            best = row
    return (best[3], best[4]) if best else (None, "")


def _waiting(world, marshal, spec: Dict[str, Any], need: Dict[str, Any], rec: Dict[str, Any],
             taken: Dict[str, str], friend_line: str) -> Dict[str, Any]:
    """His own way of waiting, by nature (§6.7.3), never the same act at the
    same place a third night running while another sensible one exists (§6.7.4)."""
    shown = _shown(marshal.name)
    nature = _nature(marshal)
    horse = bool(getattr(marshal, "cavalry", False))
    here = str(marshal.location or "")
    area = [p for p in (spec.get("area") or []) if p]
    options: List[Dict[str, Any]] = []
    foe, foe_at = _nearest_foe(world, marshal)
    # probe — the province of his area nearer the seen enemy
    if area and len(area) > 1 and here in area and foe is not None:
        other = [p for p in area if p != here][0]
        d_here = _distance(world, here, foe_at)
        d_other = _distance(world, other, foe_at)
        if (d_here is not None and d_other is not None and d_other < d_here
                and not _foes_at(world, marshal, other) and other not in taken):
            leg = _first_leg(world, marshal, [other])
            if leg:
                do = ([{"action": "unfortify"}] if getattr(marshal, "fortified", False) else [])
                options.append(_reading(marshal, "probe",
                                        f"{shown} pushes forward to {_shown(other)}, nearer "
                                        f"{_shown(foe.name)}", place=other, target=other,
                                        do=do + [{"action": "move", "target": other}]))
    digs = []
    if not horse and nature == "careful":
        if not getattr(marshal, "fortified", False):
            resolve = (" — his Iron Resolve starts to build (each night dug in makes his next attack "
                       "stronger)" if _has_resolve(marshal) else "")
            digs.append(_reading(marshal, "dig_in", f"{shown} digs in at {_shown(here)}{resolve}",
                                 place=here, target=here, do=[{"action": "fortify"}]))
    looks = [row for _place, row in _looks(world, marshal, rec, taken)]
    if nature == "careful" and not horse:
        # a careful man near an enemy he cannot beat falls back to better ground in his area
        if area and len(area) > 1 and here in area and foe is not None:
            other = [p for p in area if p != here][0]
            d_here = _distance(world, here, foe_at)
            d_other = _distance(world, other, foe_at)
            if (d_here is not None and d_other is not None and d_other > d_here
                    and getattr(marshal, "name", "") != "Davout"
                    and not _foes_at(world, marshal, other)):
                odds = odds_against(world, marshal, foe)
                if odds is not None and float(odds["ratio"]) < 1.0:
                    options.append(_reading(marshal, "fall_back",
                                            f"{shown} falls back to {_shown(other)}, better ground "
                                            f"against {_shown(foe.name)}", place=other, target=other,
                                            do=[{"action": "move", "target": other}]))
        options += digs + looks
    elif nature == "bold" or horse:
        options += looks + digs
    else:
        options += digs + looks
    acts = [tuple(a[:2]) for a in (rec.get("acts") or []) if isinstance(a, (list, tuple)) and len(a) >= 2]
    last_two = acts[-2:]

    def _third(row) -> bool:
        return len(last_two) == 2 and all(tuple(a) == (row["act"], row["place"]) for a in last_two)

    fresh = [row for row in options if not _third(row)]
    if fresh:
        pick = fresh[0]
    elif options:
        pick = dict(options[0])
        pick["line"] = pick["line"] + " again — nothing has changed"
        pick["again"] = True
        pick["visible"] = False
    else:
        if getattr(marshal, "fortified", False):
            words = f"{shown} keeps to his works at {_shown(here)}"
            if _has_resolve(marshal):
                stacks = int(getattr(marshal, "iron_resolve_stacks", 0) or 0)
                words += f" — Iron Resolve {stacks} of 3"
        else:
            words = f"{shown} stays put at {_shown(here)}"
        pick = _reading(marshal, "stay", words + " — nothing to do that he would choose",
                        place=here, why="nothing to do")
    pick["help"] = friend_line
    return pick


def _has_resolve(marshal) -> bool:
    try:
        return bool(marshal.has_iron_resolve())
    except Exception as exc:
        report(exc, "own_order._has_resolve")
        return False


def _friend_line(world, marshal) -> str:
    """"if Ney is attacked next to him, he may march to help (the usual roll)" —
    R-FRIENDS said, naming the friend nearest who would most want him (a friend
    by bond first, then the weakest)."""
    here = world.get_region(marshal.location)
    near = set(getattr(here, "adjacent_regions", ()) or ()) - {marshal.location}
    rows = []
    for other in world.get_player_marshals():
        if other.name == marshal.name or int(getattr(other, "strength", 0) or 0) <= 0:
            continue
        if getattr(other, "captured_by", "") or other.location not in near:
            continue
        if _hates(marshal, other.name):
            continue
        try:
            bond = int(marshal.get_relationship(other.name))
        except Exception as exc:
            report(exc, "own_order._friend_line: get_relationship")
            bond = 0
        rows.append((0 if bond >= 1 else 1, int(other.strength), other.name))
    if not rows:
        return ""
    friend = sorted(rows)[0][2]
    return f"if {_shown(friend)} is attacked next to him, he may march to help (a roll: not certain)"


def _task_reading(world, marshal, spec: Dict[str, Any], need: Dict[str, Any], rec: Dict[str, Any],
                  taken: Dict[str, str]) -> Tuple[Optional[Dict[str, Any]], str]:
    """The task's own act tonight, or `(None, why-he-waits)`."""
    task = spec.get("task")
    target = str(spec.get("target") or "")
    here = str(marshal.location or "")
    shown = _shown(marshal.name)
    nature = _nature(marshal)
    if task == "take":
        if target == here:
            reading, why = _take_place(world, marshal, target, need, taken)
            if reading is not None:
                return reading, ""
            if why == "ours":
                return None, f"{_shown(target)} is ours — he holds it"
            return None, why
        if _in_strike_reach(world, marshal, target):
            reading, why = _take_place(world, marshal, target, need, taken)
            if reading is not None:
                return reading, ""
            if why == "ours":
                return _march_toward(world, marshal, target, need, taken,
                                     purpose=f"to hold {_shown(target)}")
            return None, why
        reading, why = _march_toward(world, marshal, target, need, taken,
                                     purpose=f"on the road to {_shown(target)}")
        if reading is not None:
            return reading, ""
        if why.startswith("barred:"):
            _b, foe, where = (why.split(":") + ["", ""])[:3]
            if foe:
                hit, why2 = _attack_choice(world, marshal, where, need, taken)
                if hit is not None:
                    # (row IC, Session 3b — read blind: "he bars the road" after a
                    # sentence about our own man; the line names who bars it)
                    hit["line"] += f" — {_shown(foe)} bars the road to {_shown(target)}"
                    return hit, ""
                return None, f"road_barred:{why2 or _shown(foe) + ' bars the road'}"
            return None, f"road_barred:the road to {_shown(target)} is closed to him"
        return None, why
    if task == "pursue":
        quarry = world.get_marshal(target) if target else None
        if quarry is None or int(getattr(quarry, "strength", 0) or 0) <= 0:
            return None, f"France has lost sight of {_shown(target)}"
        where = quarry.location if quarry in _foes_at(world, marshal, quarry.location) else ""
        if where:
            if _in_strike_reach(world, marshal, where):
                if quarry.name in taken:
                    return None, f"taken:{taken[quarry.name]}"
                odds = odds_against(world, marshal, quarry)
                if odds is None:
                    return None, f"France cannot see how strong {_shown(quarry.name)} is"
                if float(odds["ratio"]) * 10.0 + 1e-9 >= float(need["needed"]):
                    day = _day_may(world, marshal, quarry, odds)
                    others = [n for n in odds.get("joining") or [] if n != marshal.name]
                    with_ = _names(others)
                    line = attack_line(marshal, "falls on", quarry, where, odds, need, with_, day)
                    do = ([{"action": "unfortify"}] if getattr(marshal, "fortified", False) else [])
                    return _reading(marshal, "attack", line, place=where, target=quarry.name,
                                    with_=with_, do=do + [{"action": "attack", "target": quarry.name}],
                                    odds=odds, need=need, may_day=day, counted=others), ""
                return None, (f"{_shown(quarry.name)} is too strong for him tonight: our "
                              f"{odds['tenths']} to their 10, and he goes in at {need['needed']}")
            reading, why = _march_toward(world, marshal, where, need, taken,
                                         purpose=f"after {_shown(quarry.name)}", stop_short=1)
            if reading is None and why.startswith("barred:"):
                return None, f"road_barred:the road to {_shown(quarry.name)} is barred"
            return reading, why
        last = str(spec.get("last_seen") or "")
        if last and last != here:
            reading, why = _march_toward(world, marshal, last, need, taken,
                                         purpose=f"to where {_shown(quarry.name)} was last seen")
            if reading is None and why.startswith("barred:"):
                return None, f"road_barred:the road to {_shown(last)} is barred"
            return reading, why
        return None, f"France has lost sight of {_shown(quarry.name)}"
    if task == "support":
        friend = world.get_marshal(target) if target else None
        if friend is None or int(getattr(friend, "strength", 0) or 0) <= 0 \
                or getattr(friend, "captured_by", ""):
            return None, f"{_shown(target)} has fallen"
        d = _distance(world, here, friend.location)
        if d is not None and d > 1:
            reading, why = _march_toward(world, marshal, friend.location, need, taken,
                                         purpose=f"to stay by {_shown(friend.name)}", stop_short=1,
                                         avoid_foes=True)
            if reading is None and why.startswith("barred:"):
                return None, f"road_barred:the road to {_shown(friend.name)} is barred"
            return reading, why
        if nature == "bold":
            # (R-ACTS, §6.7's bold "strike an enemy beside" made his support's
            # own act): he strikes the enemy that threatens his friend — next
            # to them both, at his odds — and stays by him after
            left_to = ""
            for place in [friend.location] + _near(world, friend.location):
                if place == here or not _in_strike_reach(world, marshal, place):
                    continue
                hit, why = _attack_choice(world, marshal, place, need, taken, verb="strikes")
                if hit is not None:
                    hit["act"] = "strike"
                    foe = world.get_marshal(hit["target"])
                    odds = odds_against(world, marshal, foe) if foe is not None else None
                    if foe is not None and odds is not None:
                        hit["line"] = attack_line(marshal, "strikes", foe, place, odds, need,
                                                  hit.get("with") or "", hit.get("may_day"),
                                                  f"; he threatens {_shown(friend.name)}, whom he stands by")
                    return hit, ""
                if why.startswith("taken:") and not left_to:
                    left_to = why
            return None, left_to
        return None, ""
    if task == "hold":
        area = [p for p in (spec.get("area") or [target]) if p]
        if here not in area:
            dest = area[0]
            reading, why = _march_toward(world, marshal, dest, need, taken,
                                         purpose=f"to hold {_shown(dest)}", avoid_foes=True)
            if reading is not None:
                return reading, ""
            if why.startswith("barred:"):
                return None, f"road_barred:the road to {_shown(dest)} is barred"
            return None, why
        # his area first: an enemy on it, or a province of it the enemy holds
        left_to = ""
        for place in [here] + [p for p in area if p != here]:
            if not _in_strike_reach(world, marshal, place):
                continue
            reading, why = _take_place(world, marshal, place, need, taken)
            if reading is not None:
                reading["line"] += " — it is his to hold"
                return reading, ""
            if why.startswith("taken:") and not left_to:
                left_to = why
        # a step outside his area — once per order (§6.7.1)
        if not spec.get("stepped_out"):
            strikes = []
            for place in area:
                for beside in _near(world, place):
                    if beside in area or not _in_strike_reach(world, marshal, beside):
                        continue
                    if not _foes_at(world, marshal, beside):
                        continue
                    strikes.append(beside)
            resolve_full = _has_resolve(marshal) and int(
                getattr(marshal, "iron_resolve_stacks", 0) or 0) >= 3
            beat_off = nature == "careful" and rec.get("last") == "won" and bool(rec.get("held"))
            if nature == "bold" or resolve_full or beat_off:
                for beside in sorted(set(strikes)):
                    hit, _why = _attack_choice(world, marshal, beside, need, taken, verb="strikes")
                    if hit is not None:
                        hit["act"] = "strike"
                        hit["step_out"] = True
                        tail = ("; Iron Resolve is full, so he strikes out and comes back after"
                                if resolve_full and nature == "careful"
                                else "; he beat them off last night and counter-attacks, then comes back"
                                if beat_off and nature == "careful"
                                else f"; {_shown(beside)} is next to the ground he holds, so he strikes "
                                     f"there once and comes back after")
                        foe = world.get_marshal(hit["target"])
                        odds = odds_against(world, marshal, foe) if foe is not None else None
                        if foe is not None and odds is not None:
                            hit["line"] = attack_line(marshal, "strikes", foe, beside, odds, need,
                                                      hit.get("with") or "", hit.get("may_day"), tail)
                        return hit, ""
                    if _why.startswith("taken:") and not left_to:
                        left_to = _why
        return None, left_to
    return None, ""


def _lannes_to_the_guns(world, marshal, taken: Dict[str, str]) -> Optional[Dict[str, Any]]:
    """Lannes's own line (§6.7.7; his +15 "to the guns", made a choice): a
    friend facing an enemy within two marches of him outranks waiting — he
    moves up beside that friend (never a man he hates)."""
    if str(getattr(marshal, "name", "")) != "Lannes":
        return None
    best = None
    for other in world.get_player_marshals():
        if other.name == marshal.name or int(getattr(other, "strength", 0) or 0) <= 0:
            continue
        if getattr(other, "captured_by", "") or _hates(marshal, other.name):
            continue
        d = _distance(world, marshal.location, other.location)
        if d is None or d < 1 or d > 2:
            continue
        foes = [e for place in [other.location] + _near(world, other.location)
                for e in _foes_at(world, marshal, place)]
        if not foes:
            continue
        row = (d, other.name)
        if best is None or row < best[0]:
            best = (row, other, foes[0])
    if best is None:
        return None
    _row_, friend, foe = best
    if best[0][0] == 1:
        return None      # already beside him: the arrival roll brings him
    for step in _near(world, marshal.location):
        if _distance(world, step, friend.location) == 1 and not _foes_at(world, marshal, step):
            leg = _first_leg(world, marshal, [step])
            if leg:
                do = [{"action": "unfortify"}] if getattr(marshal, "fortified", False) else []
                return _reading(marshal, "move_up",
                                f"{_shown(marshal.name)} moves up to {_shown(step)}, beside "
                                f"{_shown(friend.name)}, who faces {_shown(foe.name)} — to the guns",
                                place=step, target=friend.name, with_=_shown(friend.name),
                                do=do + [{"action": "move", "target": step}])
    return None


def read(world, marshal, spec: Optional[Dict[str, Any]] = None,
         taken: Optional[Dict[str, str]] = None, *, preview: bool = False) -> Dict[str, Any]:
    """What he does tonight — PURE. `spec` is his task (default: his order's
    own); `taken` the targets higher men have taken (enemy or place → name);
    `preview`: a task not yet given (the read-back: "tomorrow night")."""
    spec = spec if spec is not None else (own(marshal) or {})
    taken = dict(taken or {})
    shown = _shown(marshal.name)
    turn = _turn(world)
    rec = _record_view(marshal)
    if not preview:
        if spec.get("state") == "asks":
            why = str((spec.get("asks") or {}).get("why") or "he waits for your word")
            return _reading(marshal, "asks", f"{shown} waits for your word — {why}", why=why,
                            place=str(marshal.location or ""))
        if _int(spec, "given") == turn:
            ahead = read(world, marshal, spec, taken, preview=True)
            first = str(ahead.get("line") or "")
            if first.startswith(shown + " "):
                first = "he " + first[len(shown) + 1:]
            words = (f"{shown} makes ready — a task starts the night after it is given"
                     if first else f"{shown} starts on his task tomorrow night")
            out = _reading(marshal, "start", words, place=str(marshal.location or ""),
                           why="given tonight")
            out["ahead"] = str(ahead.get("line") or "")
            return out
        if (str(getattr(marshal, "name", "")) == "Bernadotte" and spec.get("late")
                and _int(spec, "given", -9) + 1 == turn):
            return _reading(marshal, "start",
                            f"{shown} starts a night late, as is his way",
                            place=str(marshal.location or ""), why="his way")
        # ONE THING A TURN (§6.3, the review IC3-V): his night already done (a
        # close re-entered), today's order by your hand, or a friend's battle
        # he was drawn into today — his task resumes the next night
        if _int(spec, "acted") == turn:
            return _reading(marshal, "stay", f"{shown} has done his night's work",
                            place=str(marshal.location or ""), why="his night is done")
        if _int({"t": getattr(marshal, "last_ordered_turn", None)}, "t") == turn:
            return _reading(marshal, "stay",
                            f"{shown} carried out your order today — his task resumes tomorrow night",
                            place=str(marshal.location or ""), why="your order today")
        if bool(getattr(marshal, "reinforced_this_turn", False)):
            return _reading(marshal, "stay",
                            f"{shown} fought beside a friend today — his task resumes tomorrow night",
                            place=str(marshal.location or ""), why="drawn in today")
    unfit = _unfit(world, marshal)
    if unfit:
        return _reading(marshal, "recover", f"{shown} recovers — {unfit}", why=unfit,
                        place=str(marshal.location or ""))
    if int(getattr(marshal, "strength", 0) or 0) <= 0:
        return _reading(marshal, "stay", f"{shown} has no corps", why="no corps")
    from backend.commands import if_thens as _it
    reaching = any(True for _e, _w in _it.seen_enemies(world, marshal))
    need = needed(marshal, int(spec.get("risk", 0) or 0), rec, reaching=reaching)
    # Lannes's line: a friend fighting within two marches outranks any other
    # target — he goes to stand beside him (§6.7.7)
    reading, why = _task_reading(world, marshal, spec, need, rec, taken)
    if reading is None and why.startswith("taken:"):
        lead = why.split(":", 1)[1]
        reading = _join(world, marshal, lead, taken, need)
        why = ""
    if reading is not None:
        return reading
    if not why.startswith("road_barred:") and spec.get("task") != "support":
        guns = _lannes_to_the_guns(world, marshal, taken)
        if guns is not None:
            guns["needed"] = int(need["needed"])
            guns["needed_words"] = needed_words(need)
            return guns
    friend = _friend_line(world, marshal)
    pick = _waiting(world, marshal, spec, need, rec, taken, friend)
    reason = why.split(":", 1)[1] if why.startswith("road_barred:") else why
    if reason and reason not in ("ours",):
        pick["why"] = reason
        if not pick.get("line", "").endswith(reason):
            pick["line"] = f"{pick['line']} ({reason})"
    if why.startswith("road_barred:"):
        pick["barred"] = True
    elif reason and reason != "ours" and spec.get("task") in ("take", "pursue"):
        pick["stuck"] = True        # his target beyond his odds (or his road): he waits, then asks
    pick["needed"] = int(need["needed"])
    pick["needed_words"] = needed_words(need)
    return pick


def _join(world, marshal, lead: str, taken: Dict[str, str], need: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """A higher man has taken his target: he stands beside the lead (the
    arrival roll may bring him into that one battle) or moves up beside him."""
    leader = world.get_marshal(lead)
    target_place = ""
    for key, who in taken.items():
        if who == lead and world.get_region(key) is None:
            enemy = world.get_marshal(key)
            if enemy is not None:
                target_place = enemy.location
                break
        elif who == lead and world.get_region(key) is not None:
            target_place = key
    if leader is None or not target_place:
        return None
    shown = _shown(marshal.name)
    lead_shown = _shown(lead)
    d = _distance(world, marshal.location, target_place)
    if d == 1:
        return _reading(marshal, "join",
                        f"{shown} stands beside {lead_shown} to join his attack at "
                        f"{_shown(target_place)} — he may arrive (the usual roll)",
                        place=marshal.location, target=lead, with_=lead_shown, need=need)
    # one march up to a province next to the target
    for step in _near(world, marshal.location):
        if _distance(world, step, target_place) == 1 and not _foes_at(world, marshal, step):
            leg = _first_leg(world, marshal, [step])
            if leg:
                do = ([{"action": "unfortify"}] if getattr(marshal, "fortified", False) else [])
                return _reading(marshal, "move_up",
                                f"{shown} moves up to {_shown(step)}, beside {lead_shown}'s attack "
                                f"at {_shown(target_place)}",
                                place=step, target=lead, with_=lead_shown,
                                do=do + [{"action": "move", "target": step}], need=need)
    return None


def _taken_by(reading: Dict[str, Any], world) -> Dict[str, str]:
    """What a man's act takes off the board for the men below him."""
    out: Dict[str, str] = {}
    act = reading.get("act")
    if act == "take" and not any((s or {}).get("action") == "attack" for s in reading.get("do") or []):
        # he marches in (no battle): the place is his tonight, nobody's attack
        # to join — a lower man takes his next target (the review, IC3-V)
        if reading.get("place"):
            out["~" + str(reading["place"])] = reading["marshal"]
            out["@" + str(reading["place"])] = reading["marshal"]
        return out
    if act in ("attack", "strike", "storm", "besiege", "take"):
        if reading.get("target"):
            out[str(reading["target"])] = reading["marshal"]
        if reading.get("place"):
            out[str(reading["place"])] = reading["marshal"]
    elif act in ("march", "probe", "move_up", "look", "fall_back") and reading.get("place"):
        # a province a higher man walks into, or looks into, is not a lower
        # man's to look into tonight
        out["@" + str(reading["place"])] = reading["marshal"]
    return out


def _lead_place(world, lead: str, taken: Dict[str, str]) -> str:
    for key, who in taken.items():
        if who != lead or key.startswith("@"):
            continue
        enemy = world.get_marshal(key) if world.get_region(key) is None else None
        if enemy is not None:
            return str(enemy.location or "")
    for key, who in taken.items():
        if who == lead and not key.startswith("@") and world.get_region(key) is not None:
            return key
    return ""


def join_fits(world, marshal, lead: str, place: str) -> bool:
    """Joining the lead's attack at `place` is part of HIS task — inside or
    beside his area, on his take's ground, on his quarry, beside the friend he
    supports. A man whose task lies elsewhere goes about it (he may still be
    drawn in by the arrival roll, and the line says so)."""
    spec = own(marshal) or {}
    task = spec.get("task")
    target = str(spec.get("target") or "")
    if not place:
        return False
    if task == "hold":
        area = [p for p in (spec.get("area") or [target]) if p]
        return any(place == p or place in _near(world, p) for p in area)
    if task == "take":
        return place == target or (_distance(world, place, target) or 9) <= 1
    if task == "pursue":
        quarry = world.get_marshal(target)
        return quarry is not None and quarry.location == place
    if task == "support":
        friend = world.get_marshal(target)
        return lead == target or (friend is not None and
                                  (_distance(world, friend.location, place) or 9) <= 1)
    return False


def tonight(world) -> List[Dict[str, Any]]:
    """Every man on his own, highest rank first, each reading leaving out what a
    higher man has taken — and a man the lead's forecast counts on is read as
    joining him. PURE."""
    out: List[Dict[str, Any]] = []
    taken: Dict[str, str] = {}
    counted: Dict[str, str] = {}
    for man in men(world):
        try:
            reading = _read_in_turn(world, man, taken, counted)
        except Exception as exc:
            report(exc, f"own_order.tonight: {man.name}")
            reading = _reading(man, "stay", f"{_shown(man.name)} stays put", why="the board could not be read")
        out.append(reading)
        taken.update(_taken_by(reading, world))
        for other in reading.get("counts_on") or []:
            if other not in counted and other != man.name:
                counted[other] = man.name
    return out


def _read_in_turn(world, man, taken: Dict[str, str], counted: Dict[str, str]) -> Dict[str, Any]:
    """His reading in the night's order: a man the lead's forecast counts on
    joins him when that is part of his own task; otherwise he goes about his
    task, and the line says the arrival roll may draw him into the lead's
    battle first (R-TRUE: "he may")."""
    lead = counted.get(man.name, "")
    if lead:
        place = _lead_place(world, lead, taken)
        if join_fits(world, man, lead, place):
            joined = _join(world, man, lead, taken,
                           needed(man, int((own(man) or {}).get("risk", 0) or 0)))
            if joined is not None and joined.get("act") == "join":
                return joined
        reading = read(world, man, taken=taken)
        if reading.get("act") != "join":
            reading["drawn_by"] = lead
            reading["line"] = (f"{reading['line']} — unless the usual roll draws him into "
                               f"{_shown(lead)}'s battle first")
        return reading
    return read(world, man, taken=taken)


_SHOWN: Dict[str, Any] = {"key": None, "rows": None}


def _board_key(world) -> Tuple:
    """What the night's reading depends on, cheaply: the turn, the actions left,
    every corps' place, strength and works, the orders and the sight (the
    log's length moves with every scout, battle and order)."""
    corps = tuple(sorted((m.name, str(m.location or ""), int(getattr(m, "strength", 0) or 0),
                          bool(getattr(m, "fortified", False)),
                          bool(getattr(m, "reinforced_this_turn", False)),
                          repr(getattr(m, "last_ordered_turn", None)),
                          repr(getattr(getattr(m, "strategic_order", None), "own", None)),
                          # Row IC, Session 3b: a follower's night reads his
                          # FOLLOW order (whom, since when) and his army's roll
                          _order_key(getattr(m, "strategic_order", None)))
                         for m in (getattr(world, "marshals", None) or {}).values()))
    return (id(world), _turn(world), int(getattr(world, "actions_remaining", 0) or 0),
            len(getattr(world, "event_log", None) or []),
            len(getattr(world, "command_history", None) or []), hash(corps),
            repr(getattr(world, "armies", None) or None))


def _order_key(order) -> Tuple:
    if order is None:
        return ()
    return (str(getattr(order, "command_type", "") or ""), str(getattr(order, "target", "") or ""),
            bool(getattr(order, "standing_follow", False)), repr(getattr(order, "issued_turn", None)))


def tonight_shown(world) -> List[Dict[str, Any]]:
    """`tonight` for the screens (the desk, the cards, the End Turn list) —
    kept while the board is unchanged, so a reply that draws every card reads
    the night once. The pass itself always reads afresh."""
    try:
        key = _board_key(world)
    except Exception as exc:
        report(exc, "own_order.tonight_shown: the key")
        return tonight(world)
    if _SHOWN["key"] != key:
        _SHOWN["rows"] = tonight(world)
        _SHOWN["key"] = key
    return list(_SHOWN["rows"] or [])


def tonight_for(world, marshal) -> Optional[Dict[str, Any]]:
    for reading in tonight_shown(world):
        if reading.get("marshal") == marshal.name:
            return reading
    return None


# ═══════════════════════════ his proposal (§6.7.2) ══════════════════════════

def proposal(world, marshal) -> Dict[str, Any]:
    """The task HE would choose — PURE — as a typed line on his own, with the
    reason in one sentence. Ney takes; Murat chases the weakest army France
    sees; Lannes stands by the friend nearest a fight; Masséna holds his front;
    Davout holds and digs in; Bernadotte holds in the rear; anyone else by
    nature."""
    from backend.game_logic import trial as _trial
    shown = _shown(marshal.name)
    here = str(marshal.location or "")
    key = str(marshal.name)
    nature = _nature(marshal)
    task, target, why = "hold", here, ""
    try:
        if key == "Murat" or (bool(getattr(marshal, "cavalry", False)) and nature == "bold"):
            weakest = None
            for enemy in world.get_visible_enemies(marshal.nation) or []:
                if int(getattr(enemy, "strength", 0) or 0) <= 0:
                    continue
                d = _distance(world, here, enemy.location)
                if d is None or d > PURSUE_RING:
                    continue
                row = (_known(world, enemy) or int(enemy.strength), d, enemy.name)
                if weakest is None or row < weakest[0]:
                    weakest = (row, enemy)
            if weakest is not None:
                task, target = "pursue", weakest[1].name
                why = f"{_shown(target)} is the weakest army France sees within his reach"
        if task == "hold" and key == "Lannes":
            best = None
            for other in world.get_player_marshals():
                if other.name == key or int(getattr(other, "strength", 0) or 0) <= 0:
                    continue
                if _hates(marshal, other.name) or getattr(other, "personality", "") == "sovereign":
                    continue
                foes = [e for e in world.get_visible_enemies(marshal.nation) or []
                        if (_distance(world, other.location, e.location) or 99) <= 1]
                if not foes:
                    continue
                d = _distance(world, here, other.location)
                if d is None or d > PURSUE_RING:
                    continue
                if best is None or (d, other.name) < best[0]:
                    best = ((d, other.name), other)
            if best is not None:
                task, target = "support", best[1].name
                why = f"{_shown(target)} is the friend nearest a fight"
        if task == "hold" and nature == "bold" and key not in ("Massena", "Lannes"):
            take = _trial._place_to_take(world, marshal)
            if take is not None:
                task, target = "take", take["place"]
                why = f"{_shown(target)} is the nearest place the enemy holds that he can take"
    except Exception as exc:
        report(exc, "own_order.proposal")
        task, target, why = "hold", here, ""
    if not why:
        why = {
            "Massena": "he holds his front and strikes out from it",
            "Davout": "he holds and digs in, and strikes when Iron Resolve is full",
            "Bernadotte": "he holds in the rear — he is slow to a fight",
            "Lannes": "no friend of his is near a fight",
        }.get(key, "France sees nothing he can take" if nature == "bold" else
              "a careful man holds and digs in")
    verb = {"take": "take", "pursue": "chase", "hold": "hold", "support": "support"}[task]
    line = f"{shown}, {verb} {_shown(target)} on your own."
    from backend.game_logic import own_voice as _voice
    return {"marshal": marshal.name, "shown": shown, "nature": nature, "task": task,
            "target": target, "line": line, "why": why,
            "words": f"{shown} proposes to {verb} {_shown(target)} — {why}.",
            "says": _voice.line(marshal.name, nature, "proposal", _turn(world))}


# ═══════════════════════════ giving it (§6.3) ═══════════════════════════════

def spec_from(world, marshal, task: str, target: str, *, area: Optional[List[str]] = None,
              risk: int = 0) -> Tuple[Optional[Dict[str, Any]], str]:
    """A task spec, checked — `(spec, "")` or `(None, why)` in plain words."""
    shown = _shown(marshal.name)
    if task not in TASKS:
        return None, "a task is one of take, chase, hold or support"
    target = str(target or "")
    if task == "hold":
        area = [p for p in (area or [target or marshal.location]) if p][:2]
        for place in area:
            if world.get_region(place) is None:
                return None, f"there is no province called {place}"
        if len(area) == 2 and area[1] not in _near(world, area[0]):
            return None, (f"name one or two provinces next to each other — {_shown(area[0])} and "
                          f"{_shown(area[1])} are not")
        target = area[0]
    elif task == "take":
        if world.get_region(target) is None:
            return None, f"there is no province called {target}"
        area = [target]
    elif task == "pursue":
        quarry = world.get_marshal(target)
        seen = quarry is not None and quarry in (world.get_visible_enemies(marshal.nation) or [])
        if not seen or not world.is_at_war(marshal.nation, quarry.nation):
            # the same answer for an unseen enemy and a name that does not exist (§8.3)
            return None, f"France sees no enemy army called {_shown(target)}"
        area = []
    elif task == "support":
        friend = world.get_marshal(target)
        if friend is None or friend.nation != marshal.nation or friend.name == marshal.name:
            return None, f"{_shown(target)} is not one of your marshals he could support"
        if getattr(friend, "personality", "") == "sovereign":
            return None, "the corps beside the Emperor are yours to command by hand"
        if _hates(marshal, friend.name):
            return None, f"{shown} will not support {_shown(friend.name)} — he hates him"
        area = []
    spec = {"task": task, "target": target, "area": list(area or []),
            "risk": max(-1, min(1, int(risk or 0))), "state": "given", "given": _turn(world),
            "paid": 0, "ring": str(marshal.location or "") if task == "pursue" else "",
            "last_seen": (world.get_marshal(target).location if task == "pursue" else ""),
            "unseen": 0, "blocked": 0, "stepped_out": False, "asks": None, "acted": -1,
            "line": "", "late": str(marshal.name) == "Bernadotte"}
    return spec, ""


def task_words(spec: Dict[str, Any]) -> str:
    """"take Swabia" · "hold Milan and Piedmont" · "chase Mack" · "support Ney"."""
    task = spec.get("task")
    if task == "hold":
        area = [ _shown(p) for p in (spec.get("area") or [spec.get("target")]) if p]
        return "hold " + " and ".join(area)
    verb = {"take": "take", "pursue": "chase", "support": "support"}.get(task, str(task))
    return f"{verb} {_shown(spec.get('target'))}"


def objection(world, marshal, spec: Dict[str, Any]) -> str:
    """His plain concern, read ONCE at Give — no dice (§6.3): a careful man
    against odds he would not take or against walls; a bold man told to hold
    with an enemy beside him. Never on his own proposal (the caller checks)."""
    nature = _nature(marshal)
    task = spec.get("task")
    try:
        if nature == "careful" and task in ("take", "pursue"):
            reading = read(world, marshal, spec, preview=True)
            why = str(reading.get("why") or "")
            if "too strong" in why or "will not storm" in why:
                return why
        if nature == "bold" and task == "hold":
            foe, _where = _nearest_foe(world, marshal)
            if foe is not None:
                return f"he would rather go for {_shown(foe.name)} than sit and hold"
    except Exception as exc:
        report(exc, "own_order.objection")
    return ""


def objection_cost(marshal) -> int:
    try:
        from backend.commands.objection_v2 import get_insist_penalty, get_trust_tier
        return abs(int(get_insist_penalty(get_trust_tier(int(marshal.trust.value)))))
    except Exception as exc:
        report(exc, "own_order.objection_cost")
        return 10


def slighted(world, marshal) -> Optional[Any]:
    """The bold marshal who outranks him, stands within three marches and has no
    order of his own — he will take it ill (§6.9). None when nobody minds."""
    seats = _seats(world)
    mine = seats.get(marshal.name, len(seats))
    for other in sorted(world.get_player_marshals(), key=lambda m: (seats.get(m.name, 99), m.name)):
        if other.name == marshal.name or _nature(other) != "bold":
            continue
        if seats.get(other.name, len(seats)) >= mine:
            continue
        if getattr(other, "strategic_order", None) is not None or on_his_own(other):
            continue
        d = _distance(world, other.location, marshal.location)
        if d is not None and d <= 3 and int(getattr(other, "strength", 0) or 0) > 0:
            return other
    return None


def price_of(marshal, spec: Dict[str, Any]) -> int:
    return CHANGE_PRICE if on_his_own(marshal) else int(PRICE.get(spec.get("task"), 2))


def give(world, marshal, spec: Dict[str, Any], *, line: str, own_proposal: bool = False,
         if_thens: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Set him on his own with `spec` (or change his task). The caller has
    checked the price can be paid; this charges nothing (the executor's road
    charges `variable_action_cost`). Returns the reply."""
    from backend.models.marshal import StrategicOrder
    from backend.commands.strategic import clear_order_bound_interrupt
    from backend.game_logic import own_voice as _voice
    shown = _shown(marshal.name)
    changing = on_his_own(marshal)
    refusal = why_not(world, marshal, spec.get("task", ""), replacing=changing)
    if refusal:
        return {"success": False, "message": f"{shown} cannot be set on his own: {refusal}.",
                "no_action_cost": True}
    turn = _turn(world)
    price = CHANGE_PRICE if changing else int(PRICE.get(spec["task"], 2))
    old = own(marshal) or {}
    spec = dict(spec)
    spec["line"] = line
    spec["paid"] = int(old.get("paid", 0) or 0) + price if changing and _int(old, "given") == turn else price
    if changing:
        # a change keeps when he was given (the night it was given stays his
        # first), his step outside his area, the record, where he stands in his
        # task's life and the night he last acted (the review, IC3-V)
        spec["given"] = old.get("given", turn)
        spec["stepped_out"] = bool(old.get("stepped_out")) and spec["task"] == old.get("task")
        spec["late"] = bool(old.get("late")) and spec["given"] == turn
        spec["state"] = "given" if _int(spec, "given") == turn else "work"
        spec["acted"] = old.get("acted", -1)
        # Row IC, Session 3b: a change of task leaves him at the head of the
        # army he commands (its men still follow him). The war goal he served
        # is kept only where the new task says so (`reading_of_parse`).
        if old.get("army") and not spec.get("army"):
            spec["army"] = old["army"]
    else:
        # a new order counts his battles from now: a win or a loss under an
        # earlier order is not "last night" (the review, IC3-V)
        rec = record(marshal)
        rec["tick_won"] = int(getattr(marshal, "battles_won", 0) or 0)
        rec["tick_lost"] = int(getattr(marshal, "battles_lost", 0) or 0)
        rec["held"] = False
        marshal.own_record = rec
    lines = []
    try:
        from backend.commands import if_thens as _it
        asked = list(if_thens or [])
        if asked:
            kept, _refused = _it.settle(world, marshal, ORDER_TYPE[spec["task"]], asked)
            lines = [{**dict(row), "used": False, "written": turn} for row in kept[:2]]
    except Exception as exc:
        report(exc, "own_order.give: if-thens")
    target = spec["target"]
    target_type = "marshal" if spec["task"] in ("pursue", "support") else "region"
    order = StrategicOrder(command_type=ORDER_TYPE[spec["task"]], target=target,
                           target_type=target_type, started_turn=turn, issued_turn=turn,
                           original_command=line, if_thens=lines)
    order.own = spec
    marshal.strategic_order = order
    marshal.holding_position = False
    marshal.hold_region = ""
    clear_order_bound_interrupt(marshal)
    if hasattr(marshal, "jealousy_autonomous_warned"):
        marshal.jealousy_autonomous_warned = False      # a man on his own makes no strike
    nature = _nature(marshal)
    voice_kind = "bolder" if int(spec.get("risk", 0) or 0) > 0 else (
        "careful" if int(spec.get("risk", 0) or 0) < 0 else "ack")
    said = _voice.line(marshal.name, nature, voice_kind, turn)
    took_ill = ""
    if not changing:
        senior = slighted(world, marshal)
        if senior is not None:
            try:
                from backend.game_logic import precedence as _court
                _court.note(world, senior, marshal, "passed_over", str(marshal.location or ""),
                            da=-1, note_text="set on his own while I stood by with no order")
            except Exception as exc:
                report(exc, "own_order.give: the slight")
            took_ill = (f" {_shown(senior.name)} outranks him and stood by with no order — he resents "
                        f"it (his regard for {shown} drops).")
    objected = "" if own_proposal else objection(world, marshal, spec)
    cost_words = ""
    if objected:
        cost = objection_cost(marshal)
        try:
            marshal.modify_trust(-cost)
        except Exception as exc:
            report(exc, "own_order.give: objection trust")
        cost_words = f" He objected ({objected}); giving it anyway cost {cost} of his trust."
    verb = "changes his task" if changing else "is on his own"
    starts = ("He starts tomorrow night." if _int(spec, "given") == turn
              else "He turns to it tonight.")
    message = (f"{shown} {verb}: {task_words(spec)}. {starts} "
               f"\"{said}\" {count_words(world)}.{took_ill}{cost_words}")
    world.log_event({"type": EVENT, "phase": "given", "marshal": marshal.name,
                     "nation": marshal.nation, "task": spec["task"], "target": target,
                     "changing": bool(changing), "message": message, "told": True})
    return {"success": True, "message": message, "variable_action_cost": price,
            "own": payload(world, marshal), "marshal": marshal.name}


def stand_down(world, marshal) -> Dict[str, Any]:
    """Recall him — free. Given this turn: his actions come back in full (the
    [Withdraw] of §6.3). Recalled mid-task by your choice (he had not asked):
    3 of his trust."""
    spec = own(marshal)
    shown = _shown(marshal.name)
    if spec is None:
        return {"success": False, "message": f"{shown} is not on his own.", "no_action_cost": True}
    turn = _turn(world)
    refund = int(spec.get("paid", 0) or 0) if _int(spec, "given") == turn else 0
    trust_cost = 0
    if not refund and spec.get("state") != "asks" and _int(spec, "acted") >= 0:
        trust_cost = STAND_DOWN_TRUST
        try:
            marshal.modify_trust(-trust_cost)
        except Exception as exc:
            report(exc, "own_order.stand_down: trust")
    still = _followers_words(world, marshal)      # (Session 3b) read before his task is gone
    marshal.strategic_order = None
    from backend.commands.strategic import clear_order_bound_interrupt
    clear_order_bound_interrupt(marshal)
    if refund:
        world.actions_remaining = int(getattr(world, "actions_remaining", 0) or 0) + refund
    tail = (f" The {refund} action{'s' if refund != 1 else ''} it cost come back." if refund
            else (f" Recalled in the middle of his task, he loses {trust_cost} trust." if trust_cost
                  else "")) + still
    message = f"{shown} stands down and awaits your orders.{tail} {count_words(world)}."
    world.log_event({"type": EVENT, "phase": "stood_down", "marshal": marshal.name,
                     "nation": marshal.nation, "message": message, "told": True})
    return {"success": True, "message": message, "no_action_cost": True,
            "refunded": refund, "marshal": marshal.name}


def carry_on(world, marshal) -> Dict[str, Any]:
    """Answer his ask: carry on — free; the counters that made him ask start
    again (a pursuit's ring is drawn again where he stands)."""
    spec = own(marshal)
    shown = _shown(marshal.name)
    if spec is None:
        return {"success": False, "message": f"{shown} is not on his own.", "no_action_cost": True}
    if spec.get("state") != "asks":
        return {"success": True, "message": f"{shown} is already carrying on with his task.",
                "no_action_cost": True}
    spec["state"] = "work"
    spec["asks"] = None
    spec["blocked"] = 0
    spec["unseen"] = 0
    if spec.get("task") == "pursue":
        spec["ring"] = str(marshal.location or "")
    message = f"{shown} carries on with his task: {task_words(spec)}."
    world.log_event({"type": EVENT, "phase": "carry_on", "marshal": marshal.name,
                     "nation": marshal.nation, "message": message, "told": True})
    return {"success": True, "message": message, "no_action_cost": True, "marshal": marshal.name}


def change_risk(world, marshal, step: int) -> Dict[str, Any]:
    """"Ney, more risk" / "less risk" — 1 action (§6.3)."""
    spec = own(marshal)
    shown = _shown(marshal.name)
    if spec is None:
        return {"success": False, "no_action_cost": True,
                "message": f"{shown} is not on his own — set him on his own first."}
    new = max(-1, min(1, int(spec.get("risk", 0) or 0) + int(step)))
    if new == int(spec.get("risk", 0) or 0):
        return {"success": False, "no_action_cost": True,
                "message": f"{shown} already goes in at {needed_words(needed(marshal, new))} — one step is the most you can move him."}
    spec["risk"] = new
    if _int(spec, "given") == _turn(world):
        spec["paid"] = int(spec.get("paid", 0) or 0) + CHANGE_PRICE
    message = f"{shown} now goes in at {needed_words(needed(marshal, new))}."
    return {"success": True, "message": message, "variable_action_cost": CHANGE_PRICE,
            "marshal": marshal.name}


def ask_why(world, marshal, why: str) -> None:
    spec = own(marshal)
    if spec is None or spec.get("state") == "asks":
        return
    spec["state"] = "asks"
    spec["asks"] = {"why": why, "since": _turn(world)}
    message = f"{_shown(marshal.name)} asks for your word: {why}."
    world.log_event({"type": EVENT, "phase": "asks", "marshal": marshal.name,
                     "nation": marshal.nation, "message": message})


def _followers_words(world, marshal) -> str:
    """Row IC, Session 3b: said when an army's commander's task ends — the men
    who followed him keep following, by an ordinary order now."""
    if not (own(marshal) or {}).get("army"):
        return ""
    try:
        from backend.commands import army_task as _army
        return _army.ending_words(world, marshal)
    except Exception as exc:
        report(exc, "own_order._followers_words")
        return ""


def end(world, marshal, why: str, phase: str = "ended") -> Dict[str, Any]:
    message = f"{_shown(marshal.name)}'s task on his own is over: {why}.{_followers_words(world, marshal)}"
    if own(marshal) is not None:
        marshal.strategic_order = None
        from backend.commands.strategic import clear_order_bound_interrupt
        clear_order_bound_interrupt(marshal)     # NPC-2: its question ends with it
    world.log_event({"type": EVENT, "phase": phase, "marshal": marshal.name,
                     "nation": marshal.nation, "message": message})
    return {"marshal": marshal.name, "command": "", "order_status": "completed",
            "action": "own_ended", "message": message, "reason": message}


# ═══════════════════════════ the typed road (§8.2) ══════════════════════════

def task_of_parse(world, parsed: Dict[str, Any]) -> Tuple[str, str]:
    """`(task, target)` a parse names as a task — a standing hold / pursue /
    support / march, or an attack on a place (take) or on a seen army
    (chase) — else ("", "")."""
    command = parsed.get("command") or {}
    target = str(command.get("target") or "")
    stype = str(parsed.get("strategic_type") or "").upper()
    if parsed.get("is_strategic") and stype in TASK_OF_ORDER:
        task = TASK_OF_ORDER[stype]
        if task == "take" and not target:
            return "", ""
        return task, target
    if str(command.get("action") or "") == "attack" and target:
        if world.get_region(target) is not None:
            return "take", target
        if world.get_marshal(target) is not None:
            return "pursue", target
    if str(command.get("action") or "") in ("hold", "defend") and target and world.get_region(target):
        return "hold", target
    return "", ""


def reading_of_parse(world, parsed: Dict[str, Any]) -> Dict[str, Any]:
    """What a typed task to a man would be ON HIS OWN — the read-back's and the
    give's ONE reader: `{ok, marshal, task, target, area, risk, spec, why,
    price, changing, proposal, tonight, needed, says}`. PURE."""
    from backend.game_logic import own_voice as _voice
    own_part = parsed.get("own") or {}
    command = parsed.get("command") or {}
    name = str(command.get("marshal") or "")
    marshal = world.get_marshal(name) if name else None
    out: Dict[str, Any] = {"ok": False, "marshal": name, "why": "", "kind": own_part.get("kind", "give")}
    if marshal is None:
        out["why"] = "there is no such marshal"
        return out
    out["shown"] = _shown(marshal.name)
    kind = out["kind"]
    if kind != "give":
        out["ok"] = on_his_own(marshal)
        out["why"] = "" if out["ok"] else f"{_shown(marshal.name)} is not on his own"
        return out
    task, target = (str(own_part.get("task") or ""), str(own_part.get("target") or ""))
    if not task:
        task, target = task_of_parse(world, parsed)
    if not task:
        out["why"] = "a task on his own is to take a place, chase an army, hold ground or support a friend"
        return out
    area = [target] + ([own_part["second"]] if own_part.get("second") else [])
    risk = int(own_part.get("risk", 0) or 0)
    changing = on_his_own(marshal)
    refusal = why_not(world, marshal, task, replacing=changing)
    if refusal:
        out.update(task=task, target=target, why=refusal)
        return out
    spec, why = spec_from(world, marshal, task, target, area=area if task == "hold" else None, risk=risk)
    if spec is None:
        out.update(task=task, target=target, why=why)
        return out
    goal = str(own_part.get("goal") or "")
    if goal:
        # Row IC, Session 3b: "take the war goal" — the task SERVES the goal of
        # that war (it is turned when the goal changes: `army_task`); a goal he
        # has no road to is refused free, with why.
        spec["goal"] = goal
        if task == "take" and str(marshal.location or "") != spec["target"] \
                and not _road(world, marshal, spec["target"]):
            out.update(task=task, target=target,
                       why=(f"{_shown(marshal.name)} has no road to {_shown(spec['target'])}, your war goal "
                            "— give the task to a man who can reach it, or name another goal"))
            return out
    price = CHANGE_PRICE if changing else int(PRICE.get(task, 2))
    prop = proposal(world, marshal)
    own_prop = (prop["task"] == task and str(prop["target"]) == str(spec["target"]))
    reading = read(world, marshal, spec, preview=True)
    n = needed(marshal, risk)
    nature = _nature(marshal)
    said = ""
    if risk > 0:
        said = _voice.line(marshal.name, nature, "bolder", _turn(world))
    elif risk < 0:
        said = _voice.line(marshal.name, nature, "careful", _turn(world))
    objected = "" if own_prop else objection(world, marshal, spec)
    if objected:
        said = _voice.line(marshal.name, nature, "object", _turn(world))
    if not said:
        said = _voice.line(marshal.name, nature, "ack", _turn(world))
    senior = None if changing else slighted(world, marshal)
    out.update(ok=True, task=task, target=spec["target"], area=list(spec.get("area") or []),
               goal=goal,
               risk=risk, spec=spec, price=price, changing=changing, own_proposal=own_prop,
               proposal=prop, tonight=reading, needed=n, needed_words=needed_words(n),
               says=said, objection=objected,
               objection_cost=objection_cost(marshal) if objected else 0,
               slight=_shown(senior.name) if senior is not None else "",
               count=count_words(world), allowed=allowed(world),
               count_after=count(world) + (0 if changing else 1),
               starts_tonight=bool(changing and _int(own(marshal), "given") != _turn(world)))
    return out


def from_parse(world, parsed: Dict[str, Any], command: Dict[str, Any]) -> Dict[str, Any]:
    """The typed road's give, change, stand-down and carry-on — every refusal
    free, and nothing moves before the price is known to be paid."""
    own_part = parsed.get("own") or {}
    kind = str(own_part.get("kind") or "give")
    name = str(command.get("marshal") or "")
    marshal = world.get_marshal(name) if name else None
    if marshal is None:
        return {"success": False, "message": "There is no such marshal.", "no_action_cost": True}
    shown = _shown(marshal.name)
    if kind == "stand_down":
        return stand_down(world, marshal)
    if kind == "carry_on":
        return carry_on(world, marshal)
    if kind == "risk":
        if int(getattr(world, "actions_remaining", 0) or 0) < CHANGE_PRICE:
            return {"success": False, "no_action_cost": True,
                    "message": f"Changing {shown}'s task takes {CHANGE_PRICE} action; none is left this turn."}
        return change_risk(world, marshal, int(own_part.get("step", 0) or 0))
    reading = reading_of_parse(world, parsed)
    if not reading.get("ok"):
        return {"success": False, "no_action_cost": True,
                "message": f"{shown} cannot be set on his own: {reading.get('why') or 'no task he can take'}."}
    price = int(reading["price"])
    have = int(getattr(world, "actions_remaining", 0) or 0)
    if have < price:
        return {"success": False, "no_action_cost": True,
                "message": (f"Setting {shown} on his own takes {price} action{'s' if price != 1 else ''}; "
                            f"you have {have}. Nothing was spent.")}
    line = str(command.get("raw_command") or parsed.get("raw_input") or "").strip()
    return give(world, marshal, reading["spec"], line=line,
                own_proposal=bool(reading.get("own_proposal")),
                if_thens=list(parsed.get("if_thens") or own_part.get("if_thens") or []))


# ═══════════════════════════ the seams (the exemptions, R-FRIENDS) ══════════

def acted_tonight(marshal, world) -> bool:
    """His one thing is done tonight (his if-thens sleep)."""
    spec = own(marshal)
    return spec is not None and _int(spec, "acted") == _turn(world)


def answers_the_guns(marshal) -> bool:
    """R-FRIENDS: a man on his own goes to a friend's battle next to him even dug
    in or on his hold's post (the two rules that keep a man at his post do not
    hold him); the rule against a man he hates still holds (`combat_executor`)."""
    return on_his_own(marshal) and int(getattr(marshal, "strength", 0) or 0) > 0


# ═══════════════════════════ the pass (D6, D7, D8) ══════════════════════════

def the_pass(world, executor, game_state) -> List[Dict[str, Any]]:
    """FIRST of all when the turn ends: every man on his own does what
    "Tonight" said — or stays put and says why. Returns the report rows (also
    kept on the world for the turn's report, `close_of_turn`)."""
    rows: List[Dict[str, Any]] = []
    world._own_night_rows = rows
    if not men(world):
        return rows
    _the_count_holds(world, rows)
    plan = {r["marshal"]: r for r in tonight(world)}
    # Row IC, Session 3b: the men who FOLLOW a commander as his army's task
    # move in this pass too — right after him, before the enemy — on what
    # "Tonight" said of them (`army_task`: the army moves as one).
    plan_followers: Dict[str, Dict[str, Any]] = {}
    try:
        from backend.commands import army_task as _army
        plan_followers = {r["marshal"]: r for r in _army.tonight(world, list(plan.values()))}
    except Exception as exc:
        report(exc, "own_order.the_pass: the followers' plan")
    taken: Dict[str, str] = {}
    counted: Dict[str, str] = {}
    acted_names: List[str] = []
    fought: List[str] = []
    for man in men(world):
        if getattr(world, "game_over", False):
            break
        said = plan.get(man.name)
        if said is None:
            continue
        try:
            row = _carry_out(world, executor, game_state, man, said, taken, counted, acted_names,
                             fought)
        except Exception as exc:
            report(exc, f"own_order.the_pass: {man.name}")
            row = _row(man, said, f"{_shown(man.name)} stays put — the night could not be carried out.",
                       "stay")
        rows.append(row)
        if plan_followers and (own(man) or {}).get("army"):
            try:
                rows.extend(_army.followers_night(world, executor, game_state, man, said,
                                                  plan_followers, fought))
            except Exception as exc:
                report(exc, f"own_order.the_pass: the followers of {man.name}")
    return rows


def _row(man, said: Dict[str, Any], message: str, act: str, **extra) -> Dict[str, Any]:
    row = {"marshal": man.name, "command": getattr(getattr(man, "strategic_order", None),
                                                    "command_type", "") or "",
           "order_status": "continues", "action": f"own_{act}", "message": message,
           "reason": message, "own": True, "act": act, "said": str(said.get("line") or "")}
    row.update(extra)
    return row


def _carry_out(world, executor, game_state, man, said, taken, counted, acted_names,
               fought) -> Dict[str, Any]:
    shown = _shown(man.name)
    spec = own(man) or {}
    lead_name = str(said.get("target") or "") if said.get("act") == "join" else ""
    if lead_name and lead_name in fought:
        # his lead has fought tonight: the join is over — the arrival roll
        # brought him in, or it did not. It was his one thing (§12).
        arrived = bool(getattr(man, "reinforced_this_turn", False))
        spec["acted"] = _turn(world)
        line = (f"{shown} marched to {_shown(lead_name)}'s battle and joined it" if arrived else
                f"{shown} tried to join {_shown(lead_name)}'s battle and did not arrive in time")
        _note(world, man, "join", str(man.location or ""), line, visible=True)
        acted_names.append(man.name)
        return _row(man, said, line + ".", "join", target=lead_name, arrived=arrived)
    if bool(getattr(man, "reinforced_this_turn", False)) and said.get("why") != "drawn in today":
        # the arrival roll drew him into a higher man's battle before his own
        # act came round — that was his one thing tonight (§12)
        lead = str(said.get("drawn_by") or (fought[-1] if fought else ""))
        spec["acted"] = _turn(world)
        line = (f"{shown} was drawn into {_shown(lead)}'s battle on the way — that was his night"
                if lead else f"{shown} marched to a friend's battle — that was his night")
        _note(world, man, "join", str(man.location or ""), line, visible=True)
        acted_names.append(man.name)
        return _row(man, said, line + ".", "join", target=lead, arrived=True)
    fresh = _read_in_turn(world, man, taken, counted)
    if key_of(fresh) != key_of(said):
        higher = _shown(acted_names[-1]) if acted_names else ""
        what = "fight" if acted_names and acted_names[-1] in fought else "move"
        cause = (f"{higher}'s {what} changed things" if higher
                 else str(fresh.get("why") or "the board changed"))
        line = f"{shown} stays put — {cause}"
        _note(world, man, "stay", str(man.location or ""), line, visible=False)
        return _row(man, said, line + ".", "stay")
    act = str(fresh.get("act") or "stay")
    if fresh.get("barred") or fresh.get("stuck"):
        # nights running (any night that moves his task on starts the count
        # again — the review, IC3-V): a barred road asks after two, a target
        # beyond his odds after three
        spec["blocked"] = int(spec.get("blocked", 0) or 0) + 1
        if fresh.get("barred") and spec["blocked"] >= BARRED_ASKS_AFTER:
            ask_why(world, man, f"his road has been barred {spec['blocked']} nights: "
                                f"{fresh.get('why') or 'the enemy stands across it'}")
        elif not fresh.get("barred") and spec["blocked"] >= WAITS_ASKS_AFTER:
            ask_why(world, man, f"he has waited {spec['blocked']} nights: "
                                f"{fresh.get('why') or 'his task is beyond him as things stand'}")
    elif act not in ("start", "asks", "recover"):
        spec["blocked"] = 0
    results = []
    for step in fresh.get("do") or []:
        command = {"marshal": man.name, "_strategic_execution": True, **step}
        result = executor.execute({"command": command}, game_state)
        results.append(result)
        if step.get("action") in ("unfortify",):
            continue
        if not (isinstance(result, dict) and result.get("success", False)):
            break
    battle = {}
    refused = ""
    if results:
        last = results[-1]
        from backend.commands.strategic import _combat_carry, attack_was_refused, refusal_reason
        if fresh.get("do") and fresh["do"][-1].get("action") == "attack":
            if attack_was_refused(last):
                refused = refusal_reason(last)
            else:
                battle = _combat_carry(last)
                fought.append(man.name)
        elif isinstance(last, dict) and not last.get("success", False):
            refused = str(last.get("message") or "it could not be done")
    if refused:
        line = f"{shown} could not carry out his night: {refused}"
        moved = any(isinstance(r, dict) and r.get("success") for r, s in
                    zip(results, fresh.get("do") or []) if s.get("action") != "unfortify")
        if moved:
            spec["acted"] = _turn(world)    # he went part of the way: that was his night
        _note(world, man, "stay", str(man.location or ""), line, visible=moved)
        return _row(man, said, line, "stay")
    if act not in WAITING_ACTS:
        spec["acted"] = _turn(world)
    if fresh.get("step_out"):
        spec["stepped_out"] = True
    acted_names.append(man.name)
    taken.update(_taken_by(fresh, world))
    for other in fresh.get("counts_on") or []:
        if other not in counted and other != man.name:
            counted[other] = man.name
    if spec.get("state") == "given":
        spec["state"] = "work"
    line = str(fresh.get("line") or "")
    # the morning reads the night in the past — a night he only made ready,
    # waited for your word or recovered is said as what it was
    if act == "start":
        line = f"{shown} made ready for his task: {task_words(spec)}"
    elif act == "asks":
        line = f"{shown} waited for your word — {fresh.get('why') or 'he asks for orders'}"
    elif act == "recover":
        line = f"{shown} recovered — {fresh.get('why') or 'his men rest'}"
    _note(world, man, act, str(fresh.get("place") or ""), line,
          visible=bool(fresh.get("visible")))
    return _row(man, said, line + ".", act, target=str(fresh.get("target") or ""),
                place=str(fresh.get("place") or ""), **battle)


def _note(world, man, act: str, place: str, line: str, *, visible: bool) -> None:
    """His night on his record (the third-night rule reads it) and on the log
    (the morning reads it)."""
    rec = record(man)
    man.own_record = rec
    acts = [a for a in rec.get("acts") or [] if isinstance(a, (list, tuple))]
    acts.append([act, place, _turn(world)])
    rec["acts"] = acts[-3:]
    rec["said"] = line
    rec["idle_run"] = (int(rec.get("idle_run", 0) or 0) + 1) if (act == "stay" or not visible) else 0
    world.log_event({"type": EVENT, "phase": "night", "act": act, "marshal": man.name,
                     "nation": man.nation, "place": place, "visible": bool(visible),
                     "message": line + "."})


QUIET_FRONT_ASKS = 4      # nights with nothing he would choose to do, no enemy near


def _quiet_front(world, man, rec: Dict[str, Any]) -> bool:
    """Four nights running he did nothing he would choose (stayed put, or a
    waiting act "again — nothing has changed") and France sees no enemy within
    two marches of him: he asks for work (R-ACTS — a man on his own really
    does something, or says he has nothing to do)."""
    if int(rec.get("idle_run", 0) or 0) < QUIET_FRONT_ASKS:
        return False
    from backend.commands import if_thens as _it
    for _enemy, where in _it.seen_enemies(world, man):
        if (_distance(world, man.location, where) or 9) <= 2:
            return False
    rec["idle_run"] = 0
    return True


def _the_count_holds(world, rows: List[Dict[str, Any]]) -> None:
    """N fell (a law lapsed for want of gold): the lowest-ranked orders end,
    no trust lost (§6.4)."""
    over = count(world) - allowed(world)
    if over <= 0:
        return
    for man in list(reversed(men(world)))[:over]:
        rows.append(end(world, man, "the laws that allowed it have lapsed — no trust is lost"))


# ═══════════════════════════ the close of the turn (§6.8) ═══════════════════

def close_of_turn(world, reports: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """After the enemy has moved and the standing orders have run: the night's
    rows join the turn's report (first), and each man's life table moves on —
    his record (won, lost, quiet), a task done, a pursuit lost, a friend
    fallen, an ask unanswered three turns, his trust under 30."""
    out = list(getattr(world, "_own_night_rows", None) or []) + list(reports or [])
    world._own_night_rows = []
    nation = _player(world)
    for marshal in (getattr(world, "marshals", None) or {}).values():
        if on_his_own(marshal) and marshal.nation != nation:
            marshal.strategic_order = None      # another crown's man has no task of ours
            from backend.commands.strategic import clear_order_bound_interrupt
            clear_order_bound_interrupt(marshal)
    for man in men(world):
        try:
            row = _life(world, man)
        except Exception as exc:
            report(exc, f"own_order.close_of_turn: {man.name}")
            row = None
        if row is not None:
            out.append(row)
    return out


def _life(world, man) -> Optional[Dict[str, Any]]:
    spec = own(man)
    if spec is None:
        return None
    turn = _turn(world)
    rec = record(man)
    man.own_record = rec
    won, lost = int(getattr(man, "battles_won", 0) or 0), int(getattr(man, "battles_lost", 0) or 0)
    tick_won, tick_lost = int(rec.get("tick_won", won) or 0), int(rec.get("tick_lost", lost) or 0)
    rec["held"] = False
    if won > tick_won and lost <= tick_lost:
        rec["last"], rec["quiet"] = "won", 0
        # a win on a night he did not attack: he beat off an attack on him
        rec["held"] = _int(spec, "acted") != turn
    elif lost > tick_lost:
        rec["last"], rec["quiet"] = "lost", 0
    else:
        rec["quiet"] = int(rec.get("quiet", 0) or 0) + 1
    rec["tick_won"], rec["tick_lost"] = won, lost
    if int(getattr(man, "strength", 0) or 0) <= 0 or getattr(man, "captured_by", ""):
        return end(world, man, "his corps is gone")
    if spec.get("state") == "asks":
        since = _int(spec.get("asks") or {}, "since", turn)
        if turn - since >= ASK_LAPSE:
            return end(world, man, "he had no answer for three turns and stands down — no trust is lost")
        return None
    trust = int(getattr(getattr(man, "trust", None), "value", 0) or 0)
    if trust < TRUST_NEEDED:
        ask_why(world, man, f"his trust in you has fallen to {trust}")
        return None
    task = spec.get("task")
    here = str(man.location or "")
    if task == "take":
        target = str(spec.get("target") or "")
        region = world.get_region(target)
        holder = getattr(region, "controller", None) if region is not None else None
        enemy_holds = bool(holder and holder != man.nation and world.is_at_war(man.nation, holder))
        if region is not None and here == target and not enemy_holds:
            spec["task"] = "hold"
            spec["area"] = [target]
            man.strategic_order.command_type = "HOLD"
            freed = "" if holder == man.nation or not holder else f" for {_court_name(holder)}"
            message = (f"{_shown(man.name)} has taken {_shown(target)}{freed} and holds it now."
                       if not freed else
                       f"{_shown(man.name)} has freed {_shown(target)}{freed}; he holds it now.")
            if spec.pop("goal", None):
                # Row IC, Session 3b: the war goal reached — his task is the
                # hold of it, as any take done; he serves no goal until you
                # name a new one and give him the task again.
                message += " Your war goal is won."
            world.log_event({"type": EVENT, "phase": "done", "marshal": man.name,
                             "nation": man.nation, "message": message})
            return {"marshal": man.name, "command": "HOLD", "order_status": "continues",
                    "action": "own_done", "message": message, "reason": message, "own": True}
    elif task == "pursue":
        quarry = world.get_marshal(str(spec.get("target") or ""))
        dead = (quarry is None or int(getattr(quarry, "strength", 0) or 0) <= 0
                or getattr(quarry, "captured_by", ""))
        if dead and int(spec.get("unseen", 0) or 0) == 0:
            # in France's sight to the last (the review, IC3-V: one destroyed
            # out of sight is "unseen" below, never known destroyed)
            return end(world, man, f"{_shown(spec.get('target'))} is destroyed — done", phase="done")
        if dead:
            quarry = None
        if quarry in (world.get_visible_enemies(man.nation) or []):
            spec["last_seen"] = quarry.location
            spec["unseen"] = 0
            ring = str(spec.get("ring") or "")
            d = _distance(world, ring, quarry.location) if ring else 0
            if d is not None and d > PURSUE_RING:
                ask_why(world, man, f"{_shown(quarry.name)} has left the ring of {PURSUE_RING} marches "
                                    f"around {_shown(ring)}")
        else:
            spec["unseen"] = int(spec.get("unseen", 0) or 0) + 1
            if spec["unseen"] >= UNSEEN_ASKS_AFTER:
                ask_why(world, man, f"{_shown(spec.get('target'))} has been out of sight {spec['unseen']} turns")
    elif task == "support":
        friend = world.get_marshal(str(spec.get("target") or ""))
        if friend is None or int(getattr(friend, "strength", 0) or 0) <= 0 \
                or getattr(friend, "captured_by", "") or friend.nation != man.nation:
            ask_why(world, man, f"{_shown(spec.get('target'))} has fallen; he holds where he stands")
    if _quiet_front(world, man, rec):
        ask_why(world, man, f"all has been quiet around {_shown(man.location)} for "
                            f"{QUIET_FRONT_ASKS} nights — he asks for a task with work in it")
        return None
    if spec.get("state") == "given":
        spec["state"] = "road"
    area = spec.get("area") or []
    if spec.get("state") in ("road", "work"):
        spec["state"] = "work" if (not area or here in area) else "road"
    return None


# ═══════════════════════════ what the screen says ═══════════════════════════

STATE_WORDS = {"given": "starts tomorrow night", "road": "on the road", "work": "at work",
               "asks": "asks for your word"}


def payload(world, marshal) -> Optional[Dict[str, Any]]:
    """His task as the client reads it (his card, the map, the Generals page)."""
    spec = own(marshal)
    if spec is None:
        return None
    reading = tonight_for(world, marshal) or {}
    n = needed(marshal, int(spec.get("risk", 0) or 0))
    # Row IC, Session 3b: the army he commands (and who follows him), the war
    # goal his task serves — each key rides only when it holds something.
    extra: Dict[str, Any] = {}
    if spec.get("army"):
        try:
            from backend.commands import army_task as _army
            extra.update(_army.commander_payload(world, marshal))
        except Exception as exc:
            report(exc, "own_order.payload: army_task.commander_payload")
    if spec.get("goal"):
        extra["goal"] = True
    return {
        **extra,
        "task": spec.get("task"), "target": spec.get("target"),
        "area": list(spec.get("area") or []), "words": task_words(spec),
        "state": spec.get("state"), "state_words": STATE_WORDS.get(spec.get("state"), ""),
        "asks": (spec.get("asks") or {}).get("why", "") if spec.get("asks") else "",
        "tonight": str(reading.get("line") or ""),
        "tonight_act": str(reading.get("act") or ""),
        "ahead": str(reading.get("ahead") or ""),
        # R-FRIENDS said on his card: the friend he would march to help
        "help": str(reading.get("help") or "") or _friend_line(world, marshal),
        "odds": str(reading.get("needed_words") or "") or needed_words(n),
        "risk": int(spec.get("risk", 0) or 0),
        "given_tonight": _int(spec, "given") == _turn(world),
        "stand_down": ("free — the actions it cost come back" if _int(spec, "given") == _turn(world)
                       else ("free" if spec.get("state") == "asks" or _int(spec, "acted") < 0
                             else f"free, but {STAND_DOWN_TRUST} of his trust")),
        "count": count_words(world),
        "lines": len(list(getattr(marshal.strategic_order, "if_thens", None) or [])),
    }


def tonight_rows(world) -> List[Dict[str, Any]]:
    """The End Turn list's and the desk's "Tonight" rows (empty when nobody is
    on his own — the feature is inert unused)."""
    rows = []
    for reading in tonight_shown(world):
        ahead = str(reading.get("ahead") or "")
        rows.append({"marshal": reading["marshal"], "shown": reading["shown"],
                     "act": reading["act"],
                     "line": "Tonight: " + str(reading.get("line") or "")
                     + (f". Tomorrow night, as things stand: {ahead}" if ahead else ""),
                     "may_day": bool(reading.get("may_day")), "visible": bool(reading.get("visible")),
                     "step_out": bool(reading.get("step_out"))})
        # Row IC, Session 3b: the men who follow him as his army's task move
        # right after him — their lines stand under his.
        army = str((own(world.get_marshal(reading["marshal"])) or {}).get("army") or "")
        if army:
            try:
                from backend.commands import army_task as _army
                behind = _army.tonight_rows(world, reading["marshal"])
                rows[-1]["army"] = army
                rows[-1]["followers"] = int(len(behind))
                rows.extend(behind)
            except Exception as exc:
                report(exc, "own_order.tonight_rows: army_task.tonight_rows")
    return rows


def morning_events(world) -> List[Dict[str, Any]]:
    """The night's lines for the turn's report and the morning dispatch — read
    from the event log, each told once."""
    out = []
    for event in getattr(world, "event_log", None) or []:
        if not isinstance(event, dict) or event.get("type") != EVENT or event.get("told"):
            continue
        event["told"] = True
        if event.get("phase") == "night":
            continue        # the night's own rows open the turn's report (`close_of_turn`)
        out.append({"type": EVENT, "phase": str(event.get("phase") or ""),
                    "act": str(event.get("act") or ""), "marshal": event.get("marshal"),
                    "nation": event.get("nation"), "visible": bool(event.get("visible")),
                    "message": str(event.get("message") or "")})
    return out


# ═══════════════════════════ asking him (§8.6) — free ═══════════════════════

def first_person(line: str, marshal) -> str:
    """"Ney marches from Alsace to Swabia" → "I march from Alsace to Swabia"."""
    shown = _shown(marshal.name)
    text = str(line or "")
    if text.startswith(shown + " "):
        rest = text[len(shown) + 1:]
        verb, _sep, tail = rest.partition(" ")
        fixes = {"marches": "march", "attacks": "attack", "storms": "storm", "lays": "lay",
                 "keeps": "keep", "takes": "take", "frees": "free", "sends": "send",
                 "pushes": "push", "digs": "dig", "falls": "fall", "stays": "stay",
                 "stands": "stand", "moves": "move", "strikes": "strike", "waits": "wait",
                 "starts": "start", "recovers": "recover", "has": "have"}
        verb = fixes.get(verb, verb)
        text = f"I {verb} {tail}".strip()
        text = (text.replace(" his attack", " his attack").replace(" him ", " me ")
                .replace(" his works", " my works").replace(" his scouts", " my scouts")
                .replace(" his area", " my area").replace(" his task", " my task")
                .replace(" he goes in", " I go in").replace(" he may", " I may")
                .replace(" he comes back", " I come back").replace(" he strikes", " I strike")
                .replace("he would choose", "I would choose").replace(" his way", " my way"))
    return text[:1].upper() + text[1:]


def answer(world, marshal, kind: str, place: str = "") -> Dict[str, Any]:
    """His answer, in his own voice — FREE, PURE: "what will you do?",
    "what do you see?", "can you take X?", "why did you…?". For a man not on his
    own, "what will you do?" says what he would do if set on his own."""
    from backend.game_logic import own_voice as _voice
    shown = _shown(marshal.name)
    nature = _nature(marshal)
    turn = _turn(world)
    if kind == "night":
        if on_his_own(marshal):
            reading = tonight_for(world, marshal) or read(world, marshal)
            if reading.get("act") == "start":
                ahead = read(world, marshal, preview=True)
                said = first_person(str(ahead.get("line") or ""), marshal)
                return {"says": f"Tonight I make ready. Tomorrow night, as things stand: {said}.",
                        "line": reading.get("line", "")}
            said = first_person(str(reading.get("line") or ""), marshal)
            return {"says": f"Tonight: {said}.", "line": reading.get("line", "")}
        if nature in ("bold", "careful") and not why_not(world, marshal, replacing=True):
            prop = proposal(world, marshal)
            spec, _why = spec_from(world, marshal, prop["task"], prop["target"])
            reading = read(world, marshal, spec, preview=True) if spec else {}
            said = first_person(str(reading.get("line") or ""), marshal) if reading else ""
            tail = (f" — the first night, {said if said.startswith('I ') else said[:1].lower() + said[1:]}"
                    if said else "")
            return {"says": f"Set me on my own, Sire, and I would {task_words(spec or {'task': prop['task'], 'target': prop['target']})}{tail}.",
                    "proposal": prop["line"]}
        order = getattr(marshal, "strategic_order", None)
        if order is not None:
            return {"says": f"I carry out your order, Sire: {str(order.original_command or order.command_type).strip()}"}
        return {"says": "I await your orders, Sire."}
    if kind == "sight":
        from backend.commands import if_thens as _it
        bits = []
        for enemy, where in _it.seen_enemies(world, marshal):
            odds = odds_against(world, marshal, enemy) if _in_strike_reach(world, marshal, where) else None
            label = (odds or {}).get("theirs") or ""
            size = f", {label}" if label else ""
            at = f" — our {odds['tenths']} to their 10" if odds else ""
            bits.append(f"{_shown(enemy.name)} at {_shown(where)}{size}{at}")
        if not bits:
            return {"says": "I see no enemy within my reach, Sire."}
        return {"says": "I see " + "; ".join(bits[:4]) + "."}
    if kind == "can":
        if not place or world.get_region(place) is None:
            return {"says": f"I don't know a place called {place}, Sire."}
        spec, why = spec_from(world, marshal, "take", place)
        if spec is None:
            return {"says": f"No, Sire — {why}."}
        reading = read(world, marshal, spec, preview=True)
        act = reading.get("act")
        if act in ("attack", "storm", "besiege", "take"):
            return {"says": f"Yes, Sire. {first_person(reading['line'], marshal)}."}
        if act == "march":
            return {"says": f"In time, Sire. {first_person(reading['line'], marshal)}."}
        reason = str(reading.get("why") or "not tonight")
        return {"says": f"Not tonight, Sire — {reason}."}
    if kind == "why":
        rec = _record_view(marshal)
        last = rec.get("said") or ""
        if not last:
            return {"says": ("I carried out your orders, Sire." if not on_his_own(marshal)
                             else "I have done nothing on my own yet, Sire.")}
        return {"says": f"Last night: {first_person(last, marshal)}."}
    return {"says": _voice.line(marshal.name, nature, "idle", turn)}
