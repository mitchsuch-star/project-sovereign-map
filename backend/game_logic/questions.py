"""The Questions of Europe — DY-2 and DY-3 (Tier 5; `docs/DYNAMISM_SPEC.md`
§4, the Tier-5 gate record §4a ruled November 10, 2026 in Plan Mode;
session B of §2b).

Deliberately not EU4's rivals: no symmetric picker, no declared pair. A
QUESTION is a named object — provinces in dispute — with CLAIMANT courts
seated at it (the German, the Italian, the Eastern, the Polish — the
diplomats' own vocabulary). Four pieces, one module:

* THE BLOCK — the scenario's `questions` key (validated by
  `modding.validator._validate_questions`: every province drawn, at least
  two seated claimants, a seat-less table WARNS — the T2-6 lesson).
* THE LATCH — at the ONE capture chokepoint (`WorldState.capture_region`,
  mirrored at the reckless auto-charge, the one conquest outside it): a
  Question province taken by a claimant's house latches
  `{question: {nation, turn}}`. Nowhere else writes it. Durable: it lives
  inside the moments store (`world.moments["questions"]` — the affairs
  precedent, RE-1; `WorldState.to_dict` carries no new field).
* THE ENVY TERM — one deterministic addend in `intent._derive_weight`: a
  claimant's gain quickens the OTHER claimants' designs at that table
  inside the window (N-DY2: `ENVY_WINDOW` 8, `WEIGHT_QUESTION_ENVY` +15).
  A court not seated feels nothing. O(questions); zero dice.
* THE BEAT — when a latch write makes its gainer the strict plurality
  holder among the claimant houses where it was not before THIS capture,
  "the Question turns": one `question_turns` log row (DY-0's column reads
  `question`) and a HIGH dispatch line in the Question's own authored
  voice.
* THE WORDS — the Balance of Europe tab's Questions panel, sentences and
  never a bar (`question_lines`); the Alarm's guarantee rung's Question
  arm (`share_a_table` — a court seated with the victim may guarantee it,
  not only a neighbour).
* DY-3 — THE CONGRESS RULES A QUESTION: while the Congress sits, each open
  Question's present plurality holder is recognized — the latch clears
  (envy relief), the unseated claimants take a relation write (grievance,
  N-DY3 `QUESTION_RULING_GRIEVANCE` −10), one `congress` chronicle row
  (phase `ruling`, no new log type). Prague by machinery, not script.

Two seams, each zero-arg, in this module (`tests/_t3_seams.py` rows T5-Q
and T5-C): `the_questions_of_europe` (the latch, the envy, the beat, the
words, the rung's arm — down: no Question is read anywhere) and
`the_congress_rules_a_question` (DY-3 — down: a sitting Congress rules
nothing). Rule 8: no reader walks the map — a Question's provinces (at most
a handful) are the only regions touched.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

ENVY_WINDOW = 8                      # N-DY2: turns a claimant's gain quickens the table
WEIGHT_QUESTION_ENVY = 15            # N-DY2: the addend on a seated rival's design
QUESTION_RULING_GRIEVANCE = -10      # N-DY3: an unseated claimant's relation to the recognized holder
QUESTION_ID = re.compile(r"^[a-z_]{1,32}$")
TITLE_MAX = 40
VOICE_MAX = 80
WATCHERS_MAX = 3                     # the courts a sentence names as watching
STORE_KEY = "questions"              # inside `world.moments` (the affairs precedent)


# ═══════════════════════════════════════════════════════════════════════
# The seams
# ═══════════════════════════════════════════════════════════════════════

def the_questions_of_europe() -> bool:
    """T5-Q seam (DY-2): the Questions are read — the latch writes at the
    chokepoint, the envy term quickens, the beat fires, the panel speaks,
    the rung's Question arm opens. Down: the pre-Tier-5 world — no
    Question is read anywhere (the block still loads and saves)."""
    return True


def the_congress_rules_a_question() -> bool:
    """T5-C seam (DY-3): a sitting Congress recognizes each open Question's
    present holder. Down: a sitting Congress rules nothing."""
    return True


# ═══════════════════════════════════════════════════════════════════════
# The store — inside `world.moments` (RE-1's affairs precedent)
# ═══════════════════════════════════════════════════════════════════════

def _entry(raw: Any) -> Optional[Dict[str, Any]]:
    """One authored Question, coerced to its serialized shape; None when it
    is not one (the validator refuses the file — this is the reader's own
    tolerance, never a second validator)."""
    if not isinstance(raw, dict):
        return None
    qid = str(raw.get("id") or "")
    provinces = [str(p) for p in (raw.get("provinces") or []) if p]
    claimants = [str(c) for c in (raw.get("claimants") or []) if c]
    if not qid or not provinces or not claimants:
        return None
    return {
        "id": qid,
        "title": str(raw.get("title") or qid.replace("_", " ").title()),
        "voice": str(raw.get("voice") or ""),
        "provinces": provinces,
        "claimants": claimants,
    }


def clean_block(raw: Any) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    seen = set()
    for item in (raw if isinstance(raw, list) else []):
        entry = _entry(item)
        if entry is None or entry["id"] in seen:
            continue
        seen.add(entry["id"])
        out.append(entry)
    return out


def _clean_marks(raw: Any) -> Dict[str, Dict[str, Any]]:
    """A `{question: {nation|holder: str, turn: int}}` map, ints and short
    strings only."""
    out: Dict[str, Dict[str, Any]] = {}
    for key, value in (raw.items() if isinstance(raw, dict) else []):
        if not isinstance(value, dict):
            continue
        rec: Dict[str, Any] = {}
        for k, v in value.items():
            if isinstance(v, bool):
                continue
            if isinstance(v, int):
                rec[str(k)] = int(v)
            elif isinstance(v, str):
                rec[str(k)] = v[:64]
        if rec:
            out[str(key)] = rec
    return out


def clean_store(raw: Any) -> Dict[str, Any]:
    """The serialized store, coerced: `block`, `latch`, `turned`, `ruled`."""
    if not isinstance(raw, dict):
        return {}
    block = clean_block(raw.get("block"))
    if not block:
        return {}
    turned = {str(k): str(v)[:64] for k, v in (raw.get("turned") or {}).items()
              if isinstance(v, str)} if isinstance(raw.get("turned"), dict) else {}
    return {
        "block": block,
        "latch": _clean_marks(raw.get("latch")),
        "turned": turned,
        "ruled": _clean_marks(raw.get("ruled")),
    }


def install(world, data: Dict[str, Any]) -> None:
    """`WorldState.from_dict`, beside the moments line: a scenario's
    top-level `questions` key is the authored block; a save's
    `moments.questions` is the store (carried whole). Writes NOTHING on a
    world that authors none — the bare flag world, the tutorials and the
    legacy rollback keep `moments` byte-identical."""
    data = data or {}
    moments = data.get("moments")
    saved = moments.get(STORE_KEY) if isinstance(moments, dict) else None
    store = clean_store(saved)
    if not store:
        block = clean_block(data.get(STORE_KEY))
        if not block:
            return
        store = {"block": block, "latch": {}, "turned": {}, "ruled": {}}
    _moments(world)[STORE_KEY] = store


def backfill(world, scenario_data: Dict[str, Any]) -> bool:
    """A pre-Tier-5 save of a scenario that NOW authors Questions gains the
    block on load (the `_backfill_moments` idiom), its latch empty; a save
    carrying a store is never overwritten."""
    if armed(world):
        return False
    block = clean_block((scenario_data or {}).get(STORE_KEY))
    if not block:
        return False
    _moments(world)[STORE_KEY] = {"block": block, "latch": {}, "turned": {}, "ruled": {}}
    return True


def _moments(world) -> Dict[str, Any]:
    store = getattr(world, "moments", None)
    if not isinstance(store, dict):
        store = {}
        world.moments = store
    return store


def store(world) -> Dict[str, Any]:
    """The store, read-only ({} when the scenario authors none)."""
    value = (getattr(world, "moments", None) or {})
    value = value.get(STORE_KEY) if isinstance(value, dict) else None
    return value if isinstance(value, dict) else {}


def armed(world) -> bool:
    return bool(store(world).get("block"))


def block(world) -> List[Dict[str, Any]]:
    return [q for q in (store(world).get("block") or []) if isinstance(q, dict)]


def latch(world) -> Dict[str, Dict[str, Any]]:
    return dict(store(world).get("latch") or {})


def ruled(world) -> Dict[str, Dict[str, Any]]:
    return dict(store(world).get("ruled") or {})


def question(world, qid: str) -> Optional[Dict[str, Any]]:
    for q in block(world):
        if q.get("id") == qid:
            return q
    return None


def question_of(world, region_name: str) -> Optional[Dict[str, Any]]:
    """The table a province is on, or None (a province sits at one table —
    the validator refuses two)."""
    for q in block(world):
        if region_name in (q.get("provinces") or []):
            return q
    return None


# ═══════════════════════════════════════════════════════════════════════
# The reads — houses, seats, the plurality holder
# ═══════════════════════════════════════════════════════════════════════

def _turn(world) -> int:
    return int(getattr(world, "current_turn", 0) or 0)


def _player(world) -> str:
    return str(getattr(world, "player_nation", "") or "")


def house(world, nation: str) -> str:
    """The court a Question credits: `nation`'s top overlord (a client's
    conquest is its lord's — the Alarm's own read)."""
    if not nation:
        return ""
    return str(world._top_overlord(nation) or nation)


def claimants(world, q: Dict[str, Any]) -> List[str]:
    """The claimants still standing, in authored order."""
    active = set(world.get_active_nations())
    return [c for c in (q.get("claimants") or []) if c in active]


def seated(world, nation: str, q: Dict[str, Any]) -> bool:
    return house(world, nation) in (q.get("claimants") or [])


def share_a_table(world, a: str, b: str) -> bool:
    """§3c G2's Question arm: are `a` and `b` (their houses) both seated at
    one Question?"""
    if not the_questions_of_europe() or not armed(world):
        return False
    ha, hb = house(world, a), house(world, b)
    if not ha or not hb or ha == hb:
        return False
    return any(ha in (q.get("claimants") or []) and hb in (q.get("claimants") or [])
               for q in block(world))


def holdings(world, q: Dict[str, Any],
             override: Optional[Dict[str, str]] = None) -> Dict[str, int]:
    """{claimant house: provinces of the Question it holds} — only the
    Question's own provinces are touched (Rule 8). `override` reads a
    province as another court's (the board BEFORE a capture)."""
    regions = getattr(world, "regions", {}) or {}
    seats = set(q.get("claimants") or [])
    counts: Dict[str, int] = {}
    for name in q.get("provinces") or []:
        holder = (override or {}).get(name)
        if holder is None:
            region = regions.get(name)
            holder = str(getattr(region, "controller", "") or "") if region is not None else ""
        court = house(world, holder) if holder else ""
        if court and court in seats:
            counts[court] = counts.get(court, 0) + 1
    return counts


