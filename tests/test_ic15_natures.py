"""Row IC, Session 4b (IC-15) - a marshal's nature on every screen, the server half.

"Bold - Careful - To the letter", each with one plain line. ONE table
(`display_names.NATURE_WORDS`), one helper (`nature_of`); the Emperor (the
player) has none; a nature is public, so fogged rows carry it too - but an
enemy row never carries "personality" or "trust".
"""
from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path

import pytest

from backend import display_names as DN
from backend.display_names import NATURE_WORDS, nature_of
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCENARIO = REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
WORDS = {"Bold", "Careful", "To the letter"}


@pytest.fixture(scope="module")
def _snapshot():
    with contextlib.redirect_stdout(io.StringIO()):
        return json.dumps(WorldState.from_scenario(str(SCENARIO)).to_dict(), default=str)


@pytest.fixture
def world(_snapshot):
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_dict(json.loads(_snapshot))


def _all_rows(summary):
    """(kind, row) for every row that names a marshal."""
    for row in summary["marshals"].values():
        yield "player", row
    for row in summary["enemies"].values():
        yield "enemy", row
    for region in summary["map_data"].values():
        for row in region["marshals"]:
            yield ("player_here" if row.get("nation") == "France" else "enemy_here"), row
        for row in region["fogged_forces"]:
            yield "fogged", row


class TestTheTable:

    def test_the_words_and_their_lines(self):
        assert {w for w, _ in NATURE_WORDS.values()} == WORDS
        assert all(line and line[0].isupper() for _, line in NATURE_WORDS.values())
        assert NATURE_WORDS["aggressive"][0] == "Bold"

    def test_the_helper_reads_the_table(self, world):
        ney = world.marshals["Ney"]
        assert nature_of(ney, world) == {"nature": "Bold", "nature_line": NATURE_WORDS["aggressive"][1]}
        assert nature_of(None) == {}

    def test_the_players_emperor_has_none_and_unknown_values_have_none(self, world):
        napoleon = world.marshals["Napoleon"]
        assert nature_of(napoleon, world) == {}
        assert nature_of({"personality": "balanced"}) == {}

    def test_an_enemy_sovereign_reads_through_the_ai_personality(self, world):
        napoleon = world.marshals["Napoleon"]
        world.player_nation = "Austria"
        assert nature_of(napoleon, world)["nature"] == "Bold"

    def test_a_candidate_dict_reads_too(self):
        assert nature_of({"personality": "literal"})["nature"] == "To the letter"

    def test_display_names_keeps_its_old_personality_table(self):
        assert DN.PERSONALITY_DISPLAY["aggressive"] == "Aggressive"


class TestTheSummary:

    def test_the_players_marshal_rows_carry_it_the_emperor_does_not(self, world):
        summary = world.get_filtered_game_state_summary()
        rows = summary["marshals"]
        assert "nature" not in rows["Napoleon"]
        for name, row in rows.items():
            assert row["name"] == name
            if name != "Napoleon":
                assert row["nature"] in WORDS and row["nature_line"]

    def test_every_row_that_names_a_marshal_carries_it(self, world):
        summary = world.get_filtered_game_state_summary()
        seen = set()
        for kind, row in _all_rows(summary):
            seen.add(kind)
            if row.get("name") == "Napoleon" or kind == "player" and row.get("name") == "Napoleon":
                assert "nature" not in row
                continue
            assert row.get("nature") in WORDS, (kind, row)
            assert row.get("nature_line"), (kind, row)
        assert {"player", "enemy", "player_here"} <= seen

    def test_fogged_rows_carry_the_nature_and_nothing_private(self, world):
        from backend.models.intel import PARTIAL
        ney = world.marshals["Ney"]
        # put the player's view of one enemy corps at PARTIAL
        foe = next(m for m in world.marshals.values()
                   if m.nation != world.player_nation and m.strength > 0)
        world.get_region_intel(foe.location).visibility = PARTIAL
        summary = world.get_filtered_game_state_summary()
        fogged = [r for reg in summary["map_data"].values() for r in reg["fogged_forces"]
                  if r["name"] == foe.name]
        assert fogged, "the PARTIAL enemy rides as a fogged row"
        row = fogged[0]
        assert row.get("nature") in WORDS and row.get("nature_line")
        assert set(row) <= {"name", "nation", "strength_band", "fog_level", "nature", "nature_line"}
        enemy = summary["enemies"].get(foe.name)
        assert enemy is None or enemy.get("nature") in WORDS
        assert ney is not None

    def test_no_enemy_row_names_a_personality_or_trust(self, world):
        summary = world.get_filtered_game_state_summary()
        for kind, row in _all_rows(summary):
            if kind in ("enemy", "enemy_here", "fogged"):
                assert "personality" not in row and "trust" not in row, (kind, row)


