"""GE-2 "the client" — the two STAGED saves the ending arms start from.

The Fall's two clocks are not reached by the ambient board inside a
campaign's length (GE-1 measured 0 soil-or-sword Falls in nine 46-turn
runs; the chains Fall came only on seeds where the Emperor happened to be
taken), so the driver arms that must reach them start from a save whose
state is WRITTEN, not played — and says so in its slot name:

  tests/fixtures/playtest_saves/fixture_ge2_soil_or_sword.json
      The 1805 boot with every French province but Brittany handed to
      Austria (a direct controller write). France is at war with the
      coalition from the boot, so the soil clock ticks from the first end
      turn and the Empire falls on the fifth — the R1 arm on the driver.
  tests/fixtures/playtest_saves/fixture_ge2_chains.json
      The 1805 boot with the Emperor taken by Austria on turn 1 (the real
      `capture_marshal` seam, the same road a battlefield capture takes).
      France is at war with Austria from the boot, so the chains clock ticks
      from the first end turn, the captor offers its terms on the clock's
      turns 1, 4 and 7, and — the driver's policy declining every envoy —
      the regency falls on the tenth.

Neither is a measurement of the game's balance: each is a starting state
for the ending's CLIENT surface (the digest's END SCREEN block, the Godot
end screen fed from the same payload), which is what GE-2 owes.

  python tools/gen_ge2_ending_fixtures.py

WHEN TO RE-RUN: a `FORMAT_VERSION` bump, a serialized-field change that
`from_dict` cannot default, or a change to the 1805 scenario's opening.
Commit the JSONs with the change that motivated them.
"""

from __future__ import annotations

import contextlib
import io
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "playtest_saves"
SCENARIO = (REPO_ROOT / "godot-client" / "project-sovereign" / "assets" / "maps"
            / "europe_1805.json")

SOIL = "fixture_ge2_soil_or_sword.json"
CHAINS = "fixture_ge2_chains.json"
KEEP = "Brittany"
CAPTOR = "Austria"


def _boot():
    # The byte-pinned historical boot; the fixture records its seed.
    os.environ.setdefault("SOVEREIGN_SEED", "historical")
    sys.path.insert(0, str(REPO_ROOT))
    from backend.models.world_state import WorldState
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(str(SCENARIO))


def stage_soil_or_sword(world) -> None:
    """France holds Brittany alone; the rest of the homeland is Austria's."""
    for region in list(world.get_nation_regions("France")):
        if region != KEEP:
            world.regions[region].controller = CAPTOR
    world.invalidate_active_nations_cache()
    with contextlib.redirect_stdout(io.StringIO()):
        world.calculate_visibility()


def stage_chains(world) -> None:
    """The Emperor a prisoner of Austria from turn 1 (the real capture seam)."""
    from backend.game_logic import fall
    sovereign = fall.sovereign_of(world, world.player_nation)
    if sovereign is None:
        raise SystemExit("the 1805 boot has no French sovereign to take")
    with contextlib.redirect_stdout(io.StringIO()):
        world.capture_marshal(sovereign, CAPTOR, context="ge2_staged_fixture")
    world.invalidate_active_nations_cache()


def write(world, name: str, slot_name: str) -> Path:
    from backend import save_manager
    FIXTURE_DIR.mkdir(parents=True, exist_ok=True)
    target = FIXTURE_DIR / name
    result = save_manager.save_game(world, slot_name, filepath=target)
    if not result.get("success"):
        raise SystemExit(f"save failed: {result.get('message')}")
    print(f"[ge2 fixtures] wrote {name} ({target.stat().st_size // 1024} KB) — {slot_name}")
    return target


def main() -> int:
    world = _boot()
    stage_soil_or_sword(world)
    write(world, SOIL, "GE-2 staged — the Empire without soil (Brittany alone, at war)")

    world = _boot()
    stage_chains(world)
    write(world, CHAINS, "GE-2 staged — the Eagle in chains (the Emperor taken by Austria, turn 1)")
    print("[ge2 fixtures] done — commit the JSONs under tests/fixtures/playtest_saves/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
