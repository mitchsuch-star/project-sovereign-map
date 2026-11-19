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
from backend.errors import report

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
    "and", "or", "but", "then", "so", "nor", "yet", "therefore", "thus", "hence",
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
    except Exception as exc:
        report(exc, "proper_name._resolves: import backend.ai.nation_names")
    try:
        from backend.commands import prisoners as _prisoners
        for cand in candidates:
            if _prisoners.prisoner_of(world, cand, viewer) is not None:
                return True
    except Exception as exc:
        report(exc, "proper_name._resolves: import backend.commands")
    # A province TYPO resolves — "Swabbia" is still corrected (CX3-X3).
    try:
        from backend.commands.parser import _plausible_name_typo
        for word in words:
            if len(word) >= 4 and any(_plausible_name_typo(word.lower(), r.lower())
                                      for r in regions):
                return True
    except Exception as exc:
        report(exc, "proper_name._resolves: import backend.commands.parser")
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


def _first_battle_verb(raw: str):
    """The FIRST battle, capture or bombard verb of ``raw`` (a regex match),
    or None. UI6-X16: the bombard verbs ("bombard", "shell", "cannonade")
    ride the attack action in the mock chain and were read by no object
    reader — "Lannes, bombard Zorglub" disclosed and proceeded against Mack,
    "Lannes, bombard Kutuzov and Mack" shelled Mack."""
    from backend.ai.attack_vocabulary import (BATTLE_VERB_RE, BOMBARD_VERB_RE,
                                              CAPTURE_VERB_RE)
    hits = [m for m in (BATTLE_VERB_RE.search(raw or ""),
                        CAPTURE_VERB_RE.search(raw or ""),
                        BOMBARD_VERB_RE.search(raw or "")) if m]
    if not hits:
        return None
    return min(hits, key=lambda m: m.start())


def attack_tail(raw: str) -> Optional[str]:
    """The text after the FIRST battle, capture or bombard verb of ``raw`` —
    the object position of an attack order — or None."""
    first = _first_battle_verb(raw)
    if first is None:
        return None
    return (raw or "")[first.end():]


def attack_verb(raw: str) -> str:
    """The order's own verb for the answers that re-issue it: "charge" or
    "bombard" when the line's first battle verb is one (UI6-X16 — the ask
    re-issues the order the player gave), else "attack"."""
    first = _first_battle_verb(raw)
    word = first.group(0).lower() if first is not None else ""
    if word.startswith("charg"):
        return "charge"
    from backend.ai.attack_vocabulary import BOMBARD_VERBS
    if any(word.startswith(v) for v in BOMBARD_VERBS):
        return "bombard"
    return "attack"


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


_EVERYTHING_RE = re.compile(
    r"^\s*(?:everything|everyone|everybody|anything|anyone|anybody|them\s+all|all\s+of\s+them|"
    r"the\s+lot|all\s+of\s+it)\s*[.!]*$", re.IGNORECASE)


def _own_marshal_at_head(tail: str, world, viewer: Optional[str]) -> Optional[str]:
    """The marshal of OURS whose name opens the attack's object position
    ("attack Davout"), or None. Only the head: "attack Mack with Lannes in
    support" names Lannes further on, and that is the second man's order."""
    text = (tail or "").strip()
    text = re.sub(r"^(?:marshal|general|gen\.|prince)\s+", "", text, flags=re.IGNORECASE)
    for m in (getattr(world, "marshals", None) or {}).values():
        if getattr(m, "nation", None) != viewer:
            continue
        for shown in {str(m.name), humanize_entity_name(m.name)}:
            if shown and re.match(r"^" + re.escape(shown) + r"(?![\w'’-])", text, re.IGNORECASE):
                return m.name
    return None


def _ask(world, marshal, foes: list, raw: str, question: str,
         interpreted, verb: str = "attack") -> Optional[Dict]:
    from backend.commands.clarification import build_proper_name_clarification
    response = build_proper_name_clarification(world, marshal, foes, raw, question,
                                               verb=verb)
    if response is None:
        return None
    response["interpreted_target"] = interpreted.name if interpreted else None
    response["proper_name_ask"] = True
    return response


