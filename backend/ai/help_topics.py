"""DDB-48 (Pre-Deploy S13b part 4) — the command reference's ONE section a
question names.

"How do I build ships?" and "how can I close Britain's ports?" were sent to
the whole manual on purpose (ruling R7: a question about the game's GRAMMAR
keeps the reference) — about 9,500 px of it, in a window that shows four
lines (the sea #1 / #5 / #9 / #22, diplomacy-first #8 / #21). The reference
is now read by its sections: a "how do / can I …" question whose nouns name
one section is answered with that section, and `help <topic>` prints one
section ("help navy" had fallen to "this order eludes me"). A question that
names none keeps the whole reference, as before.

ONE table, read by the parser (`help <topic>` is help, never an order) and
by the help executor (which section to print). Pure; no world.

S14E-D17 / S14E-X142 (S14f part 3, October 25, 2026): DDB-48 left "a
question that names none keeps the whole reference" -- and about 30 of 51
probed "how do I <verb> <object>" lines (hold / protect / guard Paris,
besiege Vienna, intercept Mack, pay Ney, "take a loan", "stop the turn")
still dumped the 22,573-character manual into a four-line window. The
ruling (the user's standing delegation, as recommended): such a line is
answered with the SECTION INDEX -- `section_index` below, one
`help <topic>` line per section of the reference, ~700 characters -- and
the manual stays one `help` away (DDB-48's purpose, the player never loses
the reference, is served; its letter is overturned). The topic words the
index prints live in the SAME table (the third column), so the index and the
resolver cannot drift: a pin walks every printed line back through
`help_request_section`.
"""
from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple

