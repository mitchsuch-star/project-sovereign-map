"""RE-5 the close — the Mode C walk on 8007, read off its committed record
(`docs/RECURRING_EVENTS_SPEC.md` §16 "RE-5": one affair answered, one lapsed,
the Watch seen, the withdrawal seen; §16b: a sealed letter, the Correspondence
read, a squadron sailed and settled; the landing record §26.1).

`tools/re5_mode_c_walk.py` ran the real `main.tscn` against a sandboxed
backend and wrote `docs/audits/re5_mode_c_2026_11_02/walk.json` (what each
step read off the screen's own nodes) and `run.json` (the engine's error
census). The pins read the record, never the screen: every scene present
with its read, no SCRIPT ERROR, the frames beside them.
"""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
AUDIT = REPO / "docs" / "audits" / "re5_mode_c_2026_11_02"
SCENES = ("rail", "arrival", "letter", "accept_seal", "accept_echo", "receipt", "correspondence", "home",
          "offer", "offer_seal", "offer_echo", "laws_edicts", "recruit_quote",
          "left", "lapsed", "standing", "watch", "withdrawn", "set_aside")


def _plain(text) -> str:
    return str(text).replace(" ", " ")


def _walk():
    return json.loads((AUDIT / "walk.json").read_text(encoding="utf-8"))


def _run():
    return json.loads((AUDIT / "run.json").read_text(encoding="utf-8"))


def _by(walk):
    return {s["step"]: s for s in walk["steps"]}


class TestTheWalkRanClean:
    def test_every_scene_is_on_the_record_with_its_frame(self):
        walk = _walk()
        by = _by(walk)
        assert [s["step"] for s in walk["steps"]] == list(SCENES)
        for name in SCENES:
            s = by[name]
            assert s["saved"] is True and s["frame"].endswith(".jpg"), name
            assert (AUDIT / "frames" / s["frame"]).is_file(), s["frame"]
        assert walk["booted"] is True and walk["errors"] == [], walk["errors"]
        assert "error" not in walk

    def test_no_script_error_and_the_engine_exited_clean(self):
        run = _run()
        assert run["engine_exit"] == 0 and run["script_errors"] == []
        assert run["staged"] == {"a": True, "b": True, "c": True, "d": True}     # the four crafted boards
        assert run["port"] != 8005


class TestChapterATheLetterTheSquadronAndTheEdict:
    def test_the_letter_opened_from_the_desk_in_the_dress(self):
        by = _by(_walk())
        assert by["arrival"]["turn"] == 7 and "Read the letter" in _plain(by["arrival"]["desk"])
        letter = by["letter"]
        assert letter["register"] == "affair" and letter["writer"] == "Decrès"
        assert letter["title"] == "The Squadron for Santo Domingo"
        assert letter["accept"].startswith("Send five of the line / −500 gold · 1 action")
        assert letter["decline"].startswith("Ferrand must hold alone / standing 100 → 97")
        assert letter["counsel"].startswith("Berthier — ")

    def test_the_seal_the_echo_the_receipt_and_the_correspondence(self):
        by = _by(_walk())
        assert by["accept_seal"]["turn"] == 7 and by["accept_echo"]["turn"] == 7
        assert by["receipt"]["turn"] == 8
        assert any("at sea for Santo Domingo" in ln for ln in by["receipt"]["receipt_lines"])
        page = by["correspondence"]["page"]
        assert "ANSWERED (1)" in page and "At sea — five of the line" in page
        assert "Send five of the line. — N." in page                     # the apostille

    def test_the_squadron_settled_on_the_slip_and_in_the_morning(self):
        by = _by(_walk())
        home = by["home"]
        assert home["turn"] == 11 and ("home whole" in home["fate"] or "caught" in home["fate"])
        assert any("THE SQUADRON" in ln for ln in home["morning_lines"])

    def test_the_offer_decreed_and_read_on_the_laws_and_in_the_quote(self):
        by = _by(_walk())
        offer = by["offer"]
        assert offer["register"] == "affair" and offer["title"] == "The Remounts" and offer["writer"] == "Dejean"
        assert offer["accept"].startswith("Buy the remounts / −1,500 gold · 1 action · 8 turns")
        laws = by["laws_edicts"]
        assert any("Remounts" in ln for ln in laws["edicts_lines"]), laws["edicts_lines"]
        assert any("In force until" in ln for ln in laws["edicts_lines"]), laws["edicts_lines"]
        quote = by["recruit_quote"]
        # the typed order's own reply names the decree in the price (the bare
        # `recruit cavalry` is refused for want of a corps in reach, and the
        # reply names the order to type; the walk types it)
        assert any("recruit cavalry" in ln and ln.startswith("►") for ln in quote["quote_lines"]), quote["quote_lines"]
        assert any("Remounts" in ln and not ln.startswith(("Answering", "The Remounts —")) for ln in quote["quote_lines"]), quote["quote_lines"]

    def test_the_watch_is_seen(self):
        """IN THE OFFING on the Host's board (chapter B): the Magazines' line
        with its need capped (RE5-1) and the Marine's with its latch count."""
        by = _by(_walk())
        watch = by["watch"]
        lines = [_plain(ln) for ln in (watch["offing"] or watch["watch_lines"])]
        assert any("Daru may write of the magazines" in ln and "2 of 2 mornings" in ln for ln in lines), lines
        assert not any("7 of 2" in ln for ln in lines)
        standing = _plain(by["standing"]["desk"])
        assert "The Host's Claims" in standing and "Read the letter" in standing


