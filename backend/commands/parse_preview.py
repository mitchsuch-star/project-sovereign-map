"""UI-6 "The readback" (Session UI-6, November 13, 2026) — `GET /parse_preview`.

How a typed line WOULD be read, before Enter: the marshal, the verb, the
target, the price in actions, the clock, whether he may object, or why it
would be refused — never executed. The client prints one short row under the
command line ("▸ Ney · attack Mack (Swabia) · 1 action · he may object").

THE CONTRACT (`docs/SYSTEMS_REFERENCE.md` §217; design brief §1):

* NEVER EXECUTES. It mirrors only the PURE stages of `/command`
  (`main.execute_command`): the typed `why`, the context carryover
  (`resolve_context_references`, which writes nothing — the history append
  is skipped), the lost-marshal guard, the premise split, the parse, and the
  delegation / collective DETECTORS. Every stage that answers a pending
  question, appends history, registers a clarification, relays a tail or
  calls the executor is skipped; a standing question is detected and said
  ("pending"), never answered.
* NO MODEL (Golden Rule 6). A dedicated mock-only parser (`_PreviewLLM`) under
  a lock — its own instance, because `LLMClient._condition_handoff` is
  per-parse instance state. When the LIVE client would consult the model for
  this line (its own `_should_fallback_to_llm`, or the CR-2 retry) the reading
  is "secretary" and nothing is quoted: the model's answer is never produced.
* NO SIDE EFFECTS. No action spent, no history, no popup, no trace (the parse
  runs with the trace contextvar cleared), no random draw (every evaluator
  that can roll runs behind `order_quotes._without_spending_the_dice`).
* THE DOCTRINE (R5; `llm_client._askable_enemy_names`, pinned by
  `tests/test_crt2_the_name_is_never_replaced.py`). Naming a commander is no
  fog secret the game keeps — his NAME and his SIDE are public; his POSITION
  is the fogged half. So a foreign commander out of sight is read exactly as
  `/command` reads him (the enemy-addressee refusal by name and court, "no
  intelligence on his position", the parser's own typo reading), and the
  reading never carries where he stands or what he fields: `target_place`
  only for a commander IN SIGHT (THE one rule, `intel_surfaces.in_sight`),
  and no quote, distance, turn count, strength or figure is ever read off a
  man out of sight (`_unseen_reading`). A name on NO roster yields
  `_unknown_reading`, built from the player's own typed token and the pool
  he can see (his marshals, the foes in sight, the provinces).
* A WHITELIST, every number `int()` (Golden Rule 2): the output is built key
  by key (`_base`), never pruned from the parse.
* BUSY while a POST holds the state lock (GETs are lock-free; an end turn can
  mutate for seconds) or another preview holds this one's lock.
* RULE 8: `get_llm_game_state` (a whole-board scan) is cached per state epoch
  (`_CACHE`, keyed on the epoch plus the cheap board figures); the fog sets
  and the quotes are read fresh per request.
"""

from __future__ import annotations

import contextlib
import io
import re
import threading
from typing import Any, Callable, Dict, List, Optional

from backend.ai import parse_trace as _ptrace
from backend.ai.llm_client import LLMClient
from backend.display_names import humanize_entity_name
from backend.errors import report

KINDS = ("order", "question", "meta", "cabinet", "delegation", "refusal",
         "unknown_name", "needs_marshal", "secretary", "pending", "busy", "none")

_LOCK = threading.Lock()
_LOCK_WAIT_S = 0.4
_PARSER: Dict[str, Any] = {"parser": None}
_CACHE: Dict[str, Any] = {"key": None, "state": None}

# The executor's never-priced verbs (`executor.py`'s local `free_actions`,
# order verbs only; pinned against that list by tests/test_parse_preview.py).
_FREE_ORDER_ACTIONS = frozenset({"retreat", "wait", "break_square"})
# A question or a report at the desk — never an order.
_REPORT_ACTIONS = frozenset({"help", "status", "economy", "treasury", "finances"})
# The verbs a reading prints in the imperative (anything else humanised).
_VERB_WORDS = {
    "attack": "attack", "move": "move to", "march": "march to", "scout": "scout",
    "fortify": "fortify", "unfortify": "unfortify", "drill": "drill",
    "defend": "defend", "hold": "hold", "pursue": "pursue", "support": "support",
    "follow": "follow", "garrison": "garrison", "retreat": "fall back",
    "land": "land in", "recruit": "recruit", "build": "build", "repair": "repair",
    "charge": "charge", "restrain": "restrain", "cancel": "cancel his order",
    "wait": "wait", "form_square": "form square", "break_square": "break square",
    "stance_change": "change stance", "recruit_marshal": "commission a marshal",
    "recall_marshal": "recall", "purchase_levy": "buy substitutes",
    "grant_pension": "grant a rente", "revoke_pension": "revoke a rente",
    "grant_dotation": "endow", "build_fleet": "lay down ships",
    "set_fleet_posture": "set the fleet's posture",
    "naval_diversion": "order the diversion", "enact_law": "enact a law",
    "army": "name an army", "set_war_goal": "name the war goal",
    "repeal_law": "repeal a law",
}
_STRATEGIC_VERBS = {"MOVE_TO": "march", "PURSUE": "pursue", "HOLD": "hold"}
_TARGET_VERBS = frozenset({"attack", "pursue", "march", "move", "scout",
                           "support", "follow", "land"})
# The parser's PARSE-NEG refusals, each in fixed short words (never the clause).
_REFUSAL_COPY = {
    "conditional": "a contingency — Berthier cannot hold it; give the order for today",
    "condition": "that condition cannot be held",
    "reason": "that reports the enemy but gives no order",
    "contradiction": "it orders and forbids the same thing",
    "deferral": "orders cannot be held for a later day",
    "fleet_is_no_corps": "a fleet is no corps",
    "stand_down_is_no_order": "“stand down” is no order — say hold",
    "no_letter_asks_for_men": "no letter asks a court for men",
}
_REFUSAL_DEFAULT = "no order goes out"


# ── the output: a whitelist, every number an int ─────────────────────────────

def _base(line: str, epoch: int) -> Dict[str, Any]:
    return {
        "success": True, "line": line, "epoch": int(epoch), "kind": "none",
        "parts": [], "marshal": "", "verb": "", "action": "", "strategic": False,
        "target": "", "target_kind": "none", "target_place": "",
        "ap": 0, "ap_left": 0, "pool": "none", "free": False, "ok": False,
        "refusal": "", "turns": 0, "objection": "none", "replaces": "",
        "asks_first": False, "would_consult_llm": False, "slot": "",
        "unknown": "", "candidates": [], "command": "",
        # Row IC: the line is an order to several corps — Enter opens its list.
        "directive": False,
        # Row IC, Session 2 (IC-8): the line restated WITHOUT the parts that
        # were not taken — what Enter sends while a "Not taken" row blocks.
        "understood": "",
    }


def _part(role: str, text: str) -> Dict[str, str]:
    return {"role": role, "text": str(text)}


def _cost_text(ap: int, pool: str, free: bool) -> str:
    if free or int(ap) <= 0:
        return "free"
    noun = "admin action" if pool == "admin" else "action"
    return f"1 {noun}" if int(ap) == 1 else f"{int(ap)} {noun}s"


def _turns_text(turns: int) -> str:
    return "1 turn" if int(turns) == 1 else f"{int(turns)} turns"


# ── caches and the dedicated parser ──────────────────────────────────────────

def invalidate() -> None:
    """Drop the cached parse state (a test that stages the board directly)."""
    _CACHE["key"] = None
    _CACHE["state"] = None


def _state_key(world, epoch: int):
    return (id(world), int(epoch), int(getattr(world, "current_turn", 0) or 0),
            int(getattr(world, "actions_remaining", 0) or 0),
            int(getattr(world, "admin_actions_remaining", 0) or 0),
            len(getattr(world, "command_history", None) or ()),
            tuple((m.name, m.location, int(m.strength or 0))
                  for m in (getattr(world, "marshals", None) or {}).values()))


def _llm_state(world, llm_state: Callable[[], Dict], epoch: int) -> Dict:
    """`main.get_llm_game_state` (a whole-board scan), once per state epoch
    (Rule 8). Its `enemies` are fog-filtered; staleness is safe because the
    gate below reads fresh fog."""
    key = _state_key(world, epoch)
    if _CACHE["key"] != key or _CACHE["state"] is None:
        _CACHE["state"] = llm_state()
        _CACHE["key"] = key
    return _CACHE["state"]


class _PreviewLLM(LLMClient):
    """The mock chain only — and a record of whether the LIVE client would
    have consulted the model for this line. Never calls a provider."""

    def __init__(self):
        super().__init__(use_real_api=False)
        self.live = None
        self.would_consult = False

    def parse_command(self, command_text: str, game_state: Optional[Dict] = None) -> Dict:
        fast = self._parse_with_mock(command_text, game_state)
        live = self.live
        if live is not None:
            try:
                if live._should_fallback_to_llm(fast, game_state):
                    self.would_consult = True
            except Exception as exc:
                report(exc, "parse_preview._PreviewLLM.parse_command: the live gate")
        return fast.to_dict()

    def reparse_with_llm(self, command_text: str, game_state: Optional[Dict],
                         fast_result_dict: Optional[Dict]):
        """CR-2's one forced retry: the live road would consult the model
        here (`LLMClient.reparse_with_llm`'s own conditions); the preview
        records it and declines."""
        live = self.live
        if (live is not None and getattr(live, "provider_name", "mock") != "mock"
                and getattr(live, "api_key", None) and isinstance(game_state, dict)
                and not (fast_result_dict or {}).get("llm_error")):
            self.would_consult = True
        return None, False


def _preview_parser():
    if _PARSER["parser"] is None:
        with contextlib.redirect_stdout(io.StringIO()):
            from backend.commands.parser import CommandParser
            parser = CommandParser(use_real_llm=False)
            parser.llm = _PreviewLLM()
        _PARSER["parser"] = parser
    return _PARSER["parser"]


# ── the view the reading may rest on ─────────────────────────────────────────

class _View:
    """The board as the player sees it: his own marshals, the foreign
    commanders IN SIGHT (`seen` — a reading may say where they stand), and
    the rest (`hidden` — named, never placed). Computed fresh per request —
    O(marshals)."""

    def __init__(self, world):
        # THE one sighting rule (RR6-X3 rule 1, `intel_surfaces.in_sight`) —
        # what `get_visible_enemies`, the map and the desk read.
        from backend.game_logic.intel_surfaces import in_sight
        self.world = world
        self.player = getattr(world, "player_nation", None)
        roster = getattr(world, "marshals", None) or {}
        self.own = {n: m for n, m in roster.items() if getattr(m, "nation", None) == self.player}
        self.seen = {n: m for n, m in roster.items()
                     if getattr(m, "nation", None) != self.player
                     and in_sight(world, self.player, m)}
        self.hidden = {n for n, m in roster.items()
                       if getattr(m, "nation", None) != self.player and n not in self.seen}

    def own_field(self) -> List[Any]:
        return [m for m in self.own.values()
                if int(getattr(m, "strength", 0) or 0) > 0 and not getattr(m, "captured_by", "")]

    def region(self, name: str) -> Optional[str]:
        if not name:
            return None
        region = self.world.get_region(name) if hasattr(self.world, "get_region") else None
        return getattr(region, "name", None) or (name if region is not None else None)


def mentions_hidden_name(world, line: str) -> bool:
    """Whether `line` names (any registered form, whole word, any case) a
    foreign commander the player cannot see. PURE — the history twin's oracle
    (a client never offers back a line it would have to withhold)."""
    try:
        view = _View(world)
        from backend.ai.llm_client import name_match_patterns
        low = str(line or "").lower()
        for name in view.hidden:
            for form in name_match_patterns(name):
                form = str(form).strip().lower()
                if form and re.search(r"(?<![\w'’-])" + re.escape(form) + r"(?![\w'’-])", low):
                    return True
    except Exception as exc:
        report(exc, "parse_preview.mentions_hidden_name: the scan")
        return True
    return False


def _typed_span(line: str, name: str) -> str:
    """The span of `line` the player typed for `name` (any registered form,
    longest first) — so an echo is the player's own spelling, never the
    roster's. A name the parse CORRECTED is not in the line: the word of the
    line nearest it (two edits at most) is what he typed; `name` itself only
    when nothing in the line comes near."""
    from backend.ai.llm_client import name_match_patterns
    from backend.ai.validation import _edit_distance_le2
    forms = sorted({str(f) for f in name_match_patterns(str(name))} | {str(name)},
                   key=len, reverse=True)
    for form in forms:
        if not form.strip():
            continue
        m = re.search(r"(?<![\w'’-])" + re.escape(form) + r"(?![\w'’-])", line or "", re.I)
        if m:
            return line[m.start():m.end()]
    low = humanize_entity_name(str(name)).lower()
    for word in re.findall(r"[A-Za-z][\w'’-]*", line or ""):
        if len(word) >= 3 and _edit_distance_le2(word.lower(), low):
            return word
    return str(name)


# ── the readings ─────────────────────────────────────────────────────────────

def _slot_for(token: str, line: str) -> str:
    """The register a name stands in, read off its POSITION in the line: at
    the head, the addressee."""
    from backend.ai.clause_guards import HONORIFIC
    head = re.match(r"^\s*(?:" + HONORIFIC + r")?" + re.escape(token) + r"(?![\w'’-])",
                    line or "", re.I)
    return "marshal" if head else "target"


