"""DD-C "Nothing fails silently" — the save path's fault injection (Pre-Deploy S7b,
October 12, 2026; `docs/PRE_DEPLOY_PLAN.md` §3 DD-C).

Driven by `tools/playtest_driver.py --save-faults` at the turn boundary (the
FA-102 hook's seat, in-process only): ONE fault per turn, rotating

    disk_full        the write raises OSError(ENOSPC) — through `json.dump`,
                     the real stage, with the half-written temp file cleaned
    unserializable   a value JSON cannot write planted in a SERIALIZED marshal
                     field (`original_nation`) — alternating with FA-S15-1's own
                     shape, the field `delattr`'d so `Marshal.to_dict` raises
    truncated        a save written whole, then cut to half its bytes

and each probe asks the four questions the dive owes the player:

    reached   the sentence reached the player — the `/save` or `/load` reply
              carries it, the autosave's rail row carries it, `/saves` lists a
              damaged file under `damaged`
    logged    a WARNING on `sovereign.errors` names the stage's site (and, for a
              planted value, the field's own path)
    untouched the running world is the same after the failed save or load
              (`to_dict` before and after, the rail rows aside — the failure
              row is written by design)
    recovered the next clean autosave succeeds and retires the rail row

Every turn also checks the round trip on the autosave the clean save wrote:
`to_dict(from_dict(x)) == x` after JSON normalisation, the first differing
paths recorded. The plant is made, saved and reverted INSIDE the probe, so no
game logic ever reads the planted object.
"""
from __future__ import annotations

import contextlib
import copy
import errno
import io
import json
import logging
from pathlib import Path
from typing import Any, Dict, List

KINDS = ("disk_full", "unserializable", "truncated")
SITES = {
    "disk_full": "save_manager.save_game: writing the file",
    "unserializable_planted": "save_manager.save_game: writing the file",
    "unserializable_delattr": "save_manager.save_game: reading the world",
    "truncated": "save_manager.load_game: reading the file",
}
PLANT_FIELD = "original_nation"


class _Capture(logging.Handler):
    def __init__(self):
        super().__init__(level=logging.WARNING)
        self.records: List[str] = []

    def emit(self, record):
        self.records.append(record.getMessage())


@contextlib.contextmanager
def _captured():
    from backend import errors
    log = logging.getLogger(errors.LOGGER_NAME)
    cap = _Capture()
    log.addHandler(cap)
    try:
        yield cap
    finally:
        log.removeHandler(cap)


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


class _FullDisk:
    """`save_manager.json` with a `dump` the disk refuses — the FA-S15-2
    forcing idiom, with the errno a full disk really carries."""
    JSONDecodeError = json.JSONDecodeError
    load = staticmethod(json.load)
    loads = staticmethod(json.loads)
    dumps = staticmethod(json.dumps)

    @staticmethod
    def dump(obj, fp, *a, **k):
        fp.write("{\n")   # a partial write first, as a real full disk does
        raise OSError(errno.ENOSPC, "No space left on device")


def _canon(world) -> Dict:
    """The world as JSON would carry it, the rail rows aside."""
    data = json.loads(json.dumps(world.to_dict()))
    data.pop("notifications", None)
    return data


def _rail(world) -> List[Dict]:
    from backend import notifications
    return [n for n in world.notifications.to_list()
            if n.get("type") == notifications.SAVE_FAILED]


def _diff(a: Any, b: Any, path: str = "", out: List[str] | None = None, limit: int = 8) -> List[str]:
    out = [] if out is None else out
    if len(out) >= limit:
        return out
    if type(a) is not type(b):
        out.append(f"{path or '/'}: {type(a).__name__} != {type(b).__name__}")
    elif isinstance(a, dict):
        for k in sorted(set(a) | set(b), key=str):
            if k not in a or k not in b:
                out.append(f"{path}.{k}: only on the {'right' if k not in a else 'left'}")
            else:
                _diff(a[k], b[k], f"{path}.{k}", out, limit)
    elif isinstance(a, list):
        if len(a) != len(b):
            out.append(f"{path}: {len(a)} items != {len(b)}")
        for i, (x, y) in enumerate(zip(a, b)):
            _diff(x, y, f"{path}[{i}]", out, limit)
    elif a != b:
        out.append(f"{path}: {str(a)[:60]!r} != {str(b)[:60]!r}")
    return out


def round_trip(slot: Path) -> List[str]:
    """`to_dict(from_dict(x)) == x` on the file the autosave wrote.

    ⚠ The scratch world passes `WorldState.__init__`, which empties
    Berthier's display-only line rotation (`battle_report.
    _OBSERVATION_COUNTS`, IQ-8 item 8's one chokepoint for "a campaign
    begins"). This check is not a campaign, so the counter is put back —
    measured, without it twelve battle lines of a 40-turn run took other
    words (casualties identical); with it the probed run is the plain run's
    digest line for line."""
    from backend.game_logic import battle_report
    from backend.models.world_state import WorldState
    x = json.loads(slot.read_text(encoding="utf-8"))["world_state"]
    rotation = dict(battle_report._OBSERVATION_COUNTS)
    try:
        with _quiet():
            y = json.loads(json.dumps(WorldState.from_dict(copy.deepcopy(x)).to_dict()))
    finally:
        battle_report._OBSERVATION_COUNTS.clear()
        battle_report._OBSERVATION_COUNTS.update(rotation)
    return _diff(x, y)


def _clean_autosave(sm, world) -> Dict[str, Any]:
    with _quiet():
        result = sm.autosave(world)
    slot = sm.SAVE_DIR / sm.AUTOSAVE_FILENAME
    return {
        "recovered": bool(result.get("success")) and not _rail(world),
        "round_trip": round_trip(slot) if slot.exists() else ["no autosave file"],
    }


