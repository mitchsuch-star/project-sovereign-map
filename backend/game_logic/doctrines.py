"""SR-7d "The Doctrines" (Score Finish Step 3's eighth slice; `docs/DOCTRINES_SPEC.md`).

A doctrine is a strength and a flaw per great power — how its army fought in
1805 — authored per court under the scenario key `doctrines` (and the
geography list `poor_country`), copied into ONE serialized world field
(`world.doctrines`, §9) and read at the seams the spec names (§3). Nothing
here is a new decision rule: every clause is a number on a mechanic the AI
already reads (§5). The flaw is removed only by its cure law, while the
court's Staff is in force (RV-15); whether a flaw is cured is DERIVED from the
laws at every read, never stored.

Levers (UPPER_CASE; lever down = the shipped behaviour byte for byte):
  DOCTRINES_ACTIVE      the master — down, no court carries a doctrine
  <COURT>_DOCTRINE      per court (the flip arms of the one series re-record)
  THE_CURES_HEAL        down, a cure law in force removes nothing

The rules of the house (§1): a doctrine is the army's, never the man's
(RV-2) — no clause overrides a marshal's own character; the court's flaw
never costs the man trust (RV-16); the recruit clauses price the draft, never
the substitute market (RV-17); the combat clauses ride a standing DERIVED term
on the marshal (`_doctrine_terms`, RV-6) with ONE writer
(`refresh_doctrine_terms`) and ONE setter for a marshal's court
(`set_marshal_nation`).
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

# ── Levers ────────────────────────────────────────────────────────────────────
DOCTRINES_ACTIVE = True
FRANCE_DOCTRINE = True
BRITAIN_DOCTRINE = True
RUSSIA_DOCTRINE = True
AUSTRIA_DOCTRINE = True
PRUSSIA_DOCTRINE = True
THE_CURES_HEAL = True

# ── The closed set of clause types (§3) and their clamp bands (§1) ─────────────
CLAUSE_TYPES = ("arrival_bar", "attack", "defense", "recruit_price",
                "defeat_morale", "supply")
CLAUSE_BANDS = {
    "arrival_bar": ("int", -20, 20),        # the bar, moved (RV-1)
    "attack": ("float", 0.0, 0.25),         # +N on the attack modifier
    "defense": ("float", 0.0, 0.25),        # +N on the defence modifier
    "recruit_price": ("float", 0.5, 1.5),   # ×m on a DRAFT levy (RV-17)
    "defeat_morale": ("float", 0.25, 2.0),  # ×m on the lopsided-defeat penalty
    "supply": ("float", 0.5, 1.0),          # ×m outside the homeland in poor country
}
STRIPPED_BAND = (0.1, 0.5)                  # the supply clause's `stripped_at`
WAR_DAMAGE_RECOVERY_TICK = 0.02             # `process_war_damage_recovery`'s own tick
GREAT_POWERS = ("France", "Britain", "Russia", "Austria", "Prussia")

# RV-6: the standing derived term every marshal carries, and its neutral value.
NEUTRAL_TERMS: Dict[str, object] = {
    "attack": 1.0, "attack_name": "",
    "defense": 1.0, "defense_name": "",
    "defeat_morale": 1.0, "defeat_morale_name": "",
}


# ════════════════════════════ reading the store ═══════════════════════════════

def store(world) -> Dict:
    return getattr(world, "doctrines", None) or {}


def table(world) -> Dict[str, Dict]:
    courts = store(world).get("courts")
    return courts if isinstance(courts, dict) else {}


def poor_country(world) -> List[str]:
    rows = store(world).get("poor_country")
    return [str(r) for r in rows] if isinstance(rows, list) else []


def court_lever(nation: str) -> bool:
    return bool(globals().get(f"{str(nation or '').upper()}_DOCTRINE", True))


def doctrine_of(world, nation: str) -> Optional[Dict]:
    """The court's authored doctrine, or None (lever down / no entry)."""
    if not DOCTRINES_ACTIVE or not nation or not court_lever(nation):
        return None
    row = table(world).get(nation)
    return row if isinstance(row, dict) else None


def clause(world, nation: str, role: str) -> Optional[Dict]:
    row = doctrine_of(world, nation)
    if row is None:
        return None
    c = row.get(role)
    return c if isinstance(c, dict) and c.get("type") in CLAUSE_TYPES else None


