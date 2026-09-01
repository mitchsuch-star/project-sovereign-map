"""UX23-B "The Desk Is Quiet" — the routed rows, closed August 23, 2026.

R2 and R3 landed earlier the same day inside UX23-A. This file closes the rest,
and every row turned out to be wrong about something. Each correction is
recorded beside the pin that now binds the real behaviour, because in every
case the row as written would have produced a worse bug than the one it named:

  UX23-R1  `stop_cue` — the row's completion definition put the wiring at
           `popup_base.close_popup`, which only TWO of the fifteen over-2s cues
           route through. And its flagship example, `capture_choice_dialog`'s
           coins, is the one site that must be left alone: it fires inside the
           Plunder handler as the sound of the decision. The rule is *an
           arrival sound stops on close; a departure sound IS the close* —
           `close_popup` itself plays "back" on the way out.

  UX23-R4  The row offered "derive at read time" as an option. Taken literally
           it is a serious bug: `build_morning_dispatch` CONSUMES — it clears
           queued events, overwrites the PC-7 lead memory, latches
           `last_expectation_seen`, and rolls for Talleyrand sabotage
           discovery. Pressing R would have re-rolled sabotage. Only the pure
           Unmet-Marshals half is re-derived, onto a copy.

  UX23-R5  Wrong three ways: the advisory has no `cancel` option (the hit is
           the `cancel` KEYWORD mapping onto `dismiss`); whole-line matching
           does not fix `"yes"`, the row's own second example; and scoping to
           "non-blocking" would have broken the letter-book, where
           `accept prussia's proposal` is exactly the sentence CA9 built the
           court guard to serve.

  UX23-R6  The causal claim is INVERTED. "The next diorama sound will forget
           the toggle guard" — the guard is INSIDE the diorama and inherited;
           `AudioManager._play_cue` is the side that has never read
           `UiSettings.get_battle_sfx()`. Routing as instructed would have
           silently disabled the "Battle sounds" setting.

  UX23-R7  Docs-only, and discharged.

  UX23-R8  Under-scoped: `campaign_cost_note` has the identical defect at the
           identical seam. And "the same [Reward…] affordance on EVERY
           surface" is unachievable — `enemy_phase_dialog` is CanvasLayer 118
           and `reward_dialog` is 109, so a chip there opens the dialog BEHIND
           the modal that launched it.

Plus the UX23-1 acceptance condition, which was open since the morning and is
now MEASURED rather than owed: two of the eleven caps were silencing their cue
outright.
"""

import io
import os
import re

import pytest

from backend.commands.dialogue_routing import match_dialogue_answer


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GODOT = os.path.join(REPO_ROOT, "godot-client", "project-sovereign")
SCRIPTS = os.path.join(GODOT, "scripts")


def _read(name, sub="scripts"):
    with open(os.path.join(GODOT, sub, name), encoding="utf-8") as fh:
        return fh.read()


def _live(name, sub="scripts"):
    """`_read` with commented-out code AND docstrings removed.

    A pin a comment satisfies is not a pin (UX23-A review round) — and the
    first draft of this file learned the same lesson one level down: three of
    its own assertions passed or failed on prose inside a triple-quoted
    block that was describing the very thing being forbidden. Blank the docstrings rather
    than word around them, or the next person writing a comment reddens a
    test for no reason."""
    out = []
    in_doc = False
    for line in _read(name, sub).split("\n"):
        fence_count = line.count('"""')
        if in_doc:
            if fence_count:
                in_doc = False
            continue
        if fence_count == 1:
            in_doc = True
            continue
        if fence_count >= 2:
            continue
        if line.lstrip().startswith("#"):
            continue
        if "#" in line and '"' not in line.split("#", 1)[0]:
            line = line.split("#", 1)[0]
        out.append(line)
    return "\n".join(out)


def _py_live(path):
    """The same, for a Python source file: `#` comments and docstrings out."""
    with io.open(path, encoding="utf-8") as fh:
        raw = fh.read()
    out = []
    in_doc = False
    for line in raw.split("\n"):
        fence = line.count('"""')
        if in_doc:
            if fence:
                in_doc = False
            continue
        if fence == 1:
            in_doc = True
            continue
        if fence >= 2:
            continue
        if line.lstrip().startswith("#"):
            continue
        out.append(line)
    return "\n".join(out)


# ══════════════════════════════════════════════════════════════════════════
# UX23-R1 — closing a panel silences the sound it started
# ══════════════════════════════════════════════════════════════════════════


