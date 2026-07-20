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
    apply_formation_names_to_history,
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

    def test_a_rump_state_cannot_proclaim_a_triumph(self, world):
        """REGRESSION (P2): the raw-deck scan bypasses `get_active_agenda`,
        which ranks the survival override ABOVE the deck — so the override
        must be re-applied here or a rump that happens to hold one listed
        province proclaims a triumph, banks the windfall, and takes up
        "Survival" on the same card. Formation is permanent, so it can
        never be undone. Holland's forming entry needs exactly ONE
        non-homeland province (Flanders), which makes this reachable."""
        from backend.game_logic.agendas import survival_override_active
        _free(world, "Holland")
        _hand_over(world, "Holland", ["Flanders"])
        # ...but the homeland is gone: Amsterdam (its capital) and Brabant.
        _hand_over(world, "Austria", ["Amsterdam", "Brabant"])
        assert survival_override_active(world, "Holland"), "setup control"

        assert process_formations(world) == []
        assert world.nation_formations == {}

        # Recover the homeland and the proclamation becomes legitimate.
        _hand_over(world, "Holland", ["Amsterdam", "Brabant"])
        assert not survival_override_active(world, "Holland")
        assert len(process_formations(world)) == 1

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

    def test_the_generic_label_row_survives_for_pre_na6d_saves(self, world):
        """A save written before the per-formation source keys carries a
        bare `formation_grudge` row; the static fallback must still name it.

        (This replaces a test that asserted on `coalition.
        _calculate_formation_grudge_threat` — a wrapper NA-6d left with no
        production caller, so the assertion pinned nothing. The real
        wiring pin is `test_coalition_step_two_emits_the_named_source`,
        which drives `process_coalition_turn` and reads the source key
        that actually reached `world.threat_sources_this_turn`.)
        """
        from backend.game_logic.diplomatic_ledger import (
            _THREAT_SOURCE_LABELS, _threat_source_label,
        )
        assert "formation_grudge" in _THREAT_SOURCE_LABELS
        assert "agenda_grudge" in _THREAT_SOURCE_LABELS
        assert (_threat_source_label(world, "formation_grudge")
                == "Nations raised from their lands")

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
        # `formed` is the explicit permanence latch: it declares what the
        # id/template inequality used to only imply, so an authoring
        # collision between a deck entry id and a formable template tag
        # can no longer un-latch a formation.
        assert set(record) == {"id", "sponsor", "turn", "formed"}
        assert record["id"] == "risorgimento"
        assert record["sponsor"] == ""
        assert record["turn"] == int(world.current_turn)
        assert record["formed"] is True


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


# ═══════════════════ NA-6b: THE PROCLAMATION (§11.8 stage 2) ══════════════

class TestProclamationCard:
    def test_the_card_is_queued_on_formation(self, world):
        _free_italy_with_the_peninsula(world)
        process_formations(world)
        card = world.nation_proclamation_popup
        assert card is not None
        assert card["display_name"] == "Italy"
        assert card["old_display_name"] == "Kingdom of Italy"
        assert card["flag_tag"] == "Italy"
        assert "ITALY stands" in card["proclamation"]

    def test_the_card_states_only_rewards_actually_received(self, world):
        """The cap can swallow the stability lift — the card must not
        claim a reward the world did not get."""
        _free_italy_with_the_peninsula(world)
        for name in ITALY_PROVINCES:
            world.regions[name].stability = 100
        process_formations(world)
        terms = world.nation_proclamation_popup["terms"]
        assert any("gold" in t for t in terms)
        assert not any("stability" in t for t in terms)

        world2 = WorldState.from_dict(world.to_dict())
        world2.nation_formations = {}
        world2.nation_proclamation_popup = None
        for name in ITALY_PROVINCES:
            world2.regions[name].stability = 50
        process_formations(world2)
        assert any("stability" in t
                   for t in world2.nation_proclamation_popup["terms"])

    def test_subtitle_is_perspective_aware(self, world):
        """§11.8 stage 2: witness vs author — same card, one line differs."""
        from backend.game_logic.formations import build_proclamation_card
        _free_italy_with_the_peninsula(world)
        process_formations(world)
        assert world.nation_proclamation_popup["subtitle"] == (
            "A new power takes its seat in Europe."
        )
        authored = build_proclamation_card(world, {
            "nation": "KingdomOfItaly", "old_display_name": "Kingdom of Italy",
            "display_name": "Italy", "flag_tag": "Italy", "blurb": "",
            "sponsor": world.player_nation, "aggrieved_display": [],
            "next_design": "", "gold": 2000, "stability_bonus": 2,
            "regions_lifted": 3, "turn": 1,
        })
        assert authored["subtitle"] == "By your hand."

    def test_the_card_carries_the_fury_line(self, world):
        _author_aggrieved_formable(world, aggrieved=("Prussia", "Russia"))
        process_formations(world)
        fury = world.nation_proclamation_popup["fury_line"]
        assert "Prussia" in fury and "Russia" in fury
        assert "declaration" in fury

    def test_no_fury_line_without_aggrieved_courts(self, world):
        _free_italy_with_the_peninsula(world)
        process_formations(world)
        assert world.nation_proclamation_popup["fury_line"] == ""

    def test_the_turn_is_an_int_for_godot(self, world):
        _free_italy_with_the_peninsula(world)
        process_formations(world)
        turn = world.nation_proclamation_popup["turn"]
        assert isinstance(turn, int) and not isinstance(turn, bool)


class TestPopupQueueSlot:
    def test_the_slot_and_its_response_key_exist(self):
        from backend.models.cooldown_manager import PopupQueue
        assert "proclamation_popup" in PopupQueue.PRIORITY_ORDER
        assert PopupQueue.RESPONSE_KEYS["proclamation_popup"] == (
            "nation_proclamation"
        )

    def test_a_landmark_outranks_mail_and_yields_to_crises(self):
        """§11.10-5: directly below vassal_rebellion_imminent_popup."""
        from backend.models.cooldown_manager import PopupQueue
        order = PopupQueue.PRIORITY_ORDER
        assert order.index("vassal_rebellion_imminent_popup") < order.index(
            "proclamation_popup")
        for lower in ("diplomatic_objection_popup", "pending_marshal_petition",
                      "incoming_proposal_popup"):
            assert order.index("proclamation_popup") < order.index(lower)

    def test_the_card_pops_under_its_response_key(self, world):
        _free_italy_with_the_peninsula(world)
        process_formations(world)
        ptype, key, data = world._popup_queue.pop_highest()
        assert ptype == "proclamation_popup"
        assert key == "nation_proclamation"
        assert data["display_name"] == "Italy"

    def test_the_card_survives_save_load(self, world):
        _free_italy_with_the_peninsula(world)
        process_formations(world)
        reloaded = WorldState.from_dict(world.to_dict())
        assert reloaded.nation_proclamation_popup["display_name"] == "Italy"

    def test_no_response_endpoint_exists(self):
        """Choice-less by design — Acknowledge is a client-side dismiss."""
        import inspect
        from backend import main as main_module
        source = inspect.getsource(main_module)
        assert "/nation_proclamation_response" not in source
        assert "/proclamation_response" not in source


class TestPopupCarryAcrossRebuild:
    """REGRESSION (second sweep, P1): the PL-14 safety net in
    `_respond_to_dialogue_sync` REBUILDS the response to pick up a
    newly-set proposal_result popup. The first build already ran
    `_include_popup_passthroughs`, which POPS the winning popup off the
    queue AND clears the world field — so the rebind destroyed it.

    That made the Proclamation 100% undeliverable on the settlement-ratify
    path, which is the ONE reason §11.10 decision 2 mandates that call
    site; and because the formation latch is permanent, it could never
    fire again. The defect is not NA-6-specific — it silently ate any
    popup type — so the carry is generic.
    """

    def test_a_popped_popup_survives_the_rebuild(self, world):
        from backend import main as main_module
        _free_italy_with_the_peninsula(world)
        process_formations(world)

        first = {}
        main_module._include_popup_passthroughs(first, world)
        assert first["nation_proclamation"]["display_name"] == "Italy"
        assert world.nation_proclamation_popup is None, (
            "the pop must have cleared the world slot — that is the trap"
        )

        carried = main_module._capture_popup_passthroughs(first)
        rebuilt = main_module.build_base_response(world)
        assert rebuilt.get("nation_proclamation") is None, "setup control"
        main_module._restore_popup_passthroughs(rebuilt, carried)
        assert rebuilt["nation_proclamation"]["display_name"] == "Italy"

    def test_the_carry_never_clobbers_a_fresh_popup(self, world):
        from backend import main as main_module
        carried = {"nation_proclamation": {"display_name": "STALE"}}
        response = {"nation_proclamation": {"display_name": "FRESH"}}
        main_module._restore_popup_passthroughs(response, carried)
        assert response["nation_proclamation"]["display_name"] == "FRESH"

    def test_the_dialogue_path_carries_popups(self):
        import inspect
        from backend import main as main_module
        source = inspect.getsource(main_module._respond_to_dialogue_sync)
        assert "_capture_popup_passthroughs" in source
        assert "_restore_popup_passthroughs" in source
        capture = source.index("_capture_popup_passthroughs")
        rebuild = source.index("response = build_base_response", capture)
        restore = source.index("_restore_popup_passthroughs")
        assert capture < rebuild < restore, (
            "capture must precede the rebuild and restore must follow it"
        )

    def test_capture_only_takes_real_popup_keys(self, world):
        from backend import main as main_module
        from backend.models.cooldown_manager import PopupQueue
        captured = main_module._capture_popup_passthroughs({
            "nation_proclamation": {"a": 1},
            "incoming_proposal": None,
            "message": "not a popup",
        })
        assert set(captured) == {"nation_proclamation"}
        assert set(captured) <= set(PopupQueue.RESPONSE_KEYS.values())


class TestTwoFormationsOneTick:
    """REGRESSION (found live during the NA-6b in-game review): a player
    who frees BOTH satellites and wins in Italy and Flanders on the same
    turn forms two nations in one tick — and the PopupQueue holds ONE slot
    per type. The second nation formed for real (latch, rewards, display
    override, campaign log, notification) while its once-per-campaign
    landmark was silently swallowed. Overflow rides a list, exactly like
    `vassal_rebellion_imminent_popups`."""

    def _form_both(self, world):
        _free(world, "KingdomOfItaly")
        _hand_over(world, "KingdomOfItaly", ITALY_PROVINCES)
        _free(world, "Holland")
        _hand_over(world, "Holland", DUTCH_PROVINCES)
        return process_formations(world)

    def test_both_nations_actually_form(self, world):
        assert len(self._form_both(world)) == 2
        assert sorted(world.nation_formations) == ["Holland", "KingdomOfItaly"]

    def test_the_second_card_lands_in_the_overflow(self, world):
        self._form_both(world)
        assert world.nation_proclamation_popup is not None
        assert len(world.nation_proclamation_popups) == 1
        shown = {world.nation_proclamation_popup["display_name"]}
        shown |= {c["display_name"] for c in world.nation_proclamation_popups}
        assert shown == {"Italy", "United Netherlands"}

    def test_both_cards_reach_the_player_across_two_responses(self, world):
        from backend import main as main_module
        self._form_both(world)

        first = {"enemy_phase": {"events": []}}
        main_module._apply_command_popup_contract(first, {}, world)
        second = {}
        main_module._include_popup_passthroughs(second, world)

        delivered = [first["nation_proclamation"]["display_name"],
                     second["nation_proclamation"]["display_name"]]
        assert sorted(delivered) == ["Italy", "United Netherlands"]
        assert world.nation_proclamation_popups == []
        assert world.nation_proclamation_popup is None

    def test_the_overflow_survives_save_load(self, world):
        self._form_both(world)
        reloaded = WorldState.from_dict(world.to_dict())
        assert len(reloaded.nation_proclamation_popups) == 1
        assert reloaded.nation_proclamation_popup is not None

    def test_the_overflow_is_empty_for_a_lone_formation(self, world):
        _free_italy_with_the_peninsula(world)
        process_formations(world)
        assert world.nation_proclamation_popups == []


class TestEnemyPhaseCarveOut:
    def test_the_card_is_not_deferred_behind_enemy_phase(self, world):
        """A formation almost always fires on the turn tick — the response
        carrying enemy_phase. Deferred, the Proclamation would surface a
        whole command later, long after the dispatch announced it."""
        from backend import main as main_module
        _free_italy_with_the_peninsula(world)
        process_formations(world)
        response = {"enemy_phase": {"events": []}}
        main_module._apply_command_popup_contract(response, {}, world)
        assert response["nation_proclamation"]["display_name"] == "Italy"
        assert world.nation_proclamation_popup is None, (
            "the card must be consumed, not left to re-fire"
        )

    def test_nothing_is_attached_when_no_formation_happened(self, world):
        from backend import main as main_module
        response = {"enemy_phase": {"events": []}}
        main_module._apply_command_popup_contract(response, {}, world)
        assert "nation_proclamation" not in response


