"""CRT-10 "The suggestion is honest", led by SF-V4 "A proper name asks"
(SCORE_FINISH_SPEC.md §6.3, the gate record of September 28, 2026 — its
item 5 names this file; COMMAND_ROBUSTNESS_SPEC.md §12.16; rules
SYSTEMS_REFERENCE.md §89; rows BUG_FIXES.md SF-V4, NPC-6).

THE RULING: an attack that names a PROPER NAME matching nothing makes the
marshal ASK, for free, naming only foes in sight; a descriptive phrase keeps
today's disclosed substitution (PS18-R1). Reproduced at HEAD `e631f4bd`:
"Ney, attack Zorglub" / "Alsace" / "Lombardy" each answered "Your words named
no foe our maps know, Sire — Ney marches on Mack at Swabia, the nearest in
sight." and the battle was fought; the bare "attack Zorglub" asked which
MARSHAL Zorglub was, and answering "1" sent Soult against Mack.

Every pin drives the real `POST /command` on a fresh SHIPPED 1805 boot and
reads the world before and after.
"""

import pytest
from fastapi.testclient import TestClient

import backend.commands.proper_name as PN
import backend.main as M
from backend.commands.parser import CommandParser
from backend.display_names import humanize_entity_name


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


def board(world):
    return ({m.name: (m.location, int(m.strength)) for m in world.marshals.values()},
            int(world.actions_remaining), int(world.gold))


def hidden_foes(world):
    seen = {e.name for e in world.get_visible_enemies("France")}
    return [humanize_entity_name(m.name) for m in world.marshals.values()
            if m.nation != "France" and m.name not in seen
            and world.is_at_war("France", m.nation)]


# The four personalities: aggressive, cautious, literal, the sovereign.
MARSHALS = ["Ney", "Davout", "Soult", "Napoleon"]
PROBES = ["Zorglub", "Alsace", "Lombardy", "Venetia", "Atlantis", "Ulm",
          "Bonaparte", "zorglub"]


class TestAProperNameAsks:

    @pytest.mark.parametrize("who", MARSHALS)
    @pytest.mark.parametrize("name", PROBES)
    def test_nothing_is_spent_or_lost_and_nothing_hidden_named(self, shipped, who, name):
        client, world = shipped
        before = board(world)
        reply = post(client, f"{who}, attack {name}")
        assert board(M.world) == before, (who, name, reply.get("message"))
        assert not reply.get("battle_report")
        message = str(reply.get("message") or "")
        assert message.startswith(f"No foe called {name[:1].upper()}{name[1:]} is in sight"), message
        assert reply.get("state") == "awaiting_clarification", message
        shown = message + " ".join(str(o.get("label")) for o in reply.get("options") or [])
        for foe in hidden_foes(M.world):
            assert foe not in shown, (who, name, foe)

    @pytest.mark.parametrize("who", MARSHALS)
    def test_yes_engages_the_foe_the_question_named(self, shipped, who):
        client, world = shipped
        first = post(client, f"{who}, attack Zorglub")
        named = first.get("interpreted_target")
        assert named == "Mack", first.get("message")
        reply = post(client, "yes")
        message = str(reply.get("message") or "")
        assert "No foe called" not in message, message
        assert reply.get("state") != "awaiting_clarification" or reply.get("objection") \
            or "MUSTER" in message or "Mack" in message, message

    def test_two_takes_the_second_and_cancel_withdraws(self, shipped):
        client, world = shipped
        first = post(client, "Ney, attack Zorglub")
        second_target = first["options"][1]["target"]
        reply = post(client, "2")
        assert second_target in str(reply) or humanize_entity_name(second_target) in str(reply)
        client, world = shipped
        M._reset_world_state()
        post(client, "Ney, attack Zorglub")
        before = board(M.world)
        reply = post(client, "cancel")
        assert "withdrawn" in str(reply.get("message") or "")
        assert board(M.world) == before

    def test_attack_him_engages_the_named_foe(self, shipped):
        client, world = shipped
        post(client, "Ney, attack Zorglub")
        mack = int(M.world.get_marshal("Mack").strength)
        reply = post(client, "attack him")
        assert int(M.world.get_marshal("Mack").strength) < mack or "Mack" in str(
            reply.get("message") or ""), reply.get("message")

    @pytest.mark.parametrize("who", ["Ney", "Massena", "Bernadotte", "Napoleon"])
    def test_the_foes_are_offered_nearest_first(self, shipped, who):
        client, world = shipped
        reply = post(client, f"{who}, attack Zorglub")
        here = M.world.get_marshal(who).location
        dist = [M.world.get_distance(here, M.world.get_marshal(o["target"]).location)
                for o in reply["options"]]
        assert dist == sorted(dist), (who, dist)

    def test_the_sort_is_needed_on_the_shipped_board(self, shipped):
        """The sensitivity arm (the first sweep found the pin above inert
        from Rhineland, where the map's own order is already nearest-first):
        from Milan the foes in sight come Mack at Swabia (2) before Archduke
        John at Tyrol (1), so Massena's question must name John."""
        client, world = shipped
        raw = [e for e in world.get_visible_enemies("France") if e.strength > 0]
        here = world.get_marshal("Massena").location
        dist = [world.get_distance(here, e.location) for e in raw]
        assert dist != sorted(dist), dist
        reply = post(client, "Massena, attack Zorglub")
        assert reply.get("interpreted_target") == "ArchdukeJohn", reply.get("message")
        assert reply["options"][0]["target"] == "ArchdukeJohn"
        assert "The nearest in sight is Archduke John at Tyrol" in str(reply.get("message"))

    def test_a_near_miss_asks_did_you_mean(self, shipped):
        client, world = shipped
        for typed in ("Makc", "Mach"):
            M._reset_world_state()
            before = board(M.world)
            reply = post(client, f"Ney, attack {typed}")
            assert str(reply.get("message")).startswith(
                f"No foe called {typed} is in sight, Sire — did you mean Mack at Swabia?"), reply.get("message")
            assert reply.get("interpreted_target") == "Mack"
            assert board(M.world) == before

    def test_nothing_in_sight_is_the_reworded_refusal(self, shipped):
        """Every foe France is at war with drawn off beyond sight: the
        existing refusal, reworded "in sight" (§6.3), nothing spent."""
        client, world = shipped
        far = max(M.world.regions, key=lambda r: M.world.get_distance("Rhineland", r)
                  if M.world.get_distance("Rhineland", r) < 999 else -1)
        for m in list(M.world.marshals.values()):
            if m.nation != "France" and M.world.is_at_war("France", m.nation):
                m.location = far
        M.world.calculate_visibility()
        assert not PN._visible_nearest_first(M.world, M.world.get_marshal("Ney")), far
        before = board(M.world)
        reply = post(client, "Ney, attack Zorglub")
        assert "No foe called Zorglub is in sight, Sire, nor any other" in str(
            reply.get("message") or ""), reply.get("message")
        assert board(M.world) == before


