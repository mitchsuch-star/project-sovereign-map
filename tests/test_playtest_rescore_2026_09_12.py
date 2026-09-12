"""Playtest re-score, September 12 2026 — the slice's pins.

Two families:

* **PR** — "The Peace That Never Was" and "The Nation Is Not An Adjective":
  the coalition annulled a settlement inside the same ``end turn`` that
  ratified it, and four template families carried the internal nation TAG
  into player-facing prose.
* **MS** — the diplomatic mission system: a completed mission locked the
  Cabinet forever, the undermine progress line printed its own template
  braces, every displayed figure was a third low, the collapse notice was
  fogged out by the mission it had already deleted, and three mission types
  taxed the diplomatic budget at the relation ceiling for nothing.

Every behaviour pin drives production code and every lever has a DOWN arm
that reproduces the defect, so the sweep can tell a kill from an inert pin.
"""

import unittest

from backend.models.world_state import WorldState


# ════════════════════════════════════════════════════════════════════
# helpers
# ════════════════════════════════════════════════════════════════════

def _europe():
    """The shipped 1805 board — the only board these defects live on."""
    import pathlib
    scenario = (pathlib.Path(__file__).resolve().parents[1]
                / "godot-client" / "project-sovereign" / "assets" / "maps"
                / "europe_1805.json")
    return WorldState.from_scenario(str(scenario))


def _war_instance(world, a, b, *, ended_turn, same_side=False):
    """Plant a finished war between `a` and `b`, the shape the engine writes."""
    world.war_instances = {
        "war_probe": {
            "id": "war_probe",
            "ended_turn": ended_turn,
            "participant_meta": {
                a: {"side": "attackers", "joined_turn": 1, "exited_turn": None},
                b: {"side": "attackers" if same_side else "defenders",
                    "joined_turn": 1, "exited_turn": None},
            },
        }
    }


# ════════════════════════════════════════════════════════════════════
# PR-1 — the peace that never was
# ════════════════════════════════════════════════════════════════════

class TestAFreshPeaceIsNotMarchedBackOut(unittest.TestCase):
    """A court that signed yesterday is not enrolled in today's coalition."""

    def setUp(self):
        self.world = _europe()
        self.world.current_turn = 20
        # Britain is hostile and at PEACE — exactly the post-settlement shape.
        self.world.nation_relations[
            self.world._make_diplo_key("France", "Britain")] = -80
        from backend.game_logic.diplomacy import set_diplomatic_state
        set_diplomatic_state(self.world, "France", "Britain", "PEACE", "probe")

    def test_a_court_that_just_signed_does_not_qualify(self):
        from backend.game_logic import coalition as C
        _war_instance(self.world, "France", "Britain", ended_turn=19)
        self.assertFalse(
            C.qualifies_for_coalition("Britain", self.world, target="France"))

    def test_the_same_court_qualifies_again_once_the_floor_lapses(self):
        from backend.game_logic import coalition as C
        _war_instance(self.world, "France", "Britain",
                      ended_turn=20 - C.FRESH_PEACE_FLOOR_TURNS)
        self.assertTrue(
            C.qualifies_for_coalition("Britain", self.world, target="France"))

    def test_lever_down_reproduces_the_same_turn_annulment(self):
        from backend.game_logic import coalition as C
        _war_instance(self.world, "France", "Britain", ended_turn=19)
        original = C.COALITION_HONOURS_A_FRESH_PEACE
        try:
            C.COALITION_HONOURS_A_FRESH_PEACE = False
            self.assertTrue(
                C.qualifies_for_coalition("Britain", self.world,
                                          target="France"),
                "lever DOWN must reproduce the pre-fix enrolment")
        finally:
            C.COALITION_HONOURS_A_FRESH_PEACE = original

    def test_a_co_belligerent_is_never_exempted(self):
        """Two courts on the SAME side were never at war with each other."""
        from backend.game_logic import coalition as C
        _war_instance(self.world, "France", "Britain", ended_turn=19,
                      same_side=True)
        self.assertTrue(
            C.qualifies_for_coalition("Britain", self.world, target="France"),
            "a shared war is not a peace between its co-belligerents")

    def test_an_exited_turn_outranks_the_wars_own_end(self):
        """A separate-peaced court's own exit is the pair's peace date."""
        from backend.game_logic import coalition as C
        _war_instance(self.world, "France", "Britain", ended_turn=1)
        (self.world.war_instances["war_probe"]["participant_meta"]
         ["Britain"]["exited_turn"]) = 19
        self.assertFalse(
            C.qualifies_for_coalition("Britain", self.world, target="France"))

    def test_a_court_with_no_war_at_all_is_unaffected(self):
        from backend.game_logic import coalition as C
        self.world.war_instances = {}
        self.assertTrue(
            C.qualifies_for_coalition("Britain", self.world, target="France"))

    def test_form_coalition_leaves_the_signatory_at_peace(self):
        """The end-to-end shape: `form_coalition` no longer declares for him."""
        from backend.game_logic import coalition as C
        _war_instance(self.world, "France", "Britain", ended_turn=19)
        qualifying = [n for n in ("Britain", "Sweden", "Naples")
                      if C.qualifies_for_coalition(n, self.world,
                                                   target="France")]
        self.assertNotIn("Britain", qualifying)
        for other in ("Sweden", "Naples"):
            self.world.nation_relations[
                self.world._make_diplo_key("France", other)] = -80
        qualifying = [n for n in ("Britain", "Sweden", "Naples")
                      if C.qualifies_for_coalition(n, self.world,
                                                   target="France")]
        self.assertTrue(qualifying, "the coalition still forms without him")
        C.form_coalition(qualifying, self.world, target="France")
        self.assertEqual(
            self.world.get_diplomatic_state("France", "Britain"), "PEACE",
            "the peace France ratified must survive the coalition")


