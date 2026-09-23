"""CX-R1 — "The unbound name spends nothing" (the Command-Road Queue, slice 2).

Build contract: `docs/audits/PARSER_AUTOFILL_ASSURANCE_2026_09_20.md` §3 (P1
"An unknown addressee spends gold and subjugates a great power") and §5 item
3; routing row CQ-2 in `docs/BUG_FIXES.md` §Command-Road Queue, which absorbs
L2-1 (the verb list 27 of 40 short) and the addressee family's other
state-mutating members (L2-2 `defend`, L2-3's epithet half, L2-4 filler).

Reproduced on this HEAD before a line was written (September 22, 2026),
fresh 1805 board per sentence, `POST /command`, mock mode, verdict by STATE
DELTA: ~30 forms mutated the world for a name nobody has —

    Zorglub build ships            gold 800 -> 400, a keel laid
    Zorglub recruit in Rhineland   gold 800 -> 59, Davout +3,000
    Zorglub vassalize Austria      AUSTRIA SUBJUGATED (and WITH the comma)
    Zorglub grant Holland more autonomy / release Holland / sponsor Prussia
    Zorglub crush Mack             a real battle (the L2-1 synonyms)
    Zorglub retire                 the whole army marched back, 0 AP
    Zorglub defend                 1 AP, the army defensive (L2-2)
    Zorglub just attack Mack       a real battle (L2-4)
    the Prince of Moskowa attack Mack   a real battle (L2-3, epithet half)

Two seams, both fixed here: the executor's gate guarded FA-22's marshal-less
FIELD family only, and the address locator measured the head against a
hand-written verb list. The gate now covers every order; the verb set is
GENERATED from the fast parser's own routing branches
(`tools/gen_routed_order_words.py`), and the census below re-derives it
from the live parser so the two cannot drift.

⚠ The golden corpus cannot see this defect by construction — it stops at
`CommandParser.parse`, and the gate lives in the executor. Every behaviour
pin here drives `POST /command` and asserts the state footprint.
"""

import copy
import re

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.ai import clause_guards as CG
from backend.ai.routed_order_words import ROUTED_ORDER_WORDS
from backend.commands.executor import CommandExecutor
from backend.commands.parser import CommandParser
from tools import gen_routed_order_words as GEN


# ═══════════════════════════════════════════════════════════════════════════
# Harness — a fresh SHIPPED 1805 board per sentence, verdict by state delta.
# ═══════════════════════════════════════════════════════════════════════════
@pytest.fixture
def board(monkeypatch):
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    assert M.parser.llm.use_real_api is False, "a probe must never pay"
    return TestClient(M.app)


def _snapshot(world):
    return {
        "gold": int(world.nation_gold.get(world.player_nation, 0)),
        "ap": (world.actions_remaining, world.admin_actions_remaining),
        "dp": world.diplomatic_points,
        "fleets": copy.deepcopy(world.fleets),
        "vassals": copy.deepcopy(world.vassals),
        "diplo": dict(world.diplomatic_states),
        "marshals": {n: (m.nation, m.location, int(m.strength),
                         bool(getattr(m, "fortified", False)),
                         str(getattr(m, "stance", None)),
                         bool(getattr(m, "strategic_order", None)),
                         getattr(m, "pension", 0),
                         tuple(getattr(m, "dotation_regions", []) or []))
                     for n, m in world.marshals.items()},
        "controllers": {n: r.controller for n, r in world.regions.items()},
        "dialogue": bool(world.dialogue_manager.peek()),
    }


def _drive(client, sentence):
    before = _snapshot(M.world)
    response = client.post("/command", json={"command": sentence}).json()
    after = _snapshot(M.world)
    changed = sorted(k for k in before if before[k] != after[k])
    return response, changed


def _refused(response):
    return (response.get("success") is False
            and response.get("kind") == "marshal_not_found")


_ROSTER = ["Ney", "Davout", "Soult", "Lannes", "Murat", "Bernadotte",
           "Massena", "Napoleon"]


