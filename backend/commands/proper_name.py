"""SF-V4 "A proper name asks" — CRT-10 "The suggestion is honest", the slice
it leads (SCORE_FINISH_SPEC.md §6.3, the gate record; COMMAND_ROBUSTNESS_
SPEC.md §12.16; rules SYSTEMS_REFERENCE.md §89).

An attack on a PROPER NAME the map does not know fought the nearest enemy:
``Ney, attack Zorglub`` / ``Alsace`` / ``Lombardy`` each answered "Your
words named no foe our maps know, Sire — Ney marches on Mack at Swabia, the
nearest in sight. Name another and he will turn." and the battle was fought
(Ney 24,000 → about 21,900). The same shape was already ASKED for a near miss
(CQ-30) and REFUSED free for pursue / move / march / recruit — the attack
road alone disclosed and proceeded, a rule (PS18-R1) written for
DESCRIPTIONS ("smash the retreating column"), which cannot be enumerated.
A proper name can be recognised by grammar, and is now asked about, free,
naming only foes in sight (the ruling of September 28, 2026).

* ``proper_name_in(tail, world, …)`` — PURE. The words after the attack
  verb up to the first comma / conjunction / preposition / clause word hold
  a proper name when (1) they do not open with a determiner, possessive or
  quantifier, (2) after filler and generic words a word remains that is no
  military noun, no -ly adverb and — when written in lower case — no
  description (a participle or superlative: "retreating", "weakest"), and
  (3) that word resolves to no commander on the roster, province, nation,
  demonym or prisoner (a province TYPO resolves: "Swabbia" still corrects).
* ``attack_proper_name_ask(world, command, raw)`` — the dispatch-seam
  answer for an attack order: the ask, the tombstone line, the bench line,
  or the "nothing in sight" refusal; None when the order names no unknown
  proper name. Every answer spends nothing.

Flip lever ``A_PROPER_NAME_ASKS``: False restores disclose-and-proceed.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional

from backend.display_names import humanize_entity_name

A_PROPER_NAME_ASKS = True

# Opening words that make the object a DESCRIPTION, not a name.
_BLOCKING_PREFIXES = frozenset({
    "the", "a", "an", "this", "that", "these", "those",
    "across", "over", "through", "along", "behind", "beyond", "near",
    "past", "around", "beside", "below", "above", "under", "onto", "upon",
    "his", "her", "their", "its", "our", "your", "my", "thy", "whose",
    "every", "any", "each", "some", "all", "both", "either", "neither",
    "no", "another", "other", "whichever", "whatever", "which", "what",
})

# The words that end the object: punctuation is cut first; these end it too.
_TAIL_STOPS = frozenset({
    "and", "or", "but", "then", "so", "nor", "yet",
    "at", "on", "in", "near", "from", "with", "without", "by", "before",
    "after", "toward", "towards", "across", "over", "through", "along",
    "behind", "beyond", "past", "around", "beside", "below", "above",
    "under", "onto", "upon", "into", "to", "for", "until", "till", "while",
    "when", "whenever", "if", "unless", "as", "because", "since", "once",
    "where", "wherever", "who", "whom", "which", "that", "lest",
})

# A closed list of military nouns (the description's head words).
_MILITARY_NOUNS = frozenset({
    "cavalry", "horse", "horsemen", "hussars", "cuirassiers", "dragoons",
    "lancers", "uhlans", "cossacks", "chasseurs", "infantry", "foot",
    "grenadiers", "guard", "guards", "fusiliers", "voltigeurs", "jaegers",
    "skirmishers", "riflemen", "militia", "landwehr", "conscripts",
    "guns", "gun", "battery", "batteries", "artillery", "cannon", "cannons",
    "column", "columns", "flank", "flanks", "left", "right", "centre",
    "center", "rear", "front", "line", "lines", "vanguard", "van",
    "rearguard", "baggage", "train", "convoy", "convoys", "wagons", "supply",
    "supplies", "camp", "bivouac", "outpost", "outposts", "picket",
    "pickets", "screen", "square", "squares", "wing", "wings", "division",
    "divisions", "brigade", "brigades", "regiment", "regiments", "battalion",
    "battalions", "squadron", "squadrons", "corps", "army", "armies",
    "troops", "men", "soldiers", "force", "forces", "host", "rabble",
    "stragglers", "garrison", "defenders", "position", "positions", "works",
    "redoubt", "redoubts", "fort", "fortress", "walls", "bridge", "ford",
    "crossing", "village", "town", "city", "heights", "hill", "ridge",
    "wood", "woods", "pass", "road", "roads", "rest", "remnant", "remnants",
    "survivors", "lot", "bunch", "pack", "devils", "dogs",
})

# Lower-case words that DESCRIBE (adjectives a player puts on a foe).
_DESCRIPTIVE_WORDS = frozenset({
    "enemy", "enemies", "foe", "foes", "hostile", "foreign", "opposing",
    "weak", "weakest", "weaker", "strong", "strongest", "stronger",
    "near", "nearest", "nearer", "close", "closest", "closer", "nearby",
    "isolated", "exposed", "beaten", "broken", "routed", "scattered",
    "disorganised", "disorganized", "battered", "wounded", "tired",
    "exhausted", "demoralised", "demoralized", "small", "smallest", "large",
    "largest", "big", "biggest", "main", "whole", "entire", "remaining",
    "other", "others", "fresh", "new", "next", "first", "last", "lead",
    "leading", "nearside", "far", "farthest", "furthest", "damned",
    "cursed", "bloody", "accursed", "wretched", "miserable", "cowardly",
    "proud", "arrogant", "foolish", "old", "young",
})

# Filler a player wraps around an object ("Sire", "please", "now").
_FILLER = frozenset({
    "sire", "please", "now", "immediately", "at", "once", "there", "here",
    "yonder", "them", "him", "her", "it", "us", "me", "everyone",
    "everything", "anything", "anyone", "someone", "somebody", "whoever",
    "whatever", "nearest", "closest", "enemy", "enemies", "marshal",
    "general", "commander", "region", "province", "hell", "quarter",
    "mercy", "sword",
})

_WORD_RE = re.compile(r"[A-Za-z][A-Za-z'’-]*")


def _strip_possessive(word: str) -> str:
    return re.sub(r"['’]s$", "", word)


def _roster_tokens(world) -> Dict[str, List[str]]:
    """lower-cased name / display / word -> the marshals it can name."""
    out: Dict[str, List[str]] = {}
    for marshal in (getattr(world, "marshals", None) or {}).values():
        shown = humanize_entity_name(marshal.name)
        forms = {marshal.name.lower(), shown.lower()}
        forms.update(w for w in re.findall(r"[a-z']+", shown.lower()) if len(w) >= 3)
        for form in forms:
            out.setdefault(form, []).append(marshal.name)
    return out


# A rank names no man on its own: "Archduke John" with John fallen must not
# resolve through "archduke" to the Archduke who still stands (NPC-3's rule).
_TITLE_WORDS = frozenset({
    "archduke", "archduchess", "duke", "grand", "prince", "king", "emperor",
    "empress", "tsar", "czar", "tsarevich", "count", "baron", "sir", "lord",
    "general", "marshal", "admiral", "field", "colonel", "captain", "elector",
})


def _resolves(world, words: List[str], viewer: Optional[str]) -> bool:
    """Does the object name ANYTHING on the board — a commander (any court),
    a province (or a province typo the region matcher corrects), a nation,
    a demonym, or a prisoner?"""
    span = " ".join(words).lower()
    tokens = _roster_tokens(world)
    regions = list((getattr(world, "regions", None) or {}).keys())
    region_lower = {r.lower() for r in regions}
    candidates = [span] + [w.lower() for w in words
                           if len(words) == 1 or w.lower() not in _TITLE_WORDS]
    for cand in candidates:
        if cand in tokens or cand in region_lower:
            return True
    try:
        from backend.ai.nation_names import resolve_typed_nation
        from backend.ai.strategic_parser import demonym_to_nation
        for cand in candidates:
            if resolve_typed_nation(cand, world):
                return True
            if demonym_to_nation(cand, world):
                return True
    except Exception:
        pass
    try:
        from backend.commands import prisoners as _prisoners
        for cand in candidates:
            if _prisoners.prisoner_of(world, cand, viewer) is not None:
                return True
    except Exception:
        pass
    # A province TYPO resolves — "Swabbia" is still corrected (CX3-X3).
    try:
        from backend.commands.parser import _plausible_name_typo
        for word in words:
            if len(word) >= 4 and any(_plausible_name_typo(word.lower(), r.lower())
                                      for r in regions):
                return True
    except Exception:
        pass
    return False


def object_words(tail: str) -> List[str]:
    """The words of the object: from the start of ``tail`` to the first
    punctuation mark or stop word, possessives stripped."""
    tail = re.split(r"[,;:.!?()\"—–]", tail or "", maxsplit=1)[0]
    words: List[str] = []
    for word in _WORD_RE.findall(tail):
        if word.lower() in _TAIL_STOPS:
            break
        words.append(_strip_possessive(word))
    return [w for w in words if w]


def proper_name_in(tail: str, world, viewer: Optional[str] = None) -> Optional[str]:
    """The unknown PROPER NAME the object ``tail`` holds, or None (a
    description, a known name, nothing). PURE."""
    if not A_PROPER_NAME_ASKS or world is None:
        return None
    words = object_words(tail)
    if not words:
        return None
    if words[0].lower() in _BLOCKING_PREFIXES:
        return None
    named = []
    for word in words:
        low = word.lower()
        if low in _FILLER or low in _MILITARY_NOUNS:
            continue
        if low.endswith("ly") and len(low) > 3:
            continue
        if not word[:1].isupper() and (
                low in _DESCRIPTIVE_WORDS or low.endswith(("ing", "est"))):
            continue
        named.append(word)
    if not named:
        return None
    if _resolves(world, named, viewer) or _resolves(world, words, viewer):
        return None
    return " ".join(named)


def attack_tail(raw: str) -> Optional[str]:
    """The text after the FIRST battle or capture verb of ``raw`` — the
    object position of an attack order — or None."""
    from backend.ai.attack_vocabulary import BATTLE_VERB_RE, CAPTURE_VERB_RE
    hits = [m for m in (BATTLE_VERB_RE.search(raw or ""),
                        CAPTURE_VERB_RE.search(raw or "")) if m]
    if not hits:
        return None
    first = min(hits, key=lambda m: m.start())
    return (raw or "")[first.end():]


# ── the answer ──────────────────────────────────────────────────────────

def _visible_nearest_first(world, marshal) -> list:
    viewer = getattr(marshal, "nation", None) or getattr(world, "player_nation", None)
    visible = [e for e in world.get_visible_enemies(viewer)
               if int(getattr(e, "strength", 0) or 0) > 0]
    if marshal is not None:
        origin = [marshal.location]
    else:
        origin = [m.location for m in world.get_player_marshals()
                  if int(getattr(m, "strength", 0) or 0) > 0
                  and not getattr(m, "captured_by", "")]

    def _dist(enemy):
        return min((world.get_distance(o, enemy.location) for o in origin), default=999)
    return sorted(visible, key=_dist)


def _near_miss(world, name: str, viewer: Optional[str]):
    """The foreign commander ``name`` is one typed slip from (a transposition
    counts as one — "Makc"), or None. Matched over the whole roster; the
    caller answers fog-honestly."""
    from backend.utils.fuzzy_matcher import osa_distance_at_most
    from backend.commands.parser import _plausible_name_typo
    low = name.lower()
    words = [w for w in re.findall(r"[a-z']+", low) if len(w) >= 3]
    shared: Dict[str, int] = {}
    for m in (getattr(world, "marshals", None) or {}).values():
        for w in set(re.findall(r"[a-z']+", humanize_entity_name(m.name).lower())):
            shared[w] = shared.get(w, 0) + 1
    for m in (getattr(world, "marshals", None) or {}).values():
        if getattr(m, "nation", None) == viewer:
            continue
        shown = humanize_entity_name(m.name).lower()
        tokens = [t for t in re.findall(r"[a-z']+", shown)
                  if len(t) >= 3 and shared.get(t, 0) < 2]
        for word in words:
            for token in tokens:
                if word != token and (osa_distance_at_most(word, token, 1)
                                      or _plausible_name_typo(word, token)):
                    return m
    return None


def _fallen(world, name: str, viewer: Optional[str]):
    for f_name, tomb in (getattr(world, "fallen_marshals", None) or {}).items():
        if (tomb or {}).get("nation") == viewer:
            continue
        if name.lower() in (f_name.lower(), humanize_entity_name(f_name).lower()):
            return f_name, (tomb or {})
    return None, None


def _bench(world, name: str, viewer: Optional[str]):
    pool = getattr(world, "marshal_pool", None) or {}
    for nation, candidates in pool.items():
        if nation == viewer:
            continue
        for candidate in candidates or []:
            cand = str((candidate or {}).get("name") or "")
            if cand and name.lower() in (cand.lower(), humanize_entity_name(cand).lower()):
                return cand
    return None


def _ask(world, marshal, foes: list, raw: str, question: str,
         interpreted) -> Optional[Dict]:
    from backend.commands.clarification import build_proper_name_clarification
    response = build_proper_name_clarification(world, marshal, foes, raw, question)
    if response is None:
        return None
    response["interpreted_target"] = interpreted.name if interpreted else None
    response["proper_name_ask"] = True
    return response


def attack_proper_name_ask(world, marshal, raw: str) -> Optional[Dict]:
    """The answer to an attack whose object is a proper name the map does
    not know (``marshal`` None for the bare "attack Zorglub"), or None.
    Every answer is free: an ``awaiting_clarification`` question or a
    ``success: False`` refusal at cost 0."""
    if not A_PROPER_NAME_ASKS or not raw or world is None:
        return None
    viewer = getattr(marshal, "nation", None) or getattr(world, "player_nation", None)
    tail = attack_tail(raw)
    if tail is None:
        return None
    name = proper_name_in(tail, world, viewer)
    if name is None:
        return None
    shown_name = name[:1].upper() + name[1:]
    who = marshal.name if marshal is not None else "we"
    # an enemy BENCH name answers exactly as a fogged commissioned general
    # would, so a commission never leaks (the strategic PURSUE arm's line)
    benched = _bench(world, name, viewer)
    if benched is not None:
        chaser = marshal.name if marshal is not None else "our marshals"
        return {
            "success": False,
            "message": (f"No intelligence on {humanize_entity_name(benched)}'s "
                        f"position, Sire. Scout for him before {chaser} can "
                        f"give chase."),
            "variable_action_cost": 0,
            "proper_name_ask": True,
        }
    foes = _visible_nearest_first(world, marshal)
    nearest = foes[0] if foes else None
    lead = ""
    f_name, tomb = _fallen(world, name, viewer)
    if f_name is not None:
        from backend.commands import prisoners as _prisoners
        where = str(tomb.get("location") or "")
        if where and _prisoners.cell_in_view(world, where, viewer):
            turn = tomb.get("turn")
            when = f" on turn {int(turn)}" if isinstance(turn, (int, float)) else ""
            lead = (f"{humanize_entity_name(f_name)} fell at "
                    f"{humanize_entity_name(where)}{when}, Sire — his corps is no "
                    f"more.")
    if not foes:
        # the existing refusal, reworded to "in sight" (§6.3)
        opening = (f"{lead} No other foe is in sight —" if lead else
                   f"No foe called {shown_name} is in sight, Sire, nor any other —")
        actor = marshal.name if marshal is not None else "no marshal of ours"
        return {
            "success": False,
            "message": f"{opening} {actor} will not charge at a guess.",
            "variable_action_cost": 0,
            "proper_name_ask": True,
        }
    near = _near_miss(world, name, viewer) if not lead else None
    if near is not None and near in foes:
        question = (f"No foe called {shown_name} is in sight, Sire — did you "
                    f"mean {humanize_entity_name(near.name)} at "
                    f"{humanize_entity_name(near.location)}?")
        return _ask(world, marshal, [near] + [f for f in foes if f is not near],
                    raw, question, near)
    engage = f"shall {who} engage him?" if marshal is not None else "shall we engage him?"
    question = (f"{lead + ' ' if lead else f'No foe called {shown_name} is in sight, Sire. '}"
                f"The nearest in sight is {humanize_entity_name(nearest.name)} at "
                f"{humanize_entity_name(nearest.location)} — {engage}")
    return _ask(world, marshal, foes, raw, question, nearest)


def arrival_object_note(obj_text: str, world, marshal_name: Optional[str]) -> Optional[str]:
    """SF-V4 §6.3 item 4 — "march to Swabia then attack Zorglub": the march
    stands, NO attack is armed on arrival, and the reply names the dropped
    word. The note for that, or None when the arrival object names no
    unknown proper name."""
    if not A_PROPER_NAME_ASKS or world is None:
        return None
    viewer = None
    if marshal_name:
        m = world.get_marshal(marshal_name)
        viewer = getattr(m, "nation", None)
    name = proper_name_in(obj_text, world, viewer or getattr(world, "player_nation", None))
    if name is None:
        return None
    shown_name = name[:1].upper() + name[1:]
    return (f"No foe called {shown_name} is in sight — the march stands, and "
            f"no attack is armed on arrival; name the foe and he will strike")
