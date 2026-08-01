"""AI-5b — emergent designs + the volte-face (docs/AI_INTENT_SPEC.md §3.6,
§11.1 Stage E; landing record §18).

AI-5b(i): a humiliated nation promotes its grievance into a REAL
`acquire_regions` deck entry — front-inserted, activating when the
survival override clears, at most one per nation, announced as a beat.
The three §3.6 substrate rulings are pinned: partition/capital loss are
DERIVED (no new store), the punitive settlement rides a durable
`settlement_memories` record written at the ratify seams, and the broken
bargain reads the §3.3 grievance store (never re-stored).

AI-5b(ii): a great power beaten and then COURTED — never humiliated —
reverses in one signing. The deck-advance is structural (an ALLIANCE
puts the reversed power in the hegemon's bloc, so containment goes
dormant and the deck walks on to §12.2's authored object); beat 5 fires
at the ratify chokepoint.

The §3.6 code-forced constraints pinned here:
(a) the promoted entry is a plain acquire_regions entry;
(b) FRONT-inserted (first-predicate-wins would strand an appended one);
(c) recorded AT the humiliation, ACTIVE only when the override clears.
"""

from pathlib import Path

import pytest

from backend.game_logic.agendas import (
    get_active_agenda,
    get_agenda_grudge_nations,
)
from backend.game_logic.emergent_designs import (
    EMERGENT_DESIGN_MIN_LOST,
    PUNITIVE_MEMORY_TYPE,
    PUNITIVE_SETTLEMENT_MIN_PROVINCES,
    VOLTE_FACE_RELATION_FLOOR,
    VOLTE_FACE_WE_MARK,
    VOLTE_FACE_WINDOW,
    collect_cessions_from_clauses,
    maybe_fire_volte_face,
    process_emergent_designs,
    record_punitive_cessions,
    volte_face_receptive,
)
from backend.game_logic.settlement_reactions import get_settlement_memories
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


def _partition(world, nation="Prussia", count=2, holder="Austria",
               spare_capital=True):
    """Hand `count` of the nation's homeland provinces to `holder`."""
    capital = world.get_nation_capital(nation)
    taken = []
    for region_name in world.nation_starting_regions.get(nation, []):
        if spare_capital and region_name == capital:
            continue
        world.regions[region_name].controller = holder
        taken.append(region_name)
        if len(taken) >= count:
            break
    world.invalidate_bloc_members_cache()
    return taken


# ═══════════════════════ AI-5b(i) — PROMOTION ══════════════════════════════


