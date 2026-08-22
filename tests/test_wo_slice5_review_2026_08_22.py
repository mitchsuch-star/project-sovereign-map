"""WO slice 5 — the August 22, 2026 review round.

Landing record: `docs/WEIRD_OUTCOMES_SPEC.md` §3 slice 5, the review-round
addendum. Each class below pins one thing the review MEASURED and fixed;
the slice's own file (`test_wo_slice5_berthier_names_the_peace.py`) keeps
the original contract and carries the two consciously flipped pins.

The three headline defects, all reproduced before a line was written:

1. The driver's bare-shape dialogue arm answered an **ultimatum** with the
   diplomacy policy. Measured end to end on the real endpoints: under
   `accept|first|propose` France YIELDED — Hanover ceded to Prussia, 300g
   a turn, 5,000 conscripts — silently overriding the `ultimatum: defy`
   policy the run's own `meta.json` records.
2. `--diplomacy propose` ended `blocked` on 3 of 7 seeds. The arm spends
   3 DP a turn; an incoming `settlement_confirm`'s first option costs DP
   France no longer has; the executor refuses WITHOUT popping; the driver
   re-sent the same word forever. Reproduced at seed `ulm` (blocked at
   turn 11 of 18); the run completes after the fix.
3. The war room named a court whose plain peace the game's own scorer
   REFUSED while a mutually exhausted court inside the same collapsed row
   would have signed — 7 of 13 snapshots across three seeds.
"""

import importlib.util
import io
import json
import sys
from pathlib import Path

import pytest

from backend.game_logic import diplomatic_advisory as adv
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCENARIO_PATH = (
    REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
    / "europe_1805.json"
)

_spec = importlib.util.spec_from_file_location(
    "playtest_driver_review", REPO / "tools" / "playtest_driver.py")
driver = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("playtest_driver_review", driver)
_spec.loader.exec_module(driver)


@pytest.fixture(scope="module")
def world1805():
    return WorldState.from_scenario(str(SCENARIO_PATH))


@pytest.fixture
def world(world1805):
    return WorldState.from_dict(world1805.to_dict())


# ═══════════════════════════════════════════════════════════════════════
# THE DRIVER
# ═══════════════════════════════════════════════════════════════════════

class _Transport:
    label = "stub"

    def __init__(self):
        self.posts = []
        self.replies = []
        self.echo = None

    def post(self, path, body=None):
        self.posts.append((path, dict(body or {})))
        if self.replies:
            return self.replies.pop(0)
        if self.echo is not None:
            served, self.echo = self.echo, None
            return served
        return {}

    def get(self, path):
        return {}


def _answerer(mode="propose", **policy_overrides):
    """A real Answerer over a stub transport, with a REAL digest.popup.

    The slice's own fixture stubbed `popup` out, which made
    `digest.recent` — the only thing drain()'s cycle guard reads — always
    empty, so its `assert not notes` could not fail. Here the popup writes
    the signature trail for real.
    """
    digest = driver.Digest.__new__(driver.Digest)
    digest.counters = {"popups": 0}
    digest.recent = []
    digest.unknown_blockers = []
    digest.notes = []
    digest.note = digest.notes.append
    digest.record = lambda *a, **k: None
    digest.logged = []
    digest._md = digest.logged.append
    transport = _Transport()
    policy = dict(driver.POLICY_DEFAULTS, diplomacy=mode, **policy_overrides)
    return driver.Answerer(transport, digest, policy, False), transport


_ULTIMATUM_POPUP = {
    "from_nation": "Prussia",
    "proposal_type": "ultimatum_demand",
    "is_ultimatum": True,
    "dialogue_id": 1,
}
_PEACE_POPUP = {
    "from_nation": "Russia", "proposal_type": "peace", "dialogue_id": 2,
}


