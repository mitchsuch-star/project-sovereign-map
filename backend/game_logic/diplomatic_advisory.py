"""
Diplomatic Advisory System — Phase 8 Session 4

Handles Talleyrand's strategic advisory conversations: threat assessment,
nation analysis, action recommendations, and diplomatic overview.

All functions are pure/deterministic — no LLM calls. Works identically
in mock mode. Advisory dialogues cost 0 DP and are non-blocking.

Entry points:
  - detect_advisory_type() → keyword match to advisory subtype
  - generate_advisory() → builds pending_diplomatic_dialogue dict (type="advisory")
"""

from typing import Dict, List, Optional

from backend.game_logic.diplomacy import get_war_score_for
from backend.game_logic.diplomatic_dialogue import (
    get_known_nations,
)
from backend.nation_config import get_player_nation

# ═══════ ADVISORY KEYWORD MAP ═══════
# Longest-first matching prevents "what" from shadowing "what about"

ADVISORY_KEYWORDS = {
    "what about": "assess_nation",
    "what should": "recommend_action",
    "who is": "compare_threats",
    "should i": "recommend_action",
    "what happens if": "predict_outcome",
    "what if": "predict_outcome",
    "bigger threat": "compare_threats",
    "focus on": "recommend_priority",
    "can we": "feasibility",
    "how do we": "recommend_action",
    # W6-9 (EXP-D1): the strategic assessment verb — the war room.
    # Longest-first sorting lets the specific phrases beat bare "assess";
    # "how do we stand" outranks "how do we" the same way.
    "what does europe intend": "assess_situation",
    "assess our situation": "assess_situation",
    "assess the situation": "assess_situation",
    "strategic assessment": "assess_situation",
    "where do we stand": "assess_situation",
    "how do we stand": "assess_situation",
    "situation report": "assess_situation",
    "state of europe": "assess_situation",
    "our situation": "assess_situation",
    "assess": "assess_situation",
}

# Sorted by key length descending so longer phrases match first
_SORTED_KEYWORDS = sorted(ADVISORY_KEYWORDS.items(), key=lambda kv: -len(kv[0]))

# Diplomat personality descriptors (for Talleyrand's commentary)
_DIPLOMAT_DESCRIPTORS = {
    "hawk": "bellicose",
    "schemer": "calculating",
    "dove": "conciliatory",
    "loyalist": "steadfast",
}

# State display names — single source in display_names.py (R7)
from backend.display_names import STATE_NARRATIVE_DISPLAY as _STATE_DISPLAY


# ═══════════════════════════════════════════════════════
# PUBLIC API
# ═══════════════════════════════════════════════════════

def detect_advisory_type(text: str) -> Optional[str]:
    """Detect advisory subtype from player text via keyword matching.

    Returns one of: assess_nation, recommend_action, compare_threats,
    predict_outcome, recommend_priority, feasibility — or None if no match.
    """
    text_lower = text.lower().strip()
    for keyword, subtype in _SORTED_KEYWORDS:
        if keyword in text_lower:
            # "can we" / feasibility is handled by the feasibility system, not here
            if subtype == "feasibility":
                return None
            return subtype
    return None


def generate_advisory(
    target_nation: Optional[str],
    advisory_type: str,
    world,
) -> Dict:
    """Build an advisory dialogue dict for pending_diplomatic_dialogue.

    Args:
        target_nation: Specific nation being asked about, or None for overview.
        advisory_type: One of the subtypes from detect_advisory_type().
        world: WorldState instance.

    Returns:
        Dict suitable for world.pending_diplomatic_dialogue (type="advisory").
    """
    if advisory_type == "assess_situation":
        # W6-9: "assess Austria" is a nation question, not the war room —
        # a named target downgrades to the nation assessment.
        if target_nation:
            return _assess_nation(target_nation, world)
        return _assess_situation(world)
    elif advisory_type == "compare_threats":
        return _compare_threats(world)
    elif advisory_type == "assess_nation" and target_nation:
        return _assess_nation(target_nation, world)
    elif advisory_type == "recommend_action":
        if target_nation:
            return _recommend_action(target_nation, world)
        return _recommend_action_overview(world)
    elif advisory_type == "recommend_priority":
        return _compare_threats(world)
    elif advisory_type == "predict_outcome" and target_nation:
        return _assess_nation(target_nation, world)
    else:
        # Fallback: general overview
        return _diplomatic_overview(world)


# ═══════════════════════════════════════════════════════
# W6-9 (EXP-D1) — THE WAR ROOM: "assess our situation"
# ═══════════════════════════════════════════════════════

def _war_trajectory_phrase(score: int, trend: str) -> str:
    """Deterministic prose for a war score + trend (composition only)."""
    if score >= 20:
        base = "goes well"
    elif score >= 5:
        base = "favors us"
    elif score > -5:
        base = "hangs in the balance"
    elif score > -20:
        base = "turns against us"
    else:
        base = "goes badly"
    suffix = {"rising": ", and improving", "falling": ", and worsening"}
    return base + suffix.get(trend, "")


