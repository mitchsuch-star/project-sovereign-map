"""FA slice 7 (Sept 2026) — THE QUESTION DESK, FA-D25's cheap join.

Two halves, one file, so the vocabulary they share is written once:

  classify_question(text, marshals, enemies, regions) -> Optional[dict]
      parser-side and PURE — reads only the rosters the parser already has
      and never touches the world (Golden Rule 6: parsing only).

  answer_question(world, question) -> Optional[str]
      executor-side and FOG-HONEST — own marshals omniscient, enemies
      through the intel store exactly as Berthier's report reads them, a
      province's holder public (the map already paints it).

Only FACT questions the intelligence report already answers are taken:
where a man stands, who holds a province, who is in it, what a marshal is
doing, how many men he has. Feasibility and advice ("can I attack Mack?",
"should Ney...", "how far...") stay on the COMMAND REFERENCE — that is
CR-8's advisory desk to replace, on its own gate — and the four corpus rows
pinning `can I attack Mack?` -> help are untouched by construction.

Measured before this desk existed (Agent F, Sept 4, 2026): every one of
`where is Mack?` / `who holds Swabia?` / `what is Davout doing?` / `how many
men does Ney have?` printed the 9,630-character COMMAND REFERENCE.
"""
from __future__ import annotations

import re
from typing import Dict, Iterable, List, Optional, Tuple

from backend.ai.clause_guards import HONORIFIC

# Flip lever: False makes classify_question() return None for everything, so
# every question falls back to the pre-slice `help` route byte-for-byte.
QUESTION_DESK_ACTIVE = True

_APOS = "['’]"
_HON = r"(?:" + HONORIFIC + r")?"
_ADDR = r"(?:" + _HON + r"[A-Za-z][\w'’-]*\s*,\s*)?"
_LEAD = r"^\s*(?:so\s+|and\s+|but\s+|ok(?:ay)?\s*,?\s*|well\s*,?\s*)?" + _ADDR
_TAIL = (r"(?:\s+(?:now|today|at present|this turn|right now|at the moment))?"
         r"\s*[?.!]*\s*$")
_POSSESSIVE_TAIL = r"(?:" + _APOS + r"s\s+(?:corps|men|army|troops|division))?"

_KINDS: List[Tuple[str, "re.Pattern[str]"]] = [
    ("where", re.compile(
        _LEAD + r"where(?:" + _APOS + r"s|\s+is|\s+are)\s+" + _HON
        + r"(?:the\s+)?(?P<name>.+?)" + _POSSESSIVE_TAIL + _TAIL, re.IGNORECASE)),
    ("who_holds", re.compile(
        _LEAD + r"who\s+(?:holds|controls|owns|has|rules|governs)\s+(?:the\s+)?"
        r"(?P<name>.+?)" + _TAIL, re.IGNORECASE)),
    ("who_at", re.compile(
        _LEAD + r"who(?:" + _APOS + r"s|\s+is|\s+are)\s+(?:at|in|near|around)\s+"
        r"(?:the\s+)?(?P<name>.+?)" + _TAIL, re.IGNORECASE)),
    ("doing", re.compile(
        _LEAD + r"what(?:" + _APOS + r"s|\s+is|\s+are)\s+" + _HON
        + r"(?P<name>.+?)\s+(?:doing|up to|about)" + _TAIL, re.IGNORECASE)),
    ("how_many", re.compile(
        _LEAD + r"how\s+(?:"
        r"many\s+(?:men|troops|soldiers)\s+(?:does|do|has|have)\s+" + _HON
        + r"(?P<name>.+?)(?:\s+(?:have|got|command|left|under\s+arms))?"
        r"|strong\s+is\s+" + _HON + r"(?P<name2>.+?)" + _POSSESSIVE_TAIL
        + r"|big\s+is\s+" + _HON + r"(?P<name3>.+?)" + _POSSESSIVE_TAIL
        + r")" + _TAIL, re.IGNORECASE)),
]


def _norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()


def _forms(name: str) -> List[str]:
    """Every register the game prints a name in (camelCase split, hyphen
    spaces) — ONE source, llm_client's, lazily imported (it imports this
    module lazily too, so neither loads the other at import time)."""
    from backend.ai.llm_client import name_match_patterns
    return sorted({_norm(p) for p in name_match_patterns(name)} | {_norm(name)})


def _resolve(phrase: str, marshals: Iterable[str], enemies: Iterable[str],
             regions: Iterable[str]) -> Optional[Tuple[str, str]]:
    """(canonical name, subject type) for the phrase, or None. Exact whole-
    phrase matches win in roster order own -> enemy -> region; failing that,
    the ONE name across all three rosters that appears as whole words inside
    the phrase; two candidates or none -> None (the desk does not guess)."""
    want = _norm(phrase)
    if not want:
        return None
    rosters = (("marshal", list(marshals)), ("enemy", list(enemies)),
               ("region", list(regions)))
    for kind, names in rosters:
        for name in names:
            if want in _forms(name):
                return (name, kind)
    contained = []
    for kind, names in rosters:
        for name in names:
            for form in _forms(name):
                if form and re.search(r"(?:^|\s)" + re.escape(form) + r"(?:\s|$)", want):
                    contained.append((name, kind))
                    break
    return contained[0] if len(contained) == 1 else None


