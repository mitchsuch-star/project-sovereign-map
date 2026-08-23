"""The four defects reported from a live turn-3 France/1805 campaign — Aug 23, 2026.

The user's words, and what each turned out to be:

 1. "when clicking envoys and such the paper noise goes on for a really long
    time" — `ui/letter_open.mp3` is **38.6 seconds** long and was registered as
    a one-shot cue with no cap. `AudioManager._fade_stop` existed and worked,
    but a cap only three of 71 call sites remembered to pass is not a cap.

 2. "i cant end my turn ... it says i cant answer lesser courts when i have
    pending issue to resolve but i see nothing else to resolve" — THREE
    separate faults stacked:
      (a) `_execute_command` cleared `_awaiting_end_turn_confirmation`
          unconditionally and *then* dispatched "end turn", so the typed route
          could never confirm the lapse. The warning's own text names that
          route. (client, pinned structurally below)
      (b) `activate_mailbox_item` refused for every LOCAL_PLANNING type, so a
          Talleyrand `advisory` in the active slot made every routine envoy
          unanswerable — and the refusal named nothing.
      (c) the mailbox panel is CanvasLayer 119 and the dialogue modals it
          points at are 110, so the panel was drawn ON TOP of the matter it
          was telling the player to go and settle. Hence "i see nothing".

 3. "when generals ask for more there's no way to do it without menuing, and
    when you pay them it doesn't dismiss their popup of wanting, and it
    happens so early in the war" — three defects and one balance call:
      (a) the rail told the player to navigate ("press G") instead of acting;
      (b) the rail was reconciled ONLY by the once-per-turn dotation pass, so
          paying a marshal left the row standing beside the confirmation that
          had just said his expectation was met;
      (c) the first thing the player is ever told names an ESTATE, and France
          holds zero conquered provinces at the 1805 boot;
      (d) GRACE_TURNS 2 -> 4 (in-band retune; see the note at the constant).
    Plus the no-op re-size: `compute_rente_face` ignores the rente already
    held, so a fully-paid marshal reached the success path and burned 1 of 2
    admin actions rewriting his pension to the same number.

 4. "the bernodotte free attack didnt work" — pinned in
    tests/test_counter_punch_ap_gate.py (its own file: it is a combat/action-
    economy defect, not a UX one).
"""

import io
import os
import re
import struct
import wave

import pytest

from backend.display_names import DIALOGUE_TYPE_DISPLAY, dialogue_display_name
from backend.game_logic import dotation
from backend.models.dialogue_manager import DialogueManager
from backend.models.world_state import WorldState


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GODOT = os.path.join(REPO_ROOT, "godot-client", "project-sovereign")
SCRIPTS = os.path.join(GODOT, "scripts")
AUDIO_ROOT = os.path.join(GODOT, "assets", "audio")


def _script(name, sub="scripts"):
    with open(os.path.join(GODOT, sub, name), encoding="utf-8") as fh:
        return fh.read()


# ══════════════════════════════════════════════════════════════════════
# 1 — THE AUDIO CAP
# ══════════════════════════════════════════════════════════════════════

def _mp3_duration(path):
    data = io.open(path, "rb").read()
    i = 0
    if data[:3] == b"ID3":
        i = 10 + (((data[6] & 0x7F) << 21) | ((data[7] & 0x7F) << 14)
                  | ((data[8] & 0x7F) << 7) | (data[9] & 0x7F))
    br_v1 = [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 0]
    br_v2 = [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160, 0]
    sr = {3: [44100, 48000, 32000], 2: [22050, 24000, 16000],
          0: [11025, 12000, 8000]}
    total = 0.0
    while i < len(data) - 4:
        if data[i] == 0xFF and (data[i + 1] & 0xE0) == 0xE0:
            ver, layer = (data[i + 1] >> 3) & 3, (data[i + 1] >> 1) & 3
            bi, sri, pad = ((data[i + 2] >> 4) & 15, (data[i + 2] >> 2) & 3,
                            (data[i + 2] >> 1) & 1)
            if layer != 1 or bi in (0, 15) or sri == 3 or ver not in sr:
                i += 1
                continue
            rate = (br_v1 if ver == 3 else br_v2)[bi] * 1000
            hz, spf = sr[ver][sri], (1152 if ver == 3 else 576)
            flen = int((spf / 8 * rate) / hz) + pad
            if flen <= 0:
                i += 1
                continue
            total += spf / hz
            i += flen
        else:
            i += 1
    return total


def _ogg_duration(path):
    data = io.open(path, "rb").read()
    idx = data.rfind(b"OggS")
    if idx < 0:
        return None
    gran = struct.unpack("<q", data[idx + 6:idx + 14])[0]
    j = data.find(b"\x01vorbis")
    if j >= 0:
        return gran / struct.unpack("<I", data[j + 12:j + 16])[0]
    return gran / 48000.0 if data.find(b"OpusHead") >= 0 else None


def _asset_duration(rel):
    path = os.path.join(AUDIO_ROOT, rel.replace("/", os.sep))
    if not os.path.exists(path):
        return None
    low = rel.lower()
    if low.endswith(".mp3"):
        return _mp3_duration(path)
    if low.endswith(".ogg"):
        return _ogg_duration(path)
    if low.endswith(".wav"):
        with wave.open(path) as w:
            return w.getnframes() / w.getframerate()
    return None


