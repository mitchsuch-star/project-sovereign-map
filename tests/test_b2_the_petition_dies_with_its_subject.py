"""PC15-10 B2 — "The petition dies with its subject"
(`docs/PETITION_POPUP_REVISIT_SPEC.md` §4 F2 + F10, §6 Q3 CONFIRMED; Score
Mandate Chunk 4, September 27, 2026).

F2: no numeric TTL. A marshal petition expires when its SUBJECT dies — a
confrontation whose grievance cooled (or whose rung the quarrel has since
climbed past: S7), a rivalry that mended, a Fontainebleau petition every man
of which is now provided for, a war-weary objection overtaken by a war begun
another way, a shadow petition from a man who left the Emperor's side. The
question is asked at every seam that could hand the player a card about
nothing: the per-turn re-push, the ordinary drain, the end-turn key, the
antechamber's GET, the answer and the load. Every retirement is
`retire_petition` and leaves ONE receipt line (`petition_retired`, exempt
from the drama cap). A newer card about the SAME pair supersedes the older
one (its latch kept — subsumed, not withdrawn).

F10: every restored popup slot answers "is this still true?" at load, and
each one retired leaves a receipt (`popup_retired`). PopupQueue's dead
to_dict/from_dict pair is deleted (pinned in test_cooldown_popup_manager).

Levers: `jealousy.THE_PETITION_DIES_WITH_ITS_SUBJECT`,
`jealousy.THE_NEWER_WORD_SUPERSEDES`,
`world_state.THE_LOADED_POPUP_IS_STILL_TRUE`.
"""

import contextlib
import io

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.game_logic import dispatch as D
from backend.game_logic import dotation
from backend.game_logic import jealousy as J
from backend.models.world_state import WorldState
from tests import _chip_census as C


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


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
    w = M.world
    w.authority_tracker.authority = 50
    w.pending_marshal_petition = None
    w._pending_jealousy_turn_events = []
    return w


def _receipts(world, kind=None):
    return [e for e in (getattr(world, "_pending_jealousy_turn_events", []) or [])
            if e.get("type") == "petition_retired"
            and (kind is None or e.get("kind") == kind)]


def _queued(world):
    return world._popup_queue.get("pending_marshal_petition") is not None


def _crisis_confrontation(world, who="Ney", whom="Davout"):
    """A REAL level-2 quarrel: resentment, rung and card agree."""
    ney, dav = world.marshals[who], world.marshals[whom]
    ney.jealous_of = whom
    ney.jealousy_turns_remaining = 5
    J._set_escalation_level(ney, whom, J.ESCALATION_PERMANENT_LEVEL)
    J._set_escalation_level(dav, who, J.ESCALATION_PERMANENT_LEVEL)
    status = J.queue_confrontation_petition(world, ney, dav,
                                            J.ESCALATION_PERMANENT_LEVEL)
    assert status == J.PETITION_QUEUED
    return world.pending_marshal_petition


def _rivalry(world, value=-2, a="Lannes", b="Murat"):
    ma, mb = world.marshals[a], world.marshals[b]
    ma.set_relationship(b, value)
    mb.set_relationship(a, value)
    status = J.queue_rivalry_petition(world, ma, mb, value)
    assert status == J.PETITION_QUEUED
    return world.pending_marshal_petition


def _make_eroding(world, name, steps=3):
    floor = max(dotation.GRACE_TURNS + 3, J.FONTAINEBLEAU_MIN_TURN)
    if world.current_turn < floor:
        world.current_turn = floor
    marshal = world.marshals[name]
    marshal.expectation_steps = steps
    marshal.expectation_grace_turn = world.current_turn - dotation.GRACE_TURNS
    assert dotation.is_eroding(marshal, world)
    return marshal


def _repush(world):
    world._jealousy_processed_turn = None
    with _quiet():
        return J.process_turn(world)


# ═══════════════════════ F2 — ONE PREDICATE PER KIND ═══════════════════════

