"""Nation Agendas — "The Designs of the Powers" (NA-0 substrate).

Gate record + build contract: docs/NATION_AGENDAS_SPEC.md (§0 gate record,
§3 architecture, §4 authored decks, §5 consumption seams, §6 blessed numbers).

Authored decks live in the scenario `agendas` key (stored on
`world.agendas`, the marshal_pool precedent); the ACTIVE agenda is DERIVED
each turn from live state. Deck order = priority order — the first agenda
whose predicate holds is active; exactly one active per nation. Vassals
never activate agendas while vassalized (the dormant satellite decks —
KingdomOfItaly, Holland — wake on independence). A built-in survival
override — "The Knife at the Throat" — outranks the deck when the capital
or the majority of the homeland is lost (the get_authority_proxy 25-band).

GR5: every helper takes a nation parameter; nothing is nation-hardcoded.
GR6: activation, satisfaction, and resolve are deterministic pure reads.
GR8: one cached evaluation per nation per turn (`_agenda_cache`, turn-keyed
and cleared by invalidate_bloc_members_cache — which every region-control,
vassalage, AND diplomatic-state seam reaches, since war/alliance geometry
changes activation too; treasury-only drift self-heals at the turn key).
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from backend.display_names import display_nation

# ══════════════════════ BLESSED NUMBERS (spec §6) ═════════════════════════
# In-band tunable per the standing rule; structural changes escalate.
AGENDA_ACCEPT_ADVANCE = 12            # acceptance term: offer advances the design
AGENDA_ACCEPT_ENTRENCH = -8           # acceptance term: offer entrenches denial
AGENDA_RESOLVE_ADVANCING = -8         # on effective_p1_threshold: fights longer
AGENDA_RESOLVE_SATISFIED = 10         # on effective_p1_threshold: sues sooner
AGENDA_SEPARATE_PEACE_SCORE = -30     # Pressburg arm vs stock coalition -50
AGENDA_PERSISTENCE_COOLDOWN_DELTA = -2  # hawk re-ask cooldown reduction (turns)
AGENDA_TARGET_DISTANCE_BONUS = 2      # distance-equivalent credit in target picks
AGENDA_SUBSIDY_TIER_2 = 300           # paymaster subsidy above 4,000 treasury
AGENDA_SUBSIDY_TIER_3 = 400           # paymaster subsidy above 8,000 treasury
AGENDA_SUBSIDY_CAP = 400
AGENDA_GRUDGE_TURNS = 10              # post-peace grudge horizon
AGENDA_GRUDGE_CAP = 2                 # +threat/turn cap across all nations
AGENDA_VIOLATION_RELATION_PENALTY = -25  # the Ansbach trap, one-time per pair
AGENDA_VIOLATION_COOLDOWN = 10        # turns between violation firings per pair
HEGEMON_BLOC_SHARE_FLOOR = 0.33       # default share floor (deny / contain)

# The closed set of code-owned agenda types (spec §3.1).
AGENDA_TYPES = (
    "acquire_regions",
    "deny_regions",
    "contain_hegemon",
    "paymaster",
    "guard_neutrality",
)

# The implicit survival posture (never authored — spec §3.1; the validator
# rejects an authored id colliding with the sentinel). Title and stance
# render as "Survival — The dynasty above all." via the ledger's join.
SURVIVAL_AGENDA_ID = "survival"
SURVIVAL_TITLE = "Survival"


@dataclass(frozen=True)
class AgendaView:
    """Read-only view of a nation's ACTIVE agenda for one turn."""
    nation: str
    id: str
    type: str
    title: str
    blurb: str = ""
    regions: Tuple[str, ...] = ()
    params: dict = field(default_factory=dict)
    survival: bool = False


# ═══════════════════════ PREDICATE PRIMITIVES ═════════════════════════════

def _is_vassal(world, nation: str) -> bool:
    return nation in (getattr(world, "vassals", {}) or {})


def _region_controller(world, region_name: str) -> Optional[str]:
    region = world.regions.get(region_name)
    return getattr(region, "controller", None) if region is not None else None


def _controlled_by_self_or_vassal(world, nation: str, region_name: str) -> bool:
    """True when the nation, or a nation in its vassal chain, holds the region.

    Uses the cycle-safe `_top_overlord` walk so vassal-of-vassal holdings
    count for the top lord (the get_bloc_members idiom).
    """
    controller = _region_controller(world, region_name)
    if not controller:
        return False
    if controller == nation:
        return True
    return world._top_overlord(controller) == nation


def _hegemon(world, nation: Optional[str] = None) -> Tuple[Optional[str], float]:
    """(leader, share) of the hegemon a court fears.

    Without `nation`: the raw largest bloc — the global view shared with
    coalition/diplomacy.

    With `nation`: the largest bloc that court is NOT part of. The raw
    helper answers "who is biggest", which is the wrong question for an
    anti-hegemon design. When the coalition Britain funds finally
    out-masses France, the raw answer becomes a CO-BELLIGERENT, and every
    deny/contain/paymaster predicate silently switches off — the designs
    delete themselves at the moment they start succeeding. Worse, the deny
    satisfaction check then read TRUE while France still held the Scheldt,
    handing Britain +10 resolve and an early separate peace precisely
    because France was winning the thing Britain denies.

    NOTE (phase audit, §19): the raw form must NEVER be used for a deny
    question. `coalition.form_coalition` writes no ALLIANCE rows, so the
    denier is routinely in a bloc of ONE and the raw answer points at a
    co-belligerent's camp. The share floor likewise governs ACTIVATION
    only — gating the satisfaction exclusion set on it re-opened the same
    P1. Both mistakes were made and caught inside this fix.

    Court-relative resolution keeps a design pointed at the power it was
    authored against. Boot-identical on the shipped scenario: France is
    the largest bloc and no anti-France court sits inside it, so the two
    forms agree until the geometry inverts.

    Local import: coalition pulls in the wider diplomacy stack.
    """
    from backend.game_logic.coalition import (
        _identify_max_bloc_share, identify_ranked_bloc_shares,
    )
    if nation is None:
        return _identify_max_bloc_share(world)
    for leader, share in identify_ranked_bloc_shares(world):
        if leader is None:
            return (None, 0.0)
        if nation == leader or nation in set(world.get_bloc_members(leader)):
            continue        # one's own bloc is never one's hegemon
        return (leader, share)
    return (None, 0.0)


def survival_override_active(world, nation: str) -> bool:
    """The Knife at the Throat (spec §3.1): capital lost OR majority of
    `nation_starting_regions` lost — the get_authority_proxy 25-band
    (jealousy.py), reconstructed here without the player-tracker arm
    (agenda survival is territorial for every nation, player included)."""
    home = list(getattr(world, "nation_starting_regions", {}).get(nation, []) or [])
    if not home:
        return False
    capital = world.get_nation_capital(nation)
    capital_region = world.regions.get(capital) if capital else None
    capital_held = bool(capital_region and capital_region.controller == nation)
    held = sum(
        1 for region_name in home
        if _region_controller(world, region_name) == nation
    )
    return (not capital_held) or (held * 2 < len(home))