def _parse_cues():
    """{cue: (files[], max_s or None)} straight out of the .gd registry.

    Asserts it parsed EVERY registry row. A cue the regex silently skipped —
    one with a digit in its name, or wrapped across two lines — would be
    exempt from the census below, which is the one hole that would let an
    over-long cue ship again unnoticed.
    """
    src = _script("audio_manager.gd")
    body = src[src.index("const CUES := {"):]
    body = body[:body.index("\n}\n")]
    rows = [ln for ln in body.split("\n")
            if ln.startswith('\t"') and '"files"' in ln]
    out = {}
    for m in re.finditer(r'^\t"([a-z_0-9]+)": \{(.+)\},?\s*$', body, re.M):
        cue, spec = m.group(1), m.group(2)
        files = re.findall(r'"([a-z_0-9]+/[^"]+)"', spec)
        cap = re.search(r'"max_s":\s*([0-9.]+)', spec)
        out[cue] = (files, float(cap.group(1)) if cap else None)
    assert len(out) == len(rows), (
        "the cue parser skipped %d registry row(s) — they would be exempt "
        "from the length census" % (len(rows) - len(out)))
    return out


# A one-shot fired by a UI interaction has to be over quickly. Anything longer
# is a deliberate ceremony and has to say so here, by name, with its budget.
# `_fade_stop` begins its fade AT the cap, so audible length is cap + this.
_FADE_S = 0.8
UI_CUE_CEILING_S = 4.0
CEREMONY_BUDGET_S = {
    "bells_peal": 6.0,      # the Proclamation — a new nation is declared
    "fanfare": 6.0,         # triumph
    "to_the_color": 6.0,    # honours for a marshal
    "musket_volley": 5.0,   # the battle diorama's exchange
    "reveille": 5.0,
    "first_call": 5.0,
    "mail_call": 5.5,
    "end_turn": 5.0,        # the drummer closes the day
}


class TestNoCuePlaysLongerThanItsMoment:
    """The pin that did not exist. `letter_open` was registered at 38.6s and
    nothing in the suite could have noticed — grep found zero hits for
    `letter_open`, `max_s`, `max_seconds` or `_fade_stop` across tests/."""

    def test_every_cue_is_bounded(self):
        offenders = []
        for cue, (files, cap) in sorted(_parse_cues().items()):
            budget = CEREMONY_BUDGET_S.get(cue, UI_CUE_CEILING_S)
            for rel in files:
                measured = _asset_duration(rel)
                assert measured is not None, (
                    "%s: %s could not be measured — an unmeasurable asset is "
                    "exempt from this census, the hole it exists to close"
                    % (cue, rel))
                effective = min(measured, cap + _FADE_S) if cap else measured
                if effective > budget + 0.01:
                    offenders.append(
                        f"{cue} ({rel}): asset {measured:.1f}s, cap "
                        f"{cap}, effective {effective:.1f}s > {budget}s")
        assert not offenders, (
            "a cue outlives the moment that fires it — give it a `max_s` in "
            "the CUES registry, or add it to CEREMONY_BUDGET_S deliberately:"
            "\n  " + "\n  ".join(offenders))

    def test_the_reported_cue_is_capped_hard(self):
        files, cap = _parse_cues()["letter_open"]
        assert _asset_duration(files[0]) > 30, (
            "if the asset was replaced, re-derive this pin rather than "
            "deleting it")
        assert cap is not None and cap <= 2.0, (
            "opening an envoy must not start 38 seconds of paper")

    def test_the_registry_is_the_default_and_the_argument_still_wins(self):
        src = _script("audio_manager.gd")
        assert 'max_seconds if max_seconds > 0.0 else float(spec.get("max_s"' in src

    def test_the_cap_is_actually_handed_to_the_fade(self):
        """The whole mechanism could be neutered in place with the suite
        green: replacing `_fade_stop(p, cap)` with `pass`, or widening the
        guard to `cap > 99.0`, left 39 tests passing while the 38.6s cue
        played in full again (review round, 4b09e59)."""
        src = _script("audio_manager.gd")
        body = src[src.index("func _play_cue("):]
        body = body[:body.index("\n\nfunc ")]
        assert "if cap > 0.0:" in body, "the cap guard was widened or removed"
        tail = body[body.index("if cap > 0.0:"):]
        assert "_fade_stop(p, cap)" in tail, (
            "the resolved cap must actually be handed to _fade_stop")

    def test_the_fade_really_stops_the_player(self):
        """RE-DERIVED Aug 23, 2026 (UX23-R1). The stop and the tween moved out
        of `_fade_stop` into `_fade_out_now`, which the timed cap and the new
        `stop_cue` now SHARE — one fade, two callers. The claim is unchanged;
        it is asserted against the shared helper, plus a pin that `_fade_stop`
        still routes through it rather than growing a second copy."""
        src = _script("audio_manager.gd")
        shared = src[src.index("func _fade_out_now("):]
        shared = shared[:shared.index("\n\n\n")]
        assert "p.stop()" in shared and "tween_property" in shared
        assert "p.finished.emit()" in shared, (
            "the finished lambda is the ONLY thing that decrements "
            "_oneshot_count — skipping it leaks the 14-player budget and the "
            "game goes silent after fourteen cues")
        timed = src[src.index("func _fade_stop("):]
        assert "_fade_out_now(p, 0.8)" in timed
        assert "tween_property" not in timed[:timed.index("\n\n")], (
            "one fade, not two")

    def test_a_rejected_play_does_not_poison_the_throttle(self):
        """The stamp used to be written above the budget and missing-file
        checks, so a play that never happened silenced the cue for its whole
        throttle window."""
        src = _script("audio_manager.gd")
        body = src[src.index("func _play_cue("):]
        body = body[:body.index("\n\nfunc ")]
        # Count FIRST: the mutation sweep caught this pin asserting only the
        # position of the good stamp, so re-adding the old one above the
        # guards left it green. There must be exactly one writer.
        writes = re.findall(r"_last_played_ms\[cue\]\s*=", body)
        assert len(writes) == 1, (
            "the throttle window must be stamped in exactly one place; "
            f"found {len(writes)}")
        stamp = body.index("_last_played_ms[cue] =")
        assert body.index("if _oneshot_count >= MAX_ONESHOT_PLAYERS:") < stamp
        assert body.index("if stream == null:") < stamp


