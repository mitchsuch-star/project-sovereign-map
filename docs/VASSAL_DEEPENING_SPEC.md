# Vassal Deepening Spec — Land Grants & Authority Coupling

> **Status:** Authored July 14, 2026 as the phase that follows Combat Overhaul
> Phase 5 (Vassals). **VS-R ✅ BUILT July 14, 2026** at the memo's recommended
> defaults (user-directed: "code the recommendations from the vassal spec commit"),
> landing record §2.7. **VS-3 ✅ BLESSED TO BUILD July 15, 2026** — the user directed
> "assure we build diplo stuff": VS-3 (give land to vassals via the F1 Diplomacy
> Wizard) is now the **committed next vassal-depth build** at §1's recommended
> defaults (in-band tunable; structural changes still escalate). It is the diplo-screen
> slice Sweep 4 named as a P1 path from Vassals 6.5 → 7+. §1 is spec-complete and
> buildable next session.
>
> **Owner routing:** CLAUDE.md Current Phase Queue → this spec. **VS-3 is the next
> vassal-depth slice (blessed)**; then the **Vassal Depth** follow-ons — "The Defection"
> (coalition-join, GR9), the garrison lever wire-or-remove (VP-D1), and enemy-AI
> grip-awareness (VP-D6) — see STATUS.md "Vassal Depth Queue".

---

## 0. Why this exists

Combat Overhaul Phase 5 fixed vassal-loyalty **discoverability** (the −2 satellite
bleed now surfaces; the levers are taught). But the audit of the lever set (STATUS,
July 14) found every existing lever is **transactional** (spend gold/AP/troops now)
or **combat-gated**:

| Lever | Effect | Nature |
|---|---|---|
| Invest | +10 one-shot | transactional (DP + gold) |
| Garrison capital | +5…+8 / turn | transactional (corps + AP) |
| Grant autonomy | drift −2/−4 → +1 | trades away tribute + control |
| Win battles | +1…+3 / turn | combat-gated |
| Subsidy clause | +1 per 100g/turn | transactional |
| Share a war | +2 per shared enemy | drags vassal into your fights |

Two things are missing, and both are the *actual* historical mechanisms by which
Napoleon ran (and lost) his satellite empire:

1. **A standing, strategic "enlarge the vassal" lever** — Napoleon bound Bavaria,
   Saxony, and Württemberg by *giving them conquered land*. That is **VS-3**.
2. **The empire's cohesion tracking the Emperor's grip** — in 1813–14 the
   Confederation of the Rhine dissolved as Napoleon's power collapsed; the satellites
   flipped. Loyalty should not be independent of the lord's **authority**. That is
   **VS-R** (research-first).

Design philosophy (per project memory): rewards stay **reactive and discoverable**
— the player *chooses* to cede land; nothing auto-endows. Build conservatively,
gate before code.

---

## 1. VS-3 — Land Grants to Vassals (via the Diplomacy Wizard)

**Fantasy:** "Reward Bavaria for its service — cede it the province it bled for."
A lasting concession that binds a satellite, paid in your own territory and income.

### 1.1 Mechanic shape (blessed numbers escalate to the gate)

- **New action `grant_region_to_vassal`** — a full new-action wiring (executor in
  `vassal_executor.py` → `vassal.py` helper `grant_region_to_vassal(world, vassal, region)`;
  the 12-step new-action checklist incl. VALID_ACTIONS, parser, campaign-log type,
  golden-corpus row). It is an **ADMIN/diplomatic** action.
- **Effect on ratify:**
  - `region.controller = vassal_name` (the settlement transfer seam,
    `settlement_ratify.py:267` — reuse, don't reinvent).
  - Vassal **loyalty += grant bonus**, scaled by the province's worth so a rich
    gift binds harder than a worthless moor:
    `bonus = min(GRANT_LOYALTY_CAP, GRANT_LOYALTY_BASE + income_value // GRANT_INCOME_DIVISOR)`
    (proposed: base 10, cap 25, divisor 200 — **escalates to the gate**).
  - The lord **loses the region's income**; the vassal now pays **tribute** on it at
    its autonomy rate — the historical point (you keep a cut, not the whole).
  - **Cost:** the land *is* the cost. Proposed: 1 DP + 1 AP, **no gold**.
- **Eligibility (all required):**
  - Target is the player's vassal (lord == player).
  - Region controller == lord (you can only give what you hold).
  - Region is **not** the lord's capital and not the lord's last N regions
    (no self-immolation).
  - Region is **contiguous** to the vassal's existing territory *(open question §3 —
    contiguity vs. any-owned)*.
- **Anti-abuse:**
  - Per-vassal **cooldown** (proposed 3 turns, mirrors invest) so you can't farm
    loyalty by shuffling provinces back and forth.
  - **Reclaim-on-rebellion:** granted provinces are the first to flip back if the
    vassal rebels *(needs a `granted_regions` provenance list — open question §3)*.
  - A region-worth **floor** so ceding a near-worthless province still costs a DP but
    grants little (discourages token gifts). *(open question §3)*
- **Symmetry (GR5):** AI lords cede land to their satellites through the **same**
  executor; an `enemy_ai` rung offers it when a vassal is slipping and the lord holds
  a spare contiguous province. No special-case AI path.

### 1.2 Diplomacy-wizard integration (the required surface)

The wizard already renders a **Vassals** category in Step 2 and already ships a
province/war sub-picker pattern (`diplomacy_wizard.gd` — the `war_id` picker,
~L471–490). VS-3 rides those rails:

