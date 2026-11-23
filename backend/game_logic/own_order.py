"""Row IC, Session 3 (IC-10 / IC-11) — A MARSHAL ON HIS OWN.

`docs/INDEPENDENT_COMMAND_SPEC.md` §6 (the rules), §8.6 (talking to him), §12
(the edge cases), §13 (R-ACTS, R-TOGETHER, R-FRIENDS, R-TRUE, R-VARIETY). The
user's direction for this session, verbatim: "make sure when you give genmrals
autonomy they really do stuff and iunteract withe achother and even help their
friends your strategoic suggestions are just guidance for ai".

WHAT IT IS. A standing order — take a place, pursue a named enemy army, hold one
or two provinces, support a friend, or no task at all ("act on your own") —
that a BOLD or CAREFUL marshal carries out by his own judgement. Row IC,
Session 4b (IC4-D3) — the user's ruling, corrected twice: he is an autonomous
army run by an AI whose DECISION TREE weighs every act open to him; your task
is a GOAL that weighs in it, never a fence and never a forced act
(`own_judgement.judge`: your aim's step, the chances beside him, finding the
enemy, his ways of waiting — each weighed by his nature, his odds, the men
beside him and the board).

THE ORDER. `StrategicOrder.own` (a dict; the order keeps its standing type, so
every reader that asks "has he an order?" still says yes; "free" rides a HOLD
of where he stood). The strategic pass SKIPS an own order
(`strategic.process_strategic_orders`): the cannon-fire redirect, the
stalemate questions, the careful man's dig-in and the bold man's sally never
touch him. His if-thens (two at most) are still read by the if-then sub-pass —
only on a turn he waited (`acted_tonight`).

THE ONE READING. `read` / `tonight` are PURE — no write, no die, France's own
sight — and serve the read-back's intention, every question you ask him and THE
PASS that carries the act out.

THE PASS (`the_pass`) — the user's ruling of November 23, 2026, "He moves at
turn start": it runs as each turn OPENS, after the enemy has moved and the turn
has advanced, before you give orders and before the morning report is drawn
(`turn_manager._their_own_turn`) — highest rank first
(`precedence.order_of_precedence`), one thing a turn (D7). Each man reads the
board the higher men left and his act is carried out through the executor
(free — `_strategic_execution`); the morning report opens with what he did. No
preview: nothing says beforehand what he will do (an asked intention is said as
an intention).

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
PRICE = {"take": 2, "pursue": 2, "hold": 2, "support": 1, "free": 2}
CHANGE_PRICE = 1
EVENT = "own_night"          # the campaign log's and the dispatch's event type (a saved key)

# Row IC, Session 4b: "free" — on his own with NO task ("Ney, act on your own"):
# he makes war as he sees fit; it rides a HOLD of the province he stood on.
TASKS = ("take", "pursue", "hold", "support", "free")
ORDER_TYPE = {"take": "MOVE_TO", "pursue": "PURSUE", "hold": "HOLD", "support": "SUPPORT",
              "free": "HOLD"}
# the reverse map of the four tasks a STANDING order names ("free" shares HOLD
# and is read off the order's own spec, never off its type)
TASK_OF_ORDER = {v: k for k, v in ORDER_TYPE.items() if k != "free"}

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
    if getattr(marshal, "artillery", False) and task in ("take", "pursue", "free"):
        return f"{shown}'s guns can only hold or support on their own"
    if task == "free" and not _at_war(world):
        return "there is no war to make — give him a hold or a support"
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
        return 1, f"after {int(rec.get('quiet', 0))} quiet turns — he is impatient"
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
        # the charge's own rule: a corps in ANY province between bars it
        # ("Cannot charge through X — Y blocks the path": the executor checks
        # every middle province — Session 4b's measure: this read "any one
        # clear", and the charge was refused at the turn's start)
        between = [p for p in _near(world, here) if place in _near(world, p)]
        # (France's sight only: a corps France cannot see may still bar it —
        # his report then says so, the fog's honest surprise)
        if any(_foes_at(world, marshal, p) for p in between):
            return False
    return True


def _rallying(world, marshal, spec: Dict[str, Any], unfit: str) -> Dict[str, Any]:
    """His men are rallying from a defeat: he does not attack — "he falls back
    to his ground or digs in, then carries on" (the plan Session 4b's user
    approved). Off his ground — off the post you told him to hold, or on soil
    not France's — he falls back one march toward it, never into an enemy
    France sees; on his ground a careful man digs in where the works can be
    begun; else he rests his men. PURE."""
    shown = _shown(marshal.name)
    here = str(marshal.location or "")
    nation = str(getattr(marshal, "nation", "") or "")
    back = ""
    area = [p for p in (spec.get("area") or []) if p] if spec.get("task") == "hold" else []
    region = world.get_region(here)
    on_french_soil = region is not None and str(getattr(region, "controller", "") or "") == nation
    # Falling back is to SAFETY (Session 4b's measure: a rallying man fell back
    # onto his post three turns running, was thrown off it each time, and was
    # destroyed): never onto ground with or beside an enemy France sees, never
    # straight back where he came from last turn, never a third time the same.
    rec = _record_view(marshal)
    acts = [a for a in rec.get("acts") or [] if isinstance(a, (list, tuple)) and len(a) >= 3]
    came_from = (str(acts[-1][3] or "") if acts and len(acts[-1]) >= 4
                 and _int({"t": acts[-1][2]}, "t") == _turn(world) - 1 else "")
    last_two = [tuple(a[:2]) for a in acts[-2:]]

    def _safe(place: str) -> bool:
        if not place or place == came_from or _foes_at(world, marshal, place):
            return False
        if last_two == [("fall_back", place), ("fall_back", place)]:
            return False
        return not any(_foes_at(world, marshal, p) for p in _near(world, place))

    if area and here not in area:
        best = None
        for post in area:
            road = list(_road(world, marshal, post) or [])
            if road and _safe(road[0]):
                if best is None or (len(road), road[0]) < best:
                    best = (len(road), road[0])
        back = best[1] if best else ""
    elif not on_french_soil:
        for place in sorted(_near(world, here)):
            ground = world.get_region(place)
            if (ground is not None and str(getattr(ground, "controller", "") or "") == nation
                    and _safe(place)):
                back = place
                break
    if back:
        from backend.game_logic.own_judgement import move_is_open
        back = back if move_is_open(world, marshal, back) else ""
    if back:
        do = ([{"action": "unfortify"}] if getattr(marshal, "fortified", False) else [])
        return _reading(marshal, "fall_back",
                        f"{shown} falls back to {_shown(back)} — {unfit}",
                        why=unfit, place=back, target=back, do=do + [{"action": "move", "target": back}])
    if _nature(marshal) == "careful" and not getattr(marshal, "cavalry", False):
        from backend.commands.tactical_executor import fortify_refusal
        if not fortify_refusal(world, marshal)[0]:
            return _reading(marshal, "dig_in", f"{shown} digs in at {_shown(here)} — {unfit}",
                            why=unfit, place=here, target=here, do=[{"action": "fortify"}])
    return _reading(marshal, "recover", f"{shown} recovers — {unfit}", why=unfit, place=here)


def _engaged_by(world, marshal) -> List[Any]:
    """The enemy corps (at war, standing) in his own province. While they stand
    there he may attack only them and march only onto French soil — the
    executor's own engagement rules ("Cannot attack elsewhere while engaged",
    `combat_executor`; "Cannot advance while engaged", `movement_executor`).
    (A corps in his own province is always seen.) PURE."""
    here = str(getattr(marshal, "location", "") or "")
    nation = str(getattr(marshal, "nation", "") or "")
    if not here or not nation:
        return []
    try:
        return [m for m in world.get_marshals_in_region(here)
                if m.nation != nation and int(getattr(m, "strength", 0) or 0) > 0
                and world.is_at_war(nation, m.nation)]
    except Exception as exc:
        report(exc, "own_order._engaged_by")
        return []


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
    here = str(marshal.location or "")
    if place != here:
        engaged = _engaged_by(world, marshal)
        if engaged:
            return None, (f"{_names([e.name for e in engaged])} at {_shown(here)} must be "
                          "dealt with first")
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
        return None, f"{_shown(taken['~' + place])} marches into {_shown(place)} this turn"
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
    nights = "" if left == 0 else f" — {left} more march{'es' if left != 1 else ''} to go"
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


def _waiting_options(world, marshal, spec: Dict[str, Any], need: Dict[str, Any],
                     rec: Dict[str, Any], taken: Dict[str, str]) -> List[Dict[str, Any]]:
    """His own ways of waiting, by nature (§6.7.3) — each a real act, in the
    order his nature would try them. Row IC, Session 4b: his judgement weighs
    them beside everything else (`own_judgement._waits`); `_waiting` picks."""
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
        # the executor's own predicate (`fortify_refusal`): no works while an
        # enemy stands on his ground, nor in an aggressive stance (Session 4b's
        # measure: "cannot fortify while engaged" refused a chosen dig-in)
        from backend.commands.tactical_executor import fortify_refusal
        if not fortify_refusal(world, marshal)[0]:
            resolve = (" — his Iron Resolve starts to build (each turn dug in makes his next attack "
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
    return options


def _waiting(world, marshal, spec: Dict[str, Any], need: Dict[str, Any], rec: Dict[str, Any],
             taken: Dict[str, str], friend_line: str) -> Dict[str, Any]:
    """His own way of waiting, by nature (§6.7.3), never the same act at the
    same place a third turn running while another sensible one exists (§6.7.4)."""
    shown = _shown(marshal.name)
    here = str(marshal.location or "")
    options = _waiting_options(world, marshal, spec, need, rec, taken)
    acts = [tuple(a[:2]) for a in (rec.get("acts") or []) if isinstance(a, (list, tuple)) and len(a) >= 2]
    last_two = acts[-2:]

    def _third(row) -> bool:
        return len(last_two) == 2 and all(tuple(a) == (row["act"], row["place"]) for a in last_two)

    fresh = [row for row in options if not _third(row)]
    if fresh:
        pick = fresh[0]
        if options and fresh[0] is not options[0]:
            # the third-night rule turned him from what he would have done
            # again: his morning line says so (`own_voice`, "third_night")
            pick = dict(pick)
            pick["changed"] = True
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
        pick = _reading(marshal, "stay", words + " — nothing within his reach to do",
                        place=here, why="nothing within his reach to do")
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
                return None, (f"{_shown(quarry.name)} is too strong for him now: our "
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
        # Row IC, Session 4b (IC4-D3): the old "one step outside his area, once
        # per order" is gone — an enemy beside the ground he holds is a CHANCE
        # his judgement weighs against keeping his post (`own_judgement`).
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
    """What he does at the start of a turn — PURE. `spec` is his task (default:
    his order's own); `taken` the targets higher men have taken (enemy or place
    → name); `preview`: a task not yet given (the read-back's intention).

    Row IC, Session 4b (IC4-D3): his task's own step is ONE option his
    judgement weighs beside the chances around him, finding the enemy and his
    ways of waiting (`own_judgement.judge`) — the user's "orders should be
    guiding ai that has its own actions and does its own thing"."""
    spec = spec if spec is not None else (own(marshal) or {})
    taken = dict(taken or {})
    shown = _shown(marshal.name)
    turn = _turn(world)
    rec = _record_view(marshal)
    here = str(marshal.location or "")
    if not preview:
        if spec.get("state") == "asks":
            why = str((spec.get("asks") or {}).get("why") or "he waits for your word")
            return _reading(marshal, "asks", f"{shown} waits for your word — {why}", why=why,
                            place=here)
        if _int(spec, "given") == turn:
            # given during this turn: his first move is at the start of the next
            ahead = read(world, marshal, spec, taken, preview=True)
            out = _reading(marshal, "start", f"{shown} makes his first move at the start of next turn",
                           place=here, why="given this turn")
            out["ahead"] = str(ahead.get("line") or "")
            return out
        if (str(getattr(marshal, "name", "")) == "Bernadotte" and spec.get("late")
                and _int(spec, "given", -9) + 1 == turn):
            return _reading(marshal, "start",
                            f"{shown} starts a turn late, as is his way",
                            place=here, why="his way")
        # ONE MOVE OF HIS OWN A TURN (§6.3): his move already made this turn,
        # or a friend's battle he was drawn into this turn — his next move is at
        # the start of the next turn. (An order you give him by hand is carried
        # out ON TOP of his own move, at its usual price — the user's "like any
        # other general".)
        if _int(spec, "acted") == turn:
            return _reading(marshal, "stay", f"{shown} has made his move this turn",
                            place=here, why="his move is made")
        if bool(getattr(marshal, "reinforced_this_turn", False)):
            return _reading(marshal, "stay",
                            f"{shown} fought beside a friend this turn — he moves again at the start "
                            "of next turn", place=here, why="drawn in this turn")
    unfit = _unfit(world, marshal)
    if unfit:
        return _rallying(world, marshal, spec, unfit)
    if int(getattr(marshal, "strength", 0) or 0) <= 0:
        return _reading(marshal, "stay", f"{shown} has no corps", why="no corps")
    from backend.commands import if_thens as _it
    reaching = any(True for _e, _w in _it.seen_enemies(world, marshal))
    need = needed(marshal, int(spec.get("risk", 0) or 0), rec, reaching=reaching)
    goal: Optional[Dict[str, Any]] = None
    why = ""
    join = None
    if str(spec.get("task") or "") != "free":
        goal, why = _task_reading(world, marshal, spec, need, rec, taken)
        if goal is None and why.startswith("taken:"):
            lead = why.split(":", 1)[1]
            join = _join(world, marshal, lead, taken, need)
            why = ""
    from backend.game_logic import own_judgement as _judgement
    reading = _judgement.judge(world, marshal, spec, need, rec, taken, goal=goal, goal_why=why,
                               join=join)
    reading["needed"] = int(need["needed"])
    reading["needed_words"] = needed_words(need)
    return reading


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
    if task == "free":
        # no task: a higher man's battle beside him is his to join
        return (_distance(world, marshal.location, place) or 9) <= 1
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
            # (his line follows the task proposed: a hold is never pitched as
            # a chase — the verification, three skeptics of three)
            "says": _voice.voice(world, marshal, "proposal_hold" if task == "hold" else "proposal")}


