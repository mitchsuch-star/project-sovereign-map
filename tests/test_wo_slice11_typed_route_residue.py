"""Row WO, slice 11 - the typed-route residue (WO-6, WO-7, WO-20, §2 H-15).

Landing record: docs/WEIRD_OUTCOMES_SPEC.md section 3 slice 11.

Measured on the current tree before a line was written (mock parser, the
legacy fixture world; the /command endpoint over a swapped TestClient):

  WO-6   `no wait, Ney, retreat` -> WAIT (0.8, success); `hold on, Ney,
         retreat` -> HOLD; `stand by, Ney, move to Paris` -> WAIT with the
         destination attached. The bare "wait"/"stand by" substring sits
         above retreat/move/... in the elif chain.
  H-15   `end the war on any terms` -> diplomatic_declare_war (the war
         keyword "war on "); `end the war` / `stop the war` / `I want
         peace` / `stop the war with Britain` -> "Unknown action".
  WO-20  `break the alliance with Austria` -> "Unknown action" bare, and
         a PROPOSAL of alliance when addressed to Talleyrand; `break the
         treaty with Austria` (articled) as unparseable as the alliance.
  WO-7   with an envoy's letter (a soft-stop `incoming_proposal`) pending:
         `Ney, never attack Blucher` got the executor's generic shrug
         instead of PARSE-NEG's refusal, and a bare `move to Belgium`
         MARCHED A MARSHAL without the CR-2 "Which marshal?" question -
         the soft-stop pass-through called `executor.execute` directly.

BUILT: the leading filler is BLANKED (same length, PARSE-NEG's rule) before
the keyword match rather than the wait branch being demoted - demoting it
would make `Ney, wait for reinforcements` a SUPPORT order (pinned below as
the negative control); one peace-intent predicate routes to diplomacy
before the war keywords and the declare-war arm yields to it; one
treaty-break predicate at the routing AND the action chain; and the
soft-stop pass-through falls into the ordinary road (recovery arms,
marshal-choice question, then the executor) - the dialogue takes the line
only when it claims it.

Every test names the mutation that kills it.
"""

import contextlib
import io

import pytest
from fastapi.testclient import TestClient

from backend.ai.llm_client import (
    _mentions_peace_intent,
    _mentions_treaty_break,
    strip_leading_filler,
)
from backend.commands.executor import CommandExecutor
from backend.commands.parser import CommandParser
from backend.models.world_state import WorldState


def _quiet(fn, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*args, **kwargs)


@pytest.fixture(scope="module")
def parser():
    return _quiet(CommandParser, use_real_llm=False)


def _world():
    return _quiet(WorldState, player_nation="France")


def _parse(parser, text, world=None):
    world = world or _world()
    return _quiet(parser.parse, text, {"world": world}, world=world)


def _cmd(parsed):
    return parsed.get("command") or {}


def _diplo(parsed):
    return _cmd(parsed).get("diplomatic_data") or {}


# ══════════════════════════════════════════════════════════════════
# 1. WO-6 - the leading filler no longer outranks the verb
# ══════════════════════════════════════════════════════════════════

