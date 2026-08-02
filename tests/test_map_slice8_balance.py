"""Map Slice 8 — 1805 scale/balance validation pins.

Owns the behavior tests for the Slice 8 balance items
(docs/MAP_IMPLEMENTATION_PLAN.md Slice 8 scope):

  * DEF-6 — the London<->Flanders cross-Channel link: Britain cannot walk
    into France unopposed (the Flanders Channel depot blocks the P4.5
    walk-in; entry requires grinding a 12k garrison), and an
    undefended-London rush is intercepted by the differentiated 25k major
    capital garrison (3 assaults to collapse under the >=5,000 floor).
  * Knife-edge (a) — Charles authored exactly AT Carniola's 54k home
    supply cap: `total <= cap` is inclusive, so at-cap = zero attrition
    and one man more attrits.
  * Knife-edge (b) — France|Spain relation authored exactly AT the
    ALLIANCE threshold 40: gap 0 < 30, the alliance holds indefinitely.
  * Adige standoff — verified GEOMETRIC, not ratio-stable: Carniola and
    Milan are not adjacent (the only approach runs through Tyrol), and the
    54k/42k = 1.286 ratio sits inside AI mood variance rather than safely
    under the cautious 1.3 threshold. The live smoke observed Charles
    routing to the softer Franconia rear instead — historically consistent
    (Caldiero). The pins below freeze the geometry + the threshold
    constants the deterrent arithmetic rests on.
  * Mack's turn-1 P-1 capture of Bavaria-owned Swabia is deliberate
    invasion mechanics (Austria occupied Bavaria in Sept 1805) — it flips
    Swabia Austrian and ends the authored hostile-soil strain.
"""
from __future__ import annotations

import random
from pathlib import Path

import pytest

from backend.commands.executor import CommandExecutor
from backend.game_logic.turn_manager import TurnManager
from backend.models.world_state import WorldState

SCENARIO_PATH = (
    Path(__file__).resolve().parents[1] / "godot-client" / "project-sovereign"
    / "assets" / "maps" / "europe_1805.json"
)


def _load() -> WorldState:
    return WorldState.from_scenario(str(SCENARIO_PATH))


@pytest.fixture(scope="module")
def world1805() -> WorldState:
    """Read-only module world — mutating tests load their own via _load()."""
    return _load()


# ══════════════════════════ DEF-6: the cross-Channel link ══════════════════════════


def test_channel_depot_blocks_p45_walk_in():
    """Moore's live-observed turn-1 walk-in is closed: with the 12k Channel
    depot, P4.5 (undefended capture) can never pick the beach — entry into
    France via the sea link requires a garrison assault (opposed).

    NV-8c (Aug 2, 2026): the Flanders line is cut, so the beach this test
    owns is NORMANDY — the one remaining Channel crossing. Flanders keeps
    its depot (an expedition can still land there over open water).

    NV-9 (Aug 2, review): MUTATION-TESTED and repaired. NV-5 added the
    crossing-gate skip at the head of P4.5, so Normandy was excluded
    before the garrison was ever consulted — this test passed with the
    depot set to ZERO and the DEF-6 behaviour was unpinned. The naval
    layer is therefore neutralised below (France's fleet sunk = the
    crossing is an uncontested ferry) so that the DEPOT is the only thing
    left that can refuse the walk-in, which is what DEF-6 owns."""
    from backend.ai.enemy_ai import EnemyAI

    world = _load()
    moore = world.marshals["Moore"]
    assert moore.location == "London"
    assert world.regions["Normandy"].garrison_strength >= 5000
    assert world.regions["Flanders"].garrison_strength >= 5000

    # Neutralise the naval gate so the depot must do the work alone.
    from backend.game_logic import naval
    naval.get_fleet(world, "France")["ships"] = 0
    assert naval.crossing_allowed(world, "Britain", "London", "Normandy"), (
        "the fixture must leave the crossing OPEN — otherwise the naval "
        "gate answers and the depot is never consulted")

    ai = EnemyAI(CommandExecutor())
    ai._reset_enemy_query_cache(world)
    action = ai._find_undefended_capture(moore, "Britain", world)
    assert action is None or action.get("target") != "Normandy"

    # Provocation control: drop the depot and the SAME scan offers it —
    # so the refusal above is the garrison, demonstrably.
    world.regions["Normandy"].garrison_strength = 0
    ai._reset_enemy_query_cache(world)
    offered = ai._find_undefended_capture(moore, "Britain", world)
    assert offered is not None and offered.get("target") == "Normandy", (
        "the depot-blocks-P4.5 behaviour is no longer provoked by this "
        "fixture — re-derive it before trusting the pin above")


