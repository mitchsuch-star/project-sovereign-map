"""WO slice 5 — "Berthier Names the Peace" (WEIRD_OUTCOMES_SPEC §3 slice 5).

The defect, measured: France and Russia sat at war score exactly 0 for
thirty turns with both courts pegged at the war-exhaustion cap, Austria
proposing armistices on six separate turns, and no peace concluded —
because rung 1 of `_build_situation_recommendation` fired only on
`war_score < 0`. A war can be unwinnable without being lost, and the war
room never once named the peace Russia would have signed.

Reproduced before a line was written (seed `austerlitz`, ambient, turn 16):

    pair France|Russia: age 15, WE 136 / 130, pair score 0
    -> mutually exhausted TRUE, Russia's plain peace scores ACCEPT at 54
    war row: opponent=Britain, opponents=[Britain, Austria, Russia],
             war_score=+26   <- the collapsed coalition row France is WINNING
    counsel: "Britain's war has a purpose we can price..."

At turn 12 the same board reads WE 104 / 98 and Russia scores
COUNTER_OFFER at 49 — the predicate's own turn-on and the court's
willingness arrive together, which is the calibration the spec predicted
from +8 WE/turn.

The fix is a single-source lift, not a second copy of the inequality:
`settlement_third_party.pair_is_mutually_exhausted` is the ONE place the
three comparisons live, and both the AI's pair exit and the counsel call
it. Half of these tests exist to make that structural, because a copied
inequality would pass every behavioural test in this file.
"""

import ast
import importlib.util
import inspect
import json
import re
import sys
from pathlib import Path

import pytest

from backend.game_logic import settlement_third_party as stp
from backend.game_logic.diplomatic_advisory import (
    _build_situation_recommendation,
    _mutually_exhausted_courts,
)
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCENARIO_PATH = (
    REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
    / "europe_1805.json"
)

# The measured turn-16 board, as numbers (see the module docstring).
T16_TURN = 16
T16_WE = {"France": 136, "Russia": 130, "Britain": 131, "Austria": 185}
T16_PAIR_SCORES = {"Russia": 0, "Britain": -7, "Austria": 33}
T16_ROW_SCORE = 26          # the COLLAPSED coalition row France is winning


@pytest.fixture(scope="module")
def world1805():
    return WorldState.from_scenario(str(SCENARIO_PATH))


@pytest.fixture
def world(world1805):
    return WorldState.from_dict(world1805.to_dict())


def _war(world, a, b, started_turn):
    key = world._make_diplo_key(a, b)
    world.diplomatic_states[key] = "WAR"
    world.war_start_turns[key] = int(started_turn)
    world.invalidate_bloc_members_cache()
    return key


def _set_pair_score(world, a, b, score_for_a):
    """Store a pair score oriented so `get_war_score_for(world, a, b)` reads
    `score_for_a` — the store is from the alphabetically-first perspective."""
    key = world._make_diplo_key(a, b)
    first = key.split("|")[0]
    world.war_scores[key] = int(score_for_a if first == a else -score_for_a)


def _t16_board(world):
    """Rebuild the measured turn-16 stalemate: France at war with the whole
    Third Coalition, winning on the collapsed row, dead level with Russia."""
    world.current_turn = T16_TURN
    world.war_exhaustion = dict(T16_WE)
    for court, pair_score in T16_PAIR_SCORES.items():
        _war(world, "France", court, started_turn=1)
        _set_pair_score(world, "France", court, pair_score)
    return [{
        "status": "war",
        "opponent": "Britain",
        "opponents": ["Britain", "Austria", "Russia"],
        "opponent_display": "Britain + Austria + Russia",
        "war_score": T16_ROW_SCORE,
        "trend": "stable",
        "duration": 15,
        "started_turn": 1,
        "request_terms_state": {"state": "absent"},
        "settlement_available": True,
    }]


# ═══════════════════════════════════════════════════════════════════════
# THE PREDICATE — one source, three falsifiable arms
# ═══════════════════════════════════════════════════════════════════════

