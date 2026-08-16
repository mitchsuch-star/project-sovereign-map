"""WIN-D3 "The Road Home" — the evacuation corridor and the free march orders.

Build contract: `docs/WAR_WITHDRAWAL_SPEC.md` (gate record §7a).
Evidence: `docs/audits/PLAYTEST_WIN_CAMPAIGN_2026_08_16.md` §5.3 — the turn
Russia accepted peace, four French corps deep in the east could not advance,
could not be supplied, and had no route home that did not cross a frontier
that had become sovereign the instant the ink dried. **Winning the war
stranded the army that won it.**

The rule that produced it is correct: `can_enter_territory` returns False for
PEACE and ARMISTICE, and it should. What was missing is the clause every real
peace treaty carried — the evacuation corridor.

THE DESIGN IN ONE SENTENCE (spec §2): when a war ends, the peace grants a
temporary right of transit home, and every stranded marshal is handed a free
march order to take it. The two halves are deliberately coupled — the right
without the orders is a mechanic nobody notices; the orders without the right
are orders that cannot be obeyed.

WHERE IT LIVES
--------------
* The GRANT is written at the ``set_diplomatic_state`` chokepoint, NOT at
  ``cleanup_war_end``.  PT-J1 established that typed conquest-vassalization
  and the forced-alliance ARMISTICE arm never reach ``cleanup_war_end``, and
  those are exactly the endings most likely to leave armies parked abroad.
  One write, every ending.
* The PERMISSION is ONE arm on ``can_enter_territory`` — the single movement
  chokepoint.  All ~25 movement seams, the AI's threaded candidate sites and
  the strategic-march stall arms inherit it for free, exactly the way the
  naval crossing gate propagated.  No seam-by-seam threading.
* The STATE is ONE new serialized field, ``world.evacuation_grants``, on the
  ``armistice_cooldowns`` idiom: ``{diplo_key: expiry_turn}``, plain ints.

WHAT THE CORRIDOR IS NOT (spec §3.4 — each pinned by a falsifiable test in
``tests/test_win_d3_road_home.py``)
    * It never permits an ATTACK.  Attacking requires WAR; the pair is at
      peace.  The corridor is consulted by the movement predicate only.
    * It never permits a CAPTURE.  The move-capture arm in
      ``movement_executor`` is gated on ``world.is_at_war`` and stays so.
    * It is NOT ``OPEN_BORDERS``.  It expires, and it exists only because a
      war just ended.
    * It DIES instantly if war resumes — a peace instrument cannot outlive
      the peace.
    * It does NOT feed the army.  Supply attrition continues, and that is the
      point: the corridor is a road, not a billet.  Marching home is urgent
      because standing still costs men.

TWO CORRECTIONS TO THE SPEC, MADE HERE AND RECORDED IN §7a
----------------------------------------------------------
1.  **§4.1's predicate would have missed the measured case.**  The spec says
    the orders go to "every marshal standing on soil he now has no right to
    occupy".  The four corps of the playtest were standing on soil France had
    *captured* — their own nation's colour on the map — with the newly-closed
    Russian frontier between them and France.  They occupied nothing they had
    no right to.  So the predicate here is not "whose soil is he on" but
    **"can he reach the body of his own realm at all"**: the home zone is the
    set of his nation's provinces connected to its capital through soil his
    army may legally cross, and a marshal outside it is stranded.  That
    covers the spec's shape *and* the measured one.
2.  **Slack 2 → 3.**  §6 promises the player "three explicit warnings" before
    internment.  With two turns of slack the ladder only fits two.  The
    number is not load-bearing (see the viability rule below); it is sized to
    the promise the design makes.

THE DURATION, AND WHY THE NUMBER IS NOT LOAD-BEARING (spec §3.5)
---------------------------------------------------------------
At the grant, the expiry is ``current_turn + (longest march home) + slack``.
Each turn a stranded marshal is checked for VIABILITY, not for a deadline:

    surplus = (expiry - current_turn) - (his remaining distance home)

A marshal who is genuinely marching closes one province per turn while the
clock also ticks one turn, so his surplus is CONSTANT — the corridor cannot
expire underneath him.  A marshal who stands still keeps his distance while
the clock runs, so his surplus falls.  That is the spec's "self-refreshing
corridor" with no memory of last turn's position, no second serialized field,
and no arbitrary number doing load-bearing work: expiry is derived from the
distance the army actually has to walk.

Surplus therefore reads directly as "turns of dawdling still affordable".
Warnings at 2, 1, 0; internment below 0 (spec §6, gate Q1 = yes).
"""