class TestTheUltimatumIsAnsweredByTheUltimatumPolicy:
    """The confirmed P1. `main.py`'s incoming_proposal safety valve and the
    popup queue BOTH render a pending `incoming_ultimatum` through
    `mailbox_payloads.build_pending_envoy_popup_from_terms`, which stamps
    neither a `type` key nor an options list — so the bare-shape arm could
    not tell an ultimatum from a peace offer."""

    @pytest.mark.parametrize("mode", ["decline", "accept", "first", "propose"])
    def test_every_diplomacy_mode_defies_by_default(self, mode):
        answerer, _ = _answerer(mode)
        assert answerer._dialogue_choice(dict(_ULTIMATUM_POPUP)) == "defy"

    def test_an_explicit_yield_policy_is_honoured(self):
        answerer, _ = _answerer("propose", ultimatum="yield")
        assert answerer._dialogue_choice(dict(_ULTIMATUM_POPUP)) == "yield"

    def test_the_terms_type_alone_is_enough(self):
        """Belt and braces: `is_ultimatum` rides the producer's own payload,
        but the fallback builder (`_build_pending_envoy_popup_from_terms`)
        does not stamp it, so the terms type is read too."""
        answerer, _ = _answerer("accept")
        payload = dict(_ULTIMATUM_POPUP)
        payload.pop("is_ultimatum")
        assert answerer._dialogue_choice(payload) == "defy"

    def test_a_peace_offer_is_untouched(self):
        for mode, expected in (("propose", "accept"), ("accept", "accept"),
                               ("first", "accept"), ("decline", "reject")):
            answerer, _ = _answerer(mode)
            assert answerer._dialogue_choice(dict(_PEACE_POPUP)) == expected

    def test_a_counter_offer_is_untouched(self):
        answerer, _ = _answerer("propose")
        payload = dict(_PEACE_POPUP, is_counter_offer=True, dialogue_id=3)
        assert answerer._dialogue_choice(payload) == "accept"

    def test_defy_and_yield_are_the_routers_own_exclusive_words(self):
        from backend.commands.dialogue_routing import DIALOGUE_ACTION_KEYWORDS
        assert DIALOGUE_ACTION_KEYWORDS["defy"] == ["reject_ai_ultimatum"]
        assert DIALOGUE_ACTION_KEYWORDS["yield"] == ["accept_ai_ultimatum"]
        # ...and the words the old arm used resolve to the ULTIMATUM
        # actions too, which is exactly why the bypass had teeth.
        assert "accept_ai_ultimatum" in DIALOGUE_ACTION_KEYWORDS["accept"]
        assert "reject_ai_ultimatum" in DIALOGUE_ACTION_KEYWORDS["reject"]

    def test_the_policy_default_is_defy(self):
        assert driver.POLICY_DEFAULTS["ultimatum"] == "defy"


class TestARefusedChoiceIsNeverRepeated:
    """The `--diplomacy propose` wedge: `blocked` on 3 of 7 seeds."""

    CHOOSER = {
        "type": "settlement_confirm", "dialogue_id": 9,
        "options": [{"id": "seek_bilateral_peace"},
                    {"id": "seek_armistice_instead"},
                    {"id": "open_war_detail"},
                    {"id": "back_out_settlement"}],
    }

    def test_the_next_option_is_tried_after_a_refusal(self):
        answerer, transport = _answerer("propose")
        transport.replies = [{"success": False,
                              "message": "Insufficient diplomatic points"}]
        answerer.begin_post()
        answerer.scan({"diplomatic_dialogue": dict(self.CHOOSER)})
        assert transport.posts[-1][1]["choice"] == "seek_bilateral_peace"
        answerer.begin_post()
        answerer.scan({"diplomatic_dialogue": dict(self.CHOOSER)})
        assert transport.posts[-1][1]["choice"] == "seek_armistice_instead"

    def test_the_memory_survives_the_chain_that_recorded_it(self):
        """Not a per-post guard: the wedge repeated across TURNS."""
        answerer, transport = _answerer("propose")
        for _ in range(3):
            transport.replies = [{"success": False}]
            answerer.begin_post()
            answerer.scan({"diplomatic_dialogue": dict(self.CHOOSER)})
        assert [p[1]["choice"] for p in transport.posts] == [
            "seek_bilateral_peace", "seek_armistice_instead", "open_war_detail"]

    def test_an_exhausted_option_list_is_left_standing_not_looped(self):
        answerer, transport = _answerer("propose")
        for _ in range(4):
            transport.replies = [{"success": False}]
            answerer.begin_post()
            answerer.scan({"diplomatic_dialogue": dict(self.CHOOSER)})
        before = len(transport.posts)
        answerer.begin_post()
        answerer.scan({"diplomatic_dialogue": dict(self.CHOOSER)})
        assert len(transport.posts) == before, "a fifth answer was sent"

    def test_a_successful_answer_is_not_remembered_as_refused(self):
        answerer, transport = _answerer("propose")
        transport.replies = [{"success": True}]
        answerer.begin_post()
        answerer.scan({"diplomatic_dialogue": dict(self.CHOOSER)})
        answerer.begin_post()
        answerer.scan({"diplomatic_dialogue": dict(self.CHOOSER)})
        assert [p[1]["choice"] for p in transport.posts] == [
            "seek_bilateral_peace", "seek_bilateral_peace"]

    def test_the_refusal_is_said_out_loud(self):
        """16 of 28 answers in the archived run were refused and the digest
        rendered them exactly like signed ones."""
        answerer, transport = _answerer("propose")
        transport.replies = [{"success": False,
                              "message": "Insufficient diplomatic points."}]
        answerer.begin_post()
        answerer.scan({"diplomatic_dialogue": dict(self.CHOOSER)})
        assert any("refused" in n and "diplomatic points" in n
                   for n in answerer.d.notes), answerer.d.notes


