"""NPC-12 / SF5-X3 — the name census (Score Finish Step 7 slice 7, October 4,
2026).

Every string a response carries to the screen is read for a roster KEY the
reader should never see: "ArchdukeCharles" where the game means "Archduke
Charles". An in-process driver observer (`tools/playtest_driver.py
--name-census`), on POST and GET alike — the measured leaks rode both (the
campaign log, the ledger and the petition card are GETs).

The keys are DERIVED from the world, never listed: every marshal — on the
roster, in the tombstones, on the bench — whose display name is not its key.
On the 1805 board that is two of sixty-eight (ArchdukeCharles, ArchdukeJohn);
a mod's new two-word names join the census without an edit.

Out of scope by construction, each with its reason:
  * machine fields — a field whose WHOLE value is a key ("marshal":
    "ArchdukeCharles": an identity, read back by the client and the
    executor) and every command or id the client sends back ("command":
    "attack ArchdukeCharles" is the player's own order and parses either
    way; renaming the keys was rejected — 227 test files read them);
  * the two enemy-phase fields the client never renders — the phase's
    `summary[]` and an action's `message`: `enemy_phase_dialog.gd` rebuilds
    every line from structured fields (pinned by a source check in
    `tests/test_sf7_s7_the_name_and_the_rank.py`).

Pass condition: zero leaks AND the run saw at least one of the keys' display
names in a rendered string (else the arm never met the names, and a zero is
vacuous — the verdict says so rather than passing).
"""
from __future__ import annotations

import re
from typing import Any, Dict, List

MACHINE_FIELDS = frozenset({
    "command", "commands", "typed", "suggested_command", "action_command",
    "chip_command", "identity", "key", "id", "url", "href",
})
MACHINE_SUFFIXES = ("_command", "_id", "_key", "_url")

# A path, with list indices normalised to [], that the client never renders.
UNRENDERED_PATHS = (
    re.compile(r"^enemy_phase\.summary\[\]$"),
    re.compile(r"^enemy_phase\.nations\.[^.]+\.actions\[\]\.message$"),
)


def humanize(key: str) -> str:
    from backend.display_names import humanize_entity_name
    return humanize_entity_name(key)


def derive_keys(world) -> List[str]:
    """Every marshal key whose display name differs from the key."""
    names = set((getattr(world, "marshals", None) or {}).keys())
    names |= set((getattr(world, "fallen_marshals", None) or {}).keys())
    pool = getattr(world, "marshal_pool", None) or {}
    if isinstance(pool, dict):
        for rows in pool.values():
            for row in rows or []:
                if isinstance(row, dict) and row.get("name"):
                    names.add(str(row["name"]))
    return sorted(k for k in names if k and humanize(k) != k)


def _norm(path: str) -> str:
    return re.sub(r"\[\d+\]", "[]", path)


def _is_machine(path: str) -> bool:
    leaf = path.rsplit(".", 1)[-1]
    leaf = re.sub(r"\[\]$", "", leaf)
    return leaf in MACHINE_FIELDS or leaf.endswith(MACHINE_SUFFIXES)


def _is_unrendered(path: str) -> bool:
    return any(rx.match(path) for rx in UNRENDERED_PATHS)


class NameCensus:
    def __init__(self, digest=None, backend_main=None):
        self.digest = digest
        self.backend_main = backend_main
        self.responses = 0
        self.by_method: Dict[str, int] = {}
        self.strings = 0
        self.leaks: Dict[tuple, Dict[str, Any]] = {}
        self.display_seen = 0
        self.keys: List[str] = []
        self.errors: List[str] = []

    # ── the observer ──────────────────────────────────────────────────
    def observe(self, path, payload, body, method: str = "POST") -> None:
        try:
            self._observe(path, body, method)
        except Exception as exc:  # an instrument records its own failure
            self.errors.append(f"{type(exc).__name__}: {exc}")

    def observe_get(self, path, payload, body) -> None:
        self.observe(path, payload, body, method="GET")

    def _observe(self, path, body, method):
        world = getattr(self.backend_main, "world", None) if self.backend_main else None
        if world is not None:
            self.keys = derive_keys(world)
        self.responses += 1
        self.by_method[method] = self.by_method.get(method, 0) + 1
        self.read(body, f"{method} {path}")

    def read(self, body, endpoint: str = "") -> None:
        if not self.keys:
            return
        rx = re.compile(r"\b(" + "|".join(re.escape(k) for k in self.keys) + r")\b")
        shown = [humanize(k) for k in self.keys]
        self._walk(body, "", endpoint, rx, shown)

    def _walk(self, node, path, endpoint, rx, shown):
        if isinstance(node, dict):
            for k, v in node.items():
                self._walk(v, f"{path}.{k}" if path else str(k), endpoint, rx, shown)
        elif isinstance(node, list):
            for i, v in enumerate(node):
                self._walk(v, f"{path}[{i}]", endpoint, rx, shown)
        elif isinstance(node, str):
            self.strings += 1
            norm = _norm(path)
            if any(s in node for s in shown):
                self.display_seen += 1
            if node in self.keys or _is_machine(norm) or _is_unrendered(norm):
                return
            m = rx.search(node)
            if m:
                key = (endpoint, norm)
                row = self.leaks.setdefault(key, {"endpoint": endpoint, "path": norm,
                                                  "count": 0, "sample": node[:300]})
                row["count"] += 1

    # ── the verdict ───────────────────────────────────────────────────
    def summary(self) -> Dict[str, Any]:
        leaks = sorted(self.leaks.values(), key=lambda r: -r["count"])
        total = sum(r["count"] for r in leaks)
        if self.errors:
            verdict = "INSTRUMENT ERROR"
        elif total:
            verdict = "FAIL"
        elif not self.display_seen:
            verdict = "VACUOUS — the arm never met the names"
        else:
            verdict = "PASS"
        return {"verdict": verdict, "keys": list(self.keys),
                "responses": self.responses, "by_method": dict(self.by_method),
                "strings": self.strings,
                "display_seen": self.display_seen, "leaks": total,
                "by_field": leaks[:40], "errors": self.errors[:10]}

    def digest_lines(self) -> List[str]:
        s = self.summary()
        out = [f"\n## Name census (NPC-12 / SF5-X3)\n",
               f"- verdict **{s['verdict']}** · keys {', '.join(s['keys']) or '—'} · "
               f"{s['responses']} responses · {s['strings']} strings · "
               f"{s['display_seen']} carrying a display name · {s['leaks']} leaks"]
        for row in s["by_field"]:
            out.append(f"  - LEAK {row['count']}× {row['endpoint']} `{row['path']}`: "
                       f"{row['sample'][:160]}")
        for err in s["errors"]:
            out.append(f"  - INSTRUMENT ERROR {err}")
        return out


def unmeasured(reason: str) -> Dict[str, Any]:
    return {"verdict": "UNMEASURED", "reason": reason}