# ═══════════════════════════ giving it (§6.3) ═══════════════════════════════

def spec_from(world, marshal, task: str, target: str, *, area: Optional[List[str]] = None,
              risk: int = 0) -> Tuple[Optional[Dict[str, Any]], str]:
    """A task spec, checked — `(spec, "")` or `(None, why)` in plain words."""
    shown = _shown(marshal.name)
    if task not in TASKS:
        return None, "a task is one of take, chase, hold or support — or none (\"act on your own\")"
    target = str(target or "")
    if task == "free":
        # Row IC, Session 4b: no task — he makes war as he sees fit
        if not _at_war(world):
            return None, "there is no war to make — give him a hold or a support"
        target = ""
        area = []
    elif task == "hold":
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
    """"take Swabia" · "hold Milan and Piedmont" · "chase Mack" · "support Ney" ·
    "make war as he sees fit" (no task)."""
    task = spec.get("task")
    if task == "free":
        return "make war as he sees fit"
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
        return _refused_in_his_words(world, marshal, {
            "success": False, "message": f"{shown} cannot be set on his own: {refusal}.",
            "no_action_cost": True})
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
    # (a man with no task rides a HOLD of the province he stood on — every
    # reader that asks "has he an order?" still says yes)
    target = spec["target"] or (str(marshal.location or "") if spec["task"] == "free" else "")
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
    # Row IC, Session 4 (IC-13): the line the read-back showed is the line he
    # says — his objection, else how he was told, else plain (`kind_given`);
    # the ONE thing he remembers, if it is on his mind, is said first and once.
    objected = "" if own_proposal else objection(world, marshal, spec)
    voices: List[Dict[str, Any]] = []
    said = (_voice.recall_memory(world, marshal, said=True)
            or _voice.speak(world, marshal, _voice.kind_given(int(spec.get("risk", 0) or 0),
                                                              bool(objected),
                                                              free=spec.get("task") == "free")))
    if said:
        voices.append({"speaker": marshal.name, "says": said})
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
            # ... and he says so, in his own nature's words; a man who
            # remembers a slight keeps it (`own_voice.REMEMBERS`).
            grudge = _voice.speak(world, senior, "passed_over")
            _voice.note_memory(world, senior, "passed_over", marshal.name)
            if grudge:
                voices.append({"speaker": senior.name, "says": grudge})
    cost_words = ""
    if objected:
        cost = objection_cost(marshal)
        try:
            marshal.modify_trust(-cost)
        except Exception as exc:
            report(exc, "own_order.give: objection trust")
        cost_words = f" He objected ({objected}); giving it anyway cost {cost} of his trust."
    verb = "changes his task" if changing else "is on his own"
    # (the user's "He moves at turn start": whatever is given this turn, his
    # next move is at the start of the next)
    starts = ("He makes his first move at the start of next turn." if _int(spec, "given") == turn
              else "He turns to it at the start of next turn.")
    # Row IC, Session 4 (IC-13): HIS line is not folded into the staff's
    # sentence any more — it rides `voices`, drawn once, with his portrait and
    # name (pressed in the real client: it stood twice in the reply).
    message = (f"{shown} {verb}: {task_words(spec)}. {starts} "
               f"{count_words(world)}.{took_ill}{cost_words}")
    world.log_event({"type": EVENT, "phase": "given", "marshal": marshal.name,
                     "nation": marshal.nation, "task": spec["task"], "target": target,
                     "changing": bool(changing), "message": message, "told": True})
    return {"success": True, "message": message, "variable_action_cost": price,
            "own": payload(world, marshal), "marshal": marshal.name,
            **({"voices": voices} if voices else {})}


