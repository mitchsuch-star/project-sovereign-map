"""S14d "The Table Lesson" — the first-open lines (`docs/TABLE_LESSON_SPEC.md`
§2–§3; Pre-Deploy S14d part 1, October 23, 2026).

Seven action screens name the mechanic they show the first time they open —
one short line, once per campaign, latched in the save:

    cabinet          the Cabinet's step 1 and step 2 (`GET /diplomatic_preview`)
    designs          the Emperor's Designs road page (`GET /imperial_designs`)
    formables        the Formable Nations page (`GET /formables`; the class
                     sweep of part 1's second landing, §0 Q3)
    settlement       every `settlement_confirm` dialogue (a PROPOSE and a REVIEW form)
    separate_peace   the pair-substitute chooser, peace arm only
    laws             the Strategic Ledger's eighth book
    admiralty_camp   the Admiralty's fleet block, only where camp provinces are authored
    moment_letter    the moment letter (`incoming_proposal` with `is_moment`)

The muster is not here: `what_if_line` rides every muster road (S14D-X4).

THE RULES (§0 Q2):
- The store is `world.first_opens: {screen: turn}` on the shared `to_dict` line.
- A line is ATTACHED at the response edge, on a copy — never inside a stored
  dialogue — and only while unlatched: a read is not a showing
  (`objection_v2.py:908-917`).
- The client prints the line at the head of the surface when it first draws
  and acknowledges it once through `POST /first_open`; the acknowledgement is
  the showing and sets the latch (`mark_seen`).
- Every line is a function of the live constants, ≤ `LINE_CAP` characters,
  "Sire" in its opening, no quoted diplomatic order (`_TYPED`), no outcome
  the board can shut stated as certain.

Nothing here reads a mechanic or writes one (GR6); the census in
`tests/test_first_open.py` pins that no module outside this one and
`world_state.py` touches `first_opens`.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, Mapping, Optional, Tuple

SCREENS: Tuple[str, ...] = (
    "cabinet", "designs", "formables", "settlement", "separate_peace",
    "laws", "admiralty_camp", "moment_letter",
)
LINE_CAP = 220
KEY = "first_open"


# ── the lines (§2) ─────────────────────────────────────────────────────────

def _line_cabinet(world, ctx: Optional[Mapping[str, Any]]) -> str:
    return ("Any court may be treated with here, Sire — ally, neutral or foe. "
            "Each act is priced in diplomatic points (DP), which return every "
            "turn; I read the court and name the price before you choose.")


def _line_designs(world, ctx: Optional[Mapping[str, Any]]) -> str:
    from backend.game_logic.imperial_designs import PROCLAIM_ADMIN_COST, PROCLAIM_DP_COST
    admin = "action" if int(PROCLAIM_ADMIN_COST) == 1 else "actions"
    return ("Your own aims, Sire, not the courts'. A road asks a construction, "
            "then a seal; hold both and the peace that seals it can be the "
            f"Decisive Peace. Proclaiming costs {int(PROCLAIM_DP_COST)} DP and "
            f"{int(PROCLAIM_ADMIN_COST)} administrative {admin} and cannot be undone.")


def _line_formables(world, ctx: Optional[Mapping[str, Any]]) -> str:
    # The class sweep (§0 Q3, second landing): the page's standing prompt names
    # the requirements and not what forming DOES. Class C is carved at the
    # table and born the carver's client (`formations.create_client`: loyalty,
    # the satellite's tribute, "marches when the sponsor calls"); Class T
    # forms by conquest and stands free (a vassal cannot form).
    return ("States not yet on the map, Sire; each row names what its birth "
            "requires. One carved at the table is born your client — it pays "
            "tribute and marches when you call; one that forms by conquest "
            "rises free.")


def _line_settlement(world, ctx: Optional[Mapping[str, Any]]) -> str:
    from backend.game_logic.settlement_scoring import ACCEPTANCE_THRESHOLD
    mode = str((ctx or {}).get("mode") or "").upper()
    head = ("This is the table, Sire. Every court seated here signs for itself — "
            f"each must reach {int(ACCEPTANCE_THRESHOLD)} or the draft will not carry")
    if mode == "PROPOSE":
        return (head + ". Demand more of a court, ease it, or drop it to fight on; "
                "a court that is ready may be taken alone.")
    return (head + "; the verdict beside each row is that court's own, and the "
            "terms before you stand as offered.")


def _line_separate_peace(world, ctx: Optional[Mapping[str, Any]]) -> str:
    return ("A separate peace, Sire, takes this one court out of the war while "
            "the rest fight on. The allies fighting beside you in it are carried "
            "in; an ally still at war with her is left fighting, and resents it.")


def _line_laws(world, ctx: Optional[Mapping[str, Any]]) -> str:
    from backend.game_logic.reforms import ARREARS_WINDOW_TURNS
    return ("Laws are acts of state, Sire: bought once, then paid in gold every "
            "turn. When the chest cannot pay, the heaviest upkeep lapses first; a "
            f"lapsed law returns within {int(ARREARS_WINDOW_TURNS)} turns at half "
            "its price plus the arrears.")


def _line_admiralty_camp(world, ctx: Optional[Mapping[str, Any]]) -> str:
    from backend.game_logic.naval import (
        DESCENT_CAMP_MIN_TROOPS, DESCENT_CAMP_STAGED_TURNS, WINDOW_TURNS,
    )
    # S14E-13's sweep: a march out of the camp resets the count — said here
    # too, within the cap (Britain's recall was cut; the lifted blockade stays).
    return (f"The camp, Sire: {int(DESCENT_CAMP_MIN_TROOPS):,} men on the Channel "
            f"coast, {int(DESCENT_CAMP_STAGED_TURNS)} turns at war with Britain, "
            "stage a descent — no order; a march out resets the count. Her "
            "blockade on you lifts; a won Diversion can open the Strait for up to "
            f"{int(WINDOW_TURNS)} turns.")


def _line_moment_letter(world, ctx: Optional[Mapping[str, Any]]) -> str:
    return ("A moment of history, Sire: a decision the record sets before you — "
            "two answers, each priced below, or Not Now to set it aside. It waits "
            "this turn and the next; left unanswered, it takes the second answer "
            "for you.")


LINES: Dict[str, Callable[[Any, Optional[Mapping[str, Any]]], str]] = {
    "cabinet": _line_cabinet,
    "designs": _line_designs,
    "formables": _line_formables,
    "settlement": _line_settlement,
    "separate_peace": _line_separate_peace,
    "laws": _line_laws,
    "admiralty_camp": _line_admiralty_camp,
    "moment_letter": _line_moment_letter,
}


# ── the store (§3) ─────────────────────────────────────────────────────────

def seen(world) -> Dict[str, int]:
    """The store, as a dict (created on the world if a legacy object lacks it)."""
    store = getattr(world, "first_opens", None)
    if not isinstance(store, dict):
        store = {}
        world.first_opens = store
    return store


def is_seen(world, screen: str) -> bool:
    return screen in seen(world)


def line_for(world, screen: str, ctx: Optional[Mapping[str, Any]] = None) -> str:
    """The screen's line while unlatched, and on every payload of the TURN it
    was first shown (a settlement dial restages the table, a ledger refreshes
    its books — the line must not vanish mid-read); "" on any later turn or
    for an unknown id. A pure read."""
    if screen not in LINES:
        return ""
    stamped = seen(world).get(screen)
    if stamped is not None and int(stamped) != int(getattr(world, "current_turn", 0) or 0):
        return ""
    return str(LINES[screen](world, ctx) or "")


def attach(payload: Dict[str, Any], world, screen: str,
           ctx: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    """Set `payload["first_open"] = {"screen", "line"}` while unlatched. The
    caller passes a FRESH dict (a GET's return, a builder's output, a copy
    at the response edge) — never a stored dialogue."""
    if not isinstance(payload, dict):
        return payload
    line = line_for(world, screen, ctx)
    if line:
        payload[KEY] = {"screen": screen, "line": line}
    return payload


def dialogue_screen(dialogue: Mapping[str, Any]) -> Tuple[Optional[str], Dict[str, Any]]:
    """Which screen a dialogue-borne payload opens, and the line's context."""
    if not isinstance(dialogue, Mapping):
        return None, {}
    dtype = str(dialogue.get("type") or dialogue.get("dialogue_type") or "")
    if dtype == "settlement_confirm":
        return "settlement", {"mode": str(dialogue.get("dialogue_mode") or "")}
    if dtype == "settlement_pair_substitute_confirm":
        if str(dialogue.get("proposal_type") or "") == "peace":
            return "separate_peace", {}
        return None, {}
    payload = dialogue.get("popup_payload")
    is_moment = bool(dialogue.get("is_moment")) or (
        isinstance(payload, Mapping) and bool(payload.get("is_moment")))
    if is_moment and dtype in ("", "incoming_proposal"):
        return "moment_letter", {}
    return None, {}


