"""Row IC, Session 4 — "the voice, and the other side of the hill" (November 22,
2026): the session's ONE measure, with arms, after `tools/_oc_measure.py` (its
idiom, read on this session's ladder — `tests/_ic4_seams.py`).

THE RULES, WRITTEN BEFORE ANY DATA (the plan approved in Plan Mode, November 22,
2026; `docs/INDEPENDENT_COMMAND_SPEC.md` §13; made exact here before the first
run):

  R-INERT   Arm 0 — every seam of the session down — is the commit before
            (`b69d0a5e`): the standing forty-turn record byte for byte
            (`tools/_ic4_series_arms.py`), the France band 26 / 27 / 28 on the
            three commanded seeds, and the ambient ten seeds' signature and
            census equal to row OC's ALL records. A difference STOPS the chain.
  R-HILL    Arm ALL — the tree as shipped (the plans up, their favoured
            province up, what a court learns up; the mood and the hunt down):
            (1) the band on the three commanded seeds inside 23–28;
            (2) no ambient seed loses a story class against arm 0 (the count
                of distinct classes is not lower);
            (3) the deploy gate's clauses still met on the ten ambient seeds
                (story classes >= 6, a minor promoted on >= 1 seed, the roster
                in >= 2 readings, no annexation outside aim);
            (4) a letter-following enemy marshal acts no less often than today:
                acts per man-turn — an ACT is a successful attack, a march (his
                province changed), a dig-in, leaving his works, a fall-back or a
                retreat, by his court's logic or by his written orders — read on
                the ten ambient seeds x 20 turns with each written plan FORCED
                in turn (`war_plans.the_plan_forced`); the unweighted MEAN of
                the per-plan rates of a set is not below arm 0's rate. Reported
                per plan and per man (the historical plan keeps Mack still on
                purpose — said, not hidden);
            (5) no hit is lost: a line that came true for a planned man either
                moved him or was used that night (a true line that did nothing
                and stays unused is a stall — zero).
            Reported besides: each written line that fired, by plan, step and
            man; a written line that fired on no seed is named.
  FALLBACK  If R-HILL is missed: the failing plan's content is changed — its
            favoured province first, then a line — at most two rounds, the rule
            never loosened. Still missed: arm NOFAVOUR (the favoured province's
            seam down) is read and, if it meets the rule, the plans ship with
            exact orders only and the report says so. Still missed: the plans'
            seam ships down, IC-14 is reported "built, not adopted", the row is
            NOT called complete, and it is put to the user.
  MOOD      Arm +MOOD (each man's own mood up, the tree otherwise as shipped):
            the band, the story classes and the AI-France harness REPORTED per
            seed. Ships down whatever it reads.
  R-HUNT    Arm +HUNT: the enemy's attacks on LONE French corps (a French corps
            with no French corps in its province or the ones next to it) on the
            ambient sweep, the band, the story classes — the table REPORTED
            either way. The hunt is adopted only if the attacks rise, the band
            holds and no seed loses a story class — and then only on the user's
            word. Ships down whatever it reads.

THE ARMS (`held` — what each passes to the children through the driver's
`--seam` flags or `INK_IRON_SEAMS`):

    0            every seam of `tests/_ic4_seams.py` down
    ALL          nothing held: the tree as shipped (since the outcome below:
                 the plans DOWN — it must read as arm 0 reads)
    +PLAN        the plans up, as built (what "ALL" was in the first two runs)
    +PLAN+FIGHT  … and a planned man still strikes at good odds (row FIGHT)
    NOFAVOUR     the plans up, the favoured province's seam down
    +MOOD        each man's own mood forced up
    +HUNT        the hunt forced up
    P:<id>       the plans up, that written plan forced for its holder
    PF:<id>      the same with row FIGHT up

THE OUTCOME (November 22, 2026 — written after the data, by the FALLBACK above):
R-HILL (4) was missed in the first run and after BOTH rounds of content
(round 1: the favoured province narrowed to a priority among a court's own
aims, the plans re-timed as an opening book, `support` and `chase` orders;
round 2: no order that leaves a man standing, shorter steps). So the plans'
seam SHIPS DOWN, IC-14 is "built, not adopted", row IC is NOT called complete,
and the choice is put to the user with the tables. Row FIGHT is one further arm
built for that choice and reported (it lifts the act rate and still misses the
rule, and it takes the band to 22 on CMD-A); it ships down too. Read besides,
and never used to judge the rule: the count as the approved plan words it ("a
first dig-in", leaving the works no act) — added after the first data was seen;
by it the plans stand nearer today (0.33-0.35 against 0.36) and still below.
THE GATE'S CLAUSE 2, a correction to (3) above: "a minor promoted on >= 1 seed"
is read on THIRTY seeds by the user's ruling of November 18
(`tools/_oc_gate_2026_11_18.json`), not on the ten this tool reads; on the ten
the tree before the session holds no promotion either, so `met` False on an arm
of `_ic4_gate_*.json` is not a loss. The shipped tree equals row OC's ALL on
signature and census, so the gate stands as row OC read it. To ADOPT the plans
the twenty wide seeds must be read with them up.

SESSION 4b (November 23, 2026) — THE USER'S "On, after 20 seeds" READ. The
twenty wide seeds (`--surfaces promotions`, `_oc_measure.WIDE_SEEDS`) were read
with the plans up (arm `+PLAN`, the tree as built) on the final tree of Parts 1
and 2, from a frozen copy, with the band, the ambient ten, the gate on thirty
and the enemy's acts: arm 0 still reproduces the standing records (band 26/27/
28; ambient signature and census EQUAL to row OC's ALL; the forty-turn series
byte for byte). With the plans up the band holds (28/25/28), story classes 10,
the roster in 3 readings, no annexation outside aim — and NO MINOR IS RAISED ON
ANY OF THE THIRTY SEEDS (arm 0: aspern and borodino). The deploy gate's clause 2
breaks, so by the reading recorded with the ruling the plans STAY DOWN and the
choice goes back to the user (`tools/_ic4_gate_2026_11_23.json`,
`tools/_ic4_promotions_wide_2026_11_23.json`). R-INERT reads arm 0 alone from
this session on (the shipped tree may adopt the plans).

SESSION 4b, CONTINUED (November 23, 2026) — THE USER'S "fix warplans". Traced
on the two seeds that raise a minor with the plans down (aspern: Bavaria at 21;
borodino: Denmark at 30), from a frozen copy, the plans down and up: on aspern
every court at war drew a plan — France's ally Bavaria too, in its own war with
Austria — and the general set ("guard the capital") ordered Bavaria's one
corps, Deroy, who follows orders to the letter, to hold where he stood
(Franconia, then Munich) from turn 2 until its steps ran out at 10; the peace
came at 14 with the Tyrol that crowns her untaken (with the same coalition
plan and no plan of her own he takes it at 13; with no plans at all, at 12).
On borodino no plan of her own touches Denmark (no man of hers follows orders
to the letter), but the coalition's plan does at one remove: its opening moves
Russia's money to Sweden a turn sooner (6, not 7), Sweden raises 13,000 men at
8, and Denmark's war council reads her outmatched and never declares — a
plan's effect on which minor rises, not a fault in a plan's code. THE FIX
(`war_plans._muster`): a plan is drawn only by a court at war with France.

THE RULES FOR THE FIX, WRITTEN BEFORE ITS DATA (the deploy gate as the user
ruled it, nothing new; stamp `2026_11_23_fix`):
  R-ADOPT   Arm ALL — the plans up as fixed (first read as ALL from a frozen
            copy that carried the seam up; the records of the stamp are
            re-taken as arm +PLAN, the seam held up, so they reproduce from the
            tree whatever it ships): (1) the band on the three commanded seeds inside 23-28;
            (2) story classes >= 6 on the ten ambient seeds; (3) a minor raised
            on >= 1 of the THIRTY seeds (the ten and the twenty wide); (4) the
            roster in >= 2 readings; (5) no annexation outside aim. All five
            met: the plans ship up and BASELINE_SERIES is re-pinned from the
            series' ALL arm (the old pin kept by name). One missed: the seam
            goes back down and the question returns to the user with the
            per-seed table — no rounds of content, no second fix measured
            against the same seeds.
  R-INERT   Arm 0 reproduces the standing records (the band 26/27/28; the
            ambient signature and census equal to row OC's ALL; the forty-turn
            series byte for byte against HEAD's BASELINE_SERIES).
  REPORTED  R-HILL (2) (story classes per seed against arm 0) and R-HILL (4)
            (acts per man-turn, each written plan forced) — information: the
            user adopted the plans as built without R-HILL (4) (D41).

THE OUTCOME OF THE FIX (November 23, 2026 — written after its data; first read
as arm ALL on a frozen copy that carried the seam UP, re-taken as arm +PLAN
from a frozen copy of the tree as it ships — the same numbers; every
`_2026_11_23_fix` record names the arm +PLAN): R-INERT MET (the band 26/27/28; the ambient signature and
census EQUAL to row OC's ALL; the series byte for byte). R-ADOPT: (1) the band
28/25/26 — met; (2) story classes 9 — met; (3) a minor raised on the thirty —
MISSED, zero (the ten: none; the twenty: none — Bavaria takes the Tyrol on
aspern again at 13 and lacks the crown's 3,000 gold before Austria retakes it);
(4) the roster in 2 readings — met; (5) no annexation outside aim — met. So the
seam went back DOWN and the question is the user's (D41). Measured besides, by
a rule written before its data (`tools/_ic4b_wide_promotions.py`): on 200 fresh
seeds a minor rises on 9 with the plans down (Denmark 5, Bavaria 3, Hesse 1) and
8 with them up (Bavaria 5, Hesse 3) — "no suppression shown" on the count the
gate reads: the thirty's zero is the sample's. Per court it is not even: the
plans close DENMARK's road (5 to 0, a one-sided chance near 3 in 100) — traced
on borodino and three fresh seeds, the coalition's opening moves Russia's money
to Sweden a turn sooner, Sweden arms at turn 8, and Denmark's war council reads
her outmatched and stays out, as Denmark stayed out in 1805 — while Bavaria and
Hesse rise more often. A plan's effect on WHICH minor rises; reported to the
user with the gate. R-HILL (4), reported: the acts a man-turn of the enemy's
letter-following men, each written plan forced — each set's mean 0.40-0.42
against today's 0.48 as this tool first counted (missed), 0.37-0.38 against
0.35 as the approved plan words an act (met); single plans 0.39-0.42 and
0.36-0.38; Session 4's round 2 read coalition 0.36 and default 0.34 (as
worded 0.33 and 0.32). (The
hill child does not seed `random` per turn as the ambient runner does, so its
rates move by about half a point run to run — arm 0 read 0.478 and 0.484 on
two runs of the same plans-down code.)
The review of the fix (three lanes, two refuters per finding) upheld two more
rows, fixed before the final measure: a court rejoining a standing holder takes
the step afresh (IC4b-29), and the spy promises written orders only of a court
at war with you (IC4b-30). Every record of the stamp is from the final code.
THE USER'S WORD, shown these numbers: "Switch them on" — the seam ships UP,
BASELINE_SERIES re-pinned from `_ic4b_fix_series_arms_2026_11_23.json`'s
"+PLAN" arm (the old pin kept as SERIES_BEFORE_IC4B), IC4-D1 closed.

THE SURFACES, each a chain run ALONE (run this tool from a FROZEN COPY of the
tree and copy its records back): band, ambient, promotions, gate, hill, chain_d.

    .venv/Scripts/python.exe tools/_ic4_measure.py --surfaces band --arms 0,ALL
    .venv/Scripts/python.exe tools/_ic4_measure.py --surfaces hill
"""
from __future__ import annotations

