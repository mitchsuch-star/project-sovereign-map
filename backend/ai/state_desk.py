"""SF-CMD-1 part (ii) W1 + CRT-9 "THE STATE SPEAKS FIRST" — the desk's
second table (October 3, 2026; SCORE_FINISH_SPEC.md §3 Step 4; rules
SYSTEMS_REFERENCE.md §88).

The blind census (`docs/audits/UNREHEARSED_CENSUS_2026_10_03.md`) measured
the question desk shrugging 114 of 150 natural questions: the desk owned the
terse canonical forms ("where is Mack", "how strong is Mack", "what's my
income") and nothing else. Every class the census named has one kind here,
and every kind answers the terse form AND the natural one.

Two halves, the same shape as `question_desk.py` (which calls both):

  classify_state_question(text, marshals, enemies, regions, nations)
      parser-side and PURE — the rosters only, never the world (Golden
      Rule 6). Sited AFTER the older kinds so those keep precedence on
      every phrasing they already own, and BEFORE the shrug.

  answer_state_question(world, question) -> Optional[str]
      executor-side and FOG-HONEST — our own marshals omniscient, enemies
      through the intel store, provinces as the map paints them, diplomacy
      with no fog (the standing rule).

The classifier reads TOPIC WORDS over a normalised line plus the SUBJECTS it
can resolve (a marshal of ours, a foreign commander, a province, a court, a
man on the bench), rather than one anchored regex per sentence shape — the
completion test is a FRESH blind file, so the shapes are unknown by
construction. An unknown proper name is never substituted: it is answered
as unknown (or disclosed as a typo of one roster name, CQ-30's rule).

Flip lever: `STATE_DESK_ACTIVE = False` returns None from both halves, so
every line here falls back to the pre-slice shrug byte-for-byte.
"""
from __future__ import annotations

import re
from typing import Dict, Iterable, List, Optional, Tuple

STATE_DESK_ACTIVE = True

# The kinds this module owns; `question_desk.answer_board_question` routes
# them here and the shrug router never sees them.
STATE_KINDS = frozenset({
    # money
    "net", "levy_cost", "commission_cost", "bench", "force_limit", "upkeep",
    "bills_moved", "component",
    # odds and what-ifs
    "odds_natural", "what_if_defence", "hold_region", "what_if_march",
    "how_long",
    # marshals
    "trust", "morale", "ability", "skill", "relationship", "marshal_state",
    "anyone_state", "orders", "eta", "roster", "strongest", "closest",
    "best_for", "glory", "jealous", "expectation", "army_total", "authority",
    # naval
    "fleet", "foreign_fleet", "crossing", "landing_odds", "build_time",
    "closure",
    # diplomacy
    "stance_nation", "relation", "coalition", "peace_forecast", "vassals",
    "vassal_status", "loyalty", "tribute", "war_score", "weariness_nation",
    "agenda", "buyoff_price", "why_war", "winning_war",
    # rules
    "rule",
    # map
    "terrain", "adjacent", "province_count", "can_build_at",
    # calendar
    "calendar",
    # last turn
    "enemy_moves", "attacked_us", "court_news",
    # the ground
    "garrison", "stability", "income_region", "buildings", "enemy_at",
    "enemies_near", "nation_army",
    # counsel
    "counsel", "readiness",
    # refusals
    "unknown_name",
    # minted by the mock chain itself (W3): the Reward desk, the negated end turn
    "reward", "end_turn_asked",
    # the fresh census's classes (Oct 3, 2026)
    "afford", "foe_reach", "personality", "fallen", "landing_shores", "yards",
    "treaties", "borders_nation", "war_with_place", "holder",
    # the HOLD arm's own six (Oct 3, 2026)
    "who_is", "wars_leader", "safe_natural", "what_is_in", "goal",
})

_APOS = "['’]"


