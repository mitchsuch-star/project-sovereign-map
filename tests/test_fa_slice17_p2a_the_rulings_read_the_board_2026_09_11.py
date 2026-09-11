"""FA slice 17, Phase 2 batch 2a — "The Rulings Read the Board" (September 11, 2026).

Fifteen legibility rulings built behind flip levers, each pinned on the
surface it changes AND with its lever down (the prior behaviour reproduces):

  FA-D1  the restless-interior term names the provinces that trip it
  FA-D2  the coalition row reads its objective across every pair the score sums
  FA-D3  every held marshal rides the suggested terms, the sovereign first
  FA-D8  the fallen-province headline names the counter, priced from the law
  FA-D9  the wavering line names the drill and its figure
  FA-D10 the ally-standing rows render on the War Detail screen (one formatter)
  FA-D11 the balance tab renders the threat projection + each member's trend
  FA-D12 the player's own peace has a headline class
  FA-D15 a settlement-tier war whose review is unavailable renders DISABLED with its reason
  FA-D16 the lift counsel never names the Emperor and names the Marshalate's road
  FA-D17 the paradox block names the armistice route; the wizard row carries it
  FA-D18 the truce projection counts the thaw
  FA-D22 one word means one thing (claim in arrears, not grievance)
  FA-D24 Berthier's observation is deterministic per battle
  FA-D26 the Materiel bill has a ledger row

Every census here is scoped to CODE (calls / identifiers), never to prose,
and carries a sensitivity arm.
"""
from __future__ import annotations

import random
import re
from pathlib import Path

import pytest

from backend.models.world_state import WorldState

ROOT = next(p for p in (Path(__file__).resolve().parents[1], Path.cwd()) if (p / "backend").is_dir())
SCENARIO = ROOT / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
GD = ROOT / "godot-client" / "project-sovereign" / "scripts"


def _boot():
    return WorldState.from_scenario(str(SCENARIO))


def _read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def _flip(monkeypatch, module, name, value):
    assert hasattr(module, name), f"{module.__name__} has no lever {name}"
    monkeypatch.setattr(module, name, value)


# ═══════════════════════════════════════════════════════════════════════
# FA-D1 — the restless term names its provinces
# ═══════════════════════════════════════════════════════════════════════
class TestD1RestlessTermNamesItsProvinces:
    def _restless_world(self):
        w = _boot()
        w.get_region("Gascony").stability = 30
        w.get_region("Bearn").stability = 20
        return w

    def test_the_term_carries_its_provinces_sorted(self):
        w = self._restless_world()
        terms = {t["key"]: t for t in w.get_state_charges_rate("France")["terms"]}
        term = terms["restless_interior"]
        assert term["regions"] == ["Bearn", "Gascony"]
        assert term["label"] == "the interior is restless — Bearn, Gascony"

    def test_more_than_three_are_counted_not_listed(self):
        w = self._restless_world()
        for name in ("Artois", "Picardy", "Champagne"):
            w.get_region(name).stability = 10
        term = {t["key"]: t for t in w.get_state_charges_rate("France")["terms"]}["restless_interior"]
        assert len(term["regions"]) == 5
        assert term["label"].endswith("(+2 more)")
        assert term["label"].count(",") == 2  # three named

    def test_lever_down_reproduces_the_bare_label(self, monkeypatch):
        from backend.models import world_state as WS
        _flip(monkeypatch, WS, "THE_RESTLESS_TERM_NAMES_ITS_PROVINCES", False)
        w = self._restless_world()
        term = {t["key"]: t for t in w.get_state_charges_rate("France")["terms"]}["restless_interior"]
        assert term["label"] == "the interior is restless"
        assert term["regions"] == []

    def test_the_rate_is_the_same_in_both_arms_shown_equals_applied(self, monkeypatch):
        from backend.models import world_state as WS
        w = self._restless_world()
        up = w.get_state_charges_rate("France")["rate"]
        _flip(monkeypatch, WS, "THE_RESTLESS_TERM_NAMES_ITS_PROVINCES", False)
        down = w.get_state_charges_rate("France")["rate"]
        assert up == down
        assert w.calculate_state_charges("France") == w.calculate_state_charges("France", rate=up)


