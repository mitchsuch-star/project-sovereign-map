"""
Diplomatic Ledger — 4-section backend builder (Session 8A)

Builds a structured dict for the Godot Diplomatic Ledger screen.
All values int()-wrapped per CLAUDE.md rule: "All numbers to Godot: int()".

Fog-filtered: army_strength uses diplomatic intelligence model —
national-level visibility based on best marshal visibility per nation.
"""

from typing import Dict, Any, List

from backend.models.intel import (
    FULL, PARTIAL, STALE, UNKNOWN,
    VISIBILITY_PRIORITY,
)
from backend.game_logic.agendas import build_agenda_payload
from backend.game_logic.diplomatic_templates import get_treaty_harshness_for_consumer
from backend.game_logic.instruments import (
    build_instruments_line,
    build_subsidy_payload,
)
from backend.game_logic.intent import (
    build_france_mirror_payload,
    build_intent_payload,
)


def _build_instruments_line(nation: str, world):
    """Thin adapter keeping the nations-tab call site tidy."""
    return build_instruments_line(world, nation)

ARMISTICE_DURATION = 5  # Must match diplomacy.py

# TH3: Human-readable threat source labels (module-level to avoid re-creation per call)
_THREAT_SOURCE_LABELS = {
    "battle_win": "Won a battle",
    "battle_loss": "Lost a battle",
    "capital_capture": "Captured an enemy capital",
    "region_capture": "Conquered territory",
    "war_declaration": "Declared war",
    "treaty_vassalization": "Vassalized via treaty",
    "conquest_vassalization": "Vassalized by conquest",
    "decisive_victory": "Won a decisive battle",
    "decay": "Natural threat decay",
    "treaty_annex": "Annexed territory via treaty",
    "territory_return": "Returned territory",
    "generous_peace": "Offered generous peace",
    "diplomatic_downgrade": "Downgraded diplomatic relations",
    "vassal_rebellion": "Vassal rebellion",
    "voluntary_vassal_release": "Released vassal voluntarily",
    "region_control_50": "Controls 50%+ of map",
    "region_control_40": "Controls 40%+ of map",
    "region_control_30": "Controls 30%+ of map",
    # Legacy-world keys (the 19-region fixture keeps its 60/70/80 gates, N1)
    "region_control_80": "Controls 80%+ of map",
    "region_control_70": "Controls 70%+ of map",
    "region_control_60": "Controls 60%+ of map",
    # Econ spec review Q2: the first passive contributor that reads the ARMY
    # rather than the map. Named so the player can see that re-arming is
    # visible to Europe — it is the counterweight to "The Levy is Open".
    "military_establishment": "Keeps Europe's largest army",
    # NA-3 §5.8: the post-peace grudge names itself on the threat panel
    "agenda_grudge": "Denied national designs",
    # NA-5 §8: a defied ultimatum names itself too
    "ultimatum_defied": "Defied an ultimatum",
    # NA-6 §11.9: the standing wound left by a sponsored proclamation.
    # Since NA-6d each formation emits under its own source key
    # (`formation_grudge:<tag>`) resolved by `_threat_source_label` below;
    # this generic row is the fallback for a formation with no authored
    # `grudge_label` (and for any pre-NA-6d serialized threat row).
    "formation_grudge": "Nations raised from their lands",
    "schemer_peace_rejection": "Scorned a peace overture",
}


def _threat_source_label(world, source_key: str) -> str:
    """Panel label for one threat source key — the static map, plus the
    NA-6d dynamic arm: `formation_grudge:<tag>` resolves the formation's
    authored `grudge_label` ("The Polish Question"), falling back to the
    generic formation row, so the panel names each grievance (§11.9)."""
    if source_key.startswith("formation_grudge:"):
        from backend.game_logic.formations import formation_grudge_source_label
        label = formation_grudge_source_label(world, source_key)
        return label or _THREAT_SOURCE_LABELS["formation_grudge"]
    return _THREAT_SOURCE_LABELS.get(
        source_key, source_key.replace("_", " ").title())


def build_diplomatic_ledger(world) -> Dict[str, Any]:
    """
    Build the diplomatic ledger dict for Godot rendering.

    Args:
        world: WorldState instance

    Returns:
        Dict with nations, treaties, balance_of_europe,
        talleyrand sections.
        All numeric values int()-wrapped.
    """
    from backend.game_logic.settlement_presentation import (
        build_peace_settlement_history,
        recent_settlement_summaries,
    )

    player_nation = getattr(world, "player_nation", "France")
    return {
        "current_turn": int(world.current_turn),
        "nations": _build_nations(world),
        "vassals": _build_vassals(world),
        "treaties": _build_treaties(world),
        # SC-23 legacy fields preserved for tests / save compatibility;
        # `peace_settlement_history` is the merged surface that the
        # ledger header renders. Older clients reading the legacy fields
        # see the same data split by family.
        "recent_peace_ratifications": _build_recent_peace_ratifications(world),
        "recent_settlements": recent_settlement_summaries(
            world, player_nation,
        ),
        "peace_settlement_history": build_peace_settlement_history(
            world, player_nation,
        ),
        "balance_of_europe": _build_balance_of_europe(world),
        "talleyrand": _build_talleyrand(world),
        "war_bargains": _build_war_bargains(world),
        # AI-1b (docs/AI_INTENT_SPEC.md §3.5): the player's own row —
        # Europe's derived reading of France. None on legacy/bare worlds
        # (renderers omit).
        "france_mirror": build_france_mirror_payload(world),
        # AI-3r (§2.5-3): France's own exposure — display only, never a
        # gate on the player's orders (gate Q5). None on legacy/bare.
        "france_exposure": _build_france_exposure(world),
    }


# ============================================================================
# FOG HELPER: National-level visibility
# ============================================================================

def _get_nation_visibility(nation_name: str, world) -> str:
    """Get the best visibility tier across all marshals belonging to a nation.

    Diplomatic intelligence: Talleyrand's ambassadors know court gossip and
    troop levies — national-level picture, not per-army positions.

    Returns the best VisibilityTier (FULL > PARTIAL > STALE > UNKNOWN).
    If nation has no marshals, returns UNKNOWN.
    """
    best_vis = UNKNOWN
    best_priority = VISIBILITY_PRIORITY.get(UNKNOWN, 0)

    for marshal in world.marshals.values():
        if marshal.nation != nation_name:
            continue
        if marshal.strength <= 0:
            continue

        # Get visibility for the region this marshal is in
        intel = world.get_region_intel(marshal.location)
        vis = intel.visibility
        vis_priority = VISIBILITY_PRIORITY.get(vis, 0)

        if vis_priority > best_priority:
            best_vis = vis
            best_priority = vis_priority

            # Early exit if we found FULL — can't get better
            if best_vis == FULL:
                return FULL

    return best_vis