class TestADescriptionStillProceeds:

    @pytest.mark.parametrize("phrase", [
        "the weakest enemy", "the enemy vanguard", "the British army",
        "the enemy in front of you", "the rest", "anyone nearby",
        "the retreating column", "retreating column", "enemy cavalry",
        "their left flank", "at dawn", "the Zorglub column",
    ])
    def test_it_is_no_proper_name(self, shipped, phrase):
        assert PN.proper_name_in(PN.attack_tail(f"Ney, attack {phrase}"),
                                 M.world, "France") is None

    def test_a_province_typo_is_no_proper_name(self, shipped):
        """A slip on a province's name ("Swabbia") is the region matcher's
        to correct (CX3-X3), never "No foe called Swabbia"."""
        assert PN.proper_name_in("Swabbia", M.world, "France") is None
        client, world = shipped
        reply = post(client, "Ney, attack Swabbia")
        assert "No foe called" not in str(reply.get("message") or "")

    def test_a_description_discloses_and_proceeds(self, shipped):
        client, world = shipped
        reply = post(client, "Ney, smash the retreating column")
        assert "named no foe our maps know" in str(reply.get("message") or "")


class TestTheSpecialCases:

    def test_the_bench_answer_is_identical_before_and_after_a_commission(self, shipped):
        client, world = shipped
        before = post(client, "Soult, attack Paget")
        assert "No intelligence on Paget's position" in str(before.get("message") or "")
        from backend.game_logic.recruitment import commission_marshal, find_candidate
        M._reset_world_state()
        candidate = find_candidate(M.world, "Britain", "Paget")
        M.world.nation_gold["Britain"] = 100000
        commission_marshal(M.world, "Britain", candidate)
        assert M.world.get_marshal("Paget") is not None
        after = post(client, "Soult, attack Paget")
        assert after.get("message") == before.get("message"), (before.get("message"), after.get("message"))

    def test_a_visible_death_gets_the_tombstone_line(self, shipped):
        client, world = shipped
        john = world.get_marshal("ArchdukeJohn")
        world.destroy_marshal(john, cause="battle", victor="France", location=john.location)
        reply = post(client, "Massena, attack Archduke John")
        assert str(reply.get("message")).startswith(
            "Archduke John fell at Tyrol on turn"), reply.get("message")
        assert "his corps is no more" in str(reply.get("message"))

    def test_an_unseen_death_is_the_plain_ask(self, shipped):
        client, world = shipped
        john = world.get_marshal("ArchdukeJohn")
        world.destroy_marshal(john, cause="battle", victor="Russia", location="Hungary")
        reply = post(client, "Massena, attack Archduke John")
        message = str(reply.get("message") or "")
        assert message.startswith("No foe called Archduke John is in sight"), message
        assert "fell" not in message and "Hungary" not in message

    def test_the_bare_road_asks_the_target_never_the_marshal(self, shipped):
        client, world = shipped
        reply = post(client, "attack Zorglub")
        assert "There is no Marshal" not in str(reply.get("message") or "")
        assert str(reply.get("message")).startswith("No foe called Zorglub")
        ours = {m.name for m in M.world.marshals.values() if m.nation == "France"}
        for option in reply.get("options") or []:
            assert option["target"] not in ours, option
            assert not any(option["command"].startswith(n) for n in ours), option

    def test_the_arrival_tail_marches_and_names_the_word(self, shipped):
        client, world = shipped
        reply = post(client, "Davout, march to Lorraine then attack Zorglub")
        order = M.world.get_marshal("Davout").strategic_order
        assert order is not None and order.attack_on_arrival is False
        assert "No foe called Zorglub" in str(reply.get("message") or "")

    def test_the_word_is_named_on_the_first_steps_interrupt(self, shipped):
        """The march's first step meets Mack at Swabia and stops on the
        bad-odds interrupt — a reply the strategic parser's note never
        reached; the executor names the dropped word on it (the first sweep
        found the pin above inert here: Lorraine is our own ground)."""
        client, world = shipped
        reply = post(client, "Ney, march to Swabia then attack Zorglub")
        message = str(reply.get("message") or "")
        assert "Odds unfavorable" in message, message
        assert message.count("No foe called Zorglub is in sight") == 1, message
        order = M.world.get_marshal("Ney").strategic_order
        assert order is not None and order.attack_on_arrival is False


