"""AI-4b + AI-4c + §4.4b — third-party settlements, war-exhaustion
generalisation, and coalition de-anchoring (docs/AI_INTENT_SPEC.md §4.4,
§4.4b, §3.1a; gate record §16; landing record §17).

Pins carried here:
- Pin 17(a): a 20-turn AI-vs-AI war with no French participation produces
  a monotonically non-decreasing exhaustion series for BOTH belligerents
  (the pin that failed against master before this stage).
- Pin 17(c): the legacy fixture world's tick is byte-identical.
- Pin 19(b): a nation whose exhaustion crosses the effective_p1_threshold
  seam sues on the AI-vs-AI path; (c) an AI-vs-AI war ratifies to PEACE
  with the player's mounted dialogue untouched.
- Pin 16(b): non-player slots decay on the player's schedule; (c) a
  non-player target never instant-forms — brewing is structural; (d) the
  eclipse fixture — D3's "the player can genuinely be eclipsed" as a test.
- §16.1-8: the exclusive ruling — anti-France precedence.
"""

from pathlib import Path

import pytest

from backend.game_logic import settlement_scoring
from backend.game_logic.ai_diplomacy import effective_peace_threshold
from backend.game_logic.coalition import (
    BREWING_COUNTDOWN,
    THREAT_BREWING_MIN,
    _eclipse_candidate,
    dissolve_coalition,
    process_coalition_turn,
)
from backend.game_logic.diplomacy import declare_war, get_war_score_for
from backend.game_logic.settlement_third_party import (
    THIRD_PARTY_MIN_WAR_TURNS,
    attempt_third_party_settlement,
    build_third_party_terms,
    process_third_party_settlements,
)
from backend.models.world_state import WorldState

REPO_ROOT = Path(__file__).resolve().parents[1]
SCENARIO_PATH = (REPO_ROOT / "godot-client" / "project-sovereign"
                 / "assets" / "maps" / "europe_1805.json")


@pytest.fixture(scope="module")
def world1805():
    return WorldState.from_scenario(str(SCENARIO_PATH))


@pytest.fixture()
def world(world1805):
    return WorldState.from_dict(world1805.to_dict())


def _find_war(world, a: str, b: str):
    for war_id, war in world.war_instances.items():
        if (war.get("ended_turn") is None
                and a in (war.get("active_participants") or [])
                and b in (war.get("active_participants") or [])):
            return str(war_id), war
    return None, None


class TestPin17Exhaustion:
    def test_third_party_war_accrues_for_both_belligerents(self, world):
        """Pin 17(a) — the pin that failed against master."""
        declare_war(world, "Sweden", "Denmark")
        series = {"Sweden": [], "Denmark": []}
        for _ in range(20):
            world.current_turn = int(world.current_turn) + 1
            process_coalition_turn(world)
            for nation in series:
                series[nation].append(int(world.war_exhaustion.get(nation, 0)))
        for nation, values in series.items():
            assert values[-1] > 0, f"{nation} never accrued"
            assert all(b >= a for a, b in zip(values, values[1:])), \
                f"{nation}'s series fell during its own war: {values}"

    def test_boot_third_party_belligerents_accrue_turn_one(self, world):
        """Pin 17(b)'s data arm: the four boot third-party belligerents
        begin accruing at once (Spain and Holland against Britain,
        Bavaria and the Kingdom of Italy against Austria)."""
        world.current_turn = int(world.current_turn) + 1
        process_coalition_turn(world)
        for nation in ("Spain", "Holland", "Bavaria", "KingdomOfItaly"):
            assert int(world.war_exhaustion.get(nation, 0)) >= 8, (
                f"{nation} boots at war and must accrue on the Europe tick")

    def test_legacy_world_tick_unchanged(self):
        """Pin 17(c): the legacy/bare world keeps the France-relative
        read — an AI-vs-AI pair there never accrues from the tick."""
        bare = WorldState()
        assert getattr(bare, "sovereign_map", "legacy") != "europe"
        bare.diplomatic_states["Austria|Britain"] = "WAR"
        bare.war_exhaustion["Austria"] = 20
        before = int(bare.war_exhaustion["Austria"])
        process_coalition_turn(bare)
        after = int(bare.war_exhaustion.get("Austria", 0))
        assert after == max(0, before - 5), (
            "legacy tick must keep decaying a nation not at war with France")