def attack_proper_name_ask(world, marshal, raw: str) -> Optional[Dict]:
    """The answer to an attack whose object is a proper name the map does
    not know (``marshal`` None for the bare "attack Zorglub"), or None.
    Every answer is free: an ``awaiting_clarification`` question or a
    ``success: False`` refusal at cost 0.

    UI6-X16 (Session UI-6, November 13, 2026): a CHARGE or a BOMBARDMENT
    is read here too, and its ask re-issues the order the player gave
    ("shall Murat charge him?" → "Murat, charge Mack") — "Murat, charge
    Zorglub and Mack" charged Mack and "Lannes, bombard Zorglub" shelled him
    behind a disclosure."""
    if not A_PROPER_NAME_ASKS or not raw or world is None:
        return None
    viewer = getattr(marshal, "nation", None) or getattr(world, "player_nation", None)
    tail = attack_tail(raw)
    if tail is None:
        return None
    verb = attack_verb(raw)
    # DD0-1 (October 10, 2026): an attack whose object is one of OUR OWN
    # marshals, or "everything" / "everyone", is refused or asked — never
    # the nearest enemy behind a disclosure.
    own = _own_marshal_at_head(tail, world, viewer)
    if own is not None:
        actor = marshal.name if marshal is not None else "no marshal of ours"
        return {
            "success": False,
            "message": (f"{humanize_entity_name(own)} is a marshal of "
                        f"{humanize_entity_name(viewer or 'ours')}, Sire — "
                        f"{humanize_entity_name(actor)} will not attack our own. "
                        f"Nothing has been relayed."),
            "variable_action_cost": 0,
            "proper_name_ask": True,
        }
    if _EVERYTHING_RE.match(tail):
        foes = _visible_nearest_first(world, marshal)
        if not foes:
            return {
                "success": False,
                "message": "No foe is in sight, Sire — attack whom? Nothing has been relayed.",
                "variable_action_cost": 0,
                "proper_name_ask": True,
            }
        in_sight = ", ".join(f"{humanize_entity_name(f.name)} at {humanize_entity_name(f.location)}"
                             for f in foes[:4])
        _whom = "Attack" if verb == "attack" else verb.capitalize()
        asked = _ask(world, marshal, foes, raw,
                     f"{_whom} whom, Sire? Name the foe — in sight: {in_sight}.", None,
                     verb=verb)
        if asked is not None:
            return asked
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
    # Row PW part 2: no man in sight bears the name, nor a near miss of one —
    # but it stands one slip from a PROVINCE on the map ("Carolina" for
    # Carniola). Asked back as the province, with the order to give again;
    # nothing is spent and no foe is offered in its place.
    # (The review: only an ATTACK takes a province — a charge and a
    # bombardment name a foe, and keep their own ask.)
    if not lead and verb == "attack" and _near_miss(world, name, viewer) is None:
        province = near_province(world, name)
        if province is not None:
            again = (f"{humanize_entity_name(marshal.name)}, {verb} {province}"
                     if marshal is not None else f"{verb} {province}")
            return {
                "success": False,
                "message": (f"No foe called {shown_name} is in sight, Sire — did you mean the "
                            f"province of {province}? Say '{again}'."),
                "variable_action_cost": 0,
                "proper_name_ask": True,
                "suggestion": province,
            }
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
                    raw, question, near, verb=verb)
    _deed = "engage" if verb == "attack" else verb
    engage = f"shall {who} {_deed} him?" if marshal is not None else f"shall we {_deed} him?"
    question = (f"{lead + ' ' if lead else f'No foe called {shown_name} is in sight, Sire. '}"
                f"The nearest in sight is {humanize_entity_name(nearest.name)} at "
                f"{humanize_entity_name(nearest.location)} — {engage}")
    return _ask(world, marshal, foes, raw, question, nearest, verb=verb)


