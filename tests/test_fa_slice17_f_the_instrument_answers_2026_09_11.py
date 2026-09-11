"""FA slice 17, part f — "The Instrument Answers" (FA-72, FA-75, FA-78, FA-79,
FA-85, FA-89, FA-90, FA-102, FA-N35).

Nine HARNESS rows, landed in REPRO_L's determinism-governed order. The rule
that order encodes: adding GETs and digest LINES changes nothing; adding or
changing a POST shifts every later RNG draw in that turn. So the two
logging halves (FA-75 A, FA-79 A) went first, then the answer-policy
changes, then the mailbox loop that opens the settlement ladder.

⚠ Corrections REPRO_L made to the rows, honoured here:
* FA-72's token-match fix alone fixes ONE of four diplomacy modes — the
  paradox needed its OWN policy key, answered BEFORE the generic block.
* FA-78's "filter options through _enabled" is a measured NO-OP on its own
  headline case — the `proposal_confirm` branch returns a LITERAL when
  `find()` misses, so the literal fallbacks had to be gated too; and "take
  the first enabled option" would press `cancel_proposal`.
* FA-79's `petition: rotate` ships OPT-IN, never as the default (it makes
  every archived digest non-regenerable); the redemption default flips to
  the self-expiring, non-destructive arm.
* FA-75's backend tuple edit is dead weight: `lapsed_offers` and the envoy
  list are ALREADY on `GET /dispatch`, which the driver reads every turn.
* FA-85: Bordelais, not Brittany — Brittany is a camp province and Soult's
  30,000 there would perturb the Descent staging the script measures.
* FA-102's contract is re-stated: byte-identical modulo the load lines AND
  any answer the load re-raises, Mode A only.
* FA-89's backend key is a SECOND, approximate source by construction (the
  overlay's advance predicates are fifteen GDScript functions over
  cross-response latches); it is pinned as approximate and display-only.
* FA-90's arm (2) fate-word half is NOT built (slice 2 made it unnecessary
  and slice 0's router makes it hazardous); arm (3) is already shipped.
* FA-N35's "post WITHOUT a dialogue_id" is the exact opposite of what the
  client does since slice 0 — the driver sends the id, like the client.

Decision recorded here rather than filed elsewhere: REPRO_L's step 3
("archive a fresh digest set") is NOT re-run for the nine old `audit-*`
digests — they stay as historical evidence with their old driver — and
attributability is met by stamping `driver_revision` into every run's
meta.json from here on. The Phase-3 playtest produces the fresh set.
"""

import hashlib
import importlib.util
import argparse
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

_spec = importlib.util.spec_from_file_location(
    "playtest_driver", REPO_ROOT / "tools" / "playtest_driver.py")
driver = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("playtest_driver", driver)
_spec.loader.exec_module(driver)


class StubTransport:
    def __init__(self, replies=None, gets=None):
        self.posts = []
        self.replies = replies or {}
        self.gets = gets or {}

    def post(self, path, payload=None):
        self.posts.append((path, payload))
        reply = self.replies.get(path, {"success": True})
        return dict(reply(payload) if callable(reply) else reply)

    def get(self, path):
        return dict(self.gets.get(path, {}))


class StubDigest:
    def __init__(self):
        self.popups = []
        self.battles_seen = []
        self.recent = []
        self.counters = {"commands": 0, "popups": 0, "battles": 0, "turns": 0}
        self.notes = []
        self.md_lines = []
        self.unknown_blockers = []
        self.records = []
        self.meta = {}

    def popup(self, key, summary, answer):
        self.counters["popups"] += 1
        self.popups.append((key, summary, answer))
        if str(answer) not in ("(left standing)", "display-only", "(no options)"):
            self.recent.append((str(key), str(summary), str(answer)))

    def discount_answer(self, key, summary, answer):
        sig = (str(key), str(summary), str(answer))
        if sig in self.recent:
            self.recent.remove(sig)

    def battle(self, report):
        self.counters["battles"] += 1
        self.battles_seen.append(report)

    def note(self, text):
        self.notes.append(text)

    def record(self, kind, **fields):
        self.records.append({"kind": kind} | fields)

    def _md(self, line):
        self.md_lines.append(line)

    def envoy_answer(self, row, choice, outcome):
        self.counters["popups"] += 1
        self.popups.append(("envoy_digest", row.get("from_nation"), f"{choice}{outcome}"))

    def unknown_blocker(self, key, payload):
        self.unknown_blockers.append(key)