# ═══════════════════════════════════════════════════════════════════════
# FA-D2 — the coalition row reads every pair
# ═══════════════════════════════════════════════════════════════════════
class TestD2CoalitionRowReadsEveryPair:
    @staticmethod
    def _coalition_row(w):
        from backend.game_logic.war_status import build_active_wars
        rows = [r for r in build_active_wars(w)["wars"] if r.get("is_multi_participant_war")]
        assert rows, "the 1805 boot has a coalition war"
        return rows[0]

    def test_boot_row_carries_only_the_declarations_default(self, monkeypatch):
        """FA-D4 (Phase 2b) gives every boot pair the declaration's default
        `defense`; the row shows the LEADER pair's, labelled, and nothing
        named. With D4 down the boot row has no objective at all."""
        from backend.models import world_state as WS
        w = _boot()
        row = self._coalition_row(w)
        assert row["objective"]["type"] == "defense"
        assert row["objective"]["against"] == row["opponent"]
        _flip(monkeypatch, WS, "THE_SPINE_WAR_HAS_A_PURPOSE", False)
        assert self._coalition_row(_boot())["objective"] is None

    def test_a_purpose_set_against_a_member_renders_on_the_coalition_row(self):
        w = _boot()
        row = self._coalition_row(w)
        member = "Austria"
        assert row["opponent"] != member  # the leader pair is Britain's
        key = w._make_diplo_key("France", member)
        w.war_objectives.setdefault(key, {})["France"] = {
            "type": "humiliation", "set_turn": w.current_turn, "concluded_turn": None}
        obj = self._coalition_row(w)["objective"]
        assert obj is not None
        assert obj["type"] == "humiliation"
        assert obj["against"] == member

    def test_the_leader_pair_still_wins_when_both_stand(self):
        w = _boot()
        row = self._coalition_row(w)
        leader = row["opponent"]
        for court, kind in ((leader, "conquest"), ("Austria", "humiliation")):
            key = w._make_diplo_key("France", court)
            w.war_objectives.setdefault(key, {})["France"] = {
                "type": kind, "set_turn": w.current_turn, "concluded_turn": None}
        obj = self._coalition_row(w)["objective"]
        assert obj["against"] == leader and obj["type"] == "conquest"

    def test_the_enemy_objective_reads_every_pair_too(self):
        w = _boot()
        key = w._make_diplo_key("France", "Russia")
        w.war_objectives.setdefault(key, {})["Russia"] = {
            "type": "humiliation", "set_turn": w.current_turn, "concluded_turn": None}
        enemy_obj = self._coalition_row(w)["enemy_objective"]
        assert enemy_obj is not None and enemy_obj["by"] == "Russia"

    def test_lever_down_reads_the_leader_pair_only(self, monkeypatch):
        from backend.game_logic import war_status as WSt
        _flip(monkeypatch, WSt, "THE_COALITION_ROW_READS_EVERY_PAIR", False)
        w = _boot()
        key = w._make_diplo_key("France", "Austria")
        w.war_objectives.setdefault(key, {})["France"] = {
            "type": "humiliation", "set_turn": w.current_turn, "concluded_turn": None}
        row = self._coalition_row(w)
        # the leader pair's own default (FA-D4), never the member's named purpose
        assert row["objective"]["type"] == "defense"
        assert row["objective"]["against"] == row["opponent"]

    def test_the_detail_screen_prints_the_court_it_targets(self):
        src = (GD / "war_detail_popup.gd").read_text(encoding="utf-8")
        assert 'objective.get("against", "")' in src
        assert '" (against " + Utils.display_nation_name(against) + ")"' in src


