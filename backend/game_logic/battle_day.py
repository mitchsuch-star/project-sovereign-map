"""Row BA, session BA-3 — "the day's points": a great battle fought in turns.

The user's frame (November 15, 2026; `docs/BATTLE_DIORAMA_SPEC.md` §15.14):
"what if battles just have x amount of points in them and how you and enemy
use them is at discretion?" — the points from **the commander**, the enemy to
spend his on **all that you can**, and "small battles show the screen current
state it just doesnt need all mechanics".

WHAT IT IS. When a GREAT battle (80,000 men or more engaged — the game's own
bar, `WorldState.GREAT_BATTLE_THRESHOLD`) the player is party to does not
decide the day, the day stays open and each side holds POINTS for the rest of
it: 2, or 3 under a commander of high command (`Marshal.RALLY_FAST_COMMAND`).
The sides speak in turns — the one that did not open speaks first — and each
word is resolved at once. A word is an order the game already has, FREE OF
ACTIONS: the opening attack cost its action as it always did, nothing after
it costs one. Two silences in a row, both purses empty, or a side leaving the
field: night falls.

WHAT IT IS NOT. A small battle is one clash, told as it is told today: this
module opens nothing for it and its tableau carries no `day`. And nothing
here exists outside a campaign the game SERVER holds
(`campaign_variance.campaign_is_served`): a world a test or a measuring
harness builds for itself keeps the game it pins.

THE STORE. `world.battle_days = {"days": {<enemy lead>: day}, "barred": {...}}`
— a day is our quarrel with one enemy corps. Saved only when it holds
something (`WorldState.to_dict`), so an ordinary save is byte for byte what it
was.

THE SEAMS are zero-argument functions read through this module (the driver's
`--seam backend.game_logic.battle_day:<name>=EXPR` replaces the attribute):
`the_day_has_points`, `the_enemy_spends_his`, `the_guard_goes_in`,
`the_guards_numbers_bite`, `a_marshal_may_be_left_to_it`; and the three
numbers as functions too — `points_low`, `points_high`, `key_bar`.

ROW BA, BA-4 ("the roads and the fog", November 16, 2026) added six more, each
one row of the ledger or one item the user ticked at the plan gate:
`a_word_is_quoted_in_points` (BA3-X5), `a_dead_day_bars_nothing` (BA3-X13),
`his_word_is_scored_from_the_day` (BA3-X14), `a_lead_holds_one_day` (BA3-X15),
`a_day_is_one_battle` and `a_days_close_is_told` (the telling).
"""

from __future__ import annotations

import contextlib
import weakref
from contextvars import ContextVar
from typing import Any, Dict, List, Optional

from backend.errors import report
from backend.game_logic import battle_telling as _telling
from backend.game_logic import campaign_variance as _cv

# ════════════════════════════════════════════════════════
# The numbers (the user's rulings 4 and 5; NP-D1's two are the user's own)
# ════════════════════════════════════════════════════════

POINTS = 2                  # a commander's points for the day
POINTS_HIGH_COMMAND = 3     # ...under a commander of high command
PRICES = {
    "press": 1,        # the lead presses
    "lead": 1,         # another corps leads
    "cannonade": 1,    # a battery cannonades
    "bring_up": 1,     # a corps is brought up
    "dig_in": 1,       # the lead digs in
    "guard": 2,        # the Guard goes in
    "stand": 0,        # to stand
    "break_off": 0,    # to break off / fall back
    "strike": 1,       # his: he strikes back (a press, from his side)
    "draw_off": 0,     # his: he leaves the field
}
RESERVE_PURSUIT = 3_000   # BA-5: the PARKED reserve's number, the middle of its ladder (2,000 / 3,000 / 5,000 — none passed)
GUARD_SHOCK = 10      # NP-D1: his lead's morale, as the Guard goes in
GUARD_RECOIL = 10     # NP-D1: every corps of ours that fought, if it is thrown back
LEND = 3              # the actions lent to a word while it is executed (never kept)
TURNS_CAP = 12        # a day's words, at most — a guard against a loop, never reached
HANGING = ("stalemate", "attacker_tactical_victory", "defender_tactical_victory")


def the_day_has_points() -> bool:
    """The seam of the whole: down, no day is ever opened (every battle is one
    clash, as before BA-3)."""
    return True


def the_enemy_spends_his() -> bool:
    """Down, his purse is shut: he stands at every turn of a day (the measure's
    arm E0 — what his say is worth)."""
    return True


def the_guard_goes_in() -> bool:
    """Down, the sovereign leading a renewed assault is another corps leading
    (one point, no morale numbers)."""
    return True


def the_guards_numbers_bite() -> bool:
    """NP-D1's two morale writes. Down, the Guard costs its two points and
    moves no morale (the measure's arm NG)."""
    return True


def a_marshal_may_be_left_to_it() -> bool:
    """Down, there is no "Leave it to him"."""
    return True


def our_table_reads_the_day_as_our_clash_left_it() -> bool:
    """BA5-D1 (row BA, BA-5 "the finish") seam: when his clash follows ours on
    the table, OUR clash's tableau carries the day as it stood when our clash
    ended — read before he answers. `settle` wrote the day as it stood AFTER
    his answer onto it: his purse already a point short, his word already
    told, and under the title the result of a clash the table had not yet
    shown (two blind readers of the frames found the figures of two clashes
    on one screen). Down (False): the day after his answer, as BA-3 had it."""
    return True


def the_reserve_pursues() -> bool:
    """Row BA, BA-5 (the user's tick at the plan gate — "Build it; the rule
    picks") seam: THE RESERVE PURSUES A BEATEN ENEMY. When a clash decides a
    day — a side is driven from the field — the victor counts the points he
    still holds and the beaten side counts its own; for each point the victor
    holds over the loser, the beaten lead loses `reserve_pursuit()` men more.
    A point the loser kept covers him. It is added to a cavalry leader's own
    pursuit, under the game's pursuit laws (never below 1,000 men; halved
    against the Old Fox). Nothing is paid when a side breaks off or draws off,
    or at night. Either side, the same rule (GR5); his rule for spending is
    untouched. Clausewitz's reading of these battles: the fresh reserves left
    at the end decide what a victory is worth (On War, book 4, chapters 9 and
    12) — Borodino closed with the Guard unspent and no pursuit, Jena with
    fresh cavalry and an army destroyed. Down (False): a point kept is worth
    nothing at the close, as BA-3 had it.

    PARKED — DOWN IN THE GAME (November 17, 2026). The rule was built and
    measured, and it failed the rule written for it before its data
    (`BATTLE_DIORAMA_SPEC.md` §15.22; the readings §15.23,
    `tools/_ba5_reserve_rule_2026_11_17.json`): at every value of its ladder
    about nine in ten of the men it took were OURS, where the rule allowed
    neither side more than three quarters. The side that presses spends its
    points; the side that stands keeps his, and harvests when the attack is
    thrown back; a victor who spent to win holds nothing over the loser. It
    would have taught standing still. By the plan's own words it is not
    built: no surface of the game promises it, and this function returning
    True again is the measured arm (`tools/_ba5_measure.py`, arms R<n>).
    CLOSED (session BA-6, November 17, 2026): its second form failed the same
    rule (`the_attacker_pursues`), and the reserve does not land."""
    return False


def reserve_pursuit() -> int:
    """The men a point of reserve costs a beaten lead (a function, so that the
    measure's ladder can read 2,000 / 3,000 / 5,000 through it)."""
    return RESERVE_PURSUIT


def the_attacker_pursues() -> bool:
    """Row BA, session BA-6 seam — the reserve in the form BA-5's own data
    pointed to (§15.23, "Recommended, not built"; ruled under the user's
    delegation of November 17, 2026: "make decisions yourself soundly with
    research"). ONLY THE SIDE THAT ATTACKED IN THE DECIDING CLASH PURSUES, WITH
    THE POINTS IT STILL HOLDS ITSELF: when a word's clash drives the defender
    from the field, each point the attacker kept costs the beaten lead
    `reserve_pursuit()` men more, under the game's pursuit laws (never below
    1,000 men; halved against the Old Fox). A defender who throws the attack
    back keeps the field and does not pursue; a point the loser kept does not
    cover him; nothing is paid on a break-off, a draw-off or at night. It
    rewards winning CHEAPLY - a press that breaks him with points in hand -
    and it cannot pay a side for standing, which is why BA-5's form (the
    victor's points less the loser's, either side) failed its rule: nine in
    ten of the men it took were ours. Either side, the same rule (GR5).
    Measured by the rule BA-5 wrote before its data (§15.22's five clauses,
    the same ladder; `tools/_ba6_measure.py`, arms A<n>). Down (False): no
    pursuit for a point kept, as BA-3 had it.

    CLOSED - DOWN IN THE GAME (November 17, 2026). It failed the rule's third
    clause at every value of the ladder (`tools/_ba6_reserve_rule_2026_11_17.json`):
    twenty-two of its twenty-three pursuits fell on a French corps - 70,639 /
    87,987 / 100,702 of our men against 2,000 / 3,000 / 5,000 of his. The
    reason is not standing but the purse: his AI keeps points by its own
    spending rule, so his attacks that break one of our corps are paid in
    full, while a France that spends to win holds nothing at the close.
    Whoever keeps points harvests, and the measure's France never does. Both
    forms failed the rule written before their data, so the reserve is closed
    and the hand stays as BA-3 made it (a point kept is worth nothing at the
    close). No surface of the game promises a reserve; this function returning
    True is the measured arm only."""
    return False


def _the_reserve_is_counted() -> bool:
    """Either form of the reserve is up (BA-5's parked form, BA-6's)."""
    return the_reserve_pursues() or the_attacker_pursues()


def a_words_battle_is_its_own_clash() -> bool:
    """Row BA, BA-5 seam (the session's review): the running word is THIS
    battle only where the battle is fought against the day's enemy (our word)
    or against the day's lead (his). An objection answered "his own way" whose
    attack falls on another corps fights a battle of its own: it is no clash of
    the day (not counted, named or told as one), the Guard's shock does not
    fall on that corps, and the reserve counts no purse for it. The word is
    still paid for and told as the marshal's own way (`answer_given`). Down
    (False): every battle fought while a word runs is the word's (BA-3)."""
    return True


def _word_for(ctx) -> Optional[dict]:
    """The running word, where this battle is its clash (`a_words_battle_is_
    its_own_clash`); else None."""
    word = _WORD.get()
    if not word or not a_words_battle_is_its_own_clash():
        return word
    foe = getattr(getattr(ctx, "enemy_marshal", None), "name", None)
    if word.get("who") == "ours":
        return word if foe == word.get("key") else None
    day = day_against(getattr(ctx, "world", None), word.get("key"))
    if day is None:
        return word        # the day cannot be read here: BA-3's reading stands
    return word if foe == day.get("lead") else None


def count_the_reserve(ctx) -> None:
    """At the head of a word's clash (beside `guard_shock`): what each side
    would hold with this word paid for — kept on the word, where the engine's
    pursuit step reads it (`reserve_pursuit_men`). A no-op for every attack
    that is no word of an open day."""
    word = _word_for(ctx)
    world = getattr(ctx, "world", None)
    if not (word and _the_reserve_is_counted() and _on(world)):
        return
    day = day_against(world, word.get("key"))
    if day is None:
        return
    mine, yours = ("ours", "theirs") if word.get("who") == "ours" else ("theirs", "ours")
    paid = 0 if word.get("taken") else int(word.get("price", 0) or 0)
    word["reserve"] = {"attacker": max(0, int(day.get(mine, 0) or 0) - paid),
                       "defender": int(day.get(yours, 0) or 0)}


def reserve_pursuit_men(*, attacker_wins: bool, loser):
    """(men, points): what the reserve costs the lead this clash drove from
    the field — `points` the victor holds over him, `men` after the Old Fox's
    halving and the 1,000-man floor. (0, 0) outside a day's word, with the
    seam down, when the victor holds no more than the loser, or when the
    beaten corps stands at 1,000 men or under."""
    counted = (_WORD.get() or {}).get("reserve")
    if not (_the_reserve_is_counted() and isinstance(counted, dict)):
        return 0, 0
    if the_attacker_pursues():
        # BA-6: only the attacker of the clash pursues, with his own purse
        if not attacker_wins:
            return 0, 0
        points = int(counted.get("attacker", 0))
    else:
        victor, beaten = ("attacker", "defender") if attacker_wins else ("defender", "attacker")
        points = int(counted.get(victor, 0)) - int(counted.get(beaten, 0))
    if points <= 0:
        return 0, 0
    men = int(reserve_pursuit()) * points
    if (getattr(loser, "ability", None) or {}).get("name") == "The Old Fox":
        men = int(men * 0.5)
    strength = int(getattr(loser, "strength", 0) or 0)
    if strength <= 1000:
        return 0, 0
    return max(0, min(men, strength - 1000)), points


def a_lead_holds_his_day_as_the_battle_began() -> bool:
    """Row BA, BA-5 seam (BA5-X1 — ruling 9's card pressed in the real client,
    November 17, 2026). "One day a lead" (BA3-X15) was read AFTER the battle:
    a lead whose day was open, sent against another corps, won that clash on
    points and ADVANCED — so by the time the rule asked, he stood off his first
    day's ground, that day read dead, and the second battle opened a day of
    its own under a card that had said "a single clash, with no day of its
    own" (measured: seed ba5-oneday-02, Masséna against the Archduke John
    while his day against the Archduke Charles stood open). The day he holds
    is noted at the head of the attack's resolution, before anyone moves
    (`note_the_day_he_holds`), and `_after_the_battle` reads that. His advance
    then ends the first day, and its close says he marched from it. Down
    (False): BA-4's reading."""
    return True


def note_the_day_he_holds(ctx) -> None:
    """At the head of an attack's resolution, before a victor's advance moves
    anyone: the open, living day the player's lead of this battle holds, kept
    on the context for `_after_the_battle` (BA5-X1)."""
    try:
        world = getattr(ctx, "world", None)
        if not _on(world) or not a_lead_holds_his_day_as_the_battle_began():
            return
        player = getattr(world, "player_nation", None)
        for corps in (getattr(ctx, "marshal", None), getattr(ctx, "enemy_marshal", None)):
            if corps is not None and getattr(corps, "nation", None) == player:
                held = the_day_he_holds(world, corps.name)
                setattr(ctx, "_bd_day_held", str(held.get("enemy") or "") if held else "")
                return
    except Exception as exc:
        report(exc, "battle_day.note_the_day_he_holds")


def his_first_day_ends(ctx) -> str:
    """BA5-X1: our lead of this battle held a day when it began, and has left
    that day's ground by his own advance — the day ends NOW (not at the next
    read of the table), and its close line is returned for the battle's own
    message. "" where nothing ended."""
    try:
        world = getattr(ctx, "world", None)
        kept = str(getattr(ctx, "_bd_day_held", "") or "")
        if not kept or not _on(world) or not a_lead_holds_his_day_as_the_battle_began():
            return ""
        day = open_days(world).get(kept)
        if day is None or _alive(world, day) or not _he_marched_from_it(world, day):
            return ""
        closing = _close(world, kept, "over")
        (_CLOSED.get(world) or {}).pop(kept, None)      # told here: no table waits for it
        return str((closing or {}).get("close") or "")
    except Exception as exc:
        report(exc, "battle_day.his_first_day_ends")
        return ""