def _refused_in_his_words(world, marshal, out: Dict[str, Any]) -> Dict[str, Any]:
    """Row IC, Session 4 (IC-13): a man who follows orders to the letter,
    asked to act on his own, says so HIMSELF beside the staff's plain refusal
    (`voices`). PURE — a refused order changes nothing, so nothing is recorded."""
    try:
        if _nature(marshal) == "literal":
            from backend.game_logic import own_voice as _voice
            said = _voice.voice(world, marshal, "refusal")
            if said:
                out["voices"] = [{"speaker": marshal.name, "says": said}]
    except Exception as exc:
        report(exc, "own_order._refused_in_his_words")
    return out


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
    asked = spec.get("state") == "asks" or bool(spec.get("question"))
    if not refund and not asked and _int(spec, "acted") >= 0:
        trust_cost = STAND_DOWN_TRUST
        try:
            marshal.modify_trust(-trust_cost)
        except Exception as exc:
            report(exc, "own_order.stand_down: trust")
    still = _followers_words(world, marshal)      # (Session 3b) read before his task is gone
    marshal.strategic_order = None
    from backend.commands.strategic import clear_order_bound_interrupt
    clear_order_bound_interrupt(marshal)
    # Row IC, Session 4 (IC-13): recalled from a task he had begun, he says
    # so — and a man who remembers a recall keeps it. (A task taken back the
    # turn it was given is a withdrawal: nothing was begun, nothing is said.)
    recalled = ""
    if not refund:
        from backend.game_logic import own_voice as _voice
        recalled = _voice.speak(world, marshal, "recalled")
        _voice.note_memory(world, marshal, "recalled")
    if refund:
        world.actions_remaining = int(getattr(world, "actions_remaining", 0) or 0) + refund
    tail = (f" The {refund} action{'s' if refund != 1 else ''} it cost come back." if refund
            else (f" Recalled in the middle of his task, he loses {trust_cost} trust." if trust_cost
                  else "")) + still
    message = f"{shown} stands down and awaits your orders.{tail} {count_words(world)}."
    world.log_event({"type": EVENT, "phase": "stood_down", "marshal": marshal.name,
                     "nation": marshal.nation, "message": message, "told": True})
    return {"success": True, "message": message, "no_action_cost": True,
            "refunded": refund, "marshal": marshal.name,
            **({"voices": [{"speaker": marshal.name, "says": recalled}]} if recalled else {})}


