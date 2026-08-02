"""NV-2 — Crossings & the fleet action (docs/NAVAL_SPEC.md §11).

THE HEADLINE (anchor A5): a hostile army can NEVER walk the Channel crossing
below ratio — Spain besieging London on turn 5 (the August-1 re-measure's
rank-2 believability defect) becomes structurally impossible, while
Britain's own boot descents still pass on ratio (H7).

Plus: the gate at every movement seam (player move, cavalry 2-hop, attack,
reinforcement, AI candidate filters, forced retreat with the Corunna
clause), the expedition verb with its quoted-and-applied odds (A3), and
the §4.4 fleet-action resolver.
"""

from pathlib import Path

import pytest

from backend.commands.executor import CommandExecutor
from backend.game_logic import naval
from backend.models.world_state import WorldState

SCENARIO_PATH = (
    Path(__file__).resolve().parents[1]
    / "godot-client" / "project-sovereign" / "assets" / "maps"
    / "europe_1805.json"
)


@pytest.fixture
def world():
    return WorldState.from_scenario(str(SCENARIO_PATH))


@pytest.fixture
def executor():
    return CommandExecutor()


def _game_state(world):
    return {"world": world}


def _place(world, marshal_name, region):
    marshal = world.get_marshal(marshal_name)
    marshal.location = region
    world._build_marshal_index()
    return marshal


# ═══════════════════════════════════════════════════════════════════════════
# A5 — THE HEADLINE
# ═══════════════════════════════════════════════════════════════════════════

