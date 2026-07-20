"""NA-6d post-landing audit regressions (spec §21.1).

A six-lens adversarial review of commit `1055a02` ("the Poland C→T chain +
the Formables button"). Every test here is a regression pin for a defect
that was REPRODUCED live against the 1805 boot world, plus the two
falsifiability gaps the review found in the slice's own tests — the
"drift-pinned against the settlement predicate" claim and the §11.6-8
"never dead" invariant, neither of which could fail on a broken build.

Fixtures and world helpers are reused from `test_nation_agendas_formables`
so the two files cannot drift about what a carve or a formation IS.
"""

import json

import pytest

from backend.game_logic.agendas import build_agenda_payload
from backend.game_logic.formations import (
    build_formables_payload,
    create_client_nation,
    format_progress,
    get_formation_record,
    get_formation_watch,
    process_formations,
)
from backend.game_logic.settlement_validation import (
    evaluate_create_client_eligibility,
)
from backend.models.world_state import WorldState
from backend.modding.validator import validate_scenario

from tests.test_nation_agendas_formables import (  # noqa: F401 (fixtures)
    SCENARIO_PATH,
    _at_war,
    _carve_ready,
    _erect_the_duchy,
    _free,
    _hand_over,
    _the_poland_chain,
    world,
    world1805,
)


def _row(world, tag, cls=None):
    """The formables row for `tag`, or None."""
    for row in build_formables_payload(world)["formables"]:
        if row["tag"] == tag and (cls is None or row["cls"] == cls):
            return row
    return None


def _registered_war(world, a, b, war_id="war_na6d_audit"):
    """A war between `a` and `b` that is actually in `world.war_instances`.

    `set_diplomatic_state` alone registers no war INSTANCE, and both the
    availability scan and the settlement surface walk that store — so a
    synthetic instance would make every carve test silently unavailable.
    """
    instance = _at_war(world, a, b)
    world.war_instances.setdefault(war_id, instance)
    world._war_instance_indexes_dirty = True
    return instance


def _carve_ready_at_war(world, template_id, court, carver="France"):
    """`_carve_ready`, but with the war instance registered."""
    instance = _registered_war(world, carver, court)
    _carve_ready(world, template_id, court, carver)
    return instance


# ══════════════════════════════════════════════════════════════════════════
# §11.6-8 — "never hidden, NEVER DEAD"
# ══════════════════════════════════════════════════════════════════════════

class TestNeverDeadInvariant:
    """The slice's own `test_rows_are_never_hidden_and_never_dead` checked
    only that `gate_terms` was non-empty and well-typed. It never asserted
    the actual invariant — and production violated it."""

    def _assert_invariant(self, world):
        for row in build_formables_payload(world)["formables"]:
            terms = row["gate_terms"]
            assert terms, f"{row['tag']} has no gate terms"
            if row["available"]:
                assert all(t["met"] for t in terms), (
                    f"{row['tag']} is available while a gate term reads "
                    f"unmet — the row contradicts itself")
            else:
                assert any(not t["met"] for t in terms), (
                    f"{row['tag']} is unavailable but every gate term reads "
                    f"met — the row states nothing the player can act on")

    def test_the_invariant_holds_at_boot(self, world):
        self._assert_invariant(world)

    def test_the_roman_republic_names_its_blocker(self, world):
        """The live reproduction. The Papal States are a ONE-province
        polity, so carving Rome erases them and the total-annexation rule
        refuses below war score 90 — but that condition had no gate term,
        so the row showed two green ✓ and no button."""
        _carve_ready(world, "RomanRepublic", "PapalStates", "France")
        world.war_scores[world._make_diplo_key("PapalStates", "France")] = 10
        row = _row(world, "RomanRepublic")
        assert row["available"] is False
        self._assert_invariant(world)
        blockers = [t for t in row["gate_terms"] if not t["met"]]
        assert len(blockers) == 1
        assert "decisive victory" in blockers[0]["text"]
        assert "90" in blockers[0]["text"]

    def test_a_decisive_victory_opens_the_row(self, world):
        """The other side of the same term — so it is a real gate, not
        decorative copy."""
        _carve_ready_at_war(world, "RomanRepublic", "PapalStates")
        world.war_scores[world._make_diplo_key("PapalStates", "France")] = 90
        row = _row(world, "RomanRepublic")
        assert row["available"] is True
        assert all(t["met"] for t in row["gate_terms"])
        self._assert_invariant(world)


