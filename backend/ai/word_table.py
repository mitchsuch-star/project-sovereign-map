"""Row IC, Session 2 (IC-8) — THE WORD TABLE: what the typed line takes for a task.

`docs/INDEPENDENT_COMMAND_SPEC.md` §8.3. The user's ruling (November 20, 2026):
"buttons exist for simpler things but typing is used for missions and excepts a
wide array if things". A TASK is a standing order with its parts — what he is
to do, where or to whom, for how long, and what to do IF something happens.
This is the ONE hand-written table of the words the line takes for each part.

Nothing here is read by the parser directly. `python -m tools.gen_task_words`
renders it into

    backend/ai/task_words.py                                  (the parser's lists)
    godot-client/project-sovereign/scripts/task_words.gd      (the client's chips,
                                                               Tab words and Help)

and the census in `tests/test_ic8_the_line.py` re-renders both, fails when
either has drifted, and runs every phrase below through the real parser and
the real read-back — so no word is promised here that is not read, and no
chip or Help line can teach a sentence the game refuses (the pattern of
`tools/gen_routed_order_words`, CX-R1).

THE PHRASE SYNTAX. A phrase is plain words with

    (a|b|c)     one of                    {enemy}   an enemy commander by name
    [word]      an optional word          {friend}  one of our marshals
                                          {place}   a province
                                          {n}       a number of turns

The generator expands every alternation and option into flat phrases.

WHAT IS IN IT TODAY (Session 2): the three standing tasks the line gives
(chase, hold, support — and the march), how long, the eight IFs and five
THENs of an exact order, what a march does THEN, and the words for how bold.
The how-bold words are READ and set aside in Session 2 (they change nothing
until a man can be set on his own — Session 3); "take" as a standing task and
its new word ("invest") land with it.
"""
from __future__ import annotations

# ── the task ────────────────────────────────────────────────────────────────
# `words` are read by the strategic table (`strategic_parser.STRATEGIC_KEYWORDS`)
# today; `new` words are IC-8's — each is restated, before any reader, as the
# table word it means, and only in front of the kind of object the task takes
# (so "keep an eye on Swabia" stays a scout and "stay with it" stays itself).
# `bare` words take no object ("Davout, stand fast").
TASKS = (
    {"task": "chase", "order": "PURSUE", "object": "enemy",
     "words": ("pursue", "chase", "hunt down", "harry", "go after", "shadow"),
     "new": {}, "bare": ()},
    {"task": "hold", "order": "HOLD", "object": "place",
     "words": ("hold", "guard", "protect"),
     "new": {"keep": "hold"}, "bare": ("stand fast", "stand firm")},
    {"task": "support", "order": "SUPPORT", "object": "friend",
     "words": ("support", "join", "back up", "follow", "cover"),
     "new": {"stay with": "follow"}, "bare": ()},
    {"task": "march", "order": "MOVE_TO", "object": "place",
     "words": ("march to",), "new": {}, "bare": ()},
)

# ── how long ────────────────────────────────────────────────────────────────
# The six clauses the condition grammar reads (`condition_grammar._READ_CLAUSES`).
HOW_LONG = (
    {"key": "max_turns", "say": "for {n} turns"},
    {"key": "until_turn", "say": "until turn {n}"},
    {"key": "until_marshal_arrives", "say": "until {friend} arrives"},
    {"key": "until_relieved", "say": "until relieved"},
    {"key": "until_battle_won", "say": "until the battle is won"},
    {"key": "until_marshal_destroyed", "say": "until {enemy} is destroyed"},
)

# ── if … then ───────────────────────────────────────────────────────────────
# The words that open an if-then. "once" and "as soon as" are NOT among them
# (they stay the clause guard's: a refusal, or CR-7-5's hand-off).
IF_MARKERS = ("if", "when", "should", "in case")

