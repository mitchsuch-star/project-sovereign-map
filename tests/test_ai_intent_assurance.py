"""AI-V — Stage G assurance (docs/AI_INTENT_SPEC.md §4.7, §7, §11 Stage G).

The phase-closing pin set, run against the committed sweep driver
(tools/ai_v_sweep.py — the same runner the offline memo sweep uses):

  Arm A  — control: two separate processes at the same SOVEREIGN_SEED and
           the same ambient constant K produce a byte-identical digest,
           and the runner's threat series IS the standing BASELINE_SERIES
           (the pin-16a anchor) — if Arm A is red, nothing else in the
           sweep means anything.
  Arm B  — variance: a different seed at the SAME K differs in turn-0
           dispositions and in the spec's own triple {AI-initiated war
           count, the turns wars begin, which courts reach `fight`}
           (evaluated as at-least-one, per §4.7).
  Arm (a) — the 40-turn ambient acceptance digest carries the DoD
           assertions a passive France can honestly measure: the D1
           channel discrimination and alarm, the Q3 economy shapes, the
           narration cap in the wild, the downward mirror, the courting
           stream, the beat texture, pin 21's run-level half, and the
           formation predicate's machine-readable absence explanation.
  Arm (b) — the scripted France: all three D5 instruments through the
           real executor gates, the pin-21 bought-off receipt on a live
           foregrounded crisis, the reneged compensation (beat 4), the
           volte-face signed through the conflict confirm (beat 5, scene
           4) with the §12.2 deck advance, and the §3.5 upward mirror.
  Q2     — the multi-front fixture set (spec §13): two simultaneous wars
           for one nation resolve independently — settlement tracks,
           armistice isolation, exhaustion persistence, and the
           max-not-sum rear reserve.
  Kits   — the MC-V both-sides pattern: the intent kit derives for AI
           courts, and every player-facing counterpart surface exists.

The full N-seed acceptance distribution (Arm C) and the scored creative
pass live in the sweep memo (docs/audits/AI_V_SWEEP_2026_08_01.md); this
file pins what must never regress, at suite cost (~4 subprocess runs).

NOTE: the Arm-A threat anchor imports BASELINE_SERIES from
test_ai_intent_threat_migration — a conscious re-record there flows here
automatically (one constant, two consumers).
"""

import importlib.util
import json
from pathlib import Path

import pytest

from backend.game_logic.diplomacy import declare_war, set_diplomatic_state
from backend.game_logic.instruments import grant_directed_sponsorship
from backend.game_logic.intent import (
    PRICE_LADDER,
    get_france_perceived_intent,
    get_nation_intent,
    rung_index,
)
from backend.game_logic.war_council import (
    SWEEP_WAR_ALARM,
    get_exposure_view,
)
from backend.models.world_state import WorldState

REPO_ROOT = Path(__file__).resolve().parents[1]
SCENARIO_PATH = (REPO_ROOT / "godot-client" / "project-sovereign"
                 / "assets" / "maps" / "europe_1805.json")


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


sweep = _load_module("ai_v_sweep_tool", REPO_ROOT / "tools" / "ai_v_sweep.py")
_baseline_mod = _load_module(
    "ai_v_baseline_src",
    REPO_ROOT / "tests" / "test_ai_intent_threat_migration.py")
BASELINE_SERIES = _baseline_mod.BASELINE_SERIES

MAJORS = ("Austria", "Prussia", "Russia", "Britain")


# ═══════════════════════════════════════════════════════════════════════
# The four suite runs (module-scoped — the whole file shares them)
# ═══════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="module")
def hist1():
    return sweep.spawn_run("historical", sweep.AMBIENT_K, 40)


@pytest.fixture(scope="module")
def hist2():
    return sweep.spawn_run("historical", sweep.AMBIENT_K, 40)


@pytest.fixture(scope="module")
def ulm():
    return sweep.spawn_run("ulm", sweep.AMBIENT_K, 40)


@pytest.fixture(scope="module")
def scripted():
    return sweep.spawn_run("historical", sweep.AMBIENT_K, 24,
                           script="france")