class TestTheSkippedPassthroughIsVisibleAndNotACycle:
    STALE = {"type": "proposal_confirm", "dialogue_id": 7,
             "options": [{"id": "confirm"}]}

    def test_the_skip_is_logged(self):
        answerer, transport = _answerer("propose")
        answerer.begin_post()
        answerer.scan({"diplomatic_dialogue": dict(self.STALE)})
        answerer.scan({"diplomatic_dialogue": dict(self.STALE)})
        assert len(transport.posts) == 1
        assert any("stale passthrough" in line
                   for line in answerer.d.logged), answerer.d.logged

    def test_the_skip_does_not_feed_the_cycle_guard(self):
        """It re-created the false cycle the same review removed."""
        answerer, transport = _answerer("propose")
        answerer.begin_post()
        answerer.scan({"diplomatic_dialogue": dict(self.STALE)})
        answerer.scan({"diplomatic_dialogue": dict(self.STALE)})
        answerer.scan({"diplomatic_dialogue": dict(self.STALE)})
        answers = [sig for sig in answerer.d.recent]
        assert len(answers) == 1, answers

    def test_two_different_dialogues_are_not_a_cycle(self):
        """The legitimate five-stage settlement ceremony ends in two
        DIFFERENT `proposal_confirm`s and tripped the guard every long
        propose run, because the signature could not tell them apart."""
        answerer, _ = _answerer("propose")
        answerer.begin_post()
        answerer.scan({"diplomatic_dialogue": dict(self.STALE, dialogue_id=7)})
        answerer.scan({"diplomatic_dialogue": dict(self.STALE, dialogue_id=8)})
        assert len(set(answerer.d.recent)) == 2, answerer.d.recent


class TestDriverHousekeeping:
    def test_the_accepting_modes_constant_owns_the_chooser_arm(self):
        """`first` is an accepting mode; taking the documented NO-OP `keep`
        under it restages the substitute."""
        chooser = {"type": "settlement_pair_substitute_confirm",
                   "options": [{"id": "confirm_pair_substitute"},
                               {"id": "keep_joint_settlement"}]}
        for mode in driver.ACCEPTING_DIPLOMACY_MODES:
            answerer, _ = _answerer(mode)
            assert answerer._dialogue_choice(dict(chooser)) \
                == "confirm_pair_substitute", mode
        answerer, _ = _answerer("decline")
        assert answerer._dialogue_choice(dict(chooser)) \
            == "keep_joint_settlement"

    def test_the_overture_is_sent_after_the_scripts_own_orders(self):
        """It costs 3 DP and Talleyrand's whole turn, so sending it first
        made a script's own diplomacy fail for want of points the harness
        had spent."""
        src = (REPO / "tools" / "playtest_driver.py").read_text(
            encoding="utf-8")
        loop = src.split("def run(")[1]
        script_at = loop.index("for text in turn_scripts.get(")
        overture_at = loop.index('if policy["diplomacy"] == "propose":')
        assert script_at < overture_at

    def test_the_builder_is_named_correctly(self):
        """The record and the driver comment both named a function that has
        never existed."""
        src = (REPO / "tools" / "playtest_driver.py").read_text(
            encoding="utf-8")
        assert "build_incoming_" not in src
        assert "build_pending_envoy_popup_from_terms" in src
        from backend.game_logic import mailbox_payloads
        assert hasattr(mailbox_payloads, "build_pending_envoy_popup_from_terms")
        assert not hasattr(mailbox_payloads, "build_incoming_proposal_popup")


