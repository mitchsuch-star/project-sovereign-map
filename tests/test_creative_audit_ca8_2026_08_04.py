"""Regression tests for the August 4, 2026 creative-audit fixes (CA8).

Record: `docs/audits/CREATIVE_AUDIT_2026_08_04.md`. One class per routed row,
named for the row id so a failure points straight at the finding.

Scope of this slice: the four code-proven, gate-free P1s (CA8-1/2/4/5) and
five P2/P3 rows (CA8-13/14/15/18/23). CA8-26 and CA8-27 are design calls and
stay at their gates (CA8-D6 / CA8-D2).
"""

import pathlib
import random

import pytest

from backend.campaign_log import format_event_oneliner
from backend.commands.combat_executor import CombatExecutor
from backend.commands.delegation import describe_inferred_bad_odds
from backend.commands.executor import CommandExecutor
from backend.game_logic import dispatch as dispatch_mod
from backend.game_logic import dotation as _dotation
from backend.game_logic import jealousy
from backend.game_logic.coalition import get_threat_tier
from backend.models.region import get_starting_controllers
from backend.models.world_state import WorldState, is_own_soil_recapture


# ════════════════════════════════════════════════════════════════════════
# CA8-1 — report the defending army as an army
# ════════════════════════════════════════════════════════════════════════

class TestCA81DefendingArmyIsAnArmy:
    """The single variable that decided every battle of the played campaign
    was printed only for the side that did not need it."""

    def _reinforced_defender(self):
        random.seed(11)
        world = WorldState()
        executor = CommandExecutor()
        gs = {"world": world}
        for name in list(world.marshals.keys()):
            if name not in ("Ney", "Wellington", "Uxbridge"):
                world.marshals[name].location = "Paris"
        ney = world.get_marshal("Ney")
        ney.location = "Waterloo"
        ney.strength = 40000
        wellington = world.get_marshal("Wellington")
        wellington.location = "Waterloo"
        wellington.strength = 30000
        uxbridge = world.get_marshal("Uxbridge")
        uxbridge.location = "Belgium"          # adjacent -> reinforces
        uxbridge.strength = 25000
        # A willing reinforcer: a rival commits ~0 by design (CO-1b) and
        # correctly prints no mass line, so pin the willing case.
        wellington.set_relationship("Uxbridge", 1)
        uxbridge.set_relationship("Wellington", 1)
        res = executor._execute_attack(ney, "Wellington", world, gs)
        return res, "\n".join(res.get("reinforcement_messages") or [])

    def test_the_defender_massed_strength_is_named(self):
        res, joined = self._reinforced_defender()
        assert "massed effective strength" in joined.lower(), (
            f"the defending army's committed mass was not reported: {joined}")
        assert "Wellington" in joined

    def test_the_defenders_allies_report_their_dead(self):
        res, joined = self._reinforced_defender()
        assert "supporting all" in joined, (
            f"no defender-side ally casualty line: {joined}")

    def test_both_sides_can_be_reported(self):
        """FALSIFIABLE NEGATIVE: the attacker's own two lines still exist.

        The fix is a mirror, not a move — a regression that swapped which
        side is reported would pass every test above.
        """
        import inspect
        src = inspect.getsource(CombatExecutor._execute_attack)
        assert "Massed effective strength" in src
        assert "His supporting ally lost" in src

    def test_the_casualty_line_matches_the_campaign_log_figure(self):
        """The terminal and the log must not disagree by 15x."""
        desc = "Casualties: Ney 8,141, Mack 3,431."
        out = CombatExecutor._rewrite_primary_casualties(
            desc, "Ney", 8141, 2171, "Mack", 3431, 3431)
        assert "8,141" in out, "the whole-army figure must survive"
        assert "2,171" not in out, "the lead's private share must not replace it"
        assert "Ney's army" in out, "and it must not be claimed as one man's"


# ════════════════════════════════════════════════════════════════════════
# CA8-2 — the supply headline
# ════════════════════════════════════════════════════════════════════════

class TestCA82SupplyStrainHeadline:

    def _world_with_strain(self, turns=(4, 5), current=5, region="Lyon"):
        world = WorldState(player_nation="France")
        world.current_turn = current
        r = world.get_region(region)
        r.controller = "France"
        # Park two French marshals there, well over what the province feeds.
        over_cap = int(r.supply_capacity * 1.5) + 20000
        movers = [m for m in world.marshals.values() if m.nation == "France"][:2]
        for m in movers:
            m.location = region
            m.strength = over_cap // 2 + 5000
        for t in turns:
            world.event_log.append({
                "type": "supply_attrition", "nation": "France",
                "turn": t, "region": region, "losses": 5000,
                "marshal": movers[0].name,
            })
        return world, r, movers

    def test_the_word_more_is_gone(self):
        """(a) 'stand MORE men over what X can feed' fired precisely when
        the overage was zero."""
        world, r, movers = self._world_with_strain()
        cand = dispatch_mod._supply_strain_candidate(world, "France")
        assert cand is not None, "fixture produced no candidate"
        assert cand["fields"]["over"] != "more"
        assert cand["fields"]["over"].replace(",", "").isdigit()

    def test_a_resolved_strain_yields_the_lead(self):
        """No honest sentence exists when the stack is no longer over."""
        world, r, movers = self._world_with_strain()
        for m in movers:
            m.location = "Paris"          # dispersed — the strain is over
        assert dispatch_mod._supply_strain_candidate(world, "France") is None

    def test_the_capacity_is_stated(self):
        world, r, movers = self._world_with_strain()
        cand = dispatch_mod._supply_strain_candidate(world, "France")
        assert cand["fields"]["capacity"], "the province's limit is never shown"
        text = dispatch_mod._HEADLINE_TEMPLATES["supply_strain"].format(
            **cand["fields"])
        assert cand["fields"]["capacity"] in text

    def test_the_named_men_are_the_men_who_are_there(self):
        """(b)+(c): the window accumulated names across three turns while
        `over` was computed live, so one sentence described two moments and
        named four marshals who were in other provinces."""
        world, r, movers = self._world_with_strain()
        gone = movers[0]
        gone.location = "Paris"
        cand = dispatch_mod._supply_strain_candidate(world, "France")
        assert cand is not None
        assert gone.name not in cand["fields"]["who"], (
            "a marshal who has left is still being named at the province")
        assert movers[1].name in cand["fields"]["who"]

    def test_a_stale_province_never_leads(self):
        """(d): selection was by CUMULATIVE loss with no requirement that
        any of those turns be the current one, so turn 5 led with turn 4's
        frozen figure about a province nothing was happening in."""
        # Both Lyon turns must sit INSIDE the 3-turn scan window, or the
        # `>= 2 turns` persistence test drops the region for an unrelated
        # reason and the recency filter is never exercised (this fixture
        # was corrected after a mutation sweep showed the pin was inert).
        world, r, movers = self._world_with_strain(turns=(3, 4), current=5)
        # ...but neither is the window's LATEST turn: somewhere else is
        # bleeding now, and Lyon's loss is last week's.
        world.event_log.append({
            "type": "supply_attrition", "nation": "France",
            "turn": 5, "region": "Paris", "losses": 10, "marshal": "Ney",
        })
        cand = dispatch_mod._supply_strain_candidate(world, "France")
        assert cand is None or cand["region"] != "Lyon", (
            "a province with no attrition this turn still leads the dispatch, "
            "quoting a frozen cumulative figure")


# ════════════════════════════════════════════════════════════════════════
# CA8-4 — the game's first modal
# ════════════════════════════════════════════════════════════════════════

class TestCA84BadOddsModal:

    def test_the_question_names_all_three_options(self):
        msg = describe_inferred_bad_odds("Ney", "Mack")
        assert "cancel the order" in msg, (
            "the payload has always carried attack_anyway / hold_position / "
            "cancel_order; the question named two")

    def test_the_muster_note_names_the_enemy(self):
        """'82,072 in all, against 24,000 of Ney's own' — both numbers were
        French, and the enemy's was never printed."""
        world = WorldState(player_nation="France")
        executor = CommandExecutor()
        for name in list(world.marshals.keys()):
            if name not in ("Ney", "Davout", "Wellington"):
                world.marshals[name].location = "Paris"
        ney = world.get_marshal("Ney")
        ney.location = "Waterloo"
        ney.strength = 24000
        davout = world.get_marshal("Davout")
        davout.location = "Belgium"
        davout.strength = 58000
        ney.set_relationship("Davout", 1)
        davout.set_relationship("Ney", 1)
        wellington = world.get_marshal("Wellington")
        wellington.location = "Waterloo"
        wellington.strength = 45000
        note = executor._combat._bad_odds_muster_note(ney, wellington, world)
        if not note:
            pytest.skip("fixture produced no muster (no willing reinforcer)")
        assert "Wellington" in note, f"the enemy is not named: {note}"
        assert "in all, against" not in note, (
            "the inverting phrasing survived")
        # The enemy's STRENGTH is the term that was missing entirely — a
        # name alone still leaves "82,072 against 24,000" unreadable.
        band = CombatExecutor._fog_banded_strength(wellington, world)
        assert band in note, (
            f"the enemy's strength is not stated: {note!r} lacks {band!r}")
        # And both French figures are labelled as French.
        assert "24,000" in note and "Ney" in note

    def test_the_fog_band_is_used_not_the_true_count(self):
        """A fogged enemy must read as its band, never as a leak."""
        world = WorldState(player_nation="France")
        wellington = world.get_marshal("Wellington")
        wellington.strength = 45000
        world.intel.pop(wellington.location, None)
        out = CombatExecutor._fog_banded_strength(wellington, world)
        assert out == "strength unknown"
        assert "45,000" not in out


# ════════════════════════════════════════════════════════════════════════
# CA8-5 — the triplicate headline and the unreachable sentence
# ════════════════════════════════════════════════════════════════════════

