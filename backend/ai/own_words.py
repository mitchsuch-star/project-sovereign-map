"""Row IC, Session 3 (IC-10) — THE WORDS OF A TASK ON HIS OWN.

`docs/INDEPENDENT_COMMAND_SPEC.md` §8.2, §8.3, §8.6. What the typed line takes
for a marshal you set on his own, read BEFORE the order's own readers so no
word of it becomes a province ("hold Alsace on your own" held "Alsace On Your
Own"):

    the marks of judgement   "on your own" · "as you see fit" · "use your
                             judgement" · "at your discretion" — set aside,
                             recorded: the task is ON HIS OWN
    two provinces            "hold Milan and Piedmont" — one area
    the words that change    "Ney, more risk" · "less risk" · "be bolder" ·
    his task                 "be more careful" · "stand down" · "carry on"
    the questions — free     "Ney, what will you do?" · "what do you see?" ·
                             "can you take Tyrol?" · "why did you …?"

A task becomes ON HIS OWN when the line says so (a mark of judgement) or when
it carries a how-bold word to a bold or careful man — the read-back names
which (`own_order.reading_of_parse`). Nothing here decides anything: the
parse carries `own`, and `own_order.from_parse` gives it (golden rule 6 — the
words are the word table's, never the model's).
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

MARKS = ("on your own", "on his own", "as you see fit", "as he sees fit",
         "use your judgement", "use your judgment", "use his judgement", "use his judgment",
         "at your discretion", "at his discretion", "in your own way", "your own way")
# (the review, IC3-V: "hold Alsace on your own ground" is a place's words, not a mark)
_MARK_RE = re.compile(r"[\s,;]*\b(?:" + "|".join(re.escape(m) for m in MARKS) + r")\b"
                      r"(?!\s+(?:ground|soil|land|lands|territory|side|men|flank|front))[\s,;]*",
                      re.IGNORECASE)

CHANGES = {
    "more risk": ("risk", 1), "take more risk": ("risk", 1), "be bolder": ("risk", 1),
    "bolder": ("risk", 1), "boldly": ("risk", 1), "press harder": ("risk", 1),
    "less risk": ("risk", -1), "take less risk": ("risk", -1), "be more careful": ("risk", -1),
    "more carefully": ("risk", -1), "carefully": ("risk", -1), "careful": ("risk", -1),
    "stand down": ("stand_down", 0), "stand him down": ("stand_down", 0),
    "carry on": ("carry_on", 0), "go on": ("carry_on", 0), "continue": ("carry_on", 0),
    "keep going": ("carry_on", 0), "carry on with your task": ("carry_on", 0),
}
_CHANGE_RE = re.compile(r"^(?:" + "|".join(re.escape(k) for k in sorted(CHANGES, key=len, reverse=True))
                        + r")[\s.!]*$", re.IGNORECASE)

QUESTIONS = (
    ("night", re.compile(r"^(?:what\s+(?:will|would|are)\s+you\s+(?:do|doing)(?:\s+tonight)?|"
                         r"what(?:'s|\s+is)\s+your\s+plan|what\s+do\s+you\s+(?:plan|intend)(?:\s+to\s+do)?|"
                         r"what\s+next)[\s?.!]*$", re.IGNORECASE)),
    ("sight", re.compile(r"^(?:what\s+do\s+you\s+see|what(?:'s|\s+is)\s+in\s+front\s+of\s+you|"
                         r"what\s+can\s+you\s+see|who(?:'s|\s+is)\s+near(?:\s+you)?)[\s?.!]*$",
                         re.IGNORECASE)),
    ("can", re.compile(r"^(?:can|could)\s+you\s+take\s+(?P<place>[^,;]+?)\s*\?\s*$",
                       re.IGNORECASE)),
    ("why", re.compile(r"^why\s+did\s+you\b.*$", re.IGNORECASE)),
)


def _address(text: str, names: List[str]) -> Tuple[str, str]:
    """`(marshal, rest)` for "Ney, …" / "Ney …" — ("", text) without one."""
    stripped = text.strip()
    for name in sorted(names, key=len, reverse=True):
        for spelled in {name, name.replace("Massena", "Masséna")}:
            m = re.match(r"^\s*" + re.escape(spelled) + r"\b[\s,:;]*(?P<rest>.*)$", stripped,
                         re.IGNORECASE | re.DOTALL)
            if m:
                return name, m.group("rest").strip()
    return "", stripped


def set_aside_marks(text: str) -> Tuple[str, List[str]]:
    """The line without its marks of judgement, and the marks found."""
    found = [m.group(0).strip(" ,;") for m in _MARK_RE.finditer(text or "")]
    if not found:
        return text, []

    def _the_gap(m: "re.Match") -> str:
        # Row IC, Session 3b (the metamorphic corpus, on this session's first
        # golden row with a mark): the mark took the comma beside it with it —
        # "Ney, take Swabia on your own, the men are rested" lost the comma that
        # sets the reason apart, and "take Swabia on your own, Ney" the one that
        # sets the name apart; both lines were then no order at all. A comma
        # that stood between the mark and MORE WORDS stays.
        joined = "," in m.group(0) or ";" in m.group(0)
        after = m.string[m.end():].strip(" .!?,;")
        more_before = bool(m.string[:m.start()].strip())
        if not (joined and after and more_before):
            return " "
        # "…on your own, carefully": a how-bold word is the task's own word and
        # rides with it, as it always did (the comma would set it apart as a
        # remark, and the task would lose its step)
        from backend.ai import task_words as _tw
        if after.lower() in {str(w).lower() for w in tuple(_tw.BOLDER_WORDS) + tuple(_tw.CAREFUL_WORDS)}:
            return " "
        return ", "

    cleaned = _MARK_RE.sub(_the_gap, text)
    cleaned = re.sub(r"\s+([.!?])", r"\1", re.sub(r"\s{2,}", " ", cleaned)).strip()
    return cleaned, found


def free_task(text: str, names: List[str]) -> Optional[Tuple[str, int]]:
    """Row IC, Session 4b (IC4-D3): `(marshal, risk)` when a line, read WITHOUT
    its marks of judgement (`set_aside_marks`), sets a man on his own with NO
    task — "Ney, act on your own" · "Ney, as you see fit" · "Ney, make war as
    you see fit" (the word table's `FREE_TASK`; a how-bold word may ride with
    it) — else None. Only the caller knows a mark was there."""
    marshal, rest = _address(text or "", names)
    if not marshal:
        return None
    from backend.ai import task_words as _tw
    words = re.sub(r"\s+", " ", rest.strip(" .!,;").lower())
    risk = 0
    for bold in tuple(_tw.BOLDER_WORDS) + tuple(_tw.CAREFUL_WORDS):
        for form in (f" {bold}", f"{bold} "):
            if words.endswith(form) or words.startswith(form):
                words = (words[:-len(form)] if words.endswith(form) else words[len(form):]).strip()
                risk = 1 if bold in _tw.BOLDER_WORDS else -1
                break
        if risk:
            break
        if words == bold:
            words, risk = "", (1 if bold in _tw.BOLDER_WORDS else -1)
            break
    if not words or words in tuple(getattr(_tw, "FREE_TASK", ()) or ()):
        return marshal, risk
    return None


def read_line(text: str, names: List[str], regions: List[str],
              own_names: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
    """A question to a man, or a word that changes the task of a man ON HIS OWN
    (`own_names`), as a parse — None for anything else (the ordinary readers
    take it: "Ney, carry on" to a man who is not on his own means what it
    always meant)."""
    text = text or ""
    marshal, rest = _address(text, names)
    if not marshal or not rest:
        return None
    lowered = rest.strip().lower()
    for kind, rx in QUESTIONS:
        m = rx.match(lowered)
        if not m:
            continue
        place = ""
        if kind == "can":
            wanted = m.group("place").strip(" ?.!").lower()
            for region in regions:
                if region.lower() == wanted or region.lower().replace("-", " ") == wanted:
                    place = region
                    break
            if not place:
                return None     # not a province: the ordinary readers take the line
        return {"success": True, "raw_input": text, "mode": "mock",
                "command": {"marshal": marshal, "action": "help", "type": "specific",
                            "raw_command": text, "mode": "mock",
                            "question": {"kind": f"own_{kind}", "subject": marshal,
                                         "subject_type": "marshal", "place": place,
                                         "asked": text}}}
    m = _CHANGE_RE.match(lowered)
    if m and marshal in (own_names or []):
        kind, step = CHANGES[lowered.strip(" .!")]
        return {"success": True, "raw_input": text, "mode": "mock",
                "own": {"kind": kind, "step": int(step), "line": text},
                "command": {"marshal": marshal, "action": "own_task", "type": "specific",
                            "raw_command": text, "mode": "mock"}}
    return None


# Row IC, Session 3b (§9): "Ney, take the war goal" — the task that follows
# the goal you named for the war. The words are read here; what they mean on
# the board today (a place to take, an army in sight to chase — or why not) is
# `war_goals.task_for`'s to say.
def _goal_re() -> "re.Pattern":
    # the words are the word table's (`word_table.GOAL_VERBS` / `GOAL_OBJECT`)
    from backend.ai import task_words as _tw

    def alt(phrases) -> str:
        return "|".join(re.escape(p).replace(r"\ ", r"\s+")
                        for p in sorted(phrases, key=len, reverse=True))
    return re.compile(r"\b(?:" + alt(_tw.GOAL_VERBS) + r")\s+(?:" + alt(_tw.GOAL_OBJECTS) + r")\b",
                      re.IGNORECASE)


_GOAL_RE = _goal_re()


def the_war_goal(text: str, names: List[str]) -> Optional[Tuple[str, int, int]]:
    """`(marshal, start, end)` — the man a line addresses and the span of its
    "take the war goal" — or None when the line is no such task (a question
    never is: "Ney, can you take the war goal?")."""
    text = text or ""
    if text.strip().endswith("?"):
        return None
    marshal, _rest = _address(text, names)
    if not marshal:
        return None
    found = _GOAL_RE.search(text)
    if found is None:
        return None
    return marshal, found.start(), found.end()


def two_provinces(text: str, regions: List[str], marked: bool = True) -> Tuple[str, str]:
    """"Masséna, hold Milan and Piedmont" → ("Masséna, hold Milan", "Piedmont")
    when both are provinces; else (text, "")."""
    if not marked:
        return text, ""     # (the review, IC3-V: an exact order keeps its words whole)
    m = re.match(r"^(?P<head>.*\bhold\s+)(?P<a>[A-Z][\w\-' ]+?)\s+and\s+(?P<b>[A-Z][\w\-' ]+?)"
                 r"(?P<tail>[\s,.;!].*)?$", text or "")
    if not m:
        return text, ""
    known = {r.lower(): r for r in regions}
    a, b = known.get(m.group("a").strip().lower()), known.get(m.group("b").strip().lower())
    if not a or not b:
        return text, ""
    return f"{m.group('head')}{m.group('a').strip()}{m.group('tail') or ''}", b
