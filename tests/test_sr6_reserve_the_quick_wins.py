"""The Step 2 reserve (Score Finish, October 2, 2026) — the quick-win bank.

RS-5 + VP-R1-X1 + NPC-D4 · RS-13 · NPC-11 · NPC-13 · NPC-17 · NPC-21 ·
NPC-25 · RS-28 · NP-X5. (RS-14, the desk's court / alarm kinds, is pinned
in `test_sr6a_the_dispatch_pass.py`.)
"""
import contextlib
import io
import json
import random as _random
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.commands import combat_executor as CE
from backend.commands import diplomatic_executor as DE
from backend.commands import disobedience as DS
from backend.commands import meta_executor as ME
from backend.commands import movement_executor as MV
from backend.commands import strategic_executor as SE
from backend.commands.combat_executor import CombatExecutor
from backend.commands.parser import CommandParser
from backend.display_names import MUSTER_REASON_DISPLAY
from backend.models.intel import FULL

REPO = Path(__file__).resolve().parents[1]


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture
def shipped(monkeypatch):
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    # The objection's ONE random draw (`objection_v2._random_concern_shift`:
    # 10% up, 15% down) is pinned flat so a mounted objection is a fact of
    # the staging, not of the shared RNG state another file left behind.
    monkeypatch.setattr(_random, "random", lambda: 0.5)
    return TestClient(M.app), M.world


def post(client, command):
    return client.post("/command", json={"command": command}).json()


def _see(world, region, marshal):
    world.get_region_intel(region).refresh(
        FULL, "scout", int(world.current_turn),
        marshals=[{"name": marshal.name, "nation": marshal.nation,
                   "strength": int(marshal.strength)}],
        total_strength=int(marshal.strength))


def _find(obj, key):
    """Depth-first: the first value under `key` anywhere in a payload."""
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for v in obj.values():
            got = _find(v, key)
            if got is not None:
                return got
    elif isinstance(obj, list):
        for v in obj:
            got = _find(v, key)
            if got is not None:
                return got
    return None


# ═══════════════════════════════════════════════════════════════════════════
# RS-5 — the objection offers a man we have seen
# ═══════════════════════════════════════════════════════════════════════════

