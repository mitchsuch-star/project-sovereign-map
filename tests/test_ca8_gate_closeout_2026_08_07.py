"""CA8 CLOSE-OUT GATES — August 7, 2026 (user-delegated).

Gate record = docs/audits/CREATIVE_AUDIT_2026_08_04.md §10 (authoritative).
Four gates held and built in one session:

  §10.1 CA8-D2  — leverage keys to the WAR (CA8-3 / CA8-24), and a cession
                  requires actually LOSING (CA8-27).
  §10.2 CA8-D6  — the briefing may lead with a victory (CA8-26): four
                  success classes, wound-beats-triumph-at-equal-scale.
  §10.3 CA8-17  — Voice Bible §16.1a amended: spoken-blocker vocabulary +
                  per-register table framings (labels in tables, phrases
                  in mouths).
  §10.4 CA8-D4  — hegemony_pressure escapes the fear monoculture: a third
                  non-fear variant in every one of the 24 banks (CA8-16
                  bounded build; full roster authoring stays DEF-1).
  §10.5 CA8-19  — garrison assault stays its own resolver BY DESIGN; the
                  repulsed-attacker glory divergence is CANONIZED; the
                  garrison-diorama half is homed at the Battle Gallery gate.
"""

import inspect

import pytest

from backend.game_logic import dispatch as dispatch_mod
from backend.game_logic.diplomacy import (
    calculate_side_war_score,
    calculate_war_score,
    get_side_war_score_for,
)
from backend.models.world_state import WorldState
from tests.conftest import MarshalFactory, WorldFactory


# ═══════════════════════════════════════════════════════════════════════
# §10.1 CA8-D2 — the war-level score single source
# ═══════════════════════════════════════════════════════════════════════

class TestSideWarScoreSingleSource:
    """`calculate_side_war_score` must reduce byte-identically to the pair
    helper for one opponent — every bilateral war untouched by construction."""

    def _world_with_battles(self):
        world = WorldFactory.with_marshals(
            [MarshalFactory.infantry(name="Ney", location="Paris")],
            current_turn=10)
        key_a = world._make_diplo_key("France", "Austria")
        key_p = world._make_diplo_key("France", "Prussia")
        world.battle_records = {
            key_a: [{"winner": "France", "turn": 9, "location": "Bohemia"},
                    {"winner": "France", "turn": 10, "location": "Bohemia"}],
            key_p: [{"winner": "Prussia", "turn": 10, "location": "Berlin"}],
        }
        world.decisive_battles = {
            key_a: [{"winner": "France", "turn": 9}],
        }
        return world

    def test_single_opponent_reduces_to_pair_score(self):
        world = self._world_with_battles()
        for opponent in ("Austria", "Prussia"):
            pair = calculate_war_score("France", opponent, world,
                                       return_components=True)
            side = calculate_side_war_score("France", [opponent], world,
                                            return_components=True)
            assert side == pair, (opponent, side, pair)

    def test_multi_opponent_sums_components(self):
        world = self._world_with_battles()
        side = calculate_side_war_score("France", ["Austria", "Prussia"],
                                        world, return_components=True)
        a = calculate_war_score("France", "Austria", world,
                                return_components=True)
        p = calculate_war_score("France", "Prussia", world,
                                return_components=True)
        assert side["battles"] == a["battles"] + p["battles"]
        assert side["decisive"] == a["decisive"] + p["decisive"]

    def test_component_caps_reapply_on_the_sum(self):
        """Each component re-clamps at its own pair cap — a two-front
        battle streak cannot exceed the ±30 battle cap."""
        world = self._world_with_battles()
        key_a = world._make_diplo_key("France", "Austria")
        key_p = world._make_diplo_key("France", "Prussia")
        world.battle_records[key_a] = [
            {"winner": "France", "turn": 10, "location": "Bohemia"}
            for _ in range(12)]
        world.battle_records[key_p] = [
            {"winner": "France", "turn": 10, "location": "Berlin"}
            for _ in range(12)]
        side = calculate_side_war_score("France", ["Austria", "Prussia"],
                                        world, return_components=True)
        assert side["battles"] == 30, side

    def test_self_and_empty_opponents_are_ignored(self):
        world = self._world_with_battles()
        assert calculate_side_war_score("France", [], world) == 0
        assert calculate_side_war_score(
            "France", ["France", ""], world) == 0