def clause_name(c: Optional[Dict]) -> str:
    return str((c or {}).get("name") or "")


# ════════════════════════════ the cure (RV-15, D-R4) ═════════════════════════

def cure_law(world, nation: str) -> Optional[Dict]:
    """The law row whose `cures` clause names this court's flaw, from the
    court's own deck (whether or not in force)."""
    row = doctrine_of(world, nation)
    if row is None:
        return None
    from backend.game_logic.reforms import deck
    flaw = clause_name(clause(world, nation, "flaw"))
    wanted = str(row.get("cured_by") or "")
    for law in deck(world, nation):
        if not isinstance(law, dict):
            continue
        if wanted and law.get("id") != wanted:
            continue
        for c in law.get("effects") or []:
            if isinstance(c, dict) and c.get("type") == "cures" and (
                    not flaw or str(c.get("flaw") or "") == flaw):
                return law
    return None


def staff_law(world, nation: str) -> Optional[Dict]:
    from backend.game_logic.reforms import deck, is_staff
    for law in deck(world, nation):
        if isinstance(law, dict) and is_staff(law):
            return law
    return None


def cure_status(world, nation: str) -> Dict:
    """{cured, since, law, staff, needs} — derived from the laws at every
    read (§9): the cure law in force AND the court's Staff in force (RV-15).
    `since` is the later of the two enactment turns."""
    out = {"cured": False, "since": None, "law": "", "staff": "", "needs": ""}
    if doctrine_of(world, nation) is None:
        return out
    from backend.game_logic.reforms import display_name, is_in_force
    law = cure_law(world, nation)
    staff = staff_law(world, nation)
    out["law"] = display_name(law) if law else ""
    out["staff"] = display_name(staff) if staff else ""
    if not THE_CURES_HEAL or law is None or staff is None:
        out["needs"] = "no cure is authored" if law is None else ""
        return out
    law_up = is_in_force(law)
    staff_up = is_in_force(staff)
    if law_up and staff_up:
        out["cured"] = True
        out["since"] = max(int(law.get("enacted_turn", 0) or 0),
                           int(staff.get("enacted_turn", 0) or 0))
        return out
    if law is staff:
        out["needs"] = f"{out['law']} enacted"
    elif law_up and not staff_up:
        out["needs"] = f"{out['staff']} in force (the cure needs the institution that carries it)"
    elif staff_up and not law_up:
        out["needs"] = f"{out['law']} enacted"
    else:
        out["needs"] = f"{out['law']} enacted, with {out['staff']} in force"
    return out


def flaw_cured(world, nation: str) -> bool:
    return bool(cure_status(world, nation)["cured"])


def active_clause(world, nation: str, ctype: str) -> Optional[Tuple[str, Dict]]:
    """(role, clause) of type `ctype` the court carries TODAY — a cured flaw
    is not carried."""
    for role in ("strength", "flaw"):
        c = clause(world, nation, role)
        if c is None or c.get("type") != ctype:
            continue
        if role == "flaw" and flaw_cured(world, nation):
            return None
        return role, c
    return None


# ════════════════════════════ RV-6: the standing term ═════════════════════════

def derive_terms(world, nation: str) -> Dict[str, object]:
    """The combat clauses a marshal of `nation` carries, cure applied."""
    terms = dict(NEUTRAL_TERMS)
    for ctype, key in (("attack", "attack"), ("defense", "defense"),
                       ("defeat_morale", "defeat_morale")):
        hit = active_clause(world, nation, ctype)
        if hit is None:
            continue
        _role, c = hit
        value = float(c.get("value", 0.0) or 0.0)
        terms[key] = (1.0 + value) if ctype in ("attack", "defense") else value
        terms[f"{key}_name"] = clause_name(c)
    return terms


def refresh_doctrine_terms(world, marshals=None) -> int:
    """THE one writer of `Marshal._doctrine_terms` (RV-6). Returns the
    number of marshals refreshed. A world with no doctrine store leaves every
    marshal neutral (a bare marshal reads neutral by construction)."""
    cache: Dict[str, Dict[str, object]] = {}
    rows = list(marshals) if marshals is not None else list(
        (getattr(world, "marshals", None) or {}).values())
    for m in rows:
        nation = str(getattr(m, "nation", "") or "")
        if nation not in cache:
            cache[nation] = derive_terms(world, nation)
        m._doctrine_terms = dict(cache[nation])
    return len(rows)


