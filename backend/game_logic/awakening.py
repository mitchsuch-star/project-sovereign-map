"""The Awakening — DY-4 (Tier 6; `docs/DYNAMISM_SPEC.md` §5, the Tier-6 gate
record §5a ruled November 10, 2026 in Plan Mode at session C's head under the
user's delegation — "rule yourself be rigorous make it good").

The era's own force, and the game's answer to "rising nationalism": a
PER-COURT scalar 0–100 (Q2), regional expression DERIVED — no per-region
store, no pop. The ulcer (Spain, 1808–) bleeds every occupier, the player's
house included (Q3). Four pieces, one module:

* THE STORE — `world.moments["awakening"]` (the T5 precedent; `WorldState.
  to_dict` carries no new field): `{"block": {stirring, risen}, "houses":
  {client: boot lord}, "courts": {court: {"level", "occupied"}}}`. Armed by
  the scenario's top-level `awakening` block (`{"stirring": 40, "risen":
  70}` — the two thresholds the letters and the teeth read, validator-
  clamped; a hotter or colder era is a mod's dial); the bare flag world,
  the tutorials and the legacy rollback author none and write nothing.
* THE RAISES AND COOLS — every court of the boot roster carries the scalar,
  ELIMINATED ONES INCLUDED (a people outlives its court — Poland; the
  Kingdom of Italy's soil under Austria stirs) and the player's house.
  The occupied-home count is DERIVED once a turn (§5a C1: fifteen writers
  set `region.controller` outside the capture chokepoint, so a maintained
  counter would drift on the first treaty) — the court's boot homeland
  (`nation_starting_regions`) against the holders' HOUSES (`_top_overlord`),
  O(Σ homeland) a turn, never a region scan (Rule 8). "Foreign-held": the
  holder's live house is outside the court's HOME houses — the court itself
  and its BOOT lord while the court is still that lord's client or has been
  erased (§5a C2 — a boot client's soil under its lord is home; the Kingdom
  of Italy's under France is home; Spain's under France is occupied, and so
  is a court's SUBJUGATED later: its new lord's holdings are foreign — Spain
  under Joseph, Austria under the Emperor's Pressburg). The tick adds
  by band (N-DY4: 1–2 occupied +1, 3–5 +2, 6+ +3), cools −1 with none
  occupied, −10 the lump when home rule returns (every road: the last
  province back by arms or by treaty, a client's autonomy raised, a client
  released or free by rebellion). Event writes at their ONE sites: a
  dictated peace (`emergent_designs.record_punitive_cessions`, +15 scaled
  by the court's DERIVED rank — major 15 / secondary 10 / minor 5), the
  sovereign captured (`WorldState.capture_marshal`, +10 — Bayonne), a
  client squeezed (`vassal.change_vassal_autonomy` down, +5).
* THE BEATS — ONE `awakening` log row per phase crossing (`phase` quiet /
  stirring / risen; DY-0's `awakening_events` column reads the prefix; the
  log census 183 → 184) and a HIGH dispatch line in the courts' register.
* THE ULCER — `_supply_multiplier`'s read (`ulcer_factor`): an occupier's
  cap ×0.75 on soil whose boot owner stands at `risen`; the boot owner's
  own army never bleeds, nobody bleeds on home-held soil, an ally beside
  the occupier bleeds too. Shown = applied (`get_effective_supply_cap`).
* THE LETTERS — the two predicates the affairs engine reads (`people_stir`,
  `people_risen`: the most-occupied ACTIVE court at the threshold whose
  homeland the lord's house holds; the display slots assume a court, so an
  erased court's people act through the ulcer and the beat alone) and the
  `awakening` op the letters' Accept carries (`moments.OPS`, in words).

Three seams, each zero-arg (`tests/_t3_seams.py` rows T6-STIR, T6-ULCER,
T6-LETTERS): `the_people_stir` (the store's raises, cools and beats; down:
the scalar never moves, no beat), `the_ulcer_bleeds` (down: 1.0),
`the_people_write` (row DY-4's letters — `affairs.row_armed`; down: the
templates held out of the deck whole).
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

STORE_KEY = "awakening"
LOG_TYPE = "awakening"
AWAKE_STIRRING_DEFAULT = 40          # N-DY4: the letters' first threshold
AWAKE_RISEN_DEFAULT = 70             # N-DY4: the ulcer's threshold
THRESHOLD_BOUNDS = (1, 99)
LEVEL_MAX = 100
# (at least N home provinces foreign-held, the raise a turn) — read highest first
OCCUPIED_BANDS: Tuple[Tuple[int, int], ...] = ((6, 3), (3, 2), (1, 1))
DICTATED_PEACE_RAISE = {"major": 15, "secondary": 10, "minor": 5}   # by the court's derived rank
SOVEREIGN_CAPTURED_RAISE = 10
CLIENT_SQUEEZED_RAISE = 5
QUIET_COOL = 1                       # a turn with no home province foreign-held
HOME_RULE_LUMP = 10                  # home rule restored, every road
ULCER_SUPPLY_FACTOR = 0.75
PHASES = ("quiet", "stirring", "risen")
_RANK_DEFAULT = "secondary"


# ═══════════════════════════════════════════════════════════════════════
# The seams
# ═══════════════════════════════════════════════════════════════════════

def the_people_stir() -> bool:
    """T6-STIR seam: the scalar moves — the tick's bands and cools, the
    event writes, the beats. Down: the pre-Tier-6 world — the store loads
    and saves, nothing is written to it and no beat is logged."""
    return True


def the_ulcer_bleeds() -> bool:
    """T6-ULCER seam: an occupier's supply cap bleeds on risen soil. Down:
    the multiplier reads 1.0 everywhere."""
    return True


def the_people_write() -> bool:
    """T6-LETTERS seam (row DY-4 of `affairs.SINCE_ROWS`): the Awakening's
    letters sit in the deck and their predicates read. Down: the templates
    are held out whole and the predicates never hold."""
    return True


# ═══════════════════════════════════════════════════════════════════════
# The store — inside `world.moments` (the Questions' precedent)
# ═══════════════════════════════════════════════════════════════════════

def _int_or(value: Any, default: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        return int(default)
    return int(value)


def clean_block(raw: Any) -> Optional[Dict[str, int]]:
    """The authored block, coerced: an object (empty allowed — the code
    defaults) with `stirring` and `risen` clamped to the bounds and ordered;
    None when the scenario authors none (not a dict). The validator refuses
    a malformed file — this is the reader's own tolerance."""
    if not isinstance(raw, dict):
        return None
    lo, hi = THRESHOLD_BOUNDS
    stirring = max(lo, min(hi, _int_or(raw.get("stirring"), AWAKE_STIRRING_DEFAULT)))
    risen = max(lo, min(hi, _int_or(raw.get("risen"), AWAKE_RISEN_DEFAULT)))
    if stirring >= risen:
        stirring, risen = AWAKE_STIRRING_DEFAULT, AWAKE_RISEN_DEFAULT
    return {"stirring": int(stirring), "risen": int(risen)}