# The eight IFs (§7). `say` follows if / when / in case; `should` is the
# inverted form ("should Mack advance"). `slot` names what the phrase binds.
IFS = (
    {"if": "enemy_near", "slot": None,
     "say": ("(an|the) enemy (advances|approaches|comes within reach|comes (on|near|nearer|closer|forward))",
             "(an|the) enemy (moves|marches) (on|against) (us|him|you)",
             "enemies (advance|approach|come within reach)",
             "the foe (advances|approaches|comes within reach)"),
     "should": ("(an|the) enemy (advance|approach|come within reach|come (on|near|nearer|closer|forward))",)},
    {"if": "enemy_near", "slot": "enemy",
     "say": ("{enemy} (advances|advance|approaches|comes within reach|comes (on|near|nearer|closer|forward))",
             "{enemy} (moves|marches) (on|against) (us|him|you)"),
     "should": ("{enemy} (advance|approach|come within reach|come (on|near|nearer|closer|forward))",)},
    {"if": "attacked", "slot": None,
     "say": ("attacked", "(you|he) (are|is) attacked", "(you|he) (come|comes) under attack",
             "the enemy attacks [(you|him|us)]"),
     "should": ("(you|he) be attacked", "the enemy attack [(you|him|us)]")},
    {"if": "attacked", "slot": "enemy",
     "say": ("{enemy} attacks [(you|him|us)]",),
     "should": ("{enemy} attack [(you|him|us)]",)},
    {"if": "outnumbered", "slot": None,
     "say": ("outnumbered", "(you|he) (are|is) outnumbered"),
     "should": ("(you|he) be outnumbered",)},
    {"if": "surrounded", "slot": None,
     "say": ("surrounded", "(you|he) (are|is) [being] surrounded"),
     "should": ("(you|he) be surrounded",)},
    {"if": "friend_attacked", "slot": "friend",
     "say": ("{friend} is attacked [(next to|beside) (you|him)]",
             "{friend} comes under attack [(next to|beside) (you|him)]"),
     "should": ("{friend} be attacked [(next to|beside) (you|him)]",)},
    {"if": "place_falls", "slot": "place",
     "say": ("{place} (falls|is lost|is taken)",),
     "should": ("{place} (fall|be lost|be taken)",)},
    {"if": "friend_arrives", "slot": "friend",
     "say": ("{friend} arrives",),
     "should": ("{friend} arrive",)},
)

# The five THENs (§7). "attack" means attack if not outnumbered; the any-odds
# forms are their own choice and carry their warning.
THENS = (
    {"then": "attack", "any_odds": True,
     "say": ("attack (whatever|regardless of) the odds", "attack at (any cost|all costs)",
             "attack regardless")},
    {"then": "attack", "any_odds": False,
     "say": ("attack [(him|them|it)]", "counter-attack", "give battle")},
    {"then": "fall_back", "any_odds": False,
     "say": ("(fall back|retreat|withdraw|pull back) (to|on|upon|toward|towards) {place}",)},
    {"then": "march", "any_odds": False,
     "say": ("march (to|on) {place}", "(move|go) to {place}")},
    {"then": "join", "any_odds": False,
     "say": ("join (his|her|that|the) (battle|fight)", "join (him|her|them)",
             "(march|go) to (his|her) aid", "march to (the|his|her) guns")},
    {"then": "dig_in", "any_odds": False,
     "say": ("dig in", "fortify", "entrench")},
)

# Which THEN an IF may carry. "join his battle" needs a friend whose battle it
# is; "attack" on "if outnumbered" contradicts what "attack" means.
THENS_FOR = {
    "enemy_near": ("attack", "fall_back", "march", "dig_in"),
    "attacked": ("attack", "fall_back", "march", "dig_in"),
    "outnumbered": ("fall_back", "march", "dig_in"),
    "surrounded": ("attack", "fall_back", "march", "dig_in"),
    "friend_attacked": ("join", "attack", "fall_back", "march", "dig_in"),
    "place_falls": ("attack", "fall_back", "march", "dig_in"),
    "friend_arrives": ("attack", "fall_back", "march", "dig_in"),
}

# ── then, after a march ─────────────────────────────────────────────────────
# Today's arrival verbs (`strategic_parser.ARRIVAL_VERBS`) and the words that
# mean one of them: "march to Lorraine, then dig in" is "then fortify".
ARRIVAL_THENS = (
    {"verb": "hold", "say": ("hold",)},
    {"verb": "fortify", "say": ("fortify", "dig in")},
    {"verb": "drill", "say": ("drill",)},
    {"verb": "defend", "say": ("defend",)},
)

# ── how bold ────────────────────────────────────────────────────────────────
# One step either way of HIS OWN odds — for a man on his own (Session 3). In
# Session 2 the words are READ and SET ASIDE: the read-back names each one
# under "Not taken" ("an order is carried out as written") and Enter sends the
# line without it — so "hold Rhineland carefully" holds Rhineland, and nobody
# is left thinking the word did something.
HOW_BOLD = (
    {"step": "bolder", "say": ("boldly", "aggressively", "press hard")},
    {"step": "careful", "say": ("carefully", "cautiously", "only at good odds",
                                "don't risk the army")},
    {"step": "bolder", "say": ("at any cost",)},
)