# ═══════════════ NA-6b: NO DEAD NAME IN COMPOSED PROSE (§11.8-3) ══════════

class TestNoDeadNameInProse:
    """Found LIVE on the diplomatic ledger during the NA-6b visual check:
    Austria's design line still read "while Kingdom of Italy holds Milan"
    after Italy was proclaimed.

    The class of bug: `display_nation` is STATIC, so the backend bakes the
    dead name into the sentence — and because the result is already
    humanized (no raw `KingdomOfItaly` token survives), Godot's prose
    substitution cannot repair it downstream. Composed prose must resolve
    through `formations.formed_display_name`.
    """

    def _form_italy(self, world):
        _free_italy_with_the_peninsula(world)
        process_formations(world)
        world._agenda_cache = None

    def test_agenda_stance_line_names_the_formed_nation(self, world):
        before = build_agenda_payload("Austria", world)["stance_line"]
        assert "Kingdom of Italy" in before, "boot control"
        self._form_italy(world)
        after = build_agenda_payload("Austria", world)["stance_line"]
        assert "Kingdom of Italy" not in after
        assert "Italy holds Milan" in after

    def _at_peace(self, world, nation):
        for other in list(world.get_active_nations()):
            if other != nation:
                world.diplomatic_states[
                    world._make_diplo_key(nation, other)] = "PEACE"
        world.invalidate_bloc_members_cache()
        world._agenda_cache = None

    def test_the_shift_beat_names_the_formed_nation(self, world):
        from backend.game_logic.agendas import process_agenda_shifts
        self._form_italy(world)
        # A formed Italy still at war has NO active agenda (its post-
        # formation design is a peace posture), and the beat is correctly
        # silent then — peace is what makes the shift observable.
        self._at_peace(world, "KingdomOfItaly")
        world.nation_agenda_seen["KingdomOfItaly"] = "__stale__"
        world.pending_dispatch_events = []
        process_agenda_shifts(world)
        beats = [e for e in world.pending_dispatch_events
                 if e.get("type") == "agenda_shift"
                 and e["template_vars"].get("nation") in
                 ("Italy", "Kingdom of Italy")]
        assert beats, "no shift beat fired for the formed nation"
        assert beats[0]["template_vars"]["nation"] == "Italy"

    def test_the_violation_beat_names_the_formed_nation(self, world):
        """A formed Italy's own guard regions are the NA-3 trap surface."""
        from backend.game_logic.agendas import process_agenda_violations
        self._form_italy(world)
        self._at_peace(world, "KingdomOfItaly")   # activates the guard posture
        assert get_active_agenda("KingdomOfItaly", world).id == (
            "guard_the_peninsula")
        world.marshals["Ney"].location = "Rome"
        world.pending_dispatch_events = []
        process_agenda_violations(world)
        beats = [e for e in world.pending_dispatch_events
                 if e.get("type") == "agenda_violation"]
        assert beats, "the guard violation did not fire"
        assert beats[0]["template_vars"]["guard_holder"] == "Italy"

    def test_the_war_room_design_lines_name_the_formed_nation(self, world):
        from backend.game_logic.diplomatic_advisory import generate_advisory
        self._form_italy(world)
        advisory = generate_advisory(None, "assess_situation", world)
        blob = str(advisory)
        assert "Kingdom of Italy" not in blob, (
            "the war room still names the dead nation"
        )

    def test_the_campaign_log_renames_only_post_formation_entries(self, world):
        """REGRESSION (found live in the in-game review): the campaign log
        re-derives names from the stored raw tag via the STATIC
        display_nation, so a POST-formation entry read "The court of
        Kingdom of Italy takes up a new design" on a turn AFTER the
        proclamation. History before the formation must be left alone —
        the nation really was the Kingdom of Italy then — and the
        nation_formed line itself must keep BOTH names or it turns
        incoherent."""
        from backend.game_logic.formations import (
            apply_formation_names_to_history as rename,
        )
        world.current_turn = 5
        self._form_italy(world)
        formed_turn = world.nation_formations["KingdomOfItaly"]["turn"]
        assert formed_turn == 5

        after = rename(world, "The court of Kingdom of Italy takes up a "
                              "new design: Guard the Peninsula",
                       {"type": "agenda_shift", "turn": 7})
        assert "Kingdom of Italy" not in after
        assert "The court of Italy" in after

        before = rename(world, "The court of Kingdom of Italy takes up a "
                               "new design: Risorgimento",
                        {"type": "agenda_shift", "turn": 2})
        assert before.count("Kingdom of Italy") == 1, "history was rewritten"

        proclamation = rename(
            world, "Kingdom of Italy is no more - Italy is proclaimed",
            {"type": "nation_formed", "turn": 5})
        assert proclamation == "Kingdom of Italy is no more - Italy is proclaimed"

        # A generic post-formation line renames too, not just agenda arms.
        assert rename(world, "Milan captured by Kingdom of Italy",
                      {"type": "region_captured", "turn": 6}) == (
            "Milan captured by Italy")

    def test_the_campaign_log_endpoint_uses_the_history_helper(self):
        import inspect
        from backend import main as main_module
        source = inspect.getsource(main_module)
        start = source.index('@app.get("/campaign_log")')
        body = source[start:start + 2400]
        assert "_formations_history_names" in body

    def test_history_rename_is_inert_with_no_formations(self, world):
        from backend.game_logic.formations import (
            apply_formation_names_to_history as rename,
        )
        line = "The court of Kingdom of Italy takes up a new design"
        assert rename(world, line, {"type": "agenda_shift", "turn": 9}) == line

    def test_the_helper_is_a_no_op_for_unformed_nations(self, world):
        from backend.game_logic.formations import formed_display_name
        from backend.display_names import display_nation
        for nation in ("Austria", "KingdomOfItaly", "PapalStates", "Ottoman"):
            assert formed_display_name(world, nation) == display_nation(nation)


# ═══════════════════ NA-6b: THE GODOT SURFACES (source pins) ══════════════

GODOT = (
    Path(__file__).resolve().parents[1]
    / "godot-client" / "project-sovereign"
)


def _read(relative: str) -> str:
    return (GODOT / relative).read_text(encoding="utf-8")


class TestGodotWiring:
    def test_the_scene_and_script_exist_on_the_free_layer(self):
        scene = _read("scenes/proclamation_popup.tscn")
        assert "layer = 117" in scene
        assert "res://scripts/proclamation_popup.gd" in scene
        assert "AcknowledgeButton" in scene

    def test_layer_117_is_not_double_booked(self):
        """Measured at build time, not trusted from the spec."""
        import re
        layers = {}
        for path in (GODOT / "scenes").glob("*.tscn"):
            for match in re.finditer(r"^layer = (\d+)$",
                                     path.read_text(encoding="utf-8"),
                                     re.MULTILINE):
                layers.setdefault(int(match.group(1)), []).append(path.name)
        assert layers[117] == ["proclamation_popup.tscn"]

    def test_the_script_extends_popup_base_and_re_enables_its_button(self):
        script = _read("scripts/proclamation_popup.gd")
        assert script.startswith("extends PopupBase")
        assert "acknowledge_btn.disabled = false" in script, (
            "PopupBase.close_popup() permanently disables buttons — without "
            "the re-enable the SECOND proclamation opens uncloseable"
        )

    def test_the_script_routes_names_through_the_r7_chokepoints(self):
        script = _read("scripts/proclamation_popup.gd")
        assert "Utils.humanize_nation_keys_in_text" in script
        assert "Utils.nation_flag_path" in script

    def test_main_registers_the_popup_and_connects_dismissed(self):
        """`dismissed` MUST be connected even though the card is
        choice-less: it is shown from a seam that deliberately does not
        re-enable input, and this handler is what hands control back.
        Without it the terminal soft-locks on the first formation."""
        main_gd = _read("scripts/main.gd")
        assert 'dialog_manager.register("proclamation"' in main_gd
        assert "proclamation_popup.dismissed.connect(_on_proclamation_dismissed)" in main_gd
        assert "func _on_proclamation_dismissed" in main_gd
        handler = main_gd.index("func _on_proclamation_dismissed")
        assert "set_input_enabled(true)" in main_gd[handler:handler + 200]

    def test_the_card_is_not_a_pre_empting_route(self):
        """REGRESSION (two confirmed P1s): every entry in
        `_post_hud_response_routes` returns from `_on_command_result`
        BEFORE the enemy-phase dialog, the turn result text, strategic
        reports and the Morning Dispatch — and without re-enabling input.
        A formation fires inside advance_turn, so its response is exactly
        the one carrying `enemy_phase`. Routing the card there swallowed
        the whole end-turn tail AND soft-locked the terminal."""
        main_gd = _read("scripts/main.gd")
        start = main_gd.index("_post_hud_response_routes = [")
        table = main_gd[start:main_gd.index("]", start)]
        assert "proclamation" not in table, (
            "the Proclamation must never be a pre-empting response route"
        )
        assert "_route_proclamation_response" not in main_gd

    def test_the_card_is_stashed_before_any_routing(self):
        """The backend already popped the card off the PopupQueue, and the
        formation latch never re-fires it — so anything that drops the
        response loses the moment permanently. Stashing ahead of all
        routing also survives a higher-precedence modal (capture choice)
        winning the same response."""
        main_gd = _read("scripts/main.gd")
        assert "func _stash_proclamation" in main_gd
        assert "func _show_pending_proclamation" in main_gd
        result_fn = main_gd.index("func _on_command_result")
        stash = main_gd.index("_stash_proclamation(response)", result_fn)
        route = main_gd.index("_route_response_ui(response", result_fn)
        assert stash < route, "the stash must precede all routing"

    def test_every_control_returning_seam_routes_through_one_tail(self):
        """REGRESSION (second sweep): hanging the card off ONE seam
        stranded it on the normal case. `_on_enemy_phase_dismissed`
        returns early for strategic reports and redemption events — and
        formations are TRIGGERED BY CONQUEST, i.e. by marshals under
        standing orders, which is exactly what populates
        `strategic_reports`. Every seam that hands control back must end
        with the shared tail."""
        main_gd = _read("scripts/main.gd")
        assert "func _return_control_to_player" in main_gd
        for handler in ("func _on_enemy_phase_dismissed",
                        "func _on_strategic_report_dismissed",
                        "func _on_redemption_response"):
            start = main_gd.index(handler)
            end = main_gd.index("\nfunc ", start + 10)
            assert "_return_control_to_player()" in main_gd[start:end], (
                f"{handler} does not end with the shared control-return tail"
            )

    def test_the_shared_tail_shows_the_card_before_re_enabling_input(self):
        main_gd = _read("scripts/main.gd")
        start = main_gd.index("func _return_control_to_player")
        body = main_gd[start:main_gd.index("\nfunc ", start + 10)]
        assert body.index("_show_pending_proclamation()") < body.index(
            "set_input_enabled(true)")

    def test_the_command_tail_seam_is_last_not_first(self):
        """REGRESSION (second sweep): the seam used to sit ABOVE
        `_display_result`, the enemy-phase block, the dispatch and
        `_process_active_wars` — so a player who ratified a settlement saw
        the Proclamation and never learned the settlement was ratified,
        with the ended war still in the HUD. The card comes LAST."""
        main_gd = _read("scripts/main.gd")
        result_fn = main_gd.index("func _on_command_result")
        end = main_gd.index("\nfunc _display_result", result_fn)
        body = main_gd[result_fn:end]
        seam = body.index("_show_pending_proclamation()")
        for earlier in ("_display_result(response)", "_process_active_wars(response)",
                        '_show_pending_dispatch()'):
            assert body.index(earlier) < seam, (
                f"the Proclamation seam runs before {earlier}"
            )

    def test_a_queued_second_card_follows_the_first(self):
        """The dismissal handler chains, so two formations on one tick do
        not need an unrelated command to surface the second."""
        main_gd = _read("scripts/main.gd")
        start = main_gd.index("func _on_proclamation_dismissed")
        body = main_gd[start:main_gd.index("\nfunc ", start + 10)]
        assert "_show_pending_proclamation()" in body

    def test_the_popup_is_not_added_to_the_dialogue_dtype_whitelist(self):
        """§11.10-5 makes it a PopupQueue popup, NOT a dialogue — §11.7's
        'dtype whitelist' completion line is stale for this surface."""
        main_gd = _read("scripts/main.gd")
        start = main_gd.index("PROPOSAL_CONFIRM_DIALOGUE_TYPES")
        assert "proclamation" not in main_gd[start:start + 1400]

    def test_dialog_manager_records_the_layer(self):
        assert "117: proclamation_popup" in _read("scripts/dialog_manager.gd")


