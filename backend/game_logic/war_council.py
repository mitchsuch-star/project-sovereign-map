"""The War Council — AI-3, the Decision for War (docs/AI_INTENT_SPEC.md
§4.3, §4.3a, §13.1 AI-3c; gate record §16; landing record §17).

The missing first link the phase exists to fix (§0): before this module no
AI nation could ever DECIDE to go to war — the coalition was a global
anti-France threat scalar, not a decision. The war council gives a court
with a live acquire design, an exhausted ladder, favourable force and a
justification the ability to enter a war for itself — fore-warned, priced,
courtable, and (via AI-4b) endable.

Contracts honoured here:

- **No new PEACE→WAR edge** (§0.1 Correction A): the council calls
  `diplomacy.declare_war` — the same function `combat_executor.py`'s seam
  calls — at the ANNOUNCEMENT, so the seam's own declaration later finds
  the war live and is a no-op (§4.3a-1).
- **The ladder must have been climbed** (§5 pin 8): declaration requires
  prior refused asks / a refused coercive demand on the SERIALIZED
  `diplomatic_refusals` record — or a §3.3 renege grievance, which may
  skip rungs (Schönbrunn → Jena). No cold-open wars.
- **Fore-warning before war, always** (§4.3): a crisis is opened (beat 2,
  The Brewing Crisis), coerces (beat 3's AI-AI arm, the coercive demand),
  and only then declares — never earlier than `CRISIS_FOREWARN_TURNS`
  turns of FOREGROUNDED tenure. One foregrounded crisis world-wide (the
  §4.6a tempo rule); background crises climb silently and surface when
  the foreground clears.
- **Every foregrounded crisis ends on screen** (§5 pin 21): exactly one of
  two beats — the fore-warned war, or The Crisis Passes (beat 7) with its
  cause named and the instrument credited (§12.1's taxonomy, widened by
  AI-3r §2.5-1: satisfied / bought off / deterred / starved / exposed /
  outmatched / penniless — every reachable cause has its OWN copy, and no
  cause is ever rendered under another's string).
- **AI-vs-AI only in v1** (§16.2): a player-targeted design expresses
  `coerce` through the NA-5 ultimatum and `fight` through the coalition
  machinery — the campaign's central pressure — never a unilateral
  declaration (the NA-5 pin stands).
- **The exposure calculus replaces D1's cap** (AI_WAR_DECISION_SPEC.md
  §6.1 Q1, amending AI_INTENT_SPEC §6 D1): `MAX_SIMULTANEOUS_AI_WARS` is
  DELETED — the ceiling on simultaneous wars is what each court can
  afford to leave behind (`get_rear_reserve`/`get_free_strength`), plus
  the one-design-war-per-court rule and the AI-4a step-5 self-threat
  costs. The runaway guard lives in the SUITE (`SWEEP_WAR_ALARM`), not
  the engine.
- **Pin 15**: the council never fore-warns a crisis whose declaration
  predicate is already refused (`can_declare_war` is the shared preview,
  §4.3a-4), and the combat seams abort on a refused declaration.
- **Deckless-neutral** (§5 pin 18): no deck → no intent → no crisis; the
  bare suite world and the legacy fixture world never enter this module's
  behaviour (process returns [] with `war_intents` empty).

Serialized state: ONE new world field — `world.war_intents`
(coveter → crisis record). Everything else is derived per turn or rides
already-serialized containers (`war_instances` records gain
`ai_initiated` / `design_id` / `stated_reason` keys; `war_objectives`
records gain `design` and design-scoped `target_regions` — reuse, not a
new war-goal system).
"""

from typing import Dict, List, Optional

# ── Blessed numbers (in-band tunable; shape changes escalate) ──────────
# AI-3r §6.1 Q1: MAX_SIMULTANEOUS_AI_WARS is DELETED — it never bound in
# the qualifying arithmetic (probe memo AI_3R_PROBE_2026_07_25.md), it
# could not be rendered diegetically, and the costs that should govern
# (the exposure gate + one design war per court + AI-4a self-threat)
# are built. SWEEP_WAR_ALARM is the SUITE's runaway tripwire (N8), not
# an engine rule — a 40-turn seeded run producing more council wars than
# this sends a human to look at the costs.
SWEEP_WAR_ALARM = 6                # N8: per 40 turns, suite-level only
CRISIS_FOREWARN_TURNS = 2          # foregrounded tenure before declaration
CRISIS_REFUSALS_REQUIRED = 2       # ladder gate: refused asks on record
AI_WAR_FORCE_RATIO = 1.25          # the NA-5 strength idiom
AI_WAR_TREASURY_FLOOR = 500        # no bankrupt adventures
CRISIS_HARD_STALL_TURNS = 4        # preview-refused predicate → starved
CRISIS_SOFT_STALL_TURNS = 8        # ladder/restraints blocked → cooled
COERCIVE_DEMAND_TYPE = "coercive_demand"

# AI-3r §2.3 (gate Q3): deny_regions and contain_hegemon — the highest-
# base, most historically warlike designs — may open crises. The D3
# guard is structural: the v1 AI-vs-AI rule already excludes the player,
# so a containment war against France stays the coalition's business
# (pinned). Ruling R4: their objectives keep the [capital] default —
# get_agenda_military_targets stays acquire-only (the NA-3 §3.1
# never-self-conquest pin is preserved verbatim).
CRISIS_ELIGIBLE_DESIGNS = ("acquire_regions", "deny_regions",
                           "contain_hegemon")

# SF-LB-2 "The Defenceless Prize" (SCORE_FINISH_SPEC.md §6.4, RULED
# October 3, 2026). Measured on seven 40-turn ambient seeds
# (tools/_sf_lb1_fight_bar_probe.py): Prussia's design on Hanover had the
# ladder climbed (turns 3–13), every restraint clear and a holder fielding
# NO corps — and never opened, because the only gate left was the `fight`
# bar (85) that AI-3r's N7 keeps where it is ("the terms climb to the bar,
# the bar stays"). The ruling adds ONE derived reading, shared by the two
# clauses it feeds (never two copies — pinned by an AST census):
#   `holder_outmatched`: the holder's standing strength plus its
#   guarantors' is at most HOLDER_OUTMATCHED_FRACTION of the asker's FREE
#   strength (the restraint gate's own arithmetic); an armyless holder
#   counts.
# Clause 1 lives in intent.py (`WEIGHT_HOLDER_OUTMATCHED`, under
# `A_HOLDER_WITHOUT_AN_ARMY_IS_A_PRIZE`). Clause 2 lives here: an AI-vs-AI
# ACQUIRE crisis opens at `coerce` (72) instead of `fight` (85) when that
# reading holds AND `_restraint_block_reason` is None; everything after the
# opening — the fore-warning, the coercive demand, the ladder and every
# restraint at the declaration — is exactly AI-3's. The fight bar stays 85
# for everything else. False = AI-3r's tree byte for byte.
THE_DEFENCELESS_PRIZE_OPENS_AT_COERCE = True
HOLDER_OUTMATCHED_FRACTION = 0.5   # blessed §6.4-1: "at most HALF"
# SF-LB-2 addendum (AI_WAR_DECISION_SPEC.md §8, October 3, 2026 — a
# consequence the ruling did not foresee, measured on the seven-seed probe):
# the §6.4 terms lift courts the restraints already forbid onto the
# `fight` road, which never read the restraints at the OPENING — Sardinia
# fore-warned a war on Austria twice with a free strength of 0 (cooling
# `outmatched` eight turns later, twice), Russia a war on Sweden while at
# war with France (cooling `starved`). A fore-warning with no road is pin
# 15's lie one gate over ("never fore-warn a refused predicate"), and pin
# 13's soap opera. The ruling made the coerce road open only with every
# restraint clear; with this lever the fight road honours the SAME
# predicate — a crisis opens only where its court could declare today.
# The restraints are re-read at the declaration exactly as before, and a
# restraint that APPEARS after the opening still cools the crisis on
# screen (the soft stall). False = AI-3's fight-road opening byte for byte.
A_CRISIS_OPENS_ONLY_WHERE_IT_CAN_DECLARE = True
# SF-LB-2b "The Chest the Council Can Spend" (SCORE_FINISH_SPEC.md §6 row
# 14, RULED October 3, 2026): the council sits AFTER the admin phase's
# spending and BEFORE the income phase, so the chest it read at the
# OPENING was the post-spending, pre-income purse — an AI court that
# spends its whole purse every turn read `penniless` on every seed until
# its unseeded economy cleared AI_WAR_TREASURY_FLOOR on the same turn
# everywhere (Prussia→Hanover: turn 9 on six of seven seeds). With this
# lever the OPENING (step 3) reads the chest the court will have when
# this turn ends — the ledger's own projection, `ledger.chest_forecast`,
# the ONE seam `reforms.lapse_forecast` reads (never a second copy); the
# DECLARATION (step 1) keeps the live chest, so no bankrupt adventure is
# ever declared. Every court reads the same seam (GR5). False = the
# SF-LB-2 tree byte for byte (the turn-9 lockstep returns).
THE_COUNCIL_SPENDS_THE_TURNS_INCOME = True

# The §12.1 cause taxonomy for beat 7 (display strings composed
# backend-side, R7), widened by AI-3r §2.5-1 + ruling R2: every cause the
# engine can produce has its OWN copy — `starved` never again renders for
# a gate refusal that was not decayed opportunism (the §0.3 defect).
_CRISIS_CAUSE_COPY = {
    "satisfied": "the design is satisfied — the want is won",
    "bought_off": "the design was bought off — compensation stands",
    "deterred": "the guarantee raised the price past reach",
    "starved": "the moment passed — opportunism decayed",
    "exposed": "the frontier could not be stripped — {threat} stands "
               "armed at their back",
    "outmatched": "the odds never came — the design outweighs the army",
    "penniless": "the treasury could not bear a campaign",
    # Aug 30, 2026 review: a crisis whose pair reached WAR by ANOTHER road —
    # a mutual-crisis counterpart declaring first, a guarantor joining, a
    # coalition cascade — had no arm at all. `can_declare_war` answered
    # `already_at_war`, which the loop below read as a refused predicate and
    # counted as a STALL, so after the hard-stall turns the beat announced
    # "the crisis passes — the moment passed" while that very war was being
    # fought. The design is not abandoned; it is being pressed by arms.
    "war_joined": "the war came by another road — the design is pressed "
                  "by arms",
    "overtaken": "events overtook the design — the quarrel is set aside, "
                 "the want unwon",
}

# SHORT-form beat-7 cause copy, for the compact surfaces: the campaign-log
# one-liner and the dispatch headline. The long form above rides the event
# `message`; these two surfaces re-derive from the raw `cause` field, so they
# MUST cover the same taxonomy. In-game review July 25, 2026 found both
# consumers carrying private 4-entry copies that degraded AI-3r's three new
# causes to the `starved` phrase — reintroducing the exact §0.3 lie ("the
# moment passed" for a refusal that was really exposure/force/treasury).
# Single source now; consumers call crisis_cause_phrase().
_CRISIS_CAUSE_SHORT = {
    "satisfied": "the want is won",
    "bought_off": "bought off",
    "deterred": "deterred by guarantee",
    "starved": "the moment passed",
    "exposed": "their frontier could not be stripped",
    "outmatched": "the odds never came",
    "penniless": "the treasury could not bear it",
    "war_joined": "the war came anyway",
    "overtaken": "overtaken by events",
}


def crisis_cause_phrase(cause: str) -> str:
    """Short beat-7 stand-down phrase for a cause id.

    Every cause the engine can emit has its own entry, so the `starved`
    copy never stands in for an exposure / force / treasury refusal.
    """
    return _CRISIS_CAUSE_SHORT.get(str(cause or ""), "the moment passed")


# Soft-gate block → the beat-7 cause it truthfully renders as. "busy"
# and a fallen ladder ARE decayed moments; the three named refusals are
# facts about the coveter and render as themselves.
_SOFT_BLOCK_CAUSE = {
    "exposed": "exposed",
    "outmatched": "outmatched",
    "penniless": "penniless",
    "busy": "starved",
    "ladder": "starved",
}


