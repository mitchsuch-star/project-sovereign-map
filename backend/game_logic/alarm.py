"""DY-1 "The Alarm of Europe" (`docs/DYNAMISM_SPEC.md` §3; the Tier-4 gate
record §3c, ruled November 9, 2026 in Plan Mode — the user's "your call" on
each question) — conquest spends standing with every third court. France has
always paid for conquest through threat; this module is where every other
court's conquest is FELT. ONE home for the three pieces:

  1. THE WRITE (§3c G1) — `sound_the_alarm`, called at the ONE capture
     chokepoint (`WorldState.capture_region`) and its single mirror (the
     reckless auto-charge, which bypasses the chokepoint by construction): an
     AI court's capture writes Europe's alarm against its HOUSE through the
     existing generalized store (`coalition.add_threat`, source
     `alarm:<region>`, the serialized `threat_by_target`). Census correction
     C1: every conqueror ALREADY pays at capture (+2 a province beside this
     call, +15 a capital and +3 / +5 a battle in the combat pipeline) — the
     alarm is the ADDEND that carries an AI conqueror past the instruments'
     floors. The player's house writes nothing new: France's machinery is
     untouched, so nothing double-charges. Decay is the store's own.

  2. THE GUARANTEE RUNG (§3c G2) — `process_alarm_guarantees`, run in the
     AI-AI diplomatic phase: a court alarmed by a conqueror gives its word
     for the likely next victim — the EXISTING D5 guarantee
     (`instruments.pledge_guarantee`), so everything after the pledge is the
     instruments' own machinery: a DEFENDING ward's guarantor marches at the
     tick (the Fürstenbund of 1785, Prussia's word for Bavaria against
     Joseph II's exchange); a ward that declared its own war is not marched
     for and nobody is branded (census correction C2 — the honour defends);
     the deterrent is a design weight −8 and the guarantor's army in the
     holder's scale; a later war on the ward is honoured.

  3. THE WORDS (§3c G4; Q6 — words only, the user's "your call") —
     `alarm_line` / `alarm_lines`: "Vienna's appetite is remarked in Berlin
     and St. Petersburg." Talleyrand's readings and the Balance tab say it;
     no surface ever carries an AI court's alarm as a figure.

The numbers are authored (N-DY1) and tuneable at the measure. The seams hold
each piece down (`tests/_t3_seams.py` row T4-1, the recorded boards'
hold-list). No new store, no new serialized field: the alarm rides
`threat_by_target`, the cooldown rides `ai_proposal_cooldowns`.
"""
from __future__ import annotations

from typing import Dict, List, Optional

# ── N-DY1 (authored; the gate record §3c G1/G2) ─────────────────────────
ALARM_PROVINCE = 6          # an ordinary province taken
ALARM_CAPITAL = 12          # a capital taken (precedes the client arm)
ALARM_CLIENT = 8            # a province of some THIRD court's client
ALARM_GUARANTEE_COOLDOWN_TURNS = 12   # per guarantor, the auction/vassalage idiom
ALARM_GUARANTEE_COOLDOWN_KEY = "alarm_guarantee"
ALARM_GUARANTOR_TIERS = ("major", "secondary")   # a minor never promises
ALARM_LINES_MAX = 3         # the Balance tab's sentences
ALARM_REMARKERS_MAX = 2     # the courts a sentence names
# The formation-peer arm of the spec's first draft is REMOVED, explicitly
# (§3c G1): no such relation exists in the engine; a crown erected at Tier 8
# is a client and takes the client arm.


def the_alarm_sounds() -> bool:
    """DY-1 seam (§3c G1): an AI court's capture writes Europe's alarm
    against its house (`sound_the_alarm`). Down: no `alarm:` write — every
    conqueror pays only what it paid before (the +2, the capital, the
    battles)."""
    return True


def an_alarmed_court_guarantees() -> bool:
    """DY-1 seam (§3c G2): the guarantee rung — a court alarmed by a
    conqueror pledges the existing D5 guarantee for the likely next victim.
    Down: only the crisis producer ever pledges an AI guarantee."""
    return True


def _player(world) -> str:
    return getattr(world, "player_nation", "France")


def house_leader(world, nation: str) -> str:
    """The court a capture is charged to: `nation`'s top overlord (a
    client's conquest alarms Europe against its lord's house)."""
    return world._top_overlord(nation) or nation


def _in_player_house(world, nation: str) -> bool:
    return bool(nation) and house_leader(world, nation) == _player(world)


