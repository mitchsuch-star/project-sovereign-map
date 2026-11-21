"""Row IC "Independent Command", the desk (November 19, 2026) — THE PEACE, THE WAR,
TO DECIDE.

The first playtest, in the player's words: "everything feels convoluted and opaque
and disconnected." The game already knew what he was trying to do (a Congress at
45 titled provinces), whom he was fighting and why, and what wanted his word this
turn — on five screens, one question at a time, and in a warning printed into the
log when he pressed End Turn. This module says it in ONE place:

    THE PEACE   the aim of the campaign, and how far along it is
    THE WAR     each war: who, and what it is being fought for
    TO DECIDE   the matters that want his word now — one plain sentence each
                (90 characters at most), each with ONE door to the right place

`desk(world)` is the whole payload — the `desk` key on every reply
(`main.build_base_response`) and at boot (`GET /test`). The client draws it at
the head of the command desk; the End Turn list reads the same rows; the typed
"what now?" answers from them (`question_desk._answer_options`).

THE ORDER OF TO DECIDE is fixed, written before any play (the design, §4):

  1. what bites when the turn ends — a last stand unanswered, a battle waiting,
     a letter that lapses, a treasury about to go below zero, a corps in peril,
     a province an enemy we can see can walk into, a man who may attack
     without orders tonight;
  2. what wastes the turn — a corps on ground it could take, an enemy within a
     march of corps with no orders, the corps with no orders, a man left idle
     too long;
  3. what could grow the empire — the Congress, a law, a marshal to commission.

PURE. Nothing here changes what a save holds, draws a random number or closes
Take back (`tests/test_ic1_the_desk.py` pins all three; the Designs' own
readers may fill a missing key of their state with its default, as the Designs
page does on its first read — a loaded save already holds them all). FOG (R5):
an enemy is read
only through `world.get_visible_enemies` / `intel_surfaces.sighting_row`.
Golden rule 2: ints and strings only. Golden rule 8: no scan of the regions —
the readers walk the player's own roster, the enemies in sight and their
neighbours. It rides every reply, so it is built from what the envelope
already holds (`have`: the wars, the treasury's forecast) and costs well under
a millisecond on the 1805 board.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from backend.display_names import humanize_entity_name
from backend.errors import report

ROW_CAP = 90          # one sentence, this many characters at most
ROWS_SHOWN = 3        # the desk shows this many; the rest stand behind "+n more"
MAX_ROWS = 12         # the list never carries more than this
WARS_SHOWN = 2        # THE WAR names this many wars, then "+N"
REACH_ROWS = 2        # enemies named as "within one march of corps with no orders"

TIER_BITES = 1        # what bites when the turn ends
TIER_WASTES = 2       # what wastes the turn
TIER_GROWS = 3        # what could grow the empire


def the_desk_is_shown() -> bool:
    """Row IC seam (one line to reverse). Down (False): no `desk` is built —
    the key rides as null, the client draws no desk lines, the End Turn list
    stays the log's warning, and "what now?" answers as it did."""
    return True


# ── small words ─────────────────────────────────────────────────────────────

def _player(world) -> str:
    return str(getattr(world, "player_nation", "") or "")


def _fit(forms: List[str], cap: int = ROW_CAP) -> str:
    """The fullest of `forms` that fits in `cap` characters (they are written
    fullest first); the last one cut at a word, as a last resort."""
    for text in forms:
        if len(text) <= cap:
            return text
    text = forms[-1]
    cut = text[:cap - 1].rsplit(" ", 1)[0].rstrip(" ,;:—-")
    return cut + "…"


def _names(shown: List[str], limit: int = 3) -> str:
    """"Ney", "Ney and Davout", "Ney, Davout and Lannes", "Ney, Davout and 3 more"."""
    shown = [s for s in shown if s]
    if not shown:
        return ""
    if len(shown) == 1:
        return shown[0]
    if len(shown) <= limit:
        return ", ".join(shown[:-1]) + " and " + shown[-1]
    return ", ".join(shown[:limit - 1]) + f" and {len(shown) - (limit - 1)} more"


def _plural(n: int, one: str, many: Optional[str] = None) -> str:
    return f"{int(n)} {one if int(n) == 1 else (many or one + 's')}"


def _row(row_id: str, tier: int, text: str, door: Dict[str, Any],
         more: str = "") -> Dict[str, Any]:
    """One TO DECIDE row. `more` is the full sentence where the row is a
    shortening of one the game already says (the tooltip, the End Turn list)."""
    out = {"id": str(row_id), "tier": int(tier), "text": _fit([text]), "door": dict(door)}
    if more and more != out["text"]:
        out["more"] = str(more)
    return out


def _own_field_corps(world) -> List[Any]:
    """Our corps standing in the field (a prisoner or an empty corps is not)."""
    player = _player(world)
    return [m for m in world.marshals.values()
            if m.nation == player and int(getattr(m, "strength", 0) or 0) > 0
            and not getattr(m, "captured_by", "") and getattr(m, "location", None)]


def is_idle(marshal, turn: Optional[int] = None) -> bool:
    """A corps with nothing to do — no standing order, no works, no drill, no
    square: the client's own reading (`main.gd::_idle_marshals`, the End Turn
    gate's idle line), said once here so the two cannot part.

    Row IC, Session 2 (IC-7): a man told to "stay put" on turn `turn` is not
    idle on that turn — the player has answered for him (the next turn he is
    again)."""
    if bool(getattr(marshal, "in_strategic_mode", False)) or getattr(marshal, "strategic_command_type", None):
        return False
    stayed = getattr(marshal, "stay_put_turn", None)
    if turn is not None and stayed is not None and int(stayed) == int(turn):
        return False
    return not (bool(getattr(marshal, "fortified", False)) or bool(getattr(marshal, "drilling", False))
                or bool(getattr(marshal, "drilling_locked", False))
                or bool(getattr(marshal, "square_formation", False)))