def set_marshal_nation(world, marshal, nation: str) -> None:
    """THE one setter for a marshal's court (§3): every change of
    `marshal.nation` goes through here so the standing term follows the
    flag he fights under. An AST census forbids a bare `.nation =` write
    anywhere else in the backend."""
    marshal.nation = nation
    marshal._doctrine_terms = derive_terms(world, str(nation or ""))


def terms_of(marshal) -> Dict[str, object]:
    t = getattr(marshal, "_doctrine_terms", None)
    return t if isinstance(t, dict) else dict(NEUTRAL_TERMS)


# ════════════════════════════ the arrival bar (RV-1, RV-2) ════════════════════

def character_keeps_him_away(reinforcer, primary) -> bool:
    """RV-2: the three causes of a man's own that no strength offsets — an
    ability that keeps him away, a live grievance against the lead, a
    hostile pair. The resolver already names all three."""
    ability = ""
    if hasattr(reinforcer, "ability") and isinstance(reinforcer.ability, dict):
        ability = str(reinforcer.ability.get("name") or "")
    if ability == "Eyes on a Crown":
        return True
    if getattr(reinforcer, "jealous_of", None) == getattr(primary, "name", None):
        return True
    try:
        if reinforcer.get_relationship(primary.name) <= -2:
            return True
    except Exception:
        pass
    return False


def arrival_bar_shift(world, reinforcer, primary) -> Tuple[int, str]:
    """(shift on the arrival BAR, the clause's name) for this reinforcer —
    a negative shift is a strength (the corps system), exempt where the
    man's own character keeps him away (RV-2); a positive shift is the
    flaw (the Hofkriegsrat, slow to concentrate) and is the army's."""
    nation = str(getattr(reinforcer, "nation", "") or "")
    hit = active_clause(world, nation, "arrival_bar")
    if hit is None:
        return 0, ""
    _role, c = hit
    shift = int(c.get("value", 0) or 0)
    if shift < 0 and character_keeps_him_away(reinforcer, primary):
        return 0, ""
    return shift, clause_name(c)


# ════════════════════════════ the recruit price (RV-17) ═══════════════════════

def recruit_price_term(world, nation: str) -> Optional[Tuple[str, float]]:
    """(clause name, ×multiplier) on a DRAFT levy of `nation`, or None."""
    hit = active_clause(world, nation, "recruit_price")
    if hit is None:
        return None
    _role, c = hit
    return clause_name(c), float(c.get("value", 1.0) or 1.0)


# ════════════════════════════ living off the land (RV-5) ══════════════════════

def _homeland(world, nation: str) -> set:
    return set((getattr(world, "nation_starting_regions", None) or {}).get(nation, []) or [])


def forward_war_damage(region, forecast: bool = True, extra_damage: float = 0.0) -> float:
    """The war damage the NEXT attrition pass will read (§3 "stripped is
    read forward"): `advance_turn` runs the recovery tick before the pass,
    so a forecast reads today's damage less one tick (plus the battle a
    muster previews there); the bill (`forecast=False`) reads the value as
    it stands, which is already post-recovery."""
    damage = float(getattr(region, "war_damage", 0.0) or 0.0)
    if forecast:
        damage = max(0.0, damage - WAR_DAMAGE_RECOVERY_TICK)
    return min(0.5, damage + float(extra_damage or 0.0))


def supply_ground(world, nation: str, region, forecast: bool = True,
                  extra_damage: float = 0.0) -> Optional[Dict]:
    """Where the flaw CAN bite for `nation` on `region`: outside the court's
    1805 homeland and not on an ally's or vassal's soil (RV-5). Returns
    {clause, poor, stripped, damage, applies} or None when the court carries
    no supply clause today (cured, lever down, no entry)."""
    hit = active_clause(world, nation, "supply")
    if hit is None or region is None:
        return None
    _role, c = hit
    name = getattr(region, "name", "")
    if name in _homeland(world, nation):
        return None
    controller = getattr(region, "controller", None)
    if controller and controller != nation:
        try:
            if world.get_diplomatic_state(nation, controller) in world.ALLY_SUPPLY_STATES:
                return None
        except Exception:
            pass
    stripped_at = float(c.get("stripped_at", 0.25) or 0.25)
    damage = forward_war_damage(region, forecast, extra_damage)
    poor = name in set(poor_country(world))
    stripped = damage >= stripped_at
    return {"clause": c, "name": clause_name(c), "factor": float(c.get("value", 1.0) or 1.0),
            "poor": poor, "stripped": stripped, "damage": damage,
            "stripped_at": stripped_at, "applies": bool(poor or stripped)}