def _standing_strength(world, nation: str) -> int:
    return sum(int(m.strength) for m in world.marshals.values()
               if getattr(m, "nation", None) == nation and m.strength > 0)


# ── AI-3r §2.1: the rear-security reserve (the exposure calculus) ───────
# A great power does not commit its field army to a war of choice if that
# leaves its own soil open to a neighbour who might take it. Decision
# layer only — never a combat modifier (Golden Rule 1 untouched), and
# NEVER a gate on the player's own orders (gate Q5: display-only for
# France, pinned).

RESERVE_CAP_FRACTION = 0.60   # N1: never garrison more than 60% of the army
MENACE_BAND_COLD = 1.0        # N2: relation <= -40 (or open war)
MENACE_BAND_CHILLY = 0.6      # N2: relation <= 0
MENACE_BAND_COOL = 0.3        # N2: relation <= 30
MENACE_BAND_WARM = 0.1        # N2: relation > 30 — an ally-ish neighbour
                              #     still costs something


def _menace_band(relation: int) -> float:
    if relation <= -40:
        return MENACE_BAND_COLD
    if relation <= 0:
        return MENACE_BAND_CHILLY
    if relation <= 30:
        return MENACE_BAND_COOL
    return MENACE_BAND_WARM


def _wary_posture(world, nation: str, neighbour: str) -> float:
    """§2.6: the authored `wary_of` multiplier — scenario statecraft data
    read through the get_statecraft chokepoint; absent → 1.0."""
    try:
        wary = (world.get_statecraft(nation) or {}).get("wary_of") or {}
        return float(wary.get(neighbour, 1.0) or 1.0)
    except (TypeError, ValueError):
        return 1.0


def get_exposure_view(world, nation: str) -> Dict:
    """§2.1: {standing, reserve, free, worst_threat, worst_menace,
    threats:[{nation, menace}...]} — every term already in the world, no
    new serialized field. Per-turn cached; flushed through
    invalidate_bloc_members_cache (region control, vassalage, war and
    alliance geometry all reach it). Relations/strength staleness is
    turn-granular by design (the intent-cache choice)."""
    cache = getattr(world, "_exposure_cache", None)
    cache_turn = getattr(world, "_exposure_cache_turn", -1)
    if cache is None or cache_turn != int(world.current_turn):
        cache = {}
        world._exposure_cache = cache
        world._exposure_cache_turn = int(world.current_turn)
    if nation in cache:
        return cache[nation]

    own = _standing_strength(world, nation)
    active = set(world.get_active_nations())
    own_family = world._top_overlord(nation)
    threats = []
    for neighbour in world.get_neighbouring_nations(nation):
        if neighbour == nation or neighbour not in active:
            continue
        if world._top_overlord(neighbour) == own_family:
            continue  # own vassals, the lord, sibling clients
        if world.get_diplomatic_state(nation, neighbour) in (
                "ALLIANCE", "DEFENSIVE_ALLIANCE"):
            continue
        strength = _standing_strength(world, neighbour)
        if strength <= 0:
            continue
        if world.is_at_war(nation, neighbour):
            band = MENACE_BAND_COLD  # an open enemy is the full menace
        else:
            band = _menace_band(int(world.nation_relations.get(
                world._make_diplo_key(nation, neighbour), 0) or 0))
        menace = int(strength * band * _wary_posture(world, nation, neighbour))
        if menace > 0:
            threats.append({"nation": neighbour, "menace": menace})
    threats.sort(key=lambda t: (-t["menace"], t["nation"]))

    # Q2 (gate): MAX single menace, not the sum — a state garrisons
    # against its worst credible single opponent, clamped so a terrified
    # court still keeps 40% of its army marchable.
    worst = threats[0] if threats else None
    reserve = int(min(worst["menace"] if worst else 0,
                      RESERVE_CAP_FRACTION * own))
    view = {
        "nation": nation,
        "standing": int(own),
        "reserve": int(reserve),
        "free": int(max(0, own - reserve)),
        "worst_threat": worst["nation"] if worst else None,
        "worst_menace": int(worst["menace"]) if worst else 0,
        "threats": threats,
    }
    cache[nation] = view
    return view


def exposure_against(world, nation: str, target: str) -> Dict:
    """OCT27-D6(a) (ruled as recommended, S14i): `nation`'s exposure when
    it prices ITS war on `target` — the general view (`get_exposure_view`)
    with the target and its live guarantors struck from the reserve's
    threats. Their armies already stand in the holder's scale
    (`_holder_scale`); counting them again made a court whose worst neighbour
    IS the target need (band + 1.25)x its strength. Read by the exposed gate,
    the outmatched reading, the rear-quiet weight term and beat 7's named
    threat. Keys as the general view's. Down (`get_exposure_view(a[0],
    a[1])`): the general view."""
    view = get_exposure_view(world, nation)
    from backend.game_logic.instruments import live_guarantees_of
    struck = {str(target)} | {str(g.get("guarantor") or "")
                              for g in live_guarantees_of(world, target)}
    threats = [t for t in view["threats"] if t["nation"] not in struck]
    worst = threats[0] if threats else None
    own = int(view["standing"])
    reserve = int(min(worst["menace"] if worst else 0, RESERVE_CAP_FRACTION * own))
    return {
        "nation": nation,
        "standing": own,
        "reserve": reserve,
        "free": int(max(0, own - reserve)),
        "worst_threat": worst["nation"] if worst else None,
        "worst_menace": int(worst["menace"]) if worst else 0,
        "threats": threats,
    }


def get_rear_reserve(world, nation: str) -> int:
    """§2.1: strength that CANNOT march — held against the worst armed
    neighbour."""
    return int(get_exposure_view(world, nation)["reserve"])


def get_free_strength(world, nation: str) -> int:
    """§2.1: standing minus the rear reserve, floored at 0 — the only
    strength the war council may weigh for a war of choice."""
    return int(get_exposure_view(world, nation)["free"])


def count_ai_initiated_wars(world) -> int:
    """Live wars the war council opened. AI-3r §2.4: the CAP role is
    deleted — this survives as the sweep/AI-V metric only (no production
    caller gates on it).

    Review fix [r2 HIGH]: a war whose loser was ELIMINATED never receives
    `ended_turn` (elimination bypasses the settlement path by design), so
    counting on `ended_turn` alone jammed the old cap permanently after
    two successful minor-conquests — the feature's own happy path. A war
    is LIVE here only while it still has two standing sides.
    """
    count = 0
    for war in (getattr(world, "war_instances", {}) or {}).values():
        if not war.get("ai_initiated") or war.get("ended_turn") is not None:
            continue
        if len(war.get("active_participants") or []) < 2:
            continue  # decided by elimination — no longer a live war
        count += 1
    return count


def can_declare_war(world, aggressor: str, target: str,
                    war_objective: str = "conquest") -> Dict:
    """§4.3a-4: the shared declaration preview — armistice cooldown,
    objective validity and availability, war-instance side conflict, and
    the treaty-in-the-way state — so a refused declaration is a fail-safe
    rather than the normal path, and a fore-warned crisis never dies
    silently. Read-only.
    """
    from backend.game_logic.diplomacy import (
        OFFENSIVE_OBJECTIVE_TYPES,
        OPEN_MOVEMENT_STATES,
        _get_objective_availability,
    )
    from backend.game_logic.settlement_helpers import validate_war_declaration

    if not aggressor or not target or aggressor == target:
        return {"ok": False, "reason": "self_war"}
    state = world.get_diplomatic_state(aggressor, target)
    if state == "WAR":
        return {"ok": False, "reason": "already_at_war"}
    from backend.game_logic.diplomacy import declaration_cooldown_left
    if declaration_cooldown_left(world, aggressor, target) > 0:
        return {"ok": False, "reason": "armistice_cooldown"}
    if war_objective not in OFFENSIVE_OBJECTIVE_TYPES:
        return {"ok": False, "reason": "invalid_objective"}
    availability = _get_objective_availability(world, aggressor, target, war_objective)
    if availability and not availability.get("available", True):
        return {"ok": False, "reason": "objective_unavailable"}
    validation = validate_war_declaration(
        world, aggressor, target,
        entry_path="war_declaration", reason="war_council_preview",
    )
    if not validation.get("ok") and not validation.get("merge_required"):
        return {"ok": False, "reason": "war_instance_side_conflict"}
    if state in OPEN_MOVEMENT_STATES:
        # §4.3a-2: a coveter holding an open-movement treaty must break it
        # first — a visible ladder step between coerce and fight.
        return {"ok": False, "reason": "treaty_in_the_way"}
    return {"ok": True, "reason": ""}


def exit_shared_wars_for_defection(world, defector: str, new_enemy: str,
                                   reason: str = "coalition_defection") -> Dict:
    """§4.3a's mainline blocked case, lifted from the VS-6 side-exit idiom
    (vassal.py): a co-belligerent cannot declare on a nation that shares
    its war sides — peace out the defector's WAR pairs first, then the
    caller declares. Used by scripted defection paths (the DoD betrayal
    reachability); organic use belongs to AI-5b(ii), the volte-face.
    """
    from backend.game_logic.diplomacy import (
        cleanup_war_end,
        set_diplomatic_state,
    )
    exited = []
    for other in list(world.get_active_nations()):
        if other in (defector, new_enemy):
            continue
        if world.get_diplomatic_state(defector, other) == "WAR":
            set_diplomatic_state(world, defector, other, "PEACE", reason)
            cleanup_war_end(
                world,
                world._make_diplo_key(defector, other),
                conclude_objectives=True,
            )
            exited.append(other)
    return {"success": True, "exited": exited}


# ── The war aim (T3-2 — the Tier-3 gate record §13.2 R1/R3) ─────────────

def _instance_core_aims(world, inst: Dict) -> Dict[str, set]:
    """§13.2 R1's CORE, per participant of `inst` (the T3-2 derivation,
    unchanged): every `war_objectives` record of a pair inside this
    war's participants (`target_regions` are resolved names — the
    council writes the design's provinces), plus the active ACQUIRE
    design's regions currently held by the opposing side
    (overlord-resolved — a client's soil reads as its lord's).
    DELIBERATELY NARROW: enemy soil is never automatically in-aim."""
    attackers = set(inst.get("attackers") or [])
    defenders = set(inst.get("defenders") or [])
    party = attackers | defenders
    objectives = getattr(world, "war_objectives", {}) or {}
    core: Dict[str, set] = {}
    for nation in sorted(party):
        regions = set()
        for diplo_key, records in objectives.items():
            pair = set(str(diplo_key).split("|"))
            if nation not in pair or not pair <= party:
                continue
            record = (records or {}).get(nation)
            if isinstance(record, dict):
                regions.update(
                    str(r) for r in (record.get("target_regions") or []))
        opposing = defenders if nation in attackers else attackers
        try:
            from backend.game_logic.agendas import get_active_agenda
            view = get_active_agenda(nation, world)
        except Exception as exc:
            from backend.errors import report
            report(exc, "war_council._instance_core_aims: "
                        "get_active_agenda")
            view = None
        if (view is not None
                and getattr(view, "type", "") == "acquire_regions"):
            for region_name in getattr(view, "regions", ()) or ():
                region = (getattr(world, "regions", {}) or {}).get(
                    str(region_name))
                holder = (getattr(region, "controller", None)
                          if region is not None else None)
                effective = ((world._top_overlord(holder) or holder)
                             if holder else None)
                if effective in opposing or holder in opposing:
                    regions.add(str(region_name))
        core[nation] = regions
    return core


def _pair_capital(world, enemy: str) -> Optional[str]:
    """R1's CAPITAL DEFAULT for one pair: the enemy's own seat. Per
    PAIR, never per side — a court's object against X names X's
    capital, not a co-belligerent's (the conduct extension's first cut
    took the opposing LEADER's capital and gave Bavaria, fighting
    Austria inside France's 1805 war, London as her aim)."""
    capital = world.get_nation_capital(enemy) if enemy else None
    return str(capital) if capital else None


