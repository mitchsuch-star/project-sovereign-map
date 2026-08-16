"""Row NP — the promise audit (August 15, 2026).

Every commitment in `docs/NAPOLEON_SPEC.md` and in the 13 NP commit
messages, extracted and verified against code. Record =
`docs/audits/NP_PROMISE_AUDIT_2026_08_15.md`; landing record =
NAPOLEON_SPEC.md §15.9.

These pins cover the defects that audit found. Each one was reproduced at
runtime before the fix was written, and each asserts an APPLIED value or a
RENDERED string — never that a constant exists.
"""

import pytest

from backend.ai.parser_eval import build_llm_game_state, build_world
from backend.commands.executor import CommandExecutor
from backend.commands.parser import (
    CommandParser,
    _SOVEREIGN_ORDER_VERBS,
    normalize_sovereign_address,
)
from backend.game_logic import dispatch as D
from backend.game_logic.diplomacy import (
    displayed_dp_ceiling,
    sovereign_seat_bonus,
)
from backend.models.authority import sovereign_aura_strength
from backend.models.marshal import Marshal


def CE():
    return CommandExecutor()._combat


@pytest.fixture()
def europe():
    return build_world("1805")


# ════════════════════════════════════════════════════════════════════════
# A1 — the aura decays on EVERY path, not only the ordinary attack
# ════════════════════════════════════════════════════════════════════════

class TestTheAuraDimsEverywhere:
    """§15.4 claims `sovereign_aura_strength` is "the single source for
    both" the aura and the fear. It moved the participant stamp and the
    fear and left `_calculate_coordination_context` on a flat 1.0 — and
    that producer is the LAST word on the two paths that never reach the
    participant stamp: the garrison assault and the cavalry charge.
    Measured with the myth wholly broken the Emperor still stormed a
    capital at the full +10%.
    """

    def _stack(self, world, authority):
        nap, ney = world.marshals["Napoleon"], world.marshals["Ney"]
        nap.location = ney.location = "Lorraine"
        world._build_marshal_index()
        world.authority_tracker.authority = authority
        return nap, ney

    @pytest.mark.parametrize("authority", [100, 57, 30])
    def test_context_stamp_is_the_aura_strength_not_a_flag(
            self, europe, authority):
        nap, ney = self._stack(europe, authority)
        expected = sovereign_aura_strength(europe, "France")
        CE()._calculate_coordination_context(nap, europe)
        assert nap.sovereign_presence == pytest.approx(expected)
        assert ney.sovereign_presence == pytest.approx(expected)

    def test_a_broken_aura_grants_nothing_on_the_charge_path(self, europe):
        """The value that broke: at grip 0.0 the modifier must carry no
        presence term at all."""
        nap, _ = self._stack(europe, 30)
        assert sovereign_aura_strength(europe, "France") == 0.0
        CE()._calculate_coordination_context(nap, europe)
        broken = nap.get_attack_modifier(1.0, consume=False)

        full = build_world("1805")
        nap_f, _ = self._stack(full, 100)
        CE()._calculate_coordination_context(nap_f, full)
        intact = nap_f.get_attack_modifier(1.0, consume=False)

        assert intact > broken, "the aura never dimmed on this path"
        assert intact == pytest.approx(
            broken * (1.0 + Marshal.SOVEREIGN_PRESENCE_ATTACK))

    def test_full_authority_is_byte_identical_to_the_old_flag(self, europe):
        """The fix must not move anything while the throne stands."""
        nap, ney = self._stack(europe, 100)
        CE()._calculate_coordination_context(nap, europe)
        assert nap.sovereign_presence == 1.0
        assert ney.sovereign_presence == 1.0

    def test_no_sovereign_still_stamps_nothing(self, europe):
        del europe.marshals["Napoleon"]
        europe._build_marshal_index()
        ney = europe.marshals["Ney"]
        CE()._calculate_coordination_context(ney, europe)
        assert getattr(ney, "sovereign_presence", 0.0) == 0.0


class TestTheMusterQuotesTheAppliedNumber:
    """`presence_note` hardcoded +10% under a comment reading
    "Percentage derives from the consumed constant... Shown = applied"."""

    def _preview(self, world, authority):
        nap, ney = world.marshals["Napoleon"], world.marshals["Ney"]
        nap.location = ney.location = "Lorraine"
        world._build_marshal_index()
        world.authority_tracker.authority = authority
        mack = world.marshals["Mack"]
        return CE()._build_muster_preview(ney, mack, world, {"world": world})

    def test_note_scales_with_the_aura(self, europe):
        full = self._preview(europe, 100).get("presence_note") or ""
        assert "+10%" in full, full

        dim_world = build_world("1805")
        dim = self._preview(dim_world, 57).get("presence_note") or ""
        assert dim, "the note vanished instead of dimming"
        assert "+10%" not in dim, dim
        assert "star dims" in dim, dim

    def test_a_broken_aura_promises_nothing(self, europe):
        assert not self._preview(europe, 30).get("presence_note")


# ════════════════════════════════════════════════════════════════════════
# A2 — a captured sovereign is never announced as destroyed
# ════════════════════════════════════════════════════════════════════════