from __future__ import annotations

from collections import deque
from typing import Dict, List, Optional, Set

# ── The flip lever ────────────────────────────────────────────────────────
# Arm A of the BASELINE_SERIES flip experiment (see the landing record).
# False restores pre-slice behaviour exactly: no grant is ever written, the
# `can_enter_territory` arm can never fire, no order is issued and the tick
# is a no-op.  Kept so the attribution of any harness movement is measured
# rather than asserted.
WITHDRAWAL_ACTIVE = True

# Turns of dawdling the treaty affords beyond the march itself.  Sized to
# §6's promise of three explicit warnings before internment (see module
# docstring correction 2).  In-band tunable.
EVACUATION_SLACK_TURNS = 3

# Backstop so a corridor cannot stand open forever.  Deliberately never bites
# into the march itself — a corps whose road home is longer than this keeps a
# grant long enough to walk it, with the slack trimmed instead.  (Measured on
# the shipped 1805 map: Paris's eccentricity is 13, so this trims slack only
# for genuinely trans-continental cases.)
EVACUATION_MAX_TURNS = 12

# Warn while the surplus has fallen to this or below (but is still viable).
EVACUATION_WARNING_MARGIN = 2

# The order's own record.  Rider-(d) idiom, "words become the record": an
# evacuation march is recognised by the phrase the treaty wrote on it, which
# is also what the player reads in the Orders ledger.  No new serialized
# field on StrategicOrder.
ROAD_HOME_COMMAND = "the road home — safe passage granted by the peace"


# ══════════════════════════════════════════════════════════════════════════
# THE GRANT — state
# ══════════════════════════════════════════════════════════════════════════

def _grants(world) -> Dict[str, int]:
    grants = getattr(world, "evacuation_grants", None)
    if grants is None:
        grants = {}
        world.evacuation_grants = grants
    return grants


def has_evacuation_grant(world, nation_a: str, nation_b: str) -> bool:
    """True while a standing evacuation corridor covers this pair.

    O(1) — a dict get and an int compare.  This is called from
    `can_enter_territory`, which is called from inside pathfinding loops, so
    it must never scan (GR8).
    """
    if not WITHDRAWAL_ACTIVE:
        return False
    grants = getattr(world, "evacuation_grants", None)
    if not grants:
        return False
    key = world._make_diplo_key(nation_a, nation_b)
    expiry = grants.get(key)
    if expiry is None:
        return False
    return int(world.current_turn) <= int(expiry)


def revoke_evacuation_grant(world, nation_a: str, nation_b: str) -> bool:
    """§3.4: a peace instrument cannot outlive the peace.  Called when the
    pair re-enters WAR."""
    grants = getattr(world, "evacuation_grants", None)
    if not grants:
        return False
    key = world._make_diplo_key(nation_a, nation_b)
    return grants.pop(key, None) is not None


# ══════════════════════════════════════════════════════════════════════════
# THE HOME ZONE — "can he reach the body of his own realm at all"
# ══════════════════════════════════════════════════════════════════════════

def _passable(world, nation: str, region_name: str,
              with_grant: bool) -> bool:
    """Whether `nation`'s army may legally stand in this region.

    `with_grant=False` asks the question the peace left behind (used to
    decide WHO is stranded); `with_grant=True` asks it as it stands with the
    corridor open (used to route the march home).
    """
    region = world.regions.get(region_name)
    if region is None:
        return False
    controller = region.controller
    if not controller or controller == nation:
        return True
    from backend.game_logic.diplomacy import can_enter_territory
    return can_enter_territory(world, nation, controller,
                               ignore_evacuation=not with_grant)


