"""UI-6 Interaction & Heraldry Sweep — behavior gate.

Covers the July 16, 2026 clickability slice (docs/UI_VISUAL_FOUNDATION_SPEC.md
§8-U6):

Backend (real behavior tests):
- ``/diplomatic_ledger`` gains a ``vassals`` section: per player-vassal
  loyalty/autonomy/tribute/forecast plus the SAME honest-availability
  ``actions[]`` rows the F1 wizard consumes (``get_available_diplomatic_actions``
  is the single gate source — chips can never disagree with the executor).
- Foreign satellites are excluded; empty worlds return an empty section;
  hard-stop dialogues flag ``actions_blocked``; every number is ``int``.

Frontend (file/wiring pins, the established test_ui_visual_foundation.py
pattern — GDScript is invisible to pytest, so these pin the contracts the
manual boot-smoke then verifies live):
- VASSALS tab + chips wired in diplomatic_ledger.gd/.tscn and main.gd;
  chip typed-command strings stay byte-identical to the wizard's.
- Region Action Panel exists (layer 26), map region_clicked finally connected.
- Heraldry helpers + flags wired into ledger/wizard/war surfaces.
- Notification rail phosphor glyphs all resolve to real SVGs.
- Top-bar gear button; Generals order chips; _format_number dedupe;
  war-piece two-rank slot math shared by pieces/labels/hitboxes.

Display-only slice (Golden Rule 6): no combat/economy/AI mechanics change.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
GODOT_PROJ = REPO_ROOT / "godot-client" / "project-sovereign"
SCRIPTS = GODOT_PROJ / "scripts"
SCENES = GODOT_PROJ / "scenes"
HERALDRY_DIR = GODOT_PROJ / "assets" / "ui" / "heraldry"
PHOSPHOR_DIR = GODOT_PROJ / "assets" / "ui" / "icons" / "phosphor"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ═══════════════════════════════════════════════════════════════════════════
# Backend: the vassals ledger section
# ═══════════════════════════════════════════════════════════════════════════

@pytest.fixture
def vassal_world():
    from backend.models.world_state import WorldState
    from backend.game_logic.diplomacy import set_diplomatic_state
    from backend.game_logic.vassal import create_vassal_treaty

    world = WorldState()
    set_diplomatic_state(world, "France", "Saxony", "OPEN_BORDERS", "test")
    result = create_vassal_treaty(world, "France", "Saxony")
    assert result.get("success"), result
    return world


def _vassals_section(world):
    from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger
    return build_diplomatic_ledger(world)["vassals"]


class TestVassalsLedgerSection:
    def test_section_shape_and_row_fields(self, vassal_world):
        section = _vassals_section(vassal_world)
        assert section["count"] == 1
        assert section["actions_blocked"] is False
        row = section["rows"][0]
        assert row["name"] == "Saxony"
        for field in (
            "loyalty", "autonomy_level", "tribute", "tribute_rate_pct",
            "loyalty_forecast", "regions", "created_turn", "garrison_bonus",
        ):
            assert isinstance(row.get(field), int), field
        assert row["autonomy_name"] in ("Puppet", "Satellite", "Autonomous")
        assert row["loyalty_trend"] in ("rising", "falling", "stable")
        assert row["contribution"] in ("loyal", "wavering", "disaffected")
        assert isinstance(section["total_tribute"], int)
        assert isinstance(row["granted_regions"], list)

    def test_actions_mirror_wizard_gate_rows(self, vassal_world):
        """The chips' gate rows come from get_available_diplomatic_actions —
        byte-identical to what the F1 wizard renders for the same nation."""
        from backend.game_logic.diplomacy import get_available_diplomatic_actions
        section = _vassals_section(vassal_world)
        row = section["rows"][0]
        expected = get_available_diplomatic_actions(vassal_world, "Saxony")
        assert row["actions"] == expected
        action_ids = [a["action"] for a in row["actions"]]
        assert action_ids == [
            "invest_vassal", "increase_autonomy", "decrease_autonomy",
            "release_vassal", "grant_region_to_vassal",
        ]

    def test_insufficient_dp_disables_chips_honestly(self, vassal_world):
        vassal_world.diplomatic_points = 0
        section = _vassals_section(vassal_world)
        actions = {a["action"]: a for a in section["rows"][0]["actions"]}
        assert not actions["invest_vassal"]["available"]
        assert "DP" in actions["invest_vassal"]["disabled_reason"]
        assert not actions["release_vassal"]["available"]

    def test_foreign_satellites_excluded(self, vassal_world):
        """A vassal whose lord is not the player never rows on the tab."""
        vassal_world.vassals["Spain"] = {
            "lord": "Britain", "loyalty": 50, "autonomy": 1,
            "path": "treaty", "created_turn": 1, "tribute_rate": 0.75,
            "regions": [],
        }
        section = _vassals_section(vassal_world)
        names = [r["name"] for r in section["rows"]]
        assert "Spain" not in names
        assert names == ["Saxony"]

    def test_no_vassals_returns_empty_section(self):
        from backend.models.world_state import WorldState
        section = _vassals_section(WorldState())
        assert section["rows"] == []
        assert section["count"] == 0
        assert section["total_tribute"] == 0

    def test_hard_stop_dialogue_flags_actions_blocked(self, vassal_world):
        vassal_world.dialogue_manager.is_hard_stop = lambda: True
        section = _vassals_section(vassal_world)
        assert section["actions_blocked"] is True
        # get_available_diplomatic_actions returns [] under a hard stop —
        # the tab shows the section-level notice instead of dead chips.
        assert section["rows"][0]["actions"] == []

    def test_garrison_lever_counted_in_forecast(self, vassal_world):
        """VP-D1 single source: a lord corps in the vassal capital adds the
        flat garrison bonus to the next-turn forecast."""
        from backend.game_logic.vassal import GARRISON_LOYALTY_BONUS
        base = _vassals_section(vassal_world)["rows"][0]
        assert base["garrison_present"] is False

        ney = vassal_world.get_marshal("Ney")
        assert ney is not None
        ney.location = base["capital"]
        garrisoned = _vassals_section(vassal_world)["rows"][0]
        assert garrisoned["garrison_present"] is True
        assert garrisoned["garrison_bonus"] == GARRISON_LOYALTY_BONUS
        assert (
            garrisoned["loyalty_forecast"]
            == base["loyalty_forecast"] + GARRISON_LOYALTY_BONUS
        )

    def test_subsidy_term_counted_in_forecast(self, vassal_world):
        """Review fix UI6-VAS-1: the standing gold_per_turn treaty clause
        (+1 per 100g, process_vassal_loyalty step 3) is a KNOWABLE
        steady-state term — the forecast must include it."""
        base = _vassals_section(vassal_world)["rows"][0]
        assert base["subsidy_bonus"] == 0

        vassal_world.active_treaties["France-Saxony-subsidy"] = {
            "type": "gold_subsidy",
            "nations": ["France", "Saxony"],
            "clauses": [{
                "type": "gold_per_turn", "from": "France",
                "to": "Saxony", "amount": 300,
            }],
        }
        subsidized = _vassals_section(vassal_world)["rows"][0]
        assert subsidized["subsidy_bonus"] == 3
        assert (
            subsidized["loyalty_forecast"] == base["loyalty_forecast"] + 3
        )

    def test_forecast_single_source_with_pipeline(self, vassal_world):
        """F7 drift-lock: the shared forecast helper must agree with what
        process_vassal_loyalty actually applies in a battle-free turn."""
        from backend.game_logic.vassal import (
            forecast_vassal_loyalty, process_vassal_loyalty,
        )
        vassal_world.battles_this_turn = []
        predicted = forecast_vassal_loyalty(vassal_world, "France", "Saxony")
        before = vassal_world.vassals["Saxony"]["loyalty"]
        process_vassal_loyalty(vassal_world)
        after = vassal_world.vassals["Saxony"]["loyalty"]
        assert after - before == predicted["forecast"]

    def test_ledger_and_wizard_trend_agree(self, vassal_world):
        """Review fix UI6-VAS-2: the wizard preview's trend arrow and the
        ledger tab's trend derive from the SAME forecast. With a garrison
        pushing the net positive, both must say 'rising' — the old
        autonomy-only wizard trend said 'falling' for this exact vassal."""
        from backend.game_logic.diplomacy import get_diplomatic_preview
        row = _vassals_section(vassal_world)["rows"][0]
        ney = vassal_world.get_marshal("Ney")
        ney.location = row["capital"]

        row = _vassals_section(vassal_world)["rows"][0]
        preview = get_diplomatic_preview(vassal_world, "Saxony")
        assert preview["vassal_loyalty_trend"] == row["loyalty_trend"]
        assert row["loyalty_forecast"] > 0
        assert row["loyalty_trend"] == "rising"

    def test_grip_effective_gains_mirror_executor(self, vassal_world):
        """Review fix UI6-R2: the chip terms render backend-derived gains —
        which must equal the executor's own int(gain * mult) math."""
        from backend.game_logic.vassal import INVEST_LOYALTY_GAIN
        from backend.models.authority import get_authority_lever_multiplier
        row = _vassals_section(vassal_world)["rows"][0]
        mult = get_authority_lever_multiplier(vassal_world, "France")
        assert row["invest_gain"] == int(INVEST_LOYALTY_GAIN * mult)
        assert row["autonomy_up_gain"] == int(10 * mult)
        assert row["autonomy_down_loss"] == 15
        assert row["gains_blunted"] == (mult < 1.0)

    def test_warning_bands_and_recovery_hint(self, vassal_world):
        rows = {}
        for loyalty, expected in ((50, ""), (30, "warning"), (15, "urgent"), (5, "critical")):
            vassal_world.vassals["Saxony"]["loyalty"] = loyalty
            row = _vassals_section(vassal_world)["rows"][0]
            rows[loyalty] = row
            assert row["warning"] == expected, loyalty
        # The grip-aware hint rides exactly the warning bands (loyalty < 40).
        assert rows[50]["recovery_hint"] == ""
        for loyalty in (30, 15, 5):
            assert rows[loyalty]["recovery_hint"] != ""

    def test_contribution_tiers_match_vs4_thresholds(self, vassal_world):
        from backend.game_logic.vassal import (
            CONTRIBUTION_DISAFFECTED_BELOW, CONTRIBUTION_LOYAL_MIN,
        )
        cases = (
            (CONTRIBUTION_LOYAL_MIN, "loyal"),
            (CONTRIBUTION_DISAFFECTED_BELOW, "wavering"),
            (CONTRIBUTION_DISAFFECTED_BELOW - 1, "disaffected"),
        )
        for loyalty, expected in cases:
            vassal_world.vassals["Saxony"]["loyalty"] = loyalty
            row = _vassals_section(vassal_world)["rows"][0]
            assert row["contribution"] == expected, loyalty