# ═══════════════════════ PER-TYPE ACTIVATION ══════════════════════════════

def _acquire_active(world, nation: str, regions) -> bool:
    """Active while >=1 target is not controlled by self (and the holder is
    not self's vassal)."""
    return any(
        not _controlled_by_self_or_vassal(world, nation, r) for r in regions
    )


def _deny_active(world, nation: str, regions) -> bool:
    """Active while >=1 target is controlled by the hegemon's bloc
    (share >= floor). A nation is never threatened by its own bloc —
    inactive when self IS the hegemon or sits inside the hegemon's bloc."""
    hegemon, share = _hegemon(world, nation)
    if hegemon is None or share < HEGEMON_BLOC_SHARE_FLOOR:
        return False
    bloc = set(world.get_bloc_members(hegemon))
    if nation in bloc:
        return False
    return any(_region_controller(world, r) in bloc for r in regions)


def _contain_active(world, nation: str, share_floor: float) -> bool:
    """Active while the hegemon bloc share >= floor AND self is outside
    that bloc."""
    hegemon, share = _hegemon(world, nation)
    if hegemon is None or share < share_floor:
        return False
    return nation not in set(world.get_bloc_members(hegemon))


def _paymaster_active(world, nation: str, treasury_floor: int) -> bool:
    """Posture: at war with the hegemon OR member of an active coalition
    against the hegemon, AND treasury above the authored floor."""
    hegemon, _share = _hegemon(world, nation)
    if hegemon is None or hegemon == nation:
        return False
    treasury = int((getattr(world, "nation_gold", {}) or {}).get(nation, 0))
    if treasury <= int(treasury_floor):
        return False
    if world.is_at_war(nation, hegemon):
        return True
    coalition = getattr(world, "active_coalition", None)
    if coalition and nation in (coalition.get("members") or []):
        return coalition.get("target_nation") == hegemon
    return False


def _belligerent(world, a: str, b: str) -> bool:
    """WAR *or* ARMISTICE. An armistice is a pause in a war, not peace.

    `diplomacy.py` already states the doctrine ("ARMISTICE is
    belligerent-adjacent and deliberately excluded; it is treated like WAR
    for this check") and the NA-2 entrench arm already pairs
    ("WAR", "ARMISTICE"). The neutrality machinery has to agree, or an
    armistice both WAKES the paused opponent's guard design and STRIPS the
    war exemption from the army standing on its soil because of that very
    war — outrage priced at -25 for holding still.
    """
    return world.get_diplomatic_state(a, b) in ("WAR", "ARMISTICE")


def _has_belligerency(world, nation: str) -> bool:
    """True while the nation is a belligerent anywhere — WAR or ARMISTICE.

    Scans `diplomatic_states` exactly as `get_nations_at_war_with` does
    (a sparse ~n^2-bounded dict over the roster, not a region scan — GR8).
    """
    if world.get_nations_at_war_with(nation):
        return True
    for key, state in (getattr(world, "diplomatic_states", {}) or {}).items():
        if state == "ARMISTICE" and nation in key.split("|"):
            return True
    return False


def _guard_active(world, nation: str) -> bool:
    """Posture: active while self is a non-belligerent.

    An armistice does not restore neutrality — a power that has paused its
    war is not a neutral whose neutrality can be violated.
    """
    return not _has_belligerency(world, nation)


def _entry_active(world, nation: str, entry: dict) -> bool:
    agenda_type = entry.get("type")
    regions = list(entry.get("regions") or [])
    if agenda_type == "acquire_regions":
        return _acquire_active(world, nation, regions)
    if agenda_type == "deny_regions":
        return _deny_active(world, nation, regions)
    if agenda_type == "contain_hegemon":
        # (x or default): the key may be present-but-None (CLAUDE.md trap).
        floor = float(entry.get("share_floor") or HEGEMON_BLOC_SHARE_FLOOR)
        return _contain_active(world, nation, floor)
    if agenda_type == "paymaster":
        floor = int(entry.get("treasury_floor") or 0)
        return _paymaster_active(world, nation, floor)
    if agenda_type == "guard_neutrality":
        return _guard_active(world, nation)
    return False


def _view_from_entry(nation: str, entry: dict) -> AgendaView:
    params = {
        k: v for k, v in entry.items()
        if k not in ("id", "type", "title", "blurb", "regions")
    }
    return AgendaView(
        nation=nation,
        id=str(entry.get("id", "")),
        type=str(entry.get("type", "")),
        title=str(entry.get("title", "")),
        blurb=str(entry.get("blurb", "")),
        regions=tuple(entry.get("regions") or ()),
        params=params,
    )


# ═══════════════════════ THE DERIVATION (cached, GR8) ═════════════════════

def get_active_agenda(nation: str, world) -> Optional[AgendaView]:
    """The one derivation chokepoint. Per-turn cached on the
    _active_nations_cache idiom: cache + cache_turn, rebuilt when
    current_turn moves, cleared by invalidate_active_nations_cache()
    (region control changes activation).

    Order: vassal dormancy -> elimination -> survival override -> deck
    (first predicate that holds wins) -> None.
    """
    cache = getattr(world, "_agenda_cache", None)
    cache_turn = getattr(world, "_agenda_cache_turn", -1)
    if cache is None or cache_turn != world.current_turn:
        cache = {}
        world._agenda_cache = cache
        world._agenda_cache_turn = world.current_turn
    if nation in cache:
        return cache[nation]

    view: Optional[AgendaView] = None
    if not _is_vassal(world, nation):
        if nation in world.get_active_nations():
            if survival_override_active(world, nation):
                view = AgendaView(
                    nation=nation,
                    id=SURVIVAL_AGENDA_ID,
                    type=SURVIVAL_AGENDA_ID,
                    title=SURVIVAL_TITLE,
                    survival=True,
                )
            else:
                deck = (getattr(world, "agendas", {}) or {}).get(nation) or []
                for entry in deck:
                    # AI-2b (§3.1a b / §6 D5-1): a design bought off by
                    # agreement is SUSPENDED — the deck advances past it
                    # while the compensation bargain stands, and it wakes
                    # the turn the bargain is reneged (record removed).
                    if _design_bought_off(world, nation,
                                          str(entry.get("id") or "")):
                        continue
                    if _entry_active(world, nation, entry):
                        view = _view_from_entry(nation, entry)
                        break

    cache[nation] = view
    return view


def _design_bought_off(world, nation: str, design_id: str) -> bool:
    """AI-2b: is this deck entry suspended by a standing compensation
    bargain? Reads the raw serialized store directly (shape documented in
    instruments.py) — no import cycle with the instruments module."""
    if not design_id:
        return False
    for record in getattr(world, "compensation_bargains", []) or []:
        if (record.get("recipient") == nation
                and record.get("design_id") == design_id):
            return True
    return False


