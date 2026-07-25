"""AI-1 + AI-1b — the intent layer and the mirror (docs/AI_INTENT_SPEC.md
§3, §3.5, §4.1; Stage B).

Read-only slice: intent is a pure derivation with legibility surfaces.
Pinned here: the authored-1805 boot intents (measured values, the MC-2
re-measure idiom), the cache chokepoint (production seam flush), the
turn-granular staleness DECISION, deckless neutrality (§5 pin 18's
backend arm), the §3.8 weight jitter riding the campaign seed, the ledger
payloads, and the mirror's restraint-drift contract.
"""

from pathlib import Path

import pytest

from backend.game_logic.intent import (
    PRICE_LADDER,
    build_france_mirror_payload,
    build_intent_payload,
    get_nation_intent,
    rung_index,
)
from backend.models.world_state import WorldState

SCENARIO_PATH = (
    Path(__file__).resolve().parents[1]
    / "godot-client" / "project-sovereign" / "assets" / "maps"
    / "europe_1805.json"
)


@pytest.fixture(scope="module")
def world1805():
    """Read-only module-scoped 1805 campaign — mutating tests copy it."""
    return WorldState.from_scenario(str(SCENARIO_PATH))


@pytest.fixture
def world(world1805):
    return WorldState.from_dict(world1805.to_dict())


# ════════════════════════════════════════════════════════════════════════
# The authored 1805 boot intents — measured pins (historical seed)
# ════════════════════════════════════════════════════════════════════════

class TestBootIntents:
    @pytest.mark.parametrize("nation,want,against,weight,price", [
        # RE-MEASURED CONSCIOUSLY at AI-3r.2 (AI_WAR_DECISION_SPEC.md):
        # the dead at-war-with-holder +10 is retired (ruling R5) and the
        # §2.2 moment terms enter — every anti-France court reads the
        # allies-committed +6 at boot (Spain and Bavaria, France's
        # treaty allies, boot at war), and Austria's near-empty reserve
        # (worst armed neighbour: 22k Bavaria) reads rear-quiet +6.
        # The three coalition belligerents still price at the top of the
        # ladder — the war IS the pursuit (the _derive_price early
        # return, untouched).
        ("Austria", "redeem_italy", "France", 85, "fight"),
        ("Britain", "low_countries", "France", 84, "fight"),
        ("Russia", "arbiter_of_europe", "France", 89, "fight"),
        # Berlin covets Hanover and is maneuvering alliances for it —
        # the Potsdam winter, read straight off the authored opening.
        # UNMOVED by AI-3r: no moment term fires against a quiet,
        # ally-less Hanover — the marquee case still needs its moment.
        ("Prussia", "hanoverian_prize", "Hanover", 59, "align"),
        # Gustav IV mobilises (the allies-committed read lifts Stockholm
        # to the war rung — but its design aims at the player-hegemon,
        # which stays the coalition's business, D3); Turin seethes; the
        # neutrals guard.
        ("Sweden", "scourge_of_the_usurper", "France", 89, "fight"),
        ("Sardinia", "house_of_savoy_restored", "France", 79, "coerce"),
        ("Ottoman", "guard_the_straits", None, 25, "ask"),
        ("Denmark", "neutrality_of_the_north", None, 25, "ask"),
    ])
    def test_boot_intent(self, world1805, nation, want, against, weight,
                         price):
        view = get_nation_intent(nation, world1805)
        assert view.want_id == want
        assert view.against == against
        assert view.weight == weight
        assert view.price == price
        assert not view.survival

    def test_deckless_and_vassal_and_player_are_indifferent(self, world1805):
        # §5 pin 18's backend arm: no live agenda → the bottom rung.
        for nation in ("France", "Bavaria", "Saxony", "Hesse",
                       "KingdomOfItaly", "Holland"):
            view = get_nation_intent(nation, world1805)
            assert view.price == "indifferent"
            assert view.weight == 0
            assert view.want_id is None
            assert build_intent_payload(nation, world1805) is None

    def test_bare_world_every_nation_indifferent(self):
        # The suite's own world (SOVEREIGN_SCENARIO=none): agendas == {}.
        bare = WorldState(player_nation="France")
        for nation in list(getattr(bare, "enemy_nations", []))[:5]:
            assert get_nation_intent(nation, bare).price == "indifferent"
            assert build_intent_payload(nation, bare) is None

    def test_ladder_is_ordered(self):
        assert PRICE_LADDER == ("indifferent", "ask", "buy", "align",
                                "bandwagon", "coerce", "fight")
        assert rung_index("fight") > rung_index("coerce") > \
            rung_index("bandwagon") > rung_index("align") > \
            rung_index("buy") > rung_index("ask") > \
            rung_index("indifferent")