def supply_factor(world, nation: str, region, forecast: bool = True,
                  extra_damage: float = 0.0) -> Tuple[float, str]:
    """(×factor on the supply multiplier, the clause's name) — 1.0 and ""
    when the flaw does not bite here."""
    ground = supply_ground(world, nation, region, forecast, extra_damage)
    if not ground or not ground["applies"]:
        return 1.0, ""
    return ground["factor"], ground["name"]


def supply_mark(world, nation: str, region, econ_visible: bool) -> Optional[Dict]:
    """RV-13: the map's mark on a province where the flaw could bite —
    {poor, line}. The poor-country mark is geography and always shows; the
    stripped mark obeys fog (`econ_visible`). None where no mark applies."""
    ground = supply_ground(world, nation, region, forecast=True)
    if not ground:
        return None
    pct = int(round(ground["factor"] * 100))
    at = int(round(ground["stripped_at"] * 100))
    court = "French" if nation == "France" else f"{nation}'s"
    if ground["poor"]:
        return {"poor": True,
                "line": f"Poor country — a {court} army here draws {pct}% (living off the land)"}
    if not econ_visible:
        return {"poor": False, "line": "Stripped? unknown — scout it"}
    if ground["stripped"]:
        now = int(round(float(getattr(region, "war_damage", 0.0) or 0.0) * 100))
        return {"poor": False,
                "line": (f"Stripped by war ({now}%) — poor country for a {court} army "
                         f"until it recovers below {at}%")}
    return None


def corps_drawing_now(world, nation: str) -> int:
    """How many of the court's corps draw the flaw's share today (the LAWS
    tab's live "would lift" line, read from the SAME predicate)."""
    n = 0
    for m in (getattr(world, "marshals", None) or {}).values():
        if getattr(m, "nation", None) != nation or int(getattr(m, "strength", 0) or 0) <= 0:
            continue
        region = world.get_region(getattr(m, "location", ""))
        factor, _name = supply_factor(world, nation, region, forecast=True)
        if factor < 1.0:
            n += 1
    return n


# ════════════════════════════ the surfaces ════════════════════════════════════

def _pct(value: float) -> str:
    return f"{int(round(value * 100)):d}%"


def clause_line(c: Optional[Dict]) -> str:
    """One clause in numbers — the applied number, never a raw key."""
    if not c:
        return ""
    ctype = c.get("type")
    v = c.get("value", 0)
    if ctype == "arrival_bar":
        n = int(v or 0)
        return (f"a corps within a march comes to the guns more surely — its arrival "
                f"bar is {abs(n)} lower" if n < 0 else
                f"its corps gather slowly — the arrival bar is {n} higher")
    if ctype == "attack":
        return f"+{_pct(float(v))} on the attack when its lead attacks, and on every reinforcer's weight"
    if ctype == "defense":
        return f"+{_pct(float(v))} on the defence when its lead defends"
    if ctype == "recruit_price":
        f = float(v)
        pct = int(round((f - 1.0) * 100))
        return (f"recruits drawn from the draft cost {abs(pct)}% "
                f"{'less' if pct < 0 else 'more'} (×{f:g})")
    if ctype == "defeat_morale":
        f = float(v)
        if f < 1.0:
            return f"a beaten army loses {_pct(f)} of the morale a lopsided defeat costs"
        return f"a lopsided defeat costs ×{f:g} morale"
    if ctype == "supply":
        f = float(v)
        at = float(c.get("stripped_at", 0.25) or 0.25)
        return (f"outside the homeland, in poor or stripped country (war damage "
                f"≥ {_pct(at)}), the army draws {_pct(f)} of its supply")
    return ""