# ═══════════════════════════════════════════════════════════════════════
# THE BACKEND — the carried dialogue's identity
# ═══════════════════════════════════════════════════════════════════════

class TestTheCarriedProposalCarriesItsIdentity:
    def test_replace_stamps_the_dict_that_is_returned(self):
        """W6-0: "every popup shape derived from a dialogue carries the
        identity the client must answer with". `replace(dict(x))` stamped a
        throwaway copy while the ORIGINAL went to the client, so the
        settlement -> bilateral `proposal_confirm` reached Godot with no
        `dialogue_id` at all."""
        src = (REPO / "backend" / "game_logic"
               / "settlement_actions.py").read_text(encoding="utf-8")
        assert "world.dialogue_manager.replace(dict(proposal_dialogue))" \
            not in src
        assert "world.dialogue_manager.replace(proposal_dialogue)" in src

    def test_the_manager_stamps_in_place(self, world):
        from backend.models.dialogue_manager import DialogueManager
        manager = DialogueManager()
        manager.push({"type": "settlement_confirm"})
        carried = {"type": "proposal_confirm", "target_nation": "Britain"}
        manager.pop()
        manager.replace(carried)
        assert carried.get("dialogue_id") is not None


class TestTheSmokePresetStampsTheWarClock:
    def test_multiwar_ambiguity_seeds_war_start_turns(self, monkeypatch):
        """The only one of six settlement smoke seeders that did not, which
        left every war-age reader looking at a war with no start."""
        monkeypatch.setenv("SOVEREIGN_SMOKE_START",
                           "settlement_multiwar_ambiguity")
        monkeypatch.delenv("SOVEREIGN_SCENARIO", raising=False)
        smoke = WorldState()
        at_war = [k for k, v in smoke.diplomatic_states.items() if v == "WAR"]
        assert at_war
        missing = [k for k in at_war if k not in (smoke.war_start_turns or {})]
        assert missing == [], missing


# ═══════════════════════════════════════════════════════════════════════
# THE COUNSEL
# ═══════════════════════════════════════════════════════════════════════

def _board(world, *, row_score, pair_scores, we=None, turn=30):
    world.current_turn = turn
    world.war_exhaustion = dict(we or {n: 200 for n in
                                list(pair_scores) + ["France"]})
    for court, score in pair_scores.items():
        key = world._make_diplo_key("France", court)
        world.diplomatic_states[key] = "WAR"
        world.war_start_turns[key] = 1
        first = key.split("|")[0]
        world.war_scores[key] = int(score if first == "France" else -score)
    world.invalidate_bloc_members_cache()
    return [{
        "status": "war",
        "opponent": list(pair_scores)[0],
        "opponents": list(pair_scores),
        "opponent_display": " + ".join(pair_scores),
        "war_score": row_score,
        "duration": turn - 1,
        "started_turn": 1,
        "request_terms_state": {"state": "absent"},
        "settlement_available": True,
    }]


