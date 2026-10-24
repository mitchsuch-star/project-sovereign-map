"""S14E-4 (S14f part 1, October 24, 2026) — the corps a peace will shelter.

A peace (or a truce) with a court makes its soil neutral to us: the PT-F1
guard's neutral arm then refuses the player's lead a field on it
(`combat_executor.field_on_peace_soil`, DDB-14), so a third court's army still
at war with France and standing on that soil is out of our reach until it
leaves. That is the rule by design — but the peace preview never named the
corps it would shelter (conquest #8: Kutuzov 34k and Buxhowden 22k at
Moravia, the player signed with Austria and learned it from a refusal).

ONE predicate, no second formula: `world_state.sheltering_court` — the very
read the reckless charge uses, drift-pinned to the executor's guard — asked
of the board the treaty WOULD leave (`treaty_assumption`: the pair, and the
clients who follow the lord out, at the treaty's state; the provinces the
terms move at their new holder). Fog: only corps the player can see
(`world.get_visible_enemies`) are named. Display only — nothing here is read
by a decision, the AI's included.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from backend.models.world_state import sheltering_court


def _courts_of(target) -> List[str]:
    """One court, or the courts a settlement covers."""
    if isinstance(target, str):
        return [target] if target else []
    return [str(c) for c in (target or []) if c]


def treaty_assumption(world, nation: str, target, new_state: str = "PEACE",
                      terms=None) -> Dict[str, Dict]:
    """The board a treaty between `nation` and `target` (one court, or every
    court a settlement covers) would leave, in the shape
    `frontier_halt_owner` reads: `states` (each court `nation` would be at
    `new_state` with — the targets and the clients who follow the lord out
    of the war, `diplomacy.client_pairs_that_follow`) and `controllers` (the
    provinces the terms move: a plain cession by its holder goes to the
    receiver; any other soil-moving clause leaves the province's holder
    UNKNOWN, '' — nothing is claimed of it). `terms` is a proposal
    (`{"sweeteners", "demands"}`) or a settlement's clause list."""
    from backend.game_logic.diplomacy import client_pairs_that_follow
    followed = "ARMISTICE" if str(new_state or "").upper().startswith("ARMISTICE") else "PEACE"
    courts = _courts_of(target)
    states = {court: followed for court in courts}
    for court in courts:
        for left, right in client_pairs_that_follow(world, nation, court, followed):
            if left == nation:
                states[right] = followed
            elif right == nation:
                states[left] = followed
    return {"states": states,
            "controllers": _controllers_after(world, nation, courts, terms)}


def _controllers_after(world, nation: str, courts: List[str], terms) -> Dict[str, str]:
    if not terms:
        return {}
    from backend.game_logic.settlement_scoring import cession_shaped_regions
    from backend.game_logic.treaty import treaty_clauses_of
    if isinstance(terms, dict):
        proposal = {"sweeteners": terms.get("sweeteners") or [],
                    "demands": terms.get("demands") or []}
        clauses = treaty_clauses_of(proposal, nation, courts[0] if courts else "")
    else:
        clauses = [dict(c) for c in terms if isinstance(c, dict)]
    moved: Dict[str, str] = {}
    for clause in clauses:
        receiver = clause.get("to")
        for name in cession_shaped_regions(clause):
            region = world.get_region(name)
            holder = getattr(region, "controller", None) if region else None
            plain = (clause.get("type") == "territory_cede"
                     and isinstance(receiver, str) and receiver
                     and holder == clause.get("from"))
            moved[name] = receiver if plain else ""
    return moved