def cure_line(world, nation: str) -> str:
    """The flaw's status in words: "cured since turn 23" or
    "uncured — the Articles of War would end it once the General Staff stands"."""
    status = cure_status(world, nation)
    if status["cured"]:
        return f"cured since turn {int(status['since'])}"
    if not status["law"]:
        return "uncured — no law cures it"
    law = status["law"]
    staff = status["staff"]
    if staff and law.lower() != staff.lower():
        return f"uncured — {law} would end it once {staff} stands"
    return f"uncured — {law} would end it"


def doctrine_payload(world, nation: str) -> Optional[Dict]:
    """The court's doctrine for a screen: name, says, strength, flaw (with
    the cure's status) — None when the court carries none."""
    row = doctrine_of(world, nation)
    if row is None:
        return None
    s = clause(world, nation, "strength")
    f = clause(world, nation, "flaw")
    status = cure_status(world, nation)
    return {
        "nation": nation,
        "name": str(row.get("name") or ""),
        "says": str(row.get("says") or ""),
        "strength": {"name": clause_name(s), "line": clause_line(s)},
        "flaw": {"name": clause_name(f), "line": clause_line(f),
                 "cured": bool(status["cured"]),
                 "since": status["since"],
                 "status_line": cure_line(world, nation)},
        "cure": {"law": status["law"], "staff": status["staff"],
                 "needs": status["needs"]},
    }


def doctrine_card_line(world, nation: str) -> Optional[str]:
    """ONE line for the Diplomatic Ledger's nation card (§4a: at most two
    lines per court with the laws line)."""
    p = doctrine_payload(world, nation)
    if p is None:
        return None
    head = p["name"]
    if p["strength"]["name"].lower() != p["name"].lower():
        head += f" — {p['strength']['name']}"
    return f"{head}; flaw: {p['flaw']['name']} ({p['flaw']['status_line']})"


def doctrine_answer(world, nation: str, own: bool, weaknesses: bool = False) -> str:
    """The desk's answer to "what is our doctrine?" / "what is Austria's
    doctrine?" / "what are Austria's weaknesses?"."""
    from backend.display_names import display_nation
    p = doctrine_payload(world, nation)
    court = "Our army" if own else display_nation(nation)
    if p is None:
        return (f"{court} fights under no doctrine of its own, Sire — the common "
                f"rules of war apply." if not own else
                "We fight under no doctrine of our own, Sire — the common rules of war apply.")
    if weaknesses and not own:
        return (f"{court}'s weakness is {p['flaw']['name']}, Sire: "
                f"{p['flaw']['line']} — {p['flaw']['status_line']}.")
    lines = [f"{court} fights by {p['name']}, Sire. \"{p['says']}\"",
             f"Its strength, {p['strength']['name']}: {p['strength']['line']}.",
             f"Its flaw, {p['flaw']['name']}: {p['flaw']['line']} — {p['flaw']['status_line']}."]
    return " ".join(lines)


def boot_line(world, nation: str) -> Optional[str]:
    """The turn-1 briefing's one line (§4a discoverability)."""
    p = doctrine_payload(world, nation)
    if p is None:
        return None
    return (f"Our doctrine: {p['name']} — {p['says']} "
            f"The Generals screen (G) shows its strength and its flaw.")


def arrival_copy(row: Dict, lead_name: str) -> str:
    """RV-16: a doctrine-decided arrival or no-show, named."""
    name = str(row.get("doctrine") or "")
    who = str(row.get("marshal") or "")
    if not name or not who:
        return ""
    from backend.display_names import humanize_entity_name
    who = humanize_entity_name(who)
    if row.get("arrived") and row.get("doctrine_arrived"):
        return f"{name} brought {who} in."
    if row.get("reason") == "doctrine_delayed":
        return f"{name}'s orders reached {who} too late."
    return ""


