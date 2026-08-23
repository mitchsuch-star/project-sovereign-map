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

    def test_popup_base_stops_what_a_subclass_CLAIMED(self):
        """Not "stop everything": the base itself plays "back" ON close."""
        src = _live("popup_base.gd")
        assert "func claim_cue(cue: String) -> void:" in src
        body = src[src.index("func close_popup():"):]
        assert "AudioManager.stop_cue(cue)" in body
        assert body.index("AudioManager.stop_cue(cue)") < \
            body.index('AudioManager.play("back")'), (
            "silence the arrival before playing the departure")

    def test_the_six_second_peal_is_claimed(self):
        """`proclamation_popup` is one of only two over-2s cues that route
        through PopupBase at all."""
        src = _live("proclamation_popup.gd")
        assert 'AudioManager.play("bells_peal")' in src
        assert 'claim_cue("bells_peal")' in src

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
        assert "AudioManager.stop_cue(cue)" in body

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


class TestAnOrderIsNotAnAnswer:

    @pytest.mark.parametrize("line", [
        "soult, cancel your march",     # the comma address
        "cancel soult's march",         # the name mid-sentence
        "ney, hold position",
    ])
    def test_a_line_naming_a_marshal_is_refused(self, line):
        assert match_dialogue_answer(ADVISORY, line, ROSTER) is None

    def test_without_the_guard_it_really_did_hijack(self):
        """Falsifiable negative: the same line, no roster, still matches — so
        the pin above is testing the guard and not something else."""
        assert match_dialogue_answer(
            ADVISORY, "soult, cancel your march", None) == "cancel"

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

    def test_a_fallen_marshal_does_not_block_an_answer(self):
        """The roster is STANDING marshals — a name the player can no longer
        order is not an order, and letting it veto a dialogue answer would be
        a second defect wearing the first one's coat."""
        with io.open(os.path.join(REPO_ROOT, "backend", "main.py"),
                     encoding="utf-8") as fh:
            src = fh.read()
        body = src[src.index("def _player_marshal_names(world) -> list:"):]
        body = body[:body.index("\n\n@app")]
        assert "get_player_marshals()" in body


# ══════════════════════════════════════════════════════════════════════════
# UX23-R4 — the dispatch re-read stops naming a marshal already paid
# ══════════════════════════════════════════════════════════════════════════


SCENARIO = os.path.join(GODOT, "assets", "maps", "europe_1805.json")


@pytest.fixture
def world():
    from backend.models.world_state import WorldState
    return WorldState.from_scenario(SCENARIO)


class TestTheDispatchReReadIsNotStale:

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
