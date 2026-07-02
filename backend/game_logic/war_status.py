"""War Status Panel data builder. Produces active_wars dict for HUD + detail popup."""

from typing import Any, Dict, List, Optional

from backend.display_names import display_nation

ARMISTICE_DURATION = 5  # Must match diplomacy.py
ARMISTICE_AUTO_PEACE_RELATION = -60  # Must match diplomacy.py (G4F-17)


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
            "ticking": int(components.get("ticking", 0)),
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

        # WPS-A: War objective + settlement tier
        from backend.game_logic.diplomacy import (
            TICKING_RATES, OBJECTIVE_TYPE_DISPLAY,
            SETTLEMENT_TIER_DISPLAY, get_settlement_tier,
        )
        war_obj_data = getattr(world, 'war_objectives', {}).get(diplo_key, {})
        france_obj = war_obj_data.get(france, {})
        enemy_obj = war_obj_data.get(opponent, {})

        objective_info = None
        if france_obj and france_obj.get("concluded_turn") is None:
            obj_type = france_obj.get("type", "")
            objective_info = {
                "type": obj_type,
                "type_display": OBJECTIVE_TYPE_DISPLAY.get(obj_type, obj_type),
                "target_regions": france_obj.get("target_regions", []),
                "accumulated_ticking": int(france_obj.get("accumulated_ticking", 0)),
                "ticking_active": bool(france_obj.get("ticking_active", False)),
                "ticking_rate": int(TICKING_RATES.get(obj_type, 0)),
            }

        enemy_objective_info = None
        if enemy_obj and enemy_obj.get("concluded_turn") is None:
            eo_type = enemy_obj.get("type", "")
            enemy_objective_info = {
                "type": eo_type,
                "type_display": OBJECTIVE_TYPE_DISPLAY.get(eo_type, eo_type),
            }

        tier = get_settlement_tier(score)

        # Slice E §16.2 line 1629 — contribution share rows for the war
        # status detail panel. Resolved via the active war_instance for
        # the bilateral pair when one exists; falls back to an empty
        # block when no war_instance is wired (early game / synthetic).
        contribution = _resolve_contribution_share(world, france, opponent)

        settlement_eligibility = _evaluate_settlement_eligibility(
            world, contribution.get("war_id", ""),
        )
        settlement_available = bool(settlement_eligibility.get("available"))
        war_detail_actionability = _evaluate_war_detail_actionability(
            world,
            contribution.get("war_id", ""),
            opponent,
            settlement_eligibility.get("coverable_enemy_participants", []),
        )
        # PF-2 / D4 + UX-1: "Draft kept" badge — true iff a same-turn scoped
        # settlement draft exists for this war (drafts are cleared at turn
        # end, so existence == same-turn), making the Back Out promise
        # visible AND true on the reopen surface.
        settlement_draft_kept = _war_has_kept_settlement_draft(
            world, contribution.get("war_id", ""),
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
            "objective": objective_info,
            "enemy_objective": enemy_objective_info,
            "settlement_tier": tier,
            "settlement_tier_display": SETTLEMENT_TIER_DISPLAY.get(tier, tier),
            "contribution_share": contribution.get("rows", []),
            "contribution_overflow_count": int(
                contribution.get("overflow_count", 0) or 0
            ),
            "standing_status": contribution.get("standing_status", ""),
            "standing_status_display": contribution.get(
                "standing_status_display", ""
            ),
            "war_instance_id": contribution.get("war_id", ""),
            "settlement_available": settlement_available,
            "settlement_draft_kept": settlement_draft_kept,
            "settlement_eligibility": settlement_eligibility,
            "war_detail_actionability": war_detail_actionability,
            "settlement_disabled_reason": settlement_eligibility.get(
                "display_reason", ""
            ) if not settlement_available else "",
            "settlement_disabled_reason_display": settlement_eligibility.get(
                "disabled_reason_display", ""
            ) if not settlement_available else "",
        })

    wars = _collapse_shared_war_instance_rows(world, france, wars)

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
            # G4F-17: project the expiry fork (relations vs the -60 line)
            # so the HUD/detail can say where the truce is heading, not
            # just how long it has left.
            "armistice_projected_outcome": (
                "peace" if relation >= ARMISTICE_AUTO_PEACE_RELATION else "war"
            ),
            "armistice_auto_peace_threshold": int(ARMISTICE_AUTO_PEACE_RELATION),
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


