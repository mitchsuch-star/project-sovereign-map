"""S14c part 2, first landing — the moment letter on the client
(`docs/EVENTS_SPEC.md` §6; the siblings S14C-X11, X15 and the finds X21,
X22 in `docs/BUG_FIXES.md` §S14C).

`incoming_proposal_popup.gd` gains its `is_moment` register (the dateline,
the record, the board, what each answer does, the unanswered line; Counter
hidden; captions from the payload); `main.gd` routes a court-less letter
(X21 — the empty dismissal key swallowed every one), names it when answered
or set aside (X22), says what it could not open (X11) and opens a moment's
own letter from its rail row (X14's client half); every lapse surface prints
a carried sentence (X15). The IQ-10 frames at Interface Scale 1.0 and 2.0
show the whole letter, both answers above the fold.
"""
import importlib.util
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
GODOT = REPO / "godot-client" / "project-sovereign" / "scripts"
AUDITS = REPO / "docs" / "audits"


def _gd(name):
    return (GODOT / name).read_text(encoding="utf-8")


def _func(src, name):
    start = src.index(f"func {name}(")
    nxt = src.find("\nfunc ", start + 5)
    return src[start:nxt if nxt > 0 else len(src)]


class TestThePopupRegister:
    def test_the_register_reads_the_payload_s_own_parts(self):
        src = _gd("incoming_proposal_popup.gd")
        body = _func(src, "show_proposal")
        assert 'var is_moment = data.get("is_moment", false)' in body
        assert "A MOMENT OF HISTORY — " in body and 'data.get("dateline", "")' in body
        assert "_build_moment_body(data)" in body
        assert 'data.get("unanswered_line", "")' in body
        moment_body = _func(src, "_build_moment_body")
        for key in ('data.get("record", "")', 'data.get("board", [])', 'data.get("answers", [])'):
            assert key in moment_body
        assert "What each answer does" in moment_body

    def test_no_counter_and_the_authored_captions(self):
        body = _func(_gd("incoming_proposal_popup.gd"), "show_proposal")
        assert "and not is_call_to_arms and not is_moment" in body
        assert "or is_call_to_arms or is_moment" in body
        assert '_moment_caption(data, "accept_ai_proposal", "Accept")' in body
        assert '_moment_caption(data, "reject_ai_proposal", "Decline")' in body

    def test_backend_copy_is_never_parsed_as_a_tag(self):
        src = _gd("incoming_proposal_popup.gd")
        assert '.replace("[", "[lb]")' in _func(src, "_moment_text")
        # The emits stay the four keywords the router owns (IQ-7's pin).
        assert set(re.findall(r'choice_made\.emit\("(\w+)"', src)) == {"accept", "counter", "reject", "dismiss"}


class TestMainRoutesACourtlessLetter:
    def test_x21_the_dismissal_key_is_the_letter_s_id(self):
        src = _gd("main.gd")
        route = _func(src, "_response_has_incoming_proposal_route")
        assert "_proposal_dismiss_key(response.incoming_proposal) != _dismissed_proposal_nation" in route
        key = _func(src, "_proposal_dismiss_key")
        assert '"moment:" + str(proposal.get("moment_id", ""))' in key

    def test_x22_the_answer_names_the_letter(self):
        choice = _func(_gd("main.gd"), "_on_incoming_proposal_choice")
        assert "_dismissed_proposal_nation = _proposal_dismiss_key(data)" in choice
        assert '"]Answering " + str(data.get("title", "the letter"))' in choice
        assert '"]Setting aside " + str(data.get("title", "the letter"))' in choice

    def test_x11_an_unknown_letter_says_so_and_hands_back_the_terminal(self):
        body = _func(_gd("main.gd"), "_on_mailbox_activate_result")
        tail = body[body.rindex("elif dtype in"):]
        assert "\telse:" in tail and "That letter cannot be opened here, Sire" in tail
        assert "_return_control_to_player()" in tail
        assert body.index("tutorial_overlay.observe(response)") < body.index("That letter cannot")

    def test_the_moment_row_opens_its_letter(self):
        body = _func(_gd("main.gd"), "_on_notification_review_requested")
        arm = body[body.index('if review_target == "moment_letter":'):]
        assert "api_client.activate_mailbox_item(int(route_id), _on_mailbox_activate_result)" in arm

    def test_the_mailbox_row_says_moment(self):
        src = _gd("mailbox_panel.gd")
        assert '"moment_letter": "Moment"' in src
        assert 'str(item.get("proposal_type", "")) == "moment_letter"' in _func(src, "_build_item_row")


