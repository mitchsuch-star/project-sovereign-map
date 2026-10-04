"""CRT-11 "The second name is heard" — a second name is a ROLE, never a
second order (SCORE_FINISH_SPEC.md §3 Step 4, Chunk 3b trimmed to what the
census confirms; COMMAND_ROBUSTNESS_SPEC.md §12.16; rules
SYSTEMS_REFERENCE.md §89).

A marshal named INSIDE an order to another marshal is the order's object —
the man to support — not a man being given an order of his own. The
supporting phrasings an officer writes had no reading:

  * "Marshal Soult, bring your corps up in support of Ney."
        -> "Cannot find marshal 'Of Ney' to support."     (played, turn 1)
  * "Soult, march in support of Ney"
        -> a 1-action march to the province "In Support Of Ney"
  * "Soult, march to the aid of Ney"  -> a march to "Aid Of Ney"
  * "Soult, come to Ney's support"    -> "You wish me to support Bernadotte?"
  * "Lannes, follow Ney in and back him up." -> "the instruction is unclear"

(BUG_FIXES.md RS-6; the HOLD arm's blind line.) Each is the engine's own
SUPPORT order, said another way, and is restated as ``<address>, support
<Name>`` BEFORE any reader sees the line — the W2 precedent
(`condition_grammar.rewrite_engagement_support`): the fast parser, the
strategic layer, the word scan and the sequential split then agree by
construction. The typed text stays the record (`CommandParser.parse`
restores ``raw_input`` / ``raw_command``).

Only a marshal of OURS is ever restated: "march to the aid of Mack" names
no order the engine has, and is left for the honest refusal. Deterministic
throughout (Golden Rule 6); flip lever ``THE_SUPPORT_ROLE_IS_HEARD``.
"""

from __future__ import annotations

import re
from typing import Iterable, Optional, Tuple

from backend.ai.clause_guards import HONORIFIC

THE_SUPPORT_ROLE_IS_HEARD = True

# The movement lead an officer puts in front of the supporting phrase. It is
# consumed WITH the phrase — left behind, "march" would claim the sentence as
# a MOVE_TO again ("Soult, march support Ney").
_UNIT_NOUN = r"(?:corps|men|troops|army|cavalry|horse|division|divisions|guns|columns?|force)"
_MOVE_LEAD = (
    r"(?:(?:march|move|ride|come|go|hasten|hurry|advance|push|press|head|proceed"
    r"|race|rush|fly|wheel|swing)"
    r"|bring\s+(?:up\s+)?(?:your|his|the|thy)\s+" + _UNIT_NOUN
    + r"|bring\s+(?:your|his|the|thy)\s+" + _UNIT_NOUN + r"\s+up)"
    r"(?:\s+(?:up|over|forward|on|round|across))?"
    r"(?:\s+(?:at\s+once|quickly|swiftly|now|immediately|with\s+all\s+speed|in\s+haste))?\s+")
_SUPPORT_NOUNS = r"support|aid|assistance|relief|rescue|succou?r"
_SUPPORT_NOUN = r"(?:" + _SUPPORT_NOUNS + r")"
_BACKING_VERB = (r"(?:back|support|reinforce|help|cover|second|join|assist|aid"
                 r"|stand\s+by|stick\s+with|stay\s+with)")


def _friend_alternation(friendly_names: Iterable[str]) -> str:
    names = sorted({str(n) for n in (friendly_names or ()) if n},
                   key=len, reverse=True)
    return "|".join(re.escape(n) for n in names)


def _patterns(friends: str):
    head = (r"^(?P<head>\s*(?:(?:" + HONORIFIC + r")?[A-Za-z][\w'’-]*"
            r"(?:\s+[A-Za-z][\w'’-]*)?\s*[,:]\s*)?)"
            r"(?:(?:please|now)\s+)?")
    named = r"(?:" + HONORIFIC + r")?(?P<friend>" + friends + r")\b"
    return (
        # "(march) in support of Ney" / "to the aid of Ney" / "in aid of Ney"
        re.compile(head + r"(?:" + _MOVE_LEAD + r")?"
                   r"(?:in|to\s+the)\s+" + _SUPPORT_NOUN + r"\s+of\s+" + named,
                   re.IGNORECASE),
        # "(come) to Ney's support" / "to Ney's aid" / "to Ney's side"
        re.compile(head + r"(?:" + _MOVE_LEAD + r")?"
                   r"to\s+(?:" + HONORIFIC + r")?(?P<friend>" + friends + r")['’]s\s+"
                   r"(?:" + _SUPPORT_NOUNS + r"|side|help)\b",
                   re.IGNORECASE),
        # "follow Ney (in) (and back him up)"
        re.compile(head + r"follow\s+" + named
                   + r"(?:\s+(?:in|up|on|closely|close|forward|into\s+(?:battle|the\s+fight|action)))?"
                   r"(?:\s*,?\s+and\s+" + _BACKING_VERB
                   + r"\s+(?:him|her|them|(?:" + HONORIFIC + r")?(?P=friend))(?:\s+up)?\b)?",
                   re.IGNORECASE),
        # "back Ney up"
        re.compile(head + r"back\s+" + named + r"\s+up\b", re.IGNORECASE),
    )


def rewrite_support_role(text: str,
                         friendly_names: Iterable[str]) -> Tuple[str, Optional[str]]:
    """``(rewritten_text, friend)`` when the line orders SUPPORT of one of
    our marshals in a phrasing the engine had no reading for; ``(text,
    None)`` otherwise. Whatever follows the phrase is kept ("… until the
    battle is won", a second clause)."""
    if not THE_SUPPORT_ROLE_IS_HEARD or not text:
        return text, None
    friends = _friend_alternation(friendly_names)
    if not friends:
        return text, None
    for pattern in _patterns(friends):
        m = pattern.match(text)
        if not m:
            continue
        typed = m.group("friend")
        friend = next((n for n in friendly_names
                       if str(n).lower() == typed.lower()), typed)
        head = m.group("head") or ""
        rebuilt = f"{head}support {friend}{text[m.end():]}"
        return rebuilt, friend
    return text, None