def sheltered_corps(world, nation: str, target, new_state: str = "PEACE",
                    terms=None) -> List[Dict[str, Any]]:
    """The enemy corps `nation` can SEE that a treaty with `target` (one
    court, or every court a settlement covers) would newly shelter, grouped
    by the province they stand on: `[{region, court, marshals}]`, in
    province-name order, `marshals` by name.

    A corps counts when its own war goes on (it is not of a court the treaty
    makes peace with), the player's lead could take the field against it now,
    and could not after — it stands on the soil of a court the treaty would
    put at peace with us, or on a province the terms hand to a court at peace
    with us (`sheltering_court`, the guard's rule, asked of both boards)."""
    assume = treaty_assumption(world, nation, target, new_state, terms)
    ends = set(assume["states"])
    grouped: Dict[str, Dict[str, Any]] = {}
    for enemy in world.get_visible_enemies(nation):
        if enemy.nation in ends or getattr(enemy, "captured_by", ""):
            continue
        if sheltering_court(world, nation, enemy) is not None:
            continue                       # already beyond reach — not this treaty's doing
        court = sheltering_court(world, nation, enemy, assume)
        if court is None:
            continue
        row = grouped.setdefault(enemy.location, {
            "region": enemy.location, "court": court, "marshals": []})
        row["marshals"].append(enemy)
    rows = [grouped[name] for name in sorted(grouped)]
    for row in rows:
        row["marshals"].sort(key=lambda m: m.name)
    return rows


def _possessive(name: str) -> str:
    return f"{name}'" if name.endswith("s") else f"{name}'s"


def _join(parts: List[str]) -> str:
    return (", ".join(parts[:-1]) + " and " + parts[-1]) if len(parts) > 1 else (parts[0] if parts else "")


def sanctuary_line(world, row: Dict[str, Any], new_state: str = "PEACE") -> str:
    """"Kutuzov (Russia) stands at Moravia, Austria's soil — after this peace
    no corps of ours may take the field against him there." — one province,
    its corps joined; "truce" for a truce."""
    from backend.display_names import humanize_entity_name, with_definite_article
    from backend.game_logic.formations import formed_display_name
    treaty = "truce" if str(new_state or "").upper().startswith("ARMISTICE") else "peace"
    who = [f"{humanize_entity_name(m.name)} ({formed_display_name(world, m.nation)})"
           for m in row["marshals"]]
    soil = _possessive(with_definite_article(formed_display_name(world, row["court"])))
    many = len(who) > 1
    return (f"{_join(who)} {'stand' if many else 'stands'} at {row['region']}, {soil} soil — "
            f"after this {treaty} no corps of ours may take the field against "
            f"{'them' if many else 'him'} there.")


def sanctuary_warnings(world, nation: str, target, new_state: str = "PEACE",
                       terms=None) -> List[Dict[str, Any]]:
    """The preview's `sanctuary` rows, one per province, in the fallout
    warnings' own shape (`warning_type`, `severity`, `display`)."""
    out: List[Dict[str, Any]] = []
    for row in sheltered_corps(world, nation, target, new_state, terms):
        out.append({
            "warning_type": "sanctuary",
            "severity": "MAJOR",
            "display": sanctuary_line(world, row, new_state),
            "court": row["court"],
            "region": row["region"],
            "marshals": [m.name for m in row["marshals"]],
        })
    return out


def sanctuary_note(world, nation: str, target, new_state: str = "PEACE",
                   terms=None) -> str:
    """The rows' sentences as one string — '' when the treaty shelters no one
    we can see (the table's per-court chip appends it to its own words)."""
    return " ".join(w["display"] for w in
                    sanctuary_warnings(world, nation, target, new_state, terms))


def settlement_review_rows(world, covered, terms) -> List[Dict[str, Any]]:
    """The settlement table's review rows (`build_settlement_review`'s
    warnings dialect): the corps the settlement as drafted would shelter —
    the courts it covers go to peace with us, the others fight on, and a
    fought-on court's army standing on a covered court's soil is out of the
    lead's reach. Salience 80 keeps the row inline under the compact cap."""
    nation = getattr(world, "player_nation", "")
    if not nation or not covered:
        return []
    return [{
        "code": "sanctuary",
        "code_display": "Enemy corps sheltered",
        "detail": w["display"],
        "severity": "WARNING",
        "salience": 80,
    } for w in sanctuary_warnings(world, nation, covered, "PEACE", terms)]