def war_aims_of_instance(world, inst: Dict) -> Dict[str, List[str]]:
    """§13.2 R1's full union per participant, THE instrument's per-war
    aims (`RunCapture._war_aims` delegates here): the core
    (`_instance_core_aims`) ∪ the CAPITAL DEFAULT of every pair the
    participant fights in this war — each opposing court's seat.

    The capital default is R1's own union term (the approved plan:
    "∪ the objective's capital default"); T3-1 under-implemented it —
    the boot pairs carry DEFENSE records, so no enemy capital ever sat
    in an aim — and the T3-3 conduct extension caught it the moment
    the rule left every enemy capital, Paris included, unstormable.
    Decapitation is war-prosecution, the era's own object."""
    attackers = set(inst.get("attackers") or [])
    defenders = set(inst.get("defenders") or [])
    core = _instance_core_aims(world, inst)
    aims: Dict[str, List[str]] = {}
    for nation in sorted(attackers | defenders):
        regions = set(core.get(nation) or ())
        opposing = defenders if nation in attackers else attackers
        for enemy in opposing:
            capital = _pair_capital(world, enemy)
            if capital:
                regions.add(capital)
        if regions:
            aims[nation] = sorted(regions)
    return aims


def _opposed_live(inst, nation: str, enemy: str) -> bool:
    """Does the live instance hold the pair on opposite sides?"""
    if not isinstance(inst, dict) or inst.get("ended_turn") is not None:
        return False
    attackers = set(inst.get("attackers") or [])
    defenders = set(inst.get("defenders") or [])
    return ((nation in attackers and enemy in defenders)
            or (nation in defenders and enemy in attackers))


def has_live_war_record(world, nation: str, enemy: str) -> bool:
    """Is there a live war RECORD (instance) between the pair? A war
    that exists only as a diplomatic state — the legacy fixture world,
    a crafted board — has no aim record to read."""
    return any(_opposed_live(inst, nation, enemy)
               for inst in (getattr(world, "war_instances", {}) or {}).values())


def war_aim_core(world, nation: str, enemy: str) -> List[str]:
    """The pair's STATED object — R1's core (the objective records and
    the acquire design's arm) over every LIVE instance holding the pair
    on opposite sides, WITHOUT the capital default. What the words
    speak and the leash pulls toward: a court's object is what it
    declared and designed, never merely the enemy's seat."""
    aims: set = set()
    for inst in (getattr(world, "war_instances", {}) or {}).values():
        if _opposed_live(inst, nation, enemy):
            aims.update(_instance_core_aims(world, inst).get(nation) or ())
    return sorted(aims)


def war_aim(world, nation: str, enemy: str) -> List[str]:
    """§13.2 R3 — ONE public read of the existing objective record:
    `nation`'s FULL aim against `enemy` — the stated object
    (`war_aim_core`) plus the pair's capital default (the enemy's seat)
    wherever a live war record stands. `[]` with no record. The union
    over a court's enemies is exactly the instrument's per-war aims
    (`war_aims_of_instance`). The capital default is a PERMISSION and
    a metric credit (decapitation is war-prosecution), never a stated
    object: the words and the leash read the core alone."""
    aims = set(war_aim_core(world, nation, enemy))
    if has_live_war_record(world, nation, enemy):
        capital = _pair_capital(world, enemy)
        if capital:
            aims.add(capital)
    return sorted(aims)


def _regions_clause(regions: List[str]) -> str:
    """'Milan', 'Milan and Piedmont', 'Milan, Piedmont and Savoy'."""
    names = [str(r) for r in regions]
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    return f"{', '.join(names[:-1])} and {names[-1]}"


def war_aim_outstanding(world, nation: str, enemy: str) -> List[str]:
    """The OUTSTANDING stated object — `war_aim_core`'s regions the
    court does not presently hold (itself or through a client). A boot
    DEFENSE objective puts a court's own soil in its core, which is
    right for the march gauge (recapturing Vienna is never drift);
    what remains OUTSTANDING is what the words speak (T3-2) and what
    the leash pulls toward (T3-3) — a held province is no object, a
    LOST one joins the moment it falls (the recapture spoken, and
    marched for). The capital default is deliberately absent: it
    permits the storm, it does not steer the march (the conduct
    extension's catch — with the seat in the pull, Austria marched
    across France for Paris instead of for Italy, and every coalition
    court's peace-table line read 'Paris', pushing the PC-F46 table
    below its fold)."""
    outstanding = []
    for region_name in war_aim_core(world, nation, enemy):
        if _held_by_house(world, nation, region_name):
            continue
        outstanding.append(str(region_name))
    return outstanding


def _held_by_house(world, nation: str, region_name: str) -> bool:
    """Is `region_name` held by `nation` itself or through a client (the
    overlord-resolved read every aim consumer shares)?"""
    region = (getattr(world, "regions", {}) or {}).get(str(region_name))
    holder = getattr(region, "controller", None) if region is not None else None
    if not holder:
        return False
    return holder == nation or (world._top_overlord(holder) or holder) == nation


def war_aim_clause(world, nation: str, enemy: str) -> str:
    """The aim's WORDS alone — 'Milan, Piedmont and Savoy'; '' when
    nothing is outstanding (`war_aim_outstanding`, the shared read)."""
    return _regions_clause(war_aim_outstanding(world, nation, enemy))


def a_leash_pulls_the_march() -> bool:
    """T3-3 "the leash" (the Tier-3 gate record §13.2 R4;
    `DYNAMISM_SPEC.md` §2 Tier 3; November 8, 2026): an AT-WAR court's
    pull set widens from its design's unmet targets to its WAR AIMS —
    the objective record's targets and the recapture of its own lost
    soil join the pick bias (`aim_pull_set`, consulted by the one
    covet memo the four ranged pick surfaces read). The recall rides
    the aim itself: a lost home province is a defense-objective
    target, hence outstanding, hence in the pull — and P3.7 keeps the
    hard recall, structurally earlier in the ladder. Down: the
    pre-T3-3 read — the design's targets alone, a court at war never
    credits its objective and never feels the pull home."""
    return True


def annexation_follows_the_aim() -> bool:
    """T3-3's second half, the CONDUCT rule (§13.2 R4's own sentence —
    "a corps that should not be there should not capture there";
    extended into the slice by the user's word, November 8, 2026,
    after the first chain read the pull ALONE raising the debt 397 →
    421: the leash re-aimed the marches and the annexation rungs
    grabbed every off-aim province along the longer roads): an
    at-war AI court ANNEXES only its aim — the deliberate annexation
    verbs (P4.5 capture-undefended, P4.25 garrison storms) skip soil
    outside the pull. Field battles stay lawful everywhere (destroying
    armies is war-prosecution, never annexation); their incidental
    flips are the measured residual. Down: the pre-conduct reading —
    a court at war grabs whatever lies adjacent."""
    return True


def the_conduct_binds_every_runner() -> bool:
    """T3-5 (the Tier-3 gate record §13.2 R7 kept — no France-literal mode):
    the conduct rule binds WHOEVER runs the AI's rungs. The player-nation
    clause T3-3 wrote ("the player's own rungs never run here") never
    bound a human — the turn manager runs the AI's rungs for the AI courts
    alone (`_process_enemy_turns`; the debug turn refuses the player) — so
    its only reach was the AI-run France of the harness
    (`tools/ai_france_sweep.py`), left free to annex off its aim: the
    deploy gate's AI-France surface (France's `captures_outside_aim`
    entry) could never read 0. Down: the exemption restored."""
    return True


def _is_enemy_seat(world, nation: str, region_name: str) -> bool:
    """Is `region_name` the capital of a court `nation` holds a live war
    record against? R1's capital default read as a PERMISSION."""
    for enemy in world.get_nations_at_war_with(nation):
        if (_pair_capital(world, enemy) == str(region_name)
                and has_live_war_record(world, nation, enemy)):
            return True
    return False


def annexation_permitted(world, nation: str, region_name: str,
                         marshal=None) -> bool:
    """May `nation` deliberately ANNEX `region_name`? The conduct rule:
    an at-war court annexes only its aim — the pull (`aim_pull_set`:
    the design's unmet targets and the outstanding stated objects, the
    recapture of its own lost soil among them) and any ENEMY'S SEAT
    (R1's capital default, as a permission: decapitation is
    war-prosecution).

    The rule READS THE WAR'S AIM RECORD, so it binds only where one
    exists — a live war instance between the court and the province's
    holder (or the holder's overlord). A war that stands only as a
    diplomatic state (the legacy rollback world, a crafted board) has
    no aim to read, and the court fights there as it always did: the
    first conduct cut froze the AI outright on such worlds — the
    extension's own catch. A VASSAL'S contingent fights its lord's war
    under the lord's direction (VD-C) — exempt. The player's nation was
    wholly exempt until T3-5 (`the_conduct_binds_every_runner`): a human's
    own commands never pass through here, and the one human road that runs
    the AI's rungs — a marshal granted INDEPENDENT COMMAND
    (`EnemyAI.decide_single_action`, the player's grant) — stays exempt by
    the `marshal` it acts with; an AI-run France (the harness) is bound. A
    read with no `marshal` keeps the T3-3 reading (it cannot tell the
    two apart)."""
    if not annexation_follows_the_aim():
        return True
    if nation == getattr(world, "player_nation", "France"):
        if (not the_conduct_binds_every_runner() or marshal is None
                or getattr(marshal, "autonomous", False)):
            return True
    if nation in (getattr(world, "vassals", {}) or {}):
        return True
    region = (getattr(world, "regions", {}) or {}).get(str(region_name))
    holder = getattr(region, "controller", None) if region is not None else None
    if not holder:
        return True
    effective = world._top_overlord(holder) or holder
    if not (has_live_war_record(world, nation, holder)
            or has_live_war_record(world, nation, effective)):
        return True
    return (str(region_name) in aim_pull_set(world, nation)
            or _is_enemy_seat(world, nation, region_name))


def aim_pull_set(world, nation: str) -> frozenset:
    """§13.2 R4 — THE leash's pull set, ONE predicate: the active
    design's unmet targets (the NA-3 covet bias's own read — byte-
    identical at peace and with the seam down) ∪ for every enemy at
    WAR, the OUTSTANDING stated object (`war_aim_outstanding` — the
    objective records and the design arm, minus what the court or its
    clients hold; the capital default steers nothing). Pure and
    uncached here — the consumer memoizes per (nation, turn)
    (`enemy_ai`'s covet memo, GR8)."""
    from backend.game_logic.agendas import get_agenda_military_targets
    pull = set(get_agenda_military_targets(nation, world))
    if a_leash_pulls_the_march():
        for enemy in world.get_nations_at_war_with(nation):
            pull.update(war_aim_outstanding(world, nation, enemy))
    return frozenset(pull)


def war_aim_line(world, nation: str, enemy: str) -> str:
    """The aim in WORDS (Q6 — never a tooltip number): 'her object:
    Milan, Piedmont and Savoy'; '' when nothing is outstanding (the
    surfaces fold only a non-empty line)."""
    clause = war_aim_clause(world, nation, enemy)
    if not clause:
        return ""
    return f"her object: {clause}"


# ── The terms (T3-4 — the Tier-3 gate record §13.2 R5) ──────────────────
#
# A court that HOLDS the object of its war sues to lock it: AI–AI through
# the third-party settlement roads (`settlement_third_party`), AI–player
# as P8-Aim (`ai_diplomacy`). ONE predicate, both roads (GR5); only the
# consent differs — the AI's readiness, the player's answer.

AIM_SUE_SCORE = 25   # §13.2 R5's own number: the war score a held aim sues at


def _house_of(world, nation: str) -> set:
    """`nation` and every court whose top overlord it is (its clients)."""
    house = {str(nation)}
    for client in (getattr(world, "vassals", {}) or {}):
        if world._top_overlord(client) == nation:
            house.add(str(client))
    return house


def _held_within(world, courts: set, region_name: str) -> bool:
    """Is `region_name` held by one of `courts` (overlord-resolved)?"""
    region = (getattr(world, "regions", {}) or {}).get(str(region_name))
    holder = getattr(region, "controller", None) if region is not None else None
    if not holder:
        return False
    return holder in courts or (world._top_overlord(holder) or holder) in courts