# ═══════════════════════════════════════════════════════════════════════════
# Frontend wiring pins (boot-smoke verifies live; these stop silent regressions)
# ═══════════════════════════════════════════════════════════════════════════

class TestVassalsTabWiring:
    def test_scene_has_vassals_tab_button(self):
        assert "VassalsTab" in _read(SCENES / "diplomatic_ledger.tscn")

    def test_ledger_script_wires_tab_and_chips(self):
        src = _read(SCRIPTS / "diplomatic_ledger.gd")
        assert "signal vassal_command" in src
        assert "signal open_diplomacy_for" in src
        assert "signal assess_requested" in src
        assert "KEY_6" in src
        assert "func _render_vassals" in src
        assert "func open_to_vassals" in src
        assert "func refresh_if_open" in src
        assert 'begins_with("vassal_cede:")' in src
        assert 'begins_with("vassal:")' in src

    # The four chip-reachable vassal actions and their typed-command stems.
    _CHIP_ACTION_STEMS = {
        "invest_vassal": '"invest in "',
        "increase_autonomy": '"increase autonomy "',
        "decrease_autonomy": '"decrease autonomy "',
        "release_vassal": '"release "',
    }

    def test_chip_commands_stay_wizard_identical(self):
        """F3 pairing pin: extract the ledger's _vassal_chip_command match
        arms and assert each action id maps to the SAME typed stem the
        wizard's _build_command uses — action/string swaps fail here."""
        ledger = _read(SCRIPTS / "diplomatic_ledger.gd")
        wizard = _read(SCRIPTS / "diplomacy_wizard.gd")
        body = re.search(
            r"func _vassal_chip_command.*?(?=\nfunc |\Z)", ledger, re.DOTALL,
        )
        assert body, "_vassal_chip_command missing"
        arms = dict(re.findall(
            r'"(\w+)":\s*\n\s*return ("[^"]+")', body.group(0),
        ))
        assert set(arms) == set(self._CHIP_ACTION_STEMS)
        for action_id, stem in self._CHIP_ACTION_STEMS.items():
            assert arms[action_id] == stem, (action_id, arms[action_id])
            assert stem in wizard, stem

    def test_main_connects_ledger_signals(self):
        src = _read(SCRIPTS / "main.gd")
        assert "vassal_command.connect(_on_vassal_command)" in src
        assert "open_diplomacy_for.connect(_on_ledger_open_diplomacy_for)" in src
        assert "assess_requested.connect(_on_ledger_assess_requested)" in src
        # Result callback refreshes the ledger in place (reward pipeline pattern)
        assert "func _on_vassal_command_result" in src

    def test_top_bar_routes_ledger_vassals_review(self):
        assert "open_to_vassals" in _read(SCRIPTS / "top_bar.gd")