# ══════════════════════════════════════════════════════════════════════════
# Archived wars are not a carve route
# ══════════════════════════════════════════════════════════════════════════

class TestArchivedWarIsNotACarveRoute:
    """`war_instances` retains CONCLUDED wars for ARCHIVE_RETENTION_TURNS
    and the predicate's side resolution is pure membership — so an archived
    war produced `available: true` with a deep link the settlement layer
    then refuses as `war_archived`, beside its own "at war ✗" term."""

    def test_an_ended_war_never_makes_a_row_available(self, world):
        _carve_ready_at_war(world, "DuchyOfWarsaw", "Prussia")
        assert _row(world, "DuchyOfWarsaw", cls="C")["available"] is True

        for instance in (world.war_instances or {}).values():
            if isinstance(instance, dict):
                instance["ended_turn"] = int(world.current_turn)

        row = _row(world, "DuchyOfWarsaw", cls="C")
        assert row["available"] is False
        assert row["deep_link"] is None

    def test_the_scan_uses_the_shared_active_war_helper(self):
        """Drift guard: every other settlement consumer filters through
        `_iter_active_war_instances`. This one must too."""
        import inspect

        from backend.game_logic import formations
        source = inspect.getsource(formations.build_formables_payload)
        assert "_iter_active_war_instances" in source


# ══════════════════════════════════════════════════════════════════════════
# The drift pin, made falsifiable
# ══════════════════════════════════════════════════════════════════════════

class TestDriftPinIsFalsifiable:
    """The slice claimed availability was "drift-pinned against the
    settlement predicate", but built the one scenario where a naive
    "at war + provinces held" re-derivation returns the same answer — so it
    could not detect drift. These exercise cases where they DISAGREE."""

    def test_soil_provenance_diverges_from_the_naive_answer(self, world):
        """Naive: France is at war with Prussia and holds Rome → carve the
        Roman Republic from Prussia. The predicate refuses — Rome is not
        Prussian soil."""
        war = _at_war(world, "France", "Prussia")
        _hand_over(world, "France", ["Rome"])
        verdict = evaluate_create_client_eligibility(
            world, war_instance=war, template_id="RomanRepublic",
            from_court="Prussia", carver="France")
        assert verdict["eligible"] is False
        assert verdict["refusal_code"] == "carve_not_defeated_soil"
        row = _row(world, "RomanRepublic")
        assert (row["deep_link"] or {}).get("nation") != "Prussia"

    def test_total_annexation_diverges_from_the_naive_answer(self, world):
        war = _carve_ready(world, "RomanRepublic", "PapalStates", "France")
        world.war_scores[world._make_diplo_key("PapalStates", "France")] = 10
        verdict = evaluate_create_client_eligibility(
            world, war_instance=war, template_id="RomanRepublic",
            from_court="PapalStates", carver="France")
        assert verdict["eligible"] is False
        assert verdict["refusal_code"] == "carve_total_annexation_blocked"
        assert _row(world, "RomanRepublic")["available"] is False

    def test_the_payload_tracks_the_predicate_across_a_sweep(self, world):
        """One predicate, two consumers — asserted as EQUALITY over a
        scenario sweep rather than one hardcoded expectation."""
        war = _carve_ready_at_war(world, "RomanRepublic", "PapalStates")
        key = world._make_diplo_key("PapalStates", "France")
        for score in (0, 10, 89, 90, 120):
            world.war_scores[key] = score
            predicate = evaluate_create_client_eligibility(
                world, war_instance=war, template_id="RomanRepublic",
                from_court="PapalStates", carver="France")["eligible"]
            payload = _row(world, "RomanRepublic")["available"]
            assert payload is bool(predicate), (
                f"war score {score}: payload {payload} != predicate "
                f"{predicate} — the two surfaces have drifted")