class TestEachKindDiesWithItsSubject:

    def test_a_standing_crisis_confrontation_stands(self, world):
        card = _crisis_confrontation(world)
        assert J.petition_retirement_reason(card, world) == ""
        _repush(world)
        assert world.pending_marshal_petition is card
        assert not _receipts(world)

    def test_a_cooled_crisis_retires_with_a_receipt(self, world):
        """B1 retired a stale CRISIS in silence; nothing retires silently now."""
        card = _crisis_confrontation(world)
        world.marshals["Ney"].jealous_of = None
        assert J.petition_retirement_reason(card, world) == "cooled"
        _repush(world)
        assert world.pending_marshal_petition is None
        assert not _queued(world)
        lines = _receipts(world, "jealousy_confrontation")
        assert lines and lines[-1]["reason"] == "cooled"
        assert "no longer presses the matter" in lines[-1]["message"]
        assert "Davout" in lines[-1]["message"], "the receipt names the quarrel"

    def test_s7_a_card_a_rung_behind_the_quarrel_never_serves(self, world):
        card = _crisis_confrontation(world)
        J._set_escalation_level(world.marshals["Ney"], "Davout", 3)
        assert J.petition_retirement_reason(card, world) == "moved_on"
        _repush(world)
        assert world.pending_marshal_petition is None
        assert _receipts(world)[-1]["reason"] == "moved_on"

    def test_a_captured_petitioner_cannot_press(self, world):
        card = _crisis_confrontation(world)
        world.marshals["Ney"].captured_by = "Austria"
        assert J.petition_retirement_reason(card, world) == "absent"

    def test_a_rivalry_card_stands_while_the_breach_stands(self, world):
        card = _rivalry(world, -2)
        assert J.petition_retirement_reason(card, world) == ""

    def test_a_mended_rivalry_retires(self, world):
        card = _rivalry(world, -2)
        world.marshals["Lannes"].set_relationship("Murat", 0)
        assert J.petition_retirement_reason(card, world) == "mended"
        _repush(world)
        assert world.pending_marshal_petition is None
        line = _receipts(world, "rivalry_confrontation")[-1]
        assert "has mended" in line["message"] and "Murat" in line["message"]

    def test_a_rivalry_card_reads_the_STORED_value(self, world):
        """S4's rule: a live grievance lowers the DERIVED value by one; the
        card was announced on the stored one and must be judged on it."""
        card = _rivalry(world, -1)
        lannes = world.marshals["Lannes"]
        lannes.set_relationship("Murat", 0)
        lannes.jealous_of = "Murat"          # derived would read -1
        assert J.petition_retirement_reason(card, world) == "mended"

    def test_fontainebleau_stands_while_one_man_still_erodes(self, world):
        men = [_make_eroding(world, n) for n in ("Ney", "Davout", "Murat")]
        assert J.queue_fontainebleau_petition(world, men) == J.PETITION_QUEUED
        card = world.pending_marshal_petition
        for m in men[:2]:
            m.expectation_grace_turn = -1          # provided for
        assert J.petition_retirement_reason(card, world) == ""
        men[2].expectation_grace_turn = -1
        assert J.petition_retirement_reason(card, world) == "provided"
        _repush(world)
        assert world.pending_marshal_petition is None
        assert "provided for" in _receipts(world, "fontainebleau")[-1]["message"]

    def test_war_weary_is_overtaken_by_a_war_begun_another_way(self, world):
        ney = world.marshals["Ney"]
        assert not world.is_at_war("France", "Prussia")
        J.queue_war_weary_petition(world, ney, "Prussia", {"x": 1})
        card = world.pending_marshal_petition
        assert J.petition_retirement_reason(card, world) == ""
        world.diplomatic_states[world._make_diplo_key("France", "Prussia")] = "WAR"
        assert J.petition_retirement_reason(card, world) == "at_war"
        _repush(world)
        assert world.pending_marshal_petition is None
        assert "another road" in _receipts(world, "war_weary")[-1]["message"]

    def test_war_weary_about_a_court_that_is_no_more(self, world, monkeypatch):
        J.queue_war_weary_petition(world, world.marshals["Ney"], "Prussia", {})
        card = world.pending_marshal_petition
        monkeypatch.setattr(type(world), "get_active_nations",
                            lambda self: [n for n in ["France", "Austria"]])
        assert J.petition_retirement_reason(card, world) == "court_gone"

    def test_the_shadow_petition_dies_when_he_leaves_the_emperor(self, world):
        sov = world.marshals["Napoleon"]
        marshal = world.marshals["Soult"]
        marshal.location = sov.location
        assert J.queue_shadow_petition(world, marshal) == J.PETITION_QUEUED
        card = world.pending_marshal_petition
        assert J.petition_retirement_reason(card, world) == ""
        others = [r for r in world.regions if r != sov.location]
        marshal.location = others[0]
        assert J.petition_retirement_reason(card, world) == "no_shadow"


# ═══════════════════════ SUPERSEDE (F1 item 5) ═════════════════════════════