def carry_on(world, marshal) -> Dict[str, Any]:
    """Answer his ask: carry on — free; the counters that made him ask start
    again (a pursuit's ring is drawn again where he stands)."""
    spec = own(marshal)
    shown = _shown(marshal.name)
    if spec is None:
        return {"success": False, "message": f"{shown} is not on his own.", "no_action_cost": True}
    if spec.get("state") != "asks" and not spec.get("question"):
        return {"success": True, "message": f"{shown} is already carrying on with his task.",
                "no_action_cost": True}
    if spec.get("state") == "asks":
        spec["state"] = "work"
    spec["asks"] = None
    spec.pop("question", None)
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


def ask_why(world, marshal, why: str, *, freeze: Optional[bool] = None, cause: str = "") -> None:
    """He asks for your word. Row IC, Session 4b (IC4-D3): in a war a question
    about his task (a barred road, a target too strong, a quarry lost, a friend
    fallen) does NOT stop him — his judgement carries on while it waits
    (`spec["question"]`), and unanswered it drops after three turns. He stops
    and WAITS (`state` "asks") only when his trust has fallen under 30, or at
    peace (today's rules there). `freeze`: None = by those rules. `cause`: what
    the question is about ("barred", "stuck", "ring", "unseen") — a question
    already standing for the same cause is not asked again (its words carry a
    running count; the review of Session 4b: keyed on the words he re-asked
    every turn and the three-turn lapse never came)."""
    spec = own(marshal)
    if spec is None or spec.get("state") == "asks":
        return
    if freeze is None:
        freeze = not _at_war(world)
    turn = _turn(world)
    shown = _shown(marshal.name)
    from backend.game_logic import own_voice as _voice
    if not freeze:
        held = spec.get("question") or {}
        if isinstance(held, dict) and (held.get("why") == why
                                       or (cause and held.get("cause") == cause)):
            return                  # asked already — once, never every turn
        spec["question"] = {"why": why, "since": turn, **({"cause": cause} if cause else {})}
        message = f"{shown} asks for your word — {why}. He carries on by his own judgement meanwhile."
        said = _voice.speak(world, marshal, "asks")
        if said:
            spec["question"]["says"] = said
        world.log_event({"type": EVENT, "phase": "asks", "marshal": marshal.name,
                         "nation": marshal.nation, "message": message, "question": True,
                         **({"says": said, "speaker": marshal.name} if said else {})})
        return
    spec["state"] = "asks"
    spec["asks"] = {"why": why, "since": turn}
    message = f"{shown} asks for your word: {why}."
    said = _voice.speak(world, marshal, "asks")      # the reason is the plain words' to carry
    if said:
        spec["asks"]["says"] = said
    world.log_event({"type": EVENT, "phase": "asks", "marshal": marshal.name,
                     "nation": marshal.nation, "message": message,
                     **({"says": said, "speaker": marshal.name} if said else {})})


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
    # Row IC, Session 4 (IC-13): a task DONE is said in his own words (a task
    # that only lapsed — no answer, a law gone, his corps gone — says nothing).
    said = ""
    if phase == "done" and int(getattr(marshal, "strength", 0) or 0) > 0:
        from backend.game_logic import own_voice as _voice
        said = _voice.speak(world, marshal, "done")
    voice_keys = {"says": said, "speaker": marshal.name} if said else {}
    world.log_event({"type": EVENT, "phase": phase, "marshal": marshal.name,
                     "nation": marshal.nation, "message": message, **voice_keys})
    return {"marshal": marshal.name, "command": "", "order_status": "completed",
            "action": "own_ended", "message": message, "reason": message, **voice_keys}


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
    objected = "" if own_prop else objection(world, marshal, spec)
    # Row IC, Session 4 (IC-13): the line he WOULD say — PURE (`voice`: never
    # one of his last three), and the very line `give` says and records; the
    # one thing he remembers, while it is on his mind, comes first.
    said = (_voice.recall_memory(world, marshal, said=False)
            or _voice.voice(world, marshal, _voice.kind_given(risk, bool(objected),
                                                              free=task == "free")))
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
        return _refused_in_his_words(world, marshal, {
            "success": False, "no_action_cost": True,
            "message": f"{shown} cannot be set on his own: {reading.get('why') or 'no task he can take'}."})
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
    """His own move is made this turn (his if-thens sleep). (The name is kept:
    `strategic._if_thens_pass` reads it.)"""
    spec = own(marshal)
    return spec is not None and _int(spec, "acted") == _turn(world)


def keeps_task(marshal) -> bool:
    """Row IC, Session 4b (IC4-D3, the user's "beaten, he keeps his
    autonomy"): a man of the player's on his own whose corps still stands
    keeps his task when he is driven off — a forced retreat, a breakout, a
    broken square, the enemy's charge. Every place that would wipe an order
    asks this first (`combat_executor`, `world_state`, `tactical_executor`);
    the places that END a task (captured, corps gone, a road home at peace)
    do not."""
    return (on_his_own(marshal) and int(getattr(marshal, "strength", 0) or 0) > 0
            and not getattr(marshal, "captured_by", ""))


def target_gone(world, marshal, why: str) -> bool:
    """The man his task names has left the board (a removed corps, a client's
    contingent recalled). In a war a man on his own goes on with NO task —
    True: the caller keeps his order. At peace (or not on his own) False: the
    caller ends it as before."""
    spec = own(marshal)
    if spec is None or not keeps_task(marshal) or not _at_war(world):
        return False
    if spec.get("task") in ("pursue", "support"):
        _freed(world, marshal, spec, why)
    return True


def after_retreat(world, marshal) -> None:
    """Driven off: his post is broken (a hold's ground is to be taken back) and
    a chase's ring is drawn again where he stands — his task stands. He rallies
    first (`_unfit` reads the rally), then carries on."""
    spec = own(marshal)
    if spec is None:
        return
    marshal.holding_position = False
    marshal.hold_region = ""
    area = [p for p in (spec.get("area") or []) if p]
    if area and str(marshal.location or "") not in area and spec.get("state") == "work":
        spec["state"] = "road"
    if spec.get("task") == "pursue":
        spec["ring"] = str(marshal.location or "")


def answers_the_guns(marshal) -> bool:
    """R-FRIENDS: a man on his own goes to a friend's battle next to him even dug
    in or on his hold's post (the two rules that keep a man at his post do not
    hold him); the rule against a man he hates still holds (`combat_executor`)."""
    return on_his_own(marshal) and int(getattr(marshal, "strength", 0) or 0) > 0


# ═══════════════════════════ the pass (D6, D7, D8) ══════════════════════════

