"""Gate-4 leg-1 smoke fix slice (G4F-1 / G4F-2 / G4F-3).

June 11, 2026 player smoke findings, reproduced through the real HTTP wire
shapes and fixed:

- G4L1-1: settlement ``gold_indemnity`` fell through the harshness
  accumulator unmatched (only the bilateral ``gold_lump`` name was priced),
  so every gold demand cost ZERO acceptance and the Harsher/Ease dials were
  placebos (the frozen 63/50). Fix: the demands dialect prices
  ``gold_indemnity`` at the existing 0.08-per-100-gold weight, and the
  package raw harshness is computed over the ACCEPTING-side burden terms
  only (``compute_settlement_package_raw_harshness``) — proposer-paid
  concessions belong to ``concession_credit``, never to harshness.
- G4L1-2: the dial grew gold past the payer court's balance and relied on
  the restage validator to bounce (`gold_payment_budget_conflict` rendered
  as the generic blame-the-player copy) — the DC-1 class. Fix: dial grows
  clamp at the payer's remaining capacity (``compute_gold_payer_budgets``,
  the clamp-side mirror of the budget validator) with a player-facing note;
  the guided magnitude verbs refuse explicit over-budget amounts arm-side
  with the binding constraint named in voice.
- G4L1-3: the per-court scroll viewport (190px) hid the second court and
  every ``Add demand`` affordance below the fold; the preamble now renders
  in the header and the viewport fits the court rows.
- G4F-5 (leg-2+ follow-up, June 11): the whole-table Harsher/More generous
  dial was a SILENT DEAD CLICK on a gold-free table — the sweep only tunes
  existing gold/territory lines, the seed was gated to focused
  (``len(scope) == 1``) dials on clause-less courts, and the multilateral
  smoke baseline authors no gold. Six Harsher clicks changed nothing,
  wordlessly ("Pressed the whole table." printed behind the modal popup).
  Fix: the dial seeds a modest gold clause on EVERY scoped court the sweep
  left unchanged and unnoted (budget/cap/leader-gated, cap break appends a
  note), and the ceiling/protection notes now ride the restaged dialogue as
  one-shot ``authoring_voice_beats`` (kind ``dial_note``) so the popup
  preamble renders them — the D3 never-wordless contract, in the popup the
  player is actually looking at.
"""

from __future__ import annotations

from backend.game_logic.diplomatic_templates import (
    calculate_raw_treaty_harshness,
)
from backend.game_logic.settlement_preview import (
    SETTLEMENT_DIAL_GOLD_STEP,
    handle_settlement_dialogue_action,
    stage_settlement_confirm,
)
from backend.game_logic.settlement_scoring import (
    MAX_SETTLEMENT_CLAUSE_COUNT,
    calculate_common_peace_acceptance,
    compute_settlement_package_raw_harshness,
)
from backend.game_logic.settlement_actions import (
    _dial_territory_escalation_candidates,
)
from backend.game_logic.settlement_staging import (
    _redial_settlement_terms,
)
from backend.models.world_state import WorldState
from tests.helpers.full_europe_settlement_fixtures import (
    make_synthetic_war_instance,
)

import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
GODOT_SCRIPTS = REPO_ROOT / "godot-client" / "project-sovereign" / "scripts"
GODOT_SCENES = REPO_ROOT / "godot-client" / "project-sovereign" / "scenes"


def _winning_two_court_world(
    *, france_gold=800, britain_gold=1500, prussia_gold=800,
):
    """France (attacker leader) beating Britain (defender leader) + Prussia
    in one shared war — the `settlement_multilateral` smoke shape."""
    world = WorldState()
    war = make_synthetic_war_instance(
        "war_1",
        attackers=["France"],
        defenders=["Britain", "Prussia"],
        attacker_leader="France",
        defender_leader="Britain",
        created_turn=1,
        created_sequence=1,
    )
    world.war_instances["war_1"] = war
    for opponent in ("Britain", "Prussia"):
        pair = "|".join(sorted(("France", opponent)))
        world.diplomatic_states[pair] = "WAR"
        first = pair.split("|")[0]
        world.war_scores[pair] = 60 if first == "France" else -60
    world.nation_gold = {
        "France": france_gold,
        "Britain": britain_gold,
        "Prussia": prussia_gold,
    }
    world.invalidate_war_instance_indexes()
    return world, war


def _stage_propose(world):
    staged = stage_settlement_confirm(
        world,
        war_id="war_1",
        actor_nation="France",
        selected_target_nation="Britain",
        covered_enemy_participants=["Britain", "Prussia"],
        caller_kind="player_editor",
        dialogue_mode="PROPOSE",
    )
    assert staged.get("success"), staged
    return staged["diplomatic_dialogue"]


def _gold_for(terms, payer):
    return sum(
        int(t.get("amount", 0) or 0)
        for t in terms
        if t.get("type") == "gold_indemnity" and t.get("from") == payer
    )


def _add_demand_gold(world, dialogue, court, amount):
    """Author a gold demand through the real GT-Slice-1 verb (the dial tests
    must not depend on what the tuned baseline happens to author)."""
    result = handle_settlement_dialogue_action(
        world,
        action="settlement_demand_add",
        dialogue=dialogue,
        action_params={
            "action": "settlement_demand_add",
            "nation": court,
            "clause_type": "gold_indemnity",
            "group": "demand",
            "amount": amount,
        },
    )
    assert result["success"] is True, result.get("error_display")
    return result["diplomatic_dialogue"]


def _row(dialogue, nation):
    for row in dialogue.get("per_court_acceptance") or []:
        if row.get("nation") == nation:
            return row
    raise AssertionError(f"no per-court row for {nation}")


# ═══════════════════════════════════════════════════════════════════════════
# G4F-1 — gold demands price into harshness; concessions stay credit-side
# ═══════════════════════════════════════════════════════════════════════════


class TestGoldPricing:
    def test_gold_demand_magnitude_moves_acceptance(self):
        """The frozen-63 class: demanding more gold from a court must lower
        that court's acceptance (0.08 raw per 100 gold — the existing
        bilateral gold weight, spec §6.acceptance line 1115)."""
        world, war = _winning_two_court_world()

        def score(amount):
            result = calculate_common_peace_acceptance(
                world,
                war_id="war_1",
                war_instance=war,
                proposer_side="attackers",
                accepting_side="defenders",
                accepting_leader="Britain",
                proposer_side_leader="France",
                covered_enemy_participants=["Britain", "Prussia"],
                settlement_terms=[
                    {"type": "peace"},
                    {
                        "type": "gold_indemnity",
                        "from": "Britain",
                        "to": "France",
                        "amount": amount,
                    },
                ],
            )
            return int(result["score"]), int(
                result["components"]["term_harshness_penalty"]
            )

        score_300, penalty_300 = score(300)
        score_900, penalty_900 = score(900)
        assert penalty_300 < 0, "gold demand must carry a harshness penalty"
        assert penalty_900 < penalty_300
        assert score_900 < score_300

    def test_proposer_paid_gold_excluded_from_harshness(self):
        """Direction partition: France-paid gold is concession_credit's job;
        pricing it as harshness would make a sweetener LOWER acceptance."""
        raw = compute_settlement_package_raw_harshness(
            [
                {"type": "peace"},
                {
                    "type": "gold_indemnity",
                    "from": "France",
                    "to": "Britain",
                    "amount": 1500,
                },
                {
                    "type": "territory_cede",
                    "from": "France",
                    "to": "Britain",
                    "region": "Waterloo",
                },
            ],
            proposer_side_participants=["France"],
        )
        assert raw == 0.0

    def test_accepting_side_burdens_priced(self):
        raw = compute_settlement_package_raw_harshness(
            [
                {"type": "peace"},
                {
                    "type": "gold_indemnity",
                    "from": "Britain",
                    "to": "France",
                    "amount": 500,
                },
                {
                    "type": "territory_cede",
                    "from": "Prussia",
                    "to": "France",
                    "region": "Berlin",
                },
            ],
            proposer_side_participants=["France"],
        )
        # 0.08 * 5 (gold) + 0.3 (region) = 0.7
        assert abs(raw - 0.7) < 1e-9

    def test_ratified_treaty_clauses_dialect_prices_settlement_shapes(self):
        """settlement_ratify records treaties via `{"clauses": pair_terms}` —
        the settlement clause shapes (gold_indemnity, singular `region`,
        vassalage) must price there too, or stored `raw_harshness` reads
        near-zero for every ledger / AI / coalition consumer."""
        raw = calculate_raw_treaty_harshness({
            "clauses": [
                {
                    "type": "gold_indemnity",
                    "from": "Britain",
                    "to": "France",
                    "amount": 500,
                },
                {
                    "type": "territory_cede",
                    "from": "Britain",
                    "to": "France",
                    "region": "London",
                },
                {"type": "vassalage", "from": "Prussia", "to": "France"},
            ]
        })
        # 0.4 (gold 500) + 0.3 (one region) + 0.5 (vassalage) = 1.2
        assert abs(raw - 1.2) < 1e-9

    def test_bilateral_clause_shapes_unchanged(self):
        """The bilateral dialect (regions list, perpetual gold_per_turn)
        keeps its existing sums — settlement aliases must not perturb
        bilateral acceptance."""
        raw = calculate_raw_treaty_harshness({
            "clauses": [
                {"type": "territory_cede", "regions": ["A", "B"]},
                {"type": "gold_per_turn", "amount": 100},
            ]
        })
        # 0.3 * 2 + 0.1 * 1 = 0.7 (unchanged legacy weights)
        assert abs(raw - 0.7) < 1e-9


# ═══════════════════════════════════════════════════════════════════════════
# G4F-2 — dial clamps + arm-level refusals (through the real handler shapes)
# ═══════════════════════════════════════════════════════════════════════════