def _name(world, nation: str) -> str:
    from backend.game_logic.formations import formed_display_name
    return formed_display_name(world, nation)


# ═══════════════════════════════════════════════════════════════════════
# 1. The write — at the capture chokepoint
# ═══════════════════════════════════════════════════════════════════════

def alarm_amount(world, region_name: str, old_controller: str,
                 capturer_leader: str) -> int:
    """N-DY1: a capital 12; a province of a court that is some THIRD court's
    client 8 (its lord's circle takes note); any other province 6."""
    region = world.get_region(region_name)
    if region is not None and getattr(region, "is_capital", False):
        return ALARM_CAPITAL
    if old_controller:
        victim_leader = house_leader(world, old_controller)
        if victim_leader not in (old_controller, capturer_leader):
            return ALARM_CLIENT
    return ALARM_PROVINCE


def sound_the_alarm(world, region_name: str, capturer: str,
                    old_controller: str, *, liberated: bool,
                    prior_title: Optional[Dict]) -> int:
    """The write (§3c G1): an AI conqueror's capture of `region_name` from
    `old_controller` raises its HOUSE's slot by `alarm_amount`. The same
    three skips as the +2 beside it — the capturer's own soil, a title it
    recovers, a liberation handed home — and the player's house writes
    nothing new. Event-driven at the chokepoint: one region read, no scan
    (Golden Rule 8). Returns the amount written (0 = none)."""
    if not the_alarm_sounds():
        return 0
    if not capturer or liberated:
        return 0
    if not old_controller or old_controller == capturer:
        return 0
    leader = house_leader(world, capturer)
    if leader == _player(world):
        return 0
    from backend.models.region import get_starting_controllers
    from backend.models.world_state import capture_recovers_title
    starting = (getattr(world, "_starting_controllers", None)
                or get_starting_controllers())
    if starting.get(region_name) == capturer:
        return 0
    if capture_recovers_title(dict(prior_title or {}), capturer):
        return 0
    amount = alarm_amount(world, region_name, old_controller, leader)
    from backend.game_logic.coalition import add_threat
    add_threat(world, amount, f"alarm:{region_name}", target=leader)
    return amount


# ═══════════════════════════════════════════════════════════════════════
# 2. The guarantee rung — in the AI-AI diplomatic phase
# ═══════════════════════════════════════════════════════════════════════

def alarming_conquerors(world) -> List[str]:
    """The AI house leaders Europe has taken notice of — a slot at or above
    the tension line (`coalition.THREAT_TENSION_MIN`, 30) — loudest first,
    then by name. Reads one dict (GR8)."""
    from backend.game_logic.coalition import THREAT_TENSION_MIN
    player = _player(world)
    vassals = getattr(world, "vassals", {}) or {}
    active = set(world.get_active_nations())
    slots = getattr(world, "threat_by_target", {}) or {}
    loud = [(int(value or 0), nation) for nation, value in slots.items()
            if nation != player and nation not in vassals and nation in active
            and int(value or 0) >= int(THREAT_TENSION_MIN)]
    return [nation for _, nation in sorted(loud, key=lambda t: (-t[0], t[1]))]


def _victim_eligible(world, victim: str, conqueror: str) -> bool:
    """A court that may be guaranteed against `conqueror`: standing, not the
    conqueror's house, not the player's house (the human's wards are the
    human's), not a client (its lord answers for it), not already under a
    live word (one guarantee is protection enough)."""
    if not victim or victim == conqueror:
        return False
    if house_leader(world, victim) == conqueror:
        return False
    if _in_player_house(world, victim):
        return False
    if victim in (getattr(world, "vassals", {}) or {}):
        return False
    if victim not in world.get_active_nations():
        return False
    from backend.game_logic.instruments import live_guarantees_of
    return not live_guarantees_of(world, victim)


def _eaten_from(world, conqueror: str) -> Dict[str, int]:
    """{court: homeland provinces the conqueror's house holds} — read off the
    house's OWN regions' boot owners (the cached `get_nation_regions`), never
    a region scan (GR8)."""
    from backend.game_logic.war_council import _house_of
    from backend.models.region import get_starting_controllers
    starting = (getattr(world, "_starting_controllers", None)
                or get_starting_controllers())
    house = _house_of(world, conqueror)
    counts: Dict[str, int] = {}
    for member in sorted(house):
        for region_name in world.get_nation_regions(member):
            owner = starting.get(region_name)
            if owner and owner not in house:
                counts[owner] = counts.get(owner, 0) + 1
    return counts