# ═══════════════════ SATISFACTION / RESOLVE (pure, NA-2/3 feeders) ════════

def _entry_satisfied(world, nation: str, entry: dict) -> bool:
    """Satisfaction per the spec §3.1 table — computed per type, NOT as
    ¬active: deny/contain activation carries a self-in-hegemon-bloc gate
    that is a dormancy condition, never satisfaction (allying INTO the
    hegemon's bloc does not fulfil the design). Postures (paymaster/guard)
    never satisfy."""
    agenda_type = entry.get("type")
    if agenda_type == "acquire_regions":
        # Exact complement: all targets self-or-vassal controlled.
        return not _acquire_active(world, nation, list(entry.get("regions") or []))
    if agenda_type == "deny_regions":
        # SATISFACTION IS A STATEMENT ABOUT THE PROVINCES, NOT ABOUT BLOC
        # RANKINGS. Britain's design is the Scheldt; whether Austria has
        # grown larger than France is not an answer to "is the Scheldt in
        # French hands".
        #
        # The earlier cut asked "is any target in the hands of the largest
        # bloc I am not in", with a guard for sitting inside the dominant
        # bloc. Both halves keyed on bloc membership, and `get_bloc_members`
        # admits only vassal chains and formal ALLIANCE/DEFENSIVE_ALLIANCE
        # states — but `coalition.form_coalition` writes NO alliance rows
        # (it writes `active_coalition`, declares war, and nudges relations).
        # A coalition formed in play therefore left Britain in a bloc of
        # one, the guard silent, and the design reading SATISFIED while
        # France and Holland held all three targets: +10 resolve and an
        # early separate peace, for winning nothing, with no player-facing
        # surface able to explain it (active view None => no covets, no
        # acceptance term, no ledger Design row).
        #
        # Deny does NOT mean "mine". It means "not THEIRS" — a free Dutch
        # buffer is the British war aim, not a British possession, which is
        # why §11.2's authored mirror has the United Netherlands SATISFY
        # this design without a province changing hands to London. So the
        # question per province is: is the power holding it one this court
        # regards as a threat?
        #
        # A province counts as DENIED when, and only when, it is held by:
        #   (a) ourselves or our own client — denied outright, whatever the
        #       geometry. This is the D70 false-negative fix: a court holding
        #       its own targets is satisfied even while allied to the hegemon.
        #   (b) a power below the great-power tier that is NOT inside the
        #       hegemon's bloc — the buffer state. This is why §11.2's
        #       United Netherlands satisfies the design without a province
        #       ever passing to London, and why a French SATELLITE holding
        #       Amsterdam does not (the authored blurb is literally "London
        #       will not rest while the bloc holds it").
        # Any other great power holding it denies nothing — which preserves
        # D68 (allying INTO the camp that holds the Scheldt is DORMANCY, not
        # fulfilment) and guard 2's ruling that a cut-down France still
        # holding the targets satisfies nothing: a beaten great power is
        # still a great power, and the design was never about France's size.
        # Unknown hands never claim success.
        regions = list(entry.get("regions") or [])
        if not regions:
            return False          # a design with no provinces never lands
        # Court-relative, and NO share-floor gate: the floor governs
        # ACTIVATION (is the design urgent), never SATISFACTION. Reading the
        # RAW largest bloc here re-opened the very P1 this arm exists to
        # close — once a co-belligerent out-masses France the exclusion set
        # points at the wrong camp entirely.
        hegemon, _share = _hegemon(world, nation)
        hegemon_bloc = (set(world.get_bloc_members(hegemon))
                        if hegemon is not None else set())
        for region_name in regions:
            if _controlled_by_self_or_vassal(world, nation, region_name):
                continue                                        # (a)
            controller = _region_controller(world, region_name)
            if controller is None:
                return False
            # Resolve the vassal chain exactly as arm (a) does. A French
            # SATELLITE is a minor power on paper — reading the literal
            # controller let Holland-holding-Amsterdam pass as a neutral
            # buffer while it was still Napoleon's client, which is the P1
            # again through the back door.
            effective = world._top_overlord(controller) or controller
            if world.get_power_tier(effective) == "major":
                return False
            if effective in hegemon_bloc or controller in hegemon_bloc:
                return False
        return True                                             # (b)
    if agenda_type == "contain_hegemon":
        # "share < floor" — regardless of where self sits.
        floor = float(entry.get("share_floor") or HEGEMON_BLOC_SHARE_FLOOR)
        hegemon, share = _hegemon(world, nation)
        return hegemon is None or share < floor
    return False


def entry_satisfied(world, nation: str, entry: dict) -> bool:
    """Public wrapper over the per-type satisfaction predicate.

    NA-6 needs satisfaction for a RAW deck entry, not for the active view:
    an acquire entry is active only while UNMET, so a formable entry is
    already inactive on the tick it satisfies (see formations.py's module
    docstring). `is_agenda_satisfied` cannot serve — it takes a view that
    is unobtainable at exactly that moment.
    """
    return _entry_satisfied(world, nation, entry)


def _satisfied_views(world, nation: str) -> List[AgendaView]:
    """EVERY satisfied deck entry, highest-priority first.

    All of them, not just the first: a court that wins its WHOLE deck has no
    active view and only one "won" entry, so the later design's provinces
    fell out of both ENTRENCH arms — Austria holding all five design
    provinces priced a demand for Milan at -8 and one for Munich at 0, and
    Munich had priced -8 before Swabia was taken. That is this fix's own
    stated pathology surviving in the fully-satisfied case.

    A court that has WON its design has no ACTIVE agenda: activation is the
    complement of satisfaction for acquire, and a deny goes quiet the moment
    the provinces are safe. Both acceptance scorers gate on the active view,
    so the court that just took Milan priced a demand for Milan at 0 while
    the court still fighting for it priced the same demand at -8 — more
    complete success bought LESS defence of the very province won, and spec
    line 39's "sues to lock its gains" shipped its "sues" half (+10 resolve,
    Pressburg) with nothing delivering "lock".

    ENTRENCH arms fall back here so that success cannot make a court cheaper
    to rob. Deliberately NOT offered to the ADVANCE arms: a design already
    satisfied cannot be advanced, and paying +12 for handing a court what it
    already holds would be free acceptance for nothing.

    Gated exactly like `get_active_agenda` — a vassalized, eliminated, or
    survival-overridden court has no design voice.
    """
    if _is_vassal(world, nation) or nation not in world.get_active_nations():
        return []
    if survival_override_active(world, nation):
        return []
    return [
        _view_from_entry(nation, entry)
        for entry in ((getattr(world, "agendas", {}) or {}).get(nation) or [])
        if _entry_satisfied(world, nation, entry)
    ]


def is_agenda_satisfied(view: AgendaView, world) -> bool:
    if view is None or view.survival:
        return False
    entry = {"type": view.type, "regions": list(view.regions), **view.params}
    return _entry_satisfied(world, view.nation, entry)