class TestPredicate:
    def test_all_three_arms_pass(self, world):
        _t16_board(world)
        assert stp.pair_is_mutually_exhausted(world, "France", "Russia", 1)

    def test_too_young_fails(self, world):
        _t16_board(world)
        # One turn short of PAIR_EXIT_MIN_TURNS and nothing else changed.
        joined = T16_TURN - stp.PAIR_EXIT_MIN_TURNS + 1
        assert not stp.pair_is_mutually_exhausted(
            world, "France", "Russia", joined)
        assert stp.pair_is_mutually_exhausted(
            world, "France", "Russia", joined - 1)

    def test_one_side_not_weary_enough_fails(self, world):
        _t16_board(world)
        world.war_exhaustion["Russia"] = stp.PAIR_EXIT_WE_FLOOR - 1
        assert not stp.pair_is_mutually_exhausted(world, "France", "Russia", 1)
        world.war_exhaustion["Russia"] = stp.PAIR_EXIT_WE_FLOOR
        assert stp.pair_is_mutually_exhausted(world, "France", "Russia", 1)

    def test_the_other_side_is_checked_too(self, world):
        _t16_board(world)
        world.war_exhaustion["France"] = stp.PAIR_EXIT_WE_FLOOR - 1
        assert not stp.pair_is_mutually_exhausted(world, "France", "Russia", 1)

    def test_a_moving_war_is_not_stagnant(self, world):
        _t16_board(world)
        _set_pair_score(world, "France", "Russia",
                        stp.PAIR_EXIT_STAGNANT_SCORE + 1)
        assert not stp.pair_is_mutually_exhausted(world, "France", "Russia", 1)
        _set_pair_score(world, "France", "Russia",
                        stp.PAIR_EXIT_STAGNANT_SCORE)
        assert stp.pair_is_mutually_exhausted(world, "France", "Russia", 1)

    def test_losing_badly_is_also_not_stagnant(self, world):
        """The band is absolute: a pair being crushed is not 'still'."""
        _t16_board(world)
        _set_pair_score(world, "France", "Russia",
                        -(stp.PAIR_EXIT_STAGNANT_SCORE + 1))
        assert not stp.pair_is_mutually_exhausted(world, "France", "Russia", 1)

    def test_predicate_mutates_nothing(self, world):
        _t16_board(world)
        before = (dict(world.war_exhaustion), dict(world.war_scores),
                  dict(world.diplomatic_states), len(world.event_log))
        stp.pair_is_mutually_exhausted(world, "France", "Russia", 1)
        assert (dict(world.war_exhaustion), dict(world.war_scores),
                dict(world.diplomatic_states),
                len(world.event_log)) == before


# ═══════════════════════════════════════════════════════════════════════
# THE SINGLE SOURCE — the part a shortcut would quietly skip
# ═══════════════════════════════════════════════════════════════════════

_ADVISORY_SRC = (REPO / "backend" / "game_logic"
                 / "diplomatic_advisory.py").read_text(encoding="utf-8")
_STP_SRC = (REPO / "backend" / "game_logic"
            / "settlement_third_party.py").read_text(encoding="utf-8")


