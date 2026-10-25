"""S14f part 2 — the closing re-play's SCENES (October 25, 2026).

The re-measure's 35 rows were sighted at turns 1 … 20 of three 20-turn roads
(`docs/audits/dd_b/{conquest,diplomacy,sea}_2026_10_24/`). Re-playing every
road by hand to each sighting's turn would cost three hours of client time per
run, so the re-play reaches each sighting's STATE by a crafted save instead:
this tool writes the saves into a DD-B run's `saves/` folder BEFORE the
instrument starts (`tools/dd_b_play.py start … --out <run>` creates the folder
with `exist_ok`), and the player loads each from "Load a Campaign…" in the
real client, acts, and reads the frame. Every scene is the sighting's own
board as the ledger describes it (`BUG_FIXES.md` §S14E), built on the shipped
1805 boot with the fewest edits that reproduce it; the manifest `scenes.md`
beside the saves says, per scene, which rows it serves, what to do and what
the fixed game must show.

    .venv/Scripts/python.exe tools/_s14f_replay_scenes.py --out <run>/saves

Each save is round-tripped through `save_manager.load_game` here, so a save
the client cannot load never reaches the instrument.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SCENARIO = REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
sys.path.insert(0, str(REPO))
os.environ.setdefault("LLM_MODE", "mock")
os.environ.setdefault("SOVEREIGN_SEED", "historical")
for _k in ("SOVEREIGN_SCENARIO", "SOVEREIGN_SMOKE_START"):
    os.environ.pop(_k, None)
os.environ["SOVEREIGN_MAP"] = "europe"


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


def _boot():
    from backend.models.world_state import WorldState
    with _quiet():
        return WorldState.from_scenario(str(SCENARIO))


def _fresh(boot):
    from backend.models.world_state import WorldState
    return WorldState.from_dict(json.loads(json.dumps(boot.to_dict(), default=str)))


def _place(w, **where):
    for name, loc in where.items():
        w.get_marshal(name).location = loc
    w._build_marshal_index()
    w.invalidate_active_nations_cache()
    w.calculate_visibility()


def _key(w, a, b):
    return w._make_diplo_key(a, b)


def _set_score(w, a, b, a_view):
    key = _key(w, a, b)
    w.war_scores[key] = a_view if key.split("|")[0] == a else -a_view


def _fight(w, war_id="war_1", **points):
    from backend.game_logic.war_contribution import open_episode
    for nation, pts in points.items():
        ep = open_episode(w, war_id, nation, joined_turn=0, war_sequence=1)
        ep["battle"] = pts
        ep["total"] = pts


def _letter(w, nation, proposal_type, priority=60, war_score=0):
    """An AI court's letter to France, through the AI's own builders and
    transport (`deliver_ai_proposal`), so the mailbox row, the popup and the
    letter-book read exactly what a turn would have delivered."""
    from backend.game_logic import ai_diplomacy as AD
    terms = AD._build_proposal_terms(nation, proposal_type, war_score, w)
    prop = AD._make_proposal(nation, proposal_type, priority, terms, w)
    with _quiet():
        out = AD.deliver_ai_proposal(prop, w)
    return out, terms


# ── the scenes ──────────────────────────────────────────────────────────────

def scene_letters(boot):
    """Rows 18, 20, 23, 27, 28, 29: Prussia's Open Borders letter (a great
    court — the modal: Not Now's lock, the greyed haggle, the effect line),
    Saxony's gift letter (the sum and its direction, the receipt, the Gold
    label), and a lesser court's routine letter (the letter-book's inline
    row)."""
    w = _fresh(boot)
    w.current_turn = 2
    # Saxony's gift: relation < 0 → open_borders + a gold_lump of 10% of her
    # purse (capped 150) — 820 gold gives the sighting's 82.
    w.nation_relations[_key(w, "France", "Saxony")] = -5
    w.nation_gold["Saxony"] = 820
    w.nation_relations[_key(w, "France", "Prussia")] = 5
    w.nation_relations[_key(w, "France", "Portugal")] = 5
    delivered = {}
    for nation, ptype in (("Prussia", "open_borders"), ("Saxony", "friendly_gift"),
                          ("Portugal", "open_borders")):
        out, terms = _letter(w, nation, ptype)
        delivered[nation] = (bool(out), terms.get("type"), terms.get("sweeteners"))
    assert delivered["Prussia"][0], delivered
    assert delivered["Saxony"][0] and delivered["Saxony"][2], delivered
    return w, {"delivered": {k: [v[0], v[1], v[2]] for k, v in delivered.items()}}


def scene_sanctuary(boot):
    """Row 4 (conquest #8): Kutuzov in Moravia, Austria's, Murat at Vienna to
    see him — a peace with Austria shelters the Russians."""
    w = _fresh(boot)
    w.current_turn = 5
    _place(w, Kutuzov="Moravia", Murat="Vienna")
    w.regions["Vienna"].controller = "France"
    w.invalidate_active_nations_cache()
    w.calculate_visibility()
    _set_score(w, "France", "Austria", 45)
    return w, {}


def scene_rump(boot):
    """Row 5 (conquest #10): Hanover a rump — Prussia holds her capital and
    the rest, Osnabruck left; France at peace with Hanover (the Declare War
    chip and the war-purpose card read the rump)."""
    w = _fresh(boot)
    w.current_turn = 11
    for name in w.nation_starting_regions["Hanover"]:
        w.regions[name].controller = "Hanover" if name == "Osnabruck" else "Prussia"
    w.invalidate_active_nations_cache()
    _place(w, Murat="Flanders")
    return w, {}


def scene_beira(boot):
    """Row 6 (conquest #11) and D5: Portugal at war on France's war_1 beside
    Austria and Russia — the whole table; a demand on Portugal (Beira) is
    Portugal's claim of victory, not Austria's."""
    w = _fresh(boot)
    w.current_turn = 6
    inst = w.war_instances["war_1"]
    inst["defenders"].append("Portugal")
    inst["side_by_nation"]["Portugal"] = "defenders"
    inst["active_participants"].append("Portugal")
    w.diplomatic_states[_key(w, "France", "Portugal")] = "WAR"
    w.invalidate_active_nations_cache()
    _fight(w, France=300, Austria=60, Russia=40)
    _set_score(w, "France", "Austria", 40)
    _set_score(w, "France", "Russia", 20)
    return w, {}


def scene_peril(boot):
    """Row 7 (conquest #13) and X31: three corps below 40% morale at Vienna
    beside Kutuzov (38,000, Moravia) in full view — End Turn's army line;
    Soult at full morale beside Buxhowden at 3× — IN PERIL."""
    w = _fresh(boot)
    w.current_turn = 8
    w.regions["Vienna"].controller = "France"
    w.regions["Hungary"].controller = "France"
    _place(w, Ney="Vienna", Lannes="Vienna", Murat="Vienna", Kutuzov="Moravia",
           Soult="Hungary", Buxhowden="Hungary")
    for name in ("Ney", "Lannes", "Murat"):
        w.get_marshal(name).morale = 20
    w.get_marshal("Soult").strength = 10000
    w.get_marshal("Buxhowden").strength = 32000
    w.invalidate_active_nations_cache()
    w.calculate_visibility()
    return w, {}


def scene_detour(boot):
    """Row 22 (conquest #12): Vienna ours, Austria under a truce holding
    Bohemia and Dresden, Soult at Franconia — 'Soult, march to Vienna' must
    ask before it commits the long road through foreign courts."""
    w = _fresh(boot)
    w.current_turn = 19
    w.regions["Vienna"].controller = "France"
    w.regions["Dresden"].controller = "Austria"
    # The sighting's board: Moravia Russian (at war — walkable), so the one
    # lawful road to Vienna runs round Austria's closed frontier through
    # Prussia and Poland.
    w.regions["Moravia"].controller = "Russia"
    w.diplomatic_states[_key(w, "France", "Austria")] = "ARMISTICE"
    # Prussia's soil open to our marches (the conquest player held Open
    # Borders with Berlin by turn 19).
    w.diplomatic_states[_key(w, "France", "Prussia")] = "OPEN_BORDERS"
    w.invalidate_active_nations_cache()
    _place(w, Soult="Franconia", Mack="Bohemia", Napoleon="Vienna", Kutuzov="Podolia")
    from backend.commands.strategic import march_road
    with _quiet():
        road = march_road(w, w.get_marshal("Soult"), "Vienna")
    return w, {"soult_road_to_vienna": road if isinstance(road, list) else str(road)}


def scene_spain(boot):
    """Rows 10, 11 and D8: Spain, our ally at war with Britain, has fought
    (200 points) and slid to relation 2 — her Cabinet page offers the lever;
    a white peace with Britain prices what it does to her."""
    w = _fresh(boot)
    w.current_turn = 11
    w.nation_relations[_key(w, "France", "Spain")] = 2
    _fight(w, France=200, Spain=200, Britain=50)
    _set_score(w, "France", "Britain", 10)
    return w, {}


def scene_mission(boot):
    """Rows 9 and 34: Improve Relations on Austria begun at WAR, the pair now
    at PEACE, the books written (earned, a shock) — the Cabinet row itemises;
    the next tick ends the mission with its reason."""
    w = _fresh(boot)
    w.current_turn = 14
    w.diplomatic_states[_key(w, "France", "Austria")] = "PEACE"
    w.nation_relations[_key(w, "France", "Austria")] = -40
    w.diplomatic_points = 6
    w.active_diplomatic_mission = {
        "type": "IMPROVE_RELATIONS", "target": "Austria", "turns_active": 4,
        "paused": False, "paused_turns": 0, "started_turn": 10,
        "initial_relation": -60, "started_state": "WAR",
        "earned": 32, "shocks": [{"turn": 12, "delta": -15, "kind": "declaration",
                                  "by": "Prussia", "on": "Hanover"}],
        "paused_errand": 0, "paused_starved": 0,
    }
    w.talleyrand_state = "ON_MISSION"
    w.invalidate_active_nations_cache()
    return w, {}


def scene_sea(boot):
    """Rows 13, 14, 15, 31 and D10: the camp staged at Flanders (Soult,
    46,500 men, 2 turns) at war with Britain; Munster ours — the camp tinted
    on the map, the camp-leave line on a march, the Diversion's price, the
    Ireland road on the war card, the war title's floor."""
    from backend.game_logic import naval as NV
    w = _fresh(boot)
    w.current_turn = 6
    m = w.get_marshal("Soult")
    m.location = "Flanders"
    m.strength = 46500
    m.strategic_order = None
    _place(w, Napoleon="Picardy")
    NV.get_fleet(w, "France")["camp_turns"] = 2
    w.regions["Munster"].controller = "France"
    w.invalidate_active_nations_cache()
    w.calculate_visibility()
    return w, {}


def scene_firststep(boot):
    """Rows 1 and 30: Massena at Bohemia, his road home to Milan through
    Tyrol where Archduke John stands (the deed with its face and price);
    Soult (literal — no avoid-set) at Frankfurt with a standing march to
    Milan whose SECOND step, Munich, Mack holds — the next turn's interrupt
    ("HALTED … awaiting your word"), with the dispatch shown first."""
    w = _fresh(boot)
    w.current_turn = 4
    _place(w, Massena="Bohemia", Soult="Frankfurt", Mack="Munich")
    from backend.commands.executor import CommandExecutor
    from backend.commands.strategic import march_road
    soult = w.get_marshal("Soult")
    with _quiet():
        road = march_road(w, soult, "Milan")
        massena_road = march_road(w, w.get_marshal("Massena"), "Milan")
    ex = CommandExecutor()
    with _quiet():
        out = ex.execute({"command": {"raw_input": "Soult, march to Milan", "marshal": "Soult",
                                      "action": "move", "target": "Milan"},
                          "is_strategic": True, "strategic_type": "MOVE_TO"}, {"world": w})
    return w, {"soult_road": str(road[0]), "massena_road": str(massena_road[0]),
               "soult_order_result": {k: out.get(k) for k in ("success", "message")},
               "soult_now_at": soult.location}


def scene_clock(boot):
    """Row 35 (the sea #13): turn 19, France's latest battle stamped on the
    world at turn 13 while the roster's latest stamp is turn 4 — the quiet
    turns read from the store, not the standing marshals."""
    w = _fresh(boot)
    w.current_turn = 19
    for m in w.marshals.values():
        if m.nation == "France":
            m.last_battle_turn = 4
    store = getattr(w, "last_battle_turn_by_nation", None)
    if isinstance(store, dict):
        store["France"] = 13
    else:
        w.last_battle_turn_by_nation = {"France": 13}
    w.threat_level = 60
    return w, {"store_present_on_to_dict": "last_battle_turn_by_nation" in w.to_dict()}


SCENES = {
    "letters": scene_letters,
    "sanctuary": scene_sanctuary,
    "rump": scene_rump,
    "beira": scene_beira,
    "peril": scene_peril,
    "detour": scene_detour,
    "spain": scene_spain,
    "mission": scene_mission,
    "sea": scene_sea,
    "firststep": scene_firststep,
    "clock": scene_clock,
}


def build(out: pathlib.Path, only=None) -> dict:
    from backend import save_manager as SM
    out.mkdir(parents=True, exist_ok=True)
    boot = _boot()
    record = {}
    for name, fn in SCENES.items():
        if only and name not in only:
            continue
        w, notes = fn(boot)
        path = out / f"replay_{name}.json"
        with _quiet():
            res = SM.save_game(w, f"replay_{name}", filepath=path)
        assert res.get("success"), (name, res)
        with _quiet():
            back = SM.load_game(path)
        assert back.get("success"), (name, back.get("message"))
        record[name] = {"file": path.name, "turn": int(w.current_turn), **notes}
        print(f"{name:>10}: {path.name} turn {w.current_turn} {json.dumps(notes, default=str)[:160]}")
    (out / "scenes.json").write_text(json.dumps(record, indent=1, default=str) + "\n", encoding="utf-8")
    return record


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--only", default="")
    args = ap.parse_args()
    only = {s.strip() for s in args.only.split(",") if s.strip()}
    build(pathlib.Path(args.out).resolve(), only or None)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