def _unknown_reading(out: Dict[str, Any], token: str, line: str, view: _View,
                     verb: str = "") -> Dict[str, Any]:
    """THE ONE producer of unknown-name output — a name on no roster, or a
    slip the executor's seam asks about. Built from the player's own typed
    token and the pool he can see (his marshals, the foes in sight, the
    provinces) alone, so no candidate ever offers a man out of sight."""
    from backend.ai.validation import _edit_distance_le2
    # Whatever road led here, nothing it read survives: the reading is the
    # token and the pool alone, so every road reads the same.
    fresh = _base(out["line"], out["epoch"])
    out.clear()
    out.update(fresh)
    token = str(token or "").strip().strip(",.!?;:")
    # UI6-X66: a bare order ("Ney, march") carries the parser's GENERIC sentinel,
    # never a typed word — the readback printed "No foe or province 'generic'" (an
    # internal key, R7). It says what /command will ask: a destination.
    from backend.ai.generic_targets import is_generic_target
    if not token or is_generic_target(token):
        # UI6-X72: as `/command` meets it - a march that names nothing asks; a
        # verb that carries the nearest foe ("advance", "pursue") takes the
        # nearest IN SIGHT (no foe in sight asks, UI6-X63). Never a name.
        from backend.ai.strategic_parser import march_slot_is_empty, march_verb_stands_alone
        foes = [m for m in view.seen.values()
                if int(getattr(m, "strength", 0) or 0) > 0
                and view.world.is_at_war(view.player, m.nation)]
        chase = verb in ("pursue", "chase", "follow") or bool(
            re.search(r"\b(?:pursue|chase|hunt)\b", line or "", re.IGNORECASE))
        if march_slot_is_empty(line) or march_verb_stands_alone(line) or not foes:
            if chase:
                return _simple(out, "pending", ("head", "Whom? Name the one to pursue — Berthier will ask"))
            return _simple(out, "pending", ("head", "Where to? Name a destination — Berthier will ask"))
        word = "pursue" if chase else ("attack" if verb == "attack" else "march on")
        return _simple(out, "pending", ("head", f"{word} the nearest foe in sight — the staff picks him"),
                       ("cost", "priced when sent"))
    slot = _slot_for(token, line)
    if slot == "marshal":
        pool = [m.name for m in view.own_field()]
        head = f"No marshal ‘{token}’ of ours"
    else:
        pool = ([m.name for m in view.seen.values()] + [m.name for m in view.own_field()]
                + list((getattr(view.world, "regions", None) or {}).keys()))
        head = f"No foe or province ‘{token}’ in our sight"
    low = token.lower()
    ranked = []
    for index, name in enumerate(pool):
        shown = humanize_entity_name(name)
        cand = shown.lower()
        if not low or cand == low:
            continue
        if _edit_distance_le2(low, cand):
            ranked.append((0, index, shown))
        elif len(low) >= 2 and cand.startswith(low):
            ranked.append((1, index, shown))
    ranked.sort()
    candidates = []
    pattern = re.compile(r"(?<![\w'’-])" + re.escape(token) + r"(?![\w'’-])", re.I)
    for _rank, _index, shown in ranked[:3]:
        filled, n = pattern.subn(shown, line, count=1)
        if n:
            candidates.append({"label": shown, "line": filled})
    out.update(kind="unknown_name", slot=slot, unknown=token, candidates=candidates,
               parts=[_part("head", head)])
    return out


def _simple(out: Dict[str, Any], kind: str, *parts) -> Dict[str, Any]:
    out.update(kind=kind, parts=[_part(role, text) for role, text in parts])
    return out


def _pending_question(world, text: str, interrupt_reader=None) -> Optional[str]:
    """The standing question a typed line would be taken by (`/command`'s
    stages 2-4 and 9, DETECTED, never answered), or None.

    WS-14 (row IC, IC-8): it asks `/command`'s own readers. Berthier's
    clarification "stands" only for a line that ANSWERS it or withdraws it
    (`interpret_clarification_answer` — any other line lets the question go
    and is read as the order it is, exactly as stage 2 does); a marshal's
    interrupt stands only for a line stage 3 would take as its answer
    (`interrupt_reader`, the route's `main._interrupt_reading`). Before, the
    row called every line "this line answers it" / "answer it first" while
    Enter carried a fresh order out. With no `interrupt_reader` handed in (a
    caller outside the route) an interrupt that offers answers still claims
    every line — the cautious reading."""
    from backend.commands.clarification import (CLARIFICATION_DIALOGUE_TYPE,
                                                interpret_clarification_answer)
    low = text.strip().lower()
    dm = getattr(world, "dialogue_manager", None)
    top = dm.peek() if dm is not None else None
    if (isinstance(top, dict) and top.get("type") == CLARIFICATION_DIALOGUE_TYPE
            and not low.startswith("cheat ")):
        answer = str(interpret_clarification_answer(top, text).get("kind") or "pass")
        if answer == "cancel":
            return "Berthier’s question stands — this line withdraws the order"
        if answer == "command":
            return "Berthier’s question stands — this line answers it"
        # "pass": no answer — the question is let go and the line is read as
        # the order it is (a clarification never blocks).
    if (getattr(world, "pending_objection", None) is not None
            or getattr(world, "pending_strategic_objection", None) is not None):
        return "A question stands — answer it first"
    if dm is not None and dm.is_hard_stop():
        return "A question stands — answer it first"
    if interrupt_reader is not None:
        try:
            taken = interrupt_reader(world, text)
        except Exception as exc:
            report(exc, "parse_preview._pending_question: the interrupt's reader")
            taken = "A question stands — answer it first"
        if taken:
            return str(taken)
    else:
        for m in world.get_player_marshals():
            pending = getattr(m, "pending_interrupt", None)
            if pending and pending.get("options"):
                return "A question stands — answer it first"
    if getattr(world, "pending_capture_choice", None) and low.split()[:1] and \
            low.split()[0] in ("plunder", "secure", "confiscate", "respect"):
        return "A question stands — answer it first"
    dialogue = getattr(world, "pending_diplomatic_dialogue", None)
    if isinstance(dialogue, dict):
        options = dialogue.get("options") or []
        if not options and isinstance(dialogue.get("popup_payload"), dict):
            options = dialogue["popup_payload"].get("options") or []
        ids = {str(o.get("action") or "").strip().lower() for o in options if isinstance(o, dict)}
        # WS-7: `isdecimal` — a typed superscript is a digit and no number
        if (low.isdecimal() and 1 <= int(low) <= len(options)) or (low and low in ids):
            return "A letter waits — this line answers it"
    return None


def _first_sentence(text: str, cap: int = 90) -> str:
    first = re.split(r"(?<=[.!?])\s+", str(text or "").strip(), maxsplit=1)[0]
    return first if len(first) <= cap else first[:cap - 1].rstrip() + "…"


# ── the order reading: the reader the executor's own quotes are ─────────────

def _verb_of(parsed: Dict, command: Dict) -> str:
    action = str(command.get("action") or "")
    if parsed.get("is_strategic"):
        kind = str(parsed.get("strategic_type") or "")
        if kind == "SUPPORT":
            return "follow" if parsed.get("standing_follow") else "support"
        if kind in _STRATEGIC_VERBS:
            return _STRATEGIC_VERBS[kind]
    from backend.commands.state_probe import VERBS
    if action == "naval_expedition":
        return "land"
    if action in VERBS and VERBS[action][1] is None:
        return action
    return ""


def _target_entity(view: _View, target: str):
    """What a parsed target denotes: ("enemy", marshal) for a foreign
    commander IN SIGHT, ("unseen", marshal) for one out of sight (his name
    and court are public, his place is not — `_unseen_reading`),
    ("friendly", marshal) for one of ours, ("province", name), ("court",
    name) — or ("unknown", None) for a name on no roster."""
    if not target:
        return "none", None
    world = view.world
    marshal = world.get_marshal(target) if hasattr(world, "get_marshal") else None
    if marshal is not None:
        if marshal.name in view.own:
            return "friendly", marshal
        if marshal.name in view.seen:
            return "enemy", marshal
        return "unseen", marshal
    region = view.region(target)
    if region:
        return "province", region
    try:
        from backend.ai.nation_names import resolve_typed_nation
        nation = resolve_typed_nation(target, world)
        if nation:
            return "court", nation
    except Exception as exc:
        report(exc, "parse_preview._target_entity: resolve_typed_nation")
    return "unknown", None


def _court(world, nation: str) -> str:
    """A court as the reader sees it (a formed realm by its formed name)."""
    from backend.game_logic.formations import formed_display_name
    return formed_display_name(world, nation)


def _charge_gate(marshal) -> str:
    """UI6-X16's readback: the reason `_execute_charge` refuses this
    marshal's charge before it looks at any target — in short words — or ""."""
    if marshal is None:
        return ""
    recovering = getattr(marshal, "in_retreat_recovery", None)
    if callable(recovering) and recovering():
        return "recovering from the rout, he cannot charge"
    if not getattr(marshal, "is_reckless_cavalry", False):
        if not getattr(marshal, "cavalry", False):
            return "no cavalryman — only reckless cavalry charge"
        return "not reckless enough to charge"
    if int(getattr(marshal, "recklessness", 0) or 0) < 1:
        return "one victory as the attacker arms the charge"
    return ""


def _support_a_foreigner(world, foe, verb: str) -> str:
    """UI6-X17: support / follow aimed at a foreign commander, in the
    readback's short words — as `/command` says it: at war, he is the
    pursuit's ("pursue him, not support"); at peace, no friend of ours to
    support (and no pursuit stands — the peace refuses it)."""
    shown = humanize_entity_name(foe.name)
    court = _court(world, foe.nation)
    if world.is_at_war(getattr(world, "player_nation", None), foe.nation):
        return f"{shown} serves {court} — pursue him, not {verb}"
    return f"{shown} serves {court} — we are at peace; {verb} is for our own marshals"


def _attack_seam(out: Dict[str, Any], text: str, world, view: _View,
                 marshal) -> Optional[Dict[str, Any]]:
    """The executor's SF-V4 seam (`proper_name.attack_proper_name_ask`), which
    reads a typed attack's OBJECT off the raw words before its parsed target
    is read, mirrored in the readback's words: one of our own at the head is
    refused; "attack everything" asks whom; an object that names nobody on
    the board — a proper name on no roster, a slip of a name — is the
    unknown-name reading in the player's own spelling (the executor asks,
    naming only foes in sight); a foe's bench name has no position on the
    record. None: the attack goes on to its target."""
    from backend.commands import proper_name as pn
    if not pn.A_PROPER_NAME_ASKS:
        return None
    tail = pn.attack_tail(text)
    if tail is None:
        return None
    viewer = getattr(marshal, "nation", None) or view.player
    own = pn._own_marshal_at_head(tail, world, viewer)
    if own is not None:
        return _refusal_reading(out, f"{humanize_entity_name(own)} is one of ours — "
                                     f"he will not attack our own")
    if pn._EVERYTHING_RE.match(tail):
        return _refusal_reading(out, "Attack whom? — name the foe")
    name = pn.proper_name_in(tail, world, viewer)
    if name is None:
        return None
    benched = pn._bench(world, name, viewer)
    if benched is not None:
        return _refusal_reading(out, f"No intelligence on {humanize_entity_name(benched)}’s position")
    return _unknown_reading(out, name, text, view)


# The verbs `_unseen_reading` answers for a man out of sight (any other verb
# reads on with his name and nothing of his place). UI6-X20: + hold;
# UI6-X16: + charge.
_UNSEEN_VERBS = frozenset({"attack", "pursue", "march", "move", "scout",
                           "support", "follow", "hold", "charge"})


def _unseen_reading(out: Dict[str, Any], world, marshal, foe, verb: str,
                    strategic: bool) -> Dict[str, Any]:
    """A foreign commander OUT OF SIGHT, read as `/command` reads him (THE
    DOCTRINE — his name and court are public, his position is the fogged
    half): a province verb is told he is a commander, support is told whose
    man he is, and a chase is refused at peace, refused for want of a
    sighting, or — a sighting on the record — priced as the chase
    (`strategic.pursue_known_location`, the executors' one rule). Nothing of
    where he stands rides the reading: no `target_place`, no quote, no
    distance, no turn count, no strength."""
    from backend.commands import state_probe as sp
    from backend.commands.strategic import pursue_known_location
    shown = humanize_entity_name(foe.name)
    actor = humanize_entity_name(marshal.name)
    out.update(target=shown, target_kind="enemy", target_place="")
    court = _court(world, foe.nation)
    if verb in ("move", "scout", "march", "hold"):
        # `march` here is a march the strategic parser did not turn into a
        # pursuit (a court we are at peace with), and a HOLD at a man no
        # report places (UI6-X20): `/command` answers "X is a commander,
        # Sire, not a province".
        return _refusal_reading(out, f"{shown} is a commander — name a province")
    if verb in ("support", "follow"):
        return _refusal_reading(out, _support_a_foreigner(world, foe, verb))
    if not world.is_at_war(marshal.nation, foe.nation):
        return _refusal_reading(out, f"We are not at war with {court}")
    if verb == "charge" or (verb == "attack" and getattr(marshal, "artillery", False)):
        # UI6-X16: a charge, or guns that cannot chase, at a man out of
        # sight — `/command` refuses by name, free; no pursuit stands in.
        return _refusal_reading(out, f"No intelligence on {shown}’s position — scout for him first")
    refusal = sp.order_state_refusal(world, marshal, "pursue")
    if refusal:
        return _refusal_reading(out, f"{actor} — {refusal}")
    if not pursue_known_location(world, marshal, foe):
        return _refusal_reading(out, f"No intelligence on {shown}’s position — scout for him first")
    # A sighting on the record: a typed attack ASKS first and its yes is the
    # pursuit (DDB-R1); a standing pursuit is the order itself. Priced as the
    # chase; the sighting's province is the executor's to say, never ours.
    ap = int(sp.order_price(world, marshal, "pursue"))
    asks = verb == "attack" and not strategic
    out.update(kind="order", ok=True, ap=ap, pool="military", free=ap == 0,
               ap_left=int(getattr(world, "actions_remaining", 0) or 0),
               asks_first=asks, turns=0, objection="none")
    parts = [_part("head", f"{actor} · {'attack' if asks else 'pursue'} {shown}")]
    if asks:
        parts.append(_part("warn", f"asks first — {shown} is out of sight"))
        parts.append(_part("cost", f"{_cost_text(ap, 'military', False)} if confirmed"))
    else:
        parts.append(_part("cost", _cost_text(ap, "military", ap == 0)))
        parts.append(_part("warn", f"{shown} is out of sight — the chase follows his last sighting"))
    out["parts"] = parts
    return out