# ════════════════════════════════════════════════════════════════════
# PR-2 — the nation is not an adjective
# ════════════════════════════════════════════════════════════════════

class TestTheNationIsNotAnAdjective(unittest.TestCase):

    def test_the_envoy_line_names_the_court(self):
        from backend.game_logic.dispatch import _format_dispatch_event_text
        line = _format_dispatch_event_text("diplomatic_ai_proposal",
                                           {"nation": "PapalStates"})
        self.assertIn("the Papal States", line)
        self.assertNotIn("PapalStates", line)

    def test_a_plain_name_takes_no_article(self):
        from backend.game_logic.dispatch import _format_dispatch_event_text
        line = _format_dispatch_event_text("diplomatic_ai_proposal",
                                           {"nation": "Prussia"})
        self.assertIn("from Prussia", line)
        self.assertNotIn("the Prussia", line)

    def test_the_court_line_expands_the_tag(self):
        from backend.game_logic.dispatch import _format_dispatch_event_text
        line = _format_dispatch_event_text("diplomatic_proposal_sent",
                                           {"nation": "Ottoman"})
        self.assertIn("Ottoman Empire", line)

    def test_trafalgar_names_the_french_fleet(self):
        from backend.game_logic.dispatch import _format_dispatch_event_text
        line = _format_dispatch_event_text(
            "trafalgar", {"winner_admiral": "Nelson", "loser": "France",
                          "loser_ships_lost": 23, "winner": "Britain"})
        self.assertIn("the French fleet", line)
        self.assertNotIn("the France fleet", line)

    def test_lever_down_reproduces_the_raw_tag(self):
        from backend.game_logic import dispatch as D
        original = D.DISPATCH_TEMPLATES_NAME_THE_NATION
        try:
            D.DISPATCH_TEMPLATES_NAME_THE_NATION = False
            line = D._format_dispatch_event_text("diplomatic_ai_proposal",
                                                 {"nation": "PapalStates"})
            self.assertIn("{nation_display}", line,
                          "lever DOWN leaves the placeholder unfilled")
        finally:
            D.DISPATCH_TEMPLATES_NAME_THE_NATION = original

    def test_the_coalition_is_named_for_a_people_not_a_tag(self):
        from backend.game_logic import coalition as C
        world = _europe()
        world.coalition_count = 3
        for n in ("Britain", "Sweden", "Naples"):
            world.nation_relations[world._make_diplo_key("France", n)] = -80
        result = C.form_coalition(["Britain", "Sweden", "Naples"], world,
                                  target="France")
        self.assertTrue(result.get("success"), result.get("message"))
        # The leader is chosen from ALL members, including the courts
        # already at war — on this board that is Austria, none of the three
        # passed in. The first cut of this pin listed those three and was
        # VACUOUS; the sweep said so.
        leader = result["leader"]
        name = result["coalition_name"]
        from backend.display_names import nation_adjective
        self.assertIn(f"{nation_adjective(leader)} Coalition", name)
        self.assertNotIn(f"{leader} Coalition", name)

    def test_a_churned_board_never_prints_a_bare_numeral(self):
        """Measured on the shipped board: coalitions reach TEN in forty
        turns, and the map stopped at seven — "The 8th Austria Coalition"."""
        from backend.game_logic.coalition import _ORDINALS
        for count in range(1, 13):
            word = _ORDINALS.get(count, f"{count}th")
            self.assertFalse(word[0].isdigit(),
                             f"coalition {count} prints a bare numeral: {word}")

    def test_a_carve_tag_is_never_given_a_coined_demonym(self):
        from backend.display_names import nation_adjective
        for tag, expected in (("DuchyOfWarsaw", "Warsaw"),
                              ("RomanRepublic", "Roman"),
                              ("Poland", "Polish"),
                              ("Normandy", "Norman")):
            self.assertEqual(nation_adjective(tag), expected)

    def test_an_unauthored_compound_tag_degrades_to_its_name(self):
        from backend.display_names import nation_adjective
        self.assertEqual(nation_adjective("UnitedNetherlands"),
                         "UnitedNetherlands")

    def test_lever_down_reproduces_the_coined_demonym(self):
        from backend import display_names as DN
        original = DN.NATION_ADJECTIVE_REFUSES_TO_COIN
        try:
            DN.NATION_ADJECTIVE_REFUSES_TO_COIN = False
            self.assertEqual(DN.nation_adjective("UnitedNetherlands"),
                             "Unitednetherlandsian")
        finally:
            DN.NATION_ADJECTIVE_REFUSES_TO_COIN = original

    def test_the_regular_derivation_is_untouched(self):
        from backend.display_names import nation_adjective
        self.assertEqual(nation_adjective("Austria"), "Austrian")
        self.assertEqual(nation_adjective("France"), "French")