def war_aim_delivered(world, nation: str, enemy: str) -> List[str]:
    """T3-4 — the stated object `nation` has TAKEN from `enemy`: for every
    acquire design in its deck (`agendas.acquire_design_regions`), the
    design's provinces lying in the boot homeland of the enemy's HOUSE
    (the enemy and its clients), counted when ALL of them are held by
    `nation`'s house. A design spanning two holders is delivered per
    enemy — Russia's Finland from Sweden while Rumelia is still the
    Porte's (the Finnish War ended at Fredrikshamn, not with the Porte).
    The council's design-war record carries the same provinces (AI-3r),
    so the design is the one read. `[]` without a live war record (T3-3's
    lesson: a war standing only as a diplomatic state has no aim to read).
    The capital default is never here — a court that had to take the
    enemy's seat to sue would never sue."""
    if not has_live_war_record(world, nation, enemy):
        return []
    homes = getattr(world, "nation_starting_regions", {}) or {}
    enemy_home = set()
    for court in _house_of(world, enemy):
        enemy_home.update(str(r) for r in (homes.get(court) or []))
    if not enemy_home:
        return []
    from backend.game_logic.agendas import acquire_design_regions
    delivered = set()
    for regions in acquire_design_regions(world, nation):
        part = [r for r in regions if r in enemy_home]
        if part and all(_held_by_house(world, nation, r) for r in part):
            delivered.update(part)
    return sorted(delivered)


def war_aim_held(world, nation: str, enemy: str, side=()) -> bool:
    """T3-4 — is `nation`'s aim against `enemy` HELD? A DELIVERED gain
    (`war_aim_delivered`) and nothing still owed: (a) no province of its
    live stated object (`war_aim_core`) held by the enemy's house — it
    still wants that from this enemy; and (b) none of its own homeland
    held by the enemy's bloc or by `side` (the instance road passes the
    whole opposing side) — a peace would title it away (SR-1a's status
    quo). §13.2 R5's literal reading was degenerate: the design arm
    counts only provinces the enemy still holds, and a defense record's
    provinces are the court's own homeland, so every defender would have
    'held' its aim on turn 1. A held aim is one that was GAINED; a court
    with no stated gain never sues on 'held' (the existing roads stand).

    The enemy's own SEAT is skipped in (a): a bare declaration's objective
    defaults to the enemy's capital (`declare_war`'s road; the council
    writes its design's provinces over it), and §13.2 R5 reads the
    capital default NEVER — a court that had to take Stockholm to sue for
    Scania would never sue. A design that names a seat (Hanover's) still
    needs it in hand: it is delivered only when held."""
    if not war_aim_delivered(world, nation, enemy):
        return False
    enemy_house = _house_of(world, enemy)
    seat = _pair_capital(world, enemy)
    for region_name in war_aim_core(world, nation, enemy):
        if region_name == seat:
            continue
        if _held_within(world, enemy_house, region_name):
            return False
    blockers = set(world.get_bloc_members(enemy) or []) | {str(enemy)}
    blockers |= {str(n) for n in (side or ())}
    homes = getattr(world, "nation_starting_regions", {}) or {}
    for region_name in homes.get(nation) or []:
        if _held_within(world, blockers, region_name):
            return False
    return True


def aim_sue_due(world, nation: str, enemy: str, side=()) -> bool:
    """T3-4 — does `nation` sue `enemy` on its held aim? An AI court (the
    player answers letters, a client fights its lord's war), the pair's
    war score at or past `AIM_SUE_SCORE` (R5's 25 — read first, it is
    the cheap gate), and the aim held (`war_aim_held`)."""
    if nation == getattr(world, "player_nation", "France"):
        return False
    if nation in (getattr(world, "vassals", {}) or {}):
        return False
    from backend.game_logic.diplomacy import get_war_score_for
    if int(get_war_score_for(world, nation, enemy)) < int(AIM_SUE_SCORE):
        return False
    return war_aim_held(world, nation, enemy, side=side)


def _is_great_power_capital(world, region_name: str) -> bool:
    from backend.game_logic.coalition import _CANONICAL_MAJORS
    return any(world.get_nation_capital(major) == str(region_name)
               for major in _CANONICAL_MAJORS)


def aim_cessions(world, nation: str, enemy: str, *,
                 homeland_only: bool) -> List[str]:
    """T3-4 — the provinces the aim's terms CEDE: the delivered provinces
    `nation` holds ITSELF (a client's holding counts toward 'held' but
    stays with the status quo — the treaty names the signatory's ground).
    The existing road's guards: never a great power's capital (D2's
    routine-cession floor, read precisely — a client's capital such as
    Milan is a minor's); and an enemy that holds no province of its own is
    never stripped below the total-annexation score (90) — the applier
    eliminates a ceder left with nothing — and a great power never.
    `homeland_only` (the AI–AI road): the enemy's own homeland alone, the
    clause the validator carries (PC-F52's occupied-homeland cession —
    Tyrol at Pressburg); the bilateral ratifier carries any held cession."""
    delivered = war_aim_delivered(world, nation, enemy)
    if not delivered:
        return []
    from backend.game_logic.coalition import _CANONICAL_MAJORS
    from backend.game_logic.diplomacy import get_war_score_for
    from backend.game_logic.settlement_scoring import TOTAL_ANNEXATION_WAR_SCORE
    if not world.get_nation_regions(enemy):
        if (enemy in _CANONICAL_MAJORS
                or int(get_war_score_for(world, nation, enemy))
                < int(TOTAL_ANNEXATION_WAR_SCORE)):
            return []
    own_home = set((getattr(world, "nation_starting_regions", {}) or {})
                   .get(enemy) or [])
    out = []
    for region_name in delivered:
        region = (getattr(world, "regions", {}) or {}).get(region_name)
        if region is None or getattr(region, "controller", None) != nation:
            continue
        if homeland_only and region_name not in own_home:
            continue
        if _is_great_power_capital(world, region_name):
            continue
        out.append(region_name)
    return out


def side_aim_cessions(world, war: Dict, winner_side: str, loser: str,
                      leader: str, taken=()) -> List[Dict]:
    """T5-GIFT (DY-1f, session B — the Emperor's gift, the AI's road): the
    co-belligerents' DELIVERED aims the leader signs for at its aim peace.
    For each ACTIVE court on the winner's side other than the leader (never
    the player's house — his table is his own; a client has no design
    voice, `acquire_design_regions` reads [] for it), every province of its
    acquire designs in the loser's OWN homeland that the winner's SIDE
    holds — the Pressburg idiom the validator carries
    (`occupied_homeland_cession_ok`: an occupier hands the conquest to the
    beneficiary under the ceder's signature) — never a great power's
    capital (D2's floor), never a province the leader's own cessions
    (`taken`) already name. One `territory_cede` clause per province, `to`
    the ally. Walks the allies' designs only (Rule 8)."""
    from backend.game_logic.agendas import acquire_design_regions
    side_of = war.get("side_by_nation") or {}
    active = set(war.get("active_participants") or [])
    player = str(getattr(world, "player_nation", "France") or "France")
    homeland = set((getattr(world, "nation_starting_regions", {}) or {})
                   .get(loser) or [])
    regions = getattr(world, "regions", {}) or {}
    named = {str(r) for r in (taken or ())}
    out: List[Dict] = []
    allies = sorted(n for n in active
                    if side_of.get(n) == winner_side and n != leader)
    for ally in allies:
        if str(world._top_overlord(ally) or ally) == player:
            continue
        for design in acquire_design_regions(world, ally):
            for region_name in design:
                name = str(region_name)
                if name in named or name not in homeland:
                    continue
                region = regions.get(name)
                holder = str(getattr(region, "controller", "") or "") if region is not None else ""
                if not holder:
                    continue
                holder_house = str(world._top_overlord(holder) or holder)
                if (side_of.get(holder) != winner_side
                        and side_of.get(holder_house) != winner_side):
                    continue
                if _is_great_power_capital(world, name):
                    continue
                named.add(name)
                out.append({"type": "territory_cede", "from": loser,
                            "to": ally, "region": name})
    return out


def held_aim_clause(regions) -> str:
    """'Tyrol', 'Milan and Piedmont', 'Milan, Piedmont and Savoy'."""
    return _regions_clause([str(r) for r in regions or []])


# ── Occupation is not annexation (T3-6 — the residual debt, ruled) ───────

def _house_aims(world, nation: str) -> set:
    """Every province of the authored acquire designs of `nation`'s HOUSE
    (its top overlord's deck — a client's own deck is dormant, it holds
    for its lord), reconciled provinces stripped (`agendas.acquire_design_
    regions`). The authored aims, whatever design is active now."""
    from backend.game_logic.agendas import acquire_design_regions
    house = world._top_overlord(nation) or nation
    aims = set()
    for regions in acquire_design_regions(world, house):
        aims.update(str(r) for r in regions)
    return aims


def keepable_regions(world, holder: str, ceder: str) -> set:
    """T3-6 — what an AI holder may KEEP of `ceder`'s at their peace: its
    house's authored aims (`_house_aims`) and the province articles it
    declared at the war against the ceder (`declared_goals` — the war's
    stated object, PC-R7). The enemy's capital is never a keeper by
    itself: storming it was a permission (R1's default), not a claim."""
    keep = set(_house_aims(world, holder))
    try:
        from backend.game_logic.declared_goals import declared_articles
        for article in declared_articles(world, holder, ceder, live_only=False):
            if article.get("kind") == "province" and article.get("region"):
                keep.add(str(article.get("region")))
    except Exception as exc:
        from backend.errors import report
        report(exc, "war_council.keepable_regions: declared_articles")
    return keep


def annexations_outside_aim(world) -> Dict[str, List[str]]:
    """T3-6 — THE GATE'S READ, annexation rather than occupation: per court,
    the provinces it holds BY RIGHT (`game_end.holds_by_title` — a signed
    peace's retention or a conquest settled past its quiet clock) that are
    neither its homeland nor an explicit treaty article (the aim's lock, a
    compensation, a dictated cession — agreed, never sprawl) and that lie
    outside its house's authored aims. A liberation is the ally's homeland
    and never counts. Pure, end-of-run (the instrument's `capture_final`
    calls it); {court: [provinces]} for every court with any."""
    from backend.game_logic.game_end import TITLE_TREATY, _is_homeland, holds_by_title
    store = getattr(world, "province_title", None)
    store = store if isinstance(store, dict) else {}
    out: Dict[str, List[str]] = {}
    for court in sorted(world.get_active_nations() or []):
        aims = None
        for region_name in world.get_nation_regions(court) or []:
            if _is_homeland(world, region_name, court):
                continue
            if not holds_by_title(world, region_name, court):
                continue
            rec = store.get(region_name) or {}
            if rec.get("kind") == TITLE_TREATY and not rec.get("retained"):
                continue
            if aims is None:
                aims = _house_aims(world, court)
            if region_name in aims:
                continue
            out.setdefault(court, []).append(str(region_name))
    return {court: sorted(regions) for court, regions in out.items()}


# ── Crisis lifecycle ────────────────────────────────────────────────────


def get_war_intent(world, nation: str) -> Optional[Dict]:
    return (getattr(world, "war_intents", {}) or {}).get(nation)


def record_in_tenure(record: Optional[Dict], turn: int) -> bool:
    """A war-intent record holds the world-wide foreground at `turn` — its
    whole tenure, the forewarn, the coercion and the soft and hard stalls
    included (S14c, `docs/EVENTS_SPEC.md` §4 R1). The one test the
    foreground promotion and a newly opened crisis read."""
    if not isinstance(record, dict) or not record.get("foregrounded"):
        return False
    since = record.get("foregrounded_turn")
    return since is None or int(since) <= int(turn)


def foreground_in_tenure(world) -> bool:
    """A foregrounded crisis stands this morning — R1: a moment letter waits
    it out within its grace (`moments.tick`)."""
    turn = int(getattr(world, "current_turn", 0) or 0)
    return any(record_in_tenure(r, turn)
               for r in (getattr(world, "war_intents", {}) or {}).values())