import argparse
import collections
import contextlib
import io
import json
import os
import pathlib
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tests._ic4_seams import IC4_SEAMS_BY_ROW  # noqa: E402

STAMP = "2026_11_22"
BAND = (23, 28)
BAND_ARMS = ("CMD-H", "CMD-A", "CMD-M")
ARM0_BAND = {"CMD-H": 26, "CMD-A": 27, "CMD-M": 28}       # the standing reading (row OC's ALL)
OC_SIGNATURE = TOOLS / "_dy_signature_oc_all_2026_11_18.json"
OC_CENSUS = TOOLS / "_oc_all_census_2026_11_18.json"
SCENARIO = ROOT / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
HILL_TURNS = 20
ACTS = ("attack", "move", "fortify", "unfortify", "retreat")
PLAN_UP = "backend.game_logic.war_plans:the_courts_follow_a_plan=True"
FIGHT_UP = "backend.game_logic.war_plans:a_planned_man_still_strikes_at_good_odds=True"
MOOD_UP = "backend.ai.enemy_ai:each_man_has_his_own_mood=True"
HUNT_UP = "backend.ai.enemy_ai:the_enemy_hunts_a_lone_corps=True"
FORCED = "backend.game_logic.war_plans:the_plan_forced="


def plan_sets() -> list:
    block = json.loads(SCENARIO.read_text(encoding="utf-8")).get("war_plans") or {}
    return [(next(iter((s.get("for") or {}).items())), [str(p["id"]) for p in s.get("plans") or []])
            for s in block.get("sets") or []]