def get_home_zone(world, nation: str) -> Set[str]:
    """The provinces of `nation` that its army can actually get back to.

    A flood fill from the seat of government over soil the nation may cross
    WITHOUT the corridor, intersected with the provinces it controls.  A
    captured enclave on the far side of a closed frontier is deliberately NOT
    home — that is the whole point of the measured defect.

    One bounded graph walk (<= 126 nodes on the shipped map), run once per
    signatory per tick and only while a grant stands.  Not a hot path.
    """
    owned = set(world.get_nation_regions(nation))
    if not owned:
        return set()

    seed = world.get_nation_capital(nation)
    if not seed or seed not in owned:
        # The capital has fallen (or the nation has none authored). Fall back
        # to the largest connected body of its own provinces — "the main body
        # of the realm" — so an exiled court still has somewhere to march to.
        seed = _largest_owned_component_seed(world, nation, owned)
    if not seed:
        return set()

    seen = {seed}
    queue = deque([seed])
    while queue:
        current = queue.popleft()
        region = world.regions.get(current)
        if region is None:
            continue
        for adjacent in region.adjacent_regions:
            if adjacent in seen or adjacent not in world.regions:
                continue
            if not _passable(world, nation, adjacent, with_grant=False):
                continue
            seen.add(adjacent)
            queue.append(adjacent)
    return seen & owned


def _largest_owned_component_seed(world, nation: str,
                                  owned: Set[str]) -> Optional[str]:
    """Seed for a capital-less nation: a province in its biggest contiguous
    block of own soil.  Ties break on name so the choice is deterministic."""
    unvisited = set(owned)
    best: Optional[str] = None
    best_size = 0
    while unvisited:
        start = min(unvisited)
        component = {start}
        queue = deque([start])
        while queue:
            current = queue.popleft()
            region = world.regions.get(current)
            if region is None:
                continue
            for adjacent in region.adjacent_regions:
                if adjacent in owned and adjacent not in component:
                    component.add(adjacent)
                    queue.append(adjacent)
        unvisited -= component
        if len(component) > best_size:
            best_size = len(component)
            best = min(component)
    return best


def is_stranded(world, marshal, home: Set[str]) -> bool:
    """Does this corps need the road home?

    Two ways to need it, and BOTH are required or the rule is wrong:

    1. **He has no right to be where he stands.** §4.1's case — the peace
       turned the ground under him into somebody's sovereign soil.
    2. **He cannot get home without the corridor.** The MEASURED case
       (PLAYTEST_WIN_CAMPAIGN §5.3) — he is on soil his own nation holds, so
       he occupies nothing improperly, but the only road back crosses a
       frontier that just shut.

    And the converse matters just as much. §5's first row says a marshal
    "already home / ON PASSABLE SOIL" is untouched — no order, no mention.
    An earlier cut of this function tested only "is he outside the home
    zone", which swept up every corps standing perfectly legally on an
    ALLY's ground: the acceptance run had **the Emperor himself, at Munich
    in allied Bavaria, told to march home or be interned.** Legally placed
    with a road home is not stranded, and is now not treated as such.
    """
    if marshal.location in home:
        return False
    if not _passable(world, marshal.nation, marshal.location,
                     with_grant=False):
        return True
    return distance_home(world, marshal, home, with_grant=False) is None


def _evacuating_marshals(world, nation: str, home: Set[str]) -> List:
    """Standing marshals of `nation` who need the road home."""
    out = []
    for marshal in world.marshals.values():
        if marshal.nation != nation:
            continue
        if marshal.strength <= 0:
            continue
        if getattr(marshal, "captured_by", ""):
            continue
        if not is_stranded(world, marshal, home):
            continue
        out.append(marshal)
    return out


def distance_home(world, marshal, home: Set[str],
                  with_grant: bool = True) -> Optional[int]:
    """Marches from here to the nearest home province.

    `with_grant=True` (the default) routes THROUGH THE CORRIDOR — the road
    he will actually walk. None then means there is no land route at all even
    with safe passage: the cut-off corps of spec §5, which v1 refuses to
    rescue (gate Q4).

    `with_grant=False` asks whether he could have got home anyway, which is
    how `is_stranded` tells a corps that needs the treaty from one that is
    merely abroad.
    """
    if not home:
        return None
    if marshal.location in home:
        return 0
    seen = {marshal.location}
    queue = deque([(marshal.location, 0)])
    while queue:
        current, dist = queue.popleft()
        region = world.regions.get(current)
        if region is None:
            continue
        for adjacent in region.adjacent_regions:
            if adjacent in seen or adjacent not in world.regions:
                continue
            if adjacent in home:
                return dist + 1
            if not _passable(world, marshal.nation, adjacent,
                             with_grant=with_grant):
                continue
            seen.add(adjacent)
            queue.append((adjacent, dist + 1))
    return None


