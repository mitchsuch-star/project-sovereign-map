"""Final Whole-Game Audit — slice 7, "The Mock Speaks Plainly" (FA-80, FA-N8,
FA-N24, FA-N9, FA-N39, FA-24 / FA-48 / NPC-7 / NPC-19, FA-47, FA-73, FA-D20,
FA-D25 — plus three mechanisms the reproduction found beside them).

Every row was reproduced on the 1805 boot through the real `/command` with a
MOCK parser before a line changed (Agent F's report + scratch probe_s7); the
pins below are that probe's rows, each with the lever-off arm where a lever
exists. Headlines the rows did not say:

* A typed honorific WALKED A PRISONER OUT OF VIENNA — "General Ney, attack
  Mack" with Ney captured moved him Vienna → Bohemia (the address guards
  never saw a token, so the roster scan bound him at strength 0).
* "withdraw Ney's rente" became a 2-AP MOVE_TO toward the phantom province
  "Ney'S Rente" — the strategic upgrade ran on an administrative verb.
* "Ney, fall back" was a MOVE_TO with a GENERIC target, which the resolver
  reads as the nearest ENEMY's province — a retreat plotted toward the guns.
* "will Ney attack Mack?" FOUGHT A BATTLE (gold −128, four corps to Swabia).

ONE design (REPRO_F §4): the naval verbs anchor to the fleet and refuse an
addressed marshal; ONE derived meta list; ONE honorific composed into every
address regex; plain synonyms + one transposition-aware verb repair; a
deterministic FACT desk behind `status`; a prisoner is named at every enemy
lookup; a dismissed marshal is not mourned as destroyed.
"""
import ast
import contextlib
import inspect
import io
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.ai.clause_guards as CG
import backend.ai.llm_client as L
import backend.ai.question_desk as QD
import backend.ai.strategic_parser as SP
import backend.commands.naval_executor as NE
import backend.commands.parser as PM
import backend.commands.prisoners as PR
import backend.main as M
from backend.ai.validation import (
    META_ACTIONS,
    NEVER_STRATEGIC_ACTIONS,
    NON_ORDER_ACTIONS,
    PARSER_ONLY_META,
)
from backend.commands.parser import CommandParser, _leading_addressed_token
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCENARIO = str(REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
               / "europe_1805.json")

LEVERS = [
    (L, "NAVAL_VERBS_NEED_THEIR_OBJECT"), (L, "PLAIN_SPEECH_ACTIVE"),
    (L, "SUPPORT_SPEAKS_PLAINLY"), (L, "VERB_TYPO_PASS_ACTIVE"),
    (L, "QUESTION_DESK_ACTIVE"), (L, "BERTHIER_NAMES_AN_ENEMY"),
    (CG, "MODAL_LEADS_ARE_QUESTIONS"), (QD, "QUESTION_DESK_ACTIVE"),
    (PM, "ADMIN_VERBS_NEVER_MARCH"), (PM, "A_BARE_RETREAT_IS_A_RETREAT"),
    (PM, "ADMIRAL_IS_AN_ADDRESSEE"), (SP, "GUARDING_A_MARSHAL_IS_SUPPORT"),
    (NE, "ADMIRALTY_REFUSES_AN_ADDRESSED_MARSHAL"), (PR, "PRISONERS_ARE_NAMED"),
    (M, "DISMISSAL_IS_NOT_A_DEATH"),
]

COMMAND_REFERENCE = "COMMAND REFERENCE"


@pytest.fixture(autouse=True)
def _levers_at_default():
    saved = [(mod, name, getattr(mod, name)) for mod, name in LEVERS]
    yield
    for mod, name, value in saved:
        setattr(mod, name, value)


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


@pytest.fixture
def board(monkeypatch):
    """The 1805 boot on the module-global seams /command reads, with a MOCK
    parser — never the live one (the .env key would be billed per test)."""
    with _quiet():
        world = WorldState.from_scenario(SCENARIO)
    parser = CommandParser(use_real_llm=False)
    assert parser.llm.use_real_api is False
    monkeypatch.setattr(M, "world", world)
    monkeypatch.setattr(M, "parser", parser)
    monkeypatch.setitem(M.game_state, "world", world)
    return world


@pytest.fixture
def client():
    return TestClient(M.app)


def post(client, text):
    with _quiet():
        return client.post("/command", json={"command": text}).json()


def parse(world, text):
    with _quiet():
        result = M.parser.parse(text, M.get_llm_game_state(), world=world)
    return result, (result.get("command") or {})


def capture(world, name, captor, where):
    marshal = world.marshals[name]
    marshal.captured_by = captor
    marshal.strength = 0
    marshal.location = where
    return marshal


def fleet(world):
    return dict(world.fleets["France"])


# ═══════════════════════════════════════════════════════════════════════════
# FA-N8 / FA-N24 / FA-N9 — the Admiralty names its object
# ═══════════════════════════════════════════════════════════════════════════