def the_pass(world, executor, game_state) -> List[Dict[str, Any]]:
    """Row IC, Session 4b — the user's ruling "He moves at turn start": as each
    turn OPENS (after the enemy has moved and the turn has advanced, before you
    give orders — `turn_manager._their_own_turn`) every man on his own makes his
    move, highest rank first, each on the board the higher men left (one thing
    a turn, D7). Returns the report rows: they open the morning's report."""
    rows: List[Dict[str, Any]] = []
    world._own_night_rows = rows       # (the name is kept: the measures read it)
    if not men(world):
        return rows
    _the_count_holds(world, rows)
    try:
        from backend.commands import army_task as _army
    except Exception as exc:
        report(exc, "own_order.the_pass: army_task")
        _army = None
    taken: Dict[str, str] = {}
    counted: Dict[str, str] = {}
    acted_names: List[str] = []
    fought: List[str] = []
    drawn_by: Dict[str, Tuple[str, str]] = {}     # a man not yet moved → (whose battle, where)
    for man in men(world):
        if getattr(world, "game_over", False):
            break
        # the men not yet drawn into a battle: the usual arrival roll of THIS
        # man's battle may draw one in — after his own move (his line then says
        # so) or before it (his move is that battle)
        free_before = {m.name for m in men(world)
                       if not getattr(m, "reinforced_this_turn", False)}
        try:
            said = _read_in_turn(world, man, taken, counted)
        except Exception as exc:
            report(exc, f"own_order.the_pass: the reading of {man.name}")
            said = _reading(man, "stay", f"{_shown(man.name)} stays put",
                            why="the board could not be read")
        if man.name in drawn_by:
            said = dict(said)
            said["drawn_by"], said["drawn_at"] = drawn_by[man.name]
        try:
            row = _carry_out(world, executor, game_state, man, said, taken, counted, acted_names,
                             fought)
        except Exception as exc:
            report(exc, f"own_order.the_pass: {man.name}")
            row = _row(man, said, f"{_shown(man.name)} stayed put — his move could not be carried out.",
                       "stay")
        rows.append(row)
        # Row IC, Session 3b: the men who FOLLOW a commander as his army's task
        # move right after him (`army_task`: the army moves as one)
        if _army is not None and (own(man) or {}).get("army"):
            try:
                plan_followers = {r["marshal"]: r for r in _army.tonight(world, [said])}
                rows.extend(_army.followers_night(world, executor, game_state, man, said,
                                                  plan_followers, fought))
            except Exception as exc:
                report(exc, f"own_order.the_pass: the followers of {man.name}")
        _drawn_in_after_his_move(world, rows, free_before, man, row)
        moved = {str(r.get("marshal")) for r in rows}
        field = str(row.get("place") or getattr(man, "location", "") or "")
        for other in men(world):
            if (other.name in free_before and other.name not in moved and other.name != man.name
                    and getattr(other, "reinforced_this_turn", False)):
                drawn_by.setdefault(other.name, (man.name, field))
    return rows


def _drawn_in_after_his_move(world, rows: List[Dict[str, Any]], free_before: set, lead,
                             lead_row: Dict[str, Any]) -> None:
    """A man who had made his move and was then drawn into `lead`'s battle by
    the usual arrival roll: his line says so — the morning (R-REPORT) and his
    card ("This turn: …") never leave him where his march ended when the roll
    carried him on to a friend's field. (The measure, November 23, 2026:
    "Lannes marched from Swabia to Franconia", and he stood at Munich, in Ney's
    battle.)"""
    place = str(lead_row.get("place") or getattr(lead, "location", "") or "")
    for row in rows:
        name = str(row.get("marshal") or "")
        if name not in free_before or name == lead.name:
            continue
        man = world.marshals.get(name)
        if man is None or not getattr(man, "reinforced_this_turn", False):
            continue
        tail = f" — then the usual roll drew him into {_shown(lead.name)}'s battle at {_shown(place)}"
        message = str(row.get("message") or "").rstrip(".")
        row["message"] = row["reason"] = message + tail + "."
        row["drawn_in"] = lead.name
        rec = record(man)
        if rec.get("said"):
            rec["said"] = str(rec["said"]).rstrip(".") + tail
            man.own_record = rec


# The morning reads what he did, in the past (the user's "the morning report
# says what he did"): the leading verb of his line, and the odds said as they
# were. Longest phrase first.
_PAST = (("keeps up the siege of", "kept up the siege of"), ("lays siege to", "laid siege to"),
         ("keeps to his works", "kept to his works"), ("sends his scouts", "sent his scouts"),
         ("pushes forward", "pushed forward"), ("marches into", "marched into"),
         ("marches from", "marched from"), ("marches to", "marched to"),
         ("marches after", "marched after"), ("cannot reach", "could not reach"),
         ("halts", "halted"),
         ("falls back", "fell back"), ("falls on", "fell on"), ("stands beside", "stood beside"),
         ("stands by", "stood by"), ("stays put", "stayed put"), ("digs in", "dug in"),
         ("moves up", "moved up"), ("attacks", "attacked"), ("strikes", "struck"),
         ("storms", "stormed"), ("takes", "took"), ("frees", "freed"), ("keeps", "kept"),
         ("stays", "stayed"), ("recovers", "recovered"), ("rests", "rested"),
         ("waits", "waited"), ("makes", "made"), ("has", "had"))