# ═══════════════════════════════════════════════════════════════════════════
# (1) THE MEASURED MEMBERS — every one refused, nothing spent, nothing moved.
# ═══════════════════════════════════════════════════════════════════════════
STATE_ORDERS = [
    # the memo's four
    "Zorglub build ships",
    "Zorglub recruit in Rhineland",
    "Zorglub blockade",
    "Zorglub vassalize Austria",
    # the rest of the national verbs the census found mutating
    "Zorglub lay down a keel",
    "Zorglub subjugate Austria",
    "Zorglub make vassal of Austria",
    "Zorglub grant Holland more autonomy",
    "Zorglub release Holland",
    "Zorglub sponsor Prussia",
    "Zorglub guarantee Saxony",
    "Zorglub build a depot in Rhineland",
    "Zorglub build a fort in Paris",
    "Zorglub order the diversion",
    "Zorglub propose peace with Austria",
    "Zorglub declare war on Prussia",
    # the names the game itself prints, on an order of state
    "Grouchy build ships",
    "Marmont build ships",
]

COMMA_STATE_ORDERS = [
    # the parser's vassal/instrument early-return discarded the address, so
    # the COMMA did not save these — measured: Austria subjugated
    "Zorglub, vassalize Austria",
    "Zorglub, grant Holland more autonomy",
    "Zorglub, release Holland",
    "Zorglub, sponsor Prussia",
    "Zorglub, propose peace with Austria",
    "Zorglub, declare war on Prussia",
]

FIELD_ORDERS = [
    # L2-1: the verbs the hand list never learned
    "Zorglub crush Mack", "Zorglub smash Mack", "Zorglub destroy Mack",
    "Zorglub rout Mack", "Zorglub strike Mack", "Zorglub fight Mack",
    "Zorglub ambush Mack", "Zorglub occupy Swabia", "Zorglub capture Swabia",
    "Zorglub seize Swabia", "Zorglub intercept Mack", "Zorglub harry Mack",
    "Zorglub shadow Mack", "Zorglub retire", "Zorglub reconnaissance Swabia",
    "Zorglub reconnoitre Swabia",
    # L2-2: the sixth marshal-less type
    "Zorglub defend", "Wellington defend", "Berthier defend",
    # L2-4: filler after the name
    "Zorglub just attack Mack", "Zorglub now attack Mack",
    "Zorglub please attack Mack", "Zorglub you attack Mack",
    "Zorglub's corps attack Mack",
    # L2-3: the epithet
    "the Prince of Moskowa attack Mack", "Prince of Moskowa attack Mack",
    # names the game prints
    "Berthier crush Mack", "Grouchy crush Mack",
    # the comma that closes a clause, not an address
    "Zorglub attack Mack, then hold",
    # ... and the question mark does not hide it
    "Zorglub crush Mack?",
]


class TestTheUnboundNameSpendsNothing:

    @pytest.mark.parametrize("sentence", STATE_ORDERS + COMMA_STATE_ORDERS)
    def test_an_order_of_state(self, board, sentence):
        response, changed = _drive(board, sentence)
        assert _refused(response), (sentence, response.get("message"))
        assert changed == [], (sentence, changed)

    @pytest.mark.parametrize("sentence", FIELD_ORDERS)
    def test_a_field_order(self, board, sentence):
        response, changed = _drive(board, sentence)
        assert _refused(response), (sentence, response.get("message"))
        assert changed == [], (sentence, changed)

    def test_the_headline_at_the_digit(self, board):
        """The row's own figures: 800 gold stays 800, Austria stays Austrian."""
        world = M.world
        assert world.nation_gold["France"] == 800
        response, _ = _drive(board, "Zorglub build ships")
        assert _refused(response)
        assert world.nation_gold["France"] == 800
        response, _ = _drive(board, "Zorglub vassalize Austria")
        assert _refused(response)
        assert "Austria" not in world.vassals
        assert world.get_diplomatic_state("France", "Austria") == "WAR"

    def test_the_rewarded_man_is_not_the_addressee(self, board):
        """The rewards put the man REWARDED in the `marshal` slot, so a bound
        marshal proved nothing about the address and `Zorglub, grant Ney a
        rente` reached the grant arm."""
        for sentence in ("Zorglub, grant Ney a rente",
                         "Zorglub grant Ney a rente",
                         "Zorglub endow Ney with Rhineland"):
            response, changed = _drive(board, sentence)
            assert _refused(response), (sentence, response.get("message"))
            assert changed == [], (sentence, changed)