# ══════════════════════════════════════════════════════════════════════════
# §11.8 stage 3 — no surface may show the dead name
# ══════════════════════════════════════════════════════════════════════════

class TestNoDeadNameOnTheFormablesSurface:
    """The Class C row rendered the template's BIRTH identity, so a Duchy
    of Warsaw that had gone on to proclaim Poland showed "Duchy of Warsaw"
    — while `Utils.bb_flag` DID resolve the override, drawing Poland's flag
    beside the dead label — and the Class T pass emitted a second row for
    the same tag."""

    def test_a_formed_client_shows_its_living_name(self, world):
        _the_poland_chain(world)
        row = _row(world, "DuchyOfWarsaw", cls="C")
        assert row["display_name"] == "Poland"
        assert row["flag"] == "Poland"
        assert row["gate_terms"][0]["text"] == "Poland already stands"

    def test_a_formed_client_gets_exactly_one_row(self, world):
        _the_poland_chain(world)
        rows = [r for r in build_formables_payload(world)["formables"]
                if r["tag"] == "DuchyOfWarsaw"]
        assert len(rows) == 1, (
            "one nation, one row — both passes said 'already stands'")

    def test_an_unformed_client_keeps_its_watcher_row(self, world):
        """The dedup must suppress ONLY the redundant formed arm: a created
        client whose dream is still unfired keeps the C row AND its Class T
        watcher (§11.6-5, "the dream is visible")."""
        _erect_the_duchy(world)
        rows = {(r["cls"], r["tag"]): r
                for r in build_formables_payload(world)["formables"]}
        assert ("C", "DuchyOfWarsaw") in rows
        assert ("T", "DuchyOfWarsaw") in rows
        assert rows[("T", "DuchyOfWarsaw")]["display_name"] == "Poland"


# ══════════════════════════════════════════════════════════════════════════
# §11.1 — formation is permanent
# ══════════════════════════════════════════════════════════════════════════