class TestTheAdmiraltyNamesItsObject:

    def test_a_pontoon_bridge_is_not_a_keel(self, board, client):
        """FA-N8: a bare `lay down` spent 400g and an admin AP on a keel."""
        before, gold = fleet(board)["ships"], int(board.gold)
        r = post(client, "Ney, lay down a pontoon bridge across the Danube")
        assert r["success"] is False
        assert fleet(board)["ships"] == before and int(board.gold) == gold
        _, c = parse(board, "lay down a pontoon bridge across the Danube")
        assert c.get("action") != "build_fleet"
        L.NAVAL_VERBS_NEED_THEIR_OBJECT = False
        _, c = parse(board, "lay down a pontoon bridge across the Danube")
        assert c.get("action") == "build_fleet", "lever off = the pre-slice reading"

    def test_lay_down_a_ship_lays_a_keel(self, board, client):
        """FA-N9: the help text's own example asked 'Did you mean Davout?'."""
        before, gold = fleet(board)["ships"], int(board.gold)
        r = post(client, "lay down a ship of the line")
        assert r["success"] is True and r.get("state") != "awaiting_clarification"
        assert fleet(board)["ships"] == before + 1
        assert int(board.gold) == gold - 400

    def test_draw_off_the_fleet_is_the_diversion(self, board):
        for text in ("draw off the fleet", "draw them off", "order the diversion",
                     "the grand diversion", "a diversion against the blockade"):
            r, c = parse(board, text)
            assert r["success"] and c.get("action") == "naval_diversion", text
            assert c.get("marshal") is None, text

    def test_a_land_diversion_is_not_the_grand_diversion(self, board, client):
        """FA-N24: 'Murat, mount a diversion on the left' opened the once-per-war
        Admiralty quote and discarded Murat."""
        r = post(client, "Murat, mount a diversion on the left")
        assert r["success"] is False and r.get("state") != "awaiting_clarification"
        assert board.dialogue_manager.peek() is None
        for text in ("Murat, mount a diversion on the left",
                     "Ney, create a diversion at Ulm"):
            _, c = parse(board, text)
            assert c.get("action") != "naval_diversion", text
        L.NAVAL_VERBS_NEED_THEIR_OBJECT = False
        _, c = parse(board, "Murat, mount a diversion on the left")
        assert c.get("action") == "naval_diversion", "lever off = the pre-slice reading"

    def test_an_addressed_marshal_is_refused_not_discarded(self, board, client):
        """FA-11's optional half, shared by all three marshal-free naval verbs:
        'Ney, lay down a ship' laid the keel and forgot Ney."""
        before = fleet(board)["ships"]
        r = post(client, "Ney, lay down a ship")
        assert r["success"] is False and "Admiralty" in r["message"]
        assert "Ney" in r["message"] and fleet(board)["ships"] == before
        r = post(client, "Murat, order the diversion")
        assert r["success"] is False and "Admiralty" in r["message"]
        NE.ADMIRALTY_REFUSES_AN_ADDRESSED_MARSHAL = False
        r = post(client, "Ney, lay down a ship")
        assert r["success"] is True and fleet(board)["ships"] == before + 1, \
            "lever off = the pre-slice discard"

    def test_villeneuve_may_order_the_diversion(self, board):
        """The fleet's own admiral is decoration on a naval verb, not a marshal
        typo — with the naval verbs in the meta list, the CR-2 address arm
        would otherwise ask 'which marshal?' of the Admiralty's own officer."""
        r, c = parse(board, "Villeneuve, order the diversion")
        assert r["success"] and c.get("action") == "naval_diversion"
        assert c.get("marshal") is None and not r.get("error")
        PM.ADMIRAL_IS_AN_ADDRESSEE = False
        r, c = parse(board, "Villeneuve, order the diversion")
        assert not (r["success"] and c.get("action") == "naval_diversion"
                    and c.get("marshal") is None and not r.get("error")), \
            "lever off = the CR-2 arm treats the admiral as an unbound name"

    def test_the_meta_list_is_derived(self):
        """FA-N9: ONE list. parser.py's `meta_actions` is no longer a literal,
        the three naval verbs are in it by construction, and the parser-only
        seven never collide with validation's own set."""
        tree = ast.parse((REPO / "backend" / "commands" / "parser.py").read_text(
            encoding="utf-8"))
        assigns = [node for node in ast.walk(tree) if isinstance(node, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == "meta_actions"
                           for t in node.targets)]
        assert assigns, "the meta arm still assigns `meta_actions`"
        for node in assigns:
            assert not isinstance(node.value, (ast.List, ast.Set, ast.Tuple)), \
                "meta_actions must be DERIVED from validation, not a literal"
        derived = META_ACTIONS | PARSER_ONLY_META
        for verb in ("build_fleet", "set_fleet_posture", "naval_diversion",
                     "help", "end_turn", "status", "unknown", "debug", "charge",
                     "restrain", "build", "repair", "economy", "meta_command",
                     "cheat", "recruit"):
            assert verb in derived, verb
        assert not (PARSER_ONLY_META & META_ACTIONS)
        assert NON_ORDER_ACTIONS <= NEVER_STRATEGIC_ACTIONS
        assert META_ACTIONS <= NEVER_STRATEGIC_ACTIONS
        assert PM._NON_ORDER_ACTIONS is NON_ORDER_ACTIONS

    def test_the_fallback_gate_reads_one_list(self):
        source = inspect.getsource(type(CommandParser(use_real_llm=False).llm)
                                   ._should_fallback_to_llm)
        assert 'meta_commands = {' not in source
        assert "NON_ORDER_ACTIONS" in source


# ═══════════════════════════════════════════════════════════════════════════
# FA-N39 — one honorific; FA-47 — a dismissal is not a death
# ═══════════════════════════════════════════════════════════════════════════

ADDRESS_FILES = (
    "backend/ai/llm_client.py", "backend/ai/clause_guards.py",
    "backend/commands/parser.py", "backend/commands/clarification.py",
    "backend/commands/context_carryover.py", "backend/commands/delegation.py",
    "backend/ai/strategic_parser.py",
)
FORBIDDEN_LITERALS = (
    "^\\s*(?:marshal\\s+)?", "^(?:marshal\\s+)", "(?:marshal|general)\\s+",
    "^(marshal\\s+)?",
)