def _he_marched_from_it(world, day) -> bool:
    """BA5-X1: a day that is over because its own lead left its ground — both
    leads still under arms and at war, his still where the day found him."""
    if world is None or not day.get("our_ground") or not a_lead_holds_his_day_as_the_battle_began():
        return False
    lead, foe = world.get_marshal(day.get("lead")), world.get_marshal(day.get("enemy"))
    return bool(_under_arms(lead) and _under_arms(foe)
                and lead.location != day.get("our_ground")
                and foe.location == day.get("his_ground")
                and world.get_diplomatic_state(lead.nation, foe.nation) == "WAR")


def a_marshal_keeps_his_days() -> bool:
    """Row BA, BA-5 seam (the user's tick at the plan gate — "A marshal's
    days"): a pitched battle our marshal LED is kept on his own record when it
    is over — its name, its turn, how it went for him, what told and, for a
    great battle fought in turns, what kind of day it was (`Marshal.days`, the
    last six; his card on the Generals screen reads them). No rule of the game
    reads the record. Down (False): nothing is kept, and a save is as it was."""
    return True


def a_ruin_is_kept_as_drawn() -> bool:
    """Row BA, session BA-6 seam (BA6-X1, found by the session's fresh review
    of BA-5): a day closed by a clash that ruined both armies was decided for
    neither, and his record says "drawn" - not "won on points" (read off the
    day's toll) above its own shape "Neither army kept the field.". Down
    (False): the toll's verdict, as before."""
    return True


# How a battle went for the marshal who led it, in his card's words: by a
# clash that decided it, else on points (the toll at 5 to 4 — `better_of`).
_VERDICTS = {
    (True, "ours"): "won", (True, "theirs"): "lost",
    (False, "ours"): "won on points", (False, "theirs"): "lost on points",
}


def _verdict(decided: bool, better: str) -> str:
    return _VERDICTS.get((bool(decided), str(better or "")), "drawn")


def _keep_his_battle(world, ctx, ours, his, attacker_is_ours: bool, hanging: bool) -> None:
    """BA-5: a pitched battle that opened no day, on the record of the marshal
    who led it for us. (A battle that opens a day is kept when the day closes:
    `_keep_his_day`; a further clash of an open day is that day's.) A battle
    that `hanging` left undecided - too small for a day, or its lead's day
    already open - went on points; any other was decided for one side."""
    if not a_marshal_keeps_his_days():
        return
    try:
        read = _read(ctx, attacker_is_ours)
        decided = "" if hanging else _telling.decided_for(ctx, attacker_is_ours)
        ahead = str(read.get("ahead") or "")
        better = decided or (ahead if ahead in ("ours", "theirs") else "")
        told = _telling.what_told(ctx, attacker_is_ours, better) if better else ""
        ours.keep_day({
            "name": the_battle_of(getattr(ctx, "battle_name", "")),
            "turn": int(getattr(world, "current_turn", 0) or 0),
            "place": str(getattr(ctx, "battle_region_name", "") or his.location or ""),
            "against": str(his.name),
            "verdict": _verdict(bool(decided), better),
            "told": "" if told == "an even fight" else str(told),
            "shape": "",
            "our_loss": int(read.get("our_loss", 0) or 0),
            "his_loss": int(read.get("his_loss", 0) or 0),
        })
    except Exception as exc:
        report(exc, "battle_day._keep_his_battle")


def _keep_his_day(world, day: dict, how: str) -> None:
    """BA-5: a day of battle that has closed, on the record of the marshal who
    led it for us — once (a day closes once). Its verdict is the deciding
    clash's, or the toll's for a day no clash decided; its shape is the
    close's own (`battle_telling.shape_of`)."""
    if not a_marshal_keeps_his_days():
        return
    try:
        lead = world.get_marshal(day.get("lead"))
        fought = int(day.get("clashes", 0) or 0)
        if lead is None or fought <= 0:
            return
        toll = day.get("toll") or {}
        ours_lost, his_lost = int(toll.get("ours", 0) or 0), int(toll.get("his", 0) or 0)
        decided = str(day.get("decided_for") or "") if how == "decided" else ""
        better = decided or _telling.better_of(ours_lost, his_lost)
        if how == "decided" and not decided and a_ruin_is_kept_as_drawn():
            # BA6-X1 (BA-6's fresh review of BA-5): a clash that ruined both
            # armies decided the day for NEITHER; the toll does not make it a
            # day "won on points" beside "Neither army kept the field."
            better = ""
        told = str(day.get("decided_by") or "") if how == "decided" else ""
        lead.keep_day({
            "name": str(day.get("name") or ""),
            "turn": int(day.get("turn", 0) or getattr(world, "current_turn", 0) or 0),
            "place": str(day.get("opened_at") or day.get("field") or ""),
            "against": str(day.get("enemy") or ""),
            "verdict": _verdict(bool(decided), better if better in ("ours", "theirs") else ""),
            "told": "" if told == "an even fight" else told,
            "shape": _telling.shape_of(day, how, _shown(day.get("enemy")), _shown(day.get("lead"))),
            "our_loss": ours_lost, "his_loss": his_lost, "clashes": fought,
        })
    except Exception as exc:
        report(exc, "battle_day._keep_his_day")


def the_first_days_line_stands_on_its_first_table() -> bool:
    """Row BA, session BA-5 seam. The first day of a campaign says what a day
    is (BA-4, `first_open` "battle_day") — on the FIRST TABLE THE PLAYER SEES,
    and not on the day's next. A screen's first-open line stays on every
    payload of the turn it was first shown (`first_open.line_for`: a screen
    that re-reads itself must not lose it mid-read), and a day of battle is
    fought inside one turn — so the line stood on EVERY table of a campaign's
    first day and took the room of the exits' own words while the player was
    learning them (seen in the real client). While the line is unacknowledged
    every block carries it, as before (a table with no room for it leaves it
    to the next; a first word given from the province's panel leaves it to
    the table that follows). When the client says it has drawn it
    (`POST /first_open` → `the_days_line_was_shown`) each open day is marked
    as it stood, and from then on the line rides only a block of a day that
    still stands so: a re-read of the table that showed it. Down (False): on
    every table of the turn, as BA-4 had it."""
    return True


def _as_it_stands(day: dict) -> list:
    """A day's standing, for `the_days_line_was_shown`: a figure that every
    word of either side moves (a word given, a silence, a point spent, a
    clash fought)."""
    return [int(day.get("words", 0) or 0), int(day.get("silences", 0) or 0),
            int(day.get("ours", 0) or 0), int(day.get("theirs", 0) or 0),
            int(day.get("clashes", 0) or 0), str(day.get("awaits") or "")]


def the_days_line_was_shown(world) -> None:
    """BA-5: the client has drawn the first day's line (`POST /first_open`,
    screen "battle_day"). Every day open now is marked as it stands
    (`first_shown_at`): its table is the one that showed the line."""
    if not the_first_days_line_stands_on_its_first_table():
        return
    try:
        for day in open_days(world).values():
            day["first_shown_at"] = _as_it_stands(day)
    except Exception as exc:
        report(exc, "battle_day.the_days_line_was_shown")


def _says_its_first_line(world, day: dict) -> bool:
    """Whether this block carries the first day's line: always while it is
    unacknowledged; once acknowledged, only for a day that stands as it stood
    when its table showed the line."""
    if not the_first_days_line_stands_on_its_first_table():
        return True
    from backend.game_logic import first_open as _first_open
    if not _first_open.is_seen(world, "battle_day"):
        return True
    return day.get("first_shown_at") == _as_it_stands(day)


def a_dead_day_bars_nothing() -> bool:
    """BA3-X13 (row BA, BA-4) seam: night bars a pair from a second strike
    only where the day was still a day when night began. A day already dead —
    its lead marched off, a corps gone, peace made — was closed by the night
    with no word said, and still barred its enemy from striking our lead in
    the phase that followed. Down (False): every day open when night began
    bars its pair."""
    return True


def a_lead_holds_one_day() -> bool:
    """BA3-X15 (row BA, BA-4; the user's ruling at the plan gate — "One day a
    lead") seam: a second great battle that hangs, fought by a lead whose day
    is still open, opens no day. It is one clash, told as a battle is told,
    with a line that says why (`word_line`). Two days on one lead gave him two
    purses and two enemies to answer in turn. Down (False): every hanging
    great battle opens a day, as BA-3 had it."""
    return True


def his_word_is_scored_from_the_day() -> bool:
    """BA3-X14 (row BA, BA-4) seam: his word's order is scored from the day's
    own stream. `EnemyAI._execute_action` scores every order it runs (the
    strategic score's ±10, drawn from his court's stream of the phase —
    `enemy_ai.ai_rng`), so a word he gave in OUR turn, or at nightfall, drew
    from the stream his court's phase was about to draw from: the player's
    hand moved the phase's dice. Down (False): the phase's stream, as BA-3
    had it."""
    return True


def a_day_is_one_battle() -> bool:
    """Row BA, BA-4 (the user's tick at the plan gate — "One name for a day")
    seam: a day of battle is told under ONE name, the opening clash's, and
    each later clash is "… — the second clash". Before it every clash of a
    day took the province's next ordinal: one afternoon at Swabia was "The
    Great Battle", "The Great Second Battle" and "The Great Third Battle" of
    Swabia. The province's count still advances a clash (the battle's dice
    and the voice rotation read it); the later clashes are counted beside it
    and left out of the ordinal (`WorldState.compose_battle_name`), so the
    next battle fought there is "the Second". Display only. Down (False):
    every clash a battle of its own."""
    return True


def a_days_close_is_told() -> bool:
    """Row BA, BA-4 (the user's tick — "Line for a quiet night", widened
    under his "make any other improvements") seam: every way a day ends is
    told in ONE line with its clashes and its toll — on the closing table
    (`close`), in the campaign log (`battle_day_closed`), and, for a day the
    night closed with no table to tell it, among the morning's turn events.
    Display only. Down (False): a day closes with its banner alone, as BA-3
    had it."""
    return True


def points_low() -> int:
    return POINTS


def points_high() -> int:
    return POINTS_HIGH_COMMAND


KEY_BATTLE_MEN = 50_000


def key_bar(world) -> int:
    """A KEY battle — one fought on with the day's points when its opening
    clash does not decide the day — is a pitched battle of 50,000 men or more
    engaged, both sides together.

    Row BA, BA-4 (the user's "do research of what's the most FUN";
    `BATTLE_DIORAMA_SPEC.md` §15.19 the rule written before the data, §15.20
    M6 the ladder): of 50,000 / 60,000 / 70,000 / 80,000 the LOWEST bar whose
    days are rich (two in three offer four or more priced words), varied (at
    most one in five repeats a pairing within two turns) and rested (at most
    eight a campaign, four turns running in at most one campaign of sixteen)
    with the band and the hand in place. BA-3's bar was the game's GREAT
    battle (`WorldState.GREAT_BATTLE_THRESHOLD`, 80,000), which keeps its
    name ("The Great Battle of …") and its news; the great battle is one of
    the key ones. ONE function to reverse; never above the great bar."""
    return min(KEY_BATTLE_MEN, int(getattr(world, "GREAT_BATTLE_THRESHOLD", 80000)))


# ════════════════════════════════════════════════════════
# The store
# ════════════════════════════════════════════════════════

_WORD: ContextVar[Optional[dict]] = ContextVar("the_days_word", default=None)
# A clash's tableau, kept beside the world until it is read (never saved).
_TABLEAUX: "weakref.WeakKeyDictionary[Any, Dict[str, dict]]" = weakref.WeakKeyDictionary()
# A day's closing block, kept until the response that closed it has read it.
_CLOSED: "weakref.WeakKeyDictionary[Any, Dict[str, dict]]" = weakref.WeakKeyDictionary()
# BA-4: the closing lines of the days the NIGHT closed, kept for the morning's
# turn events (`dawn_tells_the_night`); never saved — night and dawn are one
# end of turn.
_NIGHT: "weakref.WeakKeyDictionary[Any, List[str]]" = weakref.WeakKeyDictionary()
_IN_THE_NIGHT: ContextVar[bool] = ContextVar("night_is_falling", default=False)
# BA-4 (BA3-X15): the line of a clash that opened no day because its lead
# holds one — written by the battle's hook, read once by its script's.
_ALONE: ContextVar[Optional[dict]] = ContextVar("a_clash_that_opens_no_day", default=None)


def _on(world) -> bool:
    return bool(world is not None and the_day_has_points() and _cv.campaign_is_served(world))


def _store(world) -> dict:
    store = getattr(world, "battle_days", None)
    if not isinstance(store, dict):
        store = {}
        world.battle_days = store
    store.setdefault("days", {})
    return store


def open_days(world) -> Dict[str, dict]:
    """Every day still open, by its enemy lead. {} off the served road."""
    if world is None or not isinstance(getattr(world, "battle_days", None), dict):
        return {}
    return world.battle_days.get("days") or {}


def day_against(world, enemy_name) -> Optional[dict]:
    return open_days(world).get(str(enemy_name or ""))


def the_day_he_holds(world, lead_name) -> Optional[dict]:
    """BA3-X15, one day a lead: the open, living day `lead_name` holds — the
    day a second hanging battle of his defers to (`_after_the_battle`), and
    the reason his attack card forecasts none (`order_quotes.attack_quote`;
    the session's review, lane 3: the card promised "…commands the day" for a
    battle the rule would tell as a single clash). None with the rule down,
    or where he holds none."""
    if not a_lead_holds_one_day():
        return None
    return next((d for d in open_days(world).values()
                 if d.get("lead") == str(lead_name or "") and _alive(world, d)), None)


def points_for(marshal) -> int:
    """The commander's points (ruling 4): 2, or 3 at high command."""
    from backend.models.marshal import Marshal
    command = int((getattr(marshal, "skills", None) or {}).get("command", 5) or 5)
    return int(points_high() if command >= Marshal.RALLY_FAST_COMMAND else points_low())


def forecast(world, lead, total_engaged: int, foe=None) -> Optional[dict]:
    """For the attack card: whether a battle of `total_engaged` men would be a
    great one, the points its commander would bring, and — the lesson of Ulm —
    whether a road is open behind the enemy (beaten on points with a road
    open, he draws off: the field is taken and his army is not). None where
    no day could be opened."""
    if not _on(world) or lead is None:
        return None
    if int(total_engaged or 0) < key_bar(world):
        return None
    out = {"great": True, "points": points_for(lead), "bar": key_bar(world)}
    if int(total_engaged or 0) < int(getattr(world, "GREAT_BATTLE_THRESHOLD", 80000)):
        # BA-4: a key battle short of the game's GREAT one — the card says
        # "A pitched battle — …" (`great` stays the forecast's own switch).
        out["pitched"] = True
    if foe is not None:
        road = _his_road(world, foe)
        if road is not None:
            out["his_road"] = road
    return out