# ═══════════════════════════════════════════════════════════════════════
# FA-D3 — every prisoner is on the table
# ═══════════════════════════════════════════════════════════════════════
class TestD3EveryPrisonerIsOnTheTable:
    @staticmethod
    def _capture(w, name, captor):
        m = w.marshals[name]
        m.captured_by = captor
        m.strength = 0
        m.location = w.get_nation_capital(captor)
        return m

    def test_an_ordinary_captured_marshal_rides_the_sweeteners(self):
        from backend.game_logic.diplomatic_templates import generate_suggested_terms
        w = _boot()
        self._capture(w, "Mack", "France")
        terms = generate_suggested_terms("Austria", "peace", w)
        assert {"type": "prisoner_return", "marshal": "Mack"} in terms["sweeteners"]

    def test_our_captured_men_ride_the_demands_sovereign_first(self):
        from backend.game_logic.diplomatic_templates import generate_suggested_terms
        w = _boot()
        self._capture(w, "Davout", "Austria")
        self._capture(w, "Napoleon", "Austria")
        terms = generate_suggested_terms("Austria", "peace", w)
        rows = [d["marshal"] for d in terms["demands"] if d.get("type") == "prisoner_return"]
        assert rows == ["Napoleon", "Davout"]  # the Brétigny ordering: the Emperor first

    def test_no_row_is_duplicated(self):
        from backend.game_logic.diplomatic_templates import generate_suggested_terms
        w = _boot()
        self._capture(w, "Mack", "France")
        terms = generate_suggested_terms("Austria", "peace", w)
        rows = [s["marshal"] for s in terms["sweeteners"] if s.get("type") == "prisoner_return"]
        assert rows.count("Mack") == 1

    def test_lever_down_keeps_the_sovereign_gate(self, monkeypatch):
        from backend.game_logic import diplomatic_templates as DT
        _flip(monkeypatch, DT, "EVERY_PRISONER_IS_ON_THE_TABLE", False)
        w = _boot()
        self._capture(w, "Mack", "France")
        self._capture(w, "Napoleon", "Austria")
        terms = DT.generate_suggested_terms("Austria", "peace", w)
        assert not any(s.get("marshal") == "Mack" for s in terms["sweeteners"])
        assert [d["marshal"] for d in terms["demands"] if d.get("type") == "prisoner_return"] == ["Napoleon"]