def _clean_courts(raw: Any) -> Dict[str, Dict[str, int]]:
    out: Dict[str, Dict[str, int]] = {}
    for court, row in (raw.items() if isinstance(raw, dict) else []):
        if not isinstance(row, dict):
            continue
        level = max(0, min(LEVEL_MAX, _int_or(row.get("level"), 0)))
        occupied = max(0, _int_or(row.get("occupied"), 0))
        if level or occupied:
            out[str(court)] = {"level": level, "occupied": occupied}
    return out


def _clean_houses(raw: Any) -> Dict[str, str]:
    return {str(k): str(v)[:64] for k, v in (raw.items() if isinstance(raw, dict) else [])
            if isinstance(v, str) and v}


def clean_store(raw: Any) -> Dict[str, Any]:
    """The serialized store, coerced: `block`, `houses`, `courts`."""
    if not isinstance(raw, dict):
        return {}
    block = clean_block(raw.get("block"))
    if block is None:
        return {}
    out: Dict[str, Any] = {"block": block, "courts": _clean_courts(raw.get("courts"))}
    if "houses" in raw:
        out["houses"] = _clean_houses(raw.get("houses"))
    return out


def _boot_houses_from_data(data: Dict[str, Any]) -> Dict[str, str]:
    """{client: its top overlord} off the raw `vassals` dict of a scenario or
    save (read at install, before `from_dict` loads the live web — the boot
    web is what the people remember: a client's soil under its lord is home)."""
    vassals = (data or {}).get("vassals")
    if not isinstance(vassals, dict):
        return {}
    out: Dict[str, str] = {}
    for client in vassals:
        seen = {str(client)}
        current = str(client)
        while True:
            row = vassals.get(current)
            lord = str((row or {}).get("lord") or "") if isinstance(row, dict) else ""
            if not lord or lord in seen:
                break
            seen.add(lord)
            current = lord
        if current != str(client):
            out[str(client)] = current
    return out


