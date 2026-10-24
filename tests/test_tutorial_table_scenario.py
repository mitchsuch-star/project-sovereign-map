"""S14d part 2 - The Table lesson board (`tutorial_table_1805.json`;
`docs/TABLE_LESSON_SPEC.md` §4, §5, A4).

The board is authored-deterministic like the Danube's. This file pins the
board against its contracts; the first class is the AUTHORING contract
(S14D-X14, October 24, 2026): the keys a lesson board authors - the war's
memory, the stored scores, the purses and cooldowns, the first-open latches,
the opening hints - are documented in `docs/MODDING_FORMAT.md` and their
shapes are gated by `backend.modding.validator._validate_lesson_keys`.
"""


class TestTheAuthoringContract:
    """⟨SF step=pre-deploy S14d · S14D-X14 · pillar=none⟩ The lesson keys have
    a contract: every key the Table authors is documented with its measured
    semantics, the validator checks the shape of each lesson key when it is
    present (a wrong shape is an ERROR, an unknown top-level key is still
    not), and the documented `war_scores` rule - the stored figure is the
    live one - holds on the shipped board."""

    BOARD_NAME = "tutorial_table_1805.json"
    SCENARIOS = ("europe_1805.json", "tutorial_1805.json", "tutorial_table_1805.json")

    # key -> (mutate(data), the exact error path the wrong shape must be
    # reported at). One deliberately wrong shape per lesson key.
    @staticmethod
    def _wrong_shapes():
        def put(key, value):
            def mutate(d):
                d[key] = value
            return mutate

        def ledger_capture(d):
            d["campaign_ledgers"] = {"Austria|France": {"captures": {"France": ["Atlantis"]}}}

        def battle_turn(d):
            d["battle_records"] = {"Austria|France": [{"turn": "three", "winner": "France"}]}

        def decisive_winner(d):
            d["decisive_battles"] = {"Austria|France": [{"turn": 0, "winner": "Britain"}]}

        return {
            "war_exhaustion": (put("war_exhaustion", {"Austria": "sixty"}),
                               "war_exhaustion.Austria"),
            "war_start_turns": (put("war_start_turns", {"France|Austria": -7}),
                                "war_start_turns.France|Austria"),
            "battle_records": (battle_turn, "battle_records.Austria|France[0].turn"),
            "decisive_battles": (decisive_winner,
                                 "decisive_battles.Austria|France[0].winner"),
            "campaign_ledgers": (ledger_capture,
                                 "campaign_ledgers.Austria|France.captures.France[0]"),
            "nation_starting_regions": (put("nation_starting_regions", {"Austria": ["Atlantis"]}),
                                        "nation_starting_regions.Austria[0]"),
            "diplomatic_points": (put("diplomatic_points", "five"), "diplomatic_points"),
            "max_diplomatic_points": (put("max_diplomatic_points", -1), "max_diplomatic_points"),
            "nation_dp": (put("nation_dp", {"Austria": 4.5}), "nation_dp.Austria"),
            "ai_proposal_cooldowns": (put("ai_proposal_cooldowns", {"Bavaria": 6}),
                                      "ai_proposal_cooldowns.Bavaria"),
            "war_scores": (put("war_scores", {"Austria|France": 150}),
                           "war_scores.Austria|France"),
            "first_opens": (put("first_opens", {"nonesuch": 0}), "first_opens.nonesuch"),
            "diplomatic_states": (put("diplomatic_states", {"France|Austria": "WAR"}),
                                  "diplomatic_states.France|Austria"),
            "coordination_tutorial_shown": (put("coordination_tutorial_shown", "yes"),
                                            "coordination_tutorial_shown"),
            "opening_attack_guidance_shown": (put("opening_attack_guidance_shown", 1),
                                              "opening_attack_guidance_shown"),
            "delegation_hint_shown": (put("delegation_hint_shown", "true"),
                                      "delegation_hint_shown"),
            "muster_hint_shown": (put("muster_hint_shown", None), "muster_hint_shown"),
            "commission_hint_shown": (put("commission_hint_shown", []),
                                      "commission_hint_shown"),
        }

    @classmethod
    def _maps(cls):
        from pathlib import Path
        return (Path(__file__).resolve().parents[1]
                / "godot-client" / "project-sovereign" / "assets" / "maps")

    @classmethod
    def _board(cls) -> dict:
        import json
        return json.loads((cls._maps() / cls.BOARD_NAME).read_text(encoding="utf-8"))

    @staticmethod
    def _format_doc() -> str:
        from pathlib import Path
        return (Path(__file__).resolve().parents[1] / "docs" / "MODDING_FORMAT.md").read_text(
            encoding="utf-8")

    @staticmethod
    def _errors(data) -> list:
        from backend.modding.validator import validate_scenario
        return [(e.path, e.message) for e in validate_scenario(data).errors]

    # ── (a) the documentation ────────────────────────────────────────────

    def test_every_top_level_key_of_the_table_board_is_backticked_in_the_format_doc(self):
        doc = self._format_doc()
        missing = [k for k in self._board() if not k.startswith("_") and f"`{k}`" not in doc]
        assert not missing, f"keys the Table authors that MODDING_FORMAT.md never documents: {missing}"

    def test_every_lesson_key_the_validator_gates_is_documented(self):
        from backend.modding.validator import LESSON_KEYS
        doc = self._format_doc()
        missing = [k for k in LESSON_KEYS if f"`{k}`" not in doc]
        assert not missing, f"LESSON_KEYS entries absent from MODDING_FORMAT.md: {missing}"

    def test_the_first_opens_row_names_every_screen_id(self):
        from backend.game_logic.first_open import SCREENS
        row = next(line for line in self._format_doc().split("\n")
                   if line.startswith("| `first_opens` |"))
        missing = [s for s in SCREENS if f"`{s}`" not in row]
        assert not missing, f"first_opens row omits screen ids: {missing}"

    # ── (b) the three shipped scenarios are clean ────────────────────────

    def test_the_validator_reports_no_errors_on_the_three_scenarios(self):
        from backend.modding.validator import validate_scenario
        for name in self.SCENARIOS:
            path = self._maps() / name
            assert path.exists(), f"{name} missing"
            result = validate_scenario(str(path))
            assert not result.errors, (name, [f"{e.path}: {e.message}" for e in result.errors])

    # ── (c) one wrong shape per lesson key ───────────────────────────────

    def test_the_wrong_shape_table_covers_every_lesson_key(self):
        from backend.modding.validator import LESSON_KEYS
        assert set(self._wrong_shapes()) == set(LESSON_KEYS)

    def test_one_deliberately_wrong_shape_per_lesson_key_is_an_error_at_its_path(self):
        misses = []
        for key, (mutate, expected_path) in self._wrong_shapes().items():
            data = self._board()
            mutate(data)
            paths = [p for p, _m in self._errors(data)]
            if expected_path not in paths:
                misses.append((key, expected_path, paths))
        assert not misses, misses

    def test_the_unmutated_board_has_no_lesson_key_error(self):
        # the control for the table above: a wrong shape is the ONLY difference
        assert self._errors(self._board()) == []

    def test_a_block_key_that_is_not_an_object_is_an_error_at_the_key(self):
        for key in ("war_exhaustion", "war_start_turns", "battle_records",
                    "decisive_battles", "campaign_ledgers", "nation_starting_regions",
                    "nation_dp", "ai_proposal_cooldowns", "war_scores", "first_opens",
                    "diplomatic_states"):
            data = self._board()
            data[key] = ["not", "an", "object"]
            assert (key, "Must be an object, got list") in self._errors(data), key

    def test_pair_keys_must_be_two_sorted_known_nations(self):
        cases = {
            "France|Austria": "alphabetically sorted",
            "Austria": "NationA|NationB",
            "Austria|France|Russia": "NationA|NationB",
            "France|France": "itself",
            "Atlantis|France": "Unknown nation",
        }
        for pair, fragment in cases.items():
            data = self._board()
            data["war_scores"] = {pair: 10}
            found = [m for p, m in self._errors(data) if p == f"war_scores.{pair}"]
            assert found and fragment in found[0], (pair, found)

    def test_a_record_naming_a_court_outside_its_pair_is_an_error(self):
        data = self._board()
        row = {"turn": 0, "winner": "France", "attacker": "Russia", "defender": "Austria"}
        data["battle_records"] = {"Austria|France": [row]}
        paths = [p for p, _m in self._errors(data)]
        assert "battle_records.Austria|France[0].attacker" in paths

    def test_a_ledger_credits_a_province_once_and_only_to_the_pair(self):
        data = self._board()
        data["campaign_ledgers"] = {"Austria|France": {
            "captures": {"France": ["Vienna", "Vienna"], "Russia": ["Moravia"]},
            "casualties": {"Austria": -5},
        }}
        paths = [p for p, _m in self._errors(data)]
        assert "campaign_ledgers.Austria|France.captures.France[1]" in paths
        assert "campaign_ledgers.Austria|France.captures.Russia" in paths
        assert "campaign_ledgers.Austria|France.casualties.Austria" in paths

    def test_the_numeric_bounds_are_enforced(self):
        # war exhaustion 0..200 (WAR_EXHAUSTION_MAX), scores -100..100, bool is not an int
        cases = [
            ("war_exhaustion", {"Austria": 201}, "war_exhaustion.Austria"),
            ("war_exhaustion", {"Austria": -1}, "war_exhaustion.Austria"),
            ("war_scores", {"Austria|France": -101}, "war_scores.Austria|France"),
            ("war_scores", {"Austria|France": True}, "war_scores.Austria|France"),
            ("ai_proposal_cooldowns", {"Bavaria|nation": -1}, "ai_proposal_cooldowns.Bavaria|nation"),
            ("ai_proposal_cooldowns", {"Atlantis|nation": 6}, "ai_proposal_cooldowns.Atlantis|nation"),
            ("first_opens", {"cabinet": "now"}, "first_opens.cabinet"),
            ("nation_dp", {"Atlantis": 3}, "nation_dp.Atlantis"),
        ]
        for key, value, path in cases:
            data = self._board()
            data[key] = value
            assert path in [p for p, _m in self._errors(data)], (key, value)

    def test_the_valid_edges_of_those_bounds_are_clean(self):
        data = self._board()
        data["war_exhaustion"] = {"Austria": 0, "France": 200}
        data["war_scores"] = {"Austria|France": -100, "France|Russia": 100}
        data["ai_proposal_cooldowns"] = {"Bavaria|nation": 0, "Russia|nation": 6}
        data["first_opens"] = {"cabinet": 0, "laws": 0}
        data["nation_dp"] = {"Austria": 0, "Russia": 7}
        assert self._errors(data) == []

    # ── (d) unknown keys stay legal; absent keys are fine ────────────────

    def test_an_unknown_top_level_key_is_not_an_error(self):
        data = self._board()
        data["bogus_key_xyz"] = {"anything": [1, 2, 3]}
        assert self._errors(data) == []

    def test_a_scenario_without_any_lesson_key_validates_clean(self):
        from backend.modding.validator import LESSON_KEYS, validate_scenario
        data = self._board()
        for key in LESSON_KEYS:
            data.pop(key, None)
        result = validate_scenario(data)
        assert not result.errors, [f"{e.path}: {e.message}" for e in result.errors]

    # ── the documented semantics hold on the shipped board ───────────────

    def test_the_boards_stored_war_scores_are_the_live_figure(self):
        """MODDING_FORMAT `war_scores`: the first end turn rewrites the stored
        pair score to the live `calculate_war_score` - a scenario authors it to
        that figure. The Table authors it so (France +86 over Austria is
        -86 on "Austria|France")."""
        from backend.game_logic.diplomacy import calculate_war_score
        from backend.models.world_state import WorldState
        world = WorldState.from_scenario(str(self._maps() / self.BOARD_NAME))
        assert world.war_scores, "the Table authors its stored scores"
        for pair, stored in world.war_scores.items():
            a, b = pair.split("|")
            assert stored == calculate_war_score(a, b, world), pair

    def test_nation_starting_regions_is_what_makes_the_conquest_count(self):
        """MODDING_FORMAT `nation_starting_regions`: derived from the loaded
        controllers when absent, so soil handed over by `region_overrides`
        reads as the holder's own and the territory component reads 0."""
        import json
        import os
        import tempfile
        from backend.game_logic.diplomacy import calculate_war_score
        from backend.models.world_state import WorldState
        authored = WorldState.from_scenario(str(self._maps() / self.BOARD_NAME))
        data = self._board()
        data.pop("nation_starting_regions")
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False,
                                         encoding="utf-8") as handle:
            json.dump(data, handle)
            name = handle.name
        try:
            derived = WorldState.from_scenario(name)
        finally:
            os.unlink(name)
        held = calculate_war_score("Austria", "France", authored, return_components=True)
        lost = calculate_war_score("Austria", "France", derived, return_components=True)
        assert held["territory"] < 0, held
        assert lost["territory"] == 0, lost

    def test_a_named_nation_dp_skips_the_boot_purses(self):
        """MODDING_FORMAT `nation_dp`: its PRESENCE skips `seed_boot_purses`;
        absent, every AI court opens with the purse its regen writes."""
        import json
        import os
        import tempfile
        from backend.models.world_state import WorldState
        seeded = WorldState.from_scenario(str(self._maps() / self.BOARD_NAME))
        assert seeded.nation_dp.get("Bavaria", 0) > 0 and seeded.nation_dp.get("Austria", 0) > 0
        data = self._board()
        data["nation_dp"] = {"Austria": 3}
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False,
                                         encoding="utf-8") as handle:
            json.dump(data, handle)
            name = handle.name
        try:
            named = WorldState.from_scenario(name)
        finally:
            os.unlink(name)
        assert named.nation_dp == {"Austria": 3}