# ═══════════════════════════════════════════════════════════════════════════
# (2) THE CONTROLS — nothing here may start refusing.
# ═══════════════════════════════════════════════════════════════════════════
class TestTheControlsStillAct:

    @pytest.mark.parametrize("sentence,expected", [
        # bare orders of state
        ("build ships", {"gold", "ap", "fleets"}),
        ("blockade", {"ap", "fleets"}),
        ("recruit in Rhineland", {"gold", "ap", "marshals"}),
        # SENTENCE CASE: a capitalised verb is not a name. These are the
        # false refusals a derived set with nouns in it would have shipped.
        ("Build ships", {"gold", "ap", "fleets"}),
        ("Lay down a keel", {"gold", "ap", "fleets"}),
        ("Blockade Britain", {"ap", "fleets"}),
        ("Grant Holland more autonomy", {"dp", "vassals"}),
        ("Send the fleet to blockade Britain", {"ap", "fleets"}),
        ("Keep watch on Swabia", {"ap"}),
        ("Pull back", {"marshals"}),
        ("Retire", {"marshals"}),
        # the addressees the game knows
        ("Villeneuve blockade", {"ap", "fleets"}),
        ("Villeneuve, blockade", {"ap", "fleets"}),
        ("Berthier build ships", {"gold", "ap", "fleets"}),
    ])
    def test_it_still_acts(self, board, sentence, expected):
        response, changed = _drive(board, sentence)
        assert not _refused(response), (sentence, response.get("message"))
        assert expected <= set(changed), (sentence, changed)

    @pytest.mark.parametrize("sentence", [
        "Talleyrand, propose peace with Austria",   # the Cabinet stages terms
        "Order the diversion",                      # the Admiralty's quote
        "Fall back to Paris",                       # asks which marshal
    ])
    def test_it_still_asks(self, board, sentence):
        response, changed = _drive(board, sentence)
        assert not _refused(response), (sentence, response.get("message"))
        assert "dialogue" in changed, (sentence, changed)

    def test_our_own_marshal_still_acts(self, board):
        response, changed = _drive(board, "Ney attack Mack")
        assert not _refused(response), response.get("message")
        assert "ap" in changed and "marshals" in changed, changed

    def test_a_typo_the_parser_repaired_is_bound(self, board):
        """CX's own pin, carried: `Davoust attack Mack` goes to DAVOUT."""
        response, _ = _drive(board, "Davoust attack Mack")
        assert not _refused(response), response.get("message")
        assert "Davout" in (response.get("message") or ""), \
            response.get("message")

    @pytest.mark.parametrize("sentence", ["Zorglub economy", "Zorglub status"])
    def test_a_read_keeps_its_answer(self, board, sentence):
        """`NON_ORDER_ACTIONS` and a failed parse spend nothing by
        construction — they keep the answer they had."""
        response, changed = _drive(board, sentence)
        assert not _refused(response), (sentence, response.get("message"))
        assert changed == [], changed


