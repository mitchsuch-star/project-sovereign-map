"""Score Finish Step 8, SF-R "the final reading" — the instrument's last arms
(October 5, 2026).

The baseline left two pillars partly blind: UI/UX NOT EXERCISED (no client arm
in `score_run.py` — "not wired here yet") and command C6 unmeasured (no live
arm, no reader). This slice wires both and re-points HOLD at its fresh blind
script: the client arm (`run --godot`: the IQ-10 payloads, every shot at both
Interface Scales into the run's own `frames/`, the parse harness and a boot
smoke) with the five UI/UX readers; the live-parser arm OP-LIVE (`run --live`
with a key — never on a session exit) with command C6's reader; the frames
runner's `--png-dir`; and the driver's record of the parser a live run
reached. Spec: docs/SCORE_FINISH_SPEC.md §3 Step 8, §4.2, §4.6.

Every reader is driven on a synthetic run directory and read back.
"""
import argparse
import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tools import score_run as SR  # noqa: E402


# ═════════════════════ synthetic run directories ═════════════════════════════

def _arm(run, name, records, meta=None):
    d = run / "arms" / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "meta.json").write_text(json.dumps(meta or {"status": "completed"}), encoding="utf-8")
    (d / "digest.jsonl").write_text("\n".join(json.dumps(r) for r in records), encoding="utf-8")
    (d / "digest.md").write_text("# digest\n", encoding="utf-8")
    return d


def _cmd(text, msg, ok=True, mode="mock", **kw):
    return {"kind": "command", "text": text, "success": ok, "parse_mode": mode,
            "message": msg, **kw}


def _c6(run):
    return SR.r_command_C6(SR.load_arms(run), {"run_dir": run})


REF = [_cmd("Ney, attack Mack", "MUSTER — Ney (24,000) vs Mack at Swabia"),
       _cmd("have the cavalry screen the advance", "Murat scouts Bavaria."),
       _cmd("Soult hold Lorraine", "Soult holds Lorraine."),
       _cmd("what is going on", "I cannot interpret that order, Sire.", ok=False)]


# ═════════════════════ the live arm ══════════════════════════════════════════

class TestTheLiveArm:
    def test_op_live_is_op_on_the_live_parser(self):
        op, live = SR.ARMS["OP"]["argv"], SR.ARMS["OP-LIVE"]["argv"]
        assert live[:len(op)] == op
        assert live[-2:] == ["--llm", "anthropic"], "after the runner's own --llm mock"
        assert SR.ARMS["OP-LIVE"].get("live") is True

    def _select(self, monkeypatch, *, live, key, only=()):
        monkeypatch.setattr(SR, "_live_key", lambda tree: key)
        return SR._select_live_arms(["OP", "OP-LIVE"], argparse.Namespace(live=live),
                                    set(only), REPO)

    def test_a_session_exit_never_spends_api_calls(self, monkeypatch):
        selected, _key = self._select(monkeypatch, live=False, key="k")
        assert selected == ["OP"]

    def test_on_request_with_a_key_it_runs(self, monkeypatch):
        selected, key = self._select(monkeypatch, live=True, key="k")
        assert selected == ["OP", "OP-LIVE"] and key == "k"
        selected, _key = self._select(monkeypatch, live=False, key="k", only=("OP-LIVE",))
        assert "OP-LIVE" in selected

    def test_without_a_key_it_is_skipped(self, monkeypatch):
        selected, key = self._select(monkeypatch, live=True, key="")
        assert selected == ["OP"] and key == ""

    def test_a_placeholder_is_no_key(self, monkeypatch, tmp_path):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.setattr(SR, "ROOT", tmp_path)
        (tmp_path / ".env").write_text("LLM_MODE=mock\nANTHROPIC_API_KEY=your-key-here\n",
                                       encoding="utf-8")
        assert SR._live_key(tmp_path) == ""
        (tmp_path / ".env").write_text("ANTHROPIC_API_KEY=sk-ant-real\n", encoding="utf-8")
        assert SR._live_key(tmp_path) == "sk-ant-real"