class TestGodotIdentityChokepoints:
    def test_utils_consults_the_override_first(self):
        utils = _read("scripts/utils.gd")
        assert "static var formation_overrides" in utils
        assert "static func set_formation_overrides" in utils
        # The override must be checked BEFORE the static map and before the
        # camelCase split, or a formed tag renders its authored name.
        start = utils.index("static func display_nation_name")
        body = utils[start:start + 400]
        assert body.index("formation_overrides.has(nation)") < body.index(
            "NATION_DISPLAY_NAMES.has(nation)")

    def test_the_flag_cache_is_flushed_when_the_store_changes(self):
        """utils.gd's _flag_path_cache is nation-keyed, caches the NEGATIVE
        result, and is otherwise never invalidated anywhere."""
        utils = _read("scripts/utils.gd")
        start = utils.index("static func set_formation_overrides")
        assert "_flag_path_cache.clear()" in utils[start:start + 700]

    def test_flag_lookup_resolves_the_formation_asset(self):
        utils = _read("scripts/utils.gd")
        start = utils.index("static func nation_flag_path")
        assert "formation_flag_overrides.has(nation)" in utils[start:start + 600]

    def test_the_formation_override_is_not_shadowed_by_the_static_map(self):
        """REGRESSION (P2): PROSE_NATION_KEY_SUBSTITUTIONS contains the
        literal key `KingdomOfItaly`. Running it first rewrites the token
        to "Kingdom of Italy", after which the formation loop's
        `contains(key)` can never match — which made the override branch
        DEAD for the entire v1 formable set. Order is load-bearing."""
        utils = _read("scripts/utils.gd")
        start = utils.index("static func humanize_nation_keys_in_text")
        body = utils[start:utils.index("static func _is_prose_safe_nation_key")]
        assert body.index("for key in formation_overrides") < body.index(
            "for key in PROSE_NATION_KEY_SUBSTITUTIONS"), (
            "the formation loop must run BEFORE the static prose map"
        )
        assert "if formation_overrides.has(key):" in body, (
            "a tag with a live override must be skipped by the static map"
        )
        assert body.count("for key in formation_overrides") == 1, (
            "duplicate override loop left behind"
        )

    def test_prose_substitution_skips_unsafe_single_word_tags(self):
        """`Normandy` and `Rome` are PROVINCE names on this map — a blind
        substring replace would corrupt every sentence naming them. This is
        the documented `Ottoman` exclusion, and NA-6c walks into it."""
        utils = _read("scripts/utils.gd")
        assert "_is_prose_safe_nation_key" in utils
        start = utils.index("static func humanize_nation_keys_in_text")
        assert "_is_prose_safe_nation_key(key)" in utils[start:start + 900]

    def test_api_client_adopts_overrides_before_the_callback(self):
        """One chokepoint sees every 200-OK body from every endpoint, and
        it must run BEFORE the callback so the response that proclaims a
        nation already renders under the new name."""
        api = _read("scripts/api_client.gd")
        assert "func _adopt_formation_overrides" in api
        assert api.index("_adopt_formation_overrides(json.data)") < api.index(
            "callback.call(json.data)")
        assert "Utils.set_formation_overrides" in api

    def test_absent_field_does_not_clear_the_store(self):
        api = _read("scripts/api_client.gd")
        start = api.index("func _adopt_formation_overrides")
        assert 'if not data.has("nation_display_overrides")' in api[start:start + 900]

    def test_the_new_flag_assets_are_importable_by_godot(self):
        """A .svg with no .import sibling does NOT resolve through
        ResourceLoader.exists(), so the flag silently fails to draw — found
        live: the first Proclamation opened with an empty flag frame."""
        for asset in ("Italy", "UnitedNetherlands"):
            base = GODOT / "assets" / "ui" / "heraldry" / f"{asset}.svg"
            assert base.exists(), f"missing {asset}.svg"
            assert base.with_suffix(".svg.import").exists(), (
                f"{asset}.svg has no .import sibling — Godot cannot load it"
            )

    def test_every_authored_formation_flag_has_an_asset(self):
        """No formable may proclaim under a missing flag."""
        world = WorldState.from_scenario(str(SCENARIO_PATH))
        seen = 0
        for deck in world.agendas.values():
            for entry in deck:
                block = get_forms_block(entry)
                if block is None:
                    continue
                seen += 1
                path = (GODOT / "assets" / "ui" / "heraldry"
                        / f"{block['flag']}.svg")
                assert path.exists(), (
                    f"{block['display_name']} forms with no flag asset "
                    f"({block['flag']}.svg)"
                )
        assert seen == 2   # Italy + United Netherlands


# ═════════════════════════════════════════════════════════════════════════
# NA-6c — CLASS C CARVE-OUT CLIENT CREATION (spec §11.4 / §11.10 dec. 6-7)
#
# The structural facts these tests exist to protect:
#   1. `process_formations` skips every vassal, and a carved client IS a
#      vassal from its first instant — so the carve must emit its own
#      Proclamation. `test_carve_proclaims_without_the_poll` is the pin.
#   2. Identity for a DECKLESS client resolves through the template, not a
#      deck entry. Without the template arm in `_forms_block_for_record`,
#      Normandy and the Roman Republic would silently have no display name,
#      no flag, and no standing §11.9 grudge — invisibly.
#      `test_deckless_client_still_has_an_identity` is the pin.
#   3. `nation_capitals` is NOT serialized; a carved capital is re-derived
#      on load. `test_carved_capital_survives_save_load` is the pin.
# ═════════════════════════════════════════════════════════════════════════

from backend.game_logic.ai_diplomacy import (          # noqa: E402
    _settlement_offer_build_terms,
)
from backend.game_logic.diplomatic_templates import (  # noqa: E402
    NATION_DESIRE_PROFILES,
    TALLEYRAND_COMMENTARY,
    annotate_peace_terms,
    calculate_raw_treaty_harshness,
)
from backend.game_logic.formations import (            # noqa: E402
    CARVE_LOYALTY,
    create_client_nation,
    get_template,
    get_template_identity,
    template_provinces,
)
from backend.game_logic.settlement_ratify import (     # noqa: E402
    _apply_settlement_terms,
)
from backend.game_logic.settlement_presentation import (  # noqa: E402
    build_settlement_review,
)
from backend.game_logic.settlement_validation import (  # noqa: E402
    evaluate_create_client_eligibility,
    validate_settlement_terms,
)
from backend.nation_config import NATION_POWER_TIERS   # noqa: E402

CARVE_TAGS = ("DuchyOfWarsaw", "Normandy", "RomanRepublic")


def _war(world, a, b):
    """A war instance placing `a` and `b` on opposite sides."""
    for instance in (getattr(world, "war_instances", {}) or {}).values():
        if not isinstance(instance, dict):
            continue
        att = set(instance.get("attackers") or [])
        dfd = set(instance.get("defenders") or [])
        if (a in att and b in dfd) or (a in dfd and b in att):
            return instance
    return {
        "attackers": [a], "defenders": [b],
        "diplo_key_meta": {world._make_diplo_key(a, b): {"pair_status": "war"}},
    }


def _at_war(world, a, b):
    from backend.game_logic.diplomacy import set_diplomatic_state
    if world.get_diplomatic_state(a, b) != "WAR":
        set_diplomatic_state(world, a, b, "WAR", "test_na6c")
    world.invalidate_active_nations_cache()
    return _war(world, a, b)


def _carve_ready(world, template_id, court, carver):
    """Put `carver` in a position to carve `template_id` out of `court`."""
    war_instance = _at_war(world, carver, court)
    _hand_over(world, carver,
               template_provinces(get_template(world, template_id)))
    return war_instance


class TestCarveBootZero:
    def test_no_template_tag_exists_at_boot(self, world):
        """§11.4: 'no template tag exists at boot — pinned.'"""
        active = set(world.get_active_nations())
        for tag in CARVE_TAGS:
            assert tag not in active
            assert tag not in world.vassals
            assert tag not in world.nation_capitals

    def test_the_catalogue_is_authored_but_inert(self, world):
        assert set(world.formable_nations) == set(CARVE_TAGS)
        assert world.nation_formations == {}

    def test_catalogue_survives_save_load(self, world):
        reloaded = WorldState.from_dict(world.to_dict())
        assert set(reloaded.formable_nations) == set(CARVE_TAGS)
        assert (template_provinces(get_template(reloaded, "DuchyOfWarsaw"))
                == ["Posen"])


class TestCarveEligibility:
    def test_the_player_may_carve_the_defeated(self, world):
        war_instance = _carve_ready(world, "DuchyOfWarsaw", "Prussia", "France")
        result = evaluate_create_client_eligibility(
            world, war_instance=war_instance, template_id="DuchyOfWarsaw",
            from_court="Prussia", carver="France")
        assert result["eligible"] is True

    def test_soil_must_be_HELD_before_it_can_be_carved(self, world):
        war_instance = _at_war(world, "France", "Prussia")
        assert world.regions["Posen"].controller == "Prussia"
        result = evaluate_create_client_eligibility(
            world, war_instance=war_instance, template_id="DuchyOfWarsaw",
            from_court="Prussia", carver="France")
        assert result["eligible"] is False
        assert result["refusal_code"] == "carve_provinces_not_held"
        assert result["disabled_reason_display"]

    def test_you_cannot_carve_a_client_out_of_a_THIRD_partys_soil(self, world):
        """§11.4's second half: holding the province is not enough — it must
        have BELONGED to the court paying the price. France holding Posen
        cannot carve it out of AUSTRIA."""
        war_instance = _at_war(world, "France", "Austria")
        _hand_over(world, "France", ["Posen"])
        result = evaluate_create_client_eligibility(
            world, war_instance=war_instance, template_id="DuchyOfWarsaw",
            from_court="Austria", carver="France")
        assert result["eligible"] is False
        assert result["refusal_code"] == "carve_not_defeated_soil"

    def test_you_cannot_carve_your_own_homeland(self, world):
        """Normandy starts FRENCH, so France can never be the carver of it —
        the same predicate that blocks an ally's soil."""
        war_instance = _at_war(world, "France", "Austria")
        result = evaluate_create_client_eligibility(
            world, war_instance=war_instance, template_id="Normandy",
            from_court="Austria", carver="France")
        assert result["eligible"] is False
        assert result["refusal_code"] == "carve_not_defeated_soil"

    def test_a_tag_already_standing_cannot_be_erected_twice(self, world):
        war_instance = _carve_ready(world, "DuchyOfWarsaw", "Prussia", "France")
        create_client_nation(world, "DuchyOfWarsaw", "France",
                             ceded_from="Prussia")
        result = evaluate_create_client_eligibility(
            world, war_instance=war_instance, template_id="DuchyOfWarsaw",
            from_court="Prussia", carver="France")
        assert result["eligible"] is False
        assert result["refusal_code"] == "carve_tag_already_exists"

    def test_erasing_a_state_needs_a_decisive_victory(self, world):
        """Q2 / §11.10 dec. 7: Rome is the Papal States' ONLY province, so
        the carve is also their elimination. That is allowed — but only at
        the same war score `territory_cede` demands, and stated OUT LOUD
        here rather than silently dropped at ratification."""
        war_instance = _carve_ready(
            world, "RomanRepublic", "PapalStates", "France")
        key = world._make_diplo_key("France", "PapalStates")
        world.war_scores[key] = 40
        blocked = evaluate_create_client_eligibility(
            world, war_instance=war_instance, template_id="RomanRepublic",
            from_court="PapalStates", carver="France")
        assert blocked["eligible"] is False
        assert blocked["refusal_code"] == "carve_total_annexation_blocked"
        assert "decisive" in blocked["disabled_reason_display"].lower()
        world.war_scores[key] = 95
        allowed = evaluate_create_client_eligibility(
            world, war_instance=war_instance, template_id="RomanRepublic",
            from_court="PapalStates", carver="France")
        assert allowed["eligible"] is True


