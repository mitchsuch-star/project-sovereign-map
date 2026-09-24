"""Emergent designs & the volte-face — where the surprises live (AI-5b).

Spec: docs/AI_INTENT_SPEC.md §3.6 (v1.3 substrate ruling), §11.1 Stage E.

AI-5b(i) — THE WORLD WRITES CONTENT THE AUTHOR DID NOT. Every design in
the shipped decks is authored; the most interesting designs in history
were *acquired*, by being humiliated — Prussia's design after Jena was
not Prussia's design before it. A nation that is partitioned, stripped
of its capital, forced into a punitive settlement, or betrayed by a
reneged bargain that took its soil PROMOTES the grievance into a real
`acquire_regions` deck entry — front-inserted, so every downstream
system already built (NA-1 legibility, NA-2 acceptance, NA-3 resolve and
target bias, intent, the war council) consumes it for free.

The §3.6 v1.3 substrate ruling, honoured exactly:
- Partition and capital loss need NO new store — derived from serialized
  `nation_starting_regions` vs live control (the survival-override
  comparison).
- A punitive settlement gets a durable `settlement_memories` record
  (`memory_type="punitive_settlement"`, expires_in=None) written at the
  ratify seams — settlement_ratify, settlement_third_party, and
  WorldState._ratify_treaty all call `record_punitive_cessions`.
- A broken compensation bargain already has an owner (§3.3 + pin 8) —
  read here, never re-stored.
- `betrayal_history["grievance_flags"]` is NOT extended (its to_dict
  projects four scalar keys; a `provinces` field would silently vanish).

The three code-forced constraints (§3.6), each pinned in tests:
(a) the promoted entry is a plain `acquire_regions` entry — one of the
    five AGENDA_TYPES, so `_entry_active` and the validator both know it;
(b) FRONT-inserted — `get_active_agenda` is first-predicate-wins, so an
    appended entry behind a still-active design would never activate;
(c) the survival override OUTRANKS the deck and fires on exactly the
    states promotion fires on — so the design is recorded AT the
    humiliation and ACTIVATES when the override clears, structurally,
    because the override sits above the deck walk.

Bounds: at most ONE emergent design per nation, ever (`emergent` key on
the entry is the latch); promotion is announced as a beat
(`design_promoted`, town-crier visible — diplomacy has no fog); the
PLAYER is excluded (France's wants are the player's own choices — the
§3.5 mirror is France's row; the shipped scenario authors France no
deck, and pin 18 rests on that), and vassals are excluded while
vassalized (the dormant-deck doctrine — a satellite released later
promotes then, if the loss still stands).

AI-5b(ii) — THE VOLTE-FACE (§3.6-4). A great power beaten and then
COURTED — rather than beaten and humiliated — can reverse in one
signing, from enemy to partner, and be aimed at a third party. Tilsit.
`volte_face_receptive` is the eligibility read; the proactive courier
lives in ai_diplomacy (the beaten court proposes the alliance itself and
names the design it would advance to); `maybe_fire_volte_face` is the
beat-5 hook at the alliance-ratify chokepoint. The deck-advance needs no
machinery at all: an ALLIANCE puts the reversed power inside the
hegemon's bloc, `_contain_active` reads self-in-bloc as dormancy, and
`get_active_agenda` walks on to the next authored entry —
`arbiter_of_europe` yields to `gulf_and_straits` (§12.2's object). If
the alliance later breaks, containment wakes again: Tilsit collapses
into 1812 by the same read, unscripted.

Zero new serialized fields anywhere in this module: promoted entries
ride the already-serialized `world.agendas` deck store; the punitive
record rides `world.settlement_memories`; volte-face state is derived.
"""

from typing import Dict, List, Optional, Tuple

