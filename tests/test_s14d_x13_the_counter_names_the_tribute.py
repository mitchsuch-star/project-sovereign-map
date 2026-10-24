"""S14D-X13 - a counter-offer's letter names what the court STRUCK.

Pre-Deploy S14d part 2 (October 24, 2026; defect row S14D-X13 in
`docs/BUG_FIXES.md`). Measured on the Table board
(`godot-client/project-sovereign/assets/maps/tutorial_table_1805.json`):
Talleyrand's vassalage draft to Bavaria carries one demand - 126 gold a turn,
the tribute - and scores 45 COUNTER_OFFER. Sent as suggested and answered at
the next morning, Bavaria's `counter_offer_response` is built in
`WorldState._process_proposal_in_transit` from `generate_counter_offer`, which
STRIKES the tribute: the counter's terms carry no demands, so the popup's
clause lines fell to `build_proposal_popup_clauses`'s fallback and read
`["Diplomatic proposal"]` - and the dialogue text and the event line read
"Vassalage between France and Bavaria". The player was handed a letter that
named nothing, about a clause (the tribute) that was the whole bargain.

The fix is a diff: `display_names.counter_offer_clause_lines(original,
counter)` names each term the counter removed ("Struck: the tribute - 126 gold
a turn for as long as the treaty stands") and keeps the lines of the terms it
kept; `build_pending_envoy_popup_from_terms(..., original=...)` carries the
original through. Two producers build a counter letter - the envoy's answer to
France's own proposal (the Table's road, pinned first) and France's counter to
an AI proposal (`_handle_counter_ai_proposal`, the M3 road, pinned second) -
and `/pending_envoy`'s rebuild-from-the-dialogue fallback is the third reader.
"""
from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from backend.display_names import (
    build_proposal_popup_clauses,
    counter_offer_clause_lines,
    counter_struck_lines,
    counter_struck_terms,
    counter_summary_with_struck,
)

REPO = Path(__file__).resolve().parents[1]
MAPS = REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
TABLE_BOARD = MAPS / "tutorial_table_1805.json"

TRIBUTE_LINE = "Struck: the tribute - 126 gold a turn for as long as the treaty stands"


# ══════════════════════════════════════════════════════════════════════════
# The Table's road: France proposes, Bavaria strikes the tribute
# ══════════════════════════════════════════════════════════════════════════

def _post(client, path: str, body: dict) -> dict:
    return client.post(path, json=body).json() or {}


def _choose(client, dialogue: dict, *, action: str) -> dict:
    """Answer a dialogue the way the client does - by the 1-based index of the
    option, with the dialogue's id."""
    for index, option in enumerate(dialogue.get("options") or [], start=1):
        if isinstance(option, dict) and option.get("action") == action:
            body = {"choice": index}
            if dialogue.get("dialogue_id") is not None:
                body["dialogue_id"] = dialogue.get("dialogue_id")
            return _post(client, "/respond_to_diplomatic_dialogue", body)
    raise AssertionError(f"no {action!r} option on {dialogue.get('type')!r}")


@pytest.fixture(scope="module")
def table_road():
    """The road, played once: boot the Table, draft the vassalage, send it as
    suggested, end the turn, read Bavaria's counter on every surface that
    carries it, then accept it."""
    if not TABLE_BOARD.exists():
        pytest.skip("the Table board (tutorial_table_1805.json) is not on disk")
    save_dir = Path(tempfile.mkdtemp()) / "saves"
    try:
        with patch("backend.save_manager.SAVE_DIR", save_dir):
            import backend.main as main_module
            from backend.commands.parser import CommandParser

            main_module._reset_world_state(scenario_override=str(TABLE_BOARD))
            previous_parser = main_module.parser
            main_module.parser = CommandParser(use_real_llm=False)
            try:
                with TestClient(main_module.app) as client:
                    world = main_module.game_state["world"]
                    drafted = _post(client, "/command", {"command": "propose vassalage to Bavaria"})
                    draft = drafted.get("diplomatic_dialogue") or {}
                    send = next(o for o in draft["options"] if o.get("action") == "execute_proposal")
                    sent_terms = send.get("terms")
                    estimate = (draft.get("acceptance_estimate"), draft.get("acceptance_outcome"))
                    _choose(client, draft, action="execute_proposal")
                    ended = _post(client, "/command", {"command": "end turn"})

                    counters = [d for d in [world.dialogue_manager.peek()] + list(world.dialogue_manager.iter_queue())
                                if isinstance(d, dict) and d.get("type") == "counter_offer_response"]
                    assert len(counters) == 1, [d.get("type") for d in counters]
                    counter = counters[0]
                    pending = client.get("/pending_envoy").json()
                    events = [str(e.get("message") or "") for e in (ended.get("events") or [])
                              if isinstance(e, dict) and e.get("outcome") == "COUNTER_OFFER"]

                    # the same letter, rebuilt from the dialogue alone (the
                    # fallback `/pending_envoy` takes when the payload is gone)
                    rebuilt_from = dict(counter)
                    rebuilt_from.pop("popup_payload", None)
                    rebuilt = main_module._build_pending_envoy_popup_from_dialogue(world, rebuilt_from)

                    accepted = _choose(client, counter, action="accept_counter_offer")
                    yield SimpleNamespace(
                        sent_terms=sent_terms, estimate=estimate, counter=counter, pending=pending,
                        events=events, rebuilt=rebuilt, accepted=accepted,
                        bavaria_state=world.diplomatic_states.get(world._make_diplo_key("France", "Bavaria")),
                    )
            finally:
                main_module.parser = previous_parser
                main_module._reset_world_state()
    finally:
        shutil.rmtree(save_dir.parent, ignore_errors=True)


