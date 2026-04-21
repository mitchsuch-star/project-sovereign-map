# Memory and Pressure Spec

> **Status:** v2.4.3 (Deep-audit fixes — Hegemony refactor + §7.8 / §9.5 clarifications + audit cleanup + deep-audit A1-A14 / B1-B7 / C1-C7 resolutions)
> **Date:** April 20, 2026 (v2.4.3 deep-audit fixes); April 19, 2026 (v2.4.2 audit cleanup + v2.4.1 clarification pass + v2.4 hegemony refactor); April 17, 2026 (v2.3 DG-4 amendment); April 16, 2026 (v2.2 audit); v2.0 rescope; v1.0 April 14, 2026
> **Phase placement:** Design Refinement queue item 1 (formerly "Reliability + Commitments"; renamed in v2.0).
> **Companion docs:** `RELIABILITY_IMPLEMENTATION_PLAN.md`, `COMMITMENTS_PRESENTATION_SPEC.md` (the `C3-lite` presentation pass), `WAR_BARGAIN_SPEC.md` (bargain mechanic, deferred to Peace Deals phase), `SCALE_READINESS_PLAN.md` §DG-4 Amendment (call-to-arms refusal / honored-costly contract, source of truth for §8.8), `COALITION_SPEC.md` (threat ladder; Hegemony Pressure adds passive bloc-share contribution).

---

## v2.4 rescope note (April 19, 2026) — Hegemony refactor

The April 19 design pass established that the v2.3 plan had grown too prescriptive for its own goals. The substrate that shipped is excellent — bilateral betrayal memory, episode_id threading, witness scoping, hard-reject posture all map cleanly to "Britain never forgets Amiens" / "Austria remembers being humiliated three times." The remaining ~68-74 tests across Slice B were stacking acceptance-formula constants players cannot feel and a 4-pair static concern seed that the spec itself (§7.7) admitted gets thrown away at full-Europe scale.

The Napoleonic period's diplomatic engine was the **balance-of-power doctrine**: whoever's bloc is largest, the others converge against it. Castlereagh's pentarchy, Pitt's continental subsidies, Metternich's Vienna framework — all derive from one principle expressible as a single per-turn calculation.

The rescope:

1. **§7 Concern System → Hegemony Pressure System.** Static seeded `nation_concerns` is deleted. Per-turn `_calculate_hegemony_pressure(world)` reads bloc shares dynamically and contributes passive threat against whichever bloc is largest. Hegemon-agnostic by construction — France today, but any bloc that crosses the threshold tomorrow.
2. **§9 Acceptance formula collapses.** `direct_concern_mod` / `concern_conflict_mod` / composite `political_commitment_mod` floor are deleted. Replaced by one `hegemony_target_mod` (negative on proposals from a nation in the hegemon bloc, scaling with bloc share). `bilateral_betrayal_mod` simplifies to `-6 per active strike` flat — the existing 3-strike hard-reject posture still does the door-shut work.
3. **No data structure for rivalries.** Rivalries become *derived signals* read from bloc geometry + betrayal_history, not stored fields. The `nation_concerns` field is removed from the v0.1 ship list.
4. **Slice B rewrites.** B-A1-fill (concern seed), B-B2a-fill (third-party ratification anger), B-B6 (redemption tick) are cancelled. New B-Hegemony slice replaces them. B-B1 collapses to two simple modifiers. B-B3 (paradox rename) and B-B7 (Make Amends) keep their existing scope.
5. **Slice C presentation trims.** Named-diplomat resolution + paradox popup keep. Elevated rail-card variant + split-voice render infrastructure cut — three events do not justify the infra.
6. **Substrate already shipped is unchanged.** No removal of `betrayal_history`, `next_episode_id`, `commitment_event_metadata`, witness scoping, hard-reject posture, structured `warnings[]`, cascade metadata. The hegemony engine layers on top of the existing `coalition.py` threat ladder.
7. **§8.8 DG-4 call-to-arms work is unchanged.** Orthogonal to the balance-of-power refactor; rides on the same betrayal substrate.

**Test budget:** ~25-30 tests, 1 session (down from ~68-74 / 3 sessions).

**What this preserves vs v2.3:** all shipped substrate, all design intent (Napoleonic friction, betrayal memory, repair gestures, named diplomats), DG-4 work, paradox rename, Make Amends concept.

**What this drops:** static concern seed, three new acceptance modifiers + composite floor, redemption tick, third-party ratification anger loop, elevated-card rail infra. Each was load-bearing only for design pressure that the hegemony engine now expresses more directly.

---

## v2.0 rescope note (April 16, 2026)

The April 16 audit established:

- The substrate (betrayal memory, episode_id threading, witness `scope_reason`, hard-reject posture, structured `warnings[]`, paradox episode continuity) is **shipped and tested** (~220 targeted tests passing).
- The promise mechanic (`war_bargain` / `diplomatic_commitments` / `join_opportunity` / `counter_bargain` / `war_entry_score`) was **never implemented** and is not buildable in a single phase together with the substrate.
- The acceptance-formula integration of the substrate (graduated `bilateral_betrayal_mod`, `direct_rivalry_mod`, `rival_conflict_mod`, third-party rival anger on ratification, rivalry seed data) was **partially missing**.
- The presentation spec was specced two audit rounds deep (`C3a` + `C3b`) for events that the engine cannot produce.

The rescope:

1. **War bargains move out** to `WAR_BARGAIN_SPEC.md`, scheduled in the Peace Deals phase after `Bilateral Peace Hardening` and `War Purpose + Score Semantics`.
2. **Phase rename:** `Reliability + Commitments` → `Memory and Pressure`. The new name reflects the actual scope: betrayal memory + rivalry / formula pressure + the legacy paradox renamed.
3. **Scope what remains to ship:** seed `nation_concerns`, fill the acceptance formula with the spec values for the modifiers we have data for, wire third-party anger on treaty deepening, rename `alliance_paradox` to `commitment_paradox`, and ship the narrow `C3-lite` presentation pass.
4. **Presentation rescope:** `COMMITMENTS_PRESENTATION_SPEC.md` collapses `C3a` + `C3b` into one `C3-lite` slice that delivers the named-diplomat / elevated-rail / split-voice flavor for the events that *do* fire today.

This spec covers the engine half of the rescope. Bargain content is preserved in `WAR_BARGAIN_SPEC.md` so nothing is lost; section numbers below intentionally skip slots that moved (e.g. former §9 is now in `WAR_BARGAIN_SPEC.md` §8).

---

## 1. Purpose

Memory and Pressure defines the political-memory and political-pressure layer for v0.1 diplomacy:

1. Nations remember betrayal in a way that changes both numbers and posture.
2. Nations care who France aligns with — rivalry creates real friction and forced choices.
3. The acceptance formula expresses graded political pressure, not only a binary hard-reject gate.

It deliberately does **not** ship a promise mechanic. Promises (war bargains) need bilateral peace hardening and war-purpose semantics underneath them; they live in `WAR_BARGAIN_SPEC.md`.

---

## 2. Problems To Solve

### P1. Universal friendship is too easy

France can drift toward broad friendship unless rivals punish opposite-camp alignment hard enough to force tradeoffs.

### P2. Betrayal memory is too shallow

Breaking a treaty hurts in the moment, but the game still lacks enough durable bilateral memory to make repeated bad faith structurally costly.

### P3. The acceptance formula doesn't yet use the memory

Even after the substrate ships, the live formula treats betrayal as a 0-or-100 gate (under 3 strikes nothing changes; at 3 strikes the door closes). No graded pressure.

### P4. Big political moments still land as log lines

`hard_reject_posture_triggered`, `commitment_paradox_resolved`, and `diplomatic_treaty_broken` (french_breach) all emit rich payloads and render as one-liner notifications. The `C3-lite` pass closes that gap.

---

## 3. Goals

- Make **bloc dominance** the central political pressure — when one alliance bloc holds too much of European power, the other major powers converge against it. Players feel the Napoleonic balance-of-power doctrine through a single visible meter, not through hidden formula stacking.
- Separate "France is generally reliable" (global reliability) from "this nation thinks France betrayed it" (bilateral betrayal memory). Both still drive acceptance and posture.
- Express bilateral memory as graded pressure (strike count → acceptance penalty + door-shut at 3) rather than a brute-force gate alone.
- Make the moments that matter (door-closing, paradox, betrayal) feel like political events through named-diplomat copy and the existing presentation surfaces.
- Give the player **one deliberate repair gesture** (Make Amends, §8.6.1) so repaired relationships are a chosen act, not a waiting game.
- Keep rules machine-readable for AI and tests.
- Keep the engine **hegemon-agnostic** — France today is the hegemon by starting position; any bloc that crosses the share threshold later becomes the coalition target without code changes.
- Keep the first implementation legible on the current 5-nation / 19-region map; same engine generalizes to 13-20 nations without rewrite.

---

## 4. Non-Goals

- No war bargains, ally-entry pipeline, counter-bargains, `join_opportunity`, `pending_declaration`, or `war_entry_score` (all in `WAR_BARGAIN_SPEC.md`).
- No common peace, ally beneficiaries, conference-style spoils allocation.
- No new diplomacy screen family — extends existing wizard / popup / ledger / dispatch surfaces.
- No dynamic power tiers, bloc pressure, or strategic focus.
- No periodic per-turn bargain reminders or warning ladders (event-driven only).
- No coalition generalization (defer to D2 follow-up); evaluators stay parameterized but data stores stay anti-France-only in v0.1.

---

## 5. Design Principle

Political pressure in v0.1 has three layers:

1. **Hegemony pressure** — when one alliance bloc holds too much of European power, other major powers converge against it (§7). This is the structural Napoleonic friction — the balance-of-power doctrine. Nations still care *who* France aligns with, but that concern is expressed through bloc-share math, not authored rivalry pairs.
2. **Reliability memory** — nations care whether France generally keeps its word.
3. **Bilateral betrayal memory** — nations care what France did to them specifically.

The rule that governs the spec:

- only punish the player for outcomes France could actually shape
- only explicit, player-surfaced obligations may create breach or betrayal

That means:

- no breach states triggered by AI inactivity alone
- no invisible contradictory obligations
- breach is recorded only on the player's explicit confirmed action

---

## 6. System Overview

The pressure layer has four player-facing data concepts plus shared engine seams.

### 6.1 Global reliability (already shipped)

- `world.diplomatic_reliability: Dict[str, int]` — nation-keyed shared global reputation scalar.
- Storage and emit paths stay actor-aware (no France-literal hardcodes).
- Used for broad acceptance modifiers and ledger summaries.

### 6.2 Bilateral betrayal memory (already shipped)

- `world.betrayal_history: Dict[str, Dict]` — directional key `from_nation|to_nation`.
- Value: `{strikes: List[StrikeRecord], categories: Set[str], last_turn: int}`.
- Each `StrikeRecord` is `{severity, turn, episode_id, decays_on_turn}`.
- Episode-cap queries filter by `episode_id`; severity-scaled decay reads each strike's own `decays_on_turn`.
- Pair-level `last_turn` is cached "most recent offense" for ledger only — not authoritative for decay or cap enforcement.

### 6.3 Hegemony Pressure (no stored data — computed per turn)

**v2.4 change:** the static `nation_concerns: Dict[str, Dict]` field is **deleted from the v0.1 ship list**. Bilateral concern is no longer a stored authored data structure. It is a derived signal computed from bloc geometry each turn.

- `_calculate_hegemony_pressure(world) -> Dict[str, int]` — returns `{hegemon_nation: threat_increment}` per turn, or `{}` if no bloc crosses the threshold.
- `world.get_bloc_members(nation: str) -> List[str]` — per-turn cached helper. Returns nation + its vassals + nations holding `ALLIANCE` or `DEFENSIVE_ALLIANCE` with it.
- `power_score(nation: str, world) -> int` — territory count weighted by `power_tier` from scenario data (`major=3, secondary=2, minor=1` multiplier on region count).
- v0.1 ships **no authored static rivalry seed**. Bilateral friction emerges from: (a) the asker being part of the current hegemon's bloc, (b) accumulated betrayal strikes, (c) §8.8 grievance flags from defensive-call refusals.

The hegemony engine is described in §7.

### 6.4 War bargains

**Moved to `WAR_BARGAIN_SPEC.md`.** Memory and Pressure does not implement `diplomatic_commitments` or `next_commitment_id`. The substrate code stubs `region_observer` witness scope pending the bargain store; that branch reactivates when `WAR_BARGAIN_SPEC` lands.

### 6.5 Shared engine seams (already shipped)

- `episode_id` — root-cause identifier on all diplomatic consequences from one explicit trigger; enforces strike caps by cause, not by whole turn. Allocator is `_allocate_episode_id(world)`; counter is `world.next_episode_id` (serialized).
- `commitment_event_metadata` — primitive payload on dispatch / campaign-log events: `episode_id`, `end_reason_family`, `end_reason_action`, `fault_nation`, `decision_reason`, `trigger_context`, deterministic deltas, `witnesses[].scope_reason`, `dominant_witness_scope`.

`opposition_graph` and `war_bloc.target_nation` seams are intentionally **not** stood up in v0.1 (cut in the rescope). When `WAR_BARGAIN_SPEC` and the later `Coalition Generalization` follow-up land, helpers parameterized on `(ratifier, new_treaty)` and `(actor, victim)` accept opposition pairs from a future `get_opposition_pairs()` helper without needing rewrites.

---

## 7. Hegemony Pressure System

> **v2.4 terminology:** v2.0-v2.3 called this the "Concern System" with a static `nation_concerns` data structure. v2.4 collapses that into a per-turn **Hegemony Pressure** calculation. The concept is the Napoleonic balance-of-power doctrine — Castlereagh's pentarchy, Pitt's continental subsidies, Metternich's Vienna framework — expressible as one principle: *whoever's bloc is largest, the others converge against it.* No authored rivalry pairs; rivalry emerges from bloc geometry.

**Design north star:** the mechanic's job is to make the great powers sort naturally into blocs when one court becomes too dominant. The player should experience it as **signal -> response -> consequence**, not as a hidden anti-France debuff. Great powers do the visible balancing; minors mostly bandwagon, hedge, or seek shelter under a patron. v0.1 keeps this cheap by reusing the same bloc-share math — no second "legitimacy" meter, no per-pair concern table revival.

### 7.1 Bloc definition

A nation's **bloc** at any given turn is the set of nations whose military and diplomatic interest is bound to it:

```python
_DEEP_BLOC_TREATY_STATES = {"ALLIANCE", "DEFENSIVE_ALLIANCE"}


def _top_overlord(world, nation: str) -> str:
    """Walk the vassal `lord` chain until it terminates. Returns the top overlord.

    Cycle-safe: a self-cycle or mutual-lord data error terminates at the first
    revisited nation rather than looping forever.
    """
    visited = {nation}
    current = nation
    while True:
        record = getattr(world, 'vassals', {}).get(current)
        if not record:
            return current
        lord = record.get("lord")
        if not lord or lord in visited:
            return current
        visited.add(lord)
        current = lord


def get_bloc_members(world, leader: str) -> List[str]:
    """Per-turn cached helper. Returns leader + dependents + close allies.

    Consumes existing helpers only:
      - `world.vassals` dict (nation -> {lord, ...})
      - `world.get_diplomatic_state(a, b)` returns a string treaty level
      - `world.get_active_nations()` cached per turn
    Walks the full `lord` chain so sub-vassals (Confederation-of-the-Rhine-style
    nesting) surface on the top overlord's bloc list.
    """
    members = {leader}
    for vassal_name in getattr(world, 'vassals', {}):
        if _top_overlord(world, vassal_name) == leader:
            members.add(vassal_name)
    for other in world.get_active_nations():
        if other == leader:
            continue
        if world.get_diplomatic_state(leader, other) in _DEEP_BLOC_TREATY_STATES:
            members.add(other)
    return sorted(members)
```

Rules:

- Mutual ALLIANCE / DEFENSIVE_ALLIANCE counts both directions — Saxony in France's bloc means France in Saxony's bloc.
- A vassal is in its top overlord's bloc only. `_top_overlord` walks the `lord` chain recursively — vassal-of-vassal, sub-vassal-of-vassal, etc. all surface on the chain's terminus. This is the canonical case for historical sub-vassal nesting (Confederation of the Rhine 1807-13).
- NON_AGGRESSION and OPEN_BORDERS do **not** count as bloc membership — they are non-commitment treaty levels.
- A nation can only have one lord in normal data; `_top_overlord` handles the self-cycle / mutual-lord data-error case by terminating at the first revisited nation rather than looping. There is no "two-lord collision" tie-break in v0.1 because the `lord` field is scalar. If a future multi-overlord system lands (joint protectorates, etc.), resolve collisions by `power_score(overlord_a)` vs `power_score(overlord_b)`, then alphabetical on nation name.
- Per-turn cache; invalidated on treaty ratification, vassal change, war declaration, peace.

