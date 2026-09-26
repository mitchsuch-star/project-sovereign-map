"""SR-2c / PR-D1d — "A new war is not a spent league" (Score Mandate Chunk 2
DIPLOMACY, September 26, 2026; `docs/SCORE_MANDATE_PLAN.md` §2 Chunk 2; row
`DESIGN_REFINEMENT.md` PR-D1d — this is the behaviour test the row names).

The SR-1d gate was scoped to the active league's war, so a war France
DECLARED after the league's peace drew the AI's offer at war-age 2. Three
rules were built behind levers and MEASURED on the same commanded arm before
one was chosen (the landing record). The chosen rule — lever (c): a war the
player declared (any of the player's live pairs in it carrying PR-D1c's
`declared_by` stamp) is gated on its LEADER's break-ranks clause, exactly as
the league's war is; a war declared ON the player stays ungated.

Every mechanics pin here sets the lever it reads explicitly, so the file is
true whichever default ships; `TestTheDefault` pins the shipped default and
the measured cadence.
"""
from __future__ import annotations

import contextlib
import io
from pathlib import Path

import pytest

import backend.game_logic.ai_diplomacy as AD
from backend.game_logic.diplomacy import declare_war, set_diplomatic_state
from backend.game_logic.settlement_helpers import (
    attach_pair_to_war_instance, resolve_pair_to_resolved,
)
from backend.game_logic.settlement_routes import evaluate_request_terms_affordance
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCENARIO = str(REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
               / "europe_1805.json")
DIGESTS = REPO / "docs" / "audits" / "playtest_digests"


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


def _boot() -> WorldState:
    with _quiet():
        return WorldState.from_scenario(SCENARIO)


def _league_peace(w: WorldState, turn: int = 12) -> WorldState:
    """The league's common peace, in miniature: every pair of the boot war
    resolved, the coalition dissolved, the instance ended (measured: the
    resolver ends the instance when no live pair remains)."""
    w.current_turn = turn
    war = w.war_instances["war_1"]
    with _quiet():
        for pair in list((war.get("diplo_key_meta") or {}).keys()):
            a, b = pair.split("|")
            if w.get_diplomatic_state(a, b) == "WAR":
                set_diplomatic_state(w, a, b, "PEACE", reason="peace_treaty")
            resolve_pair_to_resolved(w, pair, resolved_turn=turn)
    w.active_coalition = None
    assert w.war_instances["war_1"].get("ended_turn") == turn
    return w


def _declare(w: WorldState, *, by: str = "France", on: str = "Austria", turn: int = 14):
    w.current_turn = turn
    w.diplomatic_points = 8
    with _quiet():
        r = declare_war(w, by, on)
    assert r.get("success"), r
    return r["war_id"], w.war_instances[r["war_id"]]


def _produce(w: WorldState):
    with _quiet():
        return AD.process_settlement_offer_phase(w)


@pytest.fixture
def declared_war():
    """The filed geometry: the league at peace on turn 12, France declares on
    Austria on turn 14, the producer is asked at war-age 2 (turn 16)."""
    w = _league_peace(_boot())
    war_id, war = _declare(w)
    w.current_turn = 16
    return w, war_id, war


# ═══════════════════════════════════════════════════════════════════════
# The filed defect, in miniature
# ═══════════════════════════════════════════════════════════════════════

class TestTheFiledDefect:

    def test_the_re_declaration_is_a_fresh_war_the_court_attacked_leads(self, declared_war):
        w, war_id, war = declared_war
        assert war_id != "war_1"
        assert int(war.get("created_turn")) == 14
        side = war["side_by_nation"]["France"]
        assert AD._settlement_offer_opposing_side_leader(war, player_side=side) == "Austria"
        meta = war["diplo_key_meta"]
        assert meta[w._make_diplo_key("France", "Austria")]["declared_by"] == "France"
        assert AD.player_declared_this_war(war, "France")
        # the alliance cascade brings courts France never declared on
        assert "Britain" in war["side_by_nation"]
        assert meta[w._make_diplo_key("France", "Britain")].get("declared_by") is None

    def test_the_lever_down_draws_the_offer_at_war_age_two(self, declared_war, monkeypatch):
        """The row's own measurement (Austria asking at war-age 2), reproduced."""
        monkeypatch.setattr(AD, "THE_LEAGUE_GATE_COVERS_A_DECLARED_WAR", False)
        monkeypatch.setattr(AD, "THE_LEAGUE_GATE_COVERS_EVERY_WAR", False)
        w, war_id, war = declared_war
        assert AD._settlement_offer_eligible_for_war(
            w, war, player="France", current_turn=16) is None
        assert AD.league_offer_gate(w, war, player="France") is None
        assert len(_produce(w)) == 1


# ═══════════════════════════════════════════════════════════════════════
# Lever (c) — the chosen rule's mechanics
# ═══════════════════════════════════════════════════════════════════════

