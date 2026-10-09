"""Score Finish Step 7, slice 9 — THE FRAMES (Oct 4–5, 2026).

The IQ-10 re-shoot of every surface Steps 1–8 touched, at both Interface
Scales, and one five-turn Mode C session on the live client (the user's
"Everything now"). What the frames found is filed in `docs/BUG_FIXES.md`
§Score Finish Step 7 (SF7-X17 … SF7-X31) and fixed here. Rules:
`docs/SYSTEMS_REFERENCE.md` §93.11.

The client halves that can be DRIVEN are pinned on the real `main.tscn` in
`tests/test_cx7_predictor_driven.py` (`TestTheFramesTerminalText`: the trim,
the faces, the covered map's hover; `TestTheDaySaysWhenItEnds`: the auto-end
line). This file holds the backend pins, the scene/theme pins and the
source pins for the surfaces a headless harness cannot draw.

Every fix rides a lever; the sweep (`tools/_sweep_sf7_s9.json`) flips each
one and requires a pin here (or in the driven file) to go red.
"""

from __future__ import annotations

import contextlib
import io
import json
import random
import re
import subprocess
from pathlib import Path

import pytest

from backend.commands.executor import CommandExecutor
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
GODOT = REPO / "godot-client" / "project-sovereign"
SCRIPTS = GODOT / "scripts"
SCENES = GODOT / "scenes"
THEME = GODOT / "ui" / "main_theme.tres"
FONTS = GODOT / "assets" / "fonts"
SCENARIO = GODOT / "assets" / "maps" / "europe_1805.json"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _boot():
    with contextlib.redirect_stdout(io.StringIO()):
        world = WorldState.from_scenario(str(SCENARIO))
    executor = CommandExecutor()
    return world, executor, {"world": world, "executor": executor}


def _run(executor, game_state, command):
    with contextlib.redirect_stdout(io.StringIO()):
        random.seed(1805)
        return executor.execute({"command": command}, game_state)


def _tscn_node_block(text: str, node_name: str) -> str:
    """The property lines of one `[node name="…"]` block."""
    m = re.search(r'\[node name="%s"[^\]]*\]\n(.*?)(?:\n\[|\Z)' % re.escape(node_name),
                  text, re.S)
    assert m, f"no node {node_name}"
    return m.group(1)


# ═════════════════════════ SF7-X18 — bold and italic have faces ═══════════