def _his_road(world, foe) -> Optional[bool]:
    """Is a road open behind him — to his own soil, an ally's or a neutral's
    that lets him pass, with none of our corps on it? (Never the soil of a
    court he is at war with: a corps with only that left is surrounded.) Read
    from the map every player sees by the finder his AI itself uses; it draws
    from no stream. None when it cannot be read."""
    try:
        from backend.ai.enemy_ai import EnemyAI
        return bool(EnemyAI(None)._find_retreat_destination(
            foe, foe.nation, world, desperate=False))
    except Exception as exc:
        report(exc, "battle_day._his_road")
        return None


def _shown(name) -> str:
    from backend.display_names import humanize_entity_name
    return humanize_entity_name(str(name or ""))


def _place(world, name) -> str:
    return _shown(name)


def _under_arms(marshal) -> bool:
    return bool(marshal is not None and int(getattr(marshal, "strength", 0) or 0) > 0
                and not getattr(marshal, "broken", False)
                and not getattr(marshal, "retreating", False))


def _stands(marshal) -> bool:
    """Under arms and asked nothing: a corps the battle left with a question
    of its own (a last stand) has not fought to an open day."""
    return _under_arms(marshal) and not getattr(marshal, "pending_interrupt", None)


def _alive(world, day) -> bool:
    """A day is still a day: both leads under arms, where the day found them,
    and still at war."""
    lead, foe = world.get_marshal(day.get("lead")), world.get_marshal(day.get("enemy"))
    # A question a WORD raised (the muster's "Commit the Attack?") does not end
    # the day: the corps is under arms and waits for the answer.
    if not _under_arms(lead) or not _under_arms(foe):
        return False
    if lead.location != day.get("our_ground") or foe.location != day.get("his_ground"):
        return False
    return world.get_diplomatic_state(lead.nation, foe.nation) == "WAR"


BANNER_OPEN = "The day hangs"
BANNERS = {
    "night": "Night falls",
    "drew_off": "{enemy} draws off",
    "he_broke_off": "{enemy} breaks off",
    "broke_off": "The attack is broken off",
    "fell_back": "{lead} falls back",
}


def _close(world, key: str, how: str, line: str = "", banner: str = "") -> dict:
    """Close a day; the last block is returned (open False) for the response.
    `banner` (default: `how`) picks the closing banner — the table's headline
    for a day that ended otherwise than by a clash that decided it (that clash
    keeps its own verdict)."""
    days = _store(world)["days"]
    day = days.pop(key, None) or {"enemy": key}
    if line:
        _tell(day, "end", line)
    day["banner"] = BANNERS.get(banner or how, "").format(
        enemy=_shown(day.get("enemy")), lead=_shown(day.get("lead")))
    day.pop("pending", None)        # a closed day asks nothing (a defiant lead's own attack may close it)
    day["open"] = False
    day["ended"] = how
    _tell_the_close(world, day, how, banner or how)
    _keep_his_day(world, day, banner or how)       # BA-5: on the lead's own record
    if not days and not world.battle_days.get("barred"):
        world.battle_days = {}
    closing = block(world, day)
    _CLOSED.setdefault(world, {})[key] = closing
    return closing


_NUMBER_WORDS = ("no", "one", "two", "three", "four", "five", "six", "seven",
                 "eight", "nine", "ten", "eleven", "twelve")
_ORDINAL_WORDS = ("", "first", "second", "third", "fourth", "fifth", "sixth",
                  "seventh", "eighth", "ninth", "tenth", "eleventh", "twelfth")


def _ordinal(n: int) -> str:
    n = int(n)
    return _ORDINAL_WORDS[n] if 0 < n < len(_ORDINAL_WORDS) else f"{n}th"


def _clashes(n: int) -> str:
    n = int(n)
    word = _NUMBER_WORDS[n] if 0 <= n < len(_NUMBER_WORDS) else str(n)
    return f"{word} clash" if n == 1 else f"{word} clashes"


def _count_the_clash(day: dict, read: dict, *, opening: bool = False) -> None:
    """BA-4: a clash of the day, for its name and its close — how many were
    fought and what they cost each side (the battle's own report gives both
    tolls to the player who fought it). Kept only where one of the two
    tellings is up: with both down a day's record is BA-3's, key for key.
    The count begins at the day's OPENING clash or not at all: a day that
    kept none (one a save made before BA-4 carries open) starts none at its
    second clash — "after one clash" and half the toll would be told of a day
    of two. Such a day closes as BA-3 closed it, with no line of its own."""
    if not (a_day_is_one_battle() or a_days_close_is_told()):
        return
    if not opening and "clashes" not in day:
        return
    day.setdefault("opened_at", day.get("field"))
    day["clashes"] = int(day.get("clashes", 0) or 0) + 1
    toll = day.setdefault("toll", {"ours": 0, "his": 0})
    toll["ours"] = int(toll.get("ours", 0) or 0) + int((read or {}).get("our_loss", 0) or 0)
    toll["his"] = int(toll.get("his", 0) or 0) + int((read or {}).get("his_loss", 0) or 0)


def close_line(world, day: dict, how: str) -> str:
    """BA-4: how a day ended, in one line — its clashes and its toll. "" for
    a day that kept no count (one opened before BA-4). Fog: the field and
    both leads are the day's own, public since it opened; where he went when
    he drew off is never said."""
    fought = int(day.get("clashes", 0) or 0)
    if fought <= 0:
        return ""
    # The field the day OPENED on — the battle's own, and its name's. `field`
    # follows the last clash (he strikes back on our ground), and "the attack
    # at Rhineland was broken off" named the province Ney attacked FROM.
    field = _place(world, day.get("opened_at") or day.get("field"))
    lead, enemy = _shown(day.get("lead")), _shown(day.get("enemy"))
    after = f"after {_clashes(fought)}"
    head = {
        "night": f"Night fell on the field at {field}: {_clashes(fought)} and no decision",
        "decided": f"The day at {field} was decided at the {_ordinal(fought)} clash",
        "drew_off": f"{enemy} drew off from {field} {after}",
        "he_broke_off": f"{enemy} broke off his attack at {field} {after}",
        "broke_off": f"The attack at {field} was broken off {after}",
        "fell_back": f"{lead} fell back from {field} {after}",
    }.get(how, f"The day at {field} ended where it stood {after}")
    if how == "over" and _he_marched_from_it(world, day):
        # BA5-X1: he left the field for another — said, not "ended where it stood"
        head = f"{lead} marched from the field at {field} {after}"
    toll = day.get("toll") or {}
    return (f"{head} — {int(toll.get('ours', 0) or 0):,} of ours for "
            f"{int(toll.get('his', 0) or 0):,} of the enemy's.")


def _tell_the_close(world, day: dict, how: str, banner: str) -> None:
    """BA-4: the day's close, told — on the closing block (`close`), in the
    campaign log, and kept for the morning where the night closed it."""
    if not a_days_close_is_told():
        return
    try:
        line = close_line(world, day, banner)
        if not line:
            return
        # BA-5: what told (a day a clash decided), whom the toll favoured (any
        # other), and what kind of day it was — after BA-4's line, whose words
        # stay as they were.
        more = (_telling.close_more(day, banner, _shown(day.get("enemy")), _shown(day.get("lead")))
                if _telling.the_close_names_what_told() else [])
        if more:
            line = f"{line} {' '.join(more)}"
        day["close"] = line
        if how != "decided":
            # On the closing table, under the line that says HOW it ended (night
            # fell, he drew off, we broke off): what the day came to. A day a
            # clash decided keeps that clash's own verdict and builds no panel.
            toll = day.get("toll") or {}
            fought = _clashes(int(day.get("clashes", 0) or 0))
            _tell(day, "end", (f"{fought[:1].upper()}{fought[1:]}: "
                               f"{int(toll.get('ours', 0) or 0):,} of ours for "
                               f"{int(toll.get('his', 0) or 0):,} of the enemy's."), "tally")
            if more:
                _tell(day, "end", " ".join(more), "shape")
            follows = (_telling.what_follows(banner)
                       if _telling.the_close_names_what_told() else "")
            if follows:
                _tell(day, "end", follows, "after")
        toll = day.get("toll") or {}
        world.log_event({
            "type": "battle_day_closed",
            "nation": getattr(world, "player_nation", None),
            "field": day.get("field"), "lead": day.get("lead"), "enemy": day.get("enemy"),
            "how": how, "clashes": int(day.get("clashes", 0) or 0),
            "our_loss": int(toll.get("ours", 0) or 0), "his_loss": int(toll.get("his", 0) or 0),
            "line": line,
        })
        if _IN_THE_NIGHT.get():
            _NIGHT.setdefault(world, []).append(line)
    except Exception as exc:
        report(exc, "battle_day._tell_the_close")


def dawn_tells_the_night(world) -> None:
    """BA-4: the days the night closed — and the days the dawn closed
    (`at_dawn`) — are told among the morning's turn events: the table was not
    there to tell them (`turn_manager._the_days_dawn`, after the turn has
    advanced and the dawn has been read, before the dispatch reads the
    turn's events)."""
    lines = _NIGHT.pop(world, None) or []
    events = getattr(world, "_last_tactical_events", None)
    if not lines or not isinstance(events, list):
        return
    player = getattr(world, "player_nation", None)
    for line in lines:
        events.append({"type": "battle_day_closed", "nation": player, "message": line})


def _tell(day: dict, who: str, line: str, kind: str = "") -> None:
    told = day.setdefault("told", [])
    told.append({"who": who, "kind": kind, "line": str(line)})
    del told[:-8]
    if kind and who in ("ours", "theirs") and _telling.the_close_names_what_told():
        # BA-5: the day's words in their order, for its close (`shape_of`) —
        # the told lines keep only the last eight, and a clash's own line is
        # among them now.
        day.setdefault("said", []).append([who, kind])


def _tell_the_clash(day) -> None:
    """BA-5: the clash a word fought, told AFTER the word's own line ("Ney
    presses the attack." and then how it stood) — `_after_the_battle` keeps
    the line until the word that fought it has been told."""
    line = day.pop("clash_line", "") if isinstance(day, dict) else ""
    if line:
        _tell(day, "clash", line, "clash")


def _tell_the_last(world, key: str, who: str, line: str, kind: str = "") -> None:
    """The word that DECIDED a day: its line goes onto the closing block (the
    day itself is gone by the time the word's order returns)."""
    closing = (_CLOSED.get(world) or {}).get(key)
    if closing is not None and closing.get("ended") == "decided":
        closing.setdefault("told", []).append({"who": who, "kind": kind, "line": str(line)})


def _take(day: dict, who: str, price: int) -> None:
    day[who] = max(0, int(day.get(who, 0)) - int(price))
    if int(price) > 0:
        day["silences"] = 0


# ════════════════════════════════════════════════════════
# The battle's own hook (combat_executor, stage 18's head)
# ════════════════════════════════════════════════════════

def _hangs(ctx) -> bool:
    result = getattr(ctx, "battle_result", None) or {}
    if str(result.get("outcome") or "") not in HANGING:
        return False
    if getattr(ctx, "conquered", False) or getattr(ctx, "enemy_destroyed", False):
        return False
    for side in ("attacker", "defender"):
        if (result.get(side) or {}).get("forced_retreat"):
            return False
    return _stands(ctx.marshal) and _stands(ctx.enemy_marshal)


def _read(ctx, attacker_is_ours: bool) -> dict:
    """The clash as the day keeps it: who is ahead on points, and the two
    tolls (the battle's own report gives both to the player who fought it)."""
    result = getattr(ctx, "battle_result", None) or {}
    outcome = str(result.get("outcome") or "")
    ahead = "even"
    if outcome == "attacker_tactical_victory":
        ahead = "ours" if attacker_is_ours else "theirs"
    elif outcome == "defender_tactical_victory":
        ahead = "theirs" if attacker_is_ours else "ours"
    atk = int((result.get("attacker") or {}).get("casualties", 0) or 0)
    dfd = int((result.get("defender") or {}).get("casualties", 0) or 0)
    return {"ahead": ahead,
            "our_loss": atk if attacker_is_ours else dfd,
            "his_loss": dfd if attacker_is_ours else atk}


def guard_shock(ctx) -> None:
    """NP-D1's first write, at the head of the attack's resolution: as the
    Guard goes in, the lead it falls on loses heart (before either side's
    dice). The Guard is a SOVEREIGN's renewed assault in a day of battle —
    ours or, by Golden Rule 5, an enemy's (the same kit, the same numbers)."""
    word = _word_for(ctx)
    if not (word and word.get("kind") == "guard" and the_guards_numbers_bite()):
        return
    foe = getattr(ctx, "enemy_marshal", None)
    if foe is not None and not word.get("shocked"):
        foe.adjust_morale(-GUARD_SHOCK)
        word["shocked"] = True


def _guard_recoil(ctx, word) -> bool:
    """NP-D1's second write: the Guard thrown back — every corps of its own
    side that fought, still under arms, loses heart."""
    if not (word and word.get("kind") == "guard" and the_guards_numbers_bite()):
        return False
    result = getattr(ctx, "battle_result", None) or {}
    beaten = (str(result.get("outcome") or "") in ("defender_victory", "defender_tactical_victory")
              or bool((result.get("attacker") or {}).get("forced_retreat")))
    if not beaten:
        return False
    seen = set()
    for corps in [ctx.marshal] + list(getattr(ctx, "atk_participants", None) or []):
        name = getattr(corps, "name", None)
        if not name or name in seen or int(getattr(corps, "strength", 0) or 0) <= 0:
            continue
        seen.add(name)
        corps.adjust_morale(-GUARD_RECOIL)
    return True


def word_line(ctx) -> Optional[dict]:
    """For the tableau's script (`battle_script`): the WORD this clash is, in
    the day's own line — {who, kind, line} — or None for an opening clash and
    for every ordinary battle. Fog: the line says what the field showed (who
    came on), never an odds figure or a purse. (The re-review) The word is
    this battle's only where it is fought as the word's own clash
    (`_word_for`): a battle on another corps tells no line of the day."""
    word = _word_for(ctx)
    world = getattr(ctx, "world", None)
    alone = _ALONE.get()
    if alone is not None:
        # BA3-X15: read once, by the battle that left it.
        _ALONE.set(None)
        pair = (getattr(getattr(ctx, "marshal", None), "name", None),
                getattr(getattr(ctx, "enemy_marshal", None), "name", None))
        if alone.get("pair") == pair:
            return {"who": "", "kind": "alone", "line": str(alone.get("line") or "")}
    if not word or world is None or word.get("key") not in open_days(world):
        return None
    who, kind = str(word.get("who") or ""), str(word.get("kind") or "")
    shown, foe = _shown(word.get("marshal")), _shown(word.get("key"))
    day = open_days(world)[word["key"]]
    if who == "ours":
        line = _ours_said(day, kind, word.get("marshal"), word.get("key"))
    else:
        # The tableau's own line says what the day's telling says (BA3-X10).
        again = int(day.get("strikes_theirs", 0)) > 0 or day.get("side") == "defence"
        line = _HIS_LINES["guard" if kind == "guard" else (
            "strike_again" if again else "strike")].format(who=shown)
    return {"who": who, "kind": kind, "line": line}