def plurality_holder(world, q: Dict[str, Any],
                     override: Optional[Dict[str, str]] = None) -> str:
    """The claimant house holding strictly the most of the Question's
    provinces; '' on a tie or when no claimant holds any."""
    counts = holdings(world, q, override)
    if not counts:
        return ""
    best = max(counts.values())
    leaders = [court for court, n in counts.items() if n == best]
    return leaders[0] if len(leaders) == 1 else ""


def held_by(world, q: Dict[str, Any], court: str) -> List[str]:
    regions = getattr(world, "regions", {}) or {}
    out: List[str] = []
    for name in q.get("provinces") or []:
        region = regions.get(name)
        holder = str(getattr(region, "controller", "") or "") if region is not None else ""
        if holder and house(world, holder) == court:
            out.append(str(name))
    return out


# ═══════════════════════════════════════════════════════════════════════
# The latch and the beat — at the capture chokepoint
# ═══════════════════════════════════════════════════════════════════════

def note_capture(world, region_name: str, holder: str,
                 old_controller: str) -> Optional[Dict[str, Any]]:
    """THE latch writer — called from `WorldState.capture_region` beside
    the Alarm's write and from the reckless auto-charge's mirror, after the
    controller moved. `holder` is the court that NOW holds the province (a
    liberation hands the ground to its home court, not the liberator).
    Latches when the province is a Question's and the holder's house is
    seated; then the beat, when the write made that house the strict
    plurality holder where it was not before this capture. Returns the
    beat's event, or None."""
    if not the_questions_of_europe() or not armed(world):
        return None
    q = question_of(world, str(region_name))
    if q is None:
        return None
    gainer = house(world, holder)
    if not gainer or gainer not in (q.get("claimants") or []):
        return None
    if old_controller and house(world, old_controller) == gainer:
        return None
    st = _moments(world)[STORE_KEY]
    st.setdefault("latch", {})[q["id"]] = {"nation": gainer, "turn": _turn(world)}
    # The turn's intent cache is NOT flushed here: intent is turn-granular
    # by design (`intent.py`'s staleness contract — a mid-turn delta does
    # not recompute it), and the envy reads from the next derivation.
    before = plurality_holder(world, q, override={str(region_name): str(old_controller or "")})
    now = plurality_holder(world, q)
    if not now or now != gainer or now == before:
        return None
    st.setdefault("turned", {})[q["id"]] = now
    return _the_question_turns(world, q, now)


