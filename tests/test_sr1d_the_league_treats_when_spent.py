"""SR-1d — PR-D1b "The League Treats When Spent" (Score Mandate Chunk 1,
September 26, 2026; `DESIGN_REFINEMENT.md` PR-D1b, ruled September 23 under
the delegated grant; landing record `SCORE_MANDATE_PLAN.md` §2 Chunk 1).

The AI's multi-party settlement offer to the player is gated on P1's OWN
coalition break-ranks clause — extracted as `coalition_break_ranks_reason`
so P1 behaves exactly as before — applied to the offering leader of the
active coalition's war against the player only, in the producer loop and at
the two `request_terms` checkpoints; never in `_settlement_offer_eligible_for_war`,
which mediation shares. The player's own peace proposal stays open. The
button carries an honest clock; the resolver re-checks at answer time; the
producer waits a turn while a covered member's own envoy is on the desk.
"""
import contextlib
import io
from pathlib import Path

import pytest

import backend.game_logic.ai_diplomacy as AD
from backend.game_logic.settlement_routes import evaluate_request_terms_affordance
from backend.models.world_state import WorldState

SCENARIO_PATH = (Path(__file__).resolve().parents[1] / "godot-client"
                 / "project-sovereign" / "assets" / "maps" / "europe_1805.json")


def _boot(turn=3) -> WorldState:
    """The 1805 boot with the boot war aged past the producer's floor: the
    coalition's leader (Britain) unspent — WE 0, war score 0."""
    with contextlib.redirect_stdout(io.StringIO()):
        w = WorldState.from_scenario(str(SCENARIO_PATH))
    w.current_turn = turn
    return w


def _war(w):
    return w.war_instances["war_1"]


def _produce(w):
    with contextlib.redirect_stdout(io.StringIO()):
        return AD.process_settlement_offer_phase(w)


def _leader_key(w):
    return w._make_diplo_key("Britain", "France")


class TestTheBoardIsTheRulings:

    def test_the_boot_league_is_britains_and_unspent(self):
        w = _boot()
        c = w.active_coalition
        assert c["target_nation"] == "France" and c["leader"] == "Britain"
        assert "Britain" in c["members"]
        assert int(w.war_exhaustion.get("Britain", 0)) == 0
        assert AD._settlement_offer_eligible_for_war(w, _war(w), player="France",
                                                      current_turn=3) is None


class TestTheHelper:

    def test_loyal_while_nothing_breaks_ranks(self):
        w = _boot()
        assert AD.coalition_break_ranks_reason(w, "Britain", war_score=0,
                                               diplo_key=_leader_key(w)) is None

    def test_the_four_arms(self):
        w = _boot()
        key = _leader_key(w)
        assert AD.coalition_break_ranks_reason(w, "Britain", war_score=-51, diplo_key=key) == "score"
        w.war_exhaustion["Britain"] = 81
        assert AD.coalition_break_ranks_reason(w, "Britain", war_score=0, diplo_key=key) == "exhaustion"
        w.war_exhaustion["Britain"] = 0
        w.current_turn = 9
        w.war_start_turns[key] = 1
        # Found while extracting: a score under -60 is under -50, so P1's
        # "8+ turns at < -60" limb is subsumed by the first arm and has been
        # dead since it was written — kept for byte-identical behaviour and
        # recorded, not repaired (a balance question, not this row's).
        assert AD.coalition_break_ranks_reason(w, "Britain", war_score=-61, diplo_key=key) == "score"
        assert AD.coalition_break_ranks_reason(w, "Britain", war_score=-40, diplo_key=key) is None

    def test_the_pressburg_arm(self, monkeypatch):
        import backend.game_logic.agendas as AG
        w = _boot()
        monkeypatch.setattr(AG, "agenda_separate_peace_ready", lambda nation, world: nation == "Britain")
        assert AD.coalition_break_ranks_reason(w, "Britain", war_score=-31,
                                               diplo_key=_leader_key(w)) == "pressburg"

    def test_the_p1_clause_reads_the_helper(self):
        src = Path("backend/game_logic/ai_diplomacy.py").read_text(encoding="utf-8")
        body = src.split("# ── P1: Losing badly", 1)[1][:2600]
        assert "coalition_break_ranks_reason(world, nation, war_score=war_score" in body
        assert "coalition_blocked = True" in body
        assert "if not coalition_blocked and THE_COURT_SENDS_ONE_ENVOY_PER_WAR:" in body