class TestPeaceThresholdSeam:
    def test_seam_matches_p1_formula(self, world):
        """Pin 19(b): ONE seam — the helper reproduces P1's inline
        formula for the France pair exactly."""
        from backend.game_logic.ai_diplomacy import (
            _calculate_ticking_pressure,
            _get_personality_modifiers,
        )
        nation, player = "Austria", "France"
        world.war_exhaustion[nation] = 63
        mods = _get_personality_modifiers(nation, world)
        expected = -40 + mods["peace_threshold_delta"] + 63 // 20
        if world.is_at_war(nation, player):
            key = world._make_diplo_key(nation, player)
            expected += _calculate_ticking_pressure(nation, player, key, world)
            from backend.game_logic.agendas import get_agenda_resolve_delta
            expected += get_agenda_resolve_delta(nation, player, world)
        assert effective_peace_threshold(nation, player, world) == expected


class TestThirdPartySettlement:
    def _age_war(self, world, war, turns=THIRD_PARTY_MIN_WAR_TURNS + 1):
        war["created_turn"] = int(world.current_turn) - turns

    def test_exhausted_loser_sues_and_peace_lands(self, world):
        """Pin 19(b)+(c): the loser crosses the seam, the winner accepts
        through the standing scorer, the war ENDS — headlessly."""
        declare_war(world, "Prussia", "Hanover")
        war_id, war = _find_war(world, "Prussia", "Hanover")
        assert war_id
        self._age_war(world, war)
        # Hanover is the loser: exhausted and beaten decisively (the ≥90
        # band — a single-province minor's capital may only cede, and its
        # nation eliminate, at the total-annexation score; below it the
        # package would be a white peace).
        world.war_exhaustion["Hanover"] = 150
        world.war_scores[world._make_diplo_key("Hanover", "Prussia")] = (
            -95 if world._make_diplo_key("Hanover", "Prussia").startswith("Hanover")
            else 95)
        # The player's mounted dialogue must be untouched (pin 19c).
        world.dialogue_manager.push({
            "type": "test_sentinel", "target_nation": "Spain",
            "turn_created": int(world.current_turn), "blocking": False,
        })
        mounted_before = world.dialogue_manager.peek()
        events = process_third_party_settlements(world)
        peace = [e for e in events if e["type"] == "third_party_peace"]
        assert peace, "the exhausted loser must sue and the winner accept"
        assert world.war_instances[war_id].get("ended_turn") is not None
        assert not world.is_at_war("Prussia", "Hanover")
        assert world.get_diplomatic_state("Prussia", "Hanover") == "PEACE"
        assert world.dialogue_manager.peek() == mounted_before, \
            "pin 19(c): the player's mounted dialogue is untouchable"
        # Beat 6 named its consequences.
        assert peace[0]["consequence"]
        assert any(e.get("type") == "third_party_peace"
                   for e in world.event_log)

    def test_design_province_cedes_to_the_decisive_winner(self, world):
        """The nation-pair-general territorial term generator — a war
        fought for a want ends by taking it (§7a scene 7's shape)."""
        declare_war(world, "Prussia", "Hanover")
        war_id, war = _find_war(world, "Prussia", "Hanover")
        terms = build_third_party_terms(world, war, loser="Hanover",
                                        winner="Prussia")
        # Force the decisive band from Prussia's perspective first.
        key = world._make_diplo_key("Hanover", "Prussia")
        world.war_scores[key] = -95 if key.startswith("Hanover") else 95
        terms = build_third_party_terms(world, war, loser="Hanover",
                                        winner="Prussia")
        cessions = [t for t in terms if t.get("type") == "territory_cede"]
        assert cessions and cessions[0]["region"] == "Hanover"
        assert cessions[0]["from"] == "Hanover"
        assert cessions[0]["to"] == "Prussia"

    def test_settlement_transfers_the_design_province(self, world):
        declare_war(world, "Prussia", "Hanover")
        war_id, war = _find_war(world, "Prussia", "Hanover")
        self._age_war(world, war)
        world.war_exhaustion["Hanover"] = 150
        key = world._make_diplo_key("Hanover", "Prussia")
        world.war_scores[key] = -95 if key.startswith("Hanover") else 95
        events = process_third_party_settlements(world)
        assert any(e["type"] == "third_party_peace" for e in events)
        assert world.regions["Hanover"].controller == "Prussia"

    def test_scorer_seam_is_patchable(self, world, monkeypatch):
        """The standing test seam holds for the AI-AI arm: patching the
        module attribute intercepts the acceptor."""
        declare_war(world, "Prussia", "Hanover")
        war_id, war = _find_war(world, "Prussia", "Hanover")
        self._age_war(world, war)
        world.war_exhaustion["Hanover"] = 150
        key = world._make_diplo_key("Hanover", "Prussia")
        world.war_scores[key] = -95 if key.startswith("Hanover") else 95
        calls = {}

        def _refuse(*args, **kwargs):
            calls["hit"] = True
            return {"verdict": "reject", "score": 0, "hard_stops": ["test"],
                    "accept_threshold": 50}

        monkeypatch.setattr(settlement_scoring,
                            "calculate_common_peace_acceptance", _refuse)
        events = process_third_party_settlements(world)
        assert calls.get("hit") is True
        assert not any(e["type"] == "third_party_peace" for e in events)
        assert world.war_instances[war_id].get("ended_turn") is None

    def test_young_wars_and_player_wars_skipped(self, world):
        declare_war(world, "Prussia", "Hanover")
        war_id, war = _find_war(world, "Prussia", "Hanover")
        world.war_exhaustion["Hanover"] = 150
        key = world._make_diplo_key("Hanover", "Prussia")
        world.war_scores[key] = -95 if key.startswith("Hanover") else 95
        assert process_third_party_settlements(world) == [], \
            "a war younger than the age gate never settles"
        # France's own wars are never touched by this pass.
        france_war_id, france_war = _find_war(world, "France", "Austria")
        assert france_war_id
        self._age_war(world, france_war)
        world.war_exhaustion["Austria"] = 190
        events = process_third_party_settlements(world)
        assert france_war["ended_turn"] is None

    def test_exhausted_pair_exits_the_players_war_instance(self, world):
        """Review fix [r5 HIGH]: the 1805 boot welds all seven starting
        wars into ONE instance containing France, so the four satellite
        sub-pairs (Spain|Britain, Holland|Britain, Bavaria|Austria,
        KingdomOfItaly|Austria) had NO exit and ratcheted to exhaustion
        200 forever. A spent, stagnant, non-vassal pair now signs a white
        peace while the greater war goes on."""
        war_id, war = _find_war(world, "France", "Britain")
        assert war_id, "the boot instance contains France"
        assert "Spain" in (war.get("active_participants") or [])
        # Spain and Britain both spent; their pair old and going nowhere.
        world.war_exhaustion["Spain"] = 150
        world.war_exhaustion["Britain"] = 150
        pair_key = world._make_diplo_key("Spain", "Britain")
        meta = war.get("diplo_key_meta", {}).get(pair_key)
        assert meta is not None, "the boot pair exists in the instance"
        meta["joined_turn"] = int(world.current_turn) - 12
        world.war_scores[pair_key] = 0
        events = process_third_party_settlements(world)
        exits = [e for e in events if e["type"] == "third_party_peace"]
        assert exits and {exits[0]["proposer"], exits[0]["accepter"]} == \
            {"Spain", "Britain"}
        assert world.get_diplomatic_state("Spain", "Britain") == "PEACE"
        # The greater war is untouched: France still fights Britain.
        assert world.is_at_war("France", "Britain")
        assert war.get("ended_turn") is None
        # Spain leaves the instance once its only pair closes — its
        # exhaustion now DECAYS on the tick (the ratchet is broken).
        assert "Spain" not in (war.get("active_participants") or [])

    def test_vassal_pairs_never_exit_the_lords_war(self, world):
        """A vassal follows its lord's war — Holland (France's vassal)
        stays bound however weary."""
        war_id, war = _find_war(world, "France", "Britain")
        assert war_id
        world.war_exhaustion["Holland"] = 200
        world.war_exhaustion["Britain"] = 200
        pair_key = world._make_diplo_key("Britain", "Holland")
        meta = war.get("diplo_key_meta", {}).get(pair_key)
        if meta is None:
            pytest.skip("boot topology drift: no Britain|Holland pair")
        meta["joined_turn"] = int(world.current_turn) - 12
        world.war_scores[pair_key] = 0
        process_third_party_settlements(world)
        assert world.is_at_war("Britain", "Holland"), \
            "a vassal's pair is the lord's to end"

    def test_pair_exit_never_touches_the_players_own_pairs(self, world):
        war_id, war = _find_war(world, "France", "Britain")
        world.war_exhaustion["France"] = 200
        world.war_exhaustion["Britain"] = 200
        pair_key = world._make_diplo_key("Britain", "France")
        meta = war.get("diplo_key_meta", {}).get(pair_key)
        if meta is not None:
            meta["joined_turn"] = int(world.current_turn) - 12
        world.war_scores[pair_key] = 0
        process_third_party_settlements(world)
        assert world.is_at_war("France", "Britain")

    def test_third_party_battle_arm_accrues_for_the_loser(self, world):
        """The AI-4c battle arm (both combat copies gained it): a battle
        France is not in accrues exhaustion for the LOSER's own dead —
        exercised through the real executor pipeline."""
        import random

        from backend.commands.executor import CommandExecutor
        declare_war(world, "Prussia", "Hanover")
        executor = CommandExecutor()
        gs = {"world": world, "debug_mode": True}
        prussian = next(m for m in world.marshals.values()
                        if m.nation == "Prussia" and m.strength > 0)
        prussian.strength = 60000
        target = "Hanover"
        world.regions[target].garrison_strength = 0
        # A weak Hanoverian defender materialises for the fixture.
        from backend.models.marshal import Marshal
        defender = Marshal("Wallmoden", target, 8000, "cautious",
                           nation="Hanover")
        world.marshals["Wallmoden"] = defender
        prussian.location = world.regions[target].adjacent_regions[0]
        world._build_marshal_index()
        france_we_before = int(world.war_exhaustion.get("France", 0))
        hanover_we_before = int(world.war_exhaustion.get("Hanover", 0))
        random.seed(4242)
        executor._execute_attack(prussian, target, world, gs)
        assert int(world.war_exhaustion.get("Hanover", 0)) > hanover_we_before, \
            "the third-party loser bears its own dead"
        assert int(world.war_exhaustion.get("France", 0)) == france_we_before, \
            "France's series is untouched by a battle it is not in"

    def test_broker_ask_reaches_the_mailbox(self, world):
        """§4.2b's broker row: a court close to the table asks France."""
        declare_war(world, "Prussia", "Hanover")
        war_id, war = _find_war(world, "Prussia", "Hanover")
        self._age_war(world, war)
        # Close to the table but NOT past it: derive the band, then set
        # Hanover's score just inside it (threshold ≤ score < +10).
        world.war_exhaustion["Hanover"] = 20
        threshold = effective_peace_threshold("Hanover", "Prussia", world)
        key = world._make_diplo_key("Hanover", "Prussia")
        in_band = threshold + 3
        world.war_scores[key] = (in_band if key.startswith("Hanover")
                                 else -in_band)
        assert get_war_score_for(world, "Hanover", "Prussia") == in_band
        process_third_party_settlements(world)
        assert war.get("broker_ask_turn") is not None

    def test_forced_broker_settlement_credits_france(self, world):
        declare_war(world, "Prussia", "Hanover")
        war_id, war = _find_war(world, "Prussia", "Hanover")
        self._age_war(world, war)
        world.war_exhaustion["Hanover"] = 120
        key = world._make_diplo_key("Hanover", "Prussia")
        world.war_scores[key] = -30 if key.startswith("Hanover") else 30
        rel_key = world._make_diplo_key("France", "Prussia")
        before = int(world.nation_relations.get(rel_key, 0) or 0)
        event = attempt_third_party_settlement(
            world, war_id, war, force=True, broker="France")
        assert event is not None and event["broker"] == "France"
        after = int(world.nation_relations.get(rel_key, 0) or 0)
        assert after > before, "the broker's fee: standing with both courts"