class TestCA85DispatchStutter:

    def _mauled_world(self):
        world = WorldState(player_nation="France")
        world.current_turn = 6
        ney = world.get_marshal("Ney")
        ney.location = "Bohemia"
        ney.strength = 6000
        return world, ney

    def _battle(self, name, casualties, turn=6):
        return {
            "type": "battle", "turn": turn, "location": "Bohemia",
            "defender": name, "defender_nation": "France",
            "defender_casualties": casualties,
            "attacker": "ArchdukeCharles", "attacker_nation": "Austria",
        }

    def test_three_battles_by_one_marshal_take_one_slot(self):
        world, ney = self._mauled_world()
        for cas in (2218, 2099, 2269):
            world.event_log.append(self._battle("Ney", cas))
        head = dispatch_mod._build_headline(world, "France")
        assert head is not None
        assert head["class"] == "own_mauled"
        assert not any("mauled" in b for b in head["sub_beats"]), (
            f"the stutter survived: {head['sub_beats']}")

    def test_two_different_marshals_still_get_two_beats(self):
        """FALSIFIABLE NEGATIVE: dedupe must not swallow distinct news."""
        world, ney = self._mauled_world()
        davout = world.get_marshal("Davout")
        davout.location = "Bohemia"
        davout.strength = 6000
        world.event_log.append(self._battle("Ney", 2218))
        world.event_log.append(self._battle("Davout", 2400))
        head = dispatch_mod._build_headline(world, "France")
        rendered = head["text"] + " " + " ".join(head["sub_beats"])
        assert "Ney" in rendered and "Davout" in rendered

    def test_an_ordinary_rout_can_now_be_narrated(self):
        """`own_broken` carries the right sentence, outranks own_mauled at
        90, and could not fire at all: the ordinary break logs
        {"type": "retreat"} while own_broken listened for `marshal_broken`,
        emitted only on the rare no-retreat-route SHATTERED branch."""
        world, ney = self._mauled_world()
        world.event_log.append({
            "type": "retreat", "turn": 6, "marshal": "Ney",
            "nation": "France", "from": "Bohemia", "to": "Bavaria",
            "forced": True,
        })
        head = dispatch_mod._build_headline(world, "France")
        assert head is not None
        assert head["class"] == "own_broken", (
            f"a routed corps still cannot be reported: {head}")
        assert "has been broken" in head["text"]

    def test_an_ordered_withdrawal_is_not_a_rout(self):
        """FALSIFIABLE NEGATIVE: the player's own retreat verb logs the same
        event type and must never read as a break."""
        world, ney = self._mauled_world()
        world.event_log.append({
            "type": "retreat", "turn": 6, "marshal": "Ney",
            "nation": "France", "from": "Bohemia", "to": "Bavaria",
        })
        head = dispatch_mod._build_headline(world, "France")
        assert head is None or head["class"] != "own_broken"

    def test_every_rout_site_stamps_the_flag(self):
        """The flag is the whole mechanism; an unstamped site is a silent
        regression back to the unreachable class."""
        import inspect
        from backend.models import world_state as ws_mod
        from backend.commands import combat_executor as ce_mod
        for mod in (ws_mod, ce_mod):
            src = inspect.getsource(mod)
            for chunk in src.split('"type": "retreat"')[1:]:
                head = chunk[:400]
                if "broken army flees" in head or "vulnerable" in head:
                    assert '"forced": True' in head, (
                        f"a rout site in {mod.__name__} does not stamp forced")


# ════════════════════════════════════════════════════════════════════════
# CA8-6 / CA8-21 — the enemy phase stops printing debug tokens
# ════════════════════════════════════════════════════════════════════════

_GD = (pathlib.Path(__file__).resolve().parents[1] / "godot-client"
       / "project-sovereign" / "scripts")


class TestCA86RawActionVerbs:
    """The six AI-reachable verbs that fell through to
    `action_type.replace("_", " ")` and printed the debug token."""

    FALLTHROUGH = ["grant_dotation", "grant_pension", "form_square",
                   "break_square", "garrison", "naval_expedition"]

    def test_every_fallthrough_verb_now_has_a_render_arm(self):
        src = (_GD / "enemy_phase_dialog.gd").read_text(encoding="utf-8")
        body = src.split("func _format_action", 1)[1].split("\nfunc ", 1)[0]
        for verb in self.FALLTHROUGH:
            assert f'"{verb}":' in body, (
                f"{verb} still renders as its raw action_type token")

    def test_the_arms_never_read_the_message_field(self):
        """The audit named two verified hazards in piping `message`: the fog
        filter gates on a marshal's DESTINATION while raw move prose names
        the ORIGIN, and the prose is second-person player-addressed."""
        src = (_GD / "enemy_phase_dialog.gd").read_text(encoding="utf-8")
        body = src.split("func _format_action", 1)[1].split("\nfunc ", 1)[0]
        assert 'ai_action.get("message"' not in body
        assert 'action.get("message"' not in body


class TestCA821DecreeRegister:
    """`acting_nation` was in scope and ignored, so an electorate issued an
    *Imperial* decree and a foreign court addressed Napoleon as "Sire"."""

    def test_france_keeps_its_exact_wording(self):
        from backend.commands.economy_executor import _decree_preamble
        world = WorldState(player_nation="France")
        assert _decree_preamble(world, "France") == "By Imperial decree"

    def test_a_foreign_court_does_not_decree_imperially(self):
        from backend.commands.economy_executor import _decree_preamble
        world = WorldState(player_nation="France")
        out = _decree_preamble(world, "Bavaria")
        assert "Imperial" not in out
        assert "Bavaria" in out


# ════════════════════════════════════════════════════════════════════════
# CA8-7 — the enemy commander speaks in his own scene
# ════════════════════════════════════════════════════════════════════════

class TestCA87EnemyVoiceInEnemyPhase:

    def test_the_report_renderer_consumes_enemy_voice(self):
        src = (_GD / "enemy_phase_dialog.gd").read_text(encoding="utf-8")
        body = src.split("func _format_berthier_report", 1)[1]
        body = body.split("\nfunc ", 1)[0]
        assert 'report.get("enemy_voice"' in body, (
            "the antagonist is still mute in the phase where his story happens")

    def test_the_backend_still_attaches_it(self):
        """FALSIFIABLE NEGATIVE: a render arm over a key nobody sets is
        worse than no arm at all."""
        import inspect
        src = inspect.getsource(CombatExecutor)
        assert 'result["battle_report"]["enemy_voice"]' in src

    def test_the_two_narrators_are_visually_distinct(self):
        src = (_GD / "utils.gd").read_text(encoding="utf-8")
        assert "COLOR_ENEMY_VOICE" in src
        # Berthier's gold must not be reused for the man he is fighting.
        import re
        voice = re.search(r'COLOR_ENEMY_VOICE = "([0-9A-Fa-f]{6})"', src)
        berthier = re.search(r'COLOR_BERTHIER = "([0-9A-Fa-f]{6})"', src)
        assert voice and berthier
        assert voice.group(1).lower() != berthier.group(1).lower()


# ════════════════════════════════════════════════════════════════════════
# CA8-10 — the two income screens agree
# ════════════════════════════════════════════════════════════════════════

class TestCA810IncomeScreensAgree:

    def test_the_report_net_is_the_ledger_net(self):
        from backend.game_logic.ledger import _build_economy
        world = WorldState(sovereign_map="europe")
        executor = CommandExecutor()
        res = executor._economy._execute_economy(
            {"action": "economy"}, {"world": world})
        event = next(e for e in res["events"] if e["type"] == "economy_report")
        assert event["net"] == int(_build_economy(world, world.player_nation)["net"])

    def test_the_report_does_not_reassemble_the_net_by_hand(self):
        """The defect class, not just the instance: every stream added since
        has had to be remembered in two places, and admiralty/blockade/
        trade/tribute were not."""
        import inspect
        from backend.commands import economy_executor as econ_mod
        src = inspect.getsource(econ_mod.EconomyExecutor._execute_economy)
        assert "_build_economy" in src

    def test_war_effort_explains_itself_at_zero(self):
        """It was guarded by `if war_effort > 0`, and turn 1 — the only turn
        the played campaign ever opened this report — was 0. It then ran
        -8 -> -122 -> -538 -> -1,238 with its cause never stated on any
        surface the player saw.

        The fixture is deliberately the SHIPPED BOOT, which is exactly the
        audit's case: France at war on turn 1 with war_effort still 0. An
        earlier version of this test set `war_exhaustion` to 4, which made
        war_effort non-zero and quietly exercised the OLD branch — found by
        a mutation sweep, and the reason the fixture is now stated rather
        than constructed.
        """
        world = WorldState(sovereign_map="europe")
        nation = world.player_nation
        assert int(world.calculate_turn_income(nation).get("war_effort", 0)) == 0, (
            "fixture: boot war_effort must be 0 for this to be the audit's case")
        assert world.get_nations_at_war_with(nation), "fixture: France boots at war"
        executor = CommandExecutor()
        res = executor._economy._execute_economy(
            {"action": "economy"}, {"world": world})
        assert "War Effort" in res["message"], (
            "the drain that grew to -1,238g is still unexplained on the one "
            "turn a new player reads this screen")


# ════════════════════════════════════════════════════════════════════════
# CA8-11 — the levy names its own condition
# ════════════════════════════════════════════════════════════════════════

class TestCA811RecruitRefusal:

    def test_the_refusal_names_the_reason(self):
        world = WorldState(player_nation="France")
        for m in world.marshals.values():
            if m.nation == "France":
                m.location = "Rome"        # far from Paris, range 1
        world.invalidate_active_nations_cache()
        executor = CommandExecutor()
        res = executor._economy._execute_recruit(
            {"action": "recruit", "amount": 10000, "unit_type": "infantry",
             "target": "Paris"}, {"world": world})
        if res.get("success"):
            pytest.skip("fixture: a marshal was still in range of Paris")
        assert "out of range" in res["message"] or "too weak" in res["message"], (
            f"the refusal still gives no reason: {res['message']}")
        assert "recruit" in res["message"].lower()

    def test_the_headline_states_the_marshal_requirement(self):
        tpl = dispatch_mod._HEADLINE_TEMPLATES["levy_open"]
        assert "marshal must stand" in tpl, (
            "the headline advertises a price and a place but not the condition")


# ════════════════════════════════════════════════════════════════════════
# CA8-22 — the dispossession headline
# ════════════════════════════════════════════════════════════════════════

class TestCA822EstateLost:

    # A CONQUERED province, not homeland — losing home soil is the
    # higher-weighted `home_captured`, which this row does not touch.
    REGION = "Bavaria"

    def _lost(self, endow_to=None):
        world = WorldState(player_nation="France")
        world.current_turn = 6
        if endow_to:
            world.get_marshal(endow_to).dotation_regions = [self.REGION]
        world.event_log.append({
            "type": "region_captured", "turn": 6, "region": self.REGION,
            "captured_by": "Austria", "captured_from": "France",
        })
        return dispatch_mod._build_headline(world, "France")

    def test_a_marshals_duchy_is_named_as_his(self):
        head = self._lost(endow_to="Ney")
        assert head["class"] == "region_lost_estate"
        assert "Ney" in head["text"]
        assert "will not forget" in head["text"]

    def test_an_ordinary_province_keeps_the_plain_sentence(self):
        """FALSIFIABLE NEGATIVE: the map fact is still the map fact."""
        head = self._lost()
        assert head["class"] == "region_lost"
        assert head["text"] == f"Sire — {self.REGION} has been taken by Austria."

    def test_the_human_fact_outranks_the_map_fact(self):
        w = dispatch_mod.HEADLINE_WEIGHTS
        assert w["region_lost_estate"] > w["region_lost"]

    def test_every_class_has_a_template_and_a_note(self):
        """A class without both renders a KeyError at the worst moment."""
        for cls in dispatch_mod.HEADLINE_WEIGHTS:
            assert cls in dispatch_mod._HEADLINE_TEMPLATES, cls
            assert cls in dispatch_mod._HEADLINE_BERTHIER_NOTES, cls


# ════════════════════════════════════════════════════════════════════════
# CA8-13 — no question is asked about liberating France
# ════════════════════════════════════════════════════════════════════════