# ═════════════════════ command C6 ════════════════════════════════════════════

class TestCommandC6:
    def test_no_live_arm_is_unmeasured(self, tmp_path):
        _arm(tmp_path, "OP", REF)
        assert _c6(tmp_path)["measured"] is False

    def test_no_line_needed_the_model(self, tmp_path):
        _arm(tmp_path, "OP", REF)
        _arm(tmp_path, "OP-LIVE", REF, meta={"status": "completed",
                                             "parser": {"key_status": "connected"}})
        out = _c6(tmp_path)
        assert out["measured"] and out["pass"], out

    def test_a_parse_that_never_reached_the_model_is_unmeasured(self, tmp_path):
        _arm(tmp_path, "OP", REF)
        live = [dict(r) for r in REF]
        live[0]["parser_notice"] = "The parser key was rejected — the offline parser read it."
        _arm(tmp_path, "OP-LIVE", live, meta={"status": "completed",
                                              "parser": {"key_status": "rejected"}})
        out = _c6(tmp_path)
        assert out["measured"] is False and "not reached" in out["evidence"], out

    def test_one_misread_passes(self, tmp_path):
        _arm(tmp_path, "OP", REF)
        live = [dict(r) for r in REF]
        live[1] = _cmd(REF[1]["text"], "Murat attacks Bavaria.", mode="anthropic")
        _arm(tmp_path, "OP-LIVE", live, meta={"status": "completed",
                                              "parser": {"key_status": "connected"}})
        out = _c6(tmp_path)
        assert out["pass"] and "misreads 1" in out["evidence"], out

    def test_two_misreads_fail(self, tmp_path):
        """The first misread does not hide the second: a model-read line that
        differs is the reading under test, not evidence the boards parted."""
        _arm(tmp_path, "OP", REF)
        live = [dict(r) for r in REF]
        live[0] = _cmd(REF[0]["text"], "Ney marches on Swabia.", mode="anthropic")
        live[1] = _cmd(REF[1]["text"], "Murat attacks Bavaria.", mode="anthropic")
        _arm(tmp_path, "OP-LIVE", live, meta={"status": "completed"})
        out = _c6(tmp_path)
        assert out["measured"] and not out["pass"] and "misreads 2" in out["evidence"], out

    def test_a_line_after_the_boards_part_is_unjudged(self, tmp_path):
        ref = REF + [_cmd("Lannes, drill", "Lannes drills his corps.")]
        _arm(tmp_path, "OP", ref)
        live = [dict(r) for r in ref]
        live[1] = _cmd(ref[1]["text"], "Murat attacks Bavaria.", mode="anthropic")
        live[2] = _cmd(ref[2]["text"], "Soult is engaged and cannot hold.", ok=False)  # offline
        live[4] = _cmd(ref[4]["text"], "Lannes marches.", mode="anthropic")
        _arm(tmp_path, "OP-LIVE", live, meta={"status": "completed"})
        out = _c6(tmp_path)
        assert "misreads 1" in out["evidence"] and "unjudged) 1" in out["evidence"], out

    def test_a_line_the_offline_parser_shrugged_is_rescued_not_misread(self, tmp_path):
        _arm(tmp_path, "OP", REF)
        live = [dict(r) for r in REF]
        live[3] = _cmd(REF[3]["text"], "Sire — the board stands so: …", mode="anthropic")
        _arm(tmp_path, "OP-LIVE", live, meta={"status": "completed"})
        out = _c6(tmp_path)
        assert out["pass"] and "misreads 0" in out["evidence"] and "rescued 1" in out["evidence"]

    def test_a_line_lost_on_both_is_no_rescue(self, tmp_path):
        """Measured on c20d5bba: the model answered "I confess I am at a loss"
        where the offline parser shrugged — a refusal on both roads."""
        _arm(tmp_path, "OP", REF)
        live = [dict(r) for r in REF]
        live[3] = _cmd(REF[3]["text"], "Sire, I confess I am at a loss.", ok=False,
                       mode="anthropic")
        _arm(tmp_path, "OP-LIVE", live, meta={"status": "completed"})
        out = _c6(tmp_path)
        assert "rescued 0" in out["evidence"] and "lost on both 1" in out["evidence"], out