def _format_army_strength(total_strength: int, visibility: str) -> str:
    """Format army strength display based on visibility tier.

    NONE (UNKNOWN): "Unknown"
    STALE: Named bands
    PARTIAL: Approximate (~nearest 5k)
    FULL: Exact aggregate
    """
    if visibility == UNKNOWN:
        return "Unknown"

    if visibility == STALE:
        if total_strength < 10000:
            return "Negligible"
        elif total_strength < 30000:
            return "Minor Force"
        elif total_strength < 60000:
            return "Considerable"
        elif total_strength < 100000:
            return "Powerful"
        else:
            return "Dominant"

    if visibility == PARTIAL:
        rounded = round(total_strength / 5000) * 5000
        rounded = max(rounded, 5000) if total_strength > 0 else 0
        return f"~{int(rounded):,} men"

    # FULL
    return f"{int(total_strength):,} men"


def _build_bloc_stamp_context(world) -> Dict[str, Any]:
    """Precompute the shared D3 stamp context for all Nation rows."""
    coalition = getattr(world, 'active_coalition', None)
    coalition_members = set(coalition.get("members", []) or []) if coalition else set()
    context = {
        "band": 0,
        "hegemon": None,
        "share": 0.0,
        "bloc_info": {},
        "bloc_members": set(),
        "coalition_members": coalition_members,
    }

    try:
        from backend.game_logic.coalition import (
            _hegemony_signal_band,
            _identify_max_bloc_share,
            describe_hegemon_bloc,
        )
        hegemon, share = _identify_max_bloc_share(world)
        band = _hegemony_signal_band(float(share)) if hegemon else 0
        if not hegemon or band <= 0:
            return context
        context["band"] = int(band)
        context["hegemon"] = hegemon
        context["share"] = float(share)
        context["bloc_info"] = describe_hegemon_bloc(world, hegemon, float(share))
        context["bloc_members"] = set(world.get_bloc_members(hegemon))
    except Exception:
        return context
    return context


def _build_bloc_stamp(nation: str, world, context: Dict[str, Any]):
    """Return the transient D3 Nations-tab bloc stamp for a nation.

    The payload is display-only and never serialized. Priority follows the
    D3 contract: formal coalition membership dominates bloc labels, then
    vassal/neutral fallback tags only appear once Balance naming is active.
    """
    if nation in context.get("coalition_members", set()):
        return {"label": "Coalition Member", "kind": "coalition", "priority": 100}

    if int(context.get("band", 0) or 0) <= 0:
        return None

    if nation in context.get("bloc_members", set()):
        bloc_info = context.get("bloc_info", {}) or {}
        label = bloc_info.get("bloc_label") or bloc_info.get("descriptive_label")
        if not label:
            label = f"{context.get('hegemon', 'Hegemon')}-led alignment"
        if bool(bloc_info.get("is_proper_bloc_name")):
            return {"label": str(label), "kind": "proper_bloc", "priority": 80}
        return {"label": str(label), "kind": "descriptive_bloc", "priority": 70}

    vassal_record = getattr(world, 'vassals', {}).get(nation)
    if vassal_record:
        lord = str(vassal_record.get("lord", "") or "")
        if lord:
            return {"label": f"Vassal of {lord}", "kind": "vassal", "priority": 40}

    return {"label": "Neutral", "kind": "neutral", "priority": 10}


# ============================================================================
# TAB 1: NATIONS
# ============================================================================

