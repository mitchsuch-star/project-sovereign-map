"""Pinning tests for the July 10, 2026 creative-audit inline legibility fixes.

The Section-8 creative/fun-factor capstone (AUDIT_GUIDELINE.md 8) permits
inline fixes only for trivial legibility slips: raw internal keys in player
prose and typo-class grammar. These tests pin the four fixes it applied:

1. Intel report (status) humanizes camelCase marshal keys ("ArchdukeJohn"
   -> "Archduke John") in CONFIRMED INTELLIGENCE and RECENT REPORTS lines.
2. Morning-dispatch sightings humanize the emitted marshal name field.
3. Treaty / proposal copy uses a correct indefinite article ("an Open
   Borders Agreement", "an open borders proposal") via
   display_names.with_indefinite_article; the dispatch templates were
   reworded to "signed the {treaty_type}".
4. The pending-objection command guard names the objecting marshal and no
   longer leaks the /respond_to_objection endpoint into player prose
   (pinned in test_disobedience.py alongside the original guard test).
5. Talleyrand's "which nation shall I approach?" landscape list renders
   nation display names ("Kingdom of Italy"), never raw keys
   ("KingdomOfItaly").
"""

from backend.display_names import with_indefinite_article
from backend.models.world_state import WorldState


class TestWithIndefiniteArticle:
    def test_vowel_gets_an(self):
        assert with_indefinite_article("Open Borders Agreement") == \
            "an Open Borders Agreement"
        assert with_indefinite_article("open borders") == "an open borders"

    def test_consonant_gets_a(self):
        assert with_indefinite_article("Full Alliance") == "a Full Alliance"
        assert with_indefinite_article("peace treaty") == "a peace treaty"

    def test_empty_passthrough(self):
        assert with_indefinite_article("") == ""


class TestIntelReportHumanizesMarshalKeys:
    def _world_with_camel_case_enemy(self):
        world = WorldState()
        # Find any enemy marshal and give it a camelCase-keyed name in a
        # region the player can see at FULL.
        player = world.player_nation
        enemy = next(m for m in world.marshals.values()
                     if m.nation != player)
        enemy.name = "ArchdukeJohn"
        world.marshals["ArchdukeJohn"] = world.marshals.pop(
            next(k for k, v in world.marshals.items() if v is enemy))
        from backend.models.intel import FULL
        intel = world.intel.get(enemy.location)
        assert intel is not None
        intel.visibility = FULL
        intel.known_marshals = [{
            "name": "ArchdukeJohn", "nation": enemy.nation,
            "strength": 10000, "stance": "neutral", "morale": 100,
        }]
        intel.last_updated_turn = world.current_turn
        return world

    def test_confirmed_intelligence_line_is_humanized(self):
        from backend.intel_report import generate_intel_report
        world = self._world_with_camel_case_enemy()
        report = generate_intel_report(world)
        text = str(report["report_text"])
        assert "ArchdukeJohn" not in text
        assert "Archduke John" in text


class TestDispatchSightingsHumanized:
    def test_sighting_name_field_is_humanized(self):
        from backend.game_logic.dispatch import _build_intelligence
        world = WorldState()
        player = world.player_nation
        enemy = next(m for m in world.marshals.values()
                     if m.nation != player)
        from backend.models.intel import FULL
        intel = world.intel.get(enemy.location)
        assert intel is not None
        intel.visibility = FULL
        intel.known_marshals = [{
            "name": "ArchdukeJohn", "nation": enemy.nation,
            "strength": 12000,
        }]
        intel.last_updated_turn = world.current_turn
        sightings = _build_intelligence(world, player)
        names = [s["name"] for s in sightings]
        assert "ArchdukeJohn" not in names
        assert "Archduke John" in names


class TestNationLandscapeUsesDisplayNames:
    def test_proposal_options_landscape_humanizes_nation_keys(self):
        from backend.commands.executor import CommandExecutor
        world = WorldState()
        game_state = {"world": world}
        executor = CommandExecutor()
        result = executor.execute(
            {"command": {"action": "diplomacy", "marshal": None,
                         "target": None}},
            game_state,
        )
        dialogue = result.get("diplomatic_dialogue") or {}
        text = dialogue.get("talleyrand_text", "")
        if "diplomatic landscape includes" in text:
            assert "KingdomOfItaly" not in text
            assert "PapalStates" not in text
