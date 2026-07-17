# Battle Diorama — Creative Evaluation

*Prepared for the project lead · Fable review pass · unblessed spec `docs/BATTLE_DIORAMA_SPEC.md`*

> **Provenance.** Grounded, adversarially-verified evaluation run July 17, 2026 (18-agent workflow:
> 4 code-grounding readers → 4 creative lenses → 9 adversarial verdicts against the live codebase →
> synthesis). Every reuse/asset/cost claim in the spec was checked against source; the reality-check
> table (§3) records what HOLDS vs what was INFLATED/FALSE, with file:line evidence. An interactive
> **Tier-A hero mockup** (the Austerlitz coalition frame) was built alongside this memo — see the
> published artifact linked from `BATTLE_DIORAMA_SPEC.md` §6. The mockup fakes the `contingents[]`
> data on purpose; §3/§6 record that the build *behind* that still frame is a modest backend slice,
> **not** the "near-zero" freebie the spec advertises.

---

## 1. Verdict

**Build it — but as a significance-gated, honestly-costed slice with a real (modest) backend half, not the "near-zero" frontend freebie the spec advertises. The coalition tableau is the only thing here text genuinely cannot do; everything else is garnish on an already-adequate surface.**

**Fun rating: 7/10** — genuinely trophy-cabinet cool on the ~15–20% of battles that are decisive, involve a player marshal, or earned a dynamic name; a friction speed-bump on the rest, which is exactly why the significance gate is a definition-of-done item and not polish.

---

## 2. The fun thesis

The fun is real, sharply **non-uniform, and front-loaded**. It is not spread across battles — it lives in two places, and the design must aim all its money there.

**The fun curve, by battle kind:**

- **Decisive player-marshal win — peak.** The topple cascade *is* the reward. "Ney *shattered* Mack" wants to be seen, not read. A face on the winning corps, a standard tipping across the centre line, the odometer ticking to 21,400 as the line folds — this is the single frame the whole feature exists to earn.
- **Coalition / multi-army battle — peak, and irreplaceable.** Mixed standards + a greyed no-show block say in one glance what three sentences bury: *which* nation's corps broke, who withdrew, who never came. This is the one read that text structurally cannot deliver. It is the feature's raison d'être.
- **Routine skirmish (2k-vs-1k raid) — trough, and it decays fast.** Novelty rots into tedium within an hour of live play. The sixth auto-played tableau of a minor raid is a speed-bump, and the net fun delta on these goes **negative**.

**Why significance-gating is the load-bearing design decision.** Because the curve is bimodal, the single most important line of code in the feature is the predicate that decides whether the tableau auto-plays at all. Ungated, the feature is a net negative on the majority of battles and sours the whole thing. Gated — full tableau only for decisive results, player-marshal battles, or W6-2-named battles; everything else stays text behind a `⚔ View the field` button — it stays a reward. This is not optional polish; it belongs in the DoD, and its inputs (outcome, victor, battle name, participant nations) already ride the serialized `events[0]` payload, so it is cheap to build.

**Is §12 right?** Substantially yes — §12.1's core "very high on the marquee case, flat-to-negative on routine" thesis is correct and is the spine of this evaluation. But §12 must be corrected in three places before a gate leans on it:

- **§12 under-sells the justification and over-sells the ease.** The fun and the cost live in the *same place*: the irreplaceable coalition payoff is precisely the expensive backend half. This is not a cheap win, and §5/§7/§11.4's "nearly free in Tier A" framing inverts it.
- **§12.3's causal claim is backwards.** "The battle visibly *causes* the jealousy beat" is false in the code — a grievance drives a no-show, never the reverse (see §3). Reframe to "the grudge that explains the gap."
- **§12/§2's rationale is stale.** The feature is pitched on combat-legibility 4.5 / narration 3.5, but **Wave 6 already lifted both to 7 / 7.5, both MET**. This is a *delight-multiplier on an adequate surface*, not a pillar rescue. That is a legitimate thing to build — but the gate must weigh it on those honest terms against Nation Agendas (the competing 8.5 centrepiece), which targets a genuinely thinner enemy-motivation gap.

---

## 3. Reality check — load-bearing claims vs. the code

