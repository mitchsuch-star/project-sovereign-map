"""Session G3 — a client swears no pact of its own (DYNAMISM_SPEC.md §7c;
November 11, 2026).

The user's word: "Rule on clients first", then, at the question: "make best
cal for game".

What was found (the kept AI-France harness run on jena, session G2's record):
the Kingdom of Italy — the Emperor's client — signed a DEFENSIVE ALLIANCE with
the Pope at turn 7 through the court-to-court poll; the cast Naples declared
the Roman Expedition at 14; the pact called the kingdom into a war its lord
was not in; Naples took Piedmont and Milan and the kingdom was erased at 20.
Four provinces kept outside aim on the harness, every one of them this.

The ruling: a client's foreign policy is its lord's. A client signs no
defensive alliance and no alliance of its own — the poll proposes none to or
from it, the recipient-addressed road refuses one with `reason: client`.
Every court alike (an AI lord's clients too); the Alarm already says it of
guarantees ("not a client — its lord answers for it").
"""
from __future__ import annotations

import contextlib
import inspect
import io
import json
import random
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from backend.game_logic import ai_diplomacy as AD  # noqa: E402
from backend.game_logic import diplomatic_ledger as DL  # noqa: E402
from tests._t3_seams import T3_SEAMS_BY_ROW, hold_down  # noqa: E402

SCENARIO = (REPO / "godot-client" / "project-sovereign" / "assets"
            / "maps" / "europe_1805.json")
ROW = "G3-CLIENT"
PACTS = ("DEFENSIVE_ALLIANCE", "ALLIANCE")


def _world(seed: str = "historical"):
    from backend.models.world_state import WorldState
    return WorldState.from_scenario(str(SCENARIO), seed=seed)


@pytest.fixture()
def world():
    return _world("historical")


@pytest.fixture()
def jena():
    """The seed that casts Naples: `roman_expedition` at her deck's head."""
    return _world("jena")


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


def _state(world, a: str, b: str) -> str:
    return str(world.get_diplomatic_state(a, b))


def _set_relation(world, a: str, b: str, value: int) -> None:
    world.nation_relations[world._make_diplo_key(a, b)] = int(value)


def _warm_neighbours(world, a: str = "PapalStates", b: str = "KingdomOfItaly") -> None:
    """Trigger 3's board for the pair: at peace with each other and bound by
    a non-aggression pact, the relation past 40 — the next step up the
    ladder is the defensive alliance (the harness's turn-7 signature)."""
    _set_relation(world, a, b, 60)
    world.diplomatic_states[world._make_diplo_key(a, b)] = "NON_AGGRESSION"


def _as_client(world, court: str, lord: str) -> None:
    """A court made a client after the boot (a carve's row, the fields the
    read needs)."""
    world.vassals[court] = dict(world.vassals["Holland"], lord=lord)
    world.invalidate_bloc_members_cache()


# ═══════════════════════════════════════════════════════════════════════
# The read
# ═══════════════════════════════════════════════════════════════════════

class TestTheRead:
    def test_the_boots_three_clients_answer_to_the_emperor(self, world):
        assert {c: r["lord"] for c, r in world.vassals.items()} == {
            "Holland": "France", "KingdomOfItaly": "France", "Switzerland": "France"}

    def test_it_names_the_client_in_either_order(self, world):
        assert AD.client_in_the_pair(world, "KingdomOfItaly", "PapalStates") == "KingdomOfItaly"
        assert AD.client_in_the_pair(world, "PapalStates", "KingdomOfItaly") == "KingdomOfItaly"
        assert AD.client_in_the_pair(world, "Hanover", "Holland") == "Holland"
        assert AD.client_in_the_pair(world, "Switzerland", "Austria") == "Switzerland"

    def test_two_free_courts_read_nothing(self, world):
        assert AD.client_in_the_pair(world, "Naples", "PapalStates") == ""
        assert AD.client_in_the_pair(world, "Austria", "Russia") == ""
        # Bavaria is the Emperor's ALLY, never his client
        assert AD.client_in_the_pair(world, "Bavaria", "Austria") == ""

    def test_one_house_reads_nothing(self, world):
        """A lord and its client, two clients of one lord: their bond is the
        vassalage itself."""
        assert AD.client_in_the_pair(world, "France", "KingdomOfItaly") == ""
        assert AD.client_in_the_pair(world, "KingdomOfItaly", "Holland") == ""
        assert AD.client_in_the_pair(world, "Holland", "Holland") == ""
        assert AD.client_in_the_pair(world, "", "Holland") == ""

    def test_every_lord_alike(self, world):
        """An AI lord's client is bound the same way; the clients of two
        houses read the first asked."""
        _as_client(world, "Hesse", "Prussia")
        assert AD.client_in_the_pair(world, "Hesse", "Hanover") == "Hesse"
        assert AD.client_in_the_pair(world, "Prussia", "Hesse") == ""
        assert AD.client_in_the_pair(world, "Hesse", "Holland") == "Hesse"
        assert AD.client_in_the_pair(world, "Holland", "Hesse") == "Holland"

    def test_a_court_set_free_signs_again(self, world):
        del world.vassals["KingdomOfItaly"]
        world.invalidate_bloc_members_cache()
        assert AD.client_in_the_pair(world, "KingdomOfItaly", "PapalStates") == ""

    def test_the_seam_down_reads_nothing(self, world, monkeypatch):
        hold_down(monkeypatch, T3_SEAMS_BY_ROW[ROW])
        assert AD.client_in_the_pair(world, "KingdomOfItaly", "PapalStates") == ""


