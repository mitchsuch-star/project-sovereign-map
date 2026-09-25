"""
Vassal System — Phase 8 Session 5

Single source of truth for vassal mechanics:
  - Vassalage creation (treaty/conquest paths)
  - Loyalty processing (drift, garrison, shared enemy, battles, relations)
  - Rebellion (loyalty=0 → WAR + marshal transfer + cascade)
  - Defection cascade (war_score < -30 + loyalty < 50)
  - Tribute collection (gold per tribute_rate)
  - Investment (1 DP + 200g → +10 loyalty)
  - Autonomy changes (puppet/satellite/autonomous)
  - Marshal assimilation (vassal marshals → player pool)
  - Continental System enforcement
"""

import random
from typing import List, Optional
from backend.display_names import display_nation, with_definite_article
from backend.models.trust import Trust
# VS-R (docs/VASSAL_DEEPENING_SPEC.md §2): imperial-grip -> vassal-loyalty
# coupling. authority.py is the leaf "one grip = one module" home, so this is a
# clean downward import (no circular risk).
from backend.models.authority import (
    AUTHORITY_ACCELERATE_BELOW,
    authority_vassal_drift,
    courting_effectiveness_scale,
    courting_unlock_bonus,
    get_authority_lever_multiplier,
    get_imperial_grip,
)

# ═══════ AUTONOMY LEVELS ═══════
AUTONOMY_PUPPET = 0       # -4 drift/turn
AUTONOMY_SATELLITE = 1    # -2 drift/turn
AUTONOMY_AUTONOMOUS = 2   # +1 drift/turn

AUTONOMY_DRIFT = {0: -4, 1: -2, 2: 1}

AUTONOMY_NAMES = {0: "Puppet", 1: "Satellite", 2: "Autonomous"}

# ═══════ TRIBUTE RATES ═══════
TRIBUTE_RATES = {0: 1.0, 1: 0.75, 2: 0.5}  # % of vassal income

# ═══════ INVESTMENT COSTS ═══════
INVEST_DP_COST = 1
INVEST_GOLD_COST = 200
INVEST_LOYALTY_GAIN = 10
INVEST_COOLDOWN = 3

# ═══════ GARRISON LEVER (VP-D1, wired July 16, 2026) ═══════
# Flat, presence-based. Deliberately NOT the old authored +5..+8 ladder: at a
# -2 satellite drift that ladder made every other loyalty lever decorative
# (a standing +8/turn dwarfs invest's +10 one-shot on a 3-turn cooldown).
# A garrison is a deed priced in upkeep + front-line opportunity cost, so it
# keeps FULL value in the VS-R spiral band (it is not a cheap one-shot).
GARRISON_LOYALTY_BONUS = 2

# ═══════ THE DEFECTION (VS-6, July 16, 2026 — VASSAL_DEEPENING_SPEC §7) ═══════
# A coalition-flip is a BRIBE: a nation at war with the lord must OFFER the
# wavering vassal a concession it values (the Treaty-of-Ried dynamic). No
# willing, able briber → the vassal stays (or collapses via the ordinary
# rebellion path). Two outcomes when the bribe lands:
#   transfer — the briber takes responsibility (pays more, passes the WPS-B
#              power cap) and becomes the new lord (reuses VS-5 transfer_vassal);
#   free+WAR — the cheaper "liberation" purse: the vassal becomes independent
#              and GUARANTEED HOSTILE to its former lord (deliberate contrast
#              to the F8b graceful-PEACE fallback).
# All numbers in-band tunable.
BRIBE_TRANSFER_COST = 600      # gold: taking a vassal under your crown
BRIBE_FREE_COST = 300          # gold: merely funding its "independence"
# Deliberately equals CONTRIBUTION_DISAFFECTED_BELOW (VS-4): "first they stop
# fighting for you, then they flip" — the bribe threshold IS the disaffected
# line (pinned in test_vassal_defection.py).
BRIBE_ELIGIBLE_LOYALTY = 35
BRIBE_SPIRAL_LOYALTY = 50      # reachable when the lord's grip spirals (<30)
BRIBE_CHANCE_PIVOT = 40        # chance = (PIVOT - loyalty) / 100, grip-scaled
BRIBE_COOLDOWN = 5             # turns, per briber-vassal pair
BRIBE_VASSAL_PAUSE = 1         # per-vassal latch: one bribe attempt per turn

# ═══════ CALL-TO-ARMS (VS-4, July 16, 2026 — VASSAL_DEEPENING_SPEC §5) ═══════
# Loyalty has military teeth. Tier thresholds (in-band tunable):
#   loyal        (>= 60): full contribution, as today.
#   wavering     (35-59): the nation still answers the call, but its
#                assimilated ex-marshals drag their feet — withheld from
#                auto-reinforce/muster unless under an explicit SUPPORT
#                order (the A-D4 hostile pattern; direct orders stay obeyed).
#   disaffected  (< 35): refuses NEW calls-to-arms outright (war-cascade
#                auto-join declined). Gates only NEW wars — no retroactive
#                mid-war exit (a call-to-arms, not a desertion mechanic).
CONTRIBUTION_LOYAL_MIN = 60
CONTRIBUTION_DISAFFECTED_BELOW = 35

# ═══════ IQ-7 "THE SATELLITES HAVE A POSITION" — THE CLIENT'S PETITION ═══════
# (September 16, 2026. Build contract: the IQ-7 judge's ruling; landing record
# docs/IMPROVEMENT_QUEUE_SPEC.md §1.6; rules docs/SYSTEMS_REFERENCE.md.)
#
# Measured on the commanded 40-turn board once IQ-3's peace holds: a competent
# France AT PEACE loses 2 / 3 / 3 of its three satellites to the -2 satellite
# drift alone (6 rebellions and 2 VS-6 defections across the three seeds), and
# the only question the web ever asked was the loyalty-<=10 rebellion modal.
# Loyalty had only a downside — no benefit of a vassal scaled with it.
#
# The petition gives loyalty above 60 its first upside. Only a LOYAL client
# (>= CONTRIBUTION_LOYAL_MIN) has the STANDING to petition the Emperor, and a
# client whose petitions are honoured is BONDED: the step-6 relation term
# (`relation // 20`, 0 at boot for every satellite, dead on every measured
# arm) finally lives, +1 loyalty/turn per honoured petition, capped — the same
# idea the NA-6c carve already relies on (formations.CARVE_PATRON_RELATION).
# Refused, or left unanswered, the client spends that standing until a rival
# court can buy it. The mechanic itself lives after the LAND GRANTS section.
#
# Four flip levers, the HOST_RULE_ACTIVE idiom (BASELINE_SERIES attribution
# arms; never a config surface):
#   THE_CLIENT_PETITIONS               False = no petition is ever ISSUED.
#                                      Branches keyed on the DATA — a stored
#                                      remission, a petition pending across a
#                                      save/load — still honour it.
#   AN_UNANSWERED_PETITION_IS_REFUSED  False = a lapse costs only the stamp.
#   COURTING_SPARES_THE_LORDS_ALLIES   False = R2 off (an ally may court).
#   THE_WAVERING_LINE_IS_HONEST        False = R1 off (the old regiments line).
THE_CLIENT_PETITIONS = True
AN_UNANSWERED_PETITION_IS_REFUSED = True
COURTING_SPARES_THE_LORDS_ALLIES = True
THE_WAVERING_LINE_IS_HONEST = True

# IQ-7 review round (September 18, 2026) — four more flip levers, the same
# idiom: False reproduces the 7d10e20c behaviour byte-for-byte on its surface.
#   THE_DEED_HONOURS_THE_PETITION      R1 — a province the lord has ALREADY
#       ceded to the petitioner by VS-3's own verb (typed `cede`, the F1
#       wizard) FULFILS the petition: the capped bond step once, no DP, no
#       second loyalty gain, never a refusal — consulted FIRST in both
#       answers, before any cooldown or DP check. The refuse/lapse price is
#       waived only when the province was lost OUTSIDE the lord's hands (it
#       fell in war): a province he endowed on a marshal, or gave to another
#       client, stays a refusal. On the GRANT arm a loss of the lord's own
#       making leaves the petition STANDING (see the next lever) rather than
#       withdrawing it free. Pass 2 (P3-1): "the lord's own making" is a
#       CLASSIFICATION (`_grant_region_refusal` / `_GRANT_REFUSAL_LORDS_
#       DOING`) — a province he still holds but the WORLD made ungrantable
#       (contiguity: the client lost its adjoining province to an enemy) is
#       withdrawn free on Grant, Refuse and the lapse alike. False keeps the
#       7d10e20c arms (every ungrantable province withdrawn at the Grant; the
#       refuse/lapse arms never read the province).
#   THE_LORD_PAYS_TO_GRANT             R2 — a Grant the lord cannot pay for
#       is refused WITHOUT consuming the petition (outcome "stands": it lapses
#       at the quoted price unless refused first). False = the T11(d)
#       withdrawal, the free exit a player bought by spending DP first.
#   THE_TRANSFER_SHEDS_THE_REMISSION   R3 — `transfer_vassal` pops the old
#       lord's `remission_left` and `petitioned_turn` beside the VS-3 pops
#       (a remission is the OLD lord's purchase; the new lord never made it).
#   A_RELIEF_OF_NOTHING_IS_WITHDRAWN   R4 — a relief whose live tribute is 0
#       is withdrawn at the grant (there is nothing to remit) — the
#       re-pricer's None arm. Refusing it still costs: the waiver is for
#       inability, never for a cheaper way of saying no.
THE_DEED_HONOURS_THE_PETITION = True
THE_LORD_PAYS_TO_GRANT = True
THE_TRANSFER_SHEDS_THE_REMISSION = True
A_RELIEF_OF_NOTHING_IS_WITHDRAWN = True

# The blessed numbers. Every constant not marked "reused" is ⚠ FOR USER
# CONFIRMATION (in-band tunable; the contract's §1.1 table).
PETITION_LOYAL_MIN = CONTRIBUTION_LOYAL_MIN   # reused — the VS-4 loyal tier
PETITION_GRACE_TURNS = 5        # ⚠ FOR USER CONFIRMATION: turns since created_turn
PETITION_INTERVAL_TURNS = 8     # ⚠ FOR USER CONFIRMATION: per-vassal cadence, stamped at ISSUE whatever the answer
REMISSION_COLLECTIONS = 8       # ⚠ FOR USER CONFIRMATION: tribute collections forgone per relief grant
PETITION_RELIEF_LOYALTY = 10    # ⚠ FOR USER CONFIRMATION: x get_authority_lever_multiplier — blunted exactly as invest is
PETITION_REFUSAL_LOYALTY = 10   # ⚠ FOR USER CONFIRMATION: never blunted (VS-R Q3 — priced like autonomy-down)
PETITION_RELATION_STEP = 20     # ⚠ FOR USER CONFIRMATION: ±; `relation // 20` turns each step into ±1 loyalty/turn
PETITION_BOND_CAP = 40          # ⚠ FOR USER CONFIRMATION: a grant lifts the relation only up to 40 (two grants cancel satellite drift)
PETITION_DP_COST = 1            # reused price (grant_region_to_vassal charges its own GRANT_DP_COST)
# NOT "petition": `--petition` and "marshal petition" are the Jealousy channel.
CLIENT_PETITION_TYPE = "client_petition"

# FA-S17-D8 (slice 17, Phase 4) flip lever: the band where the mechanic BITES
# says so, once per band per vassal.
#
# The row filed this as "the rebellion warning arrives one tick before the
# rebellion" and its own reproduction narrows it: the blocking modal fires at
# loyalty <= 10 and the rebellion at <= 0, so at the ordinary -2 drift there
# are five turns of warning, and the passive `diplomatic_vassal_unrest` beat
# already covers 11-39. What is genuinely silent is the CROSSING. VS-4 gives
# loyalty military teeth at exactly 59 (a wavering satellite withholds its
# assimilated ex-marshals from auto-reinforce and from the muster preview) and
# at 34 (a disaffected one refuses NEW calls to arms outright) — and nothing
# on any surface that comes to the player says either boundary was passed.
# The per-tick line prints the NUMBER ("Bavaria loyalty 58 (-2): satellite
# drift"), which is shown-but-not-applied: the number moved by two and the
# contract underneath it changed.
#
# So the beat is the tier change, not the tick. The FIRST cut latched it in
# a `tiers_seen` list on the vassal row, and VS-R's own guardrail caught that
# immediately and was right to: the loyalty pass stamps no new key on that
# row (memo Q6). It does not need one — a crossing is a single-tick event, so
# reading THIS tick's own old and new loyalty fires each boundary exactly once
# by construction, with no store, no new field and no latch to go stale. A
# satellite that recovers and falls again is announced again, which is
# correct: it is news the second time. False = no crossing beat.
THE_TIER_CROSSING_IS_ANNOUNCED = True

# What each crossing COSTS, in the words of the mechanic that charges it.
_TIER_CROSSING_LINES = {
    "wavering": ("{vassal} is no longer a willing ally, Sire — its own "
                 "regiments will hold back from our musters and our "
                 "reinforcements until its loyalty is mended."),
    "disaffected": ("{vassal} is disaffected, Sire — it will refuse the next "
                    "call to arms outright, and a rival court may now bid "
                    "for it."),
}

# IQ-7 R1 — the wavering line tells the truth. The old sentence promised
# regiments that do not exist: VS-4 Rule 1b withholds a wavering satellite's
# ASSIMILATED ex-marshals, and on the shipped 1805 board no satellite has ever
# fielded one (measured across nine arms — the set was empty on every one).
# What the 60 boundary costs NOW is the standing to petition (IQ-7). The
# regiments clause is appended only when the lord actually fields a corps of
# the vassal's own colours, i.e. when Rule 1b is real.
#
# IQ-7 review [22] (September 18, 2026): the line names the COST only. Its
# first cut closed with "only coin, a garrison or a province will mend it
# now" — false (autonomy measurably mends it, +10), and printed beside the
# grip-aware `recovery_hint` that names the real levers on the same event.
# The remedy is that hint's to give; the crossing appends it itself only
# when the event carries none (a fall that lands below the hint's own >= 40
# gate).
_WAVERING_HONEST_LINE = (
    "{vassal} is no longer a willing ally, Sire — it has lost the standing "
    "to petition you until its loyalty is mended.")
_WAVERING_REGIMENTS_CLAUSE = (
    " Its own regiments will hold back from our musters and our "
    "reinforcements until its loyalty is mended.")


def lord_fields_the_vassals_regiments(world, lord: Optional[str],
                                      vassal_name: str) -> bool:
    """IQ-7 R1: does the lord field a marshal of the vassal's own colours
    (`original_nation == vassal`) — the only case VS-4 Rule 1b can bite."""
    if world is None:
        return False
    if not lord:
        row = (getattr(world, "vassals", {}) or {}).get(vassal_name) or {}
        lord = str(row.get("lord") or "")
    for marshal in getattr(world, "marshals", {}).values():
        if (getattr(marshal, "original_nation", None) == vassal_name
                and getattr(marshal, "nation", "") == lord):
            return True
    return False


def tier_crossing_line(vassal_name: str, old_loyalty: int,
                       new_loyalty: int, world=None, lord=None,
                       remedy_present: bool = True) -> str:
    """FA-S17-D8: the sentence for a vassal that has just FALLEN through a VS-4
    contribution boundary on THIS tick, or ''.

    Pure and stateless: the boundaries are the VS-4 constants, so the copy
    cannot drift from the mechanic that charges it, and "once per crossing"
    is a property of the arithmetic rather than of a latch. A drop that clears
    BOTH boundaries in one tick (a −10 cascade) names the worse one, which is
    the one that now binds.

    IQ-7 R1: with a `world` (and optionally the `lord`), the wavering line
    names what the boundary costs NOW and adds the regiments clause only when
    it is true. With no world the two-arg behaviour holds, so no call site
    breaks. The name is rendered through the R7 table. IQ-7 review [22]:
    `remedy_present=False` says the event carries no `recovery_hint` of its
    own, and the grip-aware hint is appended here so the player is never
    told a cost with no lever beside it.
    """
    if not THE_TIER_CROSSING_IS_ANNOUNCED:
        return ""
    old_v, new_v = int(old_loyalty), int(new_loyalty)
    # No separate "is this a fall" guard: each clause below is of the form
    # `old >= BOUND > new`, which already entails `new < old`. The first cut
    # had one and the Phase-4 sweep reported it INERT — correctly, because it
    # was unreachable, not because the pin was weak.
    tier = ""
    if old_v >= CONTRIBUTION_DISAFFECTED_BELOW > new_v:
        tier = "disaffected"
    elif old_v >= CONTRIBUTION_LOYAL_MIN > new_v:
        tier = "wavering"
    if not tier:
        return ""
    shown_name = display_nation(vassal_name)
    if tier == "wavering" and THE_WAVERING_LINE_IS_HONEST and world is not None:
        line = _WAVERING_HONEST_LINE.format(vassal=shown_name)
        if lord_fields_the_vassals_regiments(world, lord, vassal_name):
            line += _WAVERING_REGIMENTS_CLAUSE
        if not remedy_present:
            lord_name = lord
            if not lord_name:
                row = (getattr(world, "vassals", {}) or {}).get(vassal_name) or {}
                lord_name = str(row.get("lord") or "")
            if lord_name:
                line += " " + recovery_hint_for_grip(get_imperial_grip(world, lord_name))
        return line
    return _TIER_CROSSING_LINES.get(tier, "").format(vassal=shown_name)

# ═══════ LAND GRANTS (VS-3, July 16, 2026 — VASSAL_DEEPENING_SPEC §1) ═══════
# "Reward Bavaria for its service — cede it the province it bled for."
# Worth-scaled: bonus = min(CAP, BASE + income_value // DIVISOR), so a rich
# gift binds harder than a worthless moor. NEVER blunted by the VS-R spiral
# multiplier (spec §2.4-Q3: the land grant is the premier arresting lever).
# Cost: the land IS the cost — 1 DP, no AP (vassal-family free_actions
# convention), no gold. In-band tunable.
GRANT_LOYALTY_BASE = 10
GRANT_LOYALTY_CAP = 25
GRANT_INCOME_DIVISOR = 200
GRANT_DP_COST = 1
GRANT_COOLDOWN = 3  # turns, per-vassal (mirrors invest); anti land-shuffle

# ═══════ LOYALTY BOUNDS ═══════
LOYALTY_MIN = 0
LOYALTY_MAX = 100

# ═══════ WO-8 — THE COURTING CAP (row WO slice 9) ═══════
# Every throttle on enemy vassal courting was keyed per-COURTIER (the
# `court|{nation}|{vassal}` cooldown; the per-call `break`), never
# per-TARGET, so on the ambient 1805 board all nineteen enemy nations
# spent their first court on the same satellite in a single tick —
# Switzerland, loyalty 47 -> 0, ten of the nineteen moving it from 0 to 0
# while still charging 2 DP and raising a notification apiece. Two of the
# courtiers were France's OTHER satellites and the last was Switzerland
# courting itself, both reachable because the three French client states
# are full roster nations: they sit in world.enemy_nations AND in
# world.vassals at once.
# Flip lever for the BASELINE_SERIES attribution experiment: False
# reproduces the pre-slice behaviour byte-identically (the
# HOST_RULE_ACTIVE idiom). Not a config surface.
# Landing record: docs/WEIRD_OUTCOMES_SPEC.md §3 slice 9.
COURTING_TARGET_CAP_ACTIVE = True


# ═══════ WO-8 rider — THE DESIGN STAKE OUTRANKS THE ROSTER ═══════
# The cap hands the one slot to whoever comes FIRST in enemy-nation order,
# which is EUROPE_ROSTER order — Britain before Austria, always. That
# silently overruled NA-2 §5.4's courting bias on exactly the case it was
# written for: the bias sorts a COURTIER's candidate vassals, never
# courtiers per target, so a Britain court with no design stake consumed
# the slot an Austria that covets Milan should have had. A courtier with
# no stake now stands aside for one that has, when that one can still act
# this turn.
# Flip lever for the BASELINE_SERIES attribution experiment: False
# reproduces the pre-rider behaviour byte-identically (the
# HOST_RULE_ACTIVE idiom). Not a config surface.
COURTING_STAKE_PRIORITY_ACTIVE = True


def courtier_yields_to_a_design_stake(world, nation: str, vassal_name: str,
                                      state: dict) -> bool:
    """True when `nation` should stand aside on this target.

    Only ever asked of a courtier that holds NO stake itself, and only
    yields to a rival that (a) holds one, (b) is not kin to the target,
    (c) can pay the 2 DP, and (d) is not on its own per-pair cooldown —
    i.e. a rival that will actually be able to take the slot. Yielding to
    a courtier that cannot act would just waste the turn's court.

    Deliberately NOT a guarantee: the stakeholder's own candidate sort may
    still send it elsewhere (it breaks after one success), in which case
    the target simply goes uncourted this turn. Courting was never
    guaranteed, and the alternative — reserving the slot — would need
    cross-courtier state the cap deliberately does not keep.
    """
    if not COURTING_STAKE_PRIORITY_ACTIVE:
        return False
    from backend.game_logic.agendas import vassal_holds_agenda_target
    if vassal_holds_agenda_target(nation, vassal_name, world):
        return False
    dp_nations = getattr(world, "nation_dp", {})
    cooldowns = getattr(world, "ai_proposal_cooldowns", {})
    for rival in getattr(world, "enemy_nations", []):
        if rival == nation:
            continue
        if dp_nations.get(rival, 0) < 2:
            continue
        if cooldowns.get("court|%s|%s" % (rival, vassal_name), 0) > 0:
            continue
        if courtier_is_of_the_same_house(world, rival, vassal_name, state):
            continue
        # IQ-7 R2, for consistency with the guard in attempt_vassal_courting:
        # a rival that is the lord's ally will stand aside itself, so it
        # cannot be the stakeholder this courtier yields the slot to.
        if (COURTING_SPARES_THE_LORDS_ALLIES
                and courtier_is_the_lords_ally(world, rival, state)):
            continue
        if vassal_holds_agenda_target(rival, vassal_name, world):
            return True
    return False


def courtier_is_the_lords_ally(world, nation: str, state: dict) -> bool:
    """IQ-7 R2 "Courting spares the lord's allies": True when `nation` stands
    in ALLIANCE or DEFENSIVE_ALLIANCE with the target vassal's lord.

    Measured (marengo, turn 29): Spain, France's ALLY on that board, courted
    France's own satellite Switzerland — `courtier_is_of_the_same_house`
    excludes only fellow vassals, never the lord's allies. Pure predicate,
    keyed on the row's `lord` (GR5: an AI lord's allies are spared the same
    way). Checked ABOVE every side effect, so a court that stands aside
    spends nothing.
    """
    lord = str((state or {}).get("lord") or "")
    if not lord or nation == lord:
        return False
    return world.get_diplomatic_state(nation, lord) in (
        "ALLIANCE", "DEFENSIVE_ALLIANCE")


def courtier_is_of_the_same_house(world, nation: str, vassal_name: str,
                                  state: dict) -> bool:
    """True when `nation` may not court `vassal_name` on kinship grounds.

    Two arms: a nation never courts ITSELF, and never courts a FELLOW
    satellite of its own lord ("fellow" means another one, hence the
    identity check — written without it the second arm silently subsumes
    the first, since a row trivially shares a lord with itself).

    Extracted as a pure predicate on purpose. Inside the loop the guard
    is unfalsifiable: `attempt_vassal_courting` skips any vassal whose
    lord is not the player, so `courtier_row["lord"] == state["lord"]`
    and `== player` are equivalent at every reachable point and no test
    through that path can tell the two formulations apart. The generality
    is real intent for the day the loop widens past player-held vassals —
    a carved client (formations.py stamps the carver) or a defected
    satellite (VS-6 transfers one to the briber) has a non-player lord —
    so it is pinned HERE, where a non-player lord is reachable.
    """
    if nation == vassal_name:
        return True
    courtier_row = world.vassals.get(nation)
    return (courtier_row is not None
            and courtier_row is not state
            and courtier_row.get("lord") == state["lord"])

# ═══════ MARSHAL ASSIMILATION ═══════
ASSIMILATION_TRUST = 40  # Starting trust for assimilated marshals


# ═══════════════════════════════════════════════════════
# VASSAL CREATION
# ═══════════════════════════════════════════════════════

def create_vassal_treaty(
    world, lord: str, vassal: str, generosity_bonus: int = 0,
    terms: list = None,
) -> dict:
    """
    Create a vassal via treaty path.

    Requires OPEN_BORDERS+ diplomatic state.
    Loyalty = 60 + (generosity_bonus * 10), capped at 100.
    Threat += 5.

    Returns result dict with success/message.
    """
    # IQ-7 review pass 4 (R4-5, R7, September 18, 2026): every sentence
    # RETURNED to the typed road names the courts by display name, with
    # their articles — never the raw tag.
    vd = _court_name(world, vassal, article=True)
    vd_cap = _court_name(world, vassal, article=True, capitalize=True)
    ld = _court_name(world, lord, article=True)
    # Validate diplomatic state
    current_state = world.get_diplomatic_state(lord, vassal)
    from backend.game_logic.diplomacy import VASSAL_MIN_STATES
    if current_state not in VASSAL_MIN_STATES:
        return {
            "success": False,
            "message": f"Cannot create vassal via treaty: requires WAR or OPEN_BORDERS+ (current: {current_state})."
        }

    # Check not already a vassal
    if vassal in world.vassals:
        return {
            "success": False,
            "message": (f"{vd_cap} is already a vassal of "
                        f"{_court_name(world, world.vassals[vassal]['lord'], article=True)}.")
        }

    # R14: Check release cooldown (blocks treaty-cycle exploit)
    cooldowns = getattr(world, 'vassal_release_cooldowns', {})
    if cooldowns.get(vassal, 0) > 0:
        return {
            "success": False,
            "message": f"Cannot vassalize {vd}: recently released ({cooldowns[vassal]} turns remaining)."
        }

    # WPS-B: Power cap gate
    from backend.game_logic.diplomacy import check_vassalage_power_cap
    cap = check_vassalage_power_cap(world, lord, vassal, terms=terms)
    if not cap["allowed"]:
        return {
            "success": False,
            "message": f"Cannot vassalize {vd}: {cap['reason']}.",
        }

    # Calculate loyalty
    loyalty = min(LOYALTY_MAX, 60 + (generosity_bonus * 10))

    # Create vassal state
    world.vassals[vassal] = {
        "lord": lord,
        "loyalty": int(loyalty),
        "autonomy": AUTONOMY_SATELLITE,  # Treaty defaults to SATELLITE
        "path": "treaty",
        "created_turn": int(world.current_turn),
        "tribute_rate": TRIBUTE_RATES[AUTONOMY_SATELLITE],
        "carved_from": None,
        "regions": None,
    }
    # Vassalage changes both bloc geometry and the active-nation roster
    # (vassals remain active even at 0 regions).
    world.invalidate_active_nations_cache()

    # Set diplomatic state to VASSAL (R2: centralized setter)
    from backend.game_logic.diplomacy import set_diplomatic_state
    set_diplomatic_state(world, lord, vassal, "VASSAL", "treaty_vassalization")

    # Coalition threat: +5 for treaty vassalization (§2a). AI-4a step 5:
    # per-target keying dissolves the old Slice-0 asymmetry — an AI lord's
    # vassalization feeds the AI's OWN slot, never the anti-player pool.
    if lord:
        from backend.game_logic.coalition import add_threat
        add_threat(world, 5, "treaty_vassalization", target=lord)

    # R48: Reconcile diplomatic conflicts
    _reconcile_vassal_diplomacy(world, lord, vassal)

    # Dispatch event (Session 8D)
    from backend.game_logic.dispatch import queue_dispatch_event
    queue_dispatch_event(world, "diplomatic_carved_vassal_created",
                        {"carved_name": vassal, "protector": lord}, "always")

    return {
        "success": True,
        "message": f"{vd_cap} has become a {AUTONOMY_NAMES[AUTONOMY_SATELLITE]} vassal of {ld} (loyalty: {int(loyalty)}).",
        "vassal_state": world.vassals[vassal].copy(),
    }