def _war_advances_agenda(view: AgendaView, opponent: str, world) -> bool:
    """Does war against `opponent` advance the active agenda?
    acquire: the opponent's bloc holds >=1 unmet target.
    deny: the design is scoped to the HEGEMON's bloc — advancing means
    fighting a member of that bloc while it holds >=1 target.
    contain: the opponent sits in the hegemon's bloc while share >= floor."""
    if view is None or view.survival:
        return False
    if view.type == "acquire_regions":
        opponent_bloc = set(world.get_bloc_members(opponent))
        for region_name in view.regions:
            if _controlled_by_self_or_vassal(world, view.nation, region_name):
                continue
            if _region_controller(world, region_name) in opponent_bloc:
                return True
        return False
    if view.type == "deny_regions":
        hegemon, share = _hegemon(world, view.nation)
        if hegemon is None or share < HEGEMON_BLOC_SHARE_FLOOR:
            return False
        bloc = set(world.get_bloc_members(hegemon))
        if opponent not in bloc:
            return False
        return any(_region_controller(world, r) in bloc for r in view.regions)
    if view.type == "contain_hegemon":
        hegemon, share = _hegemon(world, view.nation)
        floor = float(view.params.get("share_floor") or HEGEMON_BLOC_SHARE_FLOOR)
        if hegemon is None or share < floor:
            return False
        return opponent in set(world.get_bloc_members(hegemon))
    return False


def _court_design_satisfied(world, nation: str) -> bool:
    """The Pressburg shape (§5.4/§5.5): the survival override is active OR
    the deck's HIGHEST-PRIORITY entry is satisfied — the court got what it
    most wanted (or is fighting for its life) and peace locks it in."""
    if survival_override_active(world, nation):
        return True
    deck = (getattr(world, "agendas", {}) or {}).get(nation) or []
    return bool(deck and _entry_satisfied(world, nation, deck[0]))


def get_agenda_resolve_delta(nation: str, opponent: str, world) -> int:
    """Pure NA-3 feeder for effective_p1_threshold (spec §5.5) — NOT yet
    consumed at NA-0..NA-2 (no consumer changes before NA-3).

    Survival override, or the deck's HIGHEST-PRIORITY entry satisfied
    (the court got what it most wanted — the Pressburg shape), pushes
    toward peace; a war that advances the active agenda hardens resolve;
    an irrelevant war deliberately changes nothing.

    Gated exactly like get_active_agenda: a vassalized or eliminated
    nation has no agenda voice — 0 (the lord's war is not the client's
    design; the dormancy rule holds at every entry point).
    """
    if _is_vassal(world, nation) or nation not in world.get_active_nations():
        return 0
    if _court_design_satisfied(world, nation):
        return AGENDA_RESOLVE_SATISFIED
    view = get_active_agenda(nation, world)
    if view is not None and _war_advances_agenda(view, opponent, world):
        return AGENDA_RESOLVE_ADVANCING
    return 0


def agenda_separate_peace_ready(nation: str, world) -> bool:
    """NA-2 §5.4 — the Pressburg arm's predicate for the P1 coalition-
    loyalty override: a coalition member whose court's design is SATISFIED
    (or whose survival override is active) may sue for a separate peace at
    `war_score < AGENDA_SEPARATE_PEACE_SCORE` instead of the stock -50.

    Vassal/elimination dormancy gates apply like every other entry point.
    The SURVIVAL arm deliberately needs no authored deck — the Knife at
    the Throat (§3.1) is universal, so a capital-lost coalition member on
    ANY world (legacy fixtures included) may break ranks to save the
    dynasty. Pinned in test_deckless_survival_still_ready."""
    if _is_vassal(world, nation) or nation not in world.get_active_nations():
        return False
    return _court_design_satisfied(world, nation)


def agenda_concerns_player_bloc(nation: str, world) -> bool:
    """True when the nation's active agenda is aimed at holdings of the
    player's bloc — the NA-1 arm that lets `determine_ai_offer_decision_reason`
    voice `agenda_pursuit` deterministically (spec §5.1).

    deny is HEGEMON-anchored (§3.1): it concerns the player only when the
    player sits in the hegemon's bloc — a deny design aimed at some other
    hegemon is not about France, however many listed regions France holds."""
    player = getattr(world, "player_nation", "France")
    return _agenda_concerns_bloc_of(nation, player, world)


def _agenda_concerns_bloc_of(nation: str, anchor: str, world) -> bool:
    """The anchor-general body of `agenda_concerns_player_bloc` (AI-5b:
    emergent designs make grudges point at non-player authors, so the
    grudge query below takes an author). Player-anchor calls are
    byte-identical to the pre-refactor function."""
    view = get_active_agenda(nation, world)
    if view is None or view.survival:
        return False
    if view.type == "acquire_regions":
        anchor_bloc = set(world.get_bloc_members(anchor))
        for region_name in view.regions:
            if _controlled_by_self_or_vassal(world, nation, region_name):
                continue
            if _region_controller(world, region_name) in anchor_bloc:
                return True
        return False
    if view.type == "deny_regions":
        hegemon, share = _hegemon(world, nation)
        if hegemon is None or share < HEGEMON_BLOC_SHARE_FLOOR:
            return False
        bloc = set(world.get_bloc_members(hegemon))
        if anchor not in bloc:
            return False
        return any(_region_controller(world, r) in bloc for r in view.regions)
    if view.type == "contain_hegemon":
        hegemon, share = _hegemon(world, nation)
        floor = float(view.params.get("share_floor") or HEGEMON_BLOC_SHARE_FLOOR)
        return hegemon == anchor and share >= floor
    return False


def agenda_satisfiable_by_player(nation: str, world) -> bool:
    """True when the nation's active agenda could be satisfied AT THE TABLE
    by the player — an acquire/deny design whose unmet targets the player
    can actually SIGN AWAY. contain/paymaster/guard postures are never
    table-satisfiable. Feeds the war-room "satisfy their design"
    recommendation (spec §5.1).

    Gated on player-DIRECT control, not bloc control (phase review, July
    18, 2026). The counsel promises "we hold what their court wants —
    offer it at the table", but `generate_suggested_terms` filters
    coveted regions to `world.get_nation_regions(player)`, i.e. what the
    player's own crown holds. A target sitting with a VASSAL made the
    counsel fire, cost an action, open talks, and then offer an unrelated
    province — scoring the design term at ENTRENCH, strictly worse than
    ignoring the advice. This mirrors the narrowing §16 already applied
    to NA-5's ultimatum trigger for the same reason: the cession arms can
    only transfer what `region.controller` says the signer owns.
    """
    view = get_active_agenda(nation, world)
    if view is None or view.survival:
        return False
    if view.type not in ("acquire_regions", "deny_regions"):
        return False
    if not agenda_concerns_player_bloc(nation, world):
        return False
    player = getattr(world, "player_nation", "France")
    direct = set(world.get_nation_regions(player))
    return any(region in direct for region in get_agenda_covets(nation, world))


