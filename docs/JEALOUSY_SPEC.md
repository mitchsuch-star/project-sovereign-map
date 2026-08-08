# Jealousy System — Design Spec

> **Status:** ✅ **v3.1 BLESSED July 11, 2026** (user grant: "full auth to complete jealousy spec") — **BUILD RECORD = §0 (v3.2 addendum, authoritative where it amends the body).** The v3.1 body below is the approved design; §0 reconciles it against the post-MC 1805 codebase and records every build decision.
> **Phase:** Post-MC (the MC-3 relationship web prerequisite was MET July 10, 2026; the Marshal Content Pass CLOSED July 11, 2026).
> **Prerequisite:** V2b Defiance COMPLETE, Tactical Triangle COMPLETE, Relationship system COMPLETE, MC-2 skills + MC-3 web COMPLETE.
> **v3.1 Changes:** Top of ladder = +1 all stats, glory loss mechanic, §6b deferred, §7 simplified, Literal trigger clarified, escalation tier 3 clarified, confrontation popup timing. See §17 for full changelog.

---

## 0. v3.2 GATE RECORD + 1805 BUILD ADDENDUM (July 11, 2026 — authoritative)

**Gate outcome:** v3.1 approved IN FULL, including the items v3.1 had deferred to "v3.1 implementation" — §6b Rivalry Confrontation, the Separate-Them flag, and the Crowned-with-Glory buff all land in THIS build. The gate additionally takes its three owned riders — **ESP-1 (Fontainebleau petition)**, **ESP-2 (war-weary rich marshals)**, and **ESP-4 (rente default, folded per its DESIGN_REFINEMENT row)** — plus the **literal-AI follow-on check**, and appends a user-directed final phase: **Marshal Recruitment** (own spec: `docs/MARSHAL_RECRUITMENT_SPEC.md`).

### 0.1 Roster reconciliation (the v3.2 addendum MC-3 §11 required)

The spec body's examples predate the 1805 cutover. Live mapping:

