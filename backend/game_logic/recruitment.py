"""
Marshal Recruitment — "The Marshalate" (docs/MARSHAL_RECRUITMENT_SPEC.md).

The final phase of the Jealousy v3.2 build (user-directed July 11, 2026):
nations with an authored candidate pool (scenario key `marshal_pool`) can
COMMISSION new marshals mid-campaign — France's bench (Mortier, Augereau,
Grouchy, ...) and the enemies' (Bagration, Blucher, Wellesley, ...).

Player and AI share this executor path (GR5): the player commissions via
the typed command / Generals-screen dialog; the enemy AI commissions
through its admin-phase rung when at war, under-officered, and solvent.

Costs: authored gold price + RECRUIT_MARSHAL_AP action points + an initial
corps drawn from the nation's ARM-APPROPRIATE manpower pool (infantry /
cavalry / artillery — ARTILLERY_GAP_SPEC), sized by arm (the corps then
costs normal strength-based upkeep — ES-3).
The new marshal arrives at the nation's capital (or its richest still-held
homeland province if the capital has fallen), enters the glory ladder at
zero (nobody resents an unproven man — spec §1 ties), and applies his
authored relationship seeds SYMMETRICALLY to marshals already standing.

Systems ties (the reason this lives with jealousy): commission feeds the
glory ladder, MC-2 skill tiers (Rally/Intendance/Steward derive from his
authored command/administration), the MC-3 relationship web (seeds), and
ES-7 expectations (battles_won 0 → expectation 0 — his duchy comes later).
"""

from typing import Dict, List, Optional, Tuple

# ═══════════════════ BLESSED CONSTANTS (in-band tunable) ═══════════════════

RECRUIT_MARSHAL_CORPS = 5000    # initial corps, drawn from infantry pool
RECRUIT_MARSHAL_AP = 1          # ADMIN action points (ADMIN_ACTIONS family —
                                # the AI's admin phase shares the verb, GR5)

# AI rung guards (GR5 pricing — the AI pays the same gold from the same
# treasury; these only decide WHEN it reaches for the pool).
AI_RECRUIT_MAX_STANDING = 3     # commission only while standing roster < 3
AI_RECRUIT_TREASURY_BUFFER = 1000

# Arm-aware corps sizes (ARTILLERY_GAP_SPEC §4). A commission raises its
# initial corps from the ARM-APPROPRIATE manpower pool — infantry from
# infantry, horse from the cavalry pool, guns from the (scarcer) artillery
# pool. This is what makes artillery scarce: the authored artillery pools
# are small (majors 5–6k, minors 500–2k), so majors raise batteries readily
# and minors are pool-shut-out. Artillery is fewer men (guns + train).
RECRUIT_CAVALRY_CORPS = 5000       # cavalry corps — drawn from the cavalry pool
RECRUIT_ARTILLERY_CORPS = 3000     # artillery — the scarce arm

_ARM_CORPS_SIZE = {
    "infantry": RECRUIT_MARSHAL_CORPS,
    "cavalry": RECRUIT_CAVALRY_CORPS,
    "artillery": RECRUIT_ARTILLERY_CORPS,
}


def candidate_arm(candidate: Dict) -> str:
    """The manpower arm a commissioned candidate raises its corps from."""
    if candidate.get("artillery"):
        return "artillery"
    if candidate.get("cavalry"):
        return "cavalry"
    return "infantry"


def corps_requirement(candidate: Dict) -> Tuple[str, int]:
    """(arm, men) — the candidate's initial corps and the pool it draws from."""
    arm = candidate_arm(candidate)
    return arm, _ARM_CORPS_SIZE[arm]


# ═══════════════════════════ POOL QUERIES ═════════════════════════════════

def get_marshal_pool(world, nation: str) -> List[Dict]:
    pool = getattr(world, "marshal_pool", {}) or {}
    return list(pool.get(nation, []) or [])


def find_candidate(world, nation: str, name: str) -> Optional[Dict]:
    wanted = (name or "").strip().lower()
    for candidate in get_marshal_pool(world, nation):
        if str(candidate.get("name", "")).lower() == wanted:
            return candidate
    return None