def make_answerer(replies=None, policy_overrides=None, gets=None):
    transport = StubTransport(replies, gets)
    digest = StubDigest()
    policy = dict(driver.POLICY_DEFAULTS) | (policy_overrides or {})
    answerer = driver.Answerer(transport, digest, policy, strict=False)
    answerer.begin_post()
    return answerer, transport, digest


PARADOX = {
    "type": "commitment_paradox", "dialogue_id": 7, "blocking": True,
    "options": [
        {"label": "Honor alliance with Austria", "action": "honor_defender"},
        {"label": "Side with Prussia", "action": "break_defender_alliance"},
    ],
}


# ═══════════════════════════════════════════════════════════════════════
# FA-72 — the paradox has its own policy; needles are whole tokens
# ═══════════════════════════════════════════════════════════════════════

class TestFA72TheParadoxIsAnsweredOnPurpose:

    def test_the_policy_key_exists_with_the_recorded_default(self):
        assert driver.POLICY_DEFAULTS["paradox"] == "honor"

    @pytest.mark.parametrize("mode", ["decline", "accept", "first", "propose"])
    def test_every_diplomacy_mode_answers_from_the_paradox_key(self, mode):
        a, _t, _d = make_answerer(policy_overrides={"diplomacy": mode})
        assert a._pick_dialogue_choice(dict(PARADOX)) == "honor_defender"
        a, _t, _d = make_answerer(policy_overrides={"diplomacy": mode, "paradox": "break"})
        assert a._pick_dialogue_choice(dict(PARADOX)) == "break_defender_alliance"

    def test_no_no_longer_matches_honor(self):
        """The defect: the `decline` needle "no" substring-matched
        ho-NO-r_defender. Needles now match whole `_`-tokens."""
        a, _t, _d = make_answerer(policy_overrides={"diplomacy": "decline"})
        picked = a._pick_dialogue_choice({
            "type": "some_other_dialogue", "dialogue_id": 3,
            "options": [{"action": "honor_something"}, {"action": "decline_it"}]})
        assert picked == "decline_it"


    def test_a_needle_never_matches_inside_a_longer_token(self):
        """72/b alone: substring matching (the reverted form) finds `sign`
        inside re-SIGN-_the_pact and presses it under `accept`; whole
        `_`-tokens do not. (The honor/decline case above cannot see this
        once `no` is out of the needles — this pin is the token rule's own.)"""
        a, _t, _d = make_answerer(policy_overrides={"diplomacy": "accept"})
        picked = a._pick_dialogue_choice({
            "type": "x", "dialogue_id": 12,
            "options": [{"action": "resign_the_pact"}, {"action": "accept_terms"}]})
        assert picked == "accept_terms"

    def test_the_word_no_is_not_a_decline_needle(self):
        """72/c alone: with `no` restored to the needles, ANY option carrying
        the word as a token — here `no_quarter`, an ATTACK — is pressed
        ahead of the real decline. `no` earns nothing the other three do
        not already find, and this is what it costs."""
        a, _t, _d = make_answerer(policy_overrides={"diplomacy": "decline"})
        picked = a._pick_dialogue_choice({
            "type": "x", "dialogue_id": 13,
            "options": [{"action": "no_quarter"}, {"action": "decline_offer"}]})
        assert picked == "decline_offer"

    def test_whole_token_needles_still_find_the_live_vocabulary(self):
        a, _t, _d = make_answerer(policy_overrides={"diplomacy": "accept"})
        picked = a._pick_dialogue_choice({
            "type": "x", "dialogue_id": 4,
            "options": [{"action": "reject_offer"}, {"action": "accept_settlement_offer"}]})
        assert picked == "accept_settlement_offer"


# ═══════════════════════════════════════════════════════════════════════
# FA-78 — a disabled option is never pressed
# ═══════════════════════════════════════════════════════════════════════