# ── Blessed numbers (in-band tunable; shape changes escalate) ────────────
# A settlement is PUNITIVE when it strips this many provinces in one
# signing (the victim's capital alone always qualifies).
PUNITIVE_SETTLEMENT_MIN_PROVINCES = 2
# Derived-partition promotion bar: this many homeland provinces in
# foreign hands (capital alone always qualifies; ONE province qualifies
# when a punitive record or a renege grievance marks the holder).
EMERGENT_DESIGN_MIN_LOST = 2
# The volte-face window: turns since the war with the hegemon ended.
# IQ-6 V1 "The window fits the courtship" (September 14, 2026): 15 -> 20.
# Measured: from the boot war relations (-80/-90) war freezes drift and
# the game's best courting lever (Improve Relations, +8 at Talleyrand's
# skill, +1 thaw below -10) reaches the courted floor at best 16 turns
# after the peace — so a PERFECT player stood at 29 when the 15-turn
# window closed and the beat was unreachable by construction. At 20 it
# fired on 2 of 2 courted arms, 0 of 1 uncourted, 0 of 4 ambient.
VOLTE_FACE_WINDOW = 20
VOLTE_FACE_WINDOW_BEFORE_IQ6 = 15
# The ceiling (pinned): Austria's ROUTINE ladder alliance (open borders ->
# non-aggression -> defensive alliance -> alliance, her own asks) landed
# 25 turns after the war on the measured arm — a window of 26+ would
# announce an ordinary alliance as a reversal.
VOLTE_FACE_WINDOW_CEILING = 25
# Courted = relations at or above the ALLIANCE ratify requirement — the
# courier never offers what the treaty gate would refuse (honest
# availability; STATE_RELATION_REQUIREMENTS["ALLIANCE"] is 40).
VOLTE_FACE_RELATION_FLOOR = 40
# The wrecked-army mark: war exhaustion still visibly bleeding off after
# a lost war. IQ-6 V3 RETIRED this arm under GR9 (lever
# THE_DEFEAT_IS_THE_SOIL): the constant stays for the lever-down arm only.
VOLTE_FACE_WE_MARK = 40

# ── IQ-6 "Europe Speaks Its Mind" flip levers (September 14, 2026) ─────
# Each False reproduces the pre-IQ-6 game on its surface byte-for-byte.
#
# V1 — the window fits the courtship (20, not 15).
THE_WINDOW_FITS_THE_COURTSHIP = True
# V3 — the defeat is the soil. The either/or "war exhaustion >= 40 OR
# homeland soil in the hegemon's bloc's hands" read an arm the ordinary
# route can never satisfy: R49 (`diplomacy.cleanup_war_end`) zeroes a
# court's exhaustion at every peace that ends its last war, and even
# without R49 the coalition tick decays it 5 a turn — a mark of ~70 is
# under 40 within ~6 turns, while the courting needs 14+. The two
# clauses could never hold together, so the white-peace case the arm was
# written for ("Friedland's mark was the army, not the map") was a
# promise the game could not keep. RETIRED, not repaired: repairing it
# means stamping the war's outcome on every war instance (a serialized
# shape change on every AI-vs-AI peace too), which needs a user ruling on
# §3.6's zero-new-fields contract. Re-open condition: a future row that
# records the war's outcome on the war instance under that ruling.
THE_DEFEAT_IS_THE_SOIL = True
# V4 — it speaks its mind: when every clause but COURTED holds, the
# counsel and the war room say so (display only, GR6).
VOLTE_FACE_SPEAKS_ITS_MIND = True
# V1b — a separate peace ends the war (found building T2, beyond the
# contract; its own lever so the lead can take or leave it). "Its war
# with the hegemon ended" was read off the PARTICIPANT (`exited_turn`,
# stamped only when a court's LAST pair on the instance resolves) or the
# instance's `ended_turn`. A bilateral peace resolves the pair
# (`diplo_key_meta[pair]["resolved_turn"]`, `cleanup_war_end` ->
# `resolve_pair_to_resolved`) but leaves the court at war with the
# hegemon's allies — measured on the 1805 board, France's bilateral
# peace with Austria leaves Austria|Bavaria and Austria|KingdomOfItaly
# active, so Pressburg's own geometry was NEVER "recently beaten" and
# the door never opened. The pair is asked first now (PR-1's lesson,
# one predicate over). False = the participant/instance read only.
THE_SEPARATE_PEACE_ENDS_THE_WAR = True

