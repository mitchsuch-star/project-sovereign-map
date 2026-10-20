"""PC-R7 (ii) — ruling J's compensation clause, `territory_compensate`
(Pre-Deploy S14 part 1, October 20, 2026; `docs/audits/PEACE_CONUNDRUM_2026_10_15.md`
§40 J and §46 J; `docs/BUG_FIXES.md` §PC PC-R7; rules `SYSTEMS_REFERENCE.md` §133).

The loser is paid in a THIRD party's province, or its design is pointed
elsewhere — the only way the moderate Pressburg exists in the vocabulary
(Salzburg for Tyrol, 1805; Talleyrand's Strasbourg plan to compensate
Austria at the Porte's expense, which Napoleon refused — the choice that
bred 1809; Tilsit's free hand for Russia in Finland and on the Danube).

ONE module owns the clause: the rule (`compensation_reading` — read by the
validator, the guided rows, the preview, both ratifiers and the AI's
letter), the price (`table_credit`, `bilateral_value`, `harshness`), the
apply arm both ratifiers call (`apply_territory_compensate`), the words,
and the candidates the rows and the letter offer.

The clause, canonical (the table's dialect):

    {"type": "territory_compensate", "from": <the court that pays>,
     "to": <the court compensated>, "region": <the province>,
     ["design": <the compensated court's design id>, "design_title": ...,
      "holder": <who holds the province when it was written>]}

Two FORMS, read from the province's holder — never chosen by the author:

* **paid** — the province is held by the paying court, on the side
  opposite the compensated court, and it is neither the compensated
  court's own soil (that is a return: offer it back with a cession) nor
  the paying side's LEADER's own soil (that is the leader's offer). The
  province changes hands and is titled by the treaty. Franconia —
  Bavaria's coin, Würzburg's place in the exchange that gave Austria
  Salzburg — is the board's instance.
* **pointed** — the province is held by a court OUTSIDE the war, and it
  lies in one of the compensated court's own authored designs. Nothing
  changes hands: the paying side's leader recognises the design — the
  designs ahead of it in the court's deck SLEEP (the D5 compensation
  bargain, struck at the peace table — the road the refusal "designs are
  bought off at the peace table" promised and no verb delivered) and the
  leader LICENSES it (the D5 licence, a directed sponsorship at 0 gold
  aimed at the holder). The holder takes it ill. Austria's Eastern
  Question (Albania and Rumelia, the Porte's) is the board's instance.

Both forms mint the D5 bond: what is paid is a hostage (retaking it is
reneging) and a war between the parties within the term is reneging —
the strongest grievance the instruments have (`instruments.process_
instruments`), so a moderate peace binds the victor that grants it.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple

from backend.errors import report

TERRITORY_COMPENSATE = "territory_compensate"
FORM_PAID = "paid"
FORM_POINTED = "pointed"

# A licence weighs less in a court's harshness than a province (0.3): a
# promise of non-interference — the protection clause's own weight class.
POINTED_HARSHNESS = 0.1


# ═══════════════════════════════════════════════════════════════════════
# The price — derived from the existing rates, never invented
# ═══════════════════════════════════════════════════════════════════════

def _promise_ratio() -> float:
    """What a promise weighs against a province, on the bilateral's own
    scale: the `protection` sweetener (+5) against a ceded province (+8).
    Read live, so the two can never drift."""
    from backend.game_logic.diplomacy import SWEETENER_VALUES
    province = float(SWEETENER_VALUES.get("territory_cede", 0) or 0)
    promise = float(SWEETENER_VALUES.get("protection", 0) or 0)
    return (promise / province) if province > 0 else 0.0


def is_pointed(clause: Mapping[str, Any]) -> bool:
    """The world-less reading of the form: a clause that names a design is
    the pointed form (stamped at authoring; the validator refuses a stamp
    the board contradicts, and the ratifiers re-read the board)."""
    return bool(str(clause.get("design") or "").strip())


def _clause_regions(clause: Mapping[str, Any]) -> List[str]:
    regions = clause.get("regions")
    if isinstance(regions, (list, tuple)) and regions:
        return [str(r) for r in regions if r]
    region = str(clause.get("region") or "")
    return [region] if region else []


def table_credit(clause: Mapping[str, Any]) -> int:
    """The table's concession credit to the compensated court (the court the
    row scores): a province paid is a province gained — the offer's own
    `CONCESSION_TERRITORY_PER_REGION`; a design pointed is a promise —
    that rate at the promise ratio (35 x 5/8 = 22)."""
    from backend.game_logic.settlement_scoring import CONCESSION_TERRITORY_PER_REGION
    if is_pointed(clause):
        return int(round(CONCESSION_TERRITORY_PER_REGION * _promise_ratio()))
    return int(CONCESSION_TERRITORY_PER_REGION) * max(1, len(_clause_regions(clause)))


def bilateral_value(clause: Mapping[str, Any], *, as_demand: bool = False) -> float:
    """The bilateral walk's value: as a SWEETENER (the proposer pays the
    target) a province paid is the cession sweetener's +8 a province, a
    design pointed the protection sweetener's +5; as a DEMAND (the target
    pays the proposer) the cession demand's -5 a province, a design pointed
    that rate at the promise ratio (-3)."""
    from backend.game_logic.diplomacy import DEMAND_VALUES, SWEETENER_VALUES
    count = max(1, len(_clause_regions(clause)))
    if as_demand:
        rate = float(DEMAND_VALUES.get("territory_cede", 0) or 0)
        if is_pointed(clause):
            return float(round(rate * _promise_ratio()))
        return rate * count
    if is_pointed(clause):
        return float(SWEETENER_VALUES.get("protection", 0) or 0)
    return float(SWEETENER_VALUES.get("territory_cede", 0) or 0) * count


def harshness(clause: Mapping[str, Any]) -> float:
    """What the clause weighs on the court that PAYS it (both harshness
    dialects): a province paid is a cession's 0.3; a licence 0.1."""
    if is_pointed(clause):
        return POINTED_HARSHNESS
    return 0.3 * max(1, len(_clause_regions(clause)))