class TestFA78ADisabledOptionIsNeverPressed:

    def test_the_literal_confirm_fallback_is_gated(self):
        a, _t, d = make_answerer(policy_overrides={"diplomacy": "propose"})
        choice = a._pick_dialogue_choice({
            "type": "proposal_confirm", "dialogue_id": 9,
            "options": [
                {"action": "execute_proposal", "enabled": False,
                 "description": "I cannot deliver this, Sire — Making peace with Austria while allied with Bavaria…"},
                {"action": "cancel_proposal", "enabled": True},
            ]})
        assert choice is None, "the defect: the literal 'confirm' was posted anyway"
        assert a.last_standing_reason and "cannot deliver" in a.last_standing_reason

    def test_an_enabled_confirm_still_confirms(self):
        a, _t, _d = make_answerer(policy_overrides={"diplomacy": "propose"})
        choice = a._pick_dialogue_choice({
            "type": "proposal_confirm", "dialogue_id": 9,
            "options": [{"action": "execute_proposal", "enabled": True},
                        {"action": "cancel_proposal"}]})
        # The literal is the archived, WORKING answer: the endpoint's own
        # keyword router resolves "confirm" to the execute option.
        assert choice == "confirm"

    def test_the_generic_scan_never_returns_a_disabled_accept(self):
        a, _t, _d = make_answerer(policy_overrides={"diplomacy": "accept"})
        choice = a._pick_dialogue_choice({
            "type": "x", "dialogue_id": 11,
            "options": [{"action": "accept_settlement_offer", "enabled": False, "description": "no"},
                        {"action": "decline_offer"}]})
        assert choice != "accept_settlement_offer"

    def test_the_dialogue_arm_leaves_a_disabled_surface_standing_with_its_reason(self):
        a, t, d = make_answerer(policy_overrides={"diplomacy": "propose"})
        a.scan({"diplomatic_dialogue": {
            "type": "proposal_confirm", "dialogue_id": 9,
            "options": [{"action": "execute_proposal", "enabled": False, "description": "I cannot deliver this, Sire"}]}})
        assert not [p for p in t.posts if p[0] == "/respond_to_diplomatic_dialogue"]
        assert any("disabled" in str(p[2]) for p in d.popups), d.popups


    def test_an_all_disabled_list_records_the_first_options_reason(self):
        """78/c: no confirm-family id here, so the standing reason can come
        ONLY from the all-disabled arm — a decision whose every option the
        executor greyed (an unaffordable invest beside an unreachable
        garrison). The digest must say WHY it was left standing."""
        a, t, d = make_answerer(policy_overrides={"rebellion": "invest"})
        payload = {"type": "vassal_rebellion_imminent", "dialogue_id": 14,
                   "options": [{"action": "invest_vassal_rebellion", "enabled": False,
                                "description": "The treasury cannot bear it"},
                               {"action": "garrison_vassal_rebellion", "enabled": False,
                                "description": "No corps within reach"}]}
        assert a._pick_dialogue_choice(dict(payload)) is None
        assert a.last_standing_reason == "The treasury cannot bear it"
        a.scan({"diplomatic_dialogue": payload})
        assert not [p for p in t.posts if p[0] == "/respond_to_diplomatic_dialogue"]
        assert any("treasury cannot bear" in str(p[2]) for p in d.popups), d.popups


# ═══════════════════════════════════════════════════════════════════════
# FA-79 — the redemption default does not destroy the marshal; replies are logged
# ═══════════════════════════════════════════════════════════════════════

class TestFA79TheRedemptionAndPetitionArms:

    def test_the_default_is_the_self_expiring_arm(self):
        assert driver.POLICY_DEFAULTS["redemption"] == "grant_autonomy"

    def test_the_redemption_reply_is_written_to_the_digest(self):
        a, t, d = make_answerer(replies={"/respond_to_redemption": {
            "success": False, "message": "That is not among the courses open to you, Sire. Ney awaits one of: grant_autonomy."}})
        a.scan({"redemption_event": {"marshal": "Ney", "trust": 9}})
        assert any("refused" in n and "grant_autonomy" in n for n in d.notes), d.notes

    def test_the_petition_reply_is_written_to_the_digest(self):
        a, t, d = make_answerer(replies={"/marshal_petition_response": {
            "success": True, "message": "Ney accepts the Emperor's word."}})
        a.scan({"marshal_petition": {"marshal": "Ney", "kind": "jealousy_confrontation",
                                     "options": [{"id": "acknowledge", "enabled": True}]}})
        assert any("Ney accepts" in n for n in d.notes), d.notes

    def test_rotate_cycles_the_enabled_arms_per_kind(self):
        a, t, d = make_answerer(policy_overrides={"petition": "rotate"})
        payload = {"marshal": "Ney", "kind": "jealousy_confrontation",
                   "options": [{"id": "acknowledge", "enabled": True},
                               {"id": "promise", "enabled": True, "ap_cost": 1},
                               {"id": "rebuke", "enabled": True}]}
        picks = []
        for _ in range(4):
            a.scan({"marshal_petition": dict(payload)})
            picks.append(t.posts[-1][1]["choice"])
        assert picks == ["acknowledge", "promise", "rebuke", "acknowledge"]

    def test_first_enabled_stays_the_default(self):
        assert driver.POLICY_DEFAULTS["petition"] == "first_enabled"