class TestCarveCreatesANation:
    def test_the_full_birth(self, world):
        _carve_ready(world, "DuchyOfWarsaw", "Prussia", "France")
        create_client_nation(world, "DuchyOfWarsaw", "France",
                             ceded_from="Prussia")
        assert "DuchyOfWarsaw" in world.get_active_nations()
        assert world.regions["Posen"].controller == "DuchyOfWarsaw"
        row = world.vassals["DuchyOfWarsaw"]
        assert row["lord"] == "France"
        assert row["loyalty"] == CARVE_LOYALTY
        assert row["carved_from"] == "Prussia"
        assert world.get_nation_capital("DuchyOfWarsaw") == "Posen"
        assert world.nation_gold["DuchyOfWarsaw"] == 500
        assert world.diplomatic_states[
            world._make_diplo_key("DuchyOfWarsaw", "France")] == "VASSAL"

    def test_shape_parity_with_a_boot_authored_satellite(self, world):
        """§11.10 dec. 6: the new tag must appear in every world-level
        structure the boot-authored satellite KingdomOfItaly appears in.
        Derived from the LIVE boot world so the pin cannot drift as new
        nation-keyed state is added."""
        _carve_ready(world, "DuchyOfWarsaw", "Prussia", "France")
        create_client_nation(world, "DuchyOfWarsaw", "France",
                             ceded_from="Prussia")
        missing = []
        for attr in sorted(vars(world)):
            if attr.startswith("_"):
                continue
            value = getattr(world, attr)
            if isinstance(value, (dict, list)) and "KingdomOfItaly" in value:
                if "DuchyOfWarsaw" not in value:
                    missing.append(attr)
        assert missing == [], (
            f"carved client absent from world state a boot satellite "
            f"occupies: {missing}"
        )

    def test_the_newborn_does_not_proclaim_survival_over_its_own_erection(
            self, world):
        """Its provinces ARE its homeland, so `survival_override_active`
        has real input — but holding its capital keeps it False."""
        from backend.game_logic.agendas import survival_override_active
        _carve_ready(world, "DuchyOfWarsaw", "Prussia", "France")
        create_client_nation(world, "DuchyOfWarsaw", "France",
                             ceded_from="Prussia")
        assert world.nation_starting_regions["DuchyOfWarsaw"] == ["Posen"]
        assert survival_override_active(world, "DuchyOfWarsaw") is False
        world.regions["Posen"].controller = "Prussia"
        world.invalidate_active_nations_cache()
        assert survival_override_active(world, "DuchyOfWarsaw") is True

    def test_a_missing_template_province_fails_LOUDLY(self, world):
        world.formable_nations["DuchyOfWarsaw"]["provinces"] = ["Atlantis"]
        with pytest.raises(ValueError, match="Atlantis"):
            create_client_nation(world, "DuchyOfWarsaw", "France")

    def test_unknown_template_is_a_no_op_not_a_crash(self, world):
        assert create_client_nation(world, "Ruritania", "France") is None


class TestCarveIdentity:
    def test_deckless_client_still_has_an_identity(self, world):
        """The PREFLIGHT trap: `_forms_block_for_record` resolves identity
        by scanning the nation's DECK. Normandy has no deck at all, so
        without the template arm this returns None and the client silently
        has no name, no flag and no grudge."""
        _carve_ready(world, "Normandy", "France", "Britain")
        create_client_nation(world, "Normandy", "Britain", ceded_from="France")
        assert world.agendas.get("Normandy") in (None, [])
        identity = get_display_identity(world, "Normandy")
        assert identity == {"display_name": "Duchy of Normandy",
                            "flag_tag": "Normandy"}
        assert build_nation_display_overrides(
            world)["Normandy"] == "Duchy of Normandy"
        assert build_nation_flag_overrides(world)["Normandy"] == "Normandy"

    def test_carved_capital_survives_save_load(self, world):
        """`nation_capitals` is not serialized (it is rebuilt at
        construction and excluded from the enforcement gate). A carved
        capital must be re-derived on load or the client silently pays -1
        DP every turn forever."""
        _carve_ready(world, "DuchyOfWarsaw", "Prussia", "France")
        create_client_nation(world, "DuchyOfWarsaw", "France",
                             ceded_from="Prussia")
        reloaded = WorldState.from_dict(world.to_dict())
        assert reloaded.get_nation_capital("DuchyOfWarsaw") == "Posen"
        assert get_display_identity(reloaded, "DuchyOfWarsaw") == {
            "display_name": "Duchy of Warsaw", "flag_tag": "DuchyOfWarsaw"}

    def test_the_client_deck_is_installed_but_dormant(self, world):
        _carve_ready(world, "DuchyOfWarsaw", "Prussia", "France")
        create_client_nation(world, "DuchyOfWarsaw", "France",
                             ceded_from="Prussia")
        assert [e["id"] for e in world.agendas["DuchyOfWarsaw"]] == [
            "commonwealth_restored", "guard_the_vistula"]
        # §3.2: a client never activates its deck while it answers to a lord.
        assert get_active_agenda("DuchyOfWarsaw", world) is None


class TestCarveProclamation:
    def test_carve_proclaims_without_the_poll(self, world):
        """A carved client is a vassal, and `process_formations` skips every
        vassal — so the poll can NEVER announce a creation. The carve emits
        the landmark itself."""
        _carve_ready(world, "DuchyOfWarsaw", "Prussia", "France")
        create_client_nation(world, "DuchyOfWarsaw", "France",
                             ceded_from="Prussia")
        card = world.nation_proclamation_popup
        assert card is not None
        assert card["display_name"] == "Duchy of Warsaw"
        # The poll, run afterwards, must add nothing and re-fire nothing.
        assert process_formations(world) == []

    def test_nothing_is_no_more_when_a_nation_is_CREATED(self, world):
        """A carve kills nothing. Every 'X is no more' surface must branch
        on the empty `old_display_name` — the card, the notification, and
        the campaign-log one-liner."""
        from backend.campaign_log import format_event_oneliner
        _carve_ready(world, "DuchyOfWarsaw", "Prussia", "France")
        create_client_nation(world, "DuchyOfWarsaw", "France",
                             ceded_from="Prussia")
        card = world.nation_proclamation_popup
        assert card["old_display_name"] == ""
        assert "is no more" not in card["proclamation"]
        notices = [n for n in world.notifications.get_pending()
                   if "Proclaimed" in str(n.get("title", ""))]
        assert notices, "the Proclamation raised no notification"
        assert "is no more" not in str(notices[0].get("message", ""))
        event = [e for e in world.event_log
                 if e.get("type") == "nation_formed"][-1]
        assert "is no more" not in format_event_oneliner(event)

    def test_the_author_reads_by_your_hand(self, world):
        _carve_ready(world, "DuchyOfWarsaw", "Prussia", "France")
        create_client_nation(world, "DuchyOfWarsaw", "France",
                             ceded_from="Prussia")
        assert world.nation_proclamation_popup["subtitle"] == "By your hand."

    def test_the_witness_reads_a_new_power(self, world):
        """GR5: an AI erecting a client against another AI still proclaims —
        diplomacy has no fog — but the player is a witness, not the author."""
        _carve_ready(world, "DuchyOfWarsaw", "Prussia", "Austria")
        create_client_nation(world, "DuchyOfWarsaw", "Austria",
                             ceded_from="Prussia")
        card = world.nation_proclamation_popup
        assert card["subtitle"] == "A new power takes its seat in Europe."

    def test_the_card_states_the_terms_of_dependence(self, world):
        _carve_ready(world, "DuchyOfWarsaw", "Prussia", "France")
        create_client_nation(world, "DuchyOfWarsaw", "France",
                             ceded_from="Prussia")
        terms = " ".join(world.nation_proclamation_popup["terms"])
        assert "500 gold" in terms
        assert "satellite" in terms and str(CARVE_LOYALTY) in terms

    def test_the_aggrieved_courts_are_struck_and_named(self, world):
        """§11.9 for a Class C template: the blow reads the TEMPLATE's
        aggrieved list, and strikes both the new state and its sponsor."""
        _carve_ready(world, "RomanRepublic", "PapalStates", "France")
        world.war_scores[world._make_diplo_key("France", "PapalStates")] = 95
        before = world.nation_relations.get(
            world._make_diplo_key("Austria", "France"), 0)
        create_client_nation(world, "RomanRepublic", "France",
                             ceded_from="PapalStates")
        card = world.nation_proclamation_popup
        assert "Austria" in card["fury_line"] and "Spain" in card["fury_line"]
        assert world.nation_relations[
            world._make_diplo_key("Austria", "RomanRepublic")
        ] == FORMATION_AGGRIEVED_RELATION_PENALTY
        after = world.nation_relations[
            world._make_diplo_key("Austria", "France")]
        assert after == max(-100, before + FORMATION_AGGRIEVED_RELATION_PENALTY)
        assert "Austria" in get_formation_grudge_nations(world)


class TestCarveThroughRatification:
    def test_the_player_carve_lands_through_the_real_apply_path(self, world):
        war_instance = _carve_ready(world, "DuchyOfWarsaw", "Prussia", "France")
        terms = [
            {"type": "peace"},
            {"type": "create_client", "from": "Prussia", "to": "France",
             "tag": "DuchyOfWarsaw", "provinces": ["Posen"],
             "client_display_name": "Duchy of Warsaw"},
        ]
        assert validate_settlement_terms(
            terms, world=world, war_instance=war_instance)["valid"] is True
        applied = _apply_settlement_terms(world, settlement_terms=terms)
        carve = [c for c in applied if c["type"] == "create_client"]
        assert len(carve) == 1
        assert carve[0]["loyalty_after"] == CARVE_LOYALTY
        assert "Duchy of Warsaw" in carve[0]["pair_state_transition"]
        assert world.regions["Posen"].controller == "DuchyOfWarsaw"

    def test_carving_a_one_province_polity_composes_with_its_elimination(
            self, world):
        """Section 11.2's pinned interplay: Rome IS the Papal capital and
        their only province, so taking it erases the Papal States - and the
        Roman Republic must still be erected on the same soil in the same
        settlement, with the elimination announced EXACTLY ONCE.

        Driven through `capture_region`, the real conquest path. The earlier
        version of this test wrote `region.controller` directly, which
        bypassed `capture_region`'s own R81 elimination - so it "passed"
        only by making the carve arm do work that in a real campaign has
        already happened, and it hid a duplicate-announcement bug. Carve
        eligibility REQUIRES the carver to already hold every template
        province, so by construction the court is landless BEFORE the carve:
        the elimination belongs to the conquest, and the carve must compose
        with it rather than re-fire it.
        """
        _at_war(world, "France", "PapalStates")
        world.capture_region("Rome", "France")
        assert "PapalStates" not in world.get_active_nations()
        eliminations = [e for e in world.event_log
                        if e.get("type") == "nation_eliminated"
                        and e.get("nation") == "PapalStates"]
        assert len(eliminations) == 1

        world.war_scores[world._make_diplo_key("France", "PapalStates")] = 95
        terms = [{"type": "create_client", "from": "PapalStates",
                  "to": "France", "tag": "RomanRepublic",
                  "provinces": ["Rome"],
                  "client_display_name": "Roman Republic"}]
        applied = _apply_settlement_terms(world, settlement_terms=terms)
        assert [c["type"] for c in applied] == ["create_client"]
        assert world.regions["Rome"].controller == "RomanRepublic"
        assert "RomanRepublic" in world.get_active_nations()
        assert "PapalStates" not in world.get_active_nations()
        # The landmark fired; the elimination did NOT fire a second time.
        assert any(e.get("type") == "nation_formed" for e in world.event_log)
        eliminations = [e for e in world.event_log
                        if e.get("type") == "nation_eliminated"
                        and e.get("nation") == "PapalStates"]
        assert len(eliminations) == 1, (
            "the carve re-announced an elimination that the conquest had "
            "already reported")

    def test_a_carve_never_re_announces_an_existing_elimination(self, world):
        """The duplicate-announcement regression, isolated: a package that
        both finishes off a court and carves a client out of soil taken from
        it must report the elimination once, not twice."""
        _at_war(world, "France", "PapalStates")
        world.capture_region("Rome", "France")
        before = len([e for e in world.event_log
                      if e.get("type") == "nation_eliminated"])
        _apply_settlement_terms(world, settlement_terms=[
            {"type": "create_client", "from": "PapalStates", "to": "France",
             "tag": "RomanRepublic", "provinces": ["Rome"]}])
        after = len([e for e in world.event_log
                     if e.get("type") == "nation_eliminated"])
        assert after == before

    def test_a_province_cannot_be_both_ceded_and_carved(self, world):
        """GAP G1: a carve's soil rides the TEMPLATE, so the region
        double-promise check could not see it. Whichever apply-step ran
        second used to silently win."""
        war_instance = _carve_ready(world, "DuchyOfWarsaw", "Prussia", "France")
        terms = [
            {"type": "create_client", "from": "Prussia", "to": "France",
             "tag": "DuchyOfWarsaw", "provinces": ["Posen"]},
            {"type": "territory_cede", "from": "Prussia", "to": "France",
             "region": "Posen"},
        ]
        result = validate_settlement_terms(
            terms, world=world, war_instance=war_instance)
        assert result["valid"] is False
        assert result["error"] == "carve_region_double_promised"
        assert result["disabled_reason_display"]

    def test_the_apply_arm_re_verifies_live_control(self, world):
        """VS-5's lesson: clauses apply in submitted order with no per-type
        phasing, so an earlier clause can move the soil out from under the
        carve. The arm must re-check rather than trust validation."""
        _carve_ready(world, "DuchyOfWarsaw", "Prussia", "France")
        terms = [
            {"type": "territory_cede", "from": "France", "to": "Austria",
             "region": "Posen"},
            {"type": "create_client", "from": "Prussia", "to": "France",
             "tag": "DuchyOfWarsaw", "provinces": ["Posen"]},
        ]
        applied = _apply_settlement_terms(world, settlement_terms=terms)
        assert [c["type"] for c in applied] == ["territory_cede"]
        assert "DuchyOfWarsaw" not in world.get_active_nations()