def _weakest_ally(world, player: str) -> Optional[str]:
    """The player's lowest-relation alliance partner (None if unallied)."""
    best = None
    for key, state in world.diplomatic_states.items():
        if state not in ("ALLIANCE", "DEFENSIVE_ALLIANCE"):
            continue
        a, b = key.split("|", 1)
        if player not in (a, b):
            continue
        other = b if a == player else a
        rel = int(world.nation_relations.get(key, 0))
        if best is None or rel < best[1]:
            best = (other, rel)
    return best[0] if best else None


def _recent_vassal_reason(world, vassal_name: str) -> str:
    """The most recent vassal_loyalty event's cause line (W6-3 `reason`),
    from the bounded recent event-log window (GR8-safe, W6-3 precedent)."""
    window_start = world.current_turn - 5
    reason = ""
    for event in world.event_log:
        if event.get("turn", 0) < window_start:
            continue
        if (event.get("type") == "vassal_loyalty"
                and event.get("vassal") == vassal_name
                and event.get("reason")):
            reason = event["reason"]
    return reason


def _build_situation_recommendation(world, player: str, war_rows: List[Dict],
                                    coalition_info: Optional[Dict],
                                    posture: str) -> Optional[Dict]:
    """The deterministic recommendation table (spec §11, priority order) —
    ONE suggestion, never a list. `kind` decides the executable option:
    open_proposal rides the existing expand_options arm; request_terms and
    invest_vassal ride the W6-9 execute_suggestion arm."""
    # 1. Losing war + a settlement route exists → seek terms.
    losing = sorted((w for w in war_rows if int(w.get("war_score", 0)) < 0),
                    key=lambda w: int(w.get("war_score", 0)))
    for row in losing:
        opponent = row.get("opponent", "")
        terms_state = (row.get("request_terms_state") or {}).get("state", "")
        if terms_state == "available":
            return {
                "kind": "request_terms",
                "target_nation": opponent,
                "label": f"Seek terms with {opponent}",
                "description": ("Ask their court to name settlement terms "
                                "(1 DP)."),
                "text": (f"the war with {opponent} turns against us and "
                         f"their court would name terms — ask, Sire, while "
                         f"asking is still a choice."),
            }
        if row.get("settlement_available"):
            return {
                "kind": "open_proposal",
                "target_nation": opponent,
                "label": f"Open talks with {opponent}",
                "description": "Open a proposal toward a settlement.",
                "text": (f"the war with {opponent} turns against us — "
                         f"open talks before the price of peace rises."),
            }
    # 1.5 (NA-1): a belligerent's design could be satisfied at the table —
    # the Pressburg counsel. Cede what their court actually wants and their
    # reason to fight (or the coalition's cohesion) goes with it. A
    # coalition row carries every participant in `opponents`; satisfying a
    # NON-leader member is exactly how coalitions crack.
    from backend.display_names import display_nation
    from backend.game_logic.agendas import (
        agenda_satisfiable_by_player, build_agenda_payload,
    )
    for row in war_rows:
        participants = [n for n in (row.get("opponents")
                                    or [row.get("opponent", "")]) if n]
        for opponent in participants:
            if not agenda_satisfiable_by_player(opponent, world):
                continue
            payload = build_agenda_payload(opponent, world) or {}
            title = payload.get("title", "their design")
            display = display_nation(opponent)
            terms_state = (row.get("request_terms_state") or {}).get("state", "")
            # The terms route belongs to the row's leader; other members
            # get the proposal menu (expand_options is always reachable).
            if opponent == row.get("opponent") and terms_state == "available":
                return {
                    "kind": "request_terms",
                    "target_nation": opponent,
                    "label": f"Satisfy their design ({display})",
                    "description": (f"Their court fights for '{title}' — "
                                    f"ask them to name terms (1 DP)."),
                    "text": (f"{display}'s war has a purpose we can "
                             f"price — '{title}'. We hold what their "
                             f"court wants; satisfy the design at the "
                             f"table and their reason to fight goes "
                             f"with it."),
                }
            return {
                "kind": "open_proposal",
                "target_nation": opponent,
                "label": f"Satisfy their design ({display})",
                "description": (f"Their court fights for '{title}' — open "
                                f"talks and put it on the table."),
                "text": (f"{display}'s war has a purpose we can price — "
                         f"'{title}'. We hold what their court wants; "
                         f"offer it at the table and their reason to "
                         f"fight goes with it."),
            }
    # 2. An aggressive coalition bearing down → shore the weakest friend.
    if posture == "aggressive" and int(getattr(world, "threat_level", 0)) > 60:
        ally = _weakest_ally(world, player)
        if ally:
            return {
                "kind": "open_proposal",
                "target_nation": ally,
                "label": f"Shore up {ally}",
                "description": "Open a proposal to steady our weakest ally.",
                "text": (f"the coalition means to fight — steady {ally}, "
                         f"our least certain friend, before they test him."),
            }
        weak = (coalition_info or {}).get("weak_link")
        if weak:
            return {
                "kind": "open_proposal",
                "target_nation": weak,
                "label": f"Court {weak}",
                "description": "Open a proposal to the coalition's weak link.",
                "text": (f"the coalition means to fight — {weak} is its "
                         f"weakest link, and links can be… loosened."),
            }
    # 3. A vassal near revolt → invest.
    vassals = getattr(world, "vassals", {}) or {}
    for name, record in sorted(vassals.items(),
                               key=lambda kv: int(kv[1].get("loyalty", 100))):
        if record.get("lord") != player:
            continue
        if int(record.get("loyalty", 100)) < 40:
            return {
                "kind": "invest_vassal",
                "target": name,
                "label": f"Invest in {name}",
                "description": "1 DP + 200 gold; +10 loyalty.",
                "text": (f"{name} drifts toward revolt — a little gold now "
                         f"is cheaper than a garrison later."),
            }
    # 4. The highest-value diplomatic opening (relation −10..40, no war,
    #    open proposal cooldown).
    cooldowns = world.player_proposal_cooldowns
    best = None
    for nation in world.get_active_nations():
        if nation == player or nation in vassals:
            continue
        if world.is_at_war(player, nation):
            continue
        rel = int(world.nation_relations.get(
            world._make_diplo_key(player, nation), 0))
        if not (-10 <= rel <= 40):
            continue
        if int(cooldowns.get(nation, 0)) > 0:
            continue
        if best is None or rel > best[1]:
            best = (nation, rel)
    if best:
        return {
            "kind": "open_proposal",
            "target_nation": best[0],
            "label": f"Approach {best[0]}",
            "description": "Open a proposal — the ripest diplomatic opening.",
            "text": (f"{best[0]} is neither friend nor enemy (relations "
                     f"{best[1]:+d}) — the ripest court in Europe for an "
                     f"approach."),
        }
    return None