def near_province(world, name: str) -> Optional[str]:
    """Row PW part 2 (the first playtest: "attack Carniola", mistyped, asked
    for a foe called "Carolina"). The ONE province a mistyped name stands a
    slip from: within two edits (transposition-aware) of a province's name,
    or its letters in another order — both of five letters or more. None
    when no province fits, or more than one. Read only on the ask's road."""
    from backend.utils.fuzzy_matcher import osa_distance_at_most
    word = re.sub(r"[^a-z]", "", str(name or "").lower())
    if len(word) < 5:
        return None
    hits = []
    for region_name in (getattr(world, "regions", None) or {}):
        plain = re.sub(r"[^a-z]", "", str(region_name).lower())
        if len(plain) >= 5 and plain != word and (
                osa_distance_at_most(word, plain, 2) or sorted(word) == sorted(plain)):
            hits.append(str(region_name))
    return hits[0] if len(hits) == 1 else None


def nearest_own_marshal(world, name: str) -> Optional[str]:
    """GRD-16 (ruled November 17, 2026; built by row PW part 2): the ONE
    marshal of the player's OWN a mistyped address stands a slip from — one
    edit (transposition-aware) where either name has four letters or fewer,
    two otherwise; a name of four letters or fewer must also begin as his does
    (the review: "Hey" and "Key" are one letter from Ney and are not him).
    None when none fits, or more than one. Only the player's own marshals are
    read: never a foe, never a name the fog holds."""
    from backend.utils.fuzzy_matcher import osa_distance_at_most
    word = re.sub(r"[^a-z]", "", str(name or "").lower())
    if len(word) < 3:
        return None
    hits = []
    for marshal in world.get_player_marshals():
        plain = re.sub(r"[^a-z]", "", str(marshal.name).lower())
        if not plain or plain == word:
            continue
        short = min(len(word), len(plain)) <= 4
        if short and word[0] != plain[0]:
            continue
        if osa_distance_at_most(word, plain, 1 if short else 2):
            hits.append(humanize_entity_name(marshal.name))
    return hits[0] if len(hits) == 1 else None


def unseen_commander_named(obj_text: str, world, viewer: Optional[str]):
    """UI6-X9: the foreign commander an object names FIRST (`object_words`,
    a leading honorific or filler word aside; matched on his full forms —
    the key and the printed name) when he is OUT OF the player's sight (THE
    one rule, `intel_surfaces.in_sight`), or None. His name is no fog
    secret; an order resting on where he stands cannot be given."""
    player = getattr(world, "player_nation", None)
    if world is None or viewer is None or viewer != player:
        return None
    words = object_words(obj_text)
    while words and words[0].lower() in _FILLER:
        words = words[1:]
    if not words or words[0].lower() in _BLOCKING_PREFIXES:
        return None
    forms: Dict[str, object] = {}
    for m in (getattr(world, "marshals", None) or {}).values():
        if getattr(m, "nation", None) == viewer:
            continue
        for form in (m.name, humanize_entity_name(m.name)):
            forms.setdefault(str(form).lower(), m)
    for k in range(len(words), 0, -1):
        found = forms.get(" ".join(words[:k]).lower())
        if found is None:
            continue
        try:
            from backend.game_logic.intel_surfaces import in_sight
            return None if in_sight(world, viewer, found) else found
        except Exception as exc:
            report(exc, "proper_name.unseen_commander_named: intel_surfaces.in_sight")
            return found
    return None


def arrival_object_note(obj_text: str, world, marshal_name: Optional[str]) -> Optional[str]:
    """SF-V4 §6.3 item 4 — "march to Swabia then attack Zorglub": the march
    stands, NO attack is armed on arrival, and the reply names the dropped
    word. The note for that, or None when the arrival object names no
    unknown proper name.

    UI6-X9 (Session UI-6, November 13, 2026): the note's rule is "in sight",
    and it now holds for a real commander out of sight as for a name on no
    roster — "march to Swabia then attack Kutuzov" armed an attack on a man
    in fog and said nothing (`strategic_parser._extract_arrival_target`
    read the whole roster). He is named as the map prints him (his name is
    no secret); nothing of where he stands is said."""
    if not A_PROPER_NAME_ASKS or world is None:
        return None
    viewer = None
    if marshal_name:
        m = world.get_marshal(marshal_name)
        viewer = getattr(m, "nation", None)
    viewer = viewer or getattr(world, "player_nation", None)
    name = proper_name_in(obj_text, world, viewer)
    if name is None:
        unseen = unseen_commander_named(obj_text, world, viewer)
        if unseen is None:
            return None
        name = humanize_entity_name(unseen.name)
    shown_name = name[:1].upper() + name[1:]
    return (f"No foe called {shown_name} is in sight — the march stands, and "
            f"no attack is armed on arrival; name the foe and he will strike")


