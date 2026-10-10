"""The Chunk 4 reserve (Score Mandate, Sept 26 2026) — the rows the SR-4a
recon and the session exit filed: AAR4-X1 the captor inherits the garrison,
AAR24-X1 a gun corps storms the works, AAR24-X2 the counter-punch on an
assault, AAR24-X3 the unpriced assault objection, AAR10-X1 Rule 12. Rules
`SYSTEMS_REFERENCE.md` §73.6. Every row reproduced on the shipped 1805 boot
first; every fix behind its own lever, each class carrying the lever-down arm.
"""

import contextlib
import io

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.commands.parser import CommandParser


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


@pytest.fixture
def shipped(monkeypatch):
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    with _quiet():
        M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    return TestClient(M.app), M.world


def post(client, command):
    with _quiet():
        return client.post("/command", json={"command": command}).json()


def _clear_field(world, region_name, keep=()):
    """No corps of any court stands in `region_name` but those in `keep`."""
    for m in world.marshals.values():
        if m.location == region_name and m.name not in keep:
            m.location = "Normandy" if m.nation == "France" else "Moravia"


# ═══════════════════════════ AAR4-X1 ═══════════════════════════════════════

class TestTheCaptorRaisesHisOwnGarrison:

    def test_a_capture_clears_the_losers_garrison(self, shipped):
        _client, world = shipped
        vienna = world.get_region("Vienna")
        vienna.garrison_strength = 25000
        vienna.garrison_detachment = True     # a detachment does not change sides either
        with _quiet():
            world.capture_region("Vienna", "France")
        assert vienna.controller == "France"
        assert vienna.garrison_strength == 0
        assert vienna.garrison_detachment is False

    def test_the_march_into_a_collapsing_capital_inherits_nothing(self, shipped):
        """The recon's measured case: a Vienna held by 4,000 (below the
        collapse line) marched into — France held 4,000 that regrew."""
        client, world = shipped
        vienna = world.get_region("Vienna")
        _clear_field(world, "Vienna")
        vienna.garrison_strength = 4000
        vienna.garrison_detachment = False
        ney = world.get_marshal("Ney")
        ney.location = "Bohemia"
        ney.strategic_order = None
        with _quiet():
            world.calculate_visibility()
        r = post(client, "Ney, move to Vienna")
        assert r.get("success"), r.get("message")
        assert vienna.controller == "France", r.get("message")
        assert vienna.garrison_strength == 0

    def test_the_scout_reads_the_captors_garrison(self, shipped):
        _client, world = shipped
        from backend.game_logic.garrison_report import garrison_view
        vienna = world.get_region("Vienna")
        vienna.garrison_strength = 25000
        with _quiet():
            world.capture_region("Vienna", "France")
        assert garrison_view(world, "Vienna", "France") == (None, 0)

    def test_lever_down_the_captor_inherits(self, shipped, monkeypatch):
        import backend.models.world_state as WS
        monkeypatch.setattr(WS, "CAPTURE_CLEARS_THE_GARRISON", False)
        _client, world = shipped
        vienna = world.get_region("Vienna")
        vienna.garrison_strength = 25000
        with _quiet():
            world.capture_region("Vienna", "France")
        assert vienna.garrison_strength == 25000

    def test_a_return_to_the_same_hands_is_no_capture(self, shipped):
        _client, world = shipped
        paris = world.get_region("Paris")
        before = paris.garrison_strength
        with _quiet():
            world.capture_region("Paris", "France")
        assert paris.garrison_strength == before


# ═══════════════════════════ AAR24-X1 ══════════════════════════════════════

def _stage_guns(world, guns="Soult", at="Bohemia"):
    _clear_field(world, "Vienna")
    vienna = world.get_region("Vienna")
    vienna.garrison_strength = 25000
    vienna.garrison_detachment = False
    g = world.get_marshal(guns)
    g.artillery = True
    g.location = at
    g.strategic_order = None
    g.fortified = False
    with _quiet():
        world.calculate_visibility()
    return g, vienna