def _crisis_cause_of_death(world, coveter: str, record: Dict) -> Optional[str]:
    """None while the crisis lives; else the §12.1 cause. Derived per turn
    — `price` is a reading, never a latch (§3.1a)."""
    from backend.game_logic.agendas import get_active_agenda
    from backend.game_logic.instruments import design_suspended
    from backend.game_logic.intent import get_nation_intent

    target = record.get("target")
    design_id = record.get("design_id")

    # (b) bought off — the compensation record suspends the design.
    if design_suspended(world, coveter, design_id):
        return "bought_off"

    agenda = get_active_agenda(coveter, world)
    if agenda is None or agenda.id != design_id or agenda.survival:
        # The deck moved on. "Satisfied" only when the design's own entry
        # IS satisfied; a survival override, a vassalised or eliminated
        # coveter, a superseded entry read "the want is won" over a
        # capital that had just fallen (the October 27, 2026 sweep).
        return ("satisfied" if _design_entry_satisfied(world, coveter, design_id)
                else "overtaken")

    view = get_nation_intent(coveter, world)
    if view.against != target:
        # The obstacle changed - this quarrel is over, the want is not won.
        return "overtaken"
    if crisis_rung_holds(world, coveter, view):
        return None  # still live (fight; or coerce on a defenceless prize)

    # The rung fell below fight: name why (§12.1's taxonomy).
    if guarantee_deterred(world, coveter, view, target):
        return "deterred"
    return "starved"


def guarantee_deterred(world, coveter: str, view, target: str) -> bool:
    """OCT27-D6(c) (ruled as recommended, S14i): "deterred" is credited
    only when a guarantee MOVED the rung — the counterfactual: the coveter's
    weight without the guarantee's drop (`+ GUARANTEE_WEIGHT_DETERRENT`)
    reaches the fight floor, or the coerce floor on a holder that would be a
    defenceless prize without its guarantors' armies. Otherwise the want
    starved on its own and beat 7 says so. Down: any live third-party
    guarantee on the target was credited."""
    from backend.game_logic.instruments import (
        GUARANTEE_WEIGHT_DETERRENT, live_guarantees_of)
    if not any(g.get("guarantor") != coveter for g in live_guarantees_of(world, target)):
        return False
    from backend.game_logic.intent import PRICE_THRESHOLDS
    floors = dict(PRICE_THRESHOLDS)
    weight = int(getattr(view, "weight", 0) or 0) + int(GUARANTEE_WEIGHT_DETERRENT)
    if weight >= floors["fight"]:
        return True
    if weight >= floors["coerce"] and THE_DEFENCELESS_PRIZE_OPENS_AT_COERCE:
        free = int(exposure_against(world, coveter, target)["free"])
        return free > 0 and _prize_against(_standing_strength(world, target), free)
    return False


def reset_stall_on_pass(record: Dict) -> None:
    """OCT27-17: the hard stall counts CONSECUTIVE refused turns. Down (None):
    the cumulative counter."""
    record.pop("stall_turns", None)


def failed_declaration_stalls() -> bool:
    """OCT27-19: a declaration the preview could not foresee refusing counts
    a stalled turn. Down (False): the frozen foreground slot."""
    return True


def _design_entry_satisfied(world, nation: str, design_id: str) -> bool:
    """Is the deck entry `design_id` of `nation` satisfied on the board today
    (`agendas.entry_satisfied`)? False when the entry is gone."""
    from backend.game_logic.agendas import entry_satisfied
    for entry in (getattr(world, "agendas", {}) or {}).get(nation) or []:
        if str(entry.get("id") or "") == str(design_id or ""):
            return bool(entry_satisfied(world, nation, entry))
    return False


def _emit_crisis_passed(world, coveter: str, record: Dict, cause: str,
                        events: List[Dict]) -> None:
    """Beat 7 — The Crisis Passes (§12.1, pin 21). Only a FOREGROUNDED
    crisis owes the player an ending; background coolings stay quiet
    (pin 13 untouched)."""
    if not record.get("foregrounded"):
        return
    from backend.display_names import humanize_entity_name
    from backend.game_logic.dispatch import queue_dispatch_event
    coveter_display = humanize_entity_name(coveter)
    target_display = humanize_entity_name(str(record.get("target") or ""))
    cause_copy = _CRISIS_CAUSE_COPY.get(cause, _CRISIS_CAUSE_COPY["starved"])
    if "{threat}" in cause_copy:
        # The exposed cause names the neighbour that pinned the army —
        # the same per-turn view the gate itself read (§2.5-1).
        threat = exposure_against(
            world, coveter, str(record.get("target") or "")).get("worst_threat")
        cause_copy = cause_copy.format(
            threat=humanize_entity_name(threat) if threat else "a neighbour")
    event = {
        "type": "crisis_passed",
        "nation": coveter,
        "target": record.get("target"),
        "design_id": record.get("design_id"),
        "cause": cause,
        # AI-3r §2.5-1 observability: the last soft gate that blocked,
        # so the suite's honesty pin (starved never renders for a gate
        # refusal) is falsifiable against the live log.
        "last_soft_block": record.get("last_soft_block"),
        "message": (f"{coveter_display} stands down over "
                    f"{target_display} — {cause_copy}."),
    }
    world.log_event(dict(event))
    events.append(event)
    queue_dispatch_event(world, "crisis_passed", {
        "nation": coveter_display,
        "target": target_display,
        "cause": cause_copy,
    }, "always")


# SFR-D23 (the economy audit, October 5, 2026): the crisis beat's buy-off
# line is priced against the morning's chest, not the mid-advance one.
# False = the shipped read (the live chest at council time).
THE_BEAT_READS_THE_MORNINGS_CHEST = True


def _beat_chest(world, player: str, treasury: int) -> tuple:
    """S14E-X189 / S14E-D19 - (the figure the beat prices "you can afford it"
    against, the `FREE_OF_OBLIGATIONS` clause or ''). `treasury` is the beat's
    own read (the morning's forecast `chest_forecast(...)["projected"]` with
    SFR-D23's lever up, the raw live chest with it down). ONE chest: the buy-off
    verb refuses against the treasury LESS the recurring settlement payments
    still owed (the player's chest, `bond.bid_funds`), so the beat prints the lesser of the
    morning's forecast and that chest - the forecast less the owed sum
    (`settlement_validation.recurring_obligations_owed`, the one reader).
    Read on the forecast, not the council's live chest: the council sits
    mid-advance, before the income phase, when the live chest is one the
    player never holds (SFR-D23's -167). Nothing owed, or the lever down: the
    figure unchanged, no clause."""
    if not THE_BEAT_READS_THE_MORNINGS_CHEST:
        return int(treasury), ""
    from backend.game_logic.instruments import FREE_OF_OBLIGATIONS
    from backend.game_logic.settlement_validation import recurring_obligations_owed
    owed = int(recurring_obligations_owed(world, player))
    if owed <= 0:
        return int(treasury), ""
    return min(int(treasury), max(0, int(treasury) - owed)), FREE_OF_OBLIGATIONS


def _emit_crisis_brewing(world, coveter: str, record: Dict,
                         events: List[Dict]) -> None:
    """Beat 2 — The Brewing Crisis: the fore-warning, with the instruments
    that would defuse it listed and HONESTLY gated (the /formables
    honest-availability contract applied to diplomacy)."""
    from backend.display_names import humanize_entity_name
    from backend.game_logic.dispatch import queue_dispatch_event
    from backend.game_logic.instruments import compute_buyoff_price

    coveter_display = humanize_entity_name(coveter)
    target_display = humanize_entity_name(str(record.get("target") or ""))

    # Honest availability: name each instrument WITH the player's real gate.
    player = getattr(world, "player_nation", "France")
    treasury = int((getattr(world, "nation_gold", {}) or {}).get(player, 0))
    if THE_BEAT_READS_THE_MORNINGS_CHEST:
        # SFR-D23 (the economy audit, October 5, 2026): the council sits
        # INSIDE the advance, after the enemy phase's Butcher's Bill and
        # BEFORE the income phase, so the live chest is one the player never
        # holds — measured: "the treasury holds -167" beside the morning
        # ledger's 1,398. The beat is read in the morning, so its
        # affordability is priced against the chest the turn will leave
        # (`ledger.chest_forecast`, the ONE projection seam the council's own
        # opening already reads).
        from backend.game_logic.ledger import chest_forecast
        treasury = int(chest_forecast(world, player)["projected"])
    # S14E-X189 / S14E-D19: ONE chest - the lesser of the morning's forecast
    # and the chest the verb will be gated against (the treasury less the
    # recurring settlement payments still owed); nothing owed, `treasury`
    # untouched.
    treasury, owed = _beat_chest(world, player, treasury)
    dp = int(getattr(world, "diplomatic_points", 0) or 0)
    price = compute_buyoff_price(world, coveter)
    instruments = []
    if price is not None:
        afford = "you can afford it" if treasury >= price else \
            f"the treasury holds {treasury:,}{' gold' + owed if owed else ''}"
        instruments.append(f"compensate ({price:,}g — {afford})")
    instruments.append(
        f"guarantee {target_display} (1 DP — {dp} in hand)"
        if dp >= 1 else "guarantee (needs 1 DP — none in hand)")
    instruments.append("or let the war come, having been asked")

    event = {
        "type": "crisis_brewing",
        "nation": coveter,
        "target": record.get("target"),
        "design_id": record.get("design_id"),
        "reason_title": record.get("want_title"),
        "message": (f"{coveter_display} will move on {target_display} — "
                    f"{record.get('want_title') or 'a design of state'}. "
                    f"You may {'; '.join(instruments)}."),
    }
    world.log_event(dict(event))
    events.append(event)
    queue_dispatch_event(world, "crisis_brewing", {
        "nation": coveter_display,
        "target": target_display,
        "instruments": "; ".join(instruments),
    }, "always")


def _emit_coercive_demand(world, coveter: str, record: Dict,
                          events: List[Dict]) -> None:
    """Beat 3's AI-AI arm: the coercive demand — the ladder step between
    the refused asks and the declaration, refused on the record (the
    holder does not yield its own homeland, the design_ask idiom)."""
    from backend.display_names import humanize_entity_name
    from backend.game_logic.ai_diplomacy import record_diplomatic_refusal
    from backend.game_logic.dispatch import queue_dispatch_event

    target = str(record.get("target") or "")
    record_diplomatic_refusal(world, coveter, target, COERCIVE_DEMAND_TYPE)
    coveter_display = humanize_entity_name(coveter)
    target_display = humanize_entity_name(target)
    event = {
        "type": "coercive_demand",
        "nation": coveter,
        "target": target,
        "design_id": record.get("design_id"),
        "message": (f"{coveter_display} delivers a final demand to "
                    f"{target_display} — it is refused."),
    }
    world.log_event(dict(event))
    events.append(event)
    if record.get("foregrounded"):
        queue_dispatch_event(world, "coercive_demand", {
            "nation": coveter_display,
            "target": target_display,
        }, "always")


def _ladder_climbed(world, coveter: str, target: str) -> bool:
    """§5 pin 8: prior refused asks/coercion on the serialized record — or
    a §3.3 renege grievance, the strongest casus belli, which may skip
    rungs entirely."""
    from backend.game_logic.ai_diplomacy import get_ladder_refusals
    from backend.game_logic.instruments import has_renege_grievance
    if has_renege_grievance(world, coveter, target):
        return True
    # G2-LADDER: the ladder's own memory (the 12-turn record seam-down).
    return len(get_ladder_refusals(world, coveter, target)) >= CRISIS_REFUSALS_REQUIRED