class TestOneHonorific:

    def test_a_captured_marshal_is_refused_under_every_honorific(self, board, client):
        """Measured before the fix: 'General Ney, attack Mack' with Ney a
        prisoner MOVED him Vienna → Bohemia and reported a pursuit."""
        for honorific in ("General", "Gen.", "Maréchal", "Marshal", ""):
            capture(board, "Ney", "Austria", "Vienna")
            text = f"{honorific} Ney, attack Mack".strip()
            r = post(client, text)
            assert r["success"] is False, text
            assert "prisoner of Austria" in r["message"], text
            assert board.marshals["Ney"].location == "Vienna", text
            assert not r.get("battle_report"), text

    def test_a_fallen_marshal_is_mourned_under_every_honorific(self, board, client):
        with _quiet():
            board.destroy_marshal(board.marshals["Ney"], cause="test", victor="Austria")
        for text in ("General Ney, attack Mack", "Gen. Ney, attack Mack",
                     "Ney, attack Mack"):
            r = post(client, text)
            assert r["success"] is False and "lost to us" in r["message"], text
            assert not r.get("battle_report"), text

    def test_a_dismissed_marshal_is_not_mourned_as_destroyed(self, board, client):
        """FA-47: the tombstone carries the cause; the refusal ignored it."""
        with _quiet():
            board.destroy_marshal(board.marshals["Bernadotte"], cause="dismissed")
        r = post(client, "Bernadotte, attack Mack")
        assert r["success"] is False
        assert "relieved of command by your own order" in r["message"]
        assert "destroyed" not in r["message"]
        M.DISMISSAL_IS_NOT_A_DEATH = False
        r = post(client, "Bernadotte, attack Mack")
        assert "destroyed at" in r["message"], "lever off = the pre-slice line"

    def test_the_honorific_still_binds_a_living_marshal(self, board):
        for text, action in (("Gen. Ney, hold", "hold"),
                             ("General Ney, attack Mack", "attack"),
                             ("Maréchal Ney, scout Swabia", "scout")):
            r, c = parse(board, text)
            assert r["success"] and c.get("marshal") == "Ney", text
            assert c.get("action") == action, text

    def test_a_bare_rank_is_an_interjection(self, board):
        r, c = parse(board, "General, charge")
        assert r["success"] and c.get("action") == "charge"
        assert c.get("marshal") is None

    def test_the_addressed_token_helper(self):
        for text in ("Ney, attack", "Marshal Ney, attack", "General Ney, attack",
                     "Gen. Ney, attack", "Maréchal Ney, attack", "marechal Ney, attack"):
            assert _leading_addressed_token(text) == "Ney", text
        assert _leading_addressed_token("General, charge") is None
        assert _leading_addressed_token("attack Bern, then hold") is None

    def test_a_delegation_reads_the_honorific(self, board, client):
        """delegation.py's own address regex — CR-5's ASK arm must bind the
        addressee under a rank the way it binds him under 'Marshal'."""
        control = post(client, "Ney, deal with Mack")
        r = post(client, "General Ney, deal with Mack")
        assert r.get("state") == control.get("state"), (r.get("message"), control.get("message"))
        assert r["success"] == control["success"]
        assert "Unknown action" not in str(r.get("message"))

    def test_an_addressed_repeat_reads_the_honorific(self, board, client):
        """context_carryover.py's own address regex — 'General Ney, again'."""
        first = post(client, "Ney, scout Swabia")
        assert first["success"] and "scouts Swabia" in first["message"]
        again = post(client, "General Ney, again")
        assert again["success"] and "scouts Swabia" in again["message"], again.get("message")

    def test_the_census_no_address_regex_spells_marshal_alone(self):
        assert "general" in CG.HONORIFIC and "gen\\." in CG.HONORIFIC
        assert "mar[eé]chal" in CG.HONORIFIC
        for rel in ADDRESS_FILES:
            source = (REPO / rel).read_text(encoding="utf-8")
            for literal in FORBIDDEN_LITERALS:
                assert literal not in source, f"{rel} still spells the honorific by hand: {literal}"
            if rel != "backend/ai/clause_guards.py":
                assert "HONORIFIC" in source, rel


# ═══════════════════════════════════════════════════════════════════════════
# FA-24 / FA-48 / NPC-7 / NPC-19 — a prisoner is named
# ═══════════════════════════════════════════════════════════════════════════

class TestAPrisonerIsNamed:

    def test_attacking_our_prisoner_names_him(self, board, client):
        capture(board, "Mack", "France", "Paris")
        r = post(client, "Ney, attack Mack")
        assert r["success"] is False and "our prisoner at Paris" in r["message"]
        assert "La Mancha" not in r["message"] and "Did you mean" not in r["message"]
        assert board.marshals["Ney"].location == "Rhineland"

    def test_the_bare_attack_does_not_call_him_destroyed(self, board, client):
        capture(board, "Mack", "France", "Paris")
        r = post(client, "attack Mack")
        assert r["success"] is False and "our prisoner" in r["message"]
        assert "destroyed" not in r["message"]

    def test_pursuing_a_prisoner_is_refused_at_no_cost(self, board, client):
        capture(board, "Mack", "France", "Paris")
        ap = board.get_action_summary()
        r = post(client, "Ney, pursue Mack")
        assert r["success"] is False and "our prisoner" in r["message"]
        assert board.marshals["Ney"].location == "Rhineland"
        assert board.get_action_summary() == ap
        assert board.marshals["Ney"].strategic_order is None
        r = post(client, "pursue Mack")
        assert r["success"] is False and "our prisoner" in r["message"]
        PR.PRISONERS_ARE_NAMED = False
        r = post(client, "Ney, pursue Mack")
        assert r["success"] is True and board.marshals["Ney"].location != "Rhineland", \
            "lever off = the pre-slice 2-AP chase of a man in our own cells"

    def test_the_ai_path_names_him_too(self, board):
        """GR5: the same fuzzy seam serves the enemy AI (attacker_nation set)."""
        capture(board, "Mack", "France", "Paris")
        found, error = M.executor._fuzzy_match_enemy("Mack", board, "Prussia")
        assert found is None and error and error.get("prisoner") is True
        assert "prisoner of France" in error["message"]
        assert error.get("variable_action_cost") == 0

    def test_a_prisoner_of_another_court(self, board, client):
        """Re-targeted by the review round: Brunswick is ALSO a province (the
        WO-13 collision) and a captive's province namesake now means the
        province (R2-1); a captive held in a cell we can SEE is named (R2-2)."""
        capture(board, "ArchdukeJohn", "Prussia", "Swabia")  # Swabia is PARTIAL at boot
        r = post(client, "Ney, attack Archduke John")
        assert r["success"] is False and "prisoner of Prussia" in r["message"]
        assert not r.get("battle_report")


# ═══════════════════════════════════════════════════════════════════════════
# FA-80 — the mock speaks plainly
# ═══════════════════════════════════════════════════════════════════════════

PLAIN = [
    ("Ney, stay put", "wait", None, None),
    ("Ney, stay where you are", "wait", None, None),
    ("Ney, stay here", "wait", None, None),
    ("Ney, remain in Rhineland", "wait", None, None),
    ("Ney, rest your men", "wait", None, None),
    ("Ney, stand your ground", "hold", None, "HOLD"),
    ("Ney, advance on Swabia", "move", "Swabia", "MOVE_TO"),
    ("Ney, push on to Swabia", "move", "Swabia", "MOVE_TO"),
    ("Ney, onward to Swabia", "move", "Swabia", "MOVE_TO"),
    ("Ney, forward to Swabia", "move", "Swabia", "MOVE_TO"),
    ("Ney, pull back", "retreat", None, None),
    ("Ney, pull back to Lorraine", "move", "Lorraine", "MOVE_TO"),
    ("Ney, retire", "retreat", None, None),
    ("Ney, retire to Lorraine", "move", "Lorraine", "MOVE_TO"),
]

