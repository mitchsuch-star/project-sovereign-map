"""PC-R7 (ii) part 2 — ruling J's declared goals (Pre-Deploy S14 part 2,
October 20, 2026; `docs/audits/PEACE_CONUNDRUM_2026_10_15.md` §40 J and
§46 J; `docs/BUG_FIXES.md` §PC PC-R7; rules `SYSTEMS_REFERENCE.md` §134).

A war's ARTICLES are declared at its declaration (Victoria 3's declared war
goals): the objective PLUS up to two named terms — a province of the
target, an indemnity, a client erected from its soil. Europe hears them at
once: each article is priced at the declaration in the threat engine's own
per-province rate (`coalition.TREATY_ANNEX_ALARM_PER_PROVINCE`, the alarm
both ratifiers charge for a province annexed at a treaty) — a province
one, a client one for each province it carves, an indemnity one — on the
DECLARER's own slot. At the table a declared article is LEGITIMATE: it does
not count toward the tier ceiling's surprise (`TIER_LEGITIMACY_MISMATCH`,
"the terms claim a victory the field has not delivered"); an undeclared
demand of the same kind is priced as before. At the peace each article is
SETTLED once — taken (the target no longer holds the province, an
indemnity was paid, the client stands) or dropped — and a dropped article
returns half its alarm (`coalition.reduce_threat`), named on the
aftermath line. A war that ends by a road with no treaty seam (a court's
fall, a capitulation, the Congress, a client following its lord) settles
the turn after, read from the board (`sweep_concluded`).

ONE module owns it: the candidates (`article_candidates`, the AI's
`design_articles`), the price (`article_alarm`), the declaration
(`declare_articles` — the player's War Purpose card and the AI's design
war call the same function, GR5), the legitimacy read
(`undeclared_terms`), the settlement (`settle_at_peace`), the table's
opening draft (`declared_draft`), the guided rows that lead with them
(`guided_suggestions`), and the words.

An article, as stored on the war-objective record (`declared_terms`):

    {"kind": "province" | "indemnity" | "client", "from": <the target>,
     ["region": <province>,] ["tag": <template id>, "provinces": [...],]
     "alarm": <int>, "declared_turn": <int>,
     ["settled": "taken" | "dropped", "refund": <int>, "settled_turn": <int>]}
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

from backend.errors import report

KIND_PROVINCE = "province"
KIND_INDEMNITY = "indemnity"
KIND_CLIENT = "client"
ARTICLE_KINDS = (KIND_PROVINCE, KIND_INDEMNITY, KIND_CLIENT)

# Ruling J: "the objective PLUS up to two named terms".
MAX_DECLARED_ARTICLES = 2
# The War Purpose card offers this many provinces (the capital first, then
# the frontier by income) — a card, not a gazetteer.
MAX_PROVINCE_CANDIDATES = 6
# "A declared term dropped at the peace refunds part of its cost" — half.
DROPPED_REFUND_DIVISOR = 2

THREAT_SOURCE_DECLARED = "declared_articles"
THREAT_SOURCE_REFUND = "declared_article_dropped"

_GOLD_TYPES = frozenset({"gold_indemnity", "gold_lump", "gold_per_turn"})
_CESSION_TYPES = frozenset({"territory_cede"})


# ═══════════════════════════════════════════════════════════════════════════
# Words
# ═══════════════════════════════════════════════════════════════════════════

def _shown(world: Any, nation: str) -> str:
    try:
        from backend.game_logic.formations import formed_display_name
        return formed_display_name(world, nation)
    except Exception as exc:  # pragma: no cover — a display read never blocks
        report(exc, "declared_goals._shown")
        return str(nation)


def _client_name(world: Any, tag: str) -> str:
    from backend.game_logic.formations import get_template, get_template_identity
    identity = get_template_identity(get_template(world, tag) or {}) or {}
    return str(identity.get("display_name") or tag)


def article_display(world: Any, article: Mapping[str, Any]) -> str:
    """The article in the player's words: "Tyrol", "an indemnity",
    "the Duchy of Warsaw (a client)"."""
    kind = str(article.get("kind") or "")
    if kind == KIND_PROVINCE:
        return str(article.get("region") or "a province")
    if kind == KIND_INDEMNITY:
        return "an indemnity"
    if kind == KIND_CLIENT:
        return f"{_client_name(world, str(article.get('tag') or ''))} (a client)"
    return "an article"


def _join(items: Sequence[str]) -> str:
    items = [s for s in items if s]
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + " and " + items[-1]


def articles_display(world: Any, articles: Iterable[Mapping[str, Any]]) -> str:
    return _join([article_display(world, a) for a in articles or []])


# ═══════════════════════════════════════════════════════════════════════════
# The price — derived from the threat engine's per-province rate
# ═══════════════════════════════════════════════════════════════════════════

def _per_province() -> int:
    from backend.game_logic.coalition import TREATY_ANNEX_ALARM_PER_PROVINCE
    return int(TREATY_ANNEX_ALARM_PER_PROVINCE)


def article_alarm(article: Mapping[str, Any]) -> int:
    """The alarm an article costs at the declaration: the treaty annex's
    per-province rate — a province one, a client one for each province it
    carves, an indemnity one (it takes no province; it is priced as one
    article of the war)."""
    kind = str(article.get("kind") or "")
    if kind == KIND_CLIENT:
        provinces = [p for p in (article.get("provinces") or []) if p]
        return _per_province() * max(1, len(provinces))
    if kind in (KIND_PROVINCE, KIND_INDEMNITY):
        return _per_province()
    return 0


def article_refund(article: Mapping[str, Any]) -> int:
    return int(article_alarm(article)) // DROPPED_REFUND_DIVISOR


def articles_alarm(world: Any, declarer: str, target: str,
                   articles: Optional[Iterable[Mapping[str, Any]]]) -> int:
    """What a declaration's chosen articles will add (PC-X33: the projection
    Talleyrand reads before the declaration counts them)."""
    if not articles:
        return 0
    return sum(int(article_alarm(a)) for a in normalize_articles(world, declarer, target, articles))


# ═══════════════════════════════════════════════════════════════════════════
# The candidates — what a declaration may name
# ═══════════════════════════════════════════════════════════════════════════

def _bloc(world: Any, nation: str) -> set:
    try:
        return set(world.get_bloc_members(nation)) | {nation}
    except Exception as exc:  # pragma: no cover
        report(exc, "declared_goals._bloc")
        return {nation}


def province_candidates(world: Any, declarer: str, target: str) -> List[str]:
    """A province OF the target: its capital first, then its own soil the
    declarer's side already holds (a purpose set mid-war — Tyrol, taken),
    then the provinces it holds on the declarer's bloc frontier, richest
    first (capped for the card)."""
    regions = getattr(world, "regions", {}) or {}
    held = [r for r in world.get_nation_regions(target) if r in regions]
    bloc = _bloc(world, declarer)
    homeland = [str(r) for r in ((getattr(world, "nation_starting_regions", {}) or {}).get(target) or [])
                if str(r) in regions]
    occupied = sorted(r for r in homeland
                      if str(getattr(regions[r], "controller", "") or "") in bloc)
    capital = str(world.get_nation_capital(target) or "")
    frontier = []
    for name in held:
        if name == capital:
            continue
        adjacent = getattr(regions[name], "adjacent_regions", None) or []
        if any(str(getattr(regions.get(a), "controller", "") or "") in bloc for a in adjacent):
            frontier.append(name)
    frontier.sort(key=lambda r: (-int(getattr(regions[r], "income_value", 0) or 0), r))
    out: List[str] = []
    for r in ([capital] if (capital in held or capital in occupied) else []) + occupied + frontier:
        if r and r not in out:
            out.append(r)
    return out[:MAX_PROVINCE_CANDIDATES]


def client_candidates(world: Any, target: str) -> List[Dict[str, Any]]:
    """Every formable client template the target holds soil of — the carve
    the table's `create_client` erects (`formations.apply_create_client_clause`)."""
    from backend.game_logic.formations import get_template, template_provinces
    out: List[Dict[str, Any]] = []
    regions = getattr(world, "regions", {}) or {}
    for tag in sorted((getattr(world, "formable_nations", None) or {}).keys()):
        if tag in (getattr(world, "vassals", {}) or {}):
            continue
        provinces = template_provinces(get_template(world, tag) or {})
        if provinces and any(str(getattr(regions.get(p), "controller", "") or "") == target
                             for p in provinces):
            out.append({"kind": KIND_CLIENT, "from": target, "tag": str(tag),
                        "provinces": list(provinces)})
    return out


