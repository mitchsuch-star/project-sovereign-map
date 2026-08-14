"""
naval.py â€” "The Wooden Wall" (DEF-5, docs/NAVAL_SPEC.md v1.0.4).

THE ABSTRACTION: there is NO naval map layer. A nation's navy is ONE record in
the ONE new serialized store `world.fleets` (ships / readiness / posture plus
the Descent counters). The sea exists only through its four consequences on
the land war (spec Â§4):

    1. the crossing gate   â€” `crossing_check` at every movement seam
    2. the blockade        â€” `is_blockaded` â†’ trade Ã—0.5, island WE, closure
    3. the expedition      â€” `resolve_expedition` (the H4 Bantry verb)
    4. the fleet action    â€” `resolve_fleet_action` (Trafalgar in one resolver)

Design rules (spec Â§2):
- ONE store. `world.fleets` absent/empty â†’ every hook in this module returns
  its dormant value (legacy world, bare flag world, every fixture: boot-zero
  by construction â€” the EC-W idiom).
- Shown = applied: every ratio/odds figure a surface renders comes from the
  same functions the resolvers read (the Q3/IGR-E discipline).
- GR5: one predicate gates player and AI movement alike; the AI prices ships,
  postures and expeditions through the same executor verbs.
- Deterministic under `campaign_seed` â€” every roll uses the AI-0b sha256
  helpers, namespaced by turn/actor so a re-attempt after losses re-rolls.
- Authored, not derived (D7): fleets/ports/dockyards are scenario content in
  `europe_1805.json`; the over-true `is_coastal` flag is NEVER read (Â§3.4 â€”
  DEF-8 stays un-triggered). Coverage keys off the 18 hand-authored
  `sea_links`; closure keys off authored `ports`.

Derived-state memory (blockade transitions, strait verdicts, CS tier) lives
under `world.fleets[META_KEY]` â€” the jealousy `__levels__` idiom: one
serialized field, dunder-keyed meta, skipped by every fleet iterator.
"""

