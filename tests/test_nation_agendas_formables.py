"""Nation Agendas NA-6a — "Formable Dreams" formation core.

Build contract: docs/NATION_AGENDAS_SPEC.md §11 (§11.10 = plan of record).

NA-6a pins: the formation latch and its once-only/permanent semantics, the
two `process_formations` call sites (turn tick + settlement ratification),
the §11.3 rewards, the identity-override payload, the §11.6-5 watcher, the
§11.9 aggrieved blow + the shared-cap formation grudge, the authored Class T
roster (Italy, United Netherlands) incl. the Britain-deny satisfaction
mirror, and the validator's `forms` block.

The structural fact these tests exist to protect: an `acquire_regions`
entry is ACTIVE only while UNMET, so a formable entry is already inactive
on the tick it satisfies. `process_formations` must therefore scan the raw
deck — `test_formable_authored_below_the_first_entry_still_fires` and
`test_forming_entry_is_not_the_active_agenda_when_it_satisfies` are the
pins that fail if anyone "simplifies" it back to `get_active_agenda`.
"""

from pathlib import Path

import pytest

from backend.game_logic.agendas import (
    build_agenda_payload, get_active_agenda,
)
from backend.game_logic.formations import (
    FORMATION_AGGRIEVED_RELATION_PENALTY,
    FORMATION_GOLD,
    FORMATION_STABILITY_BONUS,
    build_nation_display_overrides,
    build_nation_flag_overrides,
    get_display_identity,
    get_formation_grudge_nations,
    get_formation_grudge_threat,
    get_formation_record,
    get_formation_watch,
    get_forms_block,
    process_formations,
)
from backend.models.world_state import WorldState
from backend.modding.validator import validate_scenario

SCENARIO_PATH = (
    Path(__file__).resolve().parents[1]
    / "godot-client" / "project-sovereign" / "assets" / "maps"
    / "europe_1805.json"
)

ITALY_PROVINCES = ["Milan", "Piedmont", "Savoy", "Naples", "Rome"]
DUTCH_PROVINCES = ["Amsterdam", "Brabant", "Flanders"]


@pytest.fixture(scope="module")
def world1805():
    """Read-only module-scoped 1805 campaign — mutating tests copy it."""
    return WorldState.from_scenario(str(SCENARIO_PATH))


@pytest.fixture
def world(world1805):
    return WorldState.from_dict(world1805.to_dict())


def _free(world, nation):
    """Break the vassal link — the §3.2 dormancy gate on formation."""
    world.vassals.pop(nation, None)
    world.invalidate_bloc_members_cache()
    world.invalidate_active_nations_cache()


def _hand_over(world, nation, regions):
    for region_name in regions:
        world.regions[region_name].controller = nation
    world.invalidate_active_nations_cache()


def _free_italy_with_the_peninsula(world):
    _free(world, "KingdomOfItaly")
    _hand_over(world, "KingdomOfItaly", ITALY_PROVINCES)


def _free_holland_with_flanders(world):
    _free(world, "Holland")
    _hand_over(world, "Holland", ["Flanders"])


# ═══════════════════════ BOOT-ZERO (§11.4 pinned) ═════════════════════════

class TestBootZero:
    def test_boot_has_no_formations(self, world):
        assert world.nation_formations == {}
        assert build_nation_display_overrides(world) == {}
        assert build_nation_flag_overrides(world) == {}

    def test_nothing_forms_at_boot(self, world):
        """§11.4: 'Nothing can form or be created at boot — pinned.'"""
        assert process_formations(world) == []
        assert world.nation_formations == {}

    def test_a_full_turn_at_boot_forms_nothing(self, world):
        world.advance_turn()
        assert world.nation_formations == {}

    def test_deckless_world_can_never_form(self):
        """Legacy fixture worlds carry no decks — the poll exits at once."""
        bare = WorldState()
        assert not getattr(bare, "agendas", {})
        assert process_formations(bare) == []


# ═══════════════════════ CLASS T — ITALY (§11.2) ══════════════════════════

