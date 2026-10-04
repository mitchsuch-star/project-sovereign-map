"""RS-11 "take <province>" and SF-V8 "the landing names its man" — the two
riders of Chunk 3b trimmed to what the census confirms (SCORE_FINISH_SPEC.md
§3 Step 4; rules SYSTEMS_REFERENCE.md §89; rows BUG_FIXES.md RS-11, SF-V8).

RS-11, reproduced at HEAD `e631f4bd`: "Bernadotte, take Bohemia", "Ney, take
Swabia", "Iron Marshal, take Swabia" (the fresh blind census's line), "Ney,
take the province of Swabia" and "Ney, go and take Swabia" each SHRUGGED
keyless — "take" is deliberately no parse-seam verb (`attack_vocabulary`'s
pinned exclusion: "take care of X", "what would it take"). The rule: the
objective resolves to a marshal and a road the march law allows — in reach,
the capture verbs' attack road; beyond it, a standing march with the attack
on arrival, its road read by the march law at issuance; no marshal named,
the man in reach or the one with the shortest lawful road.

SF-V8, reproduced: "land Oudinot in Munster with 5,000 men" answered for
LANNES — the word "land" fuzzy-matched "Lannes" (partial ratio 75, over the
70 a four-letter word needs) in the parser's word scan, so the name the
player gave was never read; the expedition quoted Lannes' 18,000.
"""

import pytest
from fastapi.testclient import TestClient

import backend.commands.parser as P
import backend.main as M
from backend.commands.parser import CommandParser


@pytest.fixture
def shipped(monkeypatch):
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    return TestClient(M.app), M.world


def post(client, command):
    return client.post("/command", json={"command": command}).json()


SHRUG = ("cannot interpret", "instruction is unclear", "cannot parse this order",
         "cannot determine the order", "cannot answer that")


def shrugged(reply):
    return any(s in str(reply.get("message") or "") for s in SHRUG)


# ═══════════════════════════════════════════════════════════════════════════
# RS-11
# ═══════════════════════════════════════════════════════════════════════════