def _build_nations(world) -> List[Dict[str, Any]]:
    """Build nations tab: per-nation diplomatic overview."""
    player = world.player_nation
    active = set(world.get_active_nations())  # DLF-11
    all_nations = [n for n in getattr(world, 'enemy_nations', []) if n in active]
    nations = []
    bloc_stamp_context = _build_bloc_stamp_context(world)

    for nation in all_nations:
        diplo_key = world._make_diplo_key(player, nation)
        diplomatic_state = world.diplomatic_states.get(diplo_key, "PEACE")
        relation = world.nation_relations.get(diplo_key, 0) or 0

        # Diplomat info
        diplomats = getattr(world, 'diplomats', {})
        diplomat = diplomats.get(nation)
        diplomat_info = None
        if diplomat:
            diplomat_info = {
                "name": diplomat.name,
                "personality": diplomat.personality,
                "skill": int(diplomat.skill or 0),
            }

        # Army strength with fog
        total_strength = sum(
            m.strength for m in world.marshals.values()
            if m.nation == nation and m.strength > 0
        )

        if nation == player:
            # Defensive guard: enemy_nations should never include the player, but
            # if it does, show "Exact" for own army strength rather than fog-filtered.
            army_strength = f"{int(total_strength):,} men"
        else:
            visibility = _get_nation_visibility(nation, world)
            army_strength = _format_army_strength(total_strength, visibility)

        # Regions controlled (always visible — map control is public).
        # GR8: cached helper, not a raw scan — this sits inside the
        # per-nation loop (O(N×R) before the Aug 2026 health-check audit).
        regions_controlled = len(world.get_nation_regions(nation))

        # PF-9: Active treaty between the PLAYER and this nation only, hidden
        # while at WAR. Treaties are keyed by the canonical pair key, so the
        # player<->nation treaty (if any) is exactly active_treaties[diplo_key].
        # The old scan (`nation in treaty_nations`) leaked a THIRD-PARTY treaty
        # (e.g. Russia<->Sweden) onto this nation's row and ignored war state,
        # so a stale "[open_borders]" showed against a nation the player was at
        # WAR with. `_build_treaties` (Tab 2) still lists all treaties globally.
        active_treaties = []
        if diplomatic_state != "WAR":
            treaty = getattr(world, 'active_treaties', {}).get(diplo_key)
            if treaty:
                active_treaties.append(treaty.get("type", "unknown"))

        # Vassal eligibility mirrors the shipped `make_vassal` command:
        # treaty path from OPEN_BORDERS+ or conquest path from WAR. The ledger
        # only surfaces that affordance for minor courts so major powers do not
        # look like client-state targets.
        from backend.nation_config import _POWER_TIER_DEFAULT  # noqa: E402
        from backend.game_logic.diplomacy import VASSAL_MIN_STATES  # noqa: E402
        power_tier = world.get_power_tier(nation) or _POWER_TIER_DEFAULT
        vassals = getattr(world, 'vassals', {})
        is_vassal = nation in vassals
        release_cooldown = int(
            getattr(world, 'vassal_release_cooldowns', {}).get(nation, 0) or 0
        )
        vassal_preconditions = (
            not is_vassal
            and nation != player
            and diplomatic_state in VASSAL_MIN_STATES
            and release_cooldown <= 0
        )
        vassal_eligible = vassal_preconditions and power_tier == "minor"
        vassal_block_reason = None
        if vassal_preconditions and not vassal_eligible:
            vassal_block_reason = (
                "major_power" if power_tier == "major" else "non_minor_power"
            )

        # AI-AI relations: show diplomatic states with other AI nations
        # DPF-1: No fog gate — diplomatic relations are public knowledge
        # DLF-3: Filter to notable states only — hide PEACE to reduce display bloat
        from backend.game_logic.diplomacy import get_relation_descriptor  # noqa: E402
        ai_relations = []
        notable_states = {"WAR", "ALLIANCE", "DEFENSIVE_ALLIANCE", "OPEN_BORDERS", "NON_AGGRESSION"}
        for other_ai in all_nations:
            if other_ai == nation:
                continue
            ai_diplo_key = world._make_diplo_key(nation, other_ai)
            ai_state = world.diplomatic_states.get(ai_diplo_key, "PEACE")
            if ai_state not in notable_states:
                continue
            ai_relation_value = int(world.nation_relations.get(ai_diplo_key, 0) or 0)
            ai_relations.append({
                "nation": other_ai,
                "state": ai_state,
                "relation": ai_relation_value,
                "relation_descriptor": get_relation_descriptor(ai_relation_value),
            })

        # R17a: War score component breakdown for AT_WAR nations
        war_score_breakdown = None
        if diplomatic_state == "WAR":
            from backend.game_logic.diplomacy import calculate_war_score
            war_score_breakdown = calculate_war_score(
                player, nation, world, return_components=True
            )
            # int()-wrap all components for Godot
            if war_score_breakdown:
                war_score_breakdown = {
                    k: int(v) for k, v in war_score_breakdown.items()
                }

        # R17b: Proposal cooldowns remaining for this nation
        cooldowns = getattr(world, 'player_proposal_cooldowns', {})
        proposal_cooldowns = {}
        # Check nation-level cooldown (e.g. "Prussia": 3)
        nation_cd = cooldowns.get(nation, 0)
        if nation_cd > 0:
            proposal_cooldowns["nation"] = int(nation_cd)
        # Check per-type cooldowns (e.g. "Prussia_peace": 5)
        for cd_key, cd_val in cooldowns.items():
            if cd_key.startswith(f"{nation}_") and cd_val > 0:
                ptype = cd_key[len(nation) + 1:]
                proposal_cooldowns[ptype] = int(cd_val)

        # N5: Trade income from diplomatic state
        from backend.game_logic.diplomacy import TRADE_INCOME
        trade_income = int(TRADE_INCOME.get(diplomatic_state, 0))

        # N6: Relation descriptor
        from backend.game_logic.diplomacy import get_relation_descriptor
        relation_descriptor = get_relation_descriptor(relation)

        # N7: Relation trend (rising/falling/stable from history)
        relation_trend = "stable"
        relation_history = getattr(world, 'relation_history', {})
        history_list = relation_history.get(diplo_key, [])
        if len(history_list) >= 2:
            delta = relation - history_list[-1]
            if delta > 2:
                relation_trend = "rising"
            elif delta < -2:
                relation_trend = "falling"

        nations.append({
            "name": nation,
            "diplomatic_state": diplomatic_state,
            "relation": int(relation),
            "relation_descriptor": relation_descriptor,
            "relation_trend": relation_trend,
            "diplomat": diplomat_info,
            "army_strength": army_strength,
            "regions_controlled": int(regions_controlled),
            "active_treaties": active_treaties,
            "vassal_eligible": vassal_eligible,
            "vassal_block_reason": vassal_block_reason,
            "power_tier": power_tier,
            "ai_relations": ai_relations,
            "war_score_breakdown": war_score_breakdown,
            "proposal_cooldowns": proposal_cooldowns if proposal_cooldowns else None,
            "trade_income": trade_income,
            "bloc_stamp": _build_bloc_stamp(nation, world, bloc_stamp_context),
            # NA-1: the nation's active design — un-fogged like relations
            # (DPF-1); None when no agenda is live (renderers omit).
            "agenda": build_agenda_payload(nation, world),
            # AI-1: the nation's intent — want / against / price, D4's
            # fully-open ladder (timing is the only thing not shown).
            # None when indifferent with no design (renderers omit).
            "intent": build_intent_payload(nation, world),
            # AI-2b/2e: every live D5 instrument this court is party to
            # (sponsorships, compacts, bargains, guarantees, an open
            # allegiance auction) — one composed line, None omits.
            "compacts": _build_instruments_line(nation, world),
            # AI-4c (§4.2b): the court's war-weariness, EXPLICITLY labelled
            # as national exhaustion across ALL its wars, with the
            # belligerent list — "let them bleed while France rearms"
            # made readable. None omits (at peace, zero exhaustion).
            "war_weariness": _build_war_weariness_line(nation, world),
            # AI-3r (§2.5-2): the court's exposure — free field army vs
            # the rear-security reserve, the row that makes the war
            # council's refusals playable. None omits (fogged/army-less).
            "exposure": _build_exposure_line(nation, world),
        })

    return nations