class TestTheNewerWordSupersedes:

    def test_the_same_pair_replaces_and_keeps_the_older_latch(self, world):
        ney = world.marshals["Ney"]
        ney.jealous_of = "Davout"
        ney.jealousy_turns_remaining = 5
        J._set_escalation_level(ney, "Davout", 1)
        J.queue_confrontation_petition(world, ney, world.marshals["Davout"], 1)
        older = world.pending_marshal_petition
        assert older["tier"] == "audience"
        seen_key = f"{J._pair_key('Ney', 'Davout')}@L1"
        world.jealousy_confrontations_seen = [seen_key]
        J._set_escalation_level(ney, "Davout", 2)
        J.queue_confrontation_petition(world, ney, world.marshals["Davout"], 2)
        newer = world.pending_marshal_petition
        assert newer is not older and newer["tier"] == "crisis"
        assert seen_key in world.jealousy_confrontations_seen, \
            "a superseded card's moment is subsumed, not withdrawn"
        line = _receipts(world)[-1]
        assert line["reason"] == "superseded"
        assert "overtaken" in line["message"]

    def test_the_other_man_of_the_pair_supersedes_too(self, world):
        """The mutual spiral: Davout's card about Ney replaces Ney's about
        Davout — the unordered pair is the subject."""
        card = _crisis_confrontation(world)
        dav = world.marshals["Davout"]
        dav.jealous_of = "Ney"
        J._set_escalation_level(dav, "Ney", 3)
        J.queue_confrontation_petition(world, dav, world.marshals["Ney"], 3)
        assert world.pending_marshal_petition is not card
        assert world.pending_marshal_petition["context"]["marshal"] == "Davout"

    def test_a_different_pair_still_blocks(self, world):
        card = _crisis_confrontation(world)
        murat = world.marshals["Murat"]
        murat.jealous_of = "Lannes"
        J._set_escalation_level(murat, "Lannes", 2)
        status = J.queue_confrontation_petition(
            world, murat, world.marshals["Lannes"], 2)
        assert status == J.PETITION_BLOCKED
        assert world.pending_marshal_petition is card

    def test_a_rivalry_card_supersedes_its_own_pair(self, world):
        older = _rivalry(world, -1)
        _rivalry(world, -2)
        assert world.pending_marshal_petition is not older
        assert world.pending_marshal_petition["context"]["new_value"] == -2
        assert _receipts(world)[-1]["reason"] == "superseded"

    def test_lever_down_the_audience_is_evicted_as_before(self, world, monkeypatch):
        monkeypatch.setattr(J, "THE_NEWER_WORD_SUPERSEDES", False)
        older = _rivalry(world, -1)
        _rivalry(world, -2)
        assert world.pending_marshal_petition is not older
        assert not [e for e in _receipts(world) if e["reason"] == "superseded"]


# ═══════════════════════ EVERY DELIVERY SEAM ASKS ══════════════════════════

class TestEverySeamAsks:

    def test_the_ordinary_drain_reaps_a_stale_card_and_delivers_the_next(self, world):
        card = _crisis_confrontation(world)
        world.marshals["Ney"].jealous_of = None
        # A popup that ranks BELOW the petition (8 vs 5): the stale card is
        # examined first, reaped, and this one delivered in the same cycle.
        world._popup_queue.push("proposal_result_popup", {"result": "ACCEPT"})
        attr, key, value = M._pop_deliverable_popup(world)
        assert attr == "proposal_result_popup", attr
        assert world.pending_marshal_petition is None
        assert _receipts(world) and _receipts(world)[-1]["reason"] == "cooled"
        assert card is not None

    def test_the_end_turn_key_retires_a_stale_card_now(self, world):
        _crisis_confrontation(world)
        world.marshals["Ney"].jealous_of = None
        response = {"enemy_phase": {"actions": []}}
        with _quiet():
            M._apply_command_popup_contract(response, {}, world)
        assert "deferred_marshal_petition" not in response
        assert world.pending_marshal_petition is None
        assert _receipts(world)

    def test_the_antechamber_get_names_why(self, world):
        card = _rivalry(world, -1)
        assert card["tier"] == "audience"
        world.marshals["Lannes"].set_relationship("Murat", 0)
        with _quiet():
            got = TestClient(M.app).get("/marshal_petition").json()
        assert got["petition"] is None
        assert got["message"].startswith("The moment has passed — ")
        assert "has mended" in got["message"]

    def test_the_answer_charges_nothing_for_a_mended_rivalry(self, world):
        _rivalry(world, -1)
        lannes = world.marshals["Lannes"]
        lannes.set_relationship("Murat", 0)
        ap_before = world.actions_remaining
        trust_before = lannes.trust.value
        result = J.handle_petition_response(world, "mediate")
        assert result["success"] is True
        assert "The moment has passed" in result["message"]
        assert "Nothing was spent" in result["message"]
        assert world.actions_remaining == ap_before
        assert lannes.trust.value == trust_before
        assert lannes.relationships.get("Murat") == 0
        assert world.pending_marshal_petition is None

    def test_the_answer_still_serves_a_standing_rivalry(self, world):
        _rivalry(world, -1)
        result = J.handle_petition_response(world, "let_be")
        assert "The moment has passed" not in result.get("message", "")


# ═══════════════════════ THE RECEIPT IS NEVER SILENT ═══════════════════════

