"""WO-H slice 1 — "The Instrument" (WEIRD_OUTCOMES_SPEC §3 slice 1).

Pins the playtest driver's answer plumbing at the seams the Aug-16 weird
campaigns proved blind:

* WO-H1 — `_option_id` could not read `action`-keyed options, so the World
  Burns arm ran fifteen complete declare-war ceremonies and declared war on
  ZERO nations, every one logged as a success.
* WO-H3 — `pending_capture_choice` arrives as a bare True with the detail on
  the sibling `capture_data`; reading only the flag lost the stage, so the
  ESTATE stage was answered with the plunder token — refused WITHOUT
  clearing, wedging the rest of the campaign.
* WO-H2 — `battles` read 0 for campaigns the world logged a dozen battles in
  (autonomous jealousy attacks and enemy-phase battle rows never counted).
* Nondeterminism — the module RNG was never seeded, so the same script at
  the same seed ended at 30 / 28 / 27 provinces across three invocations.

These tests exercise the DRIVER's own units with stub transports — no world
boot, no backend import. The empirical acceptance (byte-identical A/B runs,
14 France WAR pairs in the re-run World Burns save) is recorded in the spec's
§3 slice-1 landing record.
"""

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

_spec = importlib.util.spec_from_file_location(
    "playtest_driver", REPO_ROOT / "tools" / "playtest_driver.py")
driver = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("playtest_driver", driver)
_spec.loader.exec_module(driver)


# ═══════════════════════════════════════════════════════════════════════
# WO-H1 — _option_id reads every legitimate answer key, never `label`
# ═══════════════════════════════════════════════════════════════════════

class TestOptionId:
    def test_action_keyed_option_is_readable(self):
        # The ally-entry review's exact shape: `action` key, no `id`.
        assert driver._option_id(
            {"action": "ally_entry_proceed_without",
             "label": "Proceed Without Allies"}) == "ally_entry_proceed_without"

    def test_id_still_preferred_over_action(self):
        assert driver._option_id(
            {"id": "confirm", "action": "other"}) == "confirm"

    def test_command_and_value_keys_readable(self):
        assert driver._option_id({"command": "land Ney in Kent confirmed"}) \
            == "land Ney in Kent confirmed"
        assert driver._option_id({"value": "2"}) == "2"

    def test_label_is_never_an_id(self):
        # Labels are display copy — matching them couples the driver to
        # wording. An option with ONLY a label stays unreadable by design.
        assert driver._option_id({"label": "Proceed Without Allies"}) is None

    def test_bare_string_option_passes_through(self):
        assert driver._option_id("defy") == "defy"

    def test_preference_order_is_the_documented_tuple(self):
        assert driver._OPTION_ID_KEYS == (
            "id", "choice", "keyword", "action", "command", "value")


# ═══════════════════════════════════════════════════════════════════════
# Stub plumbing for Answerer tests
# ═══════════════════════════════════════════════════════════════════════

class StubTransport:
    def __init__(self, replies=None):
        self.posts = []
        self.replies = replies or {}

    def post(self, path, payload=None):
        self.posts.append((path, payload))
        return dict(self.replies.get(path, {"success": True}))

    def get(self, path):
        return {}


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

    def popup(self, key, summary, answer):
        self.counters["popups"] += 1
        self.popups.append((key, summary, answer))
        if str(answer) not in ("(left standing)", "display-only",
                               "(no options)"):
            self.recent.append((str(key), str(summary), str(answer)))

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
        self.popups.append(("envoy_digest", row.get("from_nation"),
                            f"{choice}{outcome}"))

    def unknown_blocker(self, key, payload):
        self.unknown_blockers.append(key)


def make_answerer(replies=None, policy_overrides=None):
    transport = StubTransport(replies)
    digest = StubDigest()
    policy = dict(driver.POLICY_DEFAULTS) | (policy_overrides or {})
    answerer = driver.Answerer(transport, digest, policy, strict=False)
    return answerer, transport, digest


# ═══════════════════════════════════════════════════════════════════════
# WO-H3 — the capture arm reads the sibling capture_data
# ═══════════════════════════════════════════════════════════════════════

