"""SF-AGD-1 "The agendas arm" — regenerate the committed AGD fixture save
(Score Finish Step 5 SR-8b, October 3, 2026; DRIVEN since PC-F85, October 17).

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

PC-F85 (Pre-Deploy S13e part 4): THE BOARD IS DRIVEN, NOT WRITTEN. The first
cut planted a stored France-Prussia score of 100 and back-dated the war by
hand to a six-turn age; the live board computes 30-37 at that age, so the
"measured pair" (carve COUNTER / carve + 6,000 gold ACCEPT) was measured at a
score the game cannot produce. Now the generator stages only what a played
campaign cannot cheaply reach — the declaration, the Tilsit shape (every
other war ended through the engine's own pair resolution), the destroyed
army, Berlin and Silesia, Davout — and then DRIVES SIX END TURNS through the
playtest driver (Mode A: the same `/command` road the client posts, France
passive, every blocking letter declined) so the war's age (the
`war_start_turns` stamp `declare_war` wrote at turn 1), the stored score
(`war_scores`, recomputed by each advance) and the exhaustion are the game's
own. The save is taken at world turn 7: the war is six turns old.

What the drive required: NOTHING. With France passive the six turns left
Posen, Berlin, Silesia, Davout, the Prussian roster and the two live wars
exactly as staged, so no piece is held back by hand; the shape the consumer
test `tests/test_sf_agd1_the_agendas_arm.py::TestTheFixture` pins is ASSERTED
before the save is written, and the generator fails loudly if a future engine
change makes the drive move one (hold it back then, by the smallest honest
means - a hold order on Davout, or `world.capture_region` for a province - and
record it here). What the driven board DOES differ in, honestly: the stored
France-Prussia score is the game's own (30 at the head of world turn 7; the
planted board read 100), the war is six turns old by `declare_war`'s own stamp,
and Prussia's war is its own war instance (PC-F66: a French declaration on
Prussia no longer folds into Britain's coalition war_1), which the arm's script
reads (`tools/playtest_scripts/sf_agd1_tilsit_road.json`).

Deterministic (historical seed, mock parser, the driver's per-turn reseed);
regenerated wholesale, never hand-edited.

    python tools/gen_agd_fixture.py
"""
from __future__ import annotations

import contextlib
import io
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
FIXTURE = ROOT / "tests" / "fixtures" / "playtest_saves" / "fixture_agd_tilsit.json"
SCENARIO = ROOT / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
DRIVER = ROOT / "tools" / "playtest_driver.py"

# PC-F85: the war is six turns old when the arm opens (CA9 row 1's war-age
# term; the IGR-D fixture's age) — SIX end turns driven from the declaration.
DRIVEN_TURNS = 6


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
    """The STAGED board — turn 1, the war just declared, nothing planted that
    a turn's arithmetic owns (no stored score, no hand-set war age)."""
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
        world.nation_gold["France"] = 20000
        world.invalidate_active_nations_cache()
        world.invalidate_bloc_members_cache()
    return world


def drive(stage_path: Path, work: Path) -> Path:
    """PC-F85: end `DRIVEN_TURNS` turns on the staged board through the
    playtest driver (the same in-process `/command` road the arm itself
    plays; France issues no orders, every blocking letter is declined) and
    return the save taken at the head of the next turn."""
    env = dict(os.environ)
    env.update(PYTHONHASHSEED="0", PYTHONPATH=str(ROOT), LLM_MODE="mock")
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "PYTHONIOENCODING", "SOVEREIGN_SEED"):
        env.pop(key, None)
    head = DRIVEN_TURNS + 1          # --save-at snaps BEFORE that loop's end turn
    proc = subprocess.run(
        [sys.executable, str(DRIVER), "--from-save", str(stage_path),
         "--turns", str(head), "--diplomacy", "decline", "--save-at", str(head),
         "--name", "agdgen", "--out", str(work), "--fresh"],
        cwd=str(ROOT), env=env, capture_output=True, text=True, timeout=1800)
    if proc.returncode != 0:
        raise SystemExit("[agd] the drive failed:\n" + proc.stdout[-2000:] + proc.stderr[-2000:])
    return work / "agdgen" / "saves" / f"agdgen_t{head}.json"


def assert_shape(world) -> None:
    """The shape `tests/test_sf_agd1_the_agendas_arm.py::TestTheFixture` pins."""
    from backend.game_logic import formations as F
    assert world.regions["Posen"].controller == "Prussia", world.regions["Posen"].controller
    assert world.regions["Berlin"].controller == "France"
    assert world.regions["Silesia"].controller == "France"
    assert world.marshals["Davout"].location == "Silesia", world.marshals["Davout"].location
    assert not [m.name for m in world.marshals.values() if m.nation == "Prussia"], \
        [m.name for m in world.marshals.values() if m.nation == "Prussia"]
    assert sorted(world.get_nations_at_war_with("France")) == ["Britain", "Prussia"], \
        sorted(world.get_nations_at_war_with("France"))
    row = next(r for r in F.build_formables_payload(world)["formables"]
               if r.get("tag") == "DuchyOfWarsaw")
    terms = {t["text"]: t["met"] for t in row["gate_terms"]}
    assert row["available"] is False and terms[
        "Posen held at the settlement table (currently Prussia-held)"] is False, row


def main() -> int:
    from backend import save_manager as SM
    world = build_world()
    FIXTURE.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="agdgen_") as tmp:
        work = Path(tmp)
        stage = work / "stage.json"
        result = SM.save_game(world, "agd_stage", filepath=stage)
        if not result.get("success"):
            print("[agd] stage save failed:", result.get("message"), file=sys.stderr)
            return 2
        driven_path = drive(stage, work)
        with contextlib.redirect_stdout(io.StringIO()):
            loaded = SM.load_game(driven_path)
        if not loaded.get("success"):
            print("[agd] driven save did not load:", loaded.get("message"), file=sys.stderr)
            return 2
        world = loaded["world"]
    assert_shape(world)
    result = SM.save_game(world, "fixture_agd_tilsit", filepath=FIXTURE)
    if not result.get("success"):
        print("[agd] save failed:", result.get("message"), file=sys.stderr)
        return 2
    pair = world._make_diplo_key("France", "Prussia")
    print(f"[agd] wrote {FIXTURE.relative_to(ROOT)} "
          f"({FIXTURE.stat().st_size // 1024} KB) - world turn {world.current_turn}, "
          f"France-Prussia war age {int(world.current_turn) - int(world.war_start_turns[pair])} "
          f"(stamp {world.war_start_turns[pair]}), stored score {world.war_scores.get(pair)}, "
          f"France gold {world.nation_gold.get('France')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