# ═══════════════════════════════════════════════════════════════════════
# The poll's gate
# ═══════════════════════════════════════════════════════════════════════

class TestThePollProposesNoPactToAClient:
    def test_the_harness_signature_is_stopped_at_the_poll(self, jena):
        """The warm pair one step below the pact: the triggers answer the
        defensive alliance (what signed at turn 7); the gate returns None."""
        _warm_neighbours(jena)
        assert AD._evaluate_ai_ai_triggers("PapalStates", "KingdomOfItaly", jena) == {
            "type": "defensive_alliance", "proposer": "PapalStates", "target": "KingdomOfItaly"}
        assert AD._evaluate_ai_ai_proposal("PapalStates", "KingdomOfItaly", jena) is None

    def test_the_seam_down_proposes_it(self, jena):
        _warm_neighbours(jena)
        with pytest.MonkeyPatch.context() as m:
            hold_down(m, T3_SEAMS_BY_ROW[ROW])
            assert AD._evaluate_ai_ai_proposal("PapalStates", "KingdomOfItaly", jena) == {
                "type": "defensive_alliance", "proposer": "PapalStates", "target": "KingdomOfItaly"}

    def test_the_gate_is_the_pact_types_alone(self, world):
        """Both pact types stop, from either chair; a non-aggression pact,
        open borders and a design ask pass through untouched."""
        with pytest.MonkeyPatch.context() as m:
            for ptype in ("defensive_alliance", "alliance"):
                m.setattr(AD, "_evaluate_ai_ai_triggers",
                          lambda a, b, w, ptype=ptype: {"type": ptype, "proposer": a, "target": b})
                assert AD._evaluate_ai_ai_proposal("PapalStates", "KingdomOfItaly", world) is None
                assert AD._evaluate_ai_ai_proposal("KingdomOfItaly", "PapalStates", world) is None
                assert AD._evaluate_ai_ai_proposal("Hanover", "Holland", world) is None
                # two free courts that covet nothing of each other: untouched
                assert AD._evaluate_ai_ai_proposal("Sweden", "Denmark", world) == {
                    "type": ptype, "proposer": "Sweden", "target": "Denmark"}
            for ptype in ("non_aggression", "open_borders", "design_ask"):
                m.setattr(AD, "_evaluate_ai_ai_triggers",
                          lambda a, b, w, ptype=ptype: {"type": ptype, "proposer": a, "target": b})
                assert AD._evaluate_ai_ai_proposal("PapalStates", "KingdomOfItaly", world) == {
                    "type": ptype, "proposer": "PapalStates", "target": "KingdomOfItaly"}

    def test_the_steps_below_the_pact_still_sign(self, jena):
        """The warm pair climbs the upgrade ladder as before — open borders,
        then the non-aggression pact (no war follows either) — and stops one
        step short of the defensive alliance."""
        from backend.game_logic.diplomacy import _UPGRADE_ORDER
        _set_relation(jena, "PapalStates", "KingdomOfItaly", 60)
        key = jena._make_diplo_key("PapalStates", "KingdomOfItaly")
        assert _state(jena, "PapalStates", "KingdomOfItaly") == "PEACE"
        climbed = []
        for rung in _UPGRADE_ORDER[_UPGRADE_ORDER.index("PEACE"):]:
            jena.diplomatic_states[key] = rung
            proposal = AD._evaluate_ai_ai_proposal("PapalStates", "KingdomOfItaly", jena)
            climbed.append((rung, proposal["type"] if proposal else None))
        assert climbed == [("PEACE", "open_borders"), ("OPEN_BORDERS", "non_aggression"),
                           ("NON_AGGRESSION", None), ("DEFENSIVE_ALLIANCE", None),
                           ("ALLIANCE", None)]


