"""Row BA, session BA-6 — "the last word" (November 17, 2026): BA-5's open rows
closed and its readings ruled under the user's "ba-5 is done please assure its
good dont leave any open items" and "make decisions yourself soundly with
research"; the battle's ground made from real period surveys ("make sure the
terrain background does not look ai genned even get assets if needed").

The backend half pinned here (the client's levers: tests/test_ba6_levers.py):
BA5-X16 (a dear defeat is not a narrow one), BA5-X17 (a card's men of ours are
men in reach), BA6-X1 (a day decided for neither is kept as drawn), the
reserve's attacker form, the words' risk and the free words' stakes, and the
survey plates themselves (their coverage, their sides, never a mirror, their
contrast floors, their licences).
"""
from __future__ import annotations

import json
import random
from pathlib import Path

import pytest

from backend.game_logic import battle_day as BD
from backend.game_logic import battle_report as BR
from backend.game_logic import battle_telling as BT

REPO = Path(__file__).resolve().parents[1]
ART = REPO / "godot-client" / "project-sovereign" / "assets" / "textures" / "battle"


# ═══════════════════════ BA5-X16: a dear defeat ═══════════════════════════

def _defeat(our_cas, their_cas, original=20000, routed=False):
    """France attacked and lost; Berthier reads France's side."""
    return {
        "outcome": "defender_victory", "attacker_nation": "France",
        "attacker": {"name": "Bernadotte", "casualties": our_cas, "remaining": original - our_cas,
                     "forced_retreat": routed},
        "defender": {"name": "Mack", "casualties": their_cas, "remaining": 30000, "forced_retreat": False},
        "attacker_original_strength": original, "defender_original_strength": 30000,
        "modifier_snapshot": {"attacker": [], "defender": []},
    }


def _lines(battle, n=60):
    seen = set()
    for s in range(n):
        random.seed(s)
        seen.add(BR._pick_observation(battle, "France"))
    return seen


def _bank(name, marshal="Bernadotte", enemy="Mack"):
    return {line.replace("{marshal}", marshal).replace("{enemy}", enemy) for line in BR._OBSERVATIONS[name]}


class TestADearDefeatIsNotANarrowOne:

    def test_a_fifth_of_the_corps_lost_on_a_narrow_margin_is_dear(self):
        got = _lines(_defeat(5600, 4800))            # 28 %, margin 800 < 15 %
        assert got <= _bank("lost_dear"), got
        assert not (got & _bank("lost_narrow_no_drill"))

    def test_a_light_toll_on_a_narrow_margin_is_still_narrow(self):
        assert _lines(_defeat(2400, 2000)) <= _bank("lost_narrow_no_drill")   # 12 %

    def test_the_grievous_and_the_rout_keep_their_arms(self):
        assert _lines(_defeat(7000, 6000)) <= _bank("lost_costly")            # 35 %
        assert _lines(_defeat(5000, 1000, routed=True)) <= _bank("routed")   # 25 %, driven off

    def test_the_new_arm_is_gated_by_the_scale_of_a_battle(self):
        from tests.test_fa_s16_d3_the_scale_of_a_battle_2026_09_06 import _arm_is_gated
        assert _arm_is_gated("lost_dear")

    def test_seam_down_the_margin_alone(self, monkeypatch):
        monkeypatch.setattr(BR, "a_dear_defeat_is_not_a_narrow_one", lambda: False)
        assert _lines(_defeat(5600, 4800)) <= _bank("lost_narrow_no_drill")


# ═══════════════════ BA5-X17: men in reach, as men ═════════════════════════

class TestACardsMenAreMenInReach:

    def test_the_force_block_counts_men_and_keeps_the_weight_for_the_forecast(self):
        import inspect
        from backend.commands import order_quotes as Q
        src = inspect.getsource(Q._force_block)
        assert "if a_cards_men_are_men_in_reach():" in src
        assert 'joining = [world.marshals.get(n) for n in (odds.get("joining") or [])]' in src
        assert '"ours_weight": int(weight)' in src
        assert 'int(force.get("ours_weight", force["ours"]))' in inspect.getsource(Q.attack_quote)

    def test_the_staged_ulm_press_card_reads_men_on_the_field(self):
        day = json.loads((REPO / "docs/audits/ba1_client/payloads/day_ulm.json").read_text(encoding="utf-8"))
        press = next(c for c in day["day"]["chips"] if c["kind"] == "press")
        ours = int(press["does"].split("—")[1].split(" on ")[0].strip().replace(",", ""))
        field = [s for s in (day["attacker"], day["defender"]) if s.get("nation") == "France"][0]
        assert ours <= int(field["committed_total"]) - int(field.get("casualties_total", 0) or 0)