class TestDialBudgetClamp:
    def test_harsher_dial_moves_scores_and_clamps_at_payer_balance(self):
        """Pressing the table repeatedly: scores MOVE (no more frozen 63),
        gold never exceeds the payer's capacity, the ceiling press says so
        in voice, and no click ever bounces off the restage validator."""
        world, _war = _winning_two_court_world(prussia_gold=800)
        dialogue = _stage_propose(world)
        dialogue = _add_demand_gold(world, dialogue, "Prussia", 300)
        dialogue = _add_demand_gold(world, dialogue, "Britain", 300)
        prussia_score_before = _row(dialogue, "Prussia").get("total")

        saw_cap_note = False
        for _ in range(12):
            result = handle_settlement_dialogue_action(
                world,
                action="settlement_dial_harsher",
                dialogue=dialogue,
                action_params={
                    "action": "settlement_dial_harsher",
                    "scope": "table",
                },
            )
            assert result["success"] is True, result.get("error_display")
            assert result.get("error") != "submitted_terms_failed_revalidation"
            dialogue = result["diplomatic_dialogue"]
            terms = dialogue.get("settlement_terms") or []
            assert _gold_for(terms, "Prussia") <= 800
            assert _gold_for(terms, "Britain") <= 1500
            if "can pay no more" in str(result.get("message") or ""):
                saw_cap_note = True
        assert saw_cap_note, "the ceiling press must say so, not silently no-op"
        prussia_score_after = _row(dialogue, "Prussia").get("total")
        assert prussia_score_after is not None
        assert prussia_score_after < prussia_score_before, (
            "G4F-1: pressed gold must move the pressed court's score"
        )

    def test_focused_press_on_broke_court_never_authors_gold(self):
        """A focused press on a court with no slice and no treasury never
        authors an unpayable gold demand (G4F-2). GT-A5: the exhausted gold
        lever now escalates into the court's suggested TERRITORY demand —
        the press still moves the needle, just not in coin — and the pivot
        is voiced; a SECOND press (territory already escalated) falls back
        to the ceiling note."""
        world, _war = _winning_two_court_world(prussia_gold=0)
        dialogue = _stage_propose(world)
        # Strike every Prussia-touching material clause so the focused press
        # finds no slice and reaches the seed path.
        terms = [
            t for t in (dialogue.get("settlement_terms") or [])
            if not (
                t.get("from") == "Prussia" or t.get("to") == "Prussia"
            )
        ]
        refreshed = dict(dialogue)
        refreshed["settlement_terms"] = terms
        world.dialogue_manager.replace(refreshed)
        result = handle_settlement_dialogue_action(
            world,
            action="settlement_dial_harsher",
            dialogue=refreshed,
            action_params={
                "action": "settlement_dial_harsher",
                "scope": "Prussia",
            },
        )
        assert result["success"] is True, result.get("error_display")
        new_terms = result["diplomatic_dialogue"].get("settlement_terms") or []
        assert _gold_for(new_terms, "Prussia") == 0
        prussia_territory = [
            t for t in new_terms
            if str(t.get("type") or "").startswith("territory")
            and t.get("from") == "Prussia"
        ]
        assert len(prussia_territory) == 1, new_terms
        assert prussia_territory[0].get("authored_by") == "talleyrand"
        assert "asked for land" in str(result.get("message") or "")

        # Second press: gold still unfundable, territory already escalated —
        # the once-per-court-per-direction guard holds and the click falls
        # back to the D3 ceiling note (never a second land grab, never
        # wordless).
        second = handle_settlement_dialogue_action(
            world,
            action="settlement_dial_harsher",
            dialogue=result["diplomatic_dialogue"],
            action_params={
                "action": "settlement_dial_harsher",
                "scope": "Prussia",
            },
        )
        assert second["success"] is True, second.get("error_display")
        second_terms = second["diplomatic_dialogue"].get("settlement_terms") or []
        assert _gold_for(second_terms, "Prussia") == 0
        assert len([
            t for t in second_terms
            if str(t.get("type") or "").startswith("territory")
            and t.get("from") == "Prussia"
        ]) == 1
        assert "can pay no more" in str(second.get("message") or "")


class TestMagnitudeBudgetRefusals:
    def _staged_with_prussia_gold_line(self, world):
        dialogue = _stage_propose(world)
        dialogue = _add_demand_gold(world, dialogue, "Prussia", 300)
        row = _row(dialogue, "Prussia")
        for line in row.get("current_demands") or []:
            action = line.get("set_magnitude_action") or {}
            params = dict(action.get("action_params") or {})
            if params.get("clause_index") is not None and (
                str(params.get("expected_type") or "") == "gold_indemnity"
            ):
                return dialogue, params
        raise AssertionError("no Prussia gold line with a magnitude action")

    def test_set_magnitude_over_balance_refused_in_voice(self):
        world, _war = _winning_two_court_world(prussia_gold=800)
        dialogue, params = self._staged_with_prussia_gold_line(world)
        params["amount"] = 900
        result = handle_settlement_dialogue_action(
            world,
            action="settlement_demand_set_magnitude",
            dialogue=dialogue,
            action_params=params,
        )
        assert result["success"] is False
        assert result["error"] == "gold_payment_budget_conflict"
        display = str(result.get("error_display") or "")
        assert "Sire" in display
        assert "Prussia" in display
        assert "review and correct them" not in display
        # CH-5: the failure re-attaches the mounted dialogue.
        assert result.get("diplomatic_dialogue")

    def test_set_magnitude_at_balance_succeeds(self):
        world, _war = _winning_two_court_world(prussia_gold=800)
        dialogue, params = self._staged_with_prussia_gold_line(world)
        params["amount"] = 800
        result = handle_settlement_dialogue_action(
            world,
            action="settlement_demand_set_magnitude",
            dialogue=dialogue,
            action_params=params,
        )
        assert result["success"] is True, result.get("error_display")
        terms = result["diplomatic_dialogue"].get("settlement_terms") or []
        assert _gold_for(terms, "Prussia") == 800

    def test_demand_add_explicit_over_balance_refused_in_voice(self):
        world, _war = _winning_two_court_world(prussia_gold=800)
        dialogue = _stage_propose(world)
        result = handle_settlement_dialogue_action(
            world,
            action="settlement_demand_add",
            dialogue=dialogue,
            action_params={
                "action": "settlement_demand_add",
                "nation": "Prussia",
                "clause_type": "gold_indemnity",
                "group": "demand",
                "amount": 2000,
            },
        )
        assert result["success"] is False
        assert result["error"] == "gold_payment_budget_conflict"
        display = str(result.get("error_display") or "")
        assert "Sire" in display and "Prussia" in display
        assert result.get("diplomatic_dialogue")


# ═══════════════════════════════════════════════════════════════════════════
# G4F-4 — bare action-id `choice` resolves exactly (the wire's verb shape)
# ═══════════════════════════════════════════════════════════════════════════


class TestChoiceActionIdResolution:
    def test_bare_action_id_choice_resolves_to_option(self):
        """The fuzzy keyword matcher cannot see underscored action ids
        ("submit_settlement_for_review" matches no label substring), which is
        how per-id carve-outs like `suspend_settlement_editor` accreted.
        Exact action-id equality resolves the wire's verb before any fuzzy
        pass — through the real dialogue-response entry point."""
        from backend.commands.diplomatic_executor import DiplomaticExecutor

        world, _war = _winning_two_court_world()
        _stage_propose(world)
        result = DiplomaticExecutor(None).handle_diplomatic_dialogue_response(
            "submit_settlement_for_review", {"world": world}
        )
        assert result.get("success") is True, result.get("message")
        assert "I don't understand" not in str(result.get("message") or "")
        refreshed = world.pending_diplomatic_dialogue
        assert refreshed is not None
        assert refreshed.get("dialogue_mode") == "REVIEW"


# ═══════════════════════════════════════════════════════════════════════════
# G4F-3 — the guided surface is not hidden below the scroll fold
# ═══════════════════════════════════════════════════════════════════════════


class TestPerCourtViewport:
    def test_preamble_renders_in_header_not_inside_scroll(self):
        text = (GODOT_SCRIPTS / "proposal_confirm_popup.gd").read_text(
            encoding="utf-8"
        )
        assert "func _build_settlement_table_preamble" in text
        assert "_build_settlement_table_preamble(data)" in text
        # The scrollable block starts at the table itself — the treasury /
        # narration preamble must NOT consume scroll viewport height.
        block = text.split("func _build_settlement_per_court_block", 1)[1]
        block = block.split("\nfunc ", 1)[0]
        assert "treasury_line" not in block
        assert "multi_court_table_narration" not in block
        assert "The table" in block

    def test_scroll_viewport_fits_multiple_court_rows(self):
        scene = (GODOT_SCENES / "proposal_confirm_popup.tscn").read_text(
            encoding="utf-8"
        )
        scroll_chunk = scene.split('[node name="PerCourtScroll"', 1)[1]
        scroll_chunk = scroll_chunk.split("[node", 1)[0]
        assert "custom_minimum_size = Vector2(0, 320)" in scroll_chunk


# ═══════════════════════════════════════════════════════════════════════════
# G4F-5 — the whole-table dial is never a silent dead click
# ═══════════════════════════════════════════════════════════════════════════


def _strip_to_peace_only(world, dialogue):
    """Replace the staged draft's terms with the bare shared peace clause —
    the live leg-2 smoke shape (the tuned multilateral baseline authored no
    gold, so the whole-table sweep had nothing to tune)."""
    refreshed = dict(dialogue)
    refreshed["settlement_terms"] = [{"type": "peace"}]
    world.dialogue_manager.replace(refreshed)
    return refreshed