def _build_exposure_line(nation: str, world):
    """AI-3r §2.5-2: {standing, reserve, free, worst_threat, line} or None.

    Fogged to PARTIAL+ exactly like the weariness row — the reserve is an
    army-disposition fact, not a diplomatic one. Europe-scoped: the
    legacy/bare ledger stays byte-identical (the deckless-neutral idiom).
    """
    if getattr(world, "sovereign_map", "legacy") != "europe":
        return None
    vis = _get_nation_visibility(nation, world)
    partial_priority = VISIBILITY_PRIORITY.get(PARTIAL, 3)
    if VISIBILITY_PRIORITY.get(vis, 0) < partial_priority:
        return None
    from backend.game_logic.war_council import get_exposure_view
    view = get_exposure_view(world, nation)
    if view["standing"] <= 0:
        return None
    from backend.game_logic.formations import formed_display_name
    if view["reserve"] > 0 and view["worst_threat"]:
        threat_display = formed_display_name(world, view["worst_threat"])
        line = (f"Free field army: {view['free']:,} of "
                f"{view['standing']:,} — the rest held against "
                f"{threat_display}")
    else:
        line = (f"Free field army: the whole {view['standing']:,} — "
                f"no armed neighbour compels a reserve")
    return {
        "standing": int(view["standing"]),
        "reserve": int(view["reserve"]),
        "free": int(view["free"]),
        "worst_threat": view["worst_threat"],
        "line": line,
    }


def _build_france_exposure(world):
    """AI-3r §2.5-3: France's own exposure row — the same derivation the
    war council applies to every court, RENDERED to the player and never
    gating their orders (gate Q5's pinned asymmetry). Un-fogged (own
    forces); None on legacy/bare worlds and with no army standing."""
    if getattr(world, "sovereign_map", "legacy") != "europe":
        return None
    player = getattr(world, "player_nation", "France")
    from backend.game_logic.war_council import get_exposure_view
    view = get_exposure_view(world, player)
    if view["standing"] <= 0:
        return None
    from backend.game_logic.formations import formed_display_name
    if view["reserve"] > 0 and view["worst_threat"]:
        threat_display = formed_display_name(world, view["worst_threat"])
        line = (f"Free field army: {view['free']:,} of "
                f"{view['standing']:,} — prudence holds the rest against "
                f"{threat_display}. Advisory only, Sire: your marshals "
                f"march where you send them.")
    else:
        line = (f"Free field army: the whole {view['standing']:,} — no "
                f"armed neighbour compels a reserve.")
    return {
        "standing": int(view["standing"]),
        "reserve": int(view["reserve"]),
        "free": int(view["free"]),
        "worst_threat": view["worst_threat"],
        "line": line,
    }


def _build_war_weariness_line(nation: str, world):
    """AI-4c's display half: {value, trend, at_war_with, line} or None.

    The §4.2b contract: either the row is per-war, or it is explicitly
    labelled as NATIONAL exhaustion across all wars — this is the labelled
    arm, with the wars named beside it. Fogged to PARTIAL+ like the
    coalition tab's member exhaustion (army-internal, not a diplo fact).
    """
    vis = _get_nation_visibility(nation, world)
    partial_priority = VISIBILITY_PRIORITY.get(PARTIAL, 3)
    if VISIBILITY_PRIORITY.get(vis, 0) < partial_priority:
        return None
    we = int((getattr(world, 'war_exhaustion', {}) or {}).get(nation, 0) or 0)
    at_war = sorted(world.get_nations_at_war_with(nation))
    if we <= 0 and not at_war:
        return None
    prev_we = int(getattr(world, '_prev_war_exhaustion', {}).get(nation, 0) or 0)
    if we > prev_we:
        trend = "rising"
    elif we < prev_we:
        trend = "falling"
    else:
        trend = "stable"
    from backend.game_logic.formations import formed_display_name
    at_war_display = [formed_display_name(world, n) for n in at_war]
    if at_war_display:
        line = (f"National exhaustion across all wars: {we} ({trend}) — "
                f"at war with {', '.join(at_war_display)}")
    else:
        line = f"National exhaustion across all wars: {we} ({trend})"
    return {
        "value": we,
        "trend": trend,
        "at_war_with": at_war,
        "line": line,
    }


# ============================================================================
# TAB: VASSALS (client states — UI-6 interaction sweep)
# ============================================================================

def _build_vassals(world) -> Dict[str, Any]:
    """Build the Vassals tab: the player's client states with the full
    decision picture (loyalty / autonomy / tribute / next-turn forecast)
    plus the SAME honest-availability action rows the F1 wizard consumes
    (`get_available_diplomatic_actions`), so the ledger's chips can never
    disagree with the executor gates.

    Pull-only UI payload (built once per ledger open — not a hot path).
    Foreign satellites stay on the Nations tab via the bloc stamp; this
    tab is the player's own clients.
    """
    from backend.game_logic.diplomacy import get_available_diplomatic_actions
    from backend.game_logic.vassal import (
        AUTONOMY_NAMES,
        CONTRIBUTION_DISAFFECTED_BELOW,
        CONTRIBUTION_LOYAL_MIN,
        INVEST_LOYALTY_GAIN,
        forecast_vassal_loyalty,
        recovery_hint_for_grip,
    )
    from backend.models.authority import get_authority_lever_multiplier

    player = getattr(world, "player_nation", "France")
    vassal_records = getattr(world, "vassals", {}) or {}

    dm = world.dialogue_manager
    actions_blocked = bool(
        dm.is_hard_stop() or dm.has_current_turn_offers() or dm.is_local_planning()
    )

    # VS-R lever blunting is per-lord — hoist out of the loop. The gain
    # fields mirror the executor math EXACTLY (invest_in_vassal /
    # change_vassal_autonomy: int(gain * mult)) so the chips' terms copy can
    # never promise a +10 the executor blunts to +4 in the spiral band.
    lever_mult = get_authority_lever_multiplier(world, player)
    invest_gain = int(INVEST_LOYALTY_GAIN * lever_mult)
    autonomy_up_gain = int(10 * lever_mult)
    gains_blunted = lever_mult < 1.0

    rows: List[Dict[str, Any]] = []
    total_tribute = 0
    for name in sorted(vassal_records.keys()):
        record = vassal_records[name]
        if record.get("lord") != player:
            continue

        loyalty = int(record.get("loyalty", 50))
        autonomy = int(record.get("autonomy", 1))
        tribute_rate = float(record.get("tribute_rate", 0.75))
        vassal_income = sum(
            world.regions[r].get_effective_income()
            for r in world.get_nation_regions(name)
            if r in world.regions
        )
        tribute = int(vassal_income * tribute_rate)
        total_tribute += tribute

        # Next-turn loyalty forecast — the shared steady-state helper
        # (forecast_vassal_loyalty) mirrors process_vassal_loyalty term for
        # term minus only the transient battle term, and includes the
        # standing gold-subsidy clause the first cut of this tab missed.
        fc = forecast_vassal_loyalty(world, player, name)
        forecast = fc["forecast"]
        trend = fc["trend"]
        garrison_present = fc["garrison_present"]
        garrison_bonus = fc["garrison_bonus"]
        capital = fc["capital"]
        grip = fc["grip"]

        # VS-4 contribution tier (military teeth of loyalty).
        if loyalty >= CONTRIBUTION_LOYAL_MIN:
            contribution = "loyal"
        elif loyalty < CONTRIBUTION_DISAFFECTED_BELOW:
            contribution = "disaffected"
        else:
            contribution = "wavering"

        # Warning band mirrors get_vassal_warnings thresholds.
        if loyalty < 10:
            warning = "critical"
        elif loyalty < 20:
            warning = "urgent"
        elif loyalty < 40:
            warning = "warning"
        else:
            warning = ""

        rows.append({
            "name": name,
            "loyalty": int(loyalty),
            "autonomy_level": int(autonomy),
            "autonomy_name": AUTONOMY_NAMES.get(autonomy, "Satellite"),
            "tribute": int(tribute),
            "tribute_rate_pct": int(round(tribute_rate * 100)),
            "loyalty_forecast": int(forecast),
            "loyalty_trend": trend,
            "contribution": contribution,
            "warning": warning,
            "recovery_hint": (
                recovery_hint_for_grip(grip) if loyalty < 40 else ""
            ),
            "garrison_present": garrison_present,
            "garrison_bonus": int(garrison_bonus),
            "subsidy_bonus": int(fc["subsidy_bonus"]),
            "invest_gain": int(invest_gain),
            "autonomy_up_gain": int(autonomy_up_gain),
            "autonomy_down_loss": 15,
            "gains_blunted": gains_blunted,
            "capital": str(capital or ""),
            "regions": int(len(world.get_nation_regions(name))),
            "granted_regions": [
                str(r) for r in (record.get("granted_regions") or [])
            ],
            "path": str(record.get("path", "treaty")),
            "created_turn": int(record.get("created_turn", 0) or 0),
            "actions": get_available_diplomatic_actions(world, name),
        })

    return {
        "rows": rows,
        "count": int(len(rows)),
        "total_tribute": int(total_tribute),
        "actions_blocked": actions_blocked,
    }