def _marshal(world):
    names = sorted(n for n, m in world.marshals.items() if m.nation == world.player_nation)
    return world.marshals[names[0]] if names else next(iter(world.marshals.values()))


def probe(transport, turn: int, index: int) -> Dict[str, Any]:
    """One fault at the turn boundary; the row the driver records."""
    import backend.save_manager as sm
    world = transport.backend_main.world
    kind = KINDS[index % len(KINDS)]
    row: Dict[str, Any] = {"turn": int(turn), "kind": kind}

    # ⚠ "untouched" is measured around DIRECT save_manager calls: the HTTP
    # envelope (`build_base_response`) closes a fallen campaign and drains
    # notices on its own, so a diff taken across a route is polluted by it.
    if kind == "disk_full":
        with _captured() as cap:
            real = sm.json
            sm.json = _FullDisk
            try:
                saved = transport.post("/save", {"save_name": f"ddc_t{turn}"})
                before = _canon(world)
                with _quiet():
                    direct = sm.save_game(world, f"ddc_direct_t{turn}")
                    auto = sm.autosave(world)
                after = _canon(world)
            finally:
                sm.json = real
        rail = _rail(world)
        tmp_left = [p.name for p in sm.SAVE_DIR.glob("*.tmp")]
        row.update({
            "reached": (saved.get("success") is False
                        and "disk is full" in str(saved.get("message"))
                        and auto.get("success") is False
                        and len(rail) == 1 and "disk is full" in rail[0]["message"]),
            "logged": sum(SITES["disk_full"] in r for r in cap.records) >= 3,
            "untouched": (after == before and direct.get("success") is False
                          and not tmp_left),
            "message": saved.get("message"),
        })
        if tmp_left:
            row["tmp_left"] = tmp_left

    elif kind == "unserializable":
        m = _marshal(world)
        shape = "planted" if (index // len(KINDS)) % 2 == 0 else "delattr"
        prior = getattr(m, PLANT_FIELD, None)

        def plant():
            if shape == "planted":
                setattr(m, PLANT_FIELD, object())
            else:
                delattr(m, PLANT_FIELD)

        with _captured() as cap:
            try:
                plant()
                saved = transport.post("/save", {"save_name": f"ddc_t{turn}"})
            finally:
                setattr(m, PLANT_FIELD, prior)
            before = _canon(world)
            try:
                plant()
                with _quiet():
                    direct = sm.save_game(world, f"ddc_direct_t{turn}")
                    auto = sm.autosave(world)
            finally:
                setattr(m, PLANT_FIELD, prior)
            after = _canon(world)
        site = SITES[f"unserializable_{shape}"]
        rail = _rail(world)
        named = (shape == "delattr"
                 or any(f"marshals.{m.name}.{PLANT_FIELD}" in r for r in cap.records))
        row.update({
            "shape": shape, "marshal": m.name,
            "reached": (saved.get("success") is False
                        and "could not be written down" in str(saved.get("message"))
                        and auto.get("success") is False
                        and len(rail) == 1 and "could not be written down" in rail[0]["message"]),
            "logged": sum(site in r for r in cap.records) >= 3 and named,
            "untouched": after == before and direct.get("success") is False,
            "message": saved.get("message"),
        })

    else:  # truncated
        name = f"ddc_trunc_t{turn}"
        saved = transport.post("/save", {"save_name": name})
        path = sm.SAVE_DIR / f"{name}.json"
        raw = path.read_bytes()
        path.write_bytes(raw[: len(raw) // 2])
        world_obj, turn_before = world, int(world.current_turn)
        with _captured() as cap:
            listing = transport.get("/saves")
            loaded = transport.post("/load", {"filename": f"{name}.json"})
        damaged = [d.get("filename") for d in listing.get("damaged") or []]
        listed = [s.get("filename") for s in listing.get("saves") or []]
        row.update({
            "reached": (saved.get("success") is True
                        and f"{name}.json" in damaged and f"{name}.json" not in listed
                        and loaded.get("success") is False
                        and "corrupt" in str(loaded.get("message"))),
            "logged": any(SITES["truncated"] in r for r in cap.records),
            "untouched": (transport.backend_main.world is world_obj
                          and int(world_obj.current_turn) == turn_before),
            "message": loaded.get("message"),
        })
        try:
            path.unlink()
        except OSError:
            row["cleanup"] = "the truncated file could not be removed"

    row.update(_clean_autosave(sm, world))
    row["ok"] = bool(row["reached"] and row["logged"] and row["untouched"]
                     and row["recovered"] and not row["round_trip"])
    return row


def summary(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    by_kind: Dict[str, Dict[str, int]] = {}
    for r in rows:
        k = by_kind.setdefault(r["kind"], {"probes": 0, "ok": 0})
        k["probes"] += 1
        k["ok"] += int(bool(r["ok"]))
    return {
        "probes": len(rows),
        "ok": sum(1 for r in rows if r["ok"]),
        "by_kind": by_kind,
        "round_trips_equal": sum(1 for r in rows if not r["round_trip"]),
        "failures": [r for r in rows if not r["ok"]],
    }


def digest_line(row: Dict[str, Any]) -> str:
    marks = " · ".join(f"{k} {'✓' if row.get(k) else '✗'}"
                       for k in ("reached", "logged", "untouched", "recovered"))
    rt = "round trip ✓" if not row.get("round_trip") else f"round trip ✗ {row['round_trip'][:2]}"
    return f"DD-C t{row['turn']} {row['kind']}{'/' + row['shape'] if row.get('shape') else ''}: {marks} · {rt}"