def _assess_situation(world) -> Dict:
    """The war room (W6-9 / EXP-D1): per-war trajectory in prose, the
    coalition's POSTURE (computed for the AI six times over, shown to the
    player for the first time here), this turn's itemized threat sources,
    vassal loyalty trend + cause, and ONE recommendation ending in an
    executable option (R117).

    Composition ONLY — every number comes from the same fog-safe builders
    the ledgers use (build_active_wars, threat_sources_this_turn); no new
    formulas, no LLM (GR6). Diplomacy itself has no fog (project rule).
    """
    from backend.game_logic.coalition import (
        get_coalition_posture, get_threat_tier,
    )
    from backend.game_logic.diplomatic_ledger import _THREAT_SOURCE_LABELS
    from backend.game_logic.war_status import build_active_wars

    player = get_player_nation(world)
    wars_data = build_active_wars(world)
    all_rows = wars_data.get("wars", []) or []
    war_rows = [w for w in all_rows if w.get("status") == "war"]
    armistice_rows = [w for w in all_rows if w.get("status") == "armistice"]
    coalition_info = wars_data.get("coalition")

    lines: List[str] = ["Sire — the state of Europe, plainly told.", ""]

    # ── The wars ──
    wars_context: List[Dict] = []
    if war_rows:
        for row in war_rows:
            opponent = row.get("opponent_display") or row.get("opponent", "?")
            score = int(row.get("war_score", 0))
            trend = str(row.get("trend", "stable"))
            phrase = _war_trajectory_phrase(score, trend)
            battles = int(row.get("battles_fought", 0))
            duration = int(row.get("duration", 0))
            lines.append(
                f"  Against {opponent}: the war {phrase} ({score:+d}) — "
                f"{battles} battle{'s' if battles != 1 else ''} across "
                f"{duration} turn{'s' if duration != 1 else ''}.")
            # NA-1: name each belligerent's design so the war has a WHY —
            # a coalition row carries every participant in `opponents`.
            from backend.display_names import display_nation
            from backend.game_logic.agendas import build_agenda_payload
            participants = [n for n in (row.get("opponents")
                                        or [row.get("opponent", "")]) if n]
            agenda_payloads = {}
            for participant in participants:
                payload = build_agenda_payload(participant, world)
                if payload:
                    agenda_payloads[participant] = payload
                    lines.append(
                        f"    {display_nation(participant)}'s design: "
                        f"{payload['title']} — {payload['stance_line']}")
            wars_context.append({"opponent": row.get("opponent", ""),
                                 "war_score": score, "trend": trend,
                                 "agendas": agenda_payloads})
    else:
        lines.append("  France wages no war — a rare and precious quiet.")
    for row in armistice_rows:
        opponent = row.get("opponent", "?")
        remaining = int(row.get("armistice_remaining", 0))
        projected = str(row.get("armistice_projected_outcome", "peace"))
        lines.append(
            f"  Armistice with {opponent}: {remaining} "
            f"turn{'s' if remaining != 1 else ''} remain — the truce "
            f"points toward {projected}.")

    # ── The coalition's intent (the posture, surfaced at last) ──
    threat = int(getattr(world, "threat_level", 0))
    tier = str(get_threat_tier(threat))
    active_coalition = getattr(world, "active_coalition", None)
    if active_coalition:
        posture = str(active_coalition.get("strategic_posture")
                      or get_coalition_posture(world))
        leader = active_coalition.get("leader", "")
        name = active_coalition.get("name", "the Coalition")
        lines.append("")
        lines.append(
            f"  {name} stands against us, led by {leader} — its posture "
            f"is {posture.upper()}. (Threat {threat}, {tier}.)")
    else:
        posture = str(get_coalition_posture(world))
        lines.append("")
        lines.append(
            f"  No coalition stands against us. Europe's alarm reads "
            f"{threat} ({tier}).")

    # ── What alarmed Europe this turn (top 3, already itemized) ──
    sources = sorted(
        (s for s in (getattr(world, "threat_sources_this_turn", []) or [])
         if isinstance(s, dict)),
        key=lambda s: -abs(int(s.get("amount", 0))))[:3]
    sources_context: List[Dict] = []
    if sources:
        rendered = []
        for s in sources:
            key = str(s.get("source", ""))
            amount = int(s.get("amount", 0))
            label = _THREAT_SOURCE_LABELS.get(
                key, key.replace("_", " ").title())
            sign = "+" if amount >= 0 else ""
            rendered.append(f"{label} ({sign}{amount})")
            sources_context.append(
                {"source": key, "label": label, "amount": amount})
        lines.append(f"  What stirred Europe this turn: "
                     f"{'; '.join(rendered)}.")

    # ── The vassals (loyalty, drift, cause) ──
    vassal_context: List[Dict] = []
    own_vassals = sorted(
        ((n, v) for n, v in (getattr(world, "vassals", {}) or {}).items()
         if v.get("lord") == player),
        key=lambda kv: int(kv[1].get("loyalty", 100)))
    if own_vassals:
        lines.append("")
        from backend.game_logic.vassal import AUTONOMY_DRIFT
        for name, record in own_vassals[:4]:
            loyalty = int(record.get("loyalty", 0))
            drift = AUTONOMY_DRIFT.get(record.get("autonomy", 1), 0)
            trend = ("rising" if drift > 0
                     else "falling" if drift < 0 else "steady")
            reason = _recent_vassal_reason(world, name)
            line = f"  {name}: loyalty {loyalty}, {trend}"
            if reason:
                line += f" — {reason}"
            lines.append(line + ".")
            vassal_context.append({"vassal": name, "loyalty": loyalty,
                                   "trend": trend, "reason": reason})

    # ── The one recommendation ──
    recommendation = _build_situation_recommendation(
        world, player, war_rows, coalition_info, posture)
    options: List[Dict] = []
    if recommendation:
        lines.append("")
        lines.append(f"My counsel, Sire: {recommendation['text']}")
        if recommendation["kind"] == "open_proposal":
            options.append({
                "label": recommendation["label"],
                "description": recommendation["description"],
                "action": "expand_options",
                "terms": {"target_nation": recommendation["target_nation"]},
            })
        else:
            options.append({
                "label": recommendation["label"],
                "description": recommendation["description"],
                "action": "execute_suggestion",
                "terms": {"suggestion": dict(recommendation)},
            })
    else:
        lines.append("")
        lines.append("My counsel, Sire: hold our course — Europe offers "
                     "no opening worth the ink today.")
    options.append({"label": "Thank you", "description": "Dismiss.",
                    "action": "dismiss"})

    return {
        "type": "advisory",
        "target_nation": "",
        "talleyrand_text": "\n".join(lines),
        "options": options,
        "context": {
            "advisory_type": "assess_situation",
            "situation_summary": "The war room assessment.",
            "wars": wars_context,
            "posture": posture,
            "threat_level": threat,
            "threat_tier": tier,
            "threat_sources": sources_context,
            "vassals": vassal_context,
            "recommendation": (dict(recommendation)
                               if recommendation else None),
            "confidence_level": "high",
            "action_hints": ([recommendation["label"]]
                             if recommendation else []),
        },
        "turn_created": int(world.current_turn),
        "blocking": False,
    }