class TestWholeTableDialSeedsUnpressedCourts:
    def test_whole_table_harsher_seeds_every_unpressed_court(self):
        """The live dead click: peace + a kept territory demand, no gold.
        Pre-fix the whole-table sweep changed nothing (territory demands are
        KEPT on harsher, the seed was focused-only) — now every scoped court
        without a material delta gets the modest seed."""
        terms = [
            {"type": "peace"},
            {
                "type": "territory_cede",
                "from": "Britain",
                "to": "France",
                "region": "Netherlands",
            },
        ]
        out = _redial_settlement_terms(
            terms=terms,
            scope_courts=["Britain", "Prussia"],
            direction="harsher",
            proposer_side_leader="France",
        )
        # The kept territory demand survives untouched (identity is Tier 3).
        terr = [t for t in out if t.get("type") == "territory_cede"]
        assert len(terr) == 1 and terr[0]["region"] == "Netherlands"
        # BOTH courts now carry a pressed gold demand — the click moved the
        # needle for every court the label claims to press.
        for court in ("Britain", "Prussia"):
            seeds = [
                t for t in out
                if t.get("type") == "gold_indemnity" and t.get("from") == court
            ]
            assert len(seeds) == 1, f"no seed for {court}: {out}"
            assert seeds[0]["to"] == "France"
            assert seeds[0]["amount"] == SETTLEMENT_DIAL_GOLD_STEP

    def test_repeat_whole_table_clicks_accumulate(self):
        """Click 2 grows what click 1 seeded — repeated presses escalate
        instead of re-producing the same package."""
        terms = [{"type": "peace"}]
        first = _redial_settlement_terms(
            terms=terms,
            scope_courts=["Britain", "Prussia"],
            direction="harsher",
            proposer_side_leader="France",
        )
        second = _redial_settlement_terms(
            terms=first,
            scope_courts=["Britain", "Prussia"],
            direction="harsher",
            proposer_side_leader="France",
        )
        for court in ("Britain", "Prussia"):
            gold = [
                t for t in second
                if t.get("type") == "gold_indemnity" and t.get("from") == court
            ]
            assert len(gold) == 1
            assert gold[0]["amount"] == 2 * SETTLEMENT_DIAL_GOLD_STEP

    def test_focused_press_on_territory_only_court_seeds_gold(self):
        """A focused Press on a court whose only slice is a KEPT territory
        demand was equally dead pre-fix (the court counted as touched, so the
        seed never fired). Unchanged-and-unnoted is the seed condition now."""
        terms = [
            {"type": "peace"},
            {
                "type": "territory_cede",
                "from": "Prussia",
                "to": "France",
                "region": "Silesia",
            },
        ]
        out = _redial_settlement_terms(
            terms=terms,
            scope_courts=["Prussia"],
            direction="harsher",
            proposer_side_leader="France",
        )
        gold = [
            t for t in out
            if t.get("type") == "gold_indemnity" and t.get("from") == "Prussia"
        ]
        assert len(gold) == 1 and gold[0]["amount"] == SETTLEMENT_DIAL_GOLD_STEP
        assert any(t.get("region") == "Silesia" for t in out)

    def test_whole_table_generous_eases_every_court_across_clicks(self):
        """The generous mirror: click 1 drops the suggested demand (that IS
        Britain's delta) and seeds a proposer concession to clause-less
        Prussia; click 2 seeds the now clause-less Britain and grows
        Prussia's concession."""
        terms = [
            {"type": "peace"},
            {
                "type": "territory_cede",
                "from": "Britain",
                "to": "France",
                "region": "Netherlands",
            },
        ]
        first = _redial_settlement_terms(
            terms=terms,
            scope_courts=["Britain", "Prussia"],
            direction="generous",
            proposer_side_leader="France",
        )
        # The suggested territory demand dropped; no Britain seed on the same
        # click (the drop is Britain's material delta).
        assert not any(t.get("type") == "territory_cede" for t in first)
        assert not any(t.get("to") == "Britain" for t in first)
        prussia = [t for t in first if t.get("to") == "Prussia"]
        assert len(prussia) == 1
        assert prussia[0]["from"] == "France"
        assert prussia[0]["amount"] == SETTLEMENT_DIAL_GOLD_STEP

        second = _redial_settlement_terms(
            terms=first,
            scope_courts=["Britain", "Prussia"],
            direction="generous",
            proposer_side_leader="France",
        )
        britain = [t for t in second if t.get("to") == "Britain"]
        assert len(britain) == 1
        assert britain[0]["amount"] == SETTLEMENT_DIAL_GOLD_STEP
        prussia2 = [t for t in second if t.get("to") == "Prussia"]
        assert prussia2[0]["amount"] == 2 * SETTLEMENT_DIAL_GOLD_STEP

    def test_capped_package_notes_instead_of_silent_break(self):
        """At MAX_SETTLEMENT_CLAUSE_COUNT the seed loop must SAY it has no
        room (the D3 never-wordless contract) — not break silently."""
        terms = [{"type": "peace"}]
        i = 0
        while len(terms) < MAX_SETTLEMENT_CLAUSE_COUNT:
            terms.append({
                "type": "gold_indemnity",
                "from": "Britain",
                "to": "France",
                "amount": 1500,  # at the hard cap — presses note, not grow
            })
            i += 1
        notes: list = []
        out = _redial_settlement_terms(
            terms=terms,
            scope_courts=["Britain", "Prussia"],
            direction="harsher",
            proposer_side_leader="France",
            protected_notes=notes,
        )
        # No over-cap seed for clause-less Prussia...
        assert len(out) == MAX_SETTLEMENT_CLAUSE_COUNT
        assert not any(t.get("from") == "Prussia" for t in out)
        # ...and the refusal is named, never wordless.
        assert any("no further terms" in n for n in notes), notes


class TestDialFeedbackReachesThePopup:
    def test_whole_table_press_on_peace_only_draft_moves_terms_live(self):
        """The exact live repro, through the real handler + real scorer: a
        peace-only PROPOSE draft, one whole-table press → both courts carry
        a gold demand and the response restages the dialogue."""
        world, _war = _winning_two_court_world()
        dialogue = _stage_propose(world)
        refreshed = _strip_to_peace_only(world, dialogue)
        result = handle_settlement_dialogue_action(
            world,
            action="settlement_dial_harsher",
            dialogue=refreshed,
            action_params={
                "action": "settlement_dial_harsher",
                "scope": "table",
            },
        )
        assert result["success"] is True, result.get("error_display")
        terms = result["diplomatic_dialogue"].get("settlement_terms") or []
        assert _gold_for(terms, "Britain") == SETTLEMENT_DIAL_GOLD_STEP
        assert _gold_for(terms, "Prussia") == SETTLEMENT_DIAL_GOLD_STEP

    def test_ceiling_feedback_rides_the_restaged_dialogue_as_voice_beats(self):
        """G4F-5b: `message` prints to the terminal BEHIND the modal popup,
        so ceiling feedback must ride the restaged dialogue as one-shot
        `authoring_voice_beats` — the carrier the popup preamble renders.
        Click 1: the broke court ESCALATES (GT-A5) and the pivot is a
        `talleyrand_line` beat. Click 2: escalation exhausted — the D3
        ceiling note arrives as a `dial_note` beat."""
        world, _war = _winning_two_court_world(prussia_gold=0)
        dialogue = _stage_propose(world)
        refreshed = _strip_to_peace_only(world, dialogue)
        result = handle_settlement_dialogue_action(
            world,
            action="settlement_dial_harsher",
            dialogue=refreshed,
            action_params={
                "action": "settlement_dial_harsher",
                "scope": "table",
            },
        )
        assert result["success"] is True, result.get("error_display")
        new_dialogue = result["diplomatic_dialogue"]
        # Britain (funded) seeded gold; Prussia (broke) escalated to land.
        terms = new_dialogue.get("settlement_terms") or []
        assert _gold_for(terms, "Britain") == SETTLEMENT_DIAL_GOLD_STEP
        assert _gold_for(terms, "Prussia") == 0
        assert any(
            str(t.get("type") or "").startswith("territory")
            and t.get("from") == "Prussia"
            for t in terms
        )
        beats = new_dialogue.get("authoring_voice_beats") or []
        escalation_lines = [
            str(b.get("line") or "")
            for b in beats
            if b.get("kind") == "talleyrand_line"
        ]
        assert any("asked for land" in line for line in escalation_lines), (
            f"the escalation must reach the popup, got beats: {beats}"
        )

        # Click 2: Prussia's gold is still unfundable and its territory is
        # already escalated — the ceiling NOTE now reaches the popup as a
        # `dial_note` beat (the original G4F-5b contract).
        second = handle_settlement_dialogue_action(
            world,
            action="settlement_dial_harsher",
            dialogue=new_dialogue,
            action_params={
                "action": "settlement_dial_harsher",
                "scope": "table",
            },
        )
        assert second["success"] is True, second.get("error_display")
        second_dialogue = second["diplomatic_dialogue"]
        note_lines = [
            str(b.get("line") or "")
            for b in (second_dialogue.get("authoring_voice_beats") or [])
            if b.get("kind") == "dial_note"
        ]
        assert any("Prussia can pay no more" in line for line in note_lines), (
            "the ceiling note must reach the popup once escalation is "
            f"exhausted, got: {second_dialogue.get('authoring_voice_beats')}"
        )
        # The terminal message still carries it too.
        assert "Prussia can pay no more" in str(second.get("message") or "")


# ═══════════════════════════════════════════════════════════════════════════
# G4F-6 — the pre-proposal objection judges the DISPLAYED terms
# (live smoke: "such generous terms... rewards their failure" on a
# PUNITIVE / REJECT bilateral preview — the objection stub was empty)
# ═══════════════════════════════════════════════════════════════════════════