def article_candidates(world: Any, declarer: str, target: str) -> List[Dict[str, Any]]:
    """Every article the War Purpose card offers against `target`, priced."""
    out: List[Dict[str, Any]] = []
    for region in province_candidates(world, declarer, target):
        out.append({"kind": KIND_PROVINCE, "from": target, "region": region})
    out.append({"kind": KIND_INDEMNITY, "from": target})
    out.extend(client_candidates(world, target))
    for a in out:
        a["alarm"] = article_alarm(a)
    return out


def design_articles(world: Any, coveter: str, target: str) -> List[Dict[str, Any]]:
    """GR5 — the AI's articles at its design war: the design's own
    provinces the target holds, in the design's order, up to two. The
    series seam (down -> [], the declaration as it was)."""
    from backend.game_logic.agendas import get_agenda_military_targets
    regions = getattr(world, "regions", {}) or {}
    out: List[Dict[str, Any]] = []
    for region in get_agenda_military_targets(coveter, world) or []:
        if str(getattr(regions.get(region), "controller", "") or "") != target:
            continue
        out.append({"kind": KIND_PROVINCE, "from": target, "region": str(region)})
        if len(out) >= MAX_DECLARED_ARTICLES:
            break
    return out


def _same_article(a: Mapping[str, Any], b: Mapping[str, Any]) -> bool:
    if str(a.get("kind")) != str(b.get("kind")):
        return False
    kind = str(a.get("kind"))
    if kind == KIND_PROVINCE:
        return str(a.get("region")) == str(b.get("region"))
    if kind == KIND_CLIENT:
        return str(a.get("tag")) == str(b.get("tag"))
    return True