class TestItalyForms:
    def test_the_peninsula_proclaims_italy(self, world):
        _free_italy_with_the_peninsula(world)
        proclamations = process_formations(world)

        assert len(proclamations) == 1
        payload = proclamations[0]
        assert payload["nation"] == "KingdomOfItaly"
        assert payload["old_display_name"] == "Kingdom of Italy"
        assert payload["display_name"] == "Italy"
        assert payload["flag_tag"] == "Italy"
        assert payload["entry_id"] == "risorgimento"

    def test_the_tag_never_changes(self, world):
        """§11.1-1, GR-hard: only the DISPLAY identity moves."""
        _free_italy_with_the_peninsula(world)
        process_formations(world)
        assert "KingdomOfItaly" in world.get_active_nations()
        assert "Italy" not in world.get_active_nations()
        assert world.regions["Milan"].controller == "KingdomOfItaly"

    def test_identity_override_payload(self, world):
        _free_italy_with_the_peninsula(world)
        process_formations(world)
        assert build_nation_display_overrides(world) == {"KingdomOfItaly": "Italy"}
        assert build_nation_flag_overrides(world) == {"KingdomOfItaly": "Italy"}
        assert get_display_identity(world, "KingdomOfItaly") == {
            "display_name": "Italy", "flag_tag": "Italy",
        }

    def test_unformed_nations_have_no_identity(self, world):
        assert get_display_identity(world, "Austria") is None
        assert get_display_identity(world, "KingdomOfItaly") is None

    def test_gold_reward_lands_exactly_once(self, world):
        _free_italy_with_the_peninsula(world)
        before = int(world.nation_gold.get("KingdomOfItaly", 0))
        process_formations(world)
        after_first = int(world.nation_gold["KingdomOfItaly"])
        assert after_first == before + FORMATION_GOLD

        # The latch makes the poll idempotent — re-running must not pay again.
        assert process_formations(world) == []
        assert int(world.nation_gold["KingdomOfItaly"]) == after_first

    def test_stability_reward_is_capped_not_uncapped(self, world):
        """§11.3 'capped at max'. Boot provinces sit at 100, so the honest
        observable is that the bonus never pushes past the ceiling."""
        _free_italy_with_the_peninsula(world)
        world.regions["Milan"].stability = 91
        world.regions["Rome"].stability = 100
        process_formations(world)
        assert world.regions["Milan"].stability == 91 + FORMATION_STABILITY_BONUS
        assert world.regions["Rome"].stability == 100

    def test_regions_lifted_is_reported_honestly(self, world):
        """The Proclamation card must not claim a stability lift that the
        cap silently swallowed."""
        _free_italy_with_the_peninsula(world)
        for name in ITALY_PROVINCES:
            world.regions[name].stability = 100
        payload = process_formations(world)[0]
        assert payload["regions_lifted"] == 0

        world2 = WorldState.from_dict(world.to_dict())
        world2.nation_formations = {}
        for name in ITALY_PROVINCES:
            world2.regions[name].stability = 50
        assert process_formations(world2)[0]["regions_lifted"] == len(ITALY_PROVINCES)

    def test_formation_is_permanent(self, world):
        """§11.1: losing provinces later does not un-form the nation."""
        _free_italy_with_the_peninsula(world)
        process_formations(world)
        _hand_over(world, "Austria", ["Milan", "Rome"])
        assert process_formations(world) == []
        assert get_formation_record(world, "KingdomOfItaly") is not None
        assert build_nation_display_overrides(world) == {"KingdomOfItaly": "Italy"}

    def test_partial_peninsula_does_not_form(self, world):
        _free(world, "KingdomOfItaly")
        _hand_over(world, "KingdomOfItaly", ["Milan", "Piedmont", "Savoy", "Naples"])
        assert process_formations(world) == []
        assert world.nation_formations == {}

    def test_no_formation_while_vassalized(self, world):
        """§3.2 dormancy: a client cannot proclaim, however much it holds."""
        _hand_over(world, "KingdomOfItaly", ITALY_PROVINCES)
        assert "KingdomOfItaly" in world.vassals
        assert process_formations(world) == []
        assert world.nation_formations == {}

        # ...and the very next poll after independence fires.
        _free(world, "KingdomOfItaly")
        assert len(process_formations(world)) == 1

    def test_vassal_holdings_count_toward_the_dream(self, world):
        """`_controlled_by_self_or_vassal` is the satisfaction basis — a
        free Italy whose own client holds Rome has still gathered it."""
        _free(world, "KingdomOfItaly")
        _hand_over(world, "KingdomOfItaly",
                   ["Milan", "Piedmont", "Savoy", "Naples"])
        _hand_over(world, "Switzerland", ["Rome"])
        world.vassals["Switzerland"] = {"lord": "KingdomOfItaly", "loyalty": 50}
        world.invalidate_bloc_members_cache()
        world.invalidate_active_nations_cache()
        assert len(process_formations(world)) == 1