def _can_attack(world, marshal) -> bool:
    """The state probe's own answer: an attack by him would not be refused for
    his state or for the actions left (`state_probe.order_state_refusal`)."""
    from backend.commands.state_probe import order_state_refusal
    return not order_state_refusal(world, marshal, "attack")


def _sighting(world, foe) -> Optional[Dict[str, Any]]:
    from backend.game_logic import intel_surfaces
    return intel_surfaces.sighting_row(world, _player(world), foe)


def _force(row: Dict[str, Any]) -> str:
    """"52,000 men" at FULL, his band ("large force") at PARTIAL."""
    from backend.models.intel import FULL
    shown = str(row.get("strength_display") or "")
    return f"{shown} men" if row.get("visibility") == FULL else shown


def _shown_strength(row: Dict[str, Any]) -> int:
    """A figure to ORDER by that gives nothing away (exact at FULL, the band's
    midpoint at PARTIAL)."""
    from backend.models.intel import FULL
    if row.get("visibility") == FULL:
        return int(row.get("strength", 0) or 0)
    from backend.game_logic.dispatch import BAND_MIDPOINTS
    return int(BAND_MIDPOINTS.get(str(row.get("strength_display") or ""), 0))


def _titled(world, have: Dict[str, Any]) -> Dict[str, Any]:
    """`congress.titled`, read once a call (THE PEACE and the Congress row)."""
    if "titled" not in have:
        from backend.game_logic import congress
        have["titled"] = congress.titled(world)
    return have["titled"]


# ── THE PEACE ───────────────────────────────────────────────────────────────