class TestWO6TheLeadingFiller:

    @pytest.mark.parametrize("text,action,marshal,target", [
        ("no wait, Ney, retreat", "retreat", "Ney", None),
        ("wait, Ney, retreat", "retreat", "Ney", None),
        ("Wait — Ney, retreat", "retreat", "Ney", None),
        ("hold on, Ney, retreat", "retreat", "Ney", None),
        ("stand by, Ney, move to Paris", "move", "Ney", "Paris"),
        ("actually, Ney, fortify", "fortify", "Ney", None),
        ("wait, hold position", "hold", None, None),
    ])
    def test_the_verb_after_the_filler_is_the_order(self, parser, text,
                                                   action, marshal, target):
        """Killed by making `strip_leading_filler` the identity, or by
        deleting its call at the head of the keyword chain."""
        parsed = _parse(parser, text)
        assert parsed["success"] is True, parsed
        assert _cmd(parsed)["action"] == action
        if marshal:
            assert _cmd(parsed)["marshal"] == marshal
        if target:
            assert _cmd(parsed)["target"] == target

    @pytest.mark.parametrize("text", [
        "wait", "wait.", "Ney, wait", "Ney, stand by",
        "Ney, wait for reinforcements", "wait for Davout",
        "Ney, wait until Davout arrives", "wait and drill",
    ])
    def test_a_wait_that_is_the_order_still_waits(self, parser, text):
        """The negative controls - and the reason the wait branch was NOT
        demoted: `wait for reinforcements` carries "reinforce", which would
        win as a SUPPORT order from the bottom of the chain. Killed by
        removing the nothing-follows guard (a bare "wait." becomes an
        unknown order) or by demoting the branch."""
        parsed = _parse(parser, text)
        assert parsed["success"] is True, parsed
        assert _cmd(parsed)["action"] == "wait"

    def test_the_strip_is_same_length_and_blanks_only_the_filler(self):
        """PARSE-NEG's rule: blanked with spaces, never spliced, so every
        position-aware rule downstream still indexes into the text."""
        out = strip_leading_filler("no wait, ney, retreat")
        assert len(out) == len("no wait, ney, retreat")
        assert out.strip() == "ney, retreat"
        assert out.startswith(" " * len("no wait, "))

    @pytest.mark.parametrize("text", [
        "wait", "wait.", "no wait,", "wait for davout", "hold on to the bridge",
        "ney, wait", "waiting for davout, ney holds",
    ])
    def test_the_strip_leaves_a_non_filler_untouched(self, text):
        assert strip_leading_filler(text) == text

    def test_end_to_end_the_marshal_retreats_and_never_waits(self, parser):
        """The done-when: `no wait, Ney, retreat` retreats - never WAITs.
        Driven through the real executor."""
        world = _world()
        ney = world.get_marshal("Ney")
        parsed = _parse(parser, "no wait, Ney, retreat", world)
        assert _cmd(parsed)["action"] == "retreat"
        result = _quiet(CommandExecutor().execute, parsed, {"world": world})
        assert result.get("success") is True, result
        message = (result.get("message") or "").lower()
        assert "retreat" in message
        assert "passes" not in message and "stands by" not in message
        assert getattr(ney, "retreating", False) or ney.location != "Belgium"


# ══════════════════════════════════════════════════════════════════
# 2. §2 H-15 + WO-20 - the mock's diplomatic-tier substring hazards
# ══════════════════════════════════════════════════════════════════

