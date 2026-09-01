"""
Authority Tracker for Project Sovereign (Phase 2 - Disobedience)

Tracks Napoleon's perceived authority to prevent "always trust marshals" exploit.
If player always defers to marshals, authority erodes and marshals become less obedient.

V2b additions:
- Enriched recent_responses format: List[Dict] with {"choice": str, "turn": int}
- check_excessive_trust(): Ratio-based penalty replacing old count-based system
- modify_authority(): Clamped 0-100 setter for external callers
"""

from typing import Optional, Dict, List


class AuthorityTracker:
    """
    Tracks Napoleon's perceived authority.

    Prevents the "sycophancy exploit" where always trusting marshals
    becomes the optimal strategy. Instead:
    - Always trusting = authority drops = marshals less obedient
    - Always insisting = trust drops = marshals resent you
    - Balanced approach = healthy authority and trust

    Threshold Events:
    - Authority 70: "Whispers of Weakness" - minor warning
    - Authority 50: "Loss of Respect" - marshals start testing limits
    - Authority 30: "Emperor in Name Only" - open challenges

    Authority tiers for defiance (SEPARATE from get_obedience_modifier/get_severity_modifier):
    - >= 80: Strong leader (-10% defiance chance)
    - 50-79: Normal (0% defiance modifier)
    - < 50: Weak leader (+10% defiance chance)
    """

    # Authority threshold events
    THRESHOLD_EVENTS = {
        70: {
            'name': 'Whispers of Weakness',
            'description': 'Your marshals begin to question whether you truly command, or merely suggest.',
            'effect': 'trust_gains_reduced',
        },
        50: {
            'name': 'Loss of Respect',
            'description': 'The marshals no longer fear your displeasure. They debate openly.',
            'effect': 'obedience_reduced',
        },
        30: {
            'name': 'Emperor in Name Only',
            'description': 'Your commands are treated as suggestions. The marshals rule themselves.',
            'effect': 'severe_obedience_penalty',
        },
    }

    def __init__(self):
        """Initialize authority tracker."""
        self.authority: int = 100  # Napoleon starts fully authoritative
        # V2b: Enriched format — List[Dict] with {"choice": str, "turn": int}
        # Backward compat: from_dict handles bare strings (legacy saves)
        self.recent_responses: List[Dict] = []
        self._crossed_thresholds: List[int] = []  # Track which events have triggered

    def record_response(self, choice: str, current_turn: int = 0) -> Optional[Dict]:
        """
        Record player response to objection.

        V2b: Accepts current_turn for time-windowed penalty calculation.
        Stores enriched format {"choice": str, "turn": int}.

        Args:
            choice: 'trust', 'insist', or 'compromise'
            current_turn: Current game turn number (default 0 for backward compat)

        Returns:
            Event dict if threshold crossed, None otherwise
        """
        if choice not in ('trust', 'insist', 'compromise'):
            return None

        self.recent_responses.append({"choice": choice, "turn": int(current_turn)})
        if len(self.recent_responses) > 10:
            self.recent_responses.pop(0)

        # Apply excessive trust penalty (V2b, replaces old trust-ratio branch)
        penalty = check_excessive_trust(self, current_turn)
        if penalty != 0:
            self.authority = max(0, min(100, self.authority + penalty))

        self._evaluate_authority()

        return self._check_events()

    def _evaluate_authority(self) -> None:
        """
        Evaluate authority based on recent response pattern.

        V2b: Trust-ratio penalty REMOVED (replaced by check_excessive_trust
        in record_response). Only insist recovery and balanced recovery remain.
        """
        if len(self.recent_responses) < 5:
            return

        # Extract choices from enriched format
        choices = [r["choice"] if isinstance(r, dict) else r for r in self.recent_responses]
        total = len(choices)
        trust_ratio = choices.count('trust') / total
        insist_ratio = choices.count('insist') / total

        # V2b: Trust-ratio penalty REMOVED — handled by check_excessive_trust()
        # Only insist recovery and balanced recovery remain.

        # Always insisting = tyrant (but maintains authority)
        if insist_ratio > 0.80:
            # Authority stays high but trust suffers (handled elsewhere)
            self.authority = min(100, self.authority + 1)

        # Balanced approach = healthy leadership
        elif 0.30 <= trust_ratio <= 0.60:
            self.authority = min(100, self.authority + 1)

    def modify_authority(self, delta: int) -> None:
        """
        Modify authority by delta, clamped 0-100.

        Used by external callers (defiance outcomes, major victory/defeat).

        Args:
            delta: Amount to change (+/-)
        """
        self.authority = max(0, min(100, self.authority + delta))

    def get_trust_gain_modifier(self) -> float:
        """
        Get modifier for trust gains based on authority.

        When authority is low (player always trusts), trust gains are reduced
        because marshals see the player as a pushover.

        Returns:
            Multiplier for trust gains (0.5 to 1.0)
        """
        if len(self.recent_responses) < 5:
            return 1.0

        choices = [r["choice"] if isinstance(r, dict) else r for r in self.recent_responses]
        trust_ratio = choices.count('trust') / len(choices)

        if trust_ratio > 0.80:
            return 0.5  # Severe penalty for always trusting
        elif trust_ratio > 0.60:
            return 0.75  # Moderate penalty
        return 1.0

    def get_obedience_modifier(self) -> float:
        """
        Get modifier for obedience chance based on authority.

        High authority = marshals more likely to obey
        Low authority = marshals more likely to object

        Returns:
            Multiplier for obedience (0.9 to 1.1)
        """
        if self.authority >= 80:
            return 1.1  # Bonus for strong authority
        elif self.authority >= 50:
            return 1.0  # Normal
        else:
            return 0.9  # Penalty for weak authority

    def get_authority_label(self) -> str:
        """
        Get a human-readable label for the current authority level.

        Returns:
            Label string describing Napoleon's perceived authority.
        """
        if self.authority >= 90:
            return "Divine Right"
        elif self.authority >= 70:
            return "Commanding"
        elif self.authority >= 50:
            return "Respected"
        elif self.authority >= 30:
            return "Questionable"
        else:
            return "Emperor in Name Only"

    def get_severity_modifier(self) -> float:
        """
        Get modifier for objection severity based on authority.

        Low authority = marshals object more severely.

        Returns:
            Multiplier for severity (1.0 to 1.3)
        """
        if self.authority >= 80:
            return 1.0  # No modifier
        elif self.authority >= 50:
            return 1.1  # Slightly more severe objections
        else:
            return 1.25  # Much more severe objections

    def _check_events(self) -> Optional[Dict]:
        """
        Check for authority threshold events.

        Returns:
            Event dict if threshold crossed, None otherwise
        """
        for threshold, event in sorted(self.THRESHOLD_EVENTS.items(), reverse=True):
            if self.authority <= threshold and threshold not in self._crossed_thresholds:
                self._crossed_thresholds.append(threshold)
                return {
                    'type': 'authority_event',
                    'threshold': int(threshold),
                    'authority': int(self.authority),
                    **event
                }
        return None

    def reset_threshold_tracking(self) -> None:
        """Reset threshold tracking (useful for testing or game reset)."""
        self._crossed_thresholds = []

    def get_status(self) -> Dict:
        """
        Get current authority status.

        Returns:
            Dict with authority info
        """
        choices = [r["choice"] if isinstance(r, dict) else r for r in self.recent_responses]
        if len(choices) < 5:
            pattern = "insufficient_data"
        else:
            trust_ratio = choices.count('trust') / len(choices)
            if trust_ratio > 0.60:
                pattern = "permissive"
            elif trust_ratio < 0.30:
                pattern = "authoritarian"
            else:
                pattern = "balanced"

        return {
            'authority': int(self.authority),
            'recent_responses': self.recent_responses.copy(),
            'pattern': pattern,
            'trust_gain_modifier': self.get_trust_gain_modifier(),
            'obedience_modifier': self.get_obedience_modifier(),
        }

    def __repr__(self) -> str:
        return f"AuthorityTracker(authority={self.authority}, responses={len(self.recent_responses)})"

    def to_dict(self) -> dict:
        """Serialize authority tracker for save/load.

        V2b: recent_responses stored as List[Dict] with {"choice", "turn"}.
        """
        return {
            "authority": self.authority,
            "recent_responses": [
                r if isinstance(r, dict) else {"choice": r, "turn": 0}
                for r in self.recent_responses
            ],
            "_crossed_thresholds": self._crossed_thresholds.copy()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'AuthorityTracker':
        """Deserialize authority tracker from save/load data.

        V2b: Backward compatible — bare strings treated as legacy format.
        """
        tracker = cls()
        tracker.authority = data.get("authority", 100)
        raw = data.get("recent_responses", [])
        tracker.recent_responses = [
            r if isinstance(r, dict) else {"choice": r, "turn": 0}
            for r in raw
        ]
        tracker._crossed_thresholds = data.get("_crossed_thresholds", []).copy()
        return tracker


def check_excessive_trust(authority_tracker, current_turn: int) -> int:
    """Check if player is trusting too often (pushover behavior).

    Uses a 10-turn sliding window. Only fires when >= 3 responses in window.

    Returns authority penalty (0, -2, or -3).
    Called from record_response() after each objection response.
    """
    recent = [
        r for r in authority_tracker.recent_responses
        if isinstance(r, dict) and r.get("turn", 0) >= current_turn - 10
    ]

    total = len(recent)
    if total < 3:  # Not enough data to judge
        return 0

    trust_count = sum(1 for r in recent if r.get("choice") == "trust")
    ratio = trust_count / total

    if ratio > 0.80:    # 80%+ = egregious pushover
        return -3
    elif ratio > 0.65:  # 65%+ = concerning pattern
        return -2
    else:
        return 0


# ═══════════════════════════════════════════════════════════════════════════
# VS-R — IMPERIAL GRIP & VASSAL-LOYALTY COUPLING
# ═══════════════════════════════════════════════════════════════════════════
# Spec: docs/VASSAL_DEEPENING_SPEC.md §2 + memo
#   docs/audits/VASSAL_AUTHORITY_COUPLING_RESEARCH_2026_07_14.md.
#
# "The Empire holds because *you* hold." When Napoleon's grip spirals, the whole
# satellite web loosens — and at rock-bottom grip the cheap levers no longer
# suffice; only land / autonomy / a large subsidy / winning battles arrest it.
#
# One grip = one module (gate Open Q#5): the two shared breakpoints below live
# here, in the leaf, so both jealousy.py and vassal.py import DOWN into a single
# source of truth — marshal feuds AND satellite defection anchor on the SAME two
# lines. (get_authority_proxy / is_capital_threatened stay in jealousy.py by a
# recorded scope deviation — they are jealousy-internal in use and pinned there;
# VS-R never reads them. Their relocation is a follow-on tidy, not a v1 need.)

# Shared "one grip" breakpoints (relocated here from jealousy.py). Authority > 70
# DAMPENS marshal feuds; < 30 is the one advertised spiral line (army infighting
# AND, per VS-R, satellite flight). See jealousy.py for the polarity rationale.
AUTHORITY_SUPPRESS_ABOVE = 70
AUTHORITY_ACCELERATE_BELOW = 30

# Imperial-grip territorial-collapse docks. Enemy parity: an intact enemy court
# reads 75 (jealousy proxy parity); a capital-lost enemy grades to 35. The docks
# make the PLAYER's grip finally fall when Paris / the homeland / the war is lost
# — the raw authority_tracker never did (memo Q1: its only military movers are
# ±5 nudges gated on OUTNUMBERING, and a capital lost to an enemy assault docks
# it by zero).
GRIP_ENEMY_COURT_BASE = 75
GRIP_CAPITAL_LOST = 40
GRIP_HOMELAND_MINORITY = 25   # capital held but < half the homeland retained
GRIP_WARSCORE_DEEP = 15       # worst active war_score < -50
GRIP_WARSCORE_LOSING = 8      # worst active war_score < -30 (cascade-aligned)

# VS-R vassal-drift coupling — negative-only, spiral-band only, CAPPED, NEVER a
# multiplier (the one shape that yields unrecoverable collapse; memo Q2/Q5).
# Boot-dormant: grip >= 30 contributes 0, and process_vassal_loyalty's
# _contribute() skips zero, so the healthy band is byte-identical to pre-VS-R.
VS_R_DRIFT_SPIRAL = -2        # grip < 30
VS_R_DRIFT_CAP = -4           # hard per-turn magnitude cap on the grip term
# The optional sub-15 "-4 floor" (memo §Q4) is HELD for post-playtest tuning:
# v1 ships the single -2 spiral term. VS_R_DRIFT_CAP already bounds any future
# floor. Owner for the escalation: VASSAL_DEEPENING_SPEC §2.6-Q4.

# "No cheap recovery": blunt the CHEAP one-shots (invest, autonomy-up) in the
# spiral band. Land grants (VS-3), full release, autonomy-DOWN, and the per-turn
# subsidy are NEVER softened — a *large* subsidy stays a valid existential lever.
VS_R_CHEAP_LEVER_MULT = 0.40


def _capital_held(world, nation: str) -> bool:
    """True when ``nation`` still controls its own capital region."""
    capital = world.get_nation_capital(nation)
    region = world.regions.get(capital) if capital else None
    return bool(region is not None and getattr(region, "controller", None) == nation)


def _homeland_held_fraction(world, nation: str):
    """(held, total) of the nation's STARTING homeland it still controls.

    Reconstructed from nation_starting_regions (populated for every nation incl.
    the player); returns (0, 0) when no homeland is recorded (bare test worlds).
    """
    home = list(getattr(world, "nation_starting_regions", {}).get(nation, []) or [])
    if not home:
        return 0, 0
    held = 0
    for region_name in home:
        region = world.regions.get(region_name)
        if region is not None and getattr(region, "controller", None) == nation:
            held += 1
    return held, len(home)


def _worst_war_score(world, nation: str):
    """Most negative war_score across the nation's ACTIVE wars, or None.

    "Losing the war" is a grip signal; the worst front is the one that shakes
    the court. Function-local diplomacy import (keeps authority.py a leaf).
    """
    get_actives = getattr(world, "get_active_nations", None)
    if get_actives is None:
        return None
    from backend.game_logic.diplomacy import get_war_score_for
    worst = None
    for other in get_actives():
        if other == nation:
            continue
        if not world.is_at_war(nation, other):
            continue
        score = get_war_score_for(world, nation, other)
        if worst is None or score < worst:
            worst = score
    return worst


def sovereign_aura_strength(world, nation: str) -> float:
    """NP-V — THE AURA OF INVINCIBILITY, as a number that DECAYS.

    The fraction of a sovereign's Presence that still holds, 0.0–1.0,
    derived from `get_imperial_grip` (no serialized field). Full while
    the throne stands; fading to nothing as the Empire cracks.

    This is the single source for BOTH halves of the mechanic — the
    combat aura (+10%/+10% scaled by this) and the enemy's fear of it —
    which is the whole point. Before NP-V the fear faded with grip and
    the aura did not, and that asymmetry is why an ordinary defeat under
    his own hand had no felt consequence: six emperor-led defeats moved
    the fear factor by exactly zero, and moved the aura not at all.

    Grip already encodes every collapse signal the fantasy needs — the
    emperor-led defeats (via authority), a lost capital, a losing war
    score, and the −40 capture shock. GR5-symmetric: an authored enemy
    sovereign's aura erodes on his own court's grip.
    """
    grip = get_imperial_grip(world, nation)
    if grip >= AURA_GRIP_FULL:
        return 1.0
    if grip <= AURA_GRIP_BROKEN:
        return 0.0
    span = AURA_GRIP_FULL - AURA_GRIP_BROKEN
    return (grip - AURA_GRIP_BROKEN) / span


# NP-V blessed band (in-band tunable; the grip window over which the
# Presence fades). 85 rather than the boot ceiling deliberately: an
# authority of 100 is the boot value, so a threshold at 70 meant the
# first SIX emperor-led defeats changed nothing at all. At 85 the third
# defeat is already visible on the card and in the battle report.
AURA_GRIP_FULL = 85
AURA_GRIP_BROKEN = 30


def get_imperial_grip(world, nation: str) -> int:
    """Napoleon-style 'imperial grip' (0-100), symmetric by construction (GR5).

    Blends the lord's COURT standing — authority_tracker for the player, a flat
    baseline for enemies (jealousy-proxy parity) — with a TERRITORIAL-collapse
    term (capital held, homeland majority, worst war score). This is the VS-R
    signal, and the crux fix of the research: the raw authority_tracker does NOT
    spiral on military collapse, so a player could lose the war and Paris with
    the tracker near 100. The derived grip closes that gap, and because it keys
    off the LORD it hands enemy lords the coupling for free.

    Boot returns: player at authority 100 / full empire -> 100 (VS-R dormant);
    enemy intact -> 75; enemy capital lost -> 35. Pure derived read — NO
    serialized field (memo Q6). NOT a substitute for jealousy's
    get_authority_proxy (its 75/50/25 pins stand); this is a graded superset.
    """
    if nation == getattr(world, "player_nation", None):
        tracker = getattr(world, "authority_tracker", None)
        base = int(getattr(tracker, "authority", 100)) if tracker is not None else 100
    else:
        base = GRIP_ENEMY_COURT_BASE

    # Territorial-collapse term. Capital loss dominates (-40); an intact capital
    # atop a lost homeland is the softer signal (-25). Mutually exclusive so the
    # enemy floor stays at the -2 tier (75 - 40 - 15 = 20; never sub-15).
    if not _capital_held(world, nation):
        base -= GRIP_CAPITAL_LOST
    else:
        held, total = _homeland_held_fraction(world, nation)
        if total and held * 2 < total:
            base -= GRIP_HOMELAND_MINORITY

    worst = _worst_war_score(world, nation)
    if worst is not None:
        if worst < -50:
            base -= GRIP_WARSCORE_DEEP
        elif worst < -30:
            base -= GRIP_WARSCORE_LOSING

    return max(0, min(100, base))


def authority_vassal_drift(grip: int) -> int:
    """VS-R banded vassal-loyalty drift from the lord's imperial grip.

    Boot-dormant (grip >= 30 -> 0, byte-identical); negative-only; capped in
    magnitude at VS_R_DRIFT_CAP. Additive to AUTONOMY_DRIFT, never multiplicative.
    """
    if grip >= AUTHORITY_ACCELERATE_BELOW:
        return 0
    return max(VS_R_DRIFT_CAP, VS_R_DRIFT_SPIRAL)


def get_authority_lever_multiplier(world, lord: str) -> float:
    """VS-R 'no cheap recovery' multiplier for the CHEAP one-shot loyalty levers.

    Exactly 1.0 at healthy grip (byte-identical boot); VS_R_CHEAP_LEVER_MULT in
    the <30 spiral band. Applied ONLY to invest and autonomy-up — land grants,
    release, autonomy-DOWN, and the per-turn subsidy are never softened.
    """
    if get_imperial_grip(world, lord) >= AUTHORITY_ACCELERATE_BELOW:
        return 1.0
    return VS_R_CHEAP_LEVER_MULT


def courting_unlock_bonus(grip: int) -> int:
    """VS-R: enemy courting reaches deeper (loyalty threshold 50 -> 50 + bonus)
    as the LORD's grip falls — the Allies peel satellites once the Emperor looks
    weak (the Treaty of Ried dynamic). 0 at grip >= 30 (pins green), up to +15 at
    grip 0."""
    if grip >= AUTHORITY_ACCELERATE_BELOW:
        return 0
    span = AUTHORITY_ACCELERATE_BELOW
    return int(round(15 * (span - grip) / span))


def courting_effectiveness_scale(grip: int) -> float:
    """VS-R: enemy courting bites harder (x1.0 -> x1.5 on loyalty_reduction) as
    the lord's grip falls. 1.0 at grip >= 30 (pins green)."""
    if grip >= AUTHORITY_ACCELERATE_BELOW:
        return 1.0
    span = AUTHORITY_ACCELERATE_BELOW
    return 1.0 + 0.5 * (span - grip) / span


# ═══════════════════════════════════════════════════════
# WO-D9 — THE ANTI-PUSHOVER DAMPER, WIRED (row WO slice 9)
# ═══════════════════════════════════════════════════════
#
# `AuthorityTracker.get_trust_gain_modifier` has existed since the V2
# objection work and was read by exactly one caller — the BATTLE
# vindication award (`vindication.py`). On the objection path, the surface
# it was written for, it was wired to nothing: a player who answered
# "trust" every time paid full price for every marshal's goodwill.
#
# The user ruled this on August 22, 2026 at the recommended default
# (`DESIGN_REFINEMENT.md` §WO-D7..D11, row WO-D9): (a) NO per-marshal
# cooldown — no new mechanic; (b) diminishing returns via this modifier
# exactly as it stands; (c) the authority-band asymmetry is DELIBERATE and
# stays. Nothing here re-opens any of the three.
#
# It is applied where the number is MINTED, not where it is paid. The six
# pay sites across the tactical and strategic handlers all read the figure
# back off the objection dict, and the objection dialog puts that same
# figure on its button ("Trust Ney's Judgment (+8 trust)"). Damping at the
# quote therefore damps all six for free AND keeps shown == applied;
# damping at the payment would have made the button lie, which is the
# defect class this whole row exists to close.
#
# Flip lever for the BASELINE_SERIES attribution experiment: False
# reproduces the pre-slice behaviour byte-identically (the
# HOST_RULE_ACTIVE idiom). Not a config surface.
# Landing record: docs/WEIRD_OUTCOMES_SPEC.md §3 slice 9.
OBJECTION_TRUST_DAMPER_ACTIVE = True


def objection_trust_modifier(world) -> float:
    """The effective anti-pushover modifier, as the objection surface sees it.

    Single source with `damp_objection_trust_gain` — the number a marshal
    is paid by and the number the dialog explains itself with must be the
    same read, or the explanation becomes its own shown-vs-applied bug.
    Returns 1.0 whenever nothing is being damped (lever down, no tracker,
    or under the >=5-answers guard), so a caller can render only when it
    is < 1.0.
    """
    if not OBJECTION_TRUST_DAMPER_ACTIVE:
        return 1.0
    tracker = getattr(world, "authority_tracker", None)
    if tracker is None or not hasattr(tracker, "get_trust_gain_modifier"):
        return 1.0
    return float(tracker.get_trust_gain_modifier())


def damp_objection_trust_gain(world, trust_gain: int) -> int:
    """Scale a quoted objection trust gain by the anti-pushover modifier.

    Gains only — an insist PENALTY is never softened, and a zero gain
    (MILD/NONE concerns) is returned untouched. Defensive about the
    tracker so legacy worlds and test doubles keep working: the
    `hasattr` probe mirrors `vindication.py`'s, which several fixtures
    already satisfy with a hand-rolled stub.
    """
    if trust_gain <= 0:
        return int(trust_gain)
    return int(trust_gain * objection_trust_modifier(world))