class TestTheProducerGate:

    def test_no_offer_while_the_league_can_still_fight(self):
        w = _boot()
        assert _produce(w) == []
        assert not w.pending_settlement_dialogues

    def test_the_gate_names_its_clock(self):
        w = _boot()
        gate = AD.league_offer_gate(w, _war(w), player="France")
        assert gate["reason"] == "league_not_spent" and gate["leader"] == "Britain"
        assert gate["exhaustion"] == 0 and gate["turns_at_most"] == 11   # ceil(81 / 8)
        w.war_exhaustion["Britain"] = 72
        assert AD.league_offer_gate(w, _war(w), player="France")["turns_at_most"] == 2

    @pytest.mark.parametrize("arm", ["exhaustion", "score"])
    def test_the_offer_comes_when_the_leader_could_break_ranks(self, arm):
        w = _boot()
        if arm == "exhaustion":
            w.war_exhaustion["Britain"] = 81
        else:
            # The stored score is the alphabetically-first court's (Britain's
            # for "Britain|France"): -60 is Britain losing at -60.
            w.war_scores[_leader_key(w)] = -60
        produced = _produce(w)
        assert len(produced) == 1 and produced[0]["war_id"] == "war_1"

    def test_the_lever_down_is_the_old_producer(self, monkeypatch):
        monkeypatch.setattr(AD, "THE_LEAGUE_TREATS_WHEN_SPENT", False)
        w = _boot()
        assert len(_produce(w)) == 1

    def test_a_war_that_is_not_the_leagues_is_ungated(self):
        w = _boot()
        w.active_coalition = None
        w.war_exhaustion["Britain"] = 0
        assert AD.league_offer_gate(w, _war(w), player="France") is None

    def test_mediation_shares_no_gate(self):
        """`_settlement_offer_eligible_for_war` is untouched (mediation reads
        it); the gate lives in the producer and the request checkpoints."""
        w = _boot()
        assert AD._settlement_offer_eligible_for_war(w, _war(w), player="France",
                                                      current_turn=3) is None
        src = Path("backend/game_logic/ai_diplomacy.py").read_text(encoding="utf-8")
        elig = src.split("def _settlement_offer_eligible_for_war(", 1)[1].split("\ndef ", 1)[0]
        assert "league_offer_gate" not in elig
        med = src.split("def process_mediation_offers(", 1)[1].split("\ndef ", 1)[0]
        assert "league_offer_gate" not in med


class TestTheRider:

    def _envoy(self, source):
        return {"type": "incoming_proposal", "target_nation": source,
                "talleyrand_text": "x", "options": [],
                "context": {"proposal": {"type": "armistice", "proposer_nation": source},
                            "source_nation": source, "proposal_type": "armistice"},
                "turn_created": 3, "blocking": False}

    def test_a_covered_members_envoy_holds_the_table_a_turn(self):
        w = _boot()
        w.war_exhaustion["Britain"] = 81
        w.dialogue_manager.push(self._envoy("Austria"))
        assert AD._covered_members_envoy_pending(w, _war(w), player="France") is True
        assert _produce(w) == []
        w.dialogue_manager.pop()
        assert AD._covered_members_envoy_pending(w, _war(w), player="France") is False
        assert len(_produce(w)) == 1

    def test_an_unrelated_courts_envoy_holds_nothing(self):
        w = _boot()
        w.war_exhaustion["Britain"] = 81
        w.dialogue_manager.push(self._envoy("Prussia"))
        assert AD._covered_members_envoy_pending(w, _war(w), player="France") is False
        assert len(_produce(w)) == 1


