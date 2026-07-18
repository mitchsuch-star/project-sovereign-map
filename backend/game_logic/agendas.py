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


def _hegemon(world) -> Tuple[Optional[str], float]:
    """(leader, share) of the largest bloc — the shared hegemon-identity
    helper. Local import: coalition pulls in the wider diplomacy stack."""
    from backend.game_logic.coalition import _identify_max_bloc_share
    return _identify_max_bloc_share(world)


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
    hegemon, share = _hegemon(world)
    if hegemon is None or share < HEGEMON_BLOC_SHARE_FLOOR:
        return False
    bloc = set(world.get_bloc_members(hegemon))
    if nation in bloc:
        return False
    return any(_region_controller(world, r) in bloc for r in regions)


def _contain_active(world, nation: str, share_floor: float) -> bool:
    """Active while the hegemon bloc share >= floor AND self is outside
    that bloc."""
    hegemon, share = _hegemon(world)
    if hegemon is None or share < share_floor:
        return False
    return nation not in set(world.get_bloc_members(hegemon))


def _paymaster_active(world, nation: str, treasury_floor: int) -> bool:
    """Posture: at war with the hegemon OR member of an active coalition
    against the hegemon, AND treasury above the authored floor."""
    hegemon, _share = _hegemon(world)
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


def _guard_active(world, nation: str) -> bool:
    """Posture: active while self is at peace (no wars)."""
    return not world.get_nations_at_war_with(nation)


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
                    if _entry_active(world, nation, entry):
                        view = _view_from_entry(nation, entry)
                        break

    cache[nation] = view
    return view


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
        # "No target in hegemon bloc hands" — trivially true when no bloc
        # reaches the floor (the hegemon fell: the design achieved its aim).
        hegemon, share = _hegemon(world)
        if hegemon is None or share < HEGEMON_BLOC_SHARE_FLOOR:
            return True
        bloc = set(world.get_bloc_members(hegemon))
        return not any(_region_controller(world, r) in bloc
                       for r in (entry.get("regions") or []))
    if agenda_type == "contain_hegemon":
        # "share < floor" — regardless of where self sits.
        floor = float(entry.get("share_floor") or HEGEMON_BLOC_SHARE_FLOOR)
        hegemon, share = _hegemon(world)
        return hegemon is None or share < floor
    return False


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
        hegemon, share = _hegemon(world)
        if hegemon is None or share < HEGEMON_BLOC_SHARE_FLOOR:
            return False
        bloc = set(world.get_bloc_members(hegemon))
        if opponent not in bloc:
            return False
        return any(_region_controller(world, r) in bloc for r in view.regions)
    if view.type == "contain_hegemon":
        hegemon, share = _hegemon(world)
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
    view = get_active_agenda(nation, world)
    if view is None or view.survival:
        return False
    player = getattr(world, "player_nation", "France")
    if view.type == "acquire_regions":
        player_bloc = set(world.get_bloc_members(player))
        for region_name in view.regions:
            if _controlled_by_self_or_vassal(world, nation, region_name):
                continue
            if _region_controller(world, region_name) in player_bloc:
                return True
        return False
    if view.type == "deny_regions":
        hegemon, share = _hegemon(world)
        if hegemon is None or share < HEGEMON_BLOC_SHARE_FLOOR:
            return False
        bloc = set(world.get_bloc_members(hegemon))
        if player not in bloc:
            return False
        return any(_region_controller(world, r) in bloc for r in view.regions)
    if view.type == "contain_hegemon":
        hegemon, share = _hegemon(world)
        floor = float(view.params.get("share_floor") or HEGEMON_BLOC_SHARE_FLOOR)
        return hegemon == player and share >= floor
    return False


def agenda_satisfiable_by_player(nation: str, world) -> bool:
    """True when the nation's active agenda could be satisfied AT THE TABLE
    by the player — an acquire/deny design whose unmet targets sit in the
    player's bloc (cession would satisfy it). contain/paymaster/guard
    postures are never table-satisfiable. Feeds the war-room
    "satisfy their design" recommendation (spec §5.1)."""
    view = get_active_agenda(nation, world)
    if view is None or view.survival:
        return False
    if view.type not in ("acquire_regions", "deny_regions"):
        return False
    return agenda_concerns_player_bloc(nation, world)


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
    if view is None or view.survival:
        return 0

    ceded, demanded = _proposal_territory_content(proposal)
    targets_lower = {r.lower(): r for r in view.regions}

    def _match(names: set) -> List[str]:
        return [targets_lower[n.lower()] for n in names
                if n.lower() in targets_lower]

    ceded_targets = _match(ceded)
    demanded_targets = _match(demanded)

    # ── ADVANCE ──
    if view.type == "acquire_regions":
        for region_name in ceded_targets:
            if not _controlled_by_self_or_vassal(world, target, region_name):
                return AGENDA_ACCEPT_ADVANCE
    elif view.type == "deny_regions":
        hegemon, share = _hegemon(world)
        if hegemon is not None and share >= HEGEMON_BLOC_SHARE_FLOOR:
            bloc = set(world.get_bloc_members(hegemon))
            for region_name in ceded_targets:
                if _region_controller(world, region_name) in bloc:
                    return AGENDA_ACCEPT_ADVANCE

    # ── ENTRENCH ──
    for region_name in demanded_targets:
        if _controlled_by_self_or_vassal(world, target, region_name):
            return AGENDA_ACCEPT_ENTRENCH
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
        hegemon, share = _hegemon(world)
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


# ═══════════════════════ LEGIBILITY (NA-1 single source) ══════════════════

def _unmet_targets(view: AgendaView, world) -> List[str]:
    return [
        r for r in view.regions
        if not _controlled_by_self_or_vassal(world, view.nation, r)
    ]


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
                holder_display = display_nation(holder)
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
        hegemon, _share = _hegemon(world)
        bloc = set(world.get_bloc_members(hegemon)) if hegemon else set()
        held = [r for r in view.regions
                if _region_controller(world, r) in bloc]
        hegemon_display = display_nation(hegemon) if hegemon else "the hegemon"
        if held:
            return (f"They will not suffer {hegemon_display}'s bloc "
                    f"in {held[0]}.")
        return f"They watch {hegemon_display}'s reach with suspicion."
    if view.type == "contain_hegemon":
        hegemon, share = _hegemon(world)
        hegemon_display = display_nation(hegemon) if hegemon else "the hegemon"
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
    return {
        "id": view.id,
        "title": view.title,
        "stance_line": _stance_line(view, world),
    }


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
        nation_display = display_nation(nation)
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