# ═══════════════ THE STRUCTURAL PIN: RAW-DECK SCAN (§11.10) ═══════════════

class TestRawDeckScan:
    def test_forming_entry_is_not_the_active_agenda_when_it_satisfies(self, world):
        """The reason `process_formations` cannot use `get_active_agenda`:
        an acquire entry goes INACTIVE at the instant it satisfies."""
        _free_italy_with_the_peninsula(world)
        world._agenda_cache = None
        view = get_active_agenda("KingdomOfItaly", world)
        assert view is None or view.id != "risorgimento"
        # ...and yet the formation still fires.
        assert len(process_formations(world)) == 1

    def test_formable_authored_below_the_first_entry_still_fires(self, world):
        """`_court_design_satisfied` inspects only deck[0]; copying that
        idiom would make a formable at index >= 1 invisible."""
        deck = world.agendas["Austria"]
        deck.append({
            "id": "late_dream",
            "type": "acquire_regions",
            "title": "A Late Dream",
            "regions": ["Vienna"],
            "forms": {"display_name": "Danubia", "flag": "Danubia"},
        })
        world._agenda_cache = None
        assert world.regions["Vienna"].controller == "Austria"
        proclamations = process_formations(world)
        assert [p["display_name"] for p in proclamations] == ["Danubia"]

    def test_one_formation_per_nation_per_pass(self, world):
        """Two satisfied formables on one deck must not double-proclaim."""
        world.agendas["Austria"] = [
            {"id": "a", "type": "acquire_regions", "title": "A",
             "regions": ["Vienna"], "forms": {"display_name": "Alpha"}},
            {"id": "b", "type": "acquire_regions", "title": "B",
             "regions": ["Vienna"], "forms": {"display_name": "Beta"}},
        ]
        world._agenda_cache = None
        proclamations = process_formations(world)
        assert len(proclamations) == 1
        assert proclamations[0]["display_name"] == "Alpha"

    def test_postures_never_form(self, world):
        """guard_neutrality/paymaster never satisfy, so a `forms` block on
        one can never fire — the validator rejects it, and the runtime
        agrees (belt and braces)."""
        world.agendas["Denmark"][0]["forms"] = {"display_name": "Scandinavia"}
        world._agenda_cache = None
        assert process_formations(world) == []


# ═══════════════ CLASS T — UNITED NETHERLANDS + THE DENY MIRROR ═══════════

class TestUnitedNetherlands:
    def test_flanders_proclaims_the_united_netherlands(self, world):
        _free_holland_with_flanders(world)
        proclamations = process_formations(world)
        assert len(proclamations) == 1
        assert proclamations[0]["display_name"] == "United Netherlands"
        assert proclamations[0]["flag_tag"] == "UnitedNetherlands"
        assert build_nation_display_overrides(world) == {
            "Holland": "United Netherlands",
        }

    def test_formation_satisfies_britains_low_countries_design(self, world):
        """§11.2's authored mirror: a free Netherlands holding the Low
        Countries takes them OUT of the hegemon's bloc, which is exactly
        Britain's deny condition. Derived — no formation-aware code."""
        from backend.game_logic.agendas import entry_satisfied

        britain_deny = world.agendas["Britain"][0]
        assert britain_deny["id"] == "low_countries"
        assert not entry_satisfied(world, "Britain", britain_deny), (
            "boot control: France's bloc holds the Low Countries"
        )

        _free(world, "Holland")
        _hand_over(world, "Holland", DUTCH_PROVINCES)
        process_formations(world)
        world._agenda_cache = None
        assert entry_satisfied(world, "Britain", britain_deny)


# ═══════════════════ POST-FORMATION GOALS (§11.1-4, free) ═════════════════

