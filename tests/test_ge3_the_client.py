"""Row EP, slice GE-3 — the Congress of Paris's client surfaces, DRIVEN
(review round #58: the harness recorded a JSON no test read).

The IQ-10 `congress` capture group (`tools/iq10_capture_payloads.py --only
congress`) takes REAL backend payloads off staged boards; the GE-3 harness
(`tools/ge3_congress_harness.gd`) boots the REAL `main.tscn` behind an API
stub, hands each payload to the handler the live client hands it to, and
records what the player sees. These pins read that record. They skip without
the engine — and a skip is not a pass, which is why every payload fact is
also pinned engine-free in `tests/test_congress_of_paris.py` and
`tests/test_congress_review_round.py`.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from tests import _chip_census as C

REPO = C.REPO
PROJECT = C.PROJECT
HARNESS = REPO / "tools" / "ge3_congress_harness.gd"
CAPTURE = REPO / "tools" / "iq10_capture_payloads.py"


@pytest.fixture(scope="module")
def driven(tmp_path_factory):
    exe = C.engine()
    if exe is None:
        pytest.skip("Godot engine not on this machine — the driven pins skip, "
                    "and a skip is not a pass")
    work = tmp_path_factory.mktemp("ge3")
    payload_dir = work / "payloads"
    env = dict(os.environ)
    env.pop("PYTHONIOENCODING", None)
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        env.pop(key, None)
    env["INK_IRON_SAVE_DIR"] = str(work / "saves")
    cap = subprocess.run(
        [sys.executable, str(CAPTURE), "--out", str(payload_dir), "--only", "congress"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=900, env=env, cwd=str(REPO))
    if cap.returncode != 0:
        pytest.fail("the congress capture failed\n" + cap.stderr[-2000:])
    out = work / "out.json"
    log = work / "godot.log"
    spec = work / "spec.json"
    spec.write_text(json.dumps({"payload_dir": str(payload_dir), "out": str(out)}),
                    encoding="utf-8")
    genv = dict(env, GE3_SPEC=str(spec), SOVEREIGN_PORT="8997")
    proc = subprocess.run(
        [exe, "--headless", "--path", str(PROJECT), "--log-file", str(log),
         "--script", str(HARNESS)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=300, env=genv, cwd=str(PROJECT))
    if not out.is_file():
        pytest.fail("the harness wrote no result\n"
                    f"exit={proc.returncode}\nstderr tail:\n{proc.stderr[-2000:]}")
    result = json.loads(out.read_text(encoding="utf-8"))
    assert "error" not in result, result.get("error")
    text = log.read_text(encoding="utf-8", errors="replace") if log.is_file() else ""
    result["script_errors"] = text.count("SCRIPT ERROR")
    result["script_error_lines"] = [ln for ln in text.splitlines() if "SCRIPT ERROR" in ln][:10]
    result["payload_dir"] = str(payload_dir)
    return result


def _payload(driven, name):
    return json.loads((Path(driven["payload_dir"]) / name).read_text(encoding="utf-8"))


class TestTheCongressDriven:
    def test_the_harness_ran_clean(self, driven):
        assert driven["script_errors"] == 0, driven["script_error_lines"]
        assert not driven.get("missing_payloads")
        assert driven["ledger_registered"] is True and driven["wizard_registered"] is True

    def test_the_deep_link_opens_the_congress_tab_on_the_sitting(self, driven):
        s = driven["ledger_sitting"]
        assert s["visible"] is True and s["current_tab"] == 6
        assert s["tabs"][6].upper().startswith("CONGRESS")
        assert "THE CONGRESS SITS" in s["text"]
        assert "THE TABLE" in s["text"]
        for court in ("Britain", "Russia", "Austria", "Prussia"):
            assert court in s["text"], court

    def test_a_refusing_court_shows_its_price_or_why_it_will_not_march(self, driven):
        text = driven["ledger_sitting"]["text"]
        assert "Price:" in text
        # Review #4/#23/#54: a countdown is shown only where the war can come;
        # every other refuser says why it will not march — read off the very
        # payload the tab rendered.
        payload = _payload(driven, "diplo_ledger_congress_sitting.json")
        congress = (payload.get("ledger") or payload).get("congress") or {}
        refusers = [c for c in congress.get("courts") or []
                    if c.get("stance") == "REFUSES" and c.get("by") in ("formula", "withdrawn")]
        assert refusers, "the staged sitting has no refuser at peace"
        for row in refusers:
            if "war_in" in row:
                assert "takes up arms against us" in text
            else:
                assert row.get("march_blocker")
                assert "it will not march: " + row["march_blocker"] in text

    def test_a_courts_card_opens_the_cabinet_at_that_court(self, driven):
        s = driven["court_click"]
        assert s["wizard_visible"] is True and s["ledger_visible"] is False
        assert s["wizard_nation"] == "Prussia"

    def test_the_gate_tab_and_the_number_key(self, driven):
        s = driven["ledger_gate"]
        assert s["current_tab"] == 6
        assert "35 of 45 titled" in s["text"]
        assert driven["key_7_selects_tab"] == 6

    def test_the_wizard_row_in_its_three_phases(self, driven):
        assert driven["wizard_gate_summon_disabled"] is True
        gate = json.dumps(driven["wizard_gate"], ensure_ascii=False)
        assert "35 of 45" in gate
        assert driven["wizard_ready_summon_disabled"] is False
        sent = json.dumps(driven["wizard_ready_sent"]).lower()
        assert "summon the congress" in sent
        assert driven["wizard_ready_closed"] is True
        sitting = json.dumps(driven["wizard_sitting"], ensure_ascii=False)
        assert "View the table" in sitting
        assert driven["wizard_sitting_closed"] is True
        view = driven["view_the_table"]
        assert view["visible"] is True and view["current_tab"] == 6

    def test_the_gold_card_is_the_imperial_peace(self, driven):
        s = driven["imperial"]
        assert s["visible"] is True, driven.get("imperial_ahead_of_the_card")
        assert s["title"] == "THE IMPERIAL PEACE"
        assert s["terminal"] is False
        assert "SIGNED" in s["content"]
        # Review #59: the titled count says whose it is.
        assert "titled provinces in the Empire and its satellites" in s["content"]
        assert s["primary"] == "Continue" or "Continue" in s["primary"]
        after = driven["imperial_after_continue"]
        assert after["visible"] is False and after["input_enabled"] is True

    def test_the_clock_line_rides_the_banner_the_r_screen_and_the_territories(self, driven):
        for key in ("dispatch_terminal", "r_screen_text", "ledger_territories_text"):
            assert "CONGRESS" in driven[key].upper(), key

    def test_le_moniteur_prints_the_column(self, driven):
        assert "Congress of Paris" in driven["gazette_text"]