def held(arm: str) -> list:
    """The seam specs an arm passes down (the driver's `--seam`, `INK_IRON_SEAMS`)."""
    down = lambda rows: [spec for row in rows for spec in IC4_SEAMS_BY_ROW[row]]  # noqa: E731
    if arm == "0":
        return down(list(IC4_SEAMS_BY_ROW))
    if arm == "ALL":
        return []                      # the tree as shipped (the plans UP since November 23, 2026)
    if arm == "+PLAN":
        return [PLAN_UP]               # the plans as built
    if arm == "+PLAN+FIGHT":
        return [PLAN_UP, FIGHT_UP]     # … and a planned man still strikes at good odds
    if arm == "NOFAVOUR":
        return [PLAN_UP] + down(["FAVOUR"])
    if arm == "+MOOD":
        return [MOOD_UP]
    if arm == "+HUNT":
        return [HUNT_UP]
    if arm.startswith("P:"):
        return [PLAN_UP, f"{FORCED}{arm[2:]!r}"]
    if arm.startswith("PF:"):
        return [PLAN_UP, FIGHT_UP, f"{FORCED}{arm[3:]!r}"]
    raise SystemExit(f"[ic4] unknown arm {arm!r}")


def _label(arm: str) -> str:
    return "ic4_" + arm.lower().replace("+", "plus_").replace(":", "_")


