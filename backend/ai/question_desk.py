"""FA slice 7 (Sept 2026) — THE QUESTION DESK, FA-D25's cheap join.

Two halves, one file, so the vocabulary they share is written once:

  classify_question(text, marshals, enemies, regions) -> Optional[dict]
      parser-side and PURE — reads only the rosters the parser already has
      and never touches the world (Golden Rule 6: parsing only).

  answer_question(world, question) -> Optional[str]
      executor-side and FOG-HONEST — own marshals omniscient, enemies
      through the intel store exactly as Berthier's report reads them, a
      province's holder public (the map already paints it).

Only FACT questions the intelligence report already answers are taken by the
FIRST half: where a man stands, who holds a province, who is in it, what a
marshal is doing, how many men he has.

Measured before this desk existed (Agent F, Sept 4, 2026): every one of
`where is Mack?` / `who holds Swabia?` / `what is Davout doing?` / `how many
men does Ney have?` printed the 9,630-character COMMAND REFERENCE.

⚠ THE PARAGRAPH THAT USED TO STAND HERE IS NOW FALSE, AND IS CORRECTED
RATHER THAN DELETED. It read: *"Feasibility and advice ('can I attack
Mack?', 'should Ney…', 'how far…') stay on the COMMAND REFERENCE — that is
CR-8's advisory desk to replace, on its own gate — and the four corpus rows
pinning `can I attack Mack?` -> help are untouched by construction."*

**CX-2 (September 19, 2026) took feasibility**, on ruling R7's own re-open
condition — *"A question-answering Berthier is CR-6's to build; when it
exists, it replaces the `help` route, not the guard."* `can I attack Mack?`
and `should Ney attack Mack` are answered with the REAL muster preview, the
same `_format_muster_lines` string the attack itself prints, and the guard is
untouched: no battle, no action point. The corpus rows are flipped
consciously with their reason on the row, and their legacy twins still pin
the help route where the desk cannot classify the foe.

What is still NOT taken, and stays CR-8's: open-ended ADVICE ("what should I
do about Prussia", "is this wise"), and questions about the game's GRAMMAR
("how do I attack?"), for which the command reference genuinely is the
answer — `llm_client._SYNTAX_QUESTION_RE` keeps those on it.

The CX-2 half below (`classify_board_question` / `answer_board_question`)
answers the BOARD: the treasury, the war score, a court's design, whether a
corps can reach a province, what an attack would look like, what may be built
and what it costs, and what can be ordered at all.
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
        _LEAD + r"(?:how\s+(?:"
        r"many\s+(?:men|troops|soldiers)\s+(?:does|do|has|have)\s+" + _HON
        + r"(?P<name>.+?)(?:\s+(?:have|got|command|left|under\s+arms))?"
        r"|strong\s+is\s+" + _HON + r"(?P<name2>.+?)" + _POSSESSIVE_TAIL
        + r"|big\s+is\s+" + _HON + r"(?P<name3>.+?)" + _POSSESSIVE_TAIL
        + r")"
        # First contact (Sept 23, 2026): "is Mack strong" / "is Mack
        # dangerous" — the strength answer, asked the way a player asks
        # it. It routed to the unanswered tail while "how strong is
        # Mack" was answered a line above.
        + r"|(?:is|are)\s+" + _HON + r"(?P<name4>.+?)\s+"
        r"(?:strong|weak|powerful|dangerous|formidable|big|large|small"
        r"|a\s+threat|threatening|beatable|beaten)"
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


_REGION_FIRST_KINDS = frozenset({"who_holds", "who_at"})


def _resolve(phrase: str, marshals: Iterable[str], enemies: Iterable[str],
             regions: Iterable[str], kind: str = "") -> Optional[Tuple[str, str]]:
    """(canonical name, subject type) for the phrase, or None. Exact whole-
    phrase matches win in roster order — regions FIRST for "who holds" /
    "who is at" (the review round, R1-12 / R3-3: "who holds Brunswick?" was
    answered about the Prussian marshal), marshals first otherwise; failing
    that, the ONE name across all three rosters that appears as whole words
    inside the phrase; two candidates or none -> None (the desk does not
    guess)."""
    want = _norm(phrase)
    if not want:
        return None
    rosters = [("marshal", list(marshals)), ("enemy", list(enemies)),
               ("region", list(regions))]
    if kind in _REGION_FIRST_KINDS:
        rosters = [rosters[2], rosters[0], rosters[1]]
    for subject_type, names in rosters:
        for name in names:
            if want in _forms(name):
                return (name, subject_type)
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
                                   groups.get("name3"), groups.get("name4"))
                       if g), "")
        resolved = _resolve(phrase, marshals, enemies, regions, kind)
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
    from backend.models.intel import UNKNOWN
    best = None
    for region_name in world.regions.keys():
        intel = world.get_region_intel(region_name)
        # Review round (R2-6): every tier's snapshot counts — a corps that
        # walked out of a still-PARTIAL province is "last reported" there.
        if intel.visibility == UNKNOWN:
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
        if own_soil:
            return f"{region_name} is ours, Sire."
        if _norm(holder) == _norm(region_name):
            return f"{region_name} is held by its own crown, Sire."
        return f"{region_name} is held by {holder}."
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
            # Review round (R2-11): the intelligence report prints no band at
            # LAST_KNOWN, so neither does the desk.
            band = f"{intel.strength_band}, " if vis != LAST_KNOWN else ""
            lines.append(f"Reported: {', '.join(_display(n) for n in names)} — "
                         f"{band}{when}.")
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
    from backend.models.intel import PARTIAL
    player = world.player_nation
    shown = _display(name)
    marshal = world.get_marshal(name)
    if marshal is None:
        tomb = (getattr(world, "fallen_marshals", None) or {}).get(name)
        # Review round (R2-2): a tombstone in a province never seen is not
        # ours to read out — the campaign log filters that battle too.
        if tomb and world.get_region_intel(
                tomb.get("location") or "").visibility_at_least(PARTIAL):
            return (f"{shown}'s corps no longer exists, Sire — it was destroyed at "
                    f"{tomb.get('location') or 'the field'} on turn "
                    f"{int(tomb.get('turn') or 0)}.")
        if tomb:
            return f"We have no word of {shown}'s whereabouts, Sire."
        return f"We have no record of {shown}, Sire."
    from backend.models.intel import FULL, PARTIAL
    captor = getattr(marshal, "captured_by", "")
    if captor == player:
        return f"{shown} is our prisoner at {marshal.location}, Sire — he leads no army."
    # Fog on his position, not his name: the ALLY at Franconia is answered
    # (R3-4 — `get_visible_enemies` lists enemies only), and a third court's
    # captive is reported only where the cell that holds him is in view
    # (R3-5 — no other player surface prints a far court's prisoners).
    visible = bool(world.get_region_intel(marshal.location).visibility_at_least(PARTIAL))
    if captor:
        if visible:
            return f"{shown} is a prisoner of {_court(world, captor)}, Sire — he leads no army."
        return f"We have no word of {shown}'s whereabouts, Sire."
    court = _court(world, marshal.nation)
    if visible:
        intel = world.get_region_intel(marshal.location)
        if intel.visibility == FULL:
            # Review round (R2-7): a foreign corps' works, square and rout are
            # in no player surface at FULL (the report prints strength,
            # morale, stance, ability) — the desk prints no more.
            if kind == "how_many":
                return (f"{shown} of {court} has {int(marshal.strength):,} men at "
                        f"{marshal.location} — confirmed.")
            if kind == "doing":
                stance = getattr(getattr(marshal, "stance", None), "value", None) or "neutral"
                return (f"{shown} of {court} stands at {marshal.location} in a {stance} "
                        f"stance.")
            return (f"{shown} of {court} is at {marshal.location} — "
                    f"{int(marshal.strength):,} men, confirmed.")
        # PARTIAL: the map's own rule — the live position with the MAN's
        # band, never the province's aggregate (R2-6: a 20,000 corps beside
        # Mack read "massive force").
        from backend.models.intel import get_strength_band
        band = get_strength_band(int(marshal.strength))
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
    # CX-2: this half owns FIVE kinds and no more. Without the guard a board
    # question carrying a marshal or an enemy subject — `reach`, `what_if` —
    # fell straight into `_answer_own_marshal`/`_answer_enemy`, which have no
    # arm for those kinds and answer with their generic line: measured, "can
    # Ney reach Vienna" was answered "Marshal Ney stands at Rhineland with
    # 24,000 men" and "what happens if I attack Mack" with Mack's position.
    # Both are true sentences and neither is the answer to the question.
    if kind not in {k for k, _pattern in _KINDS}:
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


# ═══════════════════════════════════════════════════════════════════════════
# CX-2 — "BERTHIER ANSWERS THE BOARD"
# ═══════════════════════════════════════════════════════════════════════════
# The desk above answers five kinds and answers them well. Measured against
# the twelve questions a player actually asks (row CX recon, 152 driven rows):
# TWO were answered and TEN were not, and eight of the ten were answered by
# nothing at all, in any phrasing. Every one of the ten returned the SAME
# 12,717-character COMMAND REFERENCE — which does not contain the words
# `status`, `where is`, `who holds` or `how many men` even ONCE, so the desk
# that could have answered them was unreachable from the only surface the game
# hands a lost player.
#
# These kinds take no roster subject, or take a NATION, which the five above
# never did — so they are matched in their own pass, AFTER `_KINDS`, and the
# older five keep precedence on every phrasing they already own.
#
# Every answer is derived from the SAME seam the mechanic itself reads — the
# build gate, the levy pricer, the muster preview, the war score, the agenda
# deck, the diplomatic state — so a quoted figure is the applied figure and
# the two cannot drift. That is the row's central finding stated as code:
# *the chips are priced and the typed verbs are blind*, and this is where the
# typed road stops being blind.
#
# Flip lever: False returns the desk to its five kinds byte-for-byte.
THE_DESK_ANSWERS_THE_BOARD = True

# AAR-18 (Score Mandate Chunk 2 reserve, Sept 26 2026): "what can I
# build" answered "nowhere" whenever no corps stood on our own soil,
# while `build market at Paris` succeeded — the executor's build gate
# (`region.can_build`) needs no corps. With no corps to point at, the
# desk now answers from that same gate: the capital first, then the
# richest province where something can be raised. False restores the
# corps-only answer.
THE_DESK_BREAKS_GROUND_WITHOUT_A_CORPS = True

# The nouns a PRICE question may name. An allowlist rather than a free
# capture, because "how much ..." otherwise swallows "how many men does Ney
# have" — which the desk above already answers better.
_PRICEABLE = {
    "battalion": "infantry", "regiment": "infantry", "infantry": "infantry",
    "foot": "infantry", "soldier": "infantry", "soldiers": "infantry",
    "men": "infantry", "troops": "infantry", "recruit": "infantry",
    "cavalry": "cavalry", "horse": "cavalry", "squadron": "cavalry",
    "artillery": "artillery", "gun": "artillery", "guns": "artillery",
    "battery": "artillery",
    "depot": "supply_depot", "supply depot": "supply_depot",
    "fort": "fortification", "fortification": "fortification",
    "training ground": "training_ground", "market": "market",
    "stables": "stables", "watchtower": "watchtower",
    "ship": "fleet", "ships": "fleet", "fleet": "fleet", "keel": "fleet",
}

_WIDE_KINDS: List[Tuple[str, "re.Pattern[str]"]] = [
    # "what's my income" / "how much gold do we have" / "how rich are we"
    ("treasury", re.compile(
        _LEAD + r"(?:what(?:" + _APOS + r"s|\s+is|\s+are)\s+(?:my|our|the)\s+"
        r"(?:income|revenue|treasury|gold|money|finances|budget|purse)"
        r"|how\s+much\s+(?:gold|money|coin)\s+(?:do|have)\s+(?:i|we)"
        r"(?:\s+(?:have|got))?"
        r"|how\s+rich\s+are\s+we"
        r"|what\s+do\s+we\s+(?:earn|make|take\s+in))" + _TAIL, re.IGNORECASE)),
    # "who is winning" / "are we winning" / "how goes the war"
    ("winning", re.compile(
        _LEAD + r"(?:who(?:" + _APOS + r"s|\s+is)\s+winning"
        r"|(?:am\s+i|are\s+we)\s+winning"
        r"|how\s+(?:is|goes|are)\s+(?:the\s+war|we\s+doing)"
        r"(?:\s+going)?)" + _TAIL, re.IGNORECASE)),
    # "am I at war with Prussia" / "are we at peace with Austria"
    ("at_war", re.compile(
        _LEAD + r"(?:am\s+i|are\s+we|is\s+france)\s+"
        r"at\s+(?:war|peace)\s+with\s+(?:the\s+)?(?P<name>.+?)" + _TAIL,
        re.IGNORECASE)),
    # "what does Austria want"
    ("wants", re.compile(
        _LEAD + r"what\s+(?:does|do)\s+(?:the\s+)?(?P<name>.+?)\s+"
        r"(?:want|seek|desire)(?:\s+from\s+(?:me|us|france))?" + _TAIL,
        re.IGNORECASE)),
    ("wants", re.compile(
        _LEAD + r"what\s+(?:is|are)\s+(?:the\s+)?(?P<name>.+?)"
        + _APOS + r"?s?\s+(?:design|designs|aim|aims|ambition|ambitions)"
        + _TAIL, re.IGNORECASE)),
    # "can Ney reach Vienna"
    ("reach", re.compile(
        _LEAD + r"(?:can|could)\s+" + _HON
        + r"(?P<name>[\w'’-]+(?:\s+[\w'’-]+)?)"
        r"\s+(?:reach|get\s+to|make\s+it\s+to)\s+(?:the\s+)?"
        r"(?P<place>.+?)" + _TAIL, re.IGNORECASE)),
    # "what happens if I attack Mack" / "what if we attack Mack" /
    # "should I attack Mack"
    ("what_if", re.compile(
        _LEAD + r"(?:what\s+(?:happens|would\s+happen)\s+if|what\s+if"
        r"|should|can|could)\s+(?:i|we|" + _HON
        + r"[\w'’-]+)\s+(?:attack|engage|assault|fight|beat)\s+"
        r"(?:the\s+)?(?P<name>.+?)" + _TAIL, re.IGNORECASE)),
    # The MUSING forms — "why not attack Mack", "what about attacking Mack",
    # "how about we attack Mack". These are the most natural thing a person
    # types at a war table, they NAME the foe, and before CX-1 every one of
    # them fought a real battle. Having stopped them, the desk should answer
    # them: the muster is exactly the reply the player was reaching for, and
    # it costs nothing.
    ("what_if", re.compile(
        _LEAD + r"(?:why\s+not|what\s+about|how\s+about|is\s+it\s+time\s+to)"
        r"(?:\s+(?:i|we|" + _HON + r"[\w'’-]+))?"
        r"\s+(?:attack|attacking|engage|engaging|assault|assaulting"
        r"|fight|fighting)\s+(?:the\s+)?(?P<name>.+?)" + _TAIL,
        re.IGNORECASE)),
    # "what can I build here" / "what can we build in Paris"
    ("can_build", re.compile(
        _LEAD + r"what\s+can\s+(?:i|we)\s+build"
        r"(?:\s+(?:here|there))?"
        r"(?:\s+(?:in|at)\s+(?:the\s+)?(?P<place>.+?))?" + _TAIL,
        re.IGNORECASE)),
    # "how much is a battalion" / "what does a depot cost"
    ("price", re.compile(
        _LEAD + r"(?:how\s+much\s+(?:is|are|does|do)|what\s+(?:does|do))\s+"
        r"(?:a|an|the)?\s*(?P<thing>[A-Za-z ]+?)(?:\s+cost)?" + _TAIL,
        re.IGNORECASE)),
    # First contact (Sept 23, 2026): the WHOLE army — "how many men do I
    # have", "how big is my army", "what forces do we have", "how many
    # marshals do I have". The fact desk's `how_many` reads a NAME and
    # "I" resolves to nobody, so the commonest question a new player
    # asks fell to the unanswered tail.
    ("own_army", re.compile(
        _LEAD + r"(?:how\s+many\s+(?:men|troops|soldiers|marshals|generals|corps"
        r"|armies|regiments)\s+(?:do|does|have|has)\s+(?:i|we)"
        r"(?:\s+(?:have|got|command|left|under\s+arms|in\s+the\s+field))?"
        r"|how\s+(?:strong|big|large|many)\s+(?:is|are)\s+(?:my|our)\s+"
        r"(?:army|armies|forces|men|troops)"
        r"|what\s+(?:is|are)\s+(?:my|our)\s+(?:army|armies|forces|strength"
        r"|order\s+of\s+battle)(?:\s+like)?"
        r"|what\s+(?:forces|troops|men|armies|marshals)\s+(?:do|have)\s+(?:i|we)"
        r"(?:\s+(?:have|got|command))?"
        r"|(?:is|are)\s+(?:my|our)\s+(?:army|forces|armies)\s+"
        r"(?:strong|weak|big|large|small|ready)"
        r"|how\s+(?:is|are)\s+(?:my|our|the)\s+(?:army|forces|armies|men|troops)"
        r"(?:\s+doing)?"
        r"|where\s+(?:is|are)\s+(?:my|our)\s+(?:army|armies|forces|men|troops"
        r"|marshals))" + _TAIL, re.IGNORECASE)),
    # "what can I do" / "what are my options" / "what now"
    ("options", re.compile(
        _LEAD + r"(?:what\s+can\s+(?:i|we)\s+do"
        r"|what\s+(?:are|were)\s+(?:my|our)\s+options"
        r"|what\s+(?:should|shall)\s+(?:i|we)\s+do"
        r"|what\s+now)" + _TAIL, re.IGNORECASE)),
]

# The kinds whose captured `name` is a COURT, resolved against the nations the
# parser already knows rather than against the marshal/region rosters.
_NATION_KINDS = frozenset({"at_war", "wants"})
# The kinds that need no subject at all.
_SUBJECTLESS_KINDS = frozenset({"treasury", "winning", "options", "own_army"})


def classify_board_question(text: str, marshals: Iterable[str] = (),
                            enemies: Iterable[str] = (),
                            regions: Iterable[str] = (),
                            nations: Iterable[str] = ()) -> Optional[Dict]:
    """The CX-2 board question in `text`, or None.

    Separate from `classify_question` so the five older kinds keep precedence
    on every phrasing they already own, and so a caller with no nation roster
    can still reach the subjectless kinds.
    """
    if not (QUESTION_DESK_ACTIVE and THE_DESK_ANSWERS_THE_BOARD) or not text:
        return None
    stripped = text.strip()
    for kind, pattern in _WIDE_KINDS:
        match = pattern.match(stripped)
        if not match:
            continue
        groups = match.groupdict()
        if kind in _SUBJECTLESS_KINDS:
            return {"kind": kind, "subject": "", "subject_type": "board"}
        if kind == "price":
            thing = _norm(groups.get("thing") or "")
            priced = _PRICEABLE.get(thing)
            if not priced:
                continue
            return {"kind": kind, "subject": priced, "subject_type": "price"}
        if kind in _NATION_KINDS:
            nation = _resolve_nation(groups.get("name") or "", nations)
            if not nation:
                continue
            return {"kind": kind, "subject": nation, "subject_type": "nation"}
        if kind == "reach":
            who = _resolve(groups.get("name") or "", marshals, (), (),
                           kind="where")
            where = _resolve(groups.get("place") or "", (), (), regions,
                             kind="who_holds")
            if not who or not where:
                continue
            return {"kind": kind, "subject": who[0], "subject_type": "marshal",
                    "place": where[0]}
        if kind == "what_if":
            foe = _resolve(groups.get("name") or "", (), enemies, (),
                           kind="where")
            if not foe:
                continue
            return {"kind": kind, "subject": foe[0], "subject_type": "enemy"}
        if kind == "can_build":
            place = groups.get("place")
            if place:
                where = _resolve(place, (), (), regions, kind="who_holds")
                if not where:
                    continue
                return {"kind": kind, "subject": where[0],
                        "subject_type": "region"}
            return {"kind": kind, "subject": "", "subject_type": "here"}
    return None


def _resolve_nation(phrase: str, nations: Iterable[str]) -> Optional[str]:
    """A court name, matched whole. Never a guess: two candidates or none
    returns None, exactly as `_resolve` does for the other rosters."""
    want = _norm(phrase)
    if not want:
        return None
    for nation in nations:
        if want in _forms(nation):
            return nation
    hits = [n for n in nations
            if any(f and re.search(r"(?:^|\s)" + re.escape(f) + r"(?:\s|$)",
                                   want) for f in _forms(n))]
    return hits[0] if len(hits) == 1 else None


# ── the executor-side half of the board desk ──────────────────────────────
# Each arm reads the seam the MECHANIC reads. Where a figure is quoted it is
# the figure that would be charged, because it comes from the same pricer;
# where a judgement is offered it is the executor's own predicate, because the
# counsel that proposes an order must never propose one the order would be
# refused on.


def _money(value) -> str:
    return f"{int(value or 0):,}"


def _answer_treasury(world, player: str) -> Optional[str]:
    from backend.game_logic.ledger import _build_economy
    economy = _build_economy(world, player) or {}
    treasury = int(economy.get("treasury") or 0)
    income = int(economy.get("income") or 0)
    net = int(economy.get("net") or 0)
    trade = int(economy.get("trade_income") or 0)
    upkeep = int(economy.get("upkeep") or 0)
    sign = "+" if net >= 0 else ""
    line = (f"The treasury holds {_money(treasury)} gold, Sire. "
            f"The provinces yield {_money(income)} and trade "
            f"{_money(trade)}; the army costs {_money(upkeep)}. "
            f"Net {sign}{_money(net)} a turn.")
    pointer = surface_pointer("economy")
    return f"{line} The full account is in {pointer}." if pointer else line


def _answer_winning(world, player: str) -> Optional[str]:
    """The war score, from `get_war_score_for` — the canonical helper every
    other consumer reads, so the desk cannot disagree with the war banner."""
    from backend.game_logic.diplomacy import get_war_score_for
    try:
        foes = sorted({m.nation for m in world.marshals.values()
                       if m.nation != player and world.is_at_war(player, m.nation)})
    except Exception:
        foes = []
    if not foes:
        return (f"We are at war with no one, Sire. "
                f"{CABINET_LINE_FOR_DESK}")
    parts = []
    for foe in foes:
        score = int(get_war_score_for(world, player, foe) or 0)
        word = ("winning" if score > 20 else
                "losing" if score < -20 else "evenly matched")
        parts.append(f"{_court(world, foe)} {score:+d} ({word})")
    pointer = surface_pointer("war")
    tail = f" The breakdown is on {pointer}." if pointer else ""
    return "War score, Sire — " + "; ".join(parts) + "." + tail


def _answer_at_war(world, player: str, nation: str) -> Optional[str]:
    from backend.display_names import STATE_DISPLAY
    state = world.get_diplomatic_state(player, nation)
    shown = STATE_DISPLAY.get(state, str(state).replace("_", " ").title())
    court = _court(world, nation)
    if state == "WAR":
        from backend.game_logic.diplomacy import get_war_score_for
        score = int(get_war_score_for(world, player, nation) or 0)
        return (f"Yes, Sire — we are at war with {court}. "
                f"The war score stands at {score:+d}.")
    return f"No, Sire. France and {court} stand at {shown}."


def _answer_wants(world, nation: str) -> Optional[str]:
    """The court's OWN active design, from the agenda deck — the same view
    the war room and the settlement scorer read (NA-1)."""
    from backend.game_logic.agendas import get_active_agenda
    court = _court(world, nation)
    view = get_active_agenda(nation, world)
    if view is None:
        return (f"{court} pursues no design we can name, Sire — she plays for "
                f"survival and advantage as they come.")
    regions = ", ".join(view.regions) if getattr(view, "regions", None) else ""
    line = f"{court} pursues {view.title}, Sire. {view.blurb}"
    if regions:
        line += f" The provinces in question: {regions}."
    pointer = surface_pointer("courts")
    return f"{line} Every court's design is listed in {pointer}." if pointer else line


def _answer_reach(world, player: str, marshal_name: str,
                  place: str) -> Optional[str]:
    """Can he get there, and how long — asked of `find_path` with the
    MOVEMENT LAW applied (`passable_for`), so the answer is the road he would
    actually be allowed to walk rather than the one the map draws."""
    marshal = world.get_marshal(marshal_name)
    if marshal is None or marshal.nation != player:
        return None
    shown = _display(marshal_name)
    if marshal.location == place:
        return f"{shown} already stands at {place}, Sire."
    lawful = world.find_path(marshal.location, place, passable_for=player)
    if lawful:
        steps = max(0, len(lawful) - 1)
        turns = "turn" if steps == 1 else "turns"
        return (f"Yes, Sire — {shown} can reach {place} from "
                f"{marshal.location} in {steps} {turns}: "
                + " -> ".join(lawful) + ".")
    any_road = world.find_path(marshal.location, place)
    if any_road:
        return (f"Not lawfully, Sire. A road exists from {marshal.location} "
                f"to {place}, but it crosses ground we may not enter. "
                f"{CABINET_LINE_FOR_DESK}")
    return (f"There is no road from {marshal.location} to {place}, Sire — "
            f"not by land.")


def _answer_what_if(world, player: str, enemy_name: str) -> Optional[str]:
    """The muster preview the ATTACK itself would print, without the attack.

    `_build_muster_preview` is the W6-4 source: who will march, who will not,
    and the odds band, fog-legal. Answering the question with the same object
    the order uses is the whole point — the player is told exactly what he
    would be told a moment later, and nothing is spent to learn it.
    """
    enemy = world.get_marshal(enemy_name)
    if enemy is None or enemy.nation == player:
        return None
    candidates = []
    for marshal in world.get_player_marshals():
        if int(getattr(marshal, "strength", 0) or 0) <= 0:
            continue
        if marshal.location == enemy.location:
            candidates.insert(0, marshal)
            continue
        region = world.get_region(marshal.location)
        if region is not None and enemy.location in (
                getattr(region, "adjacent_regions", None) or []):
            candidates.append(marshal)
    shown = _display(enemy_name)
    if not candidates:
        return (f"No corps of ours stands within reach of {shown} at "
                f"{enemy.location}, Sire — there is no battle to weigh.")
    from backend.commands.executor import CommandExecutor
    combat = CommandExecutor()._combat
    preview = combat._build_muster_preview(
        candidates[0], enemy, world, {"world": world})
    if not preview:
        return None
    # The SAME renderer the attack itself prints (`_format_muster_lines`), so
    # what the QUESTION shows and what the ORDER shows are one string and can
    # never drift into two accounts of the same field.
    text = combat._format_muster_lines(preview)
    if not text:
        return None
    return ("Were you to give the order, Sire:\n" + str(text).strip()
            + "\n\nNothing has been ordered, and nothing spent.")


def _answer_can_build(world, player: str, region_name: str) -> Optional[str]:
    """Read through `region.can_build`, THE single build gate — so the desk
    and the executor cannot disagree about what is legal, and every price is
    the price that would be charged."""
    from backend.models.region import BUILDING_TYPES, can_build
    region = world.get_region(region_name)
    if region is None:
        return None
    if getattr(region, "controller", None) != player:
        return (f"{region_name} is not ours to build in, Sire — it answers to "
                f"{_court(world, getattr(region, 'controller', '') or '')}.")
    allowed, refused = [], []
    for key, spec in BUILDING_TYPES.items():
        verdict = can_build(world, region, key, player)
        ok = verdict[0] if isinstance(verdict, (tuple, list)) else bool(verdict)
        reason = (verdict[1] if isinstance(verdict, (tuple, list))
                  and len(verdict) > 1 else "")
        word = key.replace("_", " ")
        cost = _money(spec.get("gold_cost"))
        if ok:
            allowed.append(f"{word} ({cost}g)")
        elif reason:
            refused.append(f"{word} — {reason}")
    if not allowed:
        head = f"Nothing can be built at {region_name} today, Sire."
        return head + (" " + refused[0] + "." if refused else "")
    head = (f"At {region_name} we may build: " + ", ".join(allowed) + ".")
    if refused:
        head += f" Not {refused[0]}."
    return head


def _answer_price(world, player: str, what: str) -> Optional[str]:
    """The live price, from the pricer that would charge it."""
    if what in ("infantry", "cavalry", "artillery"):
        from backend.game_logic.ledger import _build_economy
        levy = (_build_economy(world, player) or {}).get("levy") or {}
        price = int(levy.get(f"{what}_price") or levy.get("infantry_price") or 0)
        amount = int(levy.get(f"{what}_amount") or levy.get("infantry_amount") or 0)
        where = _first_own_region_with_a_corps(world, player)
        if not price:
            return (f"No corps of ours stands where the levy could reach it, "
                    f"Sire — the price is not quoted until one does.")
        line = (f"{_money(price)} gold for {_money(amount)} "
                f"{what}, Sire")
        if where:
            line += f", at {where}"
        line += ". The price rises at war and above the force limit."
        return line
    if what == "fleet":
        from backend.game_logic import naval
        cost = int(getattr(naval, "SHIP_COST", 400) or 400)
        return (f"{_money(cost)} gold a keel, Sire, and one action of the "
                f"administration. New crews come aboard green.")
    from backend.models.region import BUILDING_TYPES
    spec = BUILDING_TYPES.get(what)
    if spec:
        word = what.replace("_", " ")
        return (f"A {word} costs {_money(spec.get('gold_cost'))} gold and "
                f"{int(spec.get('build_time') or 0)} turns, Sire.")
    if what == "watchtower":
        return "A watchtower costs 150 gold, Sire."
    return None


def _first_own_region_that_can_build(world, player: str) -> Optional[str]:
    """AAR-18: the first of our provinces where the executor's own gate
    (`region.can_build`) allows SOMETHING — the capital first, then by
    income. None when nothing can be built anywhere we hold."""
    from backend.models.region import BUILDING_TYPES, can_build
    getter = getattr(world, "get_nation_capital", None)
    capital = getter(player) if callable(getter) else None

    def _rank(name):
        region = world.get_region(name)
        income = int(getattr(region, "income_value", 0) or 0) if region else 0
        return (0 if name == capital else 1, -income, name)

    for name in sorted(world.get_nation_regions(player), key=_rank):
        region = world.get_region(name)
        if region is None:
            continue
        for key in BUILDING_TYPES:
            verdict = can_build(world, region, key, player)
            ok = verdict[0] if isinstance(verdict, (tuple, list)) else bool(verdict)
            if ok:
                return name
    return None


def _first_own_region_with_a_corps(world, player: str) -> Optional[str]:
    for marshal in world.get_player_marshals():
        if int(getattr(marshal, "strength", 0) or 0) <= 0:
            continue
        region = world.get_region(marshal.location)
        if region is not None and getattr(region, "controller", None) == player:
            return marshal.location
    return None


def _answer_own_army(world, player: str) -> str:
    """First contact: the whole army in one return — every corps of ours
    that stands in the field, strongest first, and where the full return
    lives. Captives and empty commands are left off (the Generals screen
    shows them); the total is the fielded total."""
    marshals = []
    for marshal in world.get_player_marshals():
        if getattr(marshal, "captured_by", ""):
            continue
        if int(getattr(marshal, "strength", 0) or 0) <= 0:
            continue
        marshals.append(marshal)
    if not marshals:
        return ("No corps of ours stands in the field, Sire. The Generals "
                "screen (press G) shows the roster.")
    marshals.sort(key=lambda m: -int(m.strength))
    total = sum(int(m.strength) for m in marshals)
    plural = "s" if len(marshals) != 1 else ""
    head = (f"Our army stands at {total:,} men under {len(marshals)} "
            f"marshal{plural}, Sire:")
    rows = [f"  {_display(m.name)} — {int(m.strength):,} at {m.location}"
            f" (morale {int(getattr(m, 'morale', 0) or 0)})"
            for m in marshals[:8]]
    if len(marshals) > 8:
        rows.append(f"  … and {len(marshals) - 8} more")
    tail = ("The Strategic Ledger's Forces tab (press T) has the full return; "
            "the Generals screen (press G) has each man's card.")
    return "\n".join([head, *rows, tail])


def _answer_options(world, player: str) -> Optional[str]:
    """What can be ordered, right now, that would not be refused.

    ONE source with Berthier's shrug and the counsel line (`ai/counsel.py`),
    so the game can never propose an order on one surface that it refuses on
    another — which is exactly how the shrug came to print `declare war on
    Prussia` at a France that was at peace with Prussia.
    """
    from backend.ai.counsel import what_can_i_do
    lines = what_can_i_do(world, player, limit=6)
    if not lines:
        return (f"Nothing can be ordered this turn, Sire. {CABINET_LINE_FOR_DESK}")
    body = "\n".join(f"  {line}" for line in lines)
    return ("These orders would be carried out today, Sire:\n" + body
            + f"\n{CABINET_LINE_FOR_DESK}")


CABINET_LINE_FOR_DESK = "For any matter of state, press F1 for the Cabinet."


def surface_pointer(kind: str) -> Optional[str]:
    """Delegates to the ONE pointer table (`ai/counsel.py`), so the desk and
    the shrug name a screen the same way."""
    from backend.ai.counsel import surface_pointer as _pointer
    return _pointer(kind)


def answer_board_question(world, question: Optional[Dict]) -> Optional[str]:
    """Berthier's answer to a CX-2 board question, or None."""
    if not question or world is None:
        return None
    if not (QUESTION_DESK_ACTIVE and THE_DESK_ANSWERS_THE_BOARD):
        return None
    kind = str(question.get("kind") or "")
    subject = str(question.get("subject") or "")
    player = world.player_nation
    try:
        if kind == "treasury":
            return _answer_treasury(world, player)
        if kind == "winning":
            return _answer_winning(world, player)
        if kind == "at_war":
            return _answer_at_war(world, player, subject)
        if kind == "wants":
            return _answer_wants(world, subject)
        if kind == "reach":
            return _answer_reach(world, player, subject,
                                 str(question.get("place") or ""))
        if kind == "what_if":
            return _answer_what_if(world, player, subject)
        if kind == "can_build":
            where = subject or _first_own_region_with_a_corps(world, player)
            if not where and THE_DESK_BREAKS_GROUND_WITHOUT_A_CORPS:
                # AAR-18: the executor's gate needs no corps.
                where = _first_own_region_that_can_build(world, player)
                if where:
                    return ("No corps of ours stands on our own soil, "
                            "Sire, but ground is broken without one. "
                            + _answer_can_build(world, player, where))
                if world.get_nation_regions(player):
                    return "Nothing can be built on our soil today, Sire."
            if not where:
                return ("No corps of ours stands on our own soil, Sire — "
                        "there is nowhere to break ground.")
            return _answer_can_build(world, player, where)
        if kind == "price":
            return _answer_price(world, player, subject)
        if kind == "options":
            return _answer_options(world, player)
        if kind == "own_army":
            return _answer_own_army(world, player)
    except Exception as exc:  # the desk must never break the status verb
        print(f"[QUESTION DESK] could not answer {question!r}: {exc}")
        return None
    return None