class TestGetSideWarScoreFor:
    """The instance-resolving wrapper: war-level when an instance covers the
    pair, plain pair score otherwise."""

    def _world(self, with_instance=True):
        world = WorldFactory.with_marshals(
            [MarshalFactory.infantry(name="Ney", location="Paris")],
            current_turn=10)
        key_a = world._make_diplo_key("France", "Austria")
        # STORED pair score — the source the score-consuming seams read.
        world.war_scores = {key_a: (22 if key_a.split("|")[0] == "France"
                                    else -22)}
        if with_instance:
            world.war_instances = {"war_1": {
                "attackers": ["France"],
                "defenders": ["Prussia", "Austria"],
                "side_by_nation": {"France": "attackers",
                                   "Prussia": "defenders",
                                   "Austria": "defenders"},
                "active_participants": ["France", "Prussia", "Austria"],
                "attacker_leader": "France",
                "defender_leader": "Prussia",
                "created_turn": 2,
                "ended_turn": None,
                "active_diplo_keys": [
                    world._make_diplo_key("France", "Prussia"),
                    world._make_diplo_key("France", "Austria"),
                ],
            }}
            world._war_instance_indexes_dirty = True
        return world

    def test_reads_the_war_when_an_instance_covers_the_pair(self):
        """France vs the Prussia-led side: the stored Austria score presses
        on the Prussia pair too — the CA8-3 defect inverted."""
        world = self._world(with_instance=True)
        from backend.game_logic.diplomacy import get_war_score_for
        assert get_war_score_for(world, "France", "Prussia") == 0
        vs_leader = get_side_war_score_for(world, "France", "Prussia")
        assert vs_leader == 22, vs_leader

    def test_falls_back_to_pair_without_an_instance(self):
        world = self._world(with_instance=False)
        world.war_scores[world._make_diplo_key("France", "Prussia")] = -12
        got = get_side_war_score_for(world, "France", "Prussia")
        assert got == -12

    def test_an_ended_instance_does_not_count(self):
        world = self._world(with_instance=True)
        world.war_instances["war_1"]["ended_turn"] = 8
        world._war_instance_indexes_dirty = True
        assert get_side_war_score_for(world, "France", "Prussia") == 0

    def test_a_bilateral_instance_keeps_the_stored_pair_read(self):
        """The consumer rule (§10.1): a two-court war reads the STORED pair
        score byte-identically — only a multi-party war reads the live
        aggregate. Five pre-existing bilateral offer pins depend on it."""
        world = self._world(with_instance=True)
        inst = world.war_instances["war_1"]
        inst["defenders"] = ["Prussia"]
        inst["side_by_nation"] = {"France": "attackers",
                                  "Prussia": "defenders"}
        inst["active_participants"] = ["France", "Prussia"]
        world._war_instance_indexes_dirty = True
        world.war_scores = {world._make_diplo_key("France", "Prussia"): -17}
        # The stored −17 wins even though the live components would say 0.
        assert get_side_war_score_for(world, "France", "Prussia") == -17