def told(line: str, marshal) -> str:
    """"Ney strikes Mack at Swabia — the odds are our 12 to their 10, and he
    goes in when they are our 5 to their 10 or better" → "Ney struck Mack at
    Swabia — the odds were our 12 to their 10"."""
    import re as _re
    shown = _shown(marshal.name)
    text = str(line or "")
    if text.startswith(shown + " "):
        rest = text[len(shown) + 1:]
        for now, then in _PAST:
            if rest == now or rest.startswith(now + " ") or rest.startswith(now + ","):
                rest = then + rest[len(now):]
                break
        text = f"{shown} {rest}"
    text = _re.sub(r", and he goes in when they are our [\d.]+ to their 10 or better", "", text)
    text = text.replace(" — the odds are our ", " — the odds were our ")
    text = text.replace(" (he may join)", "").replace(" (they may join)", "")
    text = text.replace(". May become a great battle", "")
    text = text.replace(" to take it if nothing unseen holds it", " to take it")
    text = text.replace(" and takes it", " and took it")
    return text


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
    origin = str(man.location or "")
    if lead_name and lead_name in fought:
        # his lead has fought this turn: the join is over — the arrival roll
        # brought him in, or it did not. It was his move (§12).
        arrived = bool(getattr(man, "reinforced_this_turn", False))
        spec["acted"] = _turn(world)
        line = (f"{shown} marched to {_shown(lead_name)}'s battle and joined it" if arrived else
                f"{shown} tried to join {_shown(lead_name)}'s battle and did not arrive in time")
        voice = _note(world, man, "join", str(man.location or ""), line, visible=True,
                      voiced=arrived, origin=origin, target=lead_name)
        acted_names.append(man.name)
        return _row(man, said, line + ".", "join", target=lead_name, arrived=arrived,
                    **_voiced(man, voice))
    if bool(getattr(man, "reinforced_this_turn", False)):
        # the arrival roll drew him into a higher man's battle before his own
        # move came round — that was his move this turn (§12). (The flag is
        # cleared as the turn advances, so at the turn-start pass it can only
        # be an earlier man's battle in this same pass — Session 4b's measure:
        # the reading now taken just before his move saw the flag, and the row
        # read "he fought beside a friend — he moves again next turn — unless
        # the usual roll draws him in first".)
        lead = str(said.get("drawn_by") or (fought[-1] if fought else ""))
        field = str(said.get("drawn_at") or "")
        spec["acted"] = _turn(world)
        line = (f"{shown} was drawn into {_shown(lead)}'s battle"
                + (f" at {_shown(field)}" if field else "")
                + " by the usual roll — that was his move this turn"
                if lead else f"{shown} marched to a friend's battle — that was his move this turn")
        voice = _note(world, man, "join", str(man.location or ""), line, visible=True,
                      origin=origin, target=lead)
        acted_names.append(man.name)
        return _row(man, said, line + ".", "join", target=lead, arrived=True, **_voiced(man, voice))
    # (read a moment ago, on the board the higher men left — the user's "He
    # moves at turn start" shows nothing beforehand, so there is no promise
    # to keep and nothing to re-read)
    fresh = said
    act = str(fresh.get("act") or "stay")
    if (fresh.get("barred") or fresh.get("stuck")) and str(fresh.get("kind") or "") == "wait":
        # turns running (a turn that moves your aim on starts the count again —
        # the review, IC3-V): a barred road asks after two, a target beyond his
        # odds after three. In a war the question does not stop him (`ask_why`).
        # Counted only on the turns he WAITED (Session 4b's review: a turn he
        # struck a chance or took a province is no turn waited — "he has
        # waited 3 turns" was said of a man who had been fighting).
        spec["blocked"] = int(spec.get("blocked", 0) or 0) + 1
        if fresh.get("barred") and spec["blocked"] >= BARRED_ASKS_AFTER:
            ask_why(world, man, cause="barred", why=f"his road has been barred {spec['blocked']} turns: "
                                f"{fresh.get('why') or 'the enemy stands across it'}")
        elif not fresh.get("barred") and spec["blocked"] >= WAITS_ASKS_AFTER:
            ask_why(world, man, cause="stuck", why=f"he has waited {spec['blocked']} turns: "
                                f"{fresh.get('why') or 'his task is beyond him as things stand'}")
    elif str(fresh.get("kind") or "") in ("goal", "join"):
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
        line = f"{shown} could not carry out his move: {refused}"
        moved = any(isinstance(r, dict) and r.get("success") for r, s in
                    zip(results, fresh.get("do") or []) if s.get("action") != "unfortify")
        if moved:
            spec["acted"] = _turn(world)    # he went part of the way: that was his move
        voice = _note(world, man, "stay", str(man.location or ""), line, visible=moved,
                      origin=origin, target=str(fresh.get("target") or ""))
        return _row(man, said, line, "stay", **_voiced(man, voice))
    if act not in WAITING_ACTS:
        spec["acted"] = _turn(world)
    acted_names.append(man.name)
    taken.update(_taken_by(fresh, world))
    for other in fresh.get("counts_on") or []:
        if other not in counted and other != man.name:
            counted[other] = man.name
    if spec.get("state") == "given":
        spec["state"] = "work"
    # the morning reads what he did, in the past (`told`) — a turn he only made
    # ready, waited for your word or rested is said as what it was
    line = told(str(fresh.get("line") or ""), man)
    if act == "start":
        # (in the pass only Bernadotte's late start — his way, §8 — reads so)
        line = (f"{shown} started a turn late, as is his way — his task: {task_words(spec)}"
                if fresh.get("why") == "his way"
                else f"{shown} makes his first move at the start of next turn — his task: "
                     f"{task_words(spec)}")
    elif act == "asks":
        line = f"{shown} waited for your word — {fresh.get('why') or 'he asks for orders'}"
    elif act == "recover":
        line = f"{shown} rested his men — {fresh.get('why') or 'they needed it'}"
    voice = _note(world, man, act, str(fresh.get("place") or ""), line,
                  visible=bool(fresh.get("visible")), changed=bool(fresh.get("changed")),
                  voice_act=_voice_act(act, battle, results, fresh.get("do") or [],
                                       str(fresh.get("why") or "")),
                  origin=origin, target=str(fresh.get("target") or ""))
    return _row(man, said, line + ".", act, target=str(fresh.get("target") or ""),
                place=str(fresh.get("place") or ""), kind=str(fresh.get("kind") or ""),
                chance=bool(fresh.get("chance")), weighed=list(fresh.get("weighed") or []),
                **battle, **_voiced(man, voice))


# Why a turn is a stay → the line that fits it ("claim" has none: the plain
# sentence says it — his move was made, he was drawn into a friend's battle,
# he has no corps).
STAY_SAYS = {"his move is made": "claim", "drawn in this turn": "claim",
             "no corps": "claim", "the board could not be read": "claim"}


def _voice_act(act: str, battle: Dict[str, Any], results: List[Any], do: List[Any],
               why: str = "") -> str:
    """The act his LINE answers (row IC, Session 4 — IC-13; the verification's
    upheld findings): a night with no battle was no fight — a take marched in
    (his "marched" line) or claimed the ground he stands on, a siege kept up,
    an attack that ran no battle: none of them says a "struck" line. A stay
    says the line that fits WHY he stayed (`STAY_SAYS`); a stay because the
    board changed says his "stayed" line."""
    from backend.game_logic import own_voice as _voice
    if act == "stay":
        if str(why or "") in STAY_SAYS:
            return STAY_SAYS[str(why)]
        # Row IC, Session 4b: a stay his judgement chose — held back from a
        # fight too strong for him ("stayed"), else a quiet wait ("waited")
        return act if "too strong" in str(why or "") else "look"
    if battle or _voice.KIND_OF_ACT.get(act) != "struck":
        return act
    if act == "take":
        marched_in = any(isinstance(r, dict) and r.get("success") and (s or {}).get("action") == "move"
                         for r, s in zip(results, do))
        return "march" if marched_in else "claim"
    return "claim"


def _voiced(man, voice: str) -> Dict[str, Any]:
    """The row's keys for the line HE said of his night (none when he said none)."""
    return {"says": voice, "speaker": man.name} if voice else {}


def _night_voice(world, man, act: str, rec: Dict[str, Any], changed: bool) -> str:
    """Row IC, Session 4 (IC-13): what HE says of his night — one line, said
    and remembered (`own_voice.speak`). In this order: the one thing he
    remembers, while it is on his mind; the night after a battle won or lost
    (his odds have moved — unless he fought again tonight); the third night's
    change; else the line of what he did. A night he only made ready or rested
    has none. It decides nothing and claims nothing the plain sentence does
    not say."""
    from backend.game_logic import own_voice as _voice
    kind = _voice.KIND_OF_ACT.get(act, "")
    if not kind:
        return ""
    remembered = _voice.recall_memory(world, man, said=True)
    if remembered:
        return remembered
    news = str(rec.pop("news", "") or "")
    if news and kind != "struck":
        kind = "after_win" if news == "won" else "after_loss"
    elif changed and kind in ("waited", "dug_in"):
        kind = "third_night"
    return _voice.speak(world, man, kind)