class TestTheTableCounterNamesTheTribute:
    """⟨SF step=pre-deploy S14d · S14D-X13 · pillar=vassals⟩
    The driven road on the Table board: the suggested vassalage to Bavaria
    (126 gold a turn, estimate 45 COUNTER_OFFER), sent and answered at the
    morning, reads as a letter that names the struck tribute on every surface
    that carries it."""

    def test_the_road_is_the_measured_one(self, table_road):
        assert table_road.sent_terms["type"] == "vassalage"
        assert table_road.sent_terms["demands"] == [{"type": "gold_per_turn", "value": 126}]
        assert table_road.estimate == (45, "COUNTER_OFFER")
        counter_terms = table_road.counter["context"]["counter_terms"]
        assert counter_terms["demands"] == [] and counter_terms["sweeteners"] == []

    def test_the_popup_names_the_struck_tribute(self, table_road):
        payload = table_road.counter["popup_payload"]
        assert payload["is_counter_offer"] is True
        assert payload["proposal_type_display"] == "Vassalage"
        lines = payload["clauses"]
        assert lines == ["Proposal: Vassalage", TRIBUTE_LINE]
        text = " ".join(lines)
        assert "126 gold a turn" in text and "tribute" in text
        assert "gold_per_turn" not in text           # R7: no raw token

    def test_the_generic_words_never_appear(self, table_road):
        for clauses in (table_road.counter["popup_payload"]["clauses"],
                        table_road.pending["incoming_proposal"]["clauses"],
                        table_road.rebuilt["clauses"]):
            assert clauses != ["Diplomatic proposal"]
            assert "Diplomatic proposal" not in clauses

    def test_every_reader_of_the_letter_carries_the_same_lines(self, table_road):
        payload_lines = table_road.counter["popup_payload"]["clauses"]
        assert table_road.pending["dialogue_type"] == "counter_offer_response"
        assert table_road.pending["incoming_proposal"]["clauses"] == payload_lines
        # the rebuild from the dialogue's own context names it too
        assert table_road.rebuilt["clauses"] == payload_lines

    def test_the_dialogue_text_and_the_event_line_name_it(self, table_road):
        text = table_road.counter["talleyrand_text"]
        assert "Their counter-proposal:" in text and TRIBUTE_LINE in text
        assert len(table_road.events) == 1
        assert TRIBUTE_LINE in table_road.events[0]

    def test_the_counter_still_binds_what_the_letter_says(self, table_road):
        """The letter reads 'Vassalage, tribute struck' - and accepting it makes
        Bavaria a vassal on those terms."""
        assert table_road.accepted.get("success") is not False, table_road.accepted
        assert table_road.bavaria_state == "VASSAL"


# ══════════════════════════════════════════════════════════════════════════
# The wording function, on synthetic drafts
# ══════════════════════════════════════════════════════════════════════════

def _draft(**kw):
    base = {"type": "vassalage", "proposer_nation": "France", "target_nation": "Bavaria",
            "sweeteners": [], "demands": [], "clauses": []}
    base.update(kw)
    return base