def after_the_battle(ctx) -> Optional[dict]:
    """Open a day, carry one on, or close one — for the battle just fought.
    Returns the day's block for the tableau's payload, or None (an ordinary
    battle: no day, nothing added)."""
    try:
        return _after_the_battle(ctx)
    except Exception as exc:
        report(exc, "battle_day.after_the_battle")
        return None


def _what_told_in_it(ctx, attacker_is_ours: bool) -> str:
    """What told in a battle that is no day's clash: for the side a decision
    left on the field — else, on points, for the side ahead; "an even fight"
    where neither is."""
    read = _read(ctx, attacker_is_ours)
    decided = "" if _hangs(ctx) else _telling.decided_for(ctx, attacker_is_ours)
    ahead = str(read.get("ahead") or "")
    better = decided or (ahead if ahead in ("ours", "theirs") else "")
    return _telling.what_told(ctx, attacker_is_ours, better) if better else "an even fight"


def _whose_line_broke(ctx) -> str:
    """The lead a clash drove from the field, as the table shows his name — ""
    where neither line broke, or both (the script's own "break" beat reads the
    same key: `battle_script._crisis`)."""
    result = getattr(ctx, "battle_result", None) or {}
    attacker = bool((result.get("attacker") or {}).get("forced_retreat"))
    defender = bool((result.get("defender") or {}).get("forced_retreat"))
    if attacker == defender:
        return ""
    lead = getattr(ctx, "marshal" if attacker else "enemy_marshal", None)
    return _shown(getattr(lead, "name", "")) if lead is not None else ""


def the_verdicts_line(ctx, day_block=None) -> str:
    """BA-5: WHAT TOLD, for the line under the headline of a battle's own
    table (`battle_telling.verdict_line`) — said to the player whose marshal
    LED a side of it, on any road (a campaign the server holds or not): it is
    a telling read from the battle's own report, which that player is given
    whole, and no rule reads it. "" for a battle we led no side of, and for a
    table that is a day's own (`day_block` open, or closed under a banner of
    its own: its lines say what told in each clash). The clash that decided a
    day names itself (`_after_the_battle` wrote the line on the closing
    block)."""
    if not _telling.a_verdict_names_what_told():
        return ""
    try:
        if isinstance(day_block, dict):
            if day_block.get("open") or day_block.get("banner"):
                return ""
            return str(day_block.get("verdict_told") or "")
        world = getattr(ctx, "world", None)
        atk, dfd = getattr(ctx, "marshal", None), getattr(ctx, "enemy_marshal", None)
        if world is None or atk is None or dfd is None:
            return ""
        player = getattr(world, "player_nation", None)
        if getattr(atk, "nation", None) == player:
            attacker_is_ours = True
        elif getattr(dfd, "nation", None) == player:
            attacker_is_ours = False
        else:
            return ""
        if _telling.the_day_speaks_plainly():
            # Row PW: the first cause WITH its numbers ("Why: he had more men —
            # 25,000 against your 12,000."); the rest ride the payload's `why`.
            why = _telling.why_plain(ctx, attacker_is_ours)
            if why:
                # (row PW part 2: who won, in two words, leads the cause)
                said = _telling.plain_verdict(ctx, attacker_is_ours)
                return (f"{said} " if said else "") + f"Why: {why[0]}."
        return _telling.verdict_line(_what_told_in_it(ctx, attacker_is_ours),
                                     broke=_whose_line_broke(ctx))
    except Exception as exc:
        report(exc, "battle_day.the_verdicts_line")
        return ""


def speaks_plainly() -> bool:
    """Row PW: the battle's words are the everyday ones (`battle_telling.
    the_day_speaks_plainly`) — the tableau says so (`plain`), and the table's
    own captions follow it."""
    return bool(_telling.the_day_speaks_plainly())


def the_whys(ctx) -> List[str]:
    """Row PW: every cause of a battle the player's marshal led a side of, in
    plain words with its numbers (`battle_telling.why_plain`) — [] for a
    battle he led no side of, or with the plain seam down."""
    if not _telling.the_day_speaks_plainly():
        return []
    try:
        world = getattr(ctx, "world", None)
        atk, dfd = getattr(ctx, "marshal", None), getattr(ctx, "enemy_marshal", None)
        if world is None or atk is None or dfd is None:
            return []
        player = getattr(world, "player_nation", None)
        if getattr(atk, "nation", None) == player:
            return _telling.why_plain(ctx, True)
        if getattr(dfd, "nation", None) == player:
            return _telling.why_plain(ctx, False)
    except Exception as exc:
        report(exc, "battle_day.the_whys")
    return []


def _after_the_battle(ctx) -> Optional[dict]:
    world = getattr(ctx, "world", None)
    if not _on(world):
        return None
    atk, dfd = getattr(ctx, "marshal", None), getattr(ctx, "enemy_marshal", None)
    if atk is None or dfd is None:
        return None
    player = getattr(world, "player_nation", None)
    if getattr(atk, "nation", None) == player:
        attacker_is_ours, ours, his = True, atk, dfd
    elif getattr(dfd, "nation", None) == player:
        attacker_is_ours, ours, his = False, dfd, atk
    else:
        return None
    word = _word_for(ctx)
    days = _store(world)["days"]
    key = str(word["key"]) if (word and word.get("key") in days) else his.name
    day = days.get(key)
    hanging = _hangs(ctx)

    if day is None:
        _ALONE.set(None)                                # no line of an earlier battle is carried over
        if not days and not world.battle_days.get("barred"):
            world.battle_days = {}                      # nothing opened: leave no trace
        region = str(getattr(ctx, "battle_region_name", "") or his.location)
        held = _held_on_this_ground(world, ours.name, region)
        if held is not None:
            # A battle our lead fought on his open day's own ground against
            # another corps: by its name a further clash of that battle
            # (`the_clashs_name`), so it is counted with it.
            _count_the_clash(held, _read(ctx, attacker_is_ours))
        if not hanging or int(getattr(ctx, "total_engaged_strength", 0) or 0) < key_bar(world):
            if held is None:
                _keep_his_battle(world, ctx, ours, his, attacker_is_ours, hanging)     # BA-5
            return None
        mine = the_day_he_holds(world, ours.name)
        marched = False
        if mine is None:
            # BA5-X1: the day he held when this battle BEGAN — his own advance
            # from it has since moved him off that day's ground
            kept = str(getattr(ctx, "_bd_day_held", "") or "")
            if kept and kept != his.name:
                mine = days.get(kept)
                # (the review) ...and the same response ends it (`his_first_day_ends`)
                marched = mine is not None and _he_marched_from_it(world, mine)
        if mine is not None:
            if held is None:
                _keep_his_battle(world, ctx, ours, his, attacker_is_ours, hanging)     # BA-5
            # BA3-X15: one day a lead. The clash is told as a battle is
            # told, and its script says why it opens no day.
            _ALONE.set({"pair": (atk.name, dfd.name), "line": (
                f"{_shown(ours.name)} has marched from his day against {_shown(mine.get('enemy'))}, "
                f"which ends where it stands — this clash opens none of its own." if marched else
                f"{_shown(ours.name)}'s day against {_shown(mine.get('enemy'))} is still "
                f"open — this clash opens none of its own.")})
            return None
        day = {
            "enemy": his.name, "lead": ours.name,
            "field": str(getattr(ctx, "battle_region_name", "") or his.location),
            "our_ground": ours.location, "his_ground": his.location,
            "side": "attack" if attacker_is_ours else "defence",
            "ours": points_for(ours), "theirs": points_for(his),
            "ours_of": points_for(ours), "theirs_of": points_for(his),
            # The side that did not open speaks first.
            "awaits": "theirs" if attacker_is_ours else "ours",
            "silences": 0, "words": 0,
            "turn": int(getattr(world, "current_turn", 0) or 0),
            "offered": False,
        }
        _store(world)["days"][his.name] = day
        day["read"] = _read(ctx, attacker_is_ours)
        _count_him(day, his)
        if a_day_is_one_battle():
            # The BATTLE's name: a day opened by a clash that was itself told
            # as a further clash of another day (two days a lead, BA3-X15's
            # seam down) is not named for that clash.
            day["name"] = the_battle_of(getattr(ctx, "battle_name", ""))
        _count_the_clash(day, day["read"], opening=True)
        if _telling.the_day_tells_its_clashes():
            # BA-5: the opening, in one line — how it stood and what told.
            _tell(day, "clash", _telling.clash_line(
                day["read"], _shown(atk.name),
                _telling.what_told(ctx, attacker_is_ours, day["read"].get("ahead", "even")),
                opening=True), "clash")
        return block(world, day, chips=False)

    # A later clash of an open day: the word's price, the Guard's recoil, the turn.
    day["words"] = int(day.get("words", 0)) + 1
    recoiled = _guard_recoil(ctx, word)
    if word and not word.get("taken"):
        _take(day, "ours" if word.get("who") == "ours" else "theirs", int(word.get("price", 0)))
        word["taken"] = True
    day["read"] = _read(ctx, attacker_is_ours)
    _count_the_clash(day, day["read"])
    _count_him(day, his)
    if recoiled:
        day["read"]["guard_thrown_back"] = True
    if not hanging:
        if _telling.the_close_names_what_told() or a_marshal_keeps_his_days():
            # BA-5: whom the clash decided it for, and what told in it (the
            # close says it; the lead's own record keeps it).
            day["decided_for"] = _telling.decided_for(ctx, attacker_is_ours)
            day["decided_by"] = _telling.what_told(ctx, attacker_is_ours, day["decided_for"])
        if _telling.the_close_names_what_told():
            pursued = (getattr(ctx, "battle_result", None) or {}).get("reserve_pursuit")
            if isinstance(pursued, dict) and int(pursued.get("men", 0) or 0) > 0:
                # the reserve pursued the lead this clash drove off (the engine's
                # own pursuit step applied it): whose, by the side that attacked
                day["reserve_pursued"] = {
                    "men": int(pursued["men"]), "points": int(pursued.get("points", 0) or 0),
                    "by": ("ours" if (pursued.get("side") == "defender") == attacker_is_ours
                           else "theirs")}
            if word:
                # The deciding word is told on the closing block, after the
                # day is gone: its place in the day's words is kept here.
                day.setdefault("said", []).append(
                    ["ours" if word.get("who") == "ours" else "theirs", str(word.get("kind") or "")])
        if _telling.a_verdict_names_what_told():
            # BA-5: the deciding clash's own table names the clash, and what
            # told in it (the day builds no panel there: that clash's verdict stands)
            told_by = str(day.get("decided_by") or "") or _telling.what_told(
                ctx, attacker_is_ours, _telling.decided_for(ctx, attacker_is_ours))
            fought = int(day.get("clashes", 0) or 0)
            day["verdict_told"] = _telling.verdict_line(
                told_by, _ordinal(fought) if fought > 1 else "", _whose_line_broke(ctx))
        return _close(world, key, "decided")
    if _telling.the_day_tells_its_clashes():
        # BA-5: this clash's own line, told after the word that fought it.
        line = _telling.clash_line(
            day["read"], _shown(atk.name),
            _telling.what_told(ctx, attacker_is_ours, day["read"].get("ahead", "even")))
        if word:
            day["clash_line"] = line
        else:
            # (the review) an attack that is no word of the day (no purse for it,
            # the day not ours to speak, a question waiting) is counted in the
            # day's toll: its line is told now — nothing else would tell it, and
            # the next word's clash would have taken its place
            _tell(day, "clash", line, "clash")
    # The ground moves with the corps: a clash won on points carries the
    # attacker onto the field.
    lead_now, foe_now = world.get_marshal(day.get("lead")), world.get_marshal(day.get("enemy"))
    if lead_now is not None and foe_now is not None:
        day["our_ground"], day["his_ground"] = lead_now.location, foe_now.location
    day["field"] = str(getattr(ctx, "battle_region_name", "") or day.get("field"))
    day["awaits"] = "theirs" if attacker_is_ours else "ours"
    return block(world, day, chips=False)


def _our_guns_told(world, day: dict, word: dict) -> None:
    """BA-5: our guns have told on him and the cannonade's own table shows it —
    the day's count of him (`_count_him`) follows it DOWN, never up (a corps
    that joined him out of sight is not read back)."""
    if word.get("kind") != "cannonade" or int(day.get("his_men", 0) or 0) <= 0:
        return
    foe = world.get_marshal(day.get("enemy"))
    if foe is not None:
        day["his_men"] = min(int(day["his_men"]), int(getattr(foe, "strength", 0) or 0))


def _count_him(day: dict, his) -> None:
    """BA-5: his lead's men as this clash's table counts them (the battle's own
    report gives the player who fought it both sides to the man) — kept for
    the cards of the day (`the_offer`), where the map's own sighting of his
    province may be only a band. Kept only where a word says what it does."""
    if not _telling.a_word_says_what_it_does():
        return
    if getattr(his, "name", None) == day.get("enemy"):
        day["his_men"] = int(getattr(his, "strength", 0) or 0)


def _held_on_this_ground(world, lead_name, region) -> Optional[dict]:
    """The open day `lead_name` holds on the ground a battle was fought on —
    the day's field or the ground our lead stands on — or None."""
    for day in open_days(world).values():
        if day.get("lead") == lead_name and region and region in (
                day.get("our_ground"), day.get("his_ground")):
            return day
    return None


def _the_day_of_this_clash(world, ctx) -> Optional[dict]:
    """The open day a battle is a FURTHER clash of, or None: the day its word
    belongs to; else the day we hold against the corps it was fought with
    (`_after_the_battle`'s own test); else the day our lead holds on the
    ground it was fought on (a clash against another corps of his)."""
    atk, dfd = getattr(ctx, "marshal", None), getattr(ctx, "enemy_marshal", None)
    if atk is None or dfd is None:
        return None
    player = getattr(world, "player_nation", None)
    if getattr(atk, "nation", None) == player:
        ours, his = atk, dfd
    elif getattr(dfd, "nation", None) == player:
        ours, his = dfd, atk
    else:
        return None
    days = open_days(world)
    word = _word_for(ctx)
    key = str(word["key"]) if (word and word.get("key") in days) else his.name
    if key in days:
        return days[key]
    return _held_on_this_ground(world, ours.name, str(getattr(ctx, "target_location", "") or ""))


def later_clashes_key(world, region) -> str:
    """The key, beside a province's own in `world.battle_counts`, under which
    the later clashes of a day fought there are counted (no province carries
    it — the Admiralty's "decisive actions at sea" is the precedent)."""
    return str(region or "") + str(getattr(world, "DAY_CLASHES_SUFFIX", " (later clashes of a day)"))