def normalize_articles(world: Any, declarer: str, target: str,
                       articles: Iterable[Mapping[str, Any]],
                       *, candidates: Optional[List[Mapping[str, Any]]] = None) -> List[Dict[str, Any]]:
    """Keep the articles the card could have offered — or the declarer's own
    design names (GR5: the AI's design war) — once each, at most two."""
    if candidates is not None:
        pool = list(candidates)
    else:
        pool = list(article_candidates(world, declarer, target))
        pool += [a for a in design_articles(world, declarer, target)
                 if not any(_same_article(a, c) for c in pool)]
    out: List[Dict[str, Any]] = []
    for raw in articles or []:
        if not isinstance(raw, Mapping):
            continue
        match = next((c for c in pool if _same_article(c, raw)), None)
        if match is None or any(_same_article(match, o) for o in out):
            continue
        out.append(dict(match))
        if len(out) >= MAX_DECLARED_ARTICLES:
            break
    return out


# ═══════════════════════════════════════════════════════════════════════════
# The declaration — ONE function for the player's card and the AI's design war
# ═══════════════════════════════════════════════════════════════════════════

def _record(world: Any, declarer: str, target: str) -> Optional[Dict[str, Any]]:
    objectives = getattr(world, "war_objectives", None)
    if not isinstance(objectives, dict) or not objectives:
        return None
    maker = getattr(world, "_make_diplo_key", None)
    key = maker(declarer, target) if callable(maker) else "|".join(sorted([declarer, target]))
    rec = (objectives.get(key) or {}).get(declarer)
    return rec if isinstance(rec, dict) else None


def declare_articles(world: Any, declarer: str, target: str,
                     articles: Iterable[Mapping[str, Any]],
                     *, candidates: Optional[List[Mapping[str, Any]]] = None) -> Dict[str, Any]:
    """Stamp the declared articles on the declarer's objective record against
    `target` and charge their alarm to the declarer's own slot. Returns
    {articles, alarm, display}; an empty declaration charges nothing."""
    rec = _record(world, declarer, target)
    chosen = normalize_articles(world, declarer, target, articles, candidates=candidates)
    if rec is None or not chosen:
        return {"articles": [], "alarm": 0, "display": ""}
    turn = int(getattr(world, "current_turn", 0) or 0)
    for a in chosen:
        a["alarm"] = int(article_alarm(a))
        a["declared_turn"] = turn
    total = sum(int(a["alarm"]) for a in chosen)
    rec["declared_terms"] = chosen
    from backend.game_logic.coalition import add_threat
    add_threat(world, total, THREAT_SOURCE_DECLARED, target=declarer)
    shown = articles_display(world, chosen)
    display = (f"{_shown(world, declarer)} declares the articles of the war on "
               f"{_shown(world, target)}: {shown} (+{total} alarm).")
    if hasattr(world, "log_event"):
        world.log_event({
            "type": "war_articles_declared",
            "declaring_nation": declarer,
            "target_nation": target,
            "articles": [dict(a) for a in chosen],
            "alarm": int(total),
            "display": display,
            "turn": turn,
        })
    return {"articles": chosen, "alarm": int(total), "display": display}


def declared_articles(world: Any, declarer: str, target: str,
                      *, live_only: bool = True) -> List[Dict[str, Any]]:
    rec = _record(world, declarer, target)
    if rec is None:
        return []
    if live_only and rec.get("concluded_turn") is not None:
        return []
    return [a for a in (rec.get("declared_terms") or []) if isinstance(a, dict)
            and not a.get("settled")]