# ═══════════════════════════════════════════════════════
# NATION ASSESSMENT
# ═══════════════════════════════════════════════════════

def _assess_nation(nation: str, world) -> Dict:
    """Assess a specific nation — relations, military, diplomatic posture."""
    player_nation = get_player_nation(world)
    diplo_key = world._make_diplo_key(player_nation, nation)
    state = world.get_diplomatic_state(player_nation, nation)
    relation = int(world.nation_relations.get(diplo_key, 0))
    advantage = _get_military_advantage(nation, world)
    diplomat = world.diplomats.get(nation)
    diplomat_desc = ""
    if diplomat:
        personality_word = _DIPLOMAT_DESCRIPTORS.get(diplomat.personality, "unknown")
        diplomat_desc = (
            f"{diplomat.name} is {personality_word} — "
            f"skill {int(diplomat.skill)}. "
        )

    player_war_score = get_war_score_for(world, player_nation, nation)

    state_text = _STATE_DISPLAY.get(state, state.lower())
    summary = _get_nation_summary(nation, world)

    # R130: Confidence based on fog of war visibility of target nation's regions
    target_regions = [r for r in world.regions.values() if getattr(r, 'controller', '') == nation]
    if target_regions:
        visible_count = sum(
            1 for r in target_regions
            if world.get_region_intel(r.name).visibility in ("full", "partial")
        )
        total_count = len(target_regions)
        visibility_ratio = visible_count / total_count
        if visibility_ratio >= 0.7:
            confidence = "high"
        elif visibility_ratio >= 0.3:
            confidence = "medium"
        else:
            confidence = "low"
    else:
        confidence = "medium"

    CONFIDENCE_PREAMBLES = {
        "high": "I am confident in this assessment, Sire. My sources are reliable. ",
        "medium": "Our intelligence is adequate, though gaps remain. ",
        "low": "I must warn you — my information is incomplete. Proceed with caution. ",
    }
    confidence_preamble = CONFIDENCE_PREAMBLES.get(confidence, "")

    if state == "WAR":
        situation = (
            f"{confidence_preamble}"
            f"We are {state_text} with {nation}, Sire. "
            f"War score stands at {int(player_war_score)} from our perspective. "
            f"Their military strength is {advantage} relative to ours. "
            f"{diplomat_desc}"
            f"{summary}"
        )
        if player_war_score > 20:
            recommendation = "We hold the advantage. Press for favorable terms or continue fighting."
            hints = [f"Propose peace with {nation}", "Continue military pressure"]
        elif player_war_score < -20:
            recommendation = "The war goes poorly. Consider armistice before it worsens."
            hints = [f"Propose armistice with {nation}", "Reinforce the front"]
        else:
            recommendation = "The war is balanced. A decisive battle could tip the scales either way."
            hints = ["Seek a decisive engagement", "Propose peace on equal terms"]
    else:
        situation = (
            f"{confidence_preamble}"
            f"We are {state_text} with {nation}, Sire. "
            f"Relations stand at {relation}. "
            f"Their military strength is {advantage} relative to ours. "
            f"{diplomat_desc}"
            f"{summary}"
        )
        if relation > 30:
            recommendation = f"{nation} is well-disposed toward us. An alliance is within reach."
            hints = [f"Propose alliance with {nation}", "Strengthen relations further"]
        elif relation > 0:
            recommendation = f"{nation} is cautiously favorable. Patience will yield dividends."
            hints = [f"Improve relations with {nation}", "Propose non-aggression pact"]
        elif relation > -30:
            recommendation = f"{nation} is wary but not hostile. Courtship could sway them."
            hints = [f"Court {nation}", f"Improve relations with {nation}"]
        else:
            recommendation = f"{nation} harbors deep resentment. Diplomatic progress will be slow and costly."
            hints = [f"Improve relations with {nation}", "Consider whether confrontation is inevitable"]

    # Build options
    options = []
    if state == "WAR":
        options.append({
            "label": "What terms would they accept?",
            "description": f"Assess feasibility of peace with {nation}.",
            "action": "expand_to_proposal",
        })
    else:
        options.append({
            "label": f"What should we do about {nation}?",
            "description": f"Get a recommendation for our next move with {nation}.",
            "action": "expand_to_proposal",
        })
    options.append({
        "label": "Thank you",
        "description": "Dismiss.",
        "action": "dismiss",
    })

    return {
        "type": "advisory",
        "target_nation": nation,
        "talleyrand_text": situation,
        "options": options,
        "context": {
            "situation_summary": summary,
            "recommendation": recommendation,
            "confidence_level": confidence,
            "action_hints": hints,
            "war_score": int(player_war_score) if state == "WAR" else 0,
            "relation": int(relation),
            "diplomatic_state": state,
            "military_advantage": advantage,
        },
        "turn_created": int(world.current_turn),
        "blocking": False,
    }


