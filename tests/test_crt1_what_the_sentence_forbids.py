"""CRT-1 — "What the sentence forbids is never the order" (the CR-6 triage,
slice 1; build contract = `docs/COMMAND_ROBUSTNESS_SPEC.md` §12.3, rows
CQ-32 / CQ-34 / CQ-35 / CXR1-3 / CX5-L5-F1 in `docs/BUG_FIXES.md`).

Four P1s on ONE seam, each carrying out the OPPOSITE of what the player
typed, silently, at confidence 0.8–0.9 — above the 0.70 gate, so no key in
any mode corrected it. Reproduced on this HEAD at the real `POST /command`
before a line was written (September 23, 2026):

    `Ney, retreat as they attack`        FOUGHT at Swabia — four corps
                                         marched, a battle, the Butcher's
                                         Bill (CQ-32); six of six forms
    `Nobody retreat`                     a GENERAL RETREAT of eight corps,
                                         −2,270 men (CQ-34)
    `No one attack Mack`                 a muster and a battle, −6,010 men
    `couldn't we attack Mack`            a muster and a battle (CXR1-3);
                                         15 of 15 forms acted
    `I would not accept` (letter current) "Treaty signed" (CQ-35); 11 of 11
                                         forms signed, incl. `I'd not accept`

All four close in `backend/ai/clause_guards.py`: the negation vocabulary
gains the modal / perfect negatives and the contracted auxiliaries; the
negative indefinites become markers and leave `_COLLECTIVE`; and ONE
subtractive third-party reason-clause guard is sited after the question and
condition guards. `is_question`'s lead is NOT widened (the ruling — it is
what keeps `Davout, don't advance on our left, fortify` fortifying).

Every pin below drives the real endpoint on the shipped 1805 boot and reads
the WORLD (locations, strengths, action points, the diplomatic state, the
letter's own slot), never only the message. The golden corpus is 711/711 in
BOTH arms of this fix — for this family it is not evidence — so the
sensitivity class flips each lever and shows the battery going red.
"""

import pytest
from fastapi.testclient import TestClient

import backend.ai.clause_guards as CG
import backend.main as M
from backend.ai.llm_client import foe_names_for_guards
from backend.ai.parser_eval import run_corpus
from backend.commands.dialogue_routing import match_dialogue_answer
from backend.commands.parser import CommandParser


# ═══════════════════════════════════════════════════════════════════════
# The board
# ═══════════════════════════════════════════════════════════════════════

@pytest.fixture
def shipped(monkeypatch):
    """A fresh SHIPPED 1805 world at all three seams with a mock parser (the
    CR-7-1 idiom). The suite pins `SOVEREIGN_SCENARIO=none`, a board with no
    marshals; these rows need Ney at Rhineland and Mack at Swabia."""
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    assert M.parser.llm.use_real_api is False, "a probe must never pay for a parse"
    return TestClient(M.app), M.world


def post(client, command):
    return client.post("/command", json={"command": command}).json()


def snapshot(world):
    """Everything an order can move: the purse, the action points, every
    marshal's ground and strength, the dialogue slot, France–Prussia."""
    out = {
        "ap": int(world.actions_remaining),
        "admin": int(getattr(world, "admin_actions_remaining", 0)),
        "gold": int(world.gold),
        "dp": int(world.diplomatic_points),
        "fr_pr": world.get_diplomatic_state("France", "Prussia"),
        "dialogue": (world.pending_diplomatic_dialogue or {}).get("type"),
    }
    for m in world.marshals.values():
        out["m:" + m.name] = (m.location, int(m.strength))
    return out


def refused_free(data, before, after):
    """The PARSE-NEG refusal: no order, no charge, nothing moved."""
    assert data.get("success") is False, data.get("message")
    assert int((data.get("action_info") or {}).get("cost", 1)) == 0
    assert before == after, {k: (before.get(k), after.get(k))
                             for k in before if before.get(k) != after.get(k)}