def _standing_count(world, nation: str) -> int:
    return len([
        m for m in world.marshals.values()
        if m.nation == nation and m.strength > 0
        and not getattr(m, "captured_by", "")
    ])


def find_spawn_region(world, nation: str) -> Optional[str]:
    """The capital while held; otherwise the richest still-held homeland
    province; None when the nation has no soil to raise a corps on."""
    capital = world.get_nation_capital(nation)
    capital_region = world.regions.get(capital) if capital else None
    if capital_region is not None and capital_region.controller == nation:
        return capital
    best = None
    best_income = -1
    for region_name in world.nation_starting_regions.get(nation, []) or []:
        region = world.regions.get(region_name)
        if region is None or region.controller != nation:
            continue
        income = int(region.get_effective_income())
        if income > best_income:
            best, best_income = region_name, income
    return best


def check_commission(world, nation: str, candidate: Dict) -> Optional[str]:
    """Refusal reason for commissioning this candidate, or None when clear.
    Player-facing copy; the AI rung reads the same gate (GR5)."""
    name = candidate.get("name", "?")
    if name in world.marshals:
        return f"Marshal {name} already serves."
    cost = int(candidate.get("cost", 0))
    if world.nation_gold.get(nation, 0) < cost:
        return (f"Commissioning {name} costs {cost}g — the treasury holds "
                f"{int(world.nation_gold.get(nation, 0))}g.")
    arm, size = corps_requirement(candidate)
    pool = world.manpower_pools.get(nation, {})
    have = int(pool.get(arm, 0))
    if have < size:
        return (f"Raising {name}'s corps needs {size:,} men from the "
                f"{arm} pool — only {have:,} remain.")
    if find_spawn_region(world, nation) is None:
        return f"No soil remains on which {name} could raise his corps."
    return None


def commission_marshal(world, nation: str, candidate: Dict) -> Dict:
    """Create the marshal, charge the treasury, draw the corps, seed
    relationships, log/notify. Caller has already validated via
    check_commission and charged AP. Returns a summary dict."""
    from backend.models.marshal import create_marshal_from_data

    name = candidate.get("name", "?")
    cost = int(candidate.get("cost", 0))
    spawn = find_spawn_region(world, nation)
    arm, size = corps_requirement(candidate)

    # Candidates use the SCENARIO field shape (trust: {"value": N}) but are
    # created through the boot factory (ctor kwarg: starting_trust int) —
    # convert here; drop the pool-only `cost` key. The `cavalry`/`artillery`
    # arm flag rides through the ctor untouched.
    ctor = {k: v for k, v in candidate.items()
            if k not in ("cost", "relationships", "nation", "location",
                         "strength", "trust")}
    ctor["name"] = name
    ctor["nation"] = nation
    ctor["location"] = spawn
    ctor["strength"] = size
    ctor["starting_trust"] = int(
        (candidate.get("trust", {}) or {}).get("value", 70))
    marshal = create_marshal_from_data(ctor)

    world.nation_gold[nation] = world.nation_gold.get(nation, 0) - cost
    if hasattr(world, "record_gold_spent"):
        world.record_gold_spent(nation, cost)
    world.manpower_pools[nation][arm] = (
        int(world.manpower_pools[nation].get(arm, 0)) - size)
    world.marshals[name] = marshal

    # Relationship seeds — symmetric both directions (MC-3 authoring
    # convention), only toward marshals actually in service.
    seeds = candidate.get("relationships", {}) or {}
    applied_seeds = {}
    for other_name, value in seeds.items():
        other = world.marshals.get(other_name)
        if other is None:
            continue
        marshal.set_relationship(other_name, int(value))
        other.set_relationship(name, int(value))
        applied_seeds[other_name] = int(value)

    # Remove from the pool (a commissioned man cannot be commissioned twice).
    world.marshal_pool[nation] = [
        c for c in world.marshal_pool.get(nation, [])
        if c.get("name") != name
    ]

    world.log_event({
        "type": "marshal_commissioned",
        "marshal": name,
        "nation": nation,
        "location": spawn,
        "cost": cost,
    })
    events = getattr(world, "_pending_jealousy_turn_events", None)
    if events is None:
        events = []
        world._pending_jealousy_turn_events = events
    if nation == world.player_nation:
        events.append({
            "type": "marshal_commissioned",
            "message": (f"Marshal {name} accepts his commission — he raises "
                        f"a corps of {size:,} at {spawn}."),
            "nation": nation,
            "marshal": name,
        })
        from backend.notifications import (
            MARSHAL_COMMISSIONED, NotificationPriority, create_notification,
        )
        world.notifications.add(create_notification(
            notification_type=MARSHAL_COMMISSIONED,
            priority=NotificationPriority.NORMAL,
            title=f"Marshal {name} commissioned",
            message=(f"{name} joins the marshalate at {spawn} with "
                     f"{size:,} men ({cost}g)."),
            turn_created=int(world.current_turn),
            details={"marshal": name, "location": spawn, "cost": cost},
        ))
    else:
        # Word of an enemy commission reaches the player through the
        # fog-ruled diplomatic event queue (visible with intel on them).
        from backend.game_logic.dispatch import queue_dispatch_event
        queue_dispatch_event(world, "enemy_marshal_commissioned", {
            "nation": nation,
            "marshal": name,
        }, fog_rule="partial_on_nation")

    return {
        "marshal": name,
        "nation": nation,
        "location": spawn,
        "cost": cost,
        "corps": size,
        "seeds": applied_seeds,
    }


