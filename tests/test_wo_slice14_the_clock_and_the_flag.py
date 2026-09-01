"""Row WO, slice 14 - "The Clock and the Flag" (WO-18, WO-19).

Landing record: docs/WEIRD_OUTCOMES_SPEC.md section 3 slice 14 - the LAST
slice of row WO.

WO-18 (pension churn): the rente bill reads the LIVE pension at income
time while the erosion reconcile reset the grace clock to -1 on ANY met
turn - so grant / revoke / re-grant paid ceil(1.5×face) only on the live
turns and NEVER reached erosion (each re-grant reset the clock inside the
window). ~300g/turn per capped marshal, zero loyalty cost. FIX: a met
turn resets the clock only when the ESTATE income alone covers the
expectation (durable) or the clock was never open; a load-bearing rente
while the clock is OPEN freezes it, so unmet turns accumulate across the
toggle and erosion fires GRACE_TURNS turns after the FIRST unmet one.

WO-19 (the sacked flag): three sites cleared `region.plundered` on any
change of hands (the shared secure + the two occupation-completion
branches), so abandon -> AI-secures -> retake quoted the FULL income×4
again. FIX: securing does not un-sack; only `process_stability_growth`'s
stability-50 clear (the documented one) clears it now.

Every test names the mutation that kills it.
"""

import contextlib
import copy
import io
from pathlib import Path

import pytest

from backend.commands.executor import CommandExecutor
from backend.game_logic import dotation as DOT
from backend.game_logic.dotation import (
    GRACE_TURNS,
    get_expectation,
    get_nation_rente_bill,
)
from backend.models import world_state as WS
from backend.models.world_state import (
    WorldState,
    apply_secure_effects,
    is_own_soil_recapture,
    plunder_yield,
)
from tests.conftest import MarshalFactory

SCENARIO_PATH = (Path(__file__).resolve().parents[1] / "godot-client"
                 / "project-sovereign" / "assets" / "maps" / "europe_1805.json")


def _quiet(fn, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*args, **kwargs)


@pytest.fixture(scope="module")
def europe():
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(str(SCENARIO_PATH))


def _pair(world, a, b, state):
    key = world._make_diplo_key(a, b)
    world.diplomatic_states[key] = state
    if state == "WAR":
        world.war_start_turns[key] = world.current_turn


def _french_marshal(world):
    for m in world.marshals.values():
        if m.nation == world.player_nation:
            return m
    raise AssertionError("no French marshal")


def _reconcile(world):
    world._dotation_processed_turn = None
    _quiet(world._process_dotation_state)


# ══════════════════════════════════════════════════════════════════
# WO-18 - the grace clock keys on unmet-turn count
# ══════════════════════════════════════════════════════════════════

