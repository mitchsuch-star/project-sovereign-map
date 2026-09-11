"""FA-S17-2 (Phase 3, September 11, 2026) — the AI's contact list is built in
MAP order.

`WorldState.get_live_visible_enemies` iterated the cached SET of visible
region names, so the order of the contact list — and P4's first-found target
at an equal ratio — was the process's hash seed. Measured on the School's
control lesson: under PYTHONHASHSEED 0 and 1 the enemy phase of turn 6
attacked a different French corps and the delivered jealousy events diverged
from there (the row's "process-state leak" that no suite-order bisection
could find). The driver pins the hash seed and never saw it.

The pins below feed the reader a region set whose iteration order is
deliberately REVERSED, so "sorted" and "as iterated" can never coincide by
luck of the seed: the lever UP yields map order, the lever DOWN the set's own.
"""
from __future__ import annotations

import contextlib
import io
from pathlib import Path

from backend.models import world_state as WS
from backend.models.world_state import WorldState

ROOT = next(p for p in (Path(__file__).resolve().parents[1], Path.cwd()) if (p / "backend").is_dir())
SCENARIO = ROOT / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"


class _ReversedSet(set):
    """A set that iterates in REVERSE sorted order — the adversary's seed."""

    def __iter__(self):
        return iter(sorted(set.__iter__(self), reverse=True))


def _boot():
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(str(SCENARIO))


def _regions_of(marshals):
    out = []
    for m in marshals:
        if m.location not in out:
            out.append(m.location)
    return out


class TestTheContactListIsInMapOrder:
    def _world_with_reversed_sight(self, monkeypatch):
        w = _boot()
        real = w._get_live_visible_regions_cached

        def reversed_sight(nation):
            return _ReversedSet(real(nation))

        monkeypatch.setattr(w, "_get_live_visible_regions_cached", reversed_sight)
        return w

    def test_austria_reads_the_french_in_map_order(self, monkeypatch):
        w = self._world_with_reversed_sight(monkeypatch)
        contacts = w.get_live_visible_enemies("Austria")
        regions = _regions_of(contacts)
        assert len(regions) >= 2, regions
        assert regions == sorted(regions), regions
        assert any(m.nation == "France" for m in contacts)

    def test_the_order_does_not_depend_on_the_sets_iteration(self, monkeypatch):
        w = _boot()
        plain = _regions_of(w.get_live_visible_enemies("Austria"))
        w2 = self._world_with_reversed_sight(monkeypatch)
        reversed_seen = _regions_of(w2.get_live_visible_enemies("Austria"))
        assert plain == reversed_seen == sorted(plain)

    def test_lever_down_reads_the_sets_own_order(self, monkeypatch):
        monkeypatch.setattr(WS, "THE_CONTACT_LIST_IS_ORDERED", False)
        w = self._world_with_reversed_sight(monkeypatch)
        regions = _regions_of(w.get_live_visible_enemies("Austria"))
        assert len(regions) >= 2
        assert regions == sorted(regions, reverse=True), regions

    def test_the_same_men_either_way(self, monkeypatch):
        w = self._world_with_reversed_sight(monkeypatch)
        up = sorted(m.name for m in w.get_live_visible_enemies("Austria"))
        monkeypatch.setattr(WS, "THE_CONTACT_LIST_IS_ORDERED", False)
        down = sorted(m.name for m in w.get_live_visible_enemies("Austria"))
        assert up == down and up