class TestChannelGateHeadline:
    def test_spain_can_never_walk_to_london(self, world):
        """The August-1 absurdity, dead: Spain's pooled ~31 effective vs
        the Royal Navy's 100 → SHUT, flat, no dice."""
        verdict = naval.crossing_check(world, "Spain", "Normandy", "London")
        assert verdict["allowed"] is False
        assert verdict["verdict"] == "shut"
        assert verdict["coverer"] == "Britain"
        # §2.3: the refusal names the gap and the real answers.
        assert "Royal Navy" in verdict["message"]
        assert "sail" in verdict["message"]

    def test_france_cannot_walk_to_london_either(self, world):
        assert not naval.crossing_check(
            world, "France", "Normandy", "London")["allowed"]

    def test_britain_commands_the_water_but_may_not_march_ashore(self, world):
        """NV-4 THE HOST RULE — pin CONSCIOUSLY FLIPPED (August 2, 2026).

        Was: `test_britains_boot_descents_still_pass` asserted allowed=True
        on London→Flanders, i.e. the Royal Navy's superiority bought a free,
        uncapped, unopposed march onto French home soil. That is the
        August-2 probe's measured defect (Moore walked 30,000 men ashore —
        TWICE the transports' 15,000 cap — and was in Berry by turn 2), and
        it made `naval_expedition` a strictly dominated verb.

        Now: the ratio arm still passes — Britain DOES command that water,
        and the numbers below prove the flip is the host rule and not a
        naval reversal — but the far shore is enemy country, so the march
        is refused and the expedition is named as the door."""
        verdict = naval.crossing_check(world, "Britain", "London", "Normandy")
        # The water is still Britain's — the ratio is untouched.
        assert verdict["ratio"] >= naval.CROSSING_RATIO
        # The shore is not.
        assert verdict["allowed"] is False
        assert verdict["verdict"] == "landing"
        assert "transports" in verdict["message"]
        assert f"{naval.EXPEDITION_MAX_TROOPS:,}" in verdict["message"]

    def test_the_descent_beach_is_normandy(self, world):
        """User-directed (August 2, 2026): a British landing comes ashore on
        the NORMAN COAST, not through the Low Countries into the French
        interior. The registry gained London↔Normandy — the SHORT Channel
        crossing (111px against Flanders's 352px, one of the map's longest
        links) and the historic descent beach.

        NV-4 amends the arrival, not the beach: Normandy is still where
        Britain comes ashore, but it comes ashore by EXPEDITION now."""
        assert naval.is_sea_link(world, "London", "Normandy")
        verdict = naval.crossing_check(world, "Britain", "London", "Normandy")
        assert verdict["ratio"] >= naval.CROSSING_RATIO
        assert verdict["verdict"] == "landing"
        # ...and the expedition really is open on that beach (the door the
        # refusal names is a door that exists — §10's standing rule).
        odds = naval.expedition_slip_odds(
            world, "Britain", "Normandy", naval.EXPEDITION_MAX_TROOPS)
        assert odds["odds"] > 0

    def test_a_host_shore_is_never_gated(self, world):
        """The Portugal case (Mondego Bay 1808) — the whole point of the
        host rule. Britain is NOT at war with Portugal, so a Portuguese
        shore is a host, not an objective: nothing about the naval layer
        stands between a British army and a friendly port."""
        assert not world.is_at_war("Britain", "Portugal")
        assert naval.is_hostile_shore(world, "Britain", "Normandy") is True
        assert naval.is_hostile_shore(world, "Britain", "Lisbon") is False
        assert naval.is_hostile_shore(world, "Britain", "London") is False

    def test_beating_the_covering_fleet_opens_the_shore(self, world):
        """The rule's own escape hatch, and the reason it is not a wall:
        uncontested water is an administrative ferry. Sink the fleet that
        covers the passage and the army marches ashore unlimited."""
        assert naval.crossing_check(
            world, "Britain", "London", "Normandy")["verdict"] == "landing"
        naval.get_fleet(world, "France")["ships"] = 0
        after = naval.crossing_check(world, "Britain", "London", "Normandy")
        assert after["allowed"] is True
        assert after["verdict"] == "open"

    def test_the_window_waives_the_host_rule(self, world):
        """§5.3: drawing the enemy off station IS the moment the army
        crosses — the Descent would be unwinnable if the host rule outlived
        the window it was designed around."""
        naval.get_fleet(world, "France")["window_turns"] = 2
        verdict = naval.crossing_check(world, "France", "Normandy", "London")
        assert naval.is_hostile_shore(world, "France", "London") is True
        # Whatever the ratio says, the host rule is not what decides it.
        assert verdict["verdict"] != "landing"

    def test_the_norman_beach_is_gated_the_other_way(self, world):
        """A5 holds on the NEW crossing too — the beach is a door Britain
        owns, not a two-way street. France cannot walk it to London."""
        verdict = naval.crossing_check(world, "France", "Normandy", "London")
        assert verdict["allowed"] is False
        assert verdict["coverer"] == "Britain"

    def test_the_beach_is_never_a_free_walk_in(self, world):
        """The DEF-6 rule applied to the new beachhead: a Channel-coast
        depot garrisons Normandy exactly as it does Flanders — which matters
        doubly here, Normandy being one march from Paris."""
        assert world.regions["Normandy"].garrison_strength == 12000
        assert world.regions["Flanders"].garrison_strength == 12000

    def test_uncontested_links_stay_free(self, world):
        """The Danish straits at peace: no hostile coverage, no change."""
        assert naval.crossing_check(
            world, "Denmark", "Copenhagen", "Scania")["verdict"] == "open"
        # France's own Mediterranean link vs nobody covering it:
        assert naval.crossing_check(
            world, "Sardinia", "Cagliari", "Rome")["allowed"]

    def test_land_borders_are_never_gated(self, world):
        assert naval.crossing_check(
            world, "Spain", "Paris", "Flanders")["verdict"] == "open"

    def test_executor_refuses_the_walk(self, world, executor):
        """The seam itself: a Spanish marshal ordered across the Channel is
        refused with the naval message + the PF-8 structured flag."""
        marshal = _place(world, "Gravina", "Normandy") if world.get_marshal(
            "Gravina") else None
        if marshal is None:
            # Use any Spanish marshal from the authored roster.
            spanish = world.get_marshals_by_nation("Spain")
            assert spanish, "scenario authors a Spanish marshal"
            marshal = _place(world, spanish[0].name, "Normandy")
        result = executor._movement._execute_move(
            marshal, "London", world, _game_state(world))
        assert result["success"] is False
        assert result.get("blocked_naval") == "Britain"

    def test_the_attack_arm_is_gated_too(self, world, executor):
        """'A blockade that stops MOVE but not ATTACK is not a blockade' —
        the amphibious assault across a covered link is refused."""
        spanish = world.get_marshals_by_nation("Spain")
        marshal = _place(world, spanish[0].name, "Normandy")
        result = executor.execute(
            {"command": {"marshal": marshal.name, "action": "attack",
                         "target": "London", "type": "specific",
                         "_acting_nation": "Spain"}},
            _game_state(world))
        assert result["success"] is False
        assert result.get("blocked_naval") == "Britain"

    def test_reinforcement_is_interdicted(self, world, executor):
        """A corps cannot muster INTO a battle across a covered link —
        control arm: sink the RN and the SAME muster becomes eligible, so
        the refusal is isolated to the naval rule."""
        marshal = _place(world, "Ney", "Normandy")
        primary = _place(world, "Davout", "London")
        gated = executor._combat._is_reinforcement_eligible(
            marshal, primary, "London", "France", world)
        world.fleets["Britain"]["ships"] = 0
        ungated = executor._combat._is_reinforcement_eligible(
            marshal, primary, "London", "France", world)
        assert gated is False
        assert ungated is True