def test_london_rush_intercepted_by_differentiated_garrison():
    """DEF-6 completion pin: a French rush on an undefended London is
    intercepted by the 25k major-capital garrison — the first two assaults
    leave it above the 5,000 collapse floor; capture takes three.

    DEF-5 naval flip (conscious, the pin NV-3 predicted): the Channel is
    now the Royal Navy's — this test's rush needs the sea first, so the RN
    is SUNK here to reach the garrison layer it actually pins. The
    naval-gated refusal itself is pinned in test_naval_channel_gate.py
    (A5); this test keeps owning the GARRISON differentiation."""
    world = _load()
    world.fleets["Britain"]["ships"] = 0  # DEF-5: clear the sea lane
    ney = world.marshals["Ney"]
    # NV-8c: the Flanders line is cut — Normandy is the Channel crossing.
    ney.location = "Normandy"
    ney.strength = 35000
    world.marshals["Moore"].location = "Highlands"  # London left undefended
    world.actions_remaining = 99
    executor = CommandExecutor()
    game_state = {"world": world}

    london = world.regions["London"]
    assert london.garrison_strength == 25000

    assaults = 0
    for _ in range(5):
        result = executor.execute(
            {"command": {"marshal": "Ney", "action": "attack", "target": "London"}},
            game_state,
        )
        assert result.get("success"), result.get("message")
        assaults += 1
        if london.controller == "France":
            break
        # Interception contract: the garrison holds through the first two.
        if assaults <= 2:
            assert london.controller == "Britain"
            assert london.garrison_strength >= 5000

    assert london.controller == "France"
    assert assaults == 3, f"25k major capital must take 3 assaults, took {assaults}"


def test_britain_cannot_take_france_unopposed_over_five_turns():
    """DEF-6 behavior test (seeded live probe, turns 1-5, passive France):
    Paris never falls, and any France-starting province Britain does take
    was entered through a FOUGHT Channel gate — never a free walk.

    DEF-5 naval amendment (August 2, 2026, user-directed): Flanders is no
    longer the sole Britain→France door. The registry gained the short
    London↔Normandy crossing (111px — the historic descent beach) precisely
    so a British landing comes ashore on the Norman coast instead of only
    through the Low Countries, whose Flanders↔Orleanais edge fed straight
    into the French interior. Both beaches carry the same 12,000-man
    Channel depot, so the DEF-6 rule the test actually owns is unchanged
    and now stated generally: whichever beach Britain uses, its garrison
    must have been ground down in combat first."""
    random.seed(20260702)  # AI mood rolls ride the global random module
    world = _load()
    france_start = {
        name for name, region in world.regions.items()
        if region.controller == "France"
    }
    tm = TurnManager(world, CommandExecutor())
    game_state = {"world": world}
    for _ in range(5):
        tm.end_turn(game_state)

    assert world.regions["Paris"].controller == "France"
    british_gains = {
        name for name in france_start
        if world.regions[name].controller == "Britain"
    }
    if british_gains:
        # A landing happened: it came through a Channel beach, and that
        # beach's depot was fought to zero (never a P4.5 walk-in).
        beaches = {"Flanders", "Normandy"}
        taken_beaches = british_gains & beaches
        assert taken_beaches, (
            f"Britain holds French soil {sorted(british_gains)} without "
            f"holding a Channel beach — that is a walk-in, not a landing"
        )
        for beach in taken_beaches:
            assert world.regions[beach].garrison_strength == 0