# ══════════════════════════════════════════════════════════════════════
# 2 — THE SOFT-LOCK
# ══════════════════════════════════════════════════════════════════════

def _mailbox_item(mailbox_id=1, dialogue_id=1):
    return {"type": "incoming_proposal", "target_nation": "Saxony",
            "mailbox_id": mailbox_id, "dialogue_id": dialogue_id,
            "turn_created": 1, "context": {"proposal_type": "open_borders"},
            "options": []}


class TestAReadOutNeverBlocksTheLetterBook:

    def test_an_advisory_is_displaced_not_obeyed(self):
        """The measured live state: advisory current, Saxony QUEUED behind
        it, every letter-book answer refused.

        (Build it in that order — `replace()` on a current mailbox item
        destroys it, which is defect 2E, not this one.)"""
        dm = DialogueManager()
        dm.replace({"type": "advisory", "target_nation": "", "options": []})
        dm.push(_mailbox_item(mailbox_id=5, dialogue_id=5))
        assert dm.peek()["type"] == "advisory"

        got = dm.activate_mailbox_item(5)
        assert got is not None, (
            "a Talleyrand read-out must not make routine envoys unanswerable")
        assert got["mailbox_id"] == 5
        assert dm.peek()["type"] == "incoming_proposal"

    @pytest.mark.parametrize("dtype", sorted(DialogueManager.DISPOSABLE_ACTIVE_TYPES))
    def test_every_disposable_type_yields(self, dtype):
        dm = DialogueManager()
        dm.replace({"type": dtype, "options": []})
        dm.push(_mailbox_item(mailbox_id=7, dialogue_id=7))
        assert dm.activate_mailbox_item(7) is not None

    def test_a_staged_draft_is_never_silently_destroyed(self):
        """The other half of the ruling: a half-drafted set of terms is NOT
        disposable, and refusing is the right answer for it."""
        dm = DialogueManager()
        dm.push(_mailbox_item(mailbox_id=3, dialogue_id=3))
        dm.replace({"type": "terms_guidance", "options": [],
                    "context": {"draft": "half-written"}})
        assert dm.activate_mailbox_item(3) is None
        assert dm.peek()["type"] == "terms_guidance"
        assert dm.peek()["context"]["draft"] == "half-written"

    def test_a_stale_mailbox_id_leaves_the_read_out_alone(self):
        """Ordering pin. A first cut discarded the advisory BEFORE looking
        the row up, so a stale id destroyed it for nothing — breaking the
        standing rule that a stale id leaves the active item untouched."""
        dm = DialogueManager()
        dm.replace({"type": "advisory", "options": []})
        assert dm.activate_mailbox_item(999) is None
        assert dm.peek() is not None and dm.peek()["type"] == "advisory"

    def test_an_unclassified_dialogue_is_denied_not_overwritten(self):
        """Anything in no taxonomy set used to fall through and be silently
        overwritten. Several reachable types are unclassified."""
        dm = DialogueManager()
        dm.replace({"type": "some_future_unclassified_type", "options": []})
        dm.push(_mailbox_item(mailbox_id=4, dialogue_id=4))
        assert dm.get_mailbox_count() == 1, (
            "precondition: the letter must really be QUEUED — building this "
            "the other way round has `replace` destroy it, and then the "
            "activation returns None for the wrong reason (caught by the "
            "mutation sweep: this pin was inert)")
        assert dm.activate_mailbox_item(4) is None
        assert dm.peek()["type"] == "some_future_unclassified_type"
        # PAIRED, per the review round: denying and naming must agree. The
        # first cut denied here while `active_blocker_type` returned "" for
        # the same type, so the refusal shipped `activation_blocked: false`
        # and told the player the letter did not exist — over a panel that
        # stayed open on top of the modal.
        assert dm.active_blocker_type() == "some_future_unclassified_type"

    def test_the_real_unclassified_producer_is_named(self):
        """`settlement_scope_replace_confirm` is in no taxonomy set and IS
        produced by `settlement_staging`. It must block, be named as a
        blocker, and have a human name."""
        dm = DialogueManager()
        dm.replace({"type": "settlement_scope_replace_confirm", "options": []})
        dm.push(_mailbox_item(mailbox_id=6, dialogue_id=6))
        assert dm.activate_mailbox_item(6) is None
        assert dm.active_blocker_type() == "settlement_scope_replace_confirm"
        named = dialogue_display_name("settlement_scope_replace_confirm")
        assert "_" not in named and named != "another matter"

    def test_hard_stops_still_refuse(self):
        dm = DialogueManager()
        dm.push(_mailbox_item(mailbox_id=2, dialogue_id=2))
        dm.replace({"type": "commitment_paradox", "options": []})
        assert dm.activate_mailbox_item(2) is None


