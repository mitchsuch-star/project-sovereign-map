"""Pins for Comprehensive Codebase Audit fixes (July 9, 2026) that have no
natural home in an existing test file. Audit log: docs/audits/AUDIT_2026_07_09.md

Fix 2.1: combat personality messages must label the PERSONALITY, never one
marshal's signature ability/epithet. The 1805 roster has 4 aggressive marshals
(Ney, Lannes, Murat, Massena) and 13 cautious ones sharing these code paths —
pre-fix, Murat's attacks were captioned "Bravest of the Brave" (Ney's ability)
and Kutuzov's defenses "Iron Marshal" (Davout's epithet).

Fix 2.2: Berthier coordination observations must read the PLAYER'S side of
coordination_context. The legacy context carried attacker-side data only, so
an enemy attacker's combined-arms triangle (or its hostile/devoted internal
politics) was narrated as "our side" whenever the player was the defender.
"""

from backend.game_logic.battle_report import _pick_observation
from backend.game_logic.combat import CombatResolver
from backend.models.marshal import Marshal, Stance


def _make_marshal(name: str, personality: str, nation: str, stance: Stance) -> Marshal:
    marshal = Marshal(
        name=name,
        location="Belgium",
        strength=50000,
        personality=personality,
        nation=nation,
        skills={
            "tactical": 6,
            "shock": 6,
            "defense": 6,
            "logistics": 5,
            "administration": 5,
            "command": 6,
        },
    )
    marshal.stance = stance
    marshal.morale = 100
    return marshal


class TestPersonalityMessagesLabelPersonalityNotAbility:
    """Audit fix 2.1 — combat.py personality-message attribution."""

    def test_aggressive_non_ney_attacker_not_captioned_bravest_of_the_brave(self):
        murat = _make_marshal("Murat", "aggressive", "France", Stance.AGGRESSIVE)
        mack = _make_marshal("Mack", "cautious", "Austria", Stance.NEUTRAL)

        result = CombatResolver().resolve_battle(murat, mack)

        message = result.get("attacker_personality_triggered")
        assert message, "aggressive-stance aggressive attacker must get a personality message"
        assert "Bravest of the Brave" not in message, (
            "Ney's signature ability name must not caption another marshal's "
            "personality bonus"
        )
        assert "Aggressive:" in message

    def test_cautious_non_davout_defender_not_captioned_iron_marshal(self):
        ney = _make_marshal("Ney", "aggressive", "France", Stance.NEUTRAL)
        kutuzov = _make_marshal("Kutuzov", "cautious", "Russia", Stance.DEFENSIVE)

        result = CombatResolver().resolve_battle(ney, kutuzov)

        message = result.get("defender_personality_triggered")
        assert message, "defensive-stance cautious defender must get a personality message"
        assert "Iron Marshal" not in message, (
            "Davout's epithet must not caption another marshal's personality bonus"
        )
        assert "Cautious:" in message


def _battle_result_player_defends(coordination_context):
    """Battle result where BRITAIN attacks the player's (France) marshal."""
    return {
        "outcome": "defender_tactical_victory",
        "attacker": {"name": "Wellington", "casualties": 9000, "remaining": 41000},
        "defender": {"name": "Davout", "casualties": 4000, "remaining": 46000},
        "attacker_nation": "Britain",
        "defender_nation": "France",
        "attacker_original_strength": 50000,
        "defender_original_strength": 50000,
        "modifier_snapshot": {"attacker": [], "defender": []},
        "coordination_context": coordination_context,
        "reinforcement_results_for_report": {},
        "relationship_changes": [],
    }


class TestBerthierCoordinationObservationsArePerspectiveAware:
    """Audit fix 2.2 — battle_report._pick_observation side selection."""

    TRIANGLE_PHRASES = ("triangle", "three arms", "infantry, cavalry, and guns",
                        "combined arms")

    def test_enemy_triangle_not_credited_to_our_side_when_defending(self):
        obs = _pick_observation(
            _battle_result_player_defends({
                "type_count": 3,             # enemy (attacker) side
                "attacker_type_count": 3,
                "defender_type_count": 1,    # our side: single arm
            }),
            player_nation="France",
        )
        assert not any(p in obs.lower() for p in self.TRIANGLE_PHRASES), (
            f"Enemy combined-arms triangle must not be narrated as ours: {obs}"
        )

    def test_our_defender_triangle_fires_when_defending(self):
        obs = _pick_observation(
            _battle_result_player_defends({
                "type_count": 1,
                "attacker_type_count": 1,
                "defender_type_count": 3,    # our side has the triangle
            }),
            player_nation="France",
        )
        assert any(p in obs.lower() for p in self.TRIANGLE_PHRASES), (
            f"Our own defender-side triangle should be narrated: {obs}"
        )

    def test_enemy_hostile_politics_not_narrated_as_ours_when_defending(self):
        obs = _pick_observation(
            _battle_result_player_defends({
                "type_count": 0,
                "hostile_forced_participants": ["Mack"],  # enemy-side squabble
            }),
            player_nation="France",
        )
        hostile_phrases = ("teeth gritted", "under protest", "as strangers",
                           "numbers if not cooperation")
        assert not any(p in obs.lower() for p in hostile_phrases), (
            f"Enemy-side forced-support politics must not be narrated as ours: {obs}"
        )

    def test_attacker_side_keys_still_fire_when_player_attacks(self):
        """Back-compat: legacy attacker-side shape keeps working for player attacks."""
        result = _battle_result_player_defends({"type_count": 3})
        # Flip perspective: France attacks
        result["attacker_nation"] = "France"
        result["defender_nation"] = "Britain"
        result["outcome"] = "attacker_tactical_victory"
        obs = _pick_observation(result, player_nation="France")
        assert any(p in obs.lower() for p in self.TRIANGLE_PHRASES), (
            f"Legacy attacker-side type_count must still fire for player attacks: {obs}"
        )