class TestPromotion:
    def test_boot_world_promotes_nothing(self, world):
        """Pin 1's neighbour: nobody acquires an appetite on turn 0 —
        the authored 1805 map has no lost homeland anywhere."""
        assert process_emergent_designs(world) == []
        assert not any(
            e.get("emergent")
            for deck in world.agendas.values() for e in deck)

    def test_partition_promotes_front_inserted_acquire(self, world):
        taken = _partition(world, "Prussia", EMERGENT_DESIGN_MIN_LOST,
                           "Austria")
        events = process_emergent_designs(world)
        assert [e["nation"] for e in events] == ["Prussia"]
        assert events[0]["author"] == "Austria"
        deck = world.agendas["Prussia"]
        entry = deck[0]
        # Constraint (a): a plain acquire entry the validator knows.
        assert entry["type"] == "acquire_regions"
        # Constraint (b): FRONT-inserted, ahead of hanoverian_prize.
        assert entry["id"] == "revanche_prussia"
        assert deck[1]["id"] == "hanoverian_prize"
        assert entry["regions"] == taken
        assert entry["emergent"] is True
        assert entry["author"] == "Austria"

    def test_capital_loss_alone_promotes(self, world):
        capital = world.get_nation_capital("Prussia")
        world.regions[capital].controller = "Austria"
        world.invalidate_bloc_members_cache()
        events = process_emergent_designs(world)
        assert [e["nation"] for e in events] == ["Prussia"]
        assert capital in world.agendas["Prussia"][0]["regions"]

    def test_single_loss_alone_does_not_promote(self, world):
        """One non-capital province with no durable record is a border
        incident, not a partition — never a vibe promotion (§3.6)."""
        _partition(world, "Prussia", 1, "Austria")
        assert process_emergent_designs(world) == []

    def test_single_loss_with_punitive_record_promotes(self, world):
        taken = _partition(world, "Prussia", 1, "Austria")
        from backend.game_logic.settlement_reactions import (
            _add_settlement_memory,
        )
        _add_settlement_memory(
            world, actor="Austria", subject="Prussia",
            memory_type=PUNITIVE_MEMORY_TYPE,
            episode_id="test", payload={"provinces": taken},
            expires_in=None)
        events = process_emergent_designs(world)
        assert [e["nation"] for e in events] == ["Prussia"]
        assert events[0]["author"] == "Austria"

    def test_single_loss_with_renege_grievance_promotes(self, world):
        """The §3.3 route: a betrayed court promotes at ONE lost province
        when the holder is the bargain-breaker (read from the existing
        grievance store — never re-stored)."""
        _partition(world, "Prussia", 1, "Austria")
        from backend.game_logic.diplomacy import _add_grievance_flag
        _add_grievance_flag(
            world, breaker="Austria", victim="Prussia",
            grievance_type="bargain_reneged", episode_id="test-renege",
            source_episode_type="compensation_bargain")
        events = process_emergent_designs(world)
        assert [e["nation"] for e in events] == ["Prussia"]
        assert events[0]["author"] == "Austria"

    def test_max_one_emergent_design_ever(self, world):
        _partition(world, "Prussia", 2, "Austria")
        assert len(process_emergent_designs(world)) == 1
        # A second, different partition later promotes nothing more.
        _partition(world, "Prussia", 4, "Austria")
        assert process_emergent_designs(world) == []
        emergent = [e for e in world.agendas["Prussia"]
                    if e.get("emergent")]
        assert len(emergent) == 1

    def test_player_never_promotes(self, world):
        """France's wants are the player's own choices — the §3.5 mirror
        is France's row (documented Stage E decision)."""
        _partition(world, "France", 3, "Austria")
        assert process_emergent_designs(world) == []
        assert "France" not in world.agendas

    def test_vassal_never_promotes_while_vassalized(self, world):
        """The dormant-deck doctrine: a satellite's grievances wake with
        its independence, not before."""
        assert "Holland" in world.vassals
        _partition(world, "Holland", 2, "Britain")
        assert process_emergent_designs(world) == []
        # Released later with the loss still standing, it promotes.
        del world.vassals["Holland"]
        world.invalidate_bloc_members_cache()
        events = process_emergent_designs(world)
        assert any(e["nation"] == "Holland" for e in events)

    def test_survival_override_outranks_then_activation_on_clear(self, world):
        """Constraint (c), BOTH halves: promoted AT the humiliation while
        the survival override holds the deck down; ACTIVE the turn the
        override clears — structurally, because the override sits above
        the deck walk. Anything else is dead code in exactly the case
        the mechanic was written for (§3.6)."""
        capital = world.get_nation_capital("Prussia")
        taken = _partition(world, "Prussia", 2, "Austria")
        world.regions[capital].controller = "Austria"
        world.invalidate_bloc_members_cache()
        events = process_emergent_designs(world)
        assert [e["nation"] for e in events] == ["Prussia"]
        view = get_active_agenda("Prussia", world)
        assert view is not None and view.survival, (
            "the Knife at the Throat outranks the promoted design")
        # The capital returns; the override clears; revanche is LIVE.
        world.regions[capital].controller = "Prussia"
        world.invalidate_bloc_members_cache()
        view = get_active_agenda("Prussia", world)
        assert view is not None and view.id == "revanche_prussia"
        assert set(taken) <= set(view.regions)

    def test_promotion_announces_beat(self, world):
        _partition(world, "Prussia", 2, "Austria")
        process_emergent_designs(world)
        logged = [e for e in world.event_log
                  if e.get("type") == "design_promoted"]
        assert logged and logged[0]["nation"] == "Prussia"
        assert logged[0]["author"] == "Austria"
        queued = [e for e in world.pending_dispatch_events
                  if e.get("type") == "design_promoted"]
        assert queued and queued[0]["fog_rule"] == "always"

    def test_promoted_entry_survives_save_load(self, world):
        _partition(world, "Prussia", 2, "Austria")
        process_emergent_designs(world)
        restored = WorldState.from_dict(world.to_dict())
        entry = restored.agendas["Prussia"][0]
        assert entry["id"] == "revanche_prussia"
        assert entry["emergent"] is True
        assert entry["author"] == "Austria"
        # And no re-promotion after the load (the latch is the entry).
        assert process_emergent_designs(restored) == []

    def test_legacy_world_is_inert(self):
        """The Europe scoping: the legacy rollback world never runs the
        poll at all (review fix: this pin covers LEGACY — the
        `SOVEREIGN_SCENARIO=none` bare flag world is Europe-SHAPED, so
        the poll legitimately runs there and stays quiet only because
        nothing is lost at boot; §3.6's 'the world writes content'
        applies to any Europe world by recorded decision — a deckless
        nation acquiring its FIRST design by humiliation is the
        Peninsular-War case, not an accident)."""
        legacy = WorldState()
        assert getattr(legacy, "sovereign_map", "legacy") != "europe"
        assert process_emergent_designs(legacy) == []

    def test_authored_id_collision_skips(self, world):
        """A scenario that authors `revanche_prussia` owns the name —
        the runtime never shadows an authored entry."""
        world.agendas["Prussia"].append({
            "id": "revanche_prussia", "type": "acquire_regions",
            "title": "Authored", "regions": ["Silesia"]})
        _partition(world, "Prussia", 2, "Austria")
        assert process_emergent_designs(world) == []

    def test_campaign_log_renders_the_beat(self, world):
        from backend.campaign_log import (
            CAMPAIGN_LOG_TYPES,
            format_event_oneliner,
        )
        assert "design_promoted" in CAMPAIGN_LOG_TYPES
        assert "volte_face" in CAMPAIGN_LOG_TYPES
        line = format_event_oneliner({
            "type": "design_promoted", "nation": "Prussia",
            "author": "Austria", "regions": ["Silesia", "Posen"]})
        assert "REVANCHE" in line and "Silesia" in line
        line = format_event_oneliner({
            "type": "volte_face", "nation": "Russia",
            "partner": "France"})
        assert "VOLTE-FACE" in line

    def test_promotion_runs_in_the_turn_pipeline(self, world):
        """The poll is sited in _advance_turn_internal between the
        formation poll and the shift poll — a partition mid-campaign
        promotes on the next tick without anyone calling the module."""
        _partition(world, "Prussia", 2, "Austria")
        world.advance_turn()
        assert any(e.get("emergent")
                   for e in world.agendas.get("Prussia", []))