class TestTheOtherScreens:

    def test_the_generals_identity_carries_it(self, world):
        from backend.game_logic.marshal_overview import build_marshal_overview
        cards = build_marshal_overview(world)
        cards = cards["marshals"] if isinstance(cards, dict) else cards
        ney = next(c for c in cards if c["name"] == "Ney")
        assert ney["nature"] == "Bold" and ney["nature_line"]
        assert ney["personality_description"].startswith("Bold:")
        for card in cards:
            desc = card["personality_description"]
            assert not desc.startswith(("Aggressive:", "Cautious:", "Literal:")), card["name"]

    def test_the_hiring_bench_carries_it(self, world):
        from backend.game_logic.recruitment import build_recruitment_payload
        rows = build_recruitment_payload(world)["candidates"]
        for row in rows:
            if row["personality"] in NATURE_WORDS:
                assert row["nature"] == NATURE_WORDS[row["personality"]][0]
                assert row["nature_line"] == NATURE_WORDS[row["personality"]][1]

    def test_his_temper_uses_the_nature_word(self):
        src = (REPO / "backend" / "game_logic" / "battle_day.py").read_text(encoding="utf-8")
        assert "NATURE_WORDS" in src and "PERSONALITY_DISPLAY" not in src

    def test_the_desk_names_the_nature(self, world):
        from backend.ai.state_desk import _answer_personality
        said = _answer_personality(world, "Ney")
        assert "Bold" in said and "aggressive" not in said.lower()
        roster = _answer_personality(world, "")
        assert "(Bold)" in roster and "(aggressive)" not in roster

    def test_there_is_one_table(self):
        for rel in ("backend/game_logic/marshal_overview.py", "backend/game_logic/recruitment.py",
                    "backend/models/world_state.py"):
            src = (REPO / rel).read_text(encoding="utf-8")
            assert "NATURE_WORDS = " not in src and '"Careful"' not in src.replace(
                "Careful: +20%", ""), rel


class TestTheRepliesCarryIt:
    """Session 4b's own review of the lanes: the objection window and the
    learned rows read the server's word — the client keeps no copy."""

    def test_an_objection_reply_names_his_nature(self, world):
        import backend.main as M
        tactical = M.build_base_response(world, success=False, message="He objects.",
                                         include_popup_passthroughs=False,
                                         marshal="Ney", personality="aggressive")
        assert tactical["nature"] == "Bold"
        strategic = M.build_base_response(world, success=False, message="He objects.",
                                          include_popup_passthroughs=False,
                                          pending_objection=True,
                                          objection={"marshal": "Davout", "personality": "cautious"})
        assert strategic["objection"]["nature"] == "Careful"
        assert "nature" not in strategic, "only where a personality rides"

    def test_a_reply_without_a_personality_gains_nothing(self, world):
        import backend.main as M
        plain = M.build_base_response(world, message="ok", include_popup_passthroughs=False)
        assert "nature" not in plain

    def test_a_learned_row_carries_the_mans_nature(self, world, monkeypatch):
        import backend.main as M
        from backend.game_logic import learned as L
        monkeypatch.setattr(L, "payload", lambda w: {"marshals": {"Mack": {
            "name": "Mack", "court": "Austria", "orders": ["Mack holds Ulm."],
            "learned": "learned last turn", "how": "from your spy's report", "turn": 1}}})
        rows = M._learned_for_wire(world)
        assert rows["marshals"]["Mack"]["nature"] in WORDS


class TestTheBattleTellingSaysIt:

    def test_the_temper_row_is_named_in_his_natures_word(self):
        from backend.game_logic.battle_telling import _temper
        assert _temper("personality (aggressive)") == "bold temper"
        assert _temper("personality (cautious)") == "careful temper"
        assert _temper("personality (literal)") == "temper"
        assert _temper("personality") == "temper"
        assert _temper("bold nature") == "bold temper"
        assert _temper("careful nature") == "careful temper"