from typing import Dict, List, Optional, Tuple

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CONSTANTS (spec Â§7 â€” gate-blessed defaults, in-band tunable; structural
# changes escalate)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

# N2 â€” Â§13.2 measured re-bless: a ship-of-the-line out-prices a fortification
# (400g, top of the building band), never undercuts a depot. The full-rate
# drip (2/turn = 800g) â‰ˆ 38% of France's measured boot net.
SHIP_COST = 400
SHIP_BUILD_RATE = 2            # per turn, national â€” the Â§3.5 TIME wall
SHIP_BUILD_RATE_BLOCKADED = 1  # Â§3.5 brake (2): pressure slows the slips
NEW_SHIP_READINESS = 40        # Â§3.3 green crews â€” hulls are not a navy

# N3 â€” "laid up in ordinary" at peace: upkeep bills at war only.
SHIP_UPKEEP_WAR = 2            # g/ship/turn

# N4 â€” one number to learn: the same 1.25Ã— judges blockade and crossing.
BLOCKADE_RATIO = 1.25
CROSSING_RATIO = 1.25
WINDOW_CROSSING_FLOOR = 0.9    # N9 â€” during a Â§5.3 window only

# NV-4 "THE HOST RULE" (Â§4.1a) â€” an opposed landing is not a march. Marching
# a sea link INTO a province held by a court we are at war with is refused
# while ANY hostile fleet still covers that water: an army does not stroll
# ashore against a defended coast. The two doors that remain are the two
# history used â€” put â‰¤EXPEDITION_MAX_TROOPS into the transports, or beat the
# fleet that covers the passage (uncontested water = an administrative
# ferry, unlimited). A Â§5.3 window WAIVES the rule: drawing the enemy off
# station is precisely the moment the army crosses, which is the Descent's
# whole point. Landing on our OWN, an ally's or a neutral's shore was never
# gated â€” that is the Portugal case (Mondego Bay 1808), and it is why
# Britain's army reaches the Continent at all.
HOST_RULE_ACTIVE = True

# N5 â€” blockade effects
BLOCKADE_TRADE_FACTOR = 0.5
ISLAND_BLOCKADE_WE = 2         # island clause (H5) â€” authored `island: true`
TRADE_DOMINANCE_FLOOR = 0.4    # smugglers and licences â€” the System leaked

# N6 â€” readiness economy (the whole H2 model)
READINESS_TICK = 5
READINESS_BLOCKADE_FLOOR = 50
READINESS_MIN = 40
READINESS_MAX = 100
NAVY_DRILL_CEILING = 75        # v1.0.3 â€” only sea room makes a 100

# N7 â€” H6: coalition fleets pooled badly
POOL_ALLIED = 0.8

# N8 â€” the expedition (curve measured + published at NV-2, anchors A3/A4)
EXPEDITION_MAX_TROOPS = 15000
EXPEDITION_BASE_PCT = 95
EXPEDITION_SIZE_PENALTY_PER_1000 = 2.0
EXPEDITION_COVERAGE_PENALTY = 13.0
EXPEDITION_COVERAGE_CAP = 4.5
# Measured at NV-2 against anchors A3 (boot Ireland 55-65 / Channel-15k
# â‰¤15): link 2.2 Â· open water 0.3 give 64 / 12 at boot readiness.
EXPEDITION_LINK_WEIGHT = 2.2    # a covered link: the fleet stands ON the lane
EXPEDITION_OPEN_WATER_WEIGHT = 0.3  # a descent: the patrol must CATCH you
EXPEDITION_WINDOW_BONUS_PP = 25
EXPEDITION_INTERCEPT_LOSS = 0.30
EXPEDITION_TURNBACK_LOSS = 0.05
EXPEDITION_TURNBACK_READINESS = 10
EXPEDITION_INTERCEPT_RATIO = 1.5  # decisive coverage â†’ intercepted, not turned

# N9 â€” the Grand Diversion
DIVERSION_SUCCESS_PCT = 45
WINDOW_TURNS = 2
WINDOW_COVERAGE_FACTOR = 0.5

# N10 â€” the fleet action (lanchester-lite)
FLEET_ACTION_LOSER_BASE = 0.20
FLEET_ACTION_LOSER_SCALE = 0.15
FLEET_ACTION_WINNER_BASE = 0.08
FLEET_ACTION_DECISIVE_RATIO = 1.5
FLEET_ACTION_DECISIVE_EXTRA = 0.20
FLEET_ACTION_LOSER_WE = 8
FLEET_ACTION_JITTER_PCT = 10

# N11 â€” CS closure war-weariness tiers (highest first)
CS_WE_TIERS = ((0.80, 3), (0.60, 2), (0.40, 1))

# Â§5.3 â€” the Descent camp
DESCENT_CAMP_MIN_TROOPS = 40000
DESCENT_CAMP_STAGED_TURNS = 2

# NV-5 â€” the AI's naval DECISION constants (Â§6). These bound what the
# council chooses, never what the rules allow: the player's own brakes are
# untouched (Â§3.5's three), and every mechanic stays GR5-symmetric.
AI_FLEET_CEILING_FACTOR = 1.5    # Ã— the AUTHORED establishment
AI_FLEET_TREASURY_RESERVE = 4    # Ã— SHIP_COST held back for the army
AI_EXPEDITION_MIN_ODDS = 55      # below this the council will not risk a corps
AI_EXPEDITION_MIN_TROOPS = 3000  # a corps, not a raiding party
AI_EXPEDITION_HOST_RELATION = 25  # a shore that will actually receive an army

# AP prices live in world_state._action_costs (the ONLY cost table â€” the
# three documented-looking constants that used to sit here were referenced
# by nothing and were removed in the Aug 2026 health-check audit; retuning
# them changed nothing, which is worse than absent documentation).

# The dunder meta key inside world.fleets (jealousy `__levels__` idiom).
META_KEY = "__naval__"

POSTURES = ("guard", "blockade")

# Alliance-family states that pool fleets (H6) â€” vassal links pool too.
_POOLING_STATES = ("ALLIANCE", "DEFENSIVE_ALLIANCE")


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# THE STORE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def get_fleets(world) -> Dict[str, dict]:
    """The raw store ({} when the world has no naval layer)."""
    return getattr(world, "fleets", None) or {}


def has_naval_layer(world) -> bool:
    """Master dormancy switch: any non-meta entry (fleet OR ports-only row)."""
    return any(k != META_KEY for k in get_fleets(world))


def iter_fleets(world):
    """Yield (nation, record) for REAL fleets only â€” ships > 0 authored or
    built. Ports-only rows (Â§3.2: closure denominator, no fleet) and the
    meta record are skipped."""
    for nation, rec in get_fleets(world).items():
        if nation == META_KEY or not isinstance(rec, dict):
            continue
        if int(rec.get("ships", 0) or 0) > 0:
            yield nation, rec


def get_fleet(world, nation: str) -> Optional[dict]:
    """The nation's fleet record, or None (ports-only rows return their
    record too when present â€” callers that need a REAL fleet check ships)."""
    rec = get_fleets(world).get(nation)
    return rec if isinstance(rec, dict) else None


def has_fleet(world, nation: str) -> bool:
    rec = get_fleet(world, nation)
    return bool(rec) and int(rec.get("ships", 0) or 0) > 0


def _meta(world) -> dict:
    """The derived-state memory record (created on first use)."""
    fleets = getattr(world, "fleets", None)
    if fleets is None:
        return {}
    return fleets.setdefault(META_KEY, {})


def boot_fleets_from_navies(world, navies: Optional[dict]) -> None:
    """Transform the scenario's authored `navies` block into live fleet
    records (from_scenario only â€” saves round-trip `world.fleets` directly).

    A row with ships > 0 becomes a full fleet record; a ships-0 row stays a
    ports-only entry (Â§3.2 â€” the closure denominator is authored, never
    derived). Boot postures are derived immediately after the scenario's
    starting wars are seeded (Â§6: Britain's boot blockade is the H2 rot)."""
    if not navies:
        return
    fleets: Dict[str, dict] = {}
    for nation, row in navies.items():
        if not isinstance(row, dict):
            continue
        ships = int(row.get("ships", 0) or 0)
        rec: Dict = {"ships": ships, "ports": int(row.get("ports", 0) or 0)}
        for key in ("dockyards", "camp_provinces"):
            if row.get(key):
                rec[key] = [str(r) for r in row[key]]
        if row.get("admiral"):
            rec["admiral"] = str(row["admiral"])
        if row.get("island"):
            rec["island"] = True
        if row.get("trade_dominance") is not None:
            rec["trade_dominance"] = int(row["trade_dominance"])
        # EB-2: the authored colonial pool rides the fleet record like
        # trade_dominance (validator-clamped [0, 1200]; runtime trusts it).
        if row.get("overseas_income") is not None:
            rec["overseas_income"] = int(row["overseas_income"])
        if ships > 0:
            rec.update({
                "readiness": int(row.get("readiness", 70) or 70),
                "posture": "guard",
                "camp_turns": 0,
                "diversion_used": False,
                "window_turns": 0,
                "built_this_turn": 0,
                # NV-5: the authored establishment â€” what this court's yards
                # and seamen actually support. The AI's build ceiling reads
                # it (the player's does not; the player's brakes stay gold
                # and time). Never mutated after boot.
                "established": ships,
            })
        fleets[nation] = rec
    world.fleets = fleets
    derive_ai_postures(world)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# STRENGTH, POOLING, GEOGRAPHY
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def effective_strength(rec: dict) -> float:
    """ships Ã— readiness/100 â€” the only strength number (Â§3.1)."""
    ships = int(rec.get("ships", 0) or 0)
    if ships <= 0:
        return 0.0
    return ships * int(rec.get("readiness", 0) or 0) / 100.0


def _is_pooled_partner(world, principal: str, partner: str, against: str) -> bool:
    """H6: a co-belligerent ally or vassal-link nation pools at Ã—0.8 â€” it
    must share the war against `against`."""
    if partner == principal or partner == against:
        return False
    if not world.is_at_war(partner, against):
        return False
    state = world.get_diplomatic_state(principal, partner)
    if state in _POOLING_STATES:
        return True
    vassals = getattr(world, "vassals", {}) or {}
    if (vassals.get(partner, {}) or {}).get("lord") == principal:
        return True
    if (vassals.get(principal, {}) or {}).get("lord") == partner:
        return True
    return False


def combined_effective(world, nation: str, against: str,
                       match_posture: Optional[str] = None) -> float:
    """Pooled effective strength of `nation`'s side against `against`
    (Â§3.1). Pool = co-belligerent allies/vassals at Ã—0.8 each, computed at
    read time from diplomatic state â€” no pool object. `match_posture`
    restricts partners to the same mode (coverage pooling, Â§3.1
    "same mode+target")."""
    own = get_fleet(world, nation)
    total = effective_strength(own) if own else 0.0
    for partner, rec in iter_fleets(world):
        if not _is_pooled_partner(world, nation, partner, against):
            continue
        if match_posture and rec.get("posture") != match_posture:
            continue
        total += POOL_ALLIED * effective_strength(rec)
    return total


def get_sea_link_pairs(world) -> frozenset:
    """The 18 hand-authored sea-link pairs as frozenset({name, name}) â€”
    empty on any non-Europe map (legacy world: gate dormant)."""
    if getattr(world, "sovereign_map", "legacy") != "europe":
        return frozenset()
    return _europe_sea_link_pairs()


_SEA_LINK_CACHE: Optional[frozenset] = None


def _europe_sea_link_pairs() -> frozenset:
    global _SEA_LINK_CACHE
    if _SEA_LINK_CACHE is None:
        from backend.models.region import _load_europe_registry
        registry = _load_europe_registry()
        raw = registry.get("regions", {})
        pairs = set()
        for a, b in registry.get("sea_links", []):
            ra = raw.get(f"Region_{int(a):03d}")
            rb = raw.get(f"Region_{int(b):03d}")
            if ra and rb:
                pairs.add(frozenset((ra["name"], rb["name"])))
        _SEA_LINK_CACHE = frozenset(pairs)
    return _SEA_LINK_CACHE


def is_sea_link(world, region_a: str, region_b: str) -> bool:
    return frozenset((region_a, region_b)) in get_sea_link_pairs(world)


def _controller(world, region_name: str) -> Optional[str]:
    region = world.regions.get(region_name)
    return getattr(region, "controller", None) if region else None


def all_dockyard_provinces(world) -> Dict[str, str]:
    """{dockyard province -> authoring nation}. Conquest grants the YARD
    (Â§3.4a) â€” build rights follow CONTROL of any listed province."""
    yards: Dict[str, str] = {}
    for nation, rec in get_fleets(world).items():
        if nation == META_KEY or not isinstance(rec, dict):
            continue
        for prov in rec.get("dockyards", []) or []:
            yards[str(prov)] = nation
    return yards


def controlled_dockyards(world, nation: str) -> List[str]:
    """Dockyard provinces `nation` controls right now (its build sites)."""
    return sorted(
        prov for prov in all_dockyard_provinces(world)
        if _controller(world, prov) == nation
    )


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# THE BLOCKADE (Â§4.2 â€” consequence 2)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def blockader_against(world, target: str) -> Tuple[Optional[str], float]:
    """The strongest at-war enemy fleet in blockade mode pinning `target`
    (untargeted posture, v1.0.3 â€” the simultaneous watch), with its pooled
    coverage. Returns (None, 0.0) when nobody qualifies on the ratio.

    Blockade requires the target to have authored naval presence (a fleet or
    a ports row) â€” a landlocked court with no entry cannot be blockaded
    (spec-gap ruling recorded in the NV-1 landing record)."""
    target_rec = get_fleet(world, target)
    if target_rec is None:
        return None, 0.0
    own_eff = effective_strength(target_rec)
    best_nation, best_cov = None, 0.0
    for nation, rec in iter_fleets(world):
        if nation == target or rec.get("posture") != "blockade":
            continue
        if not world.is_at_war(nation, target):
            continue
        coverage = combined_effective(world, nation, target,
                                      match_posture="blockade")
        if coverage >= BLOCKADE_RATIO * own_eff and coverage > best_cov:
            best_nation, best_cov = nation, coverage
    return best_nation, best_cov


def is_blockaded(world, nation: str) -> bool:
    if not has_naval_layer(world):
        return False
    return blockader_against(world, nation)[0] is not None


def blockaded_nations(world) -> List[str]:
    """Every naval-present nation currently under blockade (sorted)."""
    if not has_naval_layer(world):
        return []
    out = []
    for nation in get_fleets(world):
        if nation == META_KEY:
            continue
        if is_blockaded(world, nation):
            out.append(nation)
    return sorted(out)


def blockade_trade_loss(world) -> Dict[str, int]:
    """{nation: gold lost to blockade this turn} â€” the signed "Blockade" Net
    component. Trade income stays FULL at the `calculate_trade_income`
    chokepoint (the EC-W1 Contributions pattern: gross shown, the suspension
    its own line); `process_trade_income` applies full âˆ’ loss."""
    if not has_naval_layer(world):
        return {}
    from backend.game_logic.diplomacy import calculate_trade_income
    full = calculate_trade_income(world)
    losses: Dict[str, int] = {}
    for nation in blockaded_nations(world):
        gross = int(full.get(nation, 0))
        if gross > 0:
            losses[nation] = gross - int(gross * BLOCKADE_TRADE_FACTOR)
    return losses


def ship_upkeep(world, nation: str) -> int:
    """N3 â€” 2g/ship/turn AT WAR only ("laid up in ordinary" at peace).
    The signed "Admiralty" Net component."""
    rec = get_fleet(world, nation)
    if not rec:
        return 0
    ships = int(rec.get("ships", 0) or 0)
    if ships <= 0:
        return 0
    if not world.get_nations_at_war_with(nation):
        return 0
    return int(ships * SHIP_UPKEEP_WAR)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# THE CONTINENTAL SYSTEM 2.0 (Â§5.1 â€” closure, tiers, trade dominance)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def trade_dominance_nation(world) -> Optional[str]:
    """The authored trade_dominance holder (Britain on the shipped scenario)
    â€” GR5: derived from authored data, never a nation literal."""
    for nation, rec in get_fleets(world).items():
        if nation == META_KEY or not isinstance(rec, dict):
            continue
        if rec.get("trade_dominance"):
            return nation
    return None


def continental_ports_total(world) -> int:
    """Î£ authored ports over every non-island navies entry (26 at boot)."""
    total = 0
    for nation, rec in get_fleets(world).items():
        if nation == META_KEY or not isinstance(rec, dict):
            continue
        if rec.get("island"):
            continue
        total += int(rec.get("ports", 0) or 0)
    return total


def closure_against(world, target: str) -> float:
    """Â§5.1 closure = Î£ ports of (nations at war with `target` + their
    PUPPET/SATELLITE vassals + CS members) Ã· Î£ all continental ports.
    Boot fact (pinned): France 4 + Spain 3 + Holland 2 + KingdomOfItaly 1
    = 10 of 26 â‰ˆ 0.385."""
    total = continental_ports_total(world)
    if total <= 0:
        return 0.0
    from backend.game_logic.vassal import AUTONOMY_PUPPET, AUTONOMY_SATELLITE
    vassals = getattr(world, "vassals", {}) or {}
    members = set(getattr(world, "continental_system_members", []) or [])
    closed = 0
    for nation, rec in get_fleets(world).items():
        if nation == META_KEY or nation == target or not isinstance(rec, dict):
            continue
        if rec.get("island"):
            continue
        ports = int(rec.get("ports", 0) or 0)
        if ports <= 0:
            continue
        counted = False
        if world.is_at_war(nation, target):
            counted = True
        elif nation in members:
            counted = True
        else:
            vstate = vassals.get(nation) or {}
            lord = vstate.get("lord")
            if (lord and world.is_at_war(lord, target)
                    and vstate.get("autonomy", AUTONOMY_SATELLITE)
                    in (AUTONOMY_PUPPET, AUTONOMY_SATELLITE)):
                counted = True
            else:
                # NV-10 â€” THE CONQUERED COAST. Ports are authored per
                # NATION (Â§3.2 keeps the denominator authored), and until
                # now the numerator read only who a court was AT WAR with
                # â€” so overrunning a neutral's coastline did nothing to
                # the System. Measured on the scripted A2 drive: France
                # took all four Portuguese provinces by turn 12 and the
                # closure went DOWN. That is backwards, and it is the
                # System's own central act: Napoleon invaded Portugal in
                # 1807 precisely to shut Lisbon to British trade. A
                # court whose CAPITAL is held by a power at war with the
                # target no longer opens its harbours to that target â€”
                # the conqueror does, and the conqueror is at war.
                capital = world.get_nation_capital(nation)
                region = world.regions.get(capital) if capital else None
                holder = getattr(region, "controller", None)
                if (holder and holder != nation
                        and world.is_at_war(holder, target)):
                    counted = True
        if counted:
            closed += ports
    return closed / float(total)


def cs_closure_tier(closure: float) -> int:
    """0..3 â€” the N11 tier index (the WE add per turn IS the tier)."""
    for threshold, tier in CS_WE_TIERS:
        if closure >= threshold:
            return tier
    return 0


def trade_dominance_income(world, nation: str) -> Optional[int]:
    """The absorbed naval_income (Â§4.2/Â§5.1): authored trade_dominance
    Ã— (1 âˆ’ closure), floor Ã—0.4 â€” suspended entirely under blockade.
    None when this nation holds no authored trade_dominance (callers keep
    their legacy arm)."""
    rec = get_fleet(world, nation)
    if not rec or not rec.get("trade_dominance"):
        return None
    if is_blockaded(world, nation):
        return 0
    base = int(rec["trade_dominance"])
    closure = closure_against(world, nation)
    return int(base * max(TRADE_DOMINANCE_FLOOR, 1.0 - closure))


# EB-2 "The Wealth of Nations" (Econ Balance gate, Aug 7 2026 â€” gate record
# docs/audits/ECON_BALANCE_GATE_2026_08_07.md Â§3 EB-2): a colonial power's
# overseas trade while AT WAR with the trade-dominance holder â€” the RN sits
# on the sea lanes (the 1804 frigate seizure, the post-Trafalgar silver
# collapse) â€” one derived condition, no new state. B8, band 0.0â€“0.4.
OVERSEAS_WAR_FACTOR = 0.25

# EB-2 save-compat (review [12]): pre-EB-2 Europe saves round-trip fleet
# records without `overseas_income`, so from_dict backfills MISSING keys
# from this map â€” otherwise an in-flight campaign silently never receives
# the colonial pool. This deliberately DUPLICATES the europe_1805.json
# authored values; the duplication is safe because a drift pin
# (test_econ_balance_eb.py) asserts the two stay equal. France authors
# NONE by design and is absent here too.
OVERSEAS_INCOME_BACKFILL = {
    "Britain": 500,
    "Spain": 250,
    "Holland": 150,
    "Portugal": 150,
}


def overseas_trade_income(world, nation: str) -> int:
    """EB-2: the authored `overseas_income` pool (colonies as a MODIFIER,
    never map objects), modulated by who commands the sea.

    - The trade-dominance holder (Britain): Ã— (1 âˆ’ closure), floor Ã—0.4,
      Ã—0 under blockade â€” the same rules its trade_dominance obeys. This is
      what gives the Continental System an economic target: closure now
      strangles the pool that funds the paymaster's subsidies.
    - A non-holder colonial power (Spain's silver, the Dutch Indies,
      Brazil): Ã—0 while blockaded Â· Ã—OVERSEAS_WAR_FACTOR while at war with
      the dominance holder Â· Ã—1.0 otherwise.

    Its own positive signed "Overseas Trade" Net component â€” deliberately
    NOT folded invisibly into `income` (the NV-5 decoration lesson).
    Returns 0 when the nation authors no overseas_income (incl. France â€”
    a design pin: France's "overseas" arm is continental extraction).
    """
    rec = get_fleet(world, nation)
    if not rec:
        return 0
    base = int(rec.get("overseas_income", 0) or 0)
    if base <= 0:
        return 0
    if is_blockaded(world, nation):
        return 0
    holder = trade_dominance_nation(world)
    if holder == nation:
        closure = closure_against(world, nation)
        return int(base * max(TRADE_DOMINANCE_FLOOR, 1.0 - closure))
    if holder and world.is_at_war(nation, holder):
        return int(base * OVERSEAS_WAR_FACTOR)
    return base


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# THE CROSSING GATE (Â§4.1 â€” consequence 1)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def _fleet_covers_link(world, nation: str, rec: dict,
                       region_a: str, region_b: str) -> bool:
    """Â§4.1 coverage: a GUARD fleet covers every sea link touching its own
    nation's provinces; a BLOCKADE fleet covers every link touching the
    provinces of ANY nation its owner is at war with (untargeted)."""
    posture = rec.get("posture", "guard")
    for region_name in (region_a, region_b):
        controller = _controller(world, region_name)
        if not controller:
            continue
        if posture == "guard":
            if controller == nation:
                return True
        else:
            if controller != nation and world.is_at_war(nation, controller):
                return True
    return False


def covering_fleets(world, mover_nation: str,
                    region_a: str, region_b: str) -> List[Tuple[str, float]]:
    """Hostile fleets covering this link against `mover_nation`, with their
    pooled coverage values (window halving applied â€” Â§5.3.4)."""
    covers: List[Tuple[str, float]] = []
    mover_rec = get_fleet(world, mover_nation)
    window_open = bool(mover_rec and int(mover_rec.get("window_turns", 0) or 0) > 0)
    for nation, rec in iter_fleets(world):
        if nation == mover_nation:
            continue
        if not world.is_at_war(nation, mover_nation):
            continue
        if not _fleet_covers_link(world, nation, rec, region_a, region_b):
            continue
        coverage = combined_effective(world, nation, mover_nation,
                                      match_posture=rec.get("posture"))
        if window_open:
            coverage *= WINDOW_COVERAGE_FACTOR
        if coverage > 0:
            covers.append((nation, coverage))
    covers.sort(key=lambda item: (-item[1], item[0]))
    return covers


