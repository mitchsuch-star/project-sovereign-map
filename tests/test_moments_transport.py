"""S14c part 2, first landing — the letters' transport beside a standing
letter (`docs/EVENTS_SPEC.md` §3.4 seams 5, 7, 9; the siblings S14C-X1, X2,
X14 in `docs/BUG_FIXES.md` §S14C).

Reproduced first on the booted 1805 world with the two-turn letter that
exists today — an ally's call to arms (Spain against Portugal): the end-turn
warning counted it as lapsing on its first turn (X1); it locked the wizard
for its whole window (X2 — RULED intended for the call, the hazard named;
a moment letter never locks); an unrelated letter's lapse wiped its rail
notice while it still stood (X14).
"""
import contextlib
import io
import re
from pathlib import Path

import pytest

import backend.main as M
from backend.game_logic import ai_diplomacy as AI
from backend.game_logic import call_to_arms as CTA
from backend.game_logic import moments as MO
from backend.notifications import DIPLOMATIC_PROPOSAL, dismiss_letter_notices
from tests import _chip_census as C
from tests.test_moments_engine import _at, _block, _letter, _tick

REPO = Path(__file__).resolve().parents[1]
BACKEND = REPO / "backend"


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture(autouse=True)
def _restore_active_world():
    prior = (M.world, M.game_state.get("world"), M.parser)
    yield
    M.world = prior[0]
    M.game_state["world"] = prior[1]
    M.parser = prior[2]


@pytest.fixture
def world(monkeypatch):
    C.board_env(monkeypatch)
    return M.world


def _post_call(world):
    """Spain (France's ally) calls France into her war on Portugal."""
    world.diplomatic_states[world._make_diplo_key("Spain", "Portugal")] = "WAR"
    with _quiet():
        letter = CTA.post_call(world, ally="Spain", target="Portugal", callee="France", war_id="")
    assert letter is not None
    return letter


def _push_court_letter(world, court="Sweden"):
    terms = {"type": "open_borders", "proposer_nation": court, "target_nation": "France",
             "demands": [], "sweeteners": []}
    with _quiet():
        dialogue = AI.build_ai_proposal_dialogue(
            AI._make_proposal(court, "open_borders", 3, terms, world), world)
    world.dialogue_manager.push(dialogue)
    return dialogue


def _envoy_titles(world):
    return [n["title"] for n in world.notifications.get_pending() if n["type"] == DIPLOMATIC_PROPOSAL]


class TestX1TheWarningCountsWhatLapses:
    def test_a_kept_letter_is_not_counted_on_its_first_turn(self, world):
        letter = _post_call(world)
        dm = world.dialogue_manager
        turn = int(world.current_turn)
        assert CTA.keeps_open(letter, turn)
        assert dm.get_lapsing_count(turn) == 0          # it stands next turn too
        answer_by = CTA.answer_by_turn(CTA.call_terms_of(letter))
        assert dm.get_lapsing_count(answer_by) == 1     # its last turn: it lapses
        assert dm.get_lapsing_count() == 1              # no turn: the old reading

    def test_the_count_and_the_lapse_ask_one_predicate(self, world):
        _post_call(world)
        _push_court_letter(world)
        dm = world.dialogue_manager
        turn = int(world.current_turn)
        counted = dm.get_lapsing_count(turn)
        lapsed = dm.lapse_pending_offers(current_turn=turn, world=world)
        assert counted == len(lapsed) == 1

    def test_a_moment_letter_is_not_counted_on_its_first_turn(self, world):
        world.moments = MO.from_block(_block())
        _at(world, 8)
        _tick(world)
        dm = world.dialogue_manager
        lapsing = [d for d in [dm.peek()] + list(dm.iter_queue())
                   if d and dm.item_lapses(d, 8)]
        assert not [d for d in lapsing if MO.is_moment_letter(d)]
        assert dm.item_lapses(_letter(world, "bavarian_match"), 9)

    def test_every_endpoint_passes_the_turn(self):
        src = (BACKEND / "main.py").read_text(encoding="utf-8")
        calls = re.findall(r"get_lapsing_count\(([^)]*)\)", src)
        assert len(calls) == 5 and all(c == "int(world.current_turn" for c in calls), calls


class TestX2TheWizardLock:
    """RULED (S14c part 2, under the standing delegation): DDB-2's ruling is
    silent on the wizard; the lock is the offer-lifetime spec's ("avoids the
    obvious exploit where the player can freeze a favorable proposal while
    changing the board state"). For a call to arms the hazard is concrete — a
    wizard act that makes the call moot (`call_status`) dodges its refusal
    price — so the call keeps the lock for its window; a moment letter, the
    Cabinet's with no court to game, never takes it."""

    def test_a_standing_call_keeps_the_lock(self, world):
        from backend.game_logic.diplomacy import get_available_diplomatic_actions
        _post_call(world)
        assert world.dialogue_manager.has_current_turn_offers() is True
        with _quiet():
            assert get_available_diplomatic_actions(world, "Prussia") == []

    def test_a_moment_letter_never_takes_it(self, world):
        from backend.game_logic.diplomacy import get_available_diplomatic_actions
        world.moments = MO.from_block(_block())
        dm = world.dialogue_manager
        while dm.peek() is not None:
            dm.pop()
        dm._queue = []
        _at(world, 8)
        _tick(world)
        assert dm.peek() is not None and MO.is_moment_letter(dm.peek())
        assert dm.has_current_turn_offers() is False
        with _quiet():
            assert get_available_diplomatic_actions(world, "Prussia") != []