def classify_question(text: str, marshals: Iterable[str] = (),
                      enemies: Iterable[str] = (),
                      regions: Iterable[str] = ()) -> Optional[Dict]:
    """The fact question in `text`, or None (the caller keeps `help`)."""
    if not QUESTION_DESK_ACTIVE or not text:
        return None
    for kind, pattern in _KINDS:
        match = pattern.match(text.strip())
        if not match:
            continue
        groups = match.groupdict()
        phrase = next((g for g in (groups.get("name"), groups.get("name2"),
                                   groups.get("name3")) if g), "")
        resolved = _resolve(phrase, marshals, enemies, regions)
        if resolved is None:
            return None
        subject, subject_type = resolved
        return {"kind": kind, "subject": subject, "subject_type": subject_type}
    return None


# ── the executor-side half ────────────────────────────────────────────────

def _display(name: str) -> str:
    from backend.display_names import humanize_entity_name
    return humanize_entity_name(name)


def _court(world, nation: str) -> str:
    if not nation:
        return "no one"
    try:
        from backend.game_logic.formations import formed_display_name
        return formed_display_name(world, nation)
    except Exception:
        return str(nation)


def _order_clause(marshal) -> str:
    order = getattr(marshal, "strategic_order", None)
    if not order:
        return ""
    kind = str(getattr(order, "command_type", "") or "").replace("_", " ").lower()
    target = getattr(order, "target", None)
    if target and target != "generic":
        return f" Under a standing {kind} order — {_display(str(target))}."
    return f" Under a standing {kind} order."


def _state_words(marshal) -> List[str]:
    words = []
    if getattr(marshal, "fortified", False):
        words.append("fortified")
    if getattr(marshal, "square_formation", False):
        words.append("in square")
    if getattr(marshal, "broken", False):
        words.append("broken and recovering")
    elif int(getattr(marshal, "retreat_recovery", 0) or 0) > 0:
        words.append("recovering from a retreat")
    return words


def _last_report_of(world, name: str) -> Optional[Tuple[str, int]]:
    """(region, turns ago) of the freshest STALE/LAST_KNOWN intel snapshot
    naming this marshal — a one-off scan for a typed question, not a hot
    path (the intelligence report makes the same pass)."""
    from backend.models.intel import LAST_KNOWN, STALE
    best = None
    for region_name in world.regions.keys():
        intel = world.get_region_intel(region_name)
        if intel.visibility not in (STALE, LAST_KNOWN):
            continue
        known = getattr(intel, "known_marshals", None) or []
        names = [k.get("name") if isinstance(k, dict) else k for k in known]
        if name in names:
            ago = int(world.current_turn - intel.last_updated_turn)
            if best is None or ago < best[1]:
                best = (region_name, ago)
    return best


def _answer_region(world, kind: str, region_name: str) -> Optional[str]:
    from backend.models.intel import FULL, LAST_KNOWN, PARTIAL, STALE, UNKNOWN
    region = world.get_region(region_name)
    if region is None:
        return None
    player = world.player_nation
    holder = _court(world, region.controller)
    own_soil = region.controller == player
    if kind == "who_holds":
        return (f"{region_name} is ours, Sire." if own_soil
                else f"{region_name} is held by {holder}.")
    if kind == "where":
        adjacent = ", ".join(getattr(region, "adjacent_regions", []) or [])
        whose = "our own soil" if own_soil else f"held by {holder}"
        return f"{region_name} ({whose}) adjoins {adjacent or 'no province we know of'}."
    # who_at / doing / how_many on a province: who stands there
    lines = []
    own = [m for m in world.get_marshals_in_region(region_name)
           if m.nation == player and m.strength > 0]
    if own:
        lines.append("Our own: " + ", ".join(
            f"{_display(m.name)} ({int(m.strength):,})" for m in own) + ".")
    intel = world.get_region_intel(region_name)
    vis = intel.visibility
    if vis == FULL:
        foes = [m for m in world.get_marshals_in_region(region_name)
                if m.nation != player and m.strength > 0]
        if foes:
            lines.append("Confirmed: " + ", ".join(
                f"{_display(m.name)} of {_court(world, m.nation)} ({int(m.strength):,})"
                for m in foes) + ".")
    elif vis in (PARTIAL, STALE, LAST_KNOWN):
        known = getattr(intel, "known_marshals", None) or []
        names = [k.get("name") if isinstance(k, dict) else k for k in known]
        if names:
            ago = int(world.current_turn - intel.last_updated_turn)
            when = "this turn" if ago <= 0 else f"{ago} turn{'s' if ago != 1 else ''} ago"
            lines.append(f"Reported: {', '.join(_display(n) for n in names)} — "
                         f"{intel.strength_band}, {when}.")
    elif vis == UNKNOWN and not own:
        return f"No word from {region_name}, Sire — it has not been scouted."
    if not lines:
        return f"No army stands in {region_name} that we know of, Sire ({holder} holds it)."
    return f"{region_name} ({holder}): " + " ".join(lines)