# ═══════════════════════════════════════════════════════════════════════
# FA-D8 — the fallen province names the counter
# ═══════════════════════════════════════════════════════════════════════
class TestD8FallenProvinceNamesTheCounter:
    EVT = {"type": "region_captured", "region": "Normandy", "captured_by": "Britain",
           "previous_controller": "France", "nation": "Britain"}

    def test_the_clause_quotes_both_figures_from_the_law(self):
        from backend.game_logic import dispatch as D
        from backend.commands.economy_executor import EconomyExecutor
        from backend.commands.movement_executor import MARCH_HALTS_AT_GARRISON
        w = _boot()
        text = D._home_captured_lever(w, "Normandy", "France", dict(self.EVT))
        assert f"A garrison you detach ({EconomyExecutor.GARRISON_DETACHMENT_SIZE:,} men)" in text
        assert f"as does any garrison of {MARCH_HALTS_AT_GARRISON:,}" in text
        assert "a corps standing there forces a battle" in text

    def test_the_corps_standing_there_is_named_when_our_intel_sees_it(self):
        from backend.game_logic import dispatch as D
        w = _boot()
        w.get_region("Normandy").controller = "Britain"
        w.marshals["Moore"].location = "Normandy"
        w.marshals["Ney"].location = "Paris"  # adjacent — our own eyes
        w.calculate_visibility()
        text = D._home_captured_lever(w, "Normandy", "France", dict(self.EVT))
        assert "Moore" in text and "stands there" in text

    def test_no_name_leaks_through_fog(self):
        from backend.game_logic import dispatch as D
        from backend.models.intel import UNKNOWN
        w = _boot()
        w.get_region("Normandy").controller = "Britain"
        w.marshals["Moore"].location = "Normandy"
        w.calculate_visibility()
        # the helper reads the player's OWN intel record of the province — fog it
        intel = w.intel.get("Normandy")
        assert intel is not None
        intel.visibility = UNKNOWN
        text = D._home_captured_lever(w, "Normandy", "France", dict(self.EVT))
        assert "Moore" not in text and "stands there" not in text
        assert "A garrison you detach" in text  # the counters are still taught

    def test_lever_down_is_the_bare_sentence(self, monkeypatch):
        from backend.game_logic import dispatch as D
        _flip(monkeypatch, D, "THE_FALLEN_PROVINCE_NAMES_THE_COUNTER", False)
        w = _boot()
        assert D._home_captured_lever(w, "Normandy", "France", dict(self.EVT)) == ""
        assert D._HEADLINE_TEMPLATES["home_captured"].endswith("{lever}")

    def test_the_march_floor_has_one_home(self):
        """The law's `5000` at six sites now reads MARCH_HALTS_AT_GARRISON."""
        for rel in ("backend/commands/movement_executor.py", "backend/ai/enemy_ai.py"):
            src = _read(rel)
            bare = re.findall(r"garrison_strength[^\n]{0,12}(?:>=|<) *5000\b", src)
            assert bare == [], (rel, bare)
        assert "MARCH_HALTS_AT_GARRISON = 5000" in _read("backend/commands/movement_executor.py")

    def test_the_march_floor_census_is_sensitive(self):
        bare = re.findall(r"garrison_strength[^\n]{0,12}(?:>=|<) *5000\b",
                          "if adj_region.garrison_strength >= 5000:\n")
        assert bare


# ═══════════════════════════════════════════════════════════════════════
# FA-D9 — the wavering line names the drill
# ═══════════════════════════════════════════════════════════════════════
class TestD9WaveringLineNamesTheDrill:
    def test_the_line_quotes_the_drill_constants(self):
        from backend.game_logic import dispatch as D
        w = _boot()
        ney = w.marshals["Ney"]
        ney.morale = 25
        line = D._derive_danger(ney, w, "France", {})
        assert line.startswith("Morale failing (25) — the men waver.")
        assert f"+{int(WorldState.DRILL_MORALE_GAIN)} morale" in line
        assert f"+{int(WorldState.DRILL_MORALE_GAIN_TRAINED)} with a training ground" in line

    def test_a_drilling_corps_is_told_so(self):
        from backend.game_logic import dispatch as D
        w = _boot()
        ney = w.marshals["Ney"]
        ney.morale = 25
        ney.drilling = True
        assert D._derive_danger(ney, w, "France", {}).endswith("Drilling now.")

    def test_lever_down_is_the_bare_line(self, monkeypatch):
        from backend.game_logic import dispatch as D
        _flip(monkeypatch, D, "THE_WAVERING_LINE_NAMES_THE_DRILL", False)
        w = _boot()
        ney = w.marshals["Ney"]
        ney.morale = 25
        assert D._derive_danger(ney, w, "France", {}) == "Morale failing (25) — the men waver."