class TestClosingAPanelSilencesIt:

    def test_stop_cue_exists_as_a_static_face(self):
        src = _live("audio_manager.gd")
        assert "static func stop_cue(cue: String) -> void:" in src

    def test_the_one_shot_is_addressable_at_all(self):
        """`_play_cue` kept NO handle on the player it created, so nothing
        outside it could silence a cue. One-shots are children of the
        AudioManager singleton, not of the scene, so they outlive
        `change_scene_to_file` as well as the panel that started them."""
        src = _live("audio_manager.gd")
        assert "var _live_players: Dictionary = {}" in src
        body = src[src.index("func _play_cue("):]
        body = body[:body.index("\n\nfunc ")]
        assert "_live_players.get_or_add(cue, []).append(p)" in body

    def test_the_registry_entry_is_dropped_when_the_cue_ends(self):
        """Otherwise `_live_players` grows without bound and `stop_cue` walks
        freed players."""
        src = _live("audio_manager.gd")
        body = src[src.index("func _play_cue("):]
        body = body[:body.index("\n\nfunc ")]
        assert "_forget_live(cue, p)" in body

    def test_the_stop_path_goes_through_finished_not_queue_free(self):
        """THE way to ship a worse bug here. `_oneshot_count` is decremented
        ONLY inside the `finished` lambda; a stop that frees the player
        directly leaks the MAX_ONESHOT_PLAYERS budget permanently and the game
        goes silent after fourteen cues."""
        src = _live("audio_manager.gd")
        shared = src[src.index("func _fade_out_now("):]
        shared = shared[:shared.index("\n\n\n")]
        assert "p.finished.emit()" in shared
        assert "queue_free" not in shared

        stop = src[src.index("func _stop_cue("):]
        stop = stop[:stop.index("\n\n\n")]
        assert "_fade_out_now(p" in stop
        assert "queue_free" not in stop

    def test_the_fade_is_idempotent(self):
        """Two fade paths can now reach the same player — the `max_s` timer
        and a `stop_cue` from a closing panel. Without a latch both build a
        tween, both callbacks pass `is_instance_valid`, and `finished` fires
        TWICE: the `_play_cue` lambda runs twice and `_oneshot_count` is
        decremented twice for ONE player, corrupting the very budget that
        stops the game running out of voices. Found by this slice's own review
        round; before `stop_cue` existed only one path could fade."""
        src = _live("audio_manager.gd")
        body = src[src.index("func _fade_out_now("):]
        body = body[:body.index(chr(10) * 3)]
        assert 'if p.has_meta("_retiring"):' in body
        assert body.index('has_meta("_retiring")') < body.index("create_tween"), (
            "the latch must precede the tween, or two tweens still start")
        assert "is_instance_valid(p) and p.playing" in body, (
            "and the callback needs the playing guard too — belt and braces "
            "on the emit that decrements the budget")

    def test_popup_base_stops_what_a_subclass_CLAIMED(self):
        """Not "stop everything": the base itself plays "back" ON close."""
        src = _live("popup_base.gd")
        assert "func claim_cue(p) -> void:" in src
        body = src[src.index("func close_popup():"):]
        assert "AudioManager.stop_player(p)" in body
        assert body.index("AudioManager.stop_player(p)") < \
            body.index('AudioManager.play("back")'), (
            "silence the arrival before playing the departure")

    def test_ownership_is_a_PLAYER_not_a_cue_name(self):
        """Review round: claiming a NAME made the ownership nominal — closing
        one popup would silence every live play of that sound, including
        another surface's. Measured shape: the tableau's close would have cut
        the strategic-interrupt popup's drum, still on screen. `_play_cue` has
        the handle at the moment it registers it, so `play()` hands it back."""
        src = _live("audio_manager.gd")
        assert ("static func play(cue: String, max_seconds: float = 0.0) "
                "-> AudioStreamPlayer:") in src
        # CONSCIOUS FLIP (Aug 28, 2026): this pin used to assert
        # `stop_player(p: AudioStreamPlayer)` — and the typed annotation WAS
        # the bug. One-shots free themselves when the sound ends, so a claimed
        # handle is routinely freed by close time, and a typed parameter makes
        # GDScript throw at the CALL, before the body's is_instance_valid
        # guard can run. Crashed live in the diorama's _on_close_pressed.
        assert "static func stop_player(p) -> void:" in src
        assert "static func stop_player(p: AudioStreamPlayer)" not in src, (
            "re-typing the parameter re-creates the freed-handle crash: the "
            "argument type check runs before the body's guard")
        # ...and the static face must FORWARD it. A signature that promises a
        # player while the body drops it on the floor is the ownership going
        # nominal again, silently — the mutation sweep found this pin inert
        # when it checked only the signature.
        face = src[src.index("static func play(cue: String"):]
        face = face[:face.index(chr(10) * 2 + "static func")]
        assert "return inst._play_cue(cue, max_seconds)" in face
        body = src[src.index("func _play_cue(cue: String, max_seconds: float)"):]
        body = body[:body.index(chr(10) * 2 + "func ")]
        assert body.rstrip().endswith("return p"), (
            "the player must be handed back, or no caller can own it")
        # every refusal path returns a typed null, not a bare return
        assert "\n\t\treturn\n" not in body and "\n\t\t\treturn\n" not in body

    def test_stop_player_survives_a_freed_handle(self):
        """The crash the typed signature shipped (Aug 28, 2026): a one-shot
        frees itself when its sound ends (`finished` -> `queue_free` in
        `_play_cue`), so by the time a diorama or popup closes, the handle it
        claimed is often a freed object. `stop_player(p: AudioStreamPlayer)`
        made GDScript reject the freed instance at the call site — "previously
        freed ... is not a subclass of the expected argument class" — BEFORE
        the body's own `is_instance_valid` could run. The parameter must stay
        untyped and the body must validate before touching any property."""
        src = _live("audio_manager.gd")
        body = src[src.index("static func stop_player(p) -> void:"):]
        body = body[:body.index("\n\n\n")]
        assert "is_instance_valid(p)" in body
        assert "p is AudioStreamPlayer" in body, (
            "untyped parameter means the body owns the type check now")
        assert body.index("is_instance_valid(p)") < body.index("p.playing"), (
            "validity must be established before any property access")
        assert body.index("is_instance_valid(p)") < \
            body.index("p is AudioStreamPlayer"), (
            "`p is Class` on a freed object is itself unsafe ordering — "
            "validity first")

    def test_a_world_swap_silences_one_shots_as_well_as_loops(self):
        """`dialog_manager.hide_all()` raw-hides every registered popup
        WITHOUT running its close handler, so neither ownership seam fires.
        `stop_all_loops` has always existed for exactly this; one-shots live
        under the same singleton and had no equivalent, so a 5-second peal
        rang on into the freshly loaded campaign."""
        src = _live("audio_manager.gd")
        assert "static func stop_all_cues() -> void:" in src
        main = _live("main.gd")
        assert "AudioManager.stop_all_cues()" in main
        assert main.index("AudioManager.stop_all_cues()") > \
            main.index("AudioManager.stop_all_loops()")

    def test_the_six_second_peal_is_claimed(self):
        """`proclamation_popup` is one of only two over-2s cues that route
        through PopupBase at all."""
        src = _live("proclamation_popup.gd")
        assert 'claim_cue(AudioManager.play("bells_peal"))' in src, (
            "claim the PLAYER the call returns, not the cue name")

    def test_the_departure_sound_is_deliberately_NOT_stopped(self):
        """The row's flagship example, and the one site to leave alone:
        `coin_pour` fires inside the Plunder handler, one line before
        `hide()`. It is the sound of the decision, not an ambience left
        ringing. Stopping it would delete the feedback."""
        src = _live("capture_choice_dialog.gd")
        assert 'AudioManager.play("coin_pour")' in src
        assert "stop_cue" not in src


