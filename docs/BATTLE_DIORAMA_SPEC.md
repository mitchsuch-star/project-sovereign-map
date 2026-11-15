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
when it breaks or destroys its target.

**15.5.5 The plan of battle, from the orders the game already has.** No new modifier and no new
order. Act I names the plan the player's orders amount to (the lead, the corps ordered in support,
the provinces the attack comes from and the flank's +N on the dice, a drilled assault, stance,
guns in support); the attack row of the province panel and the muster card carry, per nearby
corps, a chip for the existing order that would bring him, priced on its face.

**15.5.6 The crisis — the Emperor's word.** Asked on a field battle the player ordered, where the
Emperor stood on the field and the day hangs (both leads standing, the enemy still on the field).
One order — Press (the lead renews the assault), The Guard (the Emperor's own corps attacks), Hold
— and the lead answers by temperament through the systems that already exist: the concern
evaluators, the insist penalty and trust gain, the defiance chance, roll and fallback, "By my
word", vindication. New numbers: the Guard's two morale effects (the enemy lead −10 as it goes in;
every French corps that fought −10 if it is beaten), which close NP-D1. Not built: a council on
defence (the enemy phase cannot stop, and by the next turn the board has reset), and marshals
settling a hanging day alone (it would move every measured arm). The courts' rule is written and
dormant (no court fields a sovereign).

**15.5.7 The two rule changes.** A pursuit ability fires for a corps commander who ARRIVED when
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
| **BA-2 — the walls, the guns and the order of battle** | §15.5.4, §15.5.5 | an assault and a bombardment each render a tableau on both roads; the plan is named in Act I and orderable at the attack row |
| **BA-3 — the crisis** | §15.5.6, §15.5.7 | the council asks, answers and plays on; NP-D1 closed; both rules behind function seams; ONE measure with arms (all seams at HEAD's answer byte-identical on the standing series, then each rule, then the crisis answered each way), reported per seed |

BA-2 and BA-3 each open in Plan Mode with their own slice plan. Three questions go to the user at
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
`tests/test_ba3_the_crisis.py` — the council rises only where §15.5.6 says, each answer goes
through the objection road and the battle plays on, the pending slot round-trips and an old save
reads empty, the Guard's two morale numbers, the pursuer among the arrived, the last hour's three
quarters; and `tests/test_ws16_the_same_order_draws_the_same_temper.py` — an order insisted on
again from the same save draws the same mood and the same defiance (WS-16's done-when).

### 15.8 Decisions taken under the delegation (each one switch or one line)

The crisis is the objection system staged at the hinge of a battle, and only the lead's trust is
at stake; it is asked where the Emperor stands; the plan of battle adds no numbers; the Guard's
rule is two morale numbers; plinth pips are six; a concealed enemy plinth is turned up on arrival;
the brief form runs about six seconds and the full form about sixteen to twenty.

### 15.9 Left with the user

Blücher's "Vorwärts!" in the 1805 game (not ticked, not built); a riposte council on defence; the
marshals' own settlement of a hanging day. Open rows are not closed silently: WS-13 ("outnumbered"
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