# ═══════════════════════════════════════════════════════════════════════
# FA-D10 / FA-D11 / FA-D15 — the client surfaces (code censuses)
# ═══════════════════════════════════════════════════════════════════════
class TestClientSurfaces:
    def test_d10_one_formatter_feeds_both_surfaces(self):
        utils = (GD / "utils.gd").read_text(encoding="utf-8")
        hud = (GD / "war_status_panel.gd").read_text(encoding="utf-8")
        detail = (GD / "war_detail_popup.gd").read_text(encoding="utf-8")
        assert "static func standing_lines(war_data: Dictionary) -> Array:" in utils
        assert "Utils.standing_lines(war_data)" in hud
        assert "Utils.standing_lines(w)" in detail
        # the HUD's inline copy is gone — the literal lives in ONE file now
        assert hud.count('"Standing (top 5):"') == 0
        assert utils.count('"Standing (top 5):"') == 1

    def test_d11_the_balance_tab_renders_projection_and_trend(self):
        src = (GD / "diplomatic_ledger.gd").read_text(encoding="utf-8")
        assert 'boe.get("threat_projection", {})' in src
        for key in ("after_next_war", "brewing_threshold", "instant_threshold",
                    "wars_until_brewing", "wars_until_instant"):
            assert f'projection.get("{key}"' in src, key
        assert 'mem.get("war_exhaustion_trend", "")' in src
        assert "trend_glyph" in src

    def test_d11_the_keys_the_client_reads_are_the_keys_the_backend_writes(self):
        src = _read("backend/game_logic/diplomatic_ledger.py")
        for key in ("after_next_war", "brewing_threshold", "instant_threshold",
                    "wars_until_brewing", "wars_until_instant", "war_exhaustion_trend"):
            assert f'"{key}"' in src, key

    def test_d15_a_settlement_tier_war_renders_a_disabled_button_with_its_reason(self):
        detail = (GD / "war_detail_popup.gd").read_text(encoding="utf-8")
        assert "func _add_disabled_settlement_button(reason: String):" in detail
        assert 'str(war_data.get("settlement_disabled_reason_display", ""))' in detail
        assert "btn.disabled = true" in detail and "btn.tooltip_text = reason" in detail
        # and the backend really writes that key
        assert '"settlement_disabled_reason_display"' in _read("backend/game_logic/war_status.py")

    def test_the_client_census_is_sensitive(self):
        assert "Utils.standing_lines(w)" not in "for ln in Utils.other(w):"


# ═══════════════════════════════════════════════════════════════════════
# FA-D12 — the player's own peace leads the briefing
# ═══════════════════════════════════════════════════════════════════════
class TestD12PeaceLeadsTheBriefing:
    PEACE = {"type": "peace_ratified", "proposer_nation": "France", "target_nation": "Austria",
             "ratifying_nations": ["France", "Austria"], "war_outcome": "white_peace",
             "state_transition": "WAR_TO_PEACE"}

    def test_a_ratified_peace_has_a_headline(self):
        from backend.game_logic import dispatch as D
        w = _boot()
        w.event_log.clear()
        w.log_event(dict(self.PEACE, turn=w.current_turn))
        head = D._build_headline(w, "France")
        assert head is not None and head["class"] == "peace_signed"
        assert head["text"] == "Sire — peace with Austria is signed. A white peace — the map stands as it was."

    def test_a_third_partys_peace_is_not_our_headline(self):
        from backend.game_logic import dispatch as D
        w = _boot()
        w.event_log.clear()
        w.log_event(dict(self.PEACE, proposer_nation="Prussia", target_nation="Russia",
                         ratifying_nations=["Prussia", "Russia"], turn=w.current_turn))
        head = D._build_headline(w, "France")
        assert head is None or head["class"] != "peace_signed"

    def test_the_weight_sits_with_the_wounds_not_above_them(self):
        from backend.game_logic import dispatch as D
        assert D.HEADLINE_WEIGHTS["peace_signed"] == D.HEADLINE_WEIGHTS["war_touches_us"]
        assert D.HEADLINE_WEIGHTS["peace_signed"] > D.HEADLINE_WEIGHTS["region_taken"]
        # road_home says the same thing and names the road — it wins by IDENTITY,
        # not weight: the peace class is not added when a road_home stands.
        src = _read("backend/game_logic/dispatch.py")
        assert 'c["identity"].startswith("road_home:") and _other in c["identity"]' in src

    def test_lever_down_has_no_peace_headline(self, monkeypatch):
        from backend.game_logic import dispatch as D
        _flip(monkeypatch, D, "THE_PEACE_LEADS_THE_BRIEFING", False)
        w = _boot()
        w.event_log.clear()
        w.log_event(dict(self.PEACE, turn=w.current_turn))
        head = D._build_headline(w, "France")
        assert head is None or head["class"] != "peace_signed"