# The machine names of the eligibility clauses, in evaluation order.
VOLTE_CLAUSE_IDENTITY = "identity"          # the hegemon itself / the player
VOLTE_CLAUSE_TIER = "not_major"
VOLTE_CLAUSE_VASSAL = "vassal"
VOLTE_CLAUSE_INACTIVE = "inactive"
VOLTE_CLAUSE_AT_WAR = "at_war"
VOLTE_CLAUSE_PUNITIVE = "punitive_record"
VOLTE_CLAUSE_REVANCHE = "sworn_revanche"
VOLTE_CLAUSE_NOT_BEATEN = "not_recently_beaten"
VOLTE_CLAUSE_NO_MARK = "defeat_does_not_show"
VOLTE_CLAUSE_NOT_COURTED = "not_courted"


def volte_face_window() -> int:
    """The window the predicate reads (V1 lever; False = the old 15)."""
    return int(VOLTE_FACE_WINDOW if THE_WINDOW_FITS_THE_COURTSHIP
               else VOLTE_FACE_WINDOW_BEFORE_IQ6)

PUNITIVE_MEMORY_TYPE = "punitive_settlement"
EMERGENT_DESIGN_TITLE = "Revanche"


# ═══════════════════ the durable punitive record ═════════════════════════

def record_punitive_cessions(world, cessions: Dict[str, List[Tuple[str, str]]]) -> List[Dict]:
    """Write durable `punitive_settlement` memories for every victim whose
    losses in ONE settlement meet the punitive bar. `cessions` maps
    victim -> ordered (province, receiver) pairs; the recorded author is
    the plurality receiver OF THE HOMELAND PROVINCES (deterministic
    tie-break: name order).

    ONLY the victim's own HOMELAND counts (`nation_starting_regions`):
    surrendering conquests back is the fortune of war, not a partition —
    Austria handing Prussian soil back to Prussia is beaten, not
    humiliated, and must stay volte-face-eligible. Tilsit stripped
    Prussia of PRUSSIAN land; that is the record this writes. The author
    is charged over the SAME filtered set (review fix: a settlement that
    hands the victim's conquests to one court and its homeland to
    another must blame the court that took the homeland — the record is
    durable and feeds the volte-face foreclosure forever).

    Called from all three ratify seams. Returns the records written."""
    from backend.game_logic.settlement_reactions import _add_settlement_memory
    written: List[Dict] = []
    for victim, pairs in cessions.items():
        if not victim or not pairs:
            continue
        homeland = set((getattr(world, "nation_starting_regions", {}) or {})
                       .get(victim, []) or [])
        homeland_pairs = [(p, r) for p, r in pairs if p in homeland]
        if not homeland_pairs:
            continue
        provinces = [p for p, _r in homeland_pairs]
        capital = world.get_nation_capital(victim)
        if (len(provinces) < PUNITIVE_SETTLEMENT_MIN_PROVINCES
                and capital not in provinces):
            continue
        receivers: Dict[str, int] = {}
        for _p, receiver in homeland_pairs:
            receivers[receiver] = receivers.get(receiver, 0) + 1
        author = max(sorted(receivers), key=lambda n: receivers[n])
        record = _add_settlement_memory(
            world,
            actor=author,
            subject=victim,
            memory_type=PUNITIVE_MEMORY_TYPE,
            episode_id=f"punitive:{victim}:{int(world.current_turn)}",
            payload={"provinces": [str(p) for p in provinces],
                     "author": author},
            expires_in=None,   # durable — a partition is not forgotten
        )
        if record:
            written.append(record)
    return written