def spent_an_action(before, after):
    return int(after["ap"]) < int(before["ap"])


def on_the_retreat_road(data, before, after):
    """Ney retreated (Rhineland → elsewhere at 0 AP), or an aggressive Ney
    OBJECTED to the retreat and stands where he was with the question
    pending — both are the retreat road. Neither is a battle."""
    assert data.get("success") is not False, data.get("message")
    assert not data.get("battle_report") and not data.get("battle_diorama")
    assert after["ap"] == before["ap"], "a retreat is free; an attack is not"
    moved = after["m:Ney"][0] != before["m:Ney"][0]
    objected = "object" in str(data.get("message", "")).lower()
    assert moved or objected, data.get("message")
    assert (data.get("command") or {}).get("action") in (None, "retreat"), data.get("command")


def prussian_letter(world):
    from backend.game_logic.ai_diplomacy import deliver_ai_proposal
    world.nation_relations[world._make_diplo_key("France", "Prussia")] = 60
    deliver_ai_proposal({"proposal_type": "non_aggression",
                         "source": "Prussia",
                         "terms": {"type": "non_aggression"}}, world)


# ═══════════════════════════════════════════════════════════════════════
# CQ-32 — the reason is not the order
# ═══════════════════════════════════════════════════════════════════════

REASON_RETREATS = [
    "Ney, retreat as they attack",
    "Ney, pull back, they are attacking",
    "Ney, retreat, Mack is attacking",
    "Ney, retreat because they are attacking",
    "Ney, retreat, they will attack us",
    "Ney, retreat, the Austrians are storming the bridge",
    "Ney, retreat since the enemy attacks",
    "Ney, withdraw, he is advancing on us",
    "Ney, retreat, the enemy has broken through",
    # the printed form of a two-word name (CX-7's through-line, one guard
    # over): with the roster KEYS alone handed in, this one ATTACKED him
    "Ney, retreat, Archduke Charles is attacking",
    "Ney, retreat as Archduke Charles advances",
]


class TestTheReasonIsNotTheOrder:

    @pytest.mark.parametrize("text", REASON_RETREATS)
    def test_a_retreat_given_with_its_reason_retreats(self, shipped, text):
        """Every one of these fought at Swabia."""
        client, world = shipped
        before = snapshot(world)
        data = post(client, text)
        on_the_retreat_road(data, before, snapshot(world))

    def test_the_reason_clauses_foe_is_not_the_retreats_destination(self, shipped):
        """The parser's fuzzy word scan is the THIRD reader of the raw text:
        with the clause blanked for the chain and the strategic layer but
        not for it, `Mack` was bound as the retreat's destination and the
        reply read "Mack cannot be reached, Sire — no such province"."""
        client, world = shipped
        data = post(client, "Ney, retreat, Mack is attacking")
        assert (data.get("command") or {}).get("target") in (None, ""), data.get("command")
        assert "cannot be reached" not in str(data.get("message", ""))

    @pytest.mark.parametrize("text", [
        "Ney, attack Mack as he retreats",
        "Lannes, pursue the retreating enemy",
        "Ney, it is time to attack Mack",
        "Ney, you ought to attack Mack",
        "Ney, they haven't fortified, attack Mack",
    ])
    def test_the_players_own_attack_still_fights(self, shipped, text):
        """The controls the contract names, and the shapes the guard must
        leave alone: `it` is not a reason-clause subject and a bare `ought`
        is not a marker."""
        client, world = shipped
        before = snapshot(world)
        data = post(client, text)
        after = snapshot(world)
        assert data.get("success") is not False, data.get("message")
        assert spent_an_action(before, after), data.get("message")

    def test_a_sentence_that_is_only_the_enemys_movements_is_refused_by_name(
            self, shipped):
        """`as they attack` alone — no order of ours in it. Not a battle,
        and not the generic shrug either: the clause is quoted back and the
        order asked for."""
        client, world = shipped
        for text in ("as they attack", "Ney, they are storming the bridge"):
            before = snapshot(world)
            data = post(client, text)
            refused_free(data, before, snapshot(world))
            assert "Nothing has been relayed" in data["message"], data["message"]
            assert "cannot interpret" not in data["message"]
        assert "they are storming the bridge" in data["message"]