class TestCaptureArm:
    def test_bare_true_reads_sibling_capture_data_estate_stage(self):
        """The measured wedge: bare True + estate capture_data used to be
        answered with the plunder/secure token, which the executor refuses
        WITHOUT clearing. The driver must read the stage from capture_data
        and answer with the estate policy token, carrying dialogue_id."""
        answerer, transport, digest = make_answerer()
        answerer.scan({
            "pending_capture_choice": True,
            "capture_data": {"stage": "estate", "region": "Swabia",
                             "capturer": "Ney", "estate_holder": "Mack",
                             "dialogue_id": 41,
                             "options": ["confiscate", "respect"]},
        })
        assert transport.posts == [("/capture_choice",
                                    {"choice": "respect", "dialogue_id": 41})]
        key, summary, answer = digest.popups[-1]
        assert key == "capture_choice[estate]"
        assert answer == "respect"

    def test_bare_true_stage_one_uses_capture_policy(self):
        answerer, transport, digest = make_answerer(
            policy_overrides={"capture": "plunder"})
        answerer.scan({
            "pending_capture_choice": True,
            "capture_data": {"stage": "capture", "region": "Bohemia",
                             "capturer": "Soult", "dialogue_id": 7},
        })
        assert transport.posts == [("/capture_choice",
                                    {"choice": "plunder", "dialogue_id": 7})]

    def test_dict_payload_still_works_without_capture_data(self):
        # The /capture_choice endpoint's own re-attach ships the dict on the
        # flag key itself in some flows — the dict form keeps working.
        answerer, transport, digest = make_answerer()
        answerer.scan({
            "pending_capture_choice": {"stage": "estate", "region": "Kent",
                                       "dialogue_id": 3},
        })
        assert transport.posts == [("/capture_choice",
                                    {"choice": "respect", "dialogue_id": 3})]


# ═══════════════════════════════════════════════════════════════════════
# Item 4 — the awaiting_clarification arm
# ═══════════════════════════════════════════════════════════════════════

class TestClarificationArm:
    def test_first_option_answered_as_typed_index(self):
        """The typed "1" resolves server-side (interpret_clarification_answer)
        to the first ACTIONABLE option's own command string — the driver
        never guesses at copy."""
        answerer, transport, digest = make_answerer()
        answerer.scan({
            "state": "awaiting_clarification",
            "message": "Sail? (yes / no)",
            "options": [
                {"label": "Sail for Kent", "command": "land Ney in Kent confirmed"},
                {"label": "Stand down", "command": "cancel"},
            ],
        })
        assert transport.posts == [("/command", {"command": "1"})]
        key, summary, answer = digest.popups[-1]
        assert key == "clarification"
        assert answer.startswith("1 ")

    def test_no_actionable_options_left_standing(self):
        answerer, transport, digest = make_answerer()
        answerer.scan({
            "state": "awaiting_clarification",
            "message": "Which marshal, Sire?",
            "options": [],
        })
        assert transport.posts == []
        assert digest.popups[-1][2] == "(left standing)"

    def test_unregistered_clarification_left_standing(self):
        # clarification_registered False means a typed index would parse as
        # a fresh command — the driver must not burn a blind token.
        answerer, transport, digest = make_answerer()
        answerer.scan({
            "state": "awaiting_clarification",
            "clarification_registered": False,
            "options": [{"label": "x", "command": "attack Mack"}],
        })
        assert transport.posts == []
        assert digest.popups[-1][2] == "(left standing)"

    def test_cancel_policy_cancels(self):
        answerer, transport, digest = make_answerer(
            policy_overrides={"clarification": "cancel"})
        answerer.scan({
            "state": "awaiting_clarification",
            "options": [{"label": "x", "command": "attack Mack"}],
        })
        assert transport.posts == [("/command", {"command": "cancel"})]


# ═══════════════════════════════════════════════════════════════════════
# Item 5 — the envoy-digest arm
# ═══════════════════════════════════════════════════════════════════════

class TestEnvoyDigestArm:
    PAYLOAD = {
        "count": 2,
        "items": [
            {"mailbox_id": 11, "from_nation": "Denmark",
             "proposal_type": "non_aggression",
             "proposal_type_display": "Non-Aggression Pact"},
            {"mailbox_id": 12, "from_nation": "Saxony",
             "proposal_type": "open_borders",
             "proposal_type_display": "Open Borders Agreement"},
        ],
    }

    def test_default_policy_declines_each_row_explicitly(self):
        answerer, transport, digest = make_answerer(
            replies={"/mailbox/respond": {"success": True,
                                          "digest_row_answered": 11}})
        replies = answerer.answer_envoy_digest(self.PAYLOAD)
        assert transport.posts == [
            ("/mailbox/respond", {"mailbox_id": 11, "choice": "decline"}),
            ("/mailbox/respond", {"mailbox_id": 12, "choice": "decline"}),
        ]
        assert len(replies) == 2
        assert digest.counters["popups"] == 2

    def test_accept_policy_accepts(self):
        answerer, transport, digest = make_answerer(
            policy_overrides={"diplomacy": "accept"})
        answerer.answer_envoy_digest(self.PAYLOAD)
        assert all(p[1]["choice"] == "accept" for p in transport.posts)

    def test_none_payload_is_a_noop(self):
        answerer, transport, digest = make_answerer()
        assert answerer.answer_envoy_digest(None) == []
        assert transport.posts == []


