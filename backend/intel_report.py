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
from backend.models.intel import (
    FULL, PARTIAL, STALE, LAST_KNOWN, UNKNOWN,
)


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
    for name, marshal in world.marshals.items():
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
                    enemies.append({
                        "name": m.name,
                        "nation": m.nation,
                        "strength": int(m.strength),
                        "morale": int(m.morale),
                        "stance": stance_val,
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

    # Confirmed (FULL)
    if confirmed:
        lines.append("CONFIRMED INTELLIGENCE:")
        for r in confirmed:
            for e in r.get("enemies", []):
                lines.append(f"  {e['name']} ({e['nation']}): {e['strength']:,} troops at {r['region']}, "
                             f"{e['stance']} stance, morale {e['morale']}")
        lines.append("")

    # Recent Reports (PARTIAL/STALE)
    if recent_reports:
        lines.append("RECENT REPORTS:")
        for r in recent_reports:
            names = [m.get("name", "Unknown") for m in r.get("known_marshals", [])]
            names_str = ", ".join(names)
            stale_marker = f" [{r['turns_ago']} turns ago]" if r.get("stale") else ""
            lines.append(f"  {names_str}: {r['strength_band']} near {r['region']}{stale_marker}")
        lines.append("")

    # Last Known
    if last_known:
        lines.append("LAST KNOWN:")
        for r in last_known:
            names = [m.get("name", "Unknown") for m in r.get("known_marshals", [])]
            names_str = ", ".join(names)
            lines.append(f"  {names_str}: last seen near {r['region']}, {r['turns_ago']} turns ago")
        lines.append("")

    # No Intelligence
    if no_intelligence:
        region_names = [r["region"] for r in no_intelligence]
        lines.append(f"NO INTELLIGENCE: {', '.join(region_names)}")
        lines.append("")

    report_text = "\n".join(lines)

    return {
        "report_text": report_text,
        "your_forces": your_forces,
        "confirmed": confirmed,
        "recent_reports": recent_reports,
        "last_known": last_known,
        "no_intelligence": no_intelligence,
        "turn": int(world.current_turn),
    }