def install(world, data: Dict[str, Any]) -> None:
    """`WorldState.from_dict`, beside the moments line: a scenario's
    top-level `awakening` key arms the store (the boot web snapshotted from
    the raw `vassals`); a save's `moments.awakening` is the store, carried
    whole. Writes NOTHING on a world that authors none — the bare flag
    world, the tutorials and the legacy rollback keep `moments` byte-
    identical."""
    data = data or {}
    moments = data.get("moments")
    saved = moments.get(STORE_KEY) if isinstance(moments, dict) else None
    store = clean_store(saved)
    if not store:
        block = clean_block(data.get(STORE_KEY))
        if block is None:
            return
        store = {"block": block, "courts": {}}
        houses = _boot_houses_from_data(data)
        if houses:
            store["houses"] = houses
        # else: the Europe boot seeds its web in `__init__` and the file
        # carries no `vassals` key — `ensure_houses` snapshots the live web
        # at the end of `from_dict`, once the vassals are final.
    _moments(world)[STORE_KEY] = store


def ensure_houses(world) -> Dict[str, str]:
    """The boot web, snapshotted ONCE from the live `world.vassals` where
    the store carries none yet (the end of `from_dict`; a hand-built test
    world on its first read). A save carries it from then on."""
    st = store(world)
    if not st:
        return {}
    houses = st.get("houses")
    if isinstance(houses, dict):
        return houses
    snapshot = {str(c): str(world._top_overlord(c) or c)
                for c in (getattr(world, "vassals", {}) or {})}
    st["houses"] = {c: lord for c, lord in snapshot.items() if lord != c}
    return st["houses"]


def backfill(world, scenario_data: Dict[str, Any]) -> bool:
    """A pre-Tier-6 save of a scenario that NOW authors the Awakening gains
    the store on load (the `_backfill_moments` idiom): every people at 0,
    the save's own web as the boot web — nothing retroactive; a save
    carrying a store is never overwritten."""
    if armed(world):
        return False
    block = clean_block((scenario_data or {}).get(STORE_KEY))
    if block is None:
        return False
    houses = {str(c): str(world._top_overlord(c) or c)
              for c in (getattr(world, "vassals", {}) or {})}
    houses = {c: lord for c, lord in houses.items() if lord != c}
    _moments(world)[STORE_KEY] = {"block": block, "houses": houses, "courts": {}}
    return True


def _moments(world) -> Dict[str, Any]:
    store = getattr(world, "moments", None)
    if not isinstance(store, dict):
        store = {}
        world.moments = store
    return store


def store(world) -> Dict[str, Any]:
    """The store, read-only ({} when the scenario authors none)."""
    value = (getattr(world, "moments", None) or {})
    value = value.get(STORE_KEY) if isinstance(value, dict) else None
    return value if isinstance(value, dict) else {}


def armed(world) -> bool:
    return isinstance(store(world).get("block"), dict)


def stirring(world) -> int:
    return _int_or((store(world).get("block") or {}).get("stirring"), AWAKE_STIRRING_DEFAULT)


def risen(world) -> int:
    return _int_or((store(world).get("block") or {}).get("risen"), AWAKE_RISEN_DEFAULT)


def level(world, court: str) -> int:
    row = (store(world).get("courts") or {}).get(str(court))
    return _int_or((row or {}).get("level"), 0) if isinstance(row, dict) else 0


def occupied(world, court: str) -> int:
    """The last tick's derived count (the save's figure, never a scan)."""
    row = (store(world).get("courts") or {}).get(str(court))
    return _int_or((row or {}).get("occupied"), 0) if isinstance(row, dict) else 0


def phase_of(world, value: int) -> str:
    if int(value) >= risen(world):
        return "risen"
    if int(value) >= stirring(world):
        return "stirring"
    return "quiet"


def phase(world, court: str) -> str:
    return phase_of(world, level(world, court))


def awakened(world) -> Dict[str, int]:
    """{court: level} for every court with a nonzero level, sorted."""
    courts = store(world).get("courts") or {}
    return {c: int(r.get("level", 0) or 0) for c, r in sorted(courts.items())
            if isinstance(r, dict) and int(r.get("level", 0) or 0) > 0}