# ═══════════════════════════════════════════════════════════════════════
# FA-D16 — the lift counsel names the Marshalate
# ═══════════════════════════════════════════════════════════════════════
class TestD16LiftCounselNamesTheMarshalate:
    def test_the_emperor_is_never_the_counsel(self):
        from backend.game_logic import naval as NV
        w = _boot()
        text = NV.over_lift_refusal(w, w.marshals["Soult"])
        assert "Napoleon stands at" not in text
        assert "Only Napoleon's Guard is under the lift, and the Emperor does not sail on an expedition." in text

    def test_the_road_names_the_cheapest_commission_the_gate_would_pass(self):
        from backend.game_logic import naval as NV
        from backend.game_logic.recruitment import first_affordable_commission, RECRUIT_MARSHAL_CORPS
        w = _boot()
        assert NV.marshalate_road(w, "France") == ""  # 800g at boot clears nobody
        w.nation_gold["France"] = 10_000
        cand = first_affordable_commission(w, "France")
        road = NV.marshalate_road(w, "France")
        assert road.startswith(f"Or commission {cand['name']} — {RECRUIT_MARSHAL_CORPS:,} men for {int(cand['cost']):,}g")
        assert road in NV.over_lift_refusal(w, w.marshals["Soult"])

    def test_lever_down_names_the_emperor_again(self, monkeypatch):
        from backend.game_logic import naval as NV
        _flip(monkeypatch, NV, "THE_LIFT_COUNSEL_NAMES_THE_MARSHALATE", False)
        w = _boot()
        w.nation_gold["France"] = 10_000
        text = NV.over_lift_refusal(w, w.marshals["Soult"])
        assert "Napoleon stands at 10,000" in text
        assert "Or commission" not in text


# ═══════════════════════════════════════════════════════════════════════
# FA-D17 — the paradox block names the truce; the wizard row tells the truth
# ═══════════════════════════════════════════════════════════════════════
class TestD17ParadoxBlockNamesTheTruce:
    def _paradox_world(self):
        from backend.game_logic.diplomacy import get_peace_commitment_conflicts
        w = _boot()
        hard = [c for c in get_peace_commitment_conflicts(w, "France", "Austria", [])
                if c.get("severity") == "HARD_STOP"]
        assert hard, "the 1805 boot carries the Bavaria paradox against Austria"
        return w

    def test_the_block_names_the_armistice_route(self):
        from backend.game_logic.diplomatic_dialogue import generate_dialogue
        w = self._paradox_world()
        dlg = generate_dialogue("proposal_confirm", {"target_nation": "Austria", "proposal_type": "peace"}, w)
        block = dlg.get("commitment_block_warning") or ""
        assert block.startswith("I cannot deliver this, Sire — ")
        assert "Propose an armistice instead" in block
        assert "resolve Bavaria's war first" not in block

    def test_the_wizard_row_is_greyed_with_the_reason(self):
        from backend.game_logic.diplomacy import get_available_diplomatic_actions, set_diplomatic_state
        w = self._paradox_world()
        set_diplomatic_state(w, "France", "Austria", "ARMISTICE")
        row = next(a for a in get_available_diplomatic_actions(w, "Austria") if a.get("action") == "propose_peace")
        assert row["available"] is False
        assert row["disabled_reason"] == "Would break an ally's war — propose an armistice, or settle jointly"
        assert row["disabled_reason_display"] == row["disabled_reason"]

    def test_lever_down_reproduces_the_old_copy_and_a_green_row(self, monkeypatch):
        from backend.game_logic import diplomatic_dialogue as DD
        from backend.game_logic.diplomacy import get_available_diplomatic_actions, set_diplomatic_state
        _flip(monkeypatch, DD, "THE_PARADOX_BLOCK_NAMES_THE_TRUCE", False)
        w = self._paradox_world()
        dlg = DD.generate_dialogue("proposal_confirm", {"target_nation": "Austria", "proposal_type": "peace"}, w)
        assert "resolve Bavaria's war first" in (dlg.get("commitment_block_warning") or "")
        set_diplomatic_state(w, "France", "Austria", "ARMISTICE")
        row = next(a for a in get_available_diplomatic_actions(w, "Austria") if a.get("action") == "propose_peace")
        assert row["available"] is True