def _objection(world, marshal, verb: str, action: str, target: str) -> str:
    from backend.commands import order_quotes as oq
    from backend.commands.state_probe import VERBS, _BATTERY_ACTIONS
    strategic_type = VERBS.get(verb, (None, None))[1]
    if strategic_type:
        return oq._strategic_objection(world, marshal, strategic_type, target or "", [])
    if action in _BATTERY_ACTIONS:
        return oq._tactical_objection(world, marshal, action, target or "")
    return "none"


def _order_reading(out: Dict[str, Any], world, view: _View, parsed: Dict,
                   text: str) -> Dict[str, Any]:
    from backend.commands import order_quotes as oq
    from backend.commands import state_probe as sp
    from backend.commands.meta_executor import ADMIN_ACTIONS
    command = parsed.get("command") or {}
    action = str(command.get("action") or "")
    marshal = view.own.get(str(command.get("marshal") or ""))
    shown = humanize_entity_name(marshal.name)
    verb = _verb_of(parsed, command)
    target = str(command.get("target") or "")
    out.update(marshal=shown, action=action, verb=verb or action,
               strategic=bool(parsed.get("is_strategic")))
    # UI6-X25: a stationary / in-place verb aimed at a COMMANDER is refused
    # free by `/command` ("Kutuzov is a commander, Sire, not a place").
    from backend.commands import exit_predicate as _xp
    _not_a_place = _xp.commander_object_pre_check(
        dict(command, marshal=marshal.name), action, world, raw=text)
    if _not_a_place is not None and not parsed.get("is_strategic"):
        return _refusal_reading(out, str(_not_a_place["message"]).replace(
            " Nothing has been relayed.", "").replace("Sire, not a place", "not a place"))
    # UI6-X67: "retreat from <a province he is not in>" - `/command` refuses it
    # free (`retreat_from_pre_check`); his own province reads "fall back from".
    retreat_from = ""
    retreat_stated = ""
    if action == "retreat" and not parsed.get("is_strategic"):
        _elsewhere = _xp.retreat_from_pre_check(
            dict(command, marshal=marshal.name), action, world, raw=text)
        if _elsewhere is not None:
            return _refusal_reading(out, str(_elsewhere["message"]).replace(
                " Nothing has been relayed.", "").replace(", Sire —", " —"))
        if _xp.retreat_from_region(text, world) == marshal.location:
            retreat_from = humanize_entity_name(marshal.location)
        retreat_stated = str(_xp.retreat_stated_destination(text) or "")
        # the from-phrase's word is never a destination ("retreat from Austria")
        if retreat_from or not target or _xp.retreat_from_place(text, target):
            target = retreat_stated
    kind, entity = _target_entity(view, target) if target else ("none", None)
    if parsed.get("target_placed_by_the_game"):
        kind, entity = "none", None
    # A standing order's destination reads the PROVINCE first where a name is
    # both (WO-13's collision, "Brunswick"): `_classify_target` and the HOLD
    # road do.
    if verb in ("hold", "march", "scout") and kind in ("enemy", "unseen", "friendly") \
            and view.region(target):
        kind, entity = "province", view.region(target)
    # A name on NO roster: the reading rests on the player's own word.
    if target and kind == "unknown" and (verb in _TARGET_VERBS or action == "attack"):
        return _unknown_reading(out, _typed_span(text, target), text, view, verb=verb or action)
    # UI6-X72: a move that names nothing ("Ney, move", "Ney, go") asks where, free
    # (`/command`'s CX3-R2 ask) - the readback priced it as an order.
    if action == "move" and not target and not parsed.get("is_strategic"):
        return _simple(out, "pending", ("head", "Where to? Name a destination — Berthier will ask"))
    # UI6-X16's readback: a charge meets `_execute_charge`'s own gates first
    # (it read as a priced order for any marshal — "Ney · charge Mack").
    if action == "charge":
        gate = _charge_gate(marshal)
        if gate:
            return _refusal_reading(out, f"{shown} — {gate}")
        # UI6-X29: then the target gates `_execute_charge` meets — no target
        # at all ("Charge requires a target"), a province with no foe at war
        # IN SIGHT in it ("Cannot find target"; a province that hides a man
        # out of sight reads as an empty one, UI6-X28).
        if kind == "none":
            return _refusal_reading(out, f"{shown} — a charge needs a target — name the foe")
        if kind == "court":
            # UI6-X38: `/command` — "Cannot find target 'Bavaria' for Glorious
            # Charge.", free: a court is no man to ride at.
            return _refusal_reading(
                out, f"{shown} — cannot find {humanize_entity_name(entity)} to charge — name the foe")
        if kind == "province":
            held = any(m.location == entity and world.is_at_war(marshal.nation, m.nation)
                       for m in view.seen.values())
            if not held:
                return _refusal_reading(
                    out, f"{shown} — no foe in sight to charge at {humanize_entity_name(entity)}")
    # Row IC (found by the directive's fuzz): a scout beyond his reach is
    # refused free by `_execute_scout` ("Bern is too far to scout") — ONE
    # source, `movement_executor.scout_range`; it read as a priced order.
    if action == "scout" and kind == "province" and not parsed.get("is_strategic"):
        from backend.commands.movement_executor import scout_range
        _gap = world.get_distance(marshal.location, entity)
        _reach = int(scout_range(marshal))
        if isinstance(_gap, int) and _gap > _reach:
            return _refusal_reading(
                out, f"{shown} — {humanize_entity_name(entity)} is too far to scout "
                     f"(he scouts within {_reach} marches)")
    # Row IC (found by the directive's fuzz): `form_square` meets the executor's
    # own pre-validation (`executor.py` FORM_SQUARE PRE-VALIDATION /
    # `_execute_form_square`) — it read as a priced order for a cavalryman.
    if action == "form_square":
        # (ONE reader with the executor and the button — row IC, IC-7)
        from backend.commands.tactical_executor import square_refusal
        _no_square = square_refusal(marshal)[1]
        if _no_square:
            return _refusal_reading(out, f"{shown} — {_no_square}")
    # UI6-X29: the guns' verb read as `/command` reads it — a marshal with no
    # guns cannot bombard (the executor's free refusal), whatever he is aimed at.
    if action == "attack" and not getattr(marshal, "artillery", False):
        from backend.commands import proper_name as _pn
        if _pn.attack_verb(text) == "bombard":
            return _refusal_reading(out, f"{shown} commands no guns — he cannot bombard")
    # UI6-X38: guns aimed at a PROVINCE beyond their reach — `/command`'s free
    # "Target out of range … adjacent regions" (no pursuit stands in for guns).
    if (action == "attack" and kind == "province"
            and getattr(marshal, "artillery", False)
            and world.get_distance(marshal.location, entity) > marshal.movement_range):
        return _refusal_reading(
            out, f"{shown} — target out of range; guns engage only adjacent provinces")
    # UI6-X37: a word two commanders share ("Archduke") opens `/command`'s
    # free ask — never the bare attack on the nearest man.
    if action == "attack" and not target:
        from backend.commands.combat_executor import shared_name_word_in
        _word = shared_name_word_in(text, world, marshal)
        # UI6-X61: its unique bearer IN SIGHT is the man named (`/command` acts
        # on him); none in sight, or several, opens the ask.
        from backend.commands.combat_executor import unique_bearer_in_sight
        _bearer = unique_bearer_in_sight(world, marshal, _word) if _word else None
        if _bearer is not None:
            target = _bearer.name
            out.update(target=humanize_entity_name(_bearer.name))
            kind, entity = _target_entity(view, target)
        elif _word:
            _typed = re.search(r"(?<![\w'’-])" + re.escape(_word) + r"(?![\w'’-])",
                               text, re.IGNORECASE)
            return _unknown_reading(out, _typed.group(0) if _typed else _word, text, view)
    # UI6-X60: the same reach for guns aimed at a NAMED commander in sight.
    if (action == "attack" and kind == "enemy" and getattr(marshal, "artillery", False)
            and world.get_distance(marshal.location, entity.location) > marshal.movement_range):
        from backend.commands import proper_name as _pn2
        if _pn2.attack_verb(text) == "bombard":
            return _refusal_reading(
                out, f"{shown} — target out of range; guns engage only adjacent provinces")
    # A commander out of sight: his name and court, never his place.
    if kind == "unseen" and (verb in _UNSEEN_VERBS or action in ("attack", "charge")):
        return _unseen_reading(out, world, marshal, entity, verb or action,
                               bool(parsed.get("is_strategic")))
    target_shown = ""
    if kind == "enemy":
        target_shown = humanize_entity_name(entity.name)
        out.update(target=target_shown, target_kind="enemy",
                   target_place=humanize_entity_name(entity.location))
        if (verb in ("attack", "pursue") or action == "charge") \
                and not world.is_at_war(view.player, entity.nation):
            return _refusal_reading(out, f"We are not at war with {_court(world, entity.nation)}")
        if verb in ("support", "follow"):
            return _refusal_reading(out, _support_a_foreigner(world, entity, verb))
        if verb in ("move", "scout"):
            # `/command`: "Mack is a commander, Sire, not a province".
            return _refusal_reading(out, f"{target_shown} is a commander — name a province")
    elif kind == "unseen":
        # Any other verb aimed at a man out of sight: his name, no place.
        target_shown = humanize_entity_name(entity.name)
        out.update(target=target_shown, target_kind="enemy", target_place="")
    elif kind == "friendly":
        target_shown = humanize_entity_name(entity.name)
        out.update(target=target_shown, target_kind="friendly")
        if verb in ("move", "scout"):
            # `/command`: "Region 'Davout' not found" — a march to a friend
            # is `march to`, a support or a follow.
            return _refusal_reading(out, f"{target_shown} is a commander — name a province")
    elif kind == "province":
        target_shown = humanize_entity_name(entity)
        out.update(target=target_shown, target_kind="province")
    elif kind == "court":
        target_shown = humanize_entity_name(entity)
        out.update(target=target_shown, target_kind="none")
        if verb in ("march", "move", "scout"):
            return _refusal_reading(out, f"{target_shown} is a court — name one of its provinces")
    # The price, the refusal, the clock: the executor's own readers.
    # (never a man out of sight's name: a mood read off his place is his place)
    _objection_target = "" if kind == "unseen" else target
    pool = "admin" if action in ADMIN_ACTIONS else "military"
    free = action in _FREE_ORDER_ACTIONS and not parsed.get("is_strategic")
    ap = 0
    turns = 0
    objection = "none"
    replaces = ""
    quote = None
    asks_first = False
    if verb in sp.VERBS:
        refusal = sp.order_state_refusal(world, marshal, verb)
        if refusal:
            return _refusal_reading(out, f"{shown} — {refusal}")
        ap = int(sp.order_price(world, marshal, verb))
        free = free or ap == 0
        if verb == "march" and kind == "province":
            then_attack = ""
            arrival = str(parsed.get("arrival_target") or "")
            if parsed.get("attack_on_arrival") and arrival in view.seen \
                    and world.is_at_war(view.player, view.seen[arrival].nation):
                then_attack = arrival
            quote = oq.march_quote(world, marshal, entity, then_attack=then_attack)
        elif verb == "attack" and kind == "enemy":
            quote = oq.attack_quote(world, marshal, entity)
            if quote.get("kind") == "march_attack":
                # DDB-R1: a typed attack out of reach ASKS first, free, and
                # its yes is the PURSUIT (`combat_executor.pursuit_ask`) —
                # refused as the pursuit is; priced below by the quote.
                refusal = sp.order_state_refusal(world, marshal, "pursue")
                if refusal:
                    return _refusal_reading(out, f"{shown} — {refusal}")
                asks_first = True
        elif verb == "support" and kind == "friendly":
            quote = oq.support_quote(world, marshal, entity)
        elif verb == "follow" and kind == "friendly":
            quote = oq.follow_quote(world, marshal, entity)
        elif verb == "move" and kind == "province" and not parsed.get("is_strategic"):
            # Row IC (found by the directive's fuzz — the list reads each man's
            # line through this reader): a typed `move` meets the executor's
            # own gates here too (`MovementExecutor.move_refusal_probe`: "X is
            # already in Y", engaged …), and a province beyond his reach is the
            # MARCH one verb over (`_execute_move`'s auto-upgrade — the
            # march's road, clock and price). The reading priced every `move`
            # as the one-action step, so "Massena, move to Lorraine" read 1
            # action and was charged 2.
            from backend.commands.movement_executor import MovementExecutor
            _there = world.get_region(entity)
            _stopped = (MovementExecutor.move_refusal_probe(world, marshal, _there, entity)
                        if _there is not None else None)
            if _stopped is not None:
                _said = _first_sentence(str(_stopped.get("message") or "the move is refused"))
                for _lead in (marshal.name + " ", shown + " "):
                    if _said.startswith(_lead):
                        _said = _said[len(_lead):]
                        break
                return _refusal_reading(out, f"{shown} — {_said.rstrip('.')}")
            _far = world.get_distance(marshal.location, entity)
            if isinstance(_far, int) and _far > max(1, int(getattr(marshal, "movement_range", 1) or 1)):
                quote = oq.march_quote(world, marshal, entity)
                out["_marches"] = True
        if quote is not None:
            if not quote.get("ok"):
                return _refusal_reading(out, f"{shown} — {_first_sentence(quote.get('refusal') or 'the order is refused')}")
            # The quote's own price — for an ask, its yes (the march that
            # carries the attack: the standing order's rate, one action when a
            # seen foe meets it in its first province — the census measured).
            ap = int(quote.get("ap", ap) or 0)
            turns = int(quote.get("turns", 0) or 0)
            objection = str(quote.get("objection") or "none")
            replaces = str(quote.get("replaces") or "")
            out["command"] = str(quote.get("command") or "")
            # Row IC (the directive's list): the quote itself rides beside the
            # reading for `read_one`'s callers — its riders (the contact, the
            # camp, the pay …) are the list's notes. `preview` drops the key:
            # the wire's whitelist is unchanged.
            out["_quote"] = quote
        elif verb == "hold" and kind in ("province", "enemy", "friendly"):
            # UI6-X20: a HOLD is a march-and-hold to its province — the
            # province named, or the province of a commander in sight (the
            # strategic road's own read, `_resolve_region_from_phrase`). Read
            # as `/command` meets it: the road law refuses where it would,
            # and the objection is weighed over the road (the executor's
            # `evaluate_strategic_situation(marshal, "HOLD", target, path)`),
            # which the bare reading never passed ("Davout, hold Swabia" read
            # no objection while Davout objected).
            dest = entity if kind == "province" else getattr(entity, "location", "")
            road: List[str] = []
            if dest and dest != marshal.location:
                from backend.commands import strategic as road_law
                road, road_refusal, _road_kind = road_law.march_road(world, marshal, dest, "HOLD")
                if road_refusal is not None:
                    why = _first_sentence(str(road_refusal.get("message") or "the order is refused"))
                    return _refusal_reading(out, f"{shown} — {why}")
            objection = oq._strategic_objection(world, marshal, "HOLD", target, list(road or []))
        else:
            objection = _objection(world, marshal, verb, action, _objection_target)
    else:
        ap = 0 if free else int(world.get_action_cost(action)) if action else 0
        if action in sp._BATTERY_ACTIONS:
            objection = _objection(world, marshal, verb, action, _objection_target)
    # BA3-X5 (row BA, BA-4): where the order is a WORD of an open day — an attack
    # on the day's enemy, a SUPPORT for its lead, the lead's defend or retreat —
    # it costs the day's points and no action. ONE source with the quotes:
    # `battle_day.classify_word`, the door's own test, asked of the same parse.
    from backend.game_logic import battle_day as _day
    day_word = None if asks_first else _day.word_of(world, parsed)
    if day_word is not None:
        ap = 0
        out["points"], out["word"] = int(day_word.get("price", 0) or 0), str(day_word.get("kind") or "")
    ap_left = int(getattr(world, "admin_actions_remaining" if pool == "admin" else "actions_remaining", 0) or 0)
    out.update(ap=int(ap), ap_left=ap_left, pool=pool, free=bool(free or ap == 0), ok=True,
               turns=int(turns), objection=objection if objection in ("none", "possible") else "none",
               replaces=replaces, asks_first=bool(asks_first), kind="order")
    # The head: who does what to whom.
    words = _VERB_WORDS.get(verb or action, (verb or action).replace("_", " "))
    # UI6-X60: a marshal with guns who is told to bombard BOMBARDS (`/command`
    # runs the shelling) - the head names the verb the sentence gave.
    if action == "attack" and not parsed.get("is_strategic") and (verb or action) == "attack":
        from backend.commands import proper_name as _pn
        if _pn.attack_verb(text) == "bombard" and getattr(marshal, "artillery", False):
            words = "bombard"
    head = f"{shown} · {words}"
    if action == "retreat" and not parsed.get("is_strategic"):
        # UI6-X67: where he falls back from, and to (W6-1 honours a legal
        # stated destination; an unknown one is named - `/command` substitutes).
        if retreat_from:
            head += f" from {retreat_from}"
        if target_shown:
            head += f" to {target_shown}"
        elif retreat_stated:
            out["retreat_note"] = (f"no province ‘{retreat_stated}’ is known — he falls back "
                                   f"to safe ground the staff chooses")
    elif target_shown:
        head += f" {target_shown}"
        if kind == "enemy":
            head += f" ({out['target_place']})"
    if verb == "march" and quote is not None and quote.get("kind") == "march_attack" and not asks_first:
        foe = humanize_entity_name(str(parsed.get("arrival_target") or ""))
        head += f" then attack {foe}"
    parts = [_part("head", head)]
    if asks_first:
        distance = world.get_distance(marshal.location, entity.location)
        far = f"{int(distance)} provinces away" if isinstance(distance, int) and distance > 1 else "beyond his reach"
        parts.append(_part("warn", f"asks first — {target_shown} is {far}"))
        parts.append(_part("cost", f"{_cost_text(ap, pool, False)} if confirmed"))
        if out["command"]:
            out["candidates"] = [{"label": out["command"], "line": out["command"]}]
    elif day_word is not None:
        parts.append(_part("cost", _day.price_line(day_word)))      # BA3-X5
    else:
        parts.append(_part("cost", _cost_text(ap, pool, free or ap == 0)))
    if turns >= 1:
        parts.append(_part("turns", _turns_text(turns)))
    if out.pop("_marches", False):
        parts.append(_part("note", "too far for one move — he marches there"))
    if out["objection"] == "possible":
        parts.append(_part("warn", "he may object"))
    # The arrival's object: a name on no roster, or a man out of sight
    # (UI6-X9), is dropped by the march's own reader (`dropped_arrival_note`,
    # whose rule is "in sight"); the readback says it in the same words.
    arrival = str(parsed.get("arrival_target") or "")
    arrival_dropped = bool(parsed.get("dropped_arrival_note")) or bool(
        parsed.get("attack_on_arrival") and arrival and arrival not in view.seen)
    if verb == "march" and arrival_dropped and not (
            quote is not None and quote.get("kind") == "march_attack"):
        obj = _arrival_object(text, str(parsed.get("dropped_arrival_note") or ""))
        if obj:
            parts.append(_part("warn", f"no attack armed on arrival — ‘{obj}’ is not in our sight"))
    if replaces:
        parts.append(_part("note", f"replaces {replaces}"))
    if out.pop("retreat_note", ""):
        parts.append(_part("warn", f"no province ‘{retreat_stated}’ is known — he falls back "
                                   f"to safe ground the staff chooses"))
    _riders(parts, parsed)
    out["parts"] = parts
    return out