def the_battle_of(name) -> str:
    """A clash's name without its clash: "The Great Battle of Swabia — the
    second clash" is the Great Battle of Swabia (for a sentence about the
    battle — the campaign's reckoning)."""
    return str(name or "").split(" — the ", 1)[0]


def the_clashs_name(ctx, composed: str) -> str:
    """Row BA, BA-4 ("one name for a day") — the battle record's hook
    (`combat_executor._attack_battle_record`, right after the province's
    count has named the battle `composed`). A further clash of an open day is
    told under the DAY's name: "<the day's name> — the second clash"; the
    table's plate keeps the day's name alone (`battle_plate`: one name on the
    table for the whole day). The province's count has advanced as it always
    did; the clash is counted beside it so the next battle fought there takes
    the next ordinal, not the one after. Every other battle: `composed`."""
    try:
        world = getattr(ctx, "world", None)
        if not _on(world) or not a_day_is_one_battle():
            return composed
        day = _the_day_of_this_clash(world, ctx)
        if day is None or not day.get("name"):
            return composed
        nth = int(day.get("clashes", 1) or 1) + 1
        counts = world.battle_counts
        key = later_clashes_key(world, getattr(ctx, "target_location", ""))
        counts[key] = int(counts.get(key, 0) or 0) + 1
        result = getattr(ctx, "battle_result", None)
        if isinstance(result, dict):
            result["battle_plate"] = str(day["name"])
        return f"{day['name']} — the {_ordinal(nth)} clash"
    except Exception as exc:
        report(exc, "battle_day.the_clashs_name")
        return composed


# ════════════════════════════════════════════════════════
# A word: recognised, lent its price, taken from the purse
# ════════════════════════════════════════════════════════

def classify_word(world, parsed) -> Optional[dict]:
    """Is this order a word of an open day that awaits us? → {key, kind, price,
    who: "ours", marshal}, or None (an ordinary order, priced as ever).

    A word is recognised by WHAT IT IS — an attack on the day's enemy lead, the
    lead's `defend`, the lead's `retreat` (the table's "Fall back" on a day he
    defends; on a day he opened it ends his attack the same way: he has left
    the field), a SUPPORT order for the lead the table offers — never by a
    flag the client sends."""
    if not _on(world) or not isinstance(parsed, dict):
        return None
    days = open_days(world)
    if not days:
        return None
    command = parsed.get("command") if isinstance(parsed.get("command"), dict) else parsed
    action = str(command.get("action") or "").lower()
    who = world.get_marshal(command.get("marshal") or "") if command.get("marshal") else None
    if who is None or getattr(who, "nation", None) != getattr(world, "player_nation", None):
        return None
    target = str(command.get("target") or "")
    strategic = str(parsed.get("strategic_type") or command.get("strategic_type") or "").upper()

    def found(key, kind):
        day = days[key]
        if day.get("awaits") != "ours" or day.get("pending") or not _alive(world, day):
            return None
        price = int(PRICES[kind])
        if int(day.get("ours", 0)) < price:
            return None
        return {"key": key, "kind": kind, "price": price, "who": "ours", "marshal": who.name,
                "side": day.get("side")}

    # Two days may share a lead (two corps of his each fought ours to a
    # hanging day): a word binds to the first day that can TAKE it — the first
    # match alone turned the second day's lit chip into an ordinary order at an
    # action's price (BA3-X11, the review).
    if strategic == "SUPPORT" or action == "support":
        for key, day in days.items():
            if target and target.lower() in (str(day.get("lead", "")).lower(),
                                             _shown(day.get("lead")).lower()) and who.name != day.get("lead"):
                if not _the_order_brings_him(world, day, key, who):
                    continue          # an ordinary order, at an action: the day keeps its point
                hit = found(key, "bring_up")
                if hit:
                    return hit
        return None
    if parsed.get("is_strategic") or strategic:
        return None
    if action in ("attack", "charge"):
        foe = world.get_marshal(target) if target else None
        for key, day in days.items():
            if (foe is not None and foe.name == key) or target == day.get("his_ground"):
                if getattr(who, "artillery", False) and who.location != day.get("his_ground"):
                    hit = found(key, "cannonade")
                elif getattr(who, "is_sovereign", False) and the_guard_goes_in():
                    hit = found(key, "guard")
                else:
                    hit = found(key, "press" if who.name == day.get("lead") else "lead")
                if hit:
                    return hit
        return None
    if action == "defend":
        for key, day in days.items():
            if who.name == day.get("lead"):
                hit = found(key, "dig_in")
                if hit:
                    return hit
        return None
    if action == "retreat":
        # The lead's retreat ends his day on EITHER side (the session's
        # review, lane 3, asked whether a day we opened should take it: its
        # table offers "Break off", not "Fall back"). It should. A retreat
        # costs no action anywhere in the game, so the door gives nothing
        # away; and taken as the day's word it closes the day at once and
        # says so — "Ney fell back from Lorraine after two clashes" — where
        # an ordinary retreat would leave a day whose lead has gone standing
        # open until night, to close as "ended where it stood".
        for key, day in days.items():
            if who.name == day.get("lead"):
                hit = found(key, "break_off")
                if hit:
                    return hit
    return None


def a_brought_up_corps_is_one_the_table_offers() -> bool:
    """Row BA, BA-4 seam (the sibling of BA2-X7 on the day's own door, found
    by loading an old save in the real client): the day took EVERY support
    order for its lead as "a corps is brought up" — also one for a corps five
    provinces off, which the table does not offer: it spent a point of the
    day, told "Murat is ordered up." and gave the enemy his next word, for a
    march of three turns that no day will see. The taker now asks the plan's
    own reading (`order_quotes.the_order_brings`, the "Bring up" chip's): any
    other support order is an ordinary order at its ordinary price, and the
    day is not touched. Down (False): every support order for the lead is a
    word, as BA-3 took it."""
    return True


_WEIGHING: ContextVar[bool] = ContextVar("a_bring_up_is_being_weighed", default=False)


def _the_order_brings_him(world, day, key, who) -> bool:
    """Is `'<who>, support <the lead>'` the order this day's table offers as
    "Bring up <who>"? The plan's own reading, weighed as the chip's quote is
    weighed (the turn's pool refuses no word: `quoting_a_word`). The quote it
    weighs asks this question again for its own price — answered yes there
    (the price is not weighed in a delivery). An error reads as an ordinary
    order: it costs its action, as every order outside a day does."""
    if not a_brought_up_corps_is_one_the_table_offers() or _WEIGHING.get():
        return True
    lead, foe = world.get_marshal(day.get("lead") or ""), world.get_marshal(key)
    if lead is None or foe is None:
        return False
    weighing = _WEIGHING.set(True)
    try:
        from backend.commands import order_quotes as _quotes
        with quoting_a_word():
            return bool(_quotes.the_order_brings(world, lead, foe, who))
    except Exception as exc:
        report(exc, "battle_day._the_order_brings_him")
        return False
    finally:
        _WEIGHING.reset(weighing)


def a_word_is_quoted_in_points() -> bool:
    """BA3-X5 (row BA, BA-4) seam: a quote says a word's price. While a day is
    open the day's own chips priced a word in points, and every surface that
    quotes the SAME order outside them — the attack card, the plan's "Bring
    up" rows, the relay's note, the province's ordinary attack row, the
    readback — still said "1 action"; the order then took a point and no
    action. ONE source: where `classify_word` would take the quoted order,
    the quote says `ap: 0` and the price in the day's points. Display only —
    it moves no number. Down (False): the quotes as they were."""
    return True


def quoted_word(world, marshal_name, action: str, target: str = "",
                strategic_type: str = "") -> Optional[dict]:
    """BA3-X5: the word a QUOTE's order would be — `classify_word`'s own
    verdict for the order the quote names (an attack on the day's enemy, a
    SUPPORT order for its lead, the lead's defend or retreat), or None: an
    ordinary order at its ordinary price (no day open, the day awaits him, a
    question stands, or the purse cannot pay — a purse spent is not a wall).
    PURE: it reads the store and writes nothing."""
    if not a_word_is_quoted_in_points():
        return None
    parsed: Dict[str, Any] = {"command": {"marshal": marshal_name, "action": action,
                                          "target": target}}
    if strategic_type:
        parsed["strategic_type"], parsed["is_strategic"] = strategic_type, True
    return word_of(world, parsed)


def word_of(world, parsed) -> Optional[dict]:
    """BA3-X5: `classify_word` for a reader that holds the parser's own dict
    (the readback), under the same seam. PURE; an error is reported and reads
    as an ordinary order."""
    if not a_word_is_quoted_in_points():
        return None
    try:
        return classify_word(world, parsed)
    except Exception as exc:
        report(exc, "battle_day.word_of: classify_word")
        return None


_QUOTING: ContextVar[bool] = ContextVar("a_word_is_being_quoted", default=False)


@contextlib.contextmanager
def quoting_a_word():
    """BA3-X5: while a QUOTE of a word is built, the turn's action pool does
    not refuse it — a word costs no action. With no action left the attack
    card said "no military action left this turn" over an order the door
    would lend its actions and take. Nothing is lent here and nothing on the
    world is touched (a quote is read off the state lock's roads too): the
    one pool test (`state_probe._pool_reason`) reads this instead."""
    token = _QUOTING.set(True)
    try:
        yield
    finally:
        _QUOTING.reset(token)


def a_word_is_being_quoted() -> bool:
    return bool(_QUOTING.get())


def price_line(word: Optional[dict]) -> str:
    """A word's price in the player's words: "a word of the day — 1 point"
    ("— free" for a word that asks none: to fall back)."""
    points = int((word or {}).get("price", 0) or 0)
    if points <= 0:
        return "a word of the day — free"
    return f"a word of the day — {points} point{'s' if points != 1 else ''}"


@contextlib.contextmanager
def lending(world, word: Optional[dict] = None):
    """Lend an order the actions its gates ask for, and take every one back:
    a word of the day costs no action. `spent` on the yielded dict is what the
    order took from the pool while it ran (0: it was refused, or it asked).
    The temper's stream subtracts the lend (`campaign_variance.lent_now`), so
    a marshal's counsel on a chip is the temper the word then meets."""
    before = int(getattr(world, "actions_remaining", 0) or 0)
    lend_token = _cv.lend(LEND)
    word_token = _WORD.set(word) if word is not None else None
    world.actions_remaining = before + LEND
    meter = {"spent": 0, "before": before}
    try:
        yield meter
    finally:
        meter["spent"] = max(0, before + LEND - int(getattr(world, "actions_remaining", 0) or 0))
        world.actions_remaining = before
        _cv.unlend(lend_token)
        if word_token is not None:
            _WORD.reset(word_token)


def _ours_said(day, kind: str, who, foe="") -> str:
    """Our word's line. On a day HE opened, the lead's own attack is his
    riposte ("strikes back"); on a day we opened it presses the attack."""
    side = (day or {}).get("side") if isinstance(day, dict) else day
    if kind in ("press", "strike") and side == "defence":
        return "{who} strikes back.".format(who=_shown(who))
    template = _OUR_LINES.get("press" if kind == "strike" else kind, "{who} answers.")
    return template.format(who=_shown(who), foe=_shown(foe))


_OUR_LINES = {
    "press": "{who} presses the attack.",
    "lead": "{who} takes the lead.",
    "guard": "The Guard goes in.",
    "cannonade": "{who}'s guns open on {foe}'s line.",
    "bring_up": "{who} is ordered up.",
    "dig_in": "{who} digs in.",
    "break_off": "{who} falls back.",
    "falls_back_to": "{who} falls back toward {to}.",
    "own_way": "{who} goes his own way.",       # an objection answered his way, by no word of the day
}


def word_given(world, word: dict, result: dict, spent: int) -> None:
    """After a word's order has run: an objection parks it; a refusal costs
    nothing; an order that took is paid for in points."""
    day = day_against(world, word.get("key"))
    if day is None:
        if word.get("taken"):
            _tell_the_last(world, str(word.get("key")), "ours", _ours_said(
                word.get("side"), word["kind"], word.get("marshal"), word.get("key")), word["kind"])
        return
    took = (spent > 0 or bool(word.get("taken"))
            or (word["kind"] == "break_off" and bool(result.get("success"))))
    if not took and _asked(world, word, result):
        # An objection, or a question of the marshal's own (the muster's
        # "Commit the Attack?"): the word waits, nothing is paid, and its
        # answer runs on the day's account (`pending_word`, `answer_given`).
        parked_by = "objection" if questioner(world) == str(word.get("marshal") or "") else "question"
        day["pending"] = {"kind": word["kind"], "price": int(word["price"]),
                          "marshal": word.get("marshal"), "by": parked_by,
                          "order": _objected_order(world) if parked_by == "objection" else []}
        return
    day.pop("pending", None)
    if not took:
        return
    if word["kind"] == "break_off":
        _close(world, word["key"], "fell_back",
               _OUR_LINES["break_off"].format(who=_shown(word.get("marshal"))))
        return
    if not word.get("taken"):
        _take(day, "ours", int(word["price"]))
        word["taken"] = True
        day["words"] = int(day.get("words", 0)) + 1
        day["awaits"] = "theirs"
    _tell(day, "ours", _ours_said(day, word["kind"], word.get("marshal"), day.get("enemy")),
          word["kind"])
    _tell_the_clash(day)
    _our_guns_told(world, day, word)


def questioner(world) -> Optional[str]:
    """The marshal whose objection stands on the board (the tactical road's
    `pending_objection` or the strategic road's `pending_strategic_objection`),
    or None."""
    tactical = getattr(world, "pending_objection", None)
    if isinstance(tactical, dict) and tactical.get("marshal"):
        return str(tactical["marshal"])
    strategic = getattr(world, "pending_strategic_objection", None)
    if isinstance(strategic, dict) and (strategic.get("marshal_name") or strategic.get("marshal")):
        return str(strategic.get("marshal_name") or strategic.get("marshal"))
    return None


def _objected_order(world) -> list:
    """The order the standing objection is about, as [action, target] — its
    answer is the parked word's only when it is the objection the word raised."""
    tactical = getattr(world, "pending_objection", None)
    if isinstance(tactical, dict) and tactical.get("marshal"):
        order = tactical.get("original_order") if isinstance(tactical.get("original_order"), dict) else {}
        return [str(order.get("action") or "").lower(), str(order.get("target") or "").lower()]
    strategic = getattr(world, "pending_strategic_objection", None)
    if isinstance(strategic, dict):
        return [str(strategic.get("strategic_type") or "").lower(),
                str(strategic.get("target") or "").lower()]
    return []