# ══════════════════════════════════════════════════════════════════════════
# UX23-R6 — the diorama stops being a second audio implementation
# ══════════════════════════════════════════════════════════════════════════


class TestOneAudioImplementation:

    def test_the_diorama_no_longer_drives_its_own_player(self):
        src = _live("battle_diorama.gd")
        assert "AudioStreamPlayer.new()" not in src
        assert ": AudioStreamPlayer" not in src
        assert "_play_sound(" not in src
        assert "AUDIO_CANNON" not in src and "AUDIO_DRUM" not in src

    def test_it_routes_through_the_shared_manager(self):
        src = _live("battle_diorama.gd")
        assert '_cue("cannon")' in src
        assert '_cue("drum_sting")' in src
        body = src[src.index("func _cue(cue: String) -> void:"):]
        body = body[:body.index("\n\n\n")]
        assert "AudioManager.play(cue)" in body

    def test_and_the_battle_sounds_TOGGLE_survives_the_refactor(self):
        """The row said the guard would be forgotten; it had the direction
        backwards. The guard lives in the diorama and AudioManager cannot see
        it — routing the calls naively, as the row instructed, would have
        silently disabled the setting. It stays at the wrapper, so anything
        added there inherits it."""
        src = _live("battle_diorama.gd")
        body = src[src.index("func _cue(cue: String) -> void:"):]
        body = body[:body.index("\n\n\n")]
        assert "UiSettings.get_battle_sfx()" in body
        assert body.index("get_battle_sfx") < body.index("AudioManager.play"), (
            "the guard must gate the play, not follow it")

    def test_closing_the_tableau_silences_its_own_guns(self):
        src = _live("battle_diorama.gd")
        body = src[src.index("func _on_close_pressed() -> void:"):]
        assert "AudioManager.stop_player(p)" in body

    def test_EVERY_diorama_one_shot_goes_through_the_claim(self):
        """The census the first draft of this class did not have, and the
        reason a P2 shipped under a green pin.

        `test_closing_the_tableau_silences_its_own_guns` only asserted that
        the close CALLS the stop — which was satisfied while six of the
        tableau's eight one-shots bypassed `_cue()` entirely and were never
        claimed. The two that WERE routed happened to be the two shortest
        (`cannon` 1.80 s, `drum_sting` 1.55 s, neither even capped), while the
        verdict `fanfare` — 36.5 s of file, 5.2 s capped — played on over the
        map after the tableau vanished.

        Routing them also closed a pre-existing hole: `musket_volley`,
        `cavalry` and `whinny` were outside the `get_battle_sfx()` guard, so
        the "Battle sounds" toggle only ever silenced 5 of the 8."""
        src = _live("battle_diorama.gd")
        direct = [ln.strip() for ln in src.split("\n")
                  if "AudioManager.play(" in ln]
        assert direct == ["var p := AudioManager.play(cue)"], (
            "every diorama one-shot must go through `_cue()`, which claims it "
            f"for the close and applies the toggle: {direct}")
        cued = [ln for ln in src.split("\n") if "_cue(\"" in ln]
        assert len(cued) >= 8, (
            f"expected the tableau's eight one-shots, found {len(cued)}")

    def test_the_claim_list_is_deduped(self):
        """`_play_cinematic` runs again on Replay, so an un-deduped list asks
        the manager to stop one player twice."""
        src = _live("battle_diorama.gd")
        body = src[src.index("func _cue(cue: String) -> void:"):]
        body = body[:body.index(chr(10) * 3)]
        assert "not _own_cues_started.has(p)" in body

    def test_no_gd_file_outside_the_manager_owns_an_audio_player(self):
        """The structural guard the row asked for. Modelled on the colour and
        AST censuses already in the suite: scan every `.gd`, allow exactly one
        file, and refuse to pass vacuously on an empty scan."""
        offenders = []
        scanned = 0
        for root, _dirs, files in os.walk(GODOT):
            for name in files:
                if not name.endswith(".gd"):
                    continue
                path = os.path.join(root, name)
                scanned += 1
                if os.path.basename(path) == "audio_manager.gd":
                    continue
                for i, line in enumerate(_py_live(path).split("\n"), 1):
                    # What is forbidden is OWNING a player — declaring one or
                    # constructing one. Merely naming the type in prose is
                    # not a second audio implementation, and the first draft
                    # of this census failed on the very docstring explaining
                    # why the diorama no longer has one.
                    if ("AudioStreamPlayer.new()" in line
                            or ": AudioStreamPlayer" in line):
                        offenders.append(f"{name}:{i}")
        assert scanned > 40, f"census scanned only {scanned} .gd files"
        assert not offenders, (
            "audio belongs to AudioManager.play/start_loop — a second "
            f"implementation bypasses the registry, the throttle, the "
            f"one-shot budget and max_s: {offenders}")