def collect_cessions_from_clauses(clauses) -> Dict[str, List[Tuple[str, str]]]:
    """Aggregate applied territory clauses into the `record_punitive_cessions`
    shape — victim -> ordered (province, receiver) pairs, the first
    receiver winning a duplicated province. Tolerant of both clause
    dialects: `from`/`from_nation`, `to`/`to_nation`, `regions` list or
    singular `region`.

    `territory_return` is deliberately EXCLUDED — a return restores prior
    ownership by definition; nobody is partitioned by giving back what
    was taken."""
    out: Dict[str, List[Tuple[str, str]]] = {}
    for clause in clauses or []:
        if not isinstance(clause, dict):
            continue
        if clause.get("type") not in ("territory_cede", "territory"):
            continue
        victim = clause.get("from_nation") or clause.get("from")
        receiver = clause.get("to_nation") or clause.get("to")
        if not victim or not receiver or victim == receiver:
            continue
        names = list(clause.get("regions") or [])
        single = clause.get("region")
        if single and single not in names:
            names.append(single)
        if not names:
            continue
        pairs = out.setdefault(str(victim), [])
        seen = {p for p, _r in pairs}
        for name in names:
            if str(name) in seen:
                continue
            seen.add(str(name))
            pairs.append((str(name), str(receiver)))
    return out


# ═══════════════════ the promotion poll (AI-5b(i)) ═══════════════════════

def _lost_homeland(world, nation: str) -> List[str]:
    """Homeland provinces in foreign hands, authored order. Foreign =
    outside the nation's own vassal chain (the intent._holder_recently_
    beaten walk — soil held by one's own client is not lost)."""
    home = list((getattr(world, "nation_starting_regions", {}) or {})
                .get(nation, []) or [])
    lost: List[str] = []
    for region_name in home:
        region = world.regions.get(region_name)
        controller = getattr(region, "controller", None) if region else None
        if (controller and controller != nation
                and world._top_overlord(controller) != nation):
            lost.append(region_name)
    return lost


def _has_emergent_design(world, nation: str) -> bool:
    deck = (getattr(world, "agendas", {}) or {}).get(nation) or []
    return any(entry.get("emergent") for entry in deck
               if isinstance(entry, dict))


def _grievance_author(world, nation: str, lost: List[str]) -> Tuple[Optional[str], bool]:
    """(author, record_backed): who the grievance is charged to, and
    whether a DURABLE record (punitive memory / renege grievance against
    a holder) backs it — the arm that lowers the derived bar to one
    province. Priority: the latest punitive memory's author; else a
    renege-marked holder of lost soil; else the capital's holder; else
    the plurality holder."""
    from backend.game_logic.instruments import has_renege_grievance
    from backend.game_logic.settlement_reactions import get_settlement_memories

    punitive = get_settlement_memories(
        world, subject=nation, memory_type=PUNITIVE_MEMORY_TYPE)
    if punitive:
        latest = max(punitive, key=lambda r: int(r.get("turn", 0) or 0))
        return str(latest.get("actor") or ""), True

    holders: Dict[str, int] = {}
    for region_name in lost:
        region = world.regions.get(region_name)
        controller = getattr(region, "controller", None) if region else None
        if not controller:
            continue
        effective = world._top_overlord(controller) or controller
        holders[effective] = holders.get(effective, 0) + 1
    for holder in sorted(holders):
        if has_renege_grievance(world, nation, holder):
            return holder, True

    capital = world.get_nation_capital(nation)
    if capital in lost:
        region = world.regions.get(capital)
        controller = getattr(region, "controller", None) if region else None
        if controller:
            return world._top_overlord(controller) or controller, False
    if holders:
        return max(sorted(holders), key=lambda n: holders[n]), False
    return None, False