class TestTheSignablePeaceIsNoLongerBuried:
    """Measured on real saves: 7 of 13 snapshots across three seeds named a
    court the scorer refused (21-28) while a stuck court in the same
    collapsed row would have signed (64-69)."""

    def test_a_stuck_signer_outranks_a_losing_leader_who_refuses(self, world):
        rows = _board(world, row_score=-82,
                      pair_scores={"Britain": -28, "Russia": 0})
        ranked = adv._settlement_candidates(world, "France", rows)
        by_name = {c["opponent"]: c for c in ranked}
        assert by_name["Britain"]["row_losing"] is True
        assert by_name["Russia"]["stuck"] is True
        assert by_name["Russia"]["acceptance"] > by_name["Britain"]["acceptance"]
        assert ranked[0]["opponent"] == "Russia"
        rec = adv._build_situation_recommendation(world, "France", rows, None,
                                                  "defensive")
        assert rec["target_nation"] == "Russia"

    def test_the_losing_leader_still_wins_when_it_would_sign(self, world):
        """Ranking, not a blanket demotion: a losing court the scorer likes
        keeps the rung."""
        rows = _board(world, row_score=-82,
                      pair_scores={"Britain": -28, "Russia": 0})
        ranked = adv._settlement_candidates(world, "France", rows)
        best_stuck = next(c for c in ranked if c["opponent"] == "Russia")
        # Hand Britain a better prospect than Russia's and it leads again.
        original = adv._peace_prospect

        def _fake(world_, player, opponent):
            if opponent == "Britain":
                return {"score": best_stuck["acceptance"] + 10,
                        "outcome": "ACCEPT"}
            return original(world_, player, opponent)

        adv._peace_prospect = _fake
        try:
            rec = adv._build_situation_recommendation(
                world, "France", rows, None, "defensive")
        finally:
            adv._peace_prospect = original
        assert rec["target_nation"] == "Britain"

    def test_losing_breaks_a_tie_in_acceptance(self, world):
        """Urgency is the TIEBREAK, not the rule: when two courts would
        meet the same answer, the war going badly is the more urgent ask.
        (Before the August 22 review this was the rule itself — "losing
        still outranks stuck" — which named a court refusing at 21-28 over
        one signing at 64-69 on 7 of 13 measured snapshots.)"""
        rows = _board(world, row_score=-40,
                      pair_scores={"Britain": -5, "Russia": 0})
        original = adv._peace_prospect
        adv._peace_prospect = lambda w, p, o: {"score": 44,
                                               "outcome": "COUNTER_OFFER"}
        try:
            ranked = adv._settlement_candidates(world, "France", rows)
        finally:
            adv._peace_prospect = original
        assert {c["opponent"] for c in ranked} == {"Britain", "Russia"}
        assert len({c["acceptance"] for c in ranked}) == 1
        assert ranked[0]["opponent"] == "Britain"
        assert ranked[0]["row_losing"] is True

    def test_the_flip_flag_is_the_only_lever(self, world):
        assert adv.COUNSEL_RANKS_BY_ACCEPTANCE is True
        src = (REPO / "backend" / "game_logic"
               / "diplomatic_advisory.py").read_text(encoding="utf-8")
        assert src.count("COUNSEL_RANKS_BY_ACCEPTANCE") == 2