class TestRegionActionPanel:
    def test_scene_exists_at_layer_26(self):
        src = _read(SCENES / "region_panel.tscn")
        assert "layer = 26" in src
        assert "region_panel.gd" in src

    def test_panel_script_contracts(self):
        src = _read(SCRIPTS / "region_panel.gd")
        assert "signal region_command" in src
        assert "signal negotiate_requested" in src
        # Fog honesty: renders from the map node's own filtered stores.
        for store in ("region_full_data", "region_visibility", "region_marshals"):
            assert store in src, store
        # Context chips: the generic do:<typed command> scheme + wizard/order
        # handoffs, and the full economy verb set the user asked for.
        for meta in ("do:", "negotiate:", "order:"):
            assert meta in src, meta
        for command in ("recruit ", "build watchtower in ",
                        "repair buildings in ", ", attack "):
            assert command in src, command
        for verb in ('"order:scout:', '"order:fortify:', '"order:drill:'):
            assert verb in src, verb

    def test_tactical_state_read_as_flat_bools(self):
        """F4 regression pin (bug hit during the build): the map summary's
        tactical_state carries FLAT bools — there is no "state" key."""
        src = _read(SCRIPTS / "region_panel.gd")
        for key in ("fortified", "retreating", "broken", "drilling"):
            assert f'tactical.get("{key}"' in src, key
        assert 'tactical.get("state"' not in src
        assert 'tactical_state["state"' not in src

    def test_map_summary_carries_chip_gate_keys(self):
        """Backend twin of the F4 pin: the four flat bools the panel gates
        chips on must exist in the player-marshal tactical_state payload."""
        from backend.models.world_state import WorldState
        world = WorldState()
        summary = world.get_game_state_summary()
        found = False
        for region_data in summary["map_data"].values():
            for m in region_data.get("marshals", []):
                tactical = m.get("tactical_state")
                if tactical is None:
                    continue
                found = True
                for key in ("fortified", "retreating", "broken", "drilling"):
                    assert key in tactical, key
        assert found, "no player marshal carried tactical_state"

    def test_build_chips_cover_canonical_building_types(self):
        """Review fix UI6-R1 + the user's 'there are more options' follow-up:
        every backend BUILDING_TYPES key gets a chip def keyed to the
        CANONICAL name (a bare "depot" string never matched anything)."""
        from backend.models.region import BUILDING_TYPES
        src = _read(SCRIPTS / "region_panel.gd")
        for key in BUILDING_TYPES:
            assert f'"{key}"' in src, key
        assert '_region_has_building(data, "depot")' not in src
        # All three recruitable arms get chips.
        for arm in ("infantry", "cavalry", "artillery"):
            assert arm in src, arm

    def test_main_finally_connects_region_clicked(self):
        src = _read(SCRIPTS / "main.gd")
        assert "region_clicked.connect(_on_map_region_clicked)" in src
        assert 'dialog_manager.register("region_panel"' in src
        assert "func _on_region_panel_command" in src
        assert "func _on_region_negotiate_requested" in src
        # Same visibility rule as the war HUD: never over a screen or modal.
        assert "region_panel.close_panel()" in src