class TestCA813OwnSoilLiberation:

    def test_the_predicate_knows_its_own_soil(self):
        world = WorldState(player_nation="France")
        assert is_own_soil_recapture(world, "Lyon", "France") is True
        assert is_own_soil_recapture(world, "Netherlands", "France") is False

    def test_liberating_home_soil_asks_nothing_and_blocks_nothing(self):
        world = WorldState(player_nation="France")
        world.diplomatic_states[
            world._make_diplo_key("France", "Britain")] = "WAR"
        lyon = world.regions["Lyon"]
        lyon.controller = "Britain"
        lyon.garrison_strength = 0
        for m in list(world.marshals.values()):
            if m.location == "Lyon":
                m.location = "London"
        ney = world.get_marshal("Ney")
        ney.location = "Paris"
        world.invalidate_active_nations_cache()
        CommandExecutor()._execute_move(ney, "Lyon", world, {"world": world})
        assert world.pending_capture_choice is None, (
            "the player was asked whether to burn his own country")

    def test_foreign_soil_is_still_asked_about(self):
        """FALSIFIABLE NEGATIVE: the guard must not delete the mechanic."""
        world = WorldState(player_nation="France")
        world.diplomatic_states[
            world._make_diplo_key("France", "Britain")] = "WAR"
        world._starting_controllers = {
            **get_starting_controllers(), "Lyon": "Britain"}
        lyon = world.regions["Lyon"]
        lyon.controller = "Britain"
        lyon.garrison_strength = 0
        for m in list(world.marshals.values()):
            if m.location == "Lyon":
                m.location = "London"
        ney = world.get_marshal("Ney")
        ney.location = "Paris"
        world.invalidate_active_nations_cache()
        CommandExecutor()._execute_move(ney, "Lyon", world, {"world": world})
        assert world.pending_capture_choice is not None


# ════════════════════════════════════════════════════════════════════════
# CA8-14 — a routed army does not annex the ground it fled to
# ════════════════════════════════════════════════════════════════════════

class TestCA814RetreatedMarshalCannotCapture:

    def test_p_minus_1_respects_the_retreat_limiter(self):
        from backend.ai.enemy_ai import EnemyAI
        world = WorldState(player_nation="France")
        world.diplomatic_states[
            world._make_diplo_key("France", "Austria")] = "WAR"
        charles = world.get_marshal("ArchdukeCharles")
        charles.location = "Lyon"           # French soil, Austria at war
        world.regions["Lyon"].controller = "France"
        world.regions["Lyon"].garrison_strength = 0
        for m in list(world.marshals.values()):
            if m.location == "Lyon" and m.name != charles.name:
                m.location = "Paris"
        world.invalidate_active_nations_cache()
        charles.retreated_this_turn = True
        ai = EnemyAI(CommandExecutor())
        action, _priority = ai._evaluate_marshal(charles, "Austria", world)
        assert action is not None
        assert action["action"] != "attack", (
            "a corps that routed this turn still annexed the tile it fled to")

    def test_a_standing_marshal_still_takes_the_ground(self):
        """FALSIFIABLE NEGATIVE: the guard must not disable P-1 outright."""
        from backend.ai.enemy_ai import EnemyAI
        world = WorldState(player_nation="France")
        world.diplomatic_states[
            world._make_diplo_key("France", "Austria")] = "WAR"
        charles = world.get_marshal("ArchdukeCharles")
        charles.location = "Lyon"
        world.regions["Lyon"].controller = "France"
        world.regions["Lyon"].garrison_strength = 0
        for m in list(world.marshals.values()):
            if m.location == "Lyon" and m.name != charles.name:
                m.location = "Paris"
        world.invalidate_active_nations_cache()
        charles.retreated_this_turn = False
        ai = EnemyAI(CommandExecutor())
        action, _priority = ai._evaluate_marshal(charles, "Austria", world)
        assert action is not None
        assert action["action"] in ("attack", "unfortify"), (
            f"P-1 no longer captures undefended enemy ground: {action}")

    def test_the_guard_is_at_the_rung(self):
        """Belt-and-braces on the seam itself: reordering or deleting the
        guard is the regression, and it is one line."""
        import inspect
        from backend.ai import enemy_ai as ai_mod
        src = inspect.getsource(ai_mod)
        marker = "PRIORITY -1: CAPTURE CURRENT REGION"
        assert marker in src
        block = src.split(marker, 1)[1][:2000]
        assert 'retreated_this_turn' in block, (
            "P-1 no longer consults the retreat limiter")


# ════════════════════════════════════════════════════════════════════════
# CA8-15 — no nation is announced and then silent
# ════════════════════════════════════════════════════════════════════════

class TestCA815EmptyNationHeader:

    def test_a_nation_emptied_by_the_collapse_is_pruned(self):
        from backend.main import _collapse_enemy_phase_composition
        phase = {"nations": {
            "Prussia": {"actions": [
                {"ai_action": {"action": "fortify", "marshal": "Blucher"}},
                {"ai_action": {"action": "unfortify", "marshal": "Blucher"}},
            ]},
            "Austria": {"actions": [
                {"ai_action": {"action": "attack", "marshal": "Charles"}},
            ]},
        }}
        _collapse_enemy_phase_composition(phase)
        assert "Prussia" not in phase["nations"], (
            "a great power is announced by name and says nothing")
        assert "Austria" in phase["nations"]


# ════════════════════════════════════════════════════════════════════════
# CA8-18 — the threat gauge
# ════════════════════════════════════════════════════════════════════════

class TestCA818ThreatTier:

    def test_a_formed_coalition_is_not_brewing(self):
        assert get_threat_tier(97, coalition_formed=True) == "Formed"

    def test_the_legacy_signature_is_byte_identical(self):
        """FALSIFIABLE NEGATIVE: every existing caller must be unchanged."""
        for level in (0, 25, 50, 75, 97):
            assert get_threat_tier(level) == get_threat_tier(
                level, coalition_formed=False)


# ════════════════════════════════════════════════════════════════════════
# CA8-23 — no raw internal key in the campaign log
# ════════════════════════════════════════════════════════════════════════

class TestCA823ProposalLabel:

    def test_the_scorer_variant_never_reaches_the_player(self):
        line = format_event_oneliner({
            "type": "proposal_arrived", "turn": 3,
            "source": "Austria", "proposal_type": "armistice_losing",
        })
        assert "armistice losing" not in line, (
            "an internal scorer distinction is being read as English")
        assert "armistice" in line

    @pytest.mark.parametrize("raw,forbidden", [
        ("design_purchase", "design purchase"),
        ("sell_neutrality", "sell neutrality"),
        ("offer_vassalage", "offer vassalage"),
        ("ultimatum_demand", "ultimatum demand"),
        ("friendly_gift", "friendly gift"),
        ("broker_peace", "broker peace"),
    ])
    def test_the_whole_family_is_mapped(self, raw, forbidden):
        line = format_event_oneliner({
            "type": "proposal_arrived", "turn": 3,
            "source": "Austria", "proposal_type": raw,
        })
        assert forbidden not in line, f"{raw} still renders as its token"

    def test_a_typeless_event_still_reads_as_a_sentence(self):
        line = format_event_oneliner({
            "type": "proposal_arrived", "turn": 3, "source": "Austria",
        })
        assert "proposal" in line
        assert "Unknown" not in line


# ════════════════════════════════════════════════════════════════════════
# CA8-9 — the campaign told a five-beat tragedy and joined none of it
# ════════════════════════════════════════════════════════════════════════

class TestCA89TheArcJoinsTheBeats:
    """Crowned (T3) -> ennobled Duke of Carniola (T8) -> broken at Bohemia
    (T10) -> estate confiscated (T10) -> the laurels have passed (T12), and
    not one line referred to any other. The arc builder read only defeats,
    retreats and attackers, so it could narrate a marshal being BEATEN and
    never one RISING.
    """

    def _world(self, turn=10):
        from tests.conftest import MarshalFactory, WorldFactory
        ney = MarshalFactory.infantry(name="Ney", location="Bohemia",
                                      strength=18000)
        world = WorldFactory.with_marshals([ney], current_turn=turn)
        world.event_log = []
        return world, ney

    def _crown(self, world, turn, marshal="Ney"):
        world.event_log.append({"type": "glory_crowned", "marshal": marshal,
                                "nation": "France", "turn": turn})

    def _endow(self, world, turn, region="Carniola",
               title=None, marshal="Ney"):
        # Review fix: the title MUST come from the real producer. The first
        # draft hardcoded "the Duchy of Carniola" — a string no producer in
        # the repo emits — so the assertion below passed while production
        # rendered "endowed with Duke of Carniola".
        from backend.game_logic.dotation import derive_title
        world.event_log.append({"type": "dotation_granted", "marshal": marshal,
                                "nation": "France", "region": region,
                                "title": derive_title(region)
                                if title is None else title,
                                "turn": turn})

    def _confiscate(self, world, turn, region="Carniola", marshal="Ney"):
        world.event_log.append({"type": "estate_confiscated",
                                "marshal": marshal, "nation": "France",
                                "region": region, "confiscated_by": "Austria",
                                "turn": turn})

    def _beat(self, world, turn, marshal="Ney"):
        world.event_log.append({
            "type": "battle", "turn": turn, "attacker": "ArchdukeCharles",
            "defender": marshal, "attacker_nation": "Austria",
            "defender_nation": "France", "outcome": "attacker_victory",
            "location": "Bohemia", "defender_casualties": 2218})

    # ── the join itself ──────────────────────────────────────────────────

    def test_the_whole_tragedy_becomes_one_sentence(self):
        world, ney = self._world(turn=10)
        self._crown(world, 7)
        self._endow(world, 8)
        self._beat(world, 10)
        self._confiscate(world, 10)
        ney.glory_crowned = False        # the laurels have passed
        arc = dispatch_mod._build_marshal_arcs(world, "France")["Ney"]
        line = arc["reversal_line"]
        # the rise
        assert "crowned" in line
        # The ESTATE is the object of "endowed with", never the man's
        # honorific — `derive_title` returns "Duke of Carniola".
        from backend.game_logic.dotation import derive_estate_noun
        assert derive_estate_noun("Carniola") in line, line
        assert "endowed with Duke of" not in line, line
        # the fall
        assert "beaten" in line
        # the dispossession, named with its taker
        assert "Austria" in line and "Carniola" in line
        # and the crown, derived from live state with no event of its own
        assert "laurels" in line
        assert arc["crown_lost"] is True and arc["estate_lost"] is True

    def test_the_gap_between_beats_is_spoken(self):
        """Beats up to five turns apart must not read as simultaneous."""
        world, ney = self._world(turn=10)
        self._crown(world, 7)
        self._beat(world, 10)
        line = dispatch_mod._build_marshal_arcs(
            world, "France")["Ney"]["reversal_line"]
        assert "three turns ago" in line, line

    # ── falsifiable negatives ────────────────────────────────────────────

    def test_a_pure_ascent_makes_no_arc_and_no_headline(self):
        """CA8-26 (no headline class for a French success) is GATED. The
        reversal must be structurally unable to build it: a rise with no
        fall produces no arc at all, so it can never reach the headline."""
        world, ney = self._world(turn=8)
        self._crown(world, 7)
        self._endow(world, 8)
        ney.glory_crowned = True
        assert dispatch_mod._build_marshal_arcs(world, "France") == {}

    def test_a_fall_with_no_rise_keeps_the_plain_arc(self):
        """The pre-CA8-9 behaviour is untouched when there is no ascent.

        Two DIFFERENT attackers, deliberately: one attacker twice running is
        the `hunted_by` arm, which outranks the defeat tally.
        """
        world, ney = self._world(turn=10)
        for turn, foe in ((9, "ArchdukeCharles"), (10, "Blucher")):
            world.event_log.append({
                "type": "battle", "turn": turn, "attacker": foe,
                "defender": "Ney", "attacker_nation": "Austria",
                "defender_nation": "France",
                "outcome": "attacker_victory", "location": "Bohemia",
                "defender_casualties": 2218})
        arc = dispatch_mod._build_marshal_arcs(world, "France")["Ney"]
        assert arc["reversal_line"] == ""
        assert arc["rose"] is False
        assert "defeats in as many turns" in arc["line"]

    def test_an_enemy_rise_is_never_read(self):
        world, ney = self._world(turn=10)
        world.event_log.append({"type": "glory_crowned", "marshal": "Ney",
                                "nation": "Austria", "turn": 8})
        self._beat(world, 10)
        arc = dispatch_mod._build_marshal_arcs(world, "France").get("Ney")
        assert arc is None or arc["reversal_line"] == ""

    # ── the headline seam ────────────────────────────────────────────────

    def test_the_reversal_outranks_the_bare_fall(self):
        w = dispatch_mod.HEADLINE_WEIGHTS
        assert w["marshal_reversal"] > w["own_broken"] > w["own_mauled"]

    def test_the_reversal_absorbs_the_plain_fall_beat(self):
        """CA8-5 dedupes on (class, identity), so a reversal ABOVE
        `own_broken` would have led with the joined sentence and restated
        the bare one as its own sub-beat — the duplicate-beat shape CA8-5
        was landed to kill."""
        world, ney = self._world(turn=10)
        self._crown(world, 8)
        self._endow(world, 8)
        ney.glory_crowned = False
        world.event_log.append({"type": "retreat", "marshal": "Ney",
                                "nation": "France", "turn": 10,
                                "forced": True, "region": "Bohemia"})
        head = dispatch_mod._build_headline(world, "France")
        assert head["class"] == "marshal_reversal"
        joined = " ".join(head["sub_beats"])
        assert "corps has been broken" not in joined, head["sub_beats"]

    def test_another_marshals_break_is_not_absorbed(self):
        """FALSIFIABLE NEGATIVE for the absorption: it is keyed on the man,
        so a different marshal breaking the same turn keeps his own beat."""
        from tests.conftest import MarshalFactory
        world, ney = self._world(turn=10)
        soult = MarshalFactory.infantry(name="Soult", location="Tyrol",
                                        strength=9000)
        world.marshals["Soult"] = soult
        self._crown(world, 8)
        ney.glory_crowned = False
        for who in ("Ney", "Soult"):
            world.event_log.append({"type": "retreat", "marshal": who,
                                    "nation": "France", "turn": 10,
                                    "forced": True, "region": "Bohemia"})
        head = dispatch_mod._build_headline(world, "France")
        assert head["class"] == "marshal_reversal"
        assert any("Soult" in b for b in head["sub_beats"]), head["sub_beats"]

    def test_the_roster_note_prefers_the_joined_line(self):
        world, ney = self._world(turn=10)
        self._crown(world, 8)
        self._endow(world, 8)
        self._beat(world, 10)
        ney.glory_crowned = False
        rows = dispatch_mod._build_marshal_status(world, "France")
        row = next(r for r in rows if r["name"] == "Ney")
        assert "crowned" in row["arc_note"]
        assert row["status_note"] == row["arc_note"]