# ═════════════════════ the client arm's readers ══════════════════════════════

def _frame(**kw):
    base = {"blank": False, "buttons_offscreen": [], "clipped_text": [],
            "texts": [{"class": "Label", "path": "x", "text": "Kingdom of Italy"}]}
    base.update(kw)
    return base


def _cli(run, frames, *, exit_code=0, errors=(), cli=None):
    d = run / "arms" / "CLI"
    d.mkdir(parents=True, exist_ok=True)
    (d / "index.json").write_text(json.dumps({
        "exit_code": exit_code, "script_errors": list(errors),
        "rows": [{"id": "s", "results": [{"ok": True, "scale": 1.0, "frames": frames}]}],
    }), encoding="utf-8")
    (d / "cli.json").write_text(json.dumps(cli or {
        "parse_exit": 0, "boot_exit": 0, "boot_script_errors": 0, "boot_log_bytes": 500,
    }), encoding="utf-8")


def _ui(run, item):
    return getattr(SR, f"r_ui_ux_{item}")({}, {"run_dir": run})


class TestTheClientArmReaders:
    @pytest.mark.parametrize("item", ["F1", "F2", "C1", "C2", "C3"])
    def test_no_client_arm_is_unmeasured(self, tmp_path, item):
        assert _ui(tmp_path, item)["measured"] is False

    def test_a_clean_run_passes_all_five(self, tmp_path):
        _cli(tmp_path, [_frame(), _frame()])
        for item in ("F1", "F2", "C1", "C2", "C3"):
            out = _ui(tmp_path, item)
            assert out["measured"] and out["pass"], (item, out)

    def test_f1_a_blank_frame_or_a_script_error_fails(self, tmp_path):
        _cli(tmp_path, [_frame(blank=True)])
        assert _ui(tmp_path, "F1")["pass"] is False
        _cli(tmp_path, [_frame()], errors=["SCRIPT ERROR: x"])
        assert _ui(tmp_path, "F1")["pass"] is False

    def test_f2_the_parse_harness_and_the_boot_smoke(self, tmp_path):
        _cli(tmp_path, [_frame()], cli={"parse_exit": 1, "boot_exit": 0,
                                        "boot_script_errors": 0, "boot_log_bytes": 500})
        assert _ui(tmp_path, "F2")["pass"] is False
        _cli(tmp_path, [_frame()], cli={"parse_exit": 0, "boot_exit": 0,
                                        "boot_script_errors": 1, "boot_log_bytes": 500})
        assert _ui(tmp_path, "F2")["pass"] is False

    def test_c1_and_c2_name_the_frame(self, tmp_path):
        _cli(tmp_path, [_frame(buttons_offscreen=["Ratify"])])
        out = _ui(tmp_path, "C1")
        assert out["pass"] is False and "Ratify" in out["evidence"]
        _cli(tmp_path, [_frame(clipped_text=["Rich"])])
        assert _ui(tmp_path, "C2")["pass"] is False

    @pytest.mark.parametrize("text", ["KingdomOfItaly holds Milan", "Archduke: <null>",
                                      "2 turn(s) left", "ArchdukeCharles retreats"])
    def test_c3_a_raw_key_null_or_hedge_fails(self, tmp_path, text):
        _cli(tmp_path, [_frame(texts=[{"class": "Label", "path": "x", "text": text}])])
        assert _ui(tmp_path, "C3")["pass"] is False

    def test_c3_the_keys_are_the_scenarios_own(self):
        rx = SR._raw_key_rx()
        for key in ("KingdomOfItaly", "PapalStates", "ArchdukeJohn", "DuchyOfWarsaw"):
            assert rx.search(f"the {key} line"), key
        for prose in ("Kingdom of Italy", "the Papal States", "Archduke John", "Milan"):
            assert not rx.search(prose), prose


