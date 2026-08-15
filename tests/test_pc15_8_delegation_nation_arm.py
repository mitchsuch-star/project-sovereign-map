"""PC15-8 — the live literal ASK arm, fixed at the DETECTION seam.

The flagship playtest's "Soult, deal with the Austrians" (canonical
delegation phrasing, literal marshal) executed a full attack on live
parse. Root cause was NOT the router (route_arm already forces ASK for a
literal marshal regardless of the parse): ``_resolve_target`` knew enemy
marshals and regions but not NATION references, so ``detect_delegation``
returned None, the whole CR-5 router — including the literal ASK — was
bypassed, and the live LLM's guessed ``attack`` (measured live at
confidence 0.85) executed through the ordinary pipeline.

Fix, three seams, router untouched (Golden Rule 6 / guardrail (e) hold):

1. The NATION arm in ``_resolve_target`` (deterministic): a demonym or
   nation name resolves to the nearest VISIBLE enemy marshal of that
   nation (fog-honest, R5), only for nations AT WAR with the player, and
   only after the marshal/region tables (so "deal with Hanover" stays the
   province). "The Austrians" now produces a DelegationMatch and every
   personality gets its blessed arm — the literal ASK included.
2. The prompt's literal row instructs a concrete no-guess: action
   "unknown" for a literal delegation.
3. PARSE_TOOL's ``action`` description names the "unknown" escape hatch —
   it previously said "One of the Valid Actions", overriding the prompt.

Live compliance was MEASURED, not assumed (Aug 15, 2026, temp-0 Haiku):
"Soult, deal with Mack" ×3 → unknown, unknown, scout; "Soult, deal with
the situation" ×2 → unknown ×2. Never attack — but not perfectly
deterministic, so NO parse-tier live pin is written for the literal arm
(the old corpus row ``cr5-deleg-literal-soult-resolves-live`` pinned
success:true off the model resolving an action and is RETIRED for a
mock_only row; the definitive literal→ASK stays deterministic here and in
``TestAskArmEndpoint``). Endpoint verified live: the ASK fired for
Soult and the aggressive PURSUE + bad-odds interrupt fired for Ney, both
on the nation phrasing.
"""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.commands.delegation import (
    _resolve_target, detect_delegation, route_arm)
from backend.models.world_state import WorldState

REPO_ROOT = Path(__file__).resolve().parent.parent
SCENARIO_PATH = (REPO_ROOT / "godot-client" / "project-sovereign" /
                 "assets" / "maps" / "europe_1805.json")


@pytest.fixture()
def world1805():
    return WorldState.from_scenario(str(SCENARIO_PATH))


class TestNationArmResolution:
    def test_demonym_resolves_to_nearest_visible_enemy(self, world1805):
        soult = world1805.get_marshal("Soult")
        resolved = _resolve_target(world1805, "the Austrians",
                                   for_marshal=soult)
        assert resolved is not None
        target, scout_target, display = resolved
        # The 1805-exact answer: Mack's army at Swabia (Ulm) is the
        # Austrian force nearest Soult at Lorraine.
        assert target == "Mack"
        assert scout_target == "Swabia"
        assert "Mack" in display

    def test_nation_name_resolves_too(self, world1805):
        soult = world1805.get_marshal("Soult")
        resolved = _resolve_target(world1805, "Austria", for_marshal=soult)
        assert resolved is not None
        assert resolved[0] == "Mack"

    def test_at_peace_nation_does_not_resolve(self, world1805):
        """A delegation is not a declaration of war: Prussia is at peace
        with France at boot, so 'the Prussians' must not hand any arm a
        Prussian officer."""
        at_war = world1805.get_nations_at_war_with("France")
        assert "Prussia" not in at_war, "boot premise moved — re-derive"
        soult = world1805.get_marshal("Soult")
        assert _resolve_target(world1805, "the Prussians",
                               for_marshal=soult) is None

    def test_region_table_still_shadows_nation_names(self, world1805):
        """'deal with Hanover' names the PROVINCE (region table runs
        first) — the nation arm must never steal it."""
        assert "Hanover" in world1805.regions
        soult = world1805.get_marshal("Soult")
        resolved = _resolve_target(world1805, "Hanover", for_marshal=soult)
        assert resolved is not None
        assert resolved[0] == "Hanover"  # the region, not an officer

    def test_fog_honest_no_visible_enemy_no_resolution(self, world1805):
        """R5: an invisible army cannot be a quarry. Blind every Austrian
        region and the arm returns None (fall through to Berthier)."""
        from backend.models.intel import UNKNOWN
        for m in world1805.get_enemies_of_nation("France"):
            if m.nation == "Austria":
                world1805._intel_entry(m.location).visibility = UNKNOWN
        soult = world1805.get_marshal("Soult")
        assert _resolve_target(world1805, "the Austrians",
                               for_marshal=soult) is None

    def test_marshal_name_still_wins_over_nation(self, world1805):
        """'deal with Mack' resolves the officer exactly as before —
        the nation arm runs LAST."""
        soult = world1805.get_marshal("Soult")
        resolved = _resolve_target(world1805, "Mack", for_marshal=soult)
        assert resolved[0] == "Mack"


