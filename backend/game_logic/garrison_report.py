"""SR-4a "The field's price" (Score Mandate Chunk 4 — AAR-4 + AAR-24): what a
garrison IS and what storming it costs, said in ONE place.

Measured at `POST /command` on the shipped 1805 boot before a line changed:
`Ney, scout Vienna` read "Controlled by Austria. Terrain: Plains. No enemy
forces detected." over a 25,000-man capital garrison (AAR-4) — while the map,
the moment the scout landed, showed Vienna at FULL with its 25,000; and
`Ney, attack Vienna` with Murat and Soult beside him stormed the works alone
with no word that they would not join and no word that the garrison regrows
2,000 a turn (AAR-24).

The numbers are the resolver's and the regen loop's own
(`CombatExecutor._resolve_garrison_combat`, `WorldState.capital_garrison_regen`,
`movement_executor.MARCH_HALTS_AT_GARRISON`); this module only SAYS them.
Display only — the enemy AI reads none of it (GR5: it never scouts, and the
assault line is the player's).
"""
from typing import Optional, Tuple

from backend.models.region import TERRAIN_DEFENSE_BONUS

# Levers: False reproduces the pre-slice surfaces byte for byte.
THE_SCOUT_NAMES_THE_GARRISON = True
THE_DESK_READS_THE_GARRISON_FOG = True


def works_bonus(region) -> float:
    """The fortification building's defense bonus, or 0.0 (a damaged work
    does not count — `has_building` reads functional buildings only)."""
    from backend.commands.objection_v2 import REGION_FORTIFICATION_DEFENSE_BONUS
    if region is None or not region.has_building("fortification"):
        return 0.0
    return REGION_FORTIFICATION_DEFENSE_BONUS


def garrison_effective(region, strength: Optional[int] = None) -> int:
    """The garrison behind its ground and its works — the ONE formula
    `_resolve_garrison_combat` fights with (int, as the resolver takes it)."""
    s = int(region.garrison_strength if strength is None else strength)
    terrain = TERRAIN_DEFENSE_BONUS.get(getattr(region, "terrain", None), 0.0)
    return int(s * (1.0 + terrain) * (1.0 + works_bonus(region)))


def garrison_view(world, region_name: str, viewer: str) -> Tuple[Optional[str], object]:
    """The ONE fog rule for a garrison — the map summary's, pinned against it
    (`get_filtered_game_state_summary`): our own soil or a FULL read gives the
    exact strength, ("exact", n); PARTIAL / STALE gives only that one stands
    and its band, ("band", "large force"); anything else says nothing,
    (None, None). A province with no garrison reads (None, 0). `viewer` is the
    player (the intel store is his)."""
    from backend.models.intel import FULL, PARTIAL, STALE, get_strength_band
    region = world.get_region(region_name)
    if region is None:
        return None, None
    strength = int(getattr(region, "garrison_strength", 0) or 0)
    if region.controller == viewer:
        return ("exact", strength) if strength > 0 else (None, 0)
    visibility = world.get_region_intel(region_name).visibility
    if visibility == FULL:
        return ("exact", strength) if strength > 0 else (None, 0)
    if visibility in (PARTIAL, STALE):
        return ("band", get_strength_band(strength)) if strength > 0 else (None, 0)
    return None, None


def describe_garrison(world, region, viewer: str) -> str:
    """One sentence for the garrison of `region` on a FULL read (a targeted
    scout): who holds it, whether it must be assaulted, whether it regrows,
    and its works. '' when no garrison stands."""
    strength = int(getattr(region, "garrison_strength", 0) or 0)
    if strength <= 0:
        return ""
    from backend.commands.movement_executor import MARCH_HALTS_AT_GARRISON
    from backend.game_logic.formations import formed_display_name
    from backend.models.world_state import CAPITAL_GARRISON_REGEN_PER_TURN
    works = works_bonus(region)
    works_clause = (f"; its works add +{int(round(works * 100))}% to the defense"
                    if works > 0 else "")
    holder = region.controller
    if holder == viewer:
        return f"Our garrison: {strength:,}{works_clause}."
    whose = formed_display_name(world, holder) if holder else "Unknown"
    if not (holder and world.is_at_war(viewer, holder)):
        return f"Garrison: {strength:,} ({whose}'s){works_clause}."
    if getattr(region, "garrison_detachment", False):
        kind = "a detachment that fights to the last man — it must be assaulted"
    elif strength >= MARCH_HALTS_AT_GARRISON:
        kind = "it must be assaulted — a march halts before it"
        if getattr(region, "is_capital", False):
            cap = world.get_capital_garrison_target(holder)
            kind += (f"; a capital's garrison, it regrows "
                     f"{CAPITAL_GARRISON_REGEN_PER_TURN:,} a turn up to {cap:,}")
    else:
        kind = (f"too few to hold (below {MARCH_HALTS_AT_GARRISON:,}) — it gives "
                f"way to the first corps that marches in")
    return f"Garrison: {strength:,} — {kind}{works_clause}."


