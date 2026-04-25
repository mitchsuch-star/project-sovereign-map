"""
Coalition System — Phase 8 Session 7 (COALITION_SPEC v1.1)

The coalition system creates the core Napoleonic strategic puzzle: the better
you play, the harder Europe pushes back. Threat accumulates from aggressive
actions, triggers brewing warnings, and eventually causes multi-nation
coalition wars.

All coalition logic lives in this file. Functions are called from:
  - executor.py (after battles, captures, vassalization → add_threat)
  - world_state.py advance_turn (process_coalition_turn)
  - diplomacy.py (acceptance formula → get_coalition_loyalty_penalty)
  - enemy_ai.py (convergence bias, friction, is_coalition_member)
"""

from typing import Dict, List, Optional

from backend.notifications import (
    create_notification, NotificationPriority,
    COALITION_THREAT_TENSION, COALITION_MURMURS, COALITION_BREWING,
    COALITION_DECLARED, COALITION_MEMBER_PEACED, COALITION_DISSOLVED,
    COALITION_COOLDOWN_ENDED, BALANCE_OF_EUROPE_SHIFTED,
)

# ════════════════════════════════════════════════════════════════
# CONSTANTS
# ════════════════════════════════════════════════════════════════

PEACEFUL_STATES = ("PEACE", "NON_AGGRESSION", "OPEN_BORDERS",
                   "DEFENSIVE_ALLIANCE", "ALLIANCE")

# Threat thresholds (§3a)
THREAT_CALM_MAX = 29
THREAT_TENSION_MIN = 30
THREAT_MURMURS_MIN = 40
THREAT_BREWING_MIN = 60
THREAT_INSTANT_MIN = 80
THREAT_OVERRIDE_COOLDOWN_MIN = 90

# Brewing cancellation floor (§3c momentum rule)
BREWING_CANCEL_THRESHOLD = 40

# Coalition dissolution threat floor (§7a)
DISSOLUTION_THREAT_THRESHOLD = 20

# Post-dissolution cooldown (§7c)
COALITION_COOLDOWN_TURNS = 5

# Brewing countdown (§3c)
BREWING_COUNTDOWN = 3

# Decay cap (§2b)
DECAY_CAP = 3

# War exhaustion caps
WAR_EXHAUSTION_MAX = 200
WAR_EXHAUSTION_BATTLE_CAP = 20

# Coalition loyalty penalty base (§6a)
COALITION_LOYALTY_BASE = -15

# Coalition ordinal names
_ORDINALS = {1: "First", 2: "Second", 3: "Third", 4: "Fourth", 5: "Fifth",
             6: "Sixth", 7: "Seventh"}


# ════════════════════════════════════════════════════════════════
# HELPER: Get all nations from world
# ════════════════════════════════════════════════════════════════

def _get_all_nations(world) -> List[str]:
    """Return all active (non-eliminated) nations. DLF-11."""
    return world.get_active_nations()


def _get_diplo_key(a: str, b: str) -> str:
    """Alphabetically sorted nation pair key."""
    return "|".join(sorted([a, b]))


def _get_relation(world, a: str, b: str) -> int:
    """Get relation between two nations."""
    return world.nation_relations.get(_get_diplo_key(a, b), 0) or 0


def _get_diplo_state(world, a: str, b: str) -> str:
    """Get diplomatic state between two nations."""
    return world.diplomatic_states.get(_get_diplo_key(a, b), "PEACE")


# ════════════════════════════════════════════════════════════════
# B-HEGEMONY: Balance-of-power engine (v2.4.3 §7.2-§7.3)
# ════════════════════════════════════════════════════════════════
#
# RELIABILITY_COMMITMENTS_SPEC §7.1-§7.3 + COMMITMENTS_PRESENTATION_SPEC
# §8.1a bloc-naming contract. Reads bloc geometry + authored power_tier
# scenario data; adds passive threat against the current hegemon via
# the existing `add_threat()` API; emits `balance_of_europe_shifted`
# beats at `33 / 50 / 60` band crossings.

# Tier weights live here (not in nation_config) because they are the
# engine's tunable authoring knob. Tier assignments themselves are
# authored per-nation in `nation_config.NATION_POWER_TIERS`.
_POWER_TIER_WEIGHT = {"major": 3, "secondary": 2, "minor": 1}

# Canonical 5-major safe-list for the defensive fallback when no
# authored `major` nations exist in the active roster (per §7.3
# defensive-fallback bullet). Keeps v0.1 calc correct under minimal
# scenario data.
_CANONICAL_MAJORS = ("France", "Britain", "Russia", "Austria", "Prussia")

# Proper-noun bloc-name taxonomy per
# COMMITMENTS_PRESENTATION_SPEC §8.1a.3. Unlocks at 50%+ share; below
# 50% consumers fall through to the `descriptive_label` field.
_BLOC_PROPER_NAMES = {
    "France": "French System",
    "Britain": "British Interest",
    "Russia": "Russian Sphere",
    "Austria": "Vienna System",
    "Prussia": "Berlin Alignment",
}

# Adjective stems paired to the proper-noun taxonomy (used to compose
# `descriptive_label` as "{adjective}-led alignment"). Fallback for
# unknown hegemons is `{hegemon}-led` by string, handled in helper.
_BLOC_ADJECTIVES = {
    "France": "French",
    "Britain": "British",
    "Russia": "Russian",
    "Austria": "Austrian",
    "Prussia": "Prussian",
    "Spain": "Spanish",
    "Ottoman": "Ottoman",
    "Sweden": "Swedish",
    "Naples": "Neapolitan",
    "Bavaria": "Bavarian",
    "Saxony": "Saxon",
    "Portugal": "Portuguese",
    "Denmark-Norway": "Danish",
}


def power_score(nation: str, world) -> int:
    """Return authored power score for a nation.

    Formula: `region_count * tier_weight` where tier_weight is
    `{major: 3, secondary: 2, minor: 1}` looked up from authored
    `power_tier` (with `_POWER_TIER_DEFAULT = "secondary"` fallback).

    Reads `world.get_nation_regions(nation)` — per-turn cached via
    `invalidate_active_nations_cache()` seam (CLAUDE.md golden rule 8 —
    NO per-region scans in hot paths).
    """
    from backend.nation_config import _POWER_TIER_DEFAULT
    region_count = len(world.get_nation_regions(nation))
    tier = world.get_power_tier(nation) or _POWER_TIER_DEFAULT
    tier_weight = _POWER_TIER_WEIGHT.get(
        tier, _POWER_TIER_WEIGHT[_POWER_TIER_DEFAULT]
    )
    return int(region_count * tier_weight)


def bloc_power(leader: str, world) -> int:
    """Sum of `power_score` across `get_bloc_members(leader)`."""
    return int(sum(power_score(n, world) for n in world.get_bloc_members(leader)))


def _hegemony_signal_band(share: float) -> int:
    """Pure current-share reader. Returns 0/1/2/3 per §7.3 thresholds.

    NOTE: distinct from `_hegemony_pressure_for_share` — the signal band
    surfaces three player-facing bands (1 noticed, 2 alarming, 3 crisis)
    but the pressure ladder has four values (1/3/5/8). Do not conflate.

    Used for label selection and band comparisons; do NOT conflate with
    `world.hegemony_signal_high_water` which is stored public-memory /
    dedupe state.
    """
    if share < 0.33:
        return 0
    if share < 0.50:
        return 1
    if share < 0.60:
        return 2
    return 3


def _hegemony_pressure_for_share(share: float) -> int:
    """Threat increment per turn based on bloc share. Authored ladder.

    Gates align to the 33 / 50 / 60 naming beats so every new public
    band crossing has a same-turn `balance_of_europe_shifted` scene.
    The 33-49% band is warning/tutorial territory. The 70%+ step is a
    scalar-only crisis intensifier — no new naming tier.
    """
    if share < 0.33:
        return 0       # safe (no beat, no pressure)
    if share < 0.50:
        return 1       # noticed — warning / anti-decay band
    if share < 0.60:
        return 3       # alarming — paired with 50% beat
    if share < 0.70:
        return 5       # crisis — paired with 60% beat
    return 8           # near-complete hegemony (>=70%) — no new beat


