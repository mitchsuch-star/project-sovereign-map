"""Row BA, session BA-6 / row MC (November 17, 2026): the open calls ruled
under the user's "leave no open calls or anything make decisions yourself
soundly with research" and BUILT here — each behind its own seam
(`tests/_ba6_seams.py`), each with its behaviour test. The whole record of the
rulings (built, homed or closed, with the reason for each):
`docs/audits/OPEN_CALLS_RULED_2026_11_17.md`.

GRD-31  a cautious marshal who defies a pursuit fortifies.
GRD-17  each aggressive marshal objects to sitting still in his own voice.
GRD-2   a declaration of war rides the morning always (diplomacy has no fog).
GRD-5   an envoy's letter names its kind on the rail.
GRD-30  a recruit-morale law says a training ground voids it.
HASH    the court forms' tie order no longer differs by hash seed.
"""
from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from backend.commands import defiance as DF
from backend.commands import strategic_executor as SE
from backend.commands.objection_v2 import ConcernLevel
from backend.game_logic import ai_diplomacy as AD
from backend.game_logic import diplomacy as DP
from backend.game_logic import reforms as RF
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCENARIO = REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"


@pytest.fixture(scope="module")
def opening():
    return WorldState.from_scenario(str(SCENARIO))


@pytest.fixture
def world(opening):
    return WorldState.from_dict(opening.to_dict())


class TestGRD31ACautiousManDefiesAPursuitByFortifying:

    def test_davout_fortifies(self, world):
        assert world.marshals["Davout"].personality == "cautious"
        assert DF.get_defiant_action(world.marshals["Davout"], "PURSUE") == "fortify"
        assert DF.get_defiant_action(world.marshals["Davout"], "pursue") == "fortify"

    def test_an_aggressive_man_never_objects_to_a_pursuit(self, world):
        assert DF.get_defiant_action(world.marshals["Ney"], "PURSUE") is None

    def test_seam_down_he_sulks(self, world, monkeypatch):
        monkeypatch.setattr(DF, "a_cautious_man_defies_a_pursuit_by_fortifying", lambda: False)
        assert DF.get_defiant_action(world.marshals["Davout"], "PURSUE") is None


class TestGRD17EachAggressiveManInHisOwnVoice:

    def _says(self, world, name, concern=ConcernLevel.MODERATE):
        from backend.commands.executor import CommandExecutor
        ex = CommandExecutor()
        return ex._strategic._generate_objection_message(
            world.marshals[name], "fortify", {}, concern, "firm", world=world)

    def test_four_voices_four_lines(self, world):
        lines = {n: self._says(world, n) for n in ("Ney", "Murat", "Lannes", "Massena")}
        assert len(set(lines.values())) == 4, lines
        for name, line in lines.items():
            assert SE.IDLE_OBJECTION_VOICES[name] in line and "sit idle" not in line, name

    def test_the_lines_that_carry_a_reading_are_unchanged(self, world):
        assert "We outnumber them" in self._says(world, "Ney", ConcernLevel.EXTREME)
        assert "we have the advantage" in self._says(world, "Murat", ConcernLevel.STRONG)

    def test_seam_down_the_one_line(self, world, monkeypatch):
        monkeypatch.setattr(SE, "each_aggressive_man_objects_in_his_own_voice", lambda: False)
        assert "I would rather attack than sit idle." in self._says(world, "Lannes")

    def test_every_voice_is_a_french_aggressive_marshal_of_the_opening(self, world):
        for name in SE.IDLE_OBJECTION_VOICES:
            m = world.marshals[name]
            assert m.nation == "France" and m.personality == "aggressive", name


