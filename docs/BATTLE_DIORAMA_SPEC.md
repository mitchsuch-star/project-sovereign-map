# Battle Diorama Popup — PRELIMINARY SPEC (for Fable review)

> **STATUS: PRELIMINARY / UNBLESSED.** This is a jumping-off document drafted from a
> July 17, 2026 design conversation, not an approved slice. It exists so **Fable can
> review the concept, the asset strategy, and the effort tiers before any build**, and
> so a later USER DESIGN GATE has something concrete to bless or cut. Nothing here is
> committed to the queue except "Fable reviews this after the econ research pass."
> Numbers, art choices, and layout are illustrative, not blessed.

## 1. The idea in one line

When a battle resolves, show it as a **framed popup tableau of mini soldiers** — two (or
more) crowds of small figures scaled to committed strength, casualties toppling as the
report is read out, an outcome banner, a casualty tally, and the Berthier line — instead
of (or alongside) the current text-only battle report.

## 2. Why it's on the table

The game's own **Creative Audit** (`docs/audits/CREATIVE_AUDIT_2026_07_10.md`) scored the
two weakest pillars **combat legibility 4.5** and **narration 3.5**, with the recurring
verdict *"the game generates great stories and doesn't tell them."* Wave 6 lifted
legibility to ~7 **with text**. A visual tableau is the natural next lift: it makes
*"Ney shattered Mack, 8k for 2k"* legible at a glance, and — critically — it's the **only
surface that can show a coordination failure** (the Davout–Bernadotte −2 "no-show" beat)
as a visible hole in the line rather than one buried sentence.

## 3. What already exists (why this is cheaper than it sounds)

| Asset | Where | Reuse |
|---|---|---|
| Piece sprites (4-layer body/coat/base/shadow, L/R facing, 3 arms, faction coat tint) | `assets/ui/pieces/`, `scenes/war_table_piece.gd` | The tint/facing pipeline transfers; the round *base* is the thing to drop for a crowd figure |
| Battle report data (outcome, per-side casualties, original strength, modifier snapshot) | `backend/game_logic/battle_report.py` (`_pick_observation`, `battle_result` dict) | Feeds figure counts, who's winning, who falls, the modifier chips |
| Multi-marshal coordination + reinforcement context (who contributed what) | `backend/commands/combat_executor.py` (`_calculate_coordination_context`, `_calculate_reinforcements`) | The per-contingent breakdown for the multi-army case |
| Offline 2D sprite pipeline (Pillow+numpy, deterministic, CC0-clean) | `tools/gen_war_table_pieces.py` | The route to period-correct new poses if we ever want animation |
| Modal-popup infra (CanvasLayer, base class, standard theme) | `popup_base.gd`, `dialog_manager.gd` | The diorama is a new scene on a free layer |

The genuinely-new work is a **battle-diorama scene** that lays out N pieces per contingent
and plays a short scripted sequence. Two of the three hard parts (art substrate, data) are
already paid for.

## 4. Effort tiers (the real decision)

| Tier | What it is | New art? | Effort | Prelim verdict |
|---|---|---|---|---|
| **A — Static tableau** | Two lines of figures sized to committed strength; clash flash; casualties greyed/toppled via Tween; winner banner; casualty tally; Berthier line. **No frame-animation.** | Recolored static figures only (or reuse existing pieces base-stripped) | ~1 slice (`.tscn` + `.gd` + fixture, reuse tint path, fed by battle_report) | **Recommended first** |
| **B — Scripted skirmish** | Figures advance, melee jitter, artillery puff, cavalry sweep, staged casualties timed to the report, rout animation | Yes — needs "fire" + "fall" poses (LPC or own pipeline) | 2–3 slices + animation-timing polish | Only after A proves the format |
| **C — Live sim** | Many small soldiers with per-unit AI | Yes, plus a sim system | Large; scaling risk (GR8) | **No** (category error) |

**The mockups proved Tier A reads as a battle with static art alone** — the toppling-tween
tableau conveyed "Ney crushed Mack" without a single firing frame. That is the core reason
to ship static first.

## 5. Multiple armies (the case that makes it worth building)

Sovereign battles are not 1-v-1: `combat_executor` resolves a primary marshal + reinforcing
corps, and coalition wars can put **two nations' corps on the defending tile**. The tableau
handles this by **scaling on contingents (banners), not raw soldiers**:

- Each corps = a small **labeled block** (marshal name + corps + nation), capped at ~8–10
  figures regardless of true strength (a slider count, not one dot per 1,000 men).
- **Coalitions carry mixed coat colors** on one side (e.g. Austrian off-white + Russian gold)
  — an instant-read legibility win text can't match; you see *which nation's* corps broke.
- Beyond ~4 contingents a side, **cap and summarize the tail** ("+2 corps in reserve"),
  same discipline the map labels already use.
- The **failed-to-arrive / routed / withdrew-in-good-order** states are shown as a greyed,
  off-line block — this is the drama surface (Bernadotte's absence becomes a visible gap).

Crucially, **multi-army is nearly free in Tier A** (more placed static figures, more labels)
and **expensive in Tier B** (every faction is another uniform recolor, every routing corps
wants death frames). Another point for static-first.

## 6. Reference mockups (jumping-off point)

Two HTML mockups were rendered in the design conversation and are the visual anchor for
this spec. Re-create with `mcp__visualize__show_widget` or port to Godot layout:

**Mock 1 — single engagement (Ney vs Mack at Ulm).** France 42k (blue coats) vs Austria 30k
(off-white); ~14 vs ~12 capped figures; 2 French / 7 Austrian toppled+greyed; dashed centre
line + crossed-sabres clash glyph; header (battle name + marshals + province); footer with
"Decisive French victory / Mack's corps shattered — routed", three stat tiles (French losses
3,100 / Austrian losses 21,400 / Ney shock +18%), and the Berthier italic line.

**Mock 2 — coalition, multi-army (Austerlitz).** France 74k = **three** labeled corps blocks
(Ney III / Lannes V / Soult IV) **plus a greyed off-line "Bernadotte I Corps — failed to
arrive"** block; Coalition 82k = **Mack (Austria, off-white)** shattered + **Kutuzov (Russia,
gold)** withdrawn mostly intact; footer surfaces "coordination bonus ×1.25 · Kutuzov withdrew
in good order" and the Berthier line names Soult/Lannes/Bernadotte by role.