# HC-4a "The Royal Navy's lifeline" (gate Â§5a) â€” flip lever for the
# BASELINE_SERIES attribution experiment: False reproduces the pre-slice
# supply behavior byte-identically (the HOST_RULE_ACTIVE idiom).
SHORE_SUPPLY_ACTIVE = True


def shore_supply_state(world, army_nation: str,
                       region_name: str) -> Optional[str]:
    """HC-4a â€” the naval supply verdict for an AT-WAR army standing on a
    COASTAL province: 'lifeline' | 'strangled' | None.

    The model keeps ONE fleet store and no naval map layer (Â§12), so
    "the adjacent water" is the abstraction's water: a fleet reaches a
    shore by PROJECTING (blockade posture â€” the untargeted watch), and
    a side's own pooled fleet runs its convoys in any posture. The
    gate's arms, read literally (presence, not dominance):
      - friendly afloat AND no hostile projecting â†’ 'lifeline'
        (Britain's Lisbon corps eats like a home army);
      - hostile projecting AND NO friendly coverage at all â†’
        'strangled' (the coast-dominating fleet strains the shore â€”
        the post-Trafalgar arc);
      - both afloat â†’ contested â†’ None; neither â†’ None â€” today's
        behavior byte-identically. The 1805 boot is thereby
        boot-neutral for France: the Combined Fleet is outmatched but
        AFLOAT, so the Royal Navy's watch does not yet starve the
        French coast (that takes sinking it).
    ZERO new constants; fleetless worlds return None before any read;
    the caller gates on `region.is_coastal` (authored per province).
    """
    if not SHORE_SUPPLY_ACTIVE or not has_naval_layer(world):
        return None
    hostile_nation: Optional[str] = None
    hostile_cov = 0.0
    for nation, rec in iter_fleets(world):
        if nation == army_nation or rec.get("posture") != "blockade":
            continue
        if not world.is_at_war(nation, army_nation):
            continue
        cov = combined_effective(world, nation, army_nation,
                                 match_posture="blockade")
        if cov > hostile_cov:
            hostile_nation, hostile_cov = nation, cov
    # The army side's own pooled strength â€” pooled against the covering
    # enemy when one stands, else against any of the army's war enemies
    # (the pool needs a shared foe to form; the own fleet always counts).
    against = hostile_nation
    if against is None:
        enemies = world.get_nations_at_war_with(army_nation)
        against = enemies[0] if enemies else ""
    friendly = combined_effective(world, army_nation, against) if against \
        else effective_strength(get_fleet(world, army_nation) or {})
    if friendly > 0 and hostile_cov <= 0:
        return "lifeline"
    if hostile_cov > 0 and friendly <= 0:
        return "strangled"
    return None


def is_hostile_shore(world, mover_nation: str, to_region: str) -> bool:
    """NV-4 (Â§4.1a): is `to_region` held by a court `mover_nation` is at war
    with? The ONE reading of "opposed" â€” own soil, an ally's soil and a
    neutral's soil are all hosts, and a host is never stormed."""
    if not HOST_RULE_ACTIVE:
        return False
    holder = _controller(world, to_region)
    if not holder or holder == mover_nation:
        return False
    return bool(world.is_at_war(mover_nation, holder))


def crossing_check(world, mover_nation: str,
                   from_region: str, to_region: str) -> Dict:
    """THE predicate (Â§4.1) â€” consulted at every movement seam, both sides
    (GR5). Returns a verdict dict; `allowed` is the only key a gate needs,
    the rest feed the honest refusal and the Crossings verdict line
    (shown = applied):

        {"allowed", "verdict", "coverer", "coverage", "mover_effective",
         "ratio", "floor", "window", "message"}

    verdict âˆˆ open (uncovered) Â· open_ratio Â· window Â· shut Â· landing.
    `landing` is NV-4's host rule (Â§4.1a): the water is ours but the far
    shore is enemy country and still watched â€” an expedition, not a march.
    No dice on ordinary MOVE â€” a refusal is flat, never a roll."""
    result = {
        "allowed": True, "verdict": "open", "coverer": None,
        "coverage": 0.0, "mover_effective": 0.0, "ratio": None,
        "floor": CROSSING_RATIO, "window": False, "message": "",
    }
    if not has_naval_layer(world):
        return result
    if not is_sea_link(world, from_region, to_region):
        return result
    covers = covering_fleets(world, mover_nation, from_region, to_region)
    if not covers:
        return result
    coverer, coverage = covers[0]
    mover_rec = get_fleet(world, mover_nation)
    window_open = bool(mover_rec and int(mover_rec.get("window_turns", 0) or 0) > 0)
    mover_eff = combined_effective(world, mover_nation, coverer)
    floor = WINDOW_CROSSING_FLOOR if window_open else CROSSING_RATIO
    ratio = (mover_eff / coverage) if coverage > 0 else float("inf")
    allowed = ratio >= floor
    result.update({
        "allowed": allowed,
        "coverer": coverer,
        "coverage": round(coverage, 1),
        "mover_effective": round(mover_eff, 1),
        "ratio": round(ratio, 2),
        "floor": floor,
        "window": window_open,
    })
    if allowed and not window_open and is_hostile_shore(
            world, mover_nation, to_region):
        # NV-4 the host rule (Â§4.1a). Sited AFTER the ratio arm so it can
        # only ever change the verdict for a mover who already commands the
        # water â€” a mover the ratio has already turned back hears the
        # stronger, truer refusal. Uncontested water never reaches here
        # (no covers â†’ early return), so beating the covering fleet
        # outright still opens the shore.
        result["allowed"] = False
        result["verdict"] = "landing"
        holder = _controller(world, to_region)
        from backend.display_names import display_nation
        result["message"] = (
            f"{to_region} is enemy country, Sire, and "
            f"{_fleet_label(coverer, get_fleet(world, coverer) or {})} still "
            f"watches that water. An army does not march ashore onto a "
            f"defended coast â€” that is a landing, not a march. Put a corps "
            f"of {EXPEDITION_MAX_TROOPS:,} men or fewer into the transports, "
            f"or break the fleet that covers the passage."
            + (f" {display_nation(holder)} holds the shore."
               if holder else ""))
    elif allowed:
        result["verdict"] = "window" if window_open else "open_ratio"
    else:
        result["verdict"] = "shut"
        coverer_rec = get_fleet(world, coverer) or {}
        coverer_ships = int(coverer_rec.get("ships", 0) or 0)
        # Â§2.3: the refusal names the gap and the two real answers. Never a
        # feature reference (Â§10 standing rule) â€” present-tense facts only.
        result["message"] = (
            f"The crossing from {from_region} to {to_region} is barred â€” "
            f"{_fleet_label(coverer, coverer_rec)} commands the water with "
            f"{coverer_ships} sail ({result['coverage']:.0f} effective) "
            f"against our {result['mover_effective']:.0f}. "
            "Build or pool a fleet to contest the passage, or land a small "
            "expedition where the patrols are thin."
        )
    return result


def _fleet_label(nation: str, rec: dict) -> str:
    from backend.display_names import nation_adjective
    if nation == "Britain":
        return "the Royal Navy"
    # Adjectival, not the raw tag: "the French fleet", never "the France
    # fleet" (spotted in the NV-4 refusal copy, August 2, 2026).
    return f"the {nation_adjective(nation)} fleet"


def crossing_allowed(world, mover_nation: str,
                     from_region: str, to_region: str) -> bool:
    """Boolean arm for candidate filters (AI destination scans)."""
    if not getattr(world, "fleets", None):
        return True
    return crossing_check(world, mover_nation, from_region, to_region)["allowed"]


def crossing_check_reach(world, mover_nation: str,
                         from_region: str, to_region: str) -> Dict:
    """NV-9 â€” THE REACH GATE: the crossing predicate for a strike whose
    range is 2, where the water may lie on the MIDDLE leg.

    The direct-pair check is blind to it: `is_sea_link(Paris, London)` is
    False, so `crossing_check` early-returns "open" and a cavalry charge
    Parisâ†’(Normandy)â†’London resolves a battle across water the Royal Navy
    commands â€” and, on victory, ADVANCES INTO LONDON. Measured on master
    at 89576c5: Murat ended his charge standing in London. The 2-tile MOVE
    seam has always checked both legs (`movement_executor` Â§4.1); this is
    that model made the single source, so every ranged strike inherits it.

    Returns the DIRECT verdict when the destination is one step away. At
    range 2 it returns `open` if ANY intermediate route clears both legs
    (a strike may go round the water), and otherwise the blocking verdict
    of the best route â€” the honest refusal naming the sea that stopped it."""
    direct = crossing_check(world, mover_nation, from_region, to_region)
    if not has_naval_layer(world) or not direct["allowed"]:
        return direct
    origin = world.regions.get(from_region)
    dest = world.regions.get(to_region)
    if origin is None or dest is None:
        return direct
    if to_region in (getattr(origin, "adjacent_regions", []) or []):
        return direct  # one step: the direct verdict IS the whole path
    blocked: Optional[Dict] = None
    for middle in getattr(origin, "adjacent_regions", []) or []:
        mid_region = world.regions.get(middle)
        if mid_region is None:
            continue
        if to_region not in (getattr(mid_region, "adjacent_regions", []) or []):
            continue
        leg1 = crossing_check(world, mover_nation, from_region, middle)
        leg2 = crossing_check(world, mover_nation, middle, to_region)
        if leg1["allowed"] and leg2["allowed"]:
            return direct  # a dry route exists â€” the strike goes round
        if blocked is None:
            blocked = leg1 if not leg1["allowed"] else leg2
    return blocked if blocked is not None else direct


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# THE FLEET ACTION (Â§4.4 â€” consequence 4: Trafalgar in one resolver)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def _seed(world) -> str:
    return str(getattr(world, "campaign_seed", "historical"))


def _pct_roll(world, namespace: str, chance_pct: int) -> bool:
    """Deterministic percentage roll on the campaign seed (AI-0b helper).
    NOTE: uses seeded_int directly, NOT seeded_jitter â€” the historical seed
    must still ROLL (jitter's historical arm returns 0, which would make
    every gamble auto-succeed); determinism, not scripting, is the pin."""
    from backend.game_logic.campaign_variance import seeded_int
    return seeded_int(_seed(world), namespace, 0, 99) < int(chance_pct)


def resolve_fleet_action(world, attacker: str, defender: str,
                         context: str = "action") -> Dict:
    """Â§4.4 â€” fires in exactly two situations (an intercepted expedition, a
    caught diversion); never orderable, never ambient. Compares pooled
    effective strengths; loser 20% + 15%Ã—min(râˆ’1,1), winner 8%/max(r,1),
    seeded jitter Â±10%; ratio â‰¥ 1.5 â†’ decisive (loser extra âˆ’20%, the
    `trafalgar` beat, loser WE +8). No land-combat code is touched."""
    atk_eff = combined_effective(world, attacker, defender)
    def_eff = combined_effective(world, defender, attacker)
    if atk_eff >= def_eff:
        winner, loser, w_eff, l_eff = attacker, defender, atk_eff, def_eff
    else:
        winner, loser, w_eff, l_eff = defender, attacker, def_eff, atk_eff
    ratio = (w_eff / l_eff) if l_eff > 0 else 3.0
    decisive = ratio >= FLEET_ACTION_DECISIVE_RATIO

    from backend.game_logic.campaign_variance import seeded_int
    jitter = seeded_int(
        _seed(world),
        f"naval::action::{int(world.current_turn)}::{attacker}::{defender}",
        -FLEET_ACTION_JITTER_PCT, FLEET_ACTION_JITTER_PCT) / 100.0

    loser_frac = (FLEET_ACTION_LOSER_BASE
                  + FLEET_ACTION_LOSER_SCALE * min(ratio - 1.0, 1.0))
    if decisive:
        loser_frac += FLEET_ACTION_DECISIVE_EXTRA
    winner_frac = FLEET_ACTION_WINNER_BASE / max(ratio, 1.0)
    loser_frac = max(0.05, loser_frac * (1.0 + jitter))
    winner_frac = max(0.01, winner_frac * (1.0 - jitter))

    losses = {
        loser: _apply_side_losses(world, loser, winner, loser_frac),
        winner: _apply_side_losses(world, winner, loser, winner_frac),
    }

    we = getattr(world, "war_exhaustion", None)
    if decisive and isinstance(we, dict):
        we[loser] = int(min(200, int(we.get(loser, 0)) + FLEET_ACTION_LOSER_WE))

    atk_rec = get_fleet(world, attacker) or {}
    def_rec = get_fleet(world, defender) or {}
    battle_name = f"the {_action_waters(world, attacker, defender)} action"
    result = {
        "winner": winner, "loser": loser, "decisive": bool(decisive),
        "ratio": round(ratio, 2), "context": str(context),
        "attacker": attacker, "defender": defender,
        "attacker_admiral": str(atk_rec.get("admiral", "")),
        "defender_admiral": str(def_rec.get("admiral", "")),
        "losses": losses, "battle_name": battle_name,
    }
    _log_fleet_action(world, result)
    # NV-7: the tableau. Built HERE, at the one seam every fleet action
    # passes through, so no caller can produce an action that has no
    # picture â€” the BD Â§14.1 lesson (the link and the stash must be
    # structurally inseparable from the render).
    from backend.game_logic.naval_diorama import build_naval_diorama
    diorama = build_naval_diorama(world, result)
    if diorama:
        # Rides the result only â€” the client stashes and raises it on
        # control return, exactly as it does the land tableau. Nothing new
        # is serialized onto the world.
        result["naval_diorama"] = diorama
    return result


