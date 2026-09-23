"""First contact — what Berthier says to a player who has typed something
that is neither an order nor a question about the board.

The keyless first-contact report (September 23, 2026) drove 92 wild
sentences at the shipped fast parser and found ONE canned reply fitting
everything: a greeting, `quit`, `undo`, `what now`, `I'm stuck` and `win the
war` all drew the same "Forgive me, Sire, but I cannot interpret that order"
— a reply that never once names `help`, `what can I do` or `status`, and
never points `quit` / `restart` / `undo` at the pause menu. A stuck player
was handed the one sentence that could not unstick them.

This module is the ONE source for that first contact — the vocabulary the
mock chain routes on AND the copy the help executor prints — so the two can
never drift, and so Berthier's shrug can quote the same three doors.

Design rules (all pinned in `tests/test_first_contact_keyless.py`):

* **Anchored, whole-line, closed vocabulary.** Every pattern matches the
  WHOLE address-stripped line. An order addressed to a marshal ("Ney, go
  back") never reaches this desk — the address is a marshal's name, not the
  desk's — and no order verb the parser knows appears in any pattern.
* **Nothing is relayed.** Every kind here is answered by `help` (free) or by
  the `status` desk's `options` answer (free). No AP, no state, no LLM.
* **The desk runs BEFORE the question arm and the order chain** in
  `llm_client._parse_with_mock_chain`, and never in front of the literal
  argument commands (`save`, `load`, `debug`, cheats).
* **Fail closed.** A line the desk does not recognise returns None and the
  parse continues exactly as before.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional

# ── the lever ────────────────────────────────────────────────────────────
FIRST_CONTACT_DESK_ACTIVE = True

# ── the three doors (quoted by the shrug, the greeting and the goal) ──────
THREE_DOORS = ("Type 'what can I do' for the orders this board will take, "
               "'status' for the state of the board, or 'help' for the "
               "full command reference.")
ESCAPE_MENU_LINE = ("The Emperor's own affairs — saving, loading, the "
                    "settings, a new campaign, the main menu — are on the "
                    "pause menu: press Esc.")
CABINET_DOOR = "For any matter of state, press F1 for the Cabinet."

# The kinds the help executor answers here; `options` is answered by the
# question desk (`question_desk._answer_options`) so the counsel stays ONE
# source with Berthier's shrug and the "what can I do" question.
FIRST_CONTACT_HELP_KINDS = frozenset({"greeting", "escape_menu", "undo", "goal"})
FIRST_CONTACT_KINDS = FIRST_CONTACT_HELP_KINDS | {"options"}

_ADDRESS_RE = re.compile(
    r"^\s*(?:(?:marshal|general|chief\s+of\s+staff|monsieur)\s+)?berthier\s*[,:!?]?\s*",
    re.IGNORECASE)
_TRAIL = r"(?:\s+(?:please|now|then|berthier|sire|again|already))*"

_GREETING_RE = re.compile(
    r"^(?:hello|hi|hey|hiya|howdy|greetings|salutations|bonjour|salut|yo|sup"
    r"|good\s+(?:morning|day|afternoon|evening)|what'?s\s+up|how\s+are\s+you"
    r"|how\s+goes\s+it|how\s+do\s+you\s+do|berthier)"
    r"(?:\s+(?:there|berthier|sire|general|marshal|everyone|all|again|to\s+you|"
    r"my\s+friend))*" + _TRAIL + r"$", re.IGNORECASE)

_ESCAPE_RE = re.compile(
    r"^(?:(?:i\s+(?:want|need|would\s+like|wish)\s+to\s+|let\s+me\s+|can\s+i\s+"
    r"|how\s+do\s+i\s+|how\s+to\s+|how\s+can\s+i\s+)?"
    r"(?:"
    r"(?:quit|exit|leave|close|pause|restart|reload|resume)"
    r"(?:\s+(?:the|this|my))?(?:\s+(?:game|campaign|war\s+room|app|program|session))?"
    r"|(?:go\s+(?:to\s+)?(?:the\s+)?)?(?:main\s+|pause\s+|game\s+)?menu"
    r"|options|settings|preferences|config(?:uration)?|volume|sound|music"
    r"|full\s*screen|resolution|graphics"
    r"|new\s+game|new\s+campaign|start\s+(?:over|again|afresh|a\s+new\s+(?:game|campaign))"
    r"|begin\s+again|restart\s+the\s+(?:game|campaign|war)"
    r"|(?:i\s+)?(?:give\s+up|resign|quit)|i\s+quit|surrender\s+the\s+game"
    r"|load\s+(?:a\s+|my\s+|the\s+|an?\s+earlier\s+)?(?:save|saved\s+game|save\s+file|game|campaign)"
    r"|save\s+(?:my\s+|the\s+|this\s+)?(?:game|progress|campaign)"
    r"|save"
    r")"
    r")" + _TRAIL + r"$", re.IGNORECASE)

_UNDO_RE = re.compile(
    r"^(?:(?:can\s+i\s+|how\s+do\s+i\s+|how\s+can\s+i\s+|i\s+want\s+to\s+|let\s+me\s+|please\s+)?"
    r"(?:undo|un-do|redo|revert|rewind|go\s+back|take\s+(?:that|it|this)\s+back"
    r"|take\s+back\s+(?:that|the\s+last|my\s+last)(?:\s+\w+)?)"
    r"(?:\s+(?:that|it|this|the\s+last\s+\w+|my\s+last\s+\w+|a\s+turn|the\s+turn|"
    r"that\s+order|that\s+move|that\s+command))?"
    r"|oops|whoops|i\s+didn'?t\s+mean\s+(?:that|it|to)|that\s+was\s+a\s+mistake"
    r"|wrong\s+(?:order|command|marshal|man)|i\s+made\s+a\s+mistake"
    r")" + _TRAIL + r"$", re.IGNORECASE)

_STUCK_RE = re.compile(
    r"^(?:what\s+now|now\s+what|what\s+next|what(?:'s|\s+is)\s+next|and\s+now"
    r"|(?:so\s+|and\s+)?then\s+what|what\s+then|so\s+what\s+now|what\s+else"
    r"|what\s+(?:to\s+do|do\s+(?:i|we)\s+do|should\s+(?:i|we)\s+do|shall\s+(?:i|we)\s+do"
    r"|can\s+(?:i|we)\s+do|could\s+(?:i|we)\s+do|must\s+(?:i|we)\s+do|ought\s+(?:i|we)\s+(?:to\s+)?do"
    r"|am\s+i\s+(?:supposed|meant)\s+to\s+do|are\s+we\s+(?:supposed|meant)\s+to\s+do"
    r"|do\s+you\s+(?:suggest|advise|recommend|think|propose)"
    r"|would\s+you\s+(?:do|suggest|advise|recommend|propose)"
    r"|are\s+(?:my|our|the)\s+(?:options|choices|moves))"
    r"(?:\s+(?:now|next|today|first|here|this\s+turn))?"
    r"|i(?:'m|\s+am|m)\s+(?:stuck|lost|confused|not\s+sure(?:\s+what\s+to\s+do)?"
    r"|at\s+a\s+loss|out\s+of\s+ideas)|stuck|lost|confused"
    r"|(?:i\s+(?:have|got)\s+|i've\s+(?:got\s+)?)?no\s+(?:idea|clue)(?:\s+what\s+to\s+do)?"
    r"|i\s+(?:don'?t|do\s+not)\s+know(?:\s+what\s+to\s+do(?:\s+next)?)?|idk|dunno"
    r"|any\s+(?:ideas?|suggestions?|advice|tips|thoughts|recommendations?)"
    r"|suggestions?|ideas?|advice|advise\s+me|counsel\s+me|guide\s+me"
    r"|help\s+me(?:\s+out)?|i\s+need\s+help|i\s+need\s+advice|what\s+are\s+my\s+choices"
    r")" + _TRAIL + r"$", re.IGNORECASE)

_GOAL_RE = re.compile(
    r"^(?:win|win\s+(?:the|this)\s+(?:war|game|campaign)"
    r"|(?:how\s+(?:do|can|could|would|should)\s+(?:i|we|you)\s+|how\s+to\s+)win"
    r"(?:\s+(?:the|this)\s+(?:war|game|campaign))?"
    r"|what(?:'s|\s+is)\s+the\s+(?:goal|objective|point|aim|object|purpose"
    r"|win\s+condition|victory\s+condition)"
    r"(?:\s+(?:of\s+(?:the|this)\s+(?:game|campaign|war)|here))?"
    r"|what\s+(?:am\s+i|are\s+we)\s+(?:supposed|meant|trying)\s+to\s+(?:do|achieve|accomplish)"
    r"|what\s+do\s+(?:i|we)\s+need\s+to\s+do\s+to\s+win"
    r"|how\s+do\s+(?:i|we|you)\s+play(?:\s+(?:this|the\s+game))?"
    r"|how\s+does\s+(?:this|the\s+game|it)\s+work|what\s+is\s+this(?:\s+game)?"
    r"|explain\s+the\s+game|what\s+do\s+i\s+do\s+here|what\s+is\s+the\s+game"
    r")" + _TRAIL + r"$", re.IGNORECASE)

# Bare `save …` and a bare `load` are the executor's own literal-argument
# meta-commands (they save and list saves today) and must keep working; the
# desk never stands in front of them.
_LITERAL_META_PREFIXES = ("save", "/debug", "debug ")


def _desk_text(text: str) -> str:
    """The line the desk reads: address stripped, trimmed, one-spaced,
    trailing punctuation dropped, lowercase."""
    line = _ADDRESS_RE.sub("", str(text or ""))
    line = re.sub(r"\s+", " ", line).strip().strip("!.,;:?").strip()
    return line.lower()


def first_contact_route(text: str) -> Optional[Dict]:
    """The first-contact kind of `text`, or None.

    Returns `{"kind": ..., "asked": <original>}` for a greeting, a word for
    the pause menu (`escape_menu`), an undo (`undo`), a stuck phrasing
    (`options` — answered by the question desk) or a question about the
    goal of the game (`goal`). None for everything else, including every
    line that starts with a literal-argument meta-command.
    """
    if not FIRST_CONTACT_DESK_ACTIVE:
        return None
    raw = str(text or "")
    lowered = raw.strip().lower()
    if not lowered or lowered.startswith(_LITERAL_META_PREFIXES) or lowered == "load":
        return None
    # A bare question mark is the oldest "what now" there is.
    if lowered.strip("?! .") == "" and "?" in lowered:
        return {"kind": "options", "asked": raw}
    line = _desk_text(raw)
    if not line:
        # A bare "Berthier" / "Berthier?" is a greeting to the desk itself.
        return ({"kind": "greeting", "asked": raw}
                if _ADDRESS_RE.match(raw) else None)
    if line in ("berthier",) or _GREETING_RE.match(line):
        return {"kind": "greeting", "asked": raw}
    if _UNDO_RE.match(line):
        return {"kind": "undo", "asked": raw}
    if _ESCAPE_RE.match(line):
        return {"kind": "escape_menu", "asked": raw}
    if _GOAL_RE.match(line):
        return {"kind": "goal", "asked": raw}
    if _STUCK_RE.match(line):
        return {"kind": "options", "asked": raw}
    return None


# ── the answers ──────────────────────────────────────────────────────────

def _counsel(world, limit: int = 3) -> List[str]:
    """The ONE counsel source (`ai/counsel.what_can_i_do`), or []."""
    if world is None:
        return []
    try:
        from backend.ai.counsel import what_can_i_do
        return list(what_can_i_do(world, getattr(world, "player_nation", None),
                                  limit=limit) or [])
    except Exception:
        return []


def _standing_order_holder(world) -> Optional[str]:
    """The display name of the first player marshal under a standing order,
    so the undo answer can name the one thing that CAN be stood down."""
    if world is None:
        return None
    try:
        from backend.display_names import humanize_entity_name
        for marshal in world.get_player_marshals():
            if getattr(marshal, "strategic_order", None):
                return humanize_entity_name(marshal.name)
    except Exception:
        return None
    return None


def _is_open_ended(world) -> bool:
    """Every Europe world plays sandbox today (victory and defeat stay with
    the Victory & Objectives Pass, ROADMAP 12–13). The goal answer reads the
    world's own flag so it turns honest by itself the day that pass lands."""
    if world is None:
        return True
    try:
        return bool(getattr(world, "sandbox_mode", True))
    except Exception:
        return True