def declared_line(world: Any, owner: str, opponent: str) -> str:
    """The war's articles in one phrase for its surfaces: "Tyrol and an
    indemnity" (ours), "; against us: Alsace" (theirs) — "" when none."""
    ours = articles_display(world, declared_articles(world, owner, opponent))
    theirs = articles_display(world, declared_articles(world, opponent, owner))
    parts = []
    if ours:
        parts.append(f"declared: {ours}")
    if theirs:
        parts.append(f"{_shown(world, opponent)} declared: {theirs}")
    return "; ".join(parts)


def undeclared_demands(world: Any, proposer: str, target: str,
                       demands: Iterable[Mapping[str, Any]]) -> List[Mapping[str, Any]]:
    """The bilateral dialect's demands without the proposer's declared
    articles against the target (a demand's payer defaults to the target):
    a declared province leaves a cession's region list; a declared
    indemnity exempts the gold demands."""
    arts = declared_articles(world, proposer, target)
    if not arts:
        return list(demands or [])
    out: List[Mapping[str, Any]] = []
    for d in demands or []:
        if not isinstance(d, Mapping):
            continue
        kept = d if str(d.get("from") or target) != target else _strip_declared(d, arts)
        if kept is not None:
            out.append(kept)
    return out


def theirs_line(world: Any, owner: str, opponent: str) -> str:
    """The opponent's declared articles against `owner`, in a phrase."""
    return articles_display(world, declared_articles(world, opponent, owner))


# ═══════════════════════════════════════════════════════════════════════════
# The table — legitimacy, the opening draft, the guided rows
# ═══════════════════════════════════════════════════════════════════════════

def _term_from(term: Mapping[str, Any]) -> str:
    return str(term.get("from") or "")


def _term_regions(term: Mapping[str, Any]) -> List[str]:
    names = []
    if term.get("region"):
        names.append(str(term["region"]))
    for key in ("regions", "provinces"):
        value = term.get(key)
        if isinstance(value, (list, tuple)):
            names.extend(str(v) for v in value if v)
    return names


def term_matches_article(term: Mapping[str, Any], article: Mapping[str, Any]) -> bool:
    """Does a table / treaty clause carry this declared article?"""
    if _term_from(term) != str(article.get("from") or ""):
        return False
    ttype = str(term.get("type") or "")
    kind = str(article.get("kind") or "")
    if kind == KIND_PROVINCE:
        return ttype in _CESSION_TYPES and str(article.get("region")) in _term_regions(term)
    if kind == KIND_INDEMNITY:
        return ttype in _GOLD_TYPES
    if kind == KIND_CLIENT:
        return ttype == "create_client" and str(term.get("tag") or "") == str(article.get("tag") or "")
    return False


def articles_for_side(world: Any, side: Iterable[str], payer: str) -> List[Dict[str, Any]]:
    """The live declared articles any court of `side` holds against `payer`."""
    out: List[Dict[str, Any]] = []
    for declarer in sorted({str(n) for n in side or [] if n}):
        if declarer == payer:
            continue
        for a in declared_articles(world, declarer, payer):
            out.append(dict(a, declarer=declarer))
    return out


def term_is_declared(world: Any, term: Mapping[str, Any], side: Iterable[str]) -> bool:
    payer = _term_from(term)
    if not payer:
        return False
    return any(term_matches_article(term, a) for a in articles_for_side(world, side, payer))


def _strip_declared(term: Mapping[str, Any], arts: List[Mapping[str, Any]]) -> Optional[Mapping[str, Any]]:
    """A term with the declared articles taken out of it: None when it is
    wholly declared, the term itself when untouched, a cession with the
    declared provinces struck from its list when only some were."""
    ttype = str(term.get("type") or "")
    if ttype in _CESSION_TYPES or ttype == "territory":
        declared = {str(a.get("region")) for a in arts if a.get("kind") == KIND_PROVINCE}
        regions = _term_regions(term)
        kept = [r for r in regions if r not in declared]
        if not regions or len(kept) == len(regions):
            return term
        if not kept:
            return None
        out = dict(term, regions=kept, value=len(kept))
        out.pop("region", None)
        return out
    if ttype in _GOLD_TYPES and any(a.get("kind") == KIND_INDEMNITY for a in arts):
        return None
    if ttype == "create_client" and any(a.get("kind") == KIND_CLIENT
                                        and str(a.get("tag")) == str(term.get("tag") or "")
                                        for a in arts):
        return None
    return term