TYPOS = [
    ("Ney, attak Mack", "attack", "Mack", "attak"),
    ("Ney, atack Mack", "attack", "Mack", "atack"),
    ("Ney, attck Mack", "attack", "Mack", "attck"),
    ("Ney, mvoe to Lorraine", "move", "Lorraine", "mvoe"),
    ("Ney, scuot Swabia", "scout", "Swabia", "scuot"),
    ("Ney, hodl", "hold", None, "hodl"),
    ("Ney, retreta", "retreat", None, "retreta"),
]


class TestTheMockSpeaksPlainly:

    @pytest.mark.parametrize("text,action,target,strategic", PLAIN)
    def test_plain_wait_hold_move_retreat(self, board, text, action, target, strategic):
        r, c = parse(board, text)
        assert r["success"], (text, r.get("error"))
        assert c.get("marshal") == "Ney" and c.get("action") == action, (text, c)
        if target is not None:
            assert c.get("target") == target, (text, c)
        got = r.get("strategic_type") if r.get("is_strategic") else None
        assert got == strategic, (text, got)

    def test_plain_speech_lever(self, board):
        L.PLAIN_SPEECH_ACTIVE = False
        for text in ("Ney, stay put", "Ney, advance on Swabia", "Ney, pull back"):
            r, _ = parse(board, text)
            assert not r["success"], f"lever off = the pre-slice shrug for {text!r}"

    def test_a_bare_retreat_is_a_retreat(self, board):
        """Measured: 'Ney, fall back' → retreat + MOVE_TO generic → 'Mack blocks
        the path at Swabia' — a retreat plotted toward the nearest enemy."""
        for text in ("Ney, fall back", "Ney, withdraw"):
            r, c = parse(board, text)
            assert c.get("action") == "retreat" and not r.get("is_strategic"), text
        r, c = parse(board, "Ney, fall back to Lorraine")
        assert c.get("action") == "move" and r.get("strategic_type") == "MOVE_TO"
        assert c.get("target") == "Lorraine"
        PM.A_BARE_RETREAT_IS_A_RETREAT = False
        r, c = parse(board, "Ney, fall back")
        assert r.get("is_strategic") and r.get("strategic_type") == "MOVE_TO", \
            "lever off = the pre-slice generic march"
        assert c.get("target") == "generic"

    def test_an_administrative_verb_never_marches(self, board):
        """Measured: revoke_pension + the strategic table's bare 'withdraw' =
        a 2-AP MOVE_TO toward the phantom province \"Ney'S Rente\"."""
        r, c = parse(board, "withdraw Ney's rente")
        assert c.get("action") == "revoke_pension" and not r.get("is_strategic")
        PM.ADMIN_VERBS_NEVER_MARCH = False
        r, c = parse(board, "withdraw Ney's rente")
        assert r.get("is_strategic") and r.get("strategic_type") == "MOVE_TO", \
            "lever off = the pre-slice march"
        for verb in ("grant_pension", "revoke_pension", "grant_dotation",
                     "recruit_marshal", "recruit", "build", "repair", "garrison"):
            assert verb in NEVER_STRATEGIC_ACTIONS, verb
        for order in ("move", "attack", "hold", "retreat", "wait", "defend", "scout"):
            assert order not in NEVER_STRATEGIC_ACTIONS, order

    @pytest.mark.parametrize("text,action,target,typo", TYPOS)
    def test_a_verb_typo_is_repaired_once(self, board, text, action, target, typo):
        r, c = parse(board, text)
        assert r["success"] and c.get("action") == action, (text, r.get("error"))
        assert c.get("marshal") == "Ney"
        if target:
            assert c.get("target") == target
        assert f"read '{typo}' as '{action}'" in str(r.get("warning")), r.get("warning")

    def test_the_note_reaches_the_player(self, board, client):
        r = post(client, "Ney, mvoe to Lorraine")
        assert r["success"] and board.marshals["Ney"].location == "Lorraine"
        assert "read 'mvoe' as 'move'" in r["message"]

    def test_a_real_word_is_never_repaired(self, board):
        for text in ("Ney, dig a hole", "Ney, the hole is deep", "Ney, hole up here"):
            r, _ = parse(board, text)
            assert not r["success"], text

    def test_a_negated_typo_stays_a_refusal(self, board, client):
        """The typo pass reads the BLANKED text: a forbidden clause is gone
        before the repair runs, so 'do not attak Mack' refuses — while a typo
        beside a negated ASIDE is repaired to the order the player meant."""
        r, c = parse(board, "Ney, do not attak Mack")
        assert not r["success"] and c.get("action") != "attack"
        assert r.get("refusal")
        gold = int(board.gold)
        out = post(client, "Ney, do not attak Mack")
        assert out["success"] is False and not out.get("battle_report")
        assert int(board.gold) == gold
        # A NEGATED clause beside the typo ("do not pursue him" is blanked by
        # the guard) must not stop the repair of the order that survives it.
        for text in ("Ney, attak Mack, do not pursue him", "Ney, attak Mack, not Davout"):
            r, c = parse(board, text)
            assert r["success"] and c.get("action") == "attack", (text, r.get("error"))
            assert c.get("target") == "Mack" and "attak" in str(r.get("warning")), text

    def test_typo_lever(self, board):
        L.VERB_TYPO_PASS_ACTIVE = False
        r, _ = parse(board, "Ney, attak Mack")
        assert not r["success"], "lever off = the pre-slice shrug"

    def test_berthier_names_an_enemy_at_war(self, board, monkeypatch):
        """FA-80 (c): the shrug proposed attacking Deroy of Bavaria — a court
        France is at PEACE with (measured 2 of 12 shrugs)."""
        monkeypatch.setattr(L.random, "choice", lambda seq: seq[0])
        assert not board.is_at_war("France", "Bavaria")
        gs = M.get_llm_game_state()
        assert list(gs["enemies"])[0] == "Deroy"
        line = M.parser.llm._berthier_mock_response(
            "Ney, do the hokey cokey", gs, {"recognized_marshal": "Ney"})
        assert "Deroy" not in line and "attack Mack" in line, line
        L.BERTHIER_NAMES_AN_ENEMY = False
        line = M.parser.llm._berthier_mock_response(
            "Ney, do the hokey cokey", gs, {"recognized_marshal": "Ney"})
        assert "Deroy" in line, "lever off = the pre-slice enemies[0]"