This is the section that keeps the gate honest. Each claim marked **HOLDS / PARTIAL / INFLATED / FALSE** against the verified codebase, with the corrected cost.

| Claim (as the spec frames it) | Verdict | Corrected reality & cost |
|---|---|---|
| Outcome + victor are in the player-facing payload | **HOLDS** | `events[0]['outcome'\|'victor']` (combat.py:945-946 → combat_executor.py:4787-88). Zero work. |
| Per-side casualties / original / remaining / morale are in the payload | **PARTIAL** | True **for the two lead marshals only** (`casualty_summary`, `events[0]['attacker'\|'defender']`). Reinforcing corps figures are never itemized on the surface. |
| A lead-vs-lead modifier snapshot is in the payload | **HOLDS** | `modifier_snapshot` → `battle_report.modifier_breakdown`. Lead-attacker-vs-lead-defender only. Zero work. |
| A structured per-contingent breakdown already rides the fog-filtered surface | **FALSE** | The identifier `contingents` appears **nowhere** in the backend. Must be assembled from scratch. |
| Per-contingent committed strength is available | **FALSE** | Only an **aggregate weighted-effective float** exists (`_committed_reinforcement_strength`), surfaced solely as prose. No per-corps or raw-men figure. Must capture pre-distribution strength for all participants (extend the `_co6_lead_pre_strength` snapshot, combat_executor.py:4000) *before* `take_casualties` mutates it. |
| Per-contingent arm (inf/cav/art) is in the payload | **FALSE** | In no payload. Derivable from `marshal.cavalry`/`.artillery` (pattern marshal.py:1728) — new, if trivial, work per corps. |
| Per-contingent nation is available | **PARTIAL** | Only the two **primary** nations. Coalition per-corps nation must be read off `marshal.nation`. |
| Per-corps status (engaged/reinforced/routed/withdrew/failed_arrive) is available | **PARTIAL** | `reinforced`/`failed_arrive` exist internally (prose only); `routed` = `forced_retreat` is **primary-pair only**; **`withdrew in good order` is unmodeled anywhere** (the Kutuzov beat is fabrication if shipped). |
| `casualty_distribution` gives per-marshal casualties for reuse | **PARTIAL** | The dict is **set at combat_executor.py:4225 and never read** — dead for display. Wiring it (and registering it) is required to reuse the numbers. |
| "Zero or near-zero new backend work" for the whole feature (§7) | **INFLATED** | Holds **only** for a 1-v-1 tableau of the two leads. The multi-army flagship — the feature's own justification — is a real **medium** backend slice: assemble `contingents[]`, derive arm, capture per-corps committed strength, wire the dead casualty dict, add per-reinforcer status, fog-filter the enemy side, and register the field in `main.py`'s `_COMMAND_RESULT_SIMPLE_FIELDS` (352-368) **or it is silently dropped**. |
| 37 PD marshal portraits exist and are reusable to head each block | **HOLDS** | 37 Wikimedia PD portraits in `assets/portraits/`, already wired via `marshal_management.gd`. Caveat: name-keyed with a **gold-monogram fallback** (Abdurrahman by design; recruited `marshal_pool` marshals may exceed the 37) — reuse the monogram path, don't assume a face for every corps. Small, not zero. |
| CC0 cannon/drum sting is downloaded, cleared, drop-in (§12.4) | **PARTIAL** | Cannon is real and CC0-cleared (`cannon_*.ogg` inside `opengameart_25-CC0-bang-sfx.zip`); **a dedicated drum/fife sting is a documented gap** (approximated from the RPG pack). Everything but 2 parchment WAVs is still **zipped** — extraction + Godot import + license-log needed. And `THIRD_PARTY_LICENSES.md`'s "198 WAVs force-tracked" is doc-drift (2 on disk). Zero new *acquisition*; not zero *work*. Cost as small. |
| Dynamic battle names (W6-2) can be engraved on the nameplate | **HOLDS** | `compose_battle_name` produces finished text, stamped on `battle_result['battle_name']` and flowed to the client on `events[0]` independent of the whitelist. Caveat: composed **only for `resolve_battle` field battles** — garrison assaults / bombardments have no name to engrave. |
| A coordination no-show creates a jealousy grievance the diorama can surface (§12.3) | **FALSE / inverted** | A no-show docks **−3 trust only** (combat_executor.py:5008-21); it creates **no grievance**. Grievances are minted **solely** by the glory-ladder gap in `process_turn → apply_jealousy`. Causality runs the other way: a **pre-existing grudge** (derived −1 in `get_relationship`) worsens the arrival roll and makes the no-show more likely. Both `jealous_of` and the "failed to arrive" copy are separately-existing display data — surface them as **grudge-explains-gap**, never battle-mints-grudge. |
| `glory_crowned` gives a per-battle victor crown | **PARTIAL** | Real display data — but a **per-nation, turn-boundary #1 marker** (`recompute_crowns`), reflecting the **pre-battle** ladder. Show it as a standing laurel the marshal already wears, never as a crowning this fight triggered (and the battle victor may not be the crowned marshal). |
| Faction color is on coats; "mixed coat colors" is the coalition read (§5/§6/§12) | **FALSE** | The shipped art is **carved wood, not tin** (`gen_war_table_pieces.py` July-13 rework; the `war_table_piece.gd` "tin/pewter" docstring is stale). The one faction-colored element on a figure is **its standard** (+ base-rim band); the coat mass is oak. "You see which nation's coats broke" is impossible. Relocate the read to **standard + base-rim + portrait locket**. |
| Coalition multi-tint "works for free" | **INFLATED** | The coat-only tint *mechanism* is real and reusable, but multi-tint is an **unchecked** Tier-A DoD item; `_legible_tint`'s VALUE_FLOOR 0.5 was tuned for single map standees and is **untested** against two faction tints side-by-side (Austria off-white next to a pale ally). Cheap to fix, but must be eyeballed before "done." |
| Falling/captured standards + cascade-topple are pure Tween on static art, Tier-A-safe | **HOLDS** | Confirmed feasible: `war_table_piece.gd` already drives `create_tween`/`tween_property`; rotate+opacity topple, staggered cascade, and a sliding glyph are all zero-animated-art. The falling standard is a static Unicode glyph — lighter still. |
| Significance-gating is a cheap predicate that solves repeat-viewing fatigue | **PARTIAL** | Predicate is cheap (HOLDS). But it solves **auto-play novelty decay across battles**, not **repeat-viewing fatigue** (re-watching the *same* battle from the log) — that is a *separate* mechanism: render the final frame **instantly, no sequence, skippable**. Ship both. |