# (section heading as the reference prints it, the words that name it in a
# QUESTION, the topic words `help <topic>` takes) — in precedence order: the
# narrower naval section before the Admiralty, several marshals before a
# single attack, the reign's victory before a battle's.
#
# The third column (S14E-D17 / S14E-X230): the EXACT topic words, matched whole before
# the keyword scan (so a word like "marshals" or "free" can name its section
# for `help <topic>` without stealing "how do I recruit marshals" or "do it
# for free" from their own). The FIRST is the one the section index prints;
# it must resolve to its own heading (pinned), and no word may name two
# headings. Empty = a continuation row of a heading already named above.
HELP_SECTIONS: Tuple[Tuple[str, str, Tuple[str, ...]], ...] = (
    ("PORTS AND THE CONTINENTAL SYSTEM",
     r"ports?|harbou?rs?|continental system|the system|closure|embargo|smuggl\w*",
     ("ports", "system")),
    ("THE ADMIRALTY",
     r"fleets?|navy|navies|naval|ships?|sail|keels?|blockad\w*|admiralty|admirals?"
     r"|readiness|postures?|crossings?|channel|expeditions?|landings?|land \w+ in"
     r"|diversion|descent|dock ?yards?|yards?|the sea|at sea|invade (?:britain|england)",
     ("navy",)),
    ("STRATEGIC COMMANDS",
     r"several marshals|two marshals|more than one marshal|marshals together"
     r"|together|combine\w*|join forces|both|support|follow|everyone|all (?:my )?marshals"
     r"|the army|pursu\w+|chase|march(?:es|ing)? to|standing orders?|cancel|halt",
     ("strategic", "standing orders")),
    ("TWO ORDERS IN ONE LINE",
     r"two orders|chain\w*|sequence|then|until|if \w+ (?:advances|comes)|in one line",
     ("chain",)),
    ("THE CONGRESS OF PARIS",
     r"congress|imperial peace|recogni[sz]\w*|titled|win the (?:game|campaign|reign|war)"
     r"|^how (?:do|can) (?:i|we) win(?=[?.!\s]*$)",
     ("congress",)),
    # S14E-X230 (S14f p3): the section had no word at all ("help designs" ->
    # "this order eludes me", and the index could not name it).
    ("THE EMPEROR'S DESIGNS",
     r"designs?|emperor'?s? designs?",
     ("designs", "design", "emperor's designs", "emperor", "empire")),
    ("DIPLOMACY",
     r"peace|treat(?:y|ies)|alliances?|allies|ally|envoys?|cabinet|talleyrand"
     r"|vassals?|clients?|satellites?|declare war|compacts?|buy off|sponsor|guarantee"
     r"|bid|relations|missions?|armistice|truce|negotiat\w*|diplomac\w*",
     ("diplomacy",)),
    ("ECONOMY",
     r"gold|money|treasury|build(?:ing)?s?|tax\w*|income|upkeep|rentes?|estates?"
     r"|endow\w*|reward\w*|debt|deficit|bankrupt\w*|markets?|depots?|economy",
     ("economy",)),
    ("TACTICAL COMMANDS",
     r"fortif\w+|dig in|drill\w*|train\w*|scout\w*|squares?",
     ("tactical",)),
    ("STANCE COMMANDS",
     r"stances?|aggressive|defensive|neutral",
     ("stance",)),
    ("GLORY AND GRIEVANCE",
     r"glory|envy|jealous\w*|grievances?|rivals?|quarrel\w*",
     ("glory",)),
    ("RETREAT RECOVERY",
     r"recover\w*|rally|demorali[sz]ed|broken",
     ("recovery",)),
    ("SCREENS & HOTKEYS",
     r"screens?|hot ?keys?|keys?|ledgers?|log|dispatch|arrows?|terminal|shortcuts?",
     ("screens", "hotkeys")),
    ("YOUR MARSHALS",
     r"abilit(?:y|ies)|famed|marshals' skills"
     # S14E-16's sweep: "how do I see my marshals" printed the whole manual.
     r"|(?:see|view|check|open|list|show)\s+(?:my\s+|our\s+|the\s+|all\s+)?(?:marshals|generals)",
     # Exact topic words only (S14E-D17): the bare noun in a QUESTION belongs
     # to the section the verb names ("how do I recruit marshals").
     ("marshals", "marshal", "generals", "general")),
    ("MILITARY COMMANDS",
     r"attack\w*|battles?|fight\w*|recruit\w*|troops|reinforce\w*|defend|retreat"
     r"|bombard\w*|artillery|garrisons?|laws?|enact|repeal|doctrines?|substitutes?|levy"
     # S14E-16's sweep: the verbs a first-time player asks the manual with.
     r"|moves?|moving|capture\w*|conquer\w*|seize\w*|beat|defeat\w*|raise",
     ("military", "combat")),
    # S14E-16 (S14f part 2): the MOVEMENT words, LAST so every noun above wins
    # first ("how do I go to the cabinet" is the Cabinet's, "how do I get
    # peace" diplomacy's) — "how do I get to Vienna" named no section, so the
    # fallback was the whole manual. A place the board knows is answered by
    # the desk's `route` kind; this is the fallback for one it does not.
    ("STRATEGIC COMMANDS",
     r"(?:get|go|travel|walk|ride)(?:es|ing)?\s+(?:to|towards?|into)\b(?!\s+war\b)"
     r"|travel(?:s|ed|led|ing|ling)?|(?:get|go)\s+(?:there|home|back|across)"
     r"|reach(?:es|ing)?\s+(?!an?\s)|(?:the\s+)?(?:way|road|route)s?\s+(?:to|towards?)"
     # "how do I get Ney to Vienna" / "march an army to Vienna"
     r"|(?:get|send|bring|take|march)\s+(?:my\s+|our\s+|the\s+|an?\s+)?[\w'-]+(?:\s+[\w'-]+)?"
     r"\s+(?:to|towards?|into)\b(?!\s+war\b)",
     ()),
    # The sweep: "how do I end the turn" printed the whole manual; the free
    # actions line is where the reference names it. "help free" is the exact
    # topic (S14E-D17) -- "free" in a question ("for free") names nothing.
    ("FREE ACTIONS",
     r"end (?:the |my |a |this )?turns?|end of (?:the |a )?turn",
     ("free", "free actions")),
)