def _write(path: pathlib.Path, record: dict) -> None:
    path.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"[ic4] written {path}", flush=True)


# ── the commanded band ───────────────────────────────────────────────────────

def band(arms, stamp: str, jobs: int) -> dict:
    from tools import _ba4_measure as B4
    from tools import score_run as SR

    run_dir = TOOLS / "playtest_runs" / "ic4_band"
    record = {"_note": ("Row IC, Session 4 — the France band on the commanded arms (the deploy "
                        "gate's difficulty guard, 23-28): score_run's CMD-H / CMD-A / CMD-M per "
                        "arm, France's provinces on the last ledger row. Arm 0 must read 26 / 27 "
                        "/ 28, the standing reading. Written by tools/_ic4_measure.py --surfaces "
                        "band (a chain run ALONE)."),
              "band": list(BAND), "arms": {}}
    tasks = []
    for arm in arms:
        where = run_dir / _label(arm)
        where.mkdir(parents=True, exist_ok=True)
        record["arms"][arm] = {"seams": held(arm)}
        for name in BAND_ARMS:
            tasks.append((arm, name, where, list(SR.ARMS[name]["argv"]) + B4._flags(held(arm))))
    for arm, name, reading in B4._driven(tasks, jobs, "band"):
        record["arms"][arm][name] = reading
    _write(TOOLS / f"_ic4_band_{stamp}.json", record)
    breach = []
    for arm in arms:
        cells = {n: record["arms"][arm][n]["provinces"] for n in BAND_ARMS}
        print(f"[ic4] band {arm:<26} {cells}", flush=True)
        if any(v is None or not (BAND[0] <= v <= BAND[1]) for v in cells.values()):
            breach.append(arm)
    # R-INERT: arm 0 (every seam down) reads the standing band. (Session 4b:
    # the plans may now be adopted, so the tree as shipped is no longer held
    # to arm 0 — it is read against the band's 23-28 like any arm.)
    for inert in ("0",):
        if inert in record["arms"]:
            got = {n: record["arms"][inert][n]["provinces"] for n in BAND_ARMS}
            if got != ARM0_BAND:
                print(f"[ic4] STOP: arm {inert} does not reproduce the band {ARM0_BAND}: got {got}.",
                      flush=True)
                raise SystemExit(2)
    if breach:
        print(f"[ic4] GUARD: the band leaves 23-28 on arm(s) {breach}.", flush=True)
    return record


# ── the ambient ten, the gate, the AI-France harness ─────────────────────────

def _strip(d: dict) -> dict:
    return {k: v for k, v in d.items() if not k.startswith("_")}


def ambient(arms, stamp: str, turns: int) -> None:
    from tools import _ba4_measure as B4

    for arm in arms:
        label = _label(arm)
        sig = TOOLS / f"_dy_signature_{label}_{stamp}.json"
        cen = TOOLS / f"_{label}_census_{stamp}.json"
        rc = B4._run([TOOLS / "_t3_4_measure.py", "--turns", turns, "--label", label.replace("_", "-"),
                      "--out", sig, "--census", cen], seams=";".join(held(arm)))
        if rc != 0:
            raise SystemExit(f"[ic4] ambient {arm} failed (rc {rc})")
        if arm == "0":                # R-INERT: every seam down (Session 4b: arm 0 alone)
            same = (_strip(json.loads(OC_SIGNATURE.read_text(encoding="utf-8")))
                    == _strip(json.loads(sig.read_text(encoding="utf-8"))),
                    _strip(json.loads(OC_CENSUS.read_text(encoding="utf-8")))
                    == _strip(json.loads(cen.read_text(encoding="utf-8"))))
            print(f"[ic4] ambient arm {arm} against row OC's ALL: signature "
                  f"{'EQUAL' if same[0] else 'DIFFERENT'}, census {'EQUAL' if same[1] else 'DIFFERENT'}",
                  flush=True)
            if not all(same):
                raise SystemExit(f"[ic4] STOP: ambient arm {arm} does not reproduce the commit before")