# ═══════════════════════════════════════════════════════
# THREAT COMPARISON
# ═══════════════════════════════════════════════════════

def _compare_threats(world) -> Dict:
    """Compare all nations as threats to France. Deterministic ranking."""
    threat_entries: List[Dict] = []
    player_nation = get_player_nation(world)
    player_strength = _get_fogged_strength(player_nation, world)
    active = set(world.get_active_nations())  # DLF-11
    active.update(getattr(world, 'vassals', {}).keys())  # Vassals always visible
    for nation in sorted(get_known_nations(world)):
        if nation not in active:
            continue
        diplo_key = world._make_diplo_key(player_nation, nation)
        state = world.get_diplomatic_state(player_nation, nation)
        relation = int(world.nation_relations.get(diplo_key, 0))
        strength = _get_fogged_strength(nation, world)

        # Threat score: higher = more threatening
        # Hostile relations, large army, at war all increase threat
        threat_score = 0
        threat_score -= relation  # negative relation = more threatening
        if state == "WAR":
            threat_score += 40
        elif state == "ARMISTICE":
            threat_score += 15
        if strength > player_strength * 0.5:
            threat_score += 20
        elif strength > player_strength:
            threat_score += 20

        threat_entries.append({
            "nation": nation,
            "state": state,
            "relation": relation,
            "strength": strength,
            "threat_score": threat_score,
        })

    # Sort by threat score descending
    threat_entries.sort(key=lambda e: -e["threat_score"])

    if not threat_entries:
        return {
            "type": "advisory",
            "target_nation": "",
            "talleyrand_text": "No foreign nations detected, Sire.",
            "options": [{"label": "Thank you", "description": "Dismiss.", "action": "dismiss"}],
            "context": {
                "situation_summary": "No foreign nations detected.",
                "recommendation": "The situation is stable.",
                "confidence_level": "low",
                "action_hints": [],
                "threat_ranking": [],
            },
            "turn_created": int(world.current_turn),
            "blocking": False,
        }

    top_threat = threat_entries[0]
    second_threat = threat_entries[1] if len(threat_entries) > 1 else None

    # Build Talleyrand's assessment
    lines = ["An astute question, Sire. Let me assess our position.\n"]
    for entry in threat_entries:
        n = entry["nation"]
        state_text = _STATE_DISPLAY.get(entry["state"], entry["state"].lower())
        adv = _get_military_advantage(n, world)
        lines.append(
            f"  {n} — {state_text.capitalize()}, relations {entry['relation']}. "
            f"Military: {adv}."
        )

    lines.append("")
    lines.append(
        f"My assessment: {top_threat['nation']} is the most pressing concern."
    )
    if second_threat and second_threat["threat_score"] > 20:
        lines.append(
            f"{second_threat['nation']} should not be ignored either."
        )
    lines.append(
        f"Address {top_threat['nation']} first, Sire — "
        f"{'end the war' if top_threat['state'] == 'WAR' else 'prevent hostilities'} "
        f"before it spirals."
    )

    talleyrand_text = "\n".join(lines)

    # Recommendation
    if top_threat["state"] == "WAR":
        recommendation = f"Prioritize the war with {top_threat['nation']}."
        hints = [
            f"Propose peace with {top_threat['nation']}",
            f"Win a decisive battle against {top_threat['nation']}",
        ]
    else:
        recommendation = f"Secure {top_threat['nation']} diplomatically before conflict erupts."
        hints = [
            f"Court {top_threat['nation']}",
            f"Propose non-aggression with {top_threat['nation']}",
        ]

    confidence = "high" if top_threat["threat_score"] > 50 else "medium"

    # Build options
    options = [
        {
            "label": f"Tell me more about {top_threat['nation']}",
            "description": f"Detailed assessment of {top_threat['nation']}.",
            "action": "expand_to_proposal",
        },
        {
            "label": "Thank you",
            "description": "Dismiss.",
            "action": "dismiss",
        },
    ]

    return {
        "type": "advisory",
        "target_nation": top_threat["nation"],
        "talleyrand_text": talleyrand_text,
        "options": options,
        "context": {
            "situation_summary": f"{top_threat['nation']} is the primary threat.",
            "recommendation": recommendation,
            "confidence_level": confidence,
            "action_hints": hints,
            "threat_ranking": [
                {"nation": e["nation"], "threat_score": int(e["threat_score"])}
                for e in threat_entries
            ],
        },
        "turn_created": int(world.current_turn),
        "blocking": False,
    }