# ════════════════════════════════════════════════════════════════════════
# CA8-8 — every grievance byte-identical, no recurrence register, and an
#         inserted rung starving the one below it
# ════════════════════════════════════════════════════════════════════════

class TestCA88GrievanceRecurrence:
    """One dispatch printed, in this order: "...has cooled with time" /
    "...appears envious of..." / "...has become entrenched." The STATE is
    legal — the timer expires, `jealous_of` clears, and step 3 re-evaluates
    the man just cleared. The defect is that no template carried a
    recurrence register, so a legal escalation was indistinguishable from a
    state bug on the page.
    """

    def _pair(self, turn=5, personality="aggressive"):
        from tests.conftest import MarshalFactory, WorldFactory
        murat = MarshalFactory.infantry(name="Murat", personality=personality)
        davout = MarshalFactory.infantry(name="Davout")
        world = WorldFactory.with_marshals([murat, davout], current_turn=turn)
        return world, murat, davout

    def _fire(self, world, a, b, turn=None):
        if turn is not None:
            world.current_turn = turn
        events = []
        jealousy.apply_jealousy(world, a, b, delta=3, threshold=2,
                                events=events)
        a.jealous_of = None          # the timer expires between fires
        return next(e["message"] for e in events
                    if e["type"] == "jealousy_fired")

    # ── the register ─────────────────────────────────────────────────────

    def test_a_first_grievance_reads_as_fresh_news(self):
        world, murat, davout = self._pair()
        line = self._fire(world, murat, davout, turn=5)
        assert "again" not in line
        assert "appears envious of" in line

    def test_a_second_grievance_says_again_and_how_long_it_held(self):
        """The interval is FIRE-TO-FIRE, and must be named as such.

        Corrected after review: the first version of this test pinned
        "4 turns after it cooled", which is never true — `jealousy_history`
        records fire turns only, and a grievance stands 2-5 turns before the
        timer can expire, so the figure overstated time-since-cooling by the
        whole duration. The test pinned the defect.
        """
        world, murat, davout = self._pair()
        self._fire(world, murat, davout, turn=5)
        line = self._fire(world, murat, davout, turn=9)
        assert "again" in line, line
        assert "4 turns after the last" in line, line

    def test_no_grievance_line_claims_a_cooling_interval(self):
        """FALSIFIABLE NEGATIVE for the above, over every reachable arm:
        the data cannot support a cooled-to-refire interval, so no arm may
        assert one."""
        world, murat, davout = self._pair()
        for turn in (3, 5, 6, 9, 14):
            line = self._fire(world, murat, davout, turn=turn)
            assert "after it cooled" not in line, line

    def test_a_third_grievance_counts(self):
        world, murat, davout = self._pair()
        self._fire(world, murat, davout, turn=3)
        self._fire(world, murat, davout, turn=5)
        line = self._fire(world, murat, davout, turn=8)
        assert "for the third time" in line, line

    def test_the_same_turn_refire_names_itself(self):
        """The exact played sequence: cleared and re-fired inside ONE
        council, two lines below the sentence announcing it had cooled."""
        world, murat, davout = self._pair()
        self._fire(world, murat, davout, turn=6)
        line = self._fire(world, murat, davout, turn=6)
        assert "the same day it was set aside" in line, line

    # ── the monoculture ──────────────────────────────────────────────────

    def test_the_expression_is_not_one_fixed_string_per_personality(self):
        """Measured in the played campaign: an aggressive marshal ALWAYS
        said "grown restless for glory" — three strings for the whole game.
        """
        world, murat, davout = self._pair()
        seen = {self._fire(world, murat, davout, turn=t)
                for t in (3, 6, 9, 12, 15)}
        expressions = {s.split(" — he has ")[-1] for s in seen}
        assert len(expressions) > 1, expressions

    def test_every_personality_has_a_bank(self):
        for p in ("aggressive", "cautious", "literal"):
            assert len(jealousy._JEALOUSY_EXPRESSIONS[p]) >= 2

    def test_the_expression_is_deterministic(self):
        """RNG-free: the same campaign must render the same words twice."""
        picks = []
        for _ in range(2):
            world, murat, davout = self._pair()
            picks.append(self._fire(world, murat, davout, turn=5))
        assert picks[0] == picks[1]

    # ── the falsified promise ────────────────────────────────────────────

    def test_an_entrenched_wound_does_not_close_on_its_own(self):
        """Tier 2 announces "The wound will not close on its own" and
        applies a permanent -1. Two turns later the grievance timer expired
        and the game said the resentment had "cooled with time", falsifying
        its own sentence in front of the player. Both were true of
        DIFFERENT things; the line now says which one cooled."""
        world, murat, davout = self._pair()
        jealousy._set_escalation_level(murat, "Davout",
                                       jealousy.ESCALATION_PERMANENT_LEVEL)
        murat.jealous_of = "Davout"
        events = []
        jealousy.clear_jealousy(world, murat, resolved_by_action=False,
                                events=events, reason="time")
        line = next(e["message"] for e in events
                    if e["type"] == "jealousy_resolved")
        assert "cooled with time" not in line, line
        assert "has not been" in line, line

    def test_an_ordinary_grievance_still_cools_with_time(self):
        """FALSIFIABLE NEGATIVE: the plain wording survives for a pair the
        game never called permanent."""
        world, murat, davout = self._pair()
        murat.jealous_of = "Davout"
        murat.jealousy_history = {"Davout": [4]}
        events = []
        jealousy.clear_jealousy(world, murat, resolved_by_action=False,
                                events=events, reason="time")
        line = next(e["message"] for e in events
                    if e["type"] == "jealousy_resolved")
        assert "cooled with time" in line

    # ── the second channel ───────────────────────────────────────────────

    def test_the_campaign_log_stops_calling_a_tier_one_wound_entrenched(self):
        """The payload has always carried `level` and the formatter ignored
        it, so the same event read "a matter of concern" in the dispatch and
        "entrenched" in the log on the same turn."""
        line = format_event_oneliner({
            "type": "jealousy_escalation", "turn": 3, "marshal": "Murat",
            "target": "Davout", "nation": "France", "level": 1})
        assert "entrenched" not in line, line
        assert "matter of concern" in line

    def test_the_campaign_log_still_says_entrenched_at_tier_two(self):
        line = format_event_oneliner({
            "type": "jealousy_escalation", "turn": 3, "marshal": "Murat",
            "target": "Davout", "nation": "France", "level": 2})
        assert "entrenched" in line

    def test_a_pre_ca8_save_keeps_the_old_wording(self):
        """`level` is absent on saves written before this landed."""
        line = format_event_oneliner({
            "type": "jealousy_escalation", "turn": 3, "marshal": "Murat",
            "target": "Davout", "nation": "France"})
        assert "entrenched" in line

    def test_the_campaign_log_marks_a_recurrence(self):
        first = format_event_oneliner({
            "type": "jealousy_fired", "turn": 3, "marshal": "Murat",
            "target": "Davout", "nation": "France",
            "personality": "aggressive", "fires": 1})
        again = format_event_oneliner({
            "type": "jealousy_fired", "turn": 9, "marshal": "Murat",
            "target": "Davout", "nation": "France",
            "personality": "aggressive", "fires": 3})
        assert "again" in again and "again" not in first

    # ── the contract ─────────────────────────────────────────────────────

    def test_the_register_adds_no_serialized_field(self):
        """It is derived from `jealousy_history`, a list of fire turns that
        was already serialized and already read by `_lifetime_fires`."""
        from tests.conftest import MarshalFactory
        keys = set(MarshalFactory.infantry(name="X").to_dict())
        assert "jealousy_history" in keys
        for invented in ("jealousy_recurrence", "jealousy_last_cleared_turn",
                         "jealousy_fire_count", "last_grievance_turn"):
            assert invented not in keys