def _the_question_turns(world, q: Dict[str, Any], holder: str) -> Dict[str, Any]:
    """ONE `question_turns` log row (DY-0's column reads `question`) and one
    beat — exempt from the narration cap, as every beat is — in the
    Question's own voice: "THE GERMAN QUESTION TURNS: Prussia holds
    Hanover; Vienna watches. Who speaks for Germany?"."""
    from backend.game_logic.dispatch import queue_dispatch_event
    held = held_by(world, q, holder)
    line = turn_line(world, q, holder, held)
    # ONE literal `log_event` (the Gazette's collector census reads the
    # literal — a row assembled elsewhere is "dead by construction").
    world.log_event({
        "type": "question_turns",
        "question": str(q["id"]),
        "title": str(q.get("title") or ""),
        "nation": holder,
        "holds": list(held),
        "message": line,
    })
    queue_dispatch_event(world, "question_turns", {
        "nation": holder, "question": str(q["id"]), "line": line,
    }, "always")
    return {"type": "question_turns", "question": str(q["id"]), "nation": holder,
            "holds": list(held), "message": line}


# ═══════════════════════════════════════════════════════════════════════
# The envy term — `intent._derive_weight`
# ═══════════════════════════════════════════════════════════════════════

def envy_weight(world, nation: str, agenda, weight: Optional[int] = None,
                against: Optional[str] = None) -> int:
    """+`WEIGHT_QUESTION_ENVY` when `nation`'s house is seated at a Question
    whose provinces the design (`agenda.regions`) touches and the latch
    names ANOTHER house inside `ENVY_WINDOW`; 0 otherwise — a court not
    seated feels nothing, a court's own gain quickens nobody. Once, not
    per table.

    THE LADDER IS HONOURED (the session's own catch, November 10, 2026,
    found on the sweep's first run and the driven board's): a court climbs
    its ladder by ASKING — asks are made at the ask, buy, align and
    bandwagon rungs, and of an AI court nothing is asked at the ultimatum —
    and the council's patient-ask gate (`war_council._ladder_climbed`, two
    refused asks on record) opens its crisis; a court the envy carried
    straight to the ultimatum stopped asking, and one carried to `fight`
    never fought (the historical Prussia sat at `fight` ten turns and never
    fought Hanover; the driven austerlitz lost its Hanover crisis). So with
    the running `weight` given (the figure AFTER the seeded jitter — the
    cap reads what the ladder reads), the addend is capped in three
    stages: below the COERCE floor until the court's ladder against its
    object has climbed; below the FIGHT floor until its crisis stands
    (`world.war_intents`); the whole addend once it stands, or once the
    court is at war with its object — the envy hastens what the
    fore-warning already promised (beat 2: no cold-open wars)."""
    if not the_questions_of_europe() or not armed(world):
        return 0
    regions = set(str(r) for r in (getattr(agenda, "regions", None) or ()))
    if not regions:
        return 0
    court = house(world, nation)
    marks = latch(world)
    turn = _turn(world)
    for q in block(world):
        if court not in (q.get("claimants") or []):
            continue
        if not regions & set(q.get("provinces") or []):
            continue
        rec = marks.get(str(q.get("id")))
        if not rec or str(rec.get("nation") or "") == court:
            continue
        if 0 <= turn - int(rec.get("turn", 0) or 0) <= ENVY_WINDOW:
            return _below_the_floors(world, nation, against, int(WEIGHT_QUESTION_ENVY), weight)
    return 0