class TestObjectionJudgesDisplayedTerms:
    def _world_with_winning_war(self):
        world, _war = _winning_two_court_world()
        return world

    def test_no_too_generous_line_when_displayed_terms_are_harsh(self):
        from backend.game_logic.diplomatic_dialogue import (
            _merge_pre_proposal_objection,
        )

        world = self._world_with_winning_war()
        dialogue = {
            "options": [{
                "action": "execute_proposal",
                "terms": {
                    "type": "peace",
                    "demands": [
                        {"type": "gold_per_turn", "value": 200},
                        {"type": "territory_cede", "value": 1},
                    ],
                    "sweeteners": [],
                },
            }],
        }
        merged = _merge_pre_proposal_objection(
            dict(dialogue),
            {"proposal_type": "peace", "target_nation": "Britain", "clauses": []},
            world,
        )
        import json as _json

        assert "rewards their failure" not in _json.dumps(merged)

    def test_too_generous_line_still_fires_on_genuinely_light_terms(self):
        from backend.game_logic.diplomatic_dialogue import (
            _merge_pre_proposal_objection,
        )

        world = self._world_with_winning_war()
        dialogue = {
            "talleyrand_text": "",
            "options": [{
                "action": "execute_proposal",
                "terms": {
                    "type": "peace",
                    "demands": [],
                    "sweeteners": [{"type": "gold_lump", "value": 100}],
                },
            }],
        }
        merged = _merge_pre_proposal_objection(
            dict(dialogue),
            {"proposal_type": "peace", "target_nation": "Britain", "clauses": []},
            world,
        )
        import json as _json

        assert "rewards their failure" in _json.dumps(merged)


# ═══════════════════════════════════════════════════════════════════════════
# G4F-7 — the full-deal carry verdict is loud, attributed, and honest
# (live smoke: two "Near acceptable" chips at 44/35 read as "net terms
# acceptable" while BOTH courts were blocking holdouts)
# ═══════════════════════════════════════════════════════════════════════════


class TestCarryVerdictPresentation:
    def test_band_chips_are_threshold_honest(self):
        from backend.display_names import acceptance_band_display

        assert acceptance_band_display("accept") == "Will sign"
        assert acceptance_band_display("near_acceptable") == "Holding out (close)"
        assert acceptance_band_display("reject") == "Holding out"
        # The word "acceptable" never appears on a blocking band again.
        assert "acceptable" not in acceptance_band_display("near_acceptable").lower()

    def test_blocked_verdict_names_every_holdout_with_scores(self):
        world, _war = _winning_two_court_world()
        dialogue = _stage_propose(world)
        overall = dialogue.get("overall_acceptance") or {}
        verdict = str(overall.get("carry_verdict_display") or "")
        assert verdict.startswith("Will NOT carry as drafted"), verdict
        assert "must reach 50" in verdict
        rows = {
            r["nation"]: r for r in dialogue.get("per_court_acceptance") or []
        }
        for holdout in overall.get("holdout_courts") or []:
            row = rows[holdout]
            assert f"{holdout} {int(row['total'])}/{int(row['threshold'])}" in verdict

    def test_carrying_verdict_states_the_pass(self):
        world, _war = _winning_two_court_world()
        dialogue = _stage_propose(world)
        result = handle_settlement_dialogue_action(
            world,
            action="settlement_dial_generous",
            dialogue=dialogue,
            action_params={
                "action": "settlement_dial_generous", "scope": "table",
            },
        )
        assert result["success"] is True, result.get("error_display")
        overall = result["diplomatic_dialogue"].get("overall_acceptance") or {}
        if overall.get("carries"):
            verdict = str(overall.get("carry_verdict_display") or "")
            assert verdict.startswith("Will carry as drafted"), verdict
            assert "at or above 50" in verdict

    def test_settlement_label_names_every_covered_court(self):
        world, _war = _winning_two_court_world()
        dialogue = _stage_propose(world)
        assert dialogue.get("war_label") == "France vs Britain + Prussia"
        # The blocked copy now reads "the settlement of France vs
        # Britain + Prussia ..." — the leader-pair label fed the
        # "Britain-only" misreading.
        result = handle_settlement_dialogue_action(
            world,
            action="submit_settlement_for_review",
            dialogue=dialogue,
            action_params={"action": "submit_settlement_for_review"},
        )
        assert result["success"] is True, result.get("error_display")
        assert "Britain + Prussia" in str(result.get("message") or "")

    def test_popup_header_leads_with_the_carry_verdict(self):
        text = (GODOT_SCRIPTS / "proposal_confirm_popup.gd").read_text(
            encoding="utf-8"
        )
        preamble = text.split("func _build_settlement_table_preamble", 1)[1]
        preamble = preamble.split("\nfunc ", 1)[0]
        assert "carry_verdict_display" in preamble
        # The verdict renders BEFORE the treasury line (header lead).
        assert preamble.index("carry_verdict_display") < preamble.index(
            "treasury_line"
        )

    def test_popup_rows_use_threshold_framing(self):
        text = (GODOT_SCRIPTS / "proposal_confirm_popup.gd").read_text(
            encoding="utf-8"
        )
        block = text.split("func _build_settlement_per_court_block", 1)[1]
        block = block.split("\nfunc ", 1)[0]
        assert '" (%d/%d)" % [int(total), int(row.get("threshold", 50))]' in block

    def test_footer_lead_court_score_suppressed_on_per_court_table(self):
        """G4F-12: the footer 'Acceptance' block is the LEAD COURT's score,
        not a deal aggregate — on the per-court table it duplicated one row
        and could contradict the header carry verdict. It renders only when
        no per-court rows exist."""
        text = (GODOT_SCRIPTS / "proposal_confirm_popup.gd").read_text(
            encoding="utf-8"
        )
        block = text.split("func _build_settlement_footer", 1)[1]
        block = block.split("\nfunc ", 1)[0]
        assert "has_per_court_rows" in block
        assert "not has_per_court_rows and acceptance is Dictionary" in block


# ═══════════════════════════════════════════════════════════════════════════
# G4F-8 — the pair substitute is a confirmed handoff that carries terms
# (live smoke: "Make peace with Britain only" read as a verdict; one click
# silently discarded the authored joint draft and opened the bilateral
# engine with fresh auto-terms)
# ═══════════════════════════════════════════════════════════════════════════


def _blocked_review_with_authored_gold(world, court="Britain", amount=300):
    dialogue = _stage_propose(world)
    dialogue = _add_demand_gold(world, dialogue, court, amount)
    result = handle_settlement_dialogue_action(
        world,
        action="submit_settlement_for_review",
        dialogue=dialogue,
        action_params={"action": "submit_settlement_for_review"},
    )
    assert result["success"] is True, result.get("error_display")
    review = result["diplomatic_dialogue"]
    assert review.get("dialogue_mode") == "REVIEW"
    return review


class TestPairSubstituteConfirmStep:
    def test_substitute_click_mounts_chooser_and_keeps_draft(self):
        from backend.game_logic.settlement_preview import (
            load_scoped_settlement_draft,
        )

        world, _war = _winning_two_court_world()
        review = _blocked_review_with_authored_gold(world)
        result = handle_settlement_dialogue_action(
            world,
            action="seek_bilateral_peace",
            dialogue=review,
            action_params={"action": "seek_bilateral_peace"},
        )
        assert result["success"] is True, result.get("error_display")
        chooser = result["diplomatic_dialogue"]
        assert chooser["type"] == "settlement_pair_substitute_confirm"
        assert [o["action"] for o in chooser["options"]] == [
            "confirm_pair_substitute", "keep_joint_settlement",
        ]
        assert isinstance(chooser.get("prior_dialogue"), dict)
        # The joint draft is UNTOUCHED until Proceed.
        kept = load_scoped_settlement_draft(
            world,
            war_id="war_1",
            selected_target_nation=str(
                review.get("selected_target_nation") or ""
            ),
            covered_enemy_participants=list(
                review.get("covered_enemy_participants") or []
            ),
        )
        assert kept, "the scoped draft must survive the chooser mount"

    def test_keep_restores_the_review_unchanged(self):
        world, _war = _winning_two_court_world()
        review = _blocked_review_with_authored_gold(world)
        chooser = handle_settlement_dialogue_action(
            world,
            action="seek_bilateral_peace",
            dialogue=review,
            action_params={"action": "seek_bilateral_peace"},
        )["diplomatic_dialogue"]
        result = handle_settlement_dialogue_action(
            world,
            action="keep_joint_settlement",
            dialogue=chooser,
            action_params={"action": "keep_joint_settlement"},
        )
        assert result["success"] is True, result.get("error_display")
        restored = result["diplomatic_dialogue"]
        assert restored.get("dialogue_mode") == "REVIEW"
        assert restored.get("settlement_terms") == review.get("settlement_terms")
        assert world.pending_diplomatic_dialogue.get("dialogue_mode") == "REVIEW"

    def test_confirm_discards_draft_and_seeds_bilateral_from_authored_slice(self):
        from backend.game_logic.settlement_preview import (
            load_scoped_settlement_draft,
        )

        world, _war = _winning_two_court_world()
        review = _blocked_review_with_authored_gold(world, amount=300)
        staged_terms = list(review.get("settlement_terms") or [])
        chooser = handle_settlement_dialogue_action(
            world,
            action="seek_bilateral_peace",
            dialogue=review,
            action_params={"action": "seek_bilateral_peace"},
        )["diplomatic_dialogue"]
        result = handle_settlement_dialogue_action(
            world,
            action="confirm_pair_substitute",
            dialogue=chooser,
            action_params={"action": "confirm_pair_substitute"},
        )
        assert result["success"] is True, result.get("error_display")
        assert result.get("draft_invalidated") is True
        assert not load_scoped_settlement_draft(
            world,
            war_id="war_1",
            selected_target_nation=str(
                review.get("selected_target_nation") or ""
            ),
            covered_enemy_participants=list(
                review.get("covered_enemy_participants") or []
            ),
        )
        bilateral = result["diplomatic_dialogue"]
        assert bilateral.get("carried_from_settlement") is True
        terms = {}
        for opt in bilateral.get("options", []):
            if opt.get("action") == "execute_proposal" and opt.get("terms"):
                terms = opt["terms"]
                break
        demands = terms.get("demands") or []
        # The authored 300-gold demand on Britain travels as a lump.
        assert {"type": "gold_lump", "value": 300} in demands
        # A staged Britain territory demand travels as an aggregated
        # regions clause.
        staged_regions = [
            str(t.get("region"))
            for t in staged_terms
            if t.get("type") == "territory_cede" and t.get("from") == "Britain"
        ]
        if staged_regions:
            terr = [d for d in demands if d.get("type") == "territory_cede"]
            assert terr and sorted(terr[0].get("regions") or []) == sorted(
                staged_regions
            )

    def test_chooser_blocks_stray_table_actions(self):
        world, _war = _winning_two_court_world()
        review = _blocked_review_with_authored_gold(world)
        chooser = handle_settlement_dialogue_action(
            world,
            action="seek_bilateral_peace",
            dialogue=review,
            action_params={"action": "seek_bilateral_peace"},
        )["diplomatic_dialogue"]
        stray = handle_settlement_dialogue_action(
            world,
            action="settlement_dial_harsher",
            dialogue=chooser,
            action_params={"action": "settlement_dial_harsher", "scope": "table"},
        )
        assert stray["success"] is False
        assert stray["error"] == "unknown_settlement_action"

    def test_seed_transform_speaks_the_bilateral_dialect(self):
        from backend.game_logic.settlement_actions import (
            _pair_substitute_seed_terms,
        )

        seed = _pair_substitute_seed_terms(
            [
                {"type": "peace"},
                {"type": "gold_indemnity", "from": "Britain", "to": "France",
                 "amount": 400},
                {"type": "gold_per_turn", "from": "Britain", "to": "France",
                 "amount": 100, "turns": 3},
                {"type": "territory_cede", "from": "Britain", "to": "France",
                 "region": "Waterloo"},
                {"type": "territory_cede", "from": "Britain", "to": "France",
                 "region": "Hanover"},
                {"type": "gold_indemnity", "from": "France", "to": "Britain",
                 "amount": 200},
                {"type": "vassalage", "from": "Britain", "to": "France"},
                {"type": "gold_indemnity", "from": "Prussia", "to": "France",
                 "amount": 999},  # other court — never carried
            ],
            target="Britain",
            proposer_leader="France",
        )
        assert {"type": "gold_lump", "value": 400} in seed["demands"]
        # Finite stream converts by TOTAL obligation (the bilateral
        # recurring dialect is perpetual).
        assert {"type": "gold_lump", "value": 300} in seed["demands"]
        terr = [d for d in seed["demands"] if d.get("type") == "territory_cede"]
        assert len(terr) == 1
        assert sorted(terr[0]["regions"]) == ["Hanover", "Waterloo"]
        assert terr[0]["value"] == 2
        assert {"type": "gold_lump", "value": 200} in seed["sweeteners"]
        # Identity-bearing and other-court clauses never travel.
        assert not any(d.get("type") == "vassalage" for d in seed["demands"])
        assert not any(d.get("value") == 999 for d in seed["demands"])


