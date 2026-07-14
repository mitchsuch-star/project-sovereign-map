# Vassal Deepening Spec — Land Grants & Authority Coupling

> **Status:** DRAFT — design gate PENDING. Authored July 14, 2026 as the phase that
> follows Combat Overhaul Phase 5 (Vassals). **Nothing here is built.** VS-3 is
> spec-complete and buildable after a bless; **VS-R is research-first** — next
> session runs the research memo, then a user gate sets the numbers before any code.
>
> **Owner routing:** CLAUDE.md Current Phase Queue → this spec. Sits after the
> Combat Overhaul program (or interleaves after Sweep 4 — user's call at the gate).

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

## 2. VS-R — Authority ↔ Vassal-Loyalty Coupling (RESEARCH-FIRST)

**Fantasy:** "The Empire holds because *you* hold. When Napoleon falters, the
satellites smell weakness — and only real concessions keep them."

Today vassal loyalty drift is **independent of the lord's authority**. VS-R couples
them so a **spiral** in the Emperor's grip loosens the whole satellite web, and at
rock-bottom authority the cheap levers (invest, a token subsidy) no longer suffice —
only **land, autonomy, or a large subsidy** arrest defection.

### 2.1 This is RESEARCH-FIRST — next session's job

The next session **must produce a research memo** (`docs/audits/VASSAL_AUTHORITY_COUPLING_RESEARCH_YYYY_MM_DD.md`)
answering the questions below with measured numbers, **then a user gate** sets the
constants **before any build**. Do not code VS-R off this draft.

### 2.2 Research questions

1. **Which authority signal?** Two exist:
   - `world.authority_tracker.authority` (0–100) — Napoleon's *marshal-deference*
     grip (defer-to-marshals erodes it; the exploit-guard). This is the "spiral" the
     brief evokes — a weak, deferring Emperor.
   - `world.nation_authority[player]` — the per-nation *strategic* authority.
   Decide which drives the coupling (or a blend). Recommendation to test: the
   `authority_tracker` grip, since the brief ties loss-of-vassals to *Napoleon
   spiraling*, not a strategic stat.
2. **Coupling curve.** A drift modifier as a function of authority, **coherent with
   the jealousy bands** (jealousy already treats >70 as calm and <30 as the
   death-spiral zone — `jealousy.py`). Proposed shape to measure:
   - authority ≥ 70 → **+1** vassal drift (empire ascendant),
   - 40–69 → **0**,
   - 20–39 → **−2**,
   - < 20 → **−4** *and* elevated defection risk.
3. **The "no cheap recovery" clause** — the crux of the brief. When authority is in
   the spiral band, the cheap levers must be **blunted**: invest gives reduced
   loyalty, an autonomy-flip alone is insufficient, and only a **land grant (VS-3),
   a large subsidy, or full release** meaningfully arrests defection. Model this as a
   *lever effectiveness multiplier* scaled by authority, and confirm it's dramatic
   but **recoverable** ("he MAY lose them" — risk, not certainty).
4. **One-way or feedback loop?** Does holding vassals loyally *bolster* authority
   back? A two-way loop is thematically rich but **risks an unrecoverable death
   spiral** — must be bounded. Default recommendation: **one-way** (authority →
   loyalty) for v1; revisit a bolster term only if v1 feels inert.
5. **Interaction with jealousy.** Jealousy *already* keys off authority (<30
   acceleration). Ensure VS-R doesn't double-count or compound into an uncontrollable
   collapse when both fire at once.
6. **Boot-band & fixture safety.** At boot authority is 100 → coupling is
   dormant/positive. Confirm zero perturbation to the E1 economy band, the existing
   vassal fixtures, and the Phase-5 `test_vassal_recovery_lever.py` pins.
7. **Defection mechanics.** At the spiral floor, is it accelerated loyalty bleed into
   the existing rebellion path, or a new direct "defection" event (join the
   coalition / flip to an enemy)? Historically the Rhine states *switched sides*, not
   merely rebelled — worth modeling as a distinct outcome.

### 2.3 Landing contract (Golden Rule 9)

- **Owner:** this spec §2. **Landing slice:** VS-R (post-research, post-gate).
- **Completion definition:** vassal drift responds to the lord's authority per the
  blessed curve; in the spiral band the cheap levers are blunted and only major
  concessions arrest defection; boot is dormant; jealousy interaction bounded.
- **STATUS line + tracking:** the research memo lands first (its own STATUS line),
  then the gate, then the build.
- **Behavior test:** `test_vassal_authority_coupling.py` — band curve, lever-blunting
  in the spiral zone, boot-dormancy, jealousy non-compounding, recoverability.

---

## 3. Open questions for the gate

1. **Sequencing** — VS-3 immediately after Sweep 4, or hold the whole Vassal
   Deepening set until the Combat Overhaul program exits? (Recommendation: VS-3 can
   land standalone; VS-R waits on its research.)
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
6. **VS-R** — everything in §2.2 (research memo first).

---

## 4. Systems touched (grounding)

| Concern | Seam |
|---|---|
| Region control transfer | `region.controller = vassal` (`settlement_ratify.py:267`) |
| Vassal loyalty / tribute | `vassal.py` (`process_vassal_loyalty`, `TRIBUTE_RATES`, `invest_in_vassal` pattern) |
| Wizard action list | `diplomatic_advisory.py` (vassal action block, `invest_vassal` kind) |
| Wizard sub-picker | `diplomacy_wizard.gd` (war_id picker pattern, `_structured_payload_for_action`) |
| Player authority (grip) | `world.authority_tracker.authority`; `world.nation_authority[player]` |
| Authority bands precedent | `jealousy.py` (>70 calm / <30 spiral) |
| AI parity (GR5) | `enemy_ai.py` (new grant/rescue rung, same executor) |

---

*Prepared July 14, 2026. VS-3 spec-complete pending a bless; VS-R research-first —
next session authors the memo, then a user gate sets the numbers. No code until the
gate.*
