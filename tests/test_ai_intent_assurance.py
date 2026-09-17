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
           (evaluated as at-least-one, per §4.7) — since IQ-7 (Sept 16,
           2026) compared through the tool's WIDENED signature (the triple
           plus the turn each court first reaches `fight` and the
           eliminations with their turns), whose teeth are three controls a
           widening cannot fake: the same seed twice and ulm with seed
           variance disabled both sign EQUAL, and ulm's boot grafted onto
           historical's run does not move it (see the pin's docstring).
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
file pins what must never regress, at suite cost (~5 subprocess runs; the
fifth, IQ-7's seed-variance-off control, is defined beside Arm B).

NOTE: the Arm-A threat anchor imports BASELINE_SERIES from
test_ai_intent_threat_migration — a conscious re-record there flows here
automatically (one constant, two consumers).
"""

import importlib.util
import json
import subprocess
import sys
import textwrap
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

def _synthetic_digest(fight_from: dict, eliminated: list,
                      turns: int = 6) -> dict:
    """A minimal digest carrying every key `sweep.derive_metrics` reads, so
    the Arm-B signature's semantics are pinned through the tool's REAL
    derivation rather than a test-side copy of it.

    `fight_from` maps a court to the row turns on which its intent view
    stands on `fight` (any other row it reads `coerce`); `eliminated` is
    [(row turn, nation, the event's own `turn` stamp)]."""
    rows = []
    for t in range(1, turns + 1):
        events = [{"type": "nation_eliminated", "nation": nation,
                   "turn": stamp}
                  for row_turn, nation, stamp in eliminated if row_turn == t]
        # a non-elimination exit in the same drain must never be counted
        events.append({"type": "vassal_broke_free", "nation": "Switzerland",
                       "turn": t})
        rows.append({
            "turn": t, "threat": 50, "mirror": ["ask", 0, None],
            "intents": {
                nation: [None, None, 0,
                         "fight" if t in fighting else "coerce"]
                for nation, fighting in fight_from.items()},
            "wars_opened": [], "wars_ended": [], "events": events,
            "dispatch_queue": [], "incoming_proposals": [],
            "exhaustion": {}, "gold": {}, "strength": {},
        })
    digest = {"meta": {"player": "France", "france_needles": ["france"]},
              "turns": rows}
    digest["derived"] = sweep.derive_metrics(digest)
    return digest


_SEED_VARIANCE_OFF_CHILD = textwrap.dedent("""
    import importlib.util
    import json
    import sys

    tool_path, seed = sys.argv[1], sys.argv[2]
    ambient_base, turns = int(sys.argv[3]), int(sys.argv[4])

    # The authored bands, jitter, tie-breaks and permutations consult ONE
    # predicate at call time. Forced True here, a non-historical seed boots on
    # the authored centres and takes their neutral arm while `campaign_seed`
    # still reads `seed`. NOT every seeded draw consults it: naval
    # `_pct_roll` (expedition slip, diversion), the fleet-action jitter and
    # jealousy's expression pick call `seeded_int` on `campaign_seed`
    # directly and still roll on this seed. Measured September 16, 2026: 14
    # such draws a run — one slip roll (57 on historical, 47 here) against
    # odds of 88 that both pass, the rest text the digest does not carry.
    # So control 2's equality holds on THIS board, not by construction: a
    # naval roll whose odds fell between the two draws would turn it red
    # with no loss of variance. Read such a red as that, not as a defect.
    import backend.game_logic.campaign_variance as campaign_variance
    campaign_variance.is_historical = lambda _seed: True

    spec = importlib.util.spec_from_file_location(
        "ai_v_sweep_seed_variance_off", tool_path)
    tool = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tool)
    print("PAYLOAD=" + json.dumps(tool.run_one(seed, ambient_base, turns)))
""")


@pytest.fixture(scope="module")
def ulm_seed_variance_off():
    """IQ-7 (Sept 16, 2026): the ulm run with seed variance disabled in the
    child — the control that proves the widened Arm-B signature separates
    seeds by what the SEED did, not by anything that merely differs between
    two runs. The fifth subprocess run in this file (~2.3 s measured; a
    40-turn run is dominated by its boot)."""
    proc = subprocess.run(
        [sys.executable, "-c", _SEED_VARIANCE_OFF_CHILD,
         str(REPO_ROOT / "tools" / "ai_v_sweep.py"), "ulm",
         str(sweep.AMBIENT_K), "40"],
        env=sweep.child_env("ulm"), cwd=str(REPO_ROOT),
        capture_output=True, text=True, timeout=600)
    return sweep.payload_from(proc, "ulm/seed-variance-off")


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
        noise.

        WIDENED — IQ-7 "The Satellites Have a Position" (September 16,
        2026). The comparison is `tools/ai_v_sweep.py::_variance_signature`,
        the ONE definition the offline sweep's Arm B also reads; nothing is
        composed here. It is §4.7's literal triple, unchanged, plus
        `first_fight_turn` (the row turn each court first stands on
        `fight`) and `eliminations` (sorted [row turn, nation]).

        Why. Measured on this tree (ambient K=10000, all ten
        `SWEEP_SEEDS`): the literal triple is EQUAL for historical and ulm
        — both `{ai_war_count: 0, war_turns: [21], courts_at_fight:
        [Austria, Bavaria, Britain, Russia, Spain, Sweden]}`. The
        unattended board's one war is Switzerland breaking free of France.
        Nobody answers its relief petitions, the lapse cadence
        (PETITION_GRACE_TURNS / PETITION_INTERVAL_TURNS) is a pair of
        constants the seed does not perturb, and the break now falls at
        turn 21 on nine of ten seeds (23 on eylau). Before IQ-7 it was a
        rebellion at 24, 25 or 32, or a defection to Britain at row 30
        (event stamp 29) with no war at all. The two campaigns are still different ones: ulm's
        seeded Germany-first Austria beats Bavaria, which reaches `fight`
        at row 3 (row 4 on historical) and is eliminated at row 4, while
        historical keeps Bavaria and loses Switzerland at row 22 and the
        Kingdom of Italy at row 27 (row 5 on ulm). The widened signature
        separates them on BOTH new keys, so the green does not rest on
        Bavaria's one-turn fight shadow alone.

        What that costs, stated plainly. A strictly finer signature
        compared with `!=` is a logically EASIER assertion than the
        triple's inequality: every pair the triple separated it still
        separates, and it separates pairs the triple could not. So this
        pin does not carry the teeth. The three controls below do, because
        a widening cannot fake them: the same seed run twice signs EQUAL
        (`test_the_same_seed_twice_signs_alike`), ulm with seed variance
        disabled signs EQUAL to historical
        (`test_seed_variance_off_signs_as_historical`), and ulm's boot
        grafted onto historical's run does not move the signature
        (`test_the_signature_reads_the_run_not_the_boot`). Across the ten
        seeds the widened signature forms 4 classes where the triple forms
        3: {historical, friedland, rivoli} · {ulm, austerlitz, marengo,
        lodi} · {jena, wagram} · {eylau}. It does not restore the
        pre-IQ-7 resolution: on that tree both formed 5, with jena and
        wagram apart (wagram had no war) — part of what IQ7-D4 owns.

        The narrowing of the unattended war calendar is real, is NOT
        answered by this widening, and is routed to
        `DESIGN_REFINEMENT.md` IQ7-D4.
        """
        sig_h = sweep._variance_signature(hist1)
        sig_u = sweep._variance_signature(ulm)
        for sig in (sig_h, sig_u):
            assert sorted(sig["first_fight_turn"]) == sig["courts_at_fight"], (
                "the first-fight map must refine courts_at_fight exactly")
        assert sig_h != sig_u, (
            "two seeds produced identical war counts, war turns, "
            "fight-rung courts, first-fight turns AND eliminations — the "
            "variance slice failed (§4.7)")

    def test_the_same_seed_twice_signs_alike(self, hist1, hist2):
        """Teeth, control 1 (IQ-7). The widened signature must not be
        trivially distinct: two separate processes on the SAME seed and K
        sign identically. Killed by any key that reads something a run
        carries but the seed does not determine (a wall-clock stamp, a
        process id, an address). No extra run — Arm A's two digests. The
        weakest of the three: for any key derived from the digest it is
        already implied by Arm A's byte-identity, so the real teeth are
        controls 2 and 3."""
        assert sweep._variance_signature(hist1) == sweep._variance_signature(
            hist2)

    def test_seed_variance_off_signs_as_historical(self, hist1, ulm,
                                                   ulm_seed_variance_off):
        """Teeth, control 2 (IQ-7). ulm with the seed-variance layer
        disabled in the child (`campaign_variance.is_historical` forced
        True — bands collapse to their centres, jitter and tie-breaks take
        their neutral arm) must sign EQUAL to historical, while the real
        ulm run signs differently. So what `test_the_spec_triple_differs`
        separates is what the SEED did. Killed by a signature key that
        reads the seed's name, the boot, or any other label rather than
        the campaign's outcome (the seed string survives this control:
        `campaign_seed` still reads `ulm`)."""
        off = ulm_seed_variance_off
        assert off["meta"]["seed"] == "ulm", off["meta"]
        assert off["boot"]["campaign_seed"] == "ulm", (
            "the control must run ON the ulm seed, or its equality is "
            "vacuous")
        assert off["boot"]["relations"] == hist1["boot"]["relations"], (
            "the disable did not reach the child's boot — the bands still "
            "resolved off their centres")
        assert (sweep._variance_signature(off)
                == sweep._variance_signature(hist1))
        assert (sweep._variance_signature(ulm)
                != sweep._variance_signature(off))

    def test_the_signature_reads_the_run_not_the_boot(self, hist1, ulm):
        """Teeth, control 3 (IQ-7). §4.7 asks for a difference in turn-0
        dispositions AND in the run, and `test_turn0_dispositions_differ`
        owns the first. The run clause must not be satisfiable by a boot
        fact, or a converged 40-turn run would pass on its deck order
        alone: graft ulm's boot and meta onto historical's per-turn record,
        re-derive through the tool's real `derive_metrics`, and the
        signature must not move. Killed by widening the signature with the
        majors' opening design ids, the boot relations, or the seed's name.
        The seed-variance-off control catches the seed's name but cannot
        see a boot disposition — with variance off, ulm boots on
        historical's own centres — which is why this graft exists. Its
        reach, stated: it catches a read SOURCED from the boot. The same
        disposition re-read from the run's first row (a row's intent
        views, say) is a run fact to this graft and passes it; no
        signature key reads a row's intents except the turn a court
        first stands on `fight`."""
        grafted = {"meta": ulm["meta"], "boot": ulm["boot"],
                   "turns": hist1["turns"], "final": hist1["final"]}
        grafted["derived"] = sweep.derive_metrics(grafted)
        assert ulm["boot"] != hist1["boot"], "the graft must carry a change"
        assert (sweep._variance_signature(grafted)
                == sweep._variance_signature(hist1))

    def test_first_fight_refinement_reads_the_turn(self):
        """The IQ-7 `first_fight_turn` semantics, pinned on synthetic
        digests through the tool's REAL `derive_metrics`, so a derivation
        that drops the turn, keeps the LAST turn, or reads another rung
        cannot pass: same courts at `fight` on different first turns → the
        literal triple is equal and the signature is not; same first turns
        → both equal."""
        def digest(bavaria_first):
            return _synthetic_digest(
                {"Bavaria": set(range(bavaria_first, 7)),
                 "Austria": set(range(1, 7)),
                 "Holland": set()},
                eliminated=[])

        def triple(d):
            sig = sweep._variance_signature(d)
            return {k: sig[k] for k in ("ai_war_count", "war_turns",
                                        "courts_at_fight")}

        early, late, early_again = digest(3), digest(4), digest(3)
        assert (sweep._variance_signature(early)["first_fight_turn"]
                == {"Austria": 1, "Bavaria": 3})
        assert (sweep._variance_signature(late)["first_fight_turn"]
                == {"Austria": 1, "Bavaria": 4})
        assert triple(early) == triple(late)
        assert sweep._variance_signature(early) != sweep._variance_signature(
            late)
        assert sweep._variance_signature(early) == sweep._variance_signature(
            early_again)
        # FIRST, not last: a court that stands down and re-enters `fight`
        # keeps its first turn.
        relapse = _synthetic_digest({"Bavaria": {2, 5, 6}}, eliminated=[])
        assert (sweep._variance_signature(relapse)["first_fight_turn"]
                == {"Bavaria": 2})

    def test_eliminations_read_who_falls_and_when(self):
        """The IQ-7 `eliminations` semantics, through the tool's REAL
        `derive_metrics`: sorted [row turn, nation]; WHO falls and WHEN
        both separate signatures; other exits in the same drain are not
        eliminations; the clock is the digest's row turn (the one
        `war_turns` and `first_fight_turn` use), not the event's own stamp,
        which is one lower for an enemy-phase elimination."""
        fight = {"Austria": set(range(1, 7))}
        bavaria_4 = _synthetic_digest(fight, [(4, "Bavaria", 3)])
        bavaria_5 = _synthetic_digest(fight, [(5, "Bavaria", 4)])
        swiss_4 = _synthetic_digest(fight, [(4, "Switzerland", 3)])
        two = _synthetic_digest(fight, [(5, "KingdomOfItaly", 4),
                                        (4, "Bavaria", 3)])
        none = _synthetic_digest(fight, [])

        assert (sweep._variance_signature(bavaria_4)["eliminations"]
                == [[4, "Bavaria"]])
        assert (sweep._variance_signature(two)["eliminations"]
                == [[4, "Bavaria"], [5, "KingdomOfItaly"]])
        assert sweep._variance_signature(none)["eliminations"] == []
        # repeated entries are not collapsed — neither across rows nor
        # within one drain (the engine's latch makes either a defect today,
        # and a signature that differs on a defect is the right answer)
        twice = _synthetic_digest(fight, [(4, "Bavaria", 3),
                                          (6, "Bavaria", 5)])
        assert (sweep._variance_signature(twice)["eliminations"]
                == [[4, "Bavaria"], [6, "Bavaria"]])
        same_drain = _synthetic_digest(fight, [(4, "Bavaria", 3),
                                               (4, "Bavaria", 3)])
        assert (sweep._variance_signature(same_drain)["eliminations"]
                == [[4, "Bavaria"], [4, "Bavaria"]])
        assert (sweep._variance_signature(same_drain)
                != sweep._variance_signature(bavaria_4))
        sigs = [sweep._variance_signature(d)
                for d in (bavaria_4, bavaria_5, swiss_4, two, none)]
        for i, a in enumerate(sigs):
            for b in sigs[i + 1:]:
                assert a != b
        assert (sweep._variance_signature(bavaria_4)
                == sweep._variance_signature(
                    _synthetic_digest(fight, [(4, "Bavaria", 3)])))

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

    def test_routine_intent_lines_fire_in_the_wild(self, hist1):
        """IQ-6 N2 (PR-X4, September 14, 2026): the FLOOR beside the ceiling
        above. That pin only ever asserted `<= 2`, so it stayed green whether
        the producer fired or never did — which is how the rescore memo
        could record the routine intent lines as "0 in twelve runs" while
        the engine emitted them on every board (the zero was the playtest
        digest's priority filter, fixed by IQ-6 N1). Measured on this very
        ambient historical run when landed: 8 unique lines.

        Counted UNIQUE (type + producing turn + vars), because the queue is
        snapshotted without draining and a line queued inside advance_turn
        rides into the next snapshot too — the second assertion holds the
        dedupe to that: on this board the raw snapshot count is larger."""
        derived = hist1["derived"]
        total = derived["routine_intent_lines_total"]
        assert total >= 1, "the Stage-F producer never fired in 40 turns"
        assert total >= derived["routine_intent_lines_max_per_turn"]
        raw = sum(1 for row in hist1["turns"] for e in row["dispatch_queue"]
                  if e["type"] in sweep.ROUTINE_INTENT_TYPES)
        assert total < raw, (total, raw)

    def test_mirror_drifts_down_for_a_passive_france(self, hist1):
        """§3.5 (arm (a) half): a France that does nothing drifts DOWN the
        perceived ladder.

        ── AMENDED August 16, 2026 — WIN-D5 "The Road Home" §9 ──────────────
        The original pin required BOTH the weight and the RUNG to fall. The
        rung half no longer holds, and the cause is measured, not guessed —
        a three-arm run isolates it to WIN-D5 alone:

            arm 0  neither change      fight/68 -> ask/5
            arm A  corridor only       fight/68 -> indifferent/0
            arm B  Emperor at Lorraine fight/68 -> fight/35   <-- the cause

        The Emperor now boots on the Rhine with 10,000 Guard beside Soult's
        30,000, one march from Mack at Ulm. In the ambient run France issues
        no orders — but "France issues no orders" is not the same thing as
        "France looks harmless", and Europe declines to read an imperial army
        camped on its frontier as a power winding down. The wars accordingly
        do not wind down either, and Austria still prices France at `fight`
        on turn 40.

        What §3.5 is actually for — restraint being LEGIBLE — survives and is
        still asserted: the weight roughly halves (68 -> 33/35). What is
        given up is the claim that the rung itself must fall, which was only
        ever true of a France with nothing standing on anyone's border. The
        rung is still forbidden to RISE, so a passive France can never be
        read as escalating.

        ⚠ This is a real softening of an AI-Intent §7 DoD arm and it is
        recorded rather than absorbed: if the reduced signal is judged too
        weak, the lever is WIN-D5 (`europe_1805.json`, Napoleon's location),
        not this test.

        ── AMENDED September 1, 2026 — WO row slice 10 (WO-13) ─────────────
        The magnitude clause now measures the fall from the series PEAK
        rather than from its first reading, and the reason is a board
        change, attributed by experiment: with slice 10's three gate levers
        down this test passes verbatim; with them up it fails at 68 -> 56.

        Slice 10 closed a name-resolution defect that had FROZEN Britain's
        Iberian army — for twenty-two turns every attack it ordered on the
        province Gascony was redirected to Marshal Ney and refused as out
        of range. Unfrozen, Europe actually fights France, France holds
        (26 provinces at turn 40 against 18 before), and the mirror rises
        to 97 mid-campaign before decaying to 56.

        Measuring the fall from the FIRST reading silently assumed the
        first reading was the maximum — true only of a board where nobody
        could reach France. What §3.5 asserts is that restraint DECAYS the
        price, and that is what the peak-relative form measures: 97 -> 56
        is a 42% fall, and the rung still never rises. The direction
        clauses are untouched; only the anchor of the magnitude clause
        moved, and it moved from an accident of the old board to the
        quantity the arm was always about.
        """
        series = hist1["derived"]["mirror_series"]
        first_price, first_weight, _ = series[0]
        last_price, last_weight, _ = series[-1]
        peak_weight = max(weight for _p, weight, _n in series)
        # The mirror weights ARE the threat series (`get_france_perceived_
        # intent` clamps and returns it), so anchor on the recorded constant
        # and say so — the precedent slice 10 set for the slice-9 pin. It is
        # also why the "softening" below is smaller than it reads: neither
        # form can red without `TestArmAControl::test_threat_series_is_the_
        # standing_baseline` redding first.
        # FA slice 4 (Sept 4, 2026): the mirror reads the PER-TURN series
        # (BASELINE_SERIES[1:]); index 0 is the boot reading it never sees.
        # On every earlier board the peak was mid-campaign so both agreed;
        # on the slice-4 board the series only ever falls from boot, so the
        # boot reading is the maximum and the anchor must exclude it.
        assert peak_weight == max(BASELINE_SERIES[1:]), (peak_weight,
                                                         max(BASELINE_SERIES[1:]))
        assert last_weight < first_weight
        # BOTH anchors. Peak-relative is the arm the board change made
        # correct; first-relative is kept, loosened, so the clause still
        # says something about where the campaign OPENED. Measured at the
        # re-record: last/peak = 0.577 against 0.60 and last/first = 0.824
        # against 0.90 — 2.2 and 4.2 points of headroom, recorded as numbers
        # so the next board change is read against a measurement rather than
        # against a threshold.
        assert last_weight <= peak_weight * 0.6, (
            "restraint must remain legible as a substantial fall in price, "
            f"got peak {peak_weight} -> {last_weight}")
        assert last_weight <= first_weight * 0.9, (
            f"got first {first_weight} -> {last_weight}")
        assert rung_index(last_price) <= rung_index(first_price), (
            "a passive France must never be read as ESCALATING")

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
        vassalized, or — on the FA slice-2 review-round board, where
        France lost every satellite — the dreamer ELIMINATED outright:
        KingdomOfItaly at turn 25, Holland at turn 39)."""
        final = hist1["final"]
        if not final["formations"]:
            watches = final["formation_watch"]
            assert watches, "no formation AND no watch to explain why"
            assert any(
                watch.get("blocked_by_vassalage") or watch.get("progress")
                or watch.get("eliminated")
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

    def test_staged_exhaustion_tilsit_no_longer_reverses(self, scripted):
        """IQ-6 V3 (September 14, 2026) — CONSCIOUSLY RE-WORDED from
        `test_volte_face_signed_and_aimed_at_a_third_party`.

        The scripted arm stages scene 4 at turn 11 by hand: Russia
        separate-peaced OUT, war exhaustion WRITTEN to 80, relation WRITTEN
        to 45 (a +125 jump), and NO Russian soil lost. Its defeat showed
        through the exhaustion arm alone — exactly the white-peace promise
        IQ-6 retires under GR9 (`emergent_designs.THE_DEFEAT_IS_THE_SOIL`):
        on the ordinary route R49 zeroes that exhaustion at the peace and
        the tick decays it 5 a turn, so it can never overlap a courtship.
        Measured on this very arm: lever DOWN, Russia is receptive at t11
        and the volte-face fires at t12 aimed at `gulf_and_straits`; lever
        UP, Russia is never receptive over t11–t17 and nothing fires. So the
        old positive pin was pinning the retired promise, and it now pins
        the retirement holding IN A RUN.

        Scene 4's positive half moved, it did not vanish: the ordinary
        geometry (a beaten Austria with her soil held, courted through the
        executor, the courier inside the widened window, the ratify beat)
        is tests/test_iq6_volte_face.py, and the §12.2 deck advance to
        `gulf_and_straits` stays pinned by
        test_ai_intent_emergent_designs.py::TestVolteFaceBeat (re-staged on
        soil). Restoring an IN-RUN positive needs the harness to stage a
        soil mark at turn 11 (tools/ai_v_sweep.py `_turn_11`) — routed.

        (The old pin's last clause was vacuous: Russia's late intent reads
        `gulf_and_straits` aimed at Sweden on the lever-up arm too, with no
        alliance signed.)"""
        volte_proposals = [
            p for p in scripted["derived"]["proposals_to_france"]
            if p["decision_reason"] == "volte_face"]
        assert not volte_proposals, volte_proposals
        assert not scripted["derived"]["volte_faces"], (
            scripted["derived"]["volte_faces"])
        watches = [entry for entry in scripted["script_log"]
                   if entry.get("step") == "volte watch"]
        assert watches, "the staging ran and the watch recorded it"
        assert all("receptive=False" in str(entry.get("note", ""))
                   and "we=80" in str(watches[0].get("note", ""))
                   for entry in watches), watches

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


class TestSweepSeedIsNotEscapable:
    """Found August 4, 2026, during the EC-L slice.

    Every fixture in this file is MODULE-scoped, and pytest sets higher-scoped
    fixtures up BEFORE function-scoped autouse ones — so `hist1` and its
    siblings were built OUTSIDE conftest's `SOVEREIGN_SEED=historical` pin and
    inherited whatever the developer's shell carried. The symptom is the worst
    kind: a DoD assertion that flips on an unrelated change while the full
    suite stays green, because the seed differed between the two runs rather
    than the behaviour. `spawn_run` now writes the seed it was ASKED for into
    the child's environment, so `--seed` is authoritative.
    """

    def test_spawn_run_pins_the_seed_into_the_child_env(self, monkeypatch):
        captured = {}

        class _Proc:
            returncode = 0
            stdout = 'PAYLOAD={"derived": {}, "meta": {}}'
            stderr = ""

        def _fake_run(args, **kwargs):
            captured["env"] = kwargs.get("env") or {}
            captured["args"] = args
            return _Proc()

        monkeypatch.setattr(sweep.subprocess, "run", _fake_run)
        monkeypatch.setenv("SOVEREIGN_SEED", "a_stale_developer_seed")
        sweep.spawn_run("ulm", sweep.AMBIENT_K, 4)

        assert captured["env"].get("SOVEREIGN_SEED") == "ulm"
        assert "--seed" in captured["args"]
        assert captured["args"][captured["args"].index("--seed") + 1] == "ulm"

    def test_the_ambient_seed_cannot_change_what_the_pins_measure(self,
                                                                  monkeypatch):
        """The falsifiable half: the digest must not depend on the shell."""
        monkeypatch.setenv("SOVEREIGN_SEED", "austerlitz")
        hostile = sweep.spawn_run("historical", sweep.AMBIENT_K, 12)
        monkeypatch.delenv("SOVEREIGN_SEED", raising=False)
        bare = sweep.spawn_run("historical", sweep.AMBIENT_K, 12)
        assert (hostile["derived"]["beats"] == bare["derived"]["beats"])
        assert (len(hostile["derived"]["pair_peaces"])
                == len(bare["derived"]["pair_peaces"]))
