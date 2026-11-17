"""Row BA, BA-3 — the day's panel: the session's gate for the client.

Owner: `docs/BATTLE_DIORAMA_SPEC.md` §15.14 (the day's points) and
`docs/SYSTEMS_REFERENCE.md` §221 (the wire, the panel, its traps). The server's
own pins are `tests/test_ba3_the_rounds.py`; this module is the panel as the
real `battle_diorama.tscn` draws it.

Six kinds of pin here:

1. DRIVEN (headless, the scene run eight times faster): the day scenes fought
   fresh on the 1805 board and played by the client; every claim of
   `tools/ba1_acts_walk.check` holds, read off the engine's own record.
2. The walk of record names every day scene and its kept frames exist.
3. The switch-off table: every case finds its anchor in `battle_acts.gd`.
4. The live walks' exported record (`docs/audits/ba3_mode_c_2026_11_15/<board>`):
   six boards, each with its step count, every step held, no script error. Three
   steps are the BEHAVIOUR PINS of ledger rows found by the review and fixed in
   the client: `r11_view_the_field` (BA3-X17: a block that says `follows` never
   replaces the remembered live block), `r12_old_chip` (BA3-X18: a day ended on
   the server unseen leaves no lit chip in an old log line) and `r15_his_clash`
   (BA3-X22: a word given from a table raised over the enemy phase's list is
   answered on that table, and his clash comes on by itself). `panel_points`
   (BA3-X19) pins the province panel's title: "1 POINT", never "1 POINTS".
5. The stager: the guns' day offers all three groups; a day decided by its
   clash carries no banner.
6. The instruments' records on the day's surfaces at the five sizes.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

import ba1_acts_walk as WALK  # noqa: E402
import ba1_stage_battles as STAGE  # noqa: E402
import ba2_switch_off as SWITCH  # noqa: E402

SCRIPTS = REPO / "godot-client" / "project-sovereign" / "scripts"
AUDIT = REPO / "docs" / "audits" / "ba1_client"
LIVE = REPO / "docs" / "audits" / "ba3_mode_c_2026_11_15"
DAY_SCENES = ("day_opens", "day_dim_chip", "day_word", "day_night", "day_defence", "day_follows",
              "day_follows_his", "day_ulm", "day_crowded", "day_guns", "day_decided")
DRIVEN = DAY_SCENES + ("ordinary_brief",)       # the ordinary table: the control, and the chrome's return
LIVE_BOARDS = ("ulm", "massena", "defence", "typed", "r12", "review")
LIVE_STEPS = {"ulm": 4, "massena": 10, "defence": 14, "typed": 6, "r12": 4, "review": 6}
DAY_CASES = (
    "day_hidden_at_opening", "day_chrome", "day_room", "day_latch", "day_dim_draw", "day_dim_press",
    "day_focus", "day_pips", "day_free_price", "day_temper", "day_follows_asks", "day_asks_twice",
    "day_no_script", "day_exits_scroll", "day_sliced", "day_exit_leave", "day_guard_row",
    "day_exits_first", "day_resorted", "day_groups_wrong_index", "day_banner", "day_shelf",
    "day_ulm_scrolls", "day_early_panel", "day_exits_off_centre", "day_head_prefix", "day_his_label",
    "day_his_advance", "day_his_reduced", "day_inline_off", "day_chipless_silent", "day_quill",
    "day_sub_banner", "day_decided_panel")


# ════════════════════════════════════════════════════════════════════════
# 1. Driven: the real tableau plays the day scenes fought today
# ════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="module")
def driven(tmp_path_factory):
    if not Path(WALK.GODOT_DEFAULT).exists():
        pytest.skip("the Godot engine is not on this machine")
    committed = json.loads((AUDIT / "payloads" / "manifest.json").read_text(encoding="utf-8"))
    payload_dir = tmp_path_factory.mktemp("ba3_payloads")
    manifest = {}
    for name in DRIVEN:
        payload, reason, _result = STAGE.fight(name, int(committed[name]["ambient_seed"]))
        assert payload is not None and reason, name
        (payload_dir / f"{name}.json").write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        manifest[name] = {"form": payload["script"]["form"]}
    (payload_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    shots = WALK.build_shots(payload_dir, [], 1.0)
    results, errors = WALK.run(shots, WALK.GODOT_DEFAULT, tmp_path_factory.mktemp("ba3_run"),
                               headless=True, time_scale=8.0)
    return {"shots": shots, "results": results, "errors": errors,
            "by_id": {r["id"]: r for r in results.get("results") or []}}


class TestThePanelDriven:
    def test_the_engine_ran_clean(self, driven):
        assert driven["errors"] == []
        assert len(driven["by_id"]) == len(driven["shots"])
        assert all(r.get("ok") for r in driven["by_id"].values())

    def test_every_claim_of_the_walk_holds(self, driven):
        """The panel is built hidden and comes in when the table is final; the
        verdict, the plate and the seal give it their room; every row whole
        and clear of Replay and Close; the exits centred on the buttons; the
        Guard beside the press; the order of the chips the block's; the banner,
        the sub-banner and the shelf; the quill silent over a day's banner; a
        table that follows says 'His answer' and goes on by itself; a day that
        awaits him asks once."""
        assert WALK.check(driven["results"], driven["shots"]) == []

    def test_the_walk_drove_every_road(self, driven):
        kinds = {sid.rsplit("__", 1)[-1] for sid in driven["by_id"] if "__" in sid}
        assert {"press_lit", "press_word", "press_group", "press_dim", "esc", "then_ordinary",
                "awaits_him", "awaits_him_acts", "awaits_him_skip", "no_script", "no_chips",
                "follows_awaits_him", "goes_on", "stays_reduced", "replays", "no_day"} <= kinds

    def test_the_digits_press_the_days_chips(self, driven):
        """Row BA, BA-4 (the user's ruling at the plan gate — "Yes, on the
        table"): a real key each, through the window's input. The walk's own
        claims ((BA4-k), (BA4-d), checked above) hold that a digit gives its
        fixed slot's word once, that an empty slot, a locked chip and a
        latched table deny, and that a key while the acts play does nothing;
        here: every one of those roads was driven, and on Ulm."""
        kinds = {sid.rsplit("__", 1)[-1] for sid in driven["by_id"] if "__digit_" in sid}
        assert kinds == {"digit_own", "digit_group", "digit_exit", "digit_empty",
                         "digit_locked", "digit_playing"}
        own = WALK._frame(driven["by_id"]["day_ulm__digit_own"], "pressed")
        assert own["emitted"] == ["Ney, attack Mack"] and own["day"]["latched"]
        again = WALK._frame(driven["by_id"]["day_ulm__digit_own"], "pressed_again")
        assert again["emitted"] == ["Ney, attack Mack"] and again["day"]["denied"] == 1
        stand = WALK._frame(driven["by_id"]["day_ulm__digit_exit"], "pressed")
        assert stand["emitted"] == ["@word:stand:Mack"]
        playing = WALK._frame(driven["by_id"]["day_ulm__digit_playing"], "pressed")
        assert playing["emitted"] == [] and not playing["final"]

    def test_the_first_days_line_has_its_row_on_ulm(self, driven):
        """Row BA, BA-4 (the user's tick — "First-open line"): on the first
        great battle of a campaign the line stands on a row of its own above
        the head, no chip scrolls for it, and the table says it showed it; on
        the day with three groups of chips there is no room without a scroll,
        and it rides the head's hover unacknowledged."""
        ulm = WALK._frame(driven["by_id"]["day_ulm__settled"], "settled")["day"]
        row = [ln for ln in ulm["lines"] if ln.get("first")]
        assert len(row) == 1 and row[0]["shown"] and row[0]["box"][1] == 0
        assert row[0]["text"].startswith("The day hangs, Sire.")
        assert ulm["first_shown"] == "battle_day"
        assert not any(ln.get("scroll_active") for ln in ulm["lines"])
        guns = WALK._frame(driven["by_id"]["day_guns__settled"], "settled")["day"]
        assert not [ln for ln in guns["lines"] if ln.get("first")] and guns["first_shown"] == ""
        night = WALK._frame(driven["by_id"]["day_night__settled"], "settled")["day"]
        assert not [ln for ln in night["lines"] if ln.get("first")], "a closed day names no rules"

    def test_a_day_decided_by_its_clash_builds_no_panel(self, driven):
        for tag in ("end",):
            frame = WALK._frame(driven["by_id"]["day_decided"], tag)
            assert not frame["day"]["has"]
            assert frame["verdict_visible"] and frame["plate_visible"]

    def test_the_guns_day_shows_all_three_groups(self, driven):
        settled = WALK._frame(driven["by_id"]["day_guns__settled"], "settled")
        assert settled["day"]["has_groups"] and settled["day"]["has_chips"] and settled["day"]["has_exits"]


# ════════════════════════════════════════════════════════════════════════
# 2. The walk of record
# ════════════════════════════════════════════════════════════════════════

class TestTheWalkOfRecord:
    @pytest.fixture(scope="class")
    def record(self):
        return json.loads((AUDIT / "walk_record.json").read_text(encoding="utf-8"))

    def test_it_walked_every_day_scene_and_kept_its_frames(self, record):
        assert record["headless"] is False and record["time_scale"] == 1.0
        assert record["script_errors"] == [] and record["problems"] == []
        ids = {r["id"] for r in record["results"]}
        for scene in DAY_SCENES:
            assert scene in STAGE.SCENES and {scene, f"{scene}__settled"} <= ids, scene
        kept = {Path(k).name for k in record["frames_kept"]}
        day_frames = [stem for _shot, _tag, stem in WALK.CURATED if int(stem.split("_", 1)[0]) >= 34]
        assert day_frames, "the day's frames are curated"
        for stem in day_frames:
            assert f"BA1_{stem}.jpg" in kept, stem
            assert (AUDIT / f"BA1_{stem}.jpg").is_file(), stem

    def test_the_record_read_the_panel_sources(self, record):
        assert "godot-client/project-sovereign/scripts/battle_acts.gd" in record["sources"]
        assert "backend/game_logic/battle_day.py" in record["sources"]


# ════════════════════════════════════════════════════════════════════════
# 3. The switch-off table
# ════════════════════════════════════════════════════════════════════════

class TestTheSwitchOffTable:
    def test_every_day_case_is_there_and_finds_its_anchor(self):
        keys = [case[0] for case in SWITCH.CASES]
        # 44 at BA-3's close; row BA's BA-4 added six (the digits on the table,
        # the first day's row — `ba4_*`)
        assert len(keys) == len(set(keys)) == 50
        assert [k for k in keys if k.startswith("ba4_")] == [
            "ba4_digit_face", "ba4_digit_press", "ba4_digit_denial", "ba4_digit_at_rest",
            "ba4_first_row_ack", "ba4_first_row_fit"]
        assert set(DAY_CASES) <= set(keys)
        clean = (SCRIPTS / "battle_acts.gd").read_bytes()
        for _key, _name, swaps, *_rest in SWITCH.CASES:
            assert SWITCH.mutated(clean, swaps) != clean

    def test_every_case_names_a_scene_the_walk_stages_and_words_it_must_carry(self):
        for key, _name, _swaps, scenes, speed, words in SWITCH.CASES:
            assert scenes and speed > 0 and words, key
            for scene in scenes.split("|")[0].split(","):
                assert scene in STAGE.SCENES, (key, scene)


# ════════════════════════════════════════════════════════════════════════
# 4. The live walks' exported record
# ════════════════════════════════════════════════════════════════════════

class TestTheLiveWalks:
    @staticmethod
    def _run(board):
        path = LIVE / board / "run.json"
        # the record is part of the session's commit: a missing board is a
        # failure, never a skip (a skip is not a pass)
        assert path.is_file(), f"the live walk of the {board} board is not on record"
        return json.loads(path.read_text(encoding="utf-8"))

    @pytest.mark.parametrize("board", LIVE_BOARDS)
    def test_every_step_of_the_board_held(self, board):
        run = self._run(board)
        walk = run.get("walk") or {}
        assert run.get("engine_exit") == 0 and run.get("script_errors") == []
        assert walk.get("results"), board
        assert walk.get("errors") == []
        assert len(walk["results"]) == LIVE_STEPS[board], board
        bad = [(row["step"], row["saw"]) for row in walk["results"] if not row.get("ok")]
        assert bad == []
        if board == "defence" and run.get("lead_before") and run.get("lead_after"):
            assert run["lead_before"] != run["lead_after"], "the lead fell back"

    @pytest.mark.parametrize("board, step, row", [
        ("typed", "r11_view_the_field", "BA3-X17"),
        ("r12", "r12_old_chip", "BA3-X18"),
        ("review", "r15_his_clash", "BA3-X22"),
        ("massena", "panel_points", "BA3-X19"),
    ])
    def test_the_review_steps_hold(self, board, step, row):
        walk = (self._run(board).get("walk") or {})
        found = [r for r in walk.get("results", []) if r.get("step") == step]
        assert len(found) == 1, f"{row}: step {step} is not on the {board} board's record"
        assert found[0].get("ok") is True, f"{row}: {found[0].get('saw')}"
        if step != "panel_points":
            assert found[0].get("holds") is True and found[0].get("reached") is True, row
        else:
            assert found[0].get("reached") is True and "1 POINT" in found[0].get("title", "")                 and "1 POINTS" not in found[0].get("title", ""), row


# ════════════════════════════════════════════════════════════════════════
# 5. The stager
# ════════════════════════════════════════════════════════════════════════

class TestTheStagedDays:
    @pytest.fixture(scope="class")
    def committed(self):
        return json.loads((AUDIT / "payloads" / "manifest.json").read_text(encoding="utf-8"))

    def test_the_guns_day_offers_all_three_groups(self, committed):
        payload, reason, _ = STAGE.fight("day_guns", int(committed["day_guns"]["ambient_seed"]))
        assert payload is not None and reason
        kinds: dict = {}
        for chip in payload["day"]["chips"]:
            kinds[chip["kind"]] = kinds.get(chip["kind"], 0) + 1
        assert kinds["lead"] >= 2 and kinds["bring_up"] >= 2 and kinds["cannonade"] >= 2
        assert [c["kind"] for c in payload["day"]["chips"][:3]] == ["press", "guard", "dig_in"]
        assert payload["day"]["chips"][-1]["word"] == "leave_it", "Leave it to the lead comes last"

    def test_a_day_decided_by_its_clash_has_no_banner(self, committed):
        payload, reason, _ = STAGE.fight("day_decided", int(committed["day_decided"]["ambient_seed"]))
        assert payload is not None and reason
        assert payload["day"]["open"] is False and payload["day"]["ended"] == "decided"
        assert not payload["day"].get("banner")

    def test_the_manifest_names_every_day_scene(self, committed):
        assert set(DAY_SCENES) <= set(committed) and set(committed) == set(STAGE.SCENES)


# ════════════════════════════════════════════════════════════════════════
# 6. The instruments: the day's surfaces at the five physical sizes
# ════════════════════════════════════════════════════════════════════════

class TestTheInstruments:
    """Nineteen surfaces (the day's tableaux, the province panel, the attack
    card, the enemy phase's list, the rail's notice, the end-turn gate) at the
    five physical sizes with the Interface Scale each derives, at the player's
    default text size (`tools/iq10_run_captures.py --only ba3 --physical`)."""

    STAMP = "ba3_days_points_2026_11_15"

    def _load(self, folder, name):
        path = REPO / "docs" / "audits" / folder / f"{name}_{self.STAMP}.json"
        assert path.is_file(), path.name
        return json.loads(path.read_text(encoding="utf-8"))

    def test_readability_has_no_red_row(self):
        record = self._load("uxr0", "readability")
        assert len(record["surfaces"]) >= 19
        rows = 0
        for name, surface in record["surfaces"].items():
            assert len(surface["readings"]) == 5, name
            for size, reading in surface["readings"].items():
                assert reading["counts"]["red"] == 0 and reading["counts"]["p1"] == 0, (name, size)
                assert abs(float(reading["text_size"]) - 1.15) < 1e-9, "shot at the default text size"
                rows += reading["counts"]["rows"]
        assert rows > 2000

    def test_nothing_reads_under_the_contrast_floor(self):
        record = self._load("uxr0", "contrast")
        for name, surface in record["surfaces"].items():
            for size, reading in surface["readings"].items():
                assert reading["counts"]["under"] == 0, (name, size, reading["under"][:1])

    def test_every_surface_fits_at_every_size(self):
        record = self._load("uxr3", "fit")
        for name, surface in record["surfaces"].items():
            assert set(surface["readings"]) == {"1920x1080", "3840x2160", "5120x1440"}, name
            for size, reading in surface["readings"].items():
                assert reading["ok"], (name, size)
                for key in ("errors", "clipped_text", "truncated_text", "buttons_offscreen", "text_offscreen"):
                    assert reading[key] == [], (name, size, key)

    def test_no_frame_has_a_cut_line_or_an_overlap(self):
        record = self._load("uxr3", "frame_census")
        assert record["frames"] >= 95 and record["frames_without_record"] == []
        assert record["cut_lines"] == [] and record["grip_overlaps"] == [] and record["tick_overlaps"] == []
        assert record["map_overlaps"] == []


# ════════════════════════════════════════════════════════════════════════
# 7. BA3-X2 — BA-2's board at Text size 130 %: the file is the ruled layout,
#    and the table says why (CLOSED by row BA's session BA-4, November 16, 2026)
# ════════════════════════════════════════════════════════

class TestTheOpenBoardRow:
    def test_ba3_x2_at_text_size_1_3_the_file_is_kept_with_its_measured_reason(self, tmp_path):
        """BA3-X2 (CLOSED, row BA's session BA-4). At text size 1.3 BA-2's board
        laid three corps a side as the FILE where the walk's claim asked the
        WEDGE (`ba1_acts_walk._board_claims`: "the table is laid as 'file'; 3
        against 1 corps lay the wedge"). MEASURED first, as the plan ruled
        (`BattleActs.wedge_faults`): the near wing's captions run 19 px below
        the baize and the far wing's stand 18 px on the near wing; two more
        station sets were tried and refused (raised, the far wing stands on
        its loss counter; stepped in beside it, it stands at rest on the
        reserve's note, the losses' caption and the banner). So the file is
        the ruled layout from 120 % up; the table records why it kept it
        (`_laid_why`) and the walk's claim reads that. This test — the row's
        strict xfail until this session, a plain test now — runs exactly the
        walk that reproduced the row (`tools/ba1_acts_walk.py --only
        ulm_full,the_reserve --headless --time-scale 8 --text-size 1.3`) and
        asserts no claim fails AND that the walk noted the measured reason on
        both scenes (a walk that did not run, a script error or a lost shot
        raises RuntimeError: a broken walk can never pass for the fix)."""
        if not Path(WALK.GODOT_DEFAULT).exists():
            pytest.skip("the Godot engine is not on this machine")
        out = subprocess.run(
            [sys.executable, "-X", "utf8", str(REPO / "tools" / "ba1_acts_walk.py"),
             "--only", "ulm_full,the_reserve", "--headless", "--time-scale", "8",
             "--text-size", "1.3", "--tag", "ba3_x2"],
            cwd=str(REPO), capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=900)
        text = (out.stdout or "") + (out.stderr or "")
        done = [ln for ln in text.splitlines() if "shots complete" in ln and "script error(s)" in ln]
        if not done:
            raise RuntimeError("the walk did not run to its end: " + text[-1500:])
        summary = done[-1]
        shots_done, shots_all = summary.split(" shots complete")[0].split("/")
        if shots_done.strip() != shots_all.strip() or ", 0 script error(s)" not in summary:
            raise RuntimeError(f"the walk logged a script error or lost a shot: {summary}")
        if "claim(s) failed" not in summary:
            raise RuntimeError(f"the walk's claim count is not in its output: {summary}")
        claims = [ln[len("CLAIM: "):] for ln in text.splitlines() if ln.startswith("CLAIM: ")]
        assert not claims, claims
        notes = [ln[len("NOTE: "):] for ln in text.splitlines()
                 if ln.startswith("NOTE: ") and "the file is kept at text 1.3" in ln]
        for scene in ("ulm_full", "the_reserve"):
            mine = [n for n in notes if n.startswith(scene + " ")]
            assert mine, f"{scene}: the walk noted no measured reason for the file ({notes})"
            assert all(" — " in n and ("leaves the baize" in n or "meets" in n or "stands on" in n)
                       for n in mine), mine

    def test_at_the_shipped_sizes_a_wedge_not_laid_is_still_a_claim(self):
        """The claim is size-aware, never lenient: up to 115 % the wedge must
        be laid, measured reason or none."""
        frame = {"corps": [{"left": True, "x": 0, "y": 0, "role": ""}] * 3
                 + [{"left": False, "x": 0, "y": 0, "role": ""}],
                 "laid": "file", "laid_why": ["Napoleon: a line leaves the baize (x 14 to 145, y 406 to 459)"]}
        for size in (1.0, 1.15):
            wrong = WALK._board_claims("scene end", frame, size)
            assert wrong and "the table is laid as 'file'" in wrong[0] and "the table's own measure" in wrong[0]
        assert WALK._board_claims("scene end", frame, 1.3) == []
        assert WALK._board_claims("scene end", dict(frame, laid_why=[]), 1.3),             "past 115 % the file needs its measured reason"