# ── held back ───────────────────────────────────────────────────────────────
# Behind an ATTACK on a named enemy: the attack goes without the glorious
# charge — the answer "restrain" to the question a reckless horseman's attack
# would ask, given beforehand (IC-7's "Attack, held back").
HELD_BACK = ("held back", "without charging", "without a charge", "without the charge",
             "no charge")

# ── filler ──────────────────────────────────────────────────────────────────
# A clause that states no condition ("Ney, attack Mack if possible"): the
# order goes as written, and the read-back names the clause as a quiet note
# that blocks nothing (§8.4: "Filler … is a quiet note and blocks nothing").
FILLER = (
    "if possible", "if able", "if practicable", "if convenient",
    "when ready", "when able", "when possible", "when convenient",
)

# ── open-ended ──────────────────────────────────────────────────────────────
# An "until" that asks for NO limit ("hold until further orders"): it is what
# the plain order already does, so it is filler — named, blocking nothing.
OPEN_ENDED = (
    "until further (orders|order|notice|word|instructions|instruction)",
    "until I say [(otherwise|so)]",
    "until (told|ordered|instructed) otherwise",
    "until you hear (otherwise|from me)",
    "until I (tell|order) you otherwise",
)

# ── a task for an ARMY, and the war goal ────────────────────────────────────
# Row IC, Session 3b (§9, §9.1). A named army given a TASK — "Army of Italy,
# take Swabia" — is its commander on his own and the rest following him
# (`backend/commands/army_task.py`). The words that make an army's line a task:
# a take, a chase, or a hold WITH A PLACE NAMED. "attack" is not among them
# (an army's attack is one battle today, its first man's); `marked` verbs are a
# task only when the line says so (a mark of judgement, a how-bold word).
ARMY_TASK = {
    "take": ("take", "capture", "seize", "occupy"),
    "chase": ("pursue", "chase", "hunt down", "hunt", "harry", "go after", "shadow", "destroy"),
    "hold": ("hold", "guard", "protect", "keep"),
    "marked": ("attack", "storm", "march to", "march on", "advance on"),
}
# What an army is told of ITSELF, and how its commander hears it.
ARMY_MARKS = (
    ("on (its|their) own", "on your own"),
    ("as (it sees|they see) fit", "as you see fit"),
    ("at (its|their) discretion", "at your discretion"),
    ("use (its|their) (judgement|judgment)", "use your judgement"),
    ("in (its|their) own way", "in your own way"),
)
# "…, hold Milan by exact orders": the same words as a plain order to each corps.
ARMY_EXACT = ("[each] by exact (orders|order)", "as exact (orders|order)", "to the letter")
# "Ney, take the war goal": the task that follows the goal named for the war
# (`backend/ai/own_words.py`, `war_goals.task_for`).
GOAL_VERBS = ("take", "capture", "seize", "march (on|to)", "go for", "make for", "strike at",
              "aim (at|for)", "win", "reach", "pursue", "chase", "hunt down", "go after",
              "destroy", "serve")
GOAL_OBJECT = "(the|our|my|your) war goal"

# ── on his own with NO task ─────────────────────────────────────────────────
# Row IC, Session 4b (IC4-D3 — the user's "if you give them nothing they should
# make decisions"): a mark of judgement with nothing else to do — "Ney, act on
# your own", "Ney, as you see fit", "Ney, make war as you see fit" — sets him on
# his own with NO task (`own_order` "free"). The words that may stand beside a
# mark and still say "no task" (`backend/ai/own_words.free_task`):
FREE_TASK = ("act", "act alone", "go", "fight", "make war", "wage war", "carry the war to them",
             "do as you will", "do your work", "lead", "command", "take the field")

# ── the sentences the Help page and the first-open line teach ───────────────
# Each is executed through the read-back by the census on the 1805 board.
EXAMPLES = (
    "Davout, hold Lorraine for three turns.",
    "Davout, hold Lorraine until Ney arrives.",
    "Murat, chase Mack until he is destroyed.",
    "Soult, follow Ney.",
    "Ney, march to Lorraine, then dig in.",
    "Soult, hold Lorraine. If attacked, dig in. If outnumbered, fall back to Champagne.",
)