# ═══════════════════ DIPLOMACY TEETH (NA-2, spec §5.2–§5.4) ═══════════════

def _proposal_territory_content(proposal: Dict) -> Tuple[set, set]:
    """(ceded_to_target, demanded_from_target) region-name sets from a
    bilateral proposal's territorial vocabulary: sweetener/demand dicts of
    type territory_cede/territory (with `regions` list or `region` key)
    plus the string `territory_<lower>` clause form, which always rides a
    cession to the target (the generate_suggested_terms shape). String
    clauses are matched case-insensitively at the call site."""
    def _regions_of(item) -> List[str]:
        if not isinstance(item, dict):
            return []
        if item.get("type") not in ("territory_cede", "territory"):
            return []
        names = list(item.get("regions") or [])
        single = item.get("region")
        if single:
            names.append(single)
        return [str(n) for n in names if n]

    ceded = set()
    demanded = set()
    for sweetener in (proposal.get("sweeteners") or []):
        ceded.update(_regions_of(sweetener))
    for demand in (proposal.get("demands") or []):
        demanded.update(_regions_of(demand))
    for clause in (proposal.get("clauses") or []):
        if isinstance(clause, str) and clause.startswith("territory_"):
            ceded.add(clause[len("territory_"):])
    return ceded, demanded


def agenda_acceptance_mod(proposal: Dict, world) -> int:
    """NA-2 §5.2 — the bounded agenda acceptance term, computed in
    calculate_acceptance as a standalone additive term OUTSIDE the
    composite floor (the respected_estate shape). One active agenda per
    nation caps exposure at +ADVANCE / ENTRENCH.

    ADVANCE (+12): the offer's territorial content moves an unmet design
    target into satisfaction position — acquire: a target region ceded TO
    the nation; deny: a listed region ceded OUT of the hegemon's bloc.

    ENTRENCH (-8): the offer asks the court to accept the loss of its
    design — a demand stripping a HELD design region (priced on ANY
    proposal type: an armistice that takes Milan is a real ask with real
    content), or a formal PEACE — from WAR or ARMISTICE state — that ends
    a conflict which was advancing the design without returning anything
    (Austria refuses the peace that does not return Milan — and the
    breakdown says so). A BARE armistice deliberately does NOT entrench:
    the pause itself legitimizes nothing (protects the freshly-tuned
    AUD-b armistice behavior — AUD-b armistices carry no design content).
    """
    target = proposal.get("target_nation", "")
    proposer = proposal.get("proposer_nation", "")
    if not target:
        return 0
    view = get_active_agenda(target, world)
    if view is not None and view.survival:
        return 0
    # A WON design still defends itself. Both the no-active-design case AND
    # the case where a LATER deck entry has since activated: Austria that
    # holds Milan is flying primacy_germany, and pricing the demand for
    # Milan against THAT entry found no match at all (see _satisfied_view).
    won = _satisfied_views(world, target)
    if view is None and not won:
        return 0

    ceded, demanded = _proposal_territory_content(proposal)

    def _match(names: set, of_view) -> List[str]:
        lower = {r.lower(): r for r in of_view.regions}
        return [lower[n.lower()] for n in names if n.lower() in lower]

    # ── ADVANCE ── (only the LIVE design; a won one has nothing to advance,
    # and paying +12 for handing a court what it already holds is free
    # acceptance for nothing)
    if view is not None:
        ceded_targets = _match(ceded, view)
        if view.type == "acquire_regions":
            for region_name in ceded_targets:
                if not _controlled_by_self_or_vassal(world, target, region_name):
                    return AGENDA_ACCEPT_ADVANCE
        elif view.type == "deny_regions":
            hegemon, share = _hegemon(world, target)
            if hegemon is not None and share >= HEGEMON_BLOC_SHARE_FLOOR:
                bloc = set(world.get_bloc_members(hegemon))
                for region_name in ceded_targets:
                    if _region_controller(world, region_name) in bloc:
                        return AGENDA_ACCEPT_ADVANCE

    # ── ENTRENCH ── priced against the live design AND every won one
    for candidate in ([view] if view is not None else []) + won:
        for region_name in _match(demanded, candidate):
            if _controlled_by_self_or_vassal(world, target, region_name):
                return AGENDA_ACCEPT_ENTRENCH
    if view is None:
        return 0
    # The formal-peace arm fires from WAR *or* ARMISTICE — the designed
    # armistice-first route still ends in "the peace that does not return
    # Milan"; only the armistice itself (a pause) is exempt.
    if (proposal.get("type") == "peace"
            and proposer
            and world.get_diplomatic_state(proposer, target)
            in ("WAR", "ARMISTICE")
            and _war_advances_agenda(view, proposer, world)):
        return AGENDA_ACCEPT_ENTRENCH
    return 0


def get_agenda_covets(nation: str, world) -> List[str]:
    """NA-2 §5.2 covets unification — the live-agenda half of the covets
    source: the nation's ACTIVE design's outstanding territorial wants,
    in authored order. acquire: unmet targets; deny: listed regions
    currently in the hegemon bloc's hands (taking them IS the design).
    Postures and dormant/absent decks return [] — consumers fall back to
    the static NATION_DESIRE_PROFILES row."""
    view = get_active_agenda(nation, world)
    if view is None or view.survival:
        return []
    if view.type == "acquire_regions":
        return _unmet_targets(view, world)
    if view.type == "deny_regions":
        hegemon, share = _hegemon(world, nation)
        if hegemon is None or share < HEGEMON_BLOC_SHARE_FLOOR:
            return []
        bloc = set(world.get_bloc_members(hegemon))
        return [r for r in view.regions
                if _region_controller(world, r) in bloc]
    return []


def ask_advances_agenda(nation: str, proposal_type: str, world) -> bool:
    """NA-2 §5.3 — does an AI->player ask of this proposal type ADVANCE the
    nation's active agenda? In the current ask vocabulary only one pairing
    qualifies: a guard_neutrality court asking for non_aggression (the pact
    IS its design — Prussia's armed neutrality seeks the guarantee).
    Territorial asks don't exist pre-NA-5 (R162 ultimatums own them);
    postures aimed at the hegemon are never advanced by treating with it."""
    view = get_active_agenda(nation, world)
    if view is None or view.survival:
        return False
    return view.type == "guard_neutrality" and proposal_type == "non_aggression"


def vassal_holds_agenda_target(courter: str, vassal_nation: str, world) -> bool:
    """NA-2 §5.4 courting-bias rider — does this vassal's territory contain
    a region the courter's active design WANTS, per the unified covets
    definition (get_agenda_covets: acquire = unmet targets, deny = targets
    in the hegemon bloc's hands — a listed region outside the bloc is not
    a live want, so peeling its holder buys nothing)? Bias only: the
    courting machinery's eligibility, cost, and cooldowns are untouched."""
    return any(
        _region_controller(world, region_name) == vassal_nation
        for region_name in get_agenda_covets(courter, world)
    )


# ═══════════════════ WAR COUPLING (NA-3, spec §5.5–§5.9 + §7 riders) ══════