class TestTheThemeHasItsFaces:
    def test_the_rich_text_label_names_three_faces(self):
        theme = _read(THEME)
        assert 'RichTextLabel/fonts/bold_font = SubResource("FontVariation_bold")' in theme
        assert 'RichTextLabel/fonts/italics_font = ExtResource("4_italic")' in theme
        assert ('RichTextLabel/fonts/bold_italics_font = '
                'SubResource("FontVariation_bold_italic")') in theme

    def test_the_bold_faces_are_the_weight_axis_not_a_fake(self):
        """EB Garamond is a variable font: weight 700 on its own wght axis,
        never the engine's embolden (which smears the strokes)."""
        theme = _read(THEME)
        for sub in ("FontVariation_bold", "FontVariation_bold_italic"):
            block = re.search(r'\[sub_resource type="FontVariation" id="%s"\]\n(.*?)\n\n' % sub,
                              theme, re.S)
            assert block, sub
            assert "700" in block.group(1), block.group(1)
            assert "variation_embolden" not in block.group(1)

    def test_the_italic_face_ships_with_its_import_sidecar(self):
        """`assets/` is git-ignored (the NP-V lesson: a fresh clone had no
        portrait); the sidecar pins the uid the theme resolves against and
        must be force-added, like the UI-1 font sidecars."""
        ttf = "assets/fonts/EBGaramond-Italic[wght].ttf"
        sidecar = FONTS / "EBGaramond-Italic[wght].ttf.import"
        assert sidecar.is_file()
        uid = re.search(r'(?m)^uid="(uid://[a-z0-9]+)"', _read(sidecar)).group(1)
        assert f'uid="{uid}" path="res://{ttf}"' in _read(THEME), (
            "the theme's ext_resource uid must be the sidecar's")
        tracked = subprocess.run(
            ["git", "ls-files", "--", f"godot-client/project-sovereign/{ttf}",
             f"godot-client/project-sovereign/{ttf}.import"],
            cwd=str(REPO), capture_output=True, text=True).stdout.split()
        assert len(tracked) == 2, tracked

    @pytest.mark.parametrize("scene,node", [
        ("main.tscn", "OutputDisplay"),
        ("dispatch_view.tscn", "ContentLabel"),
    ])
    def test_inline_emphasis_keeps_the_body_size(self, scene, node):
        """The terminal and the dispatch use `[b]` for INLINE emphasis
        ("Click [b]End Turn[/b]"); an unset bold size falls back to the
        theme's bold size against their body. The ledgers' `[b]` headings keep
        the 16 on purpose (they are headings).

        Re-seated by UXR-1 (October 9, 2026): the floor DROPPED both bodies'
        11/12-px overrides, so they read the theme's 16 — and so does the
        theme's bold. The invariant is that the four sizes AGREE: all four
        set to one number, or none set (the theme's, where normal and bold
        are both 16)."""
        block = _tscn_node_block(_read(SCENES / scene), node)
        sizes = {item: re.search(rf"theme_override_font_sizes/{item} = (\d+)", block)
                 for item in ("normal_font_size", "bold_font_size", "italics_font_size",
                              "bold_italics_font_size")}
        values = {k: (int(m.group(1)) if m else None) for k, m in sizes.items()}
        assert len(set(values.values())) == 1, (scene, values)
        if values["normal_font_size"] is not None:
            assert values["normal_font_size"] >= 14, (scene, values)


# ═════════════════════════ SF7-X20 — the famine counts its own turns ══════


class TestTheFamineCountsItsOwnTurns:
    @staticmethod
    def _starving(world, turns):
        corps = [m for m in world.marshals.values() if m.nation == "France"][:3]
        loc = corps[0].location
        for m in corps:
            m.location = loc
        for turn in turns:
            world.current_turn = turn
            for m in corps:
                world.log_event({"type": "supply_attrition", "marshal": m.name,
                                 "nation": "France", "region": loc, "losses": 700})
        world.current_turn = max(turns)
        return loc

    def test_the_run_is_the_trailing_consecutive_run(self):
        from backend.game_logic import dispatch as D
        world, _ex, _gs = _boot()
        loc = self._starving(world, (5, 7, 8, 9, 10))
        assert D._famine_run(world, "France", loc) == 4
        assert D._famine_run(world, "France", "Moscow") == 0

    def test_the_escalated_headline_states_the_famines_run_not_the_pages(
            self, monkeypatch):
        """The live session's turn 5: "3 turns of famine at Swabia now"
        stood beside the roster's "supply has failed at Swabia four turns
        running" — the headline's {turns} was the page's run. Staged: four
        famine turns, the page has carried the class for two mornings (the
        third is this one)."""
        from backend.game_logic import dispatch as D
        world, _ex, _gs = _boot()
        loc = self._starving(world, (7, 8, 9, 10))
        world.headline_lead_memory = {"runs": {f"supply_strain:{loc}": 2}}
        head = json.dumps(D._build_headline(world, "France") or {}, ensure_ascii=False)
        assert f"4 turns of famine at {loc}" in head or "been 4 turns over" in head, head
        monkeypatch.setattr(D, "THE_FAMINE_COUNTS_ITS_OWN_TURNS", False)
        world.headline_lead_memory = {"runs": {f"supply_strain:{loc}": 2}}
        head = json.dumps(D._build_headline(world, "France") or {}, ensure_ascii=False)
        assert f"3 turns of famine at {loc}" in head or "been 3 turns over" in head, head


