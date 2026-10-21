"""Score Finish residue 4 — SF-RR5 "the frames at both scales" (October 21, 2026).

The rows: `docs/BUG_FIXES.md` §Score Finish Step 8 (SFR-B10, SFR-B11), §The
Economy Audit (EA-E1, EA-E2, EA-E3, EA-E5, EA-E6, EA-E7, EA-E9), the agendas
C6 re-shoot, and the siblings the reproduction and the sweep found, §RR5
(RR5-X1 …). Rules: `docs/SYSTEMS_REFERENCE.md` §140.

Every row was reproduced on its IQ-10 frame first — the whole table shot at
Interface Scale 1.0 and 2.0 on the entry tree (`43f5b204`). Three did not
reproduce: SFR-B10 (the standard and the Close button were moved clear by
Pre-Deploy S12 part 2, UXR3-F2), EA-E3 (the blockade border has been crimson
since UXR3-F9) and EA-E7 (the filigree sits in the padding band since
UXR3-F4); their pins hold today's frame. The agendas C6 re-shoot reads clean
(EA-E8 fixed its "Loading…" frame in the economy gate).

THE DRIVEN PINS run the IQ-10 harness itself, HEADLESS, in its record-only
mode (`record_only` in the spec — no picture, the same record), on payloads
`tools/iq10_capture_payloads.py` captures off the rows' own boards. They read
what a player SEES: an answer below a scroll fold (a button outside its
scroll's window or the viewport), a word below a fold (`seen_text`: whole
lines inside the window), a glyph drawn at no width. The layout a headless
run computes is the windowed one's (measured: every button rect equal on
twenty surfaces at both scales). Every pin of a reproduced row went red on the
entry tree and green on the slice's.
"""

from __future__ import annotations

import json
import os
import pathlib
import re
import subprocess
import sys

import pytest

from tests import _chip_census as C

REPO = pathlib.Path(__file__).resolve().parents[1]
PROJECT = REPO / "godot-client" / "project-sovereign"
SCRIPTS = PROJECT / "scripts"
SCENES = PROJECT / "scenes"
ICONS = PROJECT / "assets" / "ui" / "icons"
TOOLS = REPO / "tools"
AUDITS = REPO / "docs" / "audits"
FRAME_DATE = "2026_10_21"

# The capture groups the rows' boards live in, and the shots read here.
GROUPS = ["boot", "battles", "layout_f3", "proclamation", "popups_s12",
          "frames_s9", "petition", "peace", "screen_says", "user_saves", "collapse"]
DECISION_MODALS = [
    "objection_dialog", "capture_choice", "talleyrand_objection",
    "interrupt_last_stand", "petition_command_closed", "petition_popup",
    "petition_popup_no_dp", "incoming_peace_losing", "confirm_peace_losing",
    "settlement_three_courts", "settlement_white_review_ratify",
    "settlement_white_review_holdout", "proclamation_warsaw", "reward_dialog",
]
# A shot whose board is a staged save under `saves/` (gitignored) shoots only
# on a machine that holds it; elsewhere its pins skip — a skip is not a pass.
STAGED_SAVE_SHOTS = {"reward_dialog"}
SHOTS = DECISION_MODALS + [
    "wizard_step2_austria", "wizard_step2_prussia", "wizard_formables_entry",
    "generals_boot", "top_bar_boot", "top_bar_admiralty",
    "diorama_dadj", "diorama_aadj",
]
SCALES = (1.0, 2.0)


def _read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def _func_body(src: str, name: str) -> str:
    at = src.index(f"func {name}(")
    ends = [i for i in (src.find("\nfunc ", at + 10), src.find("\nstatic func ", at + 10)) if i != -1]
    return src[at:min(ends) if ends else len(src)]