class TestFormationPermanence:
    def _lose_and_recarve(self, world):
        """Poland forms, Prussia takes it all back, France raises the
        Duchy again on the same soil."""
        _the_poland_chain(world)
        _hand_over(world, "Prussia", ["Posen", "Lithuania", "Volhynia"])
        assert "DuchyOfWarsaw" not in set(world.get_active_nations())
        _carve_ready(world, "DuchyOfWarsaw", "Prussia", "France")
        create_client_nation(world, "DuchyOfWarsaw", "France",
                             ceded_from="Prussia")
        _free(world, "DuchyOfWarsaw")
        _hand_over(world, "DuchyOfWarsaw", ["Lithuania", "Volhynia"])

    def test_a_state_raised_twice_may_dream_twice(self, world):
        """The design call: a state erased from the map and genuinely
        re-erected is NOT frozen under its birth name. Freezing it would
        leave a liberated-then-lost Poland reading "Duchy of Warsaw"
        forever, with no path back."""
        self._lose_and_recarve(world)
        again = process_formations(world)
        assert [p["display_name"] for p in again] == ["Poland"]
        from backend.game_logic.formations import get_display_identity
        assert get_display_identity(world, "DuchyOfWarsaw")["display_name"] == (
            "Poland")

    def test_but_the_treasury_is_filled_only_once(self, world):
        """The `rewarded` latch. Before the audit the re-carve path
        overwrote the record wholesale, so the second proclamation banked
        a second +2,000 gold — a farm at 2,000 a lap."""
        self._lose_and_recarve(world)
        before = world.nation_gold["DuchyOfWarsaw"]
        payload = process_formations(world)[0]
        assert payload["gold"] == 0
        assert payload["regions_lifted"] == 0
        assert world.nation_gold["DuchyOfWarsaw"] == before

    def test_and_the_offended_courts_are_offended_again(self, world):
        """The blow DOES re-fire, and must: §11.9 stands the wound up
        only "while the formation stands", so a Poland conquered out of
        existence ANSWERS Berlin and St Petersburg. Proclaiming it a
        second time is a second outrage. This costs the player relations
        rather than paying them, so it is never farmable — and the
        alternative (a silent second proclamation) would leave the
        partitioning powers indifferent to the thing they went to war
        over."""
        self._lose_and_recarve(world)
        payload = process_formations(world)[0]
        assert sorted(payload["aggrieved"]) == ["Prussia", "Russia"]

    def test_the_card_claims_no_reward_it_did_not_pay(self, world):
        """"+0 gold to its treasury" would read as a bug; the line is
        omitted entirely."""
        from backend.game_logic.formations import build_proclamation_card
        self._lose_and_recarve(world)
        card = build_proclamation_card(world, process_formations(world)[0])
        assert not any("gold" in term for term in card["terms"])
        assert card["proclamation"], "the moment still gets its blurb"

    def test_the_pay_once_latch_survives_the_round_trip(self, world):
        """It gates real gold, so it has to serialize."""
        self._lose_and_recarve(world)
        process_formations(world)
        reloaded = WorldState.from_dict(world.to_dict())
        assert reloaded.nation_formations["DuchyOfWarsaw"]["rewarded"] is True

    def test_an_id_template_collision_cannot_re_fire_the_beat(self, world):
        """`_is_creation_record` inferred "created" from `id == template`,
        coupling two independent authoring namespaces. A deck entry id
        equal to a formable tag made a FORMED record read as a creation
        record: the poll never latched and the nation re-proclaimed EVERY
        turn — +2,000 gold and a fresh −30 per tick, unbounded. The
        explicit `formed` marker is what closes it."""
        _erect_the_duchy(world)
        _free(world, "DuchyOfWarsaw")
        world.agendas["DuchyOfWarsaw"] = [{
            "id": "DuchyOfWarsaw",              # the collision
            "type": "acquire_regions",
            "regions": ["Posen"],
            "title": "Collision",
            "forms": {"display_name": "Collide", "blurb": "x"},
        }]
        assert len(process_formations(world)) == 1
        banked = world.nation_gold["DuchyOfWarsaw"]
        for _ in range(3):
            assert process_formations(world) == []
        assert world.nation_gold["DuchyOfWarsaw"] == banked

    def test_the_validator_refuses_the_collision(self):
        """...and the authoring layer rejects it loudly, so the inference
        fallback is never load-bearing in a shipped scenario."""
        data = json.loads(SCENARIO_PATH.read_text(encoding="utf-8"))
        deck = data["agendas"]["Prussia"]
        deck[0] = dict(deck[0], id="DuchyOfWarsaw")
        result = validate_scenario(data)
        assert not result.is_valid
        assert any("collides with the agenda deck entry" in str(e)
                   for e in result.errors), [str(e) for e in result.errors]

    def test_the_shipped_scenario_has_no_collision(self):
        """The guard does not retroactively break the authored campaign."""
        data = json.loads(SCENARIO_PATH.read_text(encoding="utf-8"))
        assert validate_scenario(data).is_valid


# ══════════════════════════════════════════════════════════════════════════
# Watcher copy
# ══════════════════════════════════════════════════════════════════════════