# ════════════════════════════════════════════════════════════════════
# MS — the mission system
# ════════════════════════════════════════════════════════════════════

def _mission_world(mission):
    world = _europe()
    world.current_turn = 10
    world.active_diplomatic_mission = mission
    return world


class TestTheDeskIsNotLocked(unittest.TestCase):
    """MS-1: a completed mission is a record, not a commitment."""

    def _rows(self, world, court="Prussia"):
        from backend.game_logic.diplomacy import get_available_diplomatic_actions
        return {a["action"]: a for a in
                get_available_diplomatic_actions(world, court)}

    def test_a_completed_mission_does_not_lock_the_cabinet(self):
        world = _mission_world({"type": "GATHER_INTEL", "target": "Austria",
                                "turns_active": 3, "completed": True})
        world.diplomatic_points = 10
        rows = self._rows(world)
        row = rows.get("mission_improve_relations")
        self.assertIsNotNone(row, "the mission row must still be offered")
        self.assertNotEqual(row.get("disabled_reason"), "Mission already active")

    def test_a_running_mission_still_locks_it(self):
        world = _mission_world({"type": "IMPROVE_RELATIONS", "target": "Austria",
                                "turns_active": 2, "completed": False})
        world.diplomatic_points = 10
        row = self._rows(world).get("mission_improve_relations")
        self.assertFalse(row["available"])
        self.assertEqual(row["disabled_reason"], "Mission already active")

    def test_lever_down_reproduces_the_permanent_lockout(self):
        from backend.game_logic import diplomatic_dialogue as DD
        world = _mission_world({"type": "GATHER_INTEL", "target": "Austria",
                                "turns_active": 3, "completed": True})
        world.diplomatic_points = 10
        original = DD.ONE_PREDICATE_ANSWERS_MISSION_LIVENESS
        try:
            DD.ONE_PREDICATE_ANSWERS_MISSION_LIVENESS = False
            row = self._rows(world).get("mission_improve_relations")
            self.assertEqual(row["disabled_reason"], "Mission already active")
        finally:
            DD.ONE_PREDICATE_ANSWERS_MISSION_LIVENESS = original

    def test_every_surface_gives_the_same_answer(self):
        """The top bar said idle while the Cabinet said busy."""
        from backend.game_logic.diplomatic_dialogue import mission_is_live
        from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger
        from backend.main import _get_talleyrand_mission_summary
        world = _mission_world({"type": "GATHER_INTEL", "target": "Austria",
                                "turns_active": 3, "completed": True})
        world.diplomatic_points = 10
        self.assertFalse(mission_is_live(world))
        self.assertEqual(_get_talleyrand_mission_summary(world), "None")
        ledger = build_diplomatic_ledger(world)
        self.assertIsNone(ledger["talleyrand"]["active_mission"])
        row = {a["action"]: a for a in
               __import__("backend.game_logic.diplomacy", fromlist=["x"])
               .get_available_diplomatic_actions(world, "Prussia")
               }.get("mission_improve_relations")
        self.assertTrue(row["available"])

    def test_the_cancel_row_is_not_offered_for_a_finished_mission(self):
        world = _mission_world({"type": "GATHER_INTEL", "target": "Prussia",
                                "turns_active": 3, "completed": True})
        world.diplomatic_points = 10
        self.assertNotIn("cancel_mission", self._rows(world, "Prussia"))