def _restraint_block_reason(world, coveter: str, target: str,
                            forecast: bool = False) -> Optional[str]:
    """§4.3's restraint gates, decomposed so beat 7 can name the TRUE
    cause (§2.5-1's honesty pin): None while all gates clear, else
    "busy" / "penniless" / "outmatched" / "exposed".

    AI-3r §2.1 — the force gate weighs FREE strength (standing minus the
    rear-security reserve) against the target and its guarantors: Prussia
    with Austria armed and cold on its flank cannot campaign in Hanover;
    Prussia after Austria is beaten, bankrupt or friendly can. The
    defender defends with everything — `theirs` stays standing strength.

    SF-LB-2b — `forecast=True` is the OPENING's read (step 3): the
    `penniless` gate weighs the chest the court will have when this turn
    ends (`ledger.chest_forecast`, the ONE projection seam), because the
    council sits between the admin phase's spending and the income phase.
    The declaration (step 1) and every other caller keep the live chest.
    Lever-gated: with `THE_COUNCIL_SPENDS_THE_TURNS_INCOME` down the
    parameter is inert.
    """
    if world.get_nations_at_war_with(coveter):
        return "busy"  # a court already at war opens no second design war
    treasury = int((getattr(world, "nation_gold", {}) or {}).get(coveter, 0))
    if forecast and THE_COUNCIL_SPENDS_THE_TURNS_INCOME:
        from backend.game_logic.ledger import chest_forecast
        treasury = int(chest_forecast(world, coveter)["projected"])
    if treasury < AI_WAR_TREASURY_FLOOR:
        return "penniless"
    own = _standing_strength(world, coveter)
    theirs = _standing_strength(world, target)
    # Alliance webs: a defender's guarantors stand in the scale too.
    from backend.game_logic.instruments import live_guarantees_of
    for guarantee in live_guarantees_of(world, target):
        if guarantee.get("guarantor") not in (coveter, target):
            theirs += _standing_strength(world, str(guarantee.get("guarantor")))
    if theirs > 0:
        if own < AI_WAR_FORCE_RATIO * theirs:
            return "outmatched"  # even the whole army would not suffice
        if int(exposure_against(world, coveter, target)["free"]) < AI_WAR_FORCE_RATIO * theirs:
            return "exposed"     # the army suffices; the frontier pins it (OCT27-D6a)
    if theirs == 0 and own <= 0:
        return "outmatched"
    return None


def _holder_scale(world, coveter: str, target: str) -> int:
    """The holder's standing strength plus its guarantors' — the exact
    `theirs` the restraint gate weighs (one arithmetic, two readers)."""
    theirs = _standing_strength(world, target)
    from backend.game_logic.instruments import live_guarantees_of
    for guarantee in live_guarantees_of(world, target):
        if guarantee.get("guarantor") not in (coveter, target):
            theirs += _standing_strength(world, str(guarantee.get("guarantor")))
    return int(theirs)


def holder_outmatched(world, asker: str, holder: str) -> bool:
    """SF-LB-2 §6.4-1 — THE one outmatched reading: the holder (plus its
    guarantors) stands at most `HOLDER_OUTMATCHED_FRACTION` of the asker's
    FREE strength; an armyless holder counts; an asker with no free
    strength threatens nobody. Read by the intent weight term AND the
    crisis opening — never duplicated. A guarantor's whole army enters the
    holder's scale, which is how `guarantee_nation` lifts a prize out of
    reach (the D5 instrument earning its keep)."""
    if not asker or not holder or asker == holder:
        return False
    free = int(exposure_against(world, asker, holder)["free"])   # OCT27-D6a
    if free <= 0:
        return False
    return _prize_against(_holder_scale(world, asker, holder), free)


def _prize_against(scale: int, free: int) -> bool:
    """THE one read of `HOLDER_OUTMATCHED_FRACTION`: a holder's scale at
    most that fraction of the asker's free strength is a prize (§6.4-1) —
    `holder_outmatched` and the deterrent's counterfactual
    (`guarantee_deterred`) ask it alike."""
    return int(scale) <= HOLDER_OUTMATCHED_FRACTION * int(free)


def defenceless_prize(world, coveter: str, view=None) -> Optional[str]:
    """The holder's tag when `coveter`'s CURRENT intent is an AI-vs-AI
    acquire design on a holder that cannot defend the prize — the §6.4
    clause as a surface reads it (lever-gated; None everywhere else)."""
    if not THE_DEFENCELESS_PRIZE_OPENS_AT_COERCE:
        return None
    if view is None:
        from backend.game_logic.intent import get_nation_intent
        view = get_nation_intent(coveter, world)
    if view.survival or view.want_type != "acquire_regions" or not view.against:
        return None
    player = getattr(world, "player_nation", "France")
    vassals = set((getattr(world, "vassals", {}) or {}).keys())
    if coveter == player or coveter in vassals:
        return None
    if view.against == player or view.against in vassals:
        return None
    if not holder_outmatched(world, coveter, view.against):
        return None
    return str(view.against)


def crisis_rung_holds(world, coveter: str, view) -> bool:
    """Is `coveter`'s intent at a rung that opens — or keeps — a crisis?
    `fight` always; `coerce` only for a defenceless prize (§6.4-2). ONE
    reading for the opening (step 3) and the liveness poll (step 1), so a
    crisis opened at coerce is not read dead at the next poll."""
    from backend.game_logic.intent import rung_index
    if view.price == "fight":
        return True
    if rung_index(view.price) < rung_index("coerce"):
        return False
    return defenceless_prize(world, coveter, view) is not None


def defenceless_prize_line(world, coveter: str, holder: str) -> str:
    """ONE composition for every surface that names the clause (the
    ledger's Intent row, Talleyrand's war room, the guarantee chip)."""
    # NA-6 §11.8 stage 3: a FORMED nation is never named by its dead name
    # in composed prose — the formation-aware chokepoint, not the static map.
    from backend.game_logic.formations import formed_display_name
    return (f"{formed_display_name(world, holder)} cannot defend itself — "
            f"{formed_display_name(world, coveter)}'s design opens at an "
            f"ultimatum, not at war")


def coveters_of_prize(world, holder: str) -> List[str]:
    """Every AI court whose live design reads `holder` as a defenceless
    prize (the guarantee chip's reason to exist on that court). Lever-gated
    through `defenceless_prize` itself — no second guard (the sweep found
    one here inert, October 3, 2026)."""
    out: List[str] = []
    for court in sorted(world.get_active_nations()):
        if court == holder:
            continue
        if defenceless_prize(world, court) == holder:
            out.append(court)
    return out


def _declare_design_war(world, coveter: str, record: Dict,
                        events: List[Dict]) -> bool:
    """§4.3a-1: the council owns the declaration, at the announcement."""
    from backend.game_logic.agendas import get_agenda_military_targets
    from backend.game_logic.diplomacy import declare_war
    from backend.game_logic.instruments import has_renege_grievance

    target = str(record.get("target") or "")
    casus = has_renege_grievance(world, coveter, target)
    # PC-R7 (ii) part 2 (GR5): the design war declares its articles — the
    # design's own provinces the target holds — priced as the player's are.
    from backend.game_logic.declared_goals import design_articles
    result = declare_war(world, coveter, target,
                         casus_belli=casus, war_objective="conquest",
                         declared_terms=design_articles(world, coveter, target))
    if not result.get("success"):
        # The fail-safe arm — preview said yes, the authority said no.
        # The crisis stays open; the preview re-runs next turn (a crisis
        # whose predicate goes permanently refused passes as starved).
        return False

    war_id = str(result.get("war_id") or "")
    war = (getattr(world, "war_instances", {}) or {}).get(war_id)
    if isinstance(war, dict):
        # Reuse, not a new war-goal system (§4.3): the instance carries
        # the design and the STATED REASON the ledger renders (pin 4).
        war["ai_initiated"] = True
        war["design_id"] = record.get("design_id")
        war["stated_reason"] = record.get("want_title")

    # Pin 4 ("no unexplained war"): ride the stated reason on the
    # war_declaration event declare_war just logged, so the dispatch
    # headline can render it. Single writer, same turn — the event is
    # the last matching entry by construction.
    for logged in reversed(getattr(world, "event_log", []) or []):
        if (logged.get("type") == "war_declaration"
                and logged.get("aggressor") == coveter
                and logged.get("target") == target):
            logged["stated_reason"] = record.get("want_title")
            break

    # The objective record carries the design's own provinces instead of
    # [capital] — AI-initiated design wars ONLY (§4.3: the player's War
    # Purpose numbers stay byte-identical).
    design_regions = get_agenda_military_targets(coveter, world)
    if design_regions:
        diplo_key = world._make_diplo_key(coveter, target)
        objective = ((getattr(world, "war_objectives", {}) or {})
                     .get(diplo_key, {}) or {}).get(coveter)
        if isinstance(objective, dict):
            objective["target_regions"] = list(design_regions)
            objective["design"] = record.get("design_id")

    from backend.display_names import humanize_entity_name
    events.append({
        "type": "ai_war_declared",
        "aggressor": coveter,
        "target": target,
        "war_id": war_id,
        "stated_reason": record.get("want_title"),
        "message": (f"{humanize_entity_name(coveter)} declares war on "
                    f"{humanize_entity_name(target)} — "
                    f"{record.get('want_title') or 'conquest'}"
                    + _declared_tail(world, result) + "."),
    })

    # The join arm (AI-2d / D5-3 enforcement made real): an AI guarantor
    # of the target honours its pledge at the declaration — or the
    # instruments pass brands it within the grace window. France's own
    # pledge is the player's choice; the ward's plea reaches the dispatch.
    _honour_guarantees(world, coveter, target, war_id, events)
    return True


def _declared_tail(world, result: Dict) -> str:
    """PC-R7 (ii) part 2: "; declaring Hanover" — the articles the design war
    named at its declaration (`declared_goals`)."""
    from backend.game_logic.declared_goals import articles_display
    shown = articles_display(world, result.get("declared_articles") or [])
    return f"; declaring {shown}" if shown else ""


def _honour_guarantees(world, coveter: str, target: str, war_id: str,
                       events: List[Dict]) -> None:
    """The council road's honouring: `instruments.honour_guarantees`, the
    ONE loop every declaration road calls (OCT27-D7, S14i)."""
    from backend.game_logic.instruments import honour_guarantees
    honour_guarantees(world, coveter, target, events)


def _ai_buyoff_funds(world, target: str) -> int:
    """S14E-X190 / S14E-D19 - THE SEAM: the gold an AI holder may spend on
    buying a coveter off. ONE chest: the court's treasury LESS the recurring
    settlement payments it still owes (`bond.bid_funds` - the very budget the
    player's buy-off verb is gated against), clamped to [0, the coffers], so a
    court that owes 300 a turn does not "have" the 1,000 in its vaults. With
    nothing owed it is the raw treasury, byte for byte. DOWN (the series arm
    patches this to `int(nation_gold.get(target, 0))`) restores the old read
    of the raw coffers. Pure."""
    gold = int((getattr(world, "nation_gold", {}) or {}).get(target, 0) or 0)
    try:
        from backend.game_logic import bond as _bond
        return max(0, min(gold, int(_bond.bid_funds(world, target))))
    except Exception as exc:
        from backend.errors import report
        report(exc, "war_council._ai_buyoff_funds: bond.bid_funds")
        return gold