class TestAICandidateFilter:
    def test_origin_aware_filter_rejects_the_crossing(self, world):
        from backend.ai.enemy_ai import EnemyAI
        ai = EnemyAI(CommandExecutor())
        assert ai._can_ai_move_to(world, "Spain", "London",
                                  origin="Normandy") is False
        # Destination-only calls (no origin) keep their old answer.
        assert ai._can_ai_move_to(world, "Spain", "London") is True

    def test_britain_the_superior_may_not_march_ashore(self, world):
        """NV-4 — pin CONSCIOUSLY FLIPPED (August 2, 2026), the AI half of
        the host rule. Was: the superior fleet's candidate scan accepted a
        French beach, which is how the 16-turn ambient probe put Moore in
        Berry by turn 2 and Paget in Gelderland by turn 16. The AI reads
        the SAME predicate the player does (GR5), so it stops offering
        itself an opposed landing as an ordinary march.

        Control arm: the identical scan onto a HOST shore still passes, so
        the flip is the host rule and not a broken candidate filter."""
        from backend.ai.enemy_ai import EnemyAI
        ai = EnemyAI(CommandExecutor())
        assert ai._can_ai_move_to(world, "Britain", "Normandy",
                                  origin="London") is False
        # Britain's own Irish crossing — its own soil, never gated.
        assert ai._can_ai_move_to(world, "Britain", "Ulster",
                                  origin="Highlands") is True


class TestRetreatArms:
    def test_forced_retreat_prefers_land(self, world):
        """get_safe_retreat_destination demotes a covered crossing."""
        french = world.get_marshals_by_nation("France")
        marshal = _place(world, french[0].name, "Normandy")
        dest = world.get_safe_retreat_destination(marshal.name)
        assert dest != "London"

    def test_the_corunna_clause(self, world):
        """When every land exit is enemy-held, the army takes to the boats
        rather than break in place — evacuation under fire is real."""
        british = world.get_marshals_by_nation("Britain")
        marshal = _place(world, british[0].name, "Normandy")
        # Make every Normandy land neighbour a war-held French province
        # (they are — France holds them and is at war with Britain), so the
        # only non-war exit is the London crossing... which France covers.
        dest = world.get_safe_retreat_destination(marshal.name)
        assert dest == "London"  # the sea exit, Corunna-style


# ═══════════════════════════════════════════════════════════════════════════
# THE EXPEDITION (§4.3 — anchors A3)
# ═══════════════════════════════════════════════════════════════════════════