def _action_waters(world, a: str, b: str) -> str:
    """A display handle for the engagement (no sea zones exist â€” name the
    action by its combatants)."""
    from backend.display_names import display_nation
    return f"{display_nation(a)}â€“{display_nation(b)}"


def _apply_side_losses(world, principal: str, enemy: str, frac: float) -> Dict[str, int]:
    """Apply a loss fraction to every fleet that pooled on this side (the
    Combined Fleet bled together at Trafalgar â€” H6)."""
    out: Dict[str, int] = {}
    members = [principal] + [
        partner for partner, _rec in iter_fleets(world)
        if _is_pooled_partner(world, principal, partner, enemy)
    ]
    for member in members:
        rec = get_fleet(world, member)
        if not rec:
            continue
        ships = int(rec.get("ships", 0) or 0)
        if ships <= 0:
            continue
        # NV-11: proportional, with NO minimum-of-one floor. The floor
        # made a small ally's losses wildly disproportionate on the
        # WINNING side â€” at the measured winner fraction of 3.9% a
        # 100-sail flagship lost 4.0% while a 5-sail squadron lost 20%,
        # a 2-sail squadron 50%, and a 1-sail ally was ANNIHILATED every
        # single time its side won. Rounding alone is the honest rule and
        # it is also the historical one: the Royal Navy lost ZERO ships
        # at Trafalgar. The losing side is unaffected â€” at 55% even a
        # lone hull rounds to 1 and still goes down.
        lost = int(round(ships * frac)) if frac > 0 else 0
        lost = min(lost, ships)
        rec["ships"] = int(ships - lost)
        out[member] = int(lost)
    return out


def _log_fleet_action(world, result: Dict) -> None:
    from backend.game_logic.dispatch import queue_dispatch_event
    event = {
        "type": "trafalgar" if result["decisive"] else "fleet_action",
        "turn": int(world.current_turn),
        "winner": result["winner"], "loser": result["loser"],
        "decisive": bool(result["decisive"]),
        "battle_name": result["battle_name"],
        "context": result["context"],
        "losses": {k: dict(v) for k, v in result["losses"].items()},
    }
    world.log_event(event)
    winner_rec = get_fleet(world, result["winner"]) or {}
    loser_rec = get_fleet(world, result["loser"]) or {}
    queue_dispatch_event(world, "trafalgar" if result["decisive"] else "fleet_action", {
        "winner": result["winner"], "loser": result["loser"],
        "winner_admiral": winner_rec.get("admiral", "the flag officer"),
        "loser_admiral": loser_rec.get("admiral", "the flag officer"),
        "loser_ships_lost": int(sum(result["losses"].get(result["loser"], {}).values())),
    }, "always")


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# THE EXPEDITION (Â§4.3 â€” consequence 3: the H4 verb)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def expedition_coverage(world, mover_nation: str,
                        target_region: str) -> Tuple[Optional[str], float, str]:
    """Hostile naval coverage against an expedition to `target_region`.
    Returns (coverer, coverage, mode) â€” mode 'link' when the run crosses a
    covered sea link from the embarkation shore (the fleet stands ON the
    lane), 'open_water' for a no-route descent (Bantry: the patrol must
    catch you at sea). Window halving applies (Â§5.3)."""
    mover_rec = get_fleet(world, mover_nation)
    window_open = bool(mover_rec and int(mover_rec.get("window_turns", 0) or 0) > 0)
    target_controller = _controller(world, target_region)
    best: Tuple[Optional[str], float] = (None, 0.0)
    for nation, rec in iter_fleets(world):
        if nation == mover_nation:
            continue
        if not world.is_at_war(nation, mover_nation):
            continue
        # Any hostile fleet patrols against a landing on or from its side of
        # the water: guard defends its own coast, blockade hunts everywhere
        # its war reaches (untargeted).
        relevant = False
        posture = rec.get("posture", "guard")
        if posture == "guard":
            relevant = bool(target_controller) and target_controller == nation
        else:
            relevant = True
        if not relevant:
            continue
        coverage = combined_effective(world, nation, mover_nation,
                                      match_posture=posture)
        if window_open:
            coverage *= WINDOW_COVERAGE_FACTOR
        if coverage > best[1]:
            best = (nation, coverage)
    mode = "open_water"
    # A covered-link run: the target sits across an authored sea link from a
    # province of the mover's shore (the Channel dash) â€” weightier coverage.
    if best[0] is not None:
        for pair in get_sea_link_pairs(world):
            if target_region in pair:
                other = next(iter(pair - {target_region}), None)
                if other and _controller(world, other) == mover_nation:
                    mode = "link"
                    break
    return best[0], best[1], mode


def expedition_slip_odds(world, mover_nation: str, target_region: str,
                         troops: int) -> Dict:
    """N8 â€” the quoted-and-applied odds (IGR-E discipline). Scale down with
    size and coverage-vs-escort ratio, up (+25pp) during a window. With no
    hostile fleet at all the sailing is administrative: 100."""
    troops = int(troops)
    coverer, coverage, mode = expedition_coverage(world, mover_nation, target_region)
    if coverer is None or coverage <= 0:
        return {"odds": 100, "coverer": None, "coverage": 0.0, "ratio": 0.0,
                "mode": mode, "window": False}
    escort = max(combined_effective(world, mover_nation, coverer), 1.0)
    ratio = coverage / escort
    weight = (EXPEDITION_LINK_WEIGHT if mode == "link"
              else EXPEDITION_OPEN_WATER_WEIGHT)
    mover_rec = get_fleet(world, mover_nation)
    window_open = bool(mover_rec and int(mover_rec.get("window_turns", 0) or 0) > 0)
    odds = (EXPEDITION_BASE_PCT
            - EXPEDITION_SIZE_PENALTY_PER_1000 * (troops / 1000.0)
            - EXPEDITION_COVERAGE_PENALTY
            * min(weight * ratio, EXPEDITION_COVERAGE_CAP))
    if window_open:
        odds += EXPEDITION_WINDOW_BONUS_PP
    odds = int(round(max(5, min(95, odds))))
    return {"odds": odds, "coverer": coverer, "coverage": round(coverage, 1),
            "ratio": round(ratio, 2), "mode": mode, "window": window_open}


def resolve_expedition(world, marshal, target_region: str) -> Dict:
    """Resolve a confirmed expedition the same turn (no in-flight limbo).
    Success relocates the corps; failure is turned back (small attrition,
    fleet readiness âˆ’10) or â€” on a decisive coverage ratio â€” intercepted at
    sea: corps âˆ’30% and the fleet fights Â§4.4."""
    troops = int(marshal.strength)
    quote = expedition_slip_odds(world, marshal.nation, target_region, troops)
    namespace = (f"naval::slip::{int(world.current_turn)}::{marshal.name}"
                 f"::{troops}::{target_region}")
    slipped = quote["odds"] >= 100 or _pct_roll(world, namespace, quote["odds"])
    result = {
        "success": True, "landed": bool(slipped), "odds": quote["odds"],
        "coverer": quote["coverer"], "target": target_region,
        "marshal": marshal.name, "troops": troops, "intercepted": False,
    }
    if slipped:
        origin = marshal.location
        marshal.move_to(target_region)
        world.log_event({
            "type": "expedition_landed", "turn": int(world.current_turn),
            "marshal": marshal.name, "nation": marshal.nation,
            "origin": origin, "target": target_region, "troops": troops,
        })
        from backend.game_logic.dispatch import queue_dispatch_event
        queue_dispatch_event(world, "expedition_landed", {
            "marshal": marshal.name, "nation": marshal.nation,
            "target": target_region, "troops": f"{troops:,}",
        }, "always")
        return result

    # Failure arm: decisive coverage â†’ intercepted at sea; else turned back.
    escort = max(combined_effective(world, marshal.nation,
                                    quote["coverer"] or ""), 1.0)
    decisive_coverage = (quote["coverer"] is not None
                         and quote["coverage"] >= EXPEDITION_INTERCEPT_RATIO * escort)
    fleet = get_fleet(world, marshal.nation)
    if decisive_coverage:
        result["intercepted"] = True
        lost = int(round(troops * EXPEDITION_INTERCEPT_LOSS))
        marshal.strength = int(max(0, marshal.strength - lost))
        result["troops_lost"] = lost
        if fleet and int(fleet.get("ships", 0) or 0) > 0 and quote["coverer"]:
            result["fleet_action"] = resolve_fleet_action(
                world, marshal.nation, quote["coverer"], context="expedition")
        world.log_event({
            "type": "expedition_intercepted",
            "turn": int(world.current_turn), "marshal": marshal.name,
            "nation": marshal.nation, "target": target_region,
            "troops_lost": int(lost), "coverer": quote["coverer"] or "",
        })
        from backend.game_logic.dispatch import queue_dispatch_event
        queue_dispatch_event(world, "expedition_intercepted", {
            "marshal": marshal.name, "nation": marshal.nation,
            "target": target_region,
            "coverer": quote["coverer"] or "the enemy",
            "troops_lost": f"{int(lost):,}",
        }, "always")
    else:
        lost = int(round(troops * EXPEDITION_TURNBACK_LOSS))
        marshal.strength = int(max(0, marshal.strength - lost))
        result["troops_lost"] = lost
        if fleet and int(fleet.get("ships", 0) or 0) > 0:
            fleet["readiness"] = int(max(
                READINESS_MIN,
                int(fleet.get("readiness", 0) or 0) - EXPEDITION_TURNBACK_READINESS))
        world.log_event({
            "type": "expedition_turned_back",
            "turn": int(world.current_turn), "marshal": marshal.name,
            "nation": marshal.nation, "target": target_region,
            "troops_lost": int(lost),
        })
    return result


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# THE DESCENT (Â§5.3 â€” camp, diversion, window)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def camp_strength(world, nation: str) -> int:
    """Total friendly strength standing in the nation's authored camp
    provinces (0 when none are authored)."""
    rec = get_fleet(world, nation)
    if not rec:
        return 0
    provinces = rec.get("camp_provinces") or []
    if not provinces:
        return 0
    total = 0
    for marshal in world.get_marshals_by_nation(nation):
        if marshal.location in provinces and marshal.strength > 0:
            total += int(marshal.strength)
    return int(total)


def camp_staged(world, nation: str) -> bool:
    rec = get_fleet(world, nation)
    return bool(rec) and int(rec.get("camp_turns", 0) or 0) >= DESCENT_CAMP_STAGED_TURNS


def _island_war_enemies(world, nation: str) -> List[str]:
    """At-war enemies with an island fleet (the descent's only object)."""
    out = []
    for enemy, rec in iter_fleets(world):
        if rec.get("island") and world.is_at_war(nation, enemy):
            out.append(enemy)
    return out


