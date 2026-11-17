# Battle Diorama Popup — SPEC (Tier A LANDED)

> **▶ ROW BA — "THE BATTLE IN ACTS" — THE GATE ✅ RULED November 14, 2026 (§15, authoritative:
> the user's ten rulings, the design contract, the three sessions BA-1 / BA-2 / BA-3, all before
> the deploy).** It discharges §4's Tier B ("scripted skirmish") without new art: the acts are
> tweens on the pieces already built. Landing records follow §15 as each session lands:
> **BA-1 "the dice and the acts" ✅ BUILT November 14, 2026 (§15.10)**; BA-2 (the walls, the
> guns, the order of battle) and BA-3 (the crisis) follow, each opening in Plan Mode.
>
> **STATUS: ✅ TIER A BUILT + LANDED July 31, 2026 — landing record = §14 (authoritative),
> evidence pack = `docs/audits/BD_TABLEAU_{TRIUMPH,DEFEAT,MIDCASCADE}_2026_07_31.png`.**
> The Fable review RAN July 17, 2026 (**evaluation of record =
> `docs/audits/BATTLE_DIORAMA_EVAL_2026_07_17.md`, authoritative wherever it and this spec
> disagree — verdict BUILD-IT, fun 7/10**), and the queue decision was made the same day
> (user-directed): **the Tier-A slice slotted AFTER the 8.5 Nation Agendas design gate**.
> Named landing = ROADMAP §Current Phase Queue row **BD** + the STATUS tracking line.
> **Scope of record = eval §6** (the bounded slice: the medium backend `contingents[]` half +
> the significance-gated Godot tableau; the eval §5 cuts stand; completion = eval §6 DoD +
> `tests/test_battle_diorama.py`). Numbers, art choices, and layout below remain illustrative
> where the eval or §14 has not pinned them.

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
status ∈ **{engaged, reinforced, routed(primary-pair-only), destroyed, refused, failed_arrive,
out_of_reach}** (note: **`withdrew` is UNMODELED and cut** per Evaluation §5; the absence family
**{refused, failed_arrive, out_of_reach}** landed with PT-D2, Aug 1 2026 — a by-design character
refusal (`literal_personality`/`eyes_on_a_crown`, the Session-61a trust-dock taxonomy) renders
`refused`, an honest failed roll keeps `failed_arrive`, and a WILL-JOIN muster promise the resolve
ladder silently dropped shelves as `out_of_reach` via muster-promise parity — every promised name
appears with SOME status) — from `atk_participants`/`def_participants`, fog-filtered on
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

**Gallery-gate rider (CA8-25 garrison half, homed here Aug 7, 2026 — CA8-19 close-out gate 10.5):**
a stormed garrison renders no tableau because `_resolve_garrison_combat` emits
`garrison_assault`/`conquest` (never a `battle` event) and the tableau has no
defender-without-a-marshal. The gallery gate owns teaching it one: a **garrison contingent**
(war-table piece + faction coat; no locket, no standard-take — there is no commander to lose one).
Completion definition: a garrison assault renders a tableau whose defending contingent is the
garrison itself; behavior test named when the gate is held. Until then a garrison assault
deliberately renders no diorama — that is this rider's debt, not an oversight.

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

---

## 14. LANDING RECORD — Tier A BUILT July 31, 2026 (authoritative)

**Evidence pack:** `docs/audits/BD_TABLEAU_TRIUMPH_2026_07_31.png` (the Great-Battle
coalition frame — 3 French corps + Bernadotte on the reserve shelf with his grudge, Mack
routed and his eagle taken across the line, Hohenlohe destroyed),
`BD_TABLEAU_DEFEAT_2026_07_31.png` (the defender's-eye gut-punch — crimson "THE LINE IS
BROKEN", the player's tricolor planted at the victor's rank, the enemy standard advanced
onto the player's half), `BD_TABLEAU_MIDCASCADE_2026_07_31.png` (the lines closed,
pre-topple). Captured from the live scene via a throwaway fixture harness (deleted).

### Backend half — `backend/game_logic/battle_diorama.py` (display-only, GR6)

- **`build_battle_diorama(...)`** assembles the eval-§6 `contingents[]` payload inside
  `_execute_attack` (ONE builder, both the solo and coordinated branches), attached to BOTH
  transports: the top-level `battle_diorama` result field (whitelisted in `main.py`
  `_COMMAND_RESULT_SIMPLE_FIELDS` — the register-or-dropped trap closed) and
  `events[0]["diorama"]` (the enemy-phase transport, fog-filtered with the action).