class TestSingleSource:
    def test_pair_exit_calls_the_shared_predicate(self):
        body = inspect.getsource(stp._process_exhausted_pair_exits)
        assert "pair_is_mutually_exhausted(" in body

    def test_pair_exit_keeps_no_copy_of_the_inequalities(self):
        """The turn-path reader must not compare the constants itself."""
        body = inspect.getsource(stp._process_exhausted_pair_exits)
        for const in ("PAIR_EXIT_WE_FLOOR", "PAIR_EXIT_MIN_TURNS",
                      "PAIR_EXIT_STAGNANT_SCORE"):
            assert const not in body, (
                f"{const} is compared inside _process_exhausted_pair_exits "
                f"again — the predicate was copied, not shared")

    def test_the_advisory_keeps_no_copy_either(self):
        for const in ("PAIR_EXIT_WE_FLOOR", "PAIR_EXIT_MIN_TURNS",
                      "PAIR_EXIT_STAGNANT_SCORE"):
            assert const not in _ADVISORY_SRC, (
                f"{const} appears in diplomatic_advisory.py — the counsel "
                f"re-implemented the predicate instead of calling it")

    def test_exactly_one_comparison_site_per_constant(self):
        """Each threshold is read inside ONE function. Mutating the
        predicate must break both readers together; if a second site
        appears this pin fails before behaviour drifts."""
        tree = ast.parse(_STP_SRC)
        for const in ("PAIR_EXIT_WE_FLOOR", "PAIR_EXIT_MIN_TURNS",
                      "PAIR_EXIT_STAGNANT_SCORE"):
            owners = set()
            for node in ast.walk(tree):
                if not isinstance(node, ast.FunctionDef):
                    continue
                names = {n.id for n in ast.walk(node)
                         if isinstance(n, ast.Name)}
                if const in names:
                    owners.add(node.name)
            assert owners == {"pair_is_mutually_exhausted"}, (
                f"{const} is read by {sorted(owners)}, expected only "
                f"pair_is_mutually_exhausted")

    def test_the_counsel_follows_the_engines_predicate(self, world,
                                                       monkeypatch):
        """Not "the import is written" — "the answer comes from there".

        (The first version of this pin read the source for the module name
        and was INERT: replacing the import with a local `def` of the same
        name left the docstring's mention behind and the pin still passed.
        Swapping the engine's function is the only check a copy cannot
        survive.)
        """
        rows = _t16_board(world)
        assert len(_mutually_exhausted_courts(world, "France", rows)) == 2

        monkeypatch.setattr(stp, "pair_is_mutually_exhausted",
                            lambda *a, **k: False)
        assert _mutually_exhausted_courts(world, "France", rows) == []

        monkeypatch.setattr(stp, "pair_is_mutually_exhausted",
                            lambda *a, **k: True)
        assert len(_mutually_exhausted_courts(world, "France", rows)) == 3


# ═══════════════════════════════════════════════════════════════════════
# THE COUNSEL — the measured t16 board
# ═══════════════════════════════════════════════════════════════════════

class TestCounselNamesTheStuckWar:
    def test_t16_counsel_names_russia(self, world):
        """The done-when. On the measured board the counsel names Russia —
        the court whose plain peace the scorer rates ACCEPT."""
        rows = _t16_board(world)
        rec = _build_situation_recommendation(world, "France", rows, None,
                                              "defensive")
        assert rec is not None
        assert rec["target_nation"] == "Russia"
        assert "Russia" in rec["text"]

    def test_the_old_gate_would_have_missed_it(self, world):
        """Falsifiable negative: nothing on this board is 'losing'. If the
        counsel ever names Russia only because the row went negative, this
        file is measuring the wrong thing."""
        rows = _t16_board(world)
        assert all(int(r["war_score"]) >= 0 for r in rows)

    def test_t12_board_is_not_yet_stuck(self, world):
        """The measured turn-12 numbers: same zero war score, WE still
        under the floor — and the counsel is NOT the stalemate arm."""
        rows = _t16_board(world)
        world.current_turn = 12
        world.war_exhaustion = {"France": 104, "Russia": 98,
                                "Britain": 98, "Austria": 139}
        rows[0]["duration"] = 11
        assert not _mutually_exhausted_courts(world, "France", rows)
        rec = _build_situation_recommendation(world, "France", rows, None,
                                              "defensive")
        assert rec is None or "has gone still" not in rec["text"]

    def test_a_collapsed_coalition_row_is_read_per_court(self, world):
        """The row carries three courts and one aggregate score; the stuck
        pair is inside it."""
        rows = _t16_board(world)
        stuck = _mutually_exhausted_courts(world, "France", rows)
        assert [s["opponent"] for s in stuck] == ["Russia", "Britain"]
        assert all(s["row"] is rows[0] for s in stuck)

    def test_the_deadest_war_is_named_first(self, world):
        """Russia at |0| outranks Britain at |7|. Flip the two scores and
        the counsel must follow the numbers, not the name."""
        rows = _t16_board(world)
        _set_pair_score(world, "France", "Russia", -12)
        _set_pair_score(world, "France", "Britain", 1)
        rec = _build_situation_recommendation(world, "France", rows, None,
                                              "defensive")
        assert rec["target_nation"] == "Britain"

    def test_the_age_reported_is_the_pairs_own(self, world):
        rows = _t16_board(world)
        rec = _build_situation_recommendation(world, "France", rows, None,
                                              "defensive")
        assert "15 turns" in rec["text"]

    def test_a_pair_with_no_recorded_start_is_skipped(self, world):
        """Conservative by construction: an unknown start is not 'ancient'."""
        rows = _t16_board(world)
        world.war_start_turns.pop(world._make_diplo_key("France", "Russia"))
        assert [s["opponent"]
                for s in _mutually_exhausted_courts(world, "France", rows)] \
            == ["Britain"]

    def test_terms_route_when_the_leader_is_the_stuck_court(self, world):
        rows = _t16_board(world)
        rows[0]["opponent"] = "Russia"
        rows[0]["opponents"] = ["Russia", "Britain", "Austria"]
        rows[0]["request_terms_state"] = {"state": "available"}
        rec = _build_situation_recommendation(world, "France", rows, None,
                                              "defensive")
        assert rec["kind"] == "request_terms"
        assert rec["target_nation"] == "Russia"

    def test_a_non_leader_gets_the_proposal_menu(self, world):
        """`request_terms` is war-scoped and belongs to the row's leader —
        rung 1.5's rule, inherited rather than re-decided."""
        rows = _t16_board(world)
        rows[0]["request_terms_state"] = {"state": "available"}
        rec = _build_situation_recommendation(world, "France", rows, None,
                                              "defensive")
        assert rec["target_nation"] == "Russia"
        assert rec["kind"] == "open_proposal"


