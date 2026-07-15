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

### 1.3 Landing contract (Golden Rule 9)

- **Owner:** this spec §1. **Landing slice:** VS-3 (single session, post-gate).
- **Completion definition:** a player can, from the F1 wizard, cede an eligible
  province to a vassal; control transfers, loyalty rises by the worth-scaled bonus,
  the lord loses the income, the vassal tributes it, cooldown arms, AI does the same.
- **STATUS line:** added at land.
- **Behavior test:** `test_vassal_land_grant.py` — eligibility gates, worth-scaled
  loyalty, income/tribute handoff, cooldown, reclaim-on-rebellion, GR5 AI parity,
  wizard payload shape, serialization (`granted_regions` if adopted).

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
**coalition-defection ("The Defection") as a separate GR9 follow-on slice**.

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

*Prepared July 14, 2026. VS-3 spec-complete pending a bless; **VS-R research COMPLETE**
(memo landed July 14, 2026) — §2 gate-ready with recommended numbers. No code until the
gate blesses §2.5–2.6.*