# ═══════════════════ THE PUNITIVE RECORD (the ratify seams) ═══════════════


class TestPunitiveRecord:
    def test_bar_two_provinces_or_capital(self, world):
        # Two provinces: punitive.
        record_punitive_cessions(world, {
            "Prussia": [("Silesia", "France"), ("Posen", "France")]})
        assert get_settlement_memories(
            world, subject="Prussia", memory_type=PUNITIVE_MEMORY_TYPE)
        # One non-capital province: not punitive.
        record_punitive_cessions(world, {
            "Austria": [("Tyrol", "France")]})
        assert not get_settlement_memories(
            world, subject="Austria", memory_type=PUNITIVE_MEMORY_TYPE)
        # The capital alone: punitive.
        capital = world.get_nation_capital("Austria")
        record_punitive_cessions(world, {
            "Austria": [(capital, "France")]})
        assert get_settlement_memories(
            world, subject="Austria", memory_type=PUNITIVE_MEMORY_TYPE)
        assert PUNITIVE_SETTLEMENT_MIN_PROVINCES == 2

    def test_author_is_plurality_receiver(self, world):
        record_punitive_cessions(world, {
            "Prussia": [("Silesia", "Austria"), ("Posen", "Austria"),
                        ("Berlin", "France")]})
        records = get_settlement_memories(
            world, subject="Prussia", memory_type=PUNITIVE_MEMORY_TYPE)
        assert records[0]["actor"] == "Austria"
        # Durable — a partition is not forgotten.
        assert records[0]["expires_on_turn"] is None

    def test_author_is_charged_over_homeland_only(self, world):
        """Review fix pinned: a settlement handing Prussia's CONQUESTS to
        Austria (3 provinces of Austrian soil Prussia held) and Prussia's
        HOMELAND to France (2 provinces) blames FRANCE — the court that
        took the homeland — not the plurality receiver of the whole
        package. The record is durable and feeds the volte-face
        foreclosure; a mis-charged author would foreclose the wrong
        pair forever."""
        record_punitive_cessions(world, {
            "Prussia": [("Tyrol", "Austria"), ("Styria", "Austria"),
                        ("Bohemia", "Austria"),
                        ("Silesia", "France"), ("Posen", "France")]})
        records = get_settlement_memories(
            world, subject="Prussia", memory_type=PUNITIVE_MEMORY_TYPE)
        assert records and records[0]["actor"] == "France"
        assert set(records[0]["payload"]["provinces"]) == {
            "Silesia", "Posen"}

    def test_collect_handles_both_clause_dialects(self, world):
        cessions = collect_cessions_from_clauses([
            {"type": "territory_cede", "from": "Prussia", "to": "France",
             "region": "Silesia"},
            {"type": "territory_cede", "from_nation": "Prussia",
             "to_nation": "France", "regions": ["Posen"]},
            {"type": "gold_indemnity", "from": "Prussia", "to": "France",
             "amount": 500},
        ])
        assert cessions["Prussia"] == [
            ("Silesia", "France"), ("Posen", "France")]

    def test_losing_conquests_is_not_a_partition(self, world):
        """Austria surrendering PRUSSIAN soil it held is beaten, not
        humiliated — only the victim's own homeland counts, so the
        volte-face stays open to a court that merely lost its winnings."""
        record_punitive_cessions(world, {
            "Austria": [("Silesia", "Prussia"), ("Posen", "Prussia")]})
        assert not get_settlement_memories(
            world, subject="Austria", memory_type=PUNITIVE_MEMORY_TYPE)

    def test_returns_never_count(self, world):
        """A territory_return restores prior ownership by definition —
        nobody is partitioned by giving back what was taken."""
        assert collect_cessions_from_clauses([
            {"type": "territory_return", "from": "France",
             "to": "Prussia", "regions": ["Silesia", "Posen"]},
        ]) == {}

    def test_bilateral_ratify_writes_the_record(self, world):
        """The _ratify_treaty seam: a harsh bilateral peace stripping two
        provinces leaves the durable mark (APPLIED clauses only)."""
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "WAR"
        world.war_start_turns[key] = int(world.current_turn)
        world.invalidate_bloc_members_cache()
        result = world._ratify_treaty({
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [],
            "demands": [{"type": "territory_cede",
                         "regions": ["Silesia", "Posen"]}],
        })
        assert result is not None
        records = get_settlement_memories(
            world, subject="Prussia", memory_type=PUNITIVE_MEMORY_TYPE)
        assert records and records[0]["actor"] == "France"
        assert set(records[0]["payload"]["provinces"]) == {
            "Silesia", "Posen"}

    def test_third_party_settlement_writes_the_record(self, world):
        """The Stage D AI-AI seam: Vienna's Diktat is remembered exactly
        as Paris's would be — the loser's capital cedes, the durable
        record lands, and the NEXT poll promotes revanche."""
        from backend.game_logic.diplomacy import declare_war
        from backend.game_logic.settlement_third_party import (
            THIRD_PARTY_MIN_WAR_TURNS,
            process_third_party_settlements,
        )
        declare_war(world, "Prussia", "Hanover")
        war = None
        for war_id, instance in world.war_instances.items():
            participants = instance.get("active_participants") or []
            if (instance.get("ended_turn") is None
                    and "Prussia" in participants
                    and "Hanover" in participants):
                war = instance
                break
        assert war is not None
        war["created_turn"] = (int(world.current_turn)
                               - THIRD_PARTY_MIN_WAR_TURNS - 1)
        world.war_exhaustion["Hanover"] = 150
        key = world._make_diplo_key("Hanover", "Prussia")
        world.war_scores[key] = -95 if key.startswith("Hanover") else 95
        events = process_third_party_settlements(world)
        assert any(e["type"] == "third_party_peace" for e in events)
        records = get_settlement_memories(
            world, subject="Hanover", memory_type=PUNITIVE_MEMORY_TYPE)
        assert records and records[0]["actor"] == "Prussia"


