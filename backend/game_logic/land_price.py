"""Row FUN, Session FUN-2b — "peace terms priced" (November 27, 2026).

FUN-2 (`fear.py`, `SYSTEMS_REFERENCE.md` §240) made land taken BY ARMS cost
something. Land taken AT THE TABLE was still cheap past a point: the table's
land price stopped rising at five provinces (`calculate_term_harshness_penalty`
capped at -45, `calculate_leader_own_losses` at -25), a whole court could be
bought in one peace at a war score of 90, and the table named no price at all.
FUN-2b (`docs/NEXT_SESSION_PROMPT.md`'s FUN-2b block; `docs/GAMEPLAY_REVIEW_
2026_11_25.md` §1.3, §5; `SYSTEMS_REFERENCE.md` §241) is this module — the ONE
home of the table's land price:

* THE PRICE (`the_tables_price_keeps_rising`, read by `settlement_scoring`):
  every province a package takes from a court costs that court 9 (the land) +
  5 (its own loss) on its bar of 50, its home capital 15 more, the sixth as
  much as the first — the two floors are gone. A pure scorer rule (the pin
  calls the penalty with no world), so it binds every world.
* THE WHOLE COUNTRY (`no_court_signs_away_every_province`): a package that
  takes every province a court holds by cession is refused whatever the war
  score, in every peace France's house (France and its vassals) signs —
  either side, the table and the two-court peace. Peaces between two computer
  courts keep the 90 line (AI_INTENT_SPEC D2: an AI war may erase a minor),
  and so does an authored carve ALONE (NA-6c, DY-6: the Papal States and
  Naples are one province each — the Roman Republic and Murat's crown stay
  reachable at a decisive victory); cessions plus a carve never swallow a court.
* THE OFFERS (`the_table_offers_only_what_the_war_buys`): the guided table
  offers a province only when that court would still sign with it (its own
  number at 50 or more, re-scored exactly); otherwise the row stays, greyed,
  with its price and why. The court's last province is never offered.
* THE WORDS (`price_rows`, `price_words`): each province on the table says
  what it costs that court, each court France takes land from says how many
  more provinces it would give — the same scorer the verdict reads, re-run
  (about a millisecond a call).

Armed with FUN-2's rules by the 1805 campaign's `fear` block (`fear.armed`):
the bare flag world, the tutorials and the legacy map keep the old table
byte for byte — except THE PRICE, which is a pure function of the package.

Three seams, each zero-arg (`tests/_fun2b_seams.py`): PRICE, WHOLE, OFFER.
FUN-2b's two fear rules (FRIGHT, CALM) live in `fear.py`. Down: the table
before FUN-2b.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple

from backend.errors import report

# ═══════════════════════════════════════════════════════════════════════
# The seams (one per rule — the series rig's arms)
# ═══════════════════════════════════════════════════════════════════════


def the_tables_price_keeps_rising() -> bool:
    """FUN2B-PRICE: the table's land price never stops — the harshness
    penalty loses its -45 floor and a court's own losses their -25 floor.
    Down: the price stops at five provinces (the floors as they were)."""
    return True


def no_court_signs_away_every_province() -> bool:
    """FUN2B-WHOLE: no package France's house signs takes every province a
    court holds, whatever the war score. Down: the 90 war-score line."""
    return True


def the_table_offers_only_what_the_war_buys() -> bool:
    """FUN2B-OFFER: the guided table (the opening draft, the "Take X" rows,
    the declared articles, the Harsher button's land) offers a province only
    when that court would still sign with it. Down: offers ignore the price."""
    return True


# ═══════════════════════════════════════════════════════════════════════
# Arming, houses
# ═══════════════════════════════════════════════════════════════════════

def _threshold() -> int:
    """`settlement_scoring.ACCEPTANCE_THRESHOLD` (50), read live."""
    from backend.game_logic.settlement_scoring import ACCEPTANCE_THRESHOLD
    return int(ACCEPTANCE_THRESHOLD)


def armed(world) -> bool:
    from backend.game_logic import fear
    return bool(world is not None) and fear.armed(world)


def house_member(world, nation: str) -> bool:
    from backend.game_logic import fear
    return bool(nation) and fear.in_player_house(world, str(nation))


def house_signs(world, *nations: str) -> bool:
    """A court of France's house (France or its vassals) among `nations`."""
    return any(house_member(world, n) for n in nations if n)


def house_in_war(world, war_instance: Optional[Mapping[str, Any]]) -> bool:
    """A court of France's house fights in this war — so any peace written
    for it is France's to sign (the third-party road never treats a war
    France's house fights: `settlement_third_party.war_is_the_players`,
    `client_war_waits_for_france`)."""
    if not isinstance(war_instance, Mapping) or not war_instance:
        return False
    for key in ("attackers", "defenders", "active_participants"):
        for nation in war_instance.get(key) or []:
            if house_member(world, str(nation)):
                return True
    return False


def whole_rule_binds(world, *parties: str, war_instance: Optional[Mapping[str, Any]] = None,
                     players_table: bool = False) -> bool:
    """WHOLE is in force for this peace: the seam up, the world armed, and
    France's house signs it — the player's own table (`players_table`), a war
    France's house fights (`war_instance`), or a party of France's house among
    `parties` (the ceder, the receiver, the two courts of a two-court peace)."""
    if not (no_court_signs_away_every_province() and armed(world)):
        return False
    return (bool(players_table) or house_signs(world, *parties)
            or house_in_war(world, war_instance))


def offers_bind(world) -> bool:
    return the_table_offers_only_what_the_war_buys() and armed(world)


# ═══════════════════════════════════════════════════════════════════════
# The whole country
# ═══════════════════════════════════════════════════════════════════════

_CESSION_TYPES = ("territory_cede", "territory")


def _term_regions(term: Mapping[str, Any]) -> List[str]:
    out: List[str] = []
    regions = term.get("regions")
    if isinstance(regions, (list, tuple)):
        out.extend(str(r) for r in regions if r)
    region = term.get("region")
    if region:
        out.append(str(region))
    return out


def land_from(court: str, terms: Iterable[Mapping[str, Any]]) -> List[str]:
    """Every province a package takes from `court`: its cessions, the
    provinces of a client carved from it, a province it pays as
    compensation. In package order, each once."""
    out: List[str] = []
    for term in terms or []:
        if not isinstance(term, Mapping):
            continue
        ttype = str(term.get("type") or "")
        giver = str(term.get("from") or term.get("from_nation") or "")
        if giver != court:
            continue
        if ttype in _CESSION_TYPES or ttype == "territory_compensate":
            out.extend(_term_regions(term))
        elif ttype == "create_client":
            raw = term.get("provinces")
            if isinstance(raw, (list, tuple)):
                out.extend(str(p) for p in raw if p)
    return list(dict.fromkeys(out))


def _givers(terms: Iterable[Mapping[str, Any]]) -> List[str]:
    out: List[str] = []
    for term in terms or []:
        if not isinstance(term, Mapping):
            continue
        ttype = str(term.get("type") or "")
        if ttype in _CESSION_TYPES or ttype in ("create_client", "territory_compensate"):
            giver = str(term.get("from") or term.get("from_nation") or "")
            if giver and giver not in out:
                out.append(giver)
    return out


def _cedes_from(court: str, terms: Iterable[Mapping[str, Any]]) -> bool:
    """The package takes at least one province from `court` by cession or a
    paid compensation (not only by an authored carve)."""
    for term in terms or []:
        if not isinstance(term, Mapping):
            continue
        ttype = str(term.get("type") or "")
        giver = str(term.get("from") or term.get("from_nation") or "")
        if giver == court and (ttype in _CESSION_TYPES or ttype == "territory_compensate"):
            if _term_regions(term):
                return True
    return False


def _held(world, court: str) -> set:
    """The provinces `court` holds now (`get_nation_regions`, the per-turn
    cached lookup — golden rule 8). A world without the lookup reads as
    holding nothing, reported."""
    try:
        return set(world.get_nation_regions(court) or [])
    except Exception as exc:
        report(exc, "land_price._held: get_nation_regions")
        return set()


def takes_every_province(world, court: str, terms: Iterable[Mapping[str, Any]]) -> bool:
    """The package leaves `court` holding nothing: it holds at least one
    province and every one it holds is in the package's land from it — and
    at least one of them goes by cession (a province ceded or paid). An
    authored carve ALONE that takes all a court holds is not this rule's: it
    keeps NA-6c's decisive-victory line (90) — the Papal States are one
    province and Rome is their capital, Naples one and Murat's crown its
    carve (DY-6) — so the client kingdoms the scenario authors stay
    reachable, while cessions plus a carve never swallow a court."""
    if not court:
        return False
    terms = [t for t in (terms or []) if isinstance(t, Mapping)]
    held = _held(world, court)
    if not held:
        return False
    return held <= set(land_from(court, terms)) and _cedes_from(court, terms)


def whole_country_clause(world, terms: List[Mapping[str, Any]], *,
                         war_instance: Optional[Mapping[str, Any]] = None,
                         players_table: bool = False) -> Optional[Tuple[int, str]]:
    """The first clause that completes a whole court's surrender (its index
    and the court), or None — while WHOLE binds this peace. A clause's
    receiver counts as a party (France's house receiving the land)."""
    terms = [t for t in (terms or [])]
    for court in _givers(terms):
        receivers = [str(t.get("to") or t.get("to_nation") or "") for t in terms
                     if isinstance(t, Mapping)
                     and str(t.get("from") or t.get("from_nation") or "") == court]
        if not whole_rule_binds(world, court, *receivers, war_instance=war_instance,
                                players_table=players_table):
            continue
        if not takes_every_province(world, court, terms):
            continue
        last = 0
        for idx, term in enumerate(terms):
            if isinstance(term, Mapping) and land_from(court, [term]):
                last = idx
        return last, court
    return None


def _demand_land(demand: Mapping[str, Any]) -> List[str]:
    """The land one demand in the two-court dialect takes (its target gives
    it — the dialect names no `from`)."""
    ttype = str(demand.get("type") or "")
    if ttype in _CESSION_TYPES:
        return _term_regions(demand)
    if ttype == "create_client":
        raw = demand.get("provinces")
        return [str(p) for p in raw if p] if isinstance(raw, (list, tuple)) else []
    return []


def trim_whole_demands(world, target: str, demands: List[Dict[str, Any]],
                       proposer: str = "") -> List[Dict[str, Any]]:
    """A two-court letter's demands of `target` (the dialect names no
    `from`), its land dropped last-first until `target` keeps a province —
    while WHOLE binds the peace (France's house signs). The AI's letters are
    never written to be refused by the rule ("the announced peace must match
    the applied one")."""
    if not whole_rule_binds(world, target, proposer):
        return list(demands or [])
    out = [dict(d) for d in (demands or [])]
    held = _held(world, target)
    if not held:
        return out

    def _taken(rows):
        got = set()
        for row in rows:
            got.update(_demand_land(row))
        return got

    def _cedes(rows):
        return any(str(r.get("type") or "") in _CESSION_TYPES and _demand_land(r) for r in rows)

    while held <= _taken(out) and _cedes(out):
        idx = max((i for i, d in enumerate(out) if _demand_land(d)), default=None)
        if idx is None:
            break
        out.pop(idx)
    return out


def trim_whole_terms(world, court: str, terms: List[Dict[str, Any]], *,
                     war_instance: Optional[Mapping[str, Any]] = None) -> List[Dict[str, Any]]:
    """The table dialect's twin: the package's land from `court` dropped
    last-first until it keeps a province, while WHOLE binds this peace."""
    out = [dict(t) for t in (terms or [])]
    receivers = [str(t.get("to") or "") for t in out if str(t.get("from") or "") == court]
    if not whole_rule_binds(world, court, *receivers, war_instance=war_instance):
        return out
    while takes_every_province(world, court, out):
        idx = max((i for i, t in enumerate(out) if land_from(court, [t])), default=None)
        if idx is None:
            break
        out.pop(idx)
    return out


def keeps_one(world, court: str, terms: Iterable[Mapping[str, Any]], region: str) -> bool:
    """Taking `region` from `court` on top of `terms` leaves it a province —
    or the rule does not bind the player's table (the seam down, an unarmed
    world: the review, lane 1 — the seam down must restore the old table)."""
    if not whole_rule_binds(world, court, players_table=True):
        return True
    probe = list(terms or []) + [{"type": "territory_cede", "from": court, "region": region}]
    return not takes_every_province(world, court, probe)


# ═══════════════════════════════════════════════════════════════════════
# The price — read off the scorer itself
# ═══════════════════════════════════════════════════════════════════════

def list_price(world, court: str, region: str) -> int:
    """The price of one province on the table, from the scorer's own numbers:
    the land (0.3 of harshness at 45 per 1.5 — 9) and the court's own loss
    (5), its home capital 15 more. The exact figure on the table is re-scored
    (`price_rows`); this is the rule's statement."""
    from backend.game_logic.settlement_scoring import (
        HARSHNESS_NORMALIZATION_CEILING, HARSHNESS_PENALTY_MAX,
        LEADER_LOSS_CAPITAL, LEADER_LOSS_PER_REGION)
    land = int(round(0.3 / HARSHNESS_NORMALIZATION_CEILING * HARSHNESS_PENALTY_MAX))
    price = land - int(LEADER_LOSS_PER_REGION)
    getter = getattr(world, "get_settlement_home_capital", None)
    capital = getter(court) if callable(getter) else None
    if capital and str(capital) == str(region):
        price -= int(LEADER_LOSS_CAPITAL)
    return int(price)


def is_home_capital(world, court: str, region: str) -> bool:
    getter = getattr(world, "get_settlement_home_capital", None)
    capital = getter(court) if callable(getter) else None
    return bool(capital) and str(capital) == str(region)


class _Table:
    """One table's scoring context, re-scoring variants of its package with
    the table's own aggregator (`compute_per_court_acceptance`) — the number
    beside each court's name. Memoized per package."""

    def __init__(self, world, *, war_id: str, war_instance: Mapping[str, Any],
                 proposer_side: str, accepting_side: str, proposer_side_leader: str,
                 covered: Iterable[str]):
        self.world = world
        self.war_id = str(war_id or "")
        self.war_instance = war_instance
        self.proposer_side = proposer_side
        self.accepting_side = accepting_side
        self.leader = proposer_side_leader
        self.covered = sorted({str(c) for c in (covered or []) if c})
        self._memo: Dict[str, Dict[str, Optional[int]]] = {}

    def totals(self, terms: List[Mapping[str, Any]]) -> Dict[str, Optional[int]]:
        import json
        key = json.dumps([dict(t) for t in terms], sort_keys=True, default=str)
        if key in self._memo:
            return self._memo[key]
        from backend.game_logic.settlement_baseline import compute_per_court_acceptance
        try:
            view = compute_per_court_acceptance(
                self.world, war_id=self.war_id, war_instance=self.war_instance,
                proposer_side=self.proposer_side, accepting_side=self.accepting_side,
                proposer_side_leader=self.leader, covered_enemy_participants=self.covered,
                settlement_terms=[dict(t) for t in terms])
        except Exception as exc:
            report(exc, "land_price._Table.totals: compute_per_court_acceptance")
            view = {}
        out: Dict[str, Optional[int]] = {}
        for row in (view.get("per_court_acceptance") or []):
            total = row.get("total")
            out[str(row.get("nation") or "")] = int(total) if total is not None else None
        self._memo[key] = out
        return out

    def total(self, terms: List[Mapping[str, Any]], court: str) -> Optional[int]:
        return self.totals(terms).get(str(court))

    def offer(self, terms: List[Mapping[str, Any]], court: str,
              clause: Mapping[str, Any]) -> Dict[str, Any]:
        """One clause added to the package: what it costs `court`, her number
        after it, whether she still signs, whether she keeps a province."""
        terms = [dict(t) for t in terms]
        base = self.total(terms, court)
        keeps = (not whole_rule_binds(self.world, court, players_table=True)
                 or not takes_every_province(self.world, court, terms + [dict(clause)]))
        after = self.total(terms + [dict(clause)], court) if keeps else None
        price = (int(base) - int(after)) if (base is not None and after is not None) else None
        return {"price": price, "after": after, "base": base, "keeps_one": bool(keeps),
                "signs": bool(keeps and after is not None and int(after) >= _threshold())}


def table_for(world, *, war_id: str, war_instance: Mapping[str, Any], proposer_side: str,
              accepting_side: str = "", proposer_side_leader: str = "",
              covered: Iterable[str] = ()) -> _Table:
    """A table to re-score variants of one package on (memoized)."""
    if not accepting_side:
        accepting_side = "defenders" if proposer_side == "attackers" else "attackers"
    return _Table(world, war_id=war_id, war_instance=war_instance,
                  proposer_side=proposer_side, accepting_side=accepting_side,
                  proposer_side_leader=proposer_side_leader, covered=covered)


def _cede(court: str, receiver: str, region: str) -> Dict[str, Any]:
    return {"type": "territory_cede", "from": court, "to": receiver, "region": region}


def price_rows(world, *, war_id: str, war_instance: Mapping[str, Any],
               proposer_side: str, accepting_side: str, proposer_side_leader: str,
               covered: Iterable[str], terms: Iterable[Mapping[str, Any]],
               pools: Mapping[str, List[str]],
               receiver: str = "") -> Dict[str, Dict[str, Any]]:
    """The table's land prices, court by court, read by re-scoring:

    {court: {"total": int|None,
             "lines": {clause_index: price},           # each land clause it gives now
             "offers": {region: {"price", "after", "signs", "keeps_one"}},
             "gives": int,                             # more provinces she would give
             "holds": int}}                            # provinces she holds

    `pools` names each court's candidate provinces in the table's own order
    (`_demand_baseline_region_candidates`); `receiver` is who takes them
    (the proposer side's leader by default)."""
    terms = [dict(t) for t in (terms or []) if isinstance(t, Mapping)]
    receiver = str(receiver or proposer_side_leader or "")
    table = _Table(world, war_id=war_id, war_instance=war_instance,
                   proposer_side=proposer_side, accepting_side=accepting_side,
                   proposer_side_leader=proposer_side_leader, covered=covered)
    line = _threshold()
    out: Dict[str, Dict[str, Any]] = {}
    for court in table.covered:
        base = table.total(terms, court)
        holds = len(_held(world, court))
        row: Dict[str, Any] = {"total": base, "lines": {}, "offers": {}, "gives": 0,
                               "holds": int(holds)}
        out[court] = row
        if base is None:
            continue
        for idx, term in enumerate(terms):
            if str(term.get("type") or "") not in _CESSION_TYPES:
                continue
            if str(term.get("from") or "") != court:
                continue
            without = terms[:idx] + terms[idx + 1:]
            before = table.total(without, court)
            if before is not None:
                row["lines"][idx] = int(before) - int(base)
        pool = [str(r) for r in (pools.get(court) or []) if r]
        promised = set()
        for term in terms:
            promised.update(_term_regions(term))
        for region in pool:
            if region in promised:
                continue
            keeps = keeps_one(world, court, terms, region)
            after = table.total(terms + [_cede(court, receiver, region)], court) if keeps else None
            row["offers"][region] = {
                "price": (int(base) - int(after)) if after is not None else int(list_price(world, court, region)),
                "after": after,
                "signs": bool(keeps and after is not None and int(after) >= line),
                "keeps_one": bool(keeps),
            }
        # how many more provinces she would give: the cheapest one she would
        # still sign with, then the next (the review, lane 1: stopping at the
        # first refusal in the pool's order could read 0 while a cheaper row
        # below it signs)
        probe = list(terms)
        remaining = [r for r in pool if r not in promised]
        gives = 0
        while remaining:
            best = None
            for region in remaining:
                if not keeps_one(world, court, probe, region):
                    continue
                after = table.total(probe + [_cede(court, receiver, region)], court)
                if after is not None and int(after) >= line and (
                        best is None or int(after) > best[1]):
                    best = (region, int(after))
            if best is None:
                break
            probe = probe + [_cede(court, receiver, best[0])]
            remaining.remove(best[0])
            gives += 1
        row["gives"] = int(gives)
    return out


# ═══════════════════════════════════════════════════════════════════════
# The words (golden rule 11 — plain, the court as "she")
# ═══════════════════════════════════════════════════════════════════════

def price_words(price: Optional[int], capital: bool = False, *,
                counted_in: Optional[int] = None, after: Optional[int] = None) -> str:
    """A land line she gives now: 'costs her 24 — already counted in her 46'
    (`counted_in`, her number). A land row offered: 'would cost her 14 more —
    she would be at 56' (`after`). The blind reading of November 27 (FUN2B-…):
    with a bare "costs her 24" one reader of three added the cost instead of
    taking it off, and all three could not tell whether her number already
    counted the terms listed — the words now say it."""
    if price is None:
        return ""
    cap = " (her capital)" if capital else ""
    if after is not None or counted_in is None:
        if int(price) <= 0:
            # (the review, lane 2: "would cost her nothing — she would fall to 12")
            return f"would cost her nothing{cap}" + (
                f" — she would stay at {int(after)}" if after is not None else "")
        text = f"would cost her {int(price)} more{cap}"
        return text + (f" — she would fall to {int(after)}" if after is not None else "")
    if int(price) <= 0:
        return f"costs her nothing{cap}"
    return (f"costs her {int(price)}{cap} — without it she would be at "
            f"{int(counted_in) + int(price)}")


def refusal_words(act: str, price: int, total: Optional[int],
                  after: Optional[int] = None) -> str:
    """Why a land row is greyed: she would refuse it. `act` is the deed —
    "taking Tyrol", "carving the Duchy of Warsaw out of her lands"."""
    line = _threshold()
    if total is None:
        return "She would refuse: she will not sign any peace yet."
    left = int(after) if after is not None else int(total) - int(price)
    if int(total) < line:
        return (f"She would refuse: with these terms she is at {int(total)}, under the {line} "
                f"she needs to sign, and {act} would bring her down to {left}.")
    return (f"She would refuse: {act} would bring her down to {left}, under the {line} "
            f"she needs to sign.")


LAST_PROVINCE_WORDS = ("She keeps at least one province: no country gives up all its land "
                       "at one peace — taking a whole country takes more than one war.")


def gives_words(gives: int, holds: int, total: Optional[int], *, has_land: bool) -> str:
    """The court's one line: how many more provinces she would give now."""
    line = _threshold()
    if holds <= 1:
        return "She holds one province: no country gives up all its land at one peace."
    if total is None:
        return ""
    if gives >= 2:
        return f"She would give {gives} more provinces now."
    if gives == 1:
        return "She would give 1 more province now."
    if int(total) < line:
        return ("She will not sign even this yet: win more of the war, ask less of her, or "
                "give her something for it.")
    more = "more " if has_land else ""
    return (f"She would give no {more}land now: win more of the war, ask less of her, or give "
            f"her something for it.")


def legend_words() -> str:
    """The table's one rule line, under the courts France takes land from."""
    line = _threshold()
    return (f"The number beside a country's name is how willing she is to sign; she signs at "
            f"{line}. Each province you ask lowers it by the figure shown (her capital by more), "
            f"and dropping one gives that back. No country gives up every province it holds at "
            f"one peace.")