---

## 4. The creative additions, ranked by fun-per-cost

Deduped across all four lenses. Tags: **trivial / small / medium**. "Tier-A-safe" = no animated art and no new payload field beyond the one contingents slice.

| # | Idea | Size | Tier-A-safe? | Why it earns its place |
|---|---|---|---|---|
| 1 | **Falling / captured standard.** Tilt+drop the corps standard on a rout; on a decisive rout, tween it across the centre line ("the eagle taken"). | trivial | ✅ | The most emotionally legible single beat in the feature and the iconic Napoleonic image — and **best-grounded of all**: the standard is literally the only faction-colored element on a figure, so dropping it is the strongest color-moment available with zero new art. Lead with it. |
| 2 | **Significance gate + instant-final-frame on repeat.** Auto-play only for decisive / player-marshal / W6-2-named battles; else text + `⚔ View the field`; repeat/log views render the final frame instantly. | small | ✅ | The anti-tedium keystone. Not polish — it's the difference between delightful and "why is this popping up again." Predicate reads existing `events[0]` fields. |
| 3 | **Marshal portrait lockets.** Sepia/duotone-washed face in a brass oval crowning each block; crack/desaturate on rout; ★ crown on the rim of the standing glory-#1. | small | ✅ | The move that crosses *legible → my generals*: you watch Ney's line break, not a blue block. **Requires the duotone+brass treatment** — raw JPG faces on carved oak are the biggest material clash in the feature. Monogram fallback for portrait-less marshals. |
| 4 | **Engraved brass nameplate** at the tray foot carrying the W6-2 name ("The Slaughter at Ulm"). | trivial | ✅ | Rewards the naming system with a visible home; sells the diorama-as-object metaphor. Finished text already in payload. |
| 5 | **Odometer casualty tiles** ticking 0→21,400 as the figures topple. | trivial | ✅ | Binds the number to the fall — the count and the collapse become one event. Keep on the **two leads** (per-corps ticks wait on the contingents slice). |
| 6 | **Fixed topple verb + one-flank cascade.** Toppled = rotate ~78° **AND desaturate+darken AND a fresh long shadow, base stays put** — not opacity-0.3. Cascade the primary loser's flank with staggered tween delays. | small | ✅ (primary side) | opacity-0.3 alone reads "ghost/deleted" and breaks the core visual sentence; the cascade timing makes CO-3 decisiveness finally *visible* — a rout, not a grinder. Per-corps cascade waits on contingents. |
| 7 | **Berthier's verdict last.** The `observation` line fades/types in **after** the topple settles — the closing gavel. Terse, once. | trivial | ✅ | Turns the dry after-action voice into the punchline. Treat any CR-5b victor boast as optional garnish (delegation+live-mode only — don't hard-depend). |
| 8 | **Carved-wood tray staging.** Green baize ground, gilt ornament frame, wax-seal brass nameplate; one warm raking key from upper-right, long shadows. Color rarity as a rule (wood everywhere; faction hue only on standards + base-rim; red only in the casualty tally). | small | ✅ | The entire anti-"colored-blocks" move — and the assets already do 80% of it. See §8. |
| 9 | **One cannon thud on reveal + one drum sting on a decisive result**, mute-respecting, single `AudioStreamPlayer`, no bed loop. | small | ✅ | Percussive reveal is outsized feel-per-effort. Budget the zip extraction; drum is an approximation until a real sting is sourced. |
| 10 | **The `contingents[]` backend slice + enemy-corps fog visibility.** Assemble from `atk/def_participants`, derive arm, per-corps nation, pre-distribution committed strength, wire the dead `casualty_distribution`, fog-filter the enemy side, register in the whitelist. | **medium** | ✅ (it *is* Tier A — the cost centre) | This is what makes the coalition case — the whole justification — have data to render. **Bless it explicitly as its own backend slice, not "nearly free."** |
| 11 | **Motivated no-show → the existing grudge.** Greyed off-line "Bernadotte — failed to arrive"; where he carries `jealous_of`, surface it as the *reason* ("he resents Davout's glory"). Off-baize on a reserve shelf reads even better. | small | ✅ | The gap in the line gets a face and a grudge. **Reframed** per §3 — grudge as cause, never "this battle minted it." |
| 12 | **Terrain backdrop strip** + fort crenellation silhouette behind a fortified defender. | small | ⚠️ (needs a new/derived payload field) | "Where it was fought" for free-ish. Gate-optional; first to cut if over budget. The fort silhouette is honestly tied to real `fortification_*` flags; the terrain band needs a payload field it doesn't have today — defer as a named follow-up, don't auto-fold. |
| 13 | **Lone glory-attack composition.** When a marshal charged solo out of jealousy, draw his block standing alone — the ambition *is* the composition, explaining the bad odds wordlessly. | small | ✅ (leans on contingents) | Character legibility for free once contingents exists. |