_NAME_JOIN_RE = re.compile(
    r"(\s*(?:,|;|&|\band\b|\bplus\b|\bthen\b|\bso\b|\btherefore\b|\bthus\b|\bhence\b"
    r"|\balong\s+with\b|\btogether\s+with\b|\bas\s+well\s+as\b|\balongside\b|\bwith\b)\s*)",
    re.IGNORECASE)
# UI6-X69: the co-subject joiners ("attack Mack along with Kutuzov") - a FOREIGN
# commander after one is a second object the order drops, and the note says so;
# a marshal of ours after one is company the muster reads for itself ("WILL
# JOIN - Davout"), never a dropped object.
_SOFT_JOINERS = frozenset({"with", "along with", "together with", "as well as", "alongside"})
_ORDER_TAIL_VERB_RE = re.compile(r"\b(?:pursue|pursuit|chase|hunt)\b", re.IGNORECASE)
# UI6-X34: the other order verbs whose OBJECT may be a list — "support Davout
# and Kutuzov", "hold Bern and Kutuzov", "march to Swabia and Kutuzov".
_LIST_ORDER_VERB_RE = re.compile(
    r"\b(?:support|assist|aid|reinforce|hold|defend|protect|guard|march|move|"
    r"advance|head|proceed|go|ride|fortify|garrison|scout|follow)\b"
    r"(?:\s+(?:to|toward|towards|into|on|upon|at|for))?", re.IGNORECASE)
# a second segment may repeat the order's own verb: "attack Mack and attack
# Kutuzov", "attack Mack therefore attack Kutuzov" (a different verb is a second
# order, which the relay carries — never a second NAME).
_HARD_JOINERS = frozenset({"and", "so", "therefore", "thus", "hence", "plus", "&", ","})


def _list_order_tail(raw: str):
    """``(verb word, object tail)`` of the order whose object may be a list,
    or None: the first battle / pursuit verb, else the first list-order verb
    after the address."""
    first = _first_battle_verb(raw)
    if first is not None:
        return first.group(0).lower(), raw[first.end():]
    match = _ORDER_TAIL_VERB_RE.search(raw)
    if match is not None:
        return match.group(0).lower(), raw[match.end():]
    from backend.ai.llm_client import ADDRESS_TOKEN_RE
    address = ADDRESS_TOKEN_RE.match(raw)
    start = address.end() if address else 0
    match = _LIST_ORDER_VERB_RE.search(raw, start)
    if match is None:
        return None
    return re.match(r"[a-z]+", match.group(0).lower()).group(0), raw[match.end():]


class _Place:
    """A province standing where a commander would, so the note names it."""

    def __init__(self, name: str):
        self.name = name


def _segment_words(segment: str) -> List[str]:
    return [_strip_possessive(w) for w in _WORD_RE.findall(segment)]


def _commander_in(words: List[str], forms: Dict[str, object]):
    """The roster marshal a segment IS the full name of — the whole span
    first (a title is part of "Archduke John"), then with leading filler and
    title words dropped ("Marshal Davout")."""
    words = list(words)
    while words:
        found = forms.get(" ".join(words).lower())
        if found is not None:
            return found
        if words[0].lower() in _FILLER or words[0].lower() in _TITLE_WORDS:
            words = words[1:]
        else:
            return None
    return None