class TestCarveGR5TheNormandyMirror:
    def test_an_ai_victor_offers_to_carve_the_players_homeland(self, world):
        """§11.7: 'an AI victor offers the carve against France and the
        player can accept/reject through the normal incoming surface.'"""
        _at_war(world, "Britain", "France")
        _hand_over(world, "Britain", ["Normandy"])
        terms = _settlement_offer_build_terms(
            player="France", proposer_nation="Britain", war_age_turns=6,
            player_war_score=-80, world=world)
        carve = [t for t in terms if t.get("type") == "create_client"]
        assert len(carve) == 1
        assert carve[0]["from"] == "France"
        assert carve[0]["to"] == "Britain"
        assert carve[0]["tag"] == "Normandy"
        assert carve[0]["client_display_name"] == "Duchy of Normandy"

    def test_an_even_war_never_carries_a_carve(self, world):
        _at_war(world, "Britain", "France")
        _hand_over(world, "Britain", ["Normandy"])
        terms = _settlement_offer_build_terms(
            player="France", proposer_nation="Britain", war_age_turns=6,
            player_war_score=0, world=world)
        assert not [t for t in terms if t.get("type") == "create_client"]

    def test_a_losing_ai_never_carves(self, world):
        """The player winning must not hand the AI a client state."""
        _at_war(world, "Britain", "France")
        _hand_over(world, "Britain", ["Normandy"])
        terms = _settlement_offer_build_terms(
            player="France", proposer_nation="Britain", war_age_turns=6,
            player_war_score=80, world=world)
        assert not [t for t in terms if t.get("type") == "create_client"]

    def test_the_ai_cannot_offer_soil_it_does_not_hold(self, world):
        _at_war(world, "Britain", "France")
        assert world.regions["Normandy"].controller == "France"
        terms = _settlement_offer_build_terms(
            player="France", proposer_nation="Britain", war_age_turns=6,
            player_war_score=-80, world=world)
        assert not [t for t in terms if t.get("type") == "create_client"]

    def test_the_ai_carve_lands_against_the_player(self, world):
        _carve_ready(world, "Normandy", "France", "Britain")
        terms = [{"type": "create_client", "from": "France", "to": "Britain",
                  "tag": "Normandy", "provinces": ["Normandy"],
                  "client_display_name": "Duchy of Normandy"}]
        _apply_settlement_terms(world, settlement_terms=terms)
        assert world.regions["Normandy"].controller == "Normandy"
        assert world.vassals["Normandy"]["lord"] == "Britain"
        # The player is the VICTIM here, never the author.
        assert world.nation_proclamation_popup["subtitle"] != "By your hand."


class TestCarveIsPricedAndLegible:
    def test_a_carve_is_never_free_to_the_ai(self, world):
        """The G4F-1 bug class: an unregistered clause type falls through
        the harshness accumulator unmatched and prices at ZERO."""
        clause = {"type": "create_client", "from": "Prussia", "to": "France",
                  "tag": "DuchyOfWarsaw", "provinces": ["Posen"]}
        assert calculate_raw_treaty_harshness({"clauses": [clause]}) > 0

    def test_a_carve_costs_more_than_a_cession_and_less_than_vassalage(self):
        carve = calculate_raw_treaty_harshness({"clauses": [
            {"type": "create_client", "from": "a", "to": "b", "tag": "X",
             "provinces": ["P"]}]})
        cession = calculate_raw_treaty_harshness({"clauses": [
            {"type": "territory_cede", "from": "a", "to": "b",
             "region": "P"}]})
        vassalage = calculate_raw_treaty_harshness({"clauses": [
            {"type": "vassalage", "from": "a", "to": "b"}]})
        assert cession < carve < vassalage

    def test_harshness_scales_with_the_provinces_taken(self):
        one = calculate_raw_treaty_harshness({"clauses": [
            {"type": "create_client", "from": "a", "to": "b", "tag": "X",
             "provinces": ["P"]}]})
        three = calculate_raw_treaty_harshness({"clauses": [
            {"type": "create_client", "from": "a", "to": "b", "tag": "X",
             "provinces": ["P", "Q", "R"]}]})
        assert three > one

    def test_both_harshness_dialects_price_the_carve(self):
        """Registering only the clauses dialect leaves the demands dialect
        pricing at zero — exactly the shipped G4F-1 gold_indemnity bug."""
        demand = {"type": "create_client", "from": "a", "to": "b",
                  "tag": "X", "provinces": ["P"]}
        assert calculate_raw_treaty_harshness({"demands": [demand]}) > 0

    def test_the_incoming_clause_line_names_the_client_and_the_soil(self):
        """§11.6-3: 'Britain proposes to erect the Duchy of Normandy from
        your provinces: Normandy' — never a raw template tag."""
        clause = {"type": "create_client", "from": "France", "to": "Britain",
                  "tag": "Normandy", "provinces": ["Normandy"],
                  "client_display_name": "Duchy of Normandy"}
        label = annotate_peace_terms(
            {"clauses": [clause]}, "Britain", "France")[0]["display_label"]
        assert "Britain erects" in label
        assert "Duchy of Normandy" in label
        assert "Normandy" in label
        assert "out of France" in label

    def test_the_clause_line_direction_is_read_from_the_clause(self):
        """The generic annotate fallback passes proposer/target positionally
        and printed the sentence BACKWARDS for a carve."""
        clause = {"type": "create_client", "from": "Prussia", "to": "France",
                  "tag": "DuchyOfWarsaw", "provinces": ["Posen"],
                  "client_display_name": "Duchy of Warsaw"}
        row = annotate_peace_terms(
            {"clauses": [clause]}, "France", "Prussia")[0]
        assert row["from_nation"] == "Prussia"
        assert row["to_nation"] == "France"
        assert row["display_label"].startswith("France erects")

    def test_no_raw_template_tag_reaches_the_player(self):
        from backend.game_logic.settlement_presentation import _term_display
        clause = {"type": "create_client", "from": "Prussia", "to": "France",
                  "tag": "DuchyOfWarsaw", "provinces": ["Posen"],
                  "client_display_name": "Duchy of Warsaw"}
        line = _term_display(clause)
        assert "DuchyOfWarsaw" not in line
        assert "Duchy of Warsaw" in line and "Posen" in line

    def test_the_carved_court_scores_it_as_a_loss_not_a_white_peace(
            self, world):
        """GAP G2: `agenda_settlement_mod` gated on the territory family, so
        a court whose design province was CARVED away scored the package as
        indifferently as a white peace."""
        from backend.game_logic.agendas import agenda_settlement_mod
        # Austria's live design is `redeem_italy` [Milan, Piedmont, Savoy].
        # Give it Milan so the design is HELD-but-unmet, then carve Milan
        # away: that is the ENTRENCH case.
        _hand_over(world, "Austria", ["Milan"])
        carve = {"type": "create_client", "from": "Austria", "to": "France",
                 "tag": "DuchyOfWarsaw", "provinces": ["Milan"]}
        cede = {"type": "territory_cede", "from": "Austria", "to": "France",
                "region": "Milan"}
        # The whole point of GAP G2: a carve must score like the cession it
        # effectively is, not like a white peace.
        assert agenda_settlement_mod("Austria", [carve], world) < 0
        assert (agenda_settlement_mod("Austria", [carve], world)
                == agenda_settlement_mod("Austria", [cede], world))


class TestCarveAuthoringSurface:
    def _rows(self, world, court, carver="France"):
        from backend.game_logic.settlement_staging import (
            _court_demand_suggestions,
        )
        war_instance = _at_war(world, carver, court)
        rows = _court_demand_suggestions(
            world,
            court=court,
            direction="demand",
            war_id="w",
            draft_key="d",
            war_instance=war_instance,
            proposer_side_participants=[carver],
            proposer_holdings=set(world.get_nation_regions(carver)),
            proposer_leader=carver,
            settlement_terms=[],
            promised_regions=set(),
            treasury_remaining=int(world.nation_gold.get(carver, 0)),
            income_cache={},
        )
        flat = rows[0] if isinstance(rows, tuple) else rows
        return [s for s in flat if s.get("clause_type") == "create_client"]

    def test_an_unavailable_carve_is_SHOWN_with_its_gate_terms(self, world):
        """§11.6-1 honest availability: never a silent absence. France does
        not hold Posen, so the row appears greyed with what is missing."""
        rows = self._rows(world, "Prussia")
        warsaw = [r for r in rows
                  if r["action_params"]["tag"] == "DuchyOfWarsaw"]
        assert len(warsaw) == 1
        assert warsaw[0]["available"] is False
        assert "Posen" in warsaw[0]["gate_terms"]
        assert warsaw[0]["disabled_reason_display"]

    def test_an_available_carve_becomes_actionable(self, world):
        _hand_over(world, "France", ["Posen"])
        rows = self._rows(world, "Prussia")
        warsaw = [r for r in rows
                  if r["action_params"]["tag"] == "DuchyOfWarsaw"]
        assert warsaw[0]["available"] is True
        assert warsaw[0]["reason_display"]

    def test_irrelevant_templates_are_not_noise_on_this_court(self, world):
        """A template whose soil never belonged to THIS court is a different
        country's business — showing it would be noise, not honesty."""
        rows = self._rows(world, "Prussia")
        tags = {r["action_params"]["tag"] for r in rows}
        assert "RomanRepublic" not in tags
        assert "Normandy" not in tags

    def test_the_add_verb_finds_the_eligible_template(self, world):
        from backend.game_logic.settlement_actions import (
            _carve_templates_for_court,
        )
        war_instance = _carve_ready(world, "DuchyOfWarsaw", "Prussia", "France")
        assert _carve_templates_for_court(
            world, war_instance=war_instance, court="Prussia",
            carver="France") == ["DuchyOfWarsaw"]

    def test_the_staged_row_never_shows_the_literal_type_name(self):
        from backend.game_logic.settlement_staging import _guided_line_display
        clause = {"type": "create_client", "from": "Prussia", "to": "France",
                  "tag": "DuchyOfWarsaw", "provinces": ["Posen"],
                  "client_display_name": "Duchy of Warsaw"}
        tag, display = _guided_line_display(clause, "Prussia")
        assert tag == "Demanded"
        assert display == "Erect Duchy of Warsaw (Posen)"
        assert "create client" not in display


class TestCarveCompanionRows:
    def test_every_carve_tag_has_its_dont_do_rows(self):
        """CLAUDE.md standing rule: never add a nation without
        NATION_DESIRE_PROFILES + TALLEYRAND_COMMENTARY. These degrade
        SILENTLY (empty dict / default ladder), so nothing else catches it."""
        for tag in CARVE_TAGS:
            assert tag in NATION_DESIRE_PROFILES, tag
            assert any(key[0] == tag for key in TALLEYRAND_COMMENTARY), tag

    def test_every_carve_tag_is_tiered_as_a_minor(self):
        """Unauthored tags take the `secondary` default — a one-province
        client would enter coalition threat math at Spain's weight."""
        for tag in CARVE_TAGS:
            assert NATION_POWER_TIERS.get(tag) == "minor", tag

    def test_every_carve_tag_has_a_colour_and_a_display_name(self):
        from backend.display_names import NATION_DISPLAY
        utils = (GODOT / "scripts" / "utils.gd").read_text(encoding="utf-8")
        colors = utils.split(
            "const NATION_COLORS = {", 1)[1].split("\n}", 1)[0]
        for tag in CARVE_TAGS:
            assert f'"{tag}"' in colors, f"{tag} would paint bug-magenta"
        # DuchyOfWarsaw would camelCase-split to "Duchy Of Warsaw".
        assert NATION_DISPLAY["DuchyOfWarsaw"] == "Duchy of Warsaw"
        assert '"DuchyOfWarsaw": "Duchy of Warsaw"' in utils

    def test_normandy_stays_out_of_both_prose_substitution_maps(self):
        """`Normandy` and `Rome` are PROVINCE names on this map — a blind
        substring replace would corrupt every sentence naming them."""
        from backend.display_names import NATION_DISPLAY
        assert "Normandy" not in NATION_DISPLAY
        utils = (GODOT / "scripts" / "utils.gd").read_text(encoding="utf-8")
        prose = utils.split(
            "PROSE_NATION_KEY_SUBSTITUTIONS", 1)[1].split("}", 1)[0]
        assert "Normandy" not in prose
        assert "RomanRepublic" not in prose

    def test_every_carve_flag_ships_with_its_import_sibling(self):
        """A `.svg` with no `.svg.import` fails ResourceLoader.exists() and
        the flag silently does not draw — found live at NA-6b."""
        for asset in ("DuchyOfWarsaw", "Normandy", "RomanRepublic", "Poland"):
            base = GODOT / "assets" / "ui" / "heraldry" / f"{asset}.svg"
            assert base.exists(), f"missing {asset}.svg"
            assert base.with_suffix(".svg.import").exists(), asset

    def test_every_template_flag_resolves_to_an_asset(self, world):
        for tag, template in world.formable_nations.items():
            identity = get_template_identity(template)
            assert identity is not None, tag
            path = (GODOT / "assets" / "ui" / "heraldry"
                    / f"{identity['flag']}.svg")
            assert path.exists(), f"{tag} has no flag asset"

    def test_the_c_to_t_chain_flag_exists(self, world):
        """The Duchy's dormant deck forms POLAND (NA-6d builds the chain,
        but the asset it will need is authored now rather than promised)."""
        entry = world.formable_nations["DuchyOfWarsaw"]["deck"][0]
        block = get_forms_block(entry)
        assert block["display_name"] == "Poland"
        assert (GODOT / "assets" / "ui" / "heraldry" / "Poland.svg").exists()


