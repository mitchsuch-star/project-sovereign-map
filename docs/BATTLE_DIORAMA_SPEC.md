# Battle Diorama Popup — PRELIMINARY SPEC (for Fable review)

> **STATUS: ✅ REVIEWED + QUEUED July 17, 2026 — sequenced AFTER Nation Agendas.** The Fable
> review this masthead once waited on RAN July 17, 2026 (**evaluation of record =
> `docs/audits/BATTLE_DIORAMA_EVAL_2026_07_17.md`, authoritative wherever it and this spec
> disagree — verdict BUILD-IT, fun 7/10**), and the queue decision was made the same day
> (user-directed): **the Tier-A slice is IN the queue, slotted AFTER the 8.5 Nation Agendas
> design gate** — no longer competing for the centerpiece slot. Named landing = ROADMAP
> §Current Phase Queue row **BD** + the STATUS tracking line. **Scope of record = eval §6**
> (the bounded slice: the medium backend `contingents[]` half + the significance-gated Godot
> tableau; the eval §5 cuts stand; completion = eval §6 DoD + `tests/test_battle_diorama.py`).
> Numbers, art choices, and layout below remain illustrative where the eval has not pinned them.

## 1. The idea in one line

When a battle resolves, show it as a **framed popup tableau of mini soldiers** — two (or
more) crowds of small figures scaled to committed strength, casualties toppling as the
report is read out, an outcome banner, a casualty tally, and the Berthier line — instead
of (or alongside) the current text-only battle report.

## 2. Why it's on the table

The game's own **Creative Audit** (`docs/audits/CREATIVE_AUDIT_2026_07_10.md`) once scored the
two weakest pillars **combat legibility 4.5** and **narration 3.5**, with the recurring
verdict *"the game generates great stories and doesn't tell them."* A visual tableau makes
*"Ney shattered Mack, 8k for 2k"* legible at a glance, and — critically — it's the **only
surface that can show a coordination failure** (the Davout–Bernadotte "no-show" beat)
as a visible hole in the line rather than one buried sentence.

> **⚠ Correction (Evaluation §2, July 17, 2026): this rationale is stale — Wave 6 already lifted both
> pillars to their targets (combat legibility → 7, narration → 7.5, both MET).** So the diorama is a
> **delight-multiplier on an already-adequate surface, not a pillar rescue.** That is a legitimate
> thing to build, but the gate must weigh it on those honest terms **against Nation Agendas** (the
> competing 8.5 centrepiece, which targets a genuinely thinner enemy-motivation gap).

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
(`--font-voice`) for battle name + outcome + Berthier; sans for labels/stats; toppled =
`rotate(~78deg)`; standard glyph `⚔` at the clash line; per-corps standard glyph `⚑`.

> **⚠ Correction (Evaluation §3, July 17, 2026): the "faction color on coats" read is FALSE against
> the shipped art.** `gen_war_table_pieces.py`'s July-13 rework makes the figures **carved wood**, not
> tin — the coat mass is oak and the *only* faction-tinted element is the **standard + base-rim band**
> (the `war_table_piece.gd` "tin/pewter" docstring is stale). So the coalition read must ride
> **standard + base-rim + portrait locket, never coats**, and `toppled = opacity 0.3` should become
> **rotate + desaturate + darken (base disc stays put)** — opacity-0.3 reads "ghost/erased." The
> mockup below and the art-brief (Evaluation §8) supersede the mock's "coat color" language.

**▶ Live interactive mockup (built July 17, 2026):** a working Tier-A hero tableau of the Mock-2
Austerlitz coalition case — gilt frame + engraved nameplate, marshal **monogram lockets**, the
France/Coalition split with **multi-tint standards**, the **captured-eagle slide** across the centre
line, **staggered cascade-topple**, **odometer** casualty tiles, clickable **no-show grievance**, and
the **Berthier verdict delivered last**. Published artifact:
`https://claude.ai/code/artifact/f49581da-b77c-4d42-b9d0-a9836ba00ed4` (source in the session
scratchpad `battle_diorama_mockup.html`). It is a *feel-of-the-thing* proof, not the art of record: it
knowingly uses a navy-panel ground (the brief wants a carved-wood/green-baize **tray**) and includes
the **Kutuzov "withdrew in good order"** beat that the Evaluation **cuts as unmodeled** — where they
disagree, the Evaluation memo wins.

## 7. Data contract (backend — a modest slice, NOT "near-zero")

