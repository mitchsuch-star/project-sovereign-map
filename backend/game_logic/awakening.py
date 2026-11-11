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

DY-5 — THE SECOND HALF (session D, November 10, 2026; §5's three
expressions completed and the interplays named there), five more seams:

* THE LIBERATION LEVÉE (`the_levee_rises`, row T6-LEVEE — 1813): a court
  whose people stand at `stirring` or above, AT WAR, with home soil
  contested (the last tick's derived count above 0) regenerates infantry
  ×1.5 and prices the draft ×0.75 — `levee_terms`, read by
  `get_manpower_regen_rates` (after the war exhaustion, before the laws)
  and `_recruit_cost_terms` (after the doctrine's term, before the laws;
  the AI's P1 rung reads the same pricer). THE NATIONAL GUARD — the third
  letter's Accept — doubles the bonus for a term (×2.0 / ×0.5; the court
  row's `guard`, the morning it ends). The levée is a beat: ONE `levee`
  log row when it rises, when it stands down and when the Guard is armed
  (the census 184 → 185), a HIGH dispatch line, the Gazette's column.
* THE CLIENT DIAL — THE TIGER RIDDEN (`the_tiger_is_ridden`, row T6-DIAL —
  Westphalia against Spain): a client whose people are awakened (≥
  `stirring`) bleeds loyalty −2 a turn at autonomy ≤ 1 and GAINS +1 a turn
  at autonomy ≥ 2 — France can ride the force it exports, paying in
  control. ONE read, `client_dial`, for the loyalty tick, the forecast and
  the debug breakdown (the F7 lesson); a rebellion of an awakened client
  NAMES its cause (`rebellion_cause` → `vassal_broke_free.cause`).
* THE REVANCHE OF A RISEN PEOPLE (`a_risen_people_swears_revanche`, row
  T6-REVANCHE — Prussia after Jena): a court at `risen` with ANY lost
  homeland promotes its grievance into a design — the partition bar
  waived, the people's rising is the backing (`risen_grievance`, read by
  `emergent_designs.process_emergent_designs`).
* THE LIBERATORS HOLD TOGETHER (`liberators_hold_together`, row
  T6-LIBERATORS): while the league's target holds an awakened people's
  soil, the members' friction frays 1 a turn instead of 2
  (`coalition_friction_step`, read by `coalition.apply_coalition_friction`).
* THE NATION IN ARMS (`the_nation_writes`, row T6-ARMS — row DY-5 of
  `affairs.SINCE_ROWS`): the third letter — the player's OWN people at
  `risen` against an invader (`nation_in_arms`: the lord at war, home soil
  contested, the Guard not standing; the enemy house holding the most of
  the homeland bound as `host`); Accept arms the National Guard (the
  `national_guard` op — the thirteenth), Decline authority on the floor.
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
# DY-5 (N-DY5): the liberation levée and the National Guard's doubling
LEVEE_REGEN_FACTOR = 1.5             # infantry regen, the court at war on contested home soil
LEVEE_PRICE_FACTOR = 0.75            # the draft's price
GUARD_REGEN_FACTOR = 2.0             # the National Guard armed: the bonus doubled
GUARD_PRICE_FACTOR = 0.5
GUARD_TURNS_BOUNDS = (3, 12)         # the `national_guard` op's `turns`
LEVEE_LOG_TYPE = "levee"
# the client dial — the tiger ridden
DIAL_PUPPET_DRIFT = -2               # autonomy <= 1: the people's awakening
DIAL_AUTONOMOUS_DRIFT = 1            # autonomy >= 2: the tiger ridden
DIAL_AUTONOMY_SPLIT = 2
DIAL_LABEL_RESENT = "the people's awakening"
DIAL_LABEL_RIDDEN = "the tiger ridden"
REBELLION_CAUSE = "awakening"
# the liberators' friction: 1 a turn where the league frees a people, else 2
FRICTION_STEP = 2
FRICTION_STEP_EASED = 1


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


def the_levee_rises() -> bool:
    """T6-LEVEE seam (DY-5): the liberation levée — a court at war on its
    contested home soil, its people awakened, regenerates infantry ×1.5 and
    prices the draft ×0.75 (the National Guard doubles it). Down: 1.0 and
    1.0 everywhere, no levée beat, the Guard never armed."""
    return True


def the_tiger_is_ridden() -> bool:
    """T6-DIAL seam (DY-5): the client dial — an awakened client's loyalty
    −2 a turn at autonomy ≤ 1, +1 at autonomy ≥ 2; a rebellion names the
    cause. Down: the dial reads 0 and no rebellion is the Awakening's."""
    return True


def a_risen_people_swears_revanche() -> bool:
    """T6-REVANCHE seam (DY-5): a court at `risen` with any lost homeland
    promotes its grievance into a design, the partition bar waived. Down:
    the bar stands as AI-5b authored it."""
    return True


def liberators_hold_together() -> bool:
    """T6-LIBERATORS seam (DY-5): while the league's target holds an
    awakened people's soil, the members' friction frays 1 a turn, not 2.
    Down: 2 a turn as §3b authored it."""
    return True


def the_nation_writes() -> bool:
    """T6-ARMS seam (row DY-5 of `affairs.SINCE_ROWS`): The Nation in Arms
    sits in the deck and its predicate reads. Down: the template held out
    whole, the predicate never holds, the `national_guard` op skips."""
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
        clean: Dict[str, int] = {"level": level, "occupied": occupied}
        # DY-5: the levée's bit and the National Guard's term ride the row
        if _int_or(row.get("levee"), 0) > 0:
            clean["levee"] = 1
        guard = max(0, _int_or(row.get("guard"), 0))
        if guard:
            clean["guard"] = guard
        if level or occupied or len(clean) > 2:
            out[str(court)] = clean
    return out


def _row_is_empty(row: Dict[str, Any]) -> bool:
    return not any(int(row.get(k, 0) or 0) for k in ("level", "occupied", "levee", "guard"))


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


def adopt_court(world, court: str, lord: str) -> None:
    """DY-6 (§5a C2's corollary): a court ERECTED later — a carve, a crown —
    is born into the web under the lord that made it: its own soil under
    him is home, and the carved people keep THEIR boot house (the Neapolitans
    under the Kingdom of Naples count the French house foreign). Written
    once; a tag re-carved after an erasure keeps its first house (a people
    remembers). Unarmed: nothing."""
    if not armed(world) or not court or not lord or str(court) == str(lord):
        return
    ensure_houses(world).setdefault(str(court), str(lord))


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
    row = dict(row) if isinstance(row, dict) else {}
    before = _int_or(row.get("level"), 0)
    occ = _int_or(row.get("occupied"), 0) if occupied_now is None else int(occupied_now)
    after = max(0, min(LEVEL_MAX, before + int(delta)))
    row["level"], row["occupied"] = int(after), int(occ)
    # DY-5: the levée's bit and the Guard's term survive the write
    if _row_is_empty(row):
        courts.pop(str(court), None)
    else:
        courts[str(court)] = row
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
            if not _levee_bit(world, court) and not guard_until(world, court):
                continue
        beat = move(world, court, delta,
                    "home_rule" if (now == 0 and before_occ > 0) else "occupation",
                    occupied_now=now)
        if beat:
            beats.append(beat)
        # DY-5: the levée rises or stands down on the fresh level and count
        levee_beat = _settle_levee(world, court)
        if levee_beat:
            beats.append(levee_beat)
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


# ═══════════════════════════════════════════════════════════════════════
# DY-5 — the liberation levée and the National Guard
# ═══════════════════════════════════════════════════════════════════════

def _row(world, court: str) -> Dict[str, Any]:
    row = (store(world).get("courts") or {}).get(str(court))
    return row if isinstance(row, dict) else {}


def _levee_bit(world, court: str) -> bool:
    return _int_or(_row(world, court).get("levee"), 0) > 0


def guard_until(world, court: str) -> int:
    """The morning the National Guard's term ends (0: never armed)."""
    return max(0, _int_or(_row(world, court).get("guard"), 0))


def guard_stands(world, court: str) -> bool:
    return guard_until(world, court) > _turn(world)


def _at_war(world, court: str) -> bool:
    return bool(world.get_nations_at_war_with(court))


def levee_holds(world, court: str) -> bool:
    """The levée's condition: the court's people at `stirring` or above,
    the court AT WAR, its home soil contested — the LAST TICK's derived
    count (the store's figure, never a scan; the tick runs before the
    regen and before the morning's letters). Unarmed or seam down: False."""
    if not the_levee_rises() or not armed(world) or not court:
        return False
    if level(world, court) < stirring(world):
        return False
    if occupied(world, court) <= 0:
        return False
    # a people outlives its court (C3); a levée does not — an erased court has
    # no depots and no treasury to raise one (the harness's Austria, every
    # province taken by turn 11: its people stir and rise, no levée)
    if court not in set(world.get_active_nations()):
        return False
    return _at_war(world, court)


def levee_terms(world, court: str) -> Tuple[float, float, str]:
    """(regen factor, price factor, the term's name) — (1.0, 1.0, "") with
    no levée; the National Guard armed doubles the bonus for its term."""
    if not levee_holds(world, court):
        return 1.0, 1.0, ""
    if guard_stands(world, court):
        return float(GUARD_REGEN_FACTOR), float(GUARD_PRICE_FACTOR), "the National Guard"
    return float(LEVEE_REGEN_FACTOR), float(LEVEE_PRICE_FACTOR), "the levée"


def _write_bit(world, court: str, key: str, value: int) -> None:
    st = store(world)
    courts = st.setdefault("courts", {})
    row = dict(courts.get(str(court)) or {})
    row.setdefault("level", 0)
    row.setdefault("occupied", 0)
    if value:
        row[key] = int(value)
    else:
        row.pop(key, None)
    if _row_is_empty(row):
        courts.pop(str(court), None)
    else:
        courts[str(court)] = row


def _settle_levee(world, court: str) -> Optional[Dict[str, Any]]:
    """The tick's second write: the levée's bit against its condition —
    a beat when it rises or stands down (the Guard's term lapses silently
    with the levée, or outlives nothing: it is read only while the levée
    holds)."""
    if not the_levee_rises() or not armed(world):
        return None
    # the Guard's term, once past, leaves the row (a lapsed term is no bit)
    until = guard_until(world, court)
    if until and until <= _turn(world):
        _write_bit(world, court, "guard", 0)
    was, now = _levee_bit(world, court), levee_holds(world, court)
    if was == now:
        return None
    _write_bit(world, court, "levee", 1 if now else 0)
    return _the_levee_beats(world, court, "raised" if now else "stood_down")


def arm_national_guard(world, court: str, turns: int) -> Optional[Dict[str, Any]]:
    """The letter's Accept (the `national_guard` op): the Guard under arms
    for `turns` mornings from today — the levée's bonus doubled while it
    holds. Nothing with the seam down or no levée standing."""
    if not the_levee_rises() or not armed(world) or not court:
        return None
    lo, hi = GUARD_TURNS_BOUNDS
    turns = max(lo, min(hi, int(turns)))
    _write_bit(world, court, "guard", _turn(world) + turns)
    return _the_levee_beats(world, court, "guard")


def _the_levee_beats(world, court: str, direction: str) -> Dict[str, Any]:
    """ONE literal `log_event` (the Gazette's collector census reads the
    literal) and a HIGH dispatch line in the courts' register."""
    from backend.game_logic.dispatch import queue_dispatch_event
    occ = occupied(world, court)
    line = levee_line(world, court, direction, occ)
    world.log_event({
        "type": "levee",
        "nation": court,
        "direction": direction,
        "occupied": int(occ),
        "guard_until": int(guard_until(world, court)),
        "message": line,
    })
    queue_dispatch_event(world, "levee", {"nation": court, "direction": direction, "line": line},
                         "always")
    return {"type": "levee", "nation": court, "direction": direction, "occupied": int(occ),
            "message": line}


def levee_line(world, court: str, direction: str, occ: int) -> str:
    """The beat in words — R7 names, never a figure of the scalar."""
    people = _people_of(court)
    if direction == "guard":
        return (f"THE NATIONAL GUARD OF {people.upper()} UNDER ARMS: the departments send their "
                f"battalions — the levée is doubled while the Guard stands.")
    if direction == "raised":
        under = (f"{occ} home province{'s' if occ != 1 else ''} under foreign arms; "
                 if occ > 0 else "")
        return (f"THE NATION IN ARMS: the people of {people}, at war on their own soil — {under}"
                f"the depots fill and the levy comes cheap.")
    return f"The levée of {people} stands down — the war is over, or the soil is free."


# ═══════════════════════════════════════════════════════════════════════
# DY-5 — the client dial: the tiger ridden
# ═══════════════════════════════════════════════════════════════════════

def client_dial(world, client: str, autonomy: int) -> Tuple[str, int]:
    """ONE read for the loyalty tick, the forecast and the debug breakdown
    (the F7 lesson: three copies of a term drift apart): ("", 0) for a quiet
    people (below `stirring`), an unarmed world or the seam down; else
    (`DIAL_LABEL_RESENT`, −2) at autonomy ≤ 1 and (`DIAL_LABEL_RIDDEN`, +1)
    at autonomy ≥ 2 — France rides the force it exports by paying in
    control."""
    if not the_tiger_is_ridden() or not armed(world) or not client:
        return "", 0
    if client_people_level(world, client) < stirring(world):
        return "", 0
    if int(autonomy) >= DIAL_AUTONOMY_SPLIT:
        return DIAL_LABEL_RIDDEN, int(DIAL_AUTONOMOUS_DRIFT)
    # DY-7 (DYNAMISM_SPEC.md §6 — the §5 interplay it owns): a crown client
    # whose crown a legitimist still withholds drifts one worse (−3); the
    # label names the cause (`crowns.dial_extra` — 0 for a plain client).
    from backend.game_logic.crowns import DIAL_LABEL_UNRECOGNIZED, dial_extra
    extra = int(dial_extra(world, client))
    if extra:
        return DIAL_LABEL_UNRECOGNIZED, int(DIAL_PUPPET_DRIFT) + extra
    return DIAL_LABEL_RESENT, int(DIAL_PUPPET_DRIFT)


def client_people_level(world, client: str) -> int:
    """The scalar the dial and the rebellion's cause read: the client's own
    people — or, for a court CARVED out of another's soil (DY-6's crowns and
    NA-6c's carves; §5a C2: the carved people keep their scalar under the
    court they were carved from, the Neapolitans under "Naples" while the
    Kingdom of Naples reigns over them), the higher of the two. Before
    DY-7 (session F) a carved client read only its own empty row, so the
    people it sat on could rise without its dial ever moving — the sibling
    of C3's house fix, unseamed (no measured arm carves) and pinned."""
    own = level(world, client)
    row = (getattr(world, "vassals", {}) or {}).get(client)
    source = str(row.get("carved_from") or "") if isinstance(row, dict) else ""
    return max(own, level(world, source)) if source and source != client else own


def rebellion_cause(world, client: str) -> str:
    """`check_vassal_rebellion`, read BEFORE the row is deleted: "awakening"
    when the breaking client's people are awakened (≥ `stirring`), else ""
    — the `vassal_broke_free` row, the dispatch line and the one-liner
    name it."""
    if not the_tiger_is_ridden() or not armed(world) or not client:
        return ""
    return REBELLION_CAUSE if client_people_level(world, client) >= stirring(world) else ""


# ═══════════════════════════════════════════════════════════════════════
# DY-5 — the interplays: a risen people's revanche, the liberators' friction
# ═══════════════════════════════════════════════════════════════════════

def risen_grievance(world, court: str) -> bool:
    """`emergent_designs.process_emergent_designs`: a court at `risen`
    promotes its grievance with ANY lost homeland — the partition bar
    waived; the people's rising is the backing (Prussia after Jena)."""
    if not a_risen_people_swears_revanche() or not armed(world) or not court:
        return False
    return level(world, court) >= risen(world)


def friction_eased(world, target: str) -> bool:
    """True while the league's `target` (its live house) holds at least one
    province of an awakened people's homeland as a FOREIGN holder — the
    liberators have a cause. O(awakened courts × homeland), the store's
    rows, never a scan."""
    if not liberators_hold_together() or not armed(world) or not target:
        return False
    house = live_house(world, target)
    threshold = stirring(world)
    for court, row in sorted((store(world).get("courts") or {}).items()):
        if not isinstance(row, dict) or _int_or(row.get("level"), 0) < threshold:
            continue
        if held_by_house(world, court, house) > 0:
            return True
    return False


def coalition_friction_step(world, target: str) -> int:
    """`coalition.apply_coalition_friction`: the members' fray a turn — 1
    where the league frees an awakened people, else 2."""
    return int(FRICTION_STEP_EASED if friction_eased(world, target) else FRICTION_STEP)


# ═══════════════════════════════════════════════════════════════════════
# DY-5 — the third letter: The Nation in Arms
# ═══════════════════════════════════════════════════════════════════════

def nation_in_arms(world, lord: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """The Nation in Arms — the lord's OWN people at `risen`, the lord at
    war, home soil contested (the levée's own condition) and the Guard not
    standing; the enemy house holding the most of the lord's homeland is
    bound as `host` (the invader the letter names), the measure the
    provinces it holds. Ties by the active-nation order."""
    if not the_nation_writes() or not armed(world) or not lord:
        return _no()
    if level(world, lord) < risen(world) or occupied(world, lord) <= 0:
        return _no()
    if guard_stands(world, lord):
        return _no()
    enemies = [str(n) for n in (world.get_nations_at_war_with(lord) or [])]
    if not enemies:
        return _no()
    active = list(world.get_active_nations())
    order = {n: i for i, n in enumerate(active)}
    counts: Dict[str, int] = {}
    for enemy in enemies:
        house = live_house(world, enemy)
        if house in counts or house not in order:
            continue
        held = held_by_house(world, lord, house)
        if held > 0:
            counts[house] = held
    if not counts:
        return _no()
    invader = min(counts, key=lambda h: (-counts[h], order.get(h, 10 ** 6), h))
    return {"holds": True, "bind": {"host": invader}, "measure": int(counts[invader]), "latch": False}
