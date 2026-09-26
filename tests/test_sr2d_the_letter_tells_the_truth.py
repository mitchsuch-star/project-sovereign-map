"""SR-2d — "The letter tells the truth" (Score Mandate Chunk 2 exit residues
SR-2-X2 … SR-2-X5; `docs/SCORE_MANDATE_PLAN.md` §2 Chunk 2, September 26, 2026).

The Chunk 2 exit read the settlement table at the wire and found four
legibility residues on the LETTER and its rows, not on the table:

* **SR-2-X2** — the requested letter's status-quo summary named a province
  the SAME letter carved ("Austria retains … Normandy" beside "Britain erects
  the Duchy of Normandy out of France"); the ratified line never did, because
  the ratifier reads the map AFTER the appliers. The letter now subtracts what
  its own terms move (`_derive_status_quo_lines(world, war, settlement_terms)`).
* **SR-2-X3** — a ratified settlement rode the notice rail as
  `Diplomatic Action Rejected` (the PL-14 safety net's message scan found no
  accept word in "Settlement Ratified: …"). The net names the settlement off
  the ratifier's own feedback (`main._settlement_proposal_result_fields`).
  Rider found while reproducing it: the letter's own rail row ("Settlement
  offer from Britain (x5)") outlived the letter — it leaves with it now.
* **SR-2-X4** — "the requested price moves between the letter and the review
  (5,406 → 5,398)". **NOT REPRODUCED** at HEAD: measured at the wire on the
  re-driven loser arm, the letter's figure and the review's were identical on
  the accept route, the revision route (seed and Submit) and a delayed
  activation (Δ = 0 on all three). The exit's two figures were two RUNS'
  letters — a probe that ends the turn without the driver's per-turn reseed
  prices the requested package off a chest the unseeded AI turn moved. The
  invariant is pinned here so the review can never drift from the letter.
* **SR-2-X5** — the Arbiter's Offer was indistinguishable from Britain's own
  on the rail and in the mailbox, and the review it opened carried
  `mediator: null`. ONE clause (`good_offices_clause`) now rides the rail row,
  the dispatch event, the mailbox row and the review header.

Every rule has a lever whose down arm reproduces the exit's reading, so the
old behaviour is reproduced, not remembered.
"""

from pathlib import Path

import pytest