class TestTheSealDrawsOverTheNextEnvoy:
    def test_the_answer_beat_is_parented_under_the_popup_s_own_layer(self):
        """RE5-3 (the walk's seal frame): the beat's slip sat under the top
        bar's layer (75), beneath the dialog layers (101–123), and a court's
        envoy promoted into the popup on the same response covered the seal.
        main.gd hands the beat the scale card's EXISTING layer (125, above
        every dialog, always visible — only the card inside it hides), the
        top bar the fallback; the popup's `play_answer_beat` still takes the
        parent it is given (never a new CanvasLayer)."""
        src = (REPO / "godot-client" / "project-sovereign" / "scripts" / "main.gd").read_text(encoding="utf-8")
        assert "var _beat_parent = _scale_card_layer" in src
        assert 'play_answer_beat(str(_sealed.get("answer", "")), _beat_parent)' in src
        assert 'play_answer_beat(str(_sealed.get("answer", "")), top_bar)' not in src
        assert "_scale_card_layer.layer = 125" in src
        scenes = REPO / "godot-client" / "project-sovereign" / "scenes"
        layers = [int(ln.split("=")[1]) for p in scenes.glob("*.tscn")
                  for ln in p.read_text(encoding="utf-8").splitlines() if ln.startswith("layer = ")]
        assert max(layers) < 125, max(layers)                      # the slip draws over every dialog
        popup = (REPO / "godot-client" / "project-sovereign" / "scripts" / "incoming_proposal_popup.gd").read_text(encoding="utf-8")
        beat = popup.split("func play_answer_beat")[1].split("\nfunc ")[0]
        code = beat.split('"""')[2]                                 # the body past its docstring
        assert "CanvasLayer.new()" not in code
        assert "parent.add_child(slip)" in code


class TestChaptersBAndCTheWithdrawalAndTheLapse:
    def test_the_standing_letter_is_set_aside_for_the_match(self):
        by = _by(_walk())
        assert by["standing"]["turn"] == 7 and by["standing"]["chip"].startswith("corr:read:")
        assert "The Host's Claims" in _plain(by["standing"]["desk"])
        assert by["withdrawn"]["turn"] == 8
        assert any("The Host's Claims was set aside for The Bavarian Match" in _plain(ln) for ln in by["withdrawn"]["morning_lines"])
        assert "Set aside for The Bavarian Match — nothing was spent" in _plain(by["set_aside"]["page"])

    def test_a_letter_left_unopened_lapses_to_its_decline(self):
        by = _by(_walk())
        left = by["left"]
        assert left["left_id"] == "the_host#1" and left["chip"].startswith("corr:read:")
        lapsed = by["lapsed"]["lapsed"]
        assert lapsed and lapsed["id"] == "the_host#1"
        assert lapsed["line"].startswith("Filed unanswered — Live off the land")
        assert by["lapsed"]["turn"] >= 9