class TestWarRoomReadsTheWar:
    """CA8-24: the collapsed multi-participant HUD row reports the WAR —
    score, battles, duration — not the leader pair."""

    def _coalition_world(self):
        world = WorldState()
        for m in world.marshals.values():
            if m.nation == "France":
                m.location = "Bordeaux"
        key_p = world._make_diplo_key("France", "Prussia")
        key_a = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[key_p] = "WAR"
        world.diplomatic_states[key_a] = "WAR"
        world.war_start_turns = {key_p: 8, key_a: 2}
        world.current_turn = 12
        world.battle_records = {
            key_a: [{"winner": "France", "turn": 11, "location": "Bohemia",
                     "battle_name": "First Battle of Bohemia"}
                    for _ in range(3)],
        }
        world.decisive_battles = {key_a: [{"winner": "France", "turn": 11}]}
        world.war_instances = {"war_9": {
            "attackers": ["France"],
            "defenders": ["Prussia", "Austria"],
            "side_by_nation": {"France": "attackers",
                               "Prussia": "defenders",
                               "Austria": "defenders"},
            "active_participants": ["France", "Prussia", "Austria"],
            "attacker_leader": "France",
            "defender_leader": "Prussia",
            "created_turn": 2,
            "ended_turn": None,
            "active_diplo_keys": [key_p, key_a],
        }}
        world._war_instance_indexes_dirty = True
        return world

    def _collapsed_row(self, world):
        from backend.game_logic.war_status import build_active_wars
        wars = build_active_wars(world).get("wars", [])
        rows = [w for w in wars if w.get("is_multi_participant_war")]
        assert rows, wars
        return rows[0]

    def test_score_and_battles_are_war_level(self):
        """The Prussia-led row used to read the France|Prussia pair: +0,
        0 battles. It now carries the Austria front's fighting."""
        row = self._collapsed_row(self._coalition_world())
        assert row["battles_fought"] == 3, row
        assert row["decisive_won"] == 1, row
        assert row["war_score"] > 0, row
        assert row["breakdown"]["battles"] > 0, row
        assert len(row["recent_battles"]) == 3

    def test_duration_is_the_oldest_front(self):
        row = self._collapsed_row(self._coalition_world())
        assert row["duration"] == 10, row  # turn 12 − created 2


class TestOfferProducerReadsTheWar:
    """CA8-3: the incoming settlement offer's direction follows the war
    France is actually fighting, not the leader pair."""

    def _emit(self, world, war):
        from backend.game_logic.ai_diplomacy import (
            _emit_settlement_offer_for_war,
        )
        return _emit_settlement_offer_for_war(
            world, "war_1", war, player="France",
            current_turn=int(world.current_turn), pending=[], cooldowns={})

    def _world_and_war(self, decisive_vs_austria=True):
        world = WorldFactory.with_marshals(
            [MarshalFactory.infantry(name="Ney", location="Paris")],
            current_turn=15)
        key_a = world._make_diplo_key("France", "Austria")
        if decisive_vs_austria:
            world.war_scores = {
                key_a: (50 if key_a.split("|")[0] == "France" else -50)}
        world.nation_gold["Prussia"] = 3000
        world.nation_gold["Austria"] = 3000
        war = {
            "side_by_nation": {"France": "attackers",
                               "Prussia": "defenders",
                               "Austria": "defenders"},
            "attacker_leader": "France",
            "defender_leader": "Prussia",
            "created_turn": 5,
        }
        return world, war

    def test_victories_over_one_court_press_on_the_leaders_table(self):
        """Ten victories over Austria: the Prussia-led offer now arrives as
        the LOSING side's offer — the proposer pays France."""
        world, war = self._world_and_war(decisive_vs_austria=True)
        offer = self._emit(world, war)
        terms = offer["settlement_terms"]
        indemnities = [t for t in terms if t.get("type") == "gold_indemnity"]
        assert indemnities, terms
        assert indemnities[0]["to"] == "France", terms

    def test_without_the_war_level_read_this_was_a_white_peace(self):
        """FALSIFIABLE CONTROL: the same board scored pairwise vs the leader
        is 0 — the audit's measured white peace."""
        from backend.game_logic.diplomacy import get_war_score_for
        world, war = self._world_and_war(decisive_vs_austria=True)
        assert get_war_score_for(world, "France", "Prussia") == 0
        world2, war2 = self._world_and_war(decisive_vs_austria=False)
        offer = self._emit(world2, war2)
        terms = offer["settlement_terms"]
        assert not any(t.get("type") == "gold_indemnity" for t in terms), terms