# ═════════════════════════ SF7-X25 — the copy nits ═════════════════════════


class TestTheCopyReadsClean:
    def test_the_cure_line_says_no_corps(self):
        from backend.game_logic import reforms as RF
        world, _ex, _gs = _boot()
        payload = RF.laws_payload(world, "France")
        train = next(r for r in payload["rows"] if r["id"] == "train_des_equipages")
        assert "no corps drawing 80% now" in train["cure_line"], train["cure_line"]
        assert "0 corps" not in train["cure_line"]
        assert " ; " not in train["cure_line"]

    def test_the_cure_line_lever_restores_the_old_form(self, monkeypatch):
        from backend.game_logic import doctrines as DC
        from backend.game_logic import reforms as RF
        monkeypatch.setattr(DC, "THE_CURE_LINE_READS_CLEAN", False)
        world, _ex, _gs = _boot()
        train = next(r for r in RF.laws_payload(world, "France")["rows"]
                     if r["id"] == "train_des_equipages")
        assert "0 corps drawing 80% now" in train["cure_line"]

    def test_a_white_peace_names_no_terms(self, monkeypatch):
        from backend.game_logic import diplomatic_templates as DT
        for component in DT.SPOKEN_BLOCKER_PHRASES_WHITE_PEACE_NO_TERMS:
            spoken = DT.spoken_blocker_phrase(component, white_peace=True)
            assert "the terms" not in spoken, (component, spoken)
            assert spoken == DT.SPOKEN_BLOCKER_PHRASES_WHITE_PEACE_NO_TERMS[component]
        # a drafted package still hears its own sentence
        assert (DT.spoken_blocker_phrase("agenda_settlement_mod")
                == DT.SPOKEN_BLOCKER_PHRASES["agenda_settlement_mod"])
        monkeypatch.setattr(DT, "THE_WHITE_PEACE_NAMES_NO_TERMS", False)
        assert (DT.spoken_blocker_phrase("agenda_settlement_mod", white_peace=True)
                == DT.SPOKEN_BLOCKER_PHRASES["agenda_settlement_mod"])

    def test_the_whole_war_table_says_sire_once(self, monkeypatch):
        """The white peace's review: "Sire, this settlement … seats 3 courts
        at the table. Sire, Austria will not sign" — staged exactly as the
        IQ-10 capture stages it."""
        from backend.game_logic import diplomatic_templates as DT
        from backend.game_logic.settlement_staging import stage_settlement_confirm

        def staged_text():
            world, _ex, _gs = _boot()
            key = world._make_diplo_key("France", "Austria")
            world.war_scores[key] = 80 if key.split("|")[0] == "France" else -80
            with contextlib.redirect_stdout(io.StringIO()):
                staged = stage_settlement_confirm(
                    world, war_id="war_1", settlement_terms=[{"type": "peace"}],
                    covered_enemy_participants=["Austria", "Britain", "Russia"])
            return json.dumps(staged, ensure_ascii=False, default=str)

        text = staged_text()
        assert "will not sign" in text, "precondition: the hold-out line is spoken"
        assert "Sire, Austria will not sign" not in text, text[:600]
        monkeypatch.setattr(DT, "THE_TABLE_SAYS_SIRE_ONCE", False)
        assert "Sire, Austria will not sign" in staged_text()


# ═════════════════════════ SF7-X26 — the colours know our friends ═════════


