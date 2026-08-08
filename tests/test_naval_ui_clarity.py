"""NV-12 "The Clear Deck" — the naval UI clarity pass (NAVAL_SPEC §16).

Zero mechanics: every change is payload/copy + rendering. These tests pin
the honest-availability contract — every term/chip/blocked-reason mirrors
the executor gate that would actually fire — and that the client consumes
the fields (the NV-6 lesson: `expedition_terms` was built and then read by
NO .gd file at all).
"""

import json
from pathlib import Path

import pytest

from backend.game_logic import naval
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCENARIO_1805 = (REPO / "godot-client" / "project-sovereign" / "assets"
                 / "maps" / "europe_1805.json")
SCENARIO_TUTORIAL = (REPO / "godot-client" / "project-sovereign" / "assets"
                     / "maps" / "tutorial_1805.json")


@pytest.fixture
def world():
    return WorldState.from_scenario(str(SCENARIO_1805))


def _read_gd(rel: str) -> str:
    return (REPO / "godot-client" / "project-sovereign" / rel).read_text(
        encoding="utf-8")


class TestExpeditionTerms:
    def test_terms_carry_met_and_detail(self, world):
        r = naval.build_admiralty_report(world)
        terms = r["expedition_terms"]
        assert len(terms) == 2
        for t in terms:
            assert set(t) >= {"text", "met", "detail"}
        assert terms[0]["met"] is True  # France boots with dockyards
        assert "15,000" in terms[1]["text"]
        # Boot: every French corps is a big army inland — the term is unmet
        # and says what to do about it.
        assert terms[1]["met"] is False
        assert "march a corps to a yard" in terms[1]["detail"]

    def test_ready_corps_named_when_one_qualifies(self, world):
        yards = naval.controlled_dockyards(world, "France")
        m = next(m for m in world.get_marshals_by_nation("France"))
        m.strength = 9000
        m.location = yards[0]
        world._build_marshal_index()
        r = naval.build_admiralty_report(world)
        term = r["expedition_terms"][1]
        assert term["met"] is True
        assert m.name in term["detail"]
        assert yards[0] in term["detail"]

    def test_over_cap_corps_gets_the_detach_arithmetic(self, world):
        yards = naval.controlled_dockyards(world, "France")
        m = next(m for m in world.get_marshals_by_nation("France"))
        m.strength = 24000
        m.location = yards[0]
        world._build_marshal_index()
        r = naval.build_admiralty_report(world)
        term = r["expedition_terms"][1]
        assert term["met"] is False
        assert m.name in term["detail"]
        assert "9,000" in term["detail"]  # 24,000 − 15,000, exactly

    def test_notes_quote_the_resolver_constants(self, world):
        """Shown = applied: the loss magnitudes come from the SAME constants
        resolve_expedition rolls — a retune moves the copy with it."""
        notes = " ".join(naval.build_admiralty_report(world)["expedition_notes"])
        assert f"~{int(naval.EXPEDITION_INTERCEPT_LOSS * 100)}%" in notes
        assert f"~{int(naval.EXPEDITION_TURNBACK_LOSS * 100)}%" in notes
        assert str(naval.EXPEDITION_TURNBACK_READINESS) in notes
        assert "effective = sail" in notes  # the word finally defined

    def test_payload_driven_client_numbers(self, world):
        r = naval.build_admiralty_report(world)
        assert r["ship_cost"] == naval.SHIP_COST
        assert r["camp_required"] == naval.DESCENT_CAMP_MIN_TROOPS


