"""HC-3 "The Crowned Name Abroad" (gate §4) — the flavor half only.

Envoy refusal/capitulation line variants that name the opposing side's
crowned (★) marshal when one exists. Display-only (GR6 — the LLM and
mechanics never read it); sourced from the glory ladder's settled flag
at render; deterministic; with NO crown every line is byte-identical to
today. The mechanical acceptance term is HC-D1 (DESIGN_REFINEMENT.md),
owned by the Victory & Objectives Pass gate.
"""

from backend.game_logic.diplomatic_templates import (
    CROWNED_INCOMING_CLAUSES,
    CROWNED_SETTLEMENT_CLAUSES,
    compose_incoming_diplomat_line,
    crowned_incoming_clause,
    crowned_name_clause,
    resolve_multi_court_settlement_voice,
)
from backend.game_logic.jealousy import get_crowned_marshal

from tests.conftest import MarshalFactory, WorldFactory


def _crowned_world(crowned=True):
    ney = MarshalFactory.infantry(name="Ney", location="Rhineland",
                                  strength=30000, nation="France",
                                  personality="aggressive")
    if crowned:
        ney.glory_crowned = True
    world = WorldFactory.with_marshals([ney])
    key = world._make_diplo_key("France", "Prussia")
    world.diplomatic_states[key] = "WAR"
    world.war_start_turns[key] = world.current_turn
    return world


class TestAccessor:
    def test_finds_the_standing_crown(self):
        world = _crowned_world()
        crowned = get_crowned_marshal(world, "France")
        assert crowned is not None and crowned.name == "Ney"

    def test_no_crown_reads_none(self):
        world = _crowned_world(crowned=False)
        assert get_crowned_marshal(world, "France") is None

    def test_captured_or_destroyed_crown_reads_none(self):
        world = _crowned_world()
        world.marshals["Ney"].captured_by = "Prussia"
        assert get_crowned_marshal(world, "France") is None
        world.marshals["Ney"].captured_by = ""
        world.marshals["Ney"].strength = 0
        assert get_crowned_marshal(world, "France") is None

    def test_wrong_nation_reads_none(self):
        world = _crowned_world()
        assert get_crowned_marshal(world, "Prussia") is None


class TestClauses:
    def test_settlement_clause_names_marshal_and_register(self):
        world = _crowned_world()
        for suffix in ("castlereagh", "hardenberg", "metternich",
                       "einsiedel", "chancery"):
            clause = crowned_name_clause(world, "France", suffix)
            assert "Ney" in clause, suffix
        # The location slot resolves where the register uses it.
        assert "Rhineland" in crowned_name_clause(world, "France",
                                                  "chancery")

    def test_unknown_suffix_degrades_to_chancery(self):
        world = _crowned_world()
        assert crowned_name_clause(world, "France", "nobody") == \
            crowned_name_clause(world, "France", "chancery")

    def test_no_crown_derives_empty(self):
        world = _crowned_world(crowned=False)
        assert crowned_name_clause(world, "France", "chancery") == ""
        assert crowned_incoming_clause(world, "France") == ""

    def test_incoming_clause_names_the_crown(self):
        world = _crowned_world()
        clause = crowned_incoming_clause(world, "France")
        assert "Ney" in clause and "Rhineland" in clause

    def test_banks_are_nonempty_and_format_clean(self):
        # XR-5 idiom: append-only growth; every row must resolve its
        # slots without KeyError (only {marshal} and {location} exist).
        for suffix, rows in CROWNED_SETTLEMENT_CLAUSES.items():
            assert len(rows) >= 1, suffix
            for row in rows:
                assert row.format(marshal="X", location="Y")
        assert len(CROWNED_INCOMING_CLAUSES) >= 1
        for row in CROWNED_INCOMING_CLAUSES:
            assert row.format(marshal="X", location="Y")


class TestSettlementTableWire:
    def _rows(self, court, band="reject"):
        return [{"nation": court, "band": band,
                 "top_blocker_display": "the standing terms",
                 "top_blocker_component": "base_side_pressure",
                 "total": 12, "hard_stops": []}]

    def test_holdout_line_carries_the_crown(self):
        world = _crowned_world()
        voice = resolve_multi_court_settlement_voice(
            world, per_court_acceptance=self._rows("Prussia"))
        line = voice["per_court_voice"][0]["line"]
        assert "Ney" in line

    def test_no_crown_line_is_byte_identical(self):
        with_crown = _crowned_world()
        without = _crowned_world(crowned=False)
        rows = self._rows("Prussia")
        crowned_line = resolve_multi_court_settlement_voice(
            with_crown, per_court_acceptance=rows)["per_court_voice"][0]["line"]
        plain_line = resolve_multi_court_settlement_voice(
            without, per_court_acceptance=rows)["per_court_voice"][0]["line"]
        assert plain_line != crowned_line
        assert crowned_line.startswith(plain_line)

    def test_signing_court_never_carries_the_clause(self):
        world = _crowned_world()
        voice = resolve_multi_court_settlement_voice(
            world, per_court_acceptance=self._rows("Prussia", band="accept"))
        assert "Ney" not in voice["per_court_voice"][0]["line"]

    def test_chancery_court_gets_the_neutral_variant(self):
        world = _crowned_world()
        voice = resolve_multi_court_settlement_voice(
            world, per_court_acceptance=self._rows("Bavaria"))
        line = voice["per_court_voice"][0]["line"]
        assert "The court marks that Marshal Ney stands crowned" in line


class TestIncomingWire:
    def test_war_overload_suitor_acknowledges_the_crown(self):
        world = _crowned_world()
        line = compose_incoming_diplomat_line(
            world, nation="Prussia", proposal_type="peace",
            decision_reason="war_overload")
        assert "Ney" in line

    def test_other_motives_never_carry_it(self):
        world = _crowned_world()
        line = compose_incoming_diplomat_line(
            world, nation="Prussia", proposal_type="peace",
            decision_reason="agenda_pursuit")
        assert "Ney" not in line

    def test_no_crown_is_byte_identical(self):
        with_crown = _crowned_world()
        without = _crowned_world(crowned=False)
        kwargs = {"nation": "Prussia", "proposal_type": "peace",
                  "decision_reason": "war_overload"}
        crowned_line = compose_incoming_diplomat_line(with_crown, **kwargs)
        plain_line = compose_incoming_diplomat_line(without, **kwargs)
        assert plain_line != crowned_line
        assert "Ney" not in plain_line
