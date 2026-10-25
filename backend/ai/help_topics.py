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
"""
from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple

# (section heading as the reference prints it, the words that name it) — in
# precedence order: the narrower naval section before the Admiralty, several
# marshals before a single attack, the reign's victory before a battle's.
HELP_SECTIONS: Tuple[Tuple[str, str], ...] = (
    ("PORTS AND THE CONTINENTAL SYSTEM",
     r"ports?|harbou?rs?|continental system|the system|closure|embargo|smuggl\w*"),
    ("THE ADMIRALTY",
     r"fleets?|navy|navies|naval|ships?|sail|keels?|blockad\w*|admiralty|admirals?"
     r"|readiness|postures?|crossings?|channel|expeditions?|landings?|land \w+ in"
     r"|diversion|descent|dock ?yards?|yards?|the sea|at sea|invade (?:britain|england)"),
    ("STRATEGIC COMMANDS",
     r"several marshals|two marshals|more than one marshal|marshals together"
     r"|together|combine\w*|join forces|both|support|follow|everyone|all (?:my )?marshals"
     r"|the army|pursu\w+|chase|march(?:es|ing)? to|standing orders?|cancel|halt"),
    ("TWO ORDERS IN ONE LINE",
     r"two orders|chain\w*|sequence|then|until|if \w+ (?:advances|comes)|in one line"),
    ("THE CONGRESS OF PARIS",
     r"congress|imperial peace|recogni[sz]\w*|titled|win the (?:game|campaign|reign|war)"
     r"|^how (?:do|can) (?:i|we) win(?=[?.!\s]*$)"),
    ("DIPLOMACY",
     r"peace|treat(?:y|ies)|alliances?|allies|ally|envoys?|cabinet|talleyrand"
     r"|vassals?|clients?|satellites?|declare war|compacts?|buy off|sponsor|guarantee"
     r"|bid|relations|missions?|armistice|truce|negotiat\w*|diplomac\w*"),
    ("ECONOMY",
     r"gold|money|treasury|build(?:ing)?s?|tax\w*|income|upkeep|rentes?|estates?"
     r"|endow\w*|reward\w*|debt|deficit|bankrupt\w*|markets?|depots?|economy"),
    ("TACTICAL COMMANDS",
     r"fortif\w+|dig in|drill\w*|train\w*|scout\w*|squares?"),
    ("STANCE COMMANDS",
     r"stances?|aggressive|defensive|neutral"),
    ("GLORY AND GRIEVANCE",
     r"glory|envy|jealous\w*|grievances?|rivals?|quarrel\w*"),
    ("RETREAT RECOVERY",
     r"recover\w*|rally|demorali[sz]ed|broken"),
    ("SCREENS & HOTKEYS",
     r"screens?|hot ?keys?|keys?|ledgers?|log|dispatch|arrows?|terminal|shortcuts?"),
    ("YOUR MARSHALS",
     r"abilit(?:y|ies)|famed|marshals' skills"
     # S14E-16's sweep: "how do I see my marshals" printed the whole manual.
     r"|(?:see|view|check|open|list|show)\s+(?:my\s+|our\s+|the\s+|all\s+)?(?:marshals|generals)"),
    ("MILITARY COMMANDS",
     r"attack\w*|battles?|fight\w*|recruit\w*|troops|reinforce\w*|defend|retreat"
     r"|bombard\w*|artillery|garrisons?|laws?|enact|repeal|doctrines?|substitutes?|levy"
     # S14E-16's sweep: the verbs a first-time player asks the manual with.
     r"|moves?|moving|capture\w*|conquer\w*|seize\w*|beat|defeat\w*|raise"),
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
     r"\s+(?:to|towards?|into)\b(?!\s+war\b)"),
    # The sweep: "how do I end the turn" printed the whole manual; the free
    # actions line is where the reference names it.
    ("FREE ACTIONS",
     r"end (?:the |my |a |this )?turns?|end of (?:the |a )?turn"),
)

_COMPILED = tuple((heading, re.compile(r"(?:^|\b)(?:" + words + r")\b", re.IGNORECASE))
                  for heading, words in HELP_SECTIONS)

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
    return section_for(m.group("topic"))


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