class TestPostFormationGoals:
    def test_the_next_deck_entry_activates_natively(self, world):
        """Zero new goal machinery — deck priority does the work once the
        forming entry satisfies. guard_neutrality needs peace, so this
        pins the at-peace case."""
        _free_italy_with_the_peninsula(world)
        for other in list(world.get_active_nations()):
            if other != "KingdomOfItaly":
                key = world._make_diplo_key("KingdomOfItaly", other)
                world.diplomatic_states[key] = "PEACE"
        world.invalidate_bloc_members_cache()

        process_formations(world)
        world._agenda_cache = None
        view = get_active_agenda("KingdomOfItaly", world)
        assert view is not None
        assert view.id == "guard_the_peninsula"

    def test_next_design_is_silent_when_none_is_active(self, world):
        """Italy boots at war, so its guard posture is legitimately
        inactive — the card must not claim a design it does not hold."""
        _free_italy_with_the_peninsula(world)
        assert world.get_nations_at_war_with("KingdomOfItaly")
        assert process_formations(world)[0]["next_design"] == ""


# ═══════════════════════ THE WATCHER (§11.6-5 / §11.8 stage 0) ════════════

class TestFormationWatch:
    def test_boot_watch_shows_the_dream_and_its_distance(self, world):
        watch = get_formation_watch(world, "KingdomOfItaly")
        assert watch is not None
        assert watch["forms"] == "Italy"
        assert watch["required"] == 5
        assert watch["held"] == 2          # Milan + Piedmont at boot
        assert watch["progress"] == "2 of 5 provinces held"
        assert watch["blocked_by_vassalage"] is True

    def test_watch_states_vassalage_honestly(self, world):
        _hand_over(world, "KingdomOfItaly", ITALY_PROVINCES)
        watch = get_formation_watch(world, "KingdomOfItaly")
        assert watch["held"] == 5
        assert watch["blocked_by_vassalage"] is True, (
            "five of five held but still a client — the surface must not "
            "imply the proclamation is imminent"
        )

    def test_watch_clears_once_formed(self, world):
        _free_italy_with_the_peninsula(world)
        process_formations(world)
        assert get_formation_watch(world, "KingdomOfItaly") is None

    def test_nations_without_a_formable_have_no_watch(self, world):
        assert get_formation_watch(world, "Austria") is None
        assert get_formation_watch(world, "Britain") is None

    def test_agenda_payload_carries_the_forms_marker(self, world):
        """§11.6-5: the marker rides the ACTIVE agenda line."""
        _free(world, "KingdomOfItaly")
        world._agenda_cache = None
        payload = build_agenda_payload("KingdomOfItaly", world)
        assert payload["id"] == "risorgimento"
        assert payload["forms"]["display_name"] == "Italy"
        assert payload["forms"]["held"] == 2
        assert payload["forms"]["required"] == 5
        assert payload["forms"]["progress"] == "2 of 5 provinces held"

    def test_agenda_payload_omits_forms_for_plain_designs(self, world):
        assert "forms" not in build_agenda_payload("Austria", world)


# ═══════════════════════ §11.9 THE AGGRIEVED COURTS ═══════════════════════

def _author_aggrieved_formable(world, nation="Austria", aggrieved=("Prussia",)):
    world.agendas[nation] = [{
        "id": "the_dream", "type": "acquire_regions", "title": "The Dream",
        "regions": ["Vienna"],
        "forms": {"display_name": "Danubia", "flag": "Danubia",
                  "aggrieved": list(aggrieved)},
    }]
    world._agenda_cache = None


class TestAggrievedBlow:
    def test_each_aggrieved_court_takes_the_penalty_once(self, world):
        _author_aggrieved_formable(world, aggrieved=("Prussia", "Russia"))
        keys = {p: world._make_diplo_key("Austria", p)
                for p in ("Prussia", "Russia")}
        before = {p: world.nation_relations.get(k, 0) for p, k in keys.items()}

        payload = process_formations(world)[0]
        assert sorted(payload["aggrieved"]) == ["Prussia", "Russia"]
        for power, key in keys.items():
            assert world.nation_relations[key] == max(
                -100, before[power] + FORMATION_AGGRIEVED_RELATION_PENALTY)

        # No re-fire — the latch, and save/load must not resurrect it.
        after = {p: world.nation_relations[k] for p, k in keys.items()}
        process_formations(world)
        reloaded = WorldState.from_dict(world.to_dict())
        process_formations(reloaded)
        for power, key in keys.items():
            assert world.nation_relations[key] == after[power]
            assert reloaded.nation_relations[key] == after[power]

    def test_no_aggrieved_list_offends_nobody(self, world):
        """The authored Class T roster carries no `aggrieved` — Italy's
        proclamation costs no relations."""
        _free_italy_with_the_peninsula(world)
        snapshot = dict(world.nation_relations)
        payload = process_formations(world)[0]
        assert payload["aggrieved"] == []
        assert world.nation_relations == snapshot

    def test_eliminated_and_vassalized_courts_are_skipped(self, world):
        _author_aggrieved_formable(world, aggrieved=("Switzerland", "Prussia"))
        assert "Switzerland" in world.vassals   # a client has no voice here
        payload = process_formations(world)[0]
        assert payload["aggrieved"] == ["Prussia"]