# ══════════════════════════════════════════════════════════════════════════
# UX23-1 — the caps were measured, and two of them were silencing the cue
# ══════════════════════════════════════════════════════════════════════════


class TestACapNeverEndsBeforeTheSoundBegins:

    def test_the_two_measured_offenders_carry_a_start_offset(self):
        """Measured with `tools/audio_envelope_probe.gd` (Godot decodes mp3
        and ogg; the venv has no decoder). `letter_open` cap 1.4 s vs onset
        2.05 s; `cavalry` cap 3.2 s vs onset 4.9 s — both caps ended before
        their sound started."""
        src = _read("audio_manager.gd")
        letter = next(ln for ln in src.split("\n") if '"letter_open": {' in ln)
        cavalry = next(ln for ln in src.split("\n") if '"cavalry": {' in ln)
        assert '"start_s": 1.9' in letter
        assert '"start_s": 4.6' in cavalry

    def test_start_s_is_honoured_by_the_player(self):
        src = _live("audio_manager.gd")
        body = src[src.index("func _play_cue("):]
        body = body[:body.index("\n\nfunc ")]
        assert 'var start_at := float(spec.get("start_s", 0.0))' in body
        assert "p.play(start_at)" in body

    def test_no_other_cue_grew_an_offset_by_accident(self):
        """Nine of the eleven measured onsets land inside their caps."""
        src = _read("audio_manager.gd")
        offset_cues = [m.group(1) for m in
                       re.finditer(r'^\t"([a-z_0-9]+)": \{[^\n]*"start_s"',
                                   src, re.M)]
        assert sorted(offset_cues) == ["cavalry", "letter_open"]

    def test_the_probe_refuses_to_report_on_a_dummy_audio_device(self):
        """Without this the probe would cheerfully report every cue as a
        fade-in when Godot hands it no device — the measurement equivalent of
        an inert pin."""
        with io.open(os.path.join(REPO_ROOT, "tools",
                                  "audio_envelope_probe.gd"),
                     encoding="utf-8") as fh:
            probe = fh.read()
        assert "device_ok" in probe
        assert "quit(0 if _device_ok else 1)" in probe

    def test_the_spec_records_the_measurement_not_an_open_worry(self):
        with io.open(os.path.join(REPO_ROOT, "docs", "MUSIC_SOUND_SPEC.md"),
                     encoding="utf-8") as fh:
            spec = fh.read()
        assert "§1a Measured lengths" in spec
        assert "9.22 s" in spec, "the ~0:15 figure was wrong by six seconds"
        assert "the eleven capped cues owe a\n> re-audition" not in spec


# ══════════════════════════════════════════════════════════════════════════
# UX23-R5 — an order that names a marshal is never a dialogue answer
# ══════════════════════════════════════════════════════════════════════════


ROSTER = ["Ney", "Davout", "Soult", "Murat", "Lannes"]
ADVISORY = {"options": [{"label": "Act on this counsel",
                         "action": "execute_suggestion"},
                        {"label": "Thank you", "action": "dismiss"}]}
PROPOSAL = {"options": [{"label": "Accept", "action": "accept_proposal"},
                        {"label": "Reject", "action": "reject_proposal"},
                        {"label": "Counter", "action": "counter_offer"}]}
ULTIMATUM = {"options": [{"label": "Yield", "action": "yield_ultimatum"},
                         {"label": "Defy", "action": "defy_ultimatum"}]}


