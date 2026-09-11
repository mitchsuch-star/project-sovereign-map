"""FA slice 17, Phase 2 — FA-D29 "The Stub and the Field" (September 11, 2026).

The row filed a 500-man stub in a garrisoned province as a P4 sink: the AI
priced the visible field (500) and never the reinforcement that arrives.
Reproduced on the shipped board (Moore 100,000 at Artois; Ney 500 at Paris;
Davout 48,000 at Berry): P4 priced 200:1 — and the row's own fix (price the
muster) leaves the decision unchanged at 2.9:1 against a 1.2 floor. What the
reproduction found underneath: the RESOLVER sized the reinforced defender's
casualties by the primary's 500 men while pricing the attacker's against the
48,000-man committed field, a 10:1 exchange from accounting — the attacker
"lost", broke at morale 15, and on 3 of 5 rolls was CAPTURED WHOLE, 48,000
of his men "escaping home". Two levers:

  (a) P4_PRICES_THE_MUSTER        — the four field-price rungs add the visible
                                     muster forecast (the preview's own term)
  (b) CASUALTIES_FALL_ON_THE_FIELD — the loss pool is the bodies on the field
"""
from __future__ import annotations

import random
from pathlib import Path

import pytest

from backend.models.world_state import WorldState
from backend.commands.executor import CommandExecutor
from backend.ai.enemy_ai import EnemyAI

ROOT = next(p for p in (Path(__file__).resolve().parents[1], Path.cwd()) if (p / "backend").is_dir())
SCENARIO = ROOT / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"


def _boot():
    return WorldState.from_scenario(str(SCENARIO))


def _stage(w, stub=500, friend=48000, attacker=100000):
    """The row's geometry: Moore adjacent to Paris, Ney's stub at Paris, Davout adjacent."""
    paris = w.get_region("Paris")
    adj = list(paris.adjacent_regions)
    for m in w.marshals.values():
        if m.name in ("Ney", "Davout", "Moore"):
            continue
        m.location = "Moscow" if m.nation != "France" else "Gascony"
    ney, dav, moore = w.marshals["Ney"], w.marshals["Davout"], w.marshals["Moore"]
    ney.location, ney.strength, ney.morale = "Paris", stub, 70
    dav.location, dav.strength, dav.morale = adj[0], friend, 70
    dav.strategic_order = None
    dav.fortified = False
    moore.location = adj[1] if adj[1] != dav.location else adj[2]
    moore.strength, moore.morale, moore.fortified = attacker, 80, False
    for m in (ney, dav, moore):
        m.retreat_recovery = 0
        m.broken = False
        m.retreated_this_turn = False
        m.moved_this_turn = False
        m.reinforced_this_turn = False
        m.drilling = False
        m.holding_position = False
    w.calculate_visibility()
    return ney, dav, moore


def _attack(ex, w):
    cmd = {"command": {"type": "specific", "marshal": "Moore", "action": "attack",
                       "target": "Ney", "_autonomous_execution": True}}
    return ex.execute(cmd, {"world": w, "debug_mode": True})