class TestTheFigureShownIsTheFigurePaid(unittest.TestCase):
    """MS-3: displayed effect == what `_process_mission_effects` writes."""

    def test_the_helper_matches_the_tick_exactly(self):
        from backend.game_logic.diplomacy import (
            _process_mission_effects, get_mission_skill_multiplier)
        from backend.game_logic.diplomatic_dialogue import (
            mission_effect_magnitude)
        world = _mission_world({"type": "IMPROVE_RELATIONS", "target": "Prussia",
                                "turns_active": 1, "completed": False,
                                "paused": False})
        key = world._make_diplo_key("France", "Prussia")
        world.nation_relations[key] = 0
        before = world.nation_relations[key]
        _process_mission_effects(world)
        applied = world.nation_relations[key] - before
        quoted = mission_effect_magnitude(world, "IMPROVE_RELATIONS",
                                          "relation_change")
        self.assertEqual(applied, quoted,
                         "shown must equal applied, not the table constant")
        self.assertGreater(get_mission_skill_multiplier(world), 1.0)

    def test_the_ledger_quotes_the_applied_figure(self):
        from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger
        world = _mission_world({"type": "IMPROVE_RELATIONS", "target": "Prussia",
                                "turns_active": 1, "completed": False,
                                "paused": False})
        text = build_diplomatic_ledger(world)["talleyrand"]["active_mission"][
            "effect_text"]
        self.assertEqual(text, "+8 relation per turn")

    def test_lever_down_reproduces_the_unscaled_constant(self):
        from backend.game_logic import diplomatic_dialogue as DD
        from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger
        world = _mission_world({"type": "IMPROVE_RELATIONS", "target": "Prussia",
                                "turns_active": 1, "completed": False,
                                "paused": False})
        original = DD.MISSION_EFFECT_TEXT_IS_THE_APPLIED_FIGURE
        try:
            DD.MISSION_EFFECT_TEXT_IS_THE_APPLIED_FIGURE = False
            text = build_diplomatic_ledger(world)["talleyrand"][
                "active_mission"]["effect_text"]
            self.assertEqual(text, "+5 relation per turn")
        finally:
            DD.MISSION_EFFECT_TEXT_IS_THE_APPLIED_FIGURE = original