class TestTheColoursKnowOurFriends:
    def test_each_court_has_its_standing(self):
        from backend import main as M
        world, _ex, _gs = _boot()
        assert M.battle_standing(world, "France") == "player"
        assert M.battle_standing(world, "Bavaria") == "friend"   # ALLIANCE
        assert M.battle_standing(world, "Holland") == "friend"   # VASSAL
        assert M.battle_standing(world, "Austria") == "foe"      # WAR
        assert M.battle_standing(world, "Prussia") == "neutral"  # PEACE
        assert M.battle_standing(world, "") == ""

    def test_the_stamp_copies_and_never_writes_into_the_producers_event(self):
        """The IGR-B trap: a view-layer field stamped in place rides into
        whatever else holds the event (the save, the log)."""
        from backend import main as M
        world, _ex, _gs = _boot()
        original = {"type": "battle", "attacker_nation": "Bavaria",
                    "defender_nation": "Austria", "victor": "Deroy"}
        action = {"action": "attack", "events": [original]}
        phase = {"nations": {"Bavaria": {"actions": [action]}}}
        out = M._stamp_battle_standing(phase, world)
        stamped = out["nations"]["Bavaria"]["actions"][0]["events"][0]
        assert stamped["attacker_alignment"] == "friend"
        assert stamped["defender_alignment"] == "foe"
        assert "attacker_alignment" not in original
        assert action["events"][0] is original, "the producer's action is untouched"

    def test_the_end_turn_payload_carries_the_stamps(self):
        """Driven through the real end turn on the 1805 boot: every
        enemy-phase event naming its sides carries their standing (the
        friend arm — Bavaria beating Mack, the session's case — is pinned on
        the unit above; whether Deroy fights on this seed's turn 1 is the
        AI's business, not this pin's)."""
        from fastapi.testclient import TestClient
        from backend import main as M
        world, executor, gs = _boot()
        saved = (M.world, M.game_state)
        try:
            M.world, M.game_state = world, gs
            with contextlib.redirect_stdout(io.StringIO()):
                resp = TestClient(M.app).post("/command", json={"command": "end turn"}).json()
        finally:
            M.world, M.game_state = saved
        phase = resp.get("enemy_phase") or {}
        stamped = [e for nd in (phase.get("nations") or {}).values()
                   for a in nd.get("actions") or [] for e in a.get("events") or []
                   if isinstance(e, dict) and e.get("attacker_nation")]
        assert stamped, "precondition: an enemy-phase battle to colour"
        for e in stamped:
            assert e.get("attacker_alignment") == M.battle_standing(world, e["attacker_nation"]), e
            if e.get("defender_nation"):
                assert e.get("defender_alignment") == M.battle_standing(
                    world, e["defender_nation"]), e

    def test_the_dialog_colours_by_the_stamp(self):
        """The client half (a headless harness cannot open the enemy-phase
        dialog with a live payload): the result line and both retreat lines
        read the stamp through ONE colour rule, and an absent stamp keeps the
        France-only colour."""
        src = _read(SCRIPTS / "enemy_phase_dialog.gd")
        assert "const THE_COLOURS_KNOW_OUR_FRIENDS := true" in src
        body = src[src.index("func _standing_colour"):]
        body = body[:body.index("\nfunc ", 10)]
        assert 'standing == "neutral"' in body and "Utils.COLOR_INFO" in body
        assert "ours == won" in body
        fmt = src[src.index("func _format_battle"):]
        fmt = fmt[:fmt.index("\nfunc ", 10)]
        assert fmt.count("_standing_colour(") == 3, "result + both retreats"
        assert '_standing(event, "attacker")' in fmt and '_standing(event, "defender")' in fmt


# ═════════════════════════ SF7-X32 — "decisive" is the result's word ═══════


