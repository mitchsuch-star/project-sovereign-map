"""GE-3 "The Congress of Paris" — the two STAGED saves the Congress arms
start from (ENDGAME_PLAN §2.8).

The ambient board never reaches the Congress's gate (it ends turn 40 with
France at 4 provinces), and a played reach to 50 titled provinces is GE-V's
measurement, so the two driver arms that must exercise a SITTING start from
a save whose state is WRITTEN, not played — and say so in their slot names:

  tests/fixtures/playtest_saves/fixture_ge3_premature.json
      The 1805 boot, turn 1, with fifteen minor-court provinces handed to
      France by TREATY (a direct controller write + the real treaty title
      record) — exactly 50 titled. Britain, Russia and Austria at war,
      Prussia at peace: two-plus refusers and no preparation. The Premature
      arm summons on its first loop and must LOSE the Congress (§2.8).
  tests/fixtures/playtest_saves/fixture_ge3_pressburg.json
      A post-Pressburg, post-Tilsit board at turn 28 (late summer 1806),
      written through the REAL seams where one exists
      (`set_diplomatic_state`, `capture_region`, `create_vassal_treaty`,
      `congress.note_ratification`, `game_end.record_province_title`):
        * Austria at peace, having ceded Tyrol, Carniola and Croatia by
          treaty on turn 20 (the map has no Venetia — Croatia stands in);
        * Bavaria, Saxony and Hesse French satellites by treaty (loyalty 60;
          Saxony 85, the Kingdom of the Treaty of Posen);
        * Hanover taken on turn 15 and held twelve quiet turns (the
          conquest title back-dated — the court eliminated);
        * Naples taken on turn 15 (Feb 1806), held quiet — and Portugal
          (Junot's march of 1807, brought forward), so London has no
          friendly shore to land on (NV-5: a descent sails for a shore that
          will receive it); the first staging left Lisbon open and Paget's
          landing there ended the shut-out on the sitting's sixth day;
        * Russia at peace (Tilsit, turn 26) and at war with Britain —
          Denmark and Sweden too (Sweden's turn is 1810's, brought
          forward: the second staging left Stockholm a friendly shore and
          Paget's landing there ended the shut-out on the sitting's sixth
          day), so the Continental System shuts 20 of 26 ports against
          London and she has no shore on the Continent that will receive her;
        * Prussia allied to France (Schönbrunn), relation +30 — refusing
          only by its Hanoverian design until the table's price is paid.
      55 titled. The Pressburg arm summons, pays Prussia's price at the
      table, invests in the satellites the courting drains (as a prepared
      player would) and must WIN inside the sitting (§2.8: between turns 33
      and 48).

Neither is a measurement of the played reach (GE-V owns it): each is a
starting state for the Congress's own machinery on the real /command road.

  python tools/gen_ge3_congress_fixtures.py

WHEN TO RE-RUN: a FORMAT_VERSION bump, a serialized-field change that
`from_dict` cannot default, or a change to the 1805 scenario's opening.
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

PREMATURE = "fixture_ge3_premature.json"
PRESSBURG = "fixture_ge3_pressburg.json"
PREMATURE_FROM = ("Hanover", "Denmark", "Portugal", "Sardinia", "Naples",
                  "Saxony", "Hesse")


def _boot():
    os.environ.setdefault("SOVEREIGN_SEED", "historical")
    sys.path.insert(0, str(REPO_ROOT))
    from backend.models.world_state import WorldState
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(str(SCENARIO))


def stage_premature(world) -> None:
    from backend.game_logic import congress, game_end
    need = congress.hold_titled(world)
    for nation in PREMATURE_FROM:
        for region in sorted(world.get_nation_regions(nation)):
            if congress.titled(world)["count"] >= need or region == "Lisbon":
                continue
            world.regions[region].controller = world.player_nation
            game_end.record_province_title(world, region, game_end.TITLE_TREATY,
                                           nation, world.player_nation)
            world.invalidate_active_nations_cache()
    world.diplomatic_points = 5
    with contextlib.redirect_stdout(io.StringIO()):
        world.calculate_visibility()
    assert congress.titled(world)["count"] == need, congress.titled(world)


def _state(world, a, b, state, reason):
    from backend.game_logic.diplomacy import set_diplomatic_state
    with contextlib.redirect_stdout(io.StringIO()):
        set_diplomatic_state(world, a, b, state, reason)


def stage_pressburg(world) -> None:
    from backend.game_logic import congress, game_end, vassal
    player = world.player_nation
    # Pressburg, turn 20 — Austria cedes three provinces and signs.
    world.current_turn = 20
    _state(world, player, "Austria", "PEACE", "ge3_staged_pressburg")
    for region in ("Tyrol", "Carniola", "Croatia"):
        world.regions[region].controller = player
        game_end.record_province_title(world, region, game_end.TITLE_TREATY,
                                       "Austria", player)
    world.invalidate_active_nations_cache()
    congress.note_ratification(world, ["Austria"], True, beaten=["Austria"])
    # Hanover and Naples, taken on turn 15 and held twelve quiet turns.
    world.current_turn = 15
    for region in (sorted(world.get_nation_regions("Hanover")) + ["Naples"]
                   + sorted(world.get_nation_regions("Portugal"))):
        with contextlib.redirect_stdout(io.StringIO()):
            world.capture_region(region, player)
    for region, rec in (world.province_title or {}).items():
        if rec.get("kind") == game_end.TITLE_CONQUEST:
            rec["since"] = 15
    # The satellites by treaty (Bavaria from its ALLIANCE; Saxony and Hesse
    # through open borders first — the treaty road's own requirement).
    world.current_turn = 22
    for name in ("Bavaria", "Saxony", "Hesse"):
        if world.get_diplomatic_state(player, name) == "PEACE":
            _state(world, player, name, "OPEN_BORDERS", "ge3_staged_pressburg")
        with contextlib.redirect_stdout(io.StringIO()):
            result = vassal.create_vassal_treaty(world, player, name)
        assert result.get("success"), (name, result)
        world.vassals[name]["loyalty"] = max(60, int(world.vassals[name].get("loyalty", 0)))
    # Saxony is the Kingdom of the Treaty of Posen (December 1806) — raised
    # to a crown by the Emperor and loyal to 1813 — not a fresh 60-loyalty
    # client: at 60 the courting bled it below the bribe line inside the
    # sitting and London's gold bought it away (measured, 2 of 4 seeds).
    world.vassals["Saxony"]["loyalty"] = 85
    # Tilsit, turn 26 — Russia signs, and turns on London with Denmark and
    # (allied to us at Schönbrunn) Prussia.
    world.current_turn = 26
    _state(world, player, "Russia", "PEACE", "ge3_staged_tilsit")
    congress.note_ratification(world, ["Russia"], True, beaten=["Russia"])
    # Prussia, allied to us, stays OUT of London's war: an ally at war with
    # Britain makes any French peace with London an alliance conflict (the
    # fourth staging measured the peace lever refused for exactly that).
    for name in ("Russia", "Denmark", "Sweden"):
        _state(world, name, "Britain", "WAR", "ge3_staged_continental_system")
    _state(world, player, "Prussia", "ALLIANCE", "ge3_staged_schonbrunn")
    # The System's reach (Fontainebleau 1807, Schönbrunn 1809, brought
    # forward): every continental court that would still HOST a British army
    # (`naval.is_expedition_host` — an ally, or a friend at 25+) closes its
    # harbours to London. The third staging left Austria a host; Paget came
    # ashore on the Adriatic on the sitting's sixth day and took titled
    # Carniola and Croatia on the seventh. An undefended ENEMY beach is still
    # open to her (NV-5 rank 2) — the arm does not close that.
    from backend.game_logic import naval
    for nation in sorted(set(world.get_active_nations()) - {"Britain"}):
        rec = naval.get_fleet(world, nation) or {}
        if rec.get("island"):
            continue
        if naval.is_expedition_host(world, "Britain", nation):
            if world.get_diplomatic_state(nation, "Britain") not in ("PEACE",):
                _state(world, nation, "Britain", "PEACE", "ge3_staged_system")
            world.nation_relations[world._make_diplo_key(nation, "Britain")] = 0
    world.nation_relations[world._make_diplo_key(player, "Prussia")] = 30
    # Pressburg and Tilsit ended the WHOLE war, not France's pair alone: the
    # first staging left Austria at war with Bavaria and the Kingdom of Italy
    # (the boot's cascade pairs) and the driver arm watched Milan and Munich
    # fall on the summons turn. Every French satellite and ally makes its
    # peace with both courts too.
    bloc = [n for n in world.get_bloc_members(player) if n != player]
    for court in ("Austria", "Russia"):
        for member in sorted(bloc):
            if world.get_diplomatic_state(court, member) in ("WAR", "ARMISTICE"):
                _state(world, court, member, "PEACE", "ge3_staged_pressburg")
    # The summer of 1806.
    world.current_turn = 28
    world.threat_by_target[player] = 50
    world.diplomatic_points = 5
    world.nation_gold[player] = max(8000, int(world.nation_gold.get(player, 0)))
    world.invalidate_active_nations_cache()
    with contextlib.redirect_stdout(io.StringIO()):
        world.calculate_visibility()
    view = congress.titled(world)
    assert view["count"] >= congress.hold_titled(world), view
    assert congress.summon_refusal(world) is None, congress.summon_refusal(world)


def write(world, name: str, slot_name: str) -> Path:
    from backend import save_manager
    FIXTURE_DIR.mkdir(parents=True, exist_ok=True)
    target = FIXTURE_DIR / name
    result = save_manager.save_game(world, slot_name, filepath=target)
    if not result.get("success"):
        raise SystemExit(f"save failed: {result.get('message')}")
    print(f"[ge3 fixtures] wrote {name} ({target.stat().st_size // 1024} KB) — {slot_name}")
    return target


def main() -> int:
    world = _boot()
    from backend.game_logic import congress
    stage_premature(world)
    write(world, PREMATURE, "GE-3 staged — the Premature summons (exactly 50 titled, turn 1)")

    world = _boot()
    stage_pressburg(world)
    for court in congress.great_powers(world):
        row = congress.answer(world, court)
        print(f"  {court}: {row['stance']} ({row.get('by')}) — {row.get('reason')} | "
              f"{congress.price(world, court, row).get('text')}")
    write(world, PRESSBURG, "GE-3 staged — after Pressburg and Tilsit (turn 28, 55 titled)")
    print("[ge3 fixtures] done — commit the JSONs under tests/fixtures/playtest_saves/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
