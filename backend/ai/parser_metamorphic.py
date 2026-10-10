"""DD-0 S3 "The Command Road" — instrument 2, THE METAMORPHIC CORPUS
(October 10, 2026; PRE_DEPLOY_PLAN.md §3.0; rules SYSTEMS_REFERENCE.md §101).

From the golden rows (`tests/data/parser_golden_corpus.json`) generate
variants whose reading is KNOWN by construction:

  relation `same`      the variant must parse to the SAME reading as the
                       original row (compared on the harness's own keys —
                       marshal, action, target, type, strategic_type,
                       target_stance, requested_type, diplo — against the
                       parse of the ORIGINAL on the same world, never
                       against `expected`): please, an honorific, a
                       trailing reason, a dash aside, a contraction, a
                       leading-verb typo, the address moved to the tail,
                       the second name as a role, lowercase;
  relation `refusal`   the variant must be refused — a negation;
  relation `question`  the variant must NOT execute the row's order — a
                       modal question, a hedge (a question, a refusal or
                       the help desk all satisfy it).

Thousands of cases from a few hundred authored ones; it catches by
construction what the review rounds have been catching by hand. Each
family carries an APPLICABILITY predicate so it fires only where its
meaning is clear (the exclusions are the landing record's, §101); every
failure is reported with the variant's parse trace (§100), so the
worklist it produces is attributed by stage.

The harness is `tests/test_dd0_metamorphic_corpus.py` (a ratchet against
`tests/data/metamorphic_known_failures.json`) and the CLI
`tools/metamorphic_census.py`.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Optional, Tuple

# ── what an order row is ─────────────────────────────────────────────────

# The marshal-order families the transforms apply to. A diplomatic row, a
# cheat, a save / load, a question (status / help), an order of state and a
# row whose contract is "this fails" are outside every family: politeness
# on a letter to Prussia is not the same relation, and a refusal row has no
# reading to keep.
ORDER_ACTIONS = frozenset({
    "attack", "move", "hold", "defend", "retreat", "scout", "fortify",
    "unfortify", "drill", "charge", "bombard", "pursue", "support", "wait",
    "garrison", "recruit", "build", "repair", "form_square", "cancel",
    "stance_change", "restrain",
})

# A row with any of these in its utterance is a compound, a condition, a
# relative place or a deferral — the families' meaning blurs there (a
# "please" before "then hold" moves the split; a negation inside an `if`
# is PARSE-NEG's own verdict), so they are left to their own pins.
_EXCLUDED_RX = re.compile(
    r"[?]|\b(if|when|unless|until|once|then|and|but|while|after|before|"
    r"home|back|again|same|him|her|them|there|it|not|never|no|don'?t|"
    r"later|tomorrow|next turn|first|instead|rather)\b|[;:]|\.\.\.|—|-\s", re.I)

# `Name, <order>` / `Name <order>` / `Marshal Name, <order>` — the address
# shape the honorific, the word-order and the modal families need.
_HONORIFIC_RX = re.compile(r"^(?:Marshal|General|Gen\.|Maréchal|Marechal)\s+", re.I)
PLAYER_HONORIFIC = "Marshal"
_ADDRESS_RX = re.compile(
    r"^(?P<hon>(?:Marshal|General|Gen\.|Maréchal|Marechal)\s+)?"
    r"(?P<name>[A-Z][A-Za-z'’-]+)(?P<sep>,\s+|\s+)(?P<rest>\S.*)$", re.I)

# The verbs an order may lead with. The negation, the modal question and
# the typo families fire only on a line whose first word after the address
# is one of these — "do not" before a filler ("hold on, Ney, retreat"), a
# first person ("I attack Mack") or an honorific is not a negated ORDER.
ORDER_VERBS = frozenset({
    "attack", "move", "march", "scout", "defend", "hold", "retreat", "fortify",
    "recruit", "bombard", "drill", "charge", "pursue", "support", "garrison",
    "build", "repair", "advance", "withdraw", "dig", "unfortify", "form",
    "cancel", "go", "head", "proceed", "take", "wait", "stand", "protect",
    "guard", "aid", "help", "join", "push", "retire", "fall", "strike", "hit",
    "engage", "cover", "reinforce", "follow", "chase", "hunt", "ride", "occupy",
    "seize", "secure", "entrench", "shift", "deploy", "onward", "storm",
    "assault", "raise", "levy", "construct", "erect", "mend", "restore",
})


@dataclass
class Variant:
    id: str
    family: str
    relation: str          # same | refusal | question
    utterance: str
    row_id: str
    world: str
    original: str
    note: str = ""


@dataclass
class Family:
    name: str
    relation: str
    make: Callable[[str, Dict], List[Tuple[str, str]]]   # (utterance, row) -> [(variant, note)]
    applies: Callable[[str, Dict], bool] = field(default=lambda u, r: True)


def _typo_verbs() -> Tuple[str, ...]:
    from backend.ai.llm_client import _TYPO_VERBS
    return tuple(_TYPO_VERBS)


def is_order_row(row: Dict) -> bool:
    exp = row.get("expected") or {}
    if exp.get("success") is False or row.get("live_only"):
        return False
    if exp.get("diplo") or exp.get("dropped_sequel") or exp.get("strategic_condition"):
        return False
    if exp.get("attack_on_arrival") or exp.get("warning_contains") or exp.get("error_contains"):
        return False
    action = exp.get("action")
    if action not in ORDER_ACTIONS:
        return False
    return not _EXCLUDED_RX.search(row["utterance"])


def _leading_verb(utterance: str) -> Optional[Tuple[int, int, str]]:
    """The (start, end, word) of the order's first word after an address —
    None unless that word is one of `ORDER_VERBS`."""
    m = _ADDRESS_RX.match(utterance)
    rest_start = m.start("rest") if m else 0
    rest = utterance[rest_start:]
    w = re.match(r"[A-Za-z]+", rest)
    if not w or w.group(0).lower() not in ORDER_VERBS:
        return None
    return rest_start + w.start(), rest_start + w.end(), w.group(0)


def _single_clause(u: str, row: Dict) -> bool:
    """One order, one clause: no comma but the address's own."""
    m = _ADDRESS_RX.match(u)
    rest = m.group("rest") if m else u
    return "," not in rest