class TestCA88TheStarvedRung:
    """Berthier closed 7 of 11 played dispatches on the byte-identical "The
    marshals' rivalries demand attention, Sire" and never once mentioned
    Murat standing idle at Rhineland with 19,312 men for nine turns."""

    SITUATION = {"bankrupt": False, "treasury_delta": 100}

    def _note(self, marshals, world=None):
        return dispatch_mod._pick_berthier_note(
            world, "France", marshals, dict(self.SITUATION))

    def test_the_idle_rung_reads_the_integer_not_the_prose(self):
        """The rung recovered the count with `int(status_note.split()[0])`
        off a slot the arc note legitimately overwrites (pinned by
        test_arc_upgrades_the_status_note)."""
        note = self._note([{
            "name": "Murat", "status": "idle_restless", "strength": 19312,
            "status_note": "Hunted by Archduke Charles across 2 frontiers "
                           "- stands at Rhineland with 19,312 men.",
            "idle_turns": 9}])
        assert "Murat" in note and "impatient" in note.lower()

    def test_a_beaten_marshal_is_not_reported_as_impatient(self):
        """FALSIFIABLE NEGATIVE, and the sharper half of the bug: the arc
        shape "4 defeats in as many turns" PARSED cleanly and compared a
        defeat tally against an idle threshold, so a marshal beaten four
        turns running was reported to the Emperor as growing impatient for
        action."""
        note = self._note([{
            "name": "Ney", "status": "idle_restless", "strength": 8000,
            "status_note": "4 defeats in as many turns - 8,000 men remain "
                           "at Bohemia.",
            "idle_turns": 0}])
        assert "impatient" not in note.lower(), note

    def test_an_idle_army_is_never_called_ready(self):
        """Below rung 4 the ladder used to reach "Your armies stand ready,
        Sire. The initiative is ours." - not a silent default but an active
        and false reassurance about an army standing still."""
        note = self._note([{
            "name": "Murat", "status": "idle_restless", "strength": 19312,
            "status_note": "3 turns idle.", "idle_turns": 3}])
        assert "stand ready" not in note.lower(), note
        assert "initiative is ours" not in note.lower(), note

    def test_the_grievance_note_names_the_rival(self):
        from tests.conftest import MarshalFactory, WorldFactory
        murat = MarshalFactory.infantry(name="Murat", personality="aggressive")
        davout = MarshalFactory.infantry(name="Davout")
        murat.jealous_of = "Davout"
        murat.jealousy_turns_remaining = 3
        world = WorldFactory.with_marshals([murat, davout], current_turn=5)
        note = self._note([{"name": "Murat", "status": "awaiting",
                            "strength": 19312, "status_note": "",
                            "idle_turns": 0}], world=world)
        assert "Davout" in note, note

    def test_the_grievance_note_names_the_idleness_when_both_are_true(self):
        """Being passed over is what the grievance IS - one sentence, both
        jobs, and the actionable fact stops being unreachable behind a rung
        that outranks it."""
        from tests.conftest import MarshalFactory, WorldFactory
        murat = MarshalFactory.infantry(name="Murat", personality="aggressive")
        davout = MarshalFactory.infantry(name="Davout")
        murat.jealous_of = "Davout"
        murat.jealousy_turns_remaining = 3
        world = WorldFactory.with_marshals([murat, davout], current_turn=9)
        note = self._note([{"name": "Murat", "status": "idle_restless",
                            "strength": 19312, "status_note": "9 turns idle.",
                            "idle_turns": 9}], world=world)
        assert "Davout" in note and "9 turns" in note, note

    def test_the_documented_ladder_matches_the_code(self):
        """The docstring listed six rungs and never mentioned the jealousy
        rung inserted above the idle one.

        Anchored to the numbered LIST, not to the substring "3.5": the
        mutation sweep for this slice caught the first version passing with
        the ladder entry deleted, because the explanatory paragraph below
        the list also says "3.5".
        """
        import re
        doc = dispatch_mod._pick_berthier_note.__doc__ or ""
        rungs = [ln.strip() for ln in doc.splitlines()
                 if re.match(r"^\s*3\.5\s", ln)]
        assert len(rungs) == 1, doc
        assert "grievance" in rungs[0].lower(), rungs
        # and it must sit between the treasury rung and the idle rung
        order = [doc.index(x) for x in ("3. Treasury", "3.5 ", "4. Aggressive")]
        assert order == sorted(order), order


# ════════════════════════════════════════════════════════════════════════
# CA8-25 — the diorama was built and then discarded
# ════════════════════════════════════════════════════════════════════════

class TestCA825BlockedPathKeepsTheDiorama:
    """Filed as "no diorama is built" for the `press on` resolution — the
    played campaign's largest battle, 82,072 men massed. It IS built: every
    `attack_anyway` arm re-enters `_execute_attack`. The blocked-path arms
    rebuild a fresh response through an allowlist that never carried it.
    """

    def test_the_allowlist_carries_the_diorama(self):
        from backend.commands import strategic as strategic_mod
        assert "battle_diorama" in strategic_mod._COMBAT_PASSTHROUGH_FIELDS

    def test_a_rebuilt_response_keeps_the_payload(self):
        from backend.commands.strategic import _carry_combat_fields
        inner = {
            "battle_diorama": {"significant": True, "contingents": [1, 2]},
            "battle_report": {"x": 1},
            "new_state": "must not travel",
        }
        out = _carry_combat_fields({"success": True, "message": "rebuilt"},
                                   inner)
        assert out["battle_diorama"]["significant"] is True
        assert out["battle_report"] == {"x": 1}

    def test_the_allowlist_is_still_an_allowlist(self):
        """FALSIFIABLE NEGATIVE: widening it must not have turned it into a
        blanket copy — `new_state` carries circular refs and must never
        reach a response."""
        from backend.commands.strategic import _carry_combat_fields
        out = _carry_combat_fields(
            {"success": True}, {"new_state": object(), "secret": 1})
        assert "new_state" not in out
        assert "secret" not in out

    def test_absent_payload_adds_no_key(self):
        from backend.commands.strategic import _carry_combat_fields
        out = _carry_combat_fields({"success": True}, {"battle_report": None})
        assert "battle_diorama" not in out
        assert "battle_report" not in out


class TestCA89ReviewFixes:
    """Found by rendering the sentence rather than asserting keywords on it —
    the schema-shaped tests above all passed while the prose was wrong."""

    def _arc(self, events, turn=10, crowned_now=False):
        from tests.conftest import MarshalFactory, WorldFactory
        ney = MarshalFactory.infantry(name="Ney", location="Bohemia",
                                      strength=18000)
        world = WorldFactory.with_marshals([ney], current_turn=turn)
        world.event_log = list(events)
        ney.glory_crowned = crowned_now
        return dispatch_mod._build_marshal_arcs(world, "France").get("Ney")

    CROWN = {"type": "glory_crowned", "marshal": "Ney", "nation": "France",
             "turn": 7}
    BEAT = {"type": "battle", "turn": 10, "attacker": "ArchdukeCharles",
            "defender": "Ney", "attacker_nation": "Austria",
            "defender_nation": "France", "outcome": "attacker_victory",
            "location": "Bohemia", "defender_casualties": 2218}

    def test_the_ascent_is_a_closed_appositive(self):
        """"Ney, crowned three turns ago has been beaten" is a run-on."""
        line = self._arc([self.CROWN, self.BEAT],
                         crowned_now=True)["reversal_line"]
        assert "ago, has been" in line, line

    def test_an_ordered_withdrawal_is_not_a_ruin(self):
        """FALSIFIABLE NEGATIVE. `movement_executor`'s own retreat verb logs
        the same `retreat` event type as a rout; only the four rout sites
        stamp `forced: True` (the discipline CA8-5 landed for `own_broken`).
        Without that check a crowned marshal the player simply repositioned
        was narrated as a tragedy."""
        arc = self._arc([self.CROWN,
                         {"type": "retreat", "marshal": "Ney",
                          "nation": "France", "turn": 10,
                          "region": "Bohemia"}],
                        crowned_now=True)
        assert arc is None, arc

    def test_a_forced_rout_still_counts_as_a_fall(self):
        """The mirror of the above — the flag is what separates them."""
        arc = self._arc([self.CROWN,
                         {"type": "retreat", "marshal": "Ney",
                          "nation": "France", "turn": 10, "forced": True,
                          "region": "Bohemia"}],
                        crowned_now=True)
        assert arc is not None
        assert "driven back" in arc["reversal_line"]

    def test_the_tail_carries_exactly_one_conjunction(self):
        line = self._arc([
            self.CROWN,
            {"type": "dotation_granted", "marshal": "Ney", "nation": "France",
             "region": "Carniola",
             "title": _dotation.derive_title("Carniola"),
             "turn": 8},
            self.BEAT,
            {"type": "estate_confiscated", "marshal": "Ney",
             "nation": "France", "region": "Carniola",
             "confiscated_by": "Austria", "turn": 10},
        ])["reversal_line"]
        assert "— and" not in line, line
        assert line.count(" and ") == 2, line          # rise-join + tail-join
        assert line.endswith("."), line

    def test_no_sentence_is_left_dangling(self):
        """Every reachable shape ends in a full stop and never doubles
        punctuation or leaves an em-dash hanging."""
        cases = [
            [self.CROWN, self.BEAT],
            [self.CROWN, {"type": "dotation_granted", "marshal": "Ney",
                          "nation": "France", "region": "Carniola",
                          "title": "", "turn": 8}, self.BEAT],
            [self.CROWN, {"type": "estate_confiscated", "marshal": "Ney",
                          "nation": "France", "region": "Carniola",
                          "confiscated_by": "", "turn": 10}],
        ]
        for ev in cases:
            arc = self._arc(ev, crowned_now=True)
            if not arc or not arc["reversal_line"]:
                continue
            line = arc["reversal_line"]
            assert line.endswith("."), line
            assert ".." not in line and ",," not in line, line
            assert "—." not in line and "  " not in line, line
            assert "None" not in line, line


# ════════════════════════════════════════════════════════════════════════
# CA8-9/CA8-8 — the 129-agent adversarial review of e5b18c1
#
# Every pin below corresponds to a finding that survived TWO independent
# skeptics. Three of them (§1.11) exist because the seam was unobserved by
# a 16,259-test suite: the review's closing note was that the slice's own
# 21-mutation sweep "was chosen around the tests rather than around the
# seams", which was fair.
# ════════════════════════════════════════════════════════════════════════