# ═══════════════════════════════════════════════════════════════════════════
# S14d part 2, second landing (October 24, 2026) — the Table's own pins: the
# board's arithmetic read live on turn 1 through the probe's own seams, the
# committed record against the committed board, the step mirror, the script,
# the cards' offices (S14D-X41).
# ═══════════════════════════════════════════════════════════════════════════

import hashlib as _hashlib
import importlib.util as _ilu
import json as _json
import os as _os
import pathlib as _pathlib
import re as _re
import tempfile as _tempfile
from unittest.mock import patch as _patch

import pytest as _pytest

_REPO = _pathlib.Path(__file__).resolve().parents[1]
_MAPS = _REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
_BOARD = _MAPS / "tutorial_table_1805.json"
_RECORD = _REPO / "tools" / "_table_board_probe_final.json"
_STEPS_GD = _REPO / "godot-client" / "project-sovereign" / "scripts" / "tutorial_table_steps.gd"
_SCRIPT = _REPO / "tools" / "playtest_scripts" / "tutorial_table_lesson.json"


def _probe():
    spec = _ilu.spec_from_file_location("_table_probe", _REPO / "tools" / "_table_board_probe.py")
    module = _ilu.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@_pytest.fixture(scope="module")
def table_turn_one(tmp_path_factory):
    """The Table board booted once for the module, read on turn 1 through the
    probe's own seams (the door's staged table, the chip's estimate, the
    Cabinet's vassal confirm) — nothing sent, nothing ended."""
    if not _BOARD.is_file():
        _pytest.skip("the Table board is not on this machine")
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START", "PYTHONIOENCODING"):
        _os.environ.pop(key, None)
    _os.environ["LLM_MODE"] = "mock"
    P = _probe()
    from fastapi.testclient import TestClient
    save_dir = _pathlib.Path(_tempfile.mkdtemp(prefix="table_pins_")) / "saves"
    with _patch("backend.save_manager.SAVE_DIR", save_dir):
        import backend.main as M
        from backend.commands.parser import CommandParser
        P._quiet(M._reset_world_state, scenario_override=str(_BOARD))
        M.parser = CommandParser(use_real_llm=False)
        with TestClient(M.app) as client:
            world = M.game_state["world"]
            rows, ok, covered, staged = P.table(world, client)
            out = {
                "world": world, "rows": rows, "ok": ok, "covered": covered, "staged": staged,
                "separate_peace": P.separate_peace(world, staged),
                "bavaria": P.vassal(world, M, client),
                "scores": P.scores(world),
                "dp": int(world.diplomatic_points),
            }
            yield out
        P._quiet(M._reset_world_state)