def answer_first_contact(kind: str, asked: str, world) -> Optional[str]:
    """Berthier's answer for a `FIRST_CONTACT_HELP_KINDS` kind, or None."""
    kind = str(kind or "")
    counsel = _counsel(world)
    first = f" This morning, '{counsel[0]}' would be carried out at once." if counsel else ""
    if kind == "greeting":
        return (f"Berthier bows. \"Sire. The army stands ready for your "
                f"orders.{first} {THREE_DOORS} {CABINET_DOOR} "
                f"Esc opens the pause menu.\"")
    if kind == "escape_menu":
        return (f"Berthier sets down his pen. \"That is the Emperor's own "
                f"business, Sire, not the army's. {ESCAPE_MENU_LINE} "
                f"Nothing has been relayed.\"")
    if kind == "undo":
        holder = _standing_order_holder(world)
        cancel = (f" {holder}'s standing order can be stood down — "
                  f"'cancel {holder}' — and that is free."
                  if holder else
                  " A standing march or hold can be stood down with "
                  "'cancel <marshal>', free.")
        return (f"Berthier shakes his head. \"There is no unsaying an order "
                f"once relayed, Sire — what has gone out has gone out.{cancel} "
                f"An earlier day can be recalled from a saved game on the "
                f"pause menu (Esc). Nothing has been relayed.\"")
    if kind == "goal":
        if _is_open_ended(world):
            goal = ("This campaign is played open-ended, Sire — there is no "
                    "laurel to be handed out; the war is the game. Take "
                    "provinces, keep the marshals loyal and the treasury "
                    "whole, and make peace on your own terms. The Strategic "
                    "Ledger (press T) keeps the score and the Cabinet (F1) "
                    "holds every court.")
        else:
            goal = ("The campaign's objectives are on the Strategic Ledger, "
                    "Sire (press T) — that is the measure of the war.")
        today = ""
        if counsel:
            today = " Today: " + "; ".join(f"'{line}'" for line in counsel[:3]) + "."
        return f"Berthier unrolls the map. \"{goal}{today} {THREE_DOORS}\""
    return None
