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
    """{cue: (files[], max_s or None)} straight out of the .gd registry."""
    src = _script("audio_manager.gd")
    body = src[src.index("const CUES := {"):]
    body = body[:body.index("\n}\n")]
    out = {}
    for m in re.finditer(r'^\t"([a-z_]+)": \{(.+)\},?\s*$', body, re.M):
        cue, spec = m.group(1), m.group(2)
        files = re.findall(r'"([a-z_0-9]+/[^"]+)"', spec)
        cap = re.search(r'"max_s":\s*([0-9.]+)', spec)
        out[cue] = (files, float(cap.group(1)) if cap else None)
    return out


# A one-shot fired by a UI interaction has to be over quickly. Anything longer
# is a deliberate ceremony and has to say so here, by name, with its budget.
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
                if measured is None:
                    continue
                effective = min(measured, cap) if cap else measured
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
        body = self._execute_command_body()
        dispatch = body.index('if command.to_lower() == "end turn":')
        assert self._FN_LEVEL_CLEAR in body[dispatch:]

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