def process_emergent_designs(world) -> List[Dict]:
    """The once-per-turn promotion poll (sited between process_formations
    and process_agenda_shifts, so a same-tick activation announces on the
    existing shift beat). Europe-scoped like the war council — the bare
    suite world and the legacy fixture world are byte-identical."""
    if getattr(world, "sovereign_map", "legacy") != "europe":
        return []
    player = getattr(world, "player_nation", "France")
    vassals = getattr(world, "vassals", {}) or {}

    events: List[Dict] = []
    for nation in sorted(world.get_active_nations()):
        if nation == player or nation in vassals:
            continue
        if _has_emergent_design(world, nation):
            continue
        lost = _lost_homeland(world, nation)
        if not lost:
            continue
        author, record_backed = _grievance_author(world, nation, lost)
        capital = world.get_nation_capital(nation)
        partitioned = (capital in lost
                       or len(lost) >= EMERGENT_DESIGN_MIN_LOST)
        if not partitioned and not record_backed:
            continue
        if not author or author == nation:
            continue

        deck = (getattr(world, "agendas", None))
        if deck is None:
            world.agendas = {}
            deck = world.agendas
        entries = deck.setdefault(nation, [])
        design_id = f"revanche_{nation.lower()}"
        if any(str(e.get("id") or "") == design_id for e in entries
               if isinstance(e, dict)):
            continue  # authored-id collision — the scenario owns the name

        first = lost[0]
        blurb = (f"What was taken shall be retaken. The court has not "
                 f"forgiven the loss of {first}"
                 + (f" and {len(lost) - 1} more" if len(lost) > 1 else "")
                 + ".")
        entry = {
            "id": design_id,
            "type": "acquire_regions",
            "title": EMERGENT_DESIGN_TITLE,
            "blurb": blurb,
            "regions": list(lost),
            "emergent": True,
            "author": author,
            "promoted_turn": int(world.current_turn),
        }
        # Constraint (b): FRONT-insert — first-predicate-wins would leave
        # an appended entry dead behind any still-active authored design.
        entries.insert(0, entry)
        # The deck changed activation geometry mid-tick.
        world.invalidate_bloc_members_cache()

        from backend.game_logic.agendas import _live_nation_name
        nation_display = _live_nation_name(world, nation)
        author_display = _live_nation_name(world, author)
        # PT-G5(e): `EMERGENT_DESIGN_MIN_LOST = 2`, so the commonest case
        # is exactly one other province — and this rendered "Bohemia and 1
        # more provinces", in a MODAL.
        _others = len(lost) - 1
        province_line = (first + (
            f" and {_others} more province{'s' if _others != 1 else ''}"
            if _others > 0 else ""))
        event = {
            "type": "design_promoted",
            "nation": nation,
            "author": author,
            "design_id": design_id,
            "regions": list(lost),
            "message": (f"{nation_display} swears revanche — the court "
                        f"will not forgive {author_display} the loss of "
                        f"{province_line}."),
        }
        world.log_event(dict(event))
        events.append(event)
        from backend.game_logic.dispatch import queue_dispatch_event
        queue_dispatch_event(world, "design_promoted", {
            "nation": nation_display,
            "author": author_display,
            "province_line": province_line,
        }, "always")   # a court's design is public — diplomacy has no fog
    return events


# ═══════════════════ the volte-face (AI-5b(ii)) ══════════════════════════

def _war_end_turns(world, power: str, other: str):
    """Yield the end turn of every war containing `power` and `other` on
    OPPOSITE sides — the get_agenda_grudge_nations per-nation end read
    (exited_turn, else instance ended_turn). Live instances first, then
    `archived_war_instances` (instance retention 10 covers the read up
    to the grudge horizon; the archive extends it beyond).

    IQ-6 V1b (`THE_SEPARATE_PEACE_ENDS_THE_WAR`): the PAIR's own
    resolution turn answers first — a separate peace ends the war with
    the hegemon even while the court fights the hegemon's allies."""
    pair_key = world._make_diplo_key(power, other)

    def _scan(instances):
        for instance in instances:
            if not isinstance(instance, dict):
                continue
            meta = instance.get("participant_meta") or {}
            side_by = instance.get("side_by_nation") or {}

            def _side_of(n: str) -> Optional[str]:
                record = meta.get(n)
                if isinstance(record, dict) and record.get("side"):
                    return record.get("side")
                return side_by.get(n)

            power_side = _side_of(power)
            other_side = _side_of(other)
            if not power_side or not other_side or power_side == other_side:
                continue
            if THE_SEPARATE_PEACE_ENDS_THE_WAR:
                pair_meta = (instance.get("diplo_key_meta") or {}).get(pair_key)
                resolved = (pair_meta.get("resolved_turn")
                            if isinstance(pair_meta, dict)
                            and pair_meta.get("pair_status") == "resolved"
                            else None)
                if resolved is not None:
                    yield int(resolved)
                    continue
            end = (meta.get(power) or {}).get("exited_turn")
            if end is None:
                end = instance.get("ended_turn")
            if end is None:
                continue
            yield int(end)

    yield from _scan((getattr(world, "war_instances", {}) or {}).values())
    yield from _scan(getattr(world, "archived_war_instances", []) or [])