class TestTheMissionSaysWhatItIsDoing(unittest.TestCase):

    def test_the_undermine_line_renders(self):
        """MS-5: it printed its own template braces, every turn."""
        from backend.game_logic.dispatch import _format_dispatch_event_text
        line = _format_dispatch_event_text(
            "diplomatic_mission_undermine_progress",
            {"nation": "Austria", "ally": "Prussia", "delta": -4, "value": 36})
        self.assertNotIn("{", line)
        self.assertIn("Austria", line)
        self.assertIn("Prussia", line)
        self.assertIn("-4", line)

    def test_the_old_template_still_cannot_render_those_keys(self):
        """The defect reproduced, so the pin is about something real."""
        from backend.game_logic.dispatch import _format_dispatch_event_text
        line = _format_dispatch_event_text(
            "diplomatic_mission_progress",
            {"nation": "Austria", "ally": "Prussia", "delta": -4})
        self.assertIn("{value}", line)

    def test_the_undermine_tick_queues_a_renderable_event(self):
        from backend.game_logic.diplomacy import _process_mission_effects
        world = _mission_world({"type": "UNDERMINE_ALLIANCE",
                                "target": "Austria", "target_ally": "Russia",
                                "turns_active": 1, "completed": False,
                                "paused": False})
        world.nation_relations[world._make_diplo_key("Austria", "Russia")] = 60
        world.pending_dispatch_events = []
        _process_mission_effects(world)
        queued = [e for e in (getattr(world, "pending_dispatch_events", []) or [])
                  if "mission" in str(e.get("type", ""))]
        self.assertTrue(queued, "the tick must queue a progress event")
        from backend.game_logic.dispatch import _format_dispatch_event_text
        for ev in queued:
            rendered = _format_dispatch_event_text(
                ev["type"], ev.get("template_vars", {}) or {})
            self.assertNotIn("{", rendered,
                             f"unrendered template for {ev['type']}")
            # The sweep's lesson: adding `value` to the payload makes the OLD
            # template render too, so "no braces" alone does not pin the new
            # one. An undermine mission moves a pair, and the line has to
            # name BOTH halves of it or it is describing the wrong thing.
            self.assertIn("Russia", rendered,
                          "the line must name the ally being parted off")
            self.assertIn("Austria", rendered)

    def test_the_progress_readout_tracks_the_pair_the_mission_moves(self):
        """MS-7: it read our OWN relation for an undermine mission."""
        from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger
        world = _mission_world({"type": "UNDERMINE_ALLIANCE",
                                "target": "Austria", "target_ally": "Russia",
                                "turns_active": 5, "completed": False,
                                "paused": False, "initial_relation": 60})
        world.nation_relations[world._make_diplo_key("Austria", "Russia")] = 10
        world.nation_relations[world._make_diplo_key("France", "Austria")] = 90
        mission = build_diplomatic_ledger(world)["talleyrand"]["active_mission"]
        self.assertEqual(mission["current_relation"], 10)
        self.assertLess(mission["relation_delta"], 0)

    def test_the_collapse_notice_survives_the_mission_it_describes(self):
        """MS-2: the mission was deleted before its own event was fogged."""
        from backend.game_logic.diplomacy import _process_mission_dp
        world = _mission_world({"type": "IMPROVE_RELATIONS", "target": "Prussia",
                                "turns_active": 4, "completed": False,
                                "paused": True, "paused_turns": 3})
        world.diplomatic_points = 0
        world.pending_dispatch_events = []
        _process_mission_dp(world)
        self.assertIsNone(world.active_diplomatic_mission)
        from backend.game_logic.dispatch import _is_dispatch_event_visible
        cancelled = [e for e in (world.pending_dispatch_events or [])
                     if e.get("type") == "diplomatic_mission_cancelled"]
        self.assertTrue(cancelled)
        self.assertTrue(
            _is_dispatch_event_visible(cancelled[0], world, "France"),
            "the collapse notice must survive its own mission's deletion")

    def test_lever_down_reproduces_the_swallowed_collapse_notice(self):
        from backend.game_logic import diplomacy as D
        world = _mission_world({"type": "IMPROVE_RELATIONS", "target": "Prussia",
                                "turns_active": 4, "completed": False,
                                "paused": True, "paused_turns": 3})
        world.diplomatic_points = 0
        world.pending_dispatch_events = []
        original = D.MISSION_COLLAPSE_IS_ANNOUNCED
        try:
            D.MISSION_COLLAPSE_IS_ANNOUNCED = False
            D._process_mission_dp(world)
            from backend.game_logic.dispatch import _is_dispatch_event_visible
            cancelled = [e for e in (world.pending_dispatch_events or [])
                         if e.get("type") == "diplomatic_mission_cancelled"]
            self.assertTrue(cancelled, "the event is queued either way")
            self.assertFalse(
                _is_dispatch_event_visible(cancelled[0], world, "France"),
                "lever DOWN: the fog rule can no longer see its subject")
        finally:
            D.MISSION_COLLAPSE_IS_ANNOUNCED = original


class TestTheMissionStopsWhenItsWorkIsDone(unittest.TestCase):
    """MS-9: at the relation ceiling it charged DP forever for nothing."""

    def _at_ceiling(self):
        world = _mission_world({"type": "IMPROVE_RELATIONS", "target": "Prussia",
                                "turns_active": 9, "completed": False,
                                "paused": False})
        world.nation_relations[world._make_diplo_key("France", "Prussia")] = 100
        return world

    def test_a_mission_at_the_ceiling_completes(self):
        from backend.game_logic.diplomacy import _process_mission_effects
        world = self._at_ceiling()
        _process_mission_effects(world)
        self.assertTrue(world.active_diplomatic_mission["completed"])

    def test_a_mission_below_the_ceiling_keeps_running(self):
        from backend.game_logic.diplomacy import _process_mission_effects
        world = self._at_ceiling()
        world.nation_relations[world._make_diplo_key("France", "Prussia")] = 40
        _process_mission_effects(world)
        self.assertFalse(world.active_diplomatic_mission["completed"])

    def test_lever_down_reproduces_the_permanent_tax(self):
        from backend.game_logic import diplomacy as D
        world = self._at_ceiling()
        original = D.MISSION_AT_THE_CEILING_IS_FINISHED
        try:
            D.MISSION_AT_THE_CEILING_IS_FINISHED = False
            D._process_mission_effects(world)
            self.assertFalse(world.active_diplomatic_mission["completed"])
        finally:
            D.MISSION_AT_THE_CEILING_IS_FINISHED = original

    def test_the_pause_survives_while_the_diplomat_is_abroad(self):
        """MS-10: the resume arm un-paused him on the very next tick."""
        from backend.game_logic.diplomacy import _process_mission_dp
        world = _mission_world({"type": "IMPROVE_RELATIONS", "target": "Prussia",
                                "turns_active": 2, "completed": False,
                                "paused": True, "paused_turns": 1})
        world.diplomatic_points = 10
        world.talleyrand_state = "IN_TRANSIT"
        _process_mission_dp(world)
        self.assertTrue(world.active_diplomatic_mission["paused"])
        self.assertEqual(world.diplomatic_points, 10, "and charges nothing")

    def test_he_resumes_once_the_diplomat_is_home(self):
        from backend.game_logic.diplomacy import _process_mission_dp
        world = _mission_world({"type": "IMPROVE_RELATIONS", "target": "Prussia",
                                "turns_active": 2, "completed": False,
                                "paused": True, "paused_turns": 1})
        world.diplomatic_points = 10
        world.talleyrand_state = "ON_MISSION"
        _process_mission_dp(world)
        self.assertFalse(world.active_diplomatic_mission["paused"])

    def test_lever_down_reproduces_the_inert_pause(self):
        from backend.game_logic import diplomacy as D
        world = _mission_world({"type": "IMPROVE_RELATIONS", "target": "Prussia",
                                "turns_active": 2, "completed": False,
                                "paused": True, "paused_turns": 1})
        world.diplomatic_points = 10
        world.talleyrand_state = "IN_TRANSIT"
        original = D.MISSION_PAUSE_SURVIVES_TRANSIT
        try:
            D.MISSION_PAUSE_SURVIVES_TRANSIT = False
            D._process_mission_dp(world)
            self.assertFalse(world.active_diplomatic_mission["paused"])
        finally:
            D.MISSION_PAUSE_SURVIVES_TRANSIT = original