class TestLosingStillOutranksStuck:
    def test_a_losing_war_wins_the_rung(self, world):
        rows = _t16_board(world)
        rows.append({
            "status": "war", "opponent": "Prussia", "war_score": -30,
            "trend": "falling", "duration": 4, "started_turn": 12,
            "request_terms_state": {"state": "available"},
            "settlement_available": True,
        })
        _war(world, "France", "Prussia", started_turn=12)
        rec = _build_situation_recommendation(world, "France", rows, None,
                                              "defensive")
        assert rec["target_nation"] == "Prussia"
        assert rec["kind"] == "request_terms"

    def test_stuck_still_wins_over_the_agenda_counsel(self, world):
        """Rung 1b sits ABOVE rung 1.5: on the measured board the old
        counsel named Britain's design, and the stalemate now outranks it."""
        rows = _t16_board(world)
        rec = _build_situation_recommendation(world, "France", rows, None,
                                              "defensive")
        assert "design" not in rec["label"].lower()


# ═══════════════════════════════════════════════════════════════════════
# THE COPY CONTRACT (§4 N-7) — name a surface, never a sentence to type
# ═══════════════════════════════════════════════════════════════════════

_SURFACES = ("Request Terms", "Cabinet")


def _rung1_texts(world):
    """Every arm of rung 1: losing x2 (terms / no terms) and stuck x2."""
    texts = []

    losing_terms = [{"status": "war", "opponent": "Prussia",
                     "war_score": -30, "trend": "falling",
                     "request_terms_state": {"state": "available"},
                     "settlement_available": True}]
    losing_open = [dict(losing_terms[0],
                        request_terms_state={"state": "disabled"})]
    for rows in (losing_terms, losing_open):
        texts.append(_build_situation_recommendation(
            world, "France", rows, None, "defensive")["text"])

    rows = _t16_board(world)
    texts.append(_build_situation_recommendation(
        world, "France", rows, None, "defensive")["text"])
    rows[0]["opponent"] = "Russia"
    rows[0]["opponents"] = ["Russia", "Britain", "Austria"]
    rows[0]["request_terms_state"] = {"state": "available"}
    texts.append(_build_situation_recommendation(
        world, "France", rows, None, "defensive")["text"])
    return texts