def morale_line(record: Dict) -> str:
    """RV-7: the battle report's morale line for a scaled lopsided defeat —
    "the Russians would not break: Stubborn halved the rout (−21 morale,
    not −42)"; "the Prussian line broke: Brittle deepened the rout (−63
    morale, not −42)"."""
    if not record:
        return ""
    name = str(record.get("name") or "")
    base = int(record.get("base", 0) or 0)
    applied = int(record.get("applied", 0) or 0)
    nation = str(record.get("nation") or "")
    if not name or base <= 0 or applied == base:
        return ""
    from backend.display_names import nation_adjective
    adj = nation_adjective(nation) if nation else "beaten"
    if applied < base:
        return (f"the {adj} army would not break: {name} softened the rout "
                f"(−{applied} morale, not −{base})")
    return (f"the {adj} line broke: {name} deepened the rout "
            f"(−{applied} morale, not −{base})")


def scaled_defeat_penalty(marshal, base: int) -> Tuple[int, Optional[Dict]]:
    """The lopsided-defeat penalty `base` scaled by the loser's doctrine term
    — applied AFTER the penalty's own cap (§2: a Prussian rout's extra loss
    can reach 82). Returns (applied, record-or-None)."""
    base = int(base or 0)
    if base <= 0:
        return 0, None
    t = terms_of(marshal)
    factor = float(t.get("defeat_morale", 1.0) or 1.0)
    if factor == 1.0:
        return base, None
    applied = int(round(base * factor))
    return applied, {"marshal": getattr(marshal, "name", ""),
                     "nation": str(getattr(marshal, "nation", "") or ""),
                     "name": str(t.get("defeat_morale_name") or ""),
                     "base": base, "applied": applied}


def law_cure_line(world, nation: str, row: Dict) -> str:
    """The LAWS tab's cure line for a law carrying a `cures` clause (§4):
    what it cures, what it would lift THIS turn (the supply flaw's live
    count, read from the same predicate), and the Staff it needs."""
    cures = [c for c in (row.get("effects") or [])
             if isinstance(c, dict) and c.get("type") == "cures"]
    if not cures:
        return ""
    flaw = str(cures[0].get("flaw") or "")
    status = cure_status(world, nation)
    if status["cured"]:
        return f"Cures {flaw} — cured since turn {int(status['since'])}."
    from backend.game_logic.reforms import is_in_force, is_staff
    parts = [f"Cures {flaw}"]
    f = clause(world, nation, "flaw")
    if f is not None and f.get("type") == "supply":
        n = corps_drawing_now(world, nation)
        pct = int(round(float(f.get("value", 1.0) or 1.0) * 100))
        parts.append(f"{n} corps drawing {pct}% now" if n != 1 else f"1 corps drawing {pct}% now")
    staff = staff_law(world, nation)
    if staff is not None and not is_staff(row):
        from backend.game_logic.reforms import display_name
        name = display_name(staff)
        parts.append(f"needs {name} in force" if not is_in_force(staff)
                     else f"{name} stands — in force at once")
    return " — ".join(parts[:1] + [" ; ".join(parts[1:])]) if len(parts) > 1 else parts[0]


def cure_beat_vars(world, nation: str) -> Dict[str, str]:
    """Template variables for the cure beats (§4 "the catch-up is announced")."""
    from backend.display_names import display_nation
    p = doctrine_payload(world, nation) or {}
    status = cure_status(world, nation)
    return {"nation": display_nation(nation), "law": status.get("law") or "",
            "staff": status.get("staff") or "",
            "flaw": (p.get("flaw") or {}).get("name") or "its flaw",
            "strength": (p.get("strength") or {}).get("name") or ""}


# ════════════════════════════ scenario / save ═════════════════════════════════

def store_from_data(data: Dict) -> Dict:
    """ONE shape for the scenario and the save (§9): a scenario carries
    `doctrines: {court: row}` + `poor_country: [...]`; a save carries
    `doctrines: {courts: {...}, poor_country: [...]}`. Comment keys are
    dropped."""
    import copy
    block = data.get("doctrines")
    if not isinstance(block, dict):
        return {}
    if "courts" in block and isinstance(block.get("courts"), dict):
        courts = block.get("courts") or {}
        poor = block.get("poor_country") or []
    else:
        courts = block
        poor = data.get("poor_country") or []
    out_courts = {str(k): copy.deepcopy(dict(v)) for k, v in courts.items()
                  if not str(k).startswith("_") and isinstance(v, dict)}
    if not out_courts:
        return {}
    return {"courts": out_courts,
            "poor_country": [str(r) for r in poor if isinstance(r, str)]}