class TestCessionRequiresLosing:
    """CA8-27: territory cession requires war_score < -20 STRICTLY — deep
    hostility alone keeps only the gold sweetener."""

    def _terms(self, world, target="Austria"):
        from backend.game_logic.diplomatic_templates import _build_base_terms
        return _build_base_terms(target, "peace", world, deterministic=True)

    def _world(self, war_score=0, relation=-80):
        world = WorldFactory.with_marshals(
            [MarshalFactory.infantry(name="Ney", location="Paris")],
            current_turn=10)
        key = world._make_diplo_key("France", "Austria")
        world.nation_relations[key] = relation
        world.war_scores = {key: (war_score
                                  if key.split("|")[0] == "France"
                                  else -war_score)}
        return world

    def test_hostile_but_not_losing_never_cedes(self):
        """The audit's live case: relation −80, war score +2 — Talleyrand
        drafted 'France cedes Nivernais'. Never again."""
        terms = self._terms(self._world(war_score=2, relation=-80))
        cedes = [s for s in terms["sweeteners"]
                 if s.get("type") == "territory_cede"]
        assert cedes == [], terms["sweeteners"]

    def test_hostile_gold_sweetener_survives(self):
        terms = self._terms(self._world(war_score=2, relation=-80))
        golds = [s for s in terms["sweeteners"]
                 if s.get("type") == "gold_per_turn"]
        assert golds, terms["sweeteners"]

    def test_actually_losing_still_cedes(self):
        """FALSIFIABLE NEGATIVE: the losing branch is unchanged."""
        terms = self._terms(self._world(war_score=-35, relation=-80))
        cedes = [s for s in terms["sweeteners"]
                 if s.get("type") == "territory_cede"]
        assert cedes, terms["sweeteners"]

    def test_winning_demands_gold(self):
        terms = self._terms(self._world(war_score=40, relation=-80))
        assert any(d.get("type") == "gold_per_turn"
                   for d in terms["demands"]), terms


# ═══════════════════════════════════════════════════════════════════════
# §10.2 CA8-D6 — the briefing may lead with a victory
# ═══════════════════════════════════════════════════════════════════════

