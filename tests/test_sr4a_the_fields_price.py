"""SR-4a part (i) "The field's price" — the garrison family (Score Mandate
Chunk 4; AAR-4 + AAR-24). Rules `SYSTEMS_REFERENCE.md` §73.1.

Reproduced at `POST /command` on the shipped 1805 boot before a line changed:

    Ney at Franconia:   `Ney, scout Vienna` -> "Controlled by Austria.
                        Terrain: Plains. No enemy forces detected." over a
                        25,000-man capital garrison (AAR-4)
    Ney at Bohemia:     `Ney, scout` -> "Franconia (Bavaria, Plains,
                        1 enemies)" — our ally Deroy counted as an enemy
    Ney + Murat + Soult at Bohemia, Bernadotte at Moravia, Vienna held by
    its garrison alone: `Ney, attack Vienna` -> "Ney assaults the Vienna
                        garrison! Garrison: 25,000 -> 14,085 (-10,915)…" —
                        no word that he went in alone, that the corps beside
                        him would not join, or that the works regrow 2,000 a
                        turn (AAR-24)
    the desk:           "is Vienna safe?" printed the exact garrison at
                        PARTIAL; "who is at Vienna?" said "No army stands in
                        Vienna that we know of" over the garrison at FULL
"""

import contextlib
import io
import re

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.commands.combat_executor import CombatExecutor
from backend.commands.parser import CommandParser
from backend.game_logic import garrison_report as GR
from backend.models import world_state as WS


@pytest.fixture
def shipped(monkeypatch):
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    assert M.parser.llm.use_real_api is False
    return TestClient(M.app), M.world


def post(client, command):
    with contextlib.redirect_stdout(io.StringIO()):
        return client.post("/command", json={"command": command}).json()


def _empty_vienna(world):
    """Vienna held by its garrison alone (no Austrian field army inside)."""
    for m in world.marshals.values():
        if m.location == "Vienna" and m.nation != "France":
            m.location = "Hungary"


# ═══════════════════════════════════════════════════════════════════════════
# AAR-4 — the scout names the garrison and the works
# ═══════════════════════════════════════════════════════════════════════════

class TestTheScoutNamesTheGarrison:

    def _scout_vienna(self, client, world):
        _empty_vienna(world)
        world.get_marshal("Ney").location = "Bohemia"
        return post(client, "Ney, scout Vienna")

    def test_the_capital_garrison_is_named(self, shipped):
        client, world = shipped
        data = self._scout_vienna(client, world)
        msg = data["message"]
        assert "No enemy forces detected" not in msg, msg
        assert "No field army stands there." in msg
        assert ("Garrison: 25,000 — it must be assaulted — a march halts before it; "
                "a capital's garrison, it regrows 2,000 a turn up to 25,000.") in msg, msg
        intel = data["events"][0]["intel"]
        assert intel["garrison"] == 25000 and intel["works_bonus"] == 0

    def test_the_works_are_named(self, shipped):
        client, world = shipped
        world.get_region("Vienna").buildings.append({"type": "fortification", "damaged": False})
        data = self._scout_vienna(client, world)
        assert "its works add +25% to the defense" in data["message"], data["message"]
        assert data["events"][0]["intel"]["works_bonus"] == 25

    def test_a_damaged_work_is_not_counted(self, shipped):
        client, world = shipped
        world.get_region("Vienna").buildings.append({"type": "fortification", "damaged": True})
        data = self._scout_vienna(client, world)
        assert "works add" not in data["message"]

    def test_a_weak_garrison_gives_way(self, shipped):
        client, world = shipped
        world.get_region("Vienna").garrison_strength = 4000
        data = self._scout_vienna(client, world)
        assert "Garrison: 4,000 — too few to hold (below 5,000)" in data["message"], data["message"]

    def test_a_detachment_fights_to_the_last(self, shipped):
        client, world = shipped
        vienna = world.get_region("Vienna")
        vienna.garrison_strength = 3000
        vienna.garrison_detachment = True
        data = self._scout_vienna(client, world)
        assert "a detachment that fights to the last man — it must be assaulted" in data["message"]
        assert data["events"][0]["intel"]["garrison_detachment"] is True

    def test_a_field_army_and_the_garrison_both(self, shipped):
        client, world = shipped
        world.get_marshal("Ney").location = "Bohemia"
        mack = world.get_marshal("Mack")
        mack.location = "Vienna"
        data = post(client, "Ney, scout Vienna")
        assert re.search(r"Enemy forces: Mack \(Austria\): ~[\d,]+ troops\. Garrison: 25,000",
                         data["message"]), data["message"]

    def test_an_allied_garrison_is_not_to_be_stormed(self, shipped):
        client, world = shipped
        munich = world.get_region("Munich")
        assert not world.is_at_war("France", munich.controller)
        scout = world.get_marshal("Massena")
        scout.location = munich.adjacent_regions[0]
        data = post(client, "Massena, scout Munich")
        assert f"Garrison: {munich.garrison_strength:,} (Bavaria's)." in data["message"], data["message"]
        assert "must be assaulted" not in data["message"]

    def test_our_own_garrison(self, shipped):
        client, world = shipped
        world.get_marshal("Soult").location = "Picardy"
        data = post(client, "Soult, scout Paris")
        assert "Our garrison: 25,000." in data["message"], data["message"]