# ═══════════════════════════════════════════════════════════════════════
# CX5-L5-F1 — the third party's retreat is not ours
# ═══════════════════════════════════════════════════════════════════════

THIRD_PARTY_FALLS_BACK = [
    "Ney, cover the retreat as they fall back",
    "Ney, hold the line as they fall back",
    "Ney, fortify as they pull back",
    "Ney, hold as they retreat",
    "Ney, hold your ground, they are retreating",
    "Ney, hold Rhineland as the enemy withdraws",
    "Ney, dig in as they pull back",
    "Ney, stand fast, the Austrians are falling back",
]


class TestTheThirdPartysRetreatIsNotOurs:

    @pytest.mark.parametrize("text", THIRD_PARTY_FALLS_BACK)
    def test_ney_does_not_retreat_on_the_enemys_retreat(self, shipped, text):
        """Eight of eight retreated Ney to Lorraine at 0.9. He stands."""
        client, world = shipped
        before = snapshot(world)
        data = post(client, text)
        after = snapshot(world)
        assert after["m:Ney"][0] == "Rhineland", data.get("message")
        assert (data.get("command") or {}).get("action") != "retreat", data.get("command")
        assert not data.get("battle_report")
        assert "retreats from" not in str(data.get("message", ""))
        assert before["m:Ney"][1] == after["m:Ney"][1]

    def test_hold_the_line_as_they_fall_back_holds(self, shipped):
        """The strategic layer is the SECOND reader of the raw text: with the
        clause blanked for the chain only, this one staged a MARCH onto Mack
        ("Mack blocks the path at Swabia. Odds unfavorable")."""
        client, world = shipped
        data = post(client, "Ney, hold the line as they fall back")
        assert data.get("success") is not False, data.get("message")
        assert "blocks the path" not in str(data.get("message", ""))
        assert "hold" in str(data.get("message", "")).lower()

    @pytest.mark.parametrize("text", [
        "Ney, fall back, the enemy is retreating",
        "Ney, withdraw as they fall back",
    ])
    def test_our_own_retreat_still_retreats(self, shipped, text):
        client, world = shipped
        before = snapshot(world)
        data = post(client, text)
        on_the_retreat_road(data, before, snapshot(world))


# ═══════════════════════════════════════════════════════════════════════
# CQ-34 — a prohibition on everybody is a prohibition
# ═══════════════════════════════════════════════════════════════════════

NEGATIVE_INDEFINITES = [
    "Nobody retreat", "Let no one retreat", "Nobody is to retreat",
    "No one attack Mack", "None attack Mack", "Nobody retreats!",
    "Let nobody retreat", "None of you retreat", "Not a man retreats",
    "Not one of you retreat", "No-one retreat", "No man retreats",
    "No corps is to attack Mack",
    # the vocative comma — the comma used to END the clause at the marker
    # and leave `retreat` standing
    "Nobody, retreat",
]