def garrison_scan_clause(world, region_name: str, viewer: str) -> str:
    """The adjacent scan's per-province garrison note (the scan grants
    PARTIAL: a band, never a figure, unless the cell is ours or already FULL)."""
    form, value = garrison_view(world, region_name, viewer)
    region = world.get_region(region_name)
    if form == "exact":
        return (f", our garrison {int(value):,}" if region.controller == viewer
                else f", garrison {int(value):,}")
    if form == "band":
        return f", garrison: {value}"
    return ""


def assault_muster_line(world, marshal, region, attacker_effective: int,
                        garrison_effective_now: int, coordination: float,
                        garrison_shown: Optional[str] = None) -> str:
    """AAR-24: the one-line muster an assault gets — the resolver's OWN terms
    (shown = applied): he goes in alone at `attacker_effective`, his corps
    beside him lend their coordination share but no men, and the garrison
    fights at `garrison_effective_now` until it breaks below the collapse
    line (a detachment fights to the last man)."""
    from backend.commands.movement_executor import MARCH_HALTS_AT_GARRISON
    from backend.display_names import humanize_entity_name
    name = humanize_entity_name(marshal.name)
    garrison = int(region.garrison_strength)
    lead = (f"ASSAULT — {name} storms the works at {region.name} alone: "
            f"{int(marshal.strength):,} men, {int(attacker_effective):,} in the "
            f"assault's reckoning")
    if coordination > 0:
        lead += f" (+{int(round(coordination * 100))}% from the corps at his side)"
    if garrison_shown is not None:
        # The desk's forecast at PARTIAL (SR session-exit residue F2): the
        # garrison is a band there, and its effective figure would give the
        # count away, so neither is printed.
        lead += f", against {garrison_shown}"
    else:
        lead += f", against a garrison of {garrison:,}"
        if garrison_effective_now != garrison:
            lead += (f" ({int(garrison_effective_now):,} behind its ground "
                     f"and works)")
    lead += "."
    adjacent = set(getattr(region, "adjacent_regions", None) or [])
    beside = [m for m in world.marshals.values()
              if m.nation == marshal.nation and m.name != marshal.name
              and int(getattr(m, "strength", 0) or 0) > 0
              and not getattr(m, "captured_by", "")
              and (m.location == marshal.location or m.location == region.name
                   or m.location in adjacent)]
    tail = ""
    if beside:
        names = [humanize_entity_name(m.name) for m in beside]
        joined = (names[0] if len(names) == 1 else
                  ", ".join(names[:-1]) + " and " + names[-1])
        verb = "does" if len(names) == 1 else "do"
        tail = f" {joined} {verb} not join an assault on the works;"
    if getattr(region, "garrison_detachment", False):
        tail += " a detachment fights to the last man."
    else:
        tail += f" the garrison breaks below {MARCH_HALTS_AT_GARRISON:,}."
    return (lead + tail).replace(";  ", "; ").strip()


def garrison_fights(region) -> bool:
    """The attack's own rule (`CombatExecutor._execute_attack`): a garrison
    stands and must be assaulted when it is a detachment (it fights to the
    last man) or a capital's at or above the collapse line. ONE copy — the
    order and the desk's forecast both read it (SR session-exit residue F2)."""
    from backend.commands.movement_executor import MARCH_HALTS_AT_GARRISON
    garrison = int(getattr(region, "garrison_strength", 0) or 0)
    if garrison <= 0:
        return False
    if getattr(region, "garrison_detachment", False):
        return True
    return garrison >= MARCH_HALTS_AT_GARRISON