class TestCopyNamesASurface:
    def test_every_rung_1_arm_names_a_pressable_surface(self, world):
        texts = _rung1_texts(world)
        assert len(texts) == 4
        for text in texts:
            assert any(s in text for s in _SURFACES), text

    def test_no_arm_tells_the_player_to_type_a_diplomatic_sentence(self, world):
        """Slice 7 made typed diplomacy a redirect. Counsel that dictates a
        sentence sends the player at a closed door."""
        forbidden = re.compile(
            r"\btype\b|\benter\b|\bcommand\b|"
            r"\"(propose|request|sue|make) ", re.IGNORECASE)
        for text in _rung1_texts(world):
            assert not forbidden.search(text), text

    def test_the_surface_words_match_the_ones_the_game_already_uses(self, world):
        """The slice-7 redirect teaches these exact phrasings; the counsel
        must not invent a second vocabulary for the same two doors. Asserted
        on the COMPOSED text, not the source — the strings wrap in code."""
        main_gd = (REPO / "godot-client" / "project-sovereign" / "scripts"
                   / "main.gd").read_text(encoding="utf-8", errors="replace")
        assert "open the war banner and press [b]Request Terms[/b]" in main_gd
        assert "Take your seat in the Cabinet" in main_gd
        composed = " || ".join(_rung1_texts(world))
        assert "open the war banner and press Request Terms" in composed
        assert "take your seat in the Cabinet (F1)" in composed

    def test_the_counsel_still_ends_in_an_executable_option(self, world):
        """R117: the recommendation's `kind` must stay one of the two the
        war room already renders — a new kind would need client work this
        slice does not do."""
        rows = _t16_board(world)
        rec = _build_situation_recommendation(world, "France", rows, None,
                                              "defensive")
        assert rec["kind"] in ("request_terms", "open_proposal")


# ═══════════════════════════════════════════════════════════════════════
# THE NEVER-DO PINS (spec §3 slice 5)
# ═══════════════════════════════════════════════════════════════════════

class TestNeverDo:
    def test_war_exhaustion_is_not_unsaturated(self):
        """Grind-to-cap-then-dictate must stay impossible: the settlement
        component scores the ACCEPTING leader, and this slice touches
        neither the accrual nor the cap. Falsifiable at the constants."""
        from backend.game_logic import settlement_scoring
        assert settlement_scoring.WAR_EXHAUSTION_DIVISOR == 3
        assert settlement_scoring.WAR_EXHAUSTION_CLAMP == (0, 20)
        assert "war_exhaustion" not in _ADVISORY_SRC

    def test_the_advisory_writes_nothing(self, world):
        """D-2's other half: counsel is a pure read. A world snapshot must
        survive generating it."""
        from backend.game_logic.diplomatic_advisory import generate_advisory
        _t16_board(world)
        before = world.to_dict()
        generate_advisory(None, "assess_situation", world)
        assert world.to_dict() == before

    def test_no_congress_is_built(self):
        """`_emit_settlement_offer_for_war` has no pair dimension — routing
        a France|Russia peace through it would produce a whole-coalition
        settlement fronted by Britain."""
        assert "_emit_settlement_offer_for_war" not in _ADVISORY_SRC

    def test_request_terms_is_named_not_replaced(self):
        """`request_terms` already ships. The counsel points at it; it does
        not grow a second implementation."""
        assert "_execute_request_terms" not in _ADVISORY_SRC
        assert "settlement_terms_requests" not in _ADVISORY_SRC

    def test_the_advisory_stays_off_the_turn_path(self):
        """§2 D-2: exactly ONE production caller, player-command only."""
        callers = []
        for path in (REPO / "backend").rglob("*.py"):
            if path.name == "diplomatic_advisory.py":
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            if re.search(r"\bgenerate_advisory\s*\(", text):
                callers.append(path.name)
        assert callers == ["diplomatic_executor.py"], callers

    def test_no_new_serialized_field(self, world):
        """Zero new state: the slice adds a predicate and prose."""
        keys = set(world.to_dict().keys())
        for suspect in ("mutually_exhausted", "stuck_wars",
                        "exhaustion_counsel_seen"):
            assert suspect not in keys

    def test_no_new_dtype_and_no_queue_arrival(self):
        """The counsel rides the advisory dialogue the player ASKED for —
        it never arrives unbidden."""
        from backend.models.cooldown_manager import PopupQueue
        assert "stuck_war" not in PopupQueue.RESPONSE_KEYS
        assert "mutual_exhaustion" not in PopupQueue.RESPONSE_KEYS
        block = _ADVISORY_SRC.split(
            "def _mutually_exhausted_courts")[1].split("\ndef ")[0]
        assert "pending_" not in block


# ═══════════════════════════════════════════════════════════════════════
# THE DRIVER ARM — `--diplomacy propose` (Mode A)
# ═══════════════════════════════════════════════════════════════════════