# ═══════════════════════════════════════════════════════════════════════
# The recipient-addressed road's guard
# ═══════════════════════════════════════════════════════════════════════

class TestTheRoadRefusesWithItsReason:
    def test_the_refusal_names_the_client(self, world):
        for proposer, target in (("PapalStates", "KingdomOfItaly"), ("KingdomOfItaly", "PapalStates")):
            event = AD._resolve_ai_ai_proposal(
                {"type": "defensive_alliance", "proposer": proposer, "target": target}, world)
            assert event["type"] == "ai_ai_proposal_refused"
            assert (event["refused_by"], event["reason"], event["client"]) == (
                target, "client", "KingdomOfItaly")
        assert len([e for e in world.event_log if e.get("type") == "ai_ai_proposal_refused"
                    and e.get("reason") == "client"]) == 2
        assert _state(world, "PapalStates", "KingdomOfItaly") not in PACTS

    def test_an_alliance_is_refused_the_same(self, world):
        event = AD._resolve_ai_ai_proposal(
            {"type": "alliance", "proposer": "Hanover", "target": "Holland"}, world)
        assert (event["reason"], event["client"]) == ("client", "Holland")

    def test_a_non_aggression_pact_is_no_pact(self, world):
        nap = AD._resolve_ai_ai_proposal(
            {"type": "non_aggression", "proposer": "PapalStates", "target": "KingdomOfItaly"}, world)
        assert nap is None or nap.get("reason") != "client"

    def test_the_coveted_reason_is_said_first(self, world):
        """Austria's design covets the kingdom's soil: session G's reason
        stands where both rules hold (one refusal, never two)."""
        assert AD.pact_with_the_coveted(world, "Austria", "KingdomOfItaly") == "Austria"
        event = AD._resolve_ai_ai_proposal(
            {"type": "defensive_alliance", "proposer": "Austria", "target": "KingdomOfItaly"}, world)
        assert event["reason"] == "covets"

    def test_the_seam_down_refuses_nothing_for_it(self, world, monkeypatch):
        hold_down(monkeypatch, T3_SEAMS_BY_ROW[ROW])
        event = AD._resolve_ai_ai_proposal(
            {"type": "defensive_alliance", "proposer": "PapalStates", "target": "KingdomOfItaly"}, world)
        assert event is None or event.get("reason") != "client"


# ═══════════════════════════════════════════════════════════════════════
# What the rule leaves alone
# ═══════════════════════════════════════════════════════════════════════

def _run_turns(world, turns: int) -> None:
    """The series runner's in-process loop: the enemy phase and the AI–AI
    poll run inside `end_turn`."""
    from backend.commands.executor import CommandExecutor
    from backend.game_logic.turn_manager import TurnManager
    executor = CommandExecutor()
    tm = TurnManager(world, executor=executor)
    game_state = {"world": world, "executor": executor}
    with _quiet():
        for turn in range(turns):
            random.seed(10_000 + turn)
            tm.end_turn(game_state)