class TestFormationGrudge:
    def _form_under_player_sponsorship(self, world):
        _author_aggrieved_formable(world, aggrieved=("Prussia",))
        world.vassals["Austria"] = {"lord": "France", "loyalty": 50}
        world.invalidate_bloc_members_cache()
        world.invalidate_active_nations_cache()
        # A client cannot proclaim, so record the sponsor then free it —
        # the NA-6c creation shape, exercised here through the T machinery.
        world.nation_formations["Austria"] = {
            "id": "the_dream", "sponsor": "France", "turn": 0,
        }
        return world

    def test_grudge_accrues_while_the_player_is_the_sponsor(self, world):
        self._form_under_player_sponsorship(world)
        assert get_formation_grudge_nations(world) == ["Prussia"]
        assert get_formation_grudge_threat(world, budget=2) == 1

    def test_grudge_is_silent_when_no_player_link_exists(self, world):
        """The v0.1 France-scoped-scalar caveat, recorded in §11.10-8: an
        AI-erected formation costs the relation blows but feeds no
        France-targeted threat."""
        _author_aggrieved_formable(world, aggrieved=("Prussia",))
        process_formations(world)
        assert get_formation_record(world, "Austria")["sponsor"] == ""
        assert get_formation_grudge_nations(world) == []
        assert get_formation_grudge_threat(world, budget=2) == 0

    def test_grudge_ends_on_the_aggrieved_courts_vassalization(self, world):
        self._form_under_player_sponsorship(world)
        world.vassals["Prussia"] = {"lord": "France", "loyalty": 50}
        world.invalidate_bloc_members_cache()
        assert get_formation_grudge_nations(world) == []

    def test_budget_zero_yields_nothing(self, world):
        """The shared §5.8 cap: with the agenda family already at the cap,
        the formation family takes nothing."""
        self._form_under_player_sponsorship(world)
        assert get_formation_grudge_threat(world, budget=0) == 0
        assert get_formation_grudge_threat(world, budget=-1) == 0

    def test_the_two_grudge_families_never_stack_past_the_cap(self, world):
        from backend.game_logic.agendas import AGENDA_GRUDGE_CAP
        self._form_under_player_sponsorship(world)
        for budget in range(0, AGENDA_GRUDGE_CAP + 1):
            emitted = get_formation_grudge_threat(world, budget=budget)
            assert emitted + (AGENDA_GRUDGE_CAP - budget) <= AGENDA_GRUDGE_CAP

    def test_coalition_step_two_emits_a_named_source(self, world):
        """§11.9 requires the threat panel to NAME the grievance — one
        merged add_threat would destroy that, so both keys must survive."""
        from backend.game_logic.coalition import _calculate_formation_grudge_threat
        from backend.game_logic.diplomatic_ledger import _THREAT_SOURCE_LABELS
        self._form_under_player_sponsorship(world)
        assert _calculate_formation_grudge_threat(world, budget=2) == 1
        assert "formation_grudge" in _THREAT_SOURCE_LABELS
        assert "agenda_grudge" in _THREAT_SOURCE_LABELS

    def test_agenda_grudge_amount_is_unchanged_by_the_split(self, world):
        """The NA-3 pins must not move: `_calculate_agenda_grudge_threat`
        keeps clamping to the full cap on its own."""
        from backend.game_logic.agendas import AGENDA_GRUDGE_CAP
        from backend.game_logic.coalition import _calculate_agenda_grudge_threat
        import inspect
        source = inspect.getsource(_calculate_agenda_grudge_threat)
        assert f"min({AGENDA_GRUDGE_CAP}" not in source
        assert "AGENDA_GRUDGE_CAP" in source
        assert isinstance(_calculate_agenda_grudge_threat(world), int)