@pytest.fixture(scope="module")
def world1805():
    return WorldState.from_scenario(str(SCENARIO_PATH))


@pytest.fixture()
def world(world1805):
    return WorldState.from_dict(world1805.to_dict())


# ═══════════════════════════════════════════════════════════════════════
# Arm A — control
# ═══════════════════════════════════════════════════════════════════════

class TestArmAControl:
    def test_two_processes_byte_identical(self, hist1, hist2):
        """§4.7 Arm A: same seed, same K, two separate processes — the
        whole digest (boot, every per-turn record, final, derived) is
        byte-identical. If this is red, nothing else means anything."""
        view1 = json.dumps(sweep._control_view(hist1), sort_keys=True)
        view2 = json.dumps(sweep._control_view(hist2), sort_keys=True)
        assert view1 == view2

    def test_threat_series_is_the_standing_baseline(self, hist1):
        """The runner's ambient schedule IS the pin-16a baseline: boot
        threat + the 40 per-turn readings equal BASELINE_SERIES verbatim
        — so every arm-(a) assertion below is measured on the exact
        trace the standing threat pin already guards."""
        series = [hist1["boot"]["threat"]] + hist1["derived"]["threat_series"]
        assert series == BASELINE_SERIES

    def test_meta_records_the_ambient_contract(self, hist1):
        assert hist1["meta"]["seed"] == "historical"
        assert hist1["meta"]["ambient_base"] == sweep.AMBIENT_K
        assert hist1["meta"]["turns"] == 40
        assert hist1["meta"]["script"] is None


# ═══════════════════════════════════════════════════════════════════════
# Arm B — variance
# ═══════════════════════════════════════════════════════════════════════

class TestArmBVariance:
    def test_turn0_dispositions_differ(self, hist1, ulm):
        """D7/§3.8: a different seed opens a different 1805 — within the
        authored bands (the historian test guards the bounds; this pin
        guards that variance EXISTS at all)."""
        assert ulm["boot"] != hist1["boot"]
        assert ulm["boot"]["relations"] != hist1["boot"]["relations"]

    def test_the_spec_triple_differs(self, hist1, ulm):
        """§4.7 Arm B: at the SAME ambient K the runs differ in at least
        one of {AI-initiated war count, the turns wars begin, which
        courts reach fight} — attributable to the seed, not to combat
        noise."""
        sig_h = sweep._variance_signature(hist1)
        sig_u = sweep._variance_signature(ulm)
        assert sig_h != sig_u, (
            "two seeds produced identical war counts, war turns AND "
            "fight-rung courts — the variance slice failed (§4.7)")

    def test_intent_weight_series_differ(self, hist1, ulm):
        """The bars move (weights/prices), never the character (both
        decks stay the authored 1805 content — Tier 1)."""
        assert any(
            row_h["intents"] != row_u["intents"]
            for row_h, row_u in zip(hist1["turns"], ulm["turns"]))

    def test_tier1_decks_are_seed_invariant(self, hist1, ulm):
        """§3.8.1: deck CONTENT is Tier-1 fixed — the seed may reorder
        equally-live designs, never author new ones."""
        decks_h = {n: sorted(d) for n, d in hist1["boot"]["decks"].items()}
        decks_u = {n: sorted(d) for n, d in ulm["boot"]["decks"].items()}
        assert decks_h == decks_u


# ═══════════════════════════════════════════════════════════════════════
# Arm (a) — the ambient acceptance digest (DoD lines a passive France
# can honestly measure)
# ═══════════════════════════════════════════════════════════════════════

