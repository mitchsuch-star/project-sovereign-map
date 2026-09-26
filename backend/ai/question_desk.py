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

# ═══════════════════════════════════════════════════════════════════════════
# CRT-7 — "THE DESK ANSWERS WHAT THE ORDER WOULD DO" (Score Mandate Chunk 3,
# SR-3a part (ii), September 26, 2026). The through-line the CR-6 triage
# named: every desk answer asks the SEAM that would refuse or charge the
# order. Each rule below sits behind its own lever whose down arm reproduces
# the row it closes, measured at the real `POST /command` on the shipped
# 1805 boot before a line was written.
# ═══════════════════════════════════════════════════════════════════════════
# AAR-17: the first questions a player asks — "who am I fighting and why",
# "is Vienna safe?", "what does Kutuzov have with him?", "how long until the
# armistice with Austria expires?", "who are my allies", "how is the war
# effort", "what happened last turn" — every one of them drew "I cannot
# answer that from the dispatches" while the dispatch beside it listed three
# wars. Seven kinds: `wars`, `allies`, `safe`, `truce_clock`, `war_effort`,
# `news`, and the fact desk's `how_many` learning "what does X have".
THE_DESK_ANSWERS_THE_WAR_QUESTION = True
# DESK-1 (a FOG LEAK, P2): `why not attack Kutuzov` answered "No corps of
# ours stands within reach of Kutuzov at Podolia" while `where is Kutuzov`
# answered "no word of Kutuzov's whereabouts" — the what-if named the cell
# of a corps the player had never seen, and tracked it live.
THE_WHAT_IF_IS_FOG_HONEST = True
# DESK-4: the what-if mustered against Deroy (Bavaria, our ALLY) and against
# Mack under a TRUCE, where the order itself is refused — it asks the order's
# own refusals first (`friendly_fire_refusal`, the executor's armistice
# block) and says when the order would first put a declaration to the player.
THE_WHAT_IF_REFUSES_LIKE_THE_ORDER = True
# DESK-2 (P2): `how much is a battalion` quoted "654 gold for 10,000 infantry
# at Rhineland" while the order raises 3,000 for 647 under Davout, and `how
# much is a gun` quoted 654 where the order refuses (no commander of guns).
# The price is `economy_executor.recruit_quote`, CN-1's single source — the
# bare order's ground (the capital) first, then the cheapest levy a standing
# corps can raise, as the order that raises it.
THE_PRICE_IS_THE_QUOTE = True
# DESK-5: "the provinces yield 3,400 and trade 350; the army costs 2,630.
# Net +1,842" — the named figures summed to 1,120. The sentence is built
# from `ledger.NET_GOLD_COMPONENTS` with their signs, so it sums by
# construction.
THE_INCOME_SENTENCE_SUMS = True
# DESK-7 (P2): `who is winning` built its list from the courts with MARSHALS
# on the board, so a war with a court whose army was elsewhere was missing,
# and a coalition read as three even scores instead of the ONE war-level
# score the banner shows. It reads the war banner's own rows now
# (`war_status.build_active_wars`), coalition collapsed as the banner does.
WHO_IS_WINNING_READS_THE_BANNER = True
# DESK-15: our own FALLEN marshal could not be asked about — `where is Ney`
# after his corps was destroyed drew the shrug, because the parser's roster
# holds only marshals with strength > 0. The player's own tombstones join the
# desk's roster (no fog on our own dead) and are answered in the first person.
OUR_OWN_FALLEN_ARE_ANSWERED = True

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
        # CRT-7 / AAR-17: "what does Kutuzov have with him?" — the strength
        # answer, asked the way the AAR asked it. `have/command/lead/bring/
        # field/muster` keep it off the board desk's `wants` kind ("what
        # does Austria want"), which is matched AFTER this table.
        + r"|what\s+(?:does|do)\s+" + _HON + r"(?P<name5>.+?)\s+"
        r"(?:have|command|lead|bring|field|muster)"
        r"(?:\s+(?:with|under)\s+(?:him|her|them|his\s+command|their\s+command))?"
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
                                   groups.get("name3"), groups.get("name4"),
                                   groups.get("name5"))
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
            if marshal is None and OUR_OWN_FALLEN_ARE_ANSWERED:
                # DESK-15: our own fallen, in the first person.
                tomb = (getattr(world, "fallen_marshals", None) or {}).get(subject)
                if tomb and (tomb or {}).get("nation") == world.player_nation:
                    return _answer_own_fallen(world, subject, tomb)
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
    # "am I at war with Prussia". DESK-12 (CRT-7): the pattern once read
    # `at (?:war|peace) with` — the "peace" half was UNREACHABLE, because the
    # peace-intent route (`llm_client._is_peace_intent`) claims "are we at
    # peace with Austria" before the desk sees it. The dead half is deleted
    # rather than kept as a promise the code cannot honour; the answer arm
    # still says "No, Sire … stand at Peace" for a court we are not fighting.
    ("at_war", re.compile(
        _LEAD + r"(?:am\s+i|are\s+we|is\s+france)\s+"
        r"at\s+war\s+with\s+(?:the\s+)?(?P<name>.+?)" + _TAIL,
        re.IGNORECASE)),
    # ── CRT-7 / AAR-17: the first questions a player asks ─────────────────
    # "who am I fighting and why" / "who are we at war with" / "who is at war
    # with us" / "who are our enemies" / "why are we at war" / "what wars are
    # we in" / "am I at war" (no court named — the court-named form is
    # `at_war`, matched above).
    ("wars", re.compile(
        _LEAD + r"(?:who\s+(?:am\s+i|are\s+we)\s+(?:fighting|at\s+war\s+with|up\s+against)"
        r"(?:\s+and\s+why)?"
        r"|who\s+(?:is|are)\s+(?:at\s+war\s+with\s+(?:us|me|france)"
        r"|(?:our|my|the)\s+enem(?:y|ies)|against\s+(?:us|me))"
        r"|who\s+(?:are|is)\s+(?:we|i)\s+at\s+war\s+with"
        r"|who\s+(?:has|have)\s+declared\s+war\s+on\s+(?:us|me|france)"
        r"|(?:what|which)\s+(?:wars?|courts?|nations?|powers?)\s+"
        r"(?:am\s+i|are\s+we)\s+(?:in|fighting|at\s+war\s+with)"
        r"|why\s+(?:am\s+i|are\s+we)\s+(?:at\s+war|fighting)(?:\s+(?:at\s+all|them))?"
        r"|(?:am\s+i|are\s+we)\s+at\s+war(?:\s+with\s+any(?:one|body))?"
        r"|what\s+(?:is|are)\s+(?:the|our|my)\s+wars?(?:\s+about)?)" + _TAIL,
        re.IGNORECASE)),
    # "who are my allies" / "do we have any allies" / "who stands with us"
    ("allies", re.compile(
        _LEAD + r"(?:who\s+(?:are|is)\s+(?:my|our|france" + _APOS + r"s)\s+"
        r"(?:allies|ally|friends|friend)"
        r"|(?:do|does)\s+(?:i|we|france)\s+have\s+(?:any\s+)?(?:allies|friends)"
        r"|who\s+(?:is|are)\s+(?:allied|friendly)\s+(?:with|to)\s+(?:us|me|france)"
        r"|who\s+(?:stands|is|fights)\s+with\s+(?:us|me)"
        r"|(?:what|which)\s+(?:courts?|nations?|powers?)\s+(?:are|is)\s+"
        r"(?:on\s+our\s+side|with\s+us|our\s+allies))" + _TAIL, re.IGNORECASE)),
    # "is Vienna safe?" / "is Rhineland in danger" / "is Paris threatened"
    ("safe", re.compile(
        _LEAD + r"(?:is|are)\s+(?:the\s+)?(?P<name>.+?)\s+"
        r"(?:safe|secure|in\s+danger|threatened|under\s+threat|at\s+risk"
        r"|exposed|in\s+peril|defended|well\s+defended|covered)" + _TAIL,
        re.IGNORECASE)),
    # "how long until the armistice with Russia expires?" / "when does the
    # truce end" / "how many turns are left on the armistice"
    ("truce_clock", re.compile(
        _LEAD + r"(?:how\s+(?:long|many\s+turns)\s+"
        r"(?:until|till|before|(?:is|are)\s+left\s+(?:on|in|of)"
        r"|remains?\s+(?:on|in|of)|(?:does|will)\s+.*?\s+last)\s*"
        r"(?:the\s+)?(?:armistice|truce|cease-?fire)"
        r"(?:\s+with\s+(?:the\s+)?(?P<name>[A-Za-z][\w' -]*?))?"
        r"(?:\s+(?:expires?|ends?|lapses?|runs?\s+out|holds?|lasts?))?"
        r"|when\s+(?:does|will|is)\s+(?:the\s+)?(?:armistice|truce|cease-?fire)"
        r"(?:\s+with\s+(?:the\s+)?(?P<name2>[A-Za-z][\w' -]*?))?\s+"
        r"(?:expire|end|lapse|run\s+out|over|up)"
        r"|(?:is|are)\s+(?:we|i)\s+(?:in|under)\s+(?:an?\s+)?"
        r"(?:armistice|truce|cease-?fire)(?:\s+with\s+(?:the\s+)?(?P<name3>.+?))?)"
        + _TAIL, re.IGNORECASE)),
    # "how is the war effort" / "how weary are we" / "what is our war
    # exhaustion" — the NATIONAL exhaustion, ours and every court's at war
    ("war_effort", re.compile(
        _LEAD + r"(?:how\s+(?:is|goes|stands|fares)\s+(?:the|our|my)\s+war\s+effort"
        r"|what(?:" + _APOS + r"s|\s+is)\s+(?:the|our|my)\s+"
        r"(?:war\s+)?(?:effort|weariness|exhaustion)(?:\s+(?:at|like))?"
        r"|how\s+(?:weary|exhausted|tired|war-weary)\s+"
        r"(?:are\s+we|is\s+france|is\s+the\s+(?:nation|army|country))"
        r"|how\s+(?:is|are)\s+(?:the\s+)?(?:nation|country|people)\s+"
        r"(?:bearing|taking|holding)\s+(?:up\s+under\s+)?the\s+war)" + _TAIL,
        re.IGNORECASE)),
    # "what happened last turn" / "what did I miss" / "anything new"
    ("news", re.compile(
        _LEAD + r"(?:what\s+happened(?:\s+(?:last\s+turn|yesterday|overnight"
        r"|this\s+morning|recently|while\s+i\s+was\s+(?:away|gone)|since))?"
        r"|what\s+did\s+(?:i|we)\s+miss"
        r"|(?:is\s+there\s+)?any(?:thing)?\s+(?:new|news)"
        r"|what(?:" + _APOS + r"s|\s+is)\s+(?:new|the\s+news|the\s+latest|the\s+word)"
        r"|what\s+(?:has\s+)?changed(?:\s+(?:since\s+)?(?:last\s+turn|overnight))?"
        r"|(?:bring\s+me\s+up\s+to\s+date|catch\s+me\s+up|brief\s+me))" + _TAIL,
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
_SUBJECTLESS_KINDS = frozenset({"treasury", "winning", "options", "own_army",
                                "wars", "allies", "war_effort", "news"})
# CRT-7 / AAR-17: the kinds the war-question lever owns, so the lever down
# returns every one of them to the shrug byte-for-byte.
_WAR_QUESTION_KINDS = frozenset({"wars", "allies", "safe", "truce_clock",
                                 "war_effort", "news"})


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
        if kind in _WAR_QUESTION_KINDS and not THE_DESK_ANSWERS_THE_WAR_QUESTION:
            continue
        match = pattern.match(stripped)
        if not match:
            continue
        groups = match.groupdict()
        if kind in _SUBJECTLESS_KINDS:
            return {"kind": kind, "subject": "", "subject_type": "board"}
        if kind == "safe":
            where = _resolve(groups.get("name") or "", (), (), regions,
                             kind="who_holds")
            if not where:
                continue
            return {"kind": kind, "subject": where[0], "subject_type": "region"}
        if kind == "truce_clock":
            phrase = next((groups.get(k) for k in ("name", "name2", "name3")
                           if groups.get(k)), "")
            nation = _resolve_nation(phrase, nations) if phrase else None
            if phrase and not nation:
                continue
            return {"kind": kind, "subject": nation or "",
                    "subject_type": "nation" if nation else "board"}
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


# DESK-5: how each signed Net component reads in a sentence. Keyed on
# `ledger.NET_GOLD_COMPONENTS`, so a component added to the ledger without a
# label here still prints (as its key), and the sum still holds.
_NET_LABELS = {
    "income": "the provinces", "trade_income": "trade",
    "admin_bonus": "the administration", "treaty_gold": "treaty gold",
    "vassal_tribute": "vassal tribute", "settlement_gold": "settlement gold",
    "requisitions": "requisitions", "overseas": "overseas trade",
    "occupation": "occupation", "contributions": "contributions of war",
    "state_charges": "the Charges of Empire", "dotation_skim": "the dotations",
    "rente_cost": "the rentes", "infrastructure": "infrastructure",
    "blockade": "the blockade", "admiralty": "the Admiralty",
    "upkeep_base": "the army",
    "upkeep_surcharge": "the surcharge above the force limit",
}


def _answer_treasury(world, player: str) -> Optional[str]:
    from backend.game_logic.ledger import _build_economy
    economy = _build_economy(world, player) or {}
    treasury = int(economy.get("treasury") or 0)
    income = int(economy.get("income") or 0)
    net = int(economy.get("net") or 0)
    trade = int(economy.get("trade_income") or 0)
    upkeep = int(economy.get("upkeep") or 0)
    sign = "+" if net >= 0 else ""
    pointer = surface_pointer("economy")
    if not THE_INCOME_SENTENCE_SUMS:
        line = (f"The treasury holds {_money(treasury)} gold, Sire. "
                f"The provinces yield {_money(income)} and trade "
                f"{_money(trade)}; the army costs {_money(upkeep)}. "
                f"Net {sign}{_money(net)} a turn.")
        return f"{line} The full account is in {pointer}." if pointer else line
    # DESK-5: the sentence is the ledger's own identity — every non-zero
    # signed component, in and out, so the figures named SUM to the Net
    # stated (measured before: 3,400 + 350 − 2,630 = 1,120 against a printed
    # Net of +1,842; the administration, the tribute, the blockade and the
    # Admiralty had been left out of the sentence and in the sum).
    from backend.game_logic.ledger import NET_GOLD_COMPONENTS
    credits, debits = [], []
    for key, direction in NET_GOLD_COMPONENTS.items():
        signed = int(direction) * int(economy.get(key) or 0)
        if signed == 0:
            continue
        label = _NET_LABELS.get(key, key.replace("_", " "))
        (credits if signed > 0 else debits).append((abs(signed), label))
    credits.sort(key=lambda pair: -pair[0])
    debits.sort(key=lambda pair: -pair[0])
    parts = [f"The treasury holds {_money(treasury)} gold, Sire."]
    if credits:
        parts.append("In: " + ", ".join(f"{label} {_money(v)}" for v, label in credits) + ".")
    if debits:
        parts.append("Out: " + ", ".join(f"{label} {_money(v)}" for v, label in debits) + ".")
    parts.append(f"Net {sign}{_money(net)} a turn.")
    line = " ".join(parts)
    return f"{line} The full account is in {pointer}." if pointer else line


def _join(names: List[str]) -> str:
    names = [n for n in names if n]
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + " and " + names[-1]


def _banner_rows(world):
    """The war banner's own rows (`war_status.build_active_wars`) — the ONE
    source the HUD reads, so the desk cannot disagree with it. `(rows,
    coalition)`; empty on any failure (the desk must never break)."""
    try:
        from backend.game_logic.war_status import build_active_wars
        data = build_active_wars(world) or {}
    except Exception:
        return [], None
    return list(data.get("wars") or []), data.get("coalition")


def _row_courts(world, row) -> List[str]:
    opponents = [str(o) for o in (row.get("opponents") or []) if o]
    if not opponents and row.get("opponent"):
        opponents = [str(row.get("opponent"))]
    return [_court(world, o) for o in opponents]


def _row_name(world, row, coalition) -> str:
    """How the banner names a war: the coalition, with its members, where the
    row is the leader's collapsed coalition row; the court otherwise."""
    courts = _row_courts(world, row)
    if row.get("in_coalition") and row.get("is_coalition_leader") and len(courts) > 1:
        name = str((coalition or {}).get("name") or "the coalition")
        if not name.lower().startswith("the "):
            name = f"the {name}"
        return f"{name} ({_join(courts)})"
    return _join(courts) or _court(world, str(row.get("opponent") or ""))


def _score_word(score: int) -> str:
    return ("winning" if score > 20 else
            "losing" if score < -20 else "evenly matched")


def _answer_winning(world, player: str) -> Optional[str]:
    """The war score, from the war banner's own rows (DESK-7) — the same
    `build_active_wars` the HUD renders, coalition collapsed to ONE war-level
    score exactly as the banner shows it, and a court with no marshal on the
    board still named. Lever down: the pre-CRT-7 list, built from the courts
    with marshals on the board through `get_war_score_for`."""
    from backend.game_logic.diplomacy import get_war_score_for
    pointer = surface_pointer("war")
    tail = f" The breakdown is on {pointer}." if pointer else ""
    if WHO_IS_WINNING_READS_THE_BANNER:
        rows, coalition = _banner_rows(world)
        wars = [r for r in rows if str(r.get("status") or "war") == "war"]
        truces = [r for r in rows if str(r.get("status") or "") == "armistice"]
        if not wars and not truces:
            return (f"We are at war with no one, Sire. "
                    f"{CABINET_LINE_FOR_DESK}")
        parts = []
        for row in wars:
            score = int(row.get("war_score") or 0)
            parts.append(f"{_row_name(world, row, coalition)} {score:+d} "
                         f"({_score_word(score)})")
        text = ("War score, Sire — " + "; ".join(parts) + "." if parts
                else "No war is being fought today, Sire.")
        if truces:
            text += (" Under truce: "
                     + _join([_row_name(world, r, coalition) for r in truces]) + ".")
        return text + tail
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
        parts.append(f"{_court(world, foe)} {score:+d} ({_score_word(score)})")
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
    shown = _display(enemy_name)
    court = _court(world, enemy.nation)
    # DESK-1 (CRT-7): fog FIRST. The answer names a cell only where the
    # player has intelligence on it — the same rule `_answer_enemy` keeps
    # for "where is Kutuzov". A prisoner is answered by the prisoners'
    # module, which names the cell only where it is in view.
    if THE_WHAT_IF_IS_FOG_HONEST:
        from backend.models.intel import PARTIAL
        if getattr(enemy, "captured_by", ""):
            from backend.commands.prisoners import prisoner_refusal
            refusal = prisoner_refusal(world, enemy, player) or {}
            return (str(refusal.get("message") or
                        f"{shown} leads no army, Sire.")
                    + " There is no battle to weigh.")
        if not world.get_region_intel(enemy.location).visibility_at_least(PARTIAL):
            return (f"We have no word of {shown}'s whereabouts, Sire — there "
                    f"is no battle to weigh. Scout for him before naming him.")
    candidates = []
    for marshal in world.get_player_marshals():
        if int(getattr(marshal, "strength", 0) or 0) <= 0:
            continue
        if getattr(marshal, "captured_by", "") or getattr(marshal, "administrative", False):
            continue
        if marshal.location == enemy.location:
            candidates.insert(0, marshal)
            continue
        region = world.get_region(marshal.location)
        if region is not None and enemy.location in (
                getattr(region, "adjacent_regions", None) or []):
            candidates.append(marshal)
    # DESK-4 (CRT-7): the ORDER's own refusals, asked of the seams the order
    # asks — `friendly_fire_refusal` (an ally, a vassal, our own), the
    # executor's armistice block — before any muster is drawn. A court at
    # PEACE is not a refusal: the order would first put the declaration to
    # the player, and the answer says so before the muster.
    preface = ""
    if THE_WHAT_IF_REFUSES_LIKE_THE_ORDER:
        from backend.commands.combat_executor import friendly_fire_refusal
        probe = candidates[0] if candidates else next(
            (m for m in world.get_player_marshals()
             if int(getattr(m, "strength", 0) or 0) > 0
             and not getattr(m, "captured_by", "")), None)
        if probe is not None and friendly_fire_refusal(world, probe, enemy.nation):
            state = world.get_diplomatic_state(player, enemy.nation)
            bond = ("our vassal" if state == "VASSAL" else "our ally")
            return (f"{shown} is {court}'s, and {court} is {bond}, Sire — "
                    f"the order would be refused, and nothing spent. "
                    f"{CABINET_LINE_FOR_DESK}")
        state = world.get_diplomatic_state(player, enemy.nation)
        if state == "ARMISTICE":
            from backend.commands.executor import CommandExecutor
            block = CommandExecutor()._make_diplomatic_error(world, player, enemy)
            if block:
                return (f"{block.get('message')} The order would be refused, "
                        f"and nothing spent.")
        elif not world.is_at_war(player, enemy.nation):
            preface = (f"France is at peace with {court}, Sire — the order "
                       f"would first put a declaration of war to you.\n")
    if not candidates:
        return (f"{preface}No corps of ours stands within reach of {shown} at "
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
    return (preface + "Were you to give the order, Sire:\n" + str(text).strip()
            + "\n\nNothing has been ordered, and nothing spent.")


def _answer_levy_price(world, player: str, arm: str) -> Optional[str]:
    """DESK-2 (CRT-7): the price is `economy_executor.recruit_quote`, CN-1's
    single source — the recipient, the men who arrive after the field cap
    and the gold the executor would charge. The bare order (`recruit <arm>`)
    is raised at the CAPITAL, so that ground is quoted first; where it
    refuses for want of a receiver, the cheapest levy a standing corps of
    ours can raise is quoted AS the order that raises it; where nothing
    raises, the executor's own refusal — the gun remedy, the empty chest —
    is the answer. Measured before: 654 gold for 10,000 of an arm nobody
    commanded."""
    from backend.commands.economy_executor import recruit_quote
    capital = None
    getter = getattr(world, "get_nation_capital", None)
    if callable(getter):
        capital = getter(player)
    home = recruit_quote(world, capital, arm, player) if capital else {}
    tail = " The price rises at war and above the force limit."

    def _field(q):
        return " — a field levy, capped by what the province feeds" if q.get("field_capped") else ""

    if home.get("ok"):
        return (f"{_money(home['price'])} gold for {_money(home['amount'])} "
                f"{arm}, Sire — 'recruit {arm}' raises them at {capital} under "
                f"{_display(str(home['recipient']))}{_field(home)}.{tail}")
    best = None
    priced = None
    seen = set()
    for marshal in world.get_player_marshals():
        if int(getattr(marshal, "strength", 0) or 0) <= 0:
            continue
        if getattr(marshal, "captured_by", ""):
            continue
        where = marshal.location
        if where in seen or where == capital or where not in world.regions:
            continue
        seen.add(where)
        quote = recruit_quote(world, where, arm, player)
        if quote.get("ok"):
            if best is None or int(quote["price"]) < int(best[1]["price"]):
                best = (where, quote)
        elif quote.get("kind") == "treasury":
            if priced is None or int(quote.get("price") or 0) < int(priced[1].get("price") or 0):
                priced = (where, quote)
    if best is not None:
        where, quote = best
        why_not_home = str(home.get("short") or home.get("reason")
                           or "no receiver stands within reach").strip().rstrip(".")
        return (f"{_money(quote['price'])} gold for {_money(quote['amount'])} "
                f"{arm}, Sire — 'recruit {arm} in {where}' raises them under "
                f"{_display(str(quote['recipient']))}{_field(quote)}. At "
                f"{capital} the bare order is refused: {why_not_home}."
                f"{tail}")
    if priced is not None:
        where, quote = priced
        return (f"{_money(quote.get('price'))} gold for {_money(quote.get('amount'))} "
                f"{arm}, Sire — 'recruit {arm} in {where}' under "
                f"{_display(str(quote.get('recipient')))} — but the treasury "
                f"holds {_money(quote.get('have'))}; the order is refused until "
                f"it can pay.{tail}")
    reason = (home.get("short") or home.get("reason")
              or "no corps of ours stands where the levy could reach it")
    return (f"No {arm} can be raised today, Sire. {str(reason).rstrip('.')}."
            f"{tail}")


def _answer_wars(world, player: str) -> Optional[str]:
    """AAR-17: who we are fighting, and why — the war banner's own rows
    (`build_active_wars`), each with its war-level score, its age, OUR stated
    purpose (LV-8's one sentence) and every opposing court's design (the
    agenda deck, NA-1's view). Diplomacy has no fog."""
    rows, coalition = _banner_rows(world)
    wars = [r for r in rows if str(r.get("status") or "war") == "war"]
    truces = [r for r in rows if str(r.get("status") or "") == "armistice"]
    if not wars and not truces:
        return f"We are at war with no one, Sire. {CABINET_LINE_FOR_DESK}"
    from backend.game_logic.agendas import get_active_agenda
    lines = []
    for row in wars:
        score = int(row.get("war_score") or 0)
        age = int(row.get("duration") or 0)
        age_words = ("declared this turn" if age <= 0 else
                     f"in its {age + 1}{_ordinal_suffix(age + 1)} turn")
        head = (f"We are at war with {_row_name(world, row, coalition)}, Sire — "
                f"war score {score:+d} ({_score_word(score)}), {age_words}.")
        purpose = row.get("objective") or {}
        why = ""
        if purpose:
            kind = str(purpose.get("type_display") or purpose.get("type") or "").lower()
            summary = str(purpose.get("target_summary") or "")
            if kind and summary:
                why = f" Our purpose: the {kind} of {summary}."
            elif kind:
                why = f" Our purpose: {kind}."
        reason = str(row.get("stated_reason") or "").strip()
        if reason:
            why += f" Their cause: {reason.rstrip('.')}."
        designs = []
        for opponent in (row.get("opponents") or [row.get("opponent")]):
            if not opponent:
                continue
            try:
                view = get_active_agenda(str(opponent), world)
            except Exception:
                view = None
            if view is not None and getattr(view, "title", None):
                designs.append(f"{_court(world, str(opponent))} pursues {view.title}")
        if designs:
            why += " Their designs: " + "; ".join(designs) + "."
        lines.append(head + why)
    if truces:
        lines.append("Under truce: "
                     + _join([_row_name(world, r, coalition) for r in truces]) + ".")
    pointer = surface_pointer("war")
    courts = surface_pointer("courts")
    tail = ""
    if pointer:
        tail += f" Each war is on {pointer}"
        tail += f"; every court's design in {courts}." if courts else "."
    return " ".join(lines) + tail


def _ordinal_suffix(n: int) -> str:
    if 10 <= n % 100 <= 20:
        return "th"
    return {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")


def _answer_allies(world, player: str) -> Optional[str]:
    """AAR-17: our allies — every court in ALLIANCE or DEFENSIVE ALLIANCE
    with us (`are_allies`, the engine's own predicate) and every client that
    owes us fealty (`world.vassals`, lord == us). Diplomacy has no fog."""
    from backend.display_names import STATE_DISPLAY
    allies = []
    try:
        for nation in world.get_active_nations():
            if nation == player:
                continue
            if world.are_allies(player, nation):
                state = world.get_diplomatic_state(player, nation)
                shown = STATE_DISPLAY.get(state, str(state).replace("_", " ").title())
                allies.append(f"{_court(world, nation)} ({str(shown).lower()})")
    except Exception:
        allies = []
    clients = []
    for tag, row in (getattr(world, "vassals", None) or {}).items():
        if str((row or {}).get("lord") or "") == player:
            clients.append(_court(world, str(tag)))
    pointer = surface_pointer("courts")
    tail = f" Every treaty is in {pointer}." if pointer else ""
    if not allies and not clients:
        return (f"France stands alone, Sire — no alliance is signed and no "
                f"client owes us fealty.{tail} {CABINET_LINE_FOR_DESK}")
    parts = []
    if allies:
        parts.append(f"Our allies, Sire: {_join(allies)}.")
    else:
        parts.append("No alliance is signed, Sire.")
    if clients:
        parts.append(f"Our clients: {_join(clients)}.")
    return " ".join(parts) + tail


def _answer_safe(world, player: str, region_name: str) -> Optional[str]:
    """AAR-17: "is Vienna safe?" — the province, who holds it, what of ours
    stands there, and every enemy corps AT WAR with us within two marches
    THAT WE CAN SEE (`get_visible_enemies`, Golden Rule 5: a fogged corps is
    never named, and the answer says how far our intelligence reaches)."""
    from backend.models.intel import FULL, get_strength_band
    region = world.get_region(region_name)
    if region is None:
        return None
    from backend.models.intel import PARTIAL
    holder = _court(world, getattr(region, "controller", "") or "")
    ours = getattr(region, "controller", None) == player
    own = [m for m in world.get_marshals_in_region(region_name)
           if m.nation == player and int(getattr(m, "strength", 0) or 0) > 0
           and not getattr(m, "captured_by", "")]
    # A foreign garrison is intelligence: it is read only where the cell is
    # in view (PARTIAL+), exactly as the region panel's fog sentinel does.
    in_view = ours or bool(world.get_region_intel(region_name).visibility_at_least(PARTIAL))
    garrison = int(getattr(region, "garrison_strength", 0) or 0) if in_view else 0
    adjacent = list(getattr(region, "adjacent_regions", None) or [])
    two_off = set()
    for name in adjacent:
        near = world.get_region(name)
        for far in (getattr(near, "adjacent_regions", None) or []) if near else []:
            if far != region_name and far not in adjacent:
                two_off.add(far)
    threats = []
    for enemy in world.get_visible_enemies(player):
        if int(getattr(enemy, "strength", 0) or 0) <= 0:
            continue
        if not world.is_at_war(player, getattr(enemy, "nation", "")):
            continue
        where = enemy.location
        if where == region_name:
            steps = 0
        elif where in adjacent:
            steps = 1
        elif where in two_off:
            steps = 2
        else:
            continue
        intel = world.get_region_intel(where)
        force = (f"{int(enemy.strength):,} men" if intel.visibility == FULL
                 else get_strength_band(int(enemy.strength)))
        threats.append((steps, enemy, force))
    threats.sort(key=lambda t: (t[0], -int(t[1].strength)))
    parts = []
    whose = "ours" if ours else f"{holder}'s"
    if own:
        parts.append(f"{region_name} is {whose}, Sire; "
                     + _join([f"{_display(m.name)}'s {int(m.strength):,}" for m in own])
                     + " stand there"
                     + (f" beside a garrison of {garrison:,}" if garrison > 0 else "") + ".")
    elif garrison > 0:
        parts.append(f"{region_name} is {whose}, Sire, held by a garrison of {garrison:,}.")
    elif not in_view:
        parts.append(f"{region_name} is {whose}, Sire; we have no intelligence "
                     f"on what holds it.")
    else:
        parts.append(f"{region_name} is {whose}, Sire, with no corps of ours in it.")
    if threats:
        said = []
        for steps, enemy, force in threats[:4]:
            distance = ("stands IN it" if steps == 0 else
                        f"is at {enemy.location}, one march away" if steps == 1 else
                        f"is at {enemy.location}, two marches off")
            said.append(f"{_display(enemy.name)} of {_court(world, enemy.nation)} "
                        f"{distance} ({force})")
        parts.append("Threats we can see: " + "; ".join(said) + ".")
        nearest = threats[0][0]
        if nearest == 0:
            verdict = "It is contested, not safe."
        elif nearest == 1 and not own and garrison <= 0:
            verdict = "It is in danger — nothing of ours stands in its way."
        elif nearest == 1:
            verdict = "It is held, but threatened."
        else:
            verdict = "It is safe for a turn or two, no longer."
        parts.append(verdict)
    else:
        parts.append("No enemy corps stands within two marches of it, so far "
                     "as our intelligence reaches — it looks safe today.")
    return " ".join(parts)


def _answer_truce_clock(world, player: str, nation: str) -> Optional[str]:
    """AAR-17: how long the armistice has to run — `ARMISTICE_DURATION` less
    the turns elapsed (`world.armistice_turns`, the same counter the engine
    ticks), and which way it falls at expiry by the engine's own rule (the
    relation against `ARMISTICE_AUTO_PEACE_RELATION`: peace above, the war
    resumes below)."""
    from backend.display_names import STATE_DISPLAY, plural
    from backend.game_logic import diplomacy as D
    duration = int(getattr(D, "ARMISTICE_DURATION", 5) or 5)
    threshold = int(getattr(D, "ARMISTICE_AUTO_PEACE_RELATION", 0) or 0)
    elapsed_map = getattr(world, "armistice_turns", {}) or {}

    def _line(court_tag: str) -> str:
        key = world._make_diplo_key(player, court_tag)
        left = max(0, duration - int(elapsed_map.get(key, 0) or 0))
        relation = int((getattr(world, "nation_relations", {}) or {}).get(key, 0) or 0)
        court = _court(world, court_tag)
        outcome = (f"as relations stand ({relation:+d}, against {threshold:+d} "
                   f"needed) it would become peace"
                   if relation >= threshold else
                   f"as relations stand ({relation:+d}, against {threshold:+d} "
                   f"needed) the war would resume")
        when = ("lapses at the end of this turn" if left <= 0
                else f"has {plural(left, 'turn')} to run")
        return f"The armistice with {court} {when}, Sire; when it lapses, {outcome}."

    if nation:
        state = world.get_diplomatic_state(player, nation)
        if state != "ARMISTICE":
            shown = STATE_DISPLAY.get(state, str(state).replace("_", " ").title())
            standing = ("are at war" if state == "WAR"
                        else f"stand at {shown}")
            return (f"There is no armistice with {_court(world, nation)}, Sire — "
                    f"France and {_court(world, nation)} {standing}.")
        return _line(nation)
    courts = []
    for key, state in (getattr(world, "diplomatic_states", {}) or {}).items():
        if state != "ARMISTICE":
            continue
        parts = str(key).split("|")
        if len(parts) == 2 and player in parts:
            courts.append(parts[0] if parts[1] == player else parts[1])
    if not courts:
        return f"No armistice stands, Sire — every war is a war and every peace a peace."
    return " ".join(_line(c) for c in sorted(courts))


def _answer_war_effort(world, player: str) -> Optional[str]:
    """AAR-17 / DESK-8: "how is the war effort" — the NATIONAL war weariness
    (`world.war_exhaustion`, the figure the Charges of Empire and the peace
    threshold read), ours in the clear and every court's at war with us
    through the Diplomatic Ledger's own fogged line."""
    from backend.game_logic.diplomatic_ledger import _build_war_weariness_line
    exhaustion = getattr(world, "war_exhaustion", {}) or {}
    ours = int(exhaustion.get(player, 0) or 0)
    prev = int((getattr(world, "_prev_war_exhaustion", {}) or {}).get(player, 0) or 0)
    trend = "rising" if ours > prev else "falling" if ours < prev else "steady"
    parts = [f"France's war weariness stands at {ours} ({trend}), Sire."]
    foes = []
    try:
        foes = sorted(world.get_nations_at_war_with(player))
    except Exception:
        foes = []
    read, unread = [], []
    for foe in foes:
        line = _build_war_weariness_line(foe, world)
        if line:
            read.append(f"{_court(world, foe)} {int(line.get('value') or 0)} "
                        f"({line.get('trend')})")
        else:
            unread.append(_court(world, foe))
    if read:
        parts.append("Of the courts at war with us: " + ", ".join(read) + ".")
    if unread:
        parts.append(f"{_join(unread)} we cannot read.")
    parts.append("It climbs while the war lasts and falls at peace; the "
                 "Charges of Empire draw on it, and a weary court sues sooner.")
    pointer = surface_pointer("courts")
    if pointer:
        parts.append(f"Each court's line is in {pointer}.")
    return " ".join(parts)


def _answer_news(world, player: str) -> Optional[str]:
    """AAR-17 / DESK-14: "what happened last turn" — this morning's dispatch
    (`world.last_morning_dispatch`: the headline and the turn's events), and
    where the whole briefing lives. Never the raw shrug."""
    dispatch = getattr(world, "last_morning_dispatch", None) or {}
    pointer = surface_pointer("dispatch")
    gazette = surface_pointer("gazette")
    tail = ""
    if pointer:
        tail = f" The whole briefing is on {pointer}"
        tail += f"; the record in {gazette}." if gazette else "."
    headline = ((dispatch.get("headline") or {}).get("text")
                if isinstance(dispatch.get("headline"), dict) else dispatch.get("headline"))
    events = []
    for entry in (dispatch.get("turn_events") or []):
        text = (entry.get("message") or entry.get("text") or entry.get("headline")
                if isinstance(entry, dict) else entry)
        if text:
            events.append(str(text).strip().rstrip("."))
    turn = int(dispatch.get("turn") or getattr(world, "current_turn", 0) or 0)
    if not headline and not events:
        if turn <= 1:
            return ("The campaign has just opened, Sire — there is no last turn "
                    f"to report.{tail}")
        return (f"Nothing of note reached the dispatches this morning, Sire — "
                f"turn {turn} opened quietly.{tail}")
    parts = []
    if headline:
        parts.append(f"This morning's dispatch leads with: {str(headline).strip()}")
    if events:
        parts.append("Overnight: " + "; ".join(events[:4])
                     + (f"; and {len(events) - 4} more" if len(events) > 4 else "") + ".")
    return " ".join(parts) + tail


def own_fallen_names(world) -> List[str]:
    """DESK-15: the player's own fallen marshals (the tombstones with our
    nation), so the desk can be asked about them. No fog on our own dead."""
    if not OUR_OWN_FALLEN_ARE_ANSWERED or world is None:
        return []
    player = getattr(world, "player_nation", None)
    return [name for name, tomb in (getattr(world, "fallen_marshals", None) or {}).items()
            if (tomb or {}).get("nation") == player]


def _answer_own_fallen(world, name: str, tomb: Dict) -> str:
    """DESK-15: our own marshal who is gone — in the first person, with the
    cause the tombstone carries (a DISMISSED marshal was never destroyed,
    FA-47's rule)."""
    shown = _display(name)
    where = str(tomb.get("location") or "the field")
    turn = int(tomb.get("turn") or 0)
    cause = str(tomb.get("cause") or "")
    pointer = surface_pointer("marshals")
    bench = (f" The bench on {pointer} shows who may be commissioned in his place."
             if pointer else "")
    if cause == "dismissed":
        return (f"Marshal {shown} was dismissed from the service on turn {turn}, "
                f"Sire — he holds no command.{bench}")
    return (f"Marshal {shown} fell at {where} on turn {turn}, Sire — his corps "
            f"was destroyed and no order can reach him.{bench}")


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
        if THE_PRICE_IS_THE_QUOTE:
            return _answer_levy_price(world, player, what)
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
        # CRT-7 / AAR-17: the war question and its kin.
        if kind in _WAR_QUESTION_KINDS and not THE_DESK_ANSWERS_THE_WAR_QUESTION:
            return None
        if kind == "wars":
            return _answer_wars(world, player)
        if kind == "allies":
            return _answer_allies(world, player)
        if kind == "safe":
            return _answer_safe(world, player, subject)
        if kind == "truce_clock":
            return _answer_truce_clock(world, player, subject)
        if kind == "war_effort":
            return _answer_war_effort(world, player)
        if kind == "news":
            return _answer_news(world, player)
    except Exception as exc:  # the desk must never break the status verb
        print(f"[QUESTION DESK] could not answer {question!r}: {exc}")
        return None
    return None