# ═══════════════════════ AI RUNG (GR5) ════════════════════════════════════

def find_ai_commission(world, nation: str, treasury: int) -> Optional[Dict]:
    """The enemy AI's admin-phase rung: commission the FIRST authored
    candidate when at war, under-officered, and solvent (pool order is the
    authored quality order). Returns an action dict or None."""
    pool = get_marshal_pool(world, nation)
    if not pool:
        return None
    if not world.get_nations_at_war_with(nation):
        return None
    if _standing_count(world, nation) >= AI_RECRUIT_MAX_STANDING:
        return None
    for candidate in pool:
        cost = int(candidate.get("cost", 0))
        if treasury < cost + AI_RECRUIT_TREASURY_BUFFER:
            continue
        if check_commission(world, nation, candidate) is not None:
            continue
        return {
            "marshal": None,
            "action": "recruit_marshal",
            "target": candidate.get("name"),
            "_acting_nation": nation,
        }
    return None


# ═══════════════════════ PLAYER SURFACE ═══════════════════════════════════

def build_recruitment_payload(world) -> Dict:
    """The Generals-screen recruitment block: every candidate with his
    full character sheet, price, seeds, and an honest affordability verdict
    (shown = applied: the same check_commission gate the executor runs)."""
    nation = world.player_nation
    candidates = []
    for candidate in get_marshal_pool(world, nation):
        reason = check_commission(world, nation, candidate)
        candidates.append({
            "name": candidate.get("name"),
            "personality": candidate.get("personality", "cautious"),
            "skills": dict(candidate.get("skills", {}) or {}),
            "trust": int((candidate.get("trust", {}) or {}).get("value", 70)),
            "biography": candidate.get("biography", ""),
            "cost": int(candidate.get("cost", 0)),
            "corps": corps_requirement(candidate)[1],
            "arm": candidate_arm(candidate),
            "cavalry": bool(candidate.get("cavalry", False)),
            "artillery": bool(candidate.get("artillery", False)),
            "relationships": dict(candidate.get("relationships", {}) or {}),
            "available": reason is None,
            "blocked_reason": reason or "",
        })
    nation_pool = world.manpower_pools.get(nation, {}) or {}
    return {
        "candidates": candidates,
        "ap_cost": RECRUIT_MARSHAL_AP,
        "corps_size": RECRUIT_MARSHAL_CORPS,
        "treasury": int(world.nation_gold.get(nation, 0)),
        "infantry_pool": int(nation_pool.get("infantry", 0)),
        "pools": {
            "infantry": int(nation_pool.get("infantry", 0)),
            "cavalry": int(nation_pool.get("cavalry", 0)),
            "artillery": int(nation_pool.get("artillery", 0)),
        },
    }