class TestTheScanCountsOnlyEnemiesAndBandsTheGarrison:

    def test_an_ally_is_not_an_enemy_and_the_garrison_is_banded(self, shipped):
        client, world = shipped
        world.get_marshal("Ney").location = "Bohemia"
        data = post(client, "Ney, scout")
        msg = data["message"]
        assert msg.startswith("Ney scouts from Bohemia:")
        assert "Franconia (Bavaria, Plains)" in msg, msg          # Deroy is our ally
        assert "Vienna (Austria, Plains, garrison: " in msg, msg   # a band, not 25,000
        assert "Vienna (Austria, Plains, garrison 25,000" not in msg

# ═══════════════════════════════════════════════════════════════════════════
# AAR-24 — an assault gets its one-line muster
# ═══════════════════════════════════════════════════════════════════════════

def _stage_assault(world):
    _empty_vienna(world)
    for name in ("Ney", "Murat", "Soult"):
        world.get_marshal(name).location = "Bohemia"
    world.get_marshal("Bernadotte").location = "Moravia"


class TestTheAssaultNamesItsTerms:

    def test_the_line_says_alone_and_who_does_not_join(self, shipped):
        client, world = shipped
        _stage_assault(world)
        data = post(client, "Ney, attack Vienna")
        msg = data["message"]
        assert msg.startswith("ASSAULT — Ney storms the works at Vienna alone: "), msg
        head = msg.split("\n", 1)[0]
        assert "do not join an assault on the works" in head, head
        for name in ("Murat", "Soult", "Bernadotte"):
            assert name in head, (name, head)
        assert "the garrison breaks below 5,000." in head, head

    def test_shown_is_applied(self, shipped):
        """The reckoning the line prints IS the resolver's: the garrison's
        loss follows from the printed figures by the resolver's own formula."""
        client, world = shipped
        _stage_assault(world)
        data = post(client, "Ney, attack Vienna")
        head, rest = data["message"].split("\n", 1)
        att = int(re.search(r"([\d,]+) in the assault's reckoning", head).group(1).replace(",", ""))
        g_eff = re.search(r"\(([\d,]+) behind its ground and works\)", head)
        g_eff = int(g_eff.group(1).replace(",", "")) if g_eff else 25000
        lost = int(re.search(r"\(-([\d,]+)\)", rest).group(1).replace(",", ""))
        assert lost == int(25000 * min(0.50, att / g_eff * 0.35)), (att, g_eff, lost)

    def test_the_hold_names_the_regen(self, shipped):
        client, world = shipped
        _stage_assault(world)
        data = post(client, "Ney, attack Vienna")
        vienna = world.get_region("Vienna")
        assert 5000 <= vienna.garrison_strength < 25000
        gain = min(2000, 25000 - vienna.garrison_strength)
        assert f"It regains up to {gain:,} a turn (to 25,000)." in data["message"], data["message"]

    def test_the_collapse_names_no_regen(self, shipped):
        client, world = shipped
        _stage_assault(world)
        world.get_region("Vienna").garrison_strength = 5200
        world.get_marshal("Ney").strength = 60000
        data = post(client, "Ney, attack Vienna")
        assert data["message"].startswith("ASSAULT — Ney storms the works at Vienna alone")
        assert "Garrison collapses" in data["message"]
        assert "It regains" not in data["message"]

    def test_the_ai_reads_no_line(self, shipped):
        """GR5: the line is the player's; an enemy's assault message is the
        resolver's own, unchanged."""
        client, world = shipped
        john = world.get_marshal("ArchdukeJohn")
        munich = world.get_region("Munich")
        for m in world.marshals.values():
            if m.location == "Munich" and m.name != john.name:
                m.location = "Bohemia"
        john.location = munich.adjacent_regions[0]
        with contextlib.redirect_stdout(io.StringIO()):
            result = M.executor._combat._resolve_garrison_combat(
                john, munich, world, {"world": world})
        assert not result["message"].startswith("ASSAULT"), result["message"]
        assert "It regains" not in result["message"]

    def test_the_lever_down_is_the_bare_message(self, shipped, monkeypatch):
        monkeypatch.setattr(CombatExecutor, "AN_ASSAULT_NAMES_ITS_TERMS", False)
        client, world = shipped
        _stage_assault(world)
        data = post(client, "Ney, attack Vienna")
        assert data["message"].startswith("Ney assaults the Vienna garrison!"), data["message"]