class TestWatcherCopy:
    """Spec §21 claimed "a one-province claim reads 'holds its claimed
    province', not 'all 1'". That landed only in the gate-term composition;
    the `progress` field kept an unconditional plural — and this slice
    added two surfaces that render it."""

    @pytest.mark.parametrize("held,required,expected", [
        (0, 1, "0 of 1 province held"),
        (1, 1, "1 of 1 province held"),
        (2, 5, "2 of 5 provinces held"),
        (0, 0, ""),
    ])
    def test_the_copy_agrees_with_the_count(self, held, required, expected):
        assert format_progress(held, required) == expected

    def test_the_dutch_watcher_reads_singular_at_boot(self, world):
        """Live at boot: Holland forms the United Netherlands on ONE
        province, so the Formables browser, the ledger Design line and the
        war room all rendered "0 of 1 provinces held"."""
        assert get_formation_watch(world, "Holland")["progress"] == (
            "0 of 1 province held")

    def test_both_progress_surfaces_share_one_source(self, world):
        """The agenda payload's copy and the watcher's copy are the same
        string for the same nation — they were two hardcoded literals."""
        _free(world, "Holland")
        payload = build_agenda_payload("Holland", world)
        assert (payload["forms"]["progress"]
                == get_formation_watch(world, "Holland")["progress"])


# ══════════════════════════════════════════════════════════════════════════
# §11.9 — the threat panel NAMES the grievance (at its call sites)
# ══════════════════════════════════════════════════════════════════════════

class TestThreatLabelCallSites:
    """The label helper was pinned; its two player-facing call sites were
    not — reverting either to the static map failed no test, while the
    entire §11.9 payoff rests on them."""

    def test_the_balance_of_europe_panel_names_the_grievance(self, world):
        from backend.game_logic.coalition import process_coalition_turn
        from backend.game_logic.diplomatic_ledger import (
            _build_balance_of_europe,
        )
        _the_poland_chain(world)
        process_coalition_turn(world)
        labels = [s["label"] for s
                  in _build_balance_of_europe(world)["threat_sources_this_turn"]]
        assert "The Polish Question" in labels, labels

    def test_the_advisory_names_the_grievance(self, world):
        from backend.game_logic.coalition import process_coalition_turn
        from backend.game_logic.diplomatic_advisory import _assess_situation
        _the_poland_chain(world)
        process_coalition_turn(world)
        assert "The Polish Question" in str(_assess_situation(world))


# ══════════════════════════════════════════════════════════════════════════
# D1 — one grievance, one voice: the flat +1 §11.9 actually blesses
# ══════════════════════════════════════════════════════════════════════════

