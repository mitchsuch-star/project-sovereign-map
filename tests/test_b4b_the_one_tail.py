"""PC15-10 B4b "The one tail" (Score Mandate Chunk 4, September 27, 2026).

`PETITION_POPUP_REVISIT_SPEC.md` §4 F9: the client's stash-and-raise
discipline, as ONE chokepoint.

Nine surfaces are deferred rather than routed — the backend has already popped
them, or they ride an end-turn response whose route table would swallow the
report — so a response that drops one loses it for good. Each is STASHED the
moment a response arrives and RAISED where control would otherwise return.
The discipline had grown surface by surface: eight stashers called from five
ingests, only two of ~fourteen control-return tails running the full chain,
and four client defects the recon found:

* an objection overridden (or a glorious charge answered) whose attack took a
  province: the backend sent the Plunder/Secure question on that answer
  (`_carry_combat_fields`), and neither handler read a route table — the
  question surfaced only when the player's next order was refused by the
  capture block;
* an interrupt answer whose trust penalty raised a redemption CLEARED the
  interrupt queue — the other marshals' questions were thrown away — and drew
  the dialog straight after the dispatch;
* an end turn that closed with a capture question stashed raised it from
  `_show_pending_dispatch()`, whose callers then ran the control-return tail
  and stacked the tableau / the Proclamation / a hard stop over it;
* a Load kept four of the old campaign's stashes, and its relayed order was
  typed into the new campaign's command line.

Built: `_stash_pending_surfaces(response)` (every stasher; every ingest calls
it before any routing), `_clear_pending_surfaces()` (every stash, on a world
swap), `_raise_pending_surfaces()` (THE raise chain, in one canonical order,
the capture question lifted into it) and `_return_control_to_player()` (the
one tail every control-returning seam ends with). The objection and charge
answers route what they carry through `_post_answer_response_routes` (the
post-HUD table minus the redemption route, which would re-render the result).

The review of the first cut found the chain's modal guard answering TRUE: a
tail that ran while the player had opened the pause menu mid-request would
never hand the command line back. It answers false now — nothing is raised
over an open modal, and control is handed back as before. It also found the
objection, charge and capture answers re-enabling the command line BEFORE
they raised a question (the capture question the new route raises; the
estate stage) — each hands control back through the one tail now.

The pins below are engine-free where the source is the subject and DRIVEN
(`tools/b4b_one_tail_harness.gd`, the real `main.tscn` behind an API stub, on
payloads taken from the real endpoints) where behaviour is. The driven pins
skip without the engine, and a skip is not a pass.
"""

import contextlib
import io
import json
import os
import random
import re
import subprocess

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.commands import executor as executor_mod
from backend.commands.disobedience import DisobedienceSystem
from backend.commands.objection_v2 import ConcernLevel
from backend.game_logic.formations import build_proclamation_card
from tests import _chip_census as C
from tests import _gd_calls as G

REPO = C.REPO
PROJECT = C.PROJECT
HARNESS = REPO / "tools" / "b4b_one_tail_harness.gd"

# The nine deferred surfaces, in the chain's canonical order.
CHAIN_ORDER = [
    "_show_pending_diorama()",
    "_show_pending_ending()",
    "_show_pending_capture_choice()",
    "_show_pending_proclamation()",
    "_show_pending_envoy_digest()",
    "_show_pending_redemption()",
    "_show_pending_deferred_dialogue()",
    "_show_pending_petition()",
    "_process_next_interrupt()",
]

# Every response ingest — a handler that receives a backend response and may
# route it — stashes through the chokepoint BEFORE any routing.
INGESTS = [
    "_on_command_result",
    "_on_objection_response",
    "_on_interrupt_response",
    "_on_glorious_charge_response",
    "_apply_world_swap_response",
]