class TestSuccessHeadlines:

    def _world(self, turn=10):
        world = WorldFactory.with_marshals(
            [MarshalFactory.infantry(name="Ney", location="Bohemia",
                                     strength=30000)],
            current_turn=turn)
        world.event_log = []
        key = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[key] = "WAR"
        return world

    def _capture(self, w, region, prev="Austria", turn=None):
        w.event_log.append({
            "type": "region_captured", "region": region,
            "captured_by": "France", "captured_from": prev,
            "turn": turn if turn is not None else w.current_turn,
        })

    def test_a_conquest_finally_leads_the_dispatch(self):
        w = self._world()
        self._capture(w, "Bohemia")
        head = dispatch_mod._build_headline(w, "France")
        assert head and head["class"] == "region_taken", head
        assert "Bohemia" in head["text"]

    def test_a_liberated_homeland_province_reads_as_restored(self):
        w = self._world()
        self._capture(w, "Paris", prev="Austria")
        # Paris is French homeland AND the enemy's held capital is not —
        # the homeland arm wins.
        head = dispatch_mod._build_headline(w, "France")
        assert head["class"] == "region_taken", head
        assert "French again" in head["text"], head

    def test_storming_an_enemy_capital_is_its_own_class(self):
        w = self._world()
        self._capture(w, "Vienna", prev="Austria")
        head = dispatch_mod._build_headline(w, "France")
        assert head["class"] == "capital_stormed", head
        assert "capital" in head["text"], head

    def test_an_eliminated_enemy_leads_over_a_stormed_capital(self):
        w = self._world()
        self._capture(w, "Vienna", prev="Austria")
        w.war_instances = {"w": {
            "side_by_nation": {"France": "attackers", "Austria": "defenders"},
            "ended_turn": None}}
        w.event_log.append({"type": "nation_eliminated", "nation": "Austria",
                            "turn": w.current_turn})
        head = dispatch_mod._build_headline(w, "France")
        assert head["class"] == "enemy_eliminated", head
        # The stormed capital survives as a sub-beat — distinct facts.
        assert any("Vienna" in b for b in head.get("sub_beats", [])), head

    def test_a_third_party_elimination_is_not_our_triumph(self):
        w = self._world()
        w.war_instances = {"w": {
            "side_by_nation": {"Prussia": "attackers", "Bavaria": "defenders"},
            "ended_turn": None}}
        w.event_log.append({"type": "nation_eliminated", "nation": "Bavaria",
                            "turn": w.current_turn})
        head = dispatch_mod._build_headline(w, "France")
        assert head is None or head["class"] != "enemy_eliminated", head

    def test_an_annihilation_victory_is_news(self):
        w = self._world()
        w.event_log.append({
            "type": "battle", "turn": w.current_turn,
            "attacker": "Ney", "defender": "Mack",
            "attacker_nation": "France", "defender_nation": "Austria",
            "outcome": "attacker_victory", "location": "Bohemia",
            "attacker_casualties": 2000, "defender_casualties": 9000,
        })
        head = dispatch_mod._build_headline(w, "France")
        assert head and head["class"] == "victory_won", head
        assert "Mack" in head["text"], head

    def test_a_tactical_win_alone_is_not_decisive_news(self):
        w = self._world()
        w.event_log.append({
            "type": "battle", "turn": w.current_turn,
            "attacker": "Ney", "defender": "Mack",
            "attacker_nation": "France", "defender_nation": "Austria",
            "outcome": "attacker_tactical_victory", "location": "Bohemia",
            "attacker_casualties": 1000, "defender_casualties": 2000,
        })
        head = dispatch_mod._build_headline(w, "France")
        assert head is None or head["class"] != "victory_won", head

    def test_a_tactical_win_that_broke_the_enemy_is_decisive_news(self):
        w = self._world()
        w.event_log.append({
            "type": "battle", "turn": w.current_turn,
            "attacker": "Ney", "defender": "Mack",
            "attacker_nation": "France", "defender_nation": "Austria",
            "outcome": "attacker_tactical_victory", "location": "Bohemia",
            "attacker_casualties": 1000, "defender_casualties": 4000,
        })
        w.event_log.append({
            "type": "retreat", "marshal": "Mack", "nation": "Austria",
            "turn": w.current_turn, "forced": True, "region": "Bohemia",
        })
        head = dispatch_mod._build_headline(w, "France")
        assert head and head["class"] == "victory_won", head
        assert "broken" in head["text"], head

    def test_an_ai_vs_ai_rout_is_not_our_victory(self):
        """The join is on a FRENCH battle win — a Prussian rout in an
        Austro-Prussian war never reads as France's triumph."""
        w = self._world()
        w.event_log.append({
            "type": "retreat", "marshal": "Hohenlohe", "nation": "Prussia",
            "turn": w.current_turn, "forced": True, "region": "Silesia",
        })
        key = w._make_diplo_key("France", "Prussia")
        w.diplomatic_states[key] = "WAR"
        head = dispatch_mod._build_headline(w, "France")
        assert head is None or head["class"] != "victory_won", head

    def test_the_victory_absorbs_the_bare_conquest_of_its_own_field(self):
        w = self._world()
        w.event_log.append({
            "type": "battle", "turn": w.current_turn,
            "attacker": "Ney", "defender": "Mack",
            "attacker_nation": "France", "defender_nation": "Austria",
            "outcome": "attacker_victory", "location": "Bohemia",
            "attacker_casualties": 2000, "defender_casualties": 9000,
        })
        self._capture(w, "Bohemia")
        head = dispatch_mod._build_headline(w, "France")
        assert head["class"] == "victory_won", head
        classes = {head["class"]}
        classes.update()
        assert not any("fallen to our arms" in b
                       for b in head.get("sub_beats", [])), head

    def test_at_equal_scale_the_wound_still_leads(self):
        """The gate's weight principle: a lost province (75) outranks a
        decisive field victory (73) on the same turn."""
        w = self._world()
        w.event_log.append({
            "type": "battle", "turn": w.current_turn,
            "attacker": "Ney", "defender": "Mack",
            "attacker_nation": "France", "defender_nation": "Austria",
            "outcome": "attacker_victory", "location": "Bohemia",
            "attacker_casualties": 2000, "defender_casualties": 9000,
        })
        w.event_log.append({
            "type": "region_captured", "region": "Lyon",
            "captured_by": "Austria", "captured_from": "France",
            "turn": w.current_turn,
        })
        head = dispatch_mod._build_headline(w, "France")
        assert head["class"] in ("region_lost", "home_captured"), head

    def test_success_classes_are_events_not_standing(self):
        for cls in ("enemy_eliminated", "capital_stormed",
                    "victory_won", "region_taken"):
            assert cls in dispatch_mod.HEADLINE_WEIGHTS
            assert cls in dispatch_mod._HEADLINE_TEMPLATES
            assert cls in dispatch_mod._HEADLINE_BERTHIER_NOTES
            assert cls not in dispatch_mod.STANDING_HEADLINE_CLASSES

    def test_the_gate_weight_order_is_pinned(self):
        wts = dispatch_mod.HEADLINE_WEIGHTS
        assert wts["enemy_eliminated"] == 93
        assert wts["capital_stormed"] == 92
        assert wts["victory_won"] == 73
        assert wts["region_taken"] == 68
        # The principle, as arithmetic:
        assert wts["marshal_captured"] > wts["enemy_eliminated"]
        assert wts["capital_stormed"] > wts["own_broken"]
        assert wts["victory_won"] > wts["supply_strain"]
        assert wts["region_lost"] > wts["victory_won"]
        assert wts["war_touches_us"] > wts["region_taken"]
        assert wts["region_taken"] > wts["ally_broken"]


