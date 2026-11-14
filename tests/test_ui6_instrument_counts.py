"""Session UI-6 (November 13, 2026) — UI6-X23, THE COUNT THAT STOPPED AT ONE SHOT.

`tools/iq10_run_captures.py::script_errors` cut the engine log at the FIRST
shot's `[IQ10] END`, so every later shot's `SCRIPT ERROR` went uncounted since
IQ-10: this session's first full shoot printed "SCRIPT ERROR lines: 0" over an
engine log holding 77 (the Generals roster's misspelt overrun property, one a
marshal row). HEAD's three logs were re-read whole: 0 each — UI-5's claim held
in fact. The counter now reads every shot after the first begins; the engine's
exit noise is ERROR / WARNING, never SCRIPT ERROR.
"""

import importlib.util
import pathlib

_RUNNER = pathlib.Path(__file__).resolve().parents[1] / "tools" / "iq10_run_captures.py"


def _runner():
    spec = importlib.util.spec_from_file_location("iq10_run_captures_ui6", _RUNNER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _log(tmp_path, text):
    p = tmp_path / "engine.log"
    p.write_text(text, encoding="utf-8")
    return p


class TestTheCountReadsEveryShot:

    def test_an_error_in_a_later_shot_counts(self, tmp_path):
        log = _log(tmp_path, "\n".join([
            "boot line",
            "SCRIPT ERROR: before any shot (boot noise, not counted)",
            "[IQ10] BEGIN a@1.0",
            "[IQ10] END a@1.0 ok=true",
            "[IQ10] BEGIN b@1.0",
            "SCRIPT ERROR: Invalid assignment of property or key 'x' on a base object of type 'Label'.",
            "   at: Row.setup (res://scripts/row.gd:94)",
            "[IQ10] END b@1.0 ok=true",
            "ERROR: 3 RID allocations were leaked at exit.",
        ]))
        got = _runner().script_errors(log)
        assert len(got) == 1 and "Invalid assignment" in got[0], got

    def test_every_shot_after_the_first_begins_counts(self, tmp_path):
        lines = []
        for i in range(5):
            lines += [f"[IQ10] BEGIN s{i}@2.0", f"SCRIPT ERROR: e{i}", f"[IQ10] END s{i}@2.0 ok=true"]
        got = _runner().script_errors(_log(tmp_path, "\n".join(lines)))
        assert [g.split(": ")[1] for g in got] == ["e0", "e1", "e2", "e3", "e4"]

    def test_a_crashed_shot_still_counts(self, tmp_path):
        log = _log(tmp_path, "[IQ10] BEGIN a@1.0\n[IQ10] END a@1.0 ok=true\n[IQ10] BEGIN b@2.0\n"
                             "SCRIPT ERROR: the last words\nCrashHandlerException: Program crashed with signal 11\n")
        assert _runner().script_errors(log) == ["SCRIPT ERROR: the last words"]

    def test_a_clean_log_is_clean(self, tmp_path):
        log = _log(tmp_path, "[IQ10] BEGIN a@1.0\n[IQ10] END a@1.0 ok=true\nWARNING: ObjectDB instances leaked at exit\n")
        assert _runner().script_errors(log) == []
