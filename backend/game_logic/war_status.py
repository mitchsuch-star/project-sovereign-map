"""War Status Panel data builder. Produces active_wars dict for HUD + detail popup."""

from typing import Dict, Any

ARMISTICE_DURATION = 5  # Must match diplomacy.py


def build_active_wars(world) -> Dict[str, Any]:
    """Build active wars data for the war status panel.

    Returns {wars: [...], coalition: {...} | None}.
    Each war entry includes HUD-level data (score, trend) AND
    detail-popup data (breakdown, battles, WE).
    All numbers int()-wrapped per Golden Rule #2.
    """
    from backend.game_logic.diplomacy import (
        calculate_war_score,
    )
    from backend.game_logic.diplomatic_ledger import (
        _get_nation_visibility, _format_army_strength,
    )
    from backend.models.intel import PARTIAL, VISIBILITY_PRIORITY

    france = world.player_nation
    wars = []
    coalition = getattr(world, 'active_coalition', None)
    coalition_members = set(
        coalition.get("members", [])
    ) if coalition else set()
    prev_scores = getattr(world, 'previous_war_scores', {})

    # ── Active wars ──
    for key, state in world.diplomatic_states.items():
        if state != "WAR":
            continue
        nations = key.split("|")
        if france not in nations:
            continue
        opponent = nations[0] if nations[1] == france else nations[1]

        # Skip eliminated nations (0 regions + 0 living marshals)
        opp_regions = sum(
            1 for r in world.regions.values()
            if r.controller == opponent
        )
        opp_marshals = sum(
            1 for m in world.marshals.values()
            if m.nation == opponent and m.strength > 0
        )
        if opp_regions == 0 and opp_marshals == 0:
            continue

        diplo_key = world._make_diplo_key(france, opponent)

        # War score + components (always live-calculate, not cached war_scores)
        components = calculate_war_score(
            france, opponent, world, return_components=True
        )
        score = int(components["total"])
        breakdown = {
            "territory": int(components["territory"]),
            "battles": int(components["battles"]),
            "decisive": int(components["decisive"]),
            "capital": int(components["capital"]),
        }

        # Duration
        started = int(getattr(world, 'war_start_turns', {}).get(diplo_key, 0))
        duration = int(world.current_turn) - started

        # Trend (compare to previous turn)
        prev = prev_scores.get(diplo_key, 0)
        if france != diplo_key.split("|")[0]:
            prev = -prev
        if score > prev + 2:
            trend = "rising"
        elif score < prev - 2:
            trend = "falling"
        else:
            trend = "stable"

        # Battle history (for detail popup)
        all_records = getattr(world, 'battle_records', {})
        records = all_records.get(diplo_key, [])
        battles_fought = int(len(records))
        # Recent battles (last 5, newest first)
        recent_battles = []
        sorted_records = sorted(
            records, key=lambda r: r.get("turn", 0), reverse=True
        )[:5]
        decisive_set = set()
        d_records = getattr(
            world, 'decisive_battles', {}
        ).get(diplo_key, [])
        for d in d_records:
            decisive_set.add(
                (d.get("turn", 0), d.get("winner", ""))
            )
        decisive_won = int(sum(
            1 for d in d_records if d.get("winner") == france
        ))
        for rec in sorted_records:
            turn = int(rec.get("turn", 0))
            winner = rec.get("winner", "")
            location = rec.get("location", "unknown")
            is_decisive = (turn, winner) in decisive_set
            won = winner == france
            recent_battles.append({
                "turn": turn,
                "location": location,
                "won": won,
                "decisive": is_decisive,
            })

        # War exhaustion + army strength (fog-filtered)
        raw_we = world.war_exhaustion.get(opponent, 0) or 0
        vis = _get_nation_visibility(opponent, world)
        vis_priority = VISIBILITY_PRIORITY.get(vis, 0)
        partial_priority = VISIBILITY_PRIORITY.get(PARTIAL, 3)
        if vis_priority >= partial_priority:
            war_exhaustion = int(raw_we)
        else:
            war_exhaustion = None

        opp_strength = sum(
            m.strength for m in world.marshals.values()
            if m.nation == opponent and m.strength > 0
        )
        army_strength = _format_army_strength(opp_strength, vis)

        # Coalition tagging
        in_coalition = opponent in coalition_members
        is_coalition_leader = bool(
            coalition and coalition.get("leader") == opponent
        )

        wars.append({
            "opponent": opponent,
            "war_score": score,
            "breakdown": breakdown,
            "duration": duration,
            "started_turn": started,
            "trend": trend,
            "battles_fought": battles_fought,
            "decisive_won": decisive_won,
            "recent_battles": recent_battles,
            "war_exhaustion": war_exhaustion,
            "army_strength": army_strength,
            "status": "war",
            "in_coalition": in_coalition,
            "is_coalition_leader": is_coalition_leader,
        })

    # Sort: coalition leader first, then coalition members, then bilateral
    wars.sort(key=lambda w: (
        not w.get("is_coalition_leader", False),
        not w.get("in_coalition", False),
        w["opponent"],
    ))

    # ── Coalition metadata ──
    coalition_info = None
    if coalition and any(w["in_coalition"] for w in wars):
        # Coordination quality between members (for detail popup)
        from backend.game_logic.coalition import get_coalition_friction
        members = [w["opponent"] for w in wars if w["in_coalition"]]
        coordination = []
        for i, m1 in enumerate(members):
            for m2 in members[i + 1:]:
                friction = get_coalition_friction(m1, m2, world)
                if friction >= 0.75:
                    quality = "Good"
                elif friction >= 0.5:
                    quality = "Strained"
                else:
                    quality = "Poor"
                coordination.append({
                    "nation_a": m1,
                    "nation_b": m2,
                    "quality": quality,
                })

        # Weak link: highest WE among members with known WE
        weak_link = None
        max_we = -1
        for w in wars:
            if w["in_coalition"] and w["war_exhaustion"] is not None:
                if w["war_exhaustion"] > max_we:
                    max_we = w["war_exhaustion"]
                    weak_link = w["opponent"]

        coalition_info = {
            "name": coalition.get("name", "Unknown Coalition"),
            "leader": coalition.get("leader", ""),
            "posture": coalition.get("strategic_posture", "defensive"),
            "coordination": coordination,
            "weak_link": weak_link,
        }

    # ── Armistice nations ──
    armistice_turns_dict = getattr(world, 'armistice_turns', {})
    for key, state in world.diplomatic_states.items():
        if state != "ARMISTICE":
            continue
        nations_in_key = key.split("|")
        if france not in nations_in_key:
            continue
        opponent = (
            nations_in_key[0]
            if nations_in_key[1] == france
            else nations_in_key[1]
        )
        diplo_key = world._make_diplo_key(france, opponent)
        elapsed = int(armistice_turns_dict.get(diplo_key, 0))
        remaining = int(max(0, ARMISTICE_DURATION - elapsed))

        # Relation + trend for armistice detail popup
        relation = int(
            world.nation_relations.get(diplo_key, 0) or 0
        )
        from backend.game_logic.diplomacy import get_relation_descriptor
        relation_desc = get_relation_descriptor(relation)
        relation_history = getattr(
            world, 'relation_history', {}
        ).get(diplo_key, [])
        if len(relation_history) >= 2:
            delta = relation - relation_history[-1]
            rel_trend = (
                "rising" if delta > 2
                else "falling" if delta < -2
                else "stable"
            )
        else:
            rel_trend = "stable"

        wars.append({
            "opponent": opponent,
            "war_score": 0,
            "breakdown": None,
            "duration": 0,
            "started_turn": 0,
            "trend": "stable",
            "battles_fought": 0,
            "decisive_won": 0,
            "recent_battles": [],
            "war_exhaustion": None,
            "army_strength": None,
            "status": "armistice",
            "armistice_remaining": remaining,
            "relation": relation,
            "relation_descriptor": relation_desc,
            "relation_trend": rel_trend,
            "in_coalition": False,
            "is_coalition_leader": False,
        })

    return {
        "wars": wars,
        "coalition": coalition_info,
    }