class TestTheNegativeIndefiniteIsAProhibition:

    @pytest.mark.parametrize("text", NEGATIVE_INDEFINITES)
    def test_nobody_means_nobody(self, shipped, text):
        """`Nobody retreat` was a general retreat of eight corps; `No one
        attack Mack` a battle; `None attack Mack` sent NEY (the word scan
        auto-corrected `none` → Ney)."""
        client, world = shipped
        before = snapshot(world)
        data = post(client, text)
        refused_free(data, before, snapshot(world))
        assert "no order goes out" in data["message"], data["message"]

    def test_someone_attack_mack_is_still_the_auto_assign(self, shipped):
        client, world = shipped
        before = snapshot(world)
        data = post(client, "someone attack Mack")
        assert data.get("success") is not False, data.get("message")
        assert spent_an_action(before, snapshot(world))

    def test_everyone_retreat_is_still_the_general_retreat(self, shipped):
        client, world = shipped
        before = snapshot(world)
        data = post(client, "everyone retreat")
        after = snapshot(world)
        assert "General retreat" in data.get("message", "") or (
            after["m:Ney"][0] != before["m:Ney"][0])

    def test_all_marshals_attack_still_asks_who_leads(self, shipped):
        client, world = shipped
        data = post(client, "all marshals attack")
        assert "Which marshal" in data.get("message", ""), data.get("message")

    def test_a_prohibition_before_a_comma_spares_the_order_after_it(self, shipped):
        """`Nobody retreat, Ney hold Lorraine` — the prohibition ends at its
        comma; Ney's order is a real order and Davout does not move."""
        client, world = shipped
        before = snapshot(world)
        data = post(client, "Nobody retreat, Ney hold Lorraine")
        after = snapshot(world)
        assert data.get("success") is not False, data.get("message")
        assert "General retreat" not in data.get("message", "")
        assert after["m:Davout"] == before["m:Davout"]

    def test_the_negative_indefinites_left_the_collective_and_stay_unaddressable(self):
        for word in ("nobody", "noone", "none"):
            assert word not in CG._COLLECTIVE, word
            assert word in CG._NEVER_AN_ADDRESS, word
            assert CG.addresses_the_army(word) is False
            assert CG.never_an_address(word.capitalize()) is True
        # the indefinites the auto-assign serves are untouched
        for word in ("someone", "anyone", "whoever", "everyone"):
            assert CG.addresses_the_army(word) is True


# ═══════════════════════════════════════════════════════════════════════
# CXR1-3 — the negative contractions
# ═══════════════════════════════════════════════════════════════════════

NEGATIVE_CONTRACTIONS = [
    "couldn't we attack Mack", "wouldn't we do better to retreat",
    "hasn't Ney attacked Mack", "shouldn't Ney attack Mack",
    "mightn't we attack Mack", "haven't we retreated enough",
    "have we attacked Mack", "ought we to attack Mack",
    "ought we not attack Mack", "wasn't Ney to attack Mack",
    "weren't we going to retreat", "isn't Ney attacking Mack",
    "aren't we retreating", "wouldn't Ney attack Mack", "couldn't Ney retreat",
    "Ney could not attack Mack", "Ney had better not attack Mack",
    "we'd rather not attack", "Ney needn't attack Mack",
]


class TestTheNegativeContractionIsANegation:

    @pytest.mark.parametrize("text", NEGATIVE_CONTRACTIONS)
    def test_it_spends_nothing_and_moves_nothing(self, shipped, text):
        """15 of 15 acted: `couldn't we attack Mack` fought (−6,010),
        `wouldn't we do better to retreat` was a general retreat."""
        client, world = shipped
        before = snapshot(world)
        data = post(client, text)
        refused_free(data, before, snapshot(world))

    @pytest.mark.parametrize("text", [
        "can you attack Mack",
        "would you have Ney attack Mack",
        "Ney, you should attack Mack",
        "Ney, attack Mack",
    ])
    def test_the_polite_order_still_marches(self, shipped, text):
        """`is_question`'s lead is NOT widened — the controls the row names."""
        client, world = shipped
        before = snapshot(world)
        data = post(client, text)
        assert data.get("success") is not False, data.get("message")
        assert spent_an_action(before, snapshot(world))

    def test_dont_advance_on_our_left_fortify_still_fortifies(self, shipped):
        """THE ruling's own sentence: a contraction as a question LEAD would
        read this as a question and leave Davout unfortified."""
        client, world = shipped
        before = snapshot(world)
        data = post(client, "Davout, don't advance on our left, fortify")
        assert data.get("success") is not False, data.get("message")
        assert "fortif" in str(data.get("message", "")).lower()
        assert spent_an_action(before, snapshot(world))

    def test_a_negation_inside_the_sentence_spares_the_order_after_it(self, shipped):
        client, world = shipped
        before = snapshot(world)
        data = post(client, "Ney, we can't hold, retreat")
        on_the_retreat_road(data, before, snapshot(world))