class TestAWarWeDeclaredIsGatedOnItsLeader:

    @pytest.fixture(autouse=True)
    def _lever(self, monkeypatch):
        monkeypatch.setattr(AD, "THE_LEAGUE_GATE_COVERS_A_DECLARED_WAR", True)
        monkeypatch.setattr(AD, "THE_LEAGUE_GATE_COVERS_EVERY_WAR", False)

    def test_no_offer_from_a_leader_that_has_not_broken_ranks(self, declared_war):
        w, war_id, war = declared_war
        gate = AD.league_offer_gate(w, war, player="France")
        assert gate and gate["reason"] == "war_not_spent" and gate["leader"] == "Austria"
        assert _produce(w) == []
        assert not w.pending_settlement_dialogues

    def test_the_offer_comes_when_the_leader_could_break_ranks(self, declared_war):
        w, war_id, war = declared_war
        w.war_exhaustion["Austria"] = 81
        assert AD.league_offer_gate(w, war, player="France") is None
        assert len(_produce(w)) == 1

    def test_the_display_names_the_war_we_declared(self, declared_war):
        w, _, war = declared_war
        gate = AD.league_offer_gate(w, war, player="France")
        text = AD.league_offer_gate_display(w, gate)
        assert text.startswith("Austria has not broken ranks on the war we declared")
        assert "exhaustion 0 of 80" in text

    def test_the_button_carries_the_same_clock(self, declared_war):
        w, war_id, _ = declared_war
        aff = evaluate_request_terms_affordance(w, war_id)
        assert aff["state"] == "disabled" and aff["reason"] == "war_not_spent"
        assert aff["reason_display"].startswith("Austria has not broken ranks")

    def test_a_war_declared_on_us_stays_ungated(self):
        """The rule reads who DECLARED: a court that attacks France may still
        sue once the structural floor passes, as before."""
        w = _league_peace(_boot())
        war_id, war = _declare(w, by="Austria", on="France")
        w.current_turn = 16
        assert not AD.player_declared_this_war(war, "France")
        assert AD.league_offer_gate(w, war, player="France") is None
        assert len(_produce(w)) == 1

    def test_the_leagues_own_war_keeps_the_leagues_gate(self):
        w = _boot()
        w.current_turn = 3
        gate = AD.league_offer_gate(w, w.war_instances["war_1"], player="France")
        assert gate["reason"] == "league_not_spent" and gate["leader"] == "Britain"

    def test_a_peace_ends_the_stamp(self, declared_war):
        w, war_id, war = declared_war
        with _quiet():
            resolve_pair_to_resolved(w, w._make_diplo_key("France", "Austria"), resolved_turn=16)
        assert not AD.player_declared_this_war(war, "France")

    def test_mediation_shares_no_gate(self):
        src = (REPO / "backend" / "game_logic" / "ai_diplomacy.py").read_text(encoding="utf-8")
        elig = src.split("def _settlement_offer_eligible_for_war(", 1)[1].split("\ndef ", 1)[0]
        assert "player_declared_this_war" not in elig and "league_offer_gate" not in elig
        med = src.split("def process_mediation_offers(", 1)[1].split("\ndef ", 1)[0]
        assert "league_offer_gate" not in med


# ═══════════════════════════════════════════════════════════════════════
# Lever (b)'s substrate — a re-attached pair remembers its reopening
# ═══════════════════════════════════════════════════════════════════════

class TestTheReopening:

    def _reopen_britain(self):
        w = _boot()
        war = w.war_instances["war_1"]
        key = w._make_diplo_key("France", "Britain")
        war["diplo_key_meta"][key]["declared_by"] = "France"
        war["diplo_key_meta"][key]["declaration_alarm"] = 20
        with _quiet():
            resolve_pair_to_resolved(w, key, resolved_turn=5)
        assert war["diplo_key_meta"][key]["pair_status"] == "resolved"
        w.current_turn = 9
        with _quiet():
            attach_pair_to_war_instance(w, "war_1", "Britain", "France", entry_path="test_reopen")
        return w, war, key

    def test_a_re_attached_pair_records_its_reopening_and_keeps_the_stamp(self):
        w, war, key = self._reopen_britain()
        meta = war["diplo_key_meta"][key]
        assert meta["pair_status"] == "war"
        assert meta["reopened_turn"] == 9
        assert int(meta["joined_turn"]) < 9            # the first entry is kept
        assert meta["declared_by"] == "France" and meta["declaration_alarm"] == 20

    def test_a_first_attachment_records_no_reopening(self):
        w = _league_peace(_boot())
        war_id, war = _declare(w)
        assert "reopened_turn" not in war["diplo_key_meta"][w._make_diplo_key("France", "Austria")]

    def test_the_war_age_reads_the_reopening_only_with_the_lever_up(self, monkeypatch):
        w, war, key = self._reopen_britain()
        monkeypatch.setattr(AD, "THE_WAR_AGE_IS_THE_PAIRS", False)
        assert AD.settlement_war_age_start(war, player="France") == int(war["created_turn"])
        monkeypatch.setattr(AD, "THE_WAR_AGE_IS_THE_PAIRS", True)
        assert AD.settlement_war_age_start(war, player="France") == 9