- **Player literal** = **Soult** (the spec's "Grouchy" rows). The Vindicated Garrison expression, HOLD trigger, and intel enhancement apply to him; Grouchy himself arrives via the recruitment pool.
- **Player aggressive** = Ney, Lannes, Murat, Massena; **cautious** = Davout, Bernadotte. The authored MC-3 web (Ney↔Murat −1, Davout↔Bernadotte −2, Murat↔Bernadotte −2, Lannes↔Ney +1, Soult↔Massena +1…) supplies the relationship-scaled thresholds real fuel — hostile pairs are hair-triggered from turn 1.
- **Enemy pairs with authored rivalry:** Mack↔ArchdukeCharles (−2), Kutuzov↔Buxhowden (−1), Brunswick↔Hohenlohe (−1) — §9b enemy jealousy is live from boot. Single-marshal nations (Bavaria, Britain, Sweden, Naples, Denmark, Spain, Ottoman) have no same-nation target and simply never trigger.
- **No Devoted (+2) pair exists in the authored 1805 web** — the immunity rung is pinned by tests, reachable via play (battle-driven +1s) and future authoring.

### 0.2 Mechanics reconciliation (code truth over spec prose)

1. **Skills: there is no `fire` skill.** The 6-skill system is tactical/shock/defense/logistics/administration/command. **Crowned with Glory = +1 shock, +1 defense, +1 administration** (attack + defense + polity — the crowned marshal hits harder, holds firmer, administers better). Shock/defense ride `get_effective_skill` (combat reads it); administration rides an explicit crown bonus inside `get_recruit_cost_modifier` + `get_estate_stability_bonus` so the MC-1 Precision Execution +1 (combat-only by design) does NOT leak into Intendance/Steward tiers. Crown can flip admin 7→8 into the thrifty/steward tier while held — intended, shown = applied (card derives tiers from the same effective value). Crown never reduces a skill (clamp 10; the Precision min-8 cap is untouched).
2. **The temporary −1 is DERIVED, never mutated.** `Marshal.get_relationship(other)` — the chokepoint every mechanical reader uses (coordination scaling, objection SUPPORT, reinforcement eligibility + arrival, muster preview, enemy-AI ally filters, tooltip) — subtracts 1 while `jealous_of == other` (floor −2). Stored `relationships` are untouched; serialization untouched; restore-on-resolve is automatic. Escalation tier-2 permanent damage still mutates via `modify_relationship`. Known, accepted side-effect: the win/loss severity `rel_mod` reads the effective value while jealousy stands (the friction is real).
3. **Coordination direction fix:** the engine scales an ally's contribution by the RECEIVER's relationship. Jealousy must poison the pair both ways, so while either marshal of a pair is jealous of the other, the pair's scale reads through the WORSE direction (`min` of both effective views) — and an **aggressive** jealous marshal's pair scale is a hard 0.0 (spec §3). Authored MC-3 values are symmetric, so this changes nothing outside a live grievance.
4. **Glory recording** runs as a new step in `_post_combat_pipeline` immediately after the Win/Loss relationship step (EC-F ordering), covering all executor combat paths; the reckless-cavalry auto-charge block in `world_state` gets the same call after its own `process_battle_relationships`. Primary marshals score the full formula; non-primary participants (coordination/reinforcement) record base ±1 only. `is_garrison` ctx = the garrison-stomp discriminator (+0 for the attacker); defensive victories score normally (EC-A).
5. **Evaluation point:** ONE pass in `_advance_turn_internal` after the reckless auto-charge block stores `_last_tactical_events` and BEFORE `calculate_visibility()` — by then player actions, the enemy phase, strategic orders, and auto-combat have all resolved their battle relationships, and the Literal intel boost lands the same turn. The pass covers ALL nations (Building Blocks; no second enemy hook).
6. **Idle tracking extended to all nations.** `idle_turns` was player-only; the increment loop now covers enemy marshals too (hostile-threshold idle gate + accelerated thresholds need it; V2b consumers only ever read player marshals — pinned).
7. **Autonomous attack timing pin:** evaluation (end of turn T−1) sets `jealousy_autonomous_warned` + queues the dispatch warning → the player reads it at turn T start → ANY successful player command addressed to that marshal during turn T cancels the cycle (jealousy persists) → still-warned marshals fire at the TOP of `TurnManager.end_turn()` (before the enemy phase — he attacks as the turn closes; the enemy responds after). Execution = the HOLD-sally pattern: `executor.execute` with `_strategic_execution=True` (no AP, no objection, physical gates still apply) + `_jealousy_autonomous=True` for attribution. The marshal's "unavailability" is naturally consumed (he acts at end-turn). Post-victory advance stays enabled (glory-seekers take ground).
8. **Enemy autonomous attack (EC-N re-pin):** survival-first reading — the rung inserts in the enemy decision chain AFTER threat-response (P3), BEFORE the standard attack rung (P4), as "glory attack: weakest adjacent enemy." No advance warning (spec §9b).
9. **Enemy authority proxy** derives from `world.nation_starting_regions` + capital control (EC-M satisfied — reconstructible, not serialized). **Enemy Literal intel enhancement is a documented no-op**: fog is player-only; the enemy literal's jealousy still fires (relationship penalty, resolution arc, battle-report observability). This is the literal-AI follow-on decision the MC exit review routed here: enemy literals (Mack, Buxhowden, Deroy) participate in jealousy fully — Mack holding at Ulm while Charles maneuvers IS the sidelining trigger firing on schedule; his P7 hold behavior is unchanged (jealousy adds friction, never moves him).
10. **Confrontation + rivalry + Fontainebleau + war-weary all ride ONE popup channel:** `world.pending_marshal_petition` (kind-discriminated) + a `marshal_petition_popup` PopupQueue entry + POST `/marshal_petition_response` + ONE Godot scene (`marshal_petition_dialog`, dynamic option buttons, EC-I greying). One plumbing path = one wiring surface (the dialogue-popup-wiring bug class). The queue's one-popup-per-response arbitration implements the 1-popup/turn rate limit.
11. **Rate limiting is per-nation** (2 fires/turn/nation, most-aggrieved first, EC-J snapshot-then-apply).
11b. **Authority suppression SOFTENED to dampening (build amendment, live-probe driven):** boot authority is 100, so §1's ">70 suppresses entirely" left the whole system dormant for any winning campaign — contradicting the crown's own "reward for excellence creates friction" design (the marshals feuded at the height of empire; Auerstedt was 1806). Amended: authority > 70 adds +1 to every trigger threshold (winning calms the army, it doesn't anesthetize it); the <30 death-spiral acceleration and the capital-threatened full suppression are unchanged. The enemy proxy inherits the same shape (healthy factions dampen, broken factions accelerate).
12. **Glory window pruning:** `glory_events` prunes to the 5-turn window at evaluation (bounded list, GR8-safe).
13. **Serialized additions** (all with `.get()` defaults + SAVE_FORMAT_REFERENCE rows): Marshal — `jealous_of`, `jealousy_turns_remaining`, `jealousy_surge_turns`, `jealousy_autonomous_warned`, `glory_events`, `jealousy_history`, `consecutive_hold_turns`, `separation_flagged`, `glory_crowned`; World — `pending_marshal_petition`, `jealousy_confrontations_seen`, `rivalry_transitions_seen`, `fontainebleau_last_turn`.
14. **New actions cost:** none typed — jealousy has no player verbs (popup choices only). Promise Glory / Reassign charge 1 AP at response time (greyed at 0 AP, EC-I).

### 0.3 Rider contracts (the gate's owned deferrals, landing THIS build)

- **ESP-1 Fontainebleau petition:** trigger — ≥3 player marshals `is_eroding` on the same `_process_dotation_state` tick; latched (re-arms only after the eroding count drops below 3) + 8-turn minimum cooldown (`FONTAINEBLEAU_COOLDOWN`). Arms: **Concede** (grant each eroding marshal a rente at his current shortfall through the real `grant_pension` machinery, +2 trust each — the bills become next turns' problem, which is ESP-4's drama); **Refuse** ("The Empire does not beg" — trust −8 each eroding marshal, erosion continues); **Promise the next conquest** (grace extended 3 turns each via `expectation_grace_turn`, authority −2). Deterministic, popup-answerable, tested.
- **ESP-2 war-weary objection:** on the PLAYER's `diplomatic_declare_war` path, inserted directly after the Talleyrand-objection seam (same non-executing return pattern): a marshal with `get_satisfaction ≥ get_expectation` AND `get_expectation ≥ WAR_WEARY_EXPECTATION_FLOOR (160)` petitions against the NEW war ("I have my duchy, Sire — why do we march again?"). Highest-expectation qualifier speaks. **March anyway** → war executes via the stored order (bypass flag), objector trust −4; **Stand down** → nothing spent, objector trust +3. Fires once per (marshal, target-nation) pair (seen-set), never for poor marshals, never for AI declarations. (The DESIGN_REFINEMENT row suggested objection_v2; the petition channel supersedes it — the declare-war path never touches the marshal-objection seam, and the popup plumbing already exists here. Recorded deviation.)
- **ESP-4 rente default:** in `_process_dotation_state`, after income has applied: while a nation's treasury is negative and rentes remain, lapse the largest-face rente (pension→0), refund THIS turn's charge for it ("the payment bounced"), fire `RENTE_DEFAULTED` notification (player) + dispatch event + campaign log both sides (GR5). Shortfall machinery reopens naturally; re-grant after recovery is the tested path.

### 0.4 Landing record

**✅ BUILT COMPLETE July 11, 2026 — one session, backend commit `467c167` + the Godot/docs commit that follows it.** Sessions 1–4 landed together (the v3.1 session plan's walking skeleton through polish), plus the three riders and the recruitment phase.

- **New module `backend/game_logic/jealousy.py`** (~1,100 lines): glory scoring/window/ladder, triggers, apply/clear/escalation, battle-time resolution, crown recompute, the petition channel (build/queue/respond for all four kinds), autonomous attacks, Fontainebleau/war-weary helpers, card/ladder payload builders. `backend/game_logic/recruitment.py` (the Marshalate — see `MARSHAL_RECRUITMENT_SPEC.md`).
- **Wiring:** marshal.py (9 fields + serialization, derived −1 in `get_relationship`, solo/surge modifiers, `CROWN_SKILLS` in `get_effective_skill`, crown-aware `get_admin_with_crown` for Intendance/Steward), world_state.py (petition fields + serialization, all-nations idle loop, event-stash collection, Literal intel post-pass in `calculate_visibility`, reckless-block hooks, ESP-4 default pass, `marshal_pool`), turn_manager.py (autonomous attacks at end-turn top; `process_turn` after strategic orders), combat_executor.py (pipeline steps 9.5 resolution + 10.5 glory/rivalry, main-path inline resolution, coordination pair override, solo stamp, `jealousy_note` battle-report glue), executor.py (warned-cancel hook), enemy_ai.py (P3.9 glory attack + P1.75 commission rungs), diplomatic_executor.py (ESP-2 seam), dispatch/campaign_log/notifications/cooldown_manager/marshal_overview/main.py surfaces, parser/validation/llm_client/display_names/corpus for `recruit_marshal`, validator `marshal_pool` schema.
- **Godot:** `marshal_petition_dialog.tscn/.gd` (layer 114, data-driven options, EC-I greying, "Later" only for grievance/rivalry kinds), main.gd route + `/marshal_petition_response` POST, Generals screen "THE LAURELS OF THE ARMY" ladder header + per-card glory/grievance/feud/separation rows + the Commission bench view, battle-report `jealousy_note` render. Engine booted clean (0 SCRIPT ERROR); live-verified: overview payload (ladder 7 rows + bench 6), typed `commission Grouchy` through the LIVE-LLM pipeline to the honest treasury refusal, petition endpoint none-pending refusal.
- **Build decisions beyond §0.2/§0.3:** (a) authority dampening amendment (§0.2-11b — the 8-turn live probe showed boot authority 100 kept the system dormant); (b) `jealousy_history` carries the `__levels__` escalation dict (a 10th serialized shape inside the existing field — the mixed-shape serialization bug was caught by the new suite); (c) literal battle-resolution includes primary-attacker battles (enemy contact is the stated bar); (d) glory participants: primaries full formula, non-primaries base ±1; (e) reckless auto-charge path forgoes the territory glory bonus (capture resolves later in that block); (f) the confrontation popup's Promise/Reassign re-validates AP at response time (EC-I honesty both ends).
- **Tests:** `test_jealousy_v32.py` (107) · `test_estate_riders_esp.py` (22) · `test_marshal_recruitment.py` (34) + 5 corpus rows; consciously flipped pins recorded in the backend commit. Suite 12,958/3 at the backend commit; ruff clean.
- **Deferred (owned):** ESP-3 respect-by-treaty stays with its diplomacy-gate owner row (`DESIGN_REFINEMENT.md`); Jealousy §14's own exclusions (Council command, pride mechanic, Petition Chain/BALANCED) stand unchanged; the recruitment spec's §8 lists its own non-goals.

### 0.5 CA8-D3 GATE + LANDING RECORD (August 8, 2026 — the rival is a PERSON; authoritative where it amends §1/§6)

**Held under the user's delegated grant at the position-9 marshal-content slot** (the Aug-4
creative audit's routing: `DESIGN_REFINEMENT.md` §Creative Audit row CA8-D3). The measured
disease: `find_jealousy_target` recomputed from the rolling window alone, so **Murat's rival
changed four times in twelve turns** — the recurrence register CA8-8 built ("again", "for the
third time") almost never fired because the feud kept being re-cast; and the §6 confrontation
latch was **once per pair per CAMPAIGN**, so the channel spoke once on turn 1 and every later
escalation of the same feud passed without an audience. Both gate questions ruled **YES**:

- **Q1 — RIVAL MEMORY (amends §1 targeting).** Among peers STRICTLY ABOVE on the ladder, a man
  this marshal's envy has already fired on (any entry in the already-serialized
  `jealousy_history`) is preferred over the rung rule — most lifetime fires first, ties by
  worse relationship then alphabetical (the §1 tiebreak philosophy). First acquisition (no
  history above) keeps the one-rung-up rule **byte-identically**; a passed rival falls back to
  the rung rule (and passing still resolves with surge via the ladder-shift path); a fallen
  rival who RISES again re-fixes the old feud — Davout–Bernadotte stays Davout–Bernadotte for
  a whole campaign. Deeper standing gaps against a remembered high rival make the threshold
  check fire MORE readily, which is coherent (the feud self-reinforces) and needs no new
  constant. Single source `find_jealousy_target`; the restlessness pre-warning, the aggressive
  autonomous-attack targeting and the enemy proxy all inherit through the same call (GR5).
  `JEALOUSY_RIVAL_MEMORY` exists as the flip-experiment instrument, not a config surface.
- **Q2 — PETITION PER ESCALATION LEVEL (amends §6).** The confrontation latch widens from
  once-per-pair to **once per (pair, escalation level)**: keys `A|B@Ln` in the existing
  `jealousy_confrontations_seen` list (zero new serialized fields; a legacy bare pair key
  reads as "level 0 seen", so pre-gate saves get no duplicate level-0 petition but DO receive
  the new level-rise re-fires). Bounded at four confrontations per pair per campaign (levels
  0..3). `queue_confrontation_petition` gains the level and appends an escalation register to
  the body (level 1 "no longer a passing mood" / 2 "entrenched… unusual heat" / 3 "the feud is
  now mutual and the army knows it"); the §6 option arms are unchanged (the channel contract
  holds), `context.escalation_level` rides for the client. Forced mutual-spiral fires still
  never petition; enemy pairs still never petition.

**Measured at landing:** `test_jealousy_v32.py` (107) green unchanged — every no-history pin is
byte-identical by construction; **M1–M7 and the AI-intent `BASELINE_SERIES` held byte-identical
WITHOUT re-record** (a fact about the ambient board: its enemy re-fires evidently never had
history pointing at a different above-man than the rung rule chose; the flip flag stands ready
if a future series moves). One guard from the landing review: a remembered rival repaired to
**Devoted (+2) is skipped by the memory arm** — he is immune (THRESHOLDS None), so returning him
would let old friendship SHADOW a fresh non-immune rung target and suppress all new envy.
Tests: `tests/test_ca8_d3_rival_permanence.py` (19).

### 0.6 TUT-F5 ADDENDUM (August 8, 2026, same-day live report — the schoolroom is dormant; the Acknowledge arm states its terms)

The user drove The School of War hours after the Q2 landing and measured **five Soult
confrontations in three lesson turns** — the tutorial's authored Ney↔Soult −1 is an
escalation-qualified hair-trigger *by design*, and the per-level re-fire multiplied it inside a
twelve-turn syllabus that never explains the channel. Two amendments, record = STATUS top entry
+ `test_tutorial_school_fixes_2026_08_08.py`:

- **The tutorial world is jealousy-DORMANT.** `jealousy_dormant(world)`
  (`scenario_name == "tutorial"`, the TUT-F2 autosave discriminator) early-returns
  `apply_jealousy` and `_push_petition` — no grievance ever fires and no marshal petition of
  ANY kind (§6 / §6b / ESP-1 / ESP-2) queues on the lesson world; glory itself still accrues
  (the Generals screen stays honest). World-scoped, both sides together (GR5). Campaign worlds
  are pinned unchanged.
- **§6's Acknowledge detail is now honest about being a no-op** (the report: "it's unclear what
  acknowledge even does" — it does nothing, deliberately): *"Free, and it fixes nothing: the
  grievance stands N more turns — souring his ties and coordination with {target} — then cools
  on its own."* Shown = applied: N is the live `jealousy_turns_remaining` countdown and the
  tie/coordination clause is the §8 derived −1. Promise/Rebuke details already stated their
  numbers and are unchanged.

---

## Design Philosophy

"Jealousy makes marshals self-serving, not passive." They don't do less — they pursue their own agenda. Every personality type feels jealousy. What differs is how they act on it. The system routes through existing mechanics (relationships, coordination, defiance, objections) rather than creating parallel penalty tracks.

Historical anchor: Marshal rivalries were Napoleon's constant headache. Ney and Davout despised each other. Murat's cavalry charges were driven by personal glory, not strategy. Soult in Spain built his own kingdom rather than cooperate. Bernadotte at Jena refused to march to the sound of guns out of jealousy of Davout. In the Peninsula, Napoleon's marshals were so consumed by rivalry that Wellington's greatest advantage was that his enemies couldn't work together. These weren't failures of skill — they were failures of ego management. That's the player's job.

**Terminology note:** The system is called "jealousy" for Aggressive/Cautious personalities (glory-based resentment). For Literal personalities, the trigger is sidelining resentment (being overlooked for meaningful assignments), not glory envy. Both route through the same mechanical framework. "Marshal grievance" is the umbrella term; "jealousy" is the common shorthand.

---

## 1. Trigger: Glory Ladder

### Glory Tracking (replaces simple win count)

Track a **glory score** per marshal, not raw battle wins. Rolling 5-turn window. Glory captures *magnitude* of achievement — a marshal who won two garrison stomps shouldn't trigger jealousy in one who won a decisive pitched battle.

```
Glory from VICTORIES:
  Base:             +1 per victory
  Decisive win:     +1 bonus (casualty ratio >= 2:1 in your favor)
  Territory taken:  +1 bonus (captured a region this battle)
  Outnumbered:      +1 bonus (won when enemy had more troops)
  Garrison stomp:   +0 (defeating a garrison — no glory in that)

Glory from DEFEATS (v3.1 — keeps the ladder dynamic):
  Base:             -1 per defeat
  Decisive loss:    -1 extra (casualty ratio >= 2:1 against you — humiliation)
  Territory lost:   -1 extra (lost a region this battle)
  Outnumbered loss: +0 reduction (no shame in losing to superior numbers)
  Garrison defense: -0 (garrison losses are expected, no dishonor)
  Garrison ASSAULT repulsed: -0 — CANONIZED Aug 7, 2026 (CA8-19 close-out
    gate 10.5). The ladder prices reputation between COMMANDERS; an
    escalade has no opposing commander to lose face against, and the
    repulse's cost is already paid in men and materiel. This retires the
    sweep-4 "recorded divergence" as design, not debt — step 9.5 stays
    gated on the garrison path.

  Floor: A marshal's glory score cannot go below 0.
```

Losses keep the ladder fluid — you can fall as well as rise. A string of defeats drops you, potentially making you jealous of someone who passed you. A cautious marshal who avoids battle preserves glory; a reckless one who loses bleeds it. But losing while outnumbered carries no stigma — the shame is in losing battles you should have won.

Each glory event is stored as `(turn_number, glory_points)` where points can be negative. At evaluation, sum points within the 5-turn window (floor at 0).

### The Glory Ladder (v3 — replaces dogpile targeting)

Marshals don't all resent the top performer. Each marshal looks at the person **one rung above them** on the glory ranking. This distributes jealousy across different pairs instead of concentrating it on a single target.

```python
def find_jealousy_target(marshal, world):
    """Find the marshal directly above on the glory ladder."""
    same_nation = [m for m in world.marshals.values()
                   if m.nation == marshal.nation
                   and m.name != marshal.name
                   and m.strength > 0
                   and not getattr(m, 'broken', False)
                   and not getattr(m, 'retreated_this_turn', False)]

    my_glory = get_glory_score(marshal, world.current_turn)

    # Find marshal with lowest glory that's still above mine
    target = None
    target_glory = float('inf')
    for m in same_nation:
        m_glory = get_glory_score(m, world.current_turn)
        if m_glory > my_glory and m_glory < target_glory:
            target = m
            target_glory = m_glory

    return target  # None if marshal is at the top
```

**Example with 4 marshals:**
```
Glory rankings this window:
  1. Davout    — 7 glory  → TOP OF LADDER (no jealousy target)
  2. Ney       — 4 glory  → jealous of Davout (delta 3)
  3. Drouot    — 2 glory  → jealous of Ney (delta 2)
  4. Grouchy   — 0 glory  → jealous of Drouot (delta 2)
```

Three DIFFERENT rivalries instead of everyone piling on Davout. Each pair has its own dynamics, resolution path, and escalation history.

### Top of Ladder Buff — "Crowned with Glory"

The marshal at the top of the glory ladder gets **+1 to all core stats** (shock, fire, admin) while they hold the position. This is a meaningful power spike — it literally levels them up. The buff transfers when someone else takes the top spot.

```
While #1 on glory ladder (glory > 0):
  +1 shock, +1 fire, +1 admin

Implementation: Route through get_effective_skill() — derivable from glory
  ladder position. No new persistent field needed. Buff is transient:
  recalculated each turn from current ladder state.

Self-balancing: Being on top makes others jealous of you (they see the
  delta). The reward for excellence creates friction. Historically accurate —
  Napoleon's most decorated marshals were the most resented.

Announced in Morning Dispatch when the top position changes:
  "Berthier notes that Davout's recent victories have made him the
   most celebrated commander in the army. (+1 shock, +1 fire, +1 admin)"
```

### Ties on the Ladder

Tied marshals don't trigger jealousy toward each other (delta = 0). When a marshal below ties looks up, tiebreaker: target the tied marshal they have the **worse relationship** with. If relationships are also tied, either is valid (implementation picks first alphabetically or by marshal dict order).

### Trigger Conditions

```
glory_delta = target.glory_score - self.glory_score

Threshold varies by RELATIONSHIP with target (v3):
  Devoted (+2):     IMMUNE — never triggers (they celebrate each other's wins)
  Friendly (+1):    delta >= 4 (very resistant — takes major imbalance)
  Professional (0): delta >= 2 (standard threshold)
  Rival (-1):       delta >= 1 (already resentful — hair trigger)
  Hostile (-2):     delta >= 1 AND idle >= 2 turns (hair trigger)

Accelerated: when self.idle_turns >= 3 consecutive, threshold drops by 1
             (minimum threshold: delta >= 1)
```

**Literal personality uses a DIFFERENT trigger** — see §3.

### Authority Polarity (FLIPPED from draft v1)

Low authority ACCELERATES jealousy. High authority SUPPRESSES it. This mirrors history — Napoleon's marshals were at each other's throats during the Hundred Days precisely because they were losing. When things go badly, everyone looks for someone to blame.

```
Authority > 70:  Suppresses jealousy entirely (winning cures ego problems)
Authority < 30:  Accelerates jealousy (all thresholds drop to delta >= 1, idle >= 2 turns)
Capital threatened (enemy in capital or adjacent): Suppresses (survival overrides pettiness)
```

This creates a historically accurate death spiral: losing breeds infighting, which breeds more losing. The player must actively manage morale WHILE losing.

### Additional Suppression Conditions

Jealousy is suppressed (never fires) when:
- Target marshal is currently broken or retreating
- Source marshal is currently broken or retreating
- Relationship with target is Devoted (+2) — immune

### Evaluation Timing

Checked at **end of turn** during `advance_turn()`, after battle results are processed and `process_battle_relationships()` has run. This ensures battle outcomes are fully resolved before jealousy evaluation.

### Rate Limiting (v3)

To prevent popup avalanches at large roster sizes (8-12 marshals in 1805):

```
Per turn limits:
  Max jealousy FIRES per turn:          2 (even if 4 marshals cross threshold)
  Max confrontation POPUPS per turn:    1 (first-time confrontations queue)
  Max autonomous WARNINGS per turn:     1 (most urgent only)

  Overflow: remaining triggers fire on subsequent turns,
            highest glory delta first (most aggrieved marshal goes first)
```

---

## 2. Scaled Duration

Duration scales with the glory delta that triggered jealousy. A barely-triggered flare-up is different from a festering wound.

```
duration = 2 + (glory_delta - threshold)
  Minimum: 2 turns
  Maximum: 5 turns

Examples:
  delta=2 (barely triggered at default threshold): 2 turns
  delta=3: 3 turns
  delta=4: 4 turns
  delta=5+: 5 turns (cap)
```

Timer counts down each turn. At 0, jealousy expires (with no resolution surge — timer expiry is NOT the "I showed them" moment). Resolution via action clears immediately regardless of remaining timer.

### Ladder Shift Resolution (v3)

If a jealous marshal **passes their target on the glory ladder** (earns more glory than them), jealousy resolves immediately. They got what they wanted — they proved themselves. This counts as action resolution (surge buff applies).

**Important:** The escalation counter still ticks. Even though this instance resolved naturally, the lifetime jealousy history between the pair records it. Three lifetime triggers still leads to permanent damage. Passing someone on the ladder fixes the moment but doesn't erase the pattern.

---

## 3. Personality Expressions

Each personality type expresses jealousy differently. The core output is always a **temporary relationship degradation** (-1 toward the glory target), which flows through existing coordination, objection, and defiance systems automatically. On top of that, each personality has a unique behavioral expression.

### Aggressive (Ney)

**Expression:** Autonomous glory-seeking attack. Hot, loud, dangerous — to enemies AND to your plans.

- **Autonomous attack** against a nearby enemy (glory-seeking target priority — see §7)
- **No AP cost** — the marshal acts on his own initiative. Napoleon doesn't authorize it, so it doesn't consume his administrative capacity. The cost is the marshal's **unavailability** for the rest of the turn (committed to his attack, can't receive new orders). (v3 change: removed AP cost from v2)
- **+15% attack modifier** on solo attacks while jealous (jealousy as fuel — this is INTENDED as a valid strategy, not an exploit)
- **0% coordination** with the jealousy target (refuses to cooperate — hard override regardless of relationship math)
- If no valid attack target exists: just the relationship penalty, no autonomous action
- Autonomous attack is **announced 1 turn in advance** via Morning Dispatch (see §7)

**Resolution:** Win a battle where enemy strength >= 70% of yours (no stomps). OR pass target on the glory ladder (§2). Cleared immediately on qualifying victory.

### Cautious (Davout, Drouot)

**Expression:** Withholds full cooperation. Technically present in coordination but doesn't commit full strength. Cold, professional, lasts longer.

- Coordination contribution scaled to **50%** via temporary relationship downgrade (-1)
- No solo bonus — Cautious marshals don't seek glory, they withhold it
- Campaign log flavor: critical reports undermining the rival

**Resolution (v3 — softened):** Shared victory with the jealousy target (both marshals participate in the same winning battle). OR participate in any coordinated battle with **2+ same-nation allies present** and win (proving you're a team player, not just resentful). OR pass target on the glory ladder (§2). Time alone doesn't fix it — they need proof of cooperative competence.

### Literal (Grouchy) — CANDIDATE B SELECTED (v3)

**Expression: "The Vindicated Garrison" (Obsessive Competence)**

Grouchy's actual pursuit of the Prussians was competent. He found them, engaged them at Wavre, did his job. The catastrophe was that his excellent work on the wrong objective meant he wasn't where Napoleon needed him. The failure was strategic, not tactical. Jealous Grouchy recreates this exact dilemma.

**Trigger:** DIFFERENT from other personalities. Literals don't care about glory — they care about being treated as competent. Literal jealousy triggers when the marshal has been on **HOLD or garrison duty for 3+ consecutive turns** while other same-nation marshals are actively engaged. They resent being sidelined, not outshone.

**"Actively engaged" means:** At least one other same-nation marshal has an active non-HOLD strategic order (MOVE_TO, PURSUE, SUPPORT) OR received a tactical attack/move command this turn. If ALL marshals are idle/on HOLD, Grouchy doesn't feel sidelined — everyone's waiting. The trigger is differential treatment, not absolute inactivity.

**Three effects:**
- **Intel Enhancement** (`calculate_visibility`) — Grouchy's scouting output increases. Adjacent regions get boosted visibility (PARTIAL -> FULL, UNKNOWN -> PARTIAL). He's sending out extra patrols, mapping enemy supply lines, tracking movements. The player gets *better* intelligence from Grouchy's sector than anywhere else.
- **Reassignment Dispatch** (popup pattern) — When the player issues a strategic order to move Grouchy away, a dispatch popup appears. Not an objection (Literal never objects) — an intelligence briefing. Grouchy reports what he's found: enemy positions, supply lines, strategic value of his sector. Player acknowledges, order proceeds. But the information makes them *think* about whether pulling him is the right call.
- **Intel Withdrawal** (`calculate_visibility`) — If the player reassigns Grouchy, enhanced intel from his sector immediately drops to normal. Player *feels* the loss. No new system needed; the boost just stops.

**The dilemma:** Grouchy is doing something useful that you didn't ask for. Do you:
- **Leave him** — benefit from enhanced intel, but he stays jealous and relationship penalty persists
- **Pull him out** — resolve jealousy by giving him a real mission, but lose the best intelligence source on the map

**Upside:** Enhanced intel is genuinely valuable. Some players may WANT Grouchy jealous.
**Downside:** Relationship penalty persists. He's "stuck" being excellent at the wrong thing.

**Why Candidate B over A:** Evaluated against 6 criteria — Candidate B passed all 6, Candidate A passed only 3. Candidate A (Silent Front) was purely punitive with no duality, no interesting decision, and made the least-exciting marshal even worse. Candidate B creates a genuine tradeoff. See §15 Appendix for full evaluation and all candidates considered.

**Note on "reassignment dispatch":** This is NOT an objection. The order proceeds regardless. It's a briefing/report — Literal marshals don't say "no," they say "here's what I've found, your order proceeds as you command." No objection UI, no trust/insist/compromise — just an informational popup the player acknowledges.

**Resolution (v3 — tightened, requires enemy contact):**

Resolution requires proof of meaningful service, not trivial logistics. Walking to an adjacent region doesn't prove Napoleon trusts Grouchy with real work. **Enemy contact is required:**

```
Resolution requires ENEMY CONTACT:

  PURSUE  -> engage target (actually fights, regardless of outcome)
  SUPPORT -> participate in a battle alongside supported marshal
  Defend position against enemy attack (survives, not broken)
  Any battle participation while on a strategic order

  MOVE_TO alone does NOT clear (walking isn't a mission, it's logistics)
  HOLD does NOT clear (that's what caused the jealousy)
  Timer expiry is safety valve only (no surge buff)
```

The one passive resolution path: if Grouchy's position is attacked while he's jealous and he holds (not broken/retreating), that clears it. The enemy validated his post — he didn't need to go find meaning, meaning found him.

---

## 4. Resolution Surge Buff

When jealousy resolves via **action** (not timer expiry), the marshal gets a 1-turn "I showed them" buff. This turns jealousy into a narrative arc with a payoff — not just a penalty to remove, but a story with a conclusion.

| Personality | Surge Buff (1 turn) |
|---|---|
| Aggressive | +10% attack |
| Cautious | +10% defense |
| Literal | Intel enhancement persists for 1 additional turn after jealousy resolves (enhanced patrols don't stop instantly) |

---

## 5. Berthier Pre-Warning ("Restlessness")

When glory delta reaches `threshold - 1` (one win away from triggering), add a Morning Dispatch line. For Literal, when HOLD/garrison duration reaches 2 consecutive turns. This gives the player agency to **prevent** jealousy, not just react to it.

**Aggressive/Cautious:**
> *"Berthier notes that Ney has grown restless. He has not seen action while Davout wins laurels. I recommend giving him meaningful orders soon."*

**Literal:**
> *"Berthier notes that Grouchy has been holding position for some time while others receive commands. He may begin to feel... overlooked."*

**Target notification (v3):** When a marshal becomes the target of jealousy, a Morning Dispatch note informs the player (informational only, no mechanical effect on the target):
> *"Berthier notes that your recent victories have attracted... attention among the marshals. Ney in particular seems restless."*

Being good at your job should never be punished mechanically. The target gets no penalties — just awareness that their success is causing friction.

Berthier closing note priority: Below broken/bankrupt/bleeding treasury, above idle_restless/all-ready.

---

## 6. Jealousy Confrontation Popup

When jealousy fires for the **first time** between two marshals, create a popup event (using the existing objection popup pattern in `executor.py` -> `main.py` -> Godot).

### v3 Changes: Promise Glory simplified, all options have randomness

**Aggressive:**
```
"Sire, Ney has expressed... displeasure about Davout's recent recognition.
 He requests a command worthy of his talents."

[Acknowledge]     — Jealousy proceeds normally. No cost.

[Promise Glory]   — Costs 1 AP. Duration reduced by 2 turns (not 1).
                    No broken promise mechanic — simpler, still meaningful.
                    (v3: removed 2-turn deadline trust trap. Player rarely
                    controls whether qualifying battles happen in time.)

[Rebuke]          — Trust -5 immediately. Duration -1 turn. Aggressive
                    won't launch autonomous attack this cycle (respects
                    the Emperor's anger, briefly).
```

**Cautious:**
```
"Sire, Davout has expressed reservations about the recognition afforded
 to Ney. He requests that his contributions be... noted."

[Acknowledge]     — Jealousy proceeds normally. No cost.

[Promise Glory]   — Costs 1 AP. Duration reduced by 2 turns.
                    No broken promise mechanic.

[Rebuke]          — Trust -5 immediately. Duration -1 turn. No additional
                    mechanical effect (Cautious already internalizes).
```

**Literal:**
```
"Sire, Grouchy's dispatches have become unusually detailed — obsessively
 so. Staff report he feels his current assignment is... beneath his abilities."

[Acknowledge]     — Jealousy proceeds normally. No cost.

[Reassign]        — Costs 1 AP. Duration reduced by 2 turns.
                    No broken promise mechanic.

[Rebuke]          — Trust -5 immediately. Duration -1 turn. Intel
                    enhancement pauses for 1 turn (reluctant compliance
                    before obsessive scouting resumes).
```

Subsequent jealousy triggers between the same pair use the standard popup-free flow (just Morning Dispatch events). Only the FIRST occurrence gets the confrontation choice.

### Confrontation Popup Timing

The confrontation popup appears at the **start of the NEXT turn** (during Morning Dispatch phase), not during the turn jealousy fires. Jealousy evaluation runs at end-of-turn; showing a popup mid-evaluation would interrupt the player's mental model. Start-of-turn is when the player is already processing information and making decisions.

---

## 6b. Rivalry Confrontation Event (v3 — DEFERRED TO v3.1)

> **DEFERRED:** Full probability tables, authority-gated mediation, and "Separate Them" persistence flag deferred to v3.1 implementation. Relationship transitions already have mechanical consequences through coordination/objection/defiance systems — the confrontation event adds narrative flavor, not core gameplay. Implement after jealousy core (Sessions 1-3) is playtested.

Separate from jealousy confrontation. Fires when a relationship **transitions** downward: Professional(0) -> Rival(-1) or Rival(-1) -> Hostile(-2). Creates a dramatic moment with player agency and randomness on all options.

### Professional -> Rival (0 -> -1)

```
"Sire, harsh words were exchanged between Ney and Davout
 before the general staff."

[Let Them Sort It Out]
    70% -> no change (they simmer down, rivalry stands)
    20% -> relationship degrades further to -2 (it escalates without you)
    10% -> relationship restores to 0 (they work it out themselves)
    Personality weight: Cautious marshals more likely to simmer (80/15/5).
                        Aggressive marshals more likely to escalate (50/40/10).

[Mediate]  — Costs 1 AP
    Authority >= 70:  70% restore, 30% no change
    Authority 40-69:  40% restore, 50% no change, 10% both trust -3
                      (they resent your interference)
    Authority < 40:   20% restore, 40% no change, 40% authority -3
                      (they ignore you publicly — humiliating)

[Reprimand Both]  — Trust -3 on BOTH marshals, always.
    60% -> relationship restores to 0 (anger redirected at you)
    30% -> no change (they resent you AND each other)
    10% -> one marshal's trust drops an EXTRA -5
           (took the reprimand personally — personality weighted:
            Aggressive = rage, Cautious = cold withdrawal)
```

### Rival -> Hostile (-1 -> -2)

Higher stakes, worse odds, more dramatic:

```
"Sire, Davout has refused to attend council where Ney is present.
 The breach may be beyond repair."

[Accept the Breach]
    80% -> stays Hostile (they settle into cold war)
    20% -> one marshal becomes "discontented" — elevated defiance
           chance for 3 turns (mini-jealousy without the full system)

[Force Reconciliation]  — Costs 2 AP
    Authority >= 80:  50% restore to -1, 50% no change
    Authority 60-79:  30% restore to -1, 50% no change,
                      20% authority -3 (failed publicly)
    Authority < 60:   10% restore, 30% no change,
                      60% authority -5 (catastrophic — "the Emperor
                      begged and they refused")

[Separate Them]  — No AP cost. No relationship change.
    Adds a persistent flag: Morning Dispatch warns if both
    marshals are ever in the same region or adjacent.
    Not a fix — a management tool. The coward's option, but
    sometimes the smart one.
```

### Design Notes

- Fires ONCE per transition per pair (not every turn they're Rival/Hostile)
- No guaranteed outcomes — every option has uncertainty
- Authority gates probability bands, personality weights outcomes within those bands
- The player should be able to estimate odds but never be certain
- "Separate Them" at Hostile is the management tool: doesn't fix anything, but helps the player avoid consequences. Exactly what Napoleon did historically — assigned feuding marshals to different fronts.

---

## 7. Autonomous Attack Target Priority (Aggressive Only)

When a jealous Aggressive marshal launches an autonomous attack, target selection follows glory-seeking logic — not strategic logic:

```
Priority:
  1. Weakest adjacent enemy (easiest glory — desperate, not smart)
  2. Any adjacent enemy
  3. No target available -> no autonomous action (just relationship penalty)

NOT: the strategically optimal target
NOT: the strongest enemy (they want glory, not death)
```

> **v3.1 CUT:** "Steal target's glory" (attack enemy the target recently defeated) removed. Required tracking which enemies each marshal defeated — untracked state. Weakest adjacent is sufficient glory-seeking behavior.

**Advance Warning:** Autonomous attack is announced **1 turn in advance** via Morning Dispatch turn events:

> *"Ney is eyeing the Austrian position at [region]. I cannot guarantee he will wait for orders."*

The player gets 1 turn to redirect with new orders (costs AP to issue an order to the marshal). If they don't, the autonomous attack fires next turn. If the player issues ANY order to the jealous marshal (even "hold"), the autonomous attack is cancelled for that cycle (but jealousy persists).

**No AP cost (v3):** The autonomous attack does NOT consume the player's AP. The marshal acts on his own initiative — Napoleon didn't authorize it, so it doesn't cost administrative capacity. The cost is the marshal's **unavailability**: he's committed to the attack for the turn and cannot receive new orders. His autonomous action occupies his turn, not yours.

---

## 8. Relationship Integration

Jealousy's primary mechanical output is a temporary relationship degradation (-1 toward the glory target). This cascades through existing systems automatically:

```
Jealousy fires
  -> Relationship toward target: -1 (temporary, restored on resolution)
  -> This automatically triggers:
     +-- Coordination penalty (via _RELATIONSHIP_SCALING in executor.py)
     |     Professional(0) -> Rival(-1): contribution drops from 100% to 50%
     |     Rival(-1) -> Hostile(-2): contribution drops to 0%
     +-- SUPPORT objection (via _evaluate_relationship_support in objection_v2.py)
     |     Hostile target = STRONG concern (Aggressive) or MODERATE (Cautious)
     +-- Elevated defiance chance (existing modifiers in defiance.py)
```

**Important:** The relationship change is TEMPORARY. It's restored when jealousy resolves. This distinguishes jealousy (transient emotional state) from genuine relationship degradation (permanent, from battle outcomes). Track the temporary modifier in a separate field from the permanent relationship value.

**Hostile floor edge case (v3 — explicit):** When the relationship is already Hostile (-2), the temporary -1 modifier has no further relationship effect (already at floor, can't go below -2). Jealousy still fires its personality-specific expression (autonomous attack, coordination withholding, intel enhancement) and still requires resolution. The relationship cascade is already maxed out, but the behavioral expression and resolution arc still apply.

**Note:** Literal marshals still get the temporary relationship degradation. Even though their expression is informational rather than interpersonal, the resentment affects how they interact with the marshal who's getting all the "real" assignments.

---

## 9. Trust Policy

Jealousy is marshal-vs-marshal, NOT marshal-vs-Napoleon. **No trust changes** on jealousy fire or resolution.

**Exception:** The Confrontation Popup choices (§6) can affect trust as part of the player's explicit decision:
- [Rebuke] -> trust -5 immediately
- Rivalry Confrontation choices (§6b) may affect trust based on randomness

This keeps trust changes as consequences of player CHOICES, not automatic penalties.

---

## 9b. Enemy Jealousy — Building Blocks (v3)

Jealousy is marshal-to-marshal, not marshal-to-Napoleon. There is no narrative reason enemy marshals would be immune to internal rivalry. Exempting the enemy gives the AI a structural advantage — their coordination never degrades from internal friction while the player's does. This violates Building Blocks.

### Principle

Enemy marshals get the **mechanical core** of jealousy (same formulas, same relationship effects, same timers). They don't get the **player-facing layer** (confrontation popups, Berthier warnings, promise/rebuke choices). The AI doesn't need UI — it needs the same friction.

### What Enemy Marshals GET (same as player)

```
- Glory ladder evaluation (same formula, same thresholds)
- Relationship-scaled trigger thresholds (Devoted immune, etc.)
- Temporary -1 relationship on jealousy fire
  -> Cascades through coordination automatically (already Building Blocks)
  -> Cascades through reinforcement arrival scores (already Building Blocks)
- Duration timer (same 2-5 turn scaling)
- Resolution conditions (same per-personality)
- Ladder shift resolution (passing target clears it)
- Escalation system (lifetime history, permanent damage, mutual)
- Suppression conditions (broken, retreating, capital threatened)
- Glory recording after battles (same formula)
```

### What Enemy Marshals DON'T Get (player-only UI)

```
- Confrontation popup (no one to show it to)
- Promise/Rebuke/Acknowledge choices (no Napoleon to decide)
- Berthier pre-warnings (Berthier works for the player)
- Autonomous attack advance warning (player doesn't need to prevent it)
- Rivalry Confrontation event (§6b) — player-only management tool
- Literal reassignment dispatch (player-only briefing)
```

### Authority Polarity for Enemy

Player jealousy uses `world.authority_tracker.authority`. Enemy marshals don't have an authority tracker. Use a **faction-level proxy**:

```
Enemy authority proxy:
  Faction controls capital + majority of home regions: 70+ (suppresses)
  Faction lost capital OR lost majority of home regions: <30 (accelerates)
  Otherwise: 50 (neutral)
```

This means: enemy factions that are losing start having internal friction, just like the player. Enemy factions that are winning stay unified. Historically accurate — coalitions fractured when losing, held together when winning.

### AI Behavior Under Jealousy

No special AI code needed for most effects — existing systems handle it:

- **Coordination degradation:** The coordination system already reads relationships. A -1 relationship from jealousy automatically reduces coordination bonuses for that enemy pair. Zero new code.
- **Reinforcement:** Arrival scores already use relationship modifiers. A jealous enemy marshal is less likely to reinforce their rival. Zero new code.
- **Aggressive AI marshals:** The AI's existing action selection already favors attacking for aggressive personalities. The +15% solo buff applies via `get_attack_modifier()`. The AI may organically send the jealous marshal to a different front (P4.75 already skips Hostile marshals for support).
- **Resolution:** Enemy battles already fire `process_battle_relationships()`. Jealousy resolution checks hook into the same post-battle processing. Shared victories and decisive wins resolve enemy jealousy naturally through gameplay.

### What the Player SEES

Enemy jealousy creates **opportunities** the player can observe and exploit:

**Battle reports (always visible after combat):**
> *"Berthier observes that the enemy coordination was uncharacteristically poor. Wellington's support from Blucher seemed... reluctant."*

**Morning Dispatch (fog-filtered, requires PARTIAL+ visibility on enemy marshals):**
> *"Intelligence suggests friction among the enemy marshals. Their coordination may be compromised."*

**Strategic implication:** If the player notices enemy jealousy through intel, they can:
- Attack when enemy coordination is degraded
- Target the pair with the worst relationship
- Time an offensive for when enemy internal friction is peaking
- Deliberately create glory imbalances by fighting one enemy marshal repeatedly while ignoring another (at 1805 scale with non-Devoted enemy pairs)

### Current Scenario Impact

In the Waterloo scenario specifically, enemy jealousy rarely fires:
- Wellington and Blucher are Devoted (+2) — **immune**
- Other Coalition marshals (Uxbridge, Gneisenau) are Professional or better with their leads
- Austrian marshals (ArchdukeCharles, Schwarzenberg) and Saxon Reynier have no jealousy relationships yet

The system matters more at 1805 scale where Austria might have 4-5 marshals with real rivalry potential, and where the player can strategically exploit enemy friction. Implementing now ensures Building Blocks compliance and prevents a structural rewrite later.

---

## 10. Escalation System

### Escalation Triggers

Escalation activates when:
- Jealousy fires AND current relationship is already **Rival (-1) or worse**
- OR jealousy fires for the **3rd time EVER** between this pair (lifetime count, not windowed)

**Note:** Ladder shift means the same pair might not always trigger each other (if a third marshal enters the gap). But the lifetime history tracks ALL jealousy instances between a specific pair regardless of how they were triggered.

### Progressive Effects

**1st escalation:** Berthier warning in Morning Dispatch.
> *"Sire, the rivalry between Ney and Davout has become a matter of concern among the general staff. Their cooperation cannot be relied upon."*

**2nd escalation:** Permanent -1 relationship (does NOT restore on jealousy resolution). This feeds into SUPPORT objections and coordination penalties permanently.

**3rd escalation:** Mutual jealousy — if A becomes jealous of B again, B **automatically** becomes jealous of A regardless of glory ladder position. B's jealousy target is forced to A specifically (overrides normal ladder lookup). B gets full personality expression (autonomous attack if Aggressive, etc.). Creates the Ney-Davout spiral. The player's only option is to physically separate them (assign to different fronts) or accept permanent friction.

### Escalation Tracking

```python
# Per-marshal, per-target: lifetime list of turn numbers when jealousy fired
jealousy_history: Dict[str, List[int]]  # target_name -> [turn_5, turn_8, turn_22]

# Escalation level derived from len(history[target])
# Level 0: count < 3 (or relationship >= Professional)
# Level 1: first escalation trigger
# Level 2: second escalation trigger
# Level 3: mutual jealousy active
```

---

## 11. Surface to Player

### Morning Dispatch

New event types added to dispatch event whitelist:

| Event | When | Message |
|---|---|---|
| `jealousy_restlessness` | Pre-warning (§5) | "Berthier notes that {name} has grown restless..." |
| `jealousy_fired` | Jealousy activates | "Berthier reports that {name} appears envious..." |
| `jealousy_autonomous_warning` | Aggressive advance notice (§7) | "{name} is eyeing the position at {region}..." |
| `jealousy_target_notice` | Target informed (§5, v3) | "Your recent victories have attracted attention..." |
| `jealousy_escalation` | Escalation triggers (§10) | "The rivalry between {a} and {b} has become..." |
| `jealousy_resolved` | Resolved via action | "{name}'s grievance appears satisfied." |
| `jealousy_surge` | Resolution surge active | "{name} fights with renewed purpose." |
| `jealousy_ladder_shift` | Jealous marshal passed target | "{name} has proven himself. The grievance fades." |

Berthier closing note priority: Below broken/bankrupt/bleeding treasury, above idle_restless/all-ready.

### Campaign Log

New event type `jealousy` added to `CAMPAIGN_LOG_TYPES` under "command" category.

Variants per personality:
- Aggressive: "Ney, envious of Davout's victories, grows restless for glory."
- Cautious: "Davout has grown distant toward Ney. Staff report reduced cooperation."
- Literal: "Grouchy throws himself into garrison work with obsessive diligence."
- Escalation: "The rivalry between Ney and Davout has become entrenched."
- Resolution: "Ney's victories have restored his spirits. He fights with renewed vigor."
- Ladder shift: "Ney has surpassed Davout in recent glory. The resentment fades."
- Rivalry confrontation: "Harsh words between Ney and Davout. The Emperor intervened."

### Battle Report

If a jealous marshal participated in a battle, Berthier observations (P6c in `battle_report.py`) should note:

- Aggressive in solo attack: "Ney fought with particular ferocity — though one wonders if it was for France or for himself."
- Aggressive with +15% buff visible: "His jealousy made him dangerous. Whether that danger serves us remains to be seen."
- Cautious withheld coordination: "Davout's support was... measured."
- Literal in battle (defending garrison): "Grouchy defended his post with an intensity suggesting something to prove."
- Literal intel contribution: "Grouchy's enhanced patrols provided crucial intelligence on the enemy approach."

### Notifications

New notification types:
- `JEALOUSY_CONFRONTATION` (HIGH priority) — first-time jealousy confrontation popup
- `RIVALRY_CONFRONTATION` (HIGH priority) — relationship transition event (§6b)

Uses existing `NotificationCollector` and popup patterns.

---

## 12. New Marshal Fields

```python
# In marshal.py __init__

# ======= JEALOUSY SYSTEM =======
self.jealous_of: Optional[str] = None          # target marshal name, or None
self.jealousy_turns_remaining: int = 0          # countdown timer
self.jealousy_surge_turns: int = 0              # resolution surge countdown (1 = active)
self.jealousy_autonomous_warned: bool = False   # True = advance warning given, attack fires next turn

# Glory tracking
self.glory_events: List[Dict] = []              # [{turn: int, points: int}] — rolling 5-turn window

# Escalation
self.jealousy_history: Dict[str, List[int]] = {}  # target_name -> [turn_numbers] lifetime

# Literal-specific
self.consecutive_hold_turns: int = 0            # HOLD/garrison consecutive turn counter

# Rivalry management (§6b)
self.separation_flagged: Dict[str, bool] = {}   # marshal_name -> True if "Separate Them" chosen
```

### Fields Removed (v3 — derivable, reduce serialization)

These fields from v2 are **derivable** and should NOT be serialized:

- `jealousy_relationship_modifier` — always -1 when `jealous_of is not None`, 0 otherwise. Derive from `jealous_of` state.
- `jealousy_confrontation_response` — only matters for the confrontation popup turn. Handle as transient in executor flow, not a persistent field.
- `jealousy_promise_deadline` — removed entirely (Promise Glory no longer has a deadline mechanic).

All remaining fields MUST be added to `to_dict()` and `from_dict()` with `.get()` defaults. Run `test_serialization_enforcement.py` after.

---

## 13. Implementation Plan

### Walking Skeleton (Minimum Viable Jealousy)

80% of gameplay value with ~40% of implementation cost:

1. Glory tracking + ladder ranking
2. Trigger evaluation (relationship-scaled thresholds)
3. Aggressive expression: autonomous attack (the signature moment)
4. Temporary -1 relationship (cascades through existing coordination/objection automatically)
5. Duration timer + resolution conditions
6. Berthier pre-warning + fire notification

This skeleton is playtest-able before building confrontation popups, escalation, or enemy building blocks.

### Files to Modify

| File | Changes |
|------|---------|
| `backend/models/marshal.py` | New fields (§12), serialization, `clear_jealousy()` / `get_glory_score()` helpers |
| `backend/models/world_state.py` | Jealousy evaluation in `advance_turn()`, glory window pruning, `calculate_visibility()` for Literal intel enhancement |
| `backend/commands/executor.py` | Autonomous attack trigger (Aggressive), confrontation popup result handling, rivalry confrontation event, coordination modifier read, glory event recording after battle |
| `backend/commands/strategic.py` | Track consecutive HOLD turns for Literal trigger |
| `backend/game_logic/relationship.py` | Temporary relationship modifier support (apply/restore) |
| `backend/game_logic/dispatch.py` | Restlessness warning, autonomous attack warning, target notice, Literal intel briefing |
| `backend/game_logic/battle_report.py` | Jealousy-aware Berthier observations |
| `backend/campaign_log.py` | `jealousy` event type + formatter variants |
| `backend/notifications.py` | `JEALOUSY_CONFRONTATION` + `RIVALRY_CONFRONTATION` notification types |
| `backend/ai/enemy_ai.py` | Enemy jealousy evaluation (mechanical core, no UI — see §9b) |

### New File

`backend/game_logic/jealousy.py` — Core evaluation logic:
- `evaluate_jealousy(world)` — glory ladder ranking, per-marshal target finding, threshold check, rate limiting
- `find_jealousy_target(marshal, world)` — find one-rung-above target on glory ladder
- `evaluate_literal_jealousy(marshal, world)` — separate Literal trigger logic (consecutive HOLD)
- `resolve_jealousy(marshal, world)` — check resolution conditions per personality (including ladder shift)
- `apply_jealousy(marshal, target, world)` — set fields, degrade relationship, log event
- `clear_jealousy(marshal, world)` — restore relationship, clear fields, apply surge
- `check_escalation(marshal, target, world)` — escalation threshold + mutual trigger
- `get_glory_score(marshal, current_turn)` — sum glory within 5-turn window
- `record_glory(marshal, turn, battle_result)` — add glory event after battle
- `evaluate_rivalry_confrontation(marshal_a, marshal_b, transition, world)` — rivalry event with randomness

### Session Plan (3 Core + 1 Polish)

#### Session 1: Glory + Trigger + Core Mechanics (LOW RISK)

**Scope:**
- New file: `backend/game_logic/jealousy.py`
- Glory event recording after battles (in `executor.py`)
- `get_glory_score()` with 5-turn window
- `find_jealousy_target()` — glory ladder, one rung above
- `evaluate_jealousy()` — threshold check with relationship scaling
- `apply_jealousy()` — set fields, temporary -1 relationship
- `clear_jealousy()` — restore relationship, clear fields
- Duration timer in `advance_turn()`
- New marshal fields: `jealous_of`, `jealousy_turns_remaining`, `glory_events`, `consecutive_hold_turns`
- Serialization for all new fields
- Authority suppression (>70) and acceleration (<30)
- Suppression conditions (broken, retreating, Devoted)

**Reuses:** Relationship system (modify_relationship), advance_turn pattern, personality checks.
**Risk:** LOW — new file, new fields, straightforward logic. No existing code modified beyond advance_turn wiring and post-battle glory recording.
**Estimated tests:** ~40

**Gate:** `pytest` passes. Manual test: play 5 turns, see jealousy fire in test output.

#### Session 2: Personality Expressions + Resolution (MEDIUM RISK)

**Scope:**
- Aggressive: autonomous attack (advance warning, target priority, +15% solo buff, 0% coordination hard override, unavailability)
- Cautious: dispatch flavor text (coordination withholding is automatic via -1 relationship)
- Literal: trigger (consecutive HOLD), intel enhancement in `calculate_visibility()`, reassignment dispatch event
- Resolution conditions per personality
- Surge buff (1-turn post-resolution)
- Ladder shift resolution (passing target clears jealousy)
- Morning dispatch events: restlessness, fired, autonomous warning, target notice, resolved, surge, ladder shift
- Campaign log: jealousy event type + formatter variants
- Battle report: jealousy-aware Berthier observations

**Reuses:** Attack execution, calculate_visibility, dispatch builder, campaign log patterns, battle report observation system.
**Risk:** MEDIUM — autonomous attack inserts into executor flow. Model after existing autonomous/redemption attack pattern.
**Highest-risk point:** Autonomous attack in executor.py — needs to bypass normal command flow (no parser, no AP, no objection) while still using `_execute_attack()`. Use `is_player_action=False`.
**Estimated tests:** ~50

**Gate:** `pytest` passes. curl test: end turn triggers jealousy evaluation. Autonomous attack fires correctly.

#### Session 3: Confrontation + Escalation + Enemy (MEDIUM RISK)

**Scope:**
- Confrontation popup (first-time per pair): Acknowledge/Promise/Rebuke
- Escalation system: history tracking, progressive effects (warning → permanent damage → mutual)
- Enemy Building Blocks: same evaluation for enemy marshals, authority proxy, no UI layer
- Rate limiting: max 2 fires/turn, 1 popup/turn, overflow queuing
- Notification types: JEALOUSY_CONFRONTATION
- Battle report: enemy jealousy observations

**Reuses:** Popup/objection patterns in executor.py → main.py → Godot. Notification system. Enemy AI evaluation in turn_manager.
**Risk:** MEDIUM — confrontation popup follows existing objection pattern. Escalation derived from history list (clean). Enemy evaluation is player evaluation with UI stripped.
**Estimated tests:** ~45

**Gate:** `pytest` passes. Full integration: jealousy fires, popup appears, escalation triggers, enemy jealousy observable.

#### Session 4 (v3.1 Polish — DEFERRED)

- Rivalry Confrontation event (§6b) — probability tables, authority-gated mediation, "Separate Them" flag
- Separation management flag + dispatch warnings
- Top of ladder buff (see §18a for candidates — needs design approval)
- Any edge cases from playtesting

**Estimated tests:** ~30

### What Can Be Deferred to v3.1

| Feature | Impact of Deferral |
|---------|-------------------|
| Rivalry Confrontation (§6b) | Low — relationship transitions already have mechanical consequences. Narrative flavor only. |
| "Separate Them" flag | Low — player can track this mentally. |
| Top of ladder buff | Low — doesn't affect jealousy mechanics. Pure bonus. |
| Escalation tiers 2-3 | Medium — tier 1 (warning) is the most common. Tiers 2-3 require 3+ lifetime triggers, rare in 25-turn Waterloo. |

### Integration Risk Points

| Risk | File(s) | Mitigation |
|------|---------|------------|
| Autonomous attack bypassing normal flow | executor.py | Model after autonomous/redemption attack pattern. Use `_execute_attack()` with `is_player_action=False`. |
| calculate_visibility modification for Literal | world_state.py | Additive visibility boost, not replacement. Test fog leak regression. |
| Glory recording timing | executor.py | Record AFTER `process_battle_relationships()` runs. Same timing as relationship processing. |
| Advance warning state across turns | marshal.py, world_state.py | `jealousy_autonomous_warned` bool, cleared on cancel or attack. Simple state machine. |
| Confrontation popup wiring | executor.py, main.py | Follows objection popup pattern exactly. Use `world.pending_jealousy_confrontation`. |
| Enemy jealousy in turn_manager | turn_manager.py, enemy_ai.py | Evaluate after enemy phase actions resolve. Same timing as player jealousy. |

### Test Coverage

~165 tests across 4 sessions. Key areas:

- **Glory Ladder:** Target identification (one rung above), tie handling, top-of-ladder has no target
- **Ladder shift resolution:** Passing target clears jealousy with surge buff, escalation history still records
- **Relationship-scaled thresholds:** Devoted immune, Friendly delta>=4, Professional delta>=2, Rival delta>=1, Hostile delta>=1+idle
- **Trigger:** Glory delta vs threshold, idle acceleration, Literal consecutive HOLD trigger, authority acceleration/suppression
- **Glory scoring:** decisive bonus, territory bonus, outnumbered bonus, garrison stomp = 0
- **Duration scaling:** delta-based duration 2-5 turns
- **Rate limiting:** max 2 fires per turn, max 1 popup per turn, overflow queues correctly
- **Aggressive:** Autonomous attack fires, target priority (weakest first), NO AP cost, marshal unavailable, advance warning, +15% solo buff, 0% coordination with target (hard override), resolution requires >= 70% strength enemy OR ladder pass
- **Cautious:** Coordination withholding via relationship, resolution requires shared victory OR 2+ ally coordinated win OR ladder pass
- **Literal:** Intel enhancement (visibility boost), reassignment dispatch (informational only, not objection), resolution requires enemy contact (PURSUE/SUPPORT/defend), MOVE_TO alone does NOT clear, defend-against-attack passive resolution, surge = 1 extra turn of intel
- **Confrontation popup:** First-time only, acknowledge/promise/rebuke effects, Promise Glory = 1 AP + duration -2 (no deadline), Rebuke = trust -5
- **Rivalry confrontation (§6b):** Fires on transition (0->-1, -1->-2), randomness on all options, authority-gated mediation, personality-weighted outcomes, once per transition per pair
- **Resolution surge:** +10% attack (Aggressive), +10% defense (Cautious), +1 turn intel (Literal), only on action resolution or ladder pass, not timer
- **Escalation:** Rival-or-worse trigger, 3rd-lifetime trigger, permanent relationship damage, mutual jealousy spiral
- **Relationship:** Temporary modifier applied/restored correctly, Hostile floor explicit (personality expression still fires)
- **Pre-warning:** Restlessness dispatch event at threshold-1, target notification
- **Serialization:** All new fields round-trip, derivable fields NOT serialized
- **Suppression:** Authority > 70, capital threatened, broken/retreating marshals, Devoted immunity
- **Enemy jealousy (Building Blocks §9b):** Same formulas, same thresholds, same cascade. Authority proxy. Devoted enemy pairs immune. Battle report observes enemy friction.
- **Edge cases:** See §18b for full list

---

## 14. What This Spec Does NOT Cover

- **Top of ladder buff** — DESIGNED (v3.1). +1 all core stats while #1. See §1.
- **Coalition Trigger** — moved to Phase 8
- **Council command** ("to my tent" active resolution) — deferred to Phase 8 or later
- **Enemy marshal jealousy UI** — enemy gets mechanical core (same formulas), not player-facing UI (popups, warnings). See §9b.
- **Modding support** — jealousy thresholds/durations could be moddable, but not in initial implementation
- **LLM flavor text** — jealousy events use template strings, not LLM generation
- **Jealousy toward enemy-nation marshals** — explicitly excluded (same-nation only)
- **Pride mechanic** — Devoted allies celebrating each other's wins. Considered and deferred. The absence of jealousy IS the reward for high relationships. Coordination scaling (150% at Devoted) is already the payoff. Adding a pride buff on top makes positive relationships too strong. If added later, pride should come with a cost (e.g., Devoted marshals become more cautious about their own safety — "I must survive to fight alongside him again"). Phase 8+ territory.
- **Bernadotte's political jealousy** — The Petition Chain (writing to OTHER marshals to complain, multi-relationship poisoning) is better suited to BALANCED personality in the 1805 expansion. Filed for future use.

---

## 15. Appendix: Literal Jealousy — Ideas Considered

All ideas explored for Grouchy's jealousy expression. Logged for future reference.

### SELECTED: CANDIDATE B — The Vindicated Garrison (Obsessive Competence)

**Evaluation results (v3):**

| Criterion | Result |
|---|---|
| Duality test | PASS — enhanced intel vs. relationship cost |
| Decision test | PASS — leave for intel vs. pull to resolve |
| Identity test | STRONG PASS — "excellent at the wrong thing" is exactly Grouchy |
| Parallel test | PASS — comparable to Aggressive's +15% |
| Implementation test | PASS — routes through calculate_visibility |
| Waterloo test | STRONG PASS — competent at wrong objective |

Score: 6/6 (Candidate A scored 3/6 — failed duality, decision, and parallel tests)

### REJECTED: CANDIDATE A — The Silent Front (Communications Blackout)

Grouchy withdraws from the reporting network. Dispatch omission + intel degradation + enemy sighting suppression. Three existing systems affected, no stat changes, no binary overrides. Creates the "Where IS Grouchy?" experience.

**Strengths:** Strongest historical resonance (Waterloo was an information failure). Felt experience (dispatch gap is immediately noticeable). Routes cleanly through dispatch.py, world_state.py, intel filtering.
**Weakness:** Purely punitive — no upside, no dilemma. Makes the least-exciting marshal even worse. Player's only choice is "fix it ASAP." Failed duality, decision, and parallel tests.

### REJECTED: Malicious Compliance (draft v1)

SUPPORT with `join_combat=False`, MOVE_TO without fortify, attack without pursuit. Three behaviors that reduce Grouchy's effectiveness through deliberate minimum-effort execution.

**Why rejected:** Overlaps with core Literal identity (which is ALREADY "follows orders exactly"). join_combat is a binary flag override — indistinguishable from a bug to the player. "Malicious compliance" is a defiance variant wearing a different hat. No clear player-facing moment — the effects are hidden until battle results arrive.

### REJECTED: Precision Execution Loss (stat penalty)

Jealous Grouchy loses his +1 all-skills ability. Still follows orders, still fights, but performs at baseline instead of enhanced level.

**Why rejected:** Pure number modification. Player would need to check skill stats to notice. No felt experience — just slightly worse combat results. Boring.

### REJECTED: Immune to Jealousy (draft v1 Option C)

Literal marshals never get jealous. Preserves "reliable, no-drama" identity.

**Why rejected:** Loses the Waterloo fantasy entirely. Makes Literal marshals mechanically boring. Wastes the most historically dramatic personality type.

### CONSIDERED: Order Courier Interception

Grouchy, feeling sidelined, takes it upon himself to "assist" headquarters by carrying dispatches to other marshals — and interprets them with excessive literalism, garbling the intent. Orders to OTHER marshals get distorted when they pass through Grouchy's sector.

**Why shelved:** Breaks character. Marshals are corps commanders, not couriers — Napoleon had Berthier's staff for message delivery. Having Grouchy demote himself to courier duty doesn't fit his pride or his role. Also mechanically unclear: what does "distorted orders" mean in game terms? Would require a new system for order modification that doesn't exist.

**Salvageable kernel:** The idea of Grouchy's sector becoming an information dead zone that affects nearby marshals' awareness IS captured by the Silent Front's intel degradation (adjacent regions lose his scouting contribution).

### CONSIDERED: Hyper-Literal Pathing

When jealous, Grouchy interprets MOVE_TO with extreme literalism — takes the SHORTEST path even through dangerous territory. Normally marshals might path around enemy positions; jealous Grouchy takes the direct route because "the order says move to Belgium, not move safely to Belgium."

**Why shelved:** Interesting tactical consequence but narrow — only affects MOVE_TO orders. Would require new pathfinding logic (current strategic pathing doesn't have a "safe vs. direct" distinction). Risk of frustrating the player with seemingly bugged pathfinding. Could revisit if pathing system gets more sophisticated.

### CONSIDERED: The Formal Protest (Notification Spam)

Grouchy sends formal written protests to Napoleon about being sidelined. Creates persistent notifications that stack if ignored. Each unaddressed protest reduces authority by -1 (Grouchy undermines Napoleon's image among staff).

**Why shelved:** Historically authentic (Napoleon's correspondence IS full of petulant marshal letters). But mechanically it's just a notification annoyance + number penalty (authority drain). Doesn't create the visceral "blind spot" feeling. Could work as an ESCALATION effect layered on top of the Silent Front — if Grouchy stays jealous long enough, the protests start arriving. Worth revisiting.

### CONSIDERED: The Petition Chain (Multi-Marshal Poison)

Grouchy writes to OTHER marshals complaining about his assignment. Creates relationship degradation with MULTIPLE marshals, not just the jealousy target. Office politics — the passive-aggressive letter campaign.

**Why shelved:** Thematically strong (marshals DID politick behind Napoleon's back — Bernadotte was infamous for this). But spreads jealousy effects too wide for a first implementation. The relationship system handles pair-wise interactions well; poisoning multiple relationships simultaneously would need careful balancing. Better suited to BALANCED personality (Bernadotte) when that's implemented in the 1805 expansion. Filed for future use.

### CONSIDERED: The Over-Reporter (Noise Flood)

Instead of going silent, jealous Grouchy becomes ANNOYING — sends excessive pedantic dispatches about trivial matters. "A patrol of 12 enemy cavalry spotted 3 leagues east." "Supply wagon arrived with 40 barrels of flour." The Morning Dispatch gets cluttered with noise, burying important intel.

**Why shelved:** Funny and historically plausible (some officers DID flood HQ with trivia). But it's the opposite direction from the Waterloo parallel. Grouchy's failure was SILENCE, not noise. Also mechanically tricky — cluttering the dispatch UI with fake entries could frustrate more than engage. The concept of "important intel buried in noise" is interesting but better suited to a future fog-of-war enhancement than a jealousy expression.

### CONSIDERED: Rigid Re-positioning

If jealous Grouchy's region is attacked and he's pushed back via forced retreat, he RETURNS to his original hold position next turn instead of staying where he retreated to. "My orders say hold THIS region." Relentless literal compliance even after tactical displacement.

**Why shelved:** Interesting niche interaction but too narrow — only matters when Grouchy is attacked AND retreats, which may never happen during a jealousy window. Also mechanically close to a binary override (auto-return flag). The forced retreat system doesn't currently support auto-return behavior, so this would need new pathfinding and recovery logic for one edge case.

---

## 16. Reference: Existing System Integration Points

| System | How Jealousy Connects |
|--------|----------------------|
| **Personality** | Determines expression: Aggressive=autonomous attack, Cautious=withholds, Literal=obsessive competence |
| **Relationships** | Primary output: temporary -1 toward glory target. Relationship level also scales trigger threshold (§1). |
| **Coordination** | Downstream: degraded relationship reduces coordination via `_RELATIONSHIP_SCALING`. Aggressive hard override to 0%. |
| **Objection V2** | Downstream: degraded relationship triggers SUPPORT objections via `_evaluate_relationship_support()` |
| **Defiance** | Downstream: degraded relationship elevates defiance chance |
| **Authority** | Polarity: > 70 suppresses, < 30 accelerates |
| **Trust** | No automatic impact. Confrontation popup choices can affect trust. Rivalry confrontation choices may affect trust. |
| **Fog of War** | Literal expression: enhanced visibility from jealous Grouchy's sector |
| **Morning Dispatch** | Pre-warnings, fire events, autonomous warnings, target notice, resolution events, ladder shift events |
| **Campaign Log** | Jealousy events as "command" category entries |
| **Notifications** | Jealousy confrontation + rivalry confrontation (first-time only, HIGH priority) |
| **Strategic Orders** | Literal trigger (consecutive HOLD tracking), Literal resolution (enemy contact during strategic order) |
| **Battle Report** | Post-battle observations note jealous behavior (both player and enemy marshals) |
| **Enemy AI** | Building Blocks: mechanical core (glory ladder, relationship cascade, timer, resolution). No UI layer. Authority uses faction proxy. See §9b. |

---

## 18. Design Review Findings (Feb 27, 2026)

### 18a. Top of Ladder Buff — "Crowned with Glory" (APPROVED DIRECTION)

**Selected design: +1 to all core stats (shock, fire, admin)** while #1 on the glory ladder. See §1 for full specification.

**Why stat boost over alternatives:**
- **Morale regen** (rejected): Too passive. Player doesn't feel it happening. Recovery speed is invisible.
- **Authority contribution** (rejected): Creates feedback loop (authority suppresses jealousy → top marshal stays on top forever). Self-defeating.
- **Recruitment bonus** (rejected): Location-gated and niche. Only matters in manpower-rich regions.
- **Stat boost** (selected): Immediately visible in combat. "Literally levels you up." Player FEELS the difference when their star performer hits harder, defends better, and manages supply more efficiently. The buff transfers when the position changes — creates genuine excitement about ladder movement.

**Interaction with glory loss mechanic:** Losses can knock a marshal off the top. The stat buff transfers to whoever takes #1. This means the top position is contested, not permanent. A marshal who rests on laurels can lose the crown to someone still fighting. The ladder is a living thing.

**Self-balancing:** +1 all stats makes the top marshal more effective → they win more → they stay on top → others get more jealous → more friction. The reward for excellence is power AND a target on your back.

### 18b. Edge Cases (from design review)

**EC-A: Defensive glory.** Glory formula says "garrison stomp = +0" but doesn't address defensive victories. If Grouchy defends his garrison against an attacker and wins, does he earn glory? **Clarify: "Base: +1 per victory" includes defensive victories.** Garrison stomp exemption applies only to attackers defeating a garrison.

**EC-B: Autonomous attack + strategic orders.** If jealous Ney has an active MOVE_TO/PURSUE, the autonomous attack disrupts the path. **Rule: Autonomous attack clears any active strategic order** (same pattern as reinforcement relocation in MULTI_MARSHAL_SPEC).

**EC-C: Steal target's glory (§7 priority #2).** "Enemy that the jealousy target recently defeated" requires tracking which enemies a marshal defeated — not tracked anywhere in current system. **Recommendation: Cut priority #2.** Weakest adjacent enemy is sufficient glory-seeking behavior.

**EC-D: Literal trigger — what counts as "garrison duty"?** Trigger is HOLD strategic order or explicit garrison command, NOT just being physically near a garrison. If ALL marshals are on HOLD, the "while others received orders" condition is false — Grouchy's jealousy doesn't trigger.

**EC-E: Jealousy + defiance cascade.** Jealous Ney ordered to SUPPORT Davout → relationship SUPPORT objection fires (Rival/Hostile) → player insists → defiance may fire → Ney attacks instead of supporting. This is a 4-step cascade. **This is intended behavior** (Bernadotte at Jena). Document as expected interaction, not a bug.

**EC-F: Resolution + relationship processing timing.** If battle resolves jealousy, the -1 temp relationship should restore BEFORE `process_battle_relationships()` runs on that battle. **Ordering: resolve jealousy → restore relationship → process battle relationships.**

**EC-G: Bidirectional jealousy (pre-escalation).** Two marshals can independently become jealous of each other through normal ladder mechanics without escalation tier 3. Escalation "mutual" at tier 3 is about *automatic* triggering, not about prohibiting natural bidirectional jealousy.

**EC-H: Capital threatened suppression vs. helpful autonomous attack.** If the jealous aggressive marshal would attack the enemy threatening the capital, suppression still prevents it. **Correct** — survival overrides pettiness, player should be commanding defense.

**EC-I: Promise Glory with 0 AP.** Gray out the option at display time. Don't let player select then fail at execution.

**EC-J: Evaluation order + rate limiting.** Evaluate ALL marshals first (snapshot who crosses threshold), THEN apply rate limiting to sorted list. Don't interleave evaluation and application — relationship changes from early fires could affect later threshold checks.

**EC-K: Aggressive resolution — raw or effective strength?** "Win where enemy strength >= 70% of yours" uses **raw strength** (pre-modifier, pre-coordination). Glory is about fighting someone your size, not about modifier advantages.

**EC-L: Cautious resolution — "2+ allies present."** The cautious marshal must be IN the battle AND 2+ OTHER same-nation marshals must also participate. 3+ total including the cautious marshal.

**EC-M: Enemy "home regions" for authority proxy.** Define per faction. For Waterloo: regions controlled at game start by that faction. Must be reconstructible from static data (region.py starting controller), not a serialized field.

**EC-N: Enemy autonomous attack + AI priority chain.** Aggressive enemy marshal's jealousy-driven autonomous attack inserts after P1 (broken recovery) but before P2 (defend capital). Survival priorities override jealousy.

### 18c. Design Review Suggestions

**Cautious expression visibility (§3 Cautious).** The 50% coordination reduction is mechanically correct but the player may not feel it. Promote the existing "campaign log flavor: critical reports undermining the rival" to a guaranteed dispatch event: *"Davout's reports on Ney's forces have become... sparse. Do not expect full cooperation."* Surfaces the jealousy without adding mechanics.

**Rivalry Confrontation (§6b) complexity.** The probability tables have ~30+ values to balance. Consider collapsing to 2 outcome bands per option (e.g., 75%/25%) instead of 3-4. Alternatively, defer the entire §6b to v3.1 — relationship transitions already have mechanical consequences through coordination/objection systems.

**Literal reassignment dispatch.** Downgrade from popup to dispatch event. It's informational (not an objection), and making it a dispatch event lets the player read it at their pace without interrupting command flow.

**Autonomous attack targeting.** Cut priority #2 (steal target's glory) per EC-C above. Simplifies to: weakest adjacent → any adjacent → no action.

---

## 17. Changelog

### v3.1 (Design Review + Feedback Pass — Feb 27, 2026)

Design review with historical analysis, friction audit, implementation planning. Followed by user feedback pass with 7 directed changes.

**Merged into spec (design review):**
- §13 rewritten with 3+1 session plan (was outline only). Walking skeleton defined. Risk assessment per session.
- §18a: Top of ladder buff candidates evaluated.
- §18b: 14 edge cases (EC-A through EC-N) identified during review.
- §18c: Design suggestions — cautious visibility, rivalry deferral, literal dispatch downgrade, targeting simplification.

**User feedback changes (v3.1b):**
- §7: Cut "steal target's glory" priority #2. Simplified autonomous attack to 3 priorities.
- §6b: Rivalry Confrontation deferred entirely to v3.1 implementation.
- §3: Literal trigger clarified — "actively engaged" defined (non-HOLD strategic order OR tactical command this turn).
- §10: Escalation tier 3 mutual clarified — B's target forced to A specifically, overrides ladder lookup.
- §6: Confrontation popup timing added — start of NEXT turn, not during evaluation.
- §1: Top of ladder redesigned as +1 all core stats (shock/fire/admin). Morale regen rejected.
- §1: Glory loss mechanic added — defeats cost glory (-1 base, -1 decisive, -1 territory lost, outnumbered exempt). Keeps ladder dynamic.
- §18a: Updated to reflect stat boost selection with rationale.

**Deferred to v3.1 implementation:**
- Rivalry Confrontation (§6b) — highest complexity, lowest marginal gameplay value.
- "Separate Them" persistence flag.

### v3 (Design Review Session — Feb 2026)

Major design review with historical analysis. All changes below are design decisions, not implementation.

**Targeting:**
- **Glory Ladder** replaces dogpile targeting. Each marshal targets one rung above, not the highest glory holder. Distributes jealousy across pairs, prevents pile-on, scales to 12+ marshals.
- **Ladder shift resolution** — passing your target on the glory ladder clears jealousy with surge buff. Escalation history still records the instance.
- **Ties** — no jealousy between equals. Below-tie marshal uses worse-relationship tiebreaker.

**Thresholds:**
- **Relationship-scaled thresholds** — Devoted immune, Friendly delta>=4, Professional delta>=2, Rival delta>=1, Hostile delta>=1+idle. Friends are resistant, enemies have hair triggers.
- **Pride mechanic evaluated and deferred** — absence of jealousy IS the reward for Devoted. Coordination scaling (150%) already pays off high relationships.

**Literal Expression:**
- **Candidate B selected** (Vindicated Garrison / Obsessive Competence). Passed 6/6 evaluation criteria vs Candidate A's 3/6.
- **Resolution tightened** — requires enemy contact (PURSUE engage, SUPPORT battle, defend against attack). MOVE_TO alone does NOT clear. Prevents cheesing with trivial move orders.
- **Surge buff** — intel enhancement persists 1 extra turn after resolution.

**Aggressive Expression:**
- **AP cost removed** from autonomous attack. Marshal acts on own initiative — cost is unavailability, not player's AP budget. Historically, autonomous action by a subordinate doesn't consume Napoleon's administrative capacity.

**Confrontation Popup:**
- **Promise Glory simplified** — 1 AP, duration -2 turns, no broken promise mechanic. Old design was a trap choice (player can't control whether qualifying battles happen within deadline).

**Cautious Resolution:**
- **Softened** — shared victory with target OR any 2+ ally coordinated battle win. Old requirement (shared victory with specific target only) was too hard to arrange relative to Aggressive resolution.

**Rivalry Confrontation Event (NEW §6b):**
- Fires on relationship transitions (0->-1, -1->-2). Three options with randomness on all outcomes. Authority-gated mediation. Personality-weighted escalation risk. Once per transition per pair.

**Hostile Edge Case:**
- **Explicit statement** — when relationship already at -2 floor, temp -1 has no further relationship effect. Personality expression still fires, resolution still required.

**Rate Limiting:**
- Max 2 jealousy fires per turn, max 1 confrontation popup per turn, max 1 autonomous warning per turn. Overflow queues by glory delta (most aggrieved first). Prevents popup avalanche at 1805 roster sizes.

**Surface:**
- **Target notification** — informational dispatch note to the glory target. No mechanical penalty for being good.
- **Ladder shift dispatch event** — when jealousy resolves via passing target.

**Fields:**
- Removed 3 derivable fields (jealousy_relationship_modifier, jealousy_confrontation_response, jealousy_promise_deadline). Reduces serialization footprint.
- Added separation_flagged (for "Separate Them" rivalry confrontation option).

**Historical Notes:**
- Expanded historical anchors: Murat's glory-seeking charges, Soult's Spain ambitions, Bernadotte at Jena, Peninsula marshals' refusal to cooperate.
- Noted Bernadotte's political jealousy (Petition Chain) as future BALANCED personality design for 1805 expansion.
- Clarified Grouchy's Waterloo failure was NOT jealousy — it was literal compliance (already modeled by personality). Literal "jealousy" is actually sidelining resentment, a related but distinct emotion.

**Enemy Jealousy (Building Blocks):**
- **Enemy marshals INCLUDED** in jealousy mechanical core (§9b). Removed blanket exemption from v2. Jealousy is marshal-to-marshal, not marshal-to-Napoleon — no narrative reason for enemy immunity. Structural advantage violation of Building Blocks if exempt.
- Enemy gets: same glory ladder, same thresholds, same relationship cascade, same timer/resolution/escalation. Enemy doesn't get: popups, Berthier warnings, confrontation choices.
- Authority polarity uses faction-level proxy (capital + region control).
- No new AI code needed — coordination system already reads relationships, reinforcement already uses relationship scores.
- Player can observe and exploit enemy friction through battle reports and fog-filtered intel.

### v2 (Original Draft)

Initial comprehensive design. Glory scoring, personality expressions, escalation system, confrontation popups. Literal expression left as open question between Candidates A and B.

### v1 (Superseded)

Early draft with dogpile targeting, AP costs on autonomous attacks, broken promise mechanics. Replaced entirely by v2.