# ═══════════════════════════════════════════════════════════════════════════
# G4F-9 — Talleyrand never suggests a package his own estimator rejects
# (live smoke: suggested 200/turn + Waterloo scored 3/REJECT while the
# assessment read PUNITIVE and the commentary claimed the terms fit)
# ═══════════════════════════════════════════════════════════════════════════


class TestSuggestEstimateConvergence:
    def test_suggested_peace_terms_never_self_reject(self):
        from backend.game_logic.diplomacy import calculate_acceptance
        from backend.game_logic.diplomatic_templates import (
            generate_suggested_terms,
        )

        world, _war = _winning_two_court_world()
        suggested = generate_suggested_terms("Britain", "peace", world)
        proposal = {
            "type": suggested.get("type", "peace"),
            "proposer_nation": "France",
            "target_nation": "Britain",
            "demands": suggested.get("demands", []),
            "sweeteners": suggested.get("sweeteners", []),
            "clauses": suggested.get("clauses", []),
        }
        result = calculate_acceptance(proposal, world)
        assert str(result.get("verdict")) != "REJECT", (
            suggested, result.get("score"),
        )

    def test_easing_ladder_drops_territory_before_gold(self):
        # At the smoke fixture the raw suggestion (recurring gold + a
        # region) REJECTS; gold alone counters. The ladder must land on
        # the gold rung, not over-ease to white peace.
        from backend.game_logic.diplomatic_templates import (
            generate_suggested_terms,
        )

        world, _war = _winning_two_court_world()
        suggested = generate_suggested_terms("Britain", "peace", world)
        if suggested.get("suggestion_eased_to_estimate"):
            demands = suggested.get("demands") or []
            assert demands, "eased to white peace despite a viable gold rung"
            assert not any(
                d.get("type") in ("territory_cede", "territory")
                for d in demands
            )


# ═══════════════════════════════════════════════════════════════════════════
# G4F-11 — the ratification event names amounts, regions, and the full table
# (term-reflection audit: the dispatch line and the recent-settlements
# record read "Settlement of France vs Britain: Gold indemnity:
# Britain→France" — leader-pair label, no amount, no region name)
# ═══════════════════════════════════════════════════════════════════════════


class TestRatificationEventRichness:
    def test_settlement_summary_carries_rich_terms_and_full_sides_label(self):
        world, _war = _winning_two_court_world()
        dialogue = _stage_propose(world)
        # Ease once so the package carries (real scorer), then submit and
        # ratify through the live handler chain.
        eased = handle_settlement_dialogue_action(
            world,
            action="settlement_dial_generous",
            dialogue=dialogue,
            action_params={
                "action": "settlement_dial_generous", "scope": "table",
            },
        )
        assert eased["success"] is True
        review = handle_settlement_dialogue_action(
            world,
            action="submit_settlement_for_review",
            dialogue=eased["diplomatic_dialogue"],
            action_params={"action": "submit_settlement_for_review"},
        )
        assert review["success"] is True
        overall = review["diplomatic_dialogue"].get("overall_acceptance") or {}
        assert overall.get("carries"), overall
        ratified = handle_settlement_dialogue_action(
            world,
            action="confirm_settlement",
            dialogue=review["diplomatic_dialogue"],
            action_params={"action": "confirm_settlement"},
        )
        assert ratified["success"] is True, ratified.get("error_display")
        summaries = [
            e for e in world.event_log
            if e.get("type") == "settlement_summary"
        ]
        assert summaries, world.event_log
        event = summaries[-1]
        # Full-sides label — never the first-vs-first pair form.
        assert event.get("war_label") == "France vs Britain + Prussia"
        lines = [str(line) for line in event.get("terms_summary") or []]
        assert lines
        # Rich formatter: a gold line names its amount and direction; the
        # thin "type: from→to" form named neither.
        gold_lines = [ln for ln in lines if "gold" in ln.lower()]
        if gold_lines:
            assert any("gold from" in ln for ln in gold_lines), lines
        # No thin arrow-form remnants.
        assert not any("→" in ln and " from " not in ln for ln in lines), lines


# ═══════════════════════════════════════════════════════════════════════════
# GT-A5 (GT-Slice-5) — ceiling-triggered territory escalation
# (user-approved June 11, 2026: the OQ#7 crossing — spec §3.5 GT-A5)
# ═══════════════════════════════════════════════════════════════════════════