def _below_the_floors(world, nation: str, against: Optional[str], addend: int,
                      weight: Optional[int]) -> int:
    """The envy's addend, capped so `weight + addend` stays below the coerce
    floor while the court's ladder against `against` has not climbed, below
    the fight floor while no crisis of its stands; the whole addend once a
    crisis stands or it is at war with `against`, or when no running weight
    is given (a bare read of the term)."""
    if weight is None:
        return addend
    if against and world.is_at_war(nation, against):
        return addend
    crisis = (getattr(world, "war_intents", {}) or {}).get(nation)
    if isinstance(crisis, dict) and crisis.get("target"):
        return addend
    from backend.game_logic.intent import PRICE_THRESHOLDS
    floors = dict(PRICE_THRESHOLDS)
    climbed = False
    if against:
        from backend.game_logic.war_council import _ladder_climbed
        climbed = bool(_ladder_climbed(world, nation, against))
    ceiling = int(floors["fight"]) - 1 if climbed else int(floors["coerce"]) - 1
    return max(0, min(addend, ceiling - int(weight)))


# ═══════════════════════════════════════════════════════════════════════
# DY-3 — the Congress rules a Question
# ═══════════════════════════════════════════════════════════════════════

def congress_rules(world) -> List[Dict[str, Any]]:
    """While the Congress sits (the sitting's tick, after the signatures are
    taken): each Question with a live latch and no ruling this sitting is
    RULED — its present plurality holder recognized, the latch cleared
    (envy relief), every other standing claimant's relation to the holder
    written `QUESTION_RULING_GRIEVANCE` (the player's house takes no
    grievance — the Congress is his), one `congress` row (phase `ruling`)
    and one beat. A Question nobody holds is not ruled; a later capture
    re-latches it (the Question reopens). Returns the rows written."""
    if not the_congress_rules_a_question() or not the_questions_of_europe():
        return []
    if not armed(world):
        return []
    from backend.game_logic import congress as _congress
    if not _congress.sitting(world):
        return []
    record = _congress.record(world) or {}
    summoned = int(record.get("summoned_turn", _turn(world)) or 0)
    st = _moments(world)[STORE_KEY]
    marks = st.setdefault("latch", {})
    rulings = st.setdefault("ruled", {})
    player = _player(world)
    player_house = house(world, player) if player else ""
    out: List[Dict[str, Any]] = []
    for q in block(world):
        qid = str(q.get("id"))
        if qid not in marks:
            continue
        prior = rulings.get(qid) or {}
        if prior and int(prior.get("turn", -1) or -1) >= summoned:
            continue
        holder = plurality_holder(world, q)
        if not holder:
            continue
        marks.pop(qid, None)
        rulings[qid] = {"holder": holder, "turn": _turn(world)}
        aggrieved: List[str] = []
        from backend.game_logic.diplomatic_dialogue import modify_relation_booked
        for claimant in claimants(world, q):
            if claimant == holder or claimant == player_house:
                continue
            # the mission's books kept (S14E-X37): the write through the one
            # booked setter, its cause "question_ruling"
            modify_relation_booked(world, claimant, holder, int(QUESTION_RULING_GRIEVANCE),
                                   "question_ruling", claimant, holder)
            aggrieved.append(claimant)
        line = ruling_line(world, q, holder, aggrieved)
        row = {
            "type": "congress", "phase": "ruling", "nation": player,
            "question": qid, "court": holder, "aggrieved": list(aggrieved),
            "message": line,
        }
        world.log_event(dict(row))
        from backend.game_logic.dispatch import queue_dispatch_event
        queue_dispatch_event(world, "question_ruled", {
            "nation": holder, "question": qid, "line": line,
        }, "always")
        out.append(row)
    return out