class TestCA89ReviewRound2:

    def _world(self, turn=10, marshals=("Ney",)):
        from tests.conftest import MarshalFactory, WorldFactory
        ms = [MarshalFactory.infantry(name=n, location="Bohemia",
                                      strength=27000) for n in marshals]
        world = WorldFactory.with_marshals(ms, current_turn=turn)
        world.event_log = []
        return world

    def _crown(self, w, turn, who="Ney"):
        w.event_log.append({"type": "glory_crowned", "marshal": who,
                            "nation": "France", "turn": turn})

    def _endow(self, w, turn, who="Ney", region="Carniola"):
        from backend.game_logic.dotation import derive_title
        w.event_log.append({"type": "dotation_granted", "marshal": who,
                            "nation": "France", "region": region,
                            "title": derive_title(region), "turn": turn})

    def _beat(self, w, turn, who="Ney", cas=9000, foe="ArchdukeCharles"):
        w.event_log.append({
            "type": "battle", "turn": turn, "attacker": foe, "defender": who,
            "attacker_nation": "Austria", "defender_nation": "France",
            "outcome": "attacker_victory", "location": "Bohemia",
            "defender_casualties": cas})

    def _rout(self, w, turn, who="Ney"):
        w.event_log.append({"type": "retreat", "marshal": who,
                            "nation": "France", "turn": turn,
                            "forced": True, "region": "Bohemia"})

    # ── §1.2 crown_lost is not a fall ────────────────────────────────────

    def test_a_colleagues_victory_is_not_this_marshals_tragedy(self):
        """`recompute_crowns` clears `glory_crowned` when a same-nation
        marshal out-scores the holder — i.e. on a FRENCH SUCCESS. Because
        `crown_lost` implies `crown_turn is not None`, which is itself a
        disjunct of `rose`, one event satisfied BOTH halves of `rose and
        fell`: a marshal who fought nothing and lost nothing produced a
        weight-91 tragedy headline."""
        w = self._world(turn=9)
        self._crown(w, 7)                       # crowned, then overtaken
        arcs = dispatch_mod._build_marshal_arcs(w, "France")
        assert arcs == {}, arcs

    def test_a_crown_lost_beside_a_real_fall_is_still_narrated(self):
        """FALSIFIABLE NEGATIVE: `crown_lost` survives as the TAIL clause."""
        w = self._world(turn=10)
        self._crown(w, 7)
        self._beat(w, 10)
        line = dispatch_mod._build_marshal_arcs(w, "France")["Ney"]["reversal_line"]
        assert "laurels" in line, line

    def test_a_vacant_crown_is_not_claimed_by_another(self):
        """`recompute_crowns` VACATES the crown on a top-of-ladder tie, so
        "the laurels have passed to another" was a flat falsehood — nobody
        holds them."""
        w = self._world(turn=10, marshals=("Ney", "Davout"))
        self._crown(w, 7)
        self._beat(w, 10)
        for m in w.marshals.values():
            m.glory_crowned = False             # tie -> crown vacated
        line = dispatch_mod._build_marshal_arcs(w, "France")["Ney"]["reversal_line"]
        assert "passed to another" not in line, line
        assert "vacant" in line, line

    def test_a_real_successor_is_named_as_one(self):
        w = self._world(turn=10, marshals=("Ney", "Davout"))
        self._crown(w, 7)
        self._beat(w, 10)
        w.marshals["Davout"].glory_crowned = True
        line = dispatch_mod._build_marshal_arcs(w, "France")["Ney"]["reversal_line"]
        assert "passed to another" in line, line

    # ── §1.1 the reversal must be current news ───────────────────────────

    def test_a_stale_fall_never_takes_the_lead(self):
        """The arc builder reads a SIX-turn window; every other headline
        candidate is scored from a two-turn one. `marshal_reversal` was
        therefore a state-derived class that re-manufactured its candidate
        every turn — and was not in STANDING_HEADLINE_CLASSES, so PC-7's
        cooldown could not govern it and the July-19 exact-repeat demotion
        could not catch it (the sentence changes every turn as
        `_turns_ago_phrase` counts up). Measured: 4-6 consecutive leads."""
        w = self._world(turn=13)
        self._crown(w, 8)
        self._endow(w, 8)
        self._beat(w, 9)                        # four turns stale
        arc = dispatch_mod._build_marshal_arcs(w, "France")["Ney"]
        assert arc["reversal_line"], "the roster note keeps its 6-turn memory"
        head = dispatch_mod._build_headline(w, "France")
        assert head is None or head["class"] != "marshal_reversal", head

    def test_a_fresh_fall_does_take_the_lead(self):
        """FALSIFIABLE NEGATIVE for the staleness gate."""
        w = self._world(turn=10)
        self._crown(w, 8)
        self._endow(w, 8)
        self._beat(w, 10)
        head = dispatch_mod._build_headline(w, "France")
        assert head["class"] == "marshal_reversal", head

    def test_the_lead_cannot_repeat_for_more_than_two_turns(self):
        """The property the gate buys, stated directly."""
        w = self._world(turn=10)
        self._crown(w, 8)
        self._endow(w, 8)
        self._beat(w, 10)
        leads = []
        for t in (10, 11, 12, 13, 14):
            w.current_turn = t
            w.last_morning_dispatch = None
            head = dispatch_mod._build_headline(w, "France")
            leads.append((head or {}).get("class", ""))
        assert leads.count("marshal_reversal") <= 2, leads

    # ── §1.3 absorb only what the reversal restates ──────────────────────

    def test_a_battle_france_won_is_never_deleted(self):
        """The absorption was keyed on the MARSHAL, not on which act the
        composer chose, so a reversal whose fall clause was a dispossession
        deleted an `own_mauled` beat for a battle France WON — 12,000
        casualties that then appeared nowhere in the dispatch."""
        w = self._world(turn=10)
        self._crown(w, 8)
        self._endow(w, 8)
        w.event_log.append({
            "type": "estate_confiscated", "marshal": "Ney",
            "nation": "France", "region": "Carniola",
            "confiscated_by": "Austria", "turn": 10})
        # Ney ATTACKS and wins, losing 33% of a pre-battle 36,000.
        w.event_log.append({
            "type": "battle", "turn": 10, "attacker": "Ney",
            "defender": "Mack", "attacker_nation": "France",
            "defender_nation": "Austria", "outcome": "attacker_victory",
            "location": "Bohemia", "attacker_casualties": 9000})
        head = dispatch_mod._build_headline(w, "France")
        whole = head["text"] + " " + " ".join(head["sub_beats"])
        assert "9,000" in whole, (head["text"], head["sub_beats"])

    def test_the_beat_the_reversal_does_restate_is_still_absorbed(self):
        """FALSIFIABLE NEGATIVE: CA8-5's duplicate-beat shape must not
        return where the reversal genuinely narrates the same act."""
        w = self._world(turn=10)
        self._crown(w, 8)
        self._rout(w, 10)
        head = dispatch_mod._build_headline(w, "France")
        assert head["class"] == "marshal_reversal"
        assert not any("has been broken" in b for b in head["sub_beats"]), \
            head["sub_beats"]

    def test_a_hunted_reversal_absorbs_nothing(self):
        """Found INERT by the round-2 seam sweep: nothing pinned the third
        arm. The `hunted` line names the PURSUER and no casualty figure, so
        it restates neither the maul nor the break — absorbing either would
        delete a fact the headline never gives back."""
        w = self._world(turn=10)
        self._crown(w, 8)
        for t in (9, 10):                       # same attacker -> hunted
            self._beat(w, t, cas=9000)
        arc = dispatch_mod._build_marshal_arcs(w, "France")["Ney"]
        assert arc["fall_arm"] == "hunted", arc["fall_arm"]
        assert "hunted across the frontier" in arc["reversal_line"]
        head = dispatch_mod._build_headline(w, "France")
        assert head["class"] == "marshal_reversal"
        whole = head["text"] + " " + " ".join(head["sub_beats"])
        assert "9,000" in whole, (head["text"], head["sub_beats"])

    def test_the_own_mauled_half_of_the_absorption_is_observed(self):
        """§1.11c — this half was INERT: both absorption tests staged a
        forced retreat, so nothing exercised `own_mauled`."""
        w = self._world(turn=10)
        self._crown(w, 8)
        self._beat(w, 10, cas=9000)             # 33% of 27,000 -> mauled
        head = dispatch_mod._build_headline(w, "France")
        assert head["class"] == "marshal_reversal"
        assert not any("was mauled" in b for b in head["sub_beats"]), \
            head["sub_beats"]

    # ── §1.7 the roster cap must not delete a headline ───────────────────

    def test_the_display_cap_does_not_delete_the_reversal(self):
        """The max-3 cap was authored for the ROSTER's display lines, and
        the headline arm consumed the same capped dict, so a 4th-ranked
        reversal was deleted before it could be scored."""
        names = ("Alpha", "Bravo", "Cid", "Zed")
        w = self._world(turn=10, marshals=names)
        for who in ("Alpha", "Bravo", "Cid"):
            for t in (9, 10):
                self._beat(w, t, who=who)
                self._rout(w, t, who=who)
        self._crown(w, 8, who="Zed")
        self._endow(w, 8, who="Zed")
        w.event_log.append({"type": "estate_confiscated", "marshal": "Zed",
                            "nation": "France", "region": "Carniola",
                            "confiscated_by": "Austria", "turn": 10})
        capped = dispatch_mod._build_marshal_arcs(w, "France")
        assert len(capped) == 3, "the roster cap is unchanged"
        head = dispatch_mod._build_headline(w, "France")
        assert head["class"] == "marshal_reversal", head

    # ── §1.8 the estate, not the honorific ───────────────────────────────

    def test_the_estate_is_the_object_of_endowed_with(self):
        w = self._world(turn=10)
        self._endow(w, 9)
        self._beat(w, 10)
        line = dispatch_mod._build_marshal_arcs(w, "France")["Ney"]["reversal_line"]
        assert "endowed with Duke of" not in line, line
        assert "endowed with the Duchy of Carniola" in line, line

    def test_the_estate_noun_is_single_sourced(self):
        """The two hand-rolled `.replace('Duke of','Duchy of')` sites are
        gone — one helper now owns the noun."""
        import pathlib
        src = pathlib.Path("backend/commands/capture_executor.py").read_text(
            encoding="utf-8")
        assert "replace('Duke of'" not in src
        assert 'replace("Duke of"' not in src

    # ── §1.10 the closing note asserts nothing instance-specific ─────────

    def test_the_closing_note_is_true_of_every_instance(self):
        note = dispatch_mod._HEADLINE_BERTHIER_NOTES["marshal_reversal"]
        for claim in ("fortnight", "best of us", "crowned"):
            assert claim not in note, note


