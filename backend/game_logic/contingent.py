"""VD-C "The Contingent" — VASSAL_DEEPENING_SPEC.md §9 (gate record §9.1,
SCORE_FINISH_SPEC.md Step 5 SR-8a; rules SYSTEMS_REFERENCE.md §90).

A loyal satellite is FOR men. In a war it shares with its lord, a loyal
satellite raises a contingent scaled by its income and its loyalty. The
contingent marches to join its lord's host and fights on the lord's flag;
the satellite pays its men, and its loyalty bleeds by its dead. When the
shared war ends it marches home — crowned, decimated, or merely home — and
stands down; on a break it walks out of the lord's lines with its men
(La Romana's Spaniards in 1808, Yorck's Prussians at Tauroggen in 1812).

Every rule keys off the vassal row and the shared war, for every lord
(GR5). The record lives in ONE serialized store, `world.vassal_contingents`
(keyed by the vassal), so a record outlives a vassal row that a break
deletes — the four exit hooks read it there (Golden Rule 4: get the value,
use it, then clear), and a per-turn reconciliation closes whatever an exit
nobody named leaves behind.

The contingent's marshal flies the LORD's flag with `original_nation` set to
the satellite — the assimilated-corps marker VS-4 Rule 1b and IQ-7 R1 read —
so a wavering satellite's contingent holds back from the lord's musters and
reinforcements exactly as the tier line says, and the regiments clause of
the wavering line becomes true for the boot satellites.
"""

from __future__ import annotations

from typing import Dict, List, Optional

# ═══════ levers (BASELINE_SERIES attribution arms; never a config surface) ═══════
# THE_CLIENT_SENDS_ITS_CONTINGENT  False = no contingent is ever RAISED. Data
#     already on the board (a record across a save) is still honoured.
# THE_CLIENT_PAYS_ITS_MEN          False = a serving contingent bills its lord
#     like any corps (upkeep, the force limit, the levy, the Grande Armée).
# A_CLIENTS_GENERAL_IS_NOT_THE_EMPERORS_MARSHAL  False = a corps of a client's
#     colours stands on its lord's glory ladder and expects from its lord's
#     purse like any of his marshals (R12, gate record §9.1).
THE_CLIENT_SENDS_ITS_CONTINGENT = True
THE_CLIENT_PAYS_ITS_MEN = True
A_CLIENTS_GENERAL_IS_NOT_THE_EMPERORS_MARSHAL = True

# ═══════ the numbers (gate record §9.1, ruled October 3, 2026; in-band tunable) ═══════
CONTINGENT_MEN_PER_INCOME = 15      # men per gold of the satellite's province income
CONTINGENT_ROUND = 500              # sized in half-battalions of the ledger
CONTINGENT_MIN = 3000               # below this a client sends nothing
CONTINGENT_MAX = 12000              # the largest 1805-scale client contingent
CONTINGENT_REST_TURNS = 6           # turns after it came home (or was lost)
CONTINGENT_DEAD_PER_LOYALTY = 500   # one point of loyalty per 500 of its dead
CONTINGENT_DEAD_LOYALTY_CAP = 10    # the most one tick's dead can cost
CONTINGENT_CROWN_LOYALTY = 8        # it won in the field and brought half home
CONTINGENT_DECIMATED_LOYALTY = 5    # it brought fewer than half home
CONTINGENT_CROWN_SHARE = 0.5        # the share that must come home (both arms)
CONTINGENT_KEPT_LOYALTY = 2         # a turn, while the lord holds them from home
CONTINGENT_HOMEWARD_TURNS = 8       # after this long on the road it stands down where it is

DEFAULT_PERSONALITY = "cautious"
DEFAULT_SKILL = 5
DEFAULT_TRUST = 60

# The one free order the contingent is given — the road home. Its
# `original_command` names it so the AI's road-home rung and the
# kept-from-home bleed can tell it apart from an order the lord gave.
# (No march to the host is issued at the raise: measured, a free march on a
# player's corps raised the strategic-interrupt questions a march raises —
# a cannon-fire ask the turn its host moved on — on a corps the player
# never ordered. The contingent musters and awaits the lord's orders; the
# raise beat names the nearest host.)
CONTINGENT_HOME_COMMAND = "the road home — the contingent returns to its own colours"