# ============================================================================
# TAB 2: TREATIES
# ============================================================================

def _build_treaties(world) -> List[Dict[str, Any]]:
    """Build treaties tab: per active treaty."""
    player = world.player_nation
    treaties = []
    for pair_key, treaty in getattr(world, 'active_treaties', {}).items():
        nations = treaty.get("nations", [])
        nation_a = nations[0] if len(nations) > 0 else ""
        nation_b = nations[1] if len(nations) > 1 else ""

        clauses = []
        for clause in treaty.get("clauses", []):
            if isinstance(clause, dict):
                desc = clause.get("description")
                if not desc:
                    # Bug 6 fix: Generate human-readable description from clause fields
                    ctype = clause.get("type", "unknown")
                    amount = clause.get("amount", 0)
                    c_from = clause.get("from", "")
                    c_to = clause.get("to", "")
                    _CLAUSE_LABELS = {
                        "gold_lump": "Gold payment",
                        "gold_per_turn": "Gold/turn",
                        "manpower_per_turn": "Manpower/turn",
                        "ap_per_turn": "AP/turn",
                        "territory_cede": "Territory cession",
                        "infantry_manpower": "Infantry levy",
                        "cavalry_manpower": "Cavalry levy",
                        "artillery_manpower": "Artillery provision",
                        "open_borders": "Open borders",
                        "non_aggression": "Non-aggression",
                        "protection_promised": "Military protection",
                    }
                    label = _CLAUSE_LABELS.get(ctype, ctype.replace("_", " ").title())
                    if amount and c_from:
                        desc = f"{label}: {int(amount)} ({c_from} -> {c_to})"
                    elif amount:
                        desc = f"{label}: {int(amount)}"
                    else:
                        desc = label
                clauses.append(desc)
            else:
                clauses.append(str(clause))

        duration = treaty.get("duration", "permanent")
        if isinstance(duration, int):
            duration = int(duration)

        # R17c: Calculate ongoing gold/turn costs from treaty clauses
        gold_per_turn_costs = []
        for clause in treaty.get("clauses", []):
            if isinstance(clause, dict) and clause.get("type") == "gold_per_turn":
                gold_per_turn_costs.append({
                    "from": clause.get("from", ""),
                    "to": clause.get("to", ""),
                    "amount": int(clause.get("amount") or 0),
                })

        # T2: Turn signed
        turn_signed = int(treaty.get("turn_signed") or 0)

        # T3: Player vs AI-AI distinction
        involves_player = player in nations

        # T4: Armistice countdown
        armistice_remaining = None
        treaty_type = treaty.get("type", "unknown")
        if treaty_type == "armistice":
            armistice_turns = getattr(world, 'armistice_turns', {})
            pair_armistice = armistice_turns.get(pair_key, 0)
            armistice_remaining = int(max(0, ARMISTICE_DURATION - pair_armistice))

        treaties.append({
            "nation_a": nation_a,
            "nation_b": nation_b,
            "treaty_type": treaty_type,
            "clauses": clauses,
            "harshness": round(
                get_treaty_harshness_for_consumer(
                    treaty, consumer="diplomatic_ledger",
                ),
                2,
            ),
            "duration": duration,
            "cancel_cost": 1,
            "gold_per_turn": gold_per_turn_costs if gold_per_turn_costs else None,
            "turn_signed": turn_signed,
            "involves_player": involves_player,
            "armistice_remaining": armistice_remaining,
        })

    return treaties