def get_paymaster_nation(world) -> Optional[str]:
    """NA-3 §5.7 — resolve the coalition member funding the war chest.

    Deck worlds: the first coalition member (member order, deterministic)
    whose authored deck carries a `paymaster` entry with its POSTURE
    predicate live (`_paymaster_active` — at war with the hegemon or in
    the active coalition against it, treasury above the authored floor),
    not vassalized/eliminated, survival override quiet. The posture is
    deliberately read independently of deck priority: §3.1 marks paymaster
    "posture, not a quest" — Britain's gold flowed WHILE the Low Countries
    design (its deck #1) stayed active, so the announced agenda and the
    subsidy posture coexist.

    Deckless worlds (legacy fixtures): the historical Britain literal with
    its 500-gold solvency gate — byte-identical legacy behavior (N1).
    """
    coalition = getattr(world, "active_coalition", None)
    if not coalition:
        return None
    members = list(coalition.get("members") or [])
    decks = getattr(world, "agendas", {}) or {}
    if not decks:
        # Legacy arm — the pre-NA-3 Britain literal, gates preserved.
        if "Britain" not in members:
            return None
        if int((getattr(world, "nation_gold", {}) or {}).get("Britain", 0)) <= 500:
            return None
        return "Britain"
    for member in members:
        if _is_vassal(world, member):
            continue
        if member not in world.get_active_nations():
            continue
        if survival_override_active(world, member):
            continue
        for entry in decks.get(member) or []:
            if entry.get("type") != "paymaster":
                continue
            floor = int(entry.get("treasury_floor") or 0)
            if _paymaster_active(world, member, floor):
                return member
    return None


def get_paymaster_subsidy_amount(world, payer: str) -> int:
    """NA-3 §5.7 — the treasury-escalated subsidy. Base 200/turn;
    AGENDA_SUBSIDY_TIER_2 above 4,000 treasury; AGENDA_SUBSIDY_TIER_3
    above 8,000; capped at AGENDA_SUBSIDY_CAP. Deckless worlds pay the
    historical flat 200 (legacy byte-compat rides the same base)."""
    treasury = int((getattr(world, "nation_gold", {}) or {}).get(payer, 0))
    if not (getattr(world, "agendas", {}) or {}):
        return 200
    if treasury > 8000:
        amount = AGENDA_SUBSIDY_TIER_3
    elif treasury > 4000:
        amount = AGENDA_SUBSIDY_TIER_2
    else:
        amount = 200
    return int(min(AGENDA_SUBSIDY_CAP, amount))


def get_agenda_grudge_nations(world, author: Optional[str] = None) -> List[str]:
    """NA-3 §5.8 — the post-peace grudge: nations at peace with the player
    whose active acquire/deny design remains denied by the player's bloc
    and whose war with the player ENDED within AGENDA_GRUDGE_TURNS.

    AI-5b generalises the query to `(victim, author)`: pass `author` to
    ask which courts grudge THAT nation instead of the player — emergent
    designs (revanche after a partition) make grudges point at non-player
    authors, and Stage E's tests read the generalised form. The default
    (author=None → the player) is byte-identical to the pre-Stage-E
    function, which is what the §5.8 threat contributor consumes.

    "Ended" is PER-NATION (adversarial-review fix): the durable side
    record on a war instance is `participant_meta[nation]["side"]` — the
    war-end path strips `side_by_nation` as participants exit, so a
    production-ended instance reaches this scan with side_by_nation
    empty. A separate-peace exiter's own war ends at its
    `exited_turn` while the instance fights on (the Pressburg court
    grudges from ITS peace, not the whole war's end); everyone else's
    ends at the instance `ended_turn`. side_by_nation stays a fallback
    for hand-authored instances.

    Fully derived: `war_instances` retains ended instances for exactly
    ARCHIVE_RETENTION_TURNS == AGENDA_GRUDGE_TURNS (10), and a
    separate-peace exit turn always precedes the instance end, so the
    live store covers every per-nation window — no archive scan, zero
    new fields. Returning the design's targets (they leave the player's
    bloc, or the court takes them) dissolves the grudge the same turn —
    the R156 payoff.
    """
    player = author or getattr(world, "player_nation", "France")
    current_turn = int(getattr(world, "current_turn", 0))
    instances = getattr(world, "war_instances", None) or {}

    recently_ended_with_player = set()
    for instance in instances.values():
        if not isinstance(instance, dict):
            continue
        meta = instance.get("participant_meta") or {}
        side_by_nation = instance.get("side_by_nation") or {}

        def _side_of(nation: str) -> Optional[str]:
            record = meta.get(nation)
            if isinstance(record, dict) and record.get("side"):
                return record.get("side")
            return side_by_nation.get(nation)

        player_side = _side_of(player)
        if not player_side:
            continue
        instance_end = instance.get("ended_turn")
        for nation in set(meta.keys()) | set(side_by_nation.keys()):
            if nation == player:
                continue
            side = _side_of(nation)
            if not side or side == player_side:
                continue
            record = meta.get(nation) or {}
            nation_end = record.get("exited_turn")
            if nation_end is None:
                nation_end = instance_end
            if nation_end is None:
                continue  # still fighting — the war IS the grievance
            if current_turn - int(nation_end) >= AGENDA_GRUDGE_TURNS:
                continue
            recently_ended_with_player.add(nation)

    grudged = []
    for nation in recently_ended_with_player:
        if nation not in world.get_active_nations():
            continue
        if _is_vassal(world, nation):
            continue
        if world.is_at_war(nation, player):
            continue  # back at war — the grudge is the war now
        view = get_active_agenda(nation, world)
        if view is None or view.survival:
            continue
        if view.type not in ("acquire_regions", "deny_regions"):
            continue
        if _agenda_concerns_bloc_of(nation, player, world):
            grudged.append(nation)
    return sorted(grudged)


def get_agenda_military_targets(nation: str, world) -> List[str]:
    """NA-3 §5.6 — the MILITARY half of the covets source: only an
    acquire-type design turns into the court's own conquest doctrine.
    §3.1 pins deny's expressions to resolve/acceptance/subsidy targeting —
    "never self-conquest" — so a deny court's listed regions never bias
    its corps (Britain does not storm Flanders to deny it; it pays,
    refuses, and fights longer instead). Diplomatic consumers keep the
    full get_agenda_covets (adversarial-review fix, §14)."""
    view = get_active_agenda(nation, world)
    if view is None or view.survival or view.type != "acquire_regions":
        return []
    return _unmet_targets(view, world)