# ═══════════════════════════════════════════════════════════════════════════
# (3) THE MIRROR — the same list was a false refusal the other way (L2-1 §6).
# ═══════════════════════════════════════════════════════════════════════════
class TestTheMirror:

    @pytest.mark.parametrize("sentence", [
        "crush Mack, then hold your positions",
        "occupy Swabia, then hold",
        "retire, then fortify",
        "pull back, then fortify",
        "recon Swabia, then fortify",
        "attack Bern, then hold your positions",   # FA-22's own pin
    ])
    def test_an_order_before_a_comma_names_nobody(self, sentence):
        assert CG.address_of(sentence, _ROSTER) is None, sentence

    def test_end_to_end(self, board):
        response, changed = _drive(board, "crush Mack, then hold your positions")
        assert not _refused(response), response.get("message")
        assert "ap" in changed, changed


# ═══════════════════════════════════════════════════════════════════════════
# (4) THE DERIVATION — the census that keeps the two in step.
# ═══════════════════════════════════════════════════════════════════════════
class TestTheVerbSetIsDerived:

    def test_the_generated_module_is_current(self):
        """Re-derive from the live parser: the committed module must be
        byte-identical. If this fails, the router's keywords changed —
        run `python -m tools.gen_routed_order_words`."""
        assert set(ROUTED_ORDER_WORDS) == GEN.harvest()
        assert GEN.TARGET_PATH.read_text(encoding="utf-8") == GEN.render(
            GEN.harvest())

    def test_a_new_router_keyword_joins_the_vocabulary(self):
        """The sensitivity arm: hand the harvest a router with one more
        branch and watch the vocabulary follow — and a word the branch
        requires ABSENT must not."""
        source = GEN.ROUTER_PATH.read_text(encoding="utf-8")
        marker = "        # ═══════ ADD NEW ACTION KEYWORDS HERE ═══════"
        assert marker in source
        mutated = source.replace(
            marker,
            "        elif \"zapfenstreich\" in command_lower and \"quietus\""
            " not in command_lower:\n            action = \"wait\"\n"
            + marker, 1)
        words = GEN.harvest(router_source=mutated)
        assert "zapfenstreich" in words
        assert "quietus" not in words
        assert "zapfenstreich" not in GEN.harvest()

    def test_a_local_name_shadows_a_module_keyword(self):
        """A router function's LOCAL is never read as the module constant of
        the same name — Python would not, and the harvest must not either.
        (The prototype read `_parse_diplomatic_command`'s local `is_question`
        flag as clause_guards' function of that name and pulled a docstring's
        worth of prose into the vocabulary.)"""
        source = GEN.ROUTER_PATH.read_text(encoding="utf-8")
        marker = "        # ═══════ ADD NEW ACTION KEYWORDS HERE ═══════"
        module_level = "\n_ZAPFEN_WORDS = (\"zapfenstreich\",)\n"
        mutated = source.replace(
            "DIPLOMAT_ADDRESS_NAMES = (",
            module_level + "DIPLOMAT_ADDRESS_NAMES = (", 1)
        mutated = mutated.replace(
            marker,
            "        elif any(w in command_lower for w in _ZAPFEN_WORDS):\n"
            "            action = \"wait\"\n" + marker, 1)
        assert "zapfenstreich" in GEN.harvest(router_source=mutated), \
            "the module constant is followed when nothing shadows it"
        shadowed = mutated.replace(
            "    def _parse_with_mock_chain(self, command_text: str, "
            "game_state: Optional[Dict] = None) -> ParseResult:\n",
            "    def _parse_with_mock_chain(self, command_text: str, "
            "game_state: Optional[Dict] = None) -> ParseResult:\n"
            "        _ZAPFEN_WORDS = (\"tattoo\",)\n", 1)
        assert shadowed != mutated
        assert "zapfenstreich" not in GEN.harvest(router_source=shadowed)

    @pytest.mark.parametrize("pattern,words", [
        (r"\b(pursue|chase|hunt)\b", ["pursue", "chase", "hunt"]),
        (r"\bobserv(?:e|es|ing)\b", ["observe", "observes", "observing"]),
        (r"\b(sponsor|subsidi[sz]e)\b", ["sponsor", "subsidise", "subsidize"]),
        (r"\bsubstitutes?\b", ["substitutes", "substitute"]),
        (r"\b(build|raise)\b.{0,20}\b(ship|fleet)\b", ["build", "raise"]),
        (r"\bstay\s+put\b|\bremain\b", ["stay", "remain"]),
        # an OPTIONAL leading group: the branch can open with what follows it
        (r"(?:please\s+)?charge\b", ["please", "charge"]),
        (r"(?=attack)hold", ["hold"]),     # a lookahead asserts, never routes
    ])
    def test_the_regex_reader(self, pattern, words):
        """The harvest reads a keyword regex for the words it OPENS with."""
        assert GEN._leading_words(pattern) == words

    def test_the_routed_verbs_of_row_l2_1_are_all_there(self):
        """The CX-7 review's 27, verb by verb (census 40/13/27)."""
        l21 = ["crush", "smash", "destroy", "annihilate", "obliterate", "rout",
               "strike", "defeat", "fight", "ambush", "occupy", "capture",
               "seize", "hunt", "hound", "intercept", "harry", "shadow",
               "pull", "retire", "recon", "reconnaissance", "observe", "keep",
               "shell", "barrage", "cannonade"]
        missing = [w for w in l21 if w not in ROUTED_ORDER_WORDS]
        assert missing == [], missing

    @pytest.mark.parametrize("word", sorted(ROUTED_ORDER_WORDS))
    def test_every_routed_word_opens_an_order(self, word):
        """What the census pins: every word the parser routes on ends the
        address in front of it."""
        assert CG.address_of(f"Zorglub {word} Swabia", _ROSTER) == "Zorglub"

    @pytest.mark.parametrize("word", [
        "sortie", "sally", "regroup", "probe", "levy", "watch"])
    def test_the_hand_list_words_the_harvest_dropped_route_nowhere(
            self, board, word):
        """The hand list carried words the parser does not route; a word
        the router cannot act on cannot spend anything."""
        parsed = M.parser.llm.fast_parse(f"{word} Swabia")
        assert parsed.action == "unknown", (word, parsed.action)

    def test_a_substring_keyword_still_reads_its_longer_forms(self, board):
        """`"recon" in command_lower` reads "reconnoitre" — the five-letter
        prefix rule keeps that reach, and no more: "blockading" drops the
        e, and the router's own `\\bblockade\\b` does not read it either."""
        for word in ("reconnoitre", "reconnoiter", "recruiting", "crushing"):
            assert CG.order_verb_re().search(word), word
        assert not CG.order_verb_re().search("blockading")
        assert M.parser.llm.fast_parse("blockading Britain").action \
            != "set_fleet_posture"

    def test_a_short_word_is_never_a_prefix(self):
        """"be" routes ("be aggressive") — as a prefix it would read
        Bernadotte and Berthier as orders."""
        assert "be" in ROUTED_ORDER_WORDS
        for name in ("Bernadotte", "Berthier", "Bessieres", "Godot"):
            assert not CG.order_verb_re().search(name), name

    def test_no_name_the_game_prints_is_an_order_word(self, board):
        """Every marshal on every roster, every bench candidate, every
        admiral and diplomat, and the epithets the game prints, is still a
        claimable name — the prefix rule swallows none of them."""
        from backend.display_names import humanize_entity_name
        world = M.world
        names = {humanize_entity_name(n) for n in world.marshals}
        for pool in world.marshal_pool.values():
            names.update(c.get("name") for c in pool if c.get("name"))
        for fleet in world.fleets.values():
            if fleet.get("admiral"):
                names.add(fleet["admiral"])
        names.update(getattr(d, "name", "") for d in world.diplomats.values())
        names.update(("Iron Marshal", "Bravest of the Brave",
                      "Prince of Moskowa", "Duke of Swabia"))
        names.discard("")
        swallowed = sorted(n for n in names if CG.order_verb_re().search(n))
        assert swallowed == [], swallowed

    def test_the_addressees_are_not_order_words(self):
        """The router routes on WHO is addressed too; those words name the
        addressee, never the order."""
        from backend.ai.llm_client import DIPLOMAT_ADDRESS_NAMES
        for phrase in DIPLOMAT_ADDRESS_NAMES + CG.DESK_ADDRESSEES:
            for word in phrase.split():
                assert word not in ROUTED_ORDER_WORDS, word