---

## 5. What to cut / de-risk

- **"Withdrew in good order" status** (Mock 2's signature Kutuzov beat) — **CUT**. Unmodeled anywhere in the codebase; shipping it is new mechanics-adjacent work presented as a free tableau state. Ship `{engaged, reinforced, routed(primary), failed_arrive}`. If wanted, it is a separate named combat-model row.
- **The "battle *causes* the jealousy beat" framing (§12.3)** — **CUT the language.** Causality is inverted in the code. Reframe to "the grudge that explains the gap." A neutral "Davout resents Bernadotte" info line is the most it may honestly say.
- **"Zero / near-zero new backend work" (§7) applied to the whole feature** — **RELABEL.** It holds only for the 1-v-1 two-leads path. Sell the slice as *Godot tableau + one modest backend slice*, up front, so there is no mid-build surprise.
- **Proportional / one-dot-per-1000 figure counts (§10.3)** — **CUT.** Keep the fixed per-corps cap (~8–10) + a "+2 corps in reserve" tail summary. Proportional is a layout-overflow tarpit and a GR8 scale hazard, and per-corps committed strength isn't even in the payload to size it by.
- **Per-corps cascade-topple in slice 1** — **CUT to primary-side only.** Per-reinforcer rout isn't in the payload until contingents lands.
- **The word "tin" and any colored-rectangle fallback** — **CUT.** The art is carved wood with baked relief; reuse the real pieces or don't ship. "Mixed coat colors" as the coalition read goes with it — relocate to standard + base-rim + locket.
- **Untreated raw JPG portraits** — **CUT** unless they get the duotone + brass-locket treatment this slice. Photographic faces pasted on toy-wood is worse than no portraits; drop to a later pass rather than ship the clash.
- **Battle Gallery (§12.5)** — **stays OUT, gated separately.** Its persistence question is unanswered; folding it in is exactly the open-ended "battle animation backlog" §10.5 warns against.
- **All of Tier B (fire/fall poses) and Tier C** — **HOLD until Tier A is measured live** (§11.3). No CC0 pack of animated Napoleonic infantry exists; Tier B means buying LPC ShareAlike or hand-drawing via the Pillow pipeline. A Tier-A bless must not pre-commit that.
- **Ambient audio loops / multiple stings** — one thud + one decisive sting, mute-respecting. No bed loop.

**Two de-risk musts before "done":**
1. **Fog is correctness, not effort.** The enemy `contingents[]` needs new visibility logic; a bug here leaks enemy corps composition/arm/strength — a fog-boundary violation, a recurring bug class in this repo. Behavior-test at PARTIAL vs FULL visibility.
2. **Coalition multi-tint legibility is untested.** Eyeball two faction tints side-by-side over the navy panel against the `_legible_tint` 0.5 floor before calling it done.

---

## 6. The bounded Tier-A slice (gate-ready, GR9-clean)

**One slice = one backend half + one frontend half + one test. The DoD's own multi-army fog case *contains* the expensive half — you cannot ship the cheap 1-v-1 and honestly claim the DoD, so both halves are in by definition.**

**IN — backend (`contingents[]` builder, display-only):**
- Assemble `contingents[]` from `atk_participants`/`def_participants`.
- Derive `arm` from `marshal.cavalry`/`.artillery` (pattern marshal.py:1728); `nation` from `marshal.nation`.
- Capture per-corps **committed strength before `take_casualties` mutates it** (extend the `_co6_lead_pre_strength` snapshot at combat_executor.py:4000 to all participants).
- Wire the already-computed-but-dead `casualty_distribution` (combat_executor.py:4225) for per-corps casualties.
- Per-corps `status` **limited to the four states with data**: `{engaged, reinforced, failed_arrive, routed(primary-pair-only)}`.
- **Fog-filter the enemy side** (enemy corps present only at appropriate visibility).
- **Register `contingents[]` in `main.py` `_COMMAND_RESULT_SIMPLE_FIELDS` (352-368)** or it is silently dropped.

**IN — frontend (`battle_diorama.tscn`/`.gd`, new, extends `PopupBase`, registered via `dialog_manager` at a free CanvasLayer, modal):**
- Significance-gated auto-play; `⚔ View the field` for the rest; instant final-frame on repeat/log views (skippable).
- Carved-wood tray staging; capped figures + tail summary; portrait lockets (with monogram fallback); falling/captured standards; odometer tiles (two leads); engraved nameplate; primary-side cascade-topple with the fixed topple verb; Berthier verdict last.
- Coalition read via standard + base-rim + locket; no-show block greyed (reserve shelf).

**OUT (each a separate named row, none folds in for free):** withdrew-in-good-order status; per-corps rout; clickable-grievance beat beyond a neutral info line; proportional counts; terrain backdrop field; Battle Gallery; Tier B/C; ambient audio.

**Definition of Done:**
- Boots clean (grep `SCRIPT ERROR` on the `.gd`-touching slice — standing rule).
- Significance gate live and in the DoD (not polish).
- Repeat views instant + skippable.
- Enemy contingents fog-correct at PARTIAL vs FULL.
- Coalition multi-tint eyeballed against the `_legible_tint` floor.
- Audio: one cannon thud + one decisive sting extracted, imported, license-logged; `THIRD_PARTY_LICENSES.md` "198 WAVs" drift reconciled.

**The one test:** `tests/test_battle_diorama.py` — covers **single-army AND multi-army, fog-filtered** (enemy contingents present only at appropriate visibility), plus the significance predicate (decisive / player-marshal / named → auto-play; routine → text) and the contingents-serialization round-trip through the whitelist.

**Named landing:** a new `Battle Diorama (Tier A)` row in ROADMAP.md Current Phase Queue + a STATUS.md tracking line — the feature has neither today. Sequenced **after** the Fable econ pass and behind a USER DESIGN GATE, weighed against Nation Agendas.

---

## 7. Answers to the spec's five open questions (§10)

1. **§10.1 — Auto-play for every battle, or opt-in? And repeat-viewing?** Auto-play **only** behind the significance gate; everything else is text + `⚔ View the field`. Repeat/log views render the **final frame instantly, no sequence, always skippable**. These are two different mechanisms for two different problems (novelty decay vs. re-watch fatigue) — ship both, and both are DoD.
2. **§10.2 — What counts as "significant"?** Decisive result **OR** a player marshal involved **OR** the battle earned a W6-2 dynamic name (`compose_battle_name` fired). All three inputs already ride `events[0]`. Deliberately generous on the "named" arm — the naming system already encodes significance.
3. **§10.3 — Proportional figure counts or a fixed cap?** **Fixed cap (~8–10 per corps) + a "+N corps in reserve" tail.** Proportional is a layout-overflow tarpit and a scale hazard, block size + odometer tiles already carry "committed strength," and per-corps committed strength isn't even in the payload to size by. Consistent with the map-label summarize discipline.
4. **§10.4 — Audio / Tier-B art sourcing scope?** Audio: **one cannon thud + one decisive drum sting only**, mute-respecting, no bed loop — and budget it as *small* (extraction + import + license-log; drum is an approximation until sourced). Tier-B animated poses: **not this slice** — no CC0 Napoleonic set exists, so it means LPC ShareAlike or the Pillow pipeline; do not pre-commit that decision at a Tier-A bless.
5. **§10.5 — Battle Gallery / persistence, i.e. the open-ended animation backlog?** **Out of Tier A, named-but-not-queued.** It needs a persistence answer and its own gate. Folding it in is the exact open-ended backlog GR9 forbids. Measure Tier A live first (§11.3); let the gallery earn its own slice on that evidence.
6. **§10.6 — Hostile actions against the player's OWN armies (defender's-eye view) — Fable's framing call.** The player is often the *defender* (an enemy storms a friendly corps; a coalition falls on the player's line; a fort is assaulted or bombarded). The tableau must frame a hostile action on friendly forces deliberately: draw the player's line on the near/"home" side regardless of who attacked (a loss reads as *your* line breaking, not a mirrored enemy triumph); give an incoming assault a distinct **alarm register** (red incursion arrow / the enemy standard advancing onto your baize) versus the victorious tone of a player win; and invert the greyed-block / captured-standard / Berthier beats when it is *your* eagle that falls. **Framing + copy, not new mechanics** — the fog-filtered `contingents[]` already carries both sides — but a defeat should feel like a gut-punch, not a neutral read-out. Fable owns the register.