class TestThePeaceOverture:

    @pytest.mark.parametrize("text", [
        "end the war on any terms", "end the war", "stop the war",
        "I want peace", "make peace", "sue for peace",
    ])
    def test_a_nation_less_overture_asks_which_court_and_never_declares(
            self, parser, text):
        """Killed by deleting the peace-intent early route (the sentence
        becomes an unknown order), by dropping the declare-war arm's guard
        (`end the war on any terms` declares), or by dropping the FINAL-21
        `_mentions_peace_intent` arm (it becomes a target-less proposal)."""
        parsed = _parse(parser, text)
        assert parsed["success"] is True, parsed
        assert _cmd(parsed)["action"] == "diplomatic_error"
        assert _cmd(parsed)["action"] != "diplomatic_declare_war"
        assert _diplo(parsed)["action"] == "diplomatic_error"
        assert _diplo(parsed)["error"] == "missing_target_nation"
        assert "which nation" in _diplo(parsed)["message"].lower()

    @pytest.mark.parametrize("text", [
        "end the war with Britain", "stop the war with Britain",
        "Talleyrand, stop the war with Britain", "make peace with Britain",
        # These two carry a WAR keyword ("war on " / "war against ") AND a
        # court, so they pass the FINAL-21 ask and reach the declare-war
        # arm: the only shape whose fate the arm's guard decides. Killed by
        # dropping `not _mentions_peace_intent` from that arm.
        "end the war on Britain's terms", "stop the war against Britain",
    ])
    def test_a_named_overture_is_a_peace_proposal(self, parser, text):
        parsed = _parse(parser, text)
        assert parsed["success"] is True, parsed
        assert _cmd(parsed)["action"] == "diplomatic_proposal"
        assert _diplo(parsed)["proposal_type"] == "peace"
        assert _diplo(parsed)["target_nation"] == "Britain"

    @pytest.mark.parametrize("text,nation", [
        ("declare war on Prussia", "Prussia"),
        ("go to war with Britain", "Britain"),
        ("war on Austria", "Austria"),
    ])
    def test_a_declaration_still_declares(self, parser, text, nation):
        """The guard is the peace PREDICATE, not the word "war"."""
        parsed = _parse(parser, text)
        assert _cmd(parsed)["action"] == "diplomatic_declare_war"
        assert _diplo(parsed)["target_nation"] == nation

    @pytest.mark.parametrize("text", [
        "Ney, end the war of attrition",
        "Ney, stop the war",
        "Ney, halt the war machine",
        "Ney, make peace impossible",
        "Ney, sue for peace",
        "Davout, end the siege",
        "Ney, break the alliance with Austria",   # the treaty-break route
        "Davout, end the alliance",
    ])
    def test_a_marshal_addressed_order_is_never_hijacked_to_diplomacy(
            self, parser, text):
        """Review round: the peace-intent / treaty-break / proposal routes
        fire on keyword presence BEFORE marshal parsing, so a marshal order
        carrying a war/peace word was hijacked to the "which court?" picker
        (`Ney, make peace impossible` — an aggressive 'give no quarter'
        order — answered by an offer to sue for peace). A command that
        LEADS with a player marshal's name never routes to diplomacy.
        Killed by dropping the `_addressed_marshal` guard from any of the
        three routes."""
        parsed = _parse(parser, text)
        assert _cmd(parsed).get("action") != "diplomatic_error"
        assert _diplo(parsed).get("action") is None
        # It falls to ordinary marshal parsing — an unparseable one is
        # Berthier's honest shrug (never a diplomatic proposal).
        assert (parsed.get("success") is False
                or _cmd(parsed).get("marshal") is not None)

    def test_the_leading_address_guard_reads_the_roster(self):
        from backend.ai.llm_client import _leads_with_marshal
        roster = ["Ney", "Davout", "Grouchy", "Drouot"]
        assert _leads_with_marshal("ney, end the war", roster)
        assert _leads_with_marshal("marshal davout, end the war", roster)
        assert not _leads_with_marshal("end the war", roster)
        assert not _leads_with_marshal("talleyrand, end the war", roster)
        # A bare marshal name with no comma is not a leading ADDRESS.
        assert not _leads_with_marshal("end the war for ney", roster)
        # ...and a marshal name AFTER the comma is not the address either —
        # only the segment BEFORE the first comma is the address (kills a
        # matcher that scans the whole string).
        assert not _leads_with_marshal("end the war, ney", roster)

    def test_the_predicate_reads_war_and_hostilities_but_not_fighting(self):
        """`Ney, stop the fighting` is an order to a marshal (PARSE-NEG's
        stand-down), not a peace overture."""
        assert _mentions_peace_intent("end the war on any terms")
        assert _mentions_peace_intent("cease hostilities")
        assert _mentions_peace_intent("i want peace")
        assert not _mentions_peace_intent("ney, stop the fighting")
        assert not _mentions_peace_intent("declare war on prussia")


