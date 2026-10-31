"""S14c "Events and Historical Moments" — the moments (`docs/EVENTS_SPEC.md`,
RULED October 22, 2026; Pre-Deploy S14c part 1: the engine and its transport,
UNARMED).

A moment is an authored historical LETTER: a fork of the record that no board
system already puts in front of the Emperor, with a consequence that outlives
the fade (the record's §0 Q1). Its ONE store is `world.moments`:

    {"block": <the scenario's authored `moments` key, windows resolved at boot>,
     "state": {moment_id: {"status", "turn", "answer"?, "reason"?, ...}}}

`status` is fired | answered | lapsed | passed; pending is the ABSENCE of a row
(the latch lives here, never in the 500-row log). A world with no authored
block is UNARMED: the tick returns at once and every reader answers False / {}
(the bare flag world, the tutorial, the legacy rollback — and the shipped 1805
boot until part 2 arms the deck).

The rules (the record §3):

* **No dice, no parser, no LLM.** Windows resolve at boot
  (`campaign_variance.resolve_moment_turns`, the relations-band idiom); a
  causal entry (`lag`) counts from its anchor.
* **Predicates and ops are code, named by the deck** (`PREDICATES`, `OPS`): a
  closed vocabulary of shared functions — every effect on an AI court lands
  through the function the rest of the game uses, and no op reaches a VP-1
  source or verb (§3.6).
* **Shown = applied.** `plan` returns the delivered, clamped figures, the
  refusal and the lines ONCE; the letter renders it and the answer applies it.
* **The transport** is the call-to-arms road: an `incoming_proposal` dialogue,
  `context.proposal_type = "moment_letter"`, with NO court (no `target_nation`,
  no `context.source_nation`); `is_moment_letter` is the one predicate every
  reader asks. Two answers, Accept and Decline; unanswered for two player
  turns, it lapses as the decline.
* **Pacing is authored in the block** (§4): one open letter, a minimum gap
  between arrivals, one moment a morning (R3); a letter waits out a
  foregrounded crisis within its grace (R1) and, crowded out, ends on screen
  as a receipt with its decline applied (R2).
"""
from __future__ import annotations

import copy
from typing import Any, Callable, Dict, List, Optional, Tuple

from backend.errors import report

MOMENT_LETTER_TYPE = "moment_letter"
LOG_TYPE = "moment"
RECEIPT_EVENT = "moment_receipt"
KIND_LETTER = "letter"
KINDS = (KIND_LETTER,)

STATUS_FIRED = "fired"
STATUS_ANSWERED = "answered"
STATUS_LAPSED = "lapsed"
STATUS_PASSED = "passed"
# RE-1 (docs/RECURRING_EVENTS_SPEC.md §7): an AFFAIR letter standing when a
# moment is delivered is withdrawn free — nothing applied, its cooldown
# re-armed. A moment is never withdrawn.
STATUS_WITHDRAWN = "withdrawn"
STATUSES = (STATUS_FIRED, STATUS_ANSWERED, STATUS_LAPSED, STATUS_PASSED, STATUS_WITHDRAWN)
ARRIVED_STATUSES = (STATUS_FIRED, STATUS_ANSWERED, STATUS_LAPSED)

# RE-1 (docs/RECURRING_EVENTS_SPEC.md §9): the recurring deck's arrivals are
# OCCURRENCE rows, "<template>#<n>"; `entry()` resolves one to its template,
# `moment_rows()` is the moments' blindness to them (§7). The register names
# the deck a letter belongs to.
OCCURRENCE_SEP = "#"
REGISTER_MOMENT = "moment"
REGISTER_AFFAIR = "affair"

PASS_PREMISE = "premise"          # the board contradicted it for its whole window (silent; S14C-X24)
PASS_FORSWORN = "forsworn"        # another road of the Empire was proclaimed (silent)
PASS_CROWDED = "crowded"          # R2: still waiting when its grace ended (a receipt)
PASS_VERDICT = "verdict"          # a causal window at or past the Verdict (silent)
PASS_BEFORE_SAVE = "before_save"  # a pre-S14c save's closed window (silent)
PASS_REASONS = (PASS_PREMISE, PASS_FORSWORN, PASS_CROWDED, PASS_VERDICT, PASS_BEFORE_SAVE)

ANSWER_ACCEPT = "accept"
ANSWER_DECLINE = "decline"
ANSWER_ACTIONS = {ANSWER_ACCEPT: "accept_ai_proposal", ANSWER_DECLINE: "reject_ai_proposal"}

ROAD_ANY = "any"
ROAD_NONE = "none"
GATE_OPEN = "open"
GATE_WAIT = "wait"
GATE_FORSWORN = "forsworn"

ANSWER_TURNS = 2          # §0 Q2: a letter stands two player turns
MAILBOX_PRIORITY = 2      # ahead of routine small-court letters (incoming_proposal = 3)

VOICE_CABINET = "cabinet"
VOICE_TALLEYRAND = "talleyrand"
VOICE_ENVOY = "envoy"
# S14D-X42 (October 24, 2026): a letter the record puts in a NAMED mouth that
# is not a court's diplomat — the Dutch deputation under Admiral Ver Huell
# asked for Louis; the Grand Pensionary Schimmelpenninck (the cast's Dutch
# voice) resigned rather than sign, so `envoy` would have voiced the letter
# by the one man who refused it. The authored `name` is the display
# (validator: non-empty, at most NAMED_VOICE_MAX).
VOICE_NAMED = "named"
NAMED_VOICE_MAX = 80
VOICES = (VOICE_CABINET, VOICE_TALLEYRAND, VOICE_ENVOY, VOICE_NAMED)
# ERR-2 (RECURRING_EVENTS_SPEC.md §0b, RE-1): the letters' own office was
# named the Cabinet — the top bar's Cabinet (F1) is the diplomacy wizard, so
# the mailbox source and the voice collided with it. The `cabinet` speaker
# KEY stays (authored in the scenario); its display is the Secretariat.
SECRETARIAT = "The Secretariat"
DISPLAY = "A Moment of History"

# The copy contract (§2) and the in-band tunables (§8), validator-limited.
TITLE_MAX = 40
RECORD_MAX = 240
CAPTION_MAX = 36
ALARM_SOURCE_PREFIX = "moment_"
DECLINE_FORBIDDEN_OPS = ("gold", "dp", "autonomy", "enact_law")
PACING_DEFAULTS = {"max_open": 1, "min_gap": 3}
PACING_BOUNDS = {"max_open": (1, 1), "min_gap": (2, 5)}
GRACE_BOUNDS = (1, 3)
LAG_BOUNDS = (1, 3)
OP_BOUNDS = {"gold": (1, 2000), "dp": (1, 3), "relation": (-20, 20),
             "loyalty": (-20, 20), "alarm": (1, 5)}


# ════════════════════════════════════════════════════════════════════════
# The store
# ════════════════════════════════════════════════════════════════════════

def fresh_state() -> Dict[str, Any]:
    return {}


def resolved_turn(entry: Dict[str, Any]) -> Optional[int]:
    """A windowed entry's turn: the int a boot resolved, or the authored
    `value` of a band not yet resolved (a fixture block). None for a causal
    entry."""
    turn = (entry or {}).get("turn")
    if isinstance(turn, dict):
        value = turn.get("value")
        return None if isinstance(value, bool) or not isinstance(value, int) else int(value)
    if isinstance(turn, bool) or not isinstance(turn, int):
        return None
    return int(turn)


def _clean_block(block: Dict[str, Any]) -> Dict[str, Any]:
    out = {k: copy.deepcopy(v) for k, v in block.items() if not str(k).startswith("_")}
    for entry in out.get("deck") or []:
        if isinstance(entry, dict) and isinstance(entry.get("turn"), dict):
            # An unresolved band collapses to its authored centre (the
            # `historical` reading) — a boot resolves it first, so only a
            # hand-fed block ever reaches this.
            entry["turn"] = resolved_turn(entry)
    return out