# ═══════════════════ BA6-X1: a ruin is kept as drawn ══════════════════════

class _Lead:
    def __init__(self):
        self.days = []

    def keep_day(self, day):
        self.days.append(day)


class _World:
    def __init__(self, lead):
        self.lead = lead
        self.current_turn = 7

    def get_marshal(self, name):
        return self.lead if name == "Ney" else None


def _ruin_day():
    return {"lead": "Ney", "enemy": "Mack", "clashes": 3, "toll": {"ours": 9000, "his": 14000},
            "decided_for": "", "name": "The Great Battle of Swabia", "turn": 7}


class TestARuinIsKeptAsDrawn:

    def test_a_day_decided_for_neither_is_drawn(self):
        lead = _Lead()
        BD._keep_his_day(_World(lead), _ruin_day(), "decided")
        assert lead.days[-1]["verdict"] == "drawn"

    def test_seam_down_the_toll_says_it(self, monkeypatch):
        monkeypatch.setattr(BD, "a_ruin_is_kept_as_drawn", lambda: False)
        lead = _Lead()
        BD._keep_his_day(_World(lead), _ruin_day(), "decided")
        assert lead.days[-1]["verdict"] == "won on points"


# ═══════════════════ the reserve: the attacker pursues ═════════════════════

class TestTheAttackerPursues:

    def _counted(self, monkeypatch, attacker=2, defender=1):
        token = BD._WORD.set({"reserve": {"attacker": attacker, "defender": defender}})
        return token

    def test_only_the_attacker_pursues_with_his_own_points(self, monkeypatch):
        monkeypatch.setattr(BD, "the_attacker_pursues", lambda: True)
        monkeypatch.setattr(BD, "reserve_pursuit", lambda: 2000)
        loser = type("L", (), {"strength": 20000, "ability": {}})()
        token = BD._WORD.set({"reserve": {"attacker": 2, "defender": 3}})
        try:
            assert BD.reserve_pursuit_men(attacker_wins=True, loser=loser) == (4000, 2), \
                "his own two points, the loser's three cover him not"
            assert BD.reserve_pursuit_men(attacker_wins=False, loser=loser) == (0, 0), \
                "a defender who throws the attack back does not pursue"
        finally:
            BD._WORD.reset(token)

    def test_the_bA5_form_stays_parked(self):
        assert BD.the_reserve_pursues() is False

    def test_the_rule_picked_nothing_and_the_reserve_is_closed(self):
        """Measured by the rule written before its data: clause iii fails at
        every value (22 of 23 pursuits on a French corps) — not built."""
        record = json.loads((REPO / "tools" / "_ba6_reserve_rule_2026_11_17.json").read_text(encoding="utf-8"))
        assert record["pick"] is None
        for value, row in record["values"].items():
            assert row["clauses"]["iii_neither_side_takes_three_quarters"] is False, value
            assert row["men_from_us"] > 3 * row["men_from_him"], value
        assert BD.the_attacker_pursues() is False and BD._the_reserve_is_counted() is False


# ═══════════════════ the seams ═════════════════════════════════════════════

class TestTheSeams:

    def test_every_seam_is_up_in_the_game_but_the_closed_reserve(self):
        import importlib
        import inspect
        from tests._ba6_seams import BA6_CLOSED, BA6_SEAMS_BY_ROW
        for row, specs in BA6_SEAMS_BY_ROW.items():
            for spec in specs:
                target, expr = spec.split("=", 1)
                module, name = target.split(":", 1)
                fn = getattr(importlib.import_module(module), name)
                assert expr == "False" and not inspect.signature(fn).parameters, spec
                assert fn() is (target not in BA6_CLOSED), (row, spec)
        assert BA6_CLOSED == ["backend.game_logic.battle_day:the_attacker_pursues"]

    def test_every_seam_of_the_court_is_registered(self):
        import inspect
        from backend.game_logic import precedence as P
        from tests._ba6_seams import BA6_SEAMS_DOWN
        registered = {spec.split("=", 1)[0] for spec in BA6_SEAMS_DOWN}
        for name, fn in inspect.getmembers(P, inspect.isfunction):
            if fn.__module__ != P.__name__ or name.startswith("_"):
                continue
            if not inspect.signature(fn).parameters and fn.__annotations__.get("return") in (bool, "bool"):
                assert f"{P.__name__}:{name}" in registered, name

    def test_they_are_folded_into_the_standing_list(self):
        from tests._ba6_seams import BA6_SEAMS_DOWN
        from tests._oct27_seams import OCT27_SEAMS_DOWN
        assert BA6_SEAMS_DOWN and set(BA6_SEAMS_DOWN) <= set(OCT27_SEAMS_DOWN)