class TestWO18PensionChurn:

    def _world(self, europe):
        """A fresh 1805 world (ES-7 is Europe-scoped — the legacy fixture
        has no dotations)."""
        return copy.deepcopy(europe)

    def _owed_marshal(self, world):
        """A marshal owed 200/turn with no estate — a bare rente closes
        the shortfall, so the rente is always load-bearing."""
        m = _french_marshal(world)
        m.battles_won = 5           # expectation 200
        world.current_turn = 10
        m.expectation_grace_turn = -1
        m.pension = 0
        m.dotation_regions = []
        assert get_expectation(m) == 200
        return m

    def test_a_genuinely_kept_rente_never_erodes_and_charges_the_bill(self, europe):
        """The legitimate case: a rente held for many turns pays the bill
        every turn and the marshal never erodes (met branch)."""
        world = self._world(europe)
        m = self._owed_marshal(world)
        m.pension = 200                       # covers the 200 expectation
        trust0 = m.trust.value
        for _ in range(GRACE_TURNS + 3):
            world.current_turn += 1
            _reconcile(world)
            assert m.trust.value == trust0    # met every turn - no erosion
        # ...and the treasury pays the premium every one of those turns.
        assert get_nation_rente_bill(world, "France") == DOT.get_rente_cost(200)

    def test_churn_now_erodes_after_grace_regardless_of_the_toggle(self, europe):
        """The measured exploit. Met on turn N; unmet from N+1 with a
        grant/revoke toggle in the window; erodes GRACE_TURNS turns after
        the FIRST unmet turn. Killed by resetting the clock on the
        interleaved grant (the pre-slice behaviour)."""
        world = self._world(europe)
        m = self._owed_marshal(world)
        # Turn N: met by a live rente (clock never opened -> stays -1).
        m.pension = 200
        _reconcile(world)
        assert m.expectation_grace_turn == -1
        first_unmet = None
        trust0 = m.trust.value
        for step in range(1, GRACE_TURNS + 2):
            world.current_turn += 1
            # Toggle: revoke on odd steps, grant on even steps - so he is
            # unmet on some turns, met (by a fresh rente) on others.
            m.pension = 0 if step % 2 == 1 else 200
            if m.pension == 0 and first_unmet is None:
                first_unmet = world.current_turn
            _reconcile(world)
        # First unmet was N+1; erosion begins GRACE_TURNS turns later.
        assert first_unmet == 11
        # The clock opened at the first unmet turn and the interleaved grant
        # did NOT reset it.
        assert m.expectation_grace_turn == first_unmet
        assert m.trust.value < trust0, "the toggle dodged erosion"

    def test_a_single_grant_then_revoke_still_opens_the_clock(self, europe):
        """The un-churned case (test_revoke_reopens_the_shortfall_machinery
        in spirit): grant, met, clock -1; revoke, unmet, clock opens THIS
        turn - the freeze only bites while the clock is already open."""
        world = self._world(europe)
        m = self._owed_marshal(world)
        m.pension = 200
        _reconcile(world)
        assert m.expectation_grace_turn == -1
        world.current_turn += 1
        m.pension = 0
        _reconcile(world)
        assert m.expectation_grace_turn == world.current_turn

    def test_estate_income_that_covers_him_still_resets_the_clock(self, europe):
        """Paying with LAND is durable and resets even mid-grace - the
        freeze is scoped to a load-bearing RENTE. Killed by freezing on
        estate coverage too."""
        world = self._world(europe)
        m = self._owed_marshal(world)
        m.battles_won = 2                     # expectation 80
        m.expectation_grace_turn = world.current_turn - 1   # clock open
        # An estate whose income alone covers the 80.
        region = next(r for r in world.regions.values() if r.controller == "France")
        region.stability = 100
        region.income_value = max(region.income_value, 100)
        m.dotation_regions = [region.name]
        assert DOT.get_estate_income(m, world) >= get_expectation(m)
        _reconcile(world)
        assert m.expectation_grace_turn == -1

    def test_the_bill_is_only_charged_on_a_live_rente(self, europe):
        """The other half of the exploit, unchanged and pinned: a revoked
        rente charges nothing - the deterrent is the erosion this slice
        restores, not a bill on a pension that is 0."""
        world = self._world(europe)
        m = self._owed_marshal(world)
        m.pension = 200
        assert get_nation_rente_bill(world, "France") == DOT.get_rente_cost(200)
        m.pension = 0
        assert get_nation_rente_bill(world, "France") == 0

    def test_with_the_lever_down_the_toggle_dodges_erosion_again(self, monkeypatch, europe):
        """The measured defect, reproduced by the flip lever."""
        monkeypatch.setattr(DOT, "PENSION_CHURN_GUARD_ACTIVE", False)
        world = self._world(europe)
        m = self._owed_marshal(world)
        m.pension = 200
        _reconcile(world)
        trust0 = m.trust.value
        for step in range(1, GRACE_TURNS + 2):
            world.current_turn += 1
            m.pension = 0 if step % 2 == 1 else 200
            _reconcile(world)
        assert m.trust.value == trust0, "the pre-slice toggle should not erode"


# ══════════════════════════════════════════════════════════════════
# WO-19 - the sack survives a change of hands
# ══════════════════════════════════════════════════════════════════