_spec = importlib.util.spec_from_file_location(
    "playtest_driver", REPO / "tools" / "playtest_driver.py")
driver = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("playtest_driver", driver)
_spec.loader.exec_module(driver)

_DRIVER_SRC = (REPO / "tools" / "playtest_driver.py").read_text(
    encoding="utf-8")


def _status(*rows):
    return {"active_wars": {"wars": list(rows)}}


class TestProposeArm:
    def test_no_wars_means_no_overture(self):
        assert driver.peace_overture(_status(), 1) is None
        assert driver.peace_overture({}, 1) is None

    def test_armistice_rows_are_not_at_war(self):
        assert driver.peace_overture(
            _status({"status": "armistice", "opponent": "Austria"}), 1) is None

    def test_a_plain_war_gets_a_bilateral_peace_proposal(self):
        payload = _status({"status": "war", "opponent": "Russia",
                           "request_terms_state": {"state": "absent"}})
        assert driver.peace_overture(payload, 1) == "propose peace with Russia"

    def test_terms_are_asked_when_the_game_says_they_are_available(self):
        payload = _status({"status": "war", "opponent": "Britain",
                           "request_terms_state": {"state": "available"}})
        assert driver.peace_overture(payload, 1) == "request terms from Britain"

    def test_only_the_row_leader_can_be_asked_for_terms(self):
        """`request_terms` is war-scoped; a coalition member gets a proposal."""
        payload = _status({"status": "war", "opponent": "Britain",
                           "opponents": ["Britain", "Russia"],
                           "request_terms_state": {"state": "available"}})
        assert driver.peace_overture(payload, 2) == "propose peace with Russia"

    def test_round_robin_reaches_every_court(self):
        payload = _status({"status": "war", "opponent": "Britain",
                           "opponents": ["Britain", "Austria", "Russia"],
                           "request_terms_state": {"state": "absent"}})
        asked = {driver.peace_overture(payload, t) for t in range(1, 4)}
        assert asked == {"propose peace with Austria",
                         "propose peace with Britain",
                         "propose peace with Russia"}

    def test_the_command_is_a_golden_corpus_phrasing(self):
        """The driver keeps TYPED diplomacy (spec §6 never-do 12) — so the
        words it types must be words the parser is pinned to understand."""
        corpus = json.loads(
            (REPO / "tests" / "data" / "parser_golden_corpus.json")
            .read_text(encoding="utf-8"))
        utterances = {e["utterance"].lower() for e in corpus["entries"]}
        assert "propose peace with prussia" in utterances
        assert "request terms from austria" in utterances

    def test_propose_is_an_accepting_mode(self):
        """An arm that sues for peace and declines the peace it is handed
        measures nothing."""
        assert "propose" in driver.ACCEPTING_DIPLOMACY_MODES
        assert "decline" not in driver.ACCEPTING_DIPLOMACY_MODES

    def test_propose_is_offered_on_the_command_line(self):
        block = _DRIVER_SRC.split('ap.add_argument("--diplomacy"')[1]
        block = block.split("ap.add_argument")[0]
        assert '"propose"' in block

    def test_the_overture_only_fires_under_the_propose_policy(self):
        loop = _DRIVER_SRC.split("def run(")[1]
        assert 'if policy["diplomacy"] == "propose":' in loop


class _StubTransport:
    label = "stub"

    def __init__(self):
        self.posts = []

    echo = None

    def post(self, path, body=None):
        self.posts.append((path, dict(body or {})))
        # Re-serve the pending dialogue ONCE, the way a handler's popup
        # passthrough does when it was built before the answer landed.
        if self.echo is not None:
            served, self.echo = self.echo, None
            return served
        return {}

    def get(self, path):
        return {}


def _answerer(mode):
    digest = driver.Digest.__new__(driver.Digest)
    digest.counters = {"popups": 0}
    digest.recent = []
    digest.unknown_blockers = []
    digest.popup = lambda *a, **k: None
    digest.record = lambda *a, **k: None
    transport = _StubTransport()
    policy = dict(driver.POLICY_DEFAULTS, diplomacy=mode)
    return driver.Answerer(transport, digest, policy, False), transport