def from_block(block: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """The store a boot (or a backfill) seeds from the authored block — {}
    when the scenario authors none (unarmed)."""
    if not isinstance(block, dict) or not isinstance(block.get("deck"), list) or not block["deck"]:
        return {}
    return {"block": _clean_block(block), "state": fresh_state()}


def store_from_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """ONE shape for the scenario and the save (the `imperial_designs`
    idiom): a scenario's `moments` key is the authored block (`owner`,
    `pacing`, `deck`); a save's is the store (`block`, `state`). {} when
    neither (unarmed)."""
    raw = (data or {}).get("moments")
    if not isinstance(raw, dict):
        return {}
    if isinstance(raw.get("block"), dict):
        block = _clean_block(raw["block"])
        if not isinstance(block.get("deck"), list) or not block["deck"]:
            return {}
        state = copy.deepcopy(raw.get("state") or {})
        store = {"block": block, "state": state if isinstance(state, dict) else {}}
        due = raw.get("due")
        if isinstance(due, dict) and due:
            store["due"] = {str(k): int(v) for k, v in due.items()
                            if isinstance(v, int) and not isinstance(v, bool)}
        # RE-1 (RECURRING_EVENTS_SPEC.md §11): the affairs' RUNTIME store —
        # streaks, latch masks, due marks, the set-aside tally, the backfill's
        # `not_before` — ints and short strings only. The AUTHORED deck rides
        # `block["affairs"]` and needs no line here.
        runtime = raw.get("affairs")
        if isinstance(runtime, dict) and runtime:
            store["affairs"] = _clean_runtime(runtime)
        return store
    return from_block(raw)


def _clean_runtime(runtime: Dict[str, Any]) -> Dict[str, Any]:
    """The affairs' runtime store, each value an int or a {str: int} map."""
    out: Dict[str, Any] = {}
    for key, value in runtime.items():
        if isinstance(value, bool):
            continue
        if isinstance(value, int):
            out[str(key)] = int(value)
        elif isinstance(value, dict):
            out[str(key)] = {str(k): int(v) for k, v in value.items()
                             if isinstance(v, int) and not isinstance(v, bool)}
    return out


def _store(world) -> Dict[str, Any]:
    store = getattr(world, "moments", None)
    return store if isinstance(store, dict) else {}


def armed(world) -> bool:
    return bool(_store(world).get("block"))


def _state(world) -> Dict[str, Any]:
    store = _store(world)
    state = store.get("state")
    if not isinstance(state, dict):
        state = fresh_state()
        if store:
            store["state"] = state
    return state


def owner(world) -> str:
    return str((_store(world).get("block") or {}).get("owner") or "")


def deck(world) -> List[Dict[str, Any]]:
    return [e for e in ((_store(world).get("block") or {}).get("deck") or [])
            if isinstance(e, dict) and e.get("id")]


def affairs_block(world) -> Dict[str, Any]:
    """RE-1: the authored recurring deck, `block["affairs"]` — {} unarmed."""
    block = (_store(world).get("block") or {}).get("affairs")
    return block if isinstance(block, dict) else {}


def affairs_deck(world) -> List[Dict[str, Any]]:
    """The affairs' templates. `deck()` stays the dated deck alone: every
    reader keyed on the moments' ids (the road matrix, the windows, the
    sweep's fire turns) never sees a template here."""
    return [e for e in (affairs_block(world).get("deck") or [])
            if isinstance(e, dict) and e.get("id")]


def is_occurrence(moment_id: str) -> bool:
    return OCCURRENCE_SEP in str(moment_id or "")


def template_of(moment_id: str) -> str:
    """"the_host#2" → "the_host"; a moment's id is its own."""
    return str(moment_id or "").split(OCCURRENCE_SEP, 1)[0]


def entry(world, moment_id: str) -> Optional[Dict[str, Any]]:
    """The deck entry a letter id names: a moment by its id, else the affairs
    template an occurrence id ("the_host#2") or a template id resolves to."""
    found = next((e for e in deck(world) if e.get("id") == moment_id), None)
    if found is not None:
        return found
    template = template_of(moment_id)
    return next((e for e in affairs_deck(world) if e.get("id") == template), None)


def moment_rows(state: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """The moments' own rows — every row whose id carries no `#`. The tick's
    open letters, arrivals and gap read these alone, so an affair never
    delays, crowds out or shifts a moment (RECURRING_EVENTS_SPEC.md §7)."""
    return {str(k): v for k, v in (state or {}).items()
            if isinstance(v, dict) and not is_occurrence(k)}


# The ops whose listed amount a tier MULTIPLIES (§5 `scale`, §14: gold 300 ×
# tier, the host −2 × tier). An administrative action is one; a diplomatic
# point and a law are not priced by the tier — those ops change only by an
# authored `tiers` override.
SCALED_OPS = ("gold", "relation", "loyalty", "authority")


def scaled_op(op: Dict[str, Any], tier: int) -> Dict[str, Any]:
    """An affair's op at its tier (§5 `scale`): a `SCALED_OPS` amount / delta
    × tier, unless the op authors `tiers` {"2": x, "3": y} (T1's Decline:
    −5, then −8); any other op takes only the override. Tier 1 is the op."""
    tier = int(tier or 1)
    if tier <= 1:
        return op
    override = (op.get("tiers") or {}).get(str(tier))
    has_override = isinstance(override, int) and not isinstance(override, bool)
    if not has_override and str(op.get("op") or "") not in SCALED_OPS:
        return op
    out = dict(op)
    for key in ("amount", "delta"):
        if key in op and isinstance(op[key], int) and not isinstance(op[key], bool):
            out[key] = int(override) if has_override else int(op[key]) * tier
    return out


def pacing(world) -> Dict[str, int]:
    authored = (_store(world).get("block") or {}).get("pacing") or {}
    out = dict(PACING_DEFAULTS)
    for key in out:
        value = authored.get(key)
        if isinstance(value, int) and not isinstance(value, bool):
            out[key] = int(value)
    return out


def was_due(world, moment_id: str) -> bool:
    """S14C-X24: the letter was DUE on some morning of its window — its
    premise true, its road gate open — and was deferred (R1's crisis, the
    gap, the open letter, R3's one a morning). A letter once due ends
    arrived or on screen (R2), whatever its premise reads when its grace
    ends; `passed(premise)` is the word only for a board that contradicted
    it for its whole window."""
    due = _store(world).get("due")
    return isinstance(due, dict) and moment_id in due


def _mark_due(world, e: Dict[str, Any], turn: int) -> None:
    store = _store(world)
    if store:
        store.setdefault("due", {}).setdefault(str(e["id"]), int(turn))


def status_row(world, moment_id: str) -> Dict[str, Any]:
    row = _state(world).get(moment_id)
    return row if isinstance(row, dict) else {}


def status(world, moment_id: str) -> str:
    return str(status_row(world, moment_id).get("status") or "")


def _turn(world) -> int:
    return int(getattr(world, "current_turn", 0) or 0)


# ════════════════════════════════════════════════════════════════════════
# The predicates — pure (world, owner, params) → bool, named by the deck
# ════════════════════════════════════════════════════════════════════════

def _active(world, court: str) -> bool:
    try:
        return bool(court) and court in set(world.get_active_nations())
    except Exception as exc:
        report(exc, "moments._active: world.get_active_nations")
        return False


def _vassal_row(world, court: str, lord: str) -> Optional[Dict[str, Any]]:
    row = (getattr(world, "vassals", {}) or {}).get(court)
    return row if isinstance(row, dict) and row.get("lord") == lord else None


def _relation(world, a: str, b: str) -> int:
    from backend.game_logic.diplomacy import get_relation
    return int(get_relation(world, a, b))


def _court_warm(world, lord: str, params: Dict[str, Any]) -> bool:
    """M1: the court is active and is the owner's ally or vassal, or at peace
    with the owner at `min_relation` or better."""
    court = str(params.get("court") or "")
    if not _active(world, court):
        return False
    if _vassal_row(world, court, lord) is not None:
        return True
    state = world.get_diplomatic_state(lord, court)
    if state in ("ALLIANCE", "DEFENSIVE_ALLIANCE"):
        return True
    return state == "PEACE" and _relation(world, lord, court) >= int(params.get("min_relation", 30))


def _vassal_slipping(world, lord: str, params: Dict[str, Any]) -> bool:
    """M2: the court is the owner's vassal below `below_autonomy`, and its
    loyalty is at most `loyalty_at_most` or its forecast drift is negative."""
    court = str(params.get("court") or "")
    row = _vassal_row(world, court, lord)
    if row is None or not _active(world, court):
        return False
    if int(row.get("autonomy", 1) or 0) >= int(params.get("below_autonomy", 2)):
        return False
    if int(row.get("loyalty", 0) or 0) <= int(params.get("loyalty_at_most", 70)):
        return True
    from backend.game_logic.vassal import forecast_vassal_loyalty
    return int(forecast_vassal_loyalty(world, lord, court).get("forecast", 0) or 0) < 0


def _design_fulfilled(world, lord: str, params: Dict[str, Any]) -> bool:
    """M3: a design of the Empire stands fulfilled, and the named court is
    active and not the owner's vassal."""
    from backend.game_logic import imperial_designs as ID
    if not ID.is_fulfilled(world, str(params.get("design") or "")):
        return False
    court = str(params.get("court") or "")
    return not court or (_active(world, court) and _vassal_row(world, court, lord) is None)


def _decree_clients_of(world, lord: str, law: str = "") -> List[str]:
    """The owner's clients whose ports enacting the Decree would shut — the
    real `naval.decree_clients`, read as if the owner held it."""
    from backend.game_logic import naval
    target = naval.trade_dominance_nation(world)
    if not target:
        return []
    return [c for c in naval.decree_clients(world, target, decree_by=lord)
            if _vassal_row(world, c, lord) is not None]


def _law_bites(world, lord: str, params: Dict[str, Any]) -> bool:
    """M4: the law is the owner's and not in force, the owner is at war with
    the trade-dominant power, and enacting it would shut at least one port."""
    from backend.game_logic import naval, reforms
    row = reforms.find_law(world, lord, str(params.get("law") or ""))
    if row is None or reforms.is_in_force(row):
        return False
    target = naval.trade_dominance_nation(world)
    if not target or not world.is_at_war(lord, target):
        return False
    return bool(_decree_clients_of(world, lord))


PREDICATES: Dict[str, Callable[[Any, str, Dict[str, Any]], bool]] = {
    "court_warm": _court_warm,
    "vassal_slipping": _vassal_slipping,
    "design_fulfilled": _design_fulfilled,
    "law_bites": _law_bites,
}
# The parameters each predicate requires (the validator reads them).
PREDICATE_PARAMS: Dict[str, Tuple[str, ...]] = {
    "court_warm": ("court",),
    "vassal_slipping": ("court",),
    "design_fulfilled": ("design",),
    "law_bites": ("law",),
}


def _anchor_design_fulfilled(world, lord: str, params: Dict[str, Any]) -> Optional[int]:
    """The morning the fulfilment is first told: the design is stamped at the
    END of turn N (`imperial_designs.tick`, after this morning's tick), so
    the first morning that sees it is N + 1; `lag` counts from there."""
    from backend.game_logic import imperial_designs as ID
    turn = ID.fulfilled_turn(world, str(params.get("design") or ""))
    return None if turn is None else int(turn) + 1


# A causal entry (`lag`) counts from its predicate's anchor.
ANCHORS: Dict[str, Callable[[Any, str, Dict[str, Any]], Optional[int]]] = {
    "design_fulfilled": _anchor_design_fulfilled,
}


def premise(world, e: Dict[str, Any]) -> bool:
    when = e.get("when") or {}
    fn = PREDICATES.get(str(when.get("predicate") or ""))
    if fn is None:
        return False
    try:
        return bool(fn(world, owner(world), when))
    except Exception as exc:
        report(exc, "moments.premise: the predicate")
        return False


# ── The board: derived lines (diplomatic facts and the owner's own state) ──

def _court(world, court: str, *, capitalize: bool = False) -> str:
    from backend.display_names import with_definite_article
    from backend.game_logic.formations import formed_display_name
    return with_definite_article(formed_display_name(world, court) if court else "a court",
                                 capitalize=capitalize)


def _standing(world, lord: str, court: str) -> str:
    if _vassal_row(world, court, lord) is not None:
        return "your vassal"
    state = world.get_diplomatic_state(lord, court)
    return {"ALLIANCE": "your ally", "DEFENSIVE_ALLIANCE": "your defensive ally",
            "WAR": "at war with you", "ARMISTICE": "under an armistice"}.get(state, "at peace with you")


def _board_court_warm(world, lord, params) -> List[str]:
    court = str(params.get("court") or "")
    return [f"{_court(world, court, capitalize=True)}: {_standing(world, lord, court)}, "
            f"goodwill {_relation(world, lord, court)}."]


def _board_vassal_slipping(world, lord, params) -> List[str]:
    from backend.game_logic.vassal import AUTONOMY_NAMES, forecast_vassal_loyalty
    court = str(params.get("court") or "")
    row = _vassal_row(world, court, lord) or {}
    forecast = int(forecast_vassal_loyalty(world, lord, court).get("forecast", 0) or 0)
    return [f"{_court(world, court, capitalize=True)}: your "
            f"{AUTONOMY_NAMES.get(int(row.get('autonomy', 1) or 0), 'client')}, loyalty "
            f"{int(row.get('loyalty', 0) or 0)} (forecast {forecast:+d} a turn), tribute "
            f"{int(round(float(row.get('tribute_rate', 0.75) or 0) * 100))}%."]


def _board_design_fulfilled(world, lord, params) -> List[str]:
    from backend.game_logic import imperial_designs as ID
    design = ID.design(world, str(params.get("design") or "")) or {}
    lines = [f"{design.get('title') or 'The design'} stands, fulfilled on turn "
             f"{ID.fulfilled_turn(world, str(params.get('design') or '')) or 0}."]
    court = str(params.get("court") or "")
    if court:
        lines.append(f"{_court(world, court, capitalize=True)}: {_standing(world, lord, court)}, "
                     f"goodwill {_relation(world, lord, court)}.")
    return lines


def _board_law_bites(world, lord, params) -> List[str]:
    from backend.game_logic import naval
    target = naval.trade_dominance_nation(world) or ""
    clients = _decree_clients_of(world, lord)
    return [f"At war with {_court(world, target)}; {naval.closed_ports_against(world, target)} "
            f"of {naval.continental_ports_total(world)} continental ports are shut against her.",
            "Enacted, the Decree shuts the ports of " + _and_join([_court(world, c) for c in clients])
            + (" too, whatever its autonomy." if len(clients) == 1 else " too, whatever their autonomy.")]


_BOARD: Dict[str, Callable[[Any, str, Dict[str, Any]], List[str]]] = {
    "court_warm": _board_court_warm,
    "vassal_slipping": _board_vassal_slipping,
    "design_fulfilled": _board_design_fulfilled,
    "law_bites": _board_law_bites,
}


def board_lines(world, e: Dict[str, Any]) -> List[str]:
    when = e.get("when") or {}
    fn = _BOARD.get(str(when.get("predicate") or ""))
    if fn is None:
        return []
    try:
        return [str(x) for x in fn(world, owner(world), when) if x]
    except Exception as exc:
        report(exc, "moments.board_lines: the board")
        return []


def _and_join(items: List[str]) -> str:
    items = [str(i) for i in items if i]
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + " and " + items[-1]


# ════════════════════════════════════════════════════════════════════════
# The ops — a closed table of shared functions (the record §3.2)
# ════════════════════════════════════════════════════════════════════════

def _plan_gold(world, lord, op) -> Dict[str, Any]:
    amount = int(op.get("amount", 0) or 0)
    # S14E-X196 / S14E-D19: the gold a letter asks is gated against the ONE
    # chest (`instruments.chest_of` - the treasury less the recurring
    # settlement payments still owed); nothing owed, every sentence is the one
    # it was. RE-1 (RECURRING_EVENTS_SPEC.md §9): read through `purse_of`,
    # which IS the chest for the player and a court's raw treasury twice —
    # byte-identical for the owner, and the one source for any lord (GR5).
    from backend.game_logic.instruments import FREE_OF_OBLIGATIONS, purse_of
    treasury, chest = purse_of(world, lord)
    held = f"{chest:,} gold{FREE_OF_OBLIGATIONS}" if chest < treasury else f"{chest:,}"
    # `before`/`after` stay the COFFERS' (what `_apply_gold` leaves); the gate
    # and the words read the chest
    return {"op": "gold", "amount": amount, "before": treasury, "after": treasury - amount,
            "refusal": ("" if chest >= amount else
                        f"{amount:,} gold is asked; the treasury holds {held}."),
            "line": f"{amount:,} gold (the treasury holds {held})"}


def _apply_gold(world, lord, row) -> None:
    # A purchase, the `imperial_designs.decree` model: charged and shown as Spent.
    world.nation_gold[lord] = int(world.nation_gold.get(lord, 0) or 0) - int(row["amount"])
    if hasattr(world, "record_gold_spent"):
        world.record_gold_spent(lord, int(row["amount"]))


def _plan_dp(world, lord, op) -> Dict[str, Any]:
    from backend.game_logic.vassal import _dp_available
    amount = int(op.get("amount", 0) or 0)
    held = int(_dp_available(world, lord))
    plural = "" if amount == 1 else "s"
    return {"op": "dp", "amount": amount, "before": held, "after": held - amount,
            "refusal": ("" if held >= amount else
                        f"{amount} diplomatic point{plural} {'is' if amount == 1 else 'are'} "
                        f"asked; you hold {held}."),
            "line": f"{amount} diplomatic point{plural} (you hold {held})"}


def _apply_dp(world, lord, row) -> None:
    from backend.game_logic.vassal import _charge_dp
    _charge_dp(world, lord, int(row["amount"]))


def _plan_relation(world, lord, op) -> Dict[str, Any]:
    court = str(op.get("court") or "")
    delta = int(op.get("delta", 0) or 0)
    # RE-1 (§6.1 T2): `unless: vassal` — a client host's bill lands on its
    # loyalty (the `loyalty` op), never on the pair's relation.
    unless_vassal = op.get("unless") == "vassal" and _vassal_row(world, court, lord) is not None
    if not _active(world, court) or court == lord or unless_vassal:
        return {"op": "relation", "court": court, "delta": delta, "skip": True,
                "refusal": "", "line": ""}
    before = _relation(world, lord, court)
    after = max(-100, min(100, before + delta))
    unchanged = " (unchanged)" if after == before else ""
    return {"op": "relation", "court": court, "delta": delta, "before": before, "after": after,
            "refusal": "",
            "line": f"{_court(world, court, capitalize=True)}'s goodwill {before} → {after}{unchanged}"}


def _apply_relation(world, lord, row) -> None:
    if not row.get("skip"):
        # S14E-X112: the letter's consequence drags a mission's pair; booked
        from backend.game_logic.diplomatic_dialogue import modify_relation_booked
        modify_relation_booked(world, lord, str(row["court"]), int(row["delta"]),
                               "moment_letter", lord, str(row["court"]))


def _alarm_label(world, source: str) -> str:
    from backend.game_logic.diplomatic_ledger import _threat_source_label
    return _threat_source_label(world, source)


def _plan_alarm(world, lord, op) -> Dict[str, Any]:
    amount = int(op.get("amount", 0) or 0)
    source = str(op.get("source") or "")
    before = int((getattr(world, "threat_by_target", {}) or {}).get(lord, 0) or 0)
    after = min(100, max(0, before + amount))
    return {"op": "alarm", "amount": amount, "source": source, "before": before,
            "after": after, "refusal": "",
            "line": f"Europe's alarm {before} → {after} ({_alarm_label(world, source)})"}


def _apply_alarm(world, lord, row) -> None:
    from backend.game_logic.coalition import add_threat
    add_threat(world, int(row["amount"]), str(row["source"]), target=lord)


def _loyalty_courts(world, op) -> List[str]:
    if op.get("court"):
        return [str(op["court"])]
    if op.get("design_courts"):
        from backend.game_logic import imperial_designs as ID
        return [str(c) for c in ((ID.design(world, str(op["design_courts"])) or {}).get("courts") or [])]
    return []


def _plan_loyalty(world, lord, op) -> Dict[str, Any]:
    from backend.game_logic.vassal import LOYALTY_MAX, LOYALTY_MIN
    delta = int(op.get("delta", 0) or 0)
    rows, parts = [], []
    for court in _loyalty_courts(world, op):
        vrow = _vassal_row(world, court, lord)
        if vrow is None:
            continue
        before = int(vrow.get("loyalty", 0) or 0)
        after = int(max(LOYALTY_MIN, min(LOYALTY_MAX, before + delta)))
        rows.append({"court": court, "before": before, "after": after})
        parts.append(f"{_court(world, court, capitalize=True)}'s loyalty as your vassal "
                     f"{before} → {after}")
    return {"op": "loyalty", "delta": delta, "courts": rows, "refusal": "",
            "line": "; ".join(parts)}


def _apply_loyalty(world, lord, row) -> None:
    from backend.game_logic.vassal import adjust_loyalty
    for court_row in row.get("courts") or []:
        adjust_loyalty(world, str(court_row["court"]), int(row["delta"]), lord=lord)


def _plan_autonomy(world, lord, op) -> Dict[str, Any]:
    from backend.game_logic.vassal import AUTONOMY_NAMES, autonomy_change_plan, _dp_available
    court = str(op.get("court") or "")
    level = int(op.get("level", 0) or 0)
    p = autonomy_change_plan(world, court, level, actor=lord)
    if not p["ok"]:
        return {"op": "autonomy", "court": court, "level": level, "refusal": p["message"],
                "line": ""}
    return {"op": "autonomy", "court": court, "level": level, "refusal": "",
            "loyalty_before": p["loyalty_before"], "loyalty_after": p["loyalty_after"],
            "ports_before": p["ports_before"], "ports_after": p["ports_after"],
            "line": (f"{_court(world, court, capitalize=True)} becomes "
                     f"{AUTONOMY_NAMES.get(level, '')}: {p['line']}; {p['dp_cost']} diplomatic "
                     f"point (you hold {int(_dp_available(world, lord))})")}


def _apply_autonomy(world, lord, row) -> None:
    from backend.game_logic.vassal import change_vassal_autonomy
    change_vassal_autonomy(world, str(row["court"]), int(row["level"]), actor=lord)


def _plan_enact_law(world, lord, op) -> Dict[str, Any]:
    """The FULL verb (the critics' R3): `law_refusal` (the admin action
    included), then `enact_law`, then `use_admin_action` — the executor's
    own charge, which `enact_law` never makes."""
    from backend.game_logic import naval, reforms
    law = str(op.get("law") or "")
    row = reforms.find_law(world, lord, law)
    if row is None:
        return {"op": "enact_law", "law": law, "refusal": "The law is not in the book, Sire.",
                "line": ""}
    refusal = str(reforms.law_refusal(world, lord, law) or "")
    target = naval.trade_dominance_nation(world) or ""
    before = int(naval.closed_ports_against(world, target)) if target else 0
    after = int(naval.closed_ports_against(world, target, decree_by=lord)) if target else 0
    total = int(naval.continental_ports_total(world))
    closure = (f"; ports shut against {_court(world, target)} {before} → {after} of {total}"
               if target else "")
    return {"op": "enact_law", "law": law, "refusal": refusal,
            "ports_before": before, "ports_after": after,
            "line": f"{reforms.terms_line(world, lord, row)}; 1 administrative action{closure}"}


def _apply_enact_law(world, lord, row) -> None:
    from backend.game_logic import reforms
    law_row = reforms.find_law(world, lord, str(row["law"]))
    if law_row is None:
        return
    reforms.enact_law(world, lord, law_row)
    world.use_admin_action()


# RE-1 (RECURRING_EVENTS_SPEC.md §5, §6.1 "the `authority` op, exactly"): the
# floor is on the GRIP — what the Charges and the aura read — at 71, so the
# marshals' calm (`reforms.CALM_ABOVE`, 70) survives every affair's price.
AUTHORITY_GRIP_FLOOR = 71


def _plan_authority(world, lord, op) -> Dict[str, Any]:
    """The lord's standing, priced by an affair's Decline: the delivered loss
    is min(|amount|, max(0, grip − 71)) — never more, never a rise; the line
    is the laws' own (`reforms.authority_line` + the Charges' grip clause).
    A lord without a tracker (an AI court) is skipped, line ""."""
    delta = int(op.get("amount", 0) or 0)
    tracker = (getattr(world, "authority_tracker", None)
               if lord == getattr(world, "player_nation", None) else None)
    if tracker is None or delta >= 0:
        return {"op": "authority", "amount": delta, "skip": True, "refusal": "", "line": ""}
    from backend.game_logic.ledger import charges_grip_clause
    from backend.game_logic.reforms import authority_line
    from backend.models.authority import get_imperial_grip
    before = int(getattr(tracker, "authority", 0) or 0)
    grip = int(get_imperial_grip(world, lord))
    loss = int(min(-delta, max(0, grip - AUTHORITY_GRIP_FLOOR)))
    after = before - loss
    line = authority_line(before, after).rstrip(".")
    clause = str(charges_grip_clause(world, lord, before, after) or "").rstrip(".")
    if clause:
        line = f"{line}; {clause}"
    return {"op": "authority", "amount": delta, "loss": loss, "before": before, "after": after,
            "grip": grip, "refusal": "", "line": line}


def _apply_authority(world, lord, row) -> None:
    if row.get("skip") or not int(row.get("loss", 0) or 0):
        return
    world.authority_tracker.modify_authority(-int(row["loss"]))


def _plan_admin(world, lord, op) -> Dict[str, Any]:
    """One of today's administrative actions (`world.use_admin_action`): the
    player's budget; an AI lord's is a local of its turn, so a court is
    skipped. With none left the Accept is closed with its own words."""
    amount = int(op.get("amount", 1) or 1)
    if lord != getattr(world, "player_nation", None):
        return {"op": "admin", "amount": amount, "skip": True, "refusal": "", "line": ""}
    held = int(getattr(world, "admin_actions_remaining", 0) or 0)
    plural = "" if amount == 1 else "s"
    return {"op": "admin", "amount": amount, "before": held, "after": held - amount,
            "refusal": "" if held >= amount else "the day's administration is already spoken for.",
            "line": f"{amount} administrative action{plural} ({max(0, held - amount)} left today)"}


def _apply_admin(world, lord, row) -> None:
    if not row.get("skip"):
        world.use_admin_action(int(row["amount"]))


OPS: Dict[str, Tuple[Callable[..., Dict[str, Any]], Callable[..., None]]] = {
    "gold": (_plan_gold, _apply_gold),
    "dp": (_plan_dp, _apply_dp),
    "relation": (_plan_relation, _apply_relation),
    "alarm": (_plan_alarm, _apply_alarm),
    "loyalty": (_plan_loyalty, _apply_loyalty),
    "autonomy": (_plan_autonomy, _apply_autonomy),
    "enact_law": (_plan_enact_law, _apply_enact_law),
    "authority": (_plan_authority, _apply_authority),
    "admin": (_plan_admin, _apply_admin),
}
OP_TYPES = tuple(OPS)


def _answer_side(e: Dict[str, Any], answer: str, form: Any) -> Dict[str, Any]:
    """The answer's authored half — the frozen form's (P18) when the entry
    authors `forms` and the row froze one, else the entry's own."""
    forms = (e or {}).get("forms")
    if form and isinstance(forms, dict) and isinstance(forms.get(str(form)), dict):
        side = forms[str(form)].get(answer)
        if isinstance(side, dict):
            return side
    side = (e or {}).get(answer)
    return side if isinstance(side, dict) else {}


def _bind_op(op: Dict[str, Any], occ: Dict[str, Any]) -> Dict[str, Any]:
    """An affair op's selector (§5): `$host` is the row's bound host, `$lord`
    its lord. A moment's ops name their courts and pass through."""
    court = op.get("court")
    if court not in ("$host", "$lord"):
        return op
    bind = occ.get("bind") if isinstance(occ.get("bind"), dict) else {}
    out = dict(op)
    out["court"] = str(bind.get("host") or "") if court == "$host" else str(occ.get("lord") or "")
    return out


class _Figures(dict):
    def __missing__(self, key):
        return "?"


def _receipt(world, lord: str, side: Dict[str, Any], rows: List[Dict[str, Any]]) -> str:
    """P19: the row's frozen short line — the authored `button_line` with the
    plan's figures inserted (P11), else the first op's line; ≤ 120."""
    figures = _Figures()
    for row in rows:
        op = str(row.get("op") or "")
        if op == "gold":
            figures["gold"] = f"{int(row.get('amount', 0) or 0):,}"
        elif op == "authority":
            figures["authority_before"] = int(row.get("before", 0) or 0)
            figures["authority_after"] = int(row.get("after", 0) or 0)
        elif op == "admin":
            figures["admin_left"] = max(0, int(row.get("after", 0) or 0))
        elif op == "relation" and not row.get("skip"):
            figures["relation_before"] = int(row.get("before", 0) or 0)
            figures["relation_after"] = int(row.get("after", 0) or 0)
            figures["host"] = _court(world, str(row.get("court") or ""), capitalize=True)
        elif op == "loyalty" and row.get("courts"):
            first = row["courts"][0]
            figures["loyalty_before"] = int(first.get("before", 0) or 0)
            figures["loyalty_after"] = int(first.get("after", 0) or 0)
            figures.setdefault("host", _court(world, str(first.get("court") or ""), capitalize=True))
    template = str(side.get("button_line") or "")
    text = template.format_map(figures) if template else next(
        (str(r["line"]) for r in rows if r.get("line")), "no change")
    return text[:120]


def plan(world, e: Dict[str, Any], answer: str,
         occ: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """THE plan of one answer (shown = applied): every op's delivered,
    clamped figures, the first refusal and the lines, read once. The letter
    renders it; `answer` re-derives it and applies exactly it.

    RE-1: `occ` is an affair's occurrence row — its `lord`, its bound subject
    (`$host`), its `tier` and its frozen `form` decide the figures, and the
    plan's `id` is the occurrence's. A moment passes none and plans for the
    owner, as before."""
    occ = occ if isinstance(occ, dict) else {}
    lord = str(occ.get("lord") or owner(world))
    tier = int(occ.get("tier") or 1)
    side = _answer_side(e, answer, occ.get("form"))
    caption = str(side.get("caption") or answer)
    rows: List[Dict[str, Any]] = []
    for op in side.get("ops") or []:
        op = _bind_op(scaled_op(op or {}, tier), occ) if occ else (op or {})
        fns = OPS.get(str(op.get("op") or ""))
        if fns is None:
            continue
        try:
            rows.append(fns[0](world, lord, op))
        except Exception as exc:
            report(exc, "moments.plan: an op's plan")
            rows.append({"op": str(op.get("op")), "line": "",
                         "refusal": "The chancery cannot price this answer today, Sire."})
    refusal = next((str(r["refusal"]) for r in rows if r.get("refusal")), "")
    lines = [str(r["line"]) for r in rows if r.get("line")]
    effect = f"{'; '.join(lines)}." if lines else "no change."
    out = {"id": str(occ.get("id") or (e or {}).get("id") or ""), "answer": answer,
           "caption": caption, "ok": not refusal, "refusal": refusal, "rows": rows,
           "lines": lines, "effect": effect, "quote": f"{caption}: {effect}", "lord": lord}
    if occ:
        out["receipt"] = _receipt(world, lord, side, rows)
    return out


def _apply(world, p: Dict[str, Any]) -> None:
    lord = str(p.get("lord") or owner(world))
    for row in p.get("rows") or []:
        fns = OPS.get(str(row.get("op") or ""))
        if fns is None:
            continue
        try:
            fns[1](world, lord, row)
        except Exception as exc:
            report(exc, "moments._apply: an op's apply")


# ════════════════════════════════════════════════════════════════════════
# The windows, the road gate (the VP-1 hand-off, §3.6)
# ════════════════════════════════════════════════════════════════════════

def window(world, e: Dict[str, Any]) -> Optional[Tuple[int, int]]:
    """(first, last) eligible morning — a windowed entry's resolved turn to
    turn + grace; a causal entry's anchor + lag to + grace. None while a
    causal entry's anchor has not come."""
    grace = int(e.get("grace", 0) or 0)
    if e.get("lag") is not None:
        when = e.get("when") or {}
        anchor_fn = ANCHORS.get(str(when.get("predicate") or ""))
        if anchor_fn is None:
            return None
        anchor = anchor_fn(world, owner(world), when)
        if anchor is None:
            return None
        lo = int(anchor) + int(e.get("lag") or 0)
    else:
        lo = resolved_turn(e)
        if lo is None:
            return None
    return lo, lo + grace


def road_gate(world, e: Dict[str, Any]) -> str:
    """open | wait | forsworn. `roads` holds "any", the proclaimed road, or
    "none" while no road is proclaimed; any other proclaimed road forswears
    the moment (irreversible — VP-1's proclamation cannot be undone). Reads
    only the public `proclaimed_road` and `road_state` (S14C-X17)."""
    roads = [str(r) for r in (e.get("roads") or [ROAD_ANY])]
    if ROAD_ANY in roads:
        return GATE_OPEN
    from backend.game_logic import imperial_designs as ID
    if not ID.proclaimed_road(world):
        return GATE_OPEN if ROAD_NONE in roads else GATE_WAIT
    if any(ID.road_state(world, r) == ID.ROAD_STATE_PROCLAIMED for r in roads if r != ROAD_NONE):
        return GATE_OPEN
    return GATE_FORSWORN


# ════════════════════════════════════════════════════════════════════════
# The transport — the letter, its verdict, its answer, its lapse
# ════════════════════════════════════════════════════════════════════════

def is_moment_letter(letter: Any) -> bool:
    """THE predicate every reader asks: a dialogue (or its popup payload)
    that is a moment letter."""
    if not isinstance(letter, dict):
        return False
    context = letter.get("context") if isinstance(letter.get("context"), dict) else {}
    return (str((context or {}).get("proposal_type") or "") == MOMENT_LETTER_TYPE
            or bool(letter.get("is_moment")))


def moment_id_of(letter: Dict[str, Any]) -> str:
    context = letter.get("context") if isinstance(letter.get("context"), dict) else {}
    return str((context or {}).get("moment_id") or letter.get("moment_id") or "")


def _context(letter: Dict[str, Any]) -> Dict[str, Any]:
    context = letter.get("context")
    return context if isinstance(context, dict) else {}


def _dateline(world, turn: int) -> str:
    from backend.game_logic.calendar import calendar_label
    return calendar_label(getattr(world, "start_date", ""), int(turn)) or f"turn {int(turn)}"


def voice_of(world, e: Dict[str, Any], occ: Optional[Dict[str, Any]] = None) -> str:
    """The letter's mouth. RE-1 adds the affairs' speakers: `named` and
    `office` read the authored name; `host` is the occurrence's bound court
    (RE-2's display table names its minister by the turn)."""
    voice = e.get("voice") or {}
    speaker = str(voice.get("speaker") or VOICE_CABINET)
    if speaker == VOICE_CABINET:
        return SECRETARIAT
    if speaker in (VOICE_NAMED, "office"):
        return str(voice.get("name") or "").strip() or SECRETARIAT
    if speaker == "host":
        bind = (occ or {}).get("bind") if isinstance((occ or {}).get("bind"), dict) else {}
        host = str(bind.get("host") or "")
        return f"The court of {_court(world, host)}" if host else SECRETARIAT
    from backend.game_logic.diplomatic_templates import resolve_named_diplomat
    return resolve_named_diplomat(speaker, str(voice.get("nation") or ""), world) or SECRETARIAT


def _affair_fields(mid: str, p: Dict[str, Any]) -> Dict[str, Any]:
    """The log row's extra fields for an occurrence — {} for a moment, so a
    moment's rows are the rows they were."""
    if not is_occurrence(mid):
        return {}
    return {"lord": str(p.get("lord") or ""), "register": REGISTER_AFFAIR, "occurrence": mid}


def _stamp_receipt(world, e: Dict[str, Any], row: Dict[str, Any], p: Dict[str, Any],
                   answer_key: str) -> None:
    """P19: an occurrence row keeps the copy the Correspondence re-reads —
    the `receipt` (the plan's short line) and the `echo` (the answer's reply),
    frozen at the answer or the lapse; the 500-row log is never re-read."""
    from backend.game_logic import affairs
    row["receipt"] = str(p.get("receipt") or "")[:120]
    side = _answer_side(e, answer_key, row.get("form"))
    row["echo"] = affairs.fill_slots(world, str(side.get("echo") or ""), row)[:160]


def unanswered_sentence(e: Dict[str, Any], decline_plan: Dict[str, Any]) -> str:
    """The moment's own lapse line ("The Throne of Holland was left
    unanswered — Keep the Republic: no change.")."""
    return f"{e.get('title') or 'The letter'} was left unanswered — {decline_plan['quote']}"


def letter_payload(world, e: Dict[str, Any], issued: int, answer_by: int,
                   occ: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """The popup payload, planned afresh at every read (the IGR-2 lesson: no
    baked figure). The copy contract's parts (§2): the dateline, the record,
    the board, the answers, the unanswered line — and the sixth, the
    first-open line (S14d A5), which is NOT built here: `first_open.with_line`
    attaches it at the response edge, on a copy, on the first letter only.

    RE-1: an affair passes its occurrence row — the id, the lord, the bound
    host and the frozen form plan the figures; its record is the ground and
    the chapter, its board the premise's facts (`affairs`)."""
    occ = occ if isinstance(occ, dict) else {}
    affair = bool(occ)
    accept = plan(world, e, ANSWER_ACCEPT, occ)
    decline = plan(world, e, ANSWER_DECLINE, occ)
    if affair:
        from backend.game_logic import affairs
        board = affairs.board_lines(world, e, occ)
        record = affairs.record_text(world, e, occ)
        title = affairs.title_of(e, occ)
    else:
        board = board_lines(world, e)
        record = str(e.get("record") or "")
        title = str(e.get("title") or "")
    unanswered = (f"If unanswered by {_dateline(world, answer_by)}: {decline['caption']} — "
                  f"{decline['effect']}")
    payload = {
        "is_moment": True,
        "moment_id": str(occ.get("id") or e.get("id") or ""),
        "proposal_type": MOMENT_LETTER_TYPE,
        "proposal_type_display": DISPLAY,
        "from_nation": "",
        "diplomat_name": voice_of(world, e, occ),
        "title": title,
        "dateline": _dateline(world, issued),
        "record": record,
        "board": board,
        "answers": [{"action": ANSWER_ACTIONS[ANSWER_ACCEPT], "caption": accept["caption"],
                     "quote": accept["quote"]},
                    {"action": ANSWER_ACTIONS[ANSWER_DECLINE], "caption": decline["caption"],
                     "quote": decline["quote"]}],
        "unanswered_line": unanswered,
        "issued_turn": int(issued),
        "answer_by_turn": int(answer_by),
        "clauses": [record] + board + ["What each answer does:", accept["quote"],
                                       decline["quote"], unanswered],
        "talleyrand_assessment": "",
        "choice_display": {"accept": accept["caption"], "reject": decline["caption"]},
    }
    if affair:
        payload["register"] = REGISTER_AFFAIR
        payload["occurrence"] = str(occ.get("id") or "")
    return payload


def _letter_text(payload: Dict[str, Any]) -> str:
    body = "\n".join(f"  {line}" for line in payload["clauses"])
    return (f"{payload['diplomat_name']} — {payload['title']}, {payload['dateline']}.\n\n{body}")


def _letter_options(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [{"label": a["caption"], "description": a["quote"], "action": a["action"]}
            for a in payload["answers"]]


def build_letter(world, e: Dict[str, Any], issued: int,
                 mid: Optional[str] = None) -> Dict[str, Any]:
    """The letter as an `incoming_proposal` dialogue with no court — the
    Secretariat speaks; the Accept is stamped from THE verdict
    (`treaty.can_sign`'s moment arm) at build and at every read. RE-1: `mid`
    is an affair's occurrence id — ONE string per arrival, carried by the
    state row, the context, the payload, the notice and the log row."""
    mid = str(mid or e.get("id") or "")
    answer_by = int(issued) + ANSWER_TURNS - 1
    payload = letter_payload(world, e, issued, answer_by, status_row(world, mid))
    dialogue = {
        "type": "incoming_proposal",
        "talleyrand_text": _letter_text(payload),
        "options": _letter_options(payload),
        "context": {"proposal_type": MOMENT_LETTER_TYPE, "moment_id": mid,
                    "issued_turn": int(issued), "answer_by_turn": answer_by},
        "proposal_terms_summary": str(e.get("title") or ""),
        "turn_created": int(issued),
        "blocking": False,
        "popup_payload": payload,
    }
    from backend.game_logic.treaty import refresh_letter_verdict
    refresh_letter_verdict(world, dialogue)
    return dialogue


def refresh_letter(world, dialogue: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Seam 4: re-plan and restamp a standing letter at every read; returns
    the fresh popup payload (its `dialogue_id` kept), or None when the
    dialogue is not a moment letter of this deck."""
    if not is_moment_letter(dialogue):
        return None
    mid = moment_id_of(dialogue)
    e = entry(world, mid)
    if e is None:
        return None
    context = _context(dialogue)
    issued = int(context.get("issued_turn") or dialogue.get("turn_created") or _turn(world))
    answer_by = int(context.get("answer_by_turn") or issued + ANSWER_TURNS - 1)
    old = dialogue.get("popup_payload") if isinstance(dialogue.get("popup_payload"), dict) else {}
    payload = letter_payload(world, e, issued, answer_by, status_row(world, mid))
    if old.get("dialogue_id") or dialogue.get("dialogue_id"):
        payload["dialogue_id"] = old.get("dialogue_id") or dialogue.get("dialogue_id")
    dialogue["popup_payload"] = payload
    dialogue["talleyrand_text"] = _letter_text(payload)
    dialogue["options"] = _letter_options(payload)
    from backend.game_logic.treaty import refresh_letter_verdict
    return refresh_letter_verdict(world, dialogue) or payload


def answer_verdict(world, letter: Dict[str, Any], action: Optional[str] = None):
    """`treaty.can_sign`'s moment arm: the Accept is open while the letter
    stands and its plan carries no refusal; closed with the plan's own words
    otherwise (the letter stands). The Decline is never priced (the
    validator forbids it), so it is never closed."""
    from backend.game_logic.treaty import _no, _ok
    mid = moment_id_of(letter)
    e = entry(world, mid)
    if e is None or status(world, mid) != STATUS_FIRED:
        return _no("moment_passed", "This moment has passed, Sire.")
    answer = ANSWER_DECLINE if action == ANSWER_ACTIONS[ANSWER_DECLINE] else ANSWER_ACCEPT
    p = plan(world, e, answer, status_row(world, mid))
    return _ok() if p["ok"] else _no("moment_price", p["refusal"])


def _dismiss_notice(world, moment_id: str) -> None:
    from backend.notifications import DIPLOMATIC_PROPOSAL
    notifications = getattr(world, "notifications", None)
    if notifications is None:
        return
    notifications.dismiss_by_type(
        DIPLOMATIC_PROPOSAL,
        lambda n, _mid=moment_id: str(((n.get("details") or {}).get("moment_id")) or "") == _mid)


def _log(world, phase: str, e: Dict[str, Any], **fields) -> None:
    """One `moment` row. RE-1: an affair's row names its lord as the nation,
    its occurrence id as the moment, and carries `register: "affair"`
    (`_affair_fields`); a moment's row is the row it was."""
    lord = fields.pop("lord", None)
    occurrence = fields.pop("occurrence", None)
    event = {"type": "moment", "phase": phase, "nation": str(lord or owner(world)),
             "moment": str(occurrence or e.get("id") or ""), "title": str(e.get("title") or "")}
    event.update({k: v for k, v in fields.items() if v is not None})
    world.log_event(event)


def answer(world, dialogue: Dict[str, Any], answer_key: str) -> Dict[str, Any]:
    """Seam 3: the one answer road (the head branch of the accept, reject and
    — refusing — counter handlers). Re-derive the refusal; a refused answer
    leaves the letter standing, charges nothing and says why. Otherwise
    apply exactly the plan, write the store, pop the letter, dismiss its own
    notice, log one `moment` / `answered` row."""
    mid = moment_id_of(dialogue)
    e = entry(world, mid)
    row = status_row(world, mid)
    dm = getattr(world, "dialogue_manager", None)
    if e is None or row.get("status") != STATUS_FIRED:
        if dm is not None:
            dm.remove_matching(lambda d, _d=dialogue: d is _d)
        _dismiss_notice(world, mid)
        return {"success": False, "message": "This moment has passed, Sire — the letter is withdrawn."}
    p = plan(world, e, answer_key, row)
    if not p["ok"]:
        refresh_letter(world, dialogue)
        return {"success": False,
                "message": f"'{p['caption']}' is not open, Sire — {p['refusal']}",
                "decision_reason": "stands", "moment_stands": True,
                "diplomatic_dialogue": dialogue, "awaiting_diplomatic_response": True}
    _apply(world, p)
    row.update({"status": STATUS_ANSWERED, "answer": answer_key, "answered_turn": _turn(world)})
    if is_occurrence(mid):
        _stamp_receipt(world, e, row, p, answer_key)
    if dm is not None:
        dm.remove_matching(lambda d, _d=dialogue: d is _d)
    _dismiss_notice(world, mid)
    _log(world, "answered", e, answer=answer_key, caption=p["caption"], line=p["quote"],
         **_affair_fields(mid, p))
    return {"success": True, "message": f"{e.get('title')} — {p['quote']}",
            "decision_reason": "moment_answered", "suppress_proposal_result_popup": True,
            "moment_answered": {"id": mid, "answer": answer_key}}


def counter_refusal(dialogue: Dict[str, Any]) -> Dict[str, Any]:
    """A moment letter is answered, never bargained: the Counter refuses and
    the letter stands (nothing popped, nothing charged)."""
    return {"success": False,
            "message": "A moment of history is answered, Sire, not bargained — choose one of its two answers.",
            "decision_reason": "stands", "moment_stands": True}


def keeps_open(dialogue: Dict[str, Any], current_turn: int) -> bool:
    """Read by the lapse (`dialogue_manager.lapse_pending_offers`): a moment
    letter stands until the end of its answer-by turn — two player turns."""
    if not is_moment_letter(dialogue):
        return False
    return int(current_turn) < int(_context(dialogue).get("answer_by_turn") or 0)


def lapse_gate_rows(world) -> List[Dict[str, Any]]:
    """S14C-X26: each standing moment letter the end of THIS turn would lapse
    (the one predicate, `DialogueManager.item_lapses`), with its decline
    planned now — the end-turn gate names it as it names a petition (IQ-7
    R8(d): a lapse is priced aloud), never as a nameless envoy."""
    dm = getattr(world, "dialogue_manager", None)
    if dm is None or not armed(world):
        return []
    turn = _turn(world)
    current = dm.peek()
    rows: List[Dict[str, Any]] = []
    for letter in ([current] if current else []) + list(dm.iter_queue()):
        if not is_moment_letter(letter) or not dm.item_lapses(letter, turn):
            continue
        mid = moment_id_of(letter)
        e = entry(world, mid)
        if e is None or status(world, mid) != STATUS_FIRED:
            continue
        p = plan(world, e, ANSWER_DECLINE, status_row(world, mid))
        rows.append({"moment": mid, "title": str(e.get("title") or ""),
                     "price_line": f"{p['caption']} — {p['effect']}"})
    return rows


def lapse_default(world, letter: Dict[str, Any]) -> Dict[str, Any]:
    """Seam 5: an unanswered letter lapses as the decline — its plan applied,
    the store written `lapsed`, its notice dismissed; returns the key the
    lapse row carries (`{}` for any other letter). It never touches the
    dialogue manager (it runs inside the lapse's own loop)."""
    if not is_moment_letter(letter):
        return {}
    mid = moment_id_of(letter)
    e = entry(world, mid)
    row = status_row(world, mid)
    if e is None or row.get("status") != STATUS_FIRED:
        return {"moment": {"id": mid, "title": str((e or {}).get("title") or ""), "line": ""}}
    p = plan(world, e, ANSWER_DECLINE, row)
    if p["ok"]:
        _apply(world, p)
    row.update({"status": STATUS_LAPSED, "answer": ANSWER_DECLINE, "lapsed_turn": _turn(world)})
    if is_occurrence(mid):
        _stamp_receipt(world, e, row, p, ANSWER_DECLINE)
    _dismiss_notice(world, mid)
    return {"moment": {"id": mid, "title": str(e.get("title") or ""),
                       "line": unanswered_sentence(e, p)}}


# ════════════════════════════════════════════════════════════════════════
# The tick — the morning's moments (the record §3.5, §4)
# ════════════════════════════════════════════════════════════════════════

def _pass(world, e: Dict[str, Any], reason: str, turn: int) -> None:
    _state(world)[str(e["id"])] = {"status": STATUS_PASSED, "turn": int(turn), "reason": reason}


def _crowd_out(world, e: Dict[str, Any], turn: int) -> None:
    """R2: a letter still waiting when its grace ends is `passed(crowded)`,
    its decline applied, and ends ON SCREEN — one `moment` / `passed` row
    and one `moment_receipt` dispatch row (no headline)."""
    p = plan(world, e, ANSWER_DECLINE)
    if p["ok"]:
        _apply(world, p)
    _pass(world, e, PASS_CROWDED, turn)
    line = (f"{e.get('title') or 'A letter'} could not be laid before the Emperor in its "
            f"season, and passed — {p['quote']}")
    _log(world, "passed", e, reason=PASS_CROWDED, line=line)
    from backend.game_logic.dispatch import queue_dispatch_event
    queue_dispatch_event(world, RECEIPT_EVENT, {"line": line}, "always")


def deliver_letter(world, e: Dict[str, Any], turn: int, mid: Optional[str] = None,
                   row: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Seam 1: build and push the letter, write `fired`, one `moment` /
    `arrived` row and one rail notice (with the stable `moment_id` detail
    key). It never uses `deliver_ai_proposal` (court-indexed). RE-1: an
    affair passes its occurrence id and the row's frozen `{id, lord, bind,
    tier, form}` (§5: ints and short strings, written at delivery)."""
    mid = str(mid or e["id"])
    state_row: Dict[str, Any] = {"status": STATUS_FIRED, "turn": int(turn)}
    if row:
        state_row.update(row)
    _state(world)[mid] = state_row
    dialogue = build_letter(world, e, turn, mid)
    dm = world.dialogue_manager
    dm.push(dialogue)
    # `_assign_mailbox_metadata` stamps the dtype's priority at the push; the
    # letter sorts ahead of routine small-court mail.
    dialogue["mailbox_priority"] = MAILBOX_PRIORITY
    if dm.peek() is dialogue:
        world.incoming_proposal_popup = copy.deepcopy(dialogue["popup_payload"])
    payload = dialogue["popup_payload"]
    from backend.notifications import DIPLOMATIC_PROPOSAL, NotificationPriority, create_notification
    world.notifications.add(create_notification(
        DIPLOMATIC_PROPOSAL, NotificationPriority.HIGH,
        f"{DISPLAY}: {e.get('title')}",
        (f"{payload['diplomat_name']} lays a letter before the Emperor — answer by "
         f"{_dateline(world, payload['answer_by_turn'])}."),
        int(turn),
        # S14C-X14: the button opens THIS letter (`/mailbox/activate` with its
        # mailbox id — main.gd's `moment_letter` review target), one click
        # beside a standing settlement offer.
        details={"moment_id": mid, "mailbox_id": int(dialogue.get("mailbox_id") or 0),
                 "route_id": str(int(dialogue.get("mailbox_id") or 0)),
                 "review_target": "moment_letter", "review_label": "Read the letter"}))
    _log(world, "arrived", e, answer_by_turn=int(payload["answer_by_turn"]),
         **_affair_fields(mid, state_row))
    return dialogue


def tick(world) -> List[str]:
    """The morning's moments, sited in `_advance_turn_internal` after the
    intent movements (`current_turn` is already the new morning). Unarmed:
    returns [] at once. Returns the ids delivered this morning (at most one,
    R3). No draw at tick time. RE-1: the affairs' tick follows the moments'
    (`_affairs_tick`) — [] while the recurring deck is unarmed, so the
    shipped boot's mornings are the mornings they were."""
    if not armed(world):
        return []
    try:
        delivered = _tick(world)
    except Exception as exc:
        report(exc, "moments.tick: the morning's moments")
        delivered = []
    try:
        return list(delivered) + _affairs_tick(world, delivered)
    except Exception as exc:
        report(exc, "moments.tick: the morning's affairs")
        return list(delivered)


def _affairs_tick(world, delivered: List[str]) -> List[str]:
    """RE-1 (RECURRING_EVENTS_SPEC.md §7, §9): after `_tick` returns — a
    standing affair withdrawn free when a moment arrived this morning, then
    `affairs.deliver_due`, then the courts' (inert) resolution. [] on a world
    whose block authors no `affairs` deck."""
    from backend.game_logic import affairs
    if not affairs.armed(world):
        return []
    affairs.withdraw_standing(world, delivered)
    out = affairs.deliver_due(world, delivered)
    affairs.resolve_courts(world)
    return out


def _tick(world) -> List[str]:
    turn = _turn(world)
    state = _state(world)
    from backend.game_logic import game_end
    verdict = game_end.verdict_turn(world)
    candidates: List[Tuple[int, int, Dict[str, Any], int]] = []
    for index, e in enumerate(deck(world)):
        mid = str(e["id"])
        if mid in state:
            continue
        gate = road_gate(world, e)
        if gate == GATE_FORSWORN:
            _pass(world, e, PASS_FORSWORN, turn)
            continue
        span = window(world, e)
        if span is None:
            continue
        lo, hi = span
        if e.get("lag") is not None and verdict is not None and lo >= int(verdict):
            _pass(world, e, PASS_VERDICT, turn)
            continue
        if turn > hi:
            if was_due(world, mid):
                _crowd_out(world, e, turn)        # S14C-X24: due once, it ends on screen
            else:
                _pass(world, e, PASS_PREMISE, turn)   # silent — nothing was promised
            continue
        if turn < lo or gate != GATE_OPEN:
            continue
        if not premise(world, e):
            if turn >= hi and was_due(world, mid):
                _crowd_out(world, e, turn)        # S14C-X24: its last morning — due once, on screen
            continue
        candidates.append((lo, index, e, hi))
    if not candidates:
        return []
    candidates.sort(key=lambda c: (c[0], c[1]))
    rules = pacing(world)
    # RE-1 (§7): the moments' own rows alone — blind to every affair, so an
    # affair never delays, crowds out or shifts a moment.
    rows = list(moment_rows(state).values())
    open_letters = sum(1 for r in rows if r.get("status") == STATUS_FIRED)
    arrivals = [int(r.get("turn", 0) or 0) for r in rows if r.get("status") in ARRIVED_STATUSES]
    gap_ok = not arrivals or turn - max(arrivals) >= int(rules["min_gap"])
    from backend.game_logic.war_council import foreground_in_tenure
    crisis = foreground_in_tenure(world)
    delivered: List[str] = []
    for _lo, _index, e, hi in candidates:
        if not delivered and not crisis and open_letters < int(rules["max_open"]) and gap_ok:
            deliver_letter(world, e, turn)
            delivered.append(str(e["id"]))
        elif turn >= hi:
            _crowd_out(world, e, turn)
        else:
            _mark_due(world, e, turn)             # S14C-X24: deferred while due — remembered
    return delivered


# ════════════════════════════════════════════════════════════════════════
# The backfill — a pre-S14c save (the record §3.5)
# ════════════════════════════════════════════════════════════════════════

def backfill_store(world, data: Dict[str, Any], seed: str) -> Dict[str, Any]:
    """The store a pre-S14c save gains from its scenario's shipped block,
    resolved with the save's own seed (the boot's resolver); a windowed
    entry whose window closed by the save turn, or a causal entry whose
    anchor + lag is at or before it, is written `passed(before_save)` —
    nothing fires retroactively. {} when the scenario authors none."""
    raw = (data or {}).get("moments")
    if not isinstance(raw, dict):
        return {}
    block = copy.deepcopy(raw)
    from backend.game_logic.campaign_variance import resolve_moment_turns
    resolve_moment_turns(block, seed)
    store = from_block(block)
    if not store:
        return {}
    saved = _turn(world)
    previous = getattr(world, "moments", None)
    world.moments = store
    try:
        for e in deck(world):
            span = window(world, e)
            if span is None:
                continue
            lo, hi = span
            if (e.get("lag") is not None and lo <= saved) or (e.get("lag") is None and hi <= saved):
                _pass(world, e, PASS_BEFORE_SAVE, saved)
    finally:
        world.moments = previous
    return store


BACKFILL_LEAD = 3    # RE-1 (§11): a backfilled deck's first letter waits three mornings


def backfill_affairs(world, data: Dict[str, Any]) -> bool:
    """RE-1 (RECURRING_EVENTS_SPEC.md §11): a pre-RE save whose scenario NOW
    authors `moments.affairs` gains the deck — every streak at 0 and the
    first letter no sooner than the save turn + 3 (`not_before`); nothing
    fires retroactively. False when the scenario authors none, the save
    carries no moments store, or the store already carries the deck."""
    store = _store(world)
    block = store.get("block") if isinstance(store.get("block"), dict) else None
    moments = (data or {}).get("moments")
    authored = moments.get("affairs") if isinstance(moments, dict) else None
    if block is None or not isinstance(authored, dict) or not authored.get("deck"):
        return False
    if isinstance(block.get("affairs"), dict) and block["affairs"].get("deck"):
        return False
    block["affairs"] = copy.deepcopy(authored)
    runtime = store.get("affairs") if isinstance(store.get("affairs"), dict) else {}
    runtime["not_before"] = _turn(world) + BACKFILL_LEAD
    store["affairs"] = runtime
    return True