# ═══════════════════════════════════════════════════════
# ACTION RECOMMENDATION
# ═══════════════════════════════════════════════════════

def _recommend_action(target_nation: str, world) -> Dict:
    """Recommend a diplomatic action for a specific nation."""
    player_nation = get_player_nation(world)
    diplo_key = world._make_diplo_key(player_nation, target_nation)
    state = world.get_diplomatic_state(player_nation, target_nation)
    relation = int(world.nation_relations.get(diplo_key, 0))
    advantage = _get_military_advantage(target_nation, world)

    player_war_score = get_war_score_for(world, player_nation, target_nation)

    if state == "WAR":
        if player_war_score > 20:
            text = (
                f"Sire, we hold the upper hand against {target_nation}. "
                f"War score: {int(player_war_score)}. I recommend pressing for peace "
                f"on favorable terms. Their {advantage} military position means they "
                f"cannot sustain this war indefinitely.\n\n"
                f"Alternatively, continue fighting to improve terms further — "
                f"though I caution against overreach. Empires are lost to greed "
                f"as often as to defeat."
            )
            recommendation = "Propose peace with strong terms."
            hints = [f"Propose peace with {target_nation}", "Continue fighting for better terms"]
            confidence = "high"
        elif player_war_score < -20:
            text = (
                f"Sire, I must speak plainly — the war with {target_nation} "
                f"does not favor us. War score: {int(player_war_score)}. "
                f"I strongly advise seeking an armistice before our position "
                f"deteriorates further.\n\n"
                f"Pride is a luxury we cannot afford when armies bleed."
            )
            recommendation = "Seek armistice immediately."
            hints = [f"Propose armistice with {target_nation}", "Reinforce the front lines"]
            confidence = "high"
        else:
            text = (
                f"Sire, the war with {target_nation} hangs in the balance. "
                f"War score: {int(player_war_score)}. Neither side commands a "
                f"decisive advantage.\n\n"
                f"I recommend the Tilsit model — win one more engagement, "
                f"then propose generous peace. Military pressure makes "
                f"diplomatic solutions cheaper."
            )
            recommendation = "Win a battle, then propose peace."
            hints = [
                f"Attack {target_nation}'s forces",
                f"Propose peace with {target_nation}",
            ]
            confidence = "medium"
    else:
        # At peace — recommend next diplomatic step
        if relation > 30 and state not in ("ALLIANCE", "DEFENSIVE_ALLIANCE"):
            text = (
                f"Sire, {target_nation} is well-disposed toward us — relations "
                f"stand at {relation}. The time is ripe to deepen our ties.\n\n"
                f"I recommend pursuing a formal alliance. The diplomatic cost "
                f"is modest and the strategic benefit immense."
            )
            recommendation = f"Pursue alliance with {target_nation}."
            hints = [f"Propose alliance with {target_nation}", "Improve relations further"]
            confidence = "high"
        elif relation > 0:
            text = (
                f"Sire, relations with {target_nation} are cautiously positive "
                f"at {relation}. We should nurture this goodwill.\n\n"
                f"I suggest improving relations through diplomatic missions. "
                f"A non-aggression pact would formalize our understanding."
            )
            recommendation = "Continue improving relations."
            hints = [f"Improve relations with {target_nation}", "Propose non-aggression pact"]
            confidence = "medium"
        elif relation > -40:
            text = (
                f"Sire, {target_nation} remains suspicious of our intentions — "
                f"relations at {relation}. Direct proposals would be rebuffed.\n\n"
                f"I recommend a patient courtship. Send diplomatic missions, "
                f"improve relations, and wait for the moment to present itself. "
                f"Diplomacy, like seduction, cannot be rushed."
            )
            recommendation = "Begin diplomatic courtship."
            hints = [f"Court {target_nation}", f"Improve relations with {target_nation}"]
            confidence = "medium"
        else:
            text = (
                f"Sire, {target_nation} harbors deep hostility — relations "
                f"at {relation}. Diplomacy will be a long and arduous road.\n\n"
                f"Frankly, Sire, some nations must be defeated before they "
                f"can be befriended. Consider whether military action might "
                f"achieve what words cannot."
            )
            recommendation = "Relations too hostile for diplomacy. Consider military options."
            hints = [f"Improve relations with {target_nation}", "Prepare for potential conflict"]
            confidence = "low"

    options = [
        {
            "label": "What should we do?",
            "description": f"Explore specific proposals for {target_nation}.",
            "action": "expand_to_proposal",
        },
        {
            "label": "Thank you",
            "description": "Dismiss.",
            "action": "dismiss",
        },
    ]

    return {
        "type": "advisory",
        "target_nation": target_nation,
        "talleyrand_text": text,
        "options": options,
        "context": {
            "situation_summary": _get_nation_summary(target_nation, world),
            "recommendation": recommendation,
            "confidence_level": confidence,
            "action_hints": hints,
        },
        "turn_created": int(world.current_turn),
        "blocking": False,
    }


