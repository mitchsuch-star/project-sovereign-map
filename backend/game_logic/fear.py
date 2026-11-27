"""Row FUN, Session FUN-2 — "conquest with a cost" (November 26, 2026).

The user's second play: "I beat Austria in the first war by eliminating them
and got to keep all the land, then a coalition of every country formed
later." The push-back was ONE France-wide number and any court below -10
relations joined a league — no distance, no stake, no warning at the click.
FUN-2 (`docs/GAMEPLAY_REVIEW_2026_11_25.md` §1.3, §5; `SYSTEMS_REFERENCE.md`
§240) gives every court its own FEAR OF FRANCE, the push-back EU4 calls
aggressive expansion, in this game's numbers:

* THE STORE — `world.court_grudges` `{court: int}` (the brief's name; the
  player reads "fear"), `world.fear_rules` (the scenario's top-level `fear`
  block — None = the rules are off) and `world.fear_book` (`causes`: the
  last captures each court minds; `faded`: the courts whose fear faded them
  out of a league). Armed by the 1805 campaign's own file, as the Awakening
  is: the bare flag world, the tutorials and the legacy rollback author no
  block and keep the old rules byte for byte.
* THE WRITE — each capture by France's house (France and its clients,
  `alarm.house_leader`) adds to every other court: PROVINCE x nearness x
  stake. Nearness 1 for the court that lost it or a court bordering that
  court, 1/2 with one court between (France's house is never the court
  between), 1/4 farther. Stake x2 for a court that lost it (the holder or
  the boot owner) or wants it (an acquire design), x3 for a capital. So
  8 / 4 / 2, 16 / 8 / 4 with a stake, 24 / 12 / 6 for a capital. Taking back
  the house's own soil frightens nobody. Written at the capture chokepoint
  (`WorldState.capture_region`) and its one mirror (the reckless charge).
* THE FADE — 2 a turn (`process_coalition_turn`).
* THE LEAGUE — `coalition.qualifies_for_coalition` for the player's leagues:
  fear past the line (50) AND a border with France's house or a stake in
  land it holds, never France's ally (vassals, truces, fresh peaces and the
  Congress are the predicate's own exclusions). A league needs three. While
  one stands, a court that crosses the line joins it at the turn's end; a
  member that joined by fear and falls under 25 leaves it and will take
  France's peace (`peace_readiness`, a term in `calculate_acceptance`).
* THE RISING — a province France itself holds by conquest, Hostile, with no
  garrison and no French corps, does not settle; after 4 such turns it rises
  back to its old court (an erased court rises again in it). Deterministic,
  never a roll; the province window counts it down.
* THE CARD — `capture_warning` is what the order card and the typed line
  say before a capture that erases a court or carries a court past the
  line, with the peace table one button away.

Seven seams, each zero-arg (`tests/_fun2_seams.py`): `fear_chooses_the_league`
(the store's writes, the fade, the join rule, the three), `a_declaration_
angers_the_targets_friends` (`diplomacy.declare_war`), `the_afraid_join_a_
standing_league`, `fear_fades_a_member_home`, `unheld_land_rises` (no settling
while unheld + the rising), `recruits_wait_for_settling` (the regen gate) and
`the_charge_takes_as_the_chokepoint_does` (the reckless charge's capture sets
stability and the garrison as the chokepoint does — FUN2-1). Down: the world
before FUN-2. Every seam reads `armed(world)` too.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

# ═══════════════════════════════════════════════════════════════════════
# The numbers
# ═══════════════════════════════════════════════════════════════════════

FEAR_PROVINCE = 8                 # a province's weight
NEARNESS = (1.0, 0.5, 0.25)       # borders the loser / one court between / farther
STAKE_FACTOR = 2                  # lost it, or wants it
CAPITAL_FACTOR = 3                # every court minds a capital
FEAR_CAP = 100

JOIN_DEFAULT = 50                 # a court joins a league PAST this
LEAVE_DEFAULT = 25                # a member that joined by fear leaves UNDER this
FADE_DEFAULT = 2                  # a turn
RISES_DEFAULT = 4                 # unheld Hostile turns before a province rises
LEAGUE_MIN_FEAR = 3               # members a league against France needs
LEAGUE_MIN_OLD = 2                # the old rule (unarmed worlds, other targets)

PEACE_READINESS = 25              # `calculate_acceptance`'s "fear faded" term
RISEN_GARRISON = 3000             # the risen province's own defenders
RISEN_STABILITY = 50              # it is home again, if not yet at peace
HOSTILE_MAX = 25                  # `Region.get_stability_label`: Hostile at 25 or below
SETTLING_MIN = 51                 # recruits flow from 51 (Settling)

CAUSES_KEPT = 3                   # the last captures each court minds, for "why"

_BOUNDS = {"join": (20, 90), "leave": (0, 80), "fade": (1, 10), "rises": (2, 12)}
_DEFAULTS = {"join": JOIN_DEFAULT, "leave": LEAVE_DEFAULT,
             "fade": FADE_DEFAULT, "rises": RISES_DEFAULT}


# ═══════════════════════════════════════════════════════════════════════
# The seams (one per rule — the series rig's arms)
# ═══════════════════════════════════════════════════════════════════════

def fear_chooses_the_league() -> bool:
    """FUN2-FEAR: the store's writes, the fade, the join rule (fear + a
    border or a stake, never an ally) and the league's three. Down: relations
    below -10 choose the league, two make one, nothing is written."""
    return True


def a_declaration_angers_the_targets_friends() -> bool:
    """FUN2-FRIENDS: a declaration's -15 (-7 with a reason) falls on the
    target's allies, its clients and its neighbours only. Down: every court."""
    return True


def the_afraid_join_a_standing_league() -> bool:
    """FUN2-STAND: a court that crosses the line while a league against
    France stands joins it at the turn's end. Down: a standing league enrols
    nobody new (EA-19's rider)."""
    return True


def fear_fades_a_member_home() -> bool:
    """FUN2-HOME: a member that joined by fear and falls under the leave line
    leaves the league and will take France's peace. Down: it stays."""
    return True


def unheld_land_rises() -> bool:
    """FUN2-RISE: France's unheld Hostile conquests do not settle, and rise
    after `rises` turns. Down: +5 a turn as before, nothing rises."""
    return True


def recruits_wait_for_settling() -> bool:
    """FUN2-RECRUIT: a province adds to the cavalry and artillery regen only
    once Settling (stability 51+). Down: from the day it is held."""
    return True


def the_charge_takes_as_the_chokepoint_does() -> bool:
    """FUN2-MIRROR (FUN2-1, the sibling sweep): the reckless charge's capture
    sets stability 25, clears the loser's garrison, adds the +2 capture alarm
    and France's fear, as `capture_region` does. Down: the mirror as it was
    (the province kept its old stability and garrison, no +2)."""
    return True