def _nearest_home_region(world, marshal, home: Set[str]) -> Optional[str]:
    """The province the free march order aims at."""
    if not home:
        return None
    if marshal.location in home:
        return marshal.location
    seen = {marshal.location}
    queue = deque([marshal.location])
    while queue:
        current = queue.popleft()
        region = world.regions.get(current)
        if region is None:
            continue
        for adjacent in sorted(region.adjacent_regions):
            if adjacent in seen or adjacent not in world.regions:
                continue
            if adjacent in home:
                return adjacent
            if not _passable(world, marshal.nation, adjacent,
                             with_grant=True):
                continue
            seen.add(adjacent)
            queue.append(adjacent)
    return None


# ══════════════════════════════════════════════════════════════════════════
# HALF ONE — the corridor is opened at the peace
# ══════════════════════════════════════════════════════════════════════════

def open_evacuation_corridor(world, nation_a: str, nation_b: str) -> Dict:
    """Called from `set_diplomatic_state` when a pair LEAVES WAR.

    Writes the grant and hands out the free march orders (half two).  Both
    sides, always — GR5: the ex-enemy's corps on our soil get the same road
    home.  This is not a player courtesy; it is what ending a war means.

    Returns a summary dict (possibly empty) for the caller to log.
    """
    if not WITHDRAWAL_ACTIVE:
        return {}
    if nation_a == nation_b:
        return {}

    marching: List[Dict] = []
    cut_off: List[Dict] = []
    longest = 0

    # A PROVISIONAL grant goes in FIRST, and that ordering is load-bearing.
    # `distance_home` routes WITH the corridor — it has to, since the whole
    # point is the road the corridor opens — so measuring the marches before
    # writing the grant asks every corps to walk a road that does not exist
    # yet. Measured on the ambient harness: every corridor-dependent corps
    # was classified `cut_off`, the duration was derived from whoever
    # happened NOT to need the corridor, the beat announced "0 corps" and
    # then named two, and a peace where EVERY stranded corps needed the
    # corridor wrote no grant at all — the corridor could not open in
    # precisely the case it exists for.
    key = world._make_diplo_key(nation_a, nation_b)
    grants = _grants(world)
    had_grant = key in grants
    previous = grants.get(key)
    grants[key] = int(world.current_turn) + EVACUATION_MAX_TURNS

    for nation in (nation_a, nation_b):
        home = get_home_zone(world, nation)
        for marshal in _evacuating_marshals(world, nation, home):
            dist = distance_home(world, marshal, home)
            if dist is None:
                cut_off.append({"marshal": marshal.name,
                                "nation": nation,
                                "location": marshal.location})
                continue
            longest = max(longest, dist)
            marching.append({"marshal": marshal.name,
                             "nation": nation,
                             "location": marshal.location,
                             "distance": int(dist)})

    if not marching and not cut_off:
        # Nobody is stranded — roll the provisional grant back rather than
        # leave an unused right of transit standing.
        if had_grant:
            grants[key] = previous
        else:
            grants.pop(key, None)
        return {}

    if marching:
        # The backstop never bites into the march itself (see the constant).
        duration = min(longest + EVACUATION_SLACK_TURNS,
                       max(EVACUATION_MAX_TURNS, longest))
        grants[key] = int(world.current_turn) + int(duration)
    else:
        # Everyone stranded is cut off by land. There is no road to grant, so
        # there is no corridor — only the honest beat below (§5, gate Q4).
        duration = 0
        if had_grant:
            grants[key] = previous
        else:
            grants.pop(key, None)

    issued = _issue_road_home_orders(world, nation_a, nation_b)

    summary = {
        "pair": [nation_a, nation_b],
        "expiry": _grants(world).get(key),
        "turns": int(duration),
        "marching": marching,
        "orders": issued,
        "cut_off": cut_off,
    }

    # §4.3: one beat at the peace, naming names and the deadline — and, when
    # a corps has no land route at all, saying so plainly rather than
    # pretending (§5 / gate Q4).
    world.log_event({
        "type": "evacuation_granted",
        "nation_a": nation_a,
        "nation_b": nation_b,
        "region": "",
        "turns": int(duration),
        "marshals": [m["marshal"] for m in marching],
        "destinations": {o["marshal"]: o["to"] for o in issued},
        "cut_off": [c["marshal"] for c in cut_off],
        "message": _grant_message(world, summary),
    })
    return summary