Worked example:

- France is the top overlord of Bavaria, and Saxony's `lord` is Bavaria. `get_bloc_members(world, "France")` includes both Bavaria and Saxony even though Saxony is not France's direct vassal. If Austria is also in `DEFENSIVE_ALLIANCE` with France, the returned bloc is `["Austria", "Bavaria", "France", "Saxony"]` after sorting.

**Helper-compat note:** v0.1 code currently lacks `world.get_vassals_of(leader)`, `world.get_treaty_state(a, b)`, and a `TreatyState` enum. The engine reads through existing seams: the `world.vassals` dict is iterated inline, `world.get_diplomatic_state(a, b)` returns string literals like `"ALLIANCE"`, and the bloc-treaty test uses the string-set `_DEEP_BLOC_TREATY_STATES` shown above. If a future refactor introduces a `TreatyState` enum, the helper swap is mechanical.

### 7.2 Power score

A nation's **power score** is the input to hegemony detection. v0.1 uses a simple, scenario-data-driven formula that scales without rewrite:

```python
_POWER_TIER_WEIGHT = {"major": 3, "secondary": 2, "minor": 1}
_POWER_TIER_DEFAULT = "secondary"  # fallback when scenario data is missing


def power_score(nation: str, world) -> int:
    """Territory count weighted by authored power_tier. v0.1 simple form."""
    region_count = len(world.get_nation_regions(nation))  # already cached
    tier = world.get_power_tier(nation) or _POWER_TIER_DEFAULT
    tier_weight = _POWER_TIER_WEIGHT.get(tier, _POWER_TIER_WEIGHT[_POWER_TIER_DEFAULT])
    return region_count * tier_weight
```

Rules:

- `power_tier` is authored scenario data per `SCALE_READINESS_PLAN.md` §"Phase 0 Cross-Cutting Taxonomy". Stable for a campaign, never mutated at runtime.
- Territory count is already cached per turn via `get_nation_regions()` (CLAUDE.md golden rule 8).
- This formula is intentionally simple. v0.2+ may add manpower / treasury / military-strength terms; the helper signature stays stable.
- A `bloc_power(leader, world)` helper sums power_score across `get_bloc_members(leader)`.

**Helper-compat note:** v0.1 code does not yet expose `world.get_power_tier(nation)`, and scenario files do not yet carry `power_tier` authoring. B-Hegemony adds both: `power_tier` is authored as a field on each nation record in scenario config (colocated with capital, color, starting AP per `SCALE_READINESS_PLAN.md` §"Phase 0 Cross-Cutting Taxonomy"), and `world.get_power_tier(nation)` reads directly from that authored record with the `_POWER_TIER_DEFAULT` fallback shown above. **No separate `world.nation_power_tiers: Dict[str, str]` runtime map is created** — SCALE_READINESS_PLAN §Phase 0 is explicit that the authored scenario config is the single source of truth; runtime reads, not mutates. The current 13-nation roster mapping lives in `SCALE_READINESS_PLAN.md` §"Phase 0 Cross-Cutting Taxonomy". Serialization concern is nil: authored scenario data is recreated from scenario files on load, not persisted in save state.

### 7.3 Hegemony detection (the engine)

Per turn, during `process_coalition_turn` in `coalition.py`:

```python
def _calculate_hegemony_pressure(world) -> Dict[str, int]:
    """Per-turn passive threat from bloc-share dominance. Balance-of-power doctrine."""
    active = world.get_active_nations()
    european_power = sum(power_score(n, world) for n in active)
    if european_power == 0:
        return {}
    majors = [n for n in active if world.get_power_tier(n) == "major"]
    if not majors:
        # Defensive fallback — if no nation is authored as `major`, evaluate the canonical
        # v0.1 majors instead of expanding to every active nation. Expanding to all actives
        # silently grows the candidate pool (every minor evaluated as a potential hegemon),
        # which both bloats the calc at scale and degrades the design intent ("majors set
        # the bar"). The safe-list keeps v0.1 behavior correct even when scenario data
        # has not yet authored `power_tier`. Replace this fallback with `power_tier`
        # authoring on every scenario as part of B-Hegemony's prerequisite check.
        majors = [n for n in ("France", "Britain", "Russia", "Austria", "Prussia") if n in active]
        if not majors:
            majors = list(active)  # last-resort safety for unknown rosters (mods, tests)
    bloc_shares = {
        leader: bloc_power(leader, world) / european_power
        for leader in majors
    }
    # Deterministic tie-break: highest share, then highest absolute bloc_power,
    # then alphabetical nation name. Avoids Python `max`'s first-occurrence
    # bias on equal shares, which would otherwise depend on `majors` iteration
    # order — fine at 5 nations, not fine at 13+ where two blocs may tie exactly.
    ordered = sorted(
        bloc_shares.items(),
        key=lambda kv: (-kv[1], -bloc_power(kv[0], world), kv[0]),
    )
    hegemon, share = ordered[0]
    if share < 0.33:
        return {}  # no hegemon — balance is healthy
    pressure = _hegemony_pressure_for_share(share)
    return {hegemon: pressure}


def _hegemony_pressure_for_share(share: float) -> int:
    """Threat increment per turn based on bloc share. Authored ladder.

    Gates align to the 33 / 50 / 60 beat thresholds so every per-turn pressure
    increase coincides with a same-turn `balance_of_europe_shifted` beat — no
    silent accrual band, no unbeated jumps. The 70%+ step is intentional crisis
    intensification (1812 territory) without a new naming tier per §8.1a.
    """
    if share < 0.33: return 0   # safe (no beat, no pressure)
    if share < 0.50: return 1   # noticed   — paired with 33% beat
    if share < 0.60: return 3   # alarming  — paired with 50% beat
    if share < 0.70: return 5   # crisis    — paired with 60% beat
    return 8                     # naked hegemony (≥70%, 1812 / 1813) — no new beat, framing intensifies per §8.1a
```

Output: `{hegemon_nation: threat_increment}`. The increment is added to `coalition.py`'s existing `threat_level` scalar via the existing `add_threat()` API.

Rules:

- Hegemon-agnostic by construction — the engine identifies whichever bloc is largest. France today by starting position; any bloc later.
- Below 33% share, no passive pressure accrues and no `balance_of_europe_shifted` beat fires. Coalitions can still form from event-based threat (battles, captures, vassalizations) per the existing `coalition.py` ladder.
- Bloc share is recomputed each turn from current treaty / vassal state. Pressure decays naturally when the hegemon's bloc shrinks (allies defect, vassals released, territories lost).
- The pressure ladder values (1/3/5/8) and gates (33/50/60/70) are authored constants in `coalition.py`. Tunable in playtest. Gate values must remain aligned with the §8.1a beat thresholds — moving one without the other re-creates the silent-tax failure mode.
- v0.1 the threat scalar in `coalition.py` remains France-targeted by current implementation; the engine returns the hegemon for forward-compat surface (so display copy can name the actual hegemon nation rather than hardcoding "France"). Generalizing the threat scalar to per-target `Dict[str, int]` is a one-helper refactor when a non-French hegemon becomes possible — explicitly out of v0.1 scope.
- **Non-France-hegemon guard (call-site contract).** The `add_threat` wire-up in `process_coalition_turn` must gate on `hegemon == world.player_nation` before adding the passive increment. Rationale: `_calculate_hegemony_pressure` is hegemon-agnostic and may return `{Russia: +5}` in a losing campaign, but the threat_level scalar still accumulates against France in v0.1. Unguarded, this would add Russia's dominance threat *to France's own scalar*, which is the wrong-target bug R5 flags. The guard clause is: *if the hegemon is not the player_nation, emit a debug log for telemetry and skip the `add_threat` call this turn*. Balance of Europe headline copy still names the real hegemon (so the player sees "Russia leads with 47%"), but the coalition pressure accrual path waits for D2 Coalition Generalization.

**Threshold-crossing signal contract (required for feel, not optional polish):**

- The first time the player's bloc crosses **33%**, **50%**, or **60%** of Continental power, fire a same-turn **Balance of Europe** beat as a **named-diplomat notification** (the persistent-alert event family in `notifications.py`). The beat surface MUST NOT be (a) the Diplomatic Ledger Balance-of-Europe headline itself or (b) the Morning Dispatch's Balance-of-Europe summary line — both of those surfaces re-present the *current state*, and using either as the threshold beat collapses signal and state into one clue, defeating the "headline is not the first clue" rule. The notification is the upstream event; the headline and dispatch reflect the new state on the same turn.
- `33%` = **noticed**. A named diplomat or chancery line tells the player that courts are beginning to count obligations and patrons. Copy uses the *descriptive* label only (e.g. *"a French-led alignment"*) — the authored proper name has not yet earned its entrance per `COMMITMENTS_PRESENTATION_SPEC.md` §8.1a.
- `50%` = **alarming**. A named diplomat explicitly frames Europe as starting to align against the hegemon; this is the "subsidies / consultations begin" beat, and the scene in which Europe names the system out loud for the first time (e.g. *"the French System"*). The authored proper bloc name unlocks at this band per §8.1a.
- `60%` = **crisis**. The line must make clear that the continent is hardening into camps and that the next deep treaty will be read politically, not bilaterally. The same proper name persists — the intensification lives in the framing, not in a renamed bloc per §8.1a.
- If `world.coalition_cooldown > 0` when an upward beat fires, the line must acknowledge both facts at once: Europe is hardening, but the last coalition's dissolution still binds the courts for `{turns_remaining}` turns. This clause is mandatory at the `60%` crisis band; otherwise the player hears "crisis" and sees a cooldown timer and concludes the beat is lying.
- Beats do **not** add a second pressure mechanic. They are pure surface visibility over the existing bloc-share calculation.
- Upward beats fire only on first crossings into a higher band. Downward crossings from `60% -> 59%` or `50% -> 49%` are not allowed to be totally silent: emit one same-turn Talleyrand advisory aside in his existing bloc-naming register (not a rail notice, not a dispatch headline, no counter-play hint) so expensive compliance is visibly rewarded. Falling below `33%` resets `world.last_hegemony_signal_band` to `0`.
- The below-`33%` reset is intentional rather than "reset on every lower band": Europe should not theatrically rename the same camp every time share oscillates between `45%` and `55%`; only a real return to equilibrium wipes public memory and re-arms the full upward-beat sequence.
- Speaker selection is deterministic: use the highest-weight non-bloc major court first; if no such named diplomat exists, fall back to the chancery of that court, then to a Talleyrand advisory line in his existing bloc-naming register as the final fallback. No anonymous `system` speaker is allowed on this surface. Per-court register at each band lives in `DIPLOMAT_VOICE_BIBLE.md` (`hegemony_beat_*_{noticed,alarming,crisis}` minimum coverage).
- If a beat includes a counter-play hint, the hint must be (a) capability-aware: only suggest actions that are actually legal in the current shipped slice (`Make Amends` may be named only once B-B7 is live; before that, hints are limited to bloc-shrinking / treaty-lapse actions), AND (b) **causally specific**: name *which* members of the player's bloc account for the largest share-contribution slice, not generic levers. *"Saxony accounts for the decisive non-French slice of your bloc share — releasing it shrinks the share immediately; Europe's passive pressure eases the following turn"* is legible in the v0.1 roster; *"consider releasing a vassal"* reads as random advice. Multi-minor Confederation-of-the-Rhine examples are 13-nation forward-compat illustrations, not v0.1 assumptions. Compute the contributor breakdown by sorting `bloc_members` by their individual `power_score` contribution to the bloc total.

### 7.4 Coalition target and leader selection

The existing `coalition.py` flow handles formation, qualification, leader selection, and dissolution. Hegemony pressure adds two semantic refinements:

- **Coalition target = current hegemon.** When formation fires, the coalition's named target is the nation returned by `_calculate_hegemony_pressure`. In v0.1 this is France for the entire campaign barring extraordinary play.
- **Leader selection biases toward bloc-share-against.** The existing `coalition_leadership_score(nation, world)` (which weights troops, gold, recent damage) gains a bloc-share-against term:

  ```python
  bloc_share_against = bloc_power(nation, world) / european_power
  score += int(bloc_share_against * 50)  # tunable weight
  ```

  This naturally surfaces the largest non-hegemon power as coalition leader — Britain in 1805 once France's bloc passes 35%, switches to Russia post-1807 if Britain's bloc shrinks, etc.

  **France-anchoring caveat:** the current `coalition_leadership_score` reads `france = world.player_nation` for its hostility term. Adding `bloc_share_against` is additive — it does not fix the France-hostility anchor. That anchor is correct for v0.1 (France is the only possible hegemon by starting position) and is tracked as a D2 (Coalition Generalization) item. The B-Hegemony test for leader-score should assert the French-hegemon precondition.

### 7.5 Commitment paradox

**v0.1 behavior:** rename the existing `alliance_paradox` dialogue type to `commitment_paradox`. Keep the same trigger (war declaration that would force the player into both sides of an alliance), the same fallout-preview, the same episode_id continuity. The HARD_STOP type registration of `commitment_paradox` (already in `dialogue_manager.py`) starts being used; the legacy type name becomes the historical alias for save-load back-compat.

**Deferred:** the rivalry-driven ratification paradox (the original §7.5 design — opposition-graph evaluator running at every deep-treaty ratification, multi-conflict `ConflictResolutionPass`) is **not** v0.1 scope. It depends on bargain conflicts to feel important; without bargains, it would only fire on the legacy alliance-cross-war condition the existing flow already handles. Defer to `WAR_BARGAIN_SPEC` slice WB-C, which extends the paradox to read live bargains and rivalry data.

What this phase keeps from the original §7.5:

- one-conflict resolution (the legacy flow is one conflict per push by definition)
- deterministic downgrade fallout preview before the choice (already shipped)
- durable `commitment_paradox_resolved` log + dispatch event (already shipped)

What this phase **does not** ship:

- multi-conflict ratification consolidation
- `opposition_graph` reads
- bargain-attached fallout preview (no bargains to attach)

### 7.6 Hegemony pressure decay

Pressure decays naturally — no separate decay clock. Each turn the engine recomputes bloc shares from current state. If France allies with Bavaria, share jumps and pressure increment grows next turn. If Bavaria defects, share drops and pressure stops accruing. The existing `coalition.py` `_calculate_threat_decay` continues to drain the threat scalar between aggressive events.

This means players can *see and act on* the pressure source: vassalize fewer minor states, release a vassal as a goodwill gesture, accept a separate peace that breaks an alliance. Each of these immediately reduces bloc share next turn, which immediately reduces passive threat accrual. The same-turn threshold beat above is the designed answer to the one-turn scalar lag: Europe should **notice** the shift immediately even if the passive `threat_level` tick lands on turn N+1.

The auto-downgrade rule from earlier drafts (deep alliance reduces "concern intensity") is no longer needed — deep alliances raise bloc share, not lower friction. Friction is the share, not a label on a pair.

### 7.7 Scale architecture note (v2.4: this IS what we ship)

The v2.2 / v2.3 spec described "static seeded concerns now, dynamic evaluation later." v2.4 collapses both into one model: **the dynamic evaluation IS v0.1.** No transitional static layer.

What this buys at scale:

| Element | v0.1 (5 nations) | Full Europe (13-20 nations) | Same engine? |
|---------|------------------|------------------------------|--------------|
| Hegemony detection | bloc shares of 5 majors | bloc shares of 13+ majors | ✓ same calc |
| Coalition target | France (starting position) | Whichever bloc passes threshold | ✓ same calc |
| Coalition leader | Britain (highest non-French power) | Whichever non-bloc major has highest bloc-share-against | ✓ same calc |
| Pressure ladder | 1/3/5/8 by share bucket | same buckets | ✓ same authored constants |
| Bilateral memory | strikes + hard-reject | strikes + hard-reject | ✓ unchanged |
| Make Amends cadence | 200g + 10-turn cooldown per pair | same — repair tour scales naturally | ✓ |
| Preview warning cap | 2 inline | 2 inline | ✓ |
| Voice Bible cast | 5 named diplomats | 13+ named diplomats *or* generic-register fallback for unnamed minors | needs cast expansion |