# ═══════════════════════════════════════════════════════════════════════
# §10.3 CA8-17 — labels in tables, phrases in mouths
# ═══════════════════════════════════════════════════════════════════════

class TestSpokenBlockerVocabulary:

    def test_all_eight_negative_capable_components_have_phrases(self):
        from backend.game_logic.diplomatic_templates import (
            SPOKEN_BLOCKER_PHRASES,
        )
        expected = {
            "base_side_pressure", "settlement_tier_legitimacy",
            "term_harshness_penalty", "leader_own_losses",
            "burdened_participant_penalty", "projected_hegemony_mod",
            "abandoned_by_ally_acceptance_mod", "agenda_settlement_mod",
        }
        assert set(SPOKEN_BLOCKER_PHRASES) == expected
        for phrase in SPOKEN_BLOCKER_PHRASES.values():
            assert phrase and "{" not in phrase

    def test_unknown_component_degrades_to_the_label(self):
        from backend.game_logic.diplomatic_templates import (
            spoken_blocker_phrase,
        )
        assert (spoken_blocker_phrase("some_future_term", "Future term")
                == "Future term")
        assert spoken_blocker_phrase("", "") == "the standing terms"

    def _world(self):
        return WorldFactory.with_marshals(
            [MarshalFactory.infantry(name="Ney", location="Paris")],
            current_turn=8)

    def _voice(self, world, court, band="reject",
               component="settlement_tier_legitimacy"):
        from backend.game_logic.diplomatic_templates import (
            resolve_multi_court_settlement_voice,
        )
        out = resolve_multi_court_settlement_voice(
            world,
            per_court_acceptance=[{
                "nation": court, "band": band, "total": 20,
                "top_blocker_display": "Settlement legitimacy",
                "top_blocker_component": component,
            }],
            overall_acceptance={"carries": False,
                                "holdout_courts": [court]},
            war_label="the War of the Third Coalition",
        )
        rows = out["per_court_voice"]
        assert rows and rows[0]["line"]
        return rows[0]

    def test_the_label_is_no_longer_spoken(self):
        row = self._voice(self._world(), "Britain")
        assert "Settlement legitimacy" not in row["line"], row
        assert "a victory the field has not delivered" in row["line"], row

    def test_castlereagh_frames_it_in_his_own_register(self):
        row = self._voice(self._world(), "Britain")
        assert "arithmetic" in row["line"], row
        assert row["speaker"] in row["line"], row

    def test_a_court_without_a_cast_suffix_uses_the_chancery_frame(self):
        row = self._voice(self._world(), "Russia")
        assert "holds Russia back from the table" in row["line"], row
        assert "a victory the field has not delivered" in row["line"], row

    def test_the_leaning_band_speaks_too(self):
        row = self._voice(self._world(), "Prussia", band="near_acceptable",
                          component="term_harshness_penalty")
        assert "the terms weigh heavier than their defeat" in row["line"], row
        assert "Settlement legitimacy" not in row["line"]

    def test_no_raw_braces_ever_reach_the_player(self):
        for court in ("Britain", "Prussia", "Austria", "Saxony", "Russia"):
            for band in ("near_acceptable", "reject"):
                row = self._voice(self._world(), court, band=band)
                assert "{" not in row["line"], row

    def test_a_missing_component_key_degrades_to_the_old_line(self):
        """Rows from older producers (no component key) keep working — the
        display label rides the clause slot."""
        row = self._voice(self._world(), "Russia", component="")
        assert "Settlement legitimacy" in row["line"], row

    def test_will_sign_and_hard_stop_are_untouched(self):
        from backend.game_logic.diplomatic_templates import (
            SETTLEMENT_VOICE_TEMPLATES,
        )
        assert SETTLEMENT_VOICE_TEMPLATES[
            "settlement_multi_court_court_will_sign"].startswith("{speaker}")
        assert "no live" in SETTLEMENT_VOICE_TEMPLATES[
            "settlement_multi_court_court_hard_stop"]

    def test_talleyrand_headings_scan_with_clause_and_label(self):
        """The colon / em-dash forms: both a spoken clause and a label must
        read grammatically in the heading templates."""
        from backend.game_logic.diplomatic_templates import (
            SETTLEMENT_VOICE_TEMPLATES,
        )
        assert ("what weighs heaviest: {top_blocker}"
                in SETTLEMENT_VOICE_TEMPLATES[
                    "settlement_review_heading_talleyrand"])
        assert ("— {top_blocker} —"
                in SETTLEMENT_VOICE_TEMPLATES[
                    "settlement_blocked_for_ratification_observer"])

    def test_per_court_rows_carry_the_component_key(self):
        """`_enrich_acceptance_display` rides the KEY beside the label."""
        from backend.game_logic.settlement_baseline import (
            _enrich_acceptance_display,
        )
        enriched = _enrich_acceptance_display({
            "band": "reject",
            "feedback": [{"component": "settlement_tier_legitimacy",
                          "value": -10}],
        })
        assert (enriched["top_blocker_component"]
                == "settlement_tier_legitimacy")
        assert enriched["top_blocker_display"] == "Settlement legitimacy"

    def test_the_banned_words_stay_banned(self):
        """SC-32 D5 boundary on all the new committed copy."""
        from backend.game_logic.diplomatic_templates import (
            SETTLEMENT_VOICE_TEMPLATES, SPOKEN_BLOCKER_PHRASES,
        )
        new_keys = [k for k in SETTLEMENT_VOICE_TEMPLATES
                    if ("_leaning_" in k or "_holds_out_" in k)]
        assert len(new_keys) == 10, new_keys
        for key in new_keys:
            text = SETTLEMENT_VOICE_TEMPLATES[key].lower()
            for banned in ("conference", "congress", "veto"):
                assert banned not in text, (key, banned)
            assert "{speaker}" in SETTLEMENT_VOICE_TEMPLATES[key], key
            assert "{blocker_clause}" in SETTLEMENT_VOICE_TEMPLATES[key], key
        for phrase in SPOKEN_BLOCKER_PHRASES.values():
            for banned in ("conference", "congress", "veto"):
                assert banned not in phrase.lower()


