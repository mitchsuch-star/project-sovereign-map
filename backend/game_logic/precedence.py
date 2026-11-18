"""Row MC — "Mon Cousin": the Order of the Marshalate (docs/MARSHALATE_SPEC.md).

The Emperor addressed each marshal as "Mon Cousin". This module is the court
they stood in: a durable ORDER OF PRECEDENCE (the titles the Emperor grants,
then the order of the 1804 list) beside the season's laurels; a lifetime
RENOWN beside the eight-turn glory window; and a BOOK OF INCIDENTS — every
move of one marshal's view of another, with its cause, its place and its
turn, so that every surface can say WHY two men are friends or enemies and
the memory outlives the number.

What it adds to the game (each rule behind its own named seam, the
session's OFF list `tests/_ba6_seams.py`):

  * the book: one writer (`note`) for every new move of a view, one recorder
    (`record`) for the moves the older writers make; seeded at the opening
    from the scenario's authored causes;
  * renown: every laurel a marshal wins is banked for good (a defeat costs
    one); the season's glory still drives envy and the crown, unchanged;
  * the order: titles first (a prince, then a duke — a title of victory or
    an estate's ducal style), then the order of the 1804 list (later batons
    after); captives keep their place, marked;
  * two-way bonds: brothers in arms (a third shared victory between friends
    makes them Devoted), a shared defeat sours the view of the man who led it
    (unless the Emperor took the field himself), a rescue mends the view of
    the man who came up, a silence while a comrade fought is remembered (the
    Auerstedt rule), and an old quarrel cools with time (a Rival view, never
    a Hostile one);
  * titles of victory: a decisive victory a marshal led away from the
    Emperor's eye puts a title in the Emperor's gift — Duke of the field, or
    Prince where he is a duke already — priced in authority; the seniors it
    passes over remember it; the courts confer theirs by the same rule;
  * serving under a junior: a senior who fought under a junior's lead holds
    it against him (the order card says so beforehand);
  * the account: a joint defeat of the player's corps asks the Emperor whose
    it was (he may take it on himself, lay it on the lead or on another, or
    let it lie);
  * the claim: a marshal whose deeds stand three places above his place in
    the order asks for his due;
  * an audience names its cause (the rival's laurels, where and when).

No rule here draws on any random stream: every move is a function of the
world as the battle left it, so the battle's dice are the battle's alone.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Tuple

from backend.errors import report


# ═══════════════════════════════════════════════════════════════════════
# The seams (row MC). Each returns True in the game; held down (False) the
# rule is the commit before (`tests/_ba6_seams.py`).
# ═══════════════════════════════════════════════════════════════════════

def the_book_keeps_its_incidents() -> bool:
    """Every move of a marshal's view of another is written in the book with
    its cause, place and turn (the older writers' moves are recorded beside
    them; the new rules write through `note`), and the opening seeds it from
    the scenario's authored causes. Down: no book is kept, and no surface
    names a cause."""
    return True


def a_marshal_banks_his_renown() -> bool:
    """Every laurel a marshal wins is banked for good as his renown (a
    defeat that costs glory costs one renown). Down: no renown."""
    return True


def the_order_of_precedence_stands() -> bool:
    """The court has an order: titles first, then the order of the 1804
    list; captives keep their place. Down: no order (the rules that read it
    — titles' passing-over, serving under a junior, the claim — are idle)."""
    return True


def the_seeds_read_as_of_1805() -> bool:
    """Three authored enmities are read as they stood in 1805, not as they
    became: Davout and Bernadotte, Murat and Bernadotte, and Bernadotte and
    the Emperor open as Rivals (-1), not Hostile (-2) — the famous feud of
    Davout and Bernadotte is Auerstedt's, October 1806, and the game can
    now produce its own Auerstedt (`a_silence_is_remembered`). Down: the
    values the scenario carried before (-2)."""
    return True


def brothers_in_arms() -> bool:
    """Friends (+1 both ways) who share a fourth victory (a real battle, the
    glory ladder's own bar) become Devoted."""
    return True


def a_shared_defeat_sours() -> bool:
    """A defeat shared by two or more corps sours the view of the man who
    led it (a Professional or Rival view falls a rung, never below Rival by
    this road; a friend forgives once) — unless the Emperor was on the
    field. On the player's side the account asks first."""
    return True


def a_rescue_mends() -> bool:
    """A corps that came up to a hard-pressed comrade's battle and saw it
    not lost is owed: the view of the man who came rises a rung (from
    Hostile too)."""
    return True


def a_silence_is_remembered() -> bool:
    """A Hostile comrade who stood within reach and did not march to the
    guns while a battle was lost or hung is remembered: the view of the
    silent man falls a rung (the Auerstedt rule)."""
    return True


def a_silence_is_remembered_when_pressed() -> bool:
    """Row MC, BA-6 (the court count's find, `tools/_ba6_court_rule_2026_11_17.json`):
    the Auerstedt rule reads its own namesake. Davout WON at Auerstedt,
    outnumbered two to one, and never forgave Bernadotte, who stood within
    reach and did not come — the danger he was left in was the wrong, not
    the result. So the silence is remembered when the lead was hard pressed
    (his side's men fewer than the foe's, the rescue's own reading), whether
    he won or not. Down: only a battle lost or hung, as row MC built it —
    under which ten AI-played French campaigns recorded no silence at all."""
    return True


def old_quarrels_cool() -> bool:
    """A Rival view (-1) that a quarrel of the campaign made (an incident of
    play, not an authored history) cools to Professional (0) after twelve
    turns with no incident between them; a Hostile view never cools by time
    alone, and an authored rivalry is character."""
    return True


def titles_of_victory() -> bool:
    """A decisive victory a marshal led away from the Emperor's eye puts a
    title in the Emperor's gift for eight turns (Duke, or Prince for a duke),
    priced in authority; the seniors it passes over remember it. Down: no
    titles are offered or conferred."""
    return True


def ai_courts_confer_titles() -> bool:
    """A court confers the title its general earned by the same rule and
    price (its own authority). Down: only the player's court confers."""
    return True


def serving_under_a_junior_rankles() -> bool:
    """A senior who fought under a junior's lead holds it against him."""
    return True


def a_marshal_claims_his_due() -> bool:
    """A marshal whose renown stands three places above his place in the
    order, untitled, asks for his due (once in twelve turns)."""
    return True


def an_account_follows_a_joint_defeat() -> bool:
    """A defeat of two or more of the player's corps (the Emperor absent)
    asks whose it was before anything sours."""
    return True


def an_audience_names_its_cause() -> bool:
    """An envious marshal's audience names the laurels he resents (where and
    when they were won), and its quiet answer says what follows."""
    return True


def the_card_names_the_court() -> bool:
    """The attack card says beforehand what the court will make of the
    muster: a senior who will resent serving under the lead, a corps whose
    marshal is hostile to him or devoted to him (`order_card_line`, read over
    the muster's own joining corps). Down: the card is silent on the court."""
    return True


# ═══════════════════════════════════════════════════════════════════════
# The numbers
# ═══════════════════════════════════════════════════════════════════════

BOOK_KEEP = 4                 # incidents a pair keeps (the founding one stays)
TITLE_DUE_TURNS = 8           # a title stays in the Emperor's gift this long
DUKE_POINTS = 3               # a victory worth this much glory (unshadowed) earns a ducal title
PRINCE_POINTS = 4             # ...and this much a princely one, for a duke
DUKE_PRICE = 3                # authority, a ducal title
PRINCE_PRICE = 5              # authority, a princely title
TITLE_TRUST = 3               # his trust, on the day
ACCOUNT_PRICE = 2             # authority: the Emperor takes the defeat on himself
ACCOUNT_TRUST = 2             # the trust the account moves either way
ACCOUNT_SHOWS_FOR = 3         # turns an account waits for the channel before it lies
CLAIM_RENOWN = 6              # renown a claimant needs
CLAIM_GAP = 3                 # his renown rank above his place in the order, at least
CLAIM_COOLDOWN = 12           # turns between one man's claims
CLAIM_REFUSED_TRUST = 2       # "not yet"
CLAIM_REBUKED_TRUST = 4       # "a rebuke"
THAW_TURNS = 12               # a Rival view cools after this many quiet turns
BOND_COOLDOWN = 6             # a rescue or a silence between one pair, once in this many turns
JUNIOR_COOLDOWN = 8           # serving under a junior, once in this many turns per pair
BROTHERS_AT = 4               # shared victories (real battles) that make friends Devoted
RIVAL_DEEDS = 2               # a senior whose renown is within this of the new title's man feels passed over
SENIORITY_UNSET = 0
LATER_BATON = 100             # a marshal with no authored seat ranks after the list, in roster order

# The authored values row MC reads as of 1805 (`the_seeds_read_as_of_1805`):
# the pair, the 1805 value, the value the scenario carried before.
SEEDS_AS_OF_1805 = (
    ("Davout", "Bernadotte", -1, -2),
    ("Murat", "Bernadotte", -1, -2),
    ("Bernadotte", "Napoleon", -1, -2),
)

# What a view means in the field — the consequences already in the game,
# read off `combat_executor._RELATIONSHIP_SCALING`, the Hostile reinforcement
# bar and the SUPPORT objection ladder. Said, never computed here.
CONSEQUENCE = {
    2: "fights beside him as one mind: half again his weight in a joint fight",
    1: "a quarter more of his weight in a joint fight",
    0: "his full weight in a joint fight",
    -1: "half his weight in a joint fight; a support order beside him is resented",
    -2: "brings nothing to a joint fight and will not march to his guns unless ordered",
}

LABELS = {2: "Devoted", 1: "Friendly", 0: "Professional", -1: "Rival", -2: "Hostile"}


# ═══════════════════════════════════════════════════════════════════════
# The court and its order
# ═══════════════════════════════════════════════════════════════════════

def _is_client(marshal) -> bool:
    try:
        from backend.game_logic.contingent import is_clients_general
        return bool(is_clients_general(marshal))
    except Exception as exc:
        report(exc, "precedence._is_client")
        return False


def in_the_court(marshal) -> bool:
    """A marshal of the order: not the sovereign, not a client's general,
    standing or held captive."""
    if marshal is None or getattr(marshal, "is_sovereign", False) or _is_client(marshal):
        return False
    return int(getattr(marshal, "strength", 0) or 0) > 0 or bool(getattr(marshal, "captured_by", ""))


def court(world, nation: str) -> List[Any]:
    return [m for m in world.marshals.values()
            if getattr(m, "nation", None) == nation and in_the_court(m)]


def estate_style(marshal) -> str:
    """The ducal style an estate gives him (the dotation's own honorific)."""
    regions = list(getattr(marshal, "dotation_regions", []) or [])
    if not regions:
        return ""
    from backend.game_logic.dotation import derive_title
    return derive_title(regions[0])


def tier_of(marshal) -> int:
    """2 a prince, 1 a duke (by a title of victory or an estate's style), 0."""
    tiers = [int(h.get("tier", 0) or 0) for h in (getattr(marshal, "honours", []) or [])
             if isinstance(h, dict)]
    best = max(tiers) if tiers else 0
    if best < 1 and estate_style(marshal):
        best = 1
    return best


def style_of(marshal) -> str:
    """His highest title, as he is styled: a title of victory before an
    estate's (the title names a field he won; the estate pays him)."""
    honours = [h for h in (getattr(marshal, "honours", []) or []) if isinstance(h, dict)]
    if honours:
        top = max(honours, key=lambda h: (int(h.get("tier", 0) or 0), int(h.get("turn", 0) or 0)))
        return str(top.get("name") or "")
    return estate_style(marshal)


def seat_of(world, marshal) -> int:
    """His seat on the list: authored (the order of the 1804 list), else
    after the list in roster order."""
    seat = int(getattr(marshal, "seniority", SENIORITY_UNSET) or SENIORITY_UNSET)
    if seat > SENIORITY_UNSET:
        return seat
    names = list(world.marshals.keys())
    try:
        return LATER_BATON + names.index(marshal.name)
    except ValueError:
        return LATER_BATON + len(names)


def order_of_precedence(world, nation: str) -> List[Any]:
    """The court in its order: titles first, then the seat, then the name."""
    return sorted(court(world, nation),
                  key=lambda m: (-tier_of(m), seat_of(world, m), str(m.name)))


def place_in_the_order(world, marshal) -> Tuple[int, int]:
    """(his place, of how many) — (0, 0) outside the order."""
    if not (the_order_of_precedence_stands() and in_the_court(marshal)):
        return 0, 0
    order = order_of_precedence(world, marshal.nation)
    for i, m in enumerate(order, 1):
        if m.name == marshal.name:
            return i, len(order)
    return 0, len(order)


def renown_of(marshal) -> int:
    return int(getattr(marshal, "renown", 0) or 0)


def renown_order(world, nation: str) -> List[Any]:
    """The court by renown, its order breaking ties."""
    order = order_of_precedence(world, nation)
    rank = {m.name: i for i, m in enumerate(order)}
    return sorted(order, key=lambda m: (-renown_of(m), rank[m.name]))


def renown_place(world, marshal) -> int:
    for i, m in enumerate(renown_order(world, marshal.nation), 1):
        if m.name == marshal.name:
            return i
    return 0


def trails_his_deeds(world, marshal) -> bool:
    """His renown stands CLAIM_GAP places or more above his place in the
    order, he is untitled and he has CLAIM_RENOWN renown."""
    if not (the_order_of_precedence_stands() and in_the_court(marshal)):
        return False
    if tier_of(marshal) > 0 or renown_of(marshal) < CLAIM_RENOWN:
        return False
    place, _ = place_in_the_order(world, marshal)
    return place > 0 and place - renown_place(world, marshal) >= CLAIM_GAP


# ═══════════════════════════════════════════════════════════════════════
# The book of incidents
# ═══════════════════════════════════════════════════════════════════════

def _key(a: str, b: str) -> str:
    return "|".join(sorted((str(a), str(b))))


def book(world) -> Dict[str, Dict[str, Any]]:
    store = getattr(world, "marshal_ledger", None)
    if not isinstance(store, dict):
        store = {}
        world.marshal_ledger = store
    return store


def entry(world, a: str, b: str) -> Dict[str, Any]:
    store = book(world)
    key = _key(a, b)
    row = store.get(key)
    if not isinstance(row, dict):
        row = {"incidents": [], "won": 0, "lost": 0}
        store[key] = row
    row.setdefault("incidents", [])
    row.setdefault("won", 0)
    row.setdefault("lost", 0)
    return row


def record(world, a: str, b: str, kind: str, place: str = "", *,
           a_to_b: int = 0, b_to_a: int = 0, note_text: str = "",
           turn: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """The recorder: one incident between A and B (what A's view of B and
    B's of A moved by it). Nothing is written with the book's seam down."""
    if not the_book_keeps_its_incidents() or not a or not b or a == b:
        return None
    row = entry(world, a, b)
    first, second = sorted((str(a), str(b)))
    flipped = first != str(a)
    incident = {
        "turn": int(turn if turn is not None else getattr(world, "current_turn", 0) or 0),
        "kind": str(kind),
        "place": str(place or ""),
        "a": first, "b": second,
        "a_to_b": int(b_to_a if flipped else a_to_b),
        "b_to_a": int(a_to_b if flipped else b_to_a),
    }
    if note_text:
        incident["note"] = str(note_text)
    incidents = row["incidents"]
    incidents.append(incident)
    if len(incidents) > BOOK_KEEP:
        # the founding incident (a seed) stays: it is the pair's history
        founding = incidents[0] if incidents[0].get("kind") == "seed" else None
        tail = incidents[-(BOOK_KEEP - (1 if founding else 0)):]
        row["incidents"] = ([founding] if founding else []) + tail
    return incident


def _move_stored(marshal, other_name: str, delta: int, floor: int, cap: int) -> int:
    """Move his STORED view of the other by delta within [floor, cap] — the
    bound only stops a move, never pushes a view the other way."""
    if marshal is None or not delta:
        return 0
    stored = int((getattr(marshal, "relationships", {}) or {}).get(other_name, 0) or 0)
    if delta < 0:
        target = max(stored + delta, min(floor, stored))
    else:
        target = min(stored + delta, max(cap, stored))
    target = max(-2, min(2, target))
    if target == stored:
        return 0
    marshal.set_relationship(other_name, target)
    return target - stored


def note(world, a, b, kind: str, place: str = "", *, da: int = 0, db: int = 0,
         floor_a: int = -2, floor_b: int = -2, cap_a: int = 2, cap_b: int = 2,
         note_text: str = "", stamp: bool = True) -> Tuple[int, int]:
    """THE writer of row MC's moves: A's stored view of B by `da`, B's of A
    by `db` (each held inside its floor and cap), the incident written with
    what actually moved, the pair's change-turn stamped, one line logged.
    Returns (moved A->B, moved B->A)."""
    if a is None or b is None or a.name == b.name:
        return 0, 0
    moved_a = _move_stored(a, b.name, da, floor_a, cap_a)
    moved_b = _move_stored(b, a.name, db, floor_b, cap_b)
    turn = int(getattr(world, "current_turn", 0) or 0)
    if stamp:
        if moved_a:
            a.last_relationship_change_turn[b.name] = turn
        if moved_b:
            b.last_relationship_change_turn[a.name] = turn
    record(world, a.name, b.name, kind, place, a_to_b=moved_a, b_to_a=moved_b,
           note_text=note_text)
    if moved_a or moved_b:
        _log_move(world, a, b, kind, place, moved_a, moved_b)
    return moved_a, moved_b


def _log_move(world, a, b, kind: str, place: str, moved_a: int, moved_b: int) -> None:
    try:
        world.log_event({
            "type": "marshal_bond",
            "marshal": a.name, "toward": b.name, "kind": kind,
            "place": place, "a_to_b": int(moved_a), "b_to_a": int(moved_b),
            "a_view": int(a.relationships.get(b.name, 0)),
            "b_view": int(b.relationships.get(a.name, 0)),
            "nation": a.nation,
            "line": bond_line(world, a, b, kind, place, moved_a, moved_b),
        })
    except Exception as exc:
        report(exc, "precedence._log_move")


def incidents(world, a: str, b: str) -> List[Dict[str, Any]]:
    row = book(world).get(_key(a, b))
    return list(row.get("incidents", [])) if isinstance(row, dict) else []


def latest(world, a: str, b: str) -> Optional[Dict[str, Any]]:
    found = incidents(world, a, b)
    return found[-1] if found else None


def _shown(name: str) -> str:
    try:
        from backend.display_names import humanize_entity_name
        return humanize_entity_name(str(name))
    except Exception as exc:
        report(exc, "precedence._shown")
        return str(name)


def _place(place: str) -> str:
    return _shown(place) if place else ""


# One sentence per kind, in the staff's voice, about what passed between the
# two (A is the man whose view is read). {a} {b} {at} are filled by
# `incident_line`; {at} is " at <place>" or "".
INCIDENT_LINES = {
    "seed": "{note}",
    "shared_victory": "they fought side by side{at} and won",
    "shared_defeat": "they shared a defeat{at}",
    "brothers": "a fourth victory together{at}: brothers in arms",   # BROTHERS_AT (BA6-X11)
    "blamed_the_lead": "{a} blames {b} for the defeat{at}",
    "blame_laid": "the Emperor laid the defeat{at} on {b}",
    "blame_taken": "the Emperor took the defeat{at} on himself",
    "rescue": "{b} came up when {a} was hard pressed{at}",
    "silence": "{b} stood within reach and did not march to the guns{at}",
    "thaw": "the old quarrel cooled with time",
    "passed_over": "{b} was raised above {a}: {note}",
    "under_junior": "{a} fought under {b}'s lead{at}, his junior",
    "laurels": "{b}'s laurels{at} were counted above his own",
    "escalation": "the quarrel over the laurels hardened",
    "mediated": "the Emperor mediated between them",
    "decreed": "reconciled by the Emperor's decree",
    "reprimanded": "both were reprimanded before the staff",
    "harsh_words": "harsh words before the general staff",
    "breach": "{a} refused to attend council where {b} was present",
    "friendly_fire": "{b}'s guns fell on {a}'s men{at}",
    "commissioned": "{note}",
    "claim_rebuked": "{a}'s claim was rebuked while {b} stood above him",
}


def _note_for(incident: Dict[str, Any], viewer: str) -> str:
    """An incident's note as read from `viewer`'s side: a founding incident
    keeps each direction's own authored cause (`note_a` the first name's view
    of the second, `note_b` the second's of the first), else the one `note`."""
    first = incident.get("a", "")
    own = incident.get("note_a") if viewer == first else incident.get("note_b")
    other = incident.get("note_b") if viewer == first else incident.get("note_a")
    return str(own or incident.get("note") or other or "")


def incident_line(world, incident: Dict[str, Any], viewer: str) -> str:
    """The incident as a sentence read from `viewer`'s side."""
    if not isinstance(incident, dict):
        return ""
    first, second = incident.get("a", ""), incident.get("b", "")
    other = second if viewer == first else first
    template = INCIDENT_LINES.get(str(incident.get("kind") or ""), "")
    place = _place(str(incident.get("place") or ""))
    text = template.format(a=_shown(viewer), b=_shown(other),
                           at=(f" at {place}" if place else ""),
                           note=_note_for(incident, viewer))
    return text.strip()


# Kinds that speak against a man and for him: an incident of either kind that
# could not move a view already at its bound still names why he feels so (a
# slight to a man already a Rival feeds the quarrel the card shows).
AGAINST = {"shared_defeat", "blamed_the_lead", "blame_laid", "silence", "passed_over",
           "under_junior", "escalation", "harsh_words", "breach", "friendly_fire",
           "claim_rebuked", "laurels"}
FOR = {"shared_victory", "brothers", "rescue", "blame_taken", "thaw", "mediated", "decreed"}


def cause_of(world, viewer: str, other: str) -> str:
    """Why the viewer feels as he does about the other: the latest incident
    that moved his view, or that speaks the way his view leans (a slight to a
    Rival, a rescue to a friend), else the founding one — one line with its
    turn."""
    if not the_book_keeps_its_incidents():
        return ""
    found = incidents(world, viewer, other)
    if not found:
        return ""
    first, _second = sorted((viewer, other))
    mine = "a_to_b" if viewer == first else "b_to_a"
    view = 0
    m = world.marshals.get(viewer) if hasattr(world, "marshals") else None
    if m is not None:
        view = int((getattr(m, "relationships", {}) or {}).get(other, 0) or 0)

    def speaks(i):
        if int(i.get(mine, 0) or 0) != 0 or i.get("kind") == "seed":
            return True
        kind = str(i.get("kind") or "")
        return (view < 0 and kind in AGAINST) or (view > 0 and kind in FOR)
    moving = [i for i in found if speaks(i)]
    # the latest; within one turn, the incident that moved his view before one
    # that only fed it (a defeat blamed and a junior's lead in the same battle)
    pick = max(moving or found, key=lambda i: (int(i.get("turn", 0) or 0),
                                                1 if int(i.get(mine, 0) or 0) != 0 else 0,
                                                (moving or found).index(i)))
    line = incident_line(world, pick, viewer)
    if not line:
        return ""
    if pick.get("kind") == "seed":
        return line
    return f"{line} (turn {int(pick.get('turn', 0) or 0)})"


def bond_line(world, a, b, kind: str, place: str, moved_a: int, moved_b: int) -> str:
    """The campaign log's sentence for a move: who now feels what, and why."""
    parts = []
    if moved_a:
        parts.append(f"{_shown(a.name)}'s view of {_shown(b.name)}: "
                     f"{LABELS[int(a.relationships.get(b.name, 0))]}")
    if moved_b:
        parts.append(f"{_shown(b.name)}'s view of {_shown(a.name)}: "
                     f"{LABELS[int(b.relationships.get(a.name, 0))]}")
    why = incident_line(world, {"a": a.name, "b": b.name, "kind": kind, "place": place}, a.name)
    head = "; ".join(parts)
    return f"{head} — {why}." if why else f"{head}."


# ═══════════════════════════════════════════════════════════════════════
# Renown and the title a victory earns
# ═══════════════════════════════════════════════════════════════════════

def bank_renown(marshal, points: int) -> None:
    """From the one glory chokepoint (`jealousy._append_glory`): a laurel is
    banked for good; a defeat that costs glory costs one renown."""
    if not a_marshal_banks_his_renown() or marshal is None or not points:
        return
    if getattr(marshal, "is_sovereign", False):
        return
    now = renown_of(marshal)
    marshal.renown = now + int(points) if points > 0 else max(0, now - 1)


def title_name(tier: int, place: str) -> str:
    shown = _place(place) or "the Field"
    return f"Prince of {shown}" if tier >= 2 else f"Duke of {shown}"


def victory_earns(world, marshal, points: int, place: str, *, shadowed: bool) -> None:
    """From `record_battle_glory`, for the man who LED a victory: a decisive
    victory away from the Emperor's eye puts the next title in the gift."""
    if not (titles_of_victory() and the_order_of_precedence_stands()):
        return
    if marshal is None or shadowed or not in_the_court(marshal):
        return
    tier = tier_of(marshal)
    if tier >= 2:
        return
    needed = PRINCE_POINTS if tier >= 1 else DUKE_POINTS
    if int(points) < needed:
        return
    turn = int(getattr(world, "current_turn", 0) or 0)
    due = getattr(marshal, "title_due", None)
    if isinstance(due, dict) and int(due.get("tier", 0) or 0) == tier + 1 \
            and int(due.get("expires", -1)) >= turn:
        return                           # already in the gift: the first field names it
    marshal.title_due = {"tier": tier + 1, "name": title_name(tier + 1, place),
                         "place": str(place or ""), "turn": turn,
                         "expires": turn + TITLE_DUE_TURNS}
    if marshal.nation == getattr(world, "player_nation", None):
        try:
            world.log_event({"type": "title_in_the_gift", "marshal": marshal.name,
                             "title": marshal.title_due["name"], "place": str(place or ""),
                             "nation": marshal.nation, "turns": TITLE_DUE_TURNS})
        except Exception as exc:
            report(exc, "precedence.victory_earns: log")


def title_in_the_gift(world, marshal) -> Optional[Dict[str, Any]]:
    """The title standing in the Emperor's gift for him, or None (lapsed, or
    the rule down)."""
    if not titles_of_victory():
        return None
    due = getattr(marshal, "title_due", None)
    if not isinstance(due, dict):
        return None
    if int(due.get("expires", -1)) < int(getattr(world, "current_turn", 0) or 0):
        return None
    if int(due.get("tier", 0) or 0) <= tier_of(marshal):
        return None
    return due


def price_of(tier: int) -> int:
    """The BASE price of a title (the buy's recency raises it: `standing.buy`)."""
    return PRINCE_PRICE if tier >= 2 else DUKE_PRICE


def _priced(world, lord: str, base: int) -> Tuple[int, str]:
    """(the price a buy of `base` would pay now, the refusal or "")."""
    from backend.game_logic import standing
    price = int(standing.push_price(world, lord, base))
    q = standing.quote(world, lord, -price)
    return price, str(q.get("refusal") or "")


def _would_pass_over(world, marshal, tier: int) -> List[Any]:
    """The marshals of his court who would feel passed over by this title:
    they stood above him in the order and would stand below him after it,
    their own deeds rival his (renown within RIVAL_DEEDS of his — a senior
    with clearly fewer laurels knows the title was earned), and they are not
    his friends (a friend is glad of it)."""
    before = order_of_precedence(world, marshal.nation)
    above = [m for m in before[:before.index(marshal)]] if marshal in before else []
    out = []
    for m in above:
        if tier_of(m) >= tier:
            continue                     # a peer of the new rank keeps his place above
        if int(m.relationships.get(marshal.name, 0) or 0) >= 1:
            continue
        if renown_of(m) < renown_of(marshal) - RIVAL_DEEDS:
            continue
        out.append(m)
    return out


def confer_quote(world, marshal) -> Dict[str, Any]:
    """What conferring the title in the gift would cost and do, before it is
    done: {ok, name, tier, price, refusal, passed_over:[names], line}."""
    due = title_in_the_gift(world, marshal)
    if due is None:
        return {"ok": False, "refusal": "no title is in the Emperor's gift for him"}
    tier = int(due.get("tier", 1) or 1)
    price, refusal = _priced(world, marshal.nation, price_of(tier))
    over = [m.name for m in _would_pass_over(world, marshal, tier)]
    shown = [_shown(n) for n in over]
    if over:
        tail = ("; " + ", ".join(shown[:-1]) + (" and " if len(shown) > 1 else "") + shown[-1]
                + (" will hold it against him" if len(shown) > 1 else " will hold it against him"))
    else:
        tail = "; no senior is passed over"
    line = (f"{_shown(marshal.name)} created {due.get('name')} — {price} authority, his trust "
            f"+{TITLE_TRUST}, his expectation of a dotation rises{tail}.")
    return {"ok": not refusal, "name": due.get("name"), "tier": tier, "price": price,
            "refusal": refusal, "passed_over": over, "line": line}


def _styled(world, name: str) -> str:
    """A marshal named in prose: the ONE style (`display_names.marshal_title`)."""
    from backend.display_names import marshal_title
    return marshal_title(world, name) or _shown(name)


def confer_title(world, name: str) -> Dict[str, Any]:
    """The player's decree (POST /confer_title). BA-6's review (BA6-R2): the
    route confers only on a marshal of the player's own court; any other name
    is answered as an unknown one (a fogged court's honours are not read off
    the reply, and its authority is never spent from here). The courts confer
    their own titles in `_courts_confer`."""
    m = world.marshals.get(str(name or "")) if hasattr(world, "marshals") else None
    if m is None or getattr(m, "nation", None) != getattr(world, "player_nation", None):
        return {"success": False, "message": f"There is no marshal '{name}' in your service."}
    return _confer_title_on(world, name)


def _confer_title_on(world, name: str) -> Dict[str, Any]:
    """Confer the title in the gift: the authority paid (it lands whole or
    nothing does), the honour written, his trust and expectation raised, and
    every senior it passes over remembers it."""
    marshal = world.get_marshal(name) if hasattr(world, "get_marshal") else world.marshals.get(name)
    if marshal is None:
        return {"success": False, "message": f"There is no marshal '{name}'."}
    q = confer_quote(world, marshal)
    if not q.get("ok"):
        return {"success": False, "message": q.get("refusal") or "The title cannot be conferred."}
    due = dict(title_in_the_gift(world, marshal) or {})
    passed = _would_pass_over(world, marshal, int(q["tier"]))
    from backend.game_logic import standing
    paid = standing.buy(world, marshal.nation, price_of(int(q["tier"])), "title_conferred",
                        party=marshal.name, marshal=_shown(marshal.name), title=str(q["name"]))
    if paid.get("refusal"):
        return {"success": False, "message": str(paid.get("refusal"))}
    _confer(world, marshal, due, passed)
    return {"success": True,
            "message": (f"By decree, {_styled(world, marshal.name)} is created {q['name']}. "
                        + (f"{', '.join(_shown(m.name) for m in passed)} "
                           f"{'remember' if len(passed) > 1 else 'remembers'} it."
                           if passed else "No senior was passed over.")),
            "title_conferred": {"marshal": marshal.name, "title": q["name"],
                                "passed_over": [m.name for m in passed]}}


def _confer(world, marshal, due: Dict[str, Any], passed: Iterable[Any]) -> None:
    turn = int(getattr(world, "current_turn", 0) or 0)
    honours = list(getattr(marshal, "honours", []) or [])
    honours.append({"tier": int(due.get("tier", 1) or 1), "name": str(due.get("name") or ""),
                    "place": str(due.get("place") or ""), "turn": turn})
    marshal.honours = honours
    marshal.title_due = None
    try:
        marshal.modify_trust(TITLE_TRUST)
    except Exception as exc:
        report(exc, "precedence._confer: trust")
    try:
        from backend.game_logic import dotation
        dotation.raise_expectation(marshal, world, "title")
    except Exception as exc:
        report(exc, "precedence._confer: expectation")
    for senior in passed:
        # a slight makes a Rival, never by itself a Hostile
        note(world, senior, marshal, "passed_over", str(due.get("place") or ""),
             da=-1, floor_a=-1, note_text=f"created {due.get('name')}")
    try:
        world.log_event({"type": "title_conferred", "marshal": marshal.name,
                         "title": str(due.get("name") or ""), "nation": marshal.nation,
                         "passed_over": [m.name for m in passed]})
    except Exception as exc:
        report(exc, "precedence._confer: log")


# ═══════════════════════════════════════════════════════════════════════
# The battle: what it does to the bonds
# ═══════════════════════════════════════════════════════════════════════

def record_roll(world, a, b, change: int, won: bool, place: str) -> None:
    """The Win/Loss roll's own move (relationship.py), written in the book."""
    if change:
        record(world, a.name, b.name, "shared_victory" if won else "shared_defeat", place,
               a_to_b=int(change))


def _side_won(battle_result, primary, is_attacker: bool) -> Tuple[bool, bool]:
    outcome = str((battle_result or {}).get("outcome", "") or "")
    side = "attacker" if is_attacker else "defender"
    other = "defender" if is_attacker else "attacker"
    won = side in outcome and "victory" in outcome
    lost = other in outcome and "victory" in outcome
    return won, lost


def _a_real_battle(battle_result) -> bool:
    """The glory ladder's own bar (`jealousy.is_laurel`): a skirmish makes no
    brothers."""
    try:
        from backend.game_logic.jealousy import is_laurel
        atk = (battle_result or {}).get("attacker") or {}
        dfd = (battle_result or {}).get("defender") or {}
        return bool(is_laurel(int(atk.get("casualties", 0) or 0), int(dfd.get("casualties", 0) or 0)))
    except Exception as exc:
        report(exc, "precedence._a_real_battle")
        return False


def _decisive_loss(battle_result, is_attacker: bool) -> bool:
    """A defeat that counts: a victory of the other side, or this side's
    line broken (`forced_retreat`)."""
    _won, lost = _side_won(battle_result, None, is_attacker)
    side = (battle_result or {}).get("attacker" if is_attacker else "defender") or {}
    return bool(lost or (isinstance(side, dict) and side.get("forced_retreat")))


def after_shared_battle(world, *, attacker, defender, battle_result, region: str,
                        attacker_participants: List[Any], defender_participants: List[Any],
                        attacker_reinforcements: Iterable[Any] = (),
                        defender_reinforcements: Iterable[Any] = ()) -> None:
    """Row MC's battle rules, on both sides (GR5), after the Win/Loss roll:
    brothers in arms, the shared defeat (the account first on the player's
    side), the rescue, the silence, serving under a junior. Deterministic."""
    try:
        for is_attacker, lead, parts, came in (
                (True, attacker, attacker_participants, attacker_reinforcements),
                (False, defender, defender_participants, defender_reinforcements)):
            if lead is None:
                continue
            silent = _silent_comrades(world, lead, region, list(parts or []) + list(came or []))
            won, lost = _side_won(battle_result, lead, is_attacker)
            pool = [m for m in (parts or []) if m is not None]
            if lead not in pool:
                pool.insert(0, lead)
            sovereign_there = any(getattr(m, "is_sovereign", False) for m in pool)
            # the court's own men (a client's general fights beside them but
            # holds no place in the order and no bond in the book)
            mates = [m for m in pool if in_the_court(m)]
            if won and _a_real_battle(battle_result):
                _brothers(world, mates, region)
            if len(mates) >= 2 and _decisive_loss(battle_result, is_attacker) and not sovereign_there:
                _shared_defeat(world, lead, mates, region, battle_result)
            if not lost:
                _rescue(world, lead, came, region, battle_result, is_attacker)
            if not won or (a_silence_is_remembered_when_pressed()
                           and _hard_pressed(battle_result, is_attacker)):
                _silence(world, lead, silent, region)
            if not sovereign_there:
                _under_a_junior(world, lead, mates, region)
    except Exception as exc:
        report(exc, "precedence.after_shared_battle")


def _brothers(world, mates: List[Any], region: str) -> None:
    if not brothers_in_arms() or len(mates) < 2:
        return
    seen = set()
    for a in mates:
        for b in mates:
            if a.name >= b.name or (a.name, b.name) in seen:
                continue
            seen.add((a.name, b.name))
            row = entry(world, a.name, b.name) if the_book_keeps_its_incidents() else None
            if row is None:
                continue
            row["won"] = int(row.get("won", 0) or 0) + 1
            friends = (int(a.relationships.get(b.name, 0) or 0) >= 1
                       and int(b.relationships.get(a.name, 0) or 0) >= 1)
            devoted = (int(a.relationships.get(b.name, 0) or 0) >= 2
                       and int(b.relationships.get(a.name, 0) or 0) >= 2)
            if friends and not devoted and row["won"] >= BROTHERS_AT:
                note(world, a, b, "brothers", region, da=+1, db=+1)


def _shared_defeat(world, lead, mates: List[Any], region: str, battle_result) -> None:
    if not a_shared_defeat_sours():
        return
    others = [m for m in mates if m.name != lead.name]
    if not others:
        return
    if (lead.nation == getattr(world, "player_nation", None)
            and an_account_follows_a_joint_defeat() and the_book_keeps_its_incidents()):
        _queue_account(world, lead, others, region)
        return
    sour_on(world, lead, others, region)


def sour_on(world, lead, others: Iterable[Any], region: str) -> None:
    """Each comrade's view of the man who led the defeat: Professional or
    Rival falls a rung (never below Rival by this road); a friend forgives
    the first defeat and holds the second against him."""
    for m in others:
        view = int(m.relationships.get(lead.name, 0) or 0)
        if view >= 1:
            row = entry(world, m.name, lead.name) if the_book_keeps_its_incidents() else {"lost": 0}
            row["lost"] = int(row.get("lost", 0) or 0) + 1
            if row["lost"] >= 2:
                row["lost"] = 0
                note(world, m, lead, "blamed_the_lead", region, da=-1, floor_a=-1)
        else:
            note(world, m, lead, "blamed_the_lead", region, da=-1, floor_a=-1)


def _quiet_long_enough(m, other_name: str, world, turns: int) -> bool:
    last = int((getattr(m, "last_relationship_change_turn", {}) or {}).get(other_name, -99))
    return int(getattr(world, "current_turn", 0) or 0) - last >= turns


def _hard_pressed(battle_result, is_attacker: bool) -> bool:
    """The lead's side was hard pressed: its men (remaining and fallen) fewer
    than the foe's. ONE reading, for the rescue and the silence."""
    side = (battle_result or {}).get("attacker" if is_attacker else "defender") or {}
    other = (battle_result or {}).get("defender" if is_attacker else "attacker") or {}
    try:
        ours = int(side.get("remaining", 0) or 0) + int(side.get("casualties", 0) or 0)
        his = int(other.get("remaining", 0) or 0) + int(other.get("casualties", 0) or 0)
    except (TypeError, ValueError):
        ours, his = 0, 0
    return his > 0 and ours < his


def _rescue(world, lead, came: Iterable[Any], region: str, battle_result, is_attacker: bool) -> None:
    if not a_rescue_mends():
        return
    if not _hard_pressed(battle_result, is_attacker):
        return
    for m in came or ():
        if m is None or m.name == lead.name or not in_the_court(m) or not in_the_court(lead):
            continue
        if m.nation != lead.nation or not _quiet_long_enough(lead, m.name, world, BOND_COOLDOWN):
            continue
        note(world, lead, m, "rescue", region, da=+1)


def _silent_comrades(world, lead, region: str, fought: List[Any]) -> List[Any]:
    """The lead's Hostile comrades who stood within reach — on the field or
    one province from it — and did not march to the guns: not among those who
    fought or came up, standing, unbroken, and under no support order on him
    (a Hostile corps without one never answers the guns: the A-D4 rule). The
    field's own neighbours only — never a scan of the map."""
    if lead is None or not region or getattr(lead, "is_sovereign", False):
        return []
    near = {str(region)}
    try:
        place = world.get_region(region)
        near |= set(getattr(place, "adjacent_regions", []) or [])
    except Exception as exc:
        report(exc, "precedence._silent_comrades: region")
    fought_names = {getattr(m, "name", None) for m in fought or []}
    out = []
    for m in world.marshals.values():
        if m.nation != lead.nation or m.name == lead.name or m.name in fought_names:
            continue
        if getattr(m, "is_sovereign", False) or not in_the_court(m) or getattr(m, "captured_by", ""):
            continue
        if m.location not in near or int(getattr(m, "strength", 0) or 0) <= 0:
            continue
        if getattr(m, "broken", False) or int(getattr(m, "retreat_recovery", 0) or 0) > 0:
            continue
        if int(m.relationships.get(lead.name, 0) or 0) > -2:
            continue
        order = getattr(m, "strategic_order", None)
        if (order is not None and getattr(order, "command_type", None) == "SUPPORT"
                and getattr(order, "target", None) == lead.name):
            continue
        out.append(m)
    return sorted(out, key=lambda x: str(x.name))


def _silence(world, lead, silent: Iterable[Any], region: str) -> None:
    if not a_silence_is_remembered():
        return
    for m in silent or ():
        if m is None or m.name == lead.name or not in_the_court(lead):
            continue
        if not _quiet_long_enough(lead, m.name, world, BOND_COOLDOWN):
            continue
        note(world, lead, m, "silence", region, da=-1)


def _under_a_junior(world, lead, mates: List[Any], region: str) -> None:
    if not (serving_under_a_junior_rankles() and the_order_of_precedence_stands()):
        return
    if getattr(lead, "is_sovereign", False) or not in_the_court(lead):
        return
    lead_place, _ = place_in_the_order(world, lead)
    if lead_place <= 0:
        return
    for m in mates:
        if m.name == lead.name or not in_the_court(m):
            continue
        place, _ = place_in_the_order(world, m)
        if place <= 0 or place >= lead_place:
            continue
        if int(m.relationships.get(lead.name, 0) or 0) > 0:
            continue                     # a friend serves gladly
        if not _junior_quiet(world, m, lead):
            continue
        note(world, m, lead, "under_junior", region, da=-1, floor_a=-1)


def _junior_quiet(world, senior, lead) -> bool:
    turn = int(getattr(world, "current_turn", 0) or 0)
    for inc in reversed(incidents(world, senior.name, lead.name)):
        if inc.get("kind") == "under_junior":
            return turn - int(inc.get("turn", 0) or 0) >= JUNIOR_COOLDOWN
    return True


def order_card_line(world, lead, joining: Iterable[Any]) -> str:
    """The attack card's word on the court, beforehand: who ranks above the
    lead and will hold it against him, and the bonds that bite."""
    if lead is None or not the_card_names_the_court():
        return ""
    parts = []
    lead_place = place_in_the_order(world, lead)[0] if (
        serving_under_a_junior_rankles() and the_order_of_precedence_stands()) else 0
    for m in joining or ():
        if m is None or m.name == lead.name or getattr(m, "is_sovereign", False):
            continue
        view = int(m.relationships.get(lead.name, 0) or 0)
        if lead_place > 0 and in_the_court(m):
            place = place_in_the_order(world, m)[0]
            if 0 < place < lead_place and view <= 0:
                parts.append(f"{_shown(m.name)} ranks above {_shown(lead.name)} "
                             f"and will resent serving under him")
                continue
        if view <= -1:
            parts.append(f"{_shown(m.name)} is {LABELS[view].lower()} to {_shown(lead.name)}: "
                         f"{CONSEQUENCE[view]}")
        elif view >= 2:
            parts.append(f"{_shown(m.name)} is devoted to {_shown(lead.name)}: {CONSEQUENCE[2]}")
    return "; ".join(parts) + ("." if parts else "")


# ═══════════════════════════════════════════════════════════════════════
# The account (a joint defeat of the player's corps)
# ═══════════════════════════════════════════════════════════════════════

def _accounts(world) -> List[Dict[str, Any]]:
    store = getattr(world, "marshal_accounts", None)
    if not isinstance(store, list):
        store = []
        world.marshal_accounts = store
    return store


def _queue_account(world, lead, others: List[Any], region: str) -> None:
    turn = int(getattr(world, "current_turn", 0) or 0)
    _accounts(world).append({"lead": lead.name, "others": [m.name for m in others],
                             "place": str(region or ""), "turn": turn})


def _account_options(world, account: Dict[str, Any]) -> List[Dict[str, Any]]:
    lead = _shown(account["lead"])
    other = account.get("named") or (account.get("others") or [""])[0]
    price, refusal = _priced(world, getattr(world, "player_nation", ""), ACCOUNT_PRICE)
    can_pay = not refusal
    others_shown = ", ".join(_shown(n) for n in account.get("others", []))
    return [
        {"id": "take_it", "label": "The Emperor takes it",
         "detail": (f"{price} authority. Nothing sours between them; {lead}'s trust "
                    f"+{ACCOUNT_TRUST}."),
         "cost_note": f"{price} authority", "enabled": can_pay,
         **({} if can_pay else {"why": refusal})},
        {"id": "on_the_lead", "label": f"It falls on {lead}",
         "detail": (f"{others_shown} hold it against him (a Professional or Rival view falls a "
                    f"rung); his trust -{ACCOUNT_TRUST}."),
         "cost_note": "", "enabled": True},
        {"id": "on_another", "label": f"It falls on {_shown(other)}",
         "detail": (f"{lead}'s view of {_shown(other)} falls a rung; {_shown(other)}'s trust "
                    f"-{ACCOUNT_TRUST}. The others are spared."),
         "cost_note": "", "enabled": bool(other)},
        {"id": "let_it_lie", "label": "Let it lie",
         "detail": f"Free. {others_shown} hold it against {lead} as they will.",
         "cost_note": "", "enabled": True},
    ]


def _account_card(world, account: Dict[str, Any]) -> Dict[str, Any]:
    place = _place(account.get("place", ""))
    lead = _shown(account["lead"])
    others = account.get("others", [])
    # the man the lead would name: the senior of the others (he stood nearest the lead's own rank)
    named = sorted(others, key=lambda n: place_in_the_order(world, world.marshals.get(n))[0] or 99)
    account["named"] = named[0] if named else ""
    body = (f"Sire, an account is asked for the defeat at {place or 'the field'}. "
            f"{lead} led; {', '.join(_shown(n) for n in others)} fought under him. "
            f"Each has his version, and the staff will take whichever the Emperor gives.")
    return {
        "kind": "account",
        "title": f"An account is asked at {place or 'the field'}",
        "body": body,
        "speaker": account["lead"],
        "speaker_line": f"{lead}: \"The day was lost on the flank, Sire, not in the centre.\"",
        "options": _account_options(world, account),
        "context": dict(account),
        "tier": "audience",
        "turn": int(getattr(world, "current_turn", 0) or 0),
    }


def _same_account(a: Dict[str, Any], b: Dict[str, Any]) -> bool:
    return bool(isinstance(a, dict) and isinstance(b, dict)
                and a.get("lead") == b.get("lead") and a.get("place") == b.get("place")
                and int(a.get("turn", -1) if a.get("turn") is not None else -1)
                == int(b.get("turn", -2) if b.get("turn") is not None else -2))


def _waiting(world, context: Dict[str, Any]) -> bool:
    """The account is still in the book's waiting store (not yet settled)."""
    return any(_same_account(a, context) for a in _accounts(world))


def _the_account_on_screen(world) -> Optional[Dict[str, Any]]:
    pending = getattr(world, "pending_marshal_petition", None)
    if isinstance(pending, dict) and pending.get("kind") == "account":
        ctx = pending.get("context")
        return ctx if isinstance(ctx, dict) else None
    return None


def apply_account(world, choice: str, context: Dict[str, Any]) -> Dict[str, Any]:
    # BA-6's review (BA6-R1): an account already settled - let lie unseen, or
    # its commander gone - cannot be answered (and paid for) a second time
    if not _waiting(world, context):
        return {"success": False, "message": "That account is already settled."}
    lead = world.marshals.get(str(context.get("lead") or ""))
    others = [world.marshals.get(n) for n in (context.get("others") or [])]
    others = [m for m in others if m is not None]
    place = str(context.get("place") or "")
    _drop_account(world, context)
    if lead is None:
        return {"success": True, "message": "The account is closed: its commander is gone."}
    if choice == "take_it":
        from backend.game_logic import standing
        paid = standing.buy(world, getattr(world, "player_nation", ""), ACCOUNT_PRICE,
                            "blame_taken", party=lead.name, battle=_place(place) or "the field")
        if paid.get("refusal"):
            return {"success": False, "message": str(paid.get("refusal"))}
        lead.modify_trust(ACCOUNT_TRUST)
        for m in others:
            record(world, m.name, lead.name, "blame_taken", place)
        return {"success": True, "message": f"The Emperor takes the defeat at {_place(place)} on himself."}
    if choice == "on_the_lead":
        lead.modify_trust(-ACCOUNT_TRUST)
        sour_on(world, lead, others, place)
        return {"success": True, "message": f"The defeat at {_place(place)} is laid on {_shown(lead.name)}."}
    if choice == "on_another":
        named = world.marshals.get(str(context.get("named") or ""))
        if named is None:
            return {"success": False, "message": "There is no one else to name."}
        named.modify_trust(-ACCOUNT_TRUST)
        note(world, lead, named, "blame_laid", place, da=-1)
        return {"success": True, "message": f"The defeat at {_place(place)} is laid on {_shown(named.name)}."}
    sour_on(world, lead, others, place)
    return {"success": True, "message": f"The account of {_place(place)} is let lie."}


def _drop_account(world, context: Dict[str, Any]) -> None:
    store = _accounts(world)
    keep = [a for a in store if not (a.get("lead") == context.get("lead")
                                     and int(a.get("turn", -1)) == int(context.get("turn", -2))
                                     and a.get("place") == context.get("place"))]
    world.marshal_accounts = keep


def account_retirement_reason(world, context: Dict[str, Any]) -> str:
    lead = world.marshals.get(str(context.get("lead") or ""))
    if lead is None or int(getattr(lead, "strength", 0) or 0) <= 0:
        return "absent"
    if not _waiting(world, context):
        return "settled"          # BA6-R1: the card of a settled account retires
    return ""


def _push_accounts(world) -> None:
    """Offer the oldest waiting account when the channel is free; an account
    that waited ACCOUNT_SHOWS_FOR turns unseen is let lie."""
    store = _accounts(world)
    if not store:
        return
    turn = int(getattr(world, "current_turn", 0) or 0)
    from backend.game_logic import jealousy
    shown = _the_account_on_screen(world)
    for account in list(store):
        if shown is not None and _same_account(account, shown):
            continue      # BA6-R1: a card on screen waits for its answer, as every audience does
        if turn - int(account.get("turn", turn)) > ACCOUNT_SHOWS_FOR:
            apply_account(world, "let_it_lie", account)
    store = _accounts(world)
    pending = getattr(world, "pending_marshal_petition", None)
    if not store or pending is not None:
        return
    account = store[0]
    if account_retirement_reason(world, account):
        _drop_account(world, account)
        return
    jealousy._push_petition(world, _account_card(world, account))


# ═══════════════════════════════════════════════════════════════════════
# The claim (his deeds outrun his place)
# ═══════════════════════════════════════════════════════════════════════

def best_field(marshal) -> str:
    """The field he is best known for: the place of his largest laurel in the
    window, the latest among equals. (His card's own record of battles is
    read by no rule of the game — BA-5's promise — so a title is named from
    the laurels, which carry their field since row MC.)"""
    best = None
    for ev in getattr(marshal, "glory_events", []) or []:
        if isinstance(ev, dict) and ev.get("place") and int(ev.get("points", 0) or 0) > 0:
            if best is None or int(ev["points"]) >= int(best["points"]):
                best = ev
    return str(best.get("place") or "") if best else ""


def _claim_card(world, marshal) -> Dict[str, Any]:
    place, of = place_in_the_order(world, marshal)
    field = best_field(marshal)
    name = title_name(1, field)
    price, refusal = _priced(world, marshal.nation, DUKE_PRICE)
    can_pay = not refusal
    above = [m for m in order_of_precedence(world, marshal.nation)[:max(0, place - 1)]
             if renown_of(m) < renown_of(marshal)]
    senior = above[0] if above else None
    return {
        "kind": "claim",
        "title": f"{_shown(marshal.name)} asks for his due",
        "body": (f"Sire, {_shown(marshal.name)} asks the Emperor to remember his victories: his "
                 f"renown stands {renown_place(world, marshal)}th of the marshals, his place in "
                 f"the order {place}th of {of}."),
        "speaker": marshal.name,
        "speaker_line": f"{_shown(marshal.name)}: \"I ask only what the field has already given me, Sire.\"",
        "options": [
            {"id": "grant", "label": f"Create him {name}",
             "detail": (f"{price} authority; his trust +{TITLE_TRUST}; the seniors he passes "
                        f"hold it against him."),
             "cost_note": f"{price} authority", "enabled": can_pay,
             **({} if can_pay else {"why": refusal})},
            {"id": "not_yet", "label": "Not yet",
             "detail": f"Free. His trust -{CLAIM_REFUSED_TRUST}; he will not ask again for {CLAIM_COOLDOWN} turns.",
             "cost_note": "", "enabled": True},
            {"id": "rebuke", "label": "Rebuke his presumption",
             "detail": (f"His trust -{CLAIM_REBUKED_TRUST}"
                        + (f"; he holds it against {_shown(senior.name)}, who stands above him "
                           f"with less renown." if senior else ".")),
             "cost_note": "", "enabled": True},
        ],
        "context": {"marshal": marshal.name, "field": field, "senior": senior.name if senior else ""},
        "tier": "audience",
        "turn": int(getattr(world, "current_turn", 0) or 0),
    }


def apply_claim(world, choice: str, context: Dict[str, Any]) -> Dict[str, Any]:
    marshal = world.marshals.get(str(context.get("marshal") or ""))
    if marshal is None:
        return {"success": True, "message": "The claim is closed."}
    turn = int(getattr(world, "current_turn", 0) or 0)
    marshal.last_claim_turn = turn
    if choice == "grant":
        field = str(context.get("field") or "")
        marshal.title_due = {"tier": 1, "name": title_name(1, field), "place": field,
                             "turn": turn, "expires": turn + TITLE_DUE_TURNS}
        result = _confer_title_on(world, marshal.name)      # the court's own grant
        if not result.get("success"):
            marshal.title_due = None
        return result
    if choice == "rebuke":
        marshal.modify_trust(-CLAIM_REBUKED_TRUST)
        senior = world.marshals.get(str(context.get("senior") or ""))
        if senior is not None:
            note(world, marshal, senior, "claim_rebuked", "", da=-1, floor_a=-2)
        return {"success": True, "message": f"{_shown(marshal.name)}'s claim is rebuked."}
    marshal.modify_trust(-CLAIM_REFUSED_TRUST)
    return {"success": True, "message": f"{_shown(marshal.name)} is told: not yet."}


def claim_retirement_reason(world, context: Dict[str, Any]) -> str:
    marshal = world.marshals.get(str(context.get("marshal") or ""))
    if marshal is None or int(getattr(marshal, "strength", 0) or 0) <= 0:
        return "absent"
    if tier_of(marshal) > 0:
        return "provided"
    return ""


def _check_claims(world) -> None:
    if not (a_marshal_claims_his_due() and the_order_of_precedence_stands()):
        return
    if getattr(world, "pending_marshal_petition", None) is not None:
        return
    player = getattr(world, "player_nation", "")
    turn = int(getattr(world, "current_turn", 0) or 0)
    for m in order_of_precedence(world, player):
        if getattr(m, "captured_by", "") or int(getattr(m, "strength", 0) or 0) <= 0:
            continue
        last = int(getattr(m, "last_claim_turn", 0) or 0)
        if last and turn - last < CLAIM_COOLDOWN:
            continue
        if title_in_the_gift(world, m) is not None or not trails_his_deeds(world, m):
            continue
        m.last_claim_turn = turn
        from backend.game_logic import jealousy
        jealousy._push_petition(world, _claim_card(world, m))
        return


# ═══════════════════════════════════════════════════════════════════════
# The turn
# ═══════════════════════════════════════════════════════════════════════

def process_turn(world) -> None:
    """Once a turn (the jealousy pass's tail): old quarrels cool, lapsed
    titles leave the gift, the courts confer theirs, a waiting account is
    offered, a claim may be heard."""
    try:
        from backend.game_logic import jealousy
        if jealousy.glory_dormant(world):
            return
        _cool(world)
        _lapse_titles(world)
        _courts_confer(world)
        _push_accounts(world)
        _check_claims(world)
    except Exception as exc:
        report(exc, "precedence.process_turn")


def _cool(world) -> None:
    if not (old_quarrels_cool() and the_book_keeps_its_incidents()):
        return
    turn = int(getattr(world, "current_turn", 0) or 0)
    for key in sorted(book(world)):
        names = key.split("|")
        if len(names) != 2:
            continue
        a, b = world.marshals.get(names[0]), world.marshals.get(names[1])
        if a is None or b is None:
            continue
        for x, y in ((a, b), (b, a)):
            if int(x.relationships.get(y.name, 0) or 0) != -1:
                continue
            if getattr(x, "jealous_of", None) == y.name:
                continue
            try:
                from backend.game_logic.jealousy import get_escalation_level
                if get_escalation_level(x, y.name) >= 2:
                    continue
            except Exception as exc:
                report(exc, "precedence._cool: escalation")
            found = incidents(world, x.name, y.name)
            first, _ = sorted((x.name, y.name))
            mine = "a_to_b" if x.name == first else "b_to_a"
            moved = [i for i in found if int(i.get(mine, 0) or 0) < 0]
            if not moved:
                continue                 # an authored rivalry is character: it does not fade
            last = max([int(i.get("turn", 0) or 0) for i in found] or [0])
            if turn - last < THAW_TURNS:
                continue
            note(world, x, y, "thaw", "", da=+1, cap_a=0)


def _lapse_titles(world) -> None:
    turn = int(getattr(world, "current_turn", 0) or 0)
    for m in world.marshals.values():
        due = getattr(m, "title_due", None)
        if isinstance(due, dict) and int(due.get("expires", -1)) < turn:
            m.title_due = None


def _courts_confer(world) -> None:
    if not (ai_courts_confer_titles() and titles_of_victory()):
        return
    player = getattr(world, "player_nation", None)
    for m in sorted(world.marshals.values(), key=lambda x: str(x.name)):
        if m.nation == player or title_in_the_gift(world, m) is None:
            continue
        from backend.game_logic import standing
        due = dict(m.title_due)
        base = price_of(int(due.get("tier", 1) or 1))
        if _priced(world, m.nation, base)[1]:
            continue
        passed = _would_pass_over(world, m, int(due.get("tier", 1) or 1))
        paid = standing.buy(world, m.nation, base, "title_conferred", party=m.name,
                            marshal=_shown(m.name), title=str(due.get("name") or ""))
        if paid.get("refusal"):
            continue
        _confer(world, m, due, passed)


# ═══════════════════════════════════════════════════════════════════════
# The opening and the commission: the seeds of the book
# ═══════════════════════════════════════════════════════════════════════

def seed_the_book(world, scenario: Dict[str, Any]) -> None:
    """At a scenario's opening (`WorldState.from_scenario`): the authored seats
    (`seniority`: {nation: {name: seat}}, the list's own numbers), the 1805
    reading of three enmities, and a founding incident for every authored pair
    with its authored cause (`relationship_causes`: {"A->B": cause}); a cause
    between a marshal and a man still in the pool waits in the book for his
    commission."""
    try:
        scenario = scenario if isinstance(scenario, dict) else {}
        if the_order_of_precedence_stands():
            for _nation, seats in sorted((scenario.get("seniority") or {}).items()):
                # {name: seat} as authored (the 1804 list's own numbers), or a
                # list of names in order (seats 1..n)
                pairs = (seats.items() if isinstance(seats, dict)
                         else ((name, i) for i, name in enumerate(seats or [], 1)))
                for name, seat in pairs:
                    m = world.marshals.get(name)
                    if m is not None and isinstance(seat, int) and seat > 0:
                        m.seniority = int(seat)
        _read_as_of_1805(world)
        if not the_book_keeps_its_incidents():
            return
        causes = scenario.get("relationship_causes") or {}
        for name, data in sorted((scenario.get("marshals") or {}).items()):
            if name not in world.marshals or not isinstance(data, dict):
                continue
            for other, value in sorted((data.get("relationships") or {}).items()):
                if other not in world.marshals or not int(value):
                    continue
                _seed(world, name, other, str(causes.get(f"{name}->{other}") or ""))
        for pair, cause in sorted(causes.items()):
            a, _, b = str(pair).partition("->")
            if a and b and (a not in world.marshals or b not in world.marshals):
                row = entry(world, a, b)
                row.setdefault("waiting", {})[f"{a}->{b}"] = str(cause)
    except Exception as exc:
        report(exc, "precedence.seed_the_book")


def _read_as_of_1805(world) -> None:
    for a, b, as_of_1805, before in SEEDS_AS_OF_1805:
        x, y = world.marshals.get(a), world.marshals.get(b)
        if x is None or y is None:
            continue
        value = as_of_1805 if the_seeds_read_as_of_1805() else before
        for p, q in ((x, y), (y, x)):
            if int(p.relationships.get(q.name, 0) or 0) in (as_of_1805, before):
                p.set_relationship(q.name, value)


def _seed(world, a: str, b: str, cause: str) -> None:
    """The founding incident of an authored pair, the cause of A's view of B
    kept on A's side of it (the reverse may carry its own)."""
    first, _second = sorted((a, b))
    side = "note_a" if a == first else "note_b"
    for inc in incidents(world, a, b):
        if inc.get("kind") == "seed":
            if cause and not inc.get(side):
                inc[side] = cause
            return
    made = record(world, a, b, "seed", "", turn=0)
    if made is not None:
        made[side] = cause or "an old history between them"


def seed_the_commissioned(world, marshal, candidate: Dict[str, Any], applied: Dict[str, int]) -> None:
    """A commissioned marshal: his seat after every baton already given (a
    later creation is junior by the date of his baton), and his history with
    the men he joins (the cause the scenario left waiting in the book)."""
    try:
        if the_order_of_precedence_stands():
            seats = [seat_of(world, m) for m in world.marshals.values()
                     if m.nation == marshal.nation and m.name != marshal.name
                     and int(getattr(m, "seniority", 0) or 0) > 0]
            marshal.seniority = max(seats + [0]) + 1
        if not the_book_keeps_its_incidents():
            return
        for other in sorted(applied):
            row = book(world).get(_key(marshal.name, other)) or {}
            waiting = row.get("waiting") or {}
            made = record(world, marshal.name, other, "commissioned", "")
            if made is not None:
                first, _ = sorted((marshal.name, other))
                mine = waiting.get(f"{marshal.name}->{other}")
                theirs = waiting.get(f"{other}->{marshal.name}")
                fallback = mine or theirs or "he arrives with a history"
                made["note_a" if marshal.name == first else "note_b"] = str(mine or fallback)
                made["note_b" if marshal.name == first else "note_a"] = str(theirs or fallback)
    except Exception as exc:
        report(exc, "precedence.seed_the_commissioned")


# ═══════════════════════════════════════════════════════════════════════
# What the screens read
# ═══════════════════════════════════════════════════════════════════════

def bonds_of(world, marshal) -> List[Dict[str, Any]]:
    """His bonds and quarrels with the men of his court: both directions,
    the cause, what it means in the field. Professional pairs with no
    incident are left out."""
    out = []
    for other in court(world, marshal.nation) + [
            m for m in world.marshals.values()
            if m.nation == marshal.nation and getattr(m, "is_sovereign", False)]:
        if other.name == marshal.name:
            continue
        view = int(marshal.relationships.get(other.name, 0) or 0)
        felt = int(other.relationships.get(marshal.name, 0) or 0)
        temporary = getattr(marshal, "jealous_of", None) == other.name and view > -2
        cause = cause_of(world, marshal.name, other.name)
        if temporary and an_audience_names_its_cause():
            from backend.game_logic.jealousy import _laurels_place
            where, when = _laurels_place(other)
            if where:
                cause = f"he envies {_shown(other.name)}'s laurels at {_place(where)} (turn {when})"
        if not view and not felt and not temporary and not cause:
            continue
        shown_view = view - 1 if temporary else view
        out.append({
            "other": other.name, "shown": _shown(other.name),
            "view": shown_view, "view_label": LABELS[max(-2, shown_view)],
            "stored": view, "felt": felt, "felt_label": LABELS[felt],
            "temporary": bool(temporary),
            "cause": cause,
            "consequence": "" if getattr(other, "is_sovereign", False) else CONSEQUENCE[max(-2, shown_view)],
            "sovereign": bool(getattr(other, "is_sovereign", False)),
        })
    out.sort(key=lambda r: (-abs(int(r["view"])), r["shown"]))
    return out


def card_fields(world, marshal) -> Dict[str, Any]:
    """The marshal card's block: his place, title, renown, the title in the
    gift and its price, and his bonds."""
    if not in_the_court(marshal):
        return {}
    place, of = place_in_the_order(world, marshal)
    due = title_in_the_gift(world, marshal)
    out = {
        "place": place, "of": of,
        "seat": seat_of(world, marshal) if the_order_of_precedence_stands() else 0,
        "tier": tier_of(marshal), "style": style_of(marshal),
        "honours": [dict(h) for h in (getattr(marshal, "honours", []) or []) if isinstance(h, dict)],
        "renown": renown_of(marshal) if a_marshal_banks_his_renown() else 0,
        "renown_place": renown_place(world, marshal) if a_marshal_banks_his_renown() else 0,
        "captive": bool(getattr(marshal, "captured_by", "")),
        "trails_deeds": trails_his_deeds(world, marshal),
        "bonds": bonds_of(world, marshal) if the_book_keeps_its_incidents() else [],
    }
    if due is not None and marshal.nation == getattr(world, "player_nation", None):
        q = confer_quote(world, marshal)
        out["title_due"] = {
            "name": str(due.get("name") or ""), "place": _place(str(due.get("place") or "")),
            "turns_left": max(0, int(due.get("expires", 0)) - int(getattr(world, "current_turn", 0) or 0)),
            "price": int(q.get("price", 0) or 0), "ok": bool(q.get("ok")),
            "refusal": str(q.get("refusal") or ""), "line": str(q.get("line") or ""),
            "passed_over": [_shown(n) for n in q.get("passed_over", [])],
        }
    return out


def live_pairs(world, nation: str, cap: int = 3) -> List[Dict[str, Any]]:
    """The court's most telling pairs — at most `cap`: the open quarrels and
    the strongest bonds, the freshest incident first among equals."""
    if not the_book_keeps_its_incidents():
        return []
    members = court(world, nation)
    turn = int(getattr(world, "current_turn", 0) or 0)
    seen, rows = set(), []
    for a in members:
        for b in members:
            if a.name >= b.name or (a.name, b.name) in seen:
                continue
            seen.add((a.name, b.name))
            av, bv = int(a.relationships.get(b.name, 0) or 0), int(b.relationships.get(a.name, 0) or 0)
            found = incidents(world, a.name, b.name)
            last = max([int(i.get("turn", 0) or 0) for i in found] or [-99])
            tension = abs(min(av, bv)) * 3 if min(av, bv) < 0 else 0
            warmth = 2 if min(av, bv) >= 2 else (1 if min(av, bv) >= 1 else 0)
            fresh = 2 if turn - last <= 4 else 0
            score = tension + warmth + fresh
            if score <= 0:
                continue
            worse = a if av <= bv else b
            other = b if worse is a else a
            rows.append({"a": a.name, "b": b.name, "a_shown": _shown(a.name), "b_shown": _shown(b.name),
                         "a_view": av, "b_view": bv,
                         "label": (LABELS[av] if av == bv else f"{LABELS[av]} / {LABELS[bv]}"),
                         "cause": cause_of(world, worse.name, other.name),
                         "consequence": CONSEQUENCE[min(av, bv)],
                         "score": score, "last": last})
    rows.sort(key=lambda r: (-r["score"], -r["last"], r["a"], r["b"]))
    return rows[:cap]


def order_payload(world, nation: str) -> Dict[str, Any]:
    """The Generals screen's head: the court in its order (and by renown, and
    by the season's laurels), and the live pairs."""
    if not the_order_of_precedence_stands():
        return {}
    from backend.game_logic import jealousy
    rows = []
    for i, m in enumerate(order_of_precedence(world, nation), 1):
        rows.append({
            "name": m.name, "shown": _shown(m.name), "place": i,
            "seat": seat_of(world, m), "tier": tier_of(m), "style": style_of(m),
            "renown": renown_of(m) if a_marshal_banks_his_renown() else 0,
            "renown_place": renown_place(world, m) if a_marshal_banks_his_renown() else 0,
            "glory": int(jealousy.get_glory_score(m, int(getattr(world, "current_turn", 0) or 0))),
            "crowned": bool(getattr(m, "glory_crowned", False)),
            "envious_of": _shown(getattr(m, "jealous_of", "") or "") if getattr(m, "jealous_of", None) else "",
            "captive": bool(getattr(m, "captured_by", "")),
            "trails_deeds": trails_his_deeds(world, m),
            "title_due": bool(title_in_the_gift(world, m)) and nation == getattr(world, "player_nation", None),
        })
    return {"rows": rows, "pairs": live_pairs(world, nation)}