def _arrival_object(text: str, note: str = "") -> str:
    """The arrival order's dropped object — the name the march's own note
    gives ("No foe called Moore is in sight — …", `dropped_arrival_note`),
    else the words the player TYPED after the tail verb ("… then attack
    Zorglub" -> "Zorglub"; a comma or a semicolon leads it too)."""
    from backend.commands import proper_name as pn
    named = re.match(r"^No foe called (?P<name>.+?) is in sight\b", str(note or ""))
    if named:
        return named.group("name")
    m = re.search(r"(?:\b(?:then|and)\s+|[,;]\s*)(?:attack|assault|engage|strike|hit|fall\s+upon)"
                  r"\s+(?P<obj>.+)$", text or "", re.I)
    if not m:
        return ""
    words = pn.object_words(m.group("obj"))
    return " ".join(words)


def _riders(parts: List[Dict[str, str]], parsed: Dict) -> None:
    if parsed.get("dropped_sequel"):
        parts.append(_part("warn", "a second order waits behind it"))
    note = str(parsed.get("typo_note") or "")
    m = re.match(r"^\(Berthier read '([^']+)' as '([^']+)'\.\)$", note)
    if m:
        parts.append(_part("note", f"read ‘{m.group(1)}’ as {m.group(2)}"))


# ═══════════════════════════════════════════════════════════════════════════
# Row IC, Session 3 (IC-10; INDEPENDENT_COMMAND_SPEC §8.4, §8.6) — ON HIS OWN.
#
# The user's words: "make this engaging make the typing really fun". As you
# type a task to a man on his own the reading answers BEFORE anything is spent:
# what it takes (on his own, the count, his odds as numbers — and how your
# "boldly" moves them), what he would do TOMORROW NIGHT on the board as it
# stands (the one pure reading the night itself uses — `own_order.read`), his
# answer in his own voice (it changes with your words), the price, who takes
# it ill, his objection and its cost. A question to him is answered here too,
# free: the read-back already shows what he says.
# ═══════════════════════════════════════════════════════════════════════════

def _with_word(text: str, word: str) -> str:
    """The typed line with a word put where it belongs — before the closing
    stop ("Ney, take Swabia on your own" + "boldly")."""
    base = str(text or "").rstrip()
    stop = ""
    while base and base[-1] in ".!":
        stop = base[-1] + stop
        base = base[:-1].rstrip()
    joint = ", " if base.lower().endswith(("own", "fit", "judgement", "judgment", "discretion")) else " "
    return f"{base}{joint}{word}{stop or '.'}"


def _without_marks(text: str) -> str:
    from backend.ai.own_words import set_aside_marks
    cleaned, _found = set_aside_marks(text)
    return cleaned


def _own_question_reading(out: Dict[str, Any], world, question: Dict) -> Dict[str, Any]:
    from backend.game_logic import own_order as _own
    name = str(question.get("subject") or "")
    marshal = world.get_marshal(name) if name else None
    if marshal is None:
        return _simple(out, "question", ("head", "A question for Berthier"), ("cost", "costs nothing"))
    shown = humanize_entity_name(marshal.name)
    try:
        said = _own.answer(world, marshal, str(question.get("kind") or "")[4:],
                           str(question.get("place") or ""))
    except Exception as exc:
        report(exc, "parse_preview._own_question_reading")
        said = {}
    parts = [("head", f"A question for {shown}"), ("cost", "costs nothing")]
    if said.get("says"):
        parts.append(("answer", f"\u201c{said['says']}\u201d"))
    out.update(marshal=shown)
    return _simple(out, "question", *parts)


def _own_reading(out: Dict[str, Any], world, parsed: Dict, text: str) -> Dict[str, Any]:
    from backend.game_logic import own_order as _own
    try:
        r = _own.reading_of_parse(world, parsed)
    except Exception as exc:
        report(exc, "parse_preview._own_reading")
        return _refusal_reading(out, "That task could not be read.")
    shown = str(r.get("shown") or humanize_entity_name(str(r.get("marshal") or "")))
    kind = str(r.get("kind") or "give")
    out.update(marshal=shown, strategic=True)
    if kind in ("stand_down", "carry_on", "risk"):
        if not r.get("ok"):
            return _refusal_reading(out, f"{shown} is not on his own — there is no task of his to change.")
        marshal = world.get_marshal(str(r.get("marshal") or ""))
        info = _own.payload(world, marshal) or {}
        if kind == "stand_down":
            out.update(kind="order", ok=True, ap=0, verb="stand down")
            return _simple(out, "order", ("head", f"{shown} · stand down — his task ends"),
                           ("cost", str(info.get("stand_down") or "free")),
                           ("note", str(info.get("count") or "")))
        if kind == "carry_on":
            out.update(kind="order", ok=True, ap=0, verb="carry on")
            asks = str(info.get("asks") or "")
            return _simple(out, "order", ("head", f"{shown} · carry on with his task"),
                           ("cost", "free"),
                           ("taken", f"he asked: {asks}" if asks else "he is not waiting for your word"))
        step = int((parsed.get("own") or {}).get("step", 0) or 0)
        risk = max(-1, min(1, int(info.get("risk", 0) or 0) + step))
        if risk == int(info.get("risk", 0) or 0):
            return _refusal_reading(out, f"{shown} already goes in at {_own.needed_words(_own.needed(marshal, risk))}"
                                         f" — one step is the most you can move him.")
        if int(getattr(world, "actions_remaining", 0) or 0) < _own.CHANGE_PRICE:
            return _refusal_reading(out, f"Changing {shown}'s task takes {_own.CHANGE_PRICE} action; none is left this turn.")
        n = _own.needed(marshal, risk)
        out.update(kind="order", ok=True, ap=_own.CHANGE_PRICE,
                   verb="more risk" if step > 0 else "less risk")
        return _simple(out, "order",
                       ("head", f"{shown} · {'more' if step > 0 else 'less'} risk"),
                       ("cost", _cost_text(_own.CHANGE_PRICE, "military", False)),
                       ("taken", f"he will go in at {_own.needed_words(n)}"))
    if not r.get("ok"):
        why = str(r.get("why") or "no task he can take")
        out.update(kind="refusal", ok=False, refusal=why)
        out["parts"] = [_part("head", f"{shown} · on his own"),
                        _part("bad", f"{shown} cannot be set on his own: {why}."),
                        _part("cost", "free refusal")]
        plain = _without_marks(text)
        if plain and plain != text:
            out["candidates"] = [{"label": "Give it as an exact order", "line": plain}]
        return out
    task_words = _own.task_words(r["spec"])
    price = int(r.get("price", 2) or 2)
    out.update(kind="order", ok=True, ap=price, verb=task_words.split(" ")[0],
               target=str(r.get("target") or ""))
    parts = [("head", f"{shown} · on his own: {task_words}"),
             ("cost", _cost_text(price, "military", False) + (" — a change to his task" if r.get("changing") else ""))]
    count = (f"on his own — once given, {int(r.get('count_after', 1))} of the "
             f"{int(r.get('allowed', 1))} you may have (laws raise it)"
             if not r.get("changing") else f"on his own — {r.get('count')}")
    parts.append(("taken", count))
    _tn = r.get("tonight") or {}
    parts.append(("taken", f"he attacks only when the odds are {_tn.get('needed_words') or r.get('needed_words')}"))
    if len(r.get("area") or []) == 2:
        parts.append(("taken", "his area: " + " and ".join(humanize_entity_name(p) for p in r["area"])))
    tonight = r.get("tonight") or {}
    if tonight.get("line"):
        parts.append(("tonight", (f"Tonight, as things stand: {tonight['line']}" if r.get("starts_tonight")
                                  else f"His first night (tomorrow), as things stand: {tonight['line']}")))
    if tonight.get("help"):
        parts.append(("tonight", f"Every night: {tonight['help']}"))
    if r.get("says"):
        parts.append(("answer", f"\u201c{r['says']}\u201d"))
    if r.get("objection"):
        parts.append(("warn", f"he objects: {r['objection']} — giving it anyway costs "
                              f"{int(r.get('objection_cost', 0))} of his trust"))
    if r.get("slight"):
        parts.append(("warn", f"{r['slight']} outranks him and has no order — he will resent it "
                              f"(his regard for {shown} drops)"))
    parts.append(("note", "he starts tomorrow night; you can stand him down for free"))
    out["parts"] = [_part(role, t) for role, t in parts]
    chips = []
    risk = int(r.get("risk", 0) or 0)
    if risk == 0:
        chips.append({"label": "+ boldly (attacks at worse odds)", "line": _with_word(text, "boldly")})
        chips.append({"label": "+ carefully (only at better odds)", "line": _with_word(text, "carefully")})
    prop = r.get("proposal") or {}
    if r.get("objection") and prop.get("line"):
        chips.insert(0, {"label": "Take his advice", "line": str(prop["line"])})
    if r.get("task") == "hold" and len(r.get("area") or []) == 1:
        try:
            from backend.game_logic.own_order import _near
            here = str(r["area"][0])
            for name in _near(world, here):
                region = world.get_region(name)
                if region is not None and getattr(region, "controller", None) == world.player_nation:
                    base = str(text or "").rstrip(" .!")
                    shown_here = humanize_entity_name(here)
                    if shown_here in base:
                        chips.append({"label": f"+ and {humanize_entity_name(name)} (a second province to hold)",
                                      "line": base.replace(shown_here, f"{shown_here} and {humanize_entity_name(name)}", 1) + "."})
                    break
        except Exception as exc:
            report(exc, "parse_preview._own_reading: the second province")
    out["candidates"] = chips[:3]
    return out