class TestGrudgeFlatAmount:
    """§11.9: "a derived threat contributor `formation_grudge` adds
    `+1/turn`". NA-6a scaled the amount by aggrieved-court count, which
    was never blessed and let the earliest formation swallow the whole
    `AGENDA_GRUDGE_CAP` — so "The Polish Question" and "The Roman
    Question" could never render together, defeating the per-formation
    source key. A first fix made allocation a floor-first fair share,
    which restored the naming but left the amount context-dependent (a
    lone Poland showed +2 and dropped to +1 when an unrelated republic
    was erected). Flat +1 is the spec-literal reading and holds still."""

    def _two_formations(self, monkeypatch):
        from backend.game_logic import formations as mod
        monkeypatch.setattr(mod, "_formation_grudges", lambda _w: [
            {"tag": "DuchyOfWarsaw", "label": "The Polish Question",
             "courts": ["Prussia", "Russia"]},
            {"tag": "RomanRepublic", "label": "The Roman Question",
             "courts": ["Austria", "Spain"]},
        ])

    def test_two_questions_render_together(self, world, monkeypatch):
        from backend.game_logic.agendas import AGENDA_GRUDGE_CAP
        from backend.game_logic.formations import (
            get_formation_grudge_contributions,
        )
        self._two_formations(monkeypatch)
        rows = get_formation_grudge_contributions(world, AGENDA_GRUDGE_CAP)
        assert [r["label"] for r in rows] == [
            "The Polish Question", "The Roman Question"]
        assert [r["amount"] for r in rows] == [1, 1], (
            "one grievance, one voice — and a row that emits 0 is dropped "
            "and never seen")

    def test_the_shared_cap_still_holds(self, world, monkeypatch):
        from backend.game_logic.agendas import AGENDA_GRUDGE_CAP
        from backend.game_logic.formations import get_formation_grudge_threat
        self._two_formations(monkeypatch)
        for budget in range(0, AGENDA_GRUDGE_CAP + 1):
            emitted = get_formation_grudge_threat(world, budget)
            assert emitted <= budget
            assert emitted + (AGENDA_GRUDGE_CAP - budget) <= AGENDA_GRUDGE_CAP

    def test_the_amount_never_depends_on_court_count(self, world, monkeypatch):
        """The context-dependence guard. A grievance against four courts
        weighs the same as one against a single court — otherwise the
        panel shows a number moving for reasons the player cannot see."""
        from backend.game_logic import formations as mod
        for courts in (["Prussia"], ["Prussia", "Russia"],
                       ["Prussia", "Russia", "Austria", "Spain"]):
            monkeypatch.setattr(mod, "_formation_grudges", lambda _w, c=courts: [
                {"tag": "DuchyOfWarsaw", "label": "The Polish Question",
                 "courts": list(c)}])
            rows = mod.get_formation_grudge_contributions(world, 2)
            assert [r["amount"] for r in rows] == [1], courts

    def test_a_lone_formation_holds_still_across_budgets(
            self, world, monkeypatch):
        from backend.game_logic import formations as mod
        monkeypatch.setattr(mod, "_formation_grudges", lambda _w: [
            {"tag": "DuchyOfWarsaw", "label": "The Polish Question",
             "courts": ["Prussia", "Russia"]}])
        expected = {0: [], 1: [1], 2: [1], 3: [1]}
        for budget, amounts in expected.items():
            rows = mod.get_formation_grudge_contributions(world, budget)
            assert [r["amount"] for r in rows] == amounts, budget

    def test_grievances_beyond_the_cap_are_dropped_not_silently_merged(
            self, world, monkeypatch):
        """`AGENDA_GRUDGE_CAP` now reads as what it is: how many named
        questions can weigh on Europe at once. A third emits nothing —
        real and deliberate, and debug-logged rather than merged into a
        neighbour's number."""
        from backend.game_logic import formations as mod
        monkeypatch.setattr(mod, "_formation_grudges", lambda _w: [
            {"tag": "A", "label": "First", "courts": ["Prussia"]},
            {"tag": "B", "label": "Second", "courts": ["Russia"]},
            {"tag": "C", "label": "Third", "courts": ["Austria"]},
        ])
        rows = mod.get_formation_grudge_contributions(world, 2)
        assert [r["label"] for r in rows] == ["First", "Second"]
        assert sum(r["amount"] for r in rows) == 2

    def test_allocation_is_deterministic(self, world, monkeypatch):
        """Order comes from `_formation_grudges` ((turn, tag)), so the
        same world always splits the budget the same way."""
        from backend.game_logic.formations import (
            get_formation_grudge_contributions,
        )
        self._two_formations(monkeypatch)
        first = get_formation_grudge_contributions(world, 2)
        for _ in range(5):
            assert get_formation_grudge_contributions(world, 2) == first


# ══════════════════════════════════════════════════════════════════════════
# The formables war_id carry-over must never leak between flows
# ══════════════════════════════════════════════════════════════════════════