def _grant_message(world, summary: Dict) -> str:
    """The §4.3 beat, told from the reader's side of the table.

    The beat is addressed to the player when he signed it, so it counts HIS
    corps — an early draft counted every stranded marshal on both sides and
    announced "3 corps" while naming one, because the other two were Russian.
    """
    player = getattr(world, "player_nation", "")
    pair = summary.get("pair") or []
    side = player if player in pair else (pair[0] if pair else "")

    marching = [m for m in (summary.get("marching") or [])
                if m["nation"] == side]
    orders = [o for o in (summary.get("orders") or []) if o["nation"] == side]
    cut_off = [c for c in (summary.get("cut_off") or []) if c["nation"] == side]

    parts: List[str] = []
    if orders:
        named = ", ".join(f"{o['marshal']} to {o['to']}" for o in orders[:4])
        more = "" if len(orders) <= 4 else f", and {len(orders) - 4} more behind them"
        corps = "corps stands" if len(marching) == 1 else "corps stand"
        parts.append(
            f"{len(marching)} {corps} on the wrong side of the new frontier. "
            f"Berthier has given them the road home — {named}{more}. They "
            f"have safe passage for {summary['turns']} turns while they "
            f"march.")
    if cut_off:
        names = ", ".join(sorted({c["marshal"] for c in cut_off}))
        parts.append(
            f"{names} can find no land route home at all — cut off, and that "
            f"passage must be negotiated.")
    return " ".join(parts) or "The peace grants safe passage home."


# ══════════════════════════════════════════════════════════════════════════
# HALF TWO — the free march orders
# ══════════════════════════════════════════════════════════════════════════

def is_road_home_order(order) -> bool:
    return bool(order) and getattr(order, "original_command", "") == \
        ROAD_HOME_COMMAND


def next_step_home(world, marshal) -> Optional[str]:
    """The next province on this marshal's road home, or None.

    Consumed by the enemy AI's own rung. The player's marshals walk their
    MOVE_TO through `StrategicOrderProcessor` like any other order, but that
    processor is the PLAYER's — `enemy_ai` has never read `strategic_order`
    at all (grep it: not one reference). Without this the free march order is
    inert for every AI corps, which turns GR5 into a cruel joke: the AI would
    receive a road it cannot see and then be interned for not walking it.
    Measured on the ambient harness before the fix — THREE AI corps interned
    in 40 turns, one of them a single march from home.

    Recomputed from live positions rather than read off the order's cached
    path, so a corps knocked off its route still knows the way.
    """
    if not WITHDRAWAL_ACTIVE:
        return None
    home = get_home_zone(world, marshal.nation)
    if not home or marshal.location in home:
        return None
    destination = _nearest_home_region(world, marshal, home)
    if not destination:
        return None
    path = world.find_path(marshal.location, destination,
                           passable_for=marshal.nation)
    if not path or len(path) < 2:
        return None
    return path[1]