def _refusal_reading(out: Dict[str, Any], text: str) -> Dict[str, Any]:
    out.update(kind="refusal", ok=False, refusal=str(text),
               parts=[_part("bad", text), _part("cost", "free refusal")])
    return out


# ═══════════════════════════════════════════════════════════════════════════
# Row IC, Session 2 (IC-8; INDEPENDENT_COMMAND_SPEC §8.4) — TAKEN, NOT TAKEN.
#
# "Nothing typed is dropped in silence." The reading says, before anything is
# spent, what the order TOOK beyond who-does-what (each condition, each
# if-then, what a march does on arrival — IC-V2) and what it did NOT take
# (a one-word condition under the clause guard's floor, a time limit on an
# order that has none, a how-bold word — IC-V1), each quoted with the plain
# reason. A part that would change what he does BLOCKS: the reading carries
# the line restated without it (`understood`), Enter sends that line, and a
# line typed past the reading is refused free by `/command` with the same
# words (`typed_gate` — ONE reader for both roads). Filler blocks nothing.
#
# The order itself is untouched: every line here parses exactly as it did
# (the guard's floor, the corpus pin `cr2-when-ready-then-retreat-not-split`).
# ═══════════════════════════════════════════════════════════════════════════

WHY_NO_CONDITION = "this order takes no condition; it would go out now"
WHY_NO_CLOCK = "this order has no time limit; it is carried out once, now"
WHY_NOT_HELD = "not an end this order can keep; it would go on until you change it"
WHY_AS_WRITTEN = "an order is carried out as written, no more boldly and no more carefully"
WHY_FILLER = "changes nothing; the order goes as written"
WHY_OPEN_ENDED = "asks for no limit; the order stands until you change it"
WHY_REASON = "taken as your reason, not as a condition; he acts now"
# (the review, L3) a part that blocks, where no clean line could be restated
WHY_TYPE_AGAIN = "this line is not sent as it stands — type the order again without that part"
# what a march does on arrival, in the words its chips use (the review, W1)
_ARRIVAL_WORDS = {"fortify": "dig in", "defend": "stand on the defensive"}
_UNREAD_NOTE_RE = re.compile(r"^'(?P<clause>.+)' is not a clause I can hold\b")
_OFFER_MARKERS = frozenset({"if", "unless", "when", "in case", "once", "as soon as"})


def taken_rows(parsed: Dict) -> List[str]:
    """IC-V2: what the parse TOOK beyond who-does-what — the condition, what a
    march does on arrival, each if-then — in the words the order's own echo
    and the Ledger say them (`condition_grammar.describe_condition`,
    `if_thens.describe`). PURE."""
    from backend.ai.condition_grammar import describe_condition
    from backend.commands import if_thens as IT
    rows: List[str] = []
    if parsed.get("is_strategic"):
        cond = parsed.get("strategic_condition")
        if isinstance(cond, dict) and cond:
            shown = dict(cond)
            for key in ("until_marshal_arrives", "until_marshal_destroyed"):
                if shown.get(key):
                    shown[key] = humanize_entity_name(str(shown[key]))
            said = describe_condition(shown)
            if said:
                rows.append(said)
        verb = str(parsed.get("arrival_verb") or "")
        if verb:
            rows.append(f"then {_ARRIVAL_WORDS.get(verb, verb)} on arrival")
    for line in parsed.get("if_thens") or []:
        rows.append(IT.describe(line, humanize_entity_name))
    return rows


def _why_not_bold(world, marshal, action: str, parsed: Dict) -> str:
    """Row IC, Session 3: why a how-bold word was not taken — a man who could
    be set on his own is told what stands in the way (the count, his trust),
    so the line can be changed; anyone else hears that an exact order goes as
    written."""
    if marshal is None or world is None:
        return WHY_AS_WRITTEN
    try:
        from backend.game_logic import own_order as _own
        task, _target = _own.task_of_parse(world, parsed)
        if not task or _own._nature(marshal) not in ("bold", "careful"):
            return WHY_AS_WRITTEN
        why = _own.why_not(world, marshal, task, replacing=_own.on_his_own(marshal))
        if why:
            return f"how boldly he goes is his own only on a task on his own, and {why}"
    except Exception as exc:
        report(exc, "parse_preview._why_not_bold")
    return WHY_AS_WRITTEN


def not_taken_rows(world, parsed: Dict, text: str) -> List[Dict[str, Any]]:
    """IC-V1: every part of the typed line this order did NOT take —
    ``{"clause", "why", "blocks", "offer"}``: the words as typed, the plain
    reason, whether it would change what he does (so the line is sent
    restated without it), and — for a condition the word table knows — the
    exact order it means (`if_thens.offer`), as a sentence to fill the line
    with. PURE."""
    from backend.ai import task_words as TW
    from backend.ai.condition_grammar import TURNS_RE
    from backend.commands import if_thens as IT
    command = parsed.get("command") if isinstance(parsed.get("command"), dict) else {}
    action = str(command.get("action") or "")
    strategic = bool(parsed.get("is_strategic"))
    held = bool(strategic and parsed.get("strategic_condition"))
    marshal = world.get_marshal(str(command.get("marshal") or "")) if world is not None else None
    rows: List[Dict[str, Any]] = []
    seen: set = set()

    def add(clause: str, why: str, blocks: bool, offer: str = "") -> None:
        key = " ".join(str(clause or "").lower().split())
        if not key or key in seen:
            return
        seen.add(key)
        rows.append({"clause": " ".join(str(clause).split()), "why": why,
                     "blocks": bool(blocks), "offer": offer})

    order_words = "hold"
    if strategic and parsed.get("strategic_type") == "HOLD" and command.get("target") \
            and not parsed.get("target_placed_by_the_game"):
        order_words = f"hold {humanize_entity_name(str(command.get('target')))}"
    for blanked in parsed.get("blanked_clauses") or []:
        clause = str((blanked or {}).get("clause") or "")
        marker = str((blanked or {}).get("marker") or "")
        low = " ".join(clause.lower().split())
        if marker == "until":
            if held:
                continue                    # the grammar read it: it is TAKEN
            if low.rstrip(".!") in TW.OPEN_ENDED:
                add(clause, WHY_OPEN_ENDED, False)      # "until further orders"
                continue
            add(clause, WHY_NOT_HELD if strategic else WHY_NO_CLOCK, True)
        elif low in TW.FILLER:
            add(clause, WHY_FILLER, False)
        elif marker in ("while", "before"):
            add(clause, WHY_REASON, False)
        else:
            offer = ""
            if marker in _OFFER_MARKERS and marshal is not None:
                try:
                    offer = IT.offer(world, marshal, clause,
                                     "hold" if strategic and parsed.get("strategic_type") == "HOLD"
                                     else action, order_words)
                except Exception as exc:
                    report(exc, "parse_preview.not_taken_rows: the offer")
            add(clause, WHY_NO_CONDITION, True, offer)
    # the strategic road's own unread clauses (CR-7-4's echo), said before the send
    for note in parsed.get("condition_notes") or []:
        unread = _UNREAD_NOTE_RE.match(str(note or ""))
        if unread:
            said = " ".join(unread.group("clause").lower().split()).rstrip(".!")
            add(unread.group("clause"), WHY_OPEN_ENDED if said in TW.OPEN_ENDED else WHY_NOT_HELD,
                said not in TW.OPEN_ENDED)
    # a time limit on an order that has none ("Ney, fortify for 3 turns") —
    # never one that belongs to a second order the relay holds (the review, L4)
    if not strategic and marshal is not None and not parsed.get("dropped_sequel"):
        for found in TURNS_RE.finditer(str(text or "").lower()):
            add(str(text)[found.start():found.end()], WHY_NO_CLOCK, True)
    for word in parsed.get("risk_words") or []:
        add(str(word), _why_not_bold(world, marshal, action, parsed), True)
    # a loose time ("through the winter", "for two weeks"): offered in turns
    from backend.commands import task_line as TL
    for phrase in parsed.get("loose_time") or []:
        offer = ""
        if strategic:
            swapped = re.sub(r"\s+".join(re.escape(w) for w in str(phrase).split()),
                             "for 3 turns", str(text or ""), count=1, flags=re.IGNORECASE)
            offer = swapped if swapped != str(text or "") else ""
        add(str(phrase), TL.WHY_LOOSE_TIME, True, offer)
    # a tail no marshal's order carries ("… and build a fort")
    if marshal is not None and not parsed.get("dropped_sequel") \
            and action not in TL.FORBIDDEN_ACTIONS:
        tail = TL.forbidden_tail(text)
        if tail:
            add(tail, TL.WHY_NOT_A_MARSHALS, True)
    return rows


def restate_without(text: str, clauses: List[str]) -> str:
    """The typed line with `clauses` taken out, put right (`if_thens.tidy`) —
    "" when a clause is not in the line as typed (nothing can be restated)."""
    from backend.commands import if_thens as IT
    out = str(text or "")
    for clause in clauses:
        words = [re.escape(w) for w in str(clause or "").split()]
        if not words:
            return ""
        found = re.search(r"\s+".join(words), out, re.IGNORECASE)
        if found is None:
            return ""
        out = out[:found.start()] + " " + out[found.end():]
    return IT.tidy(out)


def _parse_key(parsed: Dict) -> tuple:
    """What a parse WILL DO, for comparing a line with its restated self."""
    command = parsed.get("command") if isinstance(parsed.get("command"), dict) else {}
    cond = parsed.get("strategic_condition") if parsed.get("is_strategic") else None
    return (
        bool(parsed.get("success")), str(command.get("marshal") or ""),
        str(command.get("action") or ""), str(command.get("target") or ""),
        str(parsed.get("strategic_type") or "") if parsed.get("is_strategic") else "",
        tuple(sorted((str(k), str(v)) for k, v in (cond or {}).items())),
        str(parsed.get("arrival_verb") or ""),
        tuple((line.get("if"), line.get("who"), line.get("friend"), line.get("place"),
               line.get("then"), line.get("to"), bool(line.get("any_odds")))
              for line in parsed.get("if_thens") or []),
    )


def understood_line(world, parsed: Dict, text: str,
                    parse_again: Optional[Callable[[str], Dict]]) -> tuple:
    """``(the line as understood, the not-taken rows)``. The line is the typed
    one restated without every BLOCKING part — and only when that line, read
    again, is the same order with nothing left to block (`parse_again`);
    otherwise it is "" and no row blocks (the order goes as it always did, and
    the rows still say what was not taken)."""
    rows = not_taken_rows(world, parsed, text)
    blocking = [row for row in rows if row["blocks"]]
    line = ""
    if blocking and parse_again is not None:
        line = restate_without(text, [row["clause"] for row in blocking])
        if line:
            try:
                again = parse_again(line)
            except Exception as exc:
                report(exc, "parse_preview.understood_line: the second read")
                again = {}
            same = (isinstance(again, dict) and _parse_key(again) == _parse_key(parsed)
                    and not any(row["blocks"] for row in not_taken_rows(world, again, line)))
            if not same:
                line = ""
    # (the review, L3) No clean line to offer: the part STILL blocks — a typed
    # line is held with "type the order again without that part" (it used to
    # go out with the part dropped, which is what the rows exist to prevent).
    # Only a reader with no second read at all (a nested reading) blocks nothing.
    if not line and parse_again is None:
        for row in rows:
            row["blocks"] = False
    return line, rows