class TestTheCounselStatesWhatTheScorerSays:
    def test_each_band_gets_its_own_clause(self, world):
        rows = _board(world, row_score=10, pair_scores={"Russia": 0})
        seen = set()
        original = adv._peace_prospect
        for outcome in ("ACCEPT", "COUNTER_OFFER", "REJECT"):
            adv._peace_prospect = (
                lambda w, p, o, _o=outcome: {"score": 0, "outcome": _o})
            try:
                rec = adv._build_situation_recommendation(
                    world, "France", rows, None, "defensive")
            finally:
                adv._peace_prospect = original
            clause = adv._PEACE_PROSPECT_CLAUSE[outcome]
            assert clause in rec["text"], outcome
            seen.add(clause)
        assert len(seen) == 3

    def test_every_clause_is_scoped_to_a_plain_peace(self):
        """A bare peace scored ACCEPT 54 on a board where the Cabinet's own
        suggested package scored COUNTER_OFFER 48 — so an unscoped "they
        would sign" would be contradicted one click later."""
        for clause in adv._PEACE_PROSPECT_CLAUSE.values():
            assert "plain peace" in clause, clause
        assert "draft will ask for more" in adv._PEACE_PROSPECT_CLAUSE["ACCEPT"]

    def test_the_unmeasured_claims_are_gone(self, world):
        """The predicate is a LEVEL, not a trend, and says nothing about
        territory or about the future."""
        rows = _board(world, row_score=10, pair_scores={"Russia": 0})
        rec = adv._build_situation_recommendation(world, "France", rows, None,
                                                  "defensive")
        assert "has gone still" in rec["text"]
        assert "the ground has not moved" not in rec["text"]
        assert "Nothing more will be won here by fighting" not in rec["text"]

    def test_a_losing_row_whose_leader_pair_is_winning_says_so(self, world):
        """A collapsed row's `war_score` is the WAR-level side score, so
        "the war with Britain turns against us" was printable while France
        stood +40 against Britain."""
        rows = _board(world, row_score=-40,
                      pair_scores={"Britain": 40, "Austria": 5}, we={})
        rec = adv._build_situation_recommendation(world, "France", rows, None,
                                                  "defensive")
        assert rec["target_nation"] == "Britain"
        assert "turns against us" not in rec["text"]
        assert "goes badly" in rec["text"]

    def test_a_formed_nation_is_never_named_by_its_dead_name(self, world):
        from backend.game_logic.formations import formed_display_name
        rows = _board(world, row_score=10, pair_scores={"KingdomOfItaly": 0})
        world.nation_formations = {"KingdomOfItaly": {"id": "risorgimento"}}
        display = formed_display_name(world, "KingdomOfItaly")
        rec = adv._build_situation_recommendation(world, "France", rows, None,
                                                  "defensive")
        assert rec["target_nation"] == "KingdomOfItaly"   # the tag routes
        assert "KingdomOfItaly" not in rec["label"]
        assert "KingdomOfItaly" not in rec["text"]
        assert display in rec["label"]

    def test_the_cabinet_key_says_when_it_works(self, world):
        """F1 is inert while the advisory modal is up."""
        rows = _board(world, row_score=10, pair_scores={"Russia": 0})
        rec = adv._build_situation_recommendation(world, "France", rows, None,
                                                  "defensive")
        assert "Cabinet (F1) once this is closed" in rec["text"]


class TestTheScorerCallIsSafeHere:
    def test_the_advisory_still_writes_nothing(self, world):
        from backend.game_logic.diplomatic_advisory import generate_advisory
        _board(world, row_score=-30, pair_scores={"Britain": -5, "Russia": 0})
        before = world.to_dict()
        generate_advisory(None, "assess_situation", world)
        assert world.to_dict() == before

    def test_the_prospect_is_deterministic(self, world):
        _board(world, row_score=10, pair_scores={"Russia": 0})
        first = adv._peace_prospect(world, "France", "Russia")
        second = adv._peace_prospect(world, "France", "Russia")
        assert first["score"] == second["score"]
        assert first["outcome"] == second["outcome"]

    def test_the_clause_table_uses_the_scorers_own_verdict(self):
        """Not a second copy of the 50/30 thresholds — this rung exists
        because a counsel and an executor kept two copies of one rule."""
        src = (REPO / "backend" / "game_logic"
               / "diplomatic_advisory.py").read_text(encoding="utf-8")
        assert "ACCEPTANCE_THRESHOLD" not in src
        assert ">= 50" not in src and ">= 30" not in src
        assert set(adv._PEACE_PROSPECT_CLAUSE) == {
            "ACCEPT", "COUNTER_OFFER", "REJECT"}


class TestTheArchiveIsRegenerated:
    def test_the_review_digest_is_archived(self):
        """Never-do 18: the archive is the citable record, and the driver
        changed under it. The pre-review archive is kept as the record of
        what the slice landed."""
        base = REPO / "docs" / "audits" / "playtest_digests"
        after = base / "wo5-propose-arm-review" / "digest.md"
        before = base / "wo5-propose-arm" / "digest.md"
        assert before.exists() and after.exists()
        text = io.open(after, encoding="utf-8").read()
        assert "(left standing)" not in text
        assert "ANSWER CYCLE" not in text
        assert "refused:" in text
        meta = json.loads(
            io.open(base / "wo5-propose-arm-review" / "meta.json",
                    encoding="utf-8").read())
        assert meta.get("status") == "completed"