---

## 8. "Looks cool" art-direction brief (for the mockup)

**One line:** a shallow raked stage of **carved-oak** figures on **green baize** inside a **gilt ornament frame**, one warm lamp raking from **upper-right** throwing long shadows toward lower-left, two ranks converging on the **⚔ clash line**, the loser's flank **toppled-and-cascading** with its **eagle tipping across the centre**, each corps crowned by a small **sepia portrait locket + brass name-plate**, the no-show corps sitting **OFF the baize on a reserve shelf**, an **engraved brass nameplate** ("The Slaughter at Ulm") with a **wax seal** at the tray's foot — and **color kept rare**.

**Concrete moves:**

- **Material — sell the object, retire "tin."** This is a Kriegsspiel / Zinnfigur **carved-wood tray**, not a UI panel. The shipped sprites are sculpted relief on turned-wood bases with baked rim-light + core-shadow + contour — the "colored blocks" fear is already 80% solved by the art; the failure mode is letting the popup *flatten the sculpture*. Frame it as a physical thing: green baize ground band, a brass-edged tray lip in the foreground, the gilt frame around it. Real assets exist: `ornamental_frame_evander_pd.png`, `wax_seal.png`, `bar_frame.png`; theme `UI_GOLD` / `UI_PANEL_BG`.
- **Light — one warm raking key from the upper-right, long cast shadows to lower-left,** soft warm lamp-pool vignette on the clash, frame edges falling into navy. **Critical constraint:** the added key **must** come from upper-right, because rim-light is baked into all 24 sprites from that direction (`add_relief`) — any other angle reads double-lit and cheapens the whole object.
- **Color rarity as a rule.** Figures stay **monochrome oak**. The one saturated faction hue appears **only on standards + the base-rim band** (this is what the art actually paints — `faction_fill`/`faction_base_rim`; the coat mass is oak). **Red appears only in the casualty tally.** A wood field with two bright standards is a composition; a field of colored uniforms is noise.
- **The portrait + standard beats — the two signature shots:**
  - **Falling / captured standard (lead with this).** On a rout, the corps standard tilts and drops; on a decisive rout, it tweens **across the centre line onto the victor's side** — the eagle taken. Pure Tween on a static glyph, and the best-grounded color moment in the feature (the standard *is* the only faction-colored element).
  - **Portrait lockets, treated.** Each corps crowned by its marshal's face in an **oval brass locket, sepia/duotone-washed and vignetted** so a photo-lithograph sits *in* the wood tray, not floating over it. On rout, crack the glass / desaturate; the standing ★ glory crown rides the locket rim. **Untreated raw JPGs are the biggest material clash — the brass-locket duotone is what earns the "cool."**