def conditional_offer(world, parsed: Dict, text: str,
                      parse_again: Callable[[str], Dict]) -> str:
    """§8.3 ("unless …" — offered back as the if-then it means): for a line
    REFUSED as a contingency ("Ney, hold Rhineland unless Mack advances"),
    the exact order that says it — "Ney, hold Rhineland. If Mack comes within
    reach, fall back to Lorraine." — when the word table reads the condition,
    his order can carry the line, and the sentence reads back as that order.
    "" otherwise. PURE."""
    from backend.commands import if_thens as IT
    clause = str((parsed.get("refusal_detail") or {}).get("clause") or "").strip()
    if not clause or world is None:
        return ""
    rest = restate_without(text, [clause])
    if not rest:
        return ""
    try:
        order = parse_again(rest)
        command = order.get("command") if isinstance(order, dict) else None
        if not isinstance(command, dict) or not order.get("success"):
            return ""
        marshal = world.get_marshal(str(command.get("marshal") or ""))
        if marshal is None or getattr(marshal, "nation", None) != world.player_nation:
            return ""
        holds = bool(order.get("is_strategic")) and order.get("strategic_type") == "HOLD"
        words = "hold"
        if holds and command.get("target") and not order.get("target_placed_by_the_game"):
            words = f"hold {humanize_entity_name(str(command.get('target')))}"
        offer = IT.offer(world, marshal, clause,
                         "hold" if holds else str(command.get("action") or ""), words)
        if not offer:
            return ""
        again = parse_again(offer)
        return offer if (isinstance(again, dict) and again.get("success")
                         and again.get("if_thens")) else ""
    except Exception as exc:
        report(exc, "parse_preview.conditional_offer")
        return ""


def not_taken_text(row: Dict[str, Any]) -> str:
    return f"‘{row.get('clause')}’ — {row.get('why')}"


def typed_gate(world, parsed: Dict, text: str,
               parse_again: Callable[[str], Dict]) -> Optional[Dict[str, Any]]:
    """`/command`'s side of "Send what I understood": a line TYPED in the
    command window whose order would go out without a part that changes what
    he does is refused free, with the line as understood — ``{"message",
    "understood", "not_taken"}`` — or None when nothing blocks. The same
    reader as the reading's rows (`understood_line`). PURE."""
    command = parsed.get("command") if isinstance(parsed, dict) else None
    if not isinstance(command, dict) or not parsed.get("success") or not _an_order(command):
        return None
    line, rows = understood_line(world, parsed, text, parse_again)
    blocking = [row for row in rows if row["blocks"]]
    if not blocking:
        return None
    named = "; ".join(f"'{row['clause']}' — {row['why']}" for row in blocking)
    one = len(blocking) == 1
    offered = (f"What I understood is: '{line}' — send that, or change the line."
               if line else "Type the order again without it.")
    return {
        "message": (f"Not sent, Sire — {'one part' if one else f'{len(blocking)} parts'} of that "
                    f"order {'was' if one else 'were'} not taken: {named}. {offered} "
                    f"Nothing was spent."),
        "understood": line,
        "not_taken": [{"clause": row["clause"], "why": row["why"]} for row in blocking],
    }


def _an_order(command) -> bool:
    """The parse is an order to a marshal — or the one order that goes out
    to them ALL at once with no list first, the general retreat ("everyone
    retreat if outnumbered": IC-V1's sibling, found by the review's sweep —
    the whole army fell back with the condition dropped unsaid)."""
    return isinstance(command, dict) and bool(
        command.get("marshal") or command.get("type") == "general_retreat")


def _his_answer(world, parsed: Dict) -> str:
    """The reading's "He says": a marshal who follows orders to the letter,
    given if-thens, answers in his own voice (one picked line, no die)."""
    command = parsed.get("command") if isinstance(parsed.get("command"), dict) else {}
    marshal = world.get_marshal(str(command.get("marshal") or "")) if world is not None else None
    if marshal is None or getattr(marshal, "personality", "") != "literal" \
            or not parsed.get("if_thens"):
        return ""
    from backend.game_logic.marshal_voice import literal_exact_ack
    return "“" + literal_exact_ack(marshal.name, int(getattr(world, "current_turn", 0) or 0)) + "”"


def _with_task_rows(world, out: Dict[str, Any], parsed: Dict, text: str,
                    parse_again: Optional[Callable[[str], Dict]]) -> Dict[str, Any]:
    """An ORDER's reading with its TAKEN / NOT TAKEN / HE SAYS parts, the line
    as understood, and the offers. Any other reading passes through."""
    if (not isinstance(out, dict) or out.get("kind") != "order"
            or not isinstance(parsed, dict) or not parsed.get("success")):
        return out
    # one man's order, read whole — or the general retreat, which goes out to
    # every corps at once with no list first (`_an_order`)
    to_all = not (parsed.get("command") or {}).get("marshal") and _an_order(parsed.get("command"))
    if not ((out.get("ok") and out.get("marshal")) or to_all):
        return out
    try:
        taken = taken_rows(parsed)
        understood, missed = understood_line(world, parsed, text, parse_again)
        answer = _his_answer(world, parsed)
        # Row IC, Session 2 (IC-7): "attack <him>, held back" — the restraint
        # the player starts. Taken where his attack would ask "charge or
        # restrain?"; anywhere else the words change nothing, and say so.
        command = parsed.get("command") if isinstance(parsed.get("command"), dict) else {}
        if command.get("held_back"):
            from backend.commands.tactical_executor import restrain_refusal
            man = world.get_marshal(str(command.get("marshal") or ""))
            short = restrain_refusal(world, man, str(command.get("target") or ""))[1] if man else ""
            if short:
                missed = list(missed) + [{"clause": "held back", "why": short, "blocks": False,
                                          "offer": ""}]
            else:
                taken = list(taken) + ["held back from the charge"]
    except Exception as exc:
        report(exc, "parse_preview._with_task_rows")
        return out
    parts = list(out.get("parts") or [])
    parts += [_part("taken", said) for said in taken]
    # what the order's own echo would warn of AFTER the send ("Ney is already
    # at Rhineland with him — that arm is met at the turn's end"), said before
    for note in parsed.get("condition_notes") or []:
        said = str(note or "").strip()
        if said and " read as " not in said and not _UNREAD_NOTE_RE.match(said):
            parts.append(_part("warn", said))
    parts += [{"role": "nottaken", "text": not_taken_text(row), "blocks": bool(row["blocks"])}
              for row in missed]
    if not understood and any(row["blocks"] for row in missed):
        parts.append({"role": "nottaken", "text": WHY_TYPE_AGAIN, "blocks": True})
    if answer:
        parts.append(_part("answer", answer))
    out["parts"] = parts
    if understood:
        out["understood"] = understood
    offers = []
    for row in missed:
        offer = str(row.get("offer") or "")
        if not offer or offer in offers or parse_again is None:
            continue
        try:
            again = parse_again(offer)
        except Exception as exc:
            report(exc, "parse_preview._with_task_rows: the offer's read")
            continue
        if (isinstance(again, dict) and again.get("success")
                and (again.get("if_thens") or again.get("strategic_condition"))):
            offers.append(offer)
    if offers:
        out["candidates"] = list(out.get("candidates") or []) + [
            {"label": offer, "line": offer} for offer in offers]
    # §8.2's word-chips: what the sentence could carry NEXT — only where
    # nothing else is offered and nothing blocks (the line is settled).
    if not understood and not out.get("candidates") and parse_again is not None:
        try:
            more = continuations(world, parsed, text, parse_again)
        except Exception as exc:
            report(exc, "parse_preview._with_task_rows: the word-chips")
            more = []
        if more:
            out["candidates"] = more
    return out


CONTINUATIONS_MAX = 3


def continuations(world, parsed: Dict, text: str,
                  parse_again: Callable[[str], Dict]) -> List[Dict[str, str]]:
    """Row IC, Session 2 (IC-8; §8.2 "Word-chips under the line write into the
    sentence: until… · for N turns · if…"): for a STANDING order to one of
    our marshals, the parts it could still carry, each a chip that writes its
    words in place — ``[{"label": "+ for 3 turns", "line": "<the line> for 3
    turns"}, …]``: a time limit and an "until" where the order has no
    condition yet, and the NEXT if-then while his order may carry another
    (three for a marshal who follows orders to the letter, one on a hold for
    anyone else). Every line offered is read again and offered only when it
    is taken with that part. PURE; nothing is sent by a chip."""
    from backend.commands import if_thens as IT
    from backend.commands import task_presets as TP
    command = parsed.get("command") if isinstance(parsed.get("command"), dict) else {}
    if not parsed.get("success") or not parsed.get("is_strategic") or world is None:
        return []
    marshal = world.get_marshal(str(command.get("marshal") or ""))
    if marshal is None or getattr(marshal, "nation", None) != world.player_nation:
        return []
    kind = str(parsed.get("strategic_type") or "")
    base = str(text or "").strip().rstrip(".!").strip()
    if not base:
        return []
    out: List[Dict[str, str]] = []

    def offer(label: str, line: str, taken) -> None:
        if len(out) >= CONTINUATIONS_MAX:
            return
        again = parse_again(line)
        if isinstance(again, dict) and again.get("success") and taken(again):
            out.append({"label": label, "line": line})

    def cond(p: Dict) -> Dict:
        return p.get("strategic_condition") or {}

    lines = list(parsed.get("if_thens") or [])
    if not cond(parsed) and not lines and kind in ("HOLD", "PURSUE", "SUPPORT"):
        offer("+ for 3 turns", base + " for 3 turns", lambda p: cond(p).get("max_turns") == 3)
        friend = humanize_entity_name(TP._friend_beside(world, marshal)) if kind == "HOLD" else ""
        if friend:
            offer(f"+ until {friend} arrives", f"{base} until {friend} arrives",
                  lambda p: bool(cond(p).get("until_marshal_arrives")))
        if kind == "PURSUE":
            offer("+ until he is destroyed", base + " until he is destroyed",
                  lambda p: bool(cond(p).get("until_marshal_destroyed")))
    if IT.carries(marshal, kind) and len(lines) < IT.capacity(marshal):
        have = {str(line.get("if") or "") for line in lines}
        safe = humanize_entity_name(TP._safe_ground(world, marshal))
        for name, sentence in (("attacked", "If attacked, dig in."),
                               ("outnumbered", f"If outnumbered, fall back to {safe}." if safe else "")):
            if name in have or not sentence:
                continue
            offer("+ " + sentence.rstrip("."), f"{base}. {sentence}",
                  lambda p, n=len(lines): len(p.get("if_thens") or []) == n + 1)
            break       # one if-chip at a time: the next shows when this is taken
    return out


def _if_then_refused(out: Dict[str, Any], parsed: Dict, text: str,
                     read_again: Callable[[str], Dict[str, Any]]) -> Dict[str, Any]:
    """An exact order with a line that cannot be taken (the parser's free
    refusal, kind `if_then`): the reading of the line AS UNDERSTOOD — its
    head, its price, what it took — with each line that was not taken named
    as a blocking row; Enter sends the understood line."""
    understood = str(parsed.get("understood") or "")
    rows = [r for r in (parsed.get("not_taken") or []) if isinstance(r, dict)]
    named = "; ".join(not_taken_text(r) for r in rows) or "one part of that order was not taken"
    base = None
    try:
        base = read_again(understood)
    except Exception as exc:
        report(exc, "parse_preview._if_then_refused: the understood line")
    if not isinstance(base, dict) or base.get("kind") != "order" or not base.get("ok"):
        return _refusal_reading(out, named)
    base["line"] = text
    parts = [p for p in (base.get("parts") or []) if isinstance(p, dict)]
    answer = [p for p in parts if p.get("role") == "answer"]
    parts = [p for p in parts if p.get("role") != "answer"]
    parts += [{"role": "nottaken", "text": not_taken_text(r), "blocks": True} for r in rows]
    base["parts"] = parts + answer
    base["understood"] = understood
    return base