def undeclared_terms(world: Any, terms: Iterable[Mapping[str, Any]],
                     side: Iterable[str]) -> List[Mapping[str, Any]]:
    """The legitimacy read's package: every term with the articles the
    proposing side declared at the war taken out (ruling J — a declared
    article is LEGITIMATE). The series seam (down -> the terms unchanged)."""
    side = list(side or [])
    out: List[Mapping[str, Any]] = []
    for t in terms or []:
        payer = _term_from(t)
        arts = articles_for_side(world, side, payer) if payer else []
        kept = _strip_declared(t, arts) if arts else t
        if kept is not None:
            out.append(kept)
    return out


def objective_articles(record: Optional[Mapping[str, Any]]) -> List[Mapping[str, Any]]:
    """PC-X37: a war objective's live declared articles — the war's own
    aims, which its objective reads as its own (the alignment and the
    burdened court's "term matches the war objective"). The series seam
    (down -> [], the objective as it was)."""
    if not isinstance(record, Mapping):
        return []
    return [a for a in record.get("declared_terms") or []
            if isinstance(a, Mapping) and not a.get("settled")]


def war_purpose_action(world: Any, player: str, target: str) -> Optional[Dict[str, Any]]:
    """PC-X42 (the user's rule: diplomacy is never typed): the Cabinet row
    that names a war's purpose and its articles — offered while France's
    purpose against `target` is the declaration's default `defense` (every
    war of the 1805 boot) or none; a purpose of her own cannot change
    mid-war (`_set_war_purpose_inner`)."""
    if world.get_diplomatic_state(player, target) != "WAR":
        return None
    rec = _record(world, player, target)
    if rec is not None and rec.get("concluded_turn") is None and rec.get("type") != "defense":
        return None
    return {"action": "set_war_purpose", "display_name": "Set War Purpose", "dp_cost": 0,
            "available": True, "disabled_reason": "",
            "effect_text": f"name what the war is for, and up to {MAX_DECLARED_ARTICLES} articles"}


def declared_province_ask(world: Any, nation: str, recipient: str,
                          held: Iterable[str]) -> str:
    """PC-X40 (GR5): the province a court's dictated letter asks first is the
    one it declared at the war, while the recipient still holds it. The
    series seam (down -> "", the letter's own pick)."""
    held = {str(r) for r in held or []}
    for a in declared_articles(world, nation, recipient):
        if a.get("kind") == KIND_PROVINCE and str(a.get("region")) in held:
            return str(a.get("region"))
    return ""


def declared_in_package(world: Any, terms: Iterable[Mapping[str, Any]],
                        side: Iterable[str]) -> List[str]:
    """The declared articles a package carries, in words (the row's note)."""
    side = list(side or [])
    out: List[str] = []
    for t in terms or []:
        payer = _term_from(t)
        if not payer:
            continue
        for a in articles_for_side(world, side, payer):
            if term_matches_article(t, a):
                shown = article_display(world, a)
                if shown not in out:
                    out.append(shown)
    return out


def _indemnity_amount(world: Any, payer: str) -> int:
    """The declared indemnity's sum at the table: the guided gold demand's own
    default (the payer's chest above the reserve, at the floor)."""
    from backend.game_logic.settlement_baseline import (
        CONCESSION_BASELINE_GOLD_FLOOR, CONCESSION_BASELINE_TREASURY_RESERVE,
        _concession_baseline_payer_balance,
    )
    balance = _concession_baseline_payer_balance(world, payer)
    return int(max(0, min(balance - CONCESSION_BASELINE_TREASURY_RESERVE,
                          CONCESSION_BASELINE_GOLD_FLOOR)))


def article_clause(world: Any, article: Mapping[str, Any], *, to: str) -> Optional[Dict[str, Any]]:
    """The article authored as the table's clause (the canonical dialect)."""
    kind = str(article.get("kind") or "")
    payer = str(article.get("from") or "")
    if kind == KIND_PROVINCE:
        return {"type": "territory_cede", "from": payer, "to": to, "region": str(article.get("region"))}
    if kind == KIND_INDEMNITY:
        amount = _indemnity_amount(world, payer)
        return ({"type": "gold_indemnity", "from": payer, "to": to, "amount": int(amount)}
                if amount > 0 else None)
    if kind == KIND_CLIENT:
        return {"type": "create_client", "from": payer, "to": to, "tag": str(article.get("tag")),
                "provinces": list(article.get("provinces") or [])}
    return None