# ═══════════════════════ THE TWO CALL SITES (§11.10-2) ════════════════════

class TestCallSites:
    def test_advance_turn_runs_the_formation_poll(self, world):
        """Wiring pin (the NA-3 idiom): deleting process_formations from
        _advance_turn_internal must fail HERE, not only in helper tests."""
        _free_italy_with_the_peninsula(world)
        world.advance_turn()
        assert get_formation_record(world, "KingdomOfItaly") is not None
        assert any(e.get("type") == "nation_formed" for e in world.event_log)

    def test_the_poll_runs_before_the_shift_beat(self, world):
        """§11.10-2 ordering: the shift beat must announce the POST-
        formation deck entry, never the dead forming one."""
        order = []
        # Both call sites use function-local imports, so patching the
        # module attribute is what the tick actually resolves.
        from backend.game_logic import agendas as agendas_module
        from backend.game_logic import formations as formations_module
        real_shifts = agendas_module.process_agenda_shifts
        real_form = formations_module.process_formations

        def spy_shifts(w):
            order.append("shifts")
            return real_shifts(w)

        def spy_form(w):
            order.append("formations")
            return real_form(w)

        agendas_module.process_agenda_shifts = spy_shifts
        formations_module.process_formations = spy_form
        try:
            world.advance_turn()
        finally:
            agendas_module.process_agenda_shifts = real_shifts
            formations_module.process_formations = real_form

        assert order.index("formations") < order.index("shifts")

    def test_settlement_ratify_calls_the_poll(self, world):
        """The second call site (§11.10-2): a cession completed at the
        table proclaims the turn it happens, not on the next tick."""
        import inspect

        from backend.game_logic import settlement_ratify
        source = inspect.getsource(settlement_ratify)
        assert "process_formations(world)" in source, (
            "the ratify-path formation call site was removed"
        )
        # ...and it sits AFTER the cache invalidations, because agenda
        # activation reads the region control the clauses just moved.
        ratify_call = source.index("process_formations(world)")
        invalidate = source.index("invalidate_active_nations_cache()")
        assert invalidate < ratify_call


# ═══════════════════════ THE BEAT (§11.8 stages 1 and 4) ══════════════════

class TestTheBeat:
    def test_campaign_log_event_and_oneliner(self, world):
        from backend.campaign_log import CAMPAIGN_LOG_TYPES, format_event_oneliner
        assert "nation_formed" in CAMPAIGN_LOG_TYPES

        _free_italy_with_the_peninsula(world)
        process_formations(world)
        event = next(e for e in world.event_log
                     if e.get("type") == "nation_formed")
        assert event["nation"] == "KingdomOfItaly"
        line = format_event_oneliner(event)
        assert "Italy is proclaimed" in line
        assert "Kingdom of Italy is no more" in line

    def test_campaign_log_is_never_fogged(self, world):
        """Diplomacy has no fog — a proclamation is open court knowledge."""
        from backend.campaign_log import filter_campaign_log
        _free_italy_with_the_peninsula(world)
        process_formations(world)
        visible = filter_campaign_log(world.event_log, world)
        assert any(e.get("type") == "nation_formed" for e in visible)

    def test_dispatch_line_is_queued_high(self, world):
        from backend.game_logic.dispatch import (
            _DIPLOMATIC_EVENT_PRIORITY, _DIPLOMATIC_EVENT_TEMPLATES,
        )
        assert _DIPLOMATIC_EVENT_PRIORITY["nation_formed"] == "HIGH"
        assert "nation_formed" in _DIPLOMATIC_EVENT_TEMPLATES

        _free_italy_with_the_peninsula(world)
        process_formations(world)
        queued = [e for e in world.pending_dispatch_events
                  if e.get("type") == "nation_formed"]
        assert len(queued) == 1
        assert queued[0]["fog_rule"] == "always"   # diplomacy has no fog
        assert queued[0]["template_vars"]["nation"] == "Italy"
        assert queued[0]["template_vars"]["old_nation"] == "Kingdom of Italy"

    def test_notification_is_raised(self, world):
        _free_italy_with_the_peninsula(world)
        process_formations(world)
        pending = world.notifications.get_pending()
        formed = [n for n in pending if n["type"] == "nation_formed"]
        assert len(formed) == 1
        assert "Italy" in formed[0]["title"]

    def test_the_beat_names_the_aggrieved_courts(self, world):
        _author_aggrieved_formable(world, aggrieved=("Prussia",))
        process_formations(world)
        formed = [n for n in world.notifications.get_pending()
                  if n["type"] == "nation_formed"][0]
        assert "Prussia" in formed["message"]