Visual language established by the mocks: navy `#141b2e` panel + gold `#b8912f` frame; serif
(`--font-voice`) for battle name + outcome + Berthier; sans for labels/stats; faction color on
coats only; toppled = `rotate(~78deg)` + `opacity 0.3`; standard glyph `⚔` at the clash line;
per-corps standard glyph `⚑` in the coat color.

## 7. Data contract (backend — likely zero or near-zero new work)

The diorama should be **display-only** (Golden Rule 6 — never read by routing/mechanics) and
**fog-safe** (Golden Rule per `project_marshal_summary_fog_boundary`): it renders only what the
player may already see in the battle report. Preferred: **reuse the existing `battle_result`
payload** the report already emits; if a per-contingent breakdown isn't already in the
player-facing payload, add a display-only `contingents[]` list (marshal name, nation, arm,
committed strength, casualties, status ∈ {engaged, reinforced, routed, withdrew, failed_arrive})
on the same fog-filtered surface — **no new serialized world fields**.

## 8. Definition of Done (Tier A, if blessed)

- [ ] `battle_diorama.tscn` + `.gd` on a free CanvasLayer; registered via `dialog_manager` (modal).
- [ ] Fed by the existing/extended battle_result payload; **skippable / instant-complete** (repeat viewings must not drag — decays to novelty fast).
- [ ] Contingent-banner layout with per-side figure cap + tail summary; coalition multi-tint.
- [ ] Casualty topple + winner banner + casualty tally + modifier chips + Berthier line.
- [ ] Faction coats via the existing `Utils.NATION_COLORS` / tint path; CC0 recolored figures or base-stripped existing pieces (license logged in `THIRD_PARTY_LICENSES.md`).
- [ ] A **mock-data fixture** so pacing can be tuned without a live battle.
- [ ] Engine boots clean (grep `SCRIPT ERROR`) per the standing `.gd`-slice rule.
- [ ] Behavior test: `tests/test_battle_diorama.py` — the backend payload carries contingents, casualties, outcome, and status flags correctly for a single engagement AND a multi-army coalition battle, fog-filtered (enemy contingents present only at appropriate visibility).

## 9. Public asset options (verified July 17, 2026)

| Pack | License | Era / style | Animations | Fit |
|---|---|---|---|---|
| [Universal LPC Spritesheet Generator](https://liberatedpixelcup.github.io/Universal-LPC-Spritesheet-Character-Generator/) | **CC-BY-SA 3.0 / GPL** | generic, modular uniforms + hats | walk / thrust / hurt / **death** ✓ | Best for *animated* (Tier B); ShareAlike obligation + credit |
| [Pixel Art Top Down Soldiers](https://opengameart.org/content/pixel-art-top-down-soldiers) | **CC0** | 32×32, soldier/spearman/officer | none | Cleanest license; Tier A static, poses faked by tween |
| [Sput's Soldier Pack](https://opengameart.org/content/sputs-soldier-pack) | CC0 | modern (AK-47) | 3 move frames | Wrong century |
| [Top-down Military Set](https://opengameart.org/content/top-down-military-set) | CC0 | modern | limited | Wrong era |
| Own Pillow pipeline (`tools/gen_war_table_pieces.py`) | CC0 (self-authored) | period-correct | as drawn | Only route to period-correct **and** CC0 **and** animated |

**Key finding:** there is **no CC0 pack of animated Napoleonic line infantry**. CC0 gets you
static or modern; period-correct + animated lives only in LPC (ShareAlike) or the own pipeline.
This is exactly why **static-first (Tier A)** is the low-risk path — it needs no animated art.

## 10. Open questions for Fable / the design gate

1. **Diorama vs. text — replace, augment, or toggle?** Does the tableau replace the text report,
   sit above it, or ride behind a "watch the battle" button? (Repeat-viewing fatigue argues for
   skippable/optional.)
2. **Does static-tableau actually lift the legibility pillar in live play,** or does it need at
   least the Tier-B fall/fire poses to feel like combat? (Prototype-then-measure, like the sweeps.)
3. **Figure-count mapping:** fixed cap per corps (clean, abstract) vs. proportional-to-strength
   (legible scale, messier). Mocks used a cap.
4. **Asset path:** accept LPC's ShareAlike for real animation, or stay CC0-static / own-pipeline?
5. **Scope boundary (GR9):** is this one Tier-A slice with a named landing, or does it invite an
   open-ended "battle animation" backlog? It must land as a bounded slice or not start.

## 11. Recommended sequencing (prelim)

1. **Fable reviews this doc** after the econ research pass (per the STATUS queue).
2. If greenlit, **prototype Tier A** with a CC0 recolored static pack + mock fixture; measure the
   legibility lift in a live playtest.
3. **Only then** decide whether Tier B animation (LPC ShareAlike or own poses) is worth buying.
4. Multi-army is in-scope for Tier A from the start (it's free there); it is the main argument for
   the whole feature.
