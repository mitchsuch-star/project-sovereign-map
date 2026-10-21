"""The four open rows of `docs/BUG_FIXES.md` §CF (the command-feel review,
`docs/audits/COMMAND_FEEL_2026_10_16.md`), built October 17, 2026; rules
`SYSTEMS_REFERENCE.md` §126.

* CF-6 — Hold (2 AP) · Fall back · Garrison (2 AP) chips on the province
  panel's own-marshal row (and the Generals card) in the CN-4 pattern: lit
  only where `tactical_state.order_refusals` carries no reason for the verb,
  dimmed with the reason otherwise, priced on the label from
  `order_prices`, sent as the literal typed string. The probe gained the
  three verbs' own gates (`state_probe._own_reason`).
* CF-4 — a refusal whose remedy is ONE known verb rides `remedy_command`
  (the ↳ offer slot); the refused order is re-offered once the remedy is
  sent (`backend/commands/remedy.py`, the `_pending_relay` pattern).
* CF-7 — "what would it cost to march Davout to Vienna" answers from
  `order_quotes.march_quote` — byte-identical to the panel's quote.
* CF-8 — "what can Ney do" answers from `state_probe.order_refusals`.

Every pin drives the real `POST /command` on a fresh mock-parser 1805 boot
(the mood variance pinned flat, as `test_cc2_march_here.py` does) and reads
the world beside the reply. The client pins are driven through
`tools/cn3_region_panel_harness.gd` when the engine is present — a skip is
not a pass — and the `.gd` sources are read for the wiring the harness
cannot exercise (the ↳ slot).
"""

import contextlib
import io
import re

import pytest
from fastapi.testclient import TestClient

import backend.commands.state_probe as SP
import backend.main as M
from backend.commands import executor as executor_mod
from backend.commands import objection_v2 as ov2
from backend.commands import strategic_executor as se_mod
from backend.commands.order_quotes import march_quote
from backend.display_names import humanize_entity_name
from backend.game_logic.recruitment import build_recruitment_payload
from backend.models.marshal import Stance
from tests import _chip_census as C

REPO = C.REPO
SCRIPTS = C.SCRIPTS
SHRUG = re.compile(r"cannot answer that from the dispatches", re.I)
CHIP_VERBS = ("hold", "retreat", "garrison")
LABELS = {"hold": "Hold", "retreat": "Fall back", "garrison": "Garrison"}


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture
def client(monkeypatch):
    """A fresh mock-parser 1805 board, the mood roll flattened."""
    C.board_env(monkeypatch)
    flat = (lambda concern: concern)
    monkeypatch.setattr(executor_mod, "apply_mood_variance", flat)
    monkeypatch.setattr(se_mod, "apply_mood_variance", flat)
    monkeypatch.setattr(ov2, "apply_mood_variance", flat)
    return TestClient(M.app)


def post(client, command):
    with _quiet():
        return client.post("/command", json={"command": command}).json()


def _player_marshals(world):
    return [m for m in world.get_player_marshals()
            if int(getattr(m, "strength", 0) or 0) > 0 and not getattr(m, "captured_by", "")]


def _asked(world, who):
    tactical = (getattr(world, "pending_objection", None) or {}).get("marshal") == who
    strategic = str((getattr(world, "pending_strategic_objection", None) or {}).get("marshal") or "") == who
    return tactical or strategic


def _fortify(marshal):
    marshal.fortified, marshal.stance, marshal.defense_bonus = True, Stance.DEFENSIVE, 0.10


# ═══════════════════════════════════════════════════════════════════════════
# CF-6 — Hold · Fall back · Garrison
# ═══════════════════════════════════════════════════════════════════════════