class TestNoInertWarIdCarryOver:
    """The first audit pass threaded the Formables deep link's qualifying
    `war_id` into `open_settlement`, believing it closed a multi-war
    mis-pick. The audit-of-the-audit proved it INERT: an AVAILABLE
    `open_settlement` always carries its own `war_id`, because
    `diplomacy.py` forces `available: false` for BOTH the
    multi-war-ambiguity and no-common-war cases — so the fallback could
    never reach the POST. It was removed rather than left looking like a
    fix; it was pure leakable state (it had already needed three separate
    clears to stay safe). The real gap is routed as NAD-4.
    """

    def test_the_inert_carry_over_is_gone(self):
        from tests.test_nation_agendas_formables import _read
        assert "_formable_war_id" not in _read("scripts/diplomacy_wizard.gd")

    def test_the_backend_invariant_that_makes_it_inert_still_holds(self):
        """The removal is only safe while an available open_settlement
        always carries a war_id. Pin the two branches that guarantee it."""
        import inspect

        from backend.game_logic import diplomacy
        source = inspect.getsource(diplomacy)
        block = source[source.index("multi_war_ambiguity = False"):]
        block = block[:block.index("elif settlement_war_id:")]
        assert '"error": "multi_war_ambiguity"' in block
        assert '"available": False' in block, (
            "multi-war ambiguity must disable the action, or a deep link "
            "could post a settlement with no war_id")

    def test_the_deep_link_still_routes_to_the_court(self):
        from tests.test_nation_agendas_formables import _read
        wizard = _read("scripts/diplomacy_wizard.gd")
        assert "_on_nation_selected.bind(court)" in wizard
        assert "NAD-4" in wizard, "the routed gap keeps its pointer"


# ══════════════════════════════════════════════════════════════════════════
# §11.9 "while the formation STANDS" — no grievance for a dead nation
# ══════════════════════════════════════════════════════════════════════════

class TestTheWoundLapsesWithTheNation:
    """`_eliminate_nation` deliberately does NOT prune `nation_formations`
    (the record is the permanent historical latch), so the grudge
    derivation has to carry the liveness check itself. Without it a Poland
    conquered out of existence kept pushing "The Polish Question" +1/turn
    forever — a dead-name grievance on the very panel this slice cleaned.
    """

    def test_a_standing_formation_grieves(self, world):
        from backend.game_logic.formations import (
            get_formation_grudge_contributions, get_formation_grudge_nations,
        )
        _the_poland_chain(world)
        assert get_formation_grudge_contributions(world, 2)
        assert get_formation_grudge_nations(world) == ["Prussia", "Russia"]

    def test_a_conquered_formation_grieves_no_longer(self, world):
        """Berlin and St Petersburg got what they wanted."""
        from backend.game_logic.formations import (
            get_formation_grudge_contributions, get_formation_grudge_nations,
        )
        _the_poland_chain(world)
        _hand_over(world, "Prussia", ["Posen", "Lithuania", "Volhynia"])
        assert "DuchyOfWarsaw" not in set(world.get_active_nations())
        assert get_formation_grudge_contributions(world, 2) == []
        assert get_formation_grudge_nations(world) == []

    def test_the_record_itself_survives_the_conquest(self, world):
        """The wound lapses; the HISTORY does not. The record is what
        keeps the pay-once latch honest across a later re-erection."""
        _the_poland_chain(world)
        _hand_over(world, "Prussia", ["Posen", "Lithuania", "Volhynia"])
        record = get_formation_record(world, "DuchyOfWarsaw")
        assert record is not None
        assert record["rewarded"] is True

    def test_the_panel_stops_naming_the_dead(self, world):
        """End to end: the threat panel drops the row entirely."""
        from backend.game_logic.coalition import process_coalition_turn
        from backend.game_logic.diplomatic_ledger import (
            _build_balance_of_europe,
        )
        _the_poland_chain(world)
        process_coalition_turn(world)
        assert any("Polish Question" in s["label"] for s
                   in _build_balance_of_europe(world)["threat_sources_this_turn"])
        _hand_over(world, "Prussia", ["Posen", "Lithuania", "Volhynia"])
        world.threat_sources_this_turn = []
        process_coalition_turn(world)
        assert not any("Polish Question" in s["label"] for s
                       in _build_balance_of_europe(world)["threat_sources_this_turn"])


# ══════════════════════════════════════════════════════════════════════════
# The record-shape truth table (every shape any commit ever wrote)
# ══════════════════════════════════════════════════════════════════════════

