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

from backend.commands.strategic import clear_order_bound_interrupt  # NPC-2

# ── The flip lever ────────────────────────────────────────────────────────
# Arm A of the BASELINE_SERIES flip experiment (see the landing record).
# False restores pre-slice behaviour exactly: no grant is ever written, the
# `can_enter_territory` arm can never fire, no order is issued and the tick
# is a no-op.  Kept so the attribution of any harness movement is measured
# rather than asserted.
WITHDRAWAL_ACTIVE = True

# WO-17 "The Corridor Has a Direction" (WEIRD_OUTCOMES_SPEC §3 slice 13).
# False restores the direction-less grant exactly — the Trojan-corridor
# exploit's control arm: park one corps deep on enemy soil, sign a 1-DP
# armistice, and march FRESH corps into enemy sovereign territory all truce
# long.  Kept so the fix is falsifiable non-vacuously and so any harness
# movement can be flip-attributed.
CORRIDOR_DIRECTION_ACTIVE = True

# FA-33 (slice 12).  False restores the stamp exactly — the treaty's order
# carries `issued_turn = current_turn`, `process_strategic_orders` skips it as
# "first step already executed by executor.py", and the corps loses the peace
# turn standing still.  Measured on the shipped board, lever up vs down:
# Davout home turn 5 with ZERO warnings, vs turn 6 warned on t2/t3/t4/t5.
THE_TREATY_CLAIMS_NO_FIRST_STEP = True

# FA-33 rider (slice 12).  False restores the pre-slice judging exactly.
# Removing the stamp un-shields the issuance turn from `_check_interrupts`
# (the skip `continue`d ABOVE it), so a corps frozen on an unanswered
# order-bound question would be interned EARLIER than before the fix —
# measured: interned at Vienna on turn 5 having marched nothing, against
# Bohemia on turn 6 having marched one province.  A corps that cannot march
# because the game is waiting on the player is not loitering.
A_STANDING_QUESTION_IS_NOT_LOITERING = True

# FA-N61 (slice 12).  False restores the one-shot issuance exactly: the road
# is handed out only at the moment the war ends, and a corps stranded
# afterwards — by the counterpart's OTHER wars capturing the ground under
# him — is never handed one.  Measured on the shipped 1805 board, lever
# down: Bernadotte and Massena stranded at t3/t4, warned 2/1/0, and BOTH
# interned on turn 7 with `order=None` on every line in between.
THE_ROAD_IS_OFFERED_WHILE_HE_IS_STRANDED = True

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