def land_at_the_table_frightens() -> bool:
    """FUN2B-FRIGHT (row FUN, Session FUN-2b, "peace terms priced"): land
    passing BY TREATY into France's house from outside adds to every court's
    fear as a capture does (`treaty_moves_land`, at the title chokepoint) —
    never for a province France's house already held. Down: a cession at the
    table frightens nobody."""
    return True


def land_handed_back_calms() -> bool:
    """FUN2B-CALM: a province France's house gives a court by treaty lowers
    THAT court's fear by what taking it added to it (the `taken` ledger every
    fear write keeps). Down: nothing calms, and no ledger is kept."""
    return True


# ═══════════════════════════════════════════════════════════════════════
# Arming — the scenario's block, the save's store
# ═══════════════════════════════════════════════════════════════════════

def _int_or(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)


def clean_block(raw: Any) -> Optional[Dict[str, int]]:
    """The `fear` block, clamped (`modding/validator.py` reports the same
    bounds). None when absent or not a mapping — the rules stay off."""
    if not isinstance(raw, dict):
        return None
    out: Dict[str, int] = {}
    for key, default in _DEFAULTS.items():
        lo, hi = _BOUNDS[key]
        out[key] = max(lo, min(hi, _int_or(raw.get(key, default), default)))
    if out["leave"] >= out["join"]:
        out["leave"] = max(0, out["join"] - 1)
    return out


def install(world, data: Dict[str, Any]) -> None:
    """`WorldState.from_dict`: a save carries `fear_rules` / `court_grudges`
    / `fear_book`; a scenario's top-level `fear` block arms a fresh campaign
    (every court at 0). A world that authors neither writes nothing."""
    data = data or {}
    rules = clean_block(data.get("fear_rules"))
    if rules is None:
        rules = clean_block(data.get("fear"))
    world.fear_rules = rules
    grudges: Dict[str, int] = {}
    for court, value in (data.get("court_grudges") or {}).items():
        v = _int_or(value, 0)
        if court and v > 0:
            grudges[str(court)] = max(0, min(FEAR_CAP, v))
    world.court_grudges = grudges
    world.fear_book = clean_book(data.get("fear_book"))


def clean_book(raw: Any) -> Dict[str, Any]:
    book: Dict[str, Any] = {"causes": {}, "faded": {}}
    if not isinstance(raw, dict):
        return book
    for court, rows in (raw.get("causes") or {}).items():
        kept = []
        for row in rows or []:
            if not isinstance(row, dict):
                continue
            kept.append({"region": str(row.get("region") or ""),
                         "amount": _int_or(row.get("amount"), 0),
                         "turn": _int_or(row.get("turn"), 0)})
        if kept:
            book["causes"][str(court)] = kept[-CAUSES_KEPT:]
    for court, turn in (raw.get("faded") or {}).items():
        book["faded"][str(court)] = _int_or(turn, 0)
    # FUN-2b: `taken` — {region: {court: amount}}, what each taking of a
    # province held by France's house added to each court's fear (the calm's
    # measure). Kept only when it holds something (an older save carries none).
    taken: Dict[str, Dict[str, int]] = {}
    for region, row in (raw.get("taken") or {}).items():
        if not region or not isinstance(row, dict):
            continue
        amounts = {str(c): _int_or(v, 0) for c, v in row.items() if c and _int_or(v, 0) > 0}
        if amounts:
            taken[str(region)] = amounts
    if taken:
        book["taken"] = taken
    return book


def backfill(world, scenario_data: Dict[str, Any]) -> bool:
    """A pre-FUN-2 save of a scenario that NOW authors the block gains the
    rules on load — every court at 0, nothing retroactive."""
    if armed(world):
        return False
    rules = clean_block((scenario_data or {}).get("fear"))
    if rules is None:
        return False
    world.fear_rules = rules
    if not isinstance(getattr(world, "court_grudges", None), dict):
        world.court_grudges = {}
    if not isinstance(getattr(world, "fear_book", None), dict):
        world.fear_book = clean_book(None)
    return True


def armed(world) -> bool:
    return bool(getattr(world, "fear_rules", None))


def rule(world, key: str) -> int:
    rules = getattr(world, "fear_rules", None) or {}
    return int(rules.get(key, _DEFAULTS[key]))


def chooses(world) -> bool:
    """The league is chosen by fear in this world (armed + FUN2-FEAR)."""
    return armed(world) and fear_chooses_the_league()


def league_min(world, target: Optional[str] = None) -> int:
    """Members a league needs: three against France in an armed world, two
    otherwise (and for every other target)."""
    player = _player(world)
    if (target or player) == player and chooses(world):
        return LEAGUE_MIN_FEAR
    return LEAGUE_MIN_OLD


# ═══════════════════════════════════════════════════════════════════════
# Houses, borders, stakes
# ═══════════════════════════════════════════════════════════════════════

def _player(world) -> str:
    return str(getattr(world, "player_nation", "") or "")


def house_of(world, nation: str) -> str:
    if not nation:
        return ""
    return str(world._top_overlord(nation) or nation)


def in_player_house(world, nation: str) -> bool:
    return bool(nation) and house_of(world, nation) == _player(world)


def house_members(world) -> List[str]:
    """France and every client whose top lord is France."""
    player = _player(world)
    members = [player] if player else []
    for client in (getattr(world, "vassals", {}) or {}):
        if client != player and house_of(world, client) == player:
            members.append(str(client))
    return members


def borders_house(world, court: str) -> bool:
    """`court` holds land next to France's or a client of France's
    (`get_neighbouring_nations` — cached per turn, sea links included)."""
    members = house_members(world)
    if not court or court in members:
        return False
    for member in members:
        if court in world.get_neighbouring_nations(member):
            return True
    return False


def _design_regions(world, court: str) -> List[str]:
    from backend.game_logic.agendas import acquire_design_regions
    out: List[str] = []
    for design in acquire_design_regions(world, court, authored=True):
        out.extend(str(r) for r in design)
    return out


def _holder(world, region_name: str) -> str:
    region = (getattr(world, "regions", {}) or {}).get(region_name)
    return str(getattr(region, "controller", "") or "") if region is not None else ""


def holds_stake(world, court: str) -> bool:
    """`court` lost homeland France's house now holds, or wants a province
    it holds (an acquire design, read as authored)."""
    if not court or in_player_house(world, court):
        return False
    from backend.game_logic.awakening import held_by_house
    if held_by_house(world, court, _player(world)) > 0:
        return True
    for name in _design_regions(world, court):
        if in_player_house(world, _holder(world, name)):
            return True
    return False


def border_or_stake(world, court: str) -> bool:
    return borders_house(world, court) or holds_stake(world, court)


def fear_of(world, court: str) -> int:
    return int((getattr(world, "court_grudges", None) or {}).get(str(court), 0) or 0)