class TestHeraldryWiring:
    def test_utils_flag_helpers(self):
        src = _read(SCRIPTS / "utils.gd")
        assert "func nation_flag_path" in src
        assert "func bb_flag" in src
        assert "func apply_flag_icon" in src
        assert 'FLAG_DIR := "res://assets/ui/heraldry/"' in src

    def test_every_roster_nation_has_a_flag(self):
        """The full Utils.NATION_COLORS roster (minus the deliberate
        'Neutral' fallback) ships a flag — the user's 'some flags are
        missing' follow-up added Hanover/Hesse/KingdomOfItaly/Switzerland."""
        src = _read(SCRIPTS / "utils.gd")
        block = re.search(
            r"const NATION_COLORS = \{(.*?)\n\}", src, re.DOTALL,
        )
        assert block, "NATION_COLORS missing"
        nations = re.findall(r'"(\w+)":\s*Color\(', block.group(1))
        assert len(nations) >= 20
        for nation in nations:
            if nation == "Neutral":
                continue
            assert (HERALDRY_DIR / f"{nation}.svg").exists(), nation

    def test_flags_wired_into_surfaces(self):
        assert "Utils.bb_flag" in _read(SCRIPTS / "diplomatic_ledger.gd")
        wizard = _read(SCRIPTS / "diplomacy_wizard.gd")
        assert "Utils.apply_flag_icon" in wizard
        assert "Utils.bb_flag" in wizard
        panel = _read(SCRIPTS / "war_status_panel.gd")
        assert "Utils.nation_flag_path" in panel
        assert "Utils.apply_flag_icon" in panel
        assert "_set_header_flag" in _read(SCRIPTS / "war_detail_popup.gd")