# ═══════════════════════════════════════════════════════════════════════
# The words — R7 names throughout, never a figure
# ═══════════════════════════════════════════════════════════════════════

def _name(world, nation: str) -> str:
    """A court as a sentence's subject — "Prussia", "the Ottoman Empire"."""
    from backend.display_names import with_definite_article
    from backend.game_logic.formations import formed_display_name
    return with_definite_article(formed_display_name(world, nation))


def _seat(world, nation: str) -> str:
    """A great court by its seat ("Vienna"), as the Alarm names them."""
    from backend.game_logic.alarm import _seat as alarm_seat
    return alarm_seat(world, nation)


def _join(names: List[str]) -> str:
    names = [n for n in names if n]
    if len(names) <= 1:
        return "".join(names)
    return ", ".join(names[:-1]) + " and " + names[-1]


def watchers(world, q: Dict[str, Any], holder: str) -> List[str]:
    """The other standing claimants, the player's house never named (the
    reading is his own), at most `WATCHERS_MAX`, in authored order."""
    player_house = house(world, _player(world)) if _player(world) else ""
    out = [c for c in claimants(world, q) if c != holder and c != player_house]
    return out[:WATCHERS_MAX]


def _watch_clause(world, q: Dict[str, Any], holder: str) -> str:
    seats = [_seat(world, c) for c in watchers(world, q, holder)]
    if not seats:
        return ""
    verb = "watches" if len(seats) == 1 else "watch"
    return f"; {_join(seats)} {verb}"