_COMPILED = tuple((heading, re.compile(r"(?:^|\b)(?:" + words + r")\b", re.IGNORECASE))
                  for heading, words, _topics in HELP_SECTIONS)

# S14E-D17: `help <topic>` -> the heading it NAMES, read off the table's
# third column (the first match wins, so a repeated word names its first row).
def _topic_headings() -> Dict[str, str]:
    table: Dict[str, str] = {}
    for heading, _words, topics in HELP_SECTIONS:
        for topic in topics:
            table.setdefault(topic, heading)
    return table


_TOPIC_HEADING: Dict[str, str] = _topic_headings()

# "help navy", "help with the fleet", "help on diplomacy" — a topic word
# after `help`, and nothing else (P8-2: "help Davout" is no help request).
_HELP_REQUEST_RE = re.compile(
    r"^\s*help\s+(?:me\s+)?(?:with|on|about|for)?\s*(?:the\s+|our\s+|my\s+)?(?P<topic>[a-z][a-z' &-]*?)\s*[?.!]*\s*$",
    re.IGNORECASE)


def section_for(text: str) -> Optional[str]:
    """The heading of the ONE section `text` names, or None."""
    lowered = (text or "").strip().lower()
    if not lowered:
        return None
    for heading, pattern in _COMPILED:
        if pattern.search(lowered):
            return heading
    return None


def help_request_section(text: str) -> Optional[str]:
    """`help <topic>` → the topic's section heading; None for any other line
    (a bare `help`, or `help` before a name — "help Davout")."""
    m = _HELP_REQUEST_RE.match(text or "")
    if not m:
        return None
    topic = " ".join(m.group("topic").lower().split())
    # S14E-D17: the table's exact topic words first ("help marshals",
    # "help designs", "help free" -- nouns the question scan must not read).
    return _TOPIC_HEADING.get(topic) or section_for(topic)


# The function words a `help …` line can end on without naming a topic.
_BARE_HELP_TOPICS = frozenset(
    {"me", "us", "please", "with", "on", "about", "for", "the", "our", "my"})


def help_topic_asked(text: str) -> Optional[str]:
    """S14E-X231: the topic word of a `help <topic>` line, whether or not the
    reference has a section for it ("help loans" -> "loans"); None for any
    other line and for a bare `help` / `help me` / `help with`."""
    m = _HELP_REQUEST_RE.match(text or "")
    if not m:
        return None
    topic = " ".join(m.group("topic").lower().split())
    return None if (not topic or topic in _BARE_HELP_TOPICS) else topic


# "what are the commands?" / "what is the syntax?" -- a request for the LIST
# itself, which is what the whole reference is (S14E-D17 keeps the manual for
# it: the ruling is about "how do I <verb> <object>" lines that name nothing).
_WHOLE_REFERENCE_RE = re.compile(
    r"^\s*(?:(?:so|and|but|ok(?:ay)?|well)\b\s*,?\s*)?"
    r"what\s+(?:is|are)\s+the\s+(?:command|commands|order|orders|syntax)"
    r"(?:\s+(?:list|reference|syntax))?\s*[?.!]*\s*$",
    re.IGNORECASE)


# S14E-X233 (the sweep): the same request in the nouns a player reaches for
# ("list commands", "show me the commands", "command list", "the manual",
# "reference", "instructions", "which commands exist") -- the whole line, and
# nothing else on it. Each answered "I cannot interpret" while the bare
# "commands" printed the reference.
_REFERENCE_REQUEST_RE = re.compile(
    r"^\s*(?:please\s+)?(?:"
    r"(?:list|show|display|print|give)(?:\s+me)?(?:\s+(?:all|the|all\s+the|all\s+of\s+the))?"
    r"\s+(?:commands|syntax)"
    r"|(?:the\s+|a\s+)?(?:command\s+(?:list|reference|manual)|manual|reference|instructions)"
    r"|(?:the\s+)?list\s+of\s+(?:the\s+)?commands"
    r"|which\s+commands\s+(?:exist|are\s+there|do\s+you\s+(?:know|take))"
    # ("orders" is left out on purpose: "list orders" may mean the standing
    # orders of the Strategic Ledger's Orders tab, not the manual.)
    r")\s*[?.!]*\s*$",
    re.IGNORECASE)