# The control-return tails `PETITION_POPUP_REVISIT_SPEC.md` §4 F9 names. The
# spec had the world swap CLEAR instead of raise; it clears (the reset), then
# stashes the ARRIVING campaign's surfaces and raises them — a Final save's
# Fall (GE-2) and a standing redemption (WO-41) must still meet the player.
SPEC_TAILS = [
    "_on_command_result", "_on_interrupt_response", "_on_objection_response",
    "_on_capture_choice_response", "_on_glorious_charge_response",
    "_on_redemption_response", "_on_enemy_phase_dismissed",
    "_on_strategic_report_dismissed", "_on_mailbox_panel_closed",
    "_on_battle_diorama_dismissed", "_on_marshal_petition_deferred",
    "_on_proclamation_dismissed", "_process_next_interrupt",
    "_apply_world_swap_response",
]

# The handlers B4b converted: each ends in the one tail and re-enables the
# command line nowhere else.
CONVERTED_TAILS = [
    "_on_battle_diorama_dismissed",
    "_on_marshal_petition_deferred",
    "_on_proclamation_dismissed",
    "_on_mailbox_panel_closed",
    "_on_marshal_audience_fetched",
    "_on_campaign_end_continued",
    "_apply_world_swap_response",
    "_on_glorious_charge_response",
    "_on_capture_choice_response",
]


@pytest.fixture(scope="module")
def src():
    return G.main_gd()


def _stashers(src):
    """Every `_stash_<x>(response...)` in main.gd but the chokepoint itself."""
    return sorted(name for name, (header, _) in G.functions(src).items()
                  if name.startswith("_stash_") and name != "_stash_pending_surfaces"
                  and "response" in header)


# ═══════════════════════════════════════════════════════════════════════════
# The stash: one chokepoint, read by every ingest before any routing
# ═══════════════════════════════════════════════════════════════════════════


class TestTheStashIsOneChokepoint:

    def test_there_are_eight_stashers(self, src):
        """A census, so a ninth surface cannot be added beside the chokepoint."""
        assert _stashers(src) == [
            "_stash_deferred_dialogue", "_stash_diorama", "_stash_ending",
            "_stash_envoy_digest", "_stash_petition", "_stash_proclamation",
            "_stash_redemption", "_stash_relay",
        ]

    def test_the_chokepoint_calls_every_stasher(self, src):
        called = G.calls(src, "_stash_pending_surfaces")
        for name in _stashers(src):
            assert name in called, name

    def test_no_ingest_calls_a_stasher_directly(self, src):
        """The chokepoint is the ONLY caller — save the ending's own two seams
        (GE-2): the game-over handler, which raises the Fall at once, and the
        boot connection test, which adopts a Final save's ending. (The
        ending's response_received connection is a signal hookup, not a
        call.)"""
        allowed = {"_stash_ending": {"_on_campaign_over", "_on_connection_test"}}
        for name in _stashers(src):
            assert "_stash_pending_surfaces" in G.callers(src, name), name
            extra = set(G.callers(src, name)) - {"_stash_pending_surfaces"}
            assert extra <= allowed.get(name, set()), (name, extra)

    @pytest.mark.parametrize("ingest", INGESTS)
    def test_every_ingest_stashes_before_it_routes(self, src, ingest):
        code = G.body(src, ingest)
        assert "_stash_pending_surfaces(response)" in code, ingest
        stash = code.index("_stash_pending_surfaces(response)")
        for marker in ("_route_response_ui(", "_route_capture_choice_response(",
                       "_route_interrupt_response("):
            if marker in code:
                assert stash < code.index(marker), (ingest, marker)
        first_return = re.search(r"^\s*return\b", code, re.M)
        assert first_return is None or stash < first_return.start(), ingest

    def test_every_router_of_a_response_is_an_ingest(self, src):
        """A new handler that routes a response must stash it first — the
        synthetic re-route of a deferred hard stop is the one exception (its
        dialogue WAS the stash)."""
        routers = set(G.callers(src, "_route_response_ui"))
        assert routers - {"_show_pending_deferred_dialogue"} <= set(INGESTS)

    def test_the_world_swap_stashes_after_its_reset(self, src):
        code = G.body(src, "_apply_world_swap_response")
        assert code.index("_reset_frontend_state_for_world_swap(") \
            < code.index("_stash_pending_surfaces(response)")