class TestAGunCorpsDoesNotStormTheWorks:

    @pytest.mark.parametrize("verb", ["attack", "bombard"])
    def test_the_order_is_refused_free_with_the_remedy(self, shipped, verb):
        client, world = shipped
        _stage_guns(world)
        ap = world.actions_remaining
        r = post(client, f"Soult, {verb} Vienna")
        assert r.get("success") is False, r.get("message")
        msg = r.get("message", "")
        assert "cannot storm the works at Vienna" in msg, msg
        assert "Infantry or cavalry must carry Vienna" in msg, msg
        assert world.actions_remaining == ap
        assert not r.get("pending_objection")
        assert world.get_region("Vienna").garrison_strength == 25000

    def test_a_corps_in_the_field_is_still_a_battle(self, shipped):
        _client, world = shipped
        from backend.game_logic.garrison_report import gun_corps_assault_refusal
        g, vienna = _stage_guns(world)
        mack = world.get_marshal("Mack")
        mack.location = "Vienna"
        assert gun_corps_assault_refusal(world, g, "Vienna") == ""

    def test_a_foot_corps_still_storms(self, shipped):
        _client, world = shipped
        from backend.game_logic.garrison_report import gun_corps_assault_refusal
        g, _vienna = _stage_guns(world)
        g.artillery = False
        assert gun_corps_assault_refusal(world, g, "Vienna") == ""

# ═══════════════════════════ AAR10-X1 ══════════════════════════════════════

class TestRuleTwelveIsTheGunsRule:

    def _reason(self, world, candidate, primary, region):
        from backend.commands.executor import CommandExecutor
        combat = CommandExecutor()._combat
        return combat._muster_reason(candidate, primary, region,
                                     candidate.nation, world)

    def _stage(self, world):
        """Ney strikes Vienna from Bohemia; Soult stands next door in
        Moravia — adjacent to the field, not on it (a corps ON the field
        shares it whatever it did this turn)."""
        _clear_field(world, "Vienna")
        mack = world.get_marshal("Mack")
        mack.location = "Vienna"
        ney = world.get_marshal("Ney")
        ney.location = "Bohemia"
        soult = world.get_marshal("Soult")
        soult.location = "Moravia"
        for flag in ("fortified", "drilling", "drilling_locked", "broken",
                     "holding_position", "square_formation",
                     "retreated_this_turn", "reinforced_this_turn"):
            setattr(soult, flag, False)
        soult.retreat_recovery = 0
        return soult, ney

    def test_guns_that_limbered_say_so(self, shipped):
        _client, world = shipped
        from backend.display_names import MUSTER_REASON_DISPLAY
        soult, ney = self._stage(world)
        soult.artillery = True
        soult.moved_this_turn = True
        join, code = self._reason(world, soult, ney, "Vienna")
        assert join is False and code == "guns_limbered"
        assert "cannot unlimber" in MUSTER_REASON_DISPLAY[code]

    def test_a_corps_that_answered_the_guns_keeps_the_cooldown(self, shipped):
        _client, world = shipped
        soult, ney = self._stage(world)
        soult.reinforced_this_turn = True
        join, code = self._reason(world, soult, ney, "Vienna")
        assert join is False and code == "cooldown_spent"

    def test_lever_down_the_guns_share_the_cooldown_row(self, shipped, monkeypatch):
        import backend.commands.combat_executor as CE
        monkeypatch.setattr(CE, "GUNS_LIMBERED_SAY_SO", False)
        _client, world = shipped
        soult, ney = self._stage(world)
        soult.artillery = True
        soult.moved_this_turn = True
        _join, code = self._reason(world, soult, ney, "Vienna")
        assert code == "cooldown_spent"


# ═══════════════════════════ AAR24-X2 ══════════════════════════════════════

def _stage_assault(world, who="Davout", strength=60000, garrison=25000):
    """`who` in Bohemia beside a Vienna held by a garrison alone."""
    _clear_field(world, "Vienna")
    vienna = world.get_region("Vienna")
    vienna.garrison_strength = garrison
    vienna.garrison_detachment = False
    m = world.get_marshal(who)
    m.location = "Bohemia"
    m.strategic_order = None
    m.fortified = False
    m.strength = strength
    with _quiet():
        world.calculate_visibility()
    return m, vienna