def _war_with_ended_recently(world, power: str, other: str,
                             window: int) -> bool:
    """Did a war containing `power` and `other` on OPPOSITE sides end for
    `power` within `window` turns? (Short-circuits in the old scan order:
    the first qualifying end turn answers.)"""
    turn = int(getattr(world, "current_turn", 0))
    return any(turn - end < window
               for end in _war_end_turns(world, power, other))


def _latest_war_end_turn(world, power: str, other: str) -> Optional[int]:
    """The most recent end turn of a war between the two on opposite
    sides, or None — the turn the volte-face window is counted from."""
    ends = list(_war_end_turns(world, power, other))
    return max(ends) if ends else None


def _next_design_after_contain(world, power: str) -> Optional[Dict]:
    """The deck entry the reversed power would advance to once its
    contain design goes dormant inside the hegemon's bloc — the object
    the volte-face aims it at (§12.2: gulf_and_straits)."""
    deck = (getattr(world, "agendas", {}) or {}).get(power) or []
    seen_contain = False
    for entry in deck:
        if not isinstance(entry, dict):
            continue
        if entry.get("type") == "contain_hegemon":
            seen_contain = True
            continue
        if seen_contain:
            return entry
    return None


def volte_face_failing_clauses(world, power: str, hegemon: str, *,
                               exhaustive: bool = False) -> List[str]:
    """§3.6-4 eligibility, reported clause by clause — the SINGLE source
    `volte_face_receptive`, the counsel and the war room all read (IQ-6
    V4). Returns the failing clause names in evaluation order; an empty
    list means receptive. By default it stops at the first failure,
    making exactly the reads the pre-IQ-6 predicate made in the same
    order, so the boolean is byte-identical; `exhaustive=True` keeps
    reading past a failure (the identity clause always answers alone —
    nothing after it means anything).

    Every clause is a per-turn reading of serialized state — nothing
    here latches:

    - major tier, active, not a vassal, not the player, at peace with
      the hegemon;
    - NOT HUMILIATED: no punitive_settlement memory authored by the
      hegemon (durable — a partition forecloses this path forever) and
      no emergent revanche charged to the hegemon;
    - BEATEN: its war with the hegemon ended within `volte_face_window()`
      turns, and the defeat still shows — homeland soil in the hegemon's
      bloc's hands (IQ-6 V3; lever down: war exhaustion at or above
      VOLTE_FACE_WE_MARK OR that soil);
    - COURTED: relations at or above the ALLIANCE ratify floor — the
      courting is real, and the offer this predicate gates can actually
      be signed.
    """
    if power == hegemon:
        return [VOLTE_CLAUSE_IDENTITY]
    player = getattr(world, "player_nation", "France")
    if power == player:
        return [VOLTE_CLAUSE_IDENTITY]
    failing: List[str] = []

    def _fails(clause: str) -> bool:
        """Record a failure; True when the caller should stop reading."""
        failing.append(clause)
        return not exhaustive

    if world.get_power_tier(power) != "major":
        if _fails(VOLTE_CLAUSE_TIER):
            return failing
    if power in (getattr(world, "vassals", {}) or {}):
        if _fails(VOLTE_CLAUSE_VASSAL):
            return failing
    if power not in world.get_active_nations():
        if _fails(VOLTE_CLAUSE_INACTIVE):
            return failing
    if world.get_diplomatic_state(power, hegemon) in ("WAR", "ARMISTICE"):
        if _fails(VOLTE_CLAUSE_AT_WAR):
            return failing

    # NOT humiliated — generosity is the whole doctrine.
    from backend.game_logic.settlement_reactions import get_settlement_memories
    if get_settlement_memories(world, actor=hegemon, subject=power,
                               memory_type=PUNITIVE_MEMORY_TYPE):
        if _fails(VOLTE_CLAUSE_PUNITIVE):
            return failing
    for entry in (getattr(world, "agendas", {}) or {}).get(power) or []:
        if (isinstance(entry, dict) and entry.get("emergent")
                and entry.get("author") == hegemon):
            if _fails(VOLTE_CLAUSE_REVANCHE):
                return failing
            break

    # BEATEN, recently, by this hegemon.
    if not _war_with_ended_recently(world, power, hegemon,
                                    volte_face_window()):
        if _fails(VOLTE_CLAUSE_NOT_BEATEN):
            return failing
    hegemon_bloc = set(world.get_bloc_members(hegemon))
    if THE_DEFEAT_IS_THE_SOIL:
        # V3: the mark is the map. The exhaustion arm is retired (the
        # constant block above says why).
        marked = any(
            (lambda c: c and (world._top_overlord(c) or c) in hegemon_bloc)(
                getattr(world.regions.get(r), "controller", None))
            for r in _lost_homeland(world, power))
    else:
        exhausted = int((getattr(world, "war_exhaustion", {}) or {})
                        .get(power, 0) or 0) >= VOLTE_FACE_WE_MARK
        soil_marked = any(
            (lambda c: c and (world._top_overlord(c) or c) in hegemon_bloc)(
                getattr(world.regions.get(r), "controller", None))
            for r in _lost_homeland(world, power))
        marked = exhausted or soil_marked
    if not marked:
        if _fails(VOLTE_CLAUSE_NO_MARK):
            return failing

    # COURTED.
    relation = int(world.nation_relations.get(
        world._make_diplo_key(power, hegemon), 0) or 0)
    if relation < VOLTE_FACE_RELATION_FLOOR:
        _fails(VOLTE_CLAUSE_NOT_COURTED)
    return failing