class TestNotificationGlyphs:
    def test_all_mapped_glyphs_resolve_to_real_svgs(self):
        src = _read(SCRIPTS / "notification_bar.gd")
        for const in ("TYPE_ICON_SVGS", "ROUTE_ICON_SVGS"):
            block = re.search(
                rf"const {const} = \{{(.*?)\}}", src, re.DOTALL,
            )
            assert block, const
            names = re.findall(r':\s*"([a-z0-9-]+)"', block.group(1))
            assert names, const
            for name in names:
                assert (PHOSPHOR_DIR / f"{name}.svg").exists(), name

    def test_icon_path_used_at_render(self):
        src = _read(SCRIPTS / "notification_bar.gd")
        assert "func _icon_svg_for" in src
        assert "Utils.ICON_PHOSPHOR" in src


class TestTopBarMenuButton:
    def test_scene_and_script(self):
        assert "MenuBtn" in _read(SCENES / "top_bar.tscn")
        src = _read(SCRIPTS / "top_bar.gd")
        assert "signal menu_clicked" in src
        assert 'gear.svg' in src

    def test_main_toggles_pause_from_gear(self):
        src = _read(SCRIPTS / "main.gd")
        assert "menu_clicked.connect(_on_top_bar_menu_clicked)" in src
        assert "func _on_top_bar_menu_clicked" in src


class TestGeneralsOrderChips:
    def test_chips_and_signal(self):
        src = _read(SCRIPTS / "marshal_management.gd")
        assert "signal order_command" in src
        for meta in ("order:fortify:", "order:unfortify:", "order:drill:"):
            assert meta in src, meta
        # Never for a captured/broken/retreating marshal.
        assert 'm.get("captured", false)' in src

    def test_main_routes_order_chips_through_reward_pipeline(self):
        src = _read(SCRIPTS / "main.gd")
        assert "order_command.connect(_on_reward_command)" in src

    def test_talleyrand_assess_chip(self):
        assert "talleyrand_assess" in _read(SCRIPTS / "diplomatic_ledger.gd")
        assert "Talleyrand, assess our situation" in _read(SCRIPTS / "main.gd")


class TestSharedHelpersDedupe:
    def test_format_number_single_source(self):
        """The four screens delegate to Utils.format_number — the hand-rolled
        comma loop lives ONLY in utils.gd now."""
        for name in ("marshal_management.gd", "strategic_ledger.gd",
                     "dispatch_view.gd", "notification_bar.gd",
                     "diplomatic_ledger.gd"):
            src = _read(SCRIPTS / name)
            assert "count % 3" not in src, name
        assert "count % 3" in _read(SCRIPTS / "utils.gd")

    def test_bb_chip_helpers_in_utils(self):
        src = _read(SCRIPTS / "utils.gd")
        assert "func bb_icon" in src
        assert "func bb_button_chip" in src
        # marshal_management delegates instead of re-authoring the pattern.
        assert "Utils.bb_button_chip" in _read(SCRIPTS / "marshal_management.gd")


