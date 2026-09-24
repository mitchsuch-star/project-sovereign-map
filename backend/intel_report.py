"""
Berthier's Intelligence Report (Phase 6 — Fog of War, Session 34A)

Generates a fog-filtered status view grouped by visibility tier.
Replaces the omniscient status dump with a Napoleonic intelligence briefing.

Reusable by Campaign Briefing (Phase 6.5).

Usage:
    from backend.intel_report import generate_intel_report
    report = generate_intel_report(world)
"""

from typing import Dict, Any
from backend.display_names import humanize_entity_name
from backend.models.intel import (
    FULL, PARTIAL, STALE, LAST_KNOWN, UNKNOWN,
)

# IQ-2 (Sept 14, 2026): YOUR FORCES filters on strength > 0, and a captured
# marshal is held at strength 0 in the captor's capital — so a captured
# Emperor simply vanished from Berthier's report, with no word that he was
# taken or by whom. A PRISONERS section now names each captured marshal of
# ours and his captor (a prisoner is not a force, so he leaves YOUR FORCES).
# Our own men are ours to name — fog governs the enemy (R5). Flip lever:
# False restores the silent report byte-for-byte.
THE_REPORT_NAMES_ITS_PRISONERS = True


def generate_intel_report(world) -> Dict[str, Any]:
    """
    Build Berthier's Intelligence Report from the intel store.

    Groups all regions by visibility tier and formats appropriately:
    - YOUR FORCES: Always shown with full detail
    - CONFIRMED: FULL visibility enemy intel (exact numbers)
    - RECENT REPORTS: PARTIAL/STALE (strength bands, timestamps)
    - LAST KNOWN: Old intel with age warning
    - NO INTELLIGENCE: Regions with UNKNOWN visibility

    Args:
        world: WorldState instance with intel store populated

    Returns:
        Dict with structured report data for API response / Godot display
    """
    player_nation = world.player_nation

    # ── YOUR FORCES (always full detail) ──
    your_forces = []
    prisoners = []
    for name, marshal in world.marshals.items():
        if (THE_REPORT_NAMES_ITS_PRISONERS and marshal.nation == player_nation
                and getattr(marshal, "captured_by", "")):
            from backend.game_logic.formations import formed_display_name
            prisoners.append({
                "name": marshal.name,
                "captor": marshal.captured_by,
                "captor_display": formed_display_name(world, marshal.captured_by),
                "location": marshal.location or "",
                "captured_turn": int(getattr(marshal, "captured_turn", 0) or 0),
            })
            continue
        if marshal.nation == player_nation and marshal.strength > 0:
            stance_val = marshal.stance.value if hasattr(marshal.stance, 'value') else str(marshal.stance)
            your_forces.append({
                "name": marshal.name,
                "location": marshal.location,
                "strength": int(marshal.strength),
                "morale": int(marshal.morale),
                "stance": stance_val,
                "broken": bool(getattr(marshal, 'broken', False)),
                "retreating": bool(getattr(marshal, 'retreating', False)),
                "in_strategic_mode": bool(marshal.in_strategic_mode),
                "strategic_command_type": str(marshal.strategic_command_type) if marshal.strategic_command_type else "",
            })

    # ── Categorize regions by visibility ──
    confirmed = []       # FULL visibility
    recent_reports = []  # PARTIAL or STALE
    last_known = []      # LAST_KNOWN
    no_intelligence = [] # UNKNOWN

    for region_name, region in world.regions.items():
        intel = world.get_region_intel(region_name)
        visibility = intel.visibility

        # Base region info (always public: controller, terrain)
        region_info = {
            "region": region_name,
            "controller": region.controller,
            "terrain": region.terrain,
            "visibility": visibility,
        }

        if visibility == FULL:
            # Full detail on enemies
            enemies = []
            for m in world.get_marshals_in_region(region_name):
                if m.nation != player_nation and m.strength > 0:
                    stance_val = m.stance.value if hasattr(m.stance, 'value') else str(m.stance)
                    # MC-1 visibility rider: a famed commander's signature
                    # ability is reputation, not troop intel — at FULL
                    # visibility Berthier names it (Habsburg Resolve, The
                    # Old Fox, the Shorncliffe System...), so enemy-side
                    # abilities are discoverable, never a hidden gotcha.
                    ability = getattr(m, 'ability', None) or {}
                    ability_name = ability.get("name", "")
                    enemies.append({
                        "name": m.name,
                        "nation": m.nation,
                        "strength": int(m.strength),
                        "morale": int(m.morale),
                        "stance": stance_val,
                        "ability": ability_name if ability_name not in ("", "None") else "",
                    })
            if enemies:
                region_info["enemies"] = enemies
                region_info["intel_source"] = intel.intel_source
                region_info["last_updated_turn"] = int(intel.last_updated_turn)
                confirmed.append(region_info)

        elif visibility in (PARTIAL, STALE):
            # Strength band only, from intel snapshot (may be stale)
            if intel.known_marshals:
                region_info["known_marshals"] = intel.known_marshals
                region_info["strength_band"] = intel.strength_band
                region_info["intel_source"] = intel.intel_source
                region_info["last_updated_turn"] = int(intel.last_updated_turn)
                turns_ago = int(world.current_turn - intel.last_updated_turn)
                region_info["turns_ago"] = turns_ago
                if visibility == STALE:
                    region_info["stale"] = True
                recent_reports.append(region_info)

        elif visibility == LAST_KNOWN:
            if intel.known_marshals:
                region_info["known_marshals"] = intel.known_marshals
                region_info["strength_band"] = intel.strength_band
                turns_ago = int(world.current_turn - intel.last_updated_turn)
                region_info["turns_ago"] = turns_ago
                last_known.append(region_info)

        elif visibility == UNKNOWN:
            no_intelligence.append(region_info)

    # ── Build formatted text for terminal display ──
    lines = ["=== BERTHIER'S INTELLIGENCE REPORT ===", ""]

    # IQ-2: a collapsed realm is the first thing the report states — the
    # one source's summary, and the scope note beside it (legible, never
    # terminal). None off-sandbox and while the realm stands.
    from backend.game_logic import collapse as _collapse
    collapse_state = _collapse.get_collapse_state(world)
    if collapse_state is not None:
        lines.append("STATE OF THE EMPIRE:")
        lines.append(f"  {_collapse.summary_line(world, collapse_state)}")
        # GE-1 R9: the clock and its exits where the rules are authored.
        from backend.game_logic import fall as _fall
        lines.append(f"  {_fall.scope_sentence(world)}")
        lines.append("")

    # Your Forces
    lines.append("YOUR FORCES:")
    if your_forces:
        for f in your_forces:
            status_parts = []
            status_parts.append(f"{f['strength']:,} troops")
            status_parts.append(f"morale {f['morale']}")
            status_parts.append(f"{f['stance']} stance")
            if f["broken"]:
                status_parts.append("BROKEN")
            if f["retreating"]:
                status_parts.append("retreating")
            if f["in_strategic_mode"]:
                status_parts.append(f"[{f['strategic_command_type']}]")
            lines.append(f"  {f['name']} ({f['location']}): {', '.join(status_parts)}")
    else:
        lines.append("  No marshals available.")
    lines.append("")

    # IQ-2: our captured marshals, named with their captor.
    if prisoners:
        lines.append("PRISONERS:")
        for p in prisoners:
            since = f" since T{p['captured_turn']}" if p["captured_turn"] else ""
            cell = f" at {p['location']}" if p["location"] else ""
            lines.append(f"  {humanize_entity_name(p['name'])}: held by "
                         f"{p['captor_display']}{cell}{since}.")
        lines.append("")

    # Confirmed (FULL)
    if confirmed:
        lines.append("CONFIRMED INTELLIGENCE:")
        for r in confirmed:
            for e in r.get("enemies", []):
                famed = f" — famed for '{e['ability']}'" if e.get("ability") else ""
                lines.append(f"  {humanize_entity_name(e['name'])} ({e['nation']}): {e['strength']:,} troops at {r['region']}, "
                             f"{e['stance']} stance, morale {e['morale']}{famed}")
        lines.append("")

    # Recent Reports (PARTIAL/STALE)
    if recent_reports:
        lines.append("RECENT REPORTS:")
        for r in recent_reports:
            names = [humanize_entity_name(m.get("name", "Unknown")) for m in r.get("known_marshals", [])]
            names_str = ", ".join(names)
            stale_marker = f" [{r['turns_ago']} turns ago]" if r.get("stale") else ""
            lines.append(f"  {names_str}: {r['strength_band']} near {r['region']}{stale_marker}")
        lines.append("")

    # Last Known
    if last_known:
        lines.append("LAST KNOWN:")
        for r in last_known:
            names = [humanize_entity_name(m.get("name", "Unknown")) for m in r.get("known_marshals", [])]
            names_str = ", ".join(names)
            lines.append(f"  {names_str}: last seen near {r['region']}, {r['turns_ago']} turns ago")
        lines.append("")

    # No Intelligence — W6-3 §5.4: on the 126-province map this listed 85
    # raw names (a wall). Collapse to a count + the FRONTIER names: unknown
    # regions adjacent to any known region (≤8), i.e. where the fog begins.
    no_intel_summary = ""
    if no_intelligence:
        unknown_names = {r["region"] for r in no_intelligence}
        frontier = []
        for r in no_intelligence:
            region = world.regions.get(r["region"])
            if region is None:
                continue
            if any(adj not in unknown_names for adj in region.adjacent_regions):
                frontier.append(r["region"])
                if len(frontier) >= 8:
                    break
        count = len(no_intelligence)
        if frontier:
            no_intel_summary = (
                f"No word from {count} provinces beyond the frontiers of "
                f"{', '.join(frontier)}."
            )
        else:
            no_intel_summary = f"No word from {count} provinces."
        lines.append(f"NO INTELLIGENCE: {no_intel_summary}")
        lines.append("")

    report_text = "\n".join(lines)

    report = {
        "report_text": report_text,
        "your_forces": your_forces,
        "confirmed": confirmed,
        "recent_reports": recent_reports,
        "last_known": last_known,
        "no_intelligence": no_intelligence,
        "no_intelligence_summary": no_intel_summary,
        "turn": int(world.current_turn),
    }
    # IQ-2: new keys only where they carry something, so a standing realm's
    # payload (and the lever-down report) is unchanged.
    if THE_REPORT_NAMES_ITS_PRISONERS and prisoners:
        report["prisoners"] = prisoners
    if collapse_state is not None:
        report["collapse_line"] = _collapse.summary_line(world, collapse_state)
    return report