class TestFleetlessChips:
    def test_fleetless_player_keeps_the_orders_block(self, world):
        """Recon trap 9: the whole chips list was gated on ships>0 — the
        player who most needs the explanation lost the header, every reason
        AND the build chip. All three chips now render with reasons."""
        rec = naval.get_fleet(world, "France")
        rec["ships"] = 0
        r = naval.build_admiralty_report(world)
        labels = {c["label"].split(" (")[0]: c for c in r["chips"]}
        assert "Blockade the enemy" in labels
        assert labels["Blockade the enemy"]["enabled"] is False
        assert "no fleet in commission" in labels["Blockade the enemy"]["reason"]
        assert "The Grand Diversion" in labels
        assert labels["The Grand Diversion"]["enabled"] is False
        assert "no fleet in commission" in labels["The Grand Diversion"]["reason"]
        assert any(c["command"] == "build ships" for c in r["chips"])

    def test_build_chip_mirrors_the_executor_gates(self, world):
        """Honest availability: enabled iff check_build_fleet passes AND the
        treasury covers the keel (the executor's own two gates)."""
        r = naval.build_admiralty_report(world)
        build = next(c for c in r["chips"] if c["command"] == "build ships")
        assert build["enabled"] is (
            naval.check_build_fleet(world, "France") is None
            and world.nation_gold.get("France", 0) >= naval.SHIP_COST)
        # Drain the treasury → the chip states the executor's price refusal.
        world.nation_gold["France"] = 100
        r2 = naval.build_admiralty_report(world)
        build2 = next(c for c in r2["chips"] if c["command"] == "build ships")
        assert build2["enabled"] is False
        assert "treasury holds 100g" in build2["reason"]

    def test_build_chip_names_the_yard(self, world):
        r = naval.build_admiralty_report(world)
        build = next(c for c in r["chips"] if c["command"] == "build ships")
        yards = naval.controlled_dockyards(world, "France")
        assert yards[0] in build["label"]


class TestBlockedLandings:
    def test_blocked_and_options_are_disjoint(self, world):
        """A region with a landing chip never carries a blocked reason, and
        vice versa — the two dicts partition the coastal answer."""
        options = naval.expedition_landing_options(world, "France")
        blocked = naval.expedition_blocked_reasons(world, "France")
        assert not (set(options) & set(blocked))

    def test_non_consenting_shore_names_the_remedy(self, world):
        blocked = naval.expedition_blocked_reasons(world, "France")
        # Portugal boots neutral and coastal — her shore is the canonical
        # court-first case.
        target = next((r for r, reason in blocked.items()
                       if "Portugal" in reason), None)
        assert target is not None
        assert "court her" in blocked[target]
        assert "make it war" in blocked[target]

    def test_no_eligible_corps_reason_is_actionable(self, world):
        blocked = naval.expedition_blocked_reasons(world, "France")
        # At boot no French corps is expedition-sized at a yard: at-war
        # coastal shores (Britain's home islands) carry the corps reason.
        corps_reasons = [r for r in blocked.values() if "stands at" in r
                         or "detach" in r]
        assert corps_reasons, blocked
        assert any("march one there" in r for r in corps_reasons)

    def test_over_cap_at_yard_gets_the_detach_line(self, world):
        yards = naval.controlled_dockyards(world, "France")
        for m in world.get_marshals_by_nation("France"):
            m.strength = 30000
        m = next(m for m in world.get_marshals_by_nation("France"))
        m.location = yards[0]
        world._build_marshal_index()
        blocked = naval.expedition_blocked_reasons(world, "France")
        assert any("detach 15,000 first" in r for r in blocked.values())

    def test_dormant_world_has_the_key_and_no_rows(self):
        tw = WorldState.from_scenario(str(SCENARIO_TUTORIAL))
        overlay = naval.map_naval_overlay(tw)
        assert overlay["expedition_blocked"] == {}
        assert naval.build_admiralty_report(tw)["active"] is False


class TestCrossingsCopy:
    def test_destroyed_fleet_still_names_the_coverer(self, world):
        """Recon trap 1: mover_effective 0 → falsy ratio → the row degraded
        to a bare 'SHUT'. The worst-informed state now names the fleet.
        The escort POOLS co-belligerent allies (Spain, Holland), so the
        whole side must be sunk to reach the bare-ratio state."""
        for nation, rec in list(world.fleets.items()):
            if nation.startswith("__") or not isinstance(rec, dict):
                continue
            if nation != "Britain":
                rec["ships"] = 0
        r = naval.build_admiralty_report(world)
        shut_lines = [c["line"] for c in r["crossings"]
                      if c["verdict"] == "shut"]
        assert shut_lines
        for line in shut_lines:
            assert line.rstrip().endswith("SHUT") is False, line
        assert any("commands the water unopposed" in line
                   for line in shut_lines)

    def test_legend_names_all_three_tints_and_the_remedy(self, world):
        legend = naval.build_admiralty_report(world)["crossings_legend"]
        for word in ("crimson", "amber", "gold", "expedition"):
            assert word in legend