# ══════════════════════════ knife-edge (a): Charles at the supply cap ══════════════════════════


def test_charles_exactly_at_carniola_home_cap_is_attrition_free():
    """`total <= cap` is inclusive (world_state.process_supply_attrition):
    Charles authored at exactly 54,000 on Carniola (city 40k x hills 0.9
    x 1.5 home bonus) takes zero attrition — and one man more attrits."""
    world = _load()
    charles = world.marshals["ArchdukeCharles"]
    assert charles.location == "Carniola"
    assert charles.strength == 54000
    assert world.regions["Carniola"].supply_capacity == 36000  # base (pre-home-bonus)

    events = world.process_supply_attrition()
    assert not [e for e in events if e.get("marshal") == "ArchdukeCharles"]

    # Meaningfully over the cap -> attrition fires. (A 1-man excess rounds
    # to 0 lost troops and emits nothing — the pinned contract is the
    # inclusive `total <= cap` boundary at exactly 54,000, plus real
    # attrition once the excess is material.)
    charles.strength = 56000
    events = world.process_supply_attrition()
    assert [e for e in events if e.get("marshal") == "ArchdukeCharles"], (
        "2,000 over the home cap must attrit — the boundary is inclusive at 54,000"
    )


# ══════════════════════════ knife-edge (b): France|Spain at the alliance threshold ══════════════════════════


def test_france_spain_alliance_holds_at_exact_threshold():
    """Relation authored exactly 40 = ALLIANCE threshold: gap is 0 (< 30),
    so the auto-downgrade counter never starts — the alliance holds
    indefinitely at the knife edge."""
    from backend.game_logic.diplomacy import check_auto_downgrade

    world = _load()
    key = world._make_diplo_key("France", "Spain")
    assert world.diplomatic_states[key] == "ALLIANCE"
    assert world.nation_relations[key] == 40

    for _ in range(6):
        check_auto_downgrade(world)
    assert world.diplomatic_states[key] == "ALLIANCE"
    assert getattr(world, "turns_below_threshold", {}).get(key, 0) == 0


def test_alliance_erodes_only_30_below_threshold():
    """Contrast pin: the same alliance at relation 10 (gap 30) accrues the
    downgrade counter and collapses after 5 consecutive turns."""
    from backend.game_logic.diplomacy import check_auto_downgrade

    world = _load()
    key = world._make_diplo_key("France", "Spain")
    world.nation_relations[key] = 10
    for _ in range(5):
        check_auto_downgrade(world)
    assert world.diplomatic_states[key] != "ALLIANCE"


# ══════════════════════════ the Adige standoff (verified geometric) ══════════════════════════


def test_adige_standoff_geometry_and_threshold_arithmetic(world1805):
    """Slice 8 verification of record: the standoff is GEOMETRIC. Charles
    (Carniola) cannot reach Massena (Milan) in one move — the corridor runs
    through Tyrol — and the 1.286 ratio is NOT safely under the cautious
    threshold once posture/mood variance applies (base 1.3, +/-10% mood;
    the turn-1 'aggressive' coalition posture subtracts 0.15). The live
    smoke observed Charles routing to the Franconia rear instead —
    historically consistent (Caldiero, Oct 1805). Any future re-authoring
    that makes Carniola<->Milan adjacent silently deletes the standoff."""
    from backend.ai.enemy_ai import EnemyAI

    carniola = world1805.regions["Carniola"]
    assert "Milan" not in carniola.adjacent_regions
    assert "Tyrol" in carniola.adjacent_regions
    assert "Tyrol" in world1805.regions["Milan"].adjacent_regions

    charles = world1805.marshals["ArchdukeCharles"]
    massena = world1805.marshals["Massena"]
    ratio = charles.strength / massena.strength
    assert 1.28 < ratio < 1.30  # 54k / 42k = 1.2857...

    # The deterrent arithmetic the verdict rests on (drift = re-verify):
    assert EnemyAI.ATTACK_THRESHOLDS["cautious"] == 1.3
    assert EnemyAI.MOOD_VARIANCE["cautious"] == 0.10