class TestDetectionAndRouting:
    def test_flagship_phrase_now_matches(self, world1805):
        m = detect_delegation(world1805, "Soult, deal with the Austrians",
                              None)
        assert m is not None
        assert m.marshal == "Soult"
        assert m.personality == "literal"
        assert m.target == "Mack"

    def test_literal_asks_even_on_a_live_resolved_parse(self, world1805):
        """The router half of the flagship defect, pinned end to end:
        route_arm ignores the parse for a literal marshal."""
        m = detect_delegation(world1805, "Soult, deal with the Austrians",
                              None)
        assert route_arm(m.personality, True) == "ask"
        assert route_arm(m.personality, False) == "ask"

    def test_unresolvable_delegation_still_falls_through(self, world1805):
        """'deal with the situation' has no officer, province, or nation —
        detection returns None exactly as before (Berthier recovers)."""
        assert detect_delegation(
            world1805, "Soult, deal with the situation", None) is None


class TestEndpointMockAsk:
    """Guardrail (e) on the nation phrasing: in mock mode EVERY
    personality degrades to the ASK — now reachable for 'the Austrians'."""

    @pytest.fixture()
    def endpoint1805(self):
        import backend.main as main_module
        from backend.commands.parser import CommandParser as _CP

        orig = (main_module.parser, main_module.world,
                main_module.game_state)
        main_module.parser = _CP(use_real_llm=False)
        main_module.world = WorldState.from_scenario(str(SCENARIO_PATH))
        main_module.game_state = {"world": main_module.world}
        try:
            yield TestClient(main_module.app), main_module
        finally:
            (main_module.parser, main_module.world,
             main_module.game_state) = orig

    def test_nation_delegation_asks_for_every_personality(self,
                                                          endpoint1805):
        client, m = endpoint1805
        for marshal in ("Soult", "Ney", "Davout"):
            data = client.post(
                "/command",
                json={"command": f"{marshal}, deal with the Austrians"}
            ).json()
            assert data.get("clarification_kind") == "delegation", (
                f"{marshal}: the nation phrasing must reach the CR-5 ASK, "
                f"got: {str(data.get('message'))[:120]!r}")
            assert "Mack" in data.get("message", "")

    def test_no_battle_executes_from_the_flagship_phrase(self,
                                                         endpoint1805):
        client, m = endpoint1805
        data = client.post(
            "/command",
            json={"command": "Soult, deal with the Austrians"}).json()
        blob = str(data.get("message", "")).lower()
        assert "casualties" not in blob
        assert "battle of" not in blob


class TestPromptAndSchemaPins:
    def test_prompt_literal_row_names_the_no_guess_action(self):
        import inspect

        from backend.ai import prompt_builder as pb
        src = inspect.getsource(pb)
        assert 'set action "unknown"' in src, (
            "the literal row lost its concrete no-guess instruction — the "
            "live model will guess attack again (PC15-8)")
        assert "NEVER resolve his delegation" in src

    def test_schema_action_names_the_escape_hatch(self):
        """The tool schema said 'One of the Valid Actions' and OVERRODE the
        prompt row — measured: the model returned attack for a literal
        delegation until the schema named unknown as legitimate."""
        from backend.ai.providers import PARSE_TOOL
        desc = PARSE_TOOL["input_schema"]["properties"]["action"][
            "description"]
        assert "unknown" in desc
        assert "LITERAL" in desc

    def test_router_and_guardrail_e_untouched(self):
        """Scope pin: the fix is detection + prompt only. classify_arm's
        literal row and the mock gate are byte-level load-bearing."""
        import inspect

        from backend.commands import delegation as d
        src = inspect.getsource(d.classify_arm)
        assert 'return "ask"' in src
        src2 = inspect.getsource(d.parse_resolved_to_action)
        assert '"mock"' in src2