class TestReviewFixPins:
    """Regression pins for the UI-6 adversarial-review fixes."""

    def test_chip_terms_derive_from_payload(self):
        """UI6-R2/F5: chip terms render backend fields (dp_cost/gold_cost/
        invest_gain/autonomy_up_gain), never re-hardcoded constants."""
        src = _read(SCRIPTS / "diplomatic_ledger.gd")
        for field in ('a.get("dp_cost"', 'a.get("gold_cost"',
                      'v.get("invest_gain"', 'v.get("autonomy_up_gain"',
                      'v.get("autonomy_down_loss"', 'v.get("gains_blunted"'):
            assert field in src, field
        assert "200g" not in src
        assert "+10 loyalty" not in src

    def test_blunted_disclosure_matches_executor_phrase(self):
        """The chip's spiral-band disclosure reuses the executor's own
        phrasing so copy and result message can never disagree."""
        phrase = "faltering grip blunts the gesture"
        assert phrase in _read(SCRIPTS / "diplomatic_ledger.gd")
        vassal_py = (REPO_ROOT / "backend" / "game_logic" / "vassal.py").read_text(
            encoding="utf-8")
        assert phrase in vassal_py

    def test_scenario_path_gets_its_own_label(self):
        """UI6-R1: the 1805 boot vassals carry path='scenario' — never
        mislabel them as conquests, never show the authoring Turn 1."""
        src = _read(SCRIPTS / "diplomatic_ledger.gd")
        assert "client state of the Empire" in src
        assert '"treaty":' in src and '"conquest":' in src
        assert 'path != "scenario"' in src

    def test_chip_double_click_latch(self):
        """UI6-R2: one shared in-flight latch guards every chip pipeline and
        clears in every result callback (including the failure path)."""
        src = _read(SCRIPTS / "main.gd")
        assert "var _chip_command_in_flight := false" in src
        assert src.count("or _chip_command_in_flight:") >= 3
        assert src.count("_chip_command_in_flight = true") >= 3
        assert src.count("_chip_command_in_flight = false") >= 3

    def test_gear_closes_screens_before_pause(self):
        """UI6-GD-1: the ESC invariant — pause never opens over a screen."""
        src = _read(SCRIPTS / "main.gd")
        body = re.search(
            r"func _on_top_bar_menu_clicked.*?(?=\nfunc )", src, re.DOTALL,
        )
        assert body, "_on_top_bar_menu_clicked missing"
        assert "close_all_screens()" in body.group(0)
        assert body.group(0).index("close_all_screens()") < body.group(0).index("open_menu()")

    def test_objection_resolution_refreshes_open_screens(self):
        """UI6-R4: a chip-raised objection resolves AFTER the chip's own
        result callback — the resolution must refresh open info surfaces."""
        src = _read(SCRIPTS / "main.gd")
        assert "func _refresh_open_info_screens" in src
        body = re.search(
            r"func _on_objection_response.*?(?=\nfunc )", src, re.DOTALL,
        )
        assert body and "_refresh_open_info_screens()" in body.group(0)

    def test_subsidy_named_on_vassal_card(self):
        """The subsidy forecast term is a named lever on the card, like the
        garrison — a forecast the player cannot explain is noise."""
        assert "subsidy_bonus" in _read(SCRIPTS / "diplomatic_ledger.gd")


class TestWarPieceRankSpread:
    def test_two_rank_slot_math_shared(self):
        src = _read(SCENES / "map_renderer_base.gd")
        assert "WAR_PIECE_RANK_DEPTH" in src
        assert "func _marshal_slot_offset_2d" in src
        # Single source: pieces, labels, and hitboxes all read the 2d helper.
        assert src.count("_marshal_slot_offset_2d(i,") >= 2
        # 1-2 co-located pieces keep the legacy flat line (byte-stable look).
        assert "if count <= 2:" in src