def resolve_diversion(world, nation: str) -> Dict:
    """Â§5.3.3(a) â€” the Grand Diversion, once per war: seeded 45%. Success
    halves the enemy's coverage for 2 turns (`window_turns`) and fires
    `strait_open`; failure is intercepted returning â€” Â§4.4 at bad readiness
    (Trafalgar, as it happened)."""
    rec = get_fleet(world, nation)
    if not rec or int(rec.get("ships", 0) or 0) <= 0:
        return {"success": False,
                "message": "We have no fleet to sail, Sire."}
    if rec.get("diversion_used"):
        return {"success": False, "message": (
            "The fleet has already attempted its grand diversion this war â€” "
            "the squadrons cannot repeat the feint while the enemy watches for it.")}
    enemies = _island_war_enemies(world, nation)
    hostile = enemies[0] if enemies else None
    if hostile is None:
        # fall back to the strongest at-war fleet (the diversion needs a
        # watcher to draw off)
        at_war = [(n, effective_strength(r)) for n, r in iter_fleets(world)
                  if world.is_at_war(nation, n)]
        at_war.sort(key=lambda item: -item[1])
        hostile = at_war[0][0] if at_war else None
    if hostile is None:
        return {"success": False, "message": (
            "There is no hostile fleet to draw away â€” the seas are open already.")}
    rec["diversion_used"] = True
    namespace = f"naval::diversion::{int(world.current_turn)}::{nation}"
    if _pct_roll(world, namespace, DIVERSION_SUCCESS_PCT):
        rec["window_turns"] = int(WINDOW_TURNS)
        world.log_event({
            "type": "strait_open", "turn": int(world.current_turn),
            "nation": nation, "against": hostile, "window_turns": int(WINDOW_TURNS),
        })
        from backend.game_logic.dispatch import queue_dispatch_event
        from backend.display_names import display_nation
        queue_dispatch_event(world, "strait_open", {
            "line": (f"{display_nation(nation)}'s diversion draws the "
                     f"{display_nation(hostile)} fleet off station â€” "
                     f"{WINDOW_TURNS} turns of open water"),
        }, "always")
        return {
            "success": True, "window": True, "against": hostile,
            "window_turns": int(WINDOW_TURNS),
            "message": (
                f"The diversion succeeds â€” the {hostile} fleet is drawn off "
                f"station. The Strait lies open: {WINDOW_TURNS} turns."),
        }
    # Intercepted returning, at bad readiness.
    rec["readiness"] = int(max(READINESS_MIN,
                               int(rec.get("readiness", 0) or 0)
                               - EXPEDITION_TURNBACK_READINESS))
    action = resolve_fleet_action(world, nation, hostile, context="diversion")
    ships_lost = int(sum(action["losses"].get(nation, {}).values()))
    return {
        "success": True, "window": False, "against": hostile,
        "fleet_action": action,
        # NV-7: this is Trafalgar's own arm â€” the diversion caught coming
        # home at bad readiness. If any battle in this game deserves a
        # tableau, it is this one.
        "naval_diorama": action.get("naval_diorama"),
        "message": (
            f"The diversion is caught coming home â€” the fleet is brought to "
            f"battle at bad readiness and loses {ships_lost} sail. "
            + ("A decisive defeat: the enemy's line held the weather gage."
               if action["loser"] == nation and action["decisive"] else
               "The squadrons limp back to port.")),
    }


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# THE PER-TURN TICK (Â§3.3 readiness Â· Â§5.3 camp/window Â· Â§6 postures Â· beats)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def derive_ai_postures(world) -> None:
    """Â§6 â€” one cheap derivation, no new decision phase. Island fleets at
    war blockade (the RN doctrine, authored via `island: true`) â€” unless a
    staged enemy camp or a live enemy window pulls them home to guard
    (Â§5.3.2, the two-front tension). Everyone else guards. The PLAYER's own
    posture is never derived â€” it is theirs to set."""
    player = getattr(world, "player_nation", None)
    for nation, rec in iter_fleets(world):
        if nation == player:
            continue
        posture = "guard"
        if rec.get("island") and world.get_nations_at_war_with(nation):
            posture = "blockade"
            for enemy, enemy_rec in iter_fleets(world):
                if enemy == nation or not world.is_at_war(nation, enemy):
                    continue
                if (int(enemy_rec.get("camp_turns", 0) or 0) >= DESCENT_CAMP_STAGED_TURNS
                        or int(enemy_rec.get("window_turns", 0) or 0) > 0):
                    posture = "guard"
                    break
        rec["posture"] = posture


def _readiness_tick(world) -> None:
    """Â§3.3 â€” the whole H2 economy in four rules, applied on a snapshot so
    order never matters:
      1. blockaded: âˆ’5/turn to floor 50 (the rot);
      2. blockading at war: +5 toward 100 (sea time drills crews);
      3. otherwise +5 toward the war drill ceiling 75 while a superior
         hostile fleet exists, toward 100 in peace / for the superior fleet
         itself."""
    snapshot = {n: effective_strength(r) for n, r in iter_fleets(world)}
    blockaded = set(blockaded_nations(world))
    for nation, rec in iter_fleets(world):
        readiness = int(rec.get("readiness", 0) or 0)
        if nation in blockaded:
            readiness = max(READINESS_BLOCKADE_FLOOR,
                            readiness - READINESS_TICK)
            rec["readiness"] = int(min(readiness, READINESS_MAX))
            continue
        at_war = bool(world.get_nations_at_war_with(nation))
        if rec.get("posture") == "blockade" and at_war:
            ceiling = READINESS_MAX
        else:
            superior = any(
                other != nation and world.is_at_war(nation, other)
                and eff > snapshot.get(nation, 0.0)
                for other, eff in snapshot.items())
            ceiling = NAVY_DRILL_CEILING if (at_war and superior) else READINESS_MAX
        if readiness < ceiling:
            readiness = min(ceiling, readiness + READINESS_TICK)
        rec["readiness"] = int(max(READINESS_MIN, readiness))


def _camp_tick(world) -> List[Dict]:
    """Â§5.3.1 â€” the visible camp: â‰¥40,000 men standing in the authored camp
    provinces of a nation at war with an island naval power ticks
    `camp_turns`; at 2 the descent is STAGED and the `boulogne_camp` beat
    fires once (Britain has seen it coming since turn one)."""
    events: List[Dict] = []
    for nation, rec in iter_fleets(world):
        if not rec.get("camp_provinces"):
            continue
        enemies = _island_war_enemies(world, nation)
        strength = camp_strength(world, nation) if enemies else 0
        previous = int(rec.get("camp_turns", 0) or 0)
        if strength >= DESCENT_CAMP_MIN_TROOPS:
            rec["camp_turns"] = previous + 1
            if (previous < DESCENT_CAMP_STAGED_TURNS
                    and rec["camp_turns"] >= DESCENT_CAMP_STAGED_TURNS):
                event = {
                    "type": "boulogne_camp",
                    "turn": int(world.current_turn), "nation": nation,
                    "against": enemies[0], "strength": int(strength),
                }
                world.log_event(event)
                events.append(event)
                from backend.game_logic.dispatch import queue_dispatch_event
                queue_dispatch_event(world, "boulogne_camp", {
                    "nation": nation, "against": enemies[0],
                    "strength": f"{int(strength):,}",
                }, "always")
        else:
            rec["camp_turns"] = 0
    return events


def _tracked_links(world) -> List[frozenset]:
    """The Crossings list (Â§9): every sea link touching the player's
    provinces or armies."""
    player = getattr(world, "player_nation", None)
    if not player:
        return []
    player_regions = set(world.get_nation_regions(player))
    for marshal in world.get_marshals_by_nation(player):
        if marshal.strength > 0 and marshal.location:
            player_regions.add(marshal.location)
    return [pair for pair in get_sea_link_pairs(world)
            if pair & player_regions]


def _link_key(pair: frozenset) -> str:
    return "|".join(sorted(pair))


def _player_travel_direction(world, player: str, a: str, b: str):
    """NV-4: the crossing gate is DIRECTIONAL now (the host rule reads the
    far shore), so the Crossings board must evaluate the direction the
    player would actually travel â€” outward from the end we hold or stand
    on. With both ends ours (or neither) the sorted order is kept, which is
    the pre-NV-4 behaviour byte-for-byte."""
    ours = set(world.get_nation_regions(player))
    for marshal in world.get_marshals_by_nation(player):
        if marshal.strength > 0 and marshal.location:
            ours.add(marshal.location)
    a_ours, b_ours = a in ours, b in ours
    if b_ours and not a_ours:
        return b, a
    return a, b


def link_verdicts(world) -> Dict[str, Dict]:
    """{link_key: crossing_check verdict} for the player-relevant links â€”
    the SAME predicate the movement gate reads (shown = applied). The key
    stays the sorted pair (stable for the flip-beat store and the map
    payload); the VERDICT is computed for the player's own direction of
    travel (`from_region`/`to_region` ride the dict)."""
    player = getattr(world, "player_nation", None)
    out: Dict[str, Dict] = {}
    if not player or not has_naval_layer(world):
        return out
    for pair in _tracked_links(world):
        a, b = sorted(pair)
        origin, dest = _player_travel_direction(world, player, a, b)
        verdict = crossing_check(world, player, origin, dest)
        verdict["from_region"] = origin
        verdict["to_region"] = dest
        out[_link_key(pair)] = verdict
    return out


def _emit_verdict_flips(world, before: Dict[str, str],
                        after: Dict[str, Dict]) -> None:
    """Â§9 â€” `strait_open`/`strait_shut` fire on state-change only, never
    per-turn repetition. Open-family = open/open_ratio/window."""
    from backend.game_logic.dispatch import queue_dispatch_event
    from backend.display_names import display_nation
    open_family = {"open", "open_ratio", "window"}
    for key, verdict in after.items():
        now = verdict["verdict"]
        was = before.get(key)
        if was is None:
            continue  # newly-tracked link: no flip to announce
        was_open = was in open_family
        now_open = now in open_family
        if was_open == now_open:
            continue
        a, b = key.split("|")
        event_type = "strait_open" if now_open else "strait_shut"
        world.log_event({
            "type": event_type, "turn": int(world.current_turn),
            "link_a": a, "link_b": b,
            "coverer": verdict.get("coverer") or "",
        })
        coverer = verdict.get("coverer")
        if now_open:
            line = f"the {a}â€“{b} crossing stands open to our armies"
        elif now == "landing":
            # NV-4: not "shut" â€” the water is ours, the shore is not. Say
            # which, or the player reads a naval defeat that never happened.
            dest = verdict.get("to_region") or b
            line = (f"the {a}â€“{b} crossing is ours to sail, but {dest} is a "
                    f"defended shore â€” only an expedition puts men on it")
        else:
            tail = (f" â€” {display_nation(coverer)} commands the water"
                    if coverer else "")
            line = f"the {a}â€“{b} crossing is shut{tail}"
        queue_dispatch_event(world, event_type, {"line": line}, "always")


def _record_blockade_pressure(world, now_blockaded: List[str]) -> None:
    """HC-1 (gate Â§2) â€” credit each war pair where a side's fleets deny
    the opponent's trade, once per (denier, victim) per turn.

    Two arms, both derived from EXISTING state:
      1. posture â€” the strongest blockade-posture fleet pinning the
         victim (`blockader_against`, the same verdict the trade loss
         and the beats read);
      2. closure â€” the victim suffers CS closure at the tier-1 notch
         (CS_WE_TIERS' 0.40) and the denier's own authored ports sit in
         that closure's numerator (an at-war continental port-owner).
    Symmetric both directions (GR5: Britain strangling France counts
    for Britain; France closing the continent counts against Britain).
    The counter rides `world.campaign_ledgers` â€” it survives armistice
    and demobilizes with the ledger on formal peace, like every other
    war memory.
    """
    if not hasattr(world, "record_blockade_turn"):
        return
    credited = set()

    # Arm 1: posture blockade (the untargeted watch, resolved per victim).
    for victim in now_blockaded:
        denier, _cov = blockader_against(world, victim)
        if denier and (denier, victim) not in credited:
            world.record_blockade_turn(denier, victim)
            credited.add((denier, victim))

    # Arm 2: Continental-System closure at the tier-1 notch.
    closure_notch = CS_WE_TIERS[-1][0]  # 0.40 â€” the lowest tier's floor
    fleets = get_fleets(world)
    for victim, vrec in fleets.items():
        if victim == META_KEY or not isinstance(vrec, dict):
            continue
        if not world.get_nations_at_war_with(victim):
            continue
        if closure_against(world, victim) < closure_notch:
            continue
        for denier, drec in fleets.items():
            if denier in (META_KEY, victim) or not isinstance(drec, dict):
                continue
            if drec.get("island"):
                continue
            if int(drec.get("ports", 0) or 0) <= 0:
                continue
            if not world.is_at_war(denier, victim):
                continue
            if (denier, victim) in credited:
                continue
            world.record_blockade_turn(denier, victim)
            credited.add((denier, victim))


