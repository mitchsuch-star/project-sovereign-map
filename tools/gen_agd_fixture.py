"""SF-AGD-1 "The agendas arm" — regenerate the committed AGD fixture save
(Score Finish Step 5 SR-8b, October 3, 2026).

    tests/fixtures/playtest_saves/fixture_agd_tilsit.json

The TILSIT board SF-M's probe stands on (`tools/_score_probes.py::
agendas_c4_tilsit`, which builds it from `tests/test_igr_d_carve_completable.py
::_beaten_prussia`): France at war with Prussia ALONE, six turns into the war,
Prussia's field army destroyed and Berlin and Silesia in French hands — with
ONE difference, and it is the point: POSEN IS STILL PRUSSIAN, and Davout
stands beside it in Silesia. The arm (`tools/playtest_scripts/
sf_agd1_tilsit_road.json`) takes Posen in play — so the Duchy of Warsaw's
formables gate flips to met DURING the run — and then carves the Duchy
through the settlement table's own clicks to the Proclamation.

Deterministic (historical seed, mock parser); regenerated wholesale, never
hand-edited.

    python tools/gen_agd_fixture.py
"""
from __future__ import annotations

import contextlib
import io
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
FIXTURE = ROOT / "tests" / "fixtures" / "playtest_saves" / "fixture_agd_tilsit.json"
SCENARIO = ROOT / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"


def _honest_peace(world, a: str, b: str) -> None:
    """A peace the engine itself would record: the pair resolved inside its
    war instance (a raw state write left it active, and an end-turn step
    re-opened the war — measured on the first draft) and the war's data
    cleaned, then the state set."""
    from backend.game_logic.diplomacy import cleanup_war_end, set_diplomatic_state
    from backend.game_logic.settlement_helpers import resolve_pair_to_resolved
    pair = world._make_diplo_key(a, b)
    resolve_pair_to_resolved(world, pair)
    cleanup_war_end(world, pair)
    set_diplomatic_state(world, a, b, "PEACE", "fixture")


def build_world():
    os.environ.setdefault("LLM_MODE", "mock")
    from backend.game_logic.diplomacy import declare_war
    from backend.models.world_state import WorldState

    with contextlib.redirect_stdout(io.StringIO()):
        world = WorldState.from_scenario(str(SCENARIO), seed="historical")
        declare_war(world, "France", "Prussia")
        # The Tilsit shape: Prussia's war, and Britain's (below); Russia, Austria
        # and the rest at peace (the TILSIT probe's own reason — a Russian
        # corps walking into Posen in the transit turn).
        # Each peace carries the truce floor a real settlement writes (RS-1 /
        # PC15-D4's PAIR_EXIT_TRUCE_FLOOR_TURNS): a raw state write records
        # no fresh peace, and an ally's offensive cascade (Bavaria's boot war
        # on Austria) re-broke it on the first end turn — measured.
        from backend.game_logic.settlement_third_party import PAIR_EXIT_TRUCE_FLOOR_TURNS
        cooldowns = getattr(world, "armistice_cooldowns", None)
        if cooldowns is None:
            cooldowns = world.armistice_cooldowns = {}
        for nation in list(world.get_active_nations()):
            if nation in ("France", "Prussia", "Britain"):
                continue
            if world.get_diplomatic_state("France", nation) in ("WAR", "ARMISTICE"):
                _honest_peace(world, "France", nation)
                cooldowns[world._make_diplo_key("France", nation)] = int(
                    PAIR_EXIT_TRUCE_FLOOR_TURNS)
        # ...and the board takes Tilsit's own shape (July 1807): the Franco-
        # Prussian war, and BRITAIN'S war still running (the Duchy of Warsaw
        # was carved from Prussia alone while the British war went on — IGR-D's
        # gate Q2(a)); every other war ends, so it holds across an end turn
        # (the IGR-D fixture never advanced one): France's allies' cascaded
        # wars on Prussia (France cannot make a separate peace past an ally
        # still fighting Prussia — the proposal confirm refuses it), and every
        # satellite's or ally's war on a court France has made peace with
        # (the lord answers for its satellites: the Kingdom of Italy's boot war
        # on Austria dragged France back in on the first end turn — measured).
        satellites = set((world.vassals or {}).keys())
        nations = sorted(world.get_active_nations())
        for i, a in enumerate(nations):
            for b in nations[i + 1:]:
                if world.get_diplomatic_state(a, b) not in ("WAR", "ARMISTICE"):
                    continue
                if "Britain" in (a, b):
                    continue
                if "Prussia" in (a, b) and ({a, b} - {"Prussia"}) <= ({"France"} | satellites):
                    continue
                _honest_peace(world, a, b)
                cooldowns[world._make_diplo_key(a, b)] = int(PAIR_EXIT_TRUCE_FLOOR_TURNS)
        # Six turns into the war (CA9 row 1's war-age term, the IGR-D fixture's age).
        pair = world._make_diplo_key("France", "Prussia")
        world.war_start_turns[pair] = int(world.current_turn) - 6
        # Prussia's field army is destroyed (tombstoned at the ONE seam).
        for name in [m.name for m in world.marshals.values() if m.nation == "Prussia"]:
            world.destroy_marshal(name, cause="battle", victor="France")
        # Berlin and Silesia in French hands; POSEN STILL PRUSSIAN.
        for name in ("Berlin", "Silesia"):
            world.regions[name].controller = "France"
        world.regions["Berlin"].garrison_strength = 0
        assert world.regions["Posen"].controller == "Prussia"
        # Davout beside Posen.
        davout = world.marshals["Davout"]
        davout.location = "Silesia"
        davout.strategic_order = None
        world.war_scores[pair] = 100
        world.nation_gold["France"] = 20000
        world.invalidate_active_nations_cache()
        world.invalidate_bloc_members_cache()
    return world


def main() -> int:
    from backend import save_manager as SM
    world = build_world()
    FIXTURE.parent.mkdir(parents=True, exist_ok=True)
    result = SM.save_game(world, "fixture_agd_tilsit", filepath=FIXTURE)
    if not result.get("success"):
        print("[agd] save failed:", result.get("message"), file=sys.stderr)
        return 2
    print(f"[agd] wrote {FIXTURE.relative_to(ROOT)} "
          f"({FIXTURE.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