def agenda_settlement_mod(court: str, settlement_terms, world,
                          proposer_side_participants=None) -> int:
    """NA-3 §7 rider (a) — the per-court agenda term for the multilateral
    settlement scorer, mirroring `agenda_acceptance_mod`'s ±ADVANCE/ENTRENCH
    semantics on the SETTLEMENT term vocabulary (`type` in territory kinds,
    `from`/`from_nation`, `to`/`to_nation`, `region`/`regions`).

    ADVANCE (+12): a term cedes an unmet design-target region TO the court
    (acquire), or moves a listed region OUT of the hegemon's bloc (deny).
    ENTRENCH (-8): a term strips a HELD design region FROM the court; or
    the package ends a war that was advancing the court's design (any
    opposing participant) without returning anything — the common peace
    that does not return Milan. First match wins; never additive.
    """
    view = get_active_agenda(court, world)
    if view is not None and view.survival:
        return 0
    # A WON design still defends itself — see agenda_acceptance_mod.
    won = _satisfied_views(world, court)
    if view is None and not won:
        return 0

    # NA-6c: a `create_client` carve moves SOIL, so it belongs in the
    # territory family here. Without it, a court whose design province is
    # carved away into a foreign client scored the package as a white
    # peace — more indifferent to losing Posen to a new Duchy of Warsaw
    # than to ceding it outright, which is exactly backwards.
    territory_kinds = ("territory", "territory_cede", "territory_return",
                       "create_client")

    def _regions_of(term) -> List[str]:
        regions = term.get("regions")
        if isinstance(regions, (list, tuple)) and regions:
            return [str(r) for r in regions]
        # A carve keys its soil as `provinces` (deliberately, so it does not
        # silently join every generic region-driven component).
        if term.get("type") == "create_client":
            provinces = term.get("provinces")
            if isinstance(provinces, (list, tuple)) and provinces:
                return [str(p) for p in provinces]
        region = str(term.get("region") or "")
        return [region] if region else []

    targets_lower = {r.lower(): r for r in (view.regions if view else ())}
    terms = [t for t in (settlement_terms or []) if isinstance(t, dict)]

    hegemon, share = _hegemon(world, court)
    bloc = (set(world.get_bloc_members(hegemon))
            if hegemon is not None and share >= HEGEMON_BLOC_SHARE_FLOOR
            else set())

    # ── ADVANCE ── (only the LIVE design — nothing left to advance on a won one)
    for term in terms if view is not None else ():
        if term.get("type") not in territory_kinds:
            continue
        to_nation = term.get("to_nation") or term.get("to")
        matched = [targets_lower[n.lower()] for n in _regions_of(term)
                   if n.lower() in targets_lower]
        if not matched:
            continue
        if view.type == "acquire_regions" and to_nation == court:
            for region_name in matched:
                if not _controlled_by_self_or_vassal(world, court, region_name):
                    return AGENDA_ACCEPT_ADVANCE
        elif view.type == "deny_regions" and bloc:
            from_nation = term.get("from_nation") or term.get("from")
            if (from_nation in bloc and to_nation
                    and to_nation not in bloc):
                for region_name in matched:
                    if _region_controller(world, region_name) in bloc:
                        return AGENDA_ACCEPT_ADVANCE

    # ── ENTRENCH: a term strips a HELD design region — live design OR won ──
    strip_lower = dict(targets_lower)
    for won_view in won:
        strip_lower.update({r.lower(): r for r in won_view.regions})
    for term in terms:
        if term.get("type") not in territory_kinds:
            continue
        from_nation = term.get("from_nation") or term.get("from")
        if from_nation != court:
            continue
        for name in _regions_of(term):
            region_name = strip_lower.get(name.lower())
            if (region_name is not None
                    and _controlled_by_self_or_vassal(world, court, region_name)):
                return AGENDA_ACCEPT_ENTRENCH

    if view is None:
        return 0

    # ── ENTRENCH: the peace ends an advancing war, returning nothing ──
    for opponent in (proposer_side_participants or []):
        if opponent == court:
            continue
        if _war_advances_agenda(view, opponent, world):
            return AGENDA_ACCEPT_ENTRENCH
    return 0


def process_agenda_violations(world) -> List[Dict]:
    """NA-3 §5.9 — the Ansbach trap. One pass over `world.marshals`
    (the EC-W1 get_disrupted_regions idiom — never a region scan): a
    belligerent nation's marshal standing in an ACTIVE guard_neutrality
    region triggers a one-time violation — relation penalty between
    violator and guard-holder plus a dispatch/campaign-log beat.

    Latch = bounded event-log lookback keyed (violator, guard-holder),
    refiring only after AGENDA_VIOLATION_COOLDOWN turns (the
    defensive-refusal-memory idiom; `log_event` auto-stamps `turn`).
    GR5: the player's columns crossing Jutland offend Copenhagen exactly
    as Bernadotte's crossing of Ansbach offended Berlin.
    """
    # Guard map: region -> holder, from ACTIVE guard agendas only (the
    # deck-priority chokepoint — a latent guard prices nothing).
    guard_holder_by_region: Dict[str, str] = {}
    for nation in world.get_active_nations():
        view = get_active_agenda(nation, world)
        if view is None or view.type != "guard_neutrality":
            continue
        for region_name in view.regions:
            guard_holder_by_region[region_name] = nation
    if not guard_holder_by_region:
        return []

    from backend.models.world_state import DISRUPTION_MIN_STRENGTH

    current_turn = int(getattr(world, "current_turn", 0))

    def _on_cooldown(violator: str, holder: str) -> bool:
        log = getattr(world, "event_log", []) or []
        # Rolling-cap guard (adversarial-review fix): if the capped log
        # has evicted events INSIDE the cooldown window, a prior latch
        # may be gone — fail SAFE and suppress rather than re-fire the
        # penalty (a missed violation is benign; a duplicate -25 is not).
        max_size = int(getattr(world, "MAX_EVENT_LOG_SIZE", 500) or 500)
        if len(log) >= max_size:
            oldest_turn = int((log[0] or {}).get("turn", 0) or 0)
            if oldest_turn > current_turn - AGENDA_VIOLATION_COOLDOWN:
                return True
        for event in log:
            if event.get("type") != "agenda_violation":
                continue
            if (event.get("violator") == violator
                    and event.get("guard_holder") == holder
                    and int(event.get("turn", 0) or 0)
                    > current_turn - AGENDA_VIOLATION_COOLDOWN):
                return True
        return False

    events: List[Dict] = []
    fired_pairs = set()
    vassals = getattr(world, "vassals", {}) or {}
    for marshal in world.marshals.values():
        holder = guard_holder_by_region.get(marshal.location)
        if holder is None:
            continue
        violator = marshal.nation
        if violator == holder:
            continue
        if getattr(marshal, "captured_by", ""):
            continue
        if marshal.strength < DISRUPTION_MIN_STRENGTH:
            continue  # a courier is not an army
        if not world.get_nations_at_war_with(violator):
            continue  # only a belligerent's columns offend
        if _controlled_by_self_or_vassal(world, violator, marshal.location):
            continue  # one's own soil cannot be "crossed" — a garrison on
            # a legally-held (e.g. treaty-ceded) province is no transit,
            # however loudly the old owner's guard covers it (review fix)
        if _belligerent(world, violator, holder):
            continue  # open war — or its armistice — supersedes outrage
        if world.are_allies(violator, holder):
            continue
        if ((vassals.get(violator) or {}).get("lord") == holder
                or (vassals.get(holder) or {}).get("lord") == violator):
            continue  # one's own lord or client is no foreign column
        pair = (violator, holder)
        if pair in fired_pairs or _on_cooldown(violator, holder):
            continue
        fired_pairs.add(pair)

        world.modify_nation_relation(
            violator, holder, AGENDA_VIOLATION_RELATION_PENALTY)
        from backend.game_logic.dispatch import queue_dispatch_event
        queue_dispatch_event(world, "agenda_violation", {
            "violator": _live_nation_name(world, violator),
            "guard_holder": _live_nation_name(world, holder),
            "region": marshal.location,
        }, fog_rule="always")
        world.log_event({
            "type": "agenda_violation",
            "violator": violator,
            "guard_holder": holder,
            "region": marshal.location,
            "penalty": AGENDA_VIOLATION_RELATION_PENALTY,
        })
        events.append({
            "type": "agenda_violation",
            "violator": violator,
            "guard_holder": holder,
            "region": marshal.location,
        })
    return events