# ═══════════════════════════════════════════════════════════════════════
# (a) the price reads the muster
# ═══════════════════════════════════════════════════════════════════════
class TestThePriceReadsTheMuster:
    def test_the_muster_term_is_the_previews_own_summer(self):
        w = _boot()
        ney, dav, moore = _stage(w)
        ex = CommandExecutor()
        ai = EnemyAI(ex)
        joining, committed = ex._combat._defender_muster(ney, w)
        assert [m.name for m in joining] == ["Davout"]
        price = ai._muster_price(ney, "Britain", w)
        assert price == int(committed) > 20_000

    def test_the_row_geometry_is_priced_honestly_and_still_attacked(self, monkeypatch):
        from backend.ai import enemy_ai as EA
        w = _boot()
        ney, dav, moore = _stage(w)
        ai = EnemyAI(CommandExecutor())
        assert ai._find_attack_opportunity(moore, "Britain", w) == {
            "marshal": "Moore", "action": "attack", "target": "Ney"}
        field = ai._defending_strength_in_region(
            w.get_live_visible_enemies_in_region("Paris", "Britain")) or ney.strength
        assert field == 500  # what the old price read: 200:1
        priced = field + ai._muster_price(ney, "Britain", w)
        assert 2.0 < moore.strength / priced < 4.0  # the honest figure (2.9:1 measured)

    def test_a_smaller_attacker_declines_what_it_would_have_charged(self, monkeypatch):
        """30,000 vs a 500 stub with 48,000 next door: 60:1 by the old price, ~0.9:1 by the honest one."""
        from backend.ai import enemy_ai as EA
        w = _boot()
        ney, dav, moore = _stage(w, attacker=30000)
        ai = EnemyAI(CommandExecutor())
        monkeypatch.setattr(ai, "_get_mood_adjusted_threshold", lambda m, world: 1.2)
        assert ai._find_attack_opportunity(moore, "Britain", w) is None
        monkeypatch.setattr(EA, "P4_PRICES_THE_MUSTER", False)
        assert ai._find_attack_opportunity(moore, "Britain", w) == {
            "marshal": "Moore", "action": "attack", "target": "Ney"}

    def test_the_price_is_ground_truth_like_the_players_own_gate(self):
        """The player's odds band reads the enemy muster as ground truth (CA9-F1:
        a safety gate, not intel surfaced); GR5 gives the AI the same gate — a
        friend the acting court cannot SEE is still priced."""
        w = _boot()
        ney, dav, moore = _stage(w)
        ai = EnemyAI(CommandExecutor())
        paris_adj = list(w.get_region("Paris").adjacent_regions)
        hidden = None
        for cand in paris_adj:
            if cand == moore.location:
                continue
            dav.location = cand
            w.calculate_visibility()
            seen = w.get_live_visible_enemies_in_region(cand, "Britain")
            if not any(v.name == "Davout" for v in seen):
                hidden = cand
                break
        if hidden is None:
            pytest.skip("every Paris neighbour is in Britain's sight from Moore's province")
        assert ai._muster_price(ney, "Britain", w) > 20_000
        # the executor's own preview summer, not a copy of it
        joining, committed = ai.executor._combat._defender_muster(ney, w)
        assert ai._muster_price(ney, "Britain", w) == int(committed)

    def test_lever_down_prices_the_field_alone(self, monkeypatch):
        from backend.ai import enemy_ai as EA
        monkeypatch.setattr(EA, "P4_PRICES_THE_MUSTER", False)
        w = _boot()
        ney, dav, moore = _stage(w)
        ai = EnemyAI(CommandExecutor())
        assert ai._muster_price(ney, "Britain", w) == 0

    def test_all_four_rungs_read_the_one_helper(self):
        src = (ROOT / "backend" / "ai" / "enemy_ai.py").read_text(encoding="utf-8")
        assert src.count("self._muster_price(") == 4
        for anchor in ("defenders += self._muster_price(weakest_enemy, nation, world)",   # P0
                       "_defenders += self._muster_price(enemy, nation, world)",          # P4
                       "field += self._muster_price(enemy, nation, world)",               # P3.25
                       "field += self._muster_price(weakest, nation, world)"):            # P7.5
            assert anchor in src, anchor