class TestTheBoardOnTurnOne:
    """⟨SF step=pre-deploy S14d · pillar=first_contact⟩ TABLE_LESSON_SPEC §4.1:
    every predicate's precondition pinned as a number, read live."""

    def test_one_war_with_austria_and_russia_and_the_record_on_the_map(self, table_turn_one):
        world = table_turn_one["world"]
        assert sorted(world.war_instances) == ["war_1"]
        assert table_turn_one["covered"] == ["Austria", "Russia"]
        for name in ("Vienna", "Tyrol", "Moravia"):
            assert world.regions[name].controller == "France", name
        assert world.regions["Carniola"].controller == "Austria"
        assert world.diplomatic_states.get("Bavaria|France") == "ALLIANCE"
        assert int(world.war_exhaustion.get("Austria", 0)) >= 57
        assert table_turn_one["dp"] == 5

    def test_the_stored_war_score_is_the_live_one(self, table_turn_one):
        s = table_turn_one["scores"]["Austria"]
        assert abs(s["stored"] - s["live_france_view"]) <= 1, s
        assert s["live_france_view"] > 30     # Talleyrand's border demand opens above 30

    def test_austria_will_sign_with_the_margin_and_russia_holds_out(self, table_turn_one):
        rows = table_turn_one["rows"]
        assert table_turn_one["ok"] is True
        austria, russia = rows["Austria"], rows["Russia"]
        thr = int(austria["threshold"])
        assert int(austria["total"]) >= thr + 3, austria
        assert austria["band"] == "accept"
        assert int(russia["total"]) < thr, russia

    def test_the_chip_stands_on_austrias_row_and_its_peace_is_accepted(self, table_turn_one):
        austria = table_turn_one["rows"]["Austria"]
        assert austria["chip"] and austria["chip"][0].startswith("Separate peace with Austria")
        chip = table_turn_one["separate_peace"]["chip"]
        assert chip["outcome"] == "ACCEPT", chip
        assert int(chip["score"]) >= 60, chip
        # the slice the chip hands off: Austria's gold and Carniola, nothing else
        kinds = sorted(d["type"] for d in chip["demands"])
        assert kinds == ["gold_lump", "territory_cede"], kinds

    def test_bavarias_vassalage_counters_then_accepts_after_one_ease(self, table_turn_one):
        b = table_turn_one["bavaria"]
        assert b["row"]["available"] is True and int(b["row"]["dp_cost"]) == 3
        assert b["suggested"]["outcome"] == "COUNTER_OFFER", b["suggested"]
        assert "More generous" in b["suggested"]["options"]
        assert b["eased_once"]["outcome"] == "ACCEPT", b["eased_once"]