class TestGRD2ADeclarationIsPublic:

    @staticmethod
    def _declared(world):
        """Prussia declares on Sweden - two courts, France a bystander - through
        the real `declare_war`; the morning's declaration event it queued."""
        world.pending_dispatch_events = []
        result = DP.declare_war(world, "Prussia", "Sweden")
        assert result.get("success"), result.get("message")
        rows = [e for e in world.pending_dispatch_events if e.get("type") == "diplomatic_war_declared"]
        assert rows, world.pending_dispatch_events
        return rows[-1]

    def test_the_declaration_rides_always(self, world):
        assert self._declared(world)["fog_rule"] == "always"

    def test_seam_down_it_needs_sight(self, world, monkeypatch):
        monkeypatch.setattr(DP, "a_declaration_of_war_is_public", lambda: False)
        assert self._declared(world)["fog_rule"] == "partial_on_nation"

    def test_a_war_between_two_courts_reaches_the_morning_unseen(self, world):
        """Prussia on Hanover — two courts France may not see at all: the
        row rides 'always'; the old tag needed PARTIAL sight of one."""
        from backend.game_logic.dispatch import _is_dispatch_event_visible
        event = {"type": "diplomatic_war_declared", "fog_rule": "always",
                 "template_vars": {"nation": "Prussia", "target": "Hanover"}}
        assert _is_dispatch_event_visible(event, world, "France") is True


class TestGRD5AnEnvoyNamesHisLetter:

    def test_the_letter_is_named(self):
        assert AD._the_letters_name({"proposal_type": "defensive_alliance"}) == "Defensive Alliance"
        assert AD._the_letters_name({"proposal_type": "p3", "terms": {"type": "non_aggression"}}) == \
            "Non-Aggression Pact"
        assert AD._the_letters_name({}) == ""

    def test_the_rail_line_says_it(self):
        src = inspect.getsource(AD)
        assert 'f"An envoy from {sender} has arrived with a letter: {_kind}."' in src
        assert 'f"Envoy from {sender}" + (f": {_kind}" if _kind else "")' in src

    @staticmethod
    def _the_rail_after_a_letter(world):
        """Denmark's open-borders letter to France - a kind with no rail line of
        its own - delivered through the real transport; the notice it wrote."""
        letter = {"source": "Denmark", "proposal_type": "open_borders", "priority": 4,
                  "terms": {"type": "open_borders", "proposer_nation": "Denmark",
                            "target_nation": "France", "sweeteners": [], "demands": [],
                            "clauses": ["open_borders"]},
                  "talleyrand_assessment": "Test", "turn_generated": 1}
        assert AD.deliver_ai_proposal(letter, world), "the letter is delivered"
        notes = [n for n in world.notifications._pending if n.get("type") == "diplomatic_proposal"
                 or "Envoy from" in str(n.get("title"))]
        assert notes, [n.get("title") for n in world.notifications._pending]
        return notes[-1]

    def test_the_rail_names_the_letter(self, world):
        note = self._the_rail_after_a_letter(world)
        assert note["title"].endswith(": Open Borders Agreement"), note["title"]
        assert note["message"].endswith("has arrived with a letter: Open Borders Agreement."), note["message"]

    def test_seam_down_the_old_line(self, world, monkeypatch):
        monkeypatch.setattr(AD, "an_envoy_names_his_letter", lambda: False)
        note = self._the_rail_after_a_letter(world)
        assert note["message"].endswith("has arrived with a proposal."), note["message"]
        assert ":" not in note["title"], note["title"]


class TestGRD30ALawSaysWhereItIsVoid:

    def test_the_line_says_the_training_ground_voids_it(self):
        line = RF.effect_line({"type": "recruit_morale", "arm": "infantry", "value": 10})
        assert line == "infantry drafts muster at +10 morale (not at a training ground, whose 70 replaces it; Moore's drafts never muster under 60)"

    def test_it_is_true_the_ground_replaces_the_base(self):
        from backend.commands.economy_executor import EconomyExecutor
        src = inspect.getsource(EconomyExecutor)
        assert 'if region.has_building("training_ground"):' in src
        assert "RECRUIT_MORALE = self.RECRUIT_MORALE_TRAINED" in src
        assert EconomyExecutor.RECRUIT_MORALE_TRAINED == 70

    def test_seam_down_the_term_alone(self, monkeypatch):
        monkeypatch.setattr(RF, "a_law_says_where_it_is_void", lambda: False)
        assert RF.effect_line({"type": "recruit_morale", "arm": "infantry", "value": 10}) == \
            "infantry drafts muster at +10 morale"


class TestTheCourtFormsTieOrder:

    def test_longest_first_ties_alphabetical(self):
        from backend.commands import dialogue_routing as DR
        DR._KNOWN_COURT_FORMS = None
        forms = DR._closed_known_court_forms()
        assert forms == sorted(forms, key=lambda f: (-len(f), f))