def likely_next_victim(world, conqueror: str) -> Optional[str]:
    """§3c G2: (a) a standing court whose homeland the conqueror holds — one
    at war with it first, then the remnant at peace, the most eaten first;
    (b) else the conqueror's defenceless prize (the holder its design opens
    on at an ultimatum, `war_council.defenceless_prize`)."""
    eaten = _eaten_from(world, conqueror)
    pool = [court for court in eaten if _victim_eligible(world, court, conqueror)]
    at_war = [court for court in pool if world.is_at_war(conqueror, court)]
    chosen = at_war or pool
    if chosen:
        return sorted(chosen, key=lambda court: (-eaten[court], court))[0]
    from backend.game_logic.war_council import defenceless_prize
    prize = defenceless_prize(world, conqueror)
    if prize and _victim_eligible(world, prize, conqueror):
        return str(prize)
    return None


def _cooldowns(world) -> Dict[str, int]:
    return getattr(world, "ai_proposal_cooldowns", {}) or {}


def _relation(world, a: str, b: str) -> int:
    return int((getattr(world, "nation_relations", {}) or {}).get(
        world._make_diplo_key(a, b), 0) or 0)


def alarmed_guarantor(world, conqueror: str, victim: str) -> Optional[str]:
    """§3c G2: the court that gives its word — an AI court of major or
    secondary rank (a minor never promises), not a client and not the
    player's house, at peace (the crisis producer's idiom: a court at war
    has no hand free), no friend of the conqueror (relation ≤ 0), no enemy
    of the victim (relation ≥ 0), bordering the victim's remnant, off its
    cooldown, not already its guarantor, and able to march lawfully
    (`instruments.guarantee_join_refusal` — a word that would void at once
    is no word). The word answers the CONQUEROR: a ward already defending
    against another court (`instruments.guarantee_exposure` — the attackers
    the pledge puts the guarantor on the clock for) would make the word a
    declaration on that court, which no alarm about the conqueror motivates
    — the measure's own catch, the Porte's word for Austria against
    Prussia's appetite marched the Porte on France, Austria's attacker of
    1805. The strongest such court; ties by name."""
    from backend.game_logic.instruments import (
        guarantee_exposure,
        guarantee_join_refusal,
        guarantors_of,
    )
    from backend.game_logic.war_council import _standing_strength
    from backend.nation_config import _POWER_TIER_DEFAULT
    player = _player(world)
    vassals = getattr(world, "vassals", {}) or {}
    neighbours = set(world.get_neighbouring_nations(victim))
    cooldowns = _cooldowns(world)
    already = set(guarantors_of(world, victim))
    candidates: List[str] = []
    for court in world.get_active_nations():
        if court in (conqueror, victim, player) or court in vassals:
            continue
        if _in_player_house(world, court) or court not in neighbours:
            continue
        tier = world.get_power_tier(court) or _POWER_TIER_DEFAULT
        if tier not in ALARM_GUARANTOR_TIERS:
            continue
        if world.get_nations_at_war_with(court):
            continue
        if _relation(world, court, conqueror) > 0:
            continue
        if _relation(world, court, victim) < 0:
            continue
        if int(cooldowns.get(f"{court}|{ALARM_GUARANTEE_COOLDOWN_KEY}", 0) or 0) > 0:
            continue
        if court in already:
            continue
        if set(guarantee_exposure(world, court, victim)) - {conqueror}:
            continue
        candidates.append(court)
    lawful = [court for court in candidates
              if not guarantee_join_refusal(world, court, conqueror)]
    if not lawful:
        return None
    return sorted(lawful, key=lambda court: (-_standing_strength(world, court),
                                             court))[0]