class TestCF6TheChips:

    def test_the_probe_prices_every_verb_as_the_executor_charges(self, client):
        world = M.world
        for m in _player_marshals(world):
            prices = SP.order_prices(world, m)
            assert set(prices) == set(SP.VERBS), m.name
            assert prices["hold"] == int(m.strategic_order_ap(order_type="HOLD"))
            assert prices["garrison"] == int(world.get_action_cost("garrison"))
            assert prices["retreat"] == 0
        # A literal marshal's standing order is 1; the rest pay 2.
        assert SP.order_prices(world, world.get_marshal("Soult"))["hold"] == 1
        assert SP.order_prices(world, world.get_marshal("Ney"))["hold"] == 2

    def test_the_payload_and_the_card_ship_the_prices(self, client):
        gs = C.game_state_now()
        seen = 0
        for region, data in gs["map_data"].items():
            for row in data.get("marshals") or []:
                if row.get("nation") != "France":
                    continue
                state = row["tactical_state"]
                assert state["order_prices"]["hold"] in (1, 2), (region, row["name"])
                assert "order_refusals" in state
                seen += 1
        assert seen >= 8
        cards = C.overview_now()["marshals"]
        assert all(card["order_prices"]["garrison"] == 2 for card in cards if not card.get("captured"))

    @pytest.mark.parametrize("verb", CHIP_VERBS)
    def test_every_chip_string_acts_as_the_probe_says(self, verb, monkeypatch):
        """`<Name>, hold` / `retreat` / `garrison` for every corps of ours on
        the boot board: taken (or put to the man) where the probe has no
        reason, at the label's price; refused for nothing where it has."""
        for name in [m.name for m in _player_marshals(M.world)]:
            C.board_env(monkeypatch)
            flat = (lambda concern: concern)
            monkeypatch.setattr(executor_mod, "apply_mood_variance", flat)
            monkeypatch.setattr(se_mod, "apply_mood_variance", flat)
            monkeypatch.setattr(ov2, "apply_mood_variance", flat)
            client = TestClient(M.app)
            world = M.world
            m = world.get_marshal(name)
            reason = SP.order_state_refusal(world, m, verb)
            price = SP.order_price(world, m, verb)
            before = int(world.actions_remaining)
            reply = post(client, f"{name}, {verb}")
            msg = str(reply.get("message") or "")
            if reason:
                assert not reply.get("success"), (name, verb, reason, msg)
                assert int(M.world.actions_remaining) == before, (name, verb, msg)
            else:
                asked = _asked(M.world, name)
                assert reply.get("success") or asked, (name, verb, msg)
                if reply.get("success") and not asked:
                    assert before - int(M.world.actions_remaining) == price, (name, verb, price, msg)

    def test_the_three_own_gates_are_the_executors(self, client):
        world = M.world
        ney = world.get_marshal("Ney")
        # the boot keeps its three garrisons: the probe's reason is the gate's
        assert SP.order_state_refusal(world, ney, "garrison") == "3 of 3 garrisons kept"
        reply = post(client, "Ney, garrison")
        assert not reply.get("success") and "3 garrisons" in str(reply.get("message"))
        # a hold already standing here: the executor takes the identical
        # order as a no-op at 0 AP ("No change", F10) — the chip is dimmed
        # with the probe's reason rather than lit at a price it never charges.
        reply = post(client, "Ney, hold")
        assert reply.get("success") or _asked(world, "Ney"), reply.get("message")
        if ney.strategic_order is not None:
            assert SP.order_state_refusal(world, ney, "hold") == "already holding here"
            ap = int(world.actions_remaining)
            reply = post(client, "Ney, hold")
            assert "already carrying out that order" in str(reply.get("message"))
            assert int(world.actions_remaining) == ap
            assert ney.strategic_order.command_type == "HOLD"
        # a retreat already made this turn
        davout = world.get_marshal("Davout")
        davout.retreated_this_turn = True
        assert SP.order_state_refusal(world, davout, "retreat") == "already retreated this turn"
        reply = post(client, "Davout, retreat")
        assert not reply.get("success") and "already retreated" in str(reply.get("message"))

    def test_the_retreat_gate_is_fog_honest(self, client):
        """No enemy we can see within a march: the chip is dimmed "not in
        danger" — and a hidden corps beside him never lights it (the
        completer's rule; the executor's own omniscient test is not
        shipped)."""
        world = M.world
        soult = world.get_marshal("Soult")
        for foe in world.get_enemies_of_nation("France"):
            if world.get_distance(foe.location, soult.location) <= 2:
                foe.location = "Vienna"
        C.refresh_view(world)
        assert SP.order_state_refusal(world, soult, "retreat") == "not in danger — no retreat needed"
        # a hidden enemy adjacent: the probe still reads what the map shows
        # (the executor's omniscient test would take the retreat; the chip
        # never says so)
        from backend.models.intel import UNKNOWN
        mack = world.get_marshal("Mack")
        mack.location = "Franche-Comte"
        world.get_region_intel("Franche-Comte").visibility = UNKNOWN
        assert world.is_in_danger("Soult")
        assert mack.name not in {e.name for e in world.get_visible_enemies("France")}
        assert SP.order_state_refusal(world, soult, "retreat") == "not in danger — no retreat needed"
        assert "Mack" not in str(SP.order_refusals(world, soult))

    def test_the_panel_source_offers_the_three_in_the_cn4_pattern(self):
        src = (SCRIPTS / "region_panel.gd").read_text(encoding="utf-8")
        assert 'for spec in [["hold", "Hold"], ["retreat", "Fall back"], ["garrison", "Garrison"]]' in src
        assert '"order:" + verb + ":" + m_name' in src
        assert 'tactical.get("order_prices", {})' in src
        assert 'refusals.get(verb, "")' in src
        cards = (SCRIPTS / "marshal_management.gd").read_text(encoding="utf-8")
        assert 'm.get("order_prices", {})' in cards and '["retreat", "Fall back"]' in cards

    def test_the_panel_driven_lights_what_the_probe_opens(self, tmp_path):
        """The REAL region panel, headless: Hold priced per marshal, Fall
        back free and lit beside the enemy, Garrison dimmed with the
        probe's reason on the boot board; every lit chip's string acts."""
        with pytest.MonkeyPatch.context() as mp:
            C.board_env(mp)
            world = M.world
            # Massena at Milan: not our soil — a second garrison reason.
            gs = C.game_state_now()
            regions = sorted({m.location for m in _player_marshals(world)})
            out = C.render(gs, regions, build_recruitment_payload(world), tmp_path,
                           overview=C.overview_now())
            assert out["errors"] == 0
            rhine = out["regions"]["Rhineland"]
            assert "[url=order:hold:Ney]" in rhine and "Hold (2 AP)" in rhine
            assert "[url=order:retreat:Ney]" in rhine and "Fall back" in rhine
            assert "[url=order:garrison:Ney]" not in rhine
            assert "3 of 3 garrisons kept" in rhine
            lorraine = out["regions"]["Lorraine"]
            assert "[url=order:hold:Soult]" in lorraine and "Hold (1 AP)" in lorraine
            milan = out["regions"]["Milan"]
            assert "not our soil" in milan
            cards = out["cards"]
            assert "[url=order:hold:Ney]" in cards and "[url=order:retreat:Soult]" in cards
            # every lit chip of the three, sent, is taken or put to the man
            for region, bb in out["regions"].items():
                for url, label, _tail in C.chips(bb):
                    if not url.startswith(("order:hold:", "order:retreat:", "order:garrison:")):
                        continue
                    C.boot()
                    who = url.split(":")[2]
                    reply = C.post(TestClient(M.app), {"command": C.chip_command(url)})
                    assert reply.get("success") or _asked(M.world, who), (region, url, reply.get("message"))