class TestRecordShapeTruthTable:
    """Two independent questions are read off one record: "may this tag
    still proclaim?" and "has its treasury already been filled?". They are
    answered by `_is_creation_record` and `_has_been_rewarded`, and they
    must agree for every record shape ANY version of this code has
    written — including the one-commit-wide `4c78284` intermediate, which
    stamped `formed` without `rewarded` under a design reversed the same
    day."""

    SHAPES = [
        # (name, record, is_creation, been_rewarded)
        ("HEAD formed",
         {"id": "risorgimento", "sponsor": "", "turn": 3,
          "formed": True, "rewarded": True}, False, True),
        ("HEAD creation",
         {"id": "DuchyOfWarsaw", "template": "DuchyOfWarsaw",
          "sponsor": "France", "turn": 1}, True, False),
        ("HEAD C->T formed",
         {"id": "commonwealth_restored", "template": "DuchyOfWarsaw",
          "formed": True, "rewarded": True}, False, True),
        ("pre-audit formed",
         {"id": "risorgimento", "sponsor": "", "turn": 3}, False, True),
        ("pre-audit C->T formed",
         {"id": "commonwealth_restored", "template": "DuchyOfWarsaw"},
         False, True),
        ("pre-audit creation",
         {"id": "DuchyOfWarsaw", "template": "DuchyOfWarsaw"}, True, False),
        # The one-commit-wide `4c78284` intermediate. Reads as FORMED:
        # deliberately NOT migrated, because "formed on a creation-shaped
        # record" is indistinguishable from the id/template COLLISION the
        # marker exists to defeat. Such a save keeps that commit's own
        # intended freeze rather than re-opening Proclamation spam.
        ("4c78284 intermediate",
         {"id": "DuchyOfWarsaw", "template": "DuchyOfWarsaw",
          "formed": True}, False, True),
    ]

    @pytest.mark.parametrize("name,record,creation,rewarded", SHAPES)
    def test_the_two_questions_agree(self, name, record, creation, rewarded):
        from backend.game_logic.formations import (
            _has_been_rewarded, _is_creation_record,
        )
        assert _is_creation_record(record) is creation, name
        assert _has_been_rewarded(record) is rewarded, name

    def test_no_shape_can_both_dream_and_be_unpaid_after_forming(self):
        """The dangerous combination: a record that reads as "may still
        proclaim" AND "never paid" when a formation already happened would
        re-open the windfall farm."""
        from backend.game_logic.formations import (
            _has_been_rewarded, _is_creation_record,
        )
        for name, record, _c, _r in self.SHAPES:
            if record.get("formed") or record.get("rewarded"):
                assert _has_been_rewarded(record), name
            if _is_creation_record(record) and not _has_been_rewarded(record):
                # Legitimate only for a tag that has NEVER formed: no
                # `formed` marker anywhere in its history.
                assert not record.get("formed"), name


class TestCreationPathAggrievedBlow:
    """The creation path re-strikes too, and consistently with the
    formation path — found by the audit-of-the-audit, which caught the
    comment there claiming the opposite. The Roman Republic is the only
    shipped template with a template-level `aggrieved` list, so it is the
    only one that exercises this."""

    def _carve_rome(self, world):
        _carve_ready(world, "RomanRepublic", "PapalStates", "France")
        return create_client_nation(world, "RomanRepublic", "France",
                                    ceded_from="PapalStates")

    def test_the_first_erection_offends_the_catholic_courts(self, world):
        payload = self._carve_rome(world)
        assert sorted(payload["aggrieved"]) == ["Austria", "Spain"]

    def test_a_re_erection_offends_them_again(self, world):
        """Consistent with `_proclaim`: the §11.9 wound lapses when the
        client is conquered away, so raising it again is a fresh
        sacrilege. Never a farm — it costs the CARVER relations."""
        self._carve_rome(world)
        _free(world, "RomanRepublic")
        _hand_over(world, "Austria", ["Rome"])
        assert "RomanRepublic" not in set(world.get_active_nations())
        again = self._carve_rome(world)
        assert sorted(again["aggrieved"]) == ["Austria", "Spain"]