def _addressed_single(u: str, row: Dict) -> bool:
    return _addressed(u, row) and _single_clause(u, row)


# ── the families ─────────────────────────────────────────────────────────

def _please(u: str, row: Dict):
    out = [(f"please, {u}", "leading please"), (f"{u}, please", "trailing please")]
    m = _ADDRESS_RX.match(u)
    if m and m.group("sep").strip() == ",":
        out.append((f"{m.group('name')}, please {m.group('rest')}", "please after the address"))
    return out


def _honorific(u: str, row: Dict):
    m = _ADDRESS_RX.match(u)
    if not m:
        return []
    if m.group("hon"):
        return [(u[len(m.group("hon")):], "honorific dropped")]
    # The PLAYER's honorific, typed before the name — input text, not prose
    # the game shows (the SF7-S7 census styles shown names via marshal_title).
    return [(PLAYER_HONORIFIC + " " + u, "honorific added")]


def _addressed(u: str, row: Dict) -> bool:
    m = _ADDRESS_RX.match(u)
    if not m:
        return False
    marshal = (row.get("expected") or {}).get("marshal")
    return bool(marshal) and m.group("name").lower() == str(marshal).lower()


def _reason_tail(u: str, row: Dict):
    return [(f"{u} because the men are ready", "because-clause"),
            (f"{u}, the men are rested", "comma reason")]


def _dash_aside(u: str, row: Dict):
    return [(f"{u} — thank you", "dash aside"), (f"{u} - at once", "hyphen aside")]


_CONTRACTIONS = (
    (r"\bdo not\b", "don't"), (r"\bit is\b", "it's"), (r"\bwe are\b", "we're"),
    (r"\bI am\b", "I'm"), (r"\blet us\b", "let's"), (r"\bcannot\b", "can't"),
    (r"\bwill not\b", "won't"), (r"\byou are\b", "you're"), (r"\bI would\b", "I'd"),
    (r"\bI will\b", "I'll"), (r"\bwe will\b", "we'll"), (r"\bthat is\b", "that's"),
    (r"\bwhat is\b", "what's"), (r"\bhe is\b", "he's"), (r"\bthey are\b", "they're"),
)


def _contraction(u: str, row: Dict):
    out = []
    for long_rx, short in _CONTRACTIONS:
        if re.search(long_rx, u):
            out.append((re.sub(long_rx, short, u, count=1), f"contracted {short}"))
        long_form = re.sub(r"\\b", "", long_rx)
        if re.search(r"\b" + re.escape(short) + r"\b", u, re.I):
            out.append((re.sub(r"\b" + re.escape(short) + r"\b", long_form, u, count=1),
                        f"expanded {short}"))
    return out