# ═══════════════════════════════════════════════════════════════════════
# FA-N35 — the three blocking decisions are answered like the client answers them
# ═══════════════════════════════════════════════════════════════════════

class TestFAN35TheThreeDecisionsAreAnswered:

    def test_the_three_keys_left_the_display_only_set(self):
        for key in ("diplomatic_sabotage", "vassal_rebellion_imminent", "commitment_paradox_popup"):
            assert key not in driver.DISPLAY_ONLY_KEYS, key
        for key in ("battle_diorama", "nation_proclamation"):
            assert key in driver.DISPLAY_ONLY_KEYS, key

    def test_a_rebellion_popup_is_answered_with_its_dialogue_id(self):
        a, t, d = make_answerer()
        a.scan({"vassal_rebellion_imminent": {"nation": "Holland", "loyalty": 9, "dialogue_id": 21}})
        posts = [p for p in t.posts if p[0] == "/respond_to_diplomatic_dialogue"]
        assert len(posts) == 1
        assert posts[0][1] == {"choice": "accept_vassal_rebellion", "dialogue_id": 21}

    def test_the_rebellion_policy_dial(self):
        a, t, d = make_answerer(policy_overrides={"rebellion": "invest"})
        a.scan({"vassal_rebellion_imminent": {"nation": "Holland", "loyalty": 9, "dialogue_id": 21}})
        assert t.posts[-1][1]["choice"] == "invest_vassal_rebellion"

    def test_a_popup_beside_its_dialogue_is_answered_once(self):
        """The paradox rides as BOTH `diplomatic_dialogue` and the popup key
        with the same id (measured) — one answer per chain."""
        a, t, d = make_answerer()
        a.scan({"diplomatic_dialogue": dict(PARADOX),
                "commitment_paradox_popup": {"attacker": "Prussia", "defender": "Austria", "dialogue_id": 7}})
        posts = [p for p in t.posts if p[0] == "/respond_to_diplomatic_dialogue"]
        assert len(posts) == 1, posts
        assert posts[0][1]["dialogue_id"] == 7


    def test_the_popup_passthrough_on_the_answers_own_reply_is_not_answered_again(self):
        """N35/c: the dialogue arm answers FIRST; the reply it gets back
        carries the popup passthrough with the SAME id (`build_base_response`
        stamps every popup on every POST). Same chain — the popup arm must
        recognise the id, or the paradox is answered twice per chain."""
        a, t, d = make_answerer()
        a.scan({"diplomatic_dialogue": dict(PARADOX)})
        a.scan({"commitment_paradox_popup": {"attacker": "Prussia", "defender": "Austria",
                                             "dialogue_id": 7}})
        posts = [p for p in t.posts if p[0] == "/respond_to_diplomatic_dialogue"]
        assert len(posts) == 1, posts
        assert any("already answered" in str(p[2]) for p in d.popups), d.popups

    def test_the_sabotage_confrontation_is_answered(self):
        a, t, d = make_answerer()
        a.scan({"diplomatic_sabotage": {"target_nation": "Prussia", "defiance_type": "softened", "dialogue_id": 5}})
        assert t.posts[-1] == ("/respond_to_diplomatic_dialogue", {"choice": "confront_sabotage", "dialogue_id": 5})

    def test_a_popup_without_an_id_is_left_standing_and_said(self):
        a, t, d = make_answerer()
        a.scan({"vassal_rebellion_imminent": {"nation": "Holland", "loyalty": 9}})
        assert not [p for p in t.posts if p[0] == "/respond_to_diplomatic_dialogue"]
        assert any("left standing" in str(p[2]) for p in d.popups)