# ═══════════════════════════════════════════════════════════════════════
# §10.4 CA8-D4 / CA8-16 — the hegemony banks escape the fear monoculture
# ═══════════════════════════════════════════════════════════════════════

class TestHegemonyBankDepth:

    _REGISTERS = ("hawk", "schemer", "dove", "chancery", "loyalist")
    _NAMED = (
        "Castlereagh", "Hardenberg", "Metternich", "Einsiedel", "Araujo",
        "Bernstorff", "Cevallos", "Chancery of Hanover",
        "Chancery of Helvetia", "Chancery of Hesse", "Chancery of Sardinia",
        "Consalvi", "Czartoryski", "Ehrenheim", "Marescalchi", "Medici",
        "Montgelas", "Reis Efendi", "Schimmelpenninck",
    )

    def test_every_hegemony_bank_has_at_least_three_variants(self):
        from backend.game_logic.diplomatic_templates import (
            _INCOMING_MOTIVE_LINES, _NAMED_MOTIVE_LINES,
        )
        for register in self._REGISTERS:
            bank = _INCOMING_MOTIVE_LINES[(register, "hegemony_pressure")]
            assert len(bank) >= 3, register
        for name in self._NAMED:
            bank = _NAMED_MOTIVE_LINES[(name, "hegemony_pressure")]
            assert len(bank) >= 3, name

    def test_register_bank_third_variants_keep_the_nation_slot(self):
        from backend.game_logic.diplomatic_templates import (
            _INCOMING_MOTIVE_LINES,
        )
        for register in self._REGISTERS:
            bank = _INCOMING_MOTIVE_LINES[(register, "hegemony_pressure")]
            assert "{nation}" in bank[2], (register, bank[2])

    def test_the_rotation_actually_reaches_the_third_line(self):
        """Three consecutive turns compose three DISTINCT lines for one
        court — the measured 72%-exact-repeat lever, moved."""
        from backend.game_logic.diplomatic_templates import (
            compose_incoming_diplomat_line,
        )
        world = WorldFactory.with_marshals(
            [MarshalFactory.infantry(name="Ney", location="Paris")],
            current_turn=1)
        lines = set()
        for turn in (1, 2, 3):
            world.current_turn = turn
            lines.add(compose_incoming_diplomat_line(
                world, nation="Austria", proposal_type="non_aggression",
                decision_reason="hegemony_pressure"))
        assert len(lines) == 3, lines