LOG_TYPE = "vassal_contingent"
DISPATCH_TYPE = "diplomatic_vassal_contingent"

_ROMAN = ("", "", " II", " III", " IV", " V", " VI", " VII", " VIII")


# ═══════════════════════ reads (pure) ═══════════════════════

def _store(world) -> Dict[str, dict]:
    store = getattr(world, "vassal_contingents", None)
    if store is None:
        store = {}
        world.vassal_contingents = store
    return store


def contingent_record(world, vassal: str) -> Optional[dict]:
    return (getattr(world, "vassal_contingents", None) or {}).get(vassal)


def shared_enemies(world, lord: str, vassal: str) -> List[str]:
    """The courts the lord and the satellite are BOTH at war with (sorted)."""
    if not lord or not vassal:
        return []
    lords = set(world.get_nations_at_war_with(lord) or [])
    clients = set(world.get_nations_at_war_with(vassal) or [])
    return sorted(n for n in lords & clients if n not in (lord, vassal))


def _held(world, nation: str) -> List[str]:
    return list(world.get_nation_regions(nation) or [])


def contingent_income(world, vassal: str) -> int:
    """The satellite's authored province income (`Region.income_value`) —
    the figure the gate record's size is scaled by."""
    total = 0
    for name in _held(world, vassal):
        region = world.regions.get(name)
        if region is not None:
            total += int(getattr(region, "income_value", 0) or 0)
    return int(total)