def _identify_max_bloc_share(world):
    """Shared hegemon-identity helper. Returns `(leader, share)` of the
    largest bloc regardless of threshold. Returns `(None, 0.0)` when no
    active nations or when `european_power == 0`.

    Both `_calculate_hegemony_pressure` (which gates passive threat
    accrual at 33%+) and `hegemony_target_mod` in `diplomacy.py` (which
    applies a per-pair acceptance penalty starting at the 30% boundary)
    read from this helper. Decoupling "who is the prospective hegemon"
    from "is threat accruing yet" lets the 30% / 33% split be real
    rather than decorative.

    Tie-break: highest share, then highest absolute bloc_power, then
    alphabetical nation name. Deterministic under 13+ nations where
    two blocs may tie exactly.
    """
    active = world.get_active_nations()
    if not active:
        return (None, 0.0)
    european_power = sum(power_score(n, world) for n in active)
    if european_power == 0:
        return (None, 0.0)
    majors = [n for n in active if world.get_power_tier(n) == "major"]
    if not majors:
        # Defensive fallback — per §7.3. Use canonical 5-major safe-list
        # intersected with actives, not the full actives pool.
        majors = [n for n in _CANONICAL_MAJORS if n in active]
        if not majors:
            majors = list(active)  # last-resort safety for unknown rosters
    bloc_shares = {
        leader: bloc_power(leader, world) / european_power
        for leader in majors
    }
    # Deterministic ordering: highest share, then highest bloc_power, then alpha
    ordered = sorted(
        bloc_shares.items(),
        key=lambda kv: (-kv[1], -bloc_power(kv[0], world), kv[0]),
    )
    return (ordered[0][0], float(ordered[0][1]))


def _calculate_hegemony_pressure(world) -> Dict[str, int]:
    """Per-turn passive threat from bloc-share dominance.

    Gates at 33%+ share. Below 33%, returns `{}` — no passive threat,
    no beat fires. The 30-33% per-pair friction zone is owned by
    `hegemony_target_mod` in `diplomacy.py`.

    Returns `{hegemon_nation: threat_increment}` or `{}`.
    """
    hegemon, share = _identify_max_bloc_share(world)
    if hegemon is None or share < 0.33:
        return {}
    return {hegemon: _hegemony_pressure_for_share(share)}


def _pick_counterplay_hint(world, hegemon: str, share: float, band: int) -> str:
    """Capability-aware counter-play hint per §7.3.

    Only returns a named-contributor hint when the player is the hegemon
    AND a non-hegemon bloc member exists that is plausibly actionable
    through a current legal lever (vassal release, alliance lapse).
    Otherwise returns the always-valid restraint floor.

    When player is NOT hegemon, returns empty string (no-hint descriptive
    variant) per §7.3 forward-compat rule.
    """
    player = getattr(world, "player_nation", "France")
    if hegemon != player:
        return ""
    # Tutorial floor at 33% noticed band
    members = world.get_bloc_members(hegemon)
    non_hegemon = [m for m in members if m != hegemon]
    if not non_hegemon:
        if band == 1:
            return ("Another major alliance would push Europe past fifty percent "
                    "and harden the courts into camp.")
        return ("Hold the bloc where it stands; another major ally would harden "
                "Europe further.")
    # Causally specific contributor: pick the highest power_score contributor
    # among non-hegemon members. This is the "decisive slice" of the bloc.
    sorted_contrib = sorted(
        non_hegemon,
        key=lambda n: (-power_score(n, world), n),
    )
    top = sorted_contrib[0]
    # Is the contributor actionable through a shipped legal lever?
    # v0.1: vassal release is the core lever; alliance lapse is adjacent.
    is_vassal = top in getattr(world, "vassals", {}) and (
        world.vassals[top].get("lord") == hegemon
    )
    is_ally = world.get_diplomatic_state(hegemon, top) in ("ALLIANCE", "DEFENSIVE_ALLIANCE")
    if is_vassal:
        return (f"{top} is the decisive non-{hegemon.lower()} slice of the bloc; "
                f"releasing it shrinks the share immediately.")
    if is_ally:
        return (f"{top} is the decisive non-{hegemon.lower()} slice of the bloc; "
                f"letting the alliance lapse would ease Europe's pressure.")
    # Fallback to restraint floor (no shipped lever)
    if band == 1:
        return ("Another major alliance would push Europe past fifty percent "
                "and harden the courts into camp.")
    return ("Hold the bloc where it stands; another major ally would harden "
            "Europe further.")


def _pick_speaker_nation(world, hegemon: str) -> str:
    """Deterministic speaker-nation pick per §7.3.

    Highest-weight non-bloc major court. If no non-bloc majors exist,
    fall back to France (Talleyrand advisory register) per the
    "fallback to Talleyrand, not generic chancery" rule. Full voice
    routing + named envoy resolution is Slice C-lite scope; this
    function hands the C-lite layer a `speaker_nation` value that is
    never None.
    """
    from backend.nation_config import _POWER_TIER_DEFAULT
    france_default = getattr(world, "player_nation", "France") or "France"
    bloc = set(world.get_bloc_members(hegemon))
    active = world.get_active_nations()
    # Non-bloc majors only
    candidates = []
    for n in active:
        if n in bloc:
            continue
        tier = world.get_power_tier(n) or _POWER_TIER_DEFAULT
        if tier == "major":
            candidates.append(n)
    if not candidates:
        # No non-bloc majors — fall straight to Talleyrand / France
        return france_default
    # Highest power_score, then alphabetical
    sorted_cand = sorted(
        candidates,
        key=lambda n: (-power_score(n, world), n),
    )
    return sorted_cand[0]


