"""Row IC, Session 2b (IC-9's second half) — THE TASK TO PROVE HIMSELF.

`docs/INDEPENDENT_COMMAND_SPEC.md` §6.11 (version 6, as the user ruled it in
Session 2b's Plan Mode, November 20, 2026). When a marshal's trust falls to 20
or less he asks for an audience. Where "Grant Autonomy" stood — three turns on
the ENEMY's decision logic, with its moods and dice, never shown beforehand —
the audience now offers **a task to prove himself**:

    HIS task, proposed by him, by his nature, read from what France can see:
      a bold man      takes the nearest enemy-held province within his reach
                      that he is not outnumbered at, then holds it (a hold
                      already makes a bold man strike a neighbour he outnumbers);
      a careful man   holds the province he stands in, and digs in;
      a literal man   holds where he stands; if outnumbered, falls back to his
                      nearest province of ours;
      nothing to take holds where he stands;
      and each of them helps the friend beside him: "if <friend> is attacked
      next to him, join his battle" (never a man he hates).
    It is given FREE, as an exact order (`backend/commands/if_thens.py`): a
    standing HOLD where he stands, a bold man's take riding it as the order's
    `opening_take`, run once by the strategic pass on the night it was
    announced for.
    He takes NO ORDERS until it ends — none at all: there is no call-back (the
    user's ruling, "No call-back").
    THREE TURNS — longer if he is ON A ROLL (the user's ruling, "He presses
    on"): a turn in which he won a battle and lost none. Read at the end of his
    last turn: one more turn, and again each turn he ends on a victory, SIX
    turns at most. A bold man on a roll goes for the next enemy province in
    his reach, announced in the morning before he moves.
    TODAY'S REWARDS, kept: spectacular (two battles won, or a defended place
    taken) +40 trust and +10 authority; good +25; none +15; poor +5.

What he achieved is read from his own record — `Marshal.battles_won` /
`battles_lost`, the counters the battle code keeps for every marshal whether
he attacks, defends or joins a friend's fight — against what it stood at when
the task was given; and one count of its own, the defended places he took
(`note_taken`, called where a province is captured after its defenders were
beaten). The old engine's scoring read result keys nothing ever wrote, so
"Grant Autonomy" always paid +15.

`proposal` is PURE: it writes nothing, casts no die and reads only what France
sees. ONE reader (`_reading`) serves the proposal, the roll's next place and
the night's last look before he marches — so what the window said is what he
does, or he stays put and says why.

No French marshal is ever moved by the enemy's decision logic
(`EnemyAI.decide_single_action` refuses a marshal of the player's nation).
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from backend.display_names import humanize_entity_name
from backend.errors import report

ARM = "trial"                   # the audience's arm
LEGACY_ARM = "grant_autonomy"   # the arm it replaced: an old save's standing question may name it
EVENT = "marshal_trial"         # the campaign log's and the dispatch's one event type
TURNS = 3                       # the task's own turns
MOST_TURNS = 6                  # with a roll: six in all, at most
SPECTACULAR_AUTHORITY = 10
# Today's rewards, kept (the bands the old three turns paid — §13).
REWARDS = {"spectacular": 40, "good": 25, "none": 15, "poor": 5}
# What the Emperor may still do FOR a man on his task: his pay and his title.
# Everything else that names him is an order, and he takes none.
_PASSES = frozenset({"grant_pension", "revoke_pension", "grant_dotation"})


# ═══════════════════════════ the state ══════════════════════════════════════

def on_trial(marshal) -> bool:
    """He is on a task to prove himself. THE one reader of the state — the
    executor's block, the audience's guard, the jealousy seams (IC-V3) and
    every surface ask it."""
    return isinstance(getattr(marshal, "trial", None), dict)


def _plural(count: int, word: str) -> str:
    return f"{int(count)} {word}{'' if int(count) == 1 else 's'}"


def achieved(marshal) -> Tuple[int, int, int]:
    """`(won, lost, taken)` since the task was given — his own battle record
    against what it stood at then, and the defended places he took."""
    state = getattr(marshal, "trial", None)
    if not isinstance(state, dict):
        return 0, 0, 0
    won = max(0, int(getattr(marshal, "battles_won", 0) or 0) - int(state.get("record_won", 0) or 0))
    lost = max(0, int(getattr(marshal, "battles_lost", 0) or 0) - int(state.get("record_lost", 0) or 0))
    return won, lost, max(0, int(state.get("taken", 0) or 0))


def on_a_roll(marshal) -> bool:
    """This turn he won at least one battle and lost none (no die: his record
    against what it stood at when the last turn closed)."""
    state = getattr(marshal, "trial", None)
    if not isinstance(state, dict):
        return False
    return (int(getattr(marshal, "battles_won", 0) or 0) > int(state.get("tick_won", 0) or 0)
            and int(getattr(marshal, "battles_lost", 0) or 0) <= int(state.get("tick_lost", 0) or 0))


def announced_take(marshal) -> str:
    """The place his task marches on as THIS turn ends, or "" — read from the
    order that will run it (`StrategicOrder.opening_take`), never from a copy:
    when a fall back, a retreat or the road home replaces his order the
    announcement goes with it, and no surface keeps promising a march (the
    review, IC2B-V7)."""
    if not on_trial(marshal):
        return ""
    order = getattr(marshal, "strategic_order", None)
    return str(getattr(order, "opening_take", None) or "") if order is not None else ""


def drop_take(marshal, why: str) -> Optional[Dict[str, Any]]:
    """The take his task announced for tonight is DROPPED — said once, in a
    report row, and never run a night late (he never marches on a place the
    morning did not announce for that night). None when nothing was
    announced."""
    state = getattr(marshal, "trial", None)
    if not isinstance(state, dict):
        return None
    order = getattr(marshal, "strategic_order", None)
    place = str((getattr(order, "opening_take", None) if order is not None else None)
                or state.get("next_take") or "")
    if order is not None and getattr(order, "opening_take", None):
        order.opening_take = None
    state["next_take"] = None
    if not place:
        return None
    message = (f"{humanize_entity_name(marshal.name)} does not march on "
               f"{humanize_entity_name(place)} tonight: {why}.")
    return {"marshal": marshal.name, "command": "HOLD", "order_status": "continues",
            "action": "trial_take_dropped", "reason": message, "message": message, "place": place}


def note_taken(marshal) -> None:
    """A defended place fell to him — called where a province is captured
    after its defenders were beaten (the attack's capture, a siege that
    followed a fight). Nothing for a man not on his task."""
    state = getattr(marshal, "trial", None)
    if isinstance(state, dict):
        state["taken"] = int(state.get("taken", 0) or 0) + 1


def note_walked_in(marshal) -> None:
    """A place fell to him that NOBODY defended. It proves nothing — `band`
    does not read it — but the morning says it (`_deeds`): the measure's own
    record read "In 3 turns he fought no battle" of a man who had freed the
    province he asked to free. Nothing for a man not on his task."""
    state = getattr(marshal, "trial", None)
    if isinstance(state, dict):
        state["walked_in"] = int(state.get("walked_in", 0) or 0) + 1


def band(won: int, lost: int, taken: int) -> Tuple[str, int]:
    """`(band, trust)` — the old three turns' own arithmetic, kept: spectacular
    is two battles won or a defended place taken; otherwise the score
    (2 a battle won, 3 a defended place, −2 a battle lost) says good, none or
    poor."""
    score = 2 * int(won) + 3 * int(taken) - 2 * int(lost)
    if int(won) >= 2 or int(taken) >= 1:
        name = "spectacular"
    elif score > 0:
        name = "good"
    elif score == 0:
        name = "none"
    else:
        name = "poor"
    return name, int(REWARDS[name])


def status_words(marshal) -> str:
    """What his card, the Generals screen and the ledger say of him."""
    state = getattr(marshal, "trial", None)
    if not isinstance(state, dict):
        return ""
    left = max(0, int(state.get("turns_left", 0) or 0))
    nxt = humanize_entity_name(announced_take(marshal))
    if int(state.get("rolls", 0) or 0) > 0:
        # (the review: "his task runs 1 more turn" read as one AFTER this
        # one, beside a refusal that said "1 turn left" of the same turn)
        tail = f": goes for {nxt} as this turn ends" if nxt else ""
        return f"On a roll with his task — {_plural(left, 'turn')} left{tail}"
    tail = f": marches on {nxt} as this turn ends" if nxt else ""
    return f"On a task to prove himself — {_plural(left, 'turn')} left{tail}"


def refusal_words(marshal) -> str:
    """Why an order to him is refused — one plain sentence."""
    state = getattr(marshal, "trial", None) or {}
    left = max(0, int(state.get("turns_left", 0) or 0))
    roll = (f" — up to {MOST_TURNS} in all while he keeps winning"
            if int(state.get("turns_done", 0) or 0) < MOST_TURNS - 1 else "")
    return (f"{humanize_entity_name(marshal.name)} is on his task to prove himself and takes no orders "
            f"until it ends ({_plural(left, 'turn')} left{roll}).")


def short_reason(marshal) -> str:
    """The same, short — a greyed button's hover, a list's row."""
    state = getattr(marshal, "trial", None) or {}
    left = max(0, int(state.get("turns_left", 0) or 0))
    return f"on his task to prove himself — he takes no orders ({_plural(left, 'turn')} left)"


def payload(marshal) -> Optional[Dict[str, Any]]:
    """The trial as the client reads it, or None."""
    state = getattr(marshal, "trial", None)
    if not isinstance(state, dict):
        return None
    won, lost, taken = achieved(marshal)
    return {
        "line": str(state.get("line") or ""),
        "task": str(state.get("task") or "hold"),
        "place": str(state.get("place") or ""),
        "turns_left": max(0, int(state.get("turns_left", 0) or 0)),
        "turns_done": max(0, int(state.get("turns_done", 0) or 0)),
        "most_turns": int(MOST_TURNS),
        "on_a_roll": int(state.get("rolls", 0) or 0) > 0,
        "next_take": announced_take(marshal),
        "won": int(won), "lost": int(lost), "taken": int(taken),
        "status": status_words(marshal),
        "reason": short_reason(marshal),
    }


# ═══════════════════════════ the proposal (PURE) ════════════════════════════

def _nature(marshal) -> str:
    return {"aggressive": "bold", "cautious": "careful", "literal": "literal"}.get(
        str(getattr(marshal, "personality", "") or ""), "")


def _unfit(world, marshal) -> str:
    """Why he cannot lead an attack now, or ""."""
    if getattr(marshal, "broken", False):
        return "his corps is broken"
    if int(getattr(marshal, "retreat_recovery", 0) or 0) > 0:
        return "his men are still rallying from a defeat"
    try:
        from backend.game_logic.fortunes_of_war import wound_refusal
        if wound_refusal(marshal, world, "attack"):
            return "he is wounded and cannot lead an attack"
    except Exception as exc:
        report(exc, "trial._unfit: fortunes_of_war.wound_refusal")
    return ""


OUTNUMBERED = "the enemy there outnumbers him, as far as France knows"


def _reading(world, marshal, name: str) -> Tuple[Optional[Dict[str, Any]], str]:
    """`(row, "")` when `name` is a place the enemy holds that he may go for,
    as France sees the board — a province of a court we are at war with, or
    ANY province an enemy army stands on (Mack in Bavaria's Swabia: he is
    driven out, the ground is not taken) — within his reach, and not held by
    a force France knows to outnumber him (§7: "attack means attack if not
    outnumbered"); else `(None, why)` in plain words. `row["ours_to_take"]`
    says whether the province itself would become ours. PURE; France's own
    sight only."""
    from backend.commands import ground
    from backend.commands import if_thens as _it
    here = str(getattr(marshal, "location", "") or "")
    region = world.get_region(name) if name else None
    if region is None:
        return None, "there is no such place"
    unfit = _unfit(world, marshal)
    if unfit:
        return None, unfit
    foe = ""
    if name == here:
        seen = ground.standing(world, marshal)
        code = str(seen.get("code") or "")
        ok = code in ("open", "garrison", "fort", "enemy_corps")
        foe = str(seen.get("foe") or "")
        distance = 0
        ours_to_take = ok
    else:
        if name not in _it.reach(world, marshal):
            return None, "it is out of his reach, or France no longer sees it"
        distance = world.get_distance(here, name)
        reach = max(1, int(getattr(marshal, "movement_range", 1) or 1))
        if distance is None or int(distance) < 0 or int(distance) > reach:
            return None, "it is out of his reach"
        seen = ground.entering(world, marshal, name)
        code = str(seen.get("code") or "")
        ok = code in ("garrison", "garrison_unsure", "fort", "takes", "takes_if_open",
                      "liberates", "enemy_corps")
        # an enemy army on ground that is not the enemy's: he is driven out
        ours_to_take = ok and not (code == "enemy_corps" and seen.get("takes") is None)
    if not ok:
        if code in ("ours", "nobody", "not_at_war", "peace_passage"):
            # ours, nobody's, or a court's we are not at war with — and no
            # enemy army stands on it (that would have read `enemy_corps`)
            return None, "no enemy holds it any longer"
        if code == "besieging":
            return None, "he is besieging it already"
        return None, str(seen.get("line") or "it cannot be taken")
    defenders, strongest = 0, None
    for enemy, where in _it.seen_enemies(world, marshal):
        if where != name:
            continue
        known = _it.known_strength(world, enemy)
        defenders += known
        if strongest is None or int(enemy.strength) > int(strongest.strength):
            strongest = enemy
    if strongest is not None:
        foe = strongest.name
        # the executor's own refusal of a field on peace soil (an enemy
        # sheltering on a neutral's ground is not to be attacked there)
        try:
            from backend.commands.order_quotes import _peace_soil_refusal_line
            if _peace_soil_refusal_line(world, marshal, strongest):
                return None, "the enemy there shelters on neutral ground"
        except Exception as exc:
            report(exc, "trial._reading: _peace_soil_refusal_line")
    elif code == "enemy_corps" and not foe:
        return None, "the enemy there is out of France's sight"
    garrison = 0
    if code == "garrison":
        try:
            from backend.game_logic.garrison_report import garrison_view
            form, value = garrison_view(world, name, world.player_nation)
            garrison = int(value) if form == "exact" else 0
        except Exception as exc:
            report(exc, "trial._reading: garrison_view")
    row = {"place": name, "distance": int(distance), "defenders": int(defenders + garrison),
           "garrison": int(garrison), "foe": foe, "code": code,
           "ours_to_take": bool(ours_to_take), "frees_for": _frees_for(world, marshal, name)}
    if defenders + garrison > int(getattr(marshal, "strength", 0) or 0):
        return None, OUTNUMBERED
    return row, ""


def _frees_for(world, marshal, place: str) -> str:
    """The ally or client whose ground `place` is — the court a capture by
    his nation hands it back to (`world_state.liberates_ally_ground`, the
    game's own rule) — or "". The measure's own find: on most boards Bavaria's
    Swabia is in Austria's hands by the fourth turn, and "take Swabia and hold
    it" promised a province the game then gives back to Bavaria."""
    try:
        from backend.models import world_state as _ws
        return str(_ws.liberates_ally_ground(world, place, marshal.nation) or "")
    except Exception as exc:
        report(exc, "trial._frees_for: liberates_ally_ground")
        return ""


def _court(nation: str) -> str:
    from backend.display_names import display_nation
    return str(display_nation(nation))


def _too_strong(world, marshal) -> str:
    """The enemy within his reach that he will NOT go for because France
    knows him to be the stronger — "Mack, at Swabia" — or "" (for the words
    of a bold man who proposes only to hold). PURE."""
    from backend.commands import if_thens as _it
    names = [str(getattr(marshal, "location", "") or "")]
    for name in _it.reach(world, marshal):
        if name not in names:
            names.append(name)
    for name in names:
        row, why = _reading(world, marshal, name)
        if row is None and why == OUTNUMBERED:
            strongest = None
            for enemy, where in _it.seen_enemies(world, marshal):
                if where == name and (strongest is None
                                      or int(enemy.strength) > int(strongest.strength)):
                    strongest = enemy
            place = humanize_entity_name(name)
            return (f"{humanize_entity_name(strongest.name)}, at {place}" if strongest is not None
                    else f"the garrison of {place}")
    return ""


def why_not(world, marshal, place: str) -> str:
    """Why he will not march on `place` tonight, or "" (the night's last look
    — `_reading`, the proposal's own reader)."""
    try:
        _row, why = _reading(world, marshal, str(place or ""))
    except Exception as exc:
        report(exc, "trial.why_not: _reading")
        return "the ground could not be read"
    return why


def _place_to_take(world, marshal) -> Optional[Dict[str, Any]]:
    """The nearest enemy-held place within his reach that he may take — then
    the one with the fewest known defenders, then by name. None when there is
    none. PURE."""
    from backend.commands import if_thens as _it
    names = [str(getattr(marshal, "location", "") or "")]
    for name in _it.reach(world, marshal):
        if name not in names:
            names.append(name)
    rows = []
    for name in names:
        row, _why = _reading(world, marshal, name)
        if row is not None:
            rows.append(row)
    rows.sort(key=lambda r: (r["distance"], r["defenders"], r["place"]))
    return rows[0] if rows else None


def _friend_to_help(world, marshal) -> str:
    """The friend whose battle he would march to — one of our own corps in a
    province NEXT to his (a corps in his own province fights beside him
    without being told), the WEAKEST first — the man who most needs him —
    then by name; never a man he hates (the game's own line for a corps that
    will not fight beside another: a relationship of −2). "" when no friend
    stands next to him."""
    here = world.get_region(marshal.location)
    near = set(getattr(here, "adjacent_regions", ()) or ()) - {marshal.location}
    rows = []
    for other in world.get_player_marshals():
        if other.name == marshal.name or int(getattr(other, "strength", 0) or 0) <= 0:
            continue
        if getattr(other, "captured_by", "") or other.location not in near:
            continue
        try:
            if int(marshal.get_relationship(other.name)) <= -2:
                continue
        except Exception as exc:
            report(exc, "trial._friend_to_help: get_relationship")
        rows.append((int(other.strength), other.name))
    return sorted(rows)[0][1] if rows else ""


def _lines(world, marshal, nature: str) -> List[Dict[str, Any]]:
    """The if-thens his task carries, as the exact-order rules take them
    (`if_thens.settle`): a literal man's fall back, and the friend's line —
    one line for a bold or a careful man, so his is the friend's."""
    from backend.commands import if_thens as _it
    from backend.commands import task_presets as _presets
    asked = []
    if nature == "literal":
        back = _presets._safe_ground(world, marshal)
        if back:
            asked.append(_it.make_line("outnumbered", then="fall_back", to=back))
    friend = _friend_to_help(world, marshal)
    if friend:
        asked.append(_it.make_line("friend_attacked", friend=friend, then="join"))
    kept, _refused = _it.settle(world, marshal, "HOLD", asked)
    return kept


def _odds_words(world, marshal, foe: str) -> str:
    """" (large force to his 24,000)" — the enemy as France knows him, against
    his own corps; "" where France has no reading."""
    label = ""
    try:
        from backend.commands.combat_executor import CombatExecutor
        label = str(CombatExecutor._fog_banded_strength(world.get_marshal(foe), world))
    except Exception as exc:
        report(exc, "trial._odds_words: _fog_banded_strength")
    own = int(getattr(marshal, "strength", 0) or 0)
    if not label or label == "strength unknown":
        return ""
    # (the review: "(large force to his 24,000)" — what does "to his" mean?)
    known = label if label[:1].isdigit() else f"a {label}"
    return f" ({known}, against his {own:,} men)"


def _take_words(world, marshal, take: Dict[str, Any]) -> str:
    """What he asks to do about the place he goes for — "take Tyrol, where
    Archduke John stands (…)" or, on ground that is not the enemy's, "drive
    Mack out of Swabia (…)" — as far as France sees it."""
    place = humanize_entity_name(take["place"])
    code = take.get("code")
    foe = str(take.get("foe") or "")
    # where he sets out from (the blind reading: "the screen did not tell me
    # where Ney is now") — unless the place is the one he stands in
    here = str(getattr(marshal, "location", "") or "")
    march = f"march from {humanize_entity_name(here)} and " if here and here != take["place"] else ""
    if foe and not take.get("ours_to_take", True):
        return (f"{march}drive {humanize_entity_name(foe)} out of {place}"
                f"{_odds_words(world, marshal, foe)}")
    # an ally's ground in the enemy's hands is FREED for that ally, not kept
    frees = str(take.get("frees_for") or "")
    takes = f"free {place} for {_court(frees)}" if frees else f"take {place}"
    if foe:
        return (f"{march}{takes}, where {humanize_entity_name(foe)} stands"
                f"{_odds_words(world, marshal, foe)}")
    if code == "garrison":
        return f"{march}{takes}, which a garrison of {int(take.get('garrison', 0)):,} holds"
    if code == "garrison_unsure":
        return f"{march}{takes}, where a garrison stands"
    if code == "fort":
        return f"{march}{takes}, which is fortified — he will have to besiege it"
    return f"{march}{takes}, where France sees no defenders"


def terms_words() -> str:
    """The trial's terms — the same for every man. On the audience's window
    behind his own proposal.

    Worded by the blind readings (nine readers over three rounds,
    `docs/audits/ic_client/session2b/README.md`): which turns the three are,
    that he is then back in hand, that six is the total and counts the first
    three, what "a victory" on his last turn is (a battle won and no BATTLE
    lost — "loses none" read as men to two readers), and what the trust comes
    to — the four amounts, each with what earns it (`band`'s own arithmetic,
    said in words: pinned against it in `tests/test_ic9b_the_trial.py`)."""
    more = {1: "one", 2: "two", 3: "three"}.get(TURNS - 1, str(TURNS - 1))
    return (f"He carries this out by himself for {TURNS} turns — this one and the next {more} — "
            f"then he is under your orders again. Until then he takes no orders, and you cannot "
            f"call him back. If he wins a battle on his last turn and loses no battle that turn, "
            f"his task runs one turn longer, and so on — up to {MOST_TURNS} turns in all, the first "
            f"{TURNS} included. When his task ends, his trust in you rises by the first of these "
            f"that is true: {REWARDS['spectacular']} (and your authority by "
            f"{SPECTACULAR_AUTHORITY}) if he won two battles or took a defended place; "
            f"{REWARDS['good']} if he won more battles than he lost; {REWARDS['none']} if he fought "
            f"none or won as many as he lost; {REWARDS['poor']} if he lost more than he won.")


def proposal(world, marshal) -> Dict[str, Any]:
    """HIS proposal — PURE (no write, no die, France's own sight). With no
    world to read (`world` None) he proposes to hold where he stands.

    `line` is the order as one sentence (the order's own words; what the
    answer is checked against); `description` is the proposal in full, in
    plain words, for the audience's window."""
    from backend.commands import if_thens as _it
    shown = humanize_entity_name(marshal.name)
    here = str(getattr(marshal, "location", "") or "")
    here_shown = humanize_entity_name(here) if here else "where he stands"
    nature = _nature(marshal)
    take, lines, too_strong = None, [], ""
    if world is not None and here:
        try:
            if nature == "bold":
                take = _place_to_take(world, marshal)
                if take is None:
                    too_strong = _too_strong(world, marshal)
            lines = _lines(world, marshal, nature)
        except Exception as exc:
            report(exc, "trial.proposal: reading the board")
            take, lines, too_strong = None, [], ""
    task = "take" if take else "hold"
    place = take["place"] if take else here
    place_shown = humanize_entity_name(place) if place else "where he stands"
    drives_out = bool(take and take.get("foe") and not take.get("ours_to_take", True))

    if drives_out:
        line = f"{shown}, drive {humanize_entity_name(take['foe'])} out of {place_shown} and hold there."
    elif task == "take" and take.get("frees_for"):
        line = f"{shown}, free {place_shown} for {_court(str(take['frees_for']))} and hold it."
    elif task == "take":
        line = f"{shown}, take {place_shown} and hold it."
    else:
        line = f"{shown}, hold {place_shown}."
    doing = line[len(shown) + 2:].rstrip(".")      # "free Swabia for Bavaria and hold it"
    for row in lines:
        line += " " + _it.sentence(row)

    if nature == "bold":
        strike = "striking any enemy next to him that he outnumbers"
        if take:
            then = "and then to hold where he ends" if drives_out else "and then to hold it"
            words = (f"{shown} is a bold man, so he asks to "
                     f"{_take_words(world, marshal, take)} — {then}, {strike}.")
        elif too_strong:
            words = (f"{shown} is a bold man, but the enemy within his reach — {too_strong} — is "
                     f"too strong for his corps alone: he asks to hold {here_shown}, where he "
                     f"stands, {strike}.")
        else:
            words = (f"{shown} is a bold man, but France sees no enemy within his reach: he asks "
                     f"to hold {here_shown}, where he stands, {strike}.")
    elif nature == "careful":
        words = (f"{shown} is a careful man, so he asks to hold {here_shown}, where he stands, "
                 f"and to dig in.")
    elif nature == "literal":
        words = (f"{shown} follows orders to the letter, so he asks for exact orders: to hold "
                 f"{here_shown}, where he stands.")
    else:
        words = f"{shown} asks to hold {here_shown}, where he stands."
    for row in lines:
        if row.get("if") == "outnumbered":
            words += f" If he is outnumbered, he falls back to {humanize_entity_name(str(row.get('to') or ''))}."
        elif row.get("if") == "friend_attacked":
            words += (f" If {humanize_entity_name(str(row.get('friend') or ''))} is attacked next to "
                      f"him, he marches to join that battle.")
    return {
        "marshal": marshal.name, "shown": shown, "nature": nature,
        "task": task, "place": place, "from": here,
        "foe": str((take or {}).get("foe") or ""),
        "if_thens": [dict(row) for row in lines],
        "line": line,
        "doing": doing,
        "words": words,
        # two paragraphs on the window: what HE asks, then the terms
        "description": f"{words}\n{terms_words()}",
        "turns": int(TURNS), "most_turns": int(MOST_TURNS),
    }


def option(world, marshal) -> Dict[str, Any]:
    """The audience's arm — always offered (the last field marshal too)."""
    read = proposal(world, marshal)
    return {
        "id": ARM,
        "text": f"Give {read['shown']} a task to prove himself",
        "description": read["description"],
        "effect": "a_task_to_prove_himself",
        "proposal": {key: read[key] for key in
                     ("nature", "task", "place", "from", "line", "words", "turns", "most_turns")},
    }


def refresh(world, event):
    """A standing audience's arm made current — the proposal is read again
    whenever the question goes to the player (the rente arm is re-priced at
    the same reads), and an old save's `grant_autonomy` arm becomes the task.
    Returns the event (changed in place)."""
    if not isinstance(event, dict) or world is None:
        return event
    options = event.get("options")
    if not isinstance(options, list):
        return event
    getter = getattr(world, "get_marshal", None)
    marshal = getter(str(event.get("marshal") or "")) if callable(getter) else None
    if marshal is None:
        return event
    fresh = None
    out = []
    for item in options:
        if isinstance(item, dict) and item.get("id") in (ARM, LEGACY_ARM):
            if fresh is None:
                fresh = option(world, marshal)
            out.append(fresh)
        else:
            out.append(item)
    event["options"] = out
    return event


def shown_line(event) -> Optional[str]:
    """The proposal the standing question last showed, or None (an old
    save's arm, which showed none)."""
    for item in (event or {}).get("options") or []:
        if isinstance(item, dict) and item.get("id") == ARM:
            line = (item.get("proposal") or {}).get("line")
            return str(line) if line else None
    return None


# ═══════════════════════════ giving it ══════════════════════════════════════

def give(world, marshal, shown: Optional[str] = None) -> Dict[str, Any]:
    """Give him his task — FREE, as an exact order. `shown` is the proposal
    the audience last showed: when the board has changed under it, NOTHING is
    given and the fresh proposal is returned (`stale`) so the window can show
    it — what was shown is what is given."""
    from backend.commands.strategic import clear_order_bound_interrupt
    from backend.models.marshal import StrategicOrder
    read = proposal(world, marshal)
    if shown is not None and str(shown) != read["line"]:
        return {"given": False, "stale": True, "proposal": read,
                "message": (f"The board has changed since {read['shown']} made his proposal — "
                            f"nothing is given yet. He now proposes: {read['words']}")}
    turn = int(world.current_turn)
    here = read["from"]
    lines = [{**dict(row), "used": False, "written": turn} for row in read["if_thens"]]
    marshal.strategic_order = StrategicOrder(
        command_type="HOLD", target=here, target_type="region",
        started_turn=turn, issued_turn=turn, original_command=read["line"],
        if_thens=lines,
        opening_take=(read["place"] if read["task"] == "take" else None))
    literal = getattr(marshal, "personality", "") == "literal"
    marshal.holding_position = bool(literal)
    marshal.hold_region = here if literal else ""
    clear_order_bound_interrupt(marshal)
    _drop_his_objection(world, marshal)
    if hasattr(marshal, "jealousy_autonomous_warned"):
        marshal.jealousy_autonomous_warned = False      # a man on his task makes no strike
    won = int(getattr(marshal, "battles_won", 0) or 0)
    lost = int(getattr(marshal, "battles_lost", 0) or 0)
    marshal.trial = {
        "line": read["line"], "words": read["words"],
        "task": read["task"], "place": read["place"],
        "turns_left": int(TURNS), "turns_done": 0, "rolls": 0, "given": turn,
        "record_won": won, "record_lost": lost, "tick_won": won, "tick_lost": lost,
        "taken": 0,
        "next_take": (read["place"] if read["task"] == "take" else None),
    }
    # What he WILL do, in the order's own words (the window said why).
    marches = (f" He marches on {humanize_entity_name(read['place'])} as this turn ends."
               if read["task"] == "take" else "")
    message = (f"{read['shown']} has his task to prove himself: \"{read['line']}\"{marches} "
               f"He takes no orders until it ends — {TURNS} turns, or up to {MOST_TURNS} while he "
               f"keeps winning.")
    world.log_event({
        "type": EVENT, "phase": "given", "marshal": marshal.name,
        "nation": marshal.nation, "task": read["task"], "place": read["place"],
        "doing": read["doing"],
        "message": message,
    })
    return {"given": True, "stale": False, "proposal": read, "message": message}


def _drop_his_objection(world, marshal) -> None:
    """An objection of his that still waits for the Emperor's answer is
    dropped with the order it was about: he takes none now, and "proceed" on
    it would have carried that order out for a man on his task (the review,
    IC2B-V5 — the road after an objection sits below the executor's refusal;
    it refuses too: `meta_executor._execute_post_objection`)."""
    for field in ("pending_objection", "pending_strategic_objection"):
        standing = getattr(world, field, None)
        if not isinstance(standing, dict):
            continue
        named = str(standing.get("marshal") or standing.get("marshal_name") or "")
        if named == marshal.name:
            setattr(world, field, None)


# ═══════════════════════════ no orders ══════════════════════════════════════

def order_refusal(world, command, action) -> Optional[Dict[str, Any]]:
    """An order to a man on his task is refused, free — EVERY order, the one
    that would cancel his standing order too (the user's ruling: no
    call-back). The Emperor's own acts FOR him pass (his pension, his title),
    and so does anything that is no order (a question, the turn's end).
    None when the command may go on."""
    if not isinstance(command, dict) or world is None:
        return None
    name = command.get("marshal")
    if not name:
        return None
    marshal = world.get_marshal(str(name))
    if (marshal is None or not on_trial(marshal)
            or marshal.nation != getattr(world, "player_nation", None)):
        return None
    from backend.ai.validation import NON_ORDER_ACTIONS
    if action is None or action in NON_ORDER_ACTIONS or action in _PASSES or action == "unknown":
        return None
    return {"success": False, "message": refusal_words(marshal), "no_action_cost": True,
            "trial": payload(marshal)}


# ═══════════════════════════ the night ══════════════════════════════════════

def run_take(executor, marshal, order, world, game_state) -> Dict[str, Any]:
    """The take his task announced for tonight — run ONCE by the strategic
    pass, at no cost, the way a fired if-then attacks (`_fire_if_then`): a
    dug-in man leaves his works, `attack <place>` goes through the executor
    as the game's own carrying-out, and the battle rides the report row. The
    hold then stands where he ends. When it can no longer be carried out as
    it was announced — the last look is `_reading`, the proposal's own
    reader — he holds where he stands and the row says why; he never picks
    another place unannounced."""
    from backend.commands.strategic import (
        _combat_carry, attack_was_refused, refusal_keys, refusal_reason)
    place = str(getattr(order, "opening_take", "") or "")
    order.opening_take = None
    state = getattr(marshal, "trial", None)
    if isinstance(state, dict):
        state["next_take"] = None
    shown = humanize_entity_name(marshal.name)
    place_shown = humanize_entity_name(place)

    def _row(message: str, action: str = "trial_take", **extra) -> Dict[str, Any]:
        row = {"marshal": marshal.name, "command": "HOLD", "order_status": "continues",
               "action": action, "reason": message, "message": message, "place": place}
        row.update(extra)
        return row

    stands = humanize_entity_name(str(marshal.location or ""))
    if getattr(marshal, "reinforced_this_turn", False):
        return _row(f"{shown} answered a friend's guns this turn, so he does not march on "
                    f"{place_shown} as well. He holds {stands}.", action="trial_take_dropped")
    why = why_not(world, marshal, place)
    if why:
        return _row(f"{shown} does not march on {place_shown}: {why}. He holds {stands}.",
                    action="trial_take_dropped")
    frees = _frees_for(world, marshal, place)      # read BEFORE the capture moves the holder
    leaves = ""
    if getattr(marshal, "fortified", False):
        executor.execute({"command": {"marshal": marshal.name, "action": "unfortify",
                                      "_strategic_execution": True}}, game_state)
        leaves = "leaves his works and "
    result = executor.execute(
        {"command": {"marshal": marshal.name, "action": "attack", "target": place,
                     "_strategic_execution": True}}, game_state)
    if attack_was_refused(result):
        # (the review: he HAS left his works by now — say so, not "he holds")
        left_them = "left his works but " if leaves else ""
        return _row(f"{shown} {left_them}could not march on {place_shown}: "
                    f"{refusal_reason(result)} He stands at "
                    f"{humanize_entity_name(str(marshal.location or ''))}.",
                    action="trial_take_refused", **refusal_keys(result))
    where = str(marshal.location or "")
    if marshal.strategic_order is order:
        # he may have advanced with the victory: the hold is of the ground he
        # now stands on
        order.target = where
        if getattr(marshal, "hold_region", ""):
            marshal.hold_region = where
    region = world.get_region(place)
    holder = getattr(region, "controller", None) if region is not None else None
    if holder == marshal.nation:
        tail = f" {place_shown} is ours."
    elif frees and holder == frees:
        tail = f" {place_shown} is {_court(frees)}'s again."
    else:
        tail = ""
    return _row(f"{shown} {leaves}marches on {place_shown}, as he proposed.{tail}",
                target=place, **_combat_carry(result))


def keep_the_hold(world, marshal) -> bool:
    """His hold is put back where he stands when it ended before his task did
    (his one line fired, a retreat cleared it, a colleague's battle consumed
    it): he is never without his order while he is on his task. True when a
    hold was put back."""
    if not on_trial(marshal) or int(getattr(marshal, "strength", 0) or 0) <= 0:
        return False
    if getattr(marshal, "captured_by", "") or not getattr(marshal, "location", None):
        return False
    if getattr(marshal, "strategic_order", None) is not None:
        return False
    from backend.commands.strategic import install_arrival_hold
    install_arrival_hold(marshal, world, str(marshal.trial.get("line") or ""), carried=[])
    return True


def _quiet_his_questions(marshal, reports: List[Dict[str, Any]]) -> None:
    """He takes no orders, so his standing order asks the Emperor nothing: a
    question it raised (a road blocked on his fall back) is dropped with the
    order that raised it, and its row says he holds. The grave questions that
    belong to no order (a last stand) are never touched."""
    from backend.commands.strategic import ORDER_BOUND_INTERRUPT_TYPES, clear_order_bound_interrupt
    cleared = clear_order_bound_interrupt(marshal)
    stands = humanize_entity_name(str(marshal.location or ""))
    for row in reports or []:
        if not isinstance(row, dict) or row.get("marshal") != marshal.name:
            continue
        if not row.get("requires_input"):
            continue
        kind = str(row.get("interrupt_type") or row.get("interrupt") or "")
        if kind and kind not in ORDER_BOUND_INTERRUPT_TYPES:
            continue
        for key in ("requires_input", "options", "pending_interrupt", "interrupt_type", "interrupt"):
            row.pop(key, None)
        row["order_status"] = "continues"
        row["action"] = "trial_holds"
        row["message"] = (f"{humanize_entity_name(marshal.name)} keeps to his task: "
                          f"he holds {stands}.")
        cleared = True
    if cleared and getattr(marshal, "strategic_order", None) is not None \
            and getattr(marshal.strategic_order, "command_type", "") != "HOLD":
        # the march that asked is over: he holds (`keep_the_hold`, below). The
        # order ends WITH its question (NPC-2's rule, at the seam itself).
        marshal.strategic_order = None
        clear_order_bound_interrupt(marshal)


def _men(world) -> List[Any]:
    nation = getattr(world, "player_nation", None)
    return sorted((m for m in (getattr(world, "marshals", None) or {}).values()
                   if on_trial(m) and m.nation == nation), key=lambda m: m.name)


def _deeds(won: int, lost: int, taken: int, turns: int, walked_in: int = 0) -> str:
    """What he did, in one sentence. A place nobody defended is SAID (he did
    take it) though it earns nothing — the terms say only a defended place
    counts, so the player can see why his trust rose by what it did."""
    parts = []
    if won:
        parts.append(f"won {_plural(won, 'battle')}")
    if lost:
        parts.append(f"lost {_plural(lost, 'battle')}")
    if taken:
        parts.append(f"took {_plural(taken, 'defended place')}")
    if walked_in:
        parts.append(f"took {_plural(walked_in, 'place')} that nobody defended")
    span = f"In {_plural(turns, 'turn')} he " if turns > 0 else "He "
    if not parts:
        return f"{span}fought no battle."
    if not (won or lost or taken):
        # only an undefended place: say plainly that no battle was fought
        return f"{span}fought no battle; he {parts[0]}."
    said = parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " and " + parts[-1]
    return f"{span}{said}."


def _settle_words(shown: str, name: str, deeds: str, gain: int, trust: int, authority: int) -> str:
    opening = {
        "spectacular": f"{shown} has proved himself.",
        "good": f"{shown} did well on his task.",
        "none": f"{shown}'s task is over with little to show for it.",
        "poor": f"{shown} did badly on his task.",
    }[name]
    moved = (f"His trust in you rises by {int(gain)} (to {int(trust)})" if gain > 0
             else f"His trust in you stands at {int(trust)}")
    if authority > 0:
        moved += f", and your authority by {int(authority)}"
    return f"{opening} {deeds} {moved}. He is under your orders again."


def _reward(world, marshal, won: int, lost: int, taken: int) -> Tuple[str, int, int]:
    """Apply the band: `(band, trust gained, authority gained)`."""
    name, gain = band(won, lost, taken)
    applied = int(marshal.modify_trust(int(gain)) or 0)
    authority = 0
    if name == "spectacular":
        try:
            from backend.game_logic import standing as _standing
            authority = int(_standing.move(world, marshal.nation, SPECTACULAR_AUTHORITY,
                                           "spectacular_return", party=marshal.name,
                                           marshal=marshal.name) or 0)
        except Exception as exc:
            report(exc, "trial._reward: standing.move")
    return name, applied, authority


def settle(world, marshal) -> Dict[str, Any]:
    """His task is over: today's rewards by what he achieved, his order
    ended, the morning's line. The report row."""
    from backend.commands.strategic import clear_order_bound_interrupt
    state = marshal.trial if isinstance(getattr(marshal, "trial", None), dict) else {}
    won, lost, taken = achieved(marshal)
    turns = int(state.get("turns_done", 0) or 0)
    walked_in = max(0, int(state.get("walked_in", 0) or 0))
    name, gain, authority = _reward(world, marshal, won, lost, taken)
    marshal.trial = None
    marshal.strategic_order = None
    marshal.holding_position = False
    marshal.hold_region = ""
    clear_order_bound_interrupt(marshal)
    shown = humanize_entity_name(marshal.name)
    message = _settle_words(shown, name, _deeds(won, lost, taken, turns, walked_in), gain,
                            int(marshal.trust.value), authority)
    world.log_event({
        "type": EVENT, "phase": "ended", "marshal": marshal.name, "nation": marshal.nation,
        "band": name, "trust_gain": int(gain), "authority_gain": int(authority),
        "won": int(won), "lost": int(lost), "taken": int(taken), "turns": int(turns),
        "walked_in": int(walked_in),
        "message": message,
    })
    return {"marshal": marshal.name, "command": "HOLD", "order_status": "completed",
            "action": "trial_ended", "band": name, "reason": message, "message": message,
            "trust_gain": int(gain), "authority_gain": int(authority)}


def _press_on(world, marshal) -> Dict[str, Any]:
    """He ended his last turn on a victory: one more turn. A bold man's next
    place is read now — by the proposal's own reader — and announced; it is
    run as this coming turn ends."""
    state = marshal.trial
    state["turns_left"] = 1
    state["rolls"] = int(state.get("rolls", 0) or 0) + 1
    shown = humanize_entity_name(marshal.name)
    order = getattr(marshal, "strategic_order", None)
    nxt = None
    if _nature(marshal) == "bold" and order is not None and order.command_type == "HOLD":
        try:
            pick = _place_to_take(world, marshal)
        except Exception as exc:
            report(exc, "trial._press_on: _place_to_take")
            pick = None
        if pick is not None:
            nxt = pick["place"]
            order.opening_take = nxt
    state["next_take"] = nxt
    stands = humanize_entity_name(str(marshal.location or ""))
    doing = (f"goes for {humanize_entity_name(nxt)} as this turn ends" if nxt
             else f"holds {stands}")
    most = max(0, int(MOST_TURNS) - int(state.get("turns_done", 0) or 0))
    # Told in the MORNING of the turn it announces: "last turn" is the one
    # that just closed, "this turn" the one now open (the review: "this turn"
    # stood for both in one sentence).
    message = (f"{shown} is on a roll — last turn he won a battle and lost none. He presses on "
               f"with his task one more turn and {doing}. He still takes no orders; he comes "
               f"back to you when a turn ends without a victory, in {_plural(most, 'turn')} at most.")
    world.log_event({
        "type": EVENT, "phase": "roll", "marshal": marshal.name, "nation": marshal.nation,
        "place": nxt or "", "message": message,
    })
    return {"marshal": marshal.name, "command": "HOLD", "order_status": "continues",
            "action": "trial_roll", "reason": message, "message": message, "place": nxt or ""}


def _fallen(world, marshal) -> Dict[str, Any]:
    """His task ended with him — destroyed or taken; nothing to settle."""
    marshal.trial = None
    shown = humanize_entity_name(marshal.name)
    message = f"{shown}'s task to prove himself ended with his corps."
    world.log_event({
        "type": EVENT, "phase": "ended", "marshal": marshal.name, "nation": marshal.nation,
        "band": "", "trust_gain": 0, "authority_gain": 0, "message": message,
    })
    return {"marshal": marshal.name, "command": "", "order_status": "completed",
            "action": "trial_ended", "band": "", "reason": message, "message": message}


def tick(world) -> List[Dict[str, Any]]:
    """The nightly count of every man on his task — after the enemy has moved
    and the standing orders have been carried out. His last turn: on a roll
    and under six turns → one more turn (`_press_on`); otherwise the task is
    settled. Returns one row for each man who pressed on or whose task ended
    (for the caller that wants them; the same words are in the event log,
    which is what the morning reads)."""
    rows = []
    for marshal in _men(world):
        state = marshal.trial
        if int(getattr(marshal, "strength", 0) or 0) <= 0 or getattr(marshal, "captured_by", ""):
            rows.append(_fallen(world, marshal))
            continue
        state["turns_done"] = int(state.get("turns_done", 0) or 0) + 1
        state["turns_left"] = int(state.get("turns_left", 0) or 0) - 1
        rolling = on_a_roll(marshal)
        state["tick_won"] = int(getattr(marshal, "battles_won", 0) or 0)
        state["tick_lost"] = int(getattr(marshal, "battles_lost", 0) or 0)
        if state["turns_left"] > 0:
            continue
        if rolling and state["turns_done"] < MOST_TURNS:
            rows.append(_press_on(world, marshal))
        else:
            rows.append(settle(world, marshal))
    return rows


def close_of_turn(world, reports: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """The turn's close for the men on their task — called by the turn
    manager right after the standing-order pass, once per End Turn: their
    questions quieted, a hold that ended early put back, the nightly count.
    Returns the strategic reports (a quieted question's row re-worded).

    The COUNT's own lines — he presses on, his task is over and how he did —
    are NOT added to the strategic rows: they are the morning's, told once
    by `morning_events` (the turn's events and the dispatch read them from
    the event log). A row here as well would print the same sentence twice
    in the turn's report.

    WHY THERE: after his standing order has been carried out (so this turn's
    battles are on his record) and BEFORE the advance (so the morning's
    report carries how he did). It is guarded with the pass it follows — once
    an End Turn, never on a resumed close, never after the Fall (the turn
    manager re-reads the Fall AFTER the standing-order pass, because the
    Emperor can fall in his own standing order, and only then counts). It stands
    where the old autonomous-marshals pass stood in the turn's order of
    work, except that that pass ran AFTER the advance and moved a French
    marshal by the ENEMY's decision logic; this one moves nobody."""
    reports = list(reports or [])
    # A man who is another crown's now (a defector, a corps handed to a
    # client) has no task of ours: nothing would ever settle it (the review).
    nation = getattr(world, "player_nation", None)
    for marshal in (getattr(world, "marshals", None) or {}).values():
        if on_trial(marshal) and marshal.nation != nation:
            marshal.trial = None
    men = _men(world)
    if not men:
        return reports
    for marshal in men:
        try:
            _quiet_his_questions(marshal, reports)
            keep_the_hold(world, marshal)
        except Exception as exc:
            report(exc, "trial.close_of_turn: keeping the hold")
    try:
        tick(world)
    except Exception as exc:
        report(exc, "trial.close_of_turn: tick")
    return reports


def morning_events(world) -> List[Dict[str, Any]]:
    """The lines the MORNING tells of the men on their task — he pressed on,
    his task ended (and how he did), an old save's man was settled on loading
    — as turn events for the end-turn report and the morning dispatch
    (`dispatch._DISPATCH_EVENT_TYPES` carries the type). Read from the event
    log, where `log_event` wrote them, and each told ONCE (`told` is set on
    the logged row, which the save carries — so a line written at a load is
    told at the next morning even across another save)."""
    out = []
    for event in getattr(world, "event_log", None) or []:
        if not isinstance(event, dict) or event.get("type") != EVENT:
            continue
        if event.get("phase") not in ("roll", "ended", "settled") or event.get("told"):
            continue
        event["told"] = True
        out.append({"type": EVENT, "phase": str(event.get("phase") or ""),
                    "marshal": event.get("marshal"), "nation": event.get("nation"),
                    "band": str(event.get("band") or ""),
                    "message": str(event.get("message") or "")})
    return out


# ═══════════════════════════ old saves ══════════════════════════════════════

def settle_legacy(world, data) -> List[Dict[str, Any]]:
    """An OLD SAVE's men in the middle of the old three turns are settled on
    loading — the same bands, on what they had achieved so far — and the next
    morning says so in one line each (§6.11). `data` is the save being loaded:
    each marshal's saved row is read ONCE, here, for the six old keys
    (`autonomous`, `autonomy_turns`, `autonomy_reason`, `autonomous_battles_won`
    / `_lost`, `autonomous_regions_captured`) — nothing else reads them, and
    `Marshal.to_dict` no longer writes them, so the game then saved carries
    none and a second load finds nothing to settle. Also: a saved audience
    whose arms still name `grant_autonomy` has them rebuilt (`refresh`)."""
    rows = []
    saved = (data or {}).get("marshals") if isinstance(data, dict) else None
    for key, row in (saved.items() if isinstance(saved, dict) else ()):
        if not isinstance(row, dict) or not row.get("autonomous"):
            continue
        marshal = (getattr(world, "marshals", None) or {}).get(key)
        if (marshal is None or on_trial(marshal)
                or marshal.nation != getattr(world, "player_nation", None)):
            continue
        won, lost, taken = (int(row.get("autonomous_battles_won", 0) or 0),
                            int(row.get("autonomous_battles_lost", 0) or 0),
                            int(row.get("autonomous_regions_captured", 0) or 0))
        name, gain, authority = _reward(world, marshal, won, lost, taken)
        shown = humanize_entity_name(marshal.name)
        moved = (f"his trust in you rises by {int(gain)} (to {int(marshal.trust.value)})" if gain > 0
                 else f"his trust in you stands at {int(marshal.trust.value)}")
        if authority > 0:
            moved += f", and your authority by {int(authority)}"
        message = (f"{shown} was acting without orders when this game was saved — a rule that has "
                   f"left the game. He is settled on what he had done by then: {moved}. He is "
                   f"under your orders again.")
        world.log_event({
            "type": EVENT, "phase": "settled", "marshal": marshal.name, "nation": marshal.nation,
            "band": name, "trust_gain": int(gain), "authority_gain": int(authority),
            "won": won, "lost": lost, "taken": taken, "message": message,
        })
        rows.append({"marshal": marshal.name, "band": name, "trust_gain": int(gain),
                     "authority_gain": int(authority), "message": message})
    standing = getattr(world, "pending_redemption", None)
    if isinstance(standing, dict) and any(
            isinstance(item, dict) and item.get("id") == LEGACY_ARM
            for item in (standing.get("options") or [])):
        try:
            refresh(world, standing)
        except Exception as exc:
            report(exc, "trial.settle_legacy: refresh")
    return rows