class TestRequestTerms:

    def test_the_button_is_disabled_with_the_honest_clock(self):
        w = _boot()
        aff = evaluate_request_terms_affordance(w, "war_1")
        assert aff["state"] == "disabled" and aff["reason"] == "league_not_spent"
        assert "exhaustion 0 of 80; at most 11 turns" in aff["reason_display"]
        assert aff["reason_display"].startswith("Britain leads a league that is not yet spent")

    def test_the_button_opens_when_the_league_is_spent(self):
        w = _boot()
        w.war_exhaustion["Britain"] = 81
        assert evaluate_request_terms_affordance(w, "war_1")["state"] == "available"

    def test_the_desk_check_still_comes_first(self):
        """FA slice 17 p2b's pin: an offer on the desk is `offer_already_pending`
        before any clock."""
        w = _boot()
        w.war_exhaustion["Britain"] = 81
        _produce(w)
        assert evaluate_request_terms_affordance(w, "war_1")["reason"] == "offer_already_pending"

    def test_the_answer_is_re_checked(self):
        """Asked while spent, answered after the board moved: refused with
        the clock, the request cooled, no offer."""
        w = _boot()
        w.settlement_terms_requests = {"war_1": {
            "status": "requested", "requested_turn": 3, "answering_leader": "Britain"}}
        with contextlib.redirect_stdout(io.StringIO()):
            granted = AD._resolve_settlement_terms_requests(
                w, player="France", current_turn=3,
                pending=w.pending_settlement_dialogues, cooldowns=w.ai_settlement_cooldowns)
        assert granted == []
        entry = w.settlement_terms_requests["war_1"]
        assert entry["status"] == "refused" and entry["resolve_reason"] == "league_not_spent"
        assert entry["cooldown_until_turn"] == 3 + AD.REQUEST_TERMS_COOLDOWN_TURNS
        titles = [n.get("title") for n in w.notifications._pending]
        assert any(t == "Terms refused by Britain" for t in titles), titles

    def test_a_spent_league_grants_the_ask(self):
        w = _boot()
        w.war_exhaustion["Britain"] = 81
        w.settlement_terms_requests = {"war_1": {
            "status": "requested", "requested_turn": 3, "answering_leader": "Britain"}}
        with contextlib.redirect_stdout(io.StringIO()):
            granted = AD._resolve_settlement_terms_requests(
                w, player="France", current_turn=3,
                pending=w.pending_settlement_dialogues, cooldowns=w.ai_settlement_cooldowns)
        assert len(granted) == 1
        assert w.settlement_terms_requests["war_1"]["status"] == "granted"


class TestThePlayersOwnProposalStaysOpen:

    def test_a_losing_france_can_still_offer_terms(self):
        """The player's peace PROPOSAL never reads the affordance — a France
        that is losing can always offer terms (the ruling's R3)."""
        src = Path("backend/commands/diplomatic_executor.py").read_text(encoding="utf-8")
        body = src.split("def _execute_propose_common_peace(", 1)[1].split("\n    def ", 1)[0]
        assert "evaluate_request_terms_affordance" not in body
        assert "league_offer_gate" not in body


DIGESTS = Path(__file__).resolve().parents[1] / "docs" / "audits" / "playtest_digests"


def _first_ratified_turn(run: str) -> int:
    """The turn of the first `Settlement Ratified` line in an archived
    commanded-arm digest (the driver prints one `## Turn N` head per turn)."""
    turn = 0
    for line in (DIGESTS / run / "digest.md").read_text(encoding="utf-8").split("\n"):
        if line.startswith("## Turn "):
            turn = int(line.split()[2])
        elif "Settlement Ratified" in line:
            return turn
    return -1


class TestTheMeasuredCadence:
    """The ruling's measurement, on the committed archives: the commanded arm
    (`commanded_full40.json --diplomacy accept`) signed the league's table on
    turn 4 on every seed before the gate (`iq8-cmd-*`, September 17) and on
    turns 9 / 10 / 11 after it (`prd1b-cmd-*`, September 26), France holding
    28 / 25 / 28 provinces at turn 40 — FA-D27's re-open (a seed under 20)
    does not fire."""

    @pytest.mark.parametrize("seed", ["historical", "austerlitz", "marengo"])
    def test_the_league_signed_on_turn_four_before_the_gate(self, seed):
        assert _first_ratified_turn(f"iq8-cmd-{seed}") == 4

    @pytest.mark.parametrize("seed,turn", [("historical", 9), ("austerlitz", 10), ("marengo", 11)])
    def test_the_league_treats_when_spent_after_it(self, seed, turn):
        assert _first_ratified_turn(f"prd1b-cmd-{seed}") == turn

    @pytest.mark.parametrize("seed,provinces", [("historical", 28), ("austerlitz", 25), ("marengo", 28)])
    def test_a_commanded_france_still_holds_its_provinces_at_turn_forty(self, seed, provinces):
        md = (DIGESTS / f"prd1b-cmd-{seed}" / "digest.md").read_text(encoding="utf-8")
        ledger = [ln for ln in md.split("\n") if ln.startswith("- LEDGER")][-1]
        assert f"provinces {provinces} " in ledger, ledger
        assert provinces >= 20   # FA-D27's re-open condition does not fire


class TestTheArticle:

    def test_an_armistice_treaty_would_be_a_downgrade(self):
        w = _boot()
        w.diplomatic_states[w._make_diplo_key("France", "Prussia")] = "PEACE"
        with contextlib.redirect_stdout(io.StringIO()):
            result = w._ratify_treaty({"proposer_nation": "Prussia", "target_nation": "France",
                                       "type": "armistice", "sweeteners": [], "demands": []})
        assert result["type"] == "diplomatic_treaty_failed"
        assert result["message"].endswith("An Armistice treaty would be a downgrade.")