def _steady(monkeypatch):
    """The objection's mood roll is the one random term in it — pinned."""
    import backend.commands.executor as EX
    monkeypatch.setattr(EX, "apply_mood_variance", lambda concern: concern)


class TestTheCounterPunchRidesTheAssault:
    """Measured on the shipped boot: Davout on his banked counter-punch,
    ordered into Vienna's works past his objection ("insist"), spent the
    blow, paid 1 action and was told nothing. The typed road was already
    free (the executor's Aug-30 belt) but silent too."""

    def _bank(self, davout):
        davout.counter_punch_available = True
        davout.counter_punch_turns = 2

    def test_the_typed_road_says_the_blow(self, shipped, monkeypatch):
        _steady(monkeypatch)
        client, world = shipped
        davout, vienna = _stage_assault(world)
        self._bank(davout)
        ap = world.actions_remaining
        r = post(client, "Davout, attack Vienna")
        assert r.get("success"), r.get("message")
        assert not r.get("pending_objection"), r.get("message")
        assert "COUNTER-PUNCH" in r.get("message", "")
        assert world.actions_remaining == ap
        assert davout.counter_punch_available is False
        assert vienna.garrison_strength < 25000

    def _insist(self, client, world, monkeypatch):
        _steady(monkeypatch)
        davout, vienna = _stage_assault(world, strength=9000)
        world.update_intel_from_scout("Vienna", world.current_turn)
        self._bank(davout)
        ap = world.actions_remaining
        staged = post(client, "Davout, attack Vienna")
        assert staged.get("pending_objection"), staged.get("message")
        with _quiet():
            r = client.post("/respond_to_objection",
                            json={"choice": "insist"}).json()
        assert r.get("success"), r.get("message")
        assert davout.counter_punch_available is False
        return r, ap

    def test_the_insist_road_is_free_and_said(self, shipped, monkeypatch):
        client, world = shipped
        r, ap = self._insist(client, world, monkeypatch)
        assert "COUNTER-PUNCH" in r.get("message", ""), r.get("message")
        assert world.actions_remaining == ap

    def test_lever_down_the_insist_road_charges_in_silence(self, shipped, monkeypatch):
        import backend.commands.combat_executor as CE
        monkeypatch.setattr(CE, "COUNTER_PUNCH_CREDITS_THE_ASSAULT", False)
        client, world = shipped
        r, ap = self._insist(client, world, monkeypatch)
        assert "COUNTER-PUNCH" not in r.get("message", "")
        assert world.actions_remaining == ap - 1

    def _ai_assault(self, world):
        paris = world.get_region("Paris")
        _clear_field(world, "Paris")
        paris.garrison_strength = 25000
        paris.garrison_detachment = False
        charles = world.get_marshal("ArchdukeCharles")
        charles.location = sorted(paris.adjacent_regions)[0]
        charles.strength = 70000
        charles.fortified = False
        charles.strategic_order = None
        self._bank(charles)
        with _quiet():
            result = M.executor.execute(
                {"command": {"marshal": "ArchdukeCharles", "action": "attack",
                             "target": "Paris", "type": "specific"}},
                {"world": world})
        assert result.get("success"), result.get("message")
        assert paris.garrison_strength < 25000
        assert charles.counter_punch_available is False
        return result

    def test_the_ai_takes_its_blow_free_too(self, shipped):
        """GR5: the AI's own road (the enemy loop prices the action off
        `free_action`) — an Austrian on a French garrison."""
        _client, world = shipped
        result = self._ai_assault(world)
        assert result.get("free_action") is True
        assert result.get("counter_punch_used") is True

    def test_lever_down_the_ai_pays(self, shipped, monkeypatch):
        import backend.commands.combat_executor as CE
        monkeypatch.setattr(CE, "COUNTER_PUNCH_CREDITS_THE_ASSAULT", False)
        _client, world = shipped
        result = self._ai_assault(world)
        assert not result.get("free_action")