class TestTheDecisiveWordIsTheResults:
    """The turn-20 enemy phase: "Result: Defender tactical victory (Deroy
    victorious)" and, two lines below, Berthier's "A decisive victory for
    Deroy!" — his 2:1 casualty arm spoke the result line's word."""

    @staticmethod
    def _battle(outcome):
        return {
            "outcome": outcome,
            "attacker": {"name": "ArchdukeJohn", "casualties": 1726},
            "defender": {"name": "Deroy", "casualties": 724},
            "attacker_nation": "Austria", "defender_nation": "Bavaria",
            "attacker_original_strength": 10890, "defender_original_strength": 9218,
            "modifier_snapshot": {"attacker": [], "defender": []},
        }

    def _line(self, outcome):
        from backend.game_logic import battle_report as BR
        BR.reset_observation_rotation()
        return BR._pick_observation(self._battle(outcome), "France")

    @staticmethod
    def _bank(name):
        from backend.game_logic import battle_report as BR
        return {b.format(marshal="Deroy", enemy="Archduke John")
                for b in BR._OBSERVATIONS[name]}

    def test_a_tactical_win_two_to_one_speaks_of_the_exchange(self):
        line = self._line("defender_tactical_victory")
        assert line in self._bank("won_the_exchange"), line
        assert "decisive" not in line.lower()

    def test_the_exchange_says_we_of_no_one(self):
        """An ally's battle is Berthier's subject too (Deroy here): the
        lines name both commanders and never say "we" or "ours"."""
        for line in self._bank("won_the_exchange"):
            assert not re.search(r"\b(we|ours|our)\b", line.lower()), line

    def test_a_decisive_result_keeps_its_bank(self):
        assert self._line("defender_victory") in self._bank("won_decisively")

    def test_the_lever_restores_the_one_bank(self, monkeypatch):
        from backend.game_logic import battle_report as BR
        monkeypatch.setattr(BR, "THE_DECISIVE_WORD_IS_THE_RESULTS", False)
        assert self._line("defender_tactical_victory") in self._bank("won_decisively")


# ═════════════════════════ SF7-X29 — the reserve names its dead ════════════


class TestTheReserveNamesItsDead:
    @staticmethod
    def _contingents(casualties):
        return [{"name": f"C{i}", "status": "engaged", "casualties": c,
                 "committed": 10000, "remaining": 10000 - c}
                for i, c in enumerate(casualties)]

    def test_the_unseated_corps_dead_ride_the_tail(self):
        from backend.game_logic import battle_diorama as BD
        side = BD._cap_side(self._contingents([100, 200, 300, 400, 258]))
        assert side["reserve_count"] == 1
        assert side["reserve_casualties"] == 258
        shown = sum(c["casualties"] for c in side["contingents"])
        assert shown + side["reserve_casualties"] == side["casualties_total"]

    def test_a_seated_line_has_no_reserve_dead(self):
        from backend.game_logic import battle_diorama as BD
        assert BD._cap_side(self._contingents([100, 200]))["reserve_casualties"] == 0

    def test_the_lever_removes_the_key(self, monkeypatch):
        from backend.game_logic import battle_diorama as BD
        monkeypatch.setattr(BD, "THE_RESERVE_NAMES_ITS_DEAD", False)
        assert "reserve_casualties" not in BD._cap_side(self._contingents([1, 2, 3, 4, 5]))

    def test_the_tableau_prints_it(self):
        src = _read(SCRIPTS / "battle_diorama.gd")
        assert "const THE_RESERVE_NAMES_ITS_DEAD := true" in src
        assert 'side.get("reserve_casualties", 0)' in src
        assert '" — %s lost"' in src
        assert "sw - tail.get_minimum_size().x - 14.0" in src, (
            "the longer line right-aligns by its own width")