class TestTheRefusalNamesWhatIsInTheWay:

    def test_the_blocker_is_reported_by_type(self):
        dm = DialogueManager()
        dm.replace({"type": "terms_guidance", "options": []})
        assert dm.active_blocker_type() == "terms_guidance"

    def test_a_read_out_is_not_a_blocker(self):
        dm = DialogueManager()
        dm.replace({"type": "advisory", "options": []})
        assert dm.active_blocker_type() == ""

    def test_an_empty_slot_is_not_a_blocker(self):
        assert DialogueManager().active_blocker_type() == ""

    def test_every_blocking_type_has_a_human_name(self):
        blocking = (DialogueManager.HARD_STOP_TYPES
                    | DialogueManager.HYBRID_SOFT_STOP_TYPES
                    | DialogueManager.LOCAL_PLANNING_TYPES)
        missing = sorted(t for t in blocking if t not in DIALOGUE_TYPE_DISPLAY)
        assert not missing, (
            "a refusal would name these by their internal key, or fall back "
            "to 'another matter' — the exact unactionable copy this fixes: "
            + ", ".join(missing))

    def test_the_fallback_is_not_a_raw_key(self):
        assert "_" not in dialogue_display_name("something_unmapped")


class TestTheClientStopsCoveringTheMatterItNames:
    """The panel is CanvasLayer 119; the dialogue modals are 110."""

    def test_both_refusal_paths_hide_the_panel_when_blocked(self):
        src = _script("main.gd")
        for fn in ("_on_mailbox_row_action_result", "_on_mailbox_activate_result"):
            body = src[src.index("func %s(" % fn):]
            body = body[:body.index("\nfunc ")]
            assert 'response.get("activation_blocked", false)' in body, fn
            assert "mailbox_panel.hide()" in body, fn

    def test_control_is_handed_back_on_EVERY_activation_failure(self):
        """`api_client` synthesises `{success: false}` for a timeout, a
        connection failure, a JSON parse error and any non-200 — none of them
        carry `activation_blocked`. With the hand-back nested inside that
        branch, a backend hiccup left the command line, Send, End Turn and
        Diplomacy all disabled with nothing on screen, recoverable only by
        F1 (review round, 4b09e59)."""
        src = _script("main.gd")
        body = src[src.index("func _on_mailbox_activate_result("):]
        body = body[:body.index("\nfunc ")]
        fail = body[body.index('if not response.get("success", false):'):]
        hand_back = fail.index("set_input_enabled(true)")
        blocked = fail.index('if response.get("activation_blocked"')
        assert hand_back < blocked, (
            "the hand-back must not be nested inside the blocked-only branch")


class TestTheLapseWarningStaysVisibleWhileItIsArmed:

    def test_reviewing_envoys_keeps_the_prompt_up(self):
        """The one place the confirmation was armed and its indicator hidden:
        close the panel — which grab-focuses the command line — and a single
        Enter lapsed every unanswered envoy with nothing on screen saying a
        confirmation was pending."""
        src = _script("main.gd")
        body = src[src.index("func _on_envoy_clicked():"):]
        body = body[:body.index("\nfunc ")]
        assert "if not _awaiting_end_turn_confirmation:" in body, (
            "armed-and-visible must be one state")
        idx = body.index("if not _awaiting_end_turn_confirmation:")
        after = body[idx:]
        assert "_set_open_envoys_prompt_visible(false)" in \
            after[:after.index("\n\t_dismissed_proposal_nation")], (
            "the guard must be the one wrapping the prompt-hide")


class TestTypedEndTurnCanActuallyConfirmTheLapse:
    """The user's literal sentence. The lapse warning tells the player to
    "type end turn again to confirm" — and that was the one route that could
    not work, because the latch was cleared on the line above the dispatch."""

    def _execute_command_body(self):
        src = _script("main.gd")
        body = src[src.index("func _execute_command():"):]
        return body[:body.index("\nfunc ")]

    # The FUNCTION-level clear is indented with exactly one tab; the one
    # inside `if command.is_empty():` sits three tabs deep and is legitimate
    # (that branch confirms the lapse on a bare Enter).
    _FN_LEVEL_CLEAR = "\n\t_awaiting_end_turn_confirmation = false"

    def test_the_latch_is_not_cleared_before_the_end_turn_dispatch(self):
        body = self._execute_command_body()
        dispatch = body.index('if command.to_lower() == "end turn":')
        assert self._FN_LEVEL_CLEAR not in body[:dispatch], (
            "clearing the latch above the dispatch makes the typed "
            "confirmation route structurally impossible")

    def test_an_unrelated_command_still_drops_the_latch(self):
        """Anchored to REACHABILITY, not to "appears somewhere below".

        The first version asserted only that the clear existed after the
        dispatch index — so moving it beneath the redemption return and the
        Cabinet-redirect return kept the pin green while every redirected
        sentence left the latch armed (review round, 4b09e59)."""
        body = self._execute_command_body()
        after = body[body.index('if command.to_lower() == "end turn":'):]
        # skip the dispatch branch's own return
        rest = after[after.index("return") + len("return"):]
        clear = rest.find(self._FN_LEVEL_CLEAR)
        assert clear != -1, "the latch is never dropped for other commands"
        next_return = rest.find("\n\t\treturn")
        assert next_return == -1 or clear < next_return, (
            "the latch clear sits below an early return, so a redirected or "
            "recovered command leaves the confirmation armed")

    def test_a_bare_enter_still_confirms(self):
        """The empty-command branch is the OTHER route the warning names, and
        it legitimately consumes the latch."""
        body = self._execute_command_body()
        empty = body[body.index("if command.is_empty():"):]
        empty = empty[:empty.index("\n\t\treturn")]
        assert "_awaiting_end_turn_confirmation = false" in empty
        assert "_send_end_turn()" in empty

    def test_reviewing_the_envoys_does_not_reset_the_confirmation(self):
        """The warning's FIRST instruction is "Click Open Envoys to review
        now" — following it used to reset the latch and send the player back
        to the warning."""
        src = _script("main.gd")
        body = src[src.index("func _on_envoy_clicked():"):]
        body = body[:body.index("\nfunc ")]
        assert "_awaiting_end_turn_confirmation = false" not in body


