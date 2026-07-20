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

    def test_but_the_world_pays_only_once(self, world):
        """...and that is the whole point of the `rewarded` latch. Before
        the audit the re-carve path overwrote the record wholesale, so the
        second proclamation banked a second +2,000 gold and struck every
        aggrieved court a second −30. Now the moment repeats and the
        payment does not."""
        self._lose_and_recarve(world)
        before = world.nation_gold["DuchyOfWarsaw"]
        payload = process_formations(world)[0]
        assert payload["gold"] == 0
        assert payload["aggrieved"] == []
        assert payload["regions_lifted"] == 0
        assert world.nation_gold["DuchyOfWarsaw"] == before

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
# D1 — the named grievance is multi-slot (floor-first fair share)
# ══════════════════════════════════════════════════════════════════════════

class TestGrudgeFairShare:
    """Greedy allocation made §11.9's whole point unreachable in shipped
    data: `AGENDA_GRUDGE_CAP` is 2 and each authored formation aggrieves
    exactly two courts, so the earliest formation swallowed the entire
    remainder and every later one emitted 0 and was dropped. Fixed by
    allocation, not by moving the blessed cap."""

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
        assert all(r["amount"] >= 1 for r in rows), (
            "a named grievance that emits 0 is dropped and never seen")

    def test_the_shared_cap_still_holds(self, world, monkeypatch):
        from backend.game_logic.agendas import AGENDA_GRUDGE_CAP
        from backend.game_logic.formations import get_formation_grudge_threat
        self._two_formations(monkeypatch)
        for budget in range(0, AGENDA_GRUDGE_CAP + 1):
            emitted = get_formation_grudge_threat(world, budget)
            assert emitted <= budget
            assert emitted + (AGENDA_GRUDGE_CAP - budget) <= AGENDA_GRUDGE_CAP

    def test_a_lone_formation_is_unchanged(self, world, monkeypatch):
        """Regression guard: the floor then tops straight back up, so the
        single-formation amounts the slice pinned do not move."""
        from backend.game_logic import formations as mod
        monkeypatch.setattr(mod, "_formation_grudges", lambda _w: [
            {"tag": "DuchyOfWarsaw", "label": "The Polish Question",
             "courts": ["Prussia", "Russia"]}])
        expected = {0: [], 1: [1], 2: [2], 3: [2]}
        for budget, amounts in expected.items():
            rows = mod.get_formation_grudge_contributions(world, budget)
            assert [r["amount"] for r in rows] == amounts, budget

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
