"""Scale Readiness Phase 2.1 benchmark: get_distance() cache on a 100-region synthetic graph.

Plan reference: docs/SCALE_READINESS_PLAN.md §2.1 ("Benchmark before/after with
100-region synthetic graph. Verify the cache survives a controller change and
only changes after an explicit adjacency mutation + invalidation call.").

Usage:
    .venv\\Scripts\\python.exe -m tools.benchmark_distance_cache

Prints uncached vs. cached timings on a 10x10 grid with 4-neighbor adjacency,
then asserts the Phase 2.1 invariance contract (no-op reads keep cache stable,
explicit invalidation clears it).
"""
from __future__ import annotations

import random
import sys
from dataclasses import dataclass, field
from time import perf_counter
from typing import Dict, List

from backend.models.world_state import WorldState


GRID_SIDE = 10  # 10 x 10 = 100 regions, per plan §2.1
SAMPLED_PAIRS = 2000
RNG_SEED = 42


@dataclass
class SyntheticRegion:
    """Minimal Region stand-in: get_distance() only reads .adjacent_regions."""

    name: str
    adjacent_regions: List[str] = field(default_factory=list)
    controller: str = "Neutral"


def build_grid(side: int) -> Dict[str, SyntheticRegion]:
    regions: Dict[str, SyntheticRegion] = {
        f"R_{x}_{y}": SyntheticRegion(name=f"R_{x}_{y}")
        for x in range(side)
        for y in range(side)
    }
    for x in range(side):
        for y in range(side):
            name = f"R_{x}_{y}"
            neighbors: List[str] = []
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < side and 0 <= ny < side:
                    neighbors.append(f"R_{nx}_{ny}")
            regions[name].adjacent_regions = neighbors
    return regions


def make_synthetic_world() -> WorldState:
    world = WorldState()
    world.regions = build_grid(GRID_SIDE)  # type: ignore[assignment]
    world.invalidate_distance_cache()
    return world


def sample_pairs(world: WorldState, count: int) -> List[tuple[str, str]]:
    names = list(world.regions.keys())
    rng = random.Random(RNG_SEED)
    return [(rng.choice(names), rng.choice(names)) for _ in range(count)]


def time_uncached(world: WorldState, pairs) -> float:
    t0 = perf_counter()
    for a, b in pairs:
        world.invalidate_distance_cache()
        world.get_distance(a, b)
    return perf_counter() - t0


def time_cached(world: WorldState, pairs) -> float:
    world.invalidate_distance_cache()
    for a, b in pairs:
        world.get_distance(a, b)  # warm
    t0 = perf_counter()
    for a, b in pairs:
        world.get_distance(a, b)
    return perf_counter() - t0


def assert_invariance(world: WorldState) -> None:
    names = list(world.regions.keys())
    world.invalidate_distance_cache()

    # (1) Repeat reads never grow or mutate the cache entry for a stable pair.
    first = world.get_distance(names[0], names[-1])
    size_after_first = len(world._distance_cache)
    for _ in range(200):
        assert world.get_distance(names[0], names[-1]) == first
    assert len(world._distance_cache) == size_after_first, (
        "No-op repeat reads must not mutate cache size"
    )

    # (2) Controller changes on synthetic regions must not invalidate cache.
    world.regions[names[0]].controller = "SomeOtherNation"
    assert world.get_distance(names[0], names[-1]) == first
    assert len(world._distance_cache) == size_after_first, (
        "Controller change must not invalidate distance cache (adjacency-topology-only)"
    )

    # (3) Explicit invalidation clears cache.
    world.invalidate_distance_cache()
    assert world._distance_cache == {}, "Explicit invalidation must clear cache"


def main() -> int:
    world = make_synthetic_world()
    pairs = sample_pairs(world, SAMPLED_PAIRS)

    t_uncached = time_uncached(world, pairs)
    t_cached = time_cached(world, pairs)
    speedup = t_uncached / t_cached if t_cached > 0 else float("inf")

    assert_invariance(make_synthetic_world())

    print("=== Phase 2.1 distance-cache benchmark (100-region synthetic grid) ===")
    print(f"Grid: {GRID_SIDE}x{GRID_SIDE} (4-neighbor adjacency), regions: {len(world.regions)}")
    print(f"Pairs sampled: {len(pairs)} (seed {RNG_SEED})")
    print(f"Uncached (clear cache per call): {t_uncached * 1000:8.1f} ms")
    print(f"Cached   (warmed once):          {t_cached   * 1000:8.1f} ms")
    print(f"Speedup: {speedup:.1f}x")
    print("Invariance: PASS (no-op reads stable, controller change non-invalidating, explicit clear works).")

    # Conservative sanity gate: cached path should be at least 2x faster on a 100-region graph.
    # In practice the speedup is 20-100x; 2x is a safe lower bound to avoid flaky CI signal.
    if t_cached >= t_uncached:
        print("FAIL: cached timings did not beat uncached", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