def _answer_own_marshal(world, kind: str, marshal) -> str:
    name = _display(marshal.name)
    if getattr(marshal, "captured_by", ""):
        return (f"Marshal {name} is a prisoner of {_court(world, marshal.captured_by)}, "
                f"Sire — no order can reach him until his release.")
    where = (f"Marshal {name} stands at {marshal.location} with "
             f"{int(marshal.strength):,} men (morale {int(marshal.morale)}).")
    if kind == "how_many":
        return (f"Marshal {name} commands {int(marshal.strength):,} men at "
                f"{marshal.location}, morale {int(marshal.morale)}.")
    if kind == "doing":
        states = _state_words(marshal)
        clause = _order_clause(marshal)
        if clause:
            return f"Marshal {name} is at {marshal.location}.{clause}" + (
                f" He is {', '.join(states)}." if states else "")
        if states:
            return f"Marshal {name} is {', '.join(states)} at {marshal.location}."
        return f"Marshal {name} awaits orders at {marshal.location}."
    return where + _order_clause(marshal)


def _answer_enemy(world, kind: str, name: str) -> str:
    from backend.models.intel import FULL
    player = world.player_nation
    shown = _display(name)
    marshal = world.get_marshal(name)
    if marshal is None:
        tomb = (getattr(world, "fallen_marshals", None) or {}).get(name)
        if tomb:
            return (f"{shown}'s corps no longer exists, Sire — it was destroyed at "
                    f"{tomb.get('location') or 'the field'} on turn "
                    f"{int(tomb.get('turn') or 0)}.")
        return f"We have no record of {shown}, Sire."
    captor = getattr(marshal, "captured_by", "")
    if captor == player:
        return f"{shown} is our prisoner at {marshal.location}, Sire — he leads no army."
    if captor:
        return f"{shown} is a prisoner of {_court(world, captor)}, Sire — he leads no army."
    court = _court(world, marshal.nation)
    visible = any(m.name == marshal.name for m in world.get_visible_enemies(player))
    if visible:
        intel = world.get_region_intel(marshal.location)
        if intel.visibility == FULL:
            states = _state_words(marshal)
            if kind == "how_many":
                return (f"{shown} of {court} has {int(marshal.strength):,} men at "
                        f"{marshal.location} — confirmed this turn.")
            if kind == "doing":
                stance = getattr(getattr(marshal, "stance", None), "value", None) or "neutral"
                return (f"{shown} of {court} stands at {marshal.location} in a {stance} "
                        f"stance" + (f", {', '.join(states)}" if states else "") + ".")
            return (f"{shown} of {court} is at {marshal.location} — "
                    f"{int(marshal.strength):,} men, confirmed this turn"
                    + (f", {', '.join(states)}" if states else "") + ".")
        band = getattr(intel, "strength_band", None) or "strength unknown"
        return f"{shown} of {court} was reported at {marshal.location} — {band}."
    last = _last_report_of(world, marshal.name)
    if last:
        region_name, ago = last
        when = "this turn" if ago <= 0 else f"{ago} turn{'s' if ago != 1 else ''} ago"
        return (f"{shown} of {court} was last reported at {region_name}, {when}; "
                f"we have no fresher word.")
    return f"We have no word of {shown}'s whereabouts, Sire."


def answer_question(world, question: Optional[Dict]) -> Optional[str]:
    """Berthier's one-line answer, or None when the desk cannot answer (the
    caller falls back to the full intelligence report)."""
    if not question or not QUESTION_DESK_ACTIVE or world is None:
        return None
    kind = str(question.get("kind") or "")
    subject = str(question.get("subject") or "")
    subject_type = str(question.get("subject_type") or "")
    if not kind or not subject:
        return None
    try:
        if subject_type == "region":
            return _answer_region(world, kind, subject)
        if subject_type == "marshal":
            marshal = world.get_marshal(subject)
            if marshal is None or marshal.nation != world.player_nation:
                return _answer_enemy(world, kind, subject)
            return _answer_own_marshal(world, kind, marshal)
        if subject_type == "enemy":
            return _answer_enemy(world, kind, subject)
    except Exception as exc:  # the desk must never break the status verb
        print(f"[QUESTION DESK] could not answer {question!r}: {exc}")
        return None
    return None