class TestAnOrderIsNotAnAnswer:

    @pytest.mark.parametrize("line", [
        "soult, cancel your march",     # the comma address
        "cancel soult's march",         # the name mid-sentence
        "ney, hold position",
    ])
    def test_a_line_naming_a_marshal_is_refused(self, line):
        assert match_dialogue_answer(ADVISORY, line, ROSTER) is None

    def test_without_the_guard_it_really_did_hijack(self):
        """Falsifiable negative: the same shape, no roster, still matches — so
        the pin above is testing the guard and not something else.

        Aug 30, 2026: the line was "soult, cancel your march", which a SECOND
        guard landed that day now refuses on its own — "march" is an order
        noun, so the answer arms decline it whether or not a marshal is named
        (an order names the war; an answer names the decision). Keeping the
        old line would have made this control pass for the wrong reason, so
        it is narrowed to a line whose ONLY order-ish content is the address
        itself. The control's meaning is unchanged: with a roster the marshal
        guard refuses; without one, the line still matches.
        """
        assert match_dialogue_answer(ADVISORY, "soult, cancel", None) == "cancel"
        assert match_dialogue_answer(ADVISORY, "soult, cancel", ROSTER) is None

    @pytest.mark.parametrize("dialogue,line,expected", [
        (PROPOSAL, "accept", "accept"),
        (PROPOSAL, "accept prussia's proposal", "accept"),
        (PROPOSAL, "reject the offer", "reject"),
        (PROPOSAL, "counter with gold", "counter"),
        # "money" contains "ney". This line reaches the KEYWORD arm, below
        # the guard, so a guard built on bare containment rather than
        # `whole_phrase_in` refuses it — and nothing else in the suite would
        # have caught that (a first draft used "counter with money", which
        # matches the label `Counter` verbatim in arm 1 and never reaches the
        # guard at all; the mutation sweep found the pin inert).
        (ADVISORY, "never mind the money", "never mind"),
        (ADVISORY, "thank you", "thank you"),
        (ADVISORY, "dismiss", "dismiss"),
    ])
    def test_the_letter_book_still_answers(self, dialogue, line, expected):
        """The row's own "scope it to non-blocking dialogues" would have
        broken every one of these — `accept prussia's proposal` is the exact
        sentence the CA9 court guard was built to serve."""
        assert match_dialogue_answer(dialogue, line, ROSTER) == expected

    @pytest.mark.parametrize("dialogue,line", [
        (ULTIMATUM, "ney, yield no ground"),
        (ULTIMATUM, "soult, defy them"),
        (PROPOSAL, "ney, accept no excuses"),
        (PROPOSAL, "davout, reject the flank"),
    ])
    def test_a_ONE_WORD_label_does_not_bypass_the_guard(self, dialogue, line):
        """THE P1 the review round caught, and it is the row's own defect
        wearing the fix's clothes.

        Arm 1 is BARE-SUBSTRING containment, and the first cut put the guard
        below it "because a verbatim match is never a guess". So any dialogue
        whose option label is one common word matched before the guard ever
        ran. Measured on production option sets: with an incoming ULTIMATUM
        mounted, **`Ney, yield no ground` YIELDED THE ULTIMATUM** — an order
        to a marshal ceding the demanded provinces. Same shape for
        `Accept`/`Reject` on an incoming proposal and `Cancel` on the
        war-purpose chooser.
        """
        assert match_dialogue_answer(dialogue, line, ROSTER) is None

    @pytest.mark.parametrize("dialogue,line,expected", [
        (ULTIMATUM, "yield", "yield"),
        (ULTIMATUM, "defy", "defy"),
        (PROPOSAL, "accept", "accept"),
    ])
    def test_but_the_one_word_answer_itself_still_works(
            self, dialogue, line, expected):
        assert match_dialogue_answer(dialogue, line, ROSTER) == expected

    def test_a_label_that_legitimately_names_a_marshal_still_resolves(self):
        """Why the guard sits BELOW the verbatim arms and above the
        inferential ones.

        The marshal named here is IN the roster on purpose. A first draft used
        `Commission Suchet` — a bench candidate, not a standing marshal — so
        the guard never fired on that line whatever its placement, and the
        mutation sweep found the pin inert."""
        assert "Ney" in ROSTER, "precondition: the guard would fire on this line"
        recall = {"options": [{"label": "Recall Ney", "action": "recall_ney"},
                              {"label": "Leave him", "action": "dismiss"}]}
        assert match_dialogue_answer(
            recall, "recall ney", ROSTER) == "recall ney"

    def test_the_subset_hijack_the_row_did_not_name(self):
        """`Send as ordered` is {send, as, ordered}, which `as ordered, send
        Ney` satisfies in any word order. Fixing only the keyword branch would
        have left the completion definition unmet."""
        send = {"options": [{"label": "Send as ordered",
                             "action": "send_override"},
                            {"label": "Reconsider", "action": "back_out"}]}
        assert match_dialogue_answer(send, "as ordered, send ney", ROSTER) is None
        assert match_dialogue_answer(
            send, "send as ordered", ROSTER) == "send as ordered"

    def test_both_call_sites_hand_it_the_roster(self):
        """A guard nobody passes a roster to is a guard that does nothing."""
        with io.open(os.path.join(REPO_ROOT, "backend", "main.py"),
                     encoding="utf-8") as fh:
            src = fh.read()
        assert "def _player_marshal_names(world) -> list:" in src
        calls = src.count("_player_marshal_names(world)") - 1  # minus the def
        assert calls == 2, (
            f"both matcher call sites must pass the roster; found {calls}")

    def test_a_captured_marshal_does_not_block_an_answer(self):
        """A name the player can no longer order is not an order, and letting
        it veto a dialogue answer would be a second defect wearing the first
        one's coat.

        BEHAVIOURAL, deliberately. The first draft grepped main.py for
        `get_player_marshals()` — which is exactly what the defect looked
        like: that call does NOT filter prisoners (`capture_marshal` leaves
        the marshal in the roster at strength 0 under his own nation), so the
        pin passed while the docstring's claim was false. The sweep caught it.
        """
        from backend.main import _player_marshal_names
        from backend.models.world_state import WorldState

        world = WorldState.from_scenario(SCENARIO)
        assert "Ney" in _player_marshal_names(world), "precondition"

        ney = world.marshals["Ney"]
        ney.captured_by = "Austria"
        ney.strength = 0
        assert "Ney" in world.marshals, (
            "precondition: capture leaves him in the roster — that is the trap")

        assert "Ney" not in _player_marshal_names(world), (
            "a prisoner's name must not veto a dialogue answer")


# ══════════════════════════════════════════════════════════════════════════
# UX23-R4 — the dispatch re-read stops naming a marshal already paid
# ══════════════════════════════════════════════════════════════════════════


SCENARIO = os.path.join(GODOT, "assets", "maps", "europe_1805.json")


@pytest.fixture
def world():
    from backend.models.world_state import WorldState
    return WorldState.from_scenario(SCENARIO)