def _issue_road_home_orders(world, nation_a: str, nation_b: str) -> List[Dict]:
    """Hand every stranded corps of either signatory a march order home.

    §4.1: 0 AP (it is not the player's order, it is the treaty's), does not
    touch the order economy, and is an ORDINARY order once issued — it shows
    in the Orders ledger and the player who wants to march somewhere else
    simply says so.

    A marshal who already has a standing order the player gave him is left
    alone: the treaty offers a road, it does not overrule the Emperor.
    """
    from backend.models.marshal import StrategicOrder

    issued: List[Dict] = []
    for nation in (nation_a, nation_b):
        home = get_home_zone(world, nation)
        if not home:
            continue
        for marshal in _evacuating_marshals(world, nation, home):
            existing = getattr(marshal, "strategic_order", None)
            if existing is not None and not is_road_home_order(existing):
                continue  # the player's own order stands
            destination = _nearest_home_region(world, marshal, home)
            if not destination:
                continue  # cut off — §5, refused honestly, never invented
            if (existing is not None and is_road_home_order(existing)
                    and existing.target == destination):
                continue  # already marching there
            path = world.find_path(marshal.location, destination,
                                   passable_for=marshal.nation) or []
            marshal.strategic_order = StrategicOrder(
                command_type="MOVE_TO",
                target=destination,
                target_type="region",
                started_turn=int(world.current_turn),
                original_command=ROAD_HOME_COMMAND,
                path=path,
                issued_turn=int(world.current_turn),
            )
            issued.append({"marshal": marshal.name,
                           "nation": nation,
                           "from": marshal.location,
                           "to": destination})
    return issued


# ══════════════════════════════════════════════════════════════════════════
# THE PER-TURN TICK — refresh, warn, intern, retire
# ══════════════════════════════════════════════════════════════════════════

def _is_immobile(marshal) -> bool:
    """A corps that physically cannot march this turn is not loitering.

    Recovery from a rout takes turns the marshal does not control, so the
    corridor waits for him rather than interning a man who is trying.
    Fortification is deliberately NOT here: breaking camp is free and is a
    choice (spec §5's last row — he is not teleported out of his own state
    machine).
    """
    return int(getattr(marshal, "retreat_recovery", 0) or 0) > 0


def process_evacuation_grants(world) -> List[Dict]:
    """One pass per turn over the standing corridors.

    Runs late in `advance_turn`, after the strategic marches of the cycle
    have already been executed, so "how far is he still from home" is
    measured on where he actually stands now.

    THE PASS IS ORGANISED BY MARSHAL, NOT BY GRANT, and that is load-bearing.
    A nation may hold several corridors at once (France made peace with
    Austria on one turn and Russia on another), and the first draft here
    walked the grants and judged every stranded marshal against each — so a
    corps marching home well inside its generous Russian corridor was
    interned by an unrelated, shorter Austrian one that had nothing to do
    with his road, and warned twice in the same tick besides. Measured, then
    fixed: each marshal is judged ONCE, against the most generous passage
    any standing treaty affords his nation. A grant that is irrelevant to
    his route cannot shorten it; a genuine loiterer still runs out of all of
    them.

    Returns tactical events for the dispatch/campaign log.
    """
    events: List[Dict] = []
    if not WITHDRAWAL_ACTIVE:
        return events
    grants = getattr(world, "evacuation_grants", None)
    if not grants:
        return events

    current = int(world.current_turn)

    # ── Retire dead pairs, and collect each nation's best standing passage ──
    best_expiry: Dict[str, int] = {}
    pairs: Dict[str, List[str]] = {}
    for key in sorted(grants):
        parts = key.split("|")
        if len(parts) != 2:
            grants.pop(key, None)
            continue
        # A resumed war has already revoked the grant at the state setter;
        # this is the belt-and-braces read for a save written mid-flight.
        if world.get_diplomatic_state(parts[0], parts[1]) == "WAR":
            grants.pop(key, None)
            continue
        expiry = int(grants[key])
        pairs[key] = parts
        for nation in parts:
            if expiry > best_expiry.get(nation, -1):
                best_expiry[nation] = expiry

    # ── Judge each stranded marshal once ───────────────────────────────────
    stranded_by_nation: Dict[str, int] = {}
    grace_nations: Set[str] = set()
    for nation in sorted(best_expiry):
        expiry = best_expiry[nation]
        home = get_home_zone(world, nation)

        # A corps that has arrived is done with the treaty's order. The
        # player's marshals clear a completed MOVE_TO through the strategic
        # processor; the AI's have nothing that would, so the order would
        # otherwise sit on them forever and keep re-triggering the P1.2 rung.
        for marshal in world.marshals.values():
            if (marshal.nation == nation and marshal.location in home
                    and is_road_home_order(
                        getattr(marshal, "strategic_order", None))):
                marshal.strategic_order = None

        for marshal in list(_evacuating_marshals(world, nation, home)):
            stranded_by_nation[nation] = stranded_by_nation.get(nation, 0) + 1
            dist = distance_home(world, marshal, home)
            if dist is None:
                # Cut off (§5 / gate Q4): v1 refuses to invent a rescue — and
                # refuses just as firmly to intern a corps for failing to walk
                # a road that does not exist.
                continue
            if _is_immobile(marshal):
                grace_nations.add(nation)
                continue
            surplus = (expiry - current) - int(dist)
            if surplus < 0:
                events.append(_intern(world, marshal, nation))
            elif surplus <= EVACUATION_WARNING_MARGIN:
                events.append(_warn(world, marshal, nation, dist, surplus))

    # ── Refresh, and retire what is finished ───────────────────────────────
    for key, parts in pairs.items():
        if key not in grants:
            continue
        if grace_nations.intersection(parts):
            # A corps reforming after a rout costs the treaty a turn, not an
            # army. Rewriting the int IS the refresh (no second field).
            grants[key] = int(grants[key]) + 1
            continue
        if not any(stranded_by_nation.get(n) for n in parts):
            # Everybody is home. The corridor closes because it is finished,
            # not because it timed out.
            grants.pop(key, None)
        elif current > int(grants[key]):
            grants.pop(key, None)

    return events