# ═══════════════════════════════════════════════════════════════════════
# The rule — ONE reading for every surface
# ═══════════════════════════════════════════════════════════════════════

def homeland_owners(world, region: str) -> List[str]:
    """The courts whose 1805 soil `region` is (`nation_starting_regions`)."""
    out = []
    for nation, regions in (getattr(world, "nation_starting_regions", {}) or {}).items():
        if region in (regions or []):
            out.append(str(nation))
    return out


def _sides(world, war_instance: Optional[Mapping[str, Any]], payer: str,
           compensated: str) -> Tuple[Dict[str, str], str]:
    """(side_by_nation, payer_side_leader). Without an instance the pair's
    own live war is read; without one the two courts are the two sides."""
    instance = war_instance if isinstance(war_instance, Mapping) and war_instance else None
    if instance is None:
        try:
            from backend.game_logic.settlement_helpers import _find_active_war_instance_for_pair
            war_id = _find_active_war_instance_for_pair(world, world._make_diplo_key(payer, compensated))
            instance = (getattr(world, "war_instances", {}) or {}).get(war_id or "") or None
        except Exception as exc:
            report(exc, "compensation._sides: _find_active_war_instance_for_pair")
            instance = None
    if instance is None:
        return ({payer: "payer_side", compensated: "compensated_side"}, payer)
    side_by_nation = {str(k): str(v) for k, v in (instance.get("side_by_nation") or {}).items()}
    if not side_by_nation:
        for side in ("attackers", "defenders"):
            for n in instance.get(side) or []:
                side_by_nation[str(n)] = side
    payer_side = side_by_nation.get(payer, "")
    leader = str(instance.get("attacker_leader") if payer_side == "attackers"
                 else instance.get("defender_leader") if payer_side == "defenders" else "") or ""
    if not leader:
        members = [str(n) for n in (instance.get(payer_side) or [])] if payer_side else []
        leader = members[0] if members else payer
    return (side_by_nation, leader)