class TestTheUndermineRowStatesItsGate(unittest.TestCase):
    """MS-6: the only diplomacy row that did not."""

    def _row(self, world, court):
        from backend.game_logic.diplomacy import get_available_diplomatic_actions
        return {a["action"]: a for a in
                get_available_diplomatic_actions(world, court)
                }.get("mission_undermine")

    def test_a_court_with_no_alliance_says_so(self):
        world = _europe()
        world.diplomatic_points = 10
        world.active_diplomatic_mission = None
        lonely = None
        for court in world.get_active_nations():
            if court == world.player_nation:
                continue
            if not any(world.are_allies(court, other)
                       for other in world.get_active_nations()
                       if other != court):
                lonely = court
                break
        self.assertIsNotNone(lonely, "the board must hold an unallied court")
        row = self._row(world, lonely)
        if row is not None:
            self.assertFalse(row["available"])
            self.assertEqual(row["disabled_reason"], "No alliance to undermine")

    def test_lever_down_reproduces_the_silent_row(self):
        from backend.game_logic import diplomacy as D
        world = _europe()
        world.diplomatic_points = 10
        world.active_diplomatic_mission = None
        lonely = next(
            (c for c in world.get_active_nations()
             if c != world.player_nation
             and not any(world.are_allies(c, o)
                         for o in world.get_active_nations() if o != c)), None)
        original = D.MISSION_UNDERMINE_ROW_IS_HONEST
        try:
            D.MISSION_UNDERMINE_ROW_IS_HONEST = False
            row = self._row(world, lonely)
            if row is not None:
                self.assertNotEqual(row.get("disabled_reason"),
                                    "No alliance to undermine")
        finally:
            D.MISSION_UNDERMINE_ROW_IS_HONEST = original


class TestTheConfirmationReadsAsEnglish(unittest.TestCase):

    def test_improve_relations_carries_its_preposition(self):
        """MS-4: "begin efforts to improve relations Austria"."""
        from backend.game_logic.diplomatic_dialogue import MISSION_DESCRIPTIONS
        for mission_type, description in MISSION_DESCRIPTIONS.items():
            composed = f"begin efforts to {description} Austria"
            self.assertNotIn("relations Austria", composed,
                             f"{mission_type} composes ungrammatically")


# ════════════════════════════════════════════════════════════════════
# the tree compiles on the interpreter that is running it
# ════════════════════════════════════════════════════════════════════