def _collapse_shared_war_instance_rows(
    world,
    france: str,
    wars: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Collapse bilateral HUD rows that are fronts of one shared war_instance."""
    instances = getattr(world, "war_instances", None) or {}
    if not instances:
        return wars

    passthrough: List[Dict[str, Any]] = []
    by_war_id: Dict[str, List[Dict[str, Any]]] = {}
    for row in wars:
        war_id = str(row.get("war_instance_id", "") or "")
        instance = instances.get(war_id)
        if (
            not war_id
            or not isinstance(instance, dict)
            or instance.get("ended_turn") is not None
            or len(instance.get("active_diplo_keys") or []) <= 1
            or str(row.get("status", "")) != "war"
        ):
            passthrough.append(row)
            continue
        by_war_id.setdefault(war_id, []).append(row)

    collapsed: List[Dict[str, Any]] = list(passthrough)
    for war_id, rows in by_war_id.items():
        if len(rows) <= 1:
            collapsed.extend(rows)
            continue

        instance = instances.get(war_id) or {}
        side_by_nation = instance.get("side_by_nation") or {}
        france_side = side_by_nation.get(france)
        enemy_side = "defenders" if france_side == "attackers" else "attackers"
        leader_key = "defender_leader" if enemy_side == "defenders" else "attacker_leader"
        enemy_leader = str(instance.get(leader_key, "") or "")
        enemy_participants = [
            nation for nation, side in side_by_nation.items()
            if side == enemy_side and nation != france
        ]
        if not enemy_participants:
            enemy_participants = [str(row.get("opponent", "")) for row in rows]

        ordered_opponents = _leader_first(enemy_participants, enemy_leader)
        representative = next(
            (row for row in rows if row.get("opponent") == enemy_leader),
            rows[0],
        )
        combined = dict(representative)
        combined["opponents"] = ordered_opponents
        combined["opponent"] = (
            ordered_opponents[0] if ordered_opponents else representative.get("opponent", "")
        )
        combined["opponent_display"] = " + ".join(
            display_nation(nation) for nation in ordered_opponents
        )
        combined["is_multi_participant_war"] = True
        collapsed.append(combined)

    return collapsed


def _leader_first(nations: List[str], leader: str) -> List[str]:
    ordered = sorted({str(nation) for nation in nations if nation})
    if leader in ordered:
        ordered.remove(leader)
        return [leader] + ordered
    return ordered


def _resolve_contribution_share(world, france: str, opponent: str) -> Dict[str, Any]:
    """Find the active war_instance covering the France/opponent pair and
    build top-N contribution share rows for it.

    Returns ``{rows, overflow_count, war_id, standing_status}``. Empty
    rows include a humanized status so Godot does not need to show a blank
    standing area or raw fallback identifiers.
    """
    from backend.game_logic.settlement_presentation import (
        build_contribution_share_rows,
    )
    war_id = _find_active_war_instance_id(world, france, opponent)
    if not war_id:
        return {
            "rows": [],
            "overflow_count": 0,
            "war_id": "",
            "standing_status": "no_war_instance",
            "standing_status_display": (
                "Standing appears once this war is opened as a settlement."
            ),
        }
    contribution = build_contribution_share_rows(world, war_id)
    contribution["war_id"] = war_id
    if contribution.get("rows"):
        contribution["standing_status"] = "available"
        contribution["standing_status_display"] = "Standing available."
    else:
        contribution["standing_status"] = "no_contribution_rows"
        contribution["standing_status_display"] = (
            "No participant standing has been recorded yet."
        )
    return contribution


def _find_active_war_instance_id(
    world, nation_a: str, nation_b: str,
) -> Optional[str]:
    """Return the active war_instance id covering both nations, or None."""
    instances = getattr(world, "war_instances", None) or {}
    if not instances:
        return None
    # Prefer the by-participant index when available.
    index_getter = getattr(world, "get_war_instances_by_participant", None)
    candidate_ids: List[str] = []
    if callable(index_getter):
        a_ids = list(index_getter(nation_a) or [])
        b_ids = set(index_getter(nation_b) or [])
        candidate_ids = [wid for wid in a_ids if wid in b_ids]
    else:
        candidate_ids = list(instances.keys())
    for war_id in candidate_ids:
        instance = instances.get(war_id)
        if not isinstance(instance, dict):
            continue
        if instance.get("ended_turn") is not None:
            continue
        attackers = set(instance.get("attackers") or [])
        defenders = set(instance.get("defenders") or [])
        if (
            (nation_a in attackers and nation_b in defenders)
            or (nation_a in defenders and nation_b in attackers)
        ):
            return war_id
    return None


def _is_common_settlement_worth_showing(world, war_id: str) -> bool:
    """Return True when common peace adds value over bilateral peace."""
    if not war_id:
        return False
    instance = (getattr(world, "war_instances", None) or {}).get(war_id)
    if not instance or instance.get("ended_turn") is not None:
        return False
    from backend.game_logic.settlement_validation import (
        is_common_settlement_worth_showing,
    )

    return is_common_settlement_worth_showing(instance)


def _war_has_kept_settlement_draft(world, war_id: str) -> bool:
    """PF-2 / D4 + UX-1: does a same-turn scoped settlement draft exist?

    True iff the SC-5R scoped draft store holds a non-empty entry for this
    war (`settlement_draft:{war_id}:` key prefix). The store is cleared at
    turn end, so existence implies same-turn; the badge appears iff a
    reopen would actually restore something.
    """
    if not war_id:
        return False
    drafts = getattr(world, "pending_settlement_drafts_by_key", None)
    if not isinstance(drafts, dict):
        return False
    prefix = f"settlement_draft:{war_id}:"
    return any(
        isinstance(key, str) and key.startswith(prefix) and entry
        for key, entry in drafts.items()
    )


def _evaluate_settlement_eligibility(world, war_id: str) -> Dict[str, Any]:
    """SC-10: Use active hostile-pair eligibility, not just unique-nation count."""
    from backend.display_names import settlement_disabled_reason_display

    def _blocked(code: str, **extra: Any) -> Dict[str, Any]:
        display = settlement_disabled_reason_display(code)
        return {
            "available": False,
            "error": code,
            "error_display": display,
            "disabled_reason_display": display,
            "display_reason": display,
            **extra,
        }

    if not war_id:
        return _blocked("invalid_war_id", war_id=war_id)
    try:
        from backend.game_logic.settlement_validation import (
            evaluate_open_settlement_eligibility,
        )
        eligibility = evaluate_open_settlement_eligibility(
            world, war_id=war_id,
            actor_nation=getattr(world, "player_nation", "France"),
            ignore_active_dialogue=True,
        )
        return dict(eligibility)
    except Exception:
        return _blocked("settlement_eligibility_unavailable", war_id=war_id)


def _evaluate_settlement_available(world, war_id: str) -> bool:
    return bool(_evaluate_settlement_eligibility(world, war_id).get("available"))


def _evaluate_war_detail_actionability(
    world,
    war_id: str,
    selected_target_nation: str,
    covered_enemy_participants: List[str],
) -> Dict[str, Any]:
    """Return SC-10b recovery metadata for the War Detail row."""
    try:
        from backend.game_logic.settlement_routes import (
            evaluate_war_detail_actionability,
        )
        return dict(evaluate_war_detail_actionability(
            world,
            war_id=war_id,
            selected_target_nation=selected_target_nation,
            covered_enemy_participants=covered_enemy_participants,
        ))
    except Exception:
        return {
            "actionable": False,
            "war_id": str(war_id or ""),
            "selected_target_nation": str(selected_target_nation or ""),
            "refusal_code": "no_peace_seeking_control",
            "refusal_code_display": "War detail recovery is unavailable.",
            "peace_seeking_controls": [],
        }