def qualifies_by_fear(world, court: str) -> bool:
    """The fear half of the join rule: past the line, a border or a stake,
    never France's ally. The predicate's other exclusions stay its own."""
    if fear_of(world, court) <= rule(world, "join"):
        return False
    if world.are_allies(_player(world), court):
        return False
    return border_or_stake(world, court)


def why_out(world, court: str) -> str:
    """Why a court stays out of a league, in plain words ('' if it would join)."""
    fear = fear_of(world, court)
    line = rule(world, "join")
    if world.is_at_war(_player(world), court):
        coalition = _france_league(world)
        if coalition is not None and court in (coalition.get("members") or []):
            return "she already fights us in the coalition"
        return "she is already at war with us"
    if world.are_allies(_player(world), court):
        return "she is our ally"
    from backend.game_logic.coalition import peace_with_target_is_fresh
    from backend.game_logic.congress import spared_from_coalition
    from backend.game_logic.diplomacy import declaration_cooldown_left
    player = _player(world)
    if declaration_cooldown_left(world, court, player) > 0:
        return "a truce with us binds her for now"
    if peace_with_target_is_fresh(court, world, player):
        return "her fresh peace with us binds her for now"
    if spared_from_coalition(world, court, player):
        return "she answers the Congress while it sits"
    if court in (getattr(world, "vassals", {}) or {}):
        return "she is another court's vassal"
    if not border_or_stake(world, court):
        return "she neither borders us nor lost or wants land we hold"
    if fear <= line:
        return f"{line + 1 - fear} more fear would bring her in"
    return ""


# ═══════════════════════════════════════════════════════════════════════
# The write — a capture
# ═══════════════════════════════════════════════════════════════════════

def loser_neighbours(world, loser: str) -> List[str]:
    """The courts next to the court that loses a province: those holding
    land beside its HOMELAND (its boot lands, whoever holds them now) and
    those bordering what it holds today. The homeland keeps the reading
    steady while the court shrinks — Russia borders Austria's lands though
    France's conquests now stand between it and Vienna."""
    if not loser:
        return []
    out = set(world.get_neighbouring_nations(loser))
    regions = getattr(world, "regions", {}) or {}
    homeland = ((getattr(world, "nation_starting_regions", {}) or {}).get(loser) or [])
    home = set(str(r) for r in homeland)
    for name in home:
        region = regions.get(name)
        if region is None:
            continue
        holder = str(getattr(region, "controller", "") or "")
        if holder and holder != loser:
            out.add(holder)
        for adjacent in getattr(region, "adjacent_regions", None) or []:
            if adjacent in home:
                continue
            other = _holder(world, adjacent)
            if other and other != loser:
                out.add(other)
    return sorted(out)


def nearness(world, court: str, loser: str,
             _near: Optional[List[str]] = None) -> float:
    """1 for the loser and the courts next to it (`loser_neighbours`; for land
    held by nobody, `_near` names the province's own neighbours), 1/2 with one
    court between (never France's house), 1/4 farther."""
    if loser and court == loser:
        return NEARNESS[0]
    near = _near if _near is not None else loser_neighbours(world, loser)
    if court in near:
        return NEARNESS[0]
    house = set(house_members(world))
    for middle in near:
        if middle in house or middle == court:
            continue
        if court in world.get_neighbouring_nations(middle):
            return NEARNESS[1]
    return NEARNESS[2]


def _boot_owner(world, region_name: str) -> str:
    from backend.game_logic.game_end import home_nation_of
    return str(home_nation_of(world, region_name) or "")


def capture_deltas(world, region_name: str, loser: str, capturer: str) -> Dict[str, int]:
    """What taking `region_name` from `loser` adds to each court's fear —
    pure; read BEFORE the controller moves (the borders and the agendas as
    they stand). {} when the capture frightens nobody: the rules off, a
    capturer outside France's house, the house's own soil taken back, or
    land passing inside the house."""
    if not chooses(world) or not capturer or not in_player_house(world, capturer):
        return {}
    region = (getattr(world, "regions", {}) or {}).get(region_name)
    if region is None:
        return {}
    boot = _boot_owner(world, region_name)
    if boot and in_player_house(world, boot):
        return {}
    if loser and in_player_house(world, loser):
        return {}
    capital = bool(getattr(region, "is_capital", False))
    if loser:
        near = loser_neighbours(world, loser)
        if _holder(world, region_name) != loser:
            # FUN-2b (the review, lane 1): a treaty road calls this AFTER the
            # province changed hands — the courts beside it bordered the loser
            # THROUGH it, as a capture (read before the move) counts them. A
            # no-op on the capture road, where the loser still holds it.
            extra = {_holder(world, a) for a in (getattr(region, "adjacent_regions", None) or [])}
            near = sorted(set(near) | {c for c in extra if c and c != loser})
    else:
        # land held by nobody: the courts next to the province itself are near
        near = sorted({_holder(world, a) for a in (getattr(region, "adjacent_regions", None) or [])
                       if _holder(world, a)})
    deltas: Dict[str, int] = {}
    vassals = getattr(world, "vassals", {}) or {}
    for court in world.get_active_nations():
        # (12) another court's client keeps no fear of its own (it cannot join a
        # coalition; its lord's fear is the one that counts)
        if not court or in_player_house(world, court) or court in vassals:
            continue
        factor = 1
        if court in (loser, boot) or region_name in _design_regions(world, court):
            factor *= STAKE_FACTOR
        if capital:
            factor *= CAPITAL_FACTOR
        amount = int(round(FEAR_PROVINCE * nearness(world, court, loser, _near=near) * factor))
        if amount > 0:
            deltas[str(court)] = amount
    return deltas


def apply_deltas(world, deltas: Dict[str, int], region_name: str) -> None:
    if not deltas:
        return
    store = getattr(world, "court_grudges", None)
    if not isinstance(store, dict):
        store = {}
        world.court_grudges = store
    book = getattr(world, "fear_book", None)
    if not isinstance(book, dict):
        book = clean_book(None)
        world.fear_book = book
    turn = int(getattr(world, "current_turn", 0) or 0)
    causes = book.setdefault("causes", {})
    book.setdefault("faded", {})
    if land_handed_back_calms():
        # FUN-2b: what this taking added, court by court — the calm's measure
        # when France's house gives the province back (a re-taking replaces it).
        book.setdefault("taken", {})[str(region_name)] = {
            str(c): int(a) for c, a in deltas.items() if int(a) > 0}
    for court, amount in deltas.items():
        store[court] = int(min(FEAR_CAP, int(store.get(court, 0) or 0) + int(amount)))
        if int(amount) < FEAR_PROVINCE:
            continue      # "alarmed by" names only what frightened it as a neighbour would be
        rows = causes.setdefault(court, [])
        rows.append({"region": str(region_name), "amount": int(amount), "turn": turn})
        del rows[:-CAUSES_KEPT]