# ═══════════════════════════════════════════════════════════════════════════
# The raise: one chain, one order
# ═══════════════════════════════════════════════════════════════════════════


class TestTheRaiseIsOneChain:

    def test_the_chain_raises_in_the_canonical_order(self, src):
        chain = G.body(src, "_raise_pending_surfaces")
        positions = [chain.index(raiser) for raiser in CHAIN_ORDER]
        assert positions == sorted(positions)

    def test_the_chain_raises_every_modal_surface(self, src):
        """Every `_show_pending_<x>() -> bool` is in the chain (the dispatch
        is printed, never a modal, and returns nothing)."""
        raisers = sorted(f"{name}()" for name, (header, _) in G.functions(src).items()
                         if name.startswith("_show_pending_") and "-> bool" in header)
        chain = G.body(src, "_raise_pending_surfaces")
        for raiser in raisers:
            assert raiser in chain, raiser
        assert set(raisers) == set(CHAIN_ORDER) - {"_process_next_interrupt()"}

    def test_only_the_chain_raises_a_surface(self, src):
        """The GE-2 end screen raises the ending the moment the war ends
        (the Fall, fetched off the record) — the one direct raise."""
        for raiser in CHAIN_ORDER[:-1]:
            name = raiser[:-2]
            callers = set(G.callers(src, name)) - {"_raise_pending_surfaces"}
            if name == "_show_pending_ending":
                assert callers <= {"_on_campaign_end_received", "_on_campaign_over"}
            else:
                assert not callers, (name, callers)

    def test_nothing_is_raised_over_an_open_modal_and_control_still_returns(self, src):
        """The guard answers FALSE: a modal the player opened while a request
        was in flight (the pause menu, the Cabinet) never calls the tail when
        it closes, so a tail that waited on it would lock the command line."""
        chain = G.body(src, "_raise_pending_surfaces")
        head = [line.strip() for line in chain.split("\n") if line.strip()][:2]
        assert head == ["if _is_modal_dialog_open():", "return false"]

    def test_the_tail_raises_before_it_hands_back(self, src):
        tail = G.body(src, "_return_control_to_player")
        assert re.search(r"if _raise_pending_surfaces\(\):\n\t\treturn\b", tail)
        assert tail.index("_raise_pending_surfaces()") < tail.index("set_input_enabled(true)")

    def test_the_dispatch_raises_nothing(self, src):
        assert "_show_pending_" not in G.body(src, "_show_pending_dispatch")


# ═══════════════════════════════════════════════════════════════════════════
# Every tail is the one tail
# ═══════════════════════════════════════════════════════════════════════════