class TestEclipseAndPrecedence:
    """Pins 16(b)-(d) + the §16.1-8 exclusive ruling."""

    def _stage_eclipse(self, world):
        """Hand Austria the bulk of France's soil so its bloc share
        exceeds France's, dissolve the boot coalition, and load its
        threat slot below instant but above brewing."""
        dissolve_coalition(world, "test_fixture")
        world.coalition_cooldown = 0
        flipped = 0
        for region in world.regions.values():
            if region.controller == "France" and flipped < 30:
                region.controller = "Austria"
                flipped += 1
        world.invalidate_active_nations_cache()
        world.threat_by_target["Austria"] = 70
        # France's own alarm sits quiet for the fixture.
        world.threat_by_target[world.player_nation] = 10
        # Courts that fear the eclipsing power (the qualifying set).
        for nation in ("Prussia", "Sweden", "Denmark"):
            world.nation_relations[
                world._make_diplo_key(nation, "Austria")] = -30

    def test_eclipse_candidate_requires_share_dominance(self, world):
        world.threat_by_target["Austria"] = 70
        assert _eclipse_candidate(world) is None, \
            "D3: no eclipse while France's bloc leads"

    def test_nonplayer_decay_on_players_schedule(self, world):
        """Pin 16(b): a slot whose sources stop returns toward 0."""
        world.threat_by_target["Sweden"] = 12
        before = 12
        world.current_turn = int(world.current_turn) + 1
        process_coalition_turn(world)
        after = int(world.threat_by_target.get("Sweden", 0))
        assert after < before

    def test_eclipse_brews_never_instant_and_forms(self, world):
        """Pins 16(c)+(d): the eclipse coalition always brews ≥1 turn —
        even ABOVE the instant threshold — then forms against the
        eclipsing power while France's own slot is unmoved."""
        self._stage_eclipse(world)
        world.threat_by_target["Austria"] = 95  # above THREAT_INSTANT_MIN
        france_before = int(world.threat_level)
        world.current_turn = int(world.current_turn) + 1
        process_coalition_turn(world)
        assert world.active_coalition is None, "pin 16(c): never instant"
        brewing = world.coalition_brewing
        assert brewing and brewing.get("target_nation") == "Austria"
        assert "France" not in (brewing.get("qualifying_nations") or []), \
            "the player is never auto-conscripted"
        for _ in range(BREWING_COUNTDOWN + 1):
            if world.active_coalition:
                break
            world.current_turn = int(world.current_turn) + 1
            # Hold the slot above the cancel line against ambient decay.
            world.threat_by_target["Austria"] = max(
                int(world.threat_by_target.get("Austria", 0)), 65)
            process_coalition_turn(world)
        coalition = world.active_coalition
        assert coalition and coalition.get("target_nation") == "Austria"
        assert "France" not in (coalition.get("members") or [])
        for member in coalition.get("members") or []:
            assert world.is_at_war(member, "Austria")
        assert int(world.threat_level) <= france_before + 1, \
            "pin 16(d): France's own slot is unmoved by the eclipse"

    def test_anti_france_precedence_dissolves_the_eclipse(self, world):
        """§16.1-8: the anti-France coalition always wins — an eclipse
        coalition dissolves the turn France's alarm crosses brewing."""
        self._stage_eclipse(world)
        world.threat_by_target["Austria"] = 95
        world.current_turn = int(world.current_turn) + 1
        process_coalition_turn(world)
        for _ in range(BREWING_COUNTDOWN + 1):
            if world.active_coalition:
                break
            world.current_turn = int(world.current_turn) + 1
            world.threat_by_target["Austria"] = max(
                int(world.threat_by_target.get("Austria", 0)), 65)
            process_coalition_turn(world)
        assert world.active_coalition is not None
        world.threat_by_target[world.player_nation] = THREAT_BREWING_MIN + 5
        world.current_turn = int(world.current_turn) + 1
        process_coalition_turn(world)
        active = world.active_coalition
        assert (active is None
                or (active.get("target_nation") or world.player_nation)
                == world.player_nation), \
            "the eclipse coalition must yield to the anti-France process"
        assert any(e.get("type") == "coalition_dissolved_for_france"
                   for e in world.event_log)


class TestLegacyCoalitionShape:
    def test_legacy_record_without_target_reads_player(self, world):
        """§4.4b: a legacy active_coalition dict (no target_nation key)
        is judged against the player, byte-identically."""
        from backend.game_logic.coalition import check_dissolution
        world.active_coalition = {
            "name": "The Test Coalition", "leader": "Austria",
            "members": ["Austria", "Britain"], "formed_turn": 1,
            "strategic_posture": "defensive",
        }
        world.threat_by_target[world.player_nation] = 50
        # Both members boot at war with France → no dissolution reason.
        assert check_dissolution(world) is None