def mirror_capture(world, region_name: str, charge_from: str, capturer: str,
                   liberated_to: str, prior_title: Dict[str, Any],
                   deltas: Dict[str, int]) -> None:
    """FUN2-1 (the sibling sweep): the reckless charge's capture — the one
    conquest outside `WorldState.capture_region` — takes the province as the
    chokepoint does: Hostile (stability 25), the count afresh, the loser's
    garrison gone, the +2 capture alarm and France's fear under the
    chokepoint's own three skips. `deltas` is `capture_deltas`, read BEFORE the
    controller moved. Armed world, seam up; else nothing."""
    if not (armed(world) and the_charge_takes_as_the_chokepoint_does()):
        return
    region = world.get_region(region_name)
    if region is None:
        return
    region.stability = HOSTILE_MAX
    region.unheld_turns = 0
    holder = liberated_to or capturer
    if charge_from and charge_from != holder:
        region.garrison_strength = 0
        region.garrison_detachment = False
    from backend.models.region import get_starting_controllers
    from backend.models.world_state import capture_recovers_title
    starting = getattr(world, "_starting_controllers", None) or get_starting_controllers()
    if (starting.get(region_name) != capturer
            and not capture_recovers_title(prior_title or {}, capturer)
            and not liberated_to):
        from backend.game_logic.coalition import add_threat
        add_threat(world, 2, "region_capture", target=capturer)
        apply_deltas(world, deltas, region_name)


# ═══════════════════════════════════════════════════════════════════════
# FUN-2b — land at the table frightens; land handed back calms
# ═══════════════════════════════════════════════════════════════════════

def _held_by_house(world, prior: Optional[Dict[str, Any]]) -> bool:
    """The province's title BEFORE this treaty says France's house held it —
    an occupation the peace confirms, a status-quo retention, a signed
    cession of held ground: its fear was paid when it was taken."""
    if not isinstance(prior, dict) or not prior:
        return False
    return (in_player_house(world, str(prior.get("holder") or ""))
            or in_player_house(world, str(prior.get("house") or "")))


def _paid_before(world, prior: Optional[Dict[str, Any]]) -> bool:
    """Its fear was paid already: France's house held it (`_held_by_house`), or
    it was taken FROM France's house and now comes back — the capture road's
    own "recovered" rule (`world_state.capture_recovers_title`, DDB-42), which
    frightens nobody by arms either (the review, lane 1)."""
    if _held_by_house(world, prior):
        return True
    return (isinstance(prior, dict) and str(prior.get("kind") or "") == "conquest"
            and in_player_house(world, str(prior.get("from") or "")))


def calm(world, region_name: str, court: str) -> int:
    """`court` receives `region_name` from France's house: its fear falls by
    what taking that province added to it (the ledger), floored at 0. The
    province's ledger row goes either way (it has left the house). Returns
    the calm."""
    book = getattr(world, "fear_book", None)
    taken = (book or {}).get("taken") if isinstance(book, dict) else None
    if not isinstance(taken, dict):
        return 0
    row = taken.pop(str(region_name), None)
    if not taken:
        book.pop("taken", None)
    amount = int((row or {}).get(str(court), 0) or 0)
    if amount <= 0:
        return 0
    store = getattr(world, "court_grudges", None)
    if not isinstance(store, dict):
        return 0
    before = int(store.get(str(court), 0) or 0)
    left = before - amount
    if left > 0:
        store[str(court)] = left
    else:
        store.pop(str(court), None)
    return min(before, amount)


def treaty_moves_land(world, region_name: str, giver: str, receiver: str,
                      prior: Optional[Dict[str, Any]] = None, house: str = "") -> int:
    """FUN-2b's ONE writer at the treaty roads — `game_end.record_province_title`
    (kind treaty: every cession, return, retention, hand-back and ultimatum
    goes through it), the carve's own title writer and the sureties' return.
    `prior` is the province's title before this treaty; `house` the court the
    land is signed to when the receiver is not yet of it (a carve's client).

    Into France's house from outside: the courts' fear as a capture (the
    giver is the loser) — never for a province France's house already held.
    Out of France's house to an outside court: that court calms. Returns the
    amount written (+) or calmed (-); 0 outside an armed world."""
    if not chooses(world) or not region_name:
        return 0
    giver = str(giver or "")
    receiver = str(receiver or "")
    signed_to = receiver if in_player_house(world, receiver) else str(house or "")
    into = bool(signed_to) and in_player_house(world, signed_to)
    out_of = bool(giver) and in_player_house(world, giver)
    if into and not out_of:
        if not land_at_the_table_frightens() or _paid_before(world, prior):
            return 0
        deltas = capture_deltas(world, region_name, giver, signed_to)
        apply_deltas(world, deltas, region_name)
        return int(sum(deltas.values()))
    if out_of and not into and receiver:
        # only land France's house HELD is handed back — a peace that leaves an
        # enemy the ground it occupies (a retention) calms nobody (the review)
        if not land_handed_back_calms() or not _held_by_house(world, prior):
            return 0
        return -calm(world, region_name, receiver)
    return 0


_LAND_INTO = ("territory_cede", "territory", "territory_compensate")


def table_moves(world, terms: List[Dict[str, Any]]) -> Dict[str, List[Tuple[str, str, str]]]:
    """The land a package moves across France's house's border, as
    (region, giver, receiver) — `into` (frightens), `out` (calms). Land
    France's house already holds is not `into` (never twice)."""
    into: List[Tuple[str, str, str]] = []
    out: List[Tuple[str, str, str]] = []
    regions = getattr(world, "regions", {}) or {}
    for term in terms or []:
        if not isinstance(term, dict):
            continue
        ttype = str(term.get("type") or "")
        giver = str(term.get("from") or term.get("from_nation") or "")
        receiver = str(term.get("to") or term.get("to_nation") or "")
        if ttype in _LAND_INTO:
            names = [str(r) for r in (term.get("regions") or []) if r] + (
                [str(term.get("region"))] if term.get("region") else [])
        elif ttype == "create_client":
            names = [str(p) for p in (term.get("provinces") or []) if p]
        else:
            continue
        titles = getattr(world, "province_title", None) or {}
        for name in dict.fromkeys(names):
            region = regions.get(name)
            if region is None:
                continue
            holder = str(getattr(region, "controller", "") or "")
            if in_player_house(world, receiver) and not in_player_house(world, giver):
                # never twice: land the house holds, or land taken FROM the
                # house coming back (the writer's own `_paid_before`)
                if not in_player_house(world, holder) and not _paid_before(
                        world, dict(titles.get(name) or {})):
                    into.append((name, giver, receiver))
            elif (in_player_house(world, giver) and not in_player_house(world, receiver)
                  and in_player_house(world, holder)):
                # only land the house HOLDS is handed back (the writer's rule)
                out.append((name, giver, receiver))
    return {"into": into, "out": out}