class TestDialTerritoryEscalation:
    def test_press_at_gold_cap_escalates_once_then_notes(self):
        """The bilateral modify_harsh ladder on the settlement table: a
        court whose gold grow is exhausted authors its candidate territory
        demand ONCE; with the candidate consumed the next press falls back
        to the ceiling note."""
        terms = [
            {"type": "peace"},
            {
                "type": "gold_indemnity", "from": "Prussia", "to": "France",
                "amount": 500,
            },
        ]
        events: list = []
        notes: list = []
        out = _redial_settlement_terms(
            terms=terms,
            scope_courts=["Prussia"],
            direction="harsher",
            proposer_side_leader="France",
            protected_notes=notes,
            seeded_events=events,
            payer_gold_budgets={"Prussia": 500},  # grow blocked at 500
            territory_escalations={
                "Prussia": {
                    "type": "territory_cede", "from": "Prussia",
                    "to": "France", "region": "Silesia",
                    "authored_by": "talleyrand",
                },
            },
        )
        terr = [t for t in out if t.get("type") == "territory_cede"]
        assert len(terr) == 1 and terr[0]["region"] == "Silesia"
        assert terr[0]["authored_by"] == "talleyrand"
        # Gold held at the budget — never grown past capacity.
        gold = next(t for t in out if t.get("type") == "gold_indemnity")
        assert gold["amount"] == 500
        assert [e for e in events if e.get("kind") == "territory_escalation"]
        assert not notes  # the escalation IS the feedback this click

        # Next press: candidate consumed (the handler's once-per-direction
        # guard supplies none) — the D3 ceiling note returns.
        notes2: list = []
        out2 = _redial_settlement_terms(
            terms=out,
            scope_courts=["Prussia"],
            direction="harsher",
            proposer_side_leader="France",
            protected_notes=notes2,
            payer_gold_budgets={"Prussia": 500},
            territory_escalations={},
        )
        assert [
            t for t in out2 if t.get("type") == "territory_cede"
        ] == terr
        assert any("can pay no more" in n for n in notes2)

    def test_ease_at_treasury_cap_escalates_to_france_territory_offer(self):
        """The symmetric ladder (Building Blocks — the same machinery must
        serve Slice G1's AI offer producer): an ease at France's treasury
        ceiling offers the court a region instead."""
        terms = [
            {"type": "peace"},
            {
                "type": "gold_indemnity", "from": "France", "to": "Prussia",
                "amount": 300,
            },
        ]
        events: list = []
        notes: list = []
        out = _redial_settlement_terms(
            terms=terms,
            scope_courts=["Prussia"],
            direction="generous",
            proposer_side_leader="France",
            protected_notes=notes,
            seeded_events=events,
            payer_gold_budgets={"France": 300},  # treasury fully committed
            territory_escalations={
                "Prussia": {
                    "type": "territory_cede", "from": "France",
                    "to": "Prussia", "region": "Bavaria",
                    "authored_by": "talleyrand",
                },
            },
        )
        terr = [t for t in out if t.get("type") == "territory_cede"]
        assert len(terr) == 1
        assert terr[0]["from"] == "France" and terr[0]["to"] == "Prussia"
        escalations = [
            e for e in events if e.get("kind") == "territory_escalation"
        ]
        assert escalations and escalations[0]["group"] == "offer"
        assert not notes

    def test_escalation_respects_clause_cap_and_still_notes(self):
        """A maxed package never gains an over-cap escalation clause — and
        the refusal is voiced, never silent."""
        terms = [{"type": "peace"}]
        while len(terms) < MAX_SETTLEMENT_CLAUSE_COUNT:
            terms.append({
                "type": "gold_indemnity", "from": "Britain", "to": "France",
                "amount": 100 + len(terms),
            })
        notes: list = []
        out = _redial_settlement_terms(
            terms=terms,
            scope_courts=["Prussia"],
            direction="harsher",
            proposer_side_leader="France",
            protected_notes=notes,
            payer_gold_budgets={"Prussia": 0},  # seed unfundable → ceiling
            territory_escalations={
                "Prussia": {
                    "type": "territory_cede", "from": "Prussia",
                    "to": "France", "region": "Silesia",
                    "authored_by": "talleyrand",
                },
            },
        )
        assert len(out) == MAX_SETTLEMENT_CLAUSE_COUNT
        assert not any(t.get("type") == "territory_cede" for t in out)
        assert any("no further terms" in n for n in notes)

    def test_candidates_builder_applies_the_anti_balloon_guards(self):
        """The candidate map enforces the GT-A5 guards: identity from the
        suggestion selectors only, one territory per court per direction,
        cross-candidate region dedupe, territory-only scope."""
        world, _war = _winning_two_court_world()
        # Harsher: both courts draw a candidate from their OWN holdings.
        candidates = _dial_territory_escalation_candidates(
            world,
            terms=[{"type": "peace"}],
            scope_courts=["Britain", "Prussia"],
            direction="harsher",
            proposer_side_participants=["France"],
            proposer_leader="France",
        )
        for court, clause in candidates.items():
            assert clause["type"] == "territory_cede"
            assert clause["from"] == court and clause["to"] == "France"
            assert clause["authored_by"] == "talleyrand"
            assert clause["region"] in {
                str(r) for r in world.get_nation_regions(court)
            }
        regions = [c["region"] for c in candidates.values()]
        assert len(regions) == len(set(regions))

        # An existing direction-matching territory line suppresses that
        # court's candidate (once per court per direction).
        if "Prussia" in candidates:
            suppressed = _dial_territory_escalation_candidates(
                world,
                terms=[
                    {"type": "peace"},
                    {
                        "type": "territory_cede", "from": "Prussia",
                        "to": "France",
                        "region": candidates["Prussia"]["region"],
                    },
                ],
                scope_courts=["Britain", "Prussia"],
                direction="harsher",
                proposer_side_participants=["France"],
                proposer_leader="France",
            )
            assert "Prussia" not in suppressed

        # Generous: offers come from the proposer side's holdings, and two
        # courts are never promised the same region in one click.
        offers = _dial_territory_escalation_candidates(
            world,
            terms=[{"type": "peace"}],
            scope_courts=["Britain", "Prussia"],
            direction="generous",
            proposer_side_participants=["France"],
            proposer_leader="France",
        )
        for court, clause in offers.items():
            assert clause["from"] == "France" and clause["to"] == court
        offer_regions = [c["region"] for c in offers.values()]
        assert len(offer_regions) == len(set(offer_regions))

    def test_ease_with_empty_treasury_offers_land_through_the_handler(self):
        """End to end through the real handler + scorer: France with an
        empty treasury eases the whole table — the courts receive France
        territory offers (distinct regions), voiced as escalation beats.
        France must hold CAPTURED land first: the transferable-region
        selector never cedes proposer home territory, so a fresh-start
        France legitimately has nothing to offer."""
        world, _war = _winning_two_court_world(france_gold=0)
        for captured in ("Rhineland", "Waterloo"):
            world.regions[captured].controller = "France"
        world.invalidate_active_nations_cache()
        dialogue = _stage_propose(world)
        refreshed = _strip_to_peace_only(world, dialogue)
        result = handle_settlement_dialogue_action(
            world,
            action="settlement_dial_generous",
            dialogue=refreshed,
            action_params={
                "action": "settlement_dial_generous",
                "scope": "table",
            },
        )
        assert result["success"] is True, result.get("error_display")
        new_dialogue = result["diplomatic_dialogue"]
        terms = new_dialogue.get("settlement_terms") or []
        offers = [
            t for t in terms
            if str(t.get("type") or "").startswith("territory")
            and t.get("from") == "France"
        ]
        assert offers, terms
        assert _gold_for(terms, "France") == 0
        offer_regions = [str(t.get("region")) for t in offers]
        assert len(offer_regions) == len(set(offer_regions))
        beats = new_dialogue.get("authoring_voice_beats") or []
        assert any(
            b.get("kind") == "talleyrand_line"
            and "offered" in str(b.get("line") or "")
            for b in beats
        ), beats


# ═══════════════════════════════════════════════════════════════════════════
# G4F-13 — a COUNTER_OFFER verdict yields an actual counter (player-sent)
# ═══════════════════════════════════════════════════════════════════════════


def _bilateral_war_world(*, france_gold=2000, britain_dp=3, relations=-40):
    """France vs Britain bilateral WAR in the COUNTER band shape the live
    smoke reproduced (France winning ~+50, hostile relations)."""
    from backend.game_logic.diplomacy import set_diplomatic_state

    world = WorldState()
    set_diplomatic_state(world, "France", "Britain", "WAR", "g4f13-fixture")
    key = world._make_diplo_key("France", "Britain")
    world.nation_relations[key] = relations
    world.war_scores[key] = 50 if key.split("|")[0] == "France" else -50
    world.nation_gold["France"] = france_gold
    world.nation_dp = dict(getattr(world, "nation_dp", {}) or {})
    world.nation_dp["Britain"] = britain_dp
    return world


def _armistice_proposal(sweeteners=None):
    return {
        "type": "armistice",
        "proposer_nation": "France",
        "target_nation": "Britain",
        "sweeteners": list(sweeteners or []),
        "demands": [],
        "clauses": [],
    }