class TestAskingTalleyrandNeverLosesALetter:

    def test_the_advisory_preempts_rather_than_replaces(self):
        """`replace()` destroyed whatever held the active slot. Reproduced:
        envoy active -> ask for counsel -> envoy gone, mailbox count 0."""
        with open(os.path.join(REPO_ROOT, "backend", "commands",
                               "diplomatic_executor.py"), encoding="utf-8") as fh:
            src = fh.read()
        body = src[src.index("advisory_type = detect_advisory_type("):]
        body = body[:body.index("return {")]
        assert "dialogue_manager.preempt(dialogue)" in body
        assert "dialogue_manager.replace(dialogue)" not in body

    def test_an_active_envoy_survives_a_preempt(self):
        dm = DialogueManager()
        dm.push(_mailbox_item(mailbox_id=9, dialogue_id=9))
        before = dm.get_mailbox_count()
        dm.preempt({"type": "advisory", "options": []})
        assert dm.get_mailbox_count() == before, "the letter was lost"

    def test_every_player_initiated_readout_preempts(self):
        """The review round found the first fix applied to the ADVISORY only,
        while `feasibility` — whose type this very commit made disposable —
        and both `mission` arms still destroyed the letter they displaced.

        Scoped deliberately: the many `replace(` calls in this file that
        advance a WIZARD to its next step are correct and must not be swept
        up. This pins the three entry points that create a fresh dialogue
        while something else may hold the slot."""
        with open(os.path.join(REPO_ROOT, "backend", "commands",
                               "diplomatic_executor.py"), encoding="utf-8") as fh:
            src = fh.read()
        for verb in ("_execute_diplomatic_advisory",
                     "_execute_diplomatic_feasibility",
                     "_execute_diplomatic_mission"):
            body = src[src.index("def %s(" % verb):]
            body = body[:body.index("\n    def ")]
            assert "dialogue_manager.replace(dialogue)" not in body, (
                "%s still destroys the dialogue it displaces" % verb)
            assert "dialogue_manager.preempt(dialogue)" in body, verb


# ══════════════════════════════════════════════════════════════════════
# 3 — THE REWARD RAIL
# ══════════════════════════════════════════════════════════════════════

def _europe_world():
    world = WorldState.from_scenario(
        os.path.join(GODOT, "assets", "maps", "europe_1805.json"))
    world.current_turn = 10
    return world


def _ney(world):
    return world.marshals["Ney"]


class TestPayingRetiresTheAsking:

    def test_the_dismisser_is_shared_not_copied(self):
        """It used to be a closure inside the once-per-turn pass, which is
        exactly why paying mid-turn changed nothing."""
        assert callable(dotation.dismiss_reward_notices)
        assert callable(dotation.post_expectation_notice)
        assert callable(dotation.post_erosion_notice)
        with open(os.path.join(REPO_ROOT, "backend", "models",
                               "world_state.py"), encoding="utf-8") as fh:
            src = fh.read()
        assert "dismiss_reward_notices as _dismiss_reward_notices_impl" in src

    def test_the_dismissal_is_per_marshal(self):
        """An unfiltered dismiss would clear everyone else's live grievance."""
        world = _europe_world()
        ney, davout = _ney(world), world.marshals["Davout"]
        ney.battles_won = davout.battles_won = 2
        world._dotation_processed_turn = None
        world._process_dotation_state()

        def rows(name):
            return [n for n in world.notifications.get_pending()
                    if n.get("details", {}).get("marshal") == name
                    and n["type"] == "dotation_expectation"]

        assert rows("Ney") and rows("Davout")
        dotation.dismiss_reward_notices(world, ney)
        assert not rows("Ney")
        assert rows("Davout"), "Davout's grievance is not Ney's to settle"