def gate(arms, stamp: str) -> dict:
    out = {}
    for arm in arms:
        label = _label(arm)
        sig_file = TOOLS / f"_dy_signature_{label}_{stamp}.json"
        cen_file = TOOLS / f"_{label}_census_{stamp}.json"
        if not (sig_file.exists() and cen_file.exists()):
            continue
        sig = json.loads(sig_file.read_text(encoding="utf-8"))
        cen = json.loads(cen_file.read_text(encoding="utf-8"))
        promoted = {s: v["signature"]["rank_promotions"] for s, v in sig["seeds"].items()
                    if v["signature"]["rank_promotions"]}
        rosters = {s: tuple(n for _, n in v["signature"]["eliminations"])
                   for s, v in sig["seeds"].items()}
        classes = {s: v.get("story_class") for s, v in sig["seeds"].items()}
        cell = {
            "story_classes": int(sig["story_class_count"]),
            "classes": classes,
            "promotions": promoted,
            "roster_readings": len(set(rosters.values())),
            "rosters": {s: list(r) for s, r in rosters.items()},
            "annexations_outside_aim": int(cen["totals"]["annexations_outside_aim"]),
            "captures_outside_aim": int(cen["totals"]["captures_outside_aim"]),
        }
        cell["met"] = (cell["story_classes"] >= 6 and bool(promoted)
                       and cell["roster_readings"] >= 2 and cell["annexations_outside_aim"] == 0)
        out[arm] = cell
        print(f"[ic4] gate {arm}: classes {cell['story_classes']}, promotions {promoted}, roster "
              f"readings {cell['roster_readings']}, annexations {cell['annexations_outside_aim']} "
              f"(captures outside aim {cell['captures_outside_aim']}) -> "
              f"{'MET' if cell['met'] else 'NOT MET'}", flush=True)
    wide_file = TOOLS / f"_ic4_promotions_wide_{stamp}.json"
    wide = json.loads(wide_file.read_text(encoding="utf-8")) if wide_file.exists() else {"arms": {}}
    for arm, cell in out.items():
        # clause 2 on THIRTY seeds — the ten and the twenty wide (the user's
        # ruling of November 18, 2026; row OC's `gate`)
        extra = wide["arms"].get(arm, {}).get("seeds_promoting")
        cell["promotions_on_the_twenty"] = extra
        cell["clause_2_on_thirty"] = bool(cell["promotions"]) or bool(extra)
        cell["met_on_thirty"] = (cell["story_classes"] >= 6 and cell["clause_2_on_thirty"]
                                 and cell["roster_readings"] >= 2
                                 and cell["annexations_outside_aim"] == 0)
        print(f"[ic4] gate {arm}: clause 2 on the twenty {extra} -> "
              f"{'MET' if cell['met_on_thirty'] else 'NOT MET'} on thirty", flush=True)
    if out:
        _write(TOOLS / f"_ic4_gate_{stamp}.json",
               {"_note": ("Row IC, Session 4 — the deploy gate per arm, read off the ambient "
                          "records: story classes >= 6, a minor promoted on >= 1 seed, the roster "
                          "in >= 2 readings, no annexation outside aim on the ten ambient seeds. "
                          "Written by tools/_ic4_measure.py --surfaces gate."), "arms": out})
    return out


def promotions(arms, stamp: str, jobs: int) -> dict:
    """Clause 2's twenty further ambient seeds per arm (row OC's runner and
    reading, `_oc_measure._wide_promotions` over `_oc_measure.WIDE_SEEDS`), so
    the gate reads "a minor raised" on THIRTY seeds (Session 4b: the plans are
    adopted only once these twenty are read with them up — the user's "On,
    after 20 seeds")."""
    from tools import _oc_measure as OC

    record = {"_note": ("Row IC, Session 4b — the deploy gate's clause 2 on the twenty wide seeds "
                        "(forty turns, the ambient runner, per arm): each seed's rank promotions "
                        "[turn, court]. Read with the ten's record by the gate surface. Written "
                        "by tools/_ic4_measure.py --surfaces promotions."),
              "seeds": list(OC.WIDE_SEEDS), "arms": {}}
    for arm in arms:
        seams = ";".join(held(arm))
        with ThreadPoolExecutor(max_workers=max(1, min(jobs, 4))) as pool:
            got = dict(zip(OC.WIDE_SEEDS,
                           pool.map(lambda sd: OC._wide_promotions(sd, seams), OC.WIDE_SEEDS)))
        record["arms"][arm] = {"seams_held": held(arm), "seeds": got,
                               "seeds_promoting": sorted(sd for sd, v in got.items() if v)}
        print(f"[ic4] promotions {arm}: {record['arms'][arm]['seeds_promoting']}", flush=True)
    _write(TOOLS / f"_ic4_promotions_wide_{stamp}.json", record)
    return record


def chain_d(arms, stamp: str, turns: int) -> None:
    from tools import _ba4_measure as B4

    out = TOOLS / f"_ic4_chain_d_{stamp}.json"
    cmd = [TOOLS / "_t3_5_chain_d.py", "--turns", turns, "--arms", ",".join(_label(a) for a in arms),
           "--out", out, "--run-dir", TOOLS / "playtest_runs" / "ic4_chain_d"]
    for arm in arms:
        if held(arm):
            cmd += ["--arm-seams", f"{_label(arm)}={';'.join(held(arm))}"]
    rc = B4._run(cmd)
    if rc != 0:
        raise SystemExit(f"[ic4] chain d failed (rc {rc})")