# ═══════════════════════════════════════════════════════════════════════
# (b) casualties fall on the field
# ═══════════════════════════════════════════════════════════════════════
class TestCasualtiesFallOnTheField:
    def test_the_reinforced_defender_bleeds_by_its_bodies(self):
        w = _boot()
        ney, dav, moore = _stage(w)
        ex = CommandExecutor()
        random.seed(11)
        res = _attack(ex, w)
        ev = next(e for e in res["events"] if e.get("type") == "battle")
        arrived = [r for r in res["reinforcement_results"]["defender"] if r.get("arrived")]
        if not arrived:
            pytest.skip("Davout's arrival roll failed on this seed — the pool is the stub alone by design")
        assert ev["defender"]["casualties"] > 5_000          # was ~250 on the primary-only pool
        assert ev["outcome"].startswith("attacker")           # a 100,000-man army beats a 48,500 field
        assert 1_000 < ev["attacker"]["casualties"] < 10_000  # the attacker's losses were already honest

    def test_lever_down_reproduces_the_stub_pool(self, monkeypatch):
        from backend.game_logic import combat as CB
        monkeypatch.setattr(CB, "CASUALTIES_FALL_ON_THE_FIELD", False)
        w = _boot()
        ney, dav, moore = _stage(w)
        ex = CommandExecutor()
        random.seed(11)
        res = _attack(ex, w)
        ev = next(e for e in res["events"] if e.get("type") == "battle")
        arrived = [r for r in res["reinforcement_results"]["defender"] if r.get("arrived")]
        if not arrived:
            pytest.skip("Davout's arrival roll failed on this seed")
        assert ev["defender"]["casualties"] <= 500            # 60% of the 500-man primary at most
        assert ev["outcome"].startswith("defender")           # the accounting rout

    def test_the_executor_passes_the_bodies_it_distributes_over(self, monkeypatch):
        w = _boot()
        ney, dav, moore = _stage(w)
        ex = CommandExecutor()
        seen = {}
        real = ex._combat.combat_resolver.resolve_battle

        def spy(*args, **kwargs):
            seen.update({k: v for k, v in kwargs.items() if k.endswith("_bodies")})
            return real(*args, **kwargs)
        monkeypatch.setattr(ex._combat.combat_resolver, "resolve_battle", spy)
        random.seed(11)
        res = _attack(ex, w)
        arrived = [r for r in res["reinforcement_results"]["defender"] if r.get("arrived")]
        if not arrived:
            pytest.skip("Davout's arrival roll failed on this seed")
        assert seen["attacker_bodies"] == 100_000
        # the ENGAGED bodies: the lead's corps + the reinforcer's committed share
        # (α × strength × the pair scale) — the quantity half of the committed term
        scale = ex._combat._pair_contribution_scale(ney, dav)
        assert scale > 0
        assert seen["defender_bodies"] == int(500 + ex._combat.COMMITTED_ALPHA * 48_000 * scale)
        assert 500 < seen["defender_bodies"] < 48_500

    def test_a_solo_battle_is_byte_identical_in_both_arms(self, monkeypatch):
        from backend.game_logic import combat as CB
        w = _boot()
        ney, dav, moore = _stage(w, friend=0)   # no friend: solo
        dav.location = "Gascony"
        outs = []
        for arm in (True, False):
            monkeypatch.setattr(CB, "CASUALTIES_FALL_ON_THE_FIELD", arm)
            w2 = _boot()
            n2, d2, m2 = _stage(w2, friend=0)
            d2.location = "Gascony"
            w2.calculate_visibility()
            random.seed(23)
            res = _attack(CommandExecutor(), w2)
            ev = next(e for e in res["events"] if e.get("type") == "battle")
            outs.append((ev["attacker"]["casualties"], ev["defender"]["casualties"], ev["outcome"]))
        assert outs[0] == outs[1]

    def test_the_resolver_pool_and_rate_read_the_bodies(self):
        from backend.game_logic.combat import CombatResolver
        w = _boot()
        ney, dav, moore = _stage(w)
        cr = CombatResolver()
        random.seed(5)
        a = cr.resolve_battle(moore, ney, terrain="plains", apply_casualties=False,
                              committed_defender=30_000.0, defender_bodies=48_500)
        random.seed(5)
        b = cr.resolve_battle(moore, ney, terrain="plains", apply_casualties=False,
                              committed_defender=30_000.0)
        assert a["defender_raw_casualties"] > 10 * b["defender_raw_casualties"]
        assert a["attacker_raw_casualties"] == b["attacker_raw_casualties"]

    def test_the_morale_rate_is_losses_over_the_bodies_that_bore_them(self, monkeypatch):
        """A 50,000-man field that loses a quarter must not be scored as a
        5,000-man primary that lost 250%: the deferred morale delta reads losses
        over the BODIES. Decisiveness is zeroed so the pin isolates the rate
        (the sweep found the pool pin alone could not tell — at a 40% loss both
        rates cap the severity)."""
        from backend.game_logic import combat as CB
        monkeypatch.setattr(CB, "decisiveness_morale_penalty", lambda a, b: 0)
        w = _boot()
        ney, dav, moore = _stage(w, stub=5_000, friend=45_000, attacker=40_000)
        cr = CB.CombatResolver()
        random.seed(9)
        res = cr.resolve_battle(moore, ney, terrain="plains", apply_casualties=False,
                                committed_defender=20_000.0, defender_bodies=50_000)
        assert res["outcome"] == "attacker_tactical_victory", res["outcome"]
        rate = res["defender_raw_casualties"] / 50_000
        severity = min(rate / 0.15, 2.5)
        assert severity < 2.5, rate                   # the bodies' rate is under the cap …
        assert res["defender_raw_casualties"] / 5_000 > 0.375   # … the primary's alone would cap it
        expected = -int(round(max(10, int(10 * severity)) * CB.DEFENDER_MORALE_CURVE_FACTOR))
        assert res["defender_morale_delta"] == expected, (res["defender_morale_delta"], expected)

    def test_a_reinforced_field_that_keeps_its_men_is_a_tactical_result(self):
        """The deferred projection is the FIELD's: 48,500 bodies losing 19,600
        is a tactical defeat, never the primary's annihilation."""
        from backend.game_logic.combat import CombatResolver
        w = _boot()
        ney, dav, moore = _stage(w)
        cr = CombatResolver()
        random.seed(5)
        res = cr.resolve_battle(moore, ney, terrain="plains", apply_casualties=False,
                                committed_defender=30_000.0, defender_bodies=48_500)
        assert res["defender_raw_casualties"] < 48_500
        assert res["outcome"] == "attacker_tactical_victory", res["outcome"]


# ═══════════════════════════════════════════════════════════════════════
# the census
# ═══════════════════════════════════════════════════════════════════════
class TestCensus:
    def test_both_levers_exist_with_false_arms(self):
        from backend.ai import enemy_ai as EA
        from backend.game_logic import combat as CB
        assert EA.P4_PRICES_THE_MUSTER is True
        assert CB.CASUALTIES_FALL_ON_THE_FIELD is True

    def test_no_pool_reads_the_primary_strength_bare(self):
        src = (ROOT / "backend" / "game_logic" / "combat.py").read_text(encoding="utf-8")
        start = src.index("    def resolve_battle(")
        end = src.index("\n    def ", start + 10)
        body = src[start:end]
        assert "self._calculate_casualties(\n            attacker.strength," not in body
        assert "self._calculate_casualties(\n            defender.strength," not in body
        assert body.count("self._calculate_casualties(\n            atk_bodies,") == 1
        assert body.count("self._calculate_casualties(\n            def_bodies,") == 1