class TestTheTreeCompilesHere(unittest.TestCase):
    """PR-3: `tests/test_notifications.py` carried a nested same-type quote
    inside an f-string — legal only on Python 3.12 (PEP 701) — so on 3.11 the
    file failed to COLLECT and pytest interrupted the ENTIRE run. The
    pre-commit hook runs that suite, so the hook was unusable there."""

    def test_every_repo_source_file_compiles(self):
        import pathlib
        root = pathlib.Path(__file__).resolve().parents[1]
        bad = []
        for sub in ("backend", "tests", "tools"):
            for path in (root / sub).rglob("*.py"):
                text = path.read_text(encoding="utf-8-sig")
                try:
                    compile(text, str(path), "exec")
                except SyntaxError as exc:
                    bad.append(f"{path.relative_to(root)}:{exc.lineno} {exc.msg}")
        self.assertEqual(bad, [], "files that do not compile on this Python")

    def test_the_census_would_catch_a_real_offender(self):
        """Sensitivity arm — the pin above must be able to fail."""
        with self.assertRaises(SyntaxError):
            compile('f"{d["k"]}"', "<probe>", "exec")

    def test_the_sweep_tool_finds_an_interpreter_here(self):
        """PR-3: `mutation_sweep.PY` was a literal Windows venv path, so the
        tool — and the twelve pins that drive it — died everywhere else."""
        import os
        import sys
        sys.path.insert(0, str(__import__("pathlib").Path(__file__)
                               .resolve().parents[1] / "tools"))
        import mutation_sweep
        self.assertTrue(os.path.exists(mutation_sweep.PY),
                        f"resolved interpreter does not exist: {mutation_sweep.PY}")
        # `sys.executable` always exists, so the line above passes even when
        # the venv is never found — the sweep said so. The claim is that the
        # tool finds THIS checkout's venv on THIS platform.
        # ...and `sys.executable` IS the venv while the suite runs under it,
        # so comparing paths cannot tell a successful search from the
        # fallback. Drive the resolver with `sys.executable` pointed
        # somewhere else: the search must still find the venv.
        venv = mutation_sweep.ROOT / ".venv"
        present = [p for p in (venv / "Scripts" / "python.exe",
                               venv / "bin" / "python") if p.exists()]
        if present:
            original = sys.executable
            try:
                sys.executable = "/nonexistent/sentinel-python"
                resolved = mutation_sweep._resolve_interpreter()
            finally:
                sys.executable = original
            self.assertEqual(os.path.realpath(resolved),
                             os.path.realpath(str(present[0])),
                             "the search must find this checkout's venv, "
                             "not fall through to sys.executable")


if __name__ == "__main__":
    unittest.main()


class TestNoInternalTagReachesTheLog(unittest.TestCase):
    """PR-2, the three producers a 40-turn board still leaked through after
    the template fix: the rebuff court list, the vassal call-to-arms
    one-liner and the settlement rail's war label."""

    def test_a_court_list_is_humanised(self):
        from backend.campaign_log import _join_courts
        line = _join_courts(["Portugal", "Saxony", "PapalStates"])
        self.assertIn("Papal States", line)
        self.assertNotIn("PapalStates", line)

    def test_the_vassal_call_to_arms_is_humanised(self):
        from backend.campaign_log import format_event_oneliner
        line = format_event_oneliner({"type": "vassal_auto_join_war",
                                      "vassal": "KingdomOfItaly",
                                      "lord": "France"})
        self.assertIn("Kingdom of Italy", line)
        self.assertNotIn("KingdomOfItaly", line)

    def test_the_settlement_war_label_is_humanised(self):
        from backend.game_logic.ai_diplomacy import _settlement_request_war_label
        label = _settlement_request_war_label(
            {"attackers": ["France", "KingdomOfItaly"],
             "defenders": ["Britain", "PapalStates"]}, "war_1")
        self.assertNotIn("KingdomOfItaly", label)
        self.assertNotIn("PapalStates", label)
        self.assertIn("Kingdom of Italy", label)

    def test_the_local_import_does_not_shadow_its_siblings(self):
        """The first cut of the vassal fix used a function-scoped
        `from ... import display_nation`, which made the name local for
        EVERY arm of `format_event_oneliner` and raised UnboundLocalError
        six hundred lines away."""
        from backend.campaign_log import format_event_oneliner
        line = format_event_oneliner({"type": "nation_eliminated",
                                      "nation": "PapalStates"})
        self.assertIsInstance(line, str)
        self.assertTrue(line)