def _run_ai_instrument_producers(world, coveter: str, record: Dict,
                                 events: List[Dict]) -> None:
    """The Stage C deferral this stage owns (§15 → AI-3): AI courts
    PRODUCING guarantees and compensation, where the choice has stakes —
    a live foregrounded crisis. At most one AI guarantee world-wide per
    turn; a folds-statecraft holder may buy the coveter off once."""
    from backend.game_logic.instruments import (
        compute_buyoff_price,
        create_compensation_bargain,
        pledge_guarantee,
    )
    player = getattr(world, "player_nation", "France")
    target = str(record.get("target") or "")

    # (a) The holder folds: buy the design off (§3.1a descent (b) for
    # AI-AI crises — beat 7's "bought off" cause needs a producer).
    if not record.get("buyoff_attempted"):
        record["buyoff_attempted"] = True
        statecraft = world.get_statecraft(target) if target != player else {}
        if statecraft.get("coercion") == "folds":
            price = compute_buyoff_price(world, coveter)
            gold = getattr(world, "nation_gold", {}) or {}
            # S14E-X190 / S14E-D19: the holder buys off with its CHEST, not
            # its coffers (`_ai_buyoff_funds`, the series arms' seam)
            if price is not None and _ai_buyoff_funds(world, target) >= price:
                gold[target] = int(gold.get(target, 0)) - int(price)
                gold[coveter] = int(gold.get(coveter, 0)) + int(price)
                # Review fix [r2 LOW]: the SAME granted shape the player
                # verb mints ({"gold": N}) — one record schema, GR5.
                create_compensation_bargain(
                    world, payer=target, recipient=coveter,
                    design_id=str(record.get("design_id") or ""),
                    granted={"gold": int(price)},
                )
                from backend.display_names import humanize_entity_name
                event = {
                    "type": "design_bought_off",
                    "payer": target,
                    "recipient": coveter,
                    "design_id": record.get("design_id"),
                    "message": (f"{humanize_entity_name(target)} buys off "
                                f"{humanize_entity_name(coveter)}'s design "
                                f"for {int(price):,} gold."),
                }
                # ONE logger per event (verify fleet, Aug 2026):
                # create_compensation_bargain already log_events its own
                # design_bought_off — a second log here rendered the same
                # campaign-log row twice. The producer only APPENDS for the
                # turn surface.
                events.append(event)
                return  # the crisis will pass at the next poll

    # (b) A protector steps forward: one AI guarantee per turn world-wide.
    if record.get("guarantee_considered"):
        return
    record["guarantee_considered"] = True
    if getattr(world, "_ai_guarantee_this_turn", -1) == int(world.current_turn):
        return
    for candidate in world.get_active_nations():
        if candidate in (coveter, target, player):
            continue
        if candidate in (getattr(world, "vassals", {}) or {}):
            continue
        statecraft = world.get_statecraft(candidate)
        reaches = tuple(statecraft.get("reaches_first") or ())
        if "sponsor" not in reaches and "align" not in reaches:
            continue
        if world.get_nations_at_war_with(candidate):
            continue
        rel_target = int(world.nation_relations.get(
            world._make_diplo_key(candidate, target), 0) or 0)
        rel_coveter = int(world.nation_relations.get(
            world._make_diplo_key(candidate, coveter), 0) or 0)
        if rel_target < 40 or rel_coveter > 0:
            continue
        pledge = pledge_guarantee(world, guarantor=candidate, protected=target)
        # Aug 2026 health-check audit: pledge_guarantee returns
        # {"success", "record", "event"} — the old `pledge.get("id")` guard
        # read a key that never existed, so this whole block was dead: the
        # one-per-turn stamp never landed, the break never fired (EVERY
        # qualifying candidate silently pledged), and the player-facing
        # narration event was never emitted.
        if pledge.get("success") and pledge.get("record"):
            world._ai_guarantee_this_turn = int(world.current_turn)
            from backend.display_names import humanize_entity_name
            event = {
                "type": "guarantee_pledged",
                "guarantor": candidate,
                "protected": target,
                "message": (f"{humanize_entity_name(candidate)} guarantees "
                            f"{humanize_entity_name(target)} against "
                            f"{humanize_entity_name(coveter)}'s design."),
            }
            # ONE logger per event (verify fleet, Aug 2026):
            # pledge_guarantee already log_events guarantee_pledged — the
            # producer only APPENDS for the turn surface.
            events.append(event)
            break


# ── AI-3c: the army agrees with the ledger (§13.1) ─────────────────────


def get_intent_frontier(world, nation: str) -> List[str]:
    """Regions `nation` can lawfully stand in that border its design's
    unmet targets — the massing bias's destination set. Empty without a
    live crisis (deckless-neutral; released the same turn a crisis cools
    — no latch). Cached per turn (GR8)."""
    cache = getattr(world, "_intent_frontier_cache", None)
    cache_turn = getattr(world, "_intent_frontier_cache_turn", -1)
    if cache is None or cache_turn != int(world.current_turn):
        cache = {}
        world._intent_frontier_cache = cache
        world._intent_frontier_cache_turn = int(world.current_turn)
    if nation in cache:
        return cache[nation]

    frontier: List[str] = []
    record = get_war_intent(world, nation)
    if record:
        # The design's own unmet provinces are the anchors: the P7 mover
        # paths toward the nearest one and the existing _can_ai_move_to
        # gate stalls every corps at the last lawful region — the massing
        # EMERGES from the same movement rules every marshal obeys (GR5).
        # Enterable border regions ride along as nearer anchors.
        from backend.game_logic.agendas import get_agenda_military_targets
        from backend.game_logic.diplomacy import can_enter_territory
        targets = [t for t in get_agenda_military_targets(nation, world)
                   if t in world.regions]
        frontier.extend(targets)
        seen = set(targets)
        for target_name in targets:
            region = world.regions.get(target_name)
            if region is None:
                continue
            for adjacent in getattr(region, "adjacent_regions", []) or []:
                if adjacent in seen:
                    continue
                seen.add(adjacent)
                neighbour = world.regions.get(adjacent)
                if neighbour is None:
                    continue
                controller = getattr(neighbour, "controller", None)
                # WO-17: deliberately the bare pair-level form (no
                # mover_location) — this derives ANCHORS for massing, it
                # relocates nobody; the actual moves toward these anchors run
                # through the direction-aware _can_ai_move_to gate. The
                # census pin in test_wo_slice13_corridor_direction.py audits
                # this call site.
                if controller and (controller == nation or can_enter_territory(
                        world, nation, controller)):
                    frontier.append(adjacent)
    cache[nation] = frontier
    return frontier


# ── The per-turn pass ───────────────────────────────────────────────────


def process_war_council(world) -> List[Dict]:
    """The once-per-turn decision pass (sited after the AI-AI diplomatic
    phase in `_advance_turn_internal`). Deckless worlds: `war_intents`
    stays empty and this returns [] — byte-identical (pin 18)."""
    events: List[Dict] = []
    store = getattr(world, "war_intents", None)
    if store is None:
        store = {}
        world.war_intents = store

    player = getattr(world, "player_nation", "France")
    turn = int(getattr(world, "current_turn", 0))

    # ── 1. Poll open crises: pass, escalate, or declare ──
    for coveter in sorted(store.keys()):
        record = store[coveter]
        cause = _crisis_cause_of_death(world, coveter, record)
        if cause is not None:
            _emit_crisis_passed(world, coveter, record, cause, events)
            del store[coveter]
            continue

        preview = can_declare_war(world, coveter, str(record.get("target")))
        if not preview["ok"]:
            if preview["reason"] == "already_at_war":
                # Not a stall — the thing the crisis was building toward has
                # happened, by a road the council did not walk. Close it with
                # its own cause rather than letting the stall counter cool it
                # as "the moment passed" over a live war.
                _emit_crisis_passed(world, coveter, record, "war_joined",
                                    events)
                del store[coveter]
                continue
            if (preview["reason"] == "treaty_in_the_way"
                    and not record.get("treaty_broken_turn")):
                # §4.3a-2: break it first — a visible ladder step. The
                # break is this turn's step; declaration waits.
                from backend.game_logic.diplomacy import break_treaty
                pair_key = world._make_diplo_key(
                    coveter, str(record.get("target")))
                break_result = break_treaty(pair_key, coveter, world)
                if break_result.get("success"):
                    record["treaty_broken_turn"] = turn
                    continue
            # A refused predicate — armistice signed mid-crisis, side
            # conflict, an unbreakable open-movement state (no treaty
            # record / no DP / a second treaty tier under the first) —
            # stalls the crisis; a stall that persists cools it on
            # screen as starved (pin 21 forbids a foregrounded crisis
            # that never ends).
            record["stall_turns"] = int(record.get("stall_turns", 0)) + 1
            if record["stall_turns"] >= CRISIS_HARD_STALL_TURNS:
                _emit_crisis_passed(world, coveter, record, "starved", events)
                del store[coveter]
            continue
        # The stall is CONSECUTIVE refused turns (the October 27, 2026
        # sweep): three flickers, five clean turns and one more refusal
        # cooled a live crisis as "the moment passed".
        reset_stall_on_pass(record)

        if not record.get("coerce_recorded_turn"):
            if record.get("foregrounded") and turn > int(record.get("opened_turn", turn)):
                _emit_coercive_demand(world, coveter, record, events)
                record["coerce_recorded_turn"] = turn
            continue

        # Declaration gate: foregrounded tenure, ladder, restraints, preview.
        # AI-3r §2.4 (gate Q1): D1's MAX_SIMULTANEOUS_AI_WARS check is
        # DELETED — the exposure gate inside the restraints is the
        # diegetic replacement, and it can be rendered honestly.
        foregrounded_turn = record.get("foregrounded_turn")
        if not record.get("foregrounded") or foregrounded_turn is None:
            continue
        if turn - int(foregrounded_turn) < CRISIS_FOREWARN_TURNS:
            continue
        target = str(record.get("target") or "")
        soft_block = ("ladder" if not _ladder_climbed(world, coveter, target)
                      else _restraint_block_reason(world, coveter, target))
        if soft_block is not None:
            # Review fix [r2 MEDIUM]: the SOFT gates (ladder/restraints)
            # also carry pin 21's termination guarantee — a fully
            # fore-warned crisis that cannot fire for a long spell (the
            # holder permanently at war, an empty chest, a pinned
            # frontier) cools ON SCREEN instead of freezing the
            # world-wide foreground slot forever. Longer window than the
            # hard predicate: these gates legitimately clear within a
            # few turns (treasuries refill, wars end). AI-3r §2.5-1: the
            # LAST blocking reason names the cause — `starved` never
            # renders for an exposure or force refusal.
            record["soft_stall_turns"] = int(record.get("soft_stall_turns", 0)) + 1
            record["last_soft_block"] = soft_block
            if record["soft_stall_turns"] >= CRISIS_SOFT_STALL_TURNS:
                cause = _SOFT_BLOCK_CAUSE.get(soft_block, "starved")
                _emit_crisis_passed(world, coveter, record, cause, events)
                del store[coveter]
            continue
        record["soft_stall_turns"] = 0
        record.pop("last_soft_block", None)
        if _declare_design_war(world, coveter, record, events):
            del store[coveter]
        elif failed_declaration_stalls():
            # Pin 21's last edge: a declaration the preview could not
            # foresee refusing (the war merge, a dead court) counts as a
            # stalled turn too, so the one foreground slot is never frozen.
            record["stall_turns"] = int(record.get("stall_turns", 0)) + 1
            if record["stall_turns"] >= CRISIS_HARD_STALL_TURNS:
                _emit_crisis_passed(world, coveter, record, "starved", events)
                del store[coveter]

    # ── 2. Foreground promotion: one crisis on stage world-wide ──
    if not any(record_in_tenure(r, turn) for r in store.values()):
        waiting = sorted(
            (int(r.get("opened_turn", 0)), coveter)
            for coveter, r in store.items()
        )
        if waiting:
            _, promoted = waiting[0]
            record = store[promoted]
            record["foregrounded"] = True
            record["foregrounded_turn"] = turn
            _emit_crisis_brewing(world, promoted, record, events)

    # ── 3. Open new crises ──
    if getattr(world, "sovereign_map", "legacy") == "europe":
        from backend.game_logic.intent import get_nation_intent
        vassals = set((getattr(world, "vassals", {}) or {}).keys())
        for nation in sorted(world.get_active_nations()):
            if nation == player or nation in vassals or nation in store:
                continue
            view = get_nation_intent(nation, world)
            if (view.survival
                    or view.want_type not in CRISIS_ELIGIBLE_DESIGNS):
                continue
            target = view.against
            # v1 (§16.2): AI-vs-AI only — a player-targeted design coerces
            # through NA-5 and fights through the coalition, never here.
            if not target or target == player or target in vassals:
                continue
            if world.is_at_war(nation, target):
                continue
            if not crisis_rung_holds(world, nation, view):
                continue
            if view.price != "fight" or A_CRISIS_OPENS_ONLY_WHERE_IT_CAN_DECLARE:
                # §6.4-2: the coerce road opens only with every restraint
                # already clear (busy / penniless / outmatched / exposed),
                # so a defenceless prize never fore-warns a war its court
                # cannot wage — and, under the addendum lever, the fight
                # road reads the same predicate (pin 15, one gate over).
                # SF-LB-2b: the OPENING reads the chest the court can
                # SPEND — the turn's income forecast (`forecast=True`);
                # the declaration above keeps the live chest.
                if _restraint_block_reason(world, nation, target,
                                           forecast=True) is not None:
                    continue
            preview = can_declare_war(world, nation, target)
            if not preview["ok"] and preview["reason"] != "treaty_in_the_way":
                continue  # pin 15: never fore-warn a refused predicate
            if not _ladder_climbed(world, nation, target):
                continue
            foreground_free = not any(
                record_in_tenure(r, turn) for r in store.values())
            record = {
                "coveter": nation,
                "target": target,
                "design_id": view.want_id,
                "want_title": view.want_title,
                "opened_turn": turn,
                "foregrounded": bool(foreground_free),
                "foregrounded_turn": turn if foreground_free else None,
                "coerce_recorded_turn": None,
                "treaty_broken_turn": None,
                # SF-LB-2: the rung the crisis opened at (display + the
                # variance pin), inside the already-serialized record.
                "opened_at_price": view.price,
            }
            store[nation] = record
            if foreground_free:
                _emit_crisis_brewing(world, nation, record, events)

    # ── 4. AI instrument producers on the foregrounded crisis ──
    for coveter, record in list(store.items()):
        if record.get("foregrounded"):
            _run_ai_instrument_producers(world, coveter, record, events)

    return events