# ═══════════════════ every word says what it risks ═════════════════════════

class TestEveryWordSaysWhatItRisks:

    def test_the_risk_follows_the_odds_band_the_card_shows(self):
        assert BT.risk_of("press", {"force": {"odds": "favorable"}}) == BT.RISK_BY_ODDS["favorable"]
        assert BT.risk_of("guard", {"force": {"odds": "unfavorable"}}) == BT.RISK_BY_ODDS["unfavorable"]
        by_count = {"force": {"odds": "", "ours": 30000, "theirs_low": 20000, "theirs_high": 20000}}
        assert BT.risk_of("press", by_count) == BT.RISK_BY_MEN["ours"]
        assert BT.risk_of("dig_in", {}).startswith("he answers next")

    def test_the_free_words_say_their_stakes(self):
        day = {"toll": {"ours": 3790, "his": 6825}}
        assert BT.stakes_of("break_off", day) == (
            "the day ends; he keeps the field; the toll stands at 3,790 of ours for 6,825 of his")
        assert BT.stakes_of("stand", day, reading="he may strike") == "he speaks next — he may strike"

    def test_the_staged_tables_carry_them(self):
        day = json.loads((REPO / "docs/audits/ba1_client/payloads/day_opens.json").read_text(encoding="utf-8"))
        chips = day["day"]["chips"]
        own = [c for c in chips if c["kind"] in ("press", "dig_in") and c.get("ok")]
        assert own and all(c.get("risk") for c in own)
        exits = [c for c in chips if c.get("word") == "break_off"]
        assert exits and "the toll stands" in exits[0]["does"]

    def test_seam_down_no_risk_and_the_old_faces(self, monkeypatch):
        monkeypatch.setattr(BT, "a_word_says_what_it_risks", lambda: False)
        assert BT.risk_of("press", {"force": {"odds": "favorable"}}) == ""


# ═══════════════════ the ground: real surveys ══════════════════════════════

def _lum(rgb):
    import numpy as np
    lin = (np.asarray(rgb, dtype=float) / 255.0) ** 2.2
    return lin[..., 0] * 0.2126 + lin[..., 1] * 0.7152 + lin[..., 2] * 0.0722