# ════════════════════════════════════════════════════════════════════════
# Cache + staleness — the DECIDED contract, pinned
# ════════════════════════════════════════════════════════════════════════

class TestCacheAndStaleness:
    def test_cache_is_per_turn(self, world):
        get_nation_intent("Austria", world)
        assert world._intent_cache_turn == world.current_turn
        world._intent_cache_turn = world.current_turn - 1
        world._intent_cache = {"Austria": None}
        assert get_nation_intent("Austria", world) is not None

    def test_production_diplomatic_seam_flushes_cache(self, world):
        # set_diplomatic_state → invalidate_bloc_members_cache → the
        # intent cache flushes beside the agenda cache — same turn.
        # AI-3r re-anchor: Austria's peacetime weight (85) now sits AT
        # the fight threshold, so its price no longer moves on peace —
        # Britain (84 → coerce) is the court whose rung must flip.
        from backend.game_logic.diplomacy import set_diplomatic_state
        assert get_nation_intent("Britain", world).price == "fight"
        set_diplomatic_state(world, "Britain", "France", "PEACE", "test")
        view = get_nation_intent("Britain", world)
        assert view.price != "fight"

    def test_relations_are_turn_granular_by_design(self, world):
        # The DECIDED staleness contract (§4.1): a mid-turn relation delta
        # does NOT recompute intent — the agendas treasury choice, applied
        # to intent. It self-heals at the turn key.
        before = get_nation_intent("Prussia", world)
        world.modify_nation_relation("Prussia", "Hanover", -60)
        assert get_nation_intent("Prussia", world) == before
        world.current_turn += 1
        after = get_nation_intent("Prussia", world)
        assert after.weight != before.weight

    def test_intent_survives_save_load_identically(self, world1805):
        # §5 pin 8's derived arm: intent is derived, so a round-trip
        # derives the SAME reading (the seed rides the save).
        restored = WorldState.from_dict(world1805.to_dict())
        for nation in ("Austria", "Prussia", "Britain", "Russia"):
            assert (get_nation_intent(nation, restored)
                    == get_nation_intent(nation, world1805))


# ════════════════════════════════════════════════════════════════════════
# §3.8 weight jitter — the seed's first consumer
# ════════════════════════════════════════════════════════════════════════