What the v2.4 engine does not depend on:
- No authored rivalry pairs — engine reads bloc shares
- No per-pair concern intensity lookup — replaced by single hegemony pressure value
- No composite acceptance-formula floor — single negative term per asker

What's flagged for later (unchanged from v2.3):
- Voice Bible cast expansion when nations >5
- Per-target threat scalar generalization in `coalition.py` when non-French hegemon becomes possible
- Witness scope caching at 13+ nations

### 7.8 Relationship to Coalition Formation

Hegemony Pressure and the existing `coalition.py` coalition system are **complementary layers, not redundant mechanics**. They model different political realities.

#### 7.8.1 Two layers, different state

|  | Hegemony Pressure (v2.4) | Coalition (existing in `coalition.py`) |
|---|---|---|
| **What** | Passive political climate | Formal military opposition |
| **State** | Pure per-turn calculation; no stored fields | `world.coalition_members`, leader, war state |
| **Trigger** | `bloc_share >= 33%` (per-turn ladder + beat per §7.3); `bloc_share > 30%` (per-pair acceptance penalty per §9.1 — formula threshold remains 30% so per-pair friction begins one band before continental consensus) | `threat_level >= INSTANT` (80) or `BREWING` + qualifying members |
| **Effect** | (a) Acceptance penalty on cross-bloc proposals; (b) passive contribution to `threat_level` | Members declare war on hegemon, military commitment, separate peace dynamics |
| **Lifecycle** | Continuous — recomputed every turn from current bloc state | Discrete — formation → active war → dissolution |
| **Player surface** | Balance of Europe headline + `hegemony` warning category in proposal preview | Coalition popup, war declaration, war HUD, post-war terms |

#### 7.8.2 Hegemony pressure FEEDS coalition formation

Before v2.4, coalitions formed only from **event-based** threat — battles fought, capitals captured, vassalizations. Pure aggression-driven.

After v2.4, coalitions also form from **passive** threat — France becoming too big is itself enough to assemble a coalition, even without recent French aggression.

Historically this is correct. The 1805 Third Coalition formed *before* any French attack that year — Britain paid Austria £1.5M in subsidies because France's bloc was perceived as too large after Pressburg, not in response to a specific French move. Event-threat-only could not model that; v2.4 can.

#### 7.8.3 Three states a non-bloc nation can be in

- **Neutral observer** — outside hegemon bloc, no hegemony pressure accumulating, not in coalition. (Russia 1803-04.)
- **Alarmed neutral** — outside hegemon bloc, hegemony pressure mounting, `threat_level` rising, coalition not yet formed. (Britain pre-Third Coalition.)
- **Belligerent** — outside hegemon bloc, in formal coalition, committed to military opposition. (Britain post-1803.)

The hegemony engine provides the passive pressure that pushes neutrals from state 1 → state 2 → state 3 through the existing `coalition.py` threshold ladder. The coalition system handles what happens once they reach state 3.

#### 7.8.4 Key playtest implication

If France plays peacefully but builds a `50%+` bloc, the v2.4 engine should still trigger coalition formation through accumulated passive threat alone — **no French aggression needed**. This is the intended design. For it to feel fair, the player must see the continent reacting before the declaration: named-court beats at `33 / 50 / 60`, then proposal-preview warning pressure, then coalition brewing.

**Pacing target (design contract, not optional flavor):**

Baseline assumptions (must hold for the targets below to be testable):

- Starting threat scalar: `0` at the moment the 50%+ share is first reached.
- No competing event-based threat sources (battles, captures, vassalizations) firing during the test window.
- Existing `_calculate_threat_decay` continues to drain the scalar at its current rate.

Targets:

- `33-49%` share should feel **noticed but manageable** — first beat fires, no coalition mobilization yet.
- `50-59%` peaceful France should reach `BREWING` (`threat_level >= 60`) in roughly **12-16 turns if ignored**.
- `60%+` sustained share should feel like an **acute crisis**, with declaration pressure (`threat_level >= 80`) mounting in roughly **another 4-8 turns** unless France shrinks the bloc or repairs relations.

If playtest misses those targets, tune the ladder values (1/3/5/8) and / or the decay rate rather than retuning the gates — gates must remain at 33/50/60/70 for beat alignment. A cold-start, zero-threat run that still takes materially longer than this contract (for example, drifting into the mid-20s turns before `BREWING`) is a tuning miss, not acceptable documentation debt. **B-Hegemony acceptance check:** instrument a deterministic test that runs a peaceful 50%-share scenario for 16 turns and asserts `threat_level >= 60` by turn 16; if it fails, retune values before merging.

---

## 8. Reliability And Betrayal

### 8.1 Split the memory cleanly

Two memories, kept separate:

- **Global reliability:** "France is known to keep or break agreements."
- **Bilateral betrayal memory:** "Austria specifically remembers France betrayed Austria."

### 8.2 Offense categories (already shipped)

Tracked betrayal categories in v0.1:

- breaking treaty voluntarily
- breaking non-aggression with rapid war follow-up
- breaking alliance / defensive alliance

Removed from v0.1 (in `WAR_BARGAIN_SPEC` until that ships):

- explicit reversal of an active war bargain
- timer-based failure for ally-land promises
- suspension-based promise expiry
- passive failure caused only by AI inactivity
- explicit exclusivity-demand offenses
- costless bargain-only cancellation actions

### 8.3 Penalty model (substrate shipped; bargain row deferred)

| Event | Global reliability | Victim strikes | Witness effect |
|------|--------------------|----------------|----------------|
| Break `OPEN_BORDERS` / `PEACE`-level commitment | -4 | +1 | `-2` to each scoped witness |
| Break `NON_AGGRESSION` | -6 | +1 | `-2` to each scoped witness |
| Break `DEFENSIVE_ALLIANCE` / `ALLIANCE` | -10 | +2 | `-4` to each scoped witness |
| Explicitly reverse an active war bargain | (`WAR_BARGAIN_SPEC`) | (`WAR_BARGAIN_SPEC`) | (`WAR_BARGAIN_SPEC`) |

Critical episode-cap rule (already shipped):

- one diplomatic episode may add at most **2 victim-side strikes to any one victim**

Episode definition:

- one diplomatic episode = all diplomatic penalties and strike applications that share the same root-cause `episode_id`
- a player-confirmed diplomatic action creates a fresh root `episode_id`
- `advance_turn()` may process multiple `episode_id`s; the turn itself is **not** one episode
- downstream treaty downgrades, witness fallout, and reliability changes caused by that same root trigger reuse the same `episode_id`
- pending dialogue, decay tracker, or delayed diplomatic consequence that may resolve after save/load serializes its originating `episode_id` lineage until resolution

Implications already wired:

- if France breaks an alliance and the cascade collapses other treaties in the same resolution step, relation and reliability penalties may stack
- multiple injured parties in the same episode may each gain strikes
- no single victim's strike gain may exceed +2 from that single episode

Global reliability rule:

- all global reliability deltas apply to the acting nation's shared `diplomatic_reliability[actor]` value
- witness scoping changes relation fallout only; it does not create witness-specific reliability variants

### 8.4 Witness scoping (substrate shipped; region_observer deferred)

Witness penalties apply only to directly interested observers:

- nations with `DEFENSIVE_ALLIANCE` or `ALLIANCE` with the victim
- nations currently at war with the betrayer (war-state proxy for the `rival` scope). v2.4 deleted the `nation_concerns` data structure; no future seed-switch is planned. When a richer rivalry signal becomes available (e.g. unremoved §8.8.4 grievance flags graduating into durable witness tags), it is a drop-in replacement under the same `scope_reason` precedence.
- nations with a live bargain that shares the same named enemy or claim region (deferred until `WAR_BARGAIN_SPEC` lands)

Everyone else gets zero witness effect. Witnesses do **not** receive victim-grade strikes in v0.1.

Witness scope tagging (shipped):

- emitted witness payloads carry one deterministic `scope_reason`
- precedence: `ally` > `rival` > `shared_enemy` > `region_observer`
- a breach may have multiple witness nations, but each witness gets exactly one resolved `scope_reason`
- witness payloads carry relation fallout only; surfaced `reliability_delta` on witness events is always `0`

Exclusivity-demand rule:

- do **not** add exclusivity-demand betrayal logic in v0.1
- if explicit exclusivity diplomacy ships later, it must create an explicit tracked commitment before it can create a betrayal offense

### 8.5 Faithful-play rewards

The system must reward sustained committed play, not only punish betrayal.

For v0.1:

- visible side-taking should feel legible through previews, warnings, and treaty outcomes rather than a bespoke hidden relation token
- bargain fulfillment reward (`+4` reliability per (promiser, beneficiary) per 10 turns + `+6` relation) lives in `WAR_BARGAIN_SPEC.md`
- clear preview / ledger surfacing so loyalty feels intentional rather than invisible

Do **not** add a dedicated `trusted_partner` state in v0.1.

### 8.6 Redemption (substrate shipped; reliability tick CANCELLED in v2.4)

**Reliability tick — cancelled.** v2.3 proposed a "+3 diplomatic_reliability per 5 honored treaty turns" global tick (requires `OPEN_BORDERS` or above; `PEACE` alone does not qualify). **v2.4 cancelled this slice (B-B6).** Implementers must NOT wire it — it is not a phase deliverable. Rationale: the tick fired invisibly to players, drifting reliability upward with no surfaced event. The v0.1 recovery paths are Make Amends (§8.6.1, `+2` reliability per use, 10-turn per-pair cooldown, France-only) and bargain fulfillment (deferred to `WAR_BARGAIN_SPEC.md`). See §14 R7 for the cancellation rationale and the conditions under which the tick can be re-opened (make it surface-visible first).

**Bilateral strike decay — shipped and active.** Passive strike-removal continues to operate:

- after honorable turns with a nation and no new offense, remove 1 bilateral strike using severity-scaled decay:
  - 6 turns: `OPEN_BORDERS` / `PEACE`-level break
  - 8 turns: `NON_AGGRESSION` break
  - 10 turns: `DEFENSIVE_ALLIANCE` / `ALLIANCE` break

Guardrails (shipped):

- passive decay clears at most 1 strike per nation per turn
- each strike decays on its own clock using its recorded `turn` + severity-scaled interval; the per-pair dict does **not** store a single shared decay clock
- strike age continues to mature during `WAR` and `ARMISTICE`
- actual strike removal requires an active non-`WAR` treaty (`PEACE` or above) with that nation
- once a non-war treaty is restored, any matured strikes may decay at the normal per-turn limit until caught up
- vassal note: `_NON_WAR_TREATY_STATES` includes `VASSAL`, so a vassal's strikes can decay while vassalized; if the vassal is released or assimilated, strikes follow the nation, not the vassal relationship

### 8.6.1 Active redemption: Make Amends (this phase ships)

Passive decay is the floor. v0.1 also ships one explicit player verb so repaired relationships can be a deliberate political act, not a waiting game.

**Action:** `make amends with {nation}` (internal: `make_amends`)

**Preconditions:**

- France has at least 1 active victim-side strike against the target
- France and target share a non-`WAR` treaty state (`PEACE` or above)
- Cooldown not active: `reparations_cooldown[diplo_key]` ≤ `current_turn`
- France has ≥ 200g gold and ≥ 1 DP

**Effects on success:**

- Consume 200g and 1 DP
- Remove 1 active strike from France's victim-side strikes with target (same selection rule as passive decay: oldest strike whose severity-scaled decay clock has matured, else the lowest-severity active strike)
- `diplomatic_reliability["France"]` += 2 (France demonstrates willingness to repair)
- `nation_relation` France → target += 5 (acknowledgment / goodwill)
- `reparations_cooldown[diplo_key]` = `current_turn + 10` (one Make Amends per pair per 10 turns)
- Emit `amends_offered` campaign-log / notice / ledger event with `episode_id`, the cleared strike's original episode lineage, deterministic deltas, and the named diplomat of the target nation
- Success result always includes one line of named-diplomat acknowledgment in the target court's register. Mechanical success is not gated on branching, but the apology may not land as numbers-only text.

**Refusal conditions (non-actionable, Talleyrand-voiced advisory):**

- no active strikes: *"There is nothing to repair with {nation}, Sire. They hold no living grievance against France."*
- cooldown active: *"We offered amends to {nation} only {turns_since} turns ago. Too soon would read as petition, not as state."*
- at `WAR` or `ARMISTICE`: *"Amends before peace read as ransom, Sire. Restore the treaty first."*
- insufficient resources: normal resource-shortfall warning surfaced through the existing DP/gold refusal path

**Design intent:**

- **Costly enough** that France cannot cheap-clear a whole stack of strikes
- **Cadence-limited** so each gesture is a real political moment, not a per-turn click
- **Feels like a deliberate act** — Talleyrand delivers the preview line in his register; the target's named diplomat answers in the result text
- **Reads as an apology loop** — gesture → named acknowledgment → durable record, not a resource purchase
- **Complements, not replaces, passive decay** — at full use, Make Amends clears 1 strike per 10 turns per pair; passive decay still clears its own stream

**Non-goals for v0.1:**

- no manpower / territory tributes (gold + DP only)
- no "reparations package" clearing multiple strikes at once
- no self-directed use (France cannot Make Amends with itself)
- no use from any nation **other than** France (keeps authoring surface narrow; enemy AI uses passive decay only in v0.1)
- no relationship recovery with a nation France has no strikes against — that is relation giftgiving, not commitments work

#### 8.6.1a Make Amends (grievance variant — ships with B-B4)

§8.8.4 specifies that defensive-refusal grievance flags can only be removed via Make Amends. Left unspecified in §8.6.1: the standard precondition requires "≥ 1 active victim-side strike," but grievance flags persist *after* their originating `+2` strike stack decays. Without an explicit variant, the mechanism has no legal entry point once strikes clear.

**Preconditions (grievance variant — overrides §8.6.1 "≥ 1 strike" rule):**