def what_the_answer_runs(world, choice: str) -> Optional[dict]:
    """The order an objection's answer runs when it is NOT the order as given:
    the marshal's alternative ("trust") or the middle ground ("compromise"),
    read from the standing objection BEFORE it is answered. None: the order as
    given (insist, by my word), or nothing to read. PURE."""
    choice = str(choice or "").lower()
    if choice not in ("trust", "compromise"):
        return None
    tactical = getattr(world, "pending_objection", None)
    if isinstance(tactical, dict) and tactical.get("marshal"):
        arm = tactical.get("suggested_alternative" if choice == "trust" else "compromise")
        return dict(arm) if isinstance(arm, dict) and arm.get("action") else None
    if isinstance(getattr(world, "pending_strategic_objection", None), dict):
        # The strategic road. Its middle ground is the SAME order with a term
        # to it (a timed SUPPORT): the corps is still ordered up — the word as
        # given. Trusting him is his own way: the order is not issued, or his
        # own counsel is.
        return {"action": "own_way"} if choice == "trust" else None
    return None


def the_word_that_runs(world, word: dict, ran: Optional[dict]) -> dict:
    """The parked word AS ITS ANSWER RUNS IT (BA3-X6, the review). The day
    bills the price the chip quoted; it TELLS — on the table and in the
    clash's own script — what the marshal then did: his attack is a clash of
    the day, a defensive stance is digging in, a retreat is falling back, and
    anything else is "his own way". Before this, a compromise that changed his
    stance was told "Ney presses the attack." and an alternative that fought a
    battle "Ney digs in.". A sovereign's attack by this road is no Guard: the
    Guard is the word that asks two points."""
    if not ran:
        return dict(word)
    day = day_against(world, word.get("key")) or {}
    who = world.get_marshal(word.get("marshal") or "")
    action = str(ran.get("action") or "").lower()
    target = str(ran.get("target") or "")
    stance = str(ran.get("target_stance") or (target if action == "stance_change" else "")).lower()
    kind = "own_way"
    if action in ("attack", "charge"):
        foe = world.get_marshal(target) if target else None
        if (foe is not None and foe.name == day.get("enemy")) or (target and target == day.get("his_ground")):
            if who is not None and getattr(who, "artillery", False) and who.location != day.get("his_ground"):
                kind = "cannonade"
            else:
                kind = "press" if (who is not None and who.name == day.get("lead")) else "lead"
    elif action == "defend" or (action == "stance_change" and stance == "defensive"):
        kind = "dig_in"
    elif action == "retreat":
        kind = "break_off"
    return dict(word, kind=kind)


def _asked(world, word: dict, result: dict) -> bool:
    """Has the WORD's own marshal raised a question instead of acting — his
    objection (on either road), or his own interrupt (the muster's
    confirmation)? A question some other marshal left standing is no part of
    this word: the word was simply not taken."""
    name = str(word.get("marshal") or "")
    if not name:
        return False
    if questioner(world) == name:
        return True
    who = world.get_marshal(name)
    return bool(who is not None and getattr(who, "pending_interrupt", None))


def pending_word(world, marshal: Optional[str] = None, by: Optional[str] = None) -> Optional[dict]:
    """The word a question parked, for the answer's own road. With `marshal`,
    only the word that marshal's question holds (an interrupt is his own).
    With `by` ("objection" | "question"), only a word THAT road parked, and
    for an objection only while the objection standing is the one the word
    raised: a word the muster's question parked is not answered by the answer
    to some other order's objection — that order then rode free, on the
    word's lend and at no point (BA3-X6, the review)."""
    for key, day in open_days(world).items():
        pending = day.get("pending")
        if not pending or (marshal is not None and pending.get("marshal") != marshal):
            continue
        parked_by = pending.get("by")
        if by is not None and parked_by is not None:
            if parked_by != by:
                continue
            if by == "objection" and pending.get("order") and list(pending["order"]) != _objected_order(world):
                continue
        return {"key": key, "kind": pending["kind"], "price": int(pending["price"]),
                "who": "ours", "marshal": pending.get("marshal"), "side": day.get("side")}
    return None


def answer_given(world, word: dict, result: dict, spent: int) -> None:
    """The objection answered (obeyed, his own way, or defied): if an order
    ran, the word is paid for; if it was withdrawn, nothing is."""
    day = day_against(world, word.get("key"))
    if day is None:
        if word.get("taken"):
            _tell_the_last(world, str(word.get("key")), "ours", _ours_said(
                word.get("side"), word["kind"], word.get("marshal"), word.get("key")), word["kind"])
        return
    if _asked(world, word, {}):
        return                                    # still asking
    day.pop("pending", None)
    left = word["kind"] == "break_off" and bool(result.get("success"))
    if spent <= 0 and not word.get("taken") and not left:
        return                                    # withdrawn: nothing is paid
    if left:
        # His answer was to leave the field (the objector's own alternative):
        # the day closes as a fall-back, told — it closed "over" with no line
        # and no banner (BA3-X6, the review).
        _close(world, word["key"], "fell_back",
               _OUR_LINES["break_off"].format(who=_shown(word.get("marshal"))))
        return
    if not word.get("taken"):
        _take(day, "ours", int(word["price"]))
        word["taken"] = True
        day["words"] = int(day.get("words", 0)) + 1
        day["awaits"] = "theirs"
    _tell(day, "ours", _ours_said(day, word["kind"], word.get("marshal"), day.get("enemy")),
          word["kind"])
    _tell_the_clash(day)
    _our_guns_told(world, day, word)


# ════════════════════════════════════════════════════════
# His answer (and ours, when a marshal is left to it)
# ════════════════════════════════════════════════════════

_HIS_LINES = {
    "strike": "{who} strikes back.",
    "strike_again": "{who} comes on again.",
    "guard": "{who} sends in his Guard.",
    "draw_off": "{who} draws off toward {to}.",
    "draws_off": "{who} draws off.",            # where he went is not ours to say (fog)
    "break_off": "{who} breaks off the attack.",
    "dig_in": "{who} digs in.",
    "bring_up": "{who} is reinforced: a fresh corps comes up.",
    "stand": "{who} stands his ground.",
}
NIGHT = "Night falls on an undecided field."


def _day_rng(world, day, who: str):
    """A day's own stream for a temper's mood: the campaign's where one is
    played on a rolled seed, else None (the module `random`)."""
    return _cv.temper_rng(world, "day", day.get("enemy"), day.get("lead"), who,
                          int(day.get("words", 0)), int(day.get("silences", 0)), saved=False)


@contextlib.contextmanager
def _the_days_own_score(world, day, marshal):
    """BA3-X14: while his word's order runs, what his AI draws to score it
    comes from a stream of the day's own (`enemy_ai.a_stream_of_its_own`) —
    the campaign's seed, the turn, his court, and the day as it stood when he
    spoke. His court's stream of the phase is not touched."""
    if not his_word_is_scored_from_the_day():
        yield
        return
    from backend.ai import enemy_ai
    with enemy_ai.a_stream_of_its_own(
            world, str(getattr(marshal, "nation", "") or ""), "day",
            day.get("enemy"), day.get("lead"),
            int(day.get("words", 0) or 0), int(day.get("silences", 0) or 0)):
        yield


def _speak(world, day, who: str, game_state, executor) -> Optional[dict]:
    """One word from `who` ("theirs", or "ours" for a lead left to it), decided
    by the engaged rule his AI already follows and run through the one
    executor. Returns {kind, line, diorama?}; the day may be closed by it."""
    from backend.ai.enemy_ai import EnemyAI
    key = day["enemy"]
    mine, yours = ("enemy", "lead") if who == "theirs" else ("lead", "enemy")
    marshal, foe = world.get_marshal(day[mine]), world.get_marshal(day[yours])
    opened = (day.get("side") == "defence") if who == "theirs" else (day.get("side") == "attack")
    ahead = (day.get("read") or {}).get("ahead", "even")
    behind = ahead == ("ours" if who == "theirs" else "theirs")
    purse = int(day.get(who, 0))
    if who == "theirs" and not the_enemy_spends_his():
        purse = 0
    ai = EnemyAI(executor)
    # A sovereign's renewed assault is the Guard, at the Guard's price — the
    # player's own chip, and the same for a lead left to it or an enemy's.
    guard = bool(getattr(marshal, "is_sovereign", False)) and the_guard_goes_in()
    choice = ai.the_days_word(marshal, foe, world, purse=purse, opened=opened, behind=behind,
                              rng=_day_rng(world, day, who),
                              strike_price=int(PRICES["guard" if guard else "strike"]))
    kind = str(choice.get("kind") or "stand")
    action = choice.get("action")
    price = int(PRICES.get(kind, 0))
    shown = _shown(marshal.name)
    reply: Dict[str, Any] = {"who": who, "kind": kind}

    if kind == "stand" or action is None:
        if kind == "break_off":
            reply["line"] = _HIS_LINES["break_off"].format(who=shown)
            _close(world, key, "broke_off", reply["line"],
                   banner="he_broke_off" if who == "theirs" else "broke_off")
            return reply
        day["silences"] = int(day.get("silences", 0)) + 1
        day["awaits"] = "ours" if who == "theirs" else "theirs"
        reply["kind"] = "stand"
        reply["line"] = _HIS_LINES["stand"].format(who=shown)
        _tell(day, who, reply["line"], "stand")
        return reply

    word = {"key": key, "kind": "guard" if (kind == "strike" and guard) else kind,
            "price": price, "who": who, "marshal": marshal.name, "side": day.get("side")}
    if word["kind"] == "guard":
        word["price"] = price = int(PRICES["guard"])
    token = _WORD.set(word)
    try:
        if who == "theirs":
            with _the_days_own_score(world, day, marshal):
                result = ai._execute_action(dict(action), game_state)
        else:
            # Our lead, left to it: his own decision — no objection to raise
            # against himself and no action to pay (the executor's own flag
            # for an order a marshal carries out on his own account).
            result = executor.execute({"command": {
                "marshal": action["marshal"], "action": action["action"],
                "target": action.get("target"), "type": "specific",
                "_strategic_execution": True}}, game_state)
    except Exception as exc:
        report(exc, "battle_day._speak: the word's own order")
        result = {"success": False}
    finally:
        _WORD.reset(token)
    if not result.get("success"):
        # The executor refused his order: he has stood.
        day = day_against(world, key)
        if day is not None:
            day["silences"] = int(day.get("silences", 0)) + 1
            day["awaits"] = "ours" if who == "theirs" else "theirs"
            reply.update(kind="stand", line=_HIS_LINES["stand"].format(who=shown))
            _tell(day, who, reply["line"], "stand")
        return reply

    day = day_against(world, key)
    reply["_result"] = result
    if kind == "strike":
        # The day HE opened, his first word's strike is already his second
        # assault: "comes on again", never a second "strikes back" under ours
        # (BA3-X10, the review).
        again = int((day or {}).get("strikes_" + who, 0)) > 0 or (who == "theirs" and opened)
        if who == "theirs":
            reply["line"] = _HIS_LINES["guard" if word["kind"] == "guard" else (
                "strike_again" if again else "strike")].format(who=shown)
        else:
            reply["line"] = _ours_said(
                (day or {}).get("side") or word.get("side"),
                "guard" if word["kind"] == "guard" else "press", marshal.name, foe.name)
        tableau = result.get("battle_diorama") or next(
            (e.get("diorama") for e in (result.get("events") or [])
             if isinstance(e, dict) and e.get("diorama")), None)
        if tableau:
            reply["diorama"] = tableau
        told_as = "press" if (who == "ours" and word["kind"] == "strike") else word["kind"]
        if day is not None:
            day["strikes_" + who] = int(day.get("strikes_" + who, 0)) + 1
            if not word.get("taken"):           # a clash that named no battle (never, by design)
                _take(day, who, price)
                day["awaits"] = "ours" if who == "theirs" else "theirs"
            _tell(day, who, reply["line"], told_as)
            _tell_the_clash(day)
        else:
            _tell_the_last(world, key, who, reply["line"], told_as)
        return reply
    if kind == "draw_off":
        to = choice.get("to")
        if who == "theirs":
            # Fog (SYSTEMS_REFERENCE §219.2, case 2 — "never where to"): the
            # province he went to is named only when the game's one sighting
            # rule shows him there. Else the line would place an unseen corps
            # on the map (BA3-X9, the review: a won cannonade, the lead not on
            # the field, "Mack draws off toward Vienna").
            seen = any(m.name == marshal.name
                       for m in world.get_visible_enemies(getattr(world, "player_nation", "")))
            reply["line"] = (_HIS_LINES["draw_off"].format(who=shown, to=_place(world, to))
                             if (seen and to) else _HIS_LINES["draws_off"].format(who=shown))
            _close(world, key, "drew_off", reply["line"])
        else:
            # OUR lead, left to it, leaves the field: he FALLS BACK — the
            # day's own word for it and its own banner. The enemy's
            # ("Mack draws off") stood over it (BA3-X8, the review).
            reply["line"] = _OUR_LINES["falls_back_to"].format(who=shown, to=_place(world, to))
            _close(world, key, "fell_back", reply["line"])
        return reply
    # dig in / bring up: a priced word that is no clash
    if day is not None:
        _take(day, who, price)
        day["words"] = int(day.get("words", 0)) + 1
        day["awaits"] = "ours" if who == "theirs" else "theirs"
        reply["line"] = (_HIS_LINES if who == "theirs" else _OUR_LINES)[kind].format(
            who=shown, foe=_shown(foe.name))
        _tell(day, who, reply["line"], kind)
    return reply


def _spent(world, key) -> Optional[dict]:
    """Night falls when both purses are empty or two silences have followed
    one another. Returns the closing block, or None (the day goes on)."""
    day = day_against(world, key)
    if day is None:
        return None
    if not _alive(world, day):
        return _close(world, key, "over")
    if int(day.get("silences", 0)) >= 2 or (int(day.get("ours", 0)) <= 0
                                             and int(day.get("theirs", 0)) <= 0):
        return _close(world, key, "night", NIGHT)
    return None


def his_answer(world, game_state, executor, only: Optional[str] = None) -> Dict[str, dict]:
    """Run every day that awaits HIM until it awaits us or night has fallen.
    Returns {enemy: reply} — the last word he said in each (its tableau held
    beside the world until the table reads it)."""
    replies: Dict[str, dict] = {}
    if not _on(world):
        return replies
    for key in list(open_days(world)):
        if only is not None and key != only:
            continue
        for _ in range(TURNS_CAP):
            day = day_against(world, key)
            if day is None or day.get("awaits") != "theirs" or day.get("pending"):
                break
            if _spent(world, key) is not None:
                break
            reply = _public(_speak(world, day, "theirs", game_state, executor))
            if reply:
                replies[key] = reply
                if reply.get("diorama"):
                    _TABLEAUX.setdefault(world, {})[key] = reply["diorama"]
            if _spent(world, key) is not None:
                break
    return replies


def our_silence(world, key, game_state, executor) -> Optional[dict]:
    """We stand: a silence. Then he speaks."""
    day = day_against(world, key)
    if day is None or day.get("awaits") != "ours" or day.get("pending"):
        return None
    day["silences"] = int(day.get("silences", 0)) + 1
    day["awaits"] = "theirs"
    _tell(day, "ours", f"{_shown(day.get('lead'))} stands.", "stand")
    if _spent(world, key) is None:
        his_answer(world, game_state, executor, only=key)
    return None