# ══════════════════════════ Mack / the Ulm opening ══════════════════════════


def test_mack_turn_one_takes_swabia_and_ends_hostile_strain():
    """Deliberate invasion mechanics: Mack stands on Bavaria-owned Swabia at
    war with Bavaria — P-1 (capture current region) flips it Austrian on
    the first enemy phase, ending the authored hostile-soil supply strain
    (Austria occupied Bavaria in September 1805). The Ulm difficulty knob
    stays at the blessed 52k band-bottom (raising Mack re-adds
    hostile-soil bleed only until this capture)."""
    random.seed(20260702)
    world = _load()
    assert world.regions["Swabia"].controller == "Bavaria"
    assert world.marshals["Mack"].strength == 52000

    tm = TurnManager(world, CommandExecutor())
    tm.end_turn({"world": world})

    assert world.regions["Swabia"].controller == "Austria"
    # Home soil now: 40k city cap x 1.5 = 60k >= 52k -> strain over.
    events = world.process_supply_attrition()
    assert not [e for e in events if e.get("marshal") == "Mack"]


# ══════════════════════════ DEF-13: UI-scale mechanism (UI-2, July 12, 2026) ══════════════════════════


def test_def13_ui_scale_mechanism_landed():
    """DEF-13 ('UI-Scale Mini-Pass') was folded into the UI Visual Foundation
    Sweep as UI-2 and LANDED July 12, 2026. The old fixed-HUD baseline pin is
    RETIRED: the command window is now user-resizable (drag grip), and a global
    content_scale_factor scale lives in BOTH the pause-menu Settings slider and
    (UI-2c, July 12) the command window's "Text Size" +/- buttons. This
    replacement pin asserts the *mechanism* exists so a silent removal fails
    loudly (docs/UI_VISUAL_FOUNDATION_SPEC.md §8 U2 / U2c).

    The war-status panel is deliberately NOT part of the resize mechanism, so
    its recorded geometry is still pinned here."""
    root = Path(__file__).resolve().parents[1] / "godot-client" / "project-sovereign"

    # The persistence layer for the user display preferences (footprint + the
    # one global UI/text scale; UI-2c retired the terminal-only text scale).
    ui_settings = (root / "scripts" / "ui_settings.gd").read_text(encoding="utf-8")
    assert "class_name UiSettings" in ui_settings
    for token in ("get_ui_scale", "set_ui_scale", "set_terminal_size"):
        assert token in ui_settings, f"ui_settings.gd missing {token}"

    # The terminal resize mechanism + the global scale wiring (the Text Size
    # buttons step content_scale_factor through _apply_ui_scale).
    main_gd = (root / "scripts" / "main.gd").read_text(encoding="utf-8")
    for token in (
        "content_scale_factor",
        "_apply_terminal_size",
        "_apply_ui_scale",
        "_step_ui_scale",
        "_on_grip_gui_input",
        "resize_grip",
    ):
        assert token in main_gd, f"main.gd missing UI-2 mechanism token {token}"

    # The renderer exposes the post-scale camera-refresh hook (Part 1); true
    # physical-resolution compensation is Part 2. content_scale_factor itself is
    # owned by main.gd, not the renderer.
    renderer = (root / "scenes" / "map_renderer_base.gd").read_text(encoding="utf-8")
    assert "refresh_viewport_scale" in renderer
    assert "content_scale_factor" in main_gd

    # The "Text Size" +/- scale buttons exist in the terminal header (UI-2c).
    main_tscn = (root / "scenes" / "main.tscn").read_text(encoding="utf-8")
    assert '[node name="ScaleDownButton"' in main_tscn
    assert '[node name="ScaleUpButton"' in main_tscn
    assert '[node name="TextSizeLabel"' in main_tscn

    # War-status panel geometry is NOT resizable — still pinned.
    war_tscn = (root / "scenes" / "war_status_panel.tscn").read_text(encoding="utf-8")
    assert "offset_left = -200.0" in war_tscn
    assert "offset_top = -200.0" in war_tscn