class TestCounterOfferReachesThePlayer:
    """The live smoke sent two COUNTER-verdict proposals and got the
    'not entirely opposed' rejection both times: generate_counter_offer
    resolved FRANCE as the countering court (no desire table, wrong
    diplomat), so a counter was structurally impossible for player-sent
    proposals."""

    def test_player_sent_counter_band_proposal_yields_counter_dialogue(self):
        from backend.game_logic.diplomacy import calculate_acceptance

        world = _bilateral_war_world()
        proposal = _armistice_proposal(sweeteners=[{"type": "gold_lump", "value": 200}])
        baseline = calculate_acceptance(proposal, world)
        assert baseline.get("outcome") == "COUNTER_OFFER", baseline

        world.current_turn = 2
        world.proposal_in_transit = {
            "target": "Britain",
            "proposal": proposal,
            "turn_sent": 1,
            "dp_cost": 1,
            "acceptance_snapshot": int(baseline["score"]),
            "diplomatic_state_at_send": "WAR",
        }
        events = world._process_proposal_in_transit()

        outcomes = [e.get("outcome") for e in events]
        assert "COUNTER_OFFER" in outcomes, events
        active = world.dialogue_manager.peek()
        assert active is not None and active.get("type") == "counter_offer_response"
        counter_terms = active["context"]["counter_terms"]
        added_gold = [
            s for s in counter_terms.get("sweeteners", [])
            if "gold" in str(s.get("type", ""))
        ]
        assert added_gold, counter_terms
        assert world.incoming_proposal_popup
        assert world.talleyrand_state == "IDLE"

    def test_counter_author_is_target_court_and_pays_r138_dp(self):
        from backend.game_logic.ai_diplomacy import generate_counter_offer

        world = _bilateral_war_world(britain_dp=2)
        result = generate_counter_offer(_armistice_proposal(), world)
        assert result is not None
        # R138: the AUTHOR (Britain) pays 1 DP — not France, not skipped.
        assert world.nation_dp["Britain"] == 1

    def test_counter_reaches_the_sign_bar_for_player_sent(self):
        from backend.game_logic.ai_diplomacy import generate_counter_offer
        from backend.game_logic.diplomacy import calculate_acceptance

        world = _bilateral_war_world()
        result = generate_counter_offer(_armistice_proposal(), world)
        assert result is not None
        # The counter is the price Britain WOULD sign at: >= 50, even
        # though Britain's diplomat is a hawk (R125 accept=60 stays M3-only).
        assert calculate_acceptance(result, world)["score"] >= 50

    def test_counter_degrades_honestly_when_payer_cannot_bridge(self):
        world = _bilateral_war_world(france_gold=0)
        world.current_turn = 2
        proposal = _armistice_proposal()
        world.proposal_in_transit = {
            "target": "Britain",
            "proposal": proposal,
            "turn_sent": 1,
            "dp_cost": 1,
            "acceptance_snapshot": 38,
            "diplomatic_state_at_send": "WAR",
        }
        events = world._process_proposal_in_transit()
        outcomes = [e.get("outcome") for e in events]
        assert "COUNTER_OFFER" not in outcomes
        popup = world.proposal_result_popup
        assert popup and popup.get("outcome") == "REJECT"
        active = world.dialogue_manager.peek()
        assert active is None or active.get("type") != "counter_offer_response"

    def test_dry_run_charges_no_dp_and_mutates_nothing(self):
        from backend.game_logic.ai_diplomacy import generate_counter_offer

        world = _bilateral_war_world(britain_dp=2)
        gold_before = dict(world.nation_gold)
        result = generate_counter_offer(
            _armistice_proposal(), world, dry_run=True
        )
        assert result is not None
        assert world.nation_dp["Britain"] == 2
        assert world.nation_gold == gold_before

    def test_m3_direction_keeps_proposer_as_author(self):
        from backend.game_logic.diplomacy import set_diplomatic_state
        from backend.game_logic.ai_diplomacy import generate_counter_offer

        world = WorldState()
        set_diplomatic_state(world, "France", "Austria", "WAR", "g4f13-m3")
        key = world._make_diplo_key("France", "Austria")
        world.nation_relations[key] = -20
        world.nation_gold["Austria"] = 1000
        world.nation_dp = {"Austria": 2, "Britain": 5}
        proposal = {
            "type": "armistice_losing",
            "proposer_nation": "Austria",
            "target_nation": "France",
            "sweeteners": [],
            "demands": [],
            "clauses": [],
        }
        generate_counter_offer(proposal, world)
        # Austria (the proposer-author, M3 semantics) paid the DP charge.
        assert world.nation_dp["Austria"] == 1
        assert world.nation_dp["Britain"] == 5

    def test_preview_enrich_attaches_counter_constructibility(self):
        from backend.game_logic.diplomatic_dialogue import _enrich_proposal_summary

        world = _bilateral_war_world()
        terms = _armistice_proposal()
        terms["type"] = "armistice_winning"
        dialogue = {
            "type": "proposal_confirm",
            "target_nation": "Britain",
            "options": [{"action": "execute_proposal", "terms": terms}],
            "context": {},
        }
        enriched = _enrich_proposal_summary(dialogue, "Britain", "armistice", world)
        assert enriched.get("acceptance_outcome") == "COUNTER_OFFER"
        assert enriched.get("counter_constructible") is True
        assert enriched.get("acceptance_outcome_display") == "COUNTER expected"

        broke = _bilateral_war_world(france_gold=0)
        dialogue2 = {
            "type": "proposal_confirm",
            "target_nation": "Britain",
            "options": [{"action": "execute_proposal", "terms": dict(terms)}],
            "context": {},
        }
        enriched2 = _enrich_proposal_summary(dialogue2, "Britain", "armistice", broke)
        assert enriched2.get("counter_constructible") is False
        assert "REJECT likely" in str(enriched2.get("acceptance_outcome_display"))

    def test_counter_respects_ratification_relation_gate(self):
        """A peace counter at relations below the STATE_RELATION_REQUIREMENTS
        threshold (-60) would bind on the formula and then fail
        _ratify_treaty — the generator must refuse it, and the preview must
        name the gate (the live smoke accepted a counter and got
        'Relations with Britain are insufficient for PEACE')."""
        from backend.game_logic.ai_diplomacy import generate_counter_offer
        from backend.game_logic.diplomatic_dialogue import _enrich_proposal_summary

        world = _bilateral_war_world(relations=-80)
        peace = dict(_armistice_proposal(), type="peace")
        assert generate_counter_offer(peace, world, dry_run=True) is None

        dialogue = {
            "type": "proposal_confirm",
            "target_nation": "Britain",
            "options": [{"action": "execute_proposal", "terms": dict(peace)}],
            "context": {},
        }
        enriched = _enrich_proposal_summary(dialogue, "Britain", "peace", world)
        warning = str(enriched.get("ratification_gate_warning", ""))
        assert "-80" in warning and "-60" in warning
        assert "armistice" in warning.lower()
        # Armistice itself has NO relation requirement — no gate warning.
        world2 = _bilateral_war_world(relations=-80)
        dialogue2b = {
            "type": "proposal_confirm",
            "target_nation": "Britain",
            "options": [
                {"action": "execute_proposal", "terms": _armistice_proposal()}
            ],
            "context": {},
        }
        enriched2b = _enrich_proposal_summary(dialogue2b, "Britain", "armistice", world2)
        assert not enriched2b.get("ratification_gate_warning")

    def test_accept_counter_with_failed_ratification_reports_failure(self):
        """'You have accepted X's counter-proposal. Relations are
        insufficient' — the success copy must not survive a failed
        ratification."""
        from backend.commands.executor import CommandExecutor

        world = _bilateral_war_world(relations=-80)
        counter_terms = {
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": "Britain",
            "sweeteners": [],
            "demands": [],
            "clauses": [],
        }
        world.dialogue_manager.push({
            "type": "counter_offer_response",
            "target_nation": "Britain",
            "talleyrand_text": "test",
            "options": [
                {"label": "Accept counter-offer", "action": "accept_counter_offer"},
                {"label": "Reject", "action": "reject_counter_offer"},
            ],
            "context": {
                "source_nation": "Britain",
                "original_proposal": dict(counter_terms),
                "counter_terms": counter_terms,
            },
            "turn_created": 1,
            "blocking": True,
        })
        executor = CommandExecutor()
        result = executor.handle_diplomatic_dialogue_response(
            "accept_counter_offer", {"world": world}
        )
        assert result.get("success") is False
        assert "could not be ratified" in str(result.get("message", ""))
        assert "accepted" not in str(result.get("message", "")).lower()

    def test_popup_renders_constructibility_display(self):
        """Godot source pin: both render sites prefer the
        constructibility-aware verdict copy over the raw band outcome."""
        source = (GODOT_SCRIPTS / "proposal_confirm_popup.gd").read_text(
            encoding="utf-8"
        )
        assert source.count("acceptance_outcome_display") >= 1
        assert source.count('acceptance.get("outcome_display"') >= 1
        assert "ratification_gate_warning" in source


# ═══════════════════════════════════════════════════════════════════════════
# G4F-14 — generic "armistice" scores as its war-score variant everywhere
# ═══════════════════════════════════════════════════════════════════════════


class TestArmisticeVariantScoringConsistency:
    """Preview scored terms["type"] (variant); send/resolution scored
    terms["proposal_type"] (generic, absent from BASE_DISPOSITION → default
    30). Same package: 45 generic / 38 winning / 58 losing on the live
    fixture — enough to cross both verdict thresholds between the popup
    estimate and the actual resolution."""

    @staticmethod
    def _package(world, ptype):
        return {
            "type": ptype,
            "proposer_nation": "France",
            "target_nation": "Britain",
            "sweeteners": [{"type": "gold_lump", "value": 200}],
            "demands": [],
            "clauses": [],
        }

    def test_generic_armistice_scores_as_winning_variant_when_winning(self):
        from backend.game_logic.diplomacy import calculate_acceptance

        world = _bilateral_war_world()
        generic = calculate_acceptance(self._package(world, "armistice"), world)
        winning = calculate_acceptance(
            self._package(world, "armistice_winning"), world
        )
        losing = calculate_acceptance(
            self._package(world, "armistice_losing"), world
        )
        assert generic["score"] == winning["score"]
        assert winning["score"] != losing["score"]

    def test_generic_armistice_scores_as_losing_variant_when_losing(self):
        from backend.game_logic.diplomacy import calculate_acceptance

        world = _bilateral_war_world()
        key = world._make_diplo_key("France", "Britain")
        world.war_scores[key] = -50 if key.split("|")[0] == "France" else 50
        generic = calculate_acceptance(self._package(world, "armistice"), world)
        losing = calculate_acceptance(
            self._package(world, "armistice_losing"), world
        )
        assert generic["score"] == losing["score"]

    def test_preview_and_send_proposal_shapes_now_agree(self):
        """The exact two shapes the wire builds: the preview scores
        terms["type"]="armistice_winning", execute_proposal scores
        proposal_type-first → generic "armistice". They must be the same
        number."""
        from backend.game_logic.diplomacy import calculate_acceptance

        world = _bilateral_war_world()
        preview_shape = self._package(world, "armistice_winning")
        send_shape = self._package(world, "armistice")
        assert (
            calculate_acceptance(preview_shape, world)["score"]
            == calculate_acceptance(send_shape, world)["score"]
        )


# ═══════════════════════════════════════════════════════════════════════════
# G4F-15 — the armistice arm carries CONCESSIONS only (user-approved)
# ═══════════════════════════════════════════════════════════════════════════