# ═══════════════════════════════════════════════════════════════════════
# FA-75 — the mailbox is read whole, and what lapsed is written down
# ═══════════════════════════════════════════════════════════════════════

class TestFA75TheMailboxIsReadWhole:

    def test_major_court_items_are_activated_and_drained(self):
        gets = {"/mailbox": {"items": [
            {"mailbox_id": 8, "from_nation": "Britain", "proposal_type": "settlement_offer"},
            {"mailbox_id": 9, "from_nation": "Prussia", "proposal_type": "open_borders"},
        ], "envoy_digest": {"items": [{"mailbox_id": 9, "from_nation": "Prussia"}]}}}
        a, t, d = make_answerer(gets=gets, replies={
            "/mailbox/activate": {"success": True, "dialogue_type": "incoming_settlement_offer",
                                  "incoming_settlement_offer": {"dialogue_id": 8, "from_nation": "Britain",
                                                                "proposal_type": "settlement_offer"}}})
        replies = a.answer_mailbox_items(gets["/mailbox"], answered_ids={9})
        activations = [p for p in t.posts if p[0] == "/mailbox/activate"]
        assert [p[1]["mailbox_id"] for p in activations] == [8], "only the item the letter-book did NOT answer"
        assert replies and replies[0].get("incoming_settlement_offer")

    def test_the_lapsed_offers_and_waiting_envoys_are_digested(self):
        out = []
        class D(StubDigest):
            pass
        d = D()
        driver.Digest.envoy_state(d, [{"nation": "Prussia", "proposal_type": "open borders"}],
                                  [{"nation": "Ottoman", "proposal_type": "friendly gift", "status": "WAITING"}], 1)
        text = "\n".join(d.md_lines)
        assert "LAPSED" in text and "Prussia" in text and "open borders" in text
        assert "ENVOYS" in text and "Ottoman" in text

    def test_nothing_lapsed_writes_nothing(self):
        d = StubDigest()
        driver.Digest.envoy_state(d, [], [], 0)
        assert d.md_lines == []


    def test_the_run_loop_activates_the_mailbox_every_turn(self, monkeypatch, tmp_path):
        """75/c: the B-half is a LOOP step, not only a method. One driven
        turn on a stub transport must POST /mailbox/activate for the item
        the letter-book did not answer (8), and not for the one it did (9)."""
        gets = {
            "/status": {"turn": 1},
            "/mailbox": {"items": [
                {"mailbox_id": 8, "source_nation": "Britain", "item_type": "settlement_offer"},
                {"mailbox_id": 9, "source_nation": "Prussia", "item_type": "open_borders"}],
                "envoy_digest": {"items": [
                    {"mailbox_id": 9, "from_nation": "Prussia", "proposal_type": "open_borders",
                     "summary": "Prussia asks for open borders"}]}},
        }

        class RunStub(StubTransport):
            label = "stub"

        transport = RunStub(replies={"/new_game": {"success": True, "message": "ok"}}, gets=gets)
        monkeypatch.setattr(driver, "make_inprocess_transport", lambda args, out_dir: transport)
        args = argparse.Namespace(
            script=None, name="mailbox_loop", seed="historical", llm="mock", scenario="",
            out=str(tmp_path), fresh=False, objection="", diplomacy="", redemption="",
            petition="", paradox="", rebellion="", sabotage="", reward="", last_stand="",
            contact="", http=False, strict=False, turns=1, save_at="", from_save="",
            cheats=False, reload_every=0, verbose=False, archive=False)
        rc = driver.run(args)
        activations = [p[1]["mailbox_id"] for p in transport.posts if p[0] == "/mailbox/activate"]
        assert activations == [8], (rc, transport.posts)


# ═══════════════════════════════════════════════════════════════════════
# FA-85 / FA-89 / FA-90 / FA-102 — the run says what it could not do
# ═══════════════════════════════════════════════════════════════════════