class TestTheBattleLinesSayIt:
    """Row IC, Session 4b — the natures' sibling the sweep missed, found
    pressing the screens: the battle's own lines said "(Aggressive: +15%
    attack)" and the report's rows "Personality (aggressive)"; the desk's
    answers said "a literal marshal" and "Cautious marshals"."""

    def test_the_reports_rows_carry_the_natures_word(self):
        from backend.game_logic.battle_report import defense_personality_components
        labels = [r[0] for r in defense_personality_components("cautious", "defensive", True, False)]
        assert labels == ["Careful nature", "Outnumbered (Careful)"], labels
        labels = [r[0] for r in defense_personality_components("aggressive", "aggressive", False, False)]
        assert labels == ["Bold nature"], labels
        labels = [r[0] for r in defense_personality_components("literal", "neutral", False, True)]
        assert labels == ["Immovable (holds to the letter)"], labels

    def test_no_line_of_the_battle_or_the_fortify_says_the_raw_key(self):
        for rel in ("backend/game_logic/combat.py", "backend/game_logic/battle_report.py",
                    "backend/commands/tactical_executor.py", "backend/models/world_state.py"):
            src = (REPO / rel).read_text(encoding="utf-8")
            # (the code that builds a line or a label; a comment may still quote the old words)
            for raw in ('(Aggressive:', '(Cautious:', 'f"Personality (', 'f"Outnumbered ({personality})',
                        'else "Cautious"', '(literal hold)'):
                assert raw not in src, (rel, raw)

    def test_the_charge_the_scout_and_the_dispatch_say_the_natures_word(self):
        """The review of the late edits (Session 4b): the charge refusal and
        its read-back said "not aggressive enough" / "reckless", the scout
        note "Cautious", the dispatch "N more aggressive corps" under "(bold)"."""
        from types import SimpleNamespace

        from backend.commands.parse_preview import _charge_gate
        careful_horse = SimpleNamespace(cavalry=True, is_reckless_cavalry=False, personality="cautious",
                                        in_retreat_recovery=lambda: False, recklessness=0)
        assert _charge_gate(careful_horse) == "only Bold cavalry charge — he is Careful"
        foot = SimpleNamespace(cavalry=False, is_reckless_cavalry=False, personality="aggressive",
                               in_retreat_recovery=lambda: False)
        assert _charge_gate(foot) == "no cavalryman — only Bold cavalry charge"
        for rel, raw in (("backend/commands/combat_executor.py", "not aggressive enough"),
                         ("backend/commands/combat_executor.py", "(aggressive cavalry)"),
                         ("backend/commands/movement_executor.py", 'else "Cautious"'),
                         ("backend/game_logic/dispatch.py", "more aggressive corps")):
            assert raw not in (REPO / rel).read_text(encoding="utf-8"), (rel, raw)

    def test_the_desks_answers_say_the_natures_word(self):
        src = (REPO / "backend" / "ai" / "state_desk.py").read_text(encoding="utf-8")
        assert "literal marshal" not in src and "Cautious marshals" not in src
        assert "1 for a marshal who goes to the letter, or the Emperor" in src


class TestTheSpyPromisesOnlyWhatPlansGive:
    """The written orders exist only while the courts write plans (the seam):
    the button, the dialogue's line and the report promise them only then."""

    @pytest.mark.parametrize("up", [False, True])
    def test_the_spys_words_follow_the_seam(self, world, monkeypatch, up):
        from backend.game_logic import cabinet_rows as CR
        from backend.game_logic import diplomatic_dialogue as DD
        from backend.game_logic import war_plans as WP
        monkeypatch.setattr(WP, "the_courts_follow_a_plan", lambda: up)
        line = CR.plain_rows(world, "France", "Prussia", [{"action": "mission_gather_intel"}])[0]["plain_line"]
        assert ("written orders" in line) is up, line
        assert ("written orders" in DD.mission_effect_text(world, "GATHER_INTEL")) is up
        assert ("written orders" in DD.mission_effect_text(world, "GATHER_INTEL", short=True)) is up

    def test_the_orders_are_promised_only_of_a_court_at_war_with_you(self, world, monkeypatch):
        """IC4b-30: only a court at war with France draws a plan (`war_plans.
        _muster`), so a spy sent to an ally or a neutral finds no written
        orders — every promise of them says whose they can be."""
        from backend.game_logic import cabinet_rows as CR
        from backend.game_logic import diplomatic_dialogue as DD
        from backend.game_logic import war_plans as WP
        monkeypatch.setattr(WP, "the_courts_follow_a_plan", lambda: True)
        line = CR.plain_rows(world, "France", "Prussia", [{"action": "mission_gather_intel"}])[0]["plain_line"]
        assert "from a court at war with you" in line, line
        assert "from a court at war with you" in DD.mission_effect_text(world, "GATHER_INTEL")
        assert "if at war with you" in DD.mission_effect_text(world, "GATHER_INTEL", short=True)