class TestIncomingProposalPopupIsAnswerable:
    """The AI's own peace offer arrives as the incoming-proposal POPUP
    payload — no `type`, no options, but a `dialogue_id`. Before this it
    was logged `(left standing)` seven times in eighteen turns, including
    Russia's answer to France's own overture."""

    POPUP = {"from_nation": "Russia", "proposal_type": "peace",
             "dialogue_id": 42, "clauses": []}

    @pytest.mark.parametrize("mode,expected", [
        ("propose", "accept"), ("accept", "accept"), ("first", "accept"),
        ("decline", "reject"),
    ])
    def test_the_popup_shape_is_answered_by_policy(self, mode, expected):
        answerer, _ = _answerer(mode)
        assert answerer._dialogue_choice(dict(self.POPUP)) == expected

    def test_a_real_dialogue_with_options_is_unaffected(self):
        answerer, _ = _answerer("propose")
        dialogue = {"type": "incoming_proposal", "nation": "Russia",
                    "options": [{"id": "accept_ai_proposal"},
                                {"id": "reject_ai_proposal"}]}
        assert answerer._dialogue_choice(dialogue) == "accept_ai_proposal"

    def test_the_answer_carries_the_dialogue_id(self):
        answerer, transport = _answerer("propose")
        answerer.begin_post()
        answerer.scan({"diplomatic_dialogue": dict(self.POPUP)})
        assert transport.posts == [
            ("/respond_to_diplomatic_dialogue",
             {"choice": "accept", "dialogue_id": 42})]

    def test_the_keywords_are_the_routers_own_words(self):
        from backend.commands.dialogue_routing import DIALOGUE_ACTION_KEYWORDS
        assert "accept_ai_proposal" in DIALOGUE_ACTION_KEYWORDS["accept"]
        assert "reject_ai_proposal" in DIALOGUE_ACTION_KEYWORDS["reject"]


class TestStalePassthroughIsNotAnsweredTwice:
    """Every POST rebuilds the popup passthroughs, so a response generated
    before an answer lands re-carries the dialogue that answer popped.
    Answering it again applies the verb to whatever the stack promoted in
    the meantime — and tripped the cycle guard on nine of eighteen turns
    the first time an arm made France sue for peace."""

    def test_the_same_dialogue_id_is_answered_once_per_post(self):
        answerer, transport = _answerer("propose")
        answerer.begin_post()
        payload = {"diplomatic_dialogue": {
            "from_nation": "Russia", "proposal_type": "peace",
            "dialogue_id": 7}}
        answerer.scan(dict(payload))
        answerer.scan(dict(payload))
        assert len(transport.posts) == 1

    def test_a_new_post_may_answer_it_again(self):
        answerer, transport = _answerer("propose")
        payload = {"diplomatic_dialogue": {
            "from_nation": "Russia", "proposal_type": "peace",
            "dialogue_id": 7}}
        answerer.begin_post()
        answerer.scan(dict(payload))
        answerer.begin_post()
        answerer.scan(dict(payload))
        assert len(transport.posts) == 2

    def test_a_different_dialogue_is_still_answered(self):
        answerer, transport = _answerer("propose")
        answerer.begin_post()
        answerer.scan({"diplomatic_dialogue": {
            "from_nation": "Russia", "proposal_type": "peace",
            "dialogue_id": 7}})
        answerer.scan({"diplomatic_dialogue": {
            "from_nation": "Austria", "proposal_type": "armistice_losing",
            "dialogue_id": 8}})
        assert len(transport.posts) == 2

    def test_drain_answers_a_re_served_dialogue_exactly_once(self):
        """The whole chain, through the real `drain()`: a transport that
        re-serves the pending dialogue (what a POST handler's passthrough
        does when it was built before the answer landed) must produce ONE
        answer and no cycle warning."""
        payload = {"diplomatic_dialogue": {
            "from_nation": "Russia", "proposal_type": "peace",
            "dialogue_id": 11}}
        answerer, transport = _answerer("propose")
        transport.echo = dict(payload)
        digest = answerer.d
        notes = []
        digest.note = notes.append

        driver.drain(transport, digest, answerer, dict(payload), False)
        assert len(transport.posts) == 1
        assert not notes

        driver.drain(transport, digest, answerer, dict(payload), False)
        assert len(transport.posts) == 2