# ═══════════════════════════ AAR24-X3 ══════════════════════════════════════

class TestTheObjectionPricesTheWorks:

    def test_good_odds_raise_no_objection(self, shipped, monkeypatch):
        """The measured case: 60,000 against Vienna's 25,000 objected "the
        enemy is too strong" with no figure; the assault's own reckoning
        prices it at 0.41 — no objection, and the assault goes in."""
        _steady(monkeypatch)
        client, world = shipped
        _stage_assault(world)
        r = post(client, "Davout, attack Vienna")
        assert not r.get("pending_objection"), r.get("message")
        assert "ASSAULT" in r.get("message", ""), r.get("message")

    def test_bad_odds_name_the_price_at_full(self, shipped, monkeypatch):
        _steady(monkeypatch)
        client, world = shipped
        davout, vienna = _stage_assault(world, strength=9000)
        world.update_intel_from_scout("Vienna", world.current_turn)
        from backend.commands.objection_v2 import garrison_assault_price
        price = garrison_assault_price(davout, vienna, world)
        assert price["exact"] and price["ratio"] >= 2.0, price
        r = post(client, "Davout, attack Vienna")
        assert r.get("pending_objection"), r.get("message")
        msg = r.get("message", "")
        assert "the works at Vienna hold 25,000" in msg, msg
        assert f"{price['attacker_effective']:,} in the assault's reckoning" in msg, msg
        assert f"I would lose about {price['attacker_losses']:,} men" in msg, msg
        assert "the enemy is too strong" not in msg

    def test_partial_intel_prices_the_band_and_gives_no_count(self, shipped, monkeypatch):
        _steady(monkeypatch)
        client, world = shipped
        davout, vienna = _stage_assault(world, strength=9000)
        from backend.commands.objection_v2 import (
            _FULL, _get_region_visibility, garrison_assault_price)
        assert _get_region_visibility("Vienna", "France", world) != _FULL
        price = garrison_assault_price(davout, vienna, world)
        assert not price["exact"] and price["ratio"] is not None, price
        r = post(client, "Davout, attack Vienna")
        assert r.get("pending_objection"), r.get("message")
        msg = r.get("message", "")
        assert "the works at Vienna hold a substantial force" in msg, msg
        assert "our intelligence gives no count" in msg, msg
        assert "25,000" not in msg, msg

    def test_a_province_with_an_army_prices_the_army(self, shipped, monkeypatch):
        """One lookup over: "attack Swabia" with Mack standing there objected
        at odds that "attack Mack" did not — both now read the man the
        executor engages."""
        _steady(monkeypatch)
        client, world = shipped
        from backend.commands.objection_v2 import attack_engages
        davout = world.get_marshal("Davout")
        mack = world.get_marshal("Mack")
        kind, engaged = attack_engages(davout, {"target": mack.location}, world)
        assert kind == "marshal" and engaged.name == "Mack"
        adjacent = sorted(world.get_region(mack.location).adjacent_regions)
        davout.location = [a for a in adjacent
                           if world.get_region(a).controller != mack.nation][0]
        davout.strength = 60000
        davout.strategic_order = None
        for m in world.marshals.values():
            if m.location == mack.location and m.name != "Mack":
                m.location = "Moravia"
        with _quiet():
            world.calculate_visibility()
        by_province = post(client, f"Davout, attack {mack.location}")
        assert not by_province.get("pending_objection"), by_province.get("message")

    def test_lever_down_the_marshal_only_read(self, shipped, monkeypatch):
        import backend.commands.objection_v2 as O
        monkeypatch.setattr(O, "THE_OBJECTION_PRICES_WHAT_THE_ATTACK_ENGAGES", False)
        _steady(monkeypatch)
        client, world = shipped
        _stage_assault(world)
        r = post(client, "Davout, attack Vienna")
        assert r.get("pending_objection"), r.get("message")
        assert "the enemy is too strong" in r.get("message", "")