# ═══════════════════════════════════════════════════════════════════════
# CQ-35 — a negated answer signs nothing
# ═══════════════════════════════════════════════════════════════════════

NEGATED_MODAL_ANSWERS = [
    "I would not accept", "I wouldn't accept", "we could not accept that",
    "we'd rather not accept", "we had better not accept", "I might not accept",
    "we ought not accept", "we may not accept", "I'd not accept",
    "we couldn't accept", "we'll not accept", "I have not decided to accept",
]


class TestTheNegatedAnswerSignsNothing:

    @pytest.mark.parametrize("text", NEGATED_MODAL_ANSWERS)
    def test_the_letter_stays_current_and_the_treaty_unsigned(self, shipped, text):
        """11 of 11 signed — "Treaty signed: PEACE → NON_AGGRESSION with
        Prussia" on a sentence refusing it."""
        client, world = shipped
        prussian_letter(world)
        assert world.pending_diplomatic_dialogue is not None
        before = snapshot(world)
        post(client, text)
        after = snapshot(world)
        assert after["fr_pr"] == before["fr_pr"] == "PEACE"
        assert world.pending_diplomatic_dialogue is not None, "the letter was consumed"
        assert after["dp"] == before["dp"]

    @pytest.mark.parametrize("text", ["accept", "I would accept", "we could accept that"])
    def test_the_affirmative_still_signs(self, shipped, text):
        client, world = shipped
        prussian_letter(world)
        post(client, text)
        assert world.get_diplomatic_state("France", "Prussia") != "PEACE"

    def test_the_proposal_confirm_twin_sends_nothing(self, shipped):
        """The second dialogue family the row measured: `I would not send it`
        dispatched Talleyrand and spent the DP."""
        client, world = shipped
        post(client, "Talleyrand, propose a non-aggression pact to Prussia")
        assert (world.pending_diplomatic_dialogue or {}).get("type") == "proposal_confirm"
        before = snapshot(world)
        for text in ("I would not send it", "we couldn't send that"):
            data = post(client, text)
            after = snapshot(world)
            assert after["dp"] == before["dp"], data.get("message")
            assert (world.pending_diplomatic_dialogue or {}).get("type") == "proposal_confirm"
        data = post(client, "send it")
        assert snapshot(world)["dp"] < before["dp"], data.get("message")

    def test_the_router_reads_the_one_vocabulary(self):
        """`dialogue_routing` never copies the markers: the same regex that
        refuses the order refuses the answer."""
        assert CG.negation_marker_spans("i would not accept")
        assert CG.negation_marker_spans("i'd not accept")
        proposal = {"type": "incoming_proposal", "options": [
            {"label": "Accept", "action": "accept_ai_proposal"},
            {"label": "Reject", "action": "reject_ai_proposal"}]}
        roster = ["Ney", "Davout"]
        for line in ("i would not accept", "we ought not accept", "i'd not accept"):
            assert match_dialogue_answer(proposal, line, roster, world_regions=[]) is None
        assert match_dialogue_answer(proposal, "i would accept", roster,
                                     world_regions=[]) == "accept"


# ═══════════════════════════════════════════════════════════════════════
# The guards stay narrow
# ═══════════════════════════════════════════════════════════════════════