class TestWO20TheTreatyBreak:

    @pytest.mark.parametrize("text", [
        "break the alliance with Austria",
        "Talleyrand, break the alliance with Austria",
        "end the alliance with Austria",
        "break the treaty with Austria",
        "leave the alliance with Austria",
        "break our alliance with Austria",
        "break treaty with Austria",
    ])
    def test_every_break_form_breaks(self, parser, text):
        """Killed by dropping `_mentions_treaty_break` from the routing
        (the bare forms become unknown orders) or from the action chain
        (the Talleyrand-addressed form PROPOSES the alliance again)."""
        parsed = _parse(parser, text)
        assert parsed["success"] is True, parsed
        assert _cmd(parsed)["action"] == "diplomatic_break"
        assert _cmd(parsed)["action"] != "diplomatic_proposal"
        assert _diplo(parsed)["target_nation"] == "Austria"

    @pytest.mark.parametrize("text,action", [
        ("propose alliance with Austria", "diplomatic_proposal"),
        ("form an alliance with Austria", "diplomatic_proposal"),
        # "withdraw from" is the DOWNGRADE family's verb and stays out of
        # the break predicate (the bare form never routed to diplomacy -
        # the routing list has no "withdraw from" - so the addressed form
        # is the one that exercises the action chain).
        ("Talleyrand, withdraw from the alliance with Austria",
         "diplomatic_downgrade"),
    ])
    def test_the_neighbouring_verbs_keep_their_arms(self, parser, text, action):
        parsed = _parse(parser, text)
        assert _cmd(parsed)["action"] == action

    def test_break_through_enemy_lines_is_not_diplomacy(self, parser):
        parsed = _parse(parser, "Ney, break through enemy lines")
        assert _cmd(parsed).get("action") != "diplomatic_break"

    def test_the_predicate_needs_a_treaty_noun(self):
        assert _mentions_treaty_break("break the alliance with austria")
        assert _mentions_treaty_break("tear up the treaty")
        assert not _mentions_treaty_break("end the war")
        assert not _mentions_treaty_break("break through enemy lines")
        assert not _mentions_treaty_break("withdraw from the alliance")


# ══════════════════════════════════════════════════════════════════
# 3. WO-7 - a pending soft-stop no longer walls off the recovery arms
# ══════════════════════════════════════════════════════════════════

def _letter(nation="Prussia"):
    """A soft-stop mailbox dialogue shaped like `build_ai_proposal_dialogue`'s
    output (the IGR-F idiom), with the options a letter really carries."""
    return {
        "type": "incoming_proposal",
        "target_nation": nation,
        "talleyrand_text": "",
        "options": [{"label": "Accept", "action": "accept"},
                    {"label": "Decline", "action": "reject"}],
        "context": {"proposal": {"type": "open_borders"},
                    "source_nation": nation, "acceptance_score": 0,
                    "decision_reason": "hegemony_pressure",
                    "proposal_type": "open_borders"},
        "turn_created": 1,
        "blocking": False,
        "popup_payload": {"from_nation": nation, "proposal_type": "open_borders",
                          "diplomat_line": f"{nation} speaks.",
                          "clauses": ["Clause: Open borders"],
                          "acceptance_hint": "", "diplomat_name": "an envoy"},
    }


@pytest.fixture
def swapped():
    """A mock-parser TestClient over a world THIS test owns (the slice-15
    idiom - swap the module world, game_state and parser singleton or the
    request silently runs against the developer's live world)."""
    import backend.main as m

    saved = (m.parser, m.world, m.game_state)
    m.parser = _quiet(CommandParser, use_real_llm=False)
    m.world = _world()
    m.game_state = {"world": m.world}
    try:
        yield TestClient(m.app), m
    finally:
        m.parser, m.world, m.game_state = saved


def _post(client, text):
    with contextlib.redirect_stdout(io.StringIO()):
        return client.post("/command", json={"command": text}).json()


def _with_letter(m):
    m.world.dialogue_manager.push(_letter())
    assert m.world.pending_diplomatic_dialogue is not None
    assert not m.world.dialogue_manager.is_hard_stop()