class TestEveryTailIsTheOneTail:

    @pytest.mark.parametrize("tail", SPEC_TAILS)
    def test_every_tail_the_spec_named_ends_in_the_one_tail(self, src, tail):
        assert "_return_control_to_player()" in G.body(src, tail), tail

    @pytest.mark.parametrize("handler", CONVERTED_TAILS)
    def test_the_handler_hands_back_through_the_tail_only(self, src, handler):
        code = G.body(src, handler)
        assert "_return_control_to_player()" in code, handler
        assert "set_input_enabled(true)" not in code, handler

    def test_the_objection_answer_routes_what_it_carries_on_every_arm(self, src):
        """The defiance arm and the normal flow each route (an attack can take
        a province), then the tail; the disobey arm hands back through it."""
        code = G.body(src, "_on_objection_response")
        assert code.count("_route_response_ui(response, _post_answer_response_routes)") == 2
        assert code.count("_return_control_to_player()") == 3
        assert "set_input_enabled(true)" not in code

    def test_the_charge_answer_routes_what_it_carries(self, src):
        code = G.body(src, "_on_glorious_charge_response")
        assert code.index("_route_response_ui(response, _post_answer_response_routes)") \
            < code.index("_return_control_to_player()")

    def test_the_interrupt_answer_keeps_the_other_questions(self, src):
        code = G.body(src, "_on_interrupt_response")
        assert "interrupt_queue.clear()" not in code
        assert "_route_response_ui(response, _post_answer_response_routes)" in code
        # With questions still queued the chain decides what comes next;
        # with the queue drained, `_process_next_interrupt` closes the flow.
        assert re.search(r"if interrupt_queue\.is_empty\(\):\n\t\t_process_next_interrupt\(\)"
                         r"\n\telse:\n\t\t_return_control_to_player\(\)", code)

    def test_the_answer_table_is_the_post_hud_table_minus_the_redemption(self, src):
        assert re.search(
            r"_post_answer_response_routes = _post_hud_response_routes\.filter\(\n"
            r"\t\tfunc\(route\): return str\(route\.get\(\"id\", \"\"\)\) != \"redemption_event\"\)",
            src)
        # The command road keeps the redemption route: its result has not
        # been rendered yet.
        assert "_route_response_ui(response, _post_hud_response_routes, _render_own_result)" \
            in G.body(src, "_on_command_result")


# ═══════════════════════════════════════════════════════════════════════════
# A world swap clears every stash
# ═══════════════════════════════════════════════════════════════════════════


class TestAWorldSwapClearsEveryStash:

    def test_the_reset_clears_through_the_chokepoint(self, src):
        assert "_clear_pending_surfaces()" in G.body(src, "_reset_frontend_state_for_world_swap")

    def test_every_variable_a_stasher_writes_is_cleared(self, src):
        """A census over the stashers' own assignments, plus the capture
        question the capture route stashes on an end-turn response."""
        written = set()
        for name in _stashers(src) + ["_response_has_capture_choice_route"]:
            for target in re.findall(r"^\s*(_?pending_\w+)\s*=(?!=)", G.body(src, name), re.M):
                written.add(target)
        assert written >= {"pending_proclamation_data", "pending_diorama_data",
                           "pending_redemption_data", "pending_deferred_dialogue",
                           "pending_petition_data", "pending_capture_response",
                           "pending_relay_command", "_pending_envoy_digest_turn"}
        clear = G.body(src, "_clear_pending_surfaces")
        for target in written:
            assert re.search(r"^\s*%s\s*=" % re.escape(target), clear, re.M), target
        assert "pending_ending_queue.clear()" in clear


# ═══════════════════════════════════════════════════════════════════════════
# The client, DRIVEN
# ═══════════════════════════════════════════════════════════════════════════


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


def _post(client, path, body=None):
    response = client.post(path, json=body or {})
    assert response.status_code == 200, (path, response.status_code, response.text[:300])
    return response.json()