# ═══════════════════ THE GRUDGE QUERY, GENERALISED ═════════════════════════


class TestGrudgeGeneralisation:
    def test_default_author_is_the_player_byte_identically(self, world):
        assert (get_agenda_grudge_nations(world)
                == get_agenda_grudge_nations(world, author="France"))

    def test_victim_author_query_for_a_non_player_author(self, world):
        """Prussia, partitioned by Austria in a war that just ended,
        grudges AUSTRIA — readable through the generalised (victim,
        author) form, invisible on the player-anchored default."""
        _partition(world, "Prussia", 2, "Austria")
        process_emergent_designs(world)
        turn = int(world.current_turn)
        world.war_instances["test_war"] = {
            "war_id": "test_war",
            "created_turn": max(0, turn - 6),
            "ended_turn": turn - 1,
            "participant_meta": {
                "Prussia": {"side": "defenders"},
                "Austria": {"side": "attackers"},
            },
            "side_by_nation": {},
        }
        grudged_at_austria = get_agenda_grudge_nations(
            world, author="Austria")
        assert "Prussia" in grudged_at_austria
        assert "Prussia" not in get_agenda_grudge_nations(world)


# ═══════════════════ AI-5b(ii) — THE VOLTE-FACE ════════════════════════════


def _beat_and_court(world, power="Russia", hegemon="France",
                    relation=None, exhausted=True):
    """Arrange the Tilsit state: the war ended recently, the defeat still
    shows (war exhaustion), no punitive record, relations courted up to
    the alliance floor."""
    for other in list(world.get_active_nations()):
        key = world._make_diplo_key(power, other)
        if world.diplomatic_states.get(key) in ("WAR", "ARMISTICE"):
            world.diplomatic_states[key] = "PEACE"
    turn = int(world.current_turn)
    world.war_instances["tilsit_war"] = {
        "war_id": "tilsit_war",
        "created_turn": max(0, turn - 8),
        "ended_turn": max(0, turn - 2),
        "participant_meta": {
            power: {"side": "attackers"},
            hegemon: {"side": "defenders"},
        },
        "side_by_nation": {},
    }
    if exhausted:
        world.war_exhaustion[power] = VOLTE_FACE_WE_MARK + 10
    world.nation_relations[world._make_diplo_key(power, hegemon)] = (
        VOLTE_FACE_RELATION_FLOOR + 5 if relation is None else relation)
    world.invalidate_bloc_members_cache()
    return world