class TestTheRunSaysWhatItCouldNotDo:

    def test_the_naval_script_stages_at_a_yard_outside_the_camp(self):
        """FA-85 (part f) staged Soult at Bordelais; FA-S17-4 (Phase 3, Sept 11,
        2026) found no boot French corps is under the 15,000-man lift, so the
        script now follows the lift counsel's own marshalate road: commission
        Oudinot (a 5,000-man corps) and stage HIM at the Atlantic yard."""
        script = json.loads((REPO_ROOT / "tools" / "playtest_scripts" / "naval_descent.json").read_text(encoding="utf-8"))
        assert "commission Oudinot" in script["turns"]["3"]
        assert "Oudinot, march to Bordelais" in script["turns"]["4"]
        assert any(x.startswith("land Oudinot in Munster") for turn in script["turns"].values() for x in turn)
        assert not any("Soult" in x and ("Bordelais" in x or "Munster" in x) for turn in script["turns"].values() for x in turn)
        assert not any("Normandy" in x and "Soult" in x for turn in script["turns"].values() for x in turn)

    def test_every_expedition_line_refused_is_a_script_precondition(self):
        d = StubDigest()
        tracker = driver.ExpeditionTracker()
        tracker.observe("land Soult in Munster with 12,000 men", {"success": False, "message": "An expedition assembles at a dockyard"})
        tracker.observe("land Soult in Munster confirmed", {"success": False, "message": "…"})
        tracker.observe("Ney, march to London", {"success": True})
        assert tracker.precondition_failed() is True
        tracker.report(d)
        assert any("SCRIPT PRECONDITION" in n for n in d.notes)

    def test_one_expedition_that_ran_clears_the_precondition(self):
        tracker = driver.ExpeditionTracker()
        tracker.observe("land Soult in Munster with 12,000 men", {"success": False})
        tracker.observe("land Soult in Munster confirmed", {"success": True, "message": "The transports lift…"})
        assert tracker.precondition_failed() is False

    def test_a_script_with_no_expedition_lines_has_no_precondition(self):
        tracker = driver.ExpeditionTracker()
        tracker.observe("Ney, attack Mack", {"success": True})
        assert tracker.precondition_failed() is False

    def test_the_ratification_summary_reaches_the_digest(self):
        d = StubDigest()
        driver.Digest.ratified(d, {"summary": "Peace with Austria: Swabia ceded; 500 gold."})
        assert any("RATIFIED" in ln and "Swabia" in ln for ln in d.md_lines)

    def test_the_school_step_reaches_the_digest(self):
        d = StubDigest()
        driver.Digest.school_step(d, {"step": 4, "id": "first_blood", "title": "IV. First Blood", "approximate": True})
        assert any("SCHOOL" in ln and "IV. First Blood" in ln for ln in d.md_lines)

    def test_the_reward_arm_types_the_rails_own_command(self):
        a, t, d = make_answerer(policy_overrides={"reward": "pay"})
        a.reward_from_rail({"notifications": [
            {"id": "n1", "type": "dotation_expectation", "details": {"action_command": "grant Ney a rente"}},
            {"id": "n2", "type": "supply_strain", "details": {}},
        ]})
        assert [p for p in t.posts if p[0] == "/command"] == [("/command", {"command": "grant Ney a rente"})]
        a.reward_from_rail({"notifications": [
            {"id": "n1", "type": "dotation_expectation", "details": {"action_command": "grant Ney a rente"}}]})
        assert len([p for p in t.posts if p[0] == "/command"]) == 1, "once per notification id"

    def test_the_reward_arm_is_off_by_default(self):
        assert driver.POLICY_DEFAULTS["reward"] == "ignore"
        a, t, d = make_answerer()
        a.reward_from_rail({"notifications": [
            {"id": "n1", "type": "dotation_expectation", "details": {"action_command": "grant Ney a rente"}}]})
        assert not [p for p in t.posts if p[0] == "/command"]

    def test_the_driver_revision_is_a_content_hash(self):
        rev = driver.driver_revision()
        src = (REPO_ROOT / "tools" / "playtest_driver.py").read_bytes()
        assert rev == hashlib.sha256(src).hexdigest()[:12]

    def test_reload_round_trip_saves_then_loads_and_says_so(self):
        gets = {}
        a, t, d = make_answerer(replies={
            "/save": {"success": True, "message": "Saved"},
            "/load": {"success": True, "message": "Loaded", "pending_interrupt": {"marshal": "Ney", "interrupt_type": "last_stand",
                                                                                   "options": ["fight_to_the_last", "attempt_breakout"]}},
        })
        driver.reload_round_trip(t, d, a, "run", 7, strict=False)
        paths = [p[0] for p in t.posts]
        assert paths[:2] == ["/save", "/load"]
        assert t.posts[1][1]["filename"].endswith(".json")
        assert any("RELOAD" in n for n in d.notes)
        assert any("re-raised" in n for n in d.notes), "the questions the load re-raised are written down"
        assert "/strategic_response" in paths, "and drained through the ordinary arm"