def _payloads(mp):
    client = TestClient(M.app)
    with _quiet():
        new_game = _post(client, "/new_game")
    topology = client.get("/map_topology").json()

    # s1/s3/s4 — an objection overridden, and the attack takes a province.
    # EP F3's staging (Archduke John cut to a remnant on Austrian Tyrol, every
    # other Austrian corps two provinces off), with the objection forced at
    # the executor's own evaluation seam so the answer is the backend's.
    M.world.marshals["ArchdukeJohn"].strength = 600
    for m in M.world.marshals.values():
        if m.nation == "Austria" and m.name != "ArchdukeJohn":
            m.location = "Vienna"
            m.strategic_order = None
    mp.setattr(executor_mod, "evaluate_situation", lambda *a, **k: ConcernLevel.STRONG)
    mp.setattr(executor_mod, "apply_mood_variance", lambda concern: concern)
    random.seed(7)
    with _quiet():
        asked = _post(client, "/command", {"command": "Massena, attack Archduke John"})
        insisted = _post(client, "/respond_to_objection", {"choice": "insist"})
        secured = _post(client, "/capture_choice", {"choice": "secure"})

    # s2 — a redemption event from the backend's own checker.
    ney = M.world.marshals["Ney"]
    ney.trust.set(10)
    event = DisobedienceSystem().check_redemption_threshold(ney, M.world)

    # s3/s5 — a Proclamation card from the backend's own builder.
    card = build_proclamation_card(M.world, {
        "nation": "KingdomOfItaly", "old_display_name": "the Kingdom of Italy",
        "display_name": "Italy", "flag_tag": "Italy", "blurb": "",
        "gold": 1500, "created": False, "sponsor": "France",
        "regions_lifted": 3, "stability_bonus": 10, "aggrieved_display": ["Austria"],
        "next_design": "", "turn": int(M.world.current_turn),
    })

    return {
        "topology": topology,
        "asked": asked,
        "objection_capture": insisted,
        "capture_answer": secured,
        "interrupt_redemption": {
            "success": True,
            "message": "Davout holds his ground as ordered.",
            "redemption_event": event,
        },
        # The shape the interrupt popup reads (every key has a default there).
        "second_question": {
            "marshal": "Soult", "interrupt_type": "cannon_fire",
            "message": "Soult hears the guns to the east, Sire.",
            "options": ["march_to_guns", "continue_order"],
        },
        "redemption_answer": {"success": True, "choice": "dismiss",
                              "message": "Ney is relieved of his command."},
        "proclamation": card,
        # The old campaign's stashes — their content is not the subject.
        "old_relay": "Ney, attack Mack",
        "old_petition": {"kind": "jealousy_confrontation", "title": "A GRIEVANCE",
                         "speaker": "Davout", "body": "An old campaign's grievance.",
                         "options": []},
        "new_game": new_game,
    }


@pytest.fixture(scope="module")
def payloads():
    with pytest.MonkeyPatch.context() as mp:
        C.board_env(mp)
        prior = (M.world, M.game_state.get("world"), M.parser)
        try:
            return _payloads(mp)
        finally:
            M.world, M.parser = prior[0], prior[2]
            M.game_state["world"] = prior[1]


class TestThePayloadsAreTheReproduction:

    def test_the_objection_was_asked(self, payloads):
        asked = payloads["asked"]
        assert asked.get("pending_objection") or asked.get("objection"), asked.get("message")

    def test_the_overridden_attack_answers_with_its_capture_question(self, payloads):
        """The backend half of defect (1): the ANSWER carries the question."""
        insisted = payloads["objection_capture"]
        assert insisted["success"] is True, insisted.get("message")
        assert insisted.get("pending_capture_choice") is True
        assert insisted.get("capture_data", {}).get("region")

    def test_the_capture_answer_closes_the_question(self, payloads):
        secured = payloads["capture_answer"]
        assert secured["success"] is True, secured.get("message")
        assert not secured.get("pending_capture_choice")

    def test_the_redemption_event_is_real(self, payloads):
        event = payloads["interrupt_redemption"]["redemption_event"]
        assert event and event.get("marshal") == "Ney"

    def test_the_card_is_the_builders(self, payloads):
        assert payloads["proclamation"]["display_name"] == "Italy"