class TestArmAAmbientDoD:
    def test_d1_channel_discrimination_and_alarm(self, hist1):
        """AI-3r §8.2 / D1: council wars are counted by the ai_initiated
        flag ONLY (the un-counselled combat-seam channel is recorded
        separately, never credited to the council), and the run stays
        inside the suite alarm."""
        derived = hist1["derived"]
        assert len(derived["ai_initiated_wars"]) <= SWEEP_WAR_ALARM
        for war in derived["ai_initiated_wars"]:
            assert war["stated_reason"], (
                "an AI-initiated war must carry a reason the ledger "
                "renders (§7)")
        for war in derived["seam_ai_ai_wars"]:
            assert not war["ai_initiated"]

    def test_q3_no_solvent_at_war_major_sits_idle(self, hist1):
        """§13 Q2/Q3: over 40 turns, no major that spent most of the run
        at war with a positive purse recorded zero recruit/commission
        activity."""
        derived = hist1["derived"]
        turns = hist1["turns"]
        for major in MAJORS:
            at_war_turns = sum(
                1 for row in turns if int(row["exhaustion"].get(major, 0)) > 0)
            mean_gold = sum(
                int(row["gold"].get(major, 0)) for row in turns) / len(turns)
            if at_war_turns >= 30 and mean_gold > 0:
                assert derived["recruit_turns"].get(major), (
                    f"{major} fought ~{at_war_turns} turns solvent and "
                    f"never recruited — the Q3 failure shape")

    def test_q3_no_commission_into_bankruptcy(self, hist1):
        """The P1.75 pre-budget gate holds in the wild: every commission
        leaves the treasury non-negative that turn."""
        for row in hist1["derived"]["commissions"]:
            assert row["gold_after"] >= 0, row

    def test_commissions_fire_ambient(self, hist1):
        """The Marshalate's AI rung is alive in the ambient world (the
        boot attrition has a recovery path both sides)."""
        assert hist1["derived"]["commissions"], (
            "no marshal commissioned in 40 ambient turns")

    def test_narration_cap_holds_in_the_wild(self, hist1):
        """AI-6: at most INTENT_DISPATCH_CAP routine intent lines per
        dispatch, every turn of the run (the tail rides its own type)."""
        assert hist1["derived"]["routine_intent_lines_max_per_turn"] <= 2

    def test_mirror_drifts_down_for_a_passive_france(self, hist1):
        """§3.5 (arm (a) half): a France that does nothing drifts DOWN
        the perceived ladder — rung and weight both fall over the run."""
        series = hist1["derived"]["mirror_series"]
        first_price, first_weight, _ = series[0]
        last_price, last_weight, _ = series[-1]
        assert last_weight < first_weight
        assert rung_index(last_price) < rung_index(first_price)

    def test_the_player_is_courted(self, hist1):
        """§4.2b: the participation surface is alive — the passive run
        still receives a steady courting/ask stream addressed to
        France."""
        proposals = hist1["derived"]["proposals_to_france"]
        assert len(proposals) >= 10
        if hist1["derived"]["ai_initiated_wars"]:
            assert proposals, "an AI war fired and France was never asked"

    def test_soap_opera_share_is_measured(self, hist1):
        """§5 pin 13: reported as a number, never asserted as a feel.
        The memo carries the value; the pin guards that it exists and is
        a real share."""
        share = hist1["derived"]["soap_opera_share"]
        lines = hist1["derived"]["soap_opera_lines"]
        assert 0.0 < share <= 1.0
        assert lines[1] >= lines[0] >= 0

    def test_ambient_beat_texture(self, hist1):
        """Stage E lives ambient: emergent designs promote, wants shift,
        and non-France pairs make peace on their own (beat 6)."""
        beats = hist1["derived"]["beats"]
        assert beats.get("design_promoted", 0) >= 1
        assert beats.get("agenda_shift", 0) >= 1
        assert beats.get("third_party_peace", 0) >= 1

    def test_pair_peace_is_exhaustion_driven(self, hist1):
        """The DoD's 'somebody bleeds and Europe notices': each pair
        peace between non-France courts follows a rising exhaustion
        window for both parties."""
        peaces = hist1["derived"]["pair_peaces"]
        assert peaces, "no third-party pair peace in 40 ambient turns"
        for peace in peaces:
            assert peace["both_rose"], peace

    def test_formation_absence_carries_its_predicate(self, hist1):
        """§7: '≥1 formation, or a written explanation of the specific
        predicate that blocked it' — the watch payload IS the
        machine-readable explanation (e.g. Holland's deck latent while
        vassalized)."""
        final = hist1["final"]
        if not final["formations"]:
            watches = final["formation_watch"]
            assert watches, "no formation AND no watch to explain why"
            assert any(
                watch.get("blocked_by_vassalage") or watch.get("progress")
                for watch in watches.values())

    def test_pin21_no_crisis_vanishes_silently(self, hist1, scripted):
        """Pin 21 (run-level half): a FOREGROUNDED war-intent record
        never disappears without either its war opening or a
        crisis_passed receipt naming the cause."""
        for digest in (hist1, scripted):
            self._assert_no_silent_vanish(digest)

    @staticmethod
    def _assert_no_silent_vanish(digest):
        turns = digest["turns"]
        for prev, curr in zip(turns, turns[1:]):
            for nation, record in prev["war_intents"].items():
                if not record.get("foregrounded"):
                    continue
                if nation in curr["war_intents"]:
                    continue
                receipt = any(
                    str(e.get("type")) == "crisis_passed"
                    and e.get("nation") == nation
                    for e in curr["events"])
                war_opened = any(
                    nation in (w["attackers"] + w["defenders"])
                    for w in curr["wars_opened"])
                assert receipt or war_opened, (
                    f"{nation}'s foregrounded crisis vanished silently "
                    f"at turn {curr['turn']} (pin 21)")

    def test_homogeneity_guard_holds_in_wartime(self, hist1):
        """§5 pin 10's WARTIME half (the aliveness file owns peacetime):
        over a 40-turn run with wars live, no two majors reduce to the
        same behavioural histogram."""
        histograms = {}
        for major in MAJORS:
            counter = {}
            for row in hist1["turns"]:
                for event in row["events"]:
                    involved = (
                        event.get("nation") == major
                        or event.get("payer") == major
                        or event.get("proposer") == major
                        or event.get("accepter") == major)
                    if involved:
                        etype = str(event.get("type"))
                        counter[etype] = counter.get(etype, 0) + 1
            histograms[major] = counter
        for index, first in enumerate(MAJORS):
            for second in MAJORS[index + 1:]:
                assert histograms[first] != histograms[second], (
                    f"{first} and {second} produced identical event "
                    f"histograms — the homogeneity guard (§3.4)")

    def test_in_character_observables(self, hist1):
        """§3.4 in-character, the ambient-observable half: Britain pays
        for a war (the paymaster), and Prussia's court passes through
        the bandwagon posture (the bandwagoner). Austria's bloc-building
        and Russia's arbitration are peacetime-file/memo territory."""
        subsidy_events = [
            e for row in hist1["turns"] for e in row["events"]
            if str(e.get("type")) == "british_subsidy"
            and e.get("payer") == "Britain"]
        assert subsidy_events, "Britain never paid a subsidy in 40 turns"
        prussia_prices = {
            row["intents"]["Prussia"][3]
            for row in hist1["turns"] if "Prussia" in row["intents"]}
        assert "bandwagon" in prussia_prices or "align" in prussia_prices


