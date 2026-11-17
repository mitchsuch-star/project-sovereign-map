"""Row BA, BA-1 — the battle in acts: the CLIENT's gate.

Owner: `docs/BATTLE_DIORAMA_SPEC.md` §15 (the gate record of November 14,
2026; §15.5.3 the table; §15.10 the landing record). The backend half — the
script — is `tests/test_battle_script.py`; the dice are
`tests/test_ws11_the_dice_are_the_campaigns.py`.

Three kinds of pin:

1. DRIVEN (the real `battle_diorama.tscn`, headless, the scene run eight
   times faster): three battles are fought fresh on the 1805 board through
   the real attack road and played by the client — the acts end where the
   settled frame stands, a skip gives that frame at once, the Settings
   choices do what they say, an enemy corps comes up dark, a payload from
   before the acts still plays. The claims are `tools/ba1_acts_walk.check`'s,
   read off the engine's own record.
2. The walk of record (`docs/audits/ba1_client/walk_record.json`): the same
   claims over ten staged battles, windowed, with the frames the slice kept.
3. Source pins on the seams: the tableau's four hooks, the Settings row, the
   harness lists, the palette tokens, display-only.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

import ba1_acts_walk as WALK  # noqa: E402
import ba1_stage_battles as STAGE  # noqa: E402

SCRIPTS = REPO / "godot-client" / "project-sovereign" / "scripts"
AUDIT = REPO / "docs" / "audits" / "ba1_client"
DRIVEN_SCENES = ("ulm_full", "enemy_comes", "ordinary_brief")
FIRST_INSTANT_SHOTS = ("ulm_full__skip_at_once", "ulm_full__closed_then_settled")


def _gd(name: str) -> str:
    return (SCRIPTS / name).read_text(encoding="utf-8").replace("\r\n", "\n")


def _func(source: str, name: str) -> str:
    match = re.search(rf"^(?:static )?func {re.escape(name)}\(.*?(?=^(?:static )?func |^class |\Z)",
                      source, re.S | re.M)
    assert match, name
    return match.group(0)


# ════════════════════════════════════════════════════════════════════════
# 1. Driven: the real tableau plays three battles fought today
# ════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="module")
def driven(tmp_path_factory):
    if not Path(WALK.GODOT_DEFAULT).exists():
        pytest.skip("the Godot engine is not on this machine")
    committed = json.loads((AUDIT / "payloads" / "manifest.json").read_text(encoding="utf-8"))
    payload_dir = tmp_path_factory.mktemp("ba1_payloads")
    manifest = {}
    for name in DRIVEN_SCENES:
        payload, reason, _result = STAGE.fight(name, int(committed[name]["ambient_seed"]))
        assert payload is not None and reason, name
        (payload_dir / f"{name}.json").write_text(
            json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        manifest[name] = {"form": payload["script"]["form"]}
    (payload_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    shots = WALK.build_shots(payload_dir, [], 1.0)
    results, errors = WALK.run(shots, WALK.GODOT_DEFAULT, tmp_path_factory.mktemp("ba1_run"),
                               headless=True, time_scale=8.0)
    # The two shots that cut a showing short in its FIRST INSTANT are also run
    # at the scene's own speed: eight times faster, the first frame steps over
    # the quarter-second fade they are about (BA1-X7).
    slow = [s for s in shots if s["id"] in FIRST_INSTANT_SHOTS]
    slow_results, slow_errors = WALK.run(slow, WALK.GODOT_DEFAULT,
                                         tmp_path_factory.mktemp("ba1_run_slow"),
                                         headless=True, time_scale=1.0)
    return {"shots": shots, "results": results, "errors": errors + slow_errors,
            "by_id": {r["id"]: r for r in results.get("results") or []},
            "slow_by_id": {r["id"]: r for r in slow_results.get("results") or []}}


class TestTheActsDriven:
    def test_the_engine_ran_clean(self, driven):
        assert driven["errors"] == []
        # three battles and their settled frames, Ulm's nine settings shots, (BA-2)
        # the old four-seat payload's pair, which every walk carries, (BA-5) Ulm's
        # three shots of the acts' speed and (BA-5's review) Ulm as a liberation's
        # longest line, at the shipped size and at 130 %
        assert len(driven["by_id"]) == len(driven["shots"]) == 22
        assert all(r.get("ok") for r in driven["by_id"].values())
        assert set(driven["slow_by_id"]) == set(FIRST_INSTANT_SHOTS)
        assert all(r.get("ok") for r in driven["slow_by_id"].values())

    def test_every_claim_of_the_walk_holds(self, driven):
        """The acts end on the settled frame; skip, Brief always, Final frame
        only, Reduce motion and Replay do what they say; every act the script
        carries is named; the dark corps is made out; the old payload plays;
        the pips are the rule's; the advance's toll is under the feet."""
        assert WALK.check(driven["results"], driven["shots"]) == []

    def test_a_great_battle_is_told_in_full_and_an_ordinary_one_in_brief(self, driven):
        full = WALK._frame(driven["by_id"]["ulm_full"], "opening")["played"]
        brief = WALK._frame(driven["by_id"]["ordinary_brief"], "opening")["played"]
        assert any(not row["captioned"] for row in full), "the full form moves more than it tells"
        assert all(row["captioned"] for row in brief), "the brief form is its head beats"
        told = sum(row["hold_ms"] for row in full) / 1000.0
        assert 8.0 < told <= WALK_FULL_BUDGET + 1.0, told
        assert sum(row["hold_ms"] for row in brief) / 1000.0 <= WALK_BRIEF_BUDGET + 0.5

    def test_the_acts_come_in_order_on_the_table(self, driven):
        for name in DRIVEN_SCENES:
            played = WALK._frame(driven["by_id"][name], "opening")["played"]
            order = [WALK.ACTS.index(row["act"]) for row in played]
            assert order == sorted(order), (name, order)
            starts = [row["at_ms"] for row in played]
            assert starts == sorted(starts) and len(set(starts)) == len(starts)

    def test_the_table_at_the_crisis_shows_the_dice_and_names_the_act(self, driven):
        frame = WALK._frame(driven["by_id"]["ulm_full"], "crisis")
        assert frame["act"].endswith("THE CRISIS") and frame["dice_shown"] and not frame["final"]
        assert frame["told"].startswith("The fortune of the day: Ney rolls ")

    def test_a_corps_that_marches_in_stands_off_its_place_first(self, driven):
        opening = WALK._frame(driven["by_id"]["ulm_full"], "opening")
        end = WALK._frame(driven["by_id"]["ulm_full"], "end")
        off = {c["name"] for c in opening["corps"] if c["alpha_pct"] < 100 or c["x"] != c["home_x"]}
        assert off and "Ney" not in off and "Mack" not in off
        assert all(c["alpha_pct"] == 100 for c in end["corps"])

    def test_the_beaten_lead_is_driven_back_and_his_plinth_turned_down(self, driven):
        end = WALK._frame(driven["by_id"]["ulm_full"], "end")
        corps = {c["name"]: c for c in end["corps"]}
        mack = corps["Mack"]
        assert mack["status"] == "routed" and mack["face_down"] and not mack["left"]
        assert mack["rest_dx"] > 0, "driven toward his own (the right) edge"
        assert not corps["Ney"]["face_down"] and corps["Ney"]["rest_dx"] >= 0

    def test_ba1_x6_the_table_does_not_tell_the_end_before_the_dice(self, driven):
        """The shipped tableau printed every corps' line whole ("52,000 →
        30,723") from its first frame; over acts of twenty seconds that told
        the day before a die was thrown. The line opens on what the corps
        BROUGHT, runs with the count and ends on its settled words."""
        shot = next(s for s in driven["shots"] if s["id"] == "ulm_full")
        payload = json.loads(Path(shot["payload"]).read_text(encoding="utf-8"))
        beaten = next(c for c in payload["defender"]["contingents"] if c.get("lead"))
        brought, kept = f"{int(beaten['committed']):,}", f"{int(beaten['remaining']):,}"
        assert brought != kept
        ulm = driven["by_id"]["ulm_full"]
        opening, crisis, end = (WALK._frame(ulm, tag) for tag in ("opening", "crisis", "end"))
        shown = [m["text"] for m in opening["marks"] if m["kind"] == "text"]
        assert brought in shown and not [text for text in shown if "→" in text], shown
        running = [label for label in crisis["labels"] if label.startswith(f"{brought} → ")]
        assert len(running) == 1 and running[0] != f"{brought} → {kept}", running
        assert f"{brought} → {kept}" in end["labels"]
        settled = WALK._frame(driven["by_id"]["ulm_full__settled"], "settled")
        assert f"{brought} → {kept}" in settled["labels"]

    def test_ba1_x6_the_laurels_and_the_defeats_cast_come_with_the_gavel(self, driven):
        """Its siblings: what the tableau sets from the battle's RESULT and
        showed from the first frame — the laurels of a triumph and the red
        cast a defeat puts on the baize. Held back while the day is open."""
        registers = {}
        for name in DRIVEN_SCENES:
            shot = next(s for s in driven["shots"] if s["id"] == name)
            register = json.loads(Path(shot["payload"]).read_text(encoding="utf-8"))["register"]
            registers[name] = register
            opening, end = (WALK._frame(driven["by_id"][name], tag) for tag in ("opening", "end"))
            assert opening["laurels"] == 0 and opening["vignette"] == WALK.NEUTRAL_CAST, name
            assert (end["laurels"] == 2) == (register == "triumph"), (name, register)
            assert (end["vignette"] != WALK.NEUTRAL_CAST) == (register == "defeat"), (name, register)
        assert {"triumph", "defeat"} <= set(registers.values()), registers
        # a click mid-act brings them at once, and Replay holds them back again
        skipped = WALK._frame(driven["by_id"]["ulm_full__skip"], "after")
        assert skipped["laurels"] == 2
        final_only = driven["by_id"]["ulm_full__final_only"]
        assert WALK._frame(final_only, "opened")["laurels"] == 2
        assert WALK._frame(final_only, "replaying")["laurels"] == 0
        assert WALK._frame(final_only, "end")["laurels"] == 2

    def test_ba1_x7_a_showing_cut_short_leaves_the_next_table_whole(self, driven):
        """The tray, the laurels and the baize's cast are chrome, built once.
        A click in the tableau's first instant used to leave the tray
        part-faded for good (the first sequence always could — nobody clicked
        the tableau before BA1-X5 let a click on it skip); and Esc mid-act
        would have left BA1-X6's held-back laurels off the next battle. Every
        table that is laid puts the chrome back first."""
        merged = {**driven["by_id"], **driven["slow_by_id"]}
        assert WALK._chrome_claims(merged) == []
        # the laurels: closed mid-act (they are held back), then a battle from
        # before the acts on the same tableau — laid with its laurels at once
        old = driven["by_id"]["ulm_full__closed_then_old"]
        before, playing, end = (WALK._frame(old, tag) for tag in ("before", "playing", "end"))
        assert before["laurels"] == 0 and not before["final"]
        assert playing["laurels"] == 2 and end["laurels"] == 2 and end["final"]
        # the tray: whole after a click in the first instant, and after Esc in
        # the first instant and a settled re-opening — at the scene's own speed
        for rid, tag in (("ulm_full__skip_at_once", "after"),
                         ("ulm_full__closed_then_settled", "seen_again")):
            frame = WALK._frame(driven["slow_by_id"][rid], tag)
            assert frame["final"] and frame["visible"] and frame["tray_alpha_pct"] == 100, (rid, frame["tray_alpha_pct"])
            assert frame["laurels"] == 2


WALK_FULL_BUDGET = 20.0
WALK_BRIEF_BUDGET = 7.5


# ════════════════════════════════════════════════════════════════════════
# 2. The walk of record
# ════════════════════════════════════════════════════════════════════════

class TestTheWalkOfRecord:
    @pytest.fixture(scope="class")
    def record(self):
        return json.loads((AUDIT / "walk_record.json").read_text(encoding="utf-8"))

    def test_it_ran_windowed_at_the_scenes_own_speed_and_clean(self, record):
        assert record["headless"] is False and record["time_scale"] == 1.0 and record["scale"] == 1.0
        assert record["script_errors"] == [] and record["problems"] == []
        assert all(r.get("ok") for r in record["results"])

    def test_it_walked_every_staged_battle_and_every_settings_choice(self, record):
        ids = {r["id"] for r in record["results"]}
        manifest = json.loads((AUDIT / "payloads" / "manifest.json").read_text(encoding="utf-8"))
        assert set(manifest) == set(STAGE.SCENES)
        for scene in manifest:
            assert {scene, f"{scene}__settled"} <= ids, scene
        assert {"ulm_full__skip", "ulm_full__skip_margin", "ulm_full__brief_always", "ulm_full__final_only",
                "ulm_full__reduce_motion", "ulm_full__old_payload", "ulm_full__skip_at_once",
                "ulm_full__closed_then_old", "ulm_full__closed_then_settled"} <= ids

    def test_the_first_instant_shots_caught_the_tableau_mid_fade(self, record):
        """BA1-X7's shots prove something only when the click (or the close)
        lands while the tray is still fading in. At the scene's own speed, in
        a real window, the record shows it did — and the table whole after."""
        by = {r["id"]: r for r in record["results"]}
        for rid, tag in (("ulm_full__skip_at_once", "after"),
                         ("ulm_full__closed_then_settled", "seen_again")):
            assert WALK._frame(by[rid], "fading_in")["tray_alpha_pct"] < 100, rid
            after = WALK._frame(by[rid], tag)
            assert after["tray_alpha_pct"] == 100 and after["final"] and after["laurels"] == 2, rid

    def test_the_record_measures_the_laurels_of_a_triumph(self, record):
        """BA1-X8's measure, on every staged triumph of the walk of record. It
        read the left laurel on the seal and the right one under Replay until
        row BA's BA-5 closed BA1-X8 (November 17, 2026: the laurels flank the
        banner); since, no piece of the plate's furniture stands on another,
        on a triumph as on a plate without laurels. (The pin kept the defect's
        reading after the fix: the final pass's full suite caught it.)"""
        by = {r["id"]: r for r in record["results"]}
        triumphs = plain = 0
        for rid, res in by.items():
            if not rid.endswith("__settled"):
                continue
            frame = WALK._frame(res, "settled")
            if frame["laurels"] == 2:
                triumphs += 1
            else:
                plain += 1
            assert WALK.chrome_overlaps(frame) == [], (rid, WALK.chrome_overlaps(frame))
        assert triumphs >= 3 and plain >= 3

    def test_the_staged_battles_show_what_they_were_staged_for(self):
        manifest = json.loads((AUDIT / "payloads" / "manifest.json").read_text(encoding="utf-8"))
        forms = {name: row["form"] for name, row in manifest.items()}
        assert forms["ulm_full"] == "full" and forms["ordinary_brief"] == "brief"
        registers = {name: row["register"] for name, row in manifest.items()}
        assert registers["defeat_defending"] == "defeat" and registers["observed_full"] == "observer"
        for name, row in manifest.items():
            assert row["shows"] and isinstance(row["ambient_seed"], int), name
            assert (AUDIT / "payloads" / f"{name}.json").exists(), name

    def test_the_frames_it_kept_are_in_the_repo(self, record):
        kept = record["frames_kept"]
        assert len(kept) == len(WALK.CURATED)
        for name in kept:
            assert (AUDIT / name).exists() and (AUDIT / name).stat().st_size > 20_000, name

    def test_the_record_names_what_it_shot(self, record):
        assert set(record["sources"]) == set(WALK.SOURCES)
        assert set(record["payloads"]) >= {f"{name}.json" for name in STAGE.SCENES}


class TestTheTableAtRest:
    """At rest no line of text stands on another or on a portrait, and none
    leaves the baize — at the game's own type size, on a fresh battle. (The
    walk of record holds the same claim over eleven staged battles, four a
    side among them, at Interface Scale 1.0 and 2.0.)"""

    def test_no_words_on_words_and_nothing_off_the_baize(self, driven):
        for name in DRIVEN_SCENES:
            for rid, tag in ((name, "end"), (f"{name}__settled", "settled")):
                frame = WALK._frame(driven["by_id"][rid], tag)
                assert frame["marks"], rid
                assert WALK.overlaps(frame) == [], rid
                assert WALK.off_the_baize(frame) == [], rid

    def test_the_overlap_rule_reads_a_shared_row_and_not_a_stack(self):
        """Two lines on one row that run into each other count (BA1-X1's
        pair); a name over its own figures at the tableau's pitch does not
        (their line boxes overlap by a third; their glyphs do not)."""
        row = {"marks": [
            {"kind": "text", "text": "24,000 → 21,994 → 21,687 after the advance", "rect": [304, 244, 300, 22]},
            {"kind": "text", "text": "52,000 → 30,723", "rect": [535, 244, 107, 22]}]}
        assert len(WALK.overlaps(row)) == 1
        stack = {"marks": [
            {"kind": "text", "text": "Ney ◆", "rect": [322, 226, 46, 25]},
            {"kind": "text", "text": "24,000 → 22,108", "rect": [322, 244, 107, 22]}]}
        assert WALK.overlaps(stack) == []
        under_a_portrait = {"marks": [
            {"kind": "portrait", "text": "Mack", "rect": [650, 224, 76, 76]},
            {"kind": "text", "text": "52,000 → 49,262", "rect": [600, 244, 107, 22]}]}
        assert len(WALK.overlaps(under_a_portrait)) == 1
        assert WALK.off_the_baize({"marks": [
            {"kind": "text", "text": "marched to the guns", "rect": [-4, 203, 125, 22]}]})


class TestBA1X4TheTableAtLargeType:
    """BA1-X4 (OPEN, owner Session H): at Text size 150 % and over the
    tableau's lines outgrow its fixed layout — the standing parts first (a
    name over its own figures, the losses caption over its count), on a
    battle of one corps a side. The pin turns red the day the layout holds,
    so the row is closed with it."""

    @pytest.mark.xfail(strict=True, reason="BA1-X4 OPEN — owner Session H (S15, the deploy)")
    def test_the_table_holds_its_lines_at_text_size_150(self, tmp_path_factory):
        if not Path(WALK.GODOT_DEFAULT).exists():
            pytest.skip("the Godot engine is not on this machine")
        committed = json.loads((AUDIT / "payloads" / "manifest.json").read_text(encoding="utf-8"))
        payload, reason, _result = STAGE.fight(
            "ordinary_brief", int(committed["ordinary_brief"]["ambient_seed"]))
        assert payload is not None and reason
        payload_dir = tmp_path_factory.mktemp("ba1_x4_payloads")
        (payload_dir / "ordinary_brief.json").write_text(
            json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        (payload_dir / "manifest.json").write_text(
            json.dumps({"ordinary_brief": {"form": "brief"}}), encoding="utf-8")
        shots = WALK.build_shots(payload_dir, [], 1.0)
        for shot in shots:
            shot["text_size"] = 1.5
        results, errors = WALK.run(shots, WALK.GODOT_DEFAULT,
                                   tmp_path_factory.mktemp("ba1_x4_run"),
                                   headless=True, time_scale=8.0)
        assert errors == []
        frame = WALK._frame({r["id"]: r for r in results["results"]}["ordinary_brief__settled"],
                            "settled")
        assert frame["marks"]
        assert WALK.overlaps(frame) == [] and WALK.off_the_baize(frame) == []


class TestBA1X8TheLaurelsOfATriumph:
    """BA1-X8 (CLOSED in row BA, BA-5, November 17, 2026 — it was open for
    Session H): on a triumph the left laurel stood on the wax seal and the
    right one under Replay. Session UI-2 had moved the seal to the plate's
    left, clear of the buttons, and the laurels stayed where they had flanked
    a plate without it. No place on the plate's row clears the seal and two
    buttons at every plate width: the laurels now flank the BANNER that
    announces the triumph, on the baize (`battle_diorama.gd` `_laurel_layout`;
    the walk's claim `_laurel_claims`). The xfail went red the day they stood
    clear, and is a plain test since."""

    PIECES = {"seal", "laurel_l", "laurel_r", "replay", "close"}

    def test_the_walk_measures_the_plates_furniture(self, driven):
        """…and finds nothing on a plate that has no laurels, so the pin
        below reads the laurels and not the instrument."""
        triumph = WALK._frame(driven["by_id"]["ulm_full__settled"], "settled")
        assert triumph["laurels"] == 2 and self.PIECES <= set(triumph["chrome"])
        for name in ("enemy_comes", "ordinary_brief"):
            plain = WALK._frame(driven["by_id"][f"{name}__settled"], "settled")
            assert plain["laurels"] == 0 and {"seal", "replay", "close", "plate"} <= set(plain["chrome"])
            assert WALK.chrome_overlaps(plain) == [], name
        assert WALK.chrome_overlaps({"chrome": {"seal": [570, 759, 44, 44], "laurel_l": [582, 776, 34, 34]}})
        assert WALK.chrome_overlaps({"chrome": {"seal": [570, 759, 44, 44], "laurel_l": [520, 776, 34, 34]}}) == []

    def test_the_laurels_stand_clear_of_the_seal_and_the_buttons(self, driven):
        triumph = WALK._frame(driven["by_id"]["ulm_full__settled"], "settled")
        assert WALK.chrome_overlaps(triumph) == []

    def test_they_flank_the_banner_on_the_baize(self, driven):
        triumph = WALK._frame(driven["by_id"]["ulm_full__settled"], "settled")
        left, right = sorted(triumph["laurel_ink"], key=lambda r: r[0])
        banner = triumph["banner_ink"]
        assert left[0] + left[2] <= banner[0] and right[0] >= banner[0] + banner[2]
        assert abs((banner[0] - (left[0] + left[2])) - (right[0] - (banner[0] + banner[2]))) <= 2, "the same gap"
        assert WALK._laurel_claims("ulm", triumph) == []
        # ...and the claim sees a laurel that stands on a word
        on_a_word = dict(triumph, laurel_ink=[list(triumph["marks"][0]["rect"]), right])
        assert any("(BA1-X8)" in line for line in WALK._laurel_claims("ulm", on_a_word))

    def test_the_host_lays_them_by_the_banners_words(self):
        host = _gd("battle_diorama.gd")
        layout = host.split("func _laurel_layout(register: String) -> void:", 1)[1].split("\nfunc ", 1)[0]
        assert "_banner.get_minimum_size().x" in layout and "_nameplate" not in layout
        assert "mid - words / 2.0 - LAUREL_GAP - LAUREL_PX" in layout
        assert "mid + words / 2.0 + LAUREL_GAP" in layout


class TestTheInstruments:
    """The standing instruments on the tableau and on Settings (which gained
    a row), shot at the five physical sizes with the Interface Scale a
    player at each size has: `tools/iq10_capture_payloads.py --only boot
    war_room battles diorama_states battle_acts`, then `tools/iq10_run_captures.py
    --physical --only diorama,war_room_pause_settings,main_menu_settings`."""

    SURFACES = {
        "diorama_aadj", "diorama_dadj", "diorama_rout_conquest", "diorama_four_contingents",
        "diorama_verdict_worst", "diorama_naval",
        "diorama_ba1_field_at_rest", "diorama_ba1_enemy_came_up", "diorama_ba1_the_guns",
        "diorama_ba1_defeat", "diorama_ba1_watched",
        "diorama_ba1_act_approach", "diorama_ba1_act_crisis",
        "war_room_pause_settings", "main_menu_settings",
    }

    @staticmethod
    def _record(folder: str, name: str) -> dict:
        path = REPO / "docs" / "audits" / folder / f"{name}_ba1_battle_acts_2026_11_14.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def test_the_new_states_are_wired_into_the_capture_pipeline(self):
        cap = (REPO / "tools" / "iq10_capture_payloads.py").read_text(encoding="utf-8")
        shots = (REPO / "tools" / "iq10_run_captures.py").read_text(encoding="utf-8")
        assert '"battle_acts": cap_battle_acts,' in cap and 'record(f"diorama_ba1_{name}", payload,' in cap
        for needle in ('"id": f"diorama_ba1_{tag}",', '"id": "diorama_ba1_act_approach",',
                       '"id": "diorama_ba1_act_crisis",', '"steps": [{"call": "_on_replay_pressed"}],'):
            assert needle in shots, needle

    @pytest.mark.parametrize("surface", ["FIELD_AT_REST", "ACT_CRISIS", "DEFEAT"])
    def test_the_acts_are_shot_at_both_interface_scales(self, surface):
        for tail in ("", "_X2"):
            png = REPO / "docs" / "audits" / f"IQ10_DIORAMA_BA1_{surface}{tail}_2026_11_14.png"
            assert png.exists() and png.stat().st_size > 8000, png

    def test_readability_reads_no_red_and_no_p1_at_the_five_sizes(self):
        from uxr0_readability_report import PHYSICAL_RESOLUTIONS
        record = self._record("uxr0", "readability")
        assert set(record["surfaces"]) == self.SURFACES
        rows = 0
        for sid, row in record["surfaces"].items():
            assert len(row["readings"]) == len(PHYSICAL_RESOLUTIONS), sid
            for label, reading in row["readings"].items():
                counts = reading["counts"]
                assert counts["rows"] > 0 and counts["red"] == 0 and counts["p1"] == 0, (sid, label)
                rows += counts["rows"]
        assert rows > 2000

    def test_contrast_reads_nothing_under_its_floor(self):
        record = self._record("uxr0", "contrast")
        assert set(record["surfaces"]) == self.SURFACES
        for sid, row in record["surfaces"].items():
            assert len(row["readings"]) == 5, sid
            for label, reading in row["readings"].items():
                assert reading["counts"]["measured"] > 0 and reading["under"] == [], (sid, label)

    def test_fit_passes_at_the_three_resolutions(self):
        from uxr3_fit_report import FIT_RESOLUTIONS
        record = self._record("uxr3", "fit")
        assert set(record["surfaces"]) == self.SURFACES
        for sid, row in record["surfaces"].items():
            assert set(row["readings"]) == {"%dx%d" % wh for wh in FIT_RESOLUTIONS}, sid
            for label, reading in row["readings"].items():
                assert reading["ok"], (sid, label)
                for key in ("errors", "clipped_text", "truncated_text", "buttons_offscreen",
                            "text_offscreen", "under_modal"):
                    assert reading[key] == [], (sid, label, key)

    def test_the_frame_census_finds_no_cut_line_and_keeps_the_verdicts_room(self):
        record = self._record("uxr3", "frame_census")
        assert record["frames"] == 75 and record["frames_without_record"] == []
        assert record["cut_lines"] == [] and record["grip_overlaps"] == [] and record["tick_overlaps"] == []
        gaps = [g["gap_px"] for g in record["verdict_gaps"]]
        assert len(gaps) == 65 and min(gaps) >= 6.0, min(gaps)


class TestTheContrastInstrumentAndTheFold:
    """The new Settings row moved the scroll's fold one row down, and the
    toggle then cut to 2 px read 3.49 : 1 at two resolutions — its own
    border's colour. A row cut under a third of its height shows no line of
    its text and is not measured (`uxr2b_contrast_report.cut_to_a_sliver`)."""

    def test_a_row_cut_under_a_third_is_not_measured(self):
        import numpy as np
        import uxr2b_contrast_report as CR
        sliver = {"rect": [853.0, 1050.0, 512.0, 2.0], "rect_raw": [853.0, 1050.0, 512.0, 37.0],
                  "colors": ["d9c08cff"]}
        assert CR.cut_to_a_sliver(sliver)
        assert CR.measure_row(sliver, np.full((1200, 1500, 3), 90, dtype=np.uint8), 1.0) is None

    def test_a_row_the_fold_only_trims_is_still_measured(self):
        import numpy as np
        import uxr2b_contrast_report as CR
        img = np.full((1200, 1500, 3), 20, dtype=np.uint8)
        for shown in (13.0, 20.0, 37.0):
            row = {"rect": [853.0, 1050.0, 512.0, shown], "rect_raw": [853.0, 1050.0, 512.0, 37.0],
                   "colors": ["d9c08cff"]}
            assert not CR.cut_to_a_sliver(row)
            assert CR.measure_row(row, img, 1.0) is not None
        assert not CR.cut_to_a_sliver({"rect": [0.0, 0.0, 512.0, 2.0]})   # no raw rect: not judged


# ════════════════════════════════════════════════════════════════════════
# 3. The seams
# ════════════════════════════════════════════════════════════════════════

class TestTheSeams:
    def test_the_tableau_hooks_the_acts_at_four_places_and_nowhere_else(self):
        src = _gd("battle_diorama.gd")
        assert "var _acts: BattleActs = null" in src
        assert "if cinematic and BattleActs.opens_settled():" in _func(src, "show_diorama")
        populate = _func(src, "_populate")
        assert populate.rstrip().endswith("_acts.dress(final_frame)")
        assert "_acts = BattleActs.new(self)" in populate
        play = _func(src, "_play_cinematic")
        assert "if _acts != null and _acts.plays():\n\t\t_acts.play()\n\t\treturn" in play
        assert _func(src, "_apply_final_frame_instant").rstrip().endswith("_acts.settle()")
        assert src.count("_acts.") == 5 and src.count("BattleActs.") == 2

    def test_a_fleet_action_and_an_old_payload_keep_the_first_sequence(self):
        acts = _gd("battle_acts.gd")
        plays = _func(acts, "plays")
        assert "host._is_naval()" in plays and 'get("acts", [])' in plays
        assert "host._is_naval()" in _func(acts, "dress") and "host._is_naval()" in _func(acts, "settle")

    def test_reduce_motion_and_the_final_choice_open_the_battle_settled(self):
        body = _func(_gd("battle_acts.gd"), "opens_settled")
        assert 'mode() == "final"' in body and "UiSettings.get_reduce_motion()" in body

    def test_the_acts_are_display_only(self):
        """Golden Rule 6: nothing here writes a setting, asks the server or
        reads the game — it is fed the tableau's payload."""
        for name in ("battle_acts.gd", "diorama_plinth.gd"):
            src = _gd(name)
            for banned in ("UiSettings.set_", "HTTPRequest", "api_client", "ApiClient",
                           "backend_url", "game_manager", "GameManager"):
                assert banned not in src, (name, banned)

    def test_the_budgets_and_the_brief_rule(self):
        acts = _gd("battle_acts.gd")
        assert f"const FULL_BUDGET_S := {WALK_FULL_BUDGET}" in acts
        assert f"const BRIEF_BUDGET_S := {WALK_BRIEF_BUDGET}" in acts
        assert 'const BRIEF_KEEPS_ONE := ["approach", "cannonade", "assault", "pursuit"]' in acts
        assert "Every act the battle has is NAMED on the table" in _func(acts, "_plan")

    def test_the_plinth_rule(self):
        """Six pips; any loss costs one; only a corps with nothing left has
        lost all six (the walk's mirror is checked against the engine's own
        figures in the driven claims)."""
        plinth = _gd("diorama_plinth.gd")
        assert "const PIPS := 6" in plinth
        body = _func(plinth, "pips_lost")
        assert "return PIPS" in body and "clampi(int(round(float(lost) / float(committed) * PIPS)), 1, PIPS - 1)" in body
        assert [WALK.pips_lost(100, r) for r in (100, 99, 92, 75, 50, 9, 1, 0)] == [0, 1, 1, 2, 3, 5, 5, 6]

    def test_the_settings_row(self):
        settings = _gd("ui_settings.gd")
        assert 'const BATTLE_SCENES := ["acts", "brief", "final"]' in settings
        assert 'const DEFAULT_BATTLE_SCENES := "acts"' in settings
        panel = _gd("settings_panel.gd")
        for label in ('"acts": "In acts (the default)"', '"brief": "Brief always"',
                      '"final": "Final frame only"', 'battle_lbl.text = "Battle scenes"'):
            assert label in panel, label
        assert "and every battle on its final frame." in panel   # Reduce motion's own hint

    def test_the_new_greys_are_palette_tokens(self):
        utils = _gd("utils.gd")
        assert "const UI_PLINTH_FACE_DOWN := Color(0.62, 0.60, 0.58, 1.0)" in utils
        assert "const UI_CORPS_UNSEEN := Color(0.30, 0.27, 0.24, 1.0)" in utils
        assert "const FACE_DOWN := Utils.UI_PLINTH_FACE_DOWN" in _gd("diorama_plinth.gd")
        assert "const UNSEEN := Utils.UI_CORPS_UNSEEN" in _gd("battle_acts.gd")

    def test_the_harness_lists_name_the_new_scripts(self):
        harness = (REPO / "tools" / "godot_parse_check.gd").read_text(encoding="utf-8")
        for path in ("res://scripts/battle_acts.gd", "res://scripts/diorama_plinth.gd",
                     "res://../../tools/ba1_acts_walk.gd"):
            assert f'"{path}"' in harness, path
        stale = (REPO / "tests" / "test_godot_parse_harness.py").read_text(encoding="utf-8")
        assert '"battle_acts.gd"' in stale and '"diorama_plinth.gd"' in stale
        report = json.loads((REPO / "tools" / "godot_parse_report.json").read_text(encoding="utf-8"))
        rows = {row["path"]: row for row in report["scripts"]}
        for path in ("res://scripts/battle_acts.gd", "res://scripts/diorama_plinth.gd",
                     "res://../../tools/ba1_acts_walk.gd"):
            assert rows[path]["parse_ok"] and rows[path]["load_ok"], path
        for name in ("battle_acts.gd.uid", "diorama_plinth.gd.uid"):
            assert (SCRIPTS / name).read_text(encoding="utf-8").startswith("uid://"), name

    def test_ba1_x5_a_click_on_the_tableau_skips(self):
        """A PanelContainer stops the mouse by default: the tableau's frame
        swallowed a click on the tableau, and "click anywhere to skip" was
        true only of the margin. (The driven walk clicks both, for real.)"""
        chrome = _func(_gd("battle_diorama.gd"), "_build_chrome")
        assert "_tray.mouse_filter = Control.MOUSE_FILTER_PASS" in chrome
        assert "_root.mouse_filter = Control.MOUSE_FILTER_STOP" in chrome
        assert "_root.gui_input.connect(_on_root_input)" in chrome
        walk = (REPO / "tools" / "ba1_acts_walk.gd").read_text(encoding="utf-8")
        assert "root.push_input(ev)" in _func(walk, "_click")
        ids = {s["id"]: s for s in WALK.build_shots(AUDIT / "payloads", [], 1.0)}
        assert {"do": "click", "t": 2.7} in [
            {k: e[k] for k in ("do", "t") if k in e} for e in ids["ulm_full__skip"]["events"]]
        assert any(e.get("do") == "click_margin" for e in ids["ulm_full__skip_margin"]["events"])

    def test_ba1_x6_the_acts_hold_the_end_back_and_the_gavel_brings_it(self):
        """Source pins on the seam (the driven pins read the table itself):
        the opening is neutral, the count runs the corps' lines, and the cast
        and the laurels come on the MASTER sequence — the chrome they touch
        outlives a showing, so a tween of its own would go on writing to it
        under a Replay."""
        acts = _gd("battle_acts.gd")
        opening = _func(acts, "_set_opening")
        for needle in ('line.text = str(held.get("strength_brought", line.text))',
                       "toll.visible = false", "host._vignette.modulate = Color.WHITE",
                       "(laurel as CanvasItem).modulate.a = 0.0",
                       "full.substr(0, full.find(RESERVE_DEAD))"):
            assert needle in opening, needle
        play = _func(acts, "play")
        assert "_run_strengths(fight_from, span + 0.4)" in play
        assert 'host._seq.parallel().tween_property(host._vignette, "modulate", _vignette_settled, 0.5)' in play
        assert 'host._seq.parallel().tween_property(laurel, "modulate:a", _laurel_alpha(laurel), 0.5)' in play
        assert "_the_end_is_told()" in _func(acts, "settle")
        rest = _func(acts, "_come_to_rest")
        assert "_tell_the_reserves_dead()" in rest and "_strength_settled(b)" in rest and "_tell_toll(b)" in rest
        assert "_tell_toll(b)" in _func(acts, "_show_beat")
        # the laurels are chrome: their own alpha is read once and kept on the node
        assert 'laurel.set_meta(&"ba_settled_alpha", laurel.modulate.a)' in _func(acts, "_laurel_alpha")
        # a fleet action and a payload from before the acts are never opened this way
        dress = _func(acts, "dress")
        assert "elif plays():\n\t\t_played = _plan()\n\t\t_set_opening()" in dress

    def test_a_line_that_is_not_shown_is_hidden_not_drawn_at_no_alpha(self):
        """The contrast instrument reads every line of text in the tree at the
        colour it is drawn in, alpha and all: a toll held back at alpha 0 read
        1.00 : 1 on both mid-act frames at all five sizes. What the acts hold
        back is taken off the table (`visible = false`) and put back as it
        fades in — the toll, and an unseen corps' name and numbers."""
        acts = _gd("battle_acts.gd")
        opening = _func(acts, "_set_opening")
        assert "toll.visible = false" in opening and "toll.modulate.a = 0.0" not in opening
        assert "(child as Label).visible = false" in opening and "(child as Label).modulate.a = 0.0" not in opening
        assert 'b["unseen_labels"] = unseen' in opening
        tell = _func(acts, "_tell_toll")
        assert "or toll.visible:\n\t\treturn" in tell and "toll.visible = true" in tell
        reveal = _func(acts, "_reveal")
        assert 'for child in b.get("unseen_labels", []):' in reveal
        assert "tw.parallel().tween_callback((child as Label).set_visible.bind(true))" in reveal
        assert "toll.visible = true" in _func(acts, "settle")
        # the record: nothing under the floor on the two mid-act frames
        record = TestTheInstruments._record("uxr0", "contrast")
        for sid in ("diorama_ba1_act_approach", "diorama_ba1_act_crisis"):
            for label, reading in record["surfaces"][sid]["readings"].items():
                assert reading["under"] == [], (sid, label)

    def test_ba1_x7_every_table_that_is_laid_puts_the_chrome_back_first(self):
        """Before the fleet action's early return: a sea battle shown after a
        land battle that was cut short is laid on whole chrome too."""
        acts = _gd("battle_acts.gd")
        dress = _func(acts, "dress")
        # (row BA, BA-5: the acts' speed switch is built between the two — a fleet
        # action plays too — so the pin reads the ORDER it always meant)
        assert "\t_put_the_chrome_back()\n" in dress and "\tif host._is_naval():\n\t\treturn" in dress
        assert dress.index("_put_the_chrome_back()") < dress.index("if host._is_naval():")
        assert dress.index("_build_the_speed()") < dress.index("if host._is_naval():"), "a sea battle has its speed"
        assert dress.index("if host._is_naval():") < dress.index("_build_the_ground()"), "and no ground"
        back = _func(acts, "_put_the_chrome_back")
        assert "host._tray.modulate.a = 1.0" in back
        assert "(laurel as CanvasItem).modulate.a = _laurel_alpha(laurel)" in back
        # the walk's two first-instant shots and its closed-mid-act shot
        ids = {s["id"]: s for s in WALK.build_shots(AUDIT / "payloads", [], 1.0)}
        assert set(FIRST_INSTANT_SHOTS) <= set(ids) and "ulm_full__closed_then_old" in ids
        assert any(e.get("do") == "reopen" and e.get("strip_script") for e in ids["ulm_full__closed_then_old"]["events"])
        walk = (REPO / "tools" / "ba1_acts_walk.gd").read_text(encoding="utf-8")
        assert '"reopen":' in walk and "_node.show_diorama(again, bool(event.get(\"cinematic\", false)))" in walk

    def test_ba1_x1_the_toll_is_told_under_the_feet(self):
        """The lead's strength line keeps two figures; LV-11's toll is the
        same words under the slab (`tests/test_ep_f2_the_display_name_pass.py`
        still finds "→ N after the advance" among the tableau's labels)."""
        body = _func(_gd("battle_acts.gd"), "_advance_toll_under_the_feet")
        assert 'const ADVANCE_TOLL := " after the advance"' in _gd("battle_acts.gd")
        assert "strength.text = strength.text.substr(0, cut)" in body
        assert "strength.size = Vector2(box_w, strength.size.y)" in body