class TestTheWording:
    """⟨SF step=pre-deploy S14d · S14D-X13 · pillar=vassals⟩
    `counter_offer_clause_lines` / `counter_struck_lines`: what was struck, what
    was kept, in the words every other letter already uses."""

    def test_a_struck_demand_and_a_kept_offer(self):
        original = _draft(demands=[{"type": "gold_per_turn", "value": 126}],
                          sweeteners=[{"type": "gold_lump", "value": 50}])
        counter = _draft(sweeteners=[{"type": "gold_lump", "value": 50}])
        assert counter_offer_clause_lines(original, counter) == [
            "Proposal: Vassalage",
            TRIBUTE_LINE,
            "Offer: Gold payment - 50",
        ]

    def test_the_tribute_is_the_vassalage_demand_only(self):
        """Outside a vassalage a struck gold stream is a struck demand, not 'the tribute'."""
        original = _draft(type="peace", demands=[{"type": "gold_per_turn", "value": 126}])
        lines = counter_offer_clause_lines(original, _draft(type="peace"))
        assert lines == ["Proposal: Peace Treaty",
                         "Struck demand: Gold per turn - 126 for as long as the treaty stands"]

    def test_a_stream_with_its_own_term_names_it(self):
        original = _draft(demands=[{"type": "gold_per_turn", "value": 80, "turns": 5}])
        assert counter_struck_lines(original, _draft()) == [
            "Struck: the tribute - 80 gold a turn for 5 turns"]

    def test_a_struck_offer_and_a_struck_clause(self):
        original = _draft(type="alliance", sweeteners=[{"type": "gold_lump", "value": 100}],
                          clauses=["open_borders"])
        counter = _draft(type="alliance")
        assert counter_offer_clause_lines(original, counter) == [
            "Proposal: Full Alliance",
            "Struck clause: Open borders",
            "Struck offer: Gold payment - 100",
        ]

    def test_a_struck_territory_names_its_regions(self):
        original = _draft(type="peace", demands=[{"type": "territory_cede", "value": 1, "regions": ["Tyrol"]}])
        lines = counter_struck_lines(original, _draft(type="peace"))
        assert lines == ["Struck demand: Territory cession - Tyrol"]

    def test_what_the_counter_kept_is_not_struck(self):
        """Identity is by term, not position; a bare clause string equals its
        {'type': ...} form; type case and 126 vs 126.0 do not split a term."""
        original = _draft(clauses=["open_borders"], demands=[{"type": "gold_per_turn", "value": 126}])
        counter = _draft(clauses=[{"type": "OPEN_BORDERS"}], demands=[{"type": "Gold_Per_Turn", "value": 126.0}])
        assert counter_struck_terms(original, counter) == []
        assert counter_struck_lines(original, counter) == []

    def test_a_changed_figure_reads_as_struck_and_as_carried(self):
        original = _draft(demands=[{"type": "gold_per_turn", "value": 126}])
        counter = _draft(demands=[{"type": "gold_per_turn", "value": 80}])
        lines = counter_offer_clause_lines(original, counter)
        assert lines[0] == "Proposal: Vassalage"
        assert TRIBUTE_LINE in lines
        assert any("Demand: Gold per turn - 80" in line for line in lines)

    def test_a_counter_that_struck_nothing_reads_as_it_always_did(self):
        original = _draft(sweeteners=[{"type": "gold_lump", "value": 50}])
        counter = _draft(sweeteners=[{"type": "gold_lump", "value": 50}, {"type": "gold_lump", "value": 100}],
                         clauses=["open_borders"])
        assert counter_offer_clause_lines(original, counter) == build_proposal_popup_clauses(
            counter, include_base=False)

    def test_an_empty_counter_still_says_which_proposal(self):
        assert counter_offer_clause_lines(_draft(), _draft()) == ["Proposal: Vassalage"]
        assert build_proposal_popup_clauses(_draft(), include_base=False) == ["Proposal: Vassalage"]
        # only a terms dict with no type at all keeps the generic words
        assert build_proposal_popup_clauses({}, include_base=False) == ["Diplomatic proposal"]

    def test_it_never_raises_on_a_partial_draft(self):
        assert counter_struck_lines(None, _draft()) == []
        assert counter_struck_lines(_draft(), None) == []
        assert counter_offer_clause_lines(None, None) == ["Diplomatic proposal"]
        # a draft missing whole lists, a null list, a string demand value
        assert counter_struck_lines({"type": "peace"}, {"type": "peace", "demands": None}) == []
        original = {"type": "peace", "demands": [{"type": "territory", "value": "Bavaria"}]}
        assert counter_struck_lines(original, {"type": "peace"}) == ["Struck demand: Territory cession - Bavaria"]

    def test_the_summary_carries_the_struck_lines(self):
        original = _draft(demands=[{"type": "gold_per_turn", "value": 126}])
        base = "Vassalage between France and Bavaria"
        assert counter_summary_with_struck(base, original, _draft()) == base + "\n  - " + TRIBUTE_LINE
        assert counter_summary_with_struck(base, original, original) == base