# ═══════════════════════════════════════════════════════════════════════════
# CF-4 — the remedy
# ═══════════════════════════════════════════════════════════════════════════

class TestCF4TheRemedy:

    def test_the_fortified_attack_names_its_remedy_and_is_re_offered_once(self, client):
        world = M.world
        _fortify(world.get_marshal("Ney"))
        ap = int(world.actions_remaining)
        reply = post(client, "Ney, attack Mack")
        assert not reply.get("success")
        assert reply.get("remedy_command") == "Ney, unfortify"
        assert "relay_command" not in reply
        assert int(world.actions_remaining) == ap
        # the remedy sent unchanged: it goes out, and the order comes back
        reply = post(client, "Ney, unfortify")
        assert reply.get("success"), reply.get("message")
        assert reply.get("relay_kind") == "ready"
        assert reply.get("relay_command") == "Ney, attack Mack"
        assert '"Ney, attack Mack" — is on the line' in str(reply.get("message"))
        assert "remedy_command" not in reply
        # once: the next reply carries nothing
        reply = post(client, "Davout, scout Swabia")
        assert "relay_command" not in reply and "remedy_command" not in reply
        # the game never sent the attack for him
        assert not world.get_marshal("Ney").fortified
        assert (getattr(world, "pending_objection", None) or {}).get("marshal") != "Ney"

    @pytest.mark.parametrize("order", ["Ney, move to Lorraine", "Ney, march to Paris", "Ney, drill"])
    def test_every_fortified_producer_stamps_unfortify(self, client, order):
        world = M.world
        _fortify(world.get_marshal("Ney"))
        reply = post(client, order)
        assert not reply.get("success"), reply.get("message")
        assert reply.get("remedy_command") == "Ney, unfortify", (order, reply.get("message"))
        reply = post(client, "ney unfortify")   # the comma and the case forgiven
        assert reply.get("success") and reply.get("relay_command") == order

    def test_the_stance_remedy_is_the_free_neutral(self, client):
        world = M.world
        ney = world.get_marshal("Ney")
        ney.stance = Stance.AGGRESSIVE
        for order in ("Ney, fortify", "Ney, drill"):
            ney.stance = Stance.AGGRESSIVE
            reply = post(client, order)
            assert not reply.get("success")
            assert reply.get("remedy_command") == "Ney, neutral", (order, reply.get("message"))
        ap = int(world.actions_remaining)
        reply = post(client, "Ney, neutral")
        assert reply.get("success") and int(world.actions_remaining) == ap
        assert reply.get("relay_command") == "Ney, drill"

    def test_another_command_lets_the_order_go_without_a_word(self, client):
        world = M.world
        _fortify(world.get_marshal("Ney"))
        post(client, "Ney, attack Mack")
        other = post(client, "Davout, scout Swabia")
        assert "relay_let_go" not in other and "let go" not in str(other.get("message"))
        reply = post(client, "Ney, unfortify")
        assert reply.get("success") and "relay_command" not in reply

    def test_the_turn_boundary_clears_it(self, client):
        world = M.world
        _fortify(world.get_marshal("Ney"))
        post(client, "Ney, attack Mack")
        assert world._pending_remedy is not None
        post(client, "end turn")
        assert world._pending_remedy is None
        reply = post(client, "Ney, unfortify")
        assert reply.get("success") and "relay_command" not in reply

    def test_a_later_refusal_replaces_the_stash(self, client):
        world = M.world
        _fortify(world.get_marshal("Ney"))
        post(client, "Ney, march to Paris")
        post(client, "Ney, drill")
        reply = post(client, "Ney, unfortify")
        assert reply.get("relay_command") == "Ney, drill"

    def test_the_withdrawal_is_offered_but_never_re_offered(self, client):
        """DDB R6's sentence names 'Ney, retreat to Swabia': the first half
        only — the retreat REPLACES the move, so the move never comes back."""
        world = M.world
        world.get_marshal("Mack").location = "Rhineland"
        C.refresh_view(world)
        reply = post(client, "Ney, move to Swabia")
        assert not reply.get("success"), reply.get("message")
        assert reply.get("remedy_command") == "Ney, retreat to Swabia", reply.get("message")
        assert "remedy_reoffer" not in reply
        reply = post(client, "Ney, retreat to Swabia")
        assert reply.get("success") or _asked(world, "Ney"), reply.get("message")
        assert "relay_command" not in reply

    def test_a_remedy_never_rides_a_success_or_a_plain_refusal(self, client):
        reply = post(client, "Ney, scout Swabia")
        assert reply.get("success") and "remedy_command" not in reply
        reply = post(client, "Ney, unfortify")   # not fortified: no remedy to name
        assert not reply.get("success") and "remedy_command" not in reply

    def test_the_client_takes_it_into_the_offer_slot(self):
        src = (SCRIPTS / "main.gd").read_text(encoding="utf-8")
        assert "var pending_remedy_command := \"\"" in src
        stash = src[src.index("func _stash_remedy("):]
        stash = stash[:stash.index("\nfunc ")]
        assert 'response.get("remedy_command")' in stash
        fill = src[src.index("func _fill_pending_remedy("):]
        fill = fill[:fill.index("\nfunc ")]
        assert "_offer_beside_line(cmd, false)" in fill
        assert "command_input.text = " not in fill   # never ON the line
        assert "_stash_remedy(response)" in src and "_fill_pending_remedy()" in src
        retire = src[src.index("func _retire_line_latches("):]
        retire = retire[:retire.index("\nfunc ")]
        assert 'pending_remedy_command = ""' in retire
        report = (REPO / "tools" / "godot_parse_report.json").read_text(encoding="utf-8")
        assert '"parse_ok": false' not in report and '"load_ok": false' not in report