class TestTheDeclarationNamesItsDeclarer(unittest.TestCase):
    """PR-4: the cause clause opened with a bare "He", following a headline
    that names TWO courts — the most frequent headline on the board."""

    class _W:
        player_nation = "France"
        threat_sources_this_turn = []

    def test_the_treaty_arm_names_the_court(self):
        from backend.game_logic.dispatch import war_declaration_cause
        line = war_declaration_cause(self._W(), "Britain",
                                     {"breached_treaty": "Peace Treaty"})
        self.assertTrue(line.startswith("Britain"), line)
        self.assertNotIn("He tears", line)

    def test_a_tagged_court_is_named_properly(self):
        from backend.game_logic.dispatch import war_declaration_cause
        line = war_declaration_cause(self._W(), "PapalStates",
                                     {"breached_treaty": "Open Borders Agreement"})
        self.assertIn("Papal States", line)
        self.assertNotIn("PapalStates", line)

    def test_lever_down_reproduces_the_dangling_pronoun(self):
        from backend.game_logic import dispatch as D
        original = D.THE_DECLARATION_NAMES_THE_DECLARER
        try:
            D.THE_DECLARATION_NAMES_THE_DECLARER = False
            line = D.war_declaration_cause(self._W(), "Britain",
                                           {"breached_treaty": "Peace Treaty"})
            self.assertTrue(line.startswith("He tears up"), line)
        finally:
            D.THE_DECLARATION_NAMES_THE_DECLARER = original

    def test_the_outer_lever_still_silences_the_whole_clause(self):
        from backend.game_logic import dispatch as D
        original = D.THE_DECLARATION_NAMES_ITS_CAUSE
        try:
            D.THE_DECLARATION_NAMES_ITS_CAUSE = False
            self.assertEqual(
                D.war_declaration_cause(self._W(), "Britain",
                                        {"breached_treaty": "Peace Treaty"}), "")
        finally:
            D.THE_DECLARATION_NAMES_ITS_CAUSE = original


class TestTheQualityGateCanRun(unittest.TestCase):
    """PR-3, fourth member: the tracked pre-commit hook hard-coded
    `.venv/Scripts/python.exe`, so on any non-Windows checkout it aborted
    every commit with "venv python not found" and the gate never ran."""

    def _hook(self):
        import pathlib
        return (pathlib.Path(__file__).resolve().parents[1]
                / "scripts" / "git-hooks" / "pre-commit").read_text(
                    encoding="utf-8")

    def test_the_hook_probes_both_venv_layouts(self):
        src = self._hook()
        self.assertIn(".venv/Scripts/python.exe", src)
        self.assertIn(".venv/bin/python", src)

    def test_the_windows_layout_is_probed_first(self):
        """So the authoring machine resolves byte-identically to before."""
        src = self._hook()
        self.assertLess(src.index(".venv/Scripts/python.exe"),
                        src.index(".venv/bin/python"))

    def test_the_installed_hook_matches_the_tracked_source(self):
        import pathlib
        root = pathlib.Path(__file__).resolve().parents[1]
        installed = root / ".git" / "hooks" / "pre-commit"
        if not installed.exists():
            self.skipTest("no hook installed in this checkout")
        self.assertEqual(installed.read_text(encoding="utf-8"), self._hook(),
                         "the installed hook is stale — re-copy it")


class TestTheSettlementRailNamesItsCourts(unittest.TestCase):
    """PR-2, the last producer: a war label is composed by several
    functions, some `X vs Y` and some `A + B vs C + D`, and every one of
    them joined internal TAGS. Humanised at the RENDER chokepoint instead of
    chased producer by producer."""

    def test_a_plus_joined_label_is_humanised(self):
        from backend.game_logic.settlement_presentation import humanize_war_label
        out = humanize_war_label(
            "France + Spain + KingdomOfItaly vs Britain + PapalStates")
        self.assertNotIn("KingdomOfItaly", out)
        self.assertNotIn("PapalStates", out)
        self.assertIn("Kingdom of Italy", out)
        self.assertIn("Papal States", out)

    def test_the_separators_survive(self):
        from backend.game_logic.settlement_presentation import humanize_war_label
        out = humanize_war_label("Ottoman + Saxony vs France")
        self.assertIn(" vs ", out)
        self.assertIn(" + ", out)

    def test_an_unknown_token_is_left_alone(self):
        from backend.game_logic.settlement_presentation import humanize_war_label
        self.assertEqual(humanize_war_label("war_3"), "war_3")
        self.assertEqual(humanize_war_label(""), "")

    def test_lever_down_reproduces_the_raw_label(self):
        from backend.game_logic import settlement_presentation as SP
        original = SP.WAR_LABEL_NAMES_ITS_COURTS
        try:
            SP.WAR_LABEL_NAMES_ITS_COURTS = False
            self.assertIn("KingdomOfItaly",
                          SP.humanize_war_label("France vs KingdomOfItaly"))
        finally:
            SP.WAR_LABEL_NAMES_ITS_COURTS = original

    def test_the_oneliner_uses_it(self):
        from backend.game_logic.settlement_presentation import (
            compose_summary_oneliner)
        line = compose_summary_oneliner({
            "war_id": "war_1",
            "war_label": "France + KingdomOfItaly vs Britain",
            "terms_summary": ["white_peace"],
        })
        self.assertNotIn("KingdomOfItaly", line)
        self.assertIn("Kingdom of Italy", line)
