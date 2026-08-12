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
VOLTE_FACE_WINDOW = 15
# Courted = relations at or above the ALLIANCE ratify requirement — the
# courier never offers what the treaty gate would refuse (honest
# availability; STATE_RELATION_REQUIREMENTS["ALLIANCE"] is 40).
VOLTE_FACE_RELATION_FLOOR = 40
# The wrecked-army mark: war exhaustion still visibly bleeding off after
# a lost war (a generous white peace leaves no soil mark — Friedland's
# mark on Russia was the army, not the map).
VOLTE_FACE_WE_MARK = 40

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

def _war_with_ended_recently(world, power: str, other: str,
                             window: int) -> bool:
    """Did a war containing `power` and `other` on OPPOSITE sides end for
    `power` within `window` turns? The get_agenda_grudge_nations per-
    nation end read (exited_turn, else instance ended_turn); instance
    retention 10 covers the read up to the grudge horizon and
    `archived_war_instances` extends it beyond."""
    turn = int(getattr(world, "current_turn", 0))

    def _scan(instances) -> bool:
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
            end = (meta.get(power) or {}).get("exited_turn")
            if end is None:
                end = instance.get("ended_turn")
            if end is None:
                continue
            if turn - int(end) < window:
                return True
        return False

    if _scan((getattr(world, "war_instances", {}) or {}).values()):
        return True
    return _scan(getattr(world, "archived_war_instances", []) or [])


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


def volte_face_receptive(world, power: str, hegemon: str) -> bool:
    """§3.6-4 eligibility: a GREAT POWER, beaten by the hegemon and then
    courted rather than humiliated, will reverse. All five clauses are
    per-turn readings of serialized state — nothing here latches:

    - major tier, active, not a vassal, not the player, at peace with
      the hegemon;
    - BEATEN: its war with the hegemon ended within VOLTE_FACE_WINDOW
      turns, and the defeat still shows — war exhaustion at or above
      VOLTE_FACE_WE_MARK, or homeland soil in the hegemon's bloc's hands;
    - NOT HUMILIATED: no punitive_settlement memory authored by the
      hegemon (durable — a partition forecloses this path forever) and
      no emergent revanche charged to the hegemon;
    - COURTED: relations at or above the ALLIANCE ratify floor — the
      courting is real, and the offer this predicate gates can actually
      be signed.
    """
    if power == hegemon:
        return False
    player = getattr(world, "player_nation", "France")
    if power == player:
        return False
    if world.get_power_tier(power) != "major":
        return False
    if power in (getattr(world, "vassals", {}) or {}):
        return False
    if power not in world.get_active_nations():
        return False
    if world.get_diplomatic_state(power, hegemon) in ("WAR", "ARMISTICE"):
        return False

    # NOT humiliated — generosity is the whole doctrine.
    from backend.game_logic.settlement_reactions import get_settlement_memories
    if get_settlement_memories(world, actor=hegemon, subject=power,
                               memory_type=PUNITIVE_MEMORY_TYPE):
        return False
    for entry in (getattr(world, "agendas", {}) or {}).get(power) or []:
        if (isinstance(entry, dict) and entry.get("emergent")
                and entry.get("author") == hegemon):
            return False

    # BEATEN, recently, by this hegemon.
    if not _war_with_ended_recently(world, power, hegemon,
                                    VOLTE_FACE_WINDOW):
        return False
    exhausted = int((getattr(world, "war_exhaustion", {}) or {})
                    .get(power, 0) or 0) >= VOLTE_FACE_WE_MARK
    hegemon_bloc = set(world.get_bloc_members(hegemon))
    soil_marked = any(
        (lambda c: c and (world._top_overlord(c) or c) in hegemon_bloc)(
            getattr(world.regions.get(r), "controller", None))
        for r in _lost_homeland(world, power))
    if not exhausted and not soil_marked:
        return False

    # COURTED.
    relation = int(world.nation_relations.get(
        world._make_diplo_key(power, hegemon), 0) or 0)
    return relation >= VOLTE_FACE_RELATION_FLOOR


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