def asks_for_the_whole_reference(text: str) -> bool:
    """True for "what are the commands", "list commands", "the manual" and
    their twins: the line asks for the whole list, so the index would be a
    worse answer than the manual."""
    return bool(_WHOLE_REFERENCE_RE.match(text or "")
                or _REFERENCE_REQUEST_RE.match(text or ""))


_LOWER_WORDS = frozenset({"and", "the", "of", "in", "a", "an", "to"})


def section_title(heading: str) -> str:
    """A table heading in title case: "PORTS AND THE CONTINENTAL SYSTEM" ->
    "Ports and the Continental System" ("THE EMPEROR'S DESIGNS" -> "The
    Emperor's Designs")."""
    words = (heading or "").lower().split()
    return " ".join(
        w if (i and w in _LOWER_WORDS) else w[:1].upper() + w[1:]
        for i, w in enumerate(words))


def _named_row(heading_line: str) -> Optional[Tuple[str, str]]:
    """(table heading, topic word) of the reference section whose heading
    line is `heading_line` (as the reference prints it, so "THE ADMIRALTY (the
    wooden wall ..." and "THE ADMIRALTY" both read the table's "navy"); None
    for a section the table does not name."""
    for heading, _words, topics in HELP_SECTIONS:
        if topics and (heading_line or "").startswith(heading):
            return heading, topics[0]
    return None


def section_index(help_text: str, unknown_topic: Optional[str] = None) -> str:
    """S14E-D17 / S14E-X142: the SECTION INDEX -- a `help` line the manual's
    size would bury in a four-line window gets the short list instead: one
    `help <topic>` line per section of the reference, in the reference's
    order, read off the very `reference_sections` cut and the table's topic
    words that `help_request_section` resolves (so every line printed can be
    typed back and prints its section). `unknown_topic` is a `help <topic>`
    the reference has no section on ("help loans"): the head line says so. A
    section the table has no topic for (the debug block, in a debug build) is
    left out -- the whole reference still holds it."""
    if unknown_topic:
        head = (f"The reference has no section on '{unknown_topic}', Sire. "
                "It has these - type one:")
    else:
        head = "Which part, Sire? The reference has these sections - type one:"
    lines = [head]
    for line in reference_sections(help_text):
        row = _named_row(line)
        if row:
            lines.append(f"  help {row[1]} — {section_title(row[0])}")
    lines.append("— or 'help' alone for the whole reference.")
    return "\n".join(lines)


def reference_sections(help_text: str) -> Dict[str, str]:
    """The reference cut at its headings: a line at column 0 that begins
    with a capital (a lower-case line at column 0 continues its heading),
    each section running to the next heading or the closing rule."""
    sections: Dict[str, str] = {}
    current: Optional[str] = None
    lines: List[str] = []
    for line in (help_text or "").splitlines():
        if line.startswith("═"):
            if current is not None:
                sections[current] = "\n".join(lines).rstrip()
            current, lines = None, []
            continue
        if line[:1].isupper():
            if current is not None:
                sections[current] = "\n".join(lines).rstrip()
            current, lines = line, [line]
            continue
        if current is not None:
            lines.append(line)
    if current is not None:
        sections[current] = "\n".join(lines).rstrip()
    return sections


def reference_section(help_text: str, heading: str) -> Optional[str]:
    """The section whose heading line begins with `heading`, or None."""
    for line, body in reference_sections(help_text).items():
        if line.startswith(heading):
            return body
    return None