def we_break_off(world, key) -> Optional[dict]:
    """We opened and we leave it: the day is over where it stands."""
    day = day_against(world, key)
    if day is None or day.get("awaits") != "ours" or day.get("side") != "attack":
        return None
    return _close(world, key, "broke_off", "You break off the attack.")


def leave_it(world, key, game_state, executor, keep: bool = False) -> List[dict]:
    """"Leave it to him": the lead spends what is left by his own temper, and
    the enemy answers by his, until night. Returns every word said (`keep`:
    with each word's own executor result under `_result`, for `say`)."""
    said: List[dict] = []
    if not a_marshal_may_be_left_to_it():
        return said
    for _ in range(TURNS_CAP):
        day = day_against(world, key)
        if day is None or day.get("pending"):
            break
        if _spent(world, key) is not None:
            break
        who = "ours" if day.get("awaits") == "ours" else "theirs"
        raw = _speak(world, day, who, game_state, executor)
        reply = raw if keep else _public(raw)
        if reply:
            said.append(reply)
            if reply.get("diorama"):
                _TABLEAUX.setdefault(world, {})[key] = reply["diorama"]
    _spent(world, key)
    return said


def _public(reply: Optional[dict]) -> Optional[dict]:
    return None if reply is None else {k: v for k, v in reply.items() if not k.startswith("_")}


def settle(world, game_state, executor, result, *, word: Optional[dict] = None,
           spent: int = 0, answered: bool = False) -> None:
    """After an order has run on the served road: a word is paid for, he
    answers where the day now awaits him, and the day as it stands is written
    onto the result — `battle_day` (with his `reply`: kind, line, and the
    tableau of his clash when he struck) and the tableau's own `day`."""
    if not _on(world) or not isinstance(result, dict):
        return
    key = ""
    if word is not None:
        key = str(word["key"])
        (answer_given if answered else word_given)(world, word, result, int(spent))
        if isinstance(result.get("action_info"), dict):
            result["action_info"] = world.get_action_info(0)   # a word costs no action
        if "action_summary" in result:
            # The executor wrote it with the lend still on the pool: the
            # muster's question read 6 actions of 4 and its answer 5 (found in
            # the real client, whose counter is this field). The pool as it is.
            result["action_summary"] = world.get_action_summary()
    payload = result.get("battle_diorama")
    if not key and isinstance(payload, dict) and isinstance(payload.get("day"), dict):
        key = str(payload["day"].get("enemy") or "")
    if not key:
        return
    # BA5-D1: the day as it stood when OUR clash ended, read before he answers
    # (a day our own clash closed has no such reading: he says nothing more).
    before = None
    if our_table_reads_the_day_as_our_clash_left_it():
        standing = day_against(world, key)
        if standing is not None:
            before = block(world, standing, chips=False)
    replies = his_answer(world, game_state, executor, only=key)
    _spent(world, key)
    day = day_against(world, key)
    live = block(world, day) if day is not None else (_CLOSED.get(world) or {}).pop(key, None)
    if live is None:
        return
    (_CLOSED.get(world) or {}).pop(key, None)
    reply = _public(replies.get(key))
    plain = dict(live)
    if reply:
        tableau_for(world, key)                      # delivered here, not held
        plain["reply"] = {k: v for k, v in reply.items() if k != "diorama"}
        if isinstance(reply.get("diorama"), dict):
            reply["diorama"]["day"] = dict(plain)
        live["reply"] = reply
    result["battle_day"] = live
    if isinstance(payload, dict):
        if reply and isinstance(reply.get("diorama"), dict):
            # HIS clash follows ours on the table: our tableau tells the day as
            # it stood when our clash ended — no chips; the live ones ride his.
            # (BA5-D1: `plain` is the day AFTER his answer — his purse a point
            # short, his word told, the line under the title his clash's — and
            # it stood on our clash's table before "His answer" was pressed.)
            payload["day"] = dict(before if before is not None else plain, chips=[], follows=True)
        else:
            payload["day"] = plain


def say(world, key: str, what: str, game_state, executor) -> dict:
    """A word that is no order — `stand`, `break_off` (a day we opened),
    `leave_it` — for `POST /battle_day/word`. Returns {success, message,
    battle_day, battle_diorama?}."""
    day = day_against(world, key)
    if not _on(world) or day is None:
        return {"success": False, "message": "No day of battle is open there."}
    if day.get("awaits") != "ours" or day.get("pending"):
        return {"success": False, "message": "The day does not await your word."}
    said: List[dict] = []
    carried: Optional[dict] = None
    if what == "stand":
        our_silence(world, key, game_state, executor)
    elif what == "break_off":
        if we_break_off(world, key) is None:
            return {"success": False, "message": "This day is not yours to break off."}
    elif what == "leave_it":
        if not a_marshal_may_be_left_to_it():
            return {"success": False, "message": "The day's words are yours to give."}
        said = leave_it(world, key, game_state, executor, keep=True)
        # The last clash OUR lead fought: whatever it left to ask (a captured
        # town's "plunder or secure") must reach the player with this answer.
        carried = next((r.get("_result") for r in reversed(said)
                        if r.get("who") == "ours" and isinstance(r.get("_result"), dict)
                        and r.get("diorama")), None)
        said = [_public(r) for r in said]
    else:
        return {"success": False, "message": f"Unknown word: {what}"}
    _spent(world, key)
    day = day_against(world, key)
    live = block(world, day) if day is not None else (_CLOSED.get(world) or {}).pop(key, None)
    (_CLOSED.get(world) or {}).pop(key, None)
    out: Dict[str, Any] = {"success": True, "battle_day": live or {"open": False, "enemy": key}}
    tableau = tableau_for(world, key)
    if tableau is None:
        tableau = next((r.get("diorama") for r in reversed(said) if r.get("diorama")), None)
    if isinstance(tableau, dict) and live is not None:
        tableau["day"] = dict(live)
        out["battle_diorama"] = tableau
    told = (live or {}).get("told") or []
    out["message"] = " ".join(str(t.get("line") or "") for t in told[-3:]).strip() or "The day is over."
    if carried is not None:
        out["_carry"] = carried
    return out


# ════════════════════════════════════════════════════════
# Night and dawn (turn_manager.end_turn)
# ════════════════════════════════════════════════════════

def night_falls(world, game_state, executor) -> List[dict]:
    """The turn is closing: every day still open is played out with our
    silence — he spends what he has left — and the pair is barred from a
    second strike in the phase that follows. Returns the executor's own
    results of what he did (each with its `ai_action`), for the phase's own
    telling (`turn_manager.end_turn` puts them at the head of his court's)."""
    said: List[dict] = []
    if not _on(world) or not open_days(world):
        return said
    night = _IN_THE_NIGHT.set(True)
    try:
        for key in list(open_days(world)):
            day = day_against(world, key)
            if day is None:
                continue
            lead = day.get("lead")
            # BA3-X13: was it still a day when night began?
            a_day_at_nightfall = _alive(world, day) or not a_dead_day_bars_nothing()
            day.pop("pending", None)
            first = len(said)
            for _ in range(TURNS_CAP):
                day = day_against(world, key)
                if day is None:
                    break
                if _spent(world, key) is not None:
                    break
                if day.get("awaits") == "ours":
                    day["silences"] = int(day.get("silences", 0)) + 1
                    day["awaits"] = "theirs"
                    continue
                reply = _speak(world, day, "theirs", game_state, executor)
                if reply and isinstance(reply.get("_result"), dict) and reply.get("kind") != "stand":
                    said.append(reply["_result"])
            if day_against(world, key) is not None:
                _close(world, key, "night", NIGHT)
            _the_end_on_the_last(world, key, said[first:])
            if a_day_at_nightfall:
                _store(world).setdefault("barred", {})[key] = lead
    finally:
        _IN_THE_NIGHT.reset(night)
    (_CLOSED.get(world) or {}).clear()
    (_TABLEAUX.get(world) or {}).clear()
    return said


def _tableaux_of(result) -> List[dict]:
    """The tableaux one executor result carries: its own and its events'."""
    if not isinstance(result, dict):
        return []
    found = [result.get("battle_diorama")]
    found += [event.get("diorama") for event in result.get("events") or [] if isinstance(event, dict)]
    return [t for t in found if isinstance(t, dict)]


def _the_end_on_the_last(world, key: str, struck: List[dict]) -> None:
    """A day closed in the night otherwise than by a clash that decided it
    (night fell; his line gave way to no blow): the tableau of his LAST clash
    of that night tells it — it carried the day as it stood after the clash,
    still open. A deciding clash wrote its own closing block."""
    closing = (_CLOSED.get(world) or {}).get(str(key))
    if closing is None or closing.get("ended") == "decided":
        return
    last = next((r for r in reversed(struck) if any(
        isinstance(t.get("day"), dict) for t in _tableaux_of(r))), None)
    for tableau in _tableaux_of(last):
        if isinstance(tableau.get("day"), dict):
            tableau["day"] = {k: v for k, v in closing.items() if k != "reply"}


def awaiting(world) -> List[dict]:
    """Every open day that awaits OUR word with no question out — what ending
    the turn now would settle by our silence (he then spends what he has left
    and night falls). For the end-turn gate, beside the unanswered envoys and
    the last stands. PURE; [] off the served road."""
    out: List[dict] = []
    if not _on(world):
        return out
    for key, day in open_days(world).items():
        if not isinstance(day, dict) or day.get("awaits") != "ours" or day.get("pending"):
            continue
        if not _alive(world, day):
            # The lead has marched off, a corps is gone, or peace is made: the
            # end-turn gate named a day that was already over (BA3-X7).
            continue
        out.append({
            "enemy": day.get("enemy") or key, "enemy_shown": _shown(day.get("enemy") or key),
            "lead": day.get("lead"), "lead_shown": _shown(day.get("lead")),
            "field": day.get("field"), "field_shown": _place(world, day.get("field")),
            "side": day.get("side"), "ours": int(day.get("ours", 0)),
        })
    return out


def living(world) -> List[str]:
    """The enemy key of every day still open AND alive — for the client, which
    keeps each day's last block (and its chips, in old log lines too) and has
    no other way to learn that a day ended unseen: night fell at the turn's
    end, or its lead marched off the field. A chip of such a day stayed lit
    on the next turn; pressed, it sent its order, which with no day open ran
    at an action's price (BA3-X18, the review — shown in the real client).
    PURE; [] off the served road."""
    if not _on(world):
        return []
    return [str(key) for key, day in open_days(world).items()
            if isinstance(day, dict) and _alive(world, day)]


def bars(world) -> set:
    """The (striker, target) pairs a day's night barred for the phase that
    follows — read into the AI's own pair brake (`enemy_ai`)."""
    store = getattr(world, "battle_days", None)
    if not isinstance(store, dict):
        return set()
    return {(str(striker), str(target)) for striker, target in (store.get("barred") or {}).items()}


def at_dawn(world, game_state=None, executor=None) -> List[dict]:
    """The new turn: the night's bars are lifted, dead days are dropped, days
    the phase opened are offered (a notice each), and where he speaks first
    he has spoken."""
    offered: List[dict] = []
    store = getattr(world, "battle_days", None)
    if not isinstance(store, dict) or not store:
        return offered
    store.pop("barred", None)
    if not _on(world):
        world.battle_days = {}
        return offered
    # A day that closes HERE — its lead gone by morning, or his first word at
    # dawn ending it — is told in the morning as a day the night closed is
    # (the session's review, lane 3: it was logged and told nowhere; the
    # night's lines had been handed over before the dawn closed anything).
    dawn = _IN_THE_NIGHT.set(True)
    try:
        for key in list(open_days(world)):
            day = day_against(world, key)
            if not _alive(world, day):
                _close(world, key, "over")
                continue
            if day.get("awaits") == "theirs" and executor is not None:
                his_answer(world, game_state, executor, only=key)
                day = day_against(world, key)
                if day is None:
                    continue
            if not day.get("offered"):
                day["offered"] = True
                offered.append(block(world, day, chips=False))
                _notice(world, day)
    finally:
        _IN_THE_NIGHT.reset(dawn)
    if not open_days(world):
        world.battle_days = {}
    return offered


def dawn_on_the_tableaux(world, phase) -> None:
    """The tableau the enemy phase's telling carries for a day is the table
    that rises by itself when the phase's list is left — so at dawn it carries
    the day AS IT STANDS AT DAWN, chips and all: on each action's
    `battle_diorama` and on each event's `diorama`. A day that did not live to
    the dawn leaves no block on its earlier clash, which is then told as the
    battle it was. Found in the real client: the table rose with both purses
    and no word to give (the block was the one written at the battle, before
    the day was offered)."""
    if not _on(world) or not isinstance(phase, dict):
        return
    live: Dict[str, Optional[dict]] = {}

    def at_dawn_it_reads(payload) -> None:
        if not isinstance(payload, dict) or not isinstance(payload.get("day"), dict):
            return
        if payload["day"].get("open") is False:
            return                  # a closing block tells how the day ended: it stands
        key = str(payload["day"].get("enemy") or "")
        if key not in live:
            day = day_against(world, key)
            live[key] = block(world, day) if day is not None else None
        if live[key] is None:
            payload.pop("day", None)
        else:
            payload["day"] = dict(live[key])

    for row in (phase.get("nations") or {}).values():
        for action in (row.get("actions") if isinstance(row, dict) else None) or []:
            for tableau in _tableaux_of(action):
                at_dawn_it_reads(tableau)


def _notice(world, day) -> None:
    try:
        from backend.notifications import (
            BATTLE_DAY_AWAITS, NotificationPriority, create_notification,
        )
        lead, foe = _shown(day.get("lead")), _shown(day.get("enemy"))
        left = int(day.get("ours", 0))
        title = f"The day at {_place(world, day.get('field'))} hangs"
        message = (f"{foe} and {lead} fought to no decision. The day is yours to answer: "
                   f"{left} point{'s' if left != 1 else ''} to spend.")
        if _telling.the_day_speaks_plainly():
            # Row PW (plain words): the notice says what happened and what is
            # asked of the player ("The day at Franconia hangs … the day is
            # yours to answer" told a first reader neither).
            title = f"Battle at {_place(world, day.get('field'))}: no winner yet"
            message = (f"{foe} and {lead} fought and neither won. The battle waits for your "
                       f"orders: {left} battle point{'s' if left != 1 else ''} to spend.")
        world.notifications.add(create_notification(
            notification_type=BATTLE_DAY_AWAITS,
            priority=NotificationPriority.HIGH,
            title=title,
            message=message,
            turn_created=int(getattr(world, "current_turn", 0) or 0),
            details={"marshal": day.get("lead"), "enemy": day.get("enemy"),
                     "field": day.get("field")}))
    except Exception as exc:
        report(exc, "battle_day._notice")