class TestOrderBreakClearsHoldState:
    """Audit fix 2.3 — the no-alternate-route order break in
    strategic_executor._handle_first_step_blocked must pair the hold-state
    clear with the order clear (its sibling reached-objective arm already
    does), per the §6.2 invariant: every order-clear also clears
    holding_position + hold_region together."""

    def test_no_alternate_route_break_clears_hold_state(self):
        import contextlib
        import io

        from backend.commands.executor import CommandExecutor
        from backend.commands.strategic_executor import StrategicExecutor
        from backend.models.marshal import StrategicOrder
        from backend.models.world_state import WorldState

        world = WorldState(player_nation="France")
        game_state = {"world": world}

        grouchy = world.get_marshal("Grouchy")
        assert grouchy.personality == "literal"  # the silently-reroute branch
        grouchy.location = "Paris"

        # Block every first hop out of Paris with an at-war enemy so the
        # reroute pathfind (avoiding all enemy regions) finds NO route.
        blockers = ["Wellington", "Uxbridge", "Blucher", "Gneisenau"]
        paris_exits = world.regions["Paris"].adjacent_regions
        assert len(paris_exits) >= len(blockers) - 1
        for name, region in zip(blockers, paris_exits):
            world.get_marshal(name).location = region

        # Leftover hold state from a prior HOLD (the +15% literal-hold defense
        # modifier keys off holding_position — a leak corrupts it).
        grouchy.holding_position = True
        grouchy.hold_region = "Paris"
        grouchy.strategic_order = StrategicOrder(
            command_type="MOVE_TO", target="Rhineland", target_type="region",
            started_turn=1, original_command="Grouchy, march to Rhineland",
            path=[paris_exits[0], "Rhineland"],
        )

        se = StrategicExecutor(CommandExecutor())
        blocked_region = paris_exits[0]
        enemies = [m for m in world.marshals.values()
                   if m.location == blocked_region and m.nation != "France"]
        with contextlib.redirect_stdout(io.StringIO()):
            result = se._handle_first_step_blocked(
                grouchy, enemies, blocked_region, world, game_state)

        assert result is not None and result.get("order_cleared") is True
        assert grouchy.strategic_order is None
        assert grouchy.holding_position is False, (
            "order break must clear holding_position with the order"
        )
        assert grouchy.hold_region == ""


class TestVassalCreatedDispatchNamesActualLord:
    """Audit fix 3.1 — the vassal-created dispatch line hardcoded "French
    protection", but both creators are reachable with an AI lord (treaty
    ratification passes `proposer`; settlement clauses pass `vassal_lord`),
    so a Prussian vassalization announced French protection."""

    def test_dispatch_line_names_the_lord_not_france(self):
        from backend.game_logic.dispatch import _format_dispatch_event_text
        from backend.game_logic.vassal import create_vassal_treaty
        from backend.models.world_state import WorldState

        world = WorldState(player_nation="France")
        world.diplomatic_states["Prussia|Saxony"] = "OPEN_BORDERS"
        # Inflate Prussia's power so Saxony falls under the WPS-B power cap
        # (the cap is not under test here — the dispatch attribution is).
        for region in world.regions.values():
            if region.controller in ("Britain", "Austria"):
                region.controller = "Prussia"
        world.invalidate_active_nations_cache()

        result = create_vassal_treaty(world, "Prussia", "Saxony")
        assert result.get("success"), result.get("message")

        event = world.pending_dispatch_events[-1]
        assert event["type"] == "diplomatic_carved_vassal_created"
        text = _format_dispatch_event_text(event["type"], event["template_vars"])
        assert "Prussia" in text
        assert "French" not in text