class TestWO7TheSoftStopWall:

    def test_parse_negs_refusal_survives_a_pending_letter(self, swapped):
        """Killed by restoring the bare `executor.execute` pass-through
        (the response becomes the executor's generic shrug)."""
        client, m = swapped
        _with_letter(m)
        resp = _post(client, "Ney, never attack Blucher")
        assert resp["success"] is False
        assert "Then no order goes out" in resp["message"]
        # ...and the letter is still waiting - the line was not an answer.
        assert m.world.pending_diplomatic_dialogue is not None

    def test_the_marshal_choice_question_survives_a_pending_letter(self, swapped):
        """The measured worst case: a bare `move to Belgium` marched a
        marshal without asking. Now it asks, and nobody moves."""
        client, m = swapped
        _with_letter(m)
        davout = m.world.get_marshal("Davout")
        before = davout.location
        resp = _post(client, "move to Belgium")
        assert resp.get("state") == "awaiting_clarification", resp
        assert "Which marshal" in resp["message"]
        assert davout.location == before

    def test_the_unknown_name_question_survives_a_pending_letter(self, swapped):
        """CR-2's did-you-mean, reached from behind the letter exactly as
        it is reached with nothing pending (parity, not a fixed string)."""
        client, m = swapped
        bare = _post(client, "Soult, attack Blucher")
        m.world = _world()
        m.game_state = {"world": m.world}
        _with_letter(m)
        behind = _post(client, "Soult, attack Blucher")
        assert behind["success"] == bare["success"]
        assert behind.get("state") == bare.get("state")
        assert behind["message"][:60] == bare["message"][:60], (
            behind["message"], bare["message"])

    def test_the_enemy_addressee_refusal_survives_a_pending_letter(self, swapped):
        client, m = swapped
        _with_letter(m)
        resp = _post(client, "Blucher, attack Ney")
        assert resp["success"] is False
        assert "does not answer to us" in resp["message"]

    def test_an_ordinary_order_still_passes_through(self, swapped):
        """PL-27's promise, kept: the letter does not block orders."""
        client, m = swapped
        _with_letter(m)
        resp = _post(client, "Ney, hold")
        assert resp["success"] is True, resp
        assert m.world.pending_diplomatic_dialogue is not None

    def test_a_dialogue_word_the_letter_does_not_offer_is_not_denied_a_matter(
            self, swapped):
        """The m1 "no pending diplomatic matter" arm is for NO dialogue.
        With a letter waiting, an unmatched dialogue word takes the
        recovery road instead of denying the letter exists. Killed by
        computing `raw_lower_check` unconditionally."""
        client, m = swapped
        _with_letter(m)
        resp = _post(client, "elaborate")
        assert "no pending diplomatic matter" not in resp["message"].lower()

    def test_a_dialogue_word_with_nothing_pending_still_says_so(self, swapped):
        client, m = swapped
        assert m.world.pending_diplomatic_dialogue is None
        resp = _post(client, "elaborate")
        assert "no pending diplomatic matter" in resp["message"].lower()

    def test_a_hard_stop_still_walls(self, swapped):
        """Untouched by design: a hard stop claims every line."""
        client, m = swapped
        m.world.dialogue_manager.open_flow({
            "type": "war_purpose_selection", "target_nation": "Prussia",
            "message": "Choose your war purpose against Prussia.",
            "objectives": [], "options": [{"label": "Back Out",
                                           "action": "reconsider"}],
            "blocking": True, "turn_created": 1})
        assert m.world.dialogue_manager.is_hard_stop()
        resp = _post(client, "Ney, hold")
        assert resp["success"] is False
        assert "awaits your answer" in resp["message"]

    def test_the_letters_own_answer_still_takes_the_line(self, swapped, monkeypatch):
        """The matched-answer arm is untouched - pinned by routing, not by
        the handler's outcome. Killed by not marking the line as taken
        (the answer would then ALSO fall into the ordinary road and reach
        the executor).

        `accept the offer`, not a bare `accept`: the bare token is consumed
        one block EARLIER by the W6-0 pending-question router (exact tokens
        only), so it never reaches the arm this test pins. The sentence
        form is claimed here, by `match_dialogue_answer`'s label arm."""
        import backend.main as m_mod

        client, m = swapped
        _with_letter(m)
        seen = {}

        def _fake_handler(keyword, game_state, *args, **kwargs):
            seen["keyword"] = keyword
            return {"success": True, "message": "answered"}

        monkeypatch.setattr(m_mod.executor, "handle_diplomatic_dialogue_response",
                            _fake_handler)
        called_executor = {}
        real_execute = m_mod.executor.execute

        def _spy(parsed, game_state):
            called_executor["yes"] = True
            return real_execute(parsed, game_state)

        monkeypatch.setattr(m_mod.executor, "execute", _spy)
        resp = _post(client, "accept the offer")
        assert seen.get("keyword") == "accept"
        assert resp["message"].startswith("answered")
        assert "yes" not in called_executor