def table_forecast(world, terms: List[Dict[str, Any]]) -> Dict[str, Any]:
    """What signing `terms` would do to Europe's fear of France, read before
    the click: {adds: {court: n}, calms: {court: n}, crossing, joiners, when,
    regions_into, regions_out}. Pure."""
    empty = {"adds": {}, "calms": {}, "crossing": [], "joiners": [], "when": "",
             "regions_into": [], "regions_out": []}
    if not chooses(world):
        return empty
    moves = table_moves(world, terms)
    adds: Dict[str, int] = {}
    if land_at_the_table_frightens():
        for name, giver, receiver in moves["into"]:
            for court, amount in capture_deltas(world, name, giver, receiver).items():
                adds[court] = adds.get(court, 0) + int(amount)
    calms: Dict[str, int] = {}
    calmed_by: Dict[str, List[str]] = {}
    if land_handed_back_calms():
        taken = ((getattr(world, "fear_book", None) or {}).get("taken") or {})
        for name, _giver, receiver in moves["out"]:
            amount = int((taken.get(name) or {}).get(receiver, 0) or 0)
            if amount > 0:
                calms[receiver] = calms.get(receiver, 0) + amount
                calmed_by.setdefault(receiver, []).append(name)
    line = rule(world, "join")
    crossing: List[str] = []
    joiners: List[str] = []
    from backend.game_logic.coalition import qualifies_for_coalition
    coalition = _france_league(world)
    members = set((coalition or {}).get("members") or [])
    for court in sorted(adds):
        before = fear_of(world, court)
        after = max(0, min(FEAR_CAP, before + adds[court] - calms.get(court, 0)))
        if before <= line < after:
            crossing.append(court)
        if court in members or qualifies_for_coalition(court, world):
            continue
        if any(_would_join(world, court, after, name) for name, _g, _r in moves["into"]):
            joiners.append(court)
    when = ""
    if joiners:
        from backend.game_logic.coalition import (
            THREAT_INSTANT_MIN, TREATY_ANNEX_ALARM_PER_PROVINCE, brewing_gate,
            get_nations_at_war_with_target)
        player = _player(world)
        at_war = [c for c in get_nations_at_war_with_target(world, player)
                  if border_or_stake(world, c)]
        size = len(set(joiners) | set(at_war))
        threat_after = (int(getattr(world, "threat_level", 0) or 0)
                        + int(TREATY_ANNEX_ALARM_PER_PROVINCE) * len(moves["into"]))
        if coalition is not None:
            when = "at the end of this turn"
        elif size < league_min(world):
            when = (f"but a coalition needs {league_min(world)} countries and only {size} "
                    f"would stand against us, so not yet")
        elif threat_after >= THREAT_INSTANT_MIN:
            when = "at the end of this turn"
        elif threat_after >= int(brewing_gate(world, player)):
            when = "in about 3 turns"
        else:
            when = (f"once France's alarm reaches {int(brewing_gate(world, player))} "
                    f"(it would be {min(100, threat_after)})")
    return {"adds": adds, "calms": calms, "calmed_by": calmed_by,
            "crossing": crossing, "joiners": joiners,
            "when": when, "regions_into": [m[0] for m in moves["into"]],
            "regions_out": [m[0] for m in moves["out"]]}


TABLE_NAMES_SHOWN = 3


def table_line(world, terms: List[Dict[str, Any]]) -> str:
    """The peace's fear in plain words, one paragraph, '' when it moves no
    fear: "This peace would add to Europe's fear of France: Bavaria +16,
    Saxony +8 and Russia +8. Bavaria would then fear France past 50 — enough
    to join a coalition against us in about 3 turns." / "Handing back Tyrol
    would calm Austria (-16)." """
    forecast = table_forecast(world, terms)
    adds = {c: a for c, a in forecast["adds"].items() if a > 0}
    parts: List[str] = []
    if adds:
        # the countries this peace carries past the line are always named,
        # first; then the most frightened, to three names in all
        crossing = set(forecast["crossing"]) | set(forecast["joiners"])
        ranked = sorted(adds.items(), key=lambda kv: (kv[0] not in crossing, -kv[1],
                                                      court_name(world, kv[0])))
        count = max(TABLE_NAMES_SHOWN, len([c for c, _a in ranked if c in crossing]))
        shown = [f"{court_name(world, c, start=True)} +{a}" for c, a in ranked[:count]]
        more = len(ranked) - count
        if more > 0:
            shown.append(f"{more} more {'country' if more == 1 else 'countries'}")
        parts.append(f"This peace would add to Europe's fear of France: {_join_names(shown)}.")
        line = rule(world, "join")
        joiners = forecast["joiners"]
        coalition = _france_league(world)
        # the blind readings (November 27): a bare "past 50" beside the table's
        # signing line of 50 read as the same scale — the fear says its own
        # figure and names its own line
        def _after(court: str) -> int:
            return max(0, min(FEAR_CAP, fear_of(world, court) + int(adds.get(court, 0))
                              - int(forecast["calms"].get(court, 0))))
        if joiners:
            target = (f"{league_name(coalition)} against us" if coalition is not None
                      else "a coalition against us")
            # the review (lane 2): "she would join … but a coalition needs 3 … so
            # not yet" said she would join and then that nothing forms — the
            # too-few case says she would be READY to join
            when = str(forecast["when"] or "")
            not_yet = when.startswith("but ")
            if len(joiners) == 1:
                court = joiners[0]
                act = (f"she would be ready to join {target} — {when}" if not_yet
                       else f"she would join {target} {when}")
                parts.append(f"With it {_possessive(court_name(world, court))} fear of France "
                             f"would reach {_after(court)} — past the {line} at which a country "
                             f"joins a coalition: {act}.")
            else:
                names = _join_names([court_name(world, c) for c in joiners])
                act = (f"they would be ready to join {target} — {when}" if not_yet
                       else f"they would join {target} {when}")
                parts.append(f"With it {names} would each fear France past {line}, the line at "
                             f"which a country joins a coalition: {act}.")
        quiet = [c for c in forecast["crossing"] if c not in joiners
                 and not world.is_at_war(_player(world), c)]
        for court in quiet:
            why = why_out(world, court) or "she is already at war with us"
            parts.append(f"{_cap(_possessive(court_name(world, court)))} fear of France would "
                         f"reach {_after(court)}, past {line}, but she would stay out: {why}.")
    calms = forecast["calms"]
    for court, amount in sorted(calms.items()):
        given = forecast["calmed_by"].get(court) or []
        parts.append(f"Handing back {_join_names(given)} would calm "
                     f"{court_name(world, court)}: her fear of France falls {int(amount)}.")
    return " ".join(parts)