def _build_recent_peace_ratifications(world) -> List[Dict[str, Any]]:
    """BPH-D 15.3: recent peace ratification summaries for Treaties tab."""
    recent = []
    from backend.game_logic.settlement_presentation import PEACE_HISTORY_DEFAULT_ROWS

    entries = list(getattr(world, "peace_ratification_log", []) or [])[
        -PEACE_HISTORY_DEFAULT_ROWS:
    ]
    for entry in reversed(entries):
        if entry.get("new_state", "PEACE") != "PEACE":
            continue

        target = str(entry.get("target_nation", "Unknown"))
        turn = int(entry.get("turn", 0) or 0)
        target_capital = str(entry.get("target_capital") or target)
        outcome = str(entry.get("war_outcome", "white_peace"))
        outcome_label = _format_peace_outcome_label(outcome)
        gained = _as_str_list(entry.get("territory_gained", []))
        lost = _as_str_list(entry.get("territory_lost", []))
        terms = _as_str_list(entry.get("terms_ratified", []))
        aftermath = _as_str_list(entry.get("political_aftermath", []))
        gold_received = int(entry.get("gold_received", 0) or 0)
        gold_paid = int(entry.get("gold_paid", 0) or 0)
        final_war_score = int(entry.get("final_war_score", 0) or 0)
        duration = int(entry.get("war_duration_turns", 0) or 0)
        casualties_france = int(entry.get("casualties_france", 0) or 0)
        casualties_enemy = int(entry.get("casualties_enemy", 0) or 0)

        summary_parts = [outcome_label]
        if gained:
            summary_parts.append(f"gained {', '.join(gained)}")
        if lost:
            summary_parts.append(f"lost {', '.join(lost)}")
        if gold_received:
            summary_parts.append(f"+{gold_received} gold")
        if gold_paid:
            summary_parts.append(f"-{gold_paid} gold")

        detail_lines = [
            f"War duration: {duration} turn{'s' if duration != 1 else ''}",
            f"Final war score: {final_war_score:+d}",
        ]
        if casualties_france or casualties_enemy:
            detail_lines.append(
                "Casualties: France "
                f"{casualties_france:,}; {target} {casualties_enemy:,}"
            )
        if terms:
            detail_lines.append(f"Terms: {'; '.join(terms)}")
        if aftermath:
            detail_lines.append(f"Political aftermath: {'; '.join(aftermath)}")

        recent.append({
            "headline": f"Treaty of {target_capital} (Turn {turn})",
            "summary": ", ".join(summary_parts),
            "detail": ". ".join(detail_lines) + ".",
            "target_nation": target,
            "turn": turn,
            "war_outcome": outcome,
            "territory_gained": gained,
            "territory_lost": lost,
            "gold_received": gold_received,
            "gold_paid": gold_paid,
            "final_war_score": final_war_score,
            "war_duration_turns": duration,
            "casualties_france": casualties_france,
            "casualties_enemy": casualties_enemy,
            "terms_ratified": terms,
            "political_aftermath": aftermath,
        })
    return recent


def _format_peace_outcome_label(outcome: str) -> str:
    labels = {
        "french_victory": "French victory",
        "enemy_victory": "Enemy victory",
        "stalemate": "Stalemate",
        "white_peace": "White peace",
    }
    return labels.get(outcome, outcome.replace("_", " ").capitalize())