# ── R-HILL and R-HUNT: the in-process sweep (one child a seed) ───────────────

def _apply(specs) -> None:
    import importlib
    for spec in specs or []:
        target, expr = str(spec).split("=", 1)
        module_name, attr = target.split(":", 1)
        owner = importlib.import_module(module_name)
        *path, name = attr.split(".")
        for step in path:
            owner = getattr(owner, step)
        assert callable(getattr(owner, name)), spec
        setattr(owner, name, eval("lambda *a, **k: " + expr, {}))  # noqa: S307 - the measure's own specs


def hill_child(arm: str, seed: str, turns: int) -> dict:
    """ONE ambient campaign (France only ends the turn), instrumented: every act
    the enemy's logic and the plans' pass make, per marshal; every line that came
    true for a planned man and what came of it; every attack on a French corps
    and whether it stood alone."""
    quiet = lambda: contextlib.redirect_stdout(io.StringIO())  # noqa: E731
    for k in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        os.environ.pop(k, None)
    os.environ["LLM_MODE"] = "mock"
    with quiet():
        import backend.main as M
        from fastapi.testclient import TestClient

        from backend.ai import enemy_ai as EA
        from backend.commands import if_thens as IT
        from backend.commands import parse_preview as PP
        from backend.commands.parser import CommandParser
        from backend.game_logic import war_plans as WP
        from backend.models.world_state import WorldState
        _apply(held(arm))
        world = WorldState.from_scenario(str(SCENARIO), seed=seed)
        M._set_active_world(world)
        M.parser = CommandParser(use_real_llm=False)
        PP.invalidate()

    acts = collections.Counter()           # (marshal, action) successful acts
    acted_turn = set()                     # (turn, marshal)
    worded_turn = set()                    # (turn, marshal) — an act AS THE PLAN WORDS IT
    dug_at = {}                            # marshal -> the province he last dug in at
    fired = collections.Counter()          # (plan, step, marshal, if, then)
    hits = []                              # (turn, marshal, index) -> outcome
    attacks = {"on_french": 0, "on_lone_french": 0}

    def note(result, action, before, by):
        w = M.world
        name = str(action.get("marshal") or "")
        man = w.get_marshal(name)
        if man is None or not result.get("success"):
            return
        kind = str(action.get("action") or "")
        if kind not in ACTS:
            return
        if kind == "move" and str(man.location) == before:
            return
        acts[(name, kind, by)] += 1
        acted_turn.add((int(w.current_turn), name))
        # The approved plan's wording: "a march, an attack, a FIRST dig-in, a
        # fall-back or a capture". A dig-in is a first one when he has not dug
        # in at this province since he came to it; leaving the works is none.
        here = str(man.location or "")
        if kind == "fortify":
            if dug_at.get(name) != here:
                dug_at[name] = here
                worded_turn.add((int(w.current_turn), name))
        elif kind != "unfortify":
            if kind in ("move", "retreat") or here != before:
                dug_at.pop(name, None)
            worded_turn.add((int(w.current_turn), name))

    real_execute = EA.EnemyAI._execute_action

    def execute(self, action, game_state):
        w = game_state.get("world")
        man = w.get_marshal(str(action.get("marshal") or "")) if w else None
        before = str(getattr(man, "location", "") or "")
        if w is not None and action.get("action") == "attack":
            target = w.get_marshal(str(action.get("target") or ""))
            if target is not None and target.nation == w.player_nation:
                attacks["on_french"] += 1
                here = w.get_region(str(target.location or ""))
                ring = [here.name] + list(getattr(here, "adjacent_regions", None) or []) if here else []
                alone = not any(o is not target and o.nation == target.nation
                                and int(getattr(o, "strength", 0) or 0) > 0
                                for name in ring for o in w.get_marshals_in_region(name))
                attacks["on_lone_french"] += int(alone)
        result = real_execute(self, action, game_state)
        note(result, action, before, "court")
        return result

    EA.EnemyAI._execute_action = execute

    real_run = WP._run

    def run(executor, game_state, w, marshal, action, target):
        before = str(marshal.location or "")
        result = real_run(executor, game_state, w, marshal, action, target)
        note(result, {"marshal": marshal.name, "action": action}, before, "plan")
        return result

    WP._run = run

    real_ready, real_fire = IT.ready, WP._fire
    tonight = {}

    def ready(w, marshal, order):
        hit = real_ready(w, marshal, order)
        if hit is not None and WP.planned(w, marshal):
            tonight[marshal.name] = (int(hit["index"]), hit["line"])
        return hit

    def fire(w, executor, game_state, marshal, hit):
        key = WP.holder_of(w, marshal.nation)
        state = WP.holders(w).get(key) or {}
        line = hit["line"]
        rows = real_fire(w, executor, game_state, marshal, hit)
        if line.get("used"):
            fired[(str(state.get("plan")), int(state.get("step", 0) or 0), marshal.name,
                   str(line.get("if")), str(line.get("then")))] += 1
        return rows

    IT.ready = ready
    WP._fire = fire

    literal_turns = collections.Counter()      # marshal -> man-turns alive
    literal_acts = collections.Counter()       # marshal -> man-turns with an act
    literal_worded = collections.Counter()     # … with an act as the plan words it
    planned_turns = collections.Counter()
    plans_drawn = {}
    stalls = 0
    with TestClient(M.app) as client:
        for _t in range(turns):
            w = M.world
            if getattr(w, "game_over", False):
                break
            turn = int(w.current_turn)
            tonight.clear()
            with quiet():
                client.post("/command", json={"command": "end turn"})
            w = M.world
            for key, state in (WP.holders(w) or {}).items():
                plans_drawn.setdefault(key, str(state.get("plan")))
            for man in w.marshals.values():
                if man.nation == w.player_nation or getattr(man, "personality", "") != "literal":
                    continue
                if int(getattr(man, "strength", 0) or 0) <= 0:
                    continue
                literal_turns[man.name] += 1
                literal_acts[man.name] += int((turn, man.name) in acted_turn)
                literal_worded[man.name] += int((turn, man.name) in worded_turn)
                planned_turns[man.name] += int(WP.planned(w, man))
            for name, (_index, line) in tonight.items():
                if (turn, name) not in acted_turn and not line.get("used"):
                    stalls += 1
                hits.append([turn, name, bool((turn, name) in acted_turn), bool(line.get("used"))])
    return {
        "arm": arm, "seed": seed, "turns": turns,
        "plans": plans_drawn,
        "man_turns": dict(literal_turns), "acted_turns": dict(literal_acts),
        "worded_turns": dict(literal_worded),
        "planned_turns": dict(planned_turns),
        "acts": {"|".join(k): v for k, v in sorted(acts.items())},
        "fired": {"|".join(map(str, k)): v for k, v in sorted(fired.items())},
        "hits": len(hits), "stalls": stalls, "attacks": attacks,
    }