def _check_hegemony_band_crossing(world, caller: str) -> bool:
    """Same-turn band-crossing detector + beat emitter (§7.3).

    Fires a `BALANCE_OF_EUROPE_SHIFTED` notification when the current
    hegemon's bloc crosses a new band (upward from stored high-water),
    OR when the hegemon identity changes within an already-surfaced band.

    Called from multiple ratification seams:
    - `set_diplomatic_state` (covers treaty ratification, war declaration,
      peace ratification, vassal creation/release, cascade, armistice)
    - End of `process_coalition_turn` (catches end-of-turn share changes
      that didn't pass through a ratification seam)

    On a same-turn multi-band jump (28% → 51%), emits ONLY the highest
    newly reached band and writes high_water to that highest value.

    Returns True if a beat was emitted, False otherwise.
    """
    try:
        hegemon, share = _identify_max_bloc_share(world)
    except Exception as exc:
        from backend.utils.debug import debug_print
        debug_print(
            f"[HEGEMONY] band-crossing identify failed ({caller}): {exc}"
        )
        return False
    if hegemon is None:
        return False

    current_band = _hegemony_signal_band(share)
    stored_band = int(getattr(world, "hegemony_signal_high_water", 0) or 0)
    stored_hegemon = getattr(world, "hegemony_signal_hegemon", None)

    # Hegemon change within already-surfaced band (>=1) is a fresh beat.
    hegemon_swap_in_band = (
        current_band >= 1
        and stored_band >= 1
        and hegemon != stored_hegemon
        and current_band == stored_band
    )

    # Upward crossing (new higher band reached)
    upward_crossing = current_band > stored_band

    if not (upward_crossing or hegemon_swap_in_band):
        return False

    # Cooldown-aware wording only at band 3 (crisis)
    cooldown_active = bool(int(getattr(world, "coalition_cooldown", 0) or 0) > 0)
    bloc_info = describe_hegemon_bloc(world, hegemon, share)
    counterplay_hint = _pick_counterplay_hint(world, hegemon, share, current_band)
    speaker_nation = _pick_speaker_nation(world, hegemon)

    # Priority: band 1 = NORMAL; bands 2+3 = CRITICAL
    if current_band >= 2:
        priority = NotificationPriority.CRITICAL
    else:
        priority = NotificationPriority.NORMAL

    # Minimal title/message; Slice C-lite will polish via commitments_notice_*.
    # TODO(Slice C-lite): route through commitments_notice_balance_of_europe_shifted
    #   template family + DIPLOMAT_VOICE_BIBLE hegemony_beat_* registers. For
    #   B-Hegemony we keep copy functional (hegemon + share + label) so the
    #   event is visible in the rail; voice polish is the next slice.
    label_for_title = bloc_info.get("bloc_label") or bloc_info.get("descriptive_label") or hegemon
    share_pct = int(share * 100)
    if current_band == 3:
        title = "Balance of Europe — Crisis"
        if cooldown_active:
            message = (
                f"{label_for_title} commands {share_pct}% of Continental power; "
                f"hostile courts harden into camp, though the last coalition's "
                f"cooldown still binds them for {int(world.coalition_cooldown)} turn(s)."
            )
        else:
            message = (
                f"{label_for_title} commands {share_pct}% of Continental power; "
                f"hostile courts are hardening into camp against it."
            )
    elif current_band == 2:
        title = "Balance of Europe — Alarming"
        message = f"{label_for_title} commands {share_pct}% of Continental power."
    else:  # band 1
        title = "Balance of Europe — Noticed"
        message = f"Europe takes note of a widening {label_for_title} ({share_pct}%)."

    details = {
        "band": int(current_band),
        "hegemon": hegemon,
        "share": round(float(share), 2),
        "bloc_label": bloc_info.get("bloc_label"),
        "descriptive_label": bloc_info.get("descriptive_label"),
        "counterplay_hint": counterplay_hint,
        "speaker_nation": speaker_nation,
        "caller_seam": caller,
    }

    try:
        world.notifications.add(create_notification(
            BALANCE_OF_EUROPE_SHIFTED,
            priority,
            title,
            message,
            int(getattr(world, "current_turn", 1)),
            details=details,
        ))
        # B-Hegemony: retire the legacy anonymous clue family for any
        # share-driven crossing. `COALITION_THREAT_TENSION` /
        # `COALITION_MURMURS` emit sites in `_check_threat_notifications()`
        # remain wired for pure event-threat accrual (battles, captures),
        # but the named `balance_of_europe_shifted` beat MUST NOT co-exist
        # with the anonymous tier line on the same turn per §7.3 bullet
        # "Legacy anonymous hegemony clue retirement".
        world.notifications.dismiss_by_type(COALITION_THREAT_TENSION)
        world.notifications.dismiss_by_type(COALITION_MURMURS)
    except Exception as exc:
        from backend.utils.debug import debug_print
        debug_print(
            f"[HEGEMONY] failed to emit balance_of_europe_shifted "
            f"({caller}) for {hegemon} at {round(float(share), 2)}: {exc}"
        )
        # Defensive: never block the ratification seam on a notify failure.
        return False

    # Update stored memory AFTER emission
    world.hegemony_signal_high_water = int(current_band)
    # Clear relaxation-aside dedupe on hegemon change
    if stored_hegemon != hegemon:
        world.hegemony_relaxation_bands_fired = set()
    world.hegemony_signal_hegemon = hegemon
    return True


def _emit_relaxation_aside(world) -> bool:
    """Downward-crossing relaxation-aside evaluator (§7.3 relaxation contract).

    Fires at most ONE quiet dispatch aside per turn when end-of-turn share
    is in a strictly lower band than stored high_water for the same
    hegemon, that lower band has not yet been recorded in
    `hegemony_relaxation_bands_fired`, and share is still >= 33%.

    On multi-band downward collapse (65% → 48%), emits the aside for
    the current (post-drop) label and records ALL crossed-out surfaced
    bands in the dedupe set so oscillation cannot re-fire.

    Returns True if an aside was emitted, False otherwise.

    Called ONCE per turn at end of `process_coalition_turn`, NOT on
    mid-turn crossings. Mid-turn oscillation (52 → 49 → 51 within the
    same turn) that ends in the starting band MUST NOT fire the aside
    or poison the dedupe set.

    TODO(Slice C-lite): build the formatted Talleyrand dispatch-aside
    copy in the dispatch pipeline; B-Hegemony just queues a dispatch
    event here so the footer text slot is reserved.
    """
    try:
        hegemon, share = _identify_max_bloc_share(world)
    except Exception as exc:
        from backend.utils.debug import debug_print
        debug_print(
            f"[HEGEMONY] relaxation identify failed on turn "
            f"{int(getattr(world, 'current_turn', 1) or 1)}: {exc}"
        )
        return False
    if hegemon is None or share < 0.33:
        return False
    stored_band = int(getattr(world, "hegemony_signal_high_water", 0) or 0)
    stored_hegemon = getattr(world, "hegemony_signal_hegemon", None)
    if stored_hegemon != hegemon:
        return False
    current_band = _hegemony_signal_band(share)
    if current_band >= stored_band:
        return False
    fired = set(getattr(world, "hegemony_relaxation_bands_fired", set()) or set())
    if current_band in fired:
        return False
    updated_fired = set(fired)
    # Record ALL crossed-out surfaced bands (current_band + 1 ... stored_band)
    # for the multi-band downward rule per §7.3.
    for b in range(current_band, stored_band):
        updated_fired.add(int(b))

    bloc_info = describe_hegemon_bloc(world, hegemon, share)
    label = bloc_info.get("bloc_label") or bloc_info.get("descriptive_label") or hegemon

    # Queue a dispatch event (footer aside, not rail notice, not popup).
    # TODO(Slice C-lite): add hegemony_beat_relaxation_* template family
    #   + owned dispatch-aside render path. For now we queue a typed
    #   event the dispatch builder can inspect.
    try:
        from backend.game_logic.dispatch import queue_dispatch_event
        queue_dispatch_event(
            world,
            "hegemony_relaxation_aside",
            {
                "hegemon": hegemon,
                "share": round(float(share), 2),
                "band": int(current_band),
                "label": label,
            },
            "always",
        )
    except Exception as exc:
        from backend.utils.debug import debug_print
        debug_print(
            f"[HEGEMONY] failed to queue relaxation aside for "
            f"{hegemon} at {round(float(share), 2)}: {exc}"
        )
        return False
    world.hegemony_relaxation_bands_fired = updated_fired
    return True


def describe_hegemon_bloc(world, hegemon: Optional[str], share: float) -> Dict:
    """Derived presentation helper. Returns `{bloc_label, descriptive_label,
    adjective, is_proper_bloc_name}` per COMMITMENTS_PRESENTATION_SPEC
    §8.1a.6.

    Presence contract:
    - `bloc_label` is non-empty (str from authored taxonomy) ONLY when
      `is_proper_bloc_name is True`, which requires `share >= 0.50`.
    - At `0.33 <= share < 0.50`, returns `bloc_label = None`,
      `is_proper_bloc_name = False`; `descriptive_label` is populated.
    - Below 33% the helper return is unspecified per §8.1a.6; surfaces
      should not call it.

    Consumers rendering headline or warning copy at the noticed band
    must fall through `bloc_label` (None) to `descriptive_label`; bare
    hegemon name is a last-resort fallback for unauthored hegemons only.
    """
    if hegemon is None:
        # Defensive: undefined per §8.1a.6 but keep structure consistent.
        return {
            "bloc_label": None,
            "descriptive_label": None,
            "adjective": None,
            "is_proper_bloc_name": False,
        }
    adjective = _BLOC_ADJECTIVES.get(hegemon, f"{hegemon}-led")
    descriptive_label = f"{adjective}-led alignment"
    if share >= 0.50:
        bloc_label = _BLOC_PROPER_NAMES.get(hegemon, f"{hegemon} Bloc")
        return {
            "bloc_label": bloc_label,
            "descriptive_label": descriptive_label,
            "adjective": adjective,
            "is_proper_bloc_name": True,
        }
    return {
        "bloc_label": None,
        "descriptive_label": descriptive_label,
        "adjective": adjective,
        "is_proper_bloc_name": False,
    }


