"""Row BA, session BA-5 — "the finish": the day of battle tells itself.

The user's word (November 16, 2026): "MAKE SURE THIS FEATURE ROCKS DONT FEAR
DEEPR ESERWARCH ETC" — and two blind readers of the table's frames, who knew
nothing of the game: the telling liked (drama 7/10), the decision not (agency
4, decision clarity 4). A word showed its price and not what it does; nothing
said what he would do, or what decided a clash (`docs/BATTLE_DIORAMA_SPEC.md`
§15.22).

EVERYTHING HERE IS DERIVED. It reads what the engine has already computed —
the battle's own result, the day's record, the quotes the table already
makes, the rule the enemy already follows — and moves no number of the game.

* `what_told` — the one factor that weighed most in a clash, by a fixed rule
  and never a percentage: numbers at 5 to 4 or better, else the largest named
  advantage of 10 points or more in the battle report's own list, else the
  dice at 3 or more from seven, else "an even fight".
* `day_so_far`, `clash_line`, `better_of` — figures with their scope: the day's
  toll under the title, one line a clash.
* `reading_of` — Berthier's reading of him: "he will strike", "he may strike",
  "he will not strike". It IS the rule he follows (`EnemyAI.the_days_reading`:
  the decision at the two ends of his mood), and it is SHOWN only as far as
  the player can see: a certain word is said only when it is true for every
  roll he could make AND follows from what is in the player's sight; all else
  reads "may". It names no corps and no fallback (the fog law: five shades
  would let a player work his strength back more finely than the fog allows,
  and a "not yet" would betray a corps out of sight).
* `would_of` — what our own lead would do, left to it.
* `does_*` — what each word of the day does, on its face.
* `close_more`, `shape_of` — the close names what told and what kind of day
  it was.
* `verdict_line` — what told, under the headline of a battle's own table (a
  battle that hangs no day, and the clash that decides one).

THE SEAMS are zero-argument functions read through this module (the driver's
`--seam backend.game_logic.battle_telling:<name>=False`). With all five down
the table and the record are BA-4's, key for key.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from backend.errors import report

BETTER_MARGIN = 1.25      # the toll, or the men committed, at 5 to 4 or better
NAMED_GAP = 10            # a named advantage tells at 10 points or more
DICE_GAP = 3              # the dice tell at 3 or more from seven
AVERAGE_THROW = 7


# ════════════════════════════════════════════════════════
# The seams
# ════════════════════════════════════════════════════════

def the_table_reads_him() -> bool:
    """Berthier's reading of the enemy's next word, on the table that awaits
    ours (the user's tick at the plan gate — "Yes, three states"). Down
    (False): his temper and his road only, as BA-3 had it."""
    return True


def a_word_says_what_it_does() -> bool:
    """Every chip of a day carries `does` — its consequence, in a few words.
    Down (False): a chip is its label, its price and its hover, as before."""
    return True


def the_day_tells_its_clashes() -> bool:
    """The line under the title is the day's toll so far ("The day so far: …")
    and every clash adds one line to the day's telling, with what told. Down
    (False): "The last clash: …" and the words alone, as before."""
    return True


def the_close_names_what_told() -> bool:
    """A day's close says whom its toll favoured, what told in the clash that
    decided it, and what kind of day it was. Down (False): BA-4's close."""
    return True


def a_verdict_names_what_told() -> bool:
    """The table of a battle the player's marshal LED says under its own
    headline WHAT TOLD in it — "Our numbers told." — and the clash that
    decides a day names itself ("Decided at the third clash: …"). The readers
    of the table's frames asked that every verdict name a cause; a day's
    clashes did, a battle decided at once did not. A telling on any road: it
    is read from the battle's own report and no rule reads it
    (`verdict_line`, `battle_day.the_verdicts_line`). Down (False): the
    headline stands alone, as before."""
    return True


# ════════════════════════════════════════════════════════
# Figures with their scope
# ════════════════════════════════════════════════════════

def better_of(ours_lost: int, his_lost: int) -> str:
    """"ours" / "theirs" / "even": who has the better of a toll, at 5 to 4."""
    ours_lost, his_lost = int(ours_lost or 0), int(his_lost or 0)
    if his_lost > ours_lost and his_lost >= BETTER_MARGIN * max(1, ours_lost):
        return "ours"
    if ours_lost > his_lost and ours_lost >= BETTER_MARGIN * max(1, his_lost):
        return "theirs"
    return "even"


def day_so_far(day: dict, enemy_shown: str) -> str:
    """The line under the title: the day's own toll, and who has the better
    of it — "The day so far: …" while it is open, "The day: …" once it has
    closed. "" for a day that kept no count (one opened before BA-4)."""
    if int(day.get("clashes", 0) or 0) <= 0:
        return ""
    toll = day.get("toll") or {}
    ours, his = int(toll.get("ours", 0) or 0), int(toll.get("his", 0) or 0)
    better = better_of(ours, his)
    if day.get("open", True) is False:
        tail = {"ours": "the better of the toll was ours",
                "theirs": f"{enemy_shown} had the better of the toll"}.get(better, "the toll stood even")
        return f"The day: {ours:,} of ours for {his:,} of his — {tail}."
    # (the second reading: "it stands even" under the headline was read against
    # "odds: unfavorable" on a card — the line says it is the TOLL it speaks of)
    tail = {"ours": "the better of the toll is ours",
            "theirs": f"{enemy_shown} has the better of the toll"}.get(better, "the toll stands even")
    return f"The day so far: {ours:,} of ours for {his:,} of his — {tail}."


_ON_POINTS = {"ours": "we won on points", "theirs": "we lost on points"}


def clash_line(read: dict, attacker_shown: str, told: str, *, opening: bool = False) -> str:
    """One clash, in one line: whose attack, how it stood for us, its own
    toll, and what told."""
    head = "The opening" if opening else f"{attacker_shown}'s attack"
    result = _ON_POINTS.get(str((read or {}).get("ahead") or ""), "drawn")
    tail = f"; {told}" if told else ""
    return (f"{head}: {result} — {int((read or {}).get('our_loss', 0) or 0):,} of ours for "
            f"{int((read or {}).get('his_loss', 0) or 0):,} of his{tail}.")


def verdict_line(told: str, clash: str = "", broke: str = "") -> str:
    """WHAT TOLD, as the line under a battle's own headline: "Our weight of
    numbers told." For a day a clash decided, `clash` is that clash's ordinal
    word and the line names the clash: "Decided at the third clash: our weight
    of numbers told." `broke` (the second reading: both readers asked for the
    decisive moment by name, last before the verdict) is the lead whose line
    broke, as the table shows his name — the line then names that moment:
    "Decided when Mack's line broke: our weight of numbers told." Never a
    figure (`what_told` carries none)."""
    told = str(told or "").strip() or "an even fight"
    when = f"when {broke}'s line broke" if broke else ""
    if clash:
        head = f"Decided at the {clash} clash" + (f", {when}" if when else "")
        if told == "an even fight":
            return f"{head}, in an even fight."
        return f"{head}: {told}."
    if when:
        if told == "an even fight":
            return f"Decided {when}, in an even fight."
        return f"Decided {when}: {told}."
    return f"{told[:1].upper()}{told[1:]}."


def assault_told(held: bool, we_attack: bool, attackers: int, garrison: int,
                 fortified: bool = False, men: Optional[Tuple[int, int]] = None) -> str:
    """What told at a wall, for the table of an assault the player's court
    made or stood (the second reading: "the assault fails with no cause").
    `attackers` / `garrison` are the strengths the assault was FOUGHT on (the
    resolver's effective figures: the ground, the works and the stormers'
    own modifiers in them); `men` the two sides' men, (attackers, garrison)
    — the same figures when not given. A wall that held told for its
    garrison where works stood behind it; a wall held or carried tells of
    the weight of NUMBERS only where the side's men stood 5 to 4 or better
    AND the fight's own figures kept that edge (the re-review: numbers judged
    on the effective figures alone named men where the ground tipped it, and
    on men alone where the ground had taken the edge away). Else nothing
    ("") — never a cause the fight did not have (the review: "the walls told"
    was said of every wall that held, works or none, whatever the odds)."""
    attackers, garrison = int(attackers or 0), int(garrison or 0)
    men_a, men_g = (int(men[0] or 0), int(men[1] or 0)) if men else (attackers, garrison)

    def edge(more: int, fewer: int) -> bool:
        return fewer > 0 and more >= BETTER_MARGIN * fewer

    if held:
        if fortified:
            return "The walls told for the garrison." if we_attack else "Our walls told."
        if edge(garrison, attackers) and edge(men_g, men_a):
            return "The garrison's weight of numbers told." if we_attack else "Our weight of numbers told."
        return ""
    if not fortified and edge(attackers, garrison) and edge(men_a, men_g):
        return "Our weight of numbers told." if we_attack else "His weight of numbers told."
    return ""


# ════════════════════════════════════════════════════════
# What told
# ════════════════════════════════════════════════════════

# The battle report's own labels (`battle_report.snapshot_*_modifiers`), in
# the table's words. A label not listed is said as it is written.
_NOUNS = (
    ("fortified position", "works"),
    ("fortification building", "walls"),
    ("defensive stance", "dug-in line"),
    ("aggressive stance", "ardour"),
    ("flanking", "flank attack"),
    ("drill training", "drill"),
    ("forced march momentum", "momentum"),
    ("recklessness", "recklessness"),
    ("exhaustion", "exhaustion"),
    ("cavalry counter", "horse among the guns"),
    ("cavalry terrain", "horse"),
    ("square formation", "squares"),
    ("ranged bombardment", "guns"),
    ("artillery overwatch", "guns"),
    ("counter-punch", "counter-stroke"),
    ("iron resolve", "resolve"),
    ("glorious charge", "charge"),
    ("caught drilling", "interrupted drill"),
    ("artillery in transit", "limbered guns"),
    ("reverse slope", "reverse slope"),
    ("habsburg resolve", "resolve"),
    ("child of victory", "stubbornness"),
    ("outnumbered (", "caution when outnumbered"),
    ("immovable", "immovable hold"),
    ("personality", "temper"),
)


def _temper(low: str) -> str:
    """"personality (aggressive)" -> "aggressive temper"."""
    named = low.split("(", 1)[1].split(")", 1)[0].strip() if "(" in low else ""
    return f"{named} temper" if named else "temper"


def _noun(label: str) -> str:
    low = str(label or "").lower()
    for fragment, noun in _NOUNS:
        if fragment in low:
            return noun
    return low.split(" (")[0] or "advantage"


def _committed(ctx) -> Tuple[int, int]:
    """(attacker, defender): the men each side brought to the clash, at the
    muster — the two leads and every corps that fought beside them."""
    pre = getattr(ctx, "_bd_pre_strengths", None) or {}

    def side(lead, parts, fallback) -> int:
        names = {getattr(lead, "name", "")}
        names.update(getattr(p, "name", "") for p in (parts or []))
        total = sum(int(pre.get(name, 0) or 0) for name in names if name)
        return total or int(fallback or 0)

    return (side(getattr(ctx, "marshal", None), getattr(ctx, "atk_participants", None),
                 getattr(ctx, "pre_battle_attacker_strength", 0)),
            side(getattr(ctx, "enemy_marshal", None), getattr(ctx, "def_participants", None),
                 getattr(ctx, "pre_battle_defender_strength", 0)))


def what_told(ctx, attacker_is_ours: bool, better: str) -> str:
    """The factor that weighed most for the side that did better, in a few
    words and never a figure. One fixed rule, in this order: NUMBERS, when the
    men committed stand 5 to 4 or better; else the largest NAMED advantage of
    10 points or more in the battle report's own list (the winner's own bonus,
    or the loser's own penalty); else THE DICE, when the throw stood 3 or more
    from seven on the side that did better; else "an even fight". The dice are
    the attacker's throw: a high one favours him, a low one the defender.
    `better`: "ours" / "theirs" (who did better), anything else is even."""
    if better not in ("ours", "theirs"):
        return "an even fight"
    try:
        result = getattr(ctx, "battle_result", None) or {}
        winner_attacks = (better == "ours") == bool(attacker_is_ours)
        whose, losers = ("our", "his") if better == "ours" else ("his", "our")
        for_whom, against = ("us", "him") if better == "ours" else ("him", "us")
        atk, dfd = _committed(ctx)
        won, lost = (atk, dfd) if winner_attacks else (dfd, atk)
        if lost > 0 and won >= BETTER_MARGIN * lost:
            return f"{whose} weight of numbers told"
        snap = result.get("modifier_snapshot") or {}
        best: Tuple[int, str] = (0, "")
        for row in snap.get("attacker" if winner_attacks else "defender") or []:
            value = int(row.get("value", 0) or 0)
            if row.get("type") == "bonus" and value > best[0]:
                label = str(row.get("label") or "")
                low = label.lower()
                if low.startswith("terrain"):
                    best = (value, f"the ground told for {for_whom}")
                elif "emperor commands" in low:
                    best = (value, f"the Emperor's presence told for {for_whom}")
                elif low.startswith("cavalry terrain"):
                    best = (value, f"the ground told for {whose} horse")
                elif "square formation (vs artillery)" in low:
                    # the ATTACKER's row, named for the defender's squares under his guns
                    best = (value, f"{whose} guns told on {losers} squares")
                elif low.startswith("personality ("):
                    best = (value, f"{whose} {_temper(low)} told")
                else:
                    best = (value, f"{whose} {_noun(label)} told")
        for row in snap.get("defender" if winner_attacks else "attacker") or []:
            value = int(row.get("value", 0) or 0)
            if row.get("type") == "penalty" and value > best[0]:
                low = str(row.get("label") or "").lower()
                # Two rows of the ATTACKER's list are named for the DEFENDER's
                # own asset (`battle_report.snapshot_attacker_modifiers`): they
                # are the winner's, not a weakness of the side that lost.
                if "square formation (vs cavalry)" in low:
                    best = (value, f"{whose} squares told")
                elif "artillery overwatch" in low:
                    best = (value, f"{whose} guns told")
                elif low.startswith("cavalry terrain"):
                    best = (value, f"the ground told against {losers} horse")
                elif low.startswith("personality ("):
                    best = (value, f"{losers} {_temper(low)} told against {against}")
                else:
                    best = (value, f"{losers} {_noun(low)} told against {against}")
        if best[0] >= NAMED_GAP:
            return best[1]
        natural = (result.get("attacker_roll") or {}).get("natural")
        if natural is not None:
            gap = int(natural) - AVERAGE_THROW
            if (winner_attacks and gap >= DICE_GAP) or (not winner_attacks and gap <= -DICE_GAP):
                return f"the dice told for {for_whom}"
    except Exception as exc:
        report(exc, "battle_telling.what_told")
    return "an even fight"


def decided_for(ctx, attacker_is_ours: bool) -> str:
    """"ours" / "theirs" / "": whom a deciding clash was decided for — the
    side that was not driven from the field."""
    result = getattr(ctx, "battle_result", None) or {}
    outcome = str(result.get("outcome") or "")
    if outcome == "mutual_destruction":
        return ""      # (the review) both armies ruined: it was decided for neither
    attacker_beaten = (bool((result.get("attacker") or {}).get("forced_retreat"))
                       or outcome.startswith("defender"))
    defender_beaten = (bool((result.get("defender") or {}).get("forced_retreat"))
                       or outcome.startswith("attacker")
                       or bool(getattr(ctx, "conquered", False))
                       or bool(getattr(ctx, "enemy_destroyed", False)))
    if defender_beaten == attacker_beaten:
        return ""
    return "ours" if defender_beaten == bool(attacker_is_ours) else "theirs"


# ════════════════════════════════════════════════════════
# Berthier's reading
# ════════════════════════════════════════════════════════

READ_LINES = {"will": "he will strike", "may": "he may strike", "will_not": "he will not strike"}
READ_HOVER = ("Berthier's reading of his next word, as things stand: a clash changes it. "
              "\"May\" is said of anything that turns on his mood, or on what is out of your sight.")
_READER: Dict[str, Any] = {}


def _reader():
    """An `EnemyAI` over one executor kept for reading (the quotes keep theirs
    the same way: `order_quotes._MUSTER_READER`)."""
    from backend.ai.enemy_ai import EnemyAI
    executor = _READER.get("executor")
    if executor is None:
        from backend.commands.executor import CommandExecutor
        executor = _READER["executor"] = CommandExecutor()
    return EnemyAI(executor)


def _pure(fn):
    """Run a reading and put `random` back as it was: a reading is no roll."""
    from backend.commands.order_quotes import _without_spending_the_dice
    return _without_spending_the_dice(fn)


def _his_terms(world, day) -> Optional[dict]:
    from backend.game_logic import battle_day as BD
    him, lead = world.get_marshal(day.get("enemy")), world.get_marshal(day.get("lead"))
    if him is None or lead is None:
        return None
    purse = int(day.get("theirs", 0) or 0) if BD.the_enemy_spends_his() else 0
    guard = bool(getattr(him, "is_sovereign", False)) and BD.the_guard_goes_in()
    return {"marshal": him, "foe": lead, "purse": purse,
            "opened": day.get("side") == "defence",
            "behind": (day.get("read") or {}).get("ahead", "even") == "ours",
            "strike_price": int(BD.PRICES["guard" if guard else "strike"])}


def _our_terms(world, day) -> Optional[dict]:
    from backend.game_logic import battle_day as BD
    him, lead = world.get_marshal(day.get("enemy")), world.get_marshal(day.get("lead"))
    if him is None or lead is None:
        return None
    guard = bool(getattr(lead, "is_sovereign", False)) and BD.the_guard_goes_in()
    return {"marshal": lead, "foe": him, "purse": int(day.get("ours", 0) or 0),
            "opened": day.get("side") == "attack",
            "behind": (day.get("read") or {}).get("ahead", "even") == "theirs",
            "strike_price": int(BD.PRICES["guard" if guard else "strike"])}


def _read(world, terms: dict) -> dict:
    ai = _reader()
    return _pure(lambda: ai.the_days_reading(
        terms["marshal"], terms["foe"], world, purse=terms["purse"], opened=terms["opened"],
        behind=terms["behind"], strike_price=terms["strike_price"]))


def _seen_field(world, him) -> Tuple[int, Optional[int]]:
    """(least, most) men of his field as the player's sight bounds them —
    `most` None when no ceiling can be put on it. A corps in sight is known
    by its strength band (`intel.get_strength_band`), one out of sight not at
    all: it adds nothing to the least and takes the ceiling away."""
    from backend.commands.order_quotes import _band_range
    from backend.game_logic.intel_surfaces import in_sight
    from backend.models.intel import get_strength_band
    player = getattr(world, "player_nation", "")
    least, most = 0, 0
    open_ended = False
    for corps in world.marshals.values():
        if (corps.nation != him.nation or corps.location != him.location
                or int(getattr(corps, "strength", 0) or 0) <= 0
                or getattr(corps, "broken", False) or getattr(corps, "retreated_this_turn", False)):
            continue
        if not in_sight(world, player, corps):
            open_ended = True
            continue
        low, high = _band_range(get_strength_band(int(corps.strength)))
        least += int(low)
        if int(high) <= 0:
            open_ended = True
        else:
            most += int(high)
    return least, (None if open_ended else most)


def _as_seen(world, him, truth: dict, terms: dict) -> str:
    """The same reading from what is in the player's sight alone. His purse is
    on the table (the pips); his field in plain sight (FULL) is read as it is;
    under less, by the strength bands — and his fitness to strike is not seen
    at all, so a "will" from the bands stands only where the truth agrees
    (`reading_of`)."""
    if int(terms["purse"]) < int(terms["strike_price"]):
        return "will_not"
    from backend.models.intel import FULL
    intel = (getattr(world, "intel", None) or {}).get(him.location)
    if intel is not None and getattr(intel, "visibility", None) == FULL:
        # (the review) full sight shows his men to the man and whether he
        # stands behind works (`FOG_OF_WAR_SPEC.md` §2: names, exact troops,
        # morale, stance, fortification) — never a wound, a retreat's recovery
        # or a drill. The reading from sight weighs what sight shows; where his
        # unseen fitness turns the rule, the two disagree and the word is "may"
        # (it was the rule's own word: "will not" over a field he plainly
        # outnumbers told the player he was unfit).
        if bool(getattr(him, "fortified", False)):
            return "will_not"
        ratio = float(truth.get("ratio") or 0.0)
        if ratio >= float(truth["bar_high"]):
            return "will"
        if ratio < float(truth["bar_low"]):
            return "will_not"
        return "may"
    defenders = float(truth.get("defenders") or 0.0)
    if defenders <= 0:
        return "may"
    least, most = _seen_field(world, him)
    if least / defenders >= float(truth["bar_high"]):
        return "will"
    if most is not None and most / defenders < float(truth["bar_low"]):
        return "will_not"
    return "may"


def reading_of(world, day) -> Optional[dict]:
    """Berthier's reading of his next word: {"strike": "will" | "may" |
    "will_not", "line", "hover"}. A certain word is said only when the rule
    says it for every roll he could make (`EnemyAI.the_days_reading`) AND it
    follows from what the player can see (`_as_seen`); anything else is "may".
    One bit stays readable, by the law as ruled (`FOG_OF_WAR_SPEC.md` §4.4):
    where what the player sees would make him strike and his unseen fitness
    forbids it, the word is "may", not "will" — the price of a certain word
    that is never falsified (the re-review weighed it and kept it).
    PURE. None where there is nothing to read."""
    try:
        terms = _his_terms(world, day)
        if terms is None:
            return None
        truth = _read(world, terms)
        seen = _as_seen(world, terms["marshal"], truth, terms)
        state = str(truth["strike"]) if seen == truth["strike"] else "may"
        return {"strike": state, "line": READ_LINES[state], "hover": READ_HOVER}
    except Exception as exc:
        report(exc, "battle_telling.reading_of")
        return None


_WOULD = {
    "strike": "press", "bring_up": "bring up a corps", "break_off": "break off",
    "draw_off": "fall back", "dig_in": "dig in", "stand": "stand",
}


def _our_word_as_seen(world, terms: dict) -> Tuple[str, str, str]:
    """(boldest, wariest, far): our lead's word read from what the player sees
    of the enemy's field (the review: `would_of` read his TRUE field — a corps
    out of sight, his exact strength inside its band). At its least (each
    corps in sight at its band's low, nobody else) at both ends of our lead's
    mood, and at no ceiling at all (`far`: a field too strong to strike or to
    bring a corps up against — what is left turns on our own side only). The
    rule falls from a strike to a corps brought up to the rest as the field
    grows, so the true word lies between them. PURE."""
    ai = _reader()

    def words():
        base, spread = ai._the_days_temper(terms["marshal"], world)
        t = ai._the_days_terms(terms["marshal"], terms["foe"], world, purse=terms["purse"],
                               opened=terms["opened"], behind=terms["behind"],
                               strike_price=terms["strike_price"])
        least, _most = _seen_field(world, terms["foe"])
        near = dict(t, defenders=float(max(1, least)), ratio=float(t["combined"]) / float(max(1, least)))
        far = dict(t, defenders=1e15, ratio=0.0)
        return (str(ai._the_days_decision(near, base * (1.0 - spread)).get("kind") or "stand"),
                str(ai._the_days_decision(near, base * (1.0 + spread)).get("kind") or "stand"),
                str(ai._the_days_decision(far, base * (1.0 - spread)).get("kind") or "stand"))
    return _pure(words)


def would_of(world, day) -> str:
    """What our own lead would do with the day, left to it — his first word,
    by the rule every commander follows: "he would press" where every mood of
    his says so, "he may press" where his mood decides. "" where unread.
    (The review) It is read as far as the player sees the enemy: at full sight
    by the rule itself — the attack card's own odds word is given on an exact
    sighting — and below it at the bounds of what is seen
    (`_our_word_as_seen`): a certain word only where it holds from the least
    field in sight to no ceiling at all, else "may" and the boldest word the
    sight allows."""
    try:
        terms = _our_terms(world, day)
        if terms is None:
            return ""
        strike = "strike back" if day.get("side") == "defence" else "press"
        said = dict(_WOULD, strike=strike)
        from backend.models.intel import FULL
        intel = (getattr(world, "intel", None) or {}).get(terms["foe"].location)
        if intel is None or getattr(intel, "visibility", None) != FULL:
            bold, wary, far = _our_word_as_seen(world, terms)
            return (f"he would {said.get(far, far)}" if bold == wary == far
                    else f"he may {said.get(bold, bold)}")
        got = _read(world, terms)
        low, high = str(got["low"].get("kind") or "stand"), str(got["high"].get("kind") or "stand")
        return (f"he would {said.get(low, low)}" if low == high
                else f"he may {said.get(low, low)}")
    except Exception as exc:
        report(exc, "battle_telling.would_of")
        return ""


# ════════════════════════════════════════════════════════
# What each word does
# ════════════════════════════════════════════════════════

def _on(force: dict) -> str:
    """"35,000 on 50,000" — ours on his, as far as his is known."""
    if not isinstance(force, dict) or not force:
        return ""
    ours = int(force.get("ours", 0) or 0)
    low, high = int(force.get("theirs_low", 0) or 0), int(force.get("theirs_high", 0) or 0)
    theirs = f"{low:,}" if (low > 0 and low == high) else str(force.get("theirs_label") or "")
    return f"{ours:,} on {theirs}" if (ours > 0 and theirs) else ""


def does_attack(kind: str, quote: dict) -> str:
    """A press, another corps' lead, the Guard: the odds the attack card
    prints (the muster's own word, given only on an exact sighting) and the
    men on each side. The Guard adds NP-D1's first number."""
    from backend.game_logic import battle_day as BD
    force = (quote or {}).get("force") or {}
    odds = str(force.get("odds") or "")
    men = _on(force)
    head = f"odds: {odds}" if odds else ""
    if not head and men and int(force.get("theirs_low", 0) or 0) > 0 \
            and force.get("theirs_low") == force.get("theirs_high"):
        # (the second reading: one card read "odds: unfavorable — …" and the next
        # the bare figures) no odds word comes with the table's own count of him
        # (`battle_day.the_offer`): the card says whose figure it is
        head = "by the day's count"
    body = " — ".join(part for part in (head, men) if part)
    if kind == "guard" and BD.the_guards_numbers_bite():
        tail = f"his morale −{int(BD.GUARD_SHOCK)}"
        return f"{body} · {tail}" if body else tail
    return body


DOES = {
    "cannonade": "his line is shelled; no clash",
    "bring_up": "comes up beside the lead",
    "dig_in": "firmer if he strikes",
    "break_off": "the day ends; he keeps the field",
    "fall_back": "the day ends; he takes the field",
    "stand": "he speaks next",
    "stand_night": "night falls, undecided",
}


def dug_in_pct(lead) -> int:
    """What the defensive stance is worth to THIS lead on the defence, in
    whole percent over where he stands now — read from the model's own single
    source (`Marshal.get_defense_modifier`, with nothing consumed), never a
    figure kept here: a temper changes it (the stance is +15% to most, +9% to
    an aggressive lead). The stance is put back as it was. 0 where unread.
    (The review) The order also ends a drill not yet locked
    (`tactical_executor._execute_defend`): the figure reads that too, and the
    drill is put back as it was."""
    from backend.models.marshal import Stance
    stance = getattr(lead, "stance", None)
    drilling = bool(getattr(lead, "drilling", False))
    now = float(lead.get_defense_modifier(consume=False))
    try:
        lead.stance = Stance.DEFENSIVE
        if drilling and not getattr(lead, "drilling_locked", False):
            lead.drilling = False
        dug = float(lead.get_defense_modifier(consume=False))
    finally:
        lead.stance = stance
        if hasattr(lead, "drilling"):
            lead.drilling = drilling
    return int(round((dug / now - 1.0) * 100)) if now > 0 else 0


def does_dig_in(lead) -> str:
    """To dig in, by where the lead stands (the second reading: "firmer if he
    strikes" read as a vague adjective): from any other stance the order is
    the defensive stance, and the card says what it is worth to him; a lead
    already in it throws up field works, which grow by the turn and carry no
    single figure."""
    try:
        from backend.models.marshal import Stance
        if getattr(lead, "stance", None) == Stance.DEFENSIVE:
            return "field works: firmer still if he strikes"
        pct = dug_in_pct(lead)
        if pct > 0:
            return f"defensive stance: +{pct}% if he strikes"
    except Exception as exc:
        report(exc, "battle_telling.does_dig_in")
    return DOES["dig_in"]


# What follows a day no clash decided, in one sentence on its closing table
# (the second reading: "the standstill is not translated into any consequence").
# True of the rule: such a day moves nobody (`battle_day._close`), and the
# night's bar on the pair is lifted at dawn (`battle_day.at_dawn`).
FOLLOWS = {
    "night": "Neither army is driven off; the fight may be renewed tomorrow.",
    "broke_off": "Neither army is driven off.",
    "he_broke_off": "Neither army is driven off.",
}


def what_follows(how: str) -> str:
    return FOLLOWS.get(str(how or ""), "")
MORE = {
    "press": "A clash that decides ends the day at once.",
    "guard": ("As the Guard goes in his lead loses {shock} morale. Thrown back, every corps of "
              "yours that fought loses {recoil}."),
    "dig_in": "A dug-in line stands firmer when it is attacked. He speaks next.",
    "stand": "A silence costs no point. Two silences running, and night falls.",
    "break_off": "The attack is given up and the day ends where it stands.",
    "fall_back": "Your lead leaves the field and the day ends.",
    "leave_it": "He spends what is left by his own temper, and the enemy answers, until night.",
}


def does_stand(day: dict) -> str:
    """To stand: the word passes — or, after a silence of his, night falls."""
    return DOES["stand_night"] if int(day.get("silences", 0) or 0) >= 1 else DOES["stand"]


RESERVE_MORE = {
    "press": "Each point you then hold over his pursues: {men:,} more of his fall.",
    "guard": "Each point you then hold over his pursues: {men:,} more of his fall.",
    "stand": "A point kept pursues an enemy a clash has broken ({men:,} men a point), and covers you if you are the one broken.",
}


def more_of(kind: str) -> str:
    """The rest of what a word does, for its hover — and, where the reserve
    pursues a beaten enemy (`battle_day.the_reserve_pursues`), what a point
    kept is worth."""
    from backend.game_logic import battle_day as BD
    said = MORE.get(kind, "").format(shock=int(BD.GUARD_SHOCK), recoil=int(BD.GUARD_RECOIL))
    if BD.the_reserve_pursues() and kind in RESERVE_MORE:
        said = (said + " " + RESERVE_MORE[kind].format(men=int(BD.reserve_pursuit()))).strip()
    return said


# ════════════════════════════════════════════════════════
# The close: what told, and what kind of day it was
# ════════════════════════════════════════════════════════

def _said(day: dict) -> List[Tuple[str, str]]:
    return [(str(who), str(kind)) for who, kind in (day.get("said") or [])
            if isinstance(who, str) and isinstance(kind, str)]


def shape_of(day: dict, how: str, enemy_shown: str = "", lead_shown: str = "") -> str:
    """What kind of day it was, in one sentence — read only from the words
    said and how the day ended (never from a purse or a corps the table did
    not show). The models are real days: the reserve that decides (Ligny),
    the reserve thrown back (Waterloo), the late corps (Marengo), the guns
    and the column (Friedland), the attack given up (Aspern-Essling), the
    withdrawal in order (Wagram), the reserve never spent (Borodino), the
    night on an undecided field (Eylau)."""
    said = _said(day)
    his = enemy_shown or "the enemy"
    ours = lead_shown or "our lead"
    winner = str(day.get("decided_for") or "")
    if how == "decided":
        if not winner:
            # (the re-review) decided for neither — a battle that ruined both armies
            # (`decided_for`): no word of the day decided it or was thrown back
            return "Neither army kept the field."
        last = said[-1] if said else ("", "")
        if last[1] == "guard":
            if winner == last[0]:
                return "The Guard decided it." if winner == "ours" else f"{his}'s Guard decided it."
            return ("The Guard went in and was thrown back." if last[0] == "ours"
                    else f"{his}'s Guard went in and was thrown back.")
        if winner and (winner, "bring_up") in said:
            return "A corps brought up in the day turned it."
        if winner and (winner, "cannonade") in said:
            return "The guns prepared it and the column carried it."
        if int(day.get("clashes", 0) or 0) <= 2:
            return "One blow after the opening decided it."
        return "It was fought out to a decision."
    if how in ("broke_off", "he_broke_off"):
        attacker, defender = ("ours", "theirs") if how == "broke_off" else ("theirs", "ours")
        gave_up = "The attack was given up" if attacker == "ours" else f"{his} gave up his attack"
        if (defender, "dig_in") in said:
            return f"{gave_up} before a dug-in line."
        return f"{gave_up}."
    if how == "drew_off":
        return f"{his} left the field in good order."
    if how == "fell_back":
        return f"{ours} left the field in good order."
    if how == "night":
        toll = day.get("toll") or {}
        better = better_of(toll.get("ours", 0), toll.get("his", 0))
        # (the review) "never spent" is said only of a purse that never was: one
        # partly spent is "part of" it (a day kept from before BA-4 has no `ours_of`)
        ours, theirs = int(day.get("ours", 0) or 0), int(day.get("theirs", 0) or 0)
        ours_of = int(day.get("ours_of", ours) or 0)
        theirs_of = int(day.get("theirs_of", theirs) or 0)
        if better == "ours" and ours > 0:
            return ("Our reserve was never spent." if ours >= ours_of
                    else "Night fell with part of our reserve unspent.")
        if better == "theirs" and theirs > 0:
            return (f"{his}'s reserve was never spent." if theirs >= theirs_of
                    else f"Night fell with part of {his}'s reserve unspent.")
        if better == "even":
            return "Neither side could claim the field."
        return "It was fought to a standstill."
    return ""


def favoured(day: dict, enemy_shown: str) -> str:
    """Whom the day's toll favoured, for a day no clash decided."""
    toll = day.get("toll") or {}
    better = better_of(toll.get("ours", 0), toll.get("his", 0))
    if better == "ours":
        return "The better of the toll was ours."
    if better == "theirs":
        return f"{enemy_shown} had the better of the toll."
    return "The toll stood even."


def close_more(day: dict, how: str, enemy_shown: str = "", lead_shown: str = "") -> List[str]:
    """What the close adds to BA-4's line: for a day a clash decided, what
    told in that clash; for any other, whom the toll favoured; then the day's
    shape. [] for a day that kept no count."""
    if int(day.get("clashes", 0) or 0) <= 0:
        return []
    out: List[str] = []
    if how == "decided":
        told = str(day.get("decided_by") or "")
        if told and told != "an even fight":
            out.append(f"{told[:1].upper()}{told[1:]}.")
        pursued = day.get("reserve_pursued")
        if isinstance(pursued, dict) and int(pursued.get("men", 0) or 0) > 0:
            # the reserve that pursued a beaten enemy (`battle_day.the_reserve_pursues`)
            men = int(pursued["men"])
            out.append(f"Our reserve pursued: {men:,} more of his fell." if pursued.get("by") == "ours"
                       else f"{enemy_shown or 'His'}'s reserve pursued: {men:,} more of ours fell.")
    elif how in ("night", "broke_off", "he_broke_off", "drew_off", "fell_back"):
        out.append(favoured(day, enemy_shown))
    shape = shape_of(day, how, enemy_shown, lead_shown)
    if shape:
        out.append(shape)
    return out