def _recommend_action_overview(world) -> Dict:
    """General recommendation when no target nation specified."""
    return _diplomatic_overview(world)


# ═══════════════════════════════════════════════════════
# DIPLOMATIC OVERVIEW
# ═══════════════════════════════════════════════════════

def _diplomatic_overview(world) -> Dict:
    """Generate a full diplomatic overview across all nations."""
    lines = ["An overview, Sire:\n"]
    most_urgent_nation = None
    most_urgent_score = -999
    player_nation = get_player_nation(world)

    active = set(world.get_active_nations())  # DLF-11
    active.update(getattr(world, 'vassals', {}).keys())  # Vassals always visible
    for nation in sorted(get_known_nations(world)):
        if nation not in active:
            continue
        diplo_key = world._make_diplo_key(player_nation, nation)
        state = world.get_diplomatic_state(player_nation, nation)
        relation = int(world.nation_relations.get(diplo_key, 0))
        state_text = _STATE_DISPLAY.get(state, state.lower())
        summary = _get_nation_summary(nation, world)
        advantage = _get_military_advantage(nation, world)

        # Priority scoring: higher = more urgent to address
        urgency = 0
        urgency -= relation  # hostile = urgent
        if state == "WAR":
            urgency += 40
        elif state == "ARMISTICE":
            urgency += 15

        if urgency > most_urgent_score:
            most_urgent_score = urgency
            most_urgent_nation = nation

        war_note = ""
        if state == "WAR":
            player_ws = get_war_score_for(world, player_nation, nation)
            war_note = f" War score: {int(player_ws)}."

        lines.append(
            f"  {nation} — {state_text.capitalize()}. Relations: {relation}. "
            f"Military: {advantage}.{war_note} {summary}"
        )

    lines.append("")
    if most_urgent_nation:
        lines.append(
            f"My recommendation: address {most_urgent_nation} first, Sire. "
            f"Everything else can wait."
        )

    talleyrand_text = "\n".join(lines)

    recommendation = (
        f"Focus on {most_urgent_nation}."
        if most_urgent_nation
        else "The situation is stable."
    )
    hints = []
    if most_urgent_nation:
        state = world.get_diplomatic_state(player_nation, most_urgent_nation)
        if state == "WAR":
            hints = [f"Propose peace with {most_urgent_nation}", "Win a decisive battle"]
        else:
            hints = [f"Court {most_urgent_nation}", f"Improve relations with {most_urgent_nation}"]

    options = []
    if most_urgent_nation:
        options.append({
            "label": f"Tell me about {most_urgent_nation}",
            "description": f"Detailed assessment of {most_urgent_nation}.",
            "action": "expand_to_proposal",
        })
    options.append({
        "label": "Thank you",
        "description": "Dismiss.",
        "action": "dismiss",
    })

    return {
        "type": "advisory",
        "target_nation": most_urgent_nation or "",
        "talleyrand_text": talleyrand_text,
        "options": options,
        "context": {
            "situation_summary": "Overview of all diplomatic relations.",
            "recommendation": recommendation,
            "confidence_level": "medium",
            "action_hints": hints,
        },
        "turn_created": int(world.current_turn),
        "blocking": False,
    }