def has_evacuation_grant(world, nation_a: str, nation_b: str,
                         mover_location: Optional[str] = None) -> bool:
    """True while a standing evacuation corridor covers this pair — AND, when
    the mover's standing location is named, while the corridor is actually
    FOR that mover (WO-17 "The Corridor Has a Direction").

    Argument order carries the direction: `nation_a` is the MOVER's nation,
    `nation_b` the host whose territory is being entered — the order
    `can_enter_territory` already passes.

    THE DIRECTION TERM is the spec's own §4.1 predicate ("can he reach the
    body of his own realm at all") applied to the entry side: the grant
    belongs to a corps that cannot get home without it.  A mover standing in
    its nation's home zone — or standing anywhere it could already walk home
    from without the treaty (allied soil, at-war third-party soil) — has no
    claim on the corridor and may NOT use it to enter the counterpart's
    territory.  A genuinely stranded corps keeps full transit, including
    from its OWN cut-off enclave (the measured Volhynia shape — which is why
    this is the stranded predicate and not a bare controller compare); the
    moment it stands on soil it no longer needs the treaty to leave, the
    grant is spent for it.  Fully derived — zero new serialized fields.

    ``mover_location=None`` (the legacy pair-level form) keeps the arm
    permissive, because the callers that cannot name a mover are not
    relocation seams — every seam that MOVES a corps passes the mover's
    standing location, and `test_wo_slice13_corridor_direction.py` carries
    the census pin that keeps the bare-call set audited.

    O(1) on the hot path (GR8) — a dict get and an int compare, plus (only
    while a grant stands and a mover is named) a memoised stranded lookup:
    `world._evac_direction_cache` is keyed per turn and per
    ``(nation, location)`` and is flushed by `invalidate_bloc_members_cache`,
    the chokepoint every region-control and diplomatic-state mutation
    already reaches, so the flood fill runs once per board state, not once
    per pathfinding node.
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
    if int(world.current_turn) > int(expiry):
        return False
    if (CORRIDOR_DIRECTION_ACTIVE and mover_location is not None
            and not _corridor_is_for(world, nation_a, mover_location)):
        return False
    return True


def _corridor_is_for(world, nation: str, location: str) -> bool:
    """WO-17 direction term: does a corps of `nation` standing at `location`
    have a claim on the corridor?  A memoised `is_stranded_at`.

    The cache is transient (never serialized), keyed per turn, and cleared
    by `invalidate_bloc_members_cache` — home zones and stranded verdicts
    read region control plus war/peace geometry, the exact mutation families
    that chokepoint already collects (the NA-0 idiom).  The per-turn key is
    belt-and-braces: the bloc invalidation is not guaranteed to fire on a
    bare turn advance.
    """
    cache = getattr(world, "_evac_direction_cache", None)
    turn = int(world.current_turn)
    if not isinstance(cache, dict) or cache.get("turn") != turn:
        cache = {"turn": turn, "zones": {}, "stranded": {}}
        world._evac_direction_cache = cache
    key = (nation, location)
    hit = cache["stranded"].get(key)
    if hit is not None:
        return hit
    home = cache["zones"].get(nation)
    if home is None:
        home = get_home_zone(world, nation)
        cache["zones"][nation] = home
    value = is_stranded_at(world, nation, location, home)
    cache["stranded"][key] = value
    return value


def revoke_evacuation_grant(world, nation_a: str, nation_b: str) -> bool:
    """§3.4: a peace instrument cannot outlive the peace.  Called when the
    pair re-enters WAR."""
    # WO-17 review round: the war just resumed one frame ago — drop any
    # direction verdicts warmed under the peace (same reasoning as the
    # flush in `open_evacuation_corridor`, mirrored).
    world._evac_direction_cache = None
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

    WO-17 note: the `with_grant=True` form deliberately does NOT pass a
    `mover_location` (so the direction term stays permissive here).  Its only
    consumers route marshals that were ALREADY judged stranded — a marshal in
    the home zone short-circuits out of `distance_home_from` /
    `_nearest_home_region` before this is ever reached — so threading the
    location would change nothing, and the audited bare form keeps the
    routing walk O(1) per node.
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
    return is_stranded_at(world, marshal.nation, marshal.location, home)


def is_stranded_at(world, nation: str, location: str,
                   home: Optional[Set[str]] = None) -> bool:
    """Location-form of `is_stranded` — the same predicate, no marshal object.

    WO-17 factored it out because the corridor's DIRECTION term judges a
    mover by where it stands, and that judgement must be byte-identical to
    the one that decides who receives a road-home order: one predicate, two
    consumers, no drift.
    """
    if home is None:
        home = get_home_zone(world, nation)
    if location in home:
        return False
    if not _passable(world, nation, location, with_grant=False):
        return True
    return distance_home_from(world, nation, location, home,
                              with_grant=False) is None


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
    return distance_home_from(world, marshal.nation, marshal.location, home,
                              with_grant=with_grant)


def distance_home_from(world, nation: str, location: str, home: Set[str],
                       with_grant: bool = True) -> Optional[int]:
    """Location-form of `distance_home` (WO-17 factoring — same walk,
    no marshal object)."""
    if not home:
        return None
    if location in home:
        return 0
    seen = {location}
    queue = deque([(location, 0)])
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
            if not _passable(world, nation, adjacent,
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

    # WO-17 review round [F3]: the diplomatic state changed one frame ago,
    # and the routing below reads the direction cache through
    # `find_path(passable_for=…)`. The `set_diplomatic_state` chokepoint's
    # own flush runs AFTER this function returns, so a verdict warmed under
    # the pre-peace geometry (the enclave read "connected home through
    # war-passable soil") would deny the freshly-stranded corps its own
    # corridor during order issuance — measured: the road-home order
    # shipped with an EMPTY path (self-healing on the first strategic tick,
    # but the beat and the ledger row showed a road with no route). Flush
    # first, so issuance and every later reader see post-peace geometry.
    world._evac_direction_cache = None

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

    # FA-N61: a NEW treaty is a NEW offer — but only for a nation that had
    # NO passage standing at all.
    #
    # The first cut cleared every marshal of both signatories unconditionally,
    # and that was wrong in a way I found by attacking my own fix: a SECOND,
    # unrelated peace defeated the first one's refusal.  Measured — Davout
    # declines the Austrian road, the tick correctly leaves him alone, then
    # France makes peace with Russia and he is handed the Austrian road again,
    # because the Russian corridor's opener wiped the record for every French
    # marshal.  His situation had not changed; only somebody else's treaty had.
    for nation in (nation_a, nation_b):
        if _nation_has_standing_grant(world, nation, exclude=key):
            continue
        for marshal in world.marshals.values():
            if marshal.nation == nation:
                marshal.road_home_offered = False

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

    # FA-33 rider (slice 12).  §4.3 promises a beat "naming names and the
    # deadline"; it named nobody whenever every stranded corps already held
    # an order of the Emperor's, because the sentence above is keyed on
    # `orders` and the treaty issues none to a marshal it will not overrule
    # (§4.1).  Measured in an archived campaign: four corps stood on Austrian
    # soil under a typed `hold position`, the beat read "The peace grants
    # safe passage home.", and the first name the player read was an
    # internment.  The treaty says which corps it declined to move, and why.
    ordered = [m["marshal"] for m in marching
               if m["marshal"] not in {o["marshal"] for o in orders}
               and m["marshal"] not in {c["marshal"] for c in cut_off}]
    if ordered:
        named = ", ".join(sorted(ordered))
        holds = "holds" if len(ordered) == 1 else "hold"
        parts.append(
            f"{named} {holds} under your own orders and {'was' if len(ordered) == 1 else 'were'} "
            f"not moved — the treaty offers a road, it does not overrule the "
            f"Emperor. Their passage lapses with the corridor.")

    return " ".join(parts) or "The peace grants safe passage home."


# ══════════════════════════════════════════════════════════════════════════
# HALF TWO — the free march orders
# ══════════════════════════════════════════════════════════════════════════

def is_road_home_order(order) -> bool:
    return bool(order) and getattr(order, "original_command", "") == \
        ROAD_HOME_COMMAND


def _the_enemy_took_his_order(marshal) -> bool:
    """Was this corps' order destroyed by a BATTLE rather than by the Emperor?

    Slice-12 review round, and it is the answer to my own argument turned
    against me.  `road_home_offered` is keyed on ISSUANCE precisely so it
    covers every way the order can be let go — but three engine sites null a
    `strategic_order` with no player anywhere near it: the encircled retreat,
    the forced retreat, and the shattered army (`combat_executor`, each one
    followed by `clear_order_bound_interrupt`).  Measured: a corps whose road
    home was cancelled by a forced retreat was never re-offered one and was
    interned, having refused nothing.  A latch that cannot tell a refusal
    from a rout is a latch that punishes the wrong thing.

    The two retreat sites leave `retreating` True; the shattered site clears
    it and sets `broken`.  Both are cleared by the ordinary recovery tick, so
    the release is self-limiting and needs no new field and no edit at the
    three seams — which matters, because "fix it at the seams somebody
    thought to name" is the failure this whole latch exists to avoid.
    """
    return (bool(getattr(marshal, "retreating", False))
            or bool(getattr(marshal, "broken", False)))


def _nation_has_standing_grant(world, nation: str,
                               exclude: Optional[str] = None) -> bool:
    """Is any corridor already open for this nation (other than `exclude`)?

    FA-N61: the difference between "a new peace" and "a second concurrent
    peace". The refusal record lapses with the treaty that made the offer,
    so it is cleared when a nation goes from no passage to some — never when
    it simply gains a second.
    """
    grants = getattr(world, "evacuation_grants", None) or {}
    for key, expiry in grants.items():
        if key == exclude:
            continue
        if nation in key.split("|") and int(world.current_turn) <= int(expiry):
            return True
    return False


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
    issued: List[Dict] = []
    for nation in (nation_a, nation_b):
        issued.extend(offer_road_home(world, nation))
    return issued


def offer_road_home(world, nation: str) -> List[Dict]:
    """The per-nation half of `_issue_road_home_orders`, shared with the tick.

    FA-N61 (slice 12) needed the SAME body at a second caller — the per-turn
    judge — and the four guards below are what makes that safe, so they are
    shared rather than re-earned:

      1. a standing order the player gave stands (`test_a_standing_player_
         order_is_not_overruled`);
      2. a corps with no land route is refused honestly, never invented for
         (`test_no_order_is_invented_for_a_corps_with_no_road`);
      3. a corps already marching to the same place is left alone;
      4. FA-N61: a corps the treaty has ALREADY offered the road to, and
         who no longer holds it, is not chased.  `road_home_offered` is
         written where the road is GIVEN and read where it would be given
         again, and that siting is the whole point.  `strategic_order =
         None` is written at MANY seams a player answer can reach — the
         typed cancel and `POST /cancel_order` converge on
         `_execute_cancel`, but `_respond_blocked_path` alone clears an
         order at five different places, and `_respond_combat_stalemate`
         and `_respond_cannon_fire` at more.  (Two independent censuses of
         that set disagreed on the count, because "player-reachable answer"
         versus "engine outcome" is not a line either of them drew; the
         number is deliberately not quoted here.)  A guard keyed on
         CANCELLATION would have been fixed only at the seams somebody
         thought to name.  Keyed on ISSUANCE, it covers every way the order
         can be let go, including ways nobody has enumerated.

    `_evacuating_marshals` (not "whose soil is he on") is the membership
    predicate — see the module docstring's correction 1.
    """
    from backend.models.marshal import StrategicOrder

    issued: List[Dict] = []
    home = get_home_zone(world, nation)
    if not home:
        return issued
    for marshal in _evacuating_marshals(world, nation, home):
        if _the_enemy_took_his_order(marshal):
            # The latch records a REFUSAL, and a battle is not one.
            marshal.road_home_offered = False
        existing = getattr(marshal, "strategic_order", None)
        if existing is not None and not is_road_home_order(existing):
            continue  # the player's own order stands
        if existing is not None and is_road_home_order(existing):
            # He is HOLDING the treaty's road. Record it here as well as at
            # issuance, because the "already marching there" guard below
            # returns without touching him — and a marshal who reached this
            # loop with the road in hand and a cleared flag would have his
            # next cancel silently overruled.
            marshal.road_home_offered = True
        if (existing is None and THE_ROAD_IS_OFFERED_WHILE_HE_IS_STRANDED
                and bool(getattr(marshal, "road_home_offered", False))):
            continue  # he was handed the road and let it go — §4.1 cancellable
        destination = _nearest_home_region(world, marshal, home)
        if not destination:
            continue  # cut off — §5, refused honestly, never invented
        if (existing is not None and is_road_home_order(existing)
                and existing.target == destination):
            continue  # already marching there
        path = world.find_path(marshal.location, destination,
                               passable_for=marshal.nation) or []
        order_kwargs = {}
        if not THE_TREATY_CLAIMS_NO_FIRST_STEP:
            # FA-33's control arm: the stamp whose documented premise
            # ("first step already executed by executor.py") is false for
            # the only StrategicOrder in the codebase built outside
            # `strategic_executor`.
            order_kwargs["issued_turn"] = int(world.current_turn)
        marshal.strategic_order = StrategicOrder(
            command_type="MOVE_TO",
            target=destination,
            target_type="region",
            started_turn=int(world.current_turn),
            original_command=ROAD_HOME_COMMAND,
            path=path,
            **order_kwargs,
        )
        marshal.road_home_offered = True
        # NPC-2: the treaty's order replaces whatever was standing, so
        # the question that order raised dies with it.
        clear_order_bound_interrupt(marshal)
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

    A standing QUESTION is deliberately NOT here — see
    `_awaiting_the_players_word`.  It is the same mercy, but it must not have
    the same SCOPE, and the slice-12 review round measured why.
    """
    return int(getattr(marshal, "retreat_recovery", 0) or 0) > 0