class TestCA88ReviewRound2:

    def _pair(self, turn=5):
        from tests.conftest import MarshalFactory, WorldFactory
        murat = MarshalFactory.infantry(name="Murat", personality="aggressive")
        davout = MarshalFactory.infantry(name="Davout")
        world = WorldFactory.with_marshals([murat, davout], current_turn=turn)
        return world, murat, davout

    # ── §1.5 the number is named for what it counts ──────────────────────

    def test_the_flare_count_is_not_called_a_cooling_count(self):
        """`_lifetime_fires` counts FIRES. `clear_jealousy` writes nothing to
        that list, and an action resolution takes the surge branch — a
        different word, a different event and a +10% surge — so "It has
        cooled 3 times" was false whenever an earlier episode was settled by
        a victory, contradicting the game's own earlier lines."""
        world, murat, davout = self._pair()
        murat.jealous_of = "Davout"
        murat.jealousy_history = {"Davout": [3, 8, 14]}
        events = []
        jealousy.clear_jealousy(world, murat, resolved_by_action=False,
                                events=events, reason="time")
        line = next(e["message"] for e in events
                    if e["type"] == "jealousy_resolved")
        assert "cooled 3 times" not in line, line
        assert "flared 3 times" in line, line

    # ── §1.6 the log may not assert a feud the engine skipped ────────────

    def test_the_log_only_claims_a_mutual_feud_when_one_applied(self):
        """The level advances to 3 whether or not the reciprocity applied —
        the producer skips it when the target is not STANDING (mid-rout) —
        so the log announced a mutual feud against a marshal with no
        grievance at all. One reviewer saw it on eight consecutive turns."""
        line = format_event_oneliner({
            "type": "jealousy_escalation", "turn": 3, "marshal": "Murat",
            "target": "Davout", "nation": "France", "level": 3,
            "mutual": False})
        assert "each schemes" not in line, line
        assert "entrenched" in line

    def test_a_genuine_mutual_feud_still_reads_as_one(self):
        line = format_event_oneliner({
            "type": "jealousy_escalation", "turn": 3, "marshal": "Murat",
            "target": "Davout", "nation": "France", "level": 3,
            "mutual": True})
        assert "each schemes" in line

    def test_the_producer_stamps_whether_reciprocity_applied(self):
        """§1.11b — the producer half was untested end to end."""
        world, murat, davout = self._pair(turn=6)
        murat.relationships["Davout"] = -2       # qualifies on every fire
        davout.relationships["Murat"] = -2
        jealousy._set_escalation_level(murat, "Davout", 2)
        jealousy._set_escalation_level(davout, "Murat", 2)
        davout.broken = True                     # not STANDING -> skipped
        world.event_log = []
        jealousy.apply_jealousy(world, murat, davout, delta=3, threshold=2,
                                events=[])
        esc = [e for e in world.event_log
               if e["type"] == "jealousy_escalation"]
        assert esc, world.event_log
        assert esc[-1]["mutual"] is False, esc[-1]
        assert davout.jealous_of != "Murat"

    # ── §1.11b the fires seam, producer to consumer ──────────────────────

    def test_the_fires_count_reaches_the_log_from_a_real_grievance(self):
        """The producer wrote `fires` and the consumer read it, and NOTHING
        connected them — both tests hand-built the dict. The `fires == 2`
        boundary, the common case, was untested in either direction."""
        world, murat, davout = self._pair(turn=3)
        world.event_log = []
        jealousy.apply_jealousy(world, murat, davout, delta=3, threshold=2,
                                events=[])
        murat.jealous_of = None
        world.current_turn = 9
        jealousy.apply_jealousy(world, murat, davout, delta=3, threshold=2,
                                events=[])
        fired = [e for e in world.event_log if e["type"] == "jealousy_fired"]
        assert [e["fires"] for e in fired] == [1, 2], fired
        first = format_event_oneliner({**fired[0], "turn": 3})
        again = format_event_oneliner({**fired[1], "turn": 9})
        assert "again" not in first, first
        assert "again" in again, again


    def test_the_idle_rung_fires_from_a_real_dispatch(self):
        """§1.11a end to end: the roster PRODUCES the int and the ladder
        CONSUMES it. Both halves were pinned only against hand-built rows,
        so the wire between them was unobserved."""
        from tests.conftest import MarshalFactory, WorldFactory
        ney = MarshalFactory.infantry(name="Ney", personality="aggressive")
        world = WorldFactory.with_marshals([ney], current_turn=6)
        ney.idle_turns = 9
        world.event_log = []
        rows = dispatch_mod._build_marshal_status(world, "France")
        assert rows[0]["idle_turns"] == 9
        note = dispatch_mod._pick_berthier_note(
            world, "France", rows,
            {"bankrupt": False, "treasury_delta": 100})
        assert "impatient" in note.lower(), note


# ════════════════════════════════════════════════════════════════════════
# CA8-19 — the three latent defects inside _resolve_garrison_combat
#
# The row's parity work (garrison assault as a real battle) stays GATED. These
# are the seams found inside it, each landable on its own. Note what each pin
# is really for: (i) is a live mechanical leak, (ii) and (iii) are DEAD code
# whose observable behaviour nothing pinned — deletions a test must now make
# falsifiable, because the whole point is that the suite could not tell.
# ════════════════════════════════════════════════════════════════════════

def _mk_marshal(name, location, strength, nation):
    from backend.models.marshal import Marshal
    return Marshal(name=name, location=location, strength=strength,
                   personality="aggressive", nation=nation,
                   spawn_location=location)


class TestCA819GarrisonSeams:

    def _garrison_world(self, garrison=40000, attacker_strength=30000):
        world = WorldState()
        world.diplomatic_states[world._make_diplo_key("France", "Britain")] = "WAR"
        world.marshals.clear()
        for name in ("Ney", "Davout", "Soult"):
            world.marshals[name] = _mk_marshal(name, "Paris", attacker_strength, "France")
        world.marshals["Lannes"] = _mk_marshal("Lannes", "Normandy", 20000, "France")
        target = world.get_region("Belgium")
        target.controller = "Britain"
        target.garrison_strength = garrison
        target.garrison_detachment = False
        return world, target

    @staticmethod
    def _stamped(world):
        return {n: round(getattr(m, "total_coordination_attack_bonus", 0.0), 4)
                for n, m in world.marshals.items()}

    # ── (i) the coordination stamp is cleared ────────────────────────────

    def test_a_garrison_assault_does_not_leave_a_permanent_attack_bonus(self):
        """The live half of CA8-19. `_resolve_garrison_combat` recomputes
        coordination (b2de36d) but both pipeline calls suppressed the clear
        (be596fd), so every marshal in the origin province kept a bonus that
        NOTHING in the game ever cleared — not advance_turn, not the tactical
        tick, and it is not serialized so a save/load was the only reset. It is
        not cosmetic: it is read back by `_committed_reinforcement_strength`,
        i.e. by real combat and by the muster preview the player decides on."""
        world, target = self._garrison_world()
        ex = CombatExecutor(CommandExecutor())
        res = ex._resolve_garrison_combat(
            world.get_marshal("Ney"), target, world, {"world": world})
        assert res["success"]
        assert "holds" in res["message"]                      # the HOLD branch
        assert self._stamped(world) == {"Ney": 0.0, "Davout": 0.0,
                                        "Soult": 0.0, "Lannes": 0.0}

    def test_the_leak_reached_committed_strength_not_just_the_display(self):
        """Why (i) is a mechanics row and not a copy row: the stale stamp is
        read back through `get_attack_modifier(consume=False)` inside
        `_committed_reinforcement_strength`, which feeds combat resolution, the
        CO-2 odds band and the CR-5 bad-odds modal."""
        world, target = self._garrison_world()
        ex = CombatExecutor(CommandExecutor())
        allies = [world.get_marshal(n) for n in ("Ney", "Davout", "Soult")]
        before = ex._committed_reinforcement_strength(allies[0], allies, world)
        ex._resolve_garrison_combat(allies[0], target, world, {"world": world})
        after = ex._committed_reinforcement_strength(allies[0], allies, world)
        assert after == before, (before, after)

    def test_the_capture_branch_clears_the_origin_it_marched_out_of(self):
        """The capture branch MOVES the attacker, so `attacker.location` is no
        longer the stamped province by the time the pipeline clears."""
        world, target = self._garrison_world(garrison=3000)
        ney = world.get_marshal("Ney")
        ex = CombatExecutor(CommandExecutor())
        res = ex._resolve_garrison_combat(ney, target, world, {"world": world})
        assert res["success"] and ney.location == "Belgium"    # he advanced
        assert self._stamped(world) == {"Ney": 0.0, "Davout": 0.0,
                                        "Soult": 0.0, "Lannes": 0.0}

    def test_the_no_strength_exit_clears_for_itself(self):
        """This exit sits AFTER the stamp and BEFORE either pipeline call."""
        world, target = self._garrison_world()
        ney = world.get_marshal("Ney")
        ney.strength = 0
        ex = CombatExecutor(CommandExecutor())
        res = ex._resolve_garrison_combat(ney, target, world, {"world": world})
        assert res["success"] is False
        assert self._stamped(world) == {"Ney": 0.0, "Davout": 0.0,
                                        "Soult": 0.0, "Lannes": 0.0}

    def test_the_stamp_itself_still_happens(self):
        """Negative control, and the pin b2de36d never wrote: the recompute
        that grants a garrison assault its coordination bonus is REAL. Without
        this, 'clear it' and 'delete the recompute' are indistinguishable to
        the suite, and the next cleanup can silently move garrison balance."""
        world, target = self._garrison_world()
        ex = CombatExecutor(CommandExecutor())
        seen = {}
        real = ex._calculate_coordination_context

        def spy(primary, *a, **k):
            out = real(primary, *a, **k)
            seen[primary.name] = round(
                getattr(primary, "total_coordination_attack_bonus", 0.0), 4)
            return out

        ex._calculate_coordination_context = spy
        ex._resolve_garrison_combat(
            world.get_marshal("Ney"), target, world, {"world": world})
        assert seen.get("Ney", 0.0) > 0.0, seen

    def test_clear_combat_transient_state_holds_the_coordination_fields(self):
        """Its docstring promised 'any new combat-transient field MUST be added
        here' and it held none of the eleven — which is why the reckless-cavalry
        auto-charge, the one `resolve_battle` call site with no coordination
        recompute on either side, could fight on leaked numbers."""
        from backend.models.marshal import Marshal as _M
        m = _mk_marshal("Probe", "Paris", 10000, "France")
        for attr in _M.COORDINATION_TRANSIENT_FIELDS:
            setattr(m, attr, 0.25)
        m.clear_combat_transient_state()
        assert all(getattr(m, a) == 0.0 for a in _M.COORDINATION_TRANSIENT_FIELDS)
        # ... and the executor's list IS that list, so they cannot drift.
        assert CombatExecutor._COORDINATION_FIELDS == list(
            _M.COORDINATION_TRANSIENT_FIELDS)

    def test_the_reckless_charge_clears_the_defender_too(self):
        """The attacker is covered by `clear_combat_transient_state`; the
        defender needs a coordination-ONLY clear, because clearing his full
        transient state before the battle would strip `fortified` /
        `square_formation` and change the fight."""
        import inspect
        from backend.models.world_state import WorldState as _WS
        src = inspect.getsource(_WS._process_reckless_cavalry_turn_start)
        assert "enemy.clear_coordination_transients()" in src
        assert "enemy.clear_combat_transient_state()" not in src.split(
            "resolve_battle")[0]

    # ── (ii) the garrison exclusion from the glory ladder ────────────────

    def test_a_garrison_assault_records_no_glory_either_way(self):
        """CA8-19(ii). Spec §1 authors 'Garrison stomp: +0'. It used to be an
        `is_garrison` argument to `record_battle_glory` that NO production
        caller could set — the garrison path passes `battle_result: None`,
        which the same guard already excluded, so the exemption held by
        accident and its only test was a direct unit call carrying a fifth
        argument the game cannot produce. The rule is now stated at the guard;
        this reds the moment anyone ungates the step without deciding."""
        for garrison, arm in ((3000, "capture"), (40000, "hold")):
            world, target = self._garrison_world(garrison=garrison)
            ney = world.get_marshal("Ney")
            ex = CombatExecutor(CommandExecutor())
            ex._resolve_garrison_combat(ney, target, world, {"world": world})
            assert ney.glory_events == [], (arm, ney.glory_events)

    def test_a_garrison_assault_does_not_resolve_a_grievance(self):
        """The same guard governs step 9.5, which MUTATES `jealous_of` — the
        derived -1 that coordination, objections, reinforcement, muster and the
        enemy-AI ally filter all read. Ungating glory without deciding this
        would move drama behaviour, which is why it is one rule, stated once."""
        world, target = self._garrison_world(garrison=3000)
        ney = world.get_marshal("Ney")
        ney.jealous_of = "Davout"
        ex = CombatExecutor(CommandExecutor())
        ex._resolve_garrison_combat(ney, target, world, {"world": world})
        assert ney.jealous_of == "Davout"

    def test_victory_points_no_longer_takes_a_garrison_argument(self):
        """The deletion, stated. A five-argument call that production could
        never make is how the dead discriminator survived every green suite."""
        import inspect
        params = list(inspect.signature(jealousy._victory_points).parameters)
        assert params == ["casualties_own", "casualties_enemy",
                          "conquered", "outnumbered"], params
        assert "is_garrison" not in inspect.signature(
            jealousy.record_battle_glory).parameters

    # ── (iii) war exhaustion: the branch was dead, the behaviour was not ──

    def test_the_repulsed_attacker_pays_on_every_cell_of_the_board(self):
        """CA8-19(iii) AS FILED says 'an AI army repulsed from a French
        garrison accrues no war exhaustion at all'. That half is FALSE — the
        arm above the dead one already charges him. The dead `elif` is deleted;
        this is the behaviour it was supposed to provide, proven present."""
        cells = [
            ("France", "Britain", "France"),   # France repulsed -> France pays
            ("Britain", "France", "Britain"),  # an AI repulsed from a French
                                               # garrison -> the AI pays
        ]
        for attacker_nation, owner, payer in cells:
            world = WorldState()
            world.diplomatic_states[
                world._make_diplo_key(attacker_nation, owner)] = "WAR"
            world.marshals.clear()
            m = _mk_marshal("Probe", "Belgium", 10000, attacker_nation)
            world.marshals["Probe"] = m
            target = world.get_region("Belgium")
            target.controller = owner
            target.garrison_strength = 80000
            target.garrison_detachment = False
            ex = CombatExecutor(CommandExecutor())
            res = ex._resolve_garrison_combat(m, target, world, {"world": world})
            assert res["success"] and target.garrison_strength > 0
            # losses saturate the 0.35 cap -> 3,500 -> 3,500 // 1,000
            assert world.war_exhaustion.get(payer, 0) == 3, (
                attacker_nation, owner, dict(world.war_exhaustion))

    def test_the_dead_garrison_exhaustion_branch_is_gone(self):
        """It was unreachable from the commit that wrote it: a garrison hold is
        a defender victory and its ctx says so, so `elif defender_won:` always
        claimed it first."""
        import inspect
        # Strip comments: the deletion is RECORDED in one, and a naive scan
        # would match the record and pass for the wrong reason.
        body = inspect.getsource(CombatExecutor._post_combat_pipeline)
        src = "\n".join(line for line in body.splitlines()
                        if not line.lstrip().startswith("#"))
        assert "not attacker_won and not defender_won and is_garrison" not in src
        # ... and the record IS there, so a future reader finds the reasoning.
        assert "CA8-19(iii)" in inspect.getsource(
            CombatExecutor._post_combat_pipeline)