def _norm(text: str) -> str:
    text = (text or "").lower().replace("’", "'")
    text = re.sub(r"[^a-z0-9' ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _forms(name: str) -> List[str]:
    from backend.ai.llm_client import name_match_patterns
    out = {_norm(p) for p in name_match_patterns(name)}
    out.add(_norm(name))
    return sorted(f for f in out if f)


def _contains(norm: str, form: str) -> bool:
    return bool(form) and re.search(r"(?:^|\s)" + re.escape(form) + r"(?:'s)?(?:\s|$)", norm) is not None


def _find_names(norm: str, names: Iterable[str]) -> List[str]:
    """Every roster name whose printed or keyed form appears as whole words,
    in order of appearance; a longer form shadows a shorter one it contains
    ("Archduke John" never also yields a bare "John")."""
    hits: List[Tuple[int, str]] = []
    for name in names:
        for form in _forms(name):
            m = re.search(r"(?:^|\s)" + re.escape(form) + r"(?:'s)?(?:\s|$)", norm)
            if m:
                hits.append((m.start(), name))
                break
    hits.sort()
    return [n for _, n in hits]


def _demonyms(nation: str) -> List[str]:
    from backend.display_names import nation_adjective
    adj = _norm(nation_adjective(nation))
    if not adj or adj == _norm(nation):
        return []
    plural = adj + ("es" if adj.endswith(("s", "sh", "ch")) else "s")
    return [adj, plural]


def _find_nations(norm: str, nations: Iterable[str]) -> List[str]:
    hits: List[Tuple[int, str]] = []
    for nation in nations:
        for form in _forms(nation) + _demonyms(nation):
            m = re.search(r"(?:^|\s)" + re.escape(form) + r"(?:'s)?(?:\s|$)", norm)
            if m:
                hits.append((m.start(), nation))
                break
    hits.sort()
    return [n for _, n in hits]


# Words that are never a name the player is asking about.
_STOP = frozenset("""
a an the of to in at on for from with by and or but if is are was were be
been am do does did has have had can could would should will shall may
might must what which who whom whose where when why how much many long far
big strong weak ours our my we i us me you your his her their its it he she
they them this that these those there here any some all no not still yet
now today turn turns last next this per each every about against over
under near next into onto out up down off back home again so very really
please berthier sire emperor napoleon france french marshal marshals general
generals army armies corps men troops soldiers fleet ships navy war peace
gold money treasury income upkeep cost price odds chances garrison province
provinces region regions terrain coalition vassal vassals design agenda
trust morale glory ability skill orders order safe hold holds held attack
attacks attacking reach move moving march marching land landing cross
crossing channel ireland london paris vienna berlin
""".split())


# Capitalised game terms a fact shape may name that are not roster names.
_GAME_TERMS = frozenset({
    "royal navy", "navy", "fleet", "admiralty", "coalition", "congress", "guard",
    "emperor", "army", "grande armee", "continental system", "staff", "presence",
    "rally", "intendance", "channel", "treasury", "senate", "cabinet",
})

_POSSESSIVE_SHAPE_RE = re.compile(
    r"^\s*(?:what(?:'s| is| are|s)|how (?:is|high|low|good))\s+(?:the\s+)?(?P<name>[A-Z][\w'’-]*(?:\s+[A-Z][\w'’-]*)?)'s\s+"
    r"(?:morale|trust|ability|skills?|glory|men|corps|army|strength|position|location|personality|expectation|rente|estate|standing order)\b"
    r"|^\s*what does\s+(?P<name2>[A-Z][\w'’-]*(?:\s+[A-Z][\w'’-]*)?)'s\s+ability\b",
    re.IGNORECASE)

_OURS_SHAPE_RE = re.compile(
    r"^\s*(?:is|was|isn't|are)\s+(?:the\s+)?(?P<name>[A-Z][\w'’-]*(?:\s+[A-Z][\w'’-]*)?)\s+"
    r"(?:ours|theirs|mine|held|taken|safe|lost|french|austrian|british|russian|prussian|"
    r"on the (?:map|board)|a (?:province|region|marshal|general|court|nation))\b", re.IGNORECASE)


def _unknown_fact_subject(text: str, known_forms: Iterable[str]) -> Optional[str]:
    """The NAME a fact-shaped question asks about ("where is X", "how strong
    is X", "who holds X", "what is X doing", "is X ours") when no roster
    knows it — else None. Only those shapes: a capitalised game term in any
    other sentence ("the Staff", "the Royal Navy", "AP") is not a name."""
    from backend.ai.question_desk import _KINDS
    known = set(known_forms)
    phrase = ""
    stripped = (text or "").strip()
    for _kind, pattern in _KINDS:
        m = pattern.match(stripped)
        if m:
            g = m.groupdict()
            phrase = next((g.get(k) for k in ("name", "name2", "name3", "name4", "name5") if g.get(k)), "")
            break
    if not phrase:
        m = _OURS_SHAPE_RE.match(stripped)
        if m:
            phrase = m.group("name")
    if not phrase:
        m = _POSSESSIVE_SHAPE_RE.match(stripped)
        if m:
            phrase = m.group("name") or m.group("name2")
    if not phrase:
        return None
    low = _norm(re.sub(r"^(?:the|our|my|his|their)\s+", "", phrase.strip(), flags=re.I))
    if not low or low in known or low in _STOP or low in _GAME_TERMS:
        return None
    if any(low == k or low in k.split() for k in known):
        return None
    if not any(tok[0].isupper() for tok in phrase.split()):
        return None
    return phrase.strip()


def _nearest(name: str, candidates: Iterable[str]) -> Optional[str]:
    """CQ-30's disclosed typo: ONE roster name within an edit of the word
    (`osa_distance_at_most`), on a surname or a whole printed form."""
    from backend.utils.fuzzy_matcher import osa_distance_at_most
    low = _norm(name)
    if len(low) < 4:
        return None
    found = []
    for cand in candidates:
        for form in _forms(cand):
            for piece in {form, form.split()[-1]}:
                if len(piece) >= 4 and piece != low and osa_distance_at_most(low, piece, 2):
                    found.append(cand)
                    break
            else:
                continue
            break
    found = sorted(set(found))
    return found[0] if len(found) == 1 else None


# ── the classifier ────────────────────────────────────────────────────────

_RULE_WORDS = {
    "fortify": r"\bfortif(?:y|ies|ying|ied|ication)?\b|\bdig(?:ging)? in\b|\bentrench",
    "unfortify": r"\bunfortif|\bbreak camp\b|\babandon (?:the )?works\b",
    "drill": r"\bdrill(?:s|ing)?\b|\btraining\b(?! ground)",
    "square": r"\b(?:form )?squares?\b",
    "support": r"\bsupport(?:s|ing)?\b|\breinforc(?:e|ing|ement)\b",
    "hold": r"\bhold(?:s|ing)?\b(?! (?:milan|against))",
    "march": r"\bmarch(?:es|ing)?\b|\bmove(?:s|ment|ing)?\b|\bstrategic order",
    "pursue": r"\bpursu(?:e|es|it|ing)\b",
    "scout": r"\bscout(?:s|ing)?\b|\breconnaissance\b",
    "retreat": r"\bretreat(?:s|ing)?\b|\bfall(?:ing)? back\b|\bwithdraw",
    "charge": r"\bcharge(?:s)?\b|\bcavalry charge\b",
    "garrison": r"\bgarrison(?:s|ing)?\b|\bdetach(?:ment)?\b",
    "recruit": r"\brecruit(?:s|ing|ment)?\b|\blev(?:y|ies)\b|\bconscript",
    "fort": r"\bforts?\b|\bfortress(?:es)?\b",
    "depot": r"\b(?:supply )?depots?\b",
    "watchtower": r"\bwatchtowers?\b",
    "market": r"\bmarkets?\b",
    "stables": r"\bstables?\b",
    "training_ground": r"\btraining grounds?\b",
    "naval_yard": r"\b(?:naval |dock|ship)?yards?\b",
    "estate": r"\bestates?\b|\bdotations?\b|\bendow",
    "rente": r"\brentes?\b|\bpensions?\b|\bannuit",
    "presence": r"\bpresence\b|\baura\b",
    "rally": r"\brally\b",
    "intendance": r"\bintendance\b",
    "iron_resolve": r"\biron resolve\b",
    "glory": r"\bglory\b|\bladder\b|\bcrown(?:ed)?\b",
    "jealousy": r"\bjealous(?:y)?\b|\bgrievance",
    "guarantee": r"\bguarantee(?:s|ing|d)?\b",
    "sponsor": r"\bsponsor(?:s|ing|ship)?\b",
    "buy_off": r"\bbuy(?:ing)? off\b|\bbuy off\b|\bbought off\b|\bcompensat",
    "vassal": r"\bvassal(?:s|age|ize|ise)?\b|\bsatellites?\b|\bclient states?\b",
    "autonomy": r"\bautonomy\b",
    "authority": r"\bauthority\b|\bgrip\b",
    "capture": r"\bcaptur(?:e|ed|ing)\b|\btaken prisoner\b|\bprisoner\b",
    "continental_system": r"\bcontinental system\b|\bclosure\b",
    "coalition": r"\bcoalition\b|\bleague\b",
    "blockade": r"\bblockad",
    "expedition": r"\bexpedition\b|\bdescent\b",
    "ap": r"\b(?:ap|action points?|actions?|orders? of the day)\b",
    "supply": r"\bsupply\b|\battrition\b|\bforag",
    "stability": r"\bstability\b",
    "war_score": r"\bwar score\b",
    "war_exhaustion": r"\bwar (?:exhaustion|weariness)\b",
    "congress": r"\bcongress\b",
    "laws": r"\blaws?\b|\bstaff\b",
    "broken": r"\bbroken\b|\brout(?:ed)?\b|\bshattered\b",
    "diversion": r"\bdiversion\b",
    "morale": r"\bmorale\b",
    "trust_rule": r"\btrust\b",
}

_RULE_ASK_RE = re.compile(
    r"^(?:what (?:does|do|is|are|would|will)|how (?:does|do|is|are)|explain|tell me (?:about|how|what)"
    r"|describe|what happens (?:if|when)|when (?:should|do|does|can|could|would) (?:i|we|a marshal|the army)"
    r"|why (?:should|would) (?:i|we))\b")


def _looks_like_a_rule_question(norm: str) -> bool:
    if not _RULE_ASK_RE.match(norm):
        return False
    if re.search(r"\bcost|\bprice|\bhow much\b|\bafford", norm):
        return False
    if re.match(r"^when (?:should|do|does|can|could|would)\b|^why (?:should|would)\b", norm):
        return True
    # "what is the Presence?" — a rule asked by its bare name
    if re.match(r"^what(?:'s| is) (?:the |a |an )?[a-z' -]{3,30}$", norm):
        return True
    return bool(re.search(
        r"\b(?:do|does|mean|work|works|for|happen|happens|get|give|gives|cost|costs"
        r"|is it|are they|good for|effect)\b", norm))


def classify_state_question(text: str, marshals: Iterable[str] = (),
                            enemies: Iterable[str] = (),
                            regions: Iterable[str] = (),
                            nations: Iterable[str] = (),
                            bench: Iterable[str] = ()) -> Optional[Dict]:
    """The state question in `text`, or None (the caller keeps the shrug)."""
    if not STATE_DESK_ACTIVE or not text:
        return None
    # A HEDGE ("perhaps build ships", "maybe attack Mack") is a musing about
    # an ORDER, not a question about the board: CRT-3's hedge arm routes it
    # to the question road so nothing is spent, and the desk leaves it to the
    # router's answer rather than reading "ships" as a fleet question.
    from backend.ai.clause_guards import (_DELIBERATIVE_OPENER_RE, _HEDGE_LEAD_RE,
                                          _leading_run_hides_a_question)
    if _HEDGE_LEAD_RE.match(text):
        return None
    # "what about build ships" / "actually what about …" — a musing about
    # an order; CRT-3's router answers it, not the fleet desk.
    if _DELIBERATIVE_OPENER_RE.match(text.strip()) or _leading_run_hides_a_question(text.strip()):
        return None
    # "how does recruiting work?" — a question about the game's GRAMMAR keeps
    # the command reference (ruling R7, `llm_client._SYNTAX_QUESTION_RE`).
    from backend.ai.llm_client import _SYNTAX_QUESTION_RE
    if _SYNTAX_QUESTION_RE.match(text.strip()):
        return None
    norm = _norm(text)
    if not norm:
        return None
    # "could the Austrian army retreat" / "can Prussia attack us" — a modal
    # about a COURT's own action is CRT-3's court-subject question (its
    # router answers), not a fact about the board.
    if (re.match(r"^(?:can|could|will|would|should|might|may|does|do|is|are)\s+(?:the\s+)?"
                 r"(?:[a-z]+\s+){0,2}(?:army|armies|forces|troops|court|courts|king|emperor|tsar)?\s*"
                 r"(?:attack|retreat|march|move|advance|invade|declare|fight|withdraw|strike|hold|take|cross|land)\b",
                 norm) and _find_nations(norm, nations) and not _find_names(norm, marshals)
            and not re.search(r"\b(?:armistice|truce|peace|alliance|terms|treaty|pact|cease)", norm)):
        return None
    # the Emperor by his title
    if re.search(r"\bthe emperor\b|\bemperor\b|\bnapoleon\b", norm):
        sovereign = next((m for m in marshals if _norm(m) == "napoleon"), None)
        if sovereign:
            norm = re.sub(r"\bthe emperor\b|\bemperor\b", "napoleon", norm)
    marshals = list(marshals)
    enemies = list(enemies)
    regions = list(regions)
    nations = list(nations)
    bench = list(bench)
    ours = _find_names(norm, marshals)
    foes = _find_names(norm, enemies)
    places = _find_names(norm, regions)
    courts = _find_nations(norm, nations)
    benchmen = _find_names(norm, bench)
    first_marshal = ours[0] if ours else ""
    first_foe = foes[0] if foes else ""
    first_place = places[0] if places else ""
    first_court = courts[0] if courts else ""

    def q(kind: str, subject: str = "", subject_type: str = "board", **extra) -> Dict:
        out = {"kind": kind, "subject": subject, "subject_type": subject_type}
        out.update(extra)
        return out

    has = lambda pattern: re.search(pattern, norm) is not None  # noqa: E731

    # ── refusals first: an unknown proper name is never substituted ────────
    known_forms = set()
    for name in marshals + enemies + regions + nations + bench:
        known_forms.update(_forms(name))
    for nation in nations:
        known_forms.update(_demonyms(nation))
    unknown = _unknown_fact_subject(text, known_forms)
    if unknown and not (ours or foes or places or courts or benchmen):
        word = unknown
        nearest = (_nearest(word, marshals + enemies) or _nearest(word, regions)
                   or _nearest(word, nations))
        return q("unknown_name", word, "none", nearest=nearest or "",
                 asked=text)

    # ── the calendar ─────────────────────────────────────────────────────
    if has(r"\b(?:what|which) (?:turn|date|month|year|day|season)\b|\bwhat(?:'s| is) the date\b|\bwhats the date\b"
           r"|\bturn (?:is it|number|are we on)\b|\bwhat time of year\b|\bwhen (?:does|is|will) (?:winter|spring|summer|autumn|the season)\b"
           r"|\bwinter\b.*\b(?:come|coming|arrive|here)\b"):
        return q("calendar", "season" if has(r"\bwinter\b|\bspring\b|\bsummer\b|\bautumn\b|\bseason") else "")

    # ── the rules (asked of a verb or a thing) ──────────────────────────
    _whatif = has(r"^(?:what|and what) (?:happens|would happen|will happen|if) (?:if|when|i|we)")
    if _looks_like_a_rule_question(norm) and not (_whatif and (ours or foes)) and not (
            ours and has(r"\b(?:ability|skill|trust|morale|think|feel|like|dislike)\b")):
        for key, pattern in _RULE_WORDS.items():
            if re.search(pattern, norm):
                return q("rule", key, "rule", place=first_place, marshal=first_marshal)
    # "how much does scouting cost" / "what does a march cost" — the verb's
    # price in actions, not a levy.
    if has(r"\bcost|\bprice|\bhow much\b") and not has(
            r"\brecruit|\blev(?:y|ies)|\braise|\bconscript|\binfantry\b|\bcavalry\b|\bartillery\b"
            r"|\bship|\bkeel|\bfleet|\bbuild|\bcommission|\bhire|\bdepot|\bfort\b|\bmarket|\bstable|\btower|\byard|\bestate|\brente|\bpension"):
        for key in ("scout", "fortify", "drill", "march", "support", "pursue", "hold", "charge", "retreat", "square", "garrison"):
            if re.search(_RULE_WORDS[key], norm):
                return q("rule", key, "rule", ap=True)
    if has(r"^(?:what|how much) (?:ap|actions?|action points?)\b|\bhow (?:many|much) (?:ap|actions?|action points?) (?:does|do|will|would)\b"
           r"|\bcost(?:s)? (?:in )?(?:ap|actions?|action points?)\b"):
        for key in ("march", "support", "scout", "fortify", "drill", "pursue", "hold", "recruit"):
            if re.search(_RULE_WORDS[key], norm):
                return q("rule", key, "rule", ap=True)
        if has(r"\battack"):
            return q("rule", "attack", "rule", ap=True)
        return q("rule", "ap", "rule", ap=True)
    if has(r"\bcan (?:napoleon|the emperor|i) be (?:captured|taken|killed)\b|\bwhat happens if (?:napoleon|the emperor|i am) (?:is )?(?:captured|taken|caught)\b"):
        return q("rule", "capture", "rule")

    # ── the HOLD arm's own shapes ────────────────────────────────────────
    if first_foe and re.match(r"^(?:who|what) (?:is|'s|are) (?:the\s+)?(?:general\s+|marshal\s+)?(?:"
                              + "|".join(re.escape(f) for f in _forms(first_foe)) + r")\b", norm) and not has(r"\bdoing\b|\bup to\b"):
        return q("who_is", first_foe, "enemy")
    from backend.ai.question_desk import THE_DESK_ANSWERS_THE_WAR_QUESTION as _war_lever
    if _war_lever and has(r"\bwho (?:are|am) (?:we|i) (?:at war with|fighting)\b|\bwho is at war with (?:us|me)\b"):
        return q("wars_leader")
    if _war_lever and first_place and has(r"\bsafe\b|\bin danger\b|\bthreatened\b|\bgetting close\b|\bsecure\b"):
        return q("safe_natural", first_place, "region")
    if first_place and has(r"\bwhat(?:'s| is) in\b|\bwho(?:'s| is) in\b|\bwhat stands in\b|\bwhat is at\b|\bwhat(?:'s| is) (?:standing )?(?:in|at)\b"):
        return q("what_is_in", first_place, "region")
    if has(r"\bsupposed to (?:be )?(?:achiev|do|accomplish)|\bwhat (?:am i|are we) (?:trying|meant|supposed)\b|\b(?:the )?(?:goal|aim|object|purpose|point) of (?:this|the|these) (?:war|wars|campaign|game)\b|\bwhat is the (?:goal|aim|objective|point)\b|\bhow do (?:i|we) win\b|\bwin condition"):
        return q("goal", "", "board", asked=text)
    if first_marshal and has(r"\bbravest of the brave\b|\biron resolve\b|\bactually do\b|\bdo in a fight\b|\bdo in battle\b|\bgift\b"):
        return q("ability", first_marshal, "marshal")
    # ── money ────────────────────────────────────────────────────────────
    if has(r"\bforce limit\b|\blevy limit\b|\bover (?:the )?limit\b|\bhow many men can (?:we|i) (?:keep|field|support|afford|maintain)\b|\barmy too (?:big|large)\b"):
        return q("force_limit")
    if has(r"\b(?:why|what) (?:did|have|has) (?:we|the treasury|the chest|our gold) (?:lose|lost|fallen|fall|drop|dropped|gone down)\b"
           r"|\bwhere did (?:the|our) (?:gold|money) go\b|\bwhy (?:is|are) (?:our|the|my) (?:upkeep|bills?|charges|expenses|costs?) (?:so )?(?:high|large|up|rising|heavy)\b"
           r"|\bwhy (?:is|was) (?:the )?(?:treasury|chest|net) (?:down|lower|negative|falling|red)\b"):
        return q("bills_moved")
    if has(r"\bupkeep\b|\bkeep(?:ing)? the army\b|\bmaintain(?:ing)? the army\b|\bpay(?:ing)? (?:for )?the (?:army|soldiers|troops|men)\b"
           r"|\bwages\b|\b(?:cost|price) of the army\b|\barmy'?s? cost\b|\bwhat does the army cost\b|\bcost to (?:keep|field|maintain)\b"):
        return q("upkeep")
    _components = (
        ("rentes", r"\brentes?\b|\bpensions?\b"),
        ("blockade", r"\bblockade\b|\badmiralty\b"),
        ("vassal_tribute", r"\btribute\b"),
        ("dotation_skim", r"\bestates?\b|\bdotations?\b"),
        ("laws", r"\blaws?\b(?! of state do)"),
        ("infrastructure", r"\binfrastructure\b|\bbuildings? (?:cost|bill)\b|\bmaintenance\b"),
        ("overseas", r"\boverseas\b|\bcolonial\b|\bcolonies\b"),
        ("state_charges", r"\bwar effort\b|\bstate charges\b|\bcharges of empire\b|\bthe charges\b"),
        ("contributions", r"\bcontributions?\b"),
        ("requisitions", r"\brequisitions?\b"),
        ("occupation", r"\boccupation\b"),
        ("trade_income", r"\btrade\b"),
    )
    if has(r"\b(?:how much|what|cost|costing|paying|pay|earn|earning|get|bring|bringing|lose|losing|is|are)\b"):
        for key, pattern in _components:
            if key == "state_charges" and not _war_lever:
                continue
            if re.search(pattern, norm) and not ours and not has(r"\bwhat (?:does|do) .* (?:do|mean)\b"):
                if key == "vassal_tribute" and has(r"\bget\b|\bfrom\b|\bowed\b|\bpay us\b|\breceive\b|\bhow much\b"):
                    return q("tribute")
                if key == "laws" and not has(r"\bcost(?:ing)?\b|\bpay(?:ing)?\b|\bupkeep\b"):
                    break
                return q("component", key, "component")
    if has(r"\bcommission\b|\bhire\b") and has(r"\bcost|\bprice|\bhow much|\bwho can\b|\bwhich .* can\b|\bbench\b"):
        return q("commission_cost", benchmen[0] if benchmen else "", "bench")
    if benchmen and has(r"\bhow much\b|\bcost|\bprice|\bafford"):
        return q("commission_cost", benchmen[0], "bench")
    if has(r"\bwho (?:can|could|may) (?:i|we) (?:commission|hire|appoint|call up)\b|\bwho is on the bench\b|\bthe bench\b|\bwhich (?:marshals?|generals?|officers?) (?:can|could|are) (?:i|we )?(?:commission|hire|available)"):
        return q("bench")
    if has(r"\b(?:cost|price|how much|what does|what do|what would)\b") and has(
            r"\brecruit|\blev(?:y|ies)|\braise|\bconscript|\bbattalion|\bregiment|\bsquadron|\bbattery"
            r"|\binfantry\b|\bcavalry\b|\bartillery\b|\bhorse\b|\bguns\b|\bmore men\b|\bmore troops\b"):
        arm = ("cavalry" if has(r"\bcavalry\b|\bhorse\b|\bsquadron") else
               "artillery" if has(r"\bartillery\b|\bguns?\b|\bbattery") else "infantry")
        return q("levy_cost", arm, "price", place=first_place)
    if has(r"\bnet\b|\bclear per turn\b|\bclear a turn\b|\bprofit\b|\btake home\b|\bsurplus\b|\bbalance sheet\b|\bper turn\b") and has(
            r"\bgold|\bnet|\bincome|\bmoney|\bclear|\bprofit|\bsurplus|\bearn|\bmake|\bbalance"):
        return q("net")
    if has(r"\b(?:income|revenue|earnings|takings|receipts)\b") and not ours and not places and has(
            r"\bwhats?\b|\bwhat is\b|\bhow much\b|\bour\b|\bmy\b|\bthis turn\b"):
        return q("net")
    if has(r"\bafford\b") and (first_place or has(r"\bfort\b|\bdepot\b|\bmarket\b|\bstables\b|\bwatchtower\b|\btraining ground\b|\byard\b|\bship\b|\bkeel\b")):
        thing = next((k for k in ("fort", "depot", "market", "stables", "watchtower", "training_ground", "naval_yard")
                      if re.search(_RULE_WORDS[k], norm)), "")
        return q("afford", thing, "price", place=first_place)
    if first_marshal and has(r"\bestate\b|\brente\b|\bpension\b") and has(r"\bcost|\bprice|\bhow much\b|\bpay\b"):
        return q("reward", first_marshal, "marshal")

    # ── naval ────────────────────────────────────────────────────────────
    _shore = ("Munster" if has(r"\bireland\b|\birish\b") else
              "London" if has(r"\bengland\b|\bbritain\b|\bthe english coast\b|\bthe channel\b") else "")
    if not first_place and _shore and _shore in regions:
        first_place = _shore
    if has(r"\bcontinental system\b|\bclosure\b"):
        return q("closure")
    if has(r"\bblockad(?:ing|ed|e)\b") and has(r"\bus\b|\bour\b|\bwe\b|\bare we\b|\bis .* blockading\b"):
        return q("fleet")
    if has(r"\bwho (?:controls|holds|rules|commands|owns) the (?:channel|sea|seas|water|waters)\b|\bcontrol of the (?:channel|sea)\b"):
        return q("crossing", "London", "region", marshal="", channel=True)
    if has(r"\bwhere (?:can|could|might|should) (?:we|i|a corps|the army) (?:land|make a landing|put ashore|go ashore|disembark)\b|\bwhere to land\b|\blanding (?:sites|shores|places)\b|\bwhich shores?\b"):
        return q("landing_shores")
    if has(r"\bdiversion\b") and has(r"\bcost|\bprice|\bhow much\b|\bodds\b|\bchances?\b|\brisk"):
        return q("rule", "diversion", "rule")
    if has(r"\b(?:naval |dock|ship)?yards?\b") and has(r"\bany\b|\bhow many\b|\bwhere\b|\bdo we have\b|\bare there\b|\bwhich\b"):
        return q("yards")
    if has(r"\broyal navy\b|\bbritish (?:fleet|navy|ships)\b|\benemy (?:fleet|navy)\b") or (
            first_court and has(r"\bfleet\b|\bnavy\b|\bships\b|\bsail\b") and _norm(first_court) != "france"):
        return q("foreign_fleet", first_court or "Britain", "nation")
    if has(r"\bhow long\b.*\b(?:build|lay down|launch)\b.*\b(?:ship|keel|fleet)|\byard rate\b|\bhow fast can we build ships\b|\bkeels? (?:a|per) turn\b"):
        return q("build_time")
    if has(r"\bodds of (?:a )?landing\b|\blanding (?:odds|chances)\b|\bchances? of (?:a )?(?:landing|descent|expedition)\b|\bodds of (?:an? )?(?:descent|expedition)\b"
           r"|\b(?:odds|chances?) .*\b(?:land(?:ing)?|expedition|descent) (?:in|at|on)\b"):
        return q("landing_odds", first_place, "region")
    if has(r"\b(?:cross|crossing|sail|land|landing|invade|get across|ferry)\b") and (first_place or has(r"\bchannel\b")) and has(
            r"\bcan\b|\bcould\b|\bis\b|\bare\b|\bopen\b|\bshut\b|\bpossible\b|\bsafe\b"):
        return q("crossing", first_place or "London", "region", marshal=first_marshal,
                 channel=has(r"\bchannel\b"))
    if has(r"\bchannel\b") and has(r"\bopen\b|\bshut\b|\bclosed\b|\bblockaded\b|\bsafe\b"):
        return q("crossing", "London", "region", marshal=first_marshal, channel=True)
    if has(r"\b(?:fleet|ships|sail|navy|squadron|admiral|readiness)\b") and not first_court and not has(r"\bbuild\b.*\bcost|\bcost\b.*\b(?:ship|fleet)"):
        return q("fleet")

    # ── what-ifs and odds in natural phrasing ────────────────────────────
    if first_place and has(r"^(?:is|isn't|are)\s") and has(r"\bours\b|\bmine\b|\btheirs\b|\bfrench\b|\bheld by us\b|\bin our hands\b|\bstill ours\b"):
        return q("holder", first_place, "region")
    if first_place and has(r"\b(?:quickest|fastest|shortest|best|safest) (?:road|route|way|path) to\b|\broad to\b|\broute to\b|\bway to\b"):
        return q("how_long", first_place, "region", marshal=first_marshal, places=places)
    if has(r"\bhow long\b|\bhow far\b|\bhow many (?:turns|marches|days)\b|\bwhen (?:would|will|could) .* (?:reach|arrive|get to)\b"):
        if has(r"\barrive|\breach|\bget to\b|\bmarch|\bfrom\b|\bto\b|\bbetween\b|\baway\b|\bfar\b"):
            if first_marshal and has(r"\barriv|\bwhen\b") and not first_place and not has(r"\bhow long\b"):
                return q("eta", first_marshal, "marshal")
            if places or first_marshal:
                return q("how_long", first_place, "region", marshal=first_marshal,
                         places=places)
    if first_marshal and has(r"\bwhen (?:does|will|do|would) " + re.escape(_norm(first_marshal).split()[-1]) + r" (?:arrive|reach|get)\b"):
        return q("eta", first_marshal, "marshal")
    if first_foe and has(r"\b(?:can|could|will|would|might)\b.*\b(?:reach|get to|make it to|arrive at|march to)\b") and first_place and not ours:
        return q("foe_reach", first_foe, "enemy", place=first_place)
    if has(r"\b(?:attacking|taking|storming|assaulting|an attack on|an assault on)\b") and has(r"\bgood idea\b|\bwise\b|\bworth it\b|\bsensible\b|\bprudent\b|\bsound\b|\brisky\b"):
        if first_foe:
            return q("odds_natural", first_foe, "enemy", marshal=first_marshal)
        if first_place:
            return q("odds_natural", first_place, "region", marshal=first_marshal)
    from backend.ai.question_desk import THE_DESK_READS_THE_ODDS as _odds_lever
    if _odds_lever and has(r"\bodds\b|\bchances?\b|\blikely to win\b|\bwould .* win\b|\bwho (?:would|will) win\b|\bcan .* (?:beat|win against|defeat)\b|\bprospects\b"):
        if first_foe and has(r"\b(?:" + "|".join(re.escape(f) for f in _forms(first_foe)) + r") (?:attacks?|attacking|falls on|strikes|hits|comes at|moves on)\b") and ours:
            return q("what_if_defence", first_foe, "enemy", marshal=first_marshal)
        if first_foe:
            return q("odds_natural", first_foe, "enemy", marshal=first_marshal)
        if first_place and ours:
            return q("odds_natural", first_place, "region", marshal=first_marshal)
        if ours and has(r"\battack|\bfight|\bengage|\btogether\b"):
            return q("odds_natural", "", "enemy", marshal=first_marshal)
    if first_foe and ours and has(r"\b(?:" + "|".join(re.escape(f) for f in _forms(first_foe)) + r") (?:attacks?|attacked|attacking|falls on|strikes|hits|comes at|moves on|assaults?)\b"):
        return q("what_if_defence", first_foe, "enemy", marshal=first_marshal)
    if first_marshal and has(r"\b(?:hold|keep|defend|retain|hang on to)\b") and first_place and has(r"\bcan\b|\bcould\b|\bwill\b|\bwould\b|\bable\b"):
        return q("hold_region", first_place, "region", marshal=first_marshal)
    if first_marshal and first_place and has(r"\b(?:if|should|were) (?:i|we)? ?(?:march|move|send|push|advance|order)\b|\bwhat (?:would|will) happen if\b|\bwhat if\b"):
        return q("what_if_march", first_place, "region", marshal=first_marshal)

    # ── the ground ───────────────────────────────────────────────────────
    if has(r"\bgarrison\b|\bhow many men (?:guard|defend|hold|garrison|protect)\b|\bwho guards\b|\bwho holds the (?:walls|works)\b|\bdefences? (?:of|at)\b") and (first_place or first_foe):
        return q("garrison", first_place or "", "region", foe=first_foe)
    if first_place and has(r"\bstability\b|\bhow stable\b|\bunrest\b|\bcontent(?:ed)?\b|\bquiet\b|\brestive\b"):
        return q("stability", first_place, "region")
    if first_place and has(r"\b(?:earn|earns|yield|yields|pay|pays|make|makes|bring|brings|worth|income|revenue|taxes)\b"):
        return q("income_region", first_place, "region")
    if first_place and has(r"\bbuildings?\b|\bstructures?\b|\bworks\b|\bbuilt\b|\bis there an?\b|\bdoes .* have an?\b"):
        return q("buildings", first_place, "region")
    if first_place and has(r"\bcan (?:i|we) build\b|\bbuild (?:at|in)\b|\bbe built\b|\bbuildable\b"):
        return q("can_build_at", first_place, "region")
    if first_place and has(r"\bterrain\b|\bground\b|\bcountry\b|\bwhat is .* like\b|\bwhat's .* like\b|\bmountain|\bhill|\bforest|\bflat\b|\bplain|\briver\b|\bdefensive bonus\b"):
        return q("terrain", first_place, "region")
    if len(places) >= 2 and has(r"\bnext to\b|\badjacent\b|\bbeside\b|\bborder|\bneighbou?r|\btouch|\bconnected\b|\bnear\b"):
        return q("adjacent", places[0], "region", other=places[1])
    if first_place and has(r"\bwhat (?:is|lies|borders|touches) (?:next to|beside|around|adjacent to)\b|\bneighbou?rs? of\b|\bwhat borders\b|\badjacent (?:to|provinces)\b"):
        return q("adjacent", first_place, "region", other="")
    if first_foe and has(r"\bfortified\b|\bentrenched\b|\bdug in\b|\bstance\b|\bstill (?:at|in)\b|\bstill (?:sitting|standing)\b|\bmoved\b|\bmoving\b|\bdoing\b|\bup to\b|\bwhere is\b|\bat\b|\bin\b"):
        if has(r"\bwhat did\b|\blast turn\b|\byesterday\b|\bhas .* moved\b|\bdid .* (?:move|attack|advance|march)\b"):
            return q("enemy_moves", first_foe, "enemy")
        return q("enemy_at", first_foe, "enemy", place=first_place,
                 fortified=has(r"\bfortified\b|\bentrenched\b|\bdug in\b"))
    if has(r"\bhow many (?:enemy|enemies|hostile|foes?|foreign)\b|\benemy (?:marshals|corps|armies|forces) (?:are )?(?:near|around|next to|adjacent|close to)\b|\bwho is (?:near|around|next to|adjacent to|threatening)\b") and first_place:
        return q("enemies_near", first_place, "region")
    if first_court and has(r"\barmy\b|\barmies\b|\btroops\b|\bforces\b|\bcorps\b|\bmen\b|\bstrong\b|\bbig\b|\bon the continent\b|\bashore\b|\blanded\b"):
        if has(r"\bmoved\b|\blast turn\b|\bdid\b"):
            return q("enemy_moves", first_court, "nation")
        return q("nation_army", first_court, "nation")

    # ── marshals of ours ─────────────────────────────────────────────────
    if len(ours) >= 2 and has(r"\bget on\b|\bget along\b|\bthink of\b|\bthinks of\b|\bfeel about\b|\bdislike|\blike\b|\bhate|\brelation|\bfriends?\b|\brivals?\b|\bquarrel|\bfeud|\bon terms\b|\btrust\b"):
        return q("relationship", ours[0], "marshal", other=ours[1])
    if first_marshal and has(r"\bhow many men\b|\bhow strong\b|\bhow big\b|\bhow large\b|\bstrength of\b") and not foes:
        return q("marshal_state", first_marshal, "marshal", asked=text)
    if first_marshal and has(r"\btrust\b|\bloyal|\breliab|\bfaithful\b|\bobey\b|\bdepend on\b|\bcount on\b"):
        return q("trust", first_marshal, "marshal")
    if first_marshal and has(r"\bmorale\b|\bspirits?\b|\bmood\b|\bheart\b"):
        return q("morale", first_marshal, "marshal")
    if first_marshal and has(r"\bability\b|\bspecial\b|\btalent\b|\bgift\b|\btrait\b|\bwhat makes .* special\b|\bknown for\b"):
        return q("ability", first_marshal, "marshal")
    _skill = re.search(r"\b(shock|tactical|tactics|defen[cs]e|defensive|logistics|administration|admin|command)\b", norm)
    if first_marshal and _skill and has(r"\bskill\b|\brating\b|\bscore\b|\bhow good\b|\bwhat is\b|\bwhat's\b|\bhow is\b"):
        return q("skill", first_marshal, "marshal", skill=_skill.group(1))
    if first_marshal and has(r"\bskills\b|\bratings\b|\bstats\b|\bcharacter sheet\b|\bhow good is\b"):
        return q("skill", first_marshal, "marshal", skill="all")
    if (first_marshal and has(r"\bpersonality\b|\btemperament\b|\bcharacter\b|\bwhat kind of (?:man|marshal|general)\b|\bwhat sort of\b")) or has(
            r"\bwho is the (?:cautious|aggressive|literal|bold|careful|reckless|rash) one\b|\bwhich (?:of my )?marshals? (?:is|are) (?:cautious|aggressive|literal|bold|careful|reckless|rash)\b|\bwho (?:is|are) (?:cautious|aggressive|literal|reckless|careful)\b"):
        return q("personality", first_marshal, "marshal" if first_marshal else "board")
    if len(ours) >= 2 and has(r"^where"):
        return q("roster", "", "board", only=ours)
    if has(r"\bwho (?:is|are) (?:fortified|drilling|entrenched|dug in|broken|retreating|recovering|engaged|idle|free|under orders|moving|marching)\b"):
        word = re.search(r"\bwho (?:is|are) (fortified|drilling|entrenched|dug in|broken|retreating|recovering|engaged|idle|free|under orders|moving|marching)\b", norm).group(1)
        return q("anyone_state", word, "state")
    if has(r"\bowe\b.*\breward\b|\breward\b.*\bowe\b|\bowed\b"):
        return q("expectation", first_marshal, "marshal" if first_marshal else "board")
    if has(r"\bdid we lose any(?:one|body)\b|\bhave we lost any(?:one|body)\b|\bwho (?:have we|did we) los[et]\b|\bfallen marshals?\b|\bwho (?:has|have) (?:fallen|died|been captured)\b|\bany (?:marshals?|generals?) (?:lost|dead|captured|fallen)\b"):
        return q("fallen")
    if first_marshal and has(r"\bexpect(?:s|ing|ation)?\b|\breward\b|\bowed\b|\bdue\b|\bwants? (?:an? )?(?:estate|rente|pension|reward)\b"):
        return q("expectation", first_marshal, "marshal")
    if first_marshal and has(r"\bunhappy\b|\bupset\b|\bangry\b|\bsulk|\bgrievance|\bjealous|\bdiscontent|\bdisgruntled|\bcontent\b|\bhappy\b|\bpleased\b|\bresent"):
        return q("jealous", first_marshal, "marshal")
    if first_marshal and has(r"\bglory\b|\bladder\b|\bcrown"):
        return q("glory", first_marshal, "marshal")
    if first_marshal and has(r"\bwhen (?:does|will|do|would)\b.*\b(?:arrive|reach|get there|be there)\b|\beta\b|\barrival\b"):
        return q("eta", first_marshal, "marshal")
    if first_marshal and has(r"\bfortified\b|\bdrilling\b|\bentrenched\b|\bdug in\b|\bbroken\b|\bretreating\b|\brecovering\b|\bin square\b|\bengaged\b|\bbusy\b|\bidle\b|\bfree\b|\bavailable\b|\bable to (?:move|act|march|attack)\b|\bmoving\b|\bmarching\b|\bstanding order\b|\bunder orders\b"):
        return q("marshal_state", first_marshal, "marshal", asked=text)
    if has(r"\b(?:is|are) (?:anyone|anybody|any of (?:my|our) marshals|any marshal|someone)\b") and has(
            r"\bfortified\b|\bdrilling\b|\bentrenched\b|\bbroken\b|\bretreating\b|\brecovering\b|\bengaged\b|\bjealous\b|\bexpecting\b|\bunhappy\b|\bidle\b|\bfree\b|\bunder orders\b|\bmoving\b"):
        word = re.search(r"\b(fortified|drilling|entrenched|broken|retreating|recovering|engaged|jealous|expecting|unhappy|idle|free|under orders|moving)\b", norm).group(1)
        if word in ("jealous", "unhappy"):
            return q("jealous", "", "board")
        if word == "expecting":
            return q("expectation", "", "board")
        return q("anyone_state", word, "state")
    if has(r"\b(?:standing|active|current|open) orders?\b|\bwhat orders\b|\bwho has orders\b|\bwhich marshals? (?:has|have|are under) orders\b|\borders? (?:in force|outstanding|active)\b"):
        return q("orders")
    if has(r"\b(?:what|how) (?:are|is) (?:my|our|the) (?:marshals|generals|commanders|officers|army) (?:doing|up to|at|about)\b|\bstatus of (?:my|our|the) (?:marshals|generals|army)\b|\blist (?:my|our|the) (?:marshals|generals)\b|\bwhere (?:are|do) (?:my|our|the) (?:marshals|generals) (?:stand|standing)?\b|\breport on (?:my|our|the) (?:marshals|generals|army)\b|\bmy (?:marshals|generals)\b.*\bdoing\b"):
        return q("roster")
    if has(r"\b(?:strongest|biggest|largest|most men|most troops|most soldiers|largest corps|biggest corps)\b") and has(r"\bmarshal|\bgeneral|\bcorps|\bwho\b|\bwhich\b"):
        return q("strongest")
    if has(r"\b(?:closest|nearest|near(?:est)? to|who is (?:near|close))\b") and (first_foe or first_place):
        return q("closest", first_foe or first_place, "enemy" if first_foe else "region")
    if has(r"\bbest (?:general|marshal|man|commander|officer|corps|choice)\b|\bwho (?:should|would|is best to) (?:lead|command|make|storm)\b|\bhighest (?:shock|defense|defence|tactical|command|administration|logistics)\b|\bbest (?:attacker|defender|administrator)\b"):
        want = ("defense" if has(r"\bdefen[cs]|\bhold\b|\bdefender\b") else
                "administration" if has(r"\badmin") else
                "command" if has(r"\bcommand\b|\brally\b") else
                "tactical" if has(r"\btactic") else "shock")
        return q("best_for", want, "skill")
    if has(r"\bglory\b|\bladder\b|\bcrown(?:ed)?\b|\bmost celebrated\b|\bmost famous\b|\blaurels\b"):
        return q("glory", "", "board")
    if has(r"\bjealous|\bgrievance|\benvy|\bfeud|\bquarrel|\brivalr|\bdiscontent|\bdisgruntled|\bsulking|\bunhappy marshals?\b|\bmarshals? (?:is|are) unhappy\b"):
        return q("jealous", "", "board")
    if has(r"\bexpect(?:s|ing|ation)? (?:a )?reward\b|\bowed (?:a )?reward\b|\bwants? (?:a |an )?(?:estate|rente|reward)\b|\bdue (?:a |an )?(?:estate|rente|reward)\b|\bwho (?:needs|wants|expects) (?:a )?reward\b|\brewards? (?:owed|due|expected)\b|\bunmet\b"):
        return q("expectation", "", "board")
    if has(r"\btotal (?:strength|men|army|force|troops|soldiers)\b|\bin total\b|\baltogether\b|\ball told\b|\bwhole army\b|\bentire army\b|\barmy'?s? (?:total )?strength\b|\bhow (?:big|large|strong) is (?:the|our|my) (?:whole |entire |french )?army\b|\bhow many men (?:do we have|have we|are there) (?:in total|altogether|all told|under arms)?\b"):
        return q("army_total")
    if has(r"\bauthority\b|\bimperial grip\b|\bmy grip\b|\bour grip\b|\bhow is my grip\b|\bhold on the (?:army|marshals|empire)\b|\bstanding with (?:the|my) marshals\b|\bdo (?:the|my) marshals (?:respect|fear|obey) me\b"):
        return q("authority")

    # ── diplomacy ────────────────────────────────────────────────────────
    # "what are the terms of the alliance with Spain" — a treaty's TERMS are
    # the Diplomatic Ledger's; the router points there (CRT-7's pin).
    if has(r"\bterms of (?:the|our|their|its|an?|this|that)\b|\bwhat (?:are|were|is) the terms\b") and not has(r"\baccept|\bwould\b|\bwill\b"):
        return None
    if has(r"\bwho leads the coalition\b|\bcoalition'?s? leader\b|\bwho is in the coalition\b|\bcoalition members?\b|\bwho pays (?:for )?the coalition\b|\bpaymaster\b|\bwho funds\b|\bwho(?:'s| is)?\s+(?:leading|heading|bankrolling|paying for|funding)\b.*\bcoalition\b|\bwhich (?:courts|nations|powers) (?:are in|form|make up) the (?:coalition|league)\b|\bis there (?:a|any) coalition\b|\bcoalition against (?:us|me|france)\b|\bwhat coalition\b"):
        return q("coalition")
    if has(r"\bwhat treaties\b|\bour treaties\b|\btreaties (?:do we|have we|are in force)\b|\bwhich treaties\b|\blist (?:our|the) treaties\b|\bwho are we (?:bound|allied|treated) (?:to|with)\b"):
        return q("treaties")
    if first_court and has(r"\ballied (?:with|to)\b|\ballies with\b|\ban ally of\b|\bour ally\b|\bin alliance with\b"):
        return q("stance_nation", first_court, "nation")
    if first_court and has(r"\bstance\b|\bposture\b|\battitude\b|\bstanding\b|\bterms\b.*\bwith\b|\bfooting\b"):
        return q("stance_nation", first_court, "nation")
    if first_court and has(r"\b(?:border|borders|bordering|adjoin|adjoins|touch|touches)\b") and has(r"\bwhich provinces\b|\bwhat provinces\b|\bwhich of our\b|\bour provinces\b|\bwhere do we border\b|\bfrontier\b"):
        return q("borders_nation", first_court, "nation")
    if first_place and not first_court and has(r"\bat war with\b|\bfighting\b|\benemies with\b"):
        return q("war_with_place", first_place, "region")
    if has(r"\bthreat level\b|\bcoalition'?s? threat\b|\bhow (?:alarmed|worried|afraid|hostile) (?:is|are)\b|\balarm\b|\bbrewing\b|\bhow close (?:is|are) (?:a|the|another) coalition\b"):
        return q("alarm_natural")
    if first_court and has(r"\bbuy(?:ing)? off\b|\bbuy off\b|\bbuy out\b|\bpay off\b|\bcompensat|\bprice of .* design\b|\bcost to (?:buy|satisfy)\b"):
        return q("buyoff_price", first_court, "nation")
    if has(r"\bwar score\b|\bscore (?:against|with|versus|vs)\b|\bhow goes the war with\b|\bare we (?:beating|winning against|losing to)\b|\bhow (?:are we|am i) doing against\b") and first_court:
        return q("war_score", first_court, "nation")
    if first_court and _war_lever and has(r"\bwar (?:weariness|exhaustion)\b|\bweary\b|\bexhausted\b|\btired of (?:the )?war\b|\bhow (?:tired|weary|exhausted) is\b|\bwill .* keep fighting\b|\bstomach for (?:the )?war\b"):
        return q("weariness_nation", first_court, "nation")
    if first_court and has(r"\bagenda\b|\bdesign\b|\baim\b|\bambition\b|\bgoal\b|\bwant(?:s)? with\b|\bafter\b.*\b(?:province|land|territory)\b|\bcovet"):
        return q("agenda", first_court, "nation", place=first_place)
    if first_court and _war_lever and has(r"\bwhy (?:are|am) (?:we|i|france) (?:at war|fighting)\b|\bwhy (?:is|are) .* (?:fighting|at war with) (?:us|me|france)\b|\bwhat is the war .* (?:about|for)\b|\bwhat'?s the war .* (?:about|for)\b|\bwhy did .* declare\b|\bcause of the war\b|\bpurpose of the war\b"):
        return q("why_war", first_court, "nation")
    if _war_lever and has(r"\bwho (?:is|'s) winning\b|\bwho'?s winning\b|\bare we winning\b|\bam i winning\b|\bwho is losing\b|\bwho has the upper hand\b|\bhow goes the war\b"):
        return q("winning_war", first_court, "nation" if first_court else "board")
    if first_court and has(r"\baccept\b|\bagree to\b|\bsign\b|\bmake peace\b|\bterms\b|\bsue\b|\bcome to (?:terms|the table)\b|\bsettle\b|\bnegotiate\b|\btalk peace\b|\bopen to peace\b|\bready for peace\b") and has(
            r"\bwould\b|\bwill\b|\bcould\b|\bcan\b|\bis\b|\bare\b|\bwhat\b|\bready\b|\bopen\b|\blikely\b") and not has(
            r"\bterms of (?:the|our|their|its)\b|\bwhat (?:are|were|is) the terms\b"):
        want = ("armistice" if has(r"\barmistice\b|\btruce\b|\bcease") else
                "alliance" if has(r"\balliance\b|\bally\b") else "peace")
        return q("peace_forecast", first_court, "nation", want=want)
    if first_court and has(r"\b(?:take|accept|agree to|sign|consider|entertain)\b") and has(r"\barmistice\b|\btruce\b|\bcease-?fire\b|\bpeace\b|\balliance\b") and has(r"\bwould\b|\bwill\b|\bcould\b|\bcan\b|\bmight\b"):
        want = ("armistice" if has(r"\barmistice\b|\btruce\b|\bcease") else
                "alliance" if has(r"\balliance\b") else "peace")
        return q("peace_forecast", first_court, "nation", want=want)
    if has(r"\bwho are (?:our|my|france'?s) (?:vassals|satellites|clients|client states|puppets|dependents)\b|\bour (?:vassals|satellites|client states)\b|\bwhich (?:nations|courts|states) (?:are|do we hold as) (?:our )?(?:vassals|satellites|clients)\b|\bdo (?:we|i) have (?:any )?vassals\b|\blist (?:our|my|the) vassals\b|\bvassals do (?:we|i) have\b"):
        return q("vassals")
    if first_court and has(r"\bvassal\b|\bsatellite\b|\bclient\b|\bpuppet\b|\bsubject (?:to|of)\b|\bdependent\b"):
        return q("vassal_status", first_court, "nation", other=courts[1] if len(courts) > 1 else "")
    if first_court and has(r"\bloyal|\bloyalty\b|\bfaithful\b|\breliable\b|\brebel|\brestive\b|\bcontent\b"):
        return q("loyalty", first_court, "nation")
    if has(r"\btribute\b"):
        return q("tribute", first_court, "nation" if first_court else "board")
    if first_court and has(r"\brelations?(?:hip)?\b|\bstanding with\b|\bhow (?:does|do) .* (?:feel|regard|see|view|think) (?:about |of )?(?:us|me|france)\b|\bterms with\b|\bopinion of (?:us|me|france)\b|\bfriendly with\b"):
        return q("relation", first_court, "nation")
    if first_court and has(r"\bagainst us\b|\bagainst me\b|\bhostile\b|\bfriendly\b|\bon our side\b|\bwith us\b|\bour (?:enemy|friend|ally)\b|\ban enemy\b|\ba friend\b|\ba threat\b|\bthreaten|\blikely to (?:join|attack|declare|fight|march|move)\b|\bgoing to (?:attack|join|declare|fight|march)\b|\bwill .* (?:attack|join|declare|fight|march)\b|\bwhere (?:does|do) .* stand\b|\bside\b|\bneutral\b|\bat peace\b|\btrust\b|\bdanger"):
        return q("stance_nation", first_court, "nation")
    if has(r"\bany (?:news|word|letters?|dispatches?|envoys?) from (?:the )?(?:courts?|abroad|europe|the powers|talleyrand)\b|\bwhat (?:did|have) the courts? (?:say|said|send|sent|write|written)\b|\bdiplomatic news\b|\bany (?:envoys?|letters?|proposals?|offers?) (?:waiting|today|this turn|arrived)\b|\bwho has written\b|\bwhat is in the (?:mailbox|letter book|post)\b"):
        return q("court_news")
    if (first_place or first_court) and has(r"\bany (?:news|word|report|reports|dispatches?) (?:from|of|out of|about)\b"):
        return q("enemy_moves", first_place or first_court, "region" if first_place else "nation")
    if has(r"\bhas anything changed\b|\bwhat has changed\b|\banything changed\b|\bwhat changed\b|\bsince yesterday\b|\bsince last turn\b"):
        return q("court_news", "", "board", plain=True)

    # ── last turn ────────────────────────────────────────────────────────
    if has(r"\bdid (?:anyone|anybody|the enemy|they|someone) attack\b|\bwere we attacked\b|\bwho attacked (?:us|me)\b|\bany (?:battles?|fighting|attacks?) (?:last turn|yesterday|overnight)\b|\bwas there (?:a )?(?:battle|fighting)\b|\bany battles\b"):
        return q("attacked_us")
    if has(r"\bwhat did .* do\b|\bhas .* moved\b|\bdid .* (?:move|advance|march|attack)\b|\bwhere did .* go\b|\bwhat (?:has|have) .* (?:been )?(?:doing|done)\b") and (first_foe or first_court):
        return q("enemy_moves", first_foe or first_court, "enemy" if first_foe else "nation")

    # ── the map's counts ─────────────────────────────────────────────────
    if has(r"\bhow many (?:provinces|regions|territories|lands?)\b|\bhow (?:big|large|much land)\b.*\b(?:hold|own|control|have|empire|realm)\b|\bprovince count\b|\bsize of (?:our|the) (?:empire|realm|holdings)\b"):
        return q("province_count", first_court, "nation" if first_court else "board")

    # ── counsel ──────────────────────────────────────────────────────────
    if has(r"\bready (?:to fight|for war|for battle|for a fight|to march|to campaign)\b|\bis the army ready\b|\bare we ready\b|\bfit to fight\b|\bbattle ready\b|\bin fighting (?:shape|trim|order)\b|\bhow (?:is|are) (?:the|our|my) (?:army|men|troops) (?:holding up|faring|bearing up)\b|\bstate of the army\b"):
        return q("readiness")
    if has(r"\bwho should (?:i|we) (?:attack|strike|hit|fight|engage|go for|move on|target)\b|\bwhat should (?:i|we) (?:attack|do first|do next|do now)\b|\bwhat do you (?:advise|recommend|suggest|counsel|think)\b|\bwhat would you do\b|\byour (?:advice|counsel|recommendation)\b|\bbest move\b|\bwhat'?s? (?:the|our) plan\b|\bfirst move\b|\bwhere (?:should|do) (?:i|we) (?:strike|attack|begin|start)\b|\badvise me\b|\bwhat (?:is|are) (?:my|our) best (?:option|options|course)\b|\bwhich enemy\b"):
        return q("counsel")

    return None


# ── the executor-side half ────────────────────────────────────────────────

def _display(name: str) -> str:
    from backend.display_names import humanize_entity_name
    return humanize_entity_name(name)


def _court(world, nation: str) -> str:
    from backend.display_names import display_nation
    try:
        return display_nation(nation)
    except Exception:
        return _display(nation)


def _money(value) -> str:
    try:
        return f"{int(value):,}"
    except Exception:
        return str(value)


def _join(names: List[str]) -> str:
    names = [n for n in names if n]
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + " and " + names[-1]


def _plural(n: int, word: str) -> str:
    from backend.display_names import plural
    return plural(int(n), word)


def _own(world, name: str):
    m = world.get_marshal(name)
    if m is None or m.nation != world.player_nation:
        return None
    return m


def _standing(world):
    return [m for m in world.get_player_marshals()
            if int(getattr(m, "strength", 0) or 0) > 0
            and not getattr(m, "captured_by", "")
            and not getattr(m, "administrative", False)]


def _state_clause(world, m) -> str:
    from backend.ai.question_desk import _order_clause, _state_words
    words = _state_words(m)
    if getattr(m, "drilling", False) or getattr(m, "drilling_locked", False):
        words.append("drilling")
    order = _order_clause(m)
    bits = ", ".join(words)
    out = f"{_display(m.name)} — {_money(m.strength)} men at {m.location}, morale {int(m.morale)}"
    if bits:
        out += f", {bits}"
    if order:
        out += f"; {order.strip()}"
    return out


def _visible_foe(world, name: str):
    """(marshal, shown) for a foreign commander the player has word of, or
    (None, sentence) — the desk's own fog rule."""
    from backend.models.intel import PARTIAL
    enemy = world.get_marshal(name)
    shown = _display(name)
    if enemy is None or enemy.nation == world.player_nation:
        return None, f"I know no foreign corps under {shown}, Sire."
    if getattr(enemy, "captured_by", ""):
        return None, f"{shown} is a prisoner, Sire — he leads no army."
    if int(getattr(enemy, "strength", 0) or 0) <= 0:
        return None, f"{shown} leads no army we know of, Sire."
    if not world.get_region_intel(enemy.location).visibility_at_least(PARTIAL):
        from backend.ai.question_desk import _last_report_of
        last = _last_report_of(world, name)
        if last:
            return None, (f"Our last word of {shown} placed him at {last[0]}, "
                          f"{_plural(last[1], 'turn')} ago — nothing since. Scout for him.")
        return None, f"We have no word of {shown}'s whereabouts, Sire. Scout for him."
    return enemy, shown


def _economy(world):
    from backend.game_logic.ledger import _build_economy
    return _build_economy(world, world.player_nation) or {}


# money ────────────────────────────────────────────────────────────────────

def _answer_net(world) -> Optional[str]:
    from backend.ai.question_desk import _answer_treasury
    return _answer_treasury(world, world.player_nation)


def _answer_levy_cost(world, arm: str, place: str) -> Optional[str]:
    from backend.commands.economy_executor import recruit_quote
    player = world.player_nation
    if place:
        quote = recruit_quote(world, place, arm=arm, nation=player) or {}
        if quote.get("ok"):
            return (f"{_money(quote.get('price'))} gold for {_money(quote.get('amount'))} "
                    f"{quote.get('arm') or arm} at {place}, Sire, raised by "
                    f"{_display(str(quote.get('recipient') or ''))}"
                    + (f" — {quote.get('terms')}" if quote.get("terms") else "") + ".")
        reason = str(quote.get("reason") or quote.get("short") or "")
        return (f"No {arm} levy is quoted at {place}, Sire"
                + (f": {reason}" if reason else "") + ".")
    from backend.ai.question_desk import _answer_price
    return _answer_price(world, player, arm)


def _answer_commission(world, who: str) -> str:
    from backend.game_logic.recruitment import build_recruitment_payload
    payload = build_recruitment_payload(world) or {}
    rows = payload.get("candidates") or []
    if who:
        row = next((r for r in rows if _norm(str(r.get("name"))) == _norm(who)), None)
        if row is None:
            return f"{_display(who)} is not on the bench, Sire."
        line = (f"Commissioning {_display(who)} costs {_money(row.get('cost'))} gold and one "
                f"administrative action, Sire, and brings a corps of {_money(row.get('corps') or payload.get('corps_size'))} "
                f"from the infantry pool.")
        if not row.get("available") and row.get("blocked_reason"):
            line += f" Today: {row.get('blocked_reason')}"
        return line
    if not rows:
        return "The bench is empty, Sire — no marshal waits to be commissioned."
    parts = []
    for r in rows:
        tag = "" if r.get("available") else f" ({r.get('blocked_reason') or 'not today'})"
        parts.append(f"{_display(str(r.get('name')))} {_money(r.get('cost'))}g{tag}")
    return (f"The bench, Sire — each at his price, one administrative action apiece, "
            f"the treasury holding {_money(payload.get('treasury'))}: " + "; ".join(parts) + ".")


def _answer_force_limit(world) -> str:
    # through the ledger's levy block (the IQ-2 census forbids an `ai/`
    # module reading the levy pricer directly)
    status = (_economy(world) or {}).get("levy") or {}
    limit = status.get("force_limit")
    strength = int(status.get("army_strength") or 0)
    if not limit:
        return f"No force limit binds us on this map, Sire — the army stands at {_money(strength)}."
    over = int(status.get("over_by") or 0)
    head = int(status.get("headroom") or 0)
    upkeep = world.calculate_turn_upkeep(world.player_nation) or {}
    surcharge = int(upkeep.get("surcharge") or 0)
    if over > 0:
        return (f"The force limit is {_money(limit)} men and we field {_money(strength)} — "
                f"{_money(over)} over it, Sire. The over-limit surcharge is {_money(surcharge)} "
                f"gold a turn, and the levy is priced at war rates above the limit.")
    return (f"The force limit is {_money(limit)} men and we field {_money(strength)}, "
            f"Sire — {_money(head)} of headroom before the surcharge bites.")


def _answer_upkeep(world) -> str:
    upkeep = world.calculate_turn_upkeep(world.player_nation) or {}
    econ = _economy(world)
    total = int(upkeep.get("total") or 0)
    base = int(upkeep.get("base") or 0)
    surcharge = int(upkeep.get("surcharge") or 0)
    grande = int(upkeep.get("grande_armee") or 0)
    line = (f"The army costs {_money(total)} gold a turn to keep, Sire — {_money(base)} in "
            f"pay for {_money(upkeep.get('total_strength'))} men")
    if surcharge:
        line += f", {_money(surcharge)} over-limit surcharge"
    if grande:
        line += f", {_money(grande)} for the Grande Armée's size"
    line += "."
    note = str(econ.get("upkeep_note") or "")
    if note:
        line += " Upkeep is " + note + "."
    rows = sorted((upkeep.get("breakdown") or []), key=lambda r: -int(r.get("upkeep") or 0))[:3]
    if rows:
        line += " The dearest corps: " + ", ".join(
            f"{_display(str(r.get('marshal')))} {_money(r.get('upkeep'))}g" for r in rows) + "."
    return line


def _answer_bills_moved(world) -> str:
    econ = _economy(world)
    from backend.game_logic.ledger import why_the_bills_moved
    upkeep = world.calculate_turn_upkeep(world.player_nation) or {}
    notes = why_the_bills_moved(world, world.player_nation, upkeep,
                                econ.get("state_charges"), econ.get("state_charges_terms")) or {}
    parts = [n for n in (notes.get("upkeep_note"), notes.get("charges_note"),
                         econ.get("state_charges_rate_note"), econ.get("state_charges_delta_note")) if n]
    from backend.game_logic.ledger import NET_GOLD_COMPONENTS
    outs = []
    for key, sign in NET_GOLD_COMPONENTS.items():
        if sign < 0 and int(econ.get(key) or 0):
            outs.append((int(econ.get(key) or 0), key))
    outs.sort(reverse=True)
    labels = {"upkeep_base": "upkeep", "upkeep_surcharge": "the over-limit surcharge",
              "state_charges": "the charges of empire", "dotation_skim": "the estates",
              "rente_cost": "the rentes", "laws": "the laws", "infrastructure": "infrastructure",
              "blockade": "the blockade", "admiralty": "the Admiralty", "occupation": "occupation",
              "contributions": "contributions of war"}
    bill = ", ".join(f"{labels.get(k, k.replace('_', ' '))} {_money(v)}g" for v, k in outs[:4])
    head = (f"Net this turn reads {int(econ.get('net') or 0):+,} gold, Sire. The largest bills: "
            f"{bill}." if bill else f"Net this turn reads {int(econ.get('net') or 0):+,} gold, Sire.")
    tail = []
    for n in parts:
        n = str(n).strip()
        if n.startswith("paid for"):
            n = "Upkeep is " + n
        elif n.startswith("rate points"):
            n = "The charges are " + n
        tail.append(n.rstrip(".") + ".")
    return head + ((" " + " ".join(tail)) if tail else "")


_COMPONENT_LABEL = {
    "rentes": ("the rentes", "rente_cost", -1),
    "blockade": ("the blockade", "blockade", -1),
    "dotation_skim": ("the estates", "dotation_skim", -1),
    "laws": ("the laws of state", "laws", -1),
    "infrastructure": ("infrastructure", "infrastructure", -1),
    "overseas": ("overseas trade", "overseas", 1),
    "state_charges": ("the charges of empire", "state_charges", -1),
    "contributions": ("contributions of war", "contributions", -1),
    "requisitions": ("requisitions of war", "requisitions", 1),
    "occupation": ("occupation", "occupation", -1),
    "trade_income": ("trade", "trade_income", 1),
}


def _answer_component(world, key: str) -> str:
    econ = _economy(world)
    label, field, sign = _COMPONENT_LABEL.get(key, (key.replace("_", " "), key, -1))
    value = int(econ.get(field) or 0)
    if key == "blockade":
        adm = int(econ.get("admiralty") or 0)
        note = str(econ.get("blockade_note") or "")
        if not value and not adm:
            return "No blockade costs us anything today, Sire, and the Admiralty bills nothing."
        return (f"The blockade costs us {_money(value)} gold a turn in trade, Sire, and the "
                f"Admiralty {_money(adm)} more." + (f" {note}" if note else ""))
    if key == "state_charges":
        terms = econ.get("state_charges_terms") or []
        if not value:
            return "The charges of empire bill nothing this turn, Sire."
        detail = ", ".join(f"{t.get('label')} {_money(t.get('amount'))}" for t in terms if t.get("amount"))
        return (f"The charges of empire come to {_money(value)} gold this turn, Sire"
                + (f" — {detail}" if detail else "") + ". "
                + str(econ.get("state_charges_rate_note") or ""))
    if key == "laws":
        from backend.game_logic.reforms import law_upkeep_bill
        bill = int(law_upkeep_bill(world, world.player_nation) or 0)
        if not bill:
            return "No law of state draws upkeep today, Sire — none is in force."
        return f"The laws of state cost {_money(bill)} gold a turn, Sire."
    if key == "rentes":
        from backend.game_logic.dotation import get_nation_rente_bill
        bill = int(get_nation_rente_bill(world, world.player_nation) or 0)
        holders = [m for m in world.get_player_marshals() if int(getattr(m, "pension", 0) or 0) > 0]
        if not bill:
            return "No rente is paid today, Sire — no marshal holds one."
        return (f"The rentes cost the treasury {_money(bill)} gold a turn, Sire: "
                + _join([f"{_display(m.name)} {_money(m.pension)}g" for m in holders]) + ".")
    if not value:
        return f"Nothing moves on {label} this turn, Sire."
    verb = "brings in" if sign > 0 else "costs"
    return f"{label[0].upper() + label[1:]} {verb} {_money(value)} gold a turn, Sire."


def _answer_tribute(world) -> str:
    from backend.game_logic.vassal import vassal_tribute_owed
    player = world.player_nation
    rows = [(name, int(vassal_tribute_owed(world, name) or 0))
            for name, row in (getattr(world, "vassals", None) or {}).items()
            if row.get("lord") == player]
    if not rows:
        return "France holds no vassal that pays tribute, Sire."
    total = sum(v for _, v in rows)
    return (f"Tribute brings {_money(total)} gold a turn, Sire: "
            + _join([f"{_court(world, n)} {_money(v)}g" for n, v in rows]) + ".")


# odds and what-ifs ───────────────────────────────────────────────────────

def _answer_odds_natural(world, question: Dict) -> Optional[str]:
    from backend.ai.question_desk import _answer_what_if, _answer_what_if_region
    marshal = str(question.get("marshal") or "")
    subject = str(question.get("subject") or "")
    if question.get("subject_type") == "region":
        return _answer_what_if_region(world, world.player_nation, subject, marshal, False)
    if not subject:
        # no foe named: the nearest enemy in sight to the corps named (or to any of ours)
        player = world.player_nation
        me = _own(world, marshal) if marshal else None
        cands = [e for e in world.get_visible_enemies(player)
                 if world.is_at_war(player, e.nation) and int(getattr(e, "strength", 0) or 0) > 0]
        if not cands:
            return "No enemy corps stands in our sight to weigh the odds against, Sire."
        anchor = me.location if me is not None else None
        if anchor:
            cands.sort(key=lambda e: world.get_distance(e.location, anchor))
        else:
            cands.sort(key=lambda e: min(world.get_distance(e.location, m.location) for m in _standing(world)) if _standing(world) else 0)
        subject = cands[0].name
    return _answer_what_if(world, world.player_nation, subject, marshal, False)


def _defence_lines(world, defenders, attacker, where: str) -> str:
    from backend.commands.objection_v2 import inferred_attack_odds_reading, odds_band_note
    lead = defenders[0]
    held = sum(int(m.strength) for m in defenders)
    region = world.get_region(where)
    words = []
    for m in defenders:
        from backend.ai.question_desk import _state_words
        st = _state_words(m)
        words.append(f"{_display(m.name)} {_money(m.strength)}" + (f" ({', '.join(st)})" if st else ""))
    line = f"At {where} we hold {_money(held)} men: " + _join(words) + "."
    if region is not None:
        bonus = float(getattr(region, "defense_bonus", 0.0) or 0.0)
        if bonus:
            line += f" The ground gives the defender +{int(round(bonus * 100))}% ({region.terrain})."
    if attacker is not None:
        try:
            band, weighed = inferred_attack_odds_reading(
                attacker, lead, {"world": world}, committed_defender=float(held - int(lead.strength)),
                fold_modifiers=True)
            # read from OUR side: his favorable is our unfavorable
            ours = {"favorable": "against us", "even": "even", "unfavorable": "in our favour"}.get(band, band)
            note = odds_band_note(band, weighed)
            line += f" Were {_display(attacker.name)} to attack, the odds read {ours}"
            line += (f" — {note}." if note else ".")
        except Exception:
            pass
    return line


def _answer_what_if_defence(world, foe_name: str, marshal_name: str) -> str:
    enemy, shown = _visible_foe(world, foe_name)
    if enemy is None:
        return shown + " There is no attack to weigh."
    target = _own(world, marshal_name) if marshal_name else None
    if marshal_name and target is None:
        return f"{_display(marshal_name)} leads no corps of ours, Sire."
    if target is None:
        # the nearest of ours to him
        cands = sorted(_standing(world), key=lambda m: world.get_distance(m.location, enemy.location))
        if not cands:
            return f"No corps of ours stands near {shown}, Sire."
        target = cands[0]
    where = target.location
    dist = world.get_distance(enemy.location, where)
    defenders = [m for m in _standing(world) if m.location == where]
    defenders.sort(key=lambda m: (m.name != target.name, -int(m.strength)))
    head = (f"{shown} stands at {enemy.location}, {_plural(dist, 'march')} from "
            f"{_display(target.name)} at {where}, Sire. " if dist else
            f"{shown} stands on the same ground as {_display(target.name)} at {where}, Sire. ")
    return head + _defence_lines(world, defenders, enemy, where)


def _answer_hold_region(world, place: str, marshal_name: str) -> str:
    me = _own(world, marshal_name)
    if me is None:
        return f"{_display(marshal_name)} leads no corps of ours, Sire."
    if me.location != place:
        return (f"{_display(me.name)} does not stand at {place}, Sire — he is at {me.location}, "
                f"{_plural(world.get_distance(me.location, place), 'march')} away.")
    defenders = [m for m in _standing(world) if m.location == place]
    defenders.sort(key=lambda m: (m.name != me.name, -int(m.strength)))
    foes = [e for e in world.get_visible_enemies(world.player_nation)
            if world.is_at_war(world.player_nation, e.nation)
            and world.get_distance(e.location, place) <= 1
            and int(getattr(e, "strength", 0) or 0) > 0]
    if not foes:
        return (_defence_lines(world, defenders, None, place)
                + " No enemy corps in our sight stands within a march of it.")
    foes.sort(key=lambda e: -int(e.strength))
    lines = [_defence_lines(world, defenders, foes[0], place)]
    names = _join([f"{_display(e.name)} at {e.location}" for e in foes])
    lines.append(f"Within a march: {names}.")
    return " ".join(lines)


def _answer_what_if_march(world, place: str, marshal_name: str) -> str:
    from backend.ai.question_desk import _answer_reach, _answer_what_if, _answer_what_if_region
    player = world.player_nation
    me = _own(world, marshal_name)
    if me is None:
        return f"{_display(marshal_name)} leads no corps of ours, Sire."
    foes = [e for e in world.get_visible_enemies(player)
            if e.location == place and world.is_at_war(player, e.nation)
            and int(getattr(e, "strength", 0) or 0) > 0]
    if foes:
        foes.sort(key=lambda e: -int(e.strength))
        head = (f"{place} is held by {_display(foes[0].name)}, Sire — a march there is an attack. ")
        return head + (_answer_what_if(world, player, foes[0].name, marshal_name, False) or "")
    region = world.get_region(place)
    holder = str(getattr(region, "controller", "") or "") if region is not None else ""
    if holder and holder != player and world.is_at_war(player, holder):
        return _answer_what_if_region(world, player, place, marshal_name, False) or ""
    return _answer_reach(world, player, marshal_name, place) or ""


def _answer_how_long(world, question: Dict) -> str:
    from backend.commands.strategic import march_turns, plot_route
    player = world.player_nation
    places = list(question.get("places") or [])
    marshal_name = str(question.get("marshal") or "")
    if marshal_name:
        me = _own(world, marshal_name)
        if me is None:
            return f"{_display(marshal_name)} leads no corps of ours, Sire."
        dest = places[0] if places else ""
        if not dest:
            return f"Name the province, Sire — where should {_display(me.name)} go?"
        path, verdict = plot_route(world, me, dest, use_weighted=False, want_verdict=True)
        if not path:
            reason = ""
            if isinstance(verdict, dict):
                reason = str(verdict.get("reason") or verdict.get("message") or "")
            return (f"No lawful road runs from {me.location} to {dest} for {_display(me.name)}, Sire"
                    + (f" — {reason}" if reason else "") + ".")
        turns = march_turns(len(path), int(getattr(me, "movement_range", 1) or 1))
        return (f"{_display(me.name)} reaches {dest} in {_plural(turns, 'turn')} from {me.location}, "
                f"Sire — the road runs {' -> '.join([me.location] + list(path))}.")
    if len(places) >= 2:
        a, b = places[0], places[1]
        hops = world.get_distance(a, b)
        if hops is None or hops < 0 or hops > 10_000:
            return f"No road our maps know joins {a} and {b}, Sire."
        return f"{a} lies {_plural(hops, 'march')} from {b}, Sire — {_plural(march_turns(hops, 1), 'turn')} for a corps of foot."
    if places:
        cap = world.get_nation_capital(player)
        hops = world.get_distance(cap, places[0]) if cap else None
        if cap and hops is not None:
            return f"{places[0]} lies {_plural(hops, 'march')} from {cap}, Sire."
    return "Name the two places, Sire, or the marshal and his destination."


# marshals ──────────────────────────────────────────────────────────────────

def _answer_trust(world, name: str) -> str:
    me = _own(world, name)
    if me is None:
        return f"{_display(name)} leads no corps of ours, Sire."
    if getattr(me, "is_sovereign", False):
        return "The Emperor's trust is his own, Sire — he never objects and never wavers."
    trust = getattr(me, "trust", None)
    value = int(getattr(trust, "value", 0) or 0)
    label = ""
    try:
        label = str(trust.get_label())
    except Exception:
        pass
    line = f"{_display(me.name)}'s trust stands at {value} of 100" + (f" — {label}" if label else "") + ", Sire."
    hostile = [other for other, v in (getattr(me, "relationships", None) or {}).items()
               if int(v) < 0 and _own(world, other) is not None]
    if hostile:
        line += (f" He is on bad terms with {_join([_display(o) for o in hostile])} — "
                 f"coordination between them suffers.")
    if getattr(me, "jealous_of", ""):
        line += f" He nurses a grievance against {_display(me.jealous_of)}."
    return line


def _answer_morale(world, name: str) -> str:
    me = _own(world, name)
    if me is None:
        return f"{_display(name)} leads no corps of ours, Sire."
    morale = int(getattr(me, "morale", 0) or 0)
    word = ("high" if morale >= 85 else "steady" if morale >= 65 else "shaken" if morale >= 45 else "low")
    line = f"{_display(me.name)}'s morale is {morale} — {word}, Sire."
    if morale < 70:
        line += " A turn of drill, out of the enemy's reach, restores it."
    return line


def _answer_ability(world, name: str) -> str:
    from backend.game_logic.marshal_overview import _build_ability
    me = world.get_marshal(name)
    if me is None:
        return f"I know no corps under {_display(name)}, Sire."
    if me.nation != world.player_nation:
        return f"{_display(name)} is {_court(world, me.nation)}'s, Sire — his gifts are his court's affair."
    ab = _build_ability(me, world) or {}
    title = ab.get("ability_name") or ""
    if not title:
        return f"{_display(me.name)} has no special ability on the roster, Sire."
    line = f"{_display(me.name)} — {title}: {ab.get('ability_description') or ''}"
    if ab.get("ability_effect"):
        line += f" Effect: {ab['ability_effect']}"
    if ab.get("ability_trigger"):
        line += f" ({ab['ability_trigger']})"
    if ab.get("ability_dormant_note"):
        line += f" {ab['ability_dormant_note']}"
    return line.strip()


_SKILL_NOTE = {
    "tactical": "combat dice (+1 per 3 points)",
    "shock": "attack damage (+5% a point)",
    "defense": "damage resistance (−5% a point)",
    "logistics": "answers the guns (+5 muster a point)",
    "administration": "recruit pricing (thrifty at 8+, wasteful at 3−)",
    "command": "rally and recovery (fast at 8+, poor at 3−)",
}


def _answer_skill(world, name: str, skill: str) -> str:
    me = _own(world, name)
    if me is None:
        return f"{_display(name)} leads no corps of ours, Sire."
    key = {"tactics": "tactical", "defence": "defense", "defensive": "defense", "admin": "administration"}.get(skill, skill)
    skills = getattr(me, "skills", None) or {}
    value = int(skills.get(key, 5) or 5)
    try:
        value = int(me.get_effective_skill(key))
    except Exception:
        pass
    return f"{_display(me.name)}'s {key} is {value} of 10, Sire — {_SKILL_NOTE.get(key, '')}."


def _answer_relationship(world, a: str, b: str) -> str:
    ma, mb = _own(world, a), _own(world, b)
    if ma is None or mb is None:
        return "Both must be marshals of ours, Sire."
    value = int(ma.get_relationship(mb.name))
    label = str(type(ma).get_relationship_label(value))
    eff = {2: "they coordinate with a will (×1.25)", 1: "they coordinate well",
           0: "they coordinate as professionals", -1: "they coordinate half-heartedly (×0.5)",
           -2: "they will not coordinate at all (×0.0)"}.get(value, "")
    line = f"{_display(ma.name)} and {_display(mb.name)} are {label.lower()} ({value:+d}), Sire"
    line += f" — {eff}." if eff else "."
    if getattr(ma, "jealous_of", "") == mb.name or getattr(mb, "jealous_of", "") == ma.name:
        line += " A grievance stands between them."
    return line


_STATE_ASKED = (
    ("fortified", r"\bfortified\b|\bentrenched\b|\bdug in\b"),
    ("drilling", r"\bdrilling\b"),
    ("broken", r"\bbroken\b"),
    ("retreating", r"\bretreating\b|\brecovering\b"),
    ("in square", r"\bin square\b"),
    ("under orders", r"\bstanding order\b|\bunder orders\b|\bmoving\b|\bmarching\b"),
    ("engaged", r"\bengaged\b|\bbusy\b"),
    ("free", r"\bidle\b|\bfree\b|\bavailable\b|\bable to\b"),
)


def _answer_marshal_state(world, name: str, asked: str = "") -> str:
    from backend.ai.question_desk import _state_words
    me = _own(world, name)
    if me is None:
        return f"{_display(name)} leads no corps of ours, Sire."
    words = set(_state_words(me))
    if getattr(me, "drilling", False) or getattr(me, "drilling_locked", False):
        words.add("drilling")
    if getattr(me, "strategic_order", None) is not None:
        words.add("under orders")
    if getattr(me, "retreating", False):
        words.add("retreating")
    engaged = any(e.nation != world.player_nation and world.is_at_war(world.player_nation, e.nation)
                  and int(getattr(e, "strength", 0) or 0) > 0
                  for e in world.get_marshals_in_region(me.location))
    if engaged:
        words.add("engaged")
    norm = _norm(asked)
    for word, pattern in _STATE_ASKED:
        if re.search(pattern, norm):
            if word == "free":
                yes = not words
            else:
                yes = any(word in w for w in words)
            verdict = "Yes" if yes else "No"
            return f"{verdict}, Sire — " + _state_clause(world, me) + "."
    return _state_clause(world, me) + "."


def _answer_anyone_state(world, word: str) -> str:
    from backend.ai.question_desk import _state_words
    hits = []
    for m in _standing(world):
        words = set(_state_words(m))
        if getattr(m, "drilling", False) or getattr(m, "drilling_locked", False):
            words.add("drilling")
        if getattr(m, "strategic_order", None) is not None:
            words.add("under orders")
            words.add("moving")
        if word in ("idle", "free") and not words and getattr(m, "strategic_order", None) is None:
            hits.append(m)
        elif any(word in w for w in words):
            hits.append(m)
    if not hits:
        return f"No marshal of ours is {word} today, Sire."
    return f"{_join([_display(m.name) + ' at ' + m.location for m in hits])} — {'is' if len(hits) == 1 else 'are'} {word}, Sire."


def _answer_orders(world) -> str:
    from backend.game_logic.ledger import _derive_strategic_order_summary
    rows = []
    for m in _standing(world):
        order = getattr(m, "strategic_order", None)
        if order is None:
            continue
        rows.append(f"{_display(m.name)}: {_derive_strategic_order_summary(m, world.current_turn)}")
    if not rows:
        return "No standing order is in force, Sire — every marshal awaits the day's orders."
    return "Standing orders, Sire: " + "; ".join(rows) + "."


def _answer_eta(world, name: str) -> str:
    from backend.commands.strategic import order_eta_phrase
    me = _own(world, name)
    if me is None:
        return f"{_display(name)} leads no corps of ours, Sire."
    order = getattr(me, "strategic_order", None)
    if order is None:
        return f"{_display(me.name)} holds no standing order, Sire — he stands at {me.location}."
    eta = order_eta_phrase(order, world.current_turn, movement_range=int(getattr(me, "movement_range", 1) or 1))
    return f"{_display(me.name)} — {str(getattr(order, 'command_type', '')).lower()} {getattr(order, 'target', '')}: {eta}."


def _answer_roster(world) -> str:
    rows = [_state_clause(world, m) for m in _standing(world)]
    prisoners = [m for m in world.get_player_marshals() if getattr(m, "captured_by", "")]
    if prisoners:
        rows.append(_join([f"{_display(m.name)} a prisoner of {_court(world, m.captured_by)}" for m in prisoners]))
    return "Our marshals, Sire:\n  " + "\n  ".join(rows)


def _answer_strongest(world) -> str:
    rows = sorted(_standing(world), key=lambda m: -int(m.strength))
    if not rows:
        return "No corps of ours stands in the field, Sire."
    top = rows[0]
    rest = ", ".join(f"{_display(m.name)} {_money(m.strength)}" for m in rows[1:4])
    return (f"{_display(top.name)} commands the largest corps, Sire — {_money(top.strength)} men at "
            f"{top.location}" + (f"; then {rest}" if rest else "") + ".")


def _answer_closest(world, subject: str, subject_type: str) -> str:
    if subject_type == "enemy":
        enemy, shown = _visible_foe(world, subject)
        if enemy is None:
            return shown
        where = enemy.location
    else:
        where, shown = subject, subject
    rows = sorted(_standing(world), key=lambda m: (world.get_distance(m.location, where), -int(m.strength)))
    if not rows:
        return "No corps of ours stands in the field, Sire."
    d0 = world.get_distance(rows[0].location, where)
    near = [m for m in rows if world.get_distance(m.location, where) == d0]
    names = _join([f"{_display(m.name)} at {m.location}" for m in near[:3]])
    more = f" (and {len(near) - 3} more)" if len(near) > 3 else ""
    dist = "on the same ground" if d0 == 0 else f"{_plural(d0, 'march')} away"
    return f"{names}{more} {'is' if len(near) == 1 else 'are'} nearest {shown}, Sire — {dist}."


def _answer_best_for(world, skill: str) -> str:
    rows = _standing(world)
    if not rows:
        return "No corps of ours stands in the field, Sire."
    def val(m):
        try:
            return int(m.get_effective_skill(skill))
        except Exception:
            return int((getattr(m, "skills", None) or {}).get(skill, 5) or 5)
    rows.sort(key=lambda m: -val(m))
    top = rows[0]
    word = {"shock": "an assault", "defense": "a defence", "administration": "the levies",
            "command": "a rally", "tactical": "the field"}.get(skill, skill)
    return (f"For {word}, {_display(top.name)} — {skill} {val(top)} of 10, {_money(top.strength)} men at "
            f"{top.location}, Sire. Then " + ", ".join(f"{_display(m.name)} {val(m)}" for m in rows[1:3]) + ".")


def _answer_glory(world, name: str) -> str:
    from backend.game_logic.jealousy import get_crowned_marshal, get_nation_ladder
    ladder = get_nation_ladder(world, world.player_nation) or []
    if name:
        me = _own(world, name)
        if me is None:
            return f"{_display(name)} leads no corps of ours, Sire."
        score = next((g for m, g in ladder if m.name == me.name), 0)
        rank = next((i + 1 for i, (m, _) in enumerate(ladder) if m.name == me.name), None)
        line = f"{_display(me.name)} holds {_plural(score, 'point')} of glory, Sire"
        if rank:
            line += f" — {rank}{'st' if rank == 1 else 'nd' if rank == 2 else 'rd' if rank == 3 else 'th'} on the ladder of {len(ladder)}"
        return line + "."
    if not ladder:
        return "The ladder is empty, Sire — no marshal of ours has won glory yet."
    crowned = get_crowned_marshal(world, world.player_nation)
    top = ", ".join(f"{_display(m.name)} {g}" for m, g in ladder[:4])
    line = f"The ladder of glory, Sire: {top}."
    if crowned is not None:
        line += f" {_display(getattr(crowned, 'name', str(crowned)))} wears the crown."
    else:
        line += " No one wears the crown yet."
    return line


def _answer_jealous(world, name: str) -> str:
    from backend.game_logic.dotation import get_expectation, get_shortfall, is_eroding
    rows = _standing(world) if not name else [m for m in [_own(world, name)] if m is not None]
    if name and not rows:
        return f"{_display(name)} leads no corps of ours, Sire."
    griefs = []
    for m in rows:
        bits = []
        if getattr(m, "jealous_of", ""):
            bits.append(f"envies {_display(m.jealous_of)}")
        try:
            short = int(get_shortfall(m, world) or 0)
            if short > 0:
                bits.append(f"expects a reward ({_money(short)}g short" + (", eroding" if is_eroding(m, world) else "") + ")")
        except Exception:
            pass
        trust = int(getattr(getattr(m, "trust", None), "value", 100) or 100)
        if trust < 40:
            bits.append(f"trust low at {trust}")
        if bits:
            griefs.append(f"{_display(m.name)} " + ", ".join(bits))
    if name:
        m = rows[0]
        if not griefs:
            exp = 0
            try:
                exp = int(get_expectation(m) or 0)
            except Exception:
                pass
            return (f"{_display(m.name)} is content, Sire — no grievance, no envy"
                    + (f", his expectation of {_money(exp)}g met" if exp else "") + ".")
        return griefs[0] + ", Sire."
    if not griefs:
        return "No marshal of ours nurses a grievance today, Sire."
    return "Grievances, Sire: " + "; ".join(griefs) + "."


def _answer_expectation(world, name: str) -> str:
    from backend.game_logic.dotation import (get_expectation, get_satisfaction, get_shortfall,
                                              is_eroding, is_dotation_world)
    try:
        if not is_dotation_world(world):
            return "No marshal expects a reward on this board, Sire — the estates are dormant here."
    except Exception:
        pass
    rows = _standing(world) if not name else [m for m in [_own(world, name)] if m is not None]
    if name and not rows:
        return f"{_display(name)} leads no corps of ours, Sire."
    out = []
    for m in rows:
        if getattr(m, "is_sovereign", False):
            continue
        exp = int(get_expectation(m) or 0)
        sat = int(get_satisfaction(m, world) or 0)
        short = int(get_shortfall(m, world) or 0)
        if name or short > 0:
            state = ("met" if short <= 0 else
                     f"{_money(short)}g short" + (", eroding his trust" if is_eroding(m, world) else ", in grace"))
            out.append(f"{_display(m.name)} expects {_money(exp)}g a turn and holds {_money(sat)}g — {state}")
    if not out:
        return "Every marshal's expectation is met today, Sire — no reward is owed."
    return ("Rewards, Sire: " if not name else "") + "; ".join(out) + "."


def _answer_army_total(world) -> str:
    rows = _standing(world)
    total = sum(int(m.strength) for m in rows)
    cav = sum(int(m.strength) for m in rows if getattr(m, "cavalry", False))
    art = sum(int(m.strength) for m in rows if getattr(m, "artillery", False))
    foot = total - cav - art
    return (f"The army stands at {_money(total)} men in {_plural(len(rows), 'corps')}, Sire — "
            f"{_money(foot)} foot, {_money(cav)} horse, {_money(art)} guns.")


def _answer_authority(world) -> str:
    from backend.models.authority import get_imperial_grip
    tracker = getattr(world, "authority_tracker", None)
    auth = int(getattr(tracker, "authority", 0) or 0)
    label = ""
    try:
        label = str(tracker.get_authority_label())
    except Exception:
        pass
    grip = int(get_imperial_grip(world, world.player_nation))
    return (f"Your authority stands at {auth} of 100" + (f" ({label})" if label else "")
            + f", Sire, and the imperial grip reads {grip} — the marshals' and the courts' measure of "
            f"how far the Empire holds together. Below 30 the satellites bleed; above 70 the marshals keep their calm.")


# naval ─────────────────────────────────────────────────────────────────────

def _answer_fleet(world) -> str:
    from backend.game_logic import naval
    summary = naval.player_naval_summary(world) or {}
    if not summary.get("active"):
        return "France keeps no fleet in commission on this board, Sire."
    line = (f"The fleet musters {_plural(int(summary.get('ships') or 0), 'sail')} at readiness "
            f"{int(summary.get('readiness') or 0)}, posture {summary.get('posture') or 'guard'}, "
            f"under {summary.get('admiral') or 'the Admiralty'}, Sire.")
    fleet = naval.get_fleet(world, world.player_nation) or {}
    ports = int(fleet.get("ports") or 0)
    if ports:
        line += f" It lies across {_plural(ports, 'dockyard')}."
    if summary.get("blockaded_by"):
        line += f" {summary['blockaded_by']} blockades us."
    if summary.get("line"):
        line += f" {summary['line']}"
    return line


def _answer_foreign_fleet(world, nation: str) -> str:
    from backend.game_logic import naval
    theirs = naval.get_fleet(world, nation) or {}
    ours = naval.get_fleet(world, world.player_nation) or {}
    if not theirs:
        return f"{_court(world, nation)} keeps no fleet our Admiralty counts, Sire."
    line = (f"{_court(world, nation)} musters {_plural(int(theirs.get('ships') or 0), 'sail')} "
            f"({theirs.get('admiral') or 'their admiralty'}), Sire")
    if ours:
        line += f", against our {int(ours.get('ships') or 0)}"
    line += ". Orders of battle are public — the gazettes print them."
    return line


def _answer_crossing(world, question: Dict) -> str:
    from backend.game_logic import naval
    player = world.player_nation
    place = str(question.get("subject") or "")
    marshal_name = str(question.get("marshal") or "")
    verdicts = naval.link_verdicts_for(world, player) or {}
    if not verdicts:
        return "No sea crossing bears on our roads today, Sire."
    rows = []
    for key, verdict in verdicts.items():
        ends = key.split("|") if isinstance(key, str) else list(key)
        if place and place not in ends and not question.get("channel"):
            continue
        if question.get("channel") and "London" not in ends:
            continue
        a, b = (ends + ["", ""])[:2]
        try:
            rows.append(naval.crossing_line(world, a, b, verdict, player))
        except Exception:
            rows.append(f"{a}–{b}: {verdict.get('verdict', '')}")
    if not rows:
        if place:
            return f"No sea road of ours ends at {place}, Sire — it is reached by land or not at all."
        return "No sea crossing bears on our roads today, Sire."
    head = "The crossings, Sire:" if len(rows) > 1 else "The crossing, Sire:"
    line = head + " " + " ".join(rows)
    if marshal_name:
        me = _own(world, marshal_name)
        if me is not None:
            line += f" {_display(me.name)} stands at {me.location}."
    return line


def _answer_landing_odds(world, place: str) -> str:
    from backend.game_logic import naval
    player = world.player_nation
    if not naval.get_fleet(world, player):
        return "France keeps no fleet to carry a landing, Sire."
    if not place:
        return "Name the shore, Sire — the odds are read against a province."
    troops = 5000
    try:
        odds = naval.expedition_slip_odds(world, player, place, troops) or {}
        levers = naval.expedition_odds_levers(world, player, place, troops) or []
        pct = odds.get("odds") or odds.get("pct") or odds.get("chance")
        line = f"A descent of {_money(troops)} on {place} slips through at about {int(pct) if pct is not None else '?'}%, Sire."
        if levers:
            line += " " + naval.levers_line(levers)
        return line
    except Exception as exc:
        return f"The Admiralty cannot read the odds for {place}, Sire ({exc})."


def _answer_build_time(world) -> str:
    from backend.game_logic import naval
    player = world.player_nation
    refusal = naval.check_build_fleet(world, player)
    rate = int(naval.build_rate(world, player) or 0)
    line = f"The yards lay down {_plural(rate, 'keel')} a turn, Sire"
    line += " — halved under blockade." if rate == 1 else "."
    if refusal:
        line += f" Today: {refusal}"
    return line


def _answer_closure(world) -> str:
    from backend.game_logic import naval
    closure = float(naval.closure_against(world, "Britain") or 0.0)
    tier = int(naval.cs_closure_tier(closure) or 0)
    return (f"The Continental System closes {int(round(closure * 100))}% of Britain's trade, Sire "
            f"(tier {tier} of 3). Every port we shut raises it; her own blockade answers it.")


# diplomacy ─────────────────────────────────────────────────────────────────

def _intent_clause(world, nation: str) -> str:
    try:
        from backend.game_logic.intent import build_intent_payload
        p = build_intent_payload(nation, world) or {}
        if p.get("want_title"):
            line = (f"Talleyrand reads its design as {p['want_title']}, against "
                    f"{p.get('against_display') or 'nobody'}; it would go as far as "
                    f"{str(p.get('price_display') or 'nothing').lower()} for it (weight {p.get('weight')}).")
            extra = str(p.get("defenceless_prize_line") or "")
            return line + (f" {extra[0].upper() + extra[1:]}." if extra else "")
        if p.get("summary"):
            summ = str(p["summary"])
            return summ[0].upper() + summ[1:] + "."
    except Exception:
        pass
    return ""


def _answer_stance_nation(world, nation: str) -> str:
    from backend.game_logic.diplomacy import get_relation
    player = world.player_nation
    court = _court(world, nation)
    state = str(world.get_diplomatic_state(player, nation) or "PEACE")
    rel = int(get_relation(world, player, nation) or 0)
    coalition = getattr(world, "active_coalition", None) or {}
    member = nation in (coalition.get("members") or [])
    words = {"WAR": "at war with us", "ARMISTICE": "under a truce with us", "PEACE": "at peace with us",
             "OPEN_BORDERS": "open to our armies", "NON_AGGRESSION": "bound to us by a non-aggression pact",
             "DEFENSIVE_ALLIANCE": "our defensive ally", "ALLIANCE": "our ally", "VASSAL": "our vassal"}
    line = f"{court} is {words.get(state, state.lower())}, relation {rel:+d}, Sire."
    if member:
        line += " It stands in the coalition against us."
    intent = _intent_clause(world, nation)
    if intent:
        line += " " + intent
    return line


def _answer_relation(world, nation: str) -> str:
    return _answer_stance_nation(world, nation)


def _answer_coalition(world) -> str:
    from backend.game_logic.agendas import get_paymaster_nation
    coalition = getattr(world, "active_coalition", None)
    pay = get_paymaster_nation(world)
    if not coalition:
        line = "No coalition stands against us today, Sire."
        if getattr(world, "coalition_brewing", False):
            line += " One is brewing."
        if pay:
            line += f" {_court(world, pay)} is the paymaster of Europe."
        return line
    members = [_court(world, m) for m in (coalition.get("members") or [])]
    leader = coalition.get("leader") or ""
    line = (f"{coalition.get('name') or 'The coalition'}: {_join(members)}, led by "
            f"{_court(world, leader) if leader else 'no one'}, Sire.")
    if pay:
        line += f" {_court(world, pay)} pays the subsidies."
    return line


def _answer_buyoff(world, nation: str) -> str:
    from backend.game_logic.instruments import compute_buyoff_price
    price = compute_buyoff_price(world, nation)
    if price is None:
        return f"{_court(world, nation)} has no design we could buy off today, Sire."
    return f"Buying off {_court(world, nation)}'s design would cost {_money(price)} gold, Sire, and one diplomatic point."


def _answer_war_score(world, nation: str) -> str:
    from backend.game_logic.diplomacy import calculate_war_score
    player = world.player_nation
    if not world.is_at_war(player, nation):
        return f"We are not at war with {_court(world, nation)}, Sire — there is no score to read."
    comps = calculate_war_score(player, nation, world, return_components=True) or {}
    total = int(comps.get("total") or 0)
    parts = ", ".join(f"{k} {int(v):+d}" for k, v in comps.items() if k != "total" and int(v or 0))
    word = "in our favour" if total > 0 else "against us" if total < 0 else "even"
    return f"The war score against {_court(world, nation)} reads {total:+d}, {word}, Sire" + (f" — {parts}" if parts else "") + "."


def _answer_weariness(world, nation: str) -> str:
    from backend.game_logic.diplomatic_ledger import _get_nation_visibility
    from backend.models.intel import PARTIAL, VISIBILITY_PRIORITY
    court = _court(world, nation)
    if nation == world.player_nation:
        from backend.ai.question_desk import _answer_war_effort
        return _answer_war_effort(world, nation) or ""
    vis = _get_nation_visibility(nation, world)
    if VISIBILITY_PRIORITY.get(vis, 0) < VISIBILITY_PRIORITY.get(PARTIAL, 1):
        return f"We have no reading of {court}'s war weariness, Sire — Talleyrand's agents have not reached that court."
    we = int((getattr(world, "war_exhaustion", None) or {}).get(nation, 0) or 0)
    word = "fresh" if we < 40 else "tiring" if we < 80 else "weary" if we < 120 else "exhausted"
    return f"{court}'s war weariness reads {we} — {word}, Sire. A court sues sooner the higher it climbs."


def _answer_agenda(world, nation: str, place: str) -> str:
    from backend.ai.question_desk import _answer_wants
    line = _answer_wants(world, nation) or f"{_court(world, nation)} pursues no design today, Sire."
    try:
        from backend.game_logic.formations import get_formation_watch
        watch = get_formation_watch(world, nation)
        if watch and watch.get("line"):
            line += " " + str(watch["line"])
    except Exception:
        pass
    if place:
        try:
            from backend.game_logic.agendas import get_active_agenda
            view = get_active_agenda(nation, world)
            regions = list(getattr(view, "regions", None) or []) if view else []
            if place in regions:
                line += f" {place} is named in it."
            elif view:
                line += f" {place} is not among its provinces."
        except Exception:
            pass
    return line


def _answer_why_war(world, nation: str) -> str:
    from backend.game_logic.war_status import build_active_wars
    player = world.player_nation
    court = _court(world, nation)
    if not world.is_at_war(player, nation):
        return f"We are not at war with {court}, Sire."
    wars = (build_active_wars(world) or {}).get("wars") or []
    row = next((w for w in wars if w.get("opponent") == nation), None)
    line = f"We are at war with {court}, Sire"
    if row:
        if row.get("in_coalition"):
            line += " — a member of the coalition against us"
        if row.get("started_turn") is not None:
            line += f", since turn {int(row.get('started_turn'))}"
        line += "."
        if row.get("stated_reason"):
            line += f" Casus belli: {row['stated_reason']}"
    else:
        line += "."
    intent = _intent_clause(world, nation)
    if intent:
        line += " " + intent
    return line


def _answer_peace_forecast(world, nation: str, want: str) -> str:
    from backend.game_logic.diplomacy import calculate_acceptance
    player = world.player_nation
    court = _court(world, nation)
    state = str(world.get_diplomatic_state(player, nation) or "PEACE")
    if want == "alliance":
        from backend.ai.question_desk import _answer_at_war  # noqa: F401  (kept for parity)
        ptype = "alliance"
    elif want == "armistice":
        ptype = "armistice"
    else:
        ptype = "peace"
    if ptype in ("peace", "armistice") and state not in ("WAR", "ARMISTICE"):
        return f"We are not at war with {court}, Sire — there is no peace to ask for."
    try:
        verdict = calculate_acceptance({"type": ptype, "proposer_nation": player,
                                        "target_nation": nation, "terms": {}}, world) or {}
    except Exception as exc:
        return f"Talleyrand cannot read {court}'s temper today, Sire ({exc})."
    score = int(verdict.get("score") or 0)
    outcome = str(verdict.get("outcome") or "")
    feedback = verdict.get("feedback")
    fb = ""
    if isinstance(feedback, (list, tuple)):
        fb = " ".join(str(f) for f in feedback[:2])
    elif feedback:
        fb = str(feedback)
    line = f"A bare {ptype} put to {court} today scores {score} — {outcome or 'uncertain'}, Sire."
    if fb:
        line += " " + fb
    if ptype == "peace" and state == "WAR":
        line += " The settlement table (F1) prices the terms; a white peace asks the least."
    return line


def _autonomy_word(value) -> str:
    try:
        from backend.game_logic.vassal import AUTONOMY_AUTONOMOUS, AUTONOMY_PUPPET
        v = int(value)
        return "puppet" if v == AUTONOMY_PUPPET else "autonomous" if v == AUTONOMY_AUTONOMOUS else "satellite"
    except Exception:
        return str(value or "satellite")


def _answer_vassals(world) -> str:
    from backend.game_logic.vassal import forecast_vassal_loyalty
    player = world.player_nation
    rows = [(n, r) for n, r in (getattr(world, "vassals", None) or {}).items() if r.get("lord") == player]
    if not rows:
        return "France holds no vassal today, Sire."
    parts = []
    for name, row in rows:
        trend = ""
        try:
            f = forecast_vassal_loyalty(world, player, name) or {}
            if f.get("trend"):
                trend = f", {f['trend']}"
        except Exception:
            pass
        parts.append(f"{_court(world, name)} (loyalty {int(row.get('loyalty') or 0)}, {_autonomy_word(row.get('autonomy'))}{trend})")
    return f"Our vassals, Sire: {_join(parts)}."


def _answer_vassal_status(world, nation: str, other: str) -> str:
    player = world.player_nation
    court = _court(world, nation)
    row = (getattr(world, "vassals", None) or {}).get(nation)
    if row:
        lord = row.get("lord") or ""
        line = f"{court} is a vassal of {_court(world, lord)}, Sire — loyalty {int(row.get('loyalty') or 0)}, {_autonomy_word(row.get('autonomy'))}."
        if other and other != lord:
            line = f"No — {line}"
        return line
    state = str(world.get_diplomatic_state(player, nation) or "PEACE")
    if other:
        ostate = str(world.get_diplomatic_state(other, nation) or "PEACE")
        bond = {"ALLIANCE": "an ally", "DEFENSIVE_ALLIANCE": "a defensive ally", "WAR": "an enemy"}.get(ostate, "no vassal")
        return (f"{court} is no vassal of {_court(world, other)}, Sire — {bond} of theirs"
                + (", fighting beside them" if ostate == "ALLIANCE" and world.is_at_war(player, nation) else "") + ".")
    return f"{court} is nobody's vassal, Sire — a court in its own right, {state.lower().replace('_', ' ')} with us."


def _answer_loyalty(world, nation: str) -> str:
    from backend.game_logic.vassal import forecast_vassal_loyalty
    player = world.player_nation
    row = (getattr(world, "vassals", None) or {}).get(nation)
    court = _court(world, nation)
    if not row or row.get("lord") != player:
        if row:
            return f"{court} is {_court(world, row.get('lord') or '')}'s vassal, Sire — its loyalty is theirs to read."
        return f"{court} is not our vassal, Sire."
    loyalty = int(row.get("loyalty") or 0)
    line = f"{court}'s loyalty stands at {loyalty} of 100, Sire"
    try:
        f = forecast_vassal_loyalty(world, player, nation) or {}
        delta = int(f.get("forecast") or 0)
        if delta:
            line += f" — {delta:+d} a turn ({f.get('trend') or 'moving'})"
        else:
            line += " — holding steady"
    except Exception:
        pass
    line += "."
    if loyalty < 35:
        line += " Below 35 it is disaffected; invest, garrison it or grant autonomy."
    return line


def _answer_winning_war(world, nation: str) -> str:
    from backend.ai.question_desk import _answer_winning
    if nation:
        return _answer_war_score(world, nation)
    return _answer_winning(world, world.player_nation) or ""


def _answer_alarm_natural(world) -> str:
    from backend.ai.question_desk import _answer_alarm
    return _answer_alarm(world, world.player_nation)


# rules ─────────────────────────────────────────────────────────────────────

def _rule_text(world, key: str, ap: bool) -> str:
    from backend.models import marshal as M
    player = world.player_nation
    costs = getattr(world, "_action_costs", None) or {}
    def cost(action):
        try:
            return int(world.get_action_cost(action))
        except Exception:
            return int(costs.get(action, 1) or 1)
    march_ap = 2
    support_ap = 1
    try:
        probe = next(iter(_standing(world)), None)
        if probe is not None:
            march_ap = int(probe.strategic_order_ap(order_type="MOVE_TO"))
            support_ap = int(probe.strategic_order_ap(order_type="SUPPORT"))
    except Exception:
        pass
    attack_f = getattr(M, "STANCE_ATTACK_FACTOR", {}) or {}
    def_pen = int(round((1 - float(attack_f.get("defensive", 0.9))) * 100))
    gain = int(getattr(world, "DRILL_MORALE_GAIN", 10) or 10)
    gain_t = int(getattr(world, "DRILL_MORALE_GAIN_TRAINED", 15) or 15)
    pres = int(round(float(getattr(M.Marshal, "SOVEREIGN_PRESENCE_ATTACK", 0.10)) * 100))
    T = {
        "fortify": (f"Fortify digs the corps in where it stands ({cost('fortify')} action): its defence rises a little each turn "
                    f"it holds, up to the marshal's ceiling, and it takes the defensive stance — attacks from the works "
                    f"are {def_pen}% weaker, and a fortified marshal refuses a march until he breaks camp. A counter-punch "
                    f"from the works is free."),
        "unfortify": "Unfortify breaks camp: the works are abandoned, the defence bonus lost, and the corps may march again. Cautious marshals break camp free.",
        "drill": (f"Drill ({cost('drill')} action) restores +{gain} morale (+{gain_t} on a training ground) and arms a one-shot "
                  f"shock bonus for the next attack; it locks the corps for the turn, and no corps drills within the enemy's reach — "
                  f"a corps caught drilling defends at three quarters."),
        "square": "Form square braces the corps against cavalry: a charge breaks on it, but a square cannot move and its own attack is spent.",
        "support": (f"Support is a standing order ({support_ap} action): the corps marches to a marshal of ours and stays with him, "
                    f"joining any battle he fights until he is safe or the battle is won."),
        "hold": f"Hold is a standing order ({march_ap} actions; 1 for a literal marshal or the Emperor): the corps keeps its ground turn after turn, with an 'until' condition the ledger counts down.",
        "march": (f"A march (move to / march to) is a standing order of {march_ap} actions (1 for a literal marshal or the Emperor): "
                  f"the corps walks the lawful road a province a turn until it arrives; an enemy in the road stops it and asks. "
                  f"A plain 'move to' a neighbouring province is one action."),
        "pursue": f"Pursue is a standing order ({march_ap} actions): the corps follows a named enemy wherever our intelligence places him, and attacks on contact.",
        "scout": f"Scout ({cost('scout')} action) reveals a neighbouring province for a turn — the garrison, the works and any corps standing there.",
        "retreat": "Retreat is free and a word: the corps falls back one province away from the enemy and recovers over the next turns, its attacks weakened meanwhile.",
        "charge": "A cavalry charge doubles the blow and the risk: it needs a victory first to arm it, cannot be made at infantry in square, and a reckless horseman may charge unasked.",
        "garrison": "Garrison detaches men from the corps to hold a province's walls; the capital's own garrison regrows each turn.",
        "recruit": "Recruit raises a levy from the manpower pool at the quoted price — dearer at war, above the force limit, and for horse or guns; the new men come green until drilled.",
        "fort": "A fortification (built with gold and an administrative action) gives the province's garrison +25% in defence and slows an assault; a damaged one is repaired for less.",
        "depot": "A supply depot raises how many men a province can feed before attrition bites, and lets the levy be raised beyond the field cap there.",
        "watchtower": "A watchtower keeps a neighbouring province in view every turn without a scout.",
        "market": "A market raises the province's income every turn.",
        "stables": "Stables let cavalry be raised there and keep the horse corps remounted.",
        "training_ground": f"A training ground raises drill's morale gain to +{gain_t} and lets green conscripts enter the line trained.",
        "naval_yard": "A naval yard is a site: 1,200 gold, four turns, one administrative action, at most two per court — it lays down keels where there is open water to moor them.",
        "estate": "An estate endows a marshal with a province's income and a title; it meets his expectation of reward and stops the erosion of his trust — a disrupted estate feeds nobody.",
        "rente": "A rente is a pension paid from the treasury at one and a half times its face each turn; it meets a marshal's expectation like an estate, and lapses if the chest runs dry.",
        "presence": f"The Presence is the Emperor's aura: every corps of ours where he stands fights +{pres}% on attack and defence, and the enemy will not take odds against him. It dims as the imperial grip falls.",
        "rally": "The Rally is the command skill at work: a marshal of command 8 or more recovers two stages a turn from a retreat; one of 3 or less retreats deeper.",
        "intendance": "The Intendance is the administration skill at the levy: 8 or more buys recruits 15% cheaper, 3 or less 15% dearer.",
        "iron_resolve": "Iron Resolve is Davout's: each turn fortified coils a stack (to three), and his next attack spends them at +8% apiece.",
        "glory": "Glory is won in battle and counted on an eight-turn ladder; the man at the top wears the crown (+1 to shock, defence and administration), and the men below him envy him.",
        "jealousy": "A grievance is one marshal's envy of another's glory: it halves their coordination, and a petition brings it to your door to acknowledge, promise or rebuke.",
        "guarantee": "A guarantee (1 diplomatic point) pledges France to a court's defence: a would-be attacker is deterred, and if we fail to march the pledge is held against us.",
        "sponsor": "Sponsorship (1 diplomatic point) funds a court's design each turn and buys its standing; a licence at nothing a turn is a promise not to interfere.",
        "buy_off": "Buying off a design pays a court to set its ambition aside for fifteen turns; reneging on it is the strongest casus belli there is.",
        "vassal": "A vassal pays tribute and lends its marshals; it is made at the peace table, by conquest of a beaten court, or by a treaty a court accepts — and bleeds loyalty unless invested in, garrisoned or granted autonomy.",
        "autonomy": "Autonomy is a vassal's leash: a puppet pays most and rebels soonest, a satellite between, an autonomous court least.",
        "authority": "Authority is your standing with the marshals: it falls when they defy you and are let be, rises when they are rebuked; the imperial grip blends it with the Empire's territory.",
        "capture": "The Emperor can be captured only by encirclement after a defeat: the Guard buys his escape at a third of its men while it has a thousand left; in chains he is the enemy's leverage at the table.",
        "continental_system": "The Continental System closes Europe's ports to Britain: every coast we hold or ally shuts her trade, and at 60% closure she is strangled without an invasion.",
        "coalition": "A coalition forms when Europe's alarm at France passes the brewing gate: its members declare war together, its paymaster subsidises them, and a signed peace with its leader dissolves it.",
        "blockade": "A blockade is a fleet posture: the stronger navy shuts the weaker's trade and crossings, and halves its yards.",
        "expedition": "An expedition lands a corps across the water on a shore that will receive it; the odds read the fleets, the readiness and a diversion.",
        "ap": (f"Each turn gives the day's orders (military actions) and administrative actions. A tactical order costs one; "
               f"a standing march, pursuit or hold {march_ap} (1 for a literal marshal or the Emperor); support {support_ap}; "
               f"recruiting, building and the laws spend administrative actions; retreat and the desk are free."),
        "supply": "A province feeds so many men; more than that bleed to attrition each turn. Depots and capitals raise the cap; a French army lives off the land it marches through.",
        "stability": "Stability is a province's order: it grows under quiet rule, falls under occupation and plunder, and below 50 the income suffers.",
        "war_score": "The war score sums territory, battles, decisive victories, the capitals, the campaign ledger and the blood each side has paid; it prices the peace.",
        "war_exhaustion": "War weariness climbs each turn at war and with defeats; the wearier a court, the sooner it sues.",
        "attack": "Attack (one action) engages an enemy in reach; the muster names who will march with him and the odds, and a losing side may break and retreat.",
        "laws": "The laws of state are bought once and paid for every turn; the Staff is the one road to a fifth order of the day. Press the LAWS tab of the ledger.",
        "congress": "The Congress of Paris is summoned at 45 titled provinces; it sits eight turns while every court is pressed to recognise the Empire.",
        "broken": "A corps is broken when it loses badly: it falls back and cannot take orders until it rallies (two to four turns, faster under a marshal of command 8 or more); a broken corps caught again may be destroyed.",
        "diversion": "The Grand Diversion sends the fleet out to draw the Royal Navy off the Channel: one action, readiness spent, a throw at the odds the Admiralty quotes — won, it opens a window for the Descent; lost, the fleet pays at sea.",
        "morale": "Morale is the corps's heart: it falls with defeats and bleeds in the field, rises with victories and drill, and a corps under 50 fights at a discount and breaks sooner.",
        "trust_rule": "Trust is a marshal's faith in you: it rises when his counsel is heard and his victories rewarded, falls when he is overruled, neglected or left unpaid; below 40 he objects and may defy an order.",
    }
    text = T.get(key)
    if not text:
        return f"I have no rule written for '{key}', Sire — 'help' holds the command reference."
    if ap and key not in ("ap",):
        return text
    return text


# map ──────────────────────────────────────────────────────────────────────

def _answer_terrain(world, place: str) -> str:
    region = world.get_region(place)
    if region is None:
        return f"Our maps hold no entry for {place}, Sire."
    bonus = int(round(float(getattr(region, "defense_bonus", 0.0) or 0.0) * 100))
    terrain = str(getattr(region, "terrain", "") or "plains").replace("_", " ")
    kind = str(getattr(region, "region_type", "") or "").replace("_", " ")
    holder = str(getattr(region, "controller", "") or "")
    line = f"{place} is {terrain}" + (f", a {kind}" if kind else "") + (f", held by {_court(world, holder)}" if holder else "") + ", Sire."
    if bonus:
        line += f" The ground gives a defender +{bonus}%."
    else:
        line += " Open ground: no defensive bonus."
    cap = int(getattr(region, "supply_capacity", 0) or 0)
    if cap:
        line += f" It feeds {_money(cap)} men."
    return line


def _answer_adjacent(world, place: str, other: str) -> str:
    region = world.get_region(place)
    if region is None:
        return f"Our maps hold no entry for {place}, Sire."
    adj = list(getattr(region, "adjacent_regions", None) or [])
    if other:
        if other in adj:
            return f"Yes, Sire — {place} and {other} share a border; it is one march."
        hops = world.get_distance(place, other)
        return f"No, Sire — {other} is {_plural(hops, 'march')} from {place}."
    return f"{place} borders {_join(sorted(adj))}, Sire."


def _answer_province_count(world, nation: str) -> str:
    player = world.player_nation
    who = nation or player
    count = len(world.get_nation_regions(who) or [])
    if who == player:
        total = len(getattr(world, "regions", {}) or {})
        return f"France holds {_plural(count, 'province')} of {total}, Sire."
    return f"{_court(world, who)} holds {_plural(count, 'province')}, Sire."


def _answer_can_build_at(world, place: str) -> str:
    from backend.ai.question_desk import _answer_can_build
    region = world.get_region(place)
    if region is None:
        return f"Our maps hold no entry for {place}, Sire."
    holder = str(getattr(region, "controller", "") or "")
    if holder != world.player_nation:
        return f"No, Sire — {place} is {_court(world, holder) if holder else 'nobody'}'s; we build only on our own soil."
    return _answer_can_build(world, world.player_nation, place) or f"Nothing can be built at {place} today, Sire."


# calendar ─────────────────────────────────────────────────────────────────

def _answer_calendar(world) -> str:
    label = ""
    try:
        label = str(world.get_calendar_label() or "")
    except Exception:
        pass
    turn = int(getattr(world, "current_turn", 1) or 1)
    return f"It is turn {turn}" + (f" — {label}" if label else "") + ", Sire. Each turn is half a month."


# last turn ────────────────────────────────────────────────────────────────

def _last_turn_rows(world) -> List[Dict]:
    from backend.campaign_log import filter_campaign_log
    turn = int(getattr(world, "current_turn", 1) or 1)
    if turn <= 1:
        return []
    rows = [r for r in (getattr(world, "event_log", None) or []) if int(r.get("turn", -1) or -1) == turn - 1]
    try:
        return list(filter_campaign_log(rows, world) or [])
    except Exception:
        return rows


def _answer_enemy_moves(world, subject: str, subject_type: str) -> str:
    rows = _last_turn_rows(world)
    turn = int(getattr(world, "current_turn", 1) or 1)
    if subject_type == "region":
        shown = subject
    else:
        shown = _display(subject) if subject_type == "enemy" else _court(world, subject)
    if turn <= 1:
        return f"The campaign has just opened, Sire — {shown} has made no move yet."
    forms = (_forms(subject) if subject_type in ("enemy", "region")
             else (_forms(subject) + _demonyms(subject)))
    hits = []
    for r in rows:
        blob = _norm(" ".join(str(v) for k, v in r.items() if isinstance(v, str)))
        if any(_contains(blob, f) for f in forms):
            hits.append(r)
    if not hits:
        if subject_type == "region":
            region = world.get_region(subject)
            holder = str(getattr(region, "controller", "") or "") if region is not None else ""
            there = [m for m in world.get_marshals_in_region(subject)
                     if int(getattr(m, "strength", 0) or 0) > 0]
            seen = []
            from backend.models.intel import PARTIAL
            for m in there:
                if m.nation == world.player_nation or world.get_region_intel(subject).visibility_at_least(PARTIAL):
                    seen.append(_display(m.name))
            line = f"No news from {shown} last turn, Sire"
            if holder:
                line += f" — it is {_court(world, holder)}'s"
            if seen:
                line += f", and {_join(seen)} {'stands' if len(seen) == 1 else 'stand'} there"
            return line + "."
        if subject_type == "enemy":
            enemy, line = _visible_foe(world, subject)
            if enemy is None:
                return f"Nothing of {shown}'s was reported last turn, Sire. {line}"
            return f"Nothing of {shown}'s was reported last turn, Sire — he stands at {enemy.location} as far as we see."
        return f"Nothing of {shown}'s was reported last turn, Sire."
    from backend.campaign_log import format_event_oneliner
    lines = []
    for r in hits[:4]:
        try:
            lines.append(str(format_event_oneliner(r)))
        except Exception:
            lines.append(str(r.get("message") or r.get("type")))
    return f"Last turn, Sire: " + " ".join(lines)


def _answer_attacked_us(world) -> str:
    player = world.player_nation
    turn = int(getattr(world, "current_turn", 1) or 1)
    if turn <= 1:
        return "The campaign has just opened, Sire — no one has attacked us yet."
    rows = [r for r in _last_turn_rows(world) if str(r.get("type") or "") == "battle"]
    ours = [r for r in rows if r.get("defender_nation") == player or r.get("attacker_nation") == player]
    attacks = [r for r in ours if r.get("defender_nation") == player]
    if not attacks:
        return ("No one attacked us last turn, Sire." if not ours
                else "No attack fell on us last turn, Sire — the battles were ours to open.")
    from backend.campaign_log import format_event_oneliner
    lines = []
    for r in attacks[:4]:
        try:
            lines.append(str(format_event_oneliner(r)))
        except Exception:
            lines.append(f"{r.get('attacker')} attacked {r.get('defender')} at {r.get('location')}")
    return f"Yes, Sire — {_plural(len(attacks), 'attack')} last turn: " + " ".join(lines)


def _answer_court_news(world) -> str:
    from backend.ai.question_desk import _answer_news
    base = _answer_news(world, world.player_nation) or ""
    rows = [r for r in _last_turn_rows(world)
            if str(r.get("type") or "").startswith(("diplomatic", "proposal", "treaty", "coalition", "envoy", "letter"))]
    mailbox = []
    try:
        dm = getattr(world, "dialogue_manager", None)
        pending = list(getattr(dm, "queue", None) or []) if dm is not None else []
        mailbox = [d for d in pending if isinstance(d, dict) and d.get("type")]
    except Exception:
        pass
    extra = ""
    if mailbox:
        extra = f" {_plural(len(mailbox), 'letter')} wait{'s' if len(mailbox) == 1 else ''} in the mailbox (M)."
    if rows:
        from backend.campaign_log import format_event_oneliner
        lines = []
        for r in rows[:4]:
            try:
                lines.append(str(format_event_oneliner(r)))
            except Exception:
                pass
        if lines:
            return "From the courts, Sire: " + " ".join(lines) + extra
    return (base + extra) if base else ("No word from the courts last turn, Sire." + extra)


# the ground ───────────────────────────────────────────────────────────────

def _answer_garrison(world, place: str, foe: str) -> str:
    from backend.game_logic.garrison_report import garrison_view, works_bonus
    player = world.player_nation
    if not place and foe:
        enemy, line = _visible_foe(world, foe)
        if enemy is None:
            return line
        place = enemy.location
    region = world.get_region(place)
    if region is None:
        return f"Our maps hold no entry for {place}, Sire."
    holder = str(getattr(region, "controller", "") or "")
    kind, value = garrison_view(world, place, player)
    works = float(works_bonus(region) or 0.0)
    wline = f" The works give it +{int(round(works * 100))}%." if works else ""
    if kind == "exact":
        head = f"{place} ({_court(world, holder)}) is held by a garrison of {_money(value)}, Sire."
    elif kind == "band":
        head = f"{place} ({_court(world, holder)}) is held by a garrison reported as {value}, Sire."
    elif kind is None and value == 0:
        head = f"{place} ({_court(world, holder)}) has no garrison on its walls, Sire."
    else:
        return f"{place} has not been scouted, Sire — send a corps to look before the assault is weighed."
    corps = [m for m in world.get_marshals_in_region(place)
             if int(getattr(m, "strength", 0) or 0) > 0 and not getattr(m, "captured_by", "")]
    seen = []
    for m in corps:
        if m.nation == player:
            seen.append(f"{_display(m.name)} {_money(m.strength)}")
        else:
            from backend.models.intel import PARTIAL
            if world.get_region_intel(place).visibility_at_least(PARTIAL):
                seen.append(f"{_display(m.name)} of {_court(world, m.nation)}")
    if seen:
        head += f" Standing there: {_join(seen)}."
    return head + wline


def _answer_stability(world, place: str) -> str:
    from backend.models.intel import PARTIAL
    region = world.get_region(place)
    if region is None:
        return f"Our maps hold no entry for {place}, Sire."
    holder = str(getattr(region, "controller", "") or "")
    if holder != world.player_nation and not world.get_region_intel(place).visibility_at_least(PARTIAL):
        return f"We have no reading of {place}'s order, Sire — it is {_court(world, holder)}'s and unscouted."
    stab = int(getattr(region, "stability", 0) or 0)
    label = ""
    try:
        label = str(region.get_stability_label())
    except Exception:
        pass
    line = f"{place}'s stability is {stab}" + (f" — {label}" if label else "") + ", Sire."
    dmg = float(getattr(region, "war_damage", 0.0) or 0.0)
    if dmg:
        line += f" War damage suppresses {int(round(dmg * 100))}% of its income."
    return line


def _answer_income_region(world, place: str) -> str:
    region = world.get_region(place)
    if region is None:
        return f"Our maps hold no entry for {place}, Sire."
    holder = str(getattr(region, "controller", "") or "")
    base = int(getattr(region, "income_value", 0) or 0)
    eff = base
    try:
        eff = int(region.get_effective_income())
    except Exception:
        pass
    line = f"{place} yields {_money(eff)} gold a turn" + (f" ({_money(base)} before war damage and unrest)" if eff != base else "")
    line += f" to {_court(world, holder)}" if holder else ""
    return line + ", Sire."


def _answer_buildings(world, place: str) -> str:
    from backend.models.intel import FULL
    region = world.get_region(place)
    if region is None:
        return f"Our maps hold no entry for {place}, Sire."
    holder = str(getattr(region, "controller", "") or "")
    if holder != world.player_nation and not world.get_region_intel(place).visibility_at_least(FULL):
        return f"{place} is {_court(world, holder)}'s, Sire — its works are not in view; scout it."
    buildings = list(getattr(region, "buildings", None) or [])
    names = []
    for b in buildings:
        t = str(b.get("type") if isinstance(b, dict) else b).replace("_", " ")
        if isinstance(b, dict) and b.get("damaged"):
            t += " (damaged)"
        names.append(t)
    if getattr(region, "watchtower", False):
        names.append("watchtower")
    under = getattr(region, "building_under_construction", None)
    if under:
        names.append(f"{str(under.get('type') if isinstance(under, dict) else under).replace('_', ' ')} (building)")
    if not names:
        return f"Nothing is built at {place}, Sire."
    return f"At {place}, Sire: {_join(names)}."


def _answer_enemy_at(world, foe: str, place: str, fortified: bool) -> str:
    enemy, shown = _visible_foe(world, foe)
    if enemy is None:
        return shown
    intel = world.get_region_intel(enemy.location)
    line = f"{shown} stands at {enemy.location}, Sire"
    if place and place != enemy.location:
        line = f"No, Sire — {shown} stands at {enemy.location}, not {place}"
    elif place:
        line = f"Yes, Sire — {shown} stands at {place}"
    from backend.models.intel import FULL
    if intel.visibility_at_least(FULL):
        bits = []
        if getattr(enemy, "fortified", False):
            bits.append("fortified")
        stance = getattr(intel, "stance", None) or getattr(enemy, "stance", None)
        if stance:
            bits.append(str(getattr(stance, "value", stance)).lower())
        if getattr(enemy, "square_formation", False):
            bits.append("in square")
        if bits:
            line += f" — {', '.join(bits)}"
        elif fortified:
            line += " — not fortified"
        line += f", {_money(enemy.strength)} men."
    else:
        band = getattr(intel, "strength_band", None) or "a force of unknown size"
        line += f" — {band}; his works and stance are not in view."
    return line


def _answer_enemies_near(world, place: str) -> str:
    player = world.player_nation
    region = world.get_region(place)
    if region is None:
        return f"Our maps hold no entry for {place}, Sire."
    adj = set(getattr(region, "adjacent_regions", None) or []) | {place}
    foes = [e for e in world.get_visible_enemies(player)
            if e.location in adj and world.is_at_war(player, e.nation)
            and int(getattr(e, "strength", 0) or 0) > 0]
    if not foes:
        return f"No enemy corps in our sight stands at or beside {place}, Sire."
    return (f"{_plural(len(foes), 'enemy corps')} within a march of {place}, Sire: "
            + _join([f"{_display(e.name)} of {_court(world, e.nation)} at {e.location}" for e in foes]) + ".")


def _answer_nation_army(world, nation: str) -> str:
    from backend.ai.question_desk import _answer_where_nation
    if nation == world.player_nation:
        return _answer_army_total(world)
    return _answer_where_nation(world, world.player_nation, nation)


# counsel ──────────────────────────────────────────────────────────────────

def _answer_counsel(world) -> str:
    from backend.ai.counsel import military_counsel, what_can_i_do
    player = world.player_nation
    lines = military_counsel(world, player, limit=3) or []
    if not lines:
        lines = what_can_i_do(world, player, limit=3) or []
    if not lines:
        return "Nothing presses today, Sire — the board offers no order I would urge."
    return "My counsel, Sire:\n  " + "\n  ".join(lines) + "\nNothing has been ordered."


def _answer_readiness(world) -> str:
    rows = _standing(world)
    if not rows:
        return "No corps of ours stands in the field, Sire."
    total = sum(int(m.strength) for m in rows)
    low = [m for m in rows if int(m.morale) < 70]
    recovering = [m for m in rows if getattr(m, "retreating", False) or getattr(m, "broken", False)]
    summary = world.get_action_summary()
    line = (f"{_plural(len(rows), 'corps')}, {_money(total)} men, Sire; "
            f"{int(summary.get('actions_remaining', 0))} of {_plural(int(summary.get('max_actions', 0)), 'order')} left today.")
    if low:
        line += f" Morale is low in {_join([_display(m.name) + ' (' + str(int(m.morale)) + ')' for m in low])}."
    if recovering:
        line += f" Recovering: {_join([_display(m.name) for m in recovering])}."
    if not low and not recovering:
        line += " Every corps stands ready."
    return line


# refusals ─────────────────────────────────────────────────────────────────

def _answer_unknown_name(world, question: Dict) -> str:
    word = str(question.get("subject") or "")
    nearest = str(question.get("nearest") or "")
    # The classifier is pure and sees only the rosters it was handed; a name
    # the WORLD knows (a fallen marshal with the fallen lever down, a court
    # the parser did not list) is not "unknown" — the desk stands aside and
    # the router answers as it did before this slice.
    low = _norm(word)
    for name in list((getattr(world, "marshals", None) or {}).keys()) + \
            list((getattr(world, "fallen_marshals", None) or {}).keys()) + \
            list((getattr(world, "regions", None) or {}).keys()) + list(world.get_active_nations()):
        if low in _forms(str(name)) or low == _norm(str(name)):
            return None
    if nearest:
        from backend.ai.question_desk import (answer_board_question, answer_question,
                                              classify_board_question, classify_question)
        asked = str(question.get("asked") or "")
        fixed = re.sub(re.escape(word), _display(nearest), asked, count=1)
        typo = word.split()[-1] if " " in word else word
        marshals = [m.name for m in world.get_player_marshals()]
        enemies = [m.name for m in world.get_visible_enemies(world.player_nation)]
        try:
            from backend.ai.llm_client import _askable_enemy_names
            enemies = list(_askable_enemy_names({"world": world}) or enemies)
        except Exception:
            pass
        regions = list((getattr(world, "regions", None) or {}).keys())
        nations = list(world.get_active_nations())
        q2 = classify_question(fixed, marshals=marshals, enemies=enemies, regions=regions)
        if q2 is None:
            q2 = classify_board_question(fixed, marshals=marshals, enemies=enemies,
                                         regions=regions, nations=nations)
        if q2 and q2.get("kind") != "unknown_name":
            answer = answer_question(world, q2) or answer_board_question(world, q2)
            if answer:
                return f"(I read '{typo}' as {_display(nearest)}.) {answer}"
    return (f"There is no {word} on any roster our maps know, Sire — no marshal, no province, no court. "
            f"Nothing is substituted; name whom you mean.")


def _answer_reward(world, name: str) -> str:
    """W3: "reward Lannes" — the man's expectation and each instrument's
    terms, from the single sources the Reward dialog itself reads; the
    client opens his dialog off `open_reward_for`."""
    from backend.game_logic import dotation as D
    me = _own(world, name)
    if me is None:
        return f"{_display(name)} leads no corps of ours, Sire."
    if getattr(me, "is_sovereign", False):
        return "The Emperor rewards; he is not rewarded, Sire."
    try:
        if not D.is_dotation_world(world):
            return f"No reward is owed on this board, Sire — the estates are dormant here."
    except Exception:
        pass
    exp = int(D.get_expectation(me) or 0)
    sat = int(D.get_satisfaction(me, world) or 0)
    short = int(D.get_shortfall(me, world) or 0)
    line = (f"{_display(me.name)} expects {_money(exp)} gold a turn and holds {_money(sat)}"
            + (f" — {_money(short)} short" if short > 0 else " — met") + ", Sire.")
    estates = []
    try:
        estates = list(D.list_eligible_estates(world, world.player_nation) or [])
    except Exception:
        pass
    if estates:
        best = estates[0] if isinstance(estates[0], str) else str(estates[0].get("name") or estates[0])
        line += (f" An estate endows a conquered province's income for good — "
                 f"'endow {_display(me.name)} with {best}'.")
    else:
        line += " No conquered province is free to endow today."
    try:
        face = int(D.compute_rente_face(me, world) or 0)
        if face > 0:
            cost = int(D.get_rente_cost(face, world, world.player_nation) or 0)
            line += (f" A rente of {_money(face)} a turn costs the treasury {_money(cost)} "
                     f"— 'grant {_display(me.name)} a rente'.")
        else:
            line += " A rente would add nothing today — his expectation is met."
    except Exception:
        pass
    return line + " His Reward dialog is open."


def _answer_afford(world, thing: str, place: str) -> str:
    from backend.models.region import BUILDING_TYPES
    spec = BUILDING_TYPES.get(thing) if thing else None
    chest = int(world.nation_gold.get(world.player_nation, 0) or 0)
    if not spec:
        return f"The treasury holds {_money(chest)} gold, Sire — name the thing to be priced."
    cost = int(spec.get("gold_cost") or 0)
    word = thing.replace("_", " ")
    line = (f"A {word} costs {_money(cost)} gold and {int(spec.get('build_time') or 0)} turns, Sire; "
            f"the treasury holds {_money(chest)} — {'yes' if chest >= cost else 'no, ' + _money(cost - chest) + ' short'}.")
    if place:
        from backend.ai.question_desk import _answer_can_build
        region = world.get_region(place)
        if region is not None and str(getattr(region, "controller", "") or "") != world.player_nation:
            line += f" And {place} is not ours to build on."
        else:
            extra = _answer_can_build(world, world.player_nation, place) or ""
            if extra and word not in extra.lower():
                line += f" {extra}"
    return line


def _answer_foe_reach(world, foe: str, place: str) -> str:
    enemy, shown = _visible_foe(world, foe)
    if enemy is None:
        return shown
    hops = world.get_distance(enemy.location, place)
    reach = int(getattr(enemy, "movement_range", 1) or 1)
    if hops <= reach:
        return f"Yes, Sire — {shown} stands at {enemy.location}, {_plural(hops, 'march')} from {place}; he could be there this turn."
    return f"Not this turn, Sire — {shown} stands at {enemy.location}, {_plural(hops, 'march')} from {place}, and a corps makes {reach} a turn."


def _answer_personality(world, name: str) -> str:
    from backend.display_names import PERSONALITY_DISPLAY  # noqa: F401
    words = {"aggressive": "aggressive — he attacks when the odds are fair and objects to sitting idle",
             "cautious": "cautious — he counter-punches from the works and objects to long odds",
             "literal": "literal — he does exactly what he is told and asks when an order needs a reading",
             "sovereign": "the Emperor — his orders are your own will"}
    if name:
        me = _own(world, name)
        if me is None:
            return f"{_display(name)} leads no corps of ours, Sire."
        p = str(getattr(getattr(me, "personality", ""), "value", getattr(me, "personality", "")) or "").lower()
        return f"{_display(me.name)} is {words.get(p, p)}, Sire."
    rows = []
    for m in _standing(world):
        p = str(getattr(getattr(m, "personality", ""), "value", getattr(m, "personality", "")) or "").lower()
        rows.append(f"{_display(m.name)} ({p})")
    return "Our marshals, Sire: " + _join(rows) + "."


def _answer_fallen(world) -> str:
    tombs = getattr(world, "fallen_marshals", None) or {}
    ours = [n for n, t in tombs.items() if (t or {}).get("nation", world.player_nation) == world.player_nation]
    prisoners = [m.name for m in world.get_player_marshals() if getattr(m, "captured_by", "")]
    if not ours and not prisoners:
        return "We have lost no marshal, Sire — every man on the roster stands."
    line = ""
    if ours:
        line += f"Fallen: {_join([_display(n) for n in ours])}. "
    if prisoners:
        line += f"Prisoners: {_join([_display(n) for n in prisoners])}."
    return line.strip()


def _answer_landing_shores(world) -> str:
    from backend.game_logic import naval
    player = world.player_nation
    if not naval.get_fleet(world, player):
        return "France keeps no fleet to carry a landing, Sire."
    verdicts = naval.link_verdicts_for(world, player) or {}
    rows = []
    for key, verdict in verdicts.items():
        ends = key.split("|") if isinstance(key, str) else list(key)
        a, b = (ends + ["", ""])[:2]
        try:
            rows.append(naval.crossing_line(world, a, b, verdict, player))
        except Exception:
            continue
    if not rows:
        return "No sea road of ours is charted today, Sire."
    return "The shores a corps may be carried to, Sire: " + " ".join(rows)


def _answer_yards(world) -> str:
    from backend.game_logic import naval
    fleet = naval.get_fleet(world, world.player_nation) or {}
    yards = list(fleet.get("dockyards") or [])
    built = list(fleet.get("built_dockyards") or [])
    if not yards and not built:
        return "France has no naval yard in commission, Sire."
    return (f"Our yards, Sire: {_join(yards + [y for y in built if y not in yards])} — "
            f"{_plural(int(naval.build_rate(world, world.player_nation) or 0), 'keel')} a turn.")


def _answer_treaties(world) -> str:
    player = world.player_nation
    rows = []
    for nation in world.get_active_nations():
        if nation == player:
            continue
        state = str(world.get_diplomatic_state(player, nation) or "PEACE")
        if state in ("PEACE", "WAR"):
            continue
        rows.append(f"{_court(world, nation)} — {state.replace('_', ' ').lower()}")
    if not rows:
        return "France holds no treaty today, Sire — only her wars and her peaces."
    return "Our treaties, Sire: " + "; ".join(rows) + "."


def _answer_borders_nation(world, nation: str) -> str:
    player = world.player_nation
    theirs = set(world.get_nation_regions(nation) or [])
    ours = []
    for name in world.get_nation_regions(player) or []:
        region = world.get_region(name)
        if region is None:
            continue
        if any(adj in theirs for adj in (getattr(region, "adjacent_regions", None) or [])):
            ours.append(name)
    if not ours:
        return f"No province of ours touches {_court(world, nation)}'s, Sire."
    return f"Our provinces on {_court(world, nation)}'s frontier, Sire: {_join(sorted(ours))}."


def _answer_war_with_place(world, place: str) -> str:
    region = world.get_region(place)
    if region is None:
        return f"Our maps hold no entry for {place}, Sire."
    holder = str(getattr(region, "controller", "") or "")
    if not holder:
        return f"{place} is nobody's, Sire — a province, not a court."
    if holder == world.player_nation:
        return f"{place} is ours, Sire — a province, not a court."
    at_war = world.is_at_war(world.player_nation, holder)
    return (f"{place} is a province, Sire, held by {_court(world, holder)} — and we are "
            f"{'at war' if at_war else 'not at war'} with {_court(world, holder)}.")


def _answer_holder(world, place: str) -> str:
    from backend.ai.question_desk import _answer_region
    region = world.get_region(place)
    if region is None:
        return f"Our maps hold no entry for {place}, Sire."
    holder = str(getattr(region, "controller", "") or "")
    if holder == world.player_nation:
        return f"Yes, Sire — {place} is ours."
    return "No, Sire — " + (_answer_region(world, "who_holds", place) or f"{place} is {_court(world, holder)}'s.")


def _answer_who_is(world, foe: str) -> str:
    player = world.player_nation
    enemy = world.get_marshal(foe)
    shown = _display(foe)
    if enemy is None:
        tomb = (getattr(world, "fallen_marshals", None) or {}).get(foe) or {}
        if tomb:
            return f"{shown} has fallen, Sire — he was {_court(world, tomb.get('nation') or '')}'s."
        return f"I know no commander named {shown}, Sire."
    court = _court(world, enemy.nation)
    state = str(world.get_diplomatic_state(player, enemy.nation) or "PEACE")
    side = {"WAR": "against us", "ARMISTICE": "under a truce with us", "ALLIANCE": "on our side — an ally",
            "DEFENSIVE_ALLIANCE": "our defensive ally", "VASSAL": "ours — a vassal's general",
            "PEACE": "neither with us nor against us — at peace", "OPEN_BORDERS": "at peace with us, our roads open",
            "NON_AGGRESSION": "bound to us by a non-aggression pact"}.get(state, state.lower())
    line = f"{shown} commands for {court}, Sire — {side}."
    seen, where = _visible_foe(world, foe)
    if seen is not None:
        line += f" He stands at {seen.location}."
    return line


def _answer_wars_leader(world) -> str:
    from backend.ai.question_desk import _answer_wars
    return (_answer_wars(world, world.player_nation) or "") + " " + _answer_coalition(world)


def _answer_safe_natural(world, place: str) -> str:
    from backend.ai.question_desk import _answer_safe
    return _answer_safe(world, world.player_nation, place) or f"{place}: no reading, Sire."


def _answer_what_is_in(world, place: str) -> str:
    from backend.ai.question_desk import _answer_region
    base = _answer_region(world, "who_at", place) or f"Nothing stands in {place} that we can see, Sire."
    try:
        base += " " + _answer_garrison(world, place, "")
    except Exception:
        pass
    return base


def _answer_goal(world, asked: str) -> str:
    from backend.ai.first_contact import answer_first_contact
    return answer_first_contact("goal", asked, world) or "The campaign's object is the Imperial Peace, Sire — the Congress of Paris, summoned at 45 titled provinces."


def _answer_end_turn_asked(world) -> str:
    return ("Then no order goes out, Sire — I have relayed nothing. Shall I close "
            "the day? Type 'end turn' and it is done.")


# the dispatcher ───────────────────────────────────────────────────────────

def answer_state_question(world, question: Optional[Dict]) -> Optional[str]:
    if not STATE_DESK_ACTIVE or not question or world is None:
        return None
    kind = str(question.get("kind") or "")
    subject = str(question.get("subject") or "")
    try:
        if kind == "unknown_name":
            return _answer_unknown_name(world, question)
        if kind == "reward":
            return _answer_reward(world, subject)
        if kind == "end_turn_asked":
            return _answer_end_turn_asked(world)
        if kind == "who_is":
            return _answer_who_is(world, subject)
        if kind == "wars_leader":
            return _answer_wars_leader(world)
        if kind == "safe_natural":
            return _answer_safe_natural(world, subject)
        if kind == "what_is_in":
            return _answer_what_is_in(world, subject)
        if kind == "goal":
            return _answer_goal(world, str(question.get("asked") or ""))
        if kind == "afford":
            return _answer_afford(world, subject, str(question.get("place") or ""))
        if kind == "foe_reach":
            return _answer_foe_reach(world, subject, str(question.get("place") or ""))
        if kind == "personality":
            return _answer_personality(world, subject)
        if kind == "fallen":
            return _answer_fallen(world)
        if kind == "landing_shores":
            return _answer_landing_shores(world)
        if kind == "yards":
            return _answer_yards(world)
        if kind == "treaties":
            return _answer_treaties(world)
        if kind == "borders_nation":
            return _answer_borders_nation(world, subject)
        if kind == "war_with_place":
            return _answer_war_with_place(world, subject)
        if kind == "holder":
            return _answer_holder(world, subject)
        if kind == "calendar":
            text = _answer_calendar(world)
            if subject == "season":
                text += " The seasons are not yet on this board, Sire — the calendar turns, the weather does not."
            return text
        if kind == "rule":
            text = _rule_text(world, subject, bool(question.get("ap")))
            place = str(question.get("place") or "")
            if place and subject in ("fortify", "drill", "hold", "garrison", "square", "unfortify"):
                there = [m for m in _standing(world) if m.location == place]
                if there:
                    text += (f" At {place} that would be {_join([_display(m.name) for m in there])}"
                             f"; nothing has been ordered.")
                else:
                    text += f" No corps of ours stands at {place} to do it."
            return text
        if kind == "net":
            return _answer_net(world)
        if kind == "levy_cost":
            return _answer_levy_cost(world, subject, str(question.get("place") or ""))
        if kind in ("commission_cost", "bench"):
            return _answer_commission(world, subject if kind == "commission_cost" else "")
        if kind == "force_limit":
            return _answer_force_limit(world)
        if kind == "upkeep":
            return _answer_upkeep(world)
        if kind == "bills_moved":
            return _answer_bills_moved(world)
        if kind == "component":
            return _answer_component(world, subject)
        if kind == "tribute":
            return _answer_tribute(world)
        if kind == "odds_natural":
            return _answer_odds_natural(world, question)
        if kind == "what_if_defence":
            return _answer_what_if_defence(world, subject, str(question.get("marshal") or ""))
        if kind == "hold_region":
            return _answer_hold_region(world, subject, str(question.get("marshal") or ""))
        if kind == "what_if_march":
            return _answer_what_if_march(world, subject, str(question.get("marshal") or ""))
        if kind == "how_long":
            return _answer_how_long(world, question)
        if kind == "trust":
            return _answer_trust(world, subject)
        if kind == "morale":
            return _answer_morale(world, subject)
        if kind == "ability":
            return _answer_ability(world, subject)
        if kind == "skill":
            if str(question.get("skill") or "") == "all":
                me = _own(world, subject)
                if me is None:
                    return f"{_display(subject)} leads no corps of ours, Sire."
                parts = []
                for key in ("tactical", "shock", "defense", "logistics", "administration", "command"):
                    try:
                        v = int(me.get_effective_skill(key))
                    except Exception:
                        v = int((getattr(me, "skills", None) or {}).get(key, 5) or 5)
                    parts.append(f"{key} {v}")
                return f"{_display(me.name)}'s skills, Sire: " + ", ".join(parts) + " (of 10)."
            return _answer_skill(world, subject, str(question.get("skill") or "shock"))
        if kind == "relationship":
            return _answer_relationship(world, subject, str(question.get("other") or ""))
        if kind == "marshal_state":
            return _answer_marshal_state(world, subject, str(question.get("asked") or ""))
        if kind == "anyone_state":
            return _answer_anyone_state(world, subject)
        if kind == "orders":
            return _answer_orders(world)
        if kind == "eta":
            return _answer_eta(world, subject)
        if kind == "roster":
            only = list(question.get("only") or [])
            if only:
                rows = [_state_clause(world, m) for m in _standing(world) if m.name in only]
                return ("Our marshals, Sire:\n  " + "\n  ".join(rows)) if rows else "None of those leads a corps of ours, Sire."
            return _answer_roster(world)
        if kind == "strongest":
            return _answer_strongest(world)
        if kind == "closest":
            return _answer_closest(world, subject, str(question.get("subject_type") or "region"))
        if kind == "best_for":
            return _answer_best_for(world, subject)
        if kind == "glory":
            return _answer_glory(world, subject)
        if kind == "jealous":
            return _answer_jealous(world, subject)
        if kind == "expectation":
            return _answer_expectation(world, subject)
        if kind == "army_total":
            return _answer_army_total(world)
        if kind == "authority":
            return _answer_authority(world)
        if kind == "fleet":
            return _answer_fleet(world)
        if kind == "foreign_fleet":
            return _answer_foreign_fleet(world, subject)
        if kind == "crossing":
            return _answer_crossing(world, question)
        if kind == "landing_odds":
            return _answer_landing_odds(world, subject)
        if kind == "build_time":
            return _answer_build_time(world)
        if kind == "closure":
            return _answer_closure(world)
        if kind in ("stance_nation", "relation"):
            return _answer_stance_nation(world, subject)
        if kind == "coalition":
            return _answer_coalition(world)
        if kind == "alarm_natural":
            return _answer_alarm_natural(world)
        if kind == "buyoff_price":
            return _answer_buyoff(world, subject)
        if kind == "war_score":
            return _answer_war_score(world, subject)
        if kind == "weariness_nation":
            return _answer_weariness(world, subject)
        if kind == "agenda":
            return _answer_agenda(world, subject, str(question.get("place") or ""))
        if kind == "why_war":
            return _answer_why_war(world, subject)
        if kind == "winning_war":
            return _answer_winning_war(world, subject)
        if kind == "peace_forecast":
            return _answer_peace_forecast(world, subject, str(question.get("want") or "peace"))
        if kind == "vassals":
            return _answer_vassals(world)
        if kind == "vassal_status":
            return _answer_vassal_status(world, subject, str(question.get("other") or ""))
        if kind == "loyalty":
            return _answer_loyalty(world, subject)
        if kind == "terrain":
            return _answer_terrain(world, subject)
        if kind == "adjacent":
            return _answer_adjacent(world, subject, str(question.get("other") or ""))
        if kind == "province_count":
            return _answer_province_count(world, subject)
        if kind == "can_build_at":
            return _answer_can_build_at(world, subject)
        if kind == "enemy_moves":
            return _answer_enemy_moves(world, subject, str(question.get("subject_type") or "enemy"))
        if kind == "attacked_us":
            return _answer_attacked_us(world)
        if kind == "court_news":
            if question.get("plain"):
                from backend.ai.question_desk import _answer_news
                return _answer_news(world, world.player_nation) or _answer_court_news(world)
            return _answer_court_news(world)
        if kind == "garrison":
            return _answer_garrison(world, subject, str(question.get("foe") or ""))
        if kind == "stability":
            return _answer_stability(world, subject)
        if kind == "income_region":
            return _answer_income_region(world, subject)
        if kind == "buildings":
            return _answer_buildings(world, subject)
        if kind == "enemy_at":
            return _answer_enemy_at(world, subject, str(question.get("place") or ""), bool(question.get("fortified")))
        if kind == "enemies_near":
            return _answer_enemies_near(world, subject)
        if kind == "nation_army":
            return _answer_nation_army(world, subject)
        if kind == "counsel":
            return _answer_counsel(world)
        if kind == "readiness":
            return _answer_readiness(world)
    except Exception as exc:  # the desk must never break the status verb
        print(f"[STATE DESK] could not answer {question!r}: {exc}")
        return None
    return None