class TestCarveValidator:
    def _scenario(self):
        import json
        return json.loads(SCENARIO_PATH.read_text(encoding="utf-8"))

    def test_the_shipped_catalogue_validates(self):
        result = validate_scenario(str(SCENARIO_PATH))
        assert not [e for e in result.errors
                    if "formable_nations" in e.path], [
            str(e) for e in result.errors]

    def test_a_template_shadowing_a_live_nation_is_an_error(self):
        data = self._scenario()
        data["formable_nations"]["Austria"] = {
            "display_name": "Austria", "provinces": ["Posen"]}
        result = validate_scenario(data)
        assert any("already a nation" in e.message for e in result.errors)

    def test_a_template_without_provinces_is_an_error(self):
        data = self._scenario()
        data["formable_nations"]["DuchyOfWarsaw"]["provinces"] = []
        result = validate_scenario(data)
        assert any("provinces" in e.path for e in result.errors)

    def test_a_template_without_a_display_name_is_an_error(self):
        data = self._scenario()
        del data["formable_nations"]["Normandy"]["display_name"]
        result = validate_scenario(data)
        assert any("display_name" in e.message for e in result.errors)

    def test_a_template_deck_is_held_to_the_agenda_schema(self):
        data = self._scenario()
        data["formable_nations"]["DuchyOfWarsaw"]["deck"][0]["type"] = "junk"
        result = validate_scenario(data)
        assert any("Invalid agenda type" in e.message for e in result.errors)

    def test_a_template_aggrieved_roster_miss_only_warns(self):
        data = self._scenario()
        data["formable_nations"]["RomanRepublic"]["aggrieved"] = ["Ruritania"]
        result = validate_scenario(data)
        assert not [e for e in result.errors if "aggrieved" in e.path]
        assert any("Ruritania" in w.message for w in result.warnings)


class TestCarveGodotWiring:
    def test_the_renderer_emits_unavailable_rows_as_plain_text(self):
        """§11.6-1: never hidden, never a dead button. The unavailable arm
        must not emit a [url], or it becomes clickable-but-broken."""
        source = _read(GODOT / "scripts" / "proposal_confirm_popup.gd")
        block = source.split("func _build_suggestion_lines", 1)[1].split(
            "\nfunc ", 1)[0]
        guard = block.split("var bbcode", 1)[0]
        assert 'sugg.has("available")' in guard
        assert "unavailable" in guard
        assert "[url=" not in guard, (
            "the unavailable arm emits a link — it must be inert text")

    def test_the_fire_path_refuses_an_unavailable_suggestion(self):
        source = _read(GODOT / "scripts" / "proposal_confirm_popup.gd")
        block = source.split(
            "func _fire_suggestion", 1)[1].split("\nfunc ", 1)[0]
        assert 'sugg.has("available")' in block


# ═════════════════════════════════════════════════════════════════════════
# NA-6c REVIEW FIXES (July 19, 2026)
#
# Every test below pins a defect a 136-agent adversarial review confirmed
# against the first cut. Each names the failure it would have caught.
# ═════════════════════════════════════════════════════════════════════════

class TestCarveReviewFixes:
    def test_the_carved_capital_gets_a_real_garrison(self, world):
        """Review #1 (P1). Both capital-garrison seams key off the REGION
        flag, not `world.nation_capitals` — so a carved client whose capital
        carried no `is_capital` sat at garrison 0 forever, skipped by the
        regen loop: an undefended province the enemy retakes for free,
        destroying the tribute the carve was bought for."""
        _carve_ready(world, "DuchyOfWarsaw", "Prussia", "France")
        create_client_nation(world, "DuchyOfWarsaw", "France",
                             ceded_from="Prussia")
        capital = world.regions["Posen"]
        assert capital.is_capital is True
        assert capital.garrison_strength == world.get_capital_garrison_target(
            "DuchyOfWarsaw")
        # Parity with a boot-authored peer minor.
        assert world.regions["Milan"].is_capital is True

    def test_a_newborn_client_is_not_announced_as_eliminated(self, world):
        """Review #3 (P2). The turn tick announces any marshal-less nation
        as eliminated unless it is pre-seeded into
        `eliminated_nations_notified` — which `from_scenario` does for
        army-less boot courts and the carve did not. The first end turn
        after a Proclamation reported the brand-new nation destroyed."""
        _carve_ready(world, "DuchyOfWarsaw", "Prussia", "France")
        create_client_nation(world, "DuchyOfWarsaw", "France",
                             ceded_from="Prussia")
        assert "DuchyOfWarsaw" in world.eliminated_nations_notified
        assert not world.get_nation_marshals("DuchyOfWarsaw") \
            if hasattr(world, "get_nation_marshals") else True
        world.advance_turn()
        killed = [e for e in world.event_log
                  if e.get("type") == "nation_eliminated"
                  and e.get("nation") == "DuchyOfWarsaw"]
        assert killed == []

    def test_a_province_named_tag_never_rewrites_history_prose(self, world):
        """Review #2 (P2). `apply_formation_names_to_history` did a naked
        substring replace. NA-6c makes `Normandy` the first formation key
        that is ALSO a province, so a carved Duchy of Normandy rewrote
        "Ney was broken at Normandy" into "...at Duchy of Normandy" — a
        province line corrupted into a nation's name, permanently, on every
        entry after the formation turn. Godot has carried this guard since
        NA-6b; the backend twin did not."""
        _carve_ready(world, "Normandy", "France", "Britain")
        create_client_nation(world, "Normandy", "Britain", ceded_from="France")
        world.current_turn = 25
        event = {"type": "battle", "turn": 25}
        line = apply_formation_names_to_history(
            world, "Ney was broken at Normandy", event)
        assert line == "Ney was broken at Normandy"

    def test_a_multi_word_dead_name_is_still_renamed(self, world):
        """The guard must not disarm the feature it protects: an
        unambiguous multi-token name still gets the formation rename."""
        _free_italy_with_the_peninsula(world)
        process_formations(world)
        world.current_turn = int(world.current_turn) + 1
        line = apply_formation_names_to_history(
            world, "The court of Kingdom of Italy takes up a new design",
            {"type": "agenda_shift", "turn": world.current_turn})
        assert "Italy takes up" in line
        assert "Kingdom of Italy" not in line

    def test_a_carve_burdens_the_court_it_takes_soil_from(self, world):
        """Review #6 (P2). Adding the types to `_MATERIAL_LOSS_TYPES` was a
        NO-OP: that frozenset is only the early-out gate, and the per-type
        ladder that returns a reason was never extended. A carve prices
        HARSHER than a cession (0.45 vs 0.30) yet generated no
        `sold_out_by_war_leader` fallout at all."""
        from backend.game_logic.settlement_reactions import (
            _term_burdens_participant,
        )
        carve = {"type": "create_client", "from": "Prussia", "to": "France",
                 "tag": "DuchyOfWarsaw", "provinces": ["Posen"]}
        burdened, reason = _term_burdens_participant(carve, "Prussia")
        assert burdened is True and reason
        # not the carver, and not a bystander
        assert _term_burdens_participant(carve, "France")[0] is False
        assert _term_burdens_participant(carve, "Austria")[0] is False
        # VS-5's own gap, closed alongside.
        transfer = {"type": "vassal_transfer", "from": "Prussia",
                    "to": "France", "vassal": "Saxony"}
        assert _term_burdens_participant(transfer, "Prussia")[0] is True

    def test_a_bankrupt_loser_can_still_be_carved(self, world):
        """Review #7 (P2). The EC-W4 empty-purse arm returned a white peace
        BEFORE the carve gate, coupling a territorial clause to the payer's
        coin balance. The most decisively beaten France — exactly the state
        section 11.4 models with the Duchy of Normandy — was the one state
        immune to being carved, and got gentler terms than a solvent loser."""
        _at_war(world, "Britain", "France")
        _hand_over(world, "Britain", ["Normandy"])
        for treasury in (0, -500):
            world.nation_gold["France"] = treasury
            terms = _settlement_offer_build_terms(
                player="France", proposer_nation="Britain", war_age_turns=6,
                player_war_score=-80, world=world)
            types = [t["type"] for t in terms]
            assert "create_client" in types, treasury
            # ...and an empty chest still owes no indemnity.
            assert "gold_indemnity" not in types, treasury

    def test_the_add_verb_actually_builds_a_carve_clause(self):
        """Review #8 (P2). Every ratification test hand-built the clause
        dict, so the PLAYER'S ACTUAL CLICK PATH had zero coverage — and the
        add-verb chain ends in a bare `else: # liberation`, so a
        create_client arm that is moved, lost, or never reached silently
        stages a LIBERATION instead: ratification would free a Prussian
        vassal and erect no Duchy at all.

        Driven through the real dialogue harness (the same one the
        GT-Slice-1 verb tests use), not a hand-built dialogue dict.
        """
        from tests.test_settlement_guided_terms_slice1 import (
            _demand_verb, _stage_propose, _three_court_world,
        )
        world, _ = _three_court_world()
        # The harness builds the LEGACY fixture world, so the template is
        # authored against a legacy Prussian province (Rhineland) rather
        # than the 1805 map's Posen. The seam under test is the add verb,
        # not the shipped catalogue.
        world.formable_nations = {
            "DuchyOfWarsaw": {
                "display_name": "Duchy of Warsaw",
                "provinces": ["Rhineland"],
                "seeds": {"gold": 500},
            }
        }
        world.regions["Rhineland"].controller = "France"
        world.invalidate_active_nations_cache()
        dialogue = _stage_propose(world, terms=[{"type": "peace"}])
        result = _demand_verb(
            world, dialogue, "settlement_demand_add",
            {"nation": "Prussia", "group": "demand",
             "clause_type": "create_client", "tag": "DuchyOfWarsaw"})
        assert result.get("success"), result
        staged = [t for t in
                  (result["diplomatic_dialogue"].get("settlement_terms") or [])]
        carves = [t for t in staged if t.get("type") == "create_client"]
        assert len(carves) == 1, staged
        assert carves[0]["tag"] == "DuchyOfWarsaw"
        assert carves[0]["from"] == "Prussia"
        assert carves[0]["to"] == "France"
        assert carves[0]["provinces"] == ["Rhineland"]
        # ...and it must NOT have fallen through to the liberation branch.
        assert not [t for t in staged if t.get("type") == "liberation"]

    def test_the_creation_dispatch_beat_never_says_is_no_more(self, world):
        """Review #12. The `nation_created` dispatch template exists solely
        so a creation does not render the formation line with an empty
        {old_nation} — "By the will of the nation... is no more. Duchy of
        Warsaw stands." Nothing asserted the branch was taken."""
        from backend.game_logic.dispatch import (
            _DIPLOMATIC_EVENT_PRIORITY, _DIPLOMATIC_EVENT_TEMPLATES,
        )
        assert "nation_created" in _DIPLOMATIC_EVENT_TEMPLATES
        assert _DIPLOMATIC_EVENT_PRIORITY["nation_created"] == "HIGH"
        _carve_ready(world, "DuchyOfWarsaw", "Prussia", "France")
        create_client_nation(world, "DuchyOfWarsaw", "France",
                             ceded_from="Prussia")
        queued = [e for e in (world.pending_dispatch_events or [])
                  if e.get("type") == "nation_created"]
        assert queued, "the carve queued no nation_created beat"
        rendered = _DIPLOMATIC_EVENT_TEMPLATES["nation_created"].format(
            **queued[0]["template_vars"])
        assert "is no more" not in rendered
        assert "Duchy of Warsaw" in rendered
        assert queued[0].get("fog_rule") == "always"

    def test_the_vassal_transfer_row_also_reads_as_prose(self, world):
        """Review #12. The slice fixed VS-5's missing `_guided_line_display`
        arm alongside the carve arm, but only the carve arm was pinned —
        deleting the VS-5 elif left the table showing the literal
        "vassal transfer" and nothing failed."""
        from backend.game_logic.settlement_staging import _guided_line_display
        tag, display = _guided_line_display(
            {"type": "vassal_transfer", "from": "Prussia", "to": "France",
             "vassal": "Saxony"}, "Prussia")
        assert tag == "Demanded"
        assert display == "Yield Saxony"
        assert "vassal transfer" not in display

    def test_a_malformed_template_fails_before_it_mutates_anything(self, world):
        """Review #9 (P3). Only `provinces` was pre-checked; the rest of
        `seeds` was consumed at mutation time, so a diplomat block missing
        its `skill` raised KeyError out of ratification AFTER the tag was
        already in `enemy_nations` — leaving a phantom nation that
        serializes."""
        world.formable_nations["DuchyOfWarsaw"]["seeds"] = {
            "gold": 500, "diplomat": {"name": "X", "personality": "dove"},
        }
        before = list(world.enemy_nations)
        with pytest.raises(ValueError, match="skill"):
            create_client_nation(world, "DuchyOfWarsaw", "France")
        assert world.enemy_nations == before, "a half-built nation survived"
        assert "DuchyOfWarsaw" not in world.nation_capitals

    def test_bad_seed_scalars_are_refused(self, world):
        for bad in ({"gold": -5}, {"actions": "three"},
                    {"manpower": {"infantry": "many"}}):
            fresh = WorldState.from_dict(world.to_dict())
            fresh.formable_nations["DuchyOfWarsaw"]["seeds"] = bad
            with pytest.raises(ValueError):
                create_client_nation(fresh, "DuchyOfWarsaw", "France")

    def test_capital_re_derivation_never_writes_the_legacy_global(self):
        """Review #10 (P3). The from_dict re-derivation lacked the
        copy-on-write guard its creation-time twin has. On a legacy world
        `nation_capitals` IS the module global, so loading a legacy save
        carrying a catalogue poisoned every world built afterwards in the
        process — the shared-REGIONS_DATA pollution bug class."""
        from backend.models.region import NATION_CAPITALS
        before = dict(NATION_CAPITALS)
        legacy = WorldState()
        data = legacy.to_dict()
        data["formable_nations"] = {
            "Ruritania": {"display_name": "Ruritania", "provinces": ["Bavaria"]}
        }
        data["nation_formations"] = {
            "Ruritania": {"id": "Ruritania", "template": "Ruritania",
                          "sponsor": "France", "turn": 1}
        }
        rebuilt = WorldState.from_dict(data)
        assert rebuilt.nation_capitals.get("Ruritania") == "Bavaria"
        assert NATION_CAPITALS == before, (
            "the module-global capital table was mutated")
        assert "Ruritania" not in WorldState().nation_capitals

    def test_the_preview_states_loyalty_and_tribute_before_commitment(self, world):
        """Review #11 (P3). Section 11.6-2 requires the confirm step to name
        the client's loyalty seed and tribute expectations BEFORE the player
        commits. Both first appeared at ratification and on the Proclamation
        card — strictly post-decision."""
        from backend.game_logic.settlement_presentation import (
            build_applied_clauses_preview,
        )
        rows = build_applied_clauses_preview([
            {"type": "create_client", "from": "Prussia", "to": "France",
             "tag": "DuchyOfWarsaw", "provinces": ["Posen"],
             "client_display_name": "Duchy of Warsaw"}])
        row = [r for r in rows if r.get("type") == "create_client"][0]
        assert row["loyalty_after"] == CARVE_LOYALTY
        assert row["tribute_rate"] > 0
        assert str(CARVE_LOYALTY) in row["client_terms_display"]
        assert "tribute" in row["client_terms_display"]

    def test_the_validator_schemas_the_whole_seeds_block(self):
        """Review #9(a), the half of the fix the runtime guard does not
        cover. Section 11.4 assigns this boundary to the validator
        ("templates are data - the validator is the boundary"), so a mod
        must fail at validation rather than at ratification. Note the
        original `elif`: with `gold` absent, nothing below it ran at all."""
        import copy as _copy
        import json as _json
        base = _json.loads(SCENARIO_PATH.read_text(encoding="utf-8"))

        def _errors(mutate, needle):
            data = _copy.deepcopy(base)
            mutate(data)
            result = validate_scenario(data)
            return [e for e in result.errors if needle in e.path]

        assert _errors(
            lambda d: d["formable_nations"]["DuchyOfWarsaw"]["seeds"][
                "diplomat"].pop("skill"), "seeds.diplomat")
        assert _errors(
            lambda d: d["formable_nations"]["DuchyOfWarsaw"]["seeds"][
                "diplomat"].update(skill=99), "seeds.diplomat.skill")
        assert _errors(
            lambda d: d["formable_nations"]["Normandy"]["seeds"].update(
                actions=-1), "seeds.actions")
        assert _errors(
            lambda d: d["formable_nations"]["Normandy"]["seeds"].update(
                manpower={"infantry": "lots"}), "seeds.manpower")
        # An unknown personality degrades rather than breaks -> WARN.
        data = _copy.deepcopy(base)
        data["formable_nations"]["RomanRepublic"]["seeds"]["diplomat"][
            "personality"] = "grumpy"
        result = validate_scenario(data)
        assert not [e for e in result.errors if "personality" in e.path]
        assert [w for w in result.warnings if "personality" in w.path]

    def test_the_shipped_catalogue_passes_the_seeds_schema(self):
        result = validate_scenario(str(SCENARIO_PATH))
        assert not [e for e in result.errors if "seeds" in e.path], [
            str(e) for e in result.errors]

    def test_a_carve_warns_about_a_stripped_estate_exactly_like_a_cession(
            self, world):
        """Review #5 (P2). Three separate estate-warning loops opened with
        `!= "territory_cede"`, and a carve's soil rides `provinces`, so a
        carve stripped a marshal's estate with no warning on ANY surface —
        a direct violation of section 11.6-2. The three loops had already
        diverged before NA-6c gave them a fourth shape to miss, so the fix
        is one shared extractor, not three patches."""
        from backend.game_logic.settlement_scoring import (
            CESSION_SHAPED_CLAUSE_TYPES, cession_shaped_regions,
        )
        assert "create_client" in CESSION_SHAPED_CLAUSE_TYPES
        carve = {"type": "create_client", "from": "Prussia", "to": "France",
                 "tag": "DuchyOfWarsaw", "provinces": ["Posen"]}
        cede = {"type": "territory_cede", "from": "Prussia", "to": "France",
                "region": "Posen"}
        assert cession_shaped_regions(carve) == cession_shaped_regions(cede)
        assert cession_shaped_regions({"type": "peace"}) == []

        world.regions["Posen"].controller = "France"
        world.marshals["Ney"].dotation_regions = ["Posen"]
        world.invalidate_active_nations_cache()

        def _warnings(terms):
            payload = build_settlement_review(
                war_id="war_1", war_label="the war", proposer_side=["France"],
                accepting_side=["Prussia"],
                covered_enemy_participants=["Prussia"], terms=terms,
                allies=[], warnings=[], acceptance={}, world=world)
            return [r.get("detail") for r in
                    (payload["sections"]["warnings"].get("inline") or [])]

        cede_warnings = _warnings([cede])
        carve_warnings = _warnings([carve])
        assert any("Ney" in str(t) for t in cede_warnings)
        assert carve_warnings == cede_warnings