def turn_line(world, q: Dict[str, Any], holder: str, held: List[str]) -> str:
    title = str(q.get("title") or "The Question")
    holds = f" holds {_join([str(r) for r in held])}" if held else " gains"
    voice = str(q.get("voice") or "").strip()
    tail = f" {voice}" if voice else ""
    return (f"{title.upper()} TURNS: {_name(world, holder)}{holds}"
            f"{_watch_clause(world, q, holder)}.{tail}")


def ruling_line(world, q: Dict[str, Any], holder: str, aggrieved: List[str]) -> str:
    title = str(q.get("title") or "The Question")
    grief = ""
    if aggrieved:
        seats = [_seat(world, c) for c in aggrieved[:WATCHERS_MAX]]
        verb = "takes" if len(seats) == 1 else "take"
        grief = f"; {_join(seats)} {verb} it ill"
    return (f"The Congress rules {title[0].lower() + title[1:] if title else 'the Question'}: "
            f"{_name(world, holder)} is recognized in what it holds{grief}.")


def question_line(world, q: Dict[str, Any]) -> str:
    """One sentence per Question for the Balance tab: open (who gains, who
    watches), ruled at the Congress, or quiet."""
    title = str(q.get("title") or "The Question")
    qid = str(q.get("id"))
    mark = latch(world).get(qid)
    verdict = ruled(world).get(qid)
    if mark:
        gainer = str(mark.get("nation") or "")
        return (f"{title}: open — {_name(world, gainer)} gains "
                f"(turn {int(mark.get('turn', 0) or 0)})"
                f"{_watch_clause(world, q, gainer)}.")
    if verdict:
        holder = str(verdict.get("holder") or "")
        return (f"{title}: ruled at the Congress (turn "
                f"{int(verdict.get('turn', 0) or 0)}) — {_name(world, holder)} recognized.")
    holder = plurality_holder(world, q)
    if holder:
        return f"{title}: quiet; {_name(world, holder)} holds the most of it."
    return f"{title}: quiet; no claimant holds it."


def question_lines(world) -> List[str]:
    """The Balance of Europe tab's Questions panel — [] where the scenario
    authors none (the payload is otherwise unchanged)."""
    if not the_questions_of_europe() or not armed(world):
        return []
    return [question_line(world, q) for q in block(world)]