def _awaiting_the_players_word(marshal) -> bool:
    """Is this corps frozen on a question only the player can answer?

    `process_strategic_orders` defers a marshal with a `pending_interrupt`
    and never executes his march until it is answered, so both families
    stop him: an ORDER-BOUND ask raised by the road itself (cannon fire on
    the way home, a blocked step) and a STANDALONE decision he is owed
    (`last_stand`, `muster_confirm`).  The predicate is deliberately the
    whole set rather than `ORDER_BOUND_INTERRUPT_TYPES` alone — a cornered
    marshal awaiting "fight or break out" cannot walk home either.

    ⚠ THE SCOPE IS THE POINT, and the slice-12 review round measured why.
    The first cut routed this through `_is_immobile`, which adds the
    marshal's NATION to `grace_nations` and refreshes the whole corridor.
    Measured: two French corps stranded, ONE of them frozen on a question,
    the other simply refusing to march — the refuser was never interned,
    his warning read the identical "2 turn(s) of safe passage left"
    fourteen turns running, and the corridor's expiry walked 10 → 23 and
    never closed.  Since `has_evacuation_grant` gates the transit arm on
    `can_enter_territory`, that is a permanent right of passage bought with
    one unanswered modal — and it is not exotic: in an unattended 12-turn
    run Bernadotte picked up an organic `cannon_fire` ask at t4 and held
    the corridor open by himself for the remaining nine turns.

    So this mercy is MARSHAL-scoped: the frozen corps is not judged, and
    the clock keeps running for everybody else, including him.  The comment
    that said the grace was "bounded in the only sense that matters"
    measured the offset and not the calendar, and it was wrong.
    """
    from backend.commands.strategic import (
        ORDER_BOUND_INTERRUPT_TYPES, STANDALONE_DECISION_TYPES,
    )
    pending = getattr(marshal, "pending_interrupt", None)
    if not isinstance(pending, dict):
        return False
    return pending.get("interrupt_type") in (
        ORDER_BOUND_INTERRUPT_TYPES | STANDALONE_DECISION_TYPES)


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
    best_counterpart: Dict[str, str] = {}
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
                # FA-N61: the beat below names the treaty it rides on, and
                # the fog filter reads the pair — so remember which treaty
                # is affording this nation its most generous passage.
                best_counterpart[nation] = (parts[1] if parts[0] == nation
                                            else parts[0])

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
            if marshal.nation == nation and marshal.location in home:
                # FA-N61: he is home; the next treaty finds him with a clean
                # slate rather than remembering a road he declined a war ago.
                marshal.road_home_offered = False
                if is_road_home_order(getattr(marshal, "strategic_order",
                                              None)):
                    marshal.strategic_order = None
                    clear_order_bound_interrupt(marshal)  # NPC-2

        # ── FA-N61: the offer stands while he is stranded ─────────────────
        # The judge re-derives who is stranded EVERY turn; issuance ran ONCE,
        # at the treaty.  A corps stranded afterwards — Austria's other wars
        # taking the ground under him — was warned three times and interned
        # without ever being handed a road.  The offer is renewed here,
        # BEFORE the judging pass below, so that a corps discovered stranded
        # is offered the road in the same tick he is judged on it rather
        # than one tick later — and so the events read in the order they
        # happened.  It does NOT spare him that tick's warning: `_warn` is
        # keyed on distance and surplus, not on whether he holds an order,
        # and the measured organic case warns Massena on the very tick he is
        # topped up (surplus 2, a late stranding with little slack). An
        # earlier draft of this comment claimed otherwise and the mutation
        # sweep caught the claim, not the code.
        if THE_ROAD_IS_OFFERED_WHILE_HE_IS_STRANDED:
            for offer in offer_road_home(world, nation):
                event = _offer_event(
                    world, offer,
                    best_counterpart.get(nation, ""),
                    max(0, expiry - current))
                if event is not None:
                    events.append(event)

        for marshal in list(_evacuating_marshals(world, nation, home)):
            stranded_by_nation[nation] = stranded_by_nation.get(nation, 0) + 1
            dist = distance_home(world, marshal, home)
            if dist is None:
                # Cut off (§5 / gate Q4): v1 refuses to invent a rescue — and
                # refuses just as firmly to intern a corps for failing to walk
                # a road that does not exist.
                continue
            if _is_immobile(marshal):
                # A rout is bounded (0-3 stages) and pre-slice, so it still
                # buys the whole corridor a turn.
                grace_nations.add(nation)
                continue
            if (A_STANDING_QUESTION_IS_NOT_LOITERING
                    and _awaiting_the_players_word(marshal)):
                # MARSHAL-scoped, deliberately: he is not judged, and
                # nobody else's clock stops. See the predicate's docstring.
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
            #
            # FA-33 rider (slice 12): `retreat_recovery` is bounded 0-3, an
            # unanswered question is not — so the grant grows for as long as
            # the player leaves a modal on his own screen unanswered.  That
            # is deliberate and it is bounded in the only sense that matters:
            # `expiry - current_turn` is CONSTANT under grace (both sides
            # gain one), so the window never widens, and the surplus a
            # marching corps would carry is preserved rather than spent on
            # the game's own silence.  Measured over nine grace turns: the
            # int walks 9 -> 17 while the offset holds at 7.  A clamp to
            # `current + EVACUATION_MAX_TURNS` was written here and REMOVED
            # after measurement — `duration` may legitimately exceed 12 for a
            # trans-continental march (longest 15 -> duration 15), and the
            # clamp would have SHORTENED that corridor by three turns.
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