def _as_str_list(value) -> List[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


# ============================================================================
# TAB 3: BALANCE OF EUROPE / THREAT & COALITION
# ============================================================================

def _build_balance_of_europe(world) -> Dict[str, Any]:
    """Build the v2.4.3 Balance of Europe ledger payload."""
    from backend.game_logic.coalition import (
        DISSOLUTION_THREAT_THRESHOLD,
        WAR_EXHAUSTION_MAX,
        bloc_power,
        _hegemony_signal_band,
        _identify_max_bloc_share,
        describe_hegemon_bloc,
        get_qualifying_nations,
        power_score,
    )

    threat_level = int(getattr(world, 'threat_level', 0) or 0)
    if threat_level >= 80:
        threat_tier = "CRITICAL"
    elif threat_level >= 60:
        threat_tier = "HIGH"
    elif threat_level >= 30:
        threat_tier = "MODERATE"
    else:
        threat_tier = "LOW"

    total_power = 0
    hegemon_power = 0
    try:
        hegemon, share = _identify_max_bloc_share(world)
        active_nations = world.get_active_nations()
        total_power = int(sum(power_score(n, world) for n in active_nations))
        hegemon_power = int(bloc_power(hegemon, world)) if hegemon else 0
    except Exception:
        hegemon, share = None, 0.0
    band = _hegemony_signal_band(float(share)) if hegemon else 0
    bloc_info = describe_hegemon_bloc(world, hegemon, float(share)) if hegemon else {
        "bloc_label": None,
        "descriptive_label": None,
        "adjective": None,
        "is_proper_bloc_name": False,
    }
    bloc_members = []
    if hegemon:
        try:
            bloc_members = list(world.get_bloc_members(hegemon))
        except Exception:
            bloc_members = [hegemon]

    coalition = getattr(world, 'active_coalition', None)
    brewing = getattr(world, 'coalition_brewing', None)
    cooldown = int(getattr(world, 'coalition_cooldown', 0) or 0)
    # Stage D review fix [r7]: this panel is FRANCE's coalition frame — its
    # threat/qualifying/sources are all player-scoped, so an ECLIPSE
    # coalition/brewing (target_nation != player) must not wear it. The
    # eclipse surfaces through the nations tab, campaign log and dispatch
    # until Stage F lands its own render (§4.6b).
    _lp = getattr(world, 'player_nation', 'France')
    if coalition and (coalition.get("target_nation") or _lp) != _lp:
        coalition = None
    if brewing and (brewing.get("target_nation") or _lp) != _lp:
        brewing = None
    if coalition:
        coalition_state = "DECLARED"
        headline_case = "ACTIVE_COALITION"
    elif brewing:
        coalition_state = "BREWING"
        headline_case = "BREWING"
    elif cooldown > 0:
        coalition_state = "COOLDOWN"
        headline_case = "COOLDOWN"
    elif hegemon and band > 0:
        coalition_state = "NO_COALITION"
        headline_case = "HEGEMON_NO_COALITION"
    else:
        coalition_state = "NO_HEGEMON"
        headline_case = "NO_HEGEMON"

    members = []
    leader = ""
    coalition_name = ""
    coalition_posture = "defensive"
    if coalition:
        members = list(coalition.get("members", []) or [])
        leader = str(coalition.get("leader", "") or "")
        coalition_name = str(coalition.get("name", "Unknown Coalition") or "Unknown Coalition")
        coalition_posture = str(coalition.get("strategic_posture", "defensive") or "defensive")

    # Threat sources this turn (with human-readable labels).
    # AI-4a step 5: producers now log every actor's deeds — this panel is
    # the PLAYER's alarm, so only player-targeted entries (or legacy
    # target-less ones) are shown.
    _player = getattr(world, 'player_nation', 'France')
    raw_sources = [
        s for s in getattr(world, 'threat_sources_this_turn', [])
        if not isinstance(s, dict) or s.get("target", _player) == _player
    ]
    threat_sources = []
    for s in raw_sources:
        if isinstance(s, dict):
            source_key = s.get("source", "")
            amount = int(s.get("amount") or 0)
            label = _threat_source_label(world, source_key)
            sign = "+" if amount >= 0 else ""
            threat_sources.append({
                "source": source_key,
                "label": label,
                "amount": amount,
                "display": f"{label} ({sign}{amount})",
            })
        else:
            threat_sources.append({"source": str(s), "label": str(s), "amount": 0, "display": str(s)})

    # Active coalition member details (strength, WE, WE trend)
    active_coalition_data = None
    partial_priority = VISIBILITY_PRIORITY.get(PARTIAL, 3)
    if coalition:
        members_data = []
        combined_strength = 0
        for member in members:
            member_strength = sum(
                m.strength for m in world.marshals.values()
                if m.nation == member and m.strength > 0
            )
            combined_strength += member_strength
            vis = _get_nation_visibility(member, world)
            strength_display = _format_army_strength(member_strength, vis)
            we_raw = world.war_exhaustion.get(member, 0) or 0
            if VISIBILITY_PRIORITY.get(vis, 0) < partial_priority:
                we = 0
            else:
                we = we_raw
            prev_we = getattr(world, '_prev_war_exhaustion', {}).get(member, 0)
            if we > prev_we:
                we_trend = "rising"
            elif we < prev_we:
                we_trend = "falling"
            else:
                we_trend = "stable"
            members_data.append({
                "nation": member,
                "strength_display": strength_display,
                "war_exhaustion": int(we),
                "war_exhaustion_trend": we_trend,
            })
        best_vis = UNKNOWN
        best_p = 0
        for member in members:
            vis = _get_nation_visibility(member, world)
            p = VISIBILITY_PRIORITY.get(vis, 0)
            if p > best_p:
                best_vis = vis
                best_p = p
        combined_strength_display = _format_army_strength(combined_strength, best_vis)
        active_coalition_data = {
            "name": coalition_name,
            "leader": leader,
            "posture": coalition_posture,
            "members": members_data,
            "combined_strength_display": combined_strength_display,
        }

    # Threat projection
    next_war_projection = int(min(100, threat_level + 20))
    wars_until_brewing = (
        int(max(0, (60 - threat_level + 19) // 20)) if threat_level < 60 else 0
    )
    wars_until_instant = (
        int(max(0, (80 - threat_level + 19) // 20)) if threat_level < 80 else 0
    )
    threat_projection = {
        "current": int(threat_level),
        "after_next_war": int(next_war_projection),
        "brewing_threshold": int(60),
        "instant_threshold": int(80),
        "wars_until_brewing": int(wars_until_brewing),
        "wars_until_instant": int(wars_until_instant),
    }

    return {
        "headline_case": headline_case,
        "hegemon": hegemon,
        "hegemon_share": round(float(share), 2),
        "hegemon_power": hegemon_power,
        "total_power": total_power,
        "hegemony_band": int(band),
        "bloc_label": bloc_info.get("bloc_label"),
        "descriptive_label": bloc_info.get("descriptive_label"),
        "is_proper_bloc_name": bool(bloc_info.get("is_proper_bloc_name")),
        "bloc_members": bloc_members,
        "power_basis": (
            "Bloc share is a weighted score: the leader plus direct allies "
            "and vassal-bloc members, divided by all active European courts. "
            "It is not a partition; alliance networks can overlap."
        ),
        "coalition_state": coalition_state,
        "coalition_leader": leader,
        "coalition_members": members,
        "coalition_name": coalition_name,
        "coalition_posture": coalition_posture,
        "active_coalition": active_coalition_data,
        "brewing_turns_remaining": int(brewing.get("turns_remaining", 0) or 0)
        if brewing else None,
        "cooldown_turns_remaining": int(cooldown) if cooldown > 0 else None,
        "coalition_cooldown": int(cooldown),
        "threat_level": int(threat_level),
        "threat_tier": threat_tier,
        "threat_sources_this_turn": threat_sources,
        "qualifying_nations": get_qualifying_nations(world),
        "threat_projection": threat_projection,
        # Derived from the ONLY two conditions `coalition.check_dissolution`
        # actually tests, so the stated rule cannot drift from the code
        # again. The retired `dissolution_war_exhaustion_limit: 80` was a
        # hardcoded literal describing a lever that has never existed — a
        # live 1805 campaign showed Austria pinned at the exhaustion CAP
        # with the Third Coalition standing, i.e. the ledger was teaching a
        # war plan the engine would not honour.
        "dissolution_threat_threshold": int(DISSOLUTION_THREAT_THRESHOLD),
        "dissolution_min_members": 2,
        # AI-4c: exhaustion runs to WAR_EXHAUSTION_MAX, not 100 — the member
        # rows render "WE: n/max" off this, so a saturated court reads
        # "200/200" instead of the old "200/100".
        "war_exhaustion_max": int(WAR_EXHAUSTION_MAX),
        # AI-2e §3.7: the paymaster's purse, visible and contestable —
        # payer, client, amount, and the counterplay line. None omits.
        "paymaster_subsidy": build_subsidy_payload(world),
    }

# ============================================================================
# TAB 4: TALLEYRAND
# ============================================================================

def _build_talleyrand(world) -> Dict[str, Any]:
    """Build Talleyrand status tab."""
    player = world.player_nation
    diplomats = getattr(world, 'diplomats', {})
    talleyrand = diplomats.get(player)

    skill = int(talleyrand.skill or 0) if talleyrand else 0

    # Authority-based state label (PL-23: trust removed)
    authority = world.authority_tracker.authority if hasattr(world, 'authority_tracker') else 60
    authority_label = world.authority_tracker.get_authority_label() if hasattr(world, 'authority_tracker') else "Unknown"

    dp_remaining = int(getattr(world, 'diplomatic_points', 0) or 0)
    dp_max = int(getattr(world, 'max_diplomatic_points', 3) or 0)

    # TA3: DP breakdown (world-scoped capital — 1805 pre-slice item 7 family)
    player_capital = world.get_nation_capital(player) or "Paris"
    controls_capital = False
    cap_region = world.regions.get(player_capital)
    if cap_region:
        controls_capital = cap_region.controller == player
    # Player uses authority_tracker, not nation_authority (matches calculate_dp caller in diplomacy.py)
    authority = world.authority_tracker.authority if hasattr(world, 'authority_tracker') else 60
    # Components
    dp_base = 3
    dp_skill_bonus = 1 if talleyrand and talleyrand.skill >= 8 else 0
    dp_authority_bonus = 1 if authority >= 60 else (-1 if authority < 30 else 0)
    dp_capital_penalty = -1 if not controls_capital else 0
    dp_breakdown = {
        "base": dp_base,
        "skill_bonus": dp_skill_bonus,
        "authority_bonus": dp_authority_bonus,
        "capital_penalty": dp_capital_penalty,
    }

    # Active mission
    active_mission = None
    mission = getattr(world, 'active_diplomatic_mission', None)
    if mission and not mission.get("completed"):
        mission_type = mission.get("type", "")

        # TA4: Mission effect descriptions
        from backend.game_logic.diplomatic_dialogue import MISSION_EFFECTS, MISSION_DP_COSTS
        _MISSION_EFFECT_TEXT = {
            "IMPROVE_RELATIONS": "+5 relation per turn",
            "COURT_NATION": "+5 relation per turn, 20% blowback risk",
            "GATHER_INTEL": "Full intel for 3 turns",
            "UNDERMINE_ALLIANCE": "-3 relation between targets per turn",
            "REASSURE_ALLY": "+3 relation per turn",
        }
        effect_text = _MISSION_EFFECT_TEXT.get(mission_type, "")
        dp_cost_per_turn = int(MISSION_DP_COSTS.get(mission_type, 1))

        # TA5: Remaining turns for fixed-duration missions
        remaining_turns = None
        effects = MISSION_EFFECTS.get(mission_type, {})
        if "duration" in effects:
            total_duration = effects["duration"]
            turns_active = int(mission.get("turns_active") or 0)
            remaining_turns = int(max(0, total_duration - turns_active))

        # DPF-2: Mission progress tracking
        from backend.game_logic.diplomacy import get_relation_descriptor as _get_rel_desc
        mission_target = mission.get("target", "")
        initial_relation = int(mission.get("initial_relation") or 0)
        player = getattr(world, 'player_nation', 'France')
        current_relation = int(world.nation_relations.get(
            world._make_diplo_key(player, mission_target), 0
        ) or 0)

        active_mission = {
            "type": mission_type,
            "target": mission_target,
            "duration": int(mission.get("turns_active") or 0),
            "paused": mission.get("paused", False),
            "effect_text": effect_text,
            "dp_cost_per_turn": dp_cost_per_turn,
            "remaining_turns": remaining_turns,
            "started_turn": int(mission.get("started_turn") or 0),
            "initial_relation": initial_relation,
            "current_relation": current_relation,
            "relation_delta": int(current_relation - initial_relation),
            "initial_descriptor": _get_rel_desc(initial_relation),
            "current_descriptor": _get_rel_desc(current_relation),
        }
        # DLF-2: Show target_ally for UNDERMINE_ALLIANCE
        if mission_type == "UNDERMINE_ALLIANCE":
            active_mission["target_ally"] = mission.get("target_ally", "")

    # Proposal in transit
    proposal_in_transit = None
    pit = getattr(world, 'proposal_in_transit', None)
    if pit:
        proposal_in_transit = {
            "target": pit.get("target", ""),
            "type": pit.get("type", pit.get("proposal", {}).get("type", "")),
            "eta": int(pit.get("eta") or pit.get("delivery_turn") or 0),
        }

    # Session 2 follow-up: Single source of truth for mailbox badge
    pending_envoy_count = int(world.dialogue_manager.get_mailbox_count())

    # Sabotage warnings
    SABOTAGE_TYPE_DISPLAY = {
        "softened": "Terms Weakened",
        "hardened": "Terms Hardened",
        "stalled": "Proposal Delayed",
        "ap_downgrade": "Authority Undermined",
        "unit_overpay": "Resources Wasted",
    }
    sabotage_warnings = []
    raw_sabotages = getattr(world, 'undetected_sabotages', [])
    for sab in raw_sabotages:
        if isinstance(sab, dict):
            raw_type = sab.get("type", "")
            sabotage_warnings.append({
                "target": sab.get("target", ""),
                "type": SABOTAGE_TYPE_DISPLAY.get(raw_type, raw_type.replace("_", " ").title()),
                "turn": int(sab.get("turn") or 0),
            })
        else:
            sabotage_warnings.append(str(sab))

    # R29: Diplomatic history (last 20 events)
    diplomatic_history = []
    raw_history = getattr(world, 'diplomatic_history', [])
    for entry in raw_history[-20:]:
        if isinstance(entry, dict):
            diplomatic_history.append({
                "turn": int(entry.get("turn") or 0),
                "type": entry.get("type", ""),
                "target": entry.get("target", ""),
                "nation": entry.get("nation", ""),
                "detail": entry.get("proposal_type", entry.get("treaty_type", "")),
            })
        else:
            diplomatic_history.append({"turn": 0, "type": str(entry), "target": "", "nation": "", "detail": ""})

    # R34: Diplomatic reliability
    reliability = getattr(world, 'diplomatic_reliability', {})
    player_reliability = int(reliability.get(player, 0))

    return {
        "authority": int(authority),
        "authority_label": authority_label,
        "skill": skill,
        "dp_remaining": dp_remaining,
        "dp_max": dp_max,
        "dp_breakdown": dp_breakdown,
        "active_mission": active_mission,
        "proposal_in_transit": proposal_in_transit,
        "pending_envoy_count": pending_envoy_count,
        "sabotage_warnings": sabotage_warnings,
        "diplomatic_history": diplomatic_history,
        "diplomatic_reliability": player_reliability,
    }


# ============================================================================
# WAR BARGAINS TAB (WB-C + WB-D)
# ============================================================================

def _build_war_bargains(world) -> List[Dict[str, Any]]:
    """Build war bargains section for the ledger, including completed bargains."""
    from backend.game_logic.diplomacy import get_all_bargains_for_ledger
    return get_all_bargains_for_ledger(world)
