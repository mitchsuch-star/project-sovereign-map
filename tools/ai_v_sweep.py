"""AI-V (Stage G) sweep driver — docs/AI_INTENT_SPEC.md §4.7 / §11 Stage G.

The three-arm acceptance sweep + the scripted-France arm, as one committed
runner (the AI-3r probe was session-scratch; the phase's acceptance harness
is not allowed to be):

  Arm A — control.    Same SOVEREIGN_SEED, same ambient constant K, two
                      separate processes -> byte-identical digest. If Arm A
                      is red, nothing else in the sweep means anything.
  Arm B — variance.   Different SOVEREIGN_SEED, same K. Must differ in
                      turn-0 dispositions and in at least one of
                      {AI-initiated war count, the turns wars begin, which
                      courts reach `fight`}. Holding K makes the difference
                      attributable to the seed, not to combat noise.
  Arm C — acceptance. N runs with BOTH the seed and the ambient RNG
                      varying — the distribution production actually
                      produces. Reported as a distribution.
  Arm (b) — scripted France. One run per seed on a fixed subset: each D5
                      instrument exercised once, a compensation reneged,
                      Britain's client contested, the ports closed under
                      the Continental System, and a beaten great power
                      courted into the volte-face. The §3.5 upward-mirror
                      and pin-21 instrument-caused defusal live here.

The ambient idiom is the pin-16a baseline exactly (tests/
test_ai_intent_threat_migration.py): `PYTHONHASHSEED=0`, `LLM_MODE=mock`,
`WorldState.from_scenario(europe_1805.json)`, and per-turn
`random.seed(K + turn)` immediately before `TurnManager.end_turn` — so the
control arm's historical run is directly comparable to BASELINE_SERIES.
Scripted-France steps run BEFORE the per-turn re-seed (the player phase),
so the ambient arms' schedule is byte-identical to the baseline harness.

Capture is read-only: intent views are the same per-turn cached
derivations production reads (no module RNG anywhere in the political
layer, AI-0b), the dispatch queue is read without draining (advance_turn
owns the clear), and the event log is drained by object identity each
turn because the 500-cap EVICTS — the IGR-B trap this file refuses to
re-learn.

Usage:
  # one run (spawned with PYTHONHASHSEED=0 by the orchestrator or suite):
  python tools/ai_v_sweep.py --run --seed historical --ambient-base 10000 \
      --turns 40 [--script france] [--json-out FILE] [--emit]
  # the full sweep (writes per-run JSONs + summary.json under --out):
  python tools/ai_v_sweep.py --all --out <dir> [--turns 40] [--acceptance-n 10]

Offline/dev tool + suite runner; no game import happens until --run.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCENARIO_PATH = (REPO_ROOT / "godot-client" / "project-sovereign"
                 / "assets" / "maps" / "europe_1805.json")

AMBIENT_K = 10_000        # the M7 per-turn re-seed base (the baseline idiom)
AMBIENT_PRIME = 7_919     # arm C: per-run ambient offset (varied K)
DEFAULT_TURNS = 40

# Arm B/C seed pool — the AI-3r probe's eight + two more battle names.
SWEEP_SEEDS = [
    "historical", "ulm", "austerlitz", "jena", "marengo",
    "eylau", "friedland", "wagram", "lodi", "rivoli",
]
ARM_B_SEEDS = ["historical", "ulm", "austerlitz", "jena"]
SCRIPTED_SEEDS = ["historical", "ulm", "austerlitz"]

# §4.6a beats + the Stage E pair (intent.NARRATION_EXEMPT_EVENT_TYPES is
# the production copy; the sweep keeps its own list so a production edit
# shows up as a sweep diff, not a silent re-scope).
BEAT_TYPES = (
    "crisis_brewing", "coercive_demand", "broken_bargain", "volte_face",
    "third_party_peace", "crisis_passed", "design_promoted",
    "guarantee_called", "agenda_shift",
)
ROUTINE_INTENT_TYPES = ("intent_hardens", "intent_eases")


# ═══════════════════════════════════════════════════════════════════════
# Single-run capture
# ═══════════════════════════════════════════════════════════════════════

def _die(message: str) -> None:
    print(f"AI_V_SWEEP_ERROR: {message}", file=sys.stderr)
    raise SystemExit(2)


def _jsonify(obj):
    return json.loads(json.dumps(obj, default=str))


def _project(obj, depth: int = 3):
    """Compact JSON-safe projection of arbitrary result payloads."""
    if depth <= 0:
        return str(obj)
    if isinstance(obj, dict):
        return {str(k): _project(v, depth - 1) for k, v in obj.items()
                if not str(k).startswith("new_state")}
    if isinstance(obj, (list, tuple)):
        return [_project(v, depth - 1) for v in list(obj)[:200]]
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    return str(obj)


def _mentions_any(obj, needles) -> bool:
    if isinstance(obj, dict):
        return any(_mentions_any(v, needles) for v in obj.values())
    if isinstance(obj, (list, tuple)):
        return any(_mentions_any(v, needles) for v in obj)
    if isinstance(obj, str):
        low = obj.lower()
        return any(n in low for n in needles)
    return False


class RunCapture:
    """Per-turn read-only observation of one ambient/scripted run."""

    def __init__(self, world):
        self.world = world
        self.player = getattr(world, "player_nation", "France")
        marshals = [m.name for m in world.marshals.values()
                    if getattr(m, "nation", None) == self.player]
        self.france_needles = tuple(
            [self.player.lower(), "french"] + [n.lower() for n in marshals])
        # REV-X1 (Aug 30, 2026) — `{id: the object itself}`, not `{id}`.
        #
        # `id()` is unique only among LIVE objects. This harness drained the
        # event log by address precisely BECAUSE the 500-cap evicts... and
        # that is exactly what makes the address unsound: an evicted event is
        # freed, CPython recycles its address, and the next event dict
        # allocated there reports an id this set already holds. The genuinely
        # new event is then silently dropped from the digest.
        #
        # Measured: `TestArmAControl::test_two_processes_byte_identical` — the
        # arm whose own docstring says "if this is red, nothing else means
        # anything" — failed reproducibly whenever the first of the two child
        # processes was also COMPILING the backend, because compiling changes
        # the heap layout and therefore which addresses get recycled. The GAME
        # is deterministic: a clean 40-turn driver snapshotting gold,
        # relations, marshals, controllers, manpower, refusals, cooldowns and
        # war intents is byte-identical cold vs warm. Only the harness's
        # REPORT of the game varied — the worse of the two bugs to have in an
        # instrument, and the one that would have been blamed on the game.
        #
        # Holding the object keeps its address reserved, so an id in this map
        # can never be re-issued to a different event. Bounded by the number
        # of events a run produces, which the digest already retains anyway.
        self._seen_events = {id(e): e for e in world.event_log}
        self._war_ids = set((getattr(world, "war_instances", None) or {}))
        self._ended_ids = {
            wid for wid, inst in
            (getattr(world, "war_instances", None) or {}).items()
            if inst.get("ended_turn") is not None}
        self._proposal_keys = set()

    # -- boot ----------------------------------------------------------
    def capture_boot(self) -> dict:
        world = self.world
        active = [n for n in world.get_active_nations() if n != self.player]
        decks = {}
        for nation, deck in (getattr(world, "agendas", {}) or {}).items():
            decks[nation] = [
                (e.get("id") if isinstance(e, dict) else str(e))
                for e in (deck or [])]
        return _jsonify({
            "campaign_seed": getattr(world, "campaign_seed", ""),
            "threat": int(world.threat_level),
            "relations": {str(k): int(v) for k, v in
                          (world.nation_relations or {}).items()},
            "gold": {n: int(world.nation_gold.get(n, 0))
                     for n in [self.player] + active},
            "decks": decks,
            "intents": self._intent_snapshot(active),
            "wars": self._war_summaries(),
            "exhaustion": dict(getattr(world, "war_exhaustion", {}) or {}),
        })

    # -- per-turn ------------------------------------------------------
    def _intent_snapshot(self, active) -> dict:
        from backend.game_logic.intent import get_nation_intent
        snap = {}
        for nation in active:
            view = get_nation_intent(nation, self.world)
            snap[nation] = [view.want_id, view.against, int(view.weight),
                            view.price]
        return snap

    def _war_summaries(self) -> dict:
        out = {}
        for wid, inst in (getattr(self.world, "war_instances", None)
                          or {}).items():
            out[wid] = {
                "attackers": list(inst.get("attackers") or []),
                "defenders": list(inst.get("defenders") or []),
                "ai_initiated": bool(inst.get("ai_initiated")),
                "stated_reason": inst.get("stated_reason"),
                "ended_turn": inst.get("ended_turn"),
                "end_reason": inst.get("end_reason"),
            }
        return out

    def _drain_events(self) -> list:
        world = self.world
        # REV-X1: the map ACCUMULATES and pins. Rebuilding it from the live
        # log each turn (what this used to do) threw away the references that
        # keep the addresses reserved, which is the whole point — see the
        # note on `_seen_events`.
        fresh = [e for e in world.event_log
                 if id(e) not in self._seen_events]
        for event in world.event_log:
            self._seen_events[id(event)] = event
        return [_project(e) for e in fresh]

    def _incoming_proposals(self) -> list:
        """New incoming dialogues addressed to the player this turn."""
        world = self.world
        rows = []
        manager = getattr(world, "dialogue_manager", None)
        candidates = []
        if manager is not None:
            current = manager.peek()
            if current:
                candidates.append(current)
            candidates.extend(manager.iter_queue())
        for dialogue in candidates:
            dtype = str(dialogue.get("type", ""))
            if dtype not in ("incoming_proposal", "incoming_ultimatum"):
                continue
            context = dialogue.get("context") or {}
            proposer = (context.get("source_nation")
                        or dialogue.get("target_nation") or "")
            ptype = str(context.get("proposal_type")
                        or (context.get("proposal") or {}).get("type") or "")
            key = (proposer, ptype, int(dialogue.get("turn_created", -1)))
            if key in self._proposal_keys:
                continue
            self._proposal_keys.add(key)
            rows.append({"proposer": proposer, "ptype": ptype,
                         "dtype": dtype,
                         "turn_created": int(dialogue.get("turn_created", -1)),
                         "decision_reason": str(
                             context.get("decision_reason", "") or "")})
        return rows

    def capture_turn(self, endturn_result) -> dict:
        world = self.world
        active = [n for n in world.get_active_nations() if n != self.player]
        from backend.game_logic.intent import get_france_perceived_intent
        from backend.game_logic.war_council import _standing_strength

        wars_now = getattr(world, "war_instances", None) or {}
        opened = []
        for wid, inst in wars_now.items():
            if wid in self._war_ids:
                continue
            self._war_ids.add(wid)
            opened.append({
                "war_id": wid,
                "attackers": list(inst.get("attackers") or []),
                "defenders": list(inst.get("defenders") or []),
                "ai_initiated": bool(inst.get("ai_initiated")),
                "stated_reason": inst.get("stated_reason"),
                "entry_path": (inst.get("participant_meta") or {}).get(
                    (inst.get("attackers") or [""])[0], {}).get("entry_path"),
            })
        ended = []
        for wid, inst in wars_now.items():
            if inst.get("ended_turn") is None or wid in self._ended_ids:
                continue
            self._ended_ids.add(wid)
            ended.append({
                "war_id": wid,
                "ended_turn": inst.get("ended_turn"),
                "end_reason": inst.get("end_reason"),
                "ai_initiated": bool(inst.get("ai_initiated")),
                "participants": list((inst.get("side_by_nation")
                                      or {}).keys()),
            })

        dispatch_queue = [
            {"type": str(e.get("type", "")),
             "vars": _project(e.get("template_vars", {}), 2),
             # FA slice 2 (Sept 4, 2026): the turn the entry was queued on,
             # so the narration-cap metric can count per PRODUCING turn —
             # see `derive_metrics`.
             "queued_turn": e.get("queued_turn")}
            for e in (getattr(world, "pending_dispatch_events", None) or [])]

        mirror_price, mirror_weight, mirror_target = (
            get_france_perceived_intent(world))

        war_intents = {}
        for nation, record in (getattr(world, "war_intents", None)
                               or {}).items():
            war_intents[nation] = {
                "target": record.get("target"),
                "design_id": record.get("design_id"),
                "foregrounded": bool(record.get("foregrounded")),
                "opened_turn": record.get("opened_turn"),
                "last_soft_block": record.get("last_soft_block"),
            }

        return _jsonify({
            "turn": int(world.current_turn),
            "threat": int(world.threat_level),
            "intents": self._intent_snapshot(active),
            "mirror": [mirror_price, int(mirror_weight), mirror_target],
            "war_intents": war_intents,
            "wars_opened": opened,
            "wars_ended": ended,
            "exhaustion": dict(getattr(world, "war_exhaustion", {}) or {}),
            "gold": {n: int(world.nation_gold.get(n, 0))
                     for n in [self.player] + active},
            "strength": {n: int(_standing_strength(world, n))
                         for n in [self.player] + active},
            "events": self._drain_events(),
            "dispatch_queue": dispatch_queue,
            "incoming_proposals": self._incoming_proposals(),
            "endturn_keys": sorted(list((endturn_result or {}).keys())),
        })

    # -- final ---------------------------------------------------------
    def capture_final(self) -> dict:
        world = self.world
        from backend.game_logic.formations import get_formation_watch
        watches = {}
        active = set(world.get_active_nations())
        # FA slice 2 review round (Sept 4, 2026): a dreamer that was
        # ELIMINATED is its own explanation — "no formation AND no watch"
        # was the digest forgetting the nation rather than the board
        # blocking the dream. Every deck-holding nation is scanned; an
        # inactive one carries `eliminated: True` beside its progress.
        scanned = active | set((getattr(world, "agendas", {}) or {}).keys())
        for nation in sorted(scanned):
            try:
                watch = get_formation_watch(world, nation)
            except Exception as exc:  # observability must not kill the run
                watch = {"error": str(exc)}
            if watch:
                if nation not in active:
                    watch = dict(watch, eliminated=True)
                watches[nation] = _project(watch)
        decks = {}
        for nation, deck in (getattr(world, "agendas", {}) or {}).items():
            decks[nation] = [
                (e.get("id") if isinstance(e, dict) else str(e))
                for e in (deck or [])]
        return _jsonify({
            "formations": _project(
                getattr(world, "nation_formations", {}) or {}),
            "formation_watch": watches,
            "decks": decks,
            "continental_system_members": list(
                getattr(world, "continental_system_members", []) or []),
            "directed_sponsorships": _project(
                getattr(world, "directed_sponsorships", []) or []),
            "compensation_bargains": _project(
                getattr(world, "compensation_bargains", []) or []),
            "diplomatic_guarantees": _project(
                getattr(world, "diplomatic_guarantees", []) or []),
            "war_instances": self._war_summaries(),
            "vassals": {v: {"lord": s.get("lord"),
                            "loyalty": int(s.get("loyalty", 0))}
                        for v, s in (getattr(world, "vassals", {})
                                     or {}).items()},
            "refusal_pairs": len(
                getattr(world, "diplomatic_refusals", {}) or {}),
        })


# ═══════════════════════════════════════════════════════════════════════
# Derived metrics (computed in-runner, consumed by suite + memo)
# ═══════════════════════════════════════════════════════════════════════

def derive_metrics(digest: dict) -> dict:
    player = digest["meta"]["player"]
    turns = digest["turns"]
    needles = tuple(digest["meta"]["france_needles"])

    ai_wars, seam_wars, france_wars = [], [], []
    for row in turns:
        for war in row["wars_opened"]:
            parties = set(war["attackers"]) | set(war["defenders"])
            entry = dict(war, opened_turn=row["turn"])
            if war["ai_initiated"]:
                ai_wars.append(entry)
            elif player in parties:
                france_wars.append(entry)
            else:
                seam_wars.append(entry)

    endings = []
    for row in turns:
        for war in row["wars_ended"]:
            endings.append(dict(war))
    third_party_settlements = [
        w for w in endings
        if player not in (w.get("participants") or [])
        and str(w.get("end_reason") or "") not in ("", "armistice_expired")]

    courts_at_fight = sorted({
        nation for row in turns
        for nation, view in row["intents"].items() if view[3] == "fight"})
    courts_at_coerce_plus = sorted({
        nation for row in turns
        for nation, view in row["intents"].items()
        if view[3] in ("coerce", "fight")})

    # Beats: most types log an event AND queue a dispatch copy, but beat 4
    # (broken_bargain) is dispatch-only (the log gets bargain_reneged /
    # sponsorship_reneged instead — run-4 finding). Count both streams and
    # take the per-type max so double-carried beats count once.
    beats_log, beats_dispatch = {}, {}
    for row in turns:
        for event in row["events"]:
            etype = str(event.get("type", ""))
            if etype in BEAT_TYPES:
                beats_log[etype] = beats_log.get(etype, 0) + 1
        for entry in row["dispatch_queue"]:
            etype = entry["type"]
            if etype in BEAT_TYPES:
                beats_dispatch[etype] = beats_dispatch.get(etype, 0) + 1
    beats = {etype: max(beats_log.get(etype, 0), beats_dispatch.get(etype, 0))
             for etype in set(beats_log) | set(beats_dispatch)}

    # FA slice 2 (Sept 4, 2026): count per PRODUCING turn, not per queue
    # snapshot. This runner reads the queue WITHOUT draining (advance_turn
    # owns the clear), and advance_turn's turn-stamp prune is one frame off
    # by its own comment (`dispatch.py`, the consumption clear): an entry
    # queued INSIDE advance_turn carries the NEW turn number and survives
    # the next cycle's prune. The real client consumes the queue every turn
    # when it builds the morning dispatch, so the player never sees the
    # carry-over — but a snapshot that holds two producer calls' lines read
    # as 4 against a cap of 2. Measured on the slice-2 board at turn 36:
    # Prussia both "hardens" and "eases" in one snapshot, one line from each
    # of two consecutive polls. The prior board never had two consecutive
    # producing turns, which is the only reason this pin was green.
    routine_per_turn = []
    for row in turns:
        by_stamp: dict = {}
        for e in row["dispatch_queue"]:
            if e["type"] in ROUTINE_INTENT_TYPES:
                stamp = e.get("queued_turn")
                by_stamp[stamp] = by_stamp.get(stamp, 0) + 1
        routine_per_turn.append(max(by_stamp.values()) if by_stamp else 0)

    # Soap-opera measurement (§5 pin 13): share of the dispatch-queue
    # column-inches (the diplomatic stream the player reads) spent on
    # events France was not party to. Reported, never "felt".
    total_lines = 0
    non_france_lines = 0
    for row in turns:
        for entry in row["dispatch_queue"]:
            total_lines += 1
            if not _mentions_any(entry, needles):
                non_france_lines += 1
    soap_opera_share = (
        round(non_france_lines / total_lines, 3) if total_lines else 0.0)

    # Q3 shapes: recruit/commission activity + solvency per major.
    recruit_turns = {}
    for row in turns:
        for event in row["events"]:
            etype = str(event.get("type", ""))
            if "recruit" in etype or "commission" in etype:
                nation = str(event.get("nation", "") or "")
                if nation:
                    recruit_turns.setdefault(nation, []).append(row["turn"])

    # Exhaustion monotonicity over AI-vs-AI wars France never joined.
    exhaustion_checks = []
    for war in ai_wars + seam_wars:
        parties = [n for n in (set(war["attackers"])
                               | set(war["defenders"])) if n != player]
        opened = war["opened_turn"]
        closed = next((w.get("ended_turn") for w in endings
                       if w["war_id"] == war["war_id"]), None)
        end = closed if closed is not None else (
            turns[-1]["turn"] if turns else opened)
        span = [row for row in turns if opened <= row["turn"] <= end]
        if len(span) < 5:
            continue
        for nation in parties:
            series = [int(row["exhaustion"].get(nation, 0)) for row in span]
            rises = all(b >= a for a, b in zip(series, series[1:]))
            exhaustion_checks.append({
                "war_id": war["war_id"], "nation": nation,
                "turns": len(span), "monotonic_nondecreasing": rises,
                "series": series})

    # Beat 6 evidence — the pair-level peaces (the [r5] exhausted-pair
    # exits AND full third-party settlements both log third_party_peace
    # with structured proposer/accepter). For each, the two parties' WE
    # window leading into the peace — the DoD's "somebody bleeds and
    # Europe notices" measured at the level the engine actually ends
    # AI-vs-AI belligerency at.
    pair_peaces = []
    for row in turns:
        for event in row["events"]:
            if str(event.get("type")) != "third_party_peace":
                continue
            loser = str(event.get("proposer", "") or "")
            winner = str(event.get("accepter", "") or "")
            peace_turn = row["turn"]
            window = [r for r in turns
                      if peace_turn - 10 <= r["turn"] < peace_turn]
            series = {
                nation: [int(r["exhaustion"].get(nation, 0))
                         for r in window]
                for nation in (loser, winner) if nation}
            pair_peaces.append({
                "turn": peace_turn, "war_id": event.get("war_id"),
                "loser": loser, "winner": winner,
                "we_window": series,
                "both_rose": all(
                    s[-1] >= s[0] and any(b > a for a, b in zip(s, s[1:]))
                    for s in series.values() if len(s) >= 2),
            })

    commissions = []
    for row in turns:
        for event in row["events"]:
            if str(event.get("type")) != "marshal_commissioned":
                continue
            nation = str(event.get("nation", "") or "")
            commissions.append({
                "turn": row["turn"], "nation": nation,
                "marshal": event.get("marshal"),
                "cost": int(event.get("cost", 0) or 0),
                "gold_after": int(row["gold"].get(nation, 0)),
            })

    mirror_series = [row["mirror"] for row in turns]
    proposals_to_france = [p for row in turns
                           for p in row["incoming_proposals"]]

    agenda_shifts = sum(1 for row in turns for e in row["events"]
                        if str(e.get("type")) == "agenda_shift")
    promotions = [e for row in turns for e in row["events"]
                  if str(e.get("type")) == "design_promoted"]
    volte_faces = [e for row in turns for e in row["events"]
                   if str(e.get("type")) == "volte_face"]
    crisis_passed = [e for row in turns for e in row["events"]
                     if str(e.get("type")) == "crisis_passed"]

    return _jsonify({
        "ai_initiated_wars": ai_wars,
        "seam_ai_ai_wars": seam_wars,
        "france_wars_opened": france_wars,
        "war_endings": endings,
        "third_party_settlements": third_party_settlements,
        "pair_peaces": pair_peaces,
        "commissions": commissions,
        "courts_at_fight": courts_at_fight,
        "courts_at_coerce_plus": courts_at_coerce_plus,
        "beats": beats,
        "routine_intent_lines_max_per_turn": (
            max(routine_per_turn) if routine_per_turn else 0),
        "soap_opera_share": soap_opera_share,
        "soap_opera_lines": [non_france_lines, total_lines],
        "recruit_turns": recruit_turns,
        "exhaustion_checks": exhaustion_checks,
        "mirror_series": mirror_series,
        "proposals_to_france": proposals_to_france,
        "agenda_shifts": agenda_shifts,
        "design_promotions": promotions,
        "volte_faces": volte_faces,
        "crisis_passed": crisis_passed,
        "threat_series": [row["threat"] for row in turns],
    })


# ═══════════════════════════════════════════════════════════════════════
# The scripted-France arm (arm b)
# ═══════════════════════════════════════════════════════════════════════

class FranceScript:
    """§4.7 arm (b): a France that ACTS, on a fixed schedule.

    Steps run in the player phase (before the per-turn ambient re-seed),
    through the same executor seams the stage tests drive. Staging
    mutations (the moment conjunction, the courted defeat) use the
    documented fixture idioms; every step logs its honest result.
    """

    def __init__(self):
        self.log = []

    def _record(self, turn, step, result):
        entry = {"turn": turn, "step": step}
        if isinstance(result, dict):
            entry["success"] = bool(result.get("success"))
            entry["message"] = str(result.get("message", ""))[:300]
        else:
            entry["note"] = str(result)[:300]
        self.log.append(entry)

    def step(self, world, executor, game_state, turn_index):
        player = getattr(world, "player_nation", "France")
        # The quartermaster's thumb: the scripted arm never fails a step
        # for want of gold/DP — instrument GATES stay honest, budgets do
        # not confound them.
        world.nation_gold[player] = max(
            int(world.nation_gold.get(player, 0)), 20_000)
        world.diplomatic_points = max(int(world.diplomatic_points), 6)

        handler = getattr(self, f"_turn_{turn_index}", None)
        if handler is not None:
            handler(world, executor, game_state, turn_index)
        # Standing watch: accept the volte-face proposal the turn it
        # lands; while the courted-defeat window is open, keep Russia's
        # delivery lane answered so the courier can fire at all.
        self._accept_volte_face_if_offered(world, executor, turn_index)
        if 11 <= turn_index <= 17:
            self._clear_russia_lane(world)
            from backend.game_logic.ai_diplomacy import (
                _has_pending_proposal_from,
            )
            from backend.game_logic.emergent_designs import (
                volte_face_receptive,
            )
            self._record(turn_index, "volte watch", (
                f"receptive={volte_face_receptive(world, 'Russia', player)} "
                f"pending={_has_pending_proposal_from('Russia', world)} "
                f"state={world.get_diplomatic_state('Russia', player)} "
                f"we={world.war_exhaustion.get('Russia')} "
                f"rel={world.nation_relations.get(world._make_diplo_key(player, 'Russia'))}"))

    # -- schedule ------------------------------------------------------
    # Ambient facts that shape the clock (measured, sweep run 1): Austria
    # overruns Prussia by turn ~6 (survival override, then war_1 entry),
    # so every Prussia-facing step lives in turns 0-5; and a France
    # guarantee of Hanover BEFORE the crisis deters it silently (weight
    # 87-8 < 85 — the deterrent working, but the receipt needs a LIVE
    # foregrounded crisis to kill), so the guarantee moves after the
    # buy-off.
    def _turn_0(self, world, executor, game_state, turn):
        result = executor._diplomatic._execute_sponsor_design(
            {"action": "sponsor_design", "target": "Prussia",
             "raw_input": "sponsor Prussia against Hanover, 100 gold"},
            game_state)
        self._record(turn, "sponsor_design Prussia->Hanover 100g", result)

    def _turn_1(self, world, executor, game_state, turn):
        # Stage the Prussia|Hanover moment: cold pair (+8), a reneged
        # bargain on the record (+15), the holder bankrupt (+3) and
        # exhausted (+5) on base 55 = 86 >= 85 — WITHOUT putting Hanover
        # in a war. Run-3 finding: busying the holder with a staged
        # Hanover|Denmark war flipped Prussia's derivation into the
        # BANDWAGON branch (`against` re-aims at the rival claimant) and
        # the fight posture died; the moment must crest on holder
        # weakness, not holder belligerency. Deep bankruptcy because the
        # income phase repays a -50 purse before the council poll
        # (run-2 finding).
        from backend.game_logic.instruments import _mint_grievance
        world.nation_relations[
            world._make_diplo_key("Prussia", "Hanover")] = -45
        _mint_grievance(world, breaker="Hanover", victim="Prussia",
                        grievance_type="bargain_reneged",
                        source="ai_v_arm_b")
        world.nation_gold["Hanover"] = -5000
        world.war_exhaustion["Hanover"] = 120
        world.nation_gold["Prussia"] = max(
            int(world.nation_gold.get("Prussia", 0)), 2000)
        world.invalidate_bloc_members_cache()
        self._record(turn, "stage Prussia|Hanover moment", "staged")

    def _turn_2(self, world, executor, game_state, turn):
        crisis = (getattr(world, "war_intents", {}) or {}).get("Prussia")
        self._record(turn, "crisis check before buy-off",
                     f"war_intents[Prussia]={crisis}")
        result = executor._diplomatic._execute_buy_off_design(
            {"action": "buy_off_design", "target": "Prussia",
             "raw_input": "buy off Prussia"}, game_state)
        self._record(turn, "buy_off_design Prussia (live crisis)", result)

    def _turn_4(self, world, executor, game_state, turn):
        result = executor._diplomatic._execute_guarantee_nation(
            {"action": "guarantee_nation", "target": "Hanover",
             "raw_input": "guarantee Hanover"}, game_state)
        self._record(turn, "guarantee_nation Hanover", result)

    def _turn_3(self, world, executor, game_state, turn):
        # Renege on France's own compensation: the payer opens war on the
        # recipient — beat 4, aggressor-attributed (§3.3), and the §3.5
        # upward mirror's driver. Must run before Austria's overrun folds
        # Prussia into war_1 (measured turn ~4-5 ambient — run 2's turn-5
        # renege already hit the side-conflict refusal).
        from backend.game_logic.diplomacy import declare_war
        result = declare_war(world, "France", "Prussia")
        self._record(turn, "renege: France declares war on Prussia",
                     result if isinstance(result, dict)
                     else f"declared={result}")

    def _turn_9(self, world, executor, game_state, turn):
        # The paymaster duel: contest Britain's client. The honest verb
        # refuses to bankroll an active belligerent (its design aims
        # France) — record that refusal, then place the bid at the
        # instruments seam (the D5 record IS the bid the subsidy pass
        # reads, coalition.py:1191).
        from backend.game_logic.coalition import (
            get_british_subsidy_recipient,
        )
        from backend.game_logic.instruments import (
            grant_directed_sponsorship,
        )
        client = get_british_subsidy_recipient(world) or "Austria"
        verb = executor._diplomatic._execute_sponsor_design(
            {"action": "sponsor_design", "target": client,
             "raw_input": f"sponsor {client}, 500 gold"}, game_state)
        self._record(turn, f"outbid verb attempt on {client}", verb)
        seam = grant_directed_sponsorship(
            world, payer="France", recipient=client, aim="",
            amount_per_turn=500)
        self._record(turn, f"outbid bid staged at seam for {client}",
                     seam if isinstance(seam, dict) else str(seam))

    def _turn_10(self, world, executor, game_state, turn):
        # Close the ports: seed the Continental System with France's
        # client states (the activation surface is the owned econ rider;
        # the MECHANIC — Britain's purse bleeding — is what scene 6
        # measures).
        members = [v for v, s in (world.vassals or {}).items()
                   if s.get("lord") == "France"]
        world.continental_system_members = members
        self._record(turn, "continental system closed",
                     f"members={members}")

    def _turn_11(self, world, executor, game_state, turn):
        # The courted defeat (scene 4 staging, the Tilsit shape): Russia
        # separate-peaces OUT of the boot war — participant exit, never
        # instance end (run 1 stamped ended_turn on the folded boot
        # instance and corrupted the whole war; the receptivity read
        # accepts participant_meta.exited_turn) — the defeat still shows
        # (WE 80), and the court is courted to the alliance floor. Every
        # clause of volte_face_receptive is then a live reading.
        from backend.game_logic.diplomacy import set_diplomatic_state
        set_diplomatic_state(world, "France", "Russia", "PEACE",
                             "ai_v_arm_b")
        for inst in (getattr(world, "war_instances", None) or {}).values():
            sides = inst.get("side_by_nation") or {}
            if ("France" in sides and "Russia" in sides
                    and inst.get("ended_turn") is None):
                meta = inst.setdefault("participant_meta", {})
                record = meta.setdefault("Russia", {"side": sides["Russia"]})
                if record.get("exited_turn") is None:
                    record["exited_turn"] = int(world.current_turn)
                peaced = inst.setdefault("separate_peaced", [])
                if "Russia" not in peaced:
                    peaced.append("Russia")
        world.war_exhaustion["Russia"] = 80
        world.nation_relations[
            world._make_diplo_key("France", "Russia")] = 45
        world.invalidate_bloc_members_cache()
        self._record(turn, "stage courted defeat (Russia)", "staged")
        self._install_phase_spy()

    def _install_phase_spy(self):
        """Diagnostic wrap on the phase entry (turn_manager imports it
        function-locally, so the module attribute is the seam)."""
        if getattr(self, "_spy_installed", False):
            return
        self._spy_installed = True
        from backend.game_logic import ai_diplomacy as mod
        real = mod.process_diplomatic_phase
        log = self.log

        def spy(nation, world):
            result = real(nation, world)
            if nation == "Russia":
                summary = None
                if isinstance(result, dict):
                    summary = {k: result.get(k) for k in
                               ("proposal_type", "decision_reason",
                                "priority", "recipient")}
                log.append({"turn": int(world.current_turn),
                            "step": "phase spy Russia",
                            "note": str(summary)})
            return result

        mod.process_diplomatic_phase = spy

    def _clear_russia_lane(self, world):
        """The courting is ANSWERED mail, not a full inbox: an idle-France
        run leaves Russia's stale routine asks pending, and the phase's
        per-nation dedup (`_has_pending_proposal_from`) then skips Russia
        every turn — the volte courier never even generates (run-2
        finding). A live player answers mail (IGR-F exists for exactly
        this); the harness clears the lane instead."""
        manager = getattr(world, "dialogue_manager", None)
        if manager is None:
            return

        def _is_stale_russia_mail(dialogue) -> bool:
            # Mirror _has_pending_proposal_from's OWN match exactly —
            # run-4 finding: an unanswered incoming SETTLEMENT offer from
            # the France|Russia boot war matches on target_nation alone
            # (context.source_nation unset), and one such row deadlocks
            # the dedup forever.
            if not dialogue:
                return False
            context = dialogue.get("context") or {}
            from_russia = (
                context.get("source_nation") == "Russia"
                or dialogue.get("target_nation") == "Russia")
            if not from_russia:
                return False
            # Never clear the courier itself — the accept watch owns it.
            # (Run-6 finding: decision_reason lives at CONTEXT level, not
            # inside context.proposal — the terms dict.)
            return str(context.get("decision_reason", "")) != "volte_face"

        current = manager.peek()
        if current and _is_stale_russia_mail(current):
            manager.pop()
        manager._queue = [d for d in manager._queue
                          if not _is_stale_russia_mail(d)]
        from backend.game_logic.ai_diplomacy import (
            _get_cooldowns,
            _set_cooldowns,
        )
        cooldowns = _get_cooldowns(world)
        kept = {k: v for k, v in cooldowns.items()
                if not str(k).startswith("Russia")}
        if len(kept) != len(cooldowns):
            _set_cooldowns(world, kept)

    def _turn_20(self, world, executor, game_state, turn):
        # Scene 1's on-ramp check: accept a standing submission offer if
        # any minor has bandwagoned to the hegemon's mailbox.
        manager = getattr(world, "dialogue_manager", None)
        if manager is None:
            return
        for dialogue in [manager.peek()] + manager.iter_queue():
            if not dialogue:
                continue
            context = dialogue.get("context") or {}
            if str(context.get("proposal_type", "")) == "offer_vassalage":
                result = executor._diplomatic._handle_accept_ai_proposal(
                    dialogue, world)
                self._record(turn, "accept offer_vassalage", result)
                break

    # -- watches -------------------------------------------------------
    def _accept_volte_face_if_offered(self, world, executor, turn):
        manager = getattr(world, "dialogue_manager", None)
        if manager is None:
            return
        # Two passes: the first accept on a conflicted alliance returns
        # the WARNING and pushes a `conflict_alert` continuation (run-7
        # finding — the Tilsit defection is a confirmed choice, §5b.3);
        # accepting THAT executes the transition and beat 5 fires at the
        # ratify chokepoint.
        for _ in range(2):
            target = None
            for dialogue in [manager.peek()] + manager.iter_queue():
                if not dialogue:
                    continue
                context = dialogue.get("context") or {}
                dtype = str(dialogue.get("type", ""))
                is_volte = (str(context.get("decision_reason", ""))
                            == "volte_face")
                is_continuation = (
                    dtype == "conflict_alert"
                    and context.get("source_nation") == "Russia")
                if is_volte or is_continuation:
                    target = dialogue
                    break
            if target is None:
                return
            result = executor._diplomatic._handle_accept_ai_proposal(
                target, world)
            self._record(
                turn,
                f"accept volte-face ({target.get('type')})", result)


# ═══════════════════════════════════════════════════════════════════════
# The runner
# ═══════════════════════════════════════════════════════════════════════

def run_one(seed: str, ambient_base: int, turns: int,
            script: str = "") -> dict:
    if os.environ.get("PYTHONHASHSEED") != "0":
        _die("PYTHONHASHSEED must be 0 (pin 14(c): set iteration order "
             "feeds AI decisions — spawn me as a subprocess)")
    os.environ["SOVEREIGN_SEED"] = seed
    os.environ["LLM_MODE"] = "mock"
    os.environ.pop("SOVEREIGN_SCENARIO", None)
    os.environ.pop("SOVEREIGN_MAP", None)
    sys.path.insert(0, str(REPO_ROOT))

    import random

    from backend.commands.executor import CommandExecutor
    from backend.game_logic.turn_manager import TurnManager
    from backend.models.world_state import WorldState

    world = WorldState.from_scenario(str(SCENARIO_PATH))
    executor = CommandExecutor()
    tm = TurnManager(world, executor=executor)
    game_state = {"world": world, "executor": executor}

    capture = RunCapture(world)
    france_script = FranceScript() if script == "france" else None

    digest = {
        "meta": {
            "seed": seed,
            "ambient_base": int(ambient_base),
            "turns": int(turns),
            "script": script or None,
            "player": capture.player,
            "france_needles": list(capture.france_needles),
        },
        "boot": capture.capture_boot(),
        "turns": [],
    }

    for turn in range(turns):
        if france_script is not None:
            france_script.step(world, executor, game_state, turn)
        random.seed(ambient_base + turn)  # the M7 idiom — LAST before end_turn
        result = tm.end_turn(game_state)
        digest["turns"].append(capture.capture_turn(result))

    digest["final"] = capture.capture_final()
    digest["derived"] = derive_metrics(digest)
    if france_script is not None:
        digest["script_log"] = france_script.log
    return digest


# ═══════════════════════════════════════════════════════════════════════
# Orchestration (subprocess per run — process-fresh determinism)
# ═══════════════════════════════════════════════════════════════════════

def spawn_run(seed: str, ambient_base: int, turns: int,
              script: str = "", json_out: Path = None,
              timeout: int = 600) -> dict:
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "0"
    env["PYTHONPATH"] = str(REPO_ROOT)
    env.pop("SOVEREIGN_SCENARIO", None)
    env.pop("SOVEREIGN_MAP", None)
    env.pop("PYTHONIOENCODING", None)  # the cp1252 subprocess trap
    # `--seed` is AUTHORITATIVE. Found August 4, 2026 during the EC-L slice:
    # the assurance fixtures (`test_ai_intent_assurance.py`) are MODULE-scoped,
    # and pytest sets higher-scoped fixtures up BEFORE function-scoped autouse
    # ones — so they ran outside conftest's `SOVEREIGN_SEED=historical` pin and
    # inherited whatever the developer's shell happened to carry. Every sweep
    # pin in that file was therefore running on an unpinned seed, and the
    # symptom is a DoD assertion that flips on an unrelated change while the
    # full suite stays green. The seed the caller ASKED for now goes into the
    # child's environment too, so the child cannot read a stale ambient one.
    env["SOVEREIGN_SEED"] = str(seed)
    args = [sys.executable, str(Path(__file__).resolve()), "--run",
            "--seed", seed, "--ambient-base", str(ambient_base),
            "--turns", str(turns), "--emit"]
    if script:
        args += ["--script", script]
    proc = subprocess.run(args, env=env, cwd=str(REPO_ROOT),
                          capture_output=True, text=True, timeout=timeout)
    if proc.returncode != 0:
        _die(f"run {seed}/{ambient_base}/{script or 'ambient'} failed:\n"
             f"{proc.stdout[-2000:]}\n{proc.stderr[-2000:]}")
    payload_line = [ln for ln in proc.stdout.splitlines()
                    if ln.startswith("PAYLOAD=")][-1]
    digest = json.loads(payload_line[len("PAYLOAD="):])
    if json_out is not None:
        json_out.parent.mkdir(parents=True, exist_ok=True)
        json_out.write_text(json.dumps(digest, indent=1),
                            encoding="utf-8")
    return digest


def _control_view(digest: dict) -> dict:
    """The byte-comparable projection for Arm A (drops nothing that
    matters: the whole per-turn record IS the trace)."""
    return {"boot": digest["boot"], "turns": digest["turns"],
            "final": digest["final"], "derived": digest["derived"]}


def _variance_signature(digest: dict) -> dict:
    derived = digest["derived"]
    return {
        "ai_war_count": len(derived["ai_initiated_wars"]),
        "war_turns": sorted(
            w["opened_turn"] for w in derived["ai_initiated_wars"]
            + derived["seam_ai_ai_wars"] + derived["france_wars_opened"]),
        "courts_at_fight": derived["courts_at_fight"],
    }


def run_all(out_dir: Path, turns: int, acceptance_n: int) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = {"turns": turns}

    # Arm A — control: two processes, same seed, same K.
    a1 = spawn_run("historical", AMBIENT_K, turns,
                   json_out=out_dir / "armA_historical_run1.json")
    a2 = spawn_run("historical", AMBIENT_K, turns,
                   json_out=out_dir / "armA_historical_run2.json")
    identical = (json.dumps(_control_view(a1), sort_keys=True)
                 == json.dumps(_control_view(a2), sort_keys=True))
    summary["arm_a"] = {"byte_identical": identical}
    print(f"ARM A control: byte_identical={identical}")
    if not identical:
        print("ARM A RED — nothing else in this sweep means anything.")

    # Arm B — variance: different seed, same K.
    arm_b = {}
    baseline_sig = _variance_signature(a1)
    baseline_boot = a1["boot"]
    for seed in ARM_B_SEEDS[1:]:
        digest = spawn_run(seed, AMBIENT_K, turns,
                           json_out=out_dir / f"armB_{seed}.json")
        sig = _variance_signature(digest)
        boot_differs = digest["boot"] != baseline_boot
        sig_differs = sig != baseline_sig
        weight_series_differ = any(
            row_a["intents"] != row_b["intents"]
            for row_a, row_b in zip(a1["turns"], digest["turns"]))
        arm_b[seed] = {
            "boot_differs": boot_differs,
            "signature": sig,
            "signature_differs": sig_differs,
            "weight_series_differ": weight_series_differ,
        }
        print(f"ARM B {seed}: boot_differs={boot_differs} "
              f"sig_differs={sig_differs} "
              f"weights_differ={weight_series_differ}")
    summary["arm_b"] = {"baseline_signature": baseline_sig, "seeds": arm_b}

    # Arm C — acceptance: N runs, seed AND ambient K varying.
    arm_c = {}
    for index in range(acceptance_n):
        seed = SWEEP_SEEDS[index % len(SWEEP_SEEDS)]
        k = AMBIENT_K + AMBIENT_PRIME * index
        digest = spawn_run(seed, k, turns,
                           json_out=out_dir / f"armC_{index:02d}_{seed}.json")
        derived = digest["derived"]
        arm_c[f"{index:02d}_{seed}_k{k}"] = {
            "ai_wars": len(derived["ai_initiated_wars"]),
            "seam_wars": len(derived["seam_ai_ai_wars"]),
            "war_turns": _variance_signature(digest)["war_turns"],
            "courts_at_fight": derived["courts_at_fight"],
            "third_party_settlements": len(
                derived["third_party_settlements"]),
            "agenda_shifts": derived["agenda_shifts"],
            "promotions": len(derived["design_promotions"]),
            "volte_faces": len(derived["volte_faces"]),
            "crisis_passed": len(derived["crisis_passed"]),
            "formations": list((digest["final"]["formations"] or {}).keys()),
            "soap_opera_share": derived["soap_opera_share"],
            "beats": derived["beats"],
        }
        print(f"ARM C {index:02d} {seed} k={k}: "
              f"{json.dumps(arm_c[f'{index:02d}_{seed}_k{k}'])[:200]}")
    summary["arm_c"] = arm_c

    # Arm (b) — the scripted France.
    arm_scripted = {}
    for seed in SCRIPTED_SEEDS:
        digest = spawn_run(seed, AMBIENT_K, turns, script="france",
                           json_out=out_dir / f"armb_scripted_{seed}.json")
        derived = digest["derived"]
        arm_scripted[seed] = {
            "script_log": digest.get("script_log", []),
            "beats": derived["beats"],
            "crisis_passed": derived["crisis_passed"],
            "mirror_first_last": [derived["mirror_series"][0],
                                  derived["mirror_series"][-1]],
            "mirror_peak_weight": max(
                m[1] for m in derived["mirror_series"]),
            "volte_faces": len(derived["volte_faces"]),
            "proposals_to_france": len(derived["proposals_to_france"]),
        }
        print(f"ARM (b) {seed}: beats={derived['beats']} "
              f"crisis_passed={len(derived['crisis_passed'])}")
    summary["arm_scripted"] = arm_scripted

    (out_dir / "summary.json").write_text(
        json.dumps(summary, indent=1, sort_keys=True), encoding="utf-8")
    print(f"SUMMARY written to {out_dir / 'summary.json'}")
    return summary


# ═══════════════════════════════════════════════════════════════════════

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--seed", default="historical")
    parser.add_argument("--ambient-base", type=int, default=AMBIENT_K)
    parser.add_argument("--turns", type=int, default=DEFAULT_TURNS)
    parser.add_argument("--script", default="")
    parser.add_argument("--emit", action="store_true",
                        help="print PAYLOAD=<json> on stdout")
    parser.add_argument("--json-out", default="")
    parser.add_argument("--out", default="")
    parser.add_argument("--acceptance-n", type=int, default=10)
    args = parser.parse_args()

    if args.run:
        digest = run_one(args.seed, args.ambient_base, args.turns,
                         script=args.script)
        if args.json_out:
            out = Path(args.json_out)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(digest, indent=1), encoding="utf-8")
        if args.emit or not args.json_out:
            print("PAYLOAD=" + json.dumps(digest))
        return
    if args.all:
        if not args.out:
            _die("--all needs --out <dir>")
        run_all(Path(args.out), args.turns, args.acceptance_n)
        return
    parser.print_help()


if __name__ == "__main__":
    main()