def declared_draft(world: Any, *, war_instance: Mapping[str, Any], proposer_side: str,
                   proposer_leader: str, covered: Iterable[str]) -> List[Dict[str, Any]]:
    """The table's opening draft on the declared articles: one peace plus
    each covered court's declared articles that the validator signs, in
    court order. Empty when no covered court carries an article."""
    side = [str(n) for n in (war_instance.get(proposer_side) or []) if n]
    covered = sorted({str(n) for n in covered or [] if n})
    body: List[Dict[str, Any]] = []
    for court in covered:
        for a in articles_for_side(world, side, court):
            clause = article_clause(world, a, to=proposer_leader or str(a.get("declarer")))
            if clause is None or any(term_matches_article(t, a) for t in body):
                continue
            if _valid_alone(world, clause, war_instance=war_instance,
                            proposer_side=proposer_side, covered=covered):
                body.append(clause)
    return ([{"type": "peace"}] + body) if body else []


def _valid_alone(world: Any, clause: Mapping[str, Any], *, war_instance: Mapping[str, Any],
                 proposer_side: str, covered: List[str]) -> bool:
    from backend.game_logic.settlement_validation import validate_settlement_terms
    try:
        verdict = validate_settlement_terms(
            [{"type": "peace"}, dict(clause)], actor_nation=str(getattr(world, "player_nation", "")),
            player_nation=str(getattr(world, "player_nation", "")), proposer_side=proposer_side,
            world=world, war_instance=war_instance, covered_enemy_participants=covered,
            enforce_solvency=False)
    except Exception as exc:
        report(exc, "declared_goals._valid_alone")
        return False
    return bool(verdict.get("valid"))