class TestTheDispatchReReadIsNotStale:

    def _world_owing_ney(self):
        from backend.models.world_state import WorldState
        w = WorldState.from_scenario(SCENARIO)
        w.marshals["Ney"].battles_won = 3
        w._dotation_processed_turn = None
        w._process_dotation_state()
        return w

    def test_paying_a_marshal_drops_him_from_a_re_read(self, world):
        from backend.commands.executor import CommandExecutor
        from backend.game_logic.dispatch import build_morning_dispatch
        from backend.game_logic.dotation import build_unmet_marshals

        ney = world.marshals["Ney"]
        ney.battles_won = 3
        world._dotation_processed_turn = None
        world._process_dotation_state()
        build_morning_dispatch(world)
        stored = world.last_morning_dispatch["situation"]["unmet_marshals"]
        assert any(r["marshal"] == "Ney" for r in stored), "precondition"

        CommandExecutor().execute(
            {"command": {"action": "grant_pension", "marshal": "Ney"}},
            {"world": world})

        assert not any(r["marshal"] == "Ney"
                       for r in build_unmet_marshals(world, "France")), (
            "the re-read must not go on naming a marshal already paid")
        assert any(r["marshal"] == "Ney"
                   for r in world.last_morning_dispatch["situation"]
                   ["unmet_marshals"]), (
            "and it must do it WITHOUT mutating the stored dispatch")

    def test_the_endpoint_overlays_onto_a_copy(self):
        """A read endpoint must not mutate. `dict()` twice, then a pure
        builder."""
        src = _py_live(os.path.join(REPO_ROOT, "backend", "main.py"))
        body = src[src.index("def get_dispatch():"):]
        body = body[:body.index("\n@app")]
        assert "dispatch = dict(dispatch)" in body
        assert "situation = dict(" in body
        assert "build_unmet_marshals(" in body

    def test_the_endpoint_never_rebuilds_the_whole_dispatch(self):
        """THE trap. `build_morning_dispatch` clears `pending_dispatch_events`,
        overwrites the PC-7 headline-lead memory, latches
        `last_expectation_seen`, re-adds notification families and rolls
        `check_sabotage_discovery` — calling it from a GET would let the
        player re-roll Talleyrand's sabotage by pressing R."""
        src = _py_live(os.path.join(REPO_ROOT, "backend", "main.py"))
        body = src[src.index("def get_dispatch():"):]
        body = body[:body.index("\n@app")]
        assert "build_morning_dispatch" not in body

    def test_the_builder_is_pure(self, world):
        """Called twice, it must change nothing — the latch stayed behind in
        the once-per-turn pass."""
        from backend.game_logic.dotation import build_unmet_marshals

        ney = world.marshals["Ney"]
        ney.battles_won = 3
        world._dotation_processed_turn = None
        world._process_dotation_state()
        seen_before = int(getattr(ney, "last_expectation_seen", 0))
        grace_before = int(ney.expectation_grace_turn)

        first = build_unmet_marshals(world, "France")
        second = build_unmet_marshals(world, "France")

        assert first == second
        assert int(getattr(ney, "last_expectation_seen", 0)) == seen_before
        assert int(ney.expectation_grace_turn) == grace_before

    def test_the_ENDPOINT_returns_the_refreshed_rows(self):
        """The behavioural pin the first draft of this class lacked, and the
        review round said so: three of its four R4 tests grepped main.py's
        source, and the fourth called the builder directly. Nothing bound the
        endpoint's payload SHAPE — a refactor renaming the nesting, or
        returning the store instead of the copy, would have left every test
        green while the fix went production-dead.
        """
        from fastapi.testclient import TestClient
        from backend.commands.executor import CommandExecutor
        from backend.game_logic.dispatch import build_morning_dispatch
        import backend.main as main_module

        world = self._world_owing_ney()
        build_morning_dispatch(world)
        stored_rows = world.last_morning_dispatch["situation"]["unmet_marshals"]
        assert any(r["marshal"] == "Ney" for r in stored_rows), "precondition"

        prev_world = main_module.world
        prev_state = main_module.game_state.get("world")
        try:
            main_module.world = world
            main_module.game_state["world"] = world
            client = TestClient(main_module.app)

            before = client.get("/dispatch").json()
            assert any(r["marshal"] == "Ney" for r in
                       before["dispatch"]["situation"]["unmet_marshals"])

            CommandExecutor().execute(
                {"command": {"action": "grant_pension", "marshal": "Ney"}},
                {"world": world})

            after = client.get("/dispatch").json()
            assert not any(
                r["marshal"] == "Ney" for r in
                after["dispatch"]["situation"]["unmet_marshals"]), (
                "the re-read still names a marshal the player already paid")
            assert any(
                r["marshal"] == "Ney" for r in
                world.last_morning_dispatch["situation"]["unmet_marshals"]), (
                "and it must do that WITHOUT mutating the store — a read "
                "endpoint that mutates is the defect one level up")
        finally:
            main_module.world = prev_world
            if prev_state is not None:
                main_module.game_state["world"] = prev_state

    def test_a_mid_turn_shortfall_still_states_its_window(self, world):
        """The grace clock is written only by the once-per-turn pass, so a
        shortfall that opens SINCE it ran had `grace_turns_left = -1` — and
        `dispatch_view.gd` renders a note only when the row is eroding or the
        countdown is >= 0. The row that exists to prompt action was printing
        without the window it is prompting about."""
        from backend.game_logic.dotation import GRACE_TURNS, build_unmet_marshals

        ney = world.marshals["Ney"]
        ney.battles_won = 3                     # a victory, mid-turn
        assert int(ney.expectation_grace_turn) == -1, (
            "precondition: the turn pass has not run since")

        row = next(r for r in build_unmet_marshals(world, "France")
                   if r["marshal"] == "Ney")
        assert row["grace_turns_left"] == GRACE_TURNS, (
            "his patience has not started burning yet, so the honest figure "
            "is the full window — never -1, which renders as nothing at all")

    def test_the_dispatch_builder_reads_the_shared_helper(self):
        """GR1 — one implementation of the Unmet Marshals row, not two."""
        import inspect
        from backend.game_logic import dispatch as dispatch_mod
        src = inspect.getsource(dispatch_mod)
        assert "unmet_marshals = build_unmet_marshals(world, player_nation)" in src
        assert 'unmet_marshals.append({' not in src


