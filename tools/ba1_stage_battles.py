"""Row BA "the battle in acts" — the staged battles the client walk shoots
(BA-1: ten field battles; BA-2: the order of battle, our own dispositions, a
square, five garrison assaults and three bombardments — twenty-two scenes).

Every payload here is the REAL one: the 1805 board (`europe_1805.json`), corps
placed by hand where the scene needs them, and the engagement fought through
the real attack road (`CommandExecutor._execute_attack`), whose result carries
the tableau's payload with its script (`battle_diorama` -> `payload["script"]`,
backend/game_logic/battle_script.py; a garrison assault's and a standalone
bombardment's are backend/game_logic/siege_diorama.py's, on the same key, with
`payload["kind"]` saying which table to lay).

    .venv/Scripts/python.exe tools/ba1_stage_battles.py
    .venv/Scripts/python.exe tools/ba1_stage_battles.py --out <dir> --only ulm_full

Each scene tries ambient seeds in order (`random.seed(k)`: a world nobody
serves keeps the dice its caller pins — WS-11) and keeps the FIRST one whose
battle shows what the scene is for; the seed and the reason are written to
`manifest.json` beside the payloads, so a frame can be traced to its battle.

Written to docs/audits/ba1_client/payloads/ by default. Display evidence only:
nothing here is read by the game.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
SCENARIO = ROOT / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
DEFAULT_OUT = ROOT / "docs" / "audits" / "ba1_client" / "payloads"
SEEDS_TRIED = 400


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


def _board():
    from backend.commands.executor import CommandExecutor
    from backend.models.world_state import WorldState
    with _quiet():
        world = WorldState.from_scenario(str(SCENARIO), seed="historical")
        executor = CommandExecutor()
    return world, executor


def _place(world, **where):
    for name, region in where.items():
        world.marshals[name].location = region


def _war(world, a, b):
    world.diplomatic_states[world._make_diplo_key(a, b)] = "WAR"


def _support(world, name, lead):
    """An order the game already has: `name` is ordered to support `lead`."""
    from backend.models.marshal import StrategicOrder
    world.marshals[name].strategic_order = StrategicOrder(
        command_type="SUPPORT", target=lead, target_type="marshal",
        started_turn=int(world.current_turn),
        original_command=f"{name}, support {lead}",
        issued_turn=int(world.current_turn))


def _beats(payload, kind=None, act=None):
    out = []
    for block in ((payload or {}).get("script") or {}).get("acts") or []:
        if act and block.get("act") != act:
            continue
        for beat in block.get("beats") or []:
            if kind is None or beat.get("kind") == kind:
                out.append(beat)
    return out


def _fought(payload, side):
    return [c for c in ((payload or {}).get(side) or {}).get("contingents") or []
            if c.get("status") not in ("failed_arrive", "refused", "out_of_reach")]


# ── the scenes ──────────────────────────────────────────────────────────────
# stage(world, executor) -> (attacker, target), or None when this seed's
# prelude did not leave the board the scene needs;
# wanted(payload, result) -> the reason the battle is kept, or "".

def _stage_ulm(world, executor):
    """The board as the campaign opens: Mack in Swabia, six French corps in
    the four provinces round him. Ney attacks."""
    return "Ney", "Mack"


def _want_ulm(payload, result):
    if (payload.get("script") or {}).get("form") != "full":
        return ""
    if payload.get("register") != "triumph":
        return ""
    marched = _beats(payload, "arrive")
    # BA-2: three seats a side — the lead and his two wings march on the
    # table, and the rest of the army stands in reserve behind them.
    reserve = int((payload.get("attacker") or {}).get("reserve_count", 0) or 0)
    if len(marched) < 2 or reserve < 1 or not _beats(payload, "break") \
            or not _beats(payload, "absent"):
        return ""
    if any(b.get("how") == "captured" for b in _beats(payload, "break")):
        return ""   # Mack taken with his army is its own picture; this one is the rout
    return (f"a great battle won: {len(marched)} corps march to the guns as the wings, "
            f"{reserve} more in reserve, Soult awaits orders, the enemy's line broken")


def _want_capitulation(payload, result):
    taken = [b for b in _beats(payload, "break") if b.get("how") == "captured"]
    if not taken:
        return ""
    return taken[0]["text"]


def _want_last_hour(payload, result):
    late = [b for b in _beats(payload, "arrive") if b.get("late") and "score" in b]
    if not late:
        return ""
    return (f"{late[0]['actor']} comes up at the last hour "
            f"({late[0]['score']} against a bar of {late[0]['bar']})")


def _stage_flank(world, executor):
    """Two attacks on Swabia in one turn: Lannes goes in first from
    Franche-Comte, then Ney from the Rhineland: the second comes in on a flank."""
    with _quiet():
        executor._execute_attack(world.marshals["Lannes"], "Mack", world,
                                 {"world": world, "executor": executor})
    mack = world.marshals.get("Mack")
    ney = world.marshals.get("Ney")
    if (mack is None or mack.strength <= 0 or mack.location != "Swabia"
            or getattr(mack, "captured_by", "") or ney.location != "Rhineland"):
        return None
    return "Ney", "Mack"


def _want_flank(payload, result):
    flank = _beats(payload, "flank")
    if not flank:
        return ""
    return flank[0]["text"]


def _stage_enemy_comes(world, executor):
    """Davout, from Munich, attacks Kutuzov in the Tyrol; Buxhowden stands in
    Bohemia beside the field, ordered to support Kutuzov: the enemy's corps
    comes up unseen. (An Austrian corps cannot be staged for this: the
    court's doctrine holds the Archduke John's best march, 67, under his bar
    of 70 — the Hofkriegsrat's slowness is the game's, not the tool's.)"""
    _place(world, Davout="Munich", Kutuzov="Tyrol", Buxhowden="Bohemia",
           ArchdukeJohn="Vienna", ArchdukeCharles="Vienna",
           Bernadotte="Lorraine", Massena="Franche-Comte", Murat="Lorraine",
           Lannes="Lorraine")
    _support(world, "Buxhowden", "Kutuzov")
    return "Davout", "Kutuzov"


def _want_enemy_comes(payload, result):
    hidden = [b for b in _beats(payload, "arrive") if b.get("concealed")]
    if not hidden:
        return ""
    return f"{hidden[0]['actor']} comes up unseen and is turned up on arrival"


def _stage_ordinary(world, executor):
    """Lannes alone against the Archduke John in the Tyrol; nobody near."""
    _place(world, Lannes="Munich", Bernadotte="Lorraine", Massena="Franche-Comte",
           ArchdukeCharles="Vienna", Murat="Lorraine")
    return "Lannes", "ArchdukeJohn"


def _want_ordinary(payload, result):
    if (payload.get("script") or {}).get("form") != "brief":
        return ""
    return f"an ordinary exchange ({payload.get('outcome', '')}): the brief form"


def _stage_defeat(world, executor):
    """The enemy's turn: Mack falls on Bernadotte in Franconia, the Archduke
    John in the Tyrol beside it."""
    return "Mack", "Bernadotte"


def _want_defeat(payload, result):
    if payload.get("player_side") != "defender" or payload.get("register") != "defeat":
        return ""
    return "a defeat on the defence: the player's line on the left, beaten"


def _stage_observed(world, executor):
    """Two courts' war in full sight: Kutuzov against Hohenlohe in Silesia."""
    _war(world, "Russia", "Prussia")
    silesia = world.get_region("Silesia")
    beside = sorted(silesia.adjacent_regions)[0]
    _place(world, Kutuzov=beside)
    world.update_intel_from_battle("Silesia", int(world.current_turn))
    return "Kutuzov", "Hohenlohe"


def _want_observed(payload, result):
    if payload.get("player_side"):
        return ""
    return "another court's battle, seen in full: the observer's register"


def _stage_hangs(world, executor):
    """Davout against the Archduke John in the mountains, nobody near."""
    _place(world, Davout="Munich", Bernadotte="Lorraine", Massena="Franche-Comte",
           ArchdukeCharles="Vienna", Murat="Lorraine", Lannes="Lorraine")
    return "Davout", "ArchdukeJohn"


def _want_hangs(payload, result):
    if not _beats(payload, "stand"):
        return ""
    return "neither line gives way: the day hangs"


def _stage_four(world, executor):
    """Ulm with the whole Austrian army in Swabia: the Archdukes John and
    Charles beside Mack, and Schwarzenberg and Hiller commissioned from the
    pool. Four corps a side on the table, the French reserve behind: the
    deepest line the table seats."""
    from backend.game_logic.recruitment import commission_marshal, find_candidate
    world.nation_gold["Austria"] = int(world.nation_gold.get("Austria", 0)) + 20000
    pool = world.manpower_pools.setdefault("Austria", {})
    pool["infantry"] = int(pool.get("infantry", 0)) + 80000
    with _quiet():
        for name in ("Schwarzenberg", "Hiller"):
            commission_marshal(world, "Austria", find_candidate(world, "Austria", name))
    _place(world, ArchdukeJohn="Swabia", ArchdukeCharles="Swabia",
           Schwarzenberg="Swabia", Hiller="Swabia")
    return "Ney", "Mack"


def _want_four(payload, result):
    """BA-2: three seats a side (the centre and two wings) and the rest in
    reserve — both sides seat three and BOTH keep corps behind the line."""
    if len(_fought(payload, "attacker")) != 3 or len(_fought(payload, "defender")) != 3:
        return ""
    reserve = [int((payload.get(side) or {}).get("reserve_count", 0) or 0)
               for side in ("attacker", "defender")]
    if not all(reserve):
        return ""
    return (f"three corps a side on the table, {reserve[0]} and {reserve[1]} more in reserve "
            f"({payload.get('outcome', '')})")


def _stage_guns(world, executor):
    """Marmont's guns, commissioned and ordered to support Ney, fire first."""
    from backend.game_logic.recruitment import commission_marshal, find_candidate
    world.nation_gold["France"] = int(world.nation_gold.get("France", 0)) + 5000
    with _quiet():
        commission_marshal(world, "France", find_candidate(world, "France", "Marmont"))
    _place(world, Marmont="Rhineland")
    _support(world, "Marmont", "Ney")
    return "Ney", "Mack"


def _want_guns(payload, result):
    if not _beats(payload, "battery"):
        return ""
    return "a supporting battery fires before the assault"


# ── Row BA, BA-2: the walls, the guns, the plan and the board ──────────────

def _garrison(world, region, men, *, detachment=False, fortified=False):
    walls = world.get_region(region)
    walls.garrison_strength = int(men)
    walls.garrison_detachment = bool(detachment)
    if fortified:
        walls.buildings.append({"type": "fortification", "damaged": False})


def _stage_assault_held(world, executor):
    """Ney, from Bohemia, storms Vienna: the capital's garrison of 25,000 and
    no corps in it."""
    _place(world, Ney="Bohemia")
    return "Ney", "Vienna"


def _want_assault(fate, extra=""):
    def wanted(payload, result):
        if payload.get("kind") != "assault" or payload.get("fate") != fate:
            return ""
        if extra and not payload.get(extra):
            return ""
        return f"a garrison assault: the wall {fate} ({payload.get('banner', '')})"
    return wanted


def _stage_assault_stormed(world, executor):
    """Vienna held by 6,000: the assault carries the wall and the city falls."""
    _garrison(world, "Vienna", 6000)
    _place(world, Ney="Bohemia")
    return "Ney", "Vienna"


def _stage_assault_occupied(world, executor):
    """Vienna held by 6,000 under a fortress: the wall is carried and the
    occupation begins."""
    _garrison(world, "Vienna", 6000, fortified=True)
    _place(world, Ney="Bohemia")
    return "Ney", "Vienna"


def _stage_assault_capitulated(world, executor):
    """A detachment of 3,000 in Vienna, assaulted at more than four to one:
    it lays down its arms."""
    _garrison(world, "Vienna", 3000, detachment=True)
    _place(world, Ney="Bohemia")
    return "Ney", "Vienna"


def _stage_assault_on_ours(world, executor):
    """The enemy's turn: Mack, from Artois, storms Paris — our own garrison."""
    _place(world, Mack="Artois")
    return "Mack", "Paris"


def _want_assault_on_ours(payload, result):
    if payload.get("kind") != "assault" or payload.get("player_side") != "defender":
        return ""
    return f"the enemy storms our garrison: {payload.get('banner', '')}"


def _marmont(world):
    from backend.game_logic.recruitment import commission_marshal, find_candidate
    world.nation_gold["France"] = int(world.nation_gold.get("France", 0)) + 5000
    with _quiet():
        commission_marshal(world, "France", find_candidate(world, "France", "Marmont"))
    _place(world, Marmont="Rhineland")


def _stage_bombard(world, executor):
    """Marmont's guns, in the Rhineland, bombard Mack in Swabia: the
    cannonade alone."""
    _marmont(world)
    return "Marmont", "Mack"


def _want_bombard(payload, result):
    if payload.get("kind") != "bombardment" or payload.get("significant"):
        return ""
    if any(c.get("bystander") for c in (payload.get("defender") or {}).get("contingents") or []):
        return ""
    return "a bombardment: a link by default, the cannonade alone"


def _stage_bombard_works(world, executor):
    """Mack behind light field works: one salvo brings them down to nothing."""
    _marmont(world)
    mack = world.marshals["Mack"]
    mack.fortified = True
    mack.defense_bonus = 0.10
    return "Marmont", "Mack"


def _want_bombard_works(payload, result):
    if payload.get("kind") != "bombardment" or not payload.get("significant"):
        return ""
    works = _beats(payload, "works")
    if not works or int(works[0].get("new", 1)) > 0:
        return ""
    return "a bombardment that levels the works: it opens by itself"


def _stage_bombard_ours(world, executor):
    """Lannes stands in Swabia with Mack as Marmont's guns open on him: our
    own corps is caught under our own fire."""
    _marmont(world)
    _place(world, Lannes="Swabia")
    return "Marmont", "Mack"


def _want_bombard_ours(payload, result):
    ours = [b for b in _beats(payload, "bystander") if b.get("ours")]
    if payload.get("kind") != "bombardment" or not ours:
        return ""
    return ours[0]["text"]


def _stage_dispositions(world, executor):
    """The enemy's turn: Mack falls on Bernadotte in Franconia, who stands
    behind field works on the defensive."""
    from backend.models.marshal import Stance
    bernadotte = world.marshals["Bernadotte"]
    bernadotte.fortified = True
    bernadotte.defense_bonus = 0.16
    bernadotte.stance = Stance.DEFENSIVE
    return "Mack", "Bernadotte"


def _want_dispositions(payload, result):
    plan = [b for b in _beats(payload, "plan") if b.get("side") == "defender"]
    if payload.get("player_side") != "defender" or not plan:
        return ""
    return plan[0]["text"]


def _stage_square(world, executor):
    """Murat's horse, from Munich, rides at the Archduke John in the Tyrol,
    who has formed square."""
    _place(world, Murat="Munich", Bernadotte="Lorraine", Massena="Franche-Comte",
           ArchdukeCharles="Vienna", Lannes="Lorraine", Davout="Lorraine")
    world.marshals["ArchdukeJohn"].square_formation = True
    return "Murat", "ArchdukeJohn"


def _want_square(payload, result):
    if not _beats(payload, "square"):
        return ""
    return _beats(payload, "square")[0]["text"]


def _stage_two_a_side(world, executor):
    """Davout and Lannes against Kutuzov and Buxhowden in the Tyrol: two corps
    a side — a lead and one wing each."""
    _place(world, Davout="Munich", Lannes="Munich", Kutuzov="Tyrol", Buxhowden="Tyrol",
           ArchdukeJohn="Vienna", ArchdukeCharles="Vienna", Bernadotte="Lorraine",
           Massena="Franche-Comte", Murat="Lorraine")
    return "Davout", "Kutuzov"


def _want_two_a_side(payload, result):
    if len(_fought(payload, "attacker")) != 2 or len(_fought(payload, "defender")) != 2:
        return ""
    if any(int((payload.get(side) or {}).get("reserve_count", 0) or 0)
           for side in ("attacker", "defender")):
        return ""
    return f"two corps a side: a lead and a wing each ({payload.get('outcome', '')})"


SCENES = {
    "ulm_full": (_stage_ulm, _want_ulm),
    "the_capitulation": (_stage_ulm, _want_capitulation),
    "last_hour": (_stage_ulm, _want_last_hour),
    "the_flank": (_stage_flank, _want_flank),
    "enemy_comes": (_stage_enemy_comes, _want_enemy_comes),
    "ordinary_brief": (_stage_ordinary, _want_ordinary),
    "defeat_defending": (_stage_defeat, _want_defeat),
    "observed_full": (_stage_observed, _want_observed),
    "the_day_hangs": (_stage_hangs, _want_hangs),
    "the_reserve": (_stage_four, _want_four),
    "the_guns": (_stage_guns, _want_guns),
    # BA-2
    "two_a_side": (_stage_two_a_side, _want_two_a_side),
    "our_dispositions": (_stage_dispositions, _want_dispositions),
    "square_and_horse": (_stage_square, _want_square),
    "assault_held": (_stage_assault_held, _want_assault("held")),
    "assault_stormed": (_stage_assault_stormed, _want_assault("stormed", "region_conquered")),
    "assault_occupied": (_stage_assault_occupied, _want_assault("stormed", "sub_banner")),
    "assault_capitulated": (_stage_assault_capitulated, _want_assault("capitulated")),
    "assault_on_ours": (_stage_assault_on_ours, _want_assault_on_ours),
    "bombard_link": (_stage_bombard, _want_bombard),
    "bombard_levels": (_stage_bombard_works, _want_bombard_works),
    "bombard_ours": (_stage_bombard_ours, _want_bombard_ours),
}


def fight(name: str, ambient: int):
    stage, wanted = SCENES[name]
    world, executor = _board()
    random.seed(ambient)
    staged = stage(world, executor)
    if staged is None:
        return None, "", {"message": "the prelude did not leave the board the scene needs"}
    attacker, target = staged
    with _quiet():
        result = executor._execute_attack(
            world.marshals[attacker], target, world, {"world": world, "executor": executor})
    payload = result.get("battle_diorama") if isinstance(result, dict) else None
    if not isinstance(payload, dict):
        return None, "", result
    return payload, wanted(payload, result), result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--only", nargs="*", default=[])
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    manifest_path = out / "manifest.json"
    manifest = {}
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except ValueError:
            manifest = {}
    failed = []
    for name in (args.only or list(SCENES)):
        if name not in SCENES:
            print(f"unknown scene: {name}")
            return 2
        kept = None
        last_message = ""
        for ambient in range(SEEDS_TRIED):
            payload, reason, result = fight(name, ambient)
            if payload is None:
                last_message = str((result or {}).get("message", ""))[:200]
                continue
            if reason:
                kept = (ambient, payload, reason)
                break
        if kept is None:
            failed.append(name)
            print(f"  {name}: NOT STAGED in {SEEDS_TRIED} seeds ({last_message})")
            continue
        ambient, payload, reason = kept
        text = json.dumps(payload, indent=1, ensure_ascii=False)
        (out / f"{name}.json").write_text(text, encoding="utf-8")
        script = payload.get("script") or {}
        manifest[name] = {
            "staging": " ".join((SCENES[name][0].__doc__ or "").split()),
            "ambient_seed": ambient,
            "shows": reason,
            "kind": payload.get("kind", "battle"),
            "form": script.get("form"),
            "register": payload.get("register"),
            "beats": {b["act"]: len(b["beats"]) for b in script.get("acts") or []},
        }
        print(f"  {name}: seed {ambient} - {reason} "
              f"[{script.get('form')}, {sum(len(b['beats']) for b in script.get('acts') or [])} beats]")
    # a scene this tool no longer stages leaves neither a row nor a payload
    for stale in [name for name in manifest if name not in SCENES]:
        del manifest[stale]
        old = out / f"{stale}.json"
        if old.exists():
            old.unlink()
    manifest_path.write_text(json.dumps(manifest, indent=1, ensure_ascii=False), encoding="utf-8")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