# ═══════════════════════════════════════════════════════════════════════════
# (5) THE LOCATOR — the name at the head of an unmarked address.
# ═══════════════════════════════════════════════════════════════════════════
class TestTheNameAtTheHead:

    @pytest.mark.parametrize("sentence,expected", [
        ("Zorglub just attack Mack", "Zorglub"),
        ("Zorglub please build ships", "Zorglub"),
        ("Zorglub's corps attack Mack", "Zorglub"),
        ("the Prince of Moskowa attack Mack", "Prince of Moskowa"),
        ("Prince of Moskowa attack Mack", "Prince of Moskowa"),
        ("the Iron Marshal attack Mack", "Iron Marshal"),
        ("Zorglub attack Mack, then hold", "Zorglub"),
        ("Nay attack Mack", "Nay"),
        ("Zorglub! attack Mack", "Zorglub"),       # the refusal names him bare
    ])
    def test_the_name_is_claimed(self, sentence, expected):
        assert CG.address_of(sentence, _ROSTER) == expected

    @pytest.mark.parametrize("sentence", [
        "quickly attack Mack", "can you attack Mack", "Ok retreat",
        "quickly and at once attack Mack", "cavalry attack Mack",
        "Marshal attack Mack", "zorglub attack mack",
        "Grant Holland more autonomy", "Send the fleet to blockade Britain",
    ])
    def test_grammar_at_the_head_names_nobody(self, sentence):
        assert CG.address_of(sentence, _ROSTER) is None, sentence

    def test_a_connective_lives_only_inside_a_name(self):
        assert CG.looks_like_an_address("Prince of Moskowa") is True
        assert CG.looks_like_an_address("Bravest of the Brave") is True
        assert CG.looks_like_an_address("of Moskowa") is False
        assert CG.looks_like_an_address("Alpha Beta Gamma Delta") is False

    @pytest.mark.parametrize("sentence,plain", [
        ("Zorglub build ships", "build ships"),
        ("Zorglub, vassalize Austria", "vassalize Austria"),
        ("Zorglub attack Mack, then hold", "attack Mack, then hold"),
        ("Zorglub: blockade", "blockade"),
    ])
    def test_the_order_after_the_address(self, sentence, plain):
        assert CG.order_after_address(sentence) == plain