class TestWeightJitter:
    def test_historical_seed_never_jitters(self, world1805):
        # Review fix [11] (the old form compared a cached view to itself):
        # a DEEP-campaign historical world must still read the boot weight
        # — the historical seed jitters at NO turn, ever.
        assert world1805.campaign_seed == "historical"
        deep = WorldState.from_dict(world1805.to_dict())
        deep.current_turn = 20
        assert get_nation_intent("Prussia", deep).weight == 59

    def test_variance_seed_jitter_ramps_weighted_late(self):
        # Same seeded world at turn 1 vs turn 20: the weight moves by
        # EXACTLY the ramp delta of the jitter helper — nonzero for this
        # (seed, namespace), so a dead jitter fails here (review fix [10]).
        # Comparing within one world isolates the ramp from the Tier-2
        # boot-band offsets that seed also carries.
        from backend.game_logic.campaign_variance import seeded_jitter
        namespace = "intent_weight::Prussia::hanoverian_prize"
        seeded = WorldState.from_scenario(str(SCENARIO_PATH),
                                          seed="jena-06")
        early = get_nation_intent("Prussia", seeded).weight
        seeded.current_turn = 20
        seeded._intent_cache = None
        late = get_nation_intent("Prussia", seeded).weight
        expected_delta = (seeded_jitter("jena-06", namespace, 8, 20)
                          - seeded_jitter("jena-06", namespace, 8, 1))
        assert expected_delta != 0
        assert late - early == expected_delta
        # Deterministic: the same seed re-derives the same number.
        again = WorldState.from_scenario(str(SCENARIO_PATH),
                                         seed="jena-06")
        again.current_turn = 20
        assert get_nation_intent("Prussia", again).weight == late


# ════════════════════════════════════════════════════════════════════════
# Surfaces — ledger rows, the mirror, the war room
# ════════════════════════════════════════════════════════════════════════

class TestSurfaces:
    def test_nations_tab_rows_carry_intent(self, world1805):
        from backend.game_logic.diplomatic_ledger import (
            build_diplomatic_ledger,
        )
        ledger = build_diplomatic_ledger(world1805)
        rows = {row["name"]: row for row in ledger["nations"]}
        austria = rows["Austria"]["intent"]
        assert austria is not None
        assert austria["price"] == "fight"
        assert "war" in austria["summary"]
        assert austria["against_display"] == "France"
        # Deckless court: the row carries None and the renderer omits.
        assert rows["Saxony"]["intent"] is None

    def test_mirror_reads_the_hegemon(self, world1805):
        from backend.game_logic.diplomatic_ledger import (
            build_diplomatic_ledger,
        )
        mirror = build_diplomatic_ledger(world1805)["france_mirror"]
        assert mirror is not None
        assert "hegemon" in mirror["read_as"].lower()
        assert mirror["hegemon_share"] >= 0.33
        assert mirror["perceived_price"] == "fight"  # a coalition stands
        assert mirror["perceived_weight"] == 85      # = the alarm level
        # Measured pin (re-anchor if the authored deployment moves): the
        # Grande Armee's corps read as a threat to the small neighbour
        # whose soil they stand against — §3.5's misreading, by design.
        assert mirror["perceived_target"] == "Hesse"
        assert len(mirror["lines"]) == 3

    def test_mirror_never_reads_an_ally_or_vassal(self, world1805):
        mirror = build_france_mirror_payload(world1805)
        target = mirror["perceived_target"]
        assert target is not None
        assert world1805.get_diplomatic_state("France", target) not in (
            "ALLIANCE", "DEFENSIVE_ALLIANCE", "VASSAL")

    def test_mirror_restraint_drifts_down(self, world):
        # §3.5 pin: a player who does nothing drifts DOWN the perceived
        # ladder — threat decay does the work, so a lower alarm must read
        # as a lower rung.
        hot = build_france_mirror_payload(world)
        world.threat_level = 30
        cooled = build_france_mirror_payload(world)
        assert rung_index(cooled["perceived_price"]) < \
            rung_index(hot["perceived_price"])

    def test_mirror_absent_on_legacy_worlds(self):
        bare = WorldState(player_nation="France")
        assert build_france_mirror_payload(bare) is None
        from backend.game_logic.diplomatic_ledger import (
            build_diplomatic_ledger,
        )
        assert build_diplomatic_ledger(bare)["france_mirror"] is None

    def test_war_room_names_the_price(self, world1805):
        from backend.game_logic.diplomatic_advisory import _assess_situation
        assessment = _assess_situation(world1805)
        text = assessment.get("talleyrand_text", "")
        assert "Their price:" in text
        wars = (assessment.get("context") or {}).get("wars") or []
        assert any(row.get("intents") for row in wars)