- **Per-corps figures:** `committed` from a NEW all-participant pre-battle snapshot
  (`snapshot_pre_battle_strengths`, captured before support bombardment / resolve_battle /
  take_casualties mutate anyone — the eval's "extend `_co6_lead_pre_strength` to all
  participants"); `casualties` from the once-dead `casualty_distribution` maps (now read);
  leads' `remaining` = the battle event's own figure (shown = the number every other
  surface prints). `def_distribution` initialized on both paths (was coordinated-only).
- **Status vocabulary** exactly the four states with data + arithmetic `destroyed`:
  `engaged` (fought where it stood) / `reinforced` (marched via the arrival system) /
  `failed_arrive` (with the muster vocabulary compressed to shelf labels — "awaits explicit
  orders" / "fate intervened on the march" / "weighed his own ambitions") / `routed`
  (primary pair only, per the eval cut) / `destroyed` (remaining ≤ 0). `withdrew` stays
  CUT (unmodeled).
- **The grudge line** rides a player-side no-show carrying `jealous_of` — worded as
  explanation ("He resents Davout's glory."), never causation (eval §3: grudge→no-show).
  Enemy grudges never leak (the jealousy proxy is not player-readable).
- **Fog contract** (eval de-risk must #1): player fought → both sides full (the battle IS
  the intel; `update_intel_from_battle` grants the region FULL at every resolve site);
  player absent → payload exists only at FULL region visibility (mirrors
  `_filter_enemy_phase_by_visibility`); an enemy corps that FAILED TO ARRIVE reveals its
  own region, not the battle — included only at FULL visibility of its location; player
  no-shows always show.
- **Significance vs drama — two predicates, one conscious interpretation:**
  `significant` = the eval's blessed §7-Q2 arms (decisive / player-involved / named) with
  the "named" arm read as the **Great tier** — the literal reading gates nothing, since
  EVERY field battle composes an ordinal name (recorded interpretation, not an oversight).
  `dramatic` (decisive / great / any rout or destruction / conquest / multi-corps) narrows
  the UNINVITED surface only: enemy-phase auto-play. This resolves the eval's internal
  tension (§7-Q2's literal player-marshal arm would auto-play the routine incoming raids
  its own §2 fun-curve calls net-negative) in favor of its thesis: the player's OWN attack
  auto-plays whenever significant (the payoff of their own order, one click to skip);
  an UNINVITED battle seizes the screen only when dramatic.
- **`register`** derives the §7-Q6 framing (Fable's call, now code):
  `triumph` / `defeat` / `grim` / `observer` — the player's line is ALWAYS the near/left
  side; a defeat is a gut-punch (crimson banner, "THE LINE IS BROKEN" for a broken
  defense, the victor's standard advancing onto the player's baize), never a mirrored
  enemy triumph.
- Flourishes: `crowned` (the STANDING glory laurel, pre-battle state per the eval),
  `origin_nation` (an assimilated ex-vassal corps flies its own colours — the one true
  mixed-standards read the engine produces today), `observation` + `enemy_voice`
  self-contained on the payload. Cap = 4 corps/side + honest `reserve_count` tail; the
  shelf never crowds out the line.
- **Boundary (GR9):** field battles only (`resolve_battle` results). Garrison assaults,
  bombardments, and glorious-charge redirects keep their existing surfaces (they compose
  no battle name either — eval §3). The auto-bombardment-kill early return carries no
  tableau (no battle was fought).

### Frontend half — `scenes/battle_diorama.tscn` + `scripts/battle_diorama.gd` (layer 121)

- **The carved-wood tray** per eval §8: walnut tray + crisp gold border + filigree corners
  (the U3 discipline — never a muddy full-texture frame), green-baize stage with a darker
  felt band, warm additive lamp pool from upper-right (the direction baked into the
  sprites), vignette above the figures, dashed gold clash line + ⚔.
- **The figures ARE the map's pieces:** `scenes/diorama_figure.gd` (`DioramaFigure`)
  composites the same four-layer carved-oak sprites through the same texture cache
  (`WarTablePiece.layer_texture` / `legible_tint` — new thin public statics; the instance
  `_legible_tint` now delegates so the lift stays single-source). The **fixed topple
  verb**: rotate ~78° about the feet + darken toward bare timber + the baked shadow
  stretches into a long cast — base disc and ground shadow STAY PUT; opacity-ghosting
  structurally unavailable. Figures per corps by arm (5 foot / 4 horse / 3 guns); the
  toppled FRACTION encodes losses (count stays fixed — the eval's anti-proportional
  ruling); the cascade breaks from the clash-side flank.
- **Standards that fall and are taken:** each corps plants a real pole flying its nation's
  own heraldry SVG (`Utils.nation_flag_path`, pennant-polygon fallback). A routed/destroyed
  corps' standard tilts and drops; on a decisive field the beaten LEAD's eagle slides
  across the centre line to the victor's side; on a defeat the victor's standard advances
  onto the player's half (the §7-Q6 alarm register).
- **Portrait lockets:** `scripts/portrait_locket.gd` (`PortraitLocket`) — the Generals-card
  portraits sepia-duotoned + vignetted + ellipse-cropped by ONE shared shader inside a
  drawn brass bezel with a catchlight; gold-monogram fallback (no corps is faceless); the
  glass goes grey when the corps breaks; the standing ★ rides the rim.
- **The sequence** (~4 s, any click skips): cannon thud + tray reveal → figures placed →
  the lines close → the cascade topple bound to the odometers (the count and the collapse
  are one event; red ONLY in the tally) → standards fall / the eagle taken (+ drum sting
  on a decisive field) → the register-toned banner → **Berthier's verdict types in last**
  (IM Fell italic; the enemy commander's W6-6 line beneath). Skip rebuilds the settled
  frame deterministically (no tween bookkeeping); repeat views open settled instantly with
  [Replay]; `show_diorama` kills any prior sequence FIRST (a re-open mid-cinematic was
  ticking the old battle's odometers over the new frame — caught by the visual pass).
- **Nameplate:** engraved Cinzel brass plate (battle name · province · turn) + the wax
  seal overhanging its edge; laurels flank it on a triumph only.
- **Audio:** `assets/audio/battle/cannon_thud.ogg` (extracted from the CC0 bang pack) +
  `drum_sting.wav` — **self-authored CC0, synthesized by `tools/gen_battle_audio.py`**
  (deterministic numpy snare: crescendo roll into two accents over a field-drum boom; the
  own-pipeline route, closing the eval's documented drum-gap instead of shipping a metal
  pot). One `AudioStreamPlayer`, no bed loop, honoured by a new `UiSettings.get_battle_sfx`
  toggle ("Battle sounds", pause-menu Settings — the game's first audio setting).

### Wiring

- **Player attack:** `_stash_diorama` at response arrival (the NA-6b stash discipline);
  raised in the control-return tails (BEFORE the Proclamation — the freshest moment first;
  dismissal chains proclamation → letter-book → input). The terminal battle line always
  keeps a gold `⚔ View the field` link (`output_display.meta_clicked` now connected —
  first use); re-views open settled.
- **Enemy phase:** every battle line in the dialog with a payload gets its own
  `⚔ View the field` link (opens OVER the dialog, layer 121 > 118, input hold undisturbed);
  after the dialog closes, the single most violent dramatic player-involved battle
  auto-plays via `_return_control_to_player`. AI-vs-AI battles never auto-play.
- **Objection-proceed attacks** carry the payload for free (`_build_result_response`
  forwards all executor keys).
- Parse harness extended (the IGR-E runtime-registration gap class): battle_diorama.gd /
  portrait_locket.gd / enemy_phase_dialog.gd / pause_menu.gd / ui_settings.gd +
  war_table_piece.gd / diorama_figure.gd + the battle_diorama.tscn instantiation check.

### Verification

- `tests/test_battle_diorama.py` (43): single-army AND multi-army through the REAL attack
  path, per-corps casualties summing to the event surface, statuses, the no-show shelf +
  grudge + enemy-grudge negative, fog PARTIAL-vs-FULL both for third-party battles and
  enemy no-show regions, significance + drama + register matrices, cap + reserve tail,
  arm/crown/origin flourishes, whitelist registration, JSON round-trip, enemy-phase event
  transport.
- Parse harness EXIT=0 (report regenerated); headless boot 0 SCRIPT ERROR; a live
  runtime smoke drove instantiate → final frame → cinematic → mid-cinematic skip →
  replay → close with zero errors and all assertions green (throwaway harness, deleted).
- `THIRD_PARTY_LICENSES.md`: battle-audio entries added; the "198 WAVs force-tracked"
  doc-drift the eval flagged corrected.

### Deferred (owned)

Everything the eval §6 marked OUT stays out with its owner: withdrew-status / per-corps
rout / clickable grievance beat / proportional counts / terrain backdrop (named follow-up,
needs a payload field) / Battle Gallery (own gate, persistence question) / Tier B/C
(hold until Tier A is measured live) / ambient loops. **Live measurement of the tableau in
ordinary play belongs to the next in-game review** (the standing cadence), where the
significance gate's feel is the thing to watch. **✅ First feel pass: PASSED by the user
August 1, 2026 (the play-session sign-off) — the significance gate ships as tuned; future
in-game reviews keep the standing cadence.**

### §14.1 Post-landing addendum — the render-chokepoint fix (July 31, 2026, `2ea50d1`)

The user's first live session reported the exact double symptom "clicked View the field
and nothing happened / nothing popped when I attacked." Root cause: the stash-and-raise
lived ONLY in `_on_command_result`, but a real attack frequently resolves through a
DIFFERENT handler — the W6-4 muster **"Attack Anyway" interrupt**
(`_on_interrupt_response`), an **objection Proceed** (`_on_objection_response`), or
behind the **plunder/secure capture prompt** — all of which render the battle via
`_display_result` without arming the popup. The terminal link still drew (it reads the
EVENT copy) while `last_battle_diorama` stayed null: a dead link and no auto-play, from
one cause.

**The fix is structural:** the stash moved INSIDE `_display_battle_result` — the one
chokepoint every rendered battle passes through — so the link and the stash are
inseparable by construction; the raise was added at the four control-return tails that
lacked it (`_process_next_interrupt` queue drain, the objection tail, the capture-choice
tail — the tableau waits politely behind the plunder/secure decision — and the
glorious-charge tail for uniformity, a no-op by scope). Verified end-to-end against a
fresh backend on a side port: the boot Ney-vs-Mack attack carries the payload on
/command, and the follow-up battle reproduced the capture-gated flow live. **Deployment
note that was the report's second half: a backend/client started BEFORE this feature
serves/renders no payloads — restart BOTH after pulling.** ✅ **The user then confirmed
the tableau working in-game.**

---

## 15. ROW BA — "THE BATTLE IN ACTS" — THE GATE RECORD (November 14, 2026, authoritative)

### 15.1 The user's words

- November 13, 2026 (the ask): "i also want to improve the battle screen how can we make it show
  battles that sow the generals personalities and napoelonic style warfare with cool outcomes and
  movement and only abstract player input that cant be cheesed. would this be a good add"
- November 14, 2026 (the go-ahead): "yes for the battle gate looks at game look blucher etc, we
  want this engaging  but we dont need to build whole new game but it should be a alyer of
  intrerwesting developments personalities and visualizations  with abstract player guidance"

Drafted in Plan Mode and approved November 14, 2026.

### 15.2 The rulings

| # | Question put | The user's ruling (verbatim where quoted) |
|---|---|---|
| 1 | The reading of "looks at game look blucher" | "The tabletop game" — Sam Mustafa's *Blücher* and its kin; the look, never the rules |
| 2 | The look | "Blend (Recommended)" — the carved figures stand on a card-like plinth carrying the marshal's name and strength pips; the plinth is the piece that moves |
| 3 | The decision at the crisis | "make this not chesaable but interactive your call on how we facilitate balance tradeoofs and unpredictable reactions based on generals personalities some type of system simulation" (delegated design: §15.5.6) |
| 4 | A plan of battle | "research how to best implement with existing systems" (delegated research: §15.5.5) |
| 5 | WS-11, the reload that rolls the battle again | "Seed them here, first" |
| 6 | The dice | "Dice on the table" |
| 7 | Which battles play the acts | "Great ones in full" — great and dramatic battles in full, other significant battles a brief form |
| 8 | Garrison assaults and bombardments | "Both get a tableau" |
| 9 | Against Session H (the deploy) | "Before the deploy" |
| 10 | Other rule changes | ticked "Reinforcing pursuers count" and "The last hour bites"; Blücher's "Vorwärts!" in 1805 not ticked; and "research well make good decisions we want this full and with breathd and dont want to break anything" |

### 15.3 The references (looked up November 14, 2026; visual language only)

- **Blücher** (Mustafa): a corps is a card carrying the unit and its strength boxes, ticked off as
  it wears; cards begin face down and are turned up on contact; a broken unit leaves the table; its
  campaign pre-game makes columns arrive late.
- **Napoleon's Triumph** (Simmons): blocks in lines with corps flags on a period-plan map; no
  markers — where a block stands is its state; an attack runs in named steps (threat, response,
  lead units, counter-attack, result, retreat).
- **Commands & Colors: Napoleonics**: three sections of the field; a retreat is a step back;
  squares against horse.
- **Kriegsspiel** (1824): written orders, carried out by an umpire as he judges the troops would.
- **Grand-strategy battle windows**: phases, leader traits picking tactics, and a player who sets
  only a preference.

### 15.4 What the research corrected (verified against the code)

- The 1805 game has no Wellington or Uxbridge (Wellesley and Paget sit in the recruit pools with no
  ability); **Blücher ships with no ability** ("Vorwärts!", reverse slope and Counter-Punch Mastery
  live only in the 19-region fixture world); Davout's live ability is Iron Resolve; Ney is
  infantry; Murat is the only cavalry commander at boot; no gunner is on the boot board.
- Computed and named, never shown: the 2d6 and its modifiers (`attacker_roll`), `ability_triggered`
  (Ney's shock), the Iron Resolve release, the pursuit line, per-corps routs and the orderly
  withdrawal of reinforcers. The two ±10 % variances were discarded after use.
- Criticals (12, 2) change wording only; the roll scales damage dealt, not taken; a pursuit ability
  fired only for the LEAD (MC-1, pinned).
- The enemy phase resolves in one request and cannot stop to ask. The two questions the game asks
  after a battle (plunder or secure; the last stand) are the reusable plumbing.
- New campaigns roll their own seed; the suite is pinned to `historical`.

### 15.5 The design contract

**15.5.1 The dice are seeded (WS-11).** One private stream per battle, keyed on the campaign seed,
the turn, the two leads, the province, `len(world.battles_this_turn)`, the province's battle count
and (for a bombardment) the battery's salvo count. It feeds the arrival rolls and fumble, the
supporting and the standalone bombardment, the 2d6, both variances, the flavour pick, rout
survivors, the cornered escape and the last-stand breakout, building damage, the relationship
jitter, the glorious charge and the turn-start auto-charge. The seam is a FUNCTION
(`campaign_variance.the_battle_dice_are_seeded`), not a module boolean — the code-health ratchet
caps module-level levers. The siblings a reload still re-rolls (the objection's mood, the defiance
roll, the diplomatic defiance, four smaller sites) are filed as WS-16.

The stream is `None` — every draw stays on the module `random` and every call keeps the shape it
had, byte for byte — in two cases:

- **the `historical` seed**, the suite's pin and the fixed table of every seeded rule; and
- **a world the game server does not hold.** The defect is a player's (save, fight, load, fight
  again), so the dice are the campaign's where a campaign is played:
  `backend.main._set_active_world` — the boot, New Campaign, a load — serves every world it
  installs (`campaign_variance.serve_campaign`; a weak register by identity, nothing written on
  the world, nothing saved). The measuring tools build their own worlds
  (`WorldState.from_scenario` and a `TurnManager` loop under their own `random.seed(...)`), on
  NAMED seeds; they are never served and keep the stream they pin, so the recorded series stand.
  This is the correction the build made to the gate's own sentence ("Campaigns on the
  'historical' seed keep today's behaviour byte for byte, so the test suite and the measured
  series do not move"): the series run on named seeds, not on `historical`, and the first cut —
  seeded wherever the seed was not `historical` — moved one of them
  (`tests/test_sf_lb2_the_defenceless_prize.py`, the driven board on austerlitz: Prussia's war
  on Hanover ended at turn 17 where the record has none). A harness arm that wants the seeded
  dice on its own board calls `serve_campaign(world)` (BA-3's measure has that arm).

**A second correction, found by the full suite on the final tree.** A tool that plays THROUGH the
server is a campaign the server holds. `tools/playtest_driver.py` posts `/new_game`, so its
`--seed` arms — `score_run`'s commanded arms on austerlitz, marengo and ulm, the sign-ability
sweep's seeds — fight the campaign's dice as a player does. That is the rule working (the driver
is how the game is played unattended), and it moves the readings taken on those arms, once: the
deploy gate's France band (`DYNAMISM_SPEC.md` §2, 23–28) read 26 / 26 / 25 and reads
26 / 27 / 28 (§15.10 "The measure"), and the sweep's quick seed arm was re-recorded, still 0 / 0.
`historical` arms (CMD-H, the driver's default) and every harness that builds its own world —
the ten-seed ambient sweep, the AI-France harness, `BASELINE_SERIES`, the fuzzers — do not move.

**15.5.2 The script.** `backend/game_logic/battle_script.py` builds an ordered, display-only list
of beats in five acts — the approach, the cannonade, the assault, the crisis, the pursuit — stored
inside the tableau payload as `payload["script"]` (it inherits the payload's fog gate and both
transports). Every beat is made from a number the resolver already produced; an act with no beat
is not played; a beat names only a corps the payload already shows; every number is an int.
`form` is `full` for great or dramatic battles and `brief` otherwise (the head beats only).

**15.5.3 The table.** The Blend look: each corps block stands on a plinth (nation band, name, six
strength pips that tick off as losses land); the plinth marches, is turned face down when the corps
is beaten, and leaves the table. A sequencer plays the script as verbs; temperament is a movement
signature (the aggressive lead goes in ahead of the line, the cautious one by measured steps, the
literal one to his mark and no further, the line dresses on the Emperor). Act IV draws the dice
with each modifier named and each side's fortune. The significance gate, skip, the instant settled
frame and Replay stay; Settings → Interface → Battle scenes chooses In acts / Brief always / Final
frame only. The plinth and the sequencer are NEW scripts hooked into the existing one, whose
function bodies some thirty test files pin.

**15.5.4 The walls and the guns.** A garrison assault opens the table (a garrison block with no
locket and no standard to take; held, stormed or capitulated) — this closes the garrison rider of
§12.5 (CA8-25). A bombardment plays the cannonade alone; a link by default, opening by itself only
when it breaks or destroys its target. *(As built, §15.12: when it destroys its target or levels his
works — guns never break a corps. The reading is the user's to change.)*

**15.5.5 The plan of battle, from the orders the game already has.** No new modifier and no new
order. Act I names the plan the player's orders amount to (the lead, the corps ordered in support,
the provinces the attack comes from and the flank's +N on the dice, a drilled assault, stance,
guns in support); the attack row of the province panel and the muster card carry, per nearby
corps, a chip for the existing order that would bring him, priced on its face.

**15.5.6 The crisis — the Emperor's word.** *(Amended November 14, 2026 by §15.11: the presence gate below is struck — the hand is in every battle the player fights — and BA-3 re-plans this section as "the rounds".)* Asked on a field battle the player ordered, where the
Emperor stood on the field and the day hangs (both leads standing, the enemy still on the field).
One order — Press (the lead renews the assault), The Guard (the Emperor's own corps attacks), Hold
— and the lead answers by temperament through the systems that already exist: the concern
evaluators, the insist penalty and trust gain, the defiance chance, roll and fallback, "By my
word", vindication. New numbers: the Guard's two morale effects (the enemy lead −10 as it goes in;
every French corps that fought −10 if it is beaten), which close NP-D1. Not built: a council on
defence (the enemy phase cannot stop, and by the next turn the board has reset), and marshals
settling a hanging day alone (it would move every measured arm). The courts' rule is written and
dormant (no court fields a sovereign).

**15.5.7 The two rule changes.** A pursuit ability fires for a corps commander who FOUGHT on the
field — marched in or standing there; "ARRIVED" in this section's first wording, widened to FOUGHT by
the answer recorded with the recommendations handed over at the user's word (§15.13) and built so by
BA-4 (§15.20) — when
the lead has none (highest only; the Old Fox still halves it) — this reverses MC-1's pinned "he
must lead the killing blow" by the user's tick. An arrival won by 5 points or fewer brings three
quarters of its weight, through the single function that halves a faithless man's weight, the
muster's forecast counting it the same way.

### 15.6 Why the crisis cannot be cheesed (the user's bar)

The dice are seeded, so the same order always has the same result, whether an overruled man obeys
included; the card shows the odds band, every price and the lead's temper; no order is best
everywhere; it is one order with no placement and no timing. What remains is true of every order
in the game: after a reload a different order may be given.

### 15.7 The sessions (each one commit, each reviewed; all before Session H)

| Session | Scope | Done when |
|---|---|---|
| **BA-1 — the dice and the acts** | §15.5.1, §15.5.2, §15.5.3 | the same save fights the same battle; the script is on both transports, fog-true at PARTIAL and FULL; the tableau plays the acts in the Blend look with the dice; the parse harness and the instruments are green; a Mode C walk is recorded |
| **BA-2 — the walls, the guns and the order of battle** | §15.5.4, §15.5.5, and by §15.11 the board and the manoeuvre | an assault and a bombardment each render a tableau on both roads; the plan is named in Act I and orderable at the attack row — **✅ LANDED November 15, 2026 (§15.12)** |
| **BA-3 — the day's points** (§15.14; it was "the rounds", and before that "the crisis") | §15.5.6 as amended by §15.14; WS-16; NP-D1; BA2-X14's left half; BA2-X17 | a great battle that hangs is fought in turns on points that are the battle's own, on both sides; a small battle is told as before; the same save gives the same day and the same temper; ONE measure with arms, reported per seed; nothing outside a campaign the server holds moves — **✅ LANDED November 16, 2026 (§15.17; it stopped at its own measure, §15.15, and was finished on the user's "do whatever is best not easiest", §15.16)** |
| **BA-4 — the roads and the fog** (§15.14, the user's approval of BA-3's plan) | BA2-X2, BA2-X7, BA2-X10 with the support order's approach rule, BA2-X12, BA2-X20 with the Gazette's news, BA2-X21; §15.5.7's two rules (the pursuit by any corps that fought; the last hour's three quarters); BA3-X2 and BA3-X5; the four rows BA-3's review filed, BA3-X13 to BA3-X16 (§15.18) | every row that moves a measured world-line lands with ONE re-read of the gate (the keyed probe's jena arm with no court's turn lost; the standing series re-read; the commanded band per seed); each rule behind a function seam — **✅ LANDED November 16, 2026 (§15.19 the gate, §15.20 the landing record, §15.21 its review): ROW BA COMPLETE** |

BA-2, BA-3 and BA-4 each open in Plan Mode with their own slice plan. Three questions went to the user at
BA-3's head (raised by the design review, November 14): the stroke's price (the plan of record says
no action; the review flags a near-free second attack after a narrow win), whether a pursuit by an
arrived commander includes a corps already standing on the field, and one crisis a lead a turn.
BA-3's arm 0 on the commanded band is BA-1's shipped record (`tools/_ba1_band_2026_11_14.json`,
arm ALL: 26 / 27 / 28) — the driver's named-seed arms already fight the campaign's dice.

**The behaviour tests, named now (Golden Rule 9).** BA-2: `tests/test_ba2_the_walls_and_the_guns.py`
— a garrison assault and a bombardment each carry a tableau payload through the real roads on both
transports, fog-true at PARTIAL and FULL, every number an int; Act I names the plan from the orders
actually given; the attack row's chips quote the existing order's price and send that order — with
a driven walk of both tableaux in the manner of `tests/test_ba1_the_battle_in_acts.py`. BA-3:
`tests/test_ba3_the_rounds.py` (it was named `test_ba3_the_crisis.py` before §15.11 renamed the
session) — a small battle carries nothing new; a great battle that hangs opens a day with the
commanders' points; a word costs points and never an action and goes through the objection road;
the enemy answers by his AI's own rule; silence, night and dawn; the Guard's two morale numbers;
"Leave it to him"; the store round-trips and an old save reads none; a world nobody serves has no
day; and `tests/test_ws16_the_same_order_draws_the_same_temper.py` — an order insisted on
again from the same save draws the same mood and the same defiance (WS-16's done-when). BA-4:
`tests/test_ba4_the_roads_and_the_fog.py` (written with BA-4) — a court's turn is not lost to a
corps raised again mid-phase; a muster row's hint names only a corps the order would bring; a
support order halts at the approach; a battery is never caught by its own fire; a battle lights
its field only for those who fought in it and the Gazette names a great foreign battle without a
figure; a quote names the men its first march costs; the pursuer among every corps that fought;
the last hour's three quarters.

### 15.8 Decisions taken under the delegation (each one switch or one line)

The crisis is the objection system staged at the hinge of a battle, and only the lead's trust is
at stake; it is asked where the Emperor stands; the plan of battle adds no numbers; the Guard's
rule is two morale numbers; plinth pips are six; a concealed enemy plinth is turned up on arrival;
the brief form runs about six seconds and the full form about sixteen to twenty.

### 15.9 Left with the user

Blücher's "Vorwärts!" in the 1805 game (not ticked, not built); a riposte council on defence; the
marshals' own settlement of a hanging day (§15.11 rules on these two under the user's delegation:
neither is built — the riposte is offered as an ordinary order in BA-3). Open rows are not closed silently: WS-13 ("outnumbered"
read on the two leads) is untouched, and the acts show those beats as the engine reads them.

### 15.10 LANDING RECORD — BA-1 "the dice and the acts" BUILT November 14, 2026 (authoritative)

**What a player sees.** A battle no longer resolves in one tumble. Corps march onto the table
from their own edge, each named as it comes; an enemy corps comes up as a dark slab with no face
and no name and is made out when it arrives; the guns fire from the edge of the field; each lead
closes in his own way — Ney ahead of the line and a little too far, a cautious man by a step, a
halt and a step, a literal one to his mark and no further, the line dressing on the Emperor; the
attacker's two dice are set on the baize with what they did; the line that breaks shudders, its
plinth is turned down and it is driven back; the victor follows. Nothing on the table says how
the day ends before it does: a corps' line reads what it brought and runs as the men fall, and
the laurels, a defeat's cast on the baize and what the reserve lost come with the gavel. An act
is named over the field
(I · THE APPROACH … V · THE PURSUIT) and each development is one sentence where Berthier's verdict
will be written. Then the banner and Berthier, as before. A great or dramatic battle plays in full
(about twenty seconds); any other significant battle plays its head beats (about seven); any click
skips; Settings chooses.

#### The dice (WS-11, closed)

§15.5.1 is the contract as built. `campaign_variance.battle_rng` / `serve_campaign` /
`campaign_is_served` / `the_battle_dice_are_seeded` (a function seam);
`combat_executor.battle_dice(world, attacker, defender, region, kind, salvo)`;
`AttackContext.battle_rng` made at stage 10 and handed on. `resolve_battle` keeps each side's
variance as a whole percent (`fortune`: attacker, defender) for the table. Every call passes `rng`
only when it has one, so the suite's fixed-arity doubles of `roll_combat_dice` and
`_execute_bombardment` are called as they always were.

Two bounds, both deliberate: the `historical` seed is the fixed table (a player who TYPES that
seed keeps re-rollable dice, as every seeded rule is fixed there); and a world nobody serves keeps
its caller's stream. `tests/test_ws11_the_dice_are_the_campaigns.py` (46): the stream and its
identity; the served campaign and the door (`backend/main.py` assigns its active world in ONE
function, pinned by AST); the same save fights the same battle — solo, coordinated, the enemy's
attack, and through the routes (`/new_game`, `/save`, attack, `/load`, attack again); the
`historical` campaign still re-rolls; two thousand seeded battles roll fair 2d6 and a fair ±10 %,
and the same matchup wins as often on either stream; the guns; the band on the commanded arms.

#### The measure — what the seeded dice moved

`BASELINE_SERIES` discipline (`DYNAMISM_SPEC.md`: every series-moving slice lands with its
re-measure). Each surface with WS-11's seam down and up:

| Surface | How its worlds are made | Seam down | The shipped tree |
|---|---|---|---|
| The suite — `BASELINE_SERIES`, every pinned record | its own worlds, never served | — | passes, unchanged |
| The ambient sweep (`tools/_t3_4_measure.py`, ten seeds; a 12-turn control) | its own worlds | the same | signature and census identical |
| **The France band on the commanded arms** (`tools/_ba1_band_measure.py` → `tools/_ba1_band_2026_11_14.json`) | the driver, through `/new_game` — served | **26 / 26 / 25**, Session G5's band to the province | **26 / 27 / 28** (historical / austerlitz / marengo), inside 23–28 |
| The sign-ability sweep's quick seed arm (`docs/audits/dd1/sign_ability_SEED-quick.json`) | the driver | the committed reading, row for row | one treaty moves between two columns; A 0, B 0; re-recorded |

Per seed — one world-line each, not a law: `historical` does not move (the fixed table);
austerlitz 26 → 27; marengo 25 → 28, on the guard's upper edge. The seeded dice are the same
dice (a fair 2d6 and a fair ±10 % over two thousand seeded battles; the same matchup wins as
often on either stream), so this is another sample of each seed and not a change in what a battle
is worth. **The band's standing reading from here is that record's arm ALL.** The commanded
arms' older records on austerlitz, marengo and ulm (`score_run`, the Concert's sessions) are the
game before the dice were the campaign's; `--seam
backend.game_logic.campaign_variance:the_battle_dice_are_seeded=False` on the driver plays one
of them again. Pinned by `tests/test_ws11_the_dice_are_the_campaigns.py::TestTheBandOnTheCommandedArms`.

#### The script — `backend/game_logic/battle_script.py`

`build_battle_script(world, payload, attacker, defender, battle_result, attacker_reinforcements,
defender_reinforcements, facts)` → `{"version": 1, "form": "full"|"brief", "acts": [{"act",
"beats"}], "tempers": {name: temper}}`, stored as `payload["script"]` by `build_battle_diorama`
(a failure is reported and costs the battle nothing). `facts` are the executor's extras
(`combat_executor.battle_script_facts(ctx)`: reinforcer origins, the flank's provinces and bonus,
the supporting bombardments, the overwatch count, the advance). A beat is `{kind, side, actor,
text, weight: "head"|"detail", …ints/strings/bools}`.

| Act | Beat kinds | Made from |
|---|---|---|
| approach | `open`, `arrive` (late, concealed; score/bar/margin/origin/ordered for the player's own side only), `absent`, `flank`, `ground`, `presence` | the arrival rows, the shelf, the flank record, the defender's modifier rows, the Emperor's row |
| cannonade | `battery`, `overwatch` | the supporting bombardment results, the overwatch row |
| assault | `advance` (by temper), `ability`, and one beat per modifier row the report prints (`drilled`, `overrun`, `square`, `charge`, `reckless`, `exhausted`, `caught`, `outnumbered`, `stance`, `momentum`, `ground_horse`, `doctrine`) | `modifier_snapshot`, `ability_triggered` |
| crisis | `dice` (natural, skill, flank, modified, critical, swing, both fortunes), `break`, `holds`, `last_stand`, `stand` | `attacker_roll`, `fortune`, each corps' state after the battle |
| pursuit | `pursue`, `leave`, `advance_to` (contested when the enemy still stands in the province), `province`, `works`, `counter_punch` | `pursuit_damage`, the retreats, the advance, the capture |

**Fog (law 3, BA1-X2).** Three cases. The player's own side: everything above. The enemy in a
battle the player fought: what the field showed and what the battle's own report already prints
— never the province a corps marched from (he goes back there), his arrival roll, that he was
under orders, his court's doctrine, the provinces his attack came in from, his road off the field,
the bar his line holds to, or his free counter-blow. A battle the player only watched (the payload
exists at FULL sight of the field): who came, the dice, who broke, who holds the ground — no
modifier row of either army, no tactical state, no battery off the field. `tests/test_battle_script.py`
(65), fog at PARTIAL and FULL.

#### The table — `scripts/battle_acts.gd` (`BattleActs`), `scripts/diorama_plinth.gd` (`DioramaPlinth`)

`battle_diorama.gd` is hooked at four places and nowhere else (its pinned function bodies are
untouched): `show_diorama` (a battle opens settled when Settings says so), the end of `_populate`
(`dress`), the head of `_play_cinematic` (`plays` → `play`), the end of
`_apply_final_frame_instant` (`settle`). A fleet action and a payload from before the acts keep
the tableau's first sequence.

- **The plinth.** A slab under each corps' figures: the nation's band at its outer end, six pips
  on its front face, lost from the clash side as the count runs (any loss costs one; only a corps
  with nothing left has lost six); dulled when the corps is beaten. It is part of the block's art,
  so the block that marches and is driven back IS the plinth.
- **One law of rest.** Where the acts END is where the settled frame stands. `_plan_rest` decides
  every corps' resting place once: a beaten corps 56 px toward its own edge, one that draws off in
  good order 24, the pursuer 34 forward, the advance 18 — never off the baize (the room is measured
  on the corps' own locket, slab and words), and never closer to the rank behind than the line was
  laid out to stand, so a lead who breaks in front of steady supports falls back ON them. The verbs
  move toward it, the gavel brings whatever has not arrived, and `settle` (skip, a second viewing,
  "Final frame only", Reduce motion) puts it there at once.
- **Nothing tells the end early (BA1-X6).** The host lays the table from the battle's RESULT —
  each corps' line whole (`52,000 → 30,723`), the advance's toll, the laurels of a triumph, a
  defeat's red cast on the baize, what the reserve lost — and shows it from the first frame. When
  the acts open (`_set_opening`) a line reads what the corps BROUGHT and the rest is held back;
  the count runs the line (`_run_strengths`, with the odometers, the army bars and the pips); the
  toll is told with the advance; the gavel brings the cast, the laurels and the reserve's dead;
  `settle` has all of it at once. The cast and the laurels are chrome that outlives a showing, so
  they are tweened on the master sequence (a skip or Replay kills them with it) and the laurels'
  own alpha is kept on the node. A fleet action and an old payload keep the first sequence.
- **Every table that is laid puts the chrome back first (BA1-X7).** `_put_the_chrome_back`, at
  the head of `dress` and before the fleet action's return: the tray opaque, the laurels at the
  alpha they were built with — whatever a showing that was cut short left on them.
- **The showing.** `_plan`: full — every beat moves, the head beats are told, every act the battle
  has is named (an act of details alone tells its first), and details are told too while the
  budget has room; brief — the head beats, one each from the approach, the cannonade, the assault
  and the pursuit, the dice and the first line that breaks. A told beat holds by its length; over
  the budget (20 s full, 7.5 s brief) the holds are tightened, never under 0.72 of their length.
- **The dice.** Two ivory dice, drawn; `= N`; "N on the dice  +S skill  +F flank"; "the attack
  lands at P%" (the roll scales the blood the attack draws); "luck  France ±A%  ·  Austria ±B%".
  The tray keeps to the room between the banner and the crossed swords: a row that would not fit
  is left off rather than printed over a name (at the shipped type all three fit).
- **The guns.** A battery on the table fires from its own corps; one that fires from the next
  province (guns ordered in support) is a gun set at its side's edge of the field while it fires.
- **Settings → Display → Interface → Battle scenes:** In acts (the default) / Brief always / Final
  frame only. Reduce motion opens every battle on its final frame. Replay always plays.

#### One departure from the ruling's words, for the user

Ruling 2 says the plinth carries "the marshal's name and strength pips". The plinth carries the
band and the pips; the NAME stays above the men, where it has always been. Four ranks recede on
this table and the art is scaled with depth (0.64 at the fourth): a name on the slab would read
9 px there, under the floor every other line of the tableau is held to (UXR-X5), and the slab's
face has no room for a name beside six pips. Say the word and the name goes on the slab at the
front rank only.

#### The finds (BUG_FIXES §BA1)

- **BA1-X1** (older than the acts, on the shipped tableau's opening battle): the lead's strength
  line carried the advance's toll and ran across the other lead's figures; the toll is told under
  the lead's slab.
- **BA1-X2** (the acts' own, caught by the walk's frames): the script named an enemy corps'
  origin province; the fog law above is the fix and its sweep.
- **BA1-X3** (older than the acts): at four ranks the outermost corps' one-line caption
  ("marched to the guns") hung 4 px off the baize; a line that does not fit its room is wrapped
  inside it.
- **BA1-X5** (older than the acts): "click anywhere to skip" was true only of the dark margin
  round the tableau — its frame swallowed a click on the tableau itself. With acts of twenty
  seconds that is the first thing a player does; the frame passes the click up now. It surfaced in
  the suite (the real-client session presses the tableau's centre) and the walk skips by a real
  click since. A grid of 144 points over the window, clicked mid-act, skips at every one, at
  Interface Scale 1.0 and 2.0.
- **BA1-X6** (the acts' own, found on the walk of record's first frame after every claim had
  passed): the table told the end before a die was thrown — Mack's line read `52,000 → 30,723`
  and Ney's toll "after the advance" stood under his feet at second zero of a twenty-second
  battle, with the laurels of the triumph round the plate. Marks the shipped tableau always laid
  from the result; nothing in four seconds, a give-away over twenty. The class was swept (the
  strength lines, the toll, the laurels, a defeat's cast, the reserve's dead) and the walk now
  reads every opening for it.
- **BA1-X7** (older than the acts): a battle skipped in its first quarter second stayed
  half-transparent — the tray fades in from nothing, a skip rebuilt the settled frame, and
  nothing put the fade back (58 % measured). It took a click that lands on the tableau to meet
  it. Its sibling was BA1-X6's own, caught before the commit: the laurels the acts hold back
  would have stayed off the next battle after a showing closed mid-act. Every table that is
  laid puts the chrome back first.
- **BA1-X8** (older than the acts; **OPEN, owner Session H**): on a triumph the left laurel stands
  on the wax seal and the right one under Replay (Session UI-2 moved the seal; the laurels stayed).
  The acts made it plainer — the laurels now arrive with the gavel. Measured by the walk
  (`chrome_overlaps`); its strict-xfail pin is
  `tests/test_ba1_the_battle_in_acts.py::TestBA1X8TheLaurelsOfATriumph`. Where a victory's laurels
  stand is a composition for the session that owns the tableau's chrome.
- **BA1-X4** (older than the acts; **OPEN, owner Session H**): at Text size 150 % and over the
  tableau's lines outgrow its fixed layout — a name over its own figures, the losses caption over
  its count — on a battle of one corps a side. Its strict-xfail pin is
  `tests/test_ba1_the_battle_in_acts.py::TestBA1X4TheTableAtLargeType`.

#### Verification (the final tree, November 14, 2026)

- **The full suite on the final tree** (two workers, the hook's own environment): 40,890 passed,
  27 skipped, 17 xfailed, 0 failed. Its first run on BA-1 (40,882 passed, 4 failed) found what the
  subsets had not: a source pin on the fumble's own line (`test_sr6_reserve_the_quick_wins`,
  re-pinned to the line as it stands), the sign-ability sweep's quick seed arm (re-recorded) and,
  behind it, the band ("The measure" above); the other two failures were this session's shell
  (`PYTHONDONTWRITEBYTECODE` set — the stale-bytecode tests need it unset, as the hook has it).
- **The suite's own pins:** `tests/test_ws11_the_dice_are_the_campaigns.py`,
  `tests/test_battle_script.py`, `tests/test_ba1_the_battle_in_acts.py` (a DRIVEN headless walk of
  three battles fought fresh on the 1805 board — lane `engine_frames`; the walk of record; the
  instruments' records; the seams). `tests/test_battle_diorama.py` green unchanged; the sixty test
  files that pin the client files this slice touched green.
- **The walk of record** (`docs/audits/ba1_client/`: `walk_record.json`, nineteen kept frames
  `BA1_*.jpg`, the eleven staged payloads and their manifest): `tools/ba1_stage_battles.py` fights
  eleven battles on the 1805 board through the real attack road — the opening battle at Ulm, Mack
  taken with his army, a corps at the last hour, a flank (two attacks in a turn), an enemy corps
  coming up unseen, an ordinary exchange, a defeat on the defence, another court's battle watched,
  a day that hangs, four corps a side, a supporting battery — and `tools/ba1_acts_walk.py` plays
  each on the real `battle_diorama.tscn`, windowed, at the scene's own speed: 31 shots, 0 script
  errors, every claim holds. The claims, read off the engine's record: the acts END where the
  settled frame stands; a real click on the tableau, mid-act, gives that frame at once, and so
  does one on the margin; "Final frame only" and Reduce motion open on it and Replay plays;
  "Brief always" tells fewer developments and ends on the same table; every act the script
  carries is named; when the acts open no line on the baize carries an arrow, the baize wears
  no cast and no laurel flanks the plate, at the crisis a line is running, and at the end every
  corps reads brought → kept, a triumph has its laurels, a defeat its cast and the reserve its
  dead (BA1-X6); a showing cut short — a click in the first instant, or Esc and then another
  battle on the same tableau — leaves the next table whole (BA1-X7); a corps that marches in
  starts off its place and unseen, an
  enemy corps dark until it is made out; a payload from before the acts (an old save's) plays the
  first sequence and settles with plinths and no dice; the pips are the rule's; the advance's toll
  is under the feet; at rest no line of text stands on another or on a portrait and none leaves
  the baize. The same claims hold headless at Interface Scale 2.0 and at Text size 100 %.
- **The instruments** (`docs/audits/uxr0/{readability,contrast}_ba1_battle_acts_2026_11_14.json`,
  `docs/audits/uxr3/{fit,frame_census}_ba1_battle_acts_2026_11_14.json`; shot on the working tree
  over `4009b2d5`): fifteen surfaces — the six standing tableau states (which now carry plinths and
  dice), five new settled states, two MID-ACT frames, and the two Settings pages — at the five
  physical sizes with the Interface Scale each derives (1.0 to 1.8): readability 2,599 rows, RED 0,
  P1 0; contrast 2,454 rows measured, 0 under the floor; fit 15 of 15 at 1920×1080, 3840×2160 and
  5120×1440; the frame census 75 frames, no cut line, no grip or tick overlap, the verdict's room
  9.6 px at the least. Six frames at Interface Scale 1.0 and 2.0 are kept
  (`docs/audits/IQ10_DIORAMA_BA1_{FIELD_AT_REST,ACT_CRISIS,DEFEAT}{,_X2}_2026_11_14.png`).
- **One instrument rule added.** The new Settings row moved the scroll's fold one row down, and the
  toggle then cut to 2 px read 3.49 : 1 at two sizes — its own border's colour. A row a scroll's
  edge cuts to under a third of its height is not measured (`uxr2b_contrast_report.cut_to_a_sliver`;
  eleven such rows on these seventy-five frames).
- **One rule the instruments taught the acts.** What the acts hold back is taken off the table
  (`visible = false`) and put back as it fades in — the advance's toll, an unseen corps' name and
  numbers. Drawn at no alpha instead, the toll was read by the contrast instrument as unreadable
  text (1.00 : 1) on both mid-act frames at all five sizes: the instrument reads every line in
  the tree at the colour it is drawn in, alpha and all.
- **Not measured here:** the readers' blind marks (the last reading was Session UI-6's; a battle in
  acts is motion, which a still frame does not show — the user's own look is the reading).

#### Owned by the sessions after this one (§15.7)

BA-2: the garrison assault's and the bombardment's tableau; the plan of battle named in Act I and
orderable at the attack row. BA-3: the crisis, NP-D1, the two rule changes, WS-16, the measure
with arms (its "seeded dice" arm calls `serve_campaign` on the harness's own world). Nothing of
those is in the client or the wire today, and no control promises them.

### 15.11 BA-2's gate — the board and the hand (November 14, 2026, authoritative; it amends §15.5–§15.9)

**The user's words (November 14, 2026).** Beside the BA-2 brief: "also evaluate how player agency
should work in battles i want it to be like watching an inetretsing strtagic battle with flanks and
movements unfold but the player has abstrtact interactions think black and white how the demi god
controls the town a cool way to interatc that relfects how battles wrre back then" — then, to the
model put back to him, "Plan on it". On defence: "make decision yourself do researcxh". Away from
the Emperor: "make best call". Then: "and we dont ened to use emperor framing the concept is to
make battles an enaging autobattler with abtract player feedback you are playing the emperor thew
whole time", and "but they should mvoe in napolenic stile of course keep going". On four corps a
side: "make best call". The plan was drafted in Plan Mode and approved ("go ahead with plan").

**The concept, as ruled.** The player sets the board; the battle plays itself, moving as armies of
the period moved; between rounds the table offers abstract commands. BA-2 builds the first two —
everything the player sets and everything he watches. BA-3 builds the third.

**What was measured for it** (read-only probes; five named seeds, 40 turns each; the France of the
AI-France harness is played by the courts' own AI, not a person):

| | lodi | marengo | austerlitz | jena | wagram |
|---|---|---|---|---|---|
| Every court's field battles / the day hangs | 84 / 45 | 75 / 37 | 58 / 34 | 72 / 36 | 61 / 28 |
| AI-played France attacks / the day hangs | 40 / 15 | 29 / 12 | 34 / 11 | 25 / 11 | 27 / 9 |
| …with the Emperor's corps on the field / hangs | 17 / 6 | 10 / 2 | 14 / 4 | 7 / 2 | 9 / 3 |
| France defends / the day hangs | 13 / 10 | 8 / 4 | 5 / 3 | 9 / 7 | 4 / 3 |
| A court attacks the Emperor's own stack | 0 | 2 | 0 | 1 | 1 |

The day hangs in 180 of 350 field battles (75 won on points, 71 drawn, 34 lost on points). With
§15.5.6's "the Emperor stood on the field" gate the hinge would have come up 17 times in five
campaigns; without it, 58 times — about one attack in three.

**Seven decisions under the delegation (each one line to reverse).**

1. **The hand is in every battle the player fights.** No rule hangs on where the Napoleon piece
   stands ("you are playing the emperor the whole time"). §15.5.6's presence gate is struck; the
   rest of §15.5.6 is BA-3's to re-plan as "the rounds" (below).
2. **On defence** the hand is the board the player left: Act I names his dispositions (built here)
   and, once the enemy's phase has ended, a defended day that hung offers the riposte as the
   ordinary attack order at its ordinary price — free where the lead already holds a counter-punch
   (BA-3). Nothing new resolves inside the enemy's phase. The standing instruction to the Guard is
   not built: a court attacked the Emperor's own stack 0, 2, 0, 1, 1 times.
3. **Away from the Emperor**: superseded by decision 1. "Marshals settle a hanging day alone" is
   not built: a court's marshal already decides a second attack by the AI's own decision tree.
4. **A round costs what an attack costs** (the answer recommended for BA-3's first head question,
   the stroke's price; the question stays the user's): priced rounds cannot be cheesed, so the
   hinge may be offered on any hanging day.
5. **Session shape.** BA-2 carries the board and the manoeuvre as well as the walls, the guns and
   the plan (the wall storm and the battery use the same movement verbs, and the table is re-shot
   once). BA-3 becomes "the rounds". Nothing moves after the deploy.
6. **Four corps a side: three seats and a reserve.** The layout study (stage 948 × 440, the shipped
   Text size 115 %) found that a centre and two wings fit for up to three corps a side and that
   nothing seats a fourth: the table seats three (`MAX_CONTINGENTS_PER_SIDE` 4 → 3, display only),
   the rest stand in reserve, counted with their dead as the table already did. The seats go to the
   lead, then the Emperor's corps if it fought, then the largest. The other answer — the wedge to
   three, the old file at four — would have left the wedge out of exactly the battles played in
   full; it stays the fallback for a payload that seats four (an old save's).
7. **The AI crash found in passing** (seed jena: Prussia's turn dies on `KeyError: 'Yorck'`) is
   filed here (BUG_FIXES §BA2, BA2-X2) and owned by BA-3, whose measure can show what the one-line
   fix moves.

**What BA-3 becomes — "the rounds"** (its own Plan Mode; the three head questions of §15.7 stay the
user's, with decision 4 as the answer recommended to the first). A battle the player fights is
played in rounds. When a day hangs the table stays up and offers, on the pieces themselves, the
existing orders at their ordinary prices: **Press** (the lead attacks again, with the penalty his
second attack already carries), **Commit** (a chip per corps an order would still bring — the same
rows as BA-2's `bring`; the Guard when the Emperor's own corps is at hand, with the two morale
numbers ruled for NP-D1), **Hold**. The lead answers through the objection road as it stands. After
the enemy's phase a defended day that hung offers **Riposte** the same way. BA-3 also keeps NP-D1,
the two rules of §15.5.7, WS-16, the BA2-X2 fix behind its seam, BA2-X7 (the muster's lever
sentences held to what the order delivers — the Commit chips are those rows), and ONE measure
with arms. Its
named test is `tests/test_ba3_the_rounds.py` (it supersedes §15.7's `test_ba3_the_crisis.py`) with
`tests/test_ws16_the_same_order_draws_the_same_temper.py` as named.

### 15.12 LANDING RECORD — BA-2 "the board, the walls and the guns" BUILT November 14–15, 2026 (authoritative)

**What a player sees.** Each side stands in an order of battle: the lead forward and nearest the
line, a wing on either hand behind it, the rest in reserve — counted, with their dead, beside their
side's loss counter. Foot comes on in column and deploys into line; horse comes on at the trot,
charges home and recoils, and in pursuit sweeps round the beaten corps; guns unlimber forward of
the line; a corps the battle met in square stands in square; a flank comes in as a column on the
enemy's wing; field works stand as a bank with its stakes. Act I names the plan the player's orders
amount to — or, when he is attacked, his dispositions. A garrison assault opens the table: a
battlemented wall between the garrison and the line, the stormers going in by column with ladders,
then the wall scarred, broken down under the stormers' colour, or under a white flag. A bombardment
plays the cannonade alone. At the attack row and on the attack card each corps the muster says will
not come, or may not, carries a chip for the order the game already has that would bring him.

#### The two tableaux — `backend/game_logic/siege_diorama.py`

- Both build the field battle's payload shape and ride its two keys (`battle_diorama` at the top
  level, `events[0]["diorama"]`), so the stash, the auto-play, the enemy phase and both links work
  unchanged; `payload["kind"]` (`assault`, `bombardment`; absent for a field battle) says which
  table to lay. Every number is an int. Display only: the module assigns to nothing it is handed.
- **The assault** is built at the three returns of `_resolve_garrison_combat` (a wrap each,
  `with_assault_tableau`), so every caller is covered — the player's attack, the AI's P4.25, the
  naval landing. `fate` is `held`, `stormed` or `capitulated`; the garrison is one contingent with
  no marshal (`garrison: True`). It is `significant` when the player is a party, the wall fell or
  the engagement is great, and `dramatic` when the wall fell or it is great. This closes the
  garrison rider of §12.5 (CA8-25).
- **The bombardment** is attached at every STANDALONE call site of `_execute_bombardment`
  (`with_bombardment_tableau`: the attack router, two in `meta_executor`, one in
  `strategic_executor`) and never inside it, nor on the supporting salvo before an assault (that
  one stays a beat of the battle it prepares). It opens by itself only when the target is destroyed
  or his works are brought down to nothing.
- The tableau rides a COPY of the event (`_carry`): `_execute_bombardment` logs the very dict it
  returns, and a picture written on it would be in the campaign log and the save.

#### The script — every new beat's fog case (decided before it was written; §219.2)

| Beat | Told to |
|---|---|
| `plan` — the attack's (the lead; corps ordered in support, one who was ordered and did not come among them; the provinces and the flank's +N; a drilled assault; stance; guns in support) | case 1: the player's own side only |
| `plan` on defence — "Your dispositions" (heights, field works, the fortress, a square, stance, batteries on overwatch, corps in support); it replaces the `ground` beat it would repeat | case 1 only |
| the assault's `open`, `walls`, `storm`, `wall_holds` / `wall_falls` / `capitulates`, `province`, `occupy`, `repulsed` | all three cases: what the field showed, and the garrison's figures as the assault's own report prints them |
| the assault's `drilled`, `ability` | case 1 only: the storming side's own rows |
| the cannonade's `battery` (who fired on whom, how many fell), `destroyed` | all three cases |
| the battery's own losses and the province it fired from, `bystander`, `works`, `shaken` | cases 1 and 2; never a watcher |

A watcher's payload keeps to his script: no works figures, no province fired from, the plain
banner, and levelled works open nothing. No plan beat is told for a bare one-corps attack. A
cannonade is told whole (`form` `full`).

#### The plan, orderable — `backend/commands/order_quotes.py`

`bring_quotes` walks the muster ladder as the muster's own odds do and returns, for each corps of
ours in the battle's province or beside it that will not come for a reason an order answers
(`literal_awaits_orders`, `eyes_on_a_crown`, `holding_position`) or whose odds an order lifts by 15
points (the muster's own bar for naming the lever), the EXISTING `support_quote` — its command and
its price — with the reason, or the odds before and after. Pure (it never stages the muster, which
would spend the one-time muster hint); `[]` for a lead that is not the player's. Every attack quote
carries the rows as `bring`. No new order, no new modifier, no new lever constant.

**It promises only what the order delivers.** A SUPPORT order marches the corps toward the lead at
once, so the odds "under a written order" are read from where that first march leaves him
(`_stop_this_turn`: the quote's own road as far as he ranges, short of a corps we see on it;
`_odds_under_the_order`: the muster's roll from there, on a copy of the corps), and a row is
offered only when he will still stand on the field or beside it with odds above nothing. On the
campaign's opening board that takes Bernadotte out: the ladder gives him 47 % from Franconia, the
order marches him to Munich, and from its mountains he cannot reach the field. The test holds the
offer to the game itself — each candidate's order is sent on a fresh board and the muster read
after it: offered if and only if it brings him.

**An order that asks is not an order that brings** (`_first_step_asks`). Where a corps we see
stands in the road's FIRST province (and that province is not the friend's own), the order's first
step is no march: the aggressive man fights at once if the numbers favour him, every other asks.
On the opening board that is Murat, whose road to Ney runs through Mack — the order stops him on
"Mack blocks the path at Swabia. Odds unfavorable. Your orders?" (the client's MURAT REPORTS), and
of its four answers one keeps the order (Go Around), one sends him in alone (Commit the Attack) and
two abandon it with the action spent (Hold Position, Cancel Order). No row. The first oracle read
the muster with the question still standing and passed him; pressing the chip in the real client
(`tools/ba2_mode_c_walk.py`) found it. Murat keeps a row for Lannes, beside whom he stands (no road
to walk). For every corps that could lead on Mack, not Ney alone, each offered order is sent on a
fresh board (eight on the staged opening board): the order is his — at once, or after an objection
his chip said was possible ("he may object") is insisted on — no question is raised, nothing is
fought, and the lead's muster counts him as ordered. What the order MEETS on the road still rides
a row (`contact`: "Mack blocks the road at Swabia — Soult goes round him by Lorraine, to the letter
of the order"; a march that "halts before him this turn") and is said on the chip.

#### The table — `scripts/battle_acts.gd` (the host's pinned bodies untouched; its hooks still four)

- **Three seats and a reserve** (§15.11 decision 6): `MAX_CONTINGENTS_PER_SIDE` 4 → 3; seats to
  the lead, then the Emperor's corps if it fought, then the largest. `_relay` lays the wedge before
  a corps' home is read (the lead 330, 342; the near wing 128, 380; the far wing 128, 182; the
  right side mirrored); `_wedge_is_clear` measures the live boxes and `_unrelay` puts the host's
  file back when a pair of lines is closer than 3 px (Text size 120 % and over); a duel of one
  corps a side and an old payload that seats four keep the file.
- **The reserve's note** stands beside its side's loss counter: the count on one line, its dead on
  a second, held back until the gavel as every mark laid from the result is (BA1-X6).
- **The verbs**, each keyed on data the payload already carries and none adding a beat or a second:
  column into line, the trot / charge / recoil, the pursuit's sweep, guns unlimbered, the last hour
  at the double, the flank as a column round the enemy lead's outer end, the wings a short step
  forward with the lead.
- **The ground**: `SiegeWall` (whole until the crisis; then held, stormed or capitulated), `Rampart`
  (field works at three pixels a percent, read off the beats alone, so a watcher who is told of
  none sees none), `SquareMark` and `_form_square` (the stands re-formed as a wargamer lays a
  square, in the host's own drawing order).
- **The chips and the links**: `region_panel.gd` (a marshal's own row; the ATTACK rows, behind one
  fold when several corps could lead), `order_confirm_card.gd` (the chip whole, the reason beside
  it; `bring_requested`), `main.gd` (`_on_order_card_bring`; the terminal's "⚔ View the field" for
  an assault and a cannonade), `enemy_phase_dialog.gd` (`_field_link` on three rows).

#### The finds (BUG_FIXES §BA2)

Seven rows. **Fixed:** BA2-X1 — Berthier's bombardment line is written from behind our guns, and the
enemy phase printed it for enemy batteries ("Ney's numbers absorb our fire"); he reports the
Emperor's batteries only, and the line is still picked first so no measured series moves. BA2-X3
(the session's own, caught by its frames) — a corps of the battery's own side caught under the fire
was counted in the target side's losses. BA2-X4 (the harness's) — the walk kept end frames with the
verdict half written. BA2-X5 — the settled frame of a defeat left the victor's standard at home
where the played end leaves it advanced (older than the acts). **Open:** BA2-X2, BA-3's — a court's
whole turn is lost to a `KeyError` when a corps beaten to nothing is raised again in the middle of
its phase (seed jena, Prussia, Yorck; found by the probe above); its one-line fix moves a measured
world-line and lands behind a seam in BA-3's measure. BA2-X7, BA-3's — Berthier's muster promises
what the order does not deliver: on the opening battle it says a written order "would likely bring"
Bernadotte, and the order marches him out of reach; and it names the same order for Murat, whom it
stops on his question (older than this session; the first cut of the chips repeated both as
buttons — the first was caught by sending each chip's order, the second by pressing the chips in
the real client; the chips are honest now, the muster's sentences are filed). BA2-X6, Session H's — a long province's panel opened with its
fold through a line (fixed: `_window_on_whole_lines`); scrolled, it can still rest on a cut line.

One of the session's own, caught by its named test and fixed before the measure of record: the
stormers closed up into columns and stood in line again a quarter second later whenever they won —
the host shudders a line that takes fire and puts each man back where he stood when the shudder
was scheduled. The column now forms after it (`_close_up`, `AFTER_THE_RECOIL`), and the walk
claims it at the storm.

#### Left with the user (each one line to change)

- **Three seats and a reserve in every battle**, the great ones included; the fallback (the wedge
  to three, the old file at four) is one constant and one cap.
- **A garrison that yields is drawn fallen**, with CAPITULATED under it: the tableau topples every
  figure of a corps that is no more, and the garrison's men are lost to its crown either way.
- **A garrison under the collapse line gives way without a fight** (SF7-X31): a march in, not an
  assault — no tableau.
- **"Breaks or destroys its target"** is read as "destroys its target or levels his works": guns
  never break a corps.
- **The province panel says the order once on the line** ("Bring up to support Ney:") and each chip
  is the man and the price ("Soult · 1 AP"); the attack card prints the chip whole ("Soult ·
  support Ney · 1 AP"). §15.5.5's "priced on its face" holds on both.
- **A chip on the attack card sends the order at once and closes the card** (its muster is no
  longer true), the lead selected again.
- **Berthier says nothing of an enemy battery's fire** (BA2-X1): the enemy phase's bombardment
  report keeps its figures and loses the line that was in the wrong voice.
- **A chip is offered only when the order brings the man, without a question** — so on the opening
  battle Ney's attack offers Soult alone: Bernadotte's order would march him out of reach and
  Murat's would stop him on "Your orders?" (Mack stands on his road), though Berthier's muster
  still names the order for both (BA2-X7, BA-3's). Murat has a chip for Lannes, beside whom he
  stands.
- **Recommended, and a rule, so yours** (BA-3's Commit would use it): a SUPPORT order whose road's
  first province holds the very corps the friend is to attack should halt at the approach and join
  the next attack there — the arm the order already has when the foe holds the friend's own
  province — so that a corps like Murat can be committed by an order at all. Not built.

#### Verification (the final tree, November 15, 2026)

- **Played by hand through the game server** (`/command`, `/march_quotes`, the enemy phase's
  chokepoint, `/save`) before the long runs: a wall stormed (both transports one payload, no float);
  a battery fired (a link: `significant` false; nothing of the tableau in the event log or the
  save); a chip pressed and then the attack (Soult's SUPPORT order taken at 1 action, the muster
  then names him, Act I reads "The plan: Ney leads; Soult ordered in support"); each chip's order
  sent on a fresh board and the muster read after it (which is what took Bernadotte's chip away —
  BA2-X7), then every chip for every corps that could lead on Mack (eight orders on the staged
  board: each taken, no question raised, nothing fought); an enemy assault on
  Paris carried through the enemy phase with its tableau on the action and on its event (held: a
  link; stormed: it seizes the screen).
- **The plan's loop pressed in the real client** (`tools/ba2_mode_c_walk.py`; record and frames
  `docs/audits/ba2_mode_c_2026_11_15/`): the real main scene against a sandboxed backend on the
  opening board — the panel's fold and its "+N more" (Soult offered to six leads, Murat to Lannes
  alone, Bernadotte to none); the panel's chip pressed (Soult to Ney: 4 → 3 actions, no question);
  a chip pressed on Lannes's attack card (Murat: the card shut at once, 3 → 2 actions, Lannes
  selected again, his next card counts Murat and offers him no chip); Ney's card (Soult in the
  muster, no chip left); the attack sent; Act I reads "The plan: Ney leads; Soult ordered in
  support." 9 of 9 steps hold, 10 frames kept, 0 script errors. Its FIRST run is what found Murat's question (BA2-X7's second half): his
  chip for Ney raised MURAT REPORTS, and the walk could go no further.
- **BA-2 moves no number.** The keyed world probe — every top-level key of `world.to_dict()` hashed after each turn, `PYTHONHASHSEED=0`, a notification's fresh uuid masked — on seeds jena and marengo, 30 ambient turns of the 1805 campaign, 212 keys a turn: the final backend reads identical to HEAD `74d9d139`, turn for turn and key for key, on both (jena's one lost court's turn, BA2-X2, stands in both).
- **What the plan's rows cost.** The province panel's one request at Swabia on the opening board —
  the busiest there is: eight corps quoted the attack, seven rows of the plan — takes 31.3 ms at HEAD `74d9d139` and 38.4 ms on the final tree
  (best of 15, in process).
- **The walk of record** (`docs/audits/ba1_client/walk_record.json`; windowed, at the scenes' own
  speed): 22 engagements fought on the 1805 board through the real attack road, and BA-1's
  own four-a-side payload kept as it was staged — 55 shots, 0 script errors, every claim
  holds; 33 frames kept (`BA1_01` … `BA1_33`). The claims this session added: a wall
  opens whole and ends as the assault left it, as the settled frame has it, no stormer in its
  stone, no ladder against a wall that held; a garrison shows no portrait and no standard; a
  cannonade names the cannonade alone and throws no dice; field works stand at the strength the
  battle met them with and end where its report says; two or three corps a side lay the wedge —
  the lead nearest the centre line, the wings on their own hands, the two sides mirrored — and
  anything else keeps the file; no line of a corps stands on another corps' men; a corps comes on
  in column and ends in line; a corps told in square stands in square from the first frame; at
  the storm the wall is still whole, the ladders are up and the stormers are closed up in column;
  every standard stands at the end where the settled frame has it; the reserve's dead are not on
  the table when the acts open. **Each was watched failing with its fix switched off**
  (`tools/ba2_switch_off.py`, ten cases — the four read in a showing's first instant at the
  scene's own speed): ten of ten caught. (The walk ran before the chips' rule was tightened for
  Murat; that change is in `order_quotes.py` and the tests, none of them a source the walk
  fingerprints. The captures, the instruments, the kept frames and the live-client walk were all
  shot after it.)
- **The instruments** (`docs/audits/uxr0/{readability,contrast}_ba2_walls_guns_2026_11_15.json`,
  `docs/audits/uxr3/{fit,frame_census}_ba2_walls_guns_2026_11_15.json`): 25 surfaces —
  the six standing tableau states and BA-1's seven (all re-shot on three seats), eight new settled
  states, the storm mid-act, the province panel with the plan's fold shut and open, and the attack
  card — at the five physical sizes with the Interface Scale each derives: readability 2,855
  rows, RED 0, P1 0; contrast 2,855 measured, 0 under the floor; fit 25 of 25 at
  1920×1080, 3840×2160 and 5120×1440; the frame census 125 frames, no cut line (it
  read one on the province panel at 5120×1440 — BA2-X6 — before the fold was set), no grip or tick
  overlap, the verdict's room 9.6 px at the least.
- **The parse harness:** 98 scripts and 17 scenes, no error.
- **Tests:** the session's five files in the engine (`tests/test_ba2_the_walls_and_the_guns.py`, `tests/test_ba2_backend_walls_guns_plan.py`, `tests/test_ba1_the_battle_in_acts.py`, `tests/test_battle_script.py`, `tests/test_battle_diorama.py`): 226 passed, 5 xfailed — the strict pins of the five open rows (BA2-X2, BA2-X6, BA2-X7, BA1-X4, BA1-X8). The 230 test files that read the changed surfaces, run before the chips' rule was tightened for Murat: 14,206 passed, 3 skipped, 12 xfailed.
- **The full suite on the final tree:** 40,961 passed, 27 skipped, 20 xfailed, 0 failed (four workers under `--dist loadgroup`, 17:29 — the hook's ten workers want more memory than was free beside the user's open applications; the hook itself runs at the commit).
- **Not measured here:** the readers' blind marks (a battle in acts is motion; the user's own look
  is the reading), and Text size 150 % and over (BA1-X4, open for Session H: at those sizes the
  wedge gives way to the file by `_wedge_is_clear`, and the file's own lines run together as
  before).

#### Owned by the session after this one

BA-3 "the rounds" (§15.11): the table's commands between rounds (Press, Commit, Hold; Riposte after
the enemy's phase), NP-D1, the two rules of §15.5.7, WS-16, BA2-X2 behind its seam, BA2-X7, ONE
measure with arms. Nothing of those is in the client or the wire today, and no control promises them: the
chips BA-2 added are the SUPPORT order the game already had.

### 15.13 THE REVIEW — BA-2's one review (November 15, 2026, authoritative)

The user's "Review now", after BA-2's commit `567f3e85`. Six readers on a frozen copy of the commit, each in
a lane and none able to write to the checkout: the two tableaux and their wiring; the script and the fog; the
chips played out on later boards and other seeds (about 1,700 chips sent, each on a copy of the world); the
client (read, not run); the tests and the tools; the records. Every finding was reproduced, or read in the
code, before anything was changed. **Nothing crashes, leaks or touches a save.** The rows are `BUG_FIXES.md`
§BA2, BA2-X8 … BA2-X19; the tests are `tests/test_ba2_the_review.py`; the rules are `SYSTEMS_REFERENCE.md`
§220.7.

#### Fixed in the review's commit

- **The chips promised more than their order delivers, three ways** (`order_quotes.bring_quotes`). BA2-X8: a
  chip was lit when its price was the last action; pressed, the attack it was offered for was refused. It is
  offered now only while the attack can still follow (`attack_ap`, the attack's own price). BA2-X9: a chip
  was lit when its order first ASKS "support, or cancel?" — a road round a neutral's shut frontier, guarded
  ground (the quote's `detour` and `guard`); such an order is not offered, as one that raises a marshal's
  question already was not. BA2-X10: a literal marshal's odds were read from the first province of his road
  round a corps — a march he is refused when that province is a neutral's; `_stop_this_turn` stops at a
  frontier he may not cross (`can_enter_territory`, the move's own rule).
- **The cannonade's two sides** (`siege_diorama.build_bombardment_diorama`). BA2-X11, BA2-X3's sibling: a
  corps of the guns' own side that found no seat was counted, men and dead, in the target side's reserve
  line; it is its own side's reserve. BA2-X12: a battery caught by its own stray shells was seated twice,
  once on each side; it is seated once, and its dead are its own.
- **The words** (`battle_script.py`). BA2-X13: the plan called a PURSUE order "ordered in support"; the
  reinforcement row names its order (`order_type`) and the plan words each in its own way. BA2-X14: "1
  defenders remain", "1 men", "0 men the fewer" (`_men`, `_fall`).
- **The tools.** BA2-X15: `tools/ba2_switch_off.py` changes `battle_acts.gd` in the working tree while it
  runs; it takes a lock, keeps a copy until the file is back byte for byte, checks every anchor before it
  writes and limits the walk's time. BA2-X16: `tools/ba2_mode_c_walk.py` copied a run over the committed
  record before judging it; a run that does not pass stays in its run folder. BA2-X18: the keyed world probe
  behind "BA-2 moves no number" is kept as `tools/keyed_world_probe.py`.
- **The records** (BA2-X19): `STATUS.md`'s head still named BA-2 as next; two stale pointers; the head
  questions and Session H's head list in `NEXT_SESSION_PROMPT.md`; §15.5.4's words against §15.12's reading;
  the pre-commit hook's stated time (9:51 measured at BA-2's commit; the banner and `CLAUDE.md` said 8:22).

#### Filed, each with its owner and a strict-xfail pin

| Row | Owner | What |
|---|---|---|
| BA2-X10, the cause | BA-3, behind a seam in its measure | A literal marshal's road round a corps is plotted through a neutral's shut frontier: the order is taken, the first march is refused without a word, the reply still promises an arrival. Older than row BA. The fix moves marches, the AI's too. |
| BA2-X12, the cause | BA-3, behind a seam in its measure | A battery standing in its target's own province takes its own collateral fire (the post-objection and defiance roads allow the distance). Older than row BA. The fix takes a roll out of the battle's stream on that road. |
| BA2-X14, the half left | BA-3, with its walk of record | A gunner ordered in support is named twice in one plan. The fix changes the staged scene `the_guns`, whose payload and frames are on record. |
| BA2-X17 | BA-3, with its walk of record | The walk's record carries a hash of each source and no test compared them; four sources that shape the walk are not on its list. |
| BA2-X16, the siblings | Session H | The four older live-client walk tools export before they judge; the mutation sweep takes no lock against a second copy. |
| BA2-X20 | BA-3, behind a seam in its measure | A battle between other crowns lights its province at FULL for the player. Older than row BA. Handed over by the user's word; the recommendation is below. |
| BA2-X21 | BA-3, with its Commit chips | No quote names the men an order's first march costs. Older than row BA. Handed over by the user's word; the recommendation is below. |

#### Read and left as it is

- **The fog gate of the two new tableaux is a backstop and cannot refuse on a real road.** Every battle,
  another crown's included, lights its province at FULL before the tableau is built
  (`WorldState.update_intel_from_battle`, Session 34A — older than row BA, not changed here), so
  `siege_diorama._in_sight` always passes; what keeps an unseen fight from the player is the enemy phase's
  own filter. No channel was found by which a tableau leaves the backend without passing that filter. The
  gate's tests read the gate alone. Whether a battle between two other crowns should light its province for
  the player is the fog doctrine's question, and the user's. *(Answered the same day: BA2-X20, below.)*
- The assault's `walls` beat tells a watcher that the fortress stands (§220.2 rules it for all three fog
  cases; a watcher sees the province whole).
- An order's first march costs men by the ordinary march rule, and the chip does not say so; no march quote
  does. Recommended to the user, not built: every order that marches quotes the march's cost in men.
  *(Handed to BA-3 the same day: BA2-X21, below.)*
- The client: nothing found. It was read, not run.

#### Handed to BA-3 by the user's word (November 15, 2026)

The user, on the three points the review left with him: "make allr eccomendations here … and hand them to
ba 3 in next session". The recommendations are BA-2's session's, made under that word. BA-3 builds them, each
behind a seam or in one line, and its plan's gate may overrule any of them (`NEXT_SESSION_PROMPT.md` scope
6b). Two are rows with strict-xfail pins (BA2-X20, BA2-X21); the commit that records this hand-off changes no
code of the game.

1. **A battle lights its field for those who fought in it (BA2-X20).** `update_intel_from_battle` grants the
   player FULL sight only when he is a party to the battle (his nation attacks or defends, or a marshal of
   his fought) or it is fought on his own soil; a battle between other crowns leaves the province at the
   sight he had. `FOG_OF_WAR_SPEC.md` §4.4 was written when "every battle in the current game involves a
   player marshal"; on the 1805 map the courts fight each other, and each such battle showed him the
   commanders, the men and the morale of two crowns he had no one near, for two turns. So that Europe does
   not go dark, the Gazette prints such a battle as news the turn after — who fought, where, who held the
   field, no numbers — when it is a great battle or an ally's in a war he shares. The commanded arms play
   France by what France sees: an arm of BA-3's measure, reported per seed.
2. **A quote names the men its first march costs (BA2-X21).** The march rule is exact, so the figure is: the
   calculation split from its application, a `march_cost` line on every quote of an order that marches at
   once, shown where the quote's other notes are. It moves no number.
3. **How BA-3 takes the rows.** The seam arms in this order: BA2-X2; BA2-X12; BA2-X10 with the support
   order's approach rule — recommended IN; both rewrite the SUPPORT order's first step, so one change and two
   seams; BA2-X10's road keeps to provinces he may enter, and where none goes round the order ends at the
   approach and says so; BA2-X20; then the two ticked rules and the rounds. BA2-X14's left half and BA2-X17
   ride the walk of record; BA2-X21 rides the Commit chips. The head's second question: yes — a pursuit
   ability fires for any corps of the victor that FOUGHT on the field, whether it marched in or stood there.
   The head's third: as many rounds as the actions allow — Press is the attack order the command line
   already takes. If the plan finds all of it more than one session, the cut that keeps each seam with its
   measure is the roads and the fog first, the rounds second, both before Session H; nothing moves after the
   deploy.

#### Verification

- The reviewers' own cases, read again on the fixed tree, and `tests/test_ba2_the_review.py`: 32 passed and
  7 strict xfails (the rows above).
- **The chips played out again on the fixed tree** by the reader who found them wanting: 1,685 chips sent on
  three seeds (the historical seed turns 1–8, seed 3 turns 2–11, seed 5 turns 1–10; natural play and staged
  placements), each on a copy of the world. After every press the attack it was offered for could still be
  sent. No chip that stood before is gone. Seventeen new ones stand where a shut frontier keeps a corps
  within reach of the field (it was read as marching out of reach); each was sent and delivered, at the odds
  it named. What still fails there fails on the commit before the fixes too, and none is a chip's promise:
  corps the reader had placed by hand beside an enemy, a marshal who defied after "Insist" (the chip says he
  may object), and a corps unseen on the road (a surprise no quote may name).
- **The walk of record still shows what it showed.** All 22 staged engagements were staged again on the fixed
  tree and every payload file is byte for byte the committed one; the client's four sources are untouched.
  Two backend sources of the record's six changed (`battle_script.py`, `siege_diorama.py`: words and counts
  on roads no staged scene takes). BA2-X17 owns making that comparison a plain test.
- No `.gd` file is changed, so the parse harness's committed report stands.
- Run in a private copy of the commit before the fixes were put into the checkout, the engine lanes left
  out: the test modules that read the changed code (65) — 6,751 passed; those that read the records and the
  ledgers (387) — 22,427 passed. The only failures there were tests that drive the engine or ask git what is
  tracked, which a bare copy cannot answer (they pass in the checkout), and two of the review's own first
  rows and pins, put right before the commit (an open row's tag names a scored pillar; a pin reads a ledger
  through `tests/_ledgers.doc_text`). The pre-commit hook is the full run.

### 15.14 BA-3's gate — "the day's points" (November 15, 2026, authoritative; it amends §15.5.6, §15.7 and §15.11)

**The user's words.** BA-3 opened as "the rounds" (§15.11). The user first gave four weaknesses of that
design — *"The choice may be obvious … Repetition … Actions may be too scarce … Defence is still
watching"* — with *"address all these make this a 10-10 maybe the actions within battle dont use ap ?
make ruling on all do deep research"*. A first plan that priced each word in campaign actions was
rejected with the frame this section records: **"what if battles just have x amount of points in them
and how you and enemy use them is at discretion?"** Asked three questions, the user answered: the
points come from **"The commander"**; the enemy spends his on **"All that you can"**; the defence's
timing — **"make choice"**. Then: *"look for any other improvements like i just did, and we dont want
players fatigued if they always pop up these battle screens should be for key battles … where others
get simpler"*, and — correcting my reading that small battles would lose their screen — **"small
battles show the screen current state it just doesnt need all mechanics"**. The plan built on those
words was approved in Plan Mode.

**What was measured first** (read-only probes; the commanded France script, seeds austerlitz and
marengo, 40 turns each):

| | both campaigns |
|---|---|
| Battles the player was party to | 47 (12 attacks, 35 defences) |
| …the day hangs (a draw or a win on points, nobody driven off) | 27 (6 on attack, 21 on defence) |
| …great battles (80,000 men or more engaged — `WorldState.GREAT_BATTLE_THRESHOLD`) | 11 of 47 |
| …great battles in which the day hangs | 7 of 47 (4 on attack, 3 on defence) |
| Actions left when an attack's day hangs | 3, 3, 3, 1, 3, 3 (of 4) |

Tried on a copy of the world at every hanging day: after a morning won on points a renewed assault
broke the enemy 3 times in 3, whoever led it (about 6,400 of ours for 59,700 of his); after a drawn or
lost morning it never won; on defence a riposte never broke the attacker (0 of 21). "A capital at
stake" (31 of 47) and "two corps on a side" (30 of 47) were counted as other meanings of "key" and set
aside. So: the answer was set by the morning (the user's "obvious", confirmed); a free renewed assault
is a kill button unless the enemy has a say; most hanging days are on defence; and one battle in four
is great.

**The rulings** (the user's where quoted; the rest under the delegation, each one line to reverse):

| # | Ruling | Where |
|---|---|---|
| 1 | **A key battle is a great battle** — 80,000 men or more engaged, the game's own bar. Only a key battle is fought with points. | `battle_day.key_bar` |
| 2 | **The others stay simple** (the user's): one clash, and the table shows it exactly as it does today. Nothing about when the table opens changes. | no `day` on the payload |
| 3 | **A battle has its own points** (the user's). When a key battle's opening clash does not decide the day, each side holds points for the rest of it. The opening attack costs its action as before; nothing after it costs an action. | `battle_day.lending` |
| 4 | **The points come from the commander** (the user's): 2, or 3 at command 8 or more — `Marshal.RALLY_FAST_COMMAND`, the game's own bar (on the 1805 board Napoleon, Davout and the Archduke Charles). | `points_low`, `points_high` |
| 5 | **What a point buys.** One: the lead presses; another corps leads; a battery cannonades; a corps is brought up; the lead digs in. Two: the Guard, with NP-D1's two morale numbers (his lead −10 as it goes in; every corps of ours that fought −10 if it is thrown back). Nothing: to stand, to break off. Each is an order the game already has. | `battle_day.PRICES` |
| 6 | **In turns.** The side that did not open speaks first, then the other, each word resolved at once. Two silences in a row, both purses empty, or a side leaving the field: night falls. | `_spent` |
| 7 | **The enemy spends his at his discretion — "all that you can"** (the user's), **by the rule his AI already follows**: he strikes when his odds meet his temper's bar (`ATTACK_THRESHOLDS` 0.7 / 1.0 / 1.3, moved by `MOOD_VARIANCE`); short of it, a corps beside him that would lift him over it is brought up first; else the day he opened he breaks off, the day he did not he draws off when the last clash went against him and a road is open, digs in when he must stand, and otherwise stands. No new number. | `EnemyAI.the_days_word` |
| 8 | **The marshal's counsel is on his chip and he answers by the objection road as it stands**, seeded (WS-16): the same word from the same save draws the same temper. | `order_quotes._tactical_objection` |
| 9 | **"Leave it to him."** One chip hands the rest of the day to the lead, who spends what is left by his own temper (ruling 7's rule), with no objection to raise against himself. | `battle_day.leave_it` |
| 10 | **Defence** (my choice, as asked): a key battle a court opens against the player is played in turns as the player's turn opens — a notice, and the player answers first. Silence is standing: he plays what he has left when the turn ends, and does not strike that corps again in the phase that follows. | `night_falls`, `at_dawn`, `bars` |
| 11 | **The table.** Both purses stand on it as pips; his answer is told on the same table (a new showing only when it is a clash); while a day is open the verdict, the name plate and the seal give their room to the day's panel — the tableau does not grow. The attack card says beforehand when a battle will be great and the points its commander brings. | `battle_acts.gd`, `attack_quote` |
| 12 | **Variety**: the beats told most carry two or three variant lines chosen by the campaign's seed (today's line on `historical`, off the served road and with the seam down); named moments appear only when their condition holds. | `_Script.said`, `_named_moments` |
| 13 | **Where it exists**: campaigns the game server holds, as the battle's dice do. A world a test or a measuring harness builds for itself keeps the game it pins. | `campaign_is_served` |
| 14 | **The head's second question — yes** (a pursuit ability fires for any corps of the victor that fought) and **the support order's approach rule — IN**: both built in BA-4. | §15.7 |

**One narrowing of ruling 7, made while building and reported to the user.** The plan's words were "draws
off when [his odds] do not [meet his bar] and a road is open". Read literally against the code, a
cautious commander (bar 1.3) would abandon his ground after almost any undecided morning, even one he
had won on points — the engaged rule this was taken from (`_evaluate_marshal` P0) is written for two
corps in ONE province, where staying means being struck again. The built rule adds one condition: he
draws off only when **the last clash went against him on points**. Ahead or level, he stands (the AI's
own P3 response to a stronger neighbour: the defensive stance). One line in `the_days_word` to reverse.

**And what "a road" is — settled after the stop (§15.16).** The AI's retreat finder has a last,
desperate tier: with no friendly or neutral province free, it sends a corps onto the soil of a court it
is at war with. Taken as "a road", that sent Mack — at Ulm, with France all round him — INTO France
behind the Grande Armée, which is the opposite of the ruling's own example ("Mack, surrounded, stands
and is taken"). In a day of battle a road is his own soil, an ally's or a passable neutral's, with none
of our corps on it; with only at-war soil left he is surrounded and stands. The player is told which it
is before the order (the attack card) and on the table (`his_road`).

**A purse spent is not a wall.** With the day's points gone and the day still open, a further attack is
an ordinary order again at its ordinary price in actions — what the game allowed before BA-3. The
points are what the day gives free; they take nothing away.

**The session's shape** (the user approved the cut; sizing is information). **BA-3** — the day's points,
WS-16, NP-D1, BA2-X14's left half and BA2-X17: it moves nothing outside campaigns the server holds.
**BA-4 "the roads and the fog"** — every row that moves a measured world-line, with one re-read of the
gate: BA2-X2, BA2-X7, BA2-X10 with the approach rule, BA2-X12, BA2-X20 with the Gazette's news,
BA2-X21, the two ticked rules of §15.5.7 (the pursuit; the last hour's three quarters), and BA-3's
review fixes. Then Session H. This differs from §15.7's first table, which closed BA2-X2 and BA2-X7 in
BA-3: the hand-off of November 15 allowed two sessions, and this cut keeps every world-line mover with
one measure.

**Weighed and not built** (no control promises them; each is the user's to call): ordinary battles
settled by the marshals' own tempers; courts spending points against each other; stopping the enemy's
phase to ask the player; a standing instruction per corps.

### 15.15 BA-3 — THE STATE AT THE STOP (November 15, 2026; the record of the first pass — it landed by §15.16 and §15.17): built, measured, not yet landed

**BA-3 stopped at its own measure, as its plan said it would.** The plan the user approved carried one
rule: *"I stop and bring it to you if the band leaves 23–28 on `ALL`."* It did, by one province on one
seed. Nothing is committed. What follows is exactly what is in the working tree, what was verified,
what was not, and what waits for the user's word.

**The one measure** (`tools/_ba3_measure.py` → `tools/_ba3_band_2026_11_15.json`; the commanded France
script, 40 turns; France's provinces at the end, per seed — H the `historical` seed, A austerlitz,
M marengo; "days" = great battles whose day hung and was opened, summed over the three runs):

| Arm | What it is | H | A | M | days | words |
|---|---|---|---|---|---|---|
| `0` | every new seam down | **26** | **27** | **28** | 0 | 0 |
| `T` | the seeded temper and the varied telling alone | 26 | 26 | 28 | 0 | 0 |
| `S` | the points up, France says nothing (silence is standing) | 28 | 27 | 28 | 5 | 0 |
| `P` | every day pressed | 24 | 24 | 28 | 7 | 6 |
| `G` | the Guard where it stands, else pressed | 24 | 27 | 28 | 5 | 4 |
| `D` | dug in once, then standing | 28 | 27 | 27 | 4 | 3 |
| `B` | broken off / fallen back | 26 | 27 | 26 | 11 | 9 |
| `L` | left to the marshal | **29** | 28 | 25 | 11 | 9 |
| `ALL` | the policy `sense` (press ahead, leave behind, dig in level) | 28 | **22** | 23 | 7 | 8 |
| `E0` | `sense`, the enemy's purse shut | 28 | 24 | 28 | 7 | 7 |
| `N2` / `N3` | `sense`, every commander at 2 / at 3 points | 28 | 22 | 23 | 7 | 8 |
| `K50` | `sense`, the key bar at 50,000 | 28 | 24 | 23 | 9 | 12 |
| `NG` | `G` without the Guard's two morale numbers | 24 | 27 | 26 | 6 | 7 |

- **Arm `0` reproduces the record** (BA-1's 26 / 27 / 28), and **nothing outside a served campaign
  moved**: the keyed world probe is IDENTICAL to the commit before on jena and marengo (30 turns, 212
  keys a turn).
- **Where the band left 23–28:** `ALL` on A reads **22** (and so do `N2`, `N3`); `L` on H reads **29**.
- **Why `ALL` fell on austerlitz** (the day rows of that run): the policy made France **fall back
  twice in the campaign's opening** — Bernadotte before the Archduke Charles on turn 2; Masséna dug
  in on turn 3, was struck again, and fell back. A retreat gives up its province, and the opening
  cascades. With France silent on the same days (`S`) the reading is 27. The rules did what they say;
  the hand lost the ground.
- **What the arms show about the design.** No answer is best everywhere: leaving it to the marshal
  is best on H (29) and A (28) and worst on M (25); pressing every day is level-best only on M and
  *worse* than silence on the other two (24 / 24 against 28 / 27); silence never reads under 27. The
  enemy's say is worth 2 provinces on A and 5 on M under `sense` (`E0`). Two points or three made no
  difference in these runs (`N2`, `N3`). The bar at 50,000 opens two more days (`K50`). The Guard's
  two numbers are worth 2 provinces on M (`G` 28 against `NG` 26) and none elsewhere.
- **Days are rare, as asked**: 4 to 11 across three 40-turn campaigns.

**For the user to rule** (the stop's one question; my recommendation, then its alternatives):

1. **Recommended — read the gate on the script as it was written.** The commanded script is the
   deploy gate's fixed instrument; saying nothing on a day is that script unchanged. Its reading with
   the day's points in is `S`: **28 / 27 / 28, inside the band.** `sense` is a bot I added to the
   driver this session — its "fall back when behind" is what loses austerlitz's opening — and an
   active hand that can lose provinces is what a decision that matters looks like. Record `S` as the
   gate's reading and keep `ALL` and the rest as what a hand can do, per seed.
2. Change `sense` so that a lead behind on a DEFENDED day digs in instead of falling back, and
   measure again. That is tuning the instrument until the number fits; I did not do it on my own.
3. Change a rule or a number (the prices, the purses, the bar, the enemy's rule). None is indicated by
   these arms; each is one seam.

**Built and verified in the working tree** (uncommitted):

- **The day** — `backend/game_logic/battle_day.py` (new), hooks in `combat_executor.py`
  (`after_the_battle` at stage 18's head, `guard_shock` at stage 13's, `day_word` on the script's
  facts), `backend/main.py` (the ONE door `_execute_through_the_day`, the objection's
  `_answer_through_the_day`, `GET /battle_day`, `POST /battle_day/word`, the region quotes' `day`),
  `enemy_ai.py` (`the_days_word`; the night's bar read into the pair brake), `turn_manager.py` (night
  and dawn), `world_state.py` (the store, saved only when it holds something),
  `order_quotes.attack_quote` (the great-battle forecast), `notifications.py` (`battle_day_awaits`).
  Every rule was **played by hand through the server** before the measure: a small battle (nothing
  new, one action); a great battle that hangs with each of his answers (strikes back, digs in, draws
  off, stands); a press, a dig-in, standing, breaking off, falling back; an objection raised by a word
  and answered on the day's account; the Guard and its shock; "Leave it to him"; night at the turn's
  end; a defended day at dawn with its notice. Two defects found by that play were fixed before the
  measure (a day wrongly ended when a won clash carried our corps onto the field; a deciding clash
  left no line). **`tests/test_ba3_the_rounds.py`: 77 tests, green.**
- **WS-16, the seeded temper** — `campaign_variance.temper_rng`; twelve kinds at fourteen sites (the
  row said two in `vassal.py`; the sweep found three). **`tests/test_ws16_the_same_order_draws_the_
  same_temper.py`: 44 tests, green.**
- **NP-D1** — the Guard's two morale numbers, behind `the_guards_numbers_bite()`.
- **The varied telling** — `battle_script._Script.said` (seventeen beat kinds with two or three lines),
  `_named_moments` (six), the `word` beat; today's text byte for byte on the `historical` seed, off
  the served road and with the seam down.
- **BA2-X14's left half** — `_plan` names a gunner once (the pin is a plain test now).
- **The client** — the day's panel in `battle_acts.gd` (pips, the lines told, the chips; it takes the
  verdict's, the name plate's and the seal's room and gives it back; `TRAY_H` stays 744), ONE line in
  the host (`signal word_given`; its `_acts.` hooks still five), `main.gd` (the word's send road, his
  clash shown after ours, the notice's "Take the field"), `region_panel.gd`, `enemy_phase_dialog.gd`,
  `order_confirm_card.gd`, `api_client.gd`, `notification_bar.gd`. **Verified headless only**: the
  parse harness EXIT=0; a headless smoke of the real tableau scene with a day injected (the panel at
  rest, the chrome hidden and back, one press one word, a dim chip silent).
- **The driver** — `--rounds none|press|guard|dig_in|break_off|leave|sense` (absent unless passed), a
  `round` row and a `rounds` block in the digest; `tools/_ba3_measure.py`.
- **The gate's measurement on record** — `docs/audits/ba3/hinge_probe_2026_11_15.json` (the probes'
  own rows; §15.14's table is counted again from it by a pin).
- **Found by the suite, fixed (BA3-X1):** the new world-line reached two old lines that print a
  roster key — a cavalry charge's refusal ("Attack ArchdukeJohn at …") and the Habsburg Resolve line
  at four sites; both now name the corps as the player reads him.
- **Re-pointed on purpose:** `tests/test_sf_page_the_front_page_of_the_peace.py` holds the day's seam
  down with the others for its Step 7 archive arm (CMD-H re-times from turn 2);
  `tests/test_ws11_…` no longer holds the mood level (WS-16 seeds it);
  `tests/test_serialization_enforcement.py`'s populated world carries a day;
  `tests/test_cn4_the_chip_honesty_census.py` reviews the day's three chip urls;
  `tests/test_the_plan_homes_every_row.py` knows BA-4.

**Three small changes were made AFTER the measure** — none on the driver's road, none moving a
number: `GET /battle_day` lets him answer a day opened by a road that carried no answer (an
interrupt's answer, a charge — `battle_day.caught_up`; the client's `@refresh` relies on it), and
BA3-X1's two display fixes.

**NOT done — each heads the session that resumes BA-3:**

1. **The full test suite has not been run.** Known red in the tree: the walk record's freeze pins
   (`test_the_record_names_what_it_shot`, `test_the_client_it_was_shot_from_is_the_client_committed`,
   and `tests/test_ba1_…`'s source-set pin — the walk of record must be re-shot), and the pin on
   `tools/godot_parse_report.json` if it reads the committed hash. Other driven arms that play the
   `historical` campaign through the server may need the day's seam held down as the Step 7 page
   did — the full run will name them.
2. **The staged scenes and the walk.** No day scene is staged (`tools/ba1_stage_battles.py`), the walk
   has no claim on the panel (`tools/ba1_acts_walk.py`), no switch-off case, and the scene `the_guns`
   (changed by BA2-X14's fix) is not re-recorded. The brief for this work is written and kept:
   `docs/audits/ba3/walk_brief.md`.
3. **The windowed walk of record, the live-client walk, the IQ-10 captures at the five sizes and the
   four instruments.** No control of the day has been pressed in the real client against a real
   server. `main.gd`'s 287 new lines are parse-checked and unread by me line for line.
4. **BA2-X17's second pin** (every source on record is the source committed) stays a strict xfail
   until the walk is re-shot; the source list itself is whole.
5. **A re-runnable hinge probe** (`tools/hinge_probe.py`): the probes ran as inline scripts; their
   rows are kept, the tool is not.
6. **The records of a landing** — `STATUS.md`'s landed entry, `ROADMAP.md`, `PRE_DEPLOY_PLAN.md` and
   `CLAUDE.md` say "built, stopped at its measure", not "landed".
7. **The session's review**, as every session of this row has had.

**Left with the user, beside the measure** (each one line to reverse): the narrowing of ruling 7 (he
draws off only when the last clash went against him — §15.14); a purse spent is not a wall; the field
is where the last clash was fought; with one point left the sovereign's attack is an ordinary order
without the Guard's numbers; a price of nothing is printed "· 0" on a chip; the pips show two slots,
or three when either purse holds three (the wire does not carry a purse's starting size).

### 15.16 The ruling on the measure — "do whatever is best not easiest" (November 15, 2026, authoritative)

**The user's word** on §15.15's one question: **"do whatever is best not easiest"**. The easiest answer was
the one I had recommended — read the gate on the silent script (`S`: 28 / 27 / 28) and move on. It is not
the best one, for two reasons the stop itself exposed:

1. **One seed is not evidence.** On austerlitz the arms `B` (always fall back) and `ALL` (`sense`) differ
   by a single extra clash on turn 3 — and by five provinces on turn 40 (27 against 22). A commanded
   campaign is chaotic in that sense: a reading that crosses a line by one province on one seed says
   nothing about whether the day's points help or hurt France. The user's own rule is "report seeded
   outcomes per seed", and the AI phase's acceptance run was promoted to an N-seed sweep for exactly
   this reason.
2. **The silent script does not measure the feature as it is played.** It measures the deploy gate's
   instrument (which says nothing on a day), not what a hand does to the campaign.

**So the measure is re-read as a sweep of DELTAS, with its rule written here BEFORE it is run.**

- **Seeds:** the three commanded ones (historical, austerlitz, marengo) and five more named seeds on the
  same commanded script — jena, wagram, lodi, eylau, friedland. Eight.
- **Arms:** `0` (every new seam down), `T` (the day's seam down; the seeded temper and the varied telling
  on), `S` (silent), `L` (left to the marshal), `P` (pressed), `D` (dug in), `B` (broken off), `G` (the
  Guard), `ALL` (`sense`).
- **The reading:** for every arm X and seed, Δ = France's provinces under X − under `T` (the day's own
  effect; `T` − `0` is the seeded temper's). Per arm: every Δ, their mean, their range.
- **The rule (pre-registered):**
  - **The gate's instrument holds** if arm `0` again reads 26 / 27 / 28 on the commanded seeds and the
    silent script's mean Δ lies within ±1.5 provinces: a France that never uses the day is not
    systematically shifted by its existing.
  - **The hand is healthy** if no way of playing a day is a systematic gift or a systematic trap: no arm's
    mean Δ is +3 or more, or −3 or less (more than half the 23–28 band's width, on average, over eight
    campaigns), **and** no single arm is the best on six or more of the eight seeds (a dominant answer
    is the user's first weakness — "the choice may be obvious" — come back).
  - If the hand is NOT healthy, the mechanism is read from the runs' own rows and the **rule** is changed
    behind its seam — never the bot until the number fits — and the sweep is run again.
  - `sense` is a bot of this session. Whatever it reads is reported per seed; it is not the gate.
- **What the deploy gate reads from here on:** the commanded arms as `score_run` runs them — no `--rounds`
  passed, so silent on a day — on the three commanded seeds.

**The sweep** (`tools/_ba3_measure.py --arms 0,T,S,L,P,D,B,G,ALL --seeds jena,wagram,lodi,eylau,friedland`
→ `tools/_ba3_sweep_2026_11_15.json`; 72 runs of forty turns; France's provinces at the end). It was taken
THREE times and this is the third: the first was stopped part-way when the muster's question was found to
end a day (row 1 below); the second ran whole on the tree before the road fix (row 3) and passed the rule
too (means 0.00 to +1.12); this one is the tree as it stands.

| Arm | H | A | M | jena | wagram | lodi | eylau | friedland | mean Δ vs `T` | without jena | range |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `0` every new seam down | 26 | 27 | 28 | 19 | 26 | 25 | 25 | 28 | −0.50 | −0.57 | −3 … +1 |
| `T` the day's seam down | 26 | 26 | 28 | 19 | 26 | 28 | 27 | 28 | 0 | 0 | — |
| `S` silent | 28 | 27 | 27 | 27 | 23 | 28 | 26 | 27 | **+0.62** | −0.43 | −3 … +8 |
| `L` left to the marshal | 29 | 28 | 25 | 26 | 25 | 28 | 27 | 28 | +1.00 | +0.14 | −3 … +7 |
| `P` pressed | 27 | 27 | 26 | 28 | 27 | 28 | 27 | 28 | +1.25 | +0.14 | −2 … +9 |
| `D` dug in | 28 | 27 | 28 | 25 | 26 | 23 | 27 | 25 | +0.12 | −0.71 | −5 … +6 |
| `B` broken off | 26 | 27 | 23 | 28 | 27 | 28 | 27 | 28 | +0.75 | −0.43 | −5 … +9 |
| `G` the Guard | 27 | 27 | 28 | 24 | 29 | 27 | 28 | 27 | +1.12 | +0.57 | −1 … +5 |
| `ALL` `sense` | 28 | 22 | 25 | 25 | 27 | 28 | 27 | 26 | 0.00 | −0.86 | −4 … +6 |

- **The instrument holds.** Arm `0` reads 26 / 27 / 28 again on the commanded seeds; the silent script's
  mean Δ is +0.62 (−0.43 without jena), inside ±1.5.
- **The hand is healthy.** No arm's mean Δ reaches ±3 — the largest is +1.25, the smallest 0.00 (with jena
  out: +0.57 to −0.86). No arm is best on six seeds of eight: the most is `L`, best or level-best on four
  and alone on two; `G` is alone on two; no other arm is alone on any. Every way of playing a day wins
  somewhere and loses somewhere.
- **jena is one outlier and not a defect:** with the day's seam down France holds 27–28 provinces to turn
  33 and loses nine in the last seven turns (19); every arm with the day keeps 24–28. One campaign's late
  collapse, left on another road from turn 5 — a seeded path, not a law. It is in every mean above and is
  also shown taken out.
- **The seeded temper alone** (`T` against `0`) moves three rolled seeds (−1, +3, +2) and none of the
  others: +0.5 in the mean.
- **Days are rare, as asked:** the driver met 18 to 25 open days across the eight campaigns — two or three
  in a forty-turn campaign (more than before the road fix: a surrounded corps now stands, and its day stays
  open). The bar is one function (`battle_day.key_bar`); arm `K50` below says what 50,000 does.

**THE RULING (under the user's delegation, on the rule written above before the data):** the deploy gate
reads the commanded arms as `score_run` runs them — silent on a day — and they read **28 / 27 / 27**,
inside 23–28. The day's points shift France by about one province or less in the mean whichever way a day
is played, and no answer dominates. The two readings that leave the band on single seeds (`ALL` 22 on
austerlitz, `L` 29 on historical) are seeded paths: `B`, which falls back on every day, reads 27 on the
seed where `sense` reads 22. No rule and no number is changed for the measure. `sense` stays as it is, a bot
of the driver, reported per seed and not the gate.

**The exploratory arms, on the same tree** (`tools/_ba3_arms_2026_11_15.json`; the three commanded seeds;
the common arms read exactly as in the sweep):

| Arm | What it is | H | A | M | days |
|---|---|---|---|---|---|
| `ALL` | `sense` | 28 | 22 | 25 | 7 |
| `E0` | `sense`, the enemy's purse shut | 28 | 24 | 28 | 7 |
| `N2` / `N3` | `sense`, every commander at 2 / at 3 points | 28 | 22 | 25 | 7 |
| `K50` | `sense`, the key bar at 50,000 | 28 | 24 | 25 | 12 |
| `G` | the Guard where it stands | 27 | 27 | 28 | 11 |
| `NG` | `G` without the Guard's two morale numbers | 27 | 27 | 28 | 13 |

His say is worth two provinces on austerlitz and three on marengo against a hand that plays `sense` (`E0`);
two points or three made no difference in these campaigns (a day seldom lasts long enough to spend a third);
the bar at 50,000 opens five more days in three campaigns (12 against 7); the Guard's two numbers moved no
province here (`G` and `NG` read alike), though they move the day itself (`NG` fights two more).
`tools/_ba3_band_2026_11_15.json` (§15.15's table) is the measure AT THE STOP, taken before the fixes
below; it is kept as that record and is superseded by these two.

**What "best" found after the stop** — thirty finds, none known when §15.15 was written; each was found
by doing the work the stop had left undone (reading the code whole, playing the real board, running the
suite, looking at the frames, pressing the real client against a real server), and each is fixed, with its
pin (row 30 files one for BA-4). Rows 1 to 12 were fixed before the sweep above was taken. Rows 13 to 30 came after it: each is the
table's dress, a client road, or a server fix on a road the measured arms do not take — and the commanded
arms were read again on the final backend: every new seam down 26 / 27 / 28, the gate's reading
28 / 27 / 27, the fall-back arm 26 / 27 / 23, each as in the sweep; the keyed world probe identical on
jena and marengo.

| # | Found by | What was wrong | Now |
|---|---|---|---|
| 1 | playing a word at bad odds through the server | The muster's "Commit the Attack?" — a marshal's own question, answered on another road — **ended the day** (a lead with a pending question read as "not standing") and the confirmed attack then **cost a campaign action**. | A question parks the word, whatever road answers it (`_asked`, `pending_word(marshal=)`, `main._interrupt_through_the_day` at the endpoint and at the typed route); the answer is the word and costs points; Cancel costs nothing; a question never ends a day (`_under_arms`). |
| 2 | reading for concurrency | `GET /battle_day` quotes its chips with the word's lend on the pool and was outside the server's state lock: crossing a command, it could leave the lend there — **free actions for good**. | In `_LOCKED_READS` beside the two readings WS-6 put there; the pool is as it was after every read (pinned). |
| 3 | the full suite, then the real board | **"A road" included the flight onto enemy soil.** The AI's retreat finder ends in a desperate tier — the soil of a court it is at war with — and at Ulm that sent Mack INTO France behind the Grande Armée ("Mack draws off toward Rhineland"): the opposite of the ruling's own example, and the reason the opening battle never left the player a day to play. | In a day of battle a road is his own soil, an ally's or a passable neutral's (`desperate=False`). At Ulm Mack is surrounded: he digs in, the day stays open with thirteen chips, and the Guard takes him. The attack card says "No road lies open behind him" before the order. |
| 4 | Golden Rule 5 | The Guard was the player's alone, and a sovereign "left to it" could press for one point where the player's own chip asked two. | The Guard is any sovereign's renewed assault, on either side, at one price with the same two numbers (`strike_price`). |
| 5 | reading `word_given` | A parked word was tied to ANY question standing on the board: another marshal's objection would have parked it, and that objection's answer would then have been charged to the day. | Tied to the word's own marshal — his objection on either road, or his own interrupt (`questioner`). |
| 6 | reading the roads | A day opened by an attack that reaches the executor past the command road (an interrupt's answer, a charge) waited for him with nothing said until night. | `GET /battle_day` lets him answer first (`caught_up`); the client asks once for such a table. |
| 7 | the wire | The pips had no honest size (the client guessed two or three), and the table said nothing of the man across it. | `ours_of` / `theirs_of`; `his_temper` and `his_road` — never his odds, his bar or his mood. |
| 8 | "Leave it to him" | A town taken by the lead's own strike asked "plunder or secure" on a result nobody forwarded: the next order would have been refused for a question the player never saw. | The word's answer carries the clash's own combat fields (the allowlist the interrupt roads use); the endpoint is non-draining. |
| 9 | an independent reader of the client, line by line | Seven P2s in `main.gd` — a settled-frame flag leaking onto the next battle; his clash queued behind a table whose chips were already live; the table raised over ANY open modal; Esc during a word in flight handing back the command line; a refused word shown nowhere; the chip row clipping; a replayed table offering stale chips — and a dozen smaller ones. | All fixed by the panel's builder against a written list; the panel is two rows now (the words that spend, which may scroll; the exits, always in reach). |
| 10 | the walk's first run | The told lines' box was sized for a 22 px line under a 27 px font (the third line cut), and thirteen chips did not fit. | Sized from the font; see 9. |
| 11 | the code reader's own report | The day's stash function had been RENAMED so that the census of stashers would not count it. | Named `_stash_battle_day` again; the census counts ten, on purpose. |
| 12 | the suite | Three campaign pins that play the `historical` campaign through the server moved with the day (a standing order's march, a charge's aftermath, a driven arm's report). | Each holds the day's seam down beside the seams it already held, with its reason; the day's own behaviour is pinned in `tests/test_ba3_the_rounds.py`. |
| 13 | the lead's own look at the walk of record's frames | The walk was green and the panel was not good enough: at Ulm (thirteen chips) the second row of orders was **sliced by the tray's edge** and the Guard — the day's most dramatic word — was last and half hidden; the orders stood in the server's incidental order. A claim that a box "scrolls rather than clips" had passed on a row cut in half. | One order for every surface, set on the server (`_chip_rank`: the lead's press, the Guard, the dig-in, then the others by kind, the exits and "Leave it to him" last). The panel is laid in whole rows: the lead's own words; the corps lists compacted to names under one label ("Another leads · 1:"); the exits on the floor of the tray. The shelf of corps that did not come yields its room when the panel needs it. The walk now claims that NOTHING is sliced. |
| 14 | the same look | The headline read **"A FIELD OF LEGEND IS WON"** over a day that still hung: a morning won on points is not a field won. | The block carries `banner` — "The day hangs" while open, "Night falls" / "<Enemy> draws off" / … when it closes otherwise than by a clash — and the table's headline follows it; a clash that decides the day keeps its own verdict. |
| 15 | the same look | On a day the enemy opened, the lead's own attack read "presses". | "<Lead> strikes back", on the chip and in the telling. |
| 16 | re-staging before the walk of record | The stager died half-way when its output was redirected (a scene's line holds "−"; the console's code page): a walk of record would have been shot on a stage that had not finished. | `main()` sets its output's encoding as its sibling tools do. |
| 17 | the staged defended day | **"Fall back — not in danger — no retreat needed"** under a day the enemy had opened. Two causes: the scene's board, placed by hand, kept the fog of the corps' old stations (the game offers a defended day at DAWN, after the fog is read again); and the retreat's fog-honest danger test (`state_probe._in_visible_danger`, CF-6) counts only a threatening enemy we SEE and did not know a day's own enemy. In a real campaign the attacker stands on or beside the lead's province and is in sight — every defended day of the sweep's fall-back arm fell back — so the gap was live only for an attacker the fog has closed over (a horseman's reach is two provinces). | The enemy of an open day counts as seen for its lead's retreat (`_the_days_enemy_of`): the day's block already names him, so nothing is given away. The stage reads the fog again as the game does at dawn. The rule itself is not loosened — with no day against him the same hidden corps leaves a retreat dim (pinned both ways). |
| 18 | **the real client**, a word that raised the muster's question | **The action counter read 6 of 4, then 5 of 4.** The executor writes `action_summary` with the word's lend still on the pool, and `settle` rewrote only `action_info`. The server's own pool was right throughout; the client's counter is that field. Every in-process check had read the pool and `action_info` and passed. | `battle_day.settle` rewrites `action_summary` once the lend is taken back; every `actions_remaining` a word's answer carries, wherever it sits, is pinned to the pool on all three roads (the plain word, the muster's question and its answer, the objection and its answer). |
| 19 | **the real client**, a day the enemy opened | **The table that rises by itself after the enemy phase's list carried both purses and no word to give.** A great battle is `dramatic`, so the client raises its tableau when the list is left — and that tableau's block was the one written at the battle, before the day was offered (`at_dawn` offered the day and posted the notice, and left the tableaux as they were). The player had to close the table and find the notice. The commonest day in a campaign is this one; the staged scene had been fought through the executor and showed its chips. | `battle_day.dawn_on_the_tableaux` (from `turn_manager._the_days_dawn`): each tableau the phase's telling carries for a day — the action's and its events' — reads the day as it stands at dawn, chips and all; a day that did not live to the dawn leaves no block on its earlier clash. Pinned through the server and on the function. |
| 20 | **the real client** at 1920×1080 | The panel came in at the gavel, 0.7 seconds before the table is final: for that time the "click anywhere to skip" hint lay under the exits row and Replay and Close were not there. And the exits row sat ON the tray's inner gilt line. The staged walk's end shot waits 2.8 seconds and had seen neither. | The verdict's room is cleared at the gavel and the panel comes in the moment the table is final, with the buttons; the exits row is centred on Replay and Close, clear of the frame at text sizes 1.0, 1.15 and 1.3. |
| 21 | **the real client**, our clash followed by his | The table rested on "Archduke Charles strikes back." and nothing said his clash was next: the player had to press Close to learn that Close led to it (the live walk waited a minute for chips that ride only HIS table). | On a table his clash follows, the primary button reads **"His answer ▸"**, and after 2.5 seconds at rest the table goes on by itself — the button's own road (not under Reduce Motion; Replay cancels the wait). |
| 22 | reading the sequencer against the live frames | Over a day's banner the hidden verdict was still "written": the quill's loop ran, and a fanfare (a morning won on points — Ulm) or a bell (lost on points) played under "THE DAY HANGS" — the sound of the headline row 14 corrected. | No verdict is typed while the day's panel stands; a day its clash DECIDED builds no panel and keeps its verdict, its plate and its cues. |
| 23 | the lead's second look at the frames | Three things a first-time player could not read off the table: the squares were never called points; the clash's own verdict — won on points, lost on points, drawn: what the choice turns on — had gone with the headline into a hover; and there was no room for a third group of chips (a battery in reach) without sending the last word told to a hover. | The head line begins **"The day's points — "** (the first words dropped when it does not fit); the sub-banner under the day's banner is the block's `morning`, whole; when the rows do not fit the groups are laid inline in a box as wide as the panel BEFORE the told line gives way (scene `day_guns`: sixteen chips, the told line on the table at the player's default text size). |
| 24 | reading the client's dawn road | The enemy phase list's "View the field" stripped a day's chips (the client held no block for a day the phase had opened), and a stale tableau of an open day had nothing to fetch them with. | The dawn's tableaux are remembered with their block; a table of an open day that awaits OUR word and carries no chips asks the server once, as a table that awaits his already did. |
| 25 | reading the night | When night fell after his last clash, that clash's tableau — which the client raises like any great battle — still said the day hung, with both purses and no word to give. | The night's close is written on his last clash's tableau ("NIGHT FALLS", the day's lines); an earlier night clash is told as the battle it was. |
| 26 | the game's own end-turn rule (FA-16: what a turn's end decides for the player is told before the turn goes) | Ending the turn settles an open day by our silence — he spends what he has left and night falls — and the end-turn gate, which stops once for unanswered envoys, petitions, letters and a cornered marshal's last stand, said nothing: close the table at Ulm to look at the map, press End Turn, and the day and its points were gone unannounced. | Every response lists the days that await our word (`pending_battle_days`, beside the last stands); the gate names each — "The day at Swabia still hangs — Ney holds 2 points. End the turn and Mack answers alone." — and puts a "Take the field" chip under it. |
| 27 | the size captures (nineteen surfaces at five sizes) and the lead's look at them | The enemy phase's list badged a day that still hung by its clash — **"Mack attacks Ney — DEFEAT"** over "the day awaits your word": the list's own version of row 14. Its quiet badge (the STALEMATE fill, older than the session) read 4.17:1 against a floor of 4.5. And at 5120×1440 the province panel's first view ended above the day's block, which stood where the ATTACK rows stand. | A row whose tableau carries a day with a banner is badged by that banner ("THE DAY HANGS", "NIGHT FALLS") on a solid quiet fill that reads 4.97:1 (`Utils.COLOR_BADGE_QUIET_SOLID`, the enemy phase's badges only); the day's block is the province panel's first section. |
| 28 | **the real client**, "Fall back" with a great court's letter waiting | The lead fell back, Hardenberg's letter came up — and "MASSENA FALLS BACK" never did. An incoming letter rides an order's answer and is routed first; its "Not Now" handed the command line back by itself (the one handler the client's one-tail conversion had missed), so the table the same answer had stashed waited for the NEXT order. Older than row BA, and true of any battle's tableau (BA3-X4). | "Not Now" ends in the one tail; the census names the handler; the live walk sets the letter aside and reads the closing table. |
| 29 | the record itself | The walk of record kept none of the day's frames, and no test in the suite drove the panel (BA-1's and BA-2's tableaux each have one). | Eight kept frames (`BA1_34` … `BA1_41`); `tests/test_ba3_the_days_panel.py` in the engine lane drives the day scenes headless and pins the walk's and the live walks' records. |
| 30 | the full suite on the final tree | Two older pins that fight the 1805 opening through the server on the `historical` seed — whose battle dice are the module's — were green in one full run and red in the next: where Ulm's day hangs, the script's next attack on Mack, and "Soult, support Ney", are words of that day and take no action. And they showed what the surfaces OUTSIDE the day's own chips say while a day is open: the attack card still read "1 action" and "A great battle — Ney commands the day: 2 points" over a day whose purse stood at one. | Each pin holds the day's seam down, with its reason. The card forecasts no new day while one is open. **What a quote says of a word's PRICE on those surfaces — the card, the plan's rows, the relay's note, the province's ordinary attack row, the readback — is filed as BA3-X5 for BA-4**, with a strict-xfail pin: the day's own chips say the truth, the quote errs in the player's favour, and the fix is one source across five surfaces — a slice, not a patch. |

The mechanic is also in the game's own help now (`codex_terms.gd`: "The day's points", "Great battle", "The
Guard"), written from the code.

### 15.17 LANDING RECORD — BA-3 "the day's points" BUILT November 15–16, 2026 (authoritative)

One session, one commit: the gate (§15.14), the build, the stop at its own measure (§15.15), the user's "do
whatever is best not easiest" and the finish that followed (§15.16). The rules are in `SYSTEMS_REFERENCE.md`
§221; this is what landed and how it was verified.

#### What a player gets

- **A small battle is one clash, told as before.** Nothing about when the table opens changed.
- **A great battle that does not decide the day stays open.** Both commanders hold points — 2, or 3 at command
  8 or more — shown as squares under "The day's points". The sides speak in turns, the one that did not open
  first. A word is an order the game already has: the lead presses, another corps leads, the guns, a corps is
  brought up, the lead digs in (one point each); the Guard (two, with its two morale numbers); to stand, to
  break off or fall back, and "Leave it to him" cost nothing. A word costs points and never an action. The
  enemy answers at once by the rule his AI already follows — he strikes when his odds meet his temper's bar,
  draws off by a road to his rear when the last clash went against him, digs in or stands when none is open.
  Two silences, both purses spent, or a side leaving: night falls.
- **The table tells the day.** The headline is the day's own ("THE DAY HANGS", "NIGHT FALLS", "MACK DRAWS
  OFF"); under it, how the last clash went ("The last clash: won on points — …"); the last word told; the
  lead's own words, the other corps under one label each, the exits level with Replay and Close. When his
  clash follows ours the button reads "His answer ▸" and the table goes on by itself.
- **On defence** the morning's battle rises on the table when the enemy's phase is left, with the day's chips
  on it; a notice on the rail ("Take the field") and the province's panel (the day's block first) lead back to
  it. **Before the order** the attack card says "A great battle — Ney commands the day: 2 points" and whether a
  road lies open behind the enemy. **Before the turn ends** the end-turn gate names a day that still awaits a
  word.
- **Ulm plays as history:** Mack, surrounded, has no road; he digs in, the day stays open, and the Guard takes
  him.

#### Verification (the tree BEFORE the session's review, November 16, 2026 — the final tree's figures are §15.18's)

- **Played by hand through the game server** before any long run, and again after each fix: a small battle; a
  great battle whose day hangs with each of his answers; a word and the clash after it; the same save, the
  same day and the same temper; an objection and the muster's question raised by a word, answered each way;
  the Guard thrown back; "Leave it to him"; a defended day at dawn; silence, his night strike and no second
  strike after it; an old save loaded.
- **Pressed in the real client against a real server** (`tools/ba3_mode_c_walk.py`, four boards on a
  sandboxed backend; record and frames `docs/audits/ba3_mode_c_2026_11_15/`): `ulm` — the real opening: the attack card's Send, the panel at rest, the Guard for two points and no action, Mack taken (4 of 4 steps); `massena` — the province panel's day block and its chip, the lead's press through the muster's question, "His answer ▸" and the table going on by itself, "Leave it to Masséna" (9 of 9); `defence` — End Turn, the enemy phase's list (its badge "THE DAY HANGS", "View the field" with the chips), the morning's table rising with its chips, "digs in" through the objection, his clash, the end-turn gate's sentence and its chip, the notice's "Take the field", "Fall back" with a great court's letter interposing, and an End Turn with no day open (14 of 14); `typed` — a word typed into the command line, the day told in the log after the order's own reply, a chip pressed in the log (5 of 5). 32 of 32 steps, 0 script errors, 21 frames kept. Its runs are what
  found rows 18 to 21 and 28 of §15.16.
- **The measure** (§15.16): eight seeds by nine arms; the gate's reading 28 / 27 / 27; arm 0 26 / 27 / 28. On
  the final backend the commanded arms were read once more — every new seam down 26 / 27 / 28, the gate's reading 28 / 27 / 27 — and the keyed world probe is IDENTICAL
  to the commit before on jena and marengo (30 ambient turns, 212 keys a turn): nothing outside a campaign
  the server holds moved.
- **The walk of record** (`docs/audits/ba1_client/walk_record.json`; windowed, at the scenes' own speed, at
  the player's default text size): 129 of 129 shots on 33 staged scenes (eleven of them days) and BA-1's own four-a-side payload, 0 script errors, every claim holds; 41 frames kept (`BA1_01` … `BA1_41`; the day's are `BA1_34` on). Each claim on the day's panel was watched failing with its fix
  switched off (`tools/ba2_switch_off.py`: 44 cases, 44 caught).
- **The instruments** (`docs/audits/uxr0/{readability,contrast}_ba3_days_points_2026_11_15.json`,
  `docs/audits/uxr3/{fit,frame_census}_ba3_days_points_2026_11_15.json`): nineteen surfaces — thirteen tableaux (ten staged days at rest, one mid-act, the dawn's table and the night's from real end-turn responses), the province panel, the attack card, the enemy phase's list at dawn and after a night, the rail's notice and the end-turn gate — at the five physical sizes with the Interface Scale each derives, at the player's default text size: readability 2,134 rows, RED 0, P1 0; contrast 2,121 measured, 0 under the floor (the first pass read the enemy phase's quiet badge at 4.17:1 — row 27 of §15.16); fit 19 of 19 at 1920×1080, 3840×2160 and 5120×1440; the frame census 95 frames, no cut line, no grip or tick overlap, the verdict's room 9.6 px at the least.
- **The parse harness:** 98 scripts and 17 scenes, no error.
- **Tests:** `tests/test_ba3_the_rounds.py` (110 tests; a served campaign through `TestClient`),
  `tests/test_ba3_the_days_panel.py` (20 tests; the day scenes driven headless in the engine lane, the walk's
  and the live walks' records), `tests/test_ws16_the_same_order_draws_the_same_temper.py` (44 tests).
- **The full suite on the final tree:** 41,172 passed, 27 skipped, 27 xfailed, none failed, in 9:35 at ten workers (the hook's own line: `-n 10 --dist loadgroup`). It is the fourth full run of the finish — the third is what found row 30 of §15.16 — and after it only this record's own figures were written; the pins that read the records were run again.
- **The plan's probe tool was not built** (§15.15's item 5, `tools/hinge_probe.py`). The gate's three
  probes ran as inline scripts on the commit before BA-3 and read that commit's world-line (on this tree:
  the one with every new seam down). Their rows are the record
  (`docs/audits/ba3/hinge_probe_2026_11_15.json`) and §15.14's table is counted again from them by a pin.
  What a day's words do on the mechanic as built is read by the driver's own `rounds` block and the sweep
  (`tools/_ba3_measure.py`), which is the instrument BA-4's one re-read uses. A tool of the session; nothing
  a player sees.
- **Not measured here:** the readers' blind marks (a day of battle is motion and choice; the user's own play
  is the reading), and Text size 150 % and over (BA1-X4, open for Session H). At text size 1.3 the day's
  sub-banner ends about 3 px into the dice's room, and BA-2's board lays three corps a side as the file
  (BA3-X2, BA-4).

#### Left with the user (each one line to reverse)

- **The deploy gate's reading:** the commanded arms as `score_run` runs them — silent on a day. The bot
  `sense` is the driver's and is reported per seed.
- **He draws off only when the last clash went against him, and only by a road to his rear** — his own soil,
  an ally's or a passable neutral's, never the soil of a court he is at war with.
- **A purse spent is not a wall:** a further attack is an ordinary order again, at its ordinary price.
- **The field is where the last clash was fought.**
- **The Guard is any sovereign's renewed assault and nothing else**, on either side, at two points; with one
  point left the sovereign's attack is an ordinary order without the Guard's numbers.
- **The table goes on to his clash by itself** after 2.5 seconds at rest (not under Reduce Motion).
- **The end-turn gate stops once** for a day that still awaits a word.
- **A day's later clashes are battles of their own in the record** — "The Great Second Battle of Swabia" on
  the plate and in the log, as any second attack in a turn has always been named.

#### Recommended, not built (the user's to rule; none is promised by a control)

- **A first-open line for the day's panel** — the game's own rule (S14d, `first_open.py`) names a mechanic the
  first time its action screen opens; the day's panel is not yet one of its screens.
- **Digits for the day's chips** (they are mouse-only, so that Esc, Enter and Space keep their meaning; who
  owns the bare digits is WS-10's ruling).
- **A line in the morning's telling for a night that fell with no clash** (the end-turn gate says it
  beforehand; BA2-X20's Gazette news is its natural home).
- **One name for a day of battle** in the record, its clashes told as its phases.
- **The key bar:** at 50,000 men the three commanded campaigns open twelve days against seven.
- **Weighed at the gate and not built** (§15.14): ordinary battles settled by the marshals' own tempers;
  courts spending points against each other; stopping the enemy's phase to ask; a standing instruction per
  corps.

#### Owned by the session after this one

BA-4 "the roads and the fog" (§15.7): BA2-X2, BA2-X7, BA2-X10 with the support order's approach rule, BA2-X12,
BA2-X20 with the Gazette's news, BA2-X21, §15.5.7's two rules, BA3-X2 and BA3-X5 (a word's price on the
surfaces outside the day's own chips), and the four rows the session's review filed (§15.18: BA3-X13 to
BA3-X16). The review itself is done. Then Session H.

### 15.18 THE REVIEW — BA-3's one review (November 16, 2026, authoritative)

Run BEFORE the commit. The user had passed over the question of the commit and said "keep goin"; a review
fleet over an uncommitted tree is the hazard this project has met before (a reader's `git stash`), so the
whole change was first written to a restorable bundle outside the repository, a frozen copy was rebuilt from
that bundle alone and proved identical to the working tree file for file (153 of 153), and the six readers
were given the copy and nothing else: no git, no engine, no server, the checkout off limits. Six lanes — the
day's rules and its store; the fog and the honesty of the telling; the seeded temper; the client (read, not
run); the enemy's side and the other roads; the pins and the records. **Twenty-five distinct findings. Nothing
crashes, corrupts a save or soft-locks; one is a fog leak in a corner (BA3-X9).** Every finding was reproduced
before a line was changed: the server's by running the readers' own probes on the frozen copy, before the
fix and after; the client's by a new step of the live walk that FAILED in the real client and holds now. The
rows are `BUG_FIXES.md` §BA3, BA3-X6 to BA3-X22 (thirteen fixed here, four filed for BA-4); the pins are
`tests/test_ba3_the_review.py` and the live walk's steps in `tests/test_ba3_the_days_panel.py`; the rules are
`SYSTEMS_REFERENCE.md` §221.

#### Fixed in the review

- **An objection's answer is told as what the marshal then did, and only the question that parked a word
  answers it (BA3-X6).** The word was billed and told as itself whatever its answer ran: a "compromise" that
  only changed his stance read "Ney presses the attack."; an alternative that fought a battle read "Ney digs
  in." on the day and in the clash's own script; an alternative that left the field closed the day with no
  line and no banner. And the parked word was found by the marshal's name alone, so with the muster's
  question standing on his press the lead's ordinary `defend`, objected to and insisted on, ran on the parked
  word's lend — no action — and took no point either. Now the parked word records what parked it; the order
  the chosen answer runs is read before it runs; his attack on the day's enemy is a clash of the day, a
  defensive stance is digging in, a retreat is a fall-back under its own banner, anything else "goes his own
  way". The price stays the one the chip quoted.
- **A day that is over (BA3-X7, BA3-X18).** The end-turn gate named a day whose lead had marched off the
  field (`awaiting` now asks that the day is alive). And the client kept each day's last block for ever: night
  falls at End Turn with no block, so on the next turn a chip of the dead day was still lit in the log's old
  lines — pressed, it sent its order, which with no day open fought a battle for a real action. Every response
  now names the days still open (`open_battle_days`); the client lets go of the rest.
- **Who left, and where to (BA3-X8, BA3-X9).** Our own lead, left to it and beaten on points, left the field
  under "MACK DRAWS OFF": he falls back, under his own banner. And "Mack draws off toward Vienna." named a
  province we could not see when the clash had been won without our lead on the field (the guns' word): the
  province is named only when the game's one sighting rule shows him standing there — the fog law's "never
  where to".
- **The telling (BA3-X10, BA3-X12).** On a day he opened, his answer to "Ney strikes back." was "Mack strikes
  back." too: his second assault "comes on again", on the day's line and in the tableau's own word beat. And
  the named moment of a late arrival said "The day is won" on a battle won on points — under "THE DAY HANGS":
  it and the two on the dice now say "on points" unless the battle decided it.
- **Two days, one lead (BA3-X11).** A word was classified against the first day whose lead matched and no
  other: the second day's lit chip ran as an ordinary order at an action's price. Every arm now falls through
  to the first day that can take the word. Whether a lead should hold two days at once is BA3-X15.
- **The client (BA3-X17, BA3-X19, BA3-X22).** After a word that drew his clash the client remembered our own
  tableau's snapshot (no chips, "his answer follows") as the day's latest block: "View the field" then raised
  a table that awaited us with no chips and closed itself. The province panel read "1 POINTS". And a word
  given from a table raised over the enemy phase's list never showed its answer — the readers had read it as
  a delay; pressed in the real client, neither clash's table ever came. The cause was found from the live
  walk's own state reads: a word that raised a question re-raised the list's stale dawn table, which then
  stood in the answer's way. **The client fix's own first cut failed at run time on a line the parse check
  passes (`bool(<Dictionary>)`); the live walk caught it.**
- **Pins that could not fail (BA3-X20).** The two "same save" headline pins reloaded under two ambient
  streams that happened to agree: with the temper's seam held down both still passed. Each now has a board or
  streams on which it can fail and a twin that proves it. Three core behaviours had no pin — a word is free
  with the pool empty, he answers our spent word, a priced word starts the silences again — and one pin
  asserted inside a branch its board never took.
- **The records (BA3-X21).** BA3-X2 had no behaviour test; BA-4's scope differed between records; the wire's
  field list and the count of the temper's sites; stale owners and a date in re-pointed pins; and the record's
  "never `ai_rng`" (BA3-X14).

#### Filed, each with its owner and a strict-xfail pin

| Row | Owner | What |
|---|---|---|
| BA3-X13 | BA-4, behind a seam in its measure | The night bars his strike on the day's lead for the phase that follows — also for a day that was already dead because its lead had marched away: walking off buys a phase in which that corps cannot be struck by him. The fix lets his AI strike where it could not, so it moves a measured world-line. |
| BA3-X14 | BA-4, behind a seam in its measure | His word's order is scored with a draw from his court's stream for the turn — the phase's, which no save carries: a save and a load after a word of his replay his phase from another draw. The fix changes every campaign in which he speaks before his phase; the sweep of §15.16 is read again with it. |
| BA3-X15 | BA-4, a rule for its plan gate | Two corps of his can each open a day against one lead of ours: two purses, one lead. BA-3's recommendation: a lead holds ONE day at a time, and a second great battle against him is told as the one clash it is. |
| BA3-X16 | BA-4, behind a seam in its measure | Two different stance orders to one marshal share one seeded mood (the stream is keyed on `target`, a stance order carries `target_stance`). The fix re-keys a seeded draw. |

Each is P3 and none is new behaviour the player was promised; each has a strict-xfail pin in
`tests/test_ba3_the_review.py::TestFiledForTheRoadsAndTheFog` that fails on the defect alone.

#### Read and left as it is

- **A stale claim on the next table** (`_day_word_sent`, `_day_table_held` after an answer that carries no
  day): no road reaches it but a server error — every word's answer carries the day's block. Not changed.
- **A march seen to arrive, its origin on the wire.** The enemy phase's own filter (PT-E5, older than row
  BA) blanks the structured origin of a march whose start we did not see; the action's `message` string still
  says "from Hungary". The client builds its row from the keys and never prints that message. Not a row of
  this change; noted for Session H's fog list.
- **His day's rule against his phase's.** `the_days_word` counts the corps of the foe's own nation where the
  foe stands; his phase counts every hostile corps he can see in his own province — they differ only with a
  third court's corps on the field. And his phase retreats on any bad odds where the day's rule draws off only
  when the last clash went against him: that is the recorded decision (§15.17).
- **His purse says whether his command is eight or more.** By design: a great battle names its commander.
- **A sovereign's alternative attack through an objection is no Guard** — the Guard is the word that asks two
  points; the sovereign raises no objection of his own.

#### Verification (the final tree, November 16, 2026 — after the review's fixes)

- **The readers' own probes, run again on the fixed copy**: each defect gone; `tests/test_ba3_the_review.py`
  holds a pin a row.
- **Pressed in the real client** (`tools/ba3_mode_c_walk.py`; record and frames
  `docs/audits/ba3_mode_c_2026_11_15/`): six boards on a sandboxed backend, 44 of 44 steps, no script error on any board, 30 frames kept — `ulm`: the real opening, the Guard for two points and no action, Mack taken (4 of 4); `massena`: the province panel's day block, its chip and its title "… — 1 POINT" once a point is spent, the lead's press through the muster's question, "His answer ▸" and the table going on by itself, "Leave it to Masséna" (10 of 10); `defence`: End Turn, the enemy phase's list, the morning's table with its chips, "digs in" through the objection, his clash, the end-turn gate's sentence and chip, the notice's "Take the field", "Fall back" with a great court's letter interposing, an End Turn with no day open (14 of 14); `typed`: a word typed by hand, a chip pressed in the log, and — the review's `r11_view_the_field` — a table re-opened from the log for a day that awaits us keeps its five chips and stays up (6 of 6); `r12`: the review's `r12_old_chip` — End Turn through the gate with a day open, the phase left, and on the new turn the old chip in the log is no longer live and no action is spent (4 of 4); `review`: the review's `r15_his_clash` — the lead's "strikes back" from the table raised over the enemy phase's list: our clash's table over the list, "His answer ▸", his table 2.25 seconds after ours rests, the day's new purses and chips, and the list's Continue afterwards (6 of 6). Each of the three review steps FAILED in the real client before its fix.
- **The measure, taken again whole** (`tools/_ba3_measure.py`, the sweep's own command; eight seeds by nine
  arms, 72 campaigns of forty turns): identical to the sweep of record in all 72 cells — France's provinces and each run's status. Only the LABELS of how nine cells' days ended differ: our own lead's leaving is counted `fell_back` where it read `drew_off` (arm `L`) or `over` (arms `P`, `G`). The review's fixes moved no measured number; `tools/_ba3_sweep_2026_11_15.json` is now this run. After one further line of the telling (a timed SUPPORT is told as the corps ordered up — it changes no order, price or turn) the commanded arms were read once more: every new seam down 26 / 27 / 28, the gate's reading 28 / 27 / 27, the fall-back arm 26 / 27 / 23; and the exploratory arms (`tools/_ba3_arms_2026_11_15.json`, re-taken) read as on record.
- **Nothing outside a campaign the server holds moved**: the keyed world probe is IDENTICAL to the commit before on jena and marengo (30 ambient turns, 212 keys a turn).
- **The walk of record**, re-shot (two of its eleven sources changed — `battle_day.py`, `battle_script.py`):
  129 of 129 shots on the 33 staged scenes and BA-1's four-a-side payload, every claim holding, no script error, 41 frames kept; every scene staged again and no payload differs from the record; the switch-off table 44 cases, 44 caught.
- **The instruments**, run again: every figure as before the review — nineteen surfaces at the five sizes: readability 2,134 rows, RED 0, P1 0; contrast 2,121 measured, none under the floor; fit 19 of 19 at 1920×1080, 3840×2160 and 5120×1440; the frame census 95 frames, no cut line, no overlap, the verdict's room 9.6 px at the least. No captured surface carries a line the review lengthened; "… falls back toward <province>." is of the length the draw-off's line already had.
- **The parse harness**: 98 scripts and 17 scenes, no error. The check cannot see a run-time error: the client fix's own first cut called `bool()` on a Dictionary, which parses; the live walk caught it on five boards.
- **Tests**: `tests/test_ba3_the_review.py` (28: a pin a row — 24 pass, 4 are the filed rows' strict xfails), `tests/test_ba3_the_rounds.py` (113), `tests/test_ba3_the_days_panel.py` (27: the driven day scenes, the walk's and the six live boards' records, the instruments, and BA3-X2's strict xfail, which runs the walk at text size 1.3), `tests/test_ws16_the_same_order_draws_the_same_temper.py` (46).
- **The full suite on the final tree**: 41,207 passed, 27 skipped, 32 xfailed, none failed, in 9:38 at ten workers (the hook's own line: `-n 10 --dist loadgroup`) — 35 more tests than before the review and five more strict xfails (the four filed rows' pins and BA3-X2's). After it only this figure was written into the records, and the suite was run once more on the tree as committed.

### 15.19 BA-4's gate — "the roads and the fog" (November 16, 2026, authoritative; it amends §15.5.7, §15.7 and §15.17)

BA-4 is the row's last session before the deploy. It takes every open row that moves a measured world-line —
twelve ledger rows, §15.5.7's two ticked rules — and the items BA-3 recommended and did not build (§15.17). It
opened in Plan Mode; four questions were put to the user and the plan was approved as written.

#### The user's words (verbatim)

| Question | The user's word | What it rules |
|---|---|---|
| BA3-X15 — two days on one lead | "One day a lead (Recommended)" | A second hanging great battle against a lead whose day is open opens no day; it is told as the one clash it is. |
| BA-3's three telling items | "review these are good and make any other imrpovments,First-open line,Line for a quiet night,One name for a day" | All three are built, each reviewed first; improvements may be added (each one line to reverse). |
| Digits for the day's chips | "Yes, on the table (Recommended)" | Digits 1–9 on the battle table while it awaits a word. WS-10 (who owns the bare digits elsewhere) stays Session H's. |
| The key bar | "dor erseaarch of whats the most FUN" | The bar is settled by research and a rule written before the data, then measured (below). |

#### The review of the three telling items, and what it added

- **The first-open line — built, reworded** to the table's own words ("points", "the enemy"): "The day
  hangs, Sire. Each side holds points for the rest of it: a word costs points, never an action, and the enemy
  answers each word in turn. Two silences running, or every point spent, and night falls."
- **One name for a day — built, with two corrections to the recommendation.** The province's battle count
  still advances once a clash (the battle's dice and the voice rotation read it), so the later clashes are
  counted beside it and subtracted: a later, separate battle there is still "the Second". A later clash is
  an ordinal ("— the second clash"), not a time of day: "the afternoon" would contradict the "at the last
  hour" beat the opening clash may already have told.
- **The line for a quiet night — right, too narrow, and its recommended home was wrong.** The only channel
  BA-3 named prints under DIPLOMATIC EVENTS. Built instead as the first improvement below.

Improvements added under "make any other improvements":

1. **Every day's close is told, not only the quiet night**: one line with the day's clashes and its toll,
   for every way a day ends — on the closing table, in the campaign log, and for a day the night closed
   among the morning's turn events.
2. **The second battle says why it has no day** (BA3-X15): one line in its telling, and on the same field
   it takes the day's name as a further clash.
3. **Fixed digits**, as the selection card has fixed slots: 1 press or strike back, 2 the Guard, 3 dig in,
   4–6 the first three corps chips, 7 stand, 8 break off or fall back, 9 leave it to him. Further corps
   chips stay the mouse's and show no digit.
4. **A great battle abroad forces a Gazette special** the turn after (BA2-X20's news); an ally's ordinary
   battle in a war we share is news in the log at once and in the next regular issue.
5. **A support order's quote says "halts at the approach"** where the order already does.

#### The key bar — the research, and the rule that settles it

What the game's own record said before the session (`docs/audits/ba3/hinge_probe_2026_11_15.json`: 47
battles in two commanded campaigns, by the men on both sides):

| Bar | Days opened (two campaigns) | What the bar adds |
|---|---|---|
| 80,000 (BA-3's) | 8 | three to seven corps engaged in each |
| 70,000 / 60,000 | 10 | the Emperor's own stack against the Archduke Charles (75,000 men, five corps) and one duel of one corps a side (71,000) |
| 50,000 | 12 | one more duel (52,000) and one battle of three corps (58,000) |
| 40,000 / 30,000 | 16 / 22 | the same pairs on consecutive turns; at 30,000 one pair four turns running |

Battle sizes are not spread evenly (30–46,000, then nothing until 51,000; the lower group is where the same
fight repeats). At every bar the days cluster in the campaign's opening. Marengo — a day that hung and was
turned by a fresh corps — was about 58,000 men by its end. Published design writing gives no number: a peak
needs rest before the next; players skip a battle whose result is foregone or that repeats; too much
tactical play stalls the campaign. Two campaigns are not evidence, so the bar is settled by a measured
ladder.

**The rule (written before the data).** Ladder 50,000 / 60,000 / 70,000 / 80,000; eight seeds; the silent arm
and "left to the marshal" (sixteen campaigns a bar). The bar becomes the LOWEST that passes all of:

- **Rich** — at least two days in three offer four or more priced words (more than press and dig in);
- **Varied** — at most one day in five repeats the same two leads within two turns of an earlier day;
- **Rested** — at most eight days a campaign on average, and days on four turns running in no more than
  one campaign of the sixteen;
- **Balanced** — the band stays inside 23–28 on the commanded seeds and the hand stays healthy (M4).

If none below 80,000 passes, 80,000 stands. If the bar moves, "The Great Battle of …" keeps its 80,000, the
attack card says "A pitched battle — <lead> commands the day" between the two bars, and the help follows.
Approving the plan was the user's word for the rule's pick; the table is reported per seed either way.

#### The measure — ONE, with arms, per seed (rules written before the data)

Every mover sits behind a zero-argument seam function in the module it gates; with all of them down the
game is the commit before (`aeae6967`). The hold-list is `tests/_ba4_seams.py`, folded into
`tests/_oct27_seams.py`. BA-3 moved nothing outside a campaign the server holds, so its measure read only
the commanded band; six of BA-4's rules move world-lines nobody serves, so this measure reads all three
surfaces of the deploy gate, and **Session H reads the gate against BA-4's records.**

| Rule | What it asks |
|---|---|
| M0, the control | Before the first edit, the commit before is read on every surface: the keyed probe, the ten-seed ambient sweep, the AI-France harness, the band. |
| M1, arm 0 reproduces it | Every BA-4 seam down: the keyed probe IDENTICAL on jena and marengo; ambient and harness equal to M0; the band 28 / 27 / 27; the eight-seed day sweep equal to `tools/_ba3_sweep_2026_11_15.json` cell for cell. If not: stop, and bring it to the user. |
| M2, attribution | The cumulative ladder in the arms' order. Ambient and harness for the arms that can move them; the band for every arm. The arm of the rows that move no number must equal the arm before it. |
| M3, the gate on the shipped tree | The band inside 23–28 on each commanded seed; story classes at least 6; a promotion on at least one seed; the roster in at least two readings; `annexations_outside_aim` 0 on the ambient record. A clause that held before and fails: stop, with the arm that moved it. No number is tuned. |
| M4, the hand | §15.16's rule read again: the silent script's mean shift within ±1.5 provinces; no way of playing a day beyond ±3 on average; none best on six seeds of eight. |
| M5, jena | The probe's jena arm runs its 40 turns with no court's turn lost; what the fix moves from that turn is reported. |
| M6, the key bar | The rule above. If the bar moves, M3 and M4 are read again at the new bar. |

One correction to the brief, found reading the code at the gate: the support order's approach arm already
existed for a foe on the friend's own province (DDB-20). BA-4 extends its one predicate; it builds no new
arm.

### 15.20 LANDING RECORD — BA-4 "the roads and the fog" BUILT November 16, 2026 (authoritative)

One session: the gate (§15.19), the build, ONE measure with arms on all three surfaces of the deploy gate,
the session's review (§15.21). The rules are in `SYSTEMS_REFERENCE.md` §222; this is what landed and how it
was verified. **Row BA is complete with it.**

#### What a player gets

- **A court never loses its turn to a corps raised in the middle of it** (BA2-X2). On the seed that showed
  it, Prussia took Dresden, the peace released Yorck from his prison to Berlin, and the rest of Prussia's
  turn was lost with him; it is played now.
- **A battery is no victim of its own shells** (BA2-X12).
- **A support order that meets the corps its friend is to attack halts at the approach, asks nothing, and
  joins the attack** (the approach rule; BA2-X7). Murat can be committed to Ney's battle at Ulm by an order;
  before, the order stopped on "Your orders?". The card, the province's chip and the badge on the map's road
  say "halts at the approach".
- **A road round a corps keeps to frontiers the corps may cross** (BA2-X10); where none goes round, the order
  ends at the approach and says so.
- **An order's card names the men its first march costs** (BA2-X21): "The first march costs 572 men."
- **Berthier names an order only where sending it brings the corps** (BA2-X7), and says why where it
  would not.
- **A word of the day is priced as a word everywhere it is quoted** (BA3-X5): the attack card reads "A word
  of the day — 1 point", the province's rows, the relay, the readback and the map's badge the same.
- **The day takes as "a corps is brought up" only the order its table offers** (BA4-X1): a support order for
  a corps far from the field is an ordinary order again, and the day keeps its point.
- **A pursuit is earned by any corps of the victor that fought** (§15.5.7): Murat, riding in beside Ney,
  turns Ney's rout into the annihilation it was at Jena.
- **A corps that comes up at the last hour brings three-quarters of its weight** (§15.5.7), on either side;
  the muster counts it beforehand and says so.
- **One day a lead** (BA3-X15, the user's ruling): a second great battle against a lead whose day is open is
  told as the one clash it is, with the reason.
- **Walking a lead off his day no longer buys a phase in which he cannot be struck** (BA3-X13); **the
  enemy's word no longer moves his court's dice** (BA3-X14) — a save and a load after it replay the same
  phase; **two different orders to one marshal draw their own tempers** (BA3-X16).
- **A day of battle has one name** — "The Great Battle of Swabia", and then "— the second clash", "— the
  third clash" — and the next battle there is the Second.
- **Every day's close is told** in one line with its clashes and its toll: on the closing table, in the
  campaign log, and in the morning's turn events for a day the night closed.
- **The first day of a campaign says what a day is**, once, on its own row above the chips.
- **Digits on the table**: 1 press or strike back, 2 the Guard, 3 dig in, 4–6 the first three corps chips,
  7 stand, 8 break off or fall back, 9 leave it to him.
- **A battle lights its field for those who fought in it** (BA2-X20). A great battle abroad, or an ally's in
  a war you share, is news — the crowns, the province and who held the field, never a commander or a figure
  — in the log, the morning's dispatch and Le Moniteur (a great one forces a special).
- **Help** names the last hour, the pursuit and the news of a battle.

#### The measure — ONE chain: sixteen seams and the bar, fourteen arms, three surfaces of the gate

`tools/_ba4_measure.py`, run alone on the frozen backend: the probe, the band, the ambient sweep, the
AI-France harness, the day's sweep, the key bar, the gate — 74 minutes — and then, with the picked bar
written into the game, the band and the day's sweep once more on the final tree (17 minutes). The records:
`tools/_ba4_probe_2026_11_16.json`, `_ba4_band_2026_11_16.json`, `_ba4_chain_d_2026_11_16.json`,
`_dy_signature_ba4_<arm>_2026_11_16.json` and `_ba4_<arm>_census_2026_11_16.json` (ten arms),
`_ba4_sweep_0_2026_11_16.json`, `_ba4_sweep_x14_2026_11_16.json`, `_ba4_kbar_2026_11_16.json`; the control's
(`…_control_…`); and the final tree's at the picked bar (`_ba4_band_2026_11_16_k50.json`,
`_ba4_sweep_x14_2026_11_16_k50.json`, `_ba4_probe_2026_11_16_k50.json`). Pinned by
`tests/test_ba4_the_roads_and_the_fog.py::TestTheMeasureOfRecord`.

**M0, the control** (the commit before, read before the first edit). The keyed probe: jena loses one
court's turn — Prussia's, on turn 30, to `KeyError: 'Yorck'` — and marengo none. The ambient sweep's
signature is Session G5's on all ten seeds; its census differs from G5's only by a few men of supply losses
on friedland and marengo. The AI-France harness is G5's shipped arm on all ten. The band 28 / 27 / 27. The
game had not drifted from G5's records on the two surfaces nobody had re-read since.

**M1, arm 0 reproduces the commit before** — every seam down: the probe IDENTICAL on jena and marengo
(forty turns, 212 keys a turn; its one lost turn reproduced); the band 28 / 27 / 27; the ambient signature
and census identical on all ten seeds; the harness identical; the eight-seed day sweep equal to BA-3's
sweep of record in 72 cells of 72.

**M2, attribution** — the cumulative ladder, each arm against the arm before it (the band at the bar of
80,000, where the ladder was read):

| Arm | The rule it brings up | Probe: jena | Probe: marengo | Ambient seeds moved (of 10) | Harness seeds moved (of 10) | Band H / A / M |
|---|---|---|---|---|---|---|
| `0` | every BA-4 seam down | = the commit before | = the commit before | = the control | = the control | 28 / 27 / 27 |
| `X2` | a corps raised mid-phase takes its turn (BA2-X2) | from turn 30 | identical | none | none | 28 / 27 / 27 |
| `X12` | a battery is spared its own shells (BA2-X12) | identical | identical | none | none | 28 / 27 / 27 |
| `X10` | a road round keeps to open frontiers (BA2-X10) | identical | identical | none | none | 28 / 27 / 27 |
| `APPROACH` | a support order halts before the friend's foe | identical | identical | none | none | 28 / 27 / 27 |
| `X20` | a battle lights its field for those who fought (BA2-X20) | from turn 3 | from turn 2 | none | 7: austerlitz, eylau, historical, lodi, rivoli, ulm, wagram | 28 / 27 / 27 |
| `PURSUIT` | a pursuit is any corps that fought (§15.5.7) | identical | identical | none | 10: austerlitz, eylau, friedland, historical, jena, lodi, marengo, rivoli, ulm, wagram | 27 / 27 / 27 |
| `QUARTERS` | the last hour brings three quarters (§15.5.7) | from turn 26 | from turn 32 | 7: eylau, friedland, jena, lodi, marengo, rivoli, wagram | 5: eylau, jena, marengo, rivoli, ulm | 27 / 28 / 27 |
| `TELL` | the four rows that move no number | identical | identical | none | none | 27 / 28 / 27 |
| `OFFER` | the day takes the order its table offers (BA4-X1) | identical | identical | not read (served only) | not read (served only) | 27 / 28 / 27 |
| `X13` | a dead day bars nothing (BA3-X13) | identical | identical | not read (served only) | not read (served only) | 27 / 28 / 27 |
| `X16` | an order draws its own temper (BA3-X16) | identical | identical | not read (served only) | not read (served only) | 27 / 28 / 27 |
| `X15` | a lead holds one day (BA3-X15) | identical | identical | not read (served only) | not read (served only) | 27 / 28 / 27 |
| `X14` | his word is scored from the day (BA3-X14) — the shipped tree | identical | identical | none | none | 27 / 28 / 27 |

- **X2** moves jena from turn 30 and nothing else anywhere: over the eleven turns that follow only
  `ai_stagnation_turns` and `notifications` ever differ. Prussia's turn is played; her corps waits.
- **X12, X10 and the approach rule move no measured reading.** A static scan of the opening board finds a
  road round through a shut frontier for a court's corps in 219 placements, and none was walked in forty
  turns of ten seeds; the approach rule is the player's order, which no script of the measure sends. They
  are held by their pins and by hand (§222), not by a world-line.
- **X20** moves only what the player is told where France does nothing: on the probe, over all forty turns
  of both seeds, `intel`, `event_log`, `pending_dispatch_events`, `gazette_issues` and `notifications`
  differ and no key of the board. On the harness, where the AI plays France and its orders pass the
  player's fog, seven seeds move. The commanded band does not.
- **The pursuit** moves every harness seed (an AI-run France fights with Murat beside its leads) and one
  commanded seed by one province (28 → 27); no ambient seed.
- **The last hour** is the session's widest mover: seven ambient seeds (three of them only in supply
  losses), five harness seeds, one commanded seed by one province (27 → 28). On the ambient record
  captures outside aim go 290 → 280, evacuations 46 → 52, last refuges 26 → 31; the story classes stay 10.
- **The four rows that move no number move none** (TELL equals QUARTERS on every surface); **the day's
  door** (OFFER) equals TELL on the band; and nothing of the day's reaches a campaign nobody serves (the
  shipped arm equals TELL on the ambient sweep and the harness). X13, X16, X15 and X14 leave the band where
  it was; X14 changes how many days one commanded campaign meets (six, then five).

**M3, the gate — MET on every arm, and on the final tree:**

| Clause | The final tree | Record |
|---|---|---|
| The France band inside 23–28 on each commanded seed | **28 / 28 / 27** at the picked bar (27 / 28 / 27 at 80,000; 28 / 27 / 27 before the session) | `_ba4_band_2026_11_16_k50.json`; every arm at 80,000 in `_ba4_band_2026_11_16.json` |
| Story classes at least 6 | 10 of 10 | `_dy_signature_ba4_x14_2026_11_16.json` |
| A minor at secondary rank by promotion on at least one seed | two: Hesse on lodi (33) and marengo (39) | the same, `rank_promotions` |
| The roster in at least two readings | two: {Kingdom of Italy} on eight seeds; {Kingdom of Italy, Papal States} on jena and wagram | the same, `eliminations` |
| `annexations_outside_aim` 0 on the ambient record | 0 | `_ba4_x14_census_2026_11_16.json` |

The gate's readings per arm of the ladder (the ambient record, and the harness's line beside it):

| Arm | Story classes | Promotions (seed: turn) | Roster readings | Annexations outside aim (ambient) | Captures outside aim (ambient) | Harness: annexations / captures outside aim |
|---|---|---|---|---|---|---|
| `0` | 10 | lodi 33, marengo 39 | 2 | 0 | 290 | 0 / 135 |
| `X2` | 10 | lodi 33, marengo 39 | 2 | 0 | 290 | 0 / 135 |
| `X12` | 10 | lodi 33, marengo 39 | 2 | 0 | 290 | 0 / 135 |
| `X10` | 10 | lodi 33, marengo 39 | 2 | 0 | 290 | 0 / 135 |
| `APPROACH` | 10 | lodi 33, marengo 39 | 2 | 0 | 290 | 0 / 135 |
| `X20` | 10 | lodi 33, marengo 39 | 2 | 0 | 290 | 0 / 152 |
| `PURSUIT` | 10 | lodi 33, marengo 39 | 2 | 0 | 290 | 0 / 125 |
| `QUARTERS` | 10 | lodi 33, marengo 39 | 2 | 0 | 280 | 2 / 136 |
| `TELL` | 10 | lodi 33, marengo 39 | 2 | 0 | 280 | 2 / 136 |
| `X14` | 10 | lodi 33, marengo 39 | 2 | 0 | 280 | 2 / 136 |

The ambient and harness surfaces do not see the key bar (a day exists only where a campaign is served). On
the final tree the keyed probe differs from the measured shipped arm in ONE key on every turn of both seeds
— `marshals`, which carries Murat's reworded ability sentence — and reads IDENTICAL to it with the old
sentence put back: the ambient and harness records are the final tree's.

**M4, the hand** (§15.16's rule, read again; Δ is France's provinces under an arm less under `T`, the day's
seam down). On the final tree, at the picked bar (`_ba4_sweep_x14_2026_11_16_k50.json`):

| Arm | H | A | M | jena | wagram | lodi | eylau | friedland | mean Δ vs `T` | range |
|---|---|---|---|---|---|---|---|---|---|---|
| `0` every BA-3 seam down | 28 | 26 | 28 | 27 | 28 | 28 | 28 | 24 | +0.62 | 0 … +5 |
| `T` the day's seam down | 28 | 26 | 28 | 27 | 28 | 28 | 28 | 19 | 0 | — |
| `S` silent | 28 | 28 | 27 | 27 | 25 | 28 | 26 | 22 | **−0.12** | −3 … +3 |
| `L` left to the marshal | 28 | 27 | 24 | 28 | 26 | 27 | 27 | 28 | +0.38 | −4 … +9 |
| `P` pressed | 26 | 26 | 21 | 25 | 28 | 27 | 27 | 26 | −0.75 | −7 … +7 |
| `D` dug in | 28 | 28 | 28 | 25 | 28 | 24 | 27 | 24 | 0.00 | −4 … +5 |
| `B` broken off | 26 | 26 | 28 | 28 | 23 | 27 | 27 | 28 | +0.12 | −5 … +9 |
| `G` the Guard | 26 | 27 | 28 | 28 | 27 | 28 | 19 | 28 | −0.12 | −9 … +9 |
| `ALL` `sense` | 28 | 23 | 25 | 25 | 27 | 27 | 27 | 27 | −0.38 | −3 … +8 |

- **The instrument holds:** the silent script's mean Δ is −0.12, inside ±1.5.
- **The hand is healthy:** no arm's mean Δ reaches ±3 — the largest are +0.38 and −0.75 — and no arm is
  best on six seeds of eight: the most is `D`, level-best on five and alone on none.
- At 80,000 (`_ba4_sweep_x14_2026_11_16.json`, the same tree but for the bar) the rule held too: the silent
  script −1.00, the other means between +0.50 and −0.62, `G` level-best on five.
- **Seeded paths, per seed.** friedland is this tree's outlier as jena was BA-3's: with the day's seam DOWN
  France holds 28 provinces to turn 30 and loses nine in the last ten turns (19) — the last hour's and the
  pursuit's world-line, not the day's; jena, which read 19 before, holds 27. Single readings below the band
  on other arms: `P` 21 on the third commanded seed, `G` 19 on eylau, `S` 22 on friedland. None is the
  gate's reading; each is reported, not tuned.

**M5, jena:** from the fix on, no court's turn is lost on either probe seed in any arm. What raised him,
read from the run: Yorck's attack fails on turn 29 and Saxony takes him prisoner; on turn 30, inside
Prussia's own phase, Hohenlohe storms Dresden — Saxony's last refuge — the peace releases Yorck to Berlin
with 5,000 men, and the phase chooses him for its last action. The commit before lost the rest of
Prussia's turn there.

**M6, the key bar — 50,000** (`_ba4_kbar_2026_11_16.json`; the rule of §15.19: the LOWEST bar that passes):

| Bar | Days met (16 campaigns) | Rich: days offering 4+ priced words | Varied: days repeating a pair within two turns | Rested: days a campaign; campaigns with four turns running | Band, silent (H / A / M) | Passes |
|---|---|---|---|---|---|---|
| 50,000 | 60 | 0.933 (pass) | 0.033 (pass) | 3.75; 1 (pass) | 28 / 28 / 27 (in) | yes |
| 60,000 | 52 | 0.981 (pass) | 0.038 (pass) | 3.25; 1 (pass) | 28 / 28 / 27 (in) | yes |
| 70,000 | 45 | 0.978 (pass) | 0.044 (pass) | 2.81; 1 (pass) | 28 / 28 / 27 (in) | yes |
| 80,000 | 41 | 1.0 (pass) | 0.024 (pass) | 2.56; 1 (pass) | 27 / 28 / 27 (in) | yes |

- All four bars pass. Lowering the bar from 80,000 to 50,000 adds nineteen days over sixteen campaigns (41
  → 60: 2.6 → 3.75 a campaign); 56 of the 60 offer four or more priced words; two repeat a pairing within
  two turns; the one campaign with days on four turns running is the same at every bar ("left to the
  marshal" on jena, turns 1 to 4 — the campaign's opening).
- By the rule the pick is the lowest, 50,000, with M3 and M4 read again at it (above): the band 28 / 28 /
  27 and a healthier hand than at 80,000. The expectation written beside the rule was 60,000; the rule
  decides. `battle_day.KEY_BATTLE_MEN`; one function to reverse (`key_bar`).
- "The Great Battle of …" keeps its 80,000, as does the news of a great battle abroad; between the two bars
  the attack card says "A pitched battle — <lead> commands the day: N points", and the help names both.
- **The bar re-times a served campaign, and the session OFF holds it at 80,000.** The full suite on the
  final tree showed it (find 16). RS-27's scripted volte-face arm, on the historical seed, meets five days of
  battle at the picked bar where it met three; its war takes another course (thirty-one battles on the drive
  against twenty-two, six designs promoted against one) and the beat never fires in forty turns. With the bar
  held at 80,000 ALONE it fires on turn 25. The pin holds the bar with that reason, as it holds eight rules
  before this one — a seeded path, reported, not a law. The hold-list carries the bar
  (`tests/_ba4_seams.py` `BA4_THE_KEY_BAR`) and every recorded board with it; the measure's two served
  surfaces take `--key-bar`, 80,000 by default, and read again from the final tree with the bar held arm `0`
  is 28 / 27 / 27 and X14 27 / 28 / 27 (`tools/_ba4_band_hold_2026_11_16.json`): every seam down and the bar
  held is the commit before.

**The AI-France harness's annexation line reads 2 on one seed — reported, never gated.** From the last
hour's arm on, jena's harness run ends with two provinces held by right outside an authored aim, where
every arm before reads 0 (as Session G5's record did). Read to its cause: the AI-run France destroys
Austria on turn 14 (turn 13 before); on turn 15 a British expedition lands at Carniola and takes it from
France, and on turn 16 Britain and France sign a truce — Wellesley "can find no land route home at all", so
the status quo keeps him and the province; on turn 37 Sweden takes Pomerania from Bavaria and on turn 40,
the run's last, signs her own truce with France. Both are a truce's retention of the ground a corps stands
on — the class Session G2 first recorded ("sign at the last") — reached by a world-line the last hour
opened. No conduct rule was touched and no number was tuned. The gated line, the AMBIENT record, reads 0 on
every arm. It is the user's to rule (below).

**The standing series is unmoved** on the shipped tree (`BASELINE_SERIES`; its own pin is green).

#### Verification (each once, on the frozen tree)

- **The staged scenes** (`tools/ba1_stage_battles.py`): thirty-three, staged again from the final backend — no
  kept seed moved; twenty payloads changed (the day's one name, its close, the first day's line, the pitched
  battle).
- **The parse harness:** exit 0 on 100 scripts and 17 scenes
  (`tools/godot_parse_report.json`); it names BA-3's and BA-4's live walks now (BA-3's had not been named).
- **The walk of record** (`tools/ba1_acts_walk.py`, the window, 157 shots): 157 complete, no script error, no
  claim failed; `docs/audits/ba1_client/walk_record.json` holds the hashes of its eleven sources and of the
  payloads it played. It was shot twice: the second time with the digits' claims read (find 15).
- **The switch-off table** (`tools/ba2_switch_off.py`; fifty cases, six of them this session's): fifty of fifty
  catch their fix switched off, and `battle_acts.gd` is put back byte for byte. The first run read forty-seven
  (find 15).
- **The live client** (`tools/ba4_mode_c_walk.py --export`: the real `main.tscn` against a sandboxed server;
  `docs/audits/ba4_mode_c_2026_11_16/`): the day's board 12 steps of 12, the roads' 6 of 6, a save the commit
  before wrote 6 of 6 — no script error on any. One of the roads' six steps is the key bar's own wording, pressed on
  the real opening: Bernadotte against the Archduke John, 74,535 men by the card's own bar — "A pitched battle
  — Bernadotte commands the day: 2 points." and no "A great battle". BA-3's six boards, walked again on this tree and not exported, hold as BA-3 left them: 44 steps of 44 (the defence 14, Masséna's 10, the typed word 6, the review's two 6 and 4, Ulm 4).
- **The captures and the four instruments** (`ba4_roads_and_fog_2026_11_16`: the day's surfaces as this
  session left them and the four order cards whose words it changed — a halted support order, a march that
  names its cost, a word of the day, a pitched battle — 23 surfaces at the five sizes): readability
  no red row and no P1 in 2,334 rows of 115 readings; contrast nothing under the floor in 2,321 measured; fit 23 surfaces of 23 at 1920×1080, 3840×2160 and 5120×1440; the frame census 115 frames, each with its record, no cut line and no overlap (the six rows of the map hidden under the day's gate are BA-3's, unchanged). *These are the figures read before the review; the record files on disk are the review's own re-reading — 24 surfaces, with a fifth card (§15.21).*
- **The sign-ability sweep** (DD-1, `tools/sign_ability_sweep.py`), read again on all ten arms: no promise a
  surface showed was refused when signed and no refusal went unnamed — 0 / 0 over 3,584 promises. The nine
  long arms' records had last been written on November 8; the session's two combat rules move their world-lines
  (the quick arm by one chip), and the key bar the arms that serve a campaign.
- **The suite:** run on the frozen tree before these records were written, 41,461 passed and three failed — the pin that waits for the STATUS head, and finds 16 and 17, both fixed; the run that closes the session is §15.21's.

#### The finds (defects of the session's own new work, caught before this record; the two defects of what had already landed are `BUG_FIXES.md` §BA4)

| # | Found by | What was wrong | The fix |
|---|---|---|---|
| 1 | a walk over every arrival roll | The muster's forecast used a late arrival's WEIGHT as its coin: a corps sure to arrive, perhaps at the last hour, could fall out of the floor and the bad day. | An arrival's chance and its weight are kept apart (`_arrival_chance`, `_arrival_weight`, `_outcome_committed`); the pin walks every roll. |
| 2 | the new beat's case, written before the beat | The pursuit's beat on the table named a corps of another crown that the table does not seat, with an ability only he holds. | "<lead>'s reserve": no name, no ability, unless the corps is seated, or ours and attacking. |
| 3 | a quote taken with the pool empty | A word's quote said "no military action left this turn" over an order the door lends its actions. | The one pool test reads `battle_day.quoting_a_word`. |
| 4 | the plan's rows read on an open day | The plan priced the attack at an action though it is a word, and dropped rows the table should offer. | `bring_quotes` reads the attack's own price. |
| 5 | the opening battle played by hand | Berthier's hint was empty for a corps whose order marches him out of reach (Bernadotte, to Munich). | The `no_odds` sentence says where the order would take him and that he cannot reach the field from there. |
| 6 | a day played by hand | The close named the province the lead attacked FROM ("The attack at Rhineland was broken off"). | The day keeps `opened_at`; the close names it. |
| 7 | a seam's twin | With one-day-a-lead down, a day's name nested ("— the third clash — the second clash"). | The day's name is the battle's (`the_battle_of`). |
| 8 | the full suite, on one roll | A last-hour arrival put a massed attack under its ceiling, and a pin read the mass. | `massed_strength["last_hour"]` names the corps that were cut. |
| 9 | the days-panel walk (101 claims at first) | The first day's acknowledgement rode the table's word channel and was read as a word; the first day's row pushed a chip off the fullest tables. | The showing calls the scene; `_day_first_fits` — the row may take the told line's row and never scrolls a chip. |
| 10 | the settled frame | BA3-X2's second station set passed the table's own test and stood at rest on the reserve's note, the losses' caption and the banner. | Reverted; the file is the ruled layout from 120 %, with its measured reason. |
| 11 | the live client | The first day's acknowledgement never left the client (`current_scene` is null under a `SceneTree` script). | The showing walks the tableau's ancestors. |
| 12 | the live client's frame | The badge at the head of the map's ghost road read "attack · free" beside a card that read "A word of the day — 1 point". | The badge reads the chips' helper; a halted order's badge says "halts at the approach". |
| 13 | an old save, loaded through the server | A day that a save made by BA-3 carried open began a count at its NEXT clash: its close would have told "after one clash" and half the toll of a day of three. | The count begins at a day's opening clash or not at all; such a day closes as BA-3 closed it. |
| 14 | the full suite | A comment in `battle_acts.gd` named the API client and failed BA-1's display-only pin. | Reworded. |
| 15 | the switch-off table (47 of 50 at first) | The walk built and shot the digits' six kinds of press and never read their claims — its reader's list did not name them — so three digit fixes switched off walked green. | The list names them; the walk of record was shot again with the claims read (157 shots, none failed); a pin feeds the record back through the walk's own reader with a digit's shot doctored, and fails on the reader as it stood. |
| 16 | the full suite on the final tree | RS-27's pin went red — the key bar re-times its scripted arm (above, M6) — and with it showed that the session's OFF list held sixteen switches and no bar: "every seam down" had stopped being the commit before on a served campaign. | Measured, the pin re-seated with the bar held; the bar joins the hold-list and the measure's served surfaces (`--key-bar`), read again from the final tree. |
| 17 | the full suite on the final tree | The tutorial board's committed record named another file: Murat's reworded sentence is in that board too. | `tools/_table_board_probe.py` run again: the lesson's three turns play as before and every clause holds. |
| 18 | reading the attack card's new word for where it is shown | "A pitched battle — … commands the day" had been seen by no walk and no capture: the live day is a great battle of 96,000 men. | A step on the real opening (Bernadotte against the Archduke John, 74,535 men by the card's own bar) and a fourth order card in the captures. Its helper first looked on a board that serves no campaign, found no day, and the step FAILED rather than passed — as written. |

Three claims of the session's own walks were wrong and were corrected in the walk, not in the client (other
corps' "march & attack" rows keep their ATTACK heading; a log read from an offset the load had cleared; name
chips that now carry digits). Twenty-nine recorded battles and hand enumerations hold the last hour's seam
down with their reason; six of BA-3's told-line pins read the line before the new tally.

#### Decisions taken under the delegation (each one line to reverse)

- **The five improvements** added under "make any other improvements" (§15.19): every close told; the second
  battle says why it has no day; fixed digits; a great battle abroad forces a Gazette special (weight 55);
  "halts at the approach" on the quote.
- **News names crowns only** — never a commander, a man or a figure; and none is written for a field already
  in sight.
- **A far corps' support order is an ordinary order** (BA4-X1): the day takes only the order its table
  offers.
- **BA3-X2 is closed as the ruled layout**: the file from Text size 120 % up, measured (§222.10).
- **The first day's line never scrolls a chip**: where the table has no room it is the head's hover, and the
  next day's table shows it.
- **A day that kept no count tells no close** (a save made before BA-4): silence rather than a wrong figure.
- **A pursuer of another crown whom the table does not seat is "the reserve"** on the table (the battle's report line names him).
- **A pitched battle's acts keep BA-1's form.** A duel short of a great battle is told in brief before the
  day's table, as the later clashes of a great day already were; the day's table follows either form.
- **The scripted volte-face arm holds the bar at 80,000** (RS-27, re-seated by measurement): the days stage
  that arm's war, they are not the rule it pins.
- **Murat's sentence on his card** (the two scenario files) no longer says he must lead: "+5,000 pursuit
  casualties when an enemy he helped defeat is forced to retreat (cavalry; leading the attack, or fighting
  beside a lead who has no pursuit of his own)". A save made before BA-4 keeps the old sentence on his card;
  the rule is the new one for it too.

#### Not built (none is promised by a control)

- **WS-10** — who owns the bare digits while a ledger is pinned — stays Session H's; the table's digits are
  live only while the table is up and offers.
- **Weighed at BA-3's gate and not built** (§15.14), as before: ordinary battles settled by the marshals' own
  tempers; courts spending points against each other; stopping the enemy's phase to ask; a standing
  instruction per corps.

#### Owned by the session after this one

Session H — S15, the deploy. Row BA's open rows are BA1-X4, BA1-X8, BA2-X6 and BA2-X16, all Session H's as
before; none is BA-4's. **The deploy gate reads against this section's records.**

### 15.21 THE REVIEW — BA-4's one review, run before any commit on a frozen copy (November 16, 2026; authoritative)

The session's one review, as BA-3's was (§15.18): **six readers, one lane each, read-only, on a frozen copy
rebuilt from a bundle outside the repository** — `git archive` of the commit before plus the 219 changed or
new files, every one identical in the copy by hash, 410 unchanged files sampled and none differing — with the
commit before beside it to compare. Each reader could run small probes against the copy and nothing else: no
git, no server, no engine, no suite. **Every finding was reproduced on the tree (or on the frozen copy)
before a line was changed.** The rows are `BUG_FIXES.md` §BA4 (BA4-X3 to BA4-X11); the pins are
`tests/test_ba4_the_review.py`, a class a finding.

**The count: fifteen findings and notes — one a player meets (P2), the rest P3. No crash, no corruption, no
save that loads wrong, no leak of a commander or a figure.** Twelve are fixed, in nine ledger rows; one was
reproduced and NOT upheld; two were answered without a change to the game.

| Lane | Finding | Sev | Done |
|---|---|---|---|
| the fog and the news | The news of a battle abroad was written on the main attack's road alone: an ally's assault on a garrison in a shared war, his guns, a charge and an attack whose guns destroyed the defender were told to nobody — before the session each had lit its field. | P2 | **FIXED, BA4-X3.** Every road a field is lit on tells its dark side: `battle_news.of_a_battle` on the charge's and the guns' roads and the cavalry's own charge, `of_an_assault` ("… has assaulted the works of … — the walls held." / "— the place has fallen."), `of_a_cannonade` (an ally's in a shared war only; a cannonade has no victor, so none is great and none forces a special). Behind the fog rule's own seam. |
| the combat rules | A corps that marches yet brings NOTHING (a grievance, under a written order) carried last-hour odds, and the screen then said three-quarters of his weight was "counted in the figures above". | P3 | **FIXED, BA4-X4.** No last-hour odds where the pair's scale is nothing. |
| the combat rules | A muster of corps all SURE to arrive stated no least, though one of them may come at the last hour with three quarters. | P3 | **FIXED, BA4-X5.** `_spread_of_the_certain` — a player surface; no price a court reads passes through it. |
| the roads and the quotes | The approach rule halted the order for ANY corps on the step; its quote names a corps only where the player sees him. Unseen, the card was silent, the order halted, and its reply named the province of a corps no surface showed. | P3 | **FIXED, BA4-X6.** The rule asks what its quote asks; unseen, the step meets him as before the rule. |
| the roads and the quotes | A timed support order's clock starts when the corps reaches his friend — and at the approach he never does: "for 2 turns" held him for as long as the friend sat still. | P3 | **FIXED, BA4-X7.** The clock starts at his first stand at the approach. |
| the day of battle | While a lead's day is open the attack card on another corps still promised "… commands the day", for a battle the one-day rule tells as a single clash. | P3 | **FIXED, BA4-X8.** `the_day_he_holds` — one reading for the opening and the card; the card says what the rule will do. |
| the day of battle (a note) | A day that dies at dawn — its lead gone by morning, or his first word at dawn ending it — was logged and told on no table and in no morning. | P3 | **FIXED, BA4-X9.** The dawn collects its closes as the night does. |
| the client | The help still said "a second great battle" for a rule that begins at a pitched one. | P3 | **FIXED, BA4-X10.** |
| the client | An order taken at no action read "free" on the card and the map's badge and "0 AP" on the province's chip (older than the session; the chip's helper is the session's). | P3 | **FIXED, BA4-X10.** |
| the pins and the records | The pin on the key bar's pick read the rule's verdicts back from the record the rule itself wrote; only the picked bar asserted its sixteen runs. | P3 | **FIXED, BA4-X11.** The rule is tested clause by clause on days made by hand and read again from the record on all four bars. |
| the pins and the records | §15.20 called the pitched card "the roads' sixth step" (it is one of six; the sixth is the help), and a test comment gave another figure for the same battle. | P3 | **FIXED, BA4-X11.** |
| the pins and the records | BA3-X2's row reads FIXED while the wedge is still not laid at 120 % and above. | P3 | **Answered:** the row now says in its first words that it was closed as the ruled layout — a decision under the delegation, open with the user (§15.20). |
| the client | The day's digits are guarded by "the table is up, at rest and offering" — not by "no text field is above it". | P3 | **Answered, no change:** nothing can raise a text field over the table — its root stops every click behind it and every hotkey is refused under a modal; a question raised by a word finds the table latched, where a digit is denied. |
| the day of battle | A typed "Ney, retreat" on a day WE opened is taken as the day's word, though that table offers "Break off", not "Fall back" — read as a march to the rear at no action. | P3 | **NOT UPHELD — reproduced, then the fix reverted.** A retreat costs no action anywhere in the game (played on the frozen copy and on the tree: the pool is unchanged either way). Taken as the word it closes the day at once and says so — "Ney fell back from Lorraine after two clashes — 9,026 of ours for 10,983 of the enemy's." Made an ordinary order, the day stood open with its lead gone until night and closed as "ended where it stood". The door stays; the pin holds it. |
| the roads and the quotes (not filed) | `plot_route(avoid_is_law=True)` exempts the DESTINATION from the law. | — | Checked by the reader over 1,198 plots: no intermediate province across a closed frontier; a closed destination is refused at the order's issue. No change. |

**What the readers checked and found sound** (their own probes): the quote against the order on 84 random
support and follow orders and 40 random marches — no mismatch, in what halts, what is asked, the actions
spent and the men the first march costs; the road law over 1,198 plots; the forecast's arithmetic against the
resolver, the last hour applied once and to both sides, a pursuit that cannot fire twice, for the loser or
for a corps that brought nothing, a court's tally that cannot buy an action; a save and a load in the middle
of every new state of the day (a day he opened, three more clashes, the names, the count, the next battle
"the Second"); every guard set and put back; the news naming no man and no figure, and no enemy court
reading the player's sight; the digits' handling key by key; every number of §15.20 against its record file.

#### What the fixes moved — measured again on the fixed tree

- **The final tree against the measured shipped arm, three ways** (`tools/_ba4_sentence_proof.py`, forty
  ambient turns, jena and marengo; `tools/_ba4_final_tree_2026_11_16.json`): as it is, `marshals` (Murat's
  sentence) and three keys of what the player is TOLD differ — `event_log`, `pending_dispatch_events`,
  `gazette_issues`: the review's news; with the old sentence put back, those three alone; **with the review's
  news rows left untold as well, nothing — no key of the board moved.**
- **The gate's records, read again:** the ambient sweep at the shipped arm — the signature of all ten seeds
  and the census totals — and the AI-France harness on all ten seeds are EQUAL to the records of record
  (`tools/_dy_signature_ba4_x14_2026_11_16_review.json`, `_ba4_x14_census_2026_11_16_review.json`,
  `_ba4_chain_d_2026_11_16_review.json`). The band: 28 / 27 / 27 with every seam down and the bar held,
  27 / 28 / 27 at the bar of 80,000, **28 / 28 / 27 on the shipped tree** — each as before.
- **The day's sweep was not taken again:** no fix of the review touches a word's mechanics (the one that
  did was reverted), the three silent cells the band shares with it read the same, and the probe above shows
  no key of the board moved.
- **The walk of record** was shot a third time, on the tree the review left (`battle_day.py` and `utils.gd` are two of its sources): 157 shots complete, no script error, no claim failed. The scenes were staged again first — no kept seed moved and no payload's content changed. The switch-off table was not run again: `battle_acts.gd`, the walk's reader and the payloads' content are as they were when it read fifty of fifty.
- **The live client, again:** BA-4's three boards — the day 12 steps of 12, the roads 6 of 6, the old save 6 of 6 — exported again from the fixed tree; BA-3's six boards, 44 steps of 44. The parse harness: 100 scripts, 17 scenes, exit 0.
- **The captures and the four instruments, again** (`ba4_roads_and_fog_2026_11_16`, written again from the fixed tree — the record files are these): **24 surfaces** at the five sizes, 120 frames — no red row in 2,389 rows, nothing under the contrast floor in 2,376 measured, 24 surfaces of 24 fit, no cut line and no overlap. The twenty-fourth is the review's own: the attack card of a lead who already holds a day (BA4-X8), from the server's quote on the staged day — no "… commands the day", and in the warning colour "Massena's day against Archduke Charles is still open — a battle here would be a single clash, with no day of its own." Rendered in the client, not pressed on a live board: the line rides the card's existing note.
- **The suite, on the fixed tree:** 41,509 passed, 27 skipped, 20 xfailed, none failed — 11:07 at ten workers, `ruff check backend/` clean. Run twice on the fixed tree with the same count: after the review's fixes, and once more after the fifth card's capture.

#### Found in passing — not of the session, not changed

- **Three staged bombardment payloads are byte-unstable from one staging to the next** (`bombard_link`,
  `bombard_levels`, `bombard_ours`): the script's `tempers` are written in a set's order. The content is
  equal, no seed moves and the client reads them by name; the walk's record hashes the files it played.
  BA-2's; a note for whoever next touches `battle_script.py`.

### 15.22 BA-5's gate — "the finish": BA-4's open readings ruled, and the day of battle made to tell itself (November 16–17, 2026, authoritative; it amends §15.19's news ruling, §15.5.7 and §15.20)

BA-4 was committed (`1b5bc533`) and pushed. The user's word after it: **"AFTER COMMITTING PUSHING MAKE THESE
RULLINGS AND MAKE SURE THIS FEATURE ROCKS DONT FEAR DEEPR ESERWARCH ETC"** — rule BA-4's open readings under
delegation, with research, and finish the battle feature before Session H. The session opened in Plan Mode;
four questions were put to the user and the plan was approved as written.

#### What was gathered before the plan

- **Six research briefs** (designs with a light hand; what a Napoleonic commander decided in a battle; how
  auto-resolved battles are told; tabletop games with a two- or three-point hand; screen patterns for a
  decision; the shape of real days that hung). Most of it is practitioners' writing; each brief says what it
  could not verify.
- **Two blind readers** (a strategy player, a screen critic; Sonnet, knowing nothing of the game) read 29
  frames of the battle table. **The first reading:** the player — clarity 5, drama 7, **agency 4**,
  historical flavour 8, visual appeal 6, desire to see the next battle 6; the critic — **hierarchy 4**,
  readability 5, **decision clarity 4**, drama 7, polish 6. Four of their checks read "no": the verdict names
  a cause; price AND consequence stand before a command; the figures on a screen agree; a named decisive
  moment.
- The day sweep's own record re-read, the code behind every reading traced, one reviewer's map of every test
  that pins the table, and one reviewer's attack on the plan before the user saw it (three blockers, all
  adopted: five shades of reading would leak his strength and "not yet" would betray an unseen corps — three
  states, no fallback, a clamp to what is in sight; a reserve that charged a side for breaking off would teach
  standing still — only a clash that drives a side from the field pays; the pixel budget — the day's head
  moves to the band above the baize).

| Finding | Evidence |
|---|---|
| The battle's telling is liked; the decision is not | drama 7, flavour 8; agency 4, decision clarity 4, hierarchy 4 |
| A word showed its price and not what it does | the chip read "Massena presses · 1"; the odds word was computed for every press and shown only in a hover |
| Nothing said what he will do, or what decided a clash | the table showed "Cautious · his road is open" and losses |
| A day is about one word, and a point kept was worth nothing | the sweep's bot that plays by sense: 37 days, 44 words; night converted nothing |
| Two defects of what had landed (D1, D2) and four smaller (D3–D6) | found by the blind readers, each confirmed in code before a line changed (§15.23) |

#### The user's words at the plan gate (verbatim)

| Question | The user's word | What it rules |
|---|---|---|
| The reserve | "Build it; the rule picks (Recommended)" | The one rule of the game this session adds; its number by a rule written before the data (below). |
| His intent | "Yes, three states (Recommended)" | Berthier's reading of the enemy's next word: he will strike / he may strike / he will not strike. |
| Extras | "Speed for the acts (Recommended), Sounds for the day (Recommended), A marshal's days (Recommended), The ground on the table" | All four are built. |
| Battle news | "Name the commanders (Recommended)" | A great battle's news names its two commanders — ruling 5 below changes by this tick. |

#### The twelve rulings (made under the user's delegation; each one line to reverse)

| # | Reading | Ruling | Why |
|---|---|---|---|
| 1 | The AI-France harness's annexation line reads 2 on jena | **Stands as a report; no law of peace changes. One telling fix, built.** | Neither is a cut-off corps (the line I wrote of it in §15.20 was wrong, and is corrected here). *Carniola*: Britain's truce with France ran out into a signed peace and the status quo titled what each side held — the player's own law for a peace he signs (SR-1a) — under a card that said only "what each side holds is titled by the signature". *Pomerania*: Sweden took it from Bavaria and kept it at their own peace; T3-6 sends home only the ceder's homeland, and Pomerania is Prussia's — the residual that rule wrote down. It first appears on the last-hour arm, on one seed of ten; the gated line (ambient) reads 0. **Built:** a truce whose forecast ends in peace names the ground its signature would title, as a peace card already does (`diplomacy.a_truce_names_the_ground_it_would_title`: the ratifier's own forecast, after the heading, whose words stay). **Not built:** extending T3-6 to a third court's ground — a law of peace outside this row; owner Session H's gate reading: it is built before the gate is read if the ambient line ever reads above 0 (the gate's own clause, `tools/_ba4_measure.py gate`, is the test). |
| 2 | The key bar at 50,000 | **Stands** | The rule written before the data picked the lowest bar that passed. The game's battles cluster at 30–46 thousand and then nothing until 51 thousand: the bar sits at that gap, and below it the same pairs fight on consecutive turns. |
| 3 | Served campaigns are re-timed; the scripted volte-face arm holds the bar at 80,000 | **Stands** | A seeded path, measured both ways (no beat at 50,000 in forty turns; turn 25 with the bar held). |
| 4 | The five improvements added at BA-4's gate | **Stand** | Each is pressed in the client and read by the walk of record. |
| 5 | News of a battle abroad names crowns only | **Changed by the user's tick: a GREAT battle's news names its two commanders** | The table's own law is that a great battle names its commander. An ally's ordinary battle stays crowns only; no figure is ever given (`battle_news.a_great_battle_names_its_commanders`; `FOG_OF_WAR_SPEC.md` §4.4). |
| 6 | The order of battle keeps the file from Text size 120 % up | **Stands** | Measured: at 130 % two stacked corps and their captions need about 40 px more than the baize has. |
| 7 | A far corps' support order is an ordinary order | **Stands** | The day takes only the order its own table offers. |
| 8 | Murat's sentence on his card | **Stands** | It says what the rule does. |
| 9 | The card's line for a lead who already holds a day — rendered in BA-4, never pressed | **Pressed in this pass — and the press found a defect of the rule it names (BA5-X1, §15.23)** | A live board of its own (`tools/ba4_mode_c_walk.py --board oneday`). |
| 10 | BA-3's list (he draws off only by a road to his rear; a purse spent is not a wall; the field is where the last clash was fought; the Guard is a sovereign's renewed assault; the table goes on to his clash by itself; the end-turn gate stops once) | **All stand** | Each is played and pinned; the automatic advance stays, now over an honest table (D1). |
| 11 | BA-2's list (three seats and a reserve; a garrison that yields; chips send at once; and the rest) | **All stand** | — |
| 12 | BA-1: the marshal's name on the plinth | **The name stays above the men** | On the slab it would be 9 px at the fourth rank. |

#### The bar the pass is held to (written before the work)

The same blind reading, taken again on the finished table: the same two briefs, the same frame list re-shot,
two fresh readers. **Agency (the player) and decision clarity (the critic) at 7 or more**, no score below its
first reading, and the four checks both failed read "yes". If the first reading misses, one more round of
fixes and one more reading; the scores are reported either way (§15.23).

#### The reserve's rule (written before the data)

Clausewitz's reading of these battles is that the fresh reserves left at the end decide what a victory is
worth (On War, book 4, chapters 9 and 12): Borodino ended with the Guard unspent and no pursuit; Jena ended
with fresh cavalry and an army destroyed. The rule: **when a clash drives a side from the field, the victor
counts the points he still holds and the beaten side counts its own; for each point the victor holds over the
loser, the beaten lead loses a set number of men more in the pursuit.** A point the loser kept covers him.
After a cavalry leader's own pursuit, under the pursuit's laws (never below 1,000 men; halved against the Old
Fox). Nothing when a side merely breaks off or draws off, or at night. The same rule for both sides; his own
rule for spending is untouched.

The number: the LOWEST of **2,000 / 3,000 / 5,000** men a point (3,000 and 5,000 are the game's own pursuit
figures, Blücher's and Murat's) at which, over BA-3's eight seeds and its ways of playing a day: (i) the
reserve pursues on at least eight days; (ii) no way of playing is best on more than five seeds, and neither
pressing nor the Guard stops being best anywhere; (iii) of the men it takes neither side takes more than
three quarters; (iv) the band stays inside 23–28 on the commanded seeds; (v) the hand stays healthy
(§15.16's rule). If none passes it is not built. The table is reported per seed either way, with the largest
single pursuit seen (§15.23).

### 15.23 LANDING RECORD — BA-5 "the finish" BUILT November 17, 2026 (authoritative)

The plan of §15.22 was built in its order: the six defects, the server's telling, the client's table, the
reserve behind its seam, the five extras, the measure, one pass on the frozen tree, the blind reading, the
records, the session's one review (§15.24). The rules are `SYSTEMS_REFERENCE.md` §223; the finds are
`BUG_FIXES.md` §BA5.

#### What a player gets

- **The day's table is one decision block** (the second reading, below). Its head is the STAKES — each purse
  in pips and in words, his temper and road, Berthier's reading: "Massena ■■ 2 of 2 points against Archduke
  Charles ■■□ 2 of 3 · Cautious · his road is open · he may strike" — right above the words it governs; the
  band above the baize names the battle; under the head the day's rule stands in one caption line ("A word
  costs points, and he answers it. A line that breaks decides the day; two silences running, or no point
  left, and night falls: nothing decided.").
- **Every word says its price and what it does, on its face.** The lead's own words are two-line cards: the
  digit, the word and its price in points, and under it the consequence — a press, the odds the attack card
  prints and the men on each side ("odds: unfavorable — 35,195 on 49,704"); the Guard, the same and "his
  morale −10"; to dig in, what the stance is worth to THAT marshal, read from the model ("defensive stance:
  +9% if he strikes"). The other kinds stand under labels that say what they do and cost ("Another leads the
  attack · 1 point:", "The guns, no clash · 1 point:", "Bring up · 1 point:"). The exits are quieter two-line
  cards: "Massena stands / free · he speaks next", "Break off / free · the day ends; he keeps the field",
  "Leave it to Massena / free · he would press".
- **Berthier reads him.** "he will strike", "he may strike" or "he will not strike", at the end of the day's
  head. It is the rule he follows, said only as far as the player can see.
- **The day tells itself.** Under the title, the day's toll and who has the better of THE TOLL; one line a
  clash, with what told ("Archduke Charles's attack: we lost on points — 5,023 of ours for 2,333 of his; his
  weight of numbers told."); the close says whom the toll favoured or what told, what kind of day it was, and
  — for a day no clash decided — what follows ("Neither army is driven off; the fight may be renewed
  tomorrow.").
- **Every verdict names what told, and the moment that decided it.** Under the headline of any battle the
  player's marshal led: "Decided when Mack's line broke: our weight of numbers told.", "The ground told for
  him.", "An even fight."; the clash that decides a day names itself ("Decided at the second clash, when
  Mack's line broke: …"); an assault says what told at the wall ("The walls told for the garrison.").
- **The dice in one vocabulary, and whose they are:** beside the dice what was added and the sum ("+1 = 11");
  on a dark plate under them "Ney throws 10, +1 skill = 11 / the blow lands at 112% of its weight · an
  average throw: 102% / the day's fortune in strength: France +6% · Austria −8%", read when the dice have
  landed.
- **Figures that agree.** On a day's table the two counters say they count this clash ("FRANCE LOST THIS
  CLASH") while the line under the title counts the day; the guns' toll is counted as the battery fires, on
  the counters and on the band; a corps' own line runs on the band's curve; the advance's toll says what the
  march cost.
- **The extras:** a great battle's news names its two commanders; the day's beats have their sounds; a ×1 /
  ×2 switch for the acts (kept in Settings); a marshal's last six battles on his card ("His days"); the
  province's ground drawn on the felt.

#### The six defects (each reproduced before a line changed; `BUG_FIXES.md` §BA5)

| # | What was wrong | The fix |
|---|---|---|
| D1 | Our own clash's table told his answer before "His answer" was pressed | `battle_day.settle` reads the day as our clash left it; that reading rides our tableau |
| D2 | A day closed by a word with no clash showed a clash that was not the last; "View the field" opened ours though he had struck since | a day's tableau that is raised is the day's latest (`main.gd` `_the_day_raises`) — finished by the live walk, which found one road the first fix had left |
| D3 | A caption cut after one line under a shelf; Berthier's line behind a scrollbar | the verdict's room is measured with every character shaped, lent four pixels under a shelf, and holds whole sentences (the rest in an ⓘ hover) |
| D4 | The attack card printed an exact strength twice | once |
| D5 | "Night falls on an undecided field" beside a toll that favoured one side | the close says whom the toll favoured |
| D6 | The throw was written out while the dice still tumbled | the tray's lines and the caption's figure come when the dice land |

#### Found in the finish, and fixed (`BUG_FIXES.md` §BA5)

- **BA5-X1 — "one day a lead" was read after the lead's own advance** (ruling 9's card, pressed in the real
  client): a lead whose day was open, sent against another corps, won on points and advanced — the second
  battle then opened a day its card had promised it would not, and the first day vanished without a word.
  The rule is read as the lead stood when the battle began; his advance ends the first day at once, said
  with the battle that ended it; the card says so beforehand.
- **BA5-X2 — "Our squares told against us" was said of HIS squares** (three rows of the attacker's list are
  named for the defender's own asset).
- **BA5-X3 — at the shipped Text size no staged day's exits said what they do**, and the walk was green: the
  tags were the first thing the table gave up, and every staged world was a fresh campaign, so every day
  scene carried the first day's two-line lecture. Level with the buttons the exits now keep what fits, in a
  fixed order; the staged scenes say the first day's line once, as a campaign does.
- **BA5-X4 — "38,210 on large force" beside his corps counted to the man**: the card counts him as the day's
  own table does.
- **BA5-X5 — the close's "what told" never reached the table of a battle decided at once**, nor of the clash
  that decides a day: a verdict now names it.
- **BA5-X6 — under "THE FIELD IS OURS … ROUTED" Berthier said the enemy was "still in the field"**: a
  two-to-one exchange won on points that drives him off has its own three lines.
- **BA5-X7 — the frame "a chip is dim" was a table the game no longer shows**: its staged scene laid the live
  day over the opening's table though he had struck since (the first reading's critic had named it for figures
  that do not agree). The chips ride his answering clash's table.
- **BA5-X8 — the first day's "once" was said on every table of that day**: a first-open line stays on every
  payload of the turn it was first shown, and a day is fought inside one turn. It now stays on the table that
  showed it. (The fix's first form — "until a word of ours" — was wrong, and the old save's live board caught
  it within minutes: a first word given from the province's panel.)
- **BA5-X9 — a card's second line stood under the contrast floor** (4.21 to 1 on the card's ground; the floor
  is 4.5): the contrast instrument caught it on the frozen pass's captures. It has an ink of its own.

#### Departures from the plan's words (each reported; none drops a ticked item)

- **Replay and Close keep their corner.** The plan had them "small beside" the day's head. Close goes plain
  while the words are offered (the decision is the table's only primary thing), and the exits' cards stand
  beside them.
- **The head stands in the panel, not in the band above the baize** (the second reading: the stakes stood
  700 px from the words they govern). The band names the battle instead.
- **The speed switch stands in Close's room, not beside the skip hint.** The wax seal reaches that side on a
  wide plate; Close's room is empty exactly while something plays.
- **The ladder's order** is the plan's after all (the second reading): a word keeps what it does longer than
  the table keeps its own lines. Room is made in this order — the shelves, the groups inline, the day's rule,
  the last word told, the first day's line, eight pixels of the gap under the bars, the exits' cards (they
  fall to one-line chips that keep the tags that fit), the cards' second lines, the groups scroll.
- **The verdict's line is beyond the plan's letter** (its item 6 named the close): it was added when the
  staged tables were read against the bar, before the frozen pass.

#### The second reading — and the one round of fixes the plan allowed

The blind reading was taken again on the finished table (two fresh readers, the same briefs, the frames
re-shot) and **missed the bar**: agency 5 and decision clarity 5 against 7 (each up one), with the player's
drama and flavour each one under the first reading. By the plan's words — "one more round of fixes and one
more reading" — one round was built from what both readers asked for first, and no number of the game moved:

| What the readers said | What was built |
|---|---|
| "Put a one-line consequence on EVERY button"; "eleven of thirteen chips have no explanation" | the exits are cards with their price ("free") and what they do; every group stands under a label that says what its kind does, priced in points; to dig in says its number, read from the model (it is the lead's own: Ney's temper makes the stance +9%, not +15%) |
| "The decision zone is too far from its evidence … five places for one decision" | the stakes head the panel, with each purse in words; the rule stands in one caption line on every table that offers its words; the band above the baize names the battle |
| "The headline says 'it stands even', the chip 'odds: unfavorable'" | the line under the title says it is the TOLL it speaks of; a card whose figure is the table's own count says so ("by the day's count — 38,210 on 47,175") |
| "A named decisive moment, last before the verdict" | the verdict's line names the moment a line broke; an assault's says what told at the wall |
| "Night falls … the standstill is not translated into any consequence" | a day no clash decided says what follows, on its closing table; an exit says that the day ends |
| "'= 10' beside dice that show eight pips"; "fortune's sign contradicts the roll"; the dashed line through the maths | "+2 = 10"; "of its weight"; "the day's fortune in strength"; a plate under the lines |
| "Two 'losses' on one screen"; "3,152 fall … both counters show 0"; "3,470 fall" over a counter at 876; "21,994 … 21,687: two numbers for one corps"; "58 against a bar of 55" | the counters' scope; the guns' count; a cannonade counts as its battery fires; "(307 lost on the march)"; "(his march: 58, where 55 was needed)" |

Three finds of the round itself, each caught before the frames of record were shot: the dig-in card's number
was first written as the model's general +15% and the test against the model refused it; the walk's first
claim on the counters' scope read a list that never held the counters (it could not fail); and the longer
line under a triumph's headline ran two pixels under the laurels of a short headline, the march's cost left
the baize under a lead at its foot — at the shipped Text size on two scenes, and at 120 % on seven more, which the walk at the other sizes caught after the frames of record were shot (the walk of record was shot again); and at 130 % the counters' scope fell back to " LOSSES" on every day (the words outgrew the right-hand caption's box) and the longer line under the headline reached the reserve's dead on an order of battle — the caption keeps its right edge, and that line is set in the theme's Caption size where it would reach them (`BUG_FIXES.md` §BA5, rows X10 to X14).

**Filed, not fixed here** — three finds of the readings that are older than this session's own work, each
a row of `BUG_FIXES.md` §BA5 with a strict-xfail pin, heading Session H: **BA5-X15** (while an enemy corps is
still unseen on the table the strength band already counts its men), **BA5-X16** (Berthier's "narrow defeat"
is said of a defeat that cost a fifth of the corps or more (28 % in the staged case)), **BA5-X17** (a press card's men of ours are the
muster's effective weight — "105,039 on 30,557" on a field where 94,512 of ours stand).

**Suggested by the readers, neither built nor promised on any surface** (the user's to rule: the blind
reading's section below): the reserve's men beside its note (tried — there is no room beside the counter
under a triumph's laurel, and the walk refused it), a legend for the table's marks (the lead's diamond, the
pips under a plinth), a larger decision panel.

#### The reserve: built, measured, and NOT in the game

The user's tick was "Build it; the rule picks". The rule of §15.22 was built behind
`battle_day.the_reserve_pursues`, played by hand, and measured on BA-3's eight seeds by its seven ways of
playing a day, at each value of its ladder. **The rule written before the data picked none**
(`tools/_ba5_reserve_rule_2026_11_17.json`):

| Men a point | (i) days it pursued (8 or more) | (ii) no way best on more than five seeds · pressing still best somewhere · the Guard still best somewhere | (iii) of the men it took: from us / from him (neither more than three quarters) | (iv) the band | (v) the hand healthy | Largest single pursuit | Passes |
|---|---|---|---|---|---|---|---|
| 2,000 | 34 — yes | yes · **no** · yes | 101,879 / 12,000 — **89 % ours: no** | 28 / 28 / 27 — yes | yes | 5,577 | **no** |
| 3,000 | 32 — yes | yes · **no** · yes | 140,111 / 12,000 — **92 % ours: no** | 28 / 28 / 27 — yes | yes | 6,000 | **no** |
| 5,000 | 31 — yes | yes · yes · yes | 204,302 / 20,000 — **91 % ours: no** | 28 / 28 / 27 — yes | yes | 10,000 | **no** |

Per seed (days it pursued · men it took from us · men it took from him; seven ways of playing a day each):

| Seed | 2,000 | 3,000 | 5,000 |
|---|---|---|---|
| CMD-H | 3 · 13,577 · 0 | 3 · 17,577 · 0 | 3 · 25,577 · 0 |
| CMD-A | 4 · 10,000 · 2,000 | 4 · 15,000 · 3,000 | 4 · 24,829 · 5,000 |
| CMD-M | 5 · 8,886 · 6,000 | 5 · 11,886 · 9,000 | 5 · 17,408 · 15,000 |
| jena | 4 · 16,000 · 0 | 4 · 23,283 · 0 | 5 · 32,306 · 0 |
| wagram | 7 · 21,055 · 4,000 | 6 · 27,055 · 0 | 4 · 34,082 · 0 |
| lodi | 3 · 6,000 · 0 | 2 · 6,000 · 0 | 2 · 9,569 · 0 |
| eylau | 3 · 10,000 · 0 | 3 · 15,000 · 0 | 3 · 25,000 · 0 |
| friedland | 5 · 16,361 · 0 | 5 · 24,310 · 0 | 5 · 35,531 · 0 |
| **All eight** | **34 · 101,879 · 12,000** | **32 · 140,111 · 12,000** | **31 · 204,302 · 20,000** |

Per way of playing a day, at 2,000 men a point (days · from us · from him · that way's mean change in France's
provinces against the day's baseline): pressing 9 · 33,909 · 0 · −1.62; the Guard 9 · 32,032 · 0 · −1.12;
digging in 8 · 21,577 · 2,000 · −0.12; by sense 4 · 8,000 · 6,000 · −0.62; leaving it to the marshal 3 · 4,361 ·
4,000 · −0.25; standing 1 · 2,000 · 0 · −0.38; breaking off 0. Thirty of the thirty-four pursuits fell on us.

**Why.** A word costs points, so the side that ACTS spends them. A side that stands keeps his: he is covered
by them when he is beaten, and he harvests when the attack on him is thrown back. A victor who spent to win
holds nothing over the loser. Thirty of the thirty-four pursuits at 2,000 men a point fell on us, and the two
ways of playing that ACT paid most: pressing lost 33,909 men to it and the Guard 32,032, and took none of
his. It would have taught standing still — the very thing the reviewer's first objection to the plan was
meant to prevent (§15.22) — and at 2,000 and 3,000 pressing stopped being the best way of playing a day on
any seed.

**By the plan's own words — "If none passes it is not built" — it is not in the game.** The seam returns
False; no surface promises it (the Help term, the sentence in "The day's points", the last sentence of
"Pursuit" and the chips' hovers are gone); the code, its tests (with the seam up) and its measured arm stay,
so the user's one word arms it exactly as measured. Until then a point kept is worth what it was in BA-3:
the word it can still buy.

**Recommended, not built** (the user's to rule; nothing promises it): the same idea in the form the data
points to — **only the side that ATTACKED in the deciding clash pursues, with the points it still holds
itself** (a defender who throws an attack back keeps the field and does not pursue; a point the loser kept
does not cover him). It rewards winning cheaply — "press, and keep a point to harvest" against "the Guard,
to make sure" — which is what the tick asked for, and it cannot pay a side for standing. It is a different
rule and needs its own measure: the same five clauses, the same ladder, one chain (about two hours). Owner:
the user's word; its place is the head of the next battle session, or never.

#### The measure — ONE, with arms (`tools/_ba5_measure.py`; every chain run alone)

The arms are cumulative: `0` (every BA-5 seam down — it must be the commit before on every surface), `TELL`
(the rows that move no number of the game: D1, the telling's five seams and Berthier's rout line, the
truce's named ground, the news' commanders, a marshal's days, the ground on the table, the first day's
line on its first table), `ONEDAY` (BA5-X1),
`OWNWAY` (the session's review: a word's battle is its own clash), `ALL` (the tree as shipped: every rung up, the reserve parked), and `R2000` / `R3000` / `R5000`
(the reserve armed at a ladder value). Every record below is the FINAL tree's (`tools/_ba5_*_2026_11_17.json`):
the chain was run whole once more after the last backend line changed.

| Surface | Arms | Reading |
|---|---|---|
| The keyed probe (jena and marengo, 40 ambient turns, 212 keys a turn) | `0`, `TELL`, `ALL` | **identical to `1b5bc533` on every key, both seeds**; no crash |
| The commanded band (CMD-H / CMD-A / CMD-M at the game's own key bar) | `0`, `TELL`, `ONEDAY`, `ALL`, `R2000`, `R3000`, `R5000` | **28 / 28 / 27 on every arm** (the commanded script is silent on a day: the reserve never acts there) |
| BA-3's sweep of the day (eight seeds by nine ways of playing) | `0`, `ONEDAY`, `ALL` | **72 cells of 72 equal BA-4's sweep on the commit before**, at each arm — the telling and BA5-X1 move no cell |
| The same sweep with the reserve armed (seven ways of playing) | `R2000`, `R3000`, `R5000` | the table above: the rule picks none |
| The ambient ten seeds (40 turns): the DY signature and the census | `ALL` | **equal to BA-4's final tree, entry for entry** (`tools/_dy_signature_ba5_all_2026_11_17.json`, `tools/_ba5_all_census_2026_11_17.json` against BA-4's `_ba4_x14` pair: the census identical, the signature identical but for its label) — story classes 10 of 10; Hesse promoted on lodi (33) and marengo (39); the roster in two readings; `annexations_outside_aim` 0 |
| The AI-France harness (ten seeds) | `ALL` | **equal to BA-4's arm X14, entry for entry** (`tools/_ba5_chain_d_2026_11_17.json`); its annexation line still reads 2, on jena — ruling 1; reported, never gated |
| **The deploy gate** | `ALL` | **MET on the final tree: band 28 / 28 / 27, story classes 10, promotions on lodi (33) and marengo (39), the roster in two readings, no annexation outside aim on the ambient record** |

**With the telling up, no number of the game moves:** the probe is identical key for key with every seam
up; the band and the day's sweep read as with every seam down. What moves is what is told.

The R2000 record is a clean re-run: a background chain stopped mid-arm had rewritten it with the first run's
true data and every cell flagged failed; it was run again whole, alone, and is equal to the first run cell
for cell (`SYSTEMS_REFERENCE.md` §223.8).

#### Verification (each once, on the frozen tree)

- **The staged scenes** (`tools/ba1_stage_battles.py`): thirty-three, staged again from the final backend — no
  kept seed moved; every payload changed (each carries its `ground`; sixteen a `verdict_told` — two of
  the five assaults among them, the wall carried and the wall that capitulated: since the session's review a
  wall that held with no works and no edge in men names no cause; the day scenes their cards' `does`, the
  reading and the day's lines). Three scenes say
  the first day's line (`FIRST_DAY_SCENES`); the others are days as play shows them.
- **The parse harness:** 100 scripts and 17 scenes, none bad (run on the final client).
- **The walk of record** (`tools/ba1_acts_walk.py`, the window): **162 of 162 shots, no script error, no claim failed** — on the final client and the payloads above (its record hashes both: `docs/audits/ba1_client/walk_record.json`). It was shot again after the session's review and the second review of its fixes; the forty-one frames of record are that walk's.
- **The walk at the other sizes** (headless, the same payloads): 162 of 162 shots at 100 %, at 120 %, at 130 % and in the 2.0 compact view, no script error, no claim failed. Before these runs the same walks caught two faults of the review's own fixes and one older defect, each fixed and walked again: at 120 % and 130 % a locked card's hover had lost its reason (the walk's oldest claim on a dim chip), and at the shipped size and in the 2.0 view a liberation's longest line ran into the reserve's dead even alone (BA5-X34); and once the house rule's fix had landed (BA5-X35), the walk itself still knew a verdict set a step smaller only by a BBCode size in its text — it reads the label's ladder step now, with a switch-off case of its own.
- **The switch-off table** (`tools/ba2_switch_off.py`; eighty-four cases, thirty-four of them this
  session's — four added by its review, one by its final pass): **84 of 84 claims caught their fix switched off**, the whole table run on the final client. The review added four cases and the final pass one (the verdict's step smaller, read off its label under the house rule); the final pass re-anchored three on the lines its fixes moved and re-aimed one that could not fail as first written (the night table keeps every line of its close, so a table that kept only its newest rows dropped nothing there: the case now drops the line that says how the day ended). Before the second reading its whole run had read sixty-four
  of sixty-six — two stale cases, re-aimed and caught; the second reading re-anchored five cases its re-lay touched, re-aimed one, and
  added thirteen for its own claims (sixty-six to seventy-nine). One of those was owed: the walk's first claim on the counters' scope read a
  list that never held the counters and could not fail (BA5-X13).
- **The live client** (`tools/ba4_mode_c_walk.py --export`: the real `main.tscn` against a sandboxed server;
  `docs/audits/ba5_mode_c_2026_11_17/`): five boards, 41 steps, every one held, no script error, the engine's exit clean: `day` 13 (the first day's line, a word by the digit, the card and the province's panel while the day is open, the close), `roads` 6, `oldsave` 6 (a save made before the session, its day carried open), `finish` 11 (the stakes and Berthier's reading, a card's promise, D2's closing table, "His days"), `oneday` 5 (ruling 9's card, pressed — the battle now says its lead marched from his first day, and the board's own check was brought to that line).
- **The captures and the four instruments** (`ba5_the_finish_2026_11_17`: the day's surfaces, the five order
  cards, and four tables of this session — a great battle won, a defeat, the horse against his squares, the
  clash that decides a day — at the five sizes): 28 surfaces, 140 frames, no script error. Readability: 140 readings, 3,003 rows, none red, no P1 (`docs/audits/uxr0/readability_ba5_the_finish_2026_11_17.json`). Contrast: 2,990 rows measured, none under the floor (`…/uxr0/contrast_…`). Fit: 28 of 28 surfaces at 1920x1080, 3840x2160 and 5120x1440 (`…/uxr3/fit_…`). The frame census: 140 frames, no cut line, no grip or tick overlap, the verdict's gap 9.6 px at the least (`…/uxr3/frame_census_…`).
- **The sign-ability sweep** was not read again: no world-line moved (the keyed probe is identical on every
  key), so the ten arms' records of BA-4 stand.
- **The suite:** 41,797 passed, 27 skipped, 22 xfailed, none failed (11:24 at ten workers), run once more after every record was written — its first run had caught three census and ratchet tests over the whole client and the ledger (BA5-X35), each fixed, and the client's frozen pass was run again before this one.

#### The blind reading, taken again (the bar of §15.22)

Three takes — the same two briefs, the same frame list re-shot each time, two fresh Sonnet readers each
time (blind: the frames only, no source, no document):

| | Before the work | The finished table | After the one round of fixes |
|---|---|---|---|
| **Player** — clarity | 5 | 5 | **6** |
| drama | 7 | 6 | **8** |
| **agency ("the day felt mine")** | 4 | 5 | **5** |
| historical flavour | 8 | 7 | **9** |
| visual appeal | 6 | 6 | **7** |
| desire to see the next battle | 6 | 6 | **7** |
| **Critic** — hierarchy | 4 | 5 | **5** |
| readability | 5 | 5 | **5** |
| **decision clarity** | 4 | 5 | **5** |
| drama | 7 | 7 | **7** |
| visual polish | 6 | 6 | **6** |

**THE BAR IS NOT MET.** Agency and decision clarity read 5 and 5 against 7 — each one above its first
reading, and no further. Its second clause is met on the last take: no score stands below its first reading
(on the second take the player's drama and flavour each stood one under; on the third every one of the
player's six stands above its first, and the critic's five are at or above theirs). The four checks both
first readers failed:

| Check | The player | The critic |
|---|---|---|
| The verdict names a cause | yes | "yes, mostly" — a battle of other courts names none (the fog law), and a day that ends with no decision names a result |
| Price AND consequence before a command | "Price yes … Consequence only partly": the choices are "not priced in stakes" | "partly" — the groups "show a group price only and no consequence", and "Break off does not show the day's losses" |
| The figures on a screen agree | "partly … the numbers seem right" (the fortune's figure "unexplained") | no — it lists seven: one is a fault of the game (a press card's men against the band: BA5-X17, filed), one a naming two standing rulings produce together (the day's field named for two provinces on two surfaces), the others different staged battles or figures that agree when read |
| A named decisive moment | "mostly yes" | "Ulm only" — where a line broke; none on a day no clash decided |

By the plan's words the pass stops here: "one more round of fixes and one more reading; the scores are
reported either way." Nothing ticked at the gate is dropped.

**What stands between 5 and 7, in the readers' own words — levers that are the user's** (each a design
decision; none is promised to a player on any surface):

1. **A larger decision.** "Cut the table to about 210 px and give the decision panel about 310": cards at
   body size with three lines — the word and its price, the effect, the risk. The miniature is the host's
   pinned body, and BA1-X4 owns the tableau's layout.
2. **A chance in place of an odds word** — "about 8 in 10 to win the clash". A NEW figure shown to the
   player: the engine computes no such number today, and the muster's word is given only on an exact
   sighting.
3. **The stakes of the free words** — what breaking off loses, what standing risks. By the rule a day
   broken off moves nobody and costs nothing more; the readers want it said as a stake.
4. **Fewer chips on a crowded day** (sixteen at Ulm): a drawer, or three headings.
5. **Luck against margin in one phrase** — "won by numbers; the dice added …".
6. **A legend for the table's marks, and one footer on every state** (the battle's name, the speed,
   Replay and Close).

Recommended: 1, 5 and 6 as the head of the next battle session, held to this same reading; 2 is a ruling
of the user's (a new number, and what the fog lets it say); 3 and 4 follow from the room 1 makes.

#### Decisions taken under the delegation (each one line to reverse)

| Decision | Why | To reverse |
|---|---|---|
| The reserve is parked, not armed | the rule written before its data picked none | `battle_day.the_reserve_pursues` returns True — the chips' hover sentence comes back with it; Help's three sentences were removed with the promise and are not behind the seam, so arming the rule writes them again (the session's review) |
| A verdict names what told on ANY road, not only a served campaign | it is a telling, read from the battle's own report | `battle_telling.a_verdict_names_what_told` |
| "An even fight." is said where nothing stood out | a verdict that names no cause on some tables reads as a gap | `verdict_line` |
| As one-line chips the exits keep their tags in the order leave it → leave the field → stand | what the marshal would do is the least obvious of the three | `battle_acts.gd` `DAY_TAG_ORDER` |
| The stakes head the panel; the band names the battle | the second reading: the points stood 700 px from the words they govern | `battle_acts.gd` `_build_the_day` (the head's place), `_day_name` |
| The exits are quiet cards; "Leave it to him" lost its green ground | an exit costs nothing; green read as "go" | `battle_acts.gd` `_day_exit_card_bb`, `DAY_EXIT_INK` |
| The panel may take eight pixels of the gap under the bars | Ulm's table was five short of its exits' cards | `battle_acts.gd` `DAY_LIFT` |
| To dig in says the stance's worth to that marshal, read from the model | "firmer if he strikes" read as a vague adjective; a figure kept in the telling would lie for an aggressive lead | `battle_telling.does_dig_in` |
| The verdict's line names the lead whose line broke | both readers asked for the decisive moment by name | `battle_telling.verdict_line` (`broke`) |
| A day no clash decided says "Neither army is driven off" on its table, not in the campaign log's line | the log's line is BA-4's and BA-5's as it was | `battle_telling.FOLLOWS` |
| BA-4's "(58 against a bar of 55)" is reworded with no seam | a wording of the script; no rule reads it | `battle_script.py` (the three `arrive_late_own` lines) |
| The staged scenes say the first day's line once | every staged world is a fresh campaign; a campaign says it once | `ba1_stage_battles.FIRST_DAY_SCENES` |
| The first day's line stays on the table that showed it, not on the day's next | BA-4's "once" was every table of the day (a day is fought inside one turn) | `battle_day.the_first_days_line_stands_on_its_first_table` |
| The card says the table's count of him on a band, with no odds word | the figure is already on the table; the muster's word would read back what stands beside him unseen | `battle_day.the_offer` |
| A day's card draws its second line at the ONE named step rich text may take | the house rule (no BBCode size; a size is a named step) against the two-line cards; the user's "make best call"; the second line at the box's own size was measured first and kept the cards on four tables of seven | `Utils.bb_step` (and the ratchet in `tests/test_uxr2_override_diet.py` back to 0) — the cards' second line then at the box's own size |
| Ruling 1's law of peace is not extended to a third court's ground | outside this row; the gated line reads 0 | build T3-6's extension before the gate is read if the ambient annexation line ever reads above 0 |

#### Owned by the session after this one

- **Session H (S15, the deploy)** — its head's open rows are the ones it had, less BA1-X8 (closed here), and three
  more of this session's filing: UI6-X70, X73, X74, X75; the weak-spot review's six (WS-10, WS-12, WS-13,
  WS-14, WS-15, WS-R); **BA1-X4**; BA2-X6; BA2-X16; **BA5-X15**, **BA5-X16**, **BA5-X17**. Its gate reads against this session's records (`tools/_ba5_*_2026_11_17.json`,
  `tools/_dy_signature_ba5_all_2026_11_17.json`, `tools/_ba5_all_census_2026_11_17.json`).
- **The reserve** — no surface promises it, so nothing is owed to a player. Owner: the user's word. Landing:
  the head of the next battle session, in the recommended form, after that form's own chain — or the measured
  form armed as it stands — or never. Done when: a form passes the five clauses of §15.22 on its own records
  and the user says to arm it. Tracking: `STATUS.md` "Open with you". Behaviour test:
  `tests/test_ba5_the_finish.py::TestTheReserveIsParked` (it fails the day the seam is armed, so the arming
  and its records land together).
- **Not done here, each with its reason:** BA-3's six live boards were not walked again (their tool reads
  BA-3's panel — BA2-X16's family, Session H's; the day's road is walked on the finished client by BA-4's
  `day` board and this session's `finish` and `oneday`); the DD-1 sign-ability sweep was not re-recorded (no
  world-line moved: the keyed probe is identical on every key, so the ten arms' records stand).

### 15.24 BA-5's review — six readers on a frozen copy, and a second review of its fixes (November 17, 2026, authoritative)

The session's one review ran BEFORE any commit, on a frozen copy of the tree outside the repository
(the session's commit is the user's to ask for): six Sonnet readers, one lane each (the server's
telling, the fog, the day's mechanics, the client, the reserve and the measure, the records), and a
completeness critic whose second round sent five more readers to what the six had not covered. Each
of the **34 findings** was put to three skeptics — one to reproduce it, one to refute it, one to say
whether a player can reach it — and every finding upheld was reproduced again before a line changed.
Thirty were confirmed, two contested and two refuted.

**What it found, and what was done** (`BUG_FIXES.md` §BA5, rows BA5-X18 … X33; every fix pinned in
`tests/test_ba5_the_finish.py::TestTheSessionsReview`, and every test of the review's fixes but one
fails on the frozen copy the readers read — the one pins the law the fog's fix keeps and held there too):

| Row | Sev | The defect | Seam |
|---|---|---|---|
| X18 | P2 | a corps thrown back earlier in the turn was told as breaking in a battle it held | `battle_script.a_rout_is_one_this_battle_made` (TELL) |
| X19 | P2 | the reading at full sight read the enemy's unseen fitness; "Leave it to …" read his true field | the reading's own (TELL) |
| X20 | P2 | a second battle's table said the first day "is still open" while the same response closed it | — (the telling) |
| X21 | P2 | an objection answered "his own way" against another corps took the word's effects | `battle_day.a_words_battle_is_its_own_clash` (OWNWAY, its own rung) |
| X22 | P3 | a battle that ruined both armies was decided for the attacker | the close's own (TELL) |
| X23 | P3 | "our reserve was never spent" over a spent purse | the close's own (TELL) |
| X24 | P3 | "the walls told" at every wall that held; numbers judged on one set of figures | the verdict's own (TELL) |
| X25 | P3 | a clash with no point for it was counted and never told | the day's clashes (TELL) |
| X26 | P3 | the dig-in figure left out the drill the order ends; a refused card printed one | the words' own (TELL) |
| X27 | P3 | the reserve's beat called the difference of two purses "the point he kept" | the parked reserve |
| X28 | P3 | a marshal's days listed by the order they were kept, not by turn | the days' own (TELL) |
| X29 | P3 | a closing table could crowd out the line that says how the day ended | — (the client) |
| X30 | P3 | a locked card's hover left out what the word would do | — (the client) |
| X31 | P3 | the line under the headline ran off the baize at 130 % | — (the client) |
| X32 | P3 | at the baize's foot the march's cost was dropped, and the walk's claim was exempt there | — (the client) |
| X33 | P3 | nine places where the records said more, or other, than the code and the measure | — (the records) |

**Not upheld, with the reason:**

- *A first day that a strategic order's advance ends inside the turn's order pass is not carried to the
  morning's events* (#5). By design (§15.22's "one day a lead"): the day ends at once and is told with
  the battle that ended it — on the order's own message and in the campaign log; no day goes untold.
- *A clash against the enemy of another lead's open day is filed on that lead's record* (#24). By BA-3's
  design a battle against the day's enemy on its field IS a clash of that day (another corps leading is
  one of the day's own words), and the day and its record belong to its lead, as every surface of the day
  names him.
- *The laurels' layout touches the chrome after an await without a guard* (#33) and *a published "he will
  strike" can be falsified by the player's own next word* (#34): refuted by all three skeptics — the
  stage, the banner and the line under it are built once and never freed, and the table is shown and
  hidden, never freed; the reading is of his next word as things stand, and its hover says a clash
  changes it.

**Upheld, and recorded rather than changed:** *the rule's clause iv cannot fail and clause v omits the silent
script's bound* (#19, one of the thirty confirmed) — the rule was written before its data and is not
rewritten after it. Clause iv reads the silent
  commanded script, which never speaks on a day; clause v leaves out §15.16's ±1.5 for that script.
  Neither moves the pick: clause iii failed at every value of the ladder.

**The second review — of the fixes themselves.** The diff of every fix (frozen copy against the working
tree) went to five fresh Sonnet lanes (the telling, the fog, the day, the client, the tools), each
finding to two skeptics (one to reproduce it by a probe, one to refute it), and a completeness critic
over all five. **Seven findings:**

- four fixed, each pinned by a test that failed on the tree it was found on: numbers at a wall judged on
  the effective figures alone named the ground's quarter as men (X24 now asks the men AND the fight's
  figures); a ruin whose last word was the Guard was told "the Guard went in and was thrown back" (X22: a
  day decided for neither says "Neither army kept the field."); the word's line on the tableau still read
  the running word raw, so a battle on another corps opened with "Ney presses the attack." (X21:
  `word_line` through `_word_for`); the walk's claim that the line saying how a day ended is ON the table
  read the labels' sources, where the head's hover rides (X29: it reads the rows' own text);
- one weighed and kept: *Berthier's "will" turns to "may" on the enemy's unseen fitness*. It does, by the
  law as ruled at the gate (`FOG_OF_WAR_SPEC.md` §4.4: anything that turns on his fitness or on a state out
  of sight reads "may"). The other choice — the word sight alone gives — would publish a "will strike" the
  rule then breaks, the class of #34. One bit stays readable, the price of a certain word that is never
  falsified; the spec and the code now say so;
- two that were the records: the measure's tests of record failed on a ladder that had gained ROUT and
  OWNWAY (the sweeps of arms 0 and ONEDAY had been read on an older tree — X33), cured by re-taking every
  record on the final tree;
- the critic named no fix left unexamined; the rout's fix, the campaign log's comment and the client's
  rows were read without a probe, and the walk of record and the switch-off table press the client's.

**The measure, re-taken on the final tree** (the review moved two seams and the rule's baseline; the
chain was run whole again, ALONE against backend and tool edits, every sweep re-taken — arms 0, ONEDAY and
ALL and the reserve's three — so the rule is read off records of one tree): the keyed probe identical to `1b5bc533` on every key at arms 0, TELL and ALL (both seeds); the band 28 / 28 / 27 on all seven arms; the day's sweep 72 cells of 72 at 0, ONEDAY and ALL; the reserve's three readings as before to the man — 34, 32 and 31 days; 101,879, 140,111 and 204,302 of ours against 12,000, 12,000 and 20,000 of his — and the pick still none; the ambient record and the harness equal to BA-4's final tree; **the deploy gate MET** (story classes 10; Hesse promoted on lodi 33 and marengo 39; the roster in two readings; no annexation). 92 minutes

**The client, pressed again on the final tree:** the staged scenes staged again (sixteen of thirty-three carry what told; the walls that held with no works and no edge in men now name none); the parse harness clean (100 scripts, 17 scenes); the walk of record 162 of 162 shots, no claim failed, and the same walk at 100 %, 120 %, 130 % and in the 2.0 view; the five live boards, 41 steps of 41; the captures under the four instruments clean; the switch-off table 84 of 84 caught. These runs were made four times more than planned: the first caught a locked card's hover without its reason (a fault of X30's first form) and the night table's switch-off case that could not fail; the second a liberation's longest line over the reserve's dead at the shipped size (BA5-X34) and the live board's own check of the line X20 changed; the third was clean, and the full suite's census then found the house rule broken in the client (BA5-X35); the fourth, on the client with the named step, found the walk's own reading of a verdict set a step smaller out of date (it reads the label's step now, and the check has its switch-off case); the fifth — the walks, the walk of record and the whole switch-off table — is the record

**The full suite's own census** (its first run after everything else): three tests read what no session test had — the house rule against a BBCode size and a one-off grey over the whole client, and the score census's pillar on every open row. All three were the session's: the second reading's cards set their second line a step smaller with a BBCode size, the day's rule line and the verdict's fit did too, two greys stood in the acts' own file, and BA5-X15 carried a pillar the census does not know. The rule line and the verdict's fit now take ladder steps of their labels, the greys are the palette's, X15's pillar is one of the census's. The cards were the user's call — the house rule against the two-line design — and the answer was "make best call": the second line at the box's own size had been measured first and cost the cards on three tables of seven, so a day's card draws its second line at the ONE named step rich text may take (`Utils.bb_step`, the theme's Caption step read live), and the ratchet counts that one helper (row BA5-X35). The client's frozen pass was run once more on that client, and the suite again.

**The commit's own suite** (the pre-commit hook) then met a flaky test older than the session — the B4B board's insisted order defied on some rolled campaigns (row BA5-X36): its defiance roll is pinned like its concern and mood, and the commit went through the hook again.

**The suite, once more, after everything:** 41,797 passed, 27 skipped, 22 xfailed, none failed (11:24 at ten workers), run once more after every record was written — its first run had caught three census and ratchet tests over the whole client and the ledger (BA5-X35), each fixed, and the client's frozen pass was run again before this one.

**The ladder after the review** (`tools/_ba5_measure.py`): `0` → `TELL` (now with the rout's seam) →
`ONEDAY` → `OWNWAY` (a word's battle is its own clash: the one rung after ONEDAY that can move a number,
on that one road) → `RESERVE` (alias `ALL`, the tree as shipped: the reserve parked) → `R2000` / `R3000`
/ `R5000`. The rule's reserve-down baseline is the sweep at `ALL`; `ONEDAY` now holds OWNWAY down too.