class TestTheDismissalIsWiredAtEverySeamAndOnlyWhenSettled:
    """The review round mutated all three non-pension seams to `pass`
    simultaneously and the FULL suite stayed green — only `grant_pension` was
    bound. It also showed the dismissal firing on any success, so endowing a
    0g war-torn province silenced a HIGH alarm that was still true."""

    def _rows(self, world, name="Ney"):
        return [n for n in world.notifications.get_pending()
                if n.get("details", {}).get("marshal") == name]

    def _owed(self, world, wins=2):
        ney = _ney(world)
        ney.battles_won = wins
        world._dotation_processed_turn = None
        world._process_dotation_state()
        assert self._rows(world), "precondition: a row is up"
        return ney

    def test_an_estate_that_settles_him_retires_the_row(self):
        from backend.commands.executor import CommandExecutor

        world = _europe_world()
        ney = self._owed(world, wins=1)           # expectation 40
        region = next(r for r in world.regions.values()
                      if r.controller not in ("France", None)
                      and not r.is_capital and r.income_value >= 100)
        region.controller = "France"
        region.stability = 90
        region.war_damage = 0.0

        CommandExecutor().execute(
            {"command": {"action": "grant_dotation", "marshal": "Ney",
                         "target": region.name}}, {"world": world})
        if dotation.get_shortfall(ney, world) <= 0:
            assert self._rows(world) == [], (
                "an endowment that settles the debt must retire the row in "
                "the same call")

    def test_a_partial_payment_does_NOT_silence_the_still_true_alarm(self):
        """Endowing a 0g war-torn province, or granting a token rente, leaves
        the shortfall open — so the row must survive the SAME CALL. Asserted
        immediately, with no reconciliation afterwards: re-running the pass
        re-posts the row and masks the defect (round-2 sweep caught that)."""
        from backend.commands.executor import CommandExecutor

        world = _europe_world()
        ney = self._owed(world, wins=5)           # expectation 200
        region = next(r for r in world.regions.values()
                      if r.controller not in ("France", None)
                      and not r.is_capital)
        region.controller = "France"
        region.war_damage = 1.0                   # yields nothing
        region.stability = 0

        CommandExecutor().execute(
            {"command": {"action": "grant_dotation", "marshal": "Ney",
                         "target": region.name}}, {"world": world})

        assert dotation.get_shortfall(ney, world) > 0, "still owed"
        assert self._rows(world), (
            "an endowment that settles nothing must not retire a warning "
            "that is still true — trust goes on falling behind an empty tray")

    def test_a_RENTE_that_leaves_a_gap_leaves_the_row(self):
        """The pension seam has its own gate and needs its own pin.

        The reachable partial-payment case is the disrupted estate, which is
        also the one the review named: `compute_rente_face` deliberately
        IGNORES EC-W1 disruption (so a transient occupation cannot lock an
        oversized pension), while `get_satisfaction` counts it. Measured:
        expectation 200, a 150g estate with a hostile army standing on it, so
        the rente is sized at 50 and he is still 150g/turn short after being
        "paid"."""
        from backend.commands.executor import CommandExecutor

        world = _europe_world()
        ney = self._owed(world, wins=5)           # expectation 200
        region = next(r for r in world.regions.values()
                      if r.controller not in ("France", None)
                      and not r.is_capital and r.income_value >= 120)
        region.controller = "France"
        region.stability = 95
        region.war_damage = 0.0
        ney.dotation_regions = [region.name]
        foe = next(m for m in world.marshals.values()
                   if m.nation != "France" and m.strength >= 1000
                   and world.get_diplomatic_state("France", m.nation) == "WAR")
        foe.location = region.name
        assert region.name in world.get_disrupted_regions(), "setup"

        result = CommandExecutor().execute(
            {"command": {"action": "grant_pension", "marshal": "Ney"}},
            {"world": world})
        assert result.get("success") is True, result.get("message")
        assert dotation.get_shortfall(ney, world) > 0, (
            "setup: the rente must NOT have closed the gap")
        assert self._rows(world), (
            "a rente that does not close the gap must leave the row up — "
            "silencing it hides an erosion that goes on running")

    def test_revoking_into_an_open_shortfall_does_not_silence_it(self):
        from backend.commands.executor import CommandExecutor

        world = _europe_world()
        ney = self._owed(world, wins=5)           # expectation 200
        ney.pension = 200                         # fully met by paper
        world._dotation_processed_turn = None
        world._process_dotation_state()
        assert self._rows(world) == [], "precondition: met, so the rail is clear"
        # Put a row back, so there is something for a wrong dismissal to eat.
        dotation.post_expectation_notice(world, ney, 200, 200, 0, 2)
        assert self._rows(world)

        CommandExecutor().execute(
            {"command": {"action": "revoke_pension", "marshal": "Ney"}},
            {"world": world})
        assert ney.pension == 0
        assert dotation.get_shortfall(ney, world) > 0
        assert self._rows(world), (
            "revoking INTO a reopened shortfall must not retire the very "
            "warning the same response gives")
    def test_the_fontainebleau_concede_arm_retires_what_it_pays(self):
        """UX23-A (Aug 23, 2026): both string anchors moved.

        The arm used to read `if get_shortfall(...) <= 0:
        dismiss_reward_notices(...)`. Both halves now live inside
        `dotation.restate_reward_notice`, which retires on that same gate and
        otherwise re-quotes the standing row in place — a superset, and one
        implementation instead of the rule copied into four seams (GR1). The
        claim is unchanged; only the name it looks for has moved.
        """
        with open(os.path.join(REPO_ROOT, "backend", "game_logic",
                               "jealousy.py"), encoding="utf-8") as fh:
            src = fh.read()
        arm = src[src.index('if choice == "concede":'):]
        arm = arm[:arm.index("if granted:")]
        assert "restate_reward_notice" in arm, (
            "the collective petition pays rentes and must retire the rows it "
            "settles")

    def test_the_fontainebleau_concede_arm_retires_what_it_pays_FOR_REAL(self):
        """The behavioural half, which a source-string pin never gave.

        Added with UX23-A because the string pin above was the only thing
        binding this seam, and it would have survived the call being deleted
        and re-added anywhere in the arm."""
        from backend.game_logic.jealousy import _apply_fontainebleau_choice

        world = _europe_world()
        ney = _ney(world)
        ney.battles_won = 2
        world._dotation_processed_turn = None
        world._process_dotation_state()
        assert self._rows(world), "precondition: he is asking"

        _apply_fontainebleau_choice(world, "concede", {"marshals": ["Ney"]})

        assert ney.pension > 0, "precondition: the concession paid him"
        assert dotation.get_shortfall(ney, world) <= 0, (
            "precondition: and it settled him in full")
        assert self._rows(world) == [], (
            "the collective petition paid him and the rail went on asking")

    def test_a_dead_marshal_takes_his_grievance_with_him(self):
        """The per-turn pass iterates `world.marshals`, so once he is out of
        it NOTHING can retire his rows — and this slice made them clickable."""
        world = _europe_world()
        ney = self._owed(world, wins=5)
        world.destroy_marshal(ney, cause="test")
        assert "Ney" not in world.marshals
        assert self._rows(world) == [], (
            "a fallen marshal's reward rail must not outlive him")