# ═══════════════════ NA-6d — THE POLAND CHAIN (§11.7 C→T pin) ═════════════
#
# The hinge the whole slice turns on: a Class C CREATION record must not
# latch the formation poll. Being carved into existence was the Duchy's
# BIRTH, not its formation — a freed Duchy of Warsaw taking Lithuania and
# Volhynia proclaims POLAND through the same §11.1 machinery every Class T
# formable uses, and only THAT latches it forever.

def _erect_the_duchy(world):
    _carve_ready(world, "DuchyOfWarsaw", "Prussia", "France")
    create_client_nation(world, "DuchyOfWarsaw", "France", ceded_from="Prussia")


def _the_poland_chain(world):
    """Create the Duchy, free it, hand it the Commonwealth lands, poll."""
    _erect_the_duchy(world)
    _free(world, "DuchyOfWarsaw")
    _hand_over(world, "DuchyOfWarsaw", ["Lithuania", "Volhynia"])
    return process_formations(world)


class TestPolandChain:
    def test_a_creation_record_does_not_latch_the_poll(self, world):
        proclamations = _the_poland_chain(world)
        assert len(proclamations) == 1
        payload = proclamations[0]
        assert payload["nation"] == "DuchyOfWarsaw"
        assert payload["display_name"] == "Poland"
        assert payload["old_display_name"] == "Duchy of Warsaw"
        assert payload["entry_id"] == "commonwealth_restored"

    def test_the_identity_transforms_to_poland(self, world):
        _the_poland_chain(world)
        assert get_display_identity(world, "DuchyOfWarsaw") == {
            "display_name": "Poland", "flag_tag": "Poland"}
        assert build_nation_display_overrides(
            world)["DuchyOfWarsaw"] == "Poland"
        assert build_nation_flag_overrides(world)["DuchyOfWarsaw"] == "Poland"

    def test_a_vassal_duchy_cannot_proclaim(self, world):
        """§3.2 dormancy still holds — the chain requires FREEDOM first."""
        _erect_the_duchy(world)
        _hand_over(world, "DuchyOfWarsaw", ["Lithuania", "Volhynia"])
        assert process_formations(world) == []
        record = get_formation_record(world, "DuchyOfWarsaw")
        assert record["id"] == "DuchyOfWarsaw"     # still the birth record

    def test_poland_is_latched_forever(self, world):
        _the_poland_chain(world)
        assert process_formations(world) == []
        reloaded = WorldState.from_dict(world.to_dict())
        assert process_formations(reloaded) == []
        assert get_display_identity(reloaded, "DuchyOfWarsaw") == {
            "display_name": "Poland", "flag_tag": "Poland"}

    def test_the_record_keeps_its_birth_template(self, world):
        """The `from_dict` capital re-derivation (Q10) keys off the record's
        `template` — the Poland formation must preserve it or a reloaded
        Duchy silently loses its capital and pays −1 DP forever."""
        _the_poland_chain(world)
        record = get_formation_record(world, "DuchyOfWarsaw")
        assert record["id"] == "commonwealth_restored"
        assert record["template"] == "DuchyOfWarsaw"
        reloaded = WorldState.from_dict(world.to_dict())
        assert reloaded.nation_capitals.get("DuchyOfWarsaw") == "Posen"

    def test_berlin_blames_paris(self, world):
        """§11.10 decision 8: the freed Duchy has no lord at proclamation,
        so the sponsor comes from the stored CREATION record — and the
        aggrieved blow lands on BOTH Poland and France, exactly once."""
        _erect_the_duchy(world)
        _free(world, "DuchyOfWarsaw")
        keys = {
            (power, target): world._make_diplo_key(power, target)
            for power in ("Prussia", "Russia")
            for target in ("DuchyOfWarsaw", "France")
        }
        before = {k: world.nation_relations.get(key, 0)
                  for k, key in keys.items()}
        _hand_over(world, "DuchyOfWarsaw", ["Lithuania", "Volhynia"])
        payload = process_formations(world)[0]
        assert payload["sponsor"] == "France"
        assert sorted(payload["aggrieved"]) == ["Prussia", "Russia"]
        for k, key in keys.items():
            assert world.nation_relations[key] == max(
                -100, before[k] + FORMATION_AGGRIEVED_RELATION_PENALTY)
        after = {key: world.nation_relations[key] for key in keys.values()}
        process_formations(world)
        for key, value in after.items():
            assert world.nation_relations[key] == value

    def test_the_post_formation_goal_is_guard_the_vistula(self, world):
        """§11.1-4 — deck priority natively activates the next entry."""
        _the_poland_chain(world)
        view = get_active_agenda("DuchyOfWarsaw", world)
        assert view is not None
        assert view.id == "guard_the_vistula"

    def test_a_standing_roman_republic_keeps_italy_unformed(self, world):
        """The §11.7 v1.2 risorgimento-block pin: Rome under a carved Roman
        Republic is Rome NOT under the Kingdom of Italy or its vassals, so
        the peninsula's dream stays one province short — derived, no code."""
        _carve_ready(world, "RomanRepublic", "PapalStates", "France")
        world.war_scores[world._make_diplo_key("France", "PapalStates")] = 95
        create_client_nation(world, "RomanRepublic", "France",
                             ceded_from="PapalStates")
        _free(world, "KingdomOfItaly")
        _hand_over(world, "KingdomOfItaly",
                   [p for p in ITALY_PROVINCES if p != "Rome"])
        assert world.regions["Rome"].controller == "RomanRepublic"
        assert process_formations(world) == []
        assert get_formation_record(world, "KingdomOfItaly") is None
        watch = get_formation_watch(world, "KingdomOfItaly")
        assert watch["held"] == 4 and watch["required"] == 5

    def test_history_respects_the_duchy_era(self, world):
        """`apply_formation_names_to_history` renames only at/after the
        formation turn — and "Duchy of Warsaw" is multi-token, so the
        prose-safety guard permits the rename that "Normandy" is denied."""
        _erect_the_duchy(world)
        _free(world, "DuchyOfWarsaw")
        world.current_turn = 12
        _hand_over(world, "DuchyOfWarsaw", ["Lithuania", "Volhynia"])
        process_formations(world)
        early = apply_formation_names_to_history(
            world, "Duchy of Warsaw musters its corps.", {"turn": 5})
        late = apply_formation_names_to_history(
            world, "Duchy of Warsaw musters its corps.", {"turn": 12})
        assert early == "Duchy of Warsaw musters its corps."
        assert late == "Poland musters its corps."