def volte_face_receptive(world, power: str, hegemon: str) -> bool:
    """§3.6-4 eligibility: a GREAT POWER, beaten by the hegemon and then
    courted rather than humiliated, will reverse. The clauses live in
    `volte_face_failing_clauses` (the single source); receptive means
    none fails."""
    return not volte_face_failing_clauses(world, power, hegemon)


def volte_face_courtship(world, power: str, hegemon: str) -> Optional[Dict]:
    """IQ-6 V4 — the open door. None unless `VOLTE_FACE_SPEAKS_ITS_MIND`
    and every clause but COURTED holds; otherwise the figures the counsel
    and the war room print (all ints, GR2; display only, GR6):

    - `relation` / `floor`: where the pair stands, and the courted floor;
    - `last_signing_turn`: the last turn an alliance signing still reads
      the war as recent (`end + window - 1`);
    - `turns_left`: the courting turns that can still count. The court's
      own letter is written in the diplomatic phase, which runs BEFORE
      the turn advances, and is answered the next turn — so the relation
      must stand at the floor by the phase of `last_signing_turn - 1`,
      and a mission started now ticks at the end of this turn onward:
      `end + window - 2 - current_turn`.
    """
    if not VOLTE_FACE_SPEAKS_ITS_MIND:
        return None
    if volte_face_failing_clauses(world, power, hegemon) != [
            VOLTE_CLAUSE_NOT_COURTED]:
        return None
    end = _latest_war_end_turn(world, power, hegemon)
    if end is None:     # unreachable — the BEATEN clause held
        return None
    window = volte_face_window()
    turn = int(getattr(world, "current_turn", 0))
    relation = int(world.nation_relations.get(
        world._make_diplo_key(power, hegemon), 0) or 0)
    return {
        "nation": power,
        "hegemon": hegemon,
        "relation": relation,
        "floor": int(VOLTE_FACE_RELATION_FLOOR),
        "war_ended_turn": int(end),
        "window": int(window),
        "last_signing_turn": int(end + window - 1),
        "turns_left": int(max(0, end + window - 2 - turn)),
    }