- France has at least 1 active grievance flag against the target (`grievance_type: "defensive_call_refused"` on the `betrayal_history` pair entry)
- France and target share a non-`WAR` treaty state (`PEACE` or above)
- Cooldown not active: `reparations_cooldown[diplo_key]` ≤ `current_turn` (shared with standard Make Amends — only one Make Amends of any variant per pair per 10 turns)
- France has ≥ 400g gold and ≥ 2 DP (double the standard cost, matching §8.8.4's authored candidate)
- **Standalone strikes coexisting with grievance flag:** standard Make Amends and grievance-variant Make Amends are distinct invocations — removing a grievance flag does NOT clear standalone strikes, and clearing a standalone strike does NOT clear a grievance flag. Each requires its own call and its own cooldown use (sequenced across turns because the cooldown is shared).

**Action disambiguation:** when both standalone strikes AND one or more grievance flags exist against the same target, the parser surfaces two distinct `make amends with {nation}` verbs:

- `make amends with {nation}` (default: targets oldest strike, standard cost)
- `make amends with {nation} for the abandoned alliance` (grievance variant: targets oldest grievance, `400g + 2 DP`)

Parser fuzzy-match defaults to the standard variant; the grievance-variant phrase is discoverable through the Diplomatic Ledger grievance row (clicking the row offers the grievance-variant verb).

**Effects on grievance-variant success:**

- Consume 400g and 2 DP
- Remove oldest grievance flag from the pair entry (FIFO by grievance-creation turn)
- `diplomatic_reliability["France"]` += 3 (grievance repair is a larger political gesture than a single strike)
- `nation_relation` France → target += 8 (acknowledgment weighted to grievance severity)
- `reparations_cooldown[diplo_key]` = `current_turn + 10`
- Emit `amends_offered` campaign-log / notice / ledger event with `grievance_variant: True` flag and the cleared grievance's `origin_episode_id`

**Refusal conditions:** same four conditions as §8.6.1 (no target grievance → Talleyrand advisory "There is no abandoned alliance to repair, Sire — {nation} holds no living grievance of that kind against France"; cooldown / WAR state / insufficient resources via existing paths).

### 8.7 Hard-reject posture

Repeated betrayal must eventually change AI posture.

Rule:

- 3 active bilateral strikes from France toward Nation X causes AI hard resistance to deep treaties with X.

Rules:

- witness suspicion alone never triggers this threshold
- survival exception is narrow: the 3-strike block may downgrade from absolute reject to heavy soft-resistance only when France and Nation X share a current enemy, France is not at war with X, the proposal is immediate military cooperation against that same enemy, and France did not betray X in the same episode
- when that exception opens, AI applies a major posture tax (treat as at least `-20` before normal formula evaluation); the exception removes only the absolute lock, not the political cost
- one episode cannot add more than 2 strikes to the same victim (per §8.3)
- proposal preview must warn when the contemplated action would create the third active strike against a nation (`hard_reject` category warning — already wired)
- emit `hard_reject_posture_triggered` on first crossing from 2 to 3 active strikes and `hard_reject_posture_cleared` on first return from 3+ to 2 or fewer (already wired); both events persist in dispatch and campaign-log metadata for that posture span

### 8.8 Call-to-arms refusal episodes (DG-4 amendment — April 17, 2026)

**Source of truth:** the design for this section is the DG-4 Amendment in `docs/SCALE_READINESS_PLAN.md`. This section specifies what the Memory and Pressure substrate must add to implement that amendment. Any conflict between the two documents resolves to the amendment text; update both if the amendment changes.

**Why this lives here:** the amendment introduces three new durable episode types that ride on the existing betrayal-memory substrate (`betrayal_history`, `episode_id` threading, witness scoping, acceptance formula). Without calling it out in this spec, the substrate owners have no visibility into the new obligations.

**Structural note (graduate to top-level when B-B4 ships):** §8.8 currently nests through §8.8.14 (fifteen sub-sections). Past §8.8.9 it reads as an adjunct spec inside a subsection — enough weight to stand alone. When B-B4 lands, graduate this section to its own top-level `§9. Call-to-Arms Episodes` and renumber the downstream sections (current §9 → §10, current §10 → §11, etc.). The renumber is a flat mechanical edit with search-and-replace on cross-references; it is deferred to the B-B4 merge to avoid churn on the still-in-flight `Memory and Pressure v2.4.x` revisions.

#### 8.8.1 Three new episode types

Added to the category tie-break order (currently §11 stable order: `paradox`, `hard_reject`, `bargain`, `betrayal`, `hegemony`, `peace_conflict`) as members of the `betrayal` family:

- `call_to_arms_refused_offensive`
- `call_to_arms_refused_defensive`
- `call_to_arms_honored_costly` (positive episode — §8.5 faithful-play; see §8.8.5)

All three share the payload shape defined in the amendment (`episode_type`, `breaker` or `honorer`, `victim`, `witnesses`, `severity`, `call_context`, `episode_id`). Episode continuity rules from §8.3 apply unchanged — a refusal that directly downgrades an existing treaty reuses the same `episode_id`.

#### 8.8.2 Severity table additions (extends §8.3)

| Event | Global reliability | Victim strikes | Witness effect |
|------|--------------------|----------------|----------------|
| `call_to_arms_refused_offensive` | `-6` | `+1` | `-2` to each scoped witness |
| `call_to_arms_refused_defensive` | `-10` | **`+2` victim-grade, plus permanent grievance flag (see §8.8.4)** | **`-3` to each scoped witness** (wider scope — see §8.8.3) |
| `call_to_arms_honored_costly` | **`+5`** | `0` (no strike; positive episode does not touch strike table) | **`+2`** to each scoped witness |

Defensive refusal severity intentionally exceeds `ALLIANCE` break (`-10 / +2 / -4`) in *reach* (wider witness scope, §8.8.3) rather than in raw reliability drop. The reliability number is the same; what makes defensive refusal bite harder than alliance-break is who hears about it.

The `defensive_refusal_severity_multiplier` (authored in `cascade_profile`, default `1.75`) applies on top of the base `-10` victim side and `-3` witness side. Resolved severity = base × multiplier × `honor_bias`.

#### 8.8.3 Wider witness scope for defensive refusals (extends §8.4)

Existing §8.4 scopes witnesses to: `ally` (`DEFENSIVE_ALLIANCE` / `ALLIANCE` with victim), `rival` (war-state proxy — active war with the breaker), `shared_enemy`, `region_observer` (deferred).

For `call_to_arms_refused_defensive` and `call_to_arms_honored_costly`, witness scope expands:

- **All nations holding any active treaty with the refuser/honorer**, not just with the victim
- This is the substrate answer to "defensive refusals change how everyone scores your reliability, not just the abandoned party's allies"
- New `scope_reason`: `treaty_partner_of_breaker` (or `..._of_honorer` for the positive case)
- Precedence insertion: `ally` > `rival` > **`treaty_partner_of_breaker`** > `shared_enemy` > `region_observer`
- A witness that qualifies under multiple scopes still resolves to one `scope_reason` per the single-reason rule

Scale note: at 13 nations this widens witness lists from ~2-4 nations to ~6-9. Already flagged in §7.7 "Witness scope loop | O(active_nations) per witness" — revisit caching when this lands.

#### 8.8.4 Victim-grade permanent grievance

Defensive-refusal victims take the normal `+2` victim-side strike and also gain a **permanent grievance flag** (`grievance_type: "defensive_call_refused"`) on the pair. Properties:

- Does **not** decay under §8.6 passive decay rules (the +2 strike does decay normally; the flag does not)
- Removable only via **Make Amends (grievance variant)** — see §8.6.1a for the complete precondition and effect contract. Cost is `400g + 2 DP` (double the standard strike variant); one explicit political act per grievance, not a waiting game. Standard Make Amends (§8.6.1) does NOT clear grievance flags even after all originating strikes have decayed — the two variants are distinct invocations.
- Stacking cap: grievance flags saturate at 3 active flags per asker-target pair for acceptance-formula input (§8.8.9, §9.3). The *underlying data* still records all flags (so the ledger shows "4+ grievances"), but `grievance_modifier` does not grow beyond -90 per pair.
- When a richer post-v0.1 rivalry signal is added (candidate: durable witness tags on `betrayal_history` pair entries, or derived rivalry scores read from bloc geometry + grievance age), unremoved grievance flags are the intended graduation source — each flag becomes one entry in that new signal
- Surfaces in Diplomatic Ledger with a distinct row: *"Austria remembers being abandoned by Russia — 14 turns ago"*. Row is clickable and offers the grievance-variant Make Amends verb directly.

Without this, a well-timed Make Amends tour could scrub defensive refusal entirely. The grievance flag is what makes defensive refusal feel historically durable.

#### 8.8.5 `call_to_arms_honored_costly` as faithful-play reward

Extends §8.5 with a specific positive-episode trigger. First concrete faithful-play event in the substrate. Behavior:

- Fires when the honorer enters a defensive ally's war despite the impossibility predicate firing at call moment, OR enters a defensive call where the aggressor coalition's power-score ratio exceeded an authored "costly" threshold (lower than impossibility, e.g. 1.8×)
- Positive payload routed through the same substrate seams as `_refused_defensive`, with opposite sign on reliability, relation, and witness effect
- Victim (the rescued principal) gains a loyalty bond: `nation_relation` +10, persistent for 30 turns, stackable up to authored cap
- Emits `call_to_arms_honored_costly` CRITICAL notice through C3-lite presentation (see §8.8.10)

Design intent: the amendment cannot ship only the punishment side. If honoring an impossible call is free but refusing is costly, players/AI learn "always honor" — boring. If both cost and reward exist, the decision carries weight.

#### 8.8.6 Habitual-refusal oathbreaker posture

New posture in the substrate, parallel in shape to §8.7 `hard_reject_posture` but keyed on refusal history, not strike count.

Rule:

- N `call_to_arms_refused_defensive` episodes in which the acting nation is `breaker`, within the last M turns (authored — candidate `N=2`, `M=15`), promotes the nation into `oathbreaker_posture`
- While in `oathbreaker_posture`: the nation's AI auto-rejects any incoming `ALLIANCE` or `DEFENSIVE_ALLIANCE` proposal targeting it for the authored cooldown window (`oathbreaker_posture.auto_reject_ally_proposals_turns`, candidate 10 turns)
- Proposals to or from France must preview this posture using the same `hard_reject` category warning already wired (so the player is not blindsided by auto-rejection)
- Emit `oathbreaker_posture_triggered` and `oathbreaker_posture_cleared` on transitions, analogous to hard-reject events, persisted in dispatch and campaign-log metadata

Clearance: the posture decays when a `call_to_arms_honored_costly` episode lands while the posture is active, or when `M` turns elapse without a new defensive refusal. Both paths are authored so later balance passes can make oathbreaker status harder or easier to escape.

#### 8.8.7 Anti-renewal cooldown between the pair

Orthogonal to oathbreaker posture. Applies specifically to the refuser-victim pair:

- A `call_to_arms_refused_defensive` episode blocks new `ALLIANCE` / `DEFENSIVE_ALLIANCE` ratification **between that specific pair** for an authored window (candidate 15 turns)
- Blocking is mechanical, not advisory — the proposal flow returns a dedicated refusal reason (`anti_renewal_active`) and the UI surfaces the remaining turns
- Peace and non-aggression remain available during the window; only deep defensive ties are blocked
- Once the window elapses, a new alliance is possible but must be actively ratified through normal diplomatic flow; the prior alliance does not auto-restore

#### 8.8.7a Existing-alliance consequence of defensive refusal

On `call_to_arms_refused_defensive`, the existing `ALLIANCE` or `DEFENSIVE_ALLIANCE` treaty between the refuser and the abandoned victim is **terminated** at the refusal moment, downgrading to `PEACE`. Rationale: refusing to honor the alliance IS the termination — even without a formal repudiation instrument, no court treats the treaty as live after the call is spurned. Historical pattern matches: Prussia 1795 (Peace of Basel) effectively ended its First Coalition obligation by withdrawing rather than any explicit denunciation; Russia's pre-Tilsit 1807 realignment similarly dissolved prior bindings through behavior first, instrument later.

**Same-turn mechanical effects (in order):**

1. Treaty state `ALLIANCE` or `DEFENSIVE_ALLIANCE` between `breaker` and `victim` is set to `PEACE` in the same `advance_turn` step that emits the refusal episode. Emit `diplomatic_treaty_broken` with `end_reason_family = "defensive_refusal_termination"` (new family, parallel to `french_breach` but distinct — the refusal episode itself is the fault attribution).
2. Bloc membership recomputes: `victim` leaves `breaker`'s bloc immediately. If `victim` was `breaker`'s only deep-treaty partner and `breaker` has no vassals, `breaker`'s bloc shrinks to `{breaker}`.
3. `get_bloc_members` cache (per §10.5) is invalidated on the treaty-state change — the formula reads the updated bloc on any subsequent same-turn proposal check.
4. Hegemony pressure recomputes next turn from the updated bloc state; if the share fell below 33%, the pressure accrual stops (per §7.3 ladder floor).
5. `anti_renewal_cooldown` (§8.8.7) then gates any new `ALLIANCE` / `DEFENSIVE_ALLIANCE` ratification between the pair for the authored window.

**Why termination (not downgrade to NON_AGGRESSION):** downgrading to NON_AGGRESSION would preserve a binding signal where none politically exists, and would leave the `anti_renewal_cooldown` applying to a tier the pair no longer holds. `PEACE` is the default non-belligerent state — free to be re-raised to NON_AGGRESSION during the cooldown without re-triggering the anti-renewal block (which targets ALLIANCE / DEFENSIVE_ALLIANCE only).

**Cascade interaction:** the termination emits through the normal treaty-break cascade path (§8.3 witness scoping, normal break-category strike assignment) but is NOT double-counted with the defensive-refusal episode's own strike / grievance assignment. The refusal episode is the root `episode_id`; the termination event carries the same episode_id and adds `no strikes` / `no grievance` on its own (all fault attribution lives on the refusal event).

This resolves audit A9: the bloc-share semantics of defensive refusal are deterministic, the cooldown applies to a meaningful state transition, and the player sees one durable political moment (the refusal + termination as a single coherent episode) rather than an ambiguous half-alive alliance.

#### 8.8.8 Coalition-formation hook

Refusal accumulation also feeds the coalition-threat scalar maintained in `COALITION_SPEC.md`:

- Each active `call_to_arms_refused_defensive` episode contributes a standing `+threat` signal to any nation holding an active treaty with the refuser's *victim* at refusal moment
- Signal decays with the episode's severity decay
- This is the mechanical representation of "a nation that abandons allies is seen as a bigger threat by other small states who might be next"

Implementation: the coalition-threat scalar already reads from betrayal events; this adds a new event family to its input set. No new system.

#### 8.8.9 Acceptance formula input (extends §9.3)

The bilateral betrayal modifier in §9.3 currently reads victim-side strike count. Amendment adds a second term:

- `grievance_modifier` — a nation with a live grievance flag against the asker applies an authored flat penalty to **any** proposal from the asker (not only ally proposals), on top of the existing strike-derived modifier
- Candidate value: `-30` to acceptance score per active grievance (tunable)
- Stacks with normal strike modifier; does not double-count the strike itself

This is how the abandoned nation's memory shows up in everyday diplomacy — not just "don't trust them as an ally" but "don't trust them on trade, passage, peace terms, anything."

#### 8.8.10 Presentation surface (C3-lite event families)

Per `COMMITMENTS_PRESENTATION_SPEC.md`, three new speaker="envoy" / speaker="foreign_office" event families are needed for C3-lite:

- `call_to_arms_refused_offensive`
- `call_to_arms_refused_defensive`
- `call_to_arms_honored_costly`

Each needs authored CRITICAL notice copy in `diplomatic_templates.py` (no elevated fourth-tier rail card in C3-lite v0.5.1), resolved through the Voice Bible named cast (anonymous voice is disallowed per Voice Bible). Default voices:

- Victim's diplomat voices the CRITICAL notice when the victim has a named diplomat
- French Foreign Office (Talleyrand) leads when France is breaker or honorer
- Third-party witness notices are one-liners rendered in the notification bar

Scenario-configured `cascade_profile.*` keys that govern these event families are authored in `SCALE_READINESS_PLAN.md` §DG-4 Amendment. Update the schema note there and this presentation-surface contract together.

#### 8.8.11 Audit trail (`war_entry_ledger`)

Extends `campaign_log.py`. On war declaration, emit one `war_entry_ledger` event with structured per-nation records:

```json
{
  "episode_id": "...",
  "war_id": "...",
  "entries": [
    {"nation": "Russia", "path": "honored", "side": "defender", "reason": "ALLIANCE with Austria"},
    {"nation": "Prussia", "path": "refused_discretionary", "side": "defender", "reason": "DEFENSIVE_ALLIANCE with Austria", "refusal_episode_id": "..."},
    {"nation": "Saxony", "path": "impossible_auto_declined", "side": "defender", "reason": "aggressor_power_ratio=3.1"}
  ]
}
```

Enables later Diplomatic Ledger queries ("Russia has refused 2 defensive calls in the last 10 turns") without scanning the full episode history. `path` values are the locked strings listed in the amendment.

#### 8.8.12 Scenario authoring interaction (`honor_bias`)

Per-nation scalar authored in scenario config, default `1.0`. Reads:

- Multiplies resolved `severity` on all three new episode types (including the positive `honored_costly`)
- Multiplies strike decay interval in §8.6 for strikes created from these episodes (higher `honor_bias` → slower decay, consistent with "rigid honor culture remembers longer")

`honor_bias` is authored scenario data, colocated with `power_tier`. Like `power_tier` it is stable for a campaign and never mutated at runtime.

#### 8.8.13 Implementation plan call-outs

Adds work to `RELIABILITY_IMPLEMENTATION_PLAN.md`. New slice `B-B4: call-to-arms episodes` covering:

- Episode emission at the three decision seams (attacker-side refuse, defender-side refuse, defender-side honor-costly)
- `oathbreaker_posture` state field + transitions
- `anti_renewal_cooldown` per-pair field
- Grievance flag on `betrayal_history` pair entries
- `war_entry_ledger` campaign-log event
- New acceptance formula term (`grievance_modifier`)
- Target test count: ~25-29 new (parallel to paradox rename slice)

Slice C (C3-lite) grows by three event families. Slice deferral is acceptable if scale work is urgent — substrate-only ship of 8.8.1–8.8.9 (no presentation, no C3-lite copy) is viable as an interim state, provided presentation lands within the same phase to avoid "mechanic fires silently" UX.

#### 8.8.14 Deferred for later slices

Explicitly not in the amendment's scope, flagged here so later work has a handle:

- Sequential inter-ally signaling (ally X seeing ally Y refuse first) — v2 of the amendment at earliest
- Vassal refusal path (vassals still use rebellion path, not refusal)
- Per-episode severity adjustment by *defender's* `power_tier` (currently only aggressor's tier feeds severity)
- Jealousy v3.1 signal integration (hook named, not built)

---

## 9. Acceptance Formula Hooks