# ═══════════════════════════════════════════════════════════════════════
# The reads — houses, the homeland, the derived occupied count
# ═══════════════════════════════════════════════════════════════════════

def _turn(world) -> int:
    return int(getattr(world, "current_turn", 0) or 0)


def live_house(world, nation: str) -> str:
    """A court's top overlord today (the Alarm's and the Questions' read)."""
    if not nation:
        return ""
    return str(world._top_overlord(nation) or nation)


def boot_house(world, court: str) -> str:
    """The court's house AT BOOT — its lord then, else itself. A people
    remembers the web it was born into: the Kingdom of Italy's soil under
    France is home though the court was erased; Spain's under France is
    occupied though Spain marched beside France in 1805."""
    houses = ensure_houses(world)
    return str(houses.get(str(court)) or court)


def boot_courts(world) -> List[str]:
    """Every court of the boot roster, eliminated ones included (sorted)."""
    return sorted(str(c) for c in (getattr(world, "nation_starting_regions", {}) or {}))


def homeland(world, court: str) -> List[str]:
    return [str(r) for r in ((getattr(world, "nation_starting_regions", {}) or {})
                             .get(str(court)) or [])]


def home_houses(world, court: str) -> set:
    """§5a C2 — the houses whose garrisons are HOME on `court`'s soil: the
    court itself, and its BOOT lord while the court is still (or again) that
    lord's client or has been erased (a people remembers the web it was born
    into — the Kingdom of Italy's soil under France is home though the court
    fell; Holland's under France is home while Holland is France's). A court
    SUBJUGATED later keeps its boot house, so its new lord's holdings are
    foreign — Spain under Joseph, Austria under the Emperor's Pressburg: the
    people rise against the garrisons of the lord that was imposed on them
    (DY-5's client dial reads the same scalar). A client that broke free
    reads its old lord's holdings as foreign from then on."""
    homes = {str(court)}
    boot = boot_house(world, court)
    if boot != court:
        standing = court in set(world.get_active_nations())
        if not standing or live_house(world, court) == boot:
            homes.add(boot)
    return homes


def _foreign(world, court: str, region_name: str, homes: set) -> bool:
    region = (getattr(world, "regions", {}) or {}).get(str(region_name))
    holder = str(getattr(region, "controller", "") or "") if region is not None else ""
    if not holder or holder == court:
        return False
    return live_house(world, holder) not in homes


def is_foreign_held(world, court: str, region_name: str) -> bool:
    """§5a C2: the holder's live house is outside the court's home houses
    (`home_houses`); an empty controller is nobody's garrison."""
    return _foreign(world, court, region_name, home_houses(world, court))


def occupied_count(world, court: str) -> int:
    """The derived count: the court's boot homeland foreign-held today —
    O(homeland), the regions touched by name, never a scan."""
    homes = home_houses(world, court)
    return sum(1 for name in homeland(world, court) if _foreign(world, court, name, homes))


def held_by_house(world, court: str, house: str) -> int:
    """How many of `court`'s homeland provinces `house` (a live house) holds
    as a FOREIGN holder — 0 where that house is home on the court's soil."""
    homes = home_houses(world, court)
    if house in homes:
        return 0
    regions = getattr(world, "regions", {}) or {}
    n = 0
    for name in homeland(world, court):
        region = regions.get(name)
        holder = str(getattr(region, "controller", "") or "") if region is not None else ""
        if holder and holder != court and live_house(world, holder) == house:
            n += 1
    return n


def band_raise(count: int) -> int:
    for at_least, raise_by in OCCUPIED_BANDS:
        if int(count) >= at_least:
            return int(raise_by)
    return 0


def dictated_peace_raise(world, court: str) -> int:
    rank = str(world.get_power_tier(court) or _RANK_DEFAULT)
    return int(DICTATED_PEACE_RAISE.get(rank, DICTATED_PEACE_RAISE[_RANK_DEFAULT]))


# ═══════════════════════════════════════════════════════════════════════
# The ONE writer — every change of the scalar, the beat on a crossing
# ═══════════════════════════════════════════════════════════════════════