def borders_the_court(world, court: str, region: str) -> bool:
    """A paid province borders the court's 1805 soil or a province it holds
    (Salzburg lay between Tyrol and Vienna; Würzburg beside Bohemia).
    Per-court region reads only (Rule 8)."""
    obj = (getattr(world, "regions", {}) or {}).get(region)
    adjacent = set(getattr(obj, "adjacent_regions", None) or []) if obj is not None else set()
    if not adjacent:
        return False
    home = set((getattr(world, "nation_starting_regions", {}) or {}).get(court, []) or [])
    if adjacent & home:
        return True
    try:
        held = set(world.get_nation_regions(court) or [])
    except Exception as exc:
        report(exc, "compensation.borders_the_court: get_nation_regions")
        held = set()
    return bool(adjacent & held)


def _promised_by_a_bargain(world, region: str, payer: str, leader: str) -> str:
    """The ally a LIVE war bargain of the paying side promises `region` to —
    '' when none (WB-A: a claim promised is not ours to pay away)."""
    try:
        from backend.game_logic.diplomacy import _get_live_bargains
        for bargain in _get_live_bargains(world):
            claim = str((bargain.get("claim_term") or {}).get("claim_region") or "")
            if claim == region and str(bargain.get("promiser") or "") in (payer, leader):
                return str(bargain.get("beneficiary") or "")
    except Exception as exc:
        report(exc, "compensation._promised_by_a_bargain: _get_live_bargains")
    return ""


def _design_entry(world, compensated: str, region: str) -> Optional[Dict[str, Any]]:
    """The compensated court's first authored acquire design that names
    `region`, with its deck index — or None."""
    deck = (getattr(world, "agendas", {}) or {}).get(compensated) or []
    for index, entry in enumerate(deck):
        if not isinstance(entry, Mapping) or entry.get("type") != "acquire_regions":
            continue
        if region in [str(r) for r in (entry.get("regions") or [])]:
            return {"index": index, "id": str(entry.get("id") or ""),
                    "title": str(entry.get("title") or entry.get("id") or ""),
                    "regions": [str(r) for r in (entry.get("regions") or [])]}
    return None


def _refuse(code: str, display: str, **extra: Any) -> Dict[str, Any]:
    out = {"ok": False, "form": "", "code": code, "display": display,
           "holder": "", "design": "", "design_title": "", "design_regions": []}
    out.update(extra)
    return out