class TestConfirmQuoteAndHelp:
    def test_confirm_quote_states_the_loss_magnitudes(self):
        """The quote's loss sentence is built FROM the naval constants (a
        retune moves the quote) — pinned at the source seam."""
        src = (REPO / "backend" / "commands" / "naval_executor.py").read_text(
            encoding="utf-8")
        assert "A failed run costs" in src
        assert "naval.EXPEDITION_INTERCEPT_LOSS" in src
        assert "naval.EXPEDITION_TURNBACK_LOSS" in src
        assert "naval.EXPEDITION_TURNBACK_READINESS" in src

    def test_help_text_teaches_amber(self):
        src = (REPO / "backend" / "commands" / "meta_executor.py").read_text(
            encoding="utf-8")
        assert "AMBER" in src
        assert "DEFENDED SHORE" in src


class TestClientConsumption:
    """The NV-6 lesson as standing pins: a payload nothing renders is a lie
    waiting to be filed. Every new field names its consumer."""

    def test_admiralty_is_its_own_tab(self):
        scene = _read_gd("scenes/strategic_ledger.tscn")
        assert "AdmiraltyTab" in scene
        gd = _read_gd("scripts/strategic_ledger.gd")
        assert "KEY_7" in gd
        assert "_render_admiralty_tab" in gd
        assert "admiralty_tab" in gd
        assert "press 7" in gd  # the economy page points across

    def test_expedition_terms_and_notes_render(self):
        gd = _read_gd("scripts/strategic_ledger.gd")
        assert "expedition_terms" in gd
        assert "expedition_notes" in gd
        assert "The Expedition" in gd

    def test_legend_and_camp_progress_render(self):
        gd = _read_gd("scripts/strategic_ledger.gd")
        assert "crossings_legend" in gd
        assert "camp_required" in gd
        assert "a descent requires" in gd

    def test_disabled_chips_use_the_pill_family(self):
        gd = _read_gd("scripts/strategic_ledger.gd")
        assert "bb_chip_disabled" in gd

    def test_war_detail_consumes_naval_line(self):
        gd = _read_gd("scripts/war_detail_popup.gd")
        assert "naval_line" in gd
        assert "Their fleet:" in gd

    def test_region_panel_renders_blocked_reasons(self):
        gd = _read_gd("scripts/region_panel.gd")
        assert "expedition_blocked" in gd
        assert "No landing here" in gd
        assert "the senior yard" in gd  # the nation-scoped keel note


class TestParserCoverage:
    def test_confirm_reissue_corpus_row_exists_and_parses(self):
        corpus = json.loads(
            (REPO / "tests" / "data" / "parser_golden_corpus.json").read_text(
                encoding="utf-8"))
        entries = corpus["entries"] if isinstance(corpus, dict) else corpus
        row = next((e for e in entries
                    if e.get("id") == "naval-land-confirmed-reissue"), None)
        assert row is not None
        assert row["expected"]["action"] == "naval_expedition"

        from backend.commands.parser import CommandParser
        world = WorldState.from_scenario(str(SCENARIO_1805))
        # The SERVE convention: main.py always passes a game_state with the
        # live player roster beside the world. (A cold parse with world only
        # falls back to the legacy scan roster and resolves "Soult" through
        # the world-side fuzzy stage, where the token "land" can outbid it —
        # a calling convention no production path uses.)
        game_state = {
            "marshals": {m.name: {} for m in
                         world.get_marshals_by_nation("France")},
            "enemies": {m.name: {} for m in world.marshals.values()
                        if m.nation != "France"},
        }
        result = CommandParser(use_real_llm=False).parse(
            "land Soult in Munster confirmed", game_state=game_state,
            world=world)
        assert result.get("success"), result.get("error")
        assert result["command"]["action"] == "naval_expedition"
        assert result["command"]["marshal"] == "Soult"

    def test_diversion_few_shot_exists(self):
        src = (REPO / "backend" / "ai" / "prompt_builder.py").read_text(
            encoding="utf-8")
        assert '"order the diversion"' in src
        assert '"naval_diversion"' in src