# ═══════════════════════════════════════════════════════════════════════
# FA-D18 — the truce projection counts the thaw
# ═══════════════════════════════════════════════════════════════════════
class TestD18TruceProjectionCountsTheThaw:
    def test_the_arithmetic(self):
        from backend.game_logic.diplomacy import armistice_projected_relation, ARMISTICE_THAW_PER_TURN
        assert armistice_projected_relation(-80, 5) == -80 + 5 * ARMISTICE_THAW_PER_TURN
        assert armistice_projected_relation(-80, 0) == -80

    def _truce(self, relation, elapsed):
        from backend.game_logic.diplomacy import set_diplomatic_state
        w = _boot()
        key = w._make_diplo_key("France", "Britain")
        w.nation_relations[key] = relation
        set_diplomatic_state(w, "France", "Britain", "ARMISTICE")
        w.armistice_turns[key] = elapsed
        return w

    @staticmethod
    def _hud_row(w):
        from backend.game_logic.war_status import build_active_wars
        return next(r for r in build_active_wars(w)["wars"] if r.get("opponent") == "Britain")

    def test_the_hud_fork_counts_the_turns_remaining(self):
        from backend.game_logic.diplomacy import ARMISTICE_DURATION, ARMISTICE_THAW_PER_TURN
        w = self._truce(-90, 3)
        row = self._hud_row(w)
        remaining = ARMISTICE_DURATION - 3
        assert row["armistice_remaining"] == remaining
        assert row["armistice_projected_relation"] == -90 + remaining * ARMISTICE_THAW_PER_TURN
        assert row["armistice_projected_outcome"] == "war"

    def test_a_truce_that_will_thaw_over_the_line_projects_peace(self):
        w = self._truce(-64, 3)  # two turns left: -64 + 6 = -58 >= -60
        row = self._hud_row(w)
        assert row["armistice_projected_outcome"] == "peace"

    def test_the_snapshot_says_the_figure_it_will_reach(self):
        from backend.game_logic.diplomacy import build_war_context_snapshot
        w = self._truce(-90, 3)
        snap = build_war_context_snapshot(w, "France", "Britain", "armistice")
        blob = repr(snap)
        assert "will thaw to -84 by expiry" in blob
        assert "projected_relation" in blob

    def test_lever_down_reads_the_relation_now(self, monkeypatch):
        from backend.game_logic import diplomacy as DP
        _flip(monkeypatch, DP, "THE_TRUCE_PROJECTION_COUNTS_THE_THAW", False)
        w = self._truce(-64, 3)
        row = self._hud_row(w)
        assert row["armistice_projected_relation"] == -64
        assert row["armistice_projected_outcome"] == "war"


# ═══════════════════════════════════════════════════════════════════════
# FA-D22 — one word means one thing
# ═══════════════════════════════════════════════════════════════════════
class TestD22OneWordMeansOneThing:
    def test_the_estate_variants_never_say_grievance(self):
        from backend.game_logic import dispatch as D
        variants = D._STANDING_ESCALATION["estate_eroding"]
        assert len(variants) == 3
        assert all("grievance" not in v for v in variants)
        assert any("claim is {age} turns in arrears" in v for v in variants)


