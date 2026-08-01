"""AI-6c — the client surfaces (docs/AI_INTENT_SPEC.md §4.6b, §11.1
Stage F; landing record §19).

Three §4.6b remainders, each pinned here:
- THIRD-PARTY WARS reach the war panel: `build_active_wars` previously
  dropped every war France was not in (war_status.py's own France
  filter), so "let them bleed while France rearms" was unreadable on
  the HUD. The new `foreign_wars` section carries sides, duration, the
  Stage D stated reason (court knowledge — diplomacy has no fog) and
  the two leaders' exhaustion fogged to PARTIAL+ exactly like the
  France-war rows.
- A WAR'S REASON is carried and shown wherever the war appears (§4.6's
  fifth deliverable): France's own rows now surface the instance's
  `stated_reason` stamp.
- THE COURTING SURFACE (the Stage C deferral, owner AI-6c): the three
  D5 instrument verbs as honest-availability wizard chips whose gates
  MIRROR the executor's own refusals — a chip the click would refuse
  is a lie.
"""

from pathlib import Path

import pytest

from backend.game_logic.diplomacy import (
    declare_war,
    get_available_diplomatic_actions,
)
from backend.game_logic.war_status import build_active_wars
from backend.models.world_state import WorldState

REPO_ROOT = Path(__file__).resolve().parents[1]
SCENARIO_PATH = (REPO_ROOT / "godot-client" / "project-sovereign"
                 / "assets" / "maps" / "europe_1805.json")
SCRIPTS = (REPO_ROOT / "godot-client" / "project-sovereign" / "scripts")


@pytest.fixture(scope="module")
def world1805():
    return WorldState.from_scenario(str(SCENARIO_PATH))


@pytest.fixture()
def world(world1805):
    return WorldState.from_dict(world1805.to_dict())


def _chips(world, nation):
    actions = get_available_diplomatic_actions(world, nation)
    return {a["action"]: a for a in actions
            if a["action"] in ("sponsor_design", "buy_off_design",
                               "guarantee_nation")}


# ═══════════════════ THIRD-PARTY WARS ON THE PANEL ═════════════════════════


class TestForeignWars:
    def test_boot_board_has_no_foreign_wars(self, world):
        """Every 1805 boot war folds into the France-containing
        Third-Coalition instance — the section boots empty."""
        data = build_active_wars(world)
        assert data["foreign_wars"] == []

    def test_a_third_party_war_appears_with_sides_and_reason(self, world):
        declare_war(world, "Sweden", "Denmark")
        war = next(
            instance for instance in world.war_instances.values()
            if isinstance(instance, dict)
            and instance.get("ended_turn") is None
            and "Sweden" in (instance.get("active_participants") or []))
        war["stated_reason"] = "The Sound United"
        data = build_active_wars(world)
        rows = data["foreign_wars"]
        assert len(rows) == 1
        row = rows[0]
        assert row["attackers"] == ["Sweden"]
        assert row["defenders"] == ["Denmark"]
        assert row["stated_reason"] == "The Sound United"
        assert isinstance(row["duration"], int)
        assert "attackers_display" in row and "defenders_display" in row

    def test_france_wars_never_leak_into_the_section(self, world):
        data = build_active_wars(world)
        for row in data["foreign_wars"]:
            assert "France" not in row["attackers"]
            assert "France" not in row["defenders"]

    def test_ended_wars_drop_from_the_section(self, world):
        declare_war(world, "Sweden", "Denmark")
        for instance in world.war_instances.values():
            if (isinstance(instance, dict)
                    and "Sweden" in (
                        instance.get("active_participants") or [])):
                instance["ended_turn"] = int(world.current_turn)
        data = build_active_wars(world)
        assert data["foreign_wars"] == []

    def test_exhaustion_is_fogged_like_the_france_rows(self, world):
        """The war's EXISTENCE is court knowledge; the armies' state is
        military intel — PARTIAL+ or None, the standing panel doctrine."""
        declare_war(world, "Sweden", "Denmark")
        data = build_active_wars(world)
        row = data["foreign_wars"][0]
        for key in ("attacker_exhaustion", "defender_exhaustion"):
            assert row[key] is None or isinstance(row[key], int)

    def test_panel_gd_renders_the_section(self):
        """The XR-1 wiring scrape (the test_godot_dtype_wired idiom): the
        panel script consumes `foreign_wars` and builds the rows."""
        source = (SCRIPTS / "war_status_panel.gd").read_text(
            encoding="utf-8")
        assert 'data.get("foreign_wars"' in source
        assert "_add_foreign_war_row" in source
        assert "FOREIGN WARS" in source


# ═══════════════════ THE WAR'S REASON, SHOWN ═══════════════════════════════