# ════════════════════════════════════════════════════════════════
# §2a. THREAT ACCUMULATION
# ════════════════════════════════════════════════════════════════

def add_threat(world, amount: int, source_key: str) -> int:
    """Add threat from an aggressive action (§2a).

    Args:
        world: WorldState
        amount: Positive int to add
        source_key: e.g. "battle_win", "capital_capture", "war_declaration",
                    "hegemony_passive"

    Returns:
        New threat_level (clamped 0-100)
    """
    if amount <= 0:
        return int(world.threat_level)
    world.threat_level = int(min(100, max(0, world.threat_level + amount)))
    world.threat_sources_this_turn.append({
        "source": source_key,
        "amount": int(amount),
    })
    # B-Hegemony: transient per-turn flag backing the
    # `residual_pressure_active` anti-spam gate. Set True on any positive
    # threat increment; cleared at end-of-turn / ledger evaluation.
    setattr(world, "positive_threat_delta_this_turn", True)
    return int(world.threat_level)


def reduce_threat(world, amount: int, source_key: str) -> int:
    """Reduce threat from voluntary concessions (§2b voluntary).

    For things like releasing vassals or returning territory — NOT per-turn decay.

    Returns:
        New threat_level (clamped 0-100)
    """
    if amount <= 0:
        return int(world.threat_level)
    world.threat_level = int(min(100, max(0, world.threat_level - amount)))
    world.threat_sources_this_turn.append({
        "source": source_key,
        "amount": int(-amount),
    })
    return int(world.threat_level)


def _calculate_defensive_refusal_memory_threat(world) -> int:
    """Standing DG-4 threat from active defensive-refusal episodes.

    The current coalition scalar is France-targeted, so only refusals by the
    player nation feed it here. D2 can generalize this to per-target threat.
    """
    france = world.player_nation
    current_turn = int(getattr(world, "current_turn", 0))
    amount = 0
    for event in getattr(world, "event_log", []) or []:
        if event.get("type") != "call_to_arms_refused_defensive":
            continue
        if event.get("breaker") != france:
            continue
        expires = int(event.get("coalition_threat_expires_on_turn", 0) or 0)
        if expires and expires <= current_turn:
            continue
        victim = event.get("victim", "")
        if not victim:
            continue
        treaty_partners = [
            nation for nation in _get_all_nations(world)
            if nation not in (france, victim)
            and _get_diplo_state(world, nation, victim) in (
                "OPEN_BORDERS",
                "NON_AGGRESSION",
                "DEFENSIVE_ALLIANCE",
                "ALLIANCE",
                "VASSAL",
            )
        ]
        if treaty_partners:
            amount += 1
    return int(min(3, amount))


# ════════════════════════════════════════════════════════════════
# §2b. THREAT DECAY
# ════════════════════════════════════════════════════════════════

def _calculate_threat_decay(world) -> int:
    """Calculate per-turn threat decay (§2b).

    Formula: 1 base + 1 per peaceful non-vassal nation (cap 3) + CS bonus.
    """
    france = world.player_nation
    vassals = set(getattr(world, 'vassals', {}).keys())

    peace_nations = []
    for n in _get_all_nations(world):
        if n == france:
            continue  # Self-exclusion (§2b IMPORTANT note)
        if n in vassals:
            continue
        state = _get_diplo_state(world, france, n)
        if state in PEACEFUL_STATES:
            peace_nations.append(n)

    raw_decay = 1 + len(peace_nations)
    decay = min(raw_decay, DECAY_CAP)

    # Continental System bonus — separate, not subject to cap (§2b)
    cs_members = getattr(world, 'continental_system_members', [])
    if len(cs_members) >= 2:
        decay += 1

    return int(decay)


# ════════════════════════════════════════════════════════════════
# §3b. QUALIFYING NATIONS
# ════════════════════════════════════════════════════════════════

def qualifies_for_coalition(nation: str, world) -> bool:
    """Check if a nation qualifies for coalition membership (§3b).

    Qualifies if: relation < -10, not vassal, not already at war with France.
    """
    france = world.player_nation
    if nation == france:
        return False
    relation = _get_relation(world, france, nation)
    is_vassal = nation in getattr(world, 'vassals', {})
    already_at_war = _get_diplo_state(world, france, nation) == "WAR"
    return relation < -10 and not is_vassal and not already_at_war


def get_qualifying_nations(world) -> List[str]:
    """Get all nations that qualify for coalition membership."""
    return [n for n in _get_all_nations(world) if qualifies_for_coalition(n, world)]


def get_nations_at_war_with_france(world) -> List[str]:
    """Get all non-vassal nations currently at war with France."""
    france = world.player_nation
    vassals = set(getattr(world, 'vassals', {}).keys())
    result = []
    for n in _get_all_nations(world):
        if n == france or n in vassals:
            continue
        if _get_diplo_state(world, france, n) == "WAR":
            result.append(n)
    return result


# ════════════════════════════════════════════════════════════════
# §4a. LEADER SELECTION
# ════════════════════════════════════════════════════════════════

def coalition_leadership_score(nation: str, world, european_power: Optional[int] = None) -> int:
    """Calculate leadership score for a nation (§4a + §7.4).

    Base: `military//1000 + hostility + authority`. B-Hegemony adds a
    `bloc_share_against` term — the fraction of Continental power this
    nation's bloc commands, weighted ×50. Naturally surfaces the largest
    non-hegemon power as coalition leader.

    Note the `france` hostility anchor stays France-coupled in v0.1 per
    §7.4 caveat; D2 Coalition Generalization will generalize.

    Args:
        nation: the candidate nation
        world: WorldState
        european_power: optional precomputed total power. Computed once per
            scoring pass at the caller level (see `select_coalition_leader`)
            to avoid re-computing per candidate.
    """
    france = world.player_nation
    military = sum(m.strength for m in world.marshals.values()
                   if m.nation == nation and m.strength > 0) // 1000
    hostility = abs(_get_relation(world, france, nation))
    authority = getattr(world, 'nation_authority', {}).get(nation, 60)
    score = int(military + hostility + authority)

    # B-Hegemony §7.4: bloc_share_against additive term
    if european_power is None:
        european_power = sum(power_score(n, world) for n in world.get_active_nations())
    if european_power > 0:
        bloc_share = bloc_power(nation, world) / european_power
        score += int(bloc_share * 50)

    return int(score)


def select_coalition_leader(members: List[str], world) -> str:
    """Select coalition leader from members (§4a).

    Highest leadership score. Tiebreak: most marshals, then alphabetical.
    """
    if not members:
        return ""

    # Compute european_power ONCE per scoring pass (§7.4 caller-level helper)
    european_power = sum(power_score(n, world) for n in world.get_active_nations())

    def _sort_key(nation):
        score = coalition_leadership_score(nation, world, european_power=european_power)
        marshal_count = sum(1 for m in world.marshals.values()
                           if m.nation == nation and m.strength > 0)
        # Negative for descending sort, nation for ascending alpha tiebreak
        return (-score, -marshal_count, nation)

    return sorted(members, key=_sort_key)[0]


# ════════════════════════════════════════════════════════════════
# §4c. STRATEGIC POSTURE
# ════════════════════════════════════════════════════════════════