def _turns(n: int) -> str:
    # LV-9 (row EP F2): the one plural source.
    from backend.display_names import plural
    return plural(n, "turn")


def volte_face_counsel_line(world, power: str, hegemon: str) -> str:
    """The one sentence both surfaces print when the door is open — or ""
    (lever down, or any clause but COURTED failing). The forecast is the
    mission counsel's own relation-step arithmetic
    (`diplomacy.forecast_relation_to`: the skill-scaled Improve Relations
    effect, the clamp, the drift step), a quiet-world FORECAST — so "≈"."""
    view = volte_face_courtship(world, power, hegemon)
    if view is None:
        return ""
    from backend.game_logic.agendas import _live_nation_name
    from backend.game_logic.diplomacy import forecast_relation_to
    name = _live_nation_name(world, power)
    relation, floor, left = view["relation"], view["floor"], view["turns_left"]
    road = forecast_relation_to(world, power, floor, "IMPROVE_RELATIONS")
    if left <= 0:
        return (f"{name} was beaten, not broken — but her door closes before "
                f"our courting could carry relations from {relation:+d} to "
                f"{floor}.")
    if road is not None and road[0] <= left:
        return (f"{name} was beaten, not broken — court her to {floor} within "
                f"{_turns(left)} and she may take our hand. Relations stand "
                f"at {relation:+d}; Improve Relations would carry them there "
                f"in ≈{_turns(road[0])}.")
    return (f"{name} was beaten, not broken — but relations stand at "
            f"{relation:+d}, and even Improve Relations would not carry them "
            f"to {floor} in the {_turns(left)} before her door closes.")


def maybe_fire_volte_face(world, nation_a: str, nation_b: str) -> Optional[Dict]:
    """Beat 5 — THE VOLTE-FACE (§4.6a). Called at the alliance-ratify
    chokepoint after an ALLIANCE state lands between two nations. Fires
    when either party was `volte_face_receptive` toward the other at the
    signing: the beaten court has reversed. The deck-advance is already
    done by the state change itself (in-bloc containment goes dormant);
    this hook only ANNOUNCES it — campaign log + HIGH dispatch, naming
    the design the reversed power turns to."""
    pair = None
    for power, hegemon in ((nation_a, nation_b), (nation_b, nation_a)):
        if volte_face_receptive(world, power, hegemon):
            pair = (power, hegemon)
            break
    if pair is None:
        return None
    power, hegemon = pair

    from backend.game_logic.agendas import _live_nation_name
    power_display = _live_nation_name(world, power)
    hegemon_display = _live_nation_name(world, hegemon)
    next_design = _next_design_after_contain(world, power)
    next_title = str((next_design or {}).get("title") or "")
    if next_title:
        gaze = f"Her court turns its gaze to {next_title}."
    else:
        gaze = "Her court looks abroad for a new design."
    event = {
        "type": "volte_face",
        "nation": power,
        "partner": hegemon,
        "next_design": str((next_design or {}).get("id") or ""),
        "message": (f"THE VOLTE-FACE: {power_display}, beaten and then "
                    f"courted, takes {hegemon_display}'s hand. {gaze}"),
    }
    world.log_event(dict(event))
    from backend.game_logic.dispatch import queue_dispatch_event
    queue_dispatch_event(world, "volte_face", {
        "nation": power_display,
        "partner": hegemon_display,
        "gaze": gaze,
    }, "always")
    return event