def _hill_arm(arm: str, seeds, turns: int, jobs: int) -> list:
    def one(seed):
        env = dict(os.environ)
        env["PYTHONHASHSEED"] = "0"
        env["PYTHONPATH"] = str(ROOT)
        for k in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "PYTHONIOENCODING",
                  "PYTHONDONTWRITEBYTECODE", "INK_IRON_SEAMS", "SOVEREIGN_SEED"):
            env.pop(k, None)
        proc = subprocess.run([sys.executable, str(pathlib.Path(__file__).resolve()),
                               "--hill-child", arm, seed, str(turns)],
                              env=env, cwd=str(ROOT), capture_output=True, timeout=3600)
        text = proc.stdout.decode("utf-8", errors="replace")
        rows = [ln for ln in text.splitlines() if ln.startswith("HILL=")]
        if proc.returncode != 0 or not rows:
            raise SystemExit(f"[ic4] hill {arm} {seed} failed:\n{text[-1500:]}\n"
                             f"{proc.stderr.decode('utf-8', errors='replace')[-2500:]}")
        print(f"[ic4] hill {arm} {seed} done", flush=True)
        return json.loads(rows[-1][len("HILL="):])

    with ThreadPoolExecutor(max_workers=max(1, jobs)) as pool:
        return list(pool.map(one, seeds))


def _rates(rows: list) -> dict:
    turns, acted, planned = collections.Counter(), collections.Counter(), collections.Counter()
    worded, kinds = collections.Counter(), collections.Counter()
    for row in rows:
        turns.update(row["man_turns"])
        acted.update(row["acted_turns"])
        worded.update(row.get("worded_turns") or {})
        planned.update(row["planned_turns"])
        for key, count in (row.get("acts") or {}).items():
            name, kind, by = key.split("|")
            if name in row["man_turns"]:
                kinds[f"{name}|{kind}|{by}"] += count
    per_man = {m: {"man_turns": turns[m], "acted": acted[m], "planned_turns": planned[m],
                   "rate": round(acted[m] / turns[m], 3) if turns[m] else None,
                   "worded": worded[m],
                   "rate_as_worded": round(worded[m] / turns[m], 3) if turns[m] else None}
               for m in sorted(turns)}
    total, done, said = sum(turns.values()), sum(acted.values()), sum(worded.values())
    return {"per_man": per_man, "man_turns": total, "acted": done,
            "rate": round(done / total, 3) if total else None,
            "worded": said, "rate_as_worded": round(said / total, 3) if total else None,
            "kinds": dict(sorted(kinds.items()))}