1. **Backend option** — `diplomatic_advisory.py` emits a `grant_region_to_vassal`
   option in the vassal action block (mirrors the `invest_vassal` kind at ~L239),
   *with the list of eligible regions* (diplomacy has no fog — memory
   `project_diplo_no_fog` — so the full eligible set is safe to send).
2. **Step 2 → sub-picker** — selecting "Cede Territory to {Vassal}" opens the
   existing sub-picker populated with eligible provinces (name + income + contiguity
   flag), exactly like the war-detail picker. Each button carries the chosen
   `region` in the structured payload (`_structured_payload_for_action`).
3. **Confirm line** — states the terms plainly ("Cede **Swabia** (income 400) to
   Bavaria — loyalty +18, you forfeit 400g/turn income, Bavaria remits 75% tribute").
   Consistent with the settlement/guided-terms "every option states its terms" rule.

### 1.3 Landing contract (Golden Rule 9) — ✅ LANDED July 16, 2026

- **Owner:** this spec §1. **Landing slice:** VS-3 (single session, post-gate).
- **Completion definition — MET:** a player can, from the F1 wizard, cede an eligible
  province to a vassal; control transfers, loyalty rises by the worth-scaled bonus,
  the lord loses the income, the vassal tributes it, cooldown arms. (The AI's grant
  RUNG is consolidated into VP-D6's shore-up rung, same queue — VS-3 ships the
  lord-neutral helper + a GR5 latent-parity pin, so the rung is a consumer, not a
  rebuild.)
- **What landed (pre-build seam verification amendments, July 16, 2026):**
  - `grant_region_to_vassal` + `list_grantable_regions` + `grant_loyalty_bonus`
    in `vassal.py` — worth-scaled `min(25, 10 + income_value//200)`, **never
    spiral-blunted** (§2.4-Q3); `granted_regions` provenance + `grant_cooldown`
    ride the vassal row (serialize free); reclaim-on-rebellion on the **WAR branch
    only** (armistice/graceful breaks keep the land), provenance read BEFORE the
    row delete (GR4).
  - **Eligibility:** lord-controlled + **conquered-land-only** (homeland excluded —
    replaces the draft's "last N regions"; matches the ES-7 endow triangle) + no
    capitals + not a marshal's LIVE estate (ES-7 `dotation_regions` exclusion) +
    contiguity (waived for landless vassals and for the vassal's own lost homeland
    — the Ried dynamic).
  - **Cost: 1 DP, 0 AP** (deviation from the draft's 1 DP + 1 AP — the whole
    vassal family is in `executor.py free_actions`), cooldown 3 turns per-vassal.
  - **Wizard:** the option rides `diplomacy.py get_available_diplomatic_actions`
    (NOT `diplomatic_advisory.py` — the spec §1.2 seam was wrong) with
    `eligible_regions` payload; `diplomacy_wizard.gd` renders a **positive-path
    province picker** (the multi-war rescue was error-path only) where every pick
    states its terms; `CommandRequest.region` + overlay added in `main.py`
    (pydantic silently dropped unknown fields — checklist gap found at
    verification). Boot smoke clean.
  - **Typed path:** mock-parser `\bcede\b` + nation-gated "grant X to <nation>"
    (never shadows `grant_dotation`/`change_autonomy`); executor extracts the
    province from raw text by longest known-region match; no region → answers
    with the eligible list. 3 golden-corpus rows (checklist step 12).
  - Recovery hints (healthy + spiral) now name the grant — the spiral band's one
    unblunted lever. Help text teaches "cede Tyrol to Holland".
- **STATUS line:** in the July 16, 2026 session entry.
- **Behavior test:** `test_vassal_land_grant.py` (32) — eligibility gates, worth-scaled
  loyalty, income/tribute handoff (assert-only), cooldown, reclaim matrix, GR5
  enemy-lord grant, wizard payload shape, nested serialization round-trip.

---

## 2. VS-R — Authority ↔ Vassal-Loyalty Coupling

**Fantasy:** "The Empire holds because *you* hold. When Napoleon falters, the
satellites smell weakness — and only real concessions keep them."

Today vassal loyalty drift is **independent of the lord's authority**. VS-R couples
them so a **spiral** in the Emperor's grip loosens the whole satellite web, and at
rock-bottom authority the cheap levers (invest, a token subsidy) no longer suffice —
only **land, autonomy, a large subsidy, or winning battles** arrest defection.

> **✅ RESEARCH COMPLETE — July 14, 2026.** Memo:
> [`docs/audits/VASSAL_AUTHORITY_COUPLING_RESEARCH_2026_07_14.md`](audits/VASSAL_AUTHORITY_COUPLING_RESEARCH_2026_07_14.md)
> (9-agent adversarially-verified research: history / authority-code / vassal-code /
> jealousy-coherence; historical timeline independently fact-checked). This section is
> now **gate-ready**: the memo answers all seven research questions with recommended
> numbers and **supersedes the original draft band curve**. **The gate decides §2.6
> (Open Questions) + §2.5 numbers before any code.**

### 2.1 Historical grounding — *does it play like Napoleon losing his vassals IRL?*

**Yes, on every axis except one** (the memo's headline verdict). The 1812–14 collapse
of the Confederation of the Rhine *was* loss-of-grip → loss-of-vassals:

| Real event | VS-R mechanic | Faithful? |
|---|---|---|
| Russia catastrophe breaks the aura of invincibility; the enforcement army evaporates | Grip falls → satellite drift turns negative | ✅ the whole fantasy |
| **Treaty of Ried, 8 Oct 1813** — Bavaria flips only when Napoleon can't guarantee its frontier; the deal is **sovereignty + no net territorial loss** | "No cheap recovery": at the floor only land (VS-3) / autonomy / release / large subsidy work | ✅ the binding concession was *existential* |
| **Saxony returns to Napoleon after Lützen** (spring 1813); the web holds through the summer | One-way coupling → winning raises grip → drift returns to neutral, in-progress defections arrestable | ✅ **reversibility is essential; one-way delivers it** |
| Ried is the template; Saxon + Württemberg contingents flip **mid-battle at Leipzig** | Cascade term: first flip raises defection *risk* for siblings | ✅ keep it probabilistic |
| The Rhine states **switched sides and turned their armies on France** — they did *not* rebel into an independent war | Today the game only models **independent rebellion** | ❌ **the one unfaithful element → §2.4-Q7** |

The single required correction: the flagship outcome is *"the satellite joins the
enemy coalition and its army joins the enemy order of battle."* VS-R **v1 ships
grip-accelerated *independent* rebellion** (faithful enough, near-zero cost) and homes
**coalition-defection ("The Defection") as a separate GR9 follow-on slice** — now designed
as **VS-6 (§7)**: a bribed flip whose outcome is *free → war with the former lord* or *transfer
to the bribing coalition member* (the "army joins the enemy order of battle" is the transfer/hostile
outcome). VS-4 (§5) adds the historically-faithful precursor: a disaffected satellite withholds its
contingent *before* it defects.

### 2.2 The signal — a derived "imperial grip" (the crux finding)

The draft assumed `authority_tracker.authority` was the "spiral" signal. **It is not:
the code strand proved `authority_tracker` does NOT spiral on military collapse** —
its only military movers are ±5 per-battle nudges gated on *outnumbering* (being
overrun ⇒ no dock), and a capital lost to an enemy garrison assault changes it by
**zero** (the authority block is guarded to the player-as-attacker). A player can lose
the war, shed home provinces, and have Paris taken with the tracker near 100 — high
exactly when history says the satellites should defect. `nation_authority[player]` is
**worse — inert dead code** (`modify_nation_authority` never called;
`_process_nation_authority` is a `pass`).

**Recommendation (memo Q1): a new single-source `get_imperial_grip(world, nation)`**
that blends the player's `authority_tracker` (the *court/marshal-deference* component)
with the **same territorial-collapse term the jealousy enemy proxy already carries**
(capital held, homeland majority, war_score). This makes the player's grip finally
respond to losing capital/homeland/war, and — because it keys off the lord — is
**symmetric for AI lords for free (GR5)**. Boot returns **100** for the player (full
empire) → coupling dormant; enemy intact → 75 (jealousy parity). Reuses only existing
seams; **zero new serialized fields**. *(Cheapest v1 fallback: key off the existing
`get_authority_proxy` as-is and accept a thin player-side signal — gate's call, §2.6-Q1.)*

### 2.3 The coupling curve (supersedes the draft)

The draft's `≥70 → +1 / 40–69 0 / 20–39 −2 / <20 −4` is **retired**. Two corrections:

- **The high band must be `0`, NOT `+1`.** A `+1` "ascendant" bonus is a *balance
  change* that breaks a **hard boot-dormancy pin against ~10 test files** (8
  `TestLoyaltyTicks` + 4 `test_vassal_recovery_lever` pins assert exact `-2`/`+1`
  deltas at default authority 100). Because `_contribute` records only nonzero values
  (`vassal.py:276`), a `0` term is byte-identical. **Coupling is negative-only,
  spiral-band only, and keys off the *lord's* grip (not the vassal's loyalty).**
- **Anchor on jealousy's 70/30 breakpoints, not the draft's 40/20** — so crossing a
  line lights up *both* the marshal board and the satellite board as one felt moment.

| Grip band | Vassal drift term | Rationale |
|---|---|---|
| **≥ 70** (`AUTHORITY_SUPPRESS_ABOVE`) | **0** | Same line that calms the marshals; byte-identical boot |
| **30 – 69** | **0** | Ordinary autonomy drift governs |
| **< 30** (`AUTHORITY_ACCELERATE_BELOW`) | **−2** / turn | The one advertised spiral threshold |
| *(optional nested)* **< 15** | **−4** floor | Only if −2 too gentle; below the shared 30 line |

**Additive** to `AUTONOMY_DRIFT`, **capped at −4 non-stacking, NEVER a multiplier**
(the one shape that yields unrecoverable collapse). Worst realistic case puppet(−4) +
floor(−4) = −8/turn ≈ 13 turns to 0. Enemy side auto-bounds to the −2 tier (proxy
floors at 25).

### 2.4 The remaining answered questions (from the memo)

- **Q3 — "No cheap recovery":** a `get_authority_lever_multiplier(world, lord)` returns
  exactly `1.0` at healthy grip (byte-identical boot) and `0.40` in the <30 band,
  applied to the **cheap one-shots only** — invest (+10, `:822`) and autonomy-up (+10,
  `:875` upgrade branch). **Never softened:** VS-3 land grant (the premier arresting
  lever), full release, the autonomy-*down* −15. *History addendum:* the strongest
  arrestor of all is **winning battles** (Saxony after Lützen) — it falls out of the
  one-way loop automatically but must be an explicit assertion in the recoverability test.
- **Q4 — One-way (authority → loyalty) for v1.** Do NOT feed vassal state back into
  authority: jealousy has **no automatic per-turn authority sink** (its four writes are
  all player-choice-gated), so a two-way loop would open the *first* brakeless sink in
  the exact spiral zone where Fontainebleau also fires — an unrecoverable spiral. Any
  future bolster term must be asymmetric, small, capped, and positive-state-gated
  (never rescues a spiral).
- **Q5 — Jealousy co-firing is thematically correct** (two casualties of one cause) and
  bounded by: latch-free per-turn recompute (no permanent-escalation mirror); the −4
  cap; defection routed through the existing *probabilistic* `check_defection_cascade`
  roll (risk, not certainty); and **the de-compounding lever — VS-R stays ACTIVE during
  a capital-threat where jealousy goes silent** (army-infighting when grip is low;
  satellite-flight when the capital is under the knife — more legible *and* more
  historical).
- **Q6 — Boot-dormant at authority 100; ZERO new serialized fields for v1** (all inputs
  already persist). Pins named in the memo §Q6 stay green.
- **Q7 — Defection:** v1 = grip-accelerated *independent* rebellion (reuse
  `check_vassal_rebellion` unchanged). Coalition-join is the historically faithful
  outcome but a **new mechanism** (static membership — zero `members.append` sites +
  target selection + contingent transfer) → its own GR9 slice.
- **Interaction — enemy courting scales up in the spiral** (`attempt_vassal_courting`):
  the `loyalty < 50` unlock widens and `loyalty_reduction` amplifies when the player's
  grip is low — the Allies peel satellites once Napoleon looks weak (the Ried dynamic),
  bounded by the existing cooldown + one-per-turn cap.

### 2.5 Recommended numbers (escalate to the gate)

`VS_R_DRIFT_ASCENDANT=0` · `VS_R_DRIFT_NEUTRAL=0` · `VS_R_DRIFT_SPIRAL=−2` ·
`VS_R_DRIFT_FLOOR=−4` (below grip 15, optional) · `VS_R_DRIFT_CAP=−4` non-stacking ·
`VS_R_CHEAP_LEVER_MULT=0.40` in the <30 band · grip docks `GRIP_CAPITAL_LOST=−40` /
`GRIP_HOMELAND_MINORITY=−25` / war_score `−15` (< −50) / `−8` (< −30) · reuse
`AUTHORITY_SUPPRESS_ABOVE=70` / `AUTHORITY_ACCELERATE_BELOW=30` · courting unlock widen
0→+15 by grip · courting effectiveness ×1.0→×1.5 by grip · recoverability floor **≥ 8
turns** for a full-3-satellite spiral collapse. *All in-band tunable; see memo §4.*

### 2.6 Open questions for the gate

1. **Grip helper vs. direct dock** — bless the derived `get_imperial_grip` superset
   (recommended) and keep `get_authority_proxy` untouched for jealousy? Or the cheapest
   v1 (`get_authority_proxy` as-is, thin player signal)?
2. **Does the multiplier hit the per-turn subsidy?** v1 softens only invest +
   autonomy-up, leaving subsidy full-strength (a *large* subsidy stays existential).
3. **Coalition-defection now or later** — v1 independent rebellion + "The Defection"
   as a separate GR9 slice? (Recommended.)
4. **Optional −4 floor** below grip 15 up front, or hold for post-playtest tuning?
5. **Layering relocation** — move `get_authority_proxy` + `is_capital_threatened` + the
   two breakpoints into `backend/models/authority.py` ("one grip = one module"), or
   accept a recorded `vassal.py → jealousy.py` import deviation?
6. **Copy bless** — the spiral-band `recovery_hint` variant naming *land / large
   subsidy / release / win a decisive battle*.

### 2.7 Landing contract (Golden Rule 9) — ✅ LANDED July 14, 2026

- **Owner:** this spec §2 + the research memo. **Landing slice:** VS-R ✅ **BUILT**
  (backend-only); "The Defection" coalition-join is a separately-gated GR9 follow-on.
- **Completion definition — MET:** vassal drift responds to the lord's *imperial
  grip* per the blessed curve; in the spiral band the cheap levers are blunted and
  only major concessions (or winning battles) arrest defection; enemy courting scales
  with player weakness; boot is dormant at authority 100; jealousy co-fires but stays
  recoverable (one-way, read-only on authority).
- **What landed (all six §2.6 recommendations coded at the §2.5 defaults):**
  - **Signal (Q1):** `get_imperial_grip(world, nation)` in `backend/models/authority.py`
    — the derived superset; `get_authority_proxy` left untouched for jealousy. Boot:
    player 100 / enemy 75 / enemy floor 20 (never sub-15). **Zero new serialized fields.**
  - **Curve (Q2):** `authority_vassal_drift` — grip ≥ 30 → 0 (byte-identical),
    grip < 30 → −2, capped at `VS_R_DRIFT_CAP=−4`, additive not multiplicative.
  - **No cheap recovery (Q3):** `get_authority_lever_multiplier` (1.0 healthy /
    0.40 in <30) blunts **invest + autonomy-up ONLY**; **subsidy left full-strength
    (Q2)**; release / autonomy-down / VS-3 never softened; a spiral-band `recovery_hint`
    variant names the levers that still work (land grant joins that copy when VS-3 lands).
  - **One-way (Q4):** VS-R never writes `authority_tracker` back.
  - **Courting scale:** `attempt_vassal_courting` unlock widens (50 → 50 + up to 15)
    and effectiveness scales (×1.0 → ×1.5) by the player's grip; 0/×1.0 at healthy grip.
  - **Coalition-defection (Q7):** **NOT built** — v1 ships grip-accelerated *independent*
    rebellion (reuses `check_vassal_rebellion` unchanged; the coupling just feeds loyalty
    drift into the existing collapse condition). "The Defection" stays a GR9 slice.
- **Recorded deviations (GR9):**
  - **§Q5 layering — partial:** relocated only the two shared breakpoints
    (`AUTHORITY_SUPPRESS_ABOVE`/`ACCELERATE_BELOW`) to `authority.py` (jealousy
    re-imports them). `get_authority_proxy`/`is_capital_threatened` **stay in
    `jealousy.py`** — jealousy-internal in use, VS-R never reads them; full relocation
    is a follow-on tidy, not a v1 need. No circular import (authority.py stays a leaf;
    the diplomacy war-score import is function-local).
  - **§Q4 optional −4 floor below grip 15 — HELD** for post-playtest tuning (owner:
    §2.6-Q4). v1 ships the single −2 spiral term; `VS_R_DRIFT_CAP` already bounds any
    future floor.
- **Behavior test:** `test_vassal_authority_coupling.py` (42) — banded curve, grip math
  + edge cases, boot-dormancy/byte-identical pins, lever-blunting (invest/autonomy-up
  only; subsidy/release/autonomy-down unsoftened), courting-scales-with-weakness,
  one-way/no-writeback, no-new-serialized-fields, **recoverability (winning arrests the
  spiral; full-3-satellite collapse ≥ 8 turns)**, and GR5 enemy-lord symmetry. Suite
  **13,219/3**, ruff clean, no `.gd` touched; a 5-lens adversarial review returned zero
  confirmed findings.
- **Playtest follow-up (July 14, 2026 — `docs/audits/VASSAL_PLAYTEST_2026_07_14.md`):** a
  live europe_1805 playtest confirmed VS-R fires as designed (grip spiraled to ~20 at a
  healthy authority 65 as Paris fell; invest blunted +10→+4; spiral hint fired) and routed
  10 findings — **all bug-fixes landed the same session** (`BUG_FIXES.md` §Vassal Playtest
  Findings, `test_playtest_fixes_2026_07_14.py`). VS-R-adjacent: the spiral recovery hint had
  named a VS-R-blunted lever ("grant autonomy") + a nonexistent "subsidy" + a dead "garrison
  their capital" lever → rewritten to a single-source grip-aware `recovery_hint_for_grip`;
  Talleyrand's `<35` advisory made grip-aware; the autonomy-up blunt now explained; a blocked
  co-belligerent rebellion no longer orphans the vassal at a stale `VASSAL` state (graceful
  independence). Design residuals → `DESIGN_REFINEMENT.md` VP-D1 (garrison wire-or-remove),
  VP-D4 (grip memoization). The §Q4 −4 floor remains HELD.

---

## 3. Open questions for the gate

**VS-3 questions** (the land-grant slice — §1):

1. **Sequencing** — VS-3 immediately after Sweep 4, or hold the whole Vassal
   Deepening set until the Combat Overhaul program exits? (Recommendation: VS-3 can
   land standalone; VS-R follows now that its research is done.)
2. **Contiguity** — require a granted province to touch the vassal's territory, or
   allow any lord-owned province? (Recommendation: contiguity — cleaner map, blocks
   nonsense gifts.)
3. **Provenance** — add a serialized `granted_regions` list per vassal for
   reclaim-on-rebellion, or accept that granted land is indistinguishable once
   transferred? (Recommendation: add it — the reclaim beat is worth one field.)
4. **Region-worth floor** — minimum income to be grantable, or allow token gifts at
   token loyalty? (Recommendation: no hard floor, but worth-scaled bonus already
   makes token gifts near-useless.)
5. **VS-3 numbers** — GRANT_LOYALTY_BASE/CAP/INCOME_DIVISOR, cost (DP/AP), cooldown.

**VS-R questions** — the six decisions in **§2.6** (signal choice, subsidy softening,
coalition-defection now/later, the optional −4 floor, layering relocation, copy bless),
with recommended numbers in **§2.5**. Research is complete; the memo makes a
recommendation on each.

---

## 4. Systems touched (grounding)

| Concern | Seam |
|---|---|
| Region control transfer | `region.controller = vassal` (`settlement_ratify.py:267`) |
| Vassal loyalty / tribute | `vassal.py` (`process_vassal_loyalty`, `TRIBUTE_RATES`, `invest_in_vassal` pattern) |
| Wizard action list | `diplomatic_advisory.py` (vassal action block, `invest_vassal` kind) |
| Wizard sub-picker | `diplomacy_wizard.gd` (war_id picker pattern, `_structured_payload_for_action`) |
| Player authority (grip) | **derived `get_imperial_grip`** (new, `authority.py`) — `authority_tracker` court component + territorial-collapse term; **NOT** raw `authority_tracker` (doesn't spiral on military collapse) or `nation_authority[player]` (inert dead code) |
| Authority signal / GR5 | `get_authority_proxy` (`jealousy.py:343`, enemy 75/50/25); reuse gives enemy lords the coupling for free |
| Authority bands precedent | `jealousy.py:66-67` (`AUTHORITY_SUPPRESS_ABOVE=70` / `ACCELERATE_BELOW=30`) — VS-R anchors on the same two lines |
| VS-R drift hook | `vassal.py:353→361` (`_contribute` between relation term and `# Apply delta`) |
| VS-R lever multiplier | `invest_in_vassal:822`, `change_vassal_autonomy:875` (upgrade only) |
| VS-R courting scale | `attempt_vassal_courting` (`vassal.py:1132/1152/1154`) |
| Defection / rebellion (v1) | `check_defection_cascade:654` (probabilistic roll) → `check_vassal_rebellion:505` |
| Coalition-defection (GR9 follow-on) | `coalition.py:1173/1234` (static `members`) + `diplomacy.py:7996` |
| AI parity (GR5) | `enemy_ai.py` (new grant/rescue rung, same executor); VS-R symmetric via `get_imperial_grip(lord)` |

Full seam-by-seam map + recommended constants in the research memo
[`docs/audits/VASSAL_AUTHORITY_COUPLING_RESEARCH_2026_07_14.md`](audits/VASSAL_AUTHORITY_COUPLING_RESEARCH_2026_07_14.md) §6.

---

## 5. VS-4 — Loyalty-gated call-to-arms (loyalty has military teeth)

*Added July 15, 2026 (user direction: "at low loyalty they don't send troops to help you in wars").*

**The gap:** today loyalty drives *drift → rebellion* plus a few soft modifiers, but a
wavering-but-not-yet-rebelling vassal still fights your wars at full strength. Historically a
disaffected satellite dragged its feet or withheld its contingent long before it defected
(Bavaria/Saxony, 1813). Loyalty should be **militarily consequential** — a low-loyalty vassal
will not send troops to the lord's wars.

**Mechanic shape (numbers escalate to the build gate, in-band tunable):**
- A vassal is already a co-belligerent in the lord's wars (the shared-war path, `vassal.py`;
  Puppet/Satellite marshals are assimilated, Autonomous stay AI-controlled). VS-4 gates the
  *contribution* on loyalty, graded through a single-source helper
  `vassal_military_contribution(world, vassal) -> tier`:
  - **Loyal (≈ ≥ 60):** full contribution (as today).
  - **Wavering (≈ 35–60):** reluctant — reduced / last-to-arrive (its marshals won't auto-reinforce
    the lord's battles, or arrive later); a legible "drags its feet" state.
  - **Disaffected (< ≈ 35):** **refuses** — withholds its contingent / declines the call-to-arms
    even while nominally still a vassal. Its own defense is unaffected; it just won't fight *for you*.
- GR5-symmetric (an enemy lord's disaffected satellite withholds too). Legible: the morning
  dispatch / muster preview names it ("Bavaria will not march — loyalty 31"); the existing recovery
  hint already surfaces in that band. This is the natural **soft precursor to VS-6 defection** — first
  they stop fighting for you, then they flip.

**Landing contract (GR9):** owner §5; slice **VS-4** — ✅ **LANDED July 16, 2026.**
The build verification the spec mandated ("verify the co-belligerent / assimilation seam")
re-anchored the substrate: the "shared-war path" in vassal.py is the +2 loyalty bonus, NOT
co-belligerence — actual co-belligerence is the war-cascade vassal auto-join in
`diplomacy.py _process_war_cascade`, and assimilated marshals are permanently lord-nation
(no per-war contingent object exists). What landed:
- **Single source `vassal_military_contribution`** (loyal ≥60 / wavering 35–59 /
  disaffected <35; constants in-band tunable) consumed at four seams so shown = applied.
- **Disaffected → refuses NEW calls:** both war-cascade vassal arms gate; the refusal
  emits a `vassal_refuses_call` cascade entry (carries loyalty + war_id for VS-6),
  a `refused_disaffected` war-entry ledger row, declare-war message copy, a HIGH
  player notification, a dispatch template, and a campaign-log one-liner.
  **No retroactive mid-war exit** (pinned) — a call-to-arms, not desertion.
- **Wavering → marshals withheld:** assimilated ex-vassal marshals (keyed off the
  serialized `marshal.original_nation`) are excluded from auto-reinforcement
  (Rule 1b in `_is_reinforcement_eligible`) and the muster preview
  (`vassal_wavering` reason + display copy) — UNLESS under an explicit SUPPORT
  order for the primary (the A-D4 hostile pattern; **direct orders stay obeyed**,
  pinned — no collision with the objection/defiance hierarchy). Zero new
  serialized fields.
- GR5-symmetric (enemy lords' satellites tier identically). Honest caveat: at the
  1805 boot the three satellites have zero marshals, so the marshal-level teeth are
  latent until mid-game vassalizations; the refusal beat is live for any new war.
- Drive-by: the `vassal_auto_join_war` one-liner read `overlord` while the emitter
  passes `lord` (rendered "Unknown's war") — fixed.
Test `test_vassal_call_to_arms.py` (20): tier matrix, both cascade arms, loyal/wavering
auto-join unchanged, no-retroactive-exit pin, SUPPORT override, gate released on
de-vassalization, muster pairing, ledger row, GR5, legibility surfaces.

---

## 6. VS-5 — Vassal creation & transfer in peace deals (settlement vassalage)

*Added July 15, 2026 (user direction: "assure vassals can transfer or be created in peace deals").*

The settlement package **already supports creation** — `vassalage` / `subjugation` clauses
(`{from: court, to: proposer_leader}`, `settlement_actions.py:1234`, with `evaluate_vassalage_eligibility`)
— and **liberation** (free a vassal). VS-5 assures both are reachable and adds **transfer**:

1. **Creation reachable in the guided flow (assure):** confirm the vassalage / subjugation /
   liberation clauses surface on the **guided peace surface + the F1 diplomacy wizard** (not just the
   debug/typed path), with the existing per-court eligibility.
2. **Transfer (NEW):** a peace clause that changes a vassal's *lord* —
   `{type: "vassal_transfer", vassal, from_lord, to_lord}` → `world.vassals[vassal]["lord"] = to_lord`
   with marshal-assimilation re-key, tribute re-home, and a loyalty reset **toward the new lord** (a
   transferred vassal is not instantly loyal — ties to VS-4/VS-R). This is the machinery **VS-6's
   "become someone else's vassal" outcome reuses**, and it lets a victorious coalition re-home a
   defeated power's satellites at the table.

**Notes:** transfer rides the same control-transfer seam as territory (`settlement_ratify`); the old
lord forfeits tribute, the new lord inherits it at the vassal's autonomy rate; GR5 AI parity (the AI
can impose/accept creation & transfer in its own settlements).

**Landing contract (GR9):** owner §6; slice **VS-5** — ✅ **LANDED July 16, 2026.**
- **Creation ASSURED (pin-tests, zero build):** vassalage/subjugation/liberation were already
  live end-to-end on the guided surface (suggestions → demand-add verbs → ratify); pinned in
  `test_settlement_vassalage.py::TestRegistration`.
- **Transfer (NEW):** clause `{type: "vassal_transfer", from: from_lord, to: to_lord, vassal}`
  (canonical from/to = the LORDS, so burden partitioning/concession credit/pair-matching work
  like forced_alliance; the vassal is the excluded subject, like liberation's `vassal_nation`).
  Registered across the full clause lifecycle: schema + live dependency set + burden/non-trivial/
  harshest-target sets + harshness 0.3 (a lord LOSING a satellite prices like liberation, not
  like a new subjugation) + concession credit 100 + hegemony projection step 4b + validator
  (`evaluate_vassal_transfer_eligibility`: is-their-vassal, lords on opposite war sides, WPS-B
  power cap on the RECEIVER; new refusal code `transfer_target_not_their_vassal`) + guided
  suggestion ("Claim {court}'s vassal {vassal} as your own", Talleyrand voice line) + demand-add
  verb (demand-only) + display labels.
- **Apply handler:** package-level in `_apply_settlement_terms` (next to liberation — the
  transferred vassal is typically NOT a war-pair member, so the per-pair plan structurally
  cannot host it; the spec's "same seam as territory" was imprecise). Closes any live WAR
  between receiver and vassal via `cleanup_war_end` first.
- **Shared domain helper `transfer_vassal`** (vassal.py — VS-6's outcome-2 reuses it): lord
  re-key, UNCONDITIONAL loyalty reset to `TRANSFER_LOYALTY_RESET=30`, assimilated-marshal
  re-key (original_nation preserved for the rebellion path), **VS-3 `granted_regions`
  CLEARED**, old pair→PEACE / new pair→VASSAL + R48 reconcile, rebellion popups/dialogues
  cleared, CS-membership dropped when leaving the player's web, NO release cooldown,
  autonomy/tribute carry over. Dispatch template + log event `vassal_transferred`.
- **Drive-by fixes (pre-existing, verified):** the hegemony projection's liberation step never
  matched canonical clauses (read `to`/`vassal`/`nation`; canonical carries only
  `vassal_nation`) and its vassalage step read from/to REVERSED — both fed the AI's
  acceptance pricing. Fixed + pinned.
- **AI parity scope-down (structural deviation, recorded):** v1 = accept-side pricing parity
  only; AI-AUTHORED dependency clauses (an AI demanding the player's vassalage) are a new
  fantasy → deferral row `DESIGN_REFINEMENT.md` VP-D8.
- Test `test_settlement_vassalage.py` (29): registration/reachability pins, eligibility matrix,
  validator routing, domain-helper bookkeeping, ratify apply (incl. WAR-pair-closed-first and
  stale-clause no-op), hegemony-fix regressions, display surfaces.

---

## 7. VS-6 — The Defection: coalition-flip as a BRIBE (supersedes the §2.7 stub)

*Added July 15, 2026 (user direction: "vassals flipping is essentially a bribe from the coalition —
they would want something — and they either become free or someone else's vassal; if free they are
guaranteed at war with you").*

Refines the deferred "coalition-join" GR9 slice (§2.7). *(Baseline correction, recorded at the
July 16 build: today's DEFAULT rebellion outcome is already WAR — `check_vassal_rebellion`'s main
branch; the F8b graceful-PEACE break is only the war-instance-failure FALLBACK. VS-6's genuinely
new content is therefore the bribe gate, briber attribution + payment, and the transfer outcome —
not the war itself.)* VS-6 makes a coalition-driven flip a **transactional defection**: the vassal
is *bribed* away, wants *something*, and the outcome is one of two — not a quiet neutral break.

**The bribe (the vassal wants something):** a flip is NOT automatic even at rock-bottom grip — a
coalition (or a specific coalition member) must **offer the wavering vassal a concession it values**:
a sovereignty guarantee, land, a subsidy, a better autonomy deal, or protection of its frontier (the
Treaty-of-Ried dynamic VS-R already models on the courting side). The offer is what tips a *courtable*
vassal (low loyalty + lord in a grip spiral, per VS-R's `attempt_vassal_courting`) from "withholding
troops" (VS-4) into "changing sides." **No willing/able briber → the vassal stays** (or breaks to plain
independence via the existing path). This is the "they would want something" gate.

**Two outcomes when the bribe lands:**
1. **Becomes FREE (independent) — and GUARANTEED AT WAR with the former lord.** Unlike today's
   graceful-PEACE break, a coalition-*freed* vassal turns **hostile**:
   `set_diplomatic_state(vassal, old_lord, "WAR", "coalition_defection")` and (typically) joins the
   coalition's war against the old lord. The coalition "liberated" them; they are now an enemy
   belligerent. *(This is the deliberate contrast to F8b's neutral break.)*
2. **Becomes SOMEONE ELSE's vassal** — transfers to the bribing coalition member as their new lord
   (**reuses VS-5 transfer**): the new lord paid the concession, inherits the tribute, and the vassal
   starts at low loyalty to *them* (VS-4/VS-R apply immediately — "changed masters, not necessarily
   happier").

**Which outcome:** driven by what the coalition offered — a member willing to *take responsibility*
(and pay) gets a vassal (outcome 2); a coalition that only *frees* it (cheaper — e.g. Britain funding
independence) yields outcome 1 (free + hostile). Branch weights / bribe costs escalate to the gate.
**GR5-symmetric:** the *player's* coalition can bribe an *enemy's* satellites the same way (a real
strategic lever, not just a punishment). Enemy-AI must be able to *offer* the bribe and *defend* its own
satellites — see **VP-D6** (enemy-AI grip-awareness), sequenced alongside.

**Landing contract (GR9):** owner §7; slice **VS-6** — ✅ **LANDED July 16, 2026.**
- **`attempt_vassal_bribe`** (vassal.py) runs in the AI diplomatic phase immediately AFTER
  courting and **resolves immediately** — the bribed vassal is transferred/freed before
  `advance_turn`'s cascade/rebellion chain sees it (structural double-fire guard; zero new
  serialized fields — cooldowns ride `ai_proposal_cooldowns`: per-pair `defect|` 5 turns +
  per-vassal `defect_pause|` 1-turn latch so N members can't pile on one vassal in a turn).
- **The bribe gate:** briber at WAR with the lord + can pay; vassal courtable at loyalty <35
  (**deliberately the VS-4 disaffected line** — "first they stop fighting for you, then they
  flip", pinned) or <50 while the lord's grip spirals (<30, the Ried window). Probabilistic:
  chance = (pivot − loyalty)/100 × `courting_effectiveness_scale(grip)`, pivot 40 healthy /
  50 in spiral. A failed approach burns half the purse and warns the lord's court.
- **Outcome (a) transfer:** briber passes the WPS-B power cap AND pays 600g → new lord via
  **VS-5 `transfer_vassal`** (loyalty resets to 30 — "changed masters, not necessarily happier").
- **Outcome (b) free + HOSTILE:** 300g (the cheaper "liberation" purse) →
  `_defect_vassal_free_and_hostile`: WAR with the former lord via
  `ensure_war_instance_for_pair(entry_path="coalition_defection")` + cascade, **VS-3 granted
  provinces reclaimed**, marshals return, sibling −10 shock, relation −50 lord / +30 briber,
  player-scoped threat relief; armistice-respected + F8b war-instance-failure fallbacks kept.
- **No `coalition.members` mutation (structural deviation, recorded):** free+war grants a WAR
  state + war instance, never coalition membership (the first-ever `members.append` would
  ripple through posture/friction/exhaustion/dissolution consumers). Copy says "takes the
  field", never "joins the coalition". The war is militarily nominal for marshal-less 1805
  satellites — a deliberate, documented diplomatic beat.
- **Legibility:** CRITICAL "{vassal} DEFECTS!" notification, dispatch template, campaign-log
  `vassal_defected` one-liner (both outcomes' copy) — NOT courting's debug-print sink.
- **GR5:** lord-neutral (any lord's satellite biddable — pinned with a synthetic enemy-lord
  web); the PLAYER-side bribe verb is deferred with owner row `DESIGN_REFINEMENT.md` VP-D9.
Test `test_vassal_defection.py` (18): gate matrix (war/loyalty/gold/latch/cooldown), spiral
window widening, both outcomes, armistice-respected, VS-3 reclaim, sibling shock, GR5, legibility.
Supersedes the §2.7 "graceful independence is the only coalition path" note for *coalition-driven*
flips; plain (non-coalition) collapse keeps the independent-rebellion path.

---

## 8. Vassal Depth — build sequence (the sensible phase-out)

**✅ THE WHOLE QUEUE LANDED July 16, 2026 in one session** (pre-build seam-verification →
six slices, committed in order on master). As-built order — a **Slice 0 was promoted** at
verification because three later slices depended on it:

0. **Slice 0 — Nation-neutral vassal substrate + VP-D1 garrison wire** ✅ (`1082382`) —
   lord-param on invest/change-autonomy (+the missing lord gate that let any AI path drain
   the PLAYER's DP), player-scoped coalition threat, `_acting_nation` executor wiring;
   VP-D1 wired presence-based flat +2 (the authored +5..+8 ladder discarded — it trivialized
   the −2 drift economy).
1. **VS-3 — Land Grants via the F1 diplomacy wizard** ✅ (`e2f72ad`) — §1.3 landing record.
2. **VS-4 — Loyalty-gated call-to-arms** ✅ (`02bd773`) — §5 landing record.
3. **VS-5 — Settlement vassalage (create assured + transfer)** ✅ (`5cdf354`) — §6 landing record.
4. **VS-6 — The Defection (bribe → transfer OR free+war)** ✅ (`6e2bd53`) — §7 landing record.
5. **VP-D6 — Enemy-AI grip-awareness (P1.6 shore-up rung)** ✅ — closes the loop: the AI
   defends its satellites with the same levers (incl. VS-3 grants) the player has, and pays
   VS-6 bribes through `attempt_vassal_bribe`. Row closed in `DESIGN_REFINEMENT.md`.

Sequencing rationale (held): VS-4 and VS-5 were independent floor-raisers; VS-6 reused VS-5's
transfer and VS-4's "wavering → withholding" precursor. Blessed defaults remain in-band
tunable; each landing record lists its structural deviations (all grounded in the July 16
seam verification).

---

*Prepared July 14, 2026; VS-4/VS-5/VS-6 + build sequence added July 15, 2026 (user design direction).
VS-3 ✅ BLESSED to build (masthead); **VS-R research COMPLETE** (memo landed July 14, 2026) — §2
gate-ready. Per-slice numbers escalate to each build gate.*