class TestTheGroundIsARealSurvey:

    def test_every_terrain_has_its_plates_and_a_sided_kind_both_sides(self):
        from backend.models.region import VALID_TERRAINS
        from tools import ba6_terrain_plates as T
        kinds = {p["kind"] for p in T.PLATES}
        assert set(VALID_TERRAINS) <= kinds
        for kind in ("forest", "urban"):
            assert {p.get("side") for p in T.PLATES if p["kind"] == kind} == {"right", "left"}, kind
        assert not any(p.get("flip") for p in T.PLATES), "a plate is never mirrored: its lettering would read backwards"

    def test_the_client_lays_the_plates_the_tool_makes(self):
        import re
        from tools import ba6_terrain_plates as T
        acts = (REPO / "godot-client/project-sovereign/scripts/battle_acts.gd").read_text(encoding="utf-8")
        ground = acts.split("class Ground:", 1)[1].split("\n# ──", 1)[0]
        named = set(re.findall(r'"([a-z_]+_\d)"', ground))
        assert named == {p["name"] for p in T.PLATES}

    def test_every_plate_is_recorded_with_its_source_and_licence(self):
        record = json.loads((ART / "plates.json").read_text(encoding="utf-8"))
        from tools import ba6_terrain_plates as T
        assert set(record["plates"]) == {p["name"] for p in T.PLATES}
        for name, row in record["plates"].items():
            assert row["licence"].startswith("Public domain") and row["page"].startswith(
                "https://commons.wikimedia.org/wiki/File:"), name
            assert "btv1b" not in row["source"], "nothing from Gallica/BnF (the licence policy)"
        assert record["felt"]["licence"].startswith("CC0")
        licences = (REPO / "THIRD_PARTY_LICENSES.md").read_text(encoding="utf-8")
        assert "## Battle terrain" in licences
        for name in record["plates"]:
            assert f"`{name}.jpg`" in licences, name

    @pytest.mark.parametrize("name", ["plains_1", "plains_2", "plains_3", "forest_1", "forest_2",
                                      "hills_1", "hills_2", "mountains_1", "mountains_2", "urban_1",
                                      "urban_2", "river_crossing_1"])
    def test_a_plate_keeps_every_caption_over_it_legible(self, name):
        """By lamplight: crimson (d7635e, the tightest ink the table sets on the
        sheet) keeps 3 to 1 over the brightest common paper (the 90th
        percentile), bone (c9c2b2) 5 to 1 over the brightest at all (99th)."""
        import numpy as np
        from PIL import Image
        lum = _lum(Image.open(ART / f"{name}.jpg").convert("RGB"))
        p90, p99 = np.percentile(lum, [90, 99])
        crimson, bone = float(_lum([[[0xd7, 0x63, 0x5e]]])[0, 0]), float(_lum([[[0xc9, 0xc2, 0xb2]]])[0, 0])
        assert (crimson + 0.05) / (p90 + 0.05) >= 3.0, (name, p90)
        assert (bone + 0.05) / (p99 + 0.05) >= 5.0, (name, p99)


# ═══════════════════ BA6-X3: the quill stops with its table ════════════════

class TestTheQuillStopsWithItsTable:

    def test_a_table_freed_without_its_close_stops_the_verdicts_quill(self):
        """BA6-X3: a table freed by its owner (the walk's teardown) without its
        Close left the verdict's `scribble_verdict` loop scratching over the
        next table; the host stops it as it leaves the tree."""
        src = (REPO / "godot-client" / "project-sovereign" / "scripts" / "battle_diorama.gd").read_text(
            encoding="utf-8").replace("\r\n", "\n")
        body = src.split("func _exit_tree() -> void:", 1)[1].split("\nfunc ", 1)[0]
        assert 'AudioManager.stop_loop("scribble_verdict")' in body


# ═══════════════════ the ground ships (the review's C16) ═══════════════════

class TestTheGroundShips:

    def test_every_plate_the_client_draws_is_tracked_with_its_sidecar(self):
        """`assets/` is git-ignored (`.gitignore:40`): each plate, the felt, their
        `.import` sidecars and the record are force-added, or a clean clone
        draws the bare felt (the review, C16; RE3-9's census sees only tracked
        assets)."""
        import subprocess
        from tools import ba6_terrain_plates as T
        out = subprocess.run(["git", "ls-files", "--", "godot-client/project-sovereign/assets/textures/battle"],
                             cwd=str(REPO), capture_output=True, text=True)
        if out.returncode != 0:
            pytest.skip("not a git checkout")
        tracked = {Path(line.strip()).name for line in out.stdout.splitlines() if line.strip()}
        art = [f"{p['name']}.jpg" for p in T.PLATES] + ["felt_baize.jpg"]
        missing = [n for n in art + [a + ".import" for a in art] + ["plates.json"] if n not in tracked]
        assert not missing, missing


# ═══════════════════════════ the measure of record ═══════════════════════════