class TestStatedReason:
    def test_france_rows_carry_the_stage_d_stamp(self, world):
        target = None
        for row in build_active_wars(world)["wars"]:
            if row.get("status") == "war" and row.get("war_instance_id"):
                target = row
                break
        assert target is not None
        instance = world.war_instances[target["war_instance_id"]]
        instance["stated_reason"] = "The Hanoverian Prize"
        refreshed = build_active_wars(world)["wars"]
        row = next(r for r in refreshed
                   if r.get("war_instance_id")
                   == target["war_instance_id"])
        assert row["stated_reason"] == "The Hanoverian Prize"

    def test_rows_without_a_stamp_read_empty(self, world):
        for row in build_active_wars(world)["wars"]:
            if row.get("status") == "war":
                assert row.get("stated_reason", "") == ""

    def test_detail_popup_renders_the_line(self):
        source = (SCRIPTS / "war_detail_popup.gd").read_text(
            encoding="utf-8")
        assert 'w.get("stated_reason"' in source
        assert "Casus belli" in source


# ═══════════════════ THE COURTING SURFACE (WIZARD CHIPS) ═══════════════════


class TestInstrumentChips:
    def _pacify(self, world, nation):
        key = world._make_diplo_key("France", nation)
        if world.diplomatic_states.get(key) == "WAR":
            world.diplomatic_states[key] = "PEACE"
        world.invalidate_bloc_members_cache()

    def test_peace_court_gets_all_three_chips(self, world):
        chips = _chips(world, "Prussia")
        assert set(chips) == {"sponsor_design", "buy_off_design",
                              "guarantee_nation"}
        for chip in chips.values():
            assert chip["dp_cost"] == 1

    def test_sponsor_available_and_names_the_bargain(self, world):
        chip = _chips(world, "Prussia")["sponsor_design"]
        assert chip["available"] is True
        assert chip["aim"], "the chip must carry the design's aim"
        assert chip["amount"] == 200

    def test_buyoff_names_its_price_honestly(self, world):
        """Boot France holds 800g; Prussia's price is 300 + 12 x weight —
        the chip must show the price AND the refusal in the same breath
        the executor would."""
        from backend.game_logic.instruments import compute_buyoff_price
        chip = _chips(world, "Prussia")["buy_off_design"]
        price = compute_buyoff_price(world, "Prussia")
        assert chip["price"] == int(price)
        assert str(int(price)) in chip["display_name"]
        treasury = int(world.nation_gold.get("France", 0))
        if treasury < int(price):
            assert chip["available"] is False
            assert str(treasury) in chip["disabled_reason"]
        else:
            assert chip["available"] is True

    def test_at_war_court_disables_all_three_with_reasons(self, world):
        assert world.is_at_war("France", "Britain")
        chips = _chips(world, "Britain")
        for chip in chips.values():
            assert chip["available"] is False
            assert chip["disabled_reason"]

    def test_standing_guarantee_disables_the_pledge_chip(self, world):
        from backend.game_logic.instruments import pledge_guarantee
        self._pacify(world, "Prussia")
        pledge_guarantee(world, guarantor="France", protected="Prussia")
        chip = _chips(world, "Prussia")["guarantee_nation"]
        assert chip["available"] is False
        assert "already stands" in chip["disabled_reason"]

    def test_own_vassal_never_offered_a_guarantee(self, world):
        """The vassal branch returns before the instrument block — a
        client court gets vassal management, not courtship."""
        assert "Holland" in world.vassals
        actions = get_available_diplomatic_actions(world, "Holland")
        ids = {a["action"] for a in actions}
        assert "guarantee_nation" not in ids
        assert "sponsor_design" not in ids

    def test_no_dp_disables_with_the_cost_named(self, world):
        world.diplomatic_points = 0
        chips = _chips(world, "Prussia")
        for chip in chips.values():
            assert chip["available"] is False
            assert "Insufficient DP" in chip["disabled_reason"]

    def test_deckless_world_shows_only_the_guarantee(self):
        """The two DESIGN verbs are deck-scoped (three permanently dead
        chips on the legacy world would be clutter, not honesty); the
        guarantee is world-agnostic like the D5 record itself."""
        legacy = WorldState()
        nation = next(iter(legacy.enemy_nations))
        chips = _chips(legacy, nation)
        assert "sponsor_design" not in chips
        assert "buy_off_design" not in chips
        assert "guarantee_nation" in chips

    def test_wizard_gd_echoes_the_typed_commands(self):
        """The chip -> terminal echo idiom (UI-6): the wizard maps the
        three action ids to the golden-corpus phrasings."""
        source = (SCRIPTS / "diplomacy_wizard.gd").read_text(
            encoding="utf-8")
        assert '"sponsor_design"' in source
        assert '"buy_off_design"' in source
        assert '"guarantee_nation"' in source
        assert '"buy off " + nation' in source
        assert '"guarantee " + nation' in source
        assert '" against " + aim' in source

    def test_chip_gates_mirror_the_executor(self, world):
        """The honesty contract end-to-end: an AVAILABLE buy-off chip's
        typed command SUCCEEDS through the real executor; a disabled
        one's refusal names the same obstacle."""
        from backend.commands.executor import CommandExecutor
        self._pacify(world, "Prussia")
        world.nation_gold["France"] = 5000
        world.diplomatic_points = 3
        chip = _chips(world, "Prussia")["buy_off_design"]
        assert chip["available"] is True
        executor = CommandExecutor()
        result = executor.execute(
            {"command": {"action": "buy_off_design", "target": "Prussia",
                         "type": "specific"}},
            {"world": world})
        assert result["success"] is True, result.get("message")