# ═══════════ NA-6d — "THE POLISH QUESTION" (§11.9 named wound) ════════════

class TestPolishQuestion:
    def test_the_standing_wound_names_itself(self, world):
        from backend.game_logic.formations import (
            get_formation_grudge_contributions,
        )
        _the_poland_chain(world)
        contributions = get_formation_grudge_contributions(world, budget=2)
        assert contributions == [{
            "source": "formation_grudge:DuchyOfWarsaw",
            "label": "The Polish Question",
            "amount": 2,       # Prussia + Russia, inside the shared cap
        }]

    def test_the_threat_panel_resolves_the_label(self, world):
        from backend.game_logic.diplomatic_ledger import (
            _THREAT_SOURCE_LABELS, _threat_source_label,
        )
        _the_poland_chain(world)
        assert _threat_source_label(
            world, "formation_grudge:DuchyOfWarsaw") == "The Polish Question"
        # Unknown tag / unformed world → the generic formation row.
        assert _threat_source_label(
            world, "formation_grudge:Ruritania"
        ) == _THREAT_SOURCE_LABELS["formation_grudge"]
        # The static arm is untouched.
        assert _threat_source_label(world, "battle_win") == "Won a battle"

    def test_coalition_step_two_emits_the_named_source(self, world):
        """The wiring pin: `process_coalition_turn` step 2 must emit the
        per-formation key, not one merged `formation_grudge`."""
        from backend.game_logic.coalition import process_coalition_turn
        _the_poland_chain(world)
        world.threat_sources_this_turn = []
        process_coalition_turn(world)
        named = [s for s in world.threat_sources_this_turn
                 if s.get("source") == "formation_grudge:DuchyOfWarsaw"]
        assert len(named) == 1
        assert int(named[0]["amount"]) >= 1
        assert not any(s.get("source") == "formation_grudge"
                       for s in world.threat_sources_this_turn)

    def test_the_wound_ends_with_the_aggrieved_courts(self, world):
        from backend.game_logic.formations import (
            get_formation_grudge_contributions,
        )
        _the_poland_chain(world)
        world.vassals["Prussia"] = {"lord": "France", "loyalty": 50}
        world.invalidate_bloc_members_cache()
        contributions = get_formation_grudge_contributions(world, budget=2)
        assert contributions[0]["amount"] == 1     # Russia alone grieves
        world.enemy_nations.remove("Russia")
        world.invalidate_active_nations_cache()
        assert get_formation_grudge_contributions(world, budget=2) == []

    def test_the_cap_is_shared_with_the_agenda_family(self, world):
        from backend.game_logic.formations import (
            get_formation_grudge_contributions,
        )
        _the_poland_chain(world)
        assert get_formation_grudge_contributions(world, budget=0) == []
        one = get_formation_grudge_contributions(world, budget=1)
        assert one[0]["amount"] == 1               # only the remainder

    def test_an_ai_erected_formation_feeds_no_france_threat(self, world):
        """The v0.1 France-scoped-scalar caveat, on the REAL carve path:
        Britain erecting the Roman Republic costs the relation blows but
        never feeds the France-targeted scalar."""
        from backend.game_logic.formations import (
            get_formation_grudge_contributions,
        )
        _carve_ready(world, "RomanRepublic", "PapalStates", "Britain")
        key = world._make_diplo_key("Britain", "PapalStates")
        world.war_scores[key] = 95
        create_client_nation(world, "RomanRepublic", "Britain",
                             ceded_from="PapalStates")
        assert get_formation_grudge_contributions(world, budget=2) == []

    def test_grudge_label_rides_the_forms_block(self):
        block = get_forms_block({"forms": {
            "display_name": "Poland",
            "aggrieved": ["Prussia"],
            "grudge_label": "The Polish Question",
        }})
        assert block["grudge_label"] == "The Polish Question"
        bare = get_forms_block({"forms": {"display_name": "Poland"}})
        assert bare["grudge_label"] == ""

    def test_validator_accepts_the_shipped_labels_and_rejects_junk(self):
        import json
        data = json.loads(SCENARIO_PATH.read_text(encoding="utf-8"))
        result = validate_scenario(data)
        assert not [e for e in result.errors if "grudge_label" in e.path]
        data["formable_nations"]["RomanRepublic"]["grudge_label"] = 7
        result = validate_scenario(data)
        assert [e for e in result.errors if "grudge_label" in e.path]


# ═══════════ NA-6d — THE FORMABLES BUTTON (§11.6-8 / decision 9) ══════════

class TestFormablesPayload:
    def test_every_template_and_watcher_has_a_row(self, world):
        from backend.game_logic.formations import build_formables_payload
        payload = build_formables_payload(world)
        rows = {(r["cls"], r["tag"]): r for r in payload["formables"]}
        assert ("C", "DuchyOfWarsaw") in rows
        assert ("C", "Normandy") in rows
        assert ("C", "RomanRepublic") in rows
        assert ("T", "KingdomOfItaly") in rows
        assert ("T", "Holland") in rows
        assert payload["count"] == len(payload["formables"]) == 5

    def test_rows_are_never_hidden_and_never_dead(self, world):
        """§11.6-8: an unavailable row states exactly what is missing."""
        from backend.game_logic.formations import build_formables_payload
        for row in build_formables_payload(world)["formables"]:
            assert row["gate_terms"], row["tag"]
            assert row["display_name"]
            assert row["flag"]
            for term in row["gate_terms"]:
                assert term["text"]
                assert isinstance(term["met"], bool)

    def test_boot_warsaw_row_states_its_gates_honestly(self, world):
        from backend.game_logic.formations import build_formables_payload
        row = next(r for r in build_formables_payload(world)["formables"]
                   if r["tag"] == "DuchyOfWarsaw")
        assert row["available"] is False
        assert row["deep_link"] is None
        texts = [t["text"] for t in row["gate_terms"]]
        assert any("at war with Prussia" in t for t in texts)
        assert any("Posen" in t for t in texts)
        met = {t["text"]: t["met"] for t in row["gate_terms"]}
        assert not any(met.values())       # boot France holds none of it

    def test_the_players_own_soil_row_is_the_mirror_threat(self, world):
        """Normandy's from_court IS the player — the honest gate term is
        the coalition-side mirror, never "at war with France"."""
        from backend.game_logic.formations import build_formables_payload
        row = next(r for r in build_formables_payload(world)["formables"]
                   if r["tag"] == "Normandy")
        assert row["available"] is False
        assert row["deep_link"] is None
        assert "only a victorious enemy" in row["gate_terms"][0]["text"]

    def test_a_qualifying_war_makes_the_row_available_with_a_deep_link(
            self, world):
        from backend.game_logic.formations import build_formables_payload
        from backend.game_logic.settlement_actions import (
            _carve_templates_for_court,
        )
        war_instance = _at_war(world, "France", "Prussia")
        # `set_diplomatic_state` alone registers no war INSTANCE, and the
        # payload's availability scan walks `world.war_instances` — the
        # same store the settlement surface reads.
        world.war_instances.setdefault("war_na6d_test", war_instance)
        world._war_instance_indexes_dirty = True
        _hand_over(world, "France", ["Posen"])
        row = next(r for r in build_formables_payload(world)["formables"]
                   if r["tag"] == "DuchyOfWarsaw")
        assert row["available"] is True
        assert row["deep_link"]["nation"] == "Prussia"
        assert row["deep_link"]["war_id"]
        assert all(t["met"] for t in row["gate_terms"])
        # Drift pin: availability here must equal the settlement surface's
        # own answer for the same war — one predicate, two consumers.
        assert "DuchyOfWarsaw" in _carve_templates_for_court(
            world, war_instance=war_instance, court="Prussia",
            carver="France")

    def test_an_erected_duchy_stands_and_its_dream_watches(self, world):
        """After the carve the C row says the client stands — and a NEW
        Class T watcher row appears for the dormant Poland dream."""
        from backend.game_logic.formations import build_formables_payload
        _erect_the_duchy(world)
        rows = {(r["cls"], r["tag"]): r
                for r in build_formables_payload(world)["formables"]}
        c_row = rows[("C", "DuchyOfWarsaw")]
        assert c_row["available"] is False
        assert c_row["gate_terms"][0]["text"] == "Duchy of Warsaw already stands"
        assert c_row["gate_terms"][0]["met"] is True
        t_row = rows[("T", "DuchyOfWarsaw")]
        assert t_row["display_name"] == "Poland"
        assert t_row["flag"] == "Poland"
        assert t_row["progress"] == "0 of 2 provinces held"
        assert any("vassal of France" in t["text"]
                   for t in t_row["gate_terms"])

    def test_a_formed_dream_says_it_stands(self, world):
        from backend.game_logic.formations import build_formables_payload
        _free_italy_with_the_peninsula(world)
        process_formations(world)
        rows = {(r["cls"], r["tag"]): r
                for r in build_formables_payload(world)["formables"]}
        italy = rows[("T", "KingdomOfItaly")]
        assert italy["display_name"] == "Italy"
        assert italy["gate_terms"][0]["text"] == "Italy already stands"
        assert italy["available"] is False

    def test_the_endpoint_exists_and_serves_the_payload(self):
        """Source pin on the route + builder — the wizard's fetch target."""
        main_py = (
            Path(__file__).resolve().parents[1] / "backend" / "main.py"
        ).read_text(encoding="utf-8")
        assert '@app.get("/formables")' in main_py
        assert "build_formables_payload" in main_py


# ═══════════ NA-6d — THE WATCHER'S CONSUMERS (§11.6-5 markers) ════════════

class TestWatcherConsumers:
    def test_the_war_room_names_the_forming_dream(self, world):
        """The per-belligerent design line carries the "forms:" marker with
        live progress — the §11.8 stage-0 'dream is visible' surface."""
        from backend.game_logic.diplomatic_advisory import _assess_situation
        # Austria is a REAL boot-war opponent; give its active design an
        # unmet `forms` block so the marker must ride its design line.
        world.agendas["Austria"] = [{
            "id": "the_dream", "type": "acquire_regions",
            "title": "The Dream", "regions": ["Milan", "Vienna"],
            "forms": {"display_name": "Danubia"},
        }]
        world._agenda_cache = None
        assessment = _assess_situation(world)
        text = str(assessment)
        assert "forms: Danubia" in text
        assert "1 of 2 provinces held" in text

    def test_the_nations_tab_payload_carries_the_marker(self, world):
        """The agenda payload's `forms` block (NA-6a) — re-pinned here as
        the contract the diplomatic_ledger.gd consumer renders."""
        _free(world, "KingdomOfItaly")
        payload = build_agenda_payload("KingdomOfItaly", world)
        assert payload["forms"]["display_name"] == "Italy"
        assert "provinces held" in payload["forms"]["progress"]

    def test_the_ledger_gd_renders_the_forms_marker(self):
        ledger_gd = _read("scripts/diplomatic_ledger.gd")
        assert 'agenda.get("forms")' in ledger_gd
        assert "forms: " in ledger_gd

    def test_the_wizard_gd_has_the_formables_entry(self):
        wizard_gd = _read("scripts/diplomacy_wizard.gd")
        assert "/formables" in wizard_gd
        assert "Formable Nations" in wizard_gd
        assert "gate_terms" in wizard_gd
        assert "deep_link" in wizard_gd
        assert "open_for_nation" in wizard_gd