class TestWhatTheRuleLeavesAlone:
    def test_a_pact_already_standing_stands(self, world):
        """The rule is a gate on signing, never a dissolution: a pact a
        court brought into its vassalage is read by nobody here."""
        key = world._make_diplo_key("PapalStates", "KingdomOfItaly")
        world.diplomatic_states[key] = "DEFENSIVE_ALLIANCE"
        assert AD._evaluate_ai_ai_proposal("PapalStates", "KingdomOfItaly", world) is None \
            or AD._evaluate_ai_ai_proposal("PapalStates", "KingdomOfItaly", world)["type"] not in (
                "defensive_alliance", "alliance")
        _run_turns(world, 1)
        assert world.diplomatic_states[key] == "DEFENSIVE_ALLIANCE"

    def test_the_clients_wars_are_its_lords_as_before(self, world):
        """The kingdom boots in its lord's war with Austria — the rule reads
        no war and ends none."""
        assert _state(world, "France", "Austria") == "WAR"
        assert _state(world, "KingdomOfItaly", "Austria") == "WAR"

    def test_the_players_own_proposals_never_pass_here(self):
        """The read sits at the two court-to-court sites and nowhere else:
        the player's road (the Cabinet, the wizard, the acceptance formula)
        is not gated — the Emperor may still offer any court what he likes."""
        callers = sorted(
            p.relative_to(REPO).as_posix() for p in (REPO / "backend").rglob("*.py")
            if "client_in_the_pair(" in p.read_text(encoding="utf-8"))
        assert callers == ["backend/game_logic/ai_diplomacy.py"]
        source = (REPO / "backend" / "game_logic" / "ai_diplomacy.py").read_text(encoding="utf-8")
        # the definition and its two sites
        assert source.count("client_in_the_pair(world, ") == 3

    def test_the_lords_own_pacts_are_untouched(self, world):
        """France's allies stay hers, and a lord signs for his house: the
        gate reads the pair's courts, never their houses' other treaties."""
        assert _state(world, "France", "Bavaria") == "ALLIANCE"
        with pytest.MonkeyPatch.context() as m:
            m.setattr(AD, "_evaluate_ai_ai_triggers",
                      lambda a, b, w: {"type": "defensive_alliance", "proposer": a, "target": b})
            _as_client(world, "Hesse", "Prussia")
            assert AD._evaluate_ai_ai_proposal("Prussia", "Sweden", world) == {
                "type": "defensive_alliance", "proposer": "Prussia", "target": "Sweden"}
            assert AD._evaluate_ai_ai_proposal("Hesse", "Sweden", world) is None

    def test_the_alarm_said_it_first(self):
        """The idiom the rule joins: a client neither gives nor is given a
        guarantee — "its lord answers for it" (T4-1)."""
        from backend.game_logic import alarm
        assert "its lord answers for it" in inspect.getsource(alarm)


# ═══════════════════════════════════════════════════════════════════════
# The words on the Vassals card
# ═══════════════════════════════════════════════════════════════════════

class TestTheVassalsCardSaysIt:
    def test_every_clients_card_carries_the_line(self, world):
        rows = DL.build_diplomatic_ledger(world)["vassals"]["rows"]
        assert sorted(r["name"] for r in rows) == ["Holland", "KingdomOfItaly", "Switzerland"]
        assert {r["policy_line"] for r in rows} == {
            "Its wars are yours: it signs no alliance of its own."}

    def test_the_seam_down_says_nothing(self, world, monkeypatch):
        hold_down(monkeypatch, T3_SEAMS_BY_ROW[ROW])
        rows = DL.build_diplomatic_ledger(world)["vassals"]["rows"]
        assert {r["policy_line"] for r in rows} == {""}

    def test_the_client_renders_the_backends_words(self):
        """R7: the card prints the payload's line, composing none of its own."""
        script = (REPO / "godot-client" / "project-sovereign" / "scripts"
                  / "diplomatic_ledger.gd").read_text(encoding="utf-8")
        assert 'v.get("policy_line", "")' in script
        assert "signs no alliance" not in script


# ═══════════════════════════════════════════════════════════════════════
# The seam
# ═══════════════════════════════════════════════════════════════════════

class TestTheSeam:
    def test_the_rule_has_its_row_and_ships_up(self):
        assert AD.a_client_swears_no_pact_of_its_own() is True
        assert inspect.signature(AD.a_client_swears_no_pact_of_its_own).parameters == {}
        assert T3_SEAMS_BY_ROW[ROW] == [
            "backend.game_logic.ai_diplomacy:a_client_swears_no_pact_of_its_own=False"]

    def test_the_row_joins_the_recorded_boards_hold_list(self):
        from tests._oct27_seams import OCT27_SEAMS_DOWN
        assert T3_SEAMS_BY_ROW[ROW][0] in OCT27_SEAMS_DOWN

    def test_the_one_read_sits_at_both_sites(self):
        assert "client_in_the_pair(world, nation_a, nation_b)" in inspect.getsource(AD._evaluate_ai_ai_proposal)
        assert "client_in_the_pair(world, initiator, target)" in inspect.getsource(AD._resolve_ai_ai_proposal)
        assert "a_client_swears_no_pact_of_its_own()" in inspect.getsource(AD.client_in_the_pair)


def _record(name: str) -> dict:
    return json.loads((REPO / "tools" / name).read_text(encoding="utf-8"))


def _dump(row) -> str:
    return json.dumps(row, sort_keys=True)