class TestExpeditionOdds:
    def test_a3_boot_ireland_band(self, world):
        """Bantry scale: a 12,000-man Irish run lands 55–65 at boot."""
        quote = naval.expedition_slip_odds(world, "France", "Munster", 12000)
        assert 55 <= quote["odds"] <= 65, quote
        assert quote["mode"] == "open_water"

    def test_a3_channel_run_is_desperate(self, world):
        """A 15,000-man Channel run with no window: ≤15."""
        quote = naval.expedition_slip_odds(world, "France", "London", 15000)
        assert quote["odds"] <= 15, quote
        assert quote["mode"] == "link"

    def test_no_hostile_fleet_means_no_gamble(self, world):
        quote = naval.expedition_slip_odds(world, "Denmark", "Scania", 10000)
        assert quote["odds"] == 100

    def test_window_bonus(self, world):
        base = naval.expedition_slip_odds(world, "France", "Munster", 12000)
        world.fleets["France"]["window_turns"] = 2
        boosted = naval.expedition_slip_odds(world, "France", "Munster", 12000)
        assert boosted["odds"] > base["odds"]


class TestExpeditionVerb:
    def test_expedition_parses(self, world):
        from backend.ai.llm_client import LLMClient
        client = LLMClient()
        gs = {"world": world,
              "marshals": {m.name: m for m in
                           world.get_marshals_by_nation("France")}}
        result = client._parse_with_mock(
            "land Soult in Munster with 12,000 men", gs)
        assert result.action == "naval_expedition"

    def test_quote_then_confirm(self, world, executor):
        """First call quotes the odds (shown = applied) on the EXISTING
        clarification channel; nothing moves until the confirm."""
        marshal = _place(world, "Soult", "Brittany")
        marshal.strength = 12000
        result = executor._naval._execute_naval_expedition(
            {"marshal": "Soult", "action": "naval_expedition",
             "target": "Munster",
             "raw_command": "land Soult in Munster"}, _game_state(world))
        assert result["success"]
        assert result["state"] == "awaiting_clarification"
        assert result["naval_confirm"] is True
        quote = naval.expedition_slip_odds(world, "France", "Munster", 12000)
        assert str(quote["odds"]) in result["message"]  # shown = applied
        assert marshal.location == "Brittany"  # nothing moved
        # The option reissues a full deterministic command.
        assert any("confirmed" in (o.get("command") or "")
                   for o in result["options"])

    def test_oversize_corps_refused_naming_the_cap(self, world, executor):
        marshal = _place(world, "Soult", "Brittany")
        marshal.strength = 22000
        result = executor._naval._execute_naval_expedition(
            {"marshal": "Soult", "action": "naval_expedition",
             "target": "Munster",
             "raw_command": "land Soult in Munster"}, _game_state(world))
        assert not result["success"]
        assert "15,000" in result["message"]
        assert "garrison" in result["message"]  # the real answer named

    def test_home_embarkation_needs_a_yard(self, world, executor):
        marshal = _place(world, "Soult", "Paris")
        marshal.strength = 12000
        result = executor._naval._execute_naval_expedition(
            {"marshal": "Soult", "action": "naval_expedition",
             "target": "Munster",
             "raw_command": "land Soult in Munster"}, _game_state(world))
        assert not result["success"]
        assert "dockyard" in result["message"]

    def test_inland_target_refused(self, world, executor):
        marshal = _place(world, "Soult", "Brittany")
        marshal.strength = 12000
        result = executor._naval._execute_naval_expedition(
            {"marshal": "Soult", "action": "naval_expedition",
             "target": "Paris",
             "raw_command": "land Soult in Paris"}, _game_state(world))
        assert not result["success"]

    def test_adjacent_by_land_refused(self, world, executor):
        marshal = _place(world, "Soult", "Brittany")
        marshal.strength = 12000
        result = executor._naval._execute_naval_expedition(
            {"marshal": "Soult", "action": "naval_expedition",
             "target": "Anjou",
             "raw_command": "land Soult in Anjou"}, _game_state(world))
        assert not result["success"]
        assert "march" in result["message"]

    def test_confirmed_run_resolves_deterministically(self, world, executor):
        """Same seed, same Trafalgar: two identical worlds resolve the
        same confirmed expedition identically."""
        outcomes = []
        for _ in range(2):
            w = WorldState.from_scenario(str(SCENARIO_PATH))
            marshal = _place(w, "Soult", "Brittany")
            marshal.strength = 12000
            ex = CommandExecutor()
            result = ex._naval._execute_naval_expedition(
                {"marshal": "Soult", "action": "naval_expedition",
                 "target": "Munster",
                 "raw_command": "land Soult in Munster confirmed"},
                _game_state(w))
            outcomes.append((result["landed"], result["odds"],
                             w.get_marshal("Soult").location,
                             w.get_marshal("Soult").strength))
        assert outcomes[0] == outcomes[1]

    def test_unopposed_landing_lands_and_captures(self, world, executor):
        """With no hostile fleet the sailing is administrative — and the
        landing falls through the SAME capture pipeline every march uses
        (§4.3: everything downstream is the existing land game)."""
        world.fleets["Britain"]["ships"] = 0  # the RN is gone
        marshal = _place(world, "Soult", "Brittany")
        marshal.strength = 12000
        result = executor._naval._execute_naval_expedition(
            {"marshal": "Soult", "action": "naval_expedition",
             "target": "Munster",
             "raw_command": "land Soult in Munster confirmed"},
            _game_state(world))
        assert result["success"] and result["landed"]
        assert world.get_marshal("Soult").location == "Munster"
        captured = world.regions["Munster"].controller == "France"
        assert captured or result.get("capture_choice") is not None