def contingent_size(world, vassal: str, loyalty: Optional[int] = None) -> int:
    """15 men per gold of income × loyalty/100, rounded down to 500, inside
    [3,000, 12,000] and the satellite's infantry pool; 0 = it cannot send."""
    row = (getattr(world, "vassals", {}) or {}).get(vassal) or {}
    if loyalty is None:
        loyalty = int(row.get("loyalty", 0) or 0)
    raw = contingent_income(world, vassal) * CONTINGENT_MEN_PER_INCOME
    raw = raw * max(0, min(100, int(loyalty))) // 100
    size = (raw // CONTINGENT_ROUND) * CONTINGENT_ROUND
    size = min(CONTINGENT_MAX, size)
    pool = int(((getattr(world, "manpower_pools", {}) or {})
                .get(vassal, {}) or {}).get("infantry", 0) or 0)
    size = min(size, (pool // CONTINGENT_ROUND) * CONTINGENT_ROUND)
    return int(size) if size >= CONTINGENT_MIN else 0


def client_paid_names(world, lord: str) -> set:
    """The lord's serving contingents — outside his establishment while the
    client pays its men (`calculate_turn_upkeep` skips them)."""
    if not THE_CLIENT_PAYS_ITS_MEN:
        return set()
    names = set()
    for record in (getattr(world, "vassal_contingents", None) or {}).values():
        if record.get("lord") == lord and record.get("marshal"):
            names.add(str(record["marshal"]))
    return names


def is_clients_general(marshal) -> bool:
    """R12 (gate record §9.1): a corps of a client's colours — a contingent
    or an assimilated corps, both marked by `original_nation` — is its
    court's, not the Emperor's. It fights and obeys as any corps does, but
    holds no rung on its lord's glory ladder (it envies no one and no one
    envies it) and expects nothing from its lord's purse: its own court
    rewards it (Louis Bonaparte's Holland gave Dumonceau its own marshal's
    baton). The ONE predicate `jealousy` and `dotation` read."""
    origin = getattr(marshal, "original_nation", None)
    return bool(A_CLIENTS_GENERAL_IS_NOT_THE_EMPERORS_MARSHAL and origin
                and origin != getattr(marshal, "nation", None))


def is_contingent_home_order(order) -> bool:
    return bool(order) and getattr(order, "original_command", "") == \
        CONTINGENT_HOME_COMMAND


def contingent_of(world, marshal) -> Optional[str]:
    """The satellite whose serving contingent this marshal commands, or None."""
    if marshal is None:
        return None
    name = getattr(marshal, "name", None)
    for vassal, record in (getattr(world, "vassal_contingents", None) or {}).items():
        if record.get("marshal") == name:
            return vassal
    return None


def _fields_assimilated_corps(world, lord: str, vassal: str) -> bool:
    """The lord already fields the satellite's own corps (an assimilated
    marshal standing): its men are already in his line."""
    for marshal in getattr(world, "marshals", {}).values():
        if (getattr(marshal, "original_nation", None) == vassal
                and getattr(marshal, "nation", "") == lord
                and int(getattr(marshal, "strength", 0) or 0) > 0
                and not getattr(marshal, "captured_by", "")):
            return True
    return False


def contingent_dead_tick(world, vassal: str) -> int:
    """The contingent's dead since the last tick (any fall in its strength;
    all of it if the corps is gone or taken), recording today's figure.
    Called once a tick, from `process_vassal_loyalty` (the bleed)."""
    record = contingent_record(world, vassal)
    if not record:
        return 0
    marshal = world.marshals.get(record.get("marshal") or "")
    last = int(record.get("last_strength", 0) or 0)
    if marshal is None or getattr(marshal, "captured_by", ""):
        current = 0
    elif getattr(marshal, "nation", "") != record.get("lord"):
        # walked out or stood down by an unhooked path — not dead men
        record["last_strength"] = 0
        return 0
    else:
        current = int(getattr(marshal, "strength", 0) or 0)
    record["last_strength"] = current
    return max(0, last - current)


def contingent_kept_from_home(world, vassal: str) -> bool:
    """The lord holds the contingent from its road home: no shared war
    stands, it is not home, and it carries an order the lord gave instead."""
    record = contingent_record(world, vassal)
    if not record or record.get("state") != "homeward":
        return False
    marshal = world.marshals.get(record.get("marshal") or "")
    if marshal is None or getattr(marshal, "nation", "") != record.get("lord"):
        return False
    if marshal.location in _held(world, vassal):
        return False
    order = getattr(marshal, "strategic_order", None)
    if order is None or is_contingent_home_order(order):
        return False
    target = getattr(order, "target", "")
    return target not in _held(world, vassal)


def contingent_next_step(world, marshal) -> Optional[str]:
    """The AI's road-home step for a contingent (the P1.2 rung): toward the
    order's target, by a road its flag may walk."""
    order = getattr(marshal, "strategic_order", None)
    if not is_contingent_home_order(order):
        return None
    target = getattr(order, "target", "")
    if not target or marshal.location == target:
        return None
    path = world.find_path(marshal.location, target,
                           passable_for=marshal.nation)
    if not path or len(path) < 2:
        return None
    return path[1]

# ═══════════════════════ the commander ═══════════════════════

def _name_taken(world, name: str) -> bool:
    if name in getattr(world, "marshals", {}):
        return True
    if name in (getattr(world, "fallen_marshals", None) or {}):
        return True
    for candidates in (getattr(world, "marshal_pool", None) or {}).values():
        for candidate in candidates or []:
            if (candidate or {}).get("name") == name:
                return True
    return False


def pick_commander(world, vassal: str) -> dict:
    """The satellite's next commander: the first authored one (the scenario's
    `contingents` key) who is not serving, fallen or on any bench; else
    "<Adjective> Contingent", with a numeral when that name is taken."""
    authored = (getattr(world, "contingent_commanders", None) or {}).get(vassal) or []
    for candidate in authored:
        name = str((candidate or {}).get("name") or "")
        if name and not _name_taken(world, name):
            return dict(candidate)
    from backend.display_names import nation_adjective
    base = f"{nation_adjective(vassal)} Contingent"
    for numeral in _ROMAN[1:]:
        name = base + numeral
        if not _name_taken(world, name):
            return {"name": name}
    return {"name": f"{base} of turn {int(world.current_turn)}"}


# ═══════════════════════ the road ═══════════════════════

def _issue_march(world, marshal, target: str, command: str) -> bool:
    """A free MOVE_TO (0 AP — it is the treaty's order, not the lord's),
    the WIN-D3 idiom: no `issued_turn` stamp, so the first step is walked
    (FA-33). An ordinary order once issued — the lord may give another."""
    from backend.commands.strategic import clear_order_bound_interrupt
    from backend.models.marshal import StrategicOrder
    if not target or target == marshal.location:
        return False
    path = world.find_path(marshal.location, target,
                           passable_for=marshal.nation) or []
    if not path:
        return False
    marshal.strategic_order = StrategicOrder(
        command_type="MOVE_TO",
        target=target,
        target_type="region",
        started_turn=int(world.current_turn),
        original_command=command,
        path=path,
    )
    clear_order_bound_interrupt(marshal)
    return True


def _find_host(world, lord: str, origin: str, exclude: str = "") -> Optional[object]:
    """The lord's nearest standing field marshal by road (ties by name):
    strength > 0, not a prisoner, not another contingent."""
    contingents = {str(r.get("marshal")) for r in
                   (getattr(world, "vassal_contingents", None) or {}).values()}
    best = None
    for marshal in sorted(getattr(world, "marshals", {}).values(),
                          key=lambda m: m.name):
        if (marshal.nation != lord or marshal.name == exclude
                or marshal.name in contingents
                or int(getattr(marshal, "strength", 0) or 0) <= 0
                or getattr(marshal, "captured_by", "")
                or getattr(marshal, "original_nation", None)):
            continue
        if marshal.location == origin:
            return marshal
        # From the candidate host's own ground (WO-17: a passable_for
        # pathfind starts at the mover's standing location).
        path = world.find_path(marshal.location, origin, passable_for=lord)
        if not path:
            continue
        if best is None or len(path) < best[0]:
            best = (len(path), marshal)
    return best[1] if best else None


def _home_target(world, vassal: str) -> Optional[str]:
    from backend.game_logic.recruitment import find_spawn_region
    return find_spawn_region(world, vassal)


# ═══════════════════════ the beats ═══════════════════════

def _beat(world, *, beat: str, vassal: str, lord: str, marshal_name: str,
          line: str, **extra) -> dict:
    """ONE event shape for every beat: the campaign log row, the end-turn
    event and (for the player's own satellites, else fog-ruled) the
    dispatch line."""
    event = {
        "type": LOG_TYPE,
        "beat": beat,
        "vassal": vassal,
        "lord": lord,
        "nation": lord,
        "marshal": marshal_name,
        "turn": int(world.current_turn),
        "message": line,
    }
    event.update(extra)
    world.log_event(dict(event))
    from backend.game_logic.dispatch import queue_dispatch_event
    player = getattr(world, "player_nation", "France")
    queue_dispatch_event(
        world, DISPATCH_TYPE, {"line": line, "nation": vassal, "lord": lord},
        "always" if player in (lord, vassal) else "partial_on_nation")
    return event


def _shown(world, nation: str, capitalize: bool = False) -> str:
    from backend.display_names import display_nation, with_definite_article
    return with_definite_article(display_nation(nation), capitalize=capitalize)


def _men(n: int) -> str:
    return f"{int(n):,}"


# ═══════════════════════ the four verbs ═══════════════════════

def raise_contingent(world, vassal: str) -> Optional[dict]:
    """Mint the satellite's contingent on its lord's flag at its muster
    province (the `recruitment.commission_marshal` idiom) and march it to
    the host. Returns the beat, or None when the satellite cannot send."""
    from backend.game_logic.recruitment import find_spawn_region
    from backend.models.marshal import create_marshal_from_data
    row = (getattr(world, "vassals", {}) or {}).get(vassal)
    if not row:
        return None
    lord = str(row.get("lord") or "")
    size = contingent_size(world, vassal)
    spawn = find_spawn_region(world, vassal)
    if not lord or size <= 0 or not spawn:
        return None
    candidate = pick_commander(world, vassal)
    name = str(candidate["name"])
    skills = dict(candidate.get("skills") or {})
    ctor = {
        "name": name,
        "nation": lord,
        "location": spawn,
        "strength": int(size),
        "personality": str(candidate.get("personality") or DEFAULT_PERSONALITY),
        "tactical_skill": int(candidate.get("tactical_skill")
                              or skills.get("tactical") or DEFAULT_SKILL),
        "skills": {key: int(skills.get(key, DEFAULT_SKILL)) for key in (
            "tactical", "shock", "defense", "logistics", "administration",
            "command")},
        "starting_trust": int(((candidate.get("trust") or {}).get("value"))
                              or DEFAULT_TRUST),
    }
    if candidate.get("biography"):
        ctor["biography"] = str(candidate["biography"])
    marshal = create_marshal_from_data(ctor)
    marshal.original_nation = vassal
    pools = world.manpower_pools.setdefault(vassal, {})
    pools["infantry"] = int(pools.get("infantry", 0) or 0) - int(size)
    world.marshals[name] = marshal
    from backend.game_logic.doctrines import refresh_doctrine_terms
    refresh_doctrine_terms(world, [marshal])

    host = _find_host(world, lord, spawn, exclude=name)
    _store(world)[vassal] = {
        "marshal": name,
        "lord": lord,
        "raised_turn": int(world.current_turn),
        "raised_strength": int(size),
        "last_strength": int(size),
        "won_at_raise": int(getattr(marshal, "battles_won", 0) or 0),
        "state": "serving",
        "homeward_turn": None,
        "host": host.name if host is not None else "",
    }
    from backend.display_names import humanize_entity_name
    host_clause = ""
    if host is not None:
        host_name = humanize_entity_name(host.name)
        host_clause = (f" They stand with {host_name}." if host.location == spawn
                       else f" The nearest host is {host_name} at {host.location}.")
    line = (f"{_shown(world, vassal, capitalize=True)} sends "
            f"{_men(size)} men under {name} to the colours at {spawn} — they "
            f"await the orders of {_shown(world, lord)}.{host_clause} "
            f"{_shown(world, vassal, capitalize=True)} pays them; their dead "
            f"will be its grief.")
    return _beat(world, beat="raised", vassal=vassal, lord=lord,
                 marshal_name=name, line=line, strength=int(size),
                 location=spawn, host=host.name if host is not None else "")


def stand_down(world, vassal: str, *, reason: str) -> Optional[dict]:
    """The contingent comes home: its survivors go back to the satellite's
    infantry pool (any men beyond its raised strength to the lord's), the
    marshal leaves the board WITHOUT a tombstone (he did not fall —
    `WorldState.stand_down_marshal`), the homecoming is judged, and the
    satellite rests. `reason` is "home" (it reached its own soil),
    "found_its_way" (the road ran out), "recalled" (release / transfer)."""
    store = _store(world)
    record = store.pop(vassal, None)
    if not record:
        return None
    lord = str(record.get("lord") or "")
    marshal = world.marshals.get(record.get("marshal") or "")
    survivors = int(getattr(marshal, "strength", 0) or 0) if marshal else 0
    raised = int(record.get("raised_strength", 0) or 0)
    if marshal is not None:
        back = min(survivors, raised)
        extra = max(0, survivors - raised)
        pools = world.manpower_pools.setdefault(vassal, {})
        pools["infantry"] = int(pools.get("infantry", 0) or 0) + back
        if extra and lord:
            lord_pools = world.manpower_pools.setdefault(lord, {})
            lord_pools["infantry"] = int(lord_pools.get("infantry", 0) or 0) + extra
        world.stand_down_marshal(marshal)
    won = (int(getattr(marshal, "battles_won", 0) or 0) if marshal else 0) \
        - int(record.get("won_at_raise", 0) or 0)
    outcome, delta = _judge(survivors, raised, won)
    row = (getattr(world, "vassals", {}) or {}).get(vassal)
    applied = 0
    if row is not None and row.get("lord") == lord and reason != "recalled":
        before = int(row.get("loyalty", 0) or 0)
        row["loyalty"] = max(0, min(100, before + delta))
        applied = int(row["loyalty"]) - before
        row["contingent_rest_until"] = int(world.current_turn) + CONTINGENT_REST_TURNS
    name = str(record.get("marshal") or "")
    line = _home_line(world, vassal, name, survivors, raised, outcome, applied, reason)
    return _beat(world, beat="home", vassal=vassal, lord=lord, marshal_name=name,
                 line=line, outcome=outcome, reason=reason,
                 survivors=int(survivors), raised=int(raised),
                 loyalty_delta=int(applied))


def _judge(survivors: int, raised: int, won: int) -> tuple:
    if raised <= 0:
        return "home", 0
    if survivors < raised * CONTINGENT_CROWN_SHARE:
        return "decimated", -CONTINGENT_DECIMATED_LOYALTY
    if won >= 1:
        return "crowned", CONTINGENT_CROWN_LOYALTY
    return "home", 0


def _home_line(world, vassal, name, survivors, raised, outcome, applied, reason) -> str:
    client = _shown(world, vassal, capitalize=True)
    if reason == "recalled":
        return (f"{client} recalls its contingent — {name} leads "
                f"{_men(survivors)} of {_men(raised)} men home.")
    road = (" by its own roads" if reason == "found_its_way" else "")
    loyalty = (f" ({'+' if applied > 0 else ''}{applied} loyalty)" if applied else "")
    if outcome == "crowned":
        return (f"{name}'s contingent comes home{road} crowned with victory — "
                f"{_men(survivors)} of {_men(raised)} men. {client} rejoices{loyalty}.")
    if outcome == "decimated":
        return (f"{name}'s contingent comes home{road} decimated — "
                f"{_men(survivors)} of {_men(raised)} men. {client} counts its "
                f"widows{loyalty}.")
    return (f"{name}'s contingent comes home{road} — {_men(survivors)} of "
            f"{_men(raised)} men.")


def lose_contingent(world, vassal: str) -> Optional[dict]:
    """The corps was destroyed or taken in the field: no homecoming — the
    record closes decimated and the satellite rests."""
    store = _store(world)
    record = store.pop(vassal, None)
    if not record:
        return None
    lord = str(record.get("lord") or "")
    name = str(record.get("marshal") or "")
    row = (getattr(world, "vassals", {}) or {}).get(vassal)
    applied = 0
    if row is not None and row.get("lord") == lord:
        before = int(row.get("loyalty", 0) or 0)
        row["loyalty"] = max(0, before - CONTINGENT_DECIMATED_LOYALTY)
        applied = int(row["loyalty"]) - before
        row["contingent_rest_until"] = int(world.current_turn) + CONTINGENT_REST_TURNS
    marshal = world.marshals.get(name)
    fate = "taken" if (marshal is not None and getattr(marshal, "captured_by", "")) \
        else "destroyed"
    client = _shown(world, vassal, capitalize=True)
    line = (f"{name}'s contingent is {fate} in the field — none of its "
            f"{_men(int(record.get('raised_strength', 0) or 0))} men will come home. "
            f"{client} counts its widows"
            + (f" ({applied} loyalty)." if applied else "."))
    return _beat(world, beat="lost", vassal=vassal, lord=lord, marshal_name=name,
                 line=line, outcome="decimated", fate=fate,
                 loyalty_delta=int(applied))


def walk_out(world, vassal: str, *, reason: str) -> Optional[dict]:
    """A break: the contingent walks out of its lord's lines with its men.
    Closes the record only — the break's own hand-back (every exit's
    `original_nation` loop) puts the marshal under his own flag."""
    store = _store(world)
    record = store.pop(vassal, None)
    if not record:
        return None
    lord = str(record.get("lord") or "")
    name = str(record.get("marshal") or "")
    marshal = world.marshals.get(name)
    men = int(getattr(marshal, "strength", 0) or 0) if marshal else 0
    client = _shown(world, vassal, capitalize=True)
    lord_shown = _shown(world, lord)
    line = (f"{name} marches {_men(men)} men out of {lord_shown}'s lines — "
            f"{client}'s contingent goes with its crown.")
    return _beat(world, beat="walked_out", vassal=vassal, lord=lord,
                 marshal_name=name, line=line, reason=reason, strength=int(men))


# ═══════════════════════ the exits (hooks) ═══════════════════════

def on_release(world, vassal: str, *, rebellion: bool) -> Optional[dict]:
    """`release_vassal`'s hook, read BEFORE its hand-back loop and row
    deletion: a voluntary release recalls the contingent (it stands down at
    once); a rebellion release walks it out."""
    if not contingent_record(world, vassal):
        return None
    if rebellion:
        return walk_out(world, vassal, reason="rebellion")
    return stand_down(world, vassal, reason="recalled")


def on_transfer(world, vassal: str) -> Optional[dict]:
    """`transfer_vassal`'s hook, read BEFORE its re-key loop: the men were
    lent to the old lord, never to the new — recalled, they stand down."""
    if not contingent_record(world, vassal):
        return None
    return stand_down(world, vassal, reason="recalled")


def on_break(world, vassal: str, lord: str) -> Optional[dict]:
    """`complete_vassal_break`'s hook (rebellion, graceful independence,
    armistice) and the lord-eliminated exit's: the contingent walks out."""
    record = contingent_record(world, vassal)
    if not record or (lord and record.get("lord") != lord):
        return None
    return walk_out(world, vassal, reason="break")


# ═══════════════════════ the per-turn pass ═══════════════════════

def process_vassal_contingents(world) -> List[dict]:
    """Once a turn, after the loyalty tick (which already charged the dead):
    reconcile, close the lost, walk the homeward, stand down the arrived,
    and raise for the loyal in a shared war. Every lord (GR5)."""
    events: List[dict] = []
    store = _store(world)
    vassals = getattr(world, "vassals", {}) or {}
    turn = int(world.current_turn)

    # 1. Records an unnamed exit left behind.
    for vassal in sorted(store):
        record = store.get(vassal)
        row = vassals.get(vassal)
        if row is not None and row.get("lord") == record.get("lord"):
            continue
        marshal = world.marshals.get(record.get("marshal") or "")
        if marshal is not None and marshal.nation == record.get("lord") \
                and not getattr(marshal, "captured_by", ""):
            event = stand_down(world, vassal, reason="recalled")
        elif marshal is not None and marshal.nation == vassal:
            event = walk_out(world, vassal, reason="break")
        else:
            event = lose_contingent(world, vassal)
        if event:
            events.append(event)

    for vassal in sorted(vassals):
        row = vassals[vassal]
        lord = str(row.get("lord") or "")
        record = store.get(vassal)
        if record:
            marshal = world.marshals.get(record.get("marshal") or "")
            if (marshal is None or getattr(marshal, "captured_by", "")
                    or int(getattr(marshal, "strength", 0) or 0) <= 0):
                event = lose_contingent(world, vassal)
                if event:
                    events.append(event)
                continue
            if marshal.nation != lord:
                event = walk_out(world, vassal, reason="break")
                if event:
                    events.append(event)
                continue
            if shared_enemies(world, lord, vassal):
                if record.get("state") == "homeward":
                    record["state"] = "serving"
                    record["homeward_turn"] = None
                continue
            if marshal.location in _held(world, vassal):
                event = stand_down(world, vassal, reason="home")
                if event:
                    events.append(event)
                continue
            if record.get("state") != "homeward":
                record["state"] = "homeward"
                record["homeward_turn"] = turn
                target = _home_target(world, vassal)
                _issue_march(world, marshal, target, CONTINGENT_HOME_COMMAND)
                events.append(_beat(
                    world, beat="marching_home", vassal=vassal, lord=lord,
                    marshal_name=marshal.name,
                    line=(f"The war {_shown(world, vassal)} shared with "
                          f"{_shown(world, lord)} is over — {marshal.name}'s "
                          f"contingent takes the road home to {target}."),
                    target=target or ""))
                continue
            if turn - int(record.get("homeward_turn") or turn) >= CONTINGENT_HOMEWARD_TURNS:
                event = stand_down(world, vassal, reason="found_its_way")
                if event:
                    events.append(event)
                continue
            if getattr(marshal, "strategic_order", None) is None:
                # The road was lost to a battle, a stall or a cancel: the
                # satellite calls its men home again (an override the lord
                # GAVE is a different order — the kept-from-home bleed).
                _issue_march(world, marshal, _home_target(world, vassal),
                             CONTINGENT_HOME_COMMAND)
            continue

        if not THE_CLIENT_SENDS_ITS_CONTINGENT:
            continue
        if int(row.get("contingent_rest_until", 0) or 0) > turn:
            continue
        from backend.game_logic.vassal import vassal_military_contribution
        if vassal_military_contribution(world, vassal) != "loyal":
            continue
        if not shared_enemies(world, lord, vassal):
            continue
        if _fields_assimilated_corps(world, lord, vassal):
            continue
        event = raise_contingent(world, vassal)
        if event:
            events.append(event)
    return events