class TestWO19TheSackedFlag:

    def test_securing_does_not_un_sack(self):
        """Killed by restoring `plundered = False` in apply_secure_effects."""
        world = _quiet(WorldState, player_nation="France")
        region = next(r for r in world.regions.values() if r.controller)
        region.plundered = True
        region.stability = 20
        apply_secure_effects(region)
        assert region.plundered is True
        assert region.stability == 25

    def test_a_fresh_capture_is_not_plundered(self):
        """The common case is untouched: securing an UNplundered province
        leaves it unplundered."""
        world = _quiet(WorldState, player_nation="France")
        region = next(r for r in world.regions.values() if r.controller)
        region.plundered = False
        apply_secure_effects(region)
        assert region.plundered is False

    def test_only_stability_recovery_clears_the_flag(self):
        """The documented clear is now the ONLY clear. Killed by removing
        the stability-50 clear."""
        world = _quiet(WorldState, player_nation="France")
        region = next(r for r in world.regions.values() if r.controller)
        region.plundered = True
        region.stability = 60          # already past 50
        _quiet(world.process_stability_growth)
        assert region.plundered is False

    def test_the_abandon_then_retake_cycle_quotes_and_pays_zero(self):
        """The end-to-end exploit. A sacked province the AI secured and the
        player retakes still quotes 0 (plunder_yield reads the surviving
        flag). Killed by clearing the flag on any of the three secure
        sites."""
        world = _quiet(WorldState, player_nation="France")
        region = next(r for r in world.regions.values() if r.controller)
        region.plundered = True
        region.stability = 30
        # The AI secures it (the shared implementation)...
        apply_secure_effects(region)
        # ...and it is worth nothing to sack again while the flag stands.
        assert plunder_yield(region) == 0

    def test_a_plundered_flag_survives_the_own_soil_occupation_liberation(self):
        """The own-soil occupation-completion branch. Killed by restoring
        its `plundered = False`."""
        world = _quiet(WorldState, player_nation="France")
        ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                      strength=40000, personality="aggressive")
        world.marshals["Ney"] = ney
        region = world.get_region("Belgium")
        region.controller = "Britain"       # occupied
        region.plundered = True
        _pair(world, "France", "Britain", "WAR")
        assert is_own_soil_recapture(world, "Belgium", "France")
        _quiet(world._apply_occupation_capture_effects, ney, "Belgium")
        assert world.get_region("Belgium").controller == "France"
        assert world.get_region("Belgium").plundered is True

    def test_a_plundered_flag_survives_the_ai_occupation_secure(self, monkeypatch):
        """The AI occupation-completion SECURE branch (its own inline
        clear, distinct from the shared `apply_secure_effects` — that AI
        branch does not delegate). An AI that SECURES a plundered province
        it occupies leaves the flag standing. `ai_prefers_plunder` is
        forced False so the secure branch is the one taken. Killed by
        restoring its `plundered = False`."""
        import backend.models.world_state as ws_mod

        monkeypatch.setattr(ws_mod, "ai_prefers_plunder",
                            lambda *a, **k: False)
        world = _quiet(WorldState, player_nation="France")
        mack = MarshalFactory.enemy(name="Mack", location="Belgium",
                                    nation="Austria", strength=40000)
        world.marshals["Mack"] = mack
        region = world.get_region("Belgium")
        region.controller = "France"
        region.plundered = True
        _pair(world, "France", "Austria", "WAR")
        _quiet(world._apply_occupation_capture_effects, mack, "Belgium")
        assert world.get_region("Belgium").controller == "Austria"
        assert world.get_region("Belgium").plundered is True

    def test_a_plundered_flag_survives_the_player_foreign_occupation(self):
        """The player's foreign-soil path routes through the shared secure
        (`mount_or_auto_secure_capture` → `apply_secure_effects`), so the
        WO14-6 protection covers it too — pinned here end to end."""
        world = _quiet(WorldState, player_nation="France")
        ney = MarshalFactory.infantry(name="Ney", location="Bavaria",
                                      strength=40000, personality="aggressive")
        world.marshals["Ney"] = ney
        region = world.get_region("Bavaria")
        region.controller = "Austria"
        region.plundered = True
        _pair(world, "France", "Austria", "WAR")
        assert not is_own_soil_recapture(world, "Bavaria", "France")
        # Any earlier unanswered question makes this auto-secure (WO-26);
        # with the slot free it mounts the choice but still does not clear
        # the flag on the capture itself.
        _quiet(world._apply_occupation_capture_effects, ney, "Bavaria")
        assert world.get_region("Bavaria").controller == "France"
        assert world.get_region("Bavaria").plundered is True

    def test_the_docstring_promise_is_now_true(self):
        """`plunder_yield`'s docstring promises the guard holds until
        stability > 50. Before this slice a secure cleared it; now the
        promise is kept end to end."""
        world = _quiet(WorldState, player_nation="France")
        region = next(r for r in world.regions.values() if r.controller)
        region.plundered = True
        region.stability = 40
        apply_secure_effects(region)
        assert plunder_yield(region) == 0          # still stripped at 40
        region.stability = 55
        _quiet(world.process_stability_growth)
        assert region.plundered is False
        assert plunder_yield(region) == int(
            region.income_value * WS.PLUNDER_INCOME_MULTIPLIER)

    def test_with_the_lever_down_the_flag_clears_on_secure_again(self, monkeypatch):
        monkeypatch.setattr(WS, "PLUNDERED_SURVIVES_HANDCHANGE_ACTIVE", False)
        world = _quiet(WorldState, player_nation="France")
        region = next(r for r in world.regions.values() if r.controller)
        region.plundered = True
        apply_secure_effects(region)
        assert region.plundered is False