# ═══════════════════════ SERIALIZATION (§11.1, one field) ═════════════════

class TestSerialization:
    def test_round_trip_preserves_the_latch(self, world):
        _free_italy_with_the_peninsula(world)
        process_formations(world)
        reloaded = WorldState.from_dict(world.to_dict())
        assert reloaded.nation_formations == world.nation_formations
        assert build_nation_display_overrides(reloaded) == {
            "KingdomOfItaly": "Italy",
        }

    def test_records_are_deep_copied_not_aliased(self, world):
        _free_italy_with_the_peninsula(world)
        process_formations(world)
        reloaded = WorldState.from_dict(world.to_dict())
        reloaded.nation_formations["KingdomOfItaly"]["sponsor"] = "Mars"
        assert world.nation_formations["KingdomOfItaly"]["sponsor"] == ""

    def test_pre_na6_saves_default_cleanly(self, world):
        data = world.to_dict()
        data.pop("nation_formations", None)
        reloaded = WorldState.from_dict(data)
        assert reloaded.nation_formations == {}
        assert build_nation_display_overrides(reloaded) == {}

    def test_null_value_defaults_cleanly(self, world):
        data = world.to_dict()
        data["nation_formations"] = None
        assert WorldState.from_dict(data).nation_formations == {}

    def test_the_record_shape(self, world):
        _free_italy_with_the_peninsula(world)
        process_formations(world)
        record = world.nation_formations["KingdomOfItaly"]
        assert set(record) == {"id", "sponsor", "turn"}
        assert record["id"] == "risorgimento"
        assert record["sponsor"] == ""
        assert record["turn"] == int(world.current_turn)


# ═══════════════════════ THE `forms` BLOCK + VALIDATOR ════════════════════

class TestFormsBlock:
    def test_flag_defaults_to_the_spaceless_display_name(self):
        block = get_forms_block({"forms": {"display_name": "United Provinces"}})
        assert block["flag"] == "UnitedProvinces"

    def test_a_nameless_block_is_not_formable(self):
        assert get_forms_block({"forms": {"display_name": "  "}}) is None
        assert get_forms_block({"forms": {}}) is None
        assert get_forms_block({"forms": "Italy"}) is None
        assert get_forms_block({}) is None