def compensation_reading(world, *, payer: str, compensated: str, region: str,
                         war_instance: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    """THE rule. {ok, form, code, display, holder, design, design_title,
    design_regions}. Pure read."""
    from backend.display_names import display_nation as _dn
    payer, compensated, region = str(payer or ""), str(compensated or ""), str(region or "")
    region_obj = (getattr(world, "regions", {}) or {}).get(region)
    if not region or region_obj is None:
        return _refuse("compensation_region_unknown", "Name a province to pay the compensation in.")
    if not payer or not compensated or payer == compensated:
        return _refuse("compensation_parties_invalid",
                       "A compensation is paid by one court to another.")
    holder = str(getattr(region_obj, "controller", "") or "")
    if bool(getattr(region_obj, "is_capital", False)):
        return _refuse("compensation_capital",
                       f"{region} is a capital — no court pays a peace in a capital.", holder=holder)
    if compensated in homeland_owners(world, region):
        return _refuse("compensation_is_a_return",
                       f"{region} is {_dn(compensated)}'s own soil — offer it back with a cession; "
                       f"a compensation is paid in another's coin.", holder=holder)
    if holder == compensated:
        return _refuse("compensation_already_held",
                       f"{_dn(compensated)} already holds {region}.", holder=holder)
    sides, leader = _sides(world, war_instance, payer, compensated)
    payer_side, comp_side = sides.get(payer, ""), sides.get(compensated, "")
    if not payer_side or not comp_side or payer_side == comp_side:
        return _refuse("compensation_same_side",
                       f"{_dn(payer)} and {_dn(compensated)} do not stand on opposite sides of this war.",
                       holder=holder)
    holder_side = sides.get(holder, "")
    if holder_side == comp_side:
        return _refuse("compensation_holder_is_theirs",
                       f"{region} is held by {_dn(holder)}, on {_dn(compensated)}'s own side — "
                       f"it is not ours to pay.", holder=holder)
    if holder_side == payer_side:
        if holder != payer:
            return _refuse("compensation_payer_does_not_hold",
                           f"{region} is {_dn(holder)}'s to give — {_dn(holder)} pays it.",
                           holder=holder)
        if leader and leader in homeland_owners(world, region):
            return _refuse("compensation_victors_own_soil",
                           f"{region} is {_dn(leader)}'s own soil — offer it with a cession; "
                           f"a compensation is a third party's province.", holder=holder)
        if not borders_the_court(world, compensated, region):
            return _refuse("compensation_not_on_her_frontier",
                           f"{region} does not border {_dn(compensated)}'s soil — a court is "
                           f"paid where it can hold what it is paid.", holder=holder)
        promised_to = _promised_by_a_bargain(world, region, payer, leader)
        if promised_to:
            return _refuse("compensation_promised_by_bargain",
                           f"{region} is promised to {_dn(promised_to)} by our war bargain — "
                           f"it cannot pay {_dn(compensated)}.", holder=holder)
        return {"ok": True, "form": FORM_PAID, "code": "", "display": "", "holder": holder,
                "design": "", "design_title": "", "design_regions": []}
    # The holder stands outside this war: the pointed form.
    entry = _design_entry(world, compensated, region)
    if entry is None:
        return _refuse("compensation_no_design",
                       f"{_dn(compensated)} has no design on {region} — a compensation points "
                       f"a court only where it already looks.", holder=holder)
    if leader and payer != leader:
        return _refuse("compensation_licence_is_the_leaders",
                       f"Only {_dn(leader)} can license {_dn(compensated)}'s design — the side's "
                       f"leader signs the promise.", holder=holder)
    try:
        from backend.game_logic.instruments import design_suspended, guarantors_of
        if design_suspended(world, compensated, entry["id"]):
            return _refuse("compensation_design_asleep",
                           f"{_dn(compensated)}'s design \"{entry['title']}\" is already bought off.",
                           holder=holder)
        if holder and payer in guarantors_of(world, holder):
            return _refuse("compensation_aim_guaranteed",
                           f"{_dn(payer)} guarantees {_dn(holder)} — she cannot license a design "
                           f"on its soil.", holder=holder)
    except Exception as exc:
        report(exc, "compensation.compensation_reading: instruments reads")
    top = getattr(world, "_top_overlord", None)
    if holder and callable(top) and (top(holder) or holder) in (payer, leader):
        return _refuse("compensation_aim_is_ours",
                       f"{region} is held by {_dn(holder)}, under {_dn(payer)}'s own hand.",
                       holder=holder)
    return {"ok": True, "form": FORM_POINTED, "code": "", "display": "", "holder": holder,
            "design": entry["id"], "design_title": entry["title"],
            "design_regions": list(entry["regions"])}


def clause_reading(world, clause: Mapping[str, Any],
                   war_instance: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    """The rule read on a written clause, with its stamp checked: a clause
    that names a design the board reads as paid (or the reverse) is
    refused — the price was read off the stamp."""
    regions = _clause_regions(clause)
    reading = compensation_reading(
        world, payer=str(clause.get("from") or clause.get("from_nation") or ""),
        compensated=str(clause.get("to") or clause.get("to_nation") or ""),
        region=regions[0] if regions else "", war_instance=war_instance)
    if reading["ok"] and (reading["form"] == FORM_POINTED) != is_pointed(clause):
        return _refuse("compensation_form_mismatch",
                       "The board no longer reads this compensation as it was written — "
                       "strike it and write it again.", holder=reading["holder"])
    return reading


def stamp(world, clause: Dict[str, Any], reading: Mapping[str, Any]) -> Dict[str, Any]:
    """The denormalised fields the world-less consumers read (the price, the
    words): the holder, and for the pointed form the design."""
    clause = dict(clause)
    clause["holder"] = str(reading.get("holder") or "")
    if reading.get("form") == FORM_POINTED:
        clause["design"] = str(reading.get("design") or "")
        clause["design_title"] = str(reading.get("design_title") or "")
    else:
        clause.pop("design", None)
        clause.pop("design_title", None)
    return clause


# ═══════════════════════════════════════════════════════════════════════
# The words
# ═══════════════════════════════════════════════════════════════════════

def compensation_words(clause: Mapping[str, Any]) -> str:
    """'Austria is compensated with Franconia (Bavaria's)' /
    'Austria's designs are pointed east: the Eastern Question (Albania),
    licensed by France'. World-less (reads the stamp)."""
    from backend.display_names import display_nation as _dn
    payer = _dn(str(clause.get("from") or clause.get("from_nation") or ""))
    comp = _dn(str(clause.get("to") or clause.get("to_nation") or ""))
    regions = _clause_regions(clause)
    region = regions[0] if regions else ""
    if is_pointed(clause):
        title = str(clause.get("design_title") or clause.get("design") or "")
        holder = _dn(str(clause.get("holder") or ""))
        return (f"{comp}'s design pointed elsewhere: {title} ({region}"
                + (f", {holder}'s" if holder else "") + f"), licensed by {payer}")
    return f"{comp} compensated with {region} ({payer}'s)"


def compensation_phrase(clause: Mapping[str, Any]) -> str:
    """The words after "is compensated", the court unnamed: 'with Franconia,
    Bavaria's' / '— her design pointed elsewhere: The Eastern Question
    (Albania, Ottoman Empire's), licensed by France'."""
    from backend.display_names import display_nation as _dn
    payer = _dn(str(clause.get("from") or clause.get("from_nation") or ""))
    regions = _clause_regions(clause)
    region = regions[0] if regions else ""
    if is_pointed(clause):
        title = str(clause.get("design_title") or clause.get("design") or "")
        holder = _dn(str(clause.get("holder") or ""))
        return (f"— her design pointed elsewhere: {title} ({region}"
                + (f", {holder}'s" if holder else "") + f"), licensed by {payer}")
    return f"with {region}, {payer}'s"


def short_label(clause: Mapping[str, Any]) -> str:
    """The restage message's noun phrase."""
    regions = _clause_regions(clause)
    region = regions[0] if regions else ""
    if is_pointed(clause):
        return f"the design pointed at {region}"
    return f"the compensation in {region}"


# ═══════════════════════════════════════════════════════════════════════
# The candidates — the guided rows and the AI's letter
# ═══════════════════════════════════════════════════════════════════════

def paid_candidates(world, *, compensated: str, payer_side_members: Iterable[str],
                    war_instance: Optional[Mapping[str, Any]] = None,
                    excluded: Iterable[str] = ()) -> List[Tuple[str, str]]:
    """[(region, payer)] — every province a court of the paying side holds
    that the rule reads as PAID, the compensated court's frontier first
    (adjacent to its 1805 soil), then the richest. Per-court region reads
    only (`get_nation_regions`, Rule 8)."""
    skip = {str(r) for r in excluded or ()}
    home = set((getattr(world, "nation_starting_regions", {}) or {}).get(compensated, []) or [])
    rows = []
    for member in payer_side_members or ():
        member = str(member)
        try:
            held = list(world.get_nation_regions(member) or [])
        except Exception as exc:
            report(exc, "compensation.paid_candidates: get_nation_regions")
            continue
        for region in held:
            region = str(region)
            if region in skip:
                continue
            reading = compensation_reading(world, payer=member, compensated=compensated,
                                           region=region, war_instance=war_instance)
            if not reading["ok"] or reading["form"] != FORM_PAID:
                continue
            obj = world.regions.get(region)
            adjacent = set(getattr(obj, "adjacent_regions", None) or [])
            rows.append((0 if adjacent & home else 1, -int(getattr(obj, "income_value", 0) or 0),
                         region, member))
    rows.sort()
    return [(r[2], r[3]) for r in rows]


def pointed_candidates(world, *, compensated: str, payer: str,
                       war_instance: Optional[Mapping[str, Any]] = None,
                       excluded: Iterable[str] = ()) -> List[Dict[str, Any]]:
    """Every province of the compensated court's own designs that the rule
    reads as POINTED for `payer`, deck order first: [{region, design,
    design_title, holder}]."""
    skip = {str(r) for r in excluded or ()}
    out = []
    for entry in (getattr(world, "agendas", {}) or {}).get(compensated) or []:
        if not isinstance(entry, Mapping) or entry.get("type") != "acquire_regions":
            continue
        for region in entry.get("regions") or []:
            region = str(region)
            if region in skip or any(o["region"] == region for o in out):
                continue
            reading = compensation_reading(world, payer=payer, compensated=compensated,
                                           region=region, war_instance=war_instance)
            if reading["ok"] and reading["form"] == FORM_POINTED:
                out.append({"region": region, "design": reading["design"],
                            "design_title": reading["design_title"], "holder": reading["holder"]})
    return out


def peace_table_road(world, *, payer: str, court: str) -> str:
    """PC-X29 (S14 part 1): the honest answer to "buy off a court we are at
    war with" — the refusal promised "designs are bought off at the peace
    table" while no table road existed. Now it names the road when there is
    one (the pointed form, on the table's offer rows) and says when there is
    none. ONE sentence for the verb and the league row."""
    rows = pointed_candidates(world, compensated=court, payer=payer)
    if rows:
        return (f"at the peace table her design can be pointed elsewhere — "
                f"{rows[0]['design_title']} ({rows[0]['region']})")
    return "a design is bought off in peace, and she looks nowhere a peace could point her"


def letter_compensation_ask(world, *, writer: str, payer: str) -> Optional[Dict[str, Any]]:
    """GR5 — the AI's settlement letter carries what the player's table may.
    A losing court whose desire profile values territory highly asks the
    victor to point its design elsewhere: the first province of its own
    designs the rule reads as POINTED for the victor (its deck order is its
    desire). None when its profile prizes something else, or nothing points.
    Returns the clause in the table's dialect, stamped."""
    from backend.game_logic.diplomatic_templates import NATION_DESIRE_PROFILES
    if str((NATION_DESIRE_PROFILES.get(writer) or {}).get("values_territory") or "") != "high":
        return None
    rows = pointed_candidates(world, compensated=writer, payer=payer)
    if not rows:
        return None
    row = rows[0]
    return {"type": TERRITORY_COMPENSATE, "from": payer, "to": writer, "region": row["region"],
            "design": row["design"], "design_title": row["design_title"], "holder": row["holder"],
            "authored_by": writer}


# ═══════════════════════════════════════════════════════════════════════
# The guided rows — authored from the table's "Offers to <court>" group
# ═══════════════════════════════════════════════════════════════════════

def author_clause(world, *, court: str, region: str, war_instance: Mapping[str, Any],
                  proposer_participants: Iterable[str], proposer_leader: str,
                  promised: Iterable[str] = ()) -> Tuple[Optional[Dict[str, Any]], str, str]:
    """The add verb's arm: (clause, "", "") or (None, code, display). The
    payer is never chosen by the author — it is the court that HOLDS the
    province (paid) or the side's leader (pointed); `region` defaults to the
    first candidate the rows would show."""
    participants = [str(n) for n in proposer_participants or ()]
    promised = {str(r) for r in promised or ()}
    region = str(region or "").strip()
    if not region:
        paid = paid_candidates(world, compensated=court, payer_side_members=participants,
                               war_instance=war_instance, excluded=promised)
        pointed = pointed_candidates(world, compensated=court, payer=proposer_leader,
                                     war_instance=war_instance, excluded=promised)
        region = paid[0][0] if paid else (pointed[0]["region"] if pointed else "")
    if not region:
        return None, "compensation_no_candidate", (
            f"We hold nothing to pay {court} with, Sire, and she looks nowhere a promise could point.")
    if region in promised:
        return None, "region_double_promised", (
            f"{region} is already promised elsewhere in this settlement, Sire.")
    region_obj = (getattr(world, "regions", {}) or {}).get(region)
    holder = str(getattr(region_obj, "controller", "") or "") if region_obj is not None else ""
    payer = holder if holder in participants else proposer_leader
    reading = compensation_reading(world, payer=payer, compensated=court, region=region,
                                   war_instance=war_instance)
    if not reading["ok"]:
        return None, reading["code"], f"{reading['display']} Sire."
    return stamp(world, {"type": TERRITORY_COMPENSATE, "from": payer, "to": court,
                         "region": region}, reading), "", ""


def guided_suggestions(world, *, court: str, war_id: str, draft_key: str,
                       war_instance: Mapping[str, Any], proposer_side_participants: Iterable[str],
                       proposer_leader: str, promised_regions: Iterable[str]) -> List[Dict[str, Any]]:
    """The "Offers to <court>" rows for the compensation clause: a province
    paid (the frontier's first, every candidate in the picker) and a design
    pointed (the court's own designs, deck order). Each row states its price
    beside it (`terms_display`). Valid by construction: every candidate is
    the rule's own reading."""
    from backend.display_names import display_nation as _dn
    from backend.game_logic.instruments import COMPENSATION_TERM_TURNS
    from backend.game_logic.settlement_staging import _guided_suggestion
    from backend.game_logic.settlement_reactions import RELATION_SOLD_OUT_VS_FRANCE
    out: List[Dict[str, Any]] = []
    promised = {str(r) for r in promised_regions or ()}
    paid = paid_candidates(world, compensated=court,
                           payer_side_members=proposer_side_participants,
                           war_instance=war_instance, excluded=promised)
    if paid:
        region, payer = paid[0]
        credit = table_credit({"region": region})
        out.append(_guided_suggestion(
            label=f"Compensate {_dn(court)} with {region} — {_dn(payer)}'s",
            group="offer", clause_type=TERRITORY_COMPENSATE,
            reason_display=(f"Pay her for what she cedes in another's coin, Sire — {region} is "
                            f"{_dn(payer)}'s to give, and a court made whole forgets sooner."),
            court=court, war_id=war_id, draft_key=draft_key, params={"region": region},
            region_options=[r for r, _p in paid],
            terms_display=(f"+{credit} to {_dn(court)}'s answer · {_dn(payer)} gives up {region}"
                           + ("" if payer == proposer_leader else " (her compensation, our article)")),
        ))
    pointed = pointed_candidates(world, compensated=court, payer=proposer_leader,
                                 war_instance=war_instance, excluded=promised)
    if pointed:
        row = pointed[0]
        credit = table_credit({"region": row["region"], "design": row["design"]})
        out.append(_guided_suggestion(
            label=f"Point {_dn(court)} elsewhere — {row['design_title']} ({row['region']})",
            group="offer", clause_type=TERRITORY_COMPENSATE,
            reason_display=(f"Turn her ambition from our frontier, Sire: we license "
                            f"{row['design_title']}, and her other designs sleep "
                            f"{int(COMPENSATION_TERM_TURNS)} turns. {_dn(row['holder'])} will take "
                            f"it ill — and a war on her within the term is a broken bargain."),
            court=court, war_id=war_id, draft_key=draft_key, params={"region": row["region"]},
            region_options=[r["region"] for r in pointed],
            terms_display=(f"+{credit} to {_dn(court)}'s answer · {_dn(row['holder'])} "
                           f"{int(RELATION_SOLD_OUT_VS_FRANCE)} with {_dn(proposer_leader)} · "
                           f"a licence for {int(COMPENSATION_TERM_TURNS)} turns"),
        ))
    return out


# ═══════════════════════════════════════════════════════════════════════
# The memory — a compensated cession is not a partition
# ═══════════════════════════════════════════════════════════════════════

def compensation_offsets(terms: Iterable[Mapping[str, Any]]) -> Dict[str, int]:
    """court -> the compensations it receives in one instrument (either
    dialect, either form). Each offsets ONE ceded homeland province in the
    punitive record and the two Pressburgs' line — never the capital."""
    out: Dict[str, int] = {}
    for term in terms or []:
        if not isinstance(term, Mapping) or term.get("type") != TERRITORY_COMPENSATE:
            continue
        court = str(term.get("to") or term.get("to_nation") or "")
        if court:
            out[court] = out.get(court, 0) + 1
    return out


def net_of_compensation(world, victim: str, provinces: List[str], offset: int) -> List[str]:
    """The cession list with `offset` provinces struck — the last first,
    the capital never (a capital ceded stays punitive whatever is paid)."""
    if offset <= 0:
        return list(provinces)
    capital = world.get_nation_capital(victim) if hasattr(world, "get_nation_capital") else None
    kept = list(provinces)
    for i in range(len(kept) - 1, -1, -1):
        if offset <= 0:
            break
        if kept[i] != capital:
            kept.pop(i)
            offset -= 1
    return kept


# ═══════════════════════════════════════════════════════════════════════
# The apply arm — BOTH ratifiers
# ═══════════════════════════════════════════════════════════════════════

def apply_territory_compensate(world, clause: Mapping[str, Any], *,
                               war_instance: Optional[Mapping[str, Any]] = None
                               ) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """Apply one compensation clause — the table's ratifier and the
    bilateral ratifier both call this (GR5: side-agnostic). Re-reads the
    rule on the board as it stands (a province may have changed hands since
    it was written). Returns (applied_clause, None) or (None, dropped) —
    nothing priced is dropped silently (PC-F52's rule)."""
    from backend.game_logic import instruments as I
    regions = _clause_regions(clause)
    region = regions[0] if regions else ""
    payer = str(clause.get("from") or clause.get("from_nation") or "")
    comp = str(clause.get("to") or clause.get("to_nation") or "")
    reading = compensation_reading(world, payer=payer, compensated=comp, region=region,
                                   war_instance=war_instance)
    if not reading["ok"]:
        return None, {"type": TERRITORY_COMPENSATE, "region": region, "from": payer, "to": comp,
                      "holder": reading.get("holder", ""), "reason": reading["code"],
                      "display": f"{region or 'The compensation'} not carried — {reading['display']}"}
    turn = int(getattr(world, "current_turn", 0) or 0)
    applied = dict(clause)
    applied.pop("regions", None)
    applied.update({"type": TERRITORY_COMPENSATE, "from": payer, "to": comp, "region": region,
                    "form": reading["form"], "holder": reading["holder"]})
    if reading["form"] == FORM_PAID:
        region_obj = world.regions[region]
        region_obj.controller = comp
        region_obj.stability = 50
        from backend.game_logic import game_end as _ge
        _ge.record_province_title(world, region, _ge.TITLE_TREATY, payer, comp)
        if hasattr(world, "invalidate_active_nations_cache"):
            world.invalidate_active_nations_cache()
        from backend.game_logic.coalition import add_threat, reduce_threat
        add_threat(world, 8, "treaty_annex", target=comp)
        reduce_threat(world, 5, "territory_return", target=payer)
        bonds = I.record_peace_compensation(
            world, payer=payer, recipient=comp, design_ids=[""],
            granted={"clause": TERRITORY_COMPENSATE, "form": FORM_PAID, "region": region})
        applied.pop("design", None)
        applied.pop("design_title", None)
    else:
        deck = (getattr(world, "agendas", {}) or {}).get(comp) or []
        entry = _design_entry(world, comp, region) or {}
        ahead = [str(e.get("id") or "") for e in deck[:int(entry.get("index", 0) or 0)]
                 if isinstance(e, Mapping) and e.get("id")
                 and not I.design_suspended(world, comp, str(e.get("id") or ""))]
        bonds = I.record_peace_compensation(
            world, payer=payer, recipient=comp, design_ids=ahead or [""],
            granted={"clause": TERRITORY_COMPENSATE, "form": FORM_POINTED,
                     "pointed_to": reading["design"], "region": region})
        holder = reading["holder"]
        I.grant_directed_sponsorship(
            world, payer=payer, recipient=comp, aim=holder, amount_per_turn=0,
            turns=I.COMPENSATION_TERM_TURNS, kind="sponsorship")
        if holder:
            # The court whose province was promised at a table it never sat
            # at is SOLD OUT — the settlement reactions' own figure (-15).
            from backend.game_logic.settlement_reactions import RELATION_SOLD_OUT_VS_FRANCE
            world.modify_nation_relation(holder, payer, RELATION_SOLD_OUT_VS_FRANCE)
        applied.update({"design": reading["design"], "design_title": reading["design_title"],
                        "suspended_designs": list(ahead)})
    world.log_event({
        "type": "design_bought_off", "payer": payer, "recipient": comp,
        "design_id": str(applied.get("design") or ""), "clause": TERRITORY_COMPENSATE,
        "form": reading["form"], "region": region, "holder": reading["holder"],
        "design_title": str(applied.get("design_title") or ""),
        "granted": dict((bonds[0].get("granted") if bonds else {}) or {}), "turn": turn,
    })
    applied["words"] = compensation_words(applied)
    return applied, None