def process_naval_turn(world) -> List[Dict]:
    """The one per-turn naval pass â€” sited in `_advance_turn_internal`
    immediately BEFORE the income phase, so this turn's trade Ã—0.5 and
    trade_dominance scaling read this turn's blockade verdict. Order:

      1. derive AI postures (Â§6 â€” wars settled by the diplomacy pass above)
      2. snapshot blockade set / strait verdicts / CS tier (beat baselines)
      3. readiness tick (Â§3.3, on a snapshot)
      4. camp tick (Â§5.3.1) Â· window decrement Â· per-turn build reset Â·
         diversion reset at full peace
      5. island blockade WE (+2) and CS closure WE tiers (N11)
      6. beats: blockade_begins/broken Â· boulogne_camp Â· strait flips Â·
         cs_tier_shift â€” all state-change-only, baselines in the META
         record (serialized inside the one store)."""
    if not has_naval_layer(world):
        return []
    events: List[Dict] = []
    meta = _meta(world)

    # 1-2. postures, then baselines from the PREVIOUS tick's stored state.
    derive_ai_postures(world)
    prev_blockaded = list(meta.get("blockaded", []))
    prev_verdicts = dict(meta.get("verdicts", {}))
    prev_tier = int(meta.get("cs_tier", 0) or 0)

    # 3. readiness (before the new blockade set is stored â€” judged live).
    _readiness_tick(world)

    # 4. camp / window / build-rate / diversion resets.
    events.extend(_camp_tick(world))
    for nation, rec in iter_fleets(world):
        window = int(rec.get("window_turns", 0) or 0)
        if window > 0:
            rec["window_turns"] = int(window - 1)
        rec["built_this_turn"] = 0
        if rec.get("diversion_used") and not world.get_nations_at_war_with(nation):
            rec["diversion_used"] = False

    # 5. war-weariness couplings.
    now_blockaded = blockaded_nations(world)
    we = getattr(world, "war_exhaustion", None)
    if isinstance(we, dict):
        for nation in now_blockaded:
            rec = get_fleet(world, nation) or {}
            if rec.get("island"):
                we[nation] = int(min(200, int(we.get(nation, 0)) + ISLAND_BLOCKADE_WE))
        target = trade_dominance_nation(world)
        tier = 0
        if target:
            closure = closure_against(world, target)
            tier = cs_closure_tier(closure)
            if tier > 0 and world.get_nations_at_war_with(target):
                we[target] = int(min(200, int(we.get(target, 0)) + tier))
            if tier != prev_tier:
                event = {
                    "type": "cs_tier_shift", "turn": int(world.current_turn),
                    "target": target, "closure_pct": int(round(closure * 100)),
                    "tier": int(tier), "previous_tier": int(prev_tier),
                }
                world.log_event(event)
                events.append(event)
                from backend.game_logic.dispatch import queue_dispatch_event
                queue_dispatch_event(world, "cs_tier_shift", {
                    "target": target,
                    "closure_pct": int(round(closure * 100)),
                    "tier": int(tier),
                    "direction": "tightens" if tier > prev_tier else "loosens",
                }, "always")
        meta["cs_tier"] = int(tier)

    # 5b. HC-1 "The Silver Blockade": sustained denial writes the war's
    # memory â€” once per (denier, victim) pair per turn, onto the PT-J2
    # campaign ledger (war-gated inside the recorder).
    _record_blockade_pressure(world, now_blockaded)

    # 6. blockade transition beats.
    from backend.game_logic.dispatch import queue_dispatch_event
    for nation in now_blockaded:
        if nation not in prev_blockaded:
            blockader, _cov = blockader_against(world, nation)
            event = {
                "type": "blockade_begins", "turn": int(world.current_turn),
                "nation": nation, "blockader": blockader or "",
            }
            world.log_event(event)
            events.append(event)
            queue_dispatch_event(world, "blockade_begins", {
                "nation": nation, "blockader": blockader or "the enemy",
            }, "always")
    for nation in prev_blockaded:
        if nation not in now_blockaded and get_fleet(world, nation) is not None:
            event = {
                "type": "blockade_broken", "turn": int(world.current_turn),
                "nation": nation,
            }
            world.log_event(event)
            events.append(event)
            queue_dispatch_event(world, "blockade_broken",
                                 {"nation": nation}, "always")
    meta["blockaded"] = list(now_blockaded)

    # 7. strait verdict flips (player-relevant links).
    verdicts = link_verdicts(world)
    _emit_verdict_flips(world, prev_verdicts, verdicts)
    meta["verdicts"] = {key: v["verdict"] for key, v in verdicts.items()}
    return events


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# BUILD (N2 â€” the Â§3.5 three brakes) and the AI rung (Â§6)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def build_rate(world, nation: str) -> int:
    """2/turn â€” 1 while under blockade (Â§3.5 brake 2: escaping pressure is a
    prerequisite of out-building it)."""
    return (SHIP_BUILD_RATE_BLOCKADED if is_blockaded(world, nation)
            else SHIP_BUILD_RATE)


def check_build_fleet(world, nation: str) -> Optional[str]:
    """Shown = applied: the ONE validator both the executor and the AI rung
    consult. Returns a refusal string, or None when a ship can be laid
    down (gold/AP charged by the caller).

    Ruling (recorded, NV-0 landing record): a court with NO navies row at
    all has no naval establishment and cannot found one â€” but a ports-only
    court (Austria, Prussia) that CONQUERS a dockyard province may lay down
    ships there (Â§3.4a: conquest grants the YARD)."""
    rec = get_fleet(world, nation)
    if rec is None:
        return ("We keep no naval establishment, Sire â€” no admiralty, no "
                "cadres, no tradition of the sea.")
    yards = controlled_dockyards(world, nation)
    if not yards:
        return ("We hold no dockyard. Ships of the line are laid down only "
                "in a yard we control.")
    if int(rec.get("built_this_turn", 0) or 0) >= build_rate(world, nation):
        rate = build_rate(world, nation)
        pressed = (" â€” the blockade slows the slips"
                   if rate == SHIP_BUILD_RATE_BLOCKADED else "")
        return (f"The yards are at capacity this season ({rate} keel"
                f"{'s' if rate != 1 else ''} per turn{pressed}). Time, not "
                "gold, builds a navy.")
    return None


def lay_down_ship(world, nation: str) -> Dict:
    """Add one ship at green readiness (weighted fold â€” Â§3.3: you can watch
    your navy get bigger and worse at once). Caller has validated + paid."""
    rec = get_fleet(world, nation)
    ships = int(rec.get("ships", 0) or 0)
    if ships <= 0:
        rec["ships"] = 1
        rec.setdefault("posture", "guard")
        rec["readiness"] = int(NEW_SHIP_READINESS)
        rec.setdefault("camp_turns", 0)
        rec.setdefault("diversion_used", False)
        rec.setdefault("window_turns", 0)
        rec["built_this_turn"] = int(rec.get("built_this_turn", 0) or 0) + 1
        return {"ships": 1, "readiness": int(rec["readiness"])}
    readiness = int(rec.get("readiness", 0) or 0)
    folded = int(round((ships * readiness + NEW_SHIP_READINESS) / (ships + 1)))
    rec["ships"] = ships + 1
    rec["readiness"] = int(max(READINESS_MIN, min(READINESS_MAX, folded)))
    rec["built_this_turn"] = int(rec.get("built_this_turn", 0) or 0) + 1
    return {"ships": int(rec["ships"]), "readiness": int(rec["readiness"])}