# ═══════════════════════════════════════════════════════════════════════
# Arm (b) — the scripted France
# ═══════════════════════════════════════════════════════════════════════

class TestArmBScriptedFrance:
    def test_all_three_d5_instruments_through_real_gates(self, scripted):
        """Sponsor, guarantee and buy-off each exercised once through the
        executor's own verbs, successfully."""
        log = {entry["step"]: entry for entry in scripted["script_log"]}
        assert log["sponsor_design Prussia->Hanover 100g"]["success"]
        assert log["guarantee_nation Hanover"]["success"]
        assert log["buy_off_design Prussia (live crisis)"]["success"]

    def test_instrument_lifecycles_are_on_the_record(self, scripted):
        """Sponsorships expire (10-turn term) and the reneged bargain is
        pruned, so the FINAL stores cannot pin them — the lifecycle
        events can: the grant, the pledge (whose record does stand), and
        the renege that proves the bargain lived."""
        events = [e for row in scripted["turns"] for e in row["events"]]
        assert any(str(e.get("type")) == "sponsorship_granted"
                   and e.get("payer") == "France" for e in events)
        assert any(str(e.get("type")) == "guarantee_pledged"
                   and e.get("guarantor") == "France" for e in events)
        assert any(r.get("guarantor") == "France"
                   for r in scripted["final"]["diplomatic_guarantees"])
        assert any(str(e.get("type")) == "bargain_reneged" for e in events)

    def test_ai_ai_instrument_economy_is_alive_ambient(self, hist1):
        """Stage C's AI sponsor branch in the wild: the majors run the
        D5 economy among THEMSELVES on the passive run (Britain and
        Russia funding clients unprompted)."""
        payers = {e.get("payer")
                  for row in hist1["turns"] for e in row["events"]
                  if str(e.get("type")) == "sponsorship_granted"}
        assert payers & set(MAJORS)

    def test_pin21_receipt_names_the_instrument(self, scripted):
        """Beat 2 opened a live foregrounded crisis; France bought it
        off; beat 7 fired with cause=bought_off — the deterrence
        receipt, instrument-credited (§12.1)."""
        beats = scripted["derived"]["beats"]
        assert beats.get("crisis_brewing", 0) >= 1
        assert beats.get("crisis_passed", 0) >= 1
        causes = {c.get("cause") for c in scripted["derived"]["crisis_passed"]}
        assert "bought_off" in causes

    def test_renege_fires_beat_4(self, scripted):
        """France broke its own compensation by declaring on the
        recipient — the broken-bargain beat fired (dispatch stream) and
        the grievance events are on the log."""
        assert scripted["derived"]["beats"].get("broken_bargain", 0) >= 1
        renege_events = [
            e for row in scripted["turns"] for e in row["events"]
            if str(e.get("type")) in ("bargain_reneged",
                                      "sponsorship_reneged")]
        assert renege_events

    def test_volte_face_signed_and_aimed_at_a_third_party(self, scripted):
        """Scene 4 end-to-end IN A RUN: the beaten-then-courted power
        proposed the alliance itself (decision_reason=volte_face), the
        conflict confirm signed it, beat 5 fired, and the §12.2 deck
        advance aims the reversed power at a third party."""
        volte_proposals = [
            p for p in scripted["derived"]["proposals_to_france"]
            if p["decision_reason"] == "volte_face"]
        assert volte_proposals and volte_proposals[0]["proposer"] == "Russia"
        volte_events = scripted["derived"]["volte_faces"]
        assert volte_events
        event = volte_events[0]
        assert event.get("nation") == "Russia"
        assert event.get("partner") == "France"
        assert event.get("next_design") == "gulf_and_straits"
        late_intents = [row["intents"].get("Russia")
                       for row in scripted["turns"][-5:]]
        assert any(view and view[0] == "gulf_and_straits"
                   and view[1] not in (None, "France")
                   for view in late_intents)

    def test_mirror_moves_upward_for_an_acting_france(self, scripted, hist1):
        """§3.5's upward half: the renege war RAISES Europe's reading of
        France above its own passive trajectory — the mirror is a
        surprise engine, not a decay counter."""
        scripted_series = scripted["derived"]["mirror_series"]
        weights = [row[1] for row in scripted_series]
        declaration_index = 3  # the France->Prussia renege turn
        assert max(weights[declaration_index:declaration_index + 3]) > \
            weights[declaration_index - 1]
        passive_at_same_turn = hist1["derived"]["mirror_series"][5][1]
        assert max(weights[3:8]) > passive_at_same_turn

    def test_ports_closed_and_membership_stands(self, scripted):
        assert scripted["final"]["continental_system_members"]

    def test_outbid_attempt_recorded_honestly(self, scripted):
        """Scene 5's France-bidding half: the verb REFUSES to bankroll an
        active belligerent (by design — the honest gate), and the D5
        record staged at the instruments seam is the bid the subsidy
        pass reads (coalition.py's outbid arm)."""
        steps = {entry["step"]: entry for entry in scripted["script_log"]
                 if "outbid" in entry["step"]}
        verb = next(v for k, v in steps.items() if "verb attempt" in k)
        seam = next(v for k, v in steps.items() if "staged at seam" in k)
        assert verb["success"] is False
        assert seam["success"] is True