def _verb_typo(u: str, row: Dict):
    lv = _leading_verb(u)
    if not lv:
        return []
    s, e, word = lv
    low = word.lower()
    if low not in _typo_verbs() or len(low) < 5:
        return []
    # one adjacent transposition inside the word (never the first letter —
    # the repair pass keys on it)
    i = len(low) // 2
    typo = low[:i] + low[i + 1] + low[i] + low[i + 2:]
    if typo == low:
        return []
    cased = typo if word.islower() else typo.capitalize()
    return [(u[:s] + cased + u[e:], f"'{word}' → '{cased}'")]


def _word_order(u: str, row: Dict):
    m = _ADDRESS_RX.match(u)
    if not m or m.group("hon") or m.group("sep").strip() != "," or "," in m.group("rest"):
        return []
    return [(f"{m.group('rest')}, {m.group('name')}", "address moved to the tail")]


def _second_name_role(u: str, row: Dict):
    exp = row.get("expected") or {}
    if exp.get("action") not in ("attack", "move", "pursue", "hold"):
        return []
    marshal = exp.get("marshal")
    if not marshal:
        return []
    other = "Lannes" if str(marshal).lower() != "lannes" else "Soult"
    return [(f"{u} with {other} in support", f"{other} in support")]


def _lowercase(u: str, row: Dict):
    if u == u.lower():
        return []
    return [(u.lower(), "all lowercase")]


def _negation(u: str, row: Dict):
    lv = _leading_verb(u)
    if not lv:
        return []
    s, e, word = lv
    return [(u[:s] + "do not " + word.lower() + u[e:], "do not <verb>"),
            (u[:s] + "never " + word.lower() + u[e:], "never <verb>")]


def _modal_question(u: str, row: Dict):
    m = _ADDRESS_RX.match(u)
    if not m or not _leading_verb(u):
        return []
    return [(f"should {m.group('name')} {m.group('rest')}?", "should <marshal> <order>?")]


def _hedge(u: str, row: Dict):
    return [(f"maybe {u}", "maybe"), (f"perhaps {u}", "perhaps")]


FAMILIES: List[Family] = [
    Family("please", "same", _please),
    Family("honorific", "same", _honorific, _addressed),
    Family("reason_tail", "same", _reason_tail),
    Family("dash_aside", "same", _dash_aside),
    Family("contraction", "same", _contraction),
    Family("verb_typo", "same", _verb_typo),
    Family("word_order", "same", _word_order, _addressed),
    Family("second_name_role", "same", _second_name_role, _addressed_single),
    Family("lowercase", "same", _lowercase),
    Family("negation", "refusal", _negation, _single_clause),
    Family("modal_question", "question", _modal_question, _addressed_single),
    Family("hedge", "question", _hedge),
]


def generate(rows: Iterable[Dict], families: Optional[Iterable[str]] = None) -> List[Variant]:
    """Every variant of every order row, for every world the row names."""
    wanted = set(families) if families else None
    out: List[Variant] = []
    for row in rows:
        if not is_order_row(row):
            continue
        worlds = ("legacy", "1805") if row.get("world", "any") == "any" else (row["world"],)
        for fam in FAMILIES:
            if wanted and fam.name not in wanted:
                continue
            if not fam.applies(row["utterance"], row):
                continue
            for n, (variant, note) in enumerate(fam.make(row["utterance"], row)):
                if variant == row["utterance"]:
                    continue
                for world in worlds:
                    out.append(Variant(
                        id=f"{row['id']}::{fam.name}#{n}@{world}", family=fam.name,
                        relation=fam.relation, utterance=variant, row_id=row["id"],
                        world=world, original=row["utterance"], note=note))
    return out


# ── the relation check ───────────────────────────────────────────────────

READING_KEYS = ("marshal", "action", "target", "type", "target_stance", "requested_type")


def reading_of(result: Dict) -> Dict:
    """The harness's own comparison keys, off a parse result."""
    cmd = (result.get("command") or {}) if isinstance(result, dict) else {}
    out = {"success": bool(result.get("success"))}
    for k in READING_KEYS:
        out[k] = cmd.get(k)
    out["strategic_type"] = result.get("strategic_type") if result.get("is_strategic") else None
    diplo = cmd.get("diplomatic_data")
    if isinstance(diplo, dict):
        out["diplo"] = {k: diplo.get(k) for k in ("action", "proposal_type", "target_nation")}
    return out