def second_commander_named(raw: str, world, addressee: Optional[str] = None):
    """UI6-X25 / X34 (widened): the commanders an order's OBJECT names as a
    LIST — "Ney, attack Mack and Kutuzov" -> (Mack, Kutuzov), "Ney, hold
    Lorraine and Kutuzov" -> (Lorraine, Kutuzov), "Ney, attack Mack
    therefore attack Kutuzov" -> (Mack, Kutuzov) — as (first, others), the
    first a roster marshal (or, for a place order, the province), or None.
    The order falls on the first; the rest were dropped in silence (CRT-2's
    rule: say which name was read). Only a segment that IS a commander's
    full name counts ("Mack and Davout support" is a second order, not a
    second target; "then" / ";" tails ride the relay's own note); the
    addressee is never a target. For a place order the others are FOREIGN
    commanders (our own marshals beside a place are the second-name road's).
    Names only — never a place of a man's."""
    if world is None or not raw:
        return None
    read = _list_order_tail(raw)
    if read is None:
        return None
    verb, tail = read
    tail = re.split(r"[.!?()\"—–:]", tail, maxsplit=1)[0]
    # UI6-X44: a PURPOSE tail ("so Mack and Kutuzov can't pass", "lest …") is
    # a clause about them, never part of the order's list of objects; UI6-X41:
    # and "therefore attack Kutuzov" is a second order on the `then` road -
    # the relay's note says it waits, so no list note says it was dropped.
    from backend.ai.clause_guards import PURPOSE_LEAD_RE
    _purpose = PURPOSE_LEAD_RE.search(tail)
    if _purpose is not None:
        tail = tail[:_purpose.start()]
    viewer = getattr(world, "player_nation", None)
    forms: Dict[str, object] = {}
    for m in (getattr(world, "marshals", None) or {}).values():
        if m.name == addressee:
            continue
        for form in (m.name, humanize_entity_name(m.name)):
            forms.setdefault(str(form).lower(), m)
    places: Dict[str, str] = {}
    for r in (getattr(world, "regions", None) or {}):
        for form in (str(r), humanize_entity_name(str(r))):
            places.setdefault(form.lower(), str(r))
    parts = _NAME_JOIN_RE.split(tail)
    segments = parts[0::2]
    joiners = [re.sub(r"\s+", " ", j.strip().lower()) for j in parts[1::2]]
    found: List[object] = []
    for index, segment in enumerate(segments):
        words = _segment_words(segment)
        if index and words and words[0].lower() == verb:
            if joiners[index - 1] not in _HARD_JOINERS:
                continue
            words = words[1:]
        while words and words[0].lower() in _FILLER:
            words = words[1:]
        if not words:
            continue
        marshal = _commander_in(words, forms)
        if marshal is None and not found:
            place = places.get(" ".join(w for w in words if w.lower() != "the").lower())
            if place is not None:
                found.append(_Place(place))
                continue
        if marshal is None:
            if found:
                continue  # a later segment that names nobody binds nothing
            return None
        if marshal in found:
            continue
        if (found and isinstance(found[0], _Place)
                and getattr(marshal, "nation", None) == viewer):
            continue
        if (index and joiners[index - 1] in _SOFT_JOINERS
                and getattr(marshal, "nation", None) == viewer):
            continue
        found.append(marshal)
    if len(found) < 2:
        return None
    return found[0], found[1:]


def second_name_note(raw: str, world, addressee: Optional[str] = None) -> str:
    """The sentence that says which names a list order read and which it did
    not act on ("Kutuzov, named after Mack, was not acted on — one order
    falls on one commander; give him a line of his own."), or "". Names
    only: nothing of where any of them stands."""
    named = second_commander_named(raw, world, addressee)
    if named is None:
        return ""
    first, others = named
    dropped = " and ".join(humanize_entity_name(o.name) for o in others)
    verb = "were" if len(others) > 1 else "was"
    pron = "them" if len(others) > 1 else "him"
    return (f"{dropped}, named after {humanize_entity_name(first.name)}, {verb} not acted on "
            f"— one order falls on one commander; give {pron} a line of his own.")