class TestVolteFaceEligibility:
    def test_courted_floor_equals_the_alliance_ratify_gate(self):
        """Drift pin (review fix): §18's 'the courier never offers what
        the treaty gate would refuse' rests on these two constants being
        EQUAL — retune either alone and the offer-then-refuse hole
        silently reopens."""
        from backend.game_logic.diplomacy import STATE_RELATION_REQUIREMENTS
        assert VOLTE_FACE_RELATION_FLOOR == (
            STATE_RELATION_REQUIREMENTS["ALLIANCE"])

    def test_beaten_then_courted_is_receptive(self, world):
        _beat_and_court(world)
        assert volte_face_receptive(world, "Russia", "France") is True

    def test_punitive_record_forecloses_forever(self, world):
        """Generosity is the doctrine: a partition (durable record)
        closes this path — humiliation and reversal never coexist.
        Lithuania and Livonia are RUSSIAN homeland (Finland is Swedish
        in 1805 — it is the gulf design's object, not Russia's soil)."""
        _beat_and_court(world)
        record_punitive_cessions(world, {
            "Russia": [("Lithuania", "France"), ("Livonia", "France")]})
        assert volte_face_receptive(world, "Russia", "France") is False

    def test_sworn_revanche_forecloses(self, world):
        _beat_and_court(world)
        world.agendas["Russia"].insert(0, {
            "id": "revanche_russia", "type": "acquire_regions",
            "title": "Revanche", "regions": ["Lithuania"],
            "emergent": True, "author": "France"})
        assert volte_face_receptive(world, "Russia", "France") is False

    def test_cold_court_is_not_receptive(self, world):
        _beat_and_court(world, relation=VOLTE_FACE_RELATION_FLOOR - 1)
        assert volte_face_receptive(world, "Russia", "France") is False

    def test_unbeaten_power_is_not_receptive(self, world):
        """No recent war with the hegemon — warm relations alone are an
        alliance, not a volte-face."""
        _beat_and_court(world)
        del world.war_instances["tilsit_war"]
        assert volte_face_receptive(world, "Russia", "France") is False

    def test_defeat_must_still_show(self, world):
        _beat_and_court(world, exhausted=False)
        world.war_exhaustion["Russia"] = 0
        assert volte_face_receptive(world, "Russia", "France") is False

    def test_window_expires(self, world):
        _beat_and_court(world)
        world.war_instances["tilsit_war"]["ended_turn"] = (
            int(world.current_turn) - VOLTE_FACE_WINDOW - 1)
        world.war_exhaustion["Russia"] = VOLTE_FACE_WE_MARK + 10
        assert volte_face_receptive(world, "Russia", "France") is False

    def test_minor_never_reverses(self, world):
        _beat_and_court(world, power="Bavaria")
        assert volte_face_receptive(world, "Bavaria", "France") is False

    def test_at_war_never_receptive(self, world):
        _beat_and_court(world)
        key = world._make_diplo_key("Russia", "France")
        world.diplomatic_states[key] = "WAR"
        world.invalidate_bloc_members_cache()
        assert volte_face_receptive(world, "Russia", "France") is False