class TestTheObjectionOffersAManWeHaveSeen:

    def test_at_boot_murat_is_offered_the_adjacent_mack_in_view(self, shipped):
        client, world = shipped
        post(client, "Murat, support Davout")
        objection = world.pending_strategic_objection or {}
        trust = next((o for o in objection.get("options") or [] if o.get("type") == "preferred"), {})
        assert trust.get("text") == "Trust: Murat attacks Mack", objection.get("options")
        assert "Mack" in {m.name for m in world.get_visible_enemies("France")}

    def test_a_man_never_seen_is_not_offered(self, shipped, monkeypatch):
        client, world = shipped
        murat = world.marshals["Murat"]
        monkeypatch.setattr(type(world), "get_visible_enemies", lambda self, nation: [])
        preferred = DS._get_aggressive_preferred(murat, world) or {}
        assert preferred.get("action") not in ("attack", "pursue"), preferred
        monkeypatch.setattr(DS, "THE_OBJECTION_OFFERS_A_MAN_WE_HAVE_SEEN", False)
        assert DS._get_aggressive_preferred(murat, world) == {"action": "attack", "target": "Mack"}

    def test_the_distance_is_measured_to_where_the_player_believes_him(self, shipped):
        client, world = shipped
        murat, mack = world.marshals["Murat"], world.marshals["Mack"]
        assert world.get_last_known_location("Mack")[0] == "Swabia"
        mack.location = "Bohemia"          # the truth moves; the intel does not
        world._build_marshal_index()
        preferred = DS._get_aggressive_preferred(murat, world)
        assert preferred == {"action": "attack", "target": "Mack"}, preferred

    def test_a_shut_crossing_is_skipped(self, shipped, monkeypatch):
        client, world = shipped
        ney, moore = world.marshals["Ney"], world.marshals["Moore"]
        assert moore.location == "London"
        ney.location = "Normandy"
        for other in ("Mack", "ArchdukeJohn", "ArchdukeCharles"):
            world.marshals[other].location = "Galicia"
        world._build_marshal_index()
        world.calculate_visibility()
        _see(world, "London", moore)
        assert "Moore" in {m.name for m in world.get_visible_enemies("France")}
        assert world.is_at_war("France", "Britain")
        assert not DS._crossing_open(world, ney, "London")
        preferred = DS._get_aggressive_preferred(ney, world) or {}
        assert preferred.get("target") != "Moore", preferred
        monkeypatch.setattr(DS, "THE_OBJECTION_OFFERS_A_MAN_WE_HAVE_SEEN", False)
        assert DS._get_aggressive_preferred(ney, world) == {"action": "attack", "target": "Moore"}

    def test_a_refused_trust_keeps_the_objection_and_the_order(self, shipped, monkeypatch):
        """The backstop: the Trust arm's order is REFUSED (a pursuit of a man
        nobody has seen) — the objection stays, the tracker records nothing,
        and Insist still issues the support order the player gave."""
        client, world = shipped
        r = post(client, "Murat, support Davout")
        assert world.pending_strategic_objection, r.get("message")
        # The preferred arm (attack Mack) is REFUSED by the executor when
        # the answer comes — the road is shut, say.
        monkeypatch.setattr(CombatExecutor, "_execute_attack",
                            lambda self, *a, **k: {"success": False,
                                                   "message": "The road is shut."})
        auth_before = int(world.authority_tracker.authority)
        window_before = list(world.authority_tracker.recent_responses)
        r = client.post("/respond_to_objection", json={"choice": "trust"}).json()
        assert r.get("success") is False, r.get("message")
        assert "The objection stands" in r.get("message", ""), r.get("message")
        assert world.pending_strategic_objection is not None
        assert int(world.authority_tracker.authority) == auth_before
        assert list(world.authority_tracker.recent_responses) == window_before
        r = client.post("/respond_to_objection", json={"choice": "insist"}).json()
        assert r.get("success") is True, r.get("message")
        order = world.marshals["Murat"].strategic_order
        assert order is not None and order.command_type == "SUPPORT" and order.target == "Davout"

    def test_lever_down_loses_the_order(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(SE, "A_REFUSED_TRUST_KEEPS_THE_OBJECTION", False)
        post(client, "Murat, support Davout")
        assert world.pending_strategic_objection
        monkeypatch.setattr(CombatExecutor, "_execute_attack",
                            lambda self, *a, **k: {"success": False,
                                                   "message": "The road is shut."})
        r = client.post("/respond_to_objection", json={"choice": "trust"}).json()
        assert r.get("success") is False
        assert world.pending_strategic_objection is None
        r = client.post("/respond_to_objection", json={"choice": "insist"}).json()
        assert r.get("success") is False
        assert world.marshals["Murat"].strategic_order is None


# ═══════════════════════════════════════════════════════════════════════════
# VP-R1-X1 — the alternative is a foe at war
# ═══════════════════════════════════════════════════════════════════════════

class TestTheAlternativeIsAFoeAtWar:

    def test_an_allys_corps_is_never_in_range(self, shipped, monkeypatch):
        client, world = shipped
        ney, deroy = world.marshals["Ney"], world.marshals["Deroy"]
        assert deroy.nation == "Bavaria" and not world.is_at_war("France", "Bavaria")
        ney.location = "Munich"            # adjacent to Deroy's Franconia
        world._build_marshal_index()
        world.calculate_visibility()
        names = [m.name for m in DS.get_enemies_in_range(ney, world)]
        assert "Deroy" not in names, names
        assert "Mack" in names             # Swabia adjoins Munich; at war, in view
        monkeypatch.setattr(DS, "THE_ALTERNATIVE_IS_A_FOE_AT_WAR", False)
        assert "Deroy" in [m.name for m in DS.get_enemies_in_range(ney, world)]

    def test_a_fogged_foe_is_never_in_range_for_the_player(self, shipped, monkeypatch):
        client, world = shipped
        ney = world.marshals["Ney"]
        ney.location = "Munich"
        world._build_marshal_index()
        world.calculate_visibility()
        monkeypatch.setattr(type(world), "get_visible_enemies", lambda self, nation: [])
        assert DS.get_enemies_in_range(ney, world) == []


# ═══════════════════════════════════════════════════════════════════════════
# NPC-D4 / NPC-11 — the pursuit states its terms; the literal quotes you
# ═══════════════════════════════════════════════════════════════════════════

class TestThePursuitStatesItsTermsAndTheLiteralQuotesYou:

    def _arm(self, world):
        john = world.marshals["ArchdukeJohn"]
        assert john.location == "Tyrol"
        _see(world, "Tyrol", john)

    def test_the_upgrade_announces_itself(self, shipped):
        client, world = shipped
        self._arm(world)
        msg = post(client, "Soult, attack Archduke John").get("message", "")
        assert msg.startswith("Soult pursues Archduke John (at Tyrol)."), msg
        assert "A standing order, not a single attack: he closes 1 province a turn" in msg
        assert "attacks on arrival, may be diverted by an interrupt, and stands down if intelligence on him lapses" in msg
        assert "'Soult, cancel' recalls him." in msg
        # NPC-11: the literal's quote is the player's own words.
        assert '"Soult, attack Archduke John."' in msg
        assert "ArchdukeJohn" not in msg

    def test_an_explicit_pursuit_states_no_terms(self, shipped):
        client, world = shipped
        self._arm(world)
        msg = post(client, "Soult, pursue Archduke John").get("message", "")
        assert msg.startswith("Soult pursues Archduke John"), msg
        assert "A standing order, not a single attack" not in msg

    def test_levers_down(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(SE, "THE_PURSUIT_STATES_ITS_TERMS", False)
        monkeypatch.setattr(CE, "THE_LITERAL_QUOTES_THE_TYPED_ORDER", False)
        self._arm(world)
        msg = post(client, "Soult, attack Archduke John").get("message", "")
        assert "A standing order" not in msg
        assert '"Soult attack ArchdukeJohn."' in msg, msg


# ═══════════════════════════════════════════════════════════════════════════
# RS-13 — the pressed attack prints its muster
# ═══════════════════════════════════════════════════════════════════════════

class TestThePressedAttackPrintsItsMuster:

    def _object(self, client, world):
        davout, mack = world.marshals["Davout"], world.marshals["Mack"]
        davout.location = "Lorraine"
        davout.strength = 12000
        davout.modify_trust(-30)
        world._build_marshal_index()
        world.calculate_visibility()
        r = post(client, "Davout, attack Mack")
        assert r.get("pending_objection"), r.get("message")
        return r

    def test_insist_carries_the_muster(self, shipped):
        client, world = shipped
        self._object(client, world)
        result = M.executor._meta.handle_objection_response("insist", {"world": world})
        msg = result.get("message", "")
        assert "MUSTER — Davout (" in msg, msg
        assert "the balance of force looks" in msg, msg
        assert not _find(result, "muster_confirm"), "the confirm popup must stay off"
        assert "[Combat]" in msg, "the attack still resolves behind the muster"

    def test_lever_down_opens_straight_onto_the_lines(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(ME, "THE_PRESSED_ATTACK_PRINTS_ITS_MUSTER", False)
        self._object(client, world)
        result = M.executor._meta.handle_objection_response("insist", {"world": world})
        assert "MUSTER — Davout (" not in result.get("message", "")
        assert "[Combat]" in result.get("message", "")


# ═══════════════════════════════════════════════════════════════════════════
# NPC-13 — the engaged refusal names the enemy
# ═══════════════════════════════════════════════════════════════════════════

class TestTheEngagedRefusalNamesTheEnemy:

    def _engage(self, world):
        ney = world.marshals["Ney"]
        ney.location = "Swabia"             # Mack stands here
        world._build_marshal_index()
        world.calculate_visibility()

    def test_the_refusal(self, shipped):
        client, world = shipped
        self._engage(world)
        r = post(client, "Ney, move to Tyrol")
        assert r.get("success") is False
        msg = r.get("message", "")
        assert msg.startswith("Cannot advance while engaged with Mack at Swabia."), msg
        assert "fall back to friendly ground — " in msg and "Lorraine" in msg, msg
        assert "Friendly regions adjacent:" not in json.dumps(r)
        # The structured hint rides the executor's own result.
        direct = M.executor.execute(
            {"success": True, "command": {"marshal": "Ney", "action": "move", "target": "Tyrol"}},
            {"world": world})
        assert "'Ney, retreat' falls back to" in (direct.get("suggestion") or ""), direct
        assert "Lorraine" in (direct.get("retreat_options") or []), direct

    def test_no_friendly_ground_says_so(self, shipped):
        client, world = shipped
        self._engage(world)
        for name in ("Rhineland", "Lorraine", "Franche-Comte"):
            world.regions[name].controller = "Austria"
        world.invalidate_active_nations_cache()
        r = post(client, "Ney, move to Tyrol")
        assert "No friendly province adjoins him: he must fight or stand." in r.get("message", ""), r

    def test_lever_down(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(MV, "THE_ENGAGED_REFUSAL_NAMES_THE_ENEMY", False)
        self._engage(world)
        r = post(client, "Ney, move to Tyrol")
        assert r.get("message", "").startswith("Cannot advance while engaged with enemy forces.")


# ═══════════════════════════════════════════════════════════════════════════
# NPC-17 — the muster names the lead
# ═══════════════════════════════════════════════════════════════════════════

class TestTheMusterNamesTheLead:

    def test_the_emperor_leading_is_not_hedged(self, shipped, monkeypatch):
        client, world = shipped
        nap, mack = world.marshals["Napoleon"], world.marshals["Mack"]
        assert nap.location != mack.location
        preview = M.executor._combat._build_muster_preview(nap, mack, world, {"world": world})
        assert preview["presence_note"].endswith("fights +10% harder.")
        assert "if he marches" not in preview["presence_note"]
        monkeypatch.setattr(CE, "THE_MUSTER_NAMES_THE_LEAD", False)
        preview = M.executor._combat._build_muster_preview(nap, mack, world, {"world": world})
        assert "if he marches" in preview["presence_note"]

    def test_a_marshal_leading_with_the_emperor_at_home_stays_hedged(self, shipped):
        client, world = shipped
        soult, mack = world.marshals["Soult"], world.marshals["Mack"]
        assert soult.location == world.marshals["Napoleon"].location
        preview = M.executor._combat._build_muster_preview(soult, mack, world, {"world": world})
        assert "if he marches" in preview["presence_note"]

    def test_the_hostile_row_names_the_lead(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(CombatExecutor, "_muster_reason",
                            lambda self, *a, **k: (False, "hostile_refuses"))
        nap, ney, mack = world.marshals["Napoleon"], world.marshals["Ney"], world.marshals["Mack"]
        rows = M.executor._combat._build_muster_preview(nap, mack, world, {"world": world})["rows"]
        assert rows and all(r["reason_display"] == "will not lift a finger for the Emperor Napoleon"
                            for r in rows), rows
        ney.location = nap.location
        world._build_marshal_index()
        rows = M.executor._combat._build_muster_preview(ney, mack, world, {"world": world})["rows"]
        assert rows and all(r["reason_display"] == "will not lift a finger for Marshal Ney"
                            for r in rows), rows
        monkeypatch.setattr(CE, "THE_MUSTER_NAMES_THE_LEAD", False)
        rows = M.executor._combat._build_muster_preview(ney, mack, world, {"world": world})["rows"]
        assert all(r["reason_display"] == MUSTER_REASON_DISPLAY["hostile_refuses"] for r in rows)


# ═══════════════════════════════════════════════════════════════════════════
# NPC-21 — a disabled option refuses with its reason
# ═══════════════════════════════════════════════════════════════════════════

class TestADisabledOptionRefusesWithItsReason:

    def _mount(self, world):
        dialogue = {
            "type": "proposal_confirm", "dialogue_type": "proposal_confirm",
            "dialogue_id": "npc21", "target_nation": "Austria",
            "proposal_type": "alliance",
            "options": [
                {"label": "Send as suggested", "action": "execute_proposal",
                 "enabled": False, "available": False,
                 "unavailable_reason": "I cannot deliver this, Sire — Prussia's war blocks it."},
                {"label": "Reconsider", "action": "reconsider"},
            ],
        }
        world.dialogue_manager.push(dialogue)
        return dialogue

    def test_the_typed_one_is_refused_in_place(self, shipped):
        client, world = shipped
        self._mount(world)
        r = M.executor._diplomatic.handle_diplomatic_dialogue_response("1", {"world": world})
        assert r.get("success") is False
        assert "'Send as suggested' is not open, Sire — I cannot deliver this" in r.get("message", ""), r
        assert (world.pending_diplomatic_dialogue or {}).get("dialogue_id") == "npc21"

    def test_a_live_option_still_answers(self, shipped):
        client, world = shipped
        self._mount(world)
        r = M.executor._diplomatic.handle_diplomatic_dialogue_response("2", {"world": world})
        assert "is not open" not in (r.get("message") or "")

    def test_lever_down_processes_the_dead_arm(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(DE, "A_DISABLED_OPTION_REFUSES_WITH_ITS_REASON", False)
        self._mount(world)
        r = M.executor._diplomatic.handle_diplomatic_dialogue_response("1", {"world": world})
        assert "is not open" not in (r.get("message") or "")


# ═══════════════════════════════════════════════════════════════════════════
# NPC-25 — the charge names its threshold
# ═══════════════════════════════════════════════════════════════════════════

class TestTheChargeNamesItsThreshold:

    def _stage(self, world):
        murat = world.marshals["Murat"]
        murat.location = "Lorraine"
        murat.recklessness = 0
        world._build_marshal_index()
        world.calculate_visibility()

    def test_one_victory(self, shipped):
        client, world = shipped
        self._stage(world)
        msg = post(client, "Murat, charge Mack").get("message", "")
        assert msg == ("Murat needs one victory first: a single battle won as the "
                       "attacker arms the charge (recklessness 0 of 1)."), msg

    def test_lever_down(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(CE, "THE_CHARGE_NAMES_ITS_THRESHOLD", False)
        self._stage(world)
        msg = post(client, "Murat, charge Mack").get("message", "")
        assert msg.startswith("Murat needs to build momentum first!"), msg


# ═══════════════════════════════════════════════════════════════════════════
# NP-X5 — the modding example validates; RS-28 — the dice are fixed
# ═══════════════════════════════════════════════════════════════════════════

class TestTheExampleValidates:

    def test_the_waterloo_example(self):
        from backend.modding.validator import validate_scenario
        path = REPO / "mods" / "examples" / "battle_of_waterloo.json"
        with _quiet():
            result = validate_scenario(str(path))
        assert not result.errors, result.errors
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["regions"]["Netherlands"]["controller"] == "Britain"
        assert data["regions"]["Berlin"]["controller"] == "Prussia"
        assert [n for n, r in data["regions"].items() if r.get("controller") == "Britain"
                and r.get("is_capital")] == ["Netherlands"]


class TestTheFumbleRollIsFixed:

    def test_the_fixture_pins_every_die(self):
        src = (REPO / "tests" / "test_napoleon_npv_review.py").read_text(encoding="utf-8")
        assert 'monkeypatch.setattr(_random, "randint"' in src
        # The cause: the 5% fumble on a sure arrival is the one live draw.
        ce = (REPO / "backend" / "commands" / "combat_executor.py").read_text(encoding="utf-8")
        assert "if random.randint(1, 20) == 1:  # 5% chance" in ce

    def test_the_colocated_emperor_takes_no_die(self, monkeypatch):
        """The row's own recipe tested: with the fumble die forced to 1 AND
        forced off, a co-located Emperor reaches the field both times — the
        die is not the mechanism, and the cause stays unisolated (twenty
        hash seeds pass standalone). The npv test now pins the aura's
        inputs before the attack so a recurrence names the leaked one."""
        from backend.game_logic.combat import CombatResolver
        from backend.models.marshal import Marshal
        from tests.test_napoleon_npv_review import (FIXED_DICE, attack, make_marshal,
                                                    make_sovereign, make_world)
        monkeypatch.setattr(CombatResolver, "roll_combat_dice",
                            lambda self, marshal, flanking_bonus=0: dict(FIXED_DICE))
        monkeypatch.setattr(_random, "uniform", lambda a, b: (a + b) / 2.0)
        monkeypatch.setattr(_random, "random", lambda: 0.5)
        real = Marshal.get_attack_modifier
        outcomes = {}
        for die in (1, 10):
            monkeypatch.setattr(_random, "randint", lambda a, b, _d=die: _d)
            nap = make_sovereign(location="Belgium")
            ney = make_marshal("Ney", location="Belgium", strength=40000, personality="aggressive")
            mack = make_marshal("Mack", location="Waterloo", strength=20000, nation="Austria")
            w = make_world(nap, ney, mack)
            seen = {}

            def spy(self, strength_ratio=None, consume=True, _seen=seen):
                if consume:
                    _seen.setdefault(self.name, getattr(self, "sovereign_presence", "ABSENT"))
                return real(self, strength_ratio, consume)
            monkeypatch.setattr(Marshal, "get_attack_modifier", spy)
            with _quiet():
                attack(w, "Ney", "Mack")
            outcomes[die] = seen.get("Ney")
        assert outcomes == {1: 1.0, 10: 1.0}, outcomes