class TestTheReceiptIsNeverSilent:

    def test_the_receipt_is_exempt_from_the_drama_cap(self):
        assert "petition_retired" in J.JEALOUSY_NARRATION_EXEMPT

    def test_the_receipt_reaches_the_dispatch(self):
        assert "petition_retired" in D._DISPATCH_EVENT_TYPES
        assert "popup_retired" in D._DISPATCH_EVENT_TYPES
        rows = D._build_turn_events(
            [{"type": "petition_retired", "message": "Berthier notes that x.",
              "nation": "France"}], "France")
        assert rows and rows[0]["message"] == "Berthier notes that x."

    def test_lever_down_is_b1_exactly(self, world, monkeypatch):
        """Lever down: FA-S17-D4's confrontation question only, a receipt for
        an audience only (B1's `marshal_audience`), other kinds stand."""
        monkeypatch.setattr(J, "THE_PETITION_DIES_WITH_ITS_SUBJECT", False)
        card = _rivalry(world, -2)
        world.marshals["Lannes"].set_relationship("Murat", 0)
        assert J.petition_retirement_reason(card, world) == ""
        world.pending_marshal_petition = None
        world._popup_queue.clear_type("pending_marshal_petition")
        crisis = _crisis_confrontation(world)
        world.marshals["Ney"].jealous_of = None
        _repush(world)
        assert world.pending_marshal_petition is None and crisis is not None
        assert not _receipts(world), "B1 retired a crisis in silence"


# ═══════════════════════ F10 — THE LOAD ASKS TOO ═══════════════════════════

def _reload(world):
    with _quiet():
        return WorldState.from_dict(world.to_dict())


class TestTheLoadAsksToo:

    def test_a_live_crisis_survives_the_load_and_is_re_primed(self, world):
        _crisis_confrontation(world)
        loaded = _reload(world)
        assert loaded.pending_marshal_petition is not None
        assert loaded._popup_queue.get("pending_marshal_petition") is not None
        assert not [e for e in getattr(loaded, "_pending_jealousy_turn_events", [])
                    if e.get("retired")]

    def test_a_stale_card_is_retired_at_the_load_with_a_receipt(self, world):
        _rivalry(world, -2)
        world.marshals["Lannes"].set_relationship("Murat", 0)
        loaded = _reload(world)
        assert loaded.pending_marshal_petition is None
        assert loaded._popup_queue.get("pending_marshal_petition") is None
        assert [e for e in loaded._pending_jealousy_turn_events
                if e.get("type") == "petition_retired"]

    def test_a_proclamation_for_a_nation_that_left_the_map(self, world):
        world.nation_proclamation_popup = {"nation": "Atlantis",
                                           "display_name": "Atlantis"}
        loaded = _reload(world)
        assert loaded.nation_proclamation_popup is None
        lines = [e for e in loaded._pending_jealousy_turn_events
                 if e.get("type") == "popup_retired"]
        assert lines and "Atlantis" in lines[-1]["message"]

    def test_a_letter_whose_dialogue_is_gone(self, world):
        world.incoming_proposal_popup = {"from_nation": "Prussia",
                                         "dialogue_id": 9999}
        loaded = _reload(world)
        assert loaded.incoming_proposal_popup is None
        assert [e for e in loaded._pending_jealousy_turn_events
                if e.get("slot") == "incoming_proposal_popup"]

    def test_an_unbound_letter_from_a_living_court_stands(self, world):
        world.incoming_proposal_popup = {"from_nation": "Prussia"}
        loaded = _reload(world)
        assert loaded.incoming_proposal_popup is not None

    def test_the_rebellion_warning_now_leaves_a_receipt(self, world):
        world.vassal_rebellion_imminent_popup = {"nation": "Atlantis"}
        loaded = _reload(world)
        assert loaded.vassal_rebellion_imminent_popup is None
        assert [e for e in loaded._pending_jealousy_turn_events
                if e.get("slot") == "vassal_rebellion_imminent_popup"]

    def test_a_load_leaves_no_primed_cache(self, world):
        """Found by the pre-commit hook: the pass reads `get_active_nations()`,
        which primes the per-turn nation and region caches — and every
        fixture that strips a province off a freshly loaded world then read
        the stale cache (four IQ-1 economy pins). A load primes nothing."""
        world.nation_proclamation_popup = {"nation": "Atlantis"}
        loaded = _reload(world)
        assert getattr(loaded, "_active_nations_cache", None) is None
        assert getattr(loaded, "_nation_regions_cache", None) is None

    def test_lever_down_the_load_is_pc15_17_alone(self, world, monkeypatch):
        import backend.models.world_state as WS
        monkeypatch.setattr(WS, "THE_LOADED_POPUP_IS_STILL_TRUE", False)
        world.nation_proclamation_popup = {"nation": "Atlantis"}
        loaded = _reload(world)
        assert loaded.nation_proclamation_popup is not None