# ════════════════════════════════════════════════════════════════════════
# T2-3 — PRUSSIA'S HOOK: THE BANDWAGONER (DYNAMISM_SPEC.md §2 Tier 2,
# November 8, 2026). A court whose statecraft prefers the bandwagon rung
# (§3.4: Prussia, the hesitant opportunist) attaches itself to a running
# AI-vs-AI war on the STRONGER side, against the weaker side's leader —
# and may quit ONCE a campaign when the scales turn. Deterministic
# (AI-0b: no dice in politics); everything derived or written inside the
# serialized `war_instances` rows (no new world field).
# ════════════════════════════════════════════════════════════════════════

def a_bandwagoner_joins_the_stronger_side() -> bool:
    """T2-3 "Prussia's hook" (`DYNAMISM_SPEC.md` §2 Tier 2; November 8,
    2026): a court whose statecraft `reaches_first` carries "bandwagon"
    joins a live AI-vs-AI war on the stronger side when its relation with
    the weaker side's leader is below 0 — the ally-entry join idiom
    (`ensure_war_instance_for_pair` + WAR), one join a turn world-wide —
    and RENEGES (a separate peace out of a war it bandwagoned into) at
    most ONCE a campaign, the turn its side reads strictly weaker. Down:
    the pre-T2-3 board — no court ever attaches itself to a running war
    it was not called to, and no one quits by the scales."""
    return True


def _bandwagon_courts(world) -> List[str]:
    """The hook's courts, DERIVED from statecraft (never a name): active,
    non-vassal, not the player, not fighting for survival, and the
    profile's `reaches_first` carries "bandwagon" — Prussia alone on the
    shipped table (`nation_config.NATION_STATECRAFT`)."""
    from backend.game_logic.agendas import survival_override_active
    player = getattr(world, "player_nation", "France")
    vassals = set(getattr(world, "vassals", {}) or {})
    out = []
    for nation in sorted(world.get_active_nations()):
        if nation == player or nation in vassals:
            continue
        profile = world.get_statecraft(nation)
        if "bandwagon" not in tuple(profile.get("reaches_first") or ()):
            continue
        if survival_override_active(world, nation):
            continue
        out.append(nation)
    return out


def _side_strengths(world, instance) -> tuple:
    """Both sides' ACTIVE standing strength — `_standing_strength` summed
    over `active_participants` per side (an exited court weighs nothing)."""
    active = set(instance.get("active_participants") or [])
    att = [n for n in (instance.get("attackers") or []) if n in active]
    dfd = [n for n in (instance.get("defenders") or []) if n in active]
    s_att = sum(_standing_strength(world, n) for n in att)
    s_dfd = sum(_standing_strength(world, n) for n in dfd)
    return att, dfd, s_att, s_dfd


def _bandwagon_renege_spent(world, nation: str) -> bool:
    """One renege a campaign — DERIVED from the `reneged_turn` stamp the
    renege writes into the instance's own `participant_meta` row (the
    serialized store; no new world field). O(wars), once per tick."""
    for inst in (getattr(world, "war_instances", {}) or {}).values():
        meta = (inst.get("participant_meta") or {}).get(nation) or {}
        if meta.get("reneged_turn") is not None:
            return True
    return False


def process_bandwagon(world) -> List[Dict]:
    """The per-turn tick (world_state, after `process_war_council` so the
    council's fresh declarations are on the board, before the third-party
    settlements so a join cannot land on a war already closing this
    turn). Deckless worlds (legacy fixtures) no-op, the council's own
    gate."""
    if not a_bandwagoner_joins_the_stronger_side():
        return []
    if not (getattr(world, "agendas", {}) or {}):
        return []
    events: List[Dict] = []
    for nation in _bandwagon_courts(world):
        _bandwagon_renege(world, nation, events)
        _bandwagon_join(world, nation, events)
    return events


def _bandwagon_join(world, nation: str, events: List[Dict]) -> None:
    """The join: a live AI-vs-AI war (the player on neither side — §16.2's
    v1 narrowing: the anti-France road stays the coalition's, and France's
    own side is the player's to invite), the would-be side STRICTLY
    stronger, relation with the weaker side's leader below 0, the shared
    declaration preview clean (armistice cooldown — the fresh-peace floor
    — side conflict, treaty in the way), and free strength at home. One
    join a turn, world-wide (pin 13: measured, not a soap opera)."""
    from backend.game_logic.diplomacy import get_relation, set_diplomatic_state
    player = getattr(world, "player_nation", "France")
    instances = getattr(world, "war_instances", {}) or {}
    for war_id in sorted(instances):
        inst = instances[war_id]
        if inst.get("ended_turn") is not None:
            continue
        active = set(inst.get("active_participants") or [])
        if len(active) < 2 or nation in active or player in active:
            continue
        # Never re-enter a war this court has already left — a renege
        # followed by a same-turn join of the OTHER side would be the
        # soap opera pin 13 bars, and rejoining any exited war reads
        # wrong whatever the exit was.
        prior = (inst.get("participant_meta") or {}).get(nation) or {}
        if prior.get("exited_turn") is not None \
                or prior.get("reneged_turn") is not None:
            continue
        att, dfd, s_att, s_dfd = _side_strengths(world, inst)
        if not att or not dfd or s_att == s_dfd:
            continue
        enemy_leader_key = ("defender_leader" if s_att > s_dfd
                            else "attacker_leader")
        enemy = str(inst.get(enemy_leader_key) or "")
        if not enemy or enemy == player or enemy not in active:
            continue
        if int(get_relation(world, nation, enemy)) >= 0:
            continue
        if not can_declare_war(world, nation, enemy).get("ok"):
            continue
        if get_free_strength(world, nation) <= 0:
            continue
        from backend.game_logic.settlement_helpers import (
            ensure_war_instance_for_pair,
        )
        prior_state = world.get_diplomatic_state(nation, enemy)
        attach = ensure_war_instance_for_pair(
            world, nation, enemy, entry_path="bandwagon",
            reason="T2-3: the bandwagoner joins the stronger side")
        if not attach.get("ok"):
            continue
        set_diplomatic_state(world, nation, enemy, "WAR", "bandwagon_join")
        from backend.game_logic.diplomatic_dialogue import modify_relation_booked
        modify_relation_booked(world, nation, enemy, -20,
                               "bandwagon_join", nation, enemy)
        world.invalidate_bloc_members_cache()
        world.invalidate_active_nations_cache()
        from backend.display_names import humanize_entity_name
        beside = str(inst.get("attacker_leader" if s_att > s_dfd
                              else "defender_leader") or "")
        message = (f"{humanize_entity_name(nation)} has watched the scales "
                   f"— and marches with the stronger: war against "
                   f"{humanize_entity_name(enemy)}, beside "
                   f"{humanize_entity_name(beside)}.")
        world.log_event({
            "type": "war_declaration",
            "aggressor": nation,
            "target": enemy,
            "previous_state": prior_state,
            "war_objective": "",
            "stated_reason": "the bandwagon — the stronger side's new friend",
            "entry_path": "bandwagon",
        })
        events.append({
            "type": "ai_bandwagon_joined",
            "nation": nation,
            "against": enemy,
            "beside": beside,
            "war_id": str(attach.get("war_id") or war_id),
            "message": message,
        })
        return


def _bandwagon_renege(world, nation: str, events: List[Dict]) -> None:
    """The renege: out of a war entered by bandwagon (the participant
    row's own `entry_path`), the turn its side reads STRICTLY weaker —
    a separate peace with every opposing court (the defection-exit idiom:
    PEACE + `cleanup_war_end`, whose ONE EXIT resolves the pairs), the
    abandoned leader's resentment booked, the `reneged_turn` stamp
    spending the campaign's one renege. A court's OWN design war never
    reneges — only a bandwagoned entry carries the path."""
    if _bandwagon_renege_spent(world, nation):
        return
    from backend.game_logic.diplomacy import cleanup_war_end, set_diplomatic_state
    instances = getattr(world, "war_instances", {}) or {}
    for war_id in sorted(instances):
        inst = instances[war_id]
        if inst.get("ended_turn") is not None:
            continue
        meta_row = (inst.get("participant_meta") or {}).get(nation) or {}
        if (meta_row.get("entry_path") != "bandwagon"
                or meta_row.get("exited_turn") is not None):
            continue
        active = set(inst.get("active_participants") or [])
        if nation not in active:
            continue
        att, dfd, s_att, s_dfd = _side_strengths(world, inst)
        side = (inst.get("side_by_nation") or {}).get(nation)
        mine, theirs = ((s_att, s_dfd) if side == "attackers"
                        else (s_dfd, s_att))
        if mine >= theirs:
            continue
        opposing = dfd if side == "attackers" else att
        abandoned = [n for n in (att if side == "attackers" else dfd)
                     if n != nation]
        for other in list(opposing):
            if world.get_diplomatic_state(nation, other) == "WAR":
                set_diplomatic_state(world, nation, other, "PEACE",
                                     "bandwagon_renege")
                cleanup_war_end(world, world._make_diplo_key(nation, other),
                                conclude_objectives=True)
        row = inst.setdefault("participant_meta", {}).setdefault(nation, {})
        turn = int(getattr(world, "current_turn", 0) or 0)
        row["reneged_turn"] = turn
        if row.get("exited_turn") is None:
            row["exited_turn"] = turn
            row["exit_path"] = "separate_peace"
        from backend.game_logic.diplomatic_dialogue import modify_relation_booked
        leader = str(inst.get("attacker_leader" if side == "attackers"
                              else "defender_leader") or "")
        if leader == nation and abandoned:
            leader = abandoned[0]
        if leader and leader != nation:
            modify_relation_booked(world, nation, leader, -20,
                                   "bandwagon_renege", nation, leader)
        world.invalidate_bloc_members_cache()
        world.invalidate_active_nations_cache()
        from backend.display_names import humanize_entity_name
        quit_names = ", ".join(humanize_entity_name(n) for n in opposing)
        message = (f"{humanize_entity_name(nation)} quits the field — the "
                   f"scales turned; a separate peace with {quit_names}.")
        world.log_event({
            "type": "third_party_peace",
            "proposer": nation,
            "accepter": opposing[0] if opposing else "",
            "broker": "",
            "consequence": "The bandwagoner's one renege is spent.",
            "message": message,
        })
        from backend.game_logic.dispatch import queue_dispatch_event
        queue_dispatch_event(world, "third_party_peace", {
            "proposer": humanize_entity_name(nation),
            "accepter": humanize_entity_name(opposing[0]) if opposing else "",
            "consequence": "the bandwagoner quits the weaker side",
        }, "always")
        events.append({
            "type": "ai_bandwagon_reneged",
            "nation": nation,
            "abandoned": abandoned,
            "war_id": war_id,
            "message": message,
        })
        return