class TestTheMeasureOfRecord:
    """BA-6's one measure (`BATTLE_DIORAMA_SPEC.md` §15.25; `tools/_ba6_measure.py`,
    every chain alone on a frozen copy). Arms 0 … MCRANK are the final chain's;
    the two rows built after it — PEACE (BA6-X8) and SILENCE (the court count's
    find) — each stand LAST on the ladder, so the arms before them read as
    taken, and each was re-taken when it was built: arm PEACE is the chain that
    added it, arm ALL the chain that added SILENCE."""

    STAMP = "2026_11_17"
    COMMANDED = ("CMD-H", "CMD-A", "CMD-M")
    ARMS = ("0", "TELL", "MC0", "MCBOOK", "MCSEEDS", "MCBONDS", "GRD", "WS", "MCRANK", "PEACE", "ALL")

    @staticmethod
    def _load(name):
        import json
        path = REPO / "tools" / name
        assert path.is_file(), f"{name} is not on record"
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _late(arm):
        """The rows that did not yet exist when this arm's chain ran (held down
        by their absence: the commit before's behaviour)."""
        from tools import _ba6_measure as M6
        rows = {"ALL": (), "PEACE": ("SILENCE",)}.get(arm, ("PEACE", "SILENCE"))
        return {f"{spec}=False" for row in rows for spec in M6.LADDER[row]}

    def test_the_ladder_is_the_hold_list(self):
        from tests._ba6_seams import BA6_CLOSED, BA6_SEAMS_DOWN
        from tools import _ba6_measure as M6
        ladder = {f"{spec}=False" for specs in M6.LADDER.values() for spec in specs}
        assert ladder == set(BA6_SEAMS_DOWN) - {f"{c}=False" for c in BA6_CLOSED}
        assert set(M6.held("0")) == ladder and M6.held("ALL") == []
        assert list(M6.LADDER)[-2:] == ["PEACE", "SILENCE"], "the late rows stand last"

    @pytest.mark.parametrize("seed", ["jena", "marengo"])
    def test_arm_0_is_the_commit_before_on_every_key(self, seed):
        probe = self._load(f"_ba6_probe_{self.STAMP}.json")
        cell = probe["arms"]["0"][seed]
        assert cell["vs_head"] == {"identical": True} and cell["keys"] == {}
        assert cell["keys_a_turn"] == 212
        for arm in self.ARMS:
            got = probe["arms"][arm][seed]
            assert got["crashes"] == got["head_crashes"] == 0, (arm, seed)

    @pytest.mark.parametrize("arm", ARMS)
    def test_the_band_holds_on_every_arm(self, arm):
        """The deploy gate's difficulty guard, 23–28, on the commanded arms; arm 0
        reads BA-5's 28 / 28 / 27; each record was run on the ladder as it then stood."""
        from tools import _ba6_measure as M6
        cells = self._load(f"_ba6_band_{self.STAMP}.json")["arms"][arm]
        assert all(cells[n]["ok"] for n in self.COMMANDED)
        got = [cells[n]["provinces"] for n in self.COMMANDED]
        assert all(23 <= g <= 28 for g in got), got
        if arm == "0":
            assert got == [28, 28, 27]
        assert set(cells["seams_held"]) == set(M6.held(arm)) - self._late(arm)

    def test_the_days_sweep(self):
        """Arm 0 equals the day's sweep on the commit before, 72 cells of 72; arm
        ALL is a whole run (every cell ok, forty turns)."""
        s0 = self._load(f"_ba6_sweep_0_{self.STAMP}.json")
        assert s0["cells_moved_vs_commit_before"] == []
        sa = self._load(f"_ba6_sweep_all_{self.STAMP}.json")
        assert sa["held"] == []
        for sweep in (s0, sa):
            assert len(sweep["seeds"]) == 8 and len(sweep["arms"]) == 9
            assert all(sweep["arms"][a][n]["ok"] for a in sweep["arms"] for n in sweep["seeds"])

    def test_off_the_served_road(self):
        """The ambient ten seeds and the AI-France harness: arm 0 is BA-5's final
        tree entry for entry; arm ALL keeps story classes 10 of 10 and no
        annexation outside aim on either surface."""
        sig0, sig5 = (self._load(f"_dy_signature_ba6_0_{self.STAMP}.json"),
                      self._load(f"_dy_signature_ba5_all_{self.STAMP}.json"))
        assert {k: v for k, v in sig0.items() if k != "_note"} == {k: v for k, v in sig5.items() if k != "_note"}
        assert self._load(f"_ba6_0_census_{self.STAMP}.json") == self._load(f"_ba5_all_census_{self.STAMP}.json")
        harness = self._load(f"_ba6_chain_d_{self.STAMP}.json")
        assert harness["arms"]["0"] == self._load(f"_ba5_chain_d_{self.STAMP}.json")["arms"]["ALL"]
        assert self._load(f"_dy_signature_ba6_all_{self.STAMP}.json")["story_class_count"] == 10
        assert self._load(f"_ba6_all_census_{self.STAMP}.json")["totals"]["annexations_outside_aim"] == 0
        assert harness["totals"]["ALL"]["annexations_outside_aim"] == 0