def create_vassal_conquest(world, lord: str, vassal: str, garrison_size: int = 0) -> dict:
    """
    Create a vassal via conquest path.

    Loyalty = 20 + (garrison_size // 5000), capped at 100.
    Threat += 25.
    Autonomy defaults to PUPPET.

    Returns result dict with success/message.
    """
    # IQ-7 review pass 4 (R4-5, R7, September 18, 2026): every sentence
    # RETURNED to the typed road names the courts by display name, with
    # their articles — never the raw tag.
    vd = _court_name(world, vassal, article=True)
    vd_cap = _court_name(world, vassal, article=True, capitalize=True)
    ld = _court_name(world, lord, article=True)
    if vassal in world.vassals:
        return {
            "success": False,
            "message": (f"{vd_cap} is already a vassal of "
                        f"{_court_name(world, world.vassals[vassal]['lord'], article=True)}.")
        }

    # Check release cooldown (blocks re-vassalization exploit)
    cooldowns = getattr(world, 'vassal_release_cooldowns', {})
    if cooldowns.get(vassal, 0) > 0:
        return {
            "success": False,
            "message": f"Cannot vassalize {vd}: recently released ({cooldowns[vassal]} turns remaining)."
        }

    # Require WAR state for conquest vassalization
    current_state = world.get_diplomatic_state(lord, vassal)
    if current_state != "WAR":
        return {
            "success": False,
            "message": f"Cannot conquer {vd}: must be at WAR (current: {current_state})."
        }

    # WPS-B: Power cap gate
    from backend.game_logic.diplomacy import check_vassalage_power_cap
    cap = check_vassalage_power_cap(world, lord, vassal)
    if not cap["allowed"]:
        return {
            "success": False,
            "message": (f"{vd_cap} submits, but {ld} cannot impose vassalage on so large "
                        f"a nation. Demand terms at the peace table instead."),
        }

    loyalty = min(LOYALTY_MAX, 20 + (garrison_size // 5000))

    world.vassals[vassal] = {
        "lord": lord,
        "loyalty": int(loyalty),
        "autonomy": AUTONOMY_PUPPET,
        "path": "conquest",
        "created_turn": int(world.current_turn),
        "tribute_rate": TRIBUTE_RATES[AUTONOMY_PUPPET],
        "carved_from": None,
        "regions": None,
    }
    # Vassalage changes both bloc geometry and the active-nation roster
    # (vassals remain active even at 0 regions).
    world.invalidate_active_nations_cache()

    # Set diplomatic state to VASSAL (R2: centralized setter)
    from backend.game_logic.diplomacy import set_diplomatic_state
    set_diplomatic_state(world, lord, vassal, "VASSAL", "conquest_vassalization")

    # Coalition threat: +25 for conquest vassalization (§2a). AI-4a step 5:
    # the conquering lord's own slot, whoever wears the crown.
    if lord:
        from backend.game_logic.coalition import add_threat
        add_threat(world, 25, "conquest_vassalization", target=lord)

    # R48: Reconcile diplomatic conflicts
    _reconcile_vassal_diplomacy(world, lord, vassal)

    # Dispatch event (Session 8D)
    from backend.game_logic.dispatch import queue_dispatch_event
    queue_dispatch_event(world, "diplomatic_carved_vassal_created",
                        {"carved_name": vassal, "protector": lord}, "always")

    return {
        "success": True,
        "message": f"{vd_cap} has been subjugated as a {AUTONOMY_NAMES[AUTONOMY_PUPPET]} vassal of {ld} (loyalty: {int(loyalty)}).",
        "vassal_state": world.vassals[vassal].copy(),
    }


def _reconcile_vassal_diplomacy(world, lord: str, vassal: str) -> None:
    """R48: Reconcile diplomatic conflicts after vassalization.

    - If vassal is at WAR with lord's allies → auto-armistice
    - If vassal is allied with lord's enemies → auto-break to PEACE
    """
    all_nations = world.get_active_nations()  # DLF-11

    for other in all_nations:
        if other == lord or other == vassal:
            continue

        lord_state = world.get_diplomatic_state(lord, other)
        vassal_state = world.get_diplomatic_state(vassal, other)

        # Vassal at WAR with lord's ally → force ARMISTICE
        if vassal_state == "WAR" and lord_state in ("DEFENSIVE_ALLIANCE", "ALLIANCE"):
            from backend.game_logic.diplomacy import set_diplomatic_state
            set_diplomatic_state(world, vassal, other, "ARMISTICE", "vassal_reconcile")

        # Vassal allied with lord's enemy → break to PEACE
        if vassal_state in ("DEFENSIVE_ALLIANCE", "ALLIANCE") and lord_state == "WAR":
            from backend.game_logic.diplomacy import set_diplomatic_state
            set_diplomatic_state(world, vassal, other, "PEACE", "vassal_reconcile")


# ═══════════════════════════════════════════════════════
# LOYALTY PROCESSING (advance_turn Step 6)
# ═══════════════════════════════════════════════════════

def recovery_hint_for_grip(grip: int) -> str:
    """VS-1/VS-R one-line reminder of the levers that actually ARREST a
    satellite's drift, grip-aware. Single source for every recovery surface
    (the per-event dispatch line AND Talleyrand's <35 advisory).

    Names ONLY working levers (playtest F1/F1c): the old copy recommended the
    autonomy lever that VS-R itself blunts in the spiral band and a nonexistent
    "large subsidy" action. The garrison lever was dropped by F1c while dead
    code, and RE-ADVERTISED when VP-D1 wired it (July 16, 2026). The land
    grant joined both copies when VS-3 landed (July 16, 2026) — it is the one
    lever the spiral never blunts (spec §2.4-Q3).
      grip >= 30 (healthy): invest and autonomy-up both pay full loyalty; a
        garrison in their capital adds a standing +2; a ceded province binds
        by its worth.
      grip <  30 (spiral):  coin (invest) and concessions (autonomy-up) are
        blunted to 40%; the garrison keeps full value but +2 cannot outrun
        the spiral alone — only CEDING LAND, winning a decisive battle
        (which restores grip), or releasing the vassal actually holds.
    """
    if grip < AUTHORITY_ACCELERATE_BELOW:
        return ("The Emperor's grip is slipping - coin and concessions no "
                "longer hold them. Cede them a province, win a decisive "
                "battle to restore your grip, or release them before they "
                "break away.")
    return ("Invest in them, grant them autonomy, garrison their capital, "
            "or cede them a province to steady them.")


def lord_garrison_present(world, lord: str, capital_name: str) -> bool:
    """VP-D1: is the lord physically garrisoning this vassal capital?

    True when a lord-nation marshal with strength stands in the capital
    (the primary lever — march a corps in and keep it there), OR when the
    lord controls the region and it holds a real garrison
    (`garrison_strength` > 0 — the detachment corner, e.g. a carved vassal
    whose capital the lord retained). The vassal's OWN capital garrison
    never counts: its controller is the vassal, not the lord.

    Single source for process_vassal_loyalty AND the /debug/vassal_loyalty
    breakdown (the F7 desync lesson — the two copies must never diverge).
    """
    region = world.regions.get(capital_name)
    if region is None:
        return False
    for marshal in world.get_marshals_in_region(capital_name):
        if (getattr(marshal, 'nation', '') == lord
                and getattr(marshal, 'strength', 0) > 0
                and not getattr(marshal, 'captured_by', '')):
            return True
    if (getattr(region, 'controller', '') == lord
            and getattr(region, 'garrison_strength', 0) > 0):
        return True
    return False


def forecast_vassal_loyalty(world, lord: str, vassal_name: str) -> dict:
    """Knowable steady-state next-turn loyalty delta for ONE vassal.

    Mirrors process_vassal_loyalty term for term EXCEPT the battle term
    (step 5), which is transient and unknowable before the turn resolves.
    Single source for the ledger Vassals tab AND the wizard preview trend
    (the F7 lesson: display forecasts that hand-copy the pipeline drift
    apart silently — the old preview trend read autonomy drift alone and
    could show "falling" for a garrisoned, subsidized satellite that was
    actually climbing).
    """
    state = (getattr(world, 'vassals', {}) or {}).get(vassal_name) or {}
    autonomy = state.get("autonomy", AUTONOMY_SATELLITE)
    drift = int(AUTONOMY_DRIFT.get(autonomy, 0))

    # Step 2: the lord's garrison (VP-D1 single-source predicate).
    garrison_present = False
    garrison_bonus = 0
    capital = world.get_nation_capital(vassal_name)
    if capital and lord_garrison_present(world, lord, capital):
        garrison_present = True
        garrison_bonus = GARRISON_LOYALTY_BONUS

    # Step 3: standing gold-subsidy treaty clauses (+1 per 100g/turn).
    subsidy_bonus = 0
    for treaty in getattr(world, 'active_treaties', {}).values():
        for clause in treaty.get("clauses", []):
            if (clause.get("type") == "gold_per_turn"
                    and clause.get("from") == lord
                    and clause.get("to") == vassal_name):
                subsidy_bonus += int(clause.get("amount", 0)) // 100

    # Step 4: shared enemies.
    shared_enemy_bonus = 0
    for other in world.get_active_nations():
        if other == lord or other == vassal_name:
            continue
        if (world.get_diplomatic_state(lord, other) == "WAR"
                and world.get_diplomatic_state(vassal_name, other) == "WAR"):
            shared_enemy_bonus += 2

    # Step 6: relations with the lord.
    relation = int(world.nation_relations.get(
        world._make_diplo_key(vassal_name, lord), 0) or 0)
    relation_modifier = relation // 20

    # Step 7: the lord's imperial grip (VS-R).
    grip = get_imperial_grip(world, lord)
    grip_drift = authority_vassal_drift(grip)

    forecast = (drift + garrison_bonus + subsidy_bonus + shared_enemy_bonus
                + relation_modifier + grip_drift)
    if forecast > 0:
        trend = "rising"
    elif forecast < 0:
        trend = "falling"
    else:
        trend = "stable"

    return {
        "forecast": int(forecast),
        "trend": trend,
        "drift": int(drift),
        "garrison_present": garrison_present,
        "garrison_bonus": int(garrison_bonus),
        "subsidy_bonus": int(subsidy_bonus),
        "shared_enemy_bonus": int(shared_enemy_bonus),
        "relation_modifier": int(relation_modifier),
        "grip": int(grip),
        "grip_drift": int(grip_drift),
        "capital": str(capital or ""),
    }


def process_vassal_loyalty(world) -> List[dict]:
    """
    Process all vassal loyalty modifiers per turn.

    Modifiers:
    - Autonomy drift: PUPPET -4, SATELLITE -2, AUTONOMOUS +1
    - Lord's garrison in the vassal capital: flat +2, presence-based
      (VP-D1 wired July 16, 2026 — see lord_garrison_present)
    - Gold investment treaty: +1 per 100g/turn from active treaty clause
    - Shared enemy: +2 per shared war (lord and vassal both at WAR with same)
    - Lord winning battles: +1 per battle won this turn (max +3)
    - Lord losing battles: -2 per battle lost this turn (max -6)
    - Relation modifier: nation_relation(vassal, lord) // 20
    - (VS-R) Emperor's faltering grip: -2 when the lord's imperial grip < 30

    Returns list of event dicts for dispatch.
    """
    events = []
    # VS-R: imperial grip is per-LORD; memoize so multiple satellites of the
    # same lord don't recompute it (GR8 — no repeated per-region scans).
    grip_by_lord: dict = {}

    for vassal_name, state in list(world.vassals.items()):
        lord = state["lord"]
        old_loyalty = state["loyalty"]
        delta = 0
        # W6-3 §5.4 (R132's 80/20): track each modifier's contribution so
        # the event can NAME its dominant causes ("puppet resentment, the
        # lord's defeats") instead of a bare delta.
        contributions: dict = {}

        def _contribute(label: str, value: int):
            nonlocal delta
            if value:
                delta += value
                contributions[label] = contributions.get(label, 0) + value

        # 1. Autonomy drift
        autonomy = state.get("autonomy", AUTONOMY_SATELLITE)
        drift = AUTONOMY_DRIFT.get(autonomy, 0)
        drift_label = ("puppet resentment" if autonomy == AUTONOMY_PUPPET
                       else "satellite drift" if autonomy == AUTONOMY_SATELLITE
                       else "autonomous confidence")
        _contribute(drift_label, drift)

        # 2. The lord's garrison in the vassal capital (VP-D1 — WIRED July 16,
        # 2026; replaces the dead `garrison_troops` formula that nothing in
        # production ever assigned). Presence-based: a lord-nation corps
        # standing in the capital, or a lord-controlled capital holding a real
        # garrison. Flat +2 — full value even in the VS-R spiral band (a deed,
        # not a cheap one-shot; see GARRISON_LOYALTY_BONUS).
        vassal_capital = world.get_nation_capital(vassal_name)
        if vassal_capital and lord_garrison_present(world, lord, vassal_capital):
            _contribute("the garrison's presence", GARRISON_LOYALTY_BONUS)

        # 3. Gold investment from treaty clauses
        for pair_key, treaty in getattr(world, 'active_treaties', {}).items():
            for clause in treaty.get("clauses", []):
                if (clause.get("type") == "gold_per_turn"
                        and clause.get("from") == lord
                        and clause.get("to") == vassal_name):
                    gold_amount = clause.get("amount", 0)
                    _contribute("subsidies", int(gold_amount) // 100)

        # 4. Shared enemy bonus
        all_nations = world.get_active_nations()  # DLF-11
        shared_wars = 0
        for other_nation in all_nations:
            if other_nation == lord or other_nation == vassal_name:
                continue
            lord_state = world.get_diplomatic_state(lord, other_nation)
            vassal_state_diplo = world.get_diplomatic_state(vassal_name, other_nation)
            if lord_state == "WAR" and vassal_state_diplo == "WAR":
                shared_wars += 1
        _contribute("a common enemy", shared_wars * 2)

        # 5. Lord winning/losing battles this turn
        battles = getattr(world, 'battles_this_turn', [])
        wins = 0
        losses = 0
        for battle in battles:
            attacker_name = battle.get("attacker", "")
            defender_name = battle.get("defender", "")
            result = battle.get("result", "")
            attacker_marshal = world.get_marshal(attacker_name)
            defender_marshal = world.get_marshal(defender_name)
            atk_nation = getattr(attacker_marshal, 'nation', '') if attacker_marshal else ''
            def_nation = getattr(defender_marshal, 'nation', '') if defender_marshal else ''
            # Lord involved?
            if atk_nation != lord and def_nation != lord:
                continue
            # Lord won?
            if "attacker" in result.lower() and "victory" in result.lower():
                winner_nation = atk_nation
            elif "defender" in result.lower() and "victory" in result.lower():
                winner_nation = def_nation
            else:
                continue
            if winner_nation == lord:
                wins += 1
            else:
                losses += 1
        _contribute("the lord's victories", min(wins, 3))       # +1 per win, max +3
        _contribute("the lord's defeats", -min(losses, 3) * 2)  # -2 per loss, max -6

        # 6. Relation modifier
        diplo_key = world._make_diplo_key(vassal_name, lord)
        relation = world.nation_relations.get(diplo_key, 0)
        _contribute("relations with the lord", relation // 20)

        # 7. (VS-R) The Emperor's imperial grip. When the lord's grip spirals
        # (< 30), the whole satellite web loosens and only major concessions —
        # or winning battles — arrest it. Boot-dormant: grip >= 30 contributes
        # 0 (byte-identical — _contribute skips zero). Keys off the LORD's grip,
        # not the vassal's loyalty, so it fires symmetrically for enemy lords
        # (GR5). Read-only on authority (one-way coupling; memo Q4).
        if lord not in grip_by_lord:
            grip_by_lord[lord] = get_imperial_grip(world, lord)
        lord_grip = grip_by_lord[lord]
        _contribute("the Emperor's faltering grip", authority_vassal_drift(lord_grip))

        # (VS-2, Combat Overhaul Phase 5) The old "war weariness" offset read
        # get_coalition_loyalty_penalty(vassal_name) — but a lord's own satellite
        # is never a member of a coalition AGAINST that lord, so the term was
        # always 0 (dead code). Deleted: coalition membership is a
        # diplomatic-acceptance concept, not a loyalty-drift one.

        # Apply delta
        new_loyalty = max(LOYALTY_MIN, min(LOYALTY_MAX, old_loyalty + delta))
        state["loyalty"] = int(new_loyalty)
        # N31 (CA9): the loyalty MECHANIC already took the clamped value on
        # the line above — but the event gate, the sign and the printed
        # figure all read the RAW delta, so a vassal already at the 100
        # ceiling reported "loyalty 100 (+2)" every turn. All three French
        # vassals boot at 100, so it fired from turn 1 and four times in
        # the played campaign. `applied_delta` is what actually happened.
        applied_delta = int(new_loyalty) - int(old_loyalty)

        # Generate event if significant change.
        # VS-1 (Combat Overhaul Phase 5): the gate was abs(delta) >= 3, which
        # HID the steady satellite bleed (-2/turn) until it crossed 20 — the
        # player never saw a healthy-band vassal slipping, nor learned the
        # levers to arrest it. Lowered to >= 2 so a bare satellite's drift
        # surfaces every turn, and a recovery hint teaches the fix.
        if abs(applied_delta) >= 2 or new_loyalty <= 20:
            # W6-3 §5.4: name the top same-sign contributors (max 2) so the
            # dispatch/log line reads "Switzerland 84 (−8): puppet
            # resentment, the lord's defeats".
            sign = 1 if applied_delta >= 0 else -1
            dominant = sorted(
                ((label, value) for label, value in contributions.items()
                 if value * sign > 0),
                key=lambda kv: abs(kv[1]), reverse=True,
            )[:2]
            reason = ", ".join(label for label, _ in dominant)
            delta_str = (f"+{applied_delta}" if applied_delta >= 0
                         else str(applied_delta))

            # VS-1 "teach it": a vassal slipping while still in the healthy
            # band (>= 40) gets a one-line reminder of the arresting levers, so
            # the recovery loop is discoverable BEFORE the crisis popup at <=
            # 10. Grip-aware via the single-source helper (playtest F1: the old
            # copy named a blunted lever + a nonexistent "subsidy" + the dead
            # "garrison their capital"). VP-D1 re-wired the garrison and VS-3
            # added the land grant (both July 16, 2026).
            recovery_hint = ""
            if delta < 0 and new_loyalty >= 40:
                recovery_hint = recovery_hint_for_grip(lord_grip)

            # FA-S17-D8 (Phase 4): the CROSSING, once per band. Derived from
            # the VS-4 single source, so shown is exactly what is applied.
            crossing = tier_crossing_line(vassal_name, int(old_loyalty),
                                          int(new_loyalty), world=world,
                                          lord=lord,
                                          remedy_present=bool(recovery_hint))

            events.append({
                "type": "vassal_loyalty",
                "vassal": vassal_name,
                "lord": lord,
                # `nation` keys the dispatch relevance filter: the LORD's
                # dispatch is the one that cares about this vassal's drift.
                "nation": lord,
                "old_loyalty": int(old_loyalty),
                "new_loyalty": int(new_loyalty),
                "delta": int(applied_delta),
                "reason": reason,
                "recovery_hint": recovery_hint,
                # FA-S17-D8: display-only; the tier itself is derived.
                "tier_crossing": crossing,
                "contribution_tier": vassal_military_contribution(
                    world, vassal_name),          # VS-4 single source
                "message": (
                    f"{vassal_name} loyalty {int(new_loyalty)} ({delta_str})"
                    + (f": {reason}" if reason else "")
                    + (f" — {recovery_hint}" if recovery_hint else "")
                    + (f" {crossing}" if crossing else "")
                ),
            })

        # Dispatch events for vassal unrest (Session 8D)
        if lord == getattr(world, 'player_nation', 'France'):
            from backend.game_logic.dispatch import queue_dispatch_event
            if new_loyalty < 40 and new_loyalty > 10:
                # FA-65: the remedy, on the beat that already fires in
                # this band.
                #
                # The per-tick `recovery_hint` is gated `>= 40`, so both
                # PASSIVE surfaces go silent between 11 and 39 —
                # measured, "Switzerland loyalty 39 (-2): satellite
                # drift" with no remedy, while the AI bribe window opens
                # at 35. ⚠ The row says 35-39 is a full dead zone and
                # that is REFUTED: a THIRD producer, the diplomatic
                # ledger, carries the hint with the INVERSE gate
                # (`< 40`). So the remedy exists — on a tab the player
                # must open — and what is missing is any word of it on
                # the surface that comes to him.
                #
                # ⚠ The gate is NOT touched. Dropping the `>= 40` clause,
                # as filed, fires the hint at ANY loyalty — including 8,
                # the same turn the CRITICAL rebellion notification
                # fires — duplicates the ledger sentence verbatim, and
                # reds a standing pin that asserts silence at 30. The two
                # bands already partition cleanly; this fills the lower
                # one on its own beat.
                queue_dispatch_event(
                    world, "diplomatic_vassal_unrest",
                    {"nation": vassal_name,
                     "recovery_hint": recovery_hint_for_grip(
                         get_imperial_grip(world, lord))},
                    "player_vassal")

        # Notification + popup: rebellion imminent (Session 8C)
        if new_loyalty <= 10 and lord == getattr(world, 'player_nation', 'France'):
            from backend.notifications import (
                create_notification, NotificationPriority, VASSAL_REBELLION_IMMINENT,
            )
            # IQ-7 R7 fix in passing: the tray named the raw tag.
            world.notifications.add(create_notification(
                VASSAL_REBELLION_IMMINENT,
                NotificationPriority.HIGH,
                f"{display_nation(vassal_name)} Critical!",
                f"{display_nation(vassal_name)} loyalty critical "
                f"({int(new_loyalty)}) — rebellion imminent.",
                int(world.current_turn),
            ))
            # V2-90: Append to popup list instead of overwriting (multiple vassals)
            #
            # FA-N5 / FA-N37: the popup and the dialogue that answers it are
            # two separate dicts, and only the dialogue was ever given an
            # identity — `DialogueManager.push` stamps `dialogue_id`, the
            # hand-built popup got nothing. So the client rendered a modal it
            # could not name, answered with a bare verb, and the W6-0 guard
            # (which is gated on `dialogue_id is not None`) had nothing to
            # bind. Measured on the shipped 1805 boot: with Prussia's letter
            # holding the dialogue slot, clicking **Accept Risk** on the
            # *Holland* rebellion modal signed **PEACE -> NON_AGGRESSION with
            # Prussia** — `accept_vassal_rebellion` reaches the resolver's
            # label-containment arm, where the option label "Accept" is a
            # substring of it.
            #
            # The dialogue is therefore pushed FIRST and its identity copied
            # onto the popup, so the two travel together from here on.
            # IQ-7 R3: the Garrison option says what its handler DOES —
            # `garrison_vassal_rebellion` charges 2 AP and adds +10 loyalty
            # once, and no corps moves. The standing +2/turn (VP-D1) comes
            # only from a corps actually standing in the capital, which the
            # old copy let the player mistake this button for. Copy only:
            # labels and action ids are unchanged (FA-N5 / FA-N37 routing).
            # Review [21]: ONE writer (`garrison_option_copy`) that branches
            # on whether a corps ALREADY stands in the capital — "station
            # one" was false in Milan, where Massena stands at boot. The
            # handler's result and its refusal read the same voice
            # (`garrison_result_line` / `garrison_refusal_line`).
            _garrison_copy = garrison_option_copy(world, vassal_name, lord)
            rebellion_popup = {
                "nation": vassal_name,
                "loyalty": int(new_loyalty),
                "loyalty_max": int(100),
                "invest_cost_dp": int(1),
                "garrison_ap_cost": int(2),
                "invest_effect": "Loyalty +10",
                "garrison_effect": _garrison_copy,
                "accept_effect": "Rebellion proceeds next turn if loyalty reaches 0",
            }
            # V2-89 → R12C: push() auto-queues if another dialogue is active
            rebellion_dialogue = {
                "type": "vassal_rebellion_imminent",
                "target_nation": vassal_name,
                "talleyrand_text": (
                    f"Sire, {vassal_name} teeters on the brink of rebellion! "
                    f"Their loyalty stands at {int(new_loyalty)} — action is required."
                ),
                "options": [
                    {
                        "label": "Invest",
                        "description": "1 DP + 200g → Loyalty +10.",
                        "action": "invest_vassal_rebellion",
                    },
                    {
                        "label": "Garrison",
                        "description": _garrison_copy,
                        "action": "garrison_vassal_rebellion",
                    },
                    {
                        "label": "Accept Risk",
                        "description": "Let events unfold. Rebellion if loyalty reaches 0.",
                        "action": "accept_vassal_rebellion",
                    },
                ],
                "context": {"vassal_name": vassal_name, "loyalty": int(new_loyalty)},
                "turn_created": int(world.current_turn),
                "blocking": True,
            }
            world.dialogue_manager.push(rebellion_dialogue)
            # FA-N5: the popup now carries the identity of the dialogue that
            # answers it, so the client can name what it is answering and the
            # W6-0 stale-dialogue guard can refuse an answer aimed elsewhere.
            rebellion_popup["dialogue_id"] = rebellion_dialogue.get("dialogue_id")
            world.vassal_rebellion_imminent_popups.append(rebellion_popup)
            # Dispatch event (Session 8D)
            from backend.game_logic.dispatch import queue_dispatch_event as _qde_vassal
            _qde_vassal(world, "diplomatic_vassal_rebellion_imminent",
                        {"nation": vassal_name}, "player_vassal")

    # Notification: defection cascade — multiple vassals low (Session 8C)
    low_vassals = [
        v for v, s in world.vassals.items()
        if s.get("loyalty", 100) < 25
        and s.get("lord") == getattr(world, 'player_nation', 'France')
    ]
    if len(low_vassals) >= 2:
        from backend.notifications import (
            create_notification, NotificationPriority, DEFECTION_CASCADE,
        )
        world.notifications.add(create_notification(
            DEFECTION_CASCADE,
            NotificationPriority.HIGH,
            "Empire Trembles",
            "Multiple vassals are wavering — the empire trembles.",
            int(world.current_turn),
        ))
        # Dispatch event (Session 8D)
        from backend.game_logic.dispatch import queue_dispatch_event
        queue_dispatch_event(world, "diplomatic_defection_cascade", {}, "always")

    return events


# ═══════════════════════════════════════════════════════
# REBELLION CHECK (advance_turn Step 7)
# ═══════════════════════════════════════════════════════

# FA slice 11 flip lever: False restores the pre-slice briefing (the
# "ceased to exist" line on every break, no log row, no per-exit copy).
THE_BREAK_IS_BRIEFED_TRUTHFULLY = True

# The three ways a satellite stops being one, and what the player is told.
_VASSAL_BREAK_TEMPLATE = {
    "vassal_rebellion": "diplomatic_vassal_rebellion",
    "vassal_rebellion_armistice": "diplomatic_vassal_broke_free_armistice",
    "vassal_rebellion_independent": "diplomatic_vassal_broke_free_peace",
}

# FA-N73 (slice 12) flip lever.  False restores the pre-slice tray exactly:
# the war exit alone raises an alert and the two soft exits raise none.
A_QUIET_BREAK_STILL_RINGS_THE_BELL = True

# The two exits that are NOT a declaration of war, and the sentence each is
# owed.  Neither may say "War declared." — the armistice exit's rail line one
# row below says the opposite, and the graceful exit's state is PEACE.
_SOFT_BREAK_BODY = {
    "vassal_rebellion_independent": (
        "{vassal} is no longer our satellite. She stands alone — an "
        "independent power, and no war is declared."),
    "vassal_rebellion_armistice": (
        "{vassal} is no longer our satellite. The armistice holds — no war "
        "is declared."),
}


def record_vassal_break(
    world,
    *,
    vassal: str,
    lord: str,
    exit_path: str,
) -> None:
    """Brief and LOG a satellite breaking free (FA-2 / FA-N74 / FA-38).

    Three defects met at these three exits.

    FA-2: the dispatch's DIPLOMATIC EVENTS rail said *"Switzerland has ceased
    to exist."* while Switzerland stood at Bern at war with France. The false
    line was queued with fog rule `always`; the TRUE line was queued
    `player_vassal`, and `_is_dispatch_event_visible` reads `world.vassals` at
    RENDER time — by which point the row has been deleted. So the truth was
    dropped whichever side of the `del` it sat on: the row's "queued after the
    delete" framing is an ordering bug and it is not one. Visibility is decided
    HERE, at queue time, and it is lord-aware (GR5): the player's own satellite
    is `always`, a foreign lord's is `partial_on_nation`.

    FA-N74: none of the three exits ever wrote to `world.event_log`, so the
    campaign log, `_build_headline`'s window and Le Moniteur could not see a
    rebellion at all. `vassal_broke_free` is one type carrying its `exit`.

    FA-38: with the row logged, `_build_headline` can finally lead with it.

    The graceful-independence exit (`vassal_rebellion_independent`) is the one
    that matters most and the one the filed fix would have missed: it
    `continue`s before the notification the fix named, and on the shipped 1805
    board it is the exit BOTH big satellites take, because they cascade-joined
    France's war and hit the war-instance side conflict.
    """
    # GE-3 §2.5: a satellite breaking free during the Congress breaks the
    # hold — latched here, ahead of the briefing lever, so every exit counts
    # whatever the rail says (dormant when no Congress sits).
    from backend.game_logic.congress import note_rebellion as _congress_rebellion
    _congress_rebellion(world, vassal, lord)
    if not THE_BREAK_IS_BRIEFED_TRUTHFULLY:
        return
    from backend.game_logic.dispatch import queue_dispatch_event

    player = str(getattr(world, "player_nation", "") or "")
    template = _VASSAL_BREAK_TEMPLATE.get(exit_path)
    if template:
        queue_dispatch_event(
            world,
            template,
            {"nation": vassal, "lord": lord},
            "always" if lord == player else "partial_on_nation",
        )
    world.log_event({
        "type": "vassal_broke_free",
        "vassal": vassal,
        "lord": lord,
        "exit": exit_path,
        "turn": int(getattr(world, "current_turn", 0)),
    })

    # FA-N73 (slice 12): the last of the row's five.  The slice-11 review
    # round gave all three exits the mechanical tail and the dispatch rail
    # line; what the two SOFT exits still had was no persistent tray alert,
    # while the war exit raised a CRITICAL one — so the exit BOTH big French
    # satellites take on the 1805 board left an empire smaller by a nation
    # with nothing standing on the rail afterwards.
    #
    # Deliberately not a bare fall-through to the war exit's notification,
    # which the row asked for: its body is "…has rebelled against France!
    # War declared.", and measured on both soft exits the state is
    # VASSAL→PEACE or ARMISTICE→ARMISTICE.  That copy would re-open the
    # contradiction slice 11 closed — a CRITICAL banner announcing a war one
    # row above a rail line saying no war was declared.  HIGH, not CRITICAL:
    # a satellite walking out is grave, and it is not a crisis.
    if not A_QUIET_BREAK_STILL_RINGS_THE_BELL:
        return
    if exit_path not in _SOFT_BREAK_BODY or lord != player:
        # Lord-gated exactly like the war exit's own notification — the
        # slice-11 round closed a rail banner about somebody else's
        # satellite, and a foreign lord's break still reaches the player
        # through the dispatch line above, which IS fog-gated.
        return
    from backend.notifications import (
        create_notification as _cr_notif,
        NotificationPriority as _NP,
        VASSAL_REBELLION as _VR_CONST,
    )
    # PC-9: the collector dedupes on (type, headline, SUBJECT), and
    # `_SUBJECT_KEYS` reads `details`. Without it the subject is empty,
    # so two satellites breaking free in one turn collapse into one row
    # and no consumer can read which court it is about. Slice-12 review.
    # IQ-7 R7 fix in passing: the prose names the court, `details` keeps the
    # raw keys the PC-9 dedupe reads.
    world.notifications.add(_cr_notif(
        _VR_CONST,
        _NP.HIGH,
        f"{display_nation(vassal)} breaks free",
        _SOFT_BREAK_BODY[exit_path].format(vassal=display_nation(vassal),
                                           lord=display_nation(lord)),
        int(getattr(world, "current_turn", 0)),
        details={"vassal": vassal, "lord": lord,
                 "exit": exit_path},
    ))


# Slice-11 review round: False restores the round's pre-review behaviour
# (the armistice exit's bare `continue`, and the graceful exit's
# long-standing one, both dropping the mechanical tail).
EVERY_BREAK_COMPLETES_ITSELF = True


# FA-S17-6 (slice 17, Phase 3, September 11 2026) flip lever: every exit a
# rebellion takes retires the "rebellion imminent" question. Only
# `transfer_vassal` and `release_vassal` purged it; the WAR, independent and
# armistice exits of `check_vassal_rebellion` left it standing — delivered
# the turn AFTER "Switzerland has rebelled", answering "rebellion will
# follow", and, as the current dialogue, refusing the letter-book and a
# settlement offer for 2-5 turns ("A satellite on the edge of revolt still
# awaits your word"). Measured on 9 of 17 ambient/tyrant/emperor boards.
THE_REBELLION_RETIRES_ITS_QUESTION = True


def _retire_rebellion_question(world, vassal_name: str) -> None:
    """Purge the standing `vassal_rebellion_imminent` popup(s) and dialogue
    for `vassal_name` — the one purge `transfer_vassal` always did."""
    if getattr(world, 'vassal_rebellion_imminent_popup', None):
        if world.vassal_rebellion_imminent_popup.get("nation", "") == vassal_name:
            world.vassal_rebellion_imminent_popup = None
    if hasattr(world, 'vassal_rebellion_imminent_popups'):
        world.vassal_rebellion_imminent_popups = [
            p for p in world.vassal_rebellion_imminent_popups
            if p.get("nation") != vassal_name
        ]
    world.dialogue_manager.remove_matching(
        lambda d: (d.get("type") == "vassal_rebellion_imminent"
                   and d.get("context", {}).get("vassal_name") == vassal_name)
    )


def complete_vassal_break(world, vassal_name: str, lord: str) -> None:
    """The four things that are TRUE of a satellite leaving, however it left.

    Slice-11 review round. FA-2 gave the armistice exit an early `continue` so
    it would stop falling through to the war tail's "War declared." copy — and
    took four MECHANICAL effects with it, which the comment did not name and
    the record did not disclose. Three review lenses found it independently.
    Measured on the shipped board, armistice exit, lever on vs off:

        marshal returned to the freed nation   False  /  True
        a sibling satellite's loyalty          100    /  90
        relation with the freed court            0    /  -50
        the lord's coalition threat              70   /  60

    The GRACEFUL-INDEPENDENCE exit has had the same gap since long before this
    slice — its own `continue` predates it, and the lever does not touch that
    branch — which matters, because that is the exit BOTH big satellites take
    on the 1805 board. Measured there too: the marshal is not returned, the
    siblings do not notice, the relation does not move. So all three exits
    call this now.

    What is NOT here, deliberately: the CRITICAL "War declared." notification
    and the `vassal_rebellion` event (both false outside the war exit), and
    the VS-3 granted-province reclaim (documented WAR-only — flipping
    provinces back during a respected armistice would itself be a violation).
    """
    if not EVERY_BREAK_COMPLETES_ITSELF:
        return
    # The freed nation's own corps come home.
    for marshal in list(world.marshals.values()):
        if (getattr(marshal, 'original_nation', None) == vassal_name
                and getattr(marshal, 'nation', '') == lord):
            marshal.nation = vassal_name
            marshal.original_nation = None
            marshal.trust = Trust()
            if hasattr(marshal, 'relationship_with_lord'):
                delattr(marshal, 'relationship_with_lord')

    # The other satellites are watching.
    for other_vassal, other_state in world.vassals.items():
        if other_state["lord"] == lord:
            other_state["loyalty"] = max(
                LOYALTY_MIN, other_state["loyalty"] - 10)

    # AI-4a step 5: a shrinking empire scares Europe less.
    if lord:
        from backend.game_logic.coalition import reduce_threat
        reduce_threat(world, 10, "vassal_rebellion", target=lord)

    world.modify_nation_relation(lord, vassal_name, -50)


def check_vassal_rebellion(world) -> List[dict]:
    """
    Check for vassal rebellions. Loyalty=0 triggers rebellion.

    Effects:
    - Set diplomatic state to WAR
    - Transfer vassal marshals back to vassal nation
    - Cascade: all other vassals -10 loyalty
    - Threat -10, relation -50

    Returns list of event dicts.
    """
    events = []
    rebellions = []

    for vassal_name, state in list(world.vassals.items()):
        if state["loyalty"] <= 0:
            rebellions.append(vassal_name)

    for vassal_name in rebellions:
        lord = world.vassals[vassal_name]["lord"]
        # VS-3 reclaim: read the granted-province provenance BEFORE deleting
        # the vassal row (Golden Rule 4 — get the value, use it, THEN clear).
        # Applied only on the WAR branch below: an armistice-respected or
        # graceful-independence break KEEPS the land (flipping provinces back
        # during a respected armistice would itself be a treaty violation).
        granted_regions = list(
            world.vassals[vassal_name].get("granted_regions") or [])

        # FA-2 (slice 11): the "{carved_name} has ceased to exist." line that
        # stood here was FALSE on every exit — the satellite is breaking free,
        # not being dissolved — and it was the only dispatch trace the player
        # got, because the true line was dropped at render time. Each exit now
        # briefs itself through `record_vassal_break`. Kept behind the lever
        # so False reproduces the pre-slice briefing exactly.
        if not THE_BREAK_IS_BRIEFED_TRUTHFULLY:
            from backend.game_logic.dispatch import queue_dispatch_event
            queue_dispatch_event(world, "diplomatic_carved_vassal_dissolved",
                                {"carved_name": vassal_name}, "always")

        # Remove vassal state
        del world.vassals[vassal_name]
        world.invalidate_active_nations_cache()

        # Set diplomatic state to WAR (FINAL-2: respect armistice — skip if in ceasefire)
        diplo_key = world._make_diplo_key(lord, vassal_name)
        current_state = world.diplomatic_states.get(diplo_key, "PEACE")
        if current_state == "ARMISTICE":
            # Vassal becomes independent but armistice is respected — no war declaration
            events.append({
                "type": "vassal_rebellion_armistice",
                "vassal": vassal_name,
                "lord": lord,
                "message": f"{vassal_name} breaks free but the armistice holds — no war declared."
            })
            record_vassal_break(
                world, vassal=vassal_name, lord=lord,
                exit_path="vassal_rebellion_armistice")
            # FA-2 rider (cross-row 2 of the reproduction): this exit used to
            # fall THROUGH to the shared tail, which appended the WAR copy
            # ("War declared.") and raised the CRITICAL "has rebelled against
            # France! War declared." notification — while the state stayed
            # ARMISTICE. The armistice exit ends here, like its two siblings.
            if THE_BREAK_IS_BRIEFED_TRUTHFULLY:
                # The four mechanical effects belong INSIDE this
                # gate: with the lever down the arm falls through to
                # the war tail, which applies them itself, and a call
                # out here would double them (measured: sibling
                # loyalty -20, relation -100).
                complete_vassal_break(world, vassal_name, lord)
                if THE_REBELLION_RETIRES_ITS_QUESTION:
                    _retire_rebellion_question(world, vassal_name)  # FA-S17-6
                continue
        else:
            from backend.game_logic.diplomacy import (
                _process_war_cascade,
                set_diplomatic_state,
            )
            from backend.game_logic.settlement_helpers import (
                CascadeContext,
                ensure_war_instance_for_pair,
            )

            # Slice A2 §7.2 "Direct WAR-entry rule": the vassal-rebellion
            # seam must allocate / reuse a war_instance BEFORE mutating
            # diplomatic_states, then thread the allocated war_id through
            # the cascade so allied joins attach to the same political
            # conflict as the rebellion.
            war_instance_result = ensure_war_instance_for_pair(
                world,
                vassal_name,
                lord,
                entry_path="vassal_rebellion",
                reason="check_vassal_rebellion",
            )
            if war_instance_result.get("ok"):
                set_diplomatic_state(world, vassal_name, lord, "WAR", "vassal_rebellion")

                cascade_ctx = CascadeContext(
                    war_id=war_instance_result["war_id"],
                    root_aggressor=vassal_name,
                    war_entry_entries=[],
                )
                cascade_events = _process_war_cascade(
                    world,
                    vassal_name,
                    lord,
                    ctx=cascade_ctx,
                )
                events.extend(cascade_events)

                # VS-3 reclaim-on-rebellion: granted provinces are the first
                # to flip back when the vassal turns on its lord (WAR branch
                # only — see the provenance read above).
                reclaimed = []
                for granted_name in granted_regions:
                    granted_region = world.regions.get(granted_name)
                    if (granted_region is not None
                            and getattr(granted_region, 'controller', '') == vassal_name):
                        granted_region.controller = lord
                        reclaimed.append(granted_name)
                if reclaimed:
                    world.invalidate_active_nations_cache()
                    events.append({
                        "type": "vassal_grant_reclaimed",
                        "vassal": vassal_name,
                        "lord": lord,
                        "regions": reclaimed,
                        "message": (
                            f"{lord} reclaims the granted province"
                            f"{'s' if len(reclaimed) > 1 else ''} "
                            f"{', '.join(reclaimed)} from the rebel {vassal_name}."
                        ),
                    })
            else:
                # F8b (playtest): the vassal was already removed from
                # world.vassals (above), so simply `continue`-ing here left the
                # France|vassal diplomatic_state stuck at VASSAL — a permanent
                # orphan (unattackable, never at war, never loyalty-processed).
                # Reproduced live: a co-belligerent satellite (KoI, sharing
                # France's war vs Austria) hit a war-instance side-conflict and
                # orphaned while still holding all its territory. Resolve it as
                # GRACEFUL INDEPENDENCE — the satellite breaks free as a neutral
                # rather than declaring war (the "switch sides / join the
                # coalition" outcome is the deferred GR9 slice). Clearing the
                # VASSAL relation to PEACE removes the desync AND sidesteps the
                # war-instance conflict entirely (no new war pair needed).
                set_diplomatic_state(
                    world, vassal_name, lord, "PEACE",
                    "vassal_rebellion_independent",
                )
                events.append({
                    "type": "vassal_rebellion_independent",
                    "vassal": vassal_name,
                    "lord": lord,
                    "detail": war_instance_result.get("error"),
                    "message": (
                        f"{vassal_name} breaks free of {lord} and stands alone "
                        f"- an independent power, though no war is declared."
                    ),
                })
                record_vassal_break(
                    world, vassal=vassal_name, lord=lord,
                    exit_path="vassal_rebellion_independent")
                # PRE-EXISTING (this `continue` predates slice 11 and the
                # lever does not reach it): this exit dropped the same four
                # mechanical effects, and it is the exit BOTH big satellites
                # take on the 1805 board.
                complete_vassal_break(world, vassal_name, lord)
                if THE_REBELLION_RETIRES_ITS_QUESTION:
                    _retire_rebellion_question(world, vassal_name)  # FA-S17-6
                continue

        # The four mechanical effects, shared with the other two exits.
        complete_vassal_break(world, vassal_name, lord)
        if THE_REBELLION_RETIRES_ITS_QUESTION:
            _retire_rebellion_question(world, vassal_name)  # FA-S17-6
        if not EVERY_BREAK_COMPLETES_ITSELF:
            for marshal in list(world.marshals.values()):
                if (getattr(marshal, 'original_nation', None) == vassal_name
                        and getattr(marshal, 'nation', '') == lord):
                    marshal.nation = vassal_name
                    marshal.original_nation = None
                    marshal.trust = Trust()
                    if hasattr(marshal, 'relationship_with_lord'):
                        delattr(marshal, 'relationship_with_lord')
            for other_vassal, other_state in world.vassals.items():
                if other_state["lord"] == lord:
                    other_state["loyalty"] = max(
                        LOYALTY_MIN, other_state["loyalty"] - 10)
            if lord:
                from backend.game_logic.coalition import reduce_threat
                reduce_threat(world, 10, "vassal_rebellion", target=lord)
            world.modify_nation_relation(lord, vassal_name, -50)

        # Notification: vassal rebellion (Session 8C).
        #
        # Slice-11 review round: gated on the lord being the PLAYER. This was
        # the one surface in the break family left lord-blind, and once the
        # dispatch line and the campaign-log row became lord-aware it
        # CONTRADICTED them: measured, an Austria-lorded Bavaria rebelling
        # raised a CRITICAL alert on France's own rail reading "Bavaria has
        # rebelled against Austria! War declared." — a crisis banner about
        # somebody else's satellite, with no fog gate at all. A foreign
        # lord's rebellion still reaches the player through the dispatch
        # line, which IS fog-gated.
        if (not THE_BREAK_IS_BRIEFED_TRUTHFULLY
                or lord == str(getattr(world, "player_nation", "") or "")):
            from backend.notifications import (
                create_notification as _cr_notif, NotificationPriority as _NP,
            )
            from backend.notifications import VASSAL_REBELLION as _VR_CONST
            # IQ-7 R7 fix in passing: "KingdomOfItaly REBELLED!" named the
            # raw tag while the dispatch line beside it said "Kingdom of
            # Italy". The R7 table, at the producer.
            world.notifications.add(_cr_notif(
                _VR_CONST,
                _NP.CRITICAL,
                f"{display_nation(vassal_name)} REBELLED!",
                f"{display_nation(vassal_name)} has rebelled against "
                f"{display_nation(lord)}! War declared.",
                int(world.current_turn),
            ))

        events.append({
            "type": "vassal_rebellion",
            "vassal": vassal_name,
            "lord": lord,
            "message": f"{vassal_name} has REBELLED! All vassal marshals have returned to {vassal_name}. War declared.",
        })
        record_vassal_break(
            world, vassal=vassal_name, lord=lord,
            exit_path="vassal_rebellion")
        if not THE_BREAK_IS_BRIEFED_TRUTHFULLY:
            from backend.game_logic.dispatch import queue_dispatch_event
            queue_dispatch_event(world, "diplomatic_vassal_rebellion",
                                {"nation": vassal_name}, "player_vassal")

    return events


# ═══════════════════════════════════════════════════════
# DEFECTION CASCADE (advance_turn Step 5)
# ═══════════════════════════════════════════════════════

def check_defection_cascade(world) -> List[dict]:
    """
    Check for defection cascade: war_score < -30 + loyalty < 50.

    Random roll: random() < (50 - loyalty) / 100
    Fires AT MOST once per war (tracked in world.cascade_triggered).

    Returns list of event dicts.
    """
    events = []
    lord = getattr(world, 'player_nation', 'France')
    cascade_triggered = getattr(world, 'cascade_triggered', set())

    for vassal_name, state in list(world.vassals.items()):
        if state["lord"] != lord:
            continue

        loyalty = state["loyalty"]
        if loyalty >= 50:
            continue

        # Check if lord is in a war with war_score < -30
        all_nations = world.get_active_nations()  # DLF-11
        for enemy_nation in all_nations:
            if enemy_nation == lord or enemy_nation == vassal_name:
                continue

            war_state = world.get_diplomatic_state(lord, enemy_nation)
            if war_state != "WAR":
                continue

            from backend.game_logic.diplomacy import get_war_score_for
            war_score = get_war_score_for(world, lord, enemy_nation)

            if war_score >= -30:
                continue

            # Check if cascade already triggered for this war
            diplo_key = world._make_diplo_key(lord, enemy_nation)
            cascade_key = f"{vassal_name}|{diplo_key}"
            if cascade_key in cascade_triggered:
                continue

            # Roll for defection
            roll_chance = (50 - loyalty) / 100
            if random.random() < roll_chance:
                cascade_triggered.add(cascade_key)

                # Vassal defects — immediate rebellion (set to 0, triggers rebellion check)
                state["loyalty"] = LOYALTY_MIN

                events.append({
                    "type": "vassal_defection_cascade",
                    "vassal": vassal_name,
                    "lord": lord,
                    "war_against": enemy_nation,
                    "loyalty_before": int(loyalty),
                    "loyalty_after": int(state["loyalty"]),
                    "message": f"{vassal_name} is wavering! The war against {enemy_nation} shakes their loyalty.",
                })

    world.cascade_triggered = cascade_triggered
    # Dispatch: defection cascade summary if any events fired (Session 8D)
    if events:
        from backend.game_logic.dispatch import queue_dispatch_event
        queue_dispatch_event(world, "diplomatic_defection_cascade", {}, "always")
    return events


# ═══════════════════════════════════════════════════════
# TRIBUTE PROCESSING
# ═══════════════════════════════════════════════════════

def vassal_tribute_owed(world, vassal_name: str) -> int:
    """IQ-7: THE single source for the tribute a vassal owes this turn.

    `tribute_rate` x the vassal's effective regional income, skipping any
    province a hostile army stands on (EC-W1: the lord cannot tithe revenues
    the invader is eating) — and **0 while a relief remission stands**
    (`remission_left > 0`). Four hand-copies of this arithmetic existed
    (process_vassal_tribute, ledger._build_economy, diplomatic_ledger.
    _build_vassals and the diplomacy.py wizard mirror); every one now calls
    here, so shown = applied by construction. Keyed on the row's DATA, not
    on THE_CLIENT_PETITIONS: a remission stored in a save is honoured with
    the lever down. Golden Rule 8: rides the cached region index.
    """
    row = (getattr(world, "vassals", {}) or {}).get(vassal_name)
    if not row:
        return 0
    if int(row.get("remission_left", 0) or 0) > 0:
        return 0
    tribute_rate = float(row.get("tribute_rate", 0.5))
    # The sum is `_vassal_tributable_income` (IQ-7 review R5 factored it out
    # so the province price's with/without reads the collection's own sum).
    return int(_vassal_tributable_income(world, vassal_name) * tribute_rate)


def process_vassal_tribute(world) -> dict:
    """
    Process vassal tribute payments during income phase.

    Each vassal pays tribute_rate * their regional income to their lord —
    the figure `vassal_tribute_owed` derives (IQ-7: the one source). A vassal
    under a relief remission (`remission_left > 0`) pays nothing this turn;
    the counter is consumed HERE, by the collection it remits, so "N
    collections" is exact whatever the turn ordering, and an applied 0 is
    recorded so the ledger's shown figure is the applied one.
    """
    tribute_events = {}

    for vassal_name, state in world.vassals.items():
        lord = state["lord"]
        applied = getattr(world, "_applied_income_transfers", None)

        # IQ-7 THE RELIEF: a remitted collection moves no gold and counts
        # itself down. Keyed on the row's data, never on the lever.
        remission_left = int(state.get("remission_left", 0) or 0)
        if remission_left > 0:
            state["remission_left"] = int(remission_left - 1)
            if applied is not None:
                bucket = applied.setdefault("vassal_tribute", {})
                bucket[lord] = int(bucket.get(lord, 0))
            continue

        tribute_amount = vassal_tribute_owed(world, vassal_name)
        if tribute_amount <= 0:
            continue

        # Transfer gold
        vassal_gold = world.nation_gold.get(vassal_name, 0)
        actual_tribute = min(tribute_amount, max(0, vassal_gold))
        if actual_tribute > 0:
            # IQ1-2 (3): NOT in `Spent` — this debits the VASSAL's chest, and
            # `Spent` is the player's own purchases. The lord's side is income.
            world.nation_gold[vassal_name] = int(vassal_gold - actual_tribute)
            lord_gold = world.nation_gold.get(lord, 0)
            world.nation_gold[lord] = int(lord_gold + actual_tribute)

            tribute_events[vassal_name] = {
                "amount": int(actual_tribute),
                "lord": lord,
            }

        # Record the APPLIED tribute for the ledger mirror (verify-fleet
        # correction, Aug 2026 health check — a view-time balance re-read
        # is post-debit and understates).
        if applied is not None:
            bucket = applied.setdefault("vassal_tribute", {})
            bucket[lord] = bucket.get(lord, 0) + int(actual_tribute)

    return tribute_events


# ═══════════════════════════════════════════════════════
# INVESTMENT
# ═══════════════════════════════════════════════════════

def _charge_dp(world, nation: str, amount: int) -> dict:
    """Slice-0 (Vassal Depth): charge diplomatic points nation-neutrally.

    The player's DP live on `world.diplomatic_points`; every AI nation's on
    `world.nation_dp[nation]` (the diplomacy.py break-treaty split). Returns
    {"ok": bool, "available": int}; deducts only when affordable.
    """
    player = getattr(world, 'player_nation', 'France')
    if nation == player:
        dp = getattr(world, 'diplomatic_points', 0)
        if dp < amount:
            return {"ok": False, "available": int(dp)}
        world.diplomatic_points = int(dp - amount)
        return {"ok": True, "available": int(dp)}
    nation_dp = getattr(world, 'nation_dp', {})
    dp = nation_dp.get(nation, 0)
    if dp < amount:
        return {"ok": False, "available": int(dp)}
    nation_dp[nation] = int(dp - amount)
    world.nation_dp = nation_dp
    return {"ok": True, "available": int(dp)}


def invest_in_vassal(world, vassal_name: str, actor: str = None) -> dict:
    """
    Invest in vassal: 1 DP + 200g → +10 loyalty.

    Requires:
    - Vassal exists
    - The acting nation IS the vassal's lord (Slice 0: nation-neutral — an
      AI lord invests through this same function, spending its own
      nation_dp/nation_gold; GR5)
    - Lord has DP available
    - Lord has 200+ gold
    - Not on cooldown (3 turns)

    Returns result dict.
    """
    # IQ-7 review pass 4 (R4-5, R7, September 18, 2026): every sentence this
    # verb writes names the court by its DISPLAY name, with its article —
    # measured on the typed `invest in kingdom of italy`: "Invested in
    # KingdomOfItaly: +10 loyalty…", "Investment in KingdomOfItaly on
    # cooldown…". The same `_court_name` idiom `grant_region_to_vassal` took
    # in pass 3.
    client = _court_name(world, vassal_name, article=True)
    client_cap = _court_name(world, vassal_name, article=True, capitalize=True)
    if vassal_name not in world.vassals:
        return {"success": False, "message": f"{client_cap} is not a vassal."}

    state = world.vassals[vassal_name]
    lord = state["lord"]

    # Validate caller is the lord (defaults to the player for the typed path)
    if actor is None:
        actor = getattr(world, 'player_nation', 'France')
    if lord != actor:
        return {"success": False, "message": f"Cannot invest in {client}: not your vassal."}

    # WO-D2/G1 contract 6: at full loyalty the verb refuses and charges
    # NOTHING. It used to charge 1 DP + 200g, clamp the gain to zero, and
    # report "+10 (100 → 100)" — a paid no-op on the DEFAULT interaction
    # (two of three boot vassals sit at 100). GR5: the AI invests through
    # this same function and is spared the same waste.
    if int(state.get("loyalty", 0) or 0) >= LOYALTY_MAX:
        return {
            "success": False,
            "message": (
                f"{client_cap}'s loyalty is already full "
                f"({LOYALTY_MAX}/{LOYALTY_MAX}) — the investment would buy "
                f"nothing, so nothing is charged."),
        }

    # Check cooldown
    cooldowns = getattr(world, 'vassal_investment_cooldowns', {})
    if cooldowns.get(vassal_name, 0) > 0:
        remaining = cooldowns[vassal_name]
        return {
            "success": False,
            "message": f"Investment in {client} on cooldown ({remaining} turns remaining)."
        }

    # Check gold BEFORE charging DP (no partial spend on a two-resource cost)
    gold = world.nation_gold.get(lord, 0)
    if gold < INVEST_GOLD_COST:
        return {
            "success": False,
            "message": f"Insufficient gold ({gold}/{INVEST_GOLD_COST} required)."
        }

    # Charge DP nation-neutrally (player pool vs nation_dp)
    dp_charge = _charge_dp(world, lord, INVEST_DP_COST)
    if not dp_charge["ok"]:
        return {
            "success": False,
            "message": (f"Insufficient diplomatic points "
                        f"({dp_charge['available']}/{INVEST_DP_COST} required)."),
        }

    # Apply investment. VS-R "no cheap recovery": in the spiral band (lord grip
    # < 30) the +10 loyalty is BLUNTED — you still pay full cost, which is the
    # point (a token gesture no longer holds a wavering satellite). At healthy
    # grip the multiplier is exactly 1.0, so the gain and message are byte-
    # identical to pre-VS-R.
    mult = get_authority_lever_multiplier(world, lord)
    gain = int(INVEST_LOYALTY_GAIN * mult)
    world.nation_gold[lord] = int(gold - INVEST_GOLD_COST)
    # IQ1-2 (3): investing in a satellite is a player purchase.
    world.record_gold_spent(lord, int(INVEST_GOLD_COST))
    old_loyalty = state["loyalty"]
    state["loyalty"] = int(min(LOYALTY_MAX, old_loyalty + gain))
    cooldowns[vassal_name] = INVEST_COOLDOWN
    world.vassal_investment_cooldowns = cooldowns

    blunted = "" if gain >= INVEST_LOYALTY_GAIN else (
        " — the Emperor's faltering grip blunts the gesture"
    )
    return {
        "success": True,
        "message": (
            f"Invested in {client}: +{gain} loyalty "
            f"({old_loyalty} → {state['loyalty']}){blunted}. "
            f"Cost: {INVEST_DP_COST} DP + {INVEST_GOLD_COST}g. "
            f"Cooldown: {INVEST_COOLDOWN} turns."
        ),
    }


# ═══════════════════════════════════════════════════════
# AUTONOMY CHANGES
# ═══════════════════════════════════════════════════════

def change_vassal_autonomy(world, vassal_name: str, new_level: int,
                           actor: str = None) -> dict:
    """
    Change vassal autonomy level. Costs 1 DP.

    Upgrading (more autonomy): +10 loyalty
    Downgrading (less autonomy): -15 loyalty

    Slice 0 (Vassal Depth): nation-neutral. Pre-fix this had NO lord gate and
    charged `world.diplomatic_points` unconditionally — any AI path calling it
    would have drained the PLAYER's DP for its own vassal. The actor must now
    be the vassal's lord and pays from its own pool (GR5).

    Returns result dict.
    """
    # R4-5 (R7, September 18, 2026): the court by its display name, with its
    # article — measured: "KingdomOfItaly autonomy changed: Satellite →
    # Autonomous…" on all three arms.
    client = _court_name(world, vassal_name, article=True)
    client_cap = _court_name(world, vassal_name, article=True, capitalize=True)
    if vassal_name not in world.vassals:
        return {"success": False, "message": f"{client_cap} is not a vassal."}

    if new_level not in AUTONOMY_NAMES:
        return {"success": False, "message": f"Invalid autonomy level: {new_level}. Use 0 (Puppet), 1 (Satellite), or 2 (Autonomous)."}

    state = world.vassals[vassal_name]
    lord = state.get("lord", getattr(world, 'player_nation', 'France'))
    old_level = state.get("autonomy", AUTONOMY_SATELLITE)

    # Validate caller is the lord (defaults to the player for the typed path)
    if actor is None:
        actor = getattr(world, 'player_nation', 'France')
    if lord != actor:
        return {"success": False, "message": f"Cannot change {client}'s autonomy: not your vassal."}

    if old_level == new_level:
        return {"success": False, "message": f"{client_cap} is already {AUTONOMY_NAMES[new_level]}."}

    # Charge 1 DP nation-neutrally (player pool vs nation_dp)
    dp_charge = _charge_dp(world, lord, 1)
    if not dp_charge["ok"]:
        return {"success": False, "message": f"Insufficient diplomatic points ({dp_charge['available']}/1 required)."}

    # Apply change
    state["autonomy"] = int(new_level)
    state["tribute_rate"] = TRIBUTE_RATES[new_level]

    # Loyalty adjustment
    if new_level > old_level:
        # More autonomy = vassal is happier. VS-R: the +10 is a CHEAP one-shot,
        # blunted in the lord's spiral band (byte-identical at healthy grip).
        mult = get_authority_lever_multiplier(world, lord)
        gain = int(10 * mult)
        state["loyalty"] = int(min(LOYALTY_MAX, state["loyalty"] + gain))
        # C2 (playtest): name the cause when the gesture is blunted, matching
        # invest_in_vassal — otherwise the player who followed the "grant
        # autonomy" hint hits an unexplained reduced value.
        blunted = "" if gain >= 10 else (
            " - the Emperor's faltering grip blunts the gesture"
        )
        loyalty_msg = f"+{gain} loyalty (increased autonomy){blunted}"
    else:
        # Less autonomy = vassal is unhappy. NEVER softened — low grip must not
        # cushion a downgrade (VS-R Q3).
        state["loyalty"] = int(max(LOYALTY_MIN, state["loyalty"] - 15))
        loyalty_msg = "-15 loyalty (decreased autonomy)"

    # VP-D5 (Sweep 4): surface the tribute TRADE-OFF, not just the new rate.
    # Granting autonomy is a PERMANENT income cut (Satellite 75% -> Autonomous
    # 50%); a player following the "grant autonomy" recovery hint was buying a
    # one-shot loyalty bump without being told the recurring cost. Show the
    # delta directionally so the cost/benefit is explicit at the decision point.
    old_tribute = TRIBUTE_RATES[old_level] * 100
    new_tribute = TRIBUTE_RATES[new_level] * 100
    if new_tribute < old_tribute:
        tribute_msg = (f"Tribute rate: {old_tribute:.0f}% → {new_tribute:.0f}% "
                       f"(a permanent income cut)")
    elif new_tribute > old_tribute:
        tribute_msg = (f"Tribute rate: {old_tribute:.0f}% → {new_tribute:.0f}% "
                       f"(you collect more of their income)")
    else:
        tribute_msg = f"Tribute rate: {new_tribute:.0f}%"

    return {
        "success": True,
        "message": (
            f"{client_cap} autonomy changed: "
            f"{AUTONOMY_NAMES[old_level]} → {AUTONOMY_NAMES[new_level]}. "
            f"{loyalty_msg}. {tribute_msg}."
        ),
    }


# ═══════════════════════════════════════════════════════
# CALL-TO-ARMS (VS-4)
# ═══════════════════════════════════════════════════════

def vassal_military_contribution(world, vassal_name: str) -> str:
    """VS-4 single source: how much military weight a vassal throws behind
    its lord — "loyal" / "wavering" / "disaffected" (see the tier constants).
    Consumed at four seams: the war-cascade auto-join (both arms), the
    reinforcement eligibility rule, the muster preview, and the dispatch
    copy — so shown always equals applied (W6-4).

    A non-vassal returns "loyal" (the gate simply doesn't apply).
    GR5: keys off the vassal row alone, so enemy lords' satellites tier
    identically.
    """
    state = getattr(world, 'vassals', {}).get(vassal_name)
    if not state:
        return "loyal"
    loyalty = int(state.get("loyalty", LOYALTY_MAX))
    if loyalty >= CONTRIBUTION_LOYAL_MIN:
        return "loyal"
    if loyalty >= CONTRIBUTION_DISAFFECTED_BELOW:
        return "wavering"
    return "disaffected"


# ═══════════════════════════════════════════════════════
# LAND GRANTS (VS-3)
# ═══════════════════════════════════════════════════════

def grant_loyalty_bonus(income_value: int) -> int:
    """VS-3 worth-scaled loyalty for ceding a province (see constants)."""
    return min(GRANT_LOYALTY_CAP,
               GRANT_LOYALTY_BASE + int(income_value) // GRANT_INCOME_DIVISOR)


# IQ-7 review pass 2 (P3-1, September 18, 2026): WHO made the province
# ungrantable. `_grant_region_refusal` names each refusal with a machine key;
# the keys below are the ones that can only come about by the LORD'S OWN ACT
# after a petition was issued (he endowed a marshal with the province). Every
# other key is a change in the world, not the lord's doing — above all
# `contiguity`, which breaks when the CLIENT loses its adjoining province to
# an enemy — and a petition it voids is WITHDRAWN free, never left standing
# to lapse into a priced refusal. (Ceding the province to another client and
# the grant cooldown are the lord's doing too; both are read before this
# classifier — by the controller arm and the cooldown arm of `_grant_verdict`.)
_GRANT_REFUSAL_LORDS_DOING = frozenset({"estate"})


def _grant_region_refusal(world, vassal_name: str, region_name: str,
                          lord: str) -> tuple:
    """One region's eligibility for a VS-3 grant, CLASSIFIED: `(key, reason)`
    — `("", "")` if grantable, else a machine key in {"unknown", "not_held",
    "homeland", "capital", "estate", "contiguity"} and the human-readable
    refusal reason. Rules (single source — the executor, the wizard list, the
    AI rung and the petition's re-validation all route here):

    - the lord controls it (you can only give what you hold);
    - CONQUERED land only — never the lord's own homeland (matches the ES-7
      endow triangle and the historical fantasy: Napoleon gave Bavaria
      Austrian Tyrol, not French soil);
    - no capital of any nation (capital garrisons/capture-threat mechanics
      must not change hands outside war/settlement — mirrors the estate rule);
    - not a marshal's LIVE estate (ES-7 `dotation_regions`: granting away an
      estate would silently stop paying his household — excluded, not warned);
    - contiguous to the vassal's territory, waived when the vassal holds no
      regions (carved vassals must not be permanently ineligible) or when the
      province is the vassal's OWN lost homeland (returning their soil is
      always sensible — the Ried dynamic).
    """
    region = world.regions.get(region_name)
    if region is None:
        return ("unknown", f"{region_name} is not a known province.")
    if getattr(region, 'controller', '') != lord:
        return ("not_held", f"You do not control {region_name}.")
    homeland = set(getattr(world, 'nation_starting_regions', {}).get(lord, []))
    if region_name in homeland:
        return ("homeland", f"{region_name} is {lord}'s own homeland — "
                            f"only conquered land may be ceded.")
    if getattr(region, 'is_capital', False) or getattr(region, 'region_type', '') == "capital":
        return ("capital", f"{region_name} is a capital — it cannot be given away.")
    # ES-7 estate exclusion (live claims only — mirrors dotation.py)
    from backend.game_logic.dotation import (
        capture_choice_pending,
        is_estate_respected,
    )
    for marshal in world.marshals.values():
        if region_name in (getattr(marshal, 'dotation_regions', []) or []):
            claim_region = world.regions.get(region_name)
            if claim_region is not None and (
                    claim_region.controller == marshal.nation
                    or is_estate_respected(world, marshal.name, region_name)
                    or capture_choice_pending(world, region_name)):
                return ("estate",
                        f"{region_name} is Marshal {marshal.name}'s estate — "
                        f"his title cannot be given away.")
    # Contiguity (waived for landless vassals and homeland returns)
    vassal_regions = set(world.get_nation_regions(vassal_name))
    if vassal_regions:
        from backend.models.region import get_starting_controllers
        starting_controllers = (
            getattr(world, '_starting_controllers', None)
            or get_starting_controllers()
        )
        is_homeland_return = starting_controllers.get(region_name) == vassal_name
        adjacent = set(getattr(region, 'adjacent_regions', []) or [])
        if not is_homeland_return and not (adjacent & vassal_regions):
            # R7 (P3-1): the client by its display name, with its article —
            # "the Kingdom of Italy's territory", never the raw tag (this
            # sentence reaches the petition popup's Grant reason).
            court = _court_name(world, vassal_name, article=True)
            return ("contiguity",
                    f"{region_name} does not adjoin {court}'s territory.")
    return ("", "")


def _grant_region_eligibility(world, vassal_name: str, region_name: str,
                              lord: str) -> str:
    """One region's eligibility for a VS-3 grant. Returns "" if grantable,
    else the human-readable refusal reason — `_grant_region_refusal`'s own
    sentence (the ONE rule set; this is its unclassified read for the
    executor, the wizard list and the AI rung)."""
    return _grant_region_refusal(world, vassal_name, region_name, lord)[1]


def list_grantable_regions(world, vassal_name: str, actor: str = None) -> List[dict]:
    """VS-3: the provinces the acting lord may cede to this vassal, sorted
    richest-first. Each entry states its terms (the wizard's "every option
    states its terms" rule): worth-scaled loyalty gain + the income handoff.

    NOT a hot path (a UI/action seam, called on wizard open / typed grant) —
    but still rides the cached get_nation_regions index (GR8).
    """
    if vassal_name not in getattr(world, 'vassals', {}):
        return []
    state = world.vassals[vassal_name]
    lord = actor or getattr(world, 'player_nation', 'France')
    if state.get("lord") != lord:
        return []
    out = []
    for region_name in world.get_nation_regions(lord):
        if _grant_region_eligibility(world, vassal_name, region_name, lord):
            continue
        region = world.regions[region_name]
        income = int(getattr(region, 'income_value', 0) or 0)
        out.append({
            "region": region_name,
            "income": int(region.get_effective_income()),
            "loyalty_gain": int(grant_loyalty_bonus(income)),
            "tribute_pct": int(state.get("tribute_rate", 0.75) * 100),
        })
    out.sort(key=lambda e: e["income"], reverse=True)
    return out


def grant_region_to_vassal(world, vassal_name: str, region_name: str,
                           actor: str = None) -> dict:
    """VS-3: cede a controlled province to a vassal.

    Effect: controller flips to the vassal (NO stability reset — this is a
    gift of a functioning province, not a sacking); vassal loyalty rises by
    the worth-scaled bonus (never spiral-blunted); the lord forfeits the
    region's income and the vassal now tributes it at its autonomy rate;
    provenance recorded in the vassal row's `granted_regions` so a WAR-path
    rebellion reclaims the gift. Cost: 1 DP (nation-neutral), 3-turn
    per-vassal cooldown. GR5: AI lords grant through this same function.
    """
    # IQ-7 review pass 3 (R3-8, R7): every sentence this verb writes names
    # the court by its DISPLAY name, with its article — measured on the typed
    # `cede tyrol to the kingdom of italy`: "Tyrol is ceded to
    # KingdomOfItaly… KingdomOfItaly now remits 75%…", and the cooldown
    # refusal "A grant to KingdomOfItaly is still being settled".
    client = _court_name(world, vassal_name, article=True)
    client_cap = _court_name(world, vassal_name, article=True, capitalize=True)
    if vassal_name not in getattr(world, 'vassals', {}):
        return {"success": False, "message": f"{client_cap} is not a vassal."}

    state = world.vassals[vassal_name]
    lord = state["lord"]
    if actor is None:
        actor = getattr(world, 'player_nation', 'France')
    if lord != actor:
        return {"success": False,
                "message": f"Cannot cede territory to {client}: not your vassal."}

    if state.get("grant_cooldown", 0) > 0:
        return {
            "success": False,
            "message": (f"A grant to {client} is still being settled "
                        f"({state['grant_cooldown']} turns remaining)."),
        }

    reason = _grant_region_eligibility(world, vassal_name, region_name, lord)
    if reason:
        return {"success": False, "message": f"Cannot cede {region_name}: {reason}"}

    dp_charge = _charge_dp(world, lord, GRANT_DP_COST)
    if not dp_charge["ok"]:
        return {
            "success": False,
            "message": (f"Insufficient diplomatic points "
                        f"({dp_charge['available']}/{GRANT_DP_COST} required)."),
        }

    region = world.regions[region_name]
    income_value = int(getattr(region, 'income_value', 0) or 0)
    effective_income = int(region.get_effective_income())

    # Transfer control. Deliberately NOT the settlement_ratify hostile-cession
    # idiom: no stability=50 reset (you are gifting a functioning province —
    # resetting stability would cut the very tribute this grant advertises).
    region.controller = vassal_name
    world.invalidate_active_nations_cache()

    # Worth-scaled loyalty — never blunted (spec §2.4-Q3: the premier
    # arresting lever keeps full value in the spiral band).
    bonus = grant_loyalty_bonus(income_value)
    old_loyalty = int(state["loyalty"])
    state["loyalty"] = int(min(LOYALTY_MAX, old_loyalty + bonus))

    # Provenance + cooldown (both ride the vassal row → serialize for free)
    granted = list(state.get("granted_regions") or [])
    granted.append(region_name)
    state["granted_regions"] = granted
    state["grant_cooldown"] = GRANT_COOLDOWN

    tribute_pct = int(state.get("tribute_rate", 0.75) * 100)
    return {
        "success": True,
        "message": (
            f"{region_name} is ceded to {client}. "
            f"Loyalty +{bonus} ({old_loyalty} → {state['loyalty']}). "
            f"You forfeit {effective_income}g/turn of income; "
            f"{client} now remits {tribute_pct}% of it as tribute. "
            f"Cost: {GRANT_DP_COST} DP. Cooldown: {GRANT_COOLDOWN} turns."
        ),
        "region": region_name,
        "loyalty_gain": int(bonus),
    }


# ═══════════════════════════════════════════════════════
# THE CLIENT'S PETITION (IQ-7 — levers and constants at the top of the file)
# ═══════════════════════════════════════════════════════
#
# The one non-rebellion decision the web asks. A LOYAL client petitions its
# lord — for a province the lord holds and could cede (THE PROVINCE: the VS-3
# grant, re-used whole), or, when its loyalty is forecast to fall, for relief
# from tribute (THE RELIEF: REMISSION_COLLECTIONS collections forgone).
# Granting BONDS the client — the step-6 relation term, +1 loyalty/turn per
# PETITION_RELATION_STEP, capped at PETITION_BOND_CAP; refusing, or letting
# the petition lapse, spends its standing. For the player the petition rides
# the ordinary incoming-proposal transport (deliver_ai_proposal; Builder B's
# dialogue, popup, executor arms and lapse hook branch on
# `is_client_petition`); an AI lord answers in place (GR5).
#
# State: TWO row keys on the vassal row — the WO-8 `courted_turn` / VS-3
# `grant_cooldown` idiom, serialized by the row copy, read with .get(…, 0):
#   petitioned_turn — the turn stamp written at ISSUE, whatever the answer;
#   remission_left  — collections still remitted; process_vassal_tribute
#                     consumes it, so "8 collections" is exact.
# process_vassal_loyalty writes neither (memo Q6's pin stands).

# The step-6 term in process_vassal_loyalty is `relation // 20`; the
# petition's copy derives its "loyalty a turn" figures from the same
# arithmetic so shown = applied.
_RELATION_LOYALTY_DIVISOR = 20


def is_client_petition(dialogue) -> bool:
    """True for a dialogue built from a client's petition — the key the
    transport, the executor's three answer arms and the lapse hook branch
    on (`context.proposal_type` or `context.proposal.type`)."""
    context = (dialogue or {}).get("context") or {}
    if context.get("proposal_type") == CLIENT_PETITION_TYPE:
        return True
    proposal = context.get("proposal") or {}
    return (isinstance(proposal, dict)
            and proposal.get("type") == CLIENT_PETITION_TYPE)


def petitions_live(world) -> bool:
    """IQ-7 review round [36] (September 18, 2026): ONE predicate for "may a
    petition be ISSUED on this world" — the lever AND the School of War's
    dormancy (the `jealousy_dormant` / `dotation_dormant` doctrine: an
    untaught modal does not intrude on the lesson, and the tutorial world
    seeds the three satellites at loyalty 100, so without this gate it
    issued three petitions on turns 6, 7 and 8 and lapsed each as a refusal).

    Read by the producer AND by the Vassals card's petition keys, so the two
    cannot drift — a gate on the producer alone left the card forecasting
    "may petition now" for a petition that could never come (the [36] hazard,
    measured). The DATA-keyed branches — a stored remission, a petition
    pending across a save/load — never read this.
    """
    if not THE_CLIENT_PETITIONS:
        return False
    from backend.game_logic.tutorial_state import is_tutorial_world
    return not is_tutorial_world(world)


def _dp_available(world, nation: str) -> int:
    """The lord's spendable DP, read the way `_charge_dp` reads it (player
    pool vs `nation_dp`), without charging."""
    player = getattr(world, 'player_nation', 'France')
    if nation == player:
        return int(getattr(world, 'diplomatic_points', 0) or 0)
    return int((getattr(world, 'nation_dp', {}) or {}).get(nation, 0) or 0)


def _lord_relation(world, vassal_name: str, lord: str) -> int:
    return int(world.nation_relations.get(
        world._make_diplo_key(vassal_name, lord), 0) or 0)


def _standing(relation: int) -> int:
    """The loyalty a turn the relation is worth — step 6's own arithmetic."""
    return int(relation) // _RELATION_LOYALTY_DIVISOR


def _bond_step(relation: int) -> int:
    """The relation step a grant actually applies: PETITION_RELATION_STEP,
    never past PETITION_BOND_CAP, never negative."""
    return max(0, min(PETITION_RELATION_STEP, PETITION_BOND_CAP - int(relation)))


# ─── GE-3 §2.5: the Congress doubles a client petition's loyalty stakes ────
#
# While the Congress of Paris sits for the lord (`congress.petition_stakes`,
# ×2 for the summoner, ×1 everywhere else and whenever no Congress sits) a
# client's petition carries DOUBLE LOYALTY STAKES both ways: a refusal (or a
# lapse, which is a refusal) costs twice the loyalty, and a granted RELIEF
# gains twice the loyalty. Read LIVE at every site that prices or charges
# (the subject builder, `_price_petition`, `grant_petition`,
# `refuse_petition`, `lapse_forecast`), so quote == applied. Deliberately
# NOT multiplied: the bond (relation) step — the stakes are the client's
# LOYALTY — and a PROVINCE grant's gain, which is VS-3's own worth-scaled
# figure applied by `grant_region_to_vassal` for every road that cedes land
# (the typed `cede`, the F1 wizard), not a petition price. Dormant: ×1.

def _petition_stakes(world, lord: Optional[str]) -> int:
    from backend.game_logic import congress
    return max(1, int(congress.petition_stakes(world, lord)))


def _refusal_loyalty(world, lord: Optional[str]) -> int:
    """The loyalty a refused or lapsed petition costs, before the floor
    clamp: PETITION_REFUSAL_LOYALTY × the Congress's stakes."""
    return int(PETITION_REFUSAL_LOYALTY) * _petition_stakes(world, lord)


def _relief_gain_raw(world, lord: Optional[str]) -> int:
    """The loyalty a granted relief is worth, before the ceiling clamp:
    PETITION_RELIEF_LOYALTY blunted by the lord's grip (exactly as invest
    is), × the Congress's stakes."""
    return (int(PETITION_RELIEF_LOYALTY * get_authority_lever_multiplier(world, lord))
            * _petition_stakes(world, lord))


def _stakes_clause(world, lord: Optional[str]) -> str:
    """' (×2 while the Congress of Paris sits)' while the stakes are raised,
    else '' (dormant copy byte-identical)."""
    stakes = _petition_stakes(world, lord)
    if stakes <= 1:
        return ""
    return f" (×{stakes} while the Congress of Paris sits)"


# `modify_nation_relation` clamps every relation to this band; the refusal's
# quoted step and after-figure are computed through the same clamp so a
# client at −90 is quoted the −10 it will actually lose, not −20.
_RELATION_FLOOR = -100
_RELATION_CEILING = 100


def _court_name(world, nation: str, *, article: bool = False,
                capitalize: bool = False) -> str:
    """R7: the court's CURRENT display name (formed name if it has one).

    IQ-7 review R10: `article=True` composes `with_definite_article` on it —
    "the Kingdom of Italy's tribute", while "Switzerland" stays bare — and
    `capitalize=True` is the sentence-initial form ("The Kingdom of Italy
    is no longer a vassal"). The stored `vassal_display` / `lord_display`
    term keys keep the BARE form on purpose: readers compose their own
    sentences around them (the "the the" hazard), so the article is applied
    where the sentence is written, never baked into the key.
    """
    from backend.game_logic.formations import formed_display_name
    name = formed_display_name(world, nation)
    if not article:
        return name
    return with_definite_article(name, capitalize=capitalize)


def _deck_acquire_entries(world, nation: str) -> List[dict]:
    """The nation's RAW authored acquire designs. NA-6a's raw-deck scan: the
    deck is dormant while vassalized, so `get_active_agenda` cannot see it —
    and a dormant dream is exactly what a client petitions for."""
    deck = (getattr(world, "agendas", {}) or {}).get(nation) or []
    return [entry for entry in deck
            if isinstance(entry, dict) and entry.get("type") == "acquire_regions"]


def petition_subject(world, vassal_name: str) -> Optional[dict]:
    """The ladder: THE PROVINCE, else THE RELIEF, else None.

    THE PROVINCE — the lord holds a province it could cede (VS-3's own
    eligibility, `list_grantable_regions`) and no grant is settling. A
    province in the client's own authored acquire deck outranks a richer one
    outside it; otherwise the list's own order (richest first).
    THE RELIEF — the client's steady-state loyalty forecast is falling and
    it pays a tribute there is something to remit.

    The ladder DECIDES the subject; it does not price it — `_price_petition`
    does, from live state, so the quote at issue and every later re-quote
    (`reprice_petition`) come from one arithmetic. `loyalty_gain` here is
    the RAW worth of the ask (the ladder's own figure); the priced terms
    carry the clamped one.
    """
    row = (getattr(world, "vassals", {}) or {}).get(vassal_name)
    if not row:
        return None
    lord = str(row.get("lord") or "")
    if not lord:
        return None

    if int(row.get("grant_cooldown", 0) or 0) <= 0:
        grantable = list_grantable_regions(world, vassal_name, actor=lord)
        if grantable:
            design_regions = set()
            for entry in _deck_acquire_entries(world, vassal_name):
                design_regions.update(str(r) for r in (entry.get("regions") or []))
            ranked = sorted(
                grantable,
                key=lambda e: (e["region"] not in design_regions,
                               -int(e["income"]), str(e["region"])))
            top = ranked[0]
            return {
                "subject": "province",
                "region": str(top["region"]),
                "in_design": bool(top["region"] in design_regions),
                "loyalty_gain": int(top["loyalty_gain"]),
                "income": int(top["income"]),
            }

    forecast = forecast_vassal_loyalty(world, lord, vassal_name)
    if int(forecast.get("forecast", 0)) < 0:
        tribute = int(vassal_tribute_owed(world, vassal_name))
        # A client paying nothing has nothing to be relieved of (a landless
        # or wholly-disrupted client): the ladder ends here for it.
        if tribute > 0:
            return {
                "subject": "relief",
                "tribute_per_turn": int(tribute),
                "collections": int(REMISSION_COLLECTIONS),
                "price": int(tribute * REMISSION_COLLECTIONS),
                # GE-3: × the Congress's stakes (`_relief_gain_raw`).
                "loyalty_gain": int(_relief_gain_raw(world, lord)),
                "forecast": int(forecast.get("forecast", 0)),
            }
    return None


def _number_word(n: int) -> str:
    return {1: "one", 2: "two", 3: "three", 4: "four", 5: "five"}.get(
        int(n), str(int(n)))


# ─── R5: the province's price, in the ledger's own terms ──────────────────

def _vassal_tributable_income(world, vassal_name: str) -> int:
    """The effective income the tribute rate is applied to: the vassal's
    provinces, skipping any a hostile army stands on (EC-W1). Factored out
    of `vassal_tribute_owed` so R5's with/without arithmetic reads the same
    sum the collection does — byte-identical for the collection itself."""
    disrupted = world.get_disrupted_regions()
    regions = getattr(world, "regions", {}) or {}
    total = 0
    for region_name in world.get_nation_regions(vassal_name):
        if region_name in disrupted:
            continue
        region = regions.get(region_name)
        if region is None:
            continue
        total += int(region.get_effective_income())
    return int(total)


def _upkeep_surcharge(total_strength: int, force_limit: int, rate: int,
                      europe: bool) -> int:
    """A pure mirror of `calculate_turn_upkeep`'s surcharge for a GIVEN
    force limit (the ES-3 bands + the EC-U3 Grande Armée premium), so the
    counterfactual "one province fewer" can be priced without moving a
    region. Drift-pinned against the ledger's applied net."""
    from backend.models.world_state import (
        GRANDE_ARMEE_RATE, GRANDE_ARMEE_THRESHOLD, severe_band_threshold,
    )
    surcharge = 0
    if force_limit is not None and total_strength > force_limit:
        severe_threshold = severe_band_threshold(force_limit)
        band_over = min(total_strength, severe_threshold) - force_limit
        band_severe = max(0, total_strength - severe_threshold)
        surcharge = (band_over // 1000) * (rate // 2) + (band_severe // 1000) * rate
    if europe and total_strength > GRANDE_ARMEE_THRESHOLD:
        surcharge += ((total_strength - GRANDE_ARMEE_THRESHOLD) // 1000) * GRANDE_ARMEE_RATE
    return int(surcharge)


def province_grant_price(world, lord: str, vassal_name: str,
                         region_name: str) -> dict:
    """IQ-7 review R5 ([17]/[26]): what the ledger's Net actually MOVES when
    `lord` cedes `region_name` to `vassal_name`, as a PURE with/without over
    the ledger's own terms — no controller flip, no cache invalidation, so
    it is safe in a display path (GR6/GR8).

    The four parts the copy names, each the figure the engine applies:
      income_forfeited        the province's effective income (the ledger's
                              `income` falls by it; if a hostile army stands
                              on it the `contributions` line falls by the
                              same figure, so the net of the two is 0);
      occupation_relieved     ES-2's `income_value × occupation fraction`
                              (only conquered soil is grantable, so it is
                              always present; a bankrupt lord's mercy halves
                              the TOTAL, so the delta is taken on the total);
      infrastructure_relieved EC-U2's bill on the province's works, likewise;
      tribute_gained          `vassal_tribute_owed` WITH the province minus
                              WITHOUT it — the floor-of-sum arithmetic the
                              collection uses, never per-province × rate
                              (0 while a remission stands: nothing is
                              collected until it ends);
      surcharge_rise          the ES-3 over-limit surcharge on the lower
                              force limit (`FORCE_LIMIT_PER_REGION` fewer).
    `net_delta` is their signed sum: +63 on a fresh conquest at stability
    25 (holding it costs more in occupation than it yields), −35 on stable
    soil — measured against `build_strategic_ledger`'s applied net at every
    stability tier (the drift pin), which is why the copy prints it WITH
    ITS SIGN and never calls a gain a cost.
    """
    region = (getattr(world, "regions", {}) or {}).get(region_name)
    row = (getattr(world, "vassals", {}) or {}).get(vassal_name) or {}
    parts = {
        "region": str(region_name),
        "income_forfeited": 0, "contributions_relief": 0,
        "occupation_relieved": 0, "infrastructure_relieved": 0,
        "tribute_gained": 0, "tribute_pct": int(float(row.get("tribute_rate", 0.75)) * 100),
        "remission_standing": bool(int(row.get("remission_left", 0) or 0) > 0),
        "surcharge_rise": 0, "force_limit_fall": 0, "net_delta": 0,
    }
    if region is None:
        return parts
    europe = getattr(world, "sovereign_map", "legacy") == "europe"
    effective = int(region.get_effective_income())
    disrupted = world.get_disrupted_regions() if europe else set()
    is_disrupted = region_name in disrupted
    parts["income_forfeited"] = effective
    parts["contributions_relief"] = effective if is_disrupted else 0

    bankrupt = int((getattr(world, "nation_bankruptcy_turns", {}) or {})
                   .get(lord, 0) or 0) >= 1
    occ_region = occ_total = infra_region = infra_total = 0
    if europe:
        from backend.game_logic.dotation import get_nation_dotation_map
        from backend.models.world_state import infrastructure_upkeep_rate
        homeland = set((getattr(world, "nation_starting_regions", {}) or {}).get(lord, []))
        estates = get_nation_dotation_map(world, lord)
        for name in world.get_nation_regions(lord):
            r = world.regions.get(name)
            if r is None:
                continue
            occ = 0
            if name not in estates and name not in homeland:
                occ = int(r.income_value * r.get_occupation_fraction())
            structures = sum(1 for b in r.buildings if not b.get("damaged", False))
            if getattr(r, "watchtower", None) == "active":
                structures += 1
            infra = structures * infrastructure_upkeep_rate(r)
            occ_total += occ
            infra_total += infra
            if name == region_name:
                occ_region, infra_region = occ, infra
    if bankrupt:
        parts["occupation_relieved"] = occ_total // 2 - (occ_total - occ_region) // 2
        parts["infrastructure_relieved"] = infra_total // 2 - (infra_total - infra_region) // 2
    else:
        parts["occupation_relieved"] = occ_region
        parts["infrastructure_relieved"] = infra_region

    if not parts["remission_standing"]:
        rate = float(row.get("tribute_rate", 0.5))
        base = _vassal_tributable_income(world, vassal_name)
        added = 0 if is_disrupted else effective
        parts["tribute_gained"] = int((base + added) * rate) - int(base * rate)

    force_limit = world.get_force_limit(lord)
    if force_limit is not None:
        from backend.models.world_state import (
            EUROPE_UPKEEP_RATE, FORCE_LIMIT_PER_REGION,
        )
        upkeep = world.calculate_turn_upkeep(lord)
        total_strength = int(upkeep.get("total_strength", 0) or 0)
        before = _upkeep_surcharge(total_strength, force_limit, EUROPE_UPKEEP_RATE, europe)
        after = _upkeep_surcharge(total_strength, force_limit - FORCE_LIMIT_PER_REGION,
                                  EUROPE_UPKEEP_RATE, europe)
        if bankrupt:
            before, after = before // 2, after // 2
        parts["surcharge_rise"] = int(after - before)
        parts["force_limit_fall"] = int(FORCE_LIMIT_PER_REGION)

    parts["net_delta"] = int(
        -parts["income_forfeited"] + parts["contributions_relief"]
        + parts["occupation_relieved"] + parts["infrastructure_relieved"]
        + parts["tribute_gained"] - parts["surcharge_rise"])
    return parts


def province_price_line(parts: dict, vassal_the: str = "the client") -> str:
    """The R5 sentence: the net WITH ITS SIGN, then the parts. One writer,
    read by the grant line, the result message and the lapse forecast."""
    net = int(parts.get("net_delta", 0) or 0)
    if net > 0:
        head = f"Our net rises by {net}g a turn"
    elif net < 0:
        head = f"Our net falls by {-net}g a turn"
    else:
        head = "Our net is unchanged"
    bits = [f"{int(parts.get('income_forfeited', 0))}g of income forfeited"]
    if int(parts.get("contributions_relief", 0) or 0):
        bits.append(f"{int(parts['contributions_relief'])}g of it already suspended "
                    f"by the enemy on it")
    bits.append(f"{int(parts.get('occupation_relieved', 0))}g of occupation relieved")
    if int(parts.get("infrastructure_relieved", 0) or 0):
        bits.append(f"{int(parts['infrastructure_relieved'])}g of upkeep on its works "
                    f"relieved")
    if parts.get("remission_standing"):
        bits.append(f"no tribute returned while {vassal_the}'s remission stands")
    else:
        bits.append(f"{int(parts.get('tribute_gained', 0))}g returned as tribute at "
                    f"today's {int(parts.get('tribute_pct', 0))}% rate")
    rise = int(parts.get("surcharge_rise", 0) or 0)
    fall = int(parts.get("force_limit_fall", 0) or 0)
    if rise:
        bits.append(f"the force limit falls {fall:,} (+{rise}g surcharge)")
    elif fall:
        bits.append(f"the force limit falls {fall:,} at no cost today")
    return f"{head} — {', '.join(bits)}."


# ─── the ONE pricing function (issue-time and every re-quote) ─────────────

def _design_note(world, vassal_name: str, region: str, vassal_display: str) -> tuple:
    design_regions = set()
    title = forms = ""
    for entry in _deck_acquire_entries(world, vassal_name):
        regions = [str(r) for r in (entry.get("regions") or [])]
        design_regions.update(regions)
        if region in regions and not title and not forms:
            title = str(entry.get("title") or "")
            forms = str(((entry.get("forms") or {}).get("display_name")) or "")
    in_design = region in design_regions
    if not in_design:
        return False, ""
    note = f"{region} belongs to {vassal_display}'s own design"
    if title:
        note += f" — {title}"
    if forms:
        note += f", the dream of {forms}"
    return True, note + "."


def _price_petition(world, lord: str, vassal_name: str, subject: dict, *,
                    fulfilled: bool = False) -> dict:
    """Price a FIXED subject from live state — the single arithmetic behind
    `petition_terms` (at issue) and `reprice_petition` (every later read and
    the answer itself), so quote == applied by construction.

    Figures, each the one the engine applies:
    - `loyalty_gain` — the raw worth (`loyalty_gain_raw`) CLAMPED to
      `LOYALTY_MAX − loyalty` ([04]/[26]: a client at 96 gains +4 and is
      told +4; at 100 the copy says its loyalty is already full);
    - the bond step and the after-figures, the refusal's step and loss
      through the same ±100 / LOYALTY_MIN clamps the writes apply ([05]);
    - a province's R5 parts (`province_grant_price`);
    - the lines. Vocabulary (R6/R7): the relation term is the client's
      BOND with us, never its "drift" (the −2 autonomy term) and never its
      "standing" (the standing to petition, loyalty ≥ 60).
    """
    row = world.vassals[vassal_name]
    relation = _lord_relation(world, vassal_name, lord)
    step = _bond_step(relation)
    loyalty = int(row.get("loyalty", 0) or 0)
    standing_now = _standing(relation)
    relation_after_grant = min(_RELATION_CEILING, relation + step)
    standing_after_grant = _standing(relation_after_grant)
    relation_after_refusal = max(_RELATION_FLOOR, relation - PETITION_RELATION_STEP)
    refusal_step_applied = relation - relation_after_refusal
    standing_after_refusal = _standing(relation_after_refusal)
    # GE-3 §2.5: the Congress's stakes (×2 while it sits for the lord) —
    # the same `_refusal_loyalty` `refuse_petition` charges and
    # `lapse_forecast` forecasts, so the quote is the charge.
    stakes = _petition_stakes(world, lord)
    stakes_clause = _stakes_clause(world, lord)
    refusal_loyalty = _refusal_loyalty(world, lord)
    refusal_loyalty_applied = loyalty - max(LOYALTY_MIN, loyalty - refusal_loyalty)
    vassal_display = _court_name(world, vassal_name)
    lord_display = _court_name(world, lord)
    vassal_the = _court_name(world, vassal_name, article=True)
    vassal_the_cap = _court_name(world, vassal_name, article=True, capitalize=True)

    terms = dict(subject)
    kind = str(terms.get("subject") or "")
    if kind == "province":
        region_name = str(terms.get("region") or "")
        region = world.regions[region_name]
        terms["income"] = int(region.get_effective_income())
        gain_raw = int(grant_loyalty_bonus(int(getattr(region, "income_value", 0) or 0)))
        in_design, design_note = _design_note(world, vassal_name, region_name, vassal_display)
        terms["in_design"] = bool(in_design)
        terms["price_parts"] = province_grant_price(world, lord, vassal_name, region_name)
    else:
        tribute = int(vassal_tribute_owed(world, vassal_name))
        terms["tribute_per_turn"] = tribute
        terms["collections"] = int(REMISSION_COLLECTIONS)
        terms["price"] = int(tribute * REMISSION_COLLECTIONS)
        # GE-3: × the Congress's stakes — `grant_petition` applies the same.
        gain_raw = int(_relief_gain_raw(world, lord))
        terms["forecast"] = int(forecast_vassal_loyalty(world, lord, vassal_name)
                                .get("forecast", 0))
        design_note = ""
    gain = max(0, min(gain_raw, LOYALTY_MAX - loyalty))

    terms.update({
        "vassal": vassal_name,
        "lord": lord,
        "vassal_display": vassal_display,
        "lord_display": lord_display,
        "vassal_display_the": vassal_the,
        "lord_display_the": _court_name(world, lord, article=True),
        "loyalty": loyalty,
        "loyalty_gain": int(gain),
        "loyalty_gain_raw": int(gain_raw),
        "loyalty_full": bool(gain_raw > 0 and gain <= 0 and loyalty >= LOYALTY_MAX),
        "refusal_loyalty": int(refusal_loyalty),
        "refusal_loyalty_applied": int(refusal_loyalty_applied),
        "loyalty_stakes": int(stakes),
        "relation_now": int(relation),
        "relation_step": int(step),
        "relation_after_grant": int(relation_after_grant),
        "relation_refusal_step": int(PETITION_RELATION_STEP),
        "relation_refusal_step_applied": int(refusal_step_applied),
        "relation_after_refusal": int(relation_after_refusal),
        "bond_cap": int(PETITION_BOND_CAP),
        "dp_cost": int(PETITION_DP_COST),
        "standing_now": int(standing_now),
        "standing_after_grant": int(standing_after_grant),
        "standing_after_refusal": int(standing_after_refusal),
        "lapse_counts_as_refusal": bool(AN_UNANSWERED_PETITION_IS_REFUSED),
        "design_note": design_note,
        "fulfilled": bool(fulfilled),
    })

    bond_grant = (f"its bond with us rises {relation} → {relation_after_grant} "
                  f"(worth {standing_after_grant:+d} a turn in loyalty, now "
                  f"{standing_now:+d})")
    if step <= 0:
        bond_grant = (f"its bond with us is already at the {PETITION_BOND_CAP} "
                      f"ceiling (worth {standing_now:+d} a turn in loyalty)")
    loyalty_clause = f"loyalty +{gain}"
    if terms["loyalty_full"]:
        loyalty_clause = "loyalty +0 (its loyalty is already full)"
    elif gain < gain_raw:
        loyalty_clause = f"loyalty +{gain} (to the 100 ceiling)"
    elif kind != "province":
        # GE-3: a relief's gain carries the Congress's stakes — say so.
        loyalty_clause += stakes_clause
    bond_refuse = (f"its bond with us falls {refusal_step_applied} "
                   f"({relation} → {relation_after_refusal}: worth "
                   f"{standing_after_refusal:+d} a turn in loyalty, now "
                   f"{standing_now:+d})")

    if fulfilled:
        region_name = str(terms.get("region") or "")
        terms["grant_line"] = (
            f"{region_name} has already passed to {vassal_the} by our own hand — "
            f"granting it honours the petition: {bond_grant}; no diplomatic "
            f"point is charged.")
        terms["refuse_line"] = (
            f"{region_name} is already ceded — the deed honours the petition; "
            f"there is nothing left to refuse and nothing is charged.")
        terms["lapse_line"] = (
            "Left unanswered at the turn's end, the petition closes as "
            "honoured — the deed was done.")
        terms["lapse_price_line"] = terms["lapse_line"]
    elif kind == "province":
        terms["grant_line"] = (
            f"Grant it, and {terms['region']} passes to {vassal_the}: "
            f"{loyalty_clause}, {bond_grant}, for {terms['dp_cost']} DP. "
            f"{province_price_line(terms['price_parts'], vassal_the)}")
    else:
        terms["grant_line"] = (
            f"Grant it, and {vassal_the}'s tribute of "
            f"{terms['tribute_per_turn']}g a turn is remitted for "
            f"{terms['collections']} collections ({terms['price']}g forgone): "
            f"{loyalty_clause}, {bond_grant}, for {terms['dp_cost']} DP.")
    if not fulfilled:
        terms["refuse_line"] = (
            f"Refuse it, and {vassal_the} loses {refusal_loyalty_applied} loyalty"
            f"{stakes_clause} and {bond_refuse}; nothing is charged.")
        if AN_UNANSWERED_PETITION_IS_REFUSED:
            terms["lapse_line"] = (
                "Left unanswered at the turn's end, the petition lapses — and a "
                "lapse is a refusal.")
            terms["lapse_price_line"] = (
                f"A lapse costs {vassal_the} {refusal_loyalty_applied} loyalty"
                f"{stakes_clause} and "
                f"{refusal_step_applied} bond — the same as a refusal.")
        else:
            terms["lapse_line"] = (
                f"Left unanswered at the turn's end, the petition lapses; "
                f"{vassal_the} waits {PETITION_INTERVAL_TURNS} turns before "
                f"asking again.")
            terms["lapse_price_line"] = (
                f"A lapse costs nothing; {vassal_the} waits "
                f"{PETITION_INTERVAL_TURNS} turns before asking again.")
    terms["vassal_display_the_cap"] = vassal_the_cap
    return terms


def petition_terms(world, vassal_name: str) -> Optional[dict]:
    """The single source for everything the popup, the ledger card and the
    executor show or apply AT ISSUE: `petition_subject` (the ladder) priced
    by `_price_petition` (the arithmetic every later read shares through
    `reprice_petition`). Every nation name goes through the R7 table
    (`formed_display_name`); no raw tag reaches a string.
    """
    subject = petition_subject(world, vassal_name)
    if subject is None:
        return None
    row = world.vassals[vassal_name]
    lord = str(row.get("lord") or "")
    return _price_petition(world, lord, vassal_name, subject)


# ─── R1: the deed fulfils the petition ────────────────────────────────────

def petition_is_fulfilled(world, vassal_tag: str, lord: str, petition: dict) -> bool:
    """IQ-7 review R1 ([01]): True when the petitioned province has ALREADY
    been ceded to the petitioner by the lord's own VS-3 verb — the typed
    `cede`, the F1 wizard, or `grant_region_to_vassal` by any road: subject
    `province`, the region in the row's `granted_regions` (VS-3's own
    provenance record — a province the client got some other way is not a
    gift the lord made, so it earns no bond) AND the client controls it, row
    present, lord unchanged. Pure. Consulted FIRST in both answers, before
    any cooldown or DP check (a typed cede stamps the grant cooldown, which
    the old order read as "withdrawn" — so pressing Grant paid 0 while
    ignoring the petition paid +20)."""
    if not THE_DEED_HONOURS_THE_PETITION:
        return False
    petition = petition or {}
    row = (getattr(world, "vassals", {}) or {}).get(vassal_tag)
    if not row or str(row.get("lord") or "") != lord:
        return False
    if str(petition.get("subject") or "") != "province":
        return False
    region = str(petition.get("region") or "")
    if not region or region not in (row.get("granted_regions") or []):
        return False
    region_obj = (getattr(world, "regions", {}) or {}).get(region)
    return region_obj is not None and getattr(region_obj, "controller", "") == vassal_tag


def _province_lost_outside_the_lords_hands(world, lord: str, vassal_name: str,
                                           region: str) -> bool:
    """R1's waiver test for the refuse/lapse arm: the petitioned province is
    no longer the lord's AND not by the lord's own doing — it fell in war.
    False when the lord still holds it (an estate, a cooldown: his choice),
    when he ceded it to ANOTHER of his clients, or when it is a live estate
    of one of his marshals (respected abroad)."""
    region_obj = (getattr(world, "regions", {}) or {}).get(region)
    if region_obj is None:
        return False
    controller = str(getattr(region_obj, "controller", "") or "")
    if controller == lord or controller == vassal_name:
        return False
    other = (getattr(world, "vassals", {}) or {}).get(controller) or {}
    if other and str(other.get("lord") or "") == lord:
        return False
    for marshal in getattr(world, "marshals", {}).values():
        if (getattr(marshal, "nation", "") == lord
                and region in (getattr(marshal, "dotation_regions", []) or [])):
            return False
    return True


def _world_void_cause(world, vassal_name: str, region: str, key: str,
                      reason: str) -> str:
    """The cause clause for an eligibility refusal that is a change in the
    WORLD, not the lord's act (P3-1) — no trailing period, the client named
    through `_court_name` (R7). Contiguity gets its own sentence ("no longer
    adjoins": it did at issue, or the ladder would not have asked for it)."""
    vd = _court_name(world, vassal_name, article=True)
    if key == "contiguity":
        return (f"{region} no longer adjoins {vd}'s territory and cannot be "
                f"ceded to it")
    return f"{region} can no longer be ceded to {vd} ({str(reason).rstrip('.')})"


def _province_voided_by_the_world(world, lord: str, vassal_name: str,
                                  region: str) -> str:
    """IQ-7 review pass 2 (P3-1): the cause clause when the lord still HOLDS
    the petitioned province but the WORLD — not he — made it ungrantable:
    above all a contiguity break (the client lost its adjoining province to
    an enemy). "" when the province is grantable, is no longer the lord's
    (the controller arms own that), or is ungrantable by the lord's own act
    (`_GRANT_REFUSAL_LORDS_DOING`: an estate he endowed — his answer, priced
    as a refusal). The refuse arm and the lapse forecast mirror
    `_grant_verdict` through this, so Grant, Refuse and the lapse agree: a
    petition the world voided is withdrawn free on all three. Pure."""
    region_obj = (getattr(world, "regions", {}) or {}).get(region)
    if region_obj is None or str(getattr(region_obj, "controller", "") or "") != lord:
        return ""
    key, reason = _grant_region_refusal(world, vassal_name, region, lord)
    if not key or key in _GRANT_REFUSAL_LORDS_DOING:
        return ""
    return _world_void_cause(world, vassal_name, region, key, reason)


def _withdrawn(message: str) -> dict:
    """A petition whose re-validation failed at answer time for a cause
    outside the lord's hands: nothing is charged and no refusal penalty
    applies — the petition is withdrawn."""
    return {"success": False, "withdrawn": True, "outcome": "withdrawn",
            "message": message}


def _stands(message: str) -> dict:
    """IQ-7 review R2 ([03]/[35]): a Grant the lord cannot make GOOD ON —
    he cannot pay, or he gave the province elsewhere by his own hand — has
    not answered the petition. Nothing is charged and nothing is consumed:
    the petition STANDS until the turn ends, when only a refusal or the
    lapse can end it at the quoted price. (The old rule withdrew it free —
    a player who spent his DP on ordinary verbs and pressed Grant escaped
    the −10 / −20 that Refuse and the lapse charge.)"""
    return {"success": False, "stands": True, "outcome": "stands",
            "message": message}


def _grant_verdict(world, lord: str, vassal_name: str, petition: dict) -> tuple:
    """The ONE re-validation every Grant surface reads — `grant_petition`
    (the authority), `petition_grant_availability` (the button's honest
    state) and `reprice_petition` (the quote) — in this order: the row, the
    lord, THE DEED (R1, before any cooldown or DP check), the fixed subject,
    the DP. Returns `(kind, message)` with kind in
    {"ok", "fulfilled", "withdrawn", "stands"}. Pure.

    Pass 2 (P3-1): `stands` is for the LORD'S OWN doing only — he cannot pay,
    he gave the province elsewhere, he endowed it as an estate, a grant of
    his is still settling. An eligibility refusal that is a change in the
    world (`_grant_region_refusal`'s keys outside `_GRANT_REFUSAL_LORDS_
    DOING` — contiguity: the client lost its adjoining province) is
    `withdrawn`, free. THE_DEED_HONOURS_THE_PETITION down restores the
    7d10e20c arms, which withdrew every ungrantable province."""
    petition = petition or {}
    row = (getattr(world, "vassals", {}) or {}).get(vassal_name)
    vd_cap = _court_name(world, vassal_name, article=True, capitalize=True)
    vd = _court_name(world, vassal_name, article=True)
    ld_cap = _court_name(world, lord, article=True, capitalize=True)
    ld = _court_name(world, lord, article=True)
    if not row:
        return ("withdrawn", f"{vd_cap} is no longer a vassal — the petition is withdrawn.")
    if str(row.get("lord") or "") != lord:
        return ("withdrawn", f"{vd_cap} no longer answers to {ld} — the petition is withdrawn.")
    subject = str(petition.get("subject") or "")
    region = str(petition.get("region") or "")
    if subject == "province":
        if petition_is_fulfilled(world, vassal_name, lord, petition):
            return ("fulfilled",
                    f"{region} has already passed to {vd} by our own hand — "
                    f"granting it honours the petition.")
        cooldown = int(row.get("grant_cooldown", 0) or 0)
        if THE_DEED_HONOURS_THE_PETITION:
            region_obj = (getattr(world, "regions", {}) or {}).get(region)
            controller = str(getattr(region_obj, "controller", "") or "") if region_obj else ""
            if region_obj is None:
                return ("withdrawn", f"{region} is not a known province — the petition is withdrawn.")
            if controller == vassal_name:
                return ("withdrawn", f"{vd_cap} already holds {region} — the petition is withdrawn.")
            if controller != lord:
                if _province_lost_outside_the_lords_hands(world, lord, vassal_name, region):
                    return ("withdrawn",
                            f"{region} can no longer be ceded to {vd} — it fell to "
                            f"another power; the petition is withdrawn.")
                return ("stands",
                        f"{region} was given elsewhere by our own hand — it cannot be "
                        f"ceded to {vd}. The petition stands until the turn ends, and "
                        f"a lapse is a refusal.")
            # P3-1 (pass 2): the eligibility refusals are CLASSIFIED. Only
            # the lord's own act (an estate he endowed) leaves the petition
            # standing at the refusal's price; a change in the world — the
            # CLIENT lost the province that adjoined this one — withdraws it
            # free, exactly as a province lost in war does.
            key, reason = _grant_region_refusal(world, vassal_name, region, lord)
            if key and key not in _GRANT_REFUSAL_LORDS_DOING:
                cause = _world_void_cause(world, vassal_name, region, key, reason)
                return ("withdrawn", f"{cause} — the petition is withdrawn.")
            if key:
                return ("stands",
                        f"{region} cannot be ceded to {vd} now ({reason.rstrip('.')}) — "
                        f"the petition stands until the turn ends, and a lapse is a "
                        f"refusal.")
            if cooldown > 0:
                return ("stands",
                        f"A grant to {vd} is still being settled ({cooldown} "
                        f"turn{'s' if cooldown != 1 else ''} remaining) — the petition "
                        f"stands until the turn ends, and a lapse is a refusal.")
        else:
            # 7d10e20c: the pre-review arms, byte-for-byte on their surface.
            if cooldown > 0:
                return ("withdrawn", f"A grant to {vd} is still being settled — "
                                     f"the petition is withdrawn.")
            grantable = {e["region"] for e in
                         list_grantable_regions(world, vassal_name, actor=lord)}
            if region not in grantable:
                return ("withdrawn", f"{region} can no longer be ceded to {vd} — "
                                     f"the petition is withdrawn.")
    elif subject == "relief":
        if A_RELIEF_OF_NOTHING_IS_WITHDRAWN and int(vassal_tribute_owed(world, vassal_name)) <= 0:
            return ("withdrawn", f"{vd_cap} pays no tribute now — there is nothing to "
                                 f"remit; the petition is withdrawn.")
    else:
        return ("withdrawn", "The petition names nothing that can be granted — "
                             "it is withdrawn.")
    if _dp_available(world, lord) < PETITION_DP_COST:
        if THE_LORD_PAYS_TO_GRANT:
            return ("stands",
                    f"{ld_cap} cannot spare the diplomatic point — the petition "
                    f"stands until the turn ends; keep {PETITION_DP_COST} DP to grant "
                    f"it, or refuse it.")
        return ("withdrawn", f"{ld_cap} cannot spare the diplomatic point — the "
                             f"petition is withdrawn.")
    return ("ok", "")


def petition_grant_verdict(world, lord: str, vassal_tag: str,
                           petition: dict) -> tuple:
    """The four-way re-validation, public: `(kind, message)` with kind in
    {"ok", "fulfilled", "withdrawn", "stands"} — what `grant_petition` will
    do if pressed now. The executor branches on it: only "stands" leaves
    the petition pending; every other kind is answered and retired."""
    return _grant_verdict(world, lord, vassal_tag, petition)


def petition_grant_availability(world, lord: str, vassal_tag: str,
                                petition: dict) -> tuple:
    """IQ-7 review R2: the Grant option's HONEST availability, `(enabled,
    reason)`, derived at every read from the same verdict the grant applies
    — never baked at issue (a petition is issued right after the lord's DP
    regenerates, so a flag stamped then would always read enabled: the IGR-2
    trap).

    `enabled` means "pressing Grant ENDS the petition": True for an
    ordinary grant, a fulfilled one (the press honours the deed) and a moot
    one (the press retires it, withdrawn free — the reason says so); False
    ONLY for the `stands` verdict — the lord cannot pay, or gave the
    province elsewhere by his own hand — where the press would bounce and
    the petition stays until the turn ends ([12]: only the DP arm may stay
    pending; a moot petition must still retire). `reason` carries the
    verdict's own sentence for every non-ordinary kind."""
    kind, message = _grant_verdict(world, lord, vassal_tag, petition)
    if kind == "ok":
        return (True, "")
    return (kind != "stands", message)


def reprice_petition(world, lord: str, vassal_tag: str, petition: dict) -> Optional[dict]:
    """IQ-7 review R4 ([11]/[34]/[16]/[04]): re-price the STORED subject from
    live state. Never re-runs the ladder (the ladder can change the SUBJECT
    mid-turn — a province captured this turn outranks relief — and the
    stored petition is what the answer applies; re-deciding would show one
    ask and grant another, or open a free exit from the refusal price).

    Returns the re-priced petition dict — the `petition_terms` keys, plus
    `clauses`, `grant_line` / `refuse_line` / `lapse_line`,
    `talleyrand_assessment`, `talleyrand_text`, `option_descriptions` and
    `availability` — for the transport to write back into
    `context.proposal.petition`, `popup_payload.clauses`, the option
    descriptions and `talleyrand_text` on every read, and for the answer
    handler to run immediately before `grant_petition` so quote == applied.

    None = withdraw, ONLY for: the row gone, the lord changed, the fixed
    province no longer grantable outside the lord's hands (R1: it fell in
    war; pass 2 P3-1: he holds it but the world voided it — the client lost
    its adjoining province), or a relief whose live tribute is 0. A petition the lord cannot make good on by his
    OWN doing (no DP, the province given elsewhere) is returned with its
    Grant disabled and the reason — it stands until the turn ends.
    """
    petition = petition or {}
    kind, message = _grant_verdict(world, lord, vassal_tag, petition)
    if kind == "withdrawn":
        return None
    subject = {k: petition.get(k) for k in ("subject", "region", "in_design",
                                            "loyalty_gain", "income",
                                            "tribute_per_turn", "collections",
                                            "price", "forecast")
               if k in petition}
    terms = _price_petition(world, lord, vassal_tag, subject,
                            fulfilled=(kind == "fulfilled"))
    enabled, reason = petition_grant_availability(world, lord, vassal_tag, petition)
    terms["availability"] = {"enabled": bool(enabled), "reason": str(reason)}
    clauses = [terms.get("design_note"), terms.get("grant_line"),
               terms.get("refuse_line"), terms.get("lapse_line")]
    terms["clauses"] = [str(c).strip() for c in clauses if c and str(c).strip()]
    terms["talleyrand_assessment"] = f"{terms['grant_line']} {terms['refuse_line']}"
    terms["option_descriptions"] = [terms["grant_line"], terms["refuse_line"]]
    terms["talleyrand_text"] = _petition_dialogue_text(world, vassal_tag, terms)
    return terms


def _petition_dialogue_text(world, vassal_name: str, terms: dict) -> str:
    """The dialogue body exactly as `ai_diplomacy._build_client_petition_
    dialogue` composes it, from the re-priced terms — so a re-quote can
    rewrite `talleyrand_text` byte-for-byte in the builder's shape.

    Pass 2 (P3-2): the court carries its ARTICLE exactly as the builder's
    head does — "a petition from the Kingdom of Italy. The Kingdom of Italy
    petitions…" (R10). This writer composed the bare name, and the refresh
    seam writes its output over `talleyrand_text` at every read, so the
    delivered article was undone by the first `status`."""
    from backend.game_logic.mailbox_payloads import client_petition_assessment
    court = _court_name(world, vassal_name, article=True)
    court_cap = _court_name(world, vassal_name, article=True, capitalize=True)
    diplomats = getattr(world, "diplomats", {}) or {}
    diplomat = diplomats.get(vassal_name)
    diplomat_name = diplomat.name if diplomat else f"the envoy of {court}"
    subject = str(terms.get("subject") or "")
    if subject == "province":
        ask = f"{court_cap} petitions the Emperor for a province."
    elif subject == "relief":
        ask = f"{court_cap} petitions the Emperor for relief from its tribute."
    else:
        ask = f"{court_cap} petitions the Emperor."
    body = "\n".join(f"  {line}" for line in terms.get("clauses") or [])
    assessment = client_petition_assessment({"petition": terms})
    return (f"Sire, {diplomat_name} brings a petition from {court}. {ask}"
            f"\n\n{body}\n\n{assessment}")


# ─── R7: ONE gate for the producer and the card ───────────────────────────

_GATE_COPY = {
    # P4-2 (pass 2): not a gate — the card's arm while the ask is unanswered.
    "pending": "petition on the desk",
    "eligible": "may petition",
    "loyalty": "no standing to petition",
    "grace": "{n} turn{s} until it may ask",
    "cadence": "{n} turn{s} until it may ask",
    "disrupted": "a province is disrupted",
    "dp": "the court cannot spare the diplomatic point",
    "remission": "relief running, {r} collection{rs}",
    "bonded": "bonded — nothing to ask",
    "no_subject": "nothing to ask for",
    "dormant": "no petitions on this board",
    "no_row": "not a client",
}


def _petition_gate(world, lord: str, vassal_name: str, *, turn: int,
                   projected: bool, disrupted=None,
                   waive_timing: bool = False) -> tuple:
    """Gates (a)–(g) in the producer's own order. Returns
    `(reason_key, turns_until, terms)`: `reason_key` is the FIRST failing
    gate ("eligible" when none fails), `turns_until` the number of END TURNS
    until every TIMED gate clears (0 when they have), `terms` the priced ask
    when gate (g) was reached and found one, else None.

    `projected=False` is the producer's read at ITS turn (after the advance
    increments it; DP read live; a remission blocks while `remission_left`
    > 0). `projected=True` is the Vassals card's read at the CURRENT turn,
    forecasting the NEXT advance: the grace and cadence clear at the run
    into `turn + k`, a remission of r blocks the next r advances (the
    collection that consumes its last count runs AFTER the producer, so the
    ask comes at the (r+1)th end turn — the [20] off-by-one), and gate (e)
    is skipped because DP regenerates BEFORE the producer runs (a card that
    read today's spent DP would forecast a block the advance never sees).

    GE-3 `waive_timing=True` (`present_pending_asks`, the summons of the
    Congress of Paris): the TIMED gates (b) grace and (c) cadence are waived
    — a satellite with a pending ask presents it at the summons whatever
    its clock. Every other gate holds except (e), which the summons also
    waives (see `present_pending_asks` for why); (f) a standing remission
    is DATA, not a clock, and still blocks.
    """
    row = (getattr(world, "vassals", {}) or {}).get(vassal_name)
    if not row or str(row.get("lord") or "") != lord:
        return ("no_row", 0, None)
    threshold = 1 if projected else 0
    # (a) standing
    if int(row.get("loyalty", 0) or 0) < PETITION_LOYAL_MIN:
        return ("loyalty", 0, None)
    # (b) grace / (c) cadence / (f) remission — the timed gates, each as the
    # number of end turns until it clears.
    created = int(row.get("created_turn", 0) or 0)
    grace_n = created + PETITION_GRACE_TURNS - int(turn)
    stamped = row.get("petitioned_turn")
    cadence_n = 0 if stamped is None else int(stamped) + PETITION_INTERVAL_TURNS - int(turn)
    remission = int(row.get("remission_left", 0) or 0)
    remission_n = 0 if remission <= 0 else (remission + 1 if projected else remission)
    timed = max(0, grace_n, cadence_n, remission_n)
    if grace_n > threshold and not waive_timing:
        return ("grace", timed, None)
    if cadence_n > threshold and not waive_timing:
        return ("cadence", timed, None)
    # (d) no disrupted province
    if disrupted is None:
        disrupted = world.get_disrupted_regions()
    if any(r in disrupted for r in world.get_nation_regions(vassal_name)):
        return ("disrupted", timed, None)
    # (e) the lord can pay — the producer's live read; skipped by the card
    # and at the Congress's summons (`waive_timing`, see present_pending_asks)
    if (not projected and not waive_timing
            and _dp_available(world, lord) < PETITION_DP_COST):
        return ("dp", timed, None)
    # (f) no remission standing
    if remission_n > threshold:
        return ("remission", timed, None)
    # (g) a subject
    terms = petition_terms(world, vassal_name)
    if terms is None:
        relation = _lord_relation(world, vassal_name, lord)
        return ("bonded" if relation >= PETITION_BOND_CAP else "no_subject", timed, None)
    return ("eligible", timed, terms)


def petition_gate_verdict(world, lord: str, vassal_tag: str, *,
                          turn: Optional[int] = None,
                          projected: bool = True) -> tuple:
    """IQ-7 review R7 ([08]/[20]): `(eligible, reason_key, turns_until)` —
    the ONE gate predicate the producer (`process_vassal_petitions`, via the
    same `_petition_gate`) and the Vassals card (`petition_standing_keys`)
    share, so the card can never promise a petition the producer will not
    issue. Defaults to the card's projection of the NEXT advance from the
    current turn; the producer passes its own turn with `projected=False`.
    The per-lord cap (one petition per lord per turn) is known only at
    issue and is not a per-client gate — an eligible client "may petition"
    at the turn's end."""
    if not petitions_live(world):
        return (False, "dormant", 0)
    if turn is None:
        turn = int(getattr(world, "current_turn", 0) or 0)
    key, turns, _terms = _petition_gate(world, lord, vassal_tag, turn=int(turn),
                                        projected=bool(projected))
    return (key == "eligible", key, int(turns))


def _gate_copy(key: str, turns: int, remission: int) -> str:
    # NOT named `template`: the FA-N30 producer census is scope-blind and
    # resolves every `template = ...` in this module against the vassal-break
    # `queue_dispatch_event(world, template, ...)` call (it read these ten
    # standing strings as unrenderable dispatch types).
    gate_line = _GATE_COPY.get(key, key)
    n = int(turns)
    r = int(remission)
    return gate_line.format(n=n, s="" if n == 1 else "s",
                           r=r, rs="" if r == 1 else "s")


def _petition_dialogue_parties(world, dialogue: dict) -> tuple:
    """`(vassal, lord)` of a client-petition dialogue — the ONE read of who
    asked whom (the terms' own `proposer_nation` / `target_nation`, then the
    context's `source_nation`, then the dialogue's `target_nation`; the lord
    defaults to the player, the only lord whose petitions ride a dialogue).
    Shared by `lapsing_petitions` and `petition_on_the_desk`."""
    ctx = (dialogue or {}).get("context") or {}
    terms = ctx.get("proposal") or {}
    if not isinstance(terms, dict):
        terms = {}
    vassal = str(terms.get("proposer_nation") or ctx.get("source_nation")
                 or (dialogue or {}).get("target_nation") or "")
    lord = str(terms.get("target_nation")
               or getattr(world, "player_nation", "France"))
    return (vassal, lord)


def petition_on_the_desk(world, vassal_name: str, lord: Optional[str] = None) -> bool:
    """IQ-7 review pass 2 (P4-2): True while a client petition FROM this
    vassal is on the dialogue manager — current or queued — i.e. asked and
    not yet answered. `lord`, when given, must be the petition's lord too.
    Pure; reads the manager, never the row (the `petitioned_turn` stamp
    outlives the answer)."""
    dm = getattr(world, "dialogue_manager", None)
    if dm is None:
        return False
    on_the_desk = [dm.peek(), *dm.iter_queue()]   # the current one AND the queue
    for dialogue in on_the_desk:
        if not (isinstance(dialogue, dict) and is_client_petition(dialogue)):
            continue
        vassal, petition_lord = _petition_dialogue_parties(world, dialogue)
        if vassal == vassal_name and (lord is None or petition_lord == lord):
            return True
    return False


def petition_standing_keys(world, vassal_name: str) -> dict:
    """Display-only keys for the Vassals tab (GR6 — nothing reads them
    back): the remission, the standing to petition, the turns until the next
    petition may be asked, and the bond the relation term is worth. The
    relation term was shown nowhere before IQ-7.

    IQ-7 review R7: `standing` reads "may petition" ONLY when every gate
    (a)–(g) passes at the next advance — otherwise the blocking reason, in
    `_GATE_COPY`'s vocabulary, with `standing_key` as the machine key the
    renderer branches on; `next_petition_in` counts END TURNS through the
    same gate (a relief remission of r is r+1, never r). "Standing" means
    ONE thing on the card — the standing to petition (loyalty ≥ 60); the
    relation term is the BOND. Empty on a world where petitions are not
    live (the lever down, or the School of War) — the card then carries no
    petition keys at all, so it cannot forecast what the producer will
    never issue ([36]).

    Pass 2 (P4-2): while this client's petition is ON THE DESK (current or
    queued on the dialogue manager, `petition_on_the_desk`) `standing` reads
    "petition on the desk" with `standing_key: "pending"` — the cadence it
    stamped at issue is true of the NEXT ask and read, beside an unanswered
    one in Envoys, as "8 turns until it may ask". `next_petition_in` keeps
    the gate's count (the next ask); the renderer draws every non-"may
    petition" standing amber, so the client needs no change."""
    if not petitions_live(world):
        return {}
    row = (getattr(world, "vassals", {}) or {}).get(vassal_name) or {}
    lord = str(row.get("lord") or "")
    turn = int(getattr(world, "current_turn", 0) or 0)
    relation = _lord_relation(world, vassal_name, lord) if lord else 0
    modifier = _standing(relation)
    remission = int(row.get("remission_left", 0) or 0)
    key, turns, _terms = _petition_gate(world, lord, vassal_name, turn=turn,
                                        projected=True)
    if lord and petition_on_the_desk(world, vassal_name, lord):
        key = "pending"
    if modifier > 0:
        honoured = relation // PETITION_RELATION_STEP
        bond = (f"{modifier:+d}/turn — a bond worth {_number_word(honoured)} "
                f"honoured petition{'s' if honoured != 1 else ''} "
                f"(bond {relation})")
    elif modifier < 0:
        bond = f"{modifier:+d}/turn — bond spent ({relation})"
    else:
        bond = "no bond yet — each petition honoured is worth +1/turn"
    return {
        "remission_left": int(remission),
        "standing": _gate_copy(key, turns, remission),
        "standing_key": str(key),
        "next_petition_in": int(turns),
        "bond": bond,
        "relation": int(relation),
        "relation_modifier": int(modifier),
    }


def _log_petition_answer(world, *, vassal_name: str, lord: str, subject: str,
                         region: str, outcome: str, penalty: bool,
                         loyalty_before: int, loyalty_after: int,
                         relation_before: int, relation_after: int) -> None:
    if not hasattr(world, "log_event"):
        return
    world.log_event({
        "type": "client_petition_answered",
        "vassal": vassal_name,
        "lord": lord,
        "subject": subject,
        "region": region or None,
        "outcome": outcome,
        "penalty": bool(penalty),
        "loyalty_before": int(loyalty_before),
        "loyalty_after": int(loyalty_after),
        "relation_before": int(relation_before),
        "relation_after": int(relation_after),
    })


def _bond_line(relation_before: int, relation_after: int) -> str:
    return (f"bond {relation_before} → {relation_after} "
            f"({_standing(relation_after):+d} a turn)")


def _honour_fulfilled(world, vassal_name: str, lord: str, petition: dict,
                      how: str) -> dict:
    """R1's outcome `fulfilled`, applied ONCE whichever answer reaches it
    (Grant, Refuse or the lapse — each consumes the dialogue): the capped
    bond step, no DP (the cede paid its own), no second loyalty gain (the
    cede paid that too), logged once with its own one-liner arm — never a
    refusal."""
    petition = petition or {}
    row = world.vassals[vassal_name]
    region = str(petition.get("region") or "")
    relation_before = _lord_relation(world, vassal_name, lord)
    step = _bond_step(relation_before)
    loyalty = int(row.get("loyalty", 0) or 0)
    if step > 0:
        world.modify_nation_relation(vassal_name, lord, step)
    relation_after = _lord_relation(world, vassal_name, lord)
    vd = _court_name(world, vassal_name, article=True)
    message = (f"{region} has already passed to {vd} by our own hand — the "
               f"petition is honoured: {_bond_line(relation_before, relation_after)}. "
               f"Nothing more is charged.")
    _log_petition_answer(
        world, vassal_name=vassal_name, lord=lord, subject="province",
        region=region, outcome="fulfilled", penalty=False,
        loyalty_before=loyalty, loyalty_after=loyalty,
        relation_before=relation_before, relation_after=relation_after)
    return {
        "success": True,
        "outcome": "fulfilled",
        "fulfilled": True,
        "penalty": False,
        "how": how,
        "subject": "province",
        "region": region or None,
        "loyalty_gain": 0,
        "loyalty_before": int(loyalty),
        "loyalty_after": int(loyalty),
        "relation_before": int(relation_before),
        "relation_after": int(relation_after),
        "relation_step": int(step),
        "dp_charged": 0,
        "remission_left": int(row.get("remission_left", 0) or 0),
        "remitted_price": 0,
        "message": message,
    }


def grant_petition(world, vassal_name: str, lord: str, petition: dict) -> dict:
    """Honour a client's petition. Re-validates at ANSWER time through
    `_grant_verdict` — the row still exists, it still answers to `lord`,
    THE DEED first (R1: a province already ceded by the lord's own verb
    FULFILS the petition — the capped bond step, no DP, no second gain),
    the fixed subject, the lord can pay. Outcomes: `granted`, `fulfilled`,
    `withdrawn` (a cause outside the lord's hands — nothing charged, no
    penalty) or `stands` (R2: the lord cannot pay, or gave the province
    elsewhere himself — nothing charged, nothing consumed; the petition
    stands until the turn ends and lapses at the quoted price).

    THE PROVINCE: `grant_region_to_vassal`, unchanged — it charges its own
    DP, applies its own worth-scaled gain and records `granted_regions` (a
    WAR rebellion reclaims it). THE RELIEF: 1 DP, loyalty +PETITION_RELIEF_
    LOYALTY blunted like invest, `remission_left = REMISSION_COLLECTIONS`.
    Both: the relation rises by the capped bond step. The result's
    `loyalty_gain` and message carry the REALISED delta (`after − before`,
    R4 — never the raw constant), and a province's message names the R5
    parts from the same dict the quote was built from. GR5: keyed on the
    row's lord, so an AI lord grants through this same function.
    """
    petition = petition or {}
    kind, verdict_message = _grant_verdict(world, lord, vassal_name, petition)
    if kind == "withdrawn":
        return _withdrawn(verdict_message)
    if kind == "stands":
        return _stands(verdict_message)
    if kind == "fulfilled":
        return _honour_fulfilled(world, vassal_name, lord, petition, how="granted")

    row = world.vassals[vassal_name]
    subject = str(petition.get("subject") or "")
    region = str(petition.get("region") or "")
    vd = _court_name(world, vassal_name, article=True)
    vd_cap = _court_name(world, vassal_name, article=True, capitalize=True)
    priced = _price_petition(world, lord, vassal_name,
                             {"subject": subject, "region": region})
    relation_before = _lord_relation(world, vassal_name, lord)
    step = _bond_step(relation_before)
    loyalty_before = int(row.get("loyalty", 0) or 0)
    remitted_price = 0
    if subject == "province":
        result = grant_region_to_vassal(world, vassal_name, region, actor=lord)
        if not result.get("success"):
            message = str(result.get("message")
                          or "The province could not be ceded")
            if THE_LORD_PAYS_TO_GRANT:
                return _stands(f"{message.rstrip('.')} — the petition stands until "
                               f"the turn ends, and a lapse is a refusal.")
            return _withdrawn(f"{message.rstrip('.')} — the petition is withdrawn.")
        dp_charged = int(GRANT_DP_COST)
    else:
        tribute_now = int(vassal_tribute_owed(world, vassal_name))
        charge = _charge_dp(world, lord, PETITION_DP_COST)
        if not charge["ok"]:
            ld_cap = _court_name(world, lord, article=True, capitalize=True)
            if THE_LORD_PAYS_TO_GRANT:
                return _stands(f"{ld_cap} cannot spare the diplomatic point — the "
                               f"petition stands until the turn ends; keep "
                               f"{PETITION_DP_COST} DP to grant it, or refuse it.")
            return _withdrawn(f"{ld_cap} cannot spare the diplomatic point — the "
                              f"petition is withdrawn.")
        # GE-3: × the Congress's stakes — the figure `_price_petition` quoted.
        gain_raw = int(_relief_gain_raw(world, lord))
        row["loyalty"] = int(min(LOYALTY_MAX, loyalty_before + gain_raw))
        row["remission_left"] = int(REMISSION_COLLECTIONS)
        remitted_price = int(tribute_now * REMISSION_COLLECTIONS)
        dp_charged = int(PETITION_DP_COST)
    if step > 0:
        world.modify_nation_relation(vassal_name, lord, step)
    relation_after = _lord_relation(world, vassal_name, lord)
    loyalty_after = int(row.get("loyalty", 0) or 0)
    gain = int(loyalty_after - loyalty_before)
    bond_line = _bond_line(relation_before, relation_after)
    loyalty_line = f"Loyalty +{gain} ({loyalty_before} → {loyalty_after})"
    if gain <= 0 and loyalty_before >= LOYALTY_MAX:
        loyalty_line = f"Loyalty +0 ({loyalty_before} → {loyalty_after}, already full)"
    if subject == "province":
        message = (f"{region} is ceded to {vd}. {loyalty_line}; {bond_line}. "
                   f"Cost: {dp_charged} DP. "
                   f"{province_price_line(priced['price_parts'], vd)}")
    else:
        message = (f"{vd_cap}'s tribute is remitted for "
                   f"{REMISSION_COLLECTIONS} collections ({remitted_price}g "
                   f"forgone). {loyalty_line}; {bond_line}. Cost: {dp_charged} DP.")
    _log_petition_answer(
        world, vassal_name=vassal_name, lord=lord, subject=subject,
        region=region, outcome="granted", penalty=False,
        loyalty_before=loyalty_before, loyalty_after=loyalty_after,
        relation_before=relation_before, relation_after=relation_after)
    return {
        "success": True,
        "outcome": "granted",
        "fulfilled": False,
        "subject": subject,
        "region": region or None,
        "loyalty_gain": int(gain),
        "loyalty_before": int(loyalty_before),
        "loyalty_after": int(loyalty_after),
        "relation_before": int(relation_before),
        "relation_after": int(relation_after),
        "relation_step": int(step),
        "dp_charged": int(dp_charged),
        "remission_left": int(row.get("remission_left", 0) or 0),
        "remitted_price": int(remitted_price),
        "price_parts": priced.get("price_parts"),
        "message": message,
    }


def refuse_petition(world, vassal_name: str, lord: str, petition: dict,
                    how: str) -> dict:
    """Refuse a client's petition — `how` is "refused" (the lord said no) or
    "unanswered" (it lapsed). Loyalty −PETITION_REFUSAL_LOYALTY (never
    blunted) and the relation −PETITION_RELATION_STEP; a lapse with
    AN_UNANSWERED_PETITION_IS_REFUSED down logs and costs nothing.

    IQ-7 review R1: consults `petition_is_fulfilled` FIRST — a province the
    lord already ceded by his own verb is honoured (outcome `fulfilled`),
    never refused; and the price is waived (`withdrawn`) ONLY when the
    petitioned province became ungrantable outside the lord's hands — it fell
    in war, or (pass 2, P3-1) he still holds it but the WORLD voided the ask:
    the client lost the province that adjoined it (`_province_voided_by_the_
    world`, the same classification `_grant_verdict` applies to a Grant).
    A province he endowed on a marshal or gave to another client STAYS a
    refusal — that was his answer. The DP and the grant cooldown are never
    read here: a lord who spent his points has not been excused.

    NEVER touches `record_diplomatic_refusal`, `apply_rejection_cooldowns`
    or `record_schemer_peace_rejection`: a client's refused petition is not
    an AI-3 ladder refusal. A row that is gone, or answers to another lord
    now, is not penalised — the petition is moot.
    """
    if how not in ("refused", "unanswered"):
        raise ValueError(f"refuse_petition: how must be 'refused' or "
                         f"'unanswered', not {how!r}")
    petition = petition or {}
    row = (getattr(world, "vassals", {}) or {}).get(vassal_name)
    vd = _court_name(world, vassal_name, article=True)
    vd_cap = _court_name(world, vassal_name, article=True, capitalize=True)
    if not row or str(row.get("lord") or "") != lord:
        return _withdrawn(f"{vd_cap}'s petition is moot — it no longer answers "
                          f"to {_court_name(world, lord, article=True)}.")
    if petition_is_fulfilled(world, vassal_name, lord, petition):
        return _honour_fulfilled(world, vassal_name, lord, petition, how=how)
    subject = str(petition.get("subject") or "")
    region = str(petition.get("region") or "")
    if THE_DEED_HONOURS_THE_PETITION and subject == "province" and region:
        region_obj = (getattr(world, "regions", {}) or {}).get(region)
        controller = str(getattr(region_obj, "controller", "") or "") if region_obj else ""
        if region_obj is not None and controller == vassal_name:
            return _withdrawn(f"{vd_cap} already holds {region} — the petition is "
                              f"withdrawn; nothing is charged.")
        if region_obj is not None and controller != lord and \
                _province_lost_outside_the_lords_hands(world, lord, vassal_name, region):
            return _withdrawn(f"{region} can no longer be ceded to {vd} — it fell to "
                              f"another power; the petition is withdrawn and nothing "
                              f"is charged.")
        # P3-1 (pass 2): the lord still holds it, but the WORLD made it
        # ungrantable (the client lost the province that adjoined it) —
        # `_grant_verdict`'s own classification, mirrored: withdrawn free. An
        # estate the lord endowed stays a refusal — that was his answer.
        voided = _province_voided_by_the_world(world, lord, vassal_name, region)
        if voided:
            return _withdrawn(f"{voided} — the petition is withdrawn and nothing "
                              f"is charged.")
    penalty = not (how == "unanswered" and not AN_UNANSWERED_PETITION_IS_REFUSED)
    loyalty_before = int(row.get("loyalty", 0) or 0)
    relation_before = _lord_relation(world, vassal_name, lord)
    if penalty:
        # GE-3: × the Congress's stakes — the figure `_price_petition` and
        # `lapse_forecast` quoted (`_refusal_loyalty`, read live).
        row["loyalty"] = int(max(LOYALTY_MIN,
                                 loyalty_before - _refusal_loyalty(world, lord)))
        world.modify_nation_relation(vassal_name, lord, -PETITION_RELATION_STEP)
    loyalty_after = int(row.get("loyalty", 0) or 0)
    relation_after = _lord_relation(world, vassal_name, lord)
    ask = f"for {region}" if subject == "province" and region else "for relief"
    if not penalty:
        message = (f"{vd_cap}'s petition {ask} went unanswered and "
                   f"lapses; it costs nothing.")
    else:
        verb = ("went unanswered and lapses as a refusal"
                if how == "unanswered" else "is refused")
        message = (f"{vd_cap}'s petition {ask} {verb}: loyalty "
                   f"−{loyalty_before - loyalty_after} ({loyalty_before} → "
                   f"{loyalty_after}); {_bond_line(relation_before, relation_after)}. "
                   f"Nothing is charged.")
    _log_petition_answer(
        world, vassal_name=vassal_name, lord=lord, subject=subject,
        region=region, outcome=how, penalty=penalty,
        loyalty_before=loyalty_before, loyalty_after=loyalty_after,
        relation_before=relation_before, relation_after=relation_after)
    return {
        "success": True,
        "outcome": how,
        "fulfilled": False,
        "penalty": bool(penalty),
        "subject": subject,
        "region": region or None,
        "loyalty_before": int(loyalty_before),
        "loyalty_after": int(loyalty_after),
        "relation_before": int(relation_before),
        "relation_after": int(relation_after),
        "dp_charged": 0,
        "message": message,
    }


def lapse_forecast(world, vassal_name: str, lord: str, petition: dict) -> dict:
    """What `refuse_petition(how="unanswered")` WOULD do to this petition at
    the turn's end, without doing it — the priced line the end-turn gate,
    the rail notice and the lapse briefing quote (R8: a lapse is priced
    aloud). Keys: `outcome` in {"fulfilled", "withdrawn", "refused",
    "free"}, `penalised`, `loyalty_loss`, `bond_loss`, `price_line`."""
    petition = petition or {}
    row = (getattr(world, "vassals", {}) or {}).get(vassal_name)
    vd_cap = _court_name(world, vassal_name, article=True, capitalize=True)
    region = str(petition.get("region") or "")
    base = {"vassal": vassal_name, "court": _court_name(world, vassal_name),
            "court_the": _court_name(world, vassal_name, article=True),
            "loyalty_loss": 0, "bond_loss": 0, "penalised": False}
    if not row or str(row.get("lord") or "") != lord:
        return {**base, "outcome": "withdrawn",
                "price_line": f"{vd_cap}'s petition is moot — a lapse costs nothing."}
    if petition_is_fulfilled(world, vassal_name, lord, petition):
        return {**base, "outcome": "fulfilled",
                "price_line": f"{region} is already ceded — the lapse closes the "
                              f"petition as honoured; nothing is charged."}
    subject = str(petition.get("subject") or "")
    if THE_DEED_HONOURS_THE_PETITION and subject == "province" and region:
        region_obj = (getattr(world, "regions", {}) or {}).get(region)
        controller = str(getattr(region_obj, "controller", "") or "") if region_obj else ""
        if region_obj is not None and (
                controller == vassal_name
                or (controller != lord
                    and _province_lost_outside_the_lords_hands(world, lord, vassal_name, region))):
            return {**base, "outcome": "withdrawn",
                    "price_line": f"{region} is no longer ours to cede — a lapse "
                                  f"withdraws the petition; nothing is charged."}
        # P3-1 (pass 2): still ours, but voided by the world (contiguity) —
        # the same read `refuse_petition` makes, so forecast == applied.
        voided = _province_voided_by_the_world(world, lord, vassal_name, region)
        if voided:
            return {**base, "outcome": "withdrawn",
                    "price_line": f"{voided} — a lapse withdraws the petition; "
                                  f"nothing is charged."}
    if not AN_UNANSWERED_PETITION_IS_REFUSED:
        return {**base, "outcome": "free",
                "price_line": f"{vd_cap}'s petition lapses free; it waits "
                              f"{PETITION_INTERVAL_TURNS} turns before asking again."}
    loyalty = int(row.get("loyalty", 0) or 0)
    relation = _lord_relation(world, vassal_name, lord)
    # GE-3: × the Congress's stakes — the same `_refusal_loyalty` the lapse
    # charges through `refuse_petition` (forecast == applied).
    loyalty_loss = loyalty - max(LOYALTY_MIN, loyalty - _refusal_loyalty(world, lord))
    bond_loss = relation - max(_RELATION_FLOOR, relation - PETITION_RELATION_STEP)
    stakes = _petition_stakes(world, lord)
    raised = (f"; the loyalty stakes are ×{stakes} while the Congress of "
              f"Paris sits" if stakes > 1 else "")
    return {**base, "outcome": "refused", "penalised": True,
            "loyalty_loss": int(loyalty_loss), "bond_loss": int(bond_loss),
            "price_line": (f"{vd_cap} — −{loyalty_loss} loyalty / −{bond_loss} bond "
                           f"(a lapse is a refusal{raised})")}


def client_petition_notice(sender: str, petition: dict) -> tuple:
    """The rail row a client petition raises on arrival — (title, body).
    IQ-7 review R8(a): the rail is the ONE surface every player sees on
    arrival, so it states the rule and the price the lapse applies, from the
    petition's own terms (the SAME figures `refuse_petition` charges), gated
    on the lever so the lever-down copy stays honest ("costs nothing")."""
    from backend.display_names import with_definite_article
    petition = petition if isinstance(petition, dict) else {}
    dp = int(petition.get("dp_cost", 1) or 1)
    if bool(petition.get("lapse_counts_as_refusal", AN_UNANSWERED_PETITION_IS_REFUSED)):
        loy = int(petition.get("refusal_loyalty", 10) or 10)
        rel = int(petition.get("relation_refusal_step", 20) or 20)
        stakes = int(petition.get("loyalty_stakes", 1) or 1)
        raised = (f" (×{stakes} while the Congress of Paris sits)" if stakes > 1 else "")
        lapse = (f"Left unanswered it counts as a refusal: −{loy} "
                 f"loyalty{raised}, −{rel} bond.")
    else:
        lapse = (str(petition.get("lapse_line") or "").strip()
                 or "Left unanswered it lapses at the end of the turn.")
    who = with_definite_article(sender)
    return (f"Petition from {who}",
            f"An envoy from {who} has arrived with a petition. Grant it (keep "
            f"{dp} DP in hand), or refuse it — it lapses at the end of the "
            f"turn. {lapse}")


def restate_petition_notices(world, lord: str) -> int:
    """GE-3 review #37: re-state every desk petition's rail row at its LIVE
    stakes — the summons doubles the lapse's loyalty cost and the
    dissolution halves it, and the row had kept the figure it was issued
    with (the end-turn gate, reading `lapse_forecast`, contradicted it).
    Mutates the standing row in place (its id, so no second bell). Returns
    the rows re-stated."""
    dm = getattr(world, "dialogue_manager", None)
    collector = getattr(world, "notifications", None)
    if dm is None or collector is None:
        return 0
    from backend.game_logic.formations import formed_display_name
    restated = 0
    for d in [dm.peek()] + list(dm.iter_queue()):
        if not isinstance(d, dict) or not is_client_petition(d):
            continue
        vassal, petition_lord = _petition_dialogue_parties(world, d)
        if not vassal or petition_lord != lord:
            continue
        terms = (d.get("context") or {}).get("proposal") or {}
        petition = terms.get("petition") if isinstance(terms, dict) else None
        if not isinstance(petition, dict):
            continue
        live = dict(petition)
        live["refusal_loyalty"] = int(_refusal_loyalty(world, lord))
        live["loyalty_stakes"] = int(_petition_stakes(world, lord))
        title, body = client_petition_notice(formed_display_name(world, vassal), live)
        for row in collector.get_pending():
            if row.get("type") == "diplomatic_proposal" and (
                    row.get("base_title") or row.get("title")) == title:
                row["message"] = body
                restated += 1
    return restated


def lapsing_petitions(world, lord: str) -> List[dict]:
    """Every pending petition to `lord` — current or queued on the dialogue
    manager — that would lapse at this turn's end, each with its priced
    line (`lapse_forecast`): `{vassal, court, court_the, price_line,
    outcome, penalised, loyalty_loss, bond_loss, dialogue_id}`. Read by the
    end-turn gate so it can name them ("1 petition will be REFUSED if you
    end the turn: Switzerland, −10 loyalty / −20 bond"). Pure."""
    dm = getattr(world, "dialogue_manager", None)
    if dm is None:
        return []
    out: List[dict] = []
    for d in [dm.peek()] + list(dm.iter_queue()):
        if not isinstance(d, dict) or not is_client_petition(d):
            continue
        vassal, petition_lord = _petition_dialogue_parties(world, d)
        if not vassal or petition_lord != lord:
            continue
        terms = (d.get("context") or {}).get("proposal") or {}
        if not isinstance(terms, dict):
            terms = {}
        petition = terms.get("petition") if isinstance(terms.get("petition"), dict) else {}
        entry = lapse_forecast(world, vassal, lord, petition)
        entry["dialogue_id"] = d.get("dialogue_id")
        out.append(entry)
    return out


def process_vassal_petitions(world) -> List[dict]:
    """The producer — runs once per turn between process_vassal_loyalty and
    check_vassal_rebellion. Walks `sorted(world.vassals)`, whatever the lord,
    and issues at most ONE petition per lord per turn.

    Eligibility (all must hold — `_petition_gate`, the ONE gate the Vassals
    card also reads): (a) loyal (>= PETITION_LOYAL_MIN); (b) past the grace
    since `created_turn`; (c) past the per-vassal cadence since
    `petitioned_turn`; (d) no province of the client's disrupted; (e) the
    lord can pay PETITION_DP_COST, read without charging; (f) no remission
    standing; (g) the ladder finds a subject. Then the cadence is stamped —
    whatever the answer — and the petition goes out: through the incoming-
    proposal transport for the player lord, resolved in place for an AI lord
    (GR5 — grant when payable, unless the province lies in the lord's OWN
    active acquire design; otherwise refuse, at the same prices). Returns
    `client_petition_answered` event dicts for the AI resolutions; the
    player's answers log from the executor. Dormant on the School of War
    (`petitions_live`, [36]).
    """
    if not petitions_live(world):
        return []
    vassals = getattr(world, "vassals", None) or {}
    if not vassals:
        return []
    events: List[dict] = []
    turn = int(getattr(world, "current_turn", 0) or 0)
    disrupted = world.get_disrupted_regions()
    asked_lords: set = set()

    for vassal_name in sorted(vassals):
        row = vassals.get(vassal_name)
        if not row:
            continue
        lord = str(row.get("lord") or "")
        if not lord or lord in asked_lords:
            continue
        key, _turns, terms = _petition_gate(world, lord, vassal_name, turn=turn,
                                            projected=False, disrupted=disrupted)
        if key != "eligible" or terms is None:
            continue

        asked_lords.add(lord)
        event = _issue_petition(world, vassal_name, lord, terms)
        if event is not None:
            events.append(event)
    return events


def _issue_petition(world, vassal_name: str, lord: str, terms: dict) -> Optional[dict]:
    """The producer's issuing block — ONE road for a petition to go out,
    shared by `process_vassal_petitions` (the end turn) and
    `present_pending_asks` (the Congress's summons, GE-3). The cadence is
    stamped whatever the answer; the player lord receives it through the
    incoming-proposal transport (returns None — the executor logs the
    answer); an AI lord answers in place (GR5 — grant when payable, unless
    the province lies in the lord's OWN active acquire design; otherwise
    refuse, at the same prices) and the `client_petition_answered` event
    dict is returned."""
    row = world.vassals[vassal_name]
    turn = int(getattr(world, "current_turn", 0) or 0)
    player = getattr(world, 'player_nation', 'France')
    row["petitioned_turn"] = int(turn)

    if lord == player:
        from backend.game_logic.ai_diplomacy import deliver_ai_proposal
        deliver_ai_proposal({
            "source": vassal_name,
            "recipient": lord,
            "proposal_type": CLIENT_PETITION_TYPE,
            "terms": {
                "type": CLIENT_PETITION_TYPE,
                "proposer_nation": vassal_name,
                "target_nation": lord,
                "demands": [],
                "sweeteners": [],
                "petition": terms,
            },
            "talleyrand_assessment": (
                f"{terms['grant_line']} {terms['refuse_line']}"),
            "decision_reason": "client_petition",
            "_force_send": True,
        }, world)
        return None

    # GR5 — an AI lord answers in place: no dialogue, notification or
    # mailbox. It grants what it can pay for, unless the province lies
    # in its own active acquire design.
    grant = True
    if terms["subject"] == "province":
        from backend.game_logic.agendas import get_active_agenda
        view = get_active_agenda(lord, world)
        if (view is not None and not view.survival
                and view.type == "acquire_regions"
                and terms["region"] in set(view.regions)):
            grant = False
    if grant:
        result = grant_petition(world, vassal_name, lord, terms)
        # An AI lord has no turn to let a petition STAND through (R2's
        # outcome for a lord who cannot make good on a Grant); GR5
        # maps it to the refusal at the same price the player would pay.
        if str(result.get("outcome") or "") == "stands":
            result = refuse_petition(world, vassal_name, lord, terms,
                                     how="refused")
    else:
        result = refuse_petition(world, vassal_name, lord, terms,
                                 how="refused")
    return {
        "type": "client_petition_answered",
        "vassal": vassal_name,
        "lord": lord,
        # `nation` keys the dispatch relevance filter — the lord's.
        "nation": lord,
        "subject": terms["subject"],
        "region": terms.get("region"),
        "outcome": str(result.get("outcome") or ""),
        "message": str(result.get("message") or ""),
    }


def present_pending_asks(world, lord: str) -> List[str]:
    """GE-3 §2.3 — "every satellite with a pending ask presents it" at the
    summons of the Congress of Paris. Returns the vassals that presented a
    petition NOW (sorted), for the summons' own report.

    For every satellite of `lord`, in `sorted(world.vassals)` order: the
    IQ-7 gate (`_petition_gate`) with `waive_timing=True`, and each eligible
    ask goes out through the producer's own issuing block
    (`_issue_petition`), which stamps `petitioned_turn` — so the end-turn
    producer skips these clients by cadence and nobody is asked twice.

    Deliberate waivers, recorded:
    - the TIMED gates (b) grace and (c) cadence: the summons is the moment
      the bills come due, whatever each client's clock says;
    - the producer's ONE-PETITION-PER-LORD rule: at the summons every
      client with an ask presents it at once — that is the bill, and it is
      the player's own act that calls them in;
    - gate (e), the lord can pay the DP. `congress.summon` presents the
      bills BEFORE the executor charges the summons' 2 DP, so the live read
      would be of a purse the summons is about to spend; and with the
      one-per-lord rule waived a per-client read of one purse proves
      nothing (N asks, one DP). THE_LORD_PAYS_TO_GRANT already makes a
      DP-short Grant STAND (nothing charged, nothing consumed) rather than
      withdraw, and a refusal costs no DP — so every ask presented has an
      answer with a stated price. The summons is the Emperor's choice of
      moment; keeping DP in hand for the bills is part of the preparation.
    A client whose petition is already ON THE DESK (issued at the last end
    turn, unanswered) is not asked again. (f) a standing remission, (a) the
    standing to petition, (d) a disrupted province and (g) a subject all
    hold. Dormant where petitions are not live (the lever, the School).
    """
    if not petitions_live(world):
        return []
    vassals = getattr(world, "vassals", None) or {}
    if not vassals or not lord:
        return []
    turn = int(getattr(world, "current_turn", 0) or 0)
    disrupted = world.get_disrupted_regions()
    presented: List[str] = []
    for vassal_name in sorted(vassals):
        row = vassals.get(vassal_name)
        if not row or str(row.get("lord") or "") != lord:
            continue
        if petition_on_the_desk(world, vassal_name, lord):
            continue
        key, _turns, terms = _petition_gate(world, lord, vassal_name, turn=turn,
                                            projected=False, disrupted=disrupted,
                                            waive_timing=True)
        if key != "eligible" or terms is None:
            continue
        _issue_petition(world, vassal_name, lord, terms)
        presented.append(vassal_name)
    return presented


# ─── IQ-7 R3: the Garrison option, in one voice ────────────────────────────

_GARRISON_AP_COST = 2
_GARRISON_LOYALTY = 10


def garrison_option_copy(world, vassal_name: str, lord: Optional[str] = None) -> str:
    """IQ-7 R3 (+ review [21]): what `garrison_vassal_rebellion` DOES — 2 AP,
    +10 loyalty once, NO corps moves. The standing +2/turn (VP-D1) comes only
    from a corps actually standing in the capital, so the sentence branches
    on whether one already does (Massena stands in Milan at boot — "station
    one" would be false there). The no-corps arm is the T17-pinned string."""
    row = (getattr(world, "vassals", {}) or {}).get(vassal_name) or {}
    lord = lord or str(row.get("lord") or "")
    capital = world.get_nation_capital(vassal_name) or "their capital"
    if capital != "their capital" and lord and lord_garrison_present(world, lord, capital):
        return (f"{_GARRISON_AP_COST} AP → Loyalty +{_GARRISON_LOYALTY} now. No corps "
                f"moves: our corps already standing in {capital} adds "
                f"+{GARRISON_LOYALTY_BONUS} every turn.")
    return (f"{_GARRISON_AP_COST} AP → Loyalty +{_GARRISON_LOYALTY} now. No corps moves: "
            f"a corps standing in {capital} adds +{GARRISON_LOYALTY_BONUS} every turn.")


def garrison_result_line(world, vassal_name: str, loyalty_before: int,
                         loyalty_after: int, ap_spent: int = _GARRISON_AP_COST,
                         lord: Optional[str] = None) -> str:
    """The handler's sentence after the press, built from the REAL charge
    and the REAL loyalty change, naming what did and did not happen — the
    old "Imperial garrison deployed to X" promised a corps that never moved
    ([21]). Branches on `lord_garrison_present` like the option copy."""
    row = (getattr(world, "vassals", {}) or {}).get(vassal_name) or {}
    lord = lord or str(row.get("lord") or "")
    vd_cap = _court_name(world, vassal_name, article=True, capitalize=True)
    capital = world.get_nation_capital(vassal_name) or "their capital"
    head = (f"{vd_cap} shown the flag: loyalty {int(loyalty_before)} → "
            f"{int(loyalty_after)} ({int(ap_spent)} AP spent).")
    if capital != "their capital" and lord and lord_garrison_present(world, lord, capital):
        return (f"{head} No corps moves — our corps already standing in {capital} "
                f"adds +{GARRISON_LOYALTY_BONUS} a turn.")
    return (f"{head} No corps moves — station one in {capital} for "
            f"+{GARRISON_LOYALTY_BONUS} a turn.")


def garrison_refusal_line(world, vassal_name: str, ap_available: int,
                          ap_cost: int = _GARRISON_AP_COST) -> str:
    """The <2 AP refusal, in the same voice as the option it refuses."""
    vd = _court_name(world, vassal_name, article=True)
    return (f"Showing the flag in {vd} costs {int(ap_cost)} AP — you have "
            f"{int(ap_available)}. No corps moves either way.")


# ═══════════════════════════════════════════════════════
# VASSAL TRANSFER (VS-5)
# ═══════════════════════════════════════════════════════

# VS-5 (VASSAL_DEEPENING_SPEC §6): a transferred vassal is not instantly
# loyal to its new master — reset between conquest (20) and treaty (60).
TRANSFER_LOYALTY_RESET = 30


def transfer_vassal(world, vassal_name: str, to_lord: str,
                    reason: str = "vassal_transfer") -> dict:
    """VS-5: change a vassal's LORD (peace-table re-homing; also VS-6's
    "become someone else's vassal" outcome). Unlike create/release this
    mutates the existing row directly — the vassal never passes through
    independence (no release cooldown, no rebellion path).

    Bookkeeping:
    - lord re-key + UNCONDITIONAL loyalty reset to TRANSFER_LOYALTY_RESET
      (a loyalty-0 vassal must not instantly rebel against a lord who never
      wronged it; a loyalty-90 one is not instantly devoted either);
    - assimilated marshals re-keyed to the new lord (original_nation kept so
      a future rebellion still returns them to the vassal);
    - VS-3 granted_regions CLEARED (the new lord never granted them — stale
      provenance would let a Franco-granted province "reclaim" to Britain);
    - old pair VASSAL→PEACE, new pair →VASSAL, then the R48 reconcile runs
      for the new lord; rebellion popups/dialogues for this vassal cleared;
    - Continental System membership dropped when leaving the player's web;
    - autonomy level and tribute_rate carry over unchanged.

    Callers must settle any WAR between vassal and to_lord FIRST (the
    settlement_ratify handler closes the pair via cleanup_war_end before
    calling). GR5 lord-neutral by construction.
    """
    # R4-5 (R7, September 18, 2026): display names with their articles in
    # every sentence this function returns.
    client_cap = _court_name(world, vassal_name, article=True, capitalize=True)
    if vassal_name not in getattr(world, 'vassals', {}):
        return {"success": False, "message": f"{client_cap} is not a vassal."}
    state = world.vassals[vassal_name]
    from_lord = state.get("lord", "")
    if not to_lord or to_lord == vassal_name:
        return {"success": False, "message": "Invalid receiving lord."}
    if to_lord == from_lord:
        return {"success": False,
                "message": (f"{client_cap} already serves "
                            f"{_court_name(world, to_lord, article=True)}.")}

    # Re-key the assimilated contingent to the new lord (VS-4's gates and
    # the rebellion transfer-back both key off original_nation, which stays).
    rekeyed = []
    for marshal in list(world.marshals.values()):
        if (getattr(marshal, 'original_nation', None) == vassal_name
                and getattr(marshal, 'nation', '') == from_lord):
            marshal.nation = to_lord
            if hasattr(marshal, 'trust') and hasattr(marshal.trust, 'value'):
                marshal.trust.modify(ASSIMILATION_TRUST - marshal.trust.value)
            marshal.relationship_with_lord = "Professional"
            rekeyed.append(marshal.name)

    old_loyalty = int(state.get("loyalty", 0))
    state["lord"] = to_lord
    state["loyalty"] = int(TRANSFER_LOYALTY_RESET)
    state.pop("granted_regions", None)   # VS-3 interlock
    state.pop("grant_cooldown", None)
    if THE_TRANSFER_SHEDS_THE_REMISSION:
        # IQ-7 review R3 ([02]/[27]/[32]): a relief remission is the OLD
        # lord's purchase (its loyalty and bond went to him; the transfer
        # resets the one and leaves the other on the old pair) — the new lord
        # never granted it and collects in full from his next collection.
        # The cadence stamp is the old court's too. The collection itself
        # stays keyed on the row's data (a stored remission is still honoured
        # with the lever down); only the POP is levered.
        state.pop("remission_left", None)
        state.pop("petitioned_turn", None)
    world.invalidate_active_nations_cache()

    # Diplomatic states: old pair loses VASSAL; new pair gains it.
    from backend.game_logic.diplomacy import set_diplomatic_state
    if from_lord:
        set_diplomatic_state(world, from_lord, vassal_name, "PEACE", reason)
    set_diplomatic_state(world, to_lord, vassal_name, "VASSAL", reason)
    _reconcile_vassal_diplomacy(world, to_lord, vassal_name)

    # Clear stale rebellion popups/dialogues (mirrors release_vassal) —
    # FA-S17-6: one helper, shared with every rebellion exit.
    _retire_rebellion_question(world, vassal_name)

    # R50 mirror: leaving the player's web leaves the Continental System.
    if from_lord == getattr(world, 'player_nation', 'France'):
        cs_members = getattr(world, 'continental_system_members', [])
        if isinstance(cs_members, set):
            cs_members.discard(vassal_name)
        elif isinstance(cs_members, list) and vassal_name in cs_members:
            cs_members.remove(vassal_name)

    if hasattr(world, "log_event"):
        world.log_event({
            "type": "vassal_transferred",
            "vassal": vassal_name,
            "from_lord": from_lord,
            "to_lord": to_lord,
            "loyalty_before": old_loyalty,
            "loyalty_after": int(TRANSFER_LOYALTY_RESET),
        })
    from backend.game_logic.dispatch import queue_dispatch_event
    queue_dispatch_event(
        world, "diplomatic_vassal_transferred",
        {"vassal": vassal_name, "from_lord": from_lord, "to_lord": to_lord,
         "nation": from_lord},
        "always",
    )

    return {
        "success": True,
        "message": (
            f"{client_cap} passes from "
            f"{_court_name(world, from_lord, article=True)}'s suzerainty to "
            f"{_court_name(world, to_lord, article=True)}'s "
            f"(loyalty resets to {TRANSFER_LOYALTY_RESET})."
        ),
        "from_lord": from_lord,
        "to_lord": to_lord,
        "rekeyed_marshals": rekeyed,
        "loyalty_after": int(TRANSFER_LOYALTY_RESET),
    }


# ═══════════════════════════════════════════════════════
# MARSHAL ASSIMILATION (EC-K.1)
# ═══════════════════════════════════════════════════════

def assimilate_vassal_marshals(world, vassal_name: str) -> List[str]:
    """
    Add vassal nation's marshals to the lord's control.

    PUPPET/SATELLITE: marshals become lord-controlled with trust=40.
    AUTONOMOUS: marshals stay AI-controlled (no assimilation).

    Sets marshal.original_nation for rebellion transfer-back.

    Returns list of assimilated marshal names.
    """
    if vassal_name not in world.vassals:
        return []

    state = world.vassals[vassal_name]
    lord = state["lord"]
    autonomy = state.get("autonomy", AUTONOMY_SATELLITE)

    # AUTONOMOUS vassals keep their own marshals
    if autonomy == AUTONOMY_AUTONOMOUS:
        return []

    assimilated = []
    for marshal in list(world.marshals.values()):
        if getattr(marshal, 'nation', '') == vassal_name:
            # Record original nation for rebellion transfer-back
            marshal.original_nation = vassal_name
            # Transfer to lord
            marshal.nation = lord
            # Set trust to assimilation level
            if hasattr(marshal, 'trust') and hasattr(marshal.trust, 'value'):
                marshal.trust.modify(ASSIMILATION_TRUST - marshal.trust.value)
            # Set Professional relationship baseline
            marshal.relationship_with_lord = "Professional"
            assimilated.append(marshal.name)

    return assimilated


# ═══════════════════════════════════════════════════════
# VASSAL WARNINGS
# ═══════════════════════════════════════════════════════

def get_vassal_warnings(world) -> List[dict]:
    """
    Get vassal loyalty warnings.

    <40: warning
    <20: urgent
    <10: critical notification
    """
    warnings = []
    for vassal_name, state in world.vassals.items():
        loyalty = state["loyalty"]
        if loyalty < 10:
            warnings.append({
                "vassal": vassal_name,
                "loyalty": int(loyalty),
                "level": "critical",
                "message": f"{vassal_name} CRITICAL: Loyalty at {int(loyalty)}! Rebellion imminent!",
            })
        elif loyalty < 20:
            warnings.append({
                "vassal": vassal_name,
                "loyalty": int(loyalty),
                "level": "urgent",
                "message": f"{vassal_name}: Loyalty dangerously low ({int(loyalty)}). Invest or face rebellion.",
            })
        elif loyalty < 40:
            warnings.append({
                "vassal": vassal_name,
                "loyalty": int(loyalty),
                "level": "warning",
                "message": f"{vassal_name}: Loyalty declining ({int(loyalty)}). Consider intervention.",
            })

    return warnings


# ═══════════════════════════════════════════════════════
# RELEASE VASSAL
# ═══════════════════════════════════════════════════════

# R14: turns a released vassal cannot be re-vassalized (treaty or conquest).
RELEASE_COOLDOWN_TURNS = 5


def _release_tribute_snapshot(world, vassal_name: str, state: dict) -> int:
    """Gross tribute per turn the lord is about to stop collecting.

    Mirrors the STRATEGIC LEDGER's derivation (`ledger.py` vassal_tribute):
    cached region index, effective income, EC-W1 disruption skip. Deliberately
    NOT `process_vassal_tribute`'s figure, which additionally caps by the
    vassal's own purse — a gold-poor turn would understate what the player is
    giving up permanently.
    """
    try:
        rate = float(state.get("tribute_rate", 0.5))
        disrupted = world.get_disrupted_regions()
        income = sum(
            world.regions[name].get_effective_income()
            for name in world.get_nation_regions(vassal_name)
            if name not in disrupted
        )
        return int(income * rate)
    except Exception:
        return 0


def _build_release_report(
    world,
    vassal_name: str,
    lord: str,
    *,
    lost_tribute: int,
    released_marshals: list,
    was_continental_member: bool,
    threat_before: int,
    threat_after: int,
) -> str:
    """IGR-A4: what a voluntary release actually costs and buys.

    Before this the whole consequence chain was reported as
    "<X> has been released from vassalage." — including the fact that
    releasing Kingdom of Italy is exactly what un-blocks the `forms: Italy`
    watcher, i.e. the game performed its own most interesting causal link in
    silence. Every clause is CONDITIONAL: three of the shipped vassals field
    no marshals, the Continental System is empty at boot, and Switzerland has
    no agenda deck at all.
    """
    # R4-5 (R7, September 18, 2026): the court and its lord carry their
    # articles — measured on the typed `release kingdom of italy`: "Kingdom
    # of Italy is released from vassalage…".
    name = _court_name(world, vassal_name, article=True, capitalize=True)
    lord_name = _court_name(world, lord, article=True) if lord else ""
    parts = [f"{name} is released from vassalage and stands a free court again."]

    if lost_tribute > 0:
        parts.append(f"Their tribute of {lost_tribute} gold a turn ends.")
    if released_marshals:
        parts.append(
            f"Their marshals return to their own colours: "
            f"{', '.join(released_marshals)}."
        )
    if was_continental_member:
        parts.append("They are no longer bound to the Continental System.")

    # Forward-looking, and precisely true: release does NOT end their other
    # wars — it only ends the lord-vassal pair. What is lost is the call.
    parts.append(
        f"They will no longer answer {lord_name}'s call to arms."
        if lord else "They will no longer answer our call to arms."
    )

    if threat_after < threat_before:
        parts.append(
            f"Europe's alarm at {lord_name} eases "
            f"({threat_before} → {threat_after})."
        )

    parts.append(
        f"They cannot be brought back under the yoke for "
        f"{RELEASE_COOLDOWN_TURNS} turns."
    )

    # The woken deck — read AFTER the release, since get_active_agenda is
    # per-turn cached and short-circuits on vassalage. This is the line that
    # makes the "→ forms:" watcher legible.
    try:
        from backend.game_logic.agendas import get_active_agenda
        from backend.game_logic.formations import get_formation_watch
        agenda = get_active_agenda(vassal_name, world)
        if agenda is not None:
            parts.append(f"Freed, they take up a design of their own: {agenda.title}.")
            watch = get_formation_watch(world, vassal_name)
            if watch and not watch.get("blocked_by_vassalage"):
                parts.append(
                    f"Should they see it through they would proclaim "
                    f"{watch.get('forms')} — {watch.get('progress')}."
                )
    except Exception:
        pass

    return " ".join(parts)


def release_vassal(
    world,
    vassal_name: str,
    rebellion: bool = False,
    reduce_threat_on_release: bool = True,
) -> dict:
    """
    Release a vassal. Restores their marshals.

    If rebellion=True, this is a forced release from rebellion check.
    Otherwise it's a voluntary release.
    """
    # R4-5 (R7, September 18, 2026): measured on a SECOND typed `release
    # kingdom of italy` — "KingdomOfItaly is not a vassal."
    client_cap = _court_name(world, vassal_name, article=True, capitalize=True)
    if vassal_name not in world.vassals:
        return {"success": False, "message": f"{client_cap} is not a vassal."}

    state = world.vassals[vassal_name]
    lord = state["lord"]

    # IGR-A4: snapshot BEFORE the mutations below destroy the evidence.
    # `original_nation` is the only marker of an assimilated contingent and is
    # cleared to None four lines down (it used to be `delattr`'d — FA-S15-1,
    # which broke every save for the rest of the campaign, because `to_dict`
    # reads it bare); `world.vassals[...]` is deleted outright; and
    # Continental-System membership is discarded further on. The whole report
    # is assembled at the tail from these locals.
    released_marshals = sorted(
        m.name for m in world.marshals.values()
        if getattr(m, 'original_nation', None) == vassal_name
    )
    lost_tribute = _release_tribute_snapshot(world, vassal_name, state)
    was_continental_member = vassal_name in (
        getattr(world, 'continental_system_members', None) or [])
    threat_before = int(getattr(world, 'threat_by_target', {}).get(lord, 0)) if lord else 0

    # Restore marshals to vassal nation
    for marshal in list(world.marshals.values()):
        if getattr(marshal, 'original_nation', None) == vassal_name:
            marshal.nation = vassal_name
            # ⛔ FA-S15-1 (P1, found while building slice 15). This was
            # `delattr(marshal, 'original_nation')`, and `Marshal.to_dict`
            # reads `self.original_nation` BARE — so releasing a vassal that
            # had an assimilated contingent broke EVERY save and EVERY
            # autosave for the rest of the campaign, with the AttributeError
            # swallowed into a `success: False` nobody reads.
            #
            # It is IGR-X1's pattern exactly (`del marshal._recovery_destination`
            # in `enemy_ai.py`, fixed the same way), and the two sibling
            # restore loops in this very file already write `= None`. This one
            # site was missed. A `delattr` of a SERIALIZED field is never
            # safe; `test_serialization_enforcement.py` now forbids the shape.
            marshal.original_nation = None
            if hasattr(marshal, 'relationship_with_lord'):
                delattr(marshal, 'relationship_with_lord')

    # Remove vassal state
    del world.vassals[vassal_name]
    world.invalidate_active_nations_cache()

    # Clear stale popup/dialogue referencing this vassal
    if getattr(world, 'vassal_rebellion_imminent_popup', None):
        popup_vassal = world.vassal_rebellion_imminent_popup.get("nation", "")
        if popup_vassal == vassal_name:
            world.vassal_rebellion_imminent_popup = None
    # V2-90: Also clear from popups list
    if hasattr(world, 'vassal_rebellion_imminent_popups'):
        world.vassal_rebellion_imminent_popups = [
            p for p in world.vassal_rebellion_imminent_popups
            if p.get("nation") != vassal_name
        ]
    # R12C: Clear vassal rebellion dialogues for this vassal from current + queue
    world.dialogue_manager.remove_matching(
        lambda d: (d.get("type") == "vassal_rebellion_imminent"
                   and d.get("context", {}).get("vassal_name") == vassal_name)
    )

    # R14: Set release cooldown (blocks re-vassalization — by treaty AND by
    # conquest, see create_vassal_treaty / create_vassal_conquest — for 5 turns)
    if not hasattr(world, 'vassal_release_cooldowns'):
        world.vassal_release_cooldowns = {}
    world.vassal_release_cooldowns[vassal_name] = RELEASE_COOLDOWN_TURNS

    # R50: Remove from Continental System on release
    cs_members = getattr(world, 'continental_system_members', [])
    if isinstance(cs_members, set):
        cs_members.discard(vassal_name)
    elif isinstance(cs_members, list) and vassal_name in cs_members:
        cs_members.remove(vassal_name)

    # Set diplomatic state to PEACE (or WAR if rebellion) — R2: centralized setter
    from backend.game_logic.diplomacy import set_diplomatic_state
    if rebellion:
        # Slice A2 §7.2 "Direct WAR-entry rule": vassal-release rebellion
        # must allocate / reuse a war_instance before the WAR transition.
        from backend.game_logic.settlement_helpers import (
            ensure_war_instance_for_pair,
        )
        war_instance_result = ensure_war_instance_for_pair(
            world,
            lord,
            vassal_name,
            entry_path="vassal_release_rebellion",
            reason="release_vassal rebellion",
        )
        if not war_instance_result.get("ok"):
            return {
                "success": False,
                "message": (
                    f"Vassal release rebellion blocked: "
                    f"{war_instance_result.get('error')} "
                    f"({war_instance_result.get('details', {}).get('reason', '')})"
                ),
                "error": war_instance_result.get("error"),
                "error_details": war_instance_result.get("details", {}),
            }
        set_diplomatic_state(world, lord, vassal_name, "WAR", "vassal_release_rebellion")
    else:
        set_diplomatic_state(world, lord, vassal_name, "PEACE", "vassal_release")
        # Coalition threat reduction: voluntary vassal release (COALITION_SPEC §2b)
        threat_after = threat_before
        if reduce_threat_on_release and lord:
            from backend.game_logic.coalition import reduce_threat
            # Use the RETURN value, not the constant — reduce_threat clamps at
            # 0, so "-8" is a lie whenever the slot is already below 8.
            threat_after = reduce_threat(
                world, 8, "voluntary_vassal_release", target=lord)

    if rebellion:
        # The pair went to WAR, not PEACE, and no threat was relieved — none
        # of the voluntary-concession copy below is true on this arm.
        return {
            "success": True,
            "message": f"{client_cap} has been released from vassalage.",
        }

    return {
        "success": True,
        "message": _build_release_report(
            world,
            vassal_name,
            lord,
            lost_tribute=lost_tribute,
            released_marshals=released_marshals,
            was_continental_member=was_continental_member,
            threat_before=threat_before,
            threat_after=threat_after,
        ),
    }


# ═══════════════════════════════════════════════════════
# COOLDOWN MANAGEMENT
# ═══════════════════════════════════════════════════════

def decrement_vassal_cooldowns(world) -> None:
    """Decrement vassal investment and release cooldowns by 1. Remove expired."""
    cooldowns = getattr(world, 'vassal_investment_cooldowns', {})
    expired = []
    for vassal_name in cooldowns:
        cooldowns[vassal_name] -= 1
        if cooldowns[vassal_name] <= 0:
            expired.append(vassal_name)
    for vassal_name in expired:
        del cooldowns[vassal_name]
    world.vassal_investment_cooldowns = cooldowns

    # R14: Release cooldowns
    release_cds = getattr(world, 'vassal_release_cooldowns', {})
    for n in list(release_cds):
        release_cds[n] -= 1
    expired_r = [n for n in release_cds if release_cds[n] <= 0]
    for n in expired_r:
        del release_cds[n]
    world.vassal_release_cooldowns = release_cds

    # VS-3: per-vassal grant cooldowns ride the vassal row itself
    # (serialize for free with the vassals dict).
    for state in getattr(world, 'vassals', {}).values():
        if state.get("grant_cooldown", 0) > 0:
            state["grant_cooldown"] = int(state["grant_cooldown"]) - 1
            if state["grant_cooldown"] <= 0:
                state.pop("grant_cooldown", None)


# ═══════════════════════════════════════════════════════
# ENEMY VASSAL COURTING
# ═══════════════════════════════════════════════════════

def attempt_vassal_courting(world, nation: str) -> List[dict]:
    """
    Enemy AI attempts to court player's vassals.

    Conditions:
    - Nation has 2+ DP
    - Player has vassals with loyalty < 50
    Cost: 2 DP
    Success: loyalty -15 (positive relation) or -5 (negative relation)
    Anti-spam: 3-turn cooldown per nation per vassal

    Returns list of event dicts.
    """
    events = []
    player = getattr(world, 'player_nation', 'France')

    dp = getattr(world, 'nation_dp', {}).get(nation, 0)
    if dp < 2:
        return events

    # VS-R: the Allies peel satellites precisely when Napoleon looks weak. As the
    # player's imperial grip falls the courting unlock reaches DEEPER (threshold
    # 50 -> 50 + bonus) and each success bites HARDER (loyalty_reduction x1.0 ->
    # x1.5). Both are 0 / x1.0 at healthy grip, so boot behaviour is byte-
    # identical. Bounded by the existing 3-turn cooldown + one-vassal-per-turn cap.
    player_grip = get_imperial_grip(world, player)
    unlock_bonus = courting_unlock_bonus(player_grip)
    eff_scale = courting_effectiveness_scale(player_grip)

    # NA-2 §5.4 courting bias: a court whose acquire/deny design lies in a
    # player-vassal's territory courts THAT vassal first (Austria courts
    # the Kingdom of Italy that holds Milan). Bias only — eligibility,
    # cost, cooldowns, and the one-per-turn cap below are unchanged;
    # sorted() is stable, so non-target vassals keep their original order.
    from backend.game_logic.agendas import vassal_holds_agenda_target
    courting_candidates = sorted(
        world.vassals.items(),
        key=lambda kv: 0 if vassal_holds_agenda_target(nation, kv[0], world) else 1,
    )

    for vassal_name, state in courting_candidates:
        if state["lord"] != player:
            continue
        if state["loyalty"] >= 50 + unlock_bonus:
            continue

        # Anti-spam cooldown
        cooldown_key = f"court|{nation}|{vassal_name}"
        cooldown = getattr(world, 'ai_proposal_cooldowns', {}).get(cooldown_key, 0)
        if cooldown > 0:
            continue

        # WO-8 (a)(b)(c). Sited BELOW the per-courtier cooldown read — which
        # keeps that older pin live — and ABOVE every side effect this body
        # has: the DP debit, the loyalty write, the cooldown set, the
        # notification, the event, and the 60% dispatch roll. A courtier the
        # cap turns away therefore spends nothing.
        if COURTING_TARGET_CAP_ACTIVE:
            # (b) + (c) — no self-court, no courting a fellow satellite of
            # one's own lord. Both live in the pure predicate above, where
            # a non-player lord is reachable and the rule is falsifiable.
            if courtier_is_of_the_same_house(world, nation, vassal_name, state):
                continue
            # The design stake outranks the roster (rider above). Sited
            # with the other guards, above every side effect, so a
            # courtier that stands aside spends nothing doing it.
            if courtier_yields_to_a_design_stake(world, nation, vassal_name,
                                                 state):
                continue
            # (a) one successful court per TARGET per turn, world-wide. The
            # first courtier in enemy-nation order wins; that order is a
            # list all the way down (EUROPE_ROSTER -> enemy_nations ->
            # turn_manager's filtering comprehension), so it is deterministic
            # without a sort.
            #
            # Two consequences, recorded rather than fixed (WO slice 9):
            # the winner is whoever comes FIRST, not whoever bites hardest,
            # so a Britain court worth -5 can consume the slot and block a
            # Prussia court worth -15; and the NA-2 courting bias above
            # sorts a courtier's candidate VASSALS, never courtiers per
            # target, so it is overruled by roster order on exactly the
            # contested case. A strongest-bite tiebreak would be a new
            # mechanic and would re-open the determinism this cap was
            # asked for. Note this is a `continue`, not a `break`: a
            # courtier the cap turns away still courts a DIFFERENT
            # eligible satellite this turn, so the cap redistributes
            # courting rather than destroying it.
            if state.get("courted_turn") == int(world.current_turn):
                continue

        # IQ-7 R2: the lord's own allies do not court its satellites. Sited
        # with the WO-8 guards — below the per-courtier cooldown read, above
        # the DP debit and every other side effect — so an ally that stands
        # aside spends nothing and sets no cooldown. Its own lever, so the
        # BASELINE_SERIES attribution arms can isolate it.
        if (COURTING_SPARES_THE_LORDS_ALLIES
                and courtier_is_the_lords_ally(world, nation, state)):
            continue

        # Cost 2 DP
        dp_nations = getattr(world, 'nation_dp', {})
        if dp_nations.get(nation, 0) < 2:
            continue

        dp_nations[nation] = dp_nations.get(nation, 0) - 2

        # Calculate loyalty reduction (VS-R: scaled by the player's grip)
        diplo_key = world._make_diplo_key(vassal_name, nation)
        relation = world.nation_relations.get(diplo_key, 0)
        base_reduction = 15 if relation > 0 else 5
        loyalty_reduction = int(round(base_reduction * eff_scale))

        state["loyalty"] = max(LOYALTY_MIN, state["loyalty"] - loyalty_reduction)

        # Set cooldown
        cooldowns_dict = getattr(world, 'ai_proposal_cooldowns', {})
        cooldowns_dict[cooldown_key] = 3
        world.ai_proposal_cooldowns = cooldowns_dict

        # WO-8 (a): stamp the TARGET. A turn-stamp rather than a countdown
        # needs no tick-down maintenance and cannot expire wrongly, and it
        # rides the vassal row, so it serializes for free with the vassals
        # dict — zero new serialized fields (the VS-3 `grant_cooldown`
        # precedent above).
        if COURTING_TARGET_CAP_ACTIVE:
            state["courted_turn"] = int(world.current_turn)

        # Notification: courting detected (Session 8C)
        from backend.notifications import (
            create_notification, NotificationPriority, VASSAL_COURTING_DETECTED,
        )
        world.notifications.add(create_notification(
            VASSAL_COURTING_DETECTED,
            NotificationPriority.NORMAL,
            f"{display_nation(nation)} Courts {display_nation(vassal_name)}",
            f"Enemy agents from {display_nation(nation)} detected courting "
            f"{display_nation(vassal_name)}.",
            int(world.current_turn),
        ))

        events.append({
            "type": "vassal_courting",
            "nation": nation,
            "vassal": vassal_name,
            "loyalty_reduction": int(loyalty_reduction),
            "new_loyalty": int(state["loyalty"]),
            "message": f"{nation} is courting {vassal_name}! Loyalty dropped by {loyalty_reduction}.",
        })

        # Dispatch event — 60% detection at queue time (Session 8D)
        import random as _rng
        if _rng.random() < 0.60:
            from backend.game_logic.dispatch import queue_dispatch_event
            vassal_capital = world.get_nation_capital(vassal_name) or vassal_name
            queue_dispatch_event(world, "diplomatic_vassal_courting",
                                {"enemy": nation, "vassal_capital": vassal_capital},
                                "detection_60pct")

        # Only court one vassal per nation per turn
        break

    return events


# ═══════════════════════════════════════════════════════
# THE DEFECTION (VS-6)
# ═══════════════════════════════════════════════════════

def _defect_vassal_free_and_hostile(world, vassal_name: str, briber: str) -> dict:
    """VS-6 outcome 1: the bribed vassal becomes FREE — and GUARANTEED at
    WAR with its former lord (the deliberate contrast to F8b's graceful
    PEACE break: the briber 'liberated' them; they are now an enemy
    belligerent). Mirrors the rebellion WAR block incl. the VS-3 reclaim;
    keeps the armistice + war-instance-failure fallbacks.
    """
    state = world.vassals[vassal_name]
    lord = state["lord"]
    granted_regions = list(state.get("granted_regions") or [])

    # FA-N19 (slice 11): this arm queued "{carved_name} has ceased to
    # exist." beside the caller's own "THE DEFECTION: Britain's gold turns
    # Switzerland against France." — of a court that keeps Bern and takes
    # the field. Measured on seeds 1/3/4/7/8. `attempt_vassal_bribe` briefs
    # every landed outcome already, and the TRANSFER outcome never queued
    # this line at all, so the two arms now agree. Behind FA-2's lever, so
    # False reproduces the pre-slice briefing on this arm too.
    if not THE_BREAK_IS_BRIEFED_TRUTHFULLY:
        from backend.game_logic.dispatch import queue_dispatch_event
        queue_dispatch_event(world, "diplomatic_carved_vassal_dissolved",
                             {"carved_name": vassal_name, "protector": lord},
                             "always")

    del world.vassals[vassal_name]
    world.invalidate_active_nations_cache()

    # Post-build review C7: clear any queued rebellion-imminent UI for the
    # departing vassal (mirrors transfer_vassal/release_vassal — a loyalty-8
    # vassal can queue the popup in the same end_turn's advance_turn, then
    # the AI-phase bribe deletes the row → stale modal).
    if getattr(world, 'vassal_rebellion_imminent_popup', None):
        if world.vassal_rebellion_imminent_popup.get("nation", "") == vassal_name:
            world.vassal_rebellion_imminent_popup = None
    if hasattr(world, 'vassal_rebellion_imminent_popups'):
        world.vassal_rebellion_imminent_popups = [
            p for p in world.vassal_rebellion_imminent_popups
            if p.get("nation") != vassal_name
        ]
    world.dialogue_manager.remove_matching(
        lambda d: (d.get("type") == "vassal_rebellion_imminent"
                   and d.get("context", {}).get("vassal_name") == vassal_name)
    )

    diplo_key = world._make_diplo_key(lord, vassal_name)
    current_state = world.diplomatic_states.get(diplo_key, "PEACE")
    outcome = "free_hostile"
    if current_state == "ARMISTICE":
        # A respected armistice is a treaty — the break is not hostile.
        outcome = "free_armistice"
    else:
        from backend.game_logic.diplomacy import (
            _process_war_cascade,
            cleanup_war_end,
            set_diplomatic_state,
        )
        from backend.game_logic.settlement_helpers import (
            CascadeContext,
            ensure_war_instance_for_pair,
        )
        # Post-build review C2 (HIGH, reproduced live): a cascaded-in
        # satellite is an active SAME-SIDE participant of its lord's war
        # instance(s) — ensure_war_instance_for_pair(vassal, lord) would
        # hard-fail on the side conflict and silently take the PEACE
        # fallback, inverting the guaranteed-WAR contract AND leaving the
        # "freed" nation still at war with its paid liberator. Exit the
        # vassal from its old wars FIRST: peace out every WAR pair it holds
        # (they were all fought FOR the lord) so resolve_pair_to_resolved
        # retires it from the shared instances; the freed nation then opens
        # its own war against the former lord cleanly — the historically
        # faithful side-switch.
        for other in list(world.get_active_nations()):
            if other in (vassal_name, lord):
                continue
            if world.get_diplomatic_state(vassal_name, other) == "WAR":
                set_diplomatic_state(
                    world, vassal_name, other, "PEACE",
                    "coalition_defection_realignment",
                )
                cleanup_war_end(
                    world,
                    world._make_diplo_key(vassal_name, other),
                    conclude_objectives=True,
                )
        war_instance_result = ensure_war_instance_for_pair(
            world, vassal_name, lord,
            entry_path="coalition_defection",
            reason="attempt_vassal_bribe",
        )
        if war_instance_result.get("ok"):
            set_diplomatic_state(world, vassal_name, lord, "WAR",
                                 "coalition_defection")
            cascade_ctx = CascadeContext(
                war_id=war_instance_result["war_id"],
                root_aggressor=vassal_name,
                war_entry_entries=[],
            )
            _process_war_cascade(world, vassal_name, lord, ctx=cascade_ctx)
            # VS-3 reclaim: the gift flips back when the vassal turns hostile
            reclaimed = []
            for granted_name in granted_regions:
                granted_region = world.regions.get(granted_name)
                if (granted_region is not None
                        and getattr(granted_region, 'controller', '') == vassal_name):
                    granted_region.controller = lord
                    reclaimed.append(granted_name)
            if reclaimed:
                world.invalidate_active_nations_cache()
        else:
            # F8b fallback: war-instance conflict → plain independence.
            # PINNED: the graceful fallback keeps the VS-3 granted land
            # (consistent with the rebellion path's armistice/graceful arms
            # — reclaiming during a peaceful break would itself be hostile).
            set_diplomatic_state(world, vassal_name, lord, "PEACE",
                                 "coalition_defection_independent")
            outcome = "free_peace_fallback"

    # Marshals return to the freed nation (mirror the rebellion block)
    for marshal in list(world.marshals.values()):
        if (getattr(marshal, 'original_nation', None) == vassal_name
                and getattr(marshal, 'nation', '') == lord):
            marshal.nation = vassal_name
            marshal.original_nation = None
            marshal.trust = Trust()
            if hasattr(marshal, 'relationship_with_lord'):
                delattr(marshal, 'relationship_with_lord')

    # Sibling shock + relations (mirror the rebellion block)
    for other_vassal, other_state in world.vassals.items():
        if other_state["lord"] == lord:
            other_state["loyalty"] = max(LOYALTY_MIN, other_state["loyalty"] - 10)
    world.modify_nation_relation(lord, vassal_name, -50)
    world.modify_nation_relation(vassal_name, briber, 30)
    if lord:
        from backend.game_logic.coalition import reduce_threat
        reduce_threat(world, 10, "vassal_defection", target=lord)

    return {"outcome": outcome, "lord": lord}


def attempt_vassal_bribe(world, nation: str) -> List[dict]:
    """VS-6: a nation at WAR with a lord tries to BRIBE one of that lord's
    wavering satellites into defecting. Runs in the AI diplomatic phase
    immediately after courting and RESOLVES IMMEDIATELY (the bribed vassal
    is transferred/freed before advance_turn's cascade/rebellion chain ever
    sees it — kills the double-fire risk structurally, zero new serialized
    fields).

    Gates (all required):
    - briber at WAR with the lord and able to pay (BRIBE_FREE_COST minimum);
    - vassal courtable: loyalty < 35 (the VS-4 disaffected line), or < 50
      while the lord's grip spirals (< 30) — the Ried window;
    - per-pair 5-turn cooldown + a per-vassal 1-turn latch (N coalition
      members cannot pile on one vassal in a single turn);
    - the flip is PROBABILISTIC: chance = (40 − loyalty)/100, scaled by
      courting_effectiveness_scale(lord grip). A failed bribe still burns
      the briber's gold half-stake and warns the lord.

    Outcome when it lands: the briber becomes the NEW LORD (transfer, VS-5
    machinery) when it passes the WPS-B power cap AND pays BRIBE_TRANSFER_COST;
    otherwise it pays BRIBE_FREE_COST and the vassal goes FREE + HOSTILE to
    the old lord. GR5 lord-neutral: any lord's satellites can be bribed —
    the PLAYER-side verb is a deferred owner row (structurally latent until
    an enemy lord holds a satellite).
    """
    events = []
    treasury = world.nation_gold.get(nation, 0)
    if treasury < BRIBE_FREE_COST:
        return events

    cooldowns_dict = getattr(world, 'ai_proposal_cooldowns', {})

    for vassal_name, state in list(world.vassals.items()):
        lord = state["lord"]
        if lord == nation or vassal_name == nation:
            continue
        if not world.is_at_war(nation, lord):
            continue

        # Per-pair cooldown + per-vassal latch
        pair_key = f"defect|{nation}|{vassal_name}"
        latch_key = f"defect_pause|{vassal_name}"
        if cooldowns_dict.get(pair_key, 0) > 0 or cooldowns_dict.get(latch_key, 0) > 0:
            continue

        # Courtable window (VS-4/VS-R interlock)
        loyalty = int(state.get("loyalty", 100))
        lord_grip = get_imperial_grip(world, lord)
        in_spiral = lord_grip < AUTHORITY_ACCELERATE_BELOW
        if loyalty >= BRIBE_ELIGIBLE_LOYALTY and not (
                in_spiral and loyalty < BRIBE_SPIRAL_LOYALTY):
            continue

        # The offer is on the table — latch + cooldown regardless of outcome
        cooldowns_dict[pair_key] = BRIBE_COOLDOWN
        cooldowns_dict[latch_key] = BRIBE_VASSAL_PAUSE
        world.ai_proposal_cooldowns = cooldowns_dict

        # The chance pivot widens with the lord's collapse (the Ried
        # dynamic): healthy grip flips only the disaffected (<40 pivot);
        # a spiral makes even the merely-wavering biddable (<50 pivot).
        pivot = BRIBE_SPIRAL_LOYALTY if in_spiral else BRIBE_CHANCE_PIVOT
        chance = max(0.0, (pivot - loyalty) / 100.0)
        chance *= courting_effectiveness_scale(lord_grip)
        landed = random.random() < chance

        if not landed:
            # The approach costs half the purse and the lord's court hears
            world.nation_gold[nation] = int(
                world.nation_gold.get(nation, 0) - BRIBE_FREE_COST // 2)
            # IQ1-2 (3): a failed approach is still money spent.
            world.record_gold_spent(nation, int(BRIBE_FREE_COST // 2))
            if lord == getattr(world, 'player_nation', 'France'):
                from backend.notifications import (
                    NotificationPriority,
                    VASSAL_COURTING_DETECTED,
                    create_notification,
                )
                world.notifications.add(create_notification(
                    VASSAL_COURTING_DETECTED,
                    NotificationPriority.HIGH,
                    f"{display_nation(nation)} Tempts {display_nation(vassal_name)}",
                    (f"{display_nation(nation)}'s agents offered "
                     f"{display_nation(vassal_name)} terms to change sides. "
                     f"The offer was refused — this time."),
                    int(world.current_turn),
                ))
            events.append({
                "type": "vassal_bribe_refused",
                "nation": nation,
                "vassal": vassal_name,
                "lord": lord,
                "message": (f"{nation}'s bribe is refused — {vassal_name} "
                            f"stays with {lord}, for now."),
            })
            break  # one bribe per nation per turn

        # The bribe lands — pick the outcome by what the briber can carry
        from backend.game_logic.diplomacy import check_vassalage_power_cap
        cap = check_vassalage_power_cap(world, nation, vassal_name)
        can_transfer = (cap.get("allowed")
                        and world.nation_gold.get(nation, 0) >= BRIBE_TRANSFER_COST)
        if can_transfer:
            world.nation_gold[nation] = int(
                world.nation_gold.get(nation, 0) - BRIBE_TRANSFER_COST)
            # IQ1-2 (3): the bribe is a purchase — of a satellite.
            world.record_gold_spent(nation, int(BRIBE_TRANSFER_COST))
            # Post-build review C1 (HIGH, reproduced live): the briber and
            # the vassal are usually at WAR (the vassal cascade-joined its
            # lord's war), and transfer_vassal requires that pair settled
            # FIRST — force-flipping WAR→VASSAL would strand the pair in the
            # war instance forever (all_pairs_resolved unreachable, prisoners
            # never released). Mirror the settlement_ratify arm: PEACE +
            # cleanup_war_end so resolve_pair_to_resolved exits the pair and
            # the vassal participant cleanly.
            if world.get_diplomatic_state(nation, vassal_name) in ("WAR", "ARMISTICE"):
                from backend.game_logic.diplomacy import (
                    cleanup_war_end,
                    set_diplomatic_state,
                )
                set_diplomatic_state(world, nation, vassal_name, "PEACE",
                                     "coalition_defection")
                cleanup_war_end(
                    world,
                    world._make_diplo_key(nation, vassal_name),
                    conclude_objectives=True,
                )
            transfer_result = transfer_vassal(
                world, vassal_name, nation, reason="coalition_defection")
            # Post-build review C8: losing a satellite relieves the anti-
            # player threat on every other loss path (rebellion −10, release
            # −8, defection-free −10) — the transfer outcome is the same
            # player loss and gets the same relief.
            if lord:
                from backend.game_logic.coalition import reduce_threat
                reduce_threat(world, 10, "vassal_defection", target=lord)
            outcome = "transfer"
            # IQ-7 R7 fix in passing: the DEFECTION copy is player prose on
            # the tray and the turn report — the R7 table, at the producer.
            message = (
                f"THE DEFECTION: {display_nation(vassal_name)} changes masters "
                f"— bribed away from {display_nation(lord)}, it now serves "
                f"{display_nation(nation)}."
            )
        else:
            world.nation_gold[nation] = int(
                world.nation_gold.get(nation, 0) - BRIBE_FREE_COST)
            # IQ1-2 (3): the cheaper outcome, same purchase.
            world.record_gold_spent(nation, int(BRIBE_FREE_COST))
            free_result = _defect_vassal_free_and_hostile(
                world, vassal_name, nation)
            outcome = free_result["outcome"]
            message = (
                f"THE DEFECTION: {display_nation(nation)}'s gold buys "
                f"{display_nation(vassal_name)}'s 'independence' — it breaks "
                f"with {display_nation(lord)} and takes the field against its "
                f"former master."
            ) if outcome == "free_hostile" else (
                f"{display_nation(vassal_name)} breaks with "
                f"{display_nation(lord)}, bought free by {display_nation(nation)}."
            )

        if hasattr(world, "log_event"):
            world.log_event({
                "type": "vassal_defected",
                "vassal": vassal_name,
                "lord": lord,
                "briber": nation,
                "outcome": outcome,
            })
        # GE-3: a satellite bought away during the Congress breaks the hold
        # (both outcomes — the transfer never passes `record_vassal_break`).
        from backend.game_logic.congress import note_rebellion as _congress_lost
        _congress_lost(world, vassal_name, lord, defected_to=nation)
        from backend.game_logic.dispatch import queue_dispatch_event
        queue_dispatch_event(
            world, "diplomatic_vassal_defected",
            {"vassal": vassal_name, "lord": lord, "briber": nation,
             "nation": lord},
            "always",
        )
        if lord == getattr(world, 'player_nation', 'France'):
            from backend.notifications import (
                NotificationPriority,
                VASSAL_REBELLION,
                create_notification,
            )
            world.notifications.add(create_notification(
                VASSAL_REBELLION,
                NotificationPriority.CRITICAL,
                f"{display_nation(vassal_name)} DEFECTS!",
                message,
                int(world.current_turn),
            ))

        events.append({
            "type": "vassal_defected",
            "nation": nation,
            "vassal": vassal_name,
            "lord": lord,
            "outcome": outcome,
            "message": message,
        })
        break  # one bribe per nation per turn

    return events