@pytest.fixture(scope="module")
def driven(payloads, tmp_path_factory):
    exe = C.engine()
    if exe is None:
        pytest.skip("Godot engine not on this machine — the driven pins skip, "
                    "and a skip is not a pass")
    work = tmp_path_factory.mktemp("b4b")
    out = work / "out.json"
    log = work / "godot.log"
    spec = work / "spec.json"
    spec.write_text(json.dumps(dict(payloads, out=str(out))), encoding="utf-8")
    env = dict(os.environ, B4B_SPEC=str(spec))
    proc = subprocess.run(
        [exe, "--headless", "--path", str(PROJECT), "--log-file", str(log),
         "--script", str(HARNESS)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=300, env=env, cwd=str(PROJECT))
    if not out.is_file():
        pytest.fail("the harness wrote no result\n"
                    f"exit={proc.returncode}\nstderr tail:\n{proc.stderr[-2000:]}")
    result = json.loads(out.read_text(encoding="utf-8"))
    assert "error" not in result, result.get("error")
    text = log.read_text(encoding="utf-8", errors="replace") if log.is_file() else ""
    result["script_errors"] = text.count("SCRIPT ERROR")
    return result


class TestTheHarness:

    def test_the_harness_is_in_the_parse_check(self):
        text = (REPO / "tools" / "godot_parse_check.gd").read_text(encoding="utf-8")
        assert "res://../../tools/b4b_one_tail_harness.gd" in text

    def test_the_harness_ran_clean(self, driven):
        assert driven["script_errors"] == 0


class TestTheOverriddenAttackAsksAboutItsTown:
    """s1 — defect (1): the backend sent the question; the client now asks it."""

    def test_the_capture_question_is_raised_before_control_returns(self, driven):
        assert driven["s1_capture_raised"] is True, driven["s1_modals"]

    def test_one_surface_at_a_time(self, driven):
        assert driven["s1_modals_before_control"] == ["capture_choice_dialog"]

    def test_the_command_line_stays_closed_beneath_the_question(self, driven):
        assert driven["s1_input_enabled"] is False


class TestTheRedemptionKeepsTheOtherQuestions:
    """s2 — defect (2): the redemption no longer clears the interrupt queue."""

    def test_the_redemption_is_raised_first(self, driven):
        assert driven["s2_modals"] == ["redemption_dialog"]

    def test_the_second_question_is_kept(self, driven):
        assert driven["s2_queue_after_answer"] == 1

    def test_the_second_question_follows_the_audience(self, driven):
        assert driven["s2_modals_after_redemption"] == ["interrupt_popup"]
        assert driven["s2_queue_after_redemption"] == 0


class TestTheTownIsAskedFirstAndAlone:
    """s3 — defect (3): nothing is stacked over the capture question."""

    def test_the_capture_question_stands_alone(self, driven):
        assert driven["s3_modals"] == ["capture_choice_dialog"]

    def test_the_proclamation_follows_the_answer(self, driven):
        assert driven["s3_modals_after_capture"] == ["proclamation_popup"]

    def test_control_returns_at_the_end(self, driven):
        assert driven["s3_modals_at_end"] == []
        assert driven["s3_input_enabled_at_end"] is True


class TestALoadForgetsTheOldCampaign:
    """s4 — defect (4): the old campaign's stashes do not survive a Load."""

    def test_the_old_relayed_order_is_not_typed_into_the_new_campaign(self, driven):
        assert driven["s4_command_line"] == ""

    def test_the_old_questions_do_not_wait_for_the_next_return(self, driven):
        assert driven["s4_modals"] == []
        assert driven["s4_modals_at_next_return"] == []
        assert driven["s4_input_enabled"] is True


class TestThePauseMenuNeverLocksTheLine:
    """s5 — the review's guard: a tail that runs while the pause menu stands
    raises nothing over it and still hands the command line back."""

    def test_nothing_is_raised_over_the_pause_menu(self, driven):
        assert driven["s5_modals"] == ["pause_menu"]

    def test_the_command_line_comes_back(self, driven):
        assert driven["s5_input_enabled"] is True

    def test_the_stash_waits_for_the_next_return(self, driven):
        assert driven["s5_modals_at_next_return"] == ["proclamation_popup"]


class TestTheEstateQuestionKeepsTheLineClosed:
    """s6 — a capture answer that mounts a SECOND question (the estate stage
    re-asks through the same route) leaves the command line closed beneath
    it: the handler's early re-enable is gone, like the objection's and the
    charge's."""

    def test_the_question_is_asked_again(self, driven):
        assert driven["s6_modals"] == ["capture_choice_dialog"]

    def test_the_command_line_stays_closed(self, driven):
        assert driven["s6_input_enabled"] is False