class TestX14AStandingLetterKeepsItsRow:
    def test_an_unrelated_lapse_leaves_the_call_s_notice(self, world):
        _post_call(world)
        _push_court_letter(world)
        assert "Call to Arms from Spain" in _envoy_titles(world)
        lapsed = world.dialogue_manager.lapse_pending_offers(
            current_turn=int(world.current_turn), world=world)
        assert [x["nation"] for x in lapsed] == ["Sweden"]
        dismiss_letter_notices(world)
        assert "Call to Arms from Spain" in _envoy_titles(world)

    def test_the_answered_call_s_own_row_goes(self, world):
        letter = _post_call(world)
        dm = world.dialogue_manager
        dm.remove_matching(lambda d: d is letter)        # answered: it no longer stands
        dismiss_letter_notices(world)
        assert "Call to Arms from Spain" not in _envoy_titles(world)

    def test_a_row_with_no_standing_letter_goes_as_it_always_did(self, world):
        from backend.notifications import NotificationPriority, create_notification
        world.notifications.add(create_notification(
            DIPLOMATIC_PROPOSAL, NotificationPriority.HIGH, "Envoy from Sweden", "x",
            int(world.current_turn)))
        dismiss_letter_notices(world)
        assert "Envoy from Sweden" not in _envoy_titles(world)

    def test_a_moment_letter_keeps_its_row_through_another_letter_s_lapse(self, world):
        world.moments = MO.from_block(_block())
        _at(world, 8)
        _tick(world)
        _push_court_letter(world)
        world.dialogue_manager.lapse_pending_offers(current_turn=8, world=world)
        dismiss_letter_notices(world)
        rows = [n for n in world.notifications.get_pending()
                if (n.get("details") or {}).get("moment_id") == "bavarian_match"]
        assert len(rows) == 1

    def test_the_moment_row_opens_its_own_letter(self, world):
        world.moments = MO.from_block(_block())
        _at(world, 8)
        _tick(world)
        letter = _letter(world, "bavarian_match")
        row = next(n for n in world.notifications.get_pending()
                   if (n.get("details") or {}).get("moment_id") == "bavarian_match")
        details = row["details"]
        assert details["review_target"] == "moment_letter"
        assert details["route_id"] == str(letter["mailbox_id"]) and int(details["route_id"]) > 0

    def test_the_call_s_row_carries_its_key(self, world):
        _post_call(world)
        row = next(n for n in world.notifications.get_pending()
                   if n["title"] == "Call to Arms from Spain")
        assert (row["details"]["call_ally"], row["details"]["call_enemy"]) == ("Spain", "Portugal")

    def test_no_site_dismisses_the_envoy_rows_wholesale(self):
        """The census: every former `dismiss_by_type(DIPLOMATIC_PROPOSAL)`
        site routes through the one helper."""
        offenders = []
        for path in BACKEND.rglob("*.py"):
            if path.name == "notifications.py":
                continue
            src = path.read_text(encoding="utf-8")
            if "dismiss_by_type(DIPLOMATIC_PROPOSAL)" in src:
                offenders.append(path.name)
        assert not offenders, offenders
        executor = (BACKEND / "commands" / "diplomatic_executor.py").read_text(encoding="utf-8")
        assert executor.count("dismiss_letter_notices(") >= 16


class TestX23TheAuctionKeepsItsRow:
    """S14C-X23 (found by part 2's sibling sweep of X14): an allegiance
    auction's rail row — its Bid chip — stands the auction's three-turn
    window, and an unrelated answer or lapse wiped it."""

    def test_an_unrelated_lapse_leaves_the_open_auction_s_row(self, world, monkeypatch):
        from backend.game_logic.intent import IntentView

        def fake(nation, w):
            if nation == "Denmark":
                return IntentView(nation=nation, want_id="t", want_title="T",
                                  want_type="acquire_regions", against="Austria",
                                  weight=66, price="bandwagon")
            return IntentView(nation=nation, want_id=None, want_title=None, want_type=None,
                              against=None, weight=0, price="indifferent")

        monkeypatch.setattr("backend.game_logic.intent.get_nation_intent", fake)
        with _quiet():
            AI.process_allegiance_auctions(world)
        assert "Denmark" in world.allegiance_auctions
        title = next(t for t in _envoy_titles(world) if "Denmark" in t)
        _push_court_letter(world)
        world.dialogue_manager.lapse_pending_offers(current_turn=int(world.current_turn), world=world)
        dismiss_letter_notices(world)
        assert title in _envoy_titles(world)
        world.allegiance_auctions.pop("Denmark")            # closed: the row may go
        dismiss_letter_notices(world)
        assert title not in _envoy_titles(world)


class TestThePopupSendsAKeyword:
    """The popup emits the bare words "accept" / "reject" — the router maps
    them onto a moment letter's two actions."""

    @pytest.mark.parametrize("word, answer", [("accept", "accept"), ("reject", "decline")])
    def test_the_bare_word_answers_the_letter(self, world, word, answer):
        from fastapi.testclient import TestClient
        from tests.test_moments_engine import _make_current, _rich
        world.moments = MO.from_block(_block())
        _rich(world)
        _at(world, 8)
        _tick(world)
        letter = _letter(world, "bavarian_match")
        _make_current(world, letter)
        with _quiet():
            result = TestClient(M.app).post("/respond_to_diplomatic_dialogue", json={
                "choice": word, "dialogue_id": letter["dialogue_id"]}).json()
        assert result["success"] is True, result
        assert MO.status_row(world, "bavarian_match")["answer"] == answer