class TestTheLever:

    def test_the_lever_down_restores_disclose_and_proceed(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(PN, "A_PROPER_NAME_ASKS", False)
        reply = post(client, "Ney, attack Zorglub")
        assert "named no foe our maps know" in str(reply.get("message") or "")


# ═══════════════════════════════════════════════════════════════════════════
# The instrument reads the answer (command C4, `tools/score_run.py`)
# ═══════════════════════════════════════════════════════════════════════════

class TestTheInstrumentReadsTheAnswer:
    """The exit's DL arm answers the question by the driver's dial ("first":
    yes), so the battle that follows is the order the player gave. The C4
    probe had counted it as the substitution the ruling forbids; a fight
    BEFORE the answer still fails it."""

    ASK = ("No foe called Alsace is in sight, Sire. The nearest in sight is "
           "Mack at Tyrol — shall we engage him?")

    def _c4(self, tmp_path, head, subs):
        import json
        import sys
        from pathlib import Path
        root = Path(__file__).resolve().parents[1]
        sys.path.insert(0, str(root))
        from tools import score_run as SR
        arm_dir = tmp_path / "DL"
        arm_dir.mkdir()
        (arm_dir / "meta.json").write_text(json.dumps(
            {"status": "completed", "unknown_blockers": []}), encoding="utf-8")
        body = "".join(f"  - {s}\n" for s in subs)
        (arm_dir / "digest.md").write_text(
            f"# d\n\n## Turn 1 — x\n- CMD `attack Alsace` → ✓ {head}\n{body}",
            encoding="utf-8")
        (arm_dir / "digest.jsonl").write_text('{"kind": "turn", "turn": 1}\n', encoding="utf-8")
        ctx = {"dl_script": {"dl_lines": {"SF-V4": ["attack Alsace"]}}}
        return SR.r_command_C4({"DL": SR.Arm(arm_dir)}, ctx)

    def test_a_fight_after_the_answer_is_the_players_order(self, tmp_path):
        result = self._c4(tmp_path, self.ASK, [
            "POPUP clarification: Berthier, attack_target, x → 1 (first option: Mack at Tyrol)",
            "↳ MUSTER — Massena (29,762) vs Mack at Tyrol — the balance of force looks even.",
            "⚔ Massena (lost 2946, own corps) vs Mack (lost 5986, own corps)",
        ])
        assert result["pass"] is True, result

    def test_the_substitution_still_fails(self, tmp_path):
        result = self._c4(tmp_path, "Your words named no foe our maps know, Sire — "
                          "Massena marches on Mack at Tyrol, the nearest in sight.",
                          ["⚔ Massena (lost 2946) vs Mack (lost 5986)"])
        assert result["pass"] is False, result

    def test_a_fight_before_any_answer_still_fails(self, tmp_path):
        result = self._c4(tmp_path, self.ASK, [
            "⚔ Massena (lost 2946) vs Mack (lost 5986)",
            "POPUP clarification: Berthier, attack_target, x → 1 (first option: Mack at Tyrol)",
        ])
        assert result["pass"] is False, result