def peace(world, have: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """The aim of the campaign in one line: {text, hint, door, tone}.

    A Fall clock takes the line while it runs (it is the more urgent truth);
    otherwise the Congress of Paris and how far the count stands, with the
    proclaimed road beside it. "" text off an armed world (the bare flag world
    and the lesson have no Congress)."""
    from backend.game_logic import congress, fall
    have = {} if have is None else have
    out = {"text": "", "hint": "", "door": {}, "tone": ""}
    clocks = fall.clock_lines(world)
    if clocks:
        out.update(text=str(clocks[0].get("clock_line") or ""), tone="bad",
                   hint=str((fall.warning_state(world) or {}).get("message") or ""),
                   door={"kind": "congress"})
        return out
    if not congress.armed(world):
        return out
    out["door"] = {"kind": "congress"}
    if congress.imperial_peace_signed(world):
        out.update(text="The Imperial Peace is signed — the campaign is won.", tone="good")
        return out
    record = congress.record(world) or {}
    if record.get("status") == congress.SITTING:
        out.update(text="The Congress of Paris sits — Europe is answering.", tone="good")
        return out
    view = _titled(world, have)
    held, need = int(view["count"]), int(view["needed"])
    if held >= need:
        head = f"Win the peace: you hold {held} titled provinces ({need} needed) — summon the Congress of Paris"
        out["tone"] = "good"
    else:
        # Lever L5 (the second blind reading — all three readers: "I cannot
        # tell what a 'titled province' is, or how to get the other ten"):
        # "titled" is the game's own word and stays (golden rule 11); the
        # plain words ride beside it, on the line itself — a frame cannot hover.
        turns = _title_turns(world)
        kept = f"conquests kept {_plural(turns, 'turn')}" if turns else "conquests kept long enough"
        head = (f"Win the peace: hold {need} titled provinces — your homeland, lands a treaty gave you, "
                f"and {kept} — then summon the Congress of Paris. You hold {held}")
    out["text"] = head + _road_clause(world) + "."
    out["hint"] = (f"A titled province is one held for good: your homeland, a province a treaty gave you, "
                   f"or a conquest {_title_clock_words(world)}. The Congress of Paris ends the campaign in "
                   f"your favour; it can be summoned once the Empire and its satellites hold {need} titled "
                   "provinces — the page lists every condition and which are met.")
    return out


def _title_turns(world) -> int:
    """How many turns a conquest stands in the bloc's hands before it is
    titled (`game_end.province_title_kind`'s own clock); 0 if it cannot be read."""
    try:
        from backend.game_logic import game_end
        return int(game_end.cfg(world, "title_turns", game_end.TITLE_TURNS_DEFAULT))
    except Exception as exc:
        report(exc, "today._title_turns: game_end.cfg")
        return 0


def _title_clock_words(world) -> str:
    """"you have held for 12 turns" — the conquest's own clock, for the hint."""
    turns = _title_turns(world)
    return f"you have held for {_plural(turns, 'turn')}" if turns else "you have held long enough"


def _road_clause(world) -> str:
    """" · the Protector of the Rhine: 0 of 3 courts…" for a proclaimed road
    of the Emperor's Designs (its first design not yet held); "" with none.
    Reads the chosen road's two designs only — never the whole page."""
    try:
        from backend.game_logic import imperial_designs
        chosen = imperial_designs.proclaimed_road(world)
        if not chosen:
            return ""
        row = imperial_designs.road(world, chosen) or {}
        title = str(row.get("title") or chosen)
        for design in imperial_designs.designs_of(row):
            reading = imperial_designs.design_reading(world, design)
            if not reading.get("met"):
                return f" · {title}: {imperial_designs.progress_line(world, reading)}"
        return f" · {title}: both designs held"
    except Exception as exc:
        report(exc, "today._road_clause: imperial_designs.design_reading")
        return ""


# ── THE WAR ─────────────────────────────────────────────────────────────────

def _purpose_words(war_row: Dict[str, Any]) -> str:
    """What a war is being fought for, in a few plain words."""
    objective = war_row.get("objective") if isinstance(war_row.get("objective"), dict) else {}
    kind = str(objective.get("type") or "")
    if not kind:
        return "no purpose named"
    if kind == "defense":
        return "to hold the homeland"
    shown = str(objective.get("type_display") or kind.replace("_", " ")).lower()
    summary = str(objective.get("target_summary") or "")
    return f"{shown} — {summary}" if summary else shown


def war(world, wars: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """The wars in one line: {text, hint, door, parts}. At peace: the most
    pressing want among the courts (diplomacy has no fog), or "At peace".

    `wars` is `war_status.build_active_wars(world)` when the caller already
    holds it (the envelope does), so the desk never builds it twice."""
    out: Dict[str, Any] = {"text": "", "hint": "", "door": {}, "parts": []}
    if wars is None:
        from backend.game_logic.war_status import build_active_wars
        wars = build_active_wars(world)
    every = [w for w in (wars or {}).get("wars") or [] if isinstance(w, dict)]
    rows = [w for w in every if w.get("status") == "war"]
    if not rows:
        if every:
            out["text"] = "No war is being fought — a truce holds with " + _names(
                [str(w.get("opponent_display") or w.get("opponent") or "") for w in every]) + "."
            out["door"] = {"kind": "war", "opponent": str(every[0].get("opponent") or "")}
            return out
        want = _pressing_want(world)
        if want:
            out["text"] = "At peace. " + want["text"]
            out["door"] = want["door"]
        else:
            out["text"] = "At peace."
        return out
    parts = []
    for w in rows[:WARS_SHOWN]:
        title = str(w.get("war_title") or "")
        who = str(w.get("war_roster_display") or w.get("opponent_display") or w.get("opponent") or "")
        name = f"{title} ({who})" if title and who and who not in title else (title or f"War with {who}")
        part = {"opponent": str(w.get("opponent") or ""), "text": f"{name}: {_purpose_words(w)}",
                "hint": str(w.get("objective_hint") or w.get("war_title_line") or "")}
        # Row IC, directives: the goal the player named for this war, said
        # after its purpose ("… — your war goal: Vienna"). A war with none reads as it
        # did, to the byte.
        goal = _goal_words(world, w)
        if goal:
            part["text"] += f" — {goal}"
            part["goal"] = goal
        parts.append(part)
    text = " · ".join(p["text"] for p in parts)
    if len(rows) > WARS_SHOWN:
        text += f" · +{len(rows) - WARS_SHOWN} more"
    out.update(text=text + ".", parts=parts,
               hint=" ".join(p["hint"] for p in parts if p["hint"]),
               door={"kind": "war", "opponent": parts[0]["opponent"]})
    return out


def _goal_words(world, war_row: Dict[str, Any]) -> str:
    """Row IC, directives: "your war goal: Vienna" for a war that has one, else ""
    (`war_goals.goal_of` — nothing is read on a board with no goal set)."""
    if not getattr(world, "war_goals", None):
        return ""
    from backend.game_logic import war_goals
    found = war_goals.goal_of(world, war_row)
    return war_goals.words(world, found[0], found[1]) if found else ""


def _pressing_want(world) -> Optional[Dict[str, Any]]:
    """At peace: the heaviest design among the courts of Europe, as the ledger
    already shows it ("Prussia wants the Hanoverian Prize")."""
    try:
        from backend.game_logic import intent
        from backend.game_logic.formations import formed_display_name
        player = _player(world)
        best = None
        for nation in world.get_active_nations():
            if nation == player:
                continue
            view = intent.get_nation_intent(nation, world)
            if view.want_id is None:
                continue
            rank = (-int(view.weight), nation)
            if best is None or rank < best[0]:
                best = (rank, nation, view)
        if best is None:
            return None
        _rank, nation, view = best
        court = formed_display_name(world, nation)
        against = formed_display_name(world, view.against) if view.against else ""
        tail = f", and {against} stands in the way" if against else ""
        return {"text": _fit([f"{court} wants {view.want_title}{tail}.",
                              f"{court} wants {view.want_title}."], 110),
                "door": {"kind": "court", "nation": nation}}
    except Exception as exc:
        report(exc, "today._pressing_want: intent.get_nation_intent")
        return None


# ── TO DECIDE: the readers, in the list's own order ─────────────────────────

def _rows_last_stand(world, have) -> List[Dict[str, Any]]:
    from backend.commands.strategic import pending_marshal_decisions
    rows = []
    for name in pending_marshal_decisions(world):
        shown = humanize_entity_name(name)
        rows.append(_row(f"last_stand:{name}", TIER_BITES,
                         _fit([f"{shown} is cornered and waits for your word — fight to the last, or break out.",
                               f"{shown} is cornered and waits for your word."]),
                         {"kind": "marshal", "marshal": name}))
    return rows


def _rows_battle_days(world, have) -> List[Dict[str, Any]]:
    from backend.game_logic import battle_day, trial
    rows = []
    for day in battle_day.awaiting(world):
        field = str(day.get("field_shown") or day.get("field") or "")
        lead = str(day.get("lead_shown") or "")
        forms = [f"The battle at {field} has no winner yet — {lead} still waits for your orders.",
                 f"The battle at {field} has no winner yet — it waits for your orders.",
                 f"A battle at {field} waits for your orders."]
        getter = getattr(world, "get_marshal", None)
        man = getter(str(day.get("lead") or "")) if callable(getter) else None
        if man is not None and trial.on_trial(man):
            # Row IC, Session 2b (pressed in the real client): a lead on his
            # task to prove himself waits for no order — the day's panel gives
            # his corps none. What is still the Emperor's: to send him help.
            forms = [f"The battle at {field} has no winner yet — {lead} takes no orders; you can send him help.",
                     f"The battle at {field} has no winner yet — you can send {lead} help.",
                     f"A battle at {field} has no winner yet."]
        rows.append(_row(f"day:{day.get('enemy')}", TIER_BITES, _fit(forms),
                         {"kind": "day", "enemy": str(day.get("enemy") or "")}))
    return rows


def _rows_lapses(world, have) -> List[Dict[str, Any]]:
    """The letters that lapse tonight: each priced petition and each moment by
    name, then the free ones as a count."""
    total = int(world.dialogue_manager.get_lapsing_count(int(world.current_turn)))
    if total <= 0:
        return []
    from backend.game_logic.mailbox_payloads import lapsing_petitions
    from backend.game_logic.moments import lapse_gate_rows
    rows = []
    named = 0
    for pet in lapsing_petitions(world, _player(world)) or []:
        if not isinstance(pet, dict):
            continue
        court = humanize_entity_name(str(pet.get("court") or pet.get("vassal") or ""))
        refused = bool(pet["penalised"]) if "penalised" in pet else True
        # The gate's own word: an unanswered petition "will be REFUSED" where
        # the lapse is priced, "left unanswered" where it is free.
        verb = "counts as refused" if refused else "goes unanswered"
        named += 1
        rows.append(_row(f"petition:{pet.get('vassal')}", TIER_BITES,
                         _fit([f"{court}'s petition {verb} if you do not answer it this turn.",
                               f"A petition {verb} if you do not answer it this turn."]),
                         {"kind": "envoys"}, more=str(pet.get("price_line") or "")))
    for mom in lapse_gate_rows(world) or []:
        if not isinstance(mom, dict) or not str(mom.get("title") or ""):
            continue
        named += 1
        # S14C-X26: a letter of state lapses AS ITS DECLINE (`price_line` is
        # that decline, planned now) — so the row says what the silence does.
        rows.append(_row(f"moment:{mom.get('title')}", TIER_BITES,
                         _fit([f"{mom['title']} counts as declined if you do not answer it this turn.",
                               "A letter of state counts as declined if you do not answer it this turn."]),
                         {"kind": "envoys"}, more=str(mom.get("price_line") or "")))
    rest = total - named
    if rest > 0:
        # "envoys": the button that opens them says "Open Envoys", and the
        # gate's sentence counts "unanswered envoys".
        text = ("1 envoy is still unanswered — the offer ends when the turn ends." if rest == 1
                else f"{rest} envoys are still unanswered — their offers end when the turn ends.")
        rows.append(_row("lapse", TIER_BITES, text, {"kind": "envoys"}))
    return rows


def _rows_treasury(world, have) -> List[Dict[str, Any]]:
    """The End Turn gate's own test (`main.gd::_treasury_goes_negative`): the
    chest after next turn's projected net is below zero. The net is the
    envelope's when it holds one (`gold_projected_net`)."""
    net = have.get("gold_projected_net", "?")
    if net == "?":
        from backend.game_logic.ledger import chest_forecast
        net = int(chest_forecast(world, _player(world))["net"])
    if net is None:
        return []
    gold = int(getattr(world, "gold", 0) or 0)
    total = gold + int(net)
    if total >= 0:
        return []
    # The gate's own sentence (`main.gd::_show_lapse_confirmation`): "The
    # treasury will stand at −486 gold when the turn ends (432 now, −918 next
    # turn)" — the same three figures, the same true minus sign.
    now = ("−" if gold < 0 else "") + f"{abs(gold):,}"
    return [_row("treasury", TIER_BITES,
                 _fit([f"The treasury will stand at {_signed(total)} gold when the turn ends "
                       f"({now} now, {_signed(int(net))} a turn).",
                       f"The treasury will stand at {_signed(total)} gold when the turn ends.",
                       "The treasury goes below zero when the turn ends."]),
                 {"kind": "ledger", "tab": 2})]      # the Strategic Ledger's ECONOMY book


def _signed(value: int) -> str:
    """"+1,200" / "−486" — a true minus sign (U+2212), as the client writes a
    signed figure (`main.gd::_signed_number`); a negative total reads "−486"."""
    return ("+" if int(value) > 0 else "−" if int(value) < 0 else "") + f"{abs(int(value)):,}"


def _rows_peril(world, have) -> List[Dict[str, Any]]:
    """The End Turn gate's army sentences, a row each, shortened; the full
    sentence rides as `more`, and the door is the corps the sentence names:
    a corps IN PERIL (`dispatch.end_turn_peril_reading`), spent corps beside a
    known army (`end_turn_morale_reading`), and a bold man who will drop his
    standing order for a battle near him (`end_turn_interrupt_reading`)."""
    from backend.game_logic import dispatch
    player = _player(world)
    rows = []
    peril = dispatch.end_turn_peril_reading(world, player)
    if peril and peril.get("corps"):
        line = str(peril["line"])
        head = line.split(" — ", 1)[0]
        rows.append(_row("peril", TIER_BITES,
                         _fit([line, f"{head} — a much larger enemy shares the field.",
                               "A corps of yours shares a field with a much larger enemy."]),
                         {"kind": "marshal", "marshal": str(peril["corps"][0])}, more=line))
    morale = dispatch.end_turn_morale_reading(world, player)
    if morale and morale.get("corps"):
        line = str(morale["line"])
        head = line.split(" — ", 1)[0]
        rows.append(_row("morale", TIER_BITES,
                         _fit([f"{head}.", "A tired corps of yours stands beside an enemy army."]),
                         {"kind": "marshal", "marshal": str(morale["corps"][0])}, more=line))
    interrupt = dispatch.end_turn_interrupt_reading(world, player)
    for man in (interrupt or {}).get("corps") or []:
        shown = humanize_entity_name(str(man["marshal"]))
        # What he would break off, in the order's own plain word (the third
        # blind reading: "a standing order that I never gave?" — it is the
        # march the player ordered a moment ago).
        leaves = _BREAKS_OFF.get(str(man.get("order") or ""), "will leave his standing order")
        rows.append(_row(f"interrupt:{man['marshal']}", TIER_BITES,
                         _fit([f"{shown} {leaves} to join a battle near him — {man['foe']} is close.",
                               f"{shown} {leaves} to join a battle near him."]),
                         {"kind": "marshal", "marshal": str(man["marshal"])},
                         more=str(interrupt["line"])))
    return rows


# A standing order by its type (`StrategicOrder.command_type`), as the thing a
# bold man breaks off for a battle near him.
_BREAKS_OFF = {
    "MOVE_TO": "will break off his march",
    "PURSUE": "will break off his pursuit",
    "HOLD": "will leave his post",
    "SUPPORT": "will leave the corps he supports",
}


def _rows_danger(world, have) -> List[Dict[str, Any]]:
    from backend.game_logic import threats
    return [_row(f"danger:{row['region']}", TIER_BITES, str(row["line"]),
                 {"kind": "region", "region": str(row["region"])})
            for row in threats.in_danger(world, _player(world))]


def takers(world) -> List[Dict[str, Any]]:
    """Our corps standing on an enemy province that one action takes now, or
    whose works one action begins to besiege — the End Turn gate's
    `_pw_takers`, read from the same `stands_on`."""
    from backend.models.world_state import _stands_on
    out = []
    if int(getattr(world, "actions_remaining", 0) or 0) <= 0:
        return out
    player = _player(world)
    for m in _own_field_corps(world):
        region = world.get_region(m.location)
        if region is None or getattr(region, "controller", None) in (None, "", player):
            continue        # on our own ground: nothing to take (and nothing to read)
        stands = _stands_on(world, m)
        if not stands or not stands.get("ok"):
            continue
        code = str(stands.get("code") or "")
        if stands.get("open") or code == "fort":
            out.append({"marshal": m.name, "place": str(m.location), "fort": code == "fort",
                        "label": str(stands.get("label") or "Take it")})
    return out


def _rows_take(world, have) -> List[Dict[str, Any]]:
    rows = []
    for row in takers(world):
        shown = humanize_entity_name(row["marshal"])
        place = row["place"]
        if row["fort"]:
            # the gate's own words (`main.gd::_pw_take_sentence`)
            text = _fit([f"{shown} stands in {place}, which is fortified and not yet under siege — "
                         "one action begins the siege.",
                         f"{shown} stands in {place}, fortified and not yet under siege — one action begins it.",
                         f"{shown} can begin the siege of {place} for one action."])
        else:
            text = _fit([f"{shown} stands in {place} and nothing holds it — one action takes it.",
                         f"{shown} can take {place} for one action."])
        # The door is the corps himself (his card carries the "Take" button and
        # its price): a desk row never sends an order.
        rows.append(_row(f"take:{row['marshal']}", TIER_WASTES, text,
                         {"kind": "marshal", "marshal": row["marshal"]}))
    return rows


def idle_corps(world) -> List[Any]:
    """Our field corps with nothing to do, in the roster's order (`is_idle`)."""
    turn = int(getattr(world, "current_turn", 0) or 0)
    return [m for m in _own_field_corps(world) if is_idle(m, turn)]


def _rows_reach_and_idle(world, have) -> List[Dict[str, Any]]:
    """An enemy we can see within one march of corps that have no orders and
    could attack today (the heaviest first, `REACH_ROWS` at most), then the
    idle corps those rows did not name, as one row."""
    player = _player(world)
    # Lever L4 (the blind reading, reader 3: "Actions 0/4 — a matter such as
    # '6 corps have no orders' cannot be acted on"): with no action left there
    # is nothing to decide about a corps with no orders, so it is no row — and
    # no reason for End Turn to stop (`main.gd::_ui5_idle_warning_stands`).
    if int(getattr(world, "actions_remaining", 0) or 0) <= 0:
        return []
    idle = idle_corps(world)
    if not idle:
        return []
    # Row IC, directives — ONLY where the player has named a war goal: the
    # corps with no orders that can be sent at it stand FIRST, as ONE order
    # ("8 corps with no orders can march on Vienna, your war goal — see the
    # list"), whose door opens the list filled in. It is the player's own
    # stated aim, so it leads the rows about corps with nothing to do; the
    # reach rows below still say what stands beside them. With no goal set
    # nothing here runs and the rows are what they were.
    goal_rows: List[Dict[str, Any]] = []
    aimed: set = set()
    if getattr(world, "war_goals", None):
        goal_rows, aimed = _rows_goal(world, have, idle)
    rows: List[Dict[str, Any]] = []
    named: set = set()
    ready = [m for m in idle if _can_attack(world, m)]
    if ready:
        sightings = []
        for foe in world.get_visible_enemies(player):
            row = _sighting(world, foe)
            if row is not None:
                sightings.append((foe, row))
        sightings.sort(key=lambda pair: (-_shown_strength(pair[1]), pair[1]["name"]))
        for foe, row in sightings:
            if len(rows) >= REACH_ROWS:
                break
            here = world.get_region(foe.location)
            near = set(getattr(here, "adjacent_regions", None) or []) if here is not None else set()
            near.add(str(foe.location))
            beside = [m for m in ready if str(m.location) in near and m.name not in named]
            if not beside:
                continue
            beside.sort(key=lambda m: (-int(m.strength), m.name))
            who = _names([humanize_entity_name(m.name) for m in beside])
            count = f"{_plural(len(beside), 'corps', 'corps')} of yours"
            have_no = "has no orders" if len(beside) == 1 else "have no orders"
            shown, place = str(row["name"]), str(row["location"])
            # Ours first, then the enemy (the review: "X is in Y — A, B and C
            # are within one march, with no orders" read as the ENEMY's march).
            text = _fit([
                f"{who} {have_no} and {shown} ({_force(row)}) is within one march, in {place}.",
                f"{count} {have_no} and {shown} ({_force(row)}) is within one march, in {place}.",
                f"{who} {have_no} and {shown} is within one march, in {place}.",
                f"{count} {have_no} and {shown} is within one march, in {place}.",
            ])
            # the hover names every one of them (the second reading, reader 3:
            # "'7 corps of yours' does not tell me which ones")
            every = ", ".join(humanize_entity_name(m.name) for m in beside)
            rows.append(_row(f"reach:{foe.name}", TIER_WASTES, text,
                             {"kind": "marshal", "marshal": beside[0].name},
                             more=f"No orders: {every}." if len(beside) > 1 else ""))
            named.update(m.name for m in beside)
    rest = [m for m in idle if m.name not in named and m.name not in aimed]
    if rest:
        shown = [humanize_entity_name(m.name) for m in rest]
        more = "more " if rows else ""
        if len(rest) == 1:
            text = f"{shown[0]} has no orders."
        else:
            text = _fit([f"{len(rest)} {more}corps have no orders: {_names(shown)}.",
                         f"{len(rest)} {more}corps have no orders."])
        rows.append(_row("idle", TIER_WASTES, text, {"kind": "idle"}))
    return goal_rows + rows


def _rows_goal(world, have, idle: List[Any]) -> tuple:
    """Row IC, directives: one row a war goal still to be won — the idle corps
    that can be sent at it, as one order. Returns ``(rows, the names it
    took)``. A place: "march to <place>" by each man's own plain order (the
    click road's — a move next door is the move); an army: "pursue <him>",
    only where the staff knows where he stands. One corps alone is his own
    row (the door selects him); two or more open the list."""
    from backend.game_logic import war_goals
    from backend.game_logic.war_status import build_active_wars
    wars = have.get("wars") if isinstance(have.get("wars"), dict) else None
    if wars is None:
        wars = build_active_wars(world)
    rows: List[Dict[str, Any]] = []
    taken: set = set()
    for goal in war_goals.payload(world, wars):
        if goal["status"] != "open":
            continue
        free = [m for m in idle if m.name not in taken]
        names, order = war_goals.marchers(world, goal, free)
        if not names:
            continue
        taken.update(names)
        shown = [humanize_entity_name(n) for n in names]
        verb = "close on" if goal["kind"] == "army" else "march on"
        what = f"{goal['shown']}, your war goal"
        if len(names) == 1:
            text = _fit([f"{shown[0]} has no orders and can {verb} {what}.",
                         f"{shown[0]} can {verb} {what}."])
            rows.append(_row(f"goal:{goal['court']}", TIER_WASTES, text,
                             {"kind": "marshal", "marshal": names[0]}))
            continue
        # Directives' blind reading 1 (two readers of three): "8 corps with no
        # orders can march on Vienna" stood above "7 corps of yours have no
        # orders and Mack is within one march" — the same idle corps, counted
        # two ways. Where every corps with no orders can go, the row says so
        # without a count (the list counts them; the hover names them).
        whose = "Your corps" if len(names) == len(free) else f"{len(names)} of your corps"
        # "press to list them" since the directives' blind reading 2: two
        # readers of three took "see the list" for the marshal roster.
        text = _fit([f"{whose} with no orders can {verb} {what} — press to list them.",
                     f"{whose} can {verb} {what} — press to list them.",
                     f"{whose} can {verb} your war goal — press to list them."])
        line = (", ".join(names[:-1]) + " and " + names[-1]) + ", " + order
        rows.append(_row(f"goal:{goal['court']}", TIER_WASTES, text,
                         {"kind": "directive", "line": line, "click": True},
                         more=f"No orders: {', '.join(shown)}."))
    return rows, taken


def _rows_strike(world, have) -> List[Dict[str, Any]]:
    """A jealous, bold marshal the dispatch has warned of: he attacks on his
    own as the turn closes unless an order REACHES him this turn — one he
    carried out or one he objected to; an order refused before it reached him
    does not count (`jealousy.process_autonomous_attacks`, `executor.py`'s
    stand-down). The quarry is not named here — the warning names him where
    the player may know him."""
    rows = []
    for m in _own_field_corps(world):
        if getattr(m, "jealousy_autonomous_warned", False):
            shown = humanize_entity_name(m.name)
            rows.append(_row(f"strike:{m.name}", TIER_BITES,
                             _fit([f"{shown} may attack without waiting for orders when the turn ends — an order that reaches him stops it.",
                                   f"{shown} may attack without waiting for orders when the turn ends — an order stops it.",
                                   f"{shown} may attack without waiting for orders when the turn ends."]),
                             {"kind": "marshal", "marshal": m.name}))
    return rows


def _rows_restless(world, have) -> List[Dict[str, Any]]:
    """A literal man left on HOLD or with no order while others march: at
    `LITERAL_RESTLESS_AT` turns Berthier notes it once, at
    `LITERAL_HOLD_TRIGGER` it is a grievance. The row stands for every turn of
    the window."""
    restless = [m for m in _own_field_corps(world)
                if getattr(m, "personality", "") == "literal"
                and int(getattr(m, "consecutive_hold_turns", 0) or 0) > 0]
    if not restless:
        return []
    from backend.game_logic import jealousy
    if jealousy.jealousy_dormant(world):
        return []
    from backend.game_logic.contingent import is_clients_general
    rows = []
    for m in restless:
        if getattr(m, "is_sovereign", False) or getattr(m, "jealous_of", None) or is_clients_general(m):
            continue
        turns = int(m.consecutive_hold_turns)
        if turns < jealousy.LITERAL_RESTLESS_AT:
            continue
        shown = humanize_entity_name(m.name)
        rows.append(_row(f"restless:{m.name}", TIER_WASTES,
                         _fit([f"{shown} has been left out for {_plural(turns, 'turn')} while others march — give him a task.",
                               f"{shown} has been left out while others march — give him a task."]),
                         {"kind": "marshal", "marshal": m.name}))
    return rows


def order_words(order) -> str:
    """A standing order's own words, as the typed line takes them back ("hold
    Lorraine", "march to Lorraine", "pursue Mack", "support Ney")."""
    kind = str(getattr(order, "command_type", "") or "")
    target = humanize_entity_name(str(getattr(order, "target", "") or ""))
    if kind == "HOLD":
        return f"hold {target}".strip()
    if kind == "MOVE_TO":
        return f"march to {target}"
    if kind == "PURSUE":
        return f"pursue {target}"
    if kind == "SUPPORT":
        return f"{'follow' if getattr(order, 'standing_follow', False) else 'support'} {target}"
    return "hold"


def _rows_exact_orders(world, have) -> List[Dict[str, Any]]:
    """Row IC, Session 2 (IC-9; INDEPENDENT_COMMAND_SPEC §7, §12): a standing
    order's IF-THENS that want the player's word —

    * a line that can no longer be carried out (a friend gone, a place to fall
      back on lost) is STRUCK: "his orders are broken", flagged at once;
    * every line used and the order still standing: he stands, and the row
      offers to renew them at the order's own price.

    Either row's door opens his card and WRITES the order's sentence on the
    command line (`line`) — a door never sends an order (§229)."""
    from backend.commands import if_thens
    from backend.display_names import actions_words
    rows = []
    for m in _own_field_corps(world):
        order = getattr(m, "strategic_order", None)
        lines = if_thens.lines(order)
        if not lines:
            continue
        shown = humanize_entity_name(m.name)
        struck = [line for line in lines if line.get("struck")]
        live = if_thens.unused(order)
        kept = [line for line in lines if not line.get("struck")]
        sentence = if_thens.restate(shown, order_words(order), kept or lines)
        if struck:
            why = str(struck[0].get("struck") or "")
            rows.append(_row(
                f"orders_broken:{m.name}", TIER_BITES,
                _fit([f"{shown}'s orders are broken — {why}. Give them again.",
                      f"{shown}'s orders are broken — give them again."]),
                {"kind": "marshal", "marshal": m.name, "line": sentence},
                more=(f"{shown}'s orders are broken: "
                      f"'{if_thens.describe(struck[0])}' can no longer be carried out — {why}.")))
        elif not live:
            price = actions_words(int(m.strategic_order_ap(order_type=order.command_type)))
            rows.append(_row(
                f"orders_used:{m.name}", TIER_WASTES,
                _fit([f"{shown} has used his if-thens and stands — renew them ({price}).",
                      f"{shown} has used his if-thens — renew them ({price})."]),
                {"kind": "marshal", "marshal": m.name, "line": sentence}))
    return rows


def _rows_congress(world, have) -> List[Dict[str, Any]]:
    from backend.game_logic import congress
    if not congress.armed(world):
        return []
    view = _titled(world, have)
    if int(view["count"]) < int(view["needed"]):
        return []       # the count is the bar the other terms stand behind
    from backend.ai.counsel import congress_counsel
    if not congress_counsel(world, _player(world)):
        return []
    return [_row("congress", TIER_GROWS,
                 "You can summon the Congress of Paris now — the way to win; it cannot be undone.",
                 {"kind": "congress"})]


def _rows_law(world, have) -> List[Dict[str, Any]]:
    """The first law of the deck the chest can buy NOW, by the verb's own
    predicate (`reforms.law_refusal`). Gold laws only: a law priced in
    authority is a spending of the Emperor's standing, never a nudge."""
    from backend.game_logic import reforms
    player = _player(world)
    for row in reforms.deck(world, player):
        if (not isinstance(row, dict) or reforms.is_in_force(row)
                or str(row.get("currency") or "gold") != "gold"):
            continue
        if reforms.law_refusal(world, player, str(row.get("id") or "")):
            continue
        name = reforms.display_name(row)
        quote = reforms.restoration_price(world, player, row)
        need = int(quote["price"]) + int(quote["arrears"])
        return [_row(f"law:{row.get('id')}", TIER_GROWS,
                     _fit([f"You can afford {name} ({need:,} gold) — a law, bought once and kept up each turn.",
                           f"You can afford {name} ({need:,} gold).", "You can afford a new law."]),
                     {"kind": "ledger", "tab": 7})]
    return []


def _rows_commission(world, have) -> List[Dict[str, Any]]:
    """A marshal to commission — only where the counsel's own NEED stands (the
    PT-I4 ruling: a thin roster or an army under strength,
    `recruitment.commission_counsel_need`) and a man on the bench clears the
    verb's own gate. Without the need the row was a standing nudge to spend
    (the review, IC-R4)."""
    from backend.game_logic import recruitment
    player = _player(world)
    if not recruitment.commission_counsel_need(world, player):
        return []
    man = recruitment.first_affordable_commission(world, player)
    if not man:
        return []
    shown = humanize_entity_name(str(man.get("name") or ""))
    cost = int(man.get("cost", 0) or 0)
    return [_row("commission", TIER_GROWS,
                 _fit([f"You can commission {shown} to lead a new corps ({cost:,} gold).",
                       f"You can commission {shown} ({cost:,} gold).", "You can commission a new marshal."]),
                 {"kind": "generals"})]


# (reader id, the reader) — THE ORDER OF THE LIST. A reader that raises is
# reported and skipped: one broken reading never takes the desk down.
READERS: List[tuple] = [
    ("last_stand", _rows_last_stand),
    ("battle_days", _rows_battle_days),
    ("lapses", _rows_lapses),
    ("treasury", _rows_treasury),
    ("peril", _rows_peril),
    ("danger", _rows_danger),
    ("strike", _rows_strike),
    ("take", _rows_take),
    ("reach_and_idle", _rows_reach_and_idle),
    ("restless", _rows_restless),
    ("exact_orders", _rows_exact_orders),
    ("congress", _rows_congress),
    ("law", _rows_law),
    ("commission", _rows_commission),
]


def decide(world, have: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Every matter that wants the player's word now, in the list's fixed
    order (the tiers, then the readers' own order within a tier). `have` is
    what the caller already holds (see `desk`)."""
    have = {} if have is None else have
    rows: List[Dict[str, Any]] = []
    for name, reader in READERS:
        try:
            rows.extend(reader(world, have) or [])
        except Exception as exc:
            report(exc, f"today.decide: the {name} reader")
    rows.sort(key=lambda r: int(r.get("tier", TIER_GROWS)))   # stable: readers' order within a tier
    return rows


# ── the payload ─────────────────────────────────────────────────────────────

def _guarded(what: str, build: Callable[[], Any], default: Any) -> Any:
    try:
        return build()
    except Exception as exc:
        report(exc, f"today.desk: {what}")
        return default


def desk(world, wars: Optional[Dict[str, Any]] = None,
         have: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """The `desk` key: {peace, war, decide, more, shown, danger, first_open?}
    — or None with the seam down, after the campaign has ended, or off a board
    with a player.

    `decide` is the WHOLE list (`MAX_ROWS` at most, `more` counts any beyond
    it); `shown` is how many the desk draws before "+n more". `danger` is the
    provinces the map marks. `wars` and `have` are what the envelope already
    built (`active_wars`; `gold_projected_net`) — passed so nothing is read
    twice; both optional."""
    if not the_desk_is_shown() or world is None or not _player(world):
        return None
    if _guarded("game_end.terminal_ending", lambda: _ended(world), False):
        return None
    # The School of War keeps its own guide: the tutor card says the one thing
    # to do next, and a second list beside it would talk over the lesson
    # (`tutorial_state.is_school_world` — the one predicate by which a lesson
    # switches a surface off). The desk first stands in a real campaign.
    if _guarded("tutorial_state.is_school_world", lambda: _in_school(world), False):
        return None
    have = dict(have or {})
    if wars is not None:
        have.setdefault("wars", wars)      # the readers read the wars the envelope built
    blank = {"text": "", "hint": "", "door": {}}
    rows = _guarded("decide", lambda: decide(world, have), [])
    out: Dict[str, Any] = {
        "peace": _guarded("peace", lambda: peace(world, have), dict(blank)),
        "war": _guarded("war", lambda: war(world, wars), dict(blank)),
        "decide": rows[:MAX_ROWS],
        "more": int(max(0, len(rows) - MAX_ROWS)),
        "shown": int(ROWS_SHOWN),
        # The provinces the map marks: the danger rows of the WHOLE list (the
        # reading is made once — `_rows_danger`).
        "danger": [{"region": str(r["door"].get("region") or ""), "line": str(r["text"])}
                   for r in rows if str(r.get("id") or "").startswith("danger:")],
    }
    line = _guarded("first_open", lambda: _first_open_line(world, rows), "")
    if line:
        out["first_open"] = {"screen": "desk", "line": line}
    # Row IC, directives: the wars' goals, for the map's gold ring and the war
    # popup — the key rides only when a goal is set (a board with none carries
    # the payload it always did).
    if getattr(world, "war_goals", None):
        goals = _guarded("goals", lambda: _goals(world, wars), [])
        if goals:
            out["goals"] = goals
    return out


def _goals(world, wars: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
    from backend.game_logic import war_goals
    if wars is None:
        from backend.game_logic.war_status import build_active_wars
        wars = build_active_wars(world)
    return war_goals.payload(world, wars)


def _ended(world) -> bool:
    from backend.game_logic import game_end
    return game_end.terminal_ending(world) is not None


def _in_school(world) -> bool:
    from backend.game_logic import tutorial_state
    return bool(tutorial_state.is_school_world(world))


def _first_open_line(world, rows: List[Dict[str, Any]]) -> str:
    """The desk's once-per-campaign line (`first_open.py`), only while there is
    a TO DECIDE row to point at."""
    if not rows:
        return ""
    from backend.game_logic import first_open
    return first_open.line_for(world, "desk")


def what_now_lines(world, limit: int = 3) -> List[str]:
    """The first `limit` TO DECIDE sentences, for the typed "what now?" — the
    same rows the desk shows. [] with the seam down."""
    if not the_desk_is_shown():
        return []
    try:
        return [str(row["text"]) for row in decide(world)[:max(0, int(limit))]]
    except Exception as exc:
        report(exc, "today.what_now_lines")
        return []