# ═══════════════════════════════════════════════════════════════════════════
# (6) WHO TAKES WHICH ORDER, and the copy that says so.
# ═══════════════════════════════════════════════════════════════════════════
class TestTheAddressees:

    def _unbound(self, raw, action, command_type="specific", marshal=None):
        ex = CommandExecutor()
        cmd = {"type": command_type, "action": action, "raw_input": raw,
               "marshal": marshal}
        return ex._unbound_addressee(cmd, cmd, M.world)

    def test_the_desk_takes_an_order_of_state_not_a_field_order(self, board):
        assert self._unbound("Berthier build ships", "build_fleet") is None
        assert self._unbound("Berthier retreat", "retreat",
                             "general_retreat") == "Berthier"
        assert self._unbound("Berthier defend", "defend",
                             "general_defensive") == "Berthier"

    def test_the_foreign_minister_takes_his_cabinet(self, board):
        assert self._unbound("Talleyrand build ships",
                             "diplomatic_proposal", "diplomatic") is None

    def test_the_admiral_takes_the_fleet_and_nothing_else(self, board):
        assert self._unbound("Villeneuve blockade", "set_fleet_posture") is None
        assert self._unbound("Villeneuve recruit in Paris",
                             "recruit") == "Villeneuve"

    def test_the_rewarded_marshal_does_not_bind_the_address(self, board):
        assert self._unbound("Zorglub grant Ney a rente", "grant_pension",
                             marshal="Ney") == "Zorglub"
        assert self._unbound("grant Ney a rente", "grant_pension",
                             marshal="Ney") is None
        assert self._unbound("Davout, grant Ney a rente", "grant_pension",
                             marshal="Ney") is None

    def test_a_bound_marshal_on_an_order_stands(self, board):
        """The live parser may bind an epithet the rule cannot read ("the
        Bravest of the Brave" -> Ney); a bound marshal on an ORDER is
        trusted, exactly as before."""
        assert self._unbound("the Bravest of the Brave attack Mack", "attack",
                             marshal="Ney") is None

    def test_an_order_of_state_hands_the_order_back(self, board):
        response, _ = _drive(board, "Zorglub build ships")
        message = response.get("message") or ""
        assert "nothing was spent" in message, message
        assert "'build ships'" in message, message

    def test_an_order_a_marshal_carries_keeps_fa22s_question(self, board):
        for sentence in ("Zorglub fortify", "Zorglub crush Mack"):
            response, _ = _drive(board, sentence)
            assert response.get("message") == (
                "There is no 'Zorglub' in the order of battle, Sire. "
                "Whom did you intend?"), (sentence, response.get("message"))

    def test_the_client_still_forgets_the_line(self, board):
        """CX-7's forget rule reads `kind`; the refusal keeps it."""
        response, _ = _drive(board, "Zorglub vassalize Austria")
        assert response.get("kind") == "marshal_not_found"


