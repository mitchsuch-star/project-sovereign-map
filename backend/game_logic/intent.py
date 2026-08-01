"""The Intent Layer — AI-1 / AI-1b (docs/AI_INTENT_SPEC.md §3, §4.1, §3.5).

A nation's **Intent** is a derived record answering four questions: what it
wants (`want` — the active agenda or survival), who stands in the way
(`against`), how much it cares (`weight`, 0–100), and what it is currently
prepared to pay (`price` — the ladder, climbed in order):

    indifferent → ask → buy → align → bandwagon → coerce → fight

READ-ONLY in this slice: intent is a pure reading of the world plus its
legibility surfaces (the Diplomatic Ledger's nations tab, Talleyrand's war
room). Nothing consumes it for behaviour until AI-2. Contracts:

- **Derived over serialized** (principle 3): recomputed per turn, cached on
  the `get_active_agenda` idiom — `_intent_cache` turn-keyed beside
  `_agenda_cache`, cleared through `invalidate_bloc_members_cache`
  (`world_state.py`), which every region-control, vassalage AND
  diplomatic-state seam reaches.
- **Staleness (decided + pinned):** relations, relative force and treasury
  are TURN-GRANULAR by design — the same choice `agendas.py` makes for
  treasury. A mid-turn relation delta does not recompute intent; war/peace
  state changes DO flush (set_diplomatic_state reaches the chokepoint).
- **Deckless-neutral** (§5 pin 18): no live agenda → the bottom rung
  `indifferent`, and every legibility surface omits the row. The bare
  suite world and the legacy fixture world are byte-identical.
- **D4 — no fog:** want, against and price are always readable. What is
  never shown is *when* (timing lives in the fore-warning layer, AI-3+).
- **§3.8 jitter:** `weight` carries the campaign-seed jitter, ramping from
  0 at boot (the historical seed always reads 0) — the AI-0b ordering
  constraint honoured: the seed lands with the first consumer.

AI-1b, the mirror: `build_france_mirror_payload` — Europe's derived reading
of FRANCE, from observable deeds only (hegemony share, the continent's
threat alarm, army positions near borders). It never reads the player's
plans — there are none to read (GR6) — and a player who does nothing
drifts DOWN the perceived ladder (threat decay does the work).
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from backend.game_logic.agendas import (
    AgendaView,
    get_active_agenda,
)
from backend.game_logic.campaign_variance import seeded_jitter

# The ladder, in climb order (§3). Index = rung height.
PRICE_LADDER = (
    "indifferent", "ask", "buy", "align", "bandwagon", "coerce", "fight",
)

# Player-facing rung labels (R7 — composed backend-side, never raw keys).
PRICE_DISPLAY = {
    "indifferent": "Indifferent",
    "ask": "Diplomacy",
    "buy": "Gold",
    "align": "Alliance",
    "bandwagon": "Service to the strong",
    "coerce": "An ultimatum",
    "fight": "War",
}

# Blessed weight-derivation constants (in-band tunable; shape escalates).
WEIGHT_BASE_BY_TYPE = {
    "acquire_regions": 55,
    "deny_regions": 60,
    "contain_hegemon": 65,
    "paymaster": 40,
    "guard_neutrality": 25,
}
# AI-3r ruling R5: WEIGHT_AT_WAR_WITH_HOLDER (+10, "the war IS the
# pursuit") is RETIRED — with _derive_price's already-at-war early return
# its only surviving effect was a cosmetic bump on the displayed weight,
# and for war-OPENING it was a dead term by construction (the state it
# needs disqualifies the crisis, AI_WAR_DECISION_SPEC §0.2).
WEIGHT_RELATION_COLD = 8             # relation <= -40 with `against`
WEIGHT_RELATION_CHILLY = 4           # relation <= 0
WEIGHT_RELATION_WARM = -8            # relation > 30
WEIGHT_OPPORTUNISM_ONE_WAR = 6       # §3.2 — the holder is busy
WEIGHT_OPPORTUNISM_TWO_WARS = 10     # …deeply busy
WEIGHT_OPPORTUNISM_BANKRUPT = 3      # …or bankrupt
# AI-3r §2.2 — the moment: opportunity terms that can actually climb to
# the fight bar (N3–N6, blessed at the §6.1 gate; the slice-0 probe kept
# the bar itself at 85). Each is a per-turn READING, never a latch
# (§3.1a) — an opening not taken closes by itself, and beat 7 then
# reports `starved` truthfully.
WEIGHT_HOLDER_ALLIES_COMMITTED = 6   # N3: the holder's faction is busy
WEIGHT_HOLDER_RECENTLY_BEATEN = 8    # N4: the wolves gather after Austerlitz
RECENTLY_BEATEN_TURNS = 6            # N4: the war-end window
WEIGHT_HOLDER_EXHAUSTED = 5          # N5: consumes the AI-4c signal
HOLDER_EXHAUSTION_BAND = 100         # N5: WE floor for the read
WEIGHT_OWN_REAR_QUIET = 6            # N6: a safe rear invites adventure
REAR_QUIET_FRACTION = 0.20           # N6: reserve below 20% of standing
WEIGHT_SURVIVAL = 95
# AI-5c (§12.5): the hegemon REFUSED this court's offered mediation —
# the arbiter scorned hardens. Derived from the pin-8 refusal record,
# so it expires with that record's 12-turn memory window: refusing the
# good offices is the ramp toward the next coalition, by machinery.
WEIGHT_MEDIATION_REBUFFED = 6
INTENT_WEIGHT_JITTER = 8             # §3.8 amplitude, ramps in over turns

# weight -> rung thresholds (highest rung whose floor is met).
PRICE_THRESHOLDS = (
    ("fight", 85),
    ("coerce", 72),
    ("bandwagon", 65),
    ("align", 55),
    ("buy", 40),
    ("ask", 25),
)

# Posture designs cap their ladder (§3: a guard_neutrality design never
# reaches coerce; a paymaster pays others rather than climbing itself).
PRICE_CAP_BY_TYPE = {
    "guard_neutrality": "align",
    "paymaster": "align",
}


@dataclass(frozen=True)
class IntentView:
    """The derived intent record (§3's four questions)."""
    nation: str
    want_id: Optional[str]        # agenda id, "survival", or None
    want_title: Optional[str]
    want_type: Optional[str]
    against: Optional[str]        # nation tag, or None
    weight: int                   # 0-100
    price: str                    # a PRICE_LADDER rung
    survival: bool = False


def rung_index(price: str) -> int:
    """Ladder height of a rung (unknown reads as the bottom)."""
    try:
        return PRICE_LADDER.index(price)
    except ValueError:
        return 0


def get_nation_intent(nation: str, world) -> IntentView:
    """The one derivation chokepoint. Per-turn cached; cleared through
    invalidate_bloc_members_cache (the _agenda_cache idiom).

    Deckless / vassalized / eliminated nations — and the player — read the
    bottom rung `indifferent` (§5 pin 18): the rung rework of AI-2 falls
    through to today's behaviour byte-identically at that rung.
    """
    cache = getattr(world, "_intent_cache", None)
    cache_turn = getattr(world, "_intent_cache_turn", -1)
    if cache is None or cache_turn != world.current_turn:
        cache = {}
        world._intent_cache = cache
        world._intent_cache_turn = world.current_turn
    if nation in cache:
        return cache[nation]

    view = _derive_intent(nation, world)
    cache[nation] = view
    return view


def _indifferent(nation: str) -> IntentView:
    return IntentView(nation=nation, want_id=None, want_title=None,
                      want_type=None, against=None, weight=0,
                      price="indifferent")


def _derive_intent(nation: str, world) -> IntentView:
    agenda = get_active_agenda(nation, world)
    if agenda is None:
        return _indifferent(nation)

    if agenda.survival:
        against = _survival_threat(nation, world)
        at_war = bool(against) and world.is_at_war(nation, against)
        return IntentView(
            nation=nation,
            want_id=agenda.id,
            want_title=agenda.title,
            want_type=agenda.type,
            against=against,
            weight=WEIGHT_SURVIVAL,
            price="fight" if at_war else "coerce",
            survival=True,
        )

    against = _derive_against(nation, agenda, world)
    weight = _derive_weight(nation, agenda, against, world)
    price = _derive_price(nation, agenda, against, weight, world)
    return IntentView(
        nation=nation,
        want_id=agenda.id,
        want_title=agenda.title,
        want_type=agenda.type,
        against=against,
        weight=weight,
        price=price,
    )


def _derive_against(nation: str, agenda: AgendaView,
                    world) -> Optional[str]:
    """Who stands in the way — derived, retargets as control changes."""
    if agenda.type == "acquire_regions":
        # The obstacle is whoever holds the most uncontrolled targets,
        # resolved to the top overlord (a vassal's soil is its lord's
        # sphere). Deterministic tie-break: first holder in region order.
        from backend.game_logic.agendas import (
            _controlled_by_self_or_vassal,
            _region_controller,
        )
        counts: Dict[str, int] = {}
        order: Dict[str, int] = {}
        for position, region_name in enumerate(agenda.regions):
            if _controlled_by_self_or_vassal(world, nation, region_name):
                continue
            controller = _region_controller(world, region_name)
            if not controller:
                continue
            effective = world._top_overlord(controller) or controller
            if effective == nation:
                continue
            counts[effective] = counts.get(effective, 0) + 1
            order.setdefault(effective, position)
        if not counts:
            return None
        return max(counts,
                   key=lambda holder: (counts[holder], -order[holder]))
    if agenda.type in ("deny_regions", "contain_hegemon", "paymaster"):
        from backend.game_logic.agendas import _hegemon
        hegemon, _share = _hegemon(world, nation)
        return hegemon
    return None  # guard_neutrality: nobody, until somebody trespasses


def _survival_threat(nation: str, world) -> Optional[str]:
    """The invader: an at-war nation standing on this nation's home soil
    (capital first), else the first at-war nation."""
    at_war = sorted(world.get_nations_at_war_with(nation))
    if not at_war:
        return None
    home = list(getattr(world, "nation_starting_regions", {})
                .get(nation, []) or [])
    capital = world.get_nation_capital(nation)
    if capital:
        # Review fix [2]: capital FIRST unconditionally — home always
        # contains it, so insert-only-when-absent left it mid-list and
        # the "capital first" priority never actually applied.
        home = [capital] + [r for r in home if r != capital]
    for region_name in home:
        region = world.regions.get(region_name)
        controller = getattr(region, "controller", None)
        if controller in at_war:
            return controller
    return at_war[0]


def _holder_allies_committed(nation: str, holder: str, world) -> bool:
    """AI-3r §2.2 (N3): the holder's guarantors/allies are themselves at
    war — HOI4's "their faction is busy". Before this term only the
    holder's OWN wars counted toward opportunism."""
    for record in getattr(world, "diplomatic_guarantees", []) or []:
        if record.get("protected") != holder:
            continue
        guarantor = str(record.get("guarantor") or "")
        if not guarantor or guarantor in (nation, holder):
            continue
        if world.get_nations_at_war_with(guarantor):
            return True
    for other in world.get_active_nations():
        if other in (nation, holder):
            continue
        if world.get_diplomatic_state(holder, other) in (
                "ALLIANCE", "DEFENSIVE_ALLIANCE"):
            if world.get_nations_at_war_with(other):
                return True
    return False


def _holder_recently_beaten(holder: str, world) -> bool:
    """AI-3r §2.2 (N4), derivation per gate ruling R3 — zero new fields:
    the holder reads BEATEN while its capital is not in its own hands, OR
    when a war ended for it within RECENTLY_BEATEN_TURNS (the per-nation
    exited_turn/ended_turn read — the get_agenda_grudge_nations idiom;
    instance retention 10 >= window 6) while home soil is still held by a
    power outside its vassal chain. A pure per-turn reading — recovering
    the capital or the soil ends it."""
    capital = world.get_nation_capital(holder)
    capital_region = world.regions.get(capital) if capital else None
    if capital_region is not None and capital_region.controller != holder:
        return True
    turn = int(getattr(world, "current_turn", 0))
    ended_recently = False
    for instance in (getattr(world, "war_instances", {}) or {}).values():
        if not isinstance(instance, dict):
            continue
        meta = instance.get("participant_meta") or {}
        side_by = instance.get("side_by_nation") or {}
        if holder not in meta and holder not in side_by:
            continue
        end = (meta.get(holder) or {}).get("exited_turn")
        if end is None:
            end = instance.get("ended_turn")
        if end is None:
            continue
        if turn - int(end) < RECENTLY_BEATEN_TURNS:
            ended_recently = True
            break
    if not ended_recently:
        return False
    home = (getattr(world, "nation_starting_regions", {}) or {}).get(
        holder, []) or []
    for region_name in home:
        region = world.regions.get(region_name)
        controller = getattr(region, "controller", None) if region else None
        if (controller and controller != holder
                and world._top_overlord(controller) != holder):
            return True
    return False


def _derive_weight(nation: str, agenda: AgendaView,
                   against: Optional[str], world) -> int:
    weight = WEIGHT_BASE_BY_TYPE.get(agenda.type, 40)
    # AI-2c (§3.4): the statecraft weight modifier — authored 0 for every
    # 1805 court (boot-neutral, pin 1); the wire exists for scenarios
    # that author a hungrier or sleepier great power.
    from backend.game_logic.statecraft import statecraft_weight_mod
    weight += statecraft_weight_mod(world, nation)
    if against:
        relation = int(world.nation_relations.get(
            world._make_diplo_key(nation, against), 0) or 0)
        if relation <= -40:
            weight += WEIGHT_RELATION_COLD
        elif relation <= 0:
            weight += WEIGHT_RELATION_CHILLY
        elif relation > 30:
            weight += WEIGHT_RELATION_WARM
        # §3.2 opportunism: willingness rises while the holder is busy —
        # and decays the moment the holder's situation improves, because
        # this is a per-turn READING, never a latch (§3.1a).
        holder_wars = len(world.get_nations_at_war_with(against))
        if holder_wars >= 2:
            weight += WEIGHT_OPPORTUNISM_TWO_WARS
        elif holder_wars == 1:
            weight += WEIGHT_OPPORTUNISM_ONE_WAR
        if int((getattr(world, "nation_gold", {}) or {})
               .get(against, 0)) < 0:
            weight += WEIGHT_OPPORTUNISM_BANKRUPT
        # AI-2b D5-3: a live third-party guarantee of the obstacle raises
        # the coveter's bar for war — shown as the weight it actually
        # moved to (D4: the ledger shows the number). Boot-zero: no
        # guarantees exist until one is pledged.
        from backend.game_logic.instruments import (
            GUARANTEE_WEIGHT_DETERRENT,
            WEIGHT_RENEGED_BARGAIN,
            has_renege_grievance,
        )
        for record in getattr(world, "diplomatic_guarantees", []) or []:
            if (record.get("protected") == against
                    and record.get("guarantor") != nation):
                weight -= GUARANTEE_WEIGHT_DETERRENT
                break
        # §3.3: a reneged bargain is the strongest mark in the game — the
        # victim's willingness against the breaker surges (Stage D adds
        # the may-skip-rungs casus belli).
        if has_renege_grievance(world, nation, against):
            weight += WEIGHT_RENEGED_BARGAIN
        # AI-5c (§12.5): scorned good offices. A contain/arbiter court
        # whose offered mediation `against` refused reads the refusal
        # record (pin 8) and hardens — fully derived, expiring with the
        # record's own memory window. Local import: the war_council
        # idiom (ai_diplomacy imports intent function-locally too).
        if agenda.type == "contain_hegemon":
            from backend.game_logic.ai_diplomacy import get_refused_asks
            if any(e.get("type") == "mediation"
                   for e in get_refused_asks(world, nation, against)):
                weight += WEIGHT_MEDIATION_REBUFFED
        # AI-3r §2.2 — the moment. All four are per-turn readings that
        # decay the moment the world improves for the holder (§3.1a).
        if _holder_allies_committed(nation, against, world):
            weight += WEIGHT_HOLDER_ALLIES_COMMITTED
        if _holder_recently_beaten(against, world):
            weight += WEIGHT_HOLDER_RECENTLY_BEATEN
        if int((getattr(world, "war_exhaustion", {}) or {})
               .get(against, 0) or 0) > HOLDER_EXHAUSTION_BAND:
            weight += WEIGHT_HOLDER_EXHAUSTED
        # The mirror of the exposure gate — a quiet rear invites
        # adventure. Local import: war_council imports intent the same
        # way (function-local), so no cycle exists at module load.
        from backend.game_logic.war_council import get_exposure_view
        exposure = get_exposure_view(world, nation)
        if (exposure["standing"] > 0
                and exposure["reserve"]
                < REAR_QUIET_FRACTION * exposure["standing"]):
            weight += WEIGHT_OWN_REAR_QUIET
    # §3.8 threshold jitter — 0 at boot on every seed, 0 forever on the
    # historical seed; the bars move, never the choices.
    weight += seeded_jitter(
        str(getattr(world, "campaign_seed", "historical")),
        f"intent_weight::{nation}::{agenda.id}",
        INTENT_WEIGHT_JITTER,
        int(world.current_turn),
    )
    return max(0, min(100, int(weight)))


def _derive_price(nation: str, agenda: AgendaView, against: Optional[str],
                  weight: int, world) -> str:
    if against and world.is_at_war(nation, against):
        return "fight"  # already paying the top of the ladder
    price = "ask"
    for rung, floor in PRICE_THRESHOLDS:
        if weight >= floor:
            price = rung
            break
    cap = PRICE_CAP_BY_TYPE.get(agenda.type)
    if cap is not None and rung_index(price) > rung_index(cap):
        price = cap
    # Review fix [3]: a LIVE design's floor is "ask" — `indifferent` is
    # the no-design bottom state (pin 18, renderers omit), never a
    # distance a court with a standing want is "prepared to go". A
    # negative jitter draw must not render nonsense copy.
    return price


# ── Legibility surfaces (AI-1's deliverable is the render) ───────────────


def build_intent_payload(nation: str, world) -> Optional[dict]:
    """{want_title, against_display, weight, price, price_display, summary}
    for the ledger / war-room surfaces — un-fogged by design (DPF-1,
    diplomacy has no fog). None when the nation is indifferent with no
    design (renderers omit — pin 18's surface arm)."""
    view = get_nation_intent(nation, world)
    if view.want_id is None:
        return None
    from backend.game_logic.formations import formed_display_name
    against_display = (formed_display_name(world, view.against)
                       if view.against else None)
    price_display = PRICE_DISPLAY.get(view.price, view.price)
    if view.against:
        summary = (f"prepared to go as far as "
                   f"{price_display.lower()} — {against_display} "
                   f"stands in the way (weight {view.weight})")
    else:
        summary = (f"prepared to go as far as "
                   f"{price_display.lower()} (weight {view.weight})")
    return {
        "want_id": view.want_id,
        "want_title": view.want_title,
        "against": view.against,
        "against_display": against_display,
        "weight": int(view.weight),
        "price": view.price,
        "price_display": price_display,
        "summary": summary,
    }


# ── AI-6 — the narration cap (§4.6, Stage F) ─────────────────────────────

# Blessed numbers (in-band tunable; shape escalates). The cap governs
# ROUTINE ladder movement ONLY (§4.6's v1.2 amendment): the §4.6a beats
# are EVENTS on their own dispatch types and are structurally exempt —
# this module's collapse never sees them.
INTENT_DISPATCH_CAP = 2            # routine movement lines per dispatch
RELEVANCE_CONCERNS_FRANCE = 2.0    # the design is about France's bloc
RELEVANCE_BORDERS_FRANCE = 1.5     # the court stands on France's frontier
RELEVANCE_FAR = 1.0                # a quarrel at the Danube

# The §4.6a beat types (seven) plus Stage E's two beat-class events
# (§18.1 handoff: the cap machinery must never collapse them — the exact
# jealousy failure §4.6a exists to prevent). Kept beside the cap so the
# exemption is one auditable tuple, asserted by the never-collapsed pin.
NARRATION_EXEMPT_EVENT_TYPES = (
    # beat 1 rides the incoming-proposal transport (not a dispatch line);
    # beats 2-7 + the Stage E pair are dispatch events:
    "crisis_brewing",          # beat 2 — and the fore-warning contract
    "coercive_demand",         # beat 3 (AI-AI arm)
    "broken_bargain",          # beat 4
    "volte_face",              # beat 5 (Stage E)
    "third_party_peace",       # beat 6
    "crisis_passed",           # beat 7
    "design_promoted",         # §3.6-3's own announced beat (Stage E)
    "guarantee_called",        # D5-3's plea — never routine
    "agenda_shift",            # the want changing IS an event (NA-1)
)


def _relevance(nation: str, view: IntentView, world) -> float:
    """Weight multiplier for the §4.6 relevance rule: `weight` alone
    cannot tell a Prussian design on Hanover from a Russo-Ottoman
    quarrel at the Danube. Derived, cheap (cached reads only)."""
    player = getattr(world, "player_nation", "France")
    if view.against:
        effective = world._top_overlord(view.against) or view.against
        if effective == player:
            return RELEVANCE_CONCERNS_FRANCE
    from backend.game_logic.agendas import agenda_concerns_player_bloc
    if agenda_concerns_player_bloc(nation, world):
        return RELEVANCE_CONCERNS_FRANCE
    # The AI-3r adjacency read: a WorldState method, one cached pass for
    # all nations (the exposure calculus' own substrate).
    for neighbour in world.get_neighbouring_nations(nation):
        effective = world._top_overlord(neighbour) or neighbour
        if effective == player:
            return RELEVANCE_BORDERS_FRANCE
    return RELEVANCE_FAR


def process_intent_movements(world) -> List[Dict]:
    """AI-6 (§4.6, Stage F): the dispatch reports ROUTINE movement on the
    ladder as news — a court hardening, a court easing — under the hard
    cap: at most INTENT_DISPATCH_CAP lines per dispatch, chosen by
    weight x proximity-to-French-interest, the rest collapsed into ONE
    "other courts stir" tail. The far war still happens and still shows
    in the ledger; it just does not spend the player's two lines.

    Movement = the PRICE rung changing while the WANT stands. A want
    change is the agenda_shift beat's news (NA-1) and stays silent here;
    survival postures belong to the crisis machinery; first observation
    records silently (the nation_agenda_seen idiom — boot decks must not
    spam turn 1). Dispatch-only by design: rung weather is texture, the
    campaign log stays for events.

    The poll runs once per turn AFTER process_agenda_shifts (the shift
    beat updates the want first, so a want-change turn never double
    announces). Deckless / legacy worlds: every court reads indifferent
    with no want — the seen map stays empty and nothing emits (pin 18).
    """
    seen = getattr(world, "nation_intent_seen", None)
    if seen is None:
        world.nation_intent_seen = {}
        seen = world.nation_intent_seen

    player = getattr(world, "player_nation", "France")
    vassals = getattr(world, "vassals", {}) or {}
    movements: List[Dict] = []
    for nation in sorted(world.get_active_nations()):
        if nation == player or nation in vassals:
            continue
        view = get_nation_intent(nation, world)
        if view.want_id is None or view.survival:
            # No want (or the Knife at the Throat — the crisis machinery
            # owns that drama): clear the record silently.
            seen.pop(nation, None)
            continue
        current = f"{view.want_id}|{view.price}"
        previous = seen.get(nation)
        seen[nation] = current
        if previous is None:
            continue  # first observation is bookkeeping, never news
        prev_want, _, prev_price = previous.partition("|")
        if prev_want != view.want_id:
            continue  # the want changed — agenda_shift announced it
        if prev_price == view.price:
            continue
        movements.append({
            "nation": nation,
            "view": view,
            "climbed": rung_index(view.price) > rung_index(prev_price),
        })

    if not movements:
        return []

    for movement in movements:
        view = movement["view"]
        movement["rank"] = float(view.weight) * _relevance(
            movement["nation"], view, world)
    movements.sort(key=lambda m: (-m["rank"], m["nation"]))

    from backend.game_logic.agendas import _live_nation_name
    from backend.game_logic.dispatch import queue_dispatch_event
    events: List[Dict] = []
    for movement in movements[:INTENT_DISPATCH_CAP]:
        view = movement["view"]
        nation_display = _live_nation_name(world, movement["nation"])
        price_display = PRICE_DISPLAY.get(view.price, view.price)
        vars_ = {
            "nation": nation_display,
            "want": view.want_title or "its design",
            "price": price_display.lower(),
        }
        event_type = ("intent_hardens" if movement["climbed"]
                      else "intent_eases")
        queue_dispatch_event(world, event_type, vars_, "always")
        events.append({
            "type": event_type,
            "nation": movement["nation"],
            "price": view.price,
        })
    overflow = len(movements) - INTENT_DISPATCH_CAP
    if overflow > 0:
        queue_dispatch_event(world, "intent_movement_tail", {
            "count": str(overflow),
            "plural": "" if overflow == 1 else "s",
            "verb": "s" if overflow == 1 else "",
            "poss": "its" if overflow == 1 else "their",
        }, "always")
        events.append({"type": "intent_movement_tail", "count": overflow})
    return events


# ── AI-1b — the mirror (§3.5) ────────────────────────────────────────────

# threat_level -> the rung Europe reads France at. The continent's alarm
# is the aggregate of observable French deeds (captures raise it, decay
# lowers it) — so restraint drifts France DOWN this ladder for free.
MIRROR_THREAT_RUNGS = (
    ("fight", 80),
    ("coerce", 60),
    ("align", 40),
    ("buy", 20),
    ("ask", 5),
)


def get_france_perceived_intent(world) -> Tuple[str, int, Optional[str]]:
    """(perceived_price, perceived_weight, perceived_target) — Europe's
    reading of the player, derived from observable actions only."""
    threat = int(getattr(world, "threat_level", 0))
    price = "indifferent"
    for rung, floor in MIRROR_THREAT_RUNGS:
        if threat >= floor:
            price = rung
            break
    return price, max(0, min(100, threat)), _perceived_target(world)


def _perceived_target(world) -> Optional[str]:
    """Who Europe thinks Napoleon is coming for: the non-vassal court with
    the most French corps standing on or against its soil. A defensive
    massing on the Rhine reads as a threat to whoever is across it,
    whether or not it was meant as one (§3.5)."""
    player = getattr(world, "player_nation", "France")
    presence: Dict[str, int] = {}

    def _credit(controller: Optional[str], amount: int) -> None:
        if not controller or controller == player:
            return
        effective = world._top_overlord(controller) or controller
        if effective == player:
            return
        # Corps massed on an ALLY's soil are staging, not threatening the
        # ally — the read falls on whoever borders that ground instead.
        if world.get_diplomatic_state(player, effective) in (
                "ALLIANCE", "DEFENSIVE_ALLIANCE"):
            return
        presence[effective] = presence.get(effective, 0) + amount

    for marshal in world.marshals.values():
        if getattr(marshal, "nation", None) != player:
            continue
        location = getattr(marshal, "location", None)
        region = world.regions.get(location) if location else None
        if region is None:
            continue
        _credit(getattr(region, "controller", None), 3)  # standing ON it
        for adjacent in getattr(region, "adjacent_regions", []) or []:
            neighbour = world.regions.get(adjacent)
            if neighbour is not None:
                _credit(getattr(neighbour, "controller", None), 1)
    if not presence:
        return None
    return min(presence, key=lambda n: (-presence[n], n))


def build_france_mirror_payload(world) -> Optional[dict]:
    """The player's own row: Europe's derived reading of France (§3.5).
    None on non-hegemon legacy/bare worlds where no reading exists
    (deckless-neutral — the legacy ledger is byte-identical)."""
    player = getattr(world, "player_nation", "France")
    from backend.game_logic.agendas import _hegemon
    hegemon, share = _hegemon(world)
    if getattr(world, "sovereign_map", "legacy") != "europe":
        return None
    price, weight, target = get_france_perceived_intent(world)
    from backend.game_logic.formations import formed_display_name
    if hegemon == player:
        read_as = (f"The hegemon of Europe — "
                   f"{share:.0%} of the continent's weight")
    elif hegemon:
        read_as = (f"A great power in "
                   f"{formed_display_name(world, hegemon)}'s shadow")
    else:
        read_as = "A power among powers"
    price_display = PRICE_DISPLAY.get(price, price)
    lines = [
        f"Read as: {read_as}.",
        (f"The courts believe he will go as far as "
         f"{price_display.lower()} (alarm {weight})."),
    ]
    if target:
        lines.append(
            f"They think he is coming for "
            f"{formed_display_name(world, target)} — his corps stand "
            f"against their soil.")
    return {
        "read_as": read_as,
        "hegemon_share": round(float(share), 3) if hegemon == player else 0.0,
        "perceived_price": price,
        "perceived_price_display": price_display,
        "perceived_weight": int(weight),
        "perceived_target": target,
        "perceived_target_display": (
            formed_display_name(world, target) if target else None),
        "lines": lines,
    }