# ═══════════════════════════════════════════════════════════════════════
# Q2 — the multi-front assertion set (spec §13, tracked here by name)
# ═══════════════════════════════════════════════════════════════════════

class TestQ2MultiFront:
    @staticmethod
    def _open_two_fronts(world):
        """Prussia attacks Hanover; Denmark attacks Prussia. Two
        DISTINCT instances with Prussia in both — same-originator
        declarations fold into one instance (the [r5] boot idiom), a
        reversed originator does not (measured)."""
        result_a = declare_war(world, "Prussia", "Hanover")
        result_b = declare_war(world, "Denmark", "Prussia")
        assert result_a.get("success") and result_b.get("success")
        instances = world.war_instances
        war_a = next(wid for wid, inst in instances.items()
                     if set((inst.get("side_by_nation") or {}))
                     == {"Prussia", "Hanover"})
        war_b = next(wid for wid, inst in instances.items()
                     if set((inst.get("side_by_nation") or {}))
                     == {"Denmark", "Prussia"})
        return war_a, war_b

    def test_two_wars_two_instances_both_tracked(self, world):
        war_a, war_b = self._open_two_fronts(world)
        assert war_a != war_b
        at_war = set(world.get_nations_at_war_with("Prussia"))
        assert {"Hanover", "Denmark"} <= at_war

    def test_peace_on_front_a_never_mutates_front_b(self, world):
        """The named edge case: front A's peace leaves front B's
        war_instance byte-identical and the pair still at war."""
        war_a, war_b = self._open_two_fronts(world)
        snapshot_b = json.dumps(world.war_instances[war_b], sort_keys=True,
                                default=str)
        set_diplomatic_state(world, "Prussia", "Hanover", "PEACE",
                             "q2_fixture")
        assert json.dumps(world.war_instances[war_b], sort_keys=True,
                          default=str) == snapshot_b
        assert "Denmark" in world.get_nations_at_war_with("Prussia")
        assert world.get_diplomatic_state("Prussia", "Denmark") == "WAR"

    def test_armistice_on_front_a_while_front_b_burns(self, world):
        war_a, war_b = self._open_two_fronts(world)
        snapshot_b = json.dumps(world.war_instances[war_b], sort_keys=True,
                                default=str)
        set_diplomatic_state(world, "Prussia", "Hanover", "ARMISTICE",
                             "q2_fixture")
        assert json.dumps(world.war_instances[war_b], sort_keys=True,
                          default=str) == snapshot_b
        assert world.get_diplomatic_state("Prussia", "Denmark") == "WAR"

    def test_exhaustion_survives_a_partial_peace(self, world):
        """The R49 shed rule pops exhaustion only when the LAST war ends
        — front A's peace must not reset the bill while front B burns
        (the cross-war state-bleed shape)."""
        self._open_two_fronts(world)
        world.war_exhaustion["Prussia"] = 50
        set_diplomatic_state(world, "Prussia", "Hanover", "PEACE",
                             "q2_fixture")
        assert world.war_exhaustion.get("Prussia") == 50, (
            "front A's peace reset the war bill while front B burns")

    def test_rear_reserve_is_max_not_sum(self, world):
        """The §6.1 Q2 ruling, pinned in-world (a cross-world comparison
        confounds on third-party relation drift — two aggressive
        declarations cool Russia a band and the worst single menace
        legitimately grows): the reserve reads min(the WORST single
        menace, the 60% cap) — never the sum of the threat list."""
        self._open_two_fronts(world)
        world.invalidate_bloc_members_cache()
        view = get_exposure_view(world, "Prussia")
        menaces = [t["menace"] for t in view["threats"]]
        assert len(menaces) >= 2
        assert view["worst_menace"] == max(menaces)
        assert view["reserve"] == min(
            view["worst_menace"], int(0.60 * view["standing"]))

    def test_rear_reserve_max_not_sum_unclamped(self, world):
        """The falsifying case where the cap cannot mask a summing
        implementation: boot Prussia's worst menace (Russia, ~29k) sits
        BELOW its 60% cap with a multi-entry threat list — so a summing
        reserve would read strictly higher than the max."""
        view = get_exposure_view(world, "Prussia")
        menaces = [t["menace"] for t in view["threats"]]
        assert len(menaces) >= 2
        assert view["worst_menace"] < int(0.60 * view["standing"]), (
            "fixture drifted: the cap binds, pick a different nation")
        assert view["reserve"] == view["worst_menace"] == max(menaces)
        assert view["reserve"] < sum(menaces), (
            "the reserve equals the whole threat-list sum — the reserve "
            "summed (§6.1 Q2)")

    def test_settlement_track_independence_through_the_real_machinery(
            self, world):
        """Simultaneous settlement tracks: force-settling front A through
        attempt_third_party_settlement leaves front B's instance
        untouched and its pair at war."""
        from backend.game_logic.settlement_third_party import (
            attempt_third_party_settlement,
        )
        war_a, war_b = self._open_two_fronts(world)
        # Give the loser a reason to sue on front A only.
        world.war_exhaustion["Hanover"] = 150
        snapshot_b = json.dumps(world.war_instances[war_b], sort_keys=True,
                                default=str)
        event = attempt_third_party_settlement(
            world, war_a, world.war_instances[war_a], force=True)
        if event is not None:
            assert event["war_id"] == war_a
        assert json.dumps(world.war_instances[war_b], sort_keys=True,
                          default=str) == snapshot_b
        assert world.get_diplomatic_state("Prussia", "Denmark") == "WAR"