class TestTheRenteButtonCannotOfferWhatTheExecutorRefuses:
    """One predicate — `dotation.rente_would_change` — read by the executor,
    the card payload and the AI rung. The review found four implementations."""

    def _paid_with_an_estate(self, world):
        ney = _ney(world)
        ney.battles_won = 6                        # expectation 240
        ney.pension = 240
        region = next(r for r in world.regions.values()
                      if r.controller not in ("France", None)
                      and not r.is_capital and r.income_value >= 150)
        region.controller = "France"
        region.stability = 95
        region.war_damage = 0.0
        ney.dotation_regions = [region.name]
        return ney

    def test_an_oversized_rente_may_still_be_re_sized_down(self):
        """He is MET (240 expectation, 240 rente, plus a 150g estate) — but
        the treasury is paying 360g/turn for what 135g/turn now buys. The
        first cut refused this, because `face <= held`."""
        from backend.commands.executor import CommandExecutor

        world = _europe_world()
        ney = self._paid_with_an_estate(world)
        assert dotation.get_satisfaction(ney, world) >= dotation.get_expectation(ney)
        assert dotation.rente_would_change(ney, world) is True

        result = CommandExecutor().execute(
            {"command": {"action": "grant_pension", "marshal": "Ney"}},
            {"world": world})
        assert result.get("success") is True, result.get("message")
        assert ney.pension < 240, "the rente must have been re-sized DOWN"

    def test_a_marshal_who_needs_nothing_is_refused(self):
        from backend.commands.executor import CommandExecutor

        world = _europe_world()
        ney = _ney(world)
        ney.battles_won = 2                        # expectation 80
        ney.pension = 80                           # exactly met, no estates
        assert dotation.rente_would_change(ney, world) is False

        admin_before = world.admin_actions_remaining
        result = CommandExecutor().execute(
            {"command": {"action": "grant_pension", "marshal": "Ney"}},
            {"world": world})
        assert result.get("success") is False
        assert world.admin_actions_remaining == admin_before

    def test_the_card_offers_exactly_what_the_executor_accepts(self):
        from backend.game_logic.marshal_overview import _build_estates

        world = _europe_world()
        ney = _ney(world)
        ney.battles_won = 2
        ney.pension = 80                           # met — nothing to change
        card = _build_estates(ney, world)
        assert card["rente_offer"]["face"] > 0, (
            "the face is positive even though nothing is owed — that gap is "
            "exactly why the button needed a second key")
        assert card["rente_offer"]["would_change"] is False, (
            "the button would offer a re-size the executor then refuses")

        # ...and the converse: an oversized rente the executor WILL re-size
        # must still be offered.
        world2 = _europe_world()
        ney2 = self._paid_with_an_estate(world2)
        card2 = _build_estates(ney2, world2)
        assert card2["rente_offer"]["would_change"] is True


class TestTheRailIsAWayInNotASignpost:

    def test_the_row_carries_a_deep_link_to_the_named_marshal(self):
        world = _europe_world()
        ney = _ney(world)
        ney.battles_won = 2
        world._dotation_processed_turn = None
        world._process_dotation_state()
        row = next(n for n in world.notifications.get_pending()
                   if n["type"] == "dotation_expectation"
                   and n["details"]["marshal"] == "Ney")
        assert row["details"]["review_target"] == "marshal_reward"
        assert row["details"]["route_id"] == "Ney"
        assert row["details"]["review_label"]

    def test_the_client_routes_that_target(self):
        src = _script("main.gd")
        assert 'review_target == "marshal_reward"' in src
        assert "func _open_reward_for_marshal(" in src
        body = src[src.index("func _open_reward_for_marshal("):]
        body = body[:body.index("\nfunc _on_reward_deep_link_overview")]
        assert "get_marshal_overview" in body, (
            "the dialog needs the whole card; build it from the one endpoint "
            "that already makes it, never a second payload")