def guided_suggestions(world: Any, *, court: str, war_id: str, draft_key: str,
                       war_instance: Mapping[str, Any], proposer_side_participants: List[str],
                       proposer_leader: str, promised_regions: Iterable[str],
                       settlement_terms: Iterable[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    """The rows that LEAD a court's guided list: "Declared at the war: Tyrol"
    — each the article as a demand the add verb takes, never one already in
    the draft or a province already promised."""
    from backend.game_logic.settlement_staging import _guided_suggestion
    promised = {str(r) for r in promised_regions or []}
    drafted = list(settlement_terms or [])
    rows: List[Dict[str, Any]] = []
    for a in articles_for_side(world, proposer_side_participants, court):
        if any(term_matches_article(t, a) for t in drafted):
            continue
        clause = article_clause(world, a, to=proposer_leader)
        if clause is None:
            continue
        if str(a.get("kind")) == KIND_PROVINCE and str(a.get("region")) in promised:
            continue
        params = {k: v for k, v in clause.items() if k in ("region", "amount", "tag")}
        rows.append(_guided_suggestion(
            label=f"Declared at the war: {article_display(world, a)}",
            group="demand",
            clause_type=str(clause["type"]),
            reason_display=(f"{_shown(world, str(a.get('declarer')))} declared it at the war "
                            f"(+{int(a.get('alarm', 0))} alarm then) — it is legitimate at the table; "
                            f"dropped at the peace, half its alarm returns."),
            court=court, war_id=war_id, draft_key=draft_key, params=params,
            declared=True,
        ))
    return rows


# ═══════════════════════════════════════════════════════════════════════════
# The peace — each article settled once; a dropped one refunds half
# ═══════════════════════════════════════════════════════════════════════════

def _pair_treaty_clauses(world: Any, key: str) -> List[Mapping[str, Any]]:
    """The clauses of the treaty in force on the pair — the peace this war
    ended in (a stream that runs on, a lump whose chest was empty, the
    sureties it holds): the board's own record of what was signed."""
    treaty = (getattr(world, "active_treaties", {}) or {}).get(key)
    if not isinstance(treaty, Mapping):
        return []
    out: List[Mapping[str, Any]] = []
    for name in ("clauses", "terms", "demands"):
        out.extend(c for c in treaty.get(name) or [] if isinstance(c, Mapping))
    return out


def _taken(world: Any, article: Mapping[str, Any], signed: List[Mapping[str, Any]]) -> bool:
    payer = str(article.get("from") or "")
    kind = str(article.get("kind") or "")
    if kind == KIND_PROVINCE:
        region = (getattr(world, "regions", {}) or {}).get(str(article.get("region")))
        holder = str(getattr(region, "controller", "") or "")
        # PC-X36: a province held as a stream's SURETY goes home with the last
        # payment (`_return_surety_regions`) — security, never a cession.
        surety = {str(r) for t in signed for r in (t.get("surety_regions") or [])}
        return bool(region is not None and holder and holder not in _bloc(world, payer)
                    and holder != payer and str(article.get("region")) not in surety)
    if kind == KIND_INDEMNITY:
        return any(str(t.get("type") or "") in _GOLD_TYPES and _term_from(t) == payer
                   for t in signed)
    if kind == KIND_CLIENT:
        rec = (getattr(world, "vassals", {}) or {}).get(str(article.get("tag") or ""))
        return bool(isinstance(rec, Mapping) and str(rec.get("lord") or "") != payer)
    return False


def settle_at_peace(world: Any, diplo_keys: Iterable[str],
                    applied_clauses: Iterable[Mapping[str, Any]] = ()) -> List[Dict[str, Any]]:
    """Settle every unsettled declared article on the pairs this peace ends:
    taken or dropped; a dropped article refunds half its alarm to its
    declarer. Returns one row per settled article. The series seam (down ->
    [], nothing settled, nothing refunded)."""
    applied = [t for t in applied_clauses or [] if isinstance(t, Mapping)]
    objectives = getattr(world, "war_objectives", {}) or {}
    turn = int(getattr(world, "current_turn", 0) or 0)
    rows: List[Dict[str, Any]] = []
    from backend.game_logic.coalition import reduce_threat
    for key in sorted({str(k) for k in diplo_keys or [] if k}):
        # PC-X36: what was signed is the applied clauses AND the pair's treaty
        # in force (a stream, an empty chest's lump, the sureties it holds)
        signed = applied + _pair_treaty_clauses(world, key)
        for declarer, rec in sorted((objectives.get(key) or {}).items()):
            if not isinstance(rec, dict):
                continue
            for a in rec.get("declared_terms") or []:
                if not isinstance(a, dict) or a.get("settled"):
                    continue
                taken = _taken(world, a, signed)
                a["settled"] = "taken" if taken else "dropped"
                a["settled_turn"] = turn
                refund = 0 if taken else article_refund(a)
                a["refund"] = int(refund)
                if refund > 0:
                    reduce_threat(world, refund, THREAT_SOURCE_REFUND, target=str(declarer))
                rows.append({"declarer": str(declarer), "article": dict(a),
                             "settled": a["settled"], "refund": int(refund)})
    if rows and hasattr(world, "log_event"):
        groups: Dict[tuple, List[Dict[str, Any]]] = {}
        for r in rows:
            groups.setdefault((r["declarer"], str(r["article"].get("from") or "")), []).append(r)
        for (declarer, payer), items in sorted(groups.items()):
            world.log_event({"type": "war_articles_settled", "turn": turn,
                             "declaring_nation": declarer, "target_nation": payer,
                             "rows": [dict(r) for r in items],
                             "display": " ".join(aftermath_lines(world, items))})
    return rows


def sweep_concluded(world: Any) -> List[Dict[str, Any]]:
    """The roads that end a war with no treaty seam — a court's fall, a
    capitulation, the Congress, a client following its lord — settle their
    articles here, read from the board, the turn after (every treaty seam
    settled its own at the signing). The pair's own treaty in force is
    the record of what was signed (`_pair_treaty_clauses`)."""
    objectives = getattr(world, "war_objectives", None)
    if not isinstance(objectives, dict) or not objectives:
        return []
    keys = []
    for key, recs in objectives.items():
        for rec in (recs or {}).values():
            if (isinstance(rec, dict) and rec.get("concluded_turn") is not None
                    and any(isinstance(a, dict) and not a.get("settled")
                            for a in rec.get("declared_terms") or [])):
                keys.append(key)
                break
    if not keys:
        return []
    return settle_at_peace(world, keys)


def settle_concluded_pair(world: Any, key: str) -> List[Dict[str, Any]]:
    """PC-X35: a pair back at war before the sweep ran would overwrite a
    concluded record whose articles never settled (the alarm kept, nothing
    returned) — the new war's records are written only after the old war's
    articles settle, read from the board."""
    recs = ((getattr(world, "war_objectives", None) or {}).get(key) or {})
    if any(isinstance(r, dict) and r.get("concluded_turn") is not None
           and any(isinstance(a, dict) and not a.get("settled") for a in r.get("declared_terms") or [])
           for r in recs.values()):
        return settle_at_peace(world, [key])
    return []


def aftermath_lines(world: Any, rows: Iterable[Mapping[str, Any]],
                    *, about: Optional[str] = None) -> List[str]:
    """One line per declarer: "The articles France declared at the war:
    Tyrol taken; an indemnity dropped — half its alarm returned (4)."
    `about` keeps only the rows a court is party to (the player's line)."""
    by: Dict[str, List[Mapping[str, Any]]] = {}
    for r in rows or []:
        art = r.get("article") or {}
        if about and about not in (str(r.get("declarer")), str(art.get("from"))):
            continue
        by.setdefault(str(r.get("declarer")), []).append(r)
    lines: List[str] = []
    for declarer, items in sorted(by.items()):
        bits = []
        refund = 0
        for r in items:
            art = r.get("article") or {}
            bits.append(f"{article_display(world, art)} {r.get('settled')}")
            refund += int(r.get("refund", 0) or 0)
        line = f"The articles {_shown(world, declarer)} declared at the war: {'; '.join(bits)}"
        if refund:
            line += f" — half the dropped articles' alarm returned ({refund})"
        lines.append(line + ".")
    return lines


# ═══════════════════════════════════════════════════════════════════════════
# The War Purpose card's articles stage
# ═══════════════════════════════════════════════════════════════════════════

ACTION_ARTICLE = "declare_war_article"
ACTION_DONE = "declare_war_articles_done"


def articles_stage_dialogue(world: Any, *, declarer: str, target: str, objective_type: str,
                            declared: List[Mapping[str, Any]], is_defensive_set: bool,
                            extra: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    """The card's second step: the objective chosen, name up to two articles.
    The FIRST option declares with what is chosen so far (none, at first) —
    the card's harmless answer."""
    from backend.game_logic.diplomacy import OBJECTIVE_TYPE_DISPLAY
    chosen = [dict(a) for a in declared or []]
    candidates = [c for c in article_candidates(world, declarer, target)
                  if not any(_same_article(c, d) for d in chosen)]
    purpose = OBJECTIVE_TYPE_DISPLAY.get(objective_type, str(objective_type).replace("_", " ").title())
    total = sum(int(a.get("alarm", 0) or 0) for a in chosen)
    so_far = (f"Declared so far: {articles_display(world, chosen)} (+{total} alarm)."
              if chosen else "No article declared yet.")
    room = MAX_DECLARED_ARTICLES - len(chosen)
    message = (
        f"{purpose} against {_shown(world, target)}. Name the articles of the war — up to "
        f"{MAX_DECLARED_ARTICLES}. Europe hears them now: {_per_province()} alarm a province "
        f"(a client {_per_province()} for each province it carves; an indemnity {_per_province()}). "
        f"At the peace a declared article is legitimate — never a victory the field has not "
        f"delivered — and one the peace drops returns half its alarm. {so_far}")
    verb = "Set the purpose" if is_defensive_set else "Declare war"
    done_label = (f"{verb} — {purpose}, with {articles_display(world, chosen)}" if chosen
                  else f"{verb} — {purpose}, no articles")
    options: List[Dict[str, Any]] = [{
        "label": done_label, "action": ACTION_DONE, "target_nation": target,
        "objective_type": objective_type,
    }]
    rows: List[Dict[str, Any]] = []
    if room > 0:
        for c in candidates:
            label = f"Declare {article_display(world, c)} (+{int(c['alarm'])} alarm)"
            options.append({"label": label, "action": ACTION_ARTICLE, "target_nation": target,
                            "objective_type": objective_type, "article": dict(c)})
            rows.append({"label": article_display(world, c), "available": True,
                         "description": _candidate_description(world, c)})
    options.append({"label": "Back Out", "action": "reconsider"})
    dialogue = {
        "type": "war_purpose_selection",
        "stage": "articles",
        "target_nation": target,
        "objective_type": objective_type,
        "declared_terms": chosen,
        "message": message,
        "objectives": rows,
        "options": options,
        "is_defensive_set": bool(is_defensive_set),
        "blocking": True,
        "turn_created": int(getattr(world, "current_turn", 0) or 0),
    }
    if extra:
        dialogue.update(dict(extra))
    return dialogue


def _candidate_description(world: Any, article: Mapping[str, Any]) -> str:
    kind = str(article.get("kind") or "")
    target = _shown(world, str(article.get("from") or ""))
    alarm = int(article.get("alarm", 0) or 0)
    if kind == KIND_PROVINCE:
        region = str(article.get("region") or "")
        capital = str(world.get_nation_capital(str(article.get("from") or "")) or "")
        what = f"{target}'s capital" if region == capital else f"a province of {target}'s"
        return f"{what} — +{alarm} alarm now; half back if the peace drops it."
    if kind == KIND_INDEMNITY:
        return f"{target} pays for the war — +{alarm} alarm now; half back if the peace drops it."
    if kind == KIND_CLIENT:
        provinces = ", ".join(article.get("provinces") or [])
        return (f"a client erected from {target}'s {provinces} — +{alarm} alarm now; "
                f"half back if the peace drops it.")
    return ""