# ══════════════════════════════════════════════════════════════════════════
# The sibling: France counters an AI proposal (the M3 road)
# ══════════════════════════════════════════════════════════════════════════

class TestTheAICounterFamily:
    """⟨SF step=pre-deploy S14d · S14D-X13 · pillar=vassals⟩
    `_handle_counter_ai_proposal` builds the other counter letter. A counter
    that strikes the proposal's only demand used to read 'Diplomatic proposal'
    here too (the same empty-clause fallback); it now names the struck demand,
    on the popup, in the dialogue text, and in the context a rebuild reads."""

    def _counter_the_proposal(self, monkeypatch):
        import backend.game_logic.ai_diplomacy as aidip
        from backend.commands.executor import CommandExecutor
        from backend.models.world_state import WorldState

        world = WorldState(player_nation="France")
        world.current_turn = 5
        world.diplomatic_points = 3
        proposal = {"type": "peace", "proposer_nation": "Austria", "target_nation": "France",
                    "sweeteners": [], "clauses": [],
                    "demands": [{"type": "gold_lump", "value": 500}]}

        def strike_the_demand(terms, w, **_kw):
            countered = dict(terms)
            countered["demands"] = []
            return countered

        monkeypatch.setattr(aidip, "generate_counter_offer", strike_the_demand)
        dialogue = {
            "type": "incoming_proposal", "target_nation": "Austria", "talleyrand_text": "x",
            "options": [],
            "context": {"proposal": proposal, "source_nation": "Austria",
                        "proposal_type": "peace", "decision_reason": "war_overload"},
            "turn_created": 5, "blocking": False,
        }
        result = CommandExecutor()._diplomatic._handle_counter_ai_proposal(dialogue, world)
        assert result["success"] is True, result.get("message")
        return world, world.pending_diplomatic_dialogue

    def test_the_letter_names_the_struck_demand(self, monkeypatch):
        _world, counter = self._counter_the_proposal(monkeypatch)
        assert counter["type"] == "counter_offer"
        lines = counter["popup_payload"]["clauses"]
        assert lines == ["Proposal: Peace Treaty", "Struck demand: Gold payment - 500"]
        assert "Diplomatic proposal" not in lines
        assert "Struck demand: Gold payment - 500" in counter["talleyrand_text"]

    def test_the_context_carries_the_draft_for_a_rebuild(self, monkeypatch):
        import backend.main as main_module

        world, counter = self._counter_the_proposal(monkeypatch)
        assert counter["context"]["original_proposal"]["demands"] == [{"type": "gold_lump", "value": 500}]
        rebuilt_from = dict(counter)
        rebuilt_from.pop("popup_payload", None)
        rebuilt = main_module._build_pending_envoy_popup_from_dialogue(world, rebuilt_from)
        assert "Struck demand: Gold payment - 500" in rebuilt["clauses"]
        assert "Diplomatic proposal" not in rebuilt["clauses"]


class TestThePeaceCounterPrintsItsStruckLines:
    """⟨SF step=pre-deploy S14d · S14D-X50 · pillar=narration⟩ The client's
    peace preview draws `annotated_terms` instead of `clauses` whenever they
    are non-empty, so a peace counter that struck one demand but kept others
    hid its Struck lines; it prints them beneath the kept terms when the
    letter is a counter (October 24, 2026)."""

    def test_the_preview_prints_the_struck_lines_of_a_counter(self):
        gd = (Path(__file__).resolve().parents[1] / "godot-client" / "project-sovereign"
              / "scripts" / "incoming_proposal_popup.gd").read_text(encoding="utf-8")
        body = gd[gd.index("func _build_peace_preview_section("):]
        body = body[:body.index("\nfunc ", 10)]
        assert "_build_annotated_terms_section(annotated)" in body
        assert 'data.get("is_counter_offer", false)' in body
        assert 'str(clause).begins_with("Struck")' in body
        # the struck lines print INSIDE the annotated arm, after the kept terms
        assert body.index("_build_annotated_terms_section(annotated)") < body.index('begins_with("Struck")') < body.index("\telse:")


class TestTheIncomingLettersNeverReadEmpty:
    """⟨SF step=pre-deploy S14d · S14D-X13 · pillar=vassals⟩
    The rest of the family needs no new naming: an incoming proposal, an
    ultimatum, a call to arms are built with the base line ('Proposal: <type>')
    so their clauses are never empty - only a COUNTER omits it."""

    def test_an_incoming_proposal_always_leads_with_its_type(self):
        for terms in (_draft(), _draft(type="peace"), _draft(type="open_borders")):
            lines = build_proposal_popup_clauses(terms)
            assert lines and lines[0].startswith("Proposal: ")