class TestX15EveryLapseSurfacePrintsASentence:
    """The census over every reader of `lapse["nation"]`: each prints a
    carried line for a court-less letter rather than "'s … offer lapsed"."""

    def test_both_renderers_print_a_carried_line(self):
        for name in ("main.gd", "dispatch_view.gd"):
            src = _gd(name)
            i = src.index('if bool(lapse.get("is_petition", false)) and l_line != "":')
            block = src[i:i + 900]
            assert 'if l_line != "":' in block, name
            assert 'bool(lapse.get("is_moment", false))' in block, name
            assert "A letter of the record was left unanswered." in block, name

    def test_the_backend_readers(self):
        from backend.campaign_log import format_event_oneliner
        from backend.game_logic.dispatch import _lapsed_offer_row
        row = {"type": "offer_lapsed", "nation": "", "proposal_type": "moment_letter",
               "moment": {"id": "throne_of_holland", "title": "The Throne of Holland",
                          "line": "The Throne of Holland was left unanswered — Keep the Republic: no change."}}
        assert format_event_oneliner(row).startswith("The Throne of Holland was left unanswered")
        out = _lapsed_offer_row(row)
        assert out["is_moment"] and out["line"].startswith("The Throne of Holland")
        tm = (REPO / "backend" / "game_logic" / "turn_manager.py").read_text(encoding="utf-8")
        assert '"call_to_arms", "moment")' in tm               # the row carries the sentence
        assert "if nation and nation not in lapsed_nations" in tm  # no cooldown for no court

    def test_the_driver_prints_the_sentence(self):
        spec = importlib.util.spec_from_file_location("_drv", REPO / "tools" / "playtest_driver.py")
        src = (REPO / "tools" / "playtest_driver.py").read_text(encoding="utf-8")
        envoy = src[src.index("    def envoy_state("):src.index("    def ratified(")]
        assert 'r.get("is_moment")' in envoy and 'r.get("line")' in envoy
        assert spec is not None


class TestTheFrames:
    def _runner(self):
        spec = importlib.util.spec_from_file_location("_iq10_runner", REPO / "tools" / "iq10_run_captures.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_the_shots_are_registered(self):
        shots = {s["id"]: s for s in self._runner().SHOTS}
        for mid, captions in (("bavarian_match", ("Seal the match", "Let Baden keep her")),
                              ("decree_of_berlin", ("Sign the Decree", "Not yet"))):
            row = shots[f"moment_letter_{mid}"]
            assert row["scene"] == "res://scenes/incoming_proposal_popup.tscn"
            assert row["method"] == "show_proposal"
            assert all(c in row["must_show"] for c in captions)
        cap = (REPO / "tools" / "iq10_capture_payloads.py").read_text(encoding="utf-8")
        assert '"moments": cap_moments' in cap

    @pytest.mark.parametrize("mid", ["BAVARIAN_MATCH", "DECREE_OF_BERLIN"])
    def test_the_frames_are_committed_at_both_scales(self, mid):
        for tail in ("", "_X2"):
            png = AUDITS / f"IQ10_MOMENT_LETTER_{mid}{tail}_2026_10_22.png"
            assert png.exists(), png
            assert png.stat().st_size > 8000, png