# ═════════════════════ the frames runner and the driver ══════════════════════

class TestTheRunnerAndTheDriver:
    def test_the_runner_writes_frames_where_it_is_told(self, tmp_path):
        import importlib.util
        spec = importlib.util.spec_from_file_location("_iq10_runner_s8",
                                                      REPO / "tools" / "iq10_run_captures.py")
        runner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(runner)
        row = runner.SHOTS[0]
        caps = {row["payload"]: {"file": "x.json", "staging": "", "facts": {}}}
        built, _index = runner.build_spec([row], caps, [1.0, 2.0], "pin", tmp_path / "s.json",
                                          tmp_path / "r.json", tmp_path / "frames")
        outs = built["shots"][0]["out"].values()
        assert all(str(o).startswith(str(tmp_path / "frames")) for o in outs), outs
        built, _index = runner.build_spec([row], caps, [1.0], "pin", tmp_path / "s.json",
                                          tmp_path / "r.json")
        assert str(list(built["shots"][0]["out"].values())[0]).startswith(str(runner.AUDITS))

    def test_the_packet_carries_the_frames_and_their_index(self, tmp_path):
        (tmp_path / "frames").mkdir()
        (tmp_path / "frames" / "IQ10_X_2026_10_05.png").write_bytes(b"png")
        _cli(tmp_path, [_frame()])
        SR.cmd_packet(argparse.Namespace(run=str(tmp_path)))
        frames = tmp_path / "panel_packet" / "frames"
        assert (frames / "IQ10_X_2026_10_05.png").exists()
        assert json.loads((frames / "index.json").read_text(encoding="utf-8"))["rows"]

    def _digest(self, tmp_path):
        import tools.playtest_driver as PD
        return PD, PD.Digest(tmp_path, {"name": "t", "seed": "historical", "llm": "anthropic",
                                        "transport": "in-process", "policy": {}})

    def _last(self, tmp_path):
        lines = (tmp_path / "digest.jsonl").read_text(encoding="utf-8").splitlines()
        return json.loads([x for x in lines if x.strip()][-1])

    def test_the_driver_records_a_failed_live_parse(self, tmp_path):
        _PD, d = self._digest(tmp_path)
        d.command("Ney, attack Mack", {"success": True, "message": "MUSTER",
                                       "parse_mode": "mock",
                                       "parser_notice": "The parser key was rejected."})
        assert self._last(tmp_path)["parser_notice"] == "The parser key was rejected."

    def test_lever_down_the_record_is_as_it_was(self, tmp_path, monkeypatch):
        PD, d = self._digest(tmp_path)
        monkeypatch.setattr(PD, "THE_DIGEST_RECORDS_THE_LIVE_PARSER", False)
        d.command("Ney, attack Mack", {"success": True, "message": "MUSTER",
                                       "parser_notice": "The parser key was rejected."})
        assert "parser_notice" not in self._last(tmp_path)


# ═════════════════════ the SUITE arm runs as the hook runs ═══════════════════

class TestTheSuiteArm:
    """Found on the final reading: the arm handed its pytest children
    PYTHONIOENCODING=utf-8, and the BASELINE_SERIES pin — which decodes its own
    child's output in the console code page — errored at setup (3 errors; the
    same tests green in the pre-commit hook the same hour)."""

    def test_the_suite_runs_without_pythonioencoding(self, tmp_path, monkeypatch):
        seen = []

        class _Done:
            returncode, stdout, stderr = 0, "1 passed", ""

        def _fake_run(cmd, **kw):
            seen.append(kw.get("env") or {})
            return _Done()

        monkeypatch.setattr(SR.subprocess, "run", _fake_run)
        monkeypatch.setattr(SR, "SUITE_FILES", ["tests/test_score_finish_step8.py"])
        SR._run_suite(REPO, tmp_path)
        assert seen and all("PYTHONIOENCODING" not in env for env in seen), seen[:1]
        assert all(env.get("LLM_MODE") == "mock" for env in seen)