class TestValidator:
    """The synthetic scenarios below are deliberately minimal and therefore
    carry unrelated `runtime_support` errors. Every assertion here is
    scoped to the `.forms` PATH so it can only pass or fail for the reason
    it names — an overall `is_valid` assertion would be a false pin."""

    def _forms_findings(self, world, entry):
        scenario = {
            "scenario_name": "formable-test",
            "player_nation": "France",
            "regions": {
                name: {"name": name, "adjacent_regions": [],
                       "controller": region.controller}
                for name, region in list(world.regions.items())[:12]
            },
            "agendas": {"France": [entry]},
        }
        result = validate_scenario(scenario, check_adjacency=False)
        return (
            [e for e in result.errors if ".forms" in str(e.path)],
            [w for w in result.warnings if ".forms" in str(w.path)],
        )

    def _entry(self, world, **overrides):
        entry = {
            "id": "x", "type": "acquire_regions", "title": "X",
            "regions": [next(iter(world.regions))],
        }
        entry.update(overrides)
        return entry

    def test_shipped_scenario_still_validates(self):
        result = validate_scenario(str(SCENARIO_PATH), check_adjacency=False)
        assert result.is_valid, result.errors
        assert not [e for e in result.errors if ".forms" in str(e.path)]

    def test_a_well_formed_block_raises_nothing(self, world):
        errors, warnings = self._forms_findings(
            world, self._entry(world, forms={"display_name": "Nowhere"}))
        assert errors == [] and warnings == []

    def test_missing_display_name_is_an_error(self, world):
        errors, _ = self._forms_findings(
            world, self._entry(world, forms={"flag": "Nowhere"}))
        assert any("display_name" in str(e.message) for e in errors)

    def test_non_object_forms_is_an_error(self, world):
        errors, _ = self._forms_findings(
            world, self._entry(world, forms="Italy"))
        assert any("Must be an object" in str(e.message) for e in errors)

    def test_forms_on_a_posture_is_an_error(self, world):
        """A formable that can never fire is the dead promise GR9 forbids."""
        errors, _ = self._forms_findings(world, self._entry(
            world, type="guard_neutrality",
            forms={"display_name": "Nowhere"}))
        assert any("never reaches a satisfied state" in str(e.message)
                   for e in errors)

    def test_unknown_aggrieved_nation_warns_never_errors(self, world):
        errors, warnings = self._forms_findings(world, self._entry(
            world, forms={"display_name": "Nowhere",
                          "aggrieved": ["Atlantis"]}))
        assert errors == []
        assert any("Atlantis" in str(w.message) for w in warnings)

    def test_known_aggrieved_nations_do_not_warn(self, world):
        """The roster basis is VALID_NATIONS, not the locally-derived
        known_nations — a landless/marshal-less court (exactly the kind
        most likely to be aggrieved) must not warn spuriously."""
        errors, warnings = self._forms_findings(world, self._entry(
            world, forms={"display_name": "Nowhere",
                          "aggrieved": ["Prussia", "Russia"]}))
        assert errors == [] and warnings == []

    def test_malformed_aggrieved_list_is_an_error(self, world):
        errors, _ = self._forms_findings(world, self._entry(
            world, forms={"display_name": "Nowhere", "aggrieved": "Prussia"}))
        assert any("Must be a list" in str(e.message) for e in errors)

    def test_authored_roster_is_present_and_well_formed(self):
        world = WorldState.from_scenario(str(SCENARIO_PATH))
        italy = world.agendas["KingdomOfItaly"]
        holland = world.agendas["Holland"]
        assert get_forms_block(italy[0])["display_name"] == "Italy"
        assert get_forms_block(holland[0])["display_name"] == "United Netherlands"
        # §11.1-4: the post-formation goal must actually exist to fall to.
        assert italy[1]["id"] == "guard_the_peninsula"
        assert holland[1]["id"] == "merchants_peace"
        # Nothing else on the shipped roster forms.
        formable = [n for n, deck in world.agendas.items()
                    if any(get_forms_block(e) for e in deck)]
        assert sorted(formable) == ["Holland", "KingdomOfItaly"]


# ═══════════════════════ THE RESPONSE FIELD (§11.10-3) ════════════════════

class TestResponsePayload:
    def test_base_response_carries_the_overrides(self, world):
        from backend import main as main_module
        response = main_module.build_base_response(world)
        assert response["nation_display_overrides"] == {}
        assert response["nation_flag_overrides"] == {}

        _free_italy_with_the_peninsula(world)
        process_formations(world)
        response = main_module.build_base_response(world)
        assert response["nation_display_overrides"] == {"KingdomOfItaly": "Italy"}
        assert response["nation_flag_overrides"] == {"KingdomOfItaly": "Italy"}

    def test_extra_kwargs_cannot_clobber_the_overrides(self, world):
        """The field is stamped AFTER response.update(extra), because
        _build_result_response forwards every executor key into extra."""
        from backend import main as main_module
        _free_italy_with_the_peninsula(world)
        process_formations(world)
        response = main_module.build_base_response(
            world, nation_display_overrides={"KingdomOfItaly": "WRONG"})
        assert response["nation_display_overrides"] == {"KingdomOfItaly": "Italy"}

    def test_get_endpoints_carry_the_overrides_too(self):
        """§11.8 stage 3: a player who LOADS a save with formations and
        opens a ledger before issuing any command must not read the dead
        name. Pinned by source-scrape over the hand-rolled GET payloads."""
        import inspect

        from backend import main as main_module
        source = inspect.getsource(main_module)
        for endpoint in ('@app.get("/ledger")', '@app.get("/diplomatic_ledger")',
                         '@app.get("/marshal_overview")', '@app.get("/dispatch")',
                         '@app.get("/campaign_log")', '@app.get("/map_topology")',
                         '@app.get("/status")'):
            start = source.index(endpoint)
            body = source[start:start + 2400]
            assert "_attach_nation_identity_overrides" in body, (
                f"{endpoint} does not stamp the NA-6 identity overrides"
            )