class TestTheFirstThingTheGameSaysIsTrue:

    def test_it_does_not_offer_an_estate_the_player_cannot_grant(self):
        """France holds ZERO conquered provinces at the 1805 boot, and this
        is the opening line of the whole reward economy."""
        world = _europe_world()
        assert not dotation.list_paying_estates(world, "France"), (
            "precondition: no province is paying an estate at boot")
        ney = _ney(world)
        ney.battles_won = 2
        world._dotation_processed_turn = None
        world._process_dotation_state()
        msg = next(n for n in world.notifications.get_pending()
                   if n["type"] == "dotation_expectation"
                   and n["details"]["marshal"] == "Ney")["message"]
        assert "estate" not in msg.lower()
        assert "duchy" not in msg.lower()

    def test_it_names_an_order_the_player_can_type(self):
        world = _europe_world()
        ney = _ney(world)
        ney.battles_won = 2
        world._dotation_processed_turn = None
        world._process_dotation_state()
        msg = next(n for n in world.notifications.get_pending()
                   if n["type"] == "dotation_expectation"
                   and n["details"]["marshal"] == "Ney")["message"]
        assert '"pension Ney"' in msg
        assert "rente" in msg

    def test_the_quoted_price_is_the_price_the_treasury_pays(self):
        world = _europe_world()
        ney = _ney(world)
        ney.battles_won = 2
        world._dotation_processed_turn = None
        world._process_dotation_state()
        msg = next(n for n in world.notifications.get_pending()
                   if n["type"] == "dotation_expectation"
                   and n["details"]["marshal"] == "Ney")["message"]
        expected = dotation.get_rente_cost(dotation.compute_rente_face(ney, world))
        assert f"{expected}g/turn" in msg


class TestTheNoOpResize:
    """`compute_rente_face` is expectation MINUS ESTATE INCOME and ignores the
    rente already held, so a fully-paid marshal reported a positive face."""

    def test_a_fully_paid_marshal_is_refused_and_charged_nothing(self):
        from backend.commands.executor import CommandExecutor

        world = _europe_world()
        ney = _ney(world)
        ney.battles_won = 2                 # expectation 80
        ney.pension = dotation.get_expectation(ney)   # already met, by rente
        assert dotation.get_shortfall(ney, world) == 0
        assert dotation.compute_rente_face(ney, world) > 0, (
            "precondition: the face is positive even though nothing is owed "
            "— that gap IS the defect")

        admin_before = world.admin_actions_remaining
        result = CommandExecutor().execute(
            {"command": {"action": "grant_pension", "marshal": "Ney"}},
            {"world": world})

        assert result.get("success") is False
        assert "already met" in result.get("message", "")
        assert world.admin_actions_remaining == admin_before, (
            "a no-op must not spend one of the turn's two admin actions")


class TestTheCurveHasOneImplementation:

    def test_the_battle_report_reads_the_shared_curve(self):
        with open(os.path.join(REPO_ROOT, "backend", "commands",
                               "combat_executor.py"), encoding="utf-8") as fh:
            src = fh.read()
        assert "expectation_for_wins(" in src
        assert "min(REP_STEP * _exp_before" not in src, (
            "the curve was re-derived by hand 6,800 lines from its home")

    def test_the_curve_agrees_with_itself(self):
        world = _europe_world()
        ney = _ney(world)
        for wins in (0, 1, 2, 5, 20):
            ney.battles_won = wins
            assert dotation.get_expectation(ney) == \
                dotation.expectation_for_wins(wins)


class TestTheGraceWindow:

    def test_the_retuned_value(self):
        assert dotation.GRACE_TURNS == 4

    def test_erosion_opens_later_than_it_did(self):
        """The measured complaint: on the live board erosion opened on turn 4
        of a 60-turn campaign. It must now take longer than the old window."""
        world = _europe_world()
        ney = _ney(world)
        ney.battles_won = 2
        trust_start = ney.trust.value
        for _ in range(3):              # the OLD window plus one
            world._dotation_processed_turn = None
            world._process_dotation_state()
            world.current_turn += 1
        assert ney.trust.value == trust_start, (
            "trust must still be intact where the old window had already "
            "started eroding it")


class TestTheSuiteDoesNotEatTheDevelopersSaves:
    """Found while diagnosing the live report, and it is why that campaign had
    no recoverable save: `end turn` autosaves, so any test advancing a turn
    through the executor without patching `SAVE_DIR` overwrote the repo's
    `saves/autosave.json` — with a 19-region fixture world. Measured twice on
    full-suite runs against a real 1805 campaign's autosave."""

    def test_save_dir_is_not_the_repo_during_tests(self):
        import backend.save_manager as save_manager

        resolved = os.path.abspath(str(save_manager.SAVE_DIR))
        repo_saves = os.path.abspath(os.path.join(REPO_ROOT, "saves"))
        assert resolved != repo_saves, (
            "the suite is writing into the developer's own saves/ — the "
            "autouse `_isolate_save_dir` fixture in conftest.py is gone or "
            "has been overridden")

    def test_an_autosave_written_now_lands_outside_the_repo(self):
        from backend.save_manager import autosave

        world = WorldState()
        result = autosave(world)
        assert result.get("success") is True, result
        written = os.path.abspath(str(result.get("filepath", "")))
        assert os.path.abspath(os.path.join(REPO_ROOT, "saves")) \
            not in written, written


class TestTheRailCanBeClearedOnScreen:

    def test_an_empty_rail_is_still_reported(self):
        """`has_pending()` guarded the key, so when the LAST row cleared the
        client was never told — it renders on `if response.has(...)`, so a
        ghost row stayed on screen."""
        import backend.main as M

        world = _europe_world()
        world.notifications.dismiss_all()
        response = M.build_base_response(world, success=True, message="x")
        assert "notifications" in response
        assert response["notifications"] == []