- **Coalition multi-tint — the read rides standards + base-rim + lockets, never coats.** Put the failed-to-arrive / withdrew corps physically **OFF the baize on a side reserve shelf**, greyed — the negative space *is* the drama, and it reads "never in the battle" far better than a greyed in-line block. Eyeball two faction tints side-by-side (Austria off-white next to a pale ally) against the `_legible_tint` 0.5 floor before calling it done.
- **Terrain backdrop.** A low scrim at the back — river ribbon / hill line / crenellated wall behind a fortified defender — to say "a battle, somewhere specific" with no particle system. Gate-optional.
- **Odometer.** Casualty tiles tick **0 → 21,400 as the figures topple** — the count and the collapse are the same event. Keep on the two leads.
- **Berthier last.** After the topple settles and the standard falls, the `observation` verdict **types/fades in last** — terse, once, the closing gavel.
- **Fix the topple verb.** A toppled figure = **rotate ~78° AND desaturate + darken AND cast a fresh long flat shadow while its base disc stays put** — *not* opacity-0.3, which reads "ghost/erased" and quietly breaks the core visual sentence. Cascade the routing flank with staggered delays so it reads "they broke," not "attrition."

**Ship one hero still first — the Austerlitz coalition frame** (France: 3 oak corps with lockets + standards, Bernadotte off on the reserve shelf greyed; Coalition: Mack shattered and cascading with his eagle mid-tilt, Kutuzov withdrawn intact; ⚔ at centre; brass nameplate + wax seal; odometer; Berthier line last). It is the case text cannot do and the only real justification for the slice — and it stress-tests the two hard problems (two faction tints side-by-side; portraits-on-wood) in the exact composition that matters.

> **Note on the built mockup.** The interactive HTML mockup accompanying this memo (linked from spec §6)
> implements most of this brief — gilt frame, engraved nameplate, monogram lockets, coalition split,
> captured-eagle slide, cascade topple, odometer, Berthier-last, clickable no-show. It knowingly
> **diverges from two findings above** for expedience and should not be read as the target art: it uses
> (a) a **navy-panel** ground rather than the carved-wood/green-baize tray this brief recommends, and
> (b) the **Kutuzov "withdrew in good order"** beat, which §5 flags as *unmodeled and CUT* for the real
> slice. The mockup is a feel-of-the-thing proof, not the spec of record; where they disagree, §5/§8 win.