# ═══════════════════════════════════════════════════════════════════════════
# THE FLEET ACTION (§4.4 — Trafalgar in one resolver)
# ═══════════════════════════════════════════════════════════════════════════

class TestFleetAction:
    def test_decisive_action_is_a_trafalgar(self, world):
        """Britain (100 eff) vs France's pool (~54): ratio ≥ 1.5 →
        decisive — extra losses, the beat, loser WE +8."""
        we0 = world.war_exhaustion.get("France", 0)
        fr_ships0 = world.fleets["France"]["ships"]
        sp_ships0 = world.fleets["Spain"]["ships"]
        result = naval.resolve_fleet_action(world, "France", "Britain",
                                            context="diversion")
        assert result["winner"] == "Britain"
        assert result["decisive"] is True
        assert world.fleets["France"]["ships"] < fr_ships0
        # H6: the pooled ally bleeds too — Trafalgar gutted Spain.
        assert world.fleets["Spain"]["ships"] < sp_ships0
        assert world.war_exhaustion.get("France", 0) == we0 + naval.FLEET_ACTION_LOSER_WE
        trafalgars = [e for e in world.event_log if e.get("type") == "trafalgar"]
        assert len(trafalgars) == 1

    def test_winner_pays_a_light_bill(self, world):
        gb0 = world.fleets["Britain"]["ships"]
        naval.resolve_fleet_action(world, "France", "Britain")
        lost = gb0 - world.fleets["Britain"]["ships"]
        assert 0 < lost <= int(gb0 * 0.10)

    def test_near_parity_is_indecisive(self, world):
        world.fleets["France"]["ships"] = 95
        world.fleets["France"]["readiness"] = 100
        # Strip the pools to make the ratio clean.
        for ally in ("Spain", "Holland", "Russia"):
            world.fleets[ally]["ships"] = 0
        result = naval.resolve_fleet_action(world, "France", "Britain")
        assert result["decisive"] is False
        assert not [e for e in world.event_log if e.get("type") == "trafalgar"]
        assert [e for e in world.event_log if e.get("type") == "fleet_action"]


class TestAITurnbackLine:
    def test_refused_ai_move_logs_the_ordinary_line(self, world):
        """§9: a notable AI turn-back renders as a campaign-log line,
        never a popup."""
        from backend.ai.enemy_ai import EnemyAI
        executor = CommandExecutor()
        ai = EnemyAI(executor)
        spanish = world.get_marshals_by_nation("Spain")
        marshal = _place(world, spanish[0].name, "Normandy")
        ai._execute_action(
            {"marshal": marshal.name, "action": "move", "target": "London"},
            _game_state(world))
        lines = [e for e in world.event_log if e.get("type") == "naval_turnback"]
        assert len(lines) == 1
        assert lines[0]["coverer"] == "Britain"