import backend.main as M
from backend.game_logic import settlement_offers as SO
from backend.game_logic import turn_manager as TM
from backend.game_logic.ai_diplomacy import (
    MEDIATION_WE_FLOOR,
    process_mediation_offers,
)
from backend.game_logic.settlement_offers import (
    _derive_status_quo_lines,
    build_incoming_settlement_offer_popup,
    consume_offer_by_id,
    good_offices_clause,
    handle_incoming_settlement_offer_action,
    promote_pending_settlement_offers,
)
from backend.game_logic.settlement_scoring import cession_shaped_regions
from backend.game_logic.settlement_staging import (
    _mounted_settlement_dialogue,
    stage_settlement_confirm,
)
from backend.models.world_state import WorldState
from backend.notifications import (
    DIPLOMATIC_PROPOSAL_RESULT,
    INCOMING_SETTLEMENT_OFFER,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SCENARIO_PATH = (REPO_ROOT / "godot-client" / "project-sovereign"
                 / "assets" / "maps" / "europe_1805.json")


@pytest.fixture(scope="module")
def world1805():
    return WorldState.from_scenario(str(SCENARIO_PATH))


@pytest.fixture()
def world(world1805):
    return WorldState.from_dict(world1805.to_dict())


@pytest.fixture()
def endpoint(world):
    """The TestClient world swap (the CR-4 idiom): `main`'s module globals
    point at THIS world for the duration of the test."""
    from backend.commands.parser import CommandParser

    original = (M.parser, M.world, M.game_state)
    M.parser = CommandParser(use_real_llm=False)
    M.world = world
    M.game_state = {"world": world}
    try:
        yield world
    finally:
        M.parser, M.world, M.game_state = original


# ── staging helpers ────────────────────────────────────────────────────────

def _boot_war(world):
    """The boot coalition war France is in: (war_id, instance, covered)."""
    for war_id, inst in world.war_instances.items():
        if not isinstance(inst, dict) or inst.get("ended_turn") is not None:
            continue
        side = inst.get("side_by_nation") or {}
        if "France" in side:
            covered = [n for n, s in side.items() if s != side["France"]]
            return war_id, inst, covered
    raise AssertionError("no boot war with France in it")


def _free_the_arbiter(world, mediator="Russia"):
    """The AI-5c staging (test_ai_intent_mediation): the mediator leaves the
    boot war and every pair of hers goes to PEACE."""
    turn = int(world.current_turn)
    for other in list(world.get_active_nations()):
        if other == mediator:
            continue
        key = world._make_diplo_key(mediator, other)
        if world.diplomatic_states.get(key) in ("WAR", "ARMISTICE"):
            world.diplomatic_states[key] = "PEACE"
    for war in world.war_instances.values():
        if not isinstance(war, dict):
            continue
        side_by = war.get("side_by_nation") or {}
        side_by.pop(mediator, None)
        active = war.get("active_participants") or []
        if mediator in active:
            active.remove(mediator)
        meta = war.get("participant_meta") or {}
        if mediator in meta and not meta[mediator].get("exited_turn"):
            meta[mediator]["exited_turn"] = turn
    world.invalidate_bloc_members_cache()


def _weary_boot_war(world):
    for war in world.war_instances.values():
        if isinstance(war, dict) and war.get("ended_turn") is None:
            war["created_turn"] = int(world.current_turn) - 4
    world.war_exhaustion[world.player_nation] = MEDIATION_WE_FLOOR + 20


def _stage_offer(world, terms, *, proposer="Britain", mediator=None,
                 seq=1, covered=None):
    """A produced incoming offer in the pending store, in the producer's own
    shape (`ai_diplomacy._settlement_offer_*`)."""
    war_id, inst, war_covered = _boot_war(world)
    side = inst["side_by_nation"]
    offer = {
        "type": "incoming_settlement_offer",
        "dialogue_type": "incoming_settlement_offer",
        "offer_id": f"settlement_offer:{war_id}:{world.current_turn}:{seq}",
        "war_id": war_id,
        "proposer_nation": proposer,
        "proposer_side": side[proposer],
        "accepting_side": side["France"],
        "accepting_leader": "France",
        "covered_enemy_participants": list(covered or war_covered),
        "settlement_terms": [dict(t) for t in terms],
        "turn_created": int(world.current_turn),
    }
    if mediator:
        offer["mediator"] = mediator
        offer["mediator_interest"] = "Arbiter of Europe"
    world.pending_settlement_dialogues = list(
        getattr(world, "pending_settlement_dialogues", None) or []) + [offer]
    return offer


def _occupy_an_austrian_home_province(world):
    """France holds one Austrian home province (not the capital), so the
    status-quo pass has something to say about France."""
    home = list(world.nation_starting_regions.get("Austria") or [])
    capital = world.get_nation_capital("Austria")
    prov = next(r for r in home if r != capital and r in world.regions)
    world.regions[prov].controller = "France"
    world.invalidate_active_nations_cache()
    return prov


def _rail(world, ntype):
    return [n for n in world.notifications.get_pending() if n.get("type") == ntype]


def _run_the_ai_diplomatic_phase(world):
    """The real producer road: the standard courier, the arbiter, the
    promotion, the rail row and the dispatch event — as `end turn` runs it."""
    world.pending_dispatch_events = list(
        getattr(world, "pending_dispatch_events", None) or [])
    TM.TurnManager(world)._process_ai_diplomatic_phase()


# ═══════════════════════════════════════════════════════════════════════════
# SR-2-X2 — the letter subtracts what it carves
# ═══════════════════════════════════════════════════════════════════════════

class TestTheLetterSubtractsWhatItCarves:
    def test_the_carved_province_is_not_retained_by_anybody(self, world):
        prov = _occupy_an_austrian_home_province(world)
        war_id, inst, _ = _boot_war(world)
        without_terms = _derive_status_quo_lines(world, inst)
        assert any(prov in line and line.startswith("France retains")
                   for line in without_terms), without_terms
        carve = {"type": "create_client", "from": "France", "to": "Austria",
                 "tag": "Carved", "provinces": [prov],
                 "client_display_name": "Duchy of the Carve"}
        with_carve = _derive_status_quo_lines(
            world, inst, [{"type": "peace"}, carve])
        assert not any(prov in line for line in with_carve), with_carve

    def test_a_cession_in_the_same_letter_is_subtracted_too(self, world):
        prov = _occupy_an_austrian_home_province(world)
        _, inst, _ = _boot_war(world)
        cede = {"type": "territory_cede", "from": "France", "to": "Austria",
                "region": prov}
        lines = _derive_status_quo_lines(world, inst, [cede])
        assert not any(prov in line for line in lines), lines

    def test_every_province_a_term_moves_is_absent_from_the_line(self, world):
        """The property the ratifier already had: nothing a clause moves is
        'retained' — over every cession dialect the scorer knows."""
        prov = _occupy_an_austrian_home_province(world)
        _, inst, _ = _boot_war(world)
        terms = [
            {"type": "peace"},
            {"type": "create_client", "from": "France", "to": "Austria",
             "tag": "Carved", "provinces": [prov]},
        ]
        moved = {p for t in terms for p in cession_shaped_regions(t)}
        assert prov in moved
        lines = _derive_status_quo_lines(world, inst, terms)
        for line in lines:
            for p in moved:
                assert p not in line, (p, line)

    def test_the_popup_agrees_with_itself(self, world):
        """The letter the player reads: the carve line names the province,
        the status-quo line beside it does not."""
        prov = _occupy_an_austrian_home_province(world)
        offer = _stage_offer(world, [
            {"type": "peace"},
            {"type": "create_client", "from": "France", "to": "Austria",
             "tag": "Carved", "provinces": [prov],
             "client_display_name": "Duchy of the Carve"},
        ])
        popup = build_incoming_settlement_offer_popup(world, offer)
        summary = popup["terms_summary"]
        carve_lines = [s for s in summary if "erects" in s or "Client state" in s]
        status = [s for s in summary if s.startswith("Status quo:")]
        assert carve_lines and any(prov in s for s in carve_lines), summary
        assert all(prov not in s for s in status), summary

    def test_the_lever_down_reproduces_the_exits_letter(self, world, monkeypatch):
        prov = _occupy_an_austrian_home_province(world)
        _, inst, _ = _boot_war(world)
        carve = {"type": "create_client", "from": "France", "to": "Austria",
                 "tag": "Carved", "provinces": [prov]}
        monkeypatch.setattr(SO, "THE_LETTER_SUBTRACTS_WHAT_IT_CARVES", False)
        lines = _derive_status_quo_lines(world, inst, [carve])
        assert any(prov in line for line in lines), lines

    def test_a_letter_that_moves_no_soil_is_byte_identical(self, world):
        prov = _occupy_an_austrian_home_province(world)
        _, inst, _ = _boot_war(world)
        gold_only = [{"type": "peace"},
                     {"type": "gold_indemnity", "from": "France",
                      "to": "Britain", "amount": 500}]
        assert (_derive_status_quo_lines(world, inst, gold_only)
                == _derive_status_quo_lines(world, inst))
        assert any(prov in line for line in _derive_status_quo_lines(world, inst))


# ═══════════════════════════════════════════════════════════════════════════
# SR-2-X3 — the ratified settlement names itself on the rail
# ═══════════════════════════════════════════════════════════════════════════

def _ratify_a_consented_white_peace(world):
    war_id, inst, covered = _boot_war(world)
    staged = stage_settlement_confirm(
        world, war_id=war_id, actor_nation="France", white_peace=True,
        caller_kind="ai_system", covered_enemy_participants=covered,
        selected_target_nation=covered[0],
        consenting_courts=list(covered), consent_terms=[],
        consent_offer_id="sr2d-x3")
    dialogue = staged.get("diplomatic_dialogue") or {}
    assert staged.get("success") and dialogue.get("can_ratify"), staged
    return M._respond_to_dialogue_sync(
        "confirm", dialogue_id=dialogue.get("dialogue_id"))


class TestTheRatifiedSettlementNamesItself:
    def test_the_response_names_the_settlement_and_reads_accept(self, endpoint):
        world = endpoint
        resp = _ratify_a_consented_white_peace(world)
        assert resp.get("success"), resp.get("message")
        assert str(resp.get("message") or "").startswith("Settlement Ratified")
        result = resp.get("proposal_result") or world.proposal_result_popup
        assert result, "the PL-14 net delivered nothing"
        assert result["proposal_type"] == "Settlement"
        assert result["outcome"] == "ACCEPT"
        assert result["title"] == "Settlement Ratified"
        assert "France" in result["target_nation"] and "vs" in result["target_nation"]

    def test_the_rail_row_reads_settlement_ratified(self, endpoint):
        world = endpoint
        _ratify_a_consented_white_peace(world)
        rows = _rail(world, DIPLOMATIC_PROPOSAL_RESULT)
        titles = [r.get("title") for r in rows]
        assert "Settlement Ratified" in titles, titles
        row = next(r for r in rows if r.get("title") == "Settlement Ratified")
        assert row["details"]["outcome"] == "ACCEPT"
        assert row["details"]["proposal_type"] == "Settlement"
        assert str(row.get("message") or "").startswith("Settlement Ratified")
        # The exit's reading — the ratification sentence under a REJECT title —
        # is gone.
        assert not any(
            "Rejected" in str(r.get("title") or "")
            and "Settlement Ratified" in str(r.get("message") or "")
            for r in rows), titles

    def test_the_fields_are_read_off_the_ratifiers_own_feedback(self):
        ratified = {
            "success": True, "dialogue_type": "settlement_confirm",
            "message": "Settlement Ratified: France vs Austria (2 pairs resolved).",
            "settlement_result_feedback": {
                "title": "Settlement Ratified", "war_label": "France vs Austria",
                "resolved_pair_count": 2},
        }
        fields = M._settlement_proposal_result_fields(ratified)
        assert fields == {
            "proposal_type": "Settlement", "outcome": "ACCEPT",
            "title": "Settlement Ratified", "target_nation": "France vs Austria",
            "resolved_pair_count": 2,
        }
        # Never off absent fields: a refused ratification, another dialogue
        # family, or a result with no feedback block declares nothing.
        assert M._settlement_proposal_result_fields(
            {**ratified, "success": False}) == {}
        assert M._settlement_proposal_result_fields(
            {**ratified, "dialogue_type": "incoming_proposal"}) == {}
        assert M._settlement_proposal_result_fields(
            {"success": True, "dialogue_type": "settlement_confirm",
             "message": "x"}) == {}
        assert M._settlement_proposal_result_fields("not a dict") == {}

    def test_other_results_keep_their_composed_title(self, world):
        """The net's other customers are byte-identical: a plain refusal
        still composes '<type> <outcome>' and still reads REJECT."""
        plain = {"success": True,
                 "message": "You have rejected Russia's proposal. Talleyrand will convey your decision."}
        assert M._settlement_proposal_result_fields(plain) == {}
        assert M._derive_proposal_result_outcome(plain) == "REJECT"
        response = {"proposal_result": {
            "target_nation": "Russia", "proposal_type": "Diplomatic Action",
            "outcome": "REJECT", "message": plain["message"], "feedback": ""}}
        M._queue_informational_diplomacy_notices(response, world)
        rows = _rail(world, DIPLOMATIC_PROPOSAL_RESULT)
        assert [r["title"] for r in rows if r["details"]["target_nation"] == "Russia"] == [
            "Diplomatic Action Rejected"]


# ═══════════════════════════════════════════════════════════════════════════
# SR-2-X3's rider — the letter's rail row leaves with the letter
# ═══════════════════════════════════════════════════════════════════════════

def _promote_with_the_rail_row(world, offer):
    """Promote a staged offer the way `end turn` does, so its rail row exists
    with the producer's own details."""
    _run_the_ai_diplomatic_phase(world)
    dm = world.dialogue_manager
    promoted = None
    for entry in [dm.peek()] + list(dm._queue):
        if isinstance(entry, dict) and entry.get("offer_id") == offer["offer_id"]:
            promoted = entry
            break
    assert promoted is not None, "the staged offer was not promoted"
    rows = [r for r in _rail(world, INCOMING_SETTLEMENT_OFFER)
            if (r.get("details") or {}).get("offer_id") == offer["offer_id"]]
    assert rows, "the producer wrote no rail row for the offer"
    return promoted


_GOLD_PEACE = [{"type": "peace"},
               {"type": "gold_indemnity", "from": "France", "to": "Britain",
                "amount": 1406}]


class TestTheLettersRailRowLeavesWithIt:
    def _rows_for(self, world, offer_id):
        return [r for r in _rail(world, INCOMING_SETTLEMENT_OFFER)
                if (r.get("details") or {}).get("offer_id") == offer_id]

    def test_accepting_the_letter_retires_its_row(self, world):
        offer = _stage_offer(world, _GOLD_PEACE)
        promoted = _promote_with_the_rail_row(world, offer)
        result = handle_incoming_settlement_offer_action(
            world, action="accept_settlement_offer", dialogue=promoted)
        assert result.get("success"), result
        assert self._rows_for(world, offer["offer_id"]) == []

    def test_rejecting_the_letter_retires_its_row(self, world):
        offer = _stage_offer(world, _GOLD_PEACE)
        promoted = _promote_with_the_rail_row(world, offer)
        result = handle_incoming_settlement_offer_action(
            world, action="reject_settlement_offer", dialogue=promoted)
        assert result.get("success"), result
        assert self._rows_for(world, offer["offer_id"]) == []

    def test_the_deferred_consumption_retires_it_too(self, world):
        """The revision route consumes the letter later (SR-2a) through
        `consume_offer_by_id` — the row leaves at that moment."""
        offer = _stage_offer(world, _GOLD_PEACE)
        _promote_with_the_rail_row(world, offer)
        assert consume_offer_by_id(world, offer_id=offer["offer_id"],
                                   war_id=offer["war_id"])
        assert self._rows_for(world, offer["offer_id"]) == []

    def test_another_letters_row_stands(self, world):
        """Keyed on the offer, never on the court or the war."""
        offer = _stage_offer(world, _GOLD_PEACE, seq=1)
        promoted = _promote_with_the_rail_row(world, offer)
        other = {"type": INCOMING_SETTLEMENT_OFFER, "priority": 2,
                 "title": "Settlement offer from Austria",
                 "message": "Austria has offered terms.",
                 "turn_created": int(world.current_turn),
                 "details": {"war_id": offer["war_id"],
                             "offer_id": "settlement_offer:other:9:1",
                             "proposer_nation": "Austria"}}
        from backend.notifications import create_notification, NotificationPriority
        world.notifications.add(create_notification(
            INCOMING_SETTLEMENT_OFFER, NotificationPriority.HIGH,
            other["title"], other["message"], other["turn_created"],
            details=other["details"]))
        handle_incoming_settlement_offer_action(
            world, action="accept_settlement_offer", dialogue=promoted)
        assert self._rows_for(world, offer["offer_id"]) == []
        assert self._rows_for(world, "settlement_offer:other:9:1")

    def test_the_lever_down_leaves_the_row_standing(self, world, monkeypatch):
        offer = _stage_offer(world, _GOLD_PEACE)
        promoted = _promote_with_the_rail_row(world, offer)
        monkeypatch.setattr(SO, "THE_LETTERS_RAIL_ROW_LEAVES_WITH_IT", False)
        handle_incoming_settlement_offer_action(
            world, action="accept_settlement_offer", dialogue=promoted)
        assert self._rows_for(world, offer["offer_id"]), (
            "the exit's reading: the row outlives the letter")


# ═══════════════════════════════════════════════════════════════════════════
# SR-2-X4 — the review carries the letter's figure (not reproduced; pinned)
# ═══════════════════════════════════════════════════════════════════════════

def _gold_of(dialogue):
    return [int(t.get("amount") or 0)
            for t in (dialogue or {}).get("settlement_terms") or []
            if t.get("type") == "gold_indemnity"]


class TestTheReviewCarriesTheLettersFigure:
    def test_the_accept_route_stages_the_letters_amount(self, world):
        offer = _stage_offer(world, [
            {"type": "peace"},
            {"type": "gold_indemnity", "from": "France", "to": "Britain",
             "amount": 2406}])
        promoted = promote_pending_settlement_offers(world)[0]
        assert _gold_of(promoted["popup_payload"]) == [2406]
        result = handle_incoming_settlement_offer_action(
            world, action="accept_settlement_offer", dialogue=promoted)
        assert result.get("success"), result
        assert _gold_of(result.get("diplomatic_dialogue")) == [2406]

    def test_a_ledger_move_between_letter_and_review_changes_nothing(self, world):
        """The exit's diagnosis ('re-priced against a chest the end-turn
        ledger has since moved') — the chest moves here by more than the
        exit's 8 gold, and the review still carries the letter's figure."""
        offer = _stage_offer(world, [
            {"type": "peace"},
            {"type": "gold_indemnity", "from": "France", "to": "Britain",
             "amount": 2406}])
        promoted = promote_pending_settlement_offers(world)[0]
        world.nation_gold["France"] = int(world.nation_gold.get("France", 0)) - 750
        result = handle_incoming_settlement_offer_action(
            world, action="accept_settlement_offer", dialogue=promoted)
        assert result.get("success"), result
        assert _gold_of(result.get("diplomatic_dialogue")) == [2406]

    def test_the_revision_route_seeds_the_letters_amount(self, world):
        offer = _stage_offer(world, [
            {"type": "peace"},
            {"type": "gold_indemnity", "from": "France", "to": "Britain",
             "amount": 2406}])
        promoted = promote_pending_settlement_offers(world)[0]
        result = handle_incoming_settlement_offer_action(
            world, action="request_settlement_revision", dialogue=promoted)
        assert result.get("success"), result
        table = result.get("diplomatic_dialogue") or {}
        assert str(table.get("dialogue_mode") or "").upper() == "PROPOSE"
        assert _gold_of(table) == [2406]
        # The letter stands (SR-2a) and still says 2,406.
        assert promoted.get("offer_id") == offer["offer_id"]
        assert _gold_of(promoted["popup_payload"]) == [2406]


# ═══════════════════════════════════════════════════════════════════════════
# SR-2-X5 — the mediator is named on every surface
# ═══════════════════════════════════════════════════════════════════════════

class TestTheGoodOfficesClause:
    def test_the_one_clause(self):
        assert good_offices_clause("Russia") == "under Russia's good offices"
        assert good_offices_clause("PapalStates") == "under the Papal States' good offices"
        assert good_offices_clause("") == ""
        assert good_offices_clause(None) == ""

    def test_the_lever_down_is_silent(self, monkeypatch):
        monkeypatch.setattr(SO, "THE_MEDIATOR_IS_NAMED_ON_EVERY_SURFACE", False)
        assert good_offices_clause("Russia") == ""


def _the_arbiters_offer(world):
    """The real Arbiter's Offer through the real AI diplomatic phase."""
    _free_the_arbiter(world, "Russia")
    _weary_boot_war(world)
    _run_the_ai_diplomatic_phase(world)
    dm = world.dialogue_manager
    for entry in [dm.peek()] + list(dm._queue):
        if isinstance(entry, dict) and entry.get("mediator") == "Russia":
            return entry
    raise AssertionError("the Arbiter's Offer was not promoted")


class TestTheMediatorIsNamedOnEverySurface:
    def test_the_rail_row_names_the_mediator(self, world):
        offer = _the_arbiters_offer(world)
        rows = [r for r in _rail(world, INCOMING_SETTLEMENT_OFFER)
                if (r.get("details") or {}).get("offer_id") == offer["offer_id"]]
        assert rows, "no rail row for the mediated offer"
        row = rows[0]
        assert row["title"] == "Russia offers good offices"
        assert "under Russia's good offices" in row["message"]
        assert row["message"].startswith(f"{offer['proposer_nation']}'s terms to settle")
        assert row["details"]["mediator"] == "Russia"

    def test_the_dispatch_event_carries_the_mediator(self, world):
        offer = _the_arbiters_offer(world)
        events = [e for e in world.pending_dispatch_events
                  if e.get("type") == "settlement_offer_arrival"
                  and e.get("offer_id") == offer["offer_id"]]
        assert events and events[0]["mediator"] == "Russia"
        assert "under Russia's good offices" in events[0]["message"]

    def test_the_mailbox_row_names_the_mediator(self, world):
        offer = _the_arbiters_offer(world)
        items = world.dialogue_manager.get_mailbox_items()
        mine = [i for i in items if i["item_type"] == "incoming_settlement_offer"]
        assert mine, items
        row = mine[0]
        assert row["summary_text"].startswith(
            "Under Russia's good offices — Settlement offer")
        assert row["summary"].endswith(", under Russia's good offices")
        assert row["source_nation"] == offer["proposer_nation"]

    def test_the_review_carries_the_provenance(self, world):
        offer = _the_arbiters_offer(world)
        result = handle_incoming_settlement_offer_action(
            world, action="accept_settlement_offer", dialogue=offer)
        assert result.get("success"), result
        staged = result.get("diplomatic_dialogue") or {}
        assert staged.get("mediator") == "Russia"
        assert staged.get("mediator_interest") == "Arbiter of Europe"
        mounted = _mounted_settlement_dialogue(world)
        assert mounted is not None and mounted.get("mediator") == "Russia"
        assert str(result.get("message") or "").startswith(
            "Under Russia's good offices, ")
        voice = str(staged.get("talleyrand_text") or "")
        assert voice.startswith("Under Russia's good offices, "), voice
        # The sentence that follows the clause is the staging's own, intact
        # (a vocative "Sire" keeps its capital).
        assert "Sire" in voice and "sire," not in voice, voice

    def test_the_belligerents_own_letter_is_byte_identical(self, world):
        """Britain's own letter reads as it always did — no mediator key
        anywhere, the old title, the old sentence, the old mailbox row."""
        offer = _stage_offer(world, _GOLD_PEACE)
        promoted = _promote_with_the_rail_row(world, offer)
        row = [r for r in _rail(world, INCOMING_SETTLEMENT_OFFER)
               if (r.get("details") or {}).get("offer_id") == offer["offer_id"]][0]
        assert row["title"].startswith("Settlement offer from Britain")
        assert row["message"].startswith("Britain has offered terms to settle")
        assert "mediator" not in row["details"]
        event = next(e for e in world.pending_dispatch_events
                     if e.get("offer_id") == offer["offer_id"])
        assert "mediator" not in event
        item = next(i for i in world.dialogue_manager.get_mailbox_items()
                    if i["item_type"] == "incoming_settlement_offer")
        assert item["summary"] == "Britain — Settlement Offer"
        assert item["summary_text"].startswith("Settlement offer:")
        result = handle_incoming_settlement_offer_action(
            world, action="accept_settlement_offer", dialogue=promoted)
        assert "mediator" not in (result.get("diplomatic_dialogue") or {})

    def test_the_lever_down_reproduces_the_exits_blindness(self, world, monkeypatch):
        monkeypatch.setattr(SO, "THE_MEDIATOR_IS_NAMED_ON_EVERY_SURFACE", False)
        offer = _the_arbiters_offer(world)
        row = [r for r in _rail(world, INCOMING_SETTLEMENT_OFFER)
               if (r.get("details") or {}).get("offer_id") == offer["offer_id"]][0]
        assert row["title"] == f"Settlement offer from {offer['proposer_nation']}"
        item = next(i for i in world.dialogue_manager.get_mailbox_items()
                    if i["item_type"] == "incoming_settlement_offer")
        assert "good offices" not in item["summary"]
        result = handle_incoming_settlement_offer_action(
            world, action="accept_settlement_offer", dialogue=offer)
        assert "mediator" not in (result.get("diplomatic_dialogue") or {})