def _encircling_power(world, marshal) -> Optional[str]:
    """The foreign power with the most ground around him.

    Used only to name the captor when a corps is interned inside its own
    cut-off enclave. Ties break on name so the answer is deterministic.
    """
    region = world.regions.get(marshal.location)
    if region is None:
        return None
    tally: Dict[str, int] = {}
    for adjacent in region.adjacent_regions:
        neighbour = world.regions.get(adjacent)
        if neighbour is None or not neighbour.controller:
            continue
        if neighbour.controller == marshal.nation:
            continue
        tally[neighbour.controller] = tally.get(neighbour.controller, 0) + 1
    if not tally:
        return None
    return max(sorted(tally), key=lambda n: tally[n])


def _warn(world, marshal, nation: str, distance: int, surplus: int) -> Dict:
    event = {
        "type": "evacuation_lapsing",
        "marshal": marshal.name,
        "nation": nation,
        "location": marshal.location,
        "region": marshal.location,
        "distance": int(distance),
        "turns_left": int(surplus),
        # "has not moved" would be a lie, and the acceptance run caught it
        # telling one: a corps that marched EAST all turn was reported as
        # having "not moved from Lithuania". Nothing here tracks movement —
        # it tracks whether he can still reach home in the time left — so
        # that is what the sentence says.
        "message": (
            f"{marshal.name} is no nearer home — {distance} march(es) still "
            f"to go from {marshal.location}, and {surplus} turn(s) of safe "
            f"passage left before his corps is interned."),
    }
    world.log_event(dict(event))
    return event


def _intern(world, marshal, nation: str) -> Dict:
    """§6 (gate Q1 = yes): the passage lapsed and the corps is still standing,
    illegally, on a sovereign power's soil.  It is interned — removed from the
    field as a diplomatic incident, through the ONE PC15-1 removal seam, so it
    inherits the tombstone, the dispatch ladder and the gazette for free.

    The interning power is whoever actually holds the ground he would not
    leave — and when that ground is his OWN (the measured case: a cut-off
    enclave his army captured and never left), it is the power that has him
    surrounded. An earlier cut read the controller unconditionally and
    produced "Marshal Davout's corps was interned at Volhynia BY FRANCE",
    naming his own Emperor as his captor.
    """
    region = world.regions.get(marshal.location)
    host = (region.controller if region is not None and region.controller
            else "")
    if host == marshal.nation:
        host = _encircling_power(world, marshal) or ""
    name = marshal.name
    location = marshal.location
    world.destroy_marshal(marshal, cause="interned", victor=host)
    return {
        "type": "marshal_interned",
        "marshal": name,
        "nation": marshal.nation,
        "location": location,
        "host": host,
        "message": (
            f"{name}'s corps failed to quit {host} soil before its safe "
            f"passage expired. It has been disarmed and interned."),
    }