def _runner():
    import importlib.util
    spec = importlib.util.spec_from_file_location("_rr5_runner", TOOLS / "iq10_run_captures.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ═══════════════════════════════════════════════════════════════════════════
# The record: the harness itself, headless, on the rows' own payloads
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture(scope="module")
def record(tmp_path_factory):
    exe = C.engine()
    if exe is None:
        pytest.skip("Godot engine not on this machine — the driven pins skip, "
                    "and a skip is not a pass")
    work = tmp_path_factory.mktemp("rr5")
    payloads = work / "payloads"
    env = dict(os.environ)
    env.pop("PYTHONIOENCODING", None)
    cap = subprocess.run(
        [sys.executable, str(TOOLS / "iq10_capture_payloads.py"), "--out", str(payloads),
         "--only", *GROUPS],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=900, env=env, cwd=str(REPO), stdin=subprocess.DEVNULL)
    assert cap.returncode == 0, f"the capture failed:\n{cap.stdout[-2500:]}\n{cap.stderr[-1500:]}"
    runner = _runner()
    rows = [r for r in runner.SHOTS if r["id"] in SHOTS]
    assert {r["id"] for r in rows} == set(SHOTS)
    manifest = runner.load_manifest(payloads)
    absent = {r["id"] for r in rows if r["payload"] not in manifest}
    assert absent <= STAGED_SAVE_SHOTS, absent
    spec_path, result_path = work / "spec.json", work / "result.json"
    spec, _index = runner.build_spec(rows, manifest, list(SCALES),
                                     "rr5", spec_path, result_path, work / "png")
    spec["record_only"] = True
    spec_path.write_text(json.dumps(spec, indent=1), encoding="utf-8")
    log = work / "engine.log"
    env.update({"IQ10_SPEC": str(spec_path), "SOVEREIGN_PORT": runner.HARNESS_PORT})
    proc = subprocess.run(
        [exe, "--headless", "--audio-driver", "Dummy", "--log-file", str(log),
         "--path", str(PROJECT), "--script", runner.SCRIPT],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=900, env=env, cwd=str(REPO), stdin=subprocess.DEVNULL)
    if not result_path.is_file():
        pytest.fail(f"the harness wrote no result\nexit={proc.returncode}\n{proc.stderr[-2000:]}")
    result = json.loads(result_path.read_text(encoding="utf-8"))
    frames = {}
    for row in result.get("results", []):
        for frame in row.get("frames", []):
            frames[(row["id"], float(row["scale"]))] = frame
    return {"frames": frames, "results": result.get("results", []), "absent": absent,
            "script_errors": runner.script_errors(log), "payloads": payloads}


def _payload(record, name: str) -> dict:
    return json.loads((record["payloads"] / f"{name}.json").read_text(encoding="utf-8"))


def _frame(record, shot: str, scale: float) -> dict:
    if shot in record["absent"]:
        pytest.skip(f"{shot}: its staged save is not on this machine")
    frame = record["frames"].get((shot, scale))
    assert frame is not None, f"no frame for {shot} at {scale}"
    return frame


def _inside(r, s, tol: float = 1.0) -> bool:
    return (r[0] >= s[0] - tol and r[1] >= s[1] - tol
            and r[0] + r[2] <= s[0] + s[2] + tol and r[1] + r[3] <= s[1] + s[3] + tol)


def _folded(frame: dict) -> list:
    """The buttons a player cannot see whole: outside the viewport, or
    outside the window of the scroll that holds them."""
    view = [0.0, 0.0] + list(frame.get("logical_viewport") or [0.0, 0.0])
    out = []
    for b in frame.get("buttons") or []:
        r = b["rect_raw"]
        if r[2] <= 0 or r[3] <= 0:
            continue
        s = b.get("scroll_rect")
        if not _inside(r, view) or (s is not None and not _inside(r, s)):
            out.append(b["text"] or b["path"])
    return out


def _seen(frame: dict) -> str:
    return "\n".join(e.get("seen", "") for e in frame.get("seen_text") or [])


def _button(frame: dict, text: str) -> dict:
    hits = [b for b in frame.get("buttons") or [] if b["text"].startswith(text)]
    assert hits, f"no button '{text}' in {[b['text'] for b in frame.get('buttons') or []]}"
    return hits[0]


class TestTheRecord:

    def test_the_harness_ran_clean_and_shot_every_row_at_both_scales(self, record):
        assert record["script_errors"] == [], record["script_errors"]
        for shot in SHOTS:
            for scale in SCALES:
                if shot not in record["absent"]:
                    _frame(record, shot, scale)
        bad = [(r["id"], r["scale"], r.get("errors")) for r in record["results"] if not r.get("ok")]
        assert bad == [], bad

    def test_the_harness_has_a_record_only_road(self):
        gd = _read(TOOLS / "iq10_surface_screenshot.gd")
        capture = _func_body(gd, "_capture")
        assert 'bool(_spec.get("record_only", false))' in capture
        assert "elif not _save_png(path, frame):" in capture
        assert 'frame["seen_text"] = _seen_text()' in capture
        assert "rtl.get_character_line(ci)" in _func_body(gd, "_rtl_seen")


# ═══════════════════════════════════════════════════════════════════════════
# The class: a 2.0 decision modal shows every answer above the fold
# ═══════════════════════════════════════════════════════════════════════════


class TestEveryDecisionModalShowsItsAnswers:

    @pytest.mark.parametrize("shot", DECISION_MODALS)
    @pytest.mark.parametrize("scale", SCALES)
    def test_no_answer_sits_below_a_fold(self, record, shot, scale):
        frame = _frame(record, shot, scale)
        assert _folded(frame) == [], f"{shot} at {scale}: answers below a fold"

    @pytest.mark.parametrize("shot", DECISION_MODALS)
    @pytest.mark.parametrize("scale", SCALES)
    def test_it_stands_below_the_bar_and_inside_the_window(self, record, shot, scale):
        """The clamp's band: under the top bar (36 + 8) and 12 from every
        other edge. At 2.0 the settlement table's floors held it 397 px tall
        in a 362-px band — its top 10 px over the bar's strip."""
        frame = _frame(record, shot, scale)
        vw, vh = frame["logical_viewport"]
        panels = [r for k, r in frame["surfaces"].items() if k.endswith("/PanelContainer")]
        assert panels, list(frame["surfaces"])
        for r in panels:
            assert r[1] >= 44.0 - 0.5 and r[1] + r[3] <= vh - 12.0 + 0.5, (shot, scale, r)
            assert r[0] >= 12.0 - 0.5 and r[0] + r[2] <= vw - 12.0 + 0.5, (shot, scale, r)

    def test_the_clamp_stands_a_tall_panel_below_the_bar(self):
        src = _read(SCRIPTS / "utils.gd")
        clamp = _func_body(src, "clamp_centered_panel")
        assert "var below_h: float = view.y - below_top - CLAMP_EDGE" in clamp
        assert "panel.offset_top = below_top - view.y / 2.0" in clamp
        assert "const CLAMP_EDGE := 12.0" in src
        relax = _func_body(src, "_relax_child_minimums")
        assert "_relax_floor(control)" in relax and "_RELAX_FLOOR" not in relax


# ═══════════════════════════════════════════════════════════════════════════
# SFR-B11 — the Proclamation and the petition at Interface Scale 2.0
# ═══════════════════════════════════════════════════════════════════════════


class TestSFRB11TheProclamationReadsWhole:

    @pytest.mark.parametrize("scale", SCALES)
    def test_its_closing_line_and_its_terms_are_seen(self, record, scale):
        card = _payload(record, "proclamation_warsaw")
        seen = _seen(_frame(record, "proclamation_warsaw", scale))
        assert card["subtitle"] in seen, f"'{card['subtitle']}' below the fold at {scale}"
        for term in card["terms"]:
            assert term in seen, f"term '{term}' below the fold at {scale}"
        assert card["proclamation"][:40] in seen

    def test_the_closing_line_stands_under_the_reading_not_in_it(self):
        src = _read(SCRIPTS / "proclamation_popup.gd")
        show = _func_body(src, "show_proclamation")
        assert "subtitle_label.text" in show
        assert 'bbcode += "\\n[center]%s[/center]" % Utils.bbcode_color(' not in show


class TestSFRB11ThePetitionShowsItsAnswers:

    @pytest.mark.parametrize("scale", SCALES)
    def test_every_answer_and_later_stand_above_the_fold(self, record, scale):
        frame = _frame(record, "petition_command_closed", scale)
        petition = _payload(record, "petition_command_closed")
        for option in petition["options"]:
            _button(frame, option["label"])
        _button(frame, "Later")
        assert _folded(frame) == []

    @pytest.mark.parametrize("scale", SCALES)
    def test_his_words_and_the_closed_arms_reason_are_seen(self, record, scale):
        frame = _frame(record, "petition_command_closed", scale)
        petition = _payload(record, "petition_command_closed")
        seen = _seen(frame)
        assert petition["speaker_line"].strip('"')[:30] in seen
        closed = next(o for o in petition["options"] if not o["enabled"])
        assert closed["unavailable_reason"][:30] in seen

    def test_the_letter_carries_each_answers_price(self, record):
        """The answers stand as buttons; what each costs is read in the
        letter (and in each button's tooltip) — the client's petition and
        the envoy's letter already read this way. Never the closed arm's
        reason twice."""
        frame = _frame(record, "petition_command_closed", 1.0)
        petition = _payload(record, "petition_command_closed")
        seen = _seen(frame)
        for option in petition["options"]:
            if option["enabled"]:
                assert option["detail"][:40] in seen, option["label"]
        closed = next(o for o in petition["options"] if not o["enabled"])
        assert seen.count(closed["unavailable_reason"][:30]) == 1

    def test_the_answers_are_a_row_not_a_scroll(self):
        scene = _read(SCENES / "marshal_petition_dialog.tscn")
        assert '[node name="OptionsContainer" type="HFlowContainer"' in scene
        assert 'parent="PanelContainer/VBoxContainer/ScrollContainer"' not in scene


# ═══════════════════════════════════════════════════════════════════════════
# RR5-X1 — the objection dialog ran off both edges at 2.0
# ═══════════════════════════════════════════════════════════════════════════


class TestRR5X1TheObjectionFitsItsWindow:

    @pytest.mark.parametrize("scale", SCALES)
    def test_every_answer_is_on_screen_and_the_objection_is_read(self, record, scale):
        frame = _frame(record, "objection_dialog", scale)
        asked = _payload(record, "objection_dialog")
        assert frame.get("buttons_offscreen") == []
        assert _folded(frame) == []
        for label in ("Trust Massena", "Proceed as Ordered", "Compromise", "Cancel the Order"):
            _button(frame, label)
        message = (asked.get("objection") or {}).get("message") or asked.get("message")
        assert str(message)[:40] in _seen(frame)

    def test_its_rows_wrap(self):
        scene = _read(SCENES / "objection_dialog.tscn")
        assert '[node name="ButtonContainer" type="HFlowContainer"' in scene
        assert '[node name="StatsContainer" type="HFlowContainer"' in scene


# ═══════════════════════════════════════════════════════════════════════════
# RR5-X2 — the Talleyrand objection's frame shot blank
# ═══════════════════════════════════════════════════════════════════════════


class TestRR5X2TheObjectionsBoardIsReached:

    def test_the_capture_answers_the_articles_card(self):
        src = _read(TOOLS / "iq10_capture_payloads.py")
        body = src[src.index("def cap_popups_s12"):src.index("\ndef ", src.index("def cap_popups_s12") + 10)]
        assert body.count('cmd(c, "1")') == 2
        assert 'if not answer.get("diplomatic_objection"):' in body

    @pytest.mark.parametrize("scale", SCALES)
    def test_his_three_answers_are_drawn(self, record, scale):
        frame = _frame(record, "talleyrand_objection", scale)
        for label in ("Proceed Anyway", "Modify Proposal", "Cancel"):
            _button(frame, label)
        assert "TALLEYRAND OBJECTS" in _seen(frame)


# ═══════════════════════════════════════════════════════════════════════════
# RR5-X8 — the collapse board's war-detail frames went unshot (since S13d)
# ═══════════════════════════════════════════════════════════════════════════


class TestRR5X8TheLosingWarIsShotAgain:

    @pytest.mark.parametrize("tag", ["one", "none"])
    def test_the_capture_produces_the_war_detail(self, record, tag):
        detail = _payload(record, f"war_detail_collapse_{tag}")
        assert detail["war"]["opponent"] and int(detail["war"]["war_score"]) < 0

    def test_the_capture_reads_the_score_not_the_tier(self):
        src = _read(TOOLS / "iq10_capture_payloads.py")
        at = src.index("def cap_collapse")
        body = src[at:src.index("\ndef ", at + 10)]
        assert 'key=lambda w: int(w.get("war_score", 0) or 0), default=None)' in body
        assert 'settlement_tier_side") == "theirs"' not in body


# ═══════════════════════════════════════════════════════════════════════════
# EA-E1 — the compact top bar's navigation buttons drew blank
# ═══════════════════════════════════════════════════════════════════════════

NAV = ["EventLogBtn", "LedgerBtn", "GeneralsBtn", "DiploLedgerBtn", "DispatchBtn", "GazetteBtn"]


def _nav_buttons(frame: dict) -> list:
    out = [b for b in frame.get("buttons") or [] if any(b["path"].endswith(n) for n in NAV)]
    assert len(out) == 6, [b["path"] for b in frame.get("buttons") or []]
    return out


class TestEAE1TheCompactBarDrawsItsGlyphs:

    def test_at_2_every_nav_button_is_a_glyph_with_room_to_draw(self, record):
        for b in _nav_buttons(_frame(record, "top_bar_boot", 2.0)):
            assert b["text"] == "" and b.get("icon") is True, b
            # the button's own margins are 16: a glyph of 18 needs 34
            assert b["rect_raw"][2] >= 34.0, b

    def test_at_1_the_full_bar_keeps_its_words(self, record):
        for b in _nav_buttons(_frame(record, "top_bar_boot", 1.0)):
            assert re.search(r"\([A-Z]\)$", b["text"]), b
            assert b.get("icon") is False, b

    def test_the_helper_gives_the_glyph_a_size_of_its_own(self):
        helper = _func_body(_read(SCRIPTS / "utils.gd"), "apply_button_icon")
        assert "btn.expand_icon = false" in helper
        assert 'add_theme_constant_override("icon_max_width"' in helper
        fit = _func_body(_read(SCRIPTS / "top_bar.gd"), "_fit_bar")
        assert "_nav_icons" in fit

    def test_rr5_x6_the_glyph_carries_the_antechambers_amber(self):
        """The Generals button says a marshal waits in its words — amber and
        "(1)" — and the compact bar has no words: its glyph turns amber."""
        body = _func_body(_read(SCRIPTS / "top_bar.gd"), "_update_button_highlights")
        assert 'btn.add_theme_color_override("icon_normal_color",' in body
        assert "Utils.UI_WARNING if waiting else Utils.UI_GOLD" in body


# ═══════════════════════════════════════════════════════════════════════════
# EA-E2 (+ RR5-X3) — every curated glyph is a white silhouette
# ═══════════════════════════════════════════════════════════════════════════


class TestEAE2EveryGlyphIsAWhiteSilhouette:

    def test_the_book_and_the_gear_are_white(self):
        for name in ("book-open.svg", "gear.svg"):
            svg = _read(ICONS / "phosphor" / name)
            assert "currentColor" not in svg and "#ffffff" in svg, name

    def test_no_phosphor_glyph_draws_in_currentcolor(self):
        """`currentColor` renders black, and every road the client draws a
        glyph by tints it (a gold chip, a white pill silhouette, a category
        hue): black times any tint is black."""
        black = sorted(p.name for p in (ICONS / "phosphor").glob("*.svg")
                       if "currentColor" in _read(p))
        assert black == [], black

    def test_no_game_icon_keeps_its_black_square(self):
        boxed = sorted(p.name for p in (ICONS / "game-icons").glob("*.svg")
                       if '<path d="M0 0h512v512H0z"/>' in _read(p))
        assert boxed == [], boxed


# ═══════════════════════════════════════════════════════════════════════════
# EA-E5 — the wizard's step-2 assessment at 2.0
# ═══════════════════════════════════════════════════════════════════════════


class TestEAE5TheAssessmentIsRead:

    @pytest.mark.parametrize("court", ["austria", "prussia"])
    @pytest.mark.parametrize("scale", SCALES)
    def test_talleyrands_counsel_opens_above_the_fold(self, record, court, scale):
        preview = _payload(record, f"wizard_preview_{court}")
        frame = _frame(record, f"wizard_step2_{court}", scale)
        opening = str(preview["assessment"]).split(".")[0][:40]
        assert opening and opening in _seen(frame), f"{court} at {scale}: '{opening}'"

    @pytest.mark.parametrize("scale", SCALES)
    def test_the_actions_still_show_and_say_there_are_more(self, record, scale):
        frame = _frame(record, "wizard_step2_austria", scale)
        chips = [b for b in frame.get("buttons") or []
                 if b.get("scroll_rect") and b["text"] and b["text"] not in ("Back", "Cancel")]
        seen = [b for b in chips if _inside(b["rect_raw"], b["scroll_rect"])]
        assert len(seen) >= 2, [b["text"] for b in seen]
        assert "more below" in _seen(frame)


# ═══════════════════════════════════════════════════════════════════════════
# EA-E6 — the settlement table's Press / Ease / Drop rows at 2.0
# ═══════════════════════════════════════════════════════════════════════════


class TestEAE6EveryCourtKeepsItsRow:

    @pytest.mark.parametrize("scale", SCALES)
    def test_every_court_row_is_seen_whole(self, record, scale):
        frame = _frame(record, "settlement_three_courts", scale)
        for court in ("Austria", "Britain", "Russia"):
            for verb in ("Demand more of ", "Ease ", "Drop "):
                b = _button(frame, verb + court)
                assert _inside(b["rect_raw"], b["scroll_rect"] or b["rect_raw"]), (court, verb)
        assert _folded(frame) == []

    @pytest.mark.parametrize("scale", SCALES)
    def test_the_verdict_and_the_table_lead_are_seen(self, record, scale):
        seen = _seen(_frame(record, "settlement_three_courts", scale))
        assert "This settlement cannot be ratified now." in seen
        assert "Austria" in seen


# ═══════════════════════════════════════════════════════════════════════════
# RR5-X4 — the Generals at 2.0: the whole-line pad hid the Emperor's portrait
# ═══════════════════════════════════════════════════════════════════════════


class TestRR5X4NoDeadBandUnderTheGenerals:

    @pytest.mark.parametrize("scale", SCALES)
    def test_the_reading_scroll_fills_its_panel(self, record, scale):
        frame = _frame(record, "generals_boot", scale)
        content = next(t for t in frame["texts"] if t["path"].endswith("ContentArea"))
        window = content["scroll_rect"]
        panel = frame["surfaces"]["MarshalManagement/PanelContainer"]
        band = (panel[1] + panel[3] - 16.0) - (window[1] + window[3])
        # a line the whole-line snap pads away is at most a quarter of the window
        assert band <= window[3] * 0.25 + 1.0, f"a {band:.0f}-px dead band at {scale}"

    def test_a_tall_box_is_cut_not_hidden(self):
        src = _read(SCRIPTS / "utils.gd")
        snap = _func_body(src, "snap_whole_lines")
        assert "_whole_line_max_box(view_h)" in snap
        assert "WHOLE_LINE_MAX_SHARE" in _func_body(src, "_whole_line_max_box")


# ═══════════════════════════════════════════════════════════════════════════
# RR5-X5 — the reward dialog folded a choice at 2.0 (the sweep's sibling)
# ═══════════════════════════════════════════════════════════════════════════


class TestRR5X5TheRewardKeepsItsChoices:

    @pytest.mark.parametrize("scale", SCALES)
    def test_every_choice_and_not_now_are_seen(self, record, scale):
        frame = _frame(record, "reward_dialog", scale)
        for label in ("Endow ", "Re-size rente", "Revoke his rente", "Not now"):
            _button(frame, label)
        assert _folded(frame) == []

    def test_the_choices_scroll_keeps_its_rows(self):
        body = _func_body(_read(SCRIPTS / "reward_dialog.gd"), "show_reward")
        assert 'scroll.set_meta("relax_floor", scroll.custom_minimum_size.y)' in body


# ═══════════════════════════════════════════════════════════════════════════
# EA-E9 — the dispatch has a key the common overlays leave alone
# ═══════════════════════════════════════════════════════════════════════════


class TestEAE9TheDispatchHasASecondKey:

    def test_alt_b_opens_the_dispatch_while_typing(self):
        src = _read(SCRIPTS / "main.gd")
        at = src.index("const _SCREEN_HOTKEYS := {")
        table = src[at:src.index("}", at)]
        assert re.search(r'KEY_B:\s*"dispatch"', table), table
        assert re.search(r'KEY_R:\s*"dispatch"', table), "Alt+R stays where no overlay takes it"

    def test_alt_b_opens_the_dispatch_off_the_line_too(self):
        src = _read(SCRIPTS / "main.gd")
        at = src.index("func _unhandled_input")
        body = src[at:src.index("\nfunc ", at + 10)]
        assert "event.keycode == KEY_B and event.alt_pressed" in body

    def test_every_surface_that_names_the_key_names_both(self):
        readme = _read(REPO / "deploy" / "README_TESTER.txt")
        assert "R / Alt+R / Alt+B" in readme
        assert "overlay" in readme[readme.index("Alt+B"):readme.index("Alt+B") + 260]
        bar = _read(SCRIPTS / "top_bar.gd")
        assert 'const SECOND_HOTKEYS := {"dispatch": "B"}' in bar
        assert "where a graphics overlay keeps Alt+%s" in bar
        assert "Alt+B for the Dispatch where a graphics" in _read(SCRIPTS / "settings_panel.gd")

    def test_the_live_session_presses_it(self):
        gd = _read(TOOLS / "mode_c_driven_session.gd")
        assert "[KEY_B, \"dispatch\"]" in gd
        assert "SECOND_KEYS" in gd


# ═══════════════════════════════════════════════════════════════════════════
# The rows closed by their reproduction — today's frame held
# ═══════════════════════════════════════════════════════════════════════════


def _overlap(a, b) -> bool:
    return not (a[0] + a[2] <= b[0] or b[0] + b[2] <= a[0] or a[1] + a[3] <= b[1] or b[1] + b[3] <= a[1])


class TestSFRB10TheDioramaIsClean:
    """CLOSED by its reproduction: Pre-Deploy S12 part 2 (UXR3-F2, part 5d)
    cut a rear rank's pole at two ranks and moved Replay and Close 18 px
    clear of the corner filigree; the entry frames read clean at both
    scales."""

    @pytest.mark.parametrize("shot", ["diorama_dadj", "diorama_aadj"])
    @pytest.mark.parametrize("scale", SCALES)
    def test_close_and_replay_clear_the_filigree(self, record, shot, scale):
        frame = _frame(record, shot, scale)
        corners = [g["rect"] for g in frame.get("grips") or [] if g["kind"] == "ornament"]
        assert len(corners) == 4
        for label in ("Close", "Replay"):
            b = _button(frame, label)
            assert not any(_overlap(b["rect_raw"], c) for c in corners), (label, scale)

    def test_the_rear_standard_is_cut_below_the_forward_portrait(self):
        side = _func_body(_read(SCRIPTS / "battle_diorama.gd"), "_build_side")
        assert "if n >= 2 and i > 0:" in side
        assert "STANDARD_POLE_MIN, STANDARD_POLE)" in side


class TestEAE3TheBlockadeBorderIsCrimson:
    """CLOSED by its reproduction: UXR3-F9 (Pre-Deploy S12 part 2)."""

    def test_the_blockade_style_borders_in_alert(self):
        style = _func_body(_read(SCRIPTS / "top_bar.gd"), "_blockade_style")
        assert "sb.border_color = Utils.UI_ALERT" in style

    @pytest.mark.parametrize("scale", SCALES)
    def test_the_chip_says_so_in_both_bars(self, record, scale):
        frame = _frame(record, "top_bar_admiralty", scale)
        chip = _button(frame, "\u2693")
        assert ("BLOCKADED" in chip["text"]) if scale == 1.0 else chip["text"].endswith("!")


class TestEAE7TheFiligreeStandsOffTheText:
    """CLOSED by its reproduction: UXR3-F4 (Pre-Deploy S12 part 2) set the
    Generals' corners in the bottom padding band."""

    @pytest.mark.parametrize("scale", SCALES)
    def test_no_corner_touches_the_reading_window(self, record, scale):
        frame = _frame(record, "generals_boot", scale)
        window = next(t for t in frame["texts"] if t["path"].endswith("ContentArea"))["scroll_rect"]
        corners = [g["rect"] for g in frame.get("grips") or [] if g["kind"] == "ornament"]
        assert len(corners) == 2
        assert not any(_overlap(window, c) for c in corners)


class TestTheAgendasC6ReShoot:
    """The formables entry reads clean at both scales (EA-E8 fixed the
    "Loading…" frame two EYES votes rested on); re-shot for UXR-4."""

    @pytest.mark.parametrize("scale", SCALES)
    def test_the_entry_is_present_and_live(self, record, scale):
        frame = _frame(record, "wizard_formables_entry", scale)
        entry = _button(frame, "Formable Nations")
        assert entry["disabled"] is False
        seen = _seen(frame)
        assert "which nation requires our diplomatic attention" in seen
        assert "Loading" not in seen


# ═══════════════════════════════════════════════════════════════════════════
# The frames, committed for the user's eye (UXR-4)
# ═══════════════════════════════════════════════════════════════════════════

COMMITTED = [
    "IQ10_DIORAMA_DADJ", "IQ10_DIORAMA_AADJ", "IQ10_PROCLAMATION_WARSAW",
    "IQ10_PETITION_COMMAND_CLOSED", "IQ10_OBJECTION_DIALOG", "IQ10_TALLEYRAND_OBJECTION",
    "IQ10_SETTLEMENT_THREE_COURTS", "IQ10_WIZARD_STEP2_AUSTRIA", "IQ10_WIZARD_FORMABLES_ENTRY",
    "IQ10_TOP_BAR_BOOT", "IQ10_TOP_BAR_ADMIRALTY", "IQ10_GENERALS_BOOT", "IQ10_RAIL_T20",
    "IQ10_WAR_ROOM_BOOT", "IQ10_REWARD_DIALOG",
]


class TestTheFramesAreCommitted:

    @pytest.mark.parametrize("stem", COMMITTED)
    def test_the_frame_is_committed_at_both_scales(self, stem):
        for tail in ("", "_X2"):
            png = AUDITS / f"{stem}{tail}_{FRAME_DATE}.png"
            assert png.exists(), f"missing evidence frame: {png.name}"
            assert png.stat().st_size > 8000, f"{png.name} is too small to be a real frame"

    def test_uxr4_lists_them(self):
        plan = _read(REPO / "docs" / "UX_UI_REVIEW_PLAN.md")
        section = plan[plan.index("## UXR-4"):plan.index("## What this plan does not do")]
        assert "SF-RR5" in section
        for stem in COMMITTED:
            assert stem in section, stem