# ═══════════════════════════════════════════════════════════════════════════
# CF-7 — the march priced by the quote
# ═══════════════════════════════════════════════════════════════════════════

def _figures(answer):
    ap = int(re.search(r"costs (\d+) action", answer).group(1))
    turns = 0 if "this very turn" in answer else int(re.search(r"arrives in (\d+) turn", answer).group(1))
    road = re.search(r"the road runs ([^.]+)\.", answer).group(1).split(" -> ")[1:]
    return ap, turns, road


class TestCF7TheMarchCost:

    @pytest.mark.parametrize("who,dest,ask", [
        ("Davout", "Vienna", "what would it cost to march Davout to Vienna"),
        ("Ney", "Munich", "what does it cost to send Ney to Munich"),
        ("Soult", "Paris", "how much would it cost Soult to march to Paris"),
        ("Murat", "Bohemia", "how many actions would it take Murat to march to Bohemia"),
    ])
    def test_the_answer_is_the_quote(self, client, who, dest, ask):
        world = M.world
        q = march_quote(world, world.get_marshal(who), dest)
        assert q["ok"], q
        reply = post(client, ask)
        answer = str(reply.get("message") or "")
        assert not SHRUG.search(answer), answer
        assert _figures(answer) == (int(q["ap"]), int(q["turns"]), list(q["road"])), answer
        if q["note"]:
            assert q["note"].rstrip(".") in answer
        assert int(world.actions_remaining) == 4

    def test_the_answer_is_the_panels_row(self, client):
        """GET /march_quotes for Vienna carries Davout's march row; the desk
        prints the same three figures."""
        with _quiet():
            payload = client.get("/march_quotes", params={"region": "Vienna"}).json()
        row = next(r for r in payload["march"] if r["marshal"] == "Davout")
        answer = str(post(client, "what would it cost to march Davout to Vienna").get("message"))
        assert _figures(answer) == (int(row["ap"]), int(row["turns"]), list(row["road"]))

    def test_a_refused_march_is_refused_in_the_quotes_words(self, client):
        world = M.world
        _fortify(world.get_marshal("Davout"))
        q = march_quote(world, world.get_marshal("Davout"), "Vienna")
        assert not q["ok"]
        answer = str(post(client, "what would it cost to march Davout to Vienna").get("message"))
        assert "would be refused today" in answer and q["refusal"] in answer

    def test_the_bare_march_keeps_the_manual(self, client):
        answer = str(post(client, "what does a march cost").get("message"))
        assert "standing order of 2 actions" in answer

    def test_how_long_reads_the_marchs_own_road(self, client):
        """CF-7's sibling: the clock answer walks `march_road` (the cautious
        man's avoid-set) — Davout's turns equal the quote's."""
        world = M.world
        q = march_quote(world, world.get_marshal("Davout"), "Vienna")
        answer = str(post(client, "how long would Davout take to reach Vienna").get("message"))
        assert f"in {q['turns']} turns" in answer, answer
        assert " -> ".join(["Rhineland"] + list(q["road"])) in answer