class TestTakeIsAnObjective:

    @pytest.mark.parametrize("line", [
        "Ney, take Swabia", "Ney, take the province of Swabia",
        "Ney, go and take Swabia", "Iron Marshal, take Swabia",
        "Bernadotte, take Bohemia", "Ney take Swabia", "take Swabia", "take Tyrol",
    ])
    def test_the_census_lines_no_longer_shrug(self, shipped, line):
        client, world = shipped
        assert not shrugged(post(client, line)), line

    def test_in_reach_it_is_the_capture_road(self, shipped):
        """"Ney, take Swabia" is "Ney, capture Swabia": the attack road and
        its muster."""
        client, world = shipped
        mack = int(world.get_marshal("Mack").strength)
        reply = post(client, "Ney, take Swabia")
        assert ("MUSTER" in str(reply.get("message") or "")
                or int(M.world.get_marshal("Mack").strength) < mack), reply.get("message")

    def test_beyond_reach_it_is_a_march_that_strikes_on_arrival(self, shipped):
        client, world = shipped
        post(client, "Ney, take Vienna")
        order = M.world.get_marshal("Ney").strategic_order
        assert order is not None and order.command_type == "MOVE_TO", order
        assert order.target == "Vienna" and order.attack_on_arrival is True

    def test_no_marshal_named_it_is_the_shortest_lawful_road(self, shipped):
        """Vienna is in nobody's reach; Bernadotte at Franconia has the
        shortest open road (Bohemia, Vienna) — named in the reply."""
        client, world = shipped
        from backend.commands.strategic import nearest_lawful_marcher
        chosen, road, _r = nearest_lawful_marcher(world, "Vienna")
        reply = post(client, "take Vienna")
        order = M.world.get_marshal(chosen.name).strategic_order
        assert order is not None and order.target == "Vienna", reply.get("message")
        assert order.attack_on_arrival is True
        assert f"{chosen.name} has the shortest open road to Vienna" in str(
            reply.get("warning") or reply.get("message") or ""), reply

    def test_a_province_no_road_reaches_says_why(self, shipped):
        """Berlin (Prussia, at peace) — the march law has no road; nothing
        is spent and the answer names the closed frontier."""
        client, world = shipped
        ap = int(world.actions_remaining)
        reply = post(client, "take Berlin")
        assert int(M.world.actions_remaining) == ap
        assert "Berlin" in str(reply.get("message") or ""), reply.get("message")

    def test_a_province_of_ours_is_a_march(self, shipped):
        client, world = shipped
        post(client, "Ney, take Paris")
        order = M.world.get_marshal("Ney").strategic_order
        assert order is not None and (order.command_type, order.target) == ("MOVE_TO", "Paris")
        assert order.attack_on_arrival is False

    def test_a_foe_is_attacked(self, shipped):
        assert P.rewrite_take_objective("Ney, take Mack", None, M.world)[0] == "Ney, attack Mack"

    def test_a_court_gets_the_capture_roads_answer(self, shipped):
        client, world = shipped
        reply = post(client, "Ney, take Bavaria")
        assert "is a nation, not a province" in str(reply.get("message") or "")

    @pytest.mark.parametrize("line", [
        "Ney, take care of Mack", "what would it take to beat Mack",
        "Ney, take the field", "Talleyrand, what would it take to get peace with Prussia?",
    ])
    def test_the_pinned_exclusions_are_untouched(self, shipped, line):
        assert P.rewrite_take_objective(line, None, M.world) == (line, None)

    def test_an_unknown_addressee_is_refused_by_name(self, shipped):
        client, world = shipped
        reply = post(client, "Zorglub, take Swabia")
        assert "There is no Marshal 'Zorglub'" in str(reply.get("message") or "")

    def test_the_lever_down_shrugs_again(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(P, "TAKE_IS_AN_OBJECTIVE", False)
        assert shrugged(post(client, "Ney, take Swabia"))


# ═══════════════════════════════════════════════════════════════════════════
# SF-V8
# ═══════════════════════════════════════════════════════════════════════════

class TestTheLandingNamesItsMan:

    @pytest.mark.parametrize("line,name", [
        ("land Oudinot in Munster with 5,000 men", "Oudinot"),
        ("land Oudinot in Munster", "Oudinot"),
        ("land Zorglub in Munster", "Zorglub"),
    ])
    def test_an_unknown_corps_is_refused_by_name_for_nothing(self, shipped, line, name):
        client, world = shipped
        ap, gold = int(world.actions_remaining), int(world.gold)
        reply = post(client, line)
        message = str(reply.get("message") or "")
        assert f"There is no Marshal '{name}' in the order of battle" in message, message
        assert "Lannes" not in message, message
        assert (int(M.world.actions_remaining), int(M.world.gold)) == (ap, gold)

    def test_a_named_corps_is_the_one_priced(self, shipped):
        client, world = shipped
        reply = post(client, "land Lannes in Munster")
        assert "Lannes commands" in str(reply.get("message") or ""), reply.get("message")
        reply = post(client, "land Soult in Munster")
        assert "Soult commands" in str(reply.get("message") or ""), reply.get("message")

    def test_a_routed_order_word_is_never_a_name(self, shipped):
        result = M.parser.parse("land Oudinot in Munster", M.get_llm_game_state(), world=M.world)
        assert (result.get("command") or {}).get("marshal") != "Lannes"

    def test_the_lever_down_reads_land_as_lannes_again(self, shipped, monkeypatch):
        monkeypatch.setattr(P, "A_ROUTED_WORD_IS_NEVER_A_NAME", False)
        result = M.parser.parse("land Oudinot in Munster", M.get_llm_game_state(), world=M.world)
        assert (result.get("command") or {}).get("marshal") == "Lannes"