class TestTheLineFitsTheBaize:
    """SF7-X23: a side of four contingents drew its fourth (Lannes) outside
    the baize — the fixed 118px/66px steps assume three. The steps shrink to
    the room the stage leaves; the authored steps stay the ceiling. Pinned
    against a Python mirror of the formula at the shipped stage size (the
    frames are the eyes-on half, IQ-10's `diorama_*` shots)."""

    @staticmethod
    def _stage():
        """The shipped stage, read off the scene's own constants."""
        src = _read(SCRIPTS / "battle_diorama.gd")

        def const(name):
            return float(re.search(r"(?m)^const %s := ([0-9.]+)" % name, src).group(1))
        sw = const("TRAY_W") - const("STAGE_MARGIN_X") * 2.0
        return sw, const("STAGE_H") - 58.0

    @classmethod
    def _steps(cls, n):
        sw, base_y = cls._stage()
        last = 1.0 - 0.12 * (n - 1)
        step_x = min(118.0, max(40.0, (sw / 2.0 - 128.0 - 100.0 * last - 16.0) / (n - 1)))
        step_y = min(66.0, max(30.0, (base_y - 60.0 - 158.0 * last) / (n - 1)))
        return step_x, step_y

    def test_the_formula_is_the_one_in_the_scene(self):
        src = _read(SCRIPTS / "battle_diorama.gd")
        assert "const THE_LINE_FITS_THE_BAIZE := true" in src
        assert "(sw / 2.0 - 128.0 - 100.0 * last_scale - 16.0) / float(n - 1)" in src
        assert "(base_y - 60.0 - 158.0 * last_scale) / float(n - 1)" in src
        assert "base_y - step_y * fought.size() - 8.0" in src, "the tail follows the steps"

    def test_four_contingents_stay_on_the_baize(self):
        sw, base_y = self._stage()
        step_x, step_y = self._steps(4)
        last_scale = 1.0 - 0.12 * 3
        # the fourth block's locket: outboard of the half-stage, above the odometer
        assert 128.0 + step_x * 3 + 100.0 * last_scale <= sw / 2.0 - 16.0 + 0.5
        assert base_y - step_y * 3 - 158.0 * last_scale >= 60.0 - 0.5
        # and the authored steps would NOT have (the defect, measured)
        assert 128.0 + 118.0 * 3 + 100.0 * last_scale > sw / 2.0 - 16.0
        assert base_y - 66.0 * 3 - 158.0 * last_scale < 60.0

    def test_two_contingents_keep_the_authored_steps(self):
        assert self._steps(2) == (118.0, 66.0)


# ═════════════════════════ SF7-X30 — the petition names its table ══════════


class TestThePetitionNamesItsTable:
    def _world(self):
        from tests.test_settlement_slice_h_ally_petitions import _install_war
        from backend.game_logic.diplomacy import create_war_objective
        world = WorldState()
        world.current_turn = 5
        _install_war(world, attackers=("France", "Prussia"),
                     defenders=("Britain", "Austria"))
        key = world._make_diplo_key("Prussia", "Austria")
        world.war_objectives[key] = {"Prussia": create_war_objective(
            "conquest", "Prussia", "Austria", ["Vienna"], world.current_turn)}
        return world

    def _petition_text(self, world):
        from backend.game_logic.settlement_preview import (
            ALLY_SETTLEMENT_PETITION_DIALOGUE_TYPE,
            queue_ally_settlement_petitions_for_player_action)
        with contextlib.redirect_stdout(io.StringIO()):
            queue_ally_settlement_petitions_for_player_action(
                world, trigger_action="stage_settlement", war_id="war_1",
                covered_enemy_participants=["Austria", "Britain"],
                settlement_terms=[])
        dm = world.dialogue_manager
        items = [dm.peek()] + list(dm.iter_queue())
        petitions = [d for d in items if isinstance(d, dict)
                     and d.get("type") == ALLY_SETTLEMENT_PETITION_DIALOGUE_TYPE]
        assert petitions, "precondition: Prussia petitions"
        return json.dumps(petitions, ensure_ascii=False)

    def test_the_petition_reads_the_tables_coverage(self):
        """The voice and the petition's own `war_label` name the TABLE. (The
        Grant option's "Open the settlement of France vs Britain first (War
        Detail → …)" names the WAR, as every war-scoped surface does — G4F-7
        kept the leader pair there on purpose.)"""
        text = self._petition_text(self._world())
        # The chancery register reads `{war_label}` ("petitions for … in the
        # settlement of {war_label}" — Bavaria's line on the live screen);
        # Hardenberg's own register does not, so the field is the pin.
        assert '"war_label": "France vs Austria + Britain"' in text, text[:800]
        assert '"war_label": "France vs Britain"' not in text

    def test_the_lever_restores_the_leader_pair(self, monkeypatch):
        from backend.game_logic import settlement_offers as SO
        monkeypatch.setattr(SO, "THE_PETITION_NAMES_THE_TABLE", False)
        assert '"war_label": "France vs Britain"' in self._petition_text(self._world())

    def test_the_contribution_names_the_side_it_fought_on(self, monkeypatch):
        text = self._petition_text(self._world())
        assert "Prussia fought beside France in this war" in text, text[:800]
        assert "fought for this coalition" not in text
        from backend.game_logic import settlement_offers as SO
        monkeypatch.setattr(SO, "THE_PETITION_NAMES_ITS_SIDE", False)
        assert "fought for this coalition" in self._petition_text(self._world())