# ═════════════════════ HOLD, written fresh ═══════════════════════════════════

class TestTheFreshHold:
    def _script(self):
        return json.loads((REPO / SR.SCRIPTS / SR.HOLD_SCRIPT).read_text(encoding="utf-8"))

    def test_hold_points_at_the_fresh_blind_script(self):
        assert SR.HOLD_SCRIPT == "score_hold_2026_10_05.json"
        s = self._script()
        assert s["name"] == "score-hold-2026-10-05" and "blind" in s["_note"]

    def test_twenty_and_twenty_each_typed_once(self):
        s = self._script()
        qs, os_ = s["hold"]["questions"], s["hold"]["orders"]
        assert len(qs) == 20 and len(os_) == 20
        assert s["turns"]["1"] == [q["line"] for q in qs]
        assert s["turns"]["2"] == [o["line"] for o in os_]
        lines = s["turns"]["1"] + s["turns"]["2"]
        assert len(set(lines)) == 40

    def test_every_intended_action_is_one_the_judge_reads(self):
        from tools import _score_probes as P
        for o in self._script()["hold"]["orders"]:
            assert o["intended"]["action"] in P.ACTION_WORDS, o


# ═════════════════════ the panel (§4.5) ══════════════════════════════════════

class TestThePanel:
    """`tools/score_panel.py` — the EYES marks two of three agree on, and the
    published median and spread over each scorer's anchor + clamped feel."""

    @staticmethod
    def _answers(*eyes_votes, adjusts=(0, 0, 0)):
        out = []
        for i in range(3):
            vote = eyes_votes[i] if i < len(eyes_votes) else None
            out.append({"narration": {
                "anchor": 7.5, "adjust": adjusts[i],
                "eyes": {"C6": {"pass": vote, "cite": f"scorer {i + 1}"}},
                "cite": "a line"}})
        return out

    def test_two_of_three_make_the_mark(self):
        from tools import score_panel as SP
        marks = SP.majority_eyes(self._answers(False, False, None))
        assert marks["narration.C6"]["pass"] is False
        assert "panel 2 of 3" in marks["narration.C6"]["evidence"]
        assert SP.majority_eyes(self._answers(True, True, True))["narration.C6"]["pass"] is True

    def test_one_vote_is_no_mark(self):
        from tools import score_panel as SP
        assert "narration.C6" not in SP.majority_eyes(self._answers(True, None, None))

    def test_a_split_with_cannot_judge_is_no_mark(self):
        from tools import score_panel as SP
        assert "narration.C6" not in SP.majority_eyes(self._answers(True, False, None))

    def test_the_feel_is_clamped_to_a_quarter(self):
        from tools import score_panel as SP
        scores = {"pillars": {"narration": {"low": 7.5}}}
        panel = SP.publish(self._answers(adjusts=(0.5, -1, 0)), scores)
        assert [p["narration"]["score"] for p in panel["panels"]] == [7.75, 7.25, 7.5]

    def test_the_median_and_the_spread_are_published(self):
        from tools import score_panel as SP
        scores = {"pillars": {"narration": {"low": 7.5}}}
        pub = SP.publish(self._answers(adjusts=(0, -0.25, -0.25)), scores)["published"]["narration"]
        assert (pub["median"], pub["spread"], pub["anchor"]) == (7.25, 0.25, 7.5)

    def test_compare_reads_what_publish_writes(self):
        from tools import score_panel as SP
        scores = {"pillars": {"narration": {"low": 7.5}}}
        panel = SP.publish(self._answers(adjusts=(0.25, 0, 0)), scores)
        assert SR._panel_median(panel, "narration") == (7.5, 0.25)