# ═══════════════════════════════════════════════════════════════════════════
# CF-8 — the per-marshal options
# ═══════════════════════════════════════════════════════════════════════════

class TestCF8TheOptions:

    @pytest.mark.parametrize("ask", ["what can Ney do", "what are Ney's options",
                                     "what orders can I give Ney", "what can I do with Ney",
                                     "what can Ney do today"])
    def test_the_answer_is_the_probes(self, client, ask):
        world = M.world
        ney = world.get_marshal("Ney")
        refused = SP.order_refusals(world, ney)
        prices = SP.order_prices(world, ney)
        answer = str(post(client, ask).get("message"))
        assert not SHRUG.search(answer), answer
        assert answer.startswith("Ney stands at Rhineland with 4 actions")
        for verb, why in refused.items():
            if verb == "land":
                continue
            assert why in answer, (verb, why, answer)
        assert "fall back (free)" in answer
        assert f"march ({prices['march']} actions)" in answer
        assert "attack (1 action)" in answer
        assert int(world.actions_remaining) == 4

    def test_a_fortified_corps_lists_unfortify_and_the_rest_refused(self, client):
        world = M.world
        _fortify(world.get_marshal("Ney"))
        answer = str(post(client, "what can Ney do").get("message"))
        assert "unfortify (1 action)" in answer
        assert "attack, move one province, march — fortified — unfortify first" in answer \
            or ("fortified — unfortify first" in answer and "attack" in answer)

    def test_the_armys_options_keep_their_kind(self, client):
        answer = str(post(client, "what are my options").get("message"))
        assert "These orders would be carried out today" in answer or "Nothing can be ordered" in answer

    @pytest.mark.parametrize("ask,expect", [
        ("can Ney fortify", "Yes, Sire — Ney can fortify today; it costs 1 action."),
        ("can Ney retreat", "Yes, Sire — Ney can fall back today; it is free."),
        # SFR-H4 (SF-RR2, Oct 21, 2026): the refusal names the verb it refuses.
        ("can Massena garrison", "Not today, Sire — Massena cannot garrison: not our soil."),
        ("could Davout march", "Yes, Sire — Davout can march today; it costs 2 actions."),
    ])
    def test_the_per_verb_sibling(self, client, ask, expect):
        answer = str(post(client, ask).get("message"))
        assert answer.startswith(expect), answer

    def test_a_place_or_a_foe_keeps_the_older_kinds(self, client):
        from backend.ai.question_desk import classify_board_question
        marshals = [m.name for m in M.world.marshals.values() if m.nation == "France"]
        enemies = [m.name for m in M.world.marshals.values() if m.nation != "France"]
        regions = list(M.world.regions)
        kinds = {ask: (classify_board_question(ask, marshals=marshals, enemies=enemies,
                                               regions=regions, nations=["Austria"]) or {}).get("kind")
                 for ask in ("can Ney hold Milan", "can Ney reach Vienna",
                             "what are the odds if Ney attacks Mack")}
        assert kinds["can Ney hold Milan"] == "hold_region"
        assert kinds["can Ney reach Vienna"] == "reach"
        assert kinds["what are the odds if Ney attacks Mack"] in ("what_if_odds", "odds_natural", "what_if_named")