class TestTheGuardsStayNarrow:

    def test_a_condition_keeps_the_condition_guards_refusal(self, shipped):
        """`if they attack, retreat` is a contingency, and the reason guard
        is sited AFTER the condition guard so it stays one."""
        client, world = shipped
        before = snapshot(world)
        data = post(client, "Ney, if they attack, retreat")
        refused_free(data, before, snapshot(world))
        assert "contingency" in data["message"]

    def test_until_keeps_its_clause_for_the_engine(self):
        text = "Ney, hold until they attack"
        assert CG.strip_reason_clauses(text, foes=["Mack"]) == (text, False)

    def test_a_friendly_arrival_is_timing_not_a_reason(self):
        text = "Ney, attack Mack as Davout arrives"
        assert CG.strip_reason_clauses(text, foes=["Mack"]) == (text, False)

    def test_it_is_never_a_reason_clause_subject(self):
        text = "Ney, it is time to attack Mack"
        assert CG.strip_reason_clauses(text, foes=["Mack"]) == (text, False)

    def test_a_second_marshals_order_is_never_a_reason_clause(self):
        text = "Ney, attack Mack, Davout hold Swabia"
        assert CG.strip_reason_clauses(text, foes=["Mack"]) == (text, False)

    def test_the_blank_preserves_every_position(self):
        text = "Ney, retreat, the Austrians are storming the bridge"
        out, applied = CG.strip_reason_clauses(text)
        assert applied and len(out) == len(text)
        assert out.startswith("Ney, retreat") and out.strip() == "Ney, retreat"

    def test_a_bare_ought_and_no_quarter_are_not_markers(self):
        assert CG.strip_negated_clauses("Ney, you ought to attack Mack")[1] is False
        assert CG.strip_negated_clauses("Ney, give no quarter")[1] is False
        assert CG.strip_negated_clauses("Ney, take no prisoners")[1] is False

    def test_the_foe_roster_carries_both_registers(self):
        forms = {f.lower() for f in foe_names_for_guards(names=["ArchdukeCharles"])}
        assert "archduke charles" in forms, forms
        assert "archdukecharles" in forms, forms


# ═══════════════════════════════════════════════════════════════════════
# The sensitivity arm — flip each lever and the battery reds
# ═══════════════════════════════════════════════════════════════════════

class TestSensitivity:

    def test_the_vocabulary_lever_is_what_stops_nobody_retreat(self, shipped, monkeypatch):
        monkeypatch.setattr(CG, "WHAT_THE_SENTENCE_FORBIDS_IS_NEVER_THE_ORDER", False)
        client, world = shipped
        before = snapshot(world)
        post(client, "Nobody retreat")
        after = snapshot(world)
        assert after["m:Ney"][0] != before["m:Ney"][0], "lever down must reproduce the defect"

    def test_the_vocabulary_lever_is_what_keeps_the_treaty_unsigned(self, shipped, monkeypatch):
        monkeypatch.setattr(CG, "WHAT_THE_SENTENCE_FORBIDS_IS_NEVER_THE_ORDER", False)
        client, world = shipped
        prussian_letter(world)
        post(client, "I would not accept")
        assert world.get_diplomatic_state("France", "Prussia") != "PEACE"

    def test_the_reason_lever_is_what_stops_the_battle(self, shipped, monkeypatch):
        monkeypatch.setattr(CG, "THE_REASON_IS_NOT_THE_ORDER", False)
        client, world = shipped
        before = snapshot(world)
        data = post(client, "Ney, retreat as they attack")
        assert spent_an_action(before, snapshot(world)), data.get("message")

    def test_the_legacy_regex_is_the_old_vocabulary_byte_for_byte(self):
        assert CG._NEGATION_MARKER_RE_LEGACY.pattern == (
            r"\b(?:" + CG._NEGATION_MARKER_SRC + r")\b")
        assert "would" not in CG._NEGATION_MARKER_SRC
        assert "nobody" not in CG._NEGATION_MARKER_SRC.lower()


# ═══════════════════════════════════════════════════════════════════════
# The corpus — green, and not evidence
# ═══════════════════════════════════════════════════════════════════════

class TestTheCorpusStillPasses:

    def test_every_row_is_green_with_the_fix(self, monkeypatch):
        monkeypatch.setenv("LLM_MODE", "mock")
        summary = run_corpus(use_real_llm=False)
        assert summary["passed"] == summary["total"], summary["failures"]
