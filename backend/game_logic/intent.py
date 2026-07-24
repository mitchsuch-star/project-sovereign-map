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
from typing import Dict, Optional, Tuple

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
WEIGHT_AT_WAR_WITH_HOLDER = 10       # the war IS the pursuit
WEIGHT_RELATION_COLD = 8             # relation <= -40 with `against`
WEIGHT_RELATION_CHILLY = 4           # relation <= 0
WEIGHT_RELATION_WARM = -8            # relation > 30
WEIGHT_OPPORTUNISM_ONE_WAR = 6       # §3.2 — the holder is busy
WEIGHT_OPPORTUNISM_TWO_WARS = 10     # …deeply busy
WEIGHT_OPPORTUNISM_BANKRUPT = 3      # …or bankrupt
WEIGHT_SURVIVAL = 95
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


def _derive_weight(nation: str, agenda: AgendaView,
                   against: Optional[str], world) -> int:
    weight = WEIGHT_BASE_BY_TYPE.get(agenda.type, 40)
    # AI-2c (§3.4): the statecraft weight modifier — authored 0 for every
    # 1805 court (boot-neutral, pin 1); the wire exists for scenarios
    # that author a hungrier or sleepier great power.
    from backend.game_logic.statecraft import statecraft_weight_mod
    weight += statecraft_weight_mod(world, nation)
    if against:
        if world.is_at_war(nation, against):
            weight += WEIGHT_AT_WAR_WITH_HOLDER
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