> **⚠ Correction (Evaluation §3, July 17, 2026): "zero or near-zero new work" is INFLATED and holds
> ONLY for a 1-v-1 tableau of the two lead marshals.** Verified against the code: the payload already
> carries outcome/victor, a lead-vs-lead modifier snapshot, and **primary-pair** casualties — so a
> two-leads tableau is genuinely near-free. But the **multi-army flagship — the feature's whole
> justification — is a real MEDIUM backend slice.** The identifier `contingents` exists **nowhere** in
> the backend; per-corps **committed strength does not exist** (only an aggregate weighted float,
> surfaced as prose); the per-marshal `casualty_distribution` dict is **set (combat_executor.py:4225)
> and never read** — dead for display; and any new field must be **registered in `main.py`'s
> `_COMMAND_RESULT_SIMPLE_FIELDS` (352-368) or it is silently dropped**. Bless the `contingents[]`
> builder as its own backend slice; do not sell the feature as a frontend freebie.

The diorama is **display-only** (Golden Rule 6 — never read by routing/mechanics) and **fog-safe**
(per `project_marshal_summary_fog_boundary`): it renders only what the player may already see. The
build assembles a display-only `contingents[]` list — marshal name, nation (off `marshal.nation`),
arm (derived from `marshal.cavalry`/`.artillery`), committed strength (**captured before
`take_casualties` mutates it** — extend the `_co6_lead_pre_strength` snapshot at
combat_executor.py:4000 to all participants), casualties (wire the dead `casualty_distribution`), and
status ∈ **{engaged, reinforced, routed(primary-pair-only), failed_arrive}** (note: **`withdrew` is
UNMODELED and cut** per Evaluation §5) — from `atk_participants`/`def_participants`, fog-filtered on
the enemy side, **registered in the serialization whitelist**. **No new serialized *world* fields**
(the list is built per-battle on the response), but it is real per-battle assembly work.

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
6. **Hostile actions against the player's OWN armies — the defender's-eye view (Fable's call).** The
   tableau isn't only for the player's attacks; the player is frequently the *defender* — an enemy
   marshal storms a friendly corps, a coalition falls on the player's line, a fortified province is
   assaulted or bombarded. **Fable to decide how the diorama frames a hostile action on friendly
   forces:** e.g. is the player's line always drawn on the near/"home" side regardless of who attacked
   (so a loss reads as *your* line breaking, not a mirrored enemy win); does an incoming assault carry
   a distinct alarm register (a red incursion arrow, the enemy standard advancing onto your baize)
   versus the triumphant tone of a player victory; and how do the greyed-block / captured-standard /
   Berthier-verdict beats invert when it's *your* eagle that falls. This is a framing/copy decision,
   not new mechanics — the same fog-filtered `contingents[]` already carries both sides — but it wants
   a deliberate answer so a defeat feels like a gut-punch, not a neutral read-out. (See also Eval §7.)

## 11. Recommended sequencing (prelim)

1. **Fable reviews this doc** after the econ research pass (per the STATUS queue).
2. If greenlit, **prototype Tier A** with a CC0 recolored static pack + mock fixture; measure the
   legibility lift in a live playtest.
3. **Only then** decide whether Tier B animation (LPC ShareAlike or own poses) is worth buying.
4. Multi-army is in-scope for Tier A from the start (it's free there); it is the main argument for
   the whole feature.

---

## 12. Creative review — where the fun actually is (added July 17, 2026)

> **Framing (GR9):** everything below §11 is a **creative menu for the Fable/user gate to pick
> from or cut**, not a committed backlog. Each idea is tagged by cost so the gate can bless a
> bounded Tier-A slice and explicitly drop the rest. Nothing here is queued.
>
> **✅ Adversarially verified July 17, 2026 → `docs/audits/BATTLE_DIORAMA_EVAL_2026_07_17.md`** (18-agent
> grounded eval). The verdict, the reality-check table, the honest cost of each idea, the gate-ready
> bounded slice, and the "looks cool" art-brief live there. **Three claims in this section were
> corrected by the code review** — the causality in §12.3 (fixed below), the "coats-only" color read in
> §6 (art is carved wood; faction color is on the standard), and the "cheap backend" framing in §7 (the
> multi-army flagship is a real medium slice). Read the memo before leaning on §12 at the gate.

### 12.1 Fun-factor verdict

The honest read: this feature has a **high but front-loaded** fun ceiling, and its value is
**not uniform across battles**. That shape should drive the whole design.

| Battle kind | Fun lift from a tableau | Why |
|---|---|---|
| Your marshal, **decisive** result | **Very high** | This is the payoff moment — "Ney *shattered* Mack" wants to be *seen*, not read. The topple cascade is the reward. |
| **Coalition / multi-army** | **Very high, irreplaceable** | Mixed coat colors + a greyed no-show block say in one glance what three sentences bury. This is the case text genuinely *cannot* do (spec §5) — it is the strongest reason to build. |
| Close / bloody attrition | **Medium** | Two lines both thinned, no clean winner — the diorama honestly conveys "grinder," which is itself legibility (see CO-3 decisiveness). |
| Routine skirmish, minor stakes | **Low, decays to friction** | The 6th auto-played tableau of a 2k-vs-1k raid is a *speed bump*. This is the failure mode to design against. |

**Design consequence (answers open-question §10.1 and §10.2):** don't replace the text report and
don't auto-play for everything. **Significance-gate the auto-play** — full tableau only for battles
that are decisive, involve a player marshal, or earned a **dynamic battle name (W6-2)**; everything
else stays text with a **"⚔ View the field"** button. Repeat views (from the campaign log / a future
gallery) render the **final frame instantly, no sequence**. This is what keeps novelty from rotting
into tedium, and it's cheap — a significance predicate on the existing `battle_result` payload.

### 12.2 The single highest-leverage add: marshal portraits + falling standards

Two grounded touches convert the tableau from "colored blocks" into "*my generals*, winning or dying":

1. **Marshal portrait at the head of each contingent block.** The repo already ships **37 Wikimedia
   PD marshal portraits** (used on the Generals cards). Crown each block with its marshal's face.
   Now you don't watch "a blue block break" — you watch **Ney's line break**. On rout, desaturate /
   crack the portrait; on a decisive win, a small `★` (the **Crowned-with-Glory** crown from the
   Jealousy system) rides above the victor. **Cost: near-zero** — the portraits and the crown concept
   already exist; it's layout.
2. **The per-corps `⚑` becomes a real standard, and standards fall.** The iconic Napoleonic drama beat
   is *the eagle taken*. When a corps routs, tilt/drop its standard; in a decisive rout, slide it
   **across the centre line to the victor's side** ("standard captured"). This is the most emotionally
   legible single animation in the whole feature and it is **pure Tween on a static glyph — Tier-A-safe**.

### 12.3 Make it the stage for the drama the game already generates

The diorama is the natural window onto three systems the game already runs but under-shows:

- **Coordination holes (the headline).** The greyed "Bernadotte — failed to arrive" block (spec §5) is
  already the plan. Push it one step: where the no-show marshal carries `jealous_of`, surface it as the
  **grudge that explains the gap** ("Bernadotte resents Davout's glory"). Ties the tableau to
  `jealousy.py` with **zero new mechanics** — two separately-existing pieces of display data (the
  "failed to arrive" copy and the `jealous_of` field).
  > **⚠ Correction (Evaluation §3): the causality here was BACKWARDS.** A no-show does **not** create a
  > grievance — it docks −3 trust only (combat_executor.py:5008-21); grievances are minted solely by the
  > glory-ladder gap in `apply_jealousy`. It runs the other way: a **pre-existing grudge** (derived −1 in
  > `get_relationship`) worsens the arrival roll and makes the no-show *more likely*. Surface it as
  > **grudge-explains-gap, never battle-mints-grudge.** A neutral info line is the most it may honestly say.
- **The lone glory-attack.** When a marshal attacked solo because of jealousy (autonomous glory-attack),
  his block **stands alone with no reinforcing corps beside it** — the tableau shows *why* the odds were
  what they were. Cost: it's just the contingent list the payload already carries.
- **Decisiveness reads as a rout, not attrition.** CO-3 already models one side breaking faster. In the
  topple sequence, **cascade the routing side's figures from one flank** with staggered tween delays
  instead of a uniform grey-out. Same static art; the *timing* sells "they broke." Cost: tween delays.

### 12.4 Cheap sensory touches with outsized feel-per-effort

| Touch | What | Cost | Note |
|---|---|---|---|
| **Odometer stat tiles** | Casualty numbers tick up (0 → 21,400) *as* figures topple | Trivial | Binds the number to the visual; deeply satisfying |
| **One-shot audio** | A cannon thud on reveal; a drum sting on a decisive result | Small | **Cannon is CC0-cleared** (`cannon_*.ogg` in `opengameart_25-CC0-bang-sfx.zip`); one `AudioStreamPlayer`, mute-respecting. **Corrected (Eval §3):** a dedicated **drum/fife sting is a documented gap** (approximated from the RPG pack) and assets are still **zipped** — extraction + Godot import + license-log make this *small*, not trivial |
| **Terrain backdrop strip** | A tinted ground band keyed to province terrain (forest / river / mountain / urban); a crenellation silhouette behind a fortified defender | Small | Reuses `region.py` terrain constants; you see *where* it was fought, free legibility |
| **Arm-flavored clash glyph** | `⚔` varies by combat kind — crossed sabres (charge), cannon-burst (bombardment), bayonets (infantry assault) | Small | Reuses the 3 existing arms; reads the *kind* of battle at a glance |
| **Berthier verdict, delivered last** | The Berthier line fades/types in *after* the topple settles, like a narrator's ruling; the winning marshal may get a one-line boast via the CR-5b flavor path | Small | Turns the line from a footnote into the punchline |
| **Engraved brass nameplate** | The **dynamic battle name (W6-2)** engraved serif at the tray's base — "The Slaughter at Ulm" | Trivial | Leans into the *diorama-as-object* metaphor; the name already exists |

### 12.5 One bounded meta-idea worth naming (explicitly OUT of Tier A)

**A Battle Gallery** — re-view the final-frame tableau of past named battles from the campaign log, a
little shelf of tin dioramas you've collected. This is a real fun multiplier (it makes battles feel
*collected*, and it's the natural home for repeat-viewing). **But it is a separate slice with its own
gate** — it needs a persistence question answered and would otherwise become the open-ended "battle
animation backlog" §10.5 warns against. **Named here so it isn't smuggled into Tier A; not queued.**

### 12.6 What I would cut / de-risk

- **Don't gild every skirmish.** The significance gate (§12.1) is not optional polish — it's the
  difference between "delightful" and "why is this popping up again." Build it into Tier A from day one.
- **Resist proportional figure counts** (open-question §10.3). The mocks' fixed cap reads cleaner and
  dodges a layout-overflow tarpit; "committed strength" is already legible via the stat tiles and block
  size. Capped-and-labeled is the disciplined choice, consistent with how the map labels already summarize.
- **Hold Tier B until Tier A is measured** (spec §11.3 is right). If falling standards + portrait-cracks +
  cascade-topple + audio don't make Tier A *feel* like combat in a live playtest, more art won't save it —
  and if they do, Tier B is a nice-to-have, not a need. Prototype-then-measure, exactly like the sweeps.

### 12.7 Net recommendation

Tier A **plus §12.2 (portraits + falling standards) folded in from the start** is the sweet spot: still
one bounded slice, but it crosses the line from "legible" to "*fun*" — because it puts a face on the win
and drops the enemy's eagle when the line breaks. The multi-army coalition case (§5) remains the reason
the feature justifies its slice at all; §12.3 is what makes that case *land emotionally*. Everything in
§12.4–§12.5 is a per-item pick for the gate.

---

## 13. Evaluation of record (July 17, 2026)

**`docs/audits/BATTLE_DIORAMA_EVAL_2026_07_17.md`** is the authoritative evaluation — a grounded,
adversarially-verified pass (18 agents: code-grounding readers → creative lenses → 9 skeptic verdicts
against live source → synthesis). Where it and this spec disagree, **the memo wins.** Headlines:

- **Verdict: BUILD IT — fun 7/10** — but as a *significance-gated, honestly-costed* slice: one Godot
  tableau **+ one modest backend `contingents[]` slice**, not the "near-zero" frontend freebie §7
  originally advertised. The coalition tableau is the only thing here text genuinely cannot do.
- **The fun is bimodal.** Peak on decisive player-marshal wins and coalition/multi-army battles;
  **net-negative** on routine skirmishes — which makes the **significance gate a Definition-of-Done
  item, not polish** (its inputs already ride `events[0]`, so it's cheap).
- **Three spec claims were corrected by the code review** (all folded back above): the §12.3 causality
  (grudge→no-show, not the reverse), the §6 "coats-only" color read (art is carved wood; color rides
  the standard), and the §7 "cheap backend" framing (multi-army is a real medium slice).
- **Cut for the real slice:** the **Kutuzov "withdrew in good order"** status (unmodeled), proportional
  figure counts, per-corps cascade in v1, untreated raw-JPG portraits, the Battle Gallery, all of Tier
  B/C. Memo §5 has the full list; §6 has the gate-ready bounded slice + the one test; §8 has the
  carved-wood-tray art-brief.
- **Named landing — ✅ CREATED July 17, 2026:** ROADMAP §Current Phase Queue row **BD** + the STATUS
  tracking line. The weigh-against-Nation-Agendas question was **DECIDED the same day (user-directed):
  Nation Agendas keeps the 8.5 centerpiece slot; the diorama is QUEUED as the follow-on Tier-A slice.**

The interactive hero mockup (spec §6) implements most of the art-brief as a feel-of-the-thing proof.