# ═══════════════════════════════════════════════════════════════════════════
# (7) THE QUESTION GUARD reads the same rule (CXR1-1, one source).
# ═══════════════════════════════════════════════════════════════════════════
class TestTheQuestionGuardReadsTheSameRule:

    def test_a_routed_verb_with_a_question_mark_is_still_an_order(self):
        """`Ney crush Mack?` was swallowed as a question because "crush" was
        not on the list — the comma was not the difference, the verb was."""
        assert CG.is_question("Ney crush Mack?", _ROSTER) is False
        assert CG.is_question("Ney, crush Mack?", _ROSTER) is False

    def test_an_unaddressed_question_is_still_a_question(self):
        assert CG.is_question("crush Mack?", _ROSTER) is True


# ═══════════════════════════════════════════════════════════════════════════
# (8) THE LEVERS — each one down reproduces its own measured defect.
# ═══════════════════════════════════════════════════════════════════════════
class TestTheLevers:

    def test_the_gate_lever(self, board, monkeypatch):
        monkeypatch.setattr(CommandExecutor, "THE_UNBOUND_NAME_SPENDS_NOTHING",
                            False)
        response, changed = _drive(board, "Zorglub build ships")
        assert not _refused(response)
        assert M.world.nation_gold["France"] == 400, changed

    def test_the_derivation_lever(self, board, monkeypatch):
        monkeypatch.setattr(CG, "ORDER_WORDS_ARE_DERIVED", False)
        assert CG.address_of("Zorglub crush Mack", _ROSTER) is None
        response, changed = _drive(board, "Zorglub crush Mack")
        assert not _refused(response), response.get("message")
        assert "ap" in changed, changed

    def test_the_head_lever(self, monkeypatch):
        monkeypatch.setattr(CG, "THE_ADDRESS_IS_ITS_HEAD", False)
        assert CG.address_of("Zorglub just attack Mack", _ROSTER) is None
        assert CG.address_of("the Prince of Moskowa attack Mack",
                             _ROSTER) is None
        assert CG.address_of("Zorglub attack Mack, then hold",
                             _ROSTER) is None

    def test_the_levers_are_up(self):
        assert CommandExecutor.THE_UNBOUND_NAME_SPENDS_NOTHING is True
        assert CG.ORDER_WORDS_ARE_DERIVED is True
        assert CG.THE_ADDRESS_IS_ITS_HEAD is True
