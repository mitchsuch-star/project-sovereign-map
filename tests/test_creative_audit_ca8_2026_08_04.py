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
               title="the Duchy of Carniola", marshal="Ney"):
        world.event_log.append({"type": "dotation_granted", "marshal": marshal,
                                "nation": "France", "region": region,
                                "title": title, "turn": turn})

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
        assert "Duchy of Carniola" in line
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
        world, murat, davout = self._pair()
        self._fire(world, murat, davout, turn=5)
        line = self._fire(world, murat, davout, turn=9)
        assert "again" in line, line
        assert "4 turns after it cooled" in line, line

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