# ═══════════════════════════════════════════════════════════════════════
# FA-D24 — Berthier's observation is deterministic per battle
# ═══════════════════════════════════════════════════════════════════════
class TestD24BerthierRotatesHisObservations:
    BR = {"attacker": {"name": "Ney", "nation": "France", "casualties": 3000, "personality": "aggressive"},
          "defender": {"name": "Mack", "nation": "Austria", "casualties": 5000, "personality": "literal"},
          "outcome": "attacker_victory", "attacker_original_strength": 40000,
          "defender_original_strength": 30000, "location": "Swabia", "terrain": "plains"}

    def test_consecutive_battles_between_the_same_pair_rotate_the_bank(self):
        """The row's done-when: same pair, same outcome, same bank — two different lines."""
        from backend.game_logic import battle_report as BR
        BR._OBSERVATION_COUNTS.clear()
        first = BR._pick_observation(dict(self.BR), "France")
        second = BR._pick_observation(dict(self.BR), "France")
        assert first and second and first != second

    def test_the_sequence_is_deterministic_from_a_fresh_process(self):
        from backend.game_logic import battle_report as BR
        BR._OBSERVATION_COUNTS.clear()
        a = [BR._pick_observation(dict(self.BR), "France") for _ in range(4)]
        BR._OBSERVATION_COUNTS.clear()
        b = [BR._pick_observation(dict(self.BR), "France") for _ in range(4)]
        assert a == b

    def test_the_rotator_walks_the_bank(self):
        from backend.game_logic.battle_report import _BankRotator
        assert _BankRotator(0, 1).choice(["a", "b", "c"]) == "b"
        assert _BankRotator(0, 3).choice(["a", "b", "c"]) == "a"
        assert _BankRotator(2, 0).choice(["a", "b", "c"]) == "c"

    def test_the_pick_no_longer_moves_the_mechanics_rng(self, monkeypatch):
        """GR6, measured: the old picker spent module-random draws, so a display
        line shifted every dice roll after it (the BASELINE_SERIES divergence at
        index 10 was this). The rotator spends none."""
        from backend.game_logic import battle_report as BR
        random.seed(3)
        expected = random.random()
        random.seed(3)
        BR._pick_observation(dict(self.BR), "France")
        assert random.random() == expected
        _flip(monkeypatch, BR, "BERTHIER_ROTATES_HIS_OBSERVATIONS", False)
        assert BR._observation_rng(dict(self.BR)) is random
        random.seed(3)
        BR._pick_observation(dict(self.BR), "France")
        assert random.random() != expected

    def test_no_bare_module_choice_survives_inside_the_picker(self):
        src = _read("backend/game_logic/battle_report.py")
        start = src.index("def _pick_observation(")
        end = src.index("\ndef ", start + 10)
        body = src[start:end]
        assert "random.choice(" not in body
        assert body.count("_rng.choice(") >= 40


# ═══════════════════════════════════════════════════════════════════════
# FA-D26 — the Materiel bill on the ledger
# ═══════════════════════════════════════════════════════════════════════
class TestD26MaterielBill:
    def test_the_row_reads_the_store(self):
        from backend.game_logic import ledger as LG
        w = _boot()
        assert LG._build_economy(w, "France")["materiel"] == 0
        w.materiel_spent_this_turn = {"France": 124}
        assert LG._build_economy(w, "France")["materiel"] == 124
        assert LG.build_strategic_ledger(w)["economy"]["materiel"] == 124

    def test_the_row_is_outside_net_by_design(self):
        from backend.game_logic import ledger as LG
        w = _boot()
        before = LG._build_economy(w, "France")
        w.materiel_spent_this_turn = {"France": 900}
        after = LG._build_economy(w, "France")
        assert after["net"] == before["net"]

    def test_the_client_renders_it(self):
        src = (GD / "strategic_ledger.gd").read_text(encoding="utf-8")
        assert '"materiel"' in src

    def test_lever_down_has_no_bill(self, monkeypatch):
        from backend.game_logic import ledger as LG
        _flip(monkeypatch, LG, "THE_LEDGER_SHOWS_THE_MATERIEL_BILL", False)
        w = _boot()
        w.materiel_spent_this_turn = {"France": 124}
        assert LG._build_economy(w, "France")["materiel"] == 0