# ═══════════════════════ LEGIBILITY (NA-1 single source) ══════════════════

def _unmet_targets(view: AgendaView, world) -> List[str]:
    return [
        r for r in view.regions
        if not _controlled_by_self_or_vassal(world, view.nation, r)
    ]


def _live_nation_name(world, nation: str) -> str:
    """Display name for backend-composed PROSE, formation-aware (NA-6).

    `display_nation` is static, so a formed nation would be baked into the
    sentence under its DEAD name — and because the result is already
    humanized ("Kingdom of Italy", no longer the raw tag), Godot's
    prose substitution cannot repair it downstream. Caught live on the
    ledger: "their court will not rest while Kingdom of Italy holds Milan"
    survived Italy's proclamation. §11.8 stage 3: no surface may show the
    dead name. Local import — formations reads this module.
    """
    try:
        from backend.game_logic.formations import formed_display_name
    except ImportError:      # pragma: no cover — cycle guard
        return display_nation(nation)
    return formed_display_name(world, nation)


def _stance_line(view: AgendaView, world) -> str:
    """One deterministic live-posture sentence per type (spec §5.1).
    All nation keys resolve through display_nation (R7)."""
    if view.survival:
        return "The dynasty above all."
    if view.type == "acquire_regions":
        unmet = _unmet_targets(view, world)
        if unmet:
            holder = _region_controller(world, unmet[0])
            if holder:
                holder_display = _live_nation_name(world, holder)
                # Degenerate holder==region case ("Hanover holds Hanover" —
                # live wart, July 17 2026 in-game review): an eponymous
                # minor holding its own land reads as coveting, not war.
                if holder_display == unmet[0]:
                    return (f"Their court will not rest while {unmet[0]} "
                            f"remains beyond their grasp.")
                return (f"Their court will not rest while "
                        f"{holder_display} holds {unmet[0]}.")
            return (f"Their court will not rest while {unmet[0]} "
                    f"lies in foreign hands.")
        return "Their court's design stands fulfilled."
    if view.type == "deny_regions":
        hegemon, _share = _hegemon(world, view.nation)
        bloc = set(world.get_bloc_members(hegemon)) if hegemon else set()
        held = [r for r in view.regions
                if _region_controller(world, r) in bloc]
        hegemon_display = (_live_nation_name(world, hegemon)
                           if hegemon else "the hegemon")
        if held:
            return (f"They will not suffer {hegemon_display}'s bloc "
                    f"in {held[0]}.")
        return f"They watch {hegemon_display}'s reach with suspicion."
    if view.type == "contain_hegemon":
        hegemon, share = _hegemon(world, view.nation)
        hegemon_display = (_live_nation_name(world, hegemon)
                           if hegemon else "the hegemon")
        return (f"They stand against {hegemon_display}'s dominion over "
                f"Europe ({int(share * 100)}% of its weight).")
    if view.type == "paymaster":
        return "Their gold flows to any who take the field against the hegemon."
    if view.type == "guard_neutrality":
        guards = list(view.regions)
        if guards:
            return (f"Armed and neutral — foreign columns near "
                    f"{guards[0]} would be an outrage.")
        return "Armed and neutral; the court watches the roads."
    return ""


def build_agenda_payload(nation: str, world) -> Optional[dict]:
    """{id, title, stance_line} for ledger / war-room surfaces, or None.
    Un-fogged by design — diplomacy has no fog (DPF-1)."""
    view = get_active_agenda(nation, world)
    if view is None:
        return None
    payload = {
        "id": view.id,
        "title": view.title,
        "stance_line": _stance_line(view, world),
    }
    # NA-6 §11.6-5 / §11.8 stage 0 — "the dream is visible". An ACTIVE
    # entry carrying a `forms` block advertises what it would become and
    # how close it stands, so no formation ever ambushes the player.
    # Local import: formations reads this module (one-way dependency).
    from backend.game_logic.formations import format_progress, get_forms_block
    forms = get_forms_block({"forms": view.params.get("forms")})
    if forms is not None:
        held = [r for r in view.regions
                if _controlled_by_self_or_vassal(world, nation, r)]
        payload["forms"] = {
            "display_name": forms["display_name"],
            "held": int(len(held)),
            "required": int(len(view.regions)),
            "progress": format_progress(len(held), len(view.regions)),
        }
    return payload


# ═══════════════════════ THE SHIFT BEAT (NA-1) ════════════════════════════

def process_agenda_shifts(world) -> List[Dict]:
    """Once-per-turn poll (called from _advance_turn_internal): compare each
    nation's active agenda against world.nation_agenda_seen; on change queue
    one dispatch line + campaign-log event, then update the seen map.

    First observation is recorded SILENTLY (the last_expectation_seen
    idiom — announce shifts, not bookkeeping; boot decks would otherwise
    spam turn 1). Deactivation (agenda -> None) updates the map silently.
    """
    seen = getattr(world, "nation_agenda_seen", None)
    if seen is None:
        world.nation_agenda_seen = {}
        seen = world.nation_agenda_seen

    events: List[Dict] = []
    for nation in world.get_active_nations():
        view = get_active_agenda(nation, world)
        current_id = view.id if view is not None else ""
        previous = seen.get(nation)
        if previous == current_id:
            continue
        first_observation = previous is None
        seen[nation] = current_id
        if first_observation or view is None:
            continue

        focus = view.title if not view.survival else "its own survival"
        nation_display = _live_nation_name(world, nation)
        from backend.game_logic.dispatch import queue_dispatch_event
        queue_dispatch_event(world, "agenda_shift", {
            "nation": nation_display,
            "focus": focus,
        }, fog_rule="always")
        world.log_event({
            "type": "agenda_shift",
            "nation": nation,
            "focus": focus,
            "agenda_id": current_id,
        })
        events.append({
            "type": "agenda_shift",
            "nation": nation,
            "agenda_id": current_id,
        })
    return events