# ═══════════════════════════════════════════════════════════════════════
# §10.5 CA8-19 — the parity ruling, pinned
# ═══════════════════════════════════════════════════════════════════════

class TestGarrisonParityRuling:

    def _assault(self, garrison_strength):
        from backend.commands.executor import CommandExecutor
        world = WorldState()
        for m in world.marshals.values():
            if m.nation == "France":
                m.location = "Bordeaux"
        target = world.get_region("Berlin")
        assert target is not None
        target.controller = "Britain"
        target.garrison_strength = garrison_strength
        target.garrison_detachment = False
        ney = world.marshals["Ney"]
        ney.location = "Berlin"
        ney.strength = 12000
        executor = CommandExecutor()
        result = executor._combat._resolve_garrison_combat(
            ney, target, world, {"world": world})
        return world, ney, result

    def test_a_repulsed_escalade_moves_no_glory(self):
        """CANONIZED: the ladder prices reputation between commanders — a
        garrison has none. The repulse is paid in men, not face."""
        world, ney, result = self._assault(garrison_strength=60000)
        assert result["success"] is True
        assert "holds" in result["message"], result["message"]
        assert ney.glory_events == [], ney.glory_events
        assert ney.strength < 12000  # the cost is paid in men

    def test_the_resolver_never_calls_resolve_battle(self):
        """The design ruling as a structural pin: garrison assault is a
        separate resolver, stated at its head. The docstring may NAME
        `resolve_battle` (the ruling text does); the body may not call it."""
        from backend.commands.combat_executor import CombatExecutor
        src = inspect.getsource(CombatExecutor._resolve_garrison_combat)
        assert "CA8-19 GATE RULING" in src
        body = src.split('"""', 2)[2]
        assert "resolve_battle" not in body, (
            "garrison assault started calling the field resolver — the "
            "§10.5 ruling must be consciously re-opened, not drifted past")

    def test_a_collapsed_garrison_still_conquers(self):
        """FALSIFIABLE NEGATIVE: the ruling changed no behavior."""
        world, ney, result = self._assault(garrison_strength=6000)
        assert result["success"] is True
        target = world.get_region("Berlin")
        assert target.garrison_strength == 0