def fade(world) -> None:
    """2 a turn, every court; a court at 0 leaves the store."""
    if not chooses(world):
        return
    step = rule(world, "fade")
    store = getattr(world, "court_grudges", None) or {}
    for court in list(store):
        left = int(store.get(court, 0) or 0) - step
        if left > 0:
            store[court] = left
        else:
            store.pop(court, None)
    world.court_grudges = store
    # FUN-2b: the calm's ledger keeps only provinces France's house still
    # holds, and what each taking added fades as the fear does (the review,
    # lane 1: an old conquest handed back must not wipe fear a NEWER taking
    # added). One pass over the ledger itself — at most France's conquests,
    # never a scan of the map.
    book = getattr(world, "fear_book", None)
    taken = (book or {}).get("taken") if isinstance(book, dict) else None
    if isinstance(taken, dict) and taken:
        regions = getattr(world, "regions", {}) or {}
        for name in list(taken):
            region = regions.get(name)
            holder = str(getattr(region, "controller", "") or "") if region is not None else ""
            if not in_player_house(world, holder):
                taken.pop(name, None)
                continue
            row = taken[name]
            for court in list(row):
                left = int(row.get(court, 0) or 0) - step
                if left > 0:
                    row[court] = left
                else:
                    row.pop(court, None)
            if not row:
                taken.pop(name, None)
        if not taken:
            book.pop("taken", None)


# ═══════════════════════════════════════════════════════════════════════
# The league — standing joins, the faded home, the peace term
# ═══════════════════════════════════════════════════════════════════════

def _france_league(world) -> Optional[Dict[str, Any]]:
    coalition = getattr(world, "active_coalition", None)
    if not coalition:
        return None
    if (coalition.get("target_nation") or _player(world)) != _player(world):
        return None
    return coalition


def standing_joins(world) -> List[Dict[str, Any]]:
    """FUN2-STAND: every court that qualifies (the whole predicate) while a
    league against France stands joins it — `join_coalition`, its own
    declaration. Names, never a figure the player cannot check."""
    events: List[Dict[str, Any]] = []
    if not (chooses(world) and the_afraid_join_a_standing_league()):
        return events
    coalition = _france_league(world)
    if coalition is None:
        return events
    from backend.game_logic.coalition import join_coalition, qualifies_for_coalition
    for court in sorted(world.get_active_nations()):
        members = list(coalition.get("members") or [])
        if court in members or court == _player(world):
            continue
        if not qualifies_for_coalition(court, world):
            continue
        afraid = qualifies_by_fear(world, court)    # read BEFORE the declaration moves anything
        result = join_coalition(world, court)
        if not result.get("success"):
            continue
        clear_faded(world, court)
        if afraid:
            by_fear = coalition.setdefault("by_fear", [])
            if court not in by_fear:
                by_fear.append(court)
        message = (f"{court_name(world, court, start=True)} joins {league_name(coalition)} "
                   f"against us — its fear of France passed {rule(world, 'join')} "
                   f"({fear_of(world, court)}).")
        events.append({"type": "coalition_member_joined", "nation": _player(world),
                       "court": court, "message": message})
        world.log_event({"type": "coalition_member_joined", "nation": court,
                         "target_nation": _player(world),
                         "coalition": coalition.get("name", ""),
                         "fear": fear_of(world, court), "by": "fear"})
    return events


def faded_home(world) -> List[Dict[str, Any]]:
    """FUN2-HOME: a member that joined by fear and falls under the leave
    line leaves the league (`remove_coalition_member`) and is booked ready
    for France's peace. France's own war with it is never ended without
    France's word — the player's pairs are untouchable."""
    events: List[Dict[str, Any]] = []
    if not (chooses(world) and fear_fades_a_member_home()):
        return events
    coalition = _france_league(world)
    if coalition is None:
        return events
    from backend.game_logic.coalition import remove_coalition_member
    book = getattr(world, "fear_book", None)
    if not isinstance(book, dict):
        book = clean_book(None)
        world.fear_book = book
    faded_store = book.setdefault("faded", {})
    line = rule(world, "leave")
    for court in list(coalition.get("by_fear") or []):
        if court not in (coalition.get("members") or []):
            coalition["by_fear"].remove(court)
            continue
        if fear_of(world, court) >= line:
            continue
        coalition["by_fear"].remove(court)
        faded_store[court] = int(getattr(world, "current_turn", 0) or 0)
        message = (f"{court_name(world, court, start=True)} leaves {league_name(coalition)} "
                   f"— its fear of France fell under {line} ({fear_of(world, court)}). "
                   f"It would take our peace now.")
        events.append({"type": "coalition_member_left", "nation": _player(world),
                       "court": court, "message": message})
        # the league's own events ride along (a dissolution), but not its plain
        # "has left the coalition" line — the line above says it, and why
        events.extend(ev for ev in remove_coalition_member(court, world, reason="fear_faded")
                      if not (ev.get("type") == "coalition_member_left" and ev.get("nation") == court))
        coalition = _france_league(world)
        if coalition is None:
            break
    return events


def peace_readiness(world, proposer: str, target: str) -> int:
    """`calculate_acceptance`'s term: a court whose fear faded it out of a
    league, still at war with France, takes France's peace readily (+25).
    0 everywhere else."""
    if not (chooses(world) and fear_fades_a_member_home()):
        return 0
    if proposer != _player(world) or not target:
        return 0
    book = getattr(world, "fear_book", None) or {}
    if target not in (book.get("faded") or {}):
        return 0
    if not world.is_at_war(proposer, target):
        return 0
    coalition = _france_league(world)
    if coalition is not None and target in (coalition.get("members") or []):
        return 0
    return PEACE_READINESS


def clear_faded(world, court: str) -> None:
    """The book's mark goes when the court's war with France ends."""
    book = getattr(world, "fear_book", None)
    if isinstance(book, dict):
        (book.get("faded") or {}).pop(str(court), None)


# ═══════════════════════════════════════════════════════════════════════
# The card — "Erase this country?"
# ═══════════════════════════════════════════════════════════════════════

def _join_names(names: List[str]) -> str:
    names = [n for n in names if n]
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + " and " + names[-1]


def court_name(world, court: str, start: bool = False) -> str:
    """A court as a sentence names it — "the Ottoman Empire", "Saxony"
    (`display_names.with_definite_article` over the formed name)."""
    from backend.display_names import with_definite_article
    from backend.game_logic.formations import formed_display_name
    name = with_definite_article(formed_display_name(world, court))
    return name[:1].upper() + name[1:] if start and name else name


def league_name(coalition: Optional[Dict[str, Any]]) -> str:
    """"the Third Coalition" / "the Prussian Coalition" — a league's name as
    the middle of a sentence says it."""
    name = str((coalition or {}).get("name") or "").strip()
    if not name:
        return "the league"
    if name.lower().startswith("the "):
        return "the " + name[4:]
    return "the " + name