# ═══════════════════════════════════════════════════════════════════════════
# FA-D20 — support speaks plainly
# ═══════════════════════════════════════════════════════════════════════════

SUPPORT = ["Ney, join Davout", "Ney, link up with Davout", "Ney, aid Davout",
           "Ney, assist Davout", "Ney, bolster Davout", "Ney, come to the aid of Davout",
           "Ney, help Davout", "Ney, go help Davout", "Ney, protect Davout",
           "Ney, guard Davout", "Ney, cover Davout", "Ney, screen Davout",
           "Ney, protect Marshal Davout"]


class TestSupportSpeaksPlainly:

    @pytest.mark.parametrize("text", SUPPORT)
    def test_support_synonyms(self, board, text):
        r, c = parse(board, text)
        assert r["success"], (text, r.get("error"))
        assert c.get("action") == "move", (text, c.get("action"))
        assert c.get("marshal") == "Ney" and c.get("target") == "Davout", (text, c)
        assert r.get("is_strategic") and r.get("strategic_type") == "SUPPORT", (text, r.get("strategic_type"))

    def test_a_province_keeps_hold(self, board):
        r, c = parse(board, "Ney, protect Rhineland")
        assert c.get("action") == "hold" and r.get("strategic_type") == "HOLD"
        assert c.get("target") == "Rhineland"

    def test_cover_the_retreat_stays_unknown(self, board):
        r, _ = parse(board, "Ney, cover the retreat")
        assert not r["success"] and "Unknown action" in str(r.get("error"))

    def test_an_attack_is_not_hijacked_by_a_plain_word(self, board):
        for text in ("Ney, attack Mack and cover the retreat", "Ney, attack Mack, I need help"):
            r, c = parse(board, text)
            assert c.get("action") == "attack" and c.get("target") == "Mack", text
            assert not r.get("is_strategic"), text

    def test_support_lever(self, board):
        L.SUPPORT_SPEAKS_PLAINLY = False
        r, _ = parse(board, "Ney, join Davout")
        assert not r["success"], "lever off = the pre-slice shrug"
        r, c = parse(board, "Ney, protect Davout")
        assert c.get("action") == "hold", "lever off = the hold family claims it"

    def test_guarding_lever(self, board):
        SP.GUARDING_A_MARSHAL_IS_SUPPORT = False
        r, c = parse(board, "Ney, protect Davout")
        assert r.get("strategic_type") == "HOLD" and c.get("target") == "Davout", \
            "lever off = the pre-slice HOLD 'at' a man"


# ═══════════════════════════════════════════════════════════════════════════
# FA-D25 — the question desk
# ═══════════════════════════════════════════════════════════════════════════

class TestTheQuestionDesk:

    def test_where_is_an_enemy_reads_the_intel(self, board, client):
        ap = board.get_action_summary()
        r = post(client, "where is Mack?")
        assert r["success"] and COMMAND_REFERENCE not in r["message"]
        assert "INTELLIGENCE REPORT" not in r["message"]
        assert "Mack" in r["message"] and "Swabia" in r["message"]
        # Swabia is PARTIAL at boot (adjacent to Rhineland): the band, not the count.
        assert "reported" in r["message"] and "52,000" not in r["message"]
        assert board.get_action_summary() == ap
        r = post(client, "where is Mack")
        assert "Swabia" in r["message"]

    def test_who_holds_a_province(self, board, client):
        r = post(client, "who holds Swabia?")
        assert "Swabia is held by Bavaria." in r["message"]
        r = post(client, "who holds Paris?")
        assert "Paris is ours" in r["message"]

    def test_who_is_at_a_province(self, board, client):
        r = post(client, "who is at Swabia?")
        assert "Mack" in r["message"] and COMMAND_REFERENCE not in r["message"]
        r = post(client, "who is at Rhineland?")
        assert "Ney" in r["message"] and "Davout" in r["message"]

    def test_what_is_a_marshal_doing(self, board, client):
        r = post(client, "what is Davout doing?")
        assert "Davout" in r["message"] and "Rhineland" in r["message"]
        assert COMMAND_REFERENCE not in r["message"]
        order = post(client, "Davout, hold Rhineland")
        assert order["success"], order.get("message")
        r = post(client, "what is Davout doing?")
        assert "hold" in r["message"].lower() and "Rhineland" in r["message"]

    def test_how_many_men(self, board, client):
        r = post(client, "how many men does Ney have?")
        assert "24,000" in r["message"] and "Ney" in r["message"]
        r = post(client, "how many men does Mack have?")
        assert "Mack" in r["message"] and "52,000" not in r["message"]

    def test_an_unseen_enemy_gets_no_word(self, board, client):
        """Fog-honest: an enemy in an UNKNOWN province is answered by name
        without his position — and never sent to the manual for being unseen."""
        from backend.models.intel import UNKNOWN
        hidden = next(m for m in board.get_enemy_marshals()
                      if m.strength > 0 and not getattr(m, "captured_by", "")
                      and board.get_region_intel(m.location).visibility == UNKNOWN)
        r = post(client, f"where is {hidden.name}?")
        assert COMMAND_REFERENCE not in r["message"], r["message"][:120]
        assert hidden.location not in r["message"]
        assert "no word" in r["message"].lower() or "last reported" in r["message"].lower()

    def test_an_addressed_question_is_answered(self, board, client):
        for text in ("Ney, where is Mack?", "General Ney, where is Mack?",
                     "Berthier, where is Mack?"):
            r = post(client, text)
            assert "Swabia" in r["message"] and COMMAND_REFERENCE not in r["message"], text

    def test_guidance_and_feasibility_keep_the_command_reference(self, board, client):
        for text in ("how do I attack?", "can I attack Mack?", "should Ney attack Mack?",
                     "how do I attack Mack?"):
            r = post(client, text)
            assert COMMAND_REFERENCE in r["message"], text
            assert not r.get("battle_report"), text

    def test_will_ney_attack_mack_is_a_question(self, board, client):
        """Measured: this sentence FOUGHT A BATTLE — gold −128, four corps
        marched to Swabia."""
        gold = int(board.gold)
        r = post(client, "will Ney attack Mack?")
        assert not r.get("battle_report") and int(board.gold) == gold
        assert board.marshals["Ney"].location == "Rhineland"
        assert CG.is_question("will Ney attack Mack?")
        assert CG.is_question("would Ney beat Mack?")
        CG.MODAL_LEADS_ARE_QUESTIONS = False
        assert not CG.is_question("will Ney attack Mack?"), "lever off = the pre-slice lead set"

    def test_the_polite_order_stays_an_order(self):
        """Recorded, not changed: an unpunctuated modal lead is a polite ORDER
        ('would you have Ney attack Mack', 'can Ney attack Mack')."""
        assert not CG.is_question("would you have Ney attack Mack")
        assert not CG.is_question("can Ney attack Mack")
        assert CG.is_question("can Ney attack Mack?")

    def test_the_desk_lever(self, board, client):
        QD.QUESTION_DESK_ACTIVE = False
        r = post(client, "where is Mack?")
        assert COMMAND_REFERENCE in r["message"], "lever off = the pre-slice help route"

    def test_berthier_is_the_desk(self, board, client):
        r = post(client, "Berthier, status")
        assert r["success"] and "INTELLIGENCE REPORT" in r["message"]
        assert "not found" not in r["message"]

    def test_classify_is_pure_and_does_not_guess(self):
        assert QD.classify_question("where is Mack?", ["Ney"], ["Mack"], ["Swabia"]) == {
            "kind": "where", "subject": "Mack", "subject_type": "enemy"}
        assert QD.classify_question("who holds Swabia?", ["Ney"], ["Mack"], ["Swabia"]) == {
            "kind": "who_holds", "subject": "Swabia", "subject_type": "region"}
        assert QD.classify_question("where is Blucher?", ["Ney"], ["Mack"], ["Swabia"]) is None
        assert QD.classify_question("how do I attack?", ["Ney"], ["Mack"], ["Swabia"]) is None
        assert QD.classify_question("where is the archduke?", ["Ney"],
                                    ["ArchdukeCharles", "ArchdukeJohn"], []) is None
        # Two names in one phrase: the desk does not pick the first.
        assert QD.classify_question("where is Ney and Davout?",
                                    ["Ney", "Davout"], [], []) is None
        assert QD.classify_question("where is Archduke Charles?", ["Ney"],
                                    ["ArchdukeCharles", "ArchdukeJohn"], []) == {
            "kind": "where", "subject": "ArchdukeCharles", "subject_type": "enemy"}