# ══════════════════════════════════════════════════════════════════════════
# UX23-R8 — the sentence renders where it is produced
# ══════════════════════════════════════════════════════════════════════════


class TestTheReviewRoundsRemainingFixes:
    """Seven smaller findings from the same fleet."""

    def test_start_s_can_never_run_past_the_end_of_the_file(self):
        """The new mechanism could re-create the bug it was built to fix: an
        offset past the stream plays nothing at all, and the length census
        (`_parse_cues`) reads `files` and `max_s` only — it cannot see
        `start_s`. Clamped with a second of headroom, so a mis-typed offset
        degrades to a short cue rather than to silence."""
        src = _live("audio_manager.gd")
        body = src[src.index("func _play_cue("):]
        body = body[:body.index(chr(10) * 2 + "func ")]
        assert "stream_len > 0.0 and start_at >= stream_len - 0.25" in body
        assert "start_at = max(0.0, stream_len - 1.0)" in body

    def test_the_reward_dialogs_six_second_bugle_is_stopped(self):
        """`to_the_color` is 42.4 s of file capped to 5.2 — the longest cue in
        the tree — on a dialog the player dismisses in one click. It was
        unclaimed: `reward_dialog` extends CanvasLayer, not PopupBase, so it
        holds its own handle."""
        src = _live("reward_dialog.gd")
        assert '_own_cue = AudioManager.play("to_the_color")' in src
        assert src.count("AudioManager.stop_player(_own_cue)") == 2, (
            "both exits — the option press and the cancel")

    def test_the_enemy_phase_report_mirrors_main_gds_ordering(self):
        """The arm three lines above declares it mirrors main.gd, which reads
        voice -> delegation -> expectation -> jealousy -> ... -> observation
        -> campaign cost. The first cut put expectation AFTER jealousy and the
        campaign cost BEFORE Berthier — and HC-2's own contract calls the cost
        the line the report CLOSES on."""
        body = _live("enemy_phase_dialog.gd")
        body = body[body.index("func _format_berthier_report"):]
        body = body[:body.index("\nfunc _format_bombardment")]
        assert body.index("expectation_note") < body.index("jealousy_note")
        assert body.index('report.get("observation"') < \
            body.index("campaign_cost_note")

    def test_march_step_is_NOT_recorded_as_dead(self):
        """A claim of mine the review round killed: `march_step` IS called,
        from `scenes/war_table_piece.gd` — my grep covered `scripts/`. Its
        0.65 s cap is load-bearing on a 7.5 s loop file, and retiring the row
        on that claim would have silenced every march on the map."""
        import os as _os
        hits = []
        for root, _d, files in _os.walk(GODOT):
            for name in files:
                if not name.endswith(".gd"):
                    continue
                with io.open(_os.path.join(root, name), encoding="utf-8") as fh:
                    if 'play("march_step")' in fh.read():
                        hits.append(name)
        assert hits, "march_step must still have a call site"
        with io.open(_os.path.join(REPO_ROOT, "docs", "MUSIC_SOUND_SPEC.md"),
                     encoding="utf-8") as fh:
            spec = fh.read()
        assert "One registry cue has no call site" in spec
        assert "Two registry cues have no call site" not in spec

    def test_the_owed_audition_has_a_GR9_owner_row(self):
        """It was a floating sentence while STATUS and CLAUDE.md said nothing
        but the reward curve was open."""
        with io.open(os.path.join(REPO_ROOT, "docs", "BUG_FIXES.md"),
                     encoding="utf-8") as fh:
            bug = fh.read()
        assert "UX23-R9" in bug
        for required in ("*Owner:*", "*Landing slice:*",
                         "*Completion definition:*", "*STATUS line:*",
                         "*Behaviour test:*"):
            assert required in bug, f"GR9 needs {required}"
        for path in ("docs/STATUS.md", "CLAUDE.md"):
            with io.open(os.path.join(REPO_ROOT, path), encoding="utf-8") as fh:
                assert "UX23-R9" in fh.read(), path

    def test_the_record_does_not_claim_the_player_heard_nothing(self):
        """The probe measured 0.0088 RMS in the capped window, not zero. The
        slice's own follow-up table contradicted its own prose."""
        with io.open(os.path.join(REPO_ROOT, "docs", "BUG_FIXES.md"),
                     encoding="utf-8") as fh:
            bug = fh.read()
        assert "nothing — the cap ended before the paper rustled" not in bug
        assert "0.0088 RMS" in bug

    def test_the_sweep_harness_refuses_a_red_baseline(self):
        """Found while fixing a syntax error in this very file: a test file
        that does not COLLECT makes pytest exit non-zero, which the harness
        reads as "the pin bound the mutation" — so every mutation reports
        KILLED. Measured: a clean 30-of-30 against a file that could not be
        imported. The instrument reported perfect health precisely when it was
        blind."""
        with io.open(os.path.join(REPO_ROOT, "tools", "mutation_sweep.py"),
                     encoding="utf-8") as fh:
            src = fh.read()
        assert "def _baseline_green(" in src
        assert "if not _baseline_green(mutations):" in src