def garrison_breaks(region, remaining: int) -> bool:
    """The resolver's collapse rule: a detachment breaks at nothing, a
    capital's garrison below the collapse line."""
    from backend.commands.movement_executor import MARCH_HALTS_AT_GARRISON
    if getattr(region, "garrison_detachment", False):
        return int(remaining) <= 0
    return int(remaining) < MARCH_HALTS_AT_GARRISON


def assault_forecast(world, marshal, region) -> dict:
    """The assault's reckoning WITHOUT the assault (SR session-exit residue
    F2): the resolver's own reads in the resolver's own order — the
    coordination stamp, then the attack modifier — taken PURELY. Every
    transient coordination field of every marshal is restored afterwards and
    the modifier is read with `consume=False`, so nothing a later battle
    reads is touched; the losses are `CombatExecutor.garrison_exchange`, the
    arithmetic the resolver applies (shown = applied)."""
    from backend.commands.executor import CommandExecutor
    from backend.models.marshal import Marshal
    fields = Marshal.COORDINATION_TRANSIENT_FIELDS
    saved = {}
    for key, other in world.marshals.items():
        saved[key] = {f: other.__dict__[f] for f in fields if f in other.__dict__}
    combat = CommandExecutor()._combat
    try:
        combat._calculate_coordination_context(marshal, world)
        coordination = float(
            getattr(marshal, "total_coordination_attack_bonus", 0.0) or 0.0)
        modifier = marshal.get_attack_modifier(consume=False)
    finally:
        for key, other in world.marshals.items():
            before = saved.get(key, {})
            for f in fields:
                if f in before:
                    setattr(other, f, before[f])
                elif f in other.__dict__:
                    delattr(other, f)
    attacker_effective = int(marshal.strength * modifier)
    garrison_now = int(getattr(region, "garrison_strength", 0) or 0)
    defence = garrison_effective(region)
    attacker_losses, garrison_losses = combat.garrison_exchange(
        int(marshal.strength), attacker_effective, garrison_now, defence)
    remaining = max(0, garrison_now - garrison_losses)
    return {"attacker_effective": attacker_effective,
            "garrison_effective": defence, "coordination": coordination,
            "attacker_losses": attacker_losses,
            "garrison_losses": garrison_losses, "remaining": remaining,
            "breaks": garrison_breaks(region, remaining)}


def assault_forecast_text(world, viewer: str, marshal, region) -> str:
    """The desk's answer for an assault: the order's own one-line muster,
    then — only where the garrison is counted (FULL, or our own soil) — the
    exchange the resolver would apply. At PARTIAL the garrison is a band and
    no figure that would give its count away is printed."""
    from backend.display_names import humanize_entity_name
    form, value = garrison_view(world, region.name, viewer)
    forecast = assault_forecast(world, marshal, region)
    name = humanize_entity_name(marshal.name)
    if form != "exact":
        line = assault_muster_line(
            world, marshal, region, forecast["attacker_effective"],
            forecast["garrison_effective"], forecast["coordination"],
            garrison_shown=f"a garrison ({value})")
        return (line + "\nOur intelligence gives no count of the garrison — "
                "a scout's report would let me reckon the exchange.")
    line = assault_muster_line(
        world, marshal, region, forecast["attacker_effective"],
        forecast["garrison_effective"], forecast["coordination"])
    if forecast["breaks"]:
        outcome = (f"The works would break: about "
                   f"{forecast['garrison_losses']:,} of the garrison fall, "
                   f"{name} loses about {forecast['attacker_losses']:,}, and "
                   f"{region.name} is taken.")
    else:
        outcome = (f"The works would hold: about "
                   f"{forecast['garrison_losses']:,} of the garrison fall and "
                   f"{name} loses about {forecast['attacker_losses']:,} — "
                   f"{forecast['remaining']:,} remain."
                   + assault_regen_clause(world, region))
    return line + "\n" + outcome


def assault_regen_clause(world, region) -> str:
    """AAR-24, the hold exit: what the works regain by morning — the regen
    loop's own amount (`WorldState.capital_garrison_regen`)."""
    gain = int(world.capital_garrison_regen(region))
    if gain <= 0:
        return ""
    cap = world.get_capital_garrison_target(region.controller)
    return f" It regains up to {gain:,} a turn (to {cap:,})."