# ════════════════════════════════════════════════════════════════════════
# CA8-28 — the same misspelling got a suggestion or a shrug by VERB
#
# THE PIN MUST BE EXECUTOR-LEVEL. `parser_eval.evaluate_entry` makes exactly
# one production call (`CommandParser.parse`) and never constructs an executor,
# so a golden-corpus row would be false assurance. So would
# tests/test_parse_negation.py, whose own `run()` helper is also parser-only:
# under a NAIVE delegation the parser's target stays "Pass" in both arms — the
# PARSE-NEG assertion (`target != "Nassau"`) passes — while the executor has
# quietly created a 2-AP standing HOLD on Nassau. That is why the negative
# control below asserts on the ORDER, not on the parse.
# ════════════════════════════════════════════════════════════════════════

_EUROPE = "godot-client/project-sovereign/assets/maps/europe_1805.json"


@pytest.fixture()
def europe_board(monkeypatch):
    monkeypatch.delenv("SOVEREIGN_SCENARIO", raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    return WorldState.from_scenario(_EUROPE)


def _issue(world, text):
    """Production shape: real parser -> real executor."""
    from backend.commands.parser import CommandParser
    random.seed(7)
    parser = CommandParser(use_real_llm=False)
    gs = {"world": world,
          "marshals": {n: {"name": n} for n in world.marshals}}
    parsed = parser.parse(text, gs, world=world)
    return CommandExecutor().execute(parsed, {"world": world})


class TestCA828StrategicDestinationSuggestion:

    @pytest.mark.parametrize("text", [
        "Davout, move to Venetia",          # tactical — already worked
        "Davout, march to Venetia",         # strategic MOVE_TO
        "Davout, march south to Venetia",   # directional lead-in
        "Davout, hold Venetia",             # HOLD shares the seam
    ])
    def test_the_same_typo_gets_the_same_answer_whatever_the_verb(
            self, europe_board, text):
        res = _issue(europe_board, text)
        assert res["success"] is False
        assert "Venetia" in res["message"] and "Vienna" in res["message"], res["message"]

    def test_the_low_confidence_arm_arrives_too(self, europe_board):
        """Not just "Did you mean…?" — the "Nearby: …" tier as well."""
        res = _issue(europe_board, "Davout, march to Bordeuex")
        assert res["success"] is False
        assert "Nearby:" in res["message"] and "Bordelais" in res["message"]

    # ── the three tripwires ─────────────────────────────────────────────

    def test_hold_the_pass_still_holds_and_creates_no_order(self, europe_board):
        """THE LOAD-BEARING NEGATIVE CONTROL (PARSE-NEG).

        `match_with_context("Pass", regions)` returns Nassau at the
        auto-correct tier — silently, with no error dict — so a naive
        delegation would have created a real 2-AP standing HOLD on a province
        200km away and told the player he was holding a place called "Pass".
        Assert on the ORDER and the AP, which is the half the parser-level pin
        cannot express.
        """
        before = europe_board.actions_remaining
        res = _issue(europe_board, "Davout, hold the pass")
        assert res["success"] is False
        assert "Nassau" not in res["message"], res["message"]
        assert europe_board.get_marshal("Davout").strategic_order is None
        assert europe_board.actions_remaining == before

    # NOT parametrized with "the rear" -> Bearn, which also auto-corrects:
    # the parser owns "rear" as a DIRECTION word ("rear of Rhineland" ->
    # Lorraine) and resolves it before this seam is reached. That is a
    # deliberate feature, so it is excluded here rather than silently passing
    # for a reason unrelated to the guard under test.
    @pytest.mark.parametrize("word,region", [
        ("the pass", "Nassau"), ("the line", "Berlin"), ("the guns", "Brunswick"),
    ])
    def test_ordinary_english_never_becomes_a_province(
            self, europe_board, word, region):
        res = _issue(europe_board, f"Davout, march to {word}")
        assert region not in (res.get("message") or ""), res.get("message")
        assert europe_board.get_marshal("Davout").strategic_order is None

    def test_the_nation_arm_still_runs_first(self, europe_board):
        """IGR-A3. If the fuzzy pass were inserted above it, "march to Austria"
        would suggest Asturias again."""
        res = _issue(europe_board, "Davout, march to Austria")
        assert res["success"] is False
        assert "Asturias" not in res["message"]
        assert "is a nation, not a province" in res["message"]

    def test_the_phrase_scan_still_runs_first(self, europe_board):
        """F4. A whole phrase naming a real province resolves to that province;
        the fuzzy pass is a LAST arm, never a substitute."""
        # Soult is the roster's literal — he never objects (W6-5), so the
        # order lands on the marshal rather than in a pending objection, and
        # the assertion is about resolution rather than about mood.
        from backend.commands.strategic_executor import _resolve_region_from_phrase
        # The ordering guarantee, directly: the phrase scan resolves this, so
        # the new fuzzy arm is never consulted for it.
        assert _resolve_region_from_phrase(
            europe_board, "Archduke John At Tyrol", "France") == "Tyrol"
        # And end to end. NOT `success is True`: the order IS created and
        # pathed to Tyrol, and is then cleared because its first step is
        # blocked by Mack at Swabia — a different, correct refusal. What must
        # hold is that the phrase resolved and never leaked.
        res = _issue(europe_board, "Soult, march on Archduke John at Tyrol")
        msg = res.get("message") or ""
        assert "could not make out" not in msg, msg
        assert "Archduke John At Tyrol" not in msg, msg

    def test_a_multi_word_phrase_keeps_the_honest_shrug(self, europe_board):
        """Fuzzy matching a whole SENTENCE is how the PARSE-NEG family got in.
        Only single tokens reach the new arm.

        Pinned on the helper, not end to end: an earlier version of this test
        drove `march to the Bavarian frontier` through the parser and passed
        with the guard DELETED — the parser resolves that phrase upstream, so
        the arm was never reached and the test proved nothing. Measured
        directly, the same phrase would answer "Did you mean 'Oran'?".
        """
        ex = CommandExecutor()
        strat = ex._strategic
        for phrase in ("the Bavarian frontier", "the enemy camp",
                       "his left flank", "the river crossing"):
            assert strat._suggest_region_for_phrase(phrase, europe_board) == (None, None), phrase
            # ... and the unguarded matcher really would have answered.
            _region, err = ex._fuzzy_match_region(phrase, europe_board)
            assert err is not None and (
                "Did you mean" in err["message"] or "Nearby:" in err["message"])

    def test_a_failed_resolution_is_free(self, europe_board):
        for text in ("Davout, march to Venetia", "Davout, hold Venetia",
                     "Davout, pursue Zzzqqx", "Davout, support Zzzqqx"):
            before = europe_board.actions_remaining
            res = _issue(europe_board, text)
            assert res["success"] is False
            assert europe_board.actions_remaining == before, text
            assert res.get("variable_action_cost") == 0, text

    # ── the other two of the "three messages" ───────────────────────────

    def test_support_ranks_instead_of_dumping_the_roster(self, europe_board):
        res = _issue(europe_board, "Ney, support Davot")
        assert res["success"] is False
        assert "Did you mean 'Davout'?" in res["message"], res["message"]

    def test_pursue_suggests_only_what_fog_already_reveals(self, europe_board):
        """R5. A ranked guess at a hidden army is free intelligence."""
        visible = {e.name for e in europe_board.get_visible_enemies("France")}
        assert "Mack" in visible and "Kutuzov" not in visible   # boot fog
        hit = _issue(europe_board, "Ney, pursue Macck")
        assert "Did you mean 'Mack'?" in hit["message"], hit["message"]
        miss = _issue(europe_board, "Ney, pursue Kutuzow")
        assert "Kutuzov" not in miss["message"], miss["message"]

    def test_a_fogged_army_is_not_a_destination(self, europe_board):
        """The marshal fallback inside `_resolve_region_from_phrase` used to
        scan EVERY marshal in the world, so naming a hidden foreign army
        answered with the province it was standing in."""
        hidden = [m for m in europe_board.marshals.values()
                  if m.nation != "France"
                  and m.name not in {e.name for e in
                                     europe_board.get_visible_enemies("France")}]
        assert hidden, "boot fog must hide someone for this to mean anything"
        target = hidden[0]
        res = _issue(europe_board, f"Davout, march to {target.name}")
        assert target.location not in (res.get("message") or ""), res.get("message")