# ═══════════════════════════════════════════════════════════════════════════
# The single sources
# ═══════════════════════════════════════════════════════════════════════════

class TestTheRegenIsOneRule:

    def test_the_rule(self, shipped):
        _client, world = shipped
        vienna = world.get_region("Vienna")
        vienna.garrison_strength = 24000
        assert world.capital_garrison_regen(vienna) == 1000
        vienna.garrison_strength = 12000
        assert world.capital_garrison_regen(vienna) == WS.CAPITAL_GARRISON_REGEN_PER_TURN == 2000
        vienna.garrison_detachment = True
        assert world.capital_garrison_regen(vienna) == 0
        normandy = world.get_region("Normandy")
        normandy.garrison_strength = 6000
        assert world.capital_garrison_regen(normandy) == 0          # a depot, not a capital

    def test_the_loop_applies_the_rule(self, shipped, monkeypatch):
        """The advance regrows exactly `capital_garrison_regen` — patch the
        constant and the loop follows it."""
        _client, world = shipped
        monkeypatch.setattr(WS, "CAPITAL_GARRISON_REGEN_PER_TURN", 700)
        vienna = world.get_region("Vienna")
        vienna.garrison_strength = 12000
        with contextlib.redirect_stdout(io.StringIO()):
            world.advance_turn()
        if vienna.controller == "Austria":
            assert vienna.garrison_strength == 12700


class TestOneFogRule:

    def test_the_view_agrees_with_the_map_summary(self, shipped):
        """`garrison_view` is the map summary's own rule — pinned on every
        province of the boot board and after a targeted scout."""
        client, world = shipped
        world.get_marshal("Ney").location = "Bohemia"
        post(client, "Ney, scout Vienna")
        summary = world.get_filtered_game_state_summary()["map_data"]
        checked = 0
        for name, row in summary.items():
            form, value = GR.garrison_view(world, name, world.player_nation)
            shown = row.get("garrison_strength", 0)
            if form == "exact":
                assert shown == value, (name, form, value, shown)
            elif form == "band":
                assert shown == -1 and row.get("garrison_strength_band") == value, (name, value, row)
            else:
                assert shown == 0, (name, form, shown)
            checked += 1
        assert checked >= 100

    def test_the_resolver_fights_the_one_formula(self, shipped):
        _client, world = shipped
        vienna = world.get_region("Vienna")
        vienna.buildings.append({"type": "fortification", "damaged": False})
        assert GR.garrison_effective(vienna) == int(25000 * 1.0 * 1.25)


class TestTheDeskReadsTheFog:

    def test_safe_at_partial_is_a_band(self, shipped):
        client, world = shipped
        from backend.models.intel import PARTIAL
        world.get_region_intel("Vienna").refresh(visibility=PARTIAL, source="probe",
                                                  turn=world.current_turn)
        data = post(client, "is Vienna safe")
        assert "garrison of 25,000" not in data["message"], data["message"]
        assert "held by a garrison (" in data["message"], data["message"]

    def test_who_is_at_vienna_names_the_garrison(self, shipped):
        client, world = shipped
        world.get_marshal("Ney").location = "Bohemia"
        _empty_vienna(world)
        post(client, "Ney, scout Vienna")
        data = post(client, "who is at Vienna")
        assert "No army stands in Vienna" not in data["message"], data["message"]
        assert "Garrison: 25,000." in data["message"], data["message"]