def process_alarm_guarantees(world) -> List[Dict]:
    """The rung (§3c G2): for the loudest conqueror with a likely victim and
    a willing guarantor, ONE pledge — one AI guarantee a turn world-wide,
    the stamp shared with the crisis producer
    (`world._ai_guarantee_this_turn`); the guarantor rests
    `ALARM_GUARANTEE_COOLDOWN_TURNS`. The pledge is the instrument's own
    mint (`pledge_guarantee` logs `guarantee_pledged`, carrying `against`);
    the rung only APPENDS the turn surface's line (one logger per event)."""
    if not an_alarmed_court_guarantees():
        return []
    turn = int(getattr(world, "current_turn", 0) or 0)
    if getattr(world, "_ai_guarantee_this_turn", -1) == turn:
        return []
    from backend.game_logic.instruments import pledge_guarantee
    for conqueror in alarming_conquerors(world):
        victim = likely_next_victim(world, conqueror)
        if not victim:
            continue
        guarantor = alarmed_guarantor(world, conqueror, victim)
        if not guarantor:
            continue
        pledge = pledge_guarantee(world, guarantor=guarantor, protected=victim,
                                  against=conqueror)
        if not (pledge.get("success") and pledge.get("record")):
            continue
        world._ai_guarantee_this_turn = turn
        cooldowns = dict(_cooldowns(world))
        cooldowns[f"{guarantor}|{ALARM_GUARANTEE_COOLDOWN_KEY}"] = int(
            ALARM_GUARANTEE_COOLDOWN_TURNS)
        world.ai_proposal_cooldowns = cooldowns
        return [{
            "type": "guarantee_pledged",
            "guarantor": guarantor,
            "protected": victim,
            "against": conqueror,
            "by": "alarm",
            "message": (f"{_name(world, guarantor)} guarantees "
                        f"{_name(world, victim)} against "
                        f"{_name(world, conqueror)}'s appetite."),
        }]
    return []


# ═══════════════════════════════════════════════════════════════════════
# 3. The words (Q6 — never a figure)
# ═══════════════════════════════════════════════════════════════════════

def _seat(world, nation: str) -> str:
    """A great court named by its seat, the era's diplomatic idiom ("the
    cabinet of Vienna"); any other court by its display name."""
    capital = world.get_nation_capital(nation)
    if (capital and capital in (getattr(world, "regions", {}) or {})
            and world.get_power_tier(nation) == "major"):
        return str(capital)
    return _name(world, nation)


def remarking_courts(world, conqueror: str) -> List[str]:
    """Who remarks the appetite, in order: the courts that have given their
    word for one of its victims; then the great powers cold toward it
    (relation ≤ 0, coldest first); then its cold neighbours. Never the
    player (Talleyrand speaks FOR Paris), never the conqueror's own house,
    never a court it is eating (a victim complains — it does not remark)."""
    from backend.game_logic.instruments import guarantors_of
    player = _player(world)
    vassals = getattr(world, "vassals", {}) or {}
    eaten = _eaten_from(world, conqueror)
    out: List[str] = []

    def _take(court: str) -> None:
        if (court and court not in out and court != player
                and court not in vassals and court not in eaten
                and house_leader(world, court) != conqueror):
            out.append(court)

    for victim in sorted(eaten):
        for guarantor in sorted(guarantors_of(world, victim)):
            _take(guarantor)
    active = list(world.get_active_nations())
    cold_majors = sorted(
        (court for court in active
         if world.get_power_tier(court) == "major"
         and _relation(world, court, conqueror) <= 0),
        key=lambda court: (_relation(world, court, conqueror), court))
    for court in cold_majors:
        _take(court)
    neighbours = sorted(
        (court for court in world.get_neighbouring_nations(conqueror)
         if court in active and _relation(world, court, conqueror) <= 0),
        key=lambda court: (_relation(world, court, conqueror), court))
    for court in neighbours:
        _take(court)
    return out[:ALARM_REMARKERS_MAX]


def alarm_line(world, conqueror: str) -> str:
    """The sentence for one alarming conqueror ("" when Europe has not taken
    notice): "Vienna's appetite is remarked in Berlin and St. Petersburg."
    Words only — no figure, ever (Q6)."""
    if conqueror not in alarming_conquerors(world):
        return ""
    seat = _seat(world, conqueror)
    remarkers = [_seat(world, court) for court in remarking_courts(world, conqueror)]
    if len(remarkers) >= 2:
        where = f"in {remarkers[0]} and {remarkers[1]}"
    elif remarkers:
        where = f"in {remarkers[0]}"
    else:
        where = "across Europe"
    return f"{seat}'s appetite is remarked {where}."


def alarm_lines(world) -> List[str]:
    """The Balance tab's sentences — the loudest conquerors' lines, at most
    `ALARM_LINES_MAX`; [] when Europe has taken notice of no one."""
    lines: List[str] = []
    for conqueror in alarming_conquerors(world)[:ALARM_LINES_MAX]:
        line = alarm_line(world, conqueror)
        if line:
            lines.append(line)
    return lines