# ═══════════════════════════════════════════════════════════════════════════
# THE REVIEW ROUND (three lenses at 764d0ffc) — every finding pinned on its
# own sentence, each measured on the patched tree before the pin was written
# ═══════════════════════════════════════════════════════════════════════════

def _unknown_region(world):
    from backend.models.intel import UNKNOWN
    return next(r for r in world.regions
                if world.get_region_intel(r).visibility == UNKNOWN)


class TestTheReviewRound:

    # ── R1-1 (P1): the repair is a PRE-PARSE rewrite every reader sees ────
    def test_a_repaired_verb_is_read_by_every_reader(self, board, client):
        r, c = parse(board, "Davout, hodl Lorraine")
        assert c.get("action") == "hold" and c.get("target") == "Lorraine"
        assert r.get("is_strategic") and r.get("strategic_type") == "HOLD"
        assert "read 'hodl' as 'hold'" in str(r.get("warning"))
        assert c.get("raw_command") == "Davout, hodl Lorraine"
        ap = board.get_action_summary()
        out = post(client, "Davout, hodl Lorraine")
        assert out["success"], out.get("message")
        order = board.marshals["Davout"].strategic_order
        assert order is not None and order.command_type == "HOLD"
        assert order.target == "Lorraine"
        assert board.get_action_summary() != ap, "a standing order is charged"
        # the sequential split reads the repaired first clause too
        r, c = parse(board, "Ney, hodl Lorraine, then attack Mack")
        assert c.get("action") == "hold" and r.get("strategic_type") == "HOLD"
        assert "One order at a time" in str(r.get("warning"))
        gold = int(board.gold)
        out = post(client, "Ney, hodl Lorraine, then attack Mack")
        assert not out.get("battle_report") and int(board.gold) == gold
        # and the `and <verb>` split
        r, c = parse(board, "Ney, attak Mack and hold Rhineland")
        assert c.get("action") == "attack" and c.get("target") == "Mack"
        assert "One order at a time" in str(r.get("warning"))

    # ── R1-2 (P1): the split gate knows the wait vocabulary ────────────────
    def test_the_split_gate_knows_the_wait_vocabulary(self, board, client):
        for text, action in (("Ney, stay here, then attack Mack", "wait"),
                             ("Ney, rest your men, then attack Mack", "wait"),
                             ("Ney, stay where you are, then attack Mack", "wait"),
                             ("Ney, stand your ground, then attack Mack", "hold")):
            r, c = parse(board, text)
            assert c.get("action") == action, (text, c.get("action"))
            assert "One order at a time" in str(r.get("warning")), text
        gold = int(board.gold)
        out = post(client, "Ney, stay here, then attack Mack")
        assert not out.get("battle_report") and int(board.gold) == gold
        assert board.marshals["Ney"].location == "Rhineland"

    # ── R1-3 (P2): a real word is never repaired; only verb position counts
    def test_a_real_word_in_verb_position_is_not_repaired(self, board):
        for text in ("Davout, the line held", "Davout, we depend on you",
                     "Ney, spout off", "Ney, held the bridge",
                     "Davout, the line is hodl", "Ney, our scuot returned",
                     "Ney, snout"):
            r, _ = parse(board, text)
            assert not r["success"], text

    # ── R1-4 / R3-1 (P2): stay-put yields to every order verb ─────────────
    def test_stay_put_yields_to_the_order_verbs(self, board):
        for text, action, target in (("Davout, remain at Rhineland and fortify", "fortify", None),
                                     ("Ney, remain neutral", "stance_change", None),
                                     ("Davout, scout Swabia and remain there", "scout", "Swabia"),
                                     ("Ney, move to Lorraine and remain there", "move", "Lorraine"),
                                     ("Ney, stay put", "wait", None)):
            r, c = parse(board, text)
            assert r["success"] and c.get("action") == action, (text, c.get("action"), r.get("error"))
            if target:
                assert c.get("target") == target, text

    # ── R1-5 / R1-14 / R3-8: retire is terminal; towards is a destination ─
    def test_retire_is_terminal_and_towards_is_a_destination(self, board):
        for text in ("retire Ney", "Ney, retire the guns", "retire Ney from service"):
            r, _ = parse(board, text)
            assert not r["success"], text
        r, c = parse(board, "Ney, retire")
        assert c.get("action") == "retreat"
        for text, target in (("Ney, retire towards Alsace", "Alsace"),
                             ("Ney, pull back towards Lorraine", "Lorraine"),
                             ("Ney, fall back towards Lorraine", "Lorraine"),
                             ("Ney, withdraw towards Lorraine", "Lorraine")):
            r, c = parse(board, text)
            assert c.get("action") == "move" and c.get("target") == target, (text, c)
            assert r.get("strategic_type") == "MOVE_TO", text

    # ── R1-6 / R1-15 / R3-7 (P2): a marshal at the head of the object ─────
    def test_a_marshal_at_the_head_of_the_object_is_the_object(self, board):
        for text, marshal, ally in (("Ney, help Davout attack Mack", "Ney", "Davout"),
                                    ("Ney, join Davout at Lorraine", "Ney", "Davout"),
                                    ("Ney, protect Davout's flank", "Ney", "Davout"),
                                    ("Ney, guard Davout's flank", "Ney", "Davout"),
                                    ("Davout, cover Ney's retreat", "Davout", "Ney"),
                                    ("Ney, protect Marshal Davout's corps", "Ney", "Davout")):
            r, c = parse(board, text)
            assert r["success"], (text, r.get("error"))
            assert c.get("marshal") == marshal and c.get("target") == ally, (text, c)
            assert r.get("strategic_type") == "SUPPORT", (text, r.get("strategic_type"))

    # ── R1-7 (P2): the helped man is the supportee, never the executor ────
    def test_the_helped_man_is_the_supportee(self, board):
        for text in ("help Davout", "go help Davout", "cover Davout", "screen Davout",
                     "shield Davout"):
            r, c = parse(board, text)
            assert c.get("marshal") is None and c.get("target") == "Davout", (text, c)
            assert r.get("strategic_type") == "SUPPORT", text

    # ── R1-8 / R2-9 (P2): a modal lead reads its SUBJECT, not its punctuation
    def test_a_modal_lead_reads_the_subject(self, board):
        for text, action in (("Davout, would you march to Lorraine for me", "move"),
                             ("Ney, would you scout Swabia?", "scout"),
                             ("Ney, will you hold the line for me", "hold"),
                             ("Ney, would you attack Mack, I want Swabia", "attack")):
            r, c = parse(board, text)
            assert r["success"] and c.get("action") == action, (text, c.get("action"))
        for text in ("would Ney attack Mack", "Will Ney attack Mack", "shall we attack Mack",
                     "would Davout hold?", "will Ney attack Mack?"):
            r, c = parse(board, text)
            assert c.get("action") != "attack", text
            assert CG.is_question(text), text
        for text in ("would you have Ney attack Mack", "will you hold the line for me",
                     "Ney, would you scout Swabia?"):
            assert not CG.is_question(text), text

    # ── R1-9 (P3): longest first in the march table ────────────────────────
    def test_longest_first_in_the_march_table(self, board):
        for text, target in (("Ney, push on towards Paris", "Paris"),
                             ("Ney, push on toward Lorraine", "Lorraine"),
                             ("Ney, push on to Lorraine", "Lorraine")):
            r, c = parse(board, text)
            assert c.get("target") == target and r.get("strategic_type") == "MOVE_TO", (text, c)

    # ── R3-8: "forward to" only where an order stands ──────────────────────
    def test_forward_to_only_where_an_order_stands(self, board):
        r, _ = parse(board, "send the wounded forward to Paris")
        assert not r["success"]
        r, c = parse(board, "Ney, forward to Lorraine")
        assert c.get("action") == "move" and c.get("target") == "Lorraine"

    # ── R1-10 / R3-6 (P3): the note reaches a refusal ──────────────────────
    def test_the_note_reaches_a_refusal(self, board, client):
        out = post(client, "Ney, atack Lorraine")
        assert out["success"] is False
        assert "read 'atack' as 'attack'" in out["message"]

    # ── R1-11 (P3): the record keeps the typed text ────────────────────────
    def test_the_record_keeps_the_typed_text(self, board, client):
        r, c = parse(board, "Ney, mrach to Paris")
        assert c.get("action") == "move" and c.get("raw_command") == "Ney, mrach to Paris"
        assert r.get("raw_input") == "Ney, mrach to Paris"
        out = post(client, "Ney, mrach to Paris")
        assert out["success"], out.get("message")
        order = board.marshals["Ney"].strategic_order
        assert order is not None
        assert getattr(order, "original_command", "") == "Ney, mrach to Paris"

    # ── R1-16 (P4): the admiral is known to the confidence demotion ────────
    def test_the_admiral_is_known_to_the_confidence_gate(self, board):
        r, c = parse(board, "Villeneuve, order the diversion")
        assert c.get("action") == "naval_diversion"
        assert float(c.get("confidence") or 0) >= 0.7, c.get("confidence")

    # ── R2-1 (P2): a captive whose name is a province means the province ──
    def test_a_captive_namesake_is_the_province(self, board, client):
        capture(board, "Brunswick", "France", "Paris")
        assert "Brunswick" in board.regions
        out = post(client, "Ney, attack Brunswick")
        assert "prisoner" not in out["message"].lower(), out["message"]
        assert "destroyed" not in out["message"].lower()
        out = post(client, "attack Brunswick")
        assert "prisoner" not in out["message"].lower() and "destroyed" not in out["message"].lower()
        # the AI path (GR5): the fuzzy seam lets the province through too
        found, error = M.executor._fuzzy_match_enemy("Brunswick", board, "Austria")
        assert not (error or {}).get("prisoner")
        PR.PRISONERS_ARE_NAMED = False
        out = post(client, "Ney, attack Brunswick")
        assert "prisoner" not in out["message"].lower(), "the lever changes nothing for a province"

    # ── R2-2 (P2): a far court's captive is fogged; a seen one is named ────
    def test_a_far_courts_captive_is_fogged(self, board, client):
        cell = _unknown_region(board)
        capture(board, "Kutuzov", "Prussia", cell)
        for text in ("Ney, attack Kutuzov", "Ney, pursue Kutuzov", "attack Kutuzov"):
            out = post(client, text)
            assert out["success"] is False, text
            assert "Prussia" not in out["message"] and cell not in out["message"], (text, out["message"])
            assert "No intelligence" in out["message"], (text, out["message"])
        out = post(client, "where is Kutuzov?")
        assert "Prussia" not in out["message"] and cell not in out["message"]
        assert "no word" in out["message"].lower()
        # a captive held in a cell we can see IS named
        capture(board, "ArchdukeJohn", "Prussia", "Swabia")
        out = post(client, "Ney, attack Archduke John")
        assert "prisoner of Prussia" in out["message"]
        PR.PRISONERS_ARE_NAMED = False
        out = post(client, "Ney, attack Kutuzov")
        assert "Prussia" not in out["message"], "the lever restores the pre-slice shrug, not a leak"

    def test_a_fogged_tombstone_is_not_read_out(self, board, client):
        cell = _unknown_region(board)
        board.marshals["Kutuzov"].location = cell
        with _quiet():
            board.destroy_marshal(board.marshals["Kutuzov"], cause="test", victor="Prussia")
        out = post(client, "where is Kutuzov?")
        assert cell not in out["message"] and "destroyed" not in out["message"].lower()
        out = post(client, "attack Kutuzov")
        assert cell not in out["message"]

    # ── R2-3 (P2): no objection about an order the seam refuses ───────────
    def test_no_objection_about_a_prisoner(self, board, client):
        capture(board, "Mack", "France", "Paris")
        trust = board.marshals["Davout"].trust.value
        out = post(client, "Davout, attack Mack")
        assert out.get("state") != "awaiting_player_choice"
        assert "our prisoner" in out["message"]
        assert board.marshals["Davout"].trust.value == trust
        assert board.pending_objection is None

    # ── R2-4 (P2): an ally in full view is answered ────────────────────────
    def test_an_ally_in_view_is_answered(self, board, client):
        assert not board.is_at_war("France", "Bavaria")
        out = post(client, "where is Deroy?")
        assert "Franconia" in out["message"] and "22,000" in out["message"]
        assert "no word" not in out["message"].lower()

    # ── R2-5 (P2): SUPPORT of a captive is refused ─────────────────────────
    def test_support_of_a_captive_is_refused(self, board, client):
        capture(board, "Ney", "Austria", "Vienna")
        ap = board.get_action_summary()
        out = post(client, "Davout, support Ney")
        assert out["success"] is False and "prisoner of Austria" in out["message"]
        assert board.marshals["Davout"].strategic_order is None
        assert board.get_action_summary() == ap

    # ── R2-6 / R2-7 (P3): the man's own band; no tactical states abroad ────
    def test_the_desk_reports_the_mans_own_band_and_no_states(self, board, client):
        board.marshals["ArchdukeJohn"].location = "Swabia"  # beside Mack, PARTIAL
        out = post(client, "how many men does Archduke John have?")
        assert "substantial force" in out["message"], out["message"]
        assert "massive" not in out["message"] and "large force" not in out["message"]
        board.marshals["Deroy"].fortified = True
        out = post(client, "where is Deroy?")
        assert "fortified" not in out["message"].lower()
        out = post(client, "what is Deroy doing?")
        assert "fortified" not in out["message"].lower() and "Franconia" in out["message"]

    # ── R2-8 (P3): the charge, the scout and the move name a prisoner ─────
    def test_the_charge_scout_and_move_name_a_prisoner(self, board, client):
        capture(board, "Mack", "France", "Paris")
        murat = board.marshals["Murat"]
        murat.recklessness = 5
        out = post(client, "Murat, charge Mack")
        assert "our prisoner" in out["message"], out["message"]
        for text in ("Ney, scout Mack", "Ney, move to Mack"):
            out = post(client, text)
            assert "our prisoner" in out["message"], (text, out["message"])
            assert "La Mancha" not in out["message"]
        out = post(client, "Ney, scout Kutuzov")
        assert "is a commander" in out["message"]
        assert board.marshals["Kutuzov"].location not in out["message"]

    # ── R1-12 / R3-3 (P3): who holds prefers the province ─────────────────
    def test_who_holds_prefers_the_province(self, board, client):
        out = post(client, "who holds Brunswick?")
        assert "is held by" in out["message"] and "whereabouts" not in out["message"]
        out = post(client, "who is at Brunswick?")
        assert "Brunswick" in out["message"] and "whereabouts" not in out["message"]
        out = post(client, "who holds Hanover?")
        assert "its own crown" in out["message"]

    # ── R2-11 (P4): no band at LAST_KNOWN ─────────────────────────────────
    def test_no_band_at_last_known(self, board, client):
        from backend.models.intel import LAST_KNOWN
        intel = board.get_region_intel("Swabia")
        intel.visibility = LAST_KNOWN
        intel.known_marshals = ["Mack"]
        intel.strength_band = "large force"
        intel.last_updated_turn = board.current_turn - 6
        out = post(client, "who is at Swabia?")
        assert "Mack" in out["message"] and "large force" not in out["message"]

    # ── R2-13 (P4): one Admiralty predicate ───────────────────────────────
    def test_one_admiralty_predicate(self, board):
        refusal = NE._admiralty_misaddressed({"marshal": "Mack"}, board, "France",
                                             "lay down a ship")
        assert refusal is not None and "Admiralty" in refusal["message"]

    # ── R2-14 (P4): a classified question never dumps the reference ───────
    def test_a_classified_question_never_dumps_the_reference(self, board):
        result = M.executor._meta._execute_status(
            {"action": "status",
             "question": {"kind": "where", "subject": "Atlantis", "subject_type": "region"}},
            M.game_state)
        assert result["success"] and "I cannot say" in result["message"]
        assert "INTELLIGENCE REPORT" not in result["message"]

    # ── R3-14: the SUPPORT objection speaks ───────────────────────────────
    def test_the_support_objection_speaks(self, board):
        from backend.commands.objection_v2 import ConcernLevel
        line = M.executor._strategic._generate_objection_message(
            board.marshals["Ney"], "support", {}, ConcernLevel.MODERATE, "firm")
        assert "another man's guns" in line
        assert "I have concerns about this order" not in line
        line = M.executor._strategic._generate_objection_message(
            board.marshals["Davout"], "support", {}, ConcernLevel.MODERATE, "firm")
        assert "enemy country" in line

    # ── R2-12 (P4): the viewer's own captive is not a prisoner "target" ────
    def test_the_viewers_own_captive_is_not_a_target(self, board):
        capture(board, "Ney", "Austria", "Vienna")
        assert PR.prisoner_of(board, "Ney", viewer_nation="France") is None
        assert PR.prisoner_of(board, "Ney", viewer_nation="Prussia") is not None