# ═══════════════════════════════════════════════════════════════════════
# The session's measure — ONE sweep, two arms, three surfaces, the series
# (`tools/_g3_measure.py`, `tools/_g3_series_arms.py`, `tools/_g3_client_
# pacts.py`). Seeded paths, not laws (DYNAMISM_SPEC.md §7c;
# SYSTEMS_REFERENCE.md §209).
# ═══════════════════════════════════════════════════════════════════════

SEEDS = ("austerlitz", "eylau", "friedland", "historical", "jena", "lodi",
         "marengo", "rivoli", "ulm", "wagram")
STAMP = "2026_11_11"
ARM_NAMES = ("0", "CLIENT")
AMBIENT_LABELS = {"0": "g3_control", "CLIENT": "g3"}


class TestTheSessionG3Measure:
    """Written from the records after the sweep ran ALONE. Arm 0 reproduces
    session G2; arm CLIENT is the shipped tree."""

    def _sig(self, label: str) -> dict:
        return _record(f"_dy_signature_{label}_{STAMP}.json")

    def _census(self, label: str) -> dict:
        return _record(f"_{label}_census_{STAMP}.json")

    def _harness(self) -> dict:
        return _record(f"_g3_chain_d_{STAMP}.json")

    def test_arm_0_reproduces_session_g2_on_both_surfaces(self):
        g2, ctl = self._sig("g2"), self._sig("g3_control")
        for seed in SEEDS:
            assert _dump(ctl["seeds"][seed]) == _dump(g2["seeds"][seed]), seed
        assert _dump(self._census("g3_control")["seeds"]) == _dump(self._census("g2")["seeds"])
        prior = _record(f"_g2_chain_d_{STAMP}.json")["arms"]["ALL"]
        assert _dump(self._harness()["arms"]["0"]) == _dump(prior)

    def test_the_unattended_board_does_not_move(self):
        """Ambient: the idle France's kingdom falls to Austria in the
        Emperor's own war on every seed before a client's pact matters — not
        one seed's signature or census moves."""
        ctl, shipped = self._sig("g3_control"), self._sig("g3")
        assert [s for s in SEEDS if _dump(shipped["seeds"][s]) != _dump(ctl["seeds"][s])] == []
        assert _dump(self._census("g3")["seeds"]) == _dump(self._census("g3_control")["seeds"])

    def test_the_gate_reads_met_on_the_shipped_arm(self):
        shipped, census = self._sig("g3"), self._census("g3")
        assert shipped["story_class_count"] == 10
        promoted = {s: shipped["seeds"][s]["signature"]["rank_promotions"] for s in SEEDS
                    if shipped["seeds"][s]["signature"]["rank_promotions"]}
        assert promoted == {"lodi": [[33, "Hesse"]], "marengo": [[40, "Hesse"]]}
        rosters = {s: tuple(n for _, n in shipped["seeds"][s]["signature"]["eliminations"]) for s in SEEDS}
        assert sorted(s for s, r in rosters.items() if r == ("KingdomOfItaly", "PapalStates")) == ["jena", "wagram"]
        assert all(r == ("KingdomOfItaly",) for s, r in rosters.items() if s not in ("jena", "wagram"))
        assert census["totals"]["annexations_outside_aim"] == 0
        assert (census["totals"]["captures_outside_aim"], census["totals"]["rank_promotions"]) == (266, 2)

    def test_the_band_does_not_move(self):
        band = _record(f"_g3_band_{STAMP}.json")
        for arm in ARM_NAMES:
            arms = band["arms"][arm]
            assert [arms[n]["provinces"] for n in ("CMD-H", "CMD-A", "CMD-M")] == [28, 27, 25], arm

    def test_the_harness_annexation_line_reads_nothing(self):
        """THE CURE. The AI-France harness read 4 provinces kept outside aim
        on session G2's tree — the cast Naples keeping Milan and Piedmont on
        jena and wagram, the soil of the Emperor's erased client. With the
        rule the kingdom is never called into the Roman war: 0, and no court
        but the harness's own France keeps a province outside aim."""
        mine = self._harness()
        assert [mine["totals"][a]["annexations_outside_aim"] for a in ARM_NAMES] == [4, 0]
        for seed in SEEDS:
            kept = mine["arms"]["CLIENT"][seed]["annexations_outside_aim_by_court"]
            assert set(kept) <= {"France"}, seed
        for seed, fell in (("jena", [[13, "Austria"], [26, "PapalStates"]]),
                           ("wagram", [[10, "Austria"], [17, "PapalStates"]])):
            assert mine["arms"]["CLIENT"][seed]["eliminations"] == fell
            assert "KingdomOfItaly" in [n for _, n in mine["arms"]["0"][seed]["eliminations"]]

    def test_the_harness_moves_seven_seeds(self):
        mine = self._harness()
        moved = [s for s in SEEDS if _dump(mine["arms"]["CLIENT"][s]) != _dump(mine["arms"]["0"][s])]
        assert moved == ["friedland", "historical", "jena", "lodi", "marengo", "rivoli", "wagram"]
        for arm in ARM_NAMES:
            totals = mine["totals"][arm]
            assert (totals["rank_promotions"], totals["crowns_erected"], totals["recognitions"]) == (0, 0, 0), arm
        assert [mine["totals"][a]["captures_outside_aim"] for a in ARM_NAMES] == [133, 135]
        assert [mine["totals"][a]["france_outside_aim"] for a in ARM_NAMES] == [189, 187]
        final = {a: {s: mine["arms"][a][s]["france_provinces_final"] for s in SEEDS} for a in ARM_NAMES}
        assert {s: (final["0"][s], final["CLIENT"][s]) for s in SEEDS
                if final["0"][s] != final["CLIENT"][s]} == {"jena": (40, 42), "marengo": (45, 46)}

    def test_a_freed_kingdom_no_longer_proclaims_italy_on_its_old_pacts(self):
        """REPORTED, a consequence of the rule: on session G2's tree a Kingdom
        of Italy that broke free of the harness's France proclaimed ITALY the
        same turn on four seeds — its Risorgimento (Milan, Piedmont, Savoy,
        Naples, Rome) read as gathered because Rome, Naples and Savoy stood
        in the blocs of the pacts it had signed as a client (the ally clause,
        session G's defect through a sleeping deck). With the rule it leaves
        its vassalage with no pact and the design is a live want: no seed
        proclaims Italy in forty turns. The United Netherlands (Flanders,
        taken by arms) still forms."""
        mine = self._harness()
        formed = {a: {s: mine["arms"][a][s]["formations"] for s in SEEDS if mine["arms"][a][s]["formations"]}
                  for a in ARM_NAMES}
        assert sorted(s for s, f in formed["0"].items() if "KingdomOfItaly" in f) == [
            "friedland", "historical", "marengo", "rivoli"]
        assert [s for s, f in formed["CLIENT"].items() if "KingdomOfItaly" in f] == []
        assert sorted(s for s, f in formed["0"].items() if "Holland" in f) == [
            "austerlitz", "eylau", "friedland", "marengo"]
        assert sorted(s for s, f in formed["CLIENT"].items() if "Holland" in f) == [
            "austerlitz", "eylau", "friedland", "marengo", "wagram"]

    def test_the_pacts_the_rule_stops(self):
        """Read off the kept runs: nineteen client pacts on session G2's tree
        — the kingdom with Rome on every seed (turns 7–9), with Bavaria on
        nine — and none with the rule. Three courts change lords on both arms
        (Russia buys the kingdom on eylau and lodi, Switzerland on lodi): an
        AI lord's clients, bound alike."""
        record = _record(f"_g3_client_pacts_{STAMP}.json")
        assert record["totals"] == {"0": {"client_pacts": 19, "transfers": 3},
                                    "CLIENT": {"client_pacts": 0, "transfers": 3}}
        rows = [p for seed in SEEDS for p in record["arms"]["0"][seed]["client_pacts"]]
        assert {(p[1], p[2]) for p in rows} == {("KingdomOfItaly", "France")}
        assert sorted(p[3] for p in rows).count("PapalStates") == 10
        assert sorted(p[3] for p in rows).count("Bavaria") == 9
        assert {p[0] for p in rows if p[3] == "PapalStates"} <= {7, 8, 9}
        assert record["arms"]["CLIENT"]["lodi"]["transfers"] == [
            [19, "KingdomOfItaly", "France", "Russia"], [21, "Switzerland", "France", "Russia"]]

    def test_the_series_does_not_move_and_the_rule_bites_on_the_rig(self):
        series = _record("_g3_series_arms_final.json")
        for arm in ARM_NAMES:
            row = series["arms"][arm]
            assert row["first_divergence_vs_prior"] is None, arm
            counts = row["reach"]["counts"]
            assert (counts["pacts_polled"], counts["client_bites"]) == (3339, 735), arm
            assert counts["client_seam_reads"] > 5000, arm
        assert series["arms"]["0"]["series"] == series["arms"]["CLIENT"]["series"] == series["prior"]