# ═══════════════════════════════════════════════════════════════════════
# The shipped default, and the measured cadence it was chosen on
# ═══════════════════════════════════════════════════════════════════════

def _turn_lines(run: str):
    """(turn, line) for an archived digest — the driver prints one
    `## Turn N` head per turn."""
    turn = 0
    for line in (DIGESTS / run / "digest.md").read_text(encoding="utf-8").split("\n"):
        if line.startswith("## Turn "):
            turn = int(line.split()[2])
        else:
            yield turn, line


def _declaration_turn(run: str) -> int:
    return next(t for t, line in _turn_lines(run)
                if "France declares war on Austria" in line)


def _offer_turns(run: str):
    """Any court's settlement offer arriving, by turn."""
    return [t for t, line in _turn_lines(run) if "settlement_offer_arrival" in line]


def _austria_offer_turns(run: str):
    return [t for t, line in _turn_lines(run)
            if "settlement_offer_arrival" in line and "Austria has offered terms" in line]


class TestTheDefault:
    """Lever (c) ships up; (a) and (b) stay measured and down."""

    def test_the_chosen_lever_is_up_and_the_others_down(self):
        assert AD.THE_LEAGUE_GATE_COVERS_A_DECLARED_WAR is True
        assert AD.THE_LEAGUE_GATE_COVERS_EVERY_WAR is False
        assert AD.THE_WAR_AGE_IS_THE_PAIRS is False

    def test_the_shipped_default_gates_the_war_we_declared(self, declared_war):
        """No lever is touched here: the row's own completion test on the
        shipped board — a war France declares draws no offer at war-age 2
        from a court that has not broken ranks."""
        w, war_id, war = declared_war
        gate = AD.league_offer_gate(w, war, player="France")
        assert gate and gate["reason"] == "war_not_spent"
        assert _produce(w) == []

    @pytest.mark.parametrize("seed,arm,declared,offer_turn", [
        ("historical", "off", 13, 15), ("historical", "b", 13, 15),
        ("historical", "a", 13, 22), ("historical", "c", 13, 22),
        ("austerlitz", "off", 14, 16), ("austerlitz", "c", 14, 25),
        ("marengo", "off", 11, 13), ("marengo", "c", 11, 20),
    ])
    def test_the_measured_cadence(self, seed, arm, declared, offer_turn):
        """The commanded arm with ONE French re-declaration, on Austria
        (`prd1d_redeclare.json`, `--diplomacy accept --declare-war proceed`;
        archives `prd1d-<arm>-<seed>`; `off` = the explicit lever-down arm,
        which reproduces the pre-flip board line for line). With the lever
        down Austria's offer arrives at war-age 2 on every seed — the filed
        defect; lever (b) is inert (the re-declaration is a fresh instance, so
        the pair's reopening is never later than the instance's birth); levers
        (a) and (c) hold the historical offer to turn 22, and (c) holds
        austerlitz to 25 and marengo to 20 — when Austria breaks ranks. On
        marengo the lever-down arm also shows the revolving door the row is
        about: the script's next attacks re-declare at 14 and 24, with offers
        at 16 and 29, while (c) holds the second war to turn 36."""
        run = f"prd1d-{arm}-{seed}"
        assert _declaration_turn(run) == declared
        offers = _austria_offer_turns(run)
        assert offers and offers[0] == offer_turn, offers
        if arm in ("off", "b"):
            assert offers[0] - declared == 2          # war-age 2
        else:
            assert offers[0] - declared >= 9          # held until ranks break

    def test_the_revolving_door_on_marengo(self):
        """Lever down: three declarations and offers at war-age 2 after each;
        lever (c): two declarations, each war held nine turns or more."""
        off = _turn_lines("prd1d-off-marengo")
        c = _turn_lines("prd1d-c-marengo")
        off_decl = [t for t, l in off if "France declares war on Austria" in l]
        c_decl = [t for t, l in c if "France declares war on Austria" in l]
        assert off_decl == [11, 14, 24]
        assert c_decl == [11, 21]
        # the third war's offer (turn 29) and (c)'s second (turn 36) come from
        # the opposing side's leader of the moment, not always Austria
        assert [t for t in _offer_turns("prd1d-off-marengo") if t > 11] == [13, 16, 29]
        assert [t for t in _offer_turns("prd1d-c-marengo") if t > 11] == [20, 36]