# ═══════════════════════════════════════════════════════════════════════
# FA-89 — the backend mirror is drift-pinned to the overlay, and reaches the wire
# ═══════════════════════════════════════════════════════════════════════

class TestFA89TheSchoolStepIsApproximateAndOnTheWire:

    @staticmethod
    def _overlay_steps():
        import re
        src = (REPO_ROOT / "godot-client" / "project-sovereign" / "scripts"
               / "tutorial_overlay.gd").read_text(encoding="utf-8")
        i = src.index("const STEPS")
        j = src.index("\n]", i)
        rows = []
        for block in src[i:j].split("\n\t{")[1:]:
            sid = re.search(r'"id":\s*"([a-z_]+)"', block).group(1)
            gate = int(re.search(r'"turn_gate":\s*(\d+)', block).group(1))
            title = re.search(r'"title":\s*"([^"]+)"', block).group(1)
            rows.append((sid, gate, title))
        return rows

    def test_the_mirror_matches_the_overlay_exactly(self):
        from backend.game_logic import tutorial_state as T
        assert T.STEPS == self._overlay_steps(), "tutorial_state.STEPS drifted from tutorial_overlay.gd"

    def _retired_test_the_drift_pin_is_sensitive(self):
        # Review round (L3-11): retired — `T.STEPS[:1] != rows[1:2]` only said
        # two different rows differ; the real sensitivity is the sweep's 89/a.
        from backend.game_logic import tutorial_state as T
        rows = self._overlay_steps()
        assert len(rows) == 15 and rows[5][0] == "bombardment"
        assert T.STEPS[:1] != rows[1:2], "the census can tell two different rows apart"

    def test_the_step_is_the_latest_gate_reached_and_says_it_is_approximate(self):
        from backend.game_logic import tutorial_state as T

        class W:
            scenario_name = "tutorial"
            current_turn = 6
        step = T.tutorial_step_for(W())
        assert step["id"] == "capture_answer" and step["step"] == 10
        assert step["approximate"] is True
        W.current_turn = 1
        assert T.tutorial_step_for(W())["id"] == "first_end_turn"
        W.current_turn = 40
        assert T.tutorial_step_for(W())["id"] == "handoff"

    def test_off_the_tutorial_there_is_no_key(self):
        from backend.game_logic import tutorial_state as T

        class W:
            scenario_name = ""
            current_turn = 6
        assert T.tutorial_step_for(W()) is None

    def test_the_key_rides_a_real_tutorial_response_and_no_campaign_response(self, monkeypatch, tmp_path):
        import contextlib
        import io
        from fastapi.testclient import TestClient
        import backend.main as M
        from backend import save_manager
        from backend.commands.parser import CommandParser
        from backend.models.world_state import WorldState
        maps = REPO_ROOT / "godot-client" / "project-sovereign" / "assets" / "maps"
        monkeypatch.setenv("INK_IRON_SAVE_DIR", str(tmp_path / "saves"))
        monkeypatch.setattr(save_manager, "SAVE_DIR", tmp_path / "saves")
        for scenario, expect in (("tutorial_1805.json", True), ("europe_1805.json", False)):
            with contextlib.redirect_stdout(io.StringIO()):
                world = WorldState.from_scenario(str(maps / scenario))
            monkeypatch.setattr(M, "world", world)
            monkeypatch.setattr(M, "game_state", {"world": world})
            monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
            with contextlib.redirect_stdout(io.StringIO()):
                r = TestClient(M.app).post("/command", json={"command": "status"}).json()
            assert ("tutorial_step" in r) is expect, (scenario, r.get("tutorial_step"))
            if expect:
                assert r["tutorial_step"]["approximate"] is True
                assert r["tutorial_step"]["step"] == 3