class TestTheCommittedRecord:
    """The probe's record, committed beside the board: it is THIS board's, and
    every §4.1 clause held when it was written (the three mornings — the
    peace the second, the vassal the third, no stray letter, no battle)."""

    def test_the_record_is_this_boards(self):
        record = _json.loads(_RECORD.read_text(encoding="utf-8"))
        sha = _hashlib.sha256(_BOARD.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        assert record["board_sha256"] == sha, "re-run tools/_table_board_probe.py after changing the board"

    def test_every_clause_held(self):
        record = _json.loads(_RECORD.read_text(encoding="utf-8"))
        failing = [k for k, v in record["clauses"].items() if not v]
        assert failing == [], failing
        mornings = record["script"]["mornings"]
        assert mornings[0]["austria_state"] == "PEACE" and mornings[0]["russia_state"] == "WAR"
        assert mornings[1]["bavaria_state"] == "VASSAL"
        assert all(m["letters"] == [] and m["battles_fought"] == 0 for m in mornings)
        assert all(a["success"] for a in record["script"]["acts"])


def _card_steps():
    src = _STEPS_GD.read_text(encoding="utf-8")
    body = src[src.index("const STEPS := ["):]
    rows = []
    for block in body.split("\n\t{")[1:]:
        sid = _re.search(r'"id":\s*"([a-z_]+)"', block).group(1)
        gate = int(_re.search(r'"turn_gate":\s*(\d+)', block).group(1))
        title = _re.search(r'"title":\s*"([^"]+)"', block).group(1)
        door = _re.search(r'"open":\s*"([^"]+)"', block)
        rows.append({"id": sid, "gate": gate, "title": title,
                     "open": door.group(1) if door else "", "block": block})
    return rows


class TestTheStepMirrorAndTheScript:
    """The backend's `TABLE_STEPS` mirror never drifts from the cards; the
    committed driver script issues each door's line on the card's own gate."""

    def test_the_mirror_matches_the_cards_exactly(self):
        from backend.game_logic import tutorial_state as T
        assert T.TABLE_STEPS == [(r["id"], r["gate"], r["title"]) for r in _card_steps()]
        assert T.STEPS_BY_SCENARIO["tutorial_table"] is T.TABLE_STEPS
        assert "tutorial_table" in T.SCHOOL_SCENARIOS
        assert T.SCENARIO_FILES["tutorial_table"] == "tutorial_table_1805.json"

    def test_seven_cards_over_three_turns_each_a_door_or_a_button(self):
        rows = _card_steps()
        assert [r["id"] for r in rows][-1] == "handoff" and len(rows) == 7
        assert [r["gate"] for r in rows] == [1, 1, 1, 2, 2, 3, 3]
        for r in rows:
            assert '"suggest": ""' in r["block"], r["id"]          # never typed
        assert [r["open"] for r in rows if r["open"]] == ["cabinet:Bavaria", "settlement:war_1:Austria", "cabinet:Bavaria"]

    def test_the_script_declares_the_lesson_and_issues_each_door_on_its_gate(self):
        script = _json.loads(_SCRIPT.read_text(encoding="utf-8"))
        assert script["scenario"] == "tutorial_table"
        assert script["policy"]["missions"] == "begin"
        turns = {int(k): v for k, v in script["turns"].items()}
        assert max(turns) == 3
        doors = script["doors"]
        by_door = {}
        for r in _card_steps():
            if r["open"]:
                by_door.setdefault("open:" + r["open"], []).append(r["gate"])
        for line, door in doors.items():
            gate = min(by_door[door])
            issued = [g for g, lines in turns.items() if line in lines]
            assert issued and issued[0] in by_door[door], (line, door, issued, by_door[door])
            assert gate <= issued[0]
        clicks = script["clicks"]
        assert [c["on"] for c in clicks["1"]] == ["settlement_confirm", "settlement_pair_substitute_confirm", "proposal_confirm"]
        assert [c["option"] for c in clicks["2"]] == ["More generous", "execute_proposal"]


class TestTheCardsNameOffices:
    """⟨SF step=pre-deploy S14d · S14D-X41 · pillar=narration⟩ The Table's cards
    name offices only as the record holds them in December 1805 — the Elector
    of Bavaria (a king on 1 January), the Tsar, Austria's envoy — never a man's
    later office (Metternich's ministry 1809, Castlereagh's 1812, Hardenberg's
    chancellorship 1810)."""

    LATER_OFFICES = ("Metternich", "Castlereagh", "Hardenberg", "Stadion", "Chancellor",
                     "Foreign Minister", "King of Bavaria", "King Max")

    def test_no_card_names_an_office_the_record_denies(self):
        text = " ".join(r["block"] for r in _card_steps())
        for name in self.LATER_OFFICES:
            assert name not in text, name

    def test_the_offices_the_cards_do_name_are_the_records(self):
        text = " ".join(r["block"] for r in _card_steps())
        assert "the Elector of Bavaria was a king" in text
        assert "the Tsar" in text and "her envoy" in text
        # the game steps are not dressed as history: the mission and the ease
        # are named as game steps, the dates belong to the record alone
        assert "REASSURE" in text and "MORE GENEROUS" in text
        for date in ("26th of December", "1st of January 1806"):
            assert date in text, date