class TestTheEnemyPhaseShowsWhatItProduces:

    def test_both_notes_render_in_the_enemy_phase_dialog(self):
        """Produced by the SHARED `_execute_attack`, so they fire on defence
        too — and a defensive victory is where most of a player's battles are
        won. The whitelist read neither, so the backend built the sentence and
        nothing showed it."""
        body = _live("enemy_phase_dialog.gd")
        body = body[body.index("func _format_berthier_report"):]
        body = body[:body.index("\nfunc _format_bombardment")]
        assert 'report.get("expectation_note", "")' in body
        assert 'report.get("campaign_cost_note", "")' in body

    def test_the_backend_still_produces_them(self):
        """Falsifiable negative: if a later slice gates the producer instead,
        the render arms above become decoration and this reddens."""
        import inspect
        from backend.commands import combat_executor
        src = inspect.getsource(combat_executor)
        assert 'result["battle_report"]["expectation_note"]' in src
        assert 'result["battle_report"]["campaign_cost_note"]' in src

    def test_no_reward_chip_is_added_where_it_would_open_behind_the_modal(self):
        """`enemy_phase_dialog.tscn` is CanvasLayer 118 and
        `reward_dialog.tscn` is 109, so a [Reward…] chip here would open the
        dialog BEHIND the modal that launched it. The row's "the same
        affordance on EVERY surface" is unachievable, and the sentence alone
        is the honest half."""
        assert "layer = 118" in _read("enemy_phase_dialog.tscn", "scenes")
        assert "layer = 109" in _read("reward_dialog.tscn", "scenes")
        body = _live("enemy_phase_dialog.gd")
        assert "marshal_reward" not in body


class TestUX23R9TheBugleEndsRatherThanStops:
    """UX23-R9, closed September 1, 2026 — on measurement, not on taste.

    The row asked a question a machine was said to be unable to answer:
    does a capped bugle sound abrupt? The answerable form of it is *how
    loud is the cue at the instant the fade begins, and what happens
    underneath the fade* — a fade from near-silence is inaudible, a fade
    over a swelling note is someone hitting stop.

    Measured on the uncapped renders (`tools/ux23_r9_phrase_probe.py`'s
    envelope, RMS per 20 ms window, normalised to peak):

        reveille      cut at 51.6% of peak, rising to 85.0% inside the fade
        to_the_color  cut at  8.1% (a real note gap) but the next phrase
                      reaches 90.5% inside the fade
        fanfare       cut at 15.7%, never above 22.5% inside the fade

    A search over caps from 3.0 s to 9.0 s found no better cut for either
    bugle — the quietest fade window in six seconds of music still has to
    swallow ~60% of peak. These are continuous calls with no trough, so
    the CAP was never the lever and the row's "move `max_s` to the next
    phrase boundary" could not have worked. The fade length is the lever.

    So `fade_s` joins `max_s` as a per-cue registry field, and the two
    cues the measurement condemns get a 2.0 s decrescendo. `fanfare` is
    deliberately left at the 0.8 s default: it already fades from a quiet
    place, and changing it would be a change made without evidence.
    """

    LOUD_CUT = ("reveille", "to_the_color")

    def test_the_two_loud_cuts_carry_a_long_fade(self):
        """Killed by: dropping `fade_s` from either registry row."""
        body = _live("audio_manager.gd")
        for cue in self.LOUD_CUT:
            row = [ln for ln in body.split("\n")
                   if ln.strip().startswith('"%s":' % cue)]
            assert len(row) == 1, cue
            assert '"fade_s": 2.0' in row[0], (
                "%s fades over a rising phrase and needs the long fade" % cue)

    def test_the_quiet_cut_is_left_alone(self):
        """`fanfare` fades from 15.7% and never exceeds 22.5% under the
        fade. Leaving it at the default is the evidence-driven line, not
        an oversight — a blanket change would be a taste decision wearing
        a measurement's coat.

        Killed by: adding `fade_s` to the fanfare row."""
        body = _live("audio_manager.gd")
        row = [ln for ln in body.split("\n")
               if ln.strip().startswith('"fanfare":')]
        assert len(row) == 1
        assert "fade_s" not in row[0]

    def test_the_player_honours_the_per_cue_fade(self):
        """A registry field nothing reads is a comment.

        Killed by: reverting `_fade_stop` to its hardcoded 0.8, or
        dropping the `fade_s` lookup at the call site."""
        body = _live("audio_manager.gd")
        assert ("func _fade_stop(p: AudioStreamPlayer, after_s: float, "
                "fade_s: float = 0.8) -> void:") in body
        assert "_fade_out_now(p, fade_s)" in body
        assert '_fade_stop(p, cap, float(spec.get("fade_s", 0.8)))' in body

    def test_the_default_is_unchanged_for_every_other_cue(self):
        """68-odd call sites rely on the old behaviour; only cues that
        ask for a longer fade may get one.

        Killed by: changing the default in either the signature or the
        call site."""
        body = _live("audio_manager.gd")
        assert 'spec.get("fade_s", 0.8)' in body
        assert "fade_s: float = 0.8" in body
        assert body.count('"fade_s"') == 3