# ═══════════════════════════════════════════════════════════════════════
# Both-sides kits (the MC-V pattern)
# ═══════════════════════════════════════════════════════════════════════

class TestBothSidesKits:
    def test_boot_intent_types_cover_the_families(self, world):
        """The derived kit spans the want families on the shipped 1805
        board: acquire (Prussia), deny (Britain), contain (Russia)."""
        types = {}
        for nation in ("Prussia", "Britain", "Russia"):
            view = get_nation_intent(nation, world)
            assert view.want_id, f"{nation} boots with no want"
            types[nation] = view.want_type
        assert types["Prussia"] == "acquire_regions"
        assert types["Britain"] == "deny_regions"
        assert types["Russia"] == "contain_hegemon"

    def test_every_boot_intent_reads_a_ladder_rung(self, world):
        for nation in world.get_active_nations():
            if nation == world.player_nation:
                continue
            view = get_nation_intent(nation, world)
            assert view.price in PRICE_LADDER

    def test_player_mirror_is_the_same_ladder(self, world):
        """§3.5: France's own reading rides the same rung vocabulary the
        AI kit uses — the player can be read exactly as the courts
        are."""
        price, weight, _target = get_france_perceived_intent(world)
        assert price in PRICE_LADDER
        assert 0 <= weight <= 100

    def test_player_d5_verbs_exist_for_every_instrument(self):
        from backend.ai.validation import VALID_ACTIONS
        for verb in ("sponsor_design", "buy_off_design", "guarantee_nation"):
            assert verb in VALID_ACTIONS

    def test_instrument_seam_is_side_agnostic(self, world):
        """GR5: the ONE directed record mints for an AI payer exactly as
        it does for France (Stage C's own AI sponsor branch consumes
        it)."""
        result = grant_directed_sponsorship(
            world, payer="Austria", recipient="Prussia", aim="Hanover",
            amount_per_turn=150)
        assert result["success"]
        record = world.directed_sponsorships[-1]
        assert record["payer"] == "Austria"
        assert record["recipient"] == "Prussia"

    def test_ai_war_and_player_war_share_the_instance_shape(self, world):
        """Both channels write the same war_instances vocabulary — the
        sweep's channel discrimination (ai_initiated) is a flag on a
        shared shape, not a parallel system."""
        declare_war(world, "Prussia", "Hanover")
        instance = next(
            inst for inst in world.war_instances.values()
            if set((inst.get("side_by_nation") or {}))
            == {"Prussia", "Hanover"})
        for key in ("attackers", "defenders", "side_by_nation",
                    "participant_meta", "ended_turn", "end_reason"):
            assert key in instance