# ════════════════════════════════════════════════════════
# What the table is told
# ════════════════════════════════════════════════════════

def tableau_for(world, key) -> Optional[dict]:
    """His last clash's tableau, if the table has not read it."""
    return (_TABLEAUX.get(world) or {}).pop(str(key or ""), None)


def _the_morning(day) -> str:
    """The line under the title. BA-5: the day's own toll so far and who has
    the better of it (`battle_telling.day_so_far`); with that seam down, or
    for a day that kept no count, how the last clash stood (`_morning`)."""
    if not day.get("read"):
        return ""
    if _telling.the_day_tells_its_clashes():
        said = _telling.day_so_far(day, _shown(day.get("enemy")))
        if said:
            return said
    return _morning(day)


def _morning(day) -> str:
    read = day.get("read") or {}
    ahead = read.get("ahead", "even")
    head = {"ours": "won on points", "theirs": "lost on points"}.get(ahead, "drawn")
    return (f"The last clash: {head} — {int(read.get('our_loss', 0)):,} of ours for "
            f"{int(read.get('his_loss', 0)):,} of his.")


def block(world, day: dict, *, chips: bool = True) -> dict:
    """The day as the table reads it. Fog: his purse is the commander's own
    figure (a great battle names its commander), his odds and his bar are
    never in it."""
    is_open = day.get("open", True) is not False and day.get("enemy") in open_days(world)
    out = {
        "open": bool(is_open),
        "enemy": day.get("enemy"), "enemy_shown": _shown(day.get("enemy")),
        "lead": day.get("lead"), "lead_shown": _shown(day.get("lead")),
        "field": day.get("field"), "field_shown": _place(world, day.get("field")),
        "side": day.get("side"),
        "ours": int(day.get("ours", 0)), "theirs": int(day.get("theirs", 0)),
        # What each purse held when the day opened (the pips' slots).
        "ours_of": int(day.get("ours_of", day.get("ours", 0))),
        "theirs_of": int(day.get("theirs_of", day.get("theirs", 0))),
        "awaits": day.get("awaits") if is_open else "",
        "pending": bool(day.get("pending")),
        "morning": _the_morning(day),
        "ahead": (day.get("read") or {}).get("ahead", "even"),
        "told": [dict(t) for t in (day.get("told") or [])],
        "ended": day.get("ended", ""),
        # The table's headline while the day is the story: an open day is not
        # a field won. "" leaves the clash's own verdict standing.
        "banner": BANNER_OPEN if is_open else str(day.get("banner", "") or ""),
        "chips": [],
    }
    # Row PW "Plain Words": the headline and the line under the title in
    # everyday words ("No winner yet" / "Losses so far: you … · him …"), and
    # the rule of the day in one plain sentence for the table's caption.
    if _telling.the_day_speaks_plainly():
        out["banner"] = _telling.plain_banner(out["banner"], out["enemy_shown"])
        if day.get("read") and _telling.the_day_tells_its_clashes():
            out["morning"] = (_telling.plain_so_far(dict(day, open=is_open), out["enemy_shown"])
                              or out["morning"])
        out["rule"] = _telling.PLAIN_RULE
    if day.get("close"):
        out["close"] = str(day["close"])        # BA-4: how the day ended, in one line
    if day.get("verdict_told"):
        out["verdict_told"] = str(day["verdict_told"])    # BA-5: under the deciding clash's headline
    if is_open:
        out.update(_what_the_field_shows_of_him(world, day))
        # BA-4: the first day of a campaign names its own rules, once
        # (`first_open`, the eleventh screen): attached while unlatched, on
        # this fresh dict — a day is not stored with it.
        from backend.game_logic import first_open as _first_open
        if _says_its_first_line(world, day):
            _first_open.attach(out, world, "battle_day")
    if is_open and chips and day.get("awaits") == "ours" and not day.get("pending"):
        try:
            out["chips"] = the_offer(world, day)
        except Exception as exc:
            report(exc, "battle_day.block: the_offer")
        if _telling.the_table_reads_him():
            # BA-5: Berthier's reading of his next word — only where a word is
            # ours to give, and only as far as the player can see.
            reading = _telling.reading_of(world, day)
            if reading:
                out["reading"] = reading
    return out


def _what_the_field_shows_of_him(world, day) -> dict:
    """His temper (the plinth already wears it: `battle_script.temper_of`) and
    whether a road is open behind him — read from the map every player sees
    (who holds the provinces beside him, where our own corps stand). Never his
    odds, his bar or his mood: those are his."""
    out: Dict[str, Any] = {"his_temper": "", "his_road": None}
    foe = world.get_marshal(day.get("enemy"))
    if foe is None:
        return out
    try:
        from backend.ai.enemy_ai import get_effective_ai_personality
        from backend.display_names import PERSONALITY_DISPLAY
        temper = str(get_effective_ai_personality(foe, world) or "")
        out["his_temper"] = str(PERSONALITY_DISPLAY.get(temper, temper.replace("_", " ").title()))
        # The day he opened he does not leave by a road: he breaks off.
        if day.get("side") == "attack":
            out["his_road"] = _his_road(world, foe)
    except Exception as exc:
        report(exc, "battle_day._what_the_field_shows_of_him")
    return out


def blocks(world, *, take_tableaux: bool = False) -> List[dict]:
    """Every open day's block, live. With `take_tableaux` (the table's own
    read, `GET /battle_day`) a block carries `reply_diorama` — his last
    clash's tableau, handed over once; the province panel's read leaves it."""
    out = []
    for key in list(open_days(world)):
        day = day_against(world, key)
        if day is None:
            continue
        if not _alive(world, day):
            _close(world, key, "over")
            (_CLOSED.get(world) or {}).pop(key, None)
            continue
        got = block(world, day)
        tableau = tableau_for(world, key) if take_tableaux else None
        if tableau:
            tableau["day"] = dict(got)
            got["reply_diorama"] = tableau
        out.append(got)
    return out


def awaits_him(world) -> bool:
    """Does any open day await HIS word with nothing pending? (The one case
    in which the table's read changes the board: `caught_up`.)"""
    return any(day.get("awaits") == "theirs" and not day.get("pending")
               for day in open_days(world).values())


def caught_up(world, game_state, executor) -> List[dict]:
    """For `GET /battle_day`: where a day awaits HIM by a road that did not
    carry his answer (a day opened by an interrupt's answer or a charge — the
    command road and the objection's answer settle at once), he answers now;
    then every open day, and the closing block of a day that answer closed."""
    waiting = [key for key, day in open_days(world).items()
               if day.get("awaits") == "theirs" and not day.get("pending")]
    if waiting and executor is not None and _on(world):
        his_answer(world, game_state, executor)
        for key in waiting:
            _spent(world, key)
    out = blocks(world, take_tableaux=True)
    for key in waiting:
        if key not in open_days(world):
            closing = (_CLOSED.get(world) or {}).pop(key, None)
            if closing is not None:
                tableau = tableau_for(world, key)
                if tableau:
                    tableau["day"] = dict(closing)
                    closing["reply_diorama"] = tableau
                out.append(closing)
    return out


def _chip(kind, label, *, command="", word="", ok=True, why="", counsel="none",
          odds="", who="", price=None) -> dict:
    return {"kind": kind, "label": label, "price": int(PRICES[kind] if price is None else price),
            "command": command, "word": word, "ok": bool(ok), "why": str(why or ""),
            "counsel": counsel, "odds": odds, "marshal": who, "shown": _shown(who) if who else ""}


def _does(chip: dict, does: str, more: str = "", risk: str = "") -> None:
    """BA-5: what the chip's word does — `does` for its face, `more` for its
    hover. With the seam down a chip carries neither key (BA-4's chip).
    BA-6: `risk`, what it is likely to bring (a card's third line)."""
    if _telling.a_word_says_what_it_does():
        chip["does"] = str(does or "")
        if more:
            chip["more"] = str(more)
        if risk:
            chip["risk"] = str(risk)


# One order for every surface (the table, the province panel, the log): the
# lead's own words first, then the Guard, then the others by kind, the exits
# last — "Leave it to him" last of all.
_CHIP_ORDER = ("press", "guard", "dig_in", "lead", "cannonade", "bring_up")


def _chip_rank(chip: dict) -> int:
    if chip.get("word") == "leave_it":
        return 99
    if chip.get("word") or chip.get("kind") in ("stand", "break_off"):
        return 50 if chip.get("kind") == "stand" else 51
    kind = chip.get("kind")
    return _CHIP_ORDER.index(kind) if kind in _CHIP_ORDER else 40


def the_offer(world, day) -> List[dict]:
    """The chips of a day that awaits us — built from the quotes the game
    already makes (`order_quotes`), read with the lend the words will have, so
    a chip is lit exactly when its order would be taken. PURE: the lend is
    returned before this returns."""
    from backend.commands import order_quotes as Q
    from backend.commands.state_probe import order_state_refusal
    chips: List[dict] = []
    lead, foe = world.get_marshal(day.get("lead")), world.get_marshal(day.get("enemy"))
    if lead is None or foe is None:
        return chips
    purse = int(day.get("ours", 0))
    spent_all = "The day's points are spent."

    def lit(price, refusal=""):
        if refusal:
            return False, refusal
        if purse < price:
            return False, (spent_all if purse <= 0 else f"That asks {price} points; {purse} is left.")
        return True, ""

    with lending(world):
        ours = [m for m in world.get_player_marshals() if _stands(m)]
        ours.sort(key=lambda m: (m.name != lead.name, m.name))
        for corps in ours:
            reach = world.get_distance(corps.location, foe.location)
            if reach is None or reach < 0 or reach > int(getattr(corps, "movement_range", 1) or 1):
                continue
            quote = Q.attack_quote(world, corps, foe)
            if quote.get("kind") != "attack":
                continue
            force = quote.get("force") or {}
            counted = int(day.get("his_men", 0) or 0)
            if counted > 0 and force and not (
                    int(force.get("theirs_low", 0) or 0) > 0
                    and force.get("theirs_low") == force.get("theirs_high")):
                # BA-5: the map's sighting of him is a band, but this day's own
                # table has counted him clash by clash — the card says the
                # figure the table shows. No odds word comes with it: the
                # muster's would read back what may stand beside him unseen.
                quote = dict(quote, force=dict(force, theirs_low=counted, theirs_high=counted))
            shown = quote.get("shown") or _shown(corps.name)
            if getattr(corps, "artillery", False) and corps.location != foe.location:
                kind, label = "cannonade", f"{shown}'s guns"
            elif getattr(corps, "is_sovereign", False) and the_guard_goes_in():
                kind, label = "guard", "The Guard"
            elif corps.name == lead.name:
                # On a day he opened, the lead's own attack is his riposte.
                kind = "press"
                label = f"{shown} strikes back" if day.get("side") == "defence" else f"{shown} presses"
            else:
                kind, label = "lead", f"{shown} leads"
            ok, why = lit(PRICES[kind], "" if quote.get("ok") else str(quote.get("refusal") or "He cannot."))
            chips.append(_chip(kind, label, command=str(quote.get("command") or ""), ok=ok, why=why,
                               counsel=str(quote.get("objection") or "none"),
                               odds=str((quote.get("force") or {}).get("odds") or ""), who=corps.name))
            _does(chips[-1],
                  _telling.DOES["cannonade"] if kind == "cannonade" else _telling.does_attack(kind, quote),
                  _telling.more_of("guard" if kind == "guard" else "press") if kind != "cannonade" else "",
                  _telling.risk_of(kind, quote, day))
            chips[-1]["_force"] = dict(quote.get("force") or {})   # row PW: for `speak_plainly`
            if corps.name == lead.name:
                for row in quote.get("bring") or []:
                    if not row.get("command"):
                        continue
                    ok, why = lit(PRICES["bring_up"], "" if row.get("ok", True) else str(row.get("refusal") or ""))
                    chips.append(_chip("bring_up", f"Bring up {row.get('shown') or _shown(row.get('marshal'))}",
                                       command=str(row["command"]), ok=ok, why=why,
                                       counsel=str(row.get("objection") or "none"),
                                       who=str(row.get("marshal") or "")))
                    _does(chips[-1], _telling.DOES["bring_up"], "", _telling.risk_of("bring_up", {}, day))
        refusal = order_state_refusal(world, lead, "defend")
        ok, why = lit(PRICES["dig_in"], str(refusal or ""))
        chips.append(_chip("dig_in", f"{_shown(lead.name)} digs in",
                           command=f"{_shown(lead.name)}, defend", ok=ok, why=why,
                           counsel=Q._tactical_objection(world, lead, "defend", ""), who=lead.name))
        _does(chips[-1], _telling.does_dig_in(lead) if not refusal else _telling.DOES["dig_in"],
              _telling.more_of("dig_in"), _telling.risk_of("dig_in", {}, day))
        if day.get("side") == "defence":
            refusal = order_state_refusal(world, lead, "retreat")
            chips.append(_chip("break_off", "Fall back", command=f"{_shown(lead.name)}, retreat",
                               ok=not refusal, why=str(refusal or ""), who=lead.name))
            _does(chips[-1], _telling.stakes_of("fall_back", day) if _telling.a_word_says_what_it_risks()
                  else _telling.DOES["fall_back"], _telling.more_of("fall_back"))
    # BA-6: the free words say their stakes (the toll that stands, Berthier's reading)
    _risks = _telling.a_word_says_what_it_risks()
    _reading = _telling.reading_of(world, day) if (_risks and _telling.the_table_reads_him()) else None
    _read_line = str((_reading or {}).get("line") or "") if isinstance(_reading, dict) else ""
    chips.append(_chip("stand", f"{_shown(lead.name)} stands", word="stand", who=lead.name))
    _stand = _telling.does_stand(day)
    if _risks:
        _stand = _telling.stakes_of("stand_night" if _stand == _telling.DOES["stand_night"] else "stand",
                                    day, reading=_read_line)
    _does(chips[-1], _stand, _telling.more_of("stand"))
    if isinstance(_reading, dict):
        chips[-1]["_reading"] = str(_reading.get("strike") or "")   # row PW: for `speak_plainly`
    if a_marshal_may_be_left_to_it():
        chips.append(_chip("stand", f"Leave it to {_shown(lead.name)}", word="leave_it", who=lead.name))
        if _telling.a_word_says_what_it_does():
            _does(chips[-1], _telling.would_of(world, day), _telling.more_of("leave_it"))
    if day.get("side") == "attack":
        chips.append(_chip("break_off", "Break off", word="break_off", who=lead.name))
        _does(chips[-1], _telling.stakes_of("break_off", day) if _risks else _telling.DOES["break_off"],
              _telling.more_of("break_off"))
    # Row PW "Plain Words": every chip said in everyday words — one pass over
    # the chips as built (`battle_telling.speak_plainly`; the seam down leaves
    # them as they are and only drops the pass's private hints).
    for chip in chips:
        _telling.speak_plainly(chip, day, lead_shown=_shown(lead.name))
    chips.sort(key=_chip_rank)            # stable: the order within a kind is kept
    return chips