def build_admiralty_report(world) -> Dict:
    """Â§9 â€” THE ADMIRALTY block: everything the ledger (and the map payload)
    renders, from the SAME functions the resolvers read (shown = applied).
    Fog ruling (recorded): fleet counts and postures are PUBLIC â€” period
    newspapers printed orders of battle."""
    player = getattr(world, "player_nation", None)
    report: Dict = {"active": bool(has_naval_layer(world))}
    if not report["active"] or not player:
        return report

    own = get_fleet(world, player)
    if own and int(own.get("ships", 0) or 0) > 0:
        laid = int(own.get("built_this_turn", 0) or 0)
        rate = build_rate(world, player)
        report["own_fleet"] = {
            "ships": int(own.get("ships", 0)),
            "readiness": int(own.get("readiness", 0)),
            "posture": str(own.get("posture", "guard")),
            "admiral": str(own.get("admiral", "")),
            "yards": controlled_dockyards(world, player),
            "build_rate": int(rate),
            "laid_this_turn": int(laid),
            "window_turns": int(own.get("window_turns", 0) or 0),
            "diversion_used": bool(own.get("diversion_used")),
            "camp_turns": int(own.get("camp_turns", 0) or 0),
            "camp_strength": int(camp_strength(world, player)),
            "camp_provinces": list(own.get("camp_provinces") or []),
        }
    else:
        report["own_fleet"] = None

    # The Blockade board â€” both directions, effects quoted (Â§9 v1.0.4).
    board: List[Dict] = []
    losses = blockade_trade_loss(world)
    for nation in blockaded_nations(world):
        blockader, coverage = blockader_against(world, nation)
        rec = get_fleet(world, nation) or {}
        effects = []
        loss = int(losses.get(nation, 0))
        if loss > 0:
            effects.append(f"trade halved (âˆ’{loss}/turn)")
        if int(rec.get("ships", 0) or 0) > 0:
            effects.append("the fleet pinned in port")
        if rec.get("island"):
            effects.append(f"war-weariness +{ISLAND_BLOCKADE_WE}/turn")
        board.append({
            "nation": nation,
            "blockader": blockader or "",
            "ours": bool(blockader == player),
            "against_us": bool(nation == player),
            "effects": ", ".join(effects) if effects else "ports watched",
        })
    report["blockade_board"] = board

    # Continental System closure (Â§5.1).
    target = trade_dominance_nation(world)
    if target:
        closure = closure_against(world, target)
        total_ports = continental_ports_total(world)
        # NV-5 legibility: the shipped board boots at 38.5% closure and the
        # lowest tier needs 40% â€” so the headline percentage was true and
        # did nothing, with no way to tell from the surface. Name the next
        # notch and what it costs, in ports, so the number is a target
        # rather than a decoration.
        next_threshold = None
        for pct, _tier in sorted(CS_WE_TIERS):
            if closure < pct:
                next_threshold = pct
                break
        report["continental_system"] = {
            "target": target,
            "closure_pct": int(round(closure * 100)),
            "tier": int(cs_closure_tier(closure)),
            "ports_closed": int(round(closure * total_ports)),
            "ports_total": int(total_ports),
            "next_tier_pct": (int(round(next_threshold * 100))
                              if next_threshold is not None else None),
            "ports_to_next_tier": (
                max(1, int(-(-(next_threshold * total_ports
                              - closure * total_ports) // 1)))
                if next_threshold is not None else None),
        }

    # The Crossings verdict lines (Â§9 v1.0.1) â€” the SAME predicate the
    # movement gate reads.
    crossings: List[Dict] = []
    for key, verdict in sorted(link_verdicts(world).items()):
        a, b = key.split("|")
        v = verdict["verdict"]
        if v == "open":
            line = f"{a}â€“{b}: OPEN â€” uncovered"
        elif v == "open_ratio":
            line = (f"{a}â€“{b}: OPEN â€” ours "
                    f"{verdict['ratio']:.1f}Ã— theirs")
        elif v == "landing":
            # NV-4 (Â§4.1a): the water is ours; the shore is not.
            line = (f"{a}â€“{b}: DEFENDED SHORE â€” "
                    f"{verdict.get('to_region', b)} must be taken by "
                    f"expedition, not marched into")
        elif v == "window":
            own_rec = get_fleet(world, player) or {}
            # NV-12: the countdown finally names what the window DOES.
            line = (f"{a}â€“{b}: WINDOW â€” open "
                    f"{int(own_rec.get('window_turns', 0) or 0)} more turn(s) "
                    "(their coverage halved; the defended-shore rule waived)")
        else:
            coverer = verdict.get("coverer")
            coverer_label = (_fleet_label(coverer,
                                          get_fleet(world, coverer) or {})
                             if coverer else "")
            if verdict.get("ratio"):
                line = (f"{a}â€“{b}: SHUT â€” {coverer_label}"
                        f" at {1.0 / verdict['ratio']:.1f}Ã—")
            elif coverer_label:
                # NV-12 (recon trap 1): a destroyed fleet made the ratio
                # falsy and the row degraded to a bare "SHUT" â€” the
                # worst-informed state produced the least information. The
                # coverer is still named.
                line = (f"{a}â€“{b}: SHUT â€” {coverer_label} commands the "
                        "water unopposed")
            else:
                line = f"{a}â€“{b}: SHUT"
        crossings.append({"link_a": a, "link_b": b, "verdict": v,
                          "line": line})
    report["crossings"] = crossings
    # NV-12: one legend + remedy line under the Crossings header (chosen
    # over per-row remedy tails â€” same clarity, less noise; Â§16 records the
    # deviation). The remedy copy previously fired ONLY on an attempted
    # march.
    report["crossings_legend"] = (
        "crimson = shut Â· amber = defended shore Â· gold = window. A shut "
        "crossing opens by building or pooling a fleet â€” or a small "
        "expedition slips past it.")

    # Honest gate terms IN ORDER (the Â§11.6 idiom) for the two gambles.
    own_ships = int((own or {}).get("ships", 0) or 0)
    at_war_any = bool(world.get_nations_at_war_with(player))
    # NV-6: each term carries its own NEGATIVE phrasing. The gate-terms
    # rows read as conditions ("+ the diversion not yet spent this war"),
    # which is right beside a tick â€” but a disabled chip renders
    # "<label> â€” <reason>", and reusing the condition text there said
    # "The Grand Diversion â€” the diversion not yet spent this war", i.e.
    # exactly backwards. Caught live.
    diversion_terms = [
        {"text": "a fleet in commission", "met": own_ships > 0,
         "unmet": "we keep no fleet in commission"},
        {"text": "at war with a naval power", "met": bool(
            at_war_any and any(world.is_at_war(player, n)
                               for n, _r in iter_fleets(world))),
         "unmet": "no naval power is at war with us"},
        {"text": "the diversion not yet spent this war",
         "met": not bool((own or {}).get("diversion_used")),
         "unmet": "the diversion is already spent this war"},
    ]
    report["diversion_terms"] = diversion_terms
    report["diversion_available"] = all(t["met"] for t in diversion_terms)
    yards = controlled_dockyards(world, player)
    # NV-12 "The Clear Deck": the expedition's gate terms, evaluated against
    # the player's REAL candidates (the Diversion idiom). This list was
    # built at NV-6 and then read by NO surface at all â€” the Diversion
    # rendered its terms while the Expedition's were dropped. Term 2 is
    # honest availability: it names who qualifies, or who is over the lift
    # and by exactly how much.
    player_corps = list(world.get_marshals_by_nation(player))

    # Mirror the EXECUTOR's embark rule exactly (Aug 2026 health-check
    # audit): from home soil an expedition assembles at a controlled yard;
    # from ABROAD any coastal shore serves (the Â§4.3 beachhead return). The
    # old yards-only read told a player whose corps stood on a foreign
    # beach "march a corps to a yard" while the region panel offered him
    # the landing chip.
    def _embark_ok(m) -> bool:
        loc = world.regions.get(m.location)
        ctrl = getattr(loc, "controller", None)
        if ctrl == m.nation:
            return m.location in yards
        return bool(getattr(loc, "is_coastal", False))

    ready_corps = sorted(
        (m for m in player_corps
         if 0 < int(m.strength) <= EXPEDITION_MAX_TROOPS
         and _embark_ok(m)),
        key=lambda m: -int(m.strength))
    over_corps = [m for m in player_corps
                  if int(m.strength) > EXPEDITION_MAX_TROOPS
                  and _embark_ok(m)]
    if ready_corps:
        corps_detail = "ready: " + ", ".join(
            f"{m.name} ({int(m.strength):,} at {m.location})"
            for m in ready_corps[:3])
    elif over_corps:
        smallest = min(over_corps, key=lambda m: int(m.strength))
        corps_detail = (
            f"{smallest.name} commands {int(smallest.strength):,} â€” detach "
            f"{int(smallest.strength) - EXPEDITION_MAX_TROOPS:,} first")
    else:
        corps_detail = "march a corps to a yard"
    # Verify-fleet copy corrections (Aug 2026): term 1 is scoped to HOME
    # embarkation (the executor's abroad arm has no yard requirement), and
    # term 2 names both lawful embark states.
    expedition_terms = [
        {"text": "a dockyard under our flag (to embark from home soil)",
         "met": bool(yards),
         "detail": ", ".join(yards) if yards else "take or build one"},
        {"text": (f"a corps of {EXPEDITION_MAX_TROOPS:,} men or fewer at a "
                  "yard, or on a foreign shore"),
         "met": bool(ready_corps), "detail": corps_detail},
    ]
    report["expedition_terms"] = expedition_terms
    # The numbers a captain would ask before sailing â€” from the SAME
    # constants the resolver rolls (shown = applied).
    report["expedition_notes"] = [
        ("odds fall with corps size and the hostile fleet's effective "
         "strength â€” effective = sail Ã— readiness"),
        # Shown = applied (Aug 2026 health-check audit): only the TURNED-BACK
        # arm pays the readiness penalty (NAVAL_SPEC Â§Descent); the
        # intercepted arm fights a fleet action instead. The old "either
        # way" promised a charge the resolver never applies.
        (f"a failed run: intercepted ~{int(EXPEDITION_INTERCEPT_LOSS * 100)}% "
         f"of the corps lost, turned back ~{int(EXPEDITION_TURNBACK_LOSS * 100)}% "
         f"â€” and the fleet's readiness âˆ’{EXPEDITION_TURNBACK_READINESS} if she "
         f"is turned back"),
    ]
    # Payload-driven client numbers (the client's hardcoded fallbacks were
    # duplicated backend constants â€” trap 8 of the NV-12 recon).
    report["ship_cost"] = int(SHIP_COST)
    report["camp_required"] = int(DESCENT_CAMP_MIN_TROOPS)

    # â”€â”€ NV-6: the chips (Â§9's "usability" clause, the Â§11.6 honest idiom) â”€â”€
    # Every naval verb but `build_fleet` was typed-command only. Each chip
    # below carries the SAME typed command a player would write and the
    # SAME gate the executor applies, so a shown chip is a chip that works
    # and a withheld one says why in present tense.
    chips: List[Dict] = []
    if own and own_ships > 0:
        posture = str(own.get("posture", "guard"))
        if posture == "blockade":
            chips.append({
                "command": "guard home waters",
                "label": "Recall to home waters",
                "reason": "", "enabled": True,
                "note": "covers every crossing touching our own coast"})
        else:
            blockadable = [n for n in world.get_nations_at_war_with(player)
                           if get_fleet(world, n) is not None]
            # NV-9 (R7): the chip note is player-facing prose, so the tags
            # go through the display chokepoint â€” "closes KingdomOfItaly"
            # was reachable the moment Italy entered the war.
            from backend.display_names import display_nation
            chips.append({
                "command": "blockade the enemy",
                "label": "Blockade the enemy",
                "enabled": bool(blockadable),
                "reason": ("" if blockadable else
                           "no enemy at sea to blockade"),
                "note": ("closes " + ", ".join(
                    sorted(display_nation(n) for n in blockadable))
                    if blockadable else "")})
    else:
        # NV-12 (recon trap 9): the whole list used to be gated on
        # own_ships > 0 â€” which deleted the Orders header, every
        # disabled-with-reason chip AND the embark hint for exactly the
        # player who needs the explanation most. The fleetless state now
        # reads as present-but-locked, never as missing.
        chips.append({
            "command": "blockade the enemy",
            "label": "Blockade the enemy",
            "enabled": False,
            "reason": "we keep no fleet in commission",
            "note": ""})
    # The Diversion chip stands OUTSIDE the fleet gate: its own terms carry
    # the fleetless reason.
    if not report["diversion_available"]:
        unmet = [t.get("unmet") or t["text"]
                 for t in diversion_terms if not t["met"]]
        chips.append({
            "command": "order the diversion",
            "label": "The Grand Diversion",
            "enabled": False,
            "reason": "; ".join(unmet), "note": ""})
    else:
        # The verb does NOT require a staged camp, and deliberately is
        # not being made to â€” but spending a once-per-war card to open
        # two turns of water with no army on the beach is a trap, so
        # the chip says so instead of quietly letting it happen.
        note = f"{DIVERSION_SUCCESS_PCT}% â€” and once only, this war"
        if not camp_staged(world, player):
            note += "; no army is staged to use the open water"
        chips.append({
            "command": "order the diversion",
            "label": "The Grand Diversion",
            "enabled": True, "reason": "", "note": note})
    # NV-12: the keel chip â€” build_fleet was region-panel-only, and that
    # chip is region-scoped in appearance while nation-scoped in effect
    # (recon gap 11). THE ADMIRALTY is its honest, nation-scoped home; the
    # gate composes check_build_fleet (the executor's own validator) with
    # the executor's treasury check, so enabled state IS the executor gate.
    build_reason = check_build_fleet(world, player)
    if build_reason is None:
        treasury = int(getattr(world, "nation_gold", {}).get(player, 0))
        if treasury < SHIP_COST:
            build_reason = (f"a ship of the line costs {SHIP_COST}g â€” the "
                            f"treasury holds {treasury}g")
    build_label = (f"Lay down ships ({SHIP_COST}g at {yards[0]})"
                   if yards else f"Lay down ships ({SHIP_COST}g)")
    chips.append({
        "command": "build ships",
        "label": build_label,
        "enabled": build_reason is None,
        "reason": "" if build_reason is None else build_reason,
        "note": ("a keel joins the fleet at green readiness"
                 if build_reason is None else "")})
    report["chips"] = chips

    # The expedition needs a DESTINATION, and the map is where a
    # destination is chosen â€” so its chip lives on the region panel (see
    # `expedition_landings` in map_naval_overlay) and the Admiralty block
    # only names the corps that are ready to sail and where from.
    # Verify-fleet correction (Aug 2026): built from the SAME mirrored
    # predicate as the gate term above â€” the old yards-only read made the
    # Admiralty tab disagree with itself (term said Ney ready on a foreign
    # beach, this list omitted him).
    report["embark_ready"] = [
        {"marshal": m.name, "strength": int(m.strength),
         "location": m.location}
        for m in ready_corps]
    return report


def map_naval_overlay(world) -> Dict:
    """Â§9 v1.0.4 â€” the two MAP render arms, riding the map summary payload:
    sea-link verdict tint (player perspective) + the port blockade glyph on
    blockaded nations' dockyard provinces. Fog-clean (Q4: public data)."""
    if not has_naval_layer(world):
        return {"sea_link_verdicts": [], "blockaded_ports": [],
                "expedition_blocked": {}}
    verdicts = [
        {"link_a": key.split("|")[0], "link_b": key.split("|")[1],
         "verdict": v["verdict"]}
        for key, v in sorted(link_verdicts(world).items())
    ]
    ports: List[str] = []
    for nation in blockaded_nations(world):
        rec = get_fleet(world, nation) or {}
        for prov in rec.get("dockyards", []) or []:
            if _controller(world, prov) == nation:
                ports.append(prov)
    player = getattr(world, "player_nation", None)
    return {"sea_link_verdicts": verdicts,
            "blockaded_ports": sorted(set(ports)),
            # The region panel's honest chip (Â§9): player-controlled build
            # sites + the live price, never hardcoded client-side.
            "player_dockyards": (controlled_dockyards(world, player)
                                 if player else []),
            "ship_cost": int(SHIP_COST),
            # NV-6: {region: [{marshal, strength, odds}]} â€” which corps may
            # land HERE and at what odds, resolved server-side through the
            # same eligibility the executor applies and the same
            # `expedition_slip_odds` the confirm quotes and the resolver
            # rolls (shown = applied). A chip that appears is a chip that
            # sails; the region panel never guesses.
            "expedition_landings": (expedition_landing_options(world, player)
                                    if player else {}),
            # NV-12: the honest-availability partner â€” why a coastal province
            # got NO landing chip (the executor's own gates, named).
            "expedition_blocked": (expedition_blocked_reasons(world, player)
                                   if player else {})}


def expedition_landing_options(world, nation: str) -> Dict[str, List[Dict]]:
    """NV-6 â€” the region panel's landing chips. Mirrors
    NavalExecutor._resolve_expedition_target's eligibility exactly: a
    coastal province that is not where the corps already stands and is not
    reachable by an ordinary land march."""
    if not has_naval_layer(world) or not get_fleet(world, nation):
        return {}
    yards = set(controlled_dockyards(world, nation))
    corps = [m for m in world.get_marshals_by_nation(nation)
             if 0 < int(m.strength) <= EXPEDITION_MAX_TROOPS
             and (m.location in yards
                  or (_controller(world, m.location) != nation
                      and getattr(world.regions.get(m.location), "is_coastal",
                                  False)))]
    if not corps:
        return {}
    options: Dict[str, List[Dict]] = {}
    for region_name, region in world.regions.items():
        if not getattr(region, "is_coastal", False):
            continue
        # NV-4 review â€” the consent gate, mirrored: the chip must not offer
        # a landing the executor refuses. Own soil = sealift; at-war = the
        # verb's point; anyone else must be a host (the same predicate the
        # executor and the AI read).
        holder = _controller(world, region_name)
        if (holder and holder != nation
                and not world.is_at_war(nation, holder)
                and not is_expedition_host(world, nation, holder)):
            continue
        for marshal in corps:
            if region_name == marshal.location:
                continue
            origin = world.regions.get(marshal.location)
            if origin is not None and region_name in (
                    getattr(origin, "adjacent_regions", []) or []):
                if not is_sea_link(world, marshal.location, region_name):
                    continue  # march there; the fleet is for what feet cannot
            quote = expedition_slip_odds(world, nation, region_name,
                                         int(marshal.strength))
            options.setdefault(region_name, []).append({
                "marshal": marshal.name,
                "strength": int(marshal.strength),
                "odds": int(quote["odds"]),
                "from": marshal.location,
            })
    return options


def expedition_blocked_reasons(world, nation: str) -> Dict[str, str]:
    """NV-12 "The Clear Deck" â€” the honest-availability partner of
    expedition_landing_options: for every coastal province that gets NO
    landing chip, the NAMEABLE reason why (recon gap 3: absence was the only
    signal â€” a too-large, inland, or non-consenting landing produced no chip
    and no message anywhere).

    Mirrors the executor's own gates; region-independent causes are computed
    ONCE and fanned out (GR8 â€” this runs per map refresh)."""
    if not has_naval_layer(world) or not get_fleet(world, nation):
        return {}
    yards = set(controlled_dockyards(world, nation))
    all_corps = list(world.get_marshals_by_nation(nation))
    eligible = [m for m in all_corps
                if 0 < int(m.strength) <= EXPEDITION_MAX_TROOPS
                and (m.location in yards
                     or (_controller(world, m.location) != nation
                         and getattr(world.regions.get(m.location),
                                     "is_coastal", False)))]
    # The one region-independent near-miss, computed once: a corps in an
    # embark-legal position but over the transports' lift. Verify-fleet
    # correction (Aug 2026): the near-miss reads the SAME embark predicate
    # as `eligible` (yards OR abroad-coastal) â€” the old yards-only read told
    # a player whose only corps was oversized on a foreign beach to "march
    # one to a yard" when the executor's real refusal is "detach the excess".
    def _embark_position_ok(m) -> bool:
        return (m.location in yards
                or (_controller(world, m.location) != nation
                    and getattr(world.regions.get(m.location),
                                "is_coastal", False)))

    no_corps_reason = ""
    if not eligible:
        over_embarkable = [m for m in all_corps
                           if int(m.strength) > EXPEDITION_MAX_TROOPS
                           and _embark_position_ok(m)]
        if over_embarkable:
            m = min(over_embarkable, key=lambda m: int(m.strength))
            no_corps_reason = (
                f"the transports lift {EXPEDITION_MAX_TROOPS:,} â€” "
                f"{m.name} commands {int(m.strength):,}; detach "
                f"{int(m.strength) - EXPEDITION_MAX_TROOPS:,} first")
        elif yards:
            no_corps_reason = (
                f"no corps of {EXPEDITION_MAX_TROOPS:,} or fewer stands at "
                f"a yard ({', '.join(sorted(yards))}) or on a foreign "
                f"shore â€” march one there")
        else:
            no_corps_reason = "we control no dockyard to embark from"
    blocked: Dict[str, str] = {}
    for region_name, region in world.regions.items():
        if not getattr(region, "is_coastal", False):
            continue
        holder = _controller(world, region_name)
        if holder == nation:
            continue  # own soil sealift is an option row, never a refusal
        if (holder and not world.is_at_war(nation, holder)
                and not is_expedition_host(world, nation, holder)):
            from backend.display_names import display_nation
            blocked[region_name] = (
                f"{display_nation(holder)} has not opened her ports â€” court "
                "her to friendship (25), ally, or make it war")
        elif no_corps_reason:
            blocked[region_name] = no_corps_reason
        else:
            # Aug 2026 health-check audit: the land-adjacency refusal was
            # the ONE executor gate this map never named â€” a lawful target
            # whose every eligible corps stands land-adjacent without a sea
            # link got no chip AND no reason (absence as the only signal,
            # the exact NV-12 gap). Mirror the options builder's skip.
            away = [m for m in eligible if m.location != region_name]
            if away and all(
                (world.regions.get(m.location) is not None
                 and region_name in (getattr(world.regions.get(m.location),
                                             "adjacent_regions", []) or [])
                 and not is_sea_link(world, m.location, region_name))
                    for m in away):
                blocked[region_name] = (
                    "adjacent by land â€” march there; the fleet is for "
                    "what feet cannot reach")
    return blocked


def nation_is_penned_in(world, nation: str) -> bool:
    """NV-5 (Â§6): does this court hold NO province with a LAND border onto a
    court it is at war with? Then its army reaches the war only by sea â€”
    which is Britain's whole strategic situation, and after NV-4 it is a
    real one rather than a walk across the Channel.

    ADJACENCY IS NOT THE TEST, and the first cut of this function got that
    wrong: at boot France has no province touching an at-war enemy either
    (its neighbours are all clients and neutrals) â€” yet France is plainly
    not an island power, it simply has not marched yet. The real question
    is REACHABILITY: walking only over land edges, from any province we
    hold, can the army arrive at an enemy at all? Britain: no, ever.
    France: yes, straight through Bavaria into Austria.

    One land-only breadth-first walk over â‰¤126 nodes, cached per TURN for
    every nation at once (GR8). Deliberately not serialized â€” it derives
    from ownership and war state, both of which round-trip on their own."""
    turn = int(getattr(world, "current_turn", 0))
    cache = getattr(world, "_naval_penned_cache", None)
    if cache is None or cache[0] != turn:
        cache = (turn, {})
        world._naval_penned_cache = cache
    if nation in cache[1]:
        return cache[1][nation]

    enemies = set(world.get_nations_at_war_with(nation))
    penned = bool(enemies)
    if enemies:
        seen = set(world.get_nation_regions(nation))
        frontier = list(seen)
        while frontier and penned:
            region_name = frontier.pop()
            region = world.regions.get(region_name)
            if region is None:
                continue
            for adjacent in getattr(region, "adjacent_regions", []) or []:
                if adjacent in seen:
                    continue
                if is_sea_link(world, region_name, adjacent):
                    continue  # water is not a road
                if _controller(world, adjacent) in enemies:
                    penned = False
                    break
                seen.add(adjacent)
                frontier.append(adjacent)
    cache[1][nation] = penned
    return penned


def is_expedition_host(world, nation: str, holder: str) -> bool:
    """NV-5: will this court receive our army? An ally or a vassal always
    will; anyone else needs real friendship. Measured on the shipped 1805
    board: Britainâ€“Portugal 40 (the oldest alliance in Europe, and the
    reason Wellesley had a port at all), Britainâ€“Naples 30 â€” both hosts;
    Denmark, Hanover and Sardinia sit at 0 and are not."""
    if world.is_at_war(nation, holder):
        return False
    if world.get_diplomatic_state(nation, holder) in _POOLING_STATES:
        return True
    if getattr(world, "vassals", None) and world.vassals.get(holder, {}).get(
            "lord") == nation:
        return True
    key = world._make_diplo_key(nation, holder)
    return int(world.nation_relations.get(key, 0)) >= AI_EXPEDITION_HOST_RELATION


def find_ai_expedition(world, nation: str) -> Optional[Dict]:
    """NV-5 (Â§6, promoting NV-D8's expedition arm) â€” how Britain's army
    reaches the Continent now that NV-4 has closed the Channel to marching.

    History is the algorithm (Â§1): Britain's army went where a HOST received
    it. Portugal 1808 â€” Wellesley put 15,000 men ashore at Mondego Bay
    because the oldest alliance in Europe opened its ports, and marched into
    Spain from there. Sicily, Hanover 1805, the Helder. So the target search
    is ordered: a friendly or neutral shore that BORDERS the war first, an
    open enemy beach only if no host will have us.

    Returns a `naval_expedition` command dict (the same verb, the same
    executor, the same odds the player is quoted â€” GR5) or None."""
    if not has_naval_layer(world) or not world.get_nations_at_war_with(nation):
        return None
    rec = get_fleet(world, nation)
    if not rec or int(rec.get("ships", 0) or 0) <= 0:
        return None
    if not nation_is_penned_in(world, nation):
        return None  # the army has a land war to fight; it marches
    yards = set(controlled_dockyards(world, nation))
    if not yards:
        return None

    enemies = set(world.get_nations_at_war_with(nation))
    contested = {m.location for m in world.marshals.values()
                 if m.strength > 0 and m.nation in enemies}

    # Candidate landings, best first. `rank` 0 = a HOST shore on the war's
    # doorstep (Mondego Bay), 2 = an open enemy beach when no host will
    # have us. A host is a court that will actually receive an army: an
    # ally, or a friend at AI_EXPEDITION_HOST_RELATION or better. Britain's
    # authored 1805 board reads exactly right through that filter â€”
    # Portugal 40 and Naples 30 are hosts, Denmark/Hanover/Sardinia at 0
    # are not, and no army walks onto an indifferent neutral's soil.
    candidates: List[Tuple[int, int, str]] = []
    for region_name, region in world.regions.items():
        if not getattr(region, "is_coastal", False):
            continue
        if region_name in contested:
            continue  # never land into a defended beachhead
        holder = _controller(world, region_name)
        if not holder or holder == nation:
            continue  # our own soil is a garrison, not an expedition
        borders_the_war = any(
            _controller(world, adj) in enemies
            for adj in (getattr(region, "adjacent_regions", []) or [])
            if not is_sea_link(world, region_name, adj))
        if holder in enemies:
            rank = 2
        elif borders_the_war and is_expedition_host(world, nation, holder):
            rank = 0
        else:
            continue
        candidates.append((rank, -int(getattr(region, "income_value", 0) or 0),
                           region_name))
    if not candidates:
        return None
    candidates.sort()

    # The corps: the largest that the transports will lift, from a yard.
    embarkable = [
        m for m in world.get_marshals_by_nation(nation)
        if (m.strength >= AI_EXPEDITION_MIN_TROOPS
            and m.strength <= EXPEDITION_MAX_TROOPS
            and m.location in yards
            # the capture field is `captured_by` (Aug 2026 audit â€” the old
            # `is_captured` read was a dead guard; harmless only because
            # capture also zeroes strength)
            and not getattr(m, "captured_by", ""))]
    if not embarkable:
        return None
    marshal = max(embarkable, key=lambda m: m.strength)

    for _rank, _income, target in candidates:
        if target == marshal.location:
            continue
        quote = expedition_slip_odds(world, nation, target,
                                     int(marshal.strength))
        if int(quote["odds"]) < AI_EXPEDITION_MIN_ODDS:
            continue
        return {"marshal": marshal.name, "action": "naval_expedition",
                "target": target, "region": target, "confirmed": True,
                "_acting_nation": nation}
    return None


def find_ai_diversion(world, nation: str) -> Optional[Dict]:
    """NV-5 (Â§6) â€” the Â§5.3 Grand Diversion as an AI decision. A court whose
    invasion army is STAGED and whose ports are shut has exactly one card:
    draw the blockading fleet off station. Dormant on the shipped board
    (France is the player), live the moment anyone else wears that shoe."""
    if not has_naval_layer(world):
        return None
    rec = get_fleet(world, nation)
    if not rec or int(rec.get("ships", 0) or 0) <= 0:
        return None
    if rec.get("diversion_used") or int(rec.get("window_turns", 0) or 0) > 0:
        return None
    if not camp_staged(world, nation):
        return None  # no army on the beach â€” a window would open onto nothing
    if not _island_war_enemies(world, nation):
        return None
    return {"marshal": None, "action": "naval_diversion", "target": None,
            "_acting_nation": nation}


def ai_fleet_ceiling(world, nation: str) -> int:
    """NV-5 â€” what this court's yards and seamen support: AI_FLEET_CEILING_
    FACTOR Ã— the AUTHORED establishment (Â§3.2). Measured defect this closes:
    on the August-2 probe a blockaded Spain laid down one keel every turn
    forever (30 â†’ 44 sail by turn 16, still climbing, ~70 by turn 40) for a
    net gain of 2.5 effective points, because every green hull folded its
    readiness back down to the blockade floor. The rung had no notion of
    'enough'. This is a DECISION ceiling on the AI only â€” the player's
    brakes stay the Â§3.5 three (gold, the rate cap, yards held)."""
    rec = get_fleet(world, nation) or {}
    # Legacy saves predate `established`; fall back to the live count so an
    # older campaign inherits a ceiling at its current size rather than 0.
    established = int(rec.get("established", rec.get("ships", 0)) or 0)
    return int(round(established * AI_FLEET_CEILING_FACTOR))


def find_ai_build_fleet(world, nation: str, treasury: int) -> Optional[Dict]:
    """Â§6 â€” the AI build rung (the P1.75 idiom): at war + a war chest that
    survives the keel + a live naval want (blockaded, or its own blockade
    outmatched) + room under the establishment ceiling. Same priced verb as
    the player."""
    rec = get_fleet(world, nation)
    if not rec or "readiness" not in rec:
        return None
    if not world.get_nations_at_war_with(nation):
        return None
    # NV-5: a deeper reserve than the old 2Ã— â€” a naval program must never be
    # the reason an army goes unrecruited.
    if int(treasury) <= AI_FLEET_TREASURY_RESERVE * SHIP_COST:
        return None
    if int(rec.get("ships", 0) or 0) >= ai_fleet_ceiling(world, nation):
        return None
    want = is_blockaded(world, nation)
    if not want and rec.get("posture") == "blockade":
        # Its blockade is outmatched: some at-war enemy fleet out-weighs it.
        own = effective_strength(rec)
        want = any(
            world.is_at_war(nation, other) and eff > own
            for other, eff in ((n, effective_strength(r))
                               for n, r in iter_fleets(world))
            if other != nation)
    if not want:
        return None
    if check_build_fleet(world, nation) is not None:
        return None
    return {"marshal": None, "action": "build_fleet", "target": None,
            "_acting_nation": nation}