def with_line(world, dialogue):
    """The response-edge helper: a SHALLOW COPY of `dialogue` carrying its
    line while unlatched; the same object (untouched) otherwise. The stored
    dialogue never gains the key, so a re-serve after the acknowledgement
    carries none."""
    if not isinstance(dialogue, dict):
        return dialogue
    screen, ctx = dialogue_screen(dialogue)
    if screen is None:
        return dialogue
    line = line_for(world, screen, ctx)
    if not line:
        return dialogue
    out = dict(dialogue)
    out[KEY] = {"screen": screen, "line": line}
    return out


def mark_seen(world, screen: str) -> bool:
    """The acknowledgement: stamp the turn (idempotent), refuse an unknown id,
    and strip a stray key from any dialogue the manager holds."""
    if screen not in SCREENS:
        return False
    store = seen(world)
    if screen not in store:
        store[screen] = int(getattr(world, "current_turn", 0) or 0)
    _strip_stored(world)
    return True


def _strip_stored(world) -> None:
    dm = getattr(world, "dialogue_manager", None)
    if dm is None:
        return
    held = []
    for attr in ("current", "_current", "queue", "_queue"):
        value = getattr(dm, attr, None)
        if isinstance(value, dict):
            held.append(value)
        elif isinstance(value, (list, tuple)):
            held.extend(v for v in value if isinstance(v, dict))
    for d in held:
        d.pop(KEY, None)