def _delegation_reading(out: Dict[str, Any], world, view: _View, parsed: Dict, deleg) -> Dict[str, Any]:
    from backend.commands import state_probe as sp
    from backend.commands.delegation import (delegation_is_unplaced,
                                             delegation_witness, route_arm)
    marshal = view.own.get(deleg.marshal)
    shown = humanize_entity_name(deleg.marshal)
    arm = route_arm(deleg.personality, delegation_witness(parsed, deleg))
    out.update(kind="delegation", marshal=shown, verb=str(deleg.verb), action="",
               target=humanize_entity_name(str(deleg.target_display or deleg.target)))
    parts = [_part("head", f"{shown} · {deleg.clause}")]
    foe = world.get_marshal(deleg.target) if hasattr(world, "get_marshal") else None
    if foe is not None and (foe.name in view.own or getattr(foe, "nation", None) == view.player):
        foe = None
    if arm in ("cautious", "ask") and delegation_is_unplaced(world, deleg):
        # UI6-X14: `/command` refuses, free — no report places him, so the
        # scout (or the ASK's scout) has no province to name.
        target = humanize_entity_name(deleg.target)
        return _refusal_reading(out, f"No intelligence on {target}’s position — scout for him first")
    if arm == "aggressive" and foe is not None and marshal is not None:
        # His character makes it a PURSUIT (`main._command_delegation`'s
        # re-issue): refused at peace, and — a man out of sight — for want
        # of a sighting, exactly as the pursuit itself is.
        target = humanize_entity_name(foe.name)
        if not world.is_at_war(marshal.nation, foe.nation):
            return _refusal_reading(out, f"We are not at war with {_court(world, foe.nation)}")
        if foe.name not in view.seen:
            from backend.commands.strategic import pursue_known_location
            if not pursue_known_location(world, marshal, foe):
                return _refusal_reading(out, f"No intelligence on {target}’s position — scout for him first")
    if arm == "cautious":
        # UI6-X14's readback: the scout goes where WE place him (his
        # province in sight, his last sighting out of it); one beyond the
        # scout's reach is refused as `/command` refuses it ("… is too far to
        # scout"), never priced.
        if marshal is not None and deleg.scout_target:
            from backend.commands.movement_executor import scout_range
            reach = world.get_distance(marshal.location, deleg.scout_target)
            if isinstance(reach, int) and reach > scout_range(marshal):
                return _refusal_reading(
                    out, f"{shown} — {humanize_entity_name(deleg.scout_target)} is too far to scout")
        ap = int(sp.order_price(world, marshal, "scout")) if marshal is not None else 1
        parts += [_part("note", "he observes first — a scout"), _part("cost", _cost_text(ap, "military", ap == 0))]
        out.update(ap=ap, pool="military")
    elif arm == "aggressive":
        ap = int(sp.order_price(world, marshal, "pursue")) if marshal is not None else 2
        parts += [_part("note", "he pursues and engages"), _part("cost", _cost_text(ap, "military", ap == 0))]
        out.update(ap=ap, pool="military")
    else:
        parts += [_part("warn", "he will ask you how"), _part("cost", "free")]
        out.update(free=True)
    out["ap_left"] = int(getattr(world, "actions_remaining", 0) or 0)
    out["parts"] = parts
    return out


def _collective_target_refusal(world, view: _View, rest: str, verb: str) -> str:
    """The one reason every corps would be refused a collective order aimed at
    a foreign COMMANDER named in `rest` (name and court only — never a
    place), or ""."""
    from backend.commands.strategic import pursue_known_location
    foe = None
    for m in (getattr(world, "marshals", None) or {}).values():
        if m.name in view.own or getattr(m, "nation", None) == view.player:
            continue
        forms = {str(m.name), humanize_entity_name(m.name)}
        if any(re.search(r"(?<![A-Za-z])" + re.escape(f) + r"(?![A-Za-z])", rest, re.IGNORECASE)
               for f in forms):
            foe = m
            break
    if foe is None or getattr(foe, "captured_by", ""):
        return ""
    shown = humanize_entity_name(foe.name)
    seen = foe.name in view.seen
    field = view.own_field()
    if verb in ("support", "follow"):
        return _support_a_foreigner(world, foe, verb)
    if verb in ("move", "scout", "march", "hold") and not seen:
        return f"{shown} is a commander — name a province"
    if verb == "pursue":
        if not world.is_at_war(view.player, foe.nation):
            return f"We are not at war with {_court(world, foe.nation)}"
        if field and not seen and not pursue_known_location(world, field[0], foe):
            return f"No intelligence on {shown}’s position"
    return ""


def _collective_reading(out: Dict[str, Any], world, view: _View, head: Dict, parsed: Dict) -> Dict[str, Any]:
    from backend.commands import state_probe as sp
    rest = str(head.get("rest") or "").strip()
    verb = _verb_of(parsed, parsed.get("command") or {})
    # UI6-X26: a quote is what the order will cost. An order every corps
    # would refuse for the SAME reason the single order is refused (a
    # commander's name is no province, no intelligence on his position, no war
    # with his court, support is for our own) is that reason, free — as
    # `/command` answers it — never a priced order.
    refused = _collective_target_refusal(world, view, rest, verb)
    if refused:
        return _refusal_reading(out, refused)
    prices = set()
    if verb in sp.VERBS:
        for m in view.own_field():
            if not sp.order_state_refusal(world, m, verb):
                prices.add(int(sp.order_price(world, m, verb)))
    cost = ("each at his own price" if len(prices) != 1
            else f"{_cost_text(next(iter(prices)), 'military', next(iter(prices)) == 0)} each")
    out.update(kind="order", verb=verb, action=str((parsed.get("command") or {}).get("action") or ""),
               parts=[_part("head", f"Every corps that can · {rest}"), _part("cost", cost)])
    return out


# ── the pipeline ─────────────────────────────────────────────────────────────

def _read_line(world, text: str, out: Dict[str, Any], *, llm_state, epoch, lost_marshal_refusal,
               why_rx, live_llm, unbound_addressee, premise_reader,
               interrupt_reader=None, _nested: bool = False) -> Dict[str, Any]:
    if getattr(world, "game_over", False) or not text.strip():
        return out
    if why_rx is not None and why_rx.match(text):
        return _simple(out, "meta", ("head", "‘why’ prints the last reading"), ("cost", "free"))
    question = _pending_question(world, text, interrupt_reader)
    if question:
        return _simple(out, "pending", ("head", question))
    # Stage 5: the carryover (pure) and the lost-marshal guard.
    from backend.commands.context_carryover import resolve_context_references
    carry = resolve_context_references(text, world)
    if carry.get("kind") == "error":
        return _refusal_reading(out, "Nothing earlier to refer back to")
    reading = str(carry.get("command") or text) if carry.get("kind") == "rewrite" else text
    if lost_marshal_refusal is not None:
        lost = lost_marshal_refusal(reading, world)
        if lost:
            return _refusal_reading(out, _first_sentence(lost))
    # Stage 6: the premise (pure; the route hands in `/command`'s own reader,
    # `main._premise_reading`), then the parse. The row is one short line:
    # the premise's own prose (the reply's) is never quoted here.
    if premise_reader is not None:
        try:
            reading, refused = premise_reader(reading, world)
            if refused:
                return _refusal_reading(out, "That ‘if’ does not hold on the board we can see")
        except Exception as exc:
            report(exc, "parse_preview._read_line: the premise split")
    state = _llm_state(world, llm_state, epoch)
    parser = _preview_parser()
    parser.llm.live = live_llm
    parser.llm.would_consult = False
    with contextlib.redirect_stdout(io.StringIO()):
        parsed = parser.parse(reading, state, world=world)
    if parser.llm.would_consult:
        out["would_consult_llm"] = True
        return _simple(out, "secretary",
                       ("head", "Berthier’s secretary reads this one — the price shows after you send"))

    def _parse_again(line: str) -> Dict:
        with contextlib.redirect_stdout(io.StringIO()):
            return parser.parse(line, state, world=world)

    def _read_again(line: str) -> Dict[str, Any]:
        return _read_line(world, line, _base(line, epoch), llm_state=llm_state, epoch=epoch,
                          lost_marshal_refusal=lost_marshal_refusal, why_rx=why_rx,
                          live_llm=live_llm, unbound_addressee=unbound_addressee,
                          premise_reader=premise_reader, interrupt_reader=interrupt_reader,
                          _nested=True)

    # Row IC, Session 2 (IC-9): an exact order with a line that cannot be
    # taken — the reading is of the line AS UNDERSTOOD, with what was not taken
    # named, and Enter sends the understood line.
    if (not _nested and not parsed.get("success") and parsed.get("kind") == "if_then"
            and parsed.get("understood")):
        return _if_then_refused(out, parsed, text, _read_again)
    got = _reading_of(out, world, parsed, text, reading, unbound_addressee,
                      parser=parser, state=state)
    if (not _nested and isinstance(got, dict) and got.get("kind") == "refusal"
            and parsed.get("refusal") == "conditional"):
        # §8.3: a condition the line cannot hold is offered back as the
        # exact order it means — a fill-chip, never sent.
        offer = conditional_offer(world, parsed, text, _parse_again)
        if offer:
            got["candidates"] = list(got.get("candidates") or []) + [
                {"label": offer, "line": offer}]
        return got
    return _with_task_rows(world, got, parsed, text, None if _nested else _parse_again)


def _reading_of(out, world, parsed: Dict, text: str, reading: str, unbound_addressee,
                parser=None, state=None) -> Dict[str, Any]:
    from backend.ai.validation import CABINET_ACTIONS
    view = _View(world)
    command = parsed.get("command") if isinstance(parsed.get("command"), dict) else {}
    action = str(command.get("action") or "")
    # Stage 8: the delegation detector (pure) — a foreign commander (in sight
    # or not: his name is public, `_delegation_reading` reads nothing of his
    # place) or a province; a name on no roster is no delegation.
    from backend.commands.delegation import detect_delegation
    deleg = detect_delegation(world, reading, command or None)
    if deleg is not None and deleg.marshal in view.own and (
            deleg.target in view.seen or deleg.target in view.hidden
            or view.region(deleg.target)):
        return _delegation_reading(out, world, view, parsed, deleg)
    if not parsed.get("success"):
        return _failure_reading(out, world, view, parsed, text)
    if command.get("question"):
        if str((command.get("question") or {}).get("kind") or "").startswith("own_"):
            return _own_question_reading(out, world, command["question"])
        return _simple(out, "question", ("head", "A question for Berthier"), ("cost", "costs nothing"))
    if isinstance(parsed.get("own"), dict):
        return _own_reading(out, world, parsed, text)
    if action in _REPORT_ACTIONS:
        return _simple(out, "meta", ("head", "A report from Berthier"), ("cost", "costs nothing"))
    if action == "end_turn":
        return _simple(out, "meta", ("head", "Ends the day"))
    if action in CABINET_ACTIONS or command.get("type") == "diplomatic":
        return _simple(out, "cabinet", ("head", "Diplomacy is the Cabinet’s (F1)"))
    if action in ("debug", "cheat", "meta_command", "unknown", ""):
        return out
    if action in ("army", "set_war_goal"):
        return _staff_book_reading(out, world, action, reading)
    target = str(command.get("target") or "")
    marshal_name = str(command.get("marshal") or "")
    # The executor's order: the unbound-addressee rule (CX-R1 — a named
    # address the roster cannot bind is refused, read off the same reader),
    # then the attack seam, then the target.
    if not marshal_name and unbound_addressee is not None:
        phrase = None
        try:
            phrase = unbound_addressee(command, parsed, world)
        except Exception as exc:
            report(exc, "parse_preview._reading_of: the unbound addressee")
        if phrase:
            return _unknown_reading(out, str(phrase), text, view)
    # A typed attack's object is read off the raw words, as the executor's
    # seam reads it, before its parsed target ("Ney, attack Kutuzoq": the
    # parse corrects the slip, the seam asks in his word).
    # UI6-X16: a named marshal's charge meets the same seam (the executor's).
    if (action == "attack" or (action == "charge" and marshal_name)) \
            and not parsed.get("is_strategic"):
        seam = _attack_seam(out, reading, world, view, view.own.get(marshal_name))
        if seam is not None:
            return seam
    # A name on NO roster reads as the player's own word; a commander out of
    # sight reads on by name (THE DOCTRINE), his place never read.
    aimed = action == "attack" or _verb_of(parsed, command) in _TARGET_VERBS
    # UI6-X71: a pursuit of a word two commanders share ("pursue the Archduke")
    # reads its ONE bearer in sight, as `/command` does (UI6-X61's rule); none
    # in sight, or several, stays the player's unknown word.
    if (target and isinstance(command, dict) and _verb_of(parsed, command) == "pursue"
            and marshal_name in view.own and _target_entity(view, target)[0] == "unknown"):
        from backend.commands.combat_executor import shared_name_word_in, unique_bearer_in_sight
        _word = re.sub(r"^the\s+", "", target.strip(), flags=re.IGNORECASE)
        _word = (shared_name_word_in(_word, world, view.own[marshal_name])
                 if _word and len(_word.split()) == 1 else "")
        _bearer = unique_bearer_in_sight(world, view.own[marshal_name], _word) if _word else None
        if _bearer is not None:
            target = _bearer.name
            command["target"] = _bearer.name
    if (target and aimed and not parsed.get("target_placed_by_the_game")
            and _target_entity(view, target)[0] == "unknown"):
        return _unknown_reading(out, _typed_span(text, target), text, view)
    if not marshal_name:
        # An attack on a man out of sight with no marshal named: no corps can
        # be sent at a place nobody has seen (UI6-X15: `/command` answers "No
        # intelligence on his position", free), and the reading names nothing
        # of where he stands. A sighting on the record is the pick's to read
        # (the corps nearest his last sighting) — Berthier picks or asks.
        if action == "attack" and target in view.hidden:
            out.update(target=humanize_entity_name(target), target_kind="enemy")
            from backend.game_logic.intel_surfaces import last_seen
            if not last_seen(world, view.player, target):
                return _refusal_reading(out, f"No intelligence on {humanize_entity_name(target)}’s position")
        if (action == "scout" and target
                and _target_entity(view, target)[0] in ("enemy", "unseen")):
            # UI6-X20's sweep: the marshal-less scout of a commander —
            # `/command`: "Kutuzov is a commander, Sire, not a province".
            out.update(target=humanize_entity_name(target), target_kind="enemy")
            return _refusal_reading(out, f"{humanize_entity_name(target)} is a commander — name a province")
        if action == "charge":
            # UI6-X16's readback: a bare "charge" answers a standing charge
            # question, or `/command` refuses it ("Charge requires a marshal").
            from backend.commands.combat_executor import pending_glorious_charge_marshal
            if pending_glorious_charge_marshal(world) is not None:
                return _simple(out, "pending", ("head", "A question stands — this line answers it"))
            return _refusal_reading(out, "A charge needs its cavalryman named")
        from backend.commands import group_orders as go
        head = go.collective_head(reading, places=list(getattr(world, "regions", {}) or {}))
        strategic_type = parsed.get("strategic_type") if parsed.get("is_strategic") else None
        if head is not None and ((strategic_type and strategic_type in go.GROUPABLE_STRATEGIC)
                                 or (not strategic_type and action in go.GROUPABLE_ACTIONS)):
            return _collective_reading(out, world, view, head, parsed)
        if str(command.get("type") or "") == "general_retreat":
            from backend.commands import exit_predicate as _xp
            _named = _xp.retreat_destination_commander(text, world)
            if _named is not None:
                # UI6-X39: `/command`'s free refusal - a commander is no place.
                _what = ("a title more than one commander bears"
                         if getattr(_named, "is_title", False) else "a commander")
                return _refusal_reading(
                    out, f"{humanize_entity_name(_named.name)} is {_what} — name a province")
            return _simple(out, "order", ("head", "Every corps falls back"), ("cost", "free"))
        from backend.commands.meta_executor import ADMIN_ACTIONS
        if action in ADMIN_ACTIONS:
            ap = int(world.get_action_cost(action))
            out.update(ap=ap, pool="admin", ap_left=int(getattr(world, "admin_actions_remaining", 0) or 0))
            words = _VERB_WORDS.get(action, action.replace("_", " "))
            target = str(command.get("target") or "")
            head = words[:1].upper() + words[1:] + (f" · {humanize_entity_name(target)}" if target else "")
            return _simple(out, "order", ("head", head), ("cost", _cost_text(ap, "admin", ap == 0)))
        return _simple(out, "needs_marshal", ("head", "No marshal named — Berthier picks or asks"))
    if marshal_name not in view.own:
        foe = view.seen.get(marshal_name) or (
            world.get_marshal(marshal_name) if marshal_name in view.hidden else None)
        if foe is not None:
            return _refusal_reading(
                out, f"{humanize_entity_name(marshal_name)} serves {_court(world, foe.nation)} "
                     f"— he does not answer to us")
        return _unknown_reading(out, _typed_span(text, marshal_name), text, view)
    # D6 (CC-4): a standing head with a tail that would undo it is ASKED
    # first, nothing spent, the working order offered — the relay's own
    # reader (`relay.reorder_suggestion`, the mock chain's read of the tail).
    if parser is not None and parsed.get("dropped_sequel"):
        from backend.commands import relay as _relay
        try:
            reorder = _relay.reorder_suggestion(world, parser, state, parsed)
        except Exception as exc:
            report(exc, "parse_preview._reading_of: relay.reorder_suggestion")
            reorder = None
        if reorder:
            shown = humanize_entity_name(marshal_name)
            out.update(marshal=shown, action=action)
            _refusal_reading(out, f"{shown} — the second order would undo the first")
            out["candidates"] = [{"label": str(reorder.get("command") or ""),
                                  "line": str(reorder.get("command") or "")}]
            return out
    # BA3-X5 (row BA, BA-4): a word of an open day costs no action, so its
    # reading is built without the turn's action pool refusing it — the pool
    # itself is not touched (`battle_day.quoting_a_word`).
    from backend.game_logic import battle_day as _day
    if _day.word_of(world, parsed) is not None:
        with _day.quoting_a_word():
            return _order_reading(out, world, view, parsed, reading if reading != text else text)
    return _order_reading(out, world, view, parsed, reading if reading != text else text)