# ═════════════════════════ SF7-X31 — a garrison that gives way is said ═════


class TestAGarrisonThatGivesWayIsSaid:
    @staticmethod
    def _stage_vienna(world, garrison=3000):
        vienna = world.get_region("Vienna")
        for m in world.marshals.values():
            if m.location == "Vienna":
                m.location = "Hungary"
        vienna.garrison_strength = garrison
        vienna.garrison_detachment = False
        ney = world.marshals["Ney"]
        ney.location = "Bohemia"
        ney.strength = 30000
        return vienna

    @staticmethod
    def _gave_way(result):
        return [e.get("garrison_gave_way") for e in result.get("events") or []
                if isinstance(e, dict) and e.get("garrison_gave_way")]

    def test_the_player_is_told_the_garrison_gave_way(self):
        world, executor, gs = _boot()
        vienna = self._stage_vienna(world)
        result = _run(executor, gs, {"action": "attack", "marshal": "Ney",
                                     "target": "Vienna", "_muster_confirmed": True})
        assert result.get("success"), result.get("message")
        assert "The last 3,000 of the garrison at Vienna give way." in result["message"]
        assert self._gave_way(result) == [3000], result.get("events")
        assert vienna.garrison_strength == 0

    def test_gr5_the_ai_capture_says_it_too(self):
        world, executor, gs = _boot()
        munich = world.get_region("Munich")
        for m in world.marshals.values():
            if m.location == "Munich":
                m.location = "Franconia"
        munich.garrison_strength = 2500
        munich.garrison_detachment = False
        world.marshals["Mack"].strength = 30000
        result = _run(executor, gs, {"action": "attack", "marshal": "Mack", "target": "Munich",
                                     "_acting_nation": "Austria", "_muster_confirmed": True})
        assert result.get("success"), result.get("message")
        assert "The last 2,500 of the garrison at Munich give way." in result["message"]
        assert self._gave_way(result) == [2500]

    def test_the_lever_restores_the_silent_clear(self, monkeypatch):
        from backend.commands import combat_executor as CE
        monkeypatch.setattr(CE.CombatExecutor, "A_GARRISON_THAT_GIVES_WAY_IS_SAID", False)
        world, executor, gs = _boot()
        self._stage_vienna(world)
        result = _run(executor, gs, {"action": "attack", "marshal": "Ney",
                                     "target": "Vienna", "_muster_confirmed": True})
        assert result.get("success")
        assert "give way" not in result["message"]
        assert self._gave_way(result) == []

    def test_the_enemy_phase_prints_it(self):
        src = _read(SCRIPTS / "enemy_phase_dialog.gd")
        assert 'event.get("garrison_gave_way", 0)' in src
        assert '" of the garrison of "' in src


# ═════════════════════════ the client surfaces a harness cannot draw ═══════