class TestArmisticeArmCarriesConcessionsOnly:
    """The G4F-8 carry-over fed the joint draft's DEMANDS into "Armistice
    with X only" — a carried territory demand probed 19/REJECT where a bare
    armistice sat at 38. A truce that extracts tribute is not a truce: the
    armistice arm now drops demands (voiced), keeps proposer-paid
    sweeteners, and the peace arm keeps the full carry-over."""

    @staticmethod
    def _confirmed_handoff(world, action):
        review = _blocked_review_with_authored_gold(world)
        chooser = handle_settlement_dialogue_action(
            world,
            action=action,
            dialogue=review,
            action_params={"action": action},
        )
        assert chooser["success"] is True
        result = handle_settlement_dialogue_action(
            world,
            action="confirm_pair_substitute",
            dialogue=chooser["diplomatic_dialogue"],
            action_params={"action": "confirm_pair_substitute"},
        )
        assert result["success"] is True, result.get("error_display")
        return result["diplomatic_dialogue"]

    @staticmethod
    def _execute_terms(dialogue):
        for opt in dialogue.get("options", []):
            if opt.get("action") == "execute_proposal" and opt.get("terms"):
                return opt["terms"]
        return {}

    def test_armistice_handoff_drops_demands_and_voices_it(self):
        world, _war = _winning_two_court_world()
        bilateral = self._confirmed_handoff(world, "seek_armistice_instead")
        terms = self._execute_terms(bilateral)
        assert not terms.get("demands"), terms
        assert bilateral.get("armistice_demands_dropped") is True
        text = str(bilateral.get("talleyrand_text") or "")
        assert "ceasefire" in text.lower()
        assert "concessions travel" in text.lower()

    def test_armistice_handoff_keeps_proposer_paid_sweeteners(self):
        world, _war = _winning_two_court_world()
        dialogue = _stage_propose(world)
        dialogue = _add_demand_gold(world, dialogue, "Britain", 300)
        # Author a France-paid concession so the seed has a sweetener side.
        result = handle_settlement_dialogue_action(
            world,
            action="settlement_demand_add",
            dialogue=dialogue,
            action_params={
                "action": "settlement_demand_add",
                "nation": "Britain",
                "clause_type": "gold_indemnity",
                "group": "offer",
                "amount": 200,
            },
        )
        assert result["success"] is True, result.get("error_display")
        submit = handle_settlement_dialogue_action(
            world,
            action="submit_settlement_for_review",
            dialogue=result["diplomatic_dialogue"],
            action_params={"action": "submit_settlement_for_review"},
        )
        assert submit["success"] is True
        chooser = handle_settlement_dialogue_action(
            world,
            action="seek_armistice_instead",
            dialogue=submit["diplomatic_dialogue"],
            action_params={"action": "seek_armistice_instead"},
        )
        confirmed = handle_settlement_dialogue_action(
            world,
            action="confirm_pair_substitute",
            dialogue=chooser["diplomatic_dialogue"],
            action_params={"action": "confirm_pair_substitute"},
        )
        terms = self._execute_terms(confirmed["diplomatic_dialogue"])
        assert not terms.get("demands")
        assert {"type": "gold_lump", "value": 200} in (terms.get("sweeteners") or [])

    def test_peace_arm_still_carries_demands(self):
        world, _war = _winning_two_court_world()
        bilateral = self._confirmed_handoff(world, "seek_bilateral_peace")
        terms = self._execute_terms(bilateral)
        assert {"type": "gold_lump", "value": 300} in (terms.get("demands") or [])
        assert not bilateral.get("armistice_demands_dropped")


# ═══════════════════════════════════════════════════════════════════════════
# G4F-16 — armistice arm absence is explained (disabled-with-reason widening)
# ═══════════════════════════════════════════════════════════════════════════


class TestPairSubstituteDisabledRendering:
    """SC-29 hid every refusal except cooldown_active wordlessly; the live
    smoke could not tell why the armistice arm was absent. The
    player-actionable states (cooldown / already-in-armistice /
    insufficient DP) now render disabled WITH the reason; structural codes
    stay hidden."""

    def test_already_in_armistice_renders_disabled_with_clock(self):
        world, _war = _winning_two_court_world()
        review = _blocked_review_with_authored_gold(world)
        pair = world._make_diplo_key("France", "Britain")
        world.diplomatic_states[pair] = "ARMISTICE"
        world.armistice_turns = {pair: 2}
        # Re-stage so the rail re-evaluates eligibility against live state.
        restaged = handle_settlement_dialogue_action(
            world,
            action="return_to_settlement_terms",
            dialogue=review,
            action_params={"action": "return_to_settlement_terms"},
        )
        assert restaged["success"] is True
        submit = handle_settlement_dialogue_action(
            world,
            action="submit_settlement_for_review",
            dialogue=restaged["diplomatic_dialogue"],
            action_params={"action": "submit_settlement_for_review"},
        )
        options = submit["diplomatic_dialogue"]["options"]
        by_action = {o.get("action"): o for o in options}
        arm = by_action.get("seek_armistice_instead")
        assert arm is not None, [o.get("action") for o in options]
        assert arm.get("available") is False
        reason = str(arm.get("disabled_reason_display") or "")
        assert "already in armistice" in reason.lower()
        assert "3 turns to run" in reason
        # The peace arm stays live from ARMISTICE — the asymmetry that
        # read as a bug is now explained instead of wordless.
        peace = by_action.get("seek_bilateral_peace")
        assert peace is not None and peace.get("available", True) is not False

    def test_insufficient_dp_renders_disabled_with_reason(self):
        world, _war = _winning_two_court_world()
        review = _blocked_review_with_authored_gold(world)
        world.diplomatic_points = 0
        restaged = handle_settlement_dialogue_action(
            world,
            action="return_to_settlement_terms",
            dialogue=review,
            action_params={"action": "return_to_settlement_terms"},
        )
        submit = handle_settlement_dialogue_action(
            world,
            action="submit_settlement_for_review",
            dialogue=restaged["diplomatic_dialogue"],
            action_params={"action": "submit_settlement_for_review"},
        )
        options = submit["diplomatic_dialogue"]["options"]
        by_action = {o.get("action"): o for o in options}
        arm = by_action.get("seek_armistice_instead")
        assert arm is not None
        assert arm.get("available") is False
        assert "diplomatic points" in str(
            arm.get("disabled_reason_display") or ""
        ).lower()

    def test_structural_refusals_stay_hidden(self):
        world, _war = _winning_two_court_world()
        review = _blocked_review_with_authored_gold(world)
        pair = world._make_diplo_key("France", "Britain")
        world.diplomatic_states[pair] = "PEACE"  # already_at_peace
        restaged = handle_settlement_dialogue_action(
            world,
            action="return_to_settlement_terms",
            dialogue=review,
            action_params={"action": "return_to_settlement_terms"},
        )
        submit = handle_settlement_dialogue_action(
            world,
            action="submit_settlement_for_review",
            dialogue=restaged["diplomatic_dialogue"],
            action_params={"action": "submit_settlement_for_review"},
        )
        actions = [
            o.get("action") for o in submit["diplomatic_dialogue"]["options"]
        ]
        assert "seek_bilateral_peace" not in actions
        assert "seek_armistice_instead" not in actions

    def test_popup_reads_display_reason_and_renders_withheld_block(self):
        source = (GODOT_SCRIPTS / "proposal_confirm_popup.gd").read_text(
            encoding="utf-8"
        )
        assert 'opt.get("disabled_reason_display"' in source
        assert "Not available now" in source


# ═══════════════════════════════════════════════════════════════════════════
# G4F-17 — armistice mechanics explained at decision time (fixed 5 + explain)
# ═══════════════════════════════════════════════════════════════════════════


class TestArmisticeMechanicsExplained:
    def test_armistice_proposal_snapshot_carries_mechanics_block(self):
        from backend.game_logic.diplomacy import build_war_context_snapshot

        world = _bilateral_war_world(relations=-80)
        snapshot = build_war_context_snapshot(
            world, "France", "Britain", "armistice"
        )
        block = snapshot.get("armistice_mechanics")
        assert block, snapshot.keys()
        assert block["duration_turns"] == 5
        assert block["auto_peace_relation_threshold"] == -60
        assert block["current_relation"] == -80
        assert block["projected_outcome"] == "war"
        lines = block["display_lines"]
        assert len(lines) == 3
        assert "5-turn ceasefire" in lines[0]
        assert "-60" in lines[1]
        assert "war resumes" in lines[2]
        for key in (
            "duration_turns", "auto_peace_relation_threshold",
            "current_relation",
        ):
            assert isinstance(block[key], int)  # Godot int rule

    def test_projection_flips_to_peace_when_relations_healed(self):
        from backend.game_logic.diplomacy import build_war_context_snapshot

        world = _bilateral_war_world(relations=-40)
        snapshot = build_war_context_snapshot(
            world, "France", "Britain", "armistice"
        )
        block = snapshot["armistice_mechanics"]
        assert block["projected_outcome"] == "peace"
        assert "peace" in block["display_lines"][2]

    def test_peace_proposal_snapshot_has_no_armistice_block(self):
        from backend.game_logic.diplomacy import build_war_context_snapshot

        world = _bilateral_war_world()
        snapshot = build_war_context_snapshot(world, "France", "Britain", "peace")
        assert "armistice_mechanics" not in snapshot

    def test_war_status_projects_active_armistice_outcome(self):
        from backend.game_logic.diplomacy import set_diplomatic_state
        from backend.game_logic.war_status import build_active_wars

        world = WorldState()
        set_diplomatic_state(world, "France", "Britain", "ARMISTICE", "g4f17")
        pair = world._make_diplo_key("France", "Britain")
        world.armistice_turns = {pair: 1}
        world.nation_relations[pair] = -75
        entry = next(
            w for w in build_active_wars(world)["wars"]
            if w.get("status") == "armistice" and w.get("opponent") == "Britain"
        )
        assert entry["armistice_remaining"] == 4
        assert entry["armistice_projected_outcome"] == "war"
        assert entry["armistice_auto_peace_threshold"] == -60

        world.nation_relations[pair] = -20
        entry2 = next(
            w for w in build_active_wars(world)["wars"]
            if w.get("status") == "armistice" and w.get("opponent") == "Britain"
        )
        assert entry2["armistice_projected_outcome"] == "peace"

    def test_godot_surfaces_render_the_mechanics(self):
        confirm = (GODOT_SCRIPTS / "proposal_confirm_popup.gd").read_text(
            encoding="utf-8"
        )
        incoming = (GODOT_SCRIPTS / "incoming_proposal_popup.gd").read_text(
            encoding="utf-8"
        )
        detail = (GODOT_SCRIPTS / "war_detail_popup.gd").read_text(
            encoding="utf-8"
        )
        panel = (GODOT_SCRIPTS / "war_status_panel.gd").read_text(
            encoding="utf-8"
        )
        assert "armistice_mechanics" in confirm
        assert "armistice_mechanics" in incoming
        assert "armistice_projected_outcome" in detail
        assert "armistice_projected_outcome" in panel