def _would_join(world, court: str, fear_after: int, region_name: str) -> bool:
    """Would `court` qualify once the capture lands? The predicate's own
    exclusions as they stand (`coalition.league_excluded`), its fear after
    the capture, and the border or stake the capture itself opens (the
    province's neighbours; its boot owner; a court that wants it)."""
    from backend.game_logic.coalition import league_excluded
    if fear_after <= rule(world, "join"):
        return False
    if world.are_allies(_player(world), court):
        return False
    if league_excluded(court, world):
        return False
    if border_or_stake(world, court):
        return True
    if court == _boot_owner(world, region_name) or region_name in _design_regions(world, court):
        return True
    region = (getattr(world, "regions", {}) or {}).get(region_name)
    for adjacent in (getattr(region, "adjacent_regions", None) or []) if region is not None else []:
        if _holder(world, adjacent) == court:
            return True
    return False


def capture_warning(world, region_name: str, capturer: str,
                    attack: bool = False) -> Optional[Dict[str, Any]]:
    """The order card's and the typed line's warning before a capture that
    erases a court or carries a court's fear past the line. None when the
    capture says nothing new (or the rules are off). `attack`: the order is
    a battle, so the capture is its outcome ("If this attack takes …").

    {court, court_shown, last, joiners, joiners_shown, crossing, when,
     line, short, peace_label}"""
    if not chooses(world) or not region_name or not capturer:
        return None
    if not in_player_house(world, capturer):
        return None
    holder = _holder(world, region_name)
    if not holder or in_player_house(world, holder):
        return None
    if not world.is_at_war(house_of(world, capturer), holder) and not world.is_at_war(capturer, holder):
        return None
    from backend.game_logic.coalition import qualifies_for_coalition
    from backend.game_logic.formations import formed_display_name
    deltas = capture_deltas(world, region_name, holder, capturer)
    last = (holder != _player(world)
            and holder not in (getattr(world, "vassals", {}) or {})
            and list(world.get_nation_regions(holder)) == [region_name])
    line_fear = rule(world, "join")
    crossing: List[str] = []
    joiners: List[str] = []
    coalition = _france_league(world)
    members = set((coalition or {}).get("members") or [])
    for court, amount in sorted(deltas.items()):
        if court == holder:
            continue          # the court we fight is no news to its own war
        before = fear_of(world, court)
        after = min(FEAR_CAP, before + int(amount))
        if before <= line_fear < after:
            crossing.append(court)
        if court in members or qualifies_for_coalition(court, world):
            continue          # already in, or already ready to march
        if _would_join(world, court, after, region_name):
            joiners.append(court)
    if not last and not crossing and not joiners:
        return None
    shown = formed_display_name(world, holder)
    joiners_shown = [court_name(world, c) for c in joiners]
    # A court already fighting us is no news to the card (its war is the news).
    quiet_courts = [c for c in crossing if c not in joiners
                    and not world.is_at_war(_player(world), c)]
    when = league_when(world, region_name, joiners)
    lead = (f"If {region_name} falls, it" if attack
            else f"Taking {region_name}")
    if last:
        head = f"{lead} erases {court_name(world, holder)}."
    elif joiners_shown:
        head = (f"{lead} would make {_join_names(joiners_shown)} fear France "
                f"past {line_fear}")
    else:
        names = _join_names([court_name(world, c) for c in quiet_courts])
        head = f"{lead} would make {names} fear France past {line_fear}."
    if joiners_shown and not last:
        # the crossing itself is the head: say what it leads to in the same sentence
        tail = ((f", enough to join {league_name(coalition)} against us at the end of this turn.")
                if coalition is not None else
                (f", enough to join a coalition against us — {when}."))
    elif joiners_shown and coalition is not None:
        tail = (f" {_cap(_join_names(joiners_shown))} would then fear France enough to "
                f"join {league_name(coalition)} against us at the end of this turn.")
    elif joiners_shown:
        tail = (f" {_cap(_join_names(joiners_shown))} would then fear France enough to "
                f"join a coalition against us — {when}.")
    elif last and not quiet_courts:
        tail = " No country would fear France enough to join a coalition yet."
    else:
        tail = ""
    for court in quiet_courts:
        why = why_out(world, court) or "she is already at war with us"
        tail += f" {court_name(world, court, start=True)} would still stay out: {why}."
    return {
        "court": holder, "court_shown": shown, "last": bool(last),
        "joiners": joiners, "joiners_shown": joiners_shown,
        "crossing": crossing, "when": when,
        "line": (head + tail).strip(),
        # The typed line's read-back: one short warning part.
        "short": ((f"erases {court_name(world, holder)}" if last
                   else f"would make "
                        f"{_join_names(joiners_shown or [court_name(world, c) for c in quiet_courts])}"
                        f" fear France past {line_fear}")
                  + (f"; {_join_names(joiners_shown)} would join a coalition" if joiners_shown else "")),
        "peace_label": f"Offer {shown} peace now",
    }


def _cap(text: str) -> str:
    return text[:1].upper() + text[1:] if text else text


def _possessive(name: str) -> str:
    """"Saxony's", "the Papal States'" (`display_names.possessive`)."""
    from backend.display_names import possessive
    return possessive(name)


def league_when(world, region_name: str, joiners: List[str]) -> str:
    """When the league the warning names would gather, in plain words."""
    from backend.game_logic.coalition import (
        THREAT_INSTANT_MIN, brewing_gate, get_nations_at_war_with_target)
    if not joiners:
        return ""
    if _france_league(world) is not None:
        return "at the end of this turn"
    player = _player(world)
    region = (getattr(world, "regions", {}) or {}).get(region_name)
    capital = bool(getattr(region, "is_capital", False)) if region is not None else False
    threat_after = int(getattr(world, "threat_level", 0) or 0) + 2 + (15 if capital else 0)
    at_war = [c for c in get_nations_at_war_with_target(world, player)
              if border_or_stake(world, c)]
    size = len(set(joiners) | set(at_war))
    if size < league_min(world):
        return (f"but a coalition needs {league_min(world)} countries and only {size} "
                f"would stand against us, so not yet")
    if threat_after >= THREAT_INSTANT_MIN:
        return "at the end of this turn"
    gate = int(brewing_gate(world, player))
    if threat_after >= gate:
        return "in about 3 turns"
    return (f"once France's alarm reaches {gate} (it would be {min(100, threat_after)})")


# ═══════════════════════════════════════════════════════════════════════
# The rising — land that is not held
# ═══════════════════════════════════════════════════════════════════════

def rising_applies(world, region) -> bool:
    """A province France ITSELF holds by conquest (its boot owner outside
    France's house), in an armed world with the seam up."""
    if not (armed(world) and unheld_land_rises()) or region is None:
        return False
    player = _player(world)
    if str(getattr(region, "controller", "") or "") != player:
        return False
    title = ((getattr(world, "province_title", None) or {}).get(region.name) or {})
    if str(title.get("kind") or "") != "conquest":
        return False
    boot = _boot_owner(world, region.name)
    return bool(boot) and not in_player_house(world, boot)


def is_held(world, region) -> bool:
    """Troops of France stand in it: a corps or a detached garrison."""
    return bool(world._has_marshal_in_region(region.name, region.controller)
                or world.region_has_detached_garrison(region))