def calculate_coalition_war_score(world) -> int:
    """Calculate weighted-average coalition war score (§4c).

    Weighted by each member's current army size.
    """
    coalition = world.active_coalition
    if not coalition:
        return 0

    france = world.player_nation
    members = coalition.get("members", [])
    total_weight = 0
    weighted_sum = 0

    for member in members:
        army_size = sum(m.strength for m in world.marshals.values()
                        if m.nation == member and m.strength > 0)
        from backend.game_logic.diplomacy import get_war_score_for
        france_ws = get_war_score_for(world, france, member)
        # Coalition wants NEGATIVE France scores (positive = coalition winning)
        weighted_sum += (-france_ws) * army_size
        total_weight += army_size

    if total_weight == 0:
        return 0

    return int(weighted_sum // total_weight)


def get_coalition_posture(world) -> str:
    """Determine coalition strategic posture (§4c).

    Returns: "aggressive", "defensive", or "cautious"
    """
    coalition = world.active_coalition
    if not coalition:
        return "defensive"

    coalition_ws = calculate_coalition_war_score(world)
    leader = coalition.get("leader", "")

    # Get leader personality from their diplomat
    leader_personality = _get_leader_personality(leader, world)

    # Leader personality overrides (§4c)
    if leader_personality in ("aggressive", "reckless"):
        # Aggressive leader: stays aggressive until war score < -20
        if coalition_ws >= -20:
            return "aggressive"
        else:
            return "cautious"
    elif leader_personality in ("cautious", "professional"):
        # Cautious leader: needs war score > +30 for aggressive
        if coalition_ws > 30:
            return "aggressive"
        elif coalition_ws >= -10:
            return "defensive"
        else:
            return "cautious"

    # Default thresholds
    if coalition_ws > 10:
        return "aggressive"
    elif coalition_ws >= -10:
        return "defensive"
    else:
        return "cautious"


def _get_leader_personality(nation: str, world) -> str:
    """Get the diplomatic personality of a nation's representative."""
    diplomats = getattr(world, 'diplomats', {})
    diplomat = diplomats.get(nation)
    if diplomat:
        return getattr(diplomat, 'personality', 'loyalist')
    return "loyalist"


# ════════════════════════════════════════════════════════════════
# §4e. BRITISH SUBSIDY
# ════════════════════════════════════════════════════════════════

def get_british_subsidy_recipient(world) -> Optional[str]:
    """Find the coalition partner to receive British subsidy (§4e).

    Lowest relation to Britain, minimum > -20, Britain gold > 500.
    Returns nation name or None.
    """
    coalition = world.active_coalition
    if not coalition:
        return None

    members = coalition.get("members", [])
    if "Britain" not in members:
        return None

    # Check Britain has enough gold
    britain_gold = world.nation_gold.get("Britain", 0)
    if britain_gold <= 500:
        return None

    # Find partner with lowest relation to Britain (min > -20)
    best = None
    best_relation = 200  # Higher than any possible relation

    for member in members:
        if member == "Britain":
            continue
        rel = _get_relation(world, "Britain", member)
        if rel > -20 and rel < best_relation:
            best = member
            best_relation = rel

    return best


def _process_british_subsidy(world) -> List[Dict]:
    """Process British subsidy payment (§4e). 200g/turn to lowest-relation partner."""
    events = []
    recipient = get_british_subsidy_recipient(world)
    if not recipient:
        return events

    subsidy = 200
    britain_gold = world.nation_gold.get("Britain", 0)
    if britain_gold < subsidy:
        return events

    world.nation_gold["Britain"] = int(britain_gold - subsidy)
    recipient_gold = world.nation_gold.get(recipient, 0)
    world.nation_gold[recipient] = int(recipient_gold + subsidy)

    # +5 relation between Britain and recipient
    world.modify_nation_relation("Britain", recipient, 5)

    events.append({
        "type": "british_subsidy",
        "recipient": recipient,
        "amount": int(subsidy),
        "message": f"Britain subsidizes {recipient} with {subsidy} gold.",
    })
    return events


# ════════════════════════════════════════════════════════════════
# §5b. CONVERGENCE BIAS
# ════════════════════════════════════════════════════════════════

def get_convergence_bias(posture: str) -> int:
    """Get convergence bias for P7 movement scoring (§5b).

    Returns score bonus for regions adjacent to French territory.
    """
    if posture == "aggressive":
        return 12
    elif posture == "defensive":
        return 4
    elif posture == "cautious":
        return 0
    return 8  # Default


# ════════════════════════════════════════════════════════════════
# §5c. HISTORICAL FRICTION
# ════════════════════════════════════════════════════════════════

def get_coalition_friction(nation_a: str, nation_b: str, world) -> float:
    """Get friction multiplier between coalition members (§5c).

    Returns 1.0 (full coordination) to 0.25 (near-hostile allies).
    Caller must int() the final result per Golden Rule #2.
    """
    if nation_a == nation_b:
        return 1.0

    mutual_relation = _get_relation(world, nation_a, nation_b)
    if mutual_relation >= 30:
        return 1.0
    elif mutual_relation >= 0:
        return 0.75
    elif mutual_relation >= -20:
        return 0.5
    else:
        return 0.25


# ════════════════════════════════════════════════════════════════
# §6a. COALITION LOYALTY PENALTY
# ════════════════════════════════════════════════════════════════

def get_coalition_loyalty_penalty(nation: str, world) -> int:
    """Get coalition loyalty penalty for acceptance formula (§6a).

    penalty = min(-15 + war_exhaustion // 10, 0)
    If target's relation with coalition leader < +10: halved (§6c wedge).

    Returns negative int (0 or less).
    """
    coalition = world.active_coalition
    if not coalition:
        return 0

    if nation not in coalition.get("members", []):
        return 0

    we = world.war_exhaustion.get(nation, 0)
    penalty = min(COALITION_LOYALTY_BASE + we // 10, 0)

    # §6c: Diplomatic wedge — halve penalty if target dislikes leader
    leader = coalition.get("leader", "")
    if leader and leader != nation:
        leader_relation = _get_relation(world, nation, leader)
        if leader_relation < 10:
            penalty = penalty // 2  # Halve (rounds toward zero)

    return int(penalty)


# ════════════════════════════════════════════════════════════════
# §6b. WAR EXHAUSTION FROM BATTLE
# ════════════════════════════════════════════════════════════════

def add_war_exhaustion_from_battle(nation: str, casualties: int, world) -> int:
    """Add war exhaustion from battle casualties (§10a).

    +casualties // 1000, capped at +20 per battle.
    Returns new war exhaustion for the nation.
    """
    we_gain = min(casualties // 1000, WAR_EXHAUSTION_BATTLE_CAP)
    if we_gain <= 0:
        return world.war_exhaustion.get(nation, 0)

    current = world.war_exhaustion.get(nation, 0)
    new_val = min(current + we_gain, WAR_EXHAUSTION_MAX)
    world.war_exhaustion[nation] = int(new_val)

    # S4: Dispatch when WE crosses thresholds
    _WE_THRESHOLDS = [20, 40, 60, 80]
    dispatched = world.we_dispatched_thresholds
    last_threshold = dispatched.get(nation, 0)
    for threshold in _WE_THRESHOLDS:
        if new_val >= threshold > current and threshold > last_threshold:
            from backend.game_logic.dispatch import queue_dispatch_event
            queue_dispatch_event(world, "diplomatic_we_threshold",
                                {"nation": nation, "we": int(new_val), "threshold": threshold},
                                "always")
            dispatched[nation] = threshold
            break

    return int(new_val)


def add_coalition_shock(defeated_nation: str, world) -> None:
    """Add +5 WE to other coalition members when one is defeated (§6b)."""
    coalition = world.active_coalition
    if not coalition:
        return

    if defeated_nation not in coalition.get("members", []):
        return

    for member in coalition["members"]:
        if member == defeated_nation:
            continue
        current = world.war_exhaustion.get(member, 0)
        world.war_exhaustion[member] = int(min(current + 5, WAR_EXHAUSTION_MAX))


# ════════════════════════════════════════════════════════════════
# §3e. COALITION FORMATION
# ════════════════════════════════════════════════════════════════

def form_coalition(qualifying_nations: List[str], world) -> Dict:
    """Form a coalition against France (§3e).

    qualifying_nations: Nations that meet §3b criteria (will declare war).
    Nations already at war join automatically.

    Returns dict with coalition info and events.
    """
    france = world.player_nation

    # 1. Identify all members
    already_at_war = get_nations_at_war_with_france(world)
    new_belligerents = [n for n in qualifying_nations if n not in already_at_war]
    all_members = list(set(already_at_war + qualifying_nations))

    # Must have at least 1 qualifying nation (not already at war)
    # AND at least 2 total members
    if not qualifying_nations or len(all_members) < 2:
        return {"success": False, "message": "Insufficient nations for coalition."}

    # 2. Apply war declarations for new belligerents (lazy import to avoid circular)
    from backend.game_logic.diplomacy import declare_war
    war_events = []
    for nation in new_belligerents:
        result = declare_war(world, nation, france)
        if result.get("success"):
            war_events.append(result)

    # Coalition wars don't add threat — declare_war only adds threat
    # when France is the aggressor, and here the coalition members declare.

    # EC-2: Void any in-transit proposal to a nation joining the coalition
    pit = getattr(world, 'proposal_in_transit', None)
    voided_proposal_nation = None
    if pit:
        pit_target = pit.get("target", "")
        if pit_target in all_members:
            voided_proposal_nation = pit_target
            world.proposal_in_transit = None
            # Restore Talleyrand if he was carrying this proposal
            if getattr(world, 'talleyrand_state', '') == "IN_TRANSIT":
                mission = getattr(world, 'active_diplomatic_mission', None)
                if mission and not mission.get("completed"):
                    world.talleyrand_state = "ON_MISSION"
                    mission["paused"] = False
                else:
                    world.talleyrand_state = "IDLE"
            # FINAL-1: Refund DP spent on the voided proposal (dp_cost stored at top level)
            dp_cost = pit.get("dp_cost", 0)
            if dp_cost > 0:
                world.diplomatic_points = getattr(world, 'diplomatic_points', 0) + int(dp_cost)

    # 3. United cause: +10 relation between all coalition members
    for i, m1 in enumerate(all_members):
        for m2 in all_members[i + 1:]:
            world.modify_nation_relation(m1, m2, 10)

    # 4. Select leader and determine posture
    leader = select_coalition_leader(all_members, world)
    world.coalition_count += 1

    # 5. Build coalition name (§3f)
    ordinal = _ORDINALS.get(world.coalition_count, f"{world.coalition_count}th")
    if world.coalition_count == 1:
        name = f"The {leader} Coalition"
    else:
        name = f"The {ordinal} {leader} Coalition"

    # 6. Set active coalition
    world.active_coalition = {
        "id": f"coalition_{world.current_turn}",
        "name": name,
        "leader": leader,
        "members": sorted(all_members),
        "formed_turn": int(world.current_turn),
        "strategic_posture": "defensive",  # Will be updated immediately
        "posture_last_updated": int(world.current_turn),
    }

    # Clear brewing state
    world.coalition_brewing = None

    # R51 + R12C: Void pending/queued dialogues targeting coalition members
    world.dialogue_manager.remove_matching(
        lambda d: d.get("target_nation", "") in all_members
    )

    # Update posture based on current war scores
    posture = get_coalition_posture(world)
    world.active_coalition["strategic_posture"] = posture
    world.active_coalition["posture_last_updated"] = int(world.current_turn)

    # 7. Calculate combined strength for popup
    combined_strength = sum(
        m.strength for m in world.marshals.values()
        if m.nation in all_members and m.strength > 0
    )

    # R84: Dismiss superseded TENSION/MURMURS notifications on coalition formation
    world.notifications.dismiss_by_type(COALITION_THREAT_TENSION)
    world.notifications.dismiss_by_type(COALITION_MURMURS)

    # 8. Notification
    world.notifications.add(create_notification(
        COALITION_DECLARED,
        NotificationPriority.CRITICAL,
        f"{name} Declared!",
        f"{name} has declared war. Leader: {leader}. "
        f"Members: {', '.join(sorted(all_members))}. "
        f"Combined strength: {int(combined_strength):,}.",
        int(world.current_turn),
        details={
            "coalition_name": name,
            "leader": leader,
            "members": sorted(all_members),
            "posture": posture,
            "combined_strength": int(combined_strength),
        },
    ))

    # 9. Log event
    world.log_event({
        "type": "coalition_declared",
        "coalition_name": name,
        "leader": leader,
        "members": sorted(all_members),
        "posture": posture,
        "threat_level": int(world.threat_level),
    })

    # R83: Dispatch event for coalition formation
    from backend.game_logic.dispatch import queue_dispatch_event
    queue_dispatch_event(world, "diplomatic_coalition_formed", {
        "member_list": ", ".join(sorted(all_members)),
    }, "always")

    # EC-2: Log voided proposal
    if voided_proposal_nation:
        world.log_event({
            "type": "proposal_voided_by_coalition",
            "target": voided_proposal_nation,
            "message": f"Envoy to {voided_proposal_nation} recalled — they joined the coalition.",
        })

    # 10. Build legacy coalition popup payload for result consumers only.
    # The live UI now uses the persistent notification rail instead of the
    # popup queue, so do not occupy a popup slot with this informational event.
    member_details = []
    for m in sorted(all_members):
        m_strength = sum(
            marshal.strength for marshal in world.marshals.values()
            if marshal.nation == m and marshal.strength > 0
        )
        m_we = int(world.war_exhaustion.get(m, 0))
        member_details.append({
            "nation": m,
            "strength_display": f"{int(m_strength):,}",
            "war_exhaustion": int(m_we),
        })
    coalition_popup = {
        "coalition_name": name,
        "leader": leader,
        "posture": posture,
        "members": member_details,
        "combined_strength_display": f"{int(combined_strength):,}",
        "threat_level": int(world.threat_level),
    }

    result = {
        "success": True,
        "coalition_name": name,
        "leader": leader,
        "members": sorted(all_members),
        "posture": posture,
        "combined_strength": int(combined_strength),
        "new_belligerents": new_belligerents,
        "war_events": war_events,
        "coalition_popup": coalition_popup,
    }
    if voided_proposal_nation:
        result["voided_proposal"] = voided_proposal_nation
    return result


# ════════════════════════════════════════════════════════════════
# §7. DISSOLUTION
# ════════════════════════════════════════════════════════════════

def check_dissolution(world) -> Optional[str]:
    """Check if active coalition should dissolve (§7a).

    Returns dissolution reason string, or None if coalition persists.
    """
    coalition = world.active_coalition
    if not coalition:
        return None

    france = world.player_nation
    members = coalition.get("members", [])

    # Check: < 2 members
    active_members = [m for m in members if _get_diplo_state(world, france, m) == "WAR"]
    if len(active_members) < 2:
        return "insufficient_members"

    # Check: threat below 20
    if world.threat_level < DISSOLUTION_THREAT_THRESHOLD:
        return "low_threat"

    return None


def dissolve_coalition(world, reason: str) -> List[Dict]:
    """Dissolve the active coalition (§7b).

    Returns list of tactical events.
    """
    events = []
    coalition = world.active_coalition
    if not coalition:
        return events

    name = coalition.get("name", "The Coalition")

    # Clear coalition state
    world.active_coalition = None
    world.we_dispatched_thresholds = {}

    # R84: Dismiss superseded COALITION_DECLARED notification on dissolution
    world.notifications.dismiss_by_type(COALITION_DECLARED)

    # Start cooldown (§7c)
    world.coalition_cooldown = COALITION_COOLDOWN_TURNS

    # Notification
    world.notifications.add(create_notification(
        COALITION_DISSOLVED,
        NotificationPriority.NORMAL,
        "Coalition Dissolved",
        f"{name} has dissolved. {reason.replace('_', ' ').title()}.",
        int(world.current_turn),
    ))

    # Log event
    world.log_event({
        "type": "coalition_dissolved",
        "coalition_name": name,
        "reason": reason,
    })

    events.append({
        "type": "coalition_dissolved",
        "message": f"{name} has dissolved.",
        "reason": reason,
    })

    # R83: Dispatch event for coalition dissolution
    from backend.game_logic.dispatch import queue_dispatch_event
    queue_dispatch_event(world, "diplomatic_coalition_dissolved", {}, "always")

    return events


def remove_coalition_member(nation: str, world) -> List[Dict]:
    """Remove a nation from the active coalition (e.g., separate peace).

    Handles leader transition (§4b) and dissolution check.
    Returns list of tactical events.
    """
    events = []
    coalition = world.active_coalition
    if not coalition:
        return events

    members = coalition.get("members", [])
    if nation not in members:
        return events

    # Remove member
    members.remove(nation)
    coalition["members"] = members

    # Notification
    world.notifications.add(create_notification(
        COALITION_MEMBER_PEACED,
        NotificationPriority.NORMAL,
        f"{nation} Left Coalition",
        f"{nation} has signed a separate peace and left {coalition.get('name', 'the coalition')}.",
        int(world.current_turn),
    ))

    # §4b: -15 relation with remaining members ("betrayal")
    for member in members:
        world.modify_nation_relation(nation, member, -15)

    # Log event
    world.log_event({
        "type": "coalition_member_left",
        "nation": nation,
        "coalition_name": coalition.get("name", ""),
    })

    events.append({
        "type": "coalition_member_left",
        "message": f"{nation} has left the coalition.",
        "nation": nation,
    })

    # §4b: Leader transition
    if nation == coalition.get("leader") and members:
        new_leader = select_coalition_leader(members, world)
        coalition["leader"] = new_leader
        # New leader sets posture
        posture = get_coalition_posture(world)
        coalition["strategic_posture"] = posture
        coalition["posture_last_updated"] = int(world.current_turn)
        # -5 relation between remaining members ("alliance frays")
        for i, m1 in enumerate(members):
            for m2 in members[i + 1:]:
                world.modify_nation_relation(m1, m2, -5)
        events.append({
            "type": "coalition_leader_changed",
            "message": f"{new_leader} now leads the coalition.",
            "new_leader": new_leader,
        })

    # Check dissolution
    reason = check_dissolution(world)
    if reason:
        events.extend(dissolve_coalition(world, reason))

    return events


# ════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════

def is_coalition_member(nation: str, world) -> bool:
    """Check if a nation is in the active coalition."""
    coalition = world.active_coalition
    if not coalition:
        return False
    return nation in coalition.get("members", [])


def is_coalition_active(world) -> bool:
    """Check if any coalition is currently active."""
    return world.active_coalition is not None


def get_threat_tier(threat_level: int) -> str:
    """Get the threat tier name for a given threat level."""
    if threat_level >= THREAT_BREWING_MIN:
        return "Brewing"
    elif threat_level >= THREAT_MURMURS_MIN:
        return "Murmurs"
    elif threat_level >= THREAT_TENSION_MIN:
        return "Tension"
    else:
        return "Calm"


# ════════════════════════════════════════════════════════════════
# MASTER PER-TURN FUNCTION
# ════════════════════════════════════════════════════════════════

def process_coalition_turn(world) -> List[Dict]:
    """Master per-turn coalition processing (§3c processing order).

    Called from WorldState.advance_turn() after vassal processing,
    before income phase.

    Processing order:
    1. Passive threat from region control
    2. Threat decay
    3. War exhaustion per-turn changes
    4. British subsidy
    5. Cooldown decrement
    6. If brewing: decrement countdown, check cancel/expiry/instant
    7. If not brewing: check threshold (≥60 → brew, ≥80 → instant, ≥90 → override cooldown)
    8. Update posture if coalition active
    9. Dissolution check

    Returns list of tactical events.
    """
    events = []
    france = world.player_nation

    # B-Hegemony (§7.3): reset the per-turn positive-threat-delta flag at
    # the START of the coalition turn. Sources that follow may set it True.
    world.positive_threat_delta_this_turn = False

    # ────────── 1. Passive threat from region control (§2a) ──────────
    france_regions = sum(1 for r in world.regions.values()
                        if r.controller == france)
    total_regions = len(world.regions)

    if total_regions > 0:
        control_pct = france_regions / total_regions
        if control_pct > 0.80:
            add_threat(world, 3, "region_control_80")
        elif control_pct > 0.70:
            add_threat(world, 2, "region_control_70")
        elif control_pct > 0.60:
            add_threat(world, 1, "region_control_60")

    # ────────── 1b. B-Hegemony passive pressure (§7.3) ──────────
    # Per-turn passive contribution from bloc-share dominance. Gates at
    # 33%+; returns `{hegemon: increment}` or `{}`. In v0.1 the
    # threat_level scalar remains France-targeted, so if the hegemon is
    # anyone other than `world.player_nation`, we emit a debug log for
    # telemetry and skip the `add_threat` call. D2 Coalition Generalization
    # will generalize the scalar to per-target later.
    hegemony_pressure = _calculate_hegemony_pressure(world)
    if hegemony_pressure:
        hegemon, increment = next(iter(hegemony_pressure.items()))
        if hegemon == france:
            add_threat(world, int(increment), "hegemony_passive")
        else:
            from backend.utils.debug import debug_print
            debug_print(
                f"[HEGEMONY] non-France hegemon {hegemon} at share "
                f"{bloc_power(hegemon, world) / max(1, sum(power_score(n, world) for n in world.get_active_nations())):.2f}; "
                f"skipping add_threat (v0.1 France-targeted scalar, D2 will generalize)"
            )

    # ────────── 2. Threat decay (§2b) ──────────
    refusal_memory_threat = _calculate_defensive_refusal_memory_threat(world)
    if refusal_memory_threat > 0:
        add_threat(world, refusal_memory_threat, "defensive_refusal_memory")

    decay = _calculate_threat_decay(world)
    if decay > 0:
        old_threat = world.threat_level
        world.threat_level = int(max(0, world.threat_level - decay))
        actual_decay = old_threat - world.threat_level
        if actual_decay > 0:
            world.threat_sources_this_turn.append({
                "source": "decay",
                "amount": int(-actual_decay),
            })

    # ────────── 3. War exhaustion per-turn (§10a) ──────────
    for nation in _get_all_nations(world):
        if nation == france:
            continue
        state = _get_diplo_state(world, france, nation)
        current_we = world.war_exhaustion.get(nation, 0)
        if state == "WAR":
            new_we = min(current_we + 8, WAR_EXHAUSTION_MAX)  # R11: was +5
        else:
            new_we = max(current_we - 5, 0)
        if new_we != current_we:
            world.war_exhaustion[nation] = int(new_we)

    # ────────── 3b. Coalition member relation friction (R11) ──────────
    if world.active_coalition:
        members = world.active_coalition.get("members", [])
        for i, member_a in enumerate(members):
            for member_b in members[i + 1:]:
                world.modify_nation_relation(member_a, member_b, -2)

    # ────────── 4. British subsidy (§4e) ──────────
    subsidy_events = _process_british_subsidy(world)
    events.extend(subsidy_events)

    # ────────── 5. Cooldown decrement (§7c) ──────────
    if world.coalition_cooldown > 0:
        world.coalition_cooldown -= 1
        if world.coalition_cooldown == 0:
            world.notifications.add(create_notification(
                COALITION_COOLDOWN_ENDED,
                NotificationPriority.NORMAL,
                "Coalition Cooldown Ended",
                "A new coalition may form if threat remains high.",
                int(world.current_turn),
            ))

    # ────────── 6. Brewing check (§3c) ──────────
    if world.coalition_brewing and not world.active_coalition:
        brewing = world.coalition_brewing
        qualifying = get_qualifying_nations(world)

        # Check cancellation (momentum rule §3c)
        if world.threat_level < BREWING_CANCEL_THRESHOLD or len(qualifying) == 0:
            world.coalition_brewing = None
            world.notifications.dismiss_by_type(COALITION_BREWING)
            events.append({
                "type": "coalition_brewing_cancelled",
                "message": "The coalition effort has collapsed.",
            })
            world.log_event({"type": "coalition_brewing_cancelled"})
        else:
            # Decrement countdown
            brewing["turns_remaining"] = brewing.get("turns_remaining", 1) - 1
            brewing["qualifying_nations"] = qualifying

            # Check instant override (§3d: threat ≥80 during brewing)
            if world.threat_level >= THREAT_INSTANT_MIN:
                result = form_coalition(qualifying, world)
                if result.get("success"):
                    events.append({
                        "type": "coalition_declared",
                        "message": f"{result['coalition_name']} declared! (Instant — threat {world.threat_level})",
                        "coalition": result,
                    })
            elif brewing["turns_remaining"] <= 0:
                # Countdown expired — declare
                result = form_coalition(qualifying, world)
                if result.get("success"):
                    events.append({
                        "type": "coalition_declared",
                        "message": f"{result['coalition_name']} declared!",
                        "coalition": result,
                    })
                else:
                    # Not enough nations — cancel
                    world.coalition_brewing = None
                    world.notifications.dismiss_by_type(COALITION_BREWING)
            else:
                # Update notification with remaining turns
                world.notifications.dismiss_by_type(COALITION_BREWING)
                world.notifications.add(create_notification(
                    COALITION_BREWING,
                    NotificationPriority.CRITICAL,
                    f"Coalition Brewing — {int(brewing['turns_remaining'])} turn(s)",
                    f"Nations consulting: {', '.join(qualifying)}. "
                    f"{int(brewing['turns_remaining'])} turns until declaration.",
                    int(world.current_turn),
                    details={
                        "qualifying_nations": qualifying,
                        "turns_remaining": int(brewing["turns_remaining"]),
                    },
                ))

    # ────────── 7. Threshold check (if not brewing, no active coalition) ──────────
    elif not world.active_coalition:
        threat = world.threat_level

        # §7c: Cooldown override at 90+
        if threat >= THREAT_OVERRIDE_COOLDOWN_MIN and world.coalition_cooldown > 0:
            world.coalition_cooldown = 0  # Override

        # Can only form if no cooldown
        if world.coalition_cooldown <= 0:
            qualifying = get_qualifying_nations(world)

            if threat >= THREAT_INSTANT_MIN and qualifying:
                # §3d: Instant declaration at 80+
                result = form_coalition(qualifying, world)
                if result.get("success"):
                    events.append({
                        "type": "coalition_declared",
                        "message": f"{result['coalition_name']} declared! (Instant — threat {threat})",
                        "coalition": result,
                    })
            elif threat >= THREAT_BREWING_MIN and qualifying:
                # §3c: Start brewing at 60+
                world.coalition_brewing = {
                    "qualifying_nations": qualifying,
                    "turns_remaining": BREWING_COUNTDOWN,
                    "started_turn": int(world.current_turn),
                    "threat_at_start": int(threat),
                }
                world.notifications.add(create_notification(
                    COALITION_BREWING,
                    NotificationPriority.CRITICAL,
                    f"Coalition Brewing — {BREWING_COUNTDOWN} turns",
                    f"A coalition is brewing against France. "
                    f"Nations consulting: {', '.join(qualifying)}. "
                    f"{BREWING_COUNTDOWN} turns until declaration.",
                    int(world.current_turn),
                    details={
                        "qualifying_nations": qualifying,
                        "turns_remaining": BREWING_COUNTDOWN,
                    },
                ))
                world.log_event({
                    "type": "coalition_brewing_started",
                    "qualifying_nations": qualifying,
                    "threat_level": int(threat),
                })
                events.append({
                    "type": "coalition_brewing_started",
                    "message": f"A coalition is brewing! {', '.join(qualifying)} are consulting.",
                    "qualifying_nations": qualifying,
                    "turns_remaining": BREWING_COUNTDOWN,
                })

                # R83: Dispatch event for coalition brewing
                from backend.game_logic.dispatch import queue_dispatch_event
                queue_dispatch_event(world, "diplomatic_coalition_brewing", {}, "always")

        # Threat tier notifications (regardless of cooldown)
        _check_threat_notifications(world)

    # ────────── 8. Update posture if coalition active (§4c) ──────────
    if world.active_coalition:
        posture = get_coalition_posture(world)
        world.active_coalition["strategic_posture"] = posture
        world.active_coalition["posture_last_updated"] = int(world.current_turn)

    # ────────── 9. Dissolution check (§7a) ──────────
    if world.active_coalition:
        reason = check_dissolution(world)
        if reason:
            events.extend(dissolve_coalition(world, reason))

    # ────────── 10. B-Hegemony end-of-turn hooks (§7.3) ──────────
    # Run ONCE per turn, AFTER all state mutations, to catch end-of-turn
    # share changes that didn't pass through a ratification seam.
    try:
        _check_hegemony_band_crossing(world, caller="process_coalition_turn:end")
    except Exception as exc:
        from backend.utils.debug import debug_print
        debug_print(
            f"[HEGEMONY] end-of-turn band-crossing check failed on "
            f"turn {int(getattr(world, 'current_turn', 1) or 1)}: {exc}"
        )
    # Relaxation aside — evaluates ONCE per turn per §7.3 contract.
    try:
        _emit_relaxation_aside(world)
    except Exception as exc:
        from backend.utils.debug import debug_print
        debug_print(
            f"[HEGEMONY] end-of-turn relaxation check failed on "
            f"turn {int(getattr(world, 'current_turn', 1) or 1)}: {exc}"
        )
    # Reset memory on drop below 33%.
    try:
        hegemon, share = _identify_max_bloc_share(world)
        if hegemon is None or share < 0.33:
            world.hegemony_signal_high_water = 0
            world.hegemony_signal_hegemon = None
            world.hegemony_relaxation_bands_fired = set()
    except Exception as exc:
        from backend.utils.debug import debug_print
        debug_print(
            f"[HEGEMONY] end-of-turn reset-below-33 check failed on "
            f"turn {int(getattr(world, 'current_turn', 1) or 1)}: {exc}"
        )

    return events


def _check_threat_notifications(world) -> None:
    """Emit threat tier notifications when thresholds are crossed.

    B-Hegemony: the legacy anonymous `"Diplomatic Tension"` /
    `"European Courts Concerned"` clues are retired for hegemony-driven
    share changes per §7.3 "Legacy anonymous hegemony clue retirement".
    We keep the tier emit sites for PURE event-threat accrual (battles,
    captures, vassalizations without hegemony crossings), but suppress
    the tier line on the same turn a `balance_of_europe_shifted` beat
    fired — those anonymous clues would be duplicate clues for the
    named-diplomat beat.
    """
    threat = world.threat_level

    # B-Hegemony: suppress the legacy tier line on the same turn a
    # named `balance_of_europe_shifted` beat fired. This is the cleanest
    # cut: the two notification families are still allowed to exist, but
    # one turn's share-crossing cannot produce both.
    current_turn = int(getattr(world, "current_turn", 0))
    balance_fired_this_turn = any(
        n.get("type") == BALANCE_OF_EUROPE_SHIFTED
        and int(n.get("turn_created", 0) or 0) == current_turn
        for n in world.notifications.get_pending()
    )

    if threat >= THREAT_MURMURS_MIN:
        # Dismiss tension, add murmurs (persistent until < 30)
        world.notifications.dismiss_by_type(COALITION_THREAT_TENSION)
        # Only add if not already present AND no balance beat this turn
        existing = [n for n in world.notifications.get_pending()
                    if n.get("type") == COALITION_MURMURS]
        if not existing and not balance_fired_this_turn:
            world.notifications.add(create_notification(
                COALITION_MURMURS,
                NotificationPriority.HIGH,
                "European Courts Concerned",
                f"Threat level: {int(threat)}. The courts of Europe grow restless.",
                int(world.current_turn),
            ))
    elif threat >= THREAT_TENSION_MIN:
        # Dismiss murmurs if threat dropped
        world.notifications.dismiss_by_type(COALITION_MURMURS)
        existing = [n for n in world.notifications.get_pending()
                    if n.get("type") == COALITION_THREAT_TENSION]
        if not existing and not balance_fired_this_turn:
            world.notifications.add(create_notification(
                COALITION_THREAT_TENSION,
                NotificationPriority.HIGH,
                "Diplomatic Tension",
                f"Threat level: {int(threat)}. The courts are uneasy.",
                int(world.current_turn),
            ))
    else:
        # Calm — dismiss all threat notifications
        world.notifications.dismiss_by_type(COALITION_THREAT_TENSION)
        world.notifications.dismiss_by_type(COALITION_MURMURS)