def _staff_book_reading(out: Dict[str, Any], world, action: str, text: str) -> Dict[str, Any]:
    """Row IC, directives: how a line of the staff's two free books reads — a
    named army (form · add · remove · disband) or the goal of a war — from the
    readers their executor uses (`armies.read_order`, `war_goals.read_order`),
    with the refusal the game would give (a name that cannot be an army's; a
    goal that is no enemy's place). Nothing is written."""
    out.update(action=action, pool="none", free=True, ap=0)
    if action == "army":
        from backend.game_logic import armies
        order = armies.read_order(world, text)
        if order is None:
            return _simple(out, "order", ("head", "The roll of an army"), ("cost", "free"))
        name, op = str(order.get("name") or ""), str(order.get("op") or "")
        if op == "list":
            return _simple(out, "meta", ("head", "Your armies"), ("cost", "costs nothing"))
        kept = armies.find(world, name)
        if op in ("add", "remove", "disband") and kept is None:
            return _refusal_reading(out, f"There is no army called ‘{name}’")
        if op == "form" and kept is None:
            why = armies.name_refusal(world, name)
            if why:
                return _refusal_reading(out, why.rstrip("."))
        good, bad = armies._resolve(world, list(order.get("who") or []))
        if bad and op in ("form", "add"):
            return _refusal_reading(out, f"{', '.join(bad)} — not yours to put in an army")
        who = ", ".join(humanize_entity_name(n) for n in good)
        shown = kept or name
        head = {"form": f"Form the {shown} · {who}" if kept is None else f"The {shown} now holds · {who}",
                "add": f"Add {who} to the {shown}", "remove": f"Remove {who} from the {shown}",
                "disband": f"Disband the {shown}"}.get(op, "The roll of an army")
        out.update(ok=True)
        return _simple(out, "order", ("head", head), ("cost", "free"))
    from backend.game_logic import war_goals
    goal = war_goals.read_order(text)
    if goal is None:
        return _simple(out, "order", ("head", "The goal of a war"), ("cost", "free"))
    if goal.get("op") == "clear":
        if not war_goals.store(world):
            return _refusal_reading(out, "No war goal is set")
        out.update(ok=True)
        return _simple(out, "order", ("head", "Clear the war goal"), ("cost", "free"))
    kind, named, _court, refused = war_goals.aim(world, str(goal.get("what") or ""))
    if refused:
        # the order's own refusal, in one short clause (its first sentence, no "Sire")
        short = _first_sentence(refused.split(" — ")[0].replace(", Sire", "")).rstrip(".")
        return _refusal_reading(out, short)
    shown = humanize_entity_name(named) + ("’s army" if kind == "army" else "")
    out.update(ok=True, target=humanize_entity_name(named),
               target_kind="province" if kind == "place" else "enemy")
    return _simple(out, "order", ("head", f"The war goal · {shown}"), ("cost", "free"))


def _reason_copy(world, clause) -> str:
    """UI6-X18: the reason refusal's short words, from what its clause is
    about (`llm_client.reason_clause_subject`, `/command`'s own reader) —
    "reports the enemy" was said of a friend, a province and a bridge."""
    from backend.ai.llm_client import reason_clause_subject
    kind, subject = reason_clause_subject(str(clause or ""), world)
    if kind == "enemy":
        return _REFUSAL_COPY["reason"]
    if kind in ("friend", "commander", "court", "province") and subject:
        return f"that reports on {subject} but gives no order"
    return "that is a report, not an order"


def _failure_reading(out, world, view: _View, parsed: Dict, text: str) -> Dict[str, Any]:
    error = str(parsed.get("error") or "")
    if parsed.get("refusal"):
        copy = _REFUSAL_COPY.get(str(parsed.get("refusal")), _REFUSAL_DEFAULT)
        if str(parsed.get("refusal")) == "reason":
            copy = _reason_copy(world, (parsed.get("refusal_detail") or {}).get("clause"))
        return _refusal_reading(out, copy[:1].upper() + copy[1:])
    if parsed.get("kind") == "enemy_addressee":
        # WO-1's refusal names the man and his side, in sight or not (THE
        # DOCTRINE — the side is public, only the place is fogged).
        name = str(parsed.get("unknown_name") or "")
        foe = view.seen.get(name) or (world.get_marshal(name) if name in view.hidden else None)
        if foe is not None:
            return _refusal_reading(
                out, f"{humanize_entity_name(name)} serves {_court(world, foe.nation)} "
                     f"— he does not answer to us")
        return _unknown_reading(out, _typed_span(text, name), text, view)
    if parsed.get("kind") == "fallen_recipient":
        return _refusal_reading(out, "That reward goes to a man we have lost")
    if parsed.get("kind") == "task_line":
        # Row IC, Session 2 (IC-8, §8.3): a stretch of country, "their main
        # army" — refused free, the nearest real sentences as fill-chips.
        _refusal_reading(out, str(parsed.get("short") or "That is no order a marshal can carry"))
        out["candidates"] = [{"label": str(line), "line": str(line)}
                             for line in (parsed.get("offers") or []) if line]
        return out
    if parsed.get("kind") in ("compound_pronoun", "arrival_charge", "two_orders"):
        # UI6-X43: `/command`'s free refusal, said the same way (names only).
        return _refusal_reading(out, error.replace(" Nothing has been relayed.", "")
                                .replace(", Sire", ""))
    if parsed.get("unknown_name"):
        return _unknown_reading(out, str(parsed.get("unknown_name")), text, view)
    if error.startswith("Unknown action"):
        return out
    return out


def _second_names(world, text: str, out: Dict[str, Any]) -> Dict[str, Any]:
    """UI6-X25 (widened): "Ney, attack Mack and Kutuzov" acts on the first
    name and `/command` says which names it did not act on; the readback
    warns the same (names only, never a place)."""
    if not isinstance(out, dict) or out.get("kind") not in ("order", "refusal"):
        return out
    from backend.commands import proper_name as pn
    man = world.get_marshal(str(out.get("marshal") or "")) if out.get("marshal") else None
    for note in pn.second_name_notes(text, world, getattr(man, "name", None)):
        out["parts"] = list(out.get("parts") or []) + [_part("warn", note.split(" — ")[0])]
    return out


def preview(world, line: str, *, llm_state: Callable[[], Dict], epoch: int = 0,
            lost_marshal_refusal: Optional[Callable] = None, why_rx=None,
            live_llm=None, posts_in_flight: Optional[Callable[[], bool]] = None,
            unbound_addressee: Optional[Callable] = None,
            premise_reader: Optional[Callable] = None,
            interrupt_reader: Optional[Callable] = None) -> Dict[str, Any]:
    """The reading of `line` on `world` — see the module docstring. Never
    raises: a failure (a board changing under a stray read) is kind "none".

    The `/command` pieces ride in from the route (this module never imports
    `backend.main`): `llm_state` (the parse input), `epoch` (the cache's
    clock), `lost_marshal_refusal`, `why_rx`, `live_llm` (whose own gate says
    whether the model would read the line), `posts_in_flight`,
    `unbound_addressee` (the executor's CX-R1 reader) and `premise_reader`
    (`(text, world) -> (rebuilt text, refused)`, the premise stage)."""
    text = str(line or "")[:500]
    out = _base(text, epoch)
    if world is None:
        return out
    try:
        if posts_in_flight is not None and posts_in_flight():
            return _simple(out, "busy")
    except Exception as exc:
        report(exc, "parse_preview.preview: posts in flight")
    if not _LOCK.acquire(timeout=_LOCK_WAIT_S):
        return _simple(out, "busy")
    token = _ptrace._TRACE.set(None)
    try:
        readers = dict(llm_state=llm_state, epoch=epoch,
                       lost_marshal_refusal=lost_marshal_refusal, why_rx=why_rx,
                       live_llm=live_llm, unbound_addressee=unbound_addressee,
                       premise_reader=premise_reader, interrupt_reader=interrupt_reader)
        # Row IC (the directive): a line addressed to several corps reads as
        # the list it will open — who, how many can go, what it costs — from
        # the list's own builder (ONE reader; `directive.readback`).
        from backend.commands import directive as _directive
        several = _directive.readback(world, text, out, readers)
        if several is not None:
            return several
        reading = _second_names(world, text, read_one(world, text, **readers))
        for private in ("_quote", "_marches"):
            reading.pop(private, None)
        return reading
    except Exception as exc:
        report(exc, "parse_preview.preview: the readback")
        return _base(text, epoch)
    finally:
        _ptrace._TRACE.reset(token)
        _LOCK.release()


def read_one(world, line: str, *, llm_state: Callable[[], Dict], epoch: int = 0,
             lost_marshal_refusal: Optional[Callable] = None, why_rx=None,
             live_llm=None, unbound_addressee: Optional[Callable] = None,
             premise_reader: Optional[Callable] = None,
             interrupt_reader: Optional[Callable] = None) -> Dict[str, Any]:
    """Row IC (the directive): ONE line's reading — the pure core `/parse_preview`
    answers with — for a caller that makes several (the list of an order to
    several marshals reads each man's own line through this, so the list, the
    read-back and the price check are one reader). The caller holds
    `reading()`. Besides the wire's keys the dict may carry `_quote` (the
    order's own quote, for its riders); never raises past its own report."""
    text = str(line or "")[:500]
    out = _base(text, epoch)
    if world is None:
        return out
    return _read_line(world, text, out, llm_state=llm_state, epoch=epoch,
                      lost_marshal_refusal=lost_marshal_refusal, why_rx=why_rx,
                      live_llm=live_llm, unbound_addressee=unbound_addressee,
                      premise_reader=premise_reader, interrupt_reader=interrupt_reader)


@contextlib.contextmanager
def reading(wait_s: float = 2.0):
    """Hold the read-back's lock (its mock-only parser is ONE instance with
    per-parse state) and mute the parse trace while a caller makes its
    readings — a request's own trace is put back as it stood on the way out.
    Yields whether the lock was taken (a caller under the state lock always
    gets it; the readings are made either way)."""
    took = _LOCK.acquire(timeout=wait_s)
    token = _ptrace._TRACE.set(None)
    try:
        yield took
    finally:
        _ptrace._TRACE.reset(token)
        if took:
            _LOCK.release()


def mock_parse(world, line: str, llm_state: Callable[[], Dict], epoch: int = 0) -> Dict[str, Any]:
    """`line` read by the built-in reader alone — never the model (the list's
    probe on the read-only road). The caller holds `reading()`."""
    state = _llm_state(world, llm_state, epoch)
    parser = _preview_parser()
    parser.llm.live = None
    parser.llm.would_consult = False
    with contextlib.redirect_stdout(io.StringIO()):
        return parser.parse(str(line or "")[:500], state, world=world)