def rises_in(world, region) -> Optional[int]:
    """Turns before an unheld Hostile conquest rises (None when it will not):
    the province window's count."""
    if not rising_applies(world, region):
        return None
    if int(getattr(region, "stability", 100) or 0) > HOSTILE_MAX:
        return None
    if is_held(world, region):
        return None
    return max(1, rule(world, "rises") - int(getattr(region, "unheld_turns", 0) or 0))


def rising_target(world, region_name: str) -> str:
    """Where a rising province goes: its boot court if it stands, else the
    court France took it from if it stands, else its erased boot court rises
    again in it (decision 6 of the plan — a court the game already knows)."""
    boot = _boot_owner(world, region_name)
    title = ((getattr(world, "province_title", None) or {}).get(region_name) or {})
    took_from = str(title.get("from") or "")
    active = set(world.get_active_nations())
    for court in (boot, took_from):
        if court and not in_player_house(world, court) and court in active:
            return court
    for court in (boot, took_from):
        if court and not in_player_house(world, court):
            return court
    return ""


def rise(world, region_name: str) -> Optional[Dict[str, Any]]:
    """The province goes back: controller, a garrison of its own, home
    stability, the title, the record, the war score. Returns the event."""
    region = world.get_region(region_name)
    if region is None:
        return None
    to = rising_target(world, region_name)
    if not to:
        return None
    player = _player(world)
    reborn = to not in set(world.get_active_nations())
    if reborn:
        # the NA-6c latch keeps a dead court from being torn down twice; a court
        # risen again must be erasable again
        latched = getattr(world, "_eliminated_teardown_done", None)
        if isinstance(latched, set):
            latched.discard(to)
    region.controller = to
    world.invalidate_active_nations_cache()
    region.stability = RISEN_STABILITY
    region.garrison_strength = RISEN_GARRISON
    region.garrison_detachment = True
    region.unheld_turns = 0
    from backend.game_logic import game_end as _game_end
    _game_end.record_province_title(world, region_name, _game_end.TITLE_CONQUEST,
                                    player, to)
    _game_end.count_capture(world, player, to, region_name)
    world._recalculate_capture_war_scores(region_name, player, to)
    from backend.game_logic.formations import formed_display_name
    name = formed_display_name(world, to)
    turns = rule(world, "rises")
    if reborn:
        message = (f"{region_name} rose against us after {turns} turns with no French "
                   f"troops in it — {name} rises again there.")
    else:
        message = (f"{region_name} rose against us after {turns} turns with no French "
                   f"troops in it and went back to {name}.")
    world.log_event({"type": "province_rose", "nation": player, "region": region_name,
                     "target_nation": to, "reborn": bool(reborn),
                     "turn": int(getattr(world, "current_turn", 0) or 0)})
    return {"type": "province_rose", "nation": player, "region": region_name,
            "court": to, "reborn": bool(reborn), "message": message}


def tick_risings(world, due: List[str]) -> List[Dict[str, Any]]:
    """`advance_turn`, after the stability growth that counted the turns:
    every province whose count reached the line rises; the ones a turn short
    are named (the morning's warning)."""
    events: List[Dict[str, Any]] = []
    if not (armed(world) and unheld_land_rises()):
        return events
    for name in due:
        event = rise(world, name)
        if event:
            events.append(event)
    line = rule(world, "rises")
    for name in sorted(getattr(world, "_rising_soon", None) or []):
        region = world.get_region(name)
        if region is None or int(getattr(region, "unheld_turns", 0) or 0) != line - 1:
            continue
        to = rising_target(world, name)
        from backend.game_logic.formations import formed_display_name
        events.append({
            "type": "province_restless", "nation": _player(world), "region": name,
            "court": to,
            "message": (f"{name} will rise next turn unless French troops stand there "
                        f"(a corps or a garrison) — it would go back to "
                        f"{formed_display_name(world, to) if to else 'its people'}."),
        })
    world._rising_soon = []
    return events


# ═══════════════════════════════════════════════════════════════════════
# The surfaces — rows the ledger and the map read
# ═══════════════════════════════════════════════════════════════════════

def fear_rows(world) -> List[Dict[str, Any]]:
    """Every court's fear of France, most afraid first: {nation, display,
    fear, joins, border, stake, ally, line, why}. Ints only (GR2)."""
    if not chooses(world):
        return []
    from backend.game_logic.coalition import qualifies_for_coalition
    from backend.game_logic.formations import formed_display_name
    rows: List[Dict[str, Any]] = []
    line = rule(world, "join")
    vassals = getattr(world, "vassals", {}) or {}
    book = getattr(world, "fear_book", None) or {}
    for court in world.get_active_nations():
        if not court or in_player_house(world, court) or court in vassals:
            continue
        fear = fear_of(world, court)
        joins = bool(fear > line and qualifies_for_coalition(court, world))
        causes = [str(r.get("region") or "") for r in ((book.get("causes") or {}).get(court) or [])]
        rows.append({
            "nation": court, "display": formed_display_name(world, court),
            "fear": int(fear), "joins": joins,
            "border": bool(borders_house(world, court)),
            "stake": bool(holds_stake(world, court)),
            "ally": bool(world.are_allies(_player(world), court)),
            "at_war": bool(world.is_at_war(_player(world), court)),
            "why": "" if joins else why_out(world, court),
            "causes": [c for c in causes if c][-CAUSES_KEPT:],
        })
    rows.sort(key=lambda r: (-r["fear"], r["display"]))
    return rows


def league_footer(world) -> str:
    """The rule in one paragraph, plain — the Balance tab under its rows."""
    return (f"Each province we take — by force or at the peace table — frightens the "
            f"countries: the loser and its neighbours most, a capital three times as much, a "
            f"country that lost or wants that land twice as much. A province we hand back "
            f"calms the country it goes to by as much as taking it frightened her. Fear "
            f"falls {rule(world, 'fade')} a turn. "
            f"A country whose fear passes {rule(world, 'join')} joins a coalition against "
            f"us — unless it is our ally, our vassal or under truce with us, or it neither "
            f"borders us (or one of our vassals) nor lost or wants land we hold. A "
            f"coalition needs {league_min(world)} countries. One that joined out of fear "
            f"goes home when its fear falls under {rule(world, 'leave')}.")


def fear_house(world) -> List[str]:
    """France and its vassals — the map's slate in the "Who fears you" mode."""
    if not chooses(world):
        return []
    return sorted(house_members(world))


def fear_map(world) -> Dict[str, int]:
    """{court: fear} for the "Who fears you" map mode — every active court
    outside France's house (0 included, so the map paints the calm too)."""
    if not chooses(world):
        return {}
    out: Dict[str, int] = {}
    vassals = getattr(world, "vassals", {}) or {}
    for court in world.get_active_nations():
        if court and not in_player_house(world, court) and court not in vassals:
            out[str(court)] = int(fear_of(world, court))
    return out