def hill(stamp: str, jobs: int, seeds=None, turns: int = HILL_TURNS, arms=None) -> dict:
    from tools.ai_v_sweep import SWEEP_SEEDS

    seeds = list(seeds or SWEEP_SEEDS)
    sets = plan_sets()
    forced = [f"P:{plan_id}" for _for, ids in sets for plan_id in ids]
    arms = list(arms or (["0", "+PLAN"] + forced + ["+HUNT"]))
    record = {"_note": ("Row IC, Session 4 — R-HILL (4), (5) and R-HUNT's ambient count: ten "
                        f"ambient seeds x {turns} turns a arm, France only ending the turn. Per "
                        "arm: each letter-following enemy marshal's man-turns alive, the man-turns "
                        "he acted in (a successful attack, a march, a dig-in, leaving his works, a "
                        "fall-back, a retreat — by his court's logic or his written orders) and the "
                        "rate; every line that fired; hits and stalls; the enemy's attacks on "
                        "French corps and on LONE French corps. Arm 0 is today. Written by "
                        "tools/_ic4_measure.py --surfaces hill."),
              "seeds": seeds, "turns": turns, "sets": [[list(f), ids] for f, ids in sets], "arms": {}}
    for arm in arms:
        rows = _hill_arm(arm, seeds, turns, jobs)
        fired = collections.Counter()
        attacks = collections.Counter()
        for row in rows:
            fired.update(row["fired"])
            attacks.update(row["attacks"])
        record["arms"][arm] = {"seams": held(arm), **_rates(rows), "fired": dict(sorted(fired.items())),
                               "hits": sum(r["hits"] for r in rows),
                               "stalls": sum(r["stalls"] for r in rows),
                               "attacks": dict(attacks),
                               "plans_drawn": {r["seed"]: r["plans"] for r in rows}}
        cell = record["arms"][arm]
        print(f"[ic4] hill {arm:<28} rate {cell['rate']} ({cell['acted']}/{cell['man_turns']}) "
              f"as worded {cell['rate_as_worded']} "
              f"stalls {cell['stalls']} attacks {cell['attacks']}", flush=True)
        _write(TOOLS / f"_ic4_hill_{stamp}.json", record)
    verdict = {}
    for reading, field in (("as_first_run", "rate"), ("as_the_plan_words_it", "rate_as_worded")):
        today = (record["arms"].get("0") or {}).get(field)
        cell = verdict[reading] = {}
        for prefix, label in (("P:", ""), ("PF:", " +FIGHT")):
            for (kind, value), ids in sets:
                rates = [record["arms"][f"{prefix}{i}"][field] for i in ids
                         if f"{prefix}{i}" in record["arms"]]
                rates = [r for r in rates if r is not None]
                if rates and today is not None:
                    mean = round(sum(rates) / len(rates), 3)
                    cell[f"{kind}:{value}{label}"] = {"mean_of_plans": mean, "today": today,
                                                      "met": mean >= today}
    record["r_hill_4"] = verdict
    record["r_hill_4_note"] = (
        "TWO READINGS, both kept. `as_first_run` is the count this tool made exact before its "
        "first run (every dig-in and every leaving of the works is an act). "
        "`as_the_plan_words_it` is the plan approved in Plan Mode, word for word: 'a march, an "
        "attack, a first dig-in, a fall-back or a capture' — a dig-in counts once a province, "
        "leaving the works does not. The second reading was added AFTER the first data was "
        "seen; the report says so.")
    record["r_hill_5"] = {arm: cell["stalls"] for arm, cell in record["arms"].items()}
    _write(TOOLS / f"_ic4_hill_{stamp}.json", record)
    print(f"[ic4] R-HILL (4): {verdict}", flush=True)
    return record


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--surfaces", default="band,ambient,gate,hill")
    ap.add_argument("--arms", default="0,ALL")
    ap.add_argument("--stamp", default=STAMP)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--turns", type=int, default=40)
    ap.add_argument("--hill-turns", type=int, default=HILL_TURNS)
    ap.add_argument("--hill-arms", default="")
    ap.add_argument("--hill-child", nargs=3, metavar=("ARM", "SEED", "TURNS"))
    args = ap.parse_args()
    if args.hill_child:
        arm, seed, turns = args.hill_child
        print("HILL=" + json.dumps(hill_child(arm, seed, int(turns))), flush=True)
        return
    arms = [a.strip() for a in args.arms.split(",") if a.strip()]
    for arm in arms:
        held(arm)
    surfaces = [s.strip() for s in args.surfaces.split(",") if s.strip()]
    if "band" in surfaces:
        band(arms, args.stamp, args.jobs)
    if "ambient" in surfaces:
        ambient(arms, args.stamp, args.turns)
    if "promotions" in surfaces:
        promotions(arms, args.stamp, args.jobs)
    if "gate" in surfaces:
        gate(arms, args.stamp)
    if "chain_d" in surfaces:
        chain_d(arms, args.stamp, args.turns)
    if "hill" in surfaces:
        hill(args.stamp, args.jobs, turns=args.hill_turns,
             arms=[a.strip() for a in args.hill_arms.split(",") if a.strip()] or None)


if __name__ == "__main__":
    main()