class TestVolteFaceCourier:
    def test_courier_proposes_the_reversal(self, world):
        """The §11 vignette: St. Petersburg's envoy proposes partnership
        and names the design it would advance to."""
        from backend.game_logic.ai_diplomacy import (
            process_diplomatic_phase,
        )
        _beat_and_court(world)
        proposal = process_diplomatic_phase("Russia", world)
        assert proposal is not None
        assert proposal["proposal_type"] == "alliance"
        assert proposal["decision_reason"] == "volte_face"
        assert proposal["_force_send"] is True
        assert "Gulf and the Straits" in proposal["talleyrand_assessment"]
        cooldowns = world.ai_proposal_cooldowns
        assert cooldowns.get("Russia|volte_face", 0) > 0

    def test_courier_cooldown_blocks_respam(self, world):
        from backend.game_logic.ai_diplomacy import (
            process_diplomatic_phase,
        )
        _beat_and_court(world)
        first = process_diplomatic_phase("Russia", world)
        assert first is not None and first["decision_reason"] == "volte_face"
        second = process_diplomatic_phase("Russia", world)
        assert second is None or second.get("decision_reason") != "volte_face"

    def test_courier_never_fires_on_a_deckless_court(self, world):
        """Pin 18/N1 (review fix): the volte-face is a deck-world
        mechanic — its payoff IS the deck advance — so a deckless court
        (the whole legacy fixture world) keeps its pre-Stage-E rungs
        byte-identically."""
        from backend.game_logic.ai_diplomacy import (
            process_diplomatic_phase,
        )
        _beat_and_court(world)
        world.agendas.pop("Russia", None)
        world.invalidate_bloc_members_cache()
        proposal = process_diplomatic_phase("Russia", world)
        assert proposal is None or (
            proposal.get("decision_reason") != "volte_face")

    def test_courier_never_re_proposes_to_a_standing_ally(self, world):
        """Review fix: an already-allied pair never gets the courier —
        the same-state ratify would refuse an offer the AI itself
        forced onto the mailbox."""
        from backend.game_logic.ai_diplomacy import (
            process_diplomatic_phase,
        )
        _beat_and_court(world)
        key = world._make_diplo_key("Russia", "France")
        world.diplomatic_states[key] = "ALLIANCE"
        world.invalidate_bloc_members_cache()
        proposal = process_diplomatic_phase("Russia", world)
        assert proposal is None or (
            proposal.get("decision_reason") != "volte_face")


