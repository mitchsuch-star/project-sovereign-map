"""WO slice 3 — the garrison floor (WEIRD_OUTCOMES_SPEC §3 slice 3).

WO-3: a detachment garrison stalled at ONE man forever. Garrison losses
were floored at `int(garrison × 0.10)`, which truncates to 0 below ten men,
while the attacker kept paying his 2% floor; a detachment collapses only at
`<= 0`. Measured: "Wellington assaults the Normandy garrison! Garrison:
1 → 1 (-0) … Garrison holds — 1 defenders remain." — 40 assaults, attacker
40,000 → 17,843; a Bavarian marshal spent 21 consecutive assaults and
10,152 men on a garrison that could never fall.

The fix is one term: a landed assault always kills at least one defender
(`max(…, 1)`), which cannot bind at garrison ≥ 10 — major-capital
arithmetic is byte-identical by construction.

Consciously NOT built (spec slice 3, recorded so nobody "completes" it):
the P4.25 futility guard and the garrison-shaped futility-tracker arm.
With the floor fixed every assault progresses, so unbounded futility
cannot recur.
"""

from backend.commands.executor import CommandExecutor
from backend.models.world_state import WorldState


def _cmd(marshal, action, target):
    return {"command": {"marshal": marshal, "action": action,
                        "target": target}}


class TestGarrisonFloor:
    def setup_method(self):
        self.world = WorldState()
        self.executor = CommandExecutor()
        self.game_state = {"world": self.world}
        for m in self.world.marshals.values():
            if m.nation == "France":
                m.location = "Bordeaux"

    def _assault_until_fall(self, region_name, max_assaults):
        """Drive real assaults through the executor; return the count it
        took for the garrison to fall (or None if it never did)."""
        region = self.world.get_region(region_name)
        wellington = self.world.marshals["Wellington"]
        for assault in range(1, max_assaults + 1):
            wellington.strength = max(wellington.strength, 20000)
            wellington.location = "Belgium"
            wellington.morale = 100
            self.executor.execute(
                _cmd("Wellington", "attack", region_name), self.game_state)
            if region.garrison_strength <= 0:
                return assault
        return None

    def test_detachment_garrison_falls_by_assault_13(self):
        """The measured collapse shape: 3,000 → … → 1 → 0 in ~13 assaults
        under the 0.50 damage-ratio cap. Before the floor it NEVER fell."""
        paris = self.world.get_region("Paris")
        paris.garrison_strength = 3000
        paris.garrison_detachment = True
        fell_at = self._assault_until_fall("Paris", max_assaults=20)
        assert fell_at is not None, (
            "the detachment garrison must actually fall — before WO-3 it "
            "stalled at 1 man forever")
        assert fell_at <= 15, f"collapse took {fell_at} assaults (spec ~13)"

    def test_one_man_garrison_falls_this_assault(self):
        """The terminal stall state: garrison 1, int(1×0.10) == 0 — the
        exact frozen configuration every detachment used to reach."""
        paris = self.world.get_region("Paris")
        paris.garrison_strength = 1
        paris.garrison_detachment = True
        fell_at = self._assault_until_fall("Paris", max_assaults=2)
        assert fell_at == 1

    def test_capital_arithmetic_above_ten_unchanged(self):
        """The +1 term cannot bind at garrison ≥ 10: a 15,000 capital
        garrison still takes at least its 10% floor (1,500), and the fall
        threshold semantics (capital collapses below 5,000) are untouched."""
        paris = self.world.get_region("Paris")
        assert paris.garrison_strength == 15000
        assert paris.garrison_detachment is False
        wellington = self.world.marshals["Wellington"]
        wellington.location = "Belgium"
        wellington.strength = 30000
        self.executor.execute(
            _cmd("Wellington", "attack", "Paris"), self.game_state)
        losses = 15000 - paris.garrison_strength
        assert losses >= 1500, (
            f"the 10% floor must still govern large garrisons (took {losses})")

    def test_floor_term_is_arithmetically_inert_at_ten_plus(self):
        """Documentation-grade pin: max(int(g*0.10), 1) == int(g*0.10) for
        every g ≥ 10 — the byte-identity claim, stated falsifiably."""
        for g in (10, 11, 100, 3000, 15000, 25000):
            assert max(int(g * 0.10), 1) == int(g * 0.10)
        for g in (1, 5, 9):
            assert max(int(g * 0.10), 1) == 1