def move(world, court: str, delta: int, cause: str,
         occupied_now: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """Move `court`'s level by `delta` (clamped 0–100), record the derived
    count when the tick passes it, and log the beat when a phase is
    crossed. Returns the beat's event, or None. Nothing is written with the
    seam down or on an unarmed world."""
    if not the_people_stir() or not armed(world) or not court:
        return None
    st = store(world)
    courts = st.setdefault("courts", {})
    row = courts.get(str(court))
    before = _int_or((row or {}).get("level"), 0) if isinstance(row, dict) else 0
    occ = (_int_or((row or {}).get("occupied"), 0) if isinstance(row, dict) else 0) \
        if occupied_now is None else int(occupied_now)
    after = max(0, min(LEVEL_MAX, before + int(delta)))
    if after == 0 and occ == 0:
        courts.pop(str(court), None)
    else:
        courts[str(court)] = {"level": int(after), "occupied": int(occ)}
    old, new = phase_of(world, before), phase_of(world, after)
    if old == new:
        return None
    return _the_people_cross(world, str(court), old, new, int(occ), str(cause))


def _the_people_cross(world, court: str, old: str, new: str, occ: int,
                      cause: str) -> Dict[str, Any]:
    """ONE literal `log_event` (the Gazette's collector census reads the
    literal) and a HIGH dispatch line in the courts' register."""
    from backend.game_logic.dispatch import queue_dispatch_event
    rising = PHASES.index(new) > PHASES.index(old)
    line = beat_line(world, court, new, rising, occ)
    world.log_event({
        "type": "awakening",
        "nation": court,
        "phase": new,
        "direction": "up" if rising else "down",
        "occupied": int(occ),
        "cause": cause,
        "message": line,
    })
    queue_dispatch_event(world, "awakening", {
        "nation": court, "phase": new, "line": line,
    }, "always")
    return {"type": "awakening", "nation": court, "phase": new,
            "direction": "up" if rising else "down", "occupied": int(occ), "message": line}


def _people_of(court: str) -> str:
    from backend.display_names import display_nation, with_definite_article
    return with_definite_article(display_nation(court), capitalize=False)


def beat_line(world, court: str, new: str, rising: bool, occ: int) -> str:
    """The beat in words — R7 names, never a figure of the scalar."""
    people = _people_of(court)
    if new == "risen":
        return (f"THE PEOPLE OF {people.upper()} HAVE RISEN: an occupier's columns "
                f"bleed on their roads — the country is an ulcer.")
    if new == "stirring" and rising:
        under = (f"{occ} home province{'s' if occ != 1 else ''} under foreign garrisons; "
                 if occ > 0 else "")
        return (f"THE PEOPLE OF {people.upper()} STIR: {under}couriers are waylaid and "
                f"requisitions refused.")
    if new == "stirring":
        return f"The people of {people} subside — the ulcer closes, though the country still stirs."
    return f"The people of {people} are quiet again — home rule is theirs."


# ═══════════════════════════════════════════════════════════════════════
# The tick — once a turn, before the morning's letters
# ═══════════════════════════════════════════════════════════════════════

def tick(world) -> List[Dict[str, Any]]:
    """`_advance_turn_internal`, right before `moments.tick` (the letters
    read the fresh scalar): per boot court the derived count; +band or
    −1; the lump on the transition occupied → none; the beats. O(Σ
    homeland) — 126 lookups a turn on the 1805 map. Unarmed or seam down:
    returns [] at once and writes nothing."""
    if not the_people_stir() or not armed(world):
        return []
    beats: List[Dict[str, Any]] = []
    for court in boot_courts(world):
        now = occupied_count(world, court)
        before_occ = occupied(world, court)
        if now > 0:
            delta = band_raise(now)
        else:
            delta = -QUIET_COOL
            if before_occ > 0:
                delta -= HOME_RULE_LUMP
        if level(world, court) == 0 and delta <= 0 and now == 0 and before_occ == 0:
            continue
        beat = move(world, court, delta,
                    "home_rule" if (now == 0 and before_occ > 0) else "occupation",
                    occupied_now=now)
        if beat:
            beats.append(beat)
    return beats


# ═══════════════════════════════════════════════════════════════════════
# The event writes — each at its ONE existing site
# ═══════════════════════════════════════════════════════════════════════

def note_dictated_peace(world, victim: str) -> Optional[Dict[str, Any]]:
    """`emergent_designs.record_punitive_cessions`: a peace that stripped
    the court of its homeland (the punitive bar) — +15 scaled by rank."""
    return move(world, victim, dictated_peace_raise(world, victim), "dictated_peace")


def note_sovereign_captured(world, court: str) -> Optional[Dict[str, Any]]:
    """`WorldState.capture_marshal` with `is_sovereign`: the king taken —
    Bayonne, and the people rise (+10)."""
    return move(world, court, SOVEREIGN_CAPTURED_RAISE, "sovereign_captured")


def note_client_squeezed(world, client: str) -> Optional[Dict[str, Any]]:
    """`vassal.change_vassal_autonomy` DOWN (tribute rises with it): +5."""
    return move(world, client, CLIENT_SQUEEZED_RAISE, "client_squeezed")


def home_rule_restored(world, court: str, cause: str) -> Optional[Dict[str, Any]]:
    """The lump, −10: a client's autonomy raised, a client released or free
    by rebellion (`vassal.release_vassal` — the liberation term on both
    ratify roads rides it). The last province back by arms or treaty is
    the tick's own transition."""
    return move(world, court, -HOME_RULE_LUMP, cause)


# ═══════════════════════════════════════════════════════════════════════
# The ulcer — `_supply_multiplier`'s read
# ═══════════════════════════════════════════════════════════════════════

def ulcer_factor(world, nation: str, region) -> float:
    """×0.75 when the province's boot owner stands at `risen`, the soil is
    foreign-held (the holder's house outside the owner's) and the army's
    house is outside the owner's too; else 1.0. The boot owner's own army
    never bleeds; nobody bleeds on home-held soil; the player's house
    bleeds like every court (Q3)."""
    if not the_ulcer_bleeds() or not armed(world) or region is None or not nation:
        return 1.0
    from backend.models.region import get_starting_controllers
    starting = (getattr(world, "_starting_controllers", None) or get_starting_controllers())
    owner = str(starting.get(str(getattr(region, "name", "") or "")) or "")
    if not owner or owner == nation:
        return 1.0
    if level(world, owner) < risen(world):
        return 1.0
    homes = home_houses(world, owner)
    if live_house(world, nation) in homes:
        return 1.0
    holder = str(getattr(region, "controller", "") or "")
    if not holder or holder == owner or live_house(world, holder) in homes:
        return 1.0
    return float(ULCER_SUPPLY_FACTOR)


# ═══════════════════════════════════════════════════════════════════════
# The letters — the predicates the affairs engine reads
# ═══════════════════════════════════════════════════════════════════════

def _no() -> Dict[str, Any]:
    return {"holds": False, "bind": {}, "measure": None, "latch": False}


def _host_at(world, lord: str, lo: int, hi: int) -> Dict[str, Any]:
    """The most-occupied ACTIVE court whose level sits in [lo, hi) and whose
    homeland the lord's house holds at least one province of; ties by the
    active-nation order. The measure is the provinces held."""
    if not the_people_write() or not armed(world) or not lord:
        return _no()
    lord_house = live_house(world, lord)
    active = list(world.get_active_nations())
    order = {n: i for i, n in enumerate(active)}
    counts: Dict[str, int] = {}
    for court in active:
        if court == lord:
            continue
        value = level(world, court)
        if not (lo <= value < hi):
            continue
        # a court whose soil is home to the lord's house (its boot client)
        # counts 0 here; a court subjugated LATER counts its new lord's
        # holdings — Spain under Joseph is the Emperor's own affair
        held = held_by_house(world, court, lord_house)
        if held > 0:
            counts[court] = held
    if not counts:
        return _no()
    host = min(counts, key=lambda h: (-counts[h], order.get(h, 10 ** 6), h))
    return {"holds": True, "bind": {"host": host}, "measure": int(counts[host]), "latch": False}


def people_stir(world, lord: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """The People Stir: a court at `stirring` (below `risen`) under the
    lord's garrisons."""
    return _host_at(world, lord, stirring(world), risen(world))


def people_risen(world, lord: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """The Ulcer: a court at `risen` under the lord's garrisons."""
    return _host_at(world, lord, risen(world), LEVEL_MAX + 1)


def phase_words(world, before: int, after: int) -> str:
    """The op's quote in words (Q6's spirit — never a figure): 'quieten
    (risen → stirring)', 'are unchanged (quiet)'."""
    old, new = phase_of(world, before), phase_of(world, after)
    if old == new:
        return f"are unchanged ({new})"
    verb = "quieten" if PHASES.index(new) < PHASES.index(old) else "stir"
    return f"{verb} ({old} → {new})"