# ═══════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════

def _get_nation_total_strength(nation: str, world) -> int:
    """Sum total troop strength across all marshals of a nation."""
    total = 0
    for marshal in world.marshals.values():
        if marshal.nation == nation and marshal.strength > 0:
            total += marshal.strength
    return int(total)


def _get_nation_visibility(nation: str, world) -> str:
    """Get fog visibility tier for a nation's forces (R65 fog fix).

    Imports the canonical helper from diplomatic_ledger.
    """
    from backend.game_logic.diplomatic_ledger import _get_nation_visibility as _ledger_vis
    return _ledger_vis(nation, world)


def _get_fogged_strength(nation: str, world) -> int:
    """Get fog-filtered numeric strength estimate for threat scoring.

    FULL/PARTIAL: exact raw strength.
    STALE: mid-point of display band (rough estimate).
    UNKNOWN: default estimate of 30000 (mid-range assumption).

    This prevents fog-of-war leaks in threat scoring calculations.
    """
    raw = _get_nation_total_strength(nation, world)
    vis = _get_nation_visibility(nation, world)

    if vis in ("full", "partial"):
        return raw

    if vis == "stale":
        # Return band mid-points matching _format_army_strength bands
        if raw < 10000:
            return 5000
        elif raw < 30000:
            return 20000
        elif raw < 60000:
            return 45000
        elif raw < 100000:
            return 80000
        else:
            return 120000

    # UNKNOWN: use a default mid-range estimate
    return 30000


def _get_military_advantage(nation: str, world) -> str:
    """Compare a nation's total military strength to France's.

    Returns fog-filtered qualitative assessment. FULL visibility gives
    exact ratios; lower tiers give vaguer descriptions (R65 fog fix).
    """
    nation_strength = _get_nation_total_strength(nation, world)
    player_strength = _get_nation_total_strength(get_player_nation(world), world)
    vis = _get_nation_visibility(nation, world)

    # With unknown visibility, we can't assess military strength
    if vis == "unknown":
        return "unknown"

    if player_strength == 0:
        # AUD-g: "comparable" for the both-annihilated case (vocabulary parity
        # with the full bands; "even" was ungrammatical in the templates).
        return "overwhelming" if nation_strength > 0 else "comparable"

    ratio = nation_strength / player_strength

    # Stale visibility: only broad bands (collapse slight/even/disadvantage)
    if vis == "stale":
        if ratio > 1.3:
            return "considerable"
        elif ratio > 0.7:
            return "comparable"
        else:
            return "modest"

    # PARTIAL or FULL: full detail.
    # AUD-g: a symmetric ladder CENTRED on parity (ratio 1.0). The old bands
    # were shifted so "even" landed at ratio 0.5-0.75 (a real DISadvantage,
    # never true parity — the dead "even" tier), true parity was labelled
    # "slight", and "disadvantage" was ungrammatical in the sentence templates
    # ("their military strength is disadvantage relative to ours"). Every word
    # now reads correctly as "is {X} relative to ours" and "their {X} military
    # position". Thresholds are multiplicatively symmetric (0.87 ≈ 1/1.15,
    # 0.67 ≈ 1/1.5).
    if ratio > 1.5:
        return "overwhelming"
    elif ratio > 1.15:
        return "superior"
    elif ratio > 0.87:
        return "comparable"
    elif ratio > 0.67:
        return "inferior"
    else:
        return "overmatched"


def _get_nation_summary(nation: str, world) -> str:
    """One-liner summary for a nation's diplomatic posture."""
    player_nation = get_player_nation(world)
    diplo_key = world._make_diplo_key(player_nation, nation)
    state = world.get_diplomatic_state(player_nation, nation)
    relation = int(world.nation_relations.get(diplo_key, 0))
    diplomat = world.diplomats.get(nation)

    # Check for alliances with other nations (coalition risk)
    allied_with = []
    active = set(world.get_active_nations())  # DLF-11
    active.update(getattr(world, 'vassals', {}).keys())  # Vassals always visible
    for other in get_known_nations(world):
        if other not in active or other == nation:
            continue
        other_state = world.get_diplomatic_state(nation, other)
        if other_state in ("ALLIANCE", "DEFENSIVE_ALLIANCE"):
            allied_with.append(other)

    if state == "WAR":
        if allied_with:
            return f"Embattled, but allied with {', '.join(allied_with)}."
        return "At war with no allies to call upon." if relation < -40 else "Fighting, but not beyond reason."
    elif state in ("ALLIANCE", "DEFENSIVE_ALLIANCE"):
        return "A reliable partner — for now."
    elif state == "VASSAL":
        return "Subordinate to our will."
    elif relation > 20:
        if allied_with:
            return f"Friendly, but bound to {', '.join(allied_with)}."
        return "Amenable to deeper cooperation."
    elif relation > -20:
        if diplomat and diplomat.personality == "schemer":
            return "Watching, waiting, calculating."
        return "Neutral — could go either way."
    else:
        if allied_with:
            return f"Hostile, and allied with {', '.join(allied_with)}. A dangerous combination."
        return "Hostile. Tread carefully."