class TestTheScreenSays:
    def test_the_interrupt_popup_fits_its_question(self):
        """SF7-X27: 600x360 authored, a two-line question over ~130px of
        empty panel. The fit runs AFTER the clamp and only shrinks."""
        src = _read(SCRIPTS / "interrupt_popup.gd")
        assert "const THE_QUESTION_FITS_ITS_BOX := true" in src
        show = src[src.index("func show_interrupt"):src.index("func _fit_to_content")]
        assert show.index("Utils.clamp_centered_panel($PanelContainer)") < show.index(
            'call_deferred("_fit_to_content")')
        fit = src[src.index("func _fit_to_content"):]
        fit = fit[:fit.index("\nfunc ", 10)]
        assert "need < have" in fit, "it only ever shrinks"

    def test_the_formables_prompt_hugs_its_quote(self):
        """SF7-X28: step 3 laid its two-line quote out like an assessment
        (an expanding region) — a blank band above the list."""
        src = _read(SCRIPTS / "diplomacy_wizard.gd")
        assert "const THE_FORMABLES_PROMPT_HUGS_ITS_QUOTE := true" in src
        assert "_lay_out_prompt(3)" in src[src.index("func _on_formables_pressed"):]
        lay = src[src.index("func _lay_out_prompt"):]
        lay = lay[:lay.index("\nfunc ", 10)]
        step3 = lay[lay.index("elif step == 3"):lay.index("else:")]
        assert "THE_FORMABLES_PROMPT_HUGS_ITS_QUOTE" in step3
        assert "Control.SIZE_FILL" in step3 and "SIZE_EXPAND_FILL" not in step3

    def test_our_own_soil_carries_no_hedge(self):
        """SF7-X22: Normandy, French and empty of corps, read "Intel:
        Partial (reports only)" above four exact figures — WO-V-D2 fixed the
        region panel, this is its tooltip twin."""
        src = _read(SCENES / "map_renderer_base.gd")
        assert "const OUR_SOIL_CARRIES_NO_HEDGE := true" in src
        tip = src[src.index("func _draw_region_tooltip"):]
        tip = tip[:tip.index("\nfunc ", 10)]
        assert "OUR_SOIL_CARRIES_NO_HEDGE and str(controller) == _PLAYER_NATION" in tip
        assert 'visibility == "partial" and hedge_ground' in tip
        assert 'visibility == "stale" and hedge_ground' in tip

    def test_the_main_scene_hands_the_map_its_modal_check(self):
        """SF7-X21's wiring (the driven pin overrides the check; this pins
        that the live client sets it)."""
        src = _read(SCRIPTS / "main.gd")
        assert "map_area.pointer_blocked_check = _is_modal_dialog_open" in src

    @pytest.mark.parametrize("script", ["strategic_ledger.gd", "diplomatic_ledger.gd"])
    def test_the_books_turn_while_you_type(self, script):
        """SF7-X24: digits typed into the command line turned the ledger's
        tab; the copy said "Keys 1-7" over eight books. Alt+digit turns them
        while a line edit holds focus, and the copy says so."""
        src = _read(SCRIPTS / script)
        assert "const ALT_TURNS_THE_BOOKS := true" in src
        inp = src[src.index("func _input"):]
        inp = inp[:inp.index("\nfunc ", 10)]
        assert "alt_pressed" in inp and "LineEdit" in inp

    def test_the_ledger_copy_counts_its_books(self):
        src = _read(SCRIPTS / "strategic_ledger.gd")
        assert "Keys 1–8 turn the ledger's books (Alt+1–8 while you type)" in src
        assert "Keys 1-7" not in src and "Keys 1–7" not in src

    @pytest.mark.parametrize("script", ["main.gd", "dispatch_view.gd"])
    def test_the_treasury_delta_reads_its_thousands(self, script):
        """SF7-X25: "+1032" — the delta skipped the formatter its own line
        used for the treasury beside it."""
        src = _read(SCRIPTS / script)
        assert "str(treasury_delta)" not in src
        assert "_format_number(treasury_delta)" in src

    def test_the_morale_warning_has_its_space(self):
        src = _read(SCRIPTS / "dispatch_view.gd")
        assert 'line += " Morale: " + str(m_morale) + "%"' in src
        assert '" Morale:" + str(' not in src