class TestVolteFaceBeat:
    def test_alliance_ratify_fires_beat_and_advances_the_deck(self, world):
        """Beat 5 + the §12.2 payoff in one signing: the alliance lands,
        the volte-face is announced, and Russia's deck advances past the
        dormant containment to The Gulf and the Straits — no suspension
        machinery, just bloc geometry."""
        _beat_and_court(world)
        view_before = get_active_agenda("Russia", world)
        assert view_before is not None
        assert view_before.id == "arbiter_of_europe"
        result = world._ratify_treaty({
            "type": "alliance",
            "proposer_nation": "Russia",
            "target_nation": "France",
            "sweeteners": [],
            "demands": [],
        })
        assert result is not None
        assert world.get_diplomatic_state("Russia", "France") == "ALLIANCE"
        logged = [e for e in world.event_log
                  if e.get("type") == "volte_face"]
        assert logged and logged[0]["nation"] == "Russia"
        assert logged[0]["partner"] == "France"
        assert logged[0]["next_design"] == "gulf_and_straits"
        view_after = get_active_agenda("Russia", world)
        assert view_after is not None
        assert view_after.id == "gulf_and_straits", (
            "in France's bloc, containment goes dormant and the deck "
            "advances — Tilsit aims the Tsar at Finland")

    def test_cold_alliance_never_fires_the_beat(self, world):
        """A forced or merely transactional alliance (relations below the
        courted floor) is not a reversal — no beat."""
        _beat_and_court(world, relation=0)
        # The ratify relation gate would refuse ALLIANCE below 40 for a
        # player treaty; call the hook directly to pin the eligibility.
        assert maybe_fire_volte_face(world, "Russia", "France") is None
        assert not any(e.get("type") == "volte_face"
                       for e in world.event_log)

    def test_direction_is_checked_both_ways(self, world):
        """GR5: an AI hegemon courting ITS beaten rival fires too — the
        hook takes the pair, not a France literal."""
        _beat_and_court(world, power="Russia", hegemon="Austria")
        # Make Austria the hegemon Russia fears is irrelevant here — the
        # predicate reads the PAIR's war history and relations.
        event = maybe_fire_volte_face(world, "Austria", "Russia")
        assert event is not None and event["nation"] == "Russia"
        assert event["partner"] == "Austria"