def _offer_event(world, offer: Dict, counterpart: str,
                 turns_left: int) -> Optional[Dict]:
    """FA-N61: the top-up says so.

    The measured organic case lost two marshals with no player-visible cause
    at all — the first thing said about either was an `evacuation_lapsing`
    line two turns from internment, and it opened "is no nearer home" about a
    corps that had had an order for zero turns.  A road handed out mid-treaty
    is news: nobody ordered that march, and the player is about to watch a
    corps he did not move walk across the map.

    It rides the EXISTING `evacuation_granted` type, with the pair and the
    turns filled in honestly, plus one new key (`mid_treaty`) the renderers
    branch on — the `jealousy.py` idiom.  A new type would have cost ten
    `len(CAMPAIGN_LOG_TYPES)` pins for a sentence.  ("nine" and "160" were
    both stale on the day this was written; FA-R5 paid that price knowingly
    for a whole surface, not for a sentence.)

    ⚠ IT IS TOLD FROM THE PLAYER'S SIDE OF THE TABLE, and the slice-12
    review round measured the cost of forgetting that.  The fog arm for
    `evacuation_granted` admits any SIGNATORY, which is right for the
    treaty's own beat (both courts signed it) and wrong for a per-corps
    bulletin published every turn: with no side filter, France read
    *"Berthier has put ArchdukeJohn on the road home to Bohemia"* about an
    Austrian corps it could not see, naming his province and his
    destination, in France's own chief of staff's voice, with the campaign
    log rendering it "under the peace with France".  `_grant_message` — the
    producer this one sits beside — carries a docstring paragraph about
    exactly this, written after an early draft counted both sides.
    """
    if str(offer.get("nation") or "") != str(
            getattr(world, "player_nation", "") or ""):
        return None
    event = {
        "type": "evacuation_granted",
        "nation_a": offer["nation"],
        "nation_b": counterpart,
        "region": offer["from"],
        "turns": int(turns_left),
        "marshals": [offer["marshal"]],
        "destinations": {offer["marshal"]: offer["to"]},
        "cut_off": [],
        "mid_treaty": True,
        "message": (
            f"{offer['marshal']} is on the wrong side of the frontier at "
            f"{offer['from']}, Sire — the ground changed hands under him. "
            f"Berthier has put him on the road home to {offer['to']}; he has "
            f"{int(turns_left)} turn(s) of safe passage."),
    }
    world.log_event(dict(event))
    return event


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
    # Aug 30, 2026 review: `destroy_marshal` returns False when it CAPTURES
    # instead of removing — the sovereign death-guard converts every removal
    # of a standing Emperor into a capture (NP-4: the road to the Eagle in
    # Chains is captivity, never a quiet deletion). This was the one removal
    # call site that discarded the return, so an Emperor whose safe passage
    # lapsed was reported "disarmed and interned" while the engine had in fact
    # taken him prisoner — the single most consequential event in the game,
    # announced as a footnote about paperwork.
    removed = world.destroy_marshal(marshal, cause="interned", victor=host)
    if removed is False:
        return {
            "type": "sovereign_captured",
            "marshal": name,
            "nation": marshal.nation,
            "location": location,
            "host": host,
            "message": (
                f"{name} failed to quit {host} soil before his safe passage "
                f"expired — the Emperor is taken."),
        }
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