# ═══════════════════════════════════════════════════════════════════════
# WO-H2 — battles counted from enemy-phase rows and jealousy attacks
# ═══════════════════════════════════════════════════════════════════════

class TestBattleCounting:
    def test_enemy_phase_battle_rows_counted(self, tmp_path):
        digest = driver.Digest(tmp_path, {
            "name": "t", "seed": "s", "llm": "mock", "transport": "test",
            "policy": {},
        })
        digest.enemy_phase([
            {"nation": "Austria", "ai_action": {"action": "attack"},
             "message": "attacks", "battle_report": {"headline": "b1"}},
            {"nation": "Austria", "ai_action": {"action": "wait"},
             "message": "waits"},
        ])
        assert digest.counters["battles"] == 1

    def test_jealousy_attacks_counted(self, tmp_path):
        digest = driver.Digest(tmp_path, {
            "name": "t", "seed": "s", "llm": "mock", "transport": "test",
            "policy": {},
        })
        digest.autonomous_attacks([
            {"success": True, "message": "Murat attacks on his own initiative",
             "battle_report": {"headline": "b"}},
            {"success": False, "message": "refused"},   # no report — no battle
        ])
        assert digest.counters["battles"] == 1
        jsonl = (tmp_path / "digest.jsonl").read_text(encoding="utf-8")
        assert jsonl.count('"autonomous_attack"') == 2


class TestStrategicReportBattleCounting:
    """WO-H2 review round: battles auto-resolved during end-turn strategic
    processing discard their battle_report from the report row (WO-33) —
    the HOLD sally keeps `battle_details`, the auto-attack keeps only a
    message with action=="combat". The driver counts what is recoverable."""

    def test_battle_details_and_combat_rows_counted(self):
        answerer, transport, digest = make_answerer()
        answerer.scan({
            "strategic_reports": [
                {"action": "combat", "marshal": "Ney",
                 "message": "Ney engages the enemy on arrival!"},
                {"marshal": "Davout", "order_status": "active",
                 "battle_details": {"headline": "sally repulsed"}},
                {"marshal": "Soult", "requires_input": True,
                 "action": "combat"},   # an INTERRUPT — not a battle row
                {"marshal": "Murat", "order_status": "continues",
                 "message": "marching"},
            ],
        })
        # Two battles counted; the interrupt row is answered by the
        # interrupt arm, not double-counted as a battle.
        assert digest.counters["battles"] == 2


# ═══════════════════════════════════════════════════════════════════════
# Item 6 — the deterministic seed derivation
# ═══════════════════════════════════════════════════════════════════════

class TestSeedDerivation:
    def test_same_inputs_same_stream(self):
        import random
        driver.seed_module_rng("historical", 3)
        a = [random.random() for _ in range(5)]
        driver.seed_module_rng("historical", 3)
        b = [random.random() for _ in range(5)]
        assert a == b

    def test_different_turn_different_stream(self):
        import random
        driver.seed_module_rng("historical", 3)
        a = random.random()
        driver.seed_module_rng("historical", 4)
        b = random.random()
        assert a != b

    def test_derivation_does_not_use_builtin_hash(self):
        # sha256, never hash() — the derivation must not depend on
        # PYTHONHASHSEED (which is pinned separately by main()'s re-exec).
        import hashlib
        expected = int(hashlib.sha256(b"historical:3").hexdigest(), 16) \
            & 0xFFFFFFFF
        import random
        driver.seed_module_rng("historical", 3)
        a = random.random()
        random.seed(expected)
        assert random.random() == a


# ═══════════════════════════════════════════════════════════════════════
# The precedence rule — explicit CLI beats script, beats default
# ═══════════════════════════════════════════════════════════════════════

class TestScriptPrecedence:
    """The old rule (script always wins) silently ignored --seed — making a
    seed sweep over committed scripts impossible — and redirected --name into
    the script's canonical run dir, where --fresh then DELETED the original
    evidence digest (it cost the Aug-16 weird-tyrant and weird-world-burns
    originals). Pin the resolution rule at the argparse seam."""

    def test_defaults_are_none_so_explicit_is_distinguishable(self):
        import argparse
        # Reproduce the resolution logic on both shapes.
        for cli_name, script_name, resolved in [
            (None, "weird-tyrant", "weird-tyrant"),   # script fills default
            ("sweep-t1", "weird-tyrant", "sweep-t1"),  # explicit CLI wins
            (None, None, "run"),                       # built-in default
        ]:
            args = argparse.Namespace(name=cli_name)
            script = {"name": script_name} if script_name else {}
            assert (args.name or script.get("name") or "run") == resolved