class TestTheFallClause:
    """`destroy_marshal` returns False when it converts a sovereign to
    CAPTURE (§7.1). The CHARGE copy gated its message on that return; the
    battle and auto-bombardment copies did not.
    """

    def test_a_removed_marshal_is_destroyed(self, europe):
        ney = europe.marshals["Ney"]
        assert "destroyed" in CE()._fall_clause(europe, ney, True)

    def test_a_taken_sovereign_is_taken_not_destroyed(self, europe):
        nap = europe.marshals["Napoleon"]
        europe.capture_marshal(nap, "Austria", context="probe")
        clause = CE()._fall_clause(europe, nap, False)
        assert "destroyed" not in clause.lower(), clause
        assert "taken" in clause.lower(), clause
        assert "Austria" in clause, clause
        assert "the Emperor" in clause, clause

    def test_the_ordinary_survivor_says_nothing(self, europe):
        assert CE()._fall_clause(europe, europe.marshals["Ney"], False) == ""

    def test_the_destruction_sentences_have_exactly_one_home_each(self):
        """Structural: the two copies that shipped the bug composed their
        sentence ahead of `destroy_marshal` and printed it regardless of
        the return. A future copy written that way re-opens the defect,
        so each destruction phrase gets exactly one site — the shared
        clause, or an arm explicitly gated on the removal."""
        import inspect

        from backend.commands import combat_executor as CX
        src = inspect.getsource(CX)

        assert src.count("'s army is destroyed!") == 1, (
            "the army-destroyed sentence has more than one home — route "
            "every copy through _fall_clause")
        assert src.count("The preparatory bombardment destroyed ") == 1
        # ...and that one site is inside the removal-gated arm.
        assert "if auto_kill_removed:" in src
        assert "he was taken on the field" in src, (
            "the auto-bombardment path lost its captured-sovereign arm")

        # the shared clause is genuinely shared
        assert src.count("self._fall_clause(") >= 1
        assert src.count("_fall_clause") >= 3  # def + docstring ref + call


# ════════════════════════════════════════════════════════════════════════
# A3 — the self-marker arm obeys gate (b), and no arm leaks the marker
# ════════════════════════════════════════════════════════════════════════

class TestTheSelfMarkerArm:
    @pytest.mark.parametrize("text", [
        "I will offer an alliance to Prussia myself",
        "I will negotiate with Austria myself",
        "review the terms myself",
        "I want to see the treasury myself",
        "I will handle this myself",
    ])
    def test_no_verb_no_rewrite(self, text):
        assert normalize_sovereign_address(text, "Napoleon") == text

    @pytest.mark.parametrize("text", [
        "march to Belgium myself",
        "attack Wellington in person",
        "I will march to Belgium myself",
        "the Emperor will march to Belgium myself",
        "Davout, march to Belgium myself",
    ])
    def test_the_marker_never_survives(self, text):
        out = normalize_sovereign_address(text, "Napoleon").lower()
        assert "myself" not in out, text
        assert "in person" not in out, text

    def test_the_verb_set_is_the_one_source_for_all_three_arms(self):
        """The Emperor-lead arm shipped with no verb gate; the self-marker
        arm shipped with no verb gate. Both now read the same set, so they
        cannot drift apart a third time."""
        import backend.commands.parser as P
        for pattern in (P._SOVEREIGN_EMPEROR_LEAD_RE,
                        P._SOVEREIGN_FIRST_PERSON_RE,
                        P._SOVEREIGN_BODY_HAS_VERB_RE):
            assert _SOVEREIGN_ORDER_VERBS in pattern.pattern

    def test_a_marshal_addressed_order_keeps_its_marshal(self, europe):
        parser = CommandParser()
        result = parser.parse("Ney, march to Swabia myself",
                              build_llm_game_state(europe), world=europe)
        assert result["command"]["marshal"] == "Ney"
        assert result["command"]["target"] == "Swabia"


# ════════════════════════════════════════════════════════════════════════
# A4 — the Seat: one beat per departure, and an honest denominator
# ════════════════════════════════════════════════════════════════════════

class TestTheSeat:
    def test_the_shown_ceiling_includes_the_seat(self, europe):
        assert sovereign_seat_bonus(europe, "France") == 1
        europe.advance_turn()
        assert europe.diplomatic_points == displayed_dp_ceiling(europe), (
            "the HUD read 'DP: 6/5' — a number over its own maximum")

    def test_the_ceiling_is_bare_without_a_sovereign(self, europe):
        base = int(europe.max_diplomatic_points)
        del europe.marshals["Napoleon"]
        europe._build_marshal_index()
        assert displayed_dp_ceiling(europe) == base

    def test_the_ceiling_falls_when_he_rides_out(self, europe):
        base = int(europe.max_diplomatic_points)
        europe.marshals["Napoleon"].location = "Lorraine"
        europe._build_marshal_index()
        assert displayed_dp_ceiling(europe) == base

    def test_the_field_beat_fires_once_across_every_live_war(self, europe):
        """It used to `break` after the first unnoted war, so a court in
        two live war instances got the same beat on consecutive turns
        while the Emperor simply stayed afield."""
        europe.marshals["Napoleon"].location = "Lorraine"
        europe._build_marshal_index()
        # a second live war instance France is a party to
        live = [w for w in europe.war_instances.values()
                if w.get("ended_turn") is None
                and "France" in (w.get("active_participants") or [])]
        assert live, "fixture has no live French war"
        second = dict(live[0])
        second["emperor_field_noted"] = False
        europe.war_instances["war_probe"] = second

        fired = []
        for _ in range(3):
            europe.advance_turn()
            if "taken the field" in str(D.build_morning_dispatch(europe)):
                fired.append(europe.current_turn)
        assert len(fired) == 1, (
            f"the departure beat fired on turns {fired} — once per war "
            f"instance instead of once per departure")