def _note(world, man, act: str, place: str, line: str, *, visible: bool,
          changed: bool = False, voiced: bool = True, voice_act: str = "",
          origin: str = "", target: str = "") -> str:
    """His move on his record (the third-turn rule and the step he came by
    read it: `[act, place, turn, where he stood, whom or what]`) and on the
    log (the morning reads it). Returns the line HE says of it ("" when he
    has none — `_night_voice`)."""
    rec = record(man)
    man.own_record = rec
    acts = [a for a in rec.get("acts") or [] if isinstance(a, (list, tuple))]
    acts.append([act, place, _turn(world), str(origin or ""), str(target or "")])
    rec["acts"] = acts[-3:]
    rec["said"] = line
    rec["idle_run"] = (int(rec.get("idle_run", 0) or 0) + 1) if (act == "stay" or not visible) else 0
    try:
        voice = _night_voice(world, man, voice_act or act, rec, changed) if voiced else ""
    except Exception as exc:
        report(exc, f"own_order._note: the voice of {man.name}")
        voice = ""
    if voice:
        rec["voice"] = voice
    else:
        rec.pop("voice", None)
    world.log_event({"type": EVENT, "phase": "night", "act": act, "marshal": man.name,
                     "nation": man.nation, "place": place, "visible": bool(visible),
                     "message": line + ".",
                     **({"says": voice, "speaker": man.name} if voice else {})})
    return voice


QUIET_FRONT_ASKS = 4      # turns with nothing he would choose to do, no enemy near


def _quiet_front(world, man, rec: Dict[str, Any]) -> bool:
    """AT PEACE: four turns running he did nothing he would choose (stayed put,
    or a waiting act "again — nothing has changed") and France sees no enemy
    within two marches of him — he asks for work. Row IC, Session 4b (IC4-D3):
    in a war he never asks for work; his judgement carries on."""
    if _at_war(world):
        return False
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
    """After the enemy has moved and the standing orders have run: each man's
    life table moves on — his record (won, lost, quiet), a task done, a pursuit
    lost, a friend fallen, an ask unanswered three turns, his trust under 30.
    (Row IC, Session 4b: his move's rows are told in the report of the turn
    that OPENED with it — `turn_manager._their_own_turn` — never again here.)"""
    out = list(reports or [])
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


def _freed(world, man, spec: Dict[str, Any], why: str) -> Dict[str, Any]:
    """Row IC, Session 4b (IC4-D3, the user's "if you give them nothing they
    should make decisions"): a task run out in a war — the quarry destroyed,
    the friend he stood by fallen — leaves him on his own with NO task: he
    makes war as he sees fit until you give him another (a change, 1 action)."""
    spec["task"] = "free"
    spec["target"] = ""
    spec["area"] = []
    spec["ring"] = ""
    spec["last_seen"] = ""
    spec["unseen"] = 0
    spec["blocked"] = 0
    spec.pop("question", None)
    spec.pop("goal", None)
    order = getattr(man, "strategic_order", None)
    if order is not None:
        order.command_type = "HOLD"
        order.target = str(man.location or "")
        order.target_type = "region"
    message = (f"{_shown(man.name)} has done his task: {why}. He makes war as he sees fit now — "
               "give him a new task any time.")
    from backend.game_logic import own_voice as _voice
    said = _voice.speak(world, man, "done")
    voice_keys = {"says": said, "speaker": man.name} if said else {}
    world.log_event({"type": EVENT, "phase": "done", "marshal": man.name,
                     "nation": man.nation, "message": message})
    return {"marshal": man.name, "command": "HOLD", "order_status": "continues",
            "action": "own_done", "message": message, "reason": message, "own": True,
            **voice_keys}


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
        rec["news"] = "won"         # (Session 4) said once, the next night he does not fight
        # a win on a night he did not attack: he beat off an attack on him
        rec["held"] = _int(spec, "acted") != turn
    elif lost > tick_lost:
        rec["last"], rec["quiet"] = "lost", 0
        rec["news"] = "lost"
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
    question = spec.get("question")
    if isinstance(question, dict) and turn - _int(question, "since", turn) >= ASK_LAPSE:
        spec.pop("question", None)      # unanswered: it drops; he was at work all along
        spec["blocked"] = 0             # (and its count starts again: no question straight back)
        spec["unseen"] = 0
    trust = int(getattr(getattr(man, "trust", None), "value", 0) or 0)
    if trust < TRUST_NEEDED:
        ask_why(world, man, f"his trust in you has fallen to {trust}", freeze=True)
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
            from backend.game_logic import own_voice as _voice
            said = _voice.speak(world, man, "done")
            voice_keys = {"says": said, "speaker": man.name} if said else {}
            # (his line rides the report row, which the turn's report draws;
            # on the morning's event too it was drawn twice — the census)
            world.log_event({"type": EVENT, "phase": "done", "marshal": man.name,
                             "nation": man.nation, "message": message})
            return {"marshal": man.name, "command": "HOLD", "order_status": "continues",
                    "action": "own_done", "message": message, "reason": message, "own": True,
                    **voice_keys}
    elif task == "pursue":
        quarry = world.get_marshal(str(spec.get("target") or ""))
        dead = (quarry is None or int(getattr(quarry, "strength", 0) or 0) <= 0
                or getattr(quarry, "captured_by", ""))
        if dead and int(spec.get("unseen", 0) or 0) == 0:
            # in France's sight to the last (the review, IC3-V: one destroyed
            # out of sight is "unseen" below, never known destroyed). Row IC,
            # Session 4b: in a war the chase done leaves him on his own with
            # no task — he makes war as he sees fit (at peace, done).
            if _at_war(world):
                return _freed(world, man, spec, f"{_shown(spec.get('target'))} is destroyed")
            return end(world, man, f"{_shown(spec.get('target'))} is destroyed — done", phase="done")
        if dead:
            quarry = None
        if quarry in (world.get_visible_enemies(man.nation) or []):
            spec["last_seen"] = quarry.location
            spec["unseen"] = 0
            ring = str(spec.get("ring") or "")
            d = _distance(world, ring, quarry.location) if ring else 0
            if d is not None and d > PURSUE_RING:
                ask_why(world, man, cause="ring", why=f"{_shown(quarry.name)} has left the ring of {PURSUE_RING} marches "
                                    f"around {_shown(ring)}")
        else:
            spec["unseen"] = int(spec.get("unseen", 0) or 0) + 1
            if spec["unseen"] >= UNSEEN_ASKS_AFTER:
                ask_why(world, man, cause="unseen",
                        why=f"{_shown(spec.get('target'))} has been out of sight {spec['unseen']} turns")
    elif task == "support":
        friend = world.get_marshal(str(spec.get("target") or ""))
        if friend is None or int(getattr(friend, "strength", 0) or 0) <= 0 \
                or getattr(friend, "captured_by", "") or friend.nation != man.nation:
            if _at_war(world):
                # Row IC, Session 4b: in a war he goes on by his own judgement
                return _freed(world, man, spec, f"{_shown(spec.get('target'))} has fallen")
            ask_why(world, man, f"{_shown(spec.get('target'))} has fallen; he holds where he stands")
    if _quiet_front(world, man, rec):
        ask_why(world, man, f"all has been quiet around {_shown(man.location)} for "
                            f"{QUIET_FRONT_ASKS} turns — he asks for a task with work in it")
        return None
    if spec.get("state") == "given":
        spec["state"] = "road"
    area = spec.get("area") or []
    if spec.get("state") in ("road", "work"):
        spec["state"] = "work" if (not area or here in area) else "road"
    return None