def _is_question_or_refusal(result: Dict, original_action: Optional[str]) -> bool:
    if not result.get("success"):
        return True
    cmd = result.get("command") or {}
    if result.get("refusal") or cmd.get("refusal"):
        return True
    return cmd.get("action") in ("status", "help") or bool(cmd.get("question"))


def judge(variant: Variant, original: Dict, varied: Dict) -> Optional[str]:
    """None when the relation holds, else one line saying how it broke."""
    if variant.relation == "same":
        a, b = reading_of(original), reading_of(varied)
        if a == b:
            return None
        diffs = [f"{k}: {a.get(k)!r} → {b.get(k)!r}" for k in a if a.get(k) != b.get(k)]
        return "reading changed — " + "; ".join(diffs)
    if variant.relation == "refusal":
        if not varied.get("success") and (varied.get("refusal") or (varied.get("command") or {}).get("refusal")):
            return None
        if not varied.get("success"):
            return "refused without a refusal kind (a shrug, not PARSE-NEG's refusal)"
        cmd = varied.get("command") or {}
        return f"EXECUTED a negated order as {cmd.get('action')!r} on {cmd.get('target')!r}"
    if variant.relation == "question":
        orig_action = (original.get("command") or {}).get("action")
        if _is_question_or_refusal(varied, orig_action):
            return None
        cmd = varied.get("command") or {}
        return f"EXECUTED a {variant.family} as {cmd.get('action')!r} on {cmd.get('target')!r}"
    return f"unknown relation {variant.relation!r}"


# ── running it ───────────────────────────────────────────────────────────

@dataclass
class Outcome:
    variant: Variant
    verdict: Optional[str]
    trace: List[Dict]
    last_stage: Optional[str]


def run(rows: Iterable[Dict], families: Optional[Iterable[str]] = None,
        limit: Optional[int] = None, with_trace: bool = True) -> List[Outcome]:
    """Parse every variant beside its original on a fresh parser per world;
    returns one Outcome per variant (the verdict None when the relation
    held)."""
    import contextlib
    import io
    from backend.ai import parse_trace, parser_eval
    from backend.commands.parser import CommandParser

    variants = generate(rows, families)
    if limit:
        variants = variants[:limit]
    boards: Dict[str, Tuple] = {}
    originals: Dict[Tuple[str, str], Dict] = {}
    out: List[Outcome] = []
    for v in variants:
        if v.world not in boards:
            with contextlib.redirect_stdout(io.StringIO()):
                world = parser_eval.build_world(v.world)
                gs = parser_eval.build_llm_game_state(world)
                boards[v.world] = (CommandParser(use_real_llm=False), world, gs)
        parser, world, gs = boards[v.world]
        key = (v.row_id, v.world)
        if key not in originals:
            with contextlib.redirect_stdout(io.StringIO()):
                originals[key] = parser.parse(v.original, gs, world=world)
        trace_rows: List[Dict] = []
        with contextlib.redirect_stdout(io.StringIO()):
            if with_trace:
                parse_trace.open_trace(v.utterance)
            try:
                varied = parser.parse(v.utterance, gs, world=world)
            finally:
                t = parse_trace.close_trace() if with_trace else None
                if t is not None:
                    trace_rows = list(t.rows)
        verdict = judge(v, originals[key], varied)
        out.append(Outcome(v, verdict, trace_rows,
                           trace_rows[-1]["stage"] + "·" + trace_rows[-1]["rule"] if trace_rows else None))
    return out


def summarize(outcomes: List[Outcome]) -> Dict:
    fam: Dict[str, Dict[str, int]] = {}
    stage: Dict[str, int] = {}
    for o in outcomes:
        f = fam.setdefault(o.variant.family, {"cases": 0, "failed": 0})
        f["cases"] += 1
        if o.verdict:
            f["failed"] += 1
            stage[o.last_stage or "?"] = stage.get(o.last_stage or "?", 0) + 1
    return {"cases": len(outcomes), "failed": sum(1 for o in outcomes if o.verdict),
            "by_family": fam, "by_last_stage": dict(sorted(stage.items(), key=lambda kv: -kv[1]))}