v2.4 collapses the four-modifier composite into two core terms. The hegemony engine (§7) drives the political-pressure side; bilateral betrayal memory drives the trust side. With only those two terms live, no composite floor is needed. Once DG-4's `grievance_modifier` joins the formula, §9.3 reintroduces a conditional `-60` floor.

### 9.1 Hegemony target modifier (this phase ships — replaces direct_concern_mod and concern_conflict_mod)

When a nation receives a proposal from an asker who is part of the current hegemon's bloc, friction applies:

```python
def hegemony_target_mod(asker: str, proposal_target: str, world) -> int:
    """Single negative term — replaces direct_concern_mod + concern_conflict_mod."""
    pressure = _calculate_hegemony_pressure(world)
    if not pressure:
        return 0  # no hegemon — diplomacy is open
    hegemon = next(iter(pressure))
    asker_bloc = world.get_bloc_members(hegemon)
    if asker not in asker_bloc:
        return 0  # asker is not in hegemon bloc
    if proposal_target in asker_bloc:
        return 0  # intra-bloc proposals are unrestricted
    share = bloc_power(hegemon, world) / sum(power_score(n, world) for n in world.get_active_nations())
    # Linear scaling: 0 at 30% (integer truncation), -18 at 60% (exactly),
    # clamped at -20 from ~63.34%+ onward. The "-2 at 30%" description in
    # earlier drafts was off by one integer bucket; integer truncation of
    # int((0.30 - 0.30) * 60) is 0, not -2.
    raw = int((share - 0.30) * 60)
    return max(-20, -raw)
```

Effect:

- Returns 0 when no hegemon exists (bloc share < 30%).
- Returns 0 when asker is outside the hegemon bloc — non-bloc nations don't carry the hegemony tax.
- Returns 0 for intra-bloc proposals (France ↔ Bavaria when both are in French bloc).
- Returns -1 to -20 negative on cross-bloc proposals from a hegemon-bloc nation once share rises above the 30% boundary, scaled by share.

This single term replaces:
- The 3-tier `direct_concern_mod` table (no per-pair lookup needed)
- The 4-tier `concern_conflict_mod` ladder (alignment with hegemon IS the conflict)

Captures the same player feel: France-Britain alliance is structurally hard once France is the hegemon, easier when France's bloc shrinks. France-Austria alliance is free when France's bloc is small, costly when France is dominant.

### 9.2 Bilateral betrayal modifier (this phase ships — simplified from v2.3)

```python
from backend.game_logic.diplomacy import _get_active_betrayal_strike_count


def bilateral_betrayal_mod(asker: str, target: str, world) -> int:
    """One penalty per active victim-side strike. Hard-reject at 3 still gates the door.

    `_get_active_betrayal_strike_count(world, actor, victim)` is the current module
    helper in `diplomacy.py`. Here the asker is the perpetrator (actor) and the target
    is the victim — i.e. "how many strikes does target still hold against asker".
    """
    strike_count = _get_active_betrayal_strike_count(world, asker, target)
    return -6 * strike_count  # 3-strike hard-reject blocks most proposals; §8.7 survival-exception path with 4+ strikes computes -24+ (per-strike penalty is uncapped by design).
```

Effect:

- `-6 per active victim-side strike` flat. No stacking cap is needed because the 3-strike hard-reject (§8.7, already shipped) blocks most proposals from reaching this calculation.
- Below 3 strikes: graded penalty (-6, -12) on every proposal from the breach-actor.
- At 3 strikes: hard-reject posture engages and most proposals are blocked outright.
- Above 3 strikes: reachable only via the §8.7 survival-exception path (shared-enemy, immediate military cooperation, no same-episode betrayal). A 4-strike nation processing a survival-exception proposal computes `-24`; a 5-strike nation computes `-30`. The per-strike penalty is intentionally uncapped — in practice the episode-cap (2 per episode, §8.3) plus hard-reject blocking keeps counts at 3 for almost all pairs, and 4+ is a multi-episode multi-victim scenario (Austria 1805-1809-1813 pattern).
- Above 3 strikes: not reachable in normal play (cap at 2 per episode + hard-reject blocking).

This replaces the v2.3 `-8 per strike, cap -24` formulation. The simpler `-6` flat is easier to reason about, and the hard-reject does the heavy lifting that the cap previously did.

### 9.3 Composite floor (conditional on DG-4 grievance term)

**Pre-DG-4 (B-Hegemony + B-B1-lite alone — no `grievance_modifier` active in code):**

v2.4 removes the v2.3 `political_commitment_mod = max(-40, raw)` aggregation. With only two terms (`hegemony_target_mod` capped at `-20` and `bilateral_betrayal_mod` blocked above `-18` by the 3-strike hard-reject door-shut), no composite floor is needed. The terms surface independently in debug output and `warnings[]` so player legibility is preserved.

**With DG-4 (§8.8.9 `grievance_modifier` in code — B-B4 shipped):**

A composite floor of `-60` applies when the grievance term is live. Rationale: §8.8.9 authors `grievance_modifier = -30 per active grievance` and grievances persist after their originating `+2` strikes decay (§8.8.4). Without a floor, three grievances alone reach `-90`; compounded with `hegemony_target_mod (-20)` and `bilateral_betrayal_mod (-18)` the raw political subtotal reaches `-128`. With `reliability_modifier` also at its `-6` floor (§9.4), the full worst-case acceptance swing is `-134`. Hard-reject blocks most proposals before they hit this calculation, but the §8.7 survival-exception path lets a same-actor shared-enemy military-cooperation proposal through — with no floor, that path computes an unbounded negative score that makes the exception path decorative rather than playable.

**Grievance stacking cap (per-pair):** `grievance_modifier` saturates at 3 active grievances per asker-target pair. Additional grievances beyond the third do not contribute further. Rationale: history never made a sixth betrayal score worse than the third — the political signal saturates well before the stack grows unbounded. With the cap, `grievance_modifier ∈ [-90, 0]` and the composite political worst case is `-20 + -18 + -90 = -128` raw, clamped to `-60` by the floor. The grievance flag still surfaces in the ledger even above the stacking cap so the player sees "3+ grievances" distinctly.

**Floor exposure in debug / warnings:** when the composite floor clamps, the `components` dict retains the raw term values for legibility (so the player can see "hegemony -20, betrayal -18, grievance -90, composite floor applied at -60"); the floor appears as a synthetic `composite_floor` row rather than masking the originating terms.

**Plan ordering (cross-slice constraint):** `RELIABILITY_IMPLEMENTATION_PLAN.md` must ship B-B4 (DG-4 grievance_modifier) together with or immediately after B-B1-lite's no-floor collapse lands. Under no circumstance may B-B1-lite's no-floor collapse land in code while B-B4's `grievance_modifier` is already live — see plan Execution Order "Merge ordering" paragraph.

### 9.4 Reliability modifier (already shipped — narrowed in this phase)

Tighten the existing `reliability_modifier` to the `RELIABILITY_COMMITMENTS_SPEC` baseline:

- `clamp(diplomatic_reliability[asker] // 10, -6, +6)` (current code is `// 5` capped ±10 — legacy R34)
- Narrowing keeps reliability a light input so bilateral memory dominates

This is unchanged from v2.3 §B1 spec.

When `WAR_BARGAIN_SPEC` ships, `bargain_value_mod` joins as a positive contribution; no composite floor will be needed because the additive terms remain bounded.

### 9.5 Gameplay scaling — France's alliance-building capacity

Added in v2.4 to prevent "does this stop France from allying anyone?" misreadings. The engine scales pressure with bloc share rather than imposing a binary gate.

Illustrative scaling at v0.1 scale (5 nations, 19 regions, `power_tier` weights `major=3 / secondary=2 / minor=1`). Exact values depend on which regions the hypothetical allies control; table uses representative cases:

| France's bloc | Approx. bloc share | `hegemony_target_mod` on cross-bloc proposals | Player experience |
|---|---|---|---|
| France alone | ~22% | `0` | No friction — alliances open |
| France + 1 minor (Bavaria) | ~28% | `0` (under threshold) | No friction |
| France + 2 minors | ~33-35% | `-1 to -3` | Mild friction; new alliances want a sweetener |
| France + 1 major (Austria) | ~40% | `-6` | Harder; real diplomatic investment needed |
| France + 1 major + 1 minor | ~45% | `-9` | Hard but possible with surplus DP / gold |
| France + 2 majors | ~55% | `-15` | Structurally rare; passive coalition threat becomes a medium-term crisis if ignored |
| France + 3+ majors | ~65%+ | `-20` | Acute continental alarm; holding the bloc together should provoke coordinated response within several turns, not invisibly or instantly |

Values in the "mod" column derive from `hegemony_target_mod = max(-20, -int((share - 0.30) * 60))`; the 33-35% band crosses the -1 / -2 / -3 integer boundary depending on exact region allocation.

**Two escape valves keep the engine from stopping France cold:**

1. **Bandwagoning still works.** A non-bloc nation proposing TO France gets `hegemony_target_mod = 0` — the penalty fires only when the *asker* is part of the hegemon bloc. Saxony asking to join France's bloc is unrestricted regardless of France's share. This matches Napoleonic history (Bavaria, Württemberg, Saxony all bandwagoned to Napoleon pre-1812).
2. **Intra-bloc proposals are free.** France proposing to Bavaria (already in bloc) gets `0` penalty regardless of overall share. Deepening existing alliances is unrestricted.

For the first escape valve to be real, AI must actually generate bandwagon proposals. This is a canonical behavior requirement in §10.1, not a speculative polish item.

What the engine makes hard is **broad new recruitment** — France-as-hegemon trying to flip Austria, Prussia, or Britain into its bloc outright. Historically those same flips required marriage alliances (Marie Louise 1810), post-war coercion (Tilsit 1807), or marshal-tier diplomacy. The engine surfaces the same structural difficulty numerically.

**Playtest gates** (tune the `1/3/5/8` ladder values in §7.3 if these fail; the `33 / 50 / 60 / 70` ladder gates must remain locked to the beat thresholds, and the §9.1 formula `30%` floor is intentionally one band below to surface per-pair friction first):

- France SHOULD be able to maintain 2 minor allies (Bavaria + Saxony) without triggering coalition formation
- France SHOULD be able to add 1 major ally (Austria) with real diplomatic effort but without immediate coalition formation
- France SHOULD NOT be able to hold 3+ major allies simultaneously without the continent hardening visibly into blocs over the following turns
- The player SHOULD hear named-court alarm beats at `33 / 50 / 60` before coalition declaration ever arrives

---

## 10. AI Behavior

### 10.1 Proposal generation

AI uses hegemony pressure + bilateral memory to shape branches:

- non-hegemon-bloc nations refuse deep treaties from hegemon-bloc askers (per §9.1)
- nations with active strikes resist treaties from the breach-actor (per §9.2 + §8.7 hard-reject posture)
- non-bloc **minor and exposed secondary powers may bandwagon TO the hegemon** once bloc share reaches the "alarming" band (`~45%+` in representative play), provided relations are not hostile and the nation is not already bound into a rival deep bloc
- (bargain offers move to `WAR_BARGAIN_SPEC.md`)

Minimal AI decision-reason contract (already shipped in subset; this phase tightens):

- every AI-authored offer, refusal, hard block, or counterparty reversal emits one deterministic `decision_reason`
- v0.1 enum: **`hegemony_pressure`** (replaces v2.3 `concern_pressure`), `shared_enemy_survival`, `distrust_promiser`, `war_overload`, `route_blocked`, `coalition_conflict`, `counterparty_reversal`, **`unknown_baseline`** (added in this phase to replace the current `rival_pressure` catch-all when no actual pressure is computed)
- bargain-specific reasons (`claim_trade`, `claim_obsolete`) live in `WAR_BARGAIN_SPEC.md`
- `decision_reason` is mechanical motive metadata the presentation layer, advisory logic, and campaign log can read directly — it is not freeform narrative text
- save-load alias: `concern_pressure` reads as `hegemony_pressure` for back-compat with v2.3-era saves

### 10.2 Anti-spam rules

AI must not:

- offer redundant proposals to a target with whom France currently has an unresolved hard-reject posture
- escalate ratification when a recent hard-stop was rejected by the target, especially when the target is outside the current hegemon bloc

(Bargain-specific anti-spam moves to `WAR_BARGAIN_SPEC.md`.)

### 10.3 Refusal behavior

AI should refuse or resist:

- deep alliance from a nation that is part of the current hegemon bloc when the AI is outside that bloc (uses §9.1)
- deep treaties from a nation the AI holds active betrayal strikes against (uses §9.2)
- deep treaties at 3 active victim-side strikes except under explicit survival exceptions (already wired)

### 10.4 Strategic focus / advisory layer

Deferred. Personality-specific bargaining agendas and richer court personas move later.

### 10.5 Performance / architecture guard

No new hot-path per-region scans.

Use:

- per-turn cached `get_bloc_members(leader)` and `_calculate_hegemony_pressure(world)` — invalidate on treaty ratification, vassal change, war declaration, peace, and §8.8.7a same-turn alliance termination
- direct pair-key reads on `betrayal_history`
- targeted validation checks on key event hooks

`_classify_witness_scope`'s shared-enemy loop is currently O(active_nations) per witness — fine at 5 nations, monitor at 19+.

**Runtime contracts (must stay explicit):**

- `WorldState._bloc_members_cache: Dict[str, Set[str]]` stores the per-turn cached leader → members mapping. `invalidate_bloc_members_cache()` is called from the same seams as `invalidate_active_nations_cache()`, plus the §8.8.7a same-turn alliance termination path.
- Non-France hegemon telemetry uses `logging.getLogger("backend.game_logic.coalition")` at `INFO` level with the message format `[hegemony] non-France hegemon detected ({hegemon_nation} @ {share:.2f}); skipping add_threat (threat scalar France-targeted in v0.1)`. Rate-limit is once per turn per actor.
- Named-diplomat render paths fail loud: `raise ValueError(f"loyalist register unsupported: {nation}/{personality}")` when a cast-nation `speaker="envoy"` path cannot resolve a supported register. Do not silently fall back to `system`.

---

## 11. Player-Facing Surfaces

### 11.1 Diplomatic Ledger

**v2.4 headline:** add a "Balance of Europe" line at the top of the Nations tab — one dynamically generated sentence (possibly several composed lines) that names the current hegemon, their bloc share, and the coalition state. Worked example below shows a Case 4 (coalition DECLARED) configuration so all three lines are simultaneously legal under the composition rules; for Case 3 (BREWING), the Castlereagh subsidy line is suppressed per the rule below.

```
Balance of Europe — The French System commands 53% of Continental power.
Castlereagh has begun assembling subsidies. Berlin and Vienna are listening.
Coalition pressure against the French System: Mobilizing (78/100) — Britain leads.
```

*Bloc label appears identically across all three lines — the headline is the surface where `describe_hegemon_bloc` is most visible to the player, so any inconsistency between lines reads as a name change. Authors must route every hegemon mention through the helper, even where bare nation name would parse.*

**Bloc-label contract:** The hegemon phrasing is not a bare nation name. It uses the `describe_hegemon_bloc(world, hegemon, share)` helper (B-Hegemony) per `COMMITMENTS_PRESENTATION_SPEC.md` §8.1a. Below `50%` share the label is descriptive (*"French-led alignment"*); at `50%+` the authored proper noun unlocks (*"French System"*); at `60%+` the same proper noun persists while crisis framing intensifies. `coalition` remains reserved for the formal anti-hegemon war structure and must never appear as the hegemon-side label.

Lines compose from current state — no authored copy table. The state machine has five compositional cases:

- **Case 1 — No hegemon (max bloc share < 33%):** single standalone line. (Threshold matches `_calculate_hegemony_pressure`'s pressure-floor return per §7.3 — the engine returns no hegemon below 33% even though the §9.1 acceptance-formula penalty starts at 30%.)
  > *"Balance of Europe — no bloc commands decisive power. The continent remains in equilibrium."*

  The equilibrium line is standalone. If coalition pressure is independently brewing from event-based threat, a BREWING line from Case 3 may still render below it; composable.

- **Case 2 — Hegemon exists, no coalition:** one or two composed lines. Hegemon phrasing resolves through `describe_hegemon_bloc` per §8.1a (below 50% = *"{Hegemon} leads a widening {descriptive_label} ({share}%)"*; at 50%+ = *"The {bloc_label} commands {share}% of Continental power"*).
  >
  > *"European courts have taken note, but no coordinated response has yet formed."* (present during the `Tension` / `Murmurs` tiers per `COALITION_SPEC.md` §3a, or on a turn when a same-turn `balance_of_europe_shifted` beat fired even though the scalar has not yet reached `Tension`; on that first-crossing turn it should read as a quiet echo, not as a second beat)

- **Case 3 — Coalition BREWING (no leader yet per COALITION_SPEC §3-§4):** hegemon line + brewing line. Hegemon phrasing follows the §8.1a contract above.
  >
  > *"Coalition pressure against the {bloc_label or hegemon}: Brewing ({threat}/100). Qualifying: {nation_list}."*

  Per `COALITION_SPEC.md` §3c / §4a, a coalition leader is selected only at **declaration**; during `BREWING` there is no designated leader, and the headline enumerates qualifying nations rather than naming a leader. The `Castlereagh has begun assembling subsidies` flavor line is NOT rendered at brewing (it refers to declared-coalition behavior).

  Worked example (BREWING):
  >
  > *"Balance of Europe — France leads a widening French-led alignment (41%)."*
  >
  > *"Coalition pressure against France: Brewing (64/100). Qualifying: Austria, Britain, Prussia."*

- **Case 4 — Coalition DECLARED (leader selected):** hegemon line + leader line + formal coalition line. Coalition declaration copy contrasts the formal coalition against the named bloc (e.g. *"Britain's coalition marches against the French System"*) per §8.1a surface contract.
  >
  > *"{Coalition leader's named diplomat} has begun assembling subsidies."*
  >
  > *"Coalition pressure against the {bloc_label or hegemon}: {ladder_label} ({threat}/100) — {leader} leads."*

  On the declaration turn only, the coalition-declaration popup / dispatch carries the §8.1a contrast copy (for example, *"Britain's coalition marches against the French System"*). The headline keeps the composed three-line form above.

- **Case 5 — Coalition COOLDOWN:** hegemon or equilibrium line + cooldown line.
  > *"The last coalition has disbanded. Europe takes breath, but no new coalition can form for {turns_remaining} turns."*

  If `threat_level > 0`, append one residual-pressure flavor line below the cooldown line: *"The balance has not righted itself; the courts continue to count obligations."* Lingering alarm during cooldown is real under the v0.1 scalar, so the copy must acknowledge restraint without implying Europe has forgotten.

**Composition rules:**

- Cases are mutually exclusive on their opening line (either "equilibrium" or "{Hegemon} leads"), composed linearly from current state — no authored copy tables.
- The subsidy-flavor line uses the coalition leader's named diplomat (Castlereagh for Britain, Metternich for Austria, etc.). If the leader has no named diplomat in `diplomat.py`, fall back to *"The courts of {leader} have begun assembling subsidies"*.
- The qualifying-nation list (Case 3) uses period names, sorted alphabetically, comma-separated. More than 4 qualifying nations collapse to *"Qualifying: {n} courts"*.

**Threshold-crossing beats (same-turn signal contract):**

- The Balance of Europe headline is not allowed to be the player's **first** clue that pressure rose. On the first upward crossing of `33%`, `50%`, or `60%`, a `balance_of_europe_shifted` named-diplomat notification fires *before* the headline refreshes for the turn. Per §7.3 the beat surface MUST NOT be the headline itself or the Morning Dispatch Balance line — both display state, not events.
- If `coalition_cooldown > 0`, the threshold beat uses the cooldown-aware wording from §7.3 so the player hears both truths at once: Europe is hardening, but the courts cannot yet form a new league.
- Every beat names: (a) the current hegemon, (b) the new share band, (c) what the courts are doing now, and (d) one counter-play hint when one is legible.
- Good counter-play hints in v0.1 are limited to already-existing moves: release a vassal, avoid adding another major ally, let a deep treaty lapse, or repair a wronged court before seeking another alignment once `Make Amends` is live.

Per-nation rows on the Nations tab (already present) gain:

- France's global reliability descriptor (already present)
- bilateral betrayal warning when that nation distrusts France specifically (already present)
- §8.8 grievance flags from defensive-call refusals (already specced in DG-4 amendment)
- bargain section deferred to `WAR_BARGAIN_SPEC.md`

Per-nation **bloc membership badges** (`[French System]`, `[Coalition Member]`, `[Neutral]`, `[Vassal of Saxony]`) are deferred out of v2.4.3 per `COMMITMENTS_PRESENTATION_SPEC.md` §8.1a.4. The Balance-of-Europe headline is the authoritative owner of the bloc label layer in this phase; per-row stamping waits until a later playtest pass explicitly asks for it.

Presentation rule: render as one compact commitment block per nation, not as multiple new dense subsections repeated across tabs. The Balance of Europe headline is the ledger's new entry point — players see the geopolitical situation in three lines before scanning per-nation detail.

### 11.2 Proposal preview / Talleyrand advisory (already shipped)

Dedicated **Political context** panel on proposal preview / ratification surfaces.

Surfaces:

- current hegemony pressure relevant to the target (category `hegemony` — driven by bloc share per §9.1)
- any bilateral betrayal memory affecting the offer, including one remembered referent when episode metadata exists
- main nation likely to be angered if France proceeds
- one immediate counter-play lever when one is legible from current state (release a vassal, avoid a new major ally, let an alliance lapse, or Make Amends with a wronged court once B-B7 is live)

Canonical preview contract (shipped):

- expose a structured `warnings[]` list
- each warning contains `severity`, `category`, `text`
- `betrayal` warnings cite one remembered referent when episode metadata exists (named nation, broken treaty, abandoned alliance, or witnessed slight) so later refusals read as memory rather than hidden math

Warning categories used in this phase:

- `hegemony` (v2.4 — replaces `concern`)
- `betrayal`
- `hard_reject`
- `paradox`
- `peace_conflict` (war-joiner / conflict-geometry preview; canonical name for the old war-preview token `rivalry`)

(`bargain` category reserved for `WAR_BARGAIN_SPEC.md`. Legacy warning-category aliases: `concern` reads as `hegemony`; older war-preview token `rivalry` reads as `peace_conflict`.)

Severity contract (shipped):

- ordinals: `critical = 3`, `high = 2`, `medium = 1`, `low = 0`
- stable category tie-break order: `paradox`, `hard_reject`, `bargain`, `betrayal`, `hegemony`, `peace_conflict`
- later categories should append after this order, not silently reshuffle it
- tie-break beyond severity + category currently uses text sort; a stable emit-sequence index would be more robust at scale (low priority; flagged for future)

Preview legibility rules (shipped):

- show at most 2 warnings inline
- sort by severity first, then immediate player relevance
- collapse overflow behind `View all warnings`
- on a turn that crosses a new hegemony band (as defined by `_hegemony_signal_band` in `coalition.py` — `0 / 1 / 2 / 3` for below-threshold / noticed / alarming / crisis, corresponding to the `33% / 50% / 60%` beat thresholds rather than the ladder gates), reserve one inline slot for the new `hegemony` warning if the current proposal would intensify that pressure. If the inline cap is already saturated by `critical` warnings, the hegemony warning displaces the lowest-severity slot rather than overflowing — a hegemony band-crossing turn is the dramatic moment where dropping it silently would be worst.

### 11.3 Treaty display

Active treaties tab — no new content in this phase. (Bargain rows live in `WAR_BARGAIN_SPEC.md`.)

### 11.4 Dispatch and campaign log

High-signal events for this phase:

- `balance_of_europe_shifted` (same-turn named-diplomat notice / dispatch beat on upward `33 / 50 / 60` crossings; quieter downward relaxations at `60 -> 59` and `50 -> 49` stay advisory-only per §7.3)
- betrayal recorded
- commitment paradox resolved (already shipped via legacy alliance_paradox flow)
- hard-reject posture triggered (already shipped)
- hard-reject posture cleared (already shipped)
- major reliability improvement or drop
- Make Amends offered / refused (new in this phase — §8.6.1)

Bargain events (`bargain_ratified`, `bargain_triggered`, `bargain_fulfilled`, `bargain_breached`, `bargain_voided`) live in `WAR_BARGAIN_SPEC.md`.

Campaign log metadata payload (shipped):

- `episode_id`, `end_reason_family`, `end_reason_action`, `fault_nation`, `decision_reason`, witnesses with `scope_reason`, deterministic deltas

Rendering rule: store the full metadata payload on the event record; render a compact one-line summary in the Campaign Log; deeper detail can be shown later through tooltip / expand affordances without changing the stored payload.

The full felt-experience presentation (named-diplomat CRITICAL/NORMAL notices, the dedicated paradox popup, and in-popup after-choice asides) lives in `COMMITMENTS_PRESENTATION_SPEC.md` (`C3-lite`).

---

## 12. Data Model

### 12.1 Already shipped

- `diplomatic_reliability: Dict[str, int]` — nation-keyed shared global reputation scalar
- `betrayal_history: Dict[str, Dict]` per §6.2
- `next_episode_id: int` per §6.5
- `commitment_paradox_popup: Optional[Dict]` — canonical v2.4.3 field name for the renamed paradox popup; `alliance_paradox_popup` remains a load-side alias for save-load back-compat

### 12.2 To add this phase (v2.4)

- `reparations_cooldown: Dict[str, int]` — pair-key → turn number at which Make Amends (§8.6.1) becomes available again for that pair; `0` or absent = immediately available

**v2.4 removed from this phase:**

- `nation_concerns: Dict[str, Dict]` — replaced by per-turn `_calculate_hegemony_pressure(world)` (no stored field)
- `actor_honored_turns: Dict[str, int]` — redemption tick cancelled (B6 cut as not legible to players)

**v2.4 added (no new fields — pure helpers):**

- `world.get_bloc_members(leader: str) -> List[str]` — per-turn cached, derived from existing vassal + treaty state
- `WorldState._bloc_members_cache: Dict[str, Set[str]]` — leader → members cache backing `get_bloc_members`
- `power_score(nation: str, world) -> int` — derived from existing region count + scenario `power_tier`
- `_calculate_hegemony_pressure(world) -> Dict[str, int]` — pure function over current state

§8.8 DG-4 fields (`oathbreaker_posture`, `anti_renewal_cooldown`, grievance flag on `betrayal_history`, `war_entry_ledger`) are unchanged from v2.3 and tracked in their own slice.

### 12.3 Deferred

- `diplomatic_commitments`, `next_commitment_id` → `WAR_BARGAIN_SPEC.md`
- `trusted_partners`, `nation_strategic_focus`, `nation_power_scores` → later phases
- **No `nation_power_tiers` runtime field.** `power_tier` is authored scenario data on each nation record (per `SCALE_READINESS_PLAN.md` §"Phase 0 Cross-Cutting Taxonomy": values `major / secondary / minor`). `world.get_power_tier(nation)` reads the authored record live with a `_POWER_TIER_DEFAULT = "secondary"` fallback; there is no runtime map to shadow or serialize. A future `nation_power_scores` field, if added, is a separate runtime signal that must not overwrite `power_tier`.

Do **not** add ally-beneficiary settlement entitlement fields in this spec. Do **not** add a separate `nation_claims` store — until a settlement system defines a canonical claim model, claim-like state stays inside bargain records (in `WAR_BARGAIN_SPEC.md`).

---

## 13. Implementation Sequence

### Slice A. Foundations

**Already shipped:**

- `betrayal_history`, `next_episode_id`, witness-scope classifier, `commitment_event_metadata`, structured `warnings[]`, breach preview with reliability/applied-vs-intended deltas
- substrate ledger surfacing for reliability and bilateral betrayal
- `commitment_paradox` HARD_STOP type registration (placeholder)

### Slice B. Hegemony pressure (v2.4 rewrite)

**Already shipped (B2a/B2b — unchanged):**

- third-party anger metadata produced for breach events
- witness scoping with `scope_reason` precedence
- per-episode strike cap of 2
- redemption decay (severity-scaled) — strike-removal half
- hard-reject posture trigger / clear emits
- preview plumbing for `hard_reject` warnings

**v2.4 cancelled (was in v2.3 plan, no longer ships):**

- ❌ B-A1-fill (concern seed) — replaced by hegemony engine
- ❌ B-B2a-fill (third-party ratification anger) — captured by hegemony pressure naturally rising when France allies with someone (asker's bloc grows → next turn hegemony pressure rises against asker's bloc)
- ❌ B-B6 (redemption tick) — invisible to players, cut
- ❌ Prussia-Saxony authored escalation triggers — no longer needed without static rivalry seed

**This phase ships (v2.4):**

- **B-Hegemony: balance-of-power engine (NEW).** Add `_calculate_hegemony_pressure(world)`, `world.get_bloc_members(leader)`, `power_score(nation, world)` helpers. Wire passive contribution into `coalition.py` `process_coalition_turn` via existing `add_threat()` API, gated on `hegemon == world.player_nation` (v0.1 France-only scalar; see §14 R5 and the plan wire-up). Update `coalition_leadership_score` with bloc-share-against term. Per-turn caches per CLAUDE.md golden rule 8. **~18-22 tests** (includes four prerequisite-helper tests surfaced in v2.4.2 audit: `world.get_power_tier` reads authored scenario record with no shadow runtime map; cache invalidation at four call sites — treaty ratification, vassal change, war declaration, peace; `_POWER_TIER_DEFAULT` fallback path; recursive `_top_overlord` vassal-chain walk with cycle safety and 3-deep nesting; non-France-hegemon guard skips `add_threat`). See `RELIABILITY_IMPLEMENTATION_PLAN.md` §B-Hegemony for the full test list.
- **B-B1-lite: acceptance formula collapse.** Add `hegemony_target_mod` (single negative term per §9.1) and `bilateral_betrayal_mod = -6 * strike_count` per §9.2. Tighten `reliability_modifier` to `// 10` capped ±6 per §9.4. Wire debug breakdown output and feedback strings. ~6 tests (hegemony mod returns 0 when asker outside bloc, hegemony mod scales with share, bilateral betrayal scales with strike count, hard-reject still fires at 3 strikes).
- **B-B3: paradox rename.** Unchanged from v2.3. Rename push-side `dialogue_manager.push({"type": "alliance_paradox", ...})` to `commitment_paradox`; keep `alliance_paradox` as accepted alias on read for save-load. Rename the popup type passthrough on the Godot side (`alliance_paradox_popup.gd` field reads). The dedicated `commitment_paradox_popup.{tscn,gd}` surface ships in the `C3-lite` slice (Slice C below). ~3 tests.
- **B-B7: Make Amends verb.** Standard strike-clearing path unchanged from v2.1/v2.3. Implement the active-redemption action per §8.6.1: parser entry, `_execute_make_amends` in `diplomatic_executor.py`, cost validation, `reparations_cooldown` serialization, campaign-log emit, Talleyrand-voiced refusal advisory for each of the four refusal conditions. France-only in v0.1. The grievance-clearing variant in §8.6.1a belongs to B-B4. ~8 tests.

**§8.8 DG-4 call-to-arms (B-B4) — parallel slice, tightened by v2.4.3.** Still tracked in its own slice per the DG-4 amendment, but the slice now explicitly owns three follow-through contracts: §8.6.1a grievance-variant Make Amends (distinct verb, shared cooldown, `400g + 2 DP`), §8.8.7a same-turn alliance termination with `end_reason_family = "defensive_refusal_termination"`, and the R9/R10/R11 playtest gates added in §14. ~25-29 tests once those additions are covered, parallel to this slice.

### Slice C. C3-lite presentation pass (v2.4 trimmed)

See `COMMITMENTS_PRESENTATION_SPEC.md` v0.5.1. Ships with this phase:

**v2.4 keeps:**

- Named-diplomat resolution helper: `speaker="envoy"` resolves to nation's named diplomat per Voice Bible; `speaker="foreign_office"` renders as "The Chancery of {nation}"
- Committed mock prose for the three events that fire: `hard_reject_posture_triggered`, `diplomatic_treaty_broken` (french_breach), `commitment_paradox_resolved`
- Dedicated `commitment_paradox_popup.{tscn,gd}` surface (replaces legacy `alliance_paradox_popup`)
- Balance of Europe headline rendering (new for v2.4 — see §11.1)

**v2.4 cuts:**

- ❌ Elevated card variant on the notification rail — three events do not justify the infra; route through existing notification system with named-diplomat copy doing the dramatic lift
- ❌ Split-voice render `attributed_lines[]` on popup scene — single-voice with named-diplomat attribution is enough at 5-nation scale
- ❌ N+1 Talleyrand aside callback — defer to later presentation pass if playtest shows the gap

Estimated tests: ~10-12 (named-diplomat resolution, three event copy paths, paradox popup field wiring, Balance of Europe headline composition).

### Slice D. Deferred follow-up

Same as before:

- D1 (advisory-first strategic focus, deeper AI integration)
- D2 (coalition buildout / generalization)

Both stay deferred unless playtesting proves the v0.1 pressure layer still lacks political texture.

### Slice WB-* (deferred to Peace Deals phase)

War bargain implementation moved to `WAR_BARGAIN_SPEC.md` slices WB-A through WB-D. Not part of Memory and Pressure ship.

---

## 14. Risks

### R1. Hegemony pressure dominates everything

If `hegemony_target_mod` swings deep-treaty acceptance from possible to impossible whenever France's bloc passes 30%, players may feel the engine is too on-rails.

**Mitigation:** the pressure ladder values (1/3/5/8 by share bucket) are authored in `coalition.py` and tunable. Playtest gates: France should be able to maintain Bavaria + Saxony in its bloc (~35% share) without immediately triggering coalition formation; only deep over-extension (50%+) should make coalition formation inevitable. If the 30% formula floor trips too early in playtest, raise to 33% to align with the §7.3 ladder gate; ladder-gate tuning itself must keep `33 / 50 / 60 / 70` for beat alignment.

### R2. Pressure-without-promise feels punitive

Without bargains, the player has more friction and less new agency. Risk: "diplomacy got harder but I can't do anything new."

**Mitigation:** the C3-lite presentation pass + Make Amends + Balance of Europe headline are the agency restoration paths — events that already fire should land as memorable political moments rather than log lines. Playtest after this phase ships; if friction-without-agency reads as flat, accelerate `Bilateral Peace Hardening` so `WAR_BARGAIN_SPEC` can land sooner.

### R3. Bloc-share calc opacity

If players see the pressure but can't predict which actions raise/lower bloc share, the engine feels arbitrary.

**Mitigation:** the Balance of Europe headline names the hegemon and bloc share explicitly. Threshold beats (`balance_of_europe_shifted` notifications at 33% / 50% / 60%) name the contributing levers per §7.3. Proposal preview `warnings[]` includes a `hegemony` category warning explaining the share-driven penalty per §11.2. Debug breakdown output shows `hegemony_target_mod` and `bilateral_betrayal_mod` independently for tuning. Per-row bloc membership badges are explicitly deferred per §11.1 — the headline + beats + preview warnings are the v2.4.3 visibility set.

### R4. Warning overload

If warnings fire every turn, players stop reading them.

**Mitigation:** event-driven warning model only; preview capped to 2 inline warnings; hegemony pressure surfaces once via the Balance of Europe headline rather than as per-nation warnings. Per-proposal warning fires only when a specific proposal would trigger a meaningful penalty (not every cross-bloc proposal).

### R5. Hegemon-agnostic engine but France-targeted threat scalar

The hegemony engine returns the actual hegemon (forward-compat), but `coalition.py`'s `threat_level` scalar remains France-targeted in v0.1.

**Mitigation:** the engine returns `{hegemon: pressure}` shape now; display copy reads the hegemon name from this dict, not from a hardcoded literal. When a non-French hegemon becomes possible (full-Europe scale + non-French player nation support), the threat scalar generalization is a one-helper refactor (`int` → `Dict[str, int]`) plus updates to `add_threat`, `reduce_threat`, formation/dissolution. Tracked as Coalition Generalization (D2) but not v0.1 scope.

### R6. Power score formula too simple

`region_count * tier_weight` ignores manpower, treasury, military strength. A nation with 6 regions but a depleted treasury and broken army still reads as powerful.

**Mitigation:** v0.1 simplicity is intentional — a more complex formula is hard to playtest. The helper signature `power_score(nation, world)` is stable, so v0.2+ can swap the implementation without touching the hegemony engine. Flag for playtest: if Saxony's "strength" reads as obviously wrong, accelerate the formula upgrade.

### R7. No passive reliability recovery path after cancelling B-B6

v2.4 cancelled the redemption tick (`actor_honored_turns` +3 reliability per 5 honored turns) on the grounds that it was invisible to players. The remaining recovery paths are **Make Amends** (+2 reliability per use, 10-turn cooldown per pair, France-only in v0.1) and bargain fulfillment (deferred to `WAR_BARGAIN_SPEC.md`). A long campaign with no new breaches accrues zero passive reputation recovery, even though France is demonstrably keeping its word — reliability can only drift flat or down from that point.

**Mitigation:** playtest gate after B-B7 ships. If reliability feels stuck, options in preference order are (a) bump Make Amends reliability reward to +3 or +4, (b) remove the per-pair cooldown cap, (c) reintroduce a lightweight passive tick tuned to be visible (e.g. surface the +3 as a campaign-log event so the player sees it). The tick is not categorically unshippable — the v2.4 cut rationale was "invisible to players", which a small surface change would address.

### R8. One-turn delay on coalition `threat_level` scalar after cancelling B-B2a-fill

v2.4 cancelled the third-party ratification anger loop on the grounds that hegemony pressure captures the same signal when the asker's bloc grows. Revised analysis (v2.4.3) separates the two affected signals:

**Acceptance-formula penalty (`hegemony_target_mod` in §9.1) — NO lag.** Per §10.5, `_calculate_hegemony_pressure(world)` and `get_bloc_members(leader)` are per-turn cached with invalidation on treaty ratification, vassal change, war declaration, and peace ratification. When France ratifies an alliance with Britain mid-turn, the cache invalidates immediately and a same-turn recompute sees the updated bloc share. Any subsequent same-turn proposal check reads the new `hegemony_target_mod`. The formula side is already correct.

**Coalition `threat_level` scalar (`coalition.py`) — ONE-TURN lag exists.** The passive hegemony threat contribution is added via `add_threat()` during `process_coalition_turn` (end-of-turn), not at ratification moment. When France ratifies an alliance, the coalition threat scalar jumps on turn N+1, not turn N. This means Balance of Europe headline bucket crossings and `BREWING` transitions visibly trail the player's ratification by one turn.

**Mitigation (applies to `threat_level` only — formula side already correct):** option (a) is the canonical answer and **must ship with B-Hegemony**, not be selected from a menu later. (a) Emit a deterministic same-turn `balance_of_europe_shifted` named-diplomat notification at ratification / threshold-crossing time that narrates the political reaction without moving the scalar, then let the N+1 tick do the math. The notification IS the player's clue; the scalar lag is then invisible because the dramatic moment already landed. Options (b) and (c) below are escape hatches if playtest after (a) ships still reads the lag as a bug — they are not menu items for B-Hegemony's first cut. (b) Accept the delay as a documented design call (only valid because (a) landed first). (c) Trigger an inline `add_threat` call at deep-treaty ratification / vassal-creation moment with the same increment the next-turn engine would contribute; next turn's engine must then either recognize the already-applied signal (source_key dedupe) or subtract the inline contribution from its own output to prevent double-counting — the invasive correction reserved for the case where (a) demonstrably fails playtest.

### R9. Make Amends flood per turn (v2.4.2 audit A13)

§8.6.1 cooldown is per-pair. With five wronged nations, France can invoke Make Amends five times in a single turn (`5 × 200g + 5 DP = 1000g + 5 DP`) for `+10` reliability. No global per-turn cap is documented. With the grievance variant in play (§8.6.1a, ships B-B4), the same turn can clear five grievance flags at `5 × 400g + 10 DP = 2000g + 10 DP` for `+15` reliability — still a meaningful political cost, but the "repair tour" completes in one turn rather than across the historical arc a player might expect.

**Mitigation:** likely fine economically — `1000g` is ~2-3 turns of French income, `5 DP` is a full turn's DP allocation, and the player has at most 5 pairs with active strikes at any moment on the 5-nation map. Playtest gate: if multi-Amends turns feel gamey ("speedrun reliability restoration"), add a global `max_amends_per_turn = 2` cap. At full-Europe scale (13+ nations), the pressure to add the cap rises — queue this item for revisit when B-B4 lands.

### R10. Bandwagoning escape valve AI-completeness (v2.4.2 audit A14)

§9.5 names bandwagoning as one of two escape valves: non-bloc nations proposing TO the hegemon get `hegemony_target_mod = 0`. This works only if AI nations actually generate minor→hegemon alliance proposals. Spec assumes `ai_diplomacy.py` fires them; audit could not verify.

**Mitigation:** B-Hegemony now treats this as required behavior, not just an audit question. Add an explicit bandwagon trigger (P-series rule) for non-bloc minors and exposed secondaries when hegemon share reaches the alarming band, relations are not hostile, and the nation is not already locked into a rival deep bloc. Playtest gate: if Bavaria / Saxony never propose to France when France is dominant, the escape valve is decorative — ship the AI trigger before this phase closes.

### R11. Inverted boundary after the v2.4.3 ladder realignment (was: exact-share boundary at 30%)

After the §7.3 realignment that moved the ladder gates to `33 / 50 / 60 / 70`, the inconsistency direction inverted. The §9.1 acceptance-formula penalty starts at `share > 0.30` (`-1` to `-1.8`) while `_hegemony_pressure_for_share` returns `0` until `share >= 0.33`. Between 30% and 33% bloc share, a pair sees an acceptance-formula penalty on cross-bloc proposals but no per-turn pressure accrual and no `balance_of_europe_shifted` beat. Conversely, at exactly `share = 0.33`, the ladder returns `1` (per-turn pressure begins) while `hegemony_target_mod` returns `-1` (already accruing for three percentage points). This is intentional per §7.8.1 — per-pair friction begins one band before continental consensus, mirroring how foreign offices privately count an opponent's allies before public clamor.

**Mitigation:** documented design call. The 30-33% gap surfaces in proposal-preview `warnings[]` (the per-pair friction is visible when the player attempts a relevant cross-bloc proposal — not silent), even though no headline / beat fires yet. If playtest shows the 30-33% gap reading as "the engine penalizes me for a bloc Europe hasn't noticed," shift the formula floor from `0.30` to `0.33` to merge the two thresholds; the slope `int((share - X) * 60)` then re-anchors automatically. The other direction (lowering the ladder gate) is forbidden because it would re-create the silent-tax band the realignment closed.

---

## 15. Resolved Design Calls

### Gate 1 — Hard forced-choice vs soft penalty for rival military alignment?

**Resolved:** forced choice for deep military alignment, soft pressure below that. (v2.4 implementation: `hegemony_target_mod` scales the soft-pressure band; the 3-strike `hard_reject_posture` supplies the door-shut for deep treaties. The v2.3 `political_commitment_mod` composite was removed as redundant — the two modifiers surface independently in `warnings[]` and `components`.)

### Gate 2 — Global reliability + bilateral betrayal, or all pair-specific?

**Resolved:** keep the split.

### Gate 3 — Timed territorial promises or narrower war bargains?

**Resolved:** war bargains chosen — and **moved to `WAR_BARGAIN_SPEC.md`** in the v2.0 rescope.

### Gate 4 — Promise deadlines / suspension model?

**Resolved:** cut entirely. (Inherited by `WAR_BARGAIN_SPEC.md` when bargains land.)

### Gate 5 — AI-authored only, or limited player-authored bargaining too?

**Resolved:** allow limited player-authored bargaining. (Lives in `WAR_BARGAIN_SPEC.md`.)

### Gate 6 — Hard-reject threshold?

**Resolved:** keep 3 strikes, but cap strike gain to 2 per episode. **Already shipped.**

### Gate 7 — Ally-beneficiary land promises in v0.1?

**Resolved:** defer to `Ally Participation + Common Peace`.

### Gate 8 — Global bargain cap or structural caps?

**Resolved:** structural caps only. (Inherited by `WAR_BARGAIN_SPEC.md`.)

### Gate 9 — Coalition obligation or alliance obligation?

**Resolved:** distinct textures with explicit overlap rules. v0.1 stays anti-France-only; helpers stay parameterized so later `Coalition Generalization` is a clean refactor.

### Gate 10 (new in v2.0 rescope) — Ship bargains alongside substrate, or rescope?

**Resolved:** rescope. The April 16 audit established the substrate had shipped without the bargain layer or formula integration; trying to land all of `Reliability + Commitments` as one phase would have either delayed every part or shipped a half-bargain. Splitting into Memory and Pressure (now) + Peace Deals containing `WAR_BARGAIN_SPEC.md` (later) lets the engine grow with each peace-related layer underneath it.

---

## 16. Draft Recommendation (v2.4)

For Memory and Pressure v2.4:

- **Keep all shipped substrate** — global reliability, bilateral betrayal memory, episode_id threading, witness scoping, hard-reject posture, structured warnings, cascade metadata. Nothing comes out.
- **Add the hegemony engine** (§7) — `_calculate_hegemony_pressure(world)`, `get_bloc_members`, `power_score`. Three pure helpers, ~60 LOC. Wires into existing `coalition.py` threat ladder via `add_threat()`.
- **Collapse the acceptance formula** (§9) — `hegemony_target_mod` (single negative term reading bloc geometry) + simplified `bilateral_betrayal_mod = -6 * strikes`. No composite floor needed.
- **Add the Balance of Europe headline** (§11.1) — three dynamically composed lines at the top of the Diplomatic Ledger naming the hegemon, share, and coalition leader.
- **Rename `alliance_paradox` → `commitment_paradox`** (B-B3, unchanged from v2.3).
- **Ship Make Amends** (B-B7, unchanged from v2.1/v2.3) — France's deliberate repair gesture.
- **Trim Slice C** to named-diplomat resolution + paradox popup + committed prose for three events. Cut the elevated rail-card variant + split-voice render infra.
- **Defer war bargains** to `WAR_BARGAIN_SPEC.md` (unchanged).
- **Keep §8.8 DG-4 work as-is** (unchanged) — orthogonal to the balance refactor.

That is enough to make diplomacy feel like Napoleonic balance-of-power politics, with bilateral memory still driving distrust, and named-diplomat copy carrying the dramatic moments — without authoring static rivalry pairs or stacking acceptance formula constants players cannot feel.

**Test budget:** ~25-30 tests (B-Hegemony 12 + B-B1-lite 6 + B-B3 3 + B-B7 8) + ~10-12 Slice C trimmed = **~35-42 tests, 1 session**. Down from v2.3 ~68-74 tests / 3 sessions.

---

## 17. Changelog

- **April 20, 2026 — v2.4.3 Block 3 fold.** The Block 3 bloc-naming contract and CF1-CF4 closure items have been folded back into their owning specs rather than gating the plan through a separate audit block. §7.3's threshold-crossing beats now name `noticed`/`alarming`/`crisis` semantics per-band and reference `COMMITMENTS_PRESENTATION_SPEC.md` §8.1a for the descriptive-vs-proper-noun contract. §11.1's Balance-of-Europe headline example updated to the adopted descriptive label at 47% and adds an explicit bloc-label contract paragraph; Case 2/3/4 composition lines now route through `describe_hegemon_bloc`. §11.1 per-nation bloc-membership-badge line moved out of the Nations-tab row list into an explicit deferral paragraph pointing at §8.1a.4. No new mechanical rules; this is a routing + label-layer clarification.
- **April 20, 2026 — v2.4.3 Deep-audit fixes.** Pre-implementation deep audit (`MEMORY_AND_PRESSURE_V2_4_2_DEEP_AUDIT.md`) raised 14 findings — 2 CRITICAL, 7 MAJOR, 5 MINOR — against v2.4.2. v2.4.3 applies the full action list. No new mechanical features; several contracts tightened, one new sub-section (§8.6.1a), one new sub-section (§8.8.7a), three new risks (R9/R10/R11). Edits by section:
  - **§5 — design principles.** Renamed layer 1 from *"Rivalry pressure"* to *"Hegemony pressure"* with explicit bloc-share framing. (Audit B1/C1.)
  - **§7.1 — vassal-chain recursion.** Replaced the single-hop `lord == leader` match with a `_top_overlord` walker that traverses the vassal chain to its terminus. Sub-vassals (Confederation-of-the-Rhine-style nesting) now surface on the top overlord's bloc list — unblocking the §7.7 "same engine at 13-20 nations" claim. Cycle-safe against data errors. Removed the "two-lord collision" rule (impossible under scalar `lord`); documented post-v0.1 multi-overlord tie-break as `power_score` then alphabetical. (Audit A1 — CRITICAL.)
  - **§7.2 — `power_tier` ownership.** Dropped the `world.nation_power_tiers: Dict[str, str]` runtime map. `world.get_power_tier(nation)` now reads the authored scenario record directly per `SCALE_READINESS_PLAN.md` §"Phase 0 Cross-Cutting Taxonomy" ("the authored scenario config is the single source of truth; runtime code reads from it and does not mutate it"). No serialization needed — scenario data is recreated on load. Mirror edit to the implementation plan's prerequisite-helpers block. (Audit A5 — MAJOR.)
  - **§7.3 — deterministic hegemon tie-break + non-France guard.** Replaced `max(bloc_shares.items(), ...)` with explicit `sorted` by `(-share, -bloc_power, alphabetical name)` — removes Python `max`'s first-occurrence bias over `majors` iteration order. Added a non-France-hegemon guard contract: the `add_threat` wire-up must gate on `hegemon == world.player_nation`, skipping the call (with debug telemetry) when a losing-campaign edge case produces a non-France hegemon. Balance of Europe headline copy still names the real hegemon for display. (Audit A7, A10 — MAJOR / MINOR.)
  - **§8.6 — reliability tick cancelled.** Removed the "wire this in this phase" directive that contradicted the B-B6 cancellation. Now explicitly states that the tick is cancelled, that implementers must not wire it, and that the v0.1 recovery paths are Make Amends + bargain fulfillment (deferred). See §14 R7 for the re-opening gate. (Audit A3 — MAJOR.)
  - **§8.6.1a — Make Amends (grievance variant).** New sub-section. Authors the grievance-removal contract §8.8.4 promised but §8.6.1 could not provide: precondition is ≥ 1 active grievance flag (NOT a strike), cost is 400g + 2 DP (doubled), cooldown is shared with the standard variant, action parser exposes both verbs. Grievance-variant reliability reward +3 and relation +8 (each larger than the standard variant, matching the larger political gesture). (Audit A4 — MAJOR.)
  - **§8.8.4 — grievance removal path.** Updated to reference §8.6.1a as the authoritative variant. Added grievance stacking cap (3 per pair for acceptance-formula input; underlying ledger surfaces "4+ grievances" distinctly). (Audit A4.)
  - **§8.8.7a — existing-alliance consequence of defensive refusal.** New sub-section. On `call_to_arms_refused_defensive`, the existing `ALLIANCE` / `DEFENSIVE_ALLIANCE` between refuser and victim **terminates** (downgrades to `PEACE`). Bloc membership recomputes same-turn; hegemony pressure recomputes next turn. `anti_renewal_cooldown` (§8.8.7) then gates re-ratification. Resolves the ambiguity about bloc-share semantics after refusal (historical precedent: Prussia 1795 / Russia pre-Tilsit 1807). (Audit A9 — MAJOR.)
  - **§8.8 — top-level graduation note.** Added structural-note that §8.8 (currently fifteen sub-sections) will graduate to its own top-level section when B-B4 ships, with a renumber of current §9+. Deferred to the B-B4 merge to avoid in-flight revision churn. (Audit C2.)
  - **§9.1 — `hegemony_target_mod` comment.** Corrected misleading *"Linear scaling from -2 at 30% to -20 at 60%+"* to *"0 at 30%, -18 at 60% exactly, clamped at -20 from ~63.34%+ onward"* — matches the integer truncation semantics the code implements. (Audit B4.)
  - **§9.2 — `bilateral_betrayal_mod` comment.** Corrected the misleading *"natural cap at -18 because 3 strikes triggers hard-reject"* — hard-reject blocks most proposals but does NOT cap strike accumulation. Survival-exception proposals (§8.7) with 4+ strikes compute -24+. Added explicit rules entry for above-3-strikes behavior. (Audit B5.)
  - **§9.3 — composite floor reintroduced conditionally.** The v2.4 "no composite floor needed" claim was broken by §8.8.9's stackable `grievance_modifier` (three grievances alone reach -90). §9.3 now has two clauses: *pre-DG-4* (no floor — only terms are hegemony -20 and betrayal -18), and *with DG-4* (composite floor -60 applies, grievance stacking caps at 3 per pair). Added plan-ordering callout to `RELIABILITY_IMPLEMENTATION_PLAN.md`. (Audit A2 — CRITICAL.)
  - **§11.1 — Balance of Europe state machine.** Specified four composition cases: no hegemon (equilibrium line), hegemon without coalition, coalition BREWING (no leader yet per COALITION_SPEC §3-§4), coalition DECLARED. Fixes the prior example's assumption that brewing has a named leader. (Audit A12, B6.)
  - **§13 — Slice B references updated.** `COMMITMENTS_PRESENTATION_SPEC.md` reference bumped v0.3 → v0.5.1. B-Hegemony test count raised from ~12 to ~18-22 matching the implementation plan audit. Wire-up guarded on `hegemon == world.player_nation`. (Audit B2, B3.)
  - **§14 — three new risks.** R9 (Make Amends flood per turn, cap if playtest shows gamey), R10 (bandwagoning AI-completeness, audit `ai_diplomacy.py` during B-Hegemony), R11 (exact-30% dead zone, boundary artifact). R8 rewritten to distinguish `hegemony_target_mod` (no lag — per-turn cache is invalidated on treaty ratification) from coalition `threat_level` scalar (one-turn lag — `add_threat` runs at end-of-turn). (Audit A11, A13, A14, A8.)
  - **§17 — v2.4.2 changelog bullet broken into sub-bullets** per audit C4 (a ~900-word single-blob bullet was hard to skim).
  - **Companion-doc edits.**
    - `RELIABILITY_IMPLEMENTATION_PLAN.md`: prerequisite-helper block dropped the runtime tier map; added recursive vassal-chain / cycle-safety / non-France-guard tests to the B-Hegemony test list; `add_threat` wire-up gated on `hegemon == world.player_nation`; new "Merge ordering — B-B1-lite and B-B4" section under Execution Order with three-option rubric (Option A preferred, Option B acceptable, Prohibited ordering called out).
    - `COALITION_SPEC.md`: §2a gained a new threat-table row (`hegemony_passive | +1/+3/+5/+8/turn | bloc share ≥ 30%`) and the "alliance does NOT generate threat" note softened to "alliance ratification does NOT *directly* generate threat on the signing turn" with an explicit passive-hegemony-pressure cross-reference. (Audit A6 — MAJOR.)
    - `COMMITMENTS_PRESENTATION_SPEC.md`: non-normative bulk trimmed per audit C7 (see that file's v0.5.1 changelog entry for the section-by-section list).
- **April 19, 2026 — v2.4.2 Terminology fix (same-day).** Replaced six uses of "Quadrangle" as a synonym for the forming enemy coalition. The Quadruple Alliance (1815) was the post-Napoleonic Concert of Europe diplomatic framework among Britain / Austria / Prussia / Russia — a *great-power management* structure, not the 1805-era anti-French coalition configuration. The game's mechanical term is and remains "Coalition". §7.3 ladder comment, §7.8.2 prose, §9.5 table, §9.5 playtest gates, §14 R1 mitigation, and §7.3 docstring all updated. No mechanical change.
- **April 19, 2026 — v2.4.2 Audit cleanup.** Pre-implementation audit pass (`MEMORY_AND_PRESSURE_V2_4_1_AUDIT_REPORT.md`) surfaced cross-doc stale references and substrate-helper gaps; v2.4.2 applies the doc-only fixes. No mechanical changes — all edits are doc alignment to v2.4 intent. Edits by section:
  - **§7.1 — `get_bloc_members` helper.** Rewrote code snippet to consume existing helpers (`world.vassals` dict iteration + `world.get_diplomatic_state(a, b)` returning string literals); removed the non-existent `TreatyState` enum, `world.get_vassals_of(leader)`, and `world.get_treaty_state(a, b)` calls; added helper-compat note.
  - **§7.2 — `power_score`.** Added explicit `_POWER_TIER_DEFAULT = "secondary"` fallback; added note that scenario-data wiring for `power_tier` is part of B-Hegemony.
  - **§7.3 — `_calculate_hegemony_pressure`.** Rewrote to derive majors inline via `world.get_power_tier(nation) == "major"` with a defensive fallback when no nation is authored major (no `world.get_major_powers()` dependency).
  - **§7.4 — leader selection.** Added France-hostility anchoring caveat scoping the v0.1 precondition.
  - **§8.4 — witness scoping.** Dropped the obsolete "switches to `nation_concerns` data once seeded" clause.
  - **§8.8.1 / §11.2 — category tie-break order.** Updated `concern` → `hegemony`.
  - **§8.8.3 — rival scope.** Reworded as a war-state proxy.
  - **§8.8.4 — grievance graduation path.** Rewrote to name durable witness tags as the post-v0.1 target.
  - **§9.2 — `bilateral_betrayal_mod` code snippet.** Switched to the existing `_get_active_betrayal_strike_count(world, actor, victim)` module function with an arg-order note.
  - **§9.5 — share ladder table.** Expanded the 33% row to 33-35% / `-1 to -3` to match the §9.1 formula at the bucket boundary.
  - **§10.2, §10.3, §10.5, §11.2, §11.4, §15 Gate 1 — concern prose sweep.** Cleaned up residual "high-concern nations" / "concern about" / "cached concern lookups" / "active concerns" / "View all concerns" / "concern escalation (Prussia-Saxony triggers)" phrasing and the composite `political_commitment_mod` resolution text.
  - **§14 — new risks.** Added R7 (no passive reliability recovery after B-B6 cancel) and R8 (one-turn delay on third-party reaction after B-B2a-fill cancel), each with mitigation options.
- **April 19, 2026 — v2.4.1 Clarification pass.** Added §7.8 "Relationship to Coalition Formation" — explicit two-layer distinction, state comparison table, historical 1805 Third Coalition example, three-state classification of non-bloc nations (neutral observer / alarmed neutral / belligerent), key playtest implication that peaceful hegemons can still trigger coalition formation through passive pressure. Added §9.5 "Gameplay scaling — France's alliance-building capacity" — illustrative share table showing France can still ally 1-2 minor powers freely, face mild friction at 3, real friction at 4+, structural rarity at 5+; documents the two escape valves (bandwagoning TO France is free, intra-bloc proposals are free); playtest gates for the ladder values. No mechanical changes — pure documentation fills gaps identified in a design-review conversation that would otherwise leave auditors and implementers deriving the answers themselves.
- **April 19, 2026 — v2.4 Hegemony refactor.** Replaced the static 4-pair `nation_concerns` seed with a per-turn `_calculate_hegemony_pressure(world)` engine that reads bloc shares dynamically (the §7.7 "target architecture" becomes v0.1, no transitional static layer). Renamed §7 from "Concern System" to "Hegemony Pressure System". §9 acceptance formula collapsed: `direct_concern_mod` + `concern_conflict_mod` + composite `political_commitment_mod` floor → single `hegemony_target_mod`. `bilateral_betrayal_mod` simplified to `-6 per active strike` flat (cap removed; hard-reject at 3 still gates the door). §6.3 deleted `nation_concerns` field. §10.1 AI `decision_reason`: `concern_pressure` → `hegemony_pressure` (legacy alias on read). §11.1 added Balance of Europe headline (dynamically composed three-line summary at top of Diplomatic Ledger). §11.2 warning category `concern` → `hegemony` (legacy alias on read). §12 data model: removed `nation_concerns` and `actor_honored_turns` from this-phase ship list. §13 Slice B rewritten: cancelled B-A1-fill (concern seed), B-B2a-fill (third-party ratification anger), B-B6 (redemption tick); added B-Hegemony slice (~12 tests); B-B1 collapsed to B-B1-lite (~6 tests); B-B3 and B-B7 unchanged. §13 Slice C trimmed: cut the elevated rail-card variant + split-voice render + N+1 aside; kept named-diplomat resolution + paradox popup + committed prose for three live events. §14 risks rewritten around hegemony engine. §16 recommendation rewritten. §8.8 DG-4 amendment unchanged (orthogonal). All shipped substrate (`betrayal_history`, `next_episode_id`, `commitment_event_metadata`, witness scoping, hard-reject posture, structured `warnings[]`, cascade metadata) unchanged. Test budget: ~35-42 tests, 1 session (down from v2.3 ~68-74 / 3 sessions). Companion docs: `RELIABILITY_IMPLEMENTATION_PLAN.md` rewritten in parallel; `COMMITMENTS_PRESENTATION_SPEC.md` v0.4 will trim the cut Slice C items.
- **April 17, 2026 — v2.3 DG-4 call-to-arms amendment absorbed.** Added §8.8 specifying three new episode types (`call_to_arms_refused_offensive`, `call_to_arms_refused_defensive`, `call_to_arms_honored_costly`) that implement the SCALE_READINESS_PLAN §DG-4 Amendment. Defensive refusal gets wider witness scope (`treaty_partner_of_breaker`), victim-grade permanent grievance flag (Make Amends-removable only), oathbreaker posture parallel to hard-reject, anti-renewal cooldown, and a new `grievance_modifier` acceptance-formula term. Positive episode `call_to_arms_honored_costly` is the first concrete §8.5 faithful-play trigger. New audit-trail artifact `war_entry_ledger` in campaign log. New scenario authoring scalar `honor_bias`. New implementation slice B-B4 flagged for `RELIABILITY_IMPLEMENTATION_PLAN.md` (~25 tests). Deferred: sequential inter-ally signaling, vassal refusal path, defender-tier severity weighting, Jealousy v3.1 integration.
- **April 16, 2026 — v2.2 audit fixes + scale architecture.** Renamed "rivalry" → "concern" throughout (field: `nation_concerns`) to align with target balance-of-power architecture where bilateral friction is dynamic, not static labels (§7 terminology note). Fixed seeded-pair count from 3 → 4 (stale after v2.1 added France↔Austria). Tightened redemption tick (§8.6) to require `OPEN_BORDERS` or above — `PEACE` alone no longer qualifies as active commitment. Clarified "deep treaties" = `DEFENSIVE_ALLIANCE` + `ALLIANCE` + `VASSAL` (§7.3). Added auto-downgrade rule: concern intensity drops `active` → `cold` when the concern pair reaches `DEFENSIVE_ALLIANCE` or above (§7.1). Added §7.7 Scale Architecture Note documenting the target dynamic-concern system for full Europe and listing what breaks at 15+ nations. Acceptance formula modifiers renamed: `direct_rivalry_mod` → `direct_concern_mod`, `rival_conflict_mod` → `concern_conflict_mod`. AI decision_reason enum: `rival_pressure` → `concern_pressure`. Warning category: `rivalry` → `concern`.
- **April 16, 2026 — v2.1 creative-audit folds.** §3 Goal 1 rewritten to own the "forced political tradeoff" framing (previously read as apologetic pressure-without-promise). §7.1 seeded France↔Austria as `secondary + active` to match the 1805 Third Coalition setting (previously absent on the claim Austria was a "swing partner"; creative audit flagged that framing as a period misread). §7.4.C flagged Britain-anti-continental-hegemon as the #1 historical-texture debt for D2 Coalition Generalization scope. §8.6.1 added **Make Amends** active-redemption verb — the v0.1 fun/agency lever that closes the passive-redemption gap (200g + 1 DP → remove 1 strike, 10-turn cooldown per pair, France-only actor in v0.1). §12.2 added `reparations_cooldown` field. §13 Slice B added B-B7 (Make Amends). Test budget bumped from ~60-66 to ~68-74 tests; session count unchanged at ~3.
- **April 16, 2026 — v2.0 rescope.** Renamed phase to "Memory and Pressure". War bargains moved to dedicated `WAR_BARGAIN_SPEC.md` (Peace Deals phase). Acceptance formula trimmed to three modifiers (no `bargain_value_mod`, no `war_entry_score`). §7.5 rivalry-driven paradox cut; legacy alliance-cross-war paradox renamed to `commitment_paradox`. §6.4 commitment store and §13 commitment data fields moved to `WAR_BARGAIN_SPEC.md`. Coalition forward-compat seams (`opposition_graph`, `war_bloc.target_nation` stores) cut from v0.1 — helpers stay parameterized. New Gate 10 added. New §6.5 note that `region_observer` witness scope reactivates when `WAR_BARGAIN_SPEC` ships. New §10.1 enum entry `unknown_baseline` to retire the current AI catch-all. Honored-turn reliability tick (§8.6) added explicitly as this-phase work. Vassal-decay edge case noted (§8.6). Composite-floor-supersedes-per-modifier-cap clarification added (§9.4). Stable-tie-break-index flagged as future improvement (§11.2).
- **April 14, 2026 — v1.0 draft** (`Reliability + Commitments`). Original spec covered rivalries, betrayal memory, and war bargains together. Rescoped April 16 after audit established the bargain layer was unimplementable in the same phase as the substrate. Original v1.0 content now split between this spec (substrate + rivalry pressure + paradox rename + presentation hand-off) and `WAR_BARGAIN_SPEC.md` (war bargains).