# ═══════════════════════════ what the screen says ═══════════════════════════

STATE_WORDS = {"given": "makes his first move at the start of next turn", "road": "on the road",
               "work": "at work", "asks": "asks for your word"}


def this_turn(world, marshal) -> str:
    """What he did at the start of THIS turn, as the morning told it — "" when
    he made no move of his own this turn (the user's "He moves at turn
    start": the card shows what he did, never what he will do)."""
    rec = _record_view(marshal)
    acts = [a for a in rec.get("acts") or [] if isinstance(a, (list, tuple)) and len(a) >= 3]
    if not acts or _int({"t": acts[-1][2]}, "t") != _turn(world):
        return ""
    return str(rec.get("said") or "")


def payload(world, marshal) -> Optional[Dict[str, Any]]:
    """His task as the client reads it (his card, the map, the Generals page)."""
    spec = own(marshal)
    if spec is None:
        return None
    n = needed(marshal, int(spec.get("risk", 0) or 0))
    question = spec.get("question") if isinstance(spec.get("question"), dict) else None
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
    given_now = _int(spec, "given") == _turn(world)
    asked = spec.get("state") == "asks" or question is not None
    return {
        **extra,
        "task": spec.get("task"), "target": spec.get("target"),
        "area": list(spec.get("area") or []), "words": task_words(spec),
        "state": spec.get("state"), "state_words": STATE_WORDS.get(spec.get("state"), ""),
        "asks": ((spec.get("asks") or {}).get("why", "") if spec.get("asks")
                 else (str(question.get("why") or "") if question else "")),
        # a question about his task does not stop him (Session 4b): he carries on
        "carries_on": question is not None and spec.get("state") != "asks",
        # Row IC, Session 4b — the user's "He moves at turn start": what he did
        # at the start of this turn ("" before his first move); no preview
        "this_turn": this_turn(world, marshal),
        "first_move_next": bool(given_now),
        # R-FRIENDS said on his card: the friend he would march to help
        "help": _friend_line(world, marshal),
        "odds": needed_words(n),
        "risk": int(spec.get("risk", 0) or 0),
        "stand_down": ("free — the actions it cost come back" if given_now
                       else ("free" if asked or _int(spec, "acted") < 0
                             else f"free, but {STAND_DOWN_TRUST} of his trust")),
        "count": count_words(world),
        "lines": len(list(getattr(marshal.strategic_order, "if_thens", None) or [])),
    }


def this_turn_rows(world) -> List[Dict[str, Any]]:
    """The desk's "This turn" rows: what each man on his own did as the turn
    opened (empty when nobody is on his own — the feature is inert unused),
    and the line of each man who follows him."""
    rows = []
    for man in men(world):
        line = this_turn(world, man)
        if not line:
            continue
        rows.append({"marshal": man.name, "shown": _shown(man.name),
                     "line": "This turn: " + line.rstrip(".") + "."})
    return rows


def morning_events(world) -> List[Dict[str, Any]]:
    """The turn's lines for its report and the morning dispatch — read from the
    event log, each told once."""
    out = []
    for event in getattr(world, "event_log", None) or []:
        if not isinstance(event, dict) or event.get("type") != EVENT or event.get("told"):
            continue
        event["told"] = True
        if event.get("phase") == "night":
            continue        # his move's own rows open the turn's report (`_their_own_turn`)
        out.append({"type": EVENT, "phase": str(event.get("phase") or ""),
                    "act": str(event.get("act") or ""), "marshal": event.get("marshal"),
                    "nation": event.get("nation"), "visible": bool(event.get("visible")),
                    "message": str(event.get("message") or ""),
                    **({"says": str(event["says"]), "speaker": str(event.get("speaker") or "")}
                       if event.get("says") else {})})
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
        # Row IC, Session 4b — the user's "He moves at turn start": he says
        # what he MEANS to do at the start of next turn, as an intention (the
        # enemy moves first), and what he did this turn if he has moved.
        if on_his_own(marshal):
            done = this_turn(world, marshal)
            ahead = read(world, marshal, preview=True)
            said = first_person(str(ahead.get("line") or ""), marshal)
            means = (f"At the start of next turn I mean to {said[2:] if said.startswith('I ') else said}"
                     if said else "")
            head = f"This turn: {first_person(done.rstrip('.'), marshal)}. " if done else ""
            return {"says": f"{head}{means}, if nothing changes first.".strip(),
                    "line": str(ahead.get("line") or "")}
        if nature in ("bold", "careful") and not why_not(world, marshal, replacing=True):
            prop = proposal(world, marshal)
            spec, _why = spec_from(world, marshal, prop["task"], prop["target"])
            reading = read(world, marshal, spec, preview=True) if spec else {}
            said = first_person(str(reading.get("line") or ""), marshal) if reading else ""
            tail = (f" — my first move, {said if said.startswith('I ') else said[:1].lower() + said[1:]}"
                    if said else "")
            return {"says": f"Set me on my own, Sire, and I would {task_words(spec or {'task': prop['task'], 'target': prop['target']})}{tail}.",
                    "proposal": prop["line"]}
        order = getattr(marshal, "strategic_order", None)
        if nature == "literal":
            # Row IC, Session 4 (IC-13): he repeats his orders back, or asks
            # for them — his own bank (PURE: an answer records nothing).
            written = (str(order.original_command or order.command_type).strip().rstrip(".") + "."
                       if order is not None else "")
            said = (_voice.voice(world, marshal, "repeat", orders=written) if written
                    else _voice.voice(world, marshal, "refusal"))
            if said:
                return {"says": said}
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
        reason = str(reading.get("why") or "not yet")
        return {"says": f"Not yet, Sire — {reason}."}
    if kind == "why":
        rec = _record_view(marshal)
        last = rec.get("said") or ""
        if not last:
            return {"says": ("I carried out your orders, Sire." if not on_his_own(marshal)
                             else "I have done nothing on my own yet, Sire.")}
        when = "This turn" if this_turn(world, marshal) else "Last time"
        return {"says": f"{when}: {first_person(last, marshal)}."}
    return {"says": _voice.voice(world, marshal, "idle")}
